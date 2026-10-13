#!/usr/bin/env python3
"""Portão de um episódio feito pelo produtor automático. Sai 0 só se tudo passar; imprime o motivo da reprovação.
Uso: verifica_ep.py <pasta> <n> <idmat>"""
import json
import os
import subprocess
import sys

pasta, n, idmat = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])


def falha(msg):
    print("REPROVADO:", msg)
    sys.exit(1)


try:
    ep = json.load(open(f"{pasta}/EPISODIO.json"))
except (OSError, ValueError) as e:
    falha(f"EPISODIO.json ausente ou inválido ({e})")
for k in ("n", "slug", "idmat", "album", "titulo_curto", "video", "registro", "notificar"):
    if k not in ep:
        falha(f"EPISODIO.json sem '{k}'")
if int(ep["n"]) != n or int(ep["idmat"]) != idmat:
    falha(f"n/idmat trocados ({ep['n']}/{ep['idmat']}, esperado {n}/{idmat})")
v = ep["video"]
if not os.path.isfile(v) or os.path.getsize(v) < 5_000_000:
    falha(f"vídeo ausente ou pequeno demais: {v}")
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                    "-of", "json", v], capture_output=True, text=True)
info = json.loads(r.stdout or "{}")
dur = float(info.get("format", {}).get("duration", 0))
tipos = {s.get("codec_type") for s in info.get("streams", [])}
vid = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
if not 60 <= dur <= 240:
    falha(f"duração {dur:.0f} s fora de 60–240 s")
if "audio" not in tipos:
    falha("sem faixa de áudio")
if (vid.get("width"), vid.get("height")) != (1920, 1080):
    falha(f"resolução {vid.get('width')}x{vid.get('height')}, esperado 1920x1080")
if not os.path.isfile(f"{pasta}/roteiro.md"):
    falha("sem roteiro.md")
# áudio não pode ser silêncio
r = subprocess.run(["ffmpeg", "-v", "info", "-i", v, "-af", "volumedetect", "-vn", "-f", "null", "-"],
                   capture_output=True, text=True)
media = next((float(l.split(":")[1].split()[0]) for l in r.stderr.splitlines() if "mean_volume" in l), -99)
if media < -40:
    falha(f"áudio quase mudo (média {media} dB)")
print(f"OK #{n} {ep['titulo_curto']} — {dur:.0f} s")
