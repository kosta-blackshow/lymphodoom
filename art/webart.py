"""Pixel art for the game page: the start screen, the two difficulty buttons and the
'how it works' picture that replaces the explanatory text."""
import math

from PIL import Image, ImageDraw

from common import *  # noqa: F401,F403
import monsters
import items
import ui
from ui import RGBA, blank, bg_grid, logo, ps_mask, paste_spr

# 3x5 font, full alphabet (the bible's caption style, shrunk for labels)
F35 = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": [".##", "#..", "#..", "#..", ".##"], "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"], "F": ["###", "#..", "##.", "#..", "#.."],
    "G": [".##", "#..", "#.#", "#.#", ".##"], "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"], "J": ["..#", "..#", "..#", "#.#", ".#."],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"], "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#.#", "###", "###", "#.#", "#.#"], "N": ["##.", "#.#", "#.#", "#.#", "#.#"],
    "O": [".#.", "#.#", "#.#", "#.#", ".#."], "P": ["##.", "#.#", "##.", "#..", "#.."],
    "Q": [".#.", "#.#", "#.#", "##.", ".##"], "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": [".##", "#..", ".#.", "..#", "##."], "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"], "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "W": ["#.#", "#.#", "###", "###", "#.#"], "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."], "Z": ["###", "..#", ".#.", "#..", "###"],
    "0": ["###", "#.#", "#.#", "#.#", "###"], "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["##.", "..#", ".#.", "#..", "###"], "3": ["##.", "..#", ".#.", "..#", "##."],
    "-": ["...", "...", "###", "...", "..."], "+": ["...", ".#.", "###", ".#.", "..."],
    "!": [".#.", ".#.", ".#.", "...", ".#."], " ": ["...", "...", "...", "...", "..."],
    "/": ["..#", "..#", ".#.", "#..", "#.."], "?": ["##.", "..#", ".#.", "...", ".#."],
    ".": ["...", "...", "...", "...", ".#."], ",": ["...", "...", "...", ".#.", "#.."],
}


def t35(im, x, y, text, col, k=1, center=False, shadow=BLACK):
    w = len(text) * 4 * k - k
    if center:
        x -= w // 2
    d = ImageDraw.Draw(im)
    for pass_, c in ((0, shadow), (1, col)):
        if c is None:
            continue
        o = k if pass_ == 0 else 0
        for n, ch in enumerate(text):
            for r, row in enumerate(F35[ch]):
                for q, b in enumerate(row):
                    if b == "#":
                        X, Y = x + (n * 4 + q) * k + o, y + r * k + o
                        d.rectangle((X, Y, X + k - 1, Y + k - 1), fill=RGBA(c))
    return w


def keycap(im, x, y, ch, w=11):
    d = ImageDraw.Draw(im)
    d.rectangle((x, y + 2, x + w - 1, y + 12), fill=RGBA(PLUM))
    d.rectangle((x, y, x + w - 1, y + 10), fill=RGBA(PEACH))
    t35(im, x + w // 2, y + 3, ch, BLACK, center=True, shadow=None)


def mouse_icon(im, x, y, button="L"):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + 10, y + 15), radius=4, fill=RGBA(WHITE), outline=RGBA(BLACK))
    d.line([(x + 5, y + 1), (x + 5, y + 6)], fill=RGBA(BLACK))
    d.line([(x + 1, y + 6), (x + 9, y + 6)], fill=RGBA(BLACK))
    if button == "L":
        d.rectangle((x + 2, y + 2, x + 4, y + 5), fill=RGBA(GREEN))
    elif button == "R":
        d.rectangle((x + 6, y + 2, x + 8, y + 5), fill=RGBA(GREEN))


def arrow(im, x0, y, x1, col=GREEN):
    d = ImageDraw.Draw(im)
    for x in range(x0, x1 - 3, 3):
        d.rectangle((x, y, x + 1, y), fill=RGBA(col))
    d.polygon([(x1 - 3, y - 3), (x1, y), (x1 - 3, y + 3)], fill=RGBA(col))


# ---------------------------------------------------------------- start screen

def start_screen():
    im = bg_grid(320, 200)
    lg = logo("LYMPHODOOM", 3)
    im.alpha_composite(lg, (160 - lg.width // 2, 8))
    # the two buttons are HTML on top of y 44..112
    d = ImageDraw.Draw(im)
    d.rectangle((0, 124, 320, 182), fill=RGBA(BLACK))
    # move
    x = 22
    keycap(im, x + 12, 133, "W")
    keycap(im, x, 146, "A"); keycap(im, x + 12, 146, "S"); keycap(im, x + 24, 146, "D")
    t35(im, x + 18, 166, "MOVE", WHITE, center=True)
    # aim + fire
    x = 104
    mouse_icon(im, x + 6, 136, "L")
    t35(im, x + 11, 159, "AIM", WHITE, center=True)
    t35(im, x + 11, 166, "+ FIRE", GREEN, center=True)
    # open
    x = 168
    keycap(im, x, 141, "E")
    t35(im, x + 16, 145, "OR", LGREY)
    mouse_icon(im, x + 28, 136, "R")
    t35(im, x + 22, 166, "OPEN", WHITE, center=True)
    # weapons & map
    x = 248
    for i, ch in enumerate("123"):
        keycap(im, x + i * 12, 133, ch)
    t35(im, x + 18, 150, "WEAPONS", WHITE, center=True)
    keycap(im, x + 6, 160, "TAB", w=23)
    t35(im, x + 34, 163, "MAP", WHITE)
    d.rectangle((0, 188, 320, 200), fill=RGBA(BLACK))
    tip = ui.ps_text("AN IMMUNE SYSTEM SHOOTER", GREEN, DGREEN, None, k=1)
    im.alpha_composite(tip, ((320 - tip.width) // 2, 190))
    return im


def button(kind):
    """Difficulty button art (150x26). kind: 'easy' or 'hard'."""
    im = blank(150, 26, NAVY, 12)
    d = ImageDraw.Draw(im)
    rim = GREEN if kind == "easy" else RED
    d.rectangle((0, 0, 149, 25), outline=RGBA(rim))
    d.rectangle((1, 1, 148, 24), outline=RGBA(BLACK))
    if kind == "easy":
        spr = monsters._virus()
        name, sub = "COMMON COLD", "A FEW GERMS"
    else:
        spr = monsters._mass()
        spr = scale(spr, 0.6)
        name, sub = "METASTASIS", "ALL OUT INFECTION"
    paste_spr(im, spr, 4, 13 - spr.h // 2)
    txt = ui.ps_text(name, YELLOW, ORANGE, PLUM, k=1)
    im.alpha_composite(txt, (34, 5))
    t35(im, 34, 16, sub, LGREY if kind == "easy" else PINK)
    return im


# ---------------------------------------------------------------- how it works

def howto():
    W, H = 320, 168
    im = bg_grid(W, H)
    d = ImageDraw.Draw(im)

    # row 1: you vs the infection
    d.rectangle((0, 0, W, 62), fill=RGBA(NAVY, 10))
    hero = cast.t_cell("cd8", look=1)
    paste_spr(im, hero, 6, 14)
    t35(im, 16, 38, "YOU", GREEN, center=True)
    t35(im, 16, 45, "KILLER T", WHITE, center=True)
    for i in range(3):
        x = 32 + i * 6
        d.rectangle((x, 23, x + 1, 24), fill=RGBA(BLUE if i % 2 else GREEN))
    arrow(im, 48, 24, 58)
    foes = [("VIRUS", monsters._virus()), ("BACTERIUM", monsters._bacterium()),
            ("TUMOR", monsters._tumor()), ("PARASITE", monsters._parasite()),
            ("PHAGE", monsters._phage()), ("SPORE", scale(monsters._spore(), 0.7)),
            ("BOSS", scale(monsters._mass(), 0.62))]
    x = 62
    for name, spr in foes:
        cw = max(spr.w, len(name) * 4 + 2)
        paste_spr(im, spr, x + (cw - spr.w) // 2, 34 - spr.h)
        t35(im, x + cw // 2, 40, name, PINK if name != "BOSS" else RED, center=True)
        x += cw + 3
    t35(im, 62, 50, "SHOOT THEM. THEY BLOW UP.", LGREY)

    # row 2: what to pick up
    y = 68
    t35(im, 6, y, "PICK UP", YELLOW)
    picks = [("HEALTH", items.glucose_big()["A"].spr), ("ARMOR", items.membrane_armor()["A"].spr),
             ("AMMO", items.granule_sac(8, 15, 11)["A"].spr), ("MAP", scale(cast.dendritic(), 0.8))]
    x = 6
    for name, spr in picks:
        cw = max(spr.w, len(name) * 4)
        paste_spr(im, spr, x + (cw - spr.w) // 2, y + 26 - spr.h)
        t35(im, x + cw // 2, y + 30, name, WHITE, center=True)
        x += cw + 10
    # keys open gates
    x += 4
    for i, cap in enumerate(("white", "yellow", "orange")):
        spr = items.mhc_key(cap)["A"].spr
        paste_spr(im, spr, x + i * 11, y + 14)
    t35(im, x + 16, y + 30, "KEYS", WHITE, center=True)
    arrow(im, x + 36, y + 20, x + 48)
    gx = x + 52
    d.rectangle((gx, y + 6, gx + 20, y + 28), fill=RGBA(LGREY, 9), outline=RGBA(BLACK))
    d.line([(gx + 10, y + 6), (gx + 10, y + 28)], fill=RGBA(GREEN, 5))
    d.rectangle((gx + 7, y + 12, gx + 13, y + 16), fill=RGBA(YELLOW))
    d.rectangle((gx + 9, y + 16, gx + 11, y + 22), fill=RGBA(YELLOW))
    t35(im, gx + 10, y + 30, "GATE", WHITE, center=True)

    # row 3: the route through the body
    y = 108
    d.rectangle((0, y, W, H), fill=RGBA(NAVY, 10))
    import textures as TX
    walls = [TX.lymph_wall(), TX.vessel_wall(), TX.tumor_wall()]
    casts = [[(monsters._virus(), 10), (monsters._virus(1), 52)],
             [(items.rbc()["A"].spr, 8), (monsters._bacterium(), 40), (items.rbc()["A"].spr, 64)],
             [(scale(monsters._mass(), 0.75), 25)]]
    tiles = [("LYMPH NODE", LAV), ("BLOODSTREAM", PINK), ("TUMOR", RED)]
    for i, (name, col) in enumerate(tiles):
        tx = 14 + i * 104
        wt = walls[i]
        tile = Image.new("RGB", (160, wt.height))
        for ox in range(0, 160, wt.width):
            tile.paste(wt, (ox, 0))
        bgt = tile.crop((0, 20, 81, 59)).convert("RGBA")
        im.alpha_composite(bgt, (tx, y + 8))
        d.rectangle((tx, y + 8, tx + 80, y + 46), outline=RGBA(col, 2))
        for spr, ox in casts[i]:
            paste_spr(im, spr, tx + ox, y + 44 - spr.h)
        t35(im, tx + 40, y + 50, name, WHITE, center=True)
        t35(im, tx + 40, y + 2, "LEVEL %d" % (i + 1), LGREY, center=True)
        if i < 2:
            arrow(im, tx + 84, y + 27, tx + 102)
    return im


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
    start_screen().save(out + "/start.png")
    button("easy").save(out + "/btn_easy.png")
    button("hard").save(out + "/btn_hard.png")
    howto().save(out + "/howto.png")
