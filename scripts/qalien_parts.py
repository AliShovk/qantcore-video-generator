#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка рига Q-пришельца для Rev2D: текстуры из листа + JSON с костями."""
import json
import os
from collections import deque

from PIL import Image, ImageDraw, ImageFilter

SRC = '/tmp/q_char.png'
PROJ = '/opt/qantcore/rev2d-projects/qalien'
TEX = f'{PROJ}/textures'
os.makedirs(TEX, exist_ok=True)

img = Image.open(SRC).convert('RGBA')
W, H = img.size
print('canvas', W, H)


def flood_alpha(im, thr=726):
    """Убрать белый фон, связанный с краем bbox."""
    a = im.convert('RGB')
    px = a.load()
    w, h = a.size
    light = [[sum(px[x, y][:3]) > thr for x in range(w)] for y in range(h)]
    vis = [[False] * w for _ in range(h)]
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if light[y][x]:
                vis[y][x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if light[y][x] and not vis[y][x]:
                vis[y][x] = True; dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and light[ny][nx] and not vis[ny][nx]:
                vis[ny][nx] = True; dq.append((ny, nx))
    import numpy as np
    mask = Image.fromarray(np.array([[0 if vis[y][x] else 255 for x in range(w)] for y in range(h)], dtype='uint8'))
    mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    out = im.copy(); out.putalpha(mask)
    return out


def cut(name, box, mode='auto', keep_bg=False):
    x0, y0, x1, y1 = box
    part = img.crop((x0, y0, x1, y1))
    if not keep_bg:
        part = flood_alpha(part)
    part.save(f'{TEX}/{name}.png')
    print(f'{name:12s} {part.size} -> textures/{name}.png')
    return part.size


# --- текстуры -----------------------------------------------------------
sizes = {}
sizes['head'] = cut('head', (62, 140, 508, 480))
sizes['body'] = cut('body', (112, 432, 442, 672))
sizes['armL'] = cut('armL', (10, 428, 158, 545))
sizes['armR'] = cut('armR', (396, 430, 562, 540))
sizes['legL'] = cut('legL', (190, 640, 285, 748))
sizes['legR'] = cut('legR', (318, 640, 408, 748))
sizes['shoeL'] = cut('shoeL', (128, 714, 282, 788))
sizes['shoeR'] = cut('shoeR', (318, 712, 472, 788))

# углы ботинок: убрать остатки белого у рамки
import numpy as _np
for _n in ('shoeL', 'shoeR'):
    _im = Image.open(f'{TEX}/{_n}.png').convert('RGBA')
    _a = _np.asarray(_im).copy()
    _h, _w = _a.shape[:2]
    _border = 8
    _mask = _np.zeros((_h, _w), bool)
    _mask[:_border, :] = True; _mask[-_border:, :] = True
    _mask[:, :_border] = True; _mask[:, -_border:] = True
    _white = (_a[:, :, :3] > 244).all(axis=2)
    _a[:, :, 3] = _np.where(_mask & _white, 0, _a[:, :, 3])
    Image.fromarray(_a).save(f'{TEX}/{_n}.png')
sizes['antL'] = cut('antL', (82, 25, 196, 168))
sizes['antR'] = cut('antR', (360, 20, 500, 168))

# накладки: веки, белки, рот
def solid(name, size, color, ellipse=True, radius=30):
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if ellipse:
        d.ellipse([0, 0, size[0] - 1, size[1] - 1], fill=color)
    else:
        d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=color)
    im.save(f'{TEX}/{name}.png')
    return size

def lid(name, w=170, h=198, green=(166, 216, 84)):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, w - 1, h - 1], fill=green + (255,))
    d.arc([12, h - 74, w - 12, h + 40], 200, 340, fill=(30, 40, 45, 255), width=7)
    im.save(f'{TEX}/{name}.png')
    return (w, h)

sizes['lidL'] = lid('lidL')
sizes['lidR'] = lid('lidR')
sizes['eyeL'] = solid('eyeL', (150, 175), (255, 255, 255, 255))
sizes['eyeR'] = solid('eyeR', (150, 175), (255, 255, 255, 255))
# заглушка рта: вертикальный градиент кожи, снятый выше и ниже рта
head_img = Image.open(f'{TEX}/head.png').convert('RGBA')
cx = 300 - 62
top_c = head_img.getpixel((cx, 372 - 140))[:3]
bot_c = head_img.getpixel((cx, 476 - 140))[:3]
cw, ch = 124, 92
patch_ = Image.new('RGBA', (cw, ch))
pd = ImageDraw.Draw(patch_)
for yy in range(ch):
    k = yy / (ch - 1)
    col = tuple(int(top_c[i] + (bot_c[i] - top_c[i]) * k) for i in range(3)) + (255,)
    pd.line([(0, yy), (cw, yy)], fill=col)
mask = Image.new('L', (cw, ch), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=28, fill=255)
patch_.putalpha(mask.filter(ImageFilter.GaussianBlur(3)))
patch_.save(f'{TEX}/mouthCov.png')
sizes['mouthCov'] = patch_.size
sizes['mouth'] = cut('mouth', (252, 382, 372, 462))
sizes['irisL'] = cut('irisL', (108, 262, 250, 405))
sizes['irisR'] = cut('irisR', (330, 255, 470, 398))

meta = dict(w=W, h=H)
json.dump({'sizes': sizes, 'canvas': [W, H]}, open(f'{PROJ}/parts.json', 'w'), indent=1)
print('готово', len(sizes))
