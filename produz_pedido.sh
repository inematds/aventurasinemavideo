#!/bin/bash
# Produz episódios de matérias PEDIDAS PELO NEI e põe na fila (Nei, 20/11/2026: "faça um vídeo e coloque
# na fila deste <link>"). Mesmo motor do produz_loop.sh (auto/produzir.py + PRODUZIR.md), mesmo portão
# (verifica_ep.py) e mesma fila — só que a matéria vem do pedido, não do escolhe.py, e um por vez.
#
# Uso: produz_pedido.sh <arquivo>   com uma linha por pedido:  idmat|album|slug|dica para o roteiro
# Ex.: 100906|0080967|paulo-desfile-ctg-nova-york-2008|Desfile dos gaúchos de Toronto na Avenida das Américas
# Rodar em segundo plano: systemd-run --user --unit aventuras-pedido -p MemoryMax=48G ./produz_pedido.sh pedidos.txt
cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
AVISA="$HOME/projetos/wifi/scripts/avisa-v3.sh"
FILA=privado/fila_publicar.txt
LOG=privado/produz.log
TAREFAS=privado/tarefas
TRAVA=privado/.candidatos.lock
TETO_H=${TETO_H:-4}
MEM=${MEM:-48G}
mkdir -p "$TAREFAS"
log() { echo "$(date '+%F %T') [pedido] $*" >> "$LOG"; }
marca() {  # marca <idmat> <status> [motivo] — e tira o teste='pedido-nei'
  flock "$TRAVA" python3 - "$@" <<'EOF'
import json, os, sys
p = 'privado/candidatos.json'
c = json.load(open(p))
for x in c:
    if x['idmat'] == int(sys.argv[1]):
        x['status'] = sys.argv[2]
        x.pop('teste', None)
        x['pedido_nei'] = True
        if len(sys.argv) > 3: x['motivo'] = sys.argv[3][:300]
json.dump(c, open(p + '.tmp', 'w'), ensure_ascii=False); os.replace(p + '.tmp', p)
EOF
}
python3 auto/ia_motor.py validar >> "$LOG" 2>&1 || { log "auto/ia.yaml inválido"; exit 1; }

feitos=""; falhou=""
while IFS="|" read -r -u 3 idmat album slug dica; do
  [ -z "$idmat" ] && continue
  case "$idmat" in \#*) continue;; esac
  tarefa=$(flock "$TRAVA" python3 pedido.py "$idmat" "$album" "$slug") || {
    log "idmat $idmat: não reservei ($tarefa)"; falhou="$falhou $idmat"; continue; }
  n=$(echo "$tarefa" | python3 -c "import json,sys;print(json.load(sys.stdin)['n'])")
  pasta=$(echo "$tarefa" | python3 -c "import json,sys;print(json.load(sys.stdin)['pasta'])")
  echo "$tarefa" > "$TAREFAS/$slug.json"
  log "início #$n $slug (idmat $idmat, pedido do Nei)"
  {
    echo "Você é o produtor automático da série Memórias de Aventura. Trabalhe sozinho até o fim, sem perguntar nada."
    echo "Leia antes: ~/projetos/aventurasinemavideo/CLAUDE.md (seção Lessons) e PLANO.md."
    echo
    echo "## Tarefa"
    echo '```json'; echo "$tarefa"; echo '```'
    echo "- ESTE EPISÓDIO FOI PEDIDO PELO NEI. Não desista por relato curto nem por já haver vídeo da mesma pessoa: faça o melhor episódio honesto possível com o relato e as fotos."
    [ -n "$dica" ] && echo "- Nota do pedido: $dica"
    echo "- A pasta do episódio JÁ EXISTE (é um link para o HD de 8 TB): $pasta. Trabalhe nela."
    echo "- Se a pasta já tiver trabalho (retomada), continue de onde parou; não refaça o que está certo."
    echo "- EPISODIO.json: use exatamente n=$n e idmat=$idmat; \"notificar\" = a lista da tarefa."
    echo "- NÃO publique, NÃO suba no B2, NÃO mande e-mail, NÃO mexa em privado/candidatos.json nem em privado/fila_publicar.txt, NÃO faça commit. O laço cuida disso."
    echo "- Classificação das fotos: use a etapa classificacao de auto/ia.yaml conforme PRODUZIR.md; não fixe Haiku ou outro modelo. Imagens restauradas continuam sempre Codex assinatura."
    echo "- Quem está na matéria recebe e-mail automático depois (todas as pessoas ligadas, menos o Nei)."
    echo
    cat PRODUZIR.md
  } > "$TAREFAS/$slug.prompt.md"

  t0=$(date +%s)
  timeout "${TETO_H}h" systemd-run --user --scope -q -p MemoryMax="$MEM" \
    python3 auto/produzir.py < "$TAREFAS/$slug.prompt.md" > "$TAREFAS/$slug.log" 2>&1
  rc=$?
  min=$(( ($(date +%s) - t0) / 60 ))
  if [ "$rc" -ne 0 ]; then
    log "#$n $slug motor falhou (rc=$rc, ${min} min); matéria preservada (teste=pedido-nei) para rodar de novo"
    "$AVISA" "🚨 Produtor Aventuras (pedido do Nei): falha do motor (rc=$rc) no #$n ($slug). Rodar de novo: ~/projetos/aventurasinemavideo/produz_pedido.sh. Log: $TAREFAS/$slug.log" >/dev/null 2>&1
    falhou="$falhou $slug"; continue
  fi
  if [ -f "$pasta/DESISTI.txt" ]; then
    motivo=$(head -c 300 "$pasta/DESISTI.txt")
    log "#$n $slug: o agente desistiu ($motivo) — pedido do Nei, fica em_producao para decisão"
    "$AVISA" "Produtor Aventuras (pedido do Nei): o #$n ($slug) não saiu. Motivo do agente: $motivo" >/dev/null 2>&1
    falhou="$falhou $slug"; continue
  fi
  portao=$(python3 verifica_ep.py "$pasta" "$n" "$idmat" 2>&1 | tail -1)
  if [ "${portao#OK}" != "$portao" ]; then
    marca "$idmat" produzido
    echo "$pasta" >> "$FILA"
    log "#$n $slug pronto em ${min} min, pedido do Nei → fila ($portao)"
    feitos="$feitos #$n"
    systemctl --user is-active -q aventuras-fila || systemctl --user start aventuras-fila
  else
    mv -f "$pasta/EPISODIO.json" "$pasta/EPISODIO.falhou.json" 2>/dev/null
    log "#$n $slug reprovado no portão (${min} min): $portao"
    "$AVISA" "🚨 Produtor Aventuras (pedido do Nei): #$n ($slug) reprovado no portão: $portao. Log: $TAREFAS/$slug.log" >/dev/null 2>&1
    falhou="$falhou $slug"
  fi
done 3< "$1"
log "pedido terminado: na fila${feitos:- nenhum}; sem sair:${falhou:- nenhum}"
