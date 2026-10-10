#!/usr/bin/env python3
"""Linha do tempo (bloco = lead + fala + cauda) → linha.json + narracao.wav (cada WAV no seu início)."""
import glob, json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
LEAD, TAIL = .6, .9
dur = lambda f: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
bs = sorted(os.path.basename(f)[:3] for f in glob.glob('voz/B??.wav'))
t, ini = 0.0, {}
for b in bs:
    ini[b] = round(t, 2); t += LEAD + dur(f'voz/{b}.wav') + TAIL
total = round(t + 1.5, 2)
json.dump({'inicio': ini, 'total': total, 'lead': LEAD}, open('linha.json', 'w'), indent=1)
ins = sum([['-i', f'voz/{b}.wav'] for b in ini], [])
f = ';'.join(f'[{k}:a]aresample=44100,adelay={round((ini[b] + LEAD) * 1000)}|{round((ini[b] + LEAD) * 1000)}[a{k}]' for k, b in enumerate(ini))
f += ';' + ''.join(f'[a{k}]' for k in range(len(ini))) + f'amix=inputs={len(ini)}:normalize=0,apad=whole_dur={total}[o]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', f, '-map', '[o]', '-ac', '1', 'narracao.wav'], check=True)
print(ini, total)
