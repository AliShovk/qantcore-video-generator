"""Питон-API мини-бота: bot.wave(1.5) → действие для сцены."""


class MiniBot:
    """Готовые действия. Каждый метод возвращает кортеж (действие, длительность, направление)."""

    def _a(self, name, duration=1.0, direction=None):
        if duration <= 0:
            raise ValueError('длительность должна быть больше нуля')
        return (name, float(duration), direction)

    def idle(self, duration=1.0):
        return self._a('idle', duration)

    def blink(self, duration=0.25):
        return self._a('blink', duration)

    def walk(self, duration=1.0):
        return self._a('walk', duration)

    def run(self, duration=1.0):
        return self._a('run', duration)

    def jump(self, duration=1.0):
        return self._a('jump', duration)

    def wave(self, duration=1.0):
        return self._a('wave', duration)

    def point(self, direction='right', duration=1.0):
        if direction not in ('left', 'right', 'up'):
            raise ValueError("direction: 'left', 'right' или 'up'")
        return self._a('point_up' if direction == 'up' else 'point', duration, direction)

    def turn(self, direction='right', duration=0.8):
        if direction not in ('left', 'right'):
            raise ValueError("direction: 'left' или 'right'")
        return self._a('turn', duration, direction)

    def look(self, duration=1.6):
        return self._a('look', duration)

    def think(self, duration=1.6):
        return self._a('think', duration)

    def shrug(self, duration=1.2):
        return self._a('shrug', duration)

    def stretch(self, duration=1.4):
        return self._a('stretch', duration)

    def dance(self, duration=2.0):
        return self._a('dance', duration)

    def smile(self, duration=1.2):
        return self._a('smile', duration)

    def sad_face(self, duration=1.2):
        return self._a('sad_face', duration)

    def surprised_face(self, duration=1.2):
        return self._a('surprised_face', duration)

    def neutral(self, duration=1.2):
        return self._a('neutral', duration)

    def speak(self, duration=1.0):
        return self._a('speak', duration)

    def explain(self, duration=2.0):
        return self._a('explain', duration)

    def celebrate(self, duration=1.5):
        return self._a('celebrate', duration)

    def sad(self, duration=1.5):
        return self._a('sad', duration)

    def surprise(self, duration=1.0):
        return self._a('surprise', duration)
