#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Маскот Qantcore: птица с монетой в клюве. Единый формат для всех видео.

Использование:
    from mascot import Mascot
    m = Mascot(width=420)
    m.overlay(frame_rgba, t=3.4)                 # идёт сам, пинг-понг по кадру
    m.overlay(frame_rgba, t=3.4, x=540, face=1)  # фиксированная позиция
    m.overlay(frame_rgba, t=3.4, walking=False)  # стоит, ноги прямые

Параметры (закреплены заказчиком 2026-10-30):
- спрайт /opt/qantcore/htmlvid/crow-assets/bird.png (вырезан из референса, ноги удалены)
- ширина 420 px, ноги: бедро 52, голень 86, толщина 18/13, три пальца с когтем
- крепление ног: 0.735 высоты тела, разнесены ±16 px
- монета 168 px, центр на кончике клюва (0.985W, 0.091H) + 40 px вглубь
- ходьба: скорость 110 px/с, пауза на развороте 0.7 с, покачивание 6 px
"""
import math
import os

from PIL import Image, ImageDraw

SPRITE = '/opt/qantcore/htmlvid/crow-assets/bird.png'
INK = (16, 18, 26, 255)
GOLD, GOLD_EDGE, GOLD_HL = (246, 196, 64, 255), (140, 92, 10, 255), (255, 246, 200, 240)
GOLD_EDGE_SOFT = (140, 92, 10, 200)


class Mascot:
    def __init__(self, width=360, margin=50, speed=110.0, ground=112, coin_size=144,
                 sprite=SPRITE, canvas_w=1080, canvas_h=1920):
        self.w = width
        self.sprite = Image.open(sprite).convert('RGBA')
        self.h = int(self.sprite.height * width / self.sprite.width)
        self.sprite = self.sprite.resize((self.w, self.h), Image.LANCZOS)
        self.margin, self.speed, self.ground = margin, speed, ground
        self.coin = coin_size
        self.cw, self.ch = canvas_w, canvas_h
        self.x0 = margin + int(coin_size * 0.55)
        self.x1 = canvas_w - self.w - margin - int(self.coin * 0.55)

    # ── движение ─────────────────────────────────────────────────────────
    def position(self, t):
        span = max(1.0, self.x1 - self.x0)
        period = 2 * span / self.speed + 1.4
        k = t % period
        if k < span / self.speed:
            return self.x0 + self.speed * k, 1, True
        k -= span / self.speed
        if k < 0.7:
            return self.x1, 1, False
        k -= 0.7
        if k < span / self.speed:
            return self.x1 - self.speed * k, -1, True
        return self.x0, -1, False

    # ── рисование ────────────────────────────────────────────────────────
    def _leg(self, d, hx, hy, swing, bend, face, thigh=52, shin=86):
        a1 = math.radians(swing)
        kx = hx + math.sin(a1) * thigh * face
        ky = hy + math.cos(a1) * thigh
        a2 = math.radians(swing - bend)
        fx = kx + math.sin(a2) * shin * face
        fy = ky + math.cos(a2) * shin
        d.line([(hx, hy), (kx, ky)], fill=INK, width=18)
        d.line([(kx, ky), (fx, fy)], fill=INK, width=13)
        d.ellipse([kx - 9, ky - 9, kx + 9, ky + 9], fill=INK)
        for toe in (-46, 0, 42):
            ta = math.radians(toe)
            tx = fx + math.sin(ta) * 34 * face
            ty = fy + math.cos(ta) * 12
            d.line([(fx, fy), (tx, ty)], fill=INK, width=11)
            d.line([(tx, ty), (tx - 6 * face, ty + 9)], fill=INK, width=7)
        d.line([(fx, fy), (fx - 20 * face, fy + 5)], fill=INK, width=9)

    def _coin(self):
        c = Image.new('RGBA', (self.coin, self.coin), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        k = self.coin / 168.0
        d.ellipse([8 * k, 20 * k, 160 * k, 152 * k], fill=GOLD, outline=GOLD_EDGE, width=int(9 * k))
        d.ellipse([40 * k, 46 * k, 128 * k, 116 * k], outline=GOLD_EDGE_SOFT, width=int(6 * k))
        d.arc([36 * k, 34 * k, 110 * k, 88 * k], 200, 320, fill=GOLD_HL, width=int(9 * k))
        return c

    def _halo(self, size, w, h):
        halo = Image.new('RGBA', size, (0, 0, 0, 0))
        d = ImageDraw.Draw(halo)
        cx, cy = w / 2, h
        d.ellipse([cx - w * 0.62, cy - h * 0.30, cx + w * 0.62, cy + h * 0.10],
                  fill=(255, 255, 255, 16))
        return halo

    def overlay(self, frame, t, x=None, face=None, walking=None):
        """Кладёт птицу на кадр (RGBA) и возвращает кадр."""
        wx, wf, ww = self.position(t)
        x = wx if x is None else x
        face = wf if face is None else face
        walking = ww if walking is None else walking

        layer = Image.new('RGBA', frame.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        ph = t * 7.4 if walking else 0
        bob = abs(math.sin(ph)) * 6 if walking else 0
        top = self.ch - self.ground - self.h - bob
        hipx = x + (self.w * 0.55 if face == 1 else self.w * 0.45)
        hipy = top + self.h * 0.735
        for dx, swing in ((-16, math.sin(ph) * 30), (14, -math.sin(ph) * 30)):
            self._leg(d, hipx + dx, hipy, swing if walking else 0, 20 if walking else 8, face)

        if self.coin:
            tip_x = x + (self.w * 0.985 if face == 1 else self.w * 0.015)
            tip_y = top + self.h * 0.091
            cx = tip_x + (40 if face == 1 else -40)
            frame.alpha_composite(self._coin(), (int(cx - self.coin / 2), int(tip_y - self.coin / 2)))

        frame.alpha_composite(self._halo((self.w * 2, self.h * 2), self.w * 2, self.h * 2),
                              (int(x - self.w / 2), int(top + self.h - self.h)))
        sp = self.sprite if face == 1 else self.sprite.transpose(Image.FLIP_LEFT_RIGHT)
        frame.alpha_composite(sp, (int(x), int(top)))
        frame.alpha_composite(layer, (0, 0))
        return frame
