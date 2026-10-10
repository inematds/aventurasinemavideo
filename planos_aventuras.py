#!/usr/bin/env python3
"""Converte os planos yt-pubx do lives10 em planos do canal aventuras (INEMA Aventura, 10/10/2026).
Mesmo título, descrição, tags e arte da thumb; troca a assinatura INEMA.CLUB pela do acervo e a categoria (19, viagens)."""
import json, os, shutil

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.expanduser('~/.local/share/yt-pubx/trabalhos')
ORIG = {'telmo': '20261009-161546-telmo-memorias-v4-mp4', 'lameiros': '20261009-164239-lameiros-memorias-v1-mp4',
        'naoki': '20261010-000130-naoki-memorias-v1-mp4', 'natan': '20261010-000144-natan-memorias-v1-mp4',
        'ana': '20261010-023640-ana-memorias-v1-mp4', 'guilherme': '20261010-024110-guilherme-memorias-v1-mp4'}
for ep, pasta in ORIG.items():
    src = f'{T}/{pasta}'
    pl = json.load(open(f'{src}/plano.json'))
    sn = pl['youtube']['snippet']
    linhas = [l for l in sn['description'].split('\n') if 'Mais cursos abertos e gratuitos' not in l]
    sn['description'] = '\n'.join(linhas).rstrip()
    if 'aventura.inema.club' not in sn['description']:
        sn['description'] += '\n\nAcervo INEMA Aventura: https://aventura.inema.club'
    sn['tags'] = list(dict.fromkeys('INEMA Aventura' if t == 'INEMA Agentes' else t for t in sn['tags']))
    sn['categoryId'] = '19'
    pl.update(canal='aventuras', canal_nome='INEMA Aventura', thumb=None)
    dst = f'{D}/planos-aventuras/{ep}'
    os.makedirs(dst, exist_ok=True)
    txt = json.dumps(pl, ensure_ascii=False, indent=2)
    open(f'{dst}/plano.json', 'w').write(txt)
    arte = f'{src}/thumb_arte.png'
    if os.path.exists(arte):
        shutil.copy(arte, f'{dst}/thumb_arte.png')
    print(ep, os.path.exists(pl['video']), os.path.exists(arte), sn['title'])
