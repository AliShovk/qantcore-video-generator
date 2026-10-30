#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Постпродакшн Graphify: склейка, маскот, подложка, субтитры Whisper."""
import math
import os
import shutil
import subprocess
import sys

sys.path.insert(0, '/opt/qantcore/minibot')
sys.path.insert(0, '/opt/qantcore/htmlvid')

from PIL import Image  # noqa: E402

from mascot import Mascot  # noqa: E402
from minibot import sfx  # noqa: E402

BASE = '/opt/qantcore/htmlvid/wb-graphify'
OUT = '/opt/qantcore/minibot/output/reviews'
FPS = 24

# 1. склейка с обрезкой пустых стартов
cmd = ['ffmpeg', '-y', '-v', 'error']
for i in range(1, 6):
    cmd += ['-i', f'{BASE}/s{i}.mp4']
tr = ';'.join([f'[{i}:v]trim=start=0.95,setpts=PTS-STARTPTS[v{i}]' for i in range(5)])
ta = ';'.join([f'[{i}:a]atrim=start=0.95,asetpts=PTS-STARTPTS[a{i}]' for i in range(5)])
fc = (tr + ';' + ta + ';' + ''.join(f'[v{i}][a{i}]' for i in range(5)) +
      'concat=n=5:v=1:a=1[vo][ao];[vo]tpad=stop_mode=clone:stop_duration=1.2[vv]')
cmd += ['-filter_complex', fc, '-map', '[vv]', '-map', '[ao]', '-c:v', 'libx264',
        '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
        '-b:a', '160k', f'{BASE}/base.mp4']
subprocess.run(cmd, check=True)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'csv=p=0', f'{BASE}/base.mp4'],
                           capture_output=True, text=True).stdout)

# 2. маскот поверх каждого кадра
fr = f'{BASE}/frames'
shutil.rmtree(fr, ignore_errors=True)
os.makedirs(fr)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{BASE}/base.mp4', '-vf', f'fps={FPS}',
                f'{fr}/%05d.png'], check=True)
files = sorted(os.listdir(fr))
m = Mascot(width=420)
for i, f in enumerate(files):
    t = i / FPS
    im = Image.open(os.path.join(fr, f)).convert('RGBA')
    m.overlay(im, t)
    im.convert('RGB').save(os.path.join(fr, f.replace('.png', '.jpg')), quality=92)
    os.remove(os.path.join(fr, f))

# 3. звук: подложка + голос
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{BASE}/base.mp4', '-vn', '-ar', '44100',
                f'{BASE}/voice.wav'], check=True)
bed = sfx.build(dur, cue_starts=[0.4, 6.3, 12.9, 18.4, 23.6], pings=[0.6],
                out=f'{BASE}/bed.wav')
sfx.mix(f'{BASE}/voice.wav', bed, f'{BASE}/mix.wav')

video = f'{OUT}/graphify-wb.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{fr}/%05d.jpg',
                '-i', f'{BASE}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264',
                '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                '-b:a', '160k', '-shortest', video], check=True)

# 4. субтитры Whisper по финальной дорожке
import whisper  # noqa: E402

model = whisper.load_model('small')
res = model.transcribe(f'{BASE}/mix.wav', language='ru', word_timestamps=False)


def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


srt = []
for i, seg in enumerate(res['segments'], 1):
    text = seg['text'].strip()
    if not text:
        continue
    srt.append(f"{i}\n{ts(seg['start'])} --> {ts(seg['end'])}\n{text}\n")
open(f'{OUT}/graphify-wb.srt', 'w', encoding='utf-8').write('\n'.join(srt))

for f in ('graphify-wb.mp4', 'graphify-wb.srt'):
    subprocess.run(['cp', f'{OUT}/{f}', f'/var/www/qantcore/video/reviews/{f}'], check=True)
print('done', round(dur, 2), 'segments', len(res['segments']))
