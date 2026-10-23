#!/usr/bin/env python3
"""Quantos segundos esperar até o próximo horário livre do canal aventuras (imprime 0 = publicar agora).

Regra do Nei (22/10/2026, noite): no máximo 6 episódios por dia, às 8, 10, 12, 14, 16 e 18 h (canal validado; cidades às 9/15/21 h e shorts às 11:30/17:30/20:30 ficam fora desta conta).
Cada horário vale até o próximo; publica se ainda não saiu nada nele e o dia não bateu o TETO.
Conta pelo histórico do yt-pubx (campo data em hora local).
"""
import json
import os
from datetime import datetime, timedelta

HORAS = [8, 10, 12, 14, 16, 18]
TETO = 6
# horários extras fora do teto (Nei, 22/10/2026: "hoje à noite de hora em hora até meia-noite", canal validado)
EXTRA = {"2026-10-22 22", "2026-10-23 00"}
HIST = os.path.expanduser("~/.local/share/yt-pubx/historico.jsonl")
# vídeos das cidades (fila própria, 2 por dia) não contam no teto dos episódios (22/10/2026)
FILA_CIDADES = os.path.expanduser("~/projetos/wifi/fila-cidades/fila.json")


def ids_cidades():
    try:
        return {x.get("video_id") for x in json.load(open(FILA_CIDADES)) if x.get("video_id")}
    except (OSError, ValueError):
        return set()


def publicados():
    out = []
    fora = ids_cidades()
    try:
        for linha in open(HIST):
            try:
                r = json.loads(linha)
            except ValueError:
                continue
            if r.get("canal") == "aventuras" and r.get("url") and r.get("data") and r.get("video_id") not in fora:
                out.append(datetime.fromisoformat(str(r["data"])[:19]))
    except FileNotFoundError:
        pass
    return out


def main():
    agora = datetime.now()
    pubs = publicados()
    hoje = agora.date()
    janelas = [datetime.strptime(e, "%Y-%m-%d %H") for e in EXTRA]
    n_hoje = sum(1 for d in pubs if d.date() == hoje and not any(j <= d < j + timedelta(minutes=50) for j in janelas))
    ultimo = max(pubs) if pubs else datetime.min
    slots = [datetime.combine(hoje, datetime.min.time()) + timedelta(hours=h) for h in HORAS]
    amanha = datetime.combine(hoje + timedelta(days=1), datetime.min.time()) + timedelta(hours=HORAS[0])
    extras = sorted(datetime.strptime(e, "%Y-%m-%d %H") for e in EXTRA)
    vencido = [e for e in extras if e <= agora < e + timedelta(minutes=50)]
    if vencido and ultimo < vencido[-1]:
        print(0)
        return
    futuros = [e for e in extras if e > agora]
    if n_hoje < TETO:
        atual = [s for s in slots if s <= agora]
        if atual and ultimo < atual[-1]:
            print(0)
            return
        prox = next((s for s in slots if s > agora), amanha)
    else:
        prox = amanha
    if futuros and futuros[0] < prox:
        prox = futuros[0]
    print(max(60, int((prox - agora).total_seconds()) + 5))


if __name__ == "__main__":
    main()
