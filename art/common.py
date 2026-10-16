"""Shared drawing helpers for LYMPHODOOM sprites (bible pixels, PICO-8 indices)."""
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "vendor", "pixel_kit"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

from pixel_kit.palette import *  # noqa: E402,F401,F403
from pixel_kit.pixdraw import (Spr, T, mask_radial, mask_circle, mask_superellipse,  # noqa: E402,F401
                               mask_capsule, paint_body, outline, polar, erode, scale)
from pixel_kit import cast  # noqa: E402,F401

SCALE = 3  # one bible pixel = 3 Doom world pixels


class Frame:
    """A sprite frame: Spr plus the anchor (origin) in bible pixels.
    ax: x of the thing centre; ay: row of the floor/origin point."""

    def __init__(self, spr, ax=None, ay=None):
        self.spr = spr
        self.ax = spr.w / 2 if ax is None else ax
        self.ay = spr.h if ay is None else ay


def canvas(w, h):
    return Spr(w, h)


def place(dst, src, x, y):
    """Stamp src onto dst with top-left at (x, y)."""
    dst.stamp(src, int(round(x)), int(round(y)))


def flash(s, col=WHITE):
    """Bible 'hit': white silhouette."""
    o = Spr(s.w, s.h)
    m = s.a >= 0
    o.a[m] = col
    # keep the black outline so the silhouette stays readable
    o.a[s.a == BLACK] = BLACK
    return o


def recolor(s, mapping):
    return s.recolor(mapping)


def shift(s, dx, dy):
    o = Spr(s.w, s.h)
    o.stamp(s, dx, dy)
    return o


def pad(s, l, t, r, b):
    o = Spr(s.w + l + r, s.h + t + b)
    o.stamp(s, l, t)
    return o


def burst(alive, n, seed=1, goo=(PLUM, RED, PINK), puddle=None, power=1.0, gib=False):
    """Explosion frames (the game's deviation from the bible: enemies blow up).
    alive: Frame standing on its floor row. Returns list of n Frames; the last one
    is the puddle left on the floor."""
    rnd = random.Random(seed)
    s = alive.spr
    size0 = max(s.w, s.h)
    Rmax = size0 * 0.55 * (1.15 if gib else 1.0)
    W = max(int(s.w * (1.9 if gib else 1.6)) + 8, int(2 * Rmax) + 6)
    H = max(int(s.h * 1.35) + 6, int(Rmax + 4 + alive.ay - s.h / 2) + 2)
    ox = (W - s.w) // 2
    floor = H - 2
    oy = floor - alive.ay  # top of the alive sprite in canvas
    cx, cy = ox + s.w / 2, oy + s.h / 2
    size = max(s.w, s.h)
    # chunks: 3x3 blocks of the body
    chunks = []
    for y0 in range(0, s.h, 3):
        for x0 in range(0, s.w, 3):
            blk = s.a[y0:y0 + 3, x0:x0 + 3]
            if (blk >= 0).sum() >= 4:
                px, py = ox + x0 + 1, oy + y0 + 1
                ang = math.atan2(py - cy, px - cx) + rnd.uniform(-0.4, 0.4)
                sp = rnd.uniform(0.5, 1.0) * power * (1.3 if gib else 1.0) * size / 22.0
                chunks.append([px, py, math.cos(ang) * sp, math.sin(ang) * sp - 0.5, blk.copy()])
    drops = []
    for _ in range(int(16 * power * (1.5 if gib else 1))):
        ang = rnd.uniform(0, 2 * math.pi)
        sp = rnd.uniform(0.8, 1.6) * power * size / 22.0
        drops.append([cx, cy, math.cos(ang) * sp, math.sin(ang) * sp - 0.6, rnd.choice(goo)])
    pud = puddle or goo[0]
    frames = []
    nfly = n - 2  # frames between the flash and the puddle
    for k in range(n):
        c = Spr(W, H)
        t = (k) * (4.2 / max(1, nfly))
        last = k == n - 1
        if 1 <= k <= 2 and not last:
            # the bang: a round cloud, white-hot core, goo-coloured ring (dithered when fading)
            R = size * (0.42 if k == 1 else 0.55) * (1.15 if gib else 1.0)
            for yy in range(H):
                for xx in range(W):
                    d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
                    if d <= R:
                        if k == 2 and ((xx + yy) % 2 or d < R * 0.55):
                            continue
                        col = WHITE if d < R * 0.35 else (YELLOW if d < R * 0.55 and k == 1 else goo[1] if d < R * 0.8 else goo[0])
                        c.put(xx, yy, col)
        if k == 0 and not last:
            # swell and crack: bright flash with red cracks
            sw = scale(s, 1.15)
            fl = flash(sw, WHITE)
            for _ in range(10):
                x, y = rnd.randrange(sw.w), rnd.randrange(sw.h)
                if fl.get(x, y) == WHITE:
                    fl.put(x, y, goo[1])
            place(c, fl, cx - sw.w / 2, cy - sw.h / 2)
            frames.append(Frame(c, W / 2, floor))
            continue
        if last:
            # puddle on the floor with a few bits
            pw = int(s.w * 0.9)
            for x in range(pw):
                hgt = 1 + int(1.5 * math.sin(math.pi * x / max(1, pw - 1)))
                for yy in range(hgt):
                    c.put(int(cx - pw / 2 + x), floor - yy, pud if yy < hgt - 1 else goo[-1])
            for ch in chunks[::max(1, len(chunks) // 6)]:
                x = int(cx + rnd.uniform(-pw / 2, pw / 2))
                c.put(x, floor - 2, int(ch[4][ch[4] >= 0][0]))
            # outline only around the puddle bits
            outline(c, BLACK)
            frames.append(Frame(c, W / 2, floor))
            continue
        for ch in chunks:
            x = ch[0] + ch[2] * t * 3.0
            y = ch[1] + ch[3] * t * 3.0 + 0.55 * t * t
            y = min(y, floor - 1)
            blk = ch[4]
            for by in range(blk.shape[0]):
                for bx in range(blk.shape[1]):
                    if blk[by, bx] >= 0:
                        c.put(int(x) + bx, int(y) + by, int(blk[by, bx]))
        for d in drops:
            x = d[0] + d[2] * t * 3.4
            y = min(d[1] + d[3] * t * 3.4 + 0.7 * t * t, floor - 1)
            c.put(int(x), int(y), d[4])
            if k < 3:
                c.put(int(x) + 1, int(y), d[4])
        frames.append(Frame(c, W / 2, floor))
    return frames


def fragments_only(frames):
    return frames


def bob(frame, dy):
    s = pad(frame.spr, 0, 2, 0, 2)
    o = Spr(s.w, s.h)
    o.stamp(s, 0, dy)
    return Frame(o, frame.ax, frame.ay + 2)


def villain_face(s, ci, cj, open_mouth=0, blink=False):
    """Bible villain face: angry brows, red eyes, pressed mouth (open_mouth 0..2)."""
    s.put(ci - 4, cj - 3, BLACK); s.put(ci - 3, cj - 2, BLACK)
    s.put(ci + 2, cj - 2, BLACK); s.put(ci + 3, cj - 3, BLACK)
    if blink:
        s.put(ci - 3, cj, BLACK); s.put(ci + 2, cj, BLACK)
    else:
        for ex in (ci - 3, ci + 2):
            s.put(ex, cj - 1, BLACK); s.put(ex, cj, RED)
    if open_mouth == 0:
        for dx in (-1, 0, 1):
            s.put(ci + dx, cj + 2, BLACK)
    else:
        for dx in range(-1 - open_mouth // 2, 2 + open_mouth // 2):
            s.put(ci + dx, cj + 2, BLACK)
            for k in range(1, open_mouth + 1):
                s.put(ci + dx, cj + 2 + k, BLACK)
        s.put(ci - 1, cj + 3, WHITE); s.put(ci + 1, cj + 3, WHITE)
