#!/usr/bin/env python3
"""Render the New York vlog teaser from edit.json.

Same rushes and same frame-exact pipeline as the intro (shared helpers come from
../vlog-new-york-intro/tools/build.py). Here the music is edited from several
passages of the song, and each shot carries its own start time, taken from the
song's hits rather than from a fixed tempo grid (the band breathes: 95-117 BPM).

Usage:
  python3 tools/build.py --source "VLOG NEW YORK GOOD.mp4" --music sinatra.wav \
      [--music-alt instrumental.wav] --out renders
"""
import argparse
import importlib.util
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "intro_build", ROOT.parent / "vlog-new-york-intro" / "tools" / "build.py")
_intro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_intro)
decode_segment, probe_size, run, write_edl = (
    _intro.decode_segment, _intro.probe_size, _intro.run, _intro.write_edl)


def plan(edit):
    fps = edit["fps"]
    shots = edit["shots"]
    end_frame = round(edit["end"] * fps)
    rows = []
    for i, s in enumerate(shots):
        out_in = round(s["start"] * fps)
        out_out = end_frame if i + 1 == len(shots) else round(shots[i + 1]["start"] * fps)
        n = out_out - out_in
        if n <= 0:
            raise SystemExit(f"shot {i + 1} has no frames")
        row = dict(s, idx=i + 1, out_in=out_in, n=n)
        if s["clip"] is not None:
            clip_in, clip_out = (round(x * fps) for x in edit["clips"][str(s["clip"])])
            src_in = round(s["src"] * fps)
            if src_in < clip_in or src_in + n > clip_out:
                raise SystemExit(
                    f"shot {i + 1} (clip #{s['clip']}) needs frames {src_in}-{src_in + n} "
                    f"but the clip only spans {clip_in}-{clip_out}"
                )
            row["src_in"] = src_in
        rows.append(row)
    if rows[0]["out_in"] != 0:
        raise SystemExit("the first shot must start at 0")
    return rows


def render_picture(source, rows, edit, picture):
    fps = edit["fps"]
    width, height = probe_size(source)
    frame_bytes = width * height * 3 // 2
    black = bytes([16]) * (width * height) + bytes([128]) * (width * height // 2)
    fade = edit.get("video_fade_out_frames", 0)
    total = round(edit["end"] * fps)
    vf = f"fade=t=out:start_frame={total - fade}:nb_frames={fade}" if fade else "null"
    enc = subprocess.Popen([
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{width}x{height}", "-framerate", str(fps),
        "-i", "-", "-vf", vf,
        "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-profile:v", "high",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(picture),
    ], stdin=subprocess.PIPE)

    def frames(row):
        if row["clip"] is None:
            return black * row["n"]
        return decode_segment(source, row, fps, frame_bytes)

    with ThreadPoolExecutor(4) as ex:
        for i in range(0, len(rows), 4):
            for raw in ex.map(frames, rows[i : i + 4]):
                enc.stdin.write(raw)
    enc.stdin.close()
    if enc.wait() != 0:
        raise SystemExit("video encode failed")


def edit_music(path, edit):
    """Join the song passages listed in edit.json, with a short equal-power
    crossfade centred on each join, then fade out the tail."""
    music = edit["music"]
    y, sr = sf.read(path, always_2d=True)
    h = round(music["crossfade"] * sr / 2)
    ramp = np.linspace(0, np.pi / 2, 2 * h)[:, None]
    out = np.zeros((0, y.shape[1]))
    for i, seg in enumerate(music["segments"]):
        if "silence" in seg:
            piece = np.zeros((round(seg["silence"] * sr) + (2 * h if i else h), y.shape[1]))
        else:
            a, b = round(seg["from"] * sr), round(seg["to"] * sr)
            piece = y[(a - h if i else a) : b + h].copy()
        if i:
            out[-2 * h :] = out[-2 * h :] * np.cos(ramp) + piece[: 2 * h] * np.sin(ramp)
            piece = piece[2 * h :]
        out = np.concatenate([out, piece])
    total = round(edit["end"] * sr)
    out = np.pad(out, ((0, max(0, total - len(out))), (0, 0)))[:total]
    fade = round(music["fade_out"] * sr)
    if fade:
        out[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    return out, sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--music", required=True, help="the song (WAV)")
    ap.add_argument("--music-alt", help="optional second version of the song (e.g. without vocals)")
    ap.add_argument("--out", default=str(ROOT / "renders"))
    ap.add_argument("--reuse-picture", action="store_true")
    args = ap.parse_args()

    edit = json.loads((ROOT / "edit.json").read_text())
    out_dir = Path(args.out)
    work = out_dir / "_work"
    work.mkdir(parents=True, exist_ok=True)

    rows = plan(edit)
    picture = work / "picture.mp4"
    if not (args.reuse_picture and picture.exists()):
        render_picture(args.source, rows, edit, picture)

    versions = [("sinatra", args.music)]
    if args.music_alt:
        versions.append(("sinatra-sans-voix", args.music_alt))
    for name, src in versions:
        audio, sr = edit_music(src, edit)
        wav = out_dir / f"Teaser_NYC_musique_{name}.wav"
        sf.write(wav, audio, sr, subtype="PCM_24")
        mp4 = out_dir / f"Teaser_NYC_{name}.mp4"
        run([
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(picture), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "-shortest", str(mp4),
        ])
        print("wrote", mp4)

    write_edl([r for r in rows if r["clip"] is not None], edit, out_dir / "Teaser_NYC.edl", "TEASER NEW YORK")
    fps = edit["fps"]
    with open(out_dir / "plans.tsv", "w", encoding="utf-8") as f:
        f.write("plan\tdebut\tfin\tclip\tsource_in\tdescription\n")
        for r in rows:
            src = f"{r['src_in'] / fps:.2f}" if r["clip"] is not None else "-"
            clip = f"#{r['clip']}" if r["clip"] is not None else "noir"
            f.write(f"{r['idx']}\t{r['out_in'] / fps:.2f}\t{(r['out_in'] + r['n']) / fps:.2f}\t{clip}\t{src}\t{r['label']}\n")


if __name__ == "__main__":
    main()
