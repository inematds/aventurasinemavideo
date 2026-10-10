#!/usr/bin/env python3
"""remaster/<n>.png (Codex) → fotos-rm/gui_<n>.jpg 1920x1080 (nome único: o cache de depth do pixflow é por nome)."""
import glob, os
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); os.makedirs(f'{D}/fotos-rm', exist_ok=True)
for f in sorted(glob.glob(f'{D}/remaster/*.png')):
    n = os.path.basename(f)[:-4]; im = Image.open(f).convert('RGB'); w, h = im.size
    ch = int(w * 9 / 16)
    if ch < h: im = im.crop((0, 0, w, ch))  # corta só embaixo (não corta cabeça)
    elif ch > h: cw = int(h * 16 / 9); x = (w - cw) // 2; im = im.crop((x, 0, x + cw, h))
    im.resize((1920, 1080), Image.LANCZOS).save(f'{D}/fotos-rm/gui_{n}.jpg', quality=94)
    print(n, (w, h))
