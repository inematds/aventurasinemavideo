#!/bin/bash
# Publica os episódios prontos da fila (privado/fila_publicar.txt, uma pasta por linha), em ordem.
# Saída 75 do publicar_episodio.py = limite do YouTube: espera 3 h (cada tentativa barrada gasta cota da API) e tenta de novo. Outro erro: para e avisa no log.
# Uso: systemd-run --user --unit aventuras-fila ./fila_publicar.sh
cd "$(dirname "$0")" || exit 1
FILA=privado/fila_publicar.txt
LOG=privado/fila_publicar.log
while true; do
  pasta=$(grep -v '^\s*$' "$FILA" 2>/dev/null | head -1)
  [ -z "$pasta" ] && { echo "$(date '+%F %T') fila vazia, fim" >> "$LOG"; exit 0; }
  # Teto do Nei (11/10/2026): no máximo 6 vídeos por dia no canal aventuras (conta o histórico do yt-pubx do dia)
  hoje=$(python3 -c "import json,os,time;d=time.strftime('%Y-%m-%d');print(sum(1 for l in open(os.path.expanduser('~/.local/share/yt-pubx/historico.jsonl')) if (r:=json.loads(l)).get('canal')=='aventuras' and r.get('url') and str(r.get('data','')).startswith(d)))")
  if [ "${hoje:-0}" -ge 6 ]; then
    espera=$(( $(date -d 'tomorrow 00:10' +%s) - $(date +%s) ))
    echo "$(date '+%F %T') já saíram $hoje hoje (teto 6), próxima tentativa amanhã 00:10" >> "$LOG"; sleep "$espera"; continue
  fi
  echo "$(date '+%F %T') publicando $pasta" >> "$LOG"
  python3 publicar_episodio.py "$pasta" >> "$LOG" 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then
    grep -vxF "$pasta" "$FILA" > "$FILA.tmp"; mv "$FILA.tmp" "$FILA"
    git add EPISODIOS.md descricoes/ && git commit -qm "Episódio publicado: $(basename "$pasta")" && git push -q
  elif [ $rc -eq 75 ]; then
    echo "$(date '+%F %T') limite do YouTube, nova tentativa em 3 h" >> "$LOG"; sleep 10800
  else
    echo "$(date '+%F %T') ERRO $rc em $pasta, fila parada" >> "$LOG"; exit $rc
  fi
done
