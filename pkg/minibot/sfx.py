"""Звуковой дизайн: тихая подложка, whoosh на смене сцены, пинг на цифре."""
import wave

import numpy as np

SR = 44100


def _fade(x, ms=250):
    n = int(SR * ms / 1000)
    if len(x) < 2 * n:
        return x
    ramp = np.linspace(0, 1, n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return x


def _lowpass(x, cutoff=900.0):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = a * acc + (1 - a) * v
        y[i] = acc
    return y


def build(duration, cue_starts=(), pings=(), out='bed.wav', bed_level=0.035):
    n = int(SR * duration)
    t = np.arange(n) / SR

    # подложка: три низких тона с медленным дыханием
    lfo = 0.55 + 0.45 * np.sin(2 * np.pi * 0.06 * t)
    pad = (0.5 * np.sin(2 * np.pi * 110 * t) +
           0.32 * np.sin(2 * np.pi * 164.81 * t) +
           0.18 * np.sin(2 * np.pi * 220 * t))
    pad = _lowpass(pad, 700) * lfo * bed_level

    mix = pad

    # whoosh на смене сцены
    rng = np.random.default_rng(7)
    for c in cue_starts:
        ln = int(SR * 0.42)
        idx = int(c * SR)
        if idx < 0 or idx + ln > n:
            continue
        env = np.exp(-np.linspace(0, 6, ln))
        noise = rng.normal(0, 1, ln)
        swipe = noise - _lowpass(noise, 2000)
        mix[idx:idx + ln] += swipe * env * 0.05

    # пинг на появление цифры
    for c in pings:
        ln = int(SR * 0.55)
        idx = int(c * SR)
        if idx < 0 or idx + ln > n:
            continue
        tt = np.arange(ln) / SR
        env = np.exp(-tt * 9)
        tone = (np.sin(2 * np.pi * 1568 * tt) * 0.6 + np.sin(2 * np.pi * 2093 * tt) * 0.4)
        mix[idx:idx + ln] += tone * env * 0.05

    mix = _fade(mix, 300)
    pcm = np.clip(mix, -1, 1)
    pcm = (pcm * 32767).astype('<i2')

    with wave.open(out, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out


def mix(voice_path, bed_path, out_path):
    """Складывает голос и подложку без потери громкости (amix режет вдвое)."""
    def rd(p):
        w = wave.open(p)
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        return a, w.getframerate(), w.getnchannels()

    v, sr, ch = rd(voice_path)
    b, _, _ = rd(bed_path)
    n = max(len(v), len(b))
    mix = np.zeros(n, dtype=np.float32)
    mix[:len(v)] += v
    mix[:len(b)] += b
    peak = float(np.abs(mix).max())
    if peak > 0.95:
        mix *= 0.95 / peak
    pcm = (np.clip(mix, -1, 1) * 32767).astype('<i2')
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return out_path
