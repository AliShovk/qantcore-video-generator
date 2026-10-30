"""Сцена: таймлайн действий, объекты, рендер в MP4/GIF."""
import json
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import animations as A
from .character import Pose, draw_bot
from .sprite import draw_whole
from .objects import FONT_B, FONT_R, font

W, H = 1920, 1080


class Scene:
    """Сцена с ботом и объектами.

    scene.add('wave', 1.5)        — последовательно
    scene.at(4.0, 'idle', 2.0)    — параллельно с уже добавленным
    """

    def __init__(self, width=W, height=H, fps=30, bot=(380, 700), scale=1.0,
                 palette='classic', bg='dark', sprite=True, progress=False):
        self.w, self.h, self.fps = width, height, fps
        self.bot_x, self.bot_y = bot
        self.scale = scale
        self.palette = palette
        self.bg = bg
        self.sprite = sprite
        self.progress = progress
        self._bg_cache = None
        self.cues = []
        self.objects = []
        self.captions = []
        self.t = 0.0

    # ── таймлайн ──────────────────────────────────────────────────────────
    def add(self, action, duration=None, direction=None, **kw):
        # допускаем bot.wave(1.5) → ('wave', 1.5, None)
        if isinstance(action, tuple):
            action, duration, direction = action[0], action[1], (action[2] if len(action) > 2 else None)
        if duration is None:
            raise ValueError('не указана длительность действия')
        self.cues.append({'start': self.t, 'dur': float(duration), 'action': action,
                          'direction': direction})
        self.t += float(duration)
        return self

    def at(self, start, action, duration=None, direction=None):
        if isinstance(action, tuple):
            action, duration, direction = action[0], action[1], (action[2] if len(action) > 2 else None)
        self.cues.append({'start': float(start), 'dur': float(duration), 'action': action,
                          'direction': direction})
        self.cues.sort(key=lambda c: c['start'])
        self.t = max(self.t, start + duration)
        return self

    def wait(self, duration):
        self.t += float(duration)
        return self

    def speed(self):
        """Общая длительность сцены в секундах."""
        return max([c['start'] + c['dur'] for c in self.cues] + [self.t, 0.1])

    def add_object(self, obj):
        self.objects.append(obj)
        return obj

    def pad_to(self, seconds):
        """Дотягивает сцену до нужной длины нейтральным idle."""
        if self.t < seconds:
            self.add('idle', seconds - self.t)
        return self

    def outro(self, text='qantcore.space', dur=3.6, sub='обзоры и гайды по AI-агентам',
              color=(76, 201, 255)):
        """Финальная плашка: крупный адрес сайта в конце ролика."""
        from .objects import Panel, Text
        end = self.speed()
        t0 = end
        self._outro_t0 = t0
        self.add_object(Panel(0, 0, self.w, self.h, alpha=252, start=t0, dur=dur))
        self.add_object(Text(self.w / 2, int(self.h * 0.44), text, size=104, color=color,
                             start=t0 + 0.15, dur=max(0.4, dur - 0.15), anchor='center'))
        self.add_object(Text(self.w / 2, int(self.h * 0.44) + 96, sub, size=36,
                             color=(200, 214, 232), bold=False, start=t0 + 0.35,
                             dur=max(0.4, dur - 0.35), anchor='center'))
        self.t = max(self.t, t0 + dur)
        return self

    def caption(self, text, start, end, size=40):
        """Реплика с точными границами — под озвучку."""
        self.captions.append({'text': text, 'start': float(start),
                              'dur': float(end) - float(start), 'size': size})
        return self

    def say(self, text, start=None, dur=None, size=38):
        start = 0.0 if start is None else start
        dur = 3.0 if dur is None else dur
        self.captions.append({'text': text, 'start': start, 'dur': dur, 'size': size})
        return self

    # ── поза в момент времени ─────────────────────────────────────────────
    def _offset_before(self, t):
        x = 0.0
        for c in self.cues:
            if c['start'] + c['dur'] <= t and c['action'] in ('walk', 'run'):
                x += (A.SPEED[c['action']] * c['dur'])
        return x

    def pose_at(self, t):
        active = None
        for c in self.cues:
            if c['start'] <= t <= c['start'] + c['dur']:
                active = c
        if active is None:
            done = [c for c in self.cues if c['start'] + c['dur'] < t]
            if not done:
                return Pose(), 0.0
            c = max(done, key=lambda z: z['start'] + z['dur'])
            p = A.action_pose(c['action'], c['dur'], c['dur'], c.get('direction'))
            p.x = self._offset_before(t + 0.001) + (p.x if c['action'] in ('walk', 'run') else 0)
            return p, 0.0

        c = active
        local = t - c['start']
        p = A.action_pose(c['action'], local, c['dur'], c.get('direction'))
        p.x = self._offset_before(t) + (p.x if c['action'] in ('walk', 'run') else 0)

        # плавный вход из предыдущего действия
        fade = 0.22
        if local < fade:
            prev = [z for z in self.cues if z['start'] + z['dur'] <= c['start']]
            if prev:
                pc = max(prev, key=lambda z: z['start'] + z['dur'])
                pp = A.action_pose(pc['action'], pc['dur'], pc['dur'], pc.get('direction'))
                pp.x = self._offset_before(c['start']) + (pp.x if pc['action'] in ('walk', 'run') else 0)
                p = pp.blend(p, A.ease_in_out(local / fade))
        return p, local

    # ── фон ───────────────────────────────────────────────────────────────
    def _background(self):
        """Пять фонов на выбор: dark, aurora, studio, sunset, blueprint, mono."""
        if self._bg_cache is not None:
            return self._bg_cache
        from .character import PALETTES
        accent = PALETTES.get(self.palette, PALETTES['classic'])['accent']
        style = self.bg
        w, h = self.w, self.h
        im = Image.new('RGB', (w, h), (11, 16, 32))
        d = ImageDraw.Draw(im)

        def vgrad(top, bottom):
            for y in range(h):
                k = y / h
                d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3)))

        def blobs(items, blur=180):
            layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            for box, col in items:
                ld.ellipse(box, fill=col + (96,))
            layer = layer.filter(ImageFilter.GaussianBlur(blur))
            return Image.alpha_composite(im.convert('RGBA'), layer).convert('RGB')

        if style == 'aurora':
            vgrad((8, 12, 30), (22, 26, 60))
            layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            for i in range(4):
                y0 = int(h * (0.05 + i * 0.16))
                ld.polygon([(0, y0), (w, y0 - 220), (w, y0 + 60), (0, y0 + 300)],
                           fill=(76, 201, 255, 78) if i % 2 == 0 else (183, 155, 255, 88))
            im = Image.alpha_composite(im.convert('RGBA'), layer.filter(ImageFilter.GaussianBlur(90))).convert('RGB')
        elif style == 'studio':
            vgrad((14, 18, 30), (26, 30, 48))
            im = blobs([([w * 0.1, -h * 0.35, w * 0.9, h * 0.55], accent)], 220)
            d.rectangle([0, h - 210, w, h], fill=(16, 20, 34))
        elif style == 'sunset':
            vgrad((44, 22, 60), (240, 138, 92))
            d.ellipse([w * 0.28, h * 0.42, w * 0.72, h * 0.72], fill=(255, 196, 120))
            d.rectangle([0, h * 0.7, w, h], fill=(38, 24, 44))
            d.polygon([(0, h * 0.7), (w * 0.28, h * 0.58), (w * 0.55, h * 0.7)], fill=(30, 18, 36))
            d.polygon([(w * 0.45, h * 0.7), (w * 0.75, h * 0.6), (w, h * 0.7)], fill=(26, 16, 32))
        elif style == 'blueprint':
            im = Image.new('RGB', (w, h), (13, 34, 60))
            d = ImageDraw.Draw(im)
            for x in range(0, w, 40):
                d.line([(x, 0), (x, h)], fill=(30, 62, 96))
            for y in range(0, h, 40):
                d.line([(0, y), (w, y)], fill=(30, 62, 96))
            for x in range(0, w, 200):
                d.line([(x, 0), (x, h)], fill=(45, 88, 130), width=2)
            for y in range(0, h, 200):
                d.line([(0, y), (w, y)], fill=(45, 88, 130), width=2)
        elif style in ('money', 'agents', 'chip', 'video', 'paper'):
            vgrad((10, 14, 26), (20, 24, 40))
            layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            if style == 'money':
                for i in range(9):
                    x = 80 + (i * 137) % (w - 160)
                    y = 260 + (i * 211) % (h - 700)
                    r = 42 + (i % 3) * 10
                    ld.ellipse([x - r, y - r, x + r, y + r], outline=(255, 190, 90, 95), width=5)
                    ld.ellipse([x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55],
                               outline=(255, 190, 90, 45), width=4)
                for i in range(6):
                    bx = 120 + i * 150
                    bh = 90 + (i % 3) * 70
                    ld.rectangle([bx, h - 260 - bh, bx + 70, h - 260], fill=(255, 190, 90, 42))
            elif style == 'agents':
                pts = [(140 + (i * 197) % (w - 280), 300 + (i * 271) % (h - 800)) for i in range(12)]
                for i, p1 in enumerate(pts):
                    for p2 in pts[i + 1:]:
                        if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) < 420:
                            ld.line([p1, p2], fill=(120, 200, 255, 55), width=3)
                for p1 in pts:
                    ld.ellipse([p1[0] - 18, p1[1] - 18, p1[0] + 18, p1[1] + 18], fill=(120, 200, 255, 110))
            elif style == 'chip':
                cx0, cy0 = w // 2, int(h * 0.75)
                cw, chh = 360, 300
                ld.rounded_rectangle([cx0 - cw // 2, cy0 - chh // 2, cx0 + cw // 2, cy0 + chh // 2],
                                     radius=28, outline=(90, 240, 200, 85), width=5)
                for i in range(7):
                    off = -140 + i * 46
                    ld.line([(cx0 + off, cy0 - chh // 2), (cx0 + off, cy0 - chh // 2 - 46)], fill=(90, 240, 200, 45), width=4)
                    ld.line([(cx0 + off, cy0 + chh // 2), (cx0 + off, cy0 + chh // 2 + 46)], fill=(90, 240, 200, 45), width=4)
                for i in range(5):
                    off = -100 + i * 52
                    ld.line([(cx0 - cw // 2, cy0 + off), (cx0 - cw // 2 - 46, cy0 + off)], fill=(90, 240, 200, 45), width=4)
                    ld.line([(cx0 + cw // 2, cy0 + off), (cx0 + cw // 2 + 46, cy0 + off)], fill=(90, 240, 200, 45), width=4)
            elif style == 'video':
                for i in range(5):
                    y = 200 + i * 300
                    ld.rounded_rectangle([60, y, 130, y + 220], radius=14, fill=(255, 140, 190, 26))
                    for k in range(4):
                        ld.rectangle([70, y + 14 + k * 52, 120, y + 34 + k * 52], fill=(10, 14, 26, 160))
                for i in range(5):
                    y = 200 + i * 300
                    ld.rounded_rectangle([w - 130, y, w - 60, y + 220], radius=14, fill=(255, 140, 190, 26))
                    for k in range(4):
                        ld.rectangle([w - 120, y + 14 + k * 52, w - 70, y + 34 + k * 52], fill=(10, 14, 26, 160))
                ld.polygon([(w // 2 - 60, 250), (w // 2 + 70, 320), (w // 2 - 60, 390)], fill=(255, 140, 190, 40))
            else:  # paper
                for x in range(0, w, 60):
                    ld.line([(x, 0), (x, h)], fill=(150, 180, 220, 34))
                for y in range(0, h, 60):
                    ld.line([(0, y), (w, y)], fill=(150, 180, 220, 34))
                ld.line([(150, 0), (150, h)], fill=(255, 120, 140, 40), width=4)
            im = Image.alpha_composite(im.convert('RGBA'), layer).convert('RGB')
            d = ImageDraw.Draw(im)
        elif style == 'mono':
            vgrad((12, 14, 22), (18, 20, 30))
            layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(layer).ellipse([w * 0.08, h * 0.15, w * 0.92, h * 1.0], fill=accent + (64,))
            im = Image.alpha_composite(im.convert('RGBA'), layer.filter(ImageFilter.GaussianBlur(200))).convert('RGB')
        else:  # dark
            vgrad((11, 16, 32), (24, 30, 54))
            im = blobs([([-400, -700, w * 0.75, 620], (56, 189, 248)),
                        ([w * 0.45, -600, w + 400, 700], (167, 139, 250))], 180)
            d = ImageDraw.Draw(im, 'RGBA')
            for x in range(0, w, 120):
                d.line([(x, 0), (x, h)], fill=(255, 255, 255, 8))
            for y in range(0, h, 120):
                d.line([(0, y), (w, y)], fill=(255, 255, 255, 8))

        d = ImageDraw.Draw(im, 'RGBA')
        if style != 'blueprint':
            d.line([(0, h - 170), (w, h - 170)], fill=(255, 255, 255, 26), width=2)
        self._bg_cache = im
        return im

    # ── кадр ──────────────────────────────────────────────────────────────
    def frame(self, t, bg=None):
        im = (bg.copy() if bg is not None else self._background())
        for obj in self.objects:
            obj.draw(im, t)
        pose, _ = self.pose_at(t)
        if self.sprite:
            canvas = im.convert('RGBA')
            draw_whole(canvas, pose, self.bot_x, self.bot_y, self.scale)
            im = canvas.convert('RGB')
        else:
            canvas = im.convert('RGBA')
            im = draw_bot(canvas, pose, self.bot_x + pose.x * self.scale, self.bot_y, self.scale, self.palette).convert('RGB')
        dd = ImageDraw.Draw(im)
        outro_t0 = getattr(self, '_outro_t0', 1e9)
        for cap in self.captions:
            if t >= outro_t0:
                break
            if cap['start'] <= t <= cap['start'] + cap['dur']:
                a = min(1.0, (t - cap['start']) / 0.25) * min(1.0, (cap['start'] + cap['dur'] - t) / 0.25)
                f = font(FONT_B, cap['size'])
                maxw = self.w - 150
                words, lines, cur = cap['text'].split(), [], ''
                for wd in words:
                    probe = (cur + ' ' + wd).strip()
                    if dd.textlength(probe, font=f) <= maxw:
                        cur = probe
                    else:
                        lines.append(cur)
                        cur = wd
                if cur:
                    lines.append(cur)
                lines = lines[:3]
                lh = cap['size'] * 1.5
                block_h = lh * len(lines)
                y0 = self.h - 108 - block_h
                for i, ln in enumerate(lines):
                    tw = dd.textlength(ln, font=f)
                    x = (self.w - tw) / 2
                    dd.text((x + 3, y0 + i * lh + 3), ln, font=f, fill=(0, 0, 0, int(200 * a)))
                    dd.text((x, y0 + i * lh), ln, font=f, fill=(255, 255, 255, int(255 * a)))
        if self.progress and t < outro_t0:
            total = max(0.1, self.speed())
            k = min(1.0, t / total)
            dd.rectangle([0, 0, self.w, 7], fill=(255, 255, 255, 26))
            dd.rectangle([0, 0, int(self.w * k), 7], fill=(255, 255, 255, 150))
        return im

    # ── экспорт ───────────────────────────────────────────────────────────
    def render(self, path, audio=None, verbose=True):
        dur = self.speed()
        n = int(round(dur * self.fps))
        os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
        bg = self._background()
        cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', f'{self.w}x{self.h}', '-r', str(self.fps), '-i', '-',
               '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n):
            p.stdin.write(self.frame(i / self.fps, bg).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise RuntimeError('ffmpeg завершился с ошибкой')
        if audio:
            muxed = path + '.mux.mp4'
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', path, '-i', audio,
                            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest',
                            '-movflags', '+faststart', muxed], check=True)
            os.replace(muxed, path)
        if verbose:
            print(f'{path}: {dur:.1f} c, {n} кадров, {self.w}x{self.h}@{self.fps}')
        return path

    def export_gif(self, path, fps=15, width=960):
        tmp = path + '.mp4'
        self.render(tmp, verbose=False)
        vf = f'fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-vf', vf, path], check=True)
        os.remove(tmp)
        print(f'{path}: GIF {width}px')
        return path

    # ── сохранение сценария ───────────────────────────────────────────────
    def save(self, path):
        data = {'bot': [self.bot_x, self.bot_y], 'scale': self.scale, 'fps': self.fps,
                'size': [self.w, self.h], 'cues': self.cues,
                'captions': self.captions}
        json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        return path
