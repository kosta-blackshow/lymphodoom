"""Status bar, HUD faces, fonts, menu graphics, title, intermission map, finale, help.
All images are RGBA in palette colours."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import *  # noqa: F401,F403
import doomgfx as g
from pixel_kit.font import TITLE_GLYPHS
from pixel_kit.palette import P

HERE = os.path.dirname(os.path.abspath(__file__))
PS2P = os.path.join(HERE, "..", "vendor", "pixel_kit", "fonts", "PressStart2P-Regular.ttf")
F8 = ImageFont.truetype(PS2P, 8)


def RGB(c, s=0):
    return tuple(int(v) for v in g.PAL[g.idx(c, s)])


def RGBA(c, s=0):
    return RGB(c, s) + (255,)


def blank(w, h, c=None, s=0):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0) if c is None else RGBA(c, s))


def ps_mask(text):
    w = max(1, int(F8.getlength(text)))
    m = Image.new("L", (w, 8), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = "1"
    d.text((0, 0), text, font=F8, fill=255)
    return m


def ps_text(text, top=YELLOW, bottom=ORANGE, shadow=PLUM, k=2, split=4):
    """Press Start 2P text, k times, two-tone (top rows / bottom rows) with a drop shadow."""
    m = ps_mask(text)
    w, h = m.width * k, 8 * k
    out = blank(w + k, h + k)
    mm = m.resize((w, h), Image.NEAREST)
    if shadow is not None:
        out.paste(RGBA(shadow), (k, k), mm)
    body = blank(w, h)
    arr = np.zeros((h, w, 4), np.uint8)
    a = np.asarray(mm) > 0
    for y in range(h):
        col = RGBA(top) if y < split * k else RGBA(bottom)
        arr[y][a[y]] = col
    body = Image.fromarray(arr, "RGBA")
    out.alpha_composite(body, (0, 0))
    return out


def logo(text, k, top=YELLOW, shade=ORANGE, back=PLUM):
    w = len(text) * 6 * k - k
    img = blank(w + k, 7 * k + k)
    d = ImageDraw.Draw(img)
    for n, ch in enumerate(text):
        for r, row in enumerate(TITLE_GLYPHS[ch]):
            for q, b in enumerate(row):
                if b == "#":
                    x, yy = (n * 6 + q) * k, r * k
                    d.rectangle([x + k // 2 + 0, yy + k // 2, x + k // 2 + k - 1, yy + k // 2 + k - 1], fill=RGBA(back))
    for n, ch in enumerate(text):
        for r, row in enumerate(TITLE_GLYPHS[ch]):
            for q, b in enumerate(row):
                if b == "#":
                    x, yy = (n * 6 + q) * k, r * k
                    d.rectangle([x, yy, x + k - 1, yy + k - 1], fill=RGBA(top if r < 4 else shade))
    return img


def bg_grid(w, h, base=NAVY, s=6, line_s=4, step=8):
    im = blank(w, h, base, s)
    d = ImageDraw.Draw(im)
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=RGBA(base, line_s))
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=RGBA(base, line_s))
    return im


# ---------------------------------------------------------------- status bar

def stbar():
    im = blank(320, 32, BLACK)
    d = ImageDraw.Draw(im)
    # panels like the bible's black caption bars with coloured frames
    panels = [(0, 1, 47, 31, BLUE), (48, 1, 103, 31, GREEN), (104, 1, 143, 31, LGREY),
              (178, 1, 235, 31, PEACH), (236, 1, 248, 31, LGREY), (249, 1, 319, 31, ORANGE)]
    for x0, y0, x1, y1, c in panels:
        d.rectangle((x0, y0, x1, y1), fill=RGBA(NAVY, 12), outline=RGBA(c, 4))
    d.rectangle((144, 0, 177, 31), fill=RGBA(NAVY, 8))
    lab = [("AMMO", 24, BLUE), ("HEALTH", 76, GREEN), ("ARMOR", 207, PEACH)]
    for t, cx, c in lab:
        m = ps_mask(t)
        im.paste(RGBA(c, 2), (cx - m.width // 2, 23), m)
    # ammo table labels (tiny 3x5 font)
    for i, t in enumerate(["GRAN", "VESI", "ANTB", "IFN"]):
        tiny(im, 252, 5 + i * 6, t, [BLUE, ORANGE, WHITE, LAV][i])
        tiny(im, 302, 5 + i * 6, "/", LGREY)
    return im


TINY = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"], "F": ["###", "#..", "##.", "#..", "#.."],
    "G": [".##", "#..", "#.#", "#.#", ".##"], "I": ["###", ".#.", ".#.", ".#.", "###"],
    "N": ["#.#", "###", "###", "#.#", "#.#"], "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": [".##", "#..", ".#.", "..#", "##."], "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "V": ["#.#", "#.#", "#.#", "#.#", ".#."], "/": ["..#", "..#", ".#.", "#..", "#.."],
}


def tiny(im, x, y, t, col):
    d = ImageDraw.Draw(im)
    for n, ch in enumerate(t):
        for r, row in enumerate(TINY[ch]):
            for q, b in enumerate(row):
                if b == "#":
                    d.point((x + n * 4 + q, y + r), fill=RGBA(col))


def starms_unused():
    im = blank(40, 32, NAVY, 12)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 1, 39, 31), outline=RGBA(LGREY, 4))
    m = ps_mask("ARMS")
    im.paste(RGBA(LGREY, 2), (20 - m.width // 2, 23), m)
    return im


def starms():
    """The ARMS panel becomes BODY: the organism's health (number drawn by the engine)."""
    im = blank(40, 32, NAVY, 12)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 1, 39, 31), outline=RGBA(PINK, 4))
    m = ps_mask("BODY")
    im.paste(RGBA(PINK, 2), (20 - m.width // 2, 23), m)
    return im


def body_icon(level):
    """8x13 silhouette of a person; reddens as the body's health drops (level 0..3)."""
    col = [PEACH, PINK, RED, RED][level]
    im = blank(8, 13)
    d = ImageDraw.Draw(im)
    d.ellipse((2, 0, 5, 3), fill=RGBA(col))
    d.rectangle((1, 4, 6, 8), fill=RGBA(col))
    d.rectangle((2, 9, 3, 12), fill=RGBA(col)); d.rectangle((4, 9, 5, 12), fill=RGBA(col))
    if level == 3:
        d.point((3, 6), fill=RGBA(BLACK)); d.point((4, 6), fill=RGBA(BLACK))
    return im


def body_digit(ch, top=YELLOW, shade=ORANGE):
    """Tall narrow digit for the BODY panel: the logo font, 1 px wide, 2 px tall per dot."""
    if ch == "%":
        rows = ["##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"]
    else:
        rows = TITLE_GLYPHS.get(ch) or {
            "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
            "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
            "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
        }[ch]
    im = blank(7, 15)
    d = ImageDraw.Draw(im)
    for pass_, c in ((0, PLUM), (1, None)):
        for r, row in enumerate(rows):
            for q, b in enumerate(row):
                if b == "#":
                    x, y = q + (1 if pass_ == 0 else 0), r * 2 + (1 if pass_ == 0 else 0)
                    d.rectangle((x, y, x, y + 1), fill=RGBA(c if c is not None else (top if r < 4 else shade)))
    return im


def body_dead():
    """Game over: the body's silhouette goes grey."""
    im = blank(320, 200, BLACK)
    layer = blank(320, 260)
    _body(layer)
    arr = np.asarray(layer).copy()
    m = arr[..., 3] > 0
    arr[m, :3] = RGB(DGREY, 6)
    im.alpha_composite(Image.fromarray(arr, "RGBA").crop((0, 0, 320, 200 - 60)), (0, 60))
    lg = logo("THE BODY DIED", 3, top=RED, shade=PLUM, back=BLACK)
    im.alpha_composite(lg, ((320 - lg.width) // 2, 16))
    sub = ps_text("BACK TO THE LYMPH NODE", LGREY, LGREY, None, k=1)
    im.alpha_composite(sub, ((320 - sub.width) // 2, 186))
    return im


def big_digit(ch, top=YELLOW, shade=ORANGE):
    """14x16 status bar digit from the bible logo font (5x7 x2)."""
    if ch == "%":
        rows = ["##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"]
    else:
        rows = TITLE_GLYPHS.get(ch) or {
            "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
            "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
            "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
        }[ch]
    im = blank(12, 16)
    d = ImageDraw.Draw(im)
    for r, row in enumerate(rows):
        for q, b in enumerate(row):
            if b == "#":
                x, y = q * 2, r * 2
                d.rectangle([x + 1, y + 1, x + 2, y + 2], fill=RGBA(PLUM))
    for r, row in enumerate(rows):
        for q, b in enumerate(row):
            if b == "#":
                x, y = q * 2, r * 2
                d.rectangle([x, y, x + 1, y + 1], fill=RGBA(top if r < 4 else shade))
    return im


SMALL = {
    "0": ["###", "#.#", "#.#", "#.#", "###"], "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"], "3": ["###", "..#", ".##", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"], "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"], "7": ["###", "..#", ".#.", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"], "9": ["###", "#.#", "###", "..#", "###"],
}


def small_digit(ch, col):
    im = blank(4, 6)
    d = ImageDraw.Draw(im)
    for r, row in enumerate(SMALL[ch]):
        for q, b in enumerate(row):
            if b == "#":
                d.point((q, r), fill=RGBA(col))
    return im


def key_icon(kind):
    """STKEYS0..5: white / yellow / orange MHC-I (cards and 'skulls' share the look)."""
    im = blank(7, 7)
    d = ImageDraw.Draw(im)
    body = WHITE if kind == 0 else YELLOW
    cap = {0: LGREY, 1: WHITE, 2: ORANGE}[kind]
    d.rectangle((1, 2, 5, 3), fill=RGBA(body))
    d.rectangle((3, 4, 3, 6), fill=RGBA(body))
    d.rectangle((2, 0, 4, 1), fill=RGBA(cap))
    return im


# ---------------------------------------------------------------- HUD face (killer T)

def face(pain=0, look=1, mode="normal"):
    """30x29 killer T cell. pain 0..4; look 0 right, 1 straight, 2 left;
    mode: normal / ouch / evil / kill / god / dead."""
    W_, H_ = 30, 29
    s = Spr(W_, H_)
    cx, cy = 15.0, 16.5
    body, rim, shade = WHITE, GREEN, LGREY
    if mode == "god":
        rim = YELLOW
    if mode == "dead":
        body, rim, shade = DGREY, LAV, DGREY
    elif pain >= 3:
        rim = GREEN if pain == 3 else LAV
    m = mask_circle(W_, H_, cx, cy, 11.6)
    paint_body(s, m, cx, cy, body, rim, shade=shade)
    # TCR forks on top
    for a in (-2.1, -1.57, -1.04):
        cast.fork(s, cx, cy, a, 12.0, rim)
    outline(s, BLACK)
    # bruises with pain
    for i, (x, y) in enumerate([(7, 20), (22, 12), (19, 23), (9, 11), (24, 19), (12, 24)][: [0, 1, 3, 4, 6][pain]]):
        s.put(x, y, LAV); s.put(x + 1, y, LAV); s.put(x, y + 1, PLUM)
    # granules (CD8)
    for (x, y) in [(10, 24), (15, 26), (20, 24)]:
        s.put(x, y, GREEN if mode != "dead" else LAV)
    ex = [9, 18]
    dx = {0: 1, 1: 0, 2: -1}[look]
    ey = 14
    if mode == "dead":
        for x in ex:
            s.rect(x, ey + 1, x + 2, ey + 1, BLACK)
        s.rect(13, 21, 16, 21, BLACK)
        return s
    brow = NAVY
    for i, x in enumerate(ex):
        if mode == "kill":
            # angry: slanted brows
            s.put(x + (0 if i == 0 else 2), ey - 3, brow); s.put(x + 1, ey - 2, brow); s.put(x + (2 if i == 0 else 0), ey - 1, brow)
        else:
            s.rect(x, ey - 2 - (1 if mode == "ouch" else 0), x + 2, ey - 2 - (1 if mode == "ouch" else 0), brow)
        tired = pain >= 2 and mode == "normal"
        if mode == "ouch":
            s.rect(x, ey, x + 2, ey + 2, BLACK); s.put(x + 1, ey + 1, WHITE)
        else:
            px = x + 1 + dx
            s.rect(px, ey + (1 if tired else 0), px, ey + 2, BLACK)
            if pain >= 4:
                s.rect(x, ey, x + 2, ey, shade)
    if mode == "evil":
        s.put(12, 20, BLACK); s.rect(13, 21, 17, 21, BLACK); s.put(18, 20, BLACK)
    elif mode == "ouch":
        s.rect(13, 20, 16, 23, BLACK); s.rect(14, 21, 15, 21, PINK)
    elif mode == "kill":
        s.rect(12, 21, 18, 21, BLACK); s.put(13, 21, WHITE); s.put(17, 21, WHITE)
    else:
        s.rect(13, 21, 17, 21, BLACK)
        if pain >= 3:
            s.put(13, 22, BLACK); s.put(17, 20, BLACK)
    if mode == "god":
        for (x, y) in [(3, 6), (26, 6), (2, 18), (27, 18)]:
            s.put(x, y, YELLOW)
    return s


def faces():
    out = {}
    for p in range(5):
        for lk in range(3):
            out["STFST%d%d" % (p, lk)] = face(p, lk)
        out["STFTR%d0" % p] = face(p, 0)
        out["STFTL%d0" % p] = face(p, 2)
        out["STFOUCH%d" % p] = face(p, 1, "ouch")
        out["STFEVL%d" % p] = face(p, 1, "evil")
        out["STFKILL%d" % p] = face(p, 1, "kill")
    out["STFGOD0"] = face(0, 1, "god")
    out["STFDEAD0"] = face(4, 1, "dead")
    return out


# ---------------------------------------------------------------- HUD font

def hu_char(code):
    ch = chr(code)
    m = ps_mask(ch)
    w = m.width if ch != " " else 4
    im = blank(w + 1, 9)
    im.paste(RGBA(BLACK), (1, 1), m)
    im.paste(RGBA(WHITE), (0, 0), m)
    # slight shading on the lower half so CR translations keep some depth
    arr = np.asarray(im).copy()
    for y in range(4, 8):
        row = arr[y]
        sel = (row[:, 3] > 0) & (row[:, 0] == RGB(WHITE)[0]) & (row[:, 1] == RGB(WHITE)[1])
        row[sel, :3] = RGB(LGREY)
    return Image.fromarray(arr, "RGBA")


# ---------------------------------------------------------------- menu

MENU_TEXT = {
    "M_NGAME": "NEW GAME", "M_OPTION": "OPTIONS", "M_LOADG": "LOAD GAME", "M_SAVEG": "SAVE GAME",
    "M_RDTHIS": "READ THIS!", "M_QUITG": "QUIT GAME", "M_NEWG": "NEW GAME", "M_SKILL": "CHOOSE INFECTION:",
    "M_ROUGH": "COMMON COLD", "M_HURT": "FEVER", "M_ULTRA": "METASTASIS",
    "M_JKILL": "COMMON COLD", "M_NMARE": "METASTASIS",
    "M_EPISOD": "WHICH ORGAN?", "M_EPI1": "THE BODY", "M_EPI2": "THE BODY", "M_EPI3": "THE BODY",
    "M_EPI4": "THE BODY", "M_OPTTTL": "OPTIONS", "M_SFXVOL": "SFX VOLUME", "M_MUSVOL": "MUSIC VOLUME",
    "M_SVOL": "SOUND VOLUME", "M_SGTTL": "SAVE GAME", "M_LGTTL": "LOAD GAME", "M_MSENS": "MOUSE SENSITIVITY",
    "M_MESSG": "MESSAGES:", "M_MSGON": "ON", "M_MSGOFF": "OFF", "M_DETAIL": "GRAPHIC DETAIL:",
    "M_GDHIGH": "HIGH", "M_GDLOW": "LOW", "M_DISOPT": "DISPLAY OPTIONS", "M_SCRNSZ": "SCREEN SIZE",
    "M_ENDGAM": "END GAME", "M_PAUSE": "PAUSE", "M_GENERL": "GENERAL", "M_SETUP": "SETUP",
    "M_KEYBND": "KEY BINDINGS", "M_WEAP": "WEAPONS", "M_STAT": "STATUS BAR AND HUD", "M_AUTO": "AUTOMAP",
    "M_ENEM": "ENEMIES", "M_MESS": "MESSAGES", "M_CHAT": "CHAT STRINGS", "M_COMPAT": "COMPATIBILITY",
    "M_HORSEN": "HORIZONTAL", "M_VERSEN": "VERTICAL", "M_LOKSEN": "MOUSE LOOK", "M_ACCEL": "ACCELERATION",
    "M_MOUSE": "MOUSE", "M_SOUND": "SOUND",
}


def menu_item(name):
    """Menu lines are 16 px apart: the 5x7 logo font at x2 (14 px + shadow) fits cleanly."""
    t = MENU_TEXT[name]
    clean = t.rstrip(":")
    if name not in ("M_SKILL", "M_EPISOD") and all(ch in TITLE_GLYPHS for ch in clean):
        big = name in ("M_NEWG", "M_OPTTTL", "M_SGTTL", "M_LGTTL", "M_PAUSE")
        return logo(clean, 3 if big else 2)
    if name in ("M_SKILL", "M_EPISOD"):
        return ps_text(t, LGREY, LGREY, BLACK, k=1)
    if name in ("M_NEWG", "M_OPTTTL", "M_SGTTL", "M_LGTTL", "M_PAUSE"):
        return logo(t.replace(":", ""), 3) if all(ch in TITLE_GLYPHS for ch in t) else ps_text(t, k=2)
    return ps_text(t, k=2)


def m_doom():
    return logo("LYMPHODOOM", 3)


def cursor(blink=False):
    s = cast.t_cell("cd8", look=1, blink=blink)
    return s.image(1)


def thermo(part):
    im = blank(8, 13)
    d = ImageDraw.Draw(im)
    if part == "L":
        d.rectangle((4, 2, 7, 10), fill=RGBA(GREEN, 4)); d.rectangle((3, 3, 3, 9), fill=RGBA(GREEN, 4))
    elif part == "R":
        d.rectangle((0, 2, 3, 10), fill=RGBA(GREEN, 4)); d.rectangle((4, 3, 4, 9), fill=RGBA(GREEN, 4))
    elif part == "M":
        d.rectangle((0, 2, 7, 10), fill=RGBA(GREEN, 4)); d.rectangle((0, 4, 7, 8), fill=RGBA(NAVY, 10))
    else:  # O: the knob — a granule
        d.ellipse((1, 3, 6, 10), fill=RGBA(WHITE)); d.point((3, 6), fill=RGBA(BLUE))
    return im


def save_box(part):
    w = {"M_LSLEFT": 8, "M_LSCNTR": 8, "M_LSRGHT": 8}[part]
    im = blank(w, 14)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, 13), fill=RGBA(NAVY, 12))
    d.line([(0, 0), (w, 0)], fill=RGBA(GREEN, 4)); d.line([(0, 13), (w, 13)], fill=RGBA(GREEN, 4))
    if part == "M_LSLEFT":
        d.line([(0, 0), (0, 13)], fill=RGBA(GREEN, 4))
    if part == "M_LSRGHT":
        d.line([(w - 1, 0), (w - 1, 13)], fill=RGBA(GREEN, 4))
    return im


# ---------------------------------------------------------------- full screens (320x200)

def paste_spr(img, spr, x, y, k=1):
    im = spr.image(k)
    img.alpha_composite(im, (int(x), int(y)))


def title_screen():
    im = bg_grid(320, 200)
    lg = logo("LYMPHODOOM", 3)
    im.alpha_composite(lg, (160 - lg.width // 2, 2))

    # line-up: the hero facing the invaders (bible style)
    hero = cast.t_cell("cd8", look=1)
    paste_spr(im, hero, 46, 98, 4)
    import monsters
    v = monsters._virus()
    b = monsters._bacterium()
    t = monsters._tumor()
    paste_spr(im, t, 210, 92, 3)
    paste_spr(im, v, 160, 120, 2)
    paste_spr(im, b, 252, 150, 2)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 188, 320, 200), fill=RGBA(BLACK))
    tip = ps_text("AN IMMUNE SYSTEM SHOOTER", GREEN, DGREEN, None, k=1)
    im.alpha_composite(tip, ((320 - tip.width) // 2, 190))
    return im


# intermission: body silhouette with three stops. Coordinates are mirrored in the
# engine patch (engine/lymphodoom.patch, wi_stuff.c lnodes[0]).
WI_SPOTS = [(176, 92), (126, 126), (150, 158)]
BODY_DY = 34  # the body sits below the "ENTERING <level>" title


def body_silhouette(im, dy=BODY_DY):
    layer = blank(320, 260)
    _body(layer)
    im.alpha_composite(layer.crop((0, 0, 320, 200 - dy)), (0, dy))


def _body(im):
    d = ImageDraw.Draw(im)
    skin = RGBA(PEACH, 11)
    edge = RGBA(PEACH, 8)
    cx = 160
    # head, neck, torso, arms, legs as simple shapes
    parts = [
        ("e", (cx - 18, 14, cx + 18, 50)),
        ("r", (cx - 8, 46, cx + 8, 62)),
        ("r", (cx - 40, 60, cx + 40, 140)),
        ("e", (cx - 44, 56, cx - 24, 76)), ("e", (cx + 24, 56, cx + 44, 76)),
        ("r", (cx - 58, 66, cx - 40, 132)), ("r", (cx + 40, 66, cx + 58, 132)),
        ("e", (cx - 60, 126, cx - 42, 144)), ("e", (cx + 42, 126, cx + 60, 144)),
        ("r", (cx - 36, 136, cx - 6, 200)), ("r", (cx + 6, 136, cx + 36, 200)),
    ]
    for pass_, col in ((0, edge), (1, skin)):
        for kind, (x0, y0, x1, y1) in parts:
            o = 1 if pass_ == 0 else 0
            box = (x0 - o, y0 - o, x1 + o, y1 + o)
            (d.ellipse if kind == "e" else d.rounded_rectangle if kind == "r" else d.rectangle)(
                box, fill=col, **({"radius": 6} if kind == "r" else {}))
    # vessels (faint pink lines) and liver
    for pts in ([(cx - 4, 62), (cx - 20, 80), (cx - 34, 92), (cx - 50, 110)],
                [(cx + 4, 62), (cx + 4, 100), (cx - 6, 130), (cx - 20, 170)]):
        d.line(pts, fill=RGBA(PINK, 7), width=2)
    d.ellipse((cx - 26, 116, cx + 4, 132), fill=RGBA(PLUM, 8))
    # lymph node chain on the neck
    for (x, y) in [(170, 52), (172, 56), (176, 58)]:
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=RGBA(LAV, 6))


def wimap():
    im = bg_grid(320, 200)
    body_silhouette(im)
    d = ImageDraw.Draw(im)
    # dotted route between the stops
    for (x0, y0), (x1, y1) in zip(WI_SPOTS, WI_SPOTS[1:]):
        n = int(math.hypot(x1 - x0, y1 - y0) / 4)
        for i in range(n + 1):
            x, y = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n
            if i % 2 == 0:
                d.rectangle((x - 1, y - 1, x, y), fill=RGBA(GREEN, 3))
    for (x, y) in WI_SPOTS:
        d.ellipse((x - 4, y - 4, x + 4, y + 4), outline=RGBA(BLACK), fill=RGBA(NAVY, 2))
    return im


def wi_stats_bg():
    """Plain background for the stats count (the body map comes after)."""
    im = bg_grid(320, 200)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 188, 320, 200), fill=RGBA(BLACK))
    hero = cast.t_cell("cd8", look=-1)
    paste_spr(im, hero, 296, 4, 1)
    return im


def menu_bg():
    """Clean title background behind every menu on the title screen."""
    im = bg_grid(320, 200)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 188, 320, 200), fill=RGBA(BLACK))
    tip = ps_text("AN IMMUNE SYSTEM SHOOTER", GREEN, DGREEN, None, k=1)
    im.alpha_composite(tip, ((320 - tip.width) // 2, 190))
    return im


def wi_here(blink):
    """'You are here': the killer T icon with a small down arrow (origin = spot)."""
    s = cast.t_cell("cd8", look=1, blink=blink)
    im = blank(20, 28)
    im.alpha_composite(s.image(1), (0, 0))
    d = ImageDraw.Draw(im)
    if not blink:
        d.polygon([(7, 21), (13, 21), (10, 26)], fill=RGBA(YELLOW))
    return im, 10, 27


def wi_splat():
    im = blank(11, 11)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 10, 10), fill=RGBA(GREEN), outline=RGBA(BLACK))
    d.line([(2, 5), (4, 7), (8, 2)], fill=RGBA(WHITE), width=2)
    return im, 5, 5


def finale():
    im = bg_grid(320, 200, base=NAVY)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 150, 320, 200), fill=RGBA(PEACH, 10))
    # civilians around (bible body cells), at peace again
    xs = [20, 60, 250, 290, 100, 214]
    for i, x in enumerate(xs):
        fn = [cast.epithelial, cast.stem, cast.clone][i % 3]
        sp = fn() if fn is not cast.clone else cast.clone("ABCD"[i % 4])
        paste_spr(im, sp, x - sp.w, 166 - sp.h * 2 + (i % 2) * 6, 2)
    # remains of the tumor: the bible's apoptosis fragments
    ap = cast.tumor_apoptosis(3)
    paste_spr(im, ap, 160 - ap.w * 3 // 2, 168 - ap.h * 3, 3)
    hero = cast.t_cell("cd8", look=1)
    paste_spr(im, hero, 160 - hero.w * 2, 72, 4)
    lg = logo("CLEAR!", 6, top=GREEN, shade=DGREEN, back=BLACK)
    im.alpha_composite(lg, ((320 - lg.width) // 2, 16))
    d.rectangle((0, 172, 320, 200), fill=RGBA(BLACK))
    return im


def text_screen(title, lines, title_col=YELLOW):
    im = bg_grid(320, 200)
    d = ImageDraw.Draw(im)
    lg = ps_text(title, title_col, ORANGE, PLUM, k=2)
    im.alpha_composite(lg, ((320 - lg.width) // 2, 10))
    y = 40
    for ln in lines:
        if isinstance(ln, tuple):
            t, col = ln
        else:
            t, col = ln, LGREY
        if t:
            m = ps_mask(t)
            d.rectangle((14, y - 1, 14 + m.width + 1, y + 8), fill=RGBA(BLACK))
            im.paste(RGBA(col), (15, y), m)
        y += 11
    return im


def help_screen():
    return text_screen("HOW TO FIGHT", [
        ("MOVE        W A S D", WHITE),
        ("TURN/AIM    MOUSE", WHITE),
        ("FIRE        LEFT CLICK", WHITE),
        ("USE/OPEN    E  OR RIGHT CLICK", WHITE),
        ("RUN         SHIFT", WHITE),
        ("WEAPONS     1-7 OR WHEEL", WHITE),
        ("MAP         TAB", WHITE),
        "",
        ("MHC-I BADGES OPEN MATCHING GATES.", YELLOW),
        ("GLUCOSE HEALS. MEMBRANE PROTECTS.", BLUE),
        ("SCOUTS (DENDRITIC CELLS) SHOW", PINK),
        ("THE WHOLE MAP.", PINK),
        ("TOUCH A RECEPTOR TO SWITCH IT.", GREEN),
    ])


def credit_screen():
    return text_screen("LYMPHODOOM", [
        ("A GAME BY KOSTA CHERNYSHOV", WHITE),
        ("CHARACTERS: CANCER WARS BIBLE", LGREY),
        "",
        ("ENGINE: DWASM / PRBOOMX /", GREEN),
        ("PRBOOM+ - GNU GPL V2+", GREEN),
        ("DOOM SOURCE (C) ID SOFTWARE", LGREY),
        ("MUSIC SYNTH DATA: FREEDOOM", LGREY),
        ("(BSD LICENSE)", LGREY),
        ("FONT: PRESS START 2P (OFL)", LGREY),
        "",
        ("NOT AFFILIATED WITH ID SOFTWARE", DGREY if False else LAV),
        ("OR ZENIMAX MEDIA.", LAV),
        ("SOURCE: GITHUB.COM/KOSTA-BLACKSHOW", ORANGE),
    ])
