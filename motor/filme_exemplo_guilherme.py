#!/usr/bin/env python3
"""Memórias de Aventura #6 — Guilherme Borges: Andes Kids Expedition 2003.
Motor da v4 do Telmo (render_v3 + render_v4 copiados aqui). Sem relato: só o que as fotos mostram; sem mapa
(nenhuma cidade aparece escrita nas fotos, só a Ruta Provincial 20).
Uso: filme.py [B01 ...]   (sem argumento = todos + montagem final com trilha.wav)"""
import json, os, subprocess, sys
from multiprocessing import Pool
import render_v3 as v3
import render_v4 as v4
from render_v3 import Faixa, Mosaico, Pilha, fundo, fundo_escuro
from render_v4 import Prof

D = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(f'{D}/linha.json'))
A = v3.A
C = json.load(open(f'{D}/classificacao.json'))
RM_OK = {int(os.path.basename(f)[4:-4]) for f in os.listdir(f'{D}/fotos-rm')}
I = L['inicio']
fim = lambda b: (I[list(I)[list(I).index(b) + 1]] if b != list(I)[-1] else L['total']) - I[b]


def F(i):
    return f'{D}/fotos-rm/gui_{i}.jpg'


for mod in (v3, v4):
    mod.INICIO, mod.TOTAL, mod.F = I, L['total'], F
    mod.DIP_OUT = {'B03', 'B06', 'B09'}
v3.RUIM = {c['i'] for c in C if c['cat'] == 'ruim'}
v3.ADESIVO, v3.LEAD = None, L['lead']
v4.OUT = f'{D}/v1'
v4.ENTRADA = {'B02': 'luz', 'B04': 'chicote', 'B05': 'chicote', 'B07': 'luz', 'B08': 'chicote', 'B10': 'luz'}
Wd = v3.Wd

cat = lambda *cs, n=1: [c['i'] for c in C if c['cat'] in cs and c['nota'] >= n]
TODAS = [c['i'] for c in C if c['cat'] != 'ruim']
MESA = cat('mesa', 'familia', 'criancas')
ESTR = cat('estrada', 'curiosidade')
LAGO = cat('paisagem', 'barco')
NEVE = cat('neve')


def blocos():
    pf = lambda i, mov='push', **k: Prof(F(i), mov, **k)
    bl = lambda i, **k: (lambda: fundo(F(i) if i in RM_OK else f'{D}/fotos-all/{A[i]}', blur=k.get('blur', 14), dim=k.get('dim', .5)))
    B = {}

    b = 'B01'  # chuva de cópias da viagem → o grupo de jaqueta igual
    ordem = TODAS[::3][:34]
    tempos, t = [], .15
    for k in range(len(ordem)):
        tempos.append(t)
        t += max(.12, .4 * (.9 ** k))
    t1 = Wd(b, 'jaqueta') - .3
    B[b] = dict(beats=[(0, Pilha(fundo_escuro, ordem, times=tempos, sizes=(300, 540), region=(150, 110, 1770, 970),
                                 z=(1.0, 1.1), seed=61)),
                       (t1, pf(0, 'push', z=(1.03, 1.12)))],
                txt=[dict(t=.35, d=t1 - .5, k='ACERVO INEMA AVENTURA', ti='2003 · RUMO AOS ANDES', size=110),
                     dict(t=t1 + .2, d=fim(b) - t1 - .5, pos='bl', k='AS CRIANÇAS NO CARRO', ti='A MESMA JAQUETA')])
    b = 'B02'  # o nome da viagem e quem fotografou
    t1 = Wd(b, 'quem') - .3
    B[b] = dict(beats=[(0, pf(80, 'pan_r', amt=30))],
                txt=[dict(t=.4, d=t1 - .5, k='A VIAGEM TINHA NOME', ti='ANDES KIDS\nEXPEDITION', size=128),
                     dict(t=t1 + .2, d=fim(b) - t1 - .5, pos='bl', k='FOTOS DE', ti='GUILHERME BORGES')])
    b = 'B03'  # nenhum diário, 154 fotos
    t1 = Wd(b, '154') - .3
    B[b] = dict(beats=[(0, Mosaico(TODAS * 2, every=.035))],
                txt=[dict(t=.4, d=t1 - .5, k='NENHUM DIÁRIO', ti='SÓ AS FOTOS', size=128),
                     dict(t=t1, d=fim(b) - t1 - .5, k='E ELAS CONTAM A HISTÓRIA SOZINHAS', ti='154 FOTOS', size=160)])
    b = 'B04'  # posto, grupo, jantares
    t1 = Wd(b, 'jantares') - .3
    B[b] = dict(beats=[(0, Pilha(bl(0), [0] + MESA[:4], every=.3, sizes=(440, 640), seed=4)),
                       (t1, pf(7, 'pan_l', amt=28))],
                txt=[dict(t=.4, d=t1 - .5, pos='tr', k='A PARADA NO POSTO', ti='O GRUPO\nINTEIRO', size=96, sc=0),
                     dict(t=t1 + .2, d=fim(b) - t1 - .5, pos='bl', k='PIZZA, VINHO E SONO', ti='JANTARES DE ESTRADA')])
    b = 'B05'  # Ruta Provincial 20
    t1 = Wd(b, 'reta') - .3
    B[b] = dict(beats=[(0, pf(23, 'rise', amt=30, z=(1.03, 1.1))), (t1, pf(33, 'pan_r', amt=34))],
                txt=[dict(t=.4, d=t1 - .5, pos='bl', k='ARGENTINA', ti='RUTA PROVINCIAL 20'),
                     dict(t=t1 + .2, d=fim(b) - t1 - .5, pos='bl', k='CONQUISTA DEL DESIERTO', ti='UMA RETA SEM FIM')])
    b = 'B06'  # dinossauro
    B[b] = dict(beats=[(0, pf(32, 'push', z=(1.03, 1.14), at=(.5, .45)))],
                txt=[dict(t=.6, d=fim(b) - 1.0, pos='bl', k='NO CAMINHO', ti='A FOTO DAS CRIANÇAS')])
    b = 'B07'  # os Andes: lagos, neve, barco
    t1, t2 = Wd(b, 'lagos') - .3, Wd(b, 'barco') - .5
    B[b] = dict(beats=[(0, pf(67, 'push', z=(1.03, 1.12))), (t1, Faixa(bl(131), [LAGO[::2] * 2, LAGO[1::2] * 2], h=300, speeds=(-210, 180))),
                       (t2, pf(56, 'pan_l', amt=30))],
                txt=[dict(t=.4, d=t1 - .5, k='E ENTÃO', ti='OS ANDES', size=170),
                     dict(t=t1 + .2, d=t2 - t1 - .3, k='LAGOS AZUIS', ti='MONTANHAS\nCOM NEVE', size=118),
                     dict(t=t2 + .2, d=fim(b) - t2 - .5, pos='bl', k='VENTO GELADO NO ROSTO', ti='PASSEIO DE BARCO')])
    b = 'B08'  # neve
    t1 = Wd(b, 'arvores') - .3
    B[b] = dict(beats=[(0, pf(120, 'push', z=(1.03, 1.12))), (t1, Pilha(bl(117), NEVE, every=.28, sizes=(420, 620), seed=8))],
                txt=[dict(t=.4, d=fim(b) - .9, k='O DEQUE, AS ÁRVORES, OS CASACOS', ti='E A NEVE', size=150)])
    b = 'B09'  # família e amigos
    B[b] = dict(beats=[(0, pf(72, 'push', z=(1.03, 1.1), dim=.9))],
                txt=[dict(t=.4, d=fim(b) - .9, k='A MELHOR AVENTURA', ti='COM A FAMÍLIA\nE OS AMIGOS', size=128)])
    b = 'B10'  # fecho
    B[b] = dict(beats=[(0, Mosaico(TODAS * 2, every=.04))],
                txt=[dict(t=1.2, d=fim(b) - 1.4, k='ACERVO INEMA AVENTURA', ti='MEMÓRIAS DE AVENTURA',
                          body='Andes Kids Expedition 2003 · fotos de Guilherme Borges', size=120)])
    return B


v4.blocos = blocos

if __name__ == '__main__':
    os.makedirs(v4.OUT, exist_ok=True)
    alvo = sys.argv[1:] or list(I)
    with Pool(min(len(alvo), 15)) as pool:
        for b, n in pool.imap_unordered(v4.render_bloco, alvo):
            print(b, n, 'quadros', flush=True)
    if not sys.argv[1:]:
        lst = f'{v4.OUT}/lista.txt'
        open(lst, 'w').write(''.join(f"file 'seg_{b}.mp4'\n" for b in I))
        final = f'{D}/guilherme_memorias_v1.mp4'
        base = ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst]
        enc = ['-vf', 'hqdn3d=3:2:6:4', '-c:v', 'libx264', '-preset', 'slow', '-b:v', '2500k', '-passlogfile', f'{v4.OUT}/p2']
        subprocess.run(base + enc + ['-pass', '1', '-an', '-f', 'null', '/dev/null'], check=True)
        subprocess.run(base + ['-i', f'{D}/trilha.wav', '-map', '0:v', '-map', '1:a'] + enc +
                       ['-pass', '2', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest',
                        '-movflags', '+faststart', final], check=True)
        print(final, round(os.path.getsize(final) / 1e6, 1), 'MB')
