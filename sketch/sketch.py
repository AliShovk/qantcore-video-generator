#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sketch-движок: рукописные схемы (rough.js в headless Chrome) → PNG/MP4.

Сцена описывается списком примитивов; каждый появляется в момент t0 и
«прорисовывается» за dur секунд (штрих идёт по контуру, как маркером).
"""
import json
import os
import sys

sys.path.insert(0, '/opt/qantcore/htmlvid')

W, H = 1080, 1920
INK = '#12161C'
BLUE = '#2563EB'
ORANGE = '#EA580C'
AMBER = '#B45309'
TEAL = '#0E9F8A'
GREY = '#8A94A0'
YELLOW = '#F5C542'


class Sketch:
    """Сцена: набор примитивов с таймингами."""

    def __init__(self, w=W, h=H, bg='#FFFFFF'):
        self.w, self.h, self.bg = w, h, bg
        self.items = []
        self._seed = 7

    # --- служебное -------------------------------------------------------
    def _opts(self, color=INK, fill=None, fill_style='hachure', width=3.0,
              roughness=1.6, bowing=1.1, gap=9, weight=1.5):
        return dict(stroke=color, strokeWidth=width, fill=fill,
                    fillStyle=fill_style, hachureGap=gap, fillWeight=weight,
                    roughness=roughness, bowing=bowing)

    def _add(self, d):
        self._seed += 1
        d['seed'] = self._seed
        d.setdefault('dur', 0.55)
        self.items.append(d)
        return d

    # --- фигуры ----------------------------------------------------------
    def rect(self, x, y, w, h, t0, color=INK, fill=None, width=3.0,
             roughness=1.6, seed=None, dur=0.55, fill_style='hachure'):
        d = self._add(dict(kind='rect', x=x, y=y, w=w, h=h, t0=t0, dur=dur,
                           opts=self._opts(color, fill, fill_style, width, roughness)))
        if seed is not None:
            d['seed'] = seed
        return d

    def ellipse(self, cx, cy, w, h, t0, color=INK, fill=None, width=3.0, dur=0.5):
        return self._add(dict(kind='ellipse', cx=cx, cy=cy, w=w, h=h, t0=t0, dur=dur,
                              opts=self._opts(color, fill, width=width)))

    def line(self, x1, y1, x2, y2, t0, color=INK, width=3.0, dur=0.4, dash=False):
        return self._add(dict(kind='line', x1=x1, y1=y1, x2=x2, y2=y2, t0=t0, dur=dur,
                              dash=dash, opts=self._opts(color, width=width)))

    def arrow(self, x1, y1, x2, y2, t0, color=BLUE, width=3.6, dur=0.45, bend=0.0):
        """Стрелка; bend сдвигает середину, чтобы линия шла дугой."""
        return self._add(dict(kind='arrow', x1=x1, y1=y1, x2=x2, y2=y2, t0=t0, dur=dur,
                              bend=bend, opts=self._opts(color, width=width, roughness=1.9)))

    def text(self, x, y, s, t0, size=44, color=INK, rot=-1.2, anchor='start',
             weight=600, dur=0.3, max_w=None):
        return self._add(dict(kind='text', x=x, y=y, s=s, t0=t0, size=size, color=color,
                              rot=rot, anchor=anchor, weight=weight, dur=dur, max_w=max_w))

    def sticky(self, x, y, w, h, s, t0, color=BLUE, size=38, rot=-2.0):
        """Стикер с загнутым уголком."""
        return self._add(dict(kind='sticky', x=x, y=y, w=w, h=h, s=s, t0=t0, size=size,
                              color=color, rot=rot, dur=0.7,
                              opts=self._opts(color, fill='#FFFBEA', fill_style='solid')))

    def swoosh(self, x, y, w, t0, color=ORANGE, width=9, dur=0.45):
        """Маркерное подчёркивание."""
        return self._add(dict(kind='swoosh', x=x, y=y, w=w, t0=t0, dur=dur,
                              opts=self._opts(color, width=width, roughness=2.2)))

    def spark(self, x, y, t0, color=ORANGE, r=26, dur=0.4):
        """Лучики-акценты вокруг цифры."""
        return self._add(dict(kind='spark', x=x, y=y, r=r, t0=t0, dur=dur,
                              opts=self._opts(color, width=3.2, roughness=2.0)))

    def doodle(self, kind, x, y, t0, s=1.0, color=INK, dur=0.9):
        return self._add(dict(kind='doodle', shape=kind, x=x, y=y, s=s, t0=t0, dur=dur,
                              opts=self._opts(color, width=3.4)))

    def bubble(self, x, y, w, h, s, t0, color=INK, size=34, rot=-1.4):
        return self._add(dict(kind='bubble', x=x, y=y, w=w, h=h, s=s, t0=t0, size=size,
                              rot=rot, color=color, dur=0.7,
                              opts=self._opts(color, width=3.0)))

    # --- экспорт ---------------------------------------------------------
    def scene(self, duration):
        return dict(w=self.w, h=self.h, bg=self.bg, duration=duration, items=self.items)

    def html(self, duration, path, subtitle='', caps=None, finale='qantcore.space'):
        tpl = open(os.path.join(os.path.dirname(__file__), 'template.html'), encoding='utf-8').read()
        scene = self.scene(duration)
        html = (tpl.replace('/*SCENE*/', json.dumps({'scene': scene, 'caps': caps or [],
                                                     'finale': finale}, ensure_ascii=False))
                   .replace('/*SUBTITLE*/', subtitle))
        open(path, 'w', encoding='utf-8').write(html)
        return path
