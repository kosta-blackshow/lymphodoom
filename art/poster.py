"""The LYMPHODOOM poster in the spirit of the 1993 Doom box: a big flared metal logo,
the killer T cell on top of a heap of burst germs, the infection climbing at it,
the tumour mass looming in a red glow. 320x160 bible-scale pixels, saved x4 (1280x640).
Used as the README image and as the page's og:image."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw

from common import *  # noqa: F401,F403
import monsters
from pixel_kit.font import TITLE_GLYPHS
from ui import RGBA, blank, paste_spr, ps_text

W, H = 320, 160


def background():
    im = blank(W, H, BLACK)
    a = np.zeros((H, W, 4), np.uint8)
    cx, cy = 160, 150
    for y in range(H):
        for x in range(W):
            # red-orange glow from behind the heap, fading into plum and black
            r = math.hypot((x - cx) / 1.6, (y - cy) * 1.0) / 170.0
            r += 0.05 * math.sin(x * 0.21 + y * 0.13) * math.sin(y * 0.17)
            if r < 0.28:
                c = RGBA(ORANGE, int(r / 0.28 * 6))
            elif r < 0.55:
                c = RGBA(RED, int((r - 0.28) / 0.27 * 9))
            elif r < 0.85:
                c = RGBA(PLUM, int((r - 0.55) / 0.3 * 10))
            else:
                c = RGBA(PLUM, min(15, 10 + int((r - 0.85) * 20)))
            a[y, x] = c
    im = Image.fromarray(a, "RGBA")
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    # tissue arches on both sides (dark organic walls with pink vessels)
    for side in (0, 1):
        for i in range(7):
            x0 = (0 if side == 0 else W) + (1 if side == 0 else -1) * rnd.randint(-10, 60)
            y0 = rnd.randint(30, 150)
            rr = rnd.randint(18, 40)
            d.ellipse((x0 - rr, y0 - rr, x0 + rr, y0 + rr), fill=RGBA(PLUM, 12 + rnd.randint(0, 2)))
        for i in range(4):
            pts = []
            x = (8 if side == 0 else W - 8) + rnd.randint(-6, 6)
            y = rnd.randint(40, 70)
            for k in range(9):
                pts.append((x, y))
                x += (1 if side == 0 else -1) * rnd.randint(2, 9)
                y += rnd.randint(6, 14)
            d.line(pts, fill=RGBA(PINK, 9), width=1)
    # embers / floating cells
    for i in range(70):
        x, y = rnd.randint(0, W - 1), rnd.randint(46, H - 1)
        col = rnd.choice([YELLOW, ORANGE, PINK, RED])
        d.point((x, y), fill=RGBA(col, rnd.randint(0, 4)))
    return im


def metal_logo(text="LYMPHODOOM", k=5):
    """Doom-style flared logo: straight top edge, letters growing taller towards both ends,
    a hot metal gradient, a thick dark extrusion and a black outline."""
    w = len(text) * 6 * k - k
    h0 = 7 * k
    m = np.zeros((h0, w), bool)
    for n, ch in enumerate(text):
        for r, row in enumerate(TITLE_GLYPHS[ch]):
            for q, b in enumerate(row):
                if b == "#":
                    x, y = (n * 6 + q) * k, r * k
                    m[y:y + k, x:x + k] = True
    flare = 0.55
    Hmax = int(h0 * (1 + flare)) + 1
    out = np.zeros((Hmax, w), np.float32) - 1  # relative height of the glyph pixel, -1 = empty
    c = (w - 1) / 2
    for x in range(w):
        f = 1 + flare * (abs(x - c) / c) ** 1.6
        hh = int(round(h0 * f))
        for y in range(hh):
            sy = int(y / f)
            if sy < h0 and m[sy, x]:
                out[y, x] = y / Hmax
    fill = out >= 0
    ext = 5
    pad = 3
    Wt, Ht = w + 2 * pad + ext, Hmax + 2 * pad + ext
    canvas = np.zeros((Ht, Wt, 4), np.uint8)

    def stamp(mask, color, dx, dy):
        ys, xs = np.nonzero(mask)
        canvas[ys + pad + dy, xs + pad + dx] = color

    # extrusion (down-right), darker towards the back
    for e in range(ext, 0, -1):
        stamp(fill, RGBA(BROWN, 6 + e), e, e)
    # outline around face + extrusion
    occ = canvas[..., 3] > 0
    face = np.zeros_like(occ)
    face[pad:pad + Hmax, pad:pad + w] = fill
    allm = occ | face
    grow = allm.copy()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        grow |= np.roll(np.roll(allm, dy, 0), dx, 1)
    edge = grow & ~allm
    canvas[edge] = RGBA(BLACK)
    # face: hot metal gradient
    bands = [(0.08, WHITE, 0), (0.24, YELLOW, 0), (0.40, YELLOW, 2), (0.54, ORANGE, 0),
             (0.68, ORANGE, 3), (0.82, RED, 0), (1.01, RED, 4)]
    ys, xs = np.nonzero(fill)
    for y, x in zip(ys, xs):
        t = out[y, x]
        for lim, col, s in bands:
            if t < lim:
                canvas[y + pad, x + pad] = RGBA(col, s)
                break
    # a bevel: darken the right/bottom edge pixels of each stroke
    for y, x in zip(ys, xs):
        if (x + 1 >= w or not fill[y, x + 1]) or (y + 1 >= Hmax or not fill[y + 1, x]):
            r, g_, b, _ = canvas[y + pad, x + pad]
            canvas[y + pad, x + pad] = (int(r * 0.6), int(g_ * 0.6), int(b * 0.6), 255)
        if (x == 0 or not fill[y, x - 1]) or (y == 0 or not fill[y - 1, x]):
            canvas[y + pad, x + pad] = RGBA(WHITE) if out[y, x] < 0.5 else RGBA(YELLOW)
    return Image.fromarray(canvas, "RGBA")


def shot(d, x0, y0, x1, y1, n=6):
    for i in range(n):
        t = (i + 0.5) / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=RGBA(GREEN))
        d.point((x, y), fill=RGBA(WHITE))


def poster():
    im = background()
    rnd = random.Random(3)

    # the boss looms behind, in the glow
    boss = monsters._mass()
    paste_spr(im, boss, 232, 52, 2)

    # the heap: burst germs and their puddles under the hero
    d = ImageDraw.Draw(im)
    mound = [(78, 160), (92, 134), (114, 124), (142, 119), (178, 119), (206, 125), (228, 138), (242, 160)]
    d.polygon(mound, fill=RGBA(PLUM, 9), outline=RGBA(BLACK))
    for spr, x, y in [(monsters._virus(), 94, 126), (monsters._bacterium(), 180, 122),
                      (monsters._tumor(), 120, 128), (monsters._virus(1), 208, 130),
                      (monsters._parasite(), 146, 132)]:
        dead = spr.recolor({c: (DGREY if c in (WHITE, LGREY, PEACH, YELLOW) else PLUM)
                            for c in range(16) if c != BLACK})
        paste_spr(im, dead, x, y, 1)
    for i in range(30):
        x, y = rnd.randint(90, 232), rnd.randint(122, 146)
        col = rnd.choice([PINK, RED, ORANGE])
        rr = rnd.randint(1, 3)
        d.ellipse((x - rr, y - 1, x + rr, y + 1), fill=RGBA(col, rnd.randint(0, 2)))
    d.ellipse((132, 119, 188, 126), fill=RGBA(PLUM, 14))

    # the infection climbing at the hero
    foes = [(monsters._spore(), 2, 56, 2), (monsters._tumor(), 66, 100, 2),
            (monsters._bacterium(), 2, 122, 2), (monsters._phage(), 274, 64, 2),
            (monsters._parasite(), 234, 120, 2), (monsters._virus(), 166, 44, 1)]
    for spr, x, y, k in foes:
        paste_spr(im, spr, x, y, k)

    # the hero: killer T cell on top, firing at the tumour on the left
    hero = cast.t_cell("cd8", look=-1, alert=True)
    paste_spr(im, hero, 122, 54, 4)
    d = ImageDraw.Draw(im)
    shot(d, 120, 100, 100, 116, 4)
    shot(d, 122, 92, 62, 86, 8)
    d.ellipse((115, 94, 125, 104), fill=RGBA(WHITE))
    d.ellipse((117, 96, 123, 102), fill=RGBA(YELLOW))

    # the logo
    lg = metal_logo("LYMPHODOOM", 4)
    if lg.width > W - 8:
        lg = lg.resize((W - 8, int(lg.height * (W - 8) / lg.width)), Image.NEAREST)
    im.alpha_composite(lg, ((W - lg.width) // 2, 3))

    # tagline strip
    d.rectangle((0, H - 13, W, H), fill=RGBA(BLACK))
    tag = ps_text("THE BODY IS INFECTED. YOU ARE THE CURE.", YELLOW, ORANGE, None, k=1)
    im.alpha_composite(tag, ((W - tag.width) // 2, H - 11))
    return im


def save(path):
    poster().convert("RGB").resize((W * 4, H * 4), Image.NEAREST).save(path, optimize=True)


if __name__ == "__main__":
    import sys
    save(sys.argv[1] if len(sys.argv) > 1 else "poster.png")
