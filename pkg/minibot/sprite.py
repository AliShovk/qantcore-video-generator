"""Спрайтовая риг-анимация: части вырезаны из референса, вращаются в суставах."""
import math
import os

from PIL import Image

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
_cache = {}


def _cut(box):
    key = tuple(box)
    if key not in _cache:
        im = Image.open(os.path.join(ASSETS, 'bot_sprite.png')).convert('RGBA')
        _cache[key] = im.crop(box)
    return _cache[key]


PARTS = {
    'head': (0, 0, 384, 352),
    'body': (0, 340, 384, 600),
    'arm_l': (0, 330, 92, 600),
    'arm_r': (292, 330, 384, 600),
    'leg_l': (70, 540, 196, 708),
    'leg_r': (188, 540, 314, 708),
}

PIVOT = {'arm_l': (86, 60), 'arm_r': (6, 60), 'leg_l': (60, 30), 'leg_r': (58, 30), 'head': (192, 330)}


def _paste_rot(canvas, part, x, y, angle, pivot):
    img = _cut(PARTS[part])
    if abs(angle) > 0.2:
        img = img.rotate(angle, resample=Image.BICUBIC, center=pivot)
    canvas.alpha_composite(img, (int(x), int(y)))


def draw_sprite_bot(canvas, pose, cx, cy, scale=1.0):
    """Холст — RGBA. Рисует бота по частям вокруг точки (cx, cy) — центр корпуса."""
    s = scale * pose.scale
    face = pose.face

    def place(part, dx, dy, angle, pivot):
        img = _cut(PARTS[part])
        if abs(angle) > 0.2:
            img = img.rotate(angle, resample=Image.BICUBIC, center=pivot)
        if face < 0:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            w = img.width
            px = w - (dx + img.width)
        else:
            px = dx
        canvas.alpha_composite(img, (int(cx + px * s), int(cy + dy * s + pose.bounce * s + pose.y * s)))

    # ноги
    place('leg_l', -150, 40, pose.hip_l * 0.6, PIVOT['leg_l'])
    place('leg_r', 70, 40, pose.hip_r * 0.6, PIVOT['leg_r'])
    # задняя рука
    place('arm_l', -190, -120, pose.sh_l * 0.8, PIVOT['arm_l'])
    # корпус
    place('body', -192, -230, 0, (0, 0))
    # передняя рука
    place('arm_r', 100, -120, pose.sh_r * 0.8, PIVOT['arm_r'])
    # голова
    place('head', -192, -430, -pose.tilt * 0.5, PIVOT['head'])
    return canvas


def draw_whole(canvas, pose, cx, cy, scale=1.0):
    """Цельный спрайт из референса: точное лицо и силуэт, движение — позой и наклоном."""
    im = Image.open(os.path.join(ASSETS, 'bot_sprite.png')).convert('RGBA')
    # спрайт уже очищен: только бот, без соседей и полос
    s = scale * pose.scale
    w = int(im.width * s)
    h = int(im.height * s)
    im = im.resize((w, h), Image.LANCZOS)
    if pose.face < 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    ang = -pose.tilt * 0.45
    if abs(ang) > 0.3:
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    x = int(cx - im.width / 2 + pose.x * s)
    y = int(cy - im.height * 0.72 + pose.bounce * s + pose.y * s)
    canvas.alpha_composite(im, (x, y))
    return canvas
