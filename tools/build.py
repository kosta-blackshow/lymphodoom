"""Build lymphodoom.wad (IWAD) and the palette-matched engine resource prboomx.wad.

usage: python3 tools/build.py --freedoom path/to/freedoom1.wad --prboomx path/to/prboomx.wad --out build/
"""
import argparse
import os
import struct
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "art"))

import doomgfx as g  # noqa: E402
from wad import Wad  # noqa: E402
import common  # noqa: E402
import monsters  # noqa: E402
import items  # noqa: E402
import weapons  # noqa: E402
import textures  # noqa: E402
import ui  # noqa: E402
import sfx  # noqa: E402
import music  # noqa: E402
import maps  # noqa: E402
import dehacked  # noqa: E402


def spr_lump(spr, ax, ay, k, sink=0):
    ind, mask = g.spr_to_indexed(spr)
    ind = np.repeat(np.repeat(ind, k, 0), k, 1)
    mask = np.repeat(np.repeat(mask, k, 0), k, 1)
    return g.picture(ind, mask, int(round(ax * k)), int(round(ay * k)) - sink)


def img_lump(img, xoff=0, yoff=0):
    return g.picture_from_image(img, xoff, yoff)


def freedoom_palette(fw):
    return np.frombuffer(fw.get("PLAYPAL")[:768], np.uint8).reshape(256, 3)


def remap_picture(data, src_pal):
    try:
        im, xo, yo = g.decode_picture(data, src_pal)
    except Exception:
        return None
    return g.picture_from_image(im, xo, yo)


def build(args):
    os.makedirs(args.out, exist_ok=True)
    fd = Wad.read(args.freedoom)
    fpal = freedoom_palette(fd)
    lumps = []          # main namespace
    sprites = []
    patches = []
    flats = []

    lumps.append(("LYMPHO", b"LYMPHODOOM 1.0 - an immune system shooter\n"))
    lumps.append(("PLAYPAL", g.playpal_lump()))
    lumps.append(("COLORMAP", g.colormap_lump()))

    # ---------------------------------------------------------- maps
    for name, fn in maps.LEVELS.items():
        m = fn()
        ml, stats = m.build(workdir=args.out)
        print(name, stats)
        lumps.extend((n, d) for n, d in ml)

    # ---------------------------------------------------------- textures
    walls = {n: f() for n, f in textures.WALLS.items()}
    pnames = ["AASHITTY"] + list(walls)
    patches.append(("AASHITTY", img_lump(walls["LNWALL1"].crop((0, 0, 64, 64)).convert("RGBA"))))
    for n, im in walls.items():
        patches.append((n, img_lump(im.convert("RGBA"))))
    tex_defs = [("AASHITTY", 64, 64, 0)] + [(n, im.width, im.height, pnames.index(n)) for n, im in walls.items()]
    body = b""
    offs = []
    base = 4 + 4 * len(tex_defs)
    for n, w, h, pi in tex_defs:
        offs.append(base + len(body))
        body += struct.pack("<8sihhih", n.encode(), 0, w, h, 0, 1) + struct.pack("<hhhhh", 0, 0, pi, 1, 0)
    lumps.append(("TEXTURE1", struct.pack("<i", len(tex_defs)) + b"".join(struct.pack("<i", o) for o in offs) + body))
    lumps.append(("PNAMES", struct.pack("<i", len(pnames)) + b"".join(n.encode().ljust(8, b"\0") for n in pnames)))
    for n, f in textures.FLATS.items():
        flats.append((n, g.flat_from_image(f())))

    # Boom ANIMATED / SWITCHES
    an = b""
    for is_tex, first, last, tics in textures.ANIMATED:
        an += struct.pack("<B9s9si", is_tex, last.encode(), first.encode(), tics)
    an += b"\xff"
    lumps.append(("ANIMATED", an))
    sw = b""
    for off, on in textures.SWITCHES:
        sw += struct.pack("<9s9sh", off.encode(), on.encode(), 1)
    sw += struct.pack("<9s9sh", b"", b"", 0)
    lumps.append(("SWITCHES", sw))

    # ---------------------------------------------------------- sprites
    k = common.SCALE
    for name, fn in monsters.ALL.items():
        for L, fr in fn().items():
            sprites.append((name + L + "0", spr_lump(fr.spr, fr.ax, fr.ay, k, sink=4)))
    for name, frames in items.all_items().items():
        for L, fr in frames.items():
            sprites.append((name + L + "0", spr_lump(fr.spr, fr.ax, fr.ay, k, sink=2)))
    for n, spr, l, t in weapons.all_weapons():
        W = weapons.WSCALE
        ind, mask = g.spr_to_indexed(spr)
        ind = np.repeat(np.repeat(ind, W, 0), W, 1)
        mask = np.repeat(np.repeat(mask, W, 0), W, 1)
        sprites.append((n, g.picture(ind, mask, 1 - l * W, 32 - t * W)))

    # ---------------------------------------------------------- status bar & HUD
    lumps.append(("STBAR", img_lump(ui.stbar())))
    lumps.append(("STARMS", img_lump(ui.starms())))
    for i in range(10):
        lumps.append(("STTNUM%d" % i, img_lump(ui.big_digit(str(i)))))
        lumps.append(("STYSNUM%d" % i, img_lump(ui.small_digit(str(i), 10))))
        lumps.append(("STGNUM%d" % i, img_lump(ui.small_digit(str(i), 6))))
    lumps.append(("STTPRCNT", img_lump(ui.big_digit("%"))))
    lumps.append(("STTMINUS", img_lump(ui.big_digit("-"))))
    for i in range(6):
        lumps.append(("STKEYS%d" % i, img_lump(ui.key_icon(i % 3))))
    for n, s in ui.faces().items():
        ind, mask = g.spr_to_indexed(s)
        lumps.append((n, g.picture(ind, mask, -3, -1)))
    for c in range(33, 96):
        lumps.append(("STCFN%03d" % c, img_lump(ui.hu_char(c))))
    lumps.append(("STCFN121", img_lump(ui.hu_char(ord("Y")))))

    # ---------------------------------------------------------- menus & screens
    for n in ui.MENU_TEXT:
        lumps.append((n, img_lump(ui.menu_item(n))))
    lg = ui.m_doom()
    lumps.append(("M_DOOM", img_lump(lg, 94 - (160 - lg.width // 2), 0)))
    lumps.append(("M_SKULL1", img_lump(ui.cursor(False), 0, 2)))
    lumps.append(("M_SKULL2", img_lump(ui.cursor(True), 0, 2)))
    for p in "LMRO":
        lumps.append(("M_THERM" + p, img_lump(ui.thermo(p))))
    for p in ("M_LSLEFT", "M_LSCNTR", "M_LSRGHT"):
        lumps.append((p, img_lump(ui.save_box(p), 0, 9)))  # drawn at y+7: the box starts 2 px above the text
    lumps.append(("TITLEPIC", img_lump(ui.title_screen())))
    lumps.append(("HELP1", img_lump(ui.help_screen())))
    lumps.append(("HELP2", img_lump(ui.help_screen())))
    lumps.append(("CREDIT", img_lump(ui.credit_screen())))
    lumps.append(("CLEARPIC", img_lump(ui.finale())))
    lumps.append(("VICTORY2", img_lump(ui.finale())))
    lumps.append(("WIMAP0", img_lump(ui.wimap())))
    lumps.append(("WISTATS", img_lump(ui.wi_stats_bg())))
    lumps.append(("M_MENUBG", img_lump(ui.menu_bg())))
    for b, nm in ((False, "WIURH0"), (True, "WIURH1")):
        im, ox, oy = ui.wi_here(b)
        lumps.append((nm, img_lump(im, ox, oy)))
    im, ox, oy = ui.wi_splat()
    lumps.append(("WISPLAT", img_lump(im, ox, oy)))
    names = ["LYMPH NODE", "BLOODSTREAM", "TUMOR"]
    for i in range(9):
        lumps.append(("WILV0%d" % i, img_lump(ui.ps_text(names[min(i, 2)], k=2))))
    wi_text = {"WIF": "CLEARED", "WIENTER": "ENTERING", "WIOSTK": "KILLS", "WIOSTI": "ITEMS",
               "WISCRT2": "SECRET", "WIOSTS": "SCRT", "WITIME": "TIME", "WIPAR": "PAR", "WISUCKS": "SUCKS",
               "WIFRGS": "FRAGS", "WIKILRS": "KILLERS", "WIVCTMS": "VICTIMS", "WIMSTT": "TOTAL"}
    for n, t in wi_text.items():
        lumps.append((n, img_lump(ui.ps_text(t, k=2))))
    for i in range(10):
        lumps.append(("WINUM%d" % i, img_lump(ui.big_digit(str(i)))))
    lumps.append(("WIPCNT", img_lump(ui.big_digit("%"))))
    lumps.append(("WIMINUS", img_lump(ui.big_digit("-"))))
    lumps.append(("WICOLON", img_lump(ui.ps_text(":", k=2))))

    # ---------------------------------------------------------- remapped Freedoom fallbacks (UI only)
    have = {n for n, _ in lumps}
    for n, d in fd.lumps:
        if n in have or not d:
            continue
        if n.startswith(("ST", "WI", "M_", "BRDR")) and not n.startswith(("WIA", "WILV")) and n not in ("STEP1", "STEP2"):
            r = remap_picture(d, fpal)
            if r:
                lumps.append((n, r))
                have.add(n)
    # music synth instruments (Freedoom, BSD licence)
    for n in ("GENMIDI", "DMXGUS"):
        lumps.append((n, fd.get(n)))

    # ---------------------------------------------------------- sound & music
    for n, d in sfx.all_sounds().items():
        lumps.append((n, d))
    for n, d in music.all_music().items():
        lumps.append((n, d))

    lumps.append(("DEHACKED", dehacked.dehacked()))
    lumps.append(("UMAPINFO", dehacked.umapinfo()))

    # ---------------------------------------------------------- write IWAD
    w = Wad(b"IWAD")
    for n, d in lumps:
        w.add(n, d)
    w.add("S_START")
    for n, d in sprites:
        w.add(n, d)
    w.add("S_END")
    w.add("P_START")
    for n, d in patches:
        w.add(n, d)
    w.add("P_END")
    w.add("F_START")
    for n, d in flats:
        w.add(n, d)
    w.add("F_END")
    out = os.path.join(args.out, "lymphodoom.wad")
    w.write(out)
    print("wrote", out, os.path.getsize(out), "bytes,", len(w.lumps), "lumps")

    # ---------------------------------------------------------- engine resource wad
    px = Wad.read(args.prboomx)
    nw = Wad(px.kind)
    drop = {"SWITCHES", "ANIMATED", "CHEXDEH", "NERVEBEX", "BFGBEX", "GLSHADOW", "GLFP", "GLVP"}
    cr = {"CRBRICK": (171, 82, 54), "CRTAN": (255, 204, 170), "CRGRAY": (194, 195, 199), "CRGREEN": (0, 228, 54),
          "CRBROWN": (171, 82, 54), "CRGOLD": (255, 236, 39), "CRRED": (255, 0, 77), "CRBLUE": (41, 173, 255),
          "CRBLUE2": (41, 173, 255), "CRORANGE": (255, 163, 0), "CRYELLOW": (255, 236, 39), "CRBLACK": (60, 60, 70),
          "CRPURPLE": (131, 118, 156), "CRWHITE": (255, 241, 232)}
    inspr = False
    skip_spr = False
    picture_lumps = {"M_AMMO", "M_ARMOUR", "M_ARROW", "M_HEALTH", "M_KEY", "M_NORMAL", "M_SHADOW", "M_POWER",
                     "M_WEAP", "M_MARK", "M_BUTT1", "M_BUTT2", "M_COLORS", "M_PALNO", "M_PALSEL", "M_VBOX",
                     "CROSS1", "CROSS2", "CROSS3", "STKEYS6", "STKEYS7", "STKEYS8", "STCFN096"}
    for n, d in px.lumps:
        if n in drop:
            continue
        if n == "SS_START":
            inspr = True
        if n == "SS_END":
            inspr = False
        if inspr and n not in ("SS_START", "SS_END") and not n.startswith("TNT1"):
            continue  # beta sprites and dogs are unused
        if n in cr:
            d = g.translation(cr[n])
        elif d and (n.startswith(("DIG", "STBR", "BOX")) or n in picture_lumps):
            r = remap_picture(d, fpal)
            d = r if r else d
        nw.add(n, d)
    out2 = os.path.join(args.out, "prboomx.wad")
    nw.write(out2)
    print("wrote", out2, os.path.getsize(out2), "bytes")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--freedoom", required=True)
    ap.add_argument("--prboomx", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "build"))
    build(ap.parse_args())
