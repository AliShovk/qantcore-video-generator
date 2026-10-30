#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерирует qalien.r2d.json: кости, части, анимации (idle/talk/walk)."""
import json
import os

from PIL import Image, ImageDraw

PROJ = '/opt/qantcore/rev2d-projects/qalien'
TEX = f'{PROJ}/textures'

# --- процедурные спрайты (чистые, без зелёного фона) --------------------
def iris(name, size=150, ring=(35, 190, 220), pupil=(12, 20, 34)):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2, 2, size - 3, size - 3], fill=ring + (255,))
    d.ellipse([size * 0.18, size * 0.18, size * 0.82, size * 0.82], fill=pupil + (255,))
    d.ellipse([size * 0.30, size * 0.24, size * 0.44, size * 0.36], fill=(255, 255, 255, 235))
    im.save(f'{TEX}/{name}.png')


def mouth(name, w=120, h=80):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 2, w - 5, h - 3], radius=int(h * 0.42), fill=(70, 18, 30, 255))
    d.ellipse([w * 0.22, h * 0.45, w * 0.78, h * 0.92], fill=(240, 110, 150, 255))
    im.save(f'{TEX}/{name}.png')


iris('irisL2'); iris('irisR2'); mouth('mouth2')
print('процедурные спрайты готовы')

CANVAS = (604, 870)

# --- кости --------------------------------------------------------------
def bone(bid, parent, x, y, length=0, desc=''):
    d = {'id': bid, 'x': x, 'y': y, 'length': length}
    if parent:
        d['parent'] = parent
    if desc:
        d['description'] = desc
    return d

bones = [
    bone('root', None, 300, 812, 0, 'земля'),
    bone('hips', 'root', 0, -140, 0, 'таз'),
    bone('torso', 'hips', 0, 0, 0, 'корпус'),
    bone('head', 'torso', 0, -202, 0, 'шея'),
    bone('armL', 'torso', -150, -177, 120, 'плечо левое'),
    bone('armR', 'torso', 105, -177, 120, 'плечо правое'),
    bone('legL', 'hips', -60, -4, 92, 'бедро левое'),
    bone('legR', 'hips', 60, -4, 92, 'бедро правое'),
    bone('shoeL', 'legL', -10, 92, 0, 'ботинок левый'),
    bone('shoeR', 'legR', 10, 92, 0, 'ботинок правый'),
    bone('antL', 'head', -120, -310, 90, 'антенна левая'),
    bone('antR', 'head', 90, -305, 90, 'антенна правая'),
    bone('lidL', 'head', -122, -225, 0, 'веко левое'),
    bone('lidR', 'head', 100, -232, 0, 'веко правое'),
    bone('mouth', 'head', 0, -88, 0, 'рот'),
]

# --- части --------------------------------------------------------------
def part(pid, parent, tex, x, y, w, h, z, desc=''):
    return {'id': pid, 'parent': parent, 'z': z,
            'shape': {'type': 'image', 'texture': tex, 'x': x, 'y': y, 'w': w, 'h': h, 'cols': 1, 'rows': 1},
            'description': desc}


parts = [
    part('antL', 'antL', 'antL', 82, 25, 114, 143, 5),
    part('antR', 'antR', 'antR', 360, 20, 140, 148, 5),
    part('armL', 'armL', 'armL', 10, 428, 148, 117, 6),
    part('armR', 'armR', 'armR', 396, 430, 166, 110, 6),
    part('legL', 'legL', 'legL', 190, 640, 95, 108, 7),
    part('legR', 'legR', 'legR', 318, 640, 90, 108, 7),
    part('shoeL', 'shoeL', 'shoeL', 128, 714, 154, 74, 8),
    part('shoeR', 'shoeR', 'shoeR', 318, 712, 154, 76, 8),
    part('body', 'torso', 'body', 112, 432, 330, 240, 9),
    part('head', 'head', 'head', 62, 140, 446, 340, 10),
    # рот: зелёная заглушка + спрайт, который масштабируется
    part('mouthCov', 'head', 'mouthCov', 250, 380, 128, 92, 11),
    part('mouth', 'mouth', 'mouth2', 252, 384, 120, 80, 12),
    # веки
    part('lidL', 'lidL', 'lidL', 95, 236, 170, 198, 13),
    part('lidR', 'lidR', 'lidR', 317, 229, 170, 198, 13),
]

textures = [
    {'id': t, 'path': f'textures/{t}.png',
     'width': Image.open(f'{TEX}/{t}.png').width,
     'height': Image.open(f'{TEX}/{t}.png').height}
    for t in ('head', 'body', 'armL', 'armR', 'legL', 'legR', 'shoeL', 'shoeR',
              'antL', 'antR', 'lidL', 'lidR', 'mouthCov', 'mouth2')
]

params = [{'id': 'Breath', 'min': 0, 'max': 1, 'default': 0},
          {'id': 'Blink', 'min': 0, 'max': 1, 'default': 0},
          {'id': 'Talk', 'min': 0, 'max': 1, 'default': 0},
          {'id': 'Walk', 'min': 0, 'max': 1, 'default': 0},
          {'id': 'Sway', 'min': -1, 'max': 1, 'default': 0}]

bindings = [
    # дыхание: корпус чуть вверх-вниз и по ширине
    {'target': 'bone:torso.scaleY', 'params': ['Breath'],
     'keys': [{'at': [0], 'value': 1}, {'at': [1], 'value': 1.03}]},
    {'target': 'bone:torso.scaleX', 'params': ['Breath'],
     'keys': [{'at': [0], 'value': 1}, {'at': [1], 'value': 0.985}]},
    # веки: сверху вниз
    {'target': 'bone:lidL.scaleY', 'params': ['Blink'],
     'keys': [{'at': [0], 'value': 0.02}, {'at': [1], 'value': 1.12}]},
    {'target': 'bone:lidR.scaleY', 'params': ['Blink'],
     'keys': [{'at': [0], 'value': 0.02}, {'at': [1], 'value': 1.12}]},
    # веки прозрачны в покое (иначе тонкая линия поперёк глаз)
    {'target': 'part:lidL.opacity', 'params': ['Blink'],
     'keys': [{'at': [0], 'value': 0}, {'at': [0.15], 'value': 1}, {'at': [1], 'value': 1}]},
    {'target': 'part:lidR.opacity', 'params': ['Blink'],
     'keys': [{'at': [0], 'value': 0}, {'at': [0.15], 'value': 1}, {'at': [1], 'value': 1}]},
    # веки прозрачны в покое (иначе тонкая линия поперёк глаз)
    {'target': 'part:lidL.opacity', 'params': ['Blink'],
     'keys': [{'at': [0], 'value': 0}, {'at': [0.15], 'value': 1}, {'at': [1], 'value': 1}]},
    {'target': 'part:lidR.opacity', 'params': ['Blink'],
     'keys': [{'at': [0], 'value': 0}, {'at': [0.15], 'value': 1}, {'at': [1], 'value': 1}]},
    # рот
    {'target': 'bone:mouth.scaleY', 'params': ['Talk'],
     'keys': [{'at': [0], 'value': 0.12}, {'at': [1], 'value': 1}]},
    # качание антенн
    {'target': 'bone:antL.rotation', 'params': ['Sway'],
     'keys': [{'at': [-1], 'value': 9}, {'at': [0], 'value': 0}, {'at': [1], 'value': -9}]},
    {'target': 'bone:antR.rotation', 'params': ['Sway'],
     'keys': [{'at': [-1], 'value': -7}, {'at': [0], 'value': 0}, {'at': [1], 'value': 7}]},
    # шаг
    {'target': 'bone:legL.rotation', 'params': ['Walk'],
     'keys': [{'at': [0], 'value': 0}, {'at': [1], 'value': 1}]},
]


def keys(seq):
    return [{'t': t, 'v': v, 'ease': e} for t, v, e in seq]


animations = [
    {'id': 'idle', 'duration': 2.4, 'loop': True, 'tracks': [
        {'target': 'param:Breath', 'keys': keys([(0, 0, 'inOutSine'), (1.2, 1, 'inOutSine'), (2.4, 0, 'inOutSine')])},
        {'target': 'param:Sway', 'keys': keys([(0, -0.6, 'inOutSine'), (1.2, 0.6, 'inOutSine'), (2.4, -0.6, 'inOutSine')])},
        {'target': 'bone:head.rotation', 'keys': keys([(0, -1.5, 'inOutSine'), (1.2, 1.5, 'inOutSine'), (2.4, -1.5, 'inOutSine')])},
        {'target': 'param:Blink', 'keys': [{'t': 0, 'v': 0},
                                           {'t': 1.9, 'v': 0},
                                           {'t': 1.98, 'v': 1},
                                           {'t': 2.06, 'v': 1},
                                           {'t': 2.14, 'v': 0},
                                           {'t': 2.4, 'v': 0}]},
    ]},
    {'id': 'talk', 'duration': 0.8, 'loop': True, 'tracks': [
        {'target': 'param:Talk', 'keys': keys([(0, 0.15, 'inOutSine'), (0.2, 1, 'inOutSine'),
                                               (0.4, 0.35, 'inOutSine'), (0.6, 0.8, 'inOutSine'),
                                               (0.8, 0.15, 'inOutSine')])},
        {'target': 'bone:head.rotation', 'keys': keys([(0, 1.2, 'inOutSine'), (0.4, -1.2, 'inOutSine'), (0.8, 1.2, 'inOutSine')])},
    ]},
    {'id': 'wave', 'duration': 1.1, 'loop': True, 'tracks': [
        {'target': 'bone:armR.rotation', 'keys': keys([(0, -18, 'inOutSine'), (0.35, -52, 'inOutSine'),
                                                        (0.7, -18, 'inOutSine'), (0.9, -44, 'inOutSine'), (1.1, -18, 'inOutSine')])},
        {'target': 'bone:armL.rotation', 'keys': keys([(0, 6, 'inOutSine'), (0.55, -6, 'inOutSine'), (1.1, 6, 'inOutSine')])},
        {'target': 'bone:head.rotation', 'keys': keys([(0, 3, 'inOutSine'), (0.55, -3, 'inOutSine'), (1.1, 3, 'inOutSine')])},
    ]},
    {'id': 'walk', 'duration': 0.9, 'loop': True, 'tracks': [
        {'target': 'bone:legL.rotation', 'keys': keys([(0, -20, 'smooth'), (0.45, 22, 'smooth'), (0.9, -20, 'smooth')])},
        {'target': 'bone:legR.rotation', 'offset': 0.45,
         'keys': keys([(0, -20, 'smooth'), (0.45, 22, 'smooth'), (0.9, -20, 'smooth')])},
        {'target': 'bone:armL.rotation', 'keys': keys([(0, 14, 'smooth'), (0.45, -14, 'smooth'), (0.9, 14, 'smooth')])},
        {'target': 'bone:armR.rotation', 'offset': 0.45,
         'keys': keys([(0, -14, 'smooth'), (0.45, 14, 'smooth'), (0.9, -14, 'smooth')])},
        {'target': 'bone:hips.y', 'keys': keys([(0, -140, 'smooth'), (0.22, -147, 'smooth'), (0.45, -140, 'smooth'),
                                                (0.67, -147, 'smooth'), (0.9, -140, 'smooth')])},
        {'target': 'bone:shoeL.rotation', 'keys': keys([(0, 8, 'smooth'), (0.45, -6, 'smooth'), (0.9, 8, 'smooth')])},
        {'target': 'bone:shoeR.rotation', 'offset': 0.45,
         'keys': keys([(0, 8, 'smooth'), (0.45, -6, 'smooth'), (0.9, 8, 'smooth')])},
    ]},
]

rig = {
    'format': 'rev2d', 'version': 1,
    'meta': {'name': 'qalien', 'width': CANVAS[0], 'height': CANVAS[1],
             'background': 'transparent', 'fps': 30,
             'description': 'Q-пришелец: кости рук, ног, антенн, век и рта'},
    'parameters': params,
    'textures': textures,
    'bones': bones,
    'parts': parts,
    'bindings': bindings,
    'animations': animations,
}
open(f'{PROJ}/qalien.r2d.json', 'w', encoding='utf-8').write(json.dumps(rig, ensure_ascii=False, indent=1))
print('написан', f'{PROJ}/qalien.r2d.json', len(parts), 'частей', len(bones), 'костей')
