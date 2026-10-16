"""First-person weapon sprites: the killer T cell's own pseudopod (white body, green rim,
green granules) holding an organelle. Drawn in bible pixels on a 106x67 'screen'
(320x200 / 3); each frame returns (Spr, left, top) in bible screen pixels."""
import math

import numpy as np

from common import *  # noqa: F401,F403


def _pod(s, x0, y0, x1, y1, r):
    """Pseudopod: capsule from (x0,y0) (offscreen bottom) to (x1,y1)."""
    m = mask_capsule(s.w, s.h, x0, y0, x1, y1, r)
    paint_body(s, m, x1, y1, WHITE, GREEN, shade=LGREY, hi=None)
    # granules inside the pod
    for k, t in enumerate((0.25, 0.45, 0.65)):
        gx = x0 + (x1 - x0) * t + (1 if k % 2 else -1)
        gy = y0 + (y1 - y0) * t
        s.put(int(gx), int(gy), GREEN)
    return m


def _granule(s, x, y, col=BLUE, big=False):
    if big:
        s.ascii(x - 2, y - 2, ["..c..", ".cwc.", "cwwwc", ".cwc.", "..c.."], {"c": col, "w": WHITE})
    else:
        s.ascii(x - 1, y - 1, [".c.", "cwc", ".c."], {"c": col, "w": WHITE})


def _tcr(s, x, y, col=GREEN):
    """Y-fork (TCR) muzzle, opening upwards."""
    s.put(x, y, col); s.put(x, y + 1, col)
    s.put(x - 1, y - 1, col); s.put(x + 1, y - 1, col)
    s.put(x - 2, y - 2, col); s.put(x + 2, y - 2, col)


# ---------------------------------------------------------------- fist: SYNAPSE PUNCH

def fist(k):
    s = Spr(40, 40)
    reach = [0, 6, 11, 5][k]
    tipx, tipy = 22 - reach * 0.3, 22 - reach
    r = 6 + (1 if k == 2 else 0)
    _pod(s, 28, 44, tipx, tipy, r)
    # synapse contact: a ring of granules released at the tip on impact
    if k == 2:
        for a in range(0, 360, 45):
            x, y = tipx + math.cos(math.radians(a)) * (r + 2), tipy + math.sin(math.radians(a)) * (r + 2) - 1
            s.put(int(x), int(y), BLUE if a % 90 else GREEN)
    outline(s, BLACK)
    hero_eyes(s, int(tipx) - 3, int(tipy) + 1)
    return s, 50, 27


def hero_eyes(s, x, y):
    """The cell's determined face peeking on the pod (keeps it a character)."""
    s.put(x, y - 1, NAVY); s.put(x + 1, y - 1, NAVY)
    s.put(x + 5, y - 1, NAVY); s.put(x + 6, y - 1, NAVY)
    s.put(x + 1, y, BLACK); s.put(x + 1, y + 1, BLACK)
    s.put(x + 6, y, BLACK); s.put(x + 6, y + 1, BLACK)


# ---------------------------------------------------------------- pistol: GRANULE GUN

def pistol(k):
    s = Spr(34, 44)
    squeeze = [0, 2, 1][k]
    tipx, tipy = 16, 14 + squeeze
    _pod(s, 18, 48, tipx, tipy, 6 + (1 if squeeze == 2 else 0))
    # granule sac at the tip
    sac = mask_circle(s.w, s.h, tipx, tipy - 3, 4.5 - squeeze * 0.4)
    s.a[sac & (s.a < 0)] = LAV
    s.a[mask_circle(s.w, s.h, tipx, tipy - 3, 3.5 - squeeze * 0.4)] = NAVY
    for (dx, dy, c) in [(-1, -4, BLUE), (1, -3, GREEN), (0, -2, BLUE)]:
        s.put(tipx + dx, tipy + dy, c)
    _tcr(s, tipx, tipy - 9 + squeeze)
    outline(s, BLACK)
    return s, 47, 26 + squeeze


def pistol_flash():
    s = Spr(15, 13)
    for a in range(0, 360, 30):
        r = 5 + (a % 60 == 0) * 2
        x, y = 7 + math.cos(math.radians(a)) * r, 7 + math.sin(math.radians(a)) * r * 0.8
        s.put(int(x), int(y), GREEN if a % 60 else BLUE)
    _granule(s, 7, 6, BLUE, big=True)
    return s, 56, 13


# ---------------------------------------------------------------- shotgun: CYTOKINE BURST

def _vesicles(s, cx, cy, n, col=ORANGE, spread=1.0):
    pts = [(0, 0), (-3, 1), (3, 1), (-1, -2), (2, -2), (0, 3), (-4, -2), (4, -2)][:n]
    for (dx, dy) in pts:
        x, y = int(cx + dx * spread), int(cy + dy * spread)
        s.ascii(x - 1, y - 1, [".c.", "cwc", ".c."], {"c": col, "w": PEACH})


def shotgun(k):
    """A: ready, B-D: refill (vesicles regrow), E: recoil."""
    s = Spr(44, 44)
    lift = [0, 3, 5, 3, 1][k]
    tipx, tipy = 22, 16 + lift
    _pod(s, 14, 50, tipx - 3, tipy + 2, 6)
    _pod(s, 30, 50, tipx + 3, tipy + 2, 6)
    # the vesicle cluster held between two pods
    cl = mask_circle(s.w, s.h, tipx, tipy - 2, 6.5)
    s.a[cl] = PEACH
    s.a[mask_circle(s.w, s.h, tipx, tipy - 2, 5.5)] = BROWN
    _vesicles(s, tipx, tipy - 2, [8, 3, 5, 7, 8][k])
    outline(s, BLACK)
    return s, 31, 25 + lift


def shotgun_flash(k):
    s = Spr(30, 20)
    for i in range(14 if k == 0 else 9):
        a = math.radians(200 + i * (140 / 13.0))
        r = 6 + (i * 7) % 6 + (3 if k else 0)
        x, y = 15 + math.cos(a) * r * 1.3, 15 + math.sin(a) * r
        s.ascii(int(x) - 1, int(y) - 1, [".c.", "cwc", ".c."], {"c": ORANGE, "w": YELLOW if k == 0 else PEACH})
    return s, 38, 20


# ---------------------------------------------------------------- chaingun: GRANZYME STREAM

def chaingun(k):
    s = Spr(40, 44)
    tipx, tipy = 20, 16
    _pod(s, 20, 50, tipx, tipy + 4, 7)
    ring = mask_circle(s.w, s.h, tipx, tipy, 6.5)
    s.a[ring] = WHITE
    s.a[mask_circle(s.w, s.h, tipx, tipy, 5.5)] = GREEN
    s.a[mask_circle(s.w, s.h, tipx, tipy, 2.5)] = NAVY
    for i in range(6):
        a = math.radians(i * 60 + k * 30)
        _granule(s, int(tipx + math.cos(a) * 4), int(tipy + math.sin(a) * 4), BLUE if i % 2 else WHITE)
    outline(s, BLACK)
    return s, 33, 25


def chaingun_flash(k):
    s = Spr(13, 13)
    _granule(s, 6, 6, GREEN, big=True)
    for a in range(0, 360, 60):
        x, y = 6 + math.cos(math.radians(a + k * 30)) * 5, 6 + math.sin(math.radians(a + k * 30)) * 5
        s.put(int(x), int(y), WHITE if k else GREEN)
    return s, 47, 27


# ---------------------------------------------------------------- rocket: ANTIBODY BOMB

def _antibody(s, x, y, spark=True):
    s.ascii(x, y, [
        "w.......w",
        "bw.....wb",
        ".bw...wb.",
        "..bw.wb..",
        "...bwb...",
        "....w....",
        "....w....",
        "....b....",
    ], {"w": WHITE, "b": BLUE})
    if spark:
        s.put(x + 7, y + 6, YELLOW); s.put(x + 8, y + 5, YELLOW); s.put(x + 8, y + 6, YELLOW)
        s.put(x + 8, y + 7, YELLOW); s.put(x + 9, y + 6, YELLOW)


def launcher(k):
    s = Spr(40, 46)
    rec = [0, 3][k]
    tipx, tipy = 20, 18 + rec
    _pod(s, 22, 52, tipx, tipy + 6, 7)
    # B-cell-like launcher: dark green rim
    m = mask_superellipse(s.w, s.h, tipx, tipy, 8, 7, n=2.5)
    paint_body(s, m, tipx, tipy, WHITE, DGREEN, shade=LGREY)
    s.a[mask_circle(s.w, s.h, tipx, tipy - 1, 4.0)] = NAVY
    if k == 0:
        _antibody(s, tipx - 4, tipy - 8)
    outline(s, BLACK)
    return s, 33, 24 + rec


def launcher_flash(k):
    s = Spr(21, 17)
    r = [4, 6, 7, 5][k]
    for yy in range(17):
        for xx in range(21):
            d = math.hypot(xx - 10, (yy - 9) * 1.2)
            if d <= r and (k < 2 or (xx + yy) % 2 == 0):
                s.put(xx, yy, WHITE if d < r * 0.4 else YELLOW if d < r * 0.7 else BLUE)
    return s, 43, 25


# ---------------------------------------------------------------- plasma: INTERFERON

def plasma(k):
    s = Spr(42, 44)
    tipx, tipy = 21, 17
    _pod(s, 15, 50, tipx - 3, tipy + 4, 6)
    _pod(s, 28, 50, tipx + 3, tipy + 4, 6)
    orb = mask_circle(s.w, s.h, tipx, tipy, 7.0)
    s.a[orb] = LAV
    s.a[mask_circle(s.w, s.h, tipx, tipy, 5.5)] = BLUE if k == 0 else WHITE
    s.a[mask_circle(s.w, s.h, tipx, tipy, 3.0)] = WHITE if k == 0 else LAV
    for a in range(0, 360, 72):
        x, y = tipx + math.cos(math.radians(a + 20 * k)) * 8.5, tipy + math.sin(math.radians(a + 20 * k)) * 8.5
        s.put(int(x), int(y), LAV)
    outline(s, BLACK)
    return s, 32, 24


def plasma_flash(k):
    s = Spr(19, 19)
    r = 6 + 2 * k
    for yy in range(19):
        for xx in range(19):
            d = math.hypot(xx - 9, yy - 9)
            if abs(d - r) < 1.0 or d < 2.5:
                s.put(xx, yy, WHITE if d < 2.5 else BLUE)
    return s, 44, 32


# ---------------------------------------------------------------- BFG: CAR-T BOOST

def bfg(k):
    s = Spr(52, 46)
    tipx, tipy = 26, 18
    _pod(s, 16, 52, tipx - 6, tipy + 6, 7)
    _pod(s, 36, 52, tipx + 6, tipy + 6, 7)
    m = mask_circle(s.w, s.h, tipx, tipy + 2, 10.0)
    paint_body(s, m, tipx, tipy + 2, WHITE, GREEN, shade=LGREY)
    # engineered receptor: blue claw + yellow nut (bible CAR-T)
    s.rect(tipx - 1, tipy - 10, tipx + 1, tipy - 6, LGREY)
    for side in (-1, 1):
        for t in range(5):
            s.put(tipx + side * (2 + t // 2), tipy - 11 - t, BLUE)
            s.put(tipx + side * (3 + t // 2), tipy - 11 - t, BLUE)
    s.rect(tipx - 2, tipy - 5, tipx + 2, tipy - 4, YELLOW)
    s.put(tipx, tipy - 5, ORANGE)
    if k == 1:
        s.a[mask_circle(s.w, s.h, tipx, tipy - 15, 3.5)] = GREEN
        s.a[mask_circle(s.w, s.h, tipx, tipy - 15, 2.0)] = WHITE
    outline(s, BLACK)
    hero_eyes(s, tipx - 4, tipy + 2)
    return s, 27, 23


def bfg_flash(k):
    s = Spr(31, 25)
    r = 8 + 3 * k
    for yy in range(25):
        for xx in range(31):
            d = math.hypot(xx - 15, (yy - 12) * 1.2)
            if d <= r and (d < r * 0.5 or (xx + yy + k) % 2 == 0):
                s.put(xx, yy, WHITE if d < r * 0.3 else GREEN)
    return s, 38, 14


WSCALE = 4  # weapons use the bible's own x4 video scale: an 80x50 bible-pixel screen


def all_weapons():
    """list of (lump name, Spr, left, top) on the 80x50 weapon screen (x4)."""
    out = []
    for i, L in enumerate("ABCD"):
        out.append(("PUNG" + L + "0",) + fist(i))
    for i, L in enumerate("ABC"):
        out.append(("PISG" + L + "0",) + pistol(i))
    out.append(("PISFA0",) + pistol_flash())
    for i, L in enumerate("ABCDE"):
        out.append(("SHTG" + L + "0",) + shotgun(i))
    for i, L in enumerate("AB"):
        out.append(("SHTF" + L + "0",) + shotgun_flash(i))
        out.append(("CHGG" + L + "0",) + chaingun(i))
        out.append(("CHGF" + L + "0",) + chaingun_flash(i))
        out.append(("MISG" + L + "0",) + launcher(i))
        out.append(("PLSG" + L + "0",) + plasma(i))
        out.append(("PLSF" + L + "0",) + plasma_flash(i))
        out.append(("BFGG" + L + "0",) + bfg(i))
        out.append(("BFGF" + L + "0",) + bfg_flash(i))
    for i, L in enumerate("ABCD"):
        out.append(("MISF" + L + "0",) + launcher_flash(i))
    # authored on a 106x67 grid anchored bottom-centre: move to the 80x50 screen
    return [(n, sp, l - 13 + 4, t - 17 + 9) for (n, sp, l, t) in out]
