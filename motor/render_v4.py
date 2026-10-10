#!/usr/bin/env python3
"""v4 = v3 (cópias em papel, pilha/faixa/mosaico, texto por palavra) + o que os outros sistemas de vídeo já fazem:
profundidade 2.5D nas fotos cheias (depth do pixflow), mapa com a rota desenhando, contadores de km,
tela dividida partida/chegada, entrada em chicote/luz entre blocos, grão e vinheta de filme. Só imagens.
Uso: render_v4.py [B01 ...]   (sem argumento = todos + montagem final)"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import render_v3 as v3
from render_v3 import (A, AP, AMBAR, D, DIP_OUT, F, FONT_K, FONT_T, FPS, H, INICIO, TOTAL, W, Faixa, Mosaico, Pilha,
                       bloco_texto, cached, clamp, colar, cover, ease_io, ease_out, fundo, fundo_escuro, scrim, Wd)

OUT = f'{D}/v4'
GEO = os.path.expanduser('~/projetos/output/tempo-sul-2026-10-09/geo/paises.geojson')


# ---------- foto cheia com profundidade (2.5D) ----------
class Prof:
    """desloca cada pixel conforme a profundidade: o perto anda mais que o longe (parallax), mais zoom lento"""

    def __init__(self, path, mov='push', amt=26, z=(1.04, 1.12), at=(.5, .5), dim=1.0, tint=None):
        self.path, self.mov, self.amt, self.z, self.at, self.dim, self.tint = path, mov, amt, z, at, dim, tint

    def dados(self):
        def f():
            im = np.asarray(fundo(self.path, dim=self.dim, tint=self.tint).convert('RGB'))
            nome = os.path.splitext(os.path.basename(self.path))[0]
            d = Image.open(f'{OUT}/depth/{nome}.png').convert('L').resize((W, H), Image.BILINEAR)
            d = np.asarray(d.filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
            ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
            return im, d, xs, ys
        return cached(('prof', self.path, self.dim, self.tint), f)

    def frame(self, t, dur):
        im, d, xs, ys = self.dados()
        p = ease_io(clamp(t / max(dur, .1)))
        z = self.z[0] + (self.z[1] - self.z[0]) * p
        cx, cy = self.at[0] * W, self.at[1] * H
        ox = oy = 0.0
        push = 0.0
        if self.mov == 'pan_r':
            ox = (p - .5) * 2 * self.amt
        elif self.mov == 'pan_l':
            ox = -(p - .5) * 2 * self.amt
        elif self.mov == 'rise':
            oy = -(p - .5) * 2 * self.amt
        else:  # push: o perto cresce mais que o fundo
            push = .05 * p
        s = z * (1 + push * d)
        mx = cx + (xs - cx) / s - ox * d
        my = cy + (ys - cy) / s - oy * d
        out = cv2.remap(im, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return Image.fromarray(out).convert('RGBA')


# ---------- mapa com a rota ----------
ROTA = [('PORTO ALEGRE', -30.03, -51.23), ('URUGUAIANA', -29.75, -57.09), ('LA PAZ', -30.74, -59.65),
        ('PARANÁ', -31.73, -60.52), ('SAN LUIS', -33.30, -66.34), ('MENDOZA', -32.89, -68.84),
        ('CRISTO REDENTOR', -32.83, -70.07), ('VIÑA DEL MAR', -33.02, -71.55), ('SANTIAGO', -33.45, -70.67),
        ('CHILLÁN', -36.61, -72.10), ('PUCÓN', -39.27, -71.98), ('VALDIVIA', -39.81, -73.25),
        ('V. LA ANGOSTURA', -40.76, -71.65), ('BARILOCHE', -41.13, -71.31), ('SANTA ROSA', -36.62, -64.29),
        ('BUENOS AIRES', -34.60, -58.38), ('COLÔNIA', -34.47, -57.84), ('MONTEVIDÉU', -34.90, -56.16),
        ('PUNTA DEL ESTE', -34.96, -54.95), ('CHUÍ', -33.69, -53.46), ('PORTO ALEGRE ', -30.03, -51.23)]
ESTADOS = None
PAISES = [('BRASIL', -27.6, -53.6), ('ARGENTINA', -37.8, -66.0), ('CHILE', -27.5, -70.2), ('URUGUAI', -32.6, -56.1),
          ('PARAGUAI', -25.2, -58.0)]
OCEANOS = [('OCEANO PACÍFICO', -38.0, -79.0), ('OCEANO ATLÂNTICO', -38.6, -55.5)]
ROTULO = {'PORTO ALEGRE', 'URUGUAIANA', 'LA PAZ', 'MENDOZA', 'VIÑA DEL MAR', 'PUCÓN', 'BARILOCHE', 'BUENOS AIRES',
          'CHUÍ', 'SANTA ROSA'}
LON0, LON1, LAT0, LAT1 = -80.0, -44.0, -46.0, -24.0
KX = math.cos(math.radians(33))
MS = 110  # px por grau (lon*KX) no mapa grande


def proj(lat, lon):
    return ((lon - LON0) * KX * MS, (LAT1 - lat) * MS)


MW, MH = round((LON1 - LON0) * KX * MS), round((LAT1 - LAT0) * MS)


def mapa_base():
    def f():
        rng = np.random.default_rng(4)
        mar = np.zeros((MH, MW, 3), np.float32) + np.array([24, 38, 48], np.float32)
        mar += rng.normal(0, 3, (MH, MW, 1)).astype(np.float32)
        im = Image.fromarray(np.clip(mar, 0, 255).astype(np.uint8)).convert('RGBA')
        terra = Image.new('L', (MW, MH), 0)
        bordas = Image.new('RGBA', (MW, MH), (0, 0, 0, 0))
        dt, db = ImageDraw.Draw(terra), ImageDraw.Draw(bordas)
        gj = json.load(open(GEO))
        for ft in gj['features']:
            if ft['properties'].get('CONTINENT') != 'South America':
                continue
            g = ft['geometry']
            polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
            for poly in polys:
                pts = [proj(la, lo) for lo, la in poly[0]]
                dt.polygon(pts, fill=255)
                db.line(pts + [pts[0]], fill=(120, 96, 70, 200), width=max(3, round(3 * MS / 110)))
        papel = np.zeros((MH, MW, 3), np.float32) + np.array([226, 212, 182], np.float32)
        papel += rng.normal(0, 6, (MH, MW, 1)).astype(np.float32)
        papel = Image.fromarray(np.clip(papel, 0, 255).astype(np.uint8)).convert('RGBA')
        im.paste(papel, (0, 0), terra.filter(ImageFilter.GaussianBlur(1.2)))
        if ESTADOS:  # divisas estaduais (Brasil), mais finas que as fronteiras
            de = ImageDraw.Draw(im)
            for ft in json.load(open(ESTADOS))['features']:
                g = ft['geometry']
                for poly in (g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]):
                    pts = [proj(la, lo) for lo, la in poly[0]]
                    de.line(pts + [pts[0]], fill=(150, 128, 100, 150), width=max(2, round(1.5 * MS / 110)))
        im.alpha_composite(bordas)
        dr = ImageDraw.Draw(im)
        fk = ImageFont.truetype(FONT_K, round(46 * MS / 110))
        fo = ImageFont.truetype(FONT_K, round(40 * MS / 110))
        for nome, la, lo in PAISES:
            x, y = proj(la, lo)
            v3.espacado(dr, (x - 120 * MS / 110, y), nome, fk, (110, 88, 62, 170), 10)
        for nome, la, lo in OCEANOS:
            x, y = proj(la, lo)
            v3.espacado(dr, (x, y), nome, fo, (150, 175, 190, 200), 12)
        return im
    return cached('mapa', f)


def rota_px():
    pts = [proj(la, lo) for _, la, lo in ROTA]
    acc = [0.0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    return pts, acc


class Mapa:
    """papel envelhecido; a rota se desenha de k0 até k1 (índices da ROTA) e a câmera acompanha"""

    def __init__(self, k0, k1, t_draw=(.3, 3.0), cam=None, ja=0):
        self.k0, self.k1, self.td, self.ja = k0, k1, t_draw, ja
        self.cam = cam  # [(t, lat, lon, largura_em_graus)]

    def frame(self, t, dur):
        pts, acc = rota_px()
        p = ease_io(clamp((t - self.td[0]) / (self.td[1] - self.td[0])))
        L = acc[self.k0] + (acc[self.k1] - acc[self.k0]) * p
        # câmera
        c = self.cam
        if t <= c[0][0]:
            la, lo, wd = c[0][1:]
        elif t >= c[-1][0]:
            la, lo, wd = c[-1][1:]
        else:
            j = max(i for i in range(len(c)) if c[i][0] <= t)
            q = ease_io((t - c[j][0]) / (c[j + 1][0] - c[j][0]))
            la, lo, wd = [c[j][k] + (c[j + 1][k] - c[j][k]) * q for k in (1, 2, 3)]
        cx, cy = proj(la, lo)
        bw = wd * KX * MS
        bh = bw * H / W
        bw, bh = min(bw, MW), min(bh, MH)  # câmera nunca sai do papel
        cx, cy = min(max(cx, bw / 2), MW - bw / 2), min(max(cy, bh / 2), MH - bh / 2)
        box = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
        fr = mapa_base().resize((W, H), Image.BILINEAR, box=box)
        sx = W / bw
        tela = lambda x, y: ((x - box[0]) * sx, (y - box[1]) * sx)
        # trecho desenhado
        traco = []
        for i in range(len(pts) - 1):
            if acc[i] >= L:
                break
            a, b = pts[i], pts[i + 1]
            if not traco:
                traco.append(tela(*a))
            if acc[i + 1] <= L:
                traco.append(tela(*b))
            else:
                r = (L - acc[i]) / (acc[i + 1] - acc[i])
                traco.append(tela(a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r))
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lw = min(9, max(4, round(6 * sx / 1.2)))
        if len(traco) > 1:
            ImageDraw.Draw(glow).line(traco, fill=AMBAR + (200,), width=lw * 4, joint='curve')
            fr.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
            ImageDraw.Draw(fr).line(traco, fill=(200, 70, 30, 255), width=lw, joint='curve')
        dr = ImageDraw.Draw(fr)
        fn = ImageFont.truetype(FONT_K, 30)
        for i, (nome, _, _) in enumerate(ROTA):
            if acc[i] <= L + 1:
                x, y = tela(*pts[i])
                if not (-50 < x < W + 50 and -50 < y < H + 50):
                    continue
                r = 9
                dr.ellipse((x - r, y - r, x + r, y + r), fill=(250, 244, 230, 255), outline=(150, 50, 20, 255), width=4)
                if nome in ROTULO:
                    dr.text((x + 16, y - 18), nome, font=fn, fill=(60, 40, 25, 255))
        if traco:
            x, y = traco[-1]
            pul = 18 + 6 * math.sin(t * 9)
            halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(halo).ellipse((x - pul, y - pul, x + pul, y + pul), fill=AMBAR + (170,))
            fr.alpha_composite(halo.filter(ImageFilter.GaussianBlur(6)))
            dr.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(255, 255, 255, 255))
        return fr


# ---------- tela dividida partida | chegada ----------
class Dividida:
    def __init__(self, esq, dir_, rot_e, rot_d):
        self.e, self.d, self.re, self.rd = esq, dir_, rot_e, rot_d

    def frame(self, t, dur):
        fr = Image.new('RGBA', (W, H), (12, 10, 8, 255))
        p = ease_out(clamp(t / .7))
        z = 1.0 + .06 * clamp(t / max(dur, .1))
        for k, (path, rot) in enumerate(((self.e, self.re), (self.d, self.rd))):
            def painel(path=path):
                im = Image.open(path).convert('RGB')
                return cover(im, 1020, 1160).convert('RGBA')
            im = cached(('painel', path), painel)
            cw, ch = 954 / z, 1080 / z
            x0 = (1020 - cw) / 2
            im = im.resize((954, 1080), Image.BILINEAR, box=(x0, (1160 - ch) / 2, x0 + cw, (1160 + ch) / 2))
            x = (-954 + 954 * p) if k == 0 else (W - 954 * p)
            colar(fr, im, x + 477, H / 2)
            tx = bloco_texto(rot[0], rot[1], None, 76, 'l')
            colar(fr, tx, (60 if k == 0 else 966 + 60) + tx.width / 2, H - 80 - tx.height / 2, clamp((t - .6) / .3))
        return fr


# ---------- textos com contador ----------
def fmt_km(n):
    return f'{n:,}'.replace(',', '.')


def desenha_textos(fr, eventos, t):
    for e in eventos:
        u, d = t - e['t'], e['d']
        if u < 0 or u > d:
            continue
        alpha = min(clamp(u / .22), clamp((d - u) / .25))
        pos = e.get('pos', 'c')
        ti = e.get('ti')
        if 'conta' in e:
            v0, v1, mold, dc = e['conta']
            n = round(v0 + (v1 - v0) * ease_out(clamp(u / dc)) / 10) * 10 if v1 >= 100 else round(v1 * clamp(u / dc))
            ti = mold.format(fmt_km(n))
        colar(fr, scrim(pos), W / 2, H / 2, alpha * e.get('sc', 1))
        tx = bloco_texto(e.get('k'), ti, e.get('body'), e.get('size', 128 if pos == 'c' else 92), 'c' if pos == 'c' else 'l')
        if pos == 'c':
            s = 1.12 - .12 * ease_out(clamp(u / .35))
            im = tx if s == 1 else tx.resize((round(tx.width * s), round(tx.height * s)), Image.BILINEAR)
            colar(fr, im, W / 2, H / 2 + e.get('dy', 0), alpha)
        elif pos == 'tr':
            caixa = cached(('caixa', tx.width, tx.height), lambda: caixa_escura(tx.width + 50, tx.height + 30))
            colar(fr, caixa, W - 110 - tx.width / 2, 90 + tx.height / 2, alpha)
            colar(fr, tx, W - 110 - tx.width / 2, 90 + tx.height / 2, alpha)
        else:
            dy = 36 * (1 - ease_out(clamp(u / .4)))
            colar(fr, tx, 110 + tx.width / 2, H - 90 - tx.height / 2 + dy, alpha)


def caixa_escura(w, h):
    im = Image.new('RGBA', (w + 60, h + 60), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((30, 30, w + 30, h + 30), 22, fill=(18, 14, 10, 200))
    return im.filter(ImageFilter.GaussianBlur(3))


# ---------- acabamento de filme ----------
def vinheta():
    def f():
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W * .7)) ** 2 + ((y - H / 2) / (H * .7)) ** 2)
        return (1 - .38 * np.clip(r - .45, 0, 1) ** 1.5)[..., None].astype(np.float32)
    return cached('vinheta', f)


def graos():
    def f():
        rng = np.random.default_rng(9)
        return [rng.normal(0, 7, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1) for _ in range(6)]
    return cached('graos', f)


def luz(a, p, lado):
    """vazamento de luz quente atravessando a tela (p 0..1)"""
    y, x = cached('grade_luz', lambda: np.mgrid[0:H:4, 0:W:4].astype(np.float32))
    cx = (-.2 + 1.4 * p) * W if lado > 0 else (1.2 - 1.4 * p) * W
    g = np.exp(-(((x - cx) / (W * .28)) ** 2) - ((y - H * .4) / (H * .9)) ** 2) * math.sin(math.pi * p)
    g = cv2.resize(g, (W, H))[..., None]
    return a + g * np.array([255, 150, 60], np.float32) * .85


ENTRADA = {'B03': 'chicote', 'B04': 'luz', 'B06': 'chicote', 'B08': 'luz', 'B09': 'chicote', 'B10': 'chicote',
           'B13': 'luz'}


# ---------- roteiro visual (sobre o da v3) ----------
def blocos():
    B = v3.blocos()
    pf = lambda i, mov='push', **k: Prof(F(i), mov, **k)
    pa = lambda n, mov='push', **k: Prof(AP(n), mov, **k)
    # B01: abertura da v3 (chuva de cópias) fica igual
    b = 'B02'
    bt = B[b]['beats']
    B[b]['beats'] = [(0, pa('a1_poa_madrugada', 'push', z=(1.03, 1.12), at=(.5, .45))), bt[1]]
    # B03: mapa desenha Porto Alegre → Uruguaiana → La Paz (1.000 km), depois a pilha dos amigos
    b = 'B03'
    tM = Wd(b, 'onde') - .2
    B[b]['beats'] = [(0, Mapa(0, 2, (.4, Wd(b, 'La') + .2), cam=[(0, -30.2, -54.5, 11), (tM, -30.4, -57.5, 9)])),
                     (tM, B[b]['beats'][0][1])]
    B[b]['txt'] = [dict(t=.4, d=tM - .5, pos='tr', k='NO PRIMEIRO DIA, SOZINHO', ti='{} KM', size=110,
                        conta=(0, 1000, '{} KM', Wd(b, 'La') - .2), sc=0),
                   B[b]['txt'][2]]
    # B04: faixas + Mendoza em profundidade
    b = 'B04'
    B[b]['beats'][1] = (B[b]['beats'][1][0], pf(23, 'rise', amt=30, z=(1.03, 1.1), at=(.5, .4)))
    # B05: Puente del Inca e Aconcágua em 2.5D
    b = 'B05'
    bt = B[b]['beats']
    B[b]['beats'] = [(0, pf(34, 'pan_r', amt=34)), (bt[1][0], pf(33, 'push', z=(1.03, 1.14))), bt[2]]
    # B06: Caracoles e Pacífico em 2.5D; o "+2.500 km" vira o mapa de oceano a oceano
    b = 'B06'
    bt = B[b]['beats']
    t3 = bt[3][0]
    B[b]['beats'] = [(0, pf(55, 'push', z=(1.03, 1.15), at=(.5, .55))), bt[1], (bt[2][0], pf(59, 'pan_l', amt=30)),
                     (t3, Mapa(0, 7, (.2, 2.6), cam=[(0, -33.0, -70.0, 9), (2.4, -32.0, -61.0, 27)]))]
    B[b]['txt'][2] = dict(t=t3 + .3, d=15.13 - t3 - .7, pos='tr', k='DE UM OCEANO AO OUTRO', ti='+{} KM', size=130,
                          conta=(0, 2500, '+{} KM', 2.4), sc=0)
    # B07: lago e vulcão em 2.5D
    b = 'B07'
    bt = B[b]['beats']
    B[b]['beats'] = [bt[0], (bt[1][0], pf(73, 'pan_r', amt=30)), (bt[2][0], pa('a2_villarrica', 'push', z=(1.03, 1.16), at=(.5, .35)))]
    # B09: entardecer em 2.5D e a descida com faíscas
    b = 'B09'
    bt = B[b]['beats']
    dusk = (1.0, .78, .62)
    B[b]['beats'] = [(0, pf(98, 'pan_l', amt=30, dim=.75, tint=dusk)), bt[1],
                     (bt[2][0], pa('a3_faiscas', 'push', z=(1.03, 1.14), at=(.5, .6)))]
    # B11: balsa e noite no Chuí em 2.5D
    b = 'B11'
    bt = B[b]['beats']
    B[b]['beats'] = [(0, pf(134, 'pan_r', amt=26)), bt[1], (bt[2][0], pa('a4_chui_noite', 'push', z=(1.03, 1.12)))]
    # B12: igreja ao entardecer em 2.5D; em casa → tela dividida partida | chegada
    b = 'B12'
    t1 = Wd(b, 'casa') - .5
    B[b]['beats'] = [(0, pa('a5_navegantes_tarde', 'push', z=(1.03, 1.12), at=(.5, .4))),
                     (t1, Dividida(F(1), F(147), ('13 NOV 2004', 'A PARTIDA'), ('26 NOV 2004', 'A CHEGADA')))]
    B[b]['txt'] = [B[b]['txt'][0]]
    # B13: a volta inteira se desenha no mapa com os números; depois o mosaico e a frase dele
    b = 'B13'
    tT = Wd(b, 'Thelmo') - .3
    B[b]['beats'] = [(0, Mapa(0, len(ROTA) - 1, (.2, tT - .4), cam=[(0, -30.5, -55.0, 14), (tT, -35.0, -62.0, 30)])),
                     (tT, Mosaico(B[b]['beats'][0][1].ids, every=.035))]
    tx = B[b]['txt']
    B[b]['txt'] = [dict(tx[0], pos='tr', size=120, sc=0), dict(tx[1], pos='tr', size=120, sc=0),
                   dict(tx[2], pos='tr', size=120, sc=0, conta=(0, 6700, '+{} KM', 1.2)),
                   dict(tx[3], t=tT + .3, d=tx[4]['t'] - tT - .3), tx[4]]
    # B14: fecho em 2.5D
    b = 'B14'
    B[b]['beats'][0] = (0, B[b]['beats'][0][1])
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
    vin, gr = vinheta(), graos()
    for n in range(n1 - n0):
        t = n / FPS
        k = max(j for j, (tb, _) in enumerate(beats) if tb <= t + 1e-6)
        tb, beat = beats[k]
        bdur = (beats[k + 1][0] if k + 1 < len(beats) else dur) - tb
        fr = beat.frame(t - tb, bdur)
        if k > 0 and t - tb < XF:
            ptb, pbeat = beats[k - 1]
            fr = Image.blend(pbeat.frame(t - ptb, tb - ptb + XF).convert('RGB'), fr.convert('RGB'),
                             ease_io((t - tb) / XF)).convert('RGBA')
        fr = fr.copy() if fr.mode == 'RGBA' else fr.convert('RGBA')
        desenha_textos(fr, B['txt'], t)
        a = np.asarray(fr.convert('RGB')).astype(np.float32)
        ent = ENTRADA.get(b)
        if ent == 'chicote' and t < .3:  # entra deslizando com borrão de movimento
            q = 1 - ease_out(t / .3)
            a = np.roll(a, round(-q * 420), axis=1)
            kx = 1 + 2 * round(q * 60)
            a = cv2.blur(a, (kx, 1))
        if ent == 'luz' and t < .7:
            a = luz(a, t / .7, 1 if b != 'B08' else -1)
        a = a * vin + gr[n % len(gr)]
        g = 1.0
        if prev_dip:
            g = min(g, ease_io(clamp(t / .4)))
        if b in DIP_OUT:
            g = min(g, ease_io(clamp((dur - t) / .4)))
        if b == ks[-1]:
            g = min(g, ease_io(clamp((dur - t) / 1.2)))
        p.stdin.write(np.clip(a * g, 0, 255).astype(np.uint8).tobytes())
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
        final = f'{D}/telmo_memorias_v4.mp4'
        # grão quadro a quadro não comprime: hqdn3d + 2 passadas a 1750k cabem nos 50 MB do Telegram
        base = ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst]
        enc = ['-vf', 'hqdn3d=3:2:6:4', '-c:v', 'libx264', '-preset', 'slow', '-b:v', '1750k', '-passlogfile', f'{OUT}/p2']
        subprocess.run(base + enc + ['-pass', '1', '-an', '-f', 'null', '/dev/null'], check=True)
        subprocess.run(base + ['-i', f'{D}/telmo_memorias_v1.mp4', '-map', '0:v', '-map', '1:a'] + enc +
                       ['-pass', '2', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', final],
                       check=True)
        print(final, round(os.path.getsize(final) / 1e6, 1), 'MB')
