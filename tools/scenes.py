"""Draw original illustrated Odisha scenes (flat, sunset-toned art) for use as backgrounds.

Usage in a spec: "scene": "beach" on the post, a story, or a reel scene.
Scenes: beach, surf, temple, wheel, lake, oldtown, sunrise, cycle, campfire, night
Each call with a different seed varies the composition (sun position, waves, boats, birds...).
"""
import hashlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SCENES = ["beach", "surf", "temple", "wheel", "lake", "oldtown", "sunrise", "cycle", "campfire", "night"]
SKIES = [((22, 24, 48), (120, 60, 120), (255, 150, 90)), ((18, 30, 60), (60, 90, 150), (255, 190, 120)),
         ((25, 20, 45), (150, 70, 110), (255, 120, 90)), ((15, 25, 50), (40, 110, 160), (250, 210, 150))]


def rng_for(seed): return np.random.default_rng(int(hashlib.sha256(str(seed).encode()).hexdigest(), 16) % 2**32)


def sky(w, h, top, mid, bot, horizon):
    y = np.arange(h)[:, None] / max(1, horizon)
    t1 = np.clip(y * 2, 0, 1); t2 = np.clip(y * 2 - 1, 0, 1)
    c = [(np.array(top) * (1 - t1) + np.array(mid) * t1) * (1 - t2) + np.array(bot) * t2 for _ in range(1)][0]
    arr = np.repeat(c[:, None, :], w, axis=1).reshape(h, w, 3) if c.ndim == 2 else np.broadcast_to(c, (h, w, 3))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def sun(d, cx, cy, r, col=(255, 200, 110)):
    for k in range(6, 0, -1):
        a = 30 + k * 6; rr = r * (1 + k * 0.18)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=tuple(int(min(255, c * 0.9)) for c in col) + (a,))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,))


def waves(d, w, top, h, rng, cols, n=7, amp=10):
    for i in range(n):
        y0 = top + (h - top) * (i / n) ** 1.3; col = cols[i % len(cols)]
        pts = [(x, y0 + amp * (1 + i * 0.4) * math.sin(x / (60 + i * 25) + rng.uniform(0, 6))) for x in range(0, w + 20, 20)]
        d.polygon(pts + [(w, h), (0, h)], fill=col)


def birds(d, w, y, rng, n=6, col=(30, 25, 45)):
    for _ in range(n):
        x = rng.uniform(0.1, 0.9) * w; yy = y + rng.uniform(-80, 80); s = rng.uniform(10, 22)
        d.line([(x - s, yy - s * 0.3), (x, yy), (x + s, yy - s * 0.3)], fill=col, width=4)


def person(d, x, y, s, col=(25, 22, 40)):
    d.ellipse((x - s * 0.18, y - s, x + s * 0.18, y - s * 0.64), fill=col)
    d.polygon([(x - s * 0.22, y - s * 0.62), (x + s * 0.22, y - s * 0.62), (x + s * 0.16, y - s * 0.1), (x - s * 0.16, y - s * 0.1)], fill=col)
    d.line([(x - s * 0.1, y - s * 0.12), (x - s * 0.18, y)], fill=col, width=max(3, int(s * 0.1)))
    d.line([(x + s * 0.1, y - s * 0.12), (x + s * 0.18, y)], fill=col, width=max(3, int(s * 0.1)))


def temple(d, cx, base, s, col):
    """Kalinga-style rekha deula silhouette with amalaka and flag."""
    tw = s * 0.42
    pts = [(cx - tw, base), (cx - tw * 0.92, base - s * 0.55)]
    for k in range(12):
        t = k / 11; pts.append((cx - tw * (0.92 - 0.55 * t ** 1.6), base - s * (0.55 + 0.38 * t)))
    pts += [(cx - tw * 0.3, base - s * 0.95)]
    right = [(2 * cx - x, y) for x, y in reversed(pts)]
    d.polygon(pts + right, fill=col)
    d.ellipse((cx - tw * 0.42, base - s * 1.02, cx + tw * 0.42, base - s * 0.92), fill=col)
    d.line([(cx, base - s * 1.02), (cx, base - s * 1.18)], fill=col, width=max(3, int(s * 0.012)))
    d.polygon([(cx, base - s * 1.18), (cx + s * 0.09, base - s * 1.15), (cx, base - s * 1.12)], fill=(230, 90, 70))
    # jagamohana (porch)
    pw = s * 0.36; d.polygon([(cx + tw * 0.9, base), (cx + tw * 0.9, base - s * 0.3), (cx + tw * 0.9 + pw * 0.5, base - s * 0.5),
                              (cx + tw * 0.9 + pw, base - s * 0.3), (cx + tw * 0.9 + pw, base)], fill=col)


def chariot_wheel(d, cx, cy, r, col, accent):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=int(r * 0.12))
    d.ellipse((cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78), outline=accent, width=int(r * 0.03))
    for k in range(8):
        a = k * math.pi / 4; w = int(r * (0.07 if k % 2 == 0 else 0.04))
        d.line([(cx, cy), (cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a))], fill=col, width=w)
    for k in range(32):
        a = k * math.pi / 16; d.ellipse((cx + r * 0.95 * math.cos(a) - 6, cy + r * 0.95 * math.sin(a) - 6,
                                         cx + r * 0.95 * math.cos(a) + 6, cy + r * 0.95 * math.sin(a) + 6), fill=accent)
    d.ellipse((cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18), fill=col)
    d.ellipse((cx - r * 0.08, cy - r * 0.08, cx + r * 0.08, cy + r * 0.08), fill=accent)


def boat(d, x, y, s, col):
    d.polygon([(x - s, y), (x + s, y), (x + s * 0.7, y + s * 0.25), (x - s * 0.7, y + s * 0.25)], fill=col)
    d.line([(x, y), (x, y - s * 0.9)], fill=col, width=max(2, int(s * 0.05)))
    d.polygon([(x + 4, y - s * 0.85), (x + s * 0.6, y - s * 0.2), (x + 4, y - s * 0.2)], fill=tuple(min(255, c + 60) for c in col))


def cyclist(d, x, y, s, col):
    r = s * 0.28
    for cx in (x - s * 0.38, x + s * 0.38): d.ellipse((cx - r, y - r, cx + r, y + r), outline=col, width=max(3, int(s * 0.05)))
    d.line([(x - s * 0.38, y), (x, y - s * 0.05), (x + s * 0.38, y), (x + s * 0.2, y - s * 0.4), (x - s * 0.15, y - s * 0.4), (x, y - s * 0.05)],
           fill=col, width=max(3, int(s * 0.05)))
    d.line([(x - s * 0.12, y - s * 0.45), (x + s * 0.05, y - s * 0.95), (x + s * 0.25, y - s * 0.55)], fill=col, width=max(4, int(s * 0.08)))
    d.ellipse((x - s * 0.04, y - s * 1.2, x + s * 0.2, y - s * 0.96), fill=col)


def palm(d, x, base, s, col):
    d.line([(x, base), (x + s * 0.15, base - s)], fill=col, width=max(4, int(s * 0.05)))
    tx, ty = x + s * 0.15, base - s
    for a in (-160, -130, -100, -60, -30, -5):
        r = math.radians(a)
        d.polygon([(tx, ty), (tx + s * 0.45 * math.cos(r), ty + s * 0.45 * math.sin(r) + s * 0.12),
                   (tx + s * 0.42 * math.cos(r + 0.15), ty + s * 0.42 * math.sin(r + 0.15))], fill=col)


def draw(name, w, h, seed="vayutra"):
    rng = rng_for(f"{name}-{seed}"); name = name if name in SCENES else "beach"
    top, mid, bot = SKIES[int(rng.integers(0, len(SKIES)))]
    if name == "night": top, mid, bot = (8, 10, 28), (20, 28, 60), (60, 50, 90)
    horizon = int(h * rng.uniform(0.52, 0.62))
    im = sky(w, h, top, mid, bot, horizon).convert("RGBA")
    lay = Image.new("RGBA", (w, h)); d = ImageDraw.Draw(lay)
    sx, sy, sr = w * rng.uniform(0.3, 0.7), horizon - h * rng.uniform(0.06, 0.2), w * rng.uniform(0.09, 0.14)
    if name == "night":
        for _ in range(140):
            x, y = rng.uniform(0, w), rng.uniform(0, horizon); r = rng.uniform(1, 3); d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 240, int(rng.uniform(90, 230))))
        d.ellipse((w * 0.7, h * 0.12, w * 0.7 + w * 0.12, h * 0.12 + w * 0.12), fill=(245, 240, 220, 255))
    elif name != "campfire":
        sun(d, sx, sy, sr)
    sea = [(40, 60, 110), (55, 80, 135), (35, 50, 95), (70, 95, 150)]
    if name in ("beach", "surf", "sunrise"):
        waves(d, w, horizon, int(h * 0.82), rng, sea, n=8, amp=8)
        d.rectangle((0, int(h * 0.80), w, h), fill=(205, 165, 120))
        waves(d, w, int(h * 0.79), int(h * 0.84), rng, [(235, 230, 225)], n=1, amp=6)
        palm(d, w * 0.08, h * 0.86, h * 0.33, (25, 22, 40)); palm(d, w * 0.95, h * 0.9, h * 0.26, (25, 22, 40))
        if name == "surf":
            for k in range(int(rng.integers(2, 4))):
                x = w * rng.uniform(0.25, 0.75); y = horizon + (h * 0.8 - horizon) * rng.uniform(0.3, 0.75)
                d.polygon([(x - 70, y), (x + 70, y - 8), (x + 60, y + 10), (x - 60, y + 14)], fill=(250, 210, 90))
                person(d, x, y, 120, (25, 22, 40))
        else:
            for k in range(3): person(d, w * (0.38 + 0.1 * k), h * 0.92, h * (0.08 - k * 0.006))
        birds(d, w, horizon - h * 0.25, rng)
    elif name in ("temple", "wheel"):
        d.rectangle((0, horizon, w, h), fill=(190, 140, 100))
        temple(d, w * 0.42, horizon + h * 0.03, h * 0.36, (35, 25, 45))
        if name == "wheel":
            chariot_wheel(d, w * 0.5, h * 0.76, w * 0.3, (60, 40, 50), (230, 170, 90))
        for k in range(4): person(d, w * (0.1 + 0.27 * k), h * 0.95, h * 0.07)
        birds(d, w, h * 0.22, rng, 5)
    elif name == "lake":
        for k in range(3):
            x = w * rng.uniform(0, 1); d.ellipse((x - w * 0.3, horizon - h * 0.04, x + w * 0.3, horizon + h * 0.02), fill=(45, 50, 70))
        d.rectangle((0, horizon, w, h), fill=(55, 75, 120))
        refl = Image.new("RGBA", (w, h)); rd = ImageDraw.Draw(refl)
        for k in range(24):
            y = horizon + (h - horizon) * k / 24; ww = sr * (1.2 - k / 30)
            rd.line([(sx - ww, y), (sx + ww, y)], fill=(255, 190, 120, 140), width=6)
        lay = Image.alpha_composite(lay, refl); d = ImageDraw.Draw(lay)
        for k in range(int(rng.integers(2, 4))): boat(d, w * rng.uniform(0.15, 0.85), horizon + (h - horizon) * rng.uniform(0.2, 0.7), w * rng.uniform(0.08, 0.13), (30, 25, 45))
        birds(d, w, horizon - h * 0.15, rng, 10)
    elif name in ("oldtown", "cycle"):
        d.rectangle((0, horizon, w, h), fill=(150, 110, 90))
        for k in range(5):
            s = h * rng.uniform(0.14, 0.28); temple(d, w * (0.05 + 0.24 * k), horizon + h * 0.02, s, (40 + k * 4, 30, 50))
        d.rectangle((0, int(h * 0.8), w, h), fill=(70, 55, 70))
        for k in range(12): d.rectangle((k * w / 12 + 10, h * 0.86, k * w / 12 + 60, h * 0.87), fill=(230, 210, 170))
        for k in range(3 if name == "cycle" else 1): cyclist(d, w * (0.25 + 0.25 * k), h * 0.79, h * 0.16, (20, 18, 32))
    elif name == "campfire":
        d.rectangle((0, horizon, w, h), fill=(30, 28, 45))
        for _ in range(80):
            x, y = rng.uniform(0, w), rng.uniform(0, horizon); r = rng.uniform(1, 3); d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 240, 180))
        fx, fy = w * 0.5, h * 0.78
        glow = Image.new("RGBA", (w, h)); gd = ImageDraw.Draw(glow); gd.ellipse((fx - w * 0.5, fy - w * 0.35, fx + w * 0.5, fy + w * 0.25), fill=(255, 140, 60, 110))
        lay = Image.alpha_composite(lay, glow.filter(ImageFilter.GaussianBlur(80))); d = ImageDraw.Draw(lay)
        for col, s in (((255, 120, 50), 1.0), ((255, 190, 80), 0.65), ((255, 240, 170), 0.35)):
            d.polygon([(fx - 90 * s, fy), (fx, fy - 260 * s), (fx + 90 * s, fy)], fill=col)
        for k in range(5): person(d, fx + (k - 2) * w * 0.17, fy + 80, 170 if k % 2 else 150)
    elif name == "night":
        d.rectangle((0, horizon, w, h), fill=(20, 22, 40)); waves(d, w, horizon, h, rng, [(25, 30, 60), (30, 38, 70)], n=5, amp=6)
    im = Image.alpha_composite(im, lay)
    # subtle grain so it reads as art, not flat vectors
    g = (rng.standard_normal((h, w, 1)) * 6).astype(np.int16)
    arr = np.clip(np.asarray(im.convert("RGB")).astype(np.int16) + g, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


if __name__ == "__main__":
    import sys
    os_out = sys.argv[1] if len(sys.argv) > 1 else "scenes_preview.jpg"
    tiles = [draw(n, 540, 960, "preview") for n in SCENES]
    sheet = Image.new("RGB", (540 * 5, 960 * 2))
    for i, t in enumerate(tiles): sheet.paste(t, ((i % 5) * 540, (i // 5) * 960))
    sheet.save(os_out, quality=88)
