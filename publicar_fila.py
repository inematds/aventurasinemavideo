#!/usr/bin/env python3
"""Fila de publicação das Memórias de Aventura (autorizado pelo Nei em 10/10/2026).
Para cada episódio de fila.json: publica no canal do item (padrão aventuras = INEMA Aventura, desde 10/10/2026; antes lives10) → aviso no inemaytbot.
O e-mail ao assinante NÃO espera o YouTube (pedido do Nei 10/10): sai na hora com o link de download, por enviar_email.py. O lives10 (canal não verificado) tem teto diário de upload: com uploadLimitExceeded,
espera 1 h e tenta de novo, no máximo 36 vezes. Estado em estado.json (não repete publicação nem e-mail).
Uso: publicar_fila.py [--uma]   (--uma = uma rodada só, sem esperar)"""
import html, json, os, re, subprocess, sys, time, urllib.parse, urllib.request

D = os.path.dirname(os.path.abspath(__file__))
YT = os.path.expanduser('~/projetos/yt-pubx')
HIST = os.path.expanduser('~/.local/share/yt-pubx/historico.jsonl')
EST = f'{D}/estado.json'


def log(*a):
    print(time.strftime('%Y-%m-%d %H:%M'), *a, flush=True)


def estado():
    return json.load(open(EST)) if os.path.exists(EST) else {}


def salvar(e):
    txt = json.dumps(e, ensure_ascii=False, indent=1)
    open(EST, 'w').write(txt)


def url_publicada(video, canal):
    for l in reversed(open(HIST).read().splitlines()):
        r = json.loads(l)
        if r.get('origem') == video and r.get('canal') == canal and r.get('url'):
            return r['url']


def telegram(msg):
    tok = next(l.split('=', 1)[1].strip().strip('"') for l in open(os.path.expanduser('~/projetos/yt-pub-livesx-master/config/.env'))
               if l.startswith('TELEGRAM_NOTIFY_BOT_TOKEN='))  # inemaytbot
    data = urllib.parse.urlencode({'chat_id': os.environ.get('TELEGRAM_CHAT_ID') or open(os.path.expanduser('~/.config/aventurasinemavideo/telegram_chat')).read().strip(), 'text': msg}).encode()
    urllib.request.urlopen(f'https://api.telegram.org/bot{tok}/sendMessage', data=data, timeout=60)


def email(item, yt):
    key = next(l.split('=', 1)[1].strip().strip('"') for l in open(os.path.expanduser('~/projetos/inemaonline/worker/.dev.vars'))
               if l.startswith('RESEND_API_KEY='))
    to = [r['email'] for r in json.load(open(f'{D}/subs.json'))[0]['results'] if r.get('legacy_idf') == item['idf']][0]
    txt = open(f"{D}/{item['email']}").read().replace('{YT}', yt)
    assert '{' not in txt
    body = ''.join(f'<p>{re.sub(r"(https?://\S+)", r"<a href=\"\1\">\1</a>", html.escape(p).replace(chr(10), "<br>"))}</p>'
                   for p in txt.strip().split('\n\n'))
    data = {'from': 'Nei · INEMA Aventura <acesso@inema.club>', 'to': [to], 'reply_to': 'contato@inema.club',
            'subject': item['assunto'], 'text': txt,
            'html': f'<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#222">{body}</div>'}
    req = urllib.request.Request('https://api.resend.com/emails', data=json.dumps(data).encode(),
                                 headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json',
                                          'User-Agent': 'inema-memorias/1.0'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read()).get('id')


def rodada():
    """True = fila vazia; False = barrou no limite (tentar depois)."""
    e = estado()
    for item in json.load(open(f'{D}/fila.json')):
        canal = item.get('canal', 'aventuras')
        s = e.setdefault(item['ep'], {}).setdefault(canal, {})
        if not s.get('yt'):
            s['yt'] = url_publicada(item['video'], canal)
        if not s.get('yt'):
            p = subprocess.run(['timeout', '1500', './yt-pubx', 'publicar', item['video'], '--canal', canal,
                                '--plano', item['plano']], cwd=YT, capture_output=True, text=True)
            if 'uploadLimitExceeded' in p.stdout + p.stderr:
                log(item['ep'], f'limite diário do {canal}, tento depois')
                salvar(e)
                return False
            s['yt'] = url_publicada(item['video'], canal)
            if not s['yt']:
                log(item['ep'], 'falhou sem limite:', (p.stdout + p.stderr)[-600:])
                salvar(e)
                return False
            log(item['ep'], 'publicado', s['yt'])
            salvar(e)
        if not s.get('avisado'):
            telegram(f"Memórias de Aventura: {item['ep']} publicado no {canal} ({s['yt']}).")
            s['avisado'] = True
            salvar(e)
    return True


if __name__ == '__main__':
    for n in range(1 if '--uma' in sys.argv else 36):
        if rodada():
            log('fila concluída')
            break
        if '--uma' not in sys.argv:
            time.sleep(3600)
