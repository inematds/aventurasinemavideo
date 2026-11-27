#!/usr/bin/env python3
"""Publica um episódio pronto (pasta com EPISODIO.json): B2 → YouTube (canal aventuras, sem capa) → descrição completa
→ e-mail às pessoas da matéria → registro (privado/episodios.json, EPISODIOS.md, candidatos.json) → aviso no inemaytbot.
Retomável: cada passo grava em privado/estado_pub.json e não se repete.
Uso: publicar_episodio.py <pasta-do-episodio> [--sem-email] [--so-aviso]
--so-aviso: só sobe no B2, sem e-mail.
E-mail (Nei, 22/10/2026): só depois de publicado, com o link do YouTube e o da página da matéria; nada de arquivo/download."""
import html, json, os, re, subprocess, sys, urllib.parse, urllib.request

D = os.path.dirname(os.path.abspath(__file__))
P = f'{D}/privado'
YT = os.path.expanduser('~/projetos/yt-pubx')
HIST = os.path.expanduser('~/.local/share/yt-pubx/historico.jsonl')
RCLONE = os.path.expanduser('~/projetos/inemabk/rclone/rclone')
CANAL = 'https://www.youtube.com/@aventurasinema'
NAO_AVISAR = {4819}  # o próprio Nei. Regra de 10/10/2026: avisar TODAS as pessoas ligadas à matéria
NUM = [('dois mil e onze', '2011'), ('dois mil e dez', '2010'), ('dois mil e nove', '2009'), ('dois mil e oito', '2008'),
       ('dois mil e sete', '2007'), ('dois mil e seis', '2006'), ('dois mil e cinco', '2005'), ('dois mil e quatro', '2004'),
       ('dois mil e três', '2003'), ('dois mil e dois', '2002'), ('dois mil e um', '2001'), ('dois mil', '2000')]


ESPERA_X3 = 6 * 3600


class Limite(Exception):
    pass


class Duplicado(Exception):  # matéria já publicada: a fila tira o episódio e segue (saída 65)
    pass


def jload(p, padrao):
    return json.load(open(p)) if os.path.exists(p) else padrao


def jsave(p, obj):
    txt = json.dumps(obj, ensure_ascii=False, indent=1)
    open(p, 'w').write(txt)


def marcar_feito(idmat):
    """Relê candidatos.json sob a trava do produtor e muda só esta matéria (26/11/2026).
    Antes gravava a cópia lida no início, horas antes (espera do x3), e devolvia a 'pendente' a matéria que o
    produtor acabara de reservar/produzir: Trilha Inca, Alexandre e Nanda viraram 5 episódios cada."""
    import fcntl
    with open(f'{P}/.candidatos.lock', 'a') as trava:
        fcntl.flock(trava, fcntl.LOCK_EX)
        p = f'{P}/candidatos.json'
        cands = jload(p, [])
        for x in cands:
            if x['idmat'] == idmat:
                x['status'] = 'feito'
        json.dump(cands, open(p + '.tmp', 'w'), ensure_ascii=False)
        os.replace(p + '.tmp', p)


def narracao(pasta):
    txt = open(f'{pasta}/roteiro.md').read()
    txt = txt.split('## Narração', 1)[-1]  # roteiro novo não tem esse título: usa os blocos B01… direto
    s = '\n\n'.join(re.sub(r'^B\d+( \([^)]*\))? — ', '', l).strip() for l in txt.splitlines() if re.match(r'^B\d+', l))
    for a, b in NUM:
        s = s.replace(a, b).replace(a.capitalize(), b)
    return s


def url_publicada(video):
    for l in reversed(open(HIST).read().splitlines()):
        r = json.loads(l)
        if r.get('origem') == video and r.get('canal') == 'aventuras' and r.get('url'):
            return r['url']


def yt(*args, timeout=1500):
    p = subprocess.run(['timeout', str(timeout), './yt-pubx', *args], cwd=YT, capture_output=True, text=True)
    out = p.stdout + p.stderr
    if re.search(r'uploadLimitExceeded|quotaExceeded|dailyLimitExceeded', out):
        raise Limite(out[-300:])
    return out


def entregar_x3(ep, plano):
    """Nei, 18/11/2026: o episódio longo entra na fila de clipes do x3 (lives26) e o x3 publica no horário."""
    s = json.load(open(plano))['youtube']['snippet']
    p = subprocess.run([os.path.expanduser('~/projetos/yt-pub-x3/yt-pub-x3'), 'enviar-arquivo', ep['video'], '--canal', 'lives26',
                        '--titulo', s['title'], '--descricao', s['description'], '--tags', ','.join(s.get('tags') or []),
                        '--sem-capa', '--origem', f"aventuras/{ep['slug']}", '--esperar', str(ESPERA_X3)],
                       capture_output=True, text=True, timeout=ESPERA_X3 + 600)
    m = re.search(r'Publicado: (\S+)', p.stdout)
    if m:
        return m.group(1)
    if p.returncode == 4:
        raise Limite('ainda na fila do x3')
    raise SystemExit('x3 não publicou: ' + (p.stdout + p.stderr)[-400:])


def descricao(ep, plano_txt, outros):
    abertura = plano_txt.split('\n\n')[0]
    tags = [p for p in plano_txt.split('\n\n') if p.startswith('#')]
    m = ep['idmat']
    partes = [abertura, 'A HISTÓRIA', narracao(ep['pasta']), 'SOBRE O REGISTRO', '\n'.join(ep.get('registro', [])),
              f'Matéria original com as fotos (para assinantes): aventura.inema.club/mat/idmat{m:06d}.htm',
              f'https://aventura.inema.club/mat/idmat{m:06d}.htm',
              'Você esteve nessa aventura ou tem a sua própria história guardada no INEMA? Conte nos comentários.',
              'OUTROS EPISÓDIOS DE MEMÓRIAS DE AVENTURA',
              '\n'.join(f"#{o['n']} {o['titulo_curto']}: {o['yt']}" for o in outros[-8:]),
              f'Canal Aventuras INEMA: {CANAL}', 'Acervo INEMA Aventura: https://aventura.inema.club'] + tags[-1:]
    d = '\n\n'.join(x for x in partes if x).replace('<', '').replace('>', '')
    while len(d) > 4900:  # corta episódios antigos da lista, depois a narração
        partes[9] = '\n'.join(partes[9].split('\n')[1:])
        d = '\n\n'.join(x for x in partes if x)
    return d


def email(pessoa, ep, yt_url, b2):
    key = next(l.split('=', 1)[1].strip().strip('"') for l in open(os.path.expanduser('~/projetos/inemaonline/worker/.dev.vars'))
               if l.startswith('RESEND_API_KEY='))
    nome = pessoa['nome'].strip().split()[0].capitalize()
    txt = open(f'{D}/email_modelo_nao_assinante.txt').read()
    for k, v in {'{NOME}': nome, '{TITULO}': ep['assunto'], '{ANO}': ep.get('ano', ''), '{B2}': b2, '{YT}': yt_url or '',
                 '{IDMAT}': f"{ep['idmat']:06d}"}.items():
        txt = txt.replace(k, v)
    txt = txt.replace(', publicado em ,', ',')
    assert yt_url, 'e-mail só sai com o link do YouTube (regra de 22/10/2026)'
    assert '{' not in txt, txt
    body = ''.join('<p>' + re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', html.escape(p).replace('\n', '<br>')) + '</p>'
                   for p in txt.strip().split('\n\n'))
    data = {'from': 'Nei · INEMA Aventura <acesso@inema.club>', 'to': [pessoa['email']], 'reply_to': 'contato@inema.club',
            'subject': f"Sua aventura virou vídeo: {ep['titulo_curto']}", 'text': txt,
            'html': f'<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#222">{body}</div>'}
    req = urllib.request.Request('https://api.resend.com/emails', data=json.dumps(data).encode(),
                                 headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json',
                                          'User-Agent': 'aventurasinemavideo/1.0'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read()).get('id')


def telegram(msg):
    tok = next(l.split('=', 1)[1].strip().strip('"') for l in open(os.path.expanduser('~/projetos/yt-pub-livesx-master/config/.env'))
               if l.startswith('TELEGRAM_NOTIFY_BOT_TOKEN='))  # inemaytbot (Nei, 11/10/2026), nunca o bot v3
    chat = os.environ.get('TELEGRAM_CHAT_ID') or open(os.path.expanduser('~/.config/aventurasinemavideo/telegram_chat')).read().strip()
    urllib.request.urlopen(f'https://api.telegram.org/bot{tok}/sendMessage',
                           data=urllib.parse.urlencode({'chat_id': chat, 'text': msg}).encode(), timeout=60)


def registrar_md(ep):
    linha = (f"| {ep['n']} | {ep['data']} | {ep['titulo_curto']} | [idmat{ep['idmat']:06d}](https://aventura.inema.club/mat/idmat{ep['idmat']:06d}.htm)"
             f" | {ep['album']} | {ep['yt']} | `memorias/{ep['slug']}/` | `output/memorias-aventura-{ep['slug']}` |\n")
    s = open(f'{D}/EPISODIOS.md').read()
    if ep['yt'] not in s:
        i = s.index('\n## Próximos')
        s = s[:i].rstrip('\n') + '\n' + linha + s[i:]
        open(f'{D}/EPISODIOS.md', 'w').write(s)


def avisar(c, ep, s, est, yt_url):
    enviados = s.setdefault('emails', {})
    voltou = set(jload(f'{P}/emails_voltaram.json', []))
    for p in c.get('pessoas', []):
        if p.get('email') and str(p['idf']) not in enviados and p['email'].strip().lower() not in voltou and p['idf'] not in NAO_AVISAR:
            enviados[str(p['idf'])] = email(p, ep, yt_url, s['b2'])
            jsave(f'{P}/estado_pub.json', est)


def publicar(pasta, sem_email=False, so_aviso=False):
    pasta = os.path.abspath(os.path.expanduser(pasta))
    ep = json.load(open(f'{pasta}/EPISODIO.json'))
    ep['pasta'] = pasta
    ep['idmat'] = int(ep['idmat'])  # o produtor às vezes grava como texto
    ep['notificar'] = [int(i) for i in ep.get('notificar', [])] or None
    if ep['notificar'] is None:
        ep.pop('notificar')
    repetido = [e for e in jload(f'{P}/episodios.json', [])
                if int(e.get('idmat', 0) or 0) == ep['idmat'] and e['slug'] != ep['slug']]
    if repetido:  # 26/11/2026: a mesma matéria saiu 5 vezes no canal; nunca publicar de novo
        raise Duplicado(f"matéria {ep['idmat']} já publicada como #{repetido[0]['n']} {repetido[0]['slug']} "
                        f"({repetido[0].get('yt', '')})")
    cand = {c['idmat']: c for c in jload(f'{P}/candidatos.json', [])}
    c = cand.get(ep['idmat'], {})
    ep.setdefault('assunto', c.get('assunto', ep['titulo_curto']))
    est = jload(f'{P}/estado_pub.json', {})
    s = est.setdefault(ep['slug'], {})
    nome_mp4 = os.path.basename(ep['video'])
    b2 = f"https://f005.backblazeb2.com/file/inemaaventura/memorias/{ep['slug']}/{nome_mp4}"
    if not s.get('b2'):
        subprocess.run([RCLONE, 'copy', ep['video'], f"b2:inemaaventura/memorias/{ep['slug']}/"], check=True, timeout=1800)
        urllib.request.urlopen(urllib.request.Request(b2, method='HEAD'), timeout=60)
        s['b2'] = b2
        jsave(f'{P}/estado_pub.json', est)
    if not s.get('yt'):
        s['yt'] = url_publicada(ep['video'])
    if so_aviso:  # episódio ainda na fila do YouTube: só sobe no B2 (sem e-mail desde 22/10/2026)
        print(ep['slug'], 'B2 ok, sem e-mail antes do YouTube')
        return
    if not s.get('yt'):
      try:
        if not s.get('plano'):
            ctx = (f"Memórias de Aventura #{ep['n']} (série do acervo INEMA Aventura, canal Aventuras INEMA). "
                   f"Matéria: {ep['assunto']}. Filme narrado com as fotos reais. Narração:\n" + narracao(pasta)[:3000])
            out = yt('publicar', ep['video'], '--canal', 'aventuras', '--sem-thumb', '--contexto', ctx, '--dry-run')
            m = re.search(r'PLANO: (\S+plano\.json)', out)
            if not m:
                raise SystemExit('dry-run sem plano: ' + out[-400:])
            s['plano'] = m.group(1)
            jsave(f'{P}/estado_pub.json', est)
        s['yt'] = entregar_x3(ep, s['plano'])
        if not s['yt']:
            raise SystemExit('publicação sem URL no histórico')
        jsave(f'{P}/estado_pub.json', est)
      except Limite:  # sem e-mail: só avisa quando o vídeo estiver no YouTube (22/10/2026)
        raise
    eps = jload(f'{P}/episodios.json', [])
    ep_reg = {k: ep[k] for k in ('n', 'slug', 'idmat', 'album', 'titulo_curto')}
    ep_reg.update(yt=s['yt'], b2=s['b2'], data=__import__('time').strftime('%d/%m/%Y'))
    if not s.get('descricao'):
        plano_txt = json.load(open(s['plano']))['youtube']['snippet']['description'] if s.get('plano') else ''
        outros = [e for e in eps if e['slug'] != ep['slug']]
        d = descricao(ep, plano_txt, outros)
        os.makedirs(f'{D}/descricoes', exist_ok=True)
        open(f"{D}/descricoes/{ep['slug']}.txt", 'w').write(d + '\n')
        yt('atualizar', s['yt'], '--canal', 'aventuras', '--description-arquivo', f"{D}/descricoes/{ep['slug']}.txt", timeout=300)
        s['descricao'] = True
        jsave(f'{P}/estado_pub.json', est)
    if not sem_email:
        avisar(c, ep, s, est, s['yt'])
    if not any(e['slug'] == ep['slug'] for e in eps):
        eps.append(ep_reg)
        jsave(f'{P}/episodios.json', eps)
    registrar_md(ep_reg)
    if c:
        marcar_feito(ep['idmat'])
    if not s.get('avisado'):
        telegram(f"Memórias de Aventura #{ep['n']} publicado no Aventuras INEMA: {s['yt']}")
        s['avisado'] = True
        jsave(f'{P}/estado_pub.json', est)
    print(ep['slug'], s['yt'], 'e-mails:', len(s.get('emails', {})))


if __name__ == '__main__':
    try:
        publicar(sys.argv[1], '--sem-email' in sys.argv, '--so-aviso' in sys.argv)
    except Limite as e:
        print('LIMITE do YouTube, tentar depois:', e)
        sys.exit(75)
    except Duplicado as e:
        print('DUPLICADO, fora da fila:', e)
        sys.exit(65)
