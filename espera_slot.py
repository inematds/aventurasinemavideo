#!/usr/bin/env python3
"""Quantos segundos esperar até o próximo horário livre do canal aventuras (imprime 0 = publicar agora).

Regra do Nei (12/10/2026): no máximo 8 vídeos por dia, um a cada 2 h, nos horários 6, 8, ..., 20 h.
Cada horário vale até o próximo; publica se ainda não saiu nada nele e o dia não bateu 8.
Conta pelo histórico do yt-pubx (campo data em hora local).
"""
import json
import os
from datetime import datetime, timedelta

HORAS = [6, 8, 10, 12, 14, 16, 18, 20]
TETO = 8
HIST = os.path.expanduser("~/.local/share/yt-pubx/historico.jsonl")


def publicados():
    out = []
    try:
        for linha in open(HIST):
            try:
                r = json.loads(linha)
            except ValueError:
                continue
            if r.get("canal") == "aventuras" and r.get("url") and r.get("data"):
                out.append(datetime.fromisoformat(str(r["data"])[:19]))
    except FileNotFoundError:
        pass
    return out


def main():
    agora = datetime.now()
    pubs = publicados()
    hoje = agora.date()
    n_hoje = sum(1 for d in pubs if d.date() == hoje)
    ultimo = max(pubs) if pubs else datetime.min
    slots = [datetime.combine(hoje, datetime.min.time()) + timedelta(hours=h) for h in HORAS]
    amanha = datetime.combine(hoje + timedelta(days=1), datetime.min.time()) + timedelta(hours=HORAS[0])
    if n_hoje < TETO:
        atual = [s for s in slots if s <= agora]
        if atual and ultimo < atual[-1]:
            print(0)
            return
        prox = next((s for s in slots if s > agora), amanha)
    else:
        prox = amanha
    print(max(60, int((prox - agora).total_seconds()) + 5))


if __name__ == "__main__":
    main()
