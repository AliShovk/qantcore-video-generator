#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Четыре whiteboard-кадра про AI-SEO: маркер, без персонажа."""
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
BG = (251, 251, 247)
INK = (24, 24, 28)
GREY = (98, 98, 104)
F = '/opt/qantcore/htmlvid/fonts/Caveat.ttf'
OUT = '/opt/qantcore/htmlvid/wb-seo'

random.seed(3)


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


def box(d, box_xy, w=6, color=INK, radius=18):
    x0, y0, x1, y1 = box_xy
    for _ in range(2):
        d.rounded_rectangle([x0 + random.uniform(-1.5, 1.5), y0 + random.uniform(-1.5, 1.5),
                             x1 + random.uniform(-1.5, 1.5), y1 + random.uniform(-1.5, 1.5)],
                            radius=radius, outline=color, width=w)


def arrow(d, p1, p2, w=7, color=INK):
    line(d, [p1, p2], w=w, color=color)
    import math
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    for s in (0.5, -0.5):
        line(d, [p2, (p2[0] - 34 * math.cos(ang + s), p2[1] - 34 * math.sin(ang + s))], w=w, color=color, passes=1)


def scene1():
    im, d = paper()
    f1 = ImageFont.truetype(F, 210)
    f2 = ImageFont.truetype(F, 92)
    d.text((80, 130), 'AI для SEO', font=f1, fill=INK)
    d.text((84, 380), 'пять шагов до контент-плана', font=f2, fill=GREY)
    # цифра 5 в круге
    d.ellipse([300, 620, 780, 1100], outline=INK, width=10)
    d.ellipse([312, 632, 768, 1088], outline=INK, width=5)
    f5 = ImageFont.truetype(F, 380)
    d.text((540, 860), '5', font=f5, fill=INK, anchor='mm')
    d.text((110, 1200), 'запросы · кластеры · план · аудит · отчёт', font=ImageFont.truetype(F, 56), fill=INK)
    d.text((150, 1300), 'Python · pandas · OpenAI API', font=ImageFont.truetype(F, 62), fill=GREY)
    im.save(f'{OUT}/1.png')


def scene2():
    im, d = paper()
    d.text((80, 110), 'Пайплайн', font=ImageFont.truetype(F, 170), fill=INK)
    items = [('1  Сбор данных', 'Search Console, Ahrefs, CSV'),
             ('2  AI-кластеризация', 'смысловые группы'),
             ('3  Контент-план', 'темы, интенты, приоритет'),
             ('4  SEO-аудит', 'парсинг и рекомендации'),
             ('5  Отчёт', 'Markdown и Excel')]
    y = 380
    for i, (t, s) in enumerate(items):
        box(d, (90, y, 990, y + 162))
        d.text((120, y + 14), t, font=ImageFont.truetype(F, 76), fill=INK)
        d.text((124, y + 92), s, font=ImageFont.truetype(F, 48), fill=GREY)
        if i < len(items) - 1:
            arrow(d, (540, y + 152), (540, y + 196), w=6)
        y += 250
    d.text((96, y + 10), 'один прогон вместо трёх таблиц', font=ImageFont.truetype(F, 58), fill=GREY)
    im.save(f'{OUT}/2.png')


def scene3():
    im, d = paper()
    d.text((80, 110), 'Вход и выход', font=ImageFont.truetype(F, 160), fill=INK)
    box(d, (70, 400, 500, 1080))
    box(d, (580, 400, 1010, 1080))
    fh = ImageFont.truetype(F, 68)
    fi = ImageFont.truetype(F, 56)
    d.text((100, 430), 'ВХОД', font=fh, fill=GREY)
    for i, t in enumerate(['semantic_core.csv', 'топ-500 запросов', 'volume · intent']):
        d.text((100, 540 + i * 96), t, font=fi, fill=INK)
    d.text((610, 430), 'ВЫХОД', font=fh, fill=GREY)
    for i, t in enumerate(['clusters.json', 'content_plan.md', 'audit.xlsx']):
        d.text((610, 540 + i * 96), t, font=fi, fill=INK)
    arrow(d, (520, 740), (560, 740), w=8)
    d.text((150, 1180), 'один скрипт вместо ручной сверки', font=ImageFont.truetype(F, 66), fill=INK)
    im.save(f'{OUT}/3.png')


def scene4():
    im, d = paper()
    d.text((110, 520), 'гайд по AI-SEO', font=ImageFont.truetype(F, 110), fill=GREY)
    d.text((96, 700), 'qantcore.space', font=ImageFont.truetype(F, 175), fill=INK)
    line(d, [(100, 900), (980, 896)], w=7)
    d.text((110, 1000), 'разобрать по шагам', font=ImageFont.truetype(F, 84), fill=INK)
    im.save(f'{OUT}/4.png')


os.makedirs(OUT, exist_ok=True)
scene1(); scene2(); scene3(); scene4()
print('scenes ok')
