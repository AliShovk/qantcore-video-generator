#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Пост Manim-ролика Orca: голос по слотам, маскот, подложка, SRT."""
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_sys.path.insert(0, _os.path.join(_ROOT, 'pkg'))
import os
import shutil
import subprocess
import sys

_sys.path.insert(0, _os.path.join(_ROOT, 'pkg'))
_sys.path.insert(0, _os.path.join(_ROOT, 'pkg', 'rendering'))

from PIL import Image  # noqa: E402

from mascot import Mascot  # noqa: E402
from minibot import sfx  # noqa: E402

SRC = '/root/qc-audit/explainer/media/videos/orca_scene/1920p30/OrcaScene.mp4'
WORK = '/opt/qantcore/htmlvid/orca'
OUT = '/opt/qantcore/minibot/output/reviews'
FPS = 30
DUR = 23.03

os.makedirs(WORK, exist_ok=True)
slots = [(0.5, 4.3), (4.4, 9.0), (9.1, 13.0), (13.2, 18.6), (18.8, 21.6)]
texts = ['Orca запускает флот кодовых агентов в параллельных worktrees.',
         'Один промпт расходится на пять агентов, каждый в своей ветке.',
         'Диффы сравниваются, победитель уходит в main.',
         'Сто две тысячи звёзд, пятнадцать тысяч коммитов, лицензия MIT.',
         'Подробнее на сайте qantcore.space.']

# 1. голос: подгоняем темп под слот
parts = []
for i, ((a, b), txt) in enumerate(zip(slots, texts), 1):
    src = f'/tmp/orca_vo{i}.wav'
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                              '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
    need = b - a
    tempo = max(0.85, min(1.18, d / need))
    dst = f'{WORK}/v{i}.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-filter:a', f'atempo={tempo:.3f}',
                    '-ar', '44100', dst], check=True)
    parts.append((a, dst))

# 2. склейка в один трек
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-t', str(DUR), '-ar', '44100', f'{WORK}/silence.wav'], check=True)
inputs = ['-i', f'{WORK}/silence.wav']
filters, mix_in = [], '[0:a]'
for idx, (start, path) in enumerate(parts, 1):
    inputs += ['-i', path]
    delay = int(start * 1000)
    filters.append(f'[{idx}:a]adelay={delay}|{delay}[a{idx}]')
    mix_in += f'[a{idx}]'
fc = ';'.join(filters) + f';{mix_in}amix=inputs={len(parts) + 1}:duration=first,volume=6,alimiter=limit=0.95[out]'
subprocess.run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', fc,
                '-map', '[out]', '-ar', '44100', f'{WORK}/voice.wav'], check=True)

bed = sfx.build(DUR, cue_starts=[s for s, _ in slots], pings=[slots[0][0] + 0.4],
                out=f'{WORK}/bed.wav', bed_level=0.03)
sfx.mix(f'{WORK}/voice.wav', bed, f'{WORK}/mix.wav')

# 3. кадры + маскот
fr = f'{WORK}/frames'
shutil.rmtree(fr, ignore_errors=True)
os.makedirs(fr)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', SRC, '-vf', f'fps={FPS}', f'{fr}/%05d.png'], check=True)
files = sorted(os.listdir(fr))
m = Mascot(width=290, ground=96, coin_size=116)
for i, f in enumerate(files):
    im = Image.open(os.path.join(fr, f)).convert('RGBA')
    m.overlay(im, i / FPS)
    im.convert('RGB').save(os.path.join(fr, f.replace('.png', '.jpg')), quality=92)
    os.remove(os.path.join(fr, f))

# 4. финальный энкод
video = f'{OUT}/orca.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{fr}/%05d.jpg',
                '-i', f'{WORK}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264',
                '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                '-b:a', '160k', '-shortest', video], check=True)

# 5. SRT по слотам
def ts(x):
    h, mm, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{mm:02d}:{s:06.3f}'.replace('.', ',')

srt = '\n'.join(f'{i}\n{ts(a)} --> {ts(b - 0.15)}\n{txt}\n'
                for i, ((a, b), txt) in enumerate(zip(slots, texts), 1))
open(f'{OUT}/orca.srt', 'w', encoding='utf-8').write(srt)
for f in ('orca.mp4', 'orca.srt'):
    subprocess.run(['cp', f'{OUT}/{f}', f'/var/www/qantcore/video/reviews/{f}'], check=True)
print('done')
