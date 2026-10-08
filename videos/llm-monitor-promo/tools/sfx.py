"""LLM Monitor promo — sound-design track: library SFX (Pixabay licence, see assets/sfx/CREDITS.md)
placed on the picture. Times are the moment the sound must PEAK (synced to the on-screen action).

Usage: python3 tools/sfx.py assets/sfx assets/audio/sfx.wav   (decodes the library MP3s with ffmpeg)
"""

import os
import subprocess
import sys

import numpy as np
import soundfile as sf

SR = 48000
DUR = 80.0
N = int(SR * DUR)

PEAK = {  # measured peak offset (s) of each file
    "chime": 0.43, "click-soft": 0.06, "click": 0.06, "error": 0.75, "impact-bass-1": 0.33,
    "impact-bass-2": 2.04, "key-press": 0.08, "notification": 0.24, "ping": 0.33, "pop": 0.13,
    "sparkle": 0.09, "typing": 0.0, "whoosh-cinematic": 2.55, "whoosh-short": 0.17, "whoosh": 0.17,
}

CUES = []


def cue(t, name, gain, pitch=1.0):
    CUES.append((t, name, gain, pitch))


# ---- A · la recherche devient une réponse (0 → 11.25)
cue(0.55, "whoosh", 0.45)                       # iris opens
cue(1.2, "typing", 0.32)                        # query types
for k, t in enumerate((2.72, 2.82, 2.93)):
    cue(t, "key-press", 0.22 + 0.03 * k)
cue(3.16, "click", 0.5)                         # enter
cue(4.65, "whoosh-short", 0.4)                  # links contract
cue(6.45, "whoosh", 0.32)                       # page dissolves
for t, g in ((6.9, 0.42), (8.1, 0.36), (8.65, 0.36), (9.25, 0.33), (9.8, 0.33)):
    cue(t, "pop", g)                            # answer engines fan out

# ---- B · la question business (11.25 → 18.75)
cue(11.35, "whoosh-short", 0.3)
cue(11.4, "typing", 0.24)
for t in (11.75, 12.15, 12.55):
    cue(t, "pop", 0.24)                         # profiles
cue(12.75, "click-soft", 0.3)                   # answer generates
cue(13.85, "whoosh-short", 0.18)
cue(14.35, "whoosh-short", 0.18)                # reorder
cue(14.65, "click-soft", 0.26)
for t in (15.4, 15.7, 16.0):
    cue(t, "pop", 0.24)                         # trends
cue(16.45, "error", 0.16)                       # your brand stalls
cue(17.05, "ping", 0.42)                        # reticle locks on
cue(17.6, "click-soft", 0.3)                    # quarter turn
cue(18.6, "whoosh-cinematic", 0.38)             # dive into the pupil
cue(18.75, "impact-bass-1", 0.55)               # brand world

# ---- C · une présence IA lisible (18.75 → 28.75)
cue(19.25, "sparkle", 0.32)                     # reticle traces
cue(20.05, "click-soft", 0.3)                   # quarter turn
cue(20.65, "whoosh-short", 0.3)                 # name reveal
cue(21.95, "whoosh-short", 0.24)                # logo rises
cue(23.6, "whoosh", 0.3)                        # citations converge
for t in (23.85, 23.97, 24.09):
    cue(t, "pop", 0.3)                          # glass KPIs
cue(25.6, "ping", 0.24)                         # values freeze
cue(26.05, "pop", 0.3)                          # no expertise needed
cue(28.6, "whoosh-cinematic", 0.34)             # dive into the ring
cue(28.85, "sparkle", 0.18)                     # match cut

# ---- D · mesurer (28.75 → 40)
for i in range(4):
    cue(29.55 + i * 0.36, "click-soft", 0.17)   # curve points
cue(30.75, "pop", 0.24)                         # +7 pts
cue(31.05, "whoosh-short", 0.24)                # pan → ranking
for i in range(5):
    cue(31.45 + i * 0.22, "click-soft", 0.2)    # rows
cue(32.85, "pop", 0.24)                         # +1 place
cue(33.1, "whoosh-short", 0.24)                 # pan → share of voice
cue(34.45, "pop", 0.22)                         # +4 pts
cue(34.8, "whoosh-short", 0.24)                 # pull back
for i in range(4):
    cue(36.1 + i * 0.7, "click-soft", 0.17)     # trend scrub
cue(40.25, "whoosh", 0.42)                      # travelling → E

# ---- E · ce qui influence les réponses (40 → 48.75)
cue(40.75, "pop", 0.3)                          # answer node
for i in range(5):
    cue(42.5 + i * 0.42, "pop", 0.24)           # sources connect
cue(45.75, "chime", 0.3)                        # influential sources stand out
cue(49.0, "whoosh", 0.42)                       # travelling → F

# ---- F · réputation IA (48.75 → 58.75)
cue(49.35, "whoosh-short", 0.24)
for t in (51.7, 52.08, 52.46):
    cue(t, "pop", 0.24)                         # themes
cue(53.05, "error", 0.15)                       # price = watch point
for t in (53.75, 54.75, 56.05):
    cue(t, "click-soft", 0.22)                  # bars fill
for k, t in enumerate((54.85, 55.85, 57.15)):
    cue(t, "ping", 0.16 + 0.03 * k)             # ring grows
cue(57.25, "chime", 0.24)                       # positive perception
cue(59.0, "whoosh", 0.42)                       # travelling → G

# ---- G · vérifier (58.75 → 67.5)
cue(59.15, "whoosh-short", 0.22)
for i in range(9):
    cue(59.33 + i * 0.05, "key-press", 0.12 + 0.02 * (i % 3))
for t in (60.0, 61.7, 63.1):
    cue(t, "whoosh-short", 0.14)                # scan lines
for t in (60.23, 60.51, 60.79, 61.93, 62.21, 63.33, 63.61):
    cue(t, "click", 0.19)                       # checks
for t in (62.49, 63.89):
    cue(t, "error", 0.11)                       # weak points
cue(64.4, "chime", 0.24)                        # analysis done
cue(65.4, "notification", 0.22)                 # 2 points to fix
cue(67.75, "whoosh", 0.42)                      # travelling → H

# ---- H · agir (67.5 → 74.75)
for t in (68.3, 68.72, 69.14):
    cue(t, "whoosh-short", 0.2)                 # actions by priority
cue(71.25, "ping", 0.24)                        # +11 pts
cue(71.6, "pop", 0.2)                           # loop appears
for i in range(4):
    cue(72.1 + i * 0.32, "click-soft", 0.2)     # measure → act
cue(73.35, "whoosh-short", 0.24)                # back to measure
cue(73.75, "ping", 0.36)                        # reticle on "Mesurer"
cue(74.7, "whoosh-cinematic", 0.36)             # pupil opens

# ---- I · end card (74.75 → 80)
cue(74.95, "sparkle", 0.3)
cue(75.0, "impact-bass-2", 0.5)                 # final hit (its build starts ~73 s)
for t in (76.05, 76.67, 77.29):
    cue(t, "whoosh-short", 0.14)                # Mesurez / Comprenez / Agissez
cue(77.75, "click-soft", 0.2)
cue(79.4, "whoosh", 0.18)                       # defocus to the pupil
cue(79.6, "pop", 0.18)                          # pupil (loop point)


def load(src_dir, name, cache={}):
    if name not in cache:
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", os.path.join(src_dir, name + ".mp3"), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
            check=True, capture_output=True,
        ).stdout
        cache[name] = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)
    return cache[name]


def main():
    src_dir, out = sys.argv[1], sys.argv[2]
    buf = np.zeros((N, 2))
    for t, name, gain, _ in CUES:
        x = load(src_dir, name)
        start = t - PEAK[name]
        i0 = int(round(start * SR))
        if i0 < 0:
            x = x[-i0:]
            i0 = 0
        i1 = min(N, i0 + len(x))
        buf[i0:i1] += x[: i1 - i0] * gain
    # gentle loop-safe edges
    tt = np.arange(N) / SR
    buf *= (np.clip(tt / 0.05, 0, 1) * np.clip((DUR - tt) / 0.05, 0, 1))[:, None]
    peak = np.max(np.abs(buf))
    if peak > 0.95:
        buf *= 0.95 / peak
    sf.write(out, buf.astype(np.float32), SR, subtype="PCM_24")
    print("wrote", out, len(CUES), "cues, peak", round(float(np.max(np.abs(buf))), 3))


if __name__ == "__main__":
    main()
