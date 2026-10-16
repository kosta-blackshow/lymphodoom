"""The three LYMPHODOOM levels: E1M1 Lymph Node, E1M2 Bloodstream, E1M3 Tumor."""
import math
import os

from mapgen import Map, blob_room, blob_pts, tube, make_door, ip, EASY, MED, HARD, ALL, ML_SECRET

# Doom thing numbers
PLAYER = 1
VIRUS, BACTERIUM, TUMOR, PARASITE, GHOST, PHAGE, SPORE, MASS = 3004, 9, 3001, 3002, 58, 3006, 3005, 3003
STIM, MEDI, HBON, ABON, ARM1, ARM2, SOUL, SUIT, MAP = 2011, 2012, 2014, 2015, 2018, 2019, 2013, 2025, 2026
KEY_W, KEY_Y, KEY_O = 5, 6, 13
CLIP, AMMO, SHEL, SBOX, ROCK, BROK, CELL, CELP, BPAK = 2007, 2048, 2008, 2049, 2010, 2046, 2047, 17, 8
SHOTGUN, CHAINGUN, LAUNCHER, PLASMA, BFG = 2001, 2002, 2003, 2004, 2006
STEMLAMP, RBC, BODYCELL, COLLAGEN, GRANULO, SENESC, TOXIN, DEBRIS = 2028, 34, 35, 48, 85, 86, 2035, 24

MED_UP = MED | HARD


class Theme:
    def __init__(self, wall, tube_wall, floor, ceil, tube_floor=None, tube_ceil=None, light=176, tube_light=136):
        self.wall, self.tube_wall = wall, tube_wall
        self.floor, self.ceil = floor, ceil
        self.tube_floor = tube_floor or floor
        self.tube_ceil = tube_ceil or ceil
        self.light, self.tube_light = light, tube_light


class Level:
    """Declare rooms and links, then finish(): port angles are derived from where each
    link goes, so tubes leave rooms facing their destination."""

    def __init__(self, name, theme):
        self.m = Map(name)
        self.th = theme
        self.rooms = {}
        self.specs = {}
        self.links = []

    def room(self, key, cx, cy, r, floor=0, height=192, light=None, seed=0, ry=None, wobble=0.1,
             ftex=None, ctex=None, special=0, wall=None, n=30, extra=()):
        self.specs[key] = dict(cx=cx, cy=cy, r=r, floor=floor, height=height, light=light, seed=seed, ry=ry,
                               wobble=wobble, ftex=ftex, ctex=ctex, special=special, wall=wall, n=n,
                               extra=list(extra), ports=[])

    def link(self, a, b, mids=(), width=128, **kw):
        self.links.append(dict(a=a, b=b, mids=list(mids), width=width, kw=kw))

    def finish(self):
        th = self.th
        # 1. port angles
        for li, l in enumerate(self.links):
            for end, other, first in (("a", "b", True), ("b", "a", False)):
                sp = self.specs[l[end]]
                tgt = (l["mids"][0] if first else l["mids"][-1]) if l["mids"] else (self.specs[l[other]]["cx"], self.specs[l[other]]["cy"])
                ang = math.degrees(math.atan2(tgt[1] - sp["cy"], tgt[0] - sp["cx"]))
                sp["ports"].append([ang, l["width"], li, end])
        for key, sp in self.specs.items():
            allp = sp["ports"] + [[a, 64, None, "x%d" % i] for i, a in enumerate(sp["extra"])]
            # spread ports that are too close
            for _ in range(50):
                allp.sort(key=lambda p: p[0] % 360)
                moved = False
                for i in range(len(allp)):
                    p, q = allp[i], allp[(i + 1) % len(allp)]
                    if p is q:
                        continue
                    need = math.degrees((p[1] + q[1]) / 2 / sp["r"]) + 22
                    gap = (q[0] - p[0]) % 360
                    if gap < need:
                        p[0] -= (need - gap) / 2 + 1
                        q[0] += (need - gap) / 2 + 1
                        moved = True
                if not moved:
                    break
            sp["all"] = allp
        # 2. rooms
        for key, sp in self.specs.items():
            sec = self.m.sector(sp["floor"], sp["floor"] + sp["height"], sp["ftex"] or th.floor, sp["ctex"] or th.ceil,
                                sp["light"] or th.light, special=sp["special"], wall=sp["wall"] or th.wall,
                                upper=th.tube_wall, lower=th.tube_wall)
            ps = blob_room(self.m, sec, sp["cx"], sp["cy"], sp["r"], ports=[(p[0], p[1]) for p in sp["all"]],
                           seed=sp["seed"], ry=sp["ry"], wobble=sp["wobble"], n=sp["n"])
            pmap = {}
            for p, port in zip(sp["all"], ps):
                pmap[(p[2], p[3])] = port
            self.rooms[key] = {"sector": sec, "ports": pmap, "c": (sp["cx"], sp["cy"]), "r": sp["r"]}
        # 3. tubes
        for li, l in enumerate(self.links):
            self._connect(l["a"], (li, "a"), l["b"], (li, "b"), mids=l["mids"], width=l["width"], **l["kw"])

    def _connect(self, a, ia, b, ib, mids=(), width=128, height=128, door=None, key_special=None, door_at=None,
                 light=None, ftex=None, ctex=None, wall=None, seed=0, special=0, secret=False):
        th = self.th
        A, B = self.rooms[a], self.rooms[b]
        fa, fb = A["sector"].floor, B["sector"].floor

        def sf(t, kind, info):
            s = max(0.0, min(1.0, (t - 0.2) / 0.6))
            f = int(round((fa + (fb - fa) * s) / 8.0)) * 8
            if kind == "door":
                return self.m.sector(f, f, ftex or th.tube_floor, "DOORTOP", light or th.tube_light,
                                     wall=wall or th.tube_wall)
            return self.m.sector(f, f + height, ftex or th.tube_floor, ctex or th.tube_ceil, light or th.tube_light,
                                 special=special, wall=wall or th.tube_wall)

        doors = []
        if door:
            doors.append((door_at if door_at is not None else 72, {"special": key_special or 1, "tex": door}))
        segs = tube(self.m, A["ports"][ia], B["ports"][ib], mids=mids, width=width, sector_fn=sf, seed=seed, doors=doors)
        for i, s in enumerate(segs):
            if s["kind"] == "door":
                before = segs[i - 1]["sector"] if i > 0 else A["sector"]
                after = segs[i + 1]["sector"] if i + 1 < len(segs) else B["sector"]
                make_door(self.m, s, (before, after), special=s["info"]["special"], tex=s["info"]["tex"])
                if secret:
                    for e in (("L0", "R0"), ("L1", "R1")):
                        self.m.line(s[e[0]], s[e[1]], flags=ML_SECRET)
        return segs

    def wall_feature(self, room, ip_, **props):
        """Use an extra (unconnected) port of a room as a special wall (switch, sign...)."""
        p = self.rooms[room]["ports"][(None, "x%d" % ip_)]
        self.m.line(p["a"], p["b"], **props)

    def pillars(self, room, n, r=40, dist=0.5, seed=0, phase=0.0):
        R = self.rooms[room]
        cx, cy = R["c"]
        for i in range(n):
            a = phase + 2 * math.pi * i / n
            x, y = cx + math.cos(a) * R["r"] * dist, cy + math.sin(a) * R["r"] * dist
            self.m.hole(R["sector"], blob_pts(x, y, r, n=10, seed=seed + i, wobble=0.2))

    def island(self, room, cx, cy, r, dfloor=0, dceil=0, light=None, ftex=None, ctex=None, special=0, seed=0, n=12, tag=0):
        R = self.rooms[room]
        base = R["sector"]
        pts = blob_pts(cx, cy, r, n=n, seed=seed, wobble=0.12)
        self.m.hole(base, pts)
        sec = self.m.sector(base.floor + dfloor, base.ceil + dceil, ftex or base.ftex, ctex or base.ctex,
                            light or base.light, special=special, tag=tag, wall=base.wall, upper=base.upper,
                            lower=self.th.tube_wall)
        self.m.poly(sec, pts)
        return sec

    def put(self, room, type_, n, flags=ALL, sec=None, keepout=None):
        if keepout is None and getattr(self, "player", None):
            keepout = (self.player[0], self.player[1], 150)
        self.m.scatter(sec or self.rooms[room]["sector"], type_, n, flags, keepout=keepout)

    def spawn(self, room, type_, easy, med, hard):
        """Monsters: easy count on all skills, extra on FEVER, extra on METASTASIS."""
        ko = getattr(self, "player", None)
        ko = (ko[0], ko[1], 280) if ko else None
        if easy:
            self.put(room, type_, easy, ALL, keepout=ko)
        if med > easy:
            self.put(room, type_, med - easy, MED_UP, keepout=ko)
        if hard > med:
            self.put(room, type_, hard - med, HARD, keepout=ko)

    def at(self, room, type_, dx=0, dy=0, angle=0, flags=ALL):
        cx, cy = self.rooms[room]["c"]
        self.m.thing(cx + dx, cy + dy, type_, angle, flags)
        if type_ == PLAYER:
            self.player = (cx + dx, cy + dy)


# ---------------------------------------------------------------- E1M1 LYMPH NODE

def e1m1():
    L = Level("E1M1", Theme("LNWALL1", "LNWALL2", "LNFLOOR", "LNCEIL", light=176, tube_light=140))
    W = 128
    L.room("cortex", 0, 0, 300, seed=1)
    L.room("follicle", 1150, 0, 340, seed=2, floor=16)
    L.room("germinal", 1150, 1250, 420, seed=3, floor=32, height=256, light=192)
    L.room("paracortex", -100, 1250, 340, seed=4)
    L.room("cords", -1150, 650, 300, seed=5, floor=-24, light=150)
    L.room("sinus", 2350, 1250, 330, seed=6, floor=48)
    L.room("efferent", 2350, 100, 260, seed=7, floor=48, light=200, ftex="EXITPAD", extra=[-90])
    L.room("secret", 1700, -650, 150, seed=8, floor=16, light=208, special=9)
    L.room("plasma_cell", 1900, 2050, 170, seed=9, floor=32, light=160)

    L.link("cortex", "follicle", mids=[(580, -80)], door="DOORM1", seed=11)
    L.link("follicle", "germinal", mids=[(1220, 620)], seed=12)
    L.link("germinal", "paracortex", mids=[(520, 1330)], seed=13)
    L.link("paracortex", "cortex", mids=[(-60, 640)], door="DOORM1", door_at=200, seed=14)
    L.link("paracortex", "cords", mids=[(-700, 1080)], seed=15)
    L.link("cords", "cortex", mids=[(-640, 180)], width=80, height=96, seed=16)
    L.link("germinal", "sinus", mids=[(1830, 1300)], door="DOORMY", key_special=27, seed=17)
    L.link("sinus", "efferent", mids=[(2420, 680)], seed=18)
    L.link("follicle", "secret", width=96, door="LNWALL2", key_special=31, secret=True, seed=19)
    L.link("germinal", "plasma_cell", width=96, seed=20)
    L.finish()

    L.wall_feature("efferent", 0, mid="SW1EXIT", special=11)
    L.pillars("germinal", 5, r=44, dist=0.55, seed=30)
    L.island("germinal", 1150, 1250, 90, dfloor=24, dceil=-24, light=224, ctex="LIGHTF", seed=31)
    L.island("cortex", 0, 0, 70, dceil=-16, light=208, ctex="LIGHTF", seed=32)
    L.pillars("follicle", 3, r=36, dist=0.5, seed=33, phase=0.5)
    L.island("paracortex", -100, 1250, 80, dceil=-16, light=200, ctex="LIGHTF", seed=34)

    L.at("cortex", PLAYER, -120, -40, angle=0)
    if os.environ.get("LYMPHO_TEST_CIV"):  # test build only: civilians right in front of the start
        for k, t in enumerate((BODYCELL, STEMLAMP, GRANULO, SENESC)):
            L.at("cortex", t, 40, -100 + k * 40)
    L.spawn("cortex", VIRUS, 0, 1, 2)
    L.spawn("follicle", VIRUS, 3, 5, 6)
    L.spawn("follicle", BACTERIUM, 1, 2, 3)
    L.spawn("germinal", VIRUS, 3, 4, 6)
    L.spawn("germinal", BACTERIUM, 2, 3, 5)
    L.spawn("germinal", TUMOR, 1, 2, 3)
    L.spawn("paracortex", TUMOR, 2, 3, 4)
    L.spawn("paracortex", VIRUS, 2, 3, 3)
    L.spawn("cords", BACTERIUM, 2, 3, 4)
    L.spawn("cords", TUMOR, 0, 1, 2)
    L.spawn("sinus", TUMOR, 2, 3, 5)
    L.spawn("sinus", BACTERIUM, 1, 2, 3)
    L.spawn("efferent", PARASITE, 1, 2, 2)
    L.spawn("plasma_cell", VIRUS, 0, 2, 3)

    L.put("cortex", CLIP, 2)
    L.put("cortex", HBON, 4)
    L.at("germinal", SHOTGUN, 0, 0)
    L.put("follicle", SHEL, 2)
    L.put("follicle", STIM, 1)
    L.put("germinal", SHEL, 3)
    L.put("germinal", STIM, 2)
    L.put("germinal", ABON, 5)
    L.put("paracortex", CLIP, 2)
    L.put("paracortex", MEDI, 1)
    L.at("cords", KEY_Y, 0, 0)
    L.put("cords", SHEL, 2)
    L.put("cords", STIM, 1)
    L.put("sinus", SBOX, 1)
    L.put("sinus", MEDI, 1)
    L.at("secret", ARM1, 0, 0)
    L.put("secret", SBOX, 1)
    L.at("plasma_cell", CHAINGUN, 0, 0)
    L.put("plasma_cell", AMMO, 1)
    L.put("efferent", STIM, 1)
    # own cells (civilians): 8 per level
    L.put("follicle", GRANULO, 2)
    L.put("germinal", BODYCELL, 3)
    L.put("paracortex", STEMLAMP, 2)
    L.put("sinus", SENESC, 1)
    L.put("cords", TOXIN, 2)
    L.put("sinus", TOXIN, 3)
    return L.m


# ---------------------------------------------------------------- E1M2 BLOODSTREAM

def e1m2():
    L = Level("E1M2", Theme("BVWALL1", "BVWALL2", "BVFLOR1", "BVCEIL", light=168, tube_light=136))
    W = 160
    L.room("start", 0, 0, 280, seed=41, ftex="LNFLOOR", ctex="LNCEIL", wall="LNWALL2")
    L.room("valve", 1700, 350, 330, seed=42, floor=24)
    L.room("side", 2700, -250, 170, seed=47, floor=24, light=184)
    L.room("capillary", 1800, 1700, 400, seed=43, floor=-16, light=150, height=224)
    L.room("atrium", 300, 2100, 470, seed=44, height=288, light=184)
    L.room("closet", -150, 950, 150, seed=48, light=120, special=9)
    L.room("aorta", -1150, 1400, 300, seed=45, floor=40)
    L.room("exit", -1150, 100, 240, seed=46, floor=40, light=200, ftex="EXITPAD", extra=[-90])

    flow = dict(width=W, height=160, ftex="BVFLOR1")
    L.link("start", "valve", mids=[(560, -200), (1100, 120)], door="DOORM1", door_at=120, seed=51, **flow)
    L.link("valve", "capillary", mids=[(1950, 1000)], seed=52, **flow)
    L.link("capillary", "atrium", mids=[(1150, 2050)], seed=53, **flow)
    L.link("atrium", "aorta", mids=[(-500, 2000)], door="DOORMW", key_special=26, seed=54, **flow)
    L.link("aorta", "exit", mids=[(-1220, 760)], seed=55, **flow)
    L.link("valve", "side", width=96, height=128, seed=56)
    L.link("start", "closet", width=64, height=96, door="BVWALL1", key_special=31, secret=True, seed=57)
    L.link("closet", "atrium", mids=[(-60, 1350)], width=96, height=128, seed=58)
    L.finish()

    L.wall_feature("exit", 0, mid="SW1EXIT", special=11)
    L.pillars("capillary", 7, r=34, dist=0.55, seed=60)
    L.pillars("capillary", 3, r=28, dist=0.2, seed=61, phase=0.4)
    L.island("atrium", 300, 2100, 120, dfloor=24, dceil=-32, light=224, ctex="LIGHTF", seed=62)
    L.pillars("atrium", 4, r=50, dist=0.62, seed=63, phase=0.78)
    L.island("valve", 1700, 350, 80, dfloor=16, light=200, seed=64)

    L.at("start", PLAYER, -120, 0, angle=0)
    L.spawn("start", VIRUS, 0, 1, 1)
    L.spawn("valve", BACTERIUM, 2, 3, 5)
    L.spawn("valve", PHAGE, 1, 2, 3)
    L.spawn("valve", VIRUS, 2, 3, 4)
    L.spawn("capillary", VIRUS, 4, 6, 8)
    L.spawn("capillary", PHAGE, 2, 3, 4)
    L.spawn("capillary", TUMOR, 1, 2, 3)
    L.spawn("atrium", SPORE, 1, 2, 3)
    L.spawn("atrium", TUMOR, 2, 3, 4)
    L.spawn("atrium", BACTERIUM, 2, 3, 4)
    L.spawn("aorta", PARASITE, 1, 2, 3)
    L.spawn("aorta", TUMOR, 1, 2, 3)
    L.spawn("exit", SPORE, 0, 1, 1)
    L.spawn("side", PHAGE, 1, 2, 2)

    L.put("start", SHEL, 2)
    L.put("start", CLIP, 2)
    L.at("valve", CHAINGUN, 0, 0)
    L.put("valve", AMMO, 1)
    L.put("valve", STIM, 2)
    L.put("side", MEDI, 1)
    L.put("side", ARM1, 1)
    L.put("capillary", SBOX, 1)
    L.put("capillary", HBON, 6)
    L.put("capillary", STIM, 2)
    L.at("atrium", KEY_W, 0, 0)
    L.at("atrium", LAUNCHER, 260, 0)
    L.put("atrium", ROCK, 3)
    L.put("atrium", MEDI, 1)
    L.put("atrium", AMMO, 1)
    L.put("aorta", BROK, 1)
    L.put("aorta", SHEL, 2)
    L.put("closet", SOUL, 1)
    L.put("closet", ROCK, 2)
    L.at("exit", MAP, 0, 60)
    for r in ("valve", "capillary", "atrium", "aorta"):
        L.put(r, RBC, 6)
    L.put("valve", BODYCELL, 2)
    L.put("capillary", STEMLAMP, 3)
    L.put("atrium", GRANULO, 2)
    L.put("aorta", SENESC, 1)
    L.put("atrium", TOXIN, 3)
    L.put("valve", TOXIN, 2)
    return L.m


# ---------------------------------------------------------------- E1M3 TUMOR

def e1m3():
    L = Level("E1M3", Theme("TMWALL1", "TMWALL2", "TMFLOOR", "TMCEIL", light=160, tube_light=128))
    W = 144
    L.room("front", 0, 0, 290, seed=71, light=176, ftex="LNFLOOR", wall="TMWALL2")
    L.room("stroma", 1250, 0, 340, seed=72, floor=16, light=150)
    L.room("cache", 2000, -700, 160, seed=77, floor=16, light=176)
    L.room("hypoxic", 1300, 1350, 380, seed=73, light=112, wall="TMWALL3")
    L.room("angio", -100, 1350, 330, seed=74, floor=-16, light=140)
    L.room("vault", -1000, 2000, 150, seed=76, floor=-16, light=200, special=9)
    L.room("core", 650, 2900, 600, seed=75, height=320, light=150, ry=520, n=40)

    L.link("front", "stroma", mids=[(620, 60)], door="DOORM1", seed=81, width=W)
    L.link("stroma", "hypoxic", mids=[(1350, 680)], seed=82, width=W)
    L.link("hypoxic", "angio", mids=[(600, 1420)], door="DOORM1", door_at=180, seed=83, width=W)
    L.link("angio", "front", mids=[(-80, 680)], seed=84, width=W)
    L.link("angio", "vault", mids=[(-600, 1750)], width=96, door="TMWALL1", key_special=31, secret=True, seed=85)
    L.link("angio", "core", mids=[(250, 2000)], door="DOORMO", key_special=28, seed=86, height=144, width=W)
    L.link("stroma", "cache", width=96, seed=87)
    L.finish()

    for i, (dx, dy) in enumerate([(-150, -80), (130, 120), (40, -200)]):
        L.island("hypoxic", 1300 + dx, 1350 + dy, 85, dfloor=-8, light=96, ftex="NECRO1", special=5, seed=90 + i)
    L.pillars("stroma", 4, r=40, dist=0.55, seed=93)
    L.pillars("core", 6, r=60, dist=0.62, seed=94)
    L.island("core", 650, 2900, 140, dfloor=24, dceil=-48, light=200, ctex="LIGHTF", seed=95)
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.5
        L.island("core", 650 + math.cos(a) * 330, 2900 + math.sin(a) * 290, 70, dfloor=-8, light=104,
                 ftex="NECRO1", special=7, seed=96 + i)

    L.at("front", PLAYER, -130, 0, angle=0)
    if not os.environ.get("LYMPHO_TEST_BOSS"):
        L.spawn("front", TUMOR, 0, 0, 1)
        L.spawn("front", VIRUS, 1, 1, 2)
    L.spawn("stroma", PARASITE, 2, 3, 4)
    L.spawn("stroma", TUMOR, 2, 3, 4)
    L.spawn("stroma", BACTERIUM, 1, 2, 3)
    L.spawn("hypoxic", GHOST, 2, 3, 4)
    L.spawn("hypoxic", TUMOR, 2, 3, 4)
    L.spawn("hypoxic", SPORE, 0, 1, 2)
    L.spawn("angio", SPORE, 1, 2, 3)
    L.spawn("angio", PHAGE, 2, 3, 5)
    L.spawn("angio", PARASITE, 1, 2, 2)
    L.spawn("cache", PHAGE, 1, 2, 3)
    if os.environ.get("LYMPHO_TEST_BOSS"):
        L.at("front", MASS, 120, 0, angle=180)  # test build only: boss next to the start
    else:
        L.at("core", MASS, 0, 220, angle=270)
        L.at("core", MASS, -180, 260, angle=270, flags=HARD)
    L.spawn("core", TUMOR, 2, 4, 6)
    L.spawn("core", GHOST, 1, 2, 3)
    L.spawn("core", SPORE, 0, 1, 2)

    L.put("front", SHEL, 3)
    L.put("front", CLIP, 2)
    L.put("front", STIM, 1)
    L.put("stroma", SBOX, 1)
    L.put("stroma", MEDI, 1)
    L.put("stroma", ROCK, 2)
    L.put("cache", BROK, 1)
    L.put("cache", ARM2, 1)
    L.at("hypoxic", SUIT, 0, 0)
    L.at("hypoxic", KEY_O, 230, -60)
    L.put("hypoxic", AMMO, 1)
    L.put("hypoxic", STIM, 2)
    L.at("angio", PLASMA, 0, 0)
    L.put("angio", CELL, 3)
    L.put("angio", MEDI, 1)
    L.put("angio", SHEL, 2)
    L.at("vault", BFG, 0, 0)
    L.put("vault", CELP, 1)
    L.put("vault", SOUL, 1)
    L.put("core", CELL, 2)
    L.put("core", MEDI, 2)
    L.put("core", BROK, 1)
    L.put("core", SBOX, 1)
    L.put("stroma", BODYCELL, 2)
    L.put("hypoxic", SENESC, 2)
    L.put("angio", GRANULO, 2)
    L.put("core", STEMLAMP, 2)
    L.put("stroma", COLLAGEN, 4)
    L.put("hypoxic", DEBRIS, 4)
    L.put("core", COLLAGEN, 4)
    L.put("core", TOXIN, 3)
    L.put("angio", RBC, 5)
    return L.m


LEVELS = {"E1M1": e1m1, "E1M2": e1m2, "E1M3": e1m3}
