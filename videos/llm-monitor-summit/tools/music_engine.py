"""LLM Monitor @ SEO & GEO Summit — original music beds, synthesised in code (deterministic, royalty-free).

A small arrangement engine: a song is a tempo, a chord loop and a list of sections, each with an
energy level. Energy decides which instruments play in a bar:

  0  pad + soft pluck                        (under speech, very light)
  1  pad + pluck + shaker/hats + soft kick   (under speech, groove felt)
  2  + bass + clap                           (b-roll, mid energy)
  3  + chord stabs + lead hook + open hats   (montage / drop, full energy)

Accents are placed on top: risers that end on a time, impacts, reverse swells, tape stops and
drum fills. Songs are defined in songs.py; run `python3 tools/songs.py <name> <out.wav>`.
"""

import numpy as np
from scipy import signal

SR = 48000


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def t_axis(n):
    return np.arange(n) / SR


def stereo(sig, p=0.0):
    """Mono -> equal-power panned stereo, p in [-1, 1]."""
    a = (p + 1) * np.pi / 4
    return np.stack([sig * np.cos(a), sig * np.sin(a)], axis=1)


def sos(kind, fc, order=2):
    if isinstance(fc, (list, tuple)):
        fc = [min(max(f, 20), SR / 2 - 200) for f in fc]
    else:
        fc = min(max(fc, 20), SR / 2 - 200)
    return signal.butter(order, fc, kind, fs=SR, output="sos")


def lp(x, fc, order=2):
    return signal.sosfilt(sos("low", fc, order), x, axis=0)


def hp(x, fc, order=2):
    return signal.sosfilt(sos("high", fc, order), x, axis=0)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(sos("band", [lo, hi], order), x, axis=0)


def sweep_lp(x, f0, f1, block=256, q=0.9):
    """Time-varying resonant low-pass (biquad, coefficients per block, state carried)."""
    n = len(x)
    mono = x.ndim == 1
    xs = x[:, None] if mono else x
    out = np.zeros_like(xs)
    zi = np.zeros((2, xs.shape[1]))
    nb = (n + block - 1) // block
    for b in range(nb):
        i0, i1 = b * block, min(n, (b + 1) * block)
        prog = b / max(1, nb - 1)
        fc = f0 * (f1 / f0) ** prog
        w0 = 2 * np.pi * min(fc, SR / 2 - 300) / SR
        alpha = np.sin(w0) / (2 * q)
        cw = np.cos(w0)
        bcoef = np.array([(1 - cw) / 2, 1 - cw, (1 - cw) / 2])
        acoef = np.array([1 + alpha, -2 * cw, 1 - alpha])
        bcoef /= acoef[0]
        acoef /= acoef[0]
        for c in range(xs.shape[1]):
            y, zf = signal.lfilter(bcoef, acoef, xs[i0:i1, c], zi=zi[:, c])
            out[i0:i1, c] = y
            zi[:, c] = zf
    return out[:, 0] if mono else out


def env_adsr(n, a, d, s, r, hold):
    t = t_axis(n)
    e = np.where(t < a, t / max(a, 1e-4), 0.0)
    m = (t >= a) & (t < a + d)
    e = np.where(m, 1 - (1 - s) * (t - a) / max(d, 1e-4), e)
    m = (t >= a + d) & (t < hold)
    e = np.where(m, s, e)
    m = t >= hold
    rel_start = s if hold >= a + d else 1.0
    e = np.where(m, rel_start * np.exp(-(t - hold) / max(r, 1e-4) * 4.0), e)
    return e


class Song:
    def __init__(self, bpm, duration, seed):
        self.bpm = bpm
        self.beat = 60.0 / bpm
        self.bar = 4 * self.beat
        self.dur = duration
        self.n = int(round(duration * SR))
        self.rng = np.random.default_rng(seed)
        names = ("drums", "bass", "pad", "stab", "pluck", "lead", "fx", "perc")
        self.bus = {k: np.zeros((self.n, 2)) for k in names}
        self.kicks = []

    # ------------------------------------------------------------------ util
    def place(self, bus, start, sig, gain=1.0, p=0.0):
        if sig.ndim == 1:
            sig = stereo(sig, p)
        i0 = int(round(start * SR))
        if i0 >= self.n:
            return
        if i0 < 0:
            sig = sig[-i0:]
            i0 = 0
        i1 = min(self.n, i0 + len(sig))
        self.bus[bus][i0:i1] += sig[: i1 - i0] * gain

    def noise(self, n):
        return self.rng.standard_normal(n)

    # ------------------------------------------------------------- drums
    def kick(self, punch=1.0):
        n = int(0.5 * SR)
        t = t_axis(n)
        f = 48 + 150 * np.exp(-t / 0.028) + 40 * np.exp(-t / 0.006)
        ph = 2 * np.pi * np.cumsum(f) / SR
        body = np.sin(ph) * np.exp(-t / (0.19 * punch))
        click = hp(self.noise(n) * np.exp(-t / 0.0025), 1800) * 0.35
        return np.tanh(1.8 * (body + click)) * 0.95

    def clap(self):
        n = int(0.4 * SR)
        t = t_axis(n)
        e = np.zeros(n)
        for o in (0.0, 0.009, 0.019, 0.027):
            e += (t >= o) * np.exp(-np.clip(t - o, 0, None) / 0.006)
        e += (t >= 0.03) * np.exp(-np.clip(t - 0.03, 0, None) / 0.13) * 0.7
        body = bp(self.noise(n) * e, 800, 4200)
        tone = np.sin(2 * np.pi * 210 * t) * np.exp(-t / 0.03) * 0.25
        return (body + tone) * 0.9

    def snare(self, vel=1.0):
        n = int(0.25 * SR)
        t = t_axis(n)
        s = bp(self.noise(n), 1500, 7500) * np.exp(-t / 0.07) + 0.5 * np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.045)
        return s * vel

    def hat(self, open_=False):
        n = int((0.32 if open_ else 0.07) * SR)
        t = t_axis(n)
        metal = np.zeros(n)
        for f in (3140, 4720, 5960, 7230, 8840, 10180):
            metal += np.sign(np.sin(2 * np.pi * f * t))
        s = hp(self.noise(n) * 0.6 + metal * 0.12, 7200, 3)
        return s * np.exp(-t / (0.11 if open_ else 0.018))

    def shaker(self):
        n = int(0.09 * SR)
        t = t_axis(n)
        e = np.minimum(1, t / 0.012) * np.exp(-t / 0.03)
        return bp(self.noise(n), 5500, 12000) * e

    def crash(self, length=2.8):
        n = int(length * SR)
        t = t_axis(n)
        s = hp(self.noise(n), 4500, 2) * np.exp(-t / 0.9)
        s += hp(self.noise(n), 9000, 2) * np.exp(-t / 1.6) * 0.5
        return s * 0.5

    def ride(self):
        n = int(0.6 * SR)
        t = t_axis(n)
        bell = sum(np.sin(2 * np.pi * f * t) for f in (2950, 4410, 6380)) * np.exp(-t / 0.18) * 0.12
        return hp(self.noise(n), 6500) * np.exp(-t / 0.25) * 0.5 + bell

    # ------------------------------------------------------------- tonal
    def supersaw(self, midis, length, cutoff, voices=7, detune=14.0, attack=0.25, release=0.6, hold=None):
        n = int((length + release) * SR)
        t = t_axis(n)
        out = np.zeros((n, 2))
        for k, m in enumerate(midis):
            f = mtof(m)
            for v in range(voices):
                d = (v - (voices - 1) / 2) / ((voices - 1) / 2)
                ff = f * 2 ** (d * detune / 1200.0)
                ph = self.rng.random()
                s = 2.0 * ((ff * t + ph) % 1.0) - 1.0
                out += stereo(s, d * 0.8) * (0.9 if v == (voices // 2) else 0.55)
        out /= max(1, len(midis)) * voices * 0.55
        out = lp(out, cutoff, 2)
        out = hp(out, 140, 2)
        e = env_adsr(n, attack, 0.3, 0.85, release, hold if hold is not None else length)
        return out * e[:, None]

    def stab(self, midis, length=0.22, cutoff=3800):
        n = int((length + 0.25) * SR)
        t = t_axis(n)
        out = np.zeros((n, 2))
        for m in midis:
            f = mtof(m)
            for v, d in enumerate((-0.11, 0.0, 0.12)):
                ff = f * 2 ** (d / 12)
                s = 2.0 * ((ff * t + 0.37 * v) % 1.0) - 1.0
                out += stereo(s, (-0.5, 0, 0.5)[v])
        out /= len(midis) * 3
        filt_env = cutoff * (0.35 + 0.65 * np.exp(-t / 0.08))
        out = lp(out, cutoff, 2) * 0.6 + lp(out, cutoff * 0.4, 2) * 0.4
        e = np.minimum(1, t / 0.004) * np.exp(-t / (length * 0.6))
        del filt_env
        return hp(out, 200) * e[:, None]

    def pluck(self, f, length=0.5, bright=1.0):
        n = int(length * SR)
        t = t_axis(n)
        s = np.sin(2 * np.pi * f * t)
        s += 0.55 * bright * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.07)
        s += 0.3 * bright * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.045)
        s += 0.15 * bright * np.sin(2 * np.pi * 4.01 * f * t) * np.exp(-t / 0.03)
        e = np.minimum(1, t / 0.002) * np.exp(-t / 0.19)
        return s * e

    def bell(self, f, length=1.6):
        n = int(length * SR)
        t = t_axis(n)
        idx = 2.0 * np.exp(-t / 0.3)
        s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * 3.5 * f * t))
        return s * np.minimum(1, t / 0.002) * np.exp(-t / 0.55)

    def lead(self, f, length, vib=True):
        n = int((length + 0.12) * SR)
        t = t_axis(n)
        fm = f * (1 + (0.004 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.15) / 0.2, 0, 1) if vib else 0))
        ph = 2 * np.pi * np.cumsum(fm) / SR
        s = np.sign(np.sin(ph)) * 0.35 + (2 * ((np.cumsum(fm) / SR) % 1.0) - 1) * 0.45
        s = lp(s, 3200, 2)
        e = env_adsr(n, 0.01, 0.12, 0.75, 0.08, length)
        return s * e

    def bass_note(self, f, length, drive=1.6, cutoff=900):
        n = int((length + 0.06) * SR)
        t = t_axis(n)
        sub = np.sin(2 * np.pi * f * t)
        sawv = 2 * ((f * t) % 1.0) - 1
        s = sub * 0.8 + lp(sawv, cutoff, 2) * 0.45
        s = np.tanh(drive * s)
        e = env_adsr(n, 0.004, 0.09, 0.75, 0.04, length)
        return s * e

    # ------------------------------------------------------------- fx
    def riser(self, length, top=9000):
        n = int(length * SR)
        t = t_axis(n)
        prog = t / length
        nz = sweep_lp(self.noise(n), 250, top, q=2.5)
        tone = np.sin(2 * np.pi * np.cumsum(220 + 880 * prog ** 2) / SR) * 0.2
        return (nz * 0.8 + tone) * prog ** 2.0

    def downlifter(self, length=1.6):
        n = int(length * SR)
        t = t_axis(n)
        prog = t / length
        nz = sweep_lp(self.noise(n), 7000, 300, q=1.2)
        return nz * (1 - prog) ** 1.8 * 0.7

    def impact(self, length=2.4):
        n = int(length * SR)
        t = t_axis(n)
        boom = np.sin(2 * np.pi * np.cumsum(34 + 70 * np.exp(-t / 0.09)) / SR) * np.exp(-t / 0.8)
        crash = lp(self.noise(n), 6000) * np.exp(-t / 0.45) * 0.35
        return np.tanh(1.5 * (boom + crash))

    def reverse_swell(self, length=1.2):
        n = int(length * SR)
        t = t_axis(n)
        s = hp(self.noise(n), 3000) * (t / length) ** 3
        return s * 0.6

    def sub_drop(self, length=1.4):
        n = int(length * SR)
        t = t_axis(n)
        f = 70 * np.exp(-t / 0.6) + 28
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7)


def reverb_ir(length, decay, rng):
    n = int(length * SR)
    t = t_axis(n)
    ir = np.stack([rng.standard_normal(n), rng.standard_normal(n)], axis=1) * np.exp(-t / decay * 3)[:, None]
    ir = lp(ir, 7000)
    ir[: int(0.015 * SR)] = 0
    return ir / np.sqrt((ir ** 2).sum(axis=0))


def conv(x, ir):
    return np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)


def pingpong(x, delay, fb, n_rep=5):
    d = int(delay * SR)
    out = np.zeros_like(x)
    src = x.mean(axis=1)
    for rep in range(1, n_rep + 1):
        if d * rep >= len(x):
            break
        g = fb ** (rep - 1)
        out[d * rep:, (rep + 1) % 2] += src[: len(x) - d * rep] * g
    return out


def sidechain(song, depth=0.5, rel=0.18):
    duck = np.ones(song.n)
    tt = t_axis(song.n)
    for k in song.kicks:
        i0 = int(k * SR)
        i1 = min(song.n, i0 + int(0.6 * SR))
        seg = tt[i0:i1] - k
        att = np.clip(seg / 0.004, 0, 1)
        duck[i0:i1] = np.minimum(duck[i0:i1], 1 - depth * att * np.exp(-seg / rel))
    return duck


def master(song, fade_in=0.02, fade_out=1.5, levels=None):
    lv = {"drums": 0.62, "bass": 0.62, "pad": 1.0, "stab": 0.7, "pluck": 0.95, "lead": 0.6, "fx": 0.7, "perc": 0.9}
    if levels:
        lv.update(levels)
    duck = sidechain(song)[:, None]
    b = song.bus
    b["pad"] *= duck
    b["bass"] *= sidechain(song, 0.7, 0.12)[:, None]
    b["stab"] *= duck
    ir = reverb_ir(2.6, 1.0, song.rng)
    send = b["pad"] * 0.3 + b["pluck"] * 0.45 + b["lead"] * 0.35 + b["stab"] * 0.3 + b["drums"] * 0.05 + b["fx"] * 0.3 + b["perc"] * 0.15
    wet = conv(send, ir)
    dly = pingpong(b["pluck"] * 0.6 + b["lead"] * 0.5, song.beat * 0.75, 0.38)
    mix = sum(b[k] * lv[k] for k in b) + wet * 0.5 + dly * 0.3
    mix = hp(mix, 42, 3)
    # gentle low-mid dip so speech sits on top
    mix = mix - bp(mix, 280, 900) * 0.18
    tt = t_axis(song.n)
    fi = np.clip(tt / max(fade_in, 1e-3), 0, 1)
    fo = np.clip((song.dur - tt) / max(fade_out, 1e-3), 0, 1) ** 1.3
    mix *= (fi * fo)[:, None]
    peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / peak * 1.4
    mix = np.tanh(mix) / np.tanh(1.4)
    return (mix / (np.max(np.abs(mix)) + 1e-9) * 0.89).astype(np.float32)
