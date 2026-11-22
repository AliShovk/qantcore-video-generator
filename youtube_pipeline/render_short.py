#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render video_spec.json using Qantcore's existing HTML/Chrome, TTS and FFmpeg stack."""
from __future__ import annotations
import argparse, base64, html, json, os, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pkg"))
sys.path.insert(0, str(ROOT / "pkg" / "rendering"))
import render
from minibot import sfx
from minibot.voice import Narrator


def esc(value):
    return html.escape(str(value or ""), quote=True)


def slugify(value):
    return re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", value.lower()).strip("-")[:60] or "short"


def validate(spec):
    errors = []
    scenes = spec.get("scenes")
    if not isinstance(scenes, list) or not 2 <= len(scenes) <= 10:
        errors.append("scenes must be a list containing 2–10 scenes")
        return errors
    for i, scene in enumerate(scenes, 1):
        if not isinstance(scene, dict) or not str(scene.get("voiceover", "")).strip():
            errors.append("scene %s has no voiceover" % i)
        visual = (scene or {}).get("visual") or {}
        if visual.get("type", "text") not in ("text", "stat", "steps", "comparison", "diagram"):
            errors.append("scene %s has unsupported visual.type" % i)
    return errors


def block_html(scene):
    v = scene.get("visual") or {}
    kind = v.get("type", "text")
    eyebrow = esc(v.get("eyebrow") or "YOUTUBE SHORTS")
    if kind == "stat":
        return '<div class="label">%s</div><div class="card"><div class="big">%s</div><div class="note">%s</div></div>' % (
            eyebrow, esc(v.get("value") or v.get("headline")), esc(v.get("label") or v.get("body")))
    if kind in ("steps", "diagram"):
        items = v.get("items") or []
        rows = []
        for item in items[:5]:
            if isinstance(item, dict):
                title, sub = esc(item.get("title")), esc(item.get("sub"))
            else:
                title, sub = esc(item), ""
            rows.append('<div class="item"><b>%s</b><small>%s</small></div>' % (title, sub))
        return '<div class="label">%s</div><div class="card">%s</div>' % (eyebrow, "".join(rows))
    if kind == "comparison":
        left, right = v.get("left") or {}, v.get("right") or {}
        return ('<div class="label">%s</div><div class="card compare">'
                '<div><b>%s</b><small>%s</small></div><div><b>%s</b><small>%s</small></div></div>') % (
            eyebrow, esc(left.get("value")), esc(left.get("label")),
            esc(right.get("value")), esc(right.get("label")))
    return '<div class="label">%s</div><div class="card"><h2>%s</h2><p>%s</p></div>' % (
        eyebrow, esc(v.get("headline") or scene.get("on_screen_text")), esc(v.get("body")))


def make_srt(cues):
    def stamp(t):
        ms = int(round(t * 1000))
        h, rem = divmod(ms, 3600000)
        m, rem = divmod(rem, 60000)
        s, ms = divmod(rem, 1000)
        return "%02d:%02d:%02d,%03d" % (h, m, s, ms)
    return "\n\n".join("%d\n%s --> %s\n%s" % (i, stamp(c["start"]), stamp(c["end"]), c["text"])
                       for i, c in enumerate(cues, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out-dir")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--port", type=int, default=9367)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    spec_path = Path(args.spec).expanduser().resolve()
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("Cannot read spec: %s" % exc, file=sys.stderr)
        return 2
    errors = validate(spec)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2

    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome or not shutil.which("ffmpeg"):
        print("Chrome/Chromium and ffmpeg are required.", file=sys.stderr)
        return 3
    render.CHROME = chrome

    title = str(spec.get("title") or "Qantcore Short")
    slug = slugify(str(spec.get("id") or title))
    out = Path(args.out_dir).expanduser().resolve() if args.out_dir else ROOT / "output" / "youtube_shorts" / slug
    out.mkdir(parents=True, exist_ok=True)

    voice = spec.get("voice") or {}
    narrator = Narrator(
        backend=voice.get("backend", "silero"),
        speaker=voice.get("speaker", "eugene"),
        gap=float(voice.get("gap", 0.18)),
        lead=0.25
    )
    try:
        cues = [narrator.add(str(s["voiceover"]).strip()) for s in spec["scenes"]]
        speech_end = cues[-1][1]
        duration = speech_end + float(spec.get("outro_seconds", 2.2))
        max_duration = float(spec.get("max_duration_seconds", 60))
        min_duration = float(spec.get("min_duration_seconds", 0))
        if duration > max_duration:
            raise ValueError("TTS duration %.1fs exceeds maximum %.1fs; shorten script." % (duration, max_duration))
        if min_duration and duration < min_duration:
            print("WARNING: TTS duration %.1fs is below requested minimum %.1fs." % (duration, min_duration))

        voice_path, bed_path, mix_path = out / "voice.wav", out / "bed.wav", out / "mix.wav"
        narrator.write(str(voice_path))
        sfx.build(duration, cue_starts=[c[0] for c in cues[1:]],
                  pings=[cues[i][0] for i, s in enumerate(spec["scenes"])
                         if (s.get("visual") or {}).get("type") == "stat"],
                  out=str(bed_path), bed_level=float(spec.get("bed_level", 0.025)))
        sfx.mix(str(voice_path), str(bed_path), str(mix_path))

        css = """
@font-face{font-family:Manrope;src:url('fonts/Manrope.ttf')}
*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#f7f7f3;color:#15191f;font-family:Manrope,Arial,sans-serif}
#stage{position:relative;width:1080px;height:1920px;padding:100px 76px;background:linear-gradient(150deg,#fff 0%,#f1f3ef 100%)}
header{font-size:28px;font-weight:800;color:#0e9f8a;letter-spacing:3px}
h1{font-size:78px;line-height:1.02;margin:100px 0 60px;font-weight:800;letter-spacing:-2px}
.block{position:absolute;left:76px;right:76px;top:570px}
.label{font-size:23px;letter-spacing:4px;color:#0e9f8a;font-weight:800;margin-bottom:24px}
.card{border:2px solid #dce4df;background:#fff;border-radius:32px;padding:44px;box-shadow:0 22px 60px #15221a12}
.card h2{font-size:58px;line-height:1.08;margin:0 0 25px}.card p{font-size:34px;line-height:1.35;color:#53615b}
.big{font-size:170px;font-weight:800;color:#0e9f8a}.note{font-size:34px;color:#53615b;margin-top:22px}
.item{padding:25px 0;border-bottom:1px solid #e5ebe7;font-size:36px}.item:last-child{border:0}.item small{display:block;font-size:24px;color:#68756e;margin-top:8px}
.compare{display:flex;gap:25px}.compare>div{flex:1}.compare b{display:block;font-size:52px}.compare small{font-size:24px;color:#68756e}
#caption{position:absolute;left:70px;right:70px;bottom:240px;text-align:center;font-size:38px;font-weight:800;line-height:1.25}
#outro{position:absolute;inset:0;background:#fff;display:flex;align-items:center;justify-content:center;flex-direction:column;opacity:0}
#outro b{font-size:92px;color:#0e9f8a}#outro small{font-size:30px;color:#64736a;margin-top:24px}
#progress{position:absolute;top:0;left:0;height:8px;background:#0e9f8a}
"""
        blocks, caps = [], []
        for i, (scene, cue) in enumerate(zip(spec["scenes"], cues)):
            start, end = float(cue[0]), float(cue[1])
            next_start = float(cues[i+1][0]) if i+1 < len(cues) else speech_end
            blocks.append('<div class="block" id="b%d">%s</div>' % (i, block_html(scene)))
            caps.append([start, end, " ".join(str(scene.get("on_screen_text") or scene["voiceover"]).split())[:90]])
        js_data = json.dumps({"cues": [[float(c[0]), float(c[1])] for c in cues],
                              "caps": caps, "outro": speech_end, "duration": duration},
                             ensure_ascii=False)
        js = """
const D=__DATA__;
function frame(t){
 let active=-1;
 D.cues.forEach((c,i)=>{const el=document.getElementById('b'+i);const on=t>=c[0]&&t<D.cues[i+1]?.[0]|| (i===D.cues.length-1&&t<D.outro);el.style.opacity=on?'1':'0';el.style.visibility=on?'visible':'hidden';if(on)active=i;});
 const cap=D.caps[active];document.getElementById('caption').textContent=cap?cap[2]:'';
 const k=Math.max(0,Math.min(1,(t-D.outro)/0.35));document.getElementById('outro').style.opacity=k;
 document.getElementById('progress').style.width=(Math.min(1,t/D.duration)*100)+'%';
}
window.applyFrame=frame;frame(0);
"""
        scene_html = ('<!doctype html><html lang="ru"><meta charset="utf-8"><style>' + css +
                      '</style><body><div id="stage"><header>QANTCORE · SHORTS</header><h1>' +
                      esc(title) + '</h1>' + "".join(blocks) +
                      '<div id="caption"></div><div id="outro"><b>' +
                      esc(spec.get("outro_brand", "Qantcore")) + '</b><small>' +
                      esc(spec.get("outro_text", "короткие видео и эксперименты")) +
                      '</small></div><div id="progress"></div></div><script>' +
                      js.replace("__DATA__", js_data) + '</script></body></html>')
        html_path = out / "scene.html"
        html_path.write_text(scene_html, encoding="utf-8")
        if args.dry_run:
            print(json.dumps({"title": title, "speech_seconds": round(speech_end, 2),
                              "duration_seconds": round(duration, 2), "out_dir": str(out)}, ensure_ascii=False, indent=2))
            return 0
        frames = out / "frames"
        render.render_frames_cdp(str(html_path), str(frames), duration, fps=args.fps, port=args.port)
        mp4 = out / (slug + ".mp4")
        render.encode(str(frames), str(mix_path), str(mp4), fps=args.fps, ext="jpg")
        srt = out / (slug + ".srt")
        srt.write_text(make_srt(narrator.cues), encoding="utf-8")
        manifest = {"id": slug, "title": title, "video_path": str(mp4), "subtitle_path": str(srt),
                    "duration_seconds": round(duration, 3), "resolution": "1080x1920",
                    "fps": args.fps, "published": False, "renderer": "qantcore-htmlvid"}
        (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print("Render failed: %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1
    finally:
        narrator.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
