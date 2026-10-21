"""Render a music bed from a JSON spec written by build.py.

spec = {
  "style": "vlog" | "aftermovie" | "insights",
  "duration": seconds,
  "sections": [[t0, t1, energy], ...]   # seconds, snapped to bars by build.py
  "impacts": [t, ...],                  # boom + crash on these times
  "risers": [t, ...],                   # riser that ends exactly on t
  "stops": [t, ...],                    # one beat of silence ending on t (pre-drop)
  "fills": [t, ...]                     # snare roll during the beat before t
}
Usage: python3 tools/songs.py spec.json out.wav
"""

import json
import sys

import numpy as np
import soundfile as sf

from music_engine import SR, Song, master, mtof

STYLES = {
    "vlog": {
        "bpm": 120, "seed": 2026_10_16,
        "loop": ["G", "D", "Em", "C"],
        "voicing": {"G": [55, 59, 62, 67], "D": [54, 57, 62, 66], "Em": [55, 59, 64, 67], "C": [55, 60, 64, 67]},
        "bass": {"G": 43, "D": 38, "Em": 40, "C": 36},
        "arp": {"G": [67, 71, 74, 79, 83], "D": [66, 69, 74, 78, 81], "Em": [67, 71, 76, 79, 83], "C": [67, 72, 76, 79, 84]},
        # hook over 2 bars, (8th index, midi, length in 8ths)
        "hook": [(0, 74, 2), (2, 76, 2), (4, 79, 3), (7, 78, 1), (8, 76, 2), (10, 74, 2), (12, 71, 2), (14, 74, 2)],
        "levels": {},
    },
    "aftermovie": {
        "bpm": 128, "seed": 2026_10_17,
        "loop": ["Am", "F", "C", "G"],
        "voicing": {"Am": [57, 60, 64, 69], "F": [57, 60, 65, 69], "C": [55, 60, 64, 67], "G": [55, 59, 62, 67]},
        "bass": {"Am": 45, "F": 41, "C": 36, "G": 43},
        "arp": {"Am": [69, 72, 76, 81, 84], "F": [69, 72, 77, 81, 84], "C": [67, 72, 76, 79, 84], "G": [67, 71, 74, 79, 83]},
        "hook": [(0, 76, 1), (1, 76, 1), (2, 79, 2), (4, 81, 2), (6, 79, 1), (7, 76, 1), (8, 74, 2), (10, 76, 2), (12, 72, 3), (15, 74, 1)],
        "levels": {"drums": 0.7, "stab": 0.8},
    },
    "insights": {
        "bpm": 100, "seed": 2026_10_18,
        "loop": ["Dm", "Bb", "F", "C"],
        "voicing": {"Dm": [57, 62, 65, 69], "Bb": [58, 62, 65, 70], "F": [57, 60, 65, 69], "C": [55, 60, 64, 67]},
        "bass": {"Dm": 38, "Bb": 34, "F": 41, "C": 36},
        "arp": {"Dm": [69, 74, 77, 81, 86], "Bb": [70, 74, 77, 82, 86], "F": [69, 72, 77, 81, 84], "C": [67, 72, 76, 79, 84]},
        "hook": [(0, 81, 2), (3, 77, 1), (4, 79, 2), (6, 76, 2), (8, 77, 3), (11, 74, 1), (12, 72, 4)],
        "levels": {"drums": 0.55, "lead": 0.45},
    },
}


def energy_at(sections, t):
    for t0, t1, e in sections:
        if t0 - 1e-6 <= t < t1 - 1e-6:
            return e
    return -1


def arrange_bar(song, st, style, t0, bar_len, E, nextE, b, K, CL, stopped, spec):
    beat, bar = song.beat, song.bar
    if True:
        chord = st["loop"][b % len(st["loop"])]
        voic = st["voicing"][chord]
        root = mtof(st["bass"][chord])
        tones = st["arp"][chord]

        # ---- pad (always) ------------------------------------------------
        cutoff = {0: 1100, 1: 1700, 2: 2500, 3: 4200}[E]
        lvl = {0: 0.75, 1: 0.7, 2: 0.65, 3: 0.6}[E]
        if style == "insights":
            cutoff *= 0.8
        pad = song.supersaw(voic, bar_len, cutoff, attack=0.35 if E < 2 else 0.05, release=0.7)
        song.place("pad", t0, pad, lvl)
        if E >= 2:  # sub-octave body
            song.place("pad", t0, song.supersaw([voic[0] - 12], bar_len, 600, voices=3, release=0.4), 0.35)

        # ---- pluck / arp ---------------------------------------------------
        if style == "insights":
            pattern = [0, 2, 1, 3, 2, 4, 3, 1] if E < 2 else [0, 2, 4, 2, 1, 3, 4, 3]
            step = beat / 2
        elif E == 0:
            pattern, step = [0, 2, 1, 3], beat
        elif E == 1:
            pattern, step = [0, 2, 1, 3, 2, 4, 3, 1], beat / 2
        elif E == 2:
            pattern, step = [0, 1, 2, 3, 4, 3, 2, 1] * 2, beat / 4
        else:
            pattern, step = [0, 2, 4, 3, 1, 3, 2, 4], beat / 2
        vel = {0: 0.16, 1: 0.18, 2: 0.13, 3: 0.17}[E]
        bright = {0: 0.5, 1: 0.8, 2: 1.0, 3: 1.1}[E]
        for i, pi in enumerate(pattern):
            tt = t0 + i * step
            if tt >= t0 + bar_len - 1e-6 or stopped(tt):
                continue
            p = song.pluck(mtof(tones[pi % len(tones)]), 0.55, bright)
            acc = 1.0 if i % 4 == 0 else 0.72
            song.place("pluck", tt, p, vel * acc, -0.35 if i % 2 == 0 else 0.35)

        # ---- drums -----------------------------------------------------------
        for k in range(4):
            tt = t0 + k * beat
            if tt >= t0 + bar_len - 1e-6 or stopped(tt):
                continue
            if E == 1 and k in (0, 2):
                song.place("drums", tt, K, 0.42)
                song.kicks.append(tt)
            if E >= 2:
                song.place("drums", tt, K, 0.62 if E == 2 else 0.7)
                song.kicks.append(tt)
            if E >= 2 and k in (1, 3):
                song.place("drums", tt, CL, 0.36 if E == 2 else 0.42, 0.04)
            # hats
            if E >= 1:
                off = tt + beat / 2
                if not stopped(off):
                    song.place("perc", off, song.hat(open_=(E == 3 and k % 2 == 1)), 0.11 if E == 1 else 0.14, 0.25)
            if E >= 2:
                for s in range(4):
                    ts = tt + s * beat / 4
                    if not stopped(ts):
                        song.place("perc", ts, song.shaker(), 0.07 if s % 2 else 0.045, -0.3)
            if E == 3 and style != "insights":
                song.place("perc", tt, song.ride(), 0.05, 0.4)

        # ---- bass ------------------------------------------------------------
        if E >= 2:
            if E == 2 or style == "insights":
                hits = [(t0 + k * beat + beat / 2, root, beat * 0.42) for k in range(4) if k * beat + beat / 2 < bar_len]
            else:
                seq = [1, 1, 2, 1, 1, 1.5, 2, 1]
                hits = [(t0 + i * beat / 2, root * seq[i], beat * 0.4) for i in range(8) if (i % 2 == 1 or i == 6) and i * beat / 2 < bar_len]
            for (tt, f, ln) in hits:
                if not stopped(tt):
                    song.place("bass", tt, song.bass_note(f, ln, cutoff=700 if E == 2 else 1100), 0.34)

        # ---- stabs + hook (full energy) ------------------------------------
        if E == 3:
            stab_times = [1.5, 3.5] if style == "vlog" else [0.5, 1.5, 2.75, 3.5]
            for s in stab_times:
                tt = t0 + s * beat
                if tt < t0 + bar_len and not stopped(tt):
                    song.place("stab", tt, song.stab([m + 12 for m in voic[1:]], 0.2), 0.55)
            if b % 2 == 0:
                for (i8, m, ln) in st["hook"]:
                    tt = t0 + i8 * beat / 2
                    if tt < t0 + bar_len and tt < spec["duration"] and not stopped(tt):
                        song.place("lead", tt, song.lead(mtof(m), ln * beat / 2 * 0.92), 0.22, 0.1)

        # ---- transitions -------------------------------------------------------
        if nextE > E and nextE >= 2:
            # fill in the last beat into a lift
            for s in range(8):
                tt = t0 + bar_len - beat + s * beat / 8
                song.place("drums", tt, song.snare(0.25 + 0.09 * s), 0.3, -0.1)
        if 0 <= nextE < E and E >= 2:
            song.place("fx", t0 + bar_len - 0.2, song.downlifter(1.4), 0.25)




def arrange(spec):
    st = STYLES[spec["style"]]
    song = Song(st["bpm"], spec["duration"], st["seed"])
    beat, bar = song.beat, song.bar
    sections = spec["sections"]
    stops = spec.get("stops", [])
    n_bars = int(np.ceil(spec["duration"] / bar))
    K = song.kick()
    CL = song.clap()
    style = spec["style"]

    def stopped(t):
        return any(s - beat - 1e-6 <= t < s - 1e-6 for s in stops)

    bar_count = 0
    for si, (s_t0, s_t1, E) in enumerate(sections):
        nextE = sections[si + 1][2] if si + 1 < len(sections) else -1
        nb = int(np.ceil((s_t1 - s_t0) / bar - 1e-6))
        for b in range(nb):
            t0 = s_t0 + b * bar
            last_bar = b == nb - 1
            bar_len = min(bar, s_t1 - t0)
            bar_count += 1
            arrange_bar(song, st, style, t0, bar_len, E, nextE if last_bar else E, bar_count - 1, K, CL, stopped, spec)

    # ---- explicit accents ---------------------------------------------------------
    for t in spec.get("risers", []):
        ln = min(2 * bar, max(bar, 3.0))
        song.place("fx", t - ln, song.riser(ln), 0.3)
        song.place("fx", t - 1.2, song.reverse_swell(1.2), 0.35)
    for t in spec.get("impacts", []):
        song.place("fx", t, song.impact(), 0.6)
        song.place("drums", t, song.crash(), 0.55)
        song.place("fx", t, song.sub_drop(), 0.3)
    for t in spec.get("fills", []):
        for s in range(8):
            song.place("drums", t - beat + s * beat / 8, song.snare(0.3 + 0.08 * s), 0.32, -0.1)
    return song, st


def main():
    spec = json.load(open(sys.argv[1]))
    song, st = arrange(spec)
    mix = master(song, fade_out=spec.get("fade_out", 1.8), levels=st.get("levels"))
    sf.write(sys.argv[2], mix, SR, subtype="PCM_24")
    print("wrote", sys.argv[2], f"{spec['duration']:.2f}s", st["bpm"], "bpm")


if __name__ == "__main__":
    main()
