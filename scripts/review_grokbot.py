#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ролик по обзору Grok Bot: HTML-графика через Chrome + бот сверху, лого xAI."""
import os
import shutil
import sys

sys.path.insert(0, '/opt/qantcore/minibot')
sys.path.insert(0, '/opt/qantcore/htmlvid')

import render  # noqa: E402
from minibot import MiniBot, sfx  # noqa: E402
from minibot import animations as A  # noqa: E402
from minibot.character import draw_bot  # noqa: E402
from minibot.voice import Narrator  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

OUT = '/opt/qantcore/minibot/output/reviews'
WORK = '/opt/qantcore/htmlvid/grokbot'
ACC, ACC2 = '#8BE8FF', '#B18CFF'

n = Narrator(length_scale=0.88)
lines = [
    'Grok Bot — боты на облачном компьютере: браузер, файлы, терминал.',
    'Доступ только через Cursor: Pro двадцать долларов, Ultra двести.',
    'Триста агентов — миф: один компьютер на пользователя.',
    'Подробнее на сайте qantcore.space.',
]
cues = [n.add(x) for x in lines]
s1, s2, s3 = cues[0][0], cues[1][0], cues[2][0]
f0 = cues[3][0]
duration = cues[3][1] + 1.1

blocks = [
    dict(top=620, **{'in': s1, 'out': s2}, html=f"""
      <div class="label">Что это</div>
      <div class="card chips">
        <div class="chip"><div class="dot"></div>Браузер<span class="sub">ваши сервисы</span></div>
        <div class="chip"><div class="dot"></div>Файлы<span class="sub">рабочий стол</span></div>
        <div class="chip"><div class="dot"></div>Терминал<span class="sub">реальные команды</span></div>
      </div>"""),
    dict(top=620, **{'in': s2, 'out': s3}, html=f"""
      <div class="label">Доступ</div>
      <div class="prices">
        <div class="card price"><div class="val">$20</div><div class="nm">Cursor Pro</div></div>
        <div class="card price"><div class="val">$200</div><div class="nm">Cursor Ultra</div></div>
      </div>
      <div class="note">боты включены в планы Cursor, отдельной подписки нет</div>"""),
    dict(top=600, **{'in': s3, 'out': f0}, html=f"""
      <div class="label">Миф</div>
      <div class="card">
        <div class="big"><span class="strike">300</span> агентов</div>
        <div class="note">в документации — один облачный компьютер на пользователя.
        Это не граница безопасности между ботами.</div>
      </div>"""),
]

spec = dict(
    kick='QANTCORE · ОБЗОР<br>xAI · 2026',
    brand='xAI',
    title='Grok Bot',
    logo='grok-xai.svg',
    subtitle='обзор Grok Bot: тиммейты xAI',
    accent=ACC, accent2=ACC2,
    blocks=blocks,
    cues=[[c[0], c[1]] for c in cues],
    caps=[[cues[0][0], cues[0][1], 'Облачный компьютер для агентов'],
          [cues[1][0], cues[1][1], '$20 Pro и $200 Ultra'],
          [cues[2][0], cues[2][1], '300 агентов — миф'],
          [cues[3][0], cues[3][1], 'Подробнее на сайте']],
    duration=duration,
)

os.makedirs(WORK, exist_ok=True)
shutil.copy('/var/www/qantcore/images/grok-xai.svg', os.path.join(WORK, 'grok-xai.svg'))
os.makedirs(os.path.join(WORK, 'fonts'), exist_ok=True)
shutil.copy('/opt/qantcore/htmlvid/fonts/Manrope.ttf', os.path.join(WORK, 'fonts/Manrope.ttf'))

html = render.build_html(spec, os.path.join(WORK, 'index.html'))

if os.environ.get('PREVIEW'):
    for t in (2.0, 7.5, 12.0, 16.2):
        render._shot((int(t * 100), t, html, WORK))
        os.replace(os.path.join(WORK, f'{int(t * 100):05d}.png'), os.path.join(WORK, f'p{t}.png'))
    print('preview ready', round(duration, 2), 'cues', [round(c[0], 2) for c in cues])
    sys.exit(0)

frames, count = render.render_frames_cdp(html, os.path.join(WORK, 'frames'), duration, 30, port=9333)

# ── бот поверх HTML ────────────────────────────────────────────────────────
BX, BY, SCALE = 250, 1440, 0.96
plan = [(0, 'speak', cues[0][1] - cues[0][0]),
        (s2 - 0.1, 'point', 1.2, 'right'),
        (s3 - 0.1, 'shrug', max(0.6, f0 - s3 - 0.4)),
        (f0, 'point', (duration - f0), 'up')]


def pose_at(t):
    for item in plan:
        st, act, dur = item[0], item[1], item[2]
        direction = item[3] if len(item) > 3 else None
        if st <= t < st + dur:
            return A.action_pose(act, t - st, dur, direction)
    return A.action_pose('idle', 0, 1)


for i in range(count):
    t = i / 30.0
    p = os.path.join(frames, f'{i:05d}.jpg')
    base = Image.open(p).convert('RGBA')
    canvas = Image.new('RGBA', base.size, (0, 0, 0, 0))
    canvas = draw_bot(canvas, pose_at(t), BX, BY, SCALE, 'futuristic')
    if t >= f0 + 0.15:
        k = min(1.0, (t - f0 - 0.15) / 0.9)
        d = ImageDraw.Draw(canvas)
        x1, y1 = BX + 105, BY - 250
        x2, y2 = 560, 700
        xe = x1 + (x2 - x1) * k
        ye = y1 + (y2 - y1) * k
        d.line([(x1, y1), (xe, ye)], fill=(139, 232, 255, 235), width=8)
        if k > 0.9:
            d.polygon([(x2 - 16, y2 + 6), (x2 + 16, y2 + 6), (x2, y2 - 26)], fill=(139, 232, 255, 240))
    base.alpha_composite(canvas)
    base.convert('RGB').save(p, quality=92)

# ── звук ───────────────────────────────────────────────────────────────────
voice = os.path.join(OUT, 'grokbot.wav')
n.write(voice)
bed = sfx.build(duration, cue_starts=[c[0] for c in cues], pings=[cues[0][0] + 0.3],
                out=os.path.join(OUT, 'grokbot-bed.wav'))
mixed = sfx.mix(voice, bed, os.path.join(OUT, 'grokbot-mix.wav'))

final = os.path.join(OUT, 'grokbot.mp4')
render.encode(frames, mixed, final, fps=30)
n.cleanup()
print('=== grokbot', round(duration, 2))
