#!/usr/bin/env python3
"""Render the New York vlog intro from edit.json.

Cuts the shots out of the rushes compilation frame-accurately, places each cut
on the music's beat grid, builds the edited music (one phrase removed so the
intro lands at ~50 s) and muxes one MP4 per music version.

Usage:
  python3 tools/build.py --source "VLOG NEW YORK GOOD.mp4" \
      --music music.wav --instrumental no_vocals.wav --out renders [--vo vo.wav]
"""
import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent


def beat_time(music, k):
    """Output time of beat k, after the phrase cut."""
    t = music["first_beat"] + k * music["beat"]
    if k >= 36:
        sp = music["splice"]
        t += 32 * music["beat"] - (sp["b_start"] - sp["a_end"])
    return t


def plan(edit):
    fps, music = edit["fps"], edit["music"]
    end_frame = round(edit["end"] * fps)
    rows = []
    for i, s in enumerate(edit["shots"]):
        out_in = 0 if s["from_k"] is None else round(beat_time(music, s["from_k"]) * fps)
        out_out = end_frame if s["to_k"] is None else round(beat_time(music, s["to_k"]) * fps)
        n = out_out - out_in
        clip_in, clip_out = (round(x * fps) for x in edit["clips"][str(s["clip"])])
        src_in = round(s["src"] * fps)
        if src_in < clip_in or src_in + n > clip_out:
            raise SystemExit(
                f"shot {i + 1} (clip #{s['clip']}) needs frames {src_in}-{src_in + n} "
                f"but the clip only spans {clip_in}-{clip_out}"
            )
        rows.append(dict(s, idx=i + 1, out_in=out_in, n=n, src_in=src_in))
    return rows


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_size(source):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(source)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return tuple(int(x) for x in out.split(","))


def decode_segment(source, row, fps, frame_bytes):
    """Raw yuv420p frames src_in .. src_in+n-1, exactly.

    Seeking half a frame before the target makes ffmpeg's accurate seek keep
    frame src_in as the first frame (source timestamps are exact multiples of 1/fps).
    Frames are piped raw so no container timestamp can shift or duplicate them.
    """
    raw = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
         "-ss", f"{(row['src_in'] - 0.5) / fps:.4f}", "-i", str(source),
         "-frames:v", str(row["n"]), "-an", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-"],
        capture_output=True, check=True,
    ).stdout
    if len(raw) != row["n"] * frame_bytes:
        raise SystemExit(f"shot {row['idx']}: got {len(raw) // frame_bytes} frames, expected {row['n']}")
    return raw


def render_picture(source, rows, edit, picture):
    """One encoder fed raw frames in edit order: frame i of the output is exactly
    the i-th planned frame, whatever the source container's timestamps."""
    fps = edit["fps"]
    total_frames = round(edit["end"] * fps)
    fade_frames = edit["video_fade_out_frames"]
    width, height = probe_size(source)
    frame_bytes = width * height * 3 // 2
    enc = subprocess.Popen([
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{width}x{height}", "-framerate", str(fps),
        "-i", "-",
        "-vf", f"fade=t=out:start_frame={total_frames - fade_frames}:nb_frames={fade_frames}",
        "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-profile:v", "high",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(picture),
    ], stdin=subprocess.PIPE)
    with ThreadPoolExecutor(4) as ex:
        for i in range(0, len(rows), 4):  # small batches keep memory bounded
            batch = rows[i : i + 4]
            for raw in ex.map(lambda r: decode_segment(source, r, fps, frame_bytes), batch):
                enc.stdin.write(raw)
    enc.stdin.close()
    if enc.wait() != 0:
        raise SystemExit("video encode failed")


def edit_music(path, edit, duration):
    music = edit["music"]
    sp = music["splice"]
    y, sr = sf.read(path, always_2d=True)
    a_end, b_start = round(sp["a_end"] * sr), round(sp["b_start"] * sr)
    xf = round(sp["crossfade"] * sr)
    total = round(duration * sr)
    head = y[: a_end + xf].copy()
    tail = y[b_start : b_start + total - a_end].copy()
    # Equal-power crossfade across the splice so the cut doesn't click.
    ramp = np.linspace(0, np.pi / 2, xf)[:, None]
    tail[:xf] = head[a_end:] * np.cos(ramp) + tail[:xf] * np.sin(ramp)
    out = np.concatenate([head[:a_end], tail])[:total]
    fade = round(music["fade_out"] * sr)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    return out, sr


def write_edl(rows, edit, path):
    fps = edit["fps"]

    def tc(frame):
        s, f = divmod(frame, fps)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"

    lines = ["TITLE: INTRO NEW YORK", "FCM: NON-DROP FRAME", ""]
    for r in rows:
        rec_in = r["out_in"] + 3600 * fps  # record timeline starts at 01:00:00:00
        lines.append(
            f"{r['idx']:03d}  AX       V     C        "
            f"{tc(r['src_in'])} {tc(r['src_in'] + r['n'])} {tc(rec_in)} {tc(rec_in + r['n'])}"
        )
        lines.append(f"* FROM CLIP NAME: {edit['source']}")
        lines.append(f"* PLAN {r['idx']} - {r['label']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--music", required=True, help="the original music track (WAV)")
    ap.add_argument("--instrumental", required=True, help="the same track without vocals (WAV)")
    ap.add_argument("--vo", help="optional guide voice-over WAV, mixed over the instrumental")
    ap.add_argument("--out", default=str(ROOT / "renders"))
    ap.add_argument("--work", default=None, help="scratch dir for intermediates")
    ap.add_argument("--reuse-picture", action="store_true",
                    help="keep the already encoded picture, only rebuild audio and muxes")
    args = ap.parse_args()

    edit = json.loads((ROOT / "edit.json").read_text())
    fps = edit["fps"]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(args.work or out_dir / "_work")
    work.mkdir(parents=True, exist_ok=True)

    rows = plan(edit)
    duration = edit["end"]
    picture = work / "picture.mp4"
    if not (args.reuse_picture and picture.exists()):
        render_picture(args.source, rows, edit, picture)

    tracks = {}
    for name, src in [("instru", args.instrumental), ("musique-originale", args.music)]:
        audio, sr = edit_music(src, edit, duration)
        wav = out_dir / f"Intro_NYC_musique_{name}.wav"
        sf.write(wav, audio, sr, subtype="PCM_24")
        tracks[name] = wav

    if args.vo:
        vo, sr_vo = sf.read(args.vo, always_2d=True)
        bed, sr = sf.read(tracks["instru"], always_2d=True)
        assert sr == sr_vo, "voice-over must match the music sample rate"
        vo = np.pad(vo, ((0, max(0, len(bed) - len(vo))), (0, 0)))[: len(bed)]
        if vo.shape[1] == 1:
            vo = np.repeat(vo, 2, axis=1)
        # Voice at -16 dBFS RMS while speaking, music ducked 9 dB under it.
        env = np.abs(vo).max(axis=1)
        win = round(0.25 * sr)
        env = np.convolve(env, np.ones(win) / win, mode="same")
        speaking = env > env.max() * 0.05
        vo *= 10 ** (-16 / 20) / np.sqrt(np.mean(vo[speaking] ** 2))
        duck = 1 - (1 - 10 ** (-9 / 20)) * np.clip(env / (env.max() * 0.05), 0, 1)
        mix = bed * duck[:, None] + vo
        mix /= max(1.0, np.abs(mix).max() / 0.98)
        wav = out_dir / "Intro_NYC_musique_instru+voix-temoin.wav"
        sf.write(wav, mix, sr, subtype="PCM_24")
        tracks["instru+voix-temoin"] = wav

    for name, wav in tracks.items():
        mp4 = out_dir / f"Intro_NYC_{name}.mp4"
        run([
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(picture), "-i", str(wav),
            "-map", "0:v", "-map", "1:a", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "-shortest",
            str(mp4),
        ])
        print("wrote", mp4)

    write_edl(rows, edit, out_dir / "Intro_NYC.edl")
    with open(out_dir / "plans.tsv", "w", encoding="utf-8") as f:
        f.write("plan\tdebut\tfin\tclip\tsource_in\tsource_out\tdescription\n")
        for r in rows:
            f.write(
                f"{r['idx']}\t{r['out_in'] / fps:.2f}\t{(r['out_in'] + r['n']) / fps:.2f}\t"
                f"#{r['clip']}\t{r['src_in'] / fps:.2f}\t{(r['src_in'] + r['n']) / fps:.2f}\t{r['label']}\n"
            )
    print("wrote", out_dir / "Intro_NYC.edl")


if __name__ == "__main__":
    main()
