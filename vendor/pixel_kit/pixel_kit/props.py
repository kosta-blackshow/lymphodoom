# Предметы: шприц, флакон, чашка Петри, мышь (сверху и сбоку), ДНК, глюкоза, таблетка,
# гранулы/перфорин, антитело-бонус. Плюс процедурные предметы из v7 (большая мышь, шприц).

import math
import numpy as np
from PIL import ImageDraw
from .palette import *
from .pixdraw import Spr, mask_circle, mask_radial, mask_superellipse, paint_body, outline


def syringe(liquid=BLUE):
    """Шприц сбоку, игла вправо. 26x5."""
    s = Spr(26, 5)
    s.ascii(0, 0, [
        "L.........................",
        "L.WWWWWWWWWWWW............",
        "LLWccccccccccWLLLLLLLLLLL.",
        "L.WWWWWWWWWWWW............",
        "L.........................",
    ], {"L": LGREY, "W": WHITE, "c": liquid})
    return s


def vial(liquid=BLUE):
    """Флакон (антисыворотка, лекарство): рисунок v7 в родном размере 8x10."""
    s = Spr(8, 10)
    s.ascii(0, 0, ["..5555..", "..6666..", "...77...", "..7..7..", ".7....7.",
                   ".7cccc7.", ".7cccc7.", ".7cccc7.", ".7cccc7.", "..7777.."],
            {"5": DGREY, "6": LGREY, "7": WHITE, "c": liquid})
    return s


def dish(cells=0):
    """Чашка Петри сверху, 24x24. cells — сколько точек-колоний внутри."""
    S = 24
    s = Spr(S, S)
    m = mask_circle(S, S, 12, 12, 11.5)
    s.a[m] = LGREY
    s.a[mask_circle(S, S, 12, 12, 10.5)] = LAV
    s.a[mask_circle(S, S, 12, 12, 9.5)] = NAVY
    for (x, y) in [(7, 5), (6, 6), (5, 7)]:
        s.put(x, y, WHITE)
    for (x, y) in [(15, 10), (9, 15), (13, 16), (16, 14), (10, 9), (8, 12)][:cells]:
        s.put(x, y, PLUM); s.put(x + 1, y, PLUM)
    return s


def mouse_top():
    """Мышь сверху (голова вверх), 18x34."""
    w, h = 18, 34
    s = Spr(w, h)
    for k in range(26, h):
        s.put(9 + round(1.5 * math.sin((k - 26) / 2.0)), k, PINK)
    for (x, y) in [(2, 12), (15, 12), (3, 22), (14, 22)]:
        s.rect(x, y, x, y + 1, PINK)
    m = mask_superellipse(w, h, 9, 17.5, 6.5, 9.0, n=2.2)
    paint_body(s, m, 9, 17.5, LGREY, DGREY, shade=None, hi=WHITE)
    for ex in (4, 14):
        e = mask_circle(w, h, ex + 0.5, 5.5, 2.6)
        s.a[e] = LGREY
        s.a[mask_circle(w, h, ex + 0.5, 5.5, 1.4)] = PINK
    hm = mask_radial(w, h, 9.0, 7.0, lambda a: 4.4 + 1.6 * np.maximum(0, -np.sin(a)) ** 4)
    paint_body(s, hm, 9.0, 7.0, LGREY, DGREY)
    s.put(7, 6, BLACK); s.put(11, 6, BLACK)
    s.put(9, 1, PINK)
    return s


def mouse_side():
    """Мышь сбоку (мордой вправо), 30x16."""
    w, h = 30, 16
    s = Spr(w, h)
    for k in range(8):
        s.put(k, 6 + round(4 * (k / 7) ** 2), PINK)
    for x in (10, 18):
        s.rect(x, 13, x + 1, 14, PINK)
    m = mask_superellipse(w, h, 15, 9, 8.5, 5.0, n=2.2)
    m |= mask_radial(w, h, 23.0, 8.0, lambda a: 4.0 + 2.0 * np.maximum(0, np.cos(a)) ** 6)
    paint_body(s, m, 15, 9, LGREY, DGREY, shade=None, hi=WHITE)
    s.a[mask_circle(w, h, 21.5, 3.5, 2.6)] = LGREY
    s.a[mask_circle(w, h, 21.5, 3.5, 1.4)] = PINK
    s.put(25, 7, BLACK)
    s.put(29, 8, PINK)
    return s


def dna(mutated=False):
    """Двойная спираль, 9x16. mutated — одна «ступенька» с меткой мутации."""
    s = Spr(9, 16)
    for y in range(16):
        k = math.sin(y * 0.55)
        x1, x2 = round(4 + 3.4 * k), round(4 - 3.4 * k)
        if y % 2 == 0 and abs(x1 - x2) > 1:
            for x in range(min(x1, x2) + 1, max(x1, x2)):
                s.put(x, y, ORANGE if (mutated and y == 8) else DGREY)
        front = k > 0
        s.put(x2, y, LAV if front else DGREY)
        s.put(x1, y, WHITE if front else LGREY)
    if mutated:
        s.put(0, 7, ORANGE); s.put(8, 9, ORANGE)
    return s


def glucose():
    """Молекула глюкозы — ресурс, за который спорят клетки (гл. 5). Шестиугольник 7x7."""
    s = Spr(7, 7)
    s.ascii(0, 0, ["..www..", ".w...w.", "w.....w", "w.....w", "w.....w", ".w...w.", "..www.."], {"w": WHITE})
    return s


def pill(col=ORANGE):
    """Таблетка-ингибитор (иматиниб и т. п.), 10x5."""
    s = Spr(10, 5)
    s.ascii(0, 0, [".kkkkkkkk.", "kwwwwcccck", "kwwwwcccck", "kwwwwcccck", ".kkkkkkkk."],
            {"k": BLACK, "w": WHITE, "c": col})
    return s


def granule(col=BLUE, k=0):
    """Гранула (перфорин/гранзимы) — снаряд иммунной клетки. 3 кадра пульсации, 5x5."""
    s = Spr(5, 5)
    if k == 0:
        s.ascii(0, 0, [".....", "..c..", ".cwc.", "..c..", "....."], {"c": col, "w": WHITE})
    elif k == 1:
        s.ascii(0, 0, ["..c..", ".cwc.", "cwwwc", ".cwc.", "..c.."], {"c": col, "w": WHITE})
    else:
        s.ascii(0, 0, [".....", ".c.c.", "..w..", ".c.c.", "....."], {"c": col, "w": WHITE})
    return s


def antibody_bonus(k=0):
    """Антитело — ингибитор контрольной точки как предмет-бонус. 2 кадра блеска, 11x11."""
    s = Spr(11, 11)
    s.ascii(0, 0, [
        "w.......w..",
        "bw.....wb..",
        ".bw...wb...",
        "..bw.wb....",
        "...bwb.....",
        "....w......",
        "....w......",
        "....w......",
        "....b......",
        "...........",
        "...........",
    ], {"w": WHITE, "b": BLUE})
    if k == 0:
        s.put(8, 8, YELLOW); s.put(9, 7, YELLOW); s.put(9, 8, YELLOW); s.put(9, 9, YELLOW); s.put(10, 8, YELLOW)
    else:
        s.put(9, 8, WHITE)
    return s


def chromosome(kind="normal"):
    """Хромосома 5x11: normal; 'ph' — маленькая филадельфийская (гл. 6)."""
    if kind == "ph":
        s = Spr(5, 6)
        s.ascii(0, 0, [".ll..", "llll.", ".ol..", "llll.", ".ll..", "....."], {"l": LGREY, "o": ORANGE})
        return s
    s = Spr(5, 11)
    s.ascii(0, 0, [".ll..", "llll.", "llll.", "llll.", ".ll..", ".ll..", "llll.", "llll.", "llll.", "llll.", ".ll.."],
            {"l": LGREY})
    return s


# ---------------------------------------------------------------- процедурные предметы v7

def mouse_top_v7(img, cx, cy):
    """Большая мышь сверху из v7 (голова вверху, хвост внизу), рисуется прямо в кадр."""
    d = ImageDraw.Draw(img)
    pts = [(cx + int(10 * math.sin(k / 6)), cy + 46 + k) for k in range(0, 46)]
    for (x, y) in pts:
        d.rectangle([x, y, x + 1, y], fill=C(PINK))
    d.ellipse([cx - 36, cy - 30, cx + 36, cy + 52], fill=C(LGREY))
    d.ellipse([cx - 36, cy - 30, cx + 36, cy + 52], outline=C(DGREY))
    d.ellipse([cx - 24, cy - 16, cx + 6, cy + 20], fill=C(WHITE))
    d.ellipse([cx - 20, cy - 66, cx + 20, cy - 20], fill=C(LGREY), outline=C(DGREY))
    d.polygon([(cx - 8, cy - 66), (cx + 8, cy - 66), (cx, cy - 78)], fill=C(LGREY))
    d.point([cx, cy - 78], fill=C(PINK))
    for s in (-1, 1):
        d.ellipse([cx + s * 22 - 11, cy - 58 - 11, cx + s * 22 + 11, cy - 58 + 11], fill=C(LGREY), outline=C(DGREY))
        d.ellipse([cx + s * 22 - 6, cy - 58 - 6, cx + s * 22 + 6, cy - 58 + 6], fill=C(PINK))
        d.rectangle([cx + s * 8 - 1, cy - 56, cx + s * 8 + 1, cy - 54], fill=C(BLACK))
    for s in (-1, 1):
        for yy in (cy - 18, cy + 40):
            d.rectangle([cx + s * 38 - 3, yy, cx + s * 38 + 3, yy + 4], fill=C(PINK))


def syringe_v7(img, x, y, direction):
    """Большой шприц из v7. direction: 1 — игла вправо, -1 — влево; (x, y) — кончик иглы."""
    d = ImageDraw.Draw(img)
    s = direction
    x1 = x - s * 40
    d.rectangle([min(x, x1 + s * 12), y - 1, max(x, x1 + s * 12), y], fill=C(LGREY))
    d.rectangle([min(x1 + s * 12, x1 - s * 14), y - 5, max(x1 + s * 12, x1 - s * 14), y + 4], fill=C(WHITE), outline=C(LGREY))
    d.rectangle([min(x1 - s * 14, x1 - s * 22), y - 1, max(x1 - s * 14, x1 - s * 22), y], fill=C(LGREY))
    d.rectangle([x1 - s * 24 - 1, y - 6, x1 - s * 24 + 1, y + 5], fill=C(LGREY))
