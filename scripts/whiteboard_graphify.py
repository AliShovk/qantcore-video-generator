#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Graphify: 5 белых досок под 25-секундный ролик."""
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
BG = (251, 251, 247)
INK = (24, 24, 28)
GREY = (98, 98, 104)
F = '/opt/qantcore/htmlvid/fonts/Caveat.ttf'
OUT = '/opt/qantcore/htmlvid/wb-graphify'
random.seed(9)


def paper():
    im = Image.new('RGB', (W, H), BG)
    noise = Image.effect_noise((W, H), 10).convert('L').filter(ImageFilter.GaussianBlur(0.5))
    im = Image.composite(Image.new('RGB', (W, H), (244, 244, 237)), im,
                         noise.point(lambda v: 34 if v > 145 else 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([36, 36, W - 36, H - 36], radius=26, outline=(212, 212, 206), width=4)
    return im, d


def jit(pts, a=1.6):
    return [(x + random.uniform(-a, a), y + random.uniform(-a, a)) for x, y in pts]


def line(d, pts, w=7, color=INK, passes=2):
    for k in range(passes):
        d.line(jit(pts, 1.2 + k), fill=color, width=w + random.randint(-1, 1), joint='curve')


def box(d, b, w=6, color=INK, r=18):
    for _ in range(2):
        d.rounded_rectangle([b[0] + random.uniform(-1.5, 1.5), b[1] + random.uniform(-1.5, 1.5),
                             b[2] + random.uniform(-1.5, 1.5), b[3] + random.uniform(-1.5, 1.5)],
                            radius=r, outline=color, width=w)


def arrow(d, p1, p2, w=6, color=INK):
    import math
    line(d, [p1, p2], w=w, color=color)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    for s in (0.5, -0.5):
        line(d, [p2, (p2[0] - 30 * math.cos(ang + s), p2[1] - 30 * math.sin(ang + s))], w=w, color=color, passes=1)


def s1():
    im, d = paper()
    d.text((80, 130), 'Graphify', font=ImageFont.truetype(F, 200), fill=INK)
    d.text((86, 350), 'граф знаний для кодового агента', font=ImageFont.truetype(F, 78), fill=GREY)
    box(d, (120, 500, 620, 760))
    d.text((156, 520), '20–30', font=ImageFont.truetype(F, 150), fill=INK)
    d.text((160, 675), 'минут до первого графа', font=ImageFont.truetype(F, 52), fill=GREY)
    d.text((110, 850), 'Python 3.10+ · uv · один репозиторий', font=ImageFont.truetype(F, 58), fill=INK)
    d.text((110, 950), 'ключ модели не нужен для разбора кода', font=ImageFont.truetype(F, 50), fill=GREY)
    im.save(f'{OUT}/1.png')


def s2():
    im, d = paper()
    d.text((80, 110), 'Три команды', font=ImageFont.truetype(F, 140), fill=INK)
    steps = [('1', 'uv tool install graphifyy', 'пакет с двумя y'),
             ('2', 'graphify install --platform claude', 'скилл в агенте'),
             ('3', '/graphify .', 'в чате ассистента')]
    y = 330
    for n, cmd, note in steps:
        box(d, (80, y, 1000, y + 250))
        d.text((110, y + 20), n, font=ImageFont.truetype(F, 90), fill=GREY)
        d.text((190, y + 26), cmd, font=ImageFont.truetype(F, 54), fill=INK)
        d.text((194, y + 120), note, font=ImageFont.truetype(F, 46), fill=GREY)
        y += 290
    im.save(f'{OUT}/2.png')


def s3():
    im, d = paper()
    d.text((80, 110), 'Что получится', font=ImageFont.truetype(F, 140), fill=INK)
    items = ['каталог graphify-out', 'MCP-сервер для агента', 'ответы со ссылками на файлы']
    y = 330
    for t in items:
        d.text((110, y), '·', font=ImageFont.truetype(F, 90), fill=INK)
        d.text((160, y), t, font=ImageFont.truetype(F, 74), fill=INK)
        y += 150
    box(d, (110, 830, 970, 1030))
    d.text((140, 860), 'агент отвечает по вашему репо,', font=ImageFont.truetype(F, 56), fill=INK)
    d.text((140, 940), 'а не пересказывает наугад', font=ImageFont.truetype(F, 56), fill=GREY)
    im.save(f'{OUT}/3.png')


def s4():
    im, d = paper()
    d.text((80, 110), 'Главная ловушка', font=ImageFont.truetype(F, 130), fill=INK)
    d.text((110, 330), 'пакет', font=ImageFont.truetype(F, 70), fill=GREY)
    d.text((110, 400), 'graphifyy', font=ImageFont.truetype(F, 150), fill=INK)
    d.text((110, 580), 'команда', font=ImageFont.truetype(F, 70), fill=GREY)
    d.text((110, 650), 'graphify', font=ImageFont.truetype(F, 150), fill=INK)
    arrow(d, (640, 470), (640, 640))
    d.text((110, 900), 'две буквы y в пакете — иначе не тот пакет', font=ImageFont.truetype(F, 54), fill=GREY)
    im.save(f'{OUT}/4.png')


def s5():
    im, d = paper()
    d.text((110, 520), 'гайд по Graphify', font=ImageFont.truetype(F, 110), fill=GREY)
    d.text((96, 700), 'qantcore.space', font=ImageFont.truetype(F, 175), fill=INK)
    line(d, [(100, 900), (980, 896)], w=7)
    d.text((110, 1000), 'развернуть за полчаса', font=ImageFont.truetype(F, 80), fill=INK)
    im.save(f'{OUT}/5.png')


os.makedirs(OUT, exist_ok=True)
for fn in (s1, s2, s3, s4, s5):
    fn()
print('scenes ok')
