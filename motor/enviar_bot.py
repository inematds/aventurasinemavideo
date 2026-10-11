#!/usr/bin/env python3
"""Manda o episódio (vídeo + roteiro) ao inemaytbot (Telegram, chat do Nei; regra de 11/10/2026: nada da série no bot v3). Uso: enviar_bot.py <video.mp4> "<legenda>" """
import json, os, sys, uuid, urllib.request

D = os.path.dirname(os.path.abspath(__file__))
CHAT = os.environ.get('TELEGRAM_CHAT_ID') or open(os.path.expanduser('~/.config/aventurasinemavideo/telegram_chat')).read().strip()
tok = next(l.split('=', 1)[1].strip().strip('"') for l in open(os.path.expanduser('~/projetos/yt-pub-livesx-master/config/.env'))
           if l.startswith('TELEGRAM_NOTIFY_BOT_TOKEN='))  # inemaytbot
api = f'https://api.telegram.org/bot{tok}'

def post(method, fields, files=None):
    b = uuid.uuid4().hex; body = b''
    for k, v in fields.items():
        body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, (name, data, ct) in (files or {}).items():
        body += (f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\n'
                 f'Content-Type: {ct}\r\n\r\n').encode() + data + b'\r\n'
    body += f'--{b}--\r\n'.encode()
    req = urllib.request.Request(f'{api}/{method}', data=body,
                                 headers={'Content-Type': f'multipart/form-data; boundary={b}'})
    r = json.loads(urllib.request.urlopen(req, timeout=600).read())
    print(method, r['ok']); return r['ok']

video, legenda = sys.argv[1], sys.argv[2]
assert os.path.getsize(video) < 50e6, 'acima de 50 MB'
post('sendVideo', {'chat_id': CHAT, 'caption': legenda, 'supports_streaming': 'true', 'width': '1920', 'height': '1080'},
     {'video': (os.path.basename(video), open(video, 'rb').read(), 'video/mp4')})
if len(sys.argv) > 3:
    post('sendDocument', {'chat_id': CHAT, 'caption': 'Roteiro narrado (voz nei)'},
         {'document': ('roteiro.md', open(f'{D}/roteiro.md', 'rb').read(), 'text/markdown')})
