"""Мини-бот: векторная отрисовка по референсу, все части раздельные.

Пропорции сняты с исходного рисунка: голова 317×219, корпус 170×180,
руки 42 в толщину, ноги 46, ботинки 74×38.
"""
import math
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFilter

INK = (26, 32, 44)
SCREEN = (24, 34, 46)

PALETTES = {
    'classic':    {'body': (255, 255, 255), 'accent': (52, 184, 240), 'dark': (30, 42, 58), 'glow': (120, 224, 255)},
    'dark':       {'body': (46, 53, 68),    'accent': (78, 206, 255), 'dark': (20, 26, 36), 'glow': (150, 232, 255)},
    'bright':     {'body': (255, 255, 255), 'accent': (255, 150, 66),  'dark': (40, 42, 52), 'glow': (255, 205, 150)},
    'futuristic': {'body': (255, 255, 255), 'accent': (168, 136, 255), 'dark': (40, 38, 56), 'glow': (208, 190, 255)},
    'eco':        {'body': (255, 255, 255), 'accent': (58, 200, 132),  'dark': (30, 46, 40), 'glow': (160, 240, 200)},
}

HEAD_W, HEAD_H = 300, 200
SCREEN_INSET = 30
BODY_W, BODY_H = 196, 192
NECK_H = 20


def rot(dx, dy, deg):
    a = math.radians(deg)
    return (dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a))


@dataclass
class Pose:
    x: float = 0.0
    y: float = 0.0
    bounce: float = 0.0
    tilt: float = 0.0
    face: int = 1
    sh_l: float = 8.0
    el_l: float = 4.0
    sh_r: float = 8.0
    el_r: float = 4.0
    hip_l: float = 0.0
    knee_l: float = 0.0
    hip_r: float = 0.0
    knee_r: float = 0.0
    eye: float = 1.0
    antenna: float = 0.0
    scale: float = 1.0
    mouth: str = 'none'
    arm_ext: float = 1.0

    def blend(self, other, k):
        out = {}
        for name, val in self.__dict__.items():
            ov = getattr(other, name)
            out[name] = val + (ov - val) * k if isinstance(val, (int, float)) else (ov if k > 0.5 else val)
        p = Pose()
        for name, val in out.items():
            setattr(p, name, val)
        return p


def _seg(d, p1, p2, w, fill, outline, ow):
    d.line([p1, p2], fill=outline, width=int(w + ow * 2))
    for q in (p1, p2):
        d.ellipse([q[0] - w / 2 - ow, q[1] - w / 2 - ow,
                   q[0] + w / 2 + ow, q[1] + w / 2 + ow], fill=outline)
    d.line([p1, p2], fill=fill, width=int(w))
    for q in (p1, p2):
        d.ellipse([q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2], fill=fill)


def _limb(d, root, a1, a2, l1, l2, w, fill, glove, boot=False, ow=6, edge=None):
    edge = edge or INK
    e = (root[0] + rot(0, l1, a1)[0], root[1] + rot(0, l1, a1)[1])
    wpt = (e[0] + rot(0, l2, a1 + a2)[0], e[1] + rot(0, l2, a1 + a2)[1])
    _seg(d, root, e, w, fill, edge, ow)
    _seg(d, e, wpt, w, fill, edge, ow)
    d.ellipse([e[0] - w / 2 + ow * 0.4, e[1] - w / 2 + ow * 0.4,
               e[0] + w / 2 - ow * 0.4, e[1] + w / 2 - ow * 0.4], fill=fill)
    if boot:
        bw, bh = w * 1.55, w * 0.72
        d.rounded_rectangle([wpt[0] - bw / 2, wpt[1] - bh / 2 + w * 0.25,
                             wpt[0] + bw / 2, wpt[1] + bh / 2 + w * 0.3],
                            radius=bh / 2, fill=glove, outline=(228, 238, 250), width=max(2, ow // 2))
        d.ellipse([wpt[0] - bw * 0.42, wpt[1] + bh * 0.02, wpt[0] + bw * 0.06, wpt[1] + bh * 0.52],
                  fill=(245, 250, 255, 235))
    else:
        rw, rh = w * 0.58, w * 0.68
        d.rounded_rectangle([wpt[0] - rw - ow, wpt[1] - rh - ow, wpt[0] + rw + ow, wpt[1] + rh + ow],
                            radius=rh, fill=(228, 238, 250))
        d.rounded_rectangle([wpt[0] - rw, wpt[1] - rh, wpt[0] + rw, wpt[1] + rh],
                            radius=rh * 0.8, fill=glove)
        d.ellipse([wpt[0] - rw * 1.05, wpt[1] - rh * 0.35, wpt[0] - rw * 0.45, wpt[1] + rh * 0.25], fill=glove)


def _eyes(d, hx, hy, s, eye, glow):
    for side in (-1, 1):
        ex = hx + side * 58 * s
        if eye < 0.3:
            d.line([(ex - 24 * s, hy - 6 * s), (ex + 24 * s, hy - 6 * s)], fill=glow,
                   width=max(4, int(9 * s)))
        else:
            d.arc([ex - 32 * s, hy - 30 * s, ex + 32 * s, hy + 20 * s], start=205, end=335,
                  fill=glow, width=max(6, int(11 * s)))


def _mouth(d, cx, cy, kind, s, color, base=True):
    if base:  # постоянная улыбка как на референсе
        d.arc([cx - 44 * s, cy - 10 * s, cx + 44 * s, cy + 34 * s], start=18, end=162,
              fill=color, width=max(4, int(9 * s)))
    if kind == 'none':
        return
    w = 34 * s
    if kind == 'sad':
        d.arc([cx - w, cy + 6 * s, cx + w, cy + 40 * s], start=200, end=340, fill=color,
              width=max(4, int(8 * s)))
    elif kind == 'surprise':
        d.ellipse([cx - 10 * s, cy + 4 * s, cx + 10 * s, cy + 30 * s], outline=color,
                  width=max(3, int(5 * s)))
    elif kind == 'neutral':
        d.line([(cx - 18 * s, cy + 16 * s), (cx + 18 * s, cy + 16 * s)], fill=color,
               width=max(4, int(7 * s)))


def _gloss(img, box, alpha=90, blur=18):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=(255, 255, 255, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img, layer)


def draw_bot(img, pose: Pose, cx, cy, scale=1.0, palette='classic'):
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    d = ImageDraw.Draw(img, 'RGBA')
    pal = PALETTES.get(palette, PALETTES['classic'])
    body, accent, dark, glow = pal['body'], pal['accent'], pal['dark'], pal['glow']
    f = pose.face
    s = scale * pose.scale
    ow = max(4, int(7 * s))
    edge = INK if sum(body[:3]) / 3 > 120 else (230, 240, 252)

    def P(dx, dy):
        return (cx + dx * f * s, cy + dy * s + pose.bounce * s + pose.y * s)

    base_y = cy + pose.bounce * s + pose.y * s
    # мягкая тень на полу
    d.ellipse([cx - 110 * s, base_y + 176 * s, cx + 110 * s, base_y + 200 * s],
              fill=(10, 16, 26, 22))

    # ноги: длиннее, шире, ступни крупнее
    hip_y = BODY_H / 2 - 10
    _limb(d, P(-44, hip_y), pose.hip_l, pose.knee_l, 48, 42, 62, body, dark, boot=True, ow=ow, edge=edge)
    _limb(d, P(44, hip_y), pose.hip_r, pose.knee_r, 48, 42, 62, body, dark, boot=True, ow=ow, edge=edge)
    # задняя рука: от плеча ниже головы, длиннее
    _limb(d, P(-BODY_W / 2 + 2, -BODY_H / 2 + 52), pose.sh_l + 8, pose.el_l, 58 * pose.arm_ext, 50 * pose.arm_ext, 54, body, dark, ow=ow, edge=edge)

    # корпус
    d.rounded_rectangle([cx - BODY_W / 2 * s, cy - BODY_H / 2 * s,
                         cx + BODY_W / 2 * s, cy + BODY_H / 2 * s],
                        radius=70 * s, fill=body, outline=INK, width=ow)

    d.ellipse([cx - 64 * s, cy - BODY_H / 2 * s + 12 * s,
               cx + 14 * s, cy - BODY_H / 2 * s + 32 * s], fill=(255, 255, 255, 35))
    # шея
    neck_top = cy - BODY_H / 2 * s - NECK_H * s
    d.rounded_rectangle([cx - 38 * s, neck_top, cx + 38 * s, cy - BODY_H / 2 * s + 14 * s],
                        radius=10 * s, fill=body, outline=INK, width=ow)
    d.rounded_rectangle([cx - 40 * s, cy - BODY_H / 2 * s + 2 * s, cx + 40 * s, cy - BODY_H / 2 * s + 18 * s],
                        radius=8 * s, fill=dark, outline=INK, width=max(3, int(4 * s)))
    d.rectangle([cx - 34 * s + ow, neck_top + 6 * s, cx + 34 * s - ow, neck_top + 18 * s],
                fill=(210, 222, 236, 120))

    # грудной круг
    d.ellipse([cx - 44 * s, cy - 58 * s, cx + 44 * s, cy + 30 * s], fill=accent,
              outline=INK, width=max(3, int(5 * s)))
    d.ellipse([cx - 28 * s, cy - 46 * s, cx - 2 * s, cy - 20 * s], fill=(240, 252, 255))

    # уши (полускрыты головой)
    hx = cx
    hy = cy - BODY_H / 2 * s - NECK_H * s - HEAD_H / 2 * s + 20 * s + pose.tilt * 0.4 * s
    for side in (-1, 1):
        ex = hx + side * (HEAD_W / 2 - 12) * s
        d.rounded_rectangle([ex - 16 * s, hy - 40 * s, ex + 16 * s, hy + 40 * s],
                            radius=16 * s, fill=accent, outline=INK, width=ow)

    # голова
    d.rounded_rectangle([hx - HEAD_W / 2 * s, hy - HEAD_H / 2 * s,
                         hx + HEAD_W / 2 * s, hy + HEAD_H / 2 * s],
                        radius=92 * s, fill=body, outline=INK, width=max(5, int(9 * s)))
    # экран с лёгким градиентом
    sx0, sy0 = hx - (HEAD_W / 2 - SCREEN_INSET) * s, hy - (HEAD_H / 2 - SCREEN_INSET) * s
    sx1, sy1 = hx + (HEAD_W / 2 - SCREEN_INSET) * s, hy + (HEAD_H / 2 - SCREEN_INSET) * s
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=74 * s, fill=SCREEN)

    _eyes(d, hx, hy + 8 * s, s, pose.eye, glow)
    _mouth(d, hx, hy + 46 * s, pose.mouth, s, glow)

    # антенна
    ax, ay = hx, hy - HEAD_H / 2 * s
    tx = ax + math.sin(math.radians(pose.antenna)) * 44 * s
    ty = ay - math.cos(math.radians(pose.antenna)) * 44 * s
    d.line([(ax, ay), (tx, ty)], fill=INK, width=max(7, int(11 * s)))
    d.line([(ax, ay), (tx, ty)], fill=(226, 236, 248), width=max(3, int(5 * s)))
    if palette == 'eco':
        d.polygon([(tx, ty - 20 * s), (tx + 24 * s, ty - 2 * s), (tx, ty + 16 * s), (tx - 16 * s, ty - 2 * s)],
                  fill=accent, outline=INK)
    else:
        d.ellipse([tx - 24 * s, ty - 24 * s, tx + 24 * s, ty + 24 * s], fill=accent,
                  outline=INK, width=max(4, int(6 * s)))

    # блики: голова и корпус

    # передняя рука
    d = ImageDraw.Draw(img, 'RGBA')
    _limb(d, P(BODY_W / 2 - 2, -BODY_H / 2 + 52), pose.sh_r - 8, pose.el_r, 58 * pose.arm_ext, 50 * pose.arm_ext, 54, body, dark, ow=ow, edge=edge)
    return img
