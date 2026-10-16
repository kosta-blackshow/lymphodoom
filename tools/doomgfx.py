"""Palette, colormap and Doom picture/flat encoding for LYMPHODOOM.

Palette layout: 16 rows x 16 shades. Row r is PICO-8 colour r, shade 0 is the
pure colour, shades 1..15 fade towards FOG (a dark navy, like the bible's
muted backgrounds). Row 0 (black) holds a neutral grey ramp instead, which the
colormap and translation tables use for greys.

Sprites are drawn only with the 16 pure colours (index r*16); textures may use
any shade.
"""
import os
import struct
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("PIXEL_KIT", os.path.join(HERE, "..", "vendor", "pixel_kit")))
from pixel_kit.palette import P  # noqa: E402

FOG = np.array([6, 7, 18], float)


def build_palette():
    pal = np.zeros((256, 3), float)
    for r in range(16):
        base = np.array(P[r], float)
        for s in range(16):
            if r == 0:
                v = 0 if s == 0 else 8 + s * 15
                pal[s] = (v, v, v)
            else:
                f = 1.0 - s / 16.0
                pal[r * 16 + s] = FOG + (base - FOG) * f
    return np.clip(np.round(pal), 0, 255).astype(np.uint8)


PAL = build_palette()
PALF = PAL.astype(float)


def idx(c, shade=0):
    """Palette index of PICO-8 colour c at shade (0 = pure)."""
    if c == 0:
        return 0
    return c * 16 + shade


def _weights():
    return np.array([0.30, 0.59, 0.11]) * 3


W = _weights()


def nearest(rgb, exclude_black_ramp=False):
    """Nearest palette index for an (...,3) array of RGB."""
    a = np.asarray(rgb, float)
    flat = a.reshape(-1, 3)
    pal = PALF
    d = (((flat[:, None, :] - pal[None, :, :]) ** 2) * W).sum(-1)
    if exclude_black_ramp:
        d[:, 1:16] = 1e18
    return d.argmin(1).reshape(a.shape[:-1]).astype(np.uint8)


def playpal_lump():
    """14 palettes: normal, 8 pain (red), 4 bonus (gold), 1 radsuit (green)."""
    out = bytearray()
    base = PALF
    for i in range(14):
        if i == 0:
            p = base
        elif i <= 8:
            k = i / 9.0
            p = base + (np.array([255, 0, 40]) - base) * k
        elif i <= 12:
            k = (i - 8) / 8.0
            p = base + (np.array([215, 186, 69]) - base) * k
        else:
            p = base + (np.array([0, 228, 54]) - base) * 0.125
        out += np.clip(np.round(p), 0, 255).astype(np.uint8).tobytes()
    return bytes(out)


def colormap_lump():
    maps = []
    for L in range(32):
        b = max(0.0, 1.0 - L / 31.0) ** 1.1
        tgt = FOG + (PALF - FOG) * b
        if L == 31:
            tgt = FOG.copy()[None, :].repeat(256, 0) * 0.6
        maps.append(nearest(tgt))
    # 32: invulnerability (inverse greyscale, here: white-ish green tint)
    grey = (PALF * np.array([0.3, 0.59, 0.11])).sum(1)
    inv = 255 - grey
    maps.append(nearest(np.stack([inv * 0.85, inv, inv * 0.85], 1)))
    maps.append(np.zeros(256, np.uint8))
    return b"".join(m.tobytes() for m in maps)


def translation(rgb_target):
    """CR* translation: keep luminance, take the hue of rgb_target."""
    grey = (PALF * np.array([0.3, 0.59, 0.11])).sum(1) / 255.0
    t = np.array(rgb_target, float)
    tgt = np.clip(t[None, :] * (grey[:, None] * 1.25), 0, 255)
    return nearest(tgt).tobytes()


# ---------------------------------------------------------------- pictures

def to_indexed(img):
    """RGBA PIL image -> (index array, alpha mask). Exact palette match first."""
    a = np.asarray(img.convert("RGBA"))
    rgb = a[..., :3]
    mask = a[..., 3] >= 128
    ind = nearest(rgb)
    return ind, mask


def spr_to_indexed(spr):
    """pixel_kit Spr (PICO-8 indices, -1 transparent) -> (index array, mask)."""
    a = spr.a
    mask = a >= 0
    ind = np.zeros(a.shape, np.uint8)
    for c in range(16):
        ind[a == c] = idx(c)
    return ind, mask


def picture(ind, mask, xoff=0, yoff=0):
    """Encode a Doom picture (patch) lump."""
    h, w = ind.shape
    cols = []
    for x in range(w):
        col = bytearray()
        y = 0
        while y < h:
            if not mask[y, x]:
                y += 1
                continue
            y0 = y
            while y < h and mask[y, x] and y - y0 < 128:
                y += 1
            run = ind[y0:y, x]
            top = y0
            # tall pictures: use DeePsea-style relative offsets is not supported by
            # all ports; keep columns under 255 by splitting posts.
            if top >= 255:
                raise ValueError("picture too tall")
            col += bytes([top, len(run), run[0]]) + run.tobytes() + bytes([run[-1]])
        col += b"\xff"
        cols.append(bytes(col))
    head = struct.pack("<hhhh", w, h, xoff, yoff)
    off = 8 + 4 * w
    ofs = []
    for c in cols:
        ofs.append(off)
        off += len(c)
    return head + b"".join(struct.pack("<I", o) for o in ofs) + b"".join(cols)


def picture_from_image(img, xoff=0, yoff=0):
    ind, mask = to_indexed(img)
    return picture(ind, mask, xoff, yoff)


def flat_from_image(img):
    img = img.convert("RGB")
    assert img.size == (64, 64), img.size
    return nearest(np.asarray(img)).tobytes()


def raw_screen(img):
    """320x200 raw (used for nothing in Doom, kept for completeness)."""
    return nearest(np.asarray(img.convert("RGB"))).tobytes()


def decode_picture(data, palette=None):
    """Doom picture -> RGBA image (palette: (256,3) array, default ours)."""
    pal = PAL if palette is None else palette
    w, h, xo, yo = struct.unpack_from("<hhhh", data, 0)
    img = np.zeros((h, w, 4), np.uint8)
    for x in range(w):
        (o,) = struct.unpack_from("<I", data, 8 + 4 * x)
        top = -1
        while data[o] != 0xFF:
            t = data[o]
            top = t if t > top else top + t  # tall patch support
            n = data[o + 1]
            px = data[o + 3:o + 3 + n]
            for i, p in enumerate(px):
                if 0 <= top + i < h:
                    img[top + i, x, :3] = pal[p]
                    img[top + i, x, 3] = 255
            o += n + 4
    return Image.fromarray(img, "RGBA"), xo, yo


def index_image(ind, mask=None):
    """Index array -> RGBA preview image."""
    rgb = PAL[ind]
    a = np.full(ind.shape, 255, np.uint8) if mask is None else (mask * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, a]), "RGBA")
