#!/usr/bin/env python3
"""Synthesize a guide voice-over from voiceover.json with Piper.

Each line is placed at its start time; a line too long for its window is sped up
(down to length_scale 0.8) so the guide shows where the real recording must fit.

Usage:
  python3 tools/tts_guide.py --model fr_FR-tom-medium.onnx --out vo_guide.wav [--duration 50.5]
"""
import argparse
import io
import json
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
from piper import PiperVoice, SynthesisConfig

ROOT = Path(__file__).resolve().parent.parent
SR = 44100


def synth(voice, text, length_scale):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        voice.synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=length_scale))
    buf.seek(0)
    audio, sr = sf.read(buf)
    # Trim leading/trailing silence so start times mean "first syllable".
    loud = np.flatnonzero(np.abs(audio) > 0.02)
    audio = audio[max(0, loud[0] - int(0.01 * sr)) : loud[-1] + int(0.05 * sr)]
    n = round(len(audio) * SR / sr)
    return np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--duration", type=float, default=50.5)
    args = ap.parse_args()

    voice = PiperVoice.load(args.model)
    lines = json.loads((ROOT / "voiceover.json").read_text())["lines"]
    track = np.zeros(round(args.duration * SR))
    for line in lines:
        window = line["end"] - line["start"]
        scale = 1.0
        audio = synth(voice, line["text"], scale)
        if len(audio) / SR > window:
            scale = max(0.8, window / (len(audio) / SR))
            audio = synth(voice, line["text"], scale)
        a = round(line["start"] * SR)
        audio = audio[: len(track) - a]
        track[a : a + len(audio)] += audio
        print(f"{line['start']:6.2f}  {len(audio) / SR:4.2f}s / {window:4.2f}s  x{1 / scale:.2f}  {line['text']}")
    track *= 0.7 / np.abs(track).max()
    sf.write(args.out, np.stack([track, track], axis=1), SR, subtype="PCM_24")


if __name__ == "__main__":
    main()
