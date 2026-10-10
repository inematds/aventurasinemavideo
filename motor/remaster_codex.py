#!/usr/bin/env python3
"""Remaster de foto antiga (533x400) pelo Codex image_gen (assinatura), fiel ao original.
Uso: remaster_codex.py 038 001 054 ...  → remaster/<n>.png"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

D = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(f'{D}/indice.json'))
PROMPT = """Use your image generation tool to EDIT the attached photograph (a real photo from the early 2000s, 533x400, low quality digital camera).
Goal: a faithful high-resolution photographic restoration, 16:9 landscape (1536x864 or larger), as if shot today on a good camera.
STRICT fidelity rules:
- Keep EXACTLY the same people: same faces, expressions, beards, glasses, hair, body shapes, clothes, jackets, helmets. Do not beautify or change anyone. Same number of people, same positions.
- Keep the same vehicles (motorcycles, cars, boats, gear), animals, signs, buildings, water, landscape and composition. Extend the sides naturally to fill 16:9, do not crop heads.
- Remove the yellow "inema.com.br" watermark and any orange date stamp.
- Improve only sharpness, detail, noise, dynamic range and natural color. Realistic photo, not illustration, no added text.
Save the final image as remaster.png in the current directory and reply only with OK."""

def run(n):
    d = f'{D}/remaster/work_{n}'; os.makedirs(d, exist_ok=True)
    out = f'{D}/remaster/{n}.png'
    if os.path.exists(out): return n, 'já existe'
    r = subprocess.run(['codex', 'exec', '--skip-git-repo-check', '--dangerously-bypass-approvals-and-sandbox',
                        '-i', f'{D}/fotos-all/{A[int(n)]}', '-'], input=PROMPT, cwd=d,
                       capture_output=True, text=True, timeout=1200)
    if os.path.exists(f'{d}/remaster.png'):
        os.replace(f'{d}/remaster.png', out); return n, 'OK'
    return n, 'FALHOU ' + (r.stderr or r.stdout)[-300:]

with ThreadPoolExecutor(4) as ex:
    for n, st in ex.map(run, sys.argv[1:]):
        print(n, st, flush=True)
