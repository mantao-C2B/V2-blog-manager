"""Build one version of the LLM Monitor @ SEO & GEO Summit edit.

  python3 tools/build.py v1|v2|v3 [--no-audio]

Reads the version's edit decision list (tools/versions.py), then writes into the version project:
  index.html            the HyperFrames composition (static <video> clips + window.EDL + engine)
  STORYBOARD.md         the shot list (dispatch artifact / readable plan)
  assets/music.wav      the music bed (tools/songs.py)
  assets/soundtrack.wav speech + room tone + music (ducked) + SFX, -14 LUFS / -1 dBTP
All source times refer to the raw rushes (= assets/footage.mp4, same timeline).
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SR = 48000
FPS = 30

sys.path.insert(0, str(TOOLS))
import versions  # noqa: E402

from transcript import HIGHLIGHT, WORDS, words_in  # noqa: E402


# ----------------------------------------------------------------------------- timeline
def place(shots):
    t = 0.0
    for i, s in enumerate(shots):
        s.setdefault("id", f"s{i:02d}")
        s["start"] = round(t, 4)
        s["dur"] = round(s["out"] - s["src"], 4)
        t += s["dur"]
    return t


def frame(t):
    return round(round(t * FPS) / FPS, 4)


def captions_for(shots, overrides, max_chars, max_words):
    groups = []
    n_before = 0
    for s in shots:
        if s.get("kind") not in ("talk", "bite") or s.get("nocap"):
            continue
        a0 = s.get("asrc", s["src"])
        a1 = a0 + s["dur"]
        ws = [w for w in words_in(a0, a1) if w["s"] < a1 - 0.06]
        cur = []
        for w in ws:
            txt = overrides.get(round(w["s"], 2), w["w"])
            if txt == "":
                continue
            t_out = s["start"] + (w["s"] - a0)
            e_out = s["start"] + (min(w["e"], a1) - a0)
            clean = txt.strip()
            for p in (".", ","):
                clean = clean.rstrip(p)
            hl = clean.lower().strip("?!.,'’") in HIGHLIGHT or any(k in clean.lower() for k in ("chatgpt", "llm", "seo", "geo")) or any(ch.isdigit() for ch in clean)
            item = {"w": clean, "t": round(max(t_out, s["start"]), 3), "e": round(e_out, 3), "hl": hl, "end_punct": txt.strip()[-1:] in ".?!,"}
            text_len = sum(len(x["w"]) + 1 for x in cur) + len(clean)
            gap = (item["t"] - cur[-1]["e"]) if cur else 0
            if cur and (len(cur) >= max_words or text_len > max_chars or gap > 0.45 or cur[-1]["end_punct"]):
                groups.append(cur)
                cur = []
            cur.append(item)
        if cur:
            groups.append(cur)
        for g in groups[n_before:]:
            g[-1]["shot_end"] = s["start"] + s["dur"]
        n_before = len(groups)
    out = []
    for g in groups:
        start = g[0]["t"]
        end = min(g[-1]["e"] + 0.25, g[-1].get("shot_end", 1e9))
        out.append({"start": start, "end": end, "words": [{"w": x["w"], "t": x["t"], "hl": x["hl"]} for x in g]})
    # no overlaps, small gaps closed
    for a, b in zip(out, out[1:]):
        if a["end"] > b["start"] - 0.02 or b["start"] - a["end"] < 0.3:
            a["end"] = round(b["start"] - 0.02, 3)
    for g in out:
        g["start"] = round(g["start"], 3)
        g["end"] = round(g["end"], 3)
    return [g for g in out if g["end"] - g["start"] > 0.08]


# ----------------------------------------------------------------------------- html
FONTS = [
    ("IBM Plex Mono", "normal", "400", "IBMPlexMono-normal-400"),
    ("IBM Plex Mono", "normal", "500", "IBMPlexMono-normal-500"),
    ("IBM Plex Mono", "normal", "600", "IBMPlexMono-normal-600"),
    ("Instrument Sans", "normal", "400 700", "InstrumentSans-normal-400-700"),
    ("Instrument Serif", "italic", "400", "InstrumentSerif-italic-400"),
    ("Instrument Serif", "normal", "400", "InstrumentSerif-normal-400"),
    ("Sora", "normal", "300 700", "Sora-normal-300-700"),
]
LATIN = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
LATIN_EXT = "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF"


def font_faces():
    css = []
    for fam, style, weight, stem in FONTS:
        for sub, rng in (("latin-ext", LATIN_EXT), ("latin", LATIN)):
            css.append(
                f'@font-face {{ font-family: "{fam}"; font-style: {style}; font-weight: {weight}; '
                f'src: url("assets/fonts/{stem}-{sub}.woff2") format("woff2"); unicode-range: {rng}; }}'
            )
    return "\n".join(css)


def write_html(v, shots, edl, duration):
    W, H = v["W"], v["H"]
    css_vars = ";".join(f"{k}:{val}" for k, val in v["css"].items())
    clips = []
    for i, s in enumerate(shots):
        pos = f'{s["focal"][0]}% {s["focal"][1]}%'
        clips.append(
            f'      <div class="shot" id="w-{s["id"]}" data-layout-allow-overflow><div class="inner" id="i-{s["id"]}" data-layout-allow-overflow>'
            f'<video id="{s["id"]}" class="clip" src="assets/footage.mp4" data-start="{s["start"]}" '
            f'data-duration="{s["dur"]}" data-media-start="{s["src"]}" data-track-index="0" '
            f'muted playsinline style="object-position:{pos}"></video></div></div>'
        )
    html = f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{v["title"]}</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
{font_faces()}
{(TOOLS / "edit.css").read_text()}
      html, body {{ width: {W}px; height: {H}px; }}
      #root {{ {css_vars} }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="{edl["id"]}" data-start="0" data-duration="{duration}" data-width="{W}" data-height="{H}" data-fps="{FPS}">
{chr(10).join(clips)}
      <div id="overlays"></div>
      <div id="captions"></div>
      <audio id="soundtrack" src="assets/soundtrack.wav" data-start="0" data-duration="{duration}" data-track-index="2" data-volume="1"></audio>
    </div>
    <script src="assets/kit.js"></script>
    <script src="assets/engine.js"></script>
    <script>
      window.EDL = {json.dumps(edl, ensure_ascii=False, separators=(",", ":"))};
      window.__timelines["{edl["id"]}"] = window.buildEdit(window.EDL);
    </script>
  </body>
</html>
"""
    (v["dir"] / "index.html").write_text(html)


def write_storyboard(v, shots, duration):
    lines = [
        "---",
        f"format: {v['W']}x{v['H']}",
        f"duration: {duration:.1f}s",
        f"message: \"{v['message']}\"",
        f"arc: {v['arc']}",
        "audience: \"Réseau LinkedIn de LLM Monitor et Market Connect\"",
        "mode: autonomous",
        "---",
        "",
        f"# {v['title']}",
        "",
        "Plan généré par `tools/build.py` depuis `tools/versions.py` (source de vérité des coupes).",
        "Temps source = timecode des rushes bruts (`_source/raw.mp4`).",
        "",
    ]
    for i, sec in enumerate(v["sections"]):
        lines += [
            f"## Frame {i + 1} — {sec['title']}",
            "",
            "- status: animated",
            "- src: index.html",
            f"- duration: {sec['t1'] - sec['t0']:.1f}s",
            f"- poster: {(sec['t0'] + sec['t1']) / 2:.1f}",
            f"- scene: {sec['scene']}",
            f"- motion: {sec.get('motion', '')}",
            "",
        ]
        for s in shots:
            if sec["t0"] - 1e-3 <= s["start"] < sec["t1"] - 1e-3:
                a0 = s.get("asrc", s["src"])
                ws = " ".join(w["w"] for w in words_in(a0, a0 + s["dur"])) if s.get("kind") in ("talk", "bite") else ""
                lines.append(
                    f"  - `{s['start']:6.2f}s` {s['dur']:4.2f}s · source {s['src']:.2f}→{s['out']:.2f} · {s.get('kind', 'broll')}"
                    + (f" · « {ws} »" if ws else "")
                )
        lines.append("")
    (v["dir"] / "STORYBOARD.md").write_text("\n".join(lines))


# ----------------------------------------------------------------------------- audio
def load_audio(path):
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    assert sr == SR, sr
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def fade(x, fin, fout):
    n = len(x)
    e = np.ones(n)
    a = min(n, int(fin * SR))
    b = min(n, int(fout * SR))
    if a:
        e[:a] = np.linspace(0, 1, a) ** 1.5
    if b:
        e[n - b:] = np.minimum(e[n - b:], np.linspace(1, 0, b) ** 1.5)
    return x * e[:, None]


def mix(v, shots, duration, sfx_list, music_path):
    speech_src = load_audio(ROOT / "assets_shared" / "speech.wav")
    n = int(math.ceil(duration * SR))
    speech = np.zeros((n, 2), np.float32)
    room = np.zeros((n, 2), np.float32)
    target = -20.0  # speech RMS target (dBFS) before final loudness normalisation
    for s in shots:
        kind = s.get("kind", "broll")
        a0 = s.get("asrc", s["src"])
        i_src0 = int(a0 * SR)
        i_src1 = int((a0 + s["dur"]) * SR)
        seg = speech_src[i_src0:i_src1].copy()
        i0 = int(round(s["start"] * SR))
        i1 = min(n, i0 + len(seg))
        seg = seg[: i1 - i0]
        if not len(seg):
            continue
        if kind in ("talk", "bite"):
            ws = words_in(a0, a0 + s["dur"])
            if ws:
                a = int((ws[0]["s"] - a0) * SR)
                b = int((ws[-1]["e"] - a0) * SR)
                ref = seg[max(0, a):max(a + 1, b)]
            else:
                ref = seg
            g = 10 ** ((target + s.get("gain_db", 0) - rms_db(ref)) / 20)
            g = min(g, 10 ** (18 / 20))
            speech[i0:i1] += fade(seg * g, 0.012, 0.02)
        else:
            amb = v.get("ambience", 0.0) * s.get("amb", 1.0)
            if amb > 0:
                g = 10 ** ((target - 14 - rms_db(seg)) / 20) * amb
                room[i0:i1] += fade(seg * g, 0.06, 0.08)
    # music with ducking under speech
    music = load_audio(music_path)[:n]
    if len(music) < n:
        music = np.vstack([music, np.zeros((n - len(music), 2), np.float32)])
    env = np.full(n, v["music_level"], np.float32)
    talk_iv = []
    for s in shots:
        if s.get("kind") in ("talk", "bite"):
            a, b = s["start"], s["start"] + s["dur"]
            if talk_iv and a - talk_iv[-1][1] < 0.7:
                talk_iv[-1][1] = b
            else:
                talk_iv.append([a, b])
    duck = v["music_duck"]
    for a, b in talk_iv:
        ia, ib = int((a - 0.12) * SR), int((b + 0.05) * SR)
        env[max(0, ia):min(n, ib)] = duck
    for (t0, t1, lvl) in v.get("music_overrides", []):
        env[int(t0 * SR):int(t1 * SR)] = lvl
    # smooth the envelope (≈ 250 ms ramps)
    k = int(0.25 * SR)
    cs = np.cumsum(np.concatenate([np.full(k, env[0]), env]).astype(np.float64))
    env = ((cs[k:] - cs[:-k]) / k).astype(np.float32)
    music = music * env[:, None]
    # SFX
    sfx = np.zeros((n, 2), np.float32)
    for (t, name, vol) in sfx_list:
        x = load_audio(ROOT / "assets_shared" / "sfx" / f"{name}.wav")
        i0 = int(round(t * SR))
        if i0 >= n:
            continue
        i1 = min(n, i0 + len(x))
        sfx[i0:i1] += x[: i1 - i0] * vol
    full = speech + room + music + sfx
    # fade out the very end
    tail = int(0.6 * SR)
    full[-tail:] *= np.linspace(1, 0, tail)[:, None]
    tmp = v["dir"] / "assets" / "_premix.wav"
    sf.write(tmp, full.astype(np.float32), SR, subtype="FLOAT")
    out = v["dir"] / "assets" / "soundtrack.wav"
    loudnorm(tmp, out)
    tmp.unlink()


def loudnorm(src, dst, I=-14, TP=-1.0):
    f = f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af", f, "-f", "null", "-"],
                       capture_output=True, text=True)
    js = r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1]
    m = json.loads(js)
    f2 = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
          f"aresample={SR}")
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(src), "-af", f2, "-c:a", "pcm_s24le", str(dst)], check=True)


# ----------------------------------------------------------------------------- main
def main():
    key = sys.argv[1]
    v = versions.VERSIONS[key]()
    v["dir"] = ROOT / v["folder"]
    shots = v["shots"]
    duration = place(shots)
    for s in shots:
        s.setdefault("focal", [50, 50])
        s.setdefault("zoom", 1.0)
    # overlays/sfx/music may be expressed relative to shot ids: resolve now
    ctx = versions.Ctx(shots)
    overlays, sfx_list, flashes, dips = v["post"](ctx)
    duration = round(duration + v.get("tail", 0.0), 3)
    caps = captions_for(shots, v.get("cap_overrides", {}), v["cap_chars"], v["cap_words"])
    last_end = shots[-1]["start"] + shots[-1]["dur"]
    caps = [dict(g, end=min(g["end"], last_end)) for g in caps if g["start"] < last_end - 0.1]
    edl = {
        "id": "main", "W": v["W"], "H": v["H"], "duration": duration,
        "shots": [{k: s[k] for k in ("id", "start", "dur", "focal", "zoom") } | {k: s[k] for k in ("move", "tin", "tout") if k in s} for s in shots],
        "overlays": overlays, "captions": caps, "flashes": flashes, "dips": dips,
    }
    write_html(v, shots, edl, duration)
    (v["dir"] / "assets" / "engine.js").write_text((TOOLS / "engine.js").read_text())
    v["sections"] = ctx.sections(duration)
    write_storyboard(v, shots, duration)
    print(f"{key}: {len(shots)} shots, {len(caps)} caption groups, {len(overlays)} overlays, {duration:.2f}s")
    if "--no-audio" in sys.argv:
        return
    spec = v["music"](ctx, duration)
    spec_path = v["dir"] / "assets" / "music_spec.json"
    music_path = v["dir"] / "assets" / "music.wav"
    unchanged = spec_path.exists() and music_path.exists() and json.load(open(spec_path)) == json.loads(json.dumps(spec))
    json.dump(spec, open(spec_path, "w"), indent=1)
    if not unchanged:
        subprocess.run([sys.executable, str(TOOLS / "songs.py"), str(spec_path), str(music_path)], check=True, cwd=TOOLS)
    mix(v, shots, duration, sfx_list, music_path)
    print("soundtrack written")


if __name__ == "__main__":
    main()
