#!/usr/bin/env python3
"""v3 dinâmica: as fotos do álbum (al1, 533x400) entram como cópias em papel, em pilha, faixa e mosaico,
com texto da viagem por cima; as remasterizadas (fotos-rm) e as de apoio fazem os planos cheios.
Mesmo áudio da v1 (narração nei + trilha). Renderiza por bloco em paralelo e junta.
Uso: render_v3.py [B01 B05 ...]   (sem argumento = todos + montagem final)"""
import json, math, os, random, re, subprocess, sys, unicodedata
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 30
OUT = f'{D}/v3'
A = sorted(f for f in os.listdir(f'{D}/fotos-all') if f.lower().endswith('.jpg'))
RM = {v: k for k, v in json.load(open(f'{D}/mapa_rm.json')).items()} if os.path.exists(f'{D}/mapa_rm.json') else {}
RUIM = {5}  # jpg corrompido no acervo
PAL = json.load(open(f'{D}/palavras.json')) if os.path.exists(f'{D}/palavras.json') else {}
ADESIVO = 0  # índice do adesivo da viagem (recorte do fundo preto); None = não há
LEAD = 0.6
INICIO = {'B01': 0, 'B02': 11.4, 'B03': 23.41, 'B04': 38.48, 'B05': 50.08, 'B06': 64.05, 'B07': 79.18,
          'B08': 90.87, 'B09': 101.4, 'B10': 117.36, 'B11': 129.44, 'B12': 146.7, 'B13': 161.13, 'B14': 176.48}
TOTAL = 183.9
DIP_OUT = {'B01', 'B04', 'B06', 'B10', 'B11', 'B13'}  # mesmas fronteiras com fade da v1
FONT_T = os.path.expanduser('~/.local/share/fonts/Anton-Regular.ttf')
FONT_K = os.path.expanduser('~/.local/share/fonts/Montserrat-ExtraBold.ttf')
AMBAR = (255, 179, 71)


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))


def Wd(b, palavra, n=0):
    """instante (relativo ao início do bloco) em que a palavra é dita"""
    alvo = norm(palavra)
    hits = [t for w, t in PAL[b] if norm(w).startswith(alvo)]
    if len(hits) <= n:
        raise SystemExit(f'palavra não achada: {b} {palavra}')
    return LEAD + hits[n]


def F(i):
    return f'{D}/fotos-rm/telmo_{RM[A[i]]}.jpg'


def AP(n):
    return f'{D}/apoio/{n}.png'


# ---------- curvas ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_io(p):
    return p * p * (3 - 2 * p)


def ease_out(p):
    return 1 - (1 - p) ** 3


def ease_back(p, s=1.6):
    p -= 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


# ---------- imagens ----------
_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def foto(i):
    def f():
        im = Image.open(f'{D}/fotos-all/{A[i]}').convert('RGB')
        if i == ADESIVO:  # adesivo da viagem: recorta o fundo preto
            a = np.asarray(im).sum(axis=2) > 60
            ys, xs = np.where(a)
            return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        return im.crop((0, 0, im.width, im.height - 46))  # tira a marca inema.com.br e a data
    return cached(('foto', i), f)


def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((math.ceil(im.width * r), math.ceil(im.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def fundo(path, blur=0, dim=1.0, tint=None):
    def f():
        im = cover(Image.open(path).convert('RGB'), W, H)
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        a = np.asarray(im).astype(np.float32) * dim
        if tint:
            a = a * np.array(tint, dtype=np.float32)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return cached(('fundo', path, blur, dim, tint), f)


def fundo_escuro():
    def f():
        y, x = np.mgrid[0:H, 0:W]
        r = np.sqrt(((x - W / 2) / (W * .62)) ** 2 + ((y - H / 2) / (H * .62)) ** 2)
        v = np.clip(1 - r * .75, 0, 1)[..., None]
        a = np.array([28, 22, 17], np.float32) * (0.35 + v)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return cached('escuro', f)


def cartao(i, w, ang):
    """cópia em papel: borda creme, girada, com sombra. Devolve RGBA (centro = centro da foto)."""
    def f():
        im = foto(i)
        h = round(w * im.height / im.width)
        b = max(8, round(w * .028))
        c = Image.new('RGB', (w + 2 * b, h + 2 * b), (243, 239, 230))
        c.paste(im.resize((w, h), Image.LANCZOS), (b, b))
        c = c.convert('RGBA').rotate(ang, Image.BICUBIC, expand=True)
        pad = 40
        out = Image.new('RGBA', (c.width + 2 * pad, c.height + 2 * pad), (0, 0, 0, 0))
        sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
        alpha = c.getchannel('A').point(lambda v: v * .6)
        sh.paste(Image.new('RGBA', c.size, (0, 0, 0, 255)), (pad + 10, pad + 16), alpha)
        sh = sh.filter(ImageFilter.GaussianBlur(12))
        out.alpha_composite(sh)
        out.alpha_composite(c, (pad, pad))
        return out
    return cached(('cartao', i, w, round(ang, 2)), f)


def colar(base, im, cx, cy, alpha=1.0):
    if alpha <= 0:
        return
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
    x, y = round(cx - im.width / 2), round(cy - im.height / 2)
    if x >= W or y >= H or x + im.width <= 0 or y + im.height <= 0:
        return
    base.alpha_composite(im, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))


# ---------- texto ----------
def espacado(dr, xy, txt, font, fill, track):
    x, y = xy
    for ch in txt:
        dr.text((x, y), ch, font=font, fill=fill)
        x += dr.textlength(ch, font=font) + track


def larg_esp(dr, txt, font, track):
    return sum(dr.textlength(c, font=font) + track for c in txt) - track


def bloco_texto(k=None, ti=None, body=None, size=128, align='c'):
    def f():
        fk, ft, fb = ImageFont.truetype(FONT_K, 34), ImageFont.truetype(FONT_T, size), ImageFont.truetype(FONT_K, 30)
        linhas = ti.split('\n') if ti else []
        tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        ws = [larg_esp(tmp, k, fk, 7) if k else 0] + [tmp.textlength(l, font=ft) for l in linhas] + \
             [tmp.textlength(body, font=fb) if body else 0]
        w = int(max(ws)) + 60
        lh = int(size * 1.08)
        h = (60 if k else 0) + lh * len(linhas) + (56 if body else 0) + 30
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        X = (lambda ww: (w - ww) / 2) if align == 'c' else (lambda ww: 10)
        y = 0
        if k:
            kw = larg_esp(dr, k, fk, 7)
            espacado(dr, (X(kw), y), k, fk, AMBAR + (255,), 7)
            y += 60
        for l in linhas:
            lw = dr.textlength(l, font=ft)
            dr.text((X(lw), y - size * .12), l, font=ft, fill=(255, 255, 255, 255))
            y += lh
        if body:
            dr.text((X(dr.textlength(body, font=fb)), y + 10), body, font=fb, fill=(235, 228, 215, 255))
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        sh.putalpha(im.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .85)))
        out = Image.new('RGBA', im.size, (0, 0, 0, 0))
        out.alpha_composite(sh, (3, 5))
        out.alpha_composite(im)
        return out
    return cached(('txt', k, ti, body, size, align), f)


def scrim(pos):
    def f():
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        if pos == 'c':
            a = np.exp(-((y - H / 2) / 300) ** 2) * .62
        else:
            a = np.clip((y - H * .45) / (H * .55), 0, 1) ** 1.4 * .78 * np.clip(1.25 - x / W, 0, 1)
        im = np.zeros((H, W, 4), np.uint8)
        im[..., 3] = (a * 255).astype(np.uint8)
        return Image.fromarray(im, 'RGBA')
    return cached(('scrim', pos), f)


def desenha_textos(fr, eventos, t):
    for e in eventos:
        u, d = t - e['t'], e['d']
        if u < 0 or u > d:
            continue
        a_in, a_out = clamp(u / .22), clamp((d - u) / .25)
        alpha = min(a_in, a_out)
        pos = e.get('pos', 'c')
        colar(fr, scrim(pos), W / 2, H / 2, alpha)
        tx = bloco_texto(e.get('k'), e.get('ti'), e.get('body'), e.get('size', 128 if pos == 'c' else 92),
                         'c' if pos == 'c' else 'l')
        if pos == 'c':
            s = 1.12 - .12 * ease_out(clamp(u / .35))
            im = tx if s == 1 else tx.resize((round(tx.width * s), round(tx.height * s)), Image.BILINEAR)
            colar(fr, im, W / 2, H / 2 + e.get('dy', 0), alpha)
        else:
            dy = 36 * (1 - ease_out(clamp(u / .4)))
            colar(fr, tx, 110 + tx.width / 2, H - 90 - tx.height / 2 + dy, alpha)


# ---------- planos (beats) ----------
class Pilha:
    """fundo (foto cheia, pode ir desfocada/escura) + cópias caindo uma a uma + câmera lenta"""

    def __init__(self, bg, cards=(), every=.5, t0=.2, sizes=(380, 600), region=(170, 120, 1750, 960),
                 z=(1.0, 1.08), at=(.5, .5), seed=1, times=None, big=None):
        self.bg, self.z, self.at = bg, z, at
        rnd = random.Random(seed)
        self.cards, pts = [], []
        for k, i in enumerate(cards):
            if times:
                tl = times[k]
            else:
                tl = t0 + k * every
            if big and i in big:
                w, (cx, cy), ang = big[i]
            else:
                # Nei (13/10/2026): cópias iam para a borda (cortadas) e o meio ficava vazio. Agora a cópia
                # cabe inteira na tela e a escolha pesa a distância do centro, não só a das outras cópias.
                w = rnd.randint(*sizes)
                ang = rnd.uniform(-9, 9)
                im = foto(i)
                h = w * im.height / im.width
                if h > 720:  # foto em pé também tem que caber
                    w, h = round(w * 720 / h), 720
                a = math.radians(abs(ang))
                hw = (w * math.cos(a) + h * math.sin(a)) / 2 + 28
                hh = (w * math.sin(a) + h * math.cos(a)) / 2 + 28
                zm = 1 - 1 / max(z)  # o zoom da câmera corta as bordas: a margem acompanha
                mx, my = W * zm / 2 + 30, H * zm / 2 + 30
                x0, x1 = max(region[0], hw + mx), min(region[2], W - hw - mx)
                y0, y1 = max(region[1], hh + my), min(region[3], H - hh - my)
                if x0 > x1:
                    x0 = x1 = W / 2
                if y0 > y1:
                    y0 = y1 = H / 2
                meio = ((region[0] + region[2]) / 2, (region[1] + region[3]) / 2)
                best = None
                for _ in range(24):
                    c = (rnd.uniform(x0, x1), rnd.uniform(y0, y1))
                    dmin = min([math.dist(c, p) for p in pts] or [0])
                    nota = dmin - .6 * math.dist(c, meio)
                    if best is None or nota > best[0]:
                        best = (nota, c)
                cx, cy = best[1]
            pts.append((cx, cy))
            ang_dir = rnd.uniform(0, 2 * math.pi)
            self.cards.append(dict(i=i, w=w, cx=cx, cy=cy, ang=ang, tl=tl,
                                   dx=math.cos(ang_dir) * 170, dy=math.sin(ang_dir) * 170))
        self._base, self._n = None, -1

    DUR = .42

    def frame(self, t, dur):
        assentados = [c for c in self.cards if t >= c['tl'] + self.DUR]
        if len(assentados) != self._n:
            b = self.bg().copy()
            for c in assentados:
                colar(b, cartao(c['i'], c['w'], c['ang']), c['cx'], c['cy'])
            self._base, self._n = b, len(assentados)
        fr = self._base.copy()
        for c in self.cards:
            u = t - c['tl']
            if 0 <= u < self.DUR:
                p = u / self.DUR
                s = 1.5 - .5 * ease_back(p)
                im = cartao(c['i'], c['w'], c['ang'])
                im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.BILINEAR)
                k = 1 - ease_out(p)
                colar(fr, im, c['cx'] + c['dx'] * k, c['cy'] + c['dy'] * k, clamp(u / .14))
        # câmera: zoom lento + tremidinha quando a cópia assenta
        z = self.z[0] + (self.z[1] - self.z[0]) * ease_io(clamp(t / max(dur, .1)))
        sx = sy = 0.0
        for c in self.cards:
            v = t - (c['tl'] + self.DUR * .55)
            if 0 <= v < .35:
                amp = 5 * math.exp(-v / .09)
                sx += amp * math.sin(v * 2 * math.pi * 17)
                sy += amp * math.cos(v * 2 * math.pi * 13)
        return camera(fr, z, self.at, sx, sy)


def camera(fr, z, at, sx=0, sy=0):
    if z <= 1.0005 and not sx and not sy:
        return fr
    z = max(z, 1.012)
    cw, ch = W / z, H / z
    cx = clamp(at[0] * W, cw / 2, W - cw / 2) + sx
    cy = clamp(at[1] * H, ch / 2, H - ch / 2) + sy
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return fr.resize((W, H), Image.BILINEAR, box=box)


class Faixa:
    """duas fileiras de cópias atravessando a tela em sentidos opostos sobre fundo desfocado"""

    def __init__(self, bg, rows, h=290, speeds=(-190, 160), ys=(285, 795), seed=2):
        self.bg, self.rows = bg, []
        rnd = random.Random(seed)
        for idxs, v, y in zip(rows, speeds, ys):
            items, x = [], 0
            for i in idxs:
                im = foto(i)
                w = round(h * im.width / im.height)
                items.append((i, w, rnd.uniform(-2.5, 2.5), x))
                x += w + 46
            self.rows.append(dict(items=items, v=v, y=y, L=x))

    def frame(self, t, dur):
        fr = self.bg().copy()
        for r in self.rows:
            off = (r['v'] * t) if r['v'] < 0 else (r['v'] * t - r['L'] + W)
            if r['v'] < 0:
                off += 60
            for i, w, ang, x in r['items']:
                cx = x + off + w / 2
                if -w < cx < W + w:
                    colar(fr, cartao(i, w, ang), cx, r['y'])
        return camera(fr, 1.0 + .04 * clamp(t / max(dur, .1)), (.5, .5))


class Mosaico:
    """grade de fotos que se acende peça a peça e depois afasta"""

    def __init__(self, cards, cols=8, rows=5, every=.07, t0=.15, seed=3):
        rnd = random.Random(seed)
        self.ids = cards
        self.cw, self.ch = W // cols, H // rows + 1
        cells = [(c, r) for r in range(rows) for c in range(cols)]
        ordem = list(range(len(cells)))
        rnd.shuffle(ordem)
        self.tiles = []
        for k, ci in enumerate(ordem):
            i = cards[ci % len(cards)]
            c, r = cells[ci]
            self.tiles.append(dict(i=i, x=c * self.cw, y=r * self.ch, tl=t0 + k * every))
        self._base, self._n = None, -1

    def tile(self, i):
        return cached(('tile', i, self.cw, self.ch), lambda: cover(foto(i), self.cw - 6, self.ch - 6).convert('RGBA'))

    def frame(self, t, dur):
        D_ = .3
        prontos = [x for x in self.tiles if t >= x['tl'] + D_]
        if len(prontos) != self._n:
            b = Image.new('RGBA', (W, H), (14, 12, 10, 255))
            for x in prontos:
                b.alpha_composite(self.tile(x['i']), (x['x'] + 3, x['y'] + 3))
            self._base, self._n = b, len(prontos)
        fr = self._base.copy()
        for x in self.tiles:
            u = t - x['tl']
            if 0 <= u < D_:
                s = max(.05, ease_back(u / D_))
                im = self.tile(x['i'])
                im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.BILINEAR)
                colar(fr, im, x['x'] + self.cw / 2, x['y'] + self.ch / 2, clamp(u / .1))
        return camera(fr, 1.12 - .1 * ease_io(clamp(t / max(dur, .1))), (.5, .5))


# ---------- roteiro visual ----------
def blocos():
    rm = lambda i, **k: (lambda: fundo(F(i), **k))
    ap = lambda n, **k: (lambda: fundo(AP(n), **k))
    usados = [i for i in range(len(A)) if i not in RUIM]

    # abertura: chuva de cópias acelerando, de toda a viagem; o adesivo da viagem cai no meio
    rnd = random.Random(7)
    abre = [i for i in rnd.sample(usados[1:], 46)]
    tempos, t = [], .15
    for k in range(len(abre)):
        tempos.append(t)
        t += max(.09, .42 * (.9 ** k)) if k < 34 else .42
    t_ades = Wd('B01', 'sonho') - .5
    abre_cards = abre + [0]
    tempos.append(t_ades)
    B = {}
    B['B01'] = dict(beats=[(0, Pilha(fundo_escuro, abre_cards, times=tempos, sizes=(300, 620),
                                     region=(150, 110, 1770, 970), z=(1.0, 1.1), seed=11,
                                     big={0: (360, (W - 270, H - 250), -6)}))],
                    txt=[dict(t=.35, d=Wd('B01', 'Telmo') - .55, k='ACERVO INEMA AVENTURA', ti='NOVEMBRO DE 2004'),
                         dict(t=Wd('B01', 'Telmo') - .2, d=Wd('B01', 'sonho') - Wd('B01', 'Telmo'),
                              k='O GAÚCHO', ti='TELMO SUBIU NA MOTO'),
                         dict(t=Wd('B01', 'sonho') - .1, d=Wd('B01', 'atravessar') - Wd('B01', 'sonho') - .05,
                              k='PARA REALIZAR', ti='UM SONHO DE 15 ANOS'),
                         dict(t=Wd('B01', 'atravessar') - .1, d=11.4 - Wd('B01', 'atravessar') - .3,
                              k='DE OCEANO A OCEANO', ti='ATRAVESSANDO A AMÉRICA\nSOBRE DUAS RODAS', size=118)])
    b = 'B02'
    tA = Wd(b, 'acelerou') - 1.0
    B[b] = dict(beats=[(0, Pilha(ap('a1_poa_madrugada'), z=(1.0, 1.12), at=(.5, .45))),
                       (tA, Pilha(ap('a1_poa_madrugada', blur=10, dim=.55), [1, 2], times=[.25, .7],
                                  big={1: (640, (W / 2 - 300, H / 2 + 20), -6), 2: (600, (W / 2 + 310, H / 2 - 10), 5)},
                                  z=(1.0, 1.05)))],
                txt=[dict(t=.5, d=Wd(b, 'igreja') - .7, pos='bl', k='13 NOV 2004 · 6H DA MANHÃ', ti='PORTO ALEGRE'),
                     dict(t=Wd(b, 'igreja') - .1, d=tA - Wd(b, 'igreja'), pos='bl', k='JUNTO À PONTE DO GUAÍBA',
                          ti='IGREJA DOS NAVEGANTES'),
                     dict(t=Wd(b, 'acelerou') - .1, d=1.6, ti='E ACELEROU.', size=150)])
    b = 'B03'
    B[b] = dict(beats=[(0, Pilha(rm(10, blur=14, dim=.5), [3, 4, 6, 7, 8, 9, 10, 11, 12], every=1.25, t0=.4,
                                  sizes=(400, 600), seed=3))],
                txt=[dict(t=Wd(b, 'mil') - .1, d=2.6, k='NO PRIMEIRO DIA, SOZINHO', ti='1.000 KM'),
                     dict(t=Wd(b, 'La') - .1, d=2.4, pos='bl', k='ARGENTINA', ti='LA PAZ'),
                     dict(t=Wd(b, 'amigos') - .2, d=4.5, k='UM GRUPO DE AMIGOS', ti='DE 22 A 53 ANOS')])
    b = 'B04'
    tC = Wd(b, 'Cordilheira') - .6
    B[b] = dict(beats=[(0, Faixa(rm(14, blur=16, dim=.45), [list(range(13, 22)) * 2, list(range(28, 21, -1)) * 2])),
                       (tC, Pilha(rm(23), z=(1.0, 1.1), at=(.5, .4)))],
                txt=[dict(t=Wd(b, 'chuva') - .1, d=Wd(b, 'mapa') - Wd(b, 'chuva'), k='CHUVA · TÚNEL SUBFLUVIAL · PAMPAS',
                          ti='RIO PARANÁ'),
                     dict(t=tC + .3, d=11.6 - tC - .7, pos='bl', k='MENDOZA', ti='OS ANDES À FRENTE')])
    b = 'B05'
    tA, tC = Wd(b, 'Aconcágua') - .3, Wd(b, 'Cristo') - .3
    B[b] = dict(beats=[(0, Pilha(rm(34), z=(1.0, 1.1))), (tA, Pilha(rm(33), z=(1.12, 1.0))),
                       (tC, Pilha(rm(43, blur=12, dim=.5), [47, 44, 45, 46, 48, 49, 50, 35, 36, 37, 40, 41], every=.42,
                                  t0=.15, sizes=(340, 520), seed=5))],
                txt=[dict(t=.4, d=tA - .5, pos='bl', k='MENDOZA · ARGENTINA', ti='PUENTE DEL INCA'),
                     dict(t=tA + .2, d=tC - tA - .3, pos='bl', k='QUASE 7 MIL METROS', ti='ACONCÁGUA'),
                     dict(t=tC + .2, d=Wd(b, 'cada') - tC - .4, k='NEVE ATÉ O JOELHO · FRONTEIRA COM O CHILE',
                          ti='CRISTO REDENTOR'),
                     dict(t=Wd(b, 'cada') - .1, d=13.97 - Wd(b, 'cada'), ti='CADA CURVA,\nUMA PINTURA', size=118)])
    b = 'B06'
    t1, t2, t3 = Wd(b, 'dezenas') + .8, Wd(b, 'pôr') - .3, Wd(b, 'Mais') - .2
    B[b] = dict(beats=[(0, Pilha(rm(55), z=(1.0, 1.12), at=(.5, .55))),
                       (t1, Pilha(rm(55, blur=12, dim=.5), [51, 52, 53, 54, 56, 57, 58], every=.33, sizes=(380, 560), seed=6)),
                       (t2, Pilha(rm(59), z=(1.0, 1.08))),
                       (t3, Pilha(rm(59, blur=10, dim=.55), [60, 61, 62, 63, 64, 65, 66, 67], every=.32,
                                  region=(150, 110, 1770, 970), sizes=(340, 520), seed=16))],
                txt=[dict(t=.4, d=t1 - .5, pos='bl', k='CHILE', ti='LOS CARACOLES'),
                     dict(t=t2 + .3, d=t3 - t2 - .4, k='VIÑA DEL MAR · AO PÔR DO SOL', ti='OCEANO PACÍFICO'),
                     dict(t=t3 + .3, d=15.13 - t3 - .7, k='DE UM OCEANO AO OUTRO', ti='+2.500 KM', size=170)])
    b = 'B07'
    t1, t2 = Wd(b, 'lago'), Wd(b, 'alto') - .3
    B[b] = dict(beats=[(0, Faixa(rm(73, blur=16, dim=.45), [[67, 68, 69, 70, 71, 72, 74, 75] * 2, [78, 76, 77, 72, 71, 70] * 2],
                                 speeds=(-240, 210))),
                       (t1, Pilha(rm(73), z=(1.0, 1.1))),
                       (t2, Pilha(ap('a2_villarrica'), z=(1.0, 1.14), at=(.5, .35)))],
                txt=[dict(t=.3, d=t1 - .4, k='RUMO AO SUL', ti='CHILE'),
                     dict(t=t1 + .3, d=t2 - t1 - .4, pos='bl', k='UM ARGENTINO EMPRESTOU UM BINÓCULO', ti='NA BEIRA DO LAGO'),
                     dict(t=Wd(b, 'Vila') - .1, d=11.69 - Wd(b, 'Vila') - .2, pos='bl',
                          k='LAVA CONTRA O CÉU DA NOITE', ti='VULCÃO VILLARRICA')])
    b = 'B08'
    B[b] = dict(beats=[(0, Pilha(rm(80, dim=.8), [79, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91], every=.62, t0=.3,
                                 sizes=(360, 520), seed=8, z=(1.0, 1.06)))],
                txt=[dict(t=.4, d=Wd(b, 'cartão') - .7, pos='bl', k='PUCÓN · VALDIVIA', ti='REGIÃO DOS LAGOS'),
                     dict(t=Wd(b, 'cartão') - .2, d=10.53 - Wd(b, 'cartão'), k='“SÓ PARA TER CERTEZA…”',
                          ti='UM CARTÃO-POSTAL\nNA VISEIRA?', size=118)])
    b = 'B09'
    dusk = (1.0, .78, .62)
    t1, t2 = Wd(b, 'Desligaram') - .3, Wd(b, 'pedaleiras') - .9
    B[b] = dict(beats=[(0, Pilha(rm(98, dim=.75, tint=dusk), z=(1.0, 1.1))),
                       (t1, Pilha(rm(98, blur=12, dim=.45, tint=dusk), [94, 95, 96, 97, 99, 100], every=.85, sizes=(420, 600), seed=9)),
                       (t2, Pilha(ap('a3_faiscas'), z=(1.0, 1.12), at=(.5, .6)))],
                txt=[dict(t=Wd(b, 'gasolina') - .1, d=t1 - Wd(b, 'gasolina'), pos='bl', k='NO ALTO DA CORDILHEIRA',
                          ti='A GASOLINA QUASE ACABOU'),
                     dict(t=t1 + .3, d=t2 - t1 - .5, k='DESCENDO A SERRA EM SILÊNCIO', ti='MOTORES DESLIGADOS'),
                     dict(t=t2 + .5, d=15.96 - t2 - .7, pos='bl', k='NO LUSCO-FUSCO', ti='FAÍSCAS NO ASFALTO')])
    b = 'B10'
    B[b] = dict(beats=[(0, Faixa(rm(116, blur=16, dim=.45), [list(range(101, 121)), list(range(121, 133))],
                                 speeds=(-330, 260), h=280))],
                txt=[dict(t=Wd(b, 'Bariloche') - .1, d=Wd(b, 'Vila') - Wd(b, 'Bariloche'), ti='BARILOCHE'),
                     dict(t=Wd(b, 'Vila') - .1, d=Wd(b, 'deserto') - Wd(b, 'Vila') - .1, ti='VILLA LA ANGOSTURA'),
                     dict(t=Wd(b, 'deserto') - .1, d=Wd(b, 'pressa') - Wd(b, 'deserto') - .1, k='O DESERTO DA',
                          ti='PATAGÔNIA'),
                     dict(t=Wd(b, 'botas') - .2, d=12.08 - Wd(b, 'botas'), k='NA PRESSA DE FUGIR DA CHUVA',
                          ti='BOTAS NO PÉ TROCADO')])
    b = 'B11'
    t1, t2 = Wd(b, 'Uruguai') - .3, Wd(b, 'Shui') - .3
    tE = Wd(b, 'embargada') - .2
    B[b] = dict(beats=[(0, Pilha(rm(134), z=(1.0, 1.1))),
                       (t1, Pilha(rm(136, blur=12, dim=.5), [135, 137, 138, 139, 140, 141, 142, 143, 144, 145, 133, 132],
                                  every=.2, t0=.1, sizes=(340, 520), seed=12)),
                       (t2, Pilha(ap('a4_chui_noite'), z=(1.0, 1.1)))],
                txt=[dict(t=.4, d=t1 - .5, pos='bl', k='A BALSA CRUZA O', ti='RIO DA PRATA'),
                     dict(t=t1 + .2, d=t2 - t1 - .3, k='COLÔNIA · MONTEVIDÉU · PUNTA DEL ESTE', ti='URUGUAI'),
                     dict(t=t2 + .4, d=tE - t2 - .6, pos='bl', k='CANTANDO O HINO EM PENSAMENTO', ti='CHUÍ'),
                     dict(t=tE, d=17.26 - tE - .3, k='A VOZ EMBARGADA', ti='PURA EMOÇÃO.', size=150)])
    b = 'B12'
    t1 = Wd(b, 'casa') - .5
    B[b] = dict(beats=[(0, Pilha(ap('a5_navegantes_tarde'), z=(1.0, 1.1), at=(.5, .4))),
                       (t1, Pilha(rm(147), z=(1.0, 1.08), at=(.5, .5)))],
                txt=[dict(t=.5, d=Wd(b, 'agradeceu') + .6, pos='bl', k='26 NOV 2004 · O ÚLTIMO DIA', ti='PONTE DO GUAÍBA'),
                     dict(t=t1 + .4, d=14.43 - t1 - .7, pos='bl', k='PORTO ALEGRE', ti='DE VOLTA EM CASA')])
    b = 'B13'
    mos = [i for i in usados if i not in (0,)]
    rnd = random.Random(13)
    mos = rnd.sample(mos, 40)
    tn = Wd(b, 'ninguém') - .3
    B[b] = dict(beats=[(0, Mosaico(mos, every=.075))],
                txt=[dict(t=Wd(b, '13') - .1, d=Wd(b, '3') - Wd(b, '13'), ti='13 DIAS', size=170),
                     dict(t=Wd(b, '3') - .1, d=Wd(b, '6') - Wd(b, '3'), ti='3 PAÍSES', size=170),
                     dict(t=Wd(b, '6') - .1, d=Wd(b, 'Thelmo') - Wd(b, '6'), ti='+6.700 KM', size=170),
                     dict(t=Wd(b, 'Thelmo') - .1, d=tn - Wd(b, 'Thelmo'), k='13 DIAS · 3 PAÍSES · +6.700 KM',
                          ti='A MOTO NA GARAGEM'),
                     dict(t=tn, d=15.35 - tn - .2, k='COMO ELE MESMO ESCREVEU', ti='“NINGUÉM É DE FERRO.\nSÓ A MOTO.”',
                          size=118)])
    b = 'B14'
    B[b] = dict(beats=[(0, Pilha(rm(39, blur=6, dim=.5), [0], times=[.6], big={0: (300, (W - 290, H - 250), -6)},
                                 z=(1.0, 1.06)))],
                txt=[dict(t=.5, d=TOTAL - INICIO[b] - .6, k='ACERVO INEMA AVENTURA', ti='MEMÓRIAS DE AVENTURA',
                          body='Telmo Machado da Silva · relato e fotos de 2004', size=120)])
    return B


def render_bloco(b):
    B = blocos()[b]
    ks = list(INICIO)
    t0 = INICIO[b]
    t1 = INICIO[ks[ks.index(b) + 1]] if b != ks[-1] else TOTAL
    n0, n1 = round(t0 * FPS), round(t1 * FPS)
    dur = (n1 - n0) / FPS
    beats = B['beats']
    prev_dip = ks.index(b) > 0 and ks[ks.index(b) - 1] in DIP_OUT
    out = f'{OUT}/seg_{b}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15',
                          '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    XF = .3
    for n in range(n1 - n0):
        t = n / FPS
        k = max(j for j, (tb, _) in enumerate(beats) if tb <= t + 1e-6)
        tb, beat = beats[k]
        bdur = (beats[k + 1][0] if k + 1 < len(beats) else dur) - tb
        fr = beat.frame(t - tb, bdur)
        if k > 0 and t - tb < XF:  # dissolve curto entre planos do mesmo bloco
            ptb, pbeat = beats[k - 1]
            fr = Image.blend(pbeat.frame(t - ptb, tb - ptb + XF).convert('RGB'), fr.convert('RGB'),
                             ease_io((t - tb) / XF)).convert('RGBA')
        fr = fr.copy() if fr.mode == 'RGBA' else fr.convert('RGBA')
        desenha_textos(fr, B['txt'], t)
        g = 1.0
        if prev_dip:
            g = min(g, ease_io(clamp(t / .4)))
        if b in DIP_OUT:
            g = min(g, ease_io(clamp((dur - t) / .4)))
        if b == ks[-1]:
            g = min(g, ease_io(clamp((dur - t) / 1.2)))
        a = np.asarray(fr.convert('RGB'))
        if b == 'B10' and t < .12:  # chicote da v1 vira um clarão curto
            a = np.clip(a.astype(np.float32) + 255 * (1 - t / .12) * .7, 0, 255).astype(np.uint8)
        if g < 1:
            a = (a.astype(np.float32) * g).astype(np.uint8)
        p.stdin.write(a.tobytes())
    p.stdin.close()
    p.wait()
    return b, n1 - n0


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    alvo = sys.argv[1:] or list(INICIO)
    with Pool(min(len(alvo), 14)) as pool:
        for b, n in pool.imap_unordered(render_bloco, alvo):
            print(b, n, 'quadros', flush=True)
    if not sys.argv[1:]:
        lst = f'{OUT}/lista.txt'
        open(lst, 'w').write(''.join(f"file 'seg_{b}.mp4'\n" for b in INICIO))
        final = f'{D}/telmo_memorias_v3.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                        '-i', f'{D}/telmo_memorias_v1.mp4', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264',
                        '-preset', 'slow', '-crf', '26', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-shortest',
                        '-movflags', '+faststart', final], check=True)
        print(final, round(os.path.getsize(final) / 1e6, 1), 'MB')
