"""Render one day of Vayutra Instagram content from a JSON spec.

Usage:
    python3 tools/render.py <spec.json> <out_dir>

Produces in out_dir: post.jpg (1080x1350), reel.mp4 (1080x1920, ~15-20s),
reel_cover.jpg, story1.jpg ... storyN.jpg (1080x1920).

Spec format (all text fields plain strings, keep them short):
{
  "post":    {"kicker": "THE", "title": ["Odisha", "Experience"], "subtitle": "6 days · 5 nights · Age 10+",
              "items": [["01", "Bhubaneswar", "Heritage walk & team challenges"], ...]},   # 3-6 items
  "reel":    {"scenes": [{"kicker": "DAY 1", "big": ["Bhubaneswar"], "small": "Heritage walk"}, ...],  # 4-8 scenes
              "end": {"kicker": "THE ODISHA EXPERIENCE", "small": "Age 10+ · 6 days / 5 nights", "cta": "DM us “ODISHA”"}},
  "music":   {"seed": "2026-10-10", "reel": "tropical", "stories": ["lofi", "indian", "acoustic"]},
             # styles: upbeat tropical lofi cinematic indian acoustic chill festive (see tools/music.py)
  "stories": [{"kicker": "PARENTS ASK US", "big": ["Is it safe?"], "accent": "", "body": "",
               "bullets": ["24x7 supervision", ...], "cta": "Questions? DM us"}, ...]          # 2-3 stories
}
Only the Poppins font is available: avoid arrows and unusual symbols (write "to" instead of "→").
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(ROOT, "brand", "logo.jpg")
F = "/usr/share/fonts/truetype/google-fonts/"
BG, WHITE, MUTED = (27, 26, 40), (245, 245, 250), (175, 172, 200)
GRAD = [(46, 230, 255), (255, 210, 74), (255, 95, 162), (155, 92, 255)]


def font(w, s):
    for path in (F + f"Poppins-{w}.ttf", f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if w == 'Bold' else ''}.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, s)
    return ImageFont.load_default()


def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def grad(t):
    t = max(0, min(1, t)) * (len(GRAD) - 1); i = min(int(t), len(GRAD) - 2)
    return lerp(GRAD[i], GRAD[i + 1], t - i)


def keyed(src):
    rgba = src.convert("RGBA"); px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, _ = px[x, y]
            d = abs(r - 27) + abs(g - 26) + abs(b - 40)
            px[x, y] = (r, g, b, max(0, min(255, int((d - 14) * 6))))
    return rgba


_logo = Image.open(LOGO).convert("RGB")
LOGO_FULL = keyed(_logo.crop((200, 130, 850, 830)))
LOGO_MARK = keyed(_logo.crop((240, 150, 840, 700)))


def canvas(w, h):
    im = Image.new("RGB", (w, h), BG)
    glow = Image.new("RGB", (w, h), BG); g = ImageDraw.Draw(glow)
    g.ellipse((-w * 0.3, -h * 0.15, w * 0.6, h * 0.35), fill=(40, 60, 90))
    g.ellipse((w * 0.5, h * 0.65, w * 1.3, h * 1.15), fill=(70, 40, 90))
    return Image.blend(im, glow.filter(ImageFilter.GaussianBlur(160)), 0.85)


def paste_logo(im, lg, size, cx, cy):
    lg = lg.copy(); lg.thumbnail((size, size))
    im.paste(lg, (int(cx - lg.width / 2), int(cy - lg.height / 2)), lg)


def wrap(d, s, f, maxw):
    out, cur = [], ""
    for wd in s.split():
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: out.append(cur)
            cur = wd
    if cur: out.append(cur)
    return out


def fit(d, s, w, size, maxw, minsize=40):
    while size > minsize and d.textlength(s, font=font(w, size)) > maxw: size -= 4
    return font(w, size)


def center(d, y, s, f, fill, W):
    d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill)


def footer(im, W, H):
    d = ImageDraw.Draw(im)
    paste_logo(im, LOGO_MARK, 90, 105, H - 95)
    d.text((165, H - 122), "VAYUTRA", font=font("Bold", 34), fill=WHITE)
    d.text((165, H - 80), "Explore. Engage. Evolve.", font=font("Regular", 24), fill=MUTED)
    f = font("Medium", 28); s = "vayutra.in"
    d.text((W - 60 - d.textlength(s, font=f), H - 105), s, font=f, fill=MUTED)


def render_post(p, out):
    W, H = 1080, 1350; im = canvas(W, H); d = ImageDraw.Draw(im)
    d.text((70, 90), p.get("kicker", ""), font=font("Medium", 44), fill=MUTED)
    y = 135
    for line in p["title"][:2]:
        f = fit(d, line, "Bold", 150, 940, 80); d.text((70, y), line, font=f, fill=WHITE); y += int(f.size * 1.1)
    y += 20
    d.rectangle((75, y, 375, y + 10), fill=None)
    for i in range(300): d.line([(75 + i, y), (75 + i, y + 10)], fill=grad(i / 300))
    y += 40
    d.text((70, y), p.get("subtitle", ""), font=fit(d, p.get("subtitle", ""), "Medium", 40, 940, 28), fill=grad(0))
    items = p.get("items", [])[:6]
    y += 85; step = min(100, int((H - 170 - y) / max(1, len(items))))
    for i, (n, t, s) in enumerate(items):
        d.text((70, y), n, font=font("Bold", 48), fill=grad(i / max(1, len(items) - 1)))
        d.text((180, y - 2), t, font=fit(d, t, "Bold", 40, 830, 28), fill=WHITE)
        d.text((180, y + 50), s, font=fit(d, s, "Regular", 28, 830, 22), fill=MUTED)
        y += step
    footer(im, W, H); im.save(os.path.join(out, "post.jpg"), quality=95)


def render_story(s, path):
    W, H = 1080, 1920; im = canvas(W, H); d = ImageDraw.Draw(im)
    paste_logo(im, LOGO_MARK, 200, W / 2, 230)
    center(d, 360, s.get("kicker", ""), font("Medium", 38), grad(0.1), W)
    y = 560
    for line in s.get("big", []):
        f = fit(d, line, "Bold", 110, 940, 60); center(d, y, line, f, WHITE, W); y += int(f.size * 1.25)
    if s.get("accent"):
        f = fit(d, s["accent"], "Bold", 64, 940, 36); center(d, y + 10, s["accent"], f, grad(0.4), W); y += int(f.size * 1.4) + 20
    y += 40
    if s.get("body"):
        f = font("Regular", 40)
        for ln in wrap(d, s["body"], f, 860): center(d, y, ln, f, MUTED, W); y += 60
        y += 30
    bl = s.get("bullets", [])[:6]
    if bl:
        f = font("Medium", 46); widest = max(d.textlength(b, font=f) for b in bl); x0 = int((W - widest - 70) / 2)
        for i, b in enumerate(bl):
            c = grad(i / max(1, len(bl) - 1))
            d.ellipse((x0, y + 14, x0 + 34, y + 48), outline=c, width=5)
            d.text((x0 + 70, y), b, font=fit(d, b, "Medium", 46, 860, 30), fill=WHITE); y += 95
        y += 30
    if s.get("cta"):
        y = max(y + 40, 1420); y = min(y, 1560)
        f = fit(d, s["cta"], "Bold", 46, 560, 30); tw = d.textlength(s["cta"], font=f)
        d.rounded_rectangle(((W - tw) / 2 - 60, y, (W + tw) / 2 + 60, y + 110), 55, outline=grad(0.6), width=4)
        center(d, y + 27, s["cta"], f, WHITE, W)
    footer(im, W, H); im.save(path, quality=95)


def reel_frame(sc, end=False):
    W, H = 1080, 1920; im = canvas(W, H); d = ImageDraw.Draw(im)
    if end:
        paste_logo(im, LOGO_FULL, 700, W / 2, 760)
        center(d, 1180, sc.get("kicker", ""), fit(d, sc.get("kicker", ""), "Bold", 50, 940, 30), grad(0.2), W)
        center(d, 1270, sc.get("small", ""), fit(d, sc.get("small", ""), "Medium", 52, 940, 30), MUTED, W)
        if sc.get("cta"):
            f = fit(d, sc["cta"], "Bold", 50, 600, 30); tw = d.textlength(sc["cta"], font=f)
            d.rounded_rectangle(((W - tw) / 2 - 70, 1560, (W + tw) / 2 + 70, 1680), 60, outline=grad(0.6), width=5)
            center(d, 1588, sc["cta"], f, WHITE, W)
    else:
        paste_logo(im, LOGO_MARK, 160, W / 2, 260)
        if sc.get("kicker"): center(d, 640, sc["kicker"], font("Bold", 50), grad(sc.get("_t", 0)), W)
        y = 740; big = sc.get("big", [])
        for i, line in enumerate(big):
            f = fit(d, line, "Bold", 130, 960, 60)
            col = grad(0.5) if (len(big) > 1 and i == len(big) - 1 and sc.get("accent_last", True)) else WHITE
            center(d, y, line, f, col, W); y += int(f.size * 1.2)
        if sc.get("small"):
            f = font("Medium", 52)
            for ln in wrap(d, sc["small"], f, 920): center(d, y + 10, ln, f, MUTED, W); y += 66
    for i in range(W): d.line([(i, H - 14), (i, H)], fill=grad(i / W))
    return im


def music_track(out, name, seconds, spec):
    """Each asset gets its own style + seed. spec["music"] = {"seed": D, "reel": style, "stories": [style, ...]}."""
    m = spec.get("music", {})
    if name == "reel":
        style = m.get("reel", m.get("mood", "upbeat"))
    else:
        idx = int(name.replace("story", "")) - 1; st = m.get("stories", [])
        style = st[idx] if idx < len(st) else music.STYLES[(idx + 3) % len(music.STYLES)]
    path = os.path.join(out, f"_{name}.wav")
    music.make(path, seconds, f"{m.get('seed', out)}-{name}", style)
    return path


def render_story_videos(out, n, spec):
    """Turn story images into 8-second vertical videos with a slow zoom and music."""
    for i in range(1, n + 1):
        img = os.path.join(out, f"story{i}.jpg"); wav = music_track(out, f"story{i}", 8, spec)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", img, "-i", wav, "-filter_complex",
                        "[0:v]scale=1188:2112,zoompan=z='min(1+0.0008*on,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                        ":d=240:s=1080x1920:fps=30,format=yuv420p,setsar=1[v]", "-map", "[v]", "-map", "1:a",
                        "-t", "8", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-b:v", "2000k", "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", os.path.join(out, f"story{i}.mp4")], check=True)
        os.remove(wav)


def render_reel(r, out, spec=None):
    tmp = os.path.join(out, "_reel"); os.makedirs(tmp, exist_ok=True)
    scenes = r["scenes"][:8]
    for i, sc in enumerate(scenes): sc["_t"] = i / max(1, len(scenes) - 1)
    frames = [reel_frame(sc) for sc in scenes] + [reel_frame(r["end"], end=True)]
    for i, fr in enumerate(frames): fr.save(os.path.join(tmp, f"s{i}.png"))
    dur, fade, last_extra = 2.3, 0.4, 1.2
    inputs, fc = [], []
    for i in range(len(frames)):
        n = int((dur + (last_extra if i == len(frames) - 1 else 0)) * 30)
        inputs += ["-i", os.path.join(tmp, f"s{i}.png")]
        fc.append(f"[{i}:v]scale=1188:2112,zoompan=z='min(1+0.0015*on,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={n}:s=1080x1920:fps=30,format=yuv420p,setsar=1[v{i}]")
    total = (dur - fade) * (len(frames) - 1) + dur + last_extra
    wav = music_track(out, "reel", total, spec or {})
    prev, offset = "v0", dur - fade
    for i in range(1, len(frames)):
        fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={fade}:offset={offset:.2f}[x{i}]")
        prev = f"x{i}"; offset += dur - fade
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + inputs + [
        "-i", wav,
        "-filter_complex", ";".join(fc), "-map", f"[{prev}]", "-map", f"{len(frames)}:a", "-shortest",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30", "-b:v", "2500k",
        "-maxrate", "3000k", "-bufsize", "6000k", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
        os.path.join(out, "reel.mp4")], check=True)
    frames[-1].convert("RGB").save(os.path.join(out, "reel_cover.jpg"), quality=92)
    os.remove(wav)
    for f in os.listdir(tmp): os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    render_post(spec["post"], out)
    stories = spec["stories"][:3]
    for i, s in enumerate(stories, 1): render_story(s, os.path.join(out, f"story{i}.jpg"))
    render_story_videos(out, len(stories), spec)
    render_reel(spec["reel"], out, spec)
    print("rendered:", sorted(os.listdir(out)))
