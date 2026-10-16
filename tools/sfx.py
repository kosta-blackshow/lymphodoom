"""Procedural sound effects (squishy, chiptune-flavoured), written as DMX lumps."""
import struct

import numpy as np

SR = 11025
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, r=None, curve=2.0):
    x = np.ones(n)
    na = max(1, int(a * SR))
    x[:na] = np.linspace(0, 1, na)
    nr = n - na if r is None else int(r * SR)
    nr = min(nr, n - na)
    if nr > 0:
        x[-nr:] *= np.linspace(1, 0, nr) ** curve
    return x


def sweep(f0, f1, d, wave="square", duty=0.5):
    tt = t(d)
    f = np.geomspace(max(f0, 1), max(f1, 1), len(tt))
    ph = np.cumsum(f) / SR
    if wave == "square":
        return np.where((ph % 1.0) < duty, 1.0, -1.0)
    if wave == "tri":
        return 2 * np.abs(2 * (ph % 1.0) - 1) - 1
    if wave == "saw":
        return 2 * (ph % 1.0) - 1
    return np.sin(2 * np.pi * ph)


def noise(d, color=0.0):
    n = rng.standard_normal(int(SR * d))
    if color > 0:
        # one-pole low-pass: higher color = darker
        a = color
        y = np.zeros_like(n)
        acc = 0.0
        for i, v in enumerate(n):
            acc = a * acc + (1 - a) * v
            y[i] = acc
        n = y / (np.abs(y).max() + 1e-9)
    return n


def lowpass(x, a):
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = a * acc + (1 - a) * v
        y[i] = acc
    return y


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out


def cat(*parts):
    return np.concatenate(parts)


def wobble(x, rate=18, depth=0.4):
    tt = np.arange(len(x)) / SR
    return x * (1 - depth + depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * tt)))


def dmx(x, gain=0.9):
    x = np.asarray(x, float)
    peak = np.abs(x).max() + 1e-9
    x = np.clip(x / peak * gain, -1, 1)
    s = np.round(128 + x * 127).astype(np.uint8)
    pad = bytes([128]) * 16
    body = pad + s.tobytes() + pad
    return struct.pack("<HHI", 3, SR, len(body)) + body


# ---------------------------------------------------------------- the sounds

def pew(f0=1400, f1=420, d=0.13):
    return mix(sweep(f0, f1, d, "square", 0.3) * env(int(SR * d), 0.002) * 0.7,
               noise(0.03) * env(int(SR * 0.03), 0.001) * 0.4)


def burst_pops(n=7, d=0.4):
    out = np.zeros(int(SR * d))
    for i in range(n):
        st = int(rng.uniform(0, 0.12) * SR)
        f = rng.uniform(300, 900)
        p = sweep(f * 1.8, f, 0.06, "sine") * env(int(SR * 0.06), 0.001)
        out[st:st + len(p)] += p
    thump = sweep(160, 50, 0.25, "sine") * env(int(SR * 0.25), 0.002)
    return mix(out, thump * 1.2, noise(0.18, 0.6) * env(int(SR * 0.18), 0.001) * 0.6)


def squish(d=0.25, f0=300, f1=120):
    return mix(wobble(sweep(f0, f1, d, "tri") * env(int(SR * d), 0.01), 30, 0.5), noise(d, 0.85) * env(int(SR * d), 0.01) * 0.4)


def boom(d=0.9, low=1.0):
    n = noise(d, 0.9) * env(int(SR * d), 0.002, curve=1.5)
    th = sweep(120 * low, 30, d, "sine") * env(int(SR * d), 0.002, curve=2)
    bubbles = np.zeros(int(SR * d))
    for i in range(10):
        st = int(rng.uniform(0.05, d * 0.7) * SR)
        f = rng.uniform(200, 600)
        p = sweep(f, f * 1.6, 0.05, "sine") * env(int(SR * 0.05), 0.001)
        bubbles[st:st + len(p)] += p * 0.5
    return mix(n, th * 1.3, bubbles)


def spit():
    return mix(noise(0.15, 0.5) * env(int(SR * 0.15), 0.002), sweep(500, 200, 0.12, "tri") * env(int(SR * 0.12)) * 0.6)


def splat():
    return mix(noise(0.3, 0.7) * env(int(SR * 0.3), 0.001), sweep(250, 60, 0.2, "sine") * env(int(SR * 0.2)) * 0.8)


def zap():
    return mix(sweep(1800, 900, 0.16, "saw") * env(int(SR * 0.16), 0.002), sweep(2400, 1200, 0.16, "square", 0.25) * env(int(SR * 0.16)) * 0.3)


def charge():
    a = sweep(200, 1600, 0.8, "saw") * env(int(SR * 0.8), 0.3, r=0.1)
    b = sweep(300, 2400, 0.8, "square", 0.3) * env(int(SR * 0.8), 0.3, r=0.1) * 0.4
    return cat(mix(a, b), boom(0.5) * 0.8)


def hum(d=0.5, f=70):
    return wobble(sweep(f, f, d, "saw"), 8, 0.3) * env(int(SR * d), 0.03, r=0.08) * 0.8


def slide(d=0.45, up=True):
    n = noise(d, 0.75)
    f = sweep(200 if up else 500, 500 if up else 200, d, "tri") * 0.4
    return (n + f) * env(int(SR * d), 0.03, r=0.12)


def click(f=900):
    return sweep(f, f * 0.7, 0.05, "square") * env(int(SR * 0.05), 0.001)


def blip_up(notes=(660, 990), d=0.06):
    return cat(*[sweep(f, f, d, "square", 0.25) * env(int(SR * d), 0.002) for f in notes])


def oof(f=180):
    return mix(sweep(f, f * 0.6, 0.18, "square", 0.4) * env(int(SR * 0.18), 0.005), noise(0.1, 0.8) * env(int(SR * 0.1)) * 0.3)


def wail(f0=600, f1=90, d=0.9):
    return wobble(sweep(f0, f1, d, "square", 0.4), 9, 0.4) * env(int(SR * d), 0.01)


def warble(f=900, d=0.35, rate=22):
    tt = t(d)
    fm = f * (1 + 0.15 * np.sin(2 * np.pi * rate * tt))
    ph = np.cumsum(fm) / SR
    return np.where(ph % 1 < 0.4, 1.0, -1.0) * env(len(tt), 0.01)


def growl(f=110, d=0.6):
    tt = t(d)
    fm = f * (1 + 0.2 * np.sin(2 * np.pi * 7 * tt))
    ph = np.cumsum(fm) / SR
    nz = noise(d, 0.6)[:len(tt)]
    x = (2 * (ph % 1) - 1)[:len(nz)] + nz * 0.5
    return x * env(len(x), 0.04)


def gurgle(d=0.6):
    out = np.zeros(int(SR * d))
    for i in range(16):
        st = int(rng.uniform(0, d - 0.06) * SR)
        f = rng.uniform(120, 400)
        p = sweep(f, f * 2, 0.05, "sine") * env(int(SR * 0.05), 0.001)
        out[st:st + len(p)] += p
    return mix(out, growl(80, d) * 0.3)


def roar(d=1.0):
    return mix(growl(60, d), growl(90, d) * 0.6, noise(d, 0.92) * env(int(SR * d), 0.05) * 0.5)


def chomp():
    return cat(squish(0.08, 400, 200), np.zeros(int(SR * 0.03)), squish(0.1, 300, 120))


def buzz(d=0.4):
    return wobble(sweep(220, 260, d, "saw"), 40, 0.6) * env(int(SR * d), 0.01)


def pop(f=500):
    return mix(sweep(f * 2, f / 2, 0.15, "sine") * env(int(SR * 0.15), 0.001), noise(0.08, 0.4) * env(int(SR * 0.08)) * 0.5)


def shimmer(d=0.7):
    out = np.zeros(int(SR * d))
    for i, f in enumerate((523, 659, 784, 1047, 1319, 1568)):
        st = int(i * 0.07 * SR)
        p = sweep(f, f, 0.25, "tri") * env(int(SR * 0.25), 0.005)
        out[st:st + len(p)] += p
    return out


SOUNDS = {
    "DSPISTOL": lambda: pew(),
    "DSSHOTGN": lambda: burst_pops(),
    "DSSGCOCK": lambda: cat(squish(0.08, 500, 300), np.zeros(int(SR * 0.05)), squish(0.08, 300, 500)),
    "DSSAWUP": lambda: hum(0.6, 90), "DSSAWIDL": lambda: hum(0.3, 90), "DSSAWFUL": lambda: hum(0.3, 140),
    "DSSAWHIT": lambda: squish(0.3),
    "DSRLAUNC": lambda: mix(slide(0.4, True) * 0.7, sweep(200, 900, 0.3, "saw") * env(int(SR * 0.3)) * 0.5),
    "DSRXPLOD": lambda: boom(1.0),
    "DSFIRSHT": spit,
    "DSFIRXPL": splat,
    "DSPSTART": lambda: hum(0.4, 60), "DSPSTOP": lambda: click(300), "DSSTNMOV": lambda: hum(0.2, 55),
    "DSDOROPN": lambda: slide(0.5, True), "DSDORCLS": lambda: slide(0.5, False),
    "DSBDOPN": lambda: slide(0.3, True), "DSBDCLS": lambda: slide(0.3, False),
    "DSSWTCHN": lambda: blip_up((700, 1050), 0.05), "DSSWTCHX": lambda: blip_up((1050, 700), 0.05),
    "DSPLPAIN": lambda: oof(220), "DSOUCH": lambda: oof(260),
    "DSDMPAIN": lambda: squish(0.25, 350, 150), "DSPOPAIN": lambda: warble(1200, 0.2, 30),
    "DSSLOP": lambda: boom(0.6, 1.5),
    "DSITEMUP": lambda: blip_up((880, 1320), 0.05),
    "DSWPNUP": lambda: blip_up((523, 784, 1047), 0.06),
    "DSOOF": lambda: oof(120),
    "DSTELEPT": shimmer,
    "DSPOSIT1": lambda: warble(900), "DSPOSIT2": lambda: warble(1100, 0.3, 28), "DSPOSIT3": lambda: warble(750, 0.4, 18),
    "DSBGSIT1": lambda: growl(130, 0.5), "DSBGSIT2": lambda: growl(100, 0.6),
    "DSSGTSIT": lambda: gurgle(0.6), "DSBRSSIT": lambda: roar(1.1),
    "DSSGTATK": chomp, "DSCLAW": lambda: mix(noise(0.15, 0.3) * env(int(SR * 0.15), 0.001), squish(0.12, 600, 300) * 0.5),
    "DSPLDETH": lambda: wail(500, 80, 1.0), "DSPDIEHI": lambda: wail(800, 100, 1.0),
    "DSPODTH1": lambda: pop(500), "DSPODTH2": lambda: pop(650), "DSPODTH3": lambda: pop(400),
    "DSBGDTH1": lambda: boom(0.5, 1.3), "DSBGDTH2": lambda: boom(0.6, 1.1),
    "DSSGTDTH": lambda: mix(gurgle(0.5), boom(0.5) * 0.6), "DSBRSDTH": lambda: mix(roar(0.8), boom(1.2) * 0.9),
    "DSPOSACT": lambda: warble(700, 0.25, 12), "DSBGACT": lambda: growl(90, 0.4), "DSDMACT": lambda: gurgle(0.4),
    "DSNOWAY": lambda: buzz(0.25),
    "DSBAREXP": lambda: boom(0.9, 1.2),
    "DSPUNCH": lambda: mix(squish(0.12, 200, 80), noise(0.05) * env(int(SR * 0.05), 0.001) * 0.6),
    "DSTINK": lambda: click(2000), "DSMETAL": lambda: click(600), "DSHOOF": lambda: oof(90),
    "DSITMBK": shimmer, "DSGETPOW": lambda: blip_up((523, 659, 784, 1047, 1319), 0.07),
    "DSPLASMA": zap, "DSBFG": charge,
    "DSCACSIT": lambda: gurgle(0.8), "DSCACDTH": lambda: mix(gurgle(0.6), boom(0.8) * 0.7),
    "DSSKLATK": lambda: buzz(0.5), "DSSKLDTH": lambda: pop(300),
    "DSCYBSIT": lambda: roar(1.2), "DSSPISIT": lambda: roar(1.2), "DSCYBDTH": lambda: boom(1.4), "DSSPIDTH": lambda: boom(1.4),
    "DSJUMP": lambda: blip_up((400, 600), 0.04),
}


def all_sounds():
    return {name: dmx(fn()) for name, fn in SOUNDS.items()}
