"""Wall textures, flats and sky. Painted in palette RGB (base colours + their fog shades),
so quantisation is exact. Patterns are tileable."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw

from common import *  # noqa: F401,F403
import doomgfx as g


def C_(c, s=0):
    return tuple(int(v) for v in g.PAL[g.idx(c, s)])


def new(w, h, c, s=0):
    return Image.new("RGB", (w, h), C_(c, s))


def wrap_ellipse(d, w, h, box, **kw):
    """Draw an ellipse and its wrapped copies so the texture tiles."""
    x0, y0, x1, y1 = box
    for ox in (-w, 0, w):
        for oy in (-h, 0, h):
            d.ellipse((x0 + ox, y0 + oy, x1 + ox, y1 + oy), **kw)


def wrap_line(d, w, h, pts, **kw):
    for ox in (-w, 0, w):
        for oy in (-h, 0, h):
            d.line([(x + ox, y + oy) for x, y in pts], **kw)


def cell_blob(d, w, h, x, y, r, body, rim, nucleus=None, face=False, hi=None):
    wrap_ellipse(d, w, h, (x - r, y - r, x + r, y + r), fill=rim)
    wrap_ellipse(d, w, h, (x - r + 1, y - r + 1, x + r - 1, y + r - 1), fill=body)
    if hi:
        wrap_ellipse(d, w, h, (x - r + 2, y - r + 2, x - r + 3, y - r + 3), fill=hi)
    if nucleus:
        rn = max(1, r // 3)
        wrap_ellipse(d, w, h, (x - rn, y - rn + 1, x + rn, y + rn + 1), fill=nucleus)


# ---------------------------------------------------------------- lymph node

def lymph_wall():
    w, h = 64, 128
    im = new(w, h, NAVY, 3)
    d = ImageDraw.Draw(im)
    rnd = random.Random(1)
    # reticular fibres
    for _ in range(18):
        x, y = rnd.randrange(w), rnd.randrange(h)
        pts = [(x, y)]
        for _ in range(4):
            x += rnd.randint(-14, 14); y += rnd.randint(-14, 14)
            pts.append((x, y))
        wrap_line(d, w, h, pts, fill=C_(LAV, 7), width=1)
    # packed lymphocytes (dim heroes in their home)
    for _ in range(26):
        x, y = rnd.randrange(w), rnd.randrange(h)
        r = rnd.choice((3, 4, 4, 5))
        cell_blob(d, w, h, x, y, r, C_(LGREY, 6), C_(GREEN, 9) if rnd.random() < 0.3 else C_(BLUE, 9),
                  nucleus=C_(LAV, 8))
    return im


def lymph_capsule():
    w, h = 64, 128
    im = new(w, h, PEACH, 7)
    d = ImageDraw.Draw(im)
    for band in range(0, h, 8):
        pts = [(x, band + 2.5 * math.sin(2 * math.pi * x / 64 * 2 + band * 0.3)) for x in range(0, w + 1, 2)]
        d.line(pts, fill=C_(PINK, 6), width=2)
        pts = [(x, band + 4 + 2 * math.sin(2 * math.pi * x / 64 + band)) for x in range(0, w + 1, 2)]
        d.line(pts, fill=C_(BROWN, 6), width=1)
    rnd = random.Random(2)
    for _ in range(14):
        x, y = rnd.randrange(w), rnd.randrange(h)
        d.line([(x, y), (x + 5, y)], fill=C_(BROWN, 8))
        d.point((x + 2, y - 1), fill=C_(LAV, 7))
    return im


# ---------------------------------------------------------------- bloodstream

def vessel_wall():
    """Endothelium: elongated cobblestone cells with nuclei."""
    w, h = 128, 128
    im = new(w, h, PLUM, 6)
    d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for row in range(0, h, 16):
        off = (row // 16) % 2 * 16
        for col in range(-32, w + 32, 32):
            x, y = col + off + rnd.randint(-3, 3), row + 8 + rnd.randint(-2, 2)
            rx, ry = 15 + rnd.randint(-2, 2), 7
            wrap_ellipse(d, w, h, (x - rx, y - ry, x + rx, y + ry), fill=C_(PINK, 7), outline=C_(PLUM, 9))
            wrap_ellipse(d, w, h, (x - 4, y - 2, x + 4, y + 2), fill=C_(LAV, 7))
            d.point((x - rx + 4, y - 3), fill=C_(PEACH, 6))
    return im


def vessel_muscle():
    w, h = 64, 128
    im = new(w, h, BROWN, 7)
    d = ImageDraw.Draw(im)
    for y in range(0, h, 6):
        d.line([(0, y), (w, y + 3)], fill=C_(PINK, 7), width=2)
        for x in range(0, w, 16):
            d.ellipse((x + (y * 3) % 16, y, x + (y * 3) % 16 + 6, y + 2), fill=C_(PLUM, 7))
    # internal elastic lamina: a bright wavy line
    for k in (40, 104):
        pts = [(x, k + 2 * math.sin(x * 2 * math.pi / 32)) for x in range(0, w + 1)]
        d.line(pts, fill=C_(PEACH, 4), width=1)
    return im


# ---------------------------------------------------------------- tumor

def tumor_wall():
    w, h = 128, 128
    im = new(w, h, PLUM, 9)
    d = ImageDraw.Draw(im)
    rnd = random.Random(4)
    pts = []
    for _ in range(46):
        pts.append((rnd.randrange(w), rnd.randrange(h), rnd.choice((6, 7, 8, 9))))
    for x, y, r in pts:
        cell_blob(d, w, h, x, y, r, C_(PLUM, 5), C_(RED, 7), hi=C_(PINK, 7))
    # a few tiny angry faces in the mass
    for x, y, r in pts[::6]:
        for ox in (-w, 0, w):
            for oy in (-h, 0, h):
                X, Y = x + ox, y + oy
                d.point((X - 3, Y - 2), fill=C_(BLACK)); d.point((X + 2, Y - 2), fill=C_(BLACK))
                d.point((X - 2, Y - 1), fill=C_(RED, 3)); d.point((X + 1, Y - 1), fill=C_(RED, 3))
                d.line([(X - 1, Y + 2), (X + 1, Y + 2)], fill=C_(BLACK))
    return im


def tumor_stroma():
    w, h = 64, 128
    im = new(w, h, NAVY, 6)
    d = ImageDraw.Draw(im)
    for k in range(6):
        x0 = k * 11 + 3
        pts = [(x0 + 3 * math.sin(y * 2 * math.pi / 64 + k), y) for y in range(0, h + 1, 2)]
        d.line(pts, fill=C_(BROWN, 5), width=3)
        pts = [(x0 + 1 + 3 * math.sin(y * 2 * math.pi / 64 + k + 0.6), y) for y in range(0, h + 1, 2)]
        d.line(pts, fill=C_(PEACH, 6), width=1)
    return im


def necrotic_wall():
    w, h = 64, 128
    im = new(w, h, DGREY, 8)
    d = ImageDraw.Draw(im)
    rnd = random.Random(5)
    for _ in range(40):
        x, y = rnd.randrange(w), rnd.randrange(h)
        r = rnd.randint(1, 3)
        wrap_ellipse(d, w, h, (x - r, y - r, x + r, y + r), fill=rnd.choice([C_(LAV, 8), C_(PLUM, 9), C_(DGREEN, 9)]))
    return im


# ---------------------------------------------------------------- shared tech (cell parts)

def door(emblem=None):
    """Membrane gate. emblem: None or (MHC colour, peptide colour) for keyed doors."""
    w, h = 64, 128
    im = new(w, h, LGREY, 9)
    d = ImageDraw.Draw(im)
    # bilayer bands framing the gate
    for x in (0, 1, 2, 61, 62, 63):
        d.line([(x, 0), (x, h)], fill=C_(PEACH, 5) if x in (0, 63) else C_(LGREY, 6))
    for y in range(4, h, 6):
        d.line([(4, y), (59, y)], fill=C_(WHITE, 8))
    # tight junction seam
    d.line([(31, 0), (31, h)], fill=C_(BLACK)); d.line([(32, 0), (32, h)], fill=C_(GREEN, 5))
    if emblem:
        mc, pc = emblem
        cx, cy = 32, 64
        d.rectangle((cx - 13, cy - 22, cx + 13, cy + 22), fill=C_(NAVY, 2))
        d.rectangle((cx - 8, cy - 12, cx + 8, cy - 2), fill=C_(mc))
        d.rectangle((cx - 2, cy - 2, cx + 2, cy + 16), fill=C_(mc))
        d.rectangle((cx - 5, cy - 18, cx + 5, cy - 13), fill=C_(pc))
        d.rectangle((cx - 13, cy - 22, cx + 13, cy + 22), outline=C_(mc))
    return im


def door_track():
    im = new(8, 128, DGREY, 6)
    d = ImageDraw.Draw(im)
    for y in range(0, 128, 4):
        d.line([(0, y), (7, y)], fill=C_(LGREY, 7))
    return im


def receptor_switch(on=False, label=None):
    w, h = 64, 128
    im = lymph_capsule() if label is None else new(w, h, DGREY, 9)
    d = ImageDraw.Draw(im)
    cx, cy = 32, 72
    d.rectangle((cx - 14, cy - 22, cx + 14, cy + 22), fill=C_(BLACK), outline=C_(LGREY, 4))
    col = C_(GREEN) if on else C_(LGREY, 6)
    # receptor (Y fork) socket
    d.line([(cx, cy + 14), (cx, cy - 2)], fill=col, width=3)
    d.line([(cx, cy - 2), (cx - 9, cy - 13)], fill=col, width=3)
    d.line([(cx, cy - 2), (cx + 9, cy - 13)], fill=col, width=3)
    if on:
        d.ellipse((cx - 3, cy - 17, cx + 3, cy - 11), fill=C_(YELLOW))
    if label:
        txt(im, cx, 26, label, YELLOW if on else ORANGE, ORANGE if on else BROWN)
    return im


def txt(im, cx, y, s, col, shade, k=1):
    from pixel_kit.font import TITLE_GLYPHS
    d = ImageDraw.Draw(im)
    wpx = len(s) * 6 * k - k
    x0 = cx - wpx // 2
    for n, ch in enumerate(s):
        for r, row in enumerate(TITLE_GLYPHS[ch]):
            for q, b in enumerate(row):
                if b == "#":
                    x, yy = x0 + (n * 6 + q) * k, y + r * k
                    d.rectangle([x + 1, yy + 1, x + k, yy + k], fill=C_(BLACK))
                    d.rectangle([x, yy, x + k - 1, yy + k - 1], fill=C_(col if r < 4 else shade))


def exit_sign():
    im = new(64, 16, BLACK)
    txt(im, 32, 4, "EXIT", GREEN, DGREEN)
    return im


def step_side():
    im = new(64, 16, PEACH, 6)
    d = ImageDraw.Draw(im)
    d.line([(0, 0), (64, 0)], fill=C_(WHITE, 5))
    for x in range(0, 64, 8):
        d.ellipse((x, 4, x + 6, 10), fill=C_(PINK, 6))
    return im


def sky():
    w, h = 256, 128
    im = new(w, h, NAVY, 10)
    d = ImageDraw.Draw(im)
    rnd = random.Random(9)
    for _ in range(40):
        x, y = rnd.randrange(w), rnd.randrange(20, h)
        r = rnd.randint(4, 14)
        c = rnd.choice([C_(PINK, 11), C_(LAV, 11), C_(PLUM, 10), C_(BLUE, 12)])
        wrap_ellipse(d, w, 10 ** 6, (x - r, y - r, x + r, y + r), fill=c)
    for y in range(0, 24):
        d.line([(0, y), (w, y)], fill=C_(NAVY, 12))
    return im


# ---------------------------------------------------------------- flats (64x64)

def flat_lymph():
    im = new(64, 64, NAVY, 5)
    d = ImageDraw.Draw(im)
    rnd = random.Random(11)
    for _ in range(30):
        x, y = rnd.randrange(64), rnd.randrange(64)
        cell_blob(d, 64, 64, x, y, rnd.choice((3, 4)), C_(LGREY, 6), C_(LAV, 7), nucleus=C_(LAV, 9))
    return im


def flat_lymph_ceil():
    im = lymph_wall().crop((0, 0, 64, 64))
    return Image.eval(im, lambda v: v)


def flat_blood(frame=0):
    im = new(64, 64, PLUM, 8)
    d = ImageDraw.Draw(im)
    rnd = random.Random(12)
    for i in range(14):
        x, y = rnd.randrange(64), rnd.randrange(64)
        y = (y + frame * 21) % 64  # flows along +y between frames
        rx, ry = 6, 4
        wrap_ellipse(d, 64, 64, (x - rx, y - ry, x + rx, y + ry), fill=C_(PINK, 5), outline=C_(PLUM, 6))
        wrap_ellipse(d, 64, 64, (x - 2, y - 1, x + 2, y + 1), fill=C_(PLUM, 4))
    return im


def flat_vessel_ceil():
    return vessel_wall().crop((0, 0, 64, 64))


def flat_tumor():
    return tumor_wall().crop((0, 0, 64, 64))


def flat_stroma():
    return tumor_stroma().crop((0, 0, 64, 64))


def flat_necro(frame=0):
    im = new(64, 64, DGREEN, 9)
    d = ImageDraw.Draw(im)
    rnd = random.Random(13)
    for i in range(16):
        x, y = rnd.randrange(64), rnd.randrange(64)
        r = 2 + (i + frame) % 4
        wrap_ellipse(d, 64, 64, (x - r, y - r, x + r, y + r), outline=C_(GREEN, 6 - (i + frame) % 3), fill=C_(DGREEN, 7))
    return im


def flat_light():
    im = new(64, 64, PEACH, 3)
    d = ImageDraw.Draw(im)
    d.ellipse((6, 6, 58, 58), fill=C_(WHITE), outline=C_(PEACH, 1))
    d.ellipse((20, 20, 44, 44), fill=C_(YELLOW, 1))
    return im


def flat_step():
    im = new(64, 64, PEACH, 6)
    d = ImageDraw.Draw(im)
    for y in range(0, 64, 8):
        d.line([(0, y), (64, y)], fill=C_(PINK, 7))
    return im


def flat_exit():
    im = new(64, 64, DGREEN, 6)
    d = ImageDraw.Draw(im)
    d.rectangle((4, 4, 59, 59), outline=C_(GREEN), width=3)
    d.line([(16, 34), (28, 46), (48, 18)], fill=C_(WHITE), width=5)
    return im


def flat_border():
    """Screen border (when the view is shrunk): the bible's navy grid."""
    im = new(64, 64, NAVY, 6)
    d = ImageDraw.Draw(im)
    for k in range(0, 64, 8):
        d.line([(k, 0), (k, 63)], fill=C_(NAVY, 4))
        d.line([(0, k), (63, k)], fill=C_(NAVY, 4))
    return im


def flat_door():
    return new(64, 64, LGREY, 9)


WALLS = {
    "LNWALL1": lymph_wall,
    "LNWALL2": lymph_capsule,
    "BVWALL1": vessel_wall,
    "BVWALL2": vessel_muscle,
    "TMWALL1": tumor_wall,
    "TMWALL2": tumor_stroma,
    "TMWALL3": necrotic_wall,
    "DOORM1": lambda: door(None),
    "DOORMW": lambda: door((WHITE, LGREY)),
    "DOORMY": lambda: door((YELLOW, WHITE)),
    "DOORMO": lambda: door((YELLOW, ORANGE)),
    "DOORTRK": door_track,
    "SW1RCPT": lambda: receptor_switch(False),
    "SW2RCPT": lambda: receptor_switch(True),
    "SW1EXIT": lambda: receptor_switch(False, "EXIT"),
    "SW2EXIT": lambda: receptor_switch(True, "EXIT"),
    "EXITSIGN": exit_sign,
    "STEPSIDE": step_side,
    "SKY1": sky,
}

FLATS = {
    "LNFLOOR": flat_lymph,
    "LNCEIL": flat_lymph_ceil,
    "BVFLOR1": lambda: flat_blood(0),
    "BVFLOR2": lambda: flat_blood(1),
    "BVFLOR3": lambda: flat_blood(2),
    "BVCEIL": flat_vessel_ceil,
    "TMFLOOR": flat_tumor,
    "TMCEIL": flat_stroma,
    "NECRO1": lambda: flat_necro(0),
    "NECRO2": lambda: flat_necro(1),
    "NECRO3": lambda: flat_necro(2),
    "LIGHTF": flat_light,
    "STEPF": flat_step,
    "EXITPAD": flat_exit,
    "DOORTOP": flat_door,
    "F_SKY1": lambda: new(64, 64, NAVY, 10),
    "FLOOR7_2": lambda: flat_border(),
    "FLOOR4_6": lambda: flat_border(),
    "FLOOR4_8": lambda: flat_border(),
    "MFLR8_4": lambda: flat_border(),
}

ANIMATED = [  # (is_texture, first, last, tics)
    (0, "BVFLOR1", "BVFLOR3", 8),
    (0, "NECRO1", "NECRO3", 10),
]
SWITCHES = [("SW1RCPT", "SW2RCPT"), ("SW1EXIT", "SW2EXIT")]
