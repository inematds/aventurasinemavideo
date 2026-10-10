#!/usr/bin/env python3
"""Manda o e-mail do episódio ao assinante (Resend), com o link de download. Uso: enviar_email.py <ep>"""
import json, sys
import publicar_fila as p
e = p.estado()
for item in json.load(open(f'{p.D}/fila.json')):
    if item['ep'] in sys.argv[1:] and not e.get(item['ep'], {}).get('email'):
        e.setdefault(item['ep'], {})['email'] = p.email(item, '')
        p.salvar(e)
        print(item['ep'], 'e-mail enviado', e[item['ep']]['email'])
