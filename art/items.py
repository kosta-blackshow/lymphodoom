"""Pickups, projectiles, effects and decorations (world sprites, bible pixels, x3)."""
import math
import random

import numpy as np

from common import *  # noqa: F401,F403
from common import Frame, burst, flash, pad
from pixel_kit import props


def _hex(s, cx, cy, r, col=WHITE, fill=None):
    """Glucose ring (bible glucose: white hexagon)."""
    pts = [(cx + r * math.cos(math.radians(60 * k + 30)), cy + r * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    if fill is not None:
        ys, xs = np.mgrid[0:s.h, 0:s.w]
        dx, dy = np.abs(xs + 0.5 - cx), np.abs(ys + 0.5 - cy)
        m = (dx <= r * 0.87) & (dx * 0.5 + dy * 0.866 <= r * 0.87)
        s.a[m] = fill
    for k in range(6):
        x0, y0 = pts[k]
        x1, y1 = pts[(k + 1) % 6]
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for t in range(n + 1):
            s.put(int(x0 + (x1 - x0) * t / n), int(y0 + (y1 - y0) * t / n), col)


def floor_frame(s):
    return Frame(s, s.w / 2, s.h)


def glucose_small():
    s = Spr(9, 9)
    _hex(s, 4.5, 4.5, 3.6, WHITE, fill=BLUE)
    outline(s, BLACK)
    return {"A": floor_frame(s)}


def glucose_big():
    s = Spr(17, 13)
    _hex(s, 4.5, 8.0, 3.6, WHITE, fill=BLUE)
    _hex(s, 12.0, 8.0, 3.6, WHITE, fill=BLUE)
    _hex(s, 8.3, 4.0, 3.6, WHITE, fill=BLUE)
    outline(s, BLACK)
    return {"A": floor_frame(s)}


def glucose_tiny():
    f = {}
    for k, L in enumerate("ABCD"):
        s = Spr(7, 8)
        _hex(s, 3.5, 4.0, 2.6, WHITE if k != 2 else YELLOW, fill=[BLUE, BLUE, WHITE, BLUE][k])
        outline(s, BLACK)
        f[L] = floor_frame(s)
    return f


def _membrane(s, cx, cy, rx, ry, head=PEACH, tail=LGREY, rings=1):
    """Lipid bilayer ring: heads outside, tails inside (armour = cell membrane)."""
    for ring in range(rings):
        k = ring * 2.2
        for a in range(0, 360, 14):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            s.put(int(cx + ca * (rx - k)), int(cy + sa * (ry - k * ry / rx)), head)
            s.put(int(cx + ca * (rx - k - 1)), int(cy + sa * (ry - (k + 1) * ry / rx)), tail)


def membrane_bonus():
    f = {}
    for k, L in enumerate("ABCD"):
        s = Spr(9, 9)
        _membrane(s, 4.5, 4.5, 3.6, 3.6, head=[PEACH, PEACH, WHITE, PEACH][k])
        outline(s, BLACK)
        f[L] = floor_frame(s)
    return f


def membrane_armor(blue=False):
    f = {}
    for k, L in enumerate("AB"):
        s = Spr(19, 15)
        _membrane(s, 9.5, 7.5, 8.5, 6.5, head=(BLUE if blue else PEACH) if k == 0 else WHITE,
                  tail=LGREY, rings=2 if blue else 1)
        s.a[mask_superellipse(19, 15, 9.5, 7.5, 4.0, 3.0, n=2)] = LAV if blue else PINK
        outline(s, BLACK)
        f[L] = floor_frame(s)
    return f


def il2_surge():
    """Soulsphere -> IL-2 SURGE: helper-T cytokine burst (orange)."""
    f = {}
    for k, L in enumerate("ABCD"):
        s = Spr(17, 17)
        r = 5 + (k % 2)
        s.a[mask_circle(17, 17, 8.5, 8.5, r)] = ORANGE
        s.a[mask_circle(17, 17, 8.5, 8.5, r - 2)] = YELLOW if k % 2 else PEACH
        s.a[mask_circle(17, 17, 7.5, 7.5, 1.5)] = WHITE
        for a in range(0, 360, 45):
            x, y = 8.5 + math.cos(math.radians(a + k * 11)) * 7.6, 8.5 + math.sin(math.radians(a + k * 11)) * 7.6
            s.put(int(x), int(y), ORANGE)
        outline(s, BLACK)
        f[L] = Frame(s, 8.5, 20)
    return f


def mucus_suit():
    s = Spr(15, 19)
    m = mask_superellipse(15, 19, 7.5, 10.0, 6.0, 8.5, n=2.2)
    paint_body(s, m, 7.5, 10, DGREEN, GREEN, shade=NAVY, hi=WHITE)
    for (x, y) in [(5, 6), (9, 9), (6, 13), (10, 15)]:
        s.put(x, y, GREEN)
    outline(s, BLACK)
    return {"A": floor_frame(s)}


def scout_map():
    """Computer map -> SCOUT: a dendritic cell (bible hero) that knows the area."""
    f = {}
    for k, L in enumerate("ABCD"):
        d = cast.dendritic(look=1 if k % 2 else -1, blink=(k == 3))
        f[L] = Frame(d, d.w / 2, d.h)
    return f


def mhc_key(cap):
    """Keycards -> MHC-I badges. cap: peptide colour (WHITE self / ORANGE neo / none)."""
    f = {}
    for k, L in enumerate("AB"):
        s = Spr(9, 12)
        stem = YELLOW
        body = YELLOW if cap != "white" else WHITE
        s.rect(2, 2, 6, 5, body)
        s.rect(4, 6, 4, 10, body)
        s.rect(3, 10, 5, 10, body)
        if cap == "orange":
            s.rect(3, 0, 5, 1, ORANGE)
        elif cap == "yellow":
            s.rect(3, 0, 5, 1, WHITE)
        else:
            s.rect(3, 0, 5, 1, LGREY)
        if k == 1:
            s.put(3, 3, WHITE if body != WHITE else LGREY)
        outline(s, BLACK)
        f[L] = Frame(s, 4.5, 14)
    return f


# ---------------------------------------------------------------- ammo

def granule_sac(n=3, w=9, h=8):
    s = Spr(w, h)
    m = mask_superellipse(w, h, w / 2, h / 2, w / 2 - 0.5, h / 2 - 0.5, n=2.2)
    paint_body(s, m, w / 2, h / 2, LAV, WHITE, shade=NAVY)
    rnd = random.Random(n)
    pts = [(w // 2 - 2, h // 2), (w // 2 + 1, h // 2 - 1), (w // 2, h // 2 + 1), (w // 2 - 1, h // 2 - 2),
           (w // 2 + 2, h // 2 + 1), (w // 2 - 3, h // 2 + 1), (w // 2 + 3, h // 2 - 1), (w // 2 + 1, h // 2 + 2)]
    for i, (x, y) in enumerate(pts[:n]):
        s.put(x, y, BLUE if i % 2 else GREEN)
    outline(s, BLACK)
    return {"A": floor_frame(s)}


def vesicles(n):
    s = Spr(4 + 4 * min(n, 3), 5 + 4 * (n > 3))
    for i in range(n):
        x, y = 2 + (i % 3) * 4, 2 + (i // 3) * 4
        s.ascii(x - 1, y - 1, [".c.", "cwc", ".c."], {"c": ORANGE, "w": PEACH})
    outline(s, BLACK)
    return {"A": floor_frame(s)}


def antibodies(n):
    s = Spr(10 * n, 10)
    for i in range(n):
        x = i * 10
        s.ascii(x, 1, [
            "w.......w",
            "bw.....wb",
            ".bw...wb.",
            "..bw.wb..",
            "...bwb...",
            "....w....",
            "....w....",
            "....b....",
        ], {"w": WHITE, "b": BLUE})
    s.put(10 * n - 2, 7, YELLOW)
    outline(s, BLACK)
    return {"A": floor_frame(s)}


def interferon(big=False):
    w, h = (15, 11) if big else (9, 9)
    s = Spr(w, h)
    m = mask_superellipse(w, h, w / 2, h / 2, w / 2 - 0.5, h / 2 - 0.5, n=3)
    paint_body(s, m, w / 2, h / 2, BLUE, LAV, shade=NAVY, hi=WHITE)
    s.a[mask_circle(w, h, w / 2, h / 2, 1.6)] = WHITE
    outline(s, BLACK)
    return {"A": floor_frame(s)}


def atp_pack():
    s = Spr(15, 15)
    m = mask_circle(15, 15, 7.5, 8, 6.5)
    paint_body(s, m, 7.5, 8, PEACH, BROWN, shade=PINK, hi=WHITE)
    for i, c in enumerate((BLUE, ORANGE, GREEN)):
        s.put(5 + i * 2, 8, c); s.put(5 + i * 2, 9, c)
    s.rect(6, 1, 9, 2, BROWN)
    outline(s, BLACK)
    return {"A": floor_frame(s)}


# ---------------------------------------------------------------- weapon pickups

def pickup_from_weapon(spr):
    """Weapon pickups: the organelle alone, lying on the floor (cropped, shrunk)."""
    a = spr.a
    ys, xs = np.nonzero(a >= 0)
    sub = Spr(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
    sub.a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    sm = scale(sub, 0.6)
    return {"A": floor_frame(sm)}


def weapon_pickups():
    import weapons
    out = {}
    # organelles only (top part of the idle frame)
    def top(fn, k=0, keep=0.6):
        s, l, t = fn(k)
        cut = int(s.h * keep)
        o = Spr(s.w, cut)
        o.a = s.a[:cut].copy()
        outline(o, BLACK)
        return o
    out["SHOT"] = pickup_from_weapon(top(weapons.shotgun, 0, 0.55))
    out["MGUN"] = pickup_from_weapon(top(weapons.chaingun, 0, 0.55))
    out["LAUN"] = pickup_from_weapon(top(weapons.launcher, 0, 0.55))
    out["PLAS"] = pickup_from_weapon(top(weapons.plasma, 0, 0.55))
    out["BFUG"] = pickup_from_weapon(top(weapons.bfg, 0, 0.45))
    out["CSAW"] = out["SHOT"]
    return out


# ---------------------------------------------------------------- projectiles & effects

def goo_ball(body=PLUM, rim=RED, hi=PINK, r=3.4, n_exp=3, seed=1):
    f = {}
    for k, L in enumerate("AB"):
        S = int(r * 2 + 4)
        s = Spr(S, S)
        m = mask_radial(S, S, S / 2, S / 2, lambda a, k=k: r + 0.5 * np.sin(4 * a + k * 1.5))
        paint_body(s, m, S / 2, S / 2, body, rim, hi=hi)
        s.put(int(S / 2) - 1, int(S / 2) - 1, WHITE)
        f[L] = Frame(s, S / 2, S / 2 + 2)
    base = Frame(f["A"].spr, f["A"].ax, f["A"].spr.h)
    ex = burst(base, n_exp + 1, seed=seed, goo=(body, rim, hi), power=0.9)
    for L, fr in zip("CDE", ex[:n_exp]):
        fr.ay = fr.spr.h * 0.6
        f[L] = fr
    return f


def puff():
    """Bullet puff -> granule impact sparkle."""
    f = {}
    for k, L in enumerate("ABCD"):
        s = Spr(9, 9)
        r = [1, 2, 3, 4][k]
        for a in range(0, 360, 45):
            x, y = 4.5 + math.cos(math.radians(a)) * r, 4.5 + math.sin(math.radians(a)) * r
            s.put(int(x), int(y), [WHITE, BLUE, GREEN, LAV][k])
        if k < 2:
            s.put(4, 4, WHITE)
        f[L] = Frame(s, 4.5, 6)
    return f


def blood():
    f = {}
    for k, L in enumerate("ABC"):
        s = Spr(7, 9)
        for (x, y) in [(3, 2), (2, 4), (4, 5), (3, 7)][: 4 - k]:
            s.put(x, y + k, PLUM); s.put(x + 1, y + k, PINK)
        f[L] = Frame(s, 3.5, 6)
    return f


def antibody_rocket():
    f = {}
    s = Spr(11, 10)
    s.ascii(1, 1, [
        "w.......w",
        "bw.....wb",
        ".bw...wb.",
        "..bw.wb..",
        "...bwb...",
        "....w....",
        "....w....",
        "....y....",
    ], {"w": WHITE, "b": BLUE, "y": YELLOW})
    outline(s, BLACK)
    f["A"] = Frame(s, 5.5, 7)
    base = Frame(Spr(14, 14), 7, 14)
    base.spr.a[mask_circle(14, 14, 7, 7, 6)] = BLUE
    ex = burst(base, 4, seed=91, goo=(BLUE, WHITE, YELLOW), power=1.3)
    for L, fr in zip("BCD", ex[1:]):
        fr.ay = fr.spr.h * 0.6
        f[L] = fr
    return f


def interferon_shot():
    f = {}
    for k, L in enumerate("AB"):
        s = Spr(9, 9)
        s.a[mask_circle(9, 9, 4.5, 4.5, 3.5)] = BLUE
        s.a[mask_circle(9, 9, 4.5, 4.5, 2.0 + k)] = WHITE
        f[L] = Frame(s, 4.5, 6)
    return f


def ring_burst(cols, n, R=8):
    f = {}
    for k in range(n):
        S = R * 2 + 3
        s = Spr(S, S)
        r = 1.5 + (R - 1.5) * k / max(1, n - 1)
        for a in range(0, 360, 20):
            x, y = S / 2 + math.cos(math.radians(a + k * 9)) * r, S / 2 + math.sin(math.radians(a + k * 9)) * r
            if k < n - 1 or a % 40 == 0:
                s.put(int(x), int(y), cols[(a // 20 + k) % len(cols)])
        if k < 2:
            s.a[mask_circle(S, S, S / 2, S / 2, 2.0)] = WHITE
        f[chr(65 + k)] = Frame(s, S / 2, S / 2 + 3)
    return f


def cart_ball():
    f = {}
    for k, L in enumerate("AB"):
        s = Spr(17, 17)
        s.a[mask_circle(17, 17, 8.5, 8.5, 7.5)] = GREEN
        s.a[mask_circle(17, 17, 8.5, 8.5, 5.5 + k)] = WHITE
        s.a[mask_circle(17, 17, 8.5, 8.5, 2.5)] = YELLOW
        outline(s, BLACK)
        f[L] = Frame(s, 8.5, 10)
    return f


def sparkle_fog(n=10, cols=(WHITE, GREEN, BLUE)):
    f = {}
    rnd = random.Random(7)
    pts = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(18)]
    for k in range(n):
        s = Spr(15, 25)
        t = k / max(1, n - 1)
        for i, (px, py) in enumerate(pts):
            if (i + k) % 3 == 0 and t > 0.8:
                continue
            x, y = 7.5 + px * 6 * (0.3 + t), 14 + py * 9 * (0.3 + t) - t * 6
            s.put(int(x), int(y), cols[(i + k) % len(cols)])
        f[chr(65 + k)] = Frame(s, 7.5, 25)
    return f


# ---------------------------------------------------------------- decorations

def toxin_sac():
    f = {}
    for k, L in enumerate("AB"):
        s = Spr(15, 19)
        m = mask_superellipse(15, 19, 7.5, 10.5, 6.2, 8.0 + k * 0.4, n=2.2)
        paint_body(s, m, 7.5, 10.5, DGREEN, GREEN, shade=NAVY, hi=WHITE)
        for (x, y) in [(5, 8), (9, 12), (6, 14), (8, 6)]:
            s.put(x, y + k, YELLOW if (x + k) % 2 else GREEN)
        s.rect(6, 1, 9, 2, LGREY)
        outline(s, BLACK)
        f[L] = Frame(s, 7.5, 19)
    return f


def toxin_explosion():
    base = toxin_sac()["A"]
    ex = burst(base, 6, seed=101, goo=(DGREEN, GREEN, YELLOW), power=1.5)
    return {L: fr for L, fr in zip("ABCDE", ex[:5])}


def civilian(fn, **kw):
    s = fn(**kw)
    return {"A": Frame(s, s.w / 2, s.h)}


def civilian_anim(fn, letters="ABCD"):
    f = {}
    for k, L in enumerate(letters):
        s = fn(blink=(k == 3))
        if k in (1, 2):
            s = pad(s, 0, 1, 0, 0) if k == 1 else s
        f[L] = Frame(s, s.w / 2, s.h)
    return f


def stem_glow():
    s = cast.stem()
    s = pad(s, 1, 1, 1, 1)
    # glowing halo: the stem cell is the 'lamp' of the tissue
    halo = Spr(s.w, s.h)
    m = s.a >= 0
    g = m.copy()
    g[1:, :] |= m[:-1, :]; g[:-1, :] |= m[1:, :]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]
    s.a[g & ~m] = YELLOW
    return {"A": Frame(s, s.w / 2, s.h)}


def rbc():
    """Red blood cell (drawn pink: red is reserved for villains in the bible)."""
    s = Spr(13, 7)
    m = mask_superellipse(13, 7, 6.5, 3.5, 6.0, 3.0, n=2.0)
    paint_body(s, m, 6.5, 3.5, PINK, PLUM, hi=PEACH)
    s.rect(4, 3, 8, 3, PLUM)
    outline(s, BLACK)
    return {"A": Frame(s, 6.5, 7)}


def collagen():
    s = Spr(9, 40)
    for y in range(40):
        x = 4 + round(2.2 * math.sin(y * 0.45))
        s.put(x, y, PEACH); s.put(x + 1, y, BROWN)
        x2 = 4 + round(2.2 * math.sin(y * 0.45 + math.pi))
        s.put(x2, y, WHITE); s.put(x2 - 1, y, LGREY)
    outline(s, BLACK)
    return {"A": Frame(s, 4.5, 40)}


def debris_pool():
    s = Spr(21, 5)
    for x in range(21):
        h = 1 + int(2 * math.sin(math.pi * x / 20))
        for y in range(h):
            s.put(x, 4 - y, PLUM if y < h - 1 else PINK)
    s.put(6, 2, LAV); s.put(13, 1, LAV)
    return {"A": Frame(s, 10.5, 5)}


def all_items():
    W_ = {}
    W_["STIM"] = glucose_small()
    W_["MEDI"] = glucose_big()
    W_["BON1"] = glucose_tiny()
    W_["BON2"] = membrane_bonus()
    W_["ARM1"] = membrane_armor(False)
    W_["ARM2"] = membrane_armor(True)
    W_["SOUL"] = il2_surge()
    W_["SUIT"] = mucus_suit()
    W_["PMAP"] = scout_map()
    W_["BKEY"] = mhc_key("white")
    W_["YKEY"] = mhc_key("yellow")
    W_["RKEY"] = mhc_key("orange")
    W_["CLIP"] = granule_sac(3)
    W_["AMMO"] = granule_sac(8, 15, 11)
    W_["SHEL"] = vesicles(2)
    W_["SBOX"] = vesicles(6)
    W_["ROCK"] = antibodies(1)
    W_["BROK"] = antibodies(3)
    W_["CELL"] = interferon(False)
    W_["CELP"] = interferon(True)
    W_["BPAK"] = atp_pack()
    W_.update(weapon_pickups())
    W_["BAL1"] = goo_ball(seed=111)
    W_["BAL2"] = goo_ball(DGREEN, GREEN, LGREY, r=3.8, seed=112)
    W_["BAL7"] = goo_ball(PLUM, RED, YELLOW, r=4.6, seed=113)
    W_["PUFF"] = puff()
    W_["BLUD"] = blood()
    W_["MISL"] = antibody_rocket()
    W_["PLSS"] = interferon_shot()
    W_["PLSE"] = ring_burst((BLUE, WHITE, LAV), 5)
    W_["BFS1"] = cart_ball()
    W_["BFE1"] = ring_burst((GREEN, WHITE, YELLOW), 6, R=12)
    W_["BFE2"] = ring_burst((GREEN, WHITE), 4, R=6)
    W_["TFOG"] = sparkle_fog(10)
    W_["IFOG"] = sparkle_fog(5, (WHITE, ORANGE))
    W_["BAR1"] = toxin_sac()
    W_["BEXP"] = toxin_explosion()
    W_["COLU"] = stem_glow()
    W_["CAND"] = rbc()
    W_["CBRA"] = civilian(cast.epithelial)
    W_["ELEC"] = collagen()
    W_["TLMP"] = civilian_anim(cast.granulocyte)
    W_["TLP2"] = civilian_anim(cast.senescent)
    W_["POL5"] = debris_pool()
    return W_
