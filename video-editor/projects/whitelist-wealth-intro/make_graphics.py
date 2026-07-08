#!/usr/bin/env python3
"""Author branded graphic overlays (no transcript needed) for the Whitelist Wealth
first draft: intro title card, persistent logo bug, stat callout. Full-frame 1920x1080
RGBA PNGs; ffmpeg composites them with fade + enable-timing (see run in shell)."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1920, 1080
FONTS = "assets/fonts"
OUT = "projects/whitelist-wealth-intro/assets"
os.makedirs(OUT, exist_ok=True)

GREEN = (18, 161, 80, 255)
GOLD  = (212, 167, 44, 255)
INK   = (16, 21, 28)
LIGHT = (247, 248, 250, 255)
MUTED = (168, 176, 188, 255)

def f(name, size): return ImageFont.truetype(f"{FONTS}/{name}", size)
black = lambda s: f("Inter-Black.otf", s)
bold  = lambda s: f("Inter-Bold.otf", s)
reg   = lambda s: f("Inter-Regular.otf", s)

def new(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def wtext(d, xy, s, font):  # measured width
    b = d.textbbox((0, 0), s, font=font); return b[2]-b[0]

# ---------- 1. intro title card (bottom lower-third) ----------
img = new(); d = ImageDraw.Draw(img)
px0, py0, px1, py1 = 80, 792, 1180, 984
d.rounded_rectangle([px0, py0, px1, py1], radius=26, fill=INK + (214,))
d.rounded_rectangle([px0, py0, px0+12, py1], radius=6, fill=GREEN)  # left accent
tf = black(70)
tx, ty = px0 + 52, py0 + 34
w1 = wtext(d, (0,0), "WHITELIST ", tf)
d.text((tx, ty), "WHITELIST ", font=tf, fill=LIGHT)
d.text((tx + w1, ty), "WEALTH", font=tf, fill=GREEN)
d.text((tx + 3, ty + 96), "Get paid to make short-form videos for brands",
       font=reg(31), fill=MUTED)
img.save(f"{OUT}/title_card.png")

# ---------- 2. persistent logo bug (top-right pill) ----------
img = new(); d = ImageDraw.Draw(img)
lf = bold(28); label = "WHITELIST WEALTH"
lw = wtext(d, (0,0), label, lf); padx, pady = 26, 14
pw, ph = lw + 2*padx, 30 + 2*pady
x0 = W - 44 - pw; y0 = 40
d.rounded_rectangle([x0, y0, x0+pw, y0+ph], radius=ph//2, fill=INK + (200,))
d.rounded_rectangle([x0, y0, x0+pw, y0+ph], radius=ph//2, outline=GREEN, width=2)
d.ellipse([x0+padx-2, y0+ph//2-6, x0+padx+10, y0+ph//2+6], fill=GREEN)  # green dot
d.text((x0+padx+22, y0+pady-2), label, font=lf, fill=LIGHT)
img.save(f"{OUT}/logo_bug.png")

# ---------- 3. stat callout (bottom lower-third) ----------
img = new(); d = ImageDraw.Draw(img)
d.rounded_rectangle([px0, py0, px1, py1], radius=26, fill=INK + (222,))
d.rounded_rectangle([px0, py0, px0+12, py1], radius=6, fill=GOLD)
d.text((px0+52, py0+26), "INSIDE THE COMMUNITY", font=bold(26), fill=GREEN)
stats = [("$1,101", "MRR"), ("81", "MEMBERS"), ("97%", "RETENTION")]
nf, sf = black(60), bold(26)
cols = [px0+300, px0+610, px0+900]
for cx, (num, lab) in zip(cols, stats):
    d.text((cx, py0+78), num, font=nf, fill=GOLD, anchor="ma")
    d.text((cx, py0+152), lab, font=sf, fill=MUTED, anchor="ma")
img.save(f"{OUT}/stat_callout.png")

print("wrote title_card.png, logo_bug.png, stat_callout.png ->", OUT)
