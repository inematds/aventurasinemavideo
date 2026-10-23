#!/bin/bash
# Produtor contínuo da série Memórias de Aventura (pedido do Nei, 12/10/2026: "um runtime rodando sem parar").
# Enquanto a fila de publicação tiver menos de ALVO episódios, escolhe a próxima matéria (escolhe.py, sem IA),
# manda um `claude -p` (assinatura) seguir o PRODUZIR.md, passa o portão (verifica_ep.py) e põe na fila.
# Erro nunca para calado: avisa no bot v3 (regra de 12/10) e segue para a próxima matéria.
# Unit: ~/.config/systemd/user/aventuras-produz.service (Restart=always).
cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
AVISA="$HOME/projetos/wifi/scripts/avisa-v3.sh"
FILA=privado/fila_publicar.txt
LOG=privado/produz.log
TAREFAS=privado/tarefas
ALVO=${ALVO:-8}           # 2 dias de publicação adiantados (4 por dia desde 22/10/2026)
TETO_H=${TETO_H:-4}       # tempo máximo de um episódio
MEM=${MEM:-48G}
# Padrão: Opus 5.5 com esforço medium (decisão do Nei em 13/10/2026, depois do teste Opus × Sonnet × Haiku: ver RELATORIO-MODELOS-2026-10-13.md)
# Teste de modelo (Nei, 13/10/2026): MODELO=sonnet|haiku UMA=1 NA_FILA=0 ./produz_loop.sh faz 1 episódio fora da fila
MODELO=${MODELO:-}
UMA=${UMA:-0}
NA_FILA=${NA_FILA:-1}
ESFORCO=${ESFORCO:-}      # low|medium|high|xhigh|max; vazio = medium
EXTRA=${EXTRA:-}          # regra a mais no pedido (ex.: duração mínima)
TRAVA=privado/.candidatos.lock
mkdir -p "$TAREFAS"
falhas=0

log() { echo "$(date '+%F %T') $*" >> "$LOG"; }
marca() {  # marca <idmat> <status> <motivo>
  flock "$TRAVA" python3 - "$@" <<'EOF'
import json, os, sys
p = 'privado/candidatos.json'
c = json.load(open(p))
for x in c:
    if x['idmat'] == int(sys.argv[1]):
        x['status'] = sys.argv[2]
        if len(sys.argv) > 3: x['motivo'] = sys.argv[3][:300]
json.dump(c, open(p + '.tmp', 'w'), ensure_ascii=False); os.replace(p + '.tmp', p)
EOF
}

while true; do
  # disco: / vive cheio; episódio novo vai para o HD de 8 TB, mas TTS/render usam /tmp e o cache
  livre_raiz=$(df --output=avail -BG / | tail -1 | tr -dc 0-9)
  livre_hd=$(df --output=avail -BG /mnt/hd8t 2>/dev/null | tail -1 | tr -dc 0-9)
  if [ "${livre_raiz:-0}" -lt 15 ] || [ "${livre_hd:-0}" -lt 50 ]; then
    log "disco cheio (/ ${livre_raiz}G, hd8t ${livre_hd}G), pausa 1 h"
    "$AVISA" "🚨 AJUDA: produtor do canal Aventuras PAUSADO por disco (/ com ${livre_raiz} GB livres, HD 8 TB com ${livre_hd} GB). Libere espaço; tento de novo a cada hora." >/dev/null 2>&1
    sleep 3600; continue
  fi
  na_fila=$(grep -cv '^\s*$' "$FILA" 2>/dev/null || echo 0)
  if [ "$UMA" = 0 ] && [ "$na_fila" -ge "$ALVO" ]; then
    sleep 1800; continue
  fi

  # retoma episódio que ficou pela metade (reinício do serviço); senão escolhe um novo
  tarefa=""
  [ "$UMA" = 0 ] && tarefa=$(python3 -c "
import json,os
fila=open('$FILA').read() if os.path.exists('$FILA') else ''
for c in json.load(open('privado/candidatos.json')):
    if c.get('status')=='em_producao' and not c.get('teste'):  # episódio de teste de modelo é do outro processo
        pasta=os.path.expanduser('~/projetos/output/memorias-aventura-'+c['slug'])
        if pasta not in fila:
            print(json.dumps({'n':c['n'],'idmat':c['idmat'],'album':c['album'],'slug':c['slug'],'assunto':c['assunto'],
              'area':c.get('area'),'assinante':c.get('assinante',False),'fotos_al1':c.get('fotos_al1'),
              'notificar':[p['idf'] for p in c.get('pessoas',[]) if p['idf']!=4819],'pasta':pasta,'retomada':True},ensure_ascii=False)); break
")
  [ -z "$tarefa" ] && tarefa=$(flock "$TRAVA" python3 escolhe.py)
  rc=$?
  if [ -z "$tarefa" ]; then
    log "sem matéria elegível (rc=$rc), nova busca em 6 h"
    "$AVISA" "Produtor Aventuras: não achei matéria elegível (relato ≥ 250 palavras + ≥ 12 fotos). Busco de novo em 6 h." >/dev/null 2>&1
    sleep 21600; continue
  fi
  n=$(echo "$tarefa" | python3 -c "import json,sys;print(json.load(sys.stdin)['n'])")
  idmat=$(echo "$tarefa" | python3 -c "import json,sys;print(json.load(sys.stdin)['idmat'])")
  slug=$(echo "$tarefa" | python3 -c "import json,sys;print(json.load(sys.stdin)['slug'])")
  pasta=$(echo "$tarefa" | python3 -c "import json,sys;print(json.load(sys.stdin)['pasta'])")
  echo "$tarefa" > "$TAREFAS/$slug.json"
  if [ -n "$MODELO" ]; then  # marca como teste: o laço principal não pode "retomar" este episódio (13/10/2026)
    flock "$TRAVA" python3 -c "
import json,os
p='privado/candidatos.json'; c=json.load(open(p))
for x in c:
    if x['idmat']==$idmat: x['teste']='$MODELO'
json.dump(c,open(p+'.tmp','w'),ensure_ascii=False); os.replace(p+'.tmp',p)"
  fi
  log "início #$n $slug (idmat $idmat)${MODELO:+ modelo $MODELO}${ESFORCO:+ esforço $ESFORCO}"

  {
    echo "Você é o produtor automático da série Memórias de Aventura. Trabalhe sozinho até o fim, sem perguntar nada."
    echo "Leia antes: ~/projetos/aventurasinemavideo/CLAUDE.md (seção Lessons) e PLANO.md."
    echo
    echo "## Tarefa"
    echo '```json'; echo "$tarefa"; echo '```'
    echo "- A pasta do episódio JÁ EXISTE (é um link para o HD de 8 TB): $pasta. Trabalhe nela."
    echo "- Se a pasta já tiver trabalho (retomada), continue de onde parou; não refaça o que está certo."
    echo "- EPISODIO.json: use exatamente n=$n e idmat=$idmat; \"notificar\" = a lista da tarefa."
    echo "- NÃO publique, NÃO suba no B2, NÃO mande e-mail, NÃO mexa em privado/candidatos.json nem em privado/fila_publicar.txt, NÃO faça commit. O laço cuida disso."
    echo "- Quem está na matéria recebe e-mail automático depois (todas as pessoas ligadas, menos o Nei)."
    [ -n "$EXTRA" ] && echo "- $EXTRA"
    echo "- Se a matéria não render um episódio honesto (relato fraco, fotos de outro assunto), escreva o motivo em $pasta/DESISTI.txt e pare."
    echo
    cat PRODUZIR.md
  } > "$TAREFAS/$slug.prompt.md"

  t0=$(date +%s)
  timeout "${TETO_H}h" systemd-run --user --scope -q -p MemoryMax="$MEM" \
    claude -p --permission-mode bypassPermissions --max-turns 400 --output-format json \
    --model "${MODELO:-claude-opus-5-5}" --effort "${ESFORCO:-medium}" \
    < "$TAREFAS/$slug.prompt.md" > "$TAREFAS/$slug.log" 2>&1
  rc=$?
  min=$(( ($(date +%s) - t0) / 60 ))
  custo=$(python3 -c "import json;d=json.load(open('$TAREFAS/$slug.log'));print(round(d.get('total_cost_usd',0),2))" 2>/dev/null)

  if [ -f "$pasta/DESISTI.txt" ]; then
    motivo=$(head -c 300 "$pasta/DESISTI.txt")
    mv -f "$pasta/EPISODIO.json" "$pasta/EPISODIO.descartado.json" 2>/dev/null
    marca "$idmat" descartado "$motivo"; log "#$n $slug descartado em ${min} min: $motivo"
    continue  # descarte não conta como o episódio do teste: segue para a próxima matéria
  fi
  portao=$(python3 verifica_ep.py "$pasta" "$n" "$idmat" 2>&1 | tail -1)
  if [ "${portao#OK}" != "$portao" ]; then
    marca "$idmat" produzido
    if [ "$NA_FILA" = 1 ]; then
      echo "$pasta" >> "$FILA"; log "#$n $slug pronto em ${min} min, US\$ ${custo:-?} → fila ($portao)"
    else
      log "#$n $slug pronto em ${min} min${MODELO:+ ($MODELO)}, US\$ ${custo:-?}, FORA da fila para avaliação ($portao)"
    fi
    [ $falhas -gt 0 ] && "$AVISA" "✅ Produtor Aventuras voltou a produzir (#$n $slug) depois de $falhas falha(s)." >/dev/null 2>&1
    falhas=0
    systemctl --user is-active -q aventuras-fila || systemctl --user start aventuras-fila
  else
    falhas=$((falhas + 1))
    mv -f "$pasta/EPISODIO.json" "$pasta/EPISODIO.falhou.json" 2>/dev/null  # o número volta a ficar livre
    marca "$idmat" erro_producao "rc=$rc $portao"
    log "#$n $slug FALHOU (rc=$rc, ${min} min): $portao"
    "$AVISA" "🚨 AJUDA: produtor do canal Aventuras falhou no #$n ($slug), tentativa seguida $falhas.
Motivo: $portao (rc=$rc, ${min} min)
Log: ~/projetos/aventurasinemavideo/$TAREFAS/$slug.log
Sigo para a próxima matéria$([ $falhas -ge 3 ] && echo ' depois de 30 min de pausa')." >/dev/null 2>&1
    [ $falhas -ge 3 ] && sleep 1800
  fi
  [ "$UMA" = 1 ] && exit 0
done
