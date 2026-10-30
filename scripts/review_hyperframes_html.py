#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HyperFrames: HTML-графика 60 fps, грайн, count-up, QR, лого-монограмма."""
import json
import math
import os
import shutil
import sys

sys.path.insert(0, '/opt/qantcore/minibot')
sys.path.insert(0, '/opt/qantcore/htmlvid')

import render  # noqa: E402
from minibot import sfx  # noqa: E402
from minibot import animations as A  # noqa: E402
from minibot.character import draw_bot  # noqa: E402
from minibot.voice import Narrator  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

OUT = '/opt/qantcore/minibot/output/reviews'
WORK = '/opt/qantcore/htmlvid/hyperframes'
FPS = 60
ACC, ACC2 = '#FF7EB3', '#8BE8FF'

n = Narrator()
lines = [
    'HyperFrames превращает HTML в видео: без таймлайна и монтажа.',
    'Шестьдесят три тысячи девятьсот шестьдесят семь звёзд и восемьсот тысяч загрузок npm в неделю.',
    'Рендер: Chrome снимает кадры, FFmpeg собирает MP4. Лицензия Apache два.',
    'Подробнее на сайте qantcore.space.',
]
cues = [n.add(x) for x in lines]
dur = cues[-1][1] + 1.2

CSS = f"""
@font-face {{ font-family:'Manrope'; src:url('fonts/Manrope.ttf'); font-weight:200 800; }}
@font-face {{ font-family:'JBMono'; src:url('fonts/JetBrainsMono.ttf'); font-weight:100 800; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:#0A0711; }}
body {{ font-family:'Manrope','DejaVu Sans',sans-serif; color:#F6F2FF; }}
#stage {{ position:relative; width:1080px; height:1920px; overflow:hidden;
  background:
    radial-gradient(760px 760px at 80% 6%, rgba(255,126,179,.22), transparent 62%),
    radial-gradient(700px 700px at 8% 30%, rgba(139,232,255,.16), transparent 60%),
    radial-gradient(900px 900px at 50% 108%, rgba(150,110,255,.20), transparent 62%),
    linear-gradient(180deg,#0B0713 0%,#08060E 100%); }}
#grain {{ position:absolute; inset:-40px; opacity:.055; pointer-events:none; z-index:8;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>"); }}
#perf {{ position:absolute; inset:0; z-index:7; pointer-events:none;
  background-image:linear-gradient(90deg, rgba(8,6,14,.95) 0 54px, transparent 54px 1026px, rgba(8,6,14,.95) 1026px);
  box-shadow:inset 0 0 180px 40px rgba(0,0,0,.55); }}
header {{ position:absolute; top:78px; left:76px; right:76px; display:flex; align-items:center; gap:18px; z-index:5; }}
.logo {{ width:74px; height:74px; border-radius:20px; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(140deg,#FF7EB3,#8B5CF6); font-weight:800; font-size:27px; letter-spacing:-1px; color:#0B0713; }}
.brand {{ font-size:32px; font-weight:800; letter-spacing:.3px; }}
.kick {{ margin-left:auto; font-size:19px; letter-spacing:3px; color:rgba(255,255,255,.45);
  text-transform:uppercase; text-align:right; line-height:1.5; }}
h1 {{ position:absolute; top:182px; left:72px; right:72px; font-size:80px; font-weight:800;
  line-height:.97; letter-spacing:-1.6px; z-index:5;
  background:linear-gradient(115deg,#FFFFFF 30%,{ACC2} 92%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.tabs {{ position:absolute; top:352px; left:76px; right:76px; display:flex; gap:34px; z-index:5;
  border-bottom:2px solid rgba(255,255,255,.10); padding-bottom:14px; }}
.tab {{ font-size:21px; letter-spacing:3.4px; text-transform:uppercase; color:rgba(255,255,255,.34); font-weight:700; }}
.tab.on {{ color:#FFFFFF; }}
#tabline {{ position:absolute; height:3px; bottom:-2px; background:linear-gradient(90deg,{ACC},{ACC2}); transition:none; }}
.blk {{ position:absolute; left:76px; right:76px; z-index:4; }}
.lbl {{ font-size:21px; letter-spacing:4px; text-transform:uppercase; color:{ACC}; font-weight:700; margin-bottom:16px; }}
.num {{ font-family:'JBMono','DejaVu Sans Mono',monospace; font-variant-numeric:tabular-nums;
  font-weight:800; letter-spacing:-4px; line-height:.95;
  text-shadow:0 0 42px rgba(255,126,179,.55), 0 0 90px rgba(255,126,179,.25); }}
.unit {{ font-size:34px; color:rgba(255,255,255,.62); margin-top:10px; letter-spacing:.4px; }}
.card {{ background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.11);
  border-radius:28px; padding:30px 34px; box-shadow:0 24px 60px rgba(0,0,0,.4); }}
.pipe {{ display:flex; align-items:center; gap:16px; }}
.node {{ flex:1; text-align:center; }}
.node .ico {{ width:88px; height:88px; margin:0 auto 14px; border-radius:24px; display:flex;
  align-items:center; justify-content:center; font-size:34px; font-weight:800;
  background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.13); }}
.node .t {{ font-size:24px; font-weight:700; }}
.node .s {{ font-size:19px; color:rgba(255,255,255,.5); margin-top:6px; }}
.arrow {{ font-size:30px; color:{ACC}; opacity:.8; }}
#morph {{ font-size:132px; font-weight:800; letter-spacing:-5px; line-height:1; height:150px; position:relative; }}
#morph span {{ position:absolute; left:0; top:0; }}
#finale {{ position:absolute; inset:0; z-index:6; background:rgba(6,4,11,.96);
  display:flex; flex-direction:column; align-items:center; padding-top:330px; }}
#qr {{ width:330px; height:330px; border-radius:26px; background:#fff; padding:18px; }}
#url {{ margin-top:52px; font-size:88px; font-weight:800; letter-spacing:-2px;
  background:linear-gradient(115deg,#FFFFFF,{ACC2}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
#cta {{ position:absolute; left:0; right:0; bottom:190px; text-align:center; font-size:34px; color:rgba(255,255,255,.7); }}
#cap {{ position:absolute; left:70px; right:70px; bottom:92px; text-align:center; z-index:5;
  font-size:42px; font-weight:700; line-height:1.32; text-shadow:0 4px 24px rgba(0,0,0,.85); }}
"""

HTML = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="stage">
  <div id="grain"></div><div id="perf"></div>
  <header><div class="logo">HF</div><div class="brand">HyperFrames</div>
    <div class="kick">QANTCORE · ОБЗОР<br>HTML → MP4</div></header>
  <h1>HTML, который<br>становится видео</h1>
  <div class="tabs">
    <div class="tab" data-t="0">Суть</div><div class="tab" data-t="1">Масштаб</div>
    <div class="tab" data-t="2">Рендер</div><div class="tab" data-t="3">Итог</div>
    <div id="tabline"></div>
  </div>

  <div class="blk" id="s1" style="top:470px">
    <div class="lbl">Что это</div>
    <div id="morph"><span id="m1">HTML</span><span id="m2">MP4</span></div>
    <div class="unit" style="margin-top:26px">один файл, без таймлайна и сборки</div>
  </div>

  <div class="blk" id="s2" style="top:470px">
    <div class="lbl">Масштаб</div>
    <div class="num" id="big" style="font-size:150px">63 967</div>
    <div class="unit">звёзд на GitHub · 811 570 загрузок npm в неделю</div>
    <div class="card" style="margin-top:34px; font-size:26px; color:rgba(255,255,255,.72)">
      Apache-2.0 · версия 0.8.160 · октябрь 2026</div>
  </div>

  <div class="blk" id="s3" style="top:470px">
    <div class="lbl">Рендер</div>
    <div class="card pipe">
      <div class="node"><div class="ico">◎</div><div class="t">Chrome</div><div class="s">headless</div></div>
      <div class="arrow">→</div>
      <div class="node"><div class="ico">▤</div><div class="t">Кадры</div><div class="s">60 fps</div></div>
      <div class="arrow">→</div>
      <div class="node"><div class="ico">ƒ</div><div class="t">FFmpeg</div><div class="s">MP4</div></div>
    </div>
    <div class="unit" style="margin-top:28px">открытый исходный код, без проприетарных зависимостей</div>
  </div>

  <div id="finale">
    <img id="qr" src="qr.png">
    <div id="url">qantcore.space</div>
    <div id="cta">обзор HyperFrames → попробуй сам</div>
  </div>
  <div id="cap"></div>
</div>
<script>
const CUE = {json.dumps([[c[0], c[1]] for c in cues])};
const DUR = {dur:.2f};
const CAPS = {json.dumps([[cues[0][0], cues[0][1], 'HTML превращается в MP4'],
                          [cues[1][0], cues[1][1], '63 967 звёзд и 811 570 загрузок'],
                          [cues[2][0], cues[2][1], 'Chrome снимает кадры, FFmpeg кодирует'],
                          [cues[3][0], cues[3][1], 'Подробнее на сайте']], ensure_ascii=False)};
let T = parseFloat(new URLSearchParams(location.search).get('t') || '0');
const F = CUE[CUE.length - 1];
const fmt = v => Math.round(v).toString().replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ' ');

function fade(el, a, b, k) {{
  const i = Math.min(1, Math.max(0, (T - a) / 0.3));
  const o = Math.min(1, Math.max(0, (b - T) / 0.3));
  const v = Math.min(i, o);
  el.style.opacity = v.toFixed(3);
  el.style.transform = 'translateY(' + ((1 - i) * 26).toFixed(1) + 'px)';
  el.style.visibility = v <= 0.001 ? 'hidden' : 'visible';
}}

function applyFrame(t) {{
  T = t;
  const s1 = CUE[0][0], s2 = CUE[1][0], s3 = CUE[2][0], s4 = CUE[3][0];
  fade(document.getElementById('s1'), s1, s2);
  fade(document.getElementById('s2'), s2, s3);
  fade(document.getElementById('s3'), s3, s4);

  // морфинг HTML → MP4
  const mk = Math.min(1, Math.max(0, (T - s1 - 0.7) / 0.6));
  const m1 = document.getElementById('m1'), m2 = document.getElementById('m2');
  m1.style.opacity = (1 - mk).toFixed(3);
  m1.style.filter = 'blur(' + (mk * 10).toFixed(1) + 'px)';
  m1.style.transform = 'translateY(' + (-mk * 40).toFixed(1) + 'px)';
  m2.style.opacity = mk.toFixed(3);
  m2.style.filter = 'blur(' + ((1 - mk) * 10).toFixed(1) + 'px)';
  m2.style.transform = 'translateY(' + ((1 - mk) * 40).toFixed(1) + 'px)';
  m2.style.color = '{ACC2}';

  // count-up
  const ck = Math.min(1, Math.max(0, (T - s2 - 0.15) / 1.5));
  const eased = 1 - Math.pow(1 - ck, 4);
  document.getElementById('big').textContent = fmt(63967 * eased);

  // табы
  const idx = T >= s4 ? 3 : T >= s3 ? 2 : T >= s2 ? 1 : 0;
  const tabs = [...document.querySelectorAll('.tab')];
  tabs.forEach((el, i) => el.classList.toggle('on', i === idx));
  const line = document.getElementById('tabline');
  const act = tabs[idx].getBoundingClientRect();
  const box = document.querySelector('.tabs').getBoundingClientRect();
  line.style.left = (act.left - box.left) + 'px';
  line.style.width = act.width + 'px';

  // финал
  const fk = Math.min(1, Math.max(0, (T - s4) / 0.5));
  const fin = document.getElementById('finale');
  fin.style.opacity = fk.toFixed(3);
  document.querySelectorAll('header, h1, .tabs').forEach(el => {{ if (fk > 0.5) el.style.visibility = 'hidden'; }});
  const pulse = 1 + 0.03 * (0.5 + 0.5 * Math.sin((T - s4) * Math.PI));
  document.getElementById('url').style.transform = 'scale(' + (pulse * (0.97 + 0.03 * fk)).toFixed(4) + ')';
  document.getElementById('cta').style.opacity = Math.min(1, Math.max(0, (T - s4 - 0.5) / 0.5)).toFixed(3);

  // субтитры
  const cap = document.getElementById('cap');
  const a = CAPS.find(c => T >= c[0] && T <= c[1] && T < s4);
  if (a) {{
    cap.textContent = a[2];
    cap.style.opacity = Math.min(1, (T - a[0]) / 0.2, (a[1] - T) / 0.2).toFixed(3);
  }} else {{ cap.style.opacity = '0'; }}
}}
window.applyFrame = applyFrame;
applyFrame(T);
</script></body></html>"""

os.makedirs(WORK, exist_ok=True)
os.makedirs(os.path.join(WORK, 'fonts'), exist_ok=True)
shutil.copy('/opt/qantcore/htmlvid/fonts/Manrope.ttf', os.path.join(WORK, 'fonts/Manrope.ttf'))
shutil.copy('/opt/qantcore/htmlvid/fonts/JetBrainsMono.ttf', os.path.join(WORK, 'fonts/JetBrainsMono.ttf'))
shutil.copy('/opt/qantcore/htmlvid/qr.png', os.path.join(WORK, 'qr.png'))
html = os.path.join(WORK, 'index.html')
with open(html, 'w', encoding='utf-8') as f:
    f.write(HTML)

if os.environ.get('PREVIEW'):
    for t in (1.2, 3.5, 6.0, 11.0, 15.0):
        render._shot((int(t * 100), t, html, WORK))
        os.replace(os.path.join(WORK, f'{int(t * 100):05d}.png'), os.path.join(WORK, f'p{t}.png'))
    print('preview', round(dur, 2), 'cues', [round(c[0], 2) for c in cues])
    sys.exit(0)

frames, count = render.render_frames_cdp(html, os.path.join(WORK, 'frames'), dur, FPS, port=9337)

BX, BY, SCALE = 250, 1300, 1.10
plan = [(0, 'speak', cues[0][1] - cues[0][0]),
        (cues[1][0] - 0.1, 'look', max(0.6, cues[2][0] - cues[1][0] - 0.3)),
        (cues[2][0], 'point', max(0.8, cues[3][0] - cues[2][0] - 0.4), 'right'),
        (cues[3][0], 'point', dur - cues[3][0], 'up')]


def pose_at(t):
    base = None
    for item in plan:
        st, act, d = item[0], item[1], item[2]
        direction = item[3] if len(item) > 3 else None
        if st <= t < st + d:
            base = A.action_pose(act, t - st, d, direction)
            break
    if base is None:
        base = A.action_pose('idle', 0, 1)
    # idle: дыхание, моргание, антенна
    base.y += 2.4 * math.sin(2 * math.pi * t / 3.4)
    base.antenna += 5 * math.sin(2 * math.pi * t / 2.6)
    if (t % 4.3) < 0.12:
        base.eye = 0.0
    return base


for i in range(count):
    t = i / FPS
    p = os.path.join(frames, f'{i:05d}.jpg')
    base = Image.open(p).convert('RGBA')
    canvas = Image.new('RGBA', base.size, (0, 0, 0, 0))
    canvas = draw_bot(canvas, pose_at(t), BX, BY, SCALE, 'futuristic')
    d = ImageDraw.Draw(canvas)
    glow = int(18 + 14 * (0.5 + 0.5 * math.sin(2 * math.pi * t / 2.2)))
    cx, cy, r = BX, BY - 52, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(160, 130, 255, glow))
    if t >= cues[3][0] + 0.2:
        k = min(1.0, (t - cues[3][0] - 0.2) / 0.9)
        x1, y1 = BX + 105, BY - 250
        x2, y2 = 560, 700
        d.line([(x1, y1), (x1 + (x2 - x1) * k, y1 + (y2 - y1) * k)],
               fill=(255, 126, 179, 235), width=8)
        if k > 0.9:
            d.polygon([(x2 - 16, y2 + 6), (x2 + 16, y2 + 6), (x2, y2 - 26)], fill=(255, 126, 179, 240))
    base.alpha_composite(canvas)
    base.convert('RGB').save(p, quality=92)

voice = os.path.join(OUT, 'hyperframes.wav')
n.write(voice)
bed = sfx.build(dur, cue_starts=[c[0] for c in cues],
                pings=[cues[1][0] + 0.15, cues[1][0] + 1.2],
                out=os.path.join(OUT, 'hyperframes-bed.wav'))
mixed = sfx.mix(voice, bed, os.path.join(OUT, 'hyperframes-mix.wav'))

final = os.path.join(OUT, 'hyperframes.mp4')
render.encode(frames, mixed, final, fps=FPS)

# SRT
def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')

caps = ['HTML превращается в MP4', '63 967 звёзд и 811 570 загрузок',
        'Chrome снимает кадры, FFmpeg кодирует', 'Подробнее на сайте qantcore.space']
with open(os.path.join(OUT, 'hyperframes.srt'), 'w', encoding='utf-8') as f:
    for i, ((a, b), c) in enumerate(zip(cues, caps), 1):
        f.write(f'{i}\n{ts(a)} --> {ts(b)}\n{c}\n\n')

n.cleanup()
print('=== hyperframes', round(dur, 2))
