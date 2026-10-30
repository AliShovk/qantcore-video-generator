"""Озвучка через Piper: цельные фразы, точные тайминги, единая дорожка."""
import os
import shutil
import subprocess
import tempfile
import wave

import numpy as np

PIPER = shutil.which('piper') or '/usr/local/lib/hermes-agent/venv/bin/piper'
VOICES = '/root/piper-voices'
VOICE = os.path.join(VOICES, 'ru_RU-irina-medium.onnx')


def _dur(path):
    with wave.open(path) as w:
        return w.getnframes() / float(w.getframerate())


def _postprocess(path, max_pause=0.24, target_peak=0.85):
    """Сжимает внутренние паузы, срезает края и убирает клиппинг Piper."""
    with wave.open(path) as w:
        rate, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    mono = raw.reshape(-1, ch).mean(axis=1) if ch > 1 else raw.astype(np.float32)
    a = mono.astype(np.float32) / 32768
    win = max(1, int(0.02 * rate))
    n = len(a) // win
    if n < 4:
        return
    rms = np.array([np.sqrt((a[i * win:(i + 1) * win] ** 2).mean()) for i in range(n)])
    pk = float(np.abs(a).max()) or 1.0
    silent = rms < 0.06 * pk
    keep_win = np.ones(n, dtype=bool)
    max_win = max(1, int(max_pause / 0.02))
    i = 0
    while i < n:
        if silent[i]:
            j = i
            while j < n and silent[j]:
                j += 1
            if (j - i) > max_win:
                keep_win[i + max_win:j] = False
            i = j
        else:
            i += 1
    mask = np.repeat(keep_win, win)
    mask = np.pad(mask, (0, len(a) - len(mask)), constant_values=True)
    out = a[mask]
    # края
    idx = np.where(np.abs(out) > 0.02 * pk)[0]
    if len(idx):
        out = out[max(0, idx[0] - int(0.02 * rate)): idx[-1] + int(0.03 * rate)]
    out = out * min(1.0, target_peak / (np.abs(out).max() or 1.0))
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype('<i2').tobytes())


def _smooth(path, max_pause=0.14, thr=0.012):
    """Сжимает внутренние паузы: Piper держит по 0,4–0,9 с на запятых — это и слышно как заминки."""
    with wave.open(path) as w:
        rate, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).copy()
    if ch > 1:
        mono = raw.reshape(-1, ch).mean(axis=1).astype(np.int16)
    else:
        mono = raw
    a = mono.astype(np.float32) / 32768
    win = max(1, int(0.02 * rate))
    n = len(a) // win
    rms = np.array([np.sqrt((a[i * win:(i + 1) * win] ** 2).mean()) for i in range(n)])
    silent = rms < thr
    keep = np.ones(n, dtype=bool)
    max_win = int(max_pause / 0.02)
    i = 0
    while i < n:
        if silent[i]:
            j = i
            while j < n and silent[j]:
                j += 1
            if i > 0 and j < n and (j - i) > max_win:
                keep[i + max_win:j] = False
            i = j
        else:
            i += 1
    mask = np.repeat(keep, win)
    mask = np.pad(mask, (0, len(mono) - len(mask)), constant_values=True)
    out = mono[mask]
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(out.astype('<i2').tobytes())


def _trim(path):
    """Срезает тишину по краям: без неё фразы склеиваются без «заминок»."""
    out = path.replace('.wav', '-t.wav')
    af = ('silenceremove=start_periods=1:start_silence=0.02:start_threshold=-45dB,'
          'areverse,'
          'silenceremove=start_periods=1:start_silence=0.02:start_threshold=-45dB,'
          'areverse')
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', path, '-af', af, out],
                       capture_output=True)
    if r.returncode == 0 and os.path.exists(out) and _dur(out) > 0.2:
        os.replace(out, path)


_SILERO = {}


def _silero_model():
    if 'm' not in _SILERO:
        import torch
        torch.set_num_threads(4)
        m, _ = torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_tts',
                              language='ru', speaker='v4_ru', trust_repo=True)
        _SILERO['m'] = m
    return _SILERO['m']


class Narrator:
    """Собирает реплики по порядку и знает точные границы каждой."""

    def __init__(self, voice=VOICE, gap=0.28, lead=0.4, length_scale=0.95,
                 noise_scale=0.55, clause_gap=0.0, backend='silero', speaker='aidar'):
        self.voice, self.gap, self.lead = voice, gap, lead
        self.length_scale, self.noise_scale = length_scale, noise_scale
        self.backend, self.speaker = backend, speaker
        self.tmp = tempfile.mkdtemp(prefix='mb-vo-')
        self.cues = []
        self.t = lead

    def _say(self, text, path):
        if self.backend == 'silero':
            import soundfile as sf
            audio = _silero_model().apply_tts(text=text, speaker=self.speaker, sample_rate=48000)
            raw = path.replace('.wav', '-48.wav')
            sf.write(raw, audio.numpy(), 48000)
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-ar', '44100', path],
                           check=True)
            os.remove(raw)
            # только края и пик: паузы у Silero естественные
            _postprocess(path, max_pause=0.6, target_peak=0.9)
        else:
            subprocess.run([PIPER, '--model', self.voice, '--output_file', path,
                            '--length_scale', str(self.length_scale),
                            '--noise_scale', str(self.noise_scale),
                            '--sentence_silence', '0.08'],
                           input=text.encode('utf-8'), check=True, capture_output=True)
            _postprocess(path)
        return _dur(path)

    def add(self, text):
        path = os.path.join(self.tmp, f'line{len(self.cues)}.wav')
        d = self._say(text, path)
        start, end = self.t, self.t + d
        self.cues.append({'text': text, 'start': start, 'end': end, 'wav': path})
        self.t = end + self.gap
        return start, end

    def total(self):
        return self.cues[-1]['end'] + 0.4 if self.cues else 0.0

    def write(self, path):
        if not self.cues:
            raise ValueError('нет реплик')
        with wave.open(self.cues[0]['wav']) as w:
            rate, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        pcm, cursor = bytearray(), 0.0
        for c in self.cues:
            pad = int(round((c['start'] - cursor) * rate)) * ch * sw
            if pad > 0:
                pcm += b'\x00' * pad
            with wave.open(c['wav']) as w:
                pcm += w.readframes(w.getnframes())
            cursor = c['end']
        pcm += b'\x00' * int(max(0.0, self.total() - cursor) * rate) * ch * sw
        with wave.open(path, 'wb') as w:
            w.setnchannels(ch)
            w.setsampwidth(sw)
            w.setframerate(rate)
            w.writeframes(bytes(pcm))
        # выравниваем громкость и убираем низкочастотный гул
        norm = path.replace('.wav', '-norm.wav')
        r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', path,
                            '-af', 'highpass=f=85,acompressor=threshold=0.14:ratio=2.5:attack=8:release=180,'
                                   'loudnorm=I=-16:TP=-1.5:LRA=9',
                            '-ar', '44100', norm], capture_output=True)
        if r.returncode == 0 and os.path.exists(norm):
            os.replace(norm, path)
        return path

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
