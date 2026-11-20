#!/usr/bin/env python3
"""Reserva uma matéria PEDIDA PELO NEI para virar episódio, furando a escolha automática (escolhe.py).

Pedido do Nei (20/11/2026): "faça um vídeo e coloque na fila deste <link da matéria>".
A matéria pedida não passa pelas regras do escolhe.py (≥ 250 palavras, 1 vídeo por pessoa):
o pedido do Nei vale mais. O resto é igual: mesmo PRODUZIR.md, mesmo portão (verifica_ep.py),
mesma fila (privado/fila_publicar.txt). Quem roda é produz_pedido.sh.

Uso: pedido.py <idmat> <album> <slug>
  - cria/atualiza a candidata em privado/candidatos.json com status em_producao e teste='pedido-nei'
    (o laço principal não "retoma" o que tem teste marcado — não corre dois agentes na mesma pasta);
  - grava privado/textos/<idmat>.txt a partir do HTML da matéria no B2, se ainda não existir;
  - cria a pasta no HD de 8 TB com link em ~/projetos/output;
  - imprime a tarefa (JSON) no mesmo formato do escolhe.py.
"""
import html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime

from escolhe import DISCO, NEI, OUT, P, jload, proximo_n

B2 = "https://f005.backblazeb2.com/file/inemaaventura"


def baixa(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=60).read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def texto_da_materia(s):
    """Corpo da matéria: do título até 'Outras matérias', sem menu nem scripts."""
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>", "\n", t, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n\n", t)
    a = t.find("inema.club")
    fim = t.find("Outras mat")
    corpo = t[a + len("inema.club"):fim if fim > 0 else None] if a >= 0 else t
    return corpo.strip()


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    idmat, album, slug = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    cands = jload(f"{P}/candidatos.json", [])
    c = next((x for x in cands if x.get("idmat") == idmat), None)

    s = baixa(f"{B2}/mat/idmat{idmat:06d}.htm")
    os.makedirs(f"{P}/textos", exist_ok=True)
    ptxt = f"{P}/textos/{idmat}.txt"
    if not os.path.exists(ptxt):
        open(ptxt, "w").write(texto_da_materia(s) + "\n")

    if c is None:
        titulo = html.unescape(re.sub(r"\s+", " ", (re.search(r"<title>(.*?)</title>", s, re.S | re.I) or [None, ""])[1]))
        titulo = re.sub(r"^\s*INEMA\s*-\s*", "", titulo).strip()
        idfs = sorted({int(x) for x in re.findall(r"/ff/f?0*(\d+)", s)} - {NEI})
        # Nome e email das pessoas: reaproveita de outra candidata da mesma pessoa, se houver.
        conhecidas = {p["idf"]: p for x in cands for p in x.get("pessoas", [])}
        pessoas = [conhecidas.get(i, {"idf": i, "nome": "", "email": "", "assinante": False}) for i in idfs]
        c = {"idmat": idmat, "assunto": titulo, "area": None, "album": album,
             "palavras": len(open(ptxt).read().split()), "pessoas": pessoas,
             "assinante": any(p.get("assinante") for p in pessoas), "status": "pendente"}
        cands.append(c)

    if c.get("status") in ("feito", "produzido"):
        sys.exit(f"idmat {idmat} já está {c['status']} (slug {c.get('slug')})")
    pasta = f"{OUT}/memorias-aventura-{slug}"
    if c.get("status") != "em_producao":
        if os.path.exists(pasta):
            sys.exit(f"pasta {pasta} já existe — escolha outro slug")
        n = proximo_n(cands)
        os.makedirs(f"{DISCO}/memorias-aventura-{slug}", exist_ok=True)
        os.symlink(f"{DISCO}/memorias-aventura-{slug}", pasta)
        c.update(status="em_producao", n=n, slug=slug, album=album,
                 reservado=datetime.now().isoformat(timespec="minutes"))
    c["teste"] = "pedido-nei"
    json.dump(cands, open(f"{P}/candidatos.json.tmp", "w"), ensure_ascii=False)
    os.replace(f"{P}/candidatos.json.tmp", f"{P}/candidatos.json")

    print(json.dumps({"n": c["n"], "idmat": idmat, "album": c["album"], "slug": c["slug"],
                      "assunto": c["assunto"], "area": c.get("area"), "assinante": c.get("assinante", False),
                      "notificar": [p["idf"] for p in c.get("pessoas", []) if p["idf"] != NEI],
                      "pasta": f"{OUT}/memorias-aventura-{c['slug']}", "pedido_nei": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
