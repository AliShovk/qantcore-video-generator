#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Llama 3 локально: 25 с, HTML-графика + ходящая ворона с большим мозгом внизу."""
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_sys.path.insert(0, _os.path.join(_ROOT, 'pkg'))
import json
import os
import shutil
import sys

_sys.path.insert(0, _os.path.join(_ROOT, 'pkg'))
_sys.path.insert(0, _os.path.join(_ROOT, 'pkg', 'rendering'))

import render  # noqa: E402
from minibot import sfx  # noqa: E402
from minibot.voice import Narrator  # noqa: E402

OUT = '/opt/qantcore/minibot/output/reviews'
WORK = '/opt/qantcore/htmlvid/llama3'
FPS = 30
ACC, ACC2 = '#FFB347', '#8BE8FF'

n = Narrator(speaker='baya')
lines = [
    'Llama 3.3 запускается локально одной командой: ollama pull, и модель уже работает.',
    'Восемь миллиардов параметров весят около пяти гигабайт, семьдесят миллиардов — сорок.',
    'Ollama поднимает REST API на порту одиннадцать четыре тридцать четыре.',
    'Контекст сто двадцать восемь тысяч токенов и function calling для агента.',
    'Open WebUI даёт интерфейс как у ChatGPT, а vLLM — сервер под нагрузку.',
    'Подробнее на сайте qantcore.space.',
]
cues = [n.add(x) for x in lines]
dur = cues[-1][1] + 2.6

CSS = f"""
@font-face {{ font-family:'Manrope'; src:url('fonts/Manrope.ttf'); font-weight:200 800; }}
@font-face {{ font-family:'JBMono'; src:url('fonts/JetBrainsMono.ttf'); font-weight:100 800; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:#0C0A07; }}
body {{ font-family:'Manrope','DejaVu Sans',sans-serif; color:#FFF8EE; }}
#stage {{ position:relative; width:1080px; height:1920px; overflow:hidden;
  background:
    radial-gradient(760px 760px at 84% 6%, rgba(255,179,71,.26), transparent 62%),
    radial-gradient(700px 700px at 6% 30%, rgba(139,232,255,.16), transparent 60%),
    radial-gradient(900px 900px at 50% 108%, rgba(255,140,90,.16), transparent 62%),
    linear-gradient(180deg,#120E08 0%,#0A0806 100%); }}
#grain {{ position:absolute; inset:-40px; opacity:.05; pointer-events:none; z-index:8;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>"); }}
header {{ position:absolute; top:74px; left:76px; right:76px; display:flex; align-items:center; gap:18px; z-index:5; }}
.logo {{ width:72px; height:72px; border-radius:20px; background:linear-gradient(140deg,{ACC},#C2410C);
  display:flex; align-items:center; justify-content:center; color:#1A0F05; font-weight:800; font-size:24px; }}
.brand {{ font-size:31px; font-weight:800; }}
.kick {{ margin-left:auto; font-size:19px; letter-spacing:3px; color:rgba(255,255,255,.45);
  text-transform:uppercase; text-align:right; line-height:1.5; }}
h1 {{ position:absolute; top:178px; left:72px; right:72px; font-size:86px; font-weight:800; line-height:.96;
  letter-spacing:-1.8px; z-index:5;
  background:linear-gradient(115deg,#FFFFFF 30%,{ACC} 92%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.tabs {{ position:absolute; top:378px; left:76px; right:76px; display:flex; gap:30px; z-index:5;
  border-bottom:2px solid rgba(255,255,255,.10); padding-bottom:13px; }}
.tab {{ font-size:20px; letter-spacing:3.2px; text-transform:uppercase; color:rgba(255,255,255,.32); font-weight:700; }}
.tab.on {{ color:#fff; }}
#tabline {{ position:absolute; height:3px; bottom:-2px; background:linear-gradient(90deg,{ACC},{ACC2}); }}
.blk {{ position:absolute; left:76px; right:76px; z-index:4; }}
.lbl {{ font-size:21px; letter-spacing:4px; text-transform:uppercase; color:{ACC}; font-weight:700; margin-bottom:16px; }}
.num {{ font-family:'JBMono',monospace; font-weight:800; font-size:180px; line-height:.92;
  letter-spacing:-7px; text-shadow:0 0 46px rgba(255,179,71,.45); }}
.unit {{ font-size:34px; color:rgba(255,255,255,.82); margin-top:10px; }}
.card {{ background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.11);
  border-radius:26px; padding:26px 30px; box-shadow:0 22px 56px rgba(0,0,0,.4); }}
.row {{ display:flex; gap:18px; }}
.row .card {{ flex:1; }}
.k {{ font-size:19px; letter-spacing:3px; text-transform:uppercase; color:{ACC2}; margin-bottom:10px; }}
.v {{ font-family:'JBMono',monospace; font-size:44px; color:#fff; }}
.s {{ font-size:22px; color:rgba(255,255,255,.62); margin-top:6px; }}
.pipe {{ display:flex; align-items:center; gap:14px; }}
.node {{ flex:1; text-align:center; }}
.node .ico {{ width:84px; height:84px; margin:0 auto 12px; border-radius:22px; display:flex; align-items:center;
  justify-content:center; font-size:30px; font-weight:800; background:rgba(255,255,255,.07);
  border:1px solid rgba(255,255,255,.14); }}
.node .t {{ font-size:23px; font-weight:700; }}
.node .d {{ font-size:18px; color:rgba(255,255,255,.55); margin-top:4px; }}
.arr {{ color:{ACC}; font-size:26px; }}
.chips {{ display:flex; flex-wrap:wrap; gap:14px; }}
.chip {{ padding:16px 22px; border-radius:18px; background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.12); font-size:24px; font-weight:700; }}
#finale {{ position:absolute; inset:0; z-index:6; background:rgba(8,6,4,.96);
  display:flex; flex-direction:column; align-items:center; padding-top:330px; }}
#qr {{ width:320px; height:320px; border-radius:26px; background:#fff; padding:18px; }}
#url {{ margin-top:50px; font-size:86px; font-weight:800; letter-spacing:-2px;
  background:linear-gradient(115deg,#FFFFFF,{ACC}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
#cta {{ position:absolute; bottom:300px; left:0; right:0; text-align:center; font-size:32px; color:rgba(255,255,255,.7); }}
#cap {{ position:absolute; left:70px; right:70px; bottom:520px; text-align:center; z-index:5;
  font-size:40px; font-weight:700; line-height:1.3; text-shadow:0 4px 22px rgba(0,0,0,.85); }}
#crow {{ position:absolute; bottom:44px; left:0; width:1080px; height:380px; z-index:7;
  filter:drop-shadow(0 10px 40px rgba(255,179,71,.28));
  display:flex; justify-content:center; align-items:flex-end; }}
#crowFlip {{ transform-origin:center bottom; }}
"""

CROW_SVG = """
<svg viewBox="0 0 320 300" width="372" height="350">
  <g id="crowBody" fill="#1B1712" stroke="#4A3F32" stroke-width="3.5">
    <path d="M60 190 q-6 -70 52 -96 q26 -12 52 -4 q10 -18 26 -22 l4 26 q26 6 34 30 l-34 4 q10 34 -10 66 q-24 38 -74 34 q-40 -4 -50 -38z"/>
    <path d="M226 86 l64 -10 l-58 40z"/>
    <path d="M60 190 l-46 40 l60 -4 l-8 24 l40 -26z"/>
  </g>
  <circle cx="196" cy="86" r="6" fill="#FFF8EE"/>
  <circle cx="197" cy="87" r="2.6" fill="#0B0A08"/>
  <g id="brain" transform="translate(196,26)">
    <ellipse cx="0" cy="0" rx="46" ry="34" fill="#FF7EB3" stroke="#C2185B" stroke-width="3"/>
    <path d="M-34 -6 q10 -18 22 -6 q6 -14 18 -4 q10 -12 20 2" fill="none" stroke="#C2185B" stroke-width="3.4" stroke-linecap="round"/>
    <path d="M-30 14 q12 10 22 0 q10 10 22 0 q10 10 18 -2" fill="none" stroke="#C2185B" stroke-width="3" stroke-linecap="round"/>
    <circle cx="46" cy="-26" r="4" fill="#FFE08A"/>
    <circle cx="-48" cy="-24" r="3" fill="#FFE08A"/>
  </g>
  <g id="legL" stroke="#15130F" stroke-width="9" stroke-linecap="round">
    <line x1="120" y1="228" x2="112" y2="286"/>
    <line x1="112" y1="286" x2="92" y2="292"/><line x1="112" y1="286" x2="116" y2="296"/>
  </g>
  <g id="legR" stroke="#15130F" stroke-width="9" stroke-linecap="round">
    <line x1="164" y1="228" x2="172" y2="286"/>
    <line x1="172" y1="286" x2="152" y2="292"/><line x1="172" y1="286" x2="176" y2="296"/>
  </g>
</svg>
"""

HTML = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="stage">
  <div id="grain"></div>
  <header><div class="logo">LL3</div><div class="brand">Qantcore</div>
    <div class="kick">ГАЙД · 2026<br>ЛОКАЛЬНЫЕ LLM</div></header>
  <h1>Llama 3<br>на своём железе</h1>
  <div class="tabs">
    <div class="tab" data-t="0">Размер</div><div class="tab" data-t="1">Железо</div>
    <div class="tab" data-t="2">Запуск</div><div class="tab" data-t="3">Агент</div><div class="tab" data-t="4">Оболочки</div>
    <div id="tabline"></div>
  </div>

  <div class="blk" id="s1" style="top:470px">
    <div class="lbl">Одна команда</div>
    <div class="num" id="big">0</div>
    <div class="unit">гигабайт — модель 8B в GGUF, запуск за пять минут</div>
    <div class="card" style="margin-top:30px; font-family:'JBMono',monospace; font-size:28px; color:#FFE9CC">
      ollama pull llama3.3:8b</div>
  </div>

  <div class="blk" id="s2" style="top:470px">
    <div class="lbl">Сколько весит</div>
    <div class="row">
      <div class="card"><div class="k">8B</div><div class="v">4,7 ГБ</div><div class="s">ноутбук, 8–12 ГБ VRAM</div></div>
      <div class="card"><div class="k">70B</div><div class="v">~40 ГБ</div><div class="s">Q4_K_M, серверная карта</div></div>
    </div>
    <div class="unit" style="margin-top:26px">Ollama сама подбирает квантование под железо</div>
  </div>

  <div class="blk" id="s3" style="top:470px">
    <div class="lbl">Куда стучится</div>
    <div class="card pipe">
      <div class="node"><div class="ico">◍</div><div class="t">Ollama</div><div class="d">локально</div></div>
      <div class="arr">→</div>
      <div class="node"><div class="ico">11434</div><div class="t">REST API</div><div class="d">/api/generate</div></div>
      <div class="arr">→</div>
      <div class="node"><div class="ico">▤</div><div class="t">WebUI</div><div class="d">или llama.cpp</div></div>
    </div>
    <div class="unit" style="margin-top:26px">OpenAI-совместимый эндпоинт — любой клиент подключается</div>
  </div>

  <div class="blk" id="s4" style="top:470px">
    <div class="lbl">Что умеет</div>
    <div class="chips">
      <div class="chip">128K контекст</div><div class="chip">function calling</div>
      <div class="chip">GGUF-кванты</div><div class="chip">CUDA · Metal</div>
      <div class="chip">без облака</div><div class="chip">Apache-2.0</div>
    </div>
    <div class="card" style="margin-top:28px; font-size:24px; color:rgba(255,255,255,.75)">
      агент получает инструменты: поиск, код, база данных — и вызывает их сам</div>
  </div>

  <div class="blk" id="s5" style="top:470px">
    <div class="lbl">Чем смотреть</div>
    <div class="card" style="padding:8px 30px">
      <div class="step" style="display:flex;justify-content:space-between;padding:20px 0;border-bottom:1px solid rgba(255,255,255,.08)">
        <div style="font-size:30px;font-weight:700">Open WebUI</div><div style="font-size:22px;color:rgba(255,255,255,.6)">интерфейс как у ChatGPT</div></div>
      <div class="step" style="display:flex;justify-content:space-between;padding:20px 0;border-bottom:1px solid rgba(255,255,255,.08)">
        <div style="font-size:30px;font-weight:700">llama.cpp</div><div style="font-size:22px;color:rgba(255,255,255,.6)">максимум скорости, GGUF</div></div>
      <div class="step" style="display:flex;justify-content:space-between;padding:20px 0">
        <div style="font-size:30px;font-weight:700">vLLM</div><div style="font-size:22px;color:rgba(255,255,255,.6)">сервер под нагрузку</div></div>
    </div>
    <div class="unit" style="margin-top:26px">модель одна — оболочки разные</div>
  </div>

  <div id="finale">
    <img id="qr" src="qr.png">
    <div id="url">qantcore.space</div>
    <div id="cta">гайд по Llama 3 → развернуть локально</div>
  </div>
  <div id="crow"><div id="crowFlip">{CROW_SVG}</div></div>
  <div id="cap"></div>
</div>
<script>
const CUE = {json.dumps([[c[0], c[1]] for c in cues])};
const CAPS = {json.dumps([[cues[0][0], cues[0][1], '4,7 ГБ и одна команда'],
                          [cues[1][0], cues[1][1], '8B весит 4,7 ГБ, 70B — 40 ГБ'],
                          [cues[2][0], cues[2][1], 'REST API на 11434'],
                          [cues[3][0], cues[3][1], '128K контекста и function calling'],
                          [cues[4][0], cues[4][1], 'Open WebUI, llama.cpp или vLLM'],
                          [cues[5][0], cues[5][1], 'Подробнее на сайте']], ensure_ascii=False)};
const DUR = {dur:.2f};
let T = parseFloat(new URLSearchParams(location.search).get('t') || '0');

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
  const s1 = CUE[0][0], s2 = CUE[1][0], s3 = CUE[2][0], s4 = CUE[3][0], s5 = CUE[4][0], s6 = CUE[5][0];
  fade(document.getElementById('s1'), s1, s2);
  fade(document.getElementById('s2'), s2, s3);
  fade(document.getElementById('s3'), s3, s4);
  fade(document.getElementById('s4'), s4, s5);
  fade(document.getElementById('s5'), s5, s6);

  const ck = Math.min(1, Math.max(0, (T - s1 - 0.15) / 1.3));
  document.getElementById('big').textContent = (4.7 * (1 - Math.pow(1 - ck, 4))).toFixed(1).replace('.', ',');

  const idx = T >= s6 ? 5 : T >= s5 ? 4 : T >= s4 ? 3 : T >= s3 ? 2 : T >= s2 ? 1 : 0;
  const tabs = [...document.querySelectorAll('.tab')];
  const ti = Math.min(idx, tabs.length - 1);
  tabs.forEach((el, i) => el.classList.toggle('on', i === ti));
  const act = tabs[ti].getBoundingClientRect();
  const box = document.querySelector('.tabs').getBoundingClientRect();
  const line = document.getElementById('tabline');
  line.style.left = (act.left - box.left) + 'px';
  line.style.width = act.width + 'px';

  // ворона ходит влево-вправо
  const crow = document.getElementById('crow');
  const phase = T * 0.55;
  const x = 540 + 300 * Math.sin(phase);
  const dir = Math.cos(phase) >= 0 ? 1 : -1;
  const bob = Math.abs(Math.sin(T * 7)) * 7;
  crow.style.transform = 'translateX(' + (x - 540).toFixed(1) + 'px) translateY(' + (-bob).toFixed(1) + 'px)';
  document.getElementById('crowFlip').style.transform = 'scaleX(' + dir + ')';
  const swing = Math.sin(T * 7) * 14;
  document.getElementById('legL').setAttribute('transform', 'rotate(' + swing.toFixed(1) + ' 120 228)');
  document.getElementById('legR').setAttribute('transform', 'rotate(' + (-swing).toFixed(1) + ' 164 228)');
  const fl = 1 + 0.05 * Math.sin(T * 3.1);
  document.getElementById('brain').setAttribute('transform', 'translate(196,26) scale(' + fl.toFixed(3) + ')');

  const fk = Math.min(1, Math.max(0, (T - s6) / 0.5));
  const fin = document.getElementById('finale');
  fin.style.opacity = fk.toFixed(3);
  document.querySelectorAll('header, h1, .tabs').forEach(el => {{ if (fk > 0.5) el.style.visibility = 'hidden'; }});
  crow.style.opacity = (1 - fk).toFixed(3);

  const cap = document.getElementById('cap');
  const a = CAPS.find(c => T >= c[0] && T <= c[1] && T < s6);
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
    for t in (2.0, 7.0, 13.0, 18.0, 21.0, 25.0):
        render._shot((int(t * 100), t, html, WORK))
        os.replace(os.path.join(WORK, f'{int(t * 100):05d}.png'), os.path.join(WORK, f'p{t}.png'))
    print('preview', round(dur, 2), 'cues', [round(c[0], 2) for c in cues])
    sys.exit(0)

frames, count = render.render_frames_cdp(html, os.path.join(WORK, 'frames'), dur, FPS, port=9345)
voice = os.path.join(OUT, 'llama3.wav')
n.write(voice)
bed = sfx.build(dur, cue_starts=[c[0] for c in cues], pings=[cues[0][0] + 0.2],
                out=os.path.join(OUT, 'llama3-bed.wav'))
mixed = sfx.mix(voice, bed, os.path.join(OUT, 'llama3-mix.wav'))
render.encode(frames, mixed, os.path.join(OUT, 'llama3.mp4'), fps=FPS)

def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')

caps = ['4,7 ГБ и одна команда', '8B весит 4,7 ГБ, 70B — 40 ГБ', 'REST API на 11434',
        '128K контекста и function calling', 'Open WebUI, llama.cpp или vLLM',
        'Подробнее на qantcore.space']
with open(os.path.join(OUT, 'llama3.srt'), 'w', encoding='utf-8') as f:
    for i, ((a, b), c) in enumerate(zip(cues, caps), 1):
        f.write(f'{i}\n{ts(a)} --> {ts(b)}\n{c}\n\n')
n.cleanup()
print('=== llama3', round(dur, 2))
