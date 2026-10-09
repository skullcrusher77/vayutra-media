"""Generate an original, copyright-free background track (WAV) for a reel or story.

Usage:
    python3 tools/music.py <out.wav> <seconds> [seed] [mood]

mood: "upbeat" (default, travel/adventure), "chill" (sunrise/reflection), "festive" (festival days).
The seed (e.g. the date "2026-10-10") picks key, tempo and melody so each day sounds different
but the same seed always gives the same track. Everything is synthesised here; no samples are used.
"""
import hashlib, sys
import numpy as np
from scipy.io import wavfile

SR = 44100
MOODS = {
    "upbeat":  dict(bpm=(108, 122), progs=[[0, 7, 9, 5], [0, 5, 9, 7], [9, 5, 0, 7]], drums=True,  bright=1.0),
    "chill":   dict(bpm=(84, 94),   progs=[[0, 9, 5, 7], [0, 4, 9, 5]],                drums=False, bright=0.6),
    "festive": dict(bpm=(116, 128), progs=[[0, 5, 7, 0], [0, 7, 5, 7]],                drums=True,  bright=1.2),
}


def note_hz(midi): return 440.0 * 2 ** ((midi - 69) / 12)


def env(n, a=0.01, r=0.3):
    t = np.arange(n) / SR; e = np.ones(n)
    ai = max(1, int(a * SR)); e[:ai] = np.linspace(0, 1, ai)
    return e * np.exp(-t / max(r, 1e-3))


def tone(f, dur, kind="pad", amp=0.2):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == "pad":
        w = sum(np.sin(2 * np.pi * f * m * t + m) / m for m in (1, 2, 3)) + 0.5 * np.sin(2 * np.pi * f * 1.003 * t)
        e = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4).clip(0)
    elif kind == "pluck":
        w = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)
        e = env(n, 0.003, 0.22)
    else:  # bass
        w = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
        e = env(n, 0.01, 0.5)
    return amp * w * e


def kick(): n = int(0.35 * SR); t = np.arange(n) / SR; return 0.9 * np.sin(2 * np.pi * (50 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 9)
def hat(rng): n = int(0.06 * SR); return 0.12 * rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 70)
def clap(rng): n = int(0.18 * SR); return 0.25 * rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 22)


def add(buf, sig, start):
    s = int(start * SR)
    if s >= len(buf): return
    e = min(len(buf), s + len(sig)); buf[s:e] += sig[: e - s]


def make(out, seconds, seed="vayutra", mood="upbeat"):
    m = MOODS.get(mood, MOODS["upbeat"])
    h = int(hashlib.sha256(str(seed).encode()).hexdigest(), 16); rng = np.random.default_rng(h % 2**32)
    key = 57 + int(rng.integers(0, 7))                     # A3 .. D#4 root
    bpm = int(rng.integers(*m["bpm"])); beat = 60 / bpm; bar = 4 * beat
    prog = m["progs"][int(rng.integers(0, len(m["progs"])))]
    scale = [0, 2, 4, 7, 9, 12, 14, 16]                    # major pentatonic-ish
    L = np.zeros(int((seconds + 1) * SR)); R = np.zeros_like(L)
    t, i = 0.0, 0
    melody = [int(rng.integers(0, len(scale))) for _ in range(16)]
    while t < seconds:
        root = key + prog[i % len(prog)]
        minor = prog[i % len(prog)] == 9
        chord = [root, root + (3 if minor else 4), root + 7]
        for k, nn in enumerate(chord):                      # pad, spread across stereo
            p = tone(note_hz(nn), bar, "pad", 0.06)
            add(L, p * (1.0 - 0.3 * k), t); add(R, p * (0.4 + 0.3 * k), t)
        add(L, tone(note_hz(root - 12), bar, "bass", 0.22), t); add(R, tone(note_hz(root - 12), bar, "bass", 0.22), t)
        for s in range(8):                                   # eighth-note pluck arpeggio / melody
            if rng.random() < 0.8:
                nn = key + 12 + scale[melody[(i * 8 + s) % 16]] + (prog[i % len(prog)] if s % 2 else 0)
                pl = tone(note_hz(nn), beat, "pluck", 0.09 * m["bright"])
                pan = 0.5 + 0.4 * np.sin(s)
                add(L, pl * (1 - pan + 0.3), t + s * beat / 2); add(R, pl * (pan + 0.3), t + s * beat / 2)
        if m["drums"] and t >= bar * 0.99:                  # drums enter after first bar
            for b in range(4):
                k = kick(); add(L, k, t + b * beat); add(R, k, t + b * beat)
                if b in (1, 3): c = clap(rng); add(L, c, t + b * beat); add(R, c, t + b * beat)
                for o in (0.5,): hh = hat(rng); add(L, hh * 0.8, t + (b + o) * beat); add(R, hh, t + (b + o) * beat)
        t += bar; i += 1
    n = int(seconds * SR); mix = np.stack([L[:n], R[:n]], 1)
    fade = int(1.5 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]; mix[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.85
    wavfile.write(out, SR, (mix * 32767).astype(np.int16))


if __name__ == "__main__":
    make(sys.argv[1], float(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "vayutra",
         sys.argv[4] if len(sys.argv) > 4 else "upbeat")
