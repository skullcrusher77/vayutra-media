"""Generate Vayutra branded Instagram content: 1 feed post, 3 stories, 1 reel.
Usage: python3 make_content.py <logo_path> <out_dir>
"""
import os, sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

LOGO, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
F = "/usr/share/fonts/truetype/google-fonts/"
def font(w, s): return ImageFont.truetype(F + f"Poppins-{w}.ttf", s)

BG = (27, 26, 40)
WHITE = (245, 245, 250)
MUTED = (175, 172, 200)
GRAD = [(46, 230, 255), (255, 210, 74), (255, 95, 162), (155, 92, 255)]

logo_full = Image.open(LOGO).convert("RGB").crop((200, 130, 850, 830))   # symbol + wordmark
logo_mark = Image.open(LOGO).convert("RGB").crop((240, 150, 840, 700))   # symbol only

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def grad_color(t):
    t = max(0, min(1, t)) * (len(GRAD) - 1); i = min(int(t), len(GRAD) - 2)
    return lerp(GRAD[i], GRAD[i + 1], t - i)

def canvas(w, h):
    im = Image.new("RGB", (w, h), BG)
    # soft glow blobs in brand colours
    glow = Image.new("RGB", (w, h), BG); g = ImageDraw.Draw(glow)
    g.ellipse((-w*0.3, -h*0.15, w*0.6, h*0.35), fill=(40, 60, 90))
    g.ellipse((w*0.5, h*0.65, w*1.3, h*1.15), fill=(70, 40, 90))
    return Image.blend(im, glow.filter(ImageFilter.GaussianBlur(160)), 0.85)

def grad_bar(d, x, y, w, h):
    for i in range(w):
        d.line([(x + i, y), (x + i, y + h)], fill=grad_color(i / w))

def text_c(d, y, s, f, fill, W):
    tw = d.textlength(s, font=f); d.text(((W - tw) / 2, y), s, font=f, fill=fill)

def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); return lines

def keyed(src):
    """Turn the logo's flat navy background transparent so it sits on any canvas."""
    rgba = src.convert("RGBA"); px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, _ = px[x, y]
            dist = abs(r - 27) + abs(g - 26) + abs(b - 40)
            px[x, y] = (r, g, b, max(0, min(255, int((dist - 14) * 6))))
    return rgba
logo_full, logo_mark = keyed(logo_full), keyed(logo_mark)

def paste_logo(im, kind, size, cx, cy):
    lg = (logo_full if kind == "full" else logo_mark).copy()
    lg.thumbnail((size, size))
    im.paste(lg, (int(cx - lg.width / 2), int(cy - lg.height / 2)), lg)

def footer(im, W, H):
    d = ImageDraw.Draw(im)
    lg = logo_mark.copy(); lg.thumbnail((90, 90))
    im.paste(lg, (60, H - 140), lg)
    d.text((165, H - 122), "VAYUTRA", font=font("Bold", 34), fill=WHITE)
    d.text((165, H - 80), "Explore. Engage. Evolve.", font=font("Regular", 24), fill=MUTED)
    s = "vayutra.in"; f = font("Medium", 28)
    d.text((W - 60 - d.textlength(s, font=f), H - 105), s, font=f, fill=MUTED)

# ---------------- FEED POST 1080x1350 ----------------
def make_post():
    W, H = 1080, 1350; im = canvas(W, H); d = ImageDraw.Draw(im)
    d.text((70, 90), "THE", font=font("Medium", 44), fill=MUTED)
    d.text((70, 135), "Odisha", font=font("Bold", 150), fill=WHITE)
    d.text((70, 300), "Experience", font=font("Bold", 150), fill=WHITE)
    grad_bar(d, 75, 490, 300, 10)
    d.text((70, 530), "6 days · 5 nights · Age 10+", font=font("Medium", 40), fill=grad_color(0.0))
    days = [("01", "Bhubaneswar", "Heritage walk & team challenges"),
            ("02", "Old Town", "Cycle ride through temple lanes"),
            ("03", "Konark to Puri", "Sun Temple & the coast"),
            ("04", "Konark Coast  NEW", "Surfing, SUP & forest hike"),
            ("05", "Chilika Lake", "Boat ride & ecosystem learning"),
            ("06", "Wrap-up", "Reflect. Share. Grow.")]
    y = 615
    for i, (n, t, s) in enumerate(days):
        c = grad_color(i / 5)
        d.text((70, y), n, font=font("Bold", 48), fill=c)
        d.text((180, y - 2), t, font=font("Bold", 40), fill=WHITE)
        d.text((180, y + 50), s, font=font("Regular", 28), fill=MUTED)
        y += 92
    footer(im, W, H)
    im.save(f"{OUT}/post.jpg", quality=95)

# ---------------- STORIES 1080x1920 ----------------
def story_base(kicker):
    W, H = 1080, 1920; im = canvas(W, H); d = ImageDraw.Draw(im)
    paste_logo(im, "mark", 200, W / 2, 230)
    text_c(d, 360, kicker, font("Medium", 38), grad_color(0.1), W)
    return im, d, W, H

def make_stories():
    im, d, W, H = story_base("THE ODISHA EXPERIENCE")
    for i, line in enumerate(["Have you ever", "surfed a wave?"]):
        text_c(d, 600 + i * 130, line, font("Bold", 100), WHITE, W)
    text_c(d, 900, "On Day 4 you will.", font("Medium", 54), grad_color(0.3), W)
    for i, line in enumerate(wrap(d, "Surfing and stand-up paddling on the Konark coast, with certified instructors and full safety gear.", font("Regular", 40), 860)):
        text_c(d, 1060 + i * 60, line, font("Regular", 40), MUTED, W)
    d.rounded_rectangle((240, 1420, 840, 1530), 55, fill=None, outline=grad_color(0.6), width=4)
    text_c(d, 1447, "DM us  “SURF”", font("Bold", 46), WHITE, W)
    footer(im, W, H); im.save(f"{OUT}/story1.jpg", quality=95)

    im, d, W, H = story_base("6 DAYS · 5 NIGHTS")
    text_c(d, 560, "Not a trip.", font("Bold", 110), WHITE, W)
    text_c(d, 700, "A transformation.", font("Bold", 96), grad_color(0.45), W)
    for i, s in enumerate(["Bhubaneswar", "Konark", "Puri", "Chilika Lake"]):
        y = 980 + i * 110; c = grad_color(i / 3)
        d.ellipse((300, y + 18, 330, y + 48), fill=c)
        d.text((360, y), s, font=font("Medium", 56), fill=WHITE)
    text_c(d, 1490, "Tap the link in bio to learn more", font("Regular", 38), MUTED, W)
    footer(im, W, H); im.save(f"{OUT}/story2.jpg", quality=95)

    im, d, W, H = story_base("PARENTS ASK US")
    text_c(d, 560, "Is it safe?", font("Bold", 120), WHITE, W)
    items = ["24x7 supervision", "Certified instructors", "Verified stays", "Safety gear for every activity",
             "Regular updates to parents", "Parent orientation before the trip"]
    for i, s in enumerate(items):
        y = 820 + i * 100; c = grad_color(i / 5)
        d.text((170, y), "✓", font=font("Bold", 52), fill=c) if False else d.ellipse((170, y + 14, 206, y + 50), outline=c, width=5)
        d.text((240, y), s, font=font("Medium", 48), fill=WHITE)
    text_c(d, 1480, "Questions? DM us anytime", font("Medium", 42), grad_color(0.2), W)
    footer(im, W, H); im.save(f"{OUT}/story3.jpg", quality=95)

# ---------------- REEL 1080x1920 ----------------
def reel_frame(lines, kicker=None, accent=0.0, big_logo=False, cta=None):
    W, H = 1080, 1920; im = canvas(W, H); d = ImageDraw.Draw(im)
    if big_logo:
        paste_logo(im, "full", 700, W / 2, 760)
    else:
        paste_logo(im, "mark", 160, W / 2, 260)
    if kicker:
        text_c(d, 640 if not big_logo else 1180, kicker, font("Bold", 50), grad_color(accent), W)
    y = 740 if not big_logo else 1270
    for txt, size, col in lines:
        f = font("Bold" if size >= 80 else "Medium", size)
        for ln in wrap(d, txt, f, 920):
            text_c(d, y, ln, f, col, W); y += int(size * 1.25)
    if cta:
        d.rounded_rectangle((200, 1560, 880, 1680), 60, outline=grad_color(0.6), width=5)
        text_c(d, 1588, cta, font("Bold", 50), WHITE, W)
    grad_bar(d, 0, H - 14, W, 14)
    return im

def make_reel():
    scenes = [
        reel_frame([("6 days.", 140, WHITE), ("5 nights.", 140, WHITE), ("One Odisha.", 140, grad_color(0.5))]),
        reel_frame([("Bhubaneswar", 110, WHITE), ("Heritage walk + team challenges", 52, MUTED)], "DAY 1", 0.0),
        reel_frame([("Old Town", 110, WHITE), ("Cycle ride through temple lanes", 52, MUTED)], "DAY 2", 0.15),
        reel_frame([("Konark to Puri", 104, WHITE), ("The Sun Temple and the coast", 52, MUTED)], "DAY 3", 0.3),
        reel_frame([("Surf + SUP", 120, WHITE), ("On the Konark coast, with certified instructors", 52, MUTED)], "DAY 4 · NEW", 0.5),
        reel_frame([("Chilika Lake", 110, WHITE), ("Boat ride + ecosystem learning", 52, MUTED)], "DAY 5", 0.7),
        reel_frame([("Come back", 120, WHITE), ("changed.", 120, grad_color(0.85))], "DAY 6", 0.9),
        reel_frame([("Age 10+  ·  6 days / 5 nights", 52, MUTED)], "THE ODISHA EXPERIENCE", 0.2, big_logo=True,
                   cta="DM us “ODISHA”"),
    ]
    tmp = f"{OUT}/_reel"; os.makedirs(tmp, exist_ok=True)
    for i, s in enumerate(scenes): s.save(f"{tmp}/s{i}.png")
    dur, fade = 2.3, 0.4
    inputs = []
    for i in range(len(scenes)):
        d = dur + (1.2 if i == len(scenes) - 1 else 0)
        inputs += ["-i", f"{tmp}/s{i}.png"]
    # slow zoom on each scene, then crossfade chain
    fc, prev, offset = [], None, 0.0
    for i in range(len(scenes)):
        d = dur + (1.2 if i == len(scenes) - 1 else 0)
        n = int(d * 30)
        fc.append(f"[{i}:v]scale=1188:2112,zoompan=z='min(1+0.0015*on,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={n}:s=1080x1920:fps=30,format=yuv420p,setsar=1[v{i}]")
    prev = "v0"; offset = dur - fade
    for i in range(1, len(scenes)):
        out = f"x{i}"
        fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={fade}:offset={offset:.2f}[{out}]")
        prev = out; offset += dur - fade
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + inputs + [
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-filter_complex", ";".join(fc), "-map", f"[{prev}]", "-map", f"{len(scenes)}:a",
        "-shortest", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30",
        "-b:v", "6M", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", f"{OUT}/reel.mp4"]
    subprocess.run(cmd, check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{tmp}/s7.png", "-q:v", "2", f"{OUT}/reel_cover.jpg"], check=True)

make_post(); make_stories(); make_reel()
print("done")
