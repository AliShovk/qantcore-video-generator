#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
import sys as _sys

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_sys.path.insert(0, _os.path.join(_ROOT, 'sketch'))
_sys.path.insert(0, _os.path.join(_ROOT, 'pkg', 'rendering'))
_sys.path.insert(0, _os.path.join(_ROOT, 'pkg'))

from sketch import AMBER, BLUE, GREY, INK, ORANGE, Sketch, TEAL, YELLOW  # noqa: E402

WORK = _os.path.join(_ROOT, 'output', 'sketch-demo')
os.makedirs(WORK, exist_ok=True)
os.makedirs(f'{WORK}/fonts', exist_ok=True)
for f in ('Caveat.ttf',):
    src = f'/opt/qantcore/htmlvid/fonts/{f}'
    if os.path.exists(src):
        open(f'{WORK}/fonts/{f}', 'wb').write(open(src, 'rb').read())

DUR = 20.0
s = Sketch()

# --- 01. шапка ----------------------------------------------------------
s.text(78, 210, 'CONTEXT MODE', 0.5, size=104, color=INK, rot=-1.8)
s.swoosh(86, 236, 470, 1.1, color=ORANGE, width=10)
s.text(82, 292, 'MCP-сервер для агентов', 1.3, size=46, color=GREY, rot=-1.0)
s.sticky(780, 142, 246, 164, '30 706\n★', 1.6, color=BLUE, size=54, rot=-3.0)

# --- 02. агент → MCP ----------------------------------------------------
s.text(96, 418, 'промпт', 2.0, size=34, color=GREY, rot=-1.4)
s.rect(84, 430, 292, 132, 2.2, color=INK, fill='#F1F5F7')
s.text(230, 500, 'АГЕНТ', 2.6, size=54, color=INK, anchor='middle', rot=-1.5)
s.arrow(392, 496, 556, 496, 3.4, color=BLUE, bend=18)

s.rect(572, 418, 400, 156, 3.8, color=BLUE, fill=YELLOW, fill_style='hachure')
s.text(772, 486, 'MCP', 4.3, size=62, color=INK, anchor='middle', rot=-1.2)
s.text(772, 536, 'сервер', 4.5, size=34, color=INK, anchor='middle', rot=-1.0)

# --- 03. песочница и база ----------------------------------------------
s.arrow(772, 592, 772, 700, 4.8, color=BLUE)
s.rect(556, 712, 428, 148, 5.2, color=TEAL, fill='#E9F7F3', fill_style='solid')
s.text(770, 782, 'ПЕСОЧНИЦА', 5.7, size=50, color=INK, anchor='middle', rot=-1.4)
s.text(770, 826, 'скрипт вместо промпта', 5.9, size=32, color=GREY, anchor='middle', rot=-1.0)

s.arrow(548, 786, 356, 786, 6.4, color=ORANGE, bend=-14)
s.rect(84, 712, 264, 148, 6.8, color=INK, fill='#F1F5F7')
s.text(216, 780, 'БАЗА', 7.3, size=48, color=INK, anchor='middle', rot=-1.4)
s.text(216, 820, 'событий', 7.5, size=32, color=GREY, anchor='middle', rot=-1.0)
s.text(556, 706, 'скрипт', 5.0, size=34, color=TEAL, rot=-1.2)

s.text(84, 906, 'сырой вывод остаётся', 7.9, size=44, color=ORANGE, rot=-1.6)
s.text(84, 950, 'вне контекста', 8.1, size=42, color=ORANGE, rot=-1.6)
s.swoosh(88, 962, 300, 8.4, color=ORANGE, width=8)

# --- 04. экономия -------------------------------------------------------
s.text(80, 1096, '94–100 %', 8.95, size=132, color=ORANGE, rot=-2.0)
s.spark(286, 1004, 9.35, color=AMBER, r=24)
s.text(86, 1152, 'экономии контекста', 9.7, size=46, color=INK, rot=-1.4)
s.swoosh(90, 1168, 300, 10.0, color=TEAL, width=8)

s.bubble(412, 1186, 470, 150, 'контекст не пухнет', 12.6, size=50, rot=-1.0)
s.doodle('person', 986, 1180, 12.8, s=1.25, color=INK)

s.text(84, 1418, '11 инструментов · 17 платформ', 13.6, size=42, color=GREY, rot=-1.2)
s.text(84, 1478, 'ставится одной командой', 14.0, size=42, color=INK, rot=-1.2)
s.doodle('gear', 300, 1620, 14.4, s=1.1, color=TEAL)
s.doodle('chart', 800, 1650, 14.8, s=1.0, color=BLUE)

caps = [[0.4, 3.5, 'MCP-сервер для агентов'],
        [3.6, 8.6, 'Скрипт в песочнице вместо промпта'],
        [8.9, 12.4, 'Экономия 94–100 %'],
        [12.6, 16.6, '17 платформ, одна команда']]
html = s.html(DUR, f'{WORK}/scene.html', subtitle='обзоры и гайды по AI-агентам', caps=caps)
print(html, DUR)
