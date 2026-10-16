"""Enemy sprites. Each function returns {frame_letter: Frame} at bible-pixel scale.
Layouts follow the Doom 1 monster the enemy replaces (see docs/bible-addendum.md)."""
import math

import numpy as np

from common import *  # noqa: F401,F403
from common import Frame, burst, flash, villain_face, bob, pad


# ---------------------------------------------------------------- VIRUS (zombieman, POSS)

def _virus(phase=0, mouth=0, spit=False, blink=False):
    S = 22
    c = 11.0
    s = Spr(S, S)
    ys, xs = np.mgrid[0:S, 0:S]
    dx, dy = np.abs(xs + 0.5 - c), np.abs(ys + 0.5 - c)
    m = (dy <= 6.2) & (dx * 0.866 + dy * 0.5 <= 6.6)
    paint_body(s, m, c, c, LAV, PINK, shade=DGREY, hi=WHITE)
    outline(s, BLACK)
    # glycoprotein spikes at the hexagon corners and edge midpoints
    for k in range(6):
        a = math.radians(30 + 60 * k + (8 if phase % 2 else 0))
        r0 = 7.2
        for r in (r0, r0 + 1):
            s.put(math.floor(c + math.cos(a) * r), math.floor(c + math.sin(a) * r), LGREY)
        hx, hy = math.floor(c + math.cos(a) * (r0 + 2.3) - 0.5), math.floor(c + math.sin(a) * (r0 + 2.3) - 0.5)
        s.rect(hx, hy, hx + 1, hy + 1, PINK)
    villain_face(s, 11, 10, open_mouth=mouth, blink=blink)
    if spit:
        for (x, y) in [(10, 15), (11, 16), (12, 15), (11, 17), (10, 18), (12, 18)]:
            s.put(x, y, ORANGE)
        s.put(11, 15, YELLOW)
    return s


def virus():
    f = {}
    base = Frame(_virus(), 11, 21)
    for k, L in enumerate("ABCD"):
        f[L] = bob(Frame(_virus(phase=k), 11, 21), [0, -1, -1, 0][k])
    f["E"] = bob(Frame(_virus(mouth=1), 11, 21), 0)
    f["F"] = bob(Frame(_virus(mouth=2, spit=True), 11, 21), 0)
    f["G"] = bob(Frame(flash(_virus()), 11, 21), 0)
    for L, fr in zip("HIJKL", burst(base, 5, seed=11, goo=(LAV, PINK, WHITE))):
        f[L] = fr
    for L, fr in zip("MNOPQRSTU", burst(base, 9, seed=12, goo=(LAV, PINK, WHITE), gib=True)):
        f[L] = fr
    return f


# ---------------------------------------------------------------- BACTERIUM (shotgun guy, SPOS)

def _bacterium(phase=0, mouth=0, spray=False):
    W_, H_ = 30, 18
    s = Spr(W_, H_)
    # flagella behind (left), wavy
    for strand, y0 in enumerate((6, 9, 12)):
        for x in range(0, 9):
            y = y0 + round(1.4 * math.sin((x + phase * 2 + strand * 2) * 0.9))
            s.put(x, y, BROWN)
    m = mask_capsule(W_, H_, 13.0, 9.0, 23.0, 9.0, 6.0)
    paint_body(s, m, 18.0, 9.0, ORANGE, BROWN, shade=BROWN, hi=PEACH)
    outline(s, BLACK)
    # pili dots on the cell wall
    for (x, y) in [(12, 6), (15, 4), (21, 4), (24, 6), (13, 13), (24, 13)]:
        s.put(x, y, PEACH)
    villain_face(s, 19, 8, open_mouth=mouth)
    if spray:
        for (x, y) in [(18, 12), (19, 13), (20, 12), (17, 14), (21, 14), (19, 15), (16, 15), (22, 15)]:
            s.put(x, y, YELLOW if (x + y) % 3 == 0 else ORANGE)
    return s


def bacterium():
    f = {}
    base = Frame(_bacterium(), 18, 17)
    for k, L in enumerate("ABCD"):
        f[L] = bob(Frame(_bacterium(phase=k), 18, 17), [0, -1, 0, -1][k])
    f["E"] = bob(Frame(_bacterium(mouth=1), 18, 17), 0)
    f["F"] = bob(Frame(_bacterium(mouth=2, spray=True), 18, 17), 0)
    f["G"] = bob(Frame(flash(_bacterium()), 18, 17), 0)
    for L, fr in zip("HIJKL", burst(base, 5, seed=21, goo=(ORANGE, BROWN, PEACH))):
        f[L] = fr
    for L, fr in zip("MNOPQRSTU", burst(base, 9, seed=22, goo=(ORANGE, BROWN, PEACH), gib=True)):
        f[L] = fr
    return f


# ---------------------------------------------------------------- TUMOR CELL (imp, TROO)

MHC_ANGLES = [math.radians(-112.5 + 45 * k) for k in range(8)]


def _tumor(phase=0.0, mouth=0, pdl1=False, ball=False, mhc=True, S=24):
    c = S / 2
    s = Spr(S, S)
    r = lambda a: 6.4 + 0.75 * np.sin(3 * a + 0.4 + phase) + 0.4 * np.sin(5 * a + 1.3 - phase)
    m = mask_radial(S, S, c, c, r)
    cast.villain_body(s, m, c, c)
    villain_face(s, int(c), int(c), open_mouth=mouth)
    for (x, y) in [(int(c) + 2, int(c) + 4), (int(c) - 3, int(c) + 4), (int(c) - 4, int(c) + 1)]:
        if s.get(x, y) == PLUM:
            s.put(x, y, BLACK)
    if mhc:
        for a in MHC_ANGLES:
            cast.lollipop(s, c, c, a, 7.0)
    if pdl1:
        for a in (math.radians(-160), math.radians(-20), math.radians(70)):
            cast.plug(s, c, c, a, 7.0)
    if ball:
        bx, by = int(c) - 2, int(c) + 3
        s.rect(bx, by, bx + 3, by + 2, PINK)
        s.put(bx + 1, by + 1, WHITE)
    return s


def tumor():
    f = {}
    base = Frame(_tumor(), 12, 23)
    for k, L in enumerate("ABCD"):
        f[L] = bob(Frame(_tumor(phase=k * 0.6), 12, 23), [0, -1, 0, 1][k] if k != 3 else 0)
    f["E"] = bob(Frame(_tumor(mouth=1, pdl1=True), 12, 23), 0)
    f["F"] = bob(Frame(_tumor(mouth=2, pdl1=True, ball=True), 12, 23), 0)
    f["G"] = bob(Frame(_tumor(mouth=1), 12, 23), 0)
    f["H"] = bob(Frame(flash(_tumor()), 12, 23), 0)
    for L, fr in zip("IJKLM", burst(base, 5, seed=31)):
        f[L] = fr
    for L, fr in zip("NOPQRSTU", burst(base, 8, seed=32, gib=True)):
        f[L] = fr
    return f


def tumor_ghost():
    """TUMOR NO MHC-I (spectre): same tumor without MHC-I lollipops (the bible's
    'tumor_no_mhc'); the engine draws it with the fuzz effect, so it's hard to see —
    exactly what losing MHC-I does to a T cell's view."""
    f = {}
    base = Frame(_tumor(mhc=False), 12, 23)
    for k, L in enumerate("ABCD"):
        f[L] = bob(Frame(_tumor(phase=k * 0.6, mhc=False), 12, 23), [0, -1, 0, 0][k])
    f["E"] = bob(Frame(_tumor(mouth=1, mhc=False), 12, 23), 0)
    f["F"] = bob(Frame(_tumor(mouth=3, mhc=False), 12, 23), 0)
    f["G"] = bob(Frame(_tumor(mouth=1, mhc=False), 12, 23), 0)
    f["H"] = bob(Frame(flash(_tumor(mhc=False)), 12, 23), 0)
    for L, fr in zip("IJKLMN", burst(base, 6, seed=41)):
        f[L] = fr
    return f


# ---------------------------------------------------------------- PARASITE (demon, SARG)

def _parasite(phase=0, mouth=0):
    W_, H_ = 32, 20
    s = Spr(W_, H_)
    sx = 1.0 + 0.06 * math.sin(phase * math.pi / 2)
    m = mask_superellipse(W_, H_, 15.0, 11.0, 12.5 * sx, 6.5 / sx, n=2.3)
    # tail lobe
    m |= mask_superellipse(W_, H_, 4.0, 12.0, 3.5, 3.0 + (phase % 2), n=2.0)
    if mouth:
        ys, xs = np.mgrid[0:H_, 0:W_]
        m &= ~((xs > 25) & (np.abs(ys + 0.5 - 12.0) < mouth * 1.3))
    paint_body(s, m, 15.0, 11.0, PEACH, BROWN, shade=PINK, hi=WHITE)
    outline(s, BLACK)
    # internal organs / spots
    for (x, y) in [(8, 11), (11, 13), (14, 9), (17, 14), (10, 9)]:
        s.put(x, y, LAV)
    # little hooks on the head
    for (x, y) in [(22, 4), (24, 5), (26, 6)]:
        s.put(x, y, LGREY)
    villain_face(s, 21, 9, open_mouth=0)
    if mouth:
        for k in range(-mouth, mouth + 1, 2):
            s.put(26, int(12 + k * 0.9), WHITE)
            s.put(28, int(12 + k * 0.9), WHITE)
    return s


def parasite():
    f = {}
    base = Frame(_parasite(), 16, 19)
    for k, L in enumerate("ABCD"):
        f[L] = bob(Frame(_parasite(phase=k), 16, 19), 0)
    f["E"] = bob(Frame(_parasite(mouth=1), 16, 19), 0)
    f["F"] = bob(Frame(_parasite(mouth=3), 16, 19), 0)
    f["G"] = bob(Frame(_parasite(mouth=2), 16, 19), 0)
    f["H"] = bob(Frame(flash(_parasite()), 16, 19), 0)
    for L, fr in zip("IJKLMN", burst(base, 6, seed=51, goo=(PEACH, PINK, BROWN))):
        f[L] = fr
    return f


# ---------------------------------------------------------------- PHAGE (lost soul, SKUL)

def _phage(phase=0, charge=False):
    W_, H_ = 22, 26
    s = Spr(W_, H_)
    c = 11.0
    # legs
    spread = 4 + (1 if phase else 0) + (2 if charge else 0)
    for side in (-1, 1):
        for k in range(3):
            x0, y0 = c + side * 1, 20
            for t in range(5):
                x = x0 + side * (t * spread / 4.0) * (0.6 + 0.3 * k)
                y = y0 + (t if t < 3 else 3) + (k - 1) * 0.3
                s.put(int(round(x)), int(round(y)), LAV)
    # tail
    s.rect(10, 13, 11, 19, LGREY)
    s.rect(8, 19, 13, 20, DGREY)
    for y in range(13, 19, 2):
        s.put(10, y, DGREY)
    # head
    ys, xs = np.mgrid[0:H_, 0:W_]
    dx, dy = np.abs(xs + 0.5 - c), np.abs(ys + 0.5 - 7.0)
    m = (dy <= 6.0) & (dx * 0.866 + dy * 0.5 <= 6.3)
    head = Spr(W_, H_)
    paint_body(head, m, c, 7.0, LGREY, RED if charge else LAV, shade=DGREY, hi=WHITE)
    s.stamp(head, 0, 0)
    villain_face(s, 11, 6, open_mouth=1 if charge else 0)
    outline(s, BLACK)
    return s


def phage():
    f = {}
    base = Frame(_phage(), 11, 25)
    f["A"] = Frame(_phage(0), 11, 25)
    f["B"] = Frame(_phage(1), 11, 25)
    f["C"] = Frame(_phage(0, charge=True), 11, 25)
    f["D"] = Frame(_phage(1, charge=True), 11, 25)
    f["E"] = Frame(flash(_phage()), 11, 25)
    for L, fr in zip("FGHIJK", burst(base, 6, seed=61, goo=(LGREY, LAV, WHITE))):
        f[L] = fr
    return f


# ---------------------------------------------------------------- FUNGAL SPORE (cacodemon, HEAD)

def _spore(mouth=0, glow=False, hurt=False):
    S = 34
    c = 17.0
    s = Spr(S, S)
    r = lambda a: 11.0 + 0.5 * np.sin(7 * a) + 0.3 * np.sin(11 * a + 1)
    m = mask_radial(S, S, c, c, r)
    paint_body(s, m, c, c, DGREEN, LGREY, shade=NAVY, hi=GREEN if not hurt else LGREY)
    # hyphae
    for k in range(11):
        a = k * 2 * math.pi / 11 + 0.2
        x0, y0 = c + math.cos(a) * 11.5, c + math.sin(a) * 11.5
        for t in range(3):
            s.put(int(x0 + math.cos(a) * t), int(y0 + math.sin(a) * t), LGREY)
        bx, by = x0 + math.cos(a) * 3, y0 + math.sin(a) * 3
        s.put(int(bx + math.cos(a + 1.2)), int(by + math.sin(a + 1.2)), LGREY)
        s.put(int(bx + math.cos(a - 1.2)), int(by + math.sin(a - 1.2)), LGREY)
    # spots
    for (x, y) in [(10, 12), (24, 11), (12, 23), (23, 24), (17, 8)]:
        s.put(x, y, GREEN); s.put(x + 1, y, NAVY)
    outline(s, BLACK)
    # face, larger than the small villains
    ci, cj = 17, 15
    for (x, y) in [(ci - 6, cj - 4), (ci - 5, cj - 3), (ci - 4, cj - 3), (ci + 3, cj - 3), (ci + 4, cj - 3), (ci + 5, cj - 4)]:
        s.put(x, y, BLACK)
    for ex in (ci - 5, ci + 3):
        s.rect(ex, cj - 2, ex + 1, cj - 1, BLACK)
        s.rect(ex, cj, ex + 1, cj, RED)
    if mouth == 0:
        s.rect(ci - 2, cj + 4, ci + 2, cj + 4, BLACK)
    else:
        s.rect(ci - 3, cj + 3, ci + 3, cj + 3 + mouth * 2, BLACK)
        for x in range(ci - 3, ci + 4, 2):
            s.put(x, cj + 3, WHITE)
        if glow:
            s.rect(ci - 1, cj + 4, ci + 1, cj + 2 + mouth * 2, GREEN)
            s.put(ci, cj + 3 + mouth, WHITE)
    return s


def spore():
    f = {}
    base = Frame(_spore(), 17, 33)
    f["A"] = Frame(_spore(), 17, 33)
    f["B"] = Frame(_spore(mouth=1), 17, 33)
    f["C"] = Frame(_spore(mouth=2, glow=True), 17, 33)
    f["D"] = Frame(_spore(mouth=3, glow=True), 17, 33)
    f["E"] = Frame(flash(_spore()), 17, 33)
    f["F"] = Frame(_spore(hurt=True), 17, 33)
    for L, fr in zip("GHIJKL", burst(base, 6, seed=71, goo=(DGREEN, GREEN, LGREY), power=1.2)):
        f[L] = fr
    return f


# ---------------------------------------------------------------- TUMOR MASS (baron, BOSS)

def _mass(phase=0.0, mouth=0, pdl1=False, ball=False):
    W_, H_ = 40, 38
    s = Spr(W_, H_)
    lobes = [(20, 22, 10.0), (11, 25, 7.0), (29, 25, 7.0), (14, 15, 6.5), (26, 15, 6.5), (20, 31, 6.0)]
    m = np.zeros((H_, W_), bool)
    for i, (x, y, r) in enumerate(lobes):
        rr = r * (1.0 + 0.05 * math.sin(phase + i * 1.7))
        m |= mask_radial(W_, H_, x, y, lambda a, rr=rr, i=i: rr + 0.6 * np.sin(3 * a + i) + 0.3 * np.sin(5 * a + 2 * i))
    cast.villain_body(s, m, 20, 22)
    # lobe seams
    for (x, y) in [(13, 20), (14, 21), (27, 20), (26, 21), (17, 29), (23, 29)]:
        s.put(x, y, BLACK)
    # crown of MHC-I
    for k in range(7):
        a = math.radians(-160 + 23.3 * k)
        cx, cy, r0 = 20, 22, 0
        # find the edge along the ray
        for rr in range(4, 20):
            x, y = int(cx + math.cos(a) * rr), int(cy + math.sin(a) * rr)
            if not (0 <= x < W_ and 0 <= y < H_) or not m[y, x]:
                r0 = rr
                break
        cast.lollipop(s, cx, cy, a, r0 + 0.5)
    if pdl1:
        for a in (math.radians(180), math.radians(0), math.radians(130), math.radians(50)):
            cast.plug(s, 20, 24, a, 11.5)
    # big face
    ci, cj = 20, 21
    for (x, y) in [(ci - 6, cj - 4), (ci - 5, cj - 3), (ci - 4, cj - 2), (ci + 3, cj - 2), (ci + 4, cj - 3), (ci + 5, cj - 4)]:
        s.put(x, y, BLACK)
    for ex in (ci - 5, ci + 3):
        s.rect(ex, cj - 1, ex + 1, cj, BLACK)
        s.rect(ex, cj + 1, ex + 1, cj + 1, RED)
    if mouth == 0:
        s.rect(ci - 2, cj + 5, ci + 2, cj + 5, BLACK)
    else:
        s.rect(ci - 3, cj + 4, ci + 3, cj + 4 + mouth * 2, BLACK)
        for x in range(ci - 3, ci + 4, 2):
            s.put(x, cj + 4, WHITE)
        if ball:
            s.rect(ci - 1, cj + 5, ci + 1, cj + 4 + mouth * 2, PINK)
            s.put(ci, cj + 5, WHITE)
    return s


def mass():
    f = {}
    base = Frame(_mass(), 20, 37)
    for k, L in enumerate("ABCD"):
        f[L] = Frame(_mass(phase=k * 1.4), 20, 37)
    f["E"] = Frame(_mass(mouth=1, pdl1=True), 20, 37)
    f["F"] = Frame(_mass(mouth=2, pdl1=True, ball=True), 20, 37)
    f["G"] = Frame(_mass(mouth=1, pdl1=True), 20, 37)
    f["H"] = Frame(flash(_mass()), 20, 37)
    for L, fr in zip("IJKLMNO", burst(base, 7, seed=81, power=1.4, gib=True)):
        f[L] = fr
    return f


ALL = {
    "POSS": virus,
    "SPOS": bacterium,
    "TROO": tumor,
    "SP00": tumor_ghost,
    "SARG": parasite,
    "SKUL": phage,
    "HEAD": spore,
    "BOSS": mass,
}
