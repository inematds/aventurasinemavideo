#!/usr/bin/env python3
"""cortes.py — 3 cortes verticais de ~15 s de cada episódio publicado no Aventuras.

Sem IA: ffmpeg + regras fixas.
- Trechos: um em cada terço do vídeo (pula o começo e o fim), começando e
  terminando numa pausa da narração (silencedetect no narracao.wav).
- Visual 9:16: vídeo 16:9 no meio, fundo desfocado, número do episódio e
  título em cima, "vídeo completo no canal" embaixo.
- Texto do YouTube: modelo fixo com o link do vídeo completo.
- Saída: /mnt/hd8t/memorias-aventura-cortes/<slug>/ e, com --importar,
  uma pasta por episódio em ~/projetos/yt-pub-lives26/imports/.

Uso:
  python3 cortes.py --so <slug>          # só um episódio (teste)
  python3 cortes.py                      # todos os publicados ainda sem corte
  python3 cortes.py --importar           # gera e coloca na pasta de imports
"""
import argparse, json, os, random, re, shutil, subprocess, sys, textwrap

HIST = os.path.expanduser('~/.local/share/yt-pubx/historico.jsonl')
SAIDA = '/mnt/hd8t/memorias-aventura-cortes'
IMPORTS = os.path.expanduser('~/projetos/yt-pub-lives26/imports')
FONTE = os.path.expanduser('~/.local/share/fonts/Montserrat-ExtraBold.ttf')
AMARELO = '#FACC15'
ALVO, MIN_S, MAX_S = 15.0, 12.0, 18.0
INICIO_PULA, FIM_PULA = 0.08, 0.12   # fração do vídeo ignorada no começo e no fim


def episodios_publicados():
    eps = []
    for linha in open(HIST, encoding='utf-8'):
        if not linha.strip():
            continue
        r = json.loads(linha)
        if r.get('canal') != 'aventuras' or not r.get('video_id'):
            continue
        video = os.path.realpath(r['origem'])
        pasta = os.path.dirname(video)
        slug = os.path.basename(pasta).replace('memorias-aventura-', '', 1)
        eps.append({'slug': slug, 'video': video, 'pasta': pasta,
                    'yt': r['video_id'], 'titulo_yt': r.get('titulo', '')})
    return eps


def duracao(arq):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'csv=p=0', arq], capture_output=True, text=True).stdout
    return float(out.strip())


def pausas(wav):
    """Lista de (inicio, fim) dos silêncios da narração."""
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', wav, '-af',
                          'silencedetect=noise=-35dB:d=0.35', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', err)]
    fim = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
    return list(zip(ini, fim))


def escolhe_trechos(dur, silencios, semente):
    rnd = random.Random(semente)
    a, b = dur * INICIO_PULA, dur * (1 - FIM_PULA)
    terco = (b - a) / 3
    trechos = []
    for i in range(3):
        lo, hi = a + i * terco, a + (i + 1) * terco - MIN_S
        # começa logo depois de uma pausa (início de frase)
        cands = [f for (s, f) in silencios if lo <= f <= hi]
        ini = rnd.choice(cands) - 0.15 if cands else rnd.uniform(lo, max(lo, hi))
        # termina no começo de uma pausa (fim de frase), o mais perto de 15 s
        fins = [s for (s, f) in silencios if ini + MIN_S <= s <= ini + MAX_S]
        fim = min(fins, key=lambda s: abs(s - ini - ALVO)) + 0.25 if fins else ini + ALVO
        trechos.append((round(max(0, ini), 2), round(min(fim, dur), 2)))
    return trechos


def titulo_base(ep):
    t = ep['titulo_yt'].split('|')[0].strip()
    return t or ep['slug']


def numero_ep(ep):
    m = re.search(r'#(\d+)', ep['titulo_yt'])
    return m.group(1) if m else ''


def camada_texto(ep, caminho):
    """PNG transparente 1080x1920 com os textos (o drawtext do ffmpeg 6.1 corta acentos)."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)

    def centro(texto, y, tam, cor, borda, fundo=None):
        f = ImageFont.truetype(FONTE, tam)
        x0, y0, x1, y1 = dr.textbbox((0, 0), texto, font=f, stroke_width=borda)
        x = (1080 - (x1 - x0)) / 2 - x0
        if fundo:
            p = 26
            dr.rectangle([x + x0 - p, y + y0 - p, x + x1 + p, y + y1 + p], fill=fundo)
        dr.text((x, y), texto, font=f, fill=cor, stroke_width=borda, stroke_fill='black')
        return y1 - y0

    n = numero_ep(ep)
    centro(f'MEMÓRIAS DE AVENTURA #{n}' if n else 'MEMÓRIAS DE AVENTURA', 170, 44, AMARELO, 4)
    linhas = textwrap.wrap(titulo_base(ep).upper(), 20)[:4]
    tam = 66 if len(linhas) <= 3 else 58
    y = 250
    for l in linhas:
        centro(l, y, tam, 'white', 6)
        y += int(tam * 1.25)
    centro('▶ VÍDEO COMPLETO NO CANAL', 1420, 50, 'black', 0, fundo=AMARELO)
    centro('@aventurasinema', 1550, 40, 'white', 3)
    img.save(caminho)
    return caminho


def render(ep, ini, fim, saida, tmp):
    png = camada_texto(ep, os.path.join(tmp, 'textos.png'))
    d = fim - ini
    vf = (
        f"[0:v]split[a][b];"
        f"[a]scale=-2:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.25[fundo];"
        f"[b]scale=1080:-2[frente];"
        f"[fundo][frente]overlay=0:(H-h)/2[base];"
        f"[base][1:v]overlay=0:0,"
        f"fade=in:st=0:d=0.3,fade=out:st={d - 0.4:.2f}:d=0.4[v]"
    )
    af = f"afade=in:st=0:d=0.3,afade=out:st={d - 0.5:.2f}:d=0.5"
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-ss', str(ini), '-t', f'{d:.2f}',
           '-i', ep['video'], '-i', png, '-filter_complex', vf, '-map', '[v]', '-map', '0:a', '-af', af,
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30',
           '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', saida]
    subprocess.run(cmd, check=True)


def descricao(ep, parte, epj):
    link = f"https://youtu.be/{ep['yt']}"
    linhas = [f"Trecho {parte}/3 de \"{titulo_base(ep)}\".",
              f"▶ Vídeo completo: {link}", ""]
    reg = (epj.get('registro') or [''])[0] if epj else ''
    if reg:
        linhas += [reg, ""]
    if epj and epj.get('idmat'):
        u = f"aventura.inema.club/mat/idmat{int(epj['idmat']):06d}.htm"
        linhas += [f"Matéria original com as fotos (para assinantes): {u}", f"https://{u}", ""]
    linhas += ["Acervo INEMA Aventura: https://aventura.inema.club", "#shorts #aventura #viagem"]
    return '\n'.join(linhas)


def titulo_short(ep, parte):
    base = titulo_base(ep)
    suf = f' ({parte}/3) #shorts'
    return (base[:100 - len(suf)].rstrip() + suf)


def processa(ep, importar):
    destino = os.path.join(SAIDA, ep['slug'])
    pronto = os.path.join(destino, 'cortes.json')
    if os.path.exists(pronto):
        info = json.load(open(pronto))
    else:
        os.makedirs(destino, exist_ok=True)
        dur = duracao(ep['video'])
        sil = pausas(os.path.join(ep['pasta'], 'narracao.wav'))
        trechos = escolhe_trechos(dur, sil, ep['slug'])
        epj_p = os.path.join(ep['pasta'], 'EPISODIO.json')
        epj = json.load(open(epj_p)) if os.path.exists(epj_p) else {}
        clips = []
        for i, (ini, fim) in enumerate(trechos, 1):
            nome = f"{ep['slug']}_corte{i}.mp4"
            render(ep, ini, fim, os.path.join(destino, nome), destino)
            clips.append({'file': nome, 'inicio': ini, 'fim': fim,
                          'title': titulo_short(ep, i), 'description': descricao(ep, i, epj),
                          'tags': ['aventura', 'viagem', 'memórias de aventura', 'inema aventura']})
        p = os.path.join(destino, 'textos.png')
        if os.path.exists(p):
            os.remove(p)
        info = {'slug': ep['slug'], 'yt': ep['yt'], 'clips': clips, 'importado': False}
        json.dump(info, open(pronto, 'w'), ensure_ascii=False, indent=1)
        print(f"  {ep['slug']}: " + ', '.join(f"{c['inicio']}-{c['fim']}" for c in clips))
    if importar and not info.get('importado'):
        pasta = os.path.join(IMPORTS, f"aventuras-cortes-{ep['slug']}")
        os.makedirs(pasta, exist_ok=True)
        for c in info['clips']:
            shutil.copy2(os.path.join(destino, c['file']), os.path.join(pasta, c['file']))
        man = {'titulo': f"Cortes — {ep['slug']}", 'privacy': 'public',
               'clips': [{k: c[k] for k in ('file', 'title', 'description', 'tags')} for c in info['clips']]}
        json.dump(man, open(os.path.join(pasta, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
        info['importado'] = True
        json.dump(info, open(pronto, 'w'), ensure_ascii=False, indent=1)
        print(f"  {ep['slug']}: colocado em imports/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--so', help='slug de um episódio')
    ap.add_argument('--importar', action='store_true')
    a = ap.parse_args()
    eps = episodios_publicados()
    if a.so:
        eps = [e for e in eps if e['slug'] == a.so]
    print(f'{len(eps)} episódio(s)')
    falhas = []
    for ep in eps:
        try:
            processa(ep, a.importar)
        except Exception as e:
            falhas.append(ep['slug'])
            print(f"  FALHOU {ep['slug']}: {e}", file=sys.stderr)
    print(f'ok: {len(eps) - len(falhas)}  falhas: {len(falhas)} {falhas}')
    sys.exit(1 if falhas else 0)


if __name__ == '__main__':
    main()
