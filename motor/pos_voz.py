#!/usr/bin/env python3
"""Pós da narração: corta cada WAV na última palavra transcrita (o chatterbox às vezes balbucia no fim),
atempo 1.06 + loudnorm; depois transcreve o resultado com tempos por palavra (palavras.json) e imprime o texto
para conferir contra o roteiro. Originais ficam em voz/bruto/."""
import glob, json, os, shutil, subprocess, sys
import whisper

D = os.path.dirname(os.path.abspath(__file__))
os.makedirs(f'{D}/voz/bruto', exist_ok=True)
m = whisper.load_model('medium')
fim = json.load(open(f'{D}/voz/fim_falas.json')) if os.path.exists(f'{D}/voz/fim_falas.json') else {}
pal = json.load(open(f'{D}/palavras.json')) if os.path.exists(f'{D}/palavras.json') else {}
alvo = sys.argv[1:]  # ex.: B01 B07 (sem argumento = todos)
for bb in sorted(glob.glob(f'{D}/voz/bruto/B??.wav') + glob.glob(f'{D}/voz/B??.wav')):
    b = os.path.basename(bb)[:3]
    f = f'{D}/voz/{b}.wav'
    if (alvo and b not in alvo) or b in [k for k in pal if not alvo]:
        continue
    bruto = f'{D}/voz/bruto/{b}.wav'
    if not os.path.exists(bruto):
        shutil.move(f, bruto)
    r = m.transcribe(bruto, language='pt', word_timestamps=True)
    ws = [w for s in r['segments'] for w in s['words']]
    corte = ws[-1]['end'] + .3
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', bruto, '-t', f'{corte:.2f}', '-af',
                    'atempo=1.06,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st=%.2f:d=0.15' % (corte / 1.06 - .15),
                    '-ar', '44100', f], check=True)
    r2 = m.transcribe(f, language='pt', word_timestamps=True)
    pal[b] = [(w['word'].strip(), round(w['start'], 2)) for s in r2['segments'] for w in s['words']]
    fim[b] = round(r2['segments'][-1]['end'], 2)
    print(b, fim[b], '|', r2['text'].strip(), flush=True)
json.dump(pal, open(f'{D}/palavras.json', 'w'), ensure_ascii=False, indent=0)
json.dump(fim, open(f'{D}/voz/fim_falas.json', 'w'))
