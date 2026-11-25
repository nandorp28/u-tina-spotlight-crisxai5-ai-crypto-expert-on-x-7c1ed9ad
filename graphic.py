#!/usr/bin/env python3
"""Render spotlight.png — a dense 1200x675 spotlight card for @crisxai5.

Drawn from scratch with Pillow (stdlib-adjacent, no downloads, no copied
assets). Layout: dark navy, candlestick + network-node texture, hero handle,
four topic chips, 2x2 "why follow" cards, ticker strip, follow CTA.
Run: python3 graphic.py  ->  writes spotlight.png next to this file.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 675
OUT = "spotlight.png"

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_BOLD = lambda s: ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", s)
F_REG = lambda s: ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", s)
F_MONO = lambda s: ImageFont.truetype(FONT_DIR + "DejaVuSansMono.ttf", s)
F_MONO_B = lambda s: ImageFont.truetype(FONT_DIR + "DejaVuSansMono-Bold.ttf", s)

BG_TOP = (7, 13, 26)
BG_BOT = (13, 27, 46)
CYAN = (34, 211, 238)
GREEN = (52, 211, 153)
GREEN_DIM = (16, 120, 90)
WHITE = (242, 246, 255)
MUTED = (147, 164, 196)
FAINT = (100, 116, 150)
RED = (244, 113, 116)
CARD_FILL = (255, 255, 255, 14)
CARD_EDGE = (34, 211, 238, 90)

rng = random.Random(20261125)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw, xy, s, font, fill):
    draw.text(xy, s, font=font, fill=fill)


def text_w(draw, s, font):
    box = draw.textbbox((0, 0), s, font=font)
    return box[2] - box[0]


def spaced(draw, xy, s, font, fill, gap=6):
    """Draw text with extra tracking between letters."""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=font, fill=fill)
        x += text_w(draw, ch, font) + gap
    return x


def main():
    img = Image.new("RGB", (W, H), BG_TOP)
    d = ImageDraw.Draw(img, "RGBA")

    # --- vertical gradient background ---
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp(BG_TOP, BG_BOT, y / H))

    # --- dot grid texture ---
    for gx in range(24, W, 34):
        for gy in range(24, H, 34):
            d.ellipse([gx, gy, gx + 2, gy + 2], fill=(255, 255, 255, 14))

    # --- glow blobs (concentric translucent circles) ---
    for cx, cy, r0, col in [(1010, 90, 260, (34, 211, 238)), (120, 620, 220, (52, 211, 153))]:
        for r in range(r0, 0, -14):
            a = max(0, 26 - int(26 * (r0 - r) / r0) - 8)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (a,))

    # --- candlestick chart across the lower band (decorative texture) ---
    # Kept inside the gap band (y 540-595) between the cards and the bottom bar.
    base_y = 575
    x = 30
    price = 568
    while x < W - 30:
        cw = rng.choice([10, 12, 14])
        o = price
        c = price + rng.randint(-10, 10)
        up = c < o
        col = GREEN if up else RED
        hi = min(o, c) - rng.randint(3, 6)
        lo = max(o, c) + rng.randint(3, 6)
        d.line([(x + cw // 2, hi), (x + cw // 2, lo)], fill=col + (150,), width=2)
        d.rectangle([x, min(o, c), x + cw, max(o, c)], fill=col + (110,))
        price = c
        x += cw + rng.randint(8, 16)
    # rising sparkline over the candles, staying in the gap band
    pts = []
    px, py = 40, 588
    while px < W - 40:
        pts.append((px, py))
        px += 46
        py -= rng.randint(1, 2)
    d.line(pts, fill=CYAN + (220,), width=3, joint="curve")
    for p in pts[::3]:
        d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=CYAN + (255,))

    # --- neural-node network, top right ---
    nodes = [(880, 96), (990, 60), (1085, 110), (940, 150), (1050, 185),
             (1130, 60), (860, 180), (1010, 215)]
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if math.hypot(a[0] - b[0], a[1] - b[1]) < 190:
                d.line([a, b], fill=CYAN + (70,), width=1)
    for n in nodes:
        r = rng.randint(4, 7)
        d.ellipse([n[0] - r, n[1] - r, n[0] + r, n[1] + r],
                  fill=GREEN + (230,), outline=WHITE + (160,), width=1)

    # --- top ticker strip ---
    tick = "BTC  ▲   ETH  ▲   SOL  ▲   AI AGENTS  •  WEB3  •  ON-CHAIN  •  CRYPTO  •  "
    d.rectangle([0, 0, W, 30], fill=(0, 0, 0, 90))
    text(d, (18, 7), tick * 2, F_MONO(15), (120, 200, 220, 255))
    d.line([(0, 30), (W, 30)], fill=CYAN + (120,), width=1)

    # --- SPOTLIGHT pill ---
    pill = "★  SPOTLIGHT  •  MUST-FOLLOW ON X"
    pw = text_w(d, pill, F_BOLD(21)) + 36
    rounded(d, [56, 52, 56 + pw, 92], 20, fill=(34, 211, 238, 36),
            outline=CYAN + (200,), width=2)
    text(d, (74, 62), pill, F_BOLD(21), WHITE)

    # --- hero handle ---
    text(d, (54, 108), "@crisxai5", F_BOLD(108), WHITE)
    d.line([(58, 232), (58 + text_w(d, "@crisxai5", F_BOLD(108)), 232)],
           fill=GREEN + (220,), width=5)

    # --- subhead ---
    spaced(d, (58, 252), "AI  ×  CRYPTO  EXPERT", F_BOLD(40), GREEN, gap=4)

    # --- tagline ---
    text(d, (58, 306), "The follow that filters the noise.", F_REG(30), MUTED)

    # --- 2x2 why-follow cards ---
    cards = [
        ("AI AGENTS", "explained in plain English"),
        ("CRYPTO INSIGHTS", "alpha without the hype"),
        ("WEB3 INNOVATION", "tooling that actually ships"),
        ("ON-CHAIN AUTOMATION", "decoded, step by step"),
    ]
    cx0, cy0, cw, ch, gapx, gapy = 56, 356, 316, 84, 16, 14
    for i, (title, sub) in enumerate(cards):
        x = cx0 + (i % 2) * (cw + gapx)
        y = cy0 + (i // 2) * (ch + gapy)
        rounded(d, [x, y, x + cw, y + ch], 14, fill=CARD_FILL,
                outline=CARD_EDGE, width=1)
        d.rectangle([x, y + 10, x + 5, y + ch - 10], fill=GREEN + (255,))
        text(d, (x + 18, y + 12), title, F_BOLD(21), WHITE)
        text(d, (x + 18, y + 44), sub, F_REG(20), MUTED)

    # --- right rail: signal panel ---
    rx0, ry0, rw, rh = 780, 356, 364, 182
    rounded(d, [rx0, ry0, rx0 + rw, ry0 + rh], 14, fill=(0, 0, 0, 70),
            outline=CYAN + (140,), width=1)
    text(d, (rx0 + 20, ry0 + 14), "ON THE FEED", F_MONO_B(19), CYAN)
    feed = [
        ("▸", "AI agents that do the work"),
        ("▸", "Crypto, minus the noise"),
        ("▸", "Web3 tools worth your time"),
        ("▸", "On-chain, explained simply"),
    ]
    for j, (mark, line) in enumerate(feed):
        y = ry0 + 46 + j * 33
        text(d, (rx0 + 20, y), mark, F_BOLD(20), GREEN)
        text(d, (rx0 + 48, y), line, F_REG(21), WHITE)

    # --- bottom bar: link + follow CTA ---
    d.rectangle([0, 596, W, 675], fill=(0, 0, 0, 110))
    d.line([(0, 596), (W, 596)], fill=CYAN + (140,), width=1)
    text(d, (56, 622), "x.com/crisxai5", F_MONO_B(30), WHITE)
    cta = "FOLLOW  @crisxai5  →"
    cw2 = text_w(d, cta, F_BOLD(26)) + 44
    rounded(d, [W - 56 - cw2, 612, W - 56, 656], 22, fill=GREEN + (255,))
    text(d, (W - 56 - cw2 + 22, 622), cta, F_BOLD(26), (4, 20, 14))

    img.save(OUT, optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
