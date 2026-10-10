#!/bin/bash
# Trilha: "Acima das Nuvens" (abre) → "Rumo ao Horizonte" faixa 2 (miolo) → "Acima das Nuvens" faixa 2 (fecho),
# em crossfade, sob a narração com ducking. Saída: trilha.wav (narração + música), duração da linha do tempo.
set -e
D=$(dirname "$(readlink -f "$0")"); cd "$D"
M=~/projetos/output/musicas
T=$(python3 -c "import json;print(json.load(open('linha.json'))['total'])")
ffmpeg -v error -y -i $M/balao-cinema-20260818/faixa-1.mp3 -i $M/balao-exploracao-20260818/faixa-2.mp3 \
  -i $M/balao-cinema-20260818/faixa-2.mp3 -filter_complex "[0][1]acrossfade=d=4[x];[x][2]acrossfade=d=5[m]" -map "[m]" -ar 44100 musica.wav
MD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 musica.wav)
# o fecho da faixa 2 de "Acima das Nuvens" tem que coincidir com o fim do filme: corta do meio se sobrar
ffmpeg -v error -y -i narracao.wav -i musica.wav -filter_complex "
[0]aresample=44100,apad,atrim=0:$T,asplit=2[v][sc];
[1]atrim=start=$(python3 -c "print(max(0,$MD-$T))"),asetpts=PTS-STARTPTS,atrim=0:$T,volume=0.34,afade=t=in:d=2,afade=t=out:st=$(python3 -c "print($T-4)"):d=4[m];
[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=80:release=600[md];
[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-15:TP=-1.5[a]" -map "[a]" -ar 44100 trilha.wav
ls -l trilha.wav; echo "musica $MD s, filme $T s"
