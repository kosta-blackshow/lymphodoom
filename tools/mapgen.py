"""A small polygon-based Doom map builder.

Sectors are polygons (with optional holes). Shared edges between two sectors become
two-sided lines automatically, T-junctions are split, everything else is a one-sided
wall. Nodes, blockmap and reject are built by zdbsp.
"""
import math
import os
import random
import struct
import subprocess
import tempfile

from shapely.geometry import Polygon, Point

from wad import Wad

ML_BLOCKING, ML_TWOSIDED, ML_DONTPEGTOP, ML_DONTPEGBOTTOM, ML_SECRET = 1, 4, 8, 16, 32
EASY, MED, HARD = 1, 2, 4
ALL = EASY | MED | HARD


def ip(p):
    return (int(round(p[0])), int(round(p[1])))


def area(pts):
    a = 0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return a / 2


def dedupe(pts):
    out = []
    for p in pts:
        if not out or out[-1] != p:
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


class Sector:
    def __init__(self, idx, floor, ceil, ftex, ctex, light, special=0, tag=0, wall="LNWALL1",
                 upper=None, lower=None):
        self.idx = idx
        self.floor, self.ceil = int(floor), int(ceil)
        self.ftex, self.ctex = ftex, ctex
        self.light, self.special, self.tag = light, special, tag
        self.wall = wall
        self.upper = upper or wall
        self.lower = lower or wall


class Map:
    def __init__(self, name):
        self.name = name
        self.sectors = []
        self.loops = []   # (sector, pts, hole)
        self.things = []
        self.props = {}   # undirected (a,b) -> dict
        self.polys = {}   # sector idx -> shapely polygon (outer, minus holes)
        self.rnd = random.Random(hash(name) & 0xFFFF)

    # ------------------------------------------------------------ geometry
    def sector(self, floor, ceil, ftex, ctex, light, **kw):
        s = Sector(len(self.sectors), floor, ceil, ftex, ctex, light, **kw)
        self.sectors.append(s)
        return s

    def poly(self, sec, pts):
        pts = dedupe([ip(p) for p in pts])
        self.loops.append((sec, pts, False))
        P = Polygon(pts)
        if not P.is_valid:
            raise ValueError("invalid polygon for sector %d: %s" % (sec.idx, pts[:6]))
        self.polys[sec.idx] = P if sec.idx not in self.polys else self.polys[sec.idx].union(P)
        return pts

    def hole(self, sec, pts):
        pts = dedupe([ip(p) for p in pts])
        self.loops.append((sec, pts, True))
        if sec.idx in self.polys:
            self.polys[sec.idx] = self.polys[sec.idx].difference(Polygon(pts))
        return pts

    def line(self, a, b, **props):
        k = (min(a, b), max(a, b))
        self.props.setdefault(k, {}).update(props)

    def thing(self, x, y, type_, angle=0, flags=ALL):
        self.things.append((int(x), int(y), int(angle), int(type_), int(flags)))

    # ------------------------------------------------------------ helpers
    def random_point(self, sec, margin=40, tries=400, avoid=(), keepout=None):
        P = self.polys[sec.idx].buffer(-margin)
        if P.is_empty:
            P = self.polys[sec.idx]
        minx, miny, maxx, maxy = P.bounds
        for _ in range(tries):
            x, y = self.rnd.uniform(minx, maxx), self.rnd.uniform(miny, maxy)
            if keepout and math.hypot(x - keepout[0], y - keepout[1]) < keepout[2]:
                continue
            if P.contains(Point(x, y)) and all(math.hypot(x - ax, y - ay) > 88 for ax, ay in avoid):
                return int(x), int(y)
        if keepout:
            best = None
            for _ in range(tries):
                x, y = self.rnd.uniform(minx, maxx), self.rnd.uniform(miny, maxy)
                if P.contains(Point(x, y)):
                    d = math.hypot(x - keepout[0], y - keepout[1])
                    if best is None or d > best[0]:
                        best = (d, x, y)
            if best:
                return int(best[1]), int(best[2])
        c = P.representative_point()
        return int(c.x), int(c.y)

    def scatter(self, sec, type_, n, flags=ALL, margin=48, keepout=None):
        placed = [(t[0], t[1]) for t in self.things]
        for _ in range(n):
            x, y = self.random_point(sec, margin, avoid=placed, keepout=keepout)
            placed.append((x, y))
            self.thing(x, y, type_, self.rnd.choice(range(0, 360, 45)), flags)

    # ------------------------------------------------------------ compile
    def _edges(self):
        # orient: sector interior on the right of each directed edge
        verts = set()
        loops = []
        for sec, pts, hole in self.loops:
            a = area(pts)
            cw = a < 0
            if hole == cw:  # outer must be clockwise, hole counter-clockwise
                pts = pts[::-1]
            loops.append((sec, pts))
            verts.update(pts)
        verts = list(verts)
        # split T-junctions
        edges = []
        for sec, pts in loops:
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                edges.append((a, b, sec))
        out = []
        for a, b, sec in edges:
            ax, ay = a
            bx, by = b
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy
            mids = []
            for v in verts:
                if v == a or v == b:
                    continue
                vx, vy = v
                cr = (vx - ax) * dy - (vy - ay) * dx
                if cr != 0:
                    continue
                tt = ((vx - ax) * dx + (vy - ay) * dy) / L2
                if 0 < tt < 1:
                    mids.append((tt, v))
            chain = [a] + [v for _, v in sorted(mids)] + [b]
            k = (min(a, b), max(a, b))
            for p, q in zip(chain, chain[1:]):
                kk = (min(p, q), max(p, q))
                if k in self.props and kk not in self.props:
                    self.props[kk] = dict(self.props[k])
                out.append((p, q, sec))
        return out

    def check_overlaps(self):
        items = list(self.polys.items())
        bad = []
        from shapely.strtree import STRtree
        geoms = [g for _, g in items]
        tree = STRtree(geoms)
        for i, (k, g) in enumerate(items):
            for j in tree.query(g):
                if j <= i:
                    continue
                a = g.intersection(geoms[j]).area
                if a > 4:
                    bad.append((k, items[j][0], round(a)))
        return bad

    def preview(self, path, scale=0.25):
        from PIL import Image, ImageDraw
        allp = [p for _, pts, _ in self.loops for p in pts]
        minx = min(p[0] for p in allp) - 64; maxx = max(p[0] for p in allp) + 64
        miny = min(p[1] for p in allp) - 64; maxy = max(p[1] for p in allp) + 64
        W, H = int((maxx - minx) * scale), int((maxy - miny) * scale)
        im = Image.new("RGB", (W, H), (10, 12, 30))
        d = ImageDraw.Draw(im)
        T = lambda p: ((p[0] - minx) * scale, (maxy - p[1]) * scale)
        for sec, pts, hole in self.loops:
            col = (40 + (sec.floor + 64) % 200, 60, 90 + (sec.light // 2)) if not hole else (0, 0, 0)
            d.polygon([T(p) for p in pts], fill=None if hole else col, outline=(200, 200, 200))
        for x, y, a, t, f in self.things:
            c = (255, 255, 0) if t == 1 else (255, 60, 60) if t in (3004, 9, 3001, 3002, 58, 3006, 3005, 3003) else (60, 255, 120)
            X, Y = T((x, y))
            d.rectangle((X - 2, Y - 2, X + 2, Y + 2), fill=c)
        im.save(path)

    def build(self, workdir=None):
        bad = self.check_overlaps()
        if bad:
            raise ValueError("%s: overlapping sectors %s" % (self.name, bad[:10]))
        edges = self._edges()
        directed = {}
        for a, b, sec in edges:
            if (a, b) in directed:
                raise ValueError("overlapping sectors %d and %d at edge %s-%s" % (directed[(a, b)].idx, sec.idx, a, b))
            directed[(a, b)] = sec
        vidx = {}
        vlist = []

        def V(p):
            if p not in vidx:
                vidx[p] = len(vlist)
                vlist.append(p)
            return vidx[p]

        sides = []
        lines = []
        done = set()
        for (a, b), sec in directed.items():
            k = (min(a, b), max(a, b))
            if k in done:
                continue
            done.add(k)
            pr = self.props.get(k, {})
            back = directed.get((b, a))
            front = sec
            v1, v2 = a, b
            if back is not None and pr.get("front") is not None and pr["front"] is back:
                front, back = back, front
                v1, v2 = b, a
            if back is None:
                fs = len(sides)
                sides.append((pr.get("xoff", 0), pr.get("yoff", 0), "-", "-", pr.get("mid", front.wall), front.idx))
                flags = ML_BLOCKING | pr.get("flags", 0)
                lines.append((V(v1), V(v2), flags, pr.get("special", 0), pr.get("tag", 0), fs, 0xFFFF))
            else:
                fs = len(sides)
                sides.append((pr.get("xoff", 0), pr.get("yoff", 0),
                              pr.get("upper", front.upper), pr.get("lower", front.lower), pr.get("mid", "-"), front.idx))
                bs = len(sides)
                sides.append((pr.get("xoff", 0), pr.get("yoff", 0),
                              pr.get("bupper", pr.get("upper", back.upper)), pr.get("blower", pr.get("lower", back.lower)),
                              pr.get("bmid", "-"), back.idx))
                flags = ML_TWOSIDED | pr.get("flags", 0)
                lines.append((V(v1), V(v2), flags, pr.get("special", 0), pr.get("tag", 0), fs, bs))
        th = b"".join(struct.pack("<hhhhh", *t) for t in self.things)
        ld = b"".join(struct.pack("<HHHHHHH", *l) for l in lines)
        sd = b"".join(struct.pack("<hh8s8s8sH", x, y, u.encode()[:8], l.encode()[:8], m.encode()[:8], s)
                      for x, y, u, l, m, s in sides)
        vx = b"".join(struct.pack("<hh", x, y) for x, y in vlist)
        sc = b"".join(struct.pack("<hh8s8shhh", s.floor, s.ceil, s.ftex.encode()[:8], s.ctex.encode()[:8],
                                  s.light, s.special, s.tag) for s in self.sectors)
        w = Wad(b"PWAD")
        w.add(self.name)
        for n, d in (("THINGS", th), ("LINEDEFS", ld), ("SIDEDEFS", sd), ("VERTEXES", vx),
                     ("SEGS", b""), ("SSECTORS", b""), ("NODES", b""), ("SECTORS", sc),
                     ("REJECT", b""), ("BLOCKMAP", b"")):
            w.add(n, d)
        tmp = tempfile.mkdtemp(dir=workdir)
        src, dst = os.path.join(tmp, "in.wad"), os.path.join(tmp, "out.wad")
        w.write(src)
        r = subprocess.run(["zdbsp", "-R", "-o", dst, src], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stdout + r.stderr)
        out = Wad.read(dst)
        stats = dict(lines=len(lines), sides=len(sides), verts=len(vlist), sectors=len(self.sectors), things=len(self.things))
        return out.lumps, stats


# ---------------------------------------------------------------- organic shapes

def blob_room(m, sec, cx, cy, r, ports=(), wobble=0.10, n=28, seed=0, ry=None):
    """Organic room with straight 'ports' where tubes attach.
    ports: list of (angle_deg, width). Returns list of port dicts."""
    rnd = random.Random(seed)
    ry = ry or r
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]

    def rr(a):
        k = 1 + wobble * (0.6 * math.sin(3 * a + ph[0]) + 0.3 * math.sin(5 * a + ph[1]) + 0.2 * math.sin(7 * a + ph[2]))
        return k

    def pt(a, k=None):
        k = rr(a) if k is None else k
        return (cx + math.cos(a) * r * k, cy + math.sin(a) * ry * k)

    angles = [2 * math.pi * i / n for i in range(n)]
    cut = []
    port_pts = []
    for ang, w in ports:
        a = math.radians(ang)
        c = pt(a)
        tx, ty = -math.sin(a), math.cos(a)
        p1 = (c[0] + tx * w / 2, c[1] + ty * w / 2)
        p2 = (c[0] - tx * w / 2, c[1] - ty * w / 2)
        half = math.atan2(w / 2 + 24, math.hypot(c[0] - cx, c[1] - cy))
        cut.append((a, half))
        port_pts.append((a, ip(p1), ip(p2), ip(c)))

    def in_cut(a):
        for c, h in cut:
            d = (a - c + math.pi) % (2 * math.pi) - math.pi
            if abs(d) <= h:
                return True
        return False

    pts = [(a, ip(pt(a))) for a in angles if not in_cut(a)]
    for a, p1, p2, c in port_pts:
        a1 = math.atan2(p1[1] - cy, p1[0] - cx)
        a2 = math.atan2(p2[1] - cy, p2[0] - cx)
        pts.append((a1 % (2 * math.pi), p1))
        pts.append((a2 % (2 * math.pi), p2))
    pts.sort(key=lambda e: e[0])
    poly = m.poly(sec, [p for _, p in pts])
    out = []
    for a, p1, p2, c in port_pts:
        out.append({"a": p1, "b": p2, "c": c, "dir": (math.cos(a), math.sin(a)), "sector": sec})
    return out


def blob_pts(cx, cy, r, n=12, wobble=0.15, seed=0, ry=None):
    rnd = random.Random(seed)
    ry = ry or r
    ph = [rnd.uniform(0, 6.28) for _ in range(2)]
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + wobble * (0.7 * math.sin(3 * a + ph[0]) + 0.3 * math.sin(5 * a + ph[1]))
        out.append((cx + math.cos(a) * r * k, cy + math.sin(a) * ry * k))
    return out


def _lr(port, direction):
    """Return (left, right) endpoints of a port w.r.t. travel direction."""
    a, b, c = port["a"], port["b"], port["c"]
    dx, dy = direction
    cr = dx * (a[1] - c[1]) - dy * (a[0] - c[0])
    return (a, b) if cr > 0 else (b, a)


def tube(m, pA, pB, mids=(), width=128, step=64, sector_fn=None, wobble=12, seed=0,
         doors=(), steps_to=None):
    """Connect port pA to port pB through mid points.
    sector_fn(t_mid, kind) -> Sector for a segment (kind 'tube' or 'door').
    doors: list of (distance from start, kind) where kind is a dict passed back.
    Returns list of (kind, sector, left_edge, right_edge, front_line, back_line)."""
    rnd = random.Random(seed)
    cA, cB = pA["c"], pB["c"]
    lead = min(72.0, 0.22 * math.hypot(cB[0] - cA[0], cB[1] - cA[1]))
    ctrl = [cA, (cA[0] + pA["dir"][0] * lead, cA[1] + pA["dir"][1] * lead)] + [tuple(p) for p in mids] + \
           [(cB[0] + pB["dir"][0] * lead, cB[1] + pB["dir"][1] * lead), cB]
    # Catmull-Rom through the control points, sampled densely
    P = [ctrl[0]] + ctrl + [ctrl[-1]]
    dense = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        segL = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        k = max(2, int(segL / 6))
        for j in range(k):
            t = j / k
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            dense.append((x, y))
    dense.append(ctrl[-1])
    cum = [0.0]
    for a, b in zip(dense, dense[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = cum[-1]
    import bisect

    def pos(d):
        d = max(0.0, min(total, d))
        i = max(1, bisect.bisect_left(cum, d))
        i = min(i, len(cum) - 1)
        a, b = dense[i - 1], dense[i]
        L = cum[i] - cum[i - 1] or 1e-9
        t = (d - cum[i - 1]) / L
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    def at(d):
        p = pos(d)
        q0, q1 = pos(d - 20), pos(d + 20)
        tx, ty = q1[0] - q0[0], q1[1] - q0[1]
        n_ = math.hypot(tx, ty) or 1
        return p, (tx / n_, ty / n_)

    # cross-section distances
    ds = set()
    k = int(total // step)
    for i in range(1, k):
        ds.add(round(total * i / k))
    door_marks = []
    for dd, info in doors:
        dd = max(32, min(total - 48, dd))
        for e in list(ds):
            if dd - 40 < e < dd + 56:
                ds.discard(e)
        ds.add(dd)
        ds.add(dd + 16)
        door_marks.append((dd, info))
    ds = sorted(d for d in ds if 24 < d < total - 24)
    sections = []
    dA = (pA["dir"][0], pA["dir"][1])
    sections.append((0, _lr(pA, dA)))
    for d in ds:
        (x, y), (tx, ty) = at(d)
        nx, ny = -ty, tx
        is_door_edge = any(abs(d - dd) < 1 or abs(d - dd - 16) < 1 for dd, _ in door_marks)
        w = width + (0 if is_door_edge else rnd.uniform(-wobble, wobble))
        L = ip((x + nx * w / 2, y + ny * w / 2))
        R = ip((x - nx * w / 2, y - ny * w / 2))
        sections.append((d, (L, R)))
    dB = (-pB["dir"][0], -pB["dir"][1])
    sections.append((total, _lr(pB, dB)))
    from shapely.geometry import Polygon as _P

    def ok(a, b):
        (_, (L0, R0)), (_, (L1, R1)) = a, b
        q = _P([L0, L1, R1, R0])
        return q.is_valid and q.area > 64

    def protected(d):
        return any(abs(d - dd) < 1 or abs(d - dd - 16) < 1 for dd, _ in door_marks)

    # drop cross-sections that fold over their neighbours (tight bends)
    changed = True
    while changed:
        changed = False
        for i in range(1, len(sections) - 1):
            if not ok(sections[i - 1], sections[i]) or not ok(sections[i], sections[i + 1]):
                j = i if not protected(sections[i][0]) else (i + 1 if i + 1 < len(sections) - 1 and not protected(sections[i + 1][0]) else i - 1)
                if 0 < j < len(sections) - 1 and not protected(sections[j][0]):
                    sections.pop(j)
                    changed = True
                    break
    out = []
    for (d0, (L0, R0)), (d1, (L1, R1)) in zip(sections, sections[1:]):
        kind = "tube"
        info = None
        for dd, inf in door_marks:
            if abs(d0 - dd) < 1:
                kind, info = "door", inf
        tmid = (d0 + d1) / 2 / total
        if not _P([L0, L1, R1, R0]).is_valid:
            if os.environ.get("MAPGEN_LAX"):
                print("WARN tube self-intersects near", L0, "seed", seed)
                continue
            raise ValueError("tube segment self-intersects near %s (seed %d): tighten mids or narrow the tube" % (L0, seed))
        sec = sector_fn(tmid, kind, info)
        m.poly(sec, [L0, L1, R1, R0])
        out.append({"kind": kind, "info": info, "sector": sec, "L0": L0, "R0": R0, "L1": L1, "R1": R1})
    return out


def make_door(m, seg, neighbours, special=1, tex="DOORM1", track="DOORTRK"):
    """Turn a 16-unit tube segment into a door. neighbours: (sector before, sector after)."""
    sec = seg["sector"]
    before, after = neighbours
    # faces
    m.line(seg["L0"], seg["R0"], special=special, upper=tex, bupper=tex, front=before)
    m.line(seg["L1"], seg["R1"], special=special, upper=tex, bupper=tex, front=after)
    # tracks
    m.line(seg["L0"], seg["L1"], mid=track, flags=ML_DONTPEGBOTTOM)
    m.line(seg["R0"], seg["R1"], mid=track, flags=ML_DONTPEGBOTTOM)
