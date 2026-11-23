"""Rebuild outro-logo/assets/outro.wav: the V1 end-card audio without the speech before it.

Renders only the last two sections of the V1 music (same chords via bar_offset), adds the end-card
SFX at the same offsets as in build.py (impact-bass-2 just before the hit, chime 1.25 s after),
fades the tail and normalises to -14 LUFS / -1 dBTP.
  python3 tools/outro_audio.py      (run from videos/llm-monitor-summit)
"""

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SR = 48000
sys.path.insert(0, str(TOOLS))
from build import loudnorm  # noqa: E402

spec = json.load(open(ROOT / "v1-vlog" / "assets" / "music_spec.json"))
bar = 60 / 120 * 4
end_t = spec["sections"][-1][0]
start, end = end_t - 0.067, spec["duration"]
part = dict(spec)
part["sections"] = [[end_t - bar, end_t, spec["sections"][-2][2]], spec["sections"][-1]]
part["bar_offset"] = sum(int(math.ceil((b - a) / bar - 1e-6)) for a, b, _ in spec["sections"][:-1]) - 1
part["impacts"] = [t for t in spec["impacts"] if t >= end_t - 0.01]
part["risers"] = [t for t in spec["risers"] if t >= end_t - 0.01]

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    json.dump(part, open(tmp / "spec.json", "w"))
    subprocess.run([sys.executable, str(TOOLS / "songs.py"), str(tmp / "spec.json"), str(tmp / "music.wav")], check=True, cwd=TOOLS)
    music, _ = sf.read(tmp / "music.wav", dtype="float32", always_2d=True)
    seg = music[int(start * SR):int(end * SR)] * 0.8
    for name, t, vol in (("impact-bass-2", end_t - 0.05, 0.5), ("chime", end_t + 1.25, 0.28)):
        mp3 = ROOT.parent / "llm-monitor-promo" / "assets" / "sfx" / f"{name}.mp3"
        wav = tmp / f"{name}.wav"
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(mp3), "-ar", str(SR), "-ac", "2", str(wav)], check=True)
        x, _ = sf.read(wav, dtype="float32", always_2d=True)
        i0 = int(round((t - start) * SR))
        i1 = min(len(seg), i0 + len(x))
        seg[i0:i1] += x[: i1 - i0] * vol
    tail = int(0.6 * SR)
    seg[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(tmp / "premix.wav", seg, SR, subtype="FLOAT")
    loudnorm(tmp / "premix.wav", ROOT / "outro-logo" / "assets" / "outro.wav")
print("outro-logo/assets/outro.wav written")
