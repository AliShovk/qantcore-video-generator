#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML→кадры через headless Chrome + наложение бота PIL + сборка MP4."""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, '/opt/qantcore/minibot')

CHROME = '/usr/local/bin/google-chrome'
W, H = 1080, 1920

CSS = """
@font-face { font-family: 'Manrope'; src: url('fonts/Manrope.ttf'); font-weight: 200 800; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #070A12; }
body { font-family: 'Manrope', 'DejaVu Sans', sans-serif; color: #F2F6FF; }
#stage { position: relative; width: 1080px; height: 1920px; overflow: hidden;
  background:
    radial-gradient(720px 720px at 82% 8%, rgba(120,90,255,.22), transparent 65%),
    radial-gradient(680px 680px at 10% 22%, rgba(0,200,255,.18), transparent 62%),
    radial-gradient(900px 900px at 50% 105%, rgba(255,110,180,.16), transparent 60%),
    linear-gradient(180deg, #080B14 0%, #06080F 100%); }
#grid { position: absolute; inset: 0; opacity: .5;
  background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
  background-size: 72px 72px; }
#prog { position: absolute; top: 0; left: 0; height: 6px; width: 0;
  background: linear-gradient(90deg, %ACC%, %ACC2%); z-index: 9; }
header { position: absolute; top: 84px; left: 76px; right: 76px; display: flex;
  align-items: center; gap: 20px; }
.logo { width: 74px; height: 74px; border-radius: 22px; background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.12); display: flex; align-items: center;
  justify-content: center; }
.logo img { width: 38px; height: 42px; filter: invert(1) brightness(1.1); }
.brand { font-size: 34px; font-weight: 800; letter-spacing: .5px; }
.kick { margin-left: auto; font-size: 20px; letter-spacing: 3.2px; color: rgba(255,255,255,.5);
  text-transform: uppercase; text-align: right; line-height: 1.5; }
h1 { position: absolute; top: 196px; left: 76px; right: 76px; font-size: 86px;
  font-weight: 800; line-height: .96; letter-spacing: -1.5px;
  background: linear-gradient(120deg, #FFFFFF 25%, %ACC2% 90%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.block { position: absolute; left: 76px; right: 76px; }
.label { font-size: 22px; letter-spacing: 4px; text-transform: uppercase; color: %ACC%;
  font-weight: 700; margin-bottom: 22px; }
.card { background: rgba(255,255,255,.055); border: 1px solid rgba(255,255,255,.10);
  border-radius: 30px; padding: 34px 36px; backdrop-filter: blur(6px);
  box-shadow: 0 24px 60px rgba(0,0,0,.35); }
.big { font-size: 118px; font-weight: 800; line-height: 1; letter-spacing: -2px; }
.chips { display: flex; flex-direction: column; gap: 18px; }
.chip { display: flex; align-items: center; gap: 22px; font-size: 40px; font-weight: 700; }
.dot { width: 16px; height: 16px; border-radius: 50%; background: %ACC%;
  box-shadow: 0 0 22px %ACC%; }
.chip span.sub { font-size: 24px; font-weight: 500; color: rgba(255,255,255,.55); margin-left: auto; }
.prices { display: flex; gap: 22px; }
.price { flex: 1; }
.price .val { font-size: 84px; font-weight: 800; letter-spacing: -2px; }
.price .nm { font-size: 24px; color: rgba(255,255,255,.6); margin-top: 6px; }
.strike { position: relative; display: inline-block; }
.strike:after { content: ''; position: absolute; left: -6px; right: -6px; top: 52%;
  height: 10px; background: #FF5E7A; border-radius: 6px; transform: rotate(-3deg); }
.note { font-size: 28px; color: rgba(255,255,255,.62); margin-top: 18px; line-height: 1.4; }
#finale { position: absolute; inset: 0; background: rgba(5,7,13,.95); display: flex;
  flex-direction: column; align-items: center; justify-content: flex-start; padding-top: 470px; }
#finale .url { font-size: 96px; font-weight: 800; letter-spacing: -2px;
  background: linear-gradient(120deg, #FFFFFF, %ACC2%); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; }
#finale .sub { margin-top: 26px; font-size: 30px; color: rgba(255,255,255,.6); }
#cap { position: absolute; left: 70px; right: 70px; bottom: 96px; text-align: center;
  font-size: 42px; font-weight: 700; line-height: 1.32; text-shadow: 0 4px 24px rgba(0,0,0,.8); }
"""

HTML = """<!doctype html><html lang="ru"><head><meta charset="utf-8">
<style>%CSS%</style></head><body>
<div id="stage">
  <div id="grid"></div>
  <div id="prog"></div>
  <header>
    <div class="logo"><img src="%LOGO%"></div>
    <div class="brand">%BRAND%</div>
    <div class="kick">%KICK%</div>
  </header>
  <h1>%TITLE%</h1>
  %BLOCKS%
  <div id="finale"><div class="url">qantcore.space</div><div class="sub">%SUBTITLE%</div></div>
  <div id="cap"></div>
</div>
<script>
const CUE = %CUE%;
const CAPS = %CAPS%;
const DUR = %DUR%;
let T = parseFloat(new URLSearchParams(location.search).get('t') || '0');
const FADE = 0.28;

function vis(el, a, b) {
  const inK = Math.min(1, Math.max(0, (T - a) / FADE));
  const outK = Math.min(1, Math.max(0, (b - T) / FADE));
  const k = Math.min(inK, outK);
  el.style.opacity = k.toFixed(3);
  el.style.transform = 'translateY(' + ((1 - inK) * 28).toFixed(1) + 'px)';
  el.style.visibility = k <= 0.001 ? 'hidden' : 'visible';
}

function drawFinale() {
  const F = CUE[CUE.length - 1];
  const fK = Math.min(1, Math.max(0, (T - F[0]) / 0.45));
  const fin = document.getElementById('finale');
  fin.style.opacity = fK.toFixed(3);
  fin.style.transform = 'scale(' + (1.02 - 0.02 * fK).toFixed(3) + ')';
  document.querySelectorAll('header, h1, .block').forEach(el => {
    if (fK > 0.55) el.style.visibility = 'hidden';
  });
}

function drawCaption() {
  const F = CUE[CUE.length - 1];
  const cap = document.getElementById('cap');
  const active = CAPS.find(c => T >= c[0] && T <= c[1] && T < F[0]);
  if (!active) { cap.style.opacity = '0'; return; }
  cap.textContent = active[2];
  const k = Math.min(1, (T - active[0]) / 0.2, (active[1] - T) / 0.2);
  cap.style.opacity = Math.max(0, Math.min(1, k)).toFixed(3);
}

function applyFrame(t) {
  T = t;
  document.querySelectorAll('[data-in]').forEach(el => {
    vis(el, parseFloat(el.dataset.in), parseFloat(el.dataset.out));
  });
  drawFinale();
  drawCaption();
  document.getElementById('prog').style.width = (Math.min(1, T / DUR) * 100).toFixed(2) + '%';
}

window.applyFrame = applyFrame;
applyFrame(T);
</script></body></html>"""


def build_html(spec, path):
    css = CSS.replace('%ACC%', spec['accent']).replace('%ACC2%', spec['accent2'])
    blocks = []
    for b in spec['blocks']:
        blocks.append(
            f'<div class="block" data-in="{b["in"]}" data-out="{b["out"]}" style="top:{b["top"]}px">{b["html"]}</div>')
    html = (HTML.replace('%CSS%', css)
                .replace('%LOGO%', spec['logo'])
                .replace('%BRAND%', spec['brand'])
                .replace('%KICK%', spec['kick'].replace('\n', '<br>'))
                .replace('%TITLE%', spec['title'])
                .replace('%BLOCKS%', '\n'.join(blocks))
                .replace('%SUBTITLE%', spec['subtitle'])
                .replace('%CUE%', json.dumps(spec['cues']))
                .replace('%CAPS%', json.dumps(spec['caps'], ensure_ascii=False))
                .replace('%DUR%', str(spec['duration'])))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return path


def _shot(args):
    idx, t, html, out_dir = args
    out = os.path.join(out_dir, f'{idx:05d}.png')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--hide-scrollbars', '--force-device-scale-factor=1',
                    f'--window-size={W},{H}', '--virtual-time-budget=600',
                    f'--screenshot={out}', f'file://{html}?t={t:.3f}'],
                   capture_output=True)
    return out


def render_frames(html, out_dir, duration, fps=30, workers=4):
    os.makedirs(out_dir, exist_ok=True)
    n = int(round(duration * fps))
    jobs = [(i, i / fps, html, out_dir) for i in range(n)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(_shot, jobs))
    return out_dir, n


def encode(frames_dir, audio, out_mp4, fps=30, ext='jpg'):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(fps),
                    '-i', os.path.join(frames_dir, f'%05d.{ext}'), '-i', audio,
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                    '-shortest', out_mp4], check=True)
    return out_mp4


async def _cdp_render(html, out_dir, duration, fps, port):
    import asyncio
    import base64
    import json as _json
    import urllib.request

    import websockets

    n = int(round(duration * fps))
    os.makedirs(out_dir, exist_ok=True)
    proc = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                             '--hide-scrollbars', f'--remote-debugging-port={port}',
                             f'--window-size={W},{H}', 'about:blank'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(80):
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/json/version', timeout=0.5)
                break
            except Exception:
                await asyncio.sleep(0.15)
        req = urllib.request.Request(f'http://127.0.0.1:{port}/json/new?file://{html}', method='PUT')
        target = _json.loads(urllib.request.urlopen(req, timeout=10).read())

        async with websockets.connect(target['webSocketDebuggerUrl'], max_size=None) as ws:
            ident = 0

            async def call(method, **params):
                nonlocal ident
                ident += 1
                await ws.send(_json.dumps({'id': ident, 'method': method, 'params': params}))
                while True:
                    msg = _json.loads(await ws.recv())
                    if msg.get('id') == ident:
                        return msg.get('result', {})

            await call('Page.enable')
            await call('Emulation.setDeviceMetricsOverride', width=W, height=H,
                       deviceScaleFactor=1, mobile=False)
            await call('Page.navigate', url=f'file://{html}')
            await asyncio.sleep(0.9)
            for i in range(n):
                t = i / fps
                await call('Runtime.evaluate', expression=f'window.applyFrame({t:.4f})')
                shot = await call('Page.captureScreenshot', format='jpeg', quality=90, fromSurface=True)
                with open(os.path.join(out_dir, f'{i:05d}.jpg'), 'wb') as f:
                    f.write(base64.b64decode(shot['data']))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
    return out_dir, n


def render_frames_cdp(html, out_dir, duration, fps=30, port=9333):
    import asyncio
    return asyncio.run(_cdp_render(html, out_dir, duration, fps, port))
