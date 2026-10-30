#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI-SEO: типографический ролик без персонажа, 1080×1920, Silero."""
import json
import os
import shutil
import sys

sys.path.insert(0, '/opt/qantcore/minibot')
sys.path.insert(0, '/opt/qantcore/htmlvid')

import render  # noqa: E402
from minibot import sfx  # noqa: E402
from minibot.voice import Narrator  # noqa: E402

OUT = '/opt/qantcore/minibot/output/reviews'
WORK = '/opt/qantcore/htmlvid/aiseo'
FPS = 30
ACC, ACC2 = '#7DF0C0', '#8BD4FF'

n = Narrator(speaker='baya')
lines = [
    'AI-SEO: собираем запросы, кластеризуем и получаем контент-план одним пайплайном.',
    'Пять шагов: сбор данных, кластеризация, контент-план, аудит и отчёт.',
    'На входе семантика из Search Console, на выходе Markdown и Excel.',
    'Подробнее на сайте qantcore.space.',
]
cues = [n.add(x) for x in lines]
dur = cues[-1][1] + 1.1

CSS = f"""
@font-face {{ font-family:'Manrope'; src:url('fonts/Manrope.ttf'); font-weight:200 800; }}
@font-face {{ font-family:'JBMono'; src:url('fonts/JetBrainsMono.ttf'); font-weight:100 800; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:#07110E; }}
body {{ font-family:'Manrope','DejaVu Sans',sans-serif; color:#F1FFF9; }}
#stage {{ position:relative; width:1080px; height:1920px; overflow:hidden;
  background:
    radial-gradient(720px 720px at 84% 4%, rgba(125,240,192,.20), transparent 62%),
    radial-gradient(680px 680px at 6% 26%, rgba(139,212,255,.16), transparent 60%),
    radial-gradient(900px 900px at 50% 108%, rgba(120,255,200,.12), transparent 62%),
    linear-gradient(180deg,#08130F 0%,#060B09 100%); }}
#grain {{ position:absolute; inset:-40px; opacity:.05; pointer-events:none; z-index:8;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>"); }}
header {{ position:absolute; top:80px; left:76px; right:76px; display:flex; align-items:center; gap:18px; z-index:5; }}
.logo {{ width:72px; height:72px; border-radius:20px; background:linear-gradient(140deg,{ACC},#1E7F63);
  display:flex; align-items:center; justify-content:center; color:#04120D; font-weight:800; font-size:25px; }}
.brand {{ font-size:31px; font-weight:800; }}
.kick {{ margin-left:auto; font-size:19px; letter-spacing:3px; color:rgba(255,255,255,.45);
  text-transform:uppercase; text-align:right; line-height:1.5; }}
h1 {{ position:absolute; top:184px; left:72px; right:72px; font-size:92px; font-weight:800;
  line-height:.95; letter-spacing:-2px; z-index:5;
  background:linear-gradient(115deg,#FFFFFF 32%,{ACC} 95%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.tabs {{ position:absolute; top:392px; left:76px; right:76px; display:flex; gap:32px; z-index:5;
  border-bottom:2px solid rgba(255,255,255,.10); padding-bottom:13px; }}
.tab {{ font-size:20px; letter-spacing:3.2px; text-transform:uppercase; color:rgba(255,255,255,.32); font-weight:700; }}
.tab.on {{ color:#fff; }}
#tabline {{ position:absolute; height:3px; bottom:-2px; background:linear-gradient(90deg,{ACC},{ACC2}); }}
.blk {{ position:absolute; left:76px; right:76px; z-index:4; }}
.lbl {{ font-size:21px; letter-spacing:4px; text-transform:uppercase; color:{ACC}; font-weight:700; margin-bottom:18px; }}
.num {{ font-family:'JBMono',monospace; font-weight:800; font-size:200px; line-height:.9;
  letter-spacing:-8px; text-shadow:0 0 46px rgba(125,240,192,.45); }}
.unit {{ font-size:36px; color:rgba(255,255,255,.85); margin-top:8px; }}
.card {{ background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.11);
  border-radius:28px; padding:30px 32px; box-shadow:0 24px 60px rgba(0,0,0,.4); }}
.step {{ display:flex; align-items:center; gap:22px; padding:24px 0; border-bottom:1px solid rgba(255,255,255,.07); }}
.step:last-child {{ border-bottom:none; }}
.step .n {{ width:52px; height:52px; border-radius:16px; background:rgba(125,240,192,.12);
  color:{ACC}; font-family:'JBMono',monospace; font-weight:800; font-size:24px;
  display:flex; align-items:center; justify-content:center; }}
.step .t {{ font-size:33px; font-weight:700; color:#FFFFFF; }}
.step .s {{ font-size:21px; color:rgba(255,255,255,.68); margin-top:2px; }}
.io {{ display:flex; gap:18px; }}
.io .card {{ flex:1; }}
.io .h {{ font-size:19px; letter-spacing:3px; text-transform:uppercase; color:{ACC}; margin-bottom:12px; }}
.io .v {{ font-family:'JBMono',monospace; font-size:26px; line-height:1.55; color:#FFFFFF; }}
#finale {{ position:absolute; inset:0; z-index:6; background:rgba(4,10,8,.96);
  display:flex; flex-direction:column; align-items:center; padding-top:380px; }}
#qr {{ width:330px; height:330px; border-radius:26px; background:#fff; padding:18px; }}
#url {{ margin-top:56px; font-size:88px; font-weight:800; letter-spacing:-2px;
  background:linear-gradient(115deg,#FFFFFF,{ACC}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
#cta {{ position:absolute; bottom:190px; left:0; right:0; text-align:center; font-size:32px; color:rgba(255,255,255,.68); }}
#foot {{ position:absolute; left:76px; right:76px; bottom:452px; display:flex; gap:16px; z-index:4; }}
.chip {{ flex:1; text-align:center; padding:20px 10px; border-radius:20px;
  background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.18); }}
.chip b {{ display:block; font-family:'JBMono',monospace; font-size:40px; color:#FFFFFF; }}
.chip span {{ font-size:19px; color:rgba(255,255,255,.78); }}
#cap {{ position:absolute; left:70px; right:70px; bottom:92px; text-align:center; z-index:5;
  font-size:42px; font-weight:700; line-height:1.32; text-shadow:0 4px 24px rgba(0,0,0,.85); }}
"""

HTML = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="stage">
  <div id="grain"></div>
  <header><div class="logo">SEO</div><div class="brand">Qantcore</div>
    <div class="kick">ГАЙД · 2026<br>AI + SEO</div></header>
  <h1>AI для SEO:<br>пайплайн целиком</h1>
  <div class="tabs">
    <div class="tab" data-t="0">Пайплайн</div><div class="tab" data-t="1">Шаги</div>
    <div class="tab" data-t="2">Выход</div><div class="tab" data-t="3">Итог</div>
    <div id="tabline"></div>
  </div>

  <div class="blk" id="s1" style="top:500px">
    <div class="lbl">Один прогон</div>
    <div class="num" id="big">0</div>
    <div class="unit">шагов: данные → кластеры → план → аудит → отчёт</div>
    <div class="card" style="margin-top:36px; font-size:26px; color:rgba(255,255,255,.72)">
      топ-500 запросов за 28 дней · Python, pandas, OpenAI API</div>
  </div>

  <div class="blk" id="s2" style="top:500px">
    <div class="lbl">Пайплайн</div>
    <div class="card">
      <div class="step"><div class="n">1</div><div><div class="t">Сбор данных</div>
        <div class="s">Search Console, Ahrefs, CSV</div></div></div>
      <div class="step"><div class="n">2</div><div><div class="t">AI-кластеризация</div>
        <div class="s">смысловые группы, а не простые совпадения</div></div></div>
      <div class="step"><div class="n">3</div><div><div class="t">Контент-план</div>
        <div class="s">темы, интенты, приоритет</div></div></div>
      <div class="step"><div class="n">4</div><div><div class="t">SEO-аудит</div>
        <div class="s">парсинг страниц и рекомендации</div></div></div>
      <div class="step"><div class="n">5</div><div><div class="t">Отчёт</div>
        <div class="s">Markdown и Excel</div></div></div>
    </div>
  </div>

  <div class="blk" id="s3" style="top:500px">
    <div class="lbl">Что на входе и выходе</div>
    <div class="io">
      <div class="card"><div class="h">Вход</div><div class="v">semantic_core.csv<br>500 запросов<br>volume · intent</div></div>
      <div class="card"><div class="h">Выход</div><div class="v">clusters.json<br>content_plan.md<br>audit.xlsx</div></div>
    </div>
    <div class="unit" style="margin-top:30px">один скрипт вместо трёх таблиц и ручной сверки</div>
  </div>

  <div id="finale">
    <img id="qr" src="qr.png">
    <div id="url">qantcore.space</div>
    <div id="cta">гайд по AI-SEO → разобрать по шагам</div>
  </div>
  <div id="foot">
    <div class="chip"><b>500</b><span>запросов</span></div>
    <div class="chip"><b>5</b><span>шагов</span></div>
    <div class="chip"><b>3</b><span>формата</span></div>
  </div>
  <div id="cap"></div>
</div>
<script>
const CUE = {json.dumps([[c[0], c[1]] for c in cues])};
const CAPS = {json.dumps([[cues[0][0], cues[0][1], 'Пайплайн от запросов до плана'],
                          [cues[1][0], cues[1][1], '5 шагов'],
                          [cues[2][0], cues[2][1], 'CSV на входе, Markdown на выходе'],
                          [cues[3][0], cues[3][1], 'Подробнее на сайте']], ensure_ascii=False)};
const DUR = {dur:.2f};
let T = parseFloat(new URLSearchParams(location.search).get('t') || '0');
const F = CUE[CUE.length - 1];

function fade(el, a, b) {{
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

  const ck = Math.min(1, Math.max(0, (T - s1 - 0.2) / 1.2));
  document.getElementById('big').textContent = Math.round(5 * (1 - Math.pow(1 - ck, 4)));

  const idx = T >= s4 ? 3 : T >= s3 ? 2 : T >= s2 ? 1 : 0;
  const tabs = [...document.querySelectorAll('.tab')];
  tabs.forEach((el, i) => el.classList.toggle('on', i === idx));
  const act = tabs[idx].getBoundingClientRect();
  const box = document.querySelector('.tabs').getBoundingClientRect();
  const line = document.getElementById('tabline');
  line.style.left = (act.left - box.left) + 'px';
  line.style.width = act.width + 'px';

  const fk = Math.min(1, Math.max(0, (T - s4) / 0.5));
  const fin = document.getElementById('finale');
  fin.style.opacity = fk.toFixed(3);
  document.querySelectorAll('header, h1, .tabs').forEach(el => {{ if (fk > 0.5) el.style.visibility = 'hidden'; }});
  const pulse = 1 + 0.03 * (0.5 + 0.5 * Math.sin((T - s4) * Math.PI));
  document.getElementById('url').style.transform = 'scale(' + (pulse * (0.97 + 0.03 * fk)).toFixed(4) + ')';

  const foot = document.getElementById('foot');
  if (foot) {{
    foot.style.opacity = Math.min(1, Math.max(0, (T - 0.5) / 1.0)).toFixed(3);
    foot.style.visibility = fk > 0.5 ? 'hidden' : 'visible';
  }}
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
    for t in (1.0, 4.5, 8.5, 12.5):
        render._shot((int(t * 100), t, html, WORK))
        os.replace(os.path.join(WORK, f'{int(t * 100):05d}.png'), os.path.join(WORK, f'p{t}.png'))
    print('preview', round(dur, 2), 'cues', [round(c[0], 2) for c in cues])
    sys.exit(0)

frames, count = render.render_frames_cdp(html, os.path.join(WORK, 'frames'), dur, FPS, port=9341)
voice = os.path.join(OUT, 'ai-seo.wav')
n.write(voice)
bed = sfx.build(dur, cue_starts=[c[0] for c in cues], pings=[cues[0][0] + 0.2],
                out=os.path.join(OUT, 'ai-seo-bed.wav'))
mixed = sfx.mix(voice, bed, os.path.join(OUT, 'ai-seo-mix.wav'))
final = os.path.join(OUT, 'ai-seo.mp4')
render.encode(frames, mixed, final, fps=FPS)

def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')

caps = ['Пайплайн от запросов до плана', 'Пять шагов', 'CSV на входе, Markdown на выходе',
        'Подробнее на сайте qantcore.space']
with open(os.path.join(OUT, 'ai-seo.srt'), 'w', encoding='utf-8') as f:
    for i, ((a, b), c) in enumerate(zip(cues, caps), 1):
        f.write(f'{i}\n{ts(a)} --> {ts(b)}\n{c}\n\n')
n.cleanup()
print('=== ai-seo', round(dur, 2))
