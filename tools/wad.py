"""Minimal WAD reader/writer."""
import struct


class Wad:
    def __init__(self, kind=b"IWAD"):
        self.kind = kind
        self.lumps = []  # list of [name, bytes]

    @classmethod
    def read(cls, path):
        data = open(path, "rb").read()
        kind, n, off = struct.unpack_from("<4sii", data, 0)
        w = cls(kind)
        for i in range(n):
            lo, sz, nm = struct.unpack_from("<ii8s", data, off + 16 * i)
            w.lumps.append([nm.rstrip(b"\0").decode("latin1").upper(), data[lo:lo + sz]])
        return w

    def add(self, name, data=b""):
        self.lumps.append([name.upper(), bytes(data)])

    def find(self, name):
        for i, (n, _) in enumerate(self.lumps):
            if n == name:
                return i
        return -1

    def get(self, name):
        i = self.find(name)
        return self.lumps[i][1] if i >= 0 else None

    def namespace(self, start, end):
        """Lumps between markers (exclusive)."""
        out, inside = [], False
        for n, d in self.lumps:
            if n == start:
                inside = True
                continue
            if n == end:
                inside = False
                continue
            if inside:
                out.append((n, d))
        return out

    def write(self, path):
        body = bytearray()
        dirs = []
        off = 12
        for n, d in self.lumps:
            dirs.append((off if d else 0, len(d), n))
            body += d
            off += len(d)
        head = struct.pack("<4sii", self.kind, len(self.lumps), 12 + len(body))
        dd = b"".join(struct.pack("<ii8s", o, s, n.encode("latin1")[:8]) for o, s, n in dirs)
        open(path, "wb").write(head + body + dd)
