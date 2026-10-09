"""Generate an original, copyright-free background track (WAV) for a reel or story.

Usage:
    python3 tools/music.py <out.wav> <seconds> <seed> [style]

Styles (each has its own instruments, rhythm and scale, so posts never sound alike):
    upbeat     bright pop-travel groove: four-on-the-floor kick, claps, plucked arpeggios
    tropical   tropical house: offbeat marimba plucks, shaker, laid-back kick
    lofi       lo-fi hip hop: swung slow beat, mellow electric-piano chords, vinyl crackle
    cinematic  epic build: wide strings, low taiko-style hits, rising swell
    indian     Indian fusion: tanpura drone, sitar-like plucks in raag Bhupali, tabla-style hand drums
    acoustic   acoustic guitar picking (Karplus-Strong) with light shaker
    chill      ambient pads and soft bells, no drums (sunrise / reflection / safety)
    festive    celebratory: bells, brisk beat, major progression (festival days)

The seed (e.g. "2026-10-10-reel") sets key, tempo, chord progression and melody, so every seed is a new
piece of music and the same seed always gives the same track. Everything is synthesised; no samples are used.
"""
import hashlib, sys
import numpy as np
from scipy.io import wavfile

SR = 44100
STYLES = ["upbeat", "tropical", "lofi", "cinematic", "indian", "acoustic", "chill", "festive"]
CFG = {
    "upbeat":    dict(bpm=(108, 122), progs=[[0, 7, 9, 5], [0, 5, 9, 7], [9, 5, 0, 7]], scale=[0, 2, 4, 7, 9, 12, 14, 16]),
    "tropical":  dict(bpm=(98, 106),  progs=[[9, 5, 0, 7], [0, 9, 5, 7], [5, 7, 9, 9]], scale=[0, 2, 4, 7, 9, 12, 14, 16]),
    "lofi":      dict(bpm=(72, 84),   progs=[[2, 7, 0, 9], [5, 4, 2, 0], [0, 9, 2, 7]], scale=[0, 2, 3, 5, 7, 10, 12, 14]),
    "cinematic": dict(bpm=(76, 88),   progs=[[9, 5, 0, 7], [0, 8, 3, 10], [9, 7, 5, 4]], scale=[0, 2, 3, 5, 7, 8, 12, 14]),
    "indian":    dict(bpm=(88, 104),  progs=[[0, 0, 0, 0]],                             scale=[0, 2, 4, 7, 9, 12, 14, 16]),  # Bhupali
    "acoustic":  dict(bpm=(92, 108),  progs=[[0, 5, 9, 7], [0, 7, 5, 5], [9, 7, 5, 0]], scale=[0, 2, 4, 7, 9, 12, 14, 16]),
    "chill":     dict(bpm=(66, 76),   progs=[[0, 9, 5, 7], [0, 4, 9, 5], [5, 0, 7, 9]], scale=[0, 2, 4, 7, 9, 11, 12, 16]),
    "festive":   dict(bpm=(116, 128), progs=[[0, 5, 7, 0], [0, 7, 5, 7], [0, 9, 5, 7]], scale=[0, 2, 4, 5, 7, 9, 12, 14]),
}


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)


def adsr(n, a=0.01, r=0.3):
    t = np.arange(n) / SR; e = np.exp(-t / max(r, 1e-3)); ai = max(1, int(a * SR)); e[:ai] *= np.linspace(0, 1, ai); return e


def osc(f, dur, kind, amp, rng=None):
    n = int(dur * SR); t = np.arange(n) / SR
    if n <= 0: return np.zeros(0)
    if kind == "pad":
        w = sum(np.sin(2 * np.pi * f * m * t + m) / m for m in (1, 2, 3)) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t)
        e = np.minimum(1, t / 0.5) * np.clip((dur - t) / 0.5, 0, 1)
    elif kind == "strings":
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t)
        w = sum(np.sin(2 * np.pi * f * k * vib * t) / k for k in range(1, 7))
        e = np.minimum(1, t / 0.9) * np.clip((dur - t) / 0.6, 0, 1)
    elif kind == "epiano":
        w = np.sin(2 * np.pi * f * t + 0.8 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 3))
        e = adsr(n, 0.005, 0.9)
    elif kind == "pluck":
        w = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t); e = adsr(n, 0.003, 0.22)
    elif kind == "marimba":
        w = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30); e = adsr(n, 0.002, 0.18)
    elif kind == "bell":
        w = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t); e = adsr(n, 0.002, 0.9)
    elif kind == "sitar":
        w = np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 3.01 * t)
        w *= 1 + 0.3 * np.sin(2 * np.pi * f * 0.5 * t); e = adsr(n, 0.002, 0.45)
    elif kind == "guitar":                                         # Karplus-Strong plucked string
        p = max(2, int(SR / f)); buf = (rng or np.random.default_rng(0)).uniform(-1, 1, p); out = np.zeros(n)
        for i in range(n):
            out[i] = buf[i % p]; buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
        return amp * out
    elif kind == "drone":
        w = sum(np.sin(2 * np.pi * f * k * t + k) / k ** 1.3 for k in range(1, 9)) * (1 + 0.15 * np.sin(2 * np.pi * 0.25 * t))
        e = np.minimum(1, t / 1.0) * np.clip((dur - t) / 1.0, 0, 1)
    else:  # bass
        w = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t); e = adsr(n, 0.01, 0.5)
    return amp * w * e


def noise_hit(rng, dur, decay, amp): n = int(dur * SR); return amp * rng.standard_normal(n) * np.exp(-np.arange(n) / SR * decay)
def kick(amp=0.9): n = int(0.35 * SR); t = np.arange(n) / SR; return amp * np.sin(2 * np.pi * (50 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 9)
def taiko(): n = int(0.9 * SR); t = np.arange(n) / SR; return 0.9 * np.sin(2 * np.pi * (45 + 40 * np.exp(-t * 12)) * t) * np.exp(-t * 4)
def tabla(rng, high=True):
    n = int(0.25 * SR); t = np.arange(n) / SR
    if high: return 0.35 * (np.sin(2 * np.pi * 520 * t) + 0.5 * np.sin(2 * np.pi * 1040 * t)) * np.exp(-t * 22)
    return 0.6 * np.sin(2 * np.pi * (90 + 60 * np.exp(-t * 8)) * t) * np.exp(-t * 6)


class Mix:
    def __init__(self, seconds): self.L = np.zeros(int((seconds + 2) * SR)); self.R = np.zeros_like(self.L)
    def add(self, sig, start, pan=0.5):
        s = int(start * SR)
        if s >= len(self.L) or len(sig) == 0: return
        e = min(len(self.L), s + len(sig)); self.L[s:e] += sig[: e - s] * (1.2 - pan); self.R[s:e] += sig[: e - s] * (0.2 + pan)


def make(out, seconds, seed="vayutra", style="upbeat"):
    style = style if style in CFG else "upbeat"; c = CFG[style]
    h = int(hashlib.sha256(f"{seed}|{style}".encode()).hexdigest(), 16); rng = np.random.default_rng(h % 2**32)
    key = 55 + int(rng.integers(0, 9)); bpm = int(rng.integers(*c["bpm"])); beat = 60 / bpm; bar = 4 * beat
    prog = c["progs"][int(rng.integers(0, len(c["progs"])))]; sc = c["scale"]
    motif = [int(rng.integers(0, len(sc))) for _ in range(16)]
    mx = Mix(seconds); t, i = 0.0, 0
    if style == "indian":
        mx.add(osc(hz(key - 12), seconds + 1, "drone", 0.12), 0, 0.4); mx.add(osc(hz(key - 5), seconds + 1, "drone", 0.07), 0, 0.6)
    while t < seconds:
        deg = prog[i % len(prog)]; root = key + deg; minor = deg in (2, 4, 9) or style in ("lofi", "cinematic") and deg in (0, 9)
        chord = [root, root + (3 if minor else 4), root + 7]
        swing = beat * 0.08 if style == "lofi" else 0
        if style in ("upbeat", "festive", "tropical", "acoustic", "chill"):
            for k, nn in enumerate(chord): mx.add(osc(hz(nn), bar, "pad", 0.05), t, 0.2 + 0.3 * k)
        if style == "cinematic":
            for k, nn in enumerate(chord + [root + 12]): mx.add(osc(hz(nn), bar * 1.05, "strings", 0.05 + 0.02 * min(i, 4)), t, 0.2 + 0.2 * k)
        if style == "lofi":
            for k, nn in enumerate(chord + [root + 10 if minor else root + 11]):
                mx.add(osc(hz(nn), beat * 2, "epiano", 0.07), t + k * 0.012, 0.3 + 0.15 * k); mx.add(osc(hz(nn), beat * 2, "epiano", 0.05), t + 2 * beat + swing, 0.6)
        if style != "indian" and style != "chill":
            mx.add(osc(hz(root - 12), bar, "bass", 0.22 if style != "cinematic" else 0.14), t, 0.5)
        lead = {"upbeat": "pluck", "tropical": "marimba", "lofi": "epiano", "cinematic": "pluck", "indian": "sitar",
                "acoustic": "guitar", "chill": "bell", "festive": "bell"}[style]
        steps = 8 if style not in ("chill", "cinematic") else 4
        for s in range(steps):
            if style == "tropical" and s % 2 == 0: continue
            if rng.random() < (0.85 if style != "chill" else 0.6):
                off = deg if (style == "indian" or s % 2) else 0
                nn = key + 12 + sc[motif[(i * steps + s) % 16]] + (0 if style == "indian" else off)
                dur = bar / steps * (2 if style in ("chill", "indian") else 1)
                amp = {"guitar": 0.35, "bell": 0.06, "sitar": 0.1, "epiano": 0.06}.get(lead, 0.09)
                mx.add(osc(hz(nn), dur, lead, amp, rng), t + s * bar / steps + (swing if s % 2 else 0), 0.3 + 0.4 * ((s * 3) % 5) / 4)
        drums_on = t >= bar * 0.99 or style in ("indian", "acoustic")
        if drums_on:
            for b in range(4):
                bt = t + b * beat
                if style in ("upbeat", "festive"):
                    mx.add(kick(), bt); mx.add(noise_hit(rng, 0.06, 70, 0.1), bt + beat / 2, 0.7)
                    if b in (1, 3): mx.add(noise_hit(rng, 0.18, 22, 0.25), bt)
                elif style == "tropical":
                    if b in (0, 2): mx.add(kick(0.7), bt)
                    if b in (1, 3): mx.add(noise_hit(rng, 0.14, 28, 0.18), bt)
                    for q in range(4): mx.add(noise_hit(rng, 0.04, 90, 0.05), bt + q * beat / 4, 0.8)
                elif style == "lofi":
                    if b in (0, 2): mx.add(kick(0.6), bt + (0.1 * beat if b == 2 else 0))
                    if b in (1, 3): mx.add(noise_hit(rng, 0.16, 30, 0.16), bt)
                    mx.add(noise_hit(rng, 0.05, 80, 0.06), bt + beat / 2 + swing, 0.7)
                elif style == "cinematic":
                    if b == 0 or (i % 2 and b == 2): mx.add(taiko(), bt)
                elif style == "indian":
                    mx.add(tabla(rng, False), bt, 0.4); mx.add(tabla(rng, True), bt + beat / 2, 0.6)
                    if rng.random() < 0.5: mx.add(tabla(rng, True), bt + 3 * beat / 4, 0.6)
                elif style == "acoustic":
                    mx.add(noise_hit(rng, 0.05, 60, 0.05), bt, 0.7); mx.add(noise_hit(rng, 0.05, 60, 0.04), bt + beat / 2, 0.3)
                    if b in (1, 3): mx.add(noise_hit(rng, 0.12, 35, 0.08), bt)
        t += bar; i += 1
    n = int(seconds * SR); mix = np.stack([mx.L[:n], mx.R[:n]], 1)
    if style == "lofi": mix += (rng.random((n, 1)) < 0.0004) * rng.uniform(-0.3, 0.3, (n, 1)) + 0.004 * rng.standard_normal((n, 2))
    if style == "cinematic": mix *= np.linspace(0.55, 1.0, n)[:, None]
    fade = int(min(1.5, seconds / 4) * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    fi = int(0.25 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.85
    wavfile.write(out, SR, (mix * 32767).astype(np.int16))


if __name__ == "__main__":
    make(sys.argv[1], float(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "vayutra",
         sys.argv[4] if len(sys.argv) > 4 else "upbeat")
