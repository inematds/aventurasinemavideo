#!/bin/bash
# Gera um WAV por bloco do roteiro (voz nei, chatterbox 0.6/0.6). Idempotente.
D=$(dirname "$(readlink -f "$0")")
mkdir -p "$D/voz"
python3 - "$D/roteiro.md" "$D/voz" <<'EOF' > "$D/voz/blocos.tsv"
import re,sys
t=open(sys.argv[1]).read()
for m in re.finditer(r'^(B\d\d)[^—]*— (.+)$', t, re.M):
    print(m.group(1)+'\t'+m.group(2).strip())
EOF
while IFS=$'\t' read -r id txt; do
  [ -s "$D/voz/$id.wav" ] && continue
  tmp="$D/voz/tmp_$id"; rm -rf "$tmp"; mkdir -p "$tmp"
  (cd ~/projetos/inemavox && python3 tts_direct.py --text "$txt" --lang pt --engine chatterbox \
     --ref ~/projetos/timesmkt3/media/voice-refs/nei.wav --exaggeration 0.6 --cfg-weight 0.6 --outdir "$tmp" </dev/null) \
     > "$tmp/log.txt" 2>&1
  f="$tmp/generated.wav"; [ -s "$f" ] || f=""  # só a saída do TTS: a pasta também tem ref_converted.wav (amostra da voz)
  if [ -n "$f" ]; then mv "$f" "$D/voz/$id.wav"; echo "ok $id"; else echo "FALHOU $id"; tail -3 "$tmp/log.txt"; fi
done < "$D/voz/blocos.tsv"
