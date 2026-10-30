#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Фокс меньше + идёт: кадры Rev2D, шаг с покачиванием, пыль, голос."""
import math
import os
import random
import subprocess
import sys

sys.path.insert(0, '/opt/qantcore/minibot')

from minibot import sfx  # noqa: E402
from minibot.voice import Narrator  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

W, H, FPS = 1080, 1920, 30
WORK = '/opt/qantcore/rev2d-projects/fox'
OUT = '/opt/qantcore/minibot/output/reviews'
FONT = '/opt/qantcore/htmlvid/fonts/Caveat.ttf'
INK, GREY, TEAL, ORANGE = (18, 22, 28), (122, 132, 143), (14, 159, 138), (234, 88, 12)

lines = [
    'Фокс стал меньше — и теперь ходит.',
    'Шаги, покачивание, дыхание и моргание — в одном риге.',
    'Риг собран из одной картинки в Rev2D.',
    'Подробнее на сайте qantcore.space.',
]
n = Narrator(speaker='eugene', lead=0.5, gap=0.3)
cues = [n.add(x) for x in lines]
DUR = cues[-1][1] + 3.2
n.write(f'{WORK}/voice2.wav')
n.cleanup()
C = [c[0] for c in cues]

SCALE = 0.66
frames = sorted(f for f in os.listdir(f'{WORK}/anim2') if f.endswith('.png'))
FOX = []
for f in frames:
    im = Image.open(f'{WORK}/anim2/{f}').convert('RGBA')
    FOX.append(im.resize((int(im.width * SCALE), int(im.height * SCALE)), Image.LANCZOS))
fw, fh = FOX[0].size
GROUND = H - 340           # линия, по которой идёт


def font(sz):
    return ImageFont.truetype(FONT, sz)


def hand_text(base, xy, s, size, color, rot=-1.6):
    pad = 80
    w = int(len(s) * size * 0.66) + pad * 2
    h = int(size * 2.2)
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad, int(size * 0.4)), s, font=font(size), fill=color + (255,))
    layer = layer.rotate(rot, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (int(xy[0] - pad), int(xy[1] - size * 0.4)))


def swoosh(base, x, y, w, color, width=7, seed=1):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(base)
    pts = [(x + i, y + rnd.randint(-3, 4) + int(6 * (i / w))) for i in range(0, w, 18)]
    d.line(pts, fill=color + (255,), width=width, joint='curve')


def walk_x(t):
    """Идёт слева направо всю первую половину, дальше стоит и говорит."""
    left, right = -fw - 20, W - 250
    t0, t1 = 0.4, C[1] + 0.6
    if t < t0:
        return left, 0.0
    if t < t1:
        k = (t - t0) / (t1 - t0)
        base = left + (right - left) * (k ** 1.05)
        return base + 7.0 * math.sin(t * 2 * math.pi * 2.0), 1.0
    return right, 0.0


def build_frame(t):
    im = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)

    hand_text(im, (78, 118), 'QANTCORE', 92, INK, rot=-1.4)
    swoosh(im, 84, 226, 400, ORANGE, 8, 3)
    hand_text(im, (82, 244), 'маскот Фокс', 46, GREY, rot=-1.0)

    x, walking = walk_x(t)
    bob = 0
    tilt = 0.0
    if walking:
        phase = t * 2 * math.pi * 2.0        # два шага в секунду
        bob = int(-abs(math.sin(phase)) * 30)
        tilt = 4.2 * math.sin(phase)
        # пыль у ног
        for k in range(3):
            ph = (phase + k * 2.1) % (2 * math.pi)
            if ph < 1.0:
                r = 8 + ph * 34
                a = int(170 * (1 - ph / 1.0))
                d.ellipse([x + fw * 0.5 + k * 10 - r, GROUND - r * 0.45,
                           x + fw * 0.5 + k * 10 + r, GROUND + r * 0.45],
                          fill=GREY + (a,))
        # тень
        d.ellipse([x + fw * 0.18, GROUND - 10, x + fw * 0.86, GROUND + 16],
                  fill=(20, 24, 30, 26))

    fox = FOX[int((t * FPS) % len(FOX))]
    if tilt:
        fox = fox.rotate(tilt, resample=Image.BICUBIC, expand=False)
    im.alpha_composite(fox, (int(x), int(GROUND - fox.height - 8 + bob)))

    items = [
        (C[0] + 0.2, 'меньше', 96, INK, 400, -1.8),
        (C[0] + 0.5, 'и на своих ногах', 44, GREY, 486, -1.2),
        (C[1] + 0.1, 'шаг · дыхание', 52, TEAL, 640, -1.6),
        (C[1] + 0.5, 'моргание · взгляд', 52, TEAL, 706, -1.6),
        (C[2] + 0.1, 'один риг', 50, ORANGE, 840, -1.5),
        (C[2] + 0.4, 'из одной картинки', 50, ORANGE, 900, -1.5),
    ]
    for t0, s, sz, col, y, rot in items:
        if t >= t0 + 0.2:
            hand_text(im, (80, y), s, sz, col, rot=rot)

    cap = None
    for (a, b), c in zip(cues, ['меньше и ходит', 'шаг, дыхание, моргание',
                                'риг из одной картинки', 'подробнее на сайте']):
        if a <= t <= b:
            cap = c
    if cap:
        hand_text(im, (80, 1680), cap, 54, INK, rot=-1.2)

    F = DUR - 2.9
    if t >= F:
        k = min(1.0, (t - F) / 0.5)
        im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * k))))
        hand_text(im, (110, 760), 'qantcore.space', 130, INK, rot=-1.6)
        swoosh(im, 116, 900, 690, TEAL, 10, 7)
        hand_text(im, (118, 936), 'обзоры и гайды по AI-агентам', 44, GREY, rot=-1.0)
    return im.convert('RGB')


bed = sfx.build(DUR, cue_starts=C, pings=[C[0] + 0.3], out=f'{WORK}/bed2.wav', bed_level=0.03)
mix = sfx.mix(f'{WORK}/voice2.wav', bed, f'{WORK}/mix2.wav')

fd = f'{WORK}/frames_walk'
os.makedirs(fd, exist_ok=True)
for f in os.listdir(fd):
    os.remove(os.path.join(fd, f))
nfr = int(DUR * FPS)
for i in range(nfr):
    build_frame(i / FPS).save(f'{fd}/{i:05d}.jpg', quality=92)
print('кадров', nfr, 'длительность', round(DUR, 2))

subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{fd}/%05d.jpg',
                '-i', mix, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest',
                f'{OUT}/fox-walk.mp4'], check=True)


def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


caps = ['Фокс меньше — и ходит', 'шаг, покачивание, дыхание и моргание',
        'риг собран из одной картинки в Rev2D', 'Подробнее на сайте qantcore.space']
srt = '\n'.join(f'{i}\n{ts(a)} --> {ts(b)}\n{c}\n' for i, ((a, b), c) in enumerate(zip(cues, caps), 1))
open(f'{OUT}/fox-walk.srt', 'w', encoding='utf-8').write(srt)
for f in ('fox-walk.mp4', 'fox-walk.srt'):
    subprocess.run(['cp', f'{OUT}/{f}', f'/var/www/qantcore/video/reviews/{f}'], check=True)
print('=== fox-walk', round(DUR, 2))
