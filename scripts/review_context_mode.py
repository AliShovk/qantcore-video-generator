#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Context Mode: белый фон, схемы из обзора, новый голос (eugene), маскот."""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, '/opt/qantcore/minibot')
sys.path.insert(0, '/opt/qantcore/htmlvid')

import render  # noqa: E402
from mascot import Mascot  # noqa: E402
from minibot import sfx  # noqa: E402
from minibot.voice import Narrator  # noqa: E402
from PIL import Image  # noqa: E402

OUT = '/opt/qantcore/minibot/output/reviews'
WORK = '/opt/qantcore/htmlvid/cm'
FPS = 30
ACC, ACC2 = '#0E9F8A', '#2563EB'

n = Narrator(speaker='eugene')
lines = [
    'Context Mode — MCP-сервер, который держит сырые данные вне контекста агента.',
    'Снимок страницы — пятьдесят шесть килобайт, двадцать issue — пятьдесят девять, лог доступа — сорок пять.',
    'Экономия по замерам автора — от девяноста четырёх до ста процентов.',
    'За семь недель проект вырос с восемнадцати до тридцати тысяч звёзд.',
    'Внутри четыре слоя: песочница, база событий, think in code и свой стиль.',
    'Подробнее на сайте qantcore.space.',
]
cues = [n.add(x) for x in lines]
dur = cues[-1][1] + 0.9

CSS = f"""
@font-face {{ font-family:'Manrope'; src:url('fonts/Manrope.ttf'); font-weight:200 800; }}
@font-face {{ font-family:'JBMono'; src:url('fonts/JetBrainsMono.ttf'); font-weight:100 800; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:#FFFFFF; }}
body {{ font-family:'Manrope','DejaVu Sans',sans-serif; color:#12161C; }}
#stage {{ position:relative; width:1080px; height:1920px; background:#FFFFFF; overflow:hidden; }}
header {{ position:absolute; top:78px; left:76px; right:76px; display:flex; align-items:center; gap:16px; }}
.logo {{ width:70px; height:70px; border-radius:18px; background:#0E9F8A; color:#fff;
  display:flex; align-items:center; justify-content:center; font-weight:800; font-size:26px; }}
.brand {{ font-size:30px; font-weight:800; }}
.kick {{ margin-left:auto; font-size:18px; letter-spacing:3px; color:#8A94A0; text-transform:uppercase; text-align:right; line-height:1.5; }}
h1 {{ position:absolute; top:180px; left:74px; right:74px; font-size:82px; font-weight:800; line-height:.98; letter-spacing:-1.6px; }}
h1 span {{ color:{ACC}; }}
.num {{ font-family:'JBMono',monospace; font-weight:800; font-size:150px; line-height:.95; letter-spacing:-6px; }}
.unit {{ font-size:32px; color:#5B6B7A; margin-top:6px; }}
.small {{ font-size:22px; letter-spacing:2.6px; text-transform:uppercase; color:{ACC}; font-weight:700; margin-bottom:14px; }}
.card {{ background:#F5F8FA; border:1px solid #DFE7EC; border-radius:24px; padding:24px 26px; }}
.shot {{ width:100%; border-radius:20px; border:1px solid #E3EAEF; }}
.list {{ display:flex; flex-direction:column; gap:12px; }}
.row {{ display:flex; align-items:center; gap:14px; font-size:27px; font-weight:700; }}
.dot {{ width:12px; height:12px; border-radius:50%; background:{ACC}; }}
.row small {{ font-size:19px; color:#5B6B7A; font-weight:500; margin-left:auto; }}
#finale {{ position:absolute; inset:0; background:#FFFFFF; display:flex; flex-direction:column;
  align-items:center; justify-content:flex-start; padding-top:380px; }}
#qr {{ width:300px; height:300px; border-radius:24px; background:#fff; padding:16px; border:1px solid #E3EAEF; }}
#url {{ margin-top:46px; font-size:84px; font-weight:800; letter-spacing:-2px; color:{ACC}; }}
#cta {{ position:absolute; bottom:330px; left:0; right:0; text-align:center; font-size:30px; color:#5B6B7A; }}
#cap {{ position:absolute; left:70px; right:70px; bottom:640px; text-align:center; font-size:38px;
  font-weight:700; line-height:1.3; color:#12161C; }}
"""

HTML = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="stage">
  <header><div class="logo">CM</div><div class="brand">Qantcore</div>
    <div class="kick">ОБЗОР · 2026<br>MCP · КОНТЕКСТ</div></header>
  <h1>Context Mode:<br><span>меньше мусора</span><br>в контексте</h1>

  <div class="blk" id="s1" style="position:absolute;left:76px;right:76px;top:560px">
    <div class="small">Масштаб</div>
    <div class="num">30 706</div>
    <div class="unit">звёзд GitHub · 14 546 загрузок npm в неделю · 11 инструментов</div>
    <div class="card" style="margin-top:28px;font-size:24px;color:#3E4A55">
      один скрипт вместо пятидесяти файлов в промпте</div>
  </div>

  <div class="blk" id="s2" style="position:absolute;left:76px;right:76px;top:520px">
    <div class="small">Сколько весит сырой вывод</div>
    <div class="card list">
      <div class="row"><div class="dot"></div>Снимок Playwright<small>56 КБ</small></div>
      <div class="row"><div class="dot"></div>20 GitHub issue<small>59 КБ</small></div>
      <div class="row"><div class="dot"></div>Лог доступа<small>45 КБ</small></div>
    </div>
    <div class="unit" style="margin-top:24px">за полчаса — до 40 % контекста</div>
  </div>

  <div class="blk" id="s3" style="position:absolute;left:76px;right:76px;top:520px">
    <div class="small">Сколько экономит</div>
    <img class="shot" src="scheme2.png">
  </div>

  <div class="blk" id="s4" style="position:absolute;left:76px;right:76px;top:520px">
    <div class="small">Рост за семь недель</div>
    <img class="shot" src="scheme3.png">
    <div class="unit" style="margin-top:22px">18,1 тыс → 30,7 тыс звёзд</div>
  </div>

  <div class="blk" id="s5" style="position:absolute;left:76px;right:76px;top:520px">
    <div class="small">Четыре слоя</div>
    <div class="card list">
      <div class="row"><div class="dot"></div>Песочница<small>сырой вывод не в контексте</small></div>
      <div class="row"><div class="dot"></div>База событий<small>SQLite + FTS5</small></div>
      <div class="row"><div class="dot"></div>Think in Code<small>скрипт вместо вызовов</small></div>
      <div class="row"><div class="dot"></div>Свой стиль<small>без навязывания</small></div>
    </div>
  </div>

  <div id="finale">
    <img id="qr" src="qr.png">
    <div id="url">qantcore.space</div>
    <div id="cta">обзор Context Mode → разобрать по шагам</div>
  </div>
  <div id="cap"></div>
</div>
<script>
const CUE = {json.dumps([[c[0], c[1]] for c in cues])};
const CAPS = {json.dumps([[cues[0][0], cues[0][1], 'Держит сырые данные вне контекста'],
                          [cues[1][0], cues[1][1], '56 / 59 / 45 КБ сырого вывода'],
                          [cues[2][0], cues[2][1], 'Экономия 94–100 %'],
                          [cues[3][0], cues[3][1], '18,1k → 30,7k звёзд'],
                          [cues[4][0], cues[4][1], 'Четыре слоя внутри'],
                          [cues[5][0], cues[5][1], 'Подробнее на сайте']], ensure_ascii=False)};
const DUR = {dur:.2f};
let T = parseFloat(new URLSearchParams(location.search).get('t') || '0');

function fade(el, a, b) {{
  const i = Math.min(1, Math.max(0, (T - a) / 0.3));
  const o = Math.min(1, Math.max(0, (b - T) / 0.3));
  const v = Math.min(i, o);
  el.style.opacity = v.toFixed(3);
  el.style.transform = 'translateY(' + ((1 - i) * 24).toFixed(1) + 'px)';
  el.style.visibility = v <= 0.001 ? 'hidden' : 'visible';
}}

function applyFrame(t) {{
  T = t;
  const s = CUE.map(c => c[0]).concat([DUR]);
  ['s1', 's2', 's3', 's4', 's5'].forEach((id, i) => fade(document.getElementById(id), s[i], s[i + 1]));
  const fk = Math.min(1, Math.max(0, (T - s[5]) / 0.45));
  const fin = document.getElementById('finale');
  fin.style.opacity = fk.toFixed(3);
  document.querySelectorAll('header, h1, .blk').forEach(el => {{ if (fk > 0.55) el.style.visibility = 'hidden'; }});
  const cap = document.getElementById('cap');
  const a = CAPS.find(c => T >= c[0] && T <= c[1] && T < s[5]);
  if (a) {{
    cap.textContent = a[2];
    cap.style.opacity = Math.min(1, (T - a[0]) / 0.2, (a[1] - T) / 0.2).toFixed(3);
  }} else {{ cap.style.opacity = '0'; }}
}}
window.applyFrame = applyFrame;
applyFrame(T);
</script></body></html>"""

os.makedirs(os.path.join(WORK, 'fonts'), exist_ok=True)
shutil.copy('/opt/qantcore/htmlvid/fonts/Manrope.ttf', os.path.join(WORK, 'fonts/Manrope.ttf'))
shutil.copy('/opt/qantcore/htmlvid/fonts/JetBrainsMono.ttf', os.path.join(WORK, 'fonts/JetBrainsMono.ttf'))
shutil.copy('/opt/qantcore/htmlvid/qr.png', os.path.join(WORK, 'qr.png'))
html = os.path.join(WORK, 'index.html')
open(html, 'w', encoding='utf-8').write(HTML)

if os.environ.get('PREVIEW'):
    for t in (1.5, 4.0, 7.0, 11.0, 14.5, 17.0):
        render._shot((int(t * 100), t, html, WORK))
        os.replace(os.path.join(WORK, f'{int(t * 100):05d}.png'), os.path.join(WORK, f'p{t}.png'))
    print('preview', round(dur, 2), [round(c[0], 2) for c in cues])
    sys.exit(0)

frames, count = render.render_frames_cdp(html, os.path.join(WORK, 'frames'), dur, FPS, port=9347)
voice = os.path.join(WORK, 'voice.wav')
n.write(voice)
bed = sfx.build(dur, cue_starts=[c[0] for c in cues], pings=[cues[0][0] + 0.25],
                out=os.path.join(WORK, 'bed.wav'), bed_level=0.03)
mixed = sfx.mix(voice, bed, os.path.join(WORK, 'mix.wav'))

m = Mascot(width=300, ground=96, coin_size=120)
fr = os.path.join(WORK, 'frames')
for i, f in enumerate(sorted(os.listdir(fr))):
    p = os.path.join(fr, f)
    im = Image.open(p).convert('RGBA')
    if i / FPS < cues[-1][0] + 0.2:
        m.overlay(im, i / FPS)
    im.convert('RGB').save(p.replace('.jpg', '.jpg'), quality=92)

render.encode(fr, mixed, os.path.join(OUT, 'context-mode.mp4'), fps=FPS)

def ts(x):
    h, mm, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{mm:02d}:{s:06.3f}'.replace('.', ',')

caps = ['Держит сырые данные вне контекста агента', 'Снимок 56 КБ, 20 issue 59 КБ, лог 45 КБ',
        'Экономия по замерам автора — 94–100 %', 'За семь недель: 18,1k → 30,7k звёзд',
        'Песочница, база событий, think in code, стиль', 'Подробнее на сайте qantcore.space']
srt = '\n'.join(f'{i}\n{ts(a)} --> {ts(b)}\n{c}\n' for i, ((a, b), c) in enumerate(zip(cues, caps), 1))
open(os.path.join(OUT, 'context-mode.srt'), 'w', encoding='utf-8').write(srt)
for f in ('context-mode.mp4', 'context-mode.srt'):
    subprocess.run(['cp', os.path.join(OUT, f), f'/var/www/qantcore/video/reviews/{f}'], check=True)
n.cleanup()
print('=== context-mode', round(dur, 2))
