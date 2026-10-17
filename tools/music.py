"""Original MIDI music for LYMPHODOOM (played by the engine's OPL synth via GENMIDI).

Tracks: D_INTRO (title), D_E1M1 lymph node (upbeat chiptune-metal), D_E1M2 bloodstream
(heartbeat pulse), D_E1M3 tumor (dark), D_INTER (map between levels), D_VICTOR (finale)."""
import struct

PPQ = 96

# GM drum notes
KICK, SNARE, HAT, OHAT, CRASH, TOM_L, TOM_M, TOM_H, RIDE = 36, 38, 42, 46, 49, 41, 45, 48, 51

NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def n(name, octave):
    return 12 * (octave + 1) + NOTE[name]


def vlq(v):
    out = [v & 0x7F]
    v >>= 7
    while v:
        out.append((v & 0x7F) | 0x80)
        v >>= 7
    return bytes(reversed(out))


class Song:
    def __init__(self, bpm):
        self.bpm = bpm
        self.ev = []  # (tick, order, bytes)
        self.notes = []  # (start tick, end tick, channel, pitch, velocity)
        self.programs = {}

    def program(self, ch, prog, vol=100, pan=64):
        self.ev.append((0, 0, bytes([0xC0 | ch, prog])))
        self.ev.append((0, 0, bytes([0xB0 | ch, 7, vol])))
        self.ev.append((0, 0, bytes([0xB0 | ch, 10, pan])))

    def note(self, ch, pitch, start, dur, vel=96):
        s = int(round(start * PPQ))
        e = int(round((start + dur) * PPQ)) - 2
        self.ev.append((s, 2, bytes([0x90 | ch, pitch, vel])))
        self.ev.append((max(s + 1, e), 1, bytes([0x80 | ch, pitch, 0])))
        self.notes.append((s, max(s + 1, e), ch, pitch, vel))

    def chord(self, ch, pitches, start, dur, vel=90):
        for p in pitches:
            self.note(ch, p, start, dur, vel)

    def drum(self, pitch, start, vel=100, dur=0.25):
        self.note(9, pitch, start, dur, vel)

    def bytes(self, length_beats):
        tempo = int(60_000_000 / self.bpm)
        evs = [(0, 0, b"\xff\x51\x03" + tempo.to_bytes(3, "big"))] + sorted(self.ev, key=lambda e: (e[0], e[1]))
        end = int(length_beats * PPQ)
        data = bytearray()
        last = 0
        for tick, _, b in evs:
            tick = min(tick, end)
            data += vlq(tick - last) + b
            last = tick
        data += vlq(end - last) + b"\xff\x2f\x00"
        trk = b"MTrk" + struct.pack(">I", len(data)) + bytes(data)
        return b"MThd" + struct.pack(">IHHH", 6, 0, 1, PPQ) + trk


def power(root):
    return [root, root + 7, root + 12]


# ---------------------------------------------------------------- E1M1: lymph node

def lymph_node_song():
    s = Song(150)
    s.program(0, 30, 92)       # distortion guitar
    s.program(1, 33, 110)      # electric bass (finger)
    s.program(2, 80, 80, 40)   # square lead
    s.program(3, 29, 70, 90)   # overdrive guitar (harmony)
    E, G, A, C, D, B = n("E", 2), n("G", 2), n("A", 2), n("C", 3), n("D", 3), n("B", 2)
    riff = [(E, 0), (E, 0.5), (G, 1), (E, 1.5), (A, 2), (E, 2.5), (G, 3), (Bb := n("Bb", 2), 3.5)]
    prog = [E, E, C, D, E, E, A, B]
    bars = 32
    for bar in range(bars):
        t0 = bar * 4
        sec = bar // 8
        root = prog[bar % 8]
        # guitar riff: chugs with power chords on the accents
        if sec in (0, 2):
            for p, o in riff:
                pp = p + (root - E)
                s.chord(0, power(pp), t0 + o, 0.45, 100)
        else:
            for k in range(8):
                s.chord(0, power(root), t0 + k * 0.5, 0.4 if k % 2 == 0 else 0.25, 104 if k % 2 == 0 else 80)
        # bass doubles the roots in eighths
        for k in range(8):
            s.note(1, root - 12 + (12 if k == 7 else 0), t0 + k * 0.5, 0.45, 100)
        # drums: rock beat, double kick in section 3
        for k in range(8):
            s.drum(HAT, t0 + k * 0.5, 70 if k % 2 else 90)
        s.drum(KICK, t0, 120); s.drum(KICK, t0 + 2.5, 110)
        if sec == 3:
            for k in range(16):
                s.drum(KICK, t0 + k * 0.25, 90)
        else:
            s.drum(KICK, t0 + 1.5, 100)
        s.drum(SNARE, t0 + 1, 115); s.drum(SNARE, t0 + 3, 115)
        if bar % 8 == 7:
            for k, tom in enumerate((TOM_H, TOM_H, TOM_M, TOM_L)):
                s.drum(tom, t0 + 3 + k * 0.25, 110)
        if bar % 8 == 0:
            s.drum(CRASH, t0, 110)
    # lead melody in sections 1 and 3 (heroic, E minor pentatonic)
    mel = [(n("E", 5), 1), (n("G", 5), 0.5), (n("A", 5), 0.5), (n("B", 5), 1.5), (n("A", 5), 0.5),
           (n("G", 5), 1), (n("E", 5), 1), (n("D", 5), 1), (n("E", 5), 1),
           (n("G", 5), 0.5), (n("A", 5), 0.5), (n("B", 5), 0.5), (n("D", 6), 0.5), (n("B", 5), 2),
           (n("A", 5), 1), (n("G", 5), 1), (n("A", 5), 1), (n("B", 5), 3)]
    for start_bar in (8, 24):
        t = start_bar * 4
        for rep in range(2):
            for p, d in mel:
                s.note(2, p, t, d * 0.95, 100)
                s.note(3, p - 12 - 5, t, d * 0.95, 60)
                t += d
    return s


def lymph_node():
    return lymph_node_song().bytes(128)


def web_score():
    """The same E1M1 notes, in seconds, for the page's small Web Audio synth."""
    s = lymph_node_song()
    seconds = 60 / s.bpm / PPQ
    notes = [[round(start * seconds, 4), round((end - start) * seconds, 4), channel, pitch, velocity]
             for start, end, channel, pitch, velocity in s.notes]
    return {"duration": 128 * 60 / s.bpm, "notes": sorted(notes)}


# ---------------------------------------------------------------- E1M2: bloodstream

def bloodstream():
    s = Song(76)
    s.program(0, 89, 85)       # warm pad
    s.program(1, 38, 110)      # synth bass
    s.program(2, 81, 70, 30)   # saw arp
    s.program(3, 98, 60, 100)  # crystal
    prog = [(n("D", 3), "m"), (n("Bb", 2), "M"), (n("F", 3), "M"), (n("C", 3), "M")]
    bars = 32
    for bar in range(bars):
        t0 = bar * 4
        root, q = prog[(bar // 2) % 4]
        third = 3 if q == "m" else 4
        tri = [root, root + third, root + 7]
        if bar % 2 == 0:
            s.chord(0, [p + 12 for p in tri], t0, 7.8, 70)
        # heartbeat: lub-dub, every beat
        for b in range(4):
            s.drum(KICK, t0 + b, 120)
            s.drum(KICK, t0 + b + 0.25, 85)
            s.note(1, root - 12, t0 + b, 0.2, 110)
            s.note(1, root - 12, t0 + b + 0.25, 0.2, 80)
        if bar >= 8:
            for k in range(16):
                p = (tri + [tri[1] + 12])[k % 4] + 12
                s.note(2, p, t0 + k * 0.25, 0.22, 70 if k % 4 else 90)
        if bar >= 16:
            s.drum(HAT, t0 + 0.5, 50); s.drum(HAT, t0 + 1.5, 50); s.drum(HAT, t0 + 2.5, 50); s.drum(HAT, t0 + 3.5, 50)
            s.drum(SNARE, t0 + 2, 60)
        if 16 <= bar < 32 and bar % 4 == 0:
            for k, p in enumerate([n("A", 5), n("F", 5), n("D", 5), n("E", 5)]):
                s.note(3, p, t0 + k * 2, 1.9, 70)
    return s.bytes(bars * 4)


# ---------------------------------------------------------------- E1M3: tumor

def tumor():
    s = Song(96)
    s.program(0, 48, 90)       # strings
    s.program(1, 52, 70)       # choir
    s.program(2, 30, 95)       # distortion guitar
    s.program(3, 32, 115)      # acoustic bass
    s.program(4, 19, 60)       # church organ
    C, Db, Eb, F, G, Ab, Bb = (n(x, 2) for x in ("C", "Db", "Eb", "F", "G", "Ab", "Bb"))
    prog = [C, C, Db, C, Ab, Bb, C, G]
    bars = 32
    for bar in range(bars):
        t0 = bar * 4
        root = prog[bar % 8]
        s.chord(0, [root + 12, root + 15, root + 19], t0, 3.9, 75)
        if bar >= 8:
            s.chord(1, [root + 24, root + 27], t0, 3.9, 60)
        # chugging guitar (phrygian), palm-muted feel
        if bar >= 4:
            pat = [0, 0.75, 1.5, 2, 2.75, 3.5]
            for o in pat:
                s.chord(2, power(root), t0 + o, 0.3, 105)
        s.note(3, root - 12, t0, 1.5, 110)
        s.note(3, root - 12, t0 + 2, 1.5, 100)
        # slow, heavy drums with toms
        s.drum(KICK, t0, 120); s.drum(KICK, t0 + 0.75, 100); s.drum(KICK, t0 + 2.5, 110)
        s.drum(SNARE, t0 + 2, 110)
        s.drum(RIDE, t0 + 1, 60); s.drum(RIDE, t0 + 3, 60)
        if bar % 4 == 3:
            for k, tom in enumerate((TOM_L, TOM_L, TOM_M, TOM_L)):
                s.drum(tom, t0 + 3 + k * 0.25, 110)
        if bar % 8 == 0:
            s.drum(CRASH, t0, 100)
        if 16 <= bar < 24:
            mel = [n("C", 5), n("Db", 5), n("C", 5), n("G", 4)]
            s.note(4, mel[bar % 4], t0, 3.8, 70)
    return s.bytes(bars * 4)


# ---------------------------------------------------------------- title, intermission, victory

def intro():
    s = Song(120)
    s.program(0, 61, 105)      # brass section
    s.program(1, 48, 80)       # strings
    s.program(2, 33, 100)
    fan = [(n("E", 4), 0.5), (n("E", 4), 0.25), (n("E", 4), 0.25), (n("G", 4), 1), (n("E", 4), 0.5),
           (n("D", 4), 0.5), (n("E", 4), 1), (n("B", 4), 1.5), (n("A", 4), 0.5), (n("G", 4), 1),
           (n("A", 4), 1), (n("B", 4), 3)]
    t = 0
    for p, d in fan:
        s.chord(0, [p, p + 7], t, d * 0.95, 110)
        t += d
    for bar, root in enumerate([n("E", 3), n("C", 3), n("D", 3), n("E", 3)]):
        s.chord(1, [root, root + 7, root + 12, root + 15 if bar % 2 == 0 else root + 16], bar * 4, 3.9, 70)
        for k in range(4):
            s.note(2, root - 12, bar * 4 + k, 0.9, 100)
            s.drum(TOM_L if k % 2 == 0 else TOM_M, bar * 4 + k, 90)
    s.drum(CRASH, 0, 110)
    return s.bytes(16)


def inter():
    s = Song(104)
    s.program(0, 4, 90)        # electric piano
    s.program(1, 33, 100)
    prog = [(n("A", 3), [0, 3, 7, 10]), (n("D", 3), [0, 4, 7, 10]), (n("G", 3), [0, 4, 7, 11]), (n("C", 3), [0, 4, 7, 11])]
    for bar in range(16):
        t0 = bar * 4
        root, iv = prog[bar % 4]
        for k in (0, 1.5, 2.5):
            s.chord(0, [root + i for i in iv], t0 + k, 0.8, 75)
        s.note(1, root - 12, t0, 1.4, 100); s.note(1, root - 5, t0 + 1.5, 0.9, 90)
        s.note(1, root - 12, t0 + 2.5, 1.4, 95)
        for k in range(8):
            s.drum(HAT, t0 + k * 0.5, 55 if k % 2 else 70)
        s.drum(KICK, t0, 100); s.drum(SNARE, t0 + 1, 80); s.drum(KICK, t0 + 2.5, 90); s.drum(SNARE, t0 + 3, 80)
    return s.bytes(64)


def victory():
    s = Song(112)
    s.program(0, 61, 110)
    s.program(1, 48, 85)
    s.program(2, 80, 80)
    prog = [n("C", 3), n("G", 2), n("A", 2), n("F", 2)]
    mel = [n("G", 5), n("E", 5), n("G", 5), n("C", 6), n("B", 5), n("G", 5), n("A", 5), n("F", 5)]
    for bar in range(16):
        t0 = bar * 4
        root = prog[bar % 4]
        third = 3 if bar % 4 == 2 else 4
        s.chord(1, [root + 12, root + 12 + third, root + 19], t0, 3.9, 75)
        s.chord(0, [root + 12, root + 19], t0, 1, 100)
        s.note(2, mel[(bar * 2) % 8], t0, 2, 95)
        s.note(2, mel[(bar * 2 + 1) % 8], t0 + 2, 2, 95)
        s.drum(KICK, t0, 100); s.drum(SNARE, t0 + 1, 80); s.drum(KICK, t0 + 2, 100); s.drum(SNARE, t0 + 3, 80)
        if bar % 4 == 0:
            s.drum(CRASH, t0, 100)
    return s.bytes(64)


def all_music():
    return {
        "D_INTRO": intro(),
        "D_E1M1": lymph_node(),
        "D_E1M2": bloodstream(),
        "D_E1M3": tumor(),
        "D_INTER": inter(),
        "D_VICTOR": victory(),
    }


if __name__ == "__main__":
    import os, sys
    out = sys.argv[1] if len(sys.argv) > 1 else "music"
    os.makedirs(out, exist_ok=True)
    for k, v in all_music().items():
        open(os.path.join(out, k + ".mid"), "wb").write(v)
        print(k, len(v))
