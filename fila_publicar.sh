#!/bin/bash
# Publica os episódios prontos da fila (privado/fila_publicar.txt, uma pasta por linha), em ordem.
# Saída 75 do publicar_episodio.py = limite do YouTube: espera 3 h (cada tentativa barrada gasta cota da API) e tenta de novo. Outro erro: para e avisa no log.
# Uso: systemd-run --user --unit aventuras-fila ./fila_publicar.sh
cd "$(dirname "$0")" || exit 1
# Codex novo na frente: /usr/bin/codex (0.116) morre no config.toml e parou a fila em 11/10/2026
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
AVISA="$HOME/projetos/wifi/scripts/avisa-v3.sh"
falhas=0
FILA=privado/fila_publicar.txt
LOG=privado/fila_publicar.log
while true; do
  pasta=$(grep -v '^\s*$' "$FILA" 2>/dev/null | head -1)
  # Fila vazia não encerra (12/10/2026): o produtor contínuo (produz_loop.sh) vai repondo
  [ -z "$pasta" ] && { sleep 600; continue; }
  # Aviso antecipado (Nei, 11/10/2026): todo episódio da fila já ganha B2 + e-mail com o canal, mesmo antes do YouTube
  grep -v '^\s*$' "$FILA" | while read -r p; do python3 publicar_episodio.py "$p" --so-aviso >> "$LOG" 2>&1; done
  # Ritmo do Nei (22/10/2026): no máximo 4 por dia, às 8, 12, 16 e 20 h; espera_slot.py diz quanto falta
  espera=$(python3 espera_slot.py)
  if [ "${espera:-3600}" -gt 0 ]; then
    echo "$(date '+%F %T') próximo horário em $((espera/60)) min ($(date -d "+$espera sec" '+%F %H:%M'))" >> "$LOG"; sleep "$espera"; continue
  fi
  echo "$(date '+%F %T') publicando $pasta" >> "$LOG"
  python3 publicar_episodio.py "$pasta" >> "$LOG" 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then
    [ $falhas -gt 0 ] && "$AVISA" "✅ Memórias de Aventura: a fila voltou a publicar ($(basename "$pasta")) depois de $falhas falha(s)." >> "$LOG" 2>&1
    falhas=0
    grep -vxF "$pasta" "$FILA" > "$FILA.tmp"; mv "$FILA.tmp" "$FILA"
    git add EPISODIOS.md descricoes/ && git commit -qm "Episódio publicado: $(basename "$pasta")" && git push -q
    # Shorts (Nei, 21/10/2026): 3 cortes de ~15 s do episódio vão para a fila de imports do lives26 (2 por dia).
    # Sem IA; pega também qualquer episódio publicado que ainda não tenha corte. Falha aqui não para a fila.
    nice -n 10 timeout 1800 python3 cortes.py --importar >> "$LOG" 2>&1 || echo "$(date '+%F %T') AVISO: cortes.py falhou para $(basename "$pasta") (fila segue)" >> "$LOG"
  elif [ $rc -eq 75 ]; then
    echo "$(date '+%F %T') limite do YouTube, nova tentativa em 3 h" >> "$LOG"; sleep 10800
  else
    # Regra do Nei (12/10/2026): erro não para calado; pede ajuda no bot v3, insiste a cada 30 min e tenta de novo
    falhas=$((falhas+1))
    erro=$(grep -v '^\s*$' "$LOG" | grep -iE 'error|erro|falhou|traceback' | tail -1 | cut -c1-300)
    echo "$(date '+%F %T') ERRO $rc em $pasta (falha $falhas), aviso no v3 e nova tentativa em 30 min" >> "$LOG"
    "$AVISA" "🚨 AJUDA: fila do canal Aventuras PARADA (tentativa $falhas).
Episódio: $(basename "$pasta")
Erro: $erro
Faltam $(grep -cv '^\s*$' "$FILA") vídeos na fila. Log: ~/projetos/aventurasinemavideo/privado/fila_publicar.log
Repito este aviso a cada 30 min até destravar." >> "$LOG" 2>&1
    sleep 1800
  fi
done
