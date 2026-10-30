#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ролик про Q-пришельца: клипы Rev2D (idle/talk/wave/walk) + текст + голос."""
import os
import random
import subprocess
import sys

sys.path.insert(0, '/opt/qantcore/minibot')

from minibot import sfx  # noqa: E402
from minibot.voice import Narrator  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

W, H, FPS = 1080, 1920, 30
R = '/opt/qantcore/rev2d-projects/qalien'
OUT = '/opt/qantcore/minibot/output/reviews'
FONT = '/opt/qantcore/htmlvid/fonts/Caveat.ttf'
INK, GREY, TEAL, ORANGE = (18, 22, 28), (122, 132, 143), (14, 159, 138), (234, 88, 12)

lines = [
    'Новый персонаж Qantcore — зелёный пришелец с антеннами.',
    'Моргает и говорит: глаза и рот двигаются.',
    'Машет рукой — рука на своей кости.',
    'Ноги шагают: походка собрана на костях в Rev2D.',
    'Подробнее на сайте qantcore.space.',
]
n = Narrator(speaker='eugene', lead=0.4, gap=0.25)
cues = [n.add(x) for x in lines]
n.write(f'{R}/voice.wav')
n.cleanup()
C = [c[0] for x in [0] for c in cues]
DUR = cues[-1][1] + 3.2

SEG = [('idle', C[0], C[1]), ('talk', C[1], C[2]), ('wave', C[2], C[3]),
       ('walk', C[3], C[4])]


def load(name):
    d = f'{R}/anim/{name}'
    fs = sorted(f for f in os.listdir(d) if f.endswith('.png'))
    return [Image.open(f'{d}/{f}').convert('RGBA') for f in fs]


CLIPS = {k: load(k) for k in ('idle', 'talk', 'wave', 'walk')}
SCALE = 1.16
for k in CLIPS:
    CLIPS[k] = [im.resize((int(im.width * SCALE), int(im.height * SCALE)), Image.LANCZOS) for im in CLIPS[k]]
CW, CH = CLIPS['idle'][0].size
import numpy as _np
_bb = _np.asarray(CLIPS['idle'][0])[:, :, 3] > 10
_rows = _np.where(_bb.any(axis=1))[0]
CONTENT_BOTTOM = int(_rows.max())
GROUND = 1740


def font(sz):
    return ImageFont.truetype(FONT, sz)


def hand(base, xy, s, size, color, rot=-1.5):
    pad = 70
    w = int(len(s) * size * 0.66) + pad * 2
    h = int(size * 2.1)
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad, int(size * 0.4)), s, font=font(size), fill=color + (255,))
    layer = layer.rotate(rot, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (int(xy[0] - pad), int(xy[1] - size * 0.4)))


def tick(base, x, y, color):
    d = ImageDraw.Draw(base)
    d.line([(x, y), (x + 12, y + 14), (x + 40, y - 16)], fill=color + (255,), width=7, joint='curve')


def seg_at(t):
    for name, a, b in SEG:
        if a <= t < b:
            return name, (t - a)
    return 'idle', 0.0


def frame(t):
    im = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    hand(im, (70, 126), 'Q-пришелец', 112, INK, rot=-1.6)
    d = ImageDraw.Draw(im)
    d.line([(82, 236), (470, 232)], fill=ORANGE + (255,), width=9)
    hand(im, (76, 258), 'персонаж на костях', 50, GREY, rot=-1.0)

    items = [(C[0] + 0.1, 'глаза · рот', 640, TEAL),
             (C[1] + 0.1, 'антенны', 706, TEAL),
             (C[2] + 0.1, 'руки', 772, TEAL),
             (C[3] + 0.1, 'ноги · шаг', 838, TEAL)]
    for t0, s, y, col in items:
        if t >= t0:
            tick(im, 82, y - 14, col)
            hand(im, (140, y), s, 56, col, rot=-1.3)

    name, lt = seg_at(t)
    clip = CLIPS[name]
    img = clip[int(lt * FPS) % len(clip)]
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([W - CW + 30, GROUND - 26, W - 20, GROUND + 18],
                                   fill=(20, 24, 30, 26))
    im.alpha_composite(shadow)
    im.alpha_composite(img, (W - CW - 30, GROUND - CONTENT_BOTTOM))

    cap = None
    for (a, b), c in zip(cues, ['новый персонаж', 'моргает и говорит',
                                'машет рукой', 'шагает ногами', 'подробнее на сайте']):
        if a <= t <= b:
            cap = c
    if cap:
        hand(im, (76, 1660), cap, 58, INK, rot=-1.2)

    F = DUR - 2.9
    if t >= F:
        k = min(1.0, (t - F) / 0.5)
        im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * k))))
        hand(im, (104, 740), 'qantcore.space', 128, INK, rot=-1.5)
        d.line([(112, 884), (800, 878)], fill=TEAL + (255,), width=10)
        hand(im, (110, 916), 'обзоры и гайды по AI-агентам', 44, GREY, rot=-1.0)
    return im.convert('RGB')


bed = sfx.build(DUR, cue_starts=C, pings=[C[0] + 0.3], out=f'{R}/bed.wav', bed_level=0.03)
mix = sfx.mix(f'{R}/voice.wav', bed, f'{R}/mix.wav')

fd = f'{R}/frames_video'
os.makedirs(fd, exist_ok=True)
for f in os.listdir(fd):
    os.remove(os.path.join(fd, f))
nfr = int(DUR * FPS)
for i in range(nfr):
    frame(i / FPS).save(f'{fd}/{i:05d}.jpg', quality=92)
print('кадров', nfr, 'секунд', round(DUR, 2))

subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{fd}/%05d.jpg',
                '-i', mix, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest',
                f'{OUT}/qalien.mp4'], check=True)


def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


caps = ['Новый персонаж Qantcore', 'Глаза и рот двигаются', 'Рука машет',
        'Ноги шагают', 'Подробнее на сайте qantcore.space']
srt = '\n'.join(f'{i}\n{ts(a)} --> {ts(b)}\n{c}\n' for i, ((a, b), c) in enumerate(zip(cues, caps), 1))
open(f'{OUT}/qalien.srt', 'w', encoding='utf-8').write(srt)
for f in ('qalien.mp4', 'qalien.srt'):
    subprocess.run(['cp', f'{OUT}/{f}', f'/var/www/qantcore/video/reviews/{f}'], check=True)
print('=== qalien', round(DUR, 2))
