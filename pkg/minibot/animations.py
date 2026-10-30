"""Действия мини-бота. Каждое — функция времени, возвращающая позу."""
import math

from .character import Pose


SPEED = {'walk': 170, 'run': 330}


def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _wave(x, amp=1.0, speed=1.0, phase=0.0):
    return math.sin((x * speed + phase) * 2 * math.pi) * amp


def idle(t, dur):
    """Дыхание, лёгкое покачивание головы, колебание антенны, редкое мигание."""
    k = t / max(dur, 0.001)
    blink = 0.0 if (t % 3.1) < 0.10 else 1.0
    return Pose(
        bounce=-3 * (0.5 - 0.5 * math.cos(t * 2 * math.pi / 2.6)),
        tilt=2.2 * math.sin(t * 1.7),
        antenna=7 * math.sin(t * 2.3),
        sh_l=8 + 3 * math.sin(t * 1.9),
        sh_r=8 + 3 * math.sin(t * 1.9 + 0.7),
        eye=blink,
    )


def blink(t, dur):
    p = idle(t, dur)
    p.eye = 0.0 if 0.06 < t < 0.16 else 1.0
    return p


def walk(t, dur):
    """Поочерёдные шаги, руки в противофазе, корпус покачивается, бот идёт вперёд."""
    ph = t * 2 * math.pi / 0.9
    swing = 26 * math.sin(ph)
    p = Pose(
        x=t * SPEED['walk'],
        bounce=-6 * abs(math.sin(ph)),
        tilt=1.6 * math.sin(ph),
        antenna=-6 * math.sin(ph),
        hip_l=swing, knee_l=max(0, -swing) * 0.55,
        hip_r=-swing, knee_r=max(0, swing) * 0.55,
        sh_l=-swing * 0.8, sh_r=swing * 0.8,
        eye=1.0,
    )
    return p


def run(t, dur):
    ph = t * 2 * math.pi / 0.55
    swing = 40 * math.sin(ph)
    p = walk(t, dur)
    p.x = t * SPEED['run']
    p.hip_l, p.hip_r = swing, -swing
    p.knee_l = max(0, -swing) * 0.9
    p.knee_r = max(0, swing) * 0.9
    p.sh_l, p.sh_r = -swing * 1.0, swing * 1.0
    p.bounce = -12 * abs(math.sin(ph))
    p.tilt = 6
    return p


def jump(t, dur):
    """Парабола вверх, поджатые ноги, руки вверх, короткая задержка в верхней точке."""
    k = t / max(dur, 0.001)
    up = math.sin(min(1.0, k * 1.15) * math.pi) ** 0.9
    y = -150 * up
    tuck = 34 * up
    p = Pose(
        y=y,
        bounce=-4 * up,
        hip_l=-tuck, knee_l=tuck * 0.8,
        hip_r=-tuck, knee_r=tuck * 0.8,
        sh_l=-120 * up, el_l=-10,
        sh_r=-120 * up, el_r=-10,
        antenna=-8 * up,
        eye=1.0,
    )
    return p


def wave(t, dur):
    """Правая рука вверх, предплечье качает, голова наклоняется."""
    k = ease_in_out(min(1.0, t / 0.25)) * ease_in_out(min(1.0, (dur - t) / 0.3))
    p = idle(t, dur)
    p.sh_r = -122 * k
    p.el_r = -14 * k + 3 * math.sin(t * 2 * math.pi / 0.7) * k
    p.arm_ext = 1.0 + 0.45 * k
    p.tilt = 4 * k
    p.antenna = 6 * math.sin(t * 2 * math.pi / 0.8) * k
    return p


def point(direction, t, dur):
    """Рука вытянута в сторону, голова повёрнута к объекту."""
    k = ease_in_out(min(1.0, t / 0.3)) * ease_in_out(min(1.0, (dur - t) / 0.3))
    sign = 1 if direction == 'right' else -1
    p = idle(t, dur)
    p.face = sign
    p.sh_r = -95 * k
    p.el_r = -2 * k
    p.tilt = 5 * sign * k
    p.antenna = -8 * sign * k
    p.sh_l = 8 - 6 * k
    return p


def turn(direction, t, dur):
    """Поворот: корпус сжимается и разворачивается в другую сторону."""
    k = ease_in_out(min(1.0, t / (dur * 0.5)))
    p = idle(t, dur)
    p.face = 1 if direction == 'right' else -1
    p.scale = 1 - 0.10 * math.sin(k * math.pi)
    p.tilt = 6 * math.sin(k * math.pi)
    return p


def celebrate(t, dur):
    """Обе руки вверх, мелкие подпрыгивания."""
    h = abs(math.sin(t * 2 * math.pi / 0.55))
    p = Pose(
        y=-26 * h,
        sh_l=-150, el_l=-15 + 10 * h,
        sh_r=-150, el_r=-15 + 10 * h,
        hip_l=-8, hip_r=-8,
        tilt=-4, antenna=-10 * h,
 eye=1.0,
 mouth='smile',
 )
    return p


def sad(t, dur):
    """Голова вниз, руки опущены, корпус проседает."""
    k = ease_in_out(min(1.0, t / 0.4)) * ease_in_out(min(1.0, (dur - t) / 0.4))
    p = idle(t, dur)
    p.tilt = 14 * k
    p.mouth = 'sad'
    p.bounce = 8 * k
    p.sh_l = 20 * k
    p.sh_r = 20 * k
    p.eye = 1 - 0.45 * k
    p.antenna = 14 * k
    return p


def surprise(t, dur):
    """Резкий отскок назад, руки в стороны, глаза широко."""
    k = ease_in_out(min(1.0, t / 0.18)) * ease_in_out(min(1.0, (dur - t) / 0.4))
    p = idle(t, dur)
    p.y = -34 * k
    p.x = -26 * k
    p.sh_l = -70 * k
    p.sh_r = -70 * k
    p.el_l = -30 * k
    p.el_r = -30 * k
    p.eye = 1.0 + 0.35 * k
    p.mouth = 'surprise'
    p.tilt = -6 * k
    return p


def explain(t, dur):
    """Жест одной рукой и кивки головой — «объясняет»."""
    k = ease_in_out(min(1.0, t / 0.3)) * ease_in_out(min(1.0, (dur - t) / 0.3))
    p = idle(t, dur)
    p.sh_r = (-55 - 18 * math.sin(t * 2 * math.pi / 1.1)) * k
    p.el_r = (-35 + 22 * math.sin(t * 2 * math.pi / 1.1)) * k
    p.tilt = (3 * math.sin(t * 2 * math.pi / 0.9)) * k
    p.sh_l = 8 + 4 * k
    return p


def speak(t, dur):
    """Лёгкое покачивание в такт речи и мигание экрана."""
    p = idle(t, dur)
    p.tilt = 2.6 * math.sin(t * 2 * math.pi / 0.7)
    p.bounce = -2 * (0.5 - 0.5 * math.cos(t * 2 * math.pi / 0.5))
    p.eye = 1.0
    return p


def smile(t, dur):
    p = idle(t, dur)
    p.mouth = 'smile'
    return p


def sad_face(t, dur):
    p = idle(t, dur)
    p.mouth = 'sad'
    p.tilt = 8
    p.eye = 0.75
    return p


def surprised_face(t, dur):
    p = idle(t, dur)
    p.mouth = 'surprise'
    p.eye = 1.3
    p.antenna = 12
    return p


def neutral(t, dur):
    p = idle(t, dur)
    p.mouth = 'neutral'
    return p


def look(t, dur):
    """Оглядывается: наклон головы и лёгкий поворот корпуса."""
    p = idle(t, dur)
    p.tilt = 9 * math.sin(t * 2 * math.pi / 1.6)
    p.antenna = 8 * math.sin(t * 2 * math.pi / 1.3)
    p.sh_l = 10 + 3 * math.sin(t * 2 * math.pi / 1.6)
    return p


def think(t, dur):
    """Задумался: рука у головы, наклон."""
    k = ease_in_out(min(1.0, t / 0.35)) * ease_in_out(min(1.0, (dur - t) / 0.35))
    p = idle(t, dur)
    p.sh_r = -70 * k
    p.el_r = -95 * k
    p.tilt = 7 * k
    p.antenna = -10 * k
    return p


def shrug(t, dur):
    """Пожимает плечами."""
    k = ease_in_out(min(1.0, t / 0.3)) * ease_in_out(min(1.0, (dur - t) / 0.3))
    p = idle(t, dur)
    p.sh_l = -32 * k
    p.sh_r = -32 * k
    p.el_l = -16 * k
    p.el_r = -16 * k
    p.tilt = 5 * k
    p.bounce = -4 * k
    return p


def stretch(t, dur):
    """Потягивается: руки вверх, корпус вытягивается."""
    k = math.sin(min(1.0, t / max(dur, 0.001)) * math.pi)
    p = idle(t, dur)
    p.sh_l = -150 * k
    p.sh_r = -150 * k
    p.el_l = -6
    p.el_r = -6
    p.y = -14 * k
    p.tilt = -3 * k
    return p


def dance(t, dur):
    """Танцует: покачивание и поочерёдные руки."""
    ph = t * 2 * math.pi / 0.8
    p = idle(t, dur)
    p.bounce = -10 * abs(math.sin(ph))
    p.tilt = 6 * math.sin(ph)
    p.hip_l = 10 * math.sin(ph)
    p.hip_r = -10 * math.sin(ph)
    p.sh_l = -45 + 35 * math.sin(ph)
    p.sh_r = -45 - 35 * math.sin(ph)
    p.el_l = -25
    p.el_r = -25
    p.antenna = 12 * math.sin(ph + 1)
    return p


ACTIONS = {
    'idle': idle, 'blink': blink, 'walk': walk, 'run': run, 'jump': jump,
    'wave': wave, 'celebrate': celebrate, 'sad': sad, 'surprise': surprise,
    'explain': explain, 'speak': speak,
    'look': look, 'think': think, 'shrug': shrug, 'stretch': stretch, 'dance': dance,
    'smile': smile, 'sad_face': sad_face,
    'surprised_face': surprised_face, 'neutral': neutral,
}


def action_pose(name, t, dur, direction=None):
    if name in ('point', 'point_left', 'point_right', 'point_up'):
        d = direction or ('left' if name == 'point_left' else 'right')
        if name == 'point' and direction == 'up':
            name = 'point_up'
        if name == 'point_up':
            p = point('right', t, dur)
            k = ease_in_out(min(1.0, t / 0.3)) * ease_in_out(min(1.0, (dur - t) / 0.3))
            p.sh_r = -122 * k          # рука вверх-наружу, не перед лицом
            p.el_r = -14 * k
            p.tilt = 4 * k
            p.arm_ext = 1.0 + 0.45 * k
            return p
        return point(d, t, dur)
    if name in ('turn', 'turn_left', 'turn_right'):
        d = direction or ('left' if name == 'turn_left' else 'right')
        return turn(d, t, dur)
    if name not in ACTIONS:
        raise ValueError(f'неизвестное действие: {name}')
    return ACTIONS[name](t, dur)
