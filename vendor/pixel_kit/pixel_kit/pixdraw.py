# Примитивы для рисования спрайтов в индексах палитры.
# Спрайт — массив индексов PICO-8, -1 = прозрачно. Тела клеток строятся из маски:
# заливка, ободок по краю, тень снизу-справа, блик сверху-слева.

import math
import numpy as np
from PIL import Image
from .palette import P, BLACK

T = -1


class Spr:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.full((h, w), T, np.int16)

    def put(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = c

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return int(self.a[y, x])
        return T

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def ascii(self, x0, y0, rows, key):
        """rows: строки; key: символ -> индекс палитры ('.' и ' ' — прозрачно)."""
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch in key:
                    self.put(x0 + x, y0 + y, key[ch])

    def stamp(self, other, x0, y0):
        m = other.a >= 0
        for y, x in zip(*np.nonzero(m)):
            self.put(x0 + x, y0 + y, other.a[y, x])

    def flip(self):
        s = Spr(self.w, self.h)
        s.a = self.a[:, ::-1].copy()
        return s

    def recolor(self, mapping):
        s = Spr(self.w, self.h)
        s.a = self.a.copy()
        for k, v in mapping.items():
            s.a[self.a == k] = v
        return s

    def image(self, scale=1):
        rgba = np.zeros((self.h, self.w, 4), np.uint8)
        for i, col in enumerate(P):
            rgba[self.a == i] = col + (255,)
        im = Image.fromarray(rgba, "RGBA")
        if scale > 1:
            im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        return im


# ---------------------------------------------------------------- маски

def mask_radial(w, h, cx, cy, rfun, sx=1.0, sy=1.0):
    ys, xs = np.mgrid[0:h, 0:w]
    dx = (xs + 0.5 - cx) / sx
    dy = (ys + 0.5 - cy) / sy
    d = np.hypot(dx, dy)
    a = np.arctan2(dy, dx)
    return d <= rfun(a)


def mask_circle(w, h, cx, cy, r, sx=1.0, sy=1.0):
    return mask_radial(w, h, cx, cy, lambda a: r, sx, sy)


def mask_superellipse(w, h, cx, cy, rx, ry, n=4.0):
    ys, xs = np.mgrid[0:h, 0:w]
    dx = np.abs(xs + 0.5 - cx) / rx
    dy = np.abs(ys + 0.5 - cy) / ry
    return dx ** n + dy ** n <= 1.0


def mask_capsule(w, h, x0, y0, x1, y1, r):
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = xs + 0.5, ys + 0.5
    vx, vy = x1 - x0, y1 - y0
    L = vx * vx + vy * vy or 1e-9
    t = np.clip(((px - x0) * vx + (py - y0) * vy) / L, 0, 1)
    return np.hypot(px - (x0 + t * vx), py - (y0 + t * vy)) <= r


def erode(m):
    e = m.copy()
    e[1:, :] &= m[:-1, :]
    e[:-1, :] &= m[1:, :]
    e[:, 1:] &= m[:, :-1]
    e[:, :-1] &= m[:, 1:]
    e[0, :] = e[-1, :] = False
    e[:, 0] = e[:, -1] = False
    return e & m


def paint_body(s, m, cx, cy, body, rim, shade=None, hi=None, rim_hi=None, rim_hi_k=-3.0, shade_k=2.0):
    """Заливает маску: ободок, тень (второе кольцо снизу-справа), блик (сверху-слева).
    rim_hi — цвет ободка на верхне-левой дуге (красный блик у злодеев)."""
    inner = erode(m)
    edge = m & ~inner
    ring2 = inner & ~erode(inner)
    ys, xs = np.mgrid[0:s.h, 0:s.w]
    dsum = (xs + 0.5 - cx) + (ys + 0.5 - cy)
    s.a[inner] = body
    if shade is not None:
        s.a[ring2 & (dsum > shade_k)] = shade
    if hi is not None:
        s.a[ring2 & (dsum < -shade_k - 2)] = hi
    s.a[edge] = rim
    if rim_hi is not None:
        s.a[edge & (dsum < rim_hi_k)] = rim_hi
    return inner


def outline(s, col=BLACK):
    """Обводка 1 px вокруг непрозрачных пикселей (снаружи)."""
    m = s.a >= 0
    grow = m.copy()
    grow[1:, :] |= m[:-1, :]
    grow[:-1, :] |= m[1:, :]
    grow[:, 1:] |= m[:, :-1]
    grow[:, :-1] |= m[:, 1:]
    s.a[grow & ~m] = col


def polar(cx, cy, a, r):
    return int(math.floor(cx + math.cos(a) * r)), int(math.floor(cy + math.sin(a) * r))


def from_image(im):
    """RGBA-картинка в палитре PICO-8 -> Spr (прозрачное -> -1). Чужой цвет — ошибка."""
    im = im.convert("RGBA")
    a = np.asarray(im)
    s = Spr(im.width, im.height)
    lut = {tuple(c): i for i, c in enumerate(P)}
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, al = a[y, x]
            if al == 0:
                continue
            key = (int(r), int(g), int(b))
            if key not in lut:
                raise ValueError(f"цвет {key} в ({x},{y}) не из палитры PICO-8")
            s.a[y, x] = lut[key]
    return s


def scale(s, sx, sy=None):
    """Масштаб nearest вокруг центра (для деления и сжатия при апоптозе)."""
    sy = sx if sy is None else sy
    w, h = max(1, round(s.w * sx)), max(1, round(s.h * sy))
    out = Spr(w, h)
    for y in range(h):
        for x in range(w):
            out.a[y, x] = s.a[min(s.h - 1, int((y + 0.5) / sy)), min(s.w - 1, int((x + 0.5) / sx))]
    return out


def silhouette(s, col):
    out = Spr(s.w, s.h)
    out.a[s.a >= 0] = col
    return out


def dominant(s, skip=(0,)):
    vals, cnt = np.unique(s.a[s.a >= 0], return_counts=True)
    order = [v for _, v in sorted(zip(cnt, vals), reverse=True) if v not in skip]
    return int(order[0]) if order else 0
