#!/usr/bin/env python3
"""Escolhe a próxima matéria a virar episódio e a reserva (status em_producao). Sem IA: regras do PLANO.md.

- pendente, relato ≥ 250 palavras, com álbum; álbum com ≥ 12 fotos em al1/ (conferido no B2 na hora);
- não assinante: no máximo 1 vídeo por pessoa (ninguém da matéria pode já ter aparecido);
- assinante: 2 em cada 8 (regra de 10/10 adaptada aos 8 por dia de 12/10), se houver;
- varia o assunto: evita a área dos 3 últimos episódios.
Saída (stdout): JSON da tarefa {n, idmat, album, slug, notificar, pasta, assunto, area}. Sem candidato: sai 3.
Uso: escolhe.py [--seco]   (--seco: só mostra, não reserva)
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime
from glob import glob

D = os.path.dirname(os.path.abspath(__file__))
P = f"{D}/privado"
RCLONE = os.path.expanduser("~/projetos/inemabk/rclone/rclone")
OUT = os.path.expanduser("~/projetos/output")
DISCO = "/mnt/hd8t/memorias-aventura"  # / vive em 98%: episódio novo mora no HD de 8 TB, com link em output/
NEI = 4819
MIN_FOTOS = 12
USADOS = ("feito", "produzido", "em_producao")


def jload(p, d):
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return d


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")


def proximo_n(cands):
    ns = [e.get("n", 0) for e in jload(f"{P}/episodios.json", [])]
    for f in glob(f"{OUT}/memorias-aventura-*/EPISODIO.json"):
        ns.append(int(jload(f, {}).get("n", 0) or 0))
    ns += [c.get("n", 0) for c in cands if c.get("status") in USADOS]
    return max(ns + [0]) + 1


def fotos(album):
    r = subprocess.run([RCLONE, "lsf", f"b2:inemaaventura/albuns/{album}/al1/"],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return -1
    return sum(1 for l in r.stdout.splitlines() if l.lower().endswith((".jpg", ".jpeg", ".png")))


def main():
    seco = "--seco" in sys.argv
    cands = jload(f"{P}/candidatos.json", [])
    usados = [c for c in cands if c.get("status") in USADOS]
    pessoas_usadas = {p["idf"] for c in usados for p in c.get("pessoas", [])} - {NEI}
    recentes = sorted(usados, key=lambda c: c.get("n", 0))[-8:]
    areas_recentes = [c.get("area") for c in recentes[-3:]]
    quer_assinante = sum(1 for c in recentes if c.get("assinante")) < 2

    def ok(c):
        if c.get("status") != "pendente" or c.get("palavras", 0) < 250 or not c.get("album"):
            return False
        if c.get("assinante"):
            return True
        return not ({p["idf"] for p in c.get("pessoas", [])} - {NEI}) & pessoas_usadas

    elegiveis = [c for c in cands if ok(c)]
    # relato mais rico primeiro; dentro disso, área diferente das últimas
    elegiveis.sort(key=lambda c: (not (quer_assinante and c.get("assinante")),
                                  c.get("area") in areas_recentes, -min(c.get("palavras", 0), 2500)))
    for c in elegiveis[:60]:
        nf = fotos(c["album"])
        if nf < MIN_FOTOS:
            if nf >= 0 and not seco:
                c["status"], c["fotos_al1"] = "sem_fotos", nf
                json.dump(cands, open(f"{P}/candidatos.json.tmp", "w"), ensure_ascii=False)
                os.replace(f"{P}/candidatos.json.tmp", f"{P}/candidatos.json")
            continue
        n = proximo_n(cands)
        nome = next((p["nome"].split()[0] for p in c.get("pessoas", []) if p["idf"] != NEI), "")
        ano = datetime.fromtimestamp(c["dt"]).year if c.get("dt") else ""
        base = slugify(f"{nome} {' '.join(c['assunto'].split()[:4])} {ano}")[:48].strip("-")
        slug, i = base, 2
        while os.path.exists(f"{OUT}/memorias-aventura-{slug}"):
            slug, i = f"{base}-{i}", i + 1
        tarefa = {"n": n, "idmat": c["idmat"], "album": c["album"], "slug": slug, "assunto": c["assunto"],
                  "area": c.get("area"), "assinante": c.get("assinante", False), "fotos_al1": nf,
                  "notificar": [p["idf"] for p in c.get("pessoas", []) if p["idf"] != NEI],
                  "pasta": f"{OUT}/memorias-aventura-{slug}"}
        if not seco:
            os.makedirs(f"{DISCO}/memorias-aventura-{slug}", exist_ok=True)
            os.symlink(f"{DISCO}/memorias-aventura-{slug}", tarefa["pasta"])
            c.update(status="em_producao", n=n, slug=slug, fotos_al1=nf,
                     reservado=datetime.now().isoformat(timespec="minutes"))
            json.dump(cands, open(f"{P}/candidatos.json.tmp", "w"), ensure_ascii=False)
            os.replace(f"{P}/candidatos.json.tmp", f"{P}/candidatos.json")
        print(json.dumps(tarefa, ensure_ascii=False))
        return
    sys.exit(3)


if __name__ == "__main__":
    main()
