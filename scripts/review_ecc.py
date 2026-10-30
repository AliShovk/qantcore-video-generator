#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ролик по обзору Everything Claude Code (18 с) + звуковой дизайн."""
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_sys.path.insert(0, _os.path.join(_ROOT, 'pkg'))
import os
import subprocess
import sys

_sys.path.insert(0, _os.path.join(_ROOT, 'pkg'))

from minibot import MiniBot, Number, Scene, Text  # noqa: E402
from minibot import sfx  # noqa: E402
from minibot.objects import Arrow, Panel  # noqa: E402
from minibot.voice import Narrator  # noqa: E402

OUT = '/opt/qantcore/minibot/output/reviews'
ACC = (108, 226, 255)
LIME = (196, 245, 120)
MAG = (255, 130, 200)
DIM = (200, 214, 232)

bot = MiniBot()
n = Narrator(length_scale=0.96)

lines = [
    'ECC — это триста одиннадцать скиллов и семьдесят один субагент.',
    'Оценка восемь и семь десятых — за процедуры и охват.',
    'Ставится одной командой, для Hermes — отдельный профиль.',
    'Подробнее на сайте qantcore.space.',
]
cues = [n.add(x) for x in lines]

scene = Scene(width=1080, height=1920, bot=(280, 1500), scale=1.0, bg='agents',
              palette='futuristic', sprite=False, progress=True)
scene.add_object(Text(80, 170, 'QANTCORE · ОБЗОР', size=28, color=MAG, start=0, dur=n.total()))
scene.add_object(Text(80, 220, 'Everything Claude Code', size=46, start=0, dur=n.total()))

# 1. цифра
scene.add_object(Text(80, 360, 'НАБОР', size=26, color=ACC, start=0.2, dur=cues[1][0] - 0.2))
scene.add_object(Number(311, 'скиллов', '71 субагент · 97 команд · MIT',
                         x=80, y=445, size=210, color=ACC, start=0.3, dur=cues[1][0] - 0.3))

# 2. оценка
s2, e2 = cues[1][0], cues[2][0]
scene.add_object(Text(80, 360, 'ОЦЕНКА', size=26, color=LIME, start=s2, dur=e2 - s2))
scene.add_object(Text(80, 445, '8,7', size=180, color=LIME, start=s2 + 0.05, dur=e2 - s2 - 0.05))
scene.add_object(Text(360, 545, '/ 10', size=48, color=DIM, start=s2 + 0.15, dur=e2 - s2 - 0.15))
scene.add_object(Text(80, 660, 'за процедуры и охват платформ', size=28, color=DIM, bold=False,
                      start=s2 + 0.4, dur=e2 - s2 - 0.4))

# 3. установка
s3, e3 = cues[2][0], cues[3][0]
scene.add_object(Text(80, 360, 'УСТАНОВКА', size=26, color=ACC, start=s3, dur=e3 - s3))
scene.add_object(Text(80, 445, 'npx ecc-universal setup', size=38, color=(255, 255, 255),
                      start=s3 + 0.1, dur=e3 - s3 - 0.1))
scene.add_object(Text(80, 515, 'Hermes: install.sh --profile minimal', size=28, color=DIM, bold=False,
                      start=s3 + 0.5, dur=e3 - s3 - 0.5))
scene.add_object(Text(80, 585, 'меняет ~/.hermes', size=26, color=MAG, start=s3 + 1.1, dur=e3 - s3 - 1.1))

# 4. финал
s4, e4 = cues[3]
dur4 = (e4 - s4) + 0.9
scene._outro_t0 = s4
scene.add_object(Panel(0, 0, 1080, 1920, alpha=234, start=s4, dur=dur4))
scene.add_object(Text(540, 470, 'qantcore.space', size=84, color=ACC, start=s4 + 0.1,
                      dur=dur4 - 0.1, anchor='center'))
scene.add_object(Text(540, 578, 'обзор Everything Claude Code', size=30, color=DIM, bold=False,
                      start=s4 + 0.3, dur=dur4 - 0.3, anchor='center'))
scene.add_object(Arrow((575, 1310), (545, 690), color=ACC, start=s4 + 0.1,
                      dur=max(0.7, min(1.2, dur4 - 0.6)), width=8))

for (a, b), cap in zip(cues, ['311 скиллов и 71 агент', 'Оценка 8,7 из 10', 'Одна команда', 'Подробнее на сайте']):
    scene.caption(cap, a, b, size=38)

scene.at(0, 'speak', cues[0][1] - cues[0][0])
scene.at(cues[1][0], 'point', cues[1][1] - cues[1][0], 'right')
scene.at(cues[2][0], 'think', max(0.5, cues[3][0] - cues[2][0] - 0.6))
scene.at(cues[3][0], 'point', dur4, 'up')
scene.wait(max(0.0, s4 + dur4 - scene.t))

voice = os.path.join(OUT, 'ecc.wav')
n.write(voice)

# подложка + whoosh на смене сцены + пинг на цифрах
total = scene.speed()
bed = sfx.build(total, cue_starts=[c[0] for c in cues],
                pings=[cues[0][0] + 0.25, cues[1][0] + 0.1], out=os.path.join(OUT, 'ecc-bed.wav'))
mixed = sfx.mix(voice, bed, os.path.join(OUT, 'ecc-mix.wav'))

raw = os.path.join(OUT, 'ecc-raw.mp4')
scene.render(raw, audio=mixed)
scene.save(os.path.join(OUT, 'ecc.json'))

final = os.path.join(OUT, 'ecc.mp4')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-vf', 'vignette=PI/4.6',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'copy', final], check=True)
os.remove(raw)
n.cleanup()
print('=== ecc', round(total, 2))
