#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Белая доска с вороной: маркерная графика для whiteboard-animate (v2)."""
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
BG = (251, 251, 247)
INK = (24, 24, 28)
random.seed(7)

F_HAND = '/opt/qantcore/htmlvid/fonts/Caveat.ttf'


def jitter(pts, amp=1.8):
    return [(x + random.uniform(-amp, amp), y + random.uniform(-amp, amp)) for x, y in pts]


def stroke(d, pts, width=8, color=INK, passes=2):
    for p in range(passes):
        d.line(jitter(pts, 1.4 + p), fill=color, width=width + random.randint(-1, 1), joint='curve')


def ring(d, box, width=8, color=INK):
    for _ in range(3):
        b = [box[0] + random.uniform(-1.6, 1.6), box[1] + random.uniform(-1.6, 1.6),
             box[2] + random.uniform(-1.6, 1.6), box[3] + random.uniform(-1.6, 1.6)]
        d.arc(b, 0, 360, fill=color, width=width)


def fill_shape(d, pts, color=INK):
    d.polygon(jitter(pts, 1.2), fill=color)


def crow(d, ox, oy, s=1.0):
    """Силуэт ворона в профиль: заливка + белые линии перьев."""
    P = lambda x, y: (ox + x * s, oy + y * s)
    body = [P(700, 700), P(612, 668), P(536, 596), P(470, 604), P(430, 690),
            P(300, 800), P(120, 862), P(96, 940), P(150, 1000), P(300, 930), P(360, 1006),
            P(470, 1000), P(556, 800), P(612, 748)]
    d.polygon(jitter(body, 1.0), fill=INK)
    # хохолок
    d.polygon([P(500, 620), P(470, 560), P(520, 588), P(512, 540), P(548, 596)], fill=INK)
    # крючок клюва
    d.polygon([P(700, 700), P(690, 742), P(672, 706)], fill=INK)
    # вырезы в хвосте
    d.polygon([P(150, 878), P(232, 900), P(150, 926)], fill=(250, 250, 246))
    d.polygon([P(150, 946), P(232, 962), P(152, 990)], fill=(250, 250, 246))
    # разрез клюва
    d.line([P(612, 748), P(690, 714)], fill=(250, 250, 246), width=int(5 * s))
    # глаз
    d.ellipse([P(512, 612), P(566, 666)], fill=(250, 250, 246))
    d.ellipse([P(530, 630), P(550, 650)], fill=INK)
    # перья крыла
    d.line([P(196, 812), P(470, 862)], fill=(250, 250, 246), width=int(7 * s))
    for i in range(4):
        x0 = 210 + i * 56
        d.arc([P(x0, 820), P(x0 + 140, 966)], 200, 340, fill=(250, 250, 246), width=int(7 * s))
    # лапы
    for dx in (372, 452):
        d.line([P(dx, 1000), P(dx - 6, 1058)], fill=INK, width=int(14 * s))
        for tx in (-44, 0, 44):
            d.line([P(dx - 6, 1058), P(dx - 6 + tx, 1096)], fill=INK, width=int(9 * s))


im = Image.new('RGB', (W, H), BG)
noise = Image.effect_noise((W, H), 10).convert('L').filter(ImageFilter.GaussianBlur(0.5))
im = Image.composite(Image.new('RGB', (W, H), (244, 244, 237)), im,
                     noise.point(lambda v: 34 if v > 145 else 0))
d = ImageDraw.Draw(im)

f_title = ImageFont.truetype(F_HAND, 190)
f_sub = ImageFont.truetype(F_HAND, 66)
f_line = ImageFont.truetype(F_HAND, 72)

d.text((70, 70), 'Ворона', font=f_title, fill=INK)
d.text((82, 268), 'маскот Qantcore', font=f_sub, fill=(96, 96, 102))

crow(d, 230, 200, 1.0)

d.text((110, 1460), 'рисую обзоры и гайды', font=f_line, fill=INK)
d.text((110, 1552), 'на доске, без монтажа', font=f_line, fill=INK)
d.text((110, 1668), 'qantcore.space', font=f_line, fill=(40, 40, 48))

d.rounded_rectangle([36, 36, W - 36, H - 36], radius=26, outline=(212, 212, 206), width=4)
im.save('/tmp/crow.png')
print('saved', im.size)
