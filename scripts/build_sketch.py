#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка sketch-ролика: кадры (Chrome) + голос + подложка + SRT."""
import os as _os
import sys as _sys

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_sys.path.insert(0, _os.path.join(_ROOT, 'sketch'))
_sys.path.insert(0, _os.path.join(_ROOT, 'pkg', 'rendering'))
_sys.path.insert(0, _os.path.join(_ROOT, 'pkg'))

import subprocess


import render  # noqa: E402
from minibot import sfx  # noqa: E402

WORK = _os.path.join(_ROOT, 'output', 'sketch-demo')
OUT = _os.path.join(_ROOT, 'output', 'reviews')
FPS = 30
DUR = 20.0

import sketch_context  # noqa: E402  (пересобирает scene.html)

html = f'{WORK}/scene.html'
frames = f'{WORK}/frames'
subprocess.run(['rm', '-rf', frames], check=False)
render.render_frames_cdp(html, frames, DUR, FPS, port=9351)
n = sum(1 for f in os.listdir(frames) if f.endswith('.jpg'))
print('кадров', n)

voice = f'{WORK}/voice.wav'
bed = sfx.build(DUR, cue_starts=[0.45, 3.59, 8.84, 12.57, 16.79], pings=[1.0, 9.0],
                out=f'{WORK}/bed.wav', bed_level=0.03)
mix = sfx.mix(voice, bed, f'{WORK}/mix.wav')
render.encode(frames, mix, f'{OUT}/sketch-context.mp4', fps=FPS)

def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')

cues = [(0.45, 3.35), (3.59, 8.6), (8.84, 12.35), (12.57, 16.55), (16.79, 17.8)]
caps = ['MCP-сервер для агентов', 'Скрипт в песочнице вместо промпта',
        'Экономия 94–100 %', '17 платформ, одна команда', 'Подробнее на сайте qantcore.space']
srt = '\n'.join(f'{i}\n{ts(a)} --> {ts(b)}\n{c}\n' for i, ((a, b), c) in enumerate(zip(cues, caps), 1))
open(f'{OUT}/sketch-context.srt', 'w', encoding='utf-8').write(srt)
for f in ('sketch-context.mp4', 'sketch-context.srt'):
    subprocess.run(['cp', f'{OUT}/{f}', f'/var/www/qantcore/video/reviews/{f}'], check=True)
print('=== sketch-context', DUR)
