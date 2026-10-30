#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ролик с маскотом Fox: кадры из Rev2D + рукописный текст + голос."""
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
    'Это новый маскот Qantcore — лис по имени Фокс.',
    'Он дышит, моргает, говорит и поворачивает голову.',
    'Риг собран из одной картинки в Rev2D, без ручной сборки слоёв.',
    'Подробнее на сайте qantcore.space.',
]
n = Narrator(speaker='eugene', lead=0.5, gap=0.3)
cues = [n.add(x) for x in lines]
DUR = cues[-1][1] + 3.4
n.write(f'{WORK}/voice.wav')
n.cleanup()
C = [c[0] for c in cues]

frames = sorted(f for f in os.listdir(f'{WORK}/anim2') if f.endswith('.png'))
FOX = [Image.open(f'{WORK}/anim2/{f}').convert('RGBA') for f in frames]
FOX = [im.resize((int(im.width * 1.12), int(im.height * 1.12)), Image.LANCZOS) for im in FOX]
fw, fh = FOX[0].size


def font(sz):
    return ImageFont.truetype(FONT, sz)


def hand_text(base, xy, s, size, color, rot=-1.6, anchor='la'):
    pad = 60
    w = int(len(s) * size * 0.66) + pad * 2
    h = int(size * 1.9)
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((pad, int(size * 0.35)), s, font=font(size), fill=color + (255,), anchor='la')
    layer = layer.rotate(rot, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (int(xy[0] - pad), int(xy[1] - size * 0.35)))


def swoosh(base, x, y, w, color, width=7, seed=1):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(base)
    pts = []
    for i in range(0, w, 18):
        pts.append((x + i, y + rnd.randint(-3, 4) + int(6 * (i / w))))
    d.line(pts, fill=color + (255,), width=width, joint='curve')


def build_frame(t):
    im = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)

    # шапка
    hand_text(im, (78, 120), 'QANTCORE', 96, INK, rot=-1.4)
    swoosh(im, 84, 232, 420, ORANGE, 8, 3)
    hand_text(im, (82, 250), 'новый маскот', 46, GREY, rot=-1.0)

    # лиса справа, кадры по кругу
    fi = int((t * FPS) % len(FOX))
    fox = FOX[fi]
    im.alpha_composite(fox, (W - fw - 70, H - fh - 360))

    # подписи слева, появляются по репликам
    items = [
        (C[0] + 0.1, 'Фокс', 104, INK, 430, -1.8),
        (C[0] + 0.4, 'лис-маскот Qantcore', 44, GREY, 520, -1.2),
        (C[1] + 0.1, 'дышит · моргает', 52, TEAL, 640, -1.6),
        (C[1] + 0.5, 'говорит · смотрит', 52, TEAL, 706, -1.6),
        (C[2] + 0.1, 'риг из одной', 50, ORANGE, 830, -1.5),
        (C[2] + 0.4, 'картинки — Rev2D', 50, ORANGE, 890, -1.5),
    ]
    for t0, s, sz, col, y, rot in items:
        if t >= t0:
            k = min(1.0, (t - t0) / 0.35)
            hand_text(im, (80, y), s, sz, col, rot=rot) if k > 0.5 else None

    # подпись-субтитр
    cap = None
    for (a, b), c in zip(cues, ['это Фокс', 'дышит, моргает, говорит', 'риг из одной картинки', 'подробнее на сайте']):
        if a <= t <= b:
            cap = c
    if cap:
        hand_text(im, (80, 1600), cap, 56, INK, rot=-1.2)

    # финал
    F = DUR - 3.0
    if t >= F:
        k = min(1.0, (t - F) / 0.5)
        panel = Image.new('RGBA', (W, H), (255, 255, 255, int(255 * k)))
        im.alpha_composite(panel)
        hand_text(im, (110, 760), 'qantcore.space', 132, INK, rot=-1.6)
        swoosh(im, 116, 906, 700, TEAL, 10, 7)
        hand_text(im, (118, 940), 'обзоры и гайды по AI-агентам', 44, GREY, rot=-1.0)
    return im.convert('RGB')


bed = sfx.build(DUR, cue_starts=C, pings=[C[0] + 0.3], out=f'{WORK}/bed.wav', bed_level=0.03)
mix = sfx.mix(f'{WORK}/voice.wav', bed, f'{WORK}/mix.wav')

fd = f'{WORK}/video_frames'
os.makedirs(fd, exist_ok=True)
nfr = int(DUR * FPS)
for i in range(nfr):
    build_frame(i / FPS).save(f'{fd}/{i:05d}.jpg', quality=92)
print('кадров', nfr, 'длительность', round(DUR, 2))

subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{fd}/%05d.jpg',
                '-i', mix, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest',
                f'{OUT}/fox-mascot.mp4'], check=True)


def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


caps = ['это Фокс, новый маскот Qantcore', 'дышит, моргает, говорит',
        'риг собран из одной картинки в Rev2D', 'Подробнее на сайте qantcore.space']
srt = '\n'.join(f'{i}\n{ts(a)} --> {ts(b)}\n{c}\n' for i, ((a, b), c) in enumerate(zip(cues, caps), 1))
open(f'{OUT}/fox-mascot.srt', 'w', encoding='utf-8').write(srt)
for f in ('fox-mascot.mp4', 'fox-mascot.srt'):
    subprocess.run(['cp', f'{OUT}/{f}', f'/var/www/qantcore/video/reviews/{f}'], check=True)
print('=== fox-mascot', round(DUR, 2))
