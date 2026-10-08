"""LLM Monitor promo — music bed synthesised in code (deterministic).

96 BPM (beat 0.625 s, bar 2.5 s), 80 s = 32 bars, loops seamlessly (starts and ends near silence).
Structure (seconds):
  0–10      intro      F#m D A E      soft pad, filtered pluck, light ticks
  10–17.5   build      F#m D E        16th arps, opening filter, snare roll
  17.5–20   lift       Esus → A       riser, IMPACT at 18.75 (logo reveal), A chord swells
  20–75     groove     A E F#m D      kick/clap/hats, bass, pad, arps; per-chapter variations
  75–80     outro      A              final hit, pad tail, fade to silence (loop point)

Usage: python3 tools/music.py assets/audio/music.wav
"""

import sys

import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
DUR = 80.0
N = int(SR * DUR)
BEAT = 60.0 / 96.0
BAR = 4 * BEAT
RNG = np.random.default_rng(20261008)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def t_axis(n):
    return np.arange(n) / SR


def place(buf, start, sig, gain=1.0):
    """Add a (n,) or (n,2) signal into the stereo buffer at time `start`."""
    i0 = int(round(start * SR))
    if i0 >= len(buf):
        return
    if sig.ndim == 1:
        sig = np.stack([sig, sig], axis=1)
    i1 = min(len(buf), i0 + len(sig))
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    buf[i0:i1] += sig[: i1 - i0] * gain


def pan(sig, p):
    """p in [-1,1] (equal power)."""
    a = (p + 1) * np.pi / 4
    return np.stack([sig * np.cos(a), sig * np.sin(a)], axis=1)


def lowpass(x, fc, order=2):
    sos = signal.butter(order, min(fc, SR / 2 - 100), "low", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def highpass(x, fc, order=2):
    sos = signal.butter(order, fc, "high", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def bandpass(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], "band", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def saw(f, n, phase=0.0):
    t = t_axis(n)
    return 2.0 * ((f * t + phase) % 1.0) - 1.0


def adsr(n, a, d, s, r, sustain_len):
    """Envelope of length n samples: attack a, decay d to level s, hold until sustain_len, release r."""
    t = t_axis(n)
    env = np.zeros(n)
    env = np.where(t < a, t / max(a, 1e-4), env)
    dmask = (t >= a) & (t < a + d)
    env = np.where(dmask, 1 - (1 - s) * (t - a) / max(d, 1e-4), env)
    hmask = (t >= a + d) & (t < sustain_len)
    env = np.where(hmask, s, env)
    rmask = t >= sustain_len
    env = np.where(rmask, s * np.exp(-(t - sustain_len) / max(r, 1e-4) * 3.0), env)
    return env


# ---------------------------------------------------------------- harmony ---
PAD_VOICING = {
    "A": [52, 57, 61, 64],
    "E": [52, 56, 59, 64],
    "F#m": [54, 57, 61, 66],
    "D": [50, 54, 57, 62],
    "Esus": [52, 57, 59, 64],
}
BASS_ROOT = {"A": 45, "E": 40, "F#m": 42, "D": 38, "Esus": 40}
ARP_TONES = {
    "A": [57, 61, 64, 69, 73, 76],
    "E": [56, 59, 64, 68, 71, 76],
    "F#m": [57, 61, 66, 69, 73, 78],
    "D": [57, 62, 66, 69, 74, 78],
    "Esus": [57, 59, 64, 69, 71, 76],
}

CHORDS = []  # (start, end, name)
for i, c in enumerate(["F#m", "D", "A", "E"]):
    CHORDS.append((i * BAR, (i + 1) * BAR, c))
for i, c in enumerate(["F#m", "D", "E"]):
    CHORDS.append((10 + i * BAR, 10 + (i + 1) * BAR, c))
CHORDS.append((17.5, 18.75, "Esus"))
CHORDS.append((18.75, 20.0, "A"))
LOOP = ["A", "E", "F#m", "D"]
for b in range(22):  # 20 → 75
    CHORDS.append((20 + b * BAR, 20 + (b + 1) * BAR, LOOP[b % 4]))
CHORDS.append((75.0, 80.0, "A"))


def section(t):
    if t < 10:
        return "intro"
    if t < 17.5:
        return "build"
    if t < 20:
        return "lift"
    if t < 28.75:
        return "reveal"
    if t < 40:
        return "measure"
    if t < 48.75:
        return "sources"
    if t < 58.75:
        return "reputation"
    if t < 67.5:
        return "audit"
    if t < 75:
        return "act"
    return "outro"


# ---------------------------------------------------------------- buses -----
pad_bus = np.zeros((N, 2))
bass_bus = np.zeros((N, 2))
pluck_bus = np.zeros((N, 2))
bell_bus = np.zeros((N, 2))
drum_bus = np.zeros((N, 2))
fx_bus = np.zeros((N, 2))

# ---------------------------------------------------------------- pad -------
for (t0, t1, name) in CHORDS:
    sec = section(t0)
    length = (t1 - t0) + 0.9
    n = int(length * SR)
    cutoff = {"intro": 900, "build": 1300, "lift": 1600, "reveal": 2600, "measure": 2200, "sources": 2400,
              "reputation": 2400, "audit": 1700, "act": 2800, "outro": 2200}[sec]
    lvl = {"intro": 0.78, "build": 0.6, "lift": 0.75, "reveal": 0.7, "measure": 0.6, "sources": 0.6,
           "reputation": 0.62, "audit": 0.5, "act": 0.66, "outro": 0.75}[sec]
    voices = np.zeros((n, 2))
    for k, m in enumerate(PAD_VOICING[name]):
        f = mtof(m)
        for j, det in enumerate((-9, 0, 8)):
            ff = f * 2 ** (det / 1200.0)
            ph = (k * 0.13 + j * 0.31) % 1.0
            s = saw(ff, n, ph)
            voices += pan(s, (-0.6, 0.0, 0.6)[j]) * 0.12
    voices = highpass(lowpass(voices, cutoff, 2), 170, 2)
    sustain = (t1 - t0) if name != "A" or t0 < 75 else 3.6
    env = adsr(n, 0.35 if sec != "lift" else 0.08, 0.4, 0.85, 0.7, sustain)
    place(pad_bus, t0, voices * env[:, None], lvl)

# ---------------------------------------------------------------- bass ------
for (t0, t1, name) in CHORDS:
    sec = section(t0)
    if sec in ("intro",):
        continue
    root = mtof(BASS_ROOT[name])
    if sec == "build":
        hits = [t0, t0 + 2 * BEAT]
        dur = 2 * BEAT * 0.9
    elif sec in ("lift",):
        hits = [t0]
        dur = (t1 - t0)
    elif sec == "outro":
        hits = [t0]
        dur = 3.0
    else:
        # driving 8ths with a rest on the "and" of 4
        hits = [t0 + i * BEAT / 2 for i in range(8) if i != 7]
        dur = BEAT / 2 * 0.82
    for h in hits:
        n = int((dur + 0.15) * SR)
        t = t_axis(n)
        s = np.sin(2 * np.pi * root * t) + 0.35 * np.sin(2 * np.pi * root * 2 * t) + 0.1 * np.sin(2 * np.pi * root * 0.5 * t)
        s = np.tanh(1.6 * s)
        env = adsr(n, 0.006, 0.12, 0.7, 0.08, dur)
        place(bass_bus, h, (s * env), 0.28)

# ---------------------------------------------------------------- arps ------
def pluck(f, length=0.6, bright=1.0):
    n = int(length * SR)
    t = t_axis(n)
    s = np.sin(2 * np.pi * f * t) + 0.5 * bright * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.08) \
        + 0.25 * bright * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.05)
    env = np.minimum(1.0, t / 0.003) * np.exp(-t / 0.22)
    return s * env


for (t0, t1, name) in CHORDS:
    sec = section(t0)
    tones = ARP_TONES[name]
    if sec == "intro":
        step, pattern, vel, bright = BEAT / 2, [0, 2, 1, 3, 2, 4, 3, 1], 0.22, 0.6
    elif sec == "build":
        step, pattern, vel, bright = BEAT / 4, [0, 1, 2, 3, 4, 3, 2, 1] * 2, 0.15, 0.8
    elif sec == "lift":
        continue
    elif sec in ("reveal", "reputation", "act"):
        step, pattern, vel, bright = BEAT / 2, [0, 2, 4, 5, 4, 2, 3, 1], 0.17, 1.0
    elif sec == "audit":
        step, pattern, vel, bright = BEAT / 4, [0, 3, 1, 4, 2, 5, 3, 1] * 2, 0.12, 1.1
    elif sec == "outro":
        step, pattern, vel, bright = BEAT / 2, [0, 2, 4, 5], 0.16, 0.9
    else:
        step, pattern, vel, bright = BEAT / 2, [0, 2, 1, 3, 2, 4, 3, 5], 0.15, 0.9
    t = t0
    i = 0
    while t < t1 - 1e-6:
        m = tones[pattern[i % len(pattern)]]
        p = pluck(mtof(m), 0.7, bright)
        accent = 1.0 if (i % 4 == 0) else 0.75
        # build: filter opens over the section
        if sec == "build":
            prog = (t - 10) / 7.5
            p = lowpass(p, 900 + 4500 * prog)
            accent *= 0.7 + 0.5 * prog
        if sec == "intro":
            p = lowpass(p, 1400)
        place(pluck_bus, t, pan(p, -0.35 if i % 2 == 0 else 0.35), vel * accent)
        t += step
        i += 1

# ---------------------------------------------------------------- bells -----
def bell(f, length=1.8):
    n = int(length * SR)
    t = t_axis(n)
    idx = 2.2 * np.exp(-t / 0.35)
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * 3.5 * f * t))
    env = np.minimum(1.0, t / 0.002) * np.exp(-t / 0.6)
    return s * env


MOTIF = [(0, 76), (1.5, 73), (2, 71), (3, 69), (4, 71), (5.5, 73), (6, 76), (7, 78)]  # beats, midi (A major pentatonic flavour)
for start in (20.0, 25.0, 40.0, 45.0, 67.5, 72.5):
    for b, m in MOTIF:
        tt = start + b * BEAT
        if tt >= 75:
            continue
        place(bell_bus, tt, pan(bell(mtof(m)), 0.2 if b % 2 else -0.2), 0.1)
# outro motif resolving on A
for b, m in [(0, 76), (1, 73), (2, 69), (4, 81)]:
    place(bell_bus, 75.0 + b * BEAT, pan(bell(mtof(m), 2.6), 0.0), 0.11)

# ---------------------------------------------------------------- drums -----
def kick():
    n = int(0.45 * SR)
    t = t_axis(n)
    f = 46 + 90 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / 0.22)
    click = RNG.standard_normal(n) * np.exp(-t / 0.002) * 0.25
    return np.tanh(1.4 * (s + highpass(click, 2000)))


def clap():
    n = int(0.35 * SR)
    t = t_axis(n)
    noise = RNG.standard_normal(n)
    env = np.zeros(n)
    for o in (0.0, 0.011, 0.022):
        env += (t >= o) * np.exp(-np.clip(t - o, 0, None) / 0.008)
    env += (t >= 0.03) * np.exp(-np.clip(t - 0.03, 0, None) / 0.12) * 0.6
    return bandpass(noise * env, 900, 3200) * 0.9


def hat(open_=False):
    n = int((0.25 if open_ else 0.08) * SR)
    t = t_axis(n)
    s = highpass(RNG.standard_normal(n), 7000) * np.exp(-t / (0.09 if open_ else 0.022))
    return s


def snare_hit(vel=1.0):
    n = int(0.18 * SR)
    t = t_axis(n)
    s = bandpass(RNG.standard_normal(n), 1500, 6000) * np.exp(-t / 0.05) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04)
    return s * vel


K = kick()
CL = clap()
kick_times = []

# intro ticks
t = 2.5
while t < 10:
    place(drum_bus, t + BEAT / 2, pan(hat(), 0.3), 0.05)
    t += BEAT
# build: hats 8ths, soft kick on 1
t = 10.0
while t < 17.5:
    place(drum_bus, t + BEAT / 2, pan(hat(), 0.3), 0.07)
    if abs(((t - 10) / BAR) - round((t - 10) / BAR)) < 1e-6:
        place(drum_bus, t, K, 0.35)
        kick_times.append(t)
    t += BEAT
# snare roll into the reveal (17.5 → 18.75)
t = 17.5
while t < 18.75 - 1e-6:
    prog = (t - 17.5) / 1.25
    step = BEAT / 4 if prog < 0.5 else BEAT / 8
    place(drum_bus, t, pan(snare_hit(0.25 + 0.6 * prog), -0.1), 0.35)
    t += step

# groove 20 → 75
t = 20.0
beat_i = 0
while t < 75.0 - 1e-6:
    sec = section(t)
    half_time = sec == "audit"
    on_kick = (beat_i % 2 == 0) if half_time else True
    if on_kick:
        place(drum_bus, t, K, 0.52)
        kick_times.append(t)
    if beat_i % 4 in (1, 3):
        place(drum_bus, t, pan(CL, 0.05), 0.33)
    # hats
    if sec == "audit":
        for k in range(4):
            place(drum_bus, t + k * BEAT / 4, pan(hat(), 0.35 if k % 2 else -0.35), 0.05 if k % 2 else 0.035)
    else:
        place(drum_bus, t + BEAT / 2, pan(hat(open_=(beat_i % 4 == 3)), 0.3), 0.075)
    t += BEAT
    beat_i += 1
# roll into the end card
t = 73.75
while t < 75.0 - 1e-6:
    prog = (t - 73.75) / 1.25
    step = BEAT / 4 if prog < 0.5 else BEAT / 8
    place(drum_bus, t, pan(snare_hit(0.2 + 0.6 * prog), -0.1), 0.3)
    t += step
# final hit
place(drum_bus, 75.0, K, 0.8)
kick_times.append(75.0)

# ---------------------------------------------------------------- fx --------
def riser(length):
    n = int(length * SR)
    t = t_axis(n)
    prog = t / length
    noise = RNG.standard_normal(n)
    out = np.zeros(n)
    seg = int(0.05 * SR)
    for i0 in range(0, n, seg):
        i1 = min(n, i0 + seg)
        c = 300 * (20 ** prog[i0])
        out[i0:i1] = bandpass(noise[max(0, i0 - 2000):i1], c * 0.7, min(c * 1.4, 20000))[-(i1 - i0):]
    tone = np.sin(2 * np.pi * np.cumsum(180 + 700 * prog ** 2) / SR) * 0.3
    return (out + tone) * (prog ** 2.2)


def impact(length=2.6):
    n = int(length * SR)
    t = t_axis(n)
    boom = np.sin(2 * np.pi * np.cumsum(32 + 40 * np.exp(-t / 0.15)) / SR) * np.exp(-t / 0.9)
    crash = lowpass(RNG.standard_normal(n), 5000) * np.exp(-t / 0.5) * 0.35
    return np.tanh(1.3 * (boom + crash))


place(fx_bus, 16.0, pan(riser(2.75), 0.0), 0.32)
place(fx_bus, 18.75, impact(), 0.75)
place(fx_bus, 72.5, pan(riser(2.5), 0.0), 0.22)
place(fx_bus, 75.0, impact(3.0), 0.6)

# ---------------------------------------------------------------- mix -------
# sidechain pump on pad + bass from the kicks
duck = np.ones(N)
tt = t_axis(N)
for k in kick_times:
    i0 = int(k * SR)
    i1 = min(N, i0 + int(0.5 * SR))
    seg = tt[i0:i1] - k
    duck[i0:i1] = np.minimum(duck[i0:i1], 1 - 0.42 * np.exp(-seg / 0.16))
pad_bus *= duck[:, None]
bass_bus *= duck[:, None]


def reverb_ir(length=2.4, decay=0.85):
    n = int(length * SR)
    t = t_axis(n)
    l = RNG.standard_normal(n) * np.exp(-t / decay * 3)
    r = RNG.standard_normal(n) * np.exp(-t / decay * 3)
    ir = np.stack([l, r], axis=1)
    ir = lowpass(ir, 6000)
    ir[: int(0.012 * SR)] = 0  # pre-delay
    return ir / np.sqrt((ir ** 2).sum(axis=0))


IR = reverb_ir()
send = pad_bus * 0.35 + pluck_bus * 0.35 + bell_bus * 0.5 + drum_bus * 0.08 + fx_bus * 0.25
wet = np.stack([signal.fftconvolve(send[:, c], IR[:, c])[:N] for c in range(2)], axis=1)


def delay_pingpong(x, time, fb, mix):
    d = int(time * SR)
    out = np.zeros_like(x)
    l = np.zeros(N)
    r = np.zeros(N)
    src = x.mean(axis=1)
    for rep in range(1, 6):
        g = fb ** (rep - 1)
        sh = np.zeros(N)
        sh[d * rep:] = src[: N - d * rep] * g
        if rep % 2:
            l += sh
        else:
            r += sh
    out[:, 0] = l
    out[:, 1] = r
    return out * mix


dly = delay_pingpong(pluck_bus + bell_bus * 0.6, BEAT * 0.75, 0.42, 0.32)

mix = pad_bus * 0.78 + bass_bus * 1.0 + pluck_bus * 1.0 + bell_bus * 1.0 + drum_bus * 1.0 + fx_bus * 1.0 + wet * 0.55 + dly
mix = highpass(mix, 34)

# fades: loop-friendly start and end
fade_in = np.clip(tt / 0.9, 0, 1) ** 2
fade_out = np.clip((80.0 - tt) / 2.2, 0, 1) ** 1.5
mix *= (fade_in * fade_out)[:, None]

# soft clip + normalise
peak = np.max(np.abs(mix))
mix = mix / peak * 1.25
mix = np.tanh(mix) / np.tanh(1.25)
mix = mix / np.max(np.abs(mix)) * 0.89  # ≈ -1 dBFS

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
sf.write(out, mix.astype(np.float32), SR, subtype="PCM_24")
print("wrote", out, mix.shape, "peak", float(np.max(np.abs(mix))))
