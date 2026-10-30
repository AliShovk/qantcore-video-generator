"""Визуальные объекты сцены: график, текст, стрелка, подсветка."""
import math

from PIL import ImageDraw, ImageFont

from .animations import ease_in_out

FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def font(path, size):
    return ImageFont.truetype(path, size)


class SceneObject:
    """Базовый объект: появляется в start, живёт dur секунд."""
    def __init__(self, start=0.0, dur=3.0, fade=0.35):
        self.start, self.dur, self.fade = start, dur, fade

    def alpha(self, t):
        if t < self.start or t > self.start + self.dur:
            return 0.0
        k = min(1.0, (t - self.start) / self.fade) * min(1.0, (self.start + self.dur - t) / self.fade)
        return max(0.0, min(1.0, k))

    def draw(self, img, t):
        raise NotImplementedError


class Chart(SceneObject):
    """Столбчатый график: столбцы растут, можно подсветить один."""
    def __init__(self, x, y, w, h, values, labels=None, color=(76, 201, 255),
                 title='', start=0.0, dur=4.0, grow=1.0, baseline=0.0, suffix=''):
        super().__init__(start, dur)
        self.baseline, self.suffix = float(baseline), suffix
        self.x, self.y, self.w, self.h = x, y, w, h
        self.values, self.labels = list(values), labels or []
        self.color, self.title, self.grow = color, title, grow
        self.highlight_idx, self.highlight_from = None, 0.0

    def highlight(self, idx, t_from):
        self.highlight_idx, self.highlight_from = idx, t_from

    def draw(self, img, t):
        a = self.alpha(t)
        if a <= 0:
            return
        d = ImageDraw.Draw(img, 'RGBA')
        k = ease_in_out(min(1.0, (t - self.start) / max(0.6, self.grow)))
        mx = max(self.values) or 1
        base = min(self.baseline, min(self.values) - 0.001)
        span = max(mx - base, 0.001)
        n = len(self.values)
        gap = 26
        bw = (self.w - gap * (n - 1)) / n
        if self.title:
            d.text((self.x, self.y - 54), self.title, font=font(FONT_B, 30),
                   fill=(200, 215, 235, int(230 * a)))
        d.line([(self.x, self.y + self.h), (self.x + self.w, self.y + self.h)],
               fill=(90, 105, 130, int(200 * a)), width=3)
        for i, v in enumerate(self.values):
            bh = ((v - base) / span) * self.h * k
            bx = self.x + i * (bw + gap)
            bar_color = self.color if not (self.highlight_idx == i and t >= self.highlight_from) else (255, 200, 97)
            alpha = int(235 * a)
            d.rounded_rectangle([bx, self.y + self.h - bh, bx + bw, self.y + self.h],
                                radius=10, fill=bar_color + (alpha,))
            label = self.labels[i] if i < len(self.labels) else str(v)
            d.text((bx + bw / 2 - 12 * len(str(label)) / 2, self.y + self.h + 12), str(label),
                   font=font(FONT_R, 24), fill=(190, 205, 225, int(220 * a)))
            if self.highlight_idx == i and t >= self.highlight_from:
                pulse = 0.5 + 0.5 * math.sin((t - self.highlight_from) * 6)
                d.rectangle([bx - 8, self.y + self.h - bh - 8, bx + bw + 8, self.y + self.h + 8],
                            outline=(255, 214, 120, int(180 + 60 * pulse)), width=4)
            else:
                label_v = f'{v:g}{self.suffix}'
                fv = font(FONT_B, 26)
                tw_v = d.textlength(label_v, font=fv)
                vy = self.y + self.h - bh - 40
                if vy < self.y + 10:          # столбец высокий — подпись внутрь
                    vy = self.y + self.h - bh + 14
                d.text((bx + bw / 2 - tw_v / 2, vy), label_v, font=fv,
                       fill=(255, 255, 255, alpha))


class Text(SceneObject):
    """Текстовая плашка: заголовок, подпись, реплика."""
    def __init__(self, x, y, text, size=40, color=(255, 255, 255), bold=True,
                 start=0.0, dur=3.0, anchor='left'):
        super().__init__(start, dur)
        self.x, self.y, self.text, self.size = x, y, text, size
        self.color, self.bold, self.anchor = color, bold, anchor

    def draw(self, img, t):
        a = self.alpha(t)
        if a <= 0:
            return
        d = ImageDraw.Draw(img, 'RGBA')
        f = font(FONT_B if self.bold else FONT_R, self.size)
        d.text((self.x, self.y), self.text, font=f, fill=self.color + (int(255 * a),),
               anchor='mm' if self.anchor == 'center' else 'la')


class Arrow(SceneObject):
    """Стрелка, которая прорисовывается от начала к концу."""
    def __init__(self, p1, p2, color=(255, 200, 97), start=0.0, dur=1.2, width=6):
        super().__init__(start, dur, fade=0.2)
        self.p1, self.p2, self.color, self.width = p1, p2, color, width

    def draw(self, img, t):
        if t < self.start:
            return
        k = ease_in_out(min(1.0, (t - self.start) / self.dur))
        x1, y1 = self.p1
        x2 = x1 + (self.p2[0] - x1) * k
        y2 = y1 + (self.p2[1] - y1) * k
        d = ImageDraw.Draw(img, 'RGBA')
        d.line([(x1, y1), (x2, y2)], fill=self.color + (235,), width=self.width)
        ang = math.atan2(y2 - y1, x2 - x1)
        for s in (2.6, -2.6):
            d.line([(x2, y2), (x2 + 26 * math.cos(ang + s), y2 + 26 * math.sin(ang + s))],
                   fill=self.color + (235,), width=self.width)


class Highlight(SceneObject):
    """Пульсирующая рамка вокруг области."""
    def __init__(self, box, color=(255, 200, 97), start=0.0, dur=2.0):
        super().__init__(start, dur, fade=0.2)
        self.box, self.color = box, color

    def draw(self, img, t):
        a = self.alpha(t)
        if a <= 0:
            return
        pulse = 0.5 + 0.5 * math.sin((t - self.start) * 5)
        d = ImageDraw.Draw(img, 'RGBA')
        d.rounded_rectangle(self.box, radius=18, outline=self.color + (int(150 + 90 * pulse * a),),
                            width=5)


class Scheme(SceneObject):
    """Схема из блоков со стрелками: появляются по очереди.

    items: [{"title": "...", "sub": "..."}, ...]
    """
    def __init__(self, x, y, w, items, start=0.0, dur=5.0, color=(76, 201, 255),
                 block_h=120, gap=54, title=''):
        super().__init__(start, dur, fade=0.25)
        self.x, self.y, self.w = x, y, w
        self.items, self.color = items, color
        self.block_h, self.gap = block_h, gap
        self.title = title

    def draw(self, img, t):
        a = self.alpha(t)
        if a <= 0:
            return
        d = ImageDraw.Draw(img, 'RGBA')
        if self.title:
            d.text((self.x, self.y - 52), self.title, font=font(FONT_B, 30),
                   fill=(210, 224, 240, int(230 * a)))
        n = len(self.items)
        for i, it in enumerate(self.items):
            k = ease_in_out(min(1.0, max(0.0, (t - self.start - i * 0.18) / 0.45)))
            if k <= 0:
                continue
            y = self.y + i * (self.block_h + self.gap)
            x = self.x + int(30 * (1 - k))
            d.rounded_rectangle([x, y, x + self.w, y + self.block_h], radius=20,
                                fill=(24, 32, 48, int(235 * a * k)),
                                outline=self.color + (int(200 * a * k),), width=3)
            d.rounded_rectangle([x + 18, y + 22, x + 26, y + self.block_h - 22], radius=4,
                                fill=self.color + (int(220 * a * k),))
            d.text((x + 44, y + 18), it.get('title', ''), font=font(FONT_B, 34),
                   fill=(255, 255, 255, int(255 * a * k)))
            if it.get('sub'):
                d.text((x + 44, y + 64), it['sub'], font=font(FONT_R, 25),
                       fill=(190, 205, 225, int(230 * a * k)))
            if i < n - 1:
                ay = y + self.block_h
                ah = int(self.gap * ease_in_out(min(1.0, max(0.0, (t - self.start - i * 0.18 - 0.25) / 0.3))))
                if ah > 6:
                    d.line([(self.x + 40, ay + 4), (self.x + 40, ay + ah)], fill=self.color + (int(200 * a),), width=4)
                    d.polygon([(self.x + 30, ay + ah - 2), (self.x + 50, ay + ah - 2), (self.x + 40, ay + ah + 14)],
                              fill=self.color + (int(200 * a),))


class Number(SceneObject):
    """Крупная цифра с подписью: появляется и досчитывается."""
    def __init__(self, value, label, sub='', x=90, y=430, size=260, color=(76, 201, 255),
                 start=0.0, dur=4.0):
        super().__init__(start, dur, fade=0.25)
        self.value, self.label, self.sub = value, label, sub
        self.x, self.y, self.size, self.color = x, y, size, color

    def draw(self, img, t):
        a = self.alpha(t)
        if a <= 0:
            return
        k = ease_in_out(min(1.0, (t - self.start) / 0.8))
        d = ImageDraw.Draw(img, 'RGBA')
        shown = int(round(self.value * k))
        f = font(FONT_B, self.size)
        d.text((self.x, self.y), str(shown), font=f, fill=(255, 255, 255, int(255 * a)))
        d.text((self.x, self.y + self.size * 1.14), self.label, font=font(FONT_B, 44),
               fill=self.color + (int(240 * a),))
        if self.sub:
            d.text((self.x, self.y + self.size * 1.14 + 62), self.sub, font=font(FONT_R, 30),
                   fill=(190, 205, 225, int(220 * a)))


class Panel(SceneObject):
    """Полупрозрачная плашка: затемняет кадр под финальный титр."""
    def __init__(self, x0, y0, x1, y1, color=(6, 8, 14), alpha=210, start=0.0, dur=1.0):
        super().__init__(start, dur, fade=0.25)
        self.box, self.color, self.alpha_v = (x0, y0, x1, y1), color, alpha

    def draw(self, img, t):
        a = self.alpha(t)
        if a <= 0:
            return
        d = ImageDraw.Draw(img, 'RGBA')
        d.rectangle(self.box, fill=self.color + (int(self.alpha_v * a),))
