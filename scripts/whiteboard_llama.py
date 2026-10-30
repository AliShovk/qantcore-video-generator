#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Llama 3 в whiteboard-формате: 5 кадров + ворона с мозгом поверх."""
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
BG = (251, 251, 247)
INK = (24, 24, 28)
GREY = (98, 98, 104)
F = '/opt/qantcore/htmlvid/fonts/Caveat.ttf'
OUT = '/opt/qantcore/htmlvid/wb-llama'
random.seed(5)


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
    d.text((80, 120), 'Llama 3', font=ImageFont.truetype(F, 220), fill=INK)
    d.text((86, 360), 'локально, без облака', font=ImageFont.truetype(F, 90), fill=GREY)
    box(d, (120, 510, 720, 860))
    d.text((165, 535), '4,7 ГБ', font=ImageFont.truetype(F, 180), fill=INK)
    d.text((168, 762), 'модель 8B в GGUF', font=ImageFont.truetype(F, 56), fill=GREY)
    d.text((110, 940), 'ollama pull llama3.3:8b', font=ImageFont.truetype(F, 66), fill=(30, 30, 34))
    d.text((110, 1050), 'пять минут — и модель отвечает', font=ImageFont.truetype(F, 62), fill=GREY)
    im.save(f'{OUT}/1.png')


def s2():
    im, d = paper()
    d.text((80, 110), 'Сколько весит', font=ImageFont.truetype(F, 150), fill=INK)
    box(d, (80, 380, 520, 760))
    d.text((110, 410), '8B', font=ImageFont.truetype(F, 96), fill=GREY)
    d.text((110, 510), '4,7 ГБ', font=ImageFont.truetype(F, 120), fill=INK)
    d.text((110, 660), 'ноутбук, 8–12 ГБ VRAM', font=ImageFont.truetype(F, 46), fill=GREY)
    box(d, (560, 380, 1000, 760))
    d.text((590, 410), '70B', font=ImageFont.truetype(F, 96), fill=GREY)
    d.text((590, 510), '40 ГБ', font=ImageFont.truetype(F, 120), fill=INK)
    d.text((590, 660), 'Q4_K_M, серверная карта', font=ImageFont.truetype(F, 46), fill=GREY)
    d.text((100, 850), 'Ollama сама подбирает квантование под железо', font=ImageFont.truetype(F, 58), fill=INK)
    im.save(f'{OUT}/2.png')


def s3():
    im, d = paper()
    d.text((80, 110), 'Куда стучится', font=ImageFont.truetype(F, 150), fill=INK)
    ys = 420
    box(d, (110, ys, 470, ys + 160))
    d.text((140, ys + 30), 'Ollama', font=ImageFont.truetype(F, 74), fill=INK)
    d.text((144, ys + 110), 'локальный процесс', font=ImageFont.truetype(F, 40), fill=GREY)
    arrow(d, (480, ys + 80), (560, ys + 80))
    box(d, (570, ys, 970, ys + 160))
    d.text((600, ys + 30), 'порт 11434', font=ImageFont.truetype(F, 74), fill=INK)
    d.text((604, ys + 110), 'REST API', font=ImageFont.truetype(F, 40), fill=GREY)
    arrow(d, (770, ys + 165), (770, ys + 245))
    box(d, (430, ys + 250, 1000, ys + 430))
    d.text((460, ys + 276), 'Open WebUI · llama.cpp', font=ImageFont.truetype(F, 56), fill=INK)
    d.text((460, ys + 336), 'vLLM — сервер под нагрузку', font=ImageFont.truetype(F, 48), fill=INK)
    d.text((464, ys + 380), 'любой OpenAI-совместимый клиент', font=ImageFont.truetype(F, 30), fill=GREY)
    d.text((100, 1120), 'модель одна — оболочек много', font=ImageFont.truetype(F, 56), fill=GREY)
    im.save(f'{OUT}/3.png')


def s4():
    im, d = paper()
    d.text((80, 110), 'Что умеет', font=ImageFont.truetype(F, 150), fill=INK)
    items = ['128K контекст', 'function calling', 'GGUF-кванты', 'CUDA и Metal', 'без облака']
    y = 380
    for t in items:
        d.text((110, y), '·', font=ImageFont.truetype(F, 90), fill=INK)
        d.text((160, y), t, font=ImageFont.truetype(F, 82), fill=INK)
        y += 150
    d.text((110, y + 20), 'агент сам вызывает поиск, код и базу', font=ImageFont.truetype(F, 54), fill=GREY)
    im.save(f'{OUT}/4.png')


def s5():
    im, d = paper()
    d.text((110, 520), 'гайд по Llama 3', font=ImageFont.truetype(F, 110), fill=GREY)
    d.text((96, 700), 'qantcore.space', font=ImageFont.truetype(F, 175), fill=INK)
    line(d, [(100, 900), (980, 896)], w=7)
    d.text((110, 1000), 'развернуть локально', font=ImageFont.truetype(F, 84), fill=INK)
    im.save(f'{OUT}/5.png')


os.makedirs(OUT, exist_ok=True)
for fn in (s1, s2, s3, s4, s5):
    fn()
print('scenes ok')
