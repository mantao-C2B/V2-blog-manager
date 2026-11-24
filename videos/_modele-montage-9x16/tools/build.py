"""Build the HyperFrames composition and the soundtracks from edit.json.

  python3 tools/build.py            (run from the project root)

Writes:
  index.html               the composition (npx hyperframes render); with --sans-musique it plays the
                           voice + outro sound effects only
  assets/music.wav         light music bed (tools/songs.py, style "light")
  assets/soundtrack.wav, assets/soundtrack-voix.wav   premixed audio, -14 LUFS / -1 dBTP
The caption look is a composition variable: captionStyle = ligne | surlignage | karaoke.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
SONGS = ROOT / "tools" / "songs.py"
PROJECT = json.load(open(ROOT / "project.json"))
SR = 48000


def timeline(edit):
    """Place the clips end to end; return clips with output start and the edit's total length."""
    t, clips = 0.0, []
    for i, s in enumerate(edit["segments"]):
        d = round(s["out"] - s["in"], 3)
        clips.append(dict(s, id=f"c{i}", start=round(t, 3), dur=d))
        t += d
    return clips, round(t, 3)


def to_out(clips, src_t):
    for c in clips:
        if c["in"] - 1e-3 <= src_t <= c["out"] + 1e-3:
            return round(c["start"] + src_t - c["in"], 3)
    return None


def captions_out(edit, clips, end):
    out = []
    for g in edit["captions"]:
        s, e = to_out(clips, g["start"]), to_out(clips, min(g["end"], clips[-1]["out"]))
        if s is None or e is None or e - s < 0.08:
            continue
        words = []
        for w in g["words"]:
            wt = to_out(clips, w["t"])
            words.append({"w": w["w"], "t": s if wt is None else max(s, wt), "hl": bool(w["hl"])})
        out.append({"start": s, "end": min(e, end), "words": words})
    return out


FONTS = """
@font-face { font-family: "Instrument Sans"; font-style: normal; font-weight: 400 700; src: url("assets/fonts/InstrumentSans-normal-400-700-latin-ext.woff2") format("woff2"); unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF; }
@font-face { font-family: "Instrument Sans"; font-style: normal; font-weight: 400 700; src: url("assets/fonts/InstrumentSans-normal-400-700-latin.woff2") format("woff2"); unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
"""


def write_html(edit, clips, end, total, soundtrack, path):
    W, H = edit["canvas"]["w"], edit["canvas"]["h"]
    st = edit["style"]
    shots = []
    for c in clips:
        shots.append(
            f'      <div class="shot" id="w-{c["id"]}" data-layout-allow-overflow><div class="inner" id="i-{c["id"]}" data-layout-allow-overflow>'
            f'<video id="{c["id"]}" class="clip" src="assets/footage.mp4" data-start="{c["start"]}" data-duration="{c["dur"]}" '
            f'data-media-start="{c["in"]}" data-track-index="0" muted playsinline></video></div></div>'
        )
    caps = captions_out(edit, clips, end)
    cap_html = []
    for i, g in enumerate(caps):
        words = " ".join(
            f'<span class="w{" hl" if w["hl"] else ""}" data-t="{w["t"]}"><span class="bx"></span><span class="tx">{w["w"]}</span></span>'
            for w in g["words"]
        )
        cap_html.append(
            f'      <div class="cap clip" id="cap{i}" data-start="{g["start"]}" data-duration="{round(g["end"] - g["start"], 3)}" '
            f'data-track-index="2"><div class="cap-fit"><div class="cap-line">{words}</div></div></div>'
        )
    outro = ""
    if edit["outro"]["enabled"]:
        outro = (f'      <video id="outro" class="clip" src="assets/outro.mp4" data-start="{end}" '
                 f'data-duration="{edit["outro"]["duration"]}" data-track-index="1" muted playsinline></video>')
    variables = json.dumps([{"id": "captionStyle", "type": "enum", "label": "Style des sous-titres", "default": st["captions"],
                             "options": [{"value": "ligne", "label": "Ligne blanche, mots clés en vert"},
                                         {"value": "surlignage", "label": "Mots clés surlignés en vert"},
                                         {"value": "karaoke", "label": "Mot prononcé surligné"}]}], ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="fr" data-composition-variables='{variables}'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{PROJECT["title"]}</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
{FONTS}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #0e1a17; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #0e1a17; font-family: "Instrument Sans", sans-serif; }}
      .shot {{ position: absolute; inset: 0; overflow: hidden; }}
      .shot .inner {{ position: absolute; inset: 0; }}
      .shot video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      #outro {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      #whiteout {{ position: absolute; inset: 0; background: #ffffff; opacity: 0; }}
      /* Captions: one line, Instrument Sans (brand text face), white; key words in brand green. */
      .cap {{ position: absolute; left: 0; right: 0; top: {round(st["y"] * H)}px; height: 0; }}
      .cap-fit {{ position: absolute; left: 0; right: 0; top: 0; display: flex; justify-content: center; }}
      .cap-line {{ display: flex; gap: 0 0.1em; align-items: center; transform-origin: 50% 50%; white-space: nowrap;
                  font-weight: 700; font-size: {st["size"]}px; line-height: 1; letter-spacing: -0.005em; color: #ffffff; margin-top: -0.6em; }}
      .w {{ position: relative; display: inline-block; padding: 0.08em 0.1em 0.12em; }}
      .w .tx {{ position: relative; -webkit-text-stroke: 0.09em rgba(14, 26, 23, 0.62); paint-order: stroke fill;
                text-shadow: 0 0.04em 0.12em rgba(14, 26, 23, 0.5), 0 0 0.5em rgba(14, 26, 23, 0.35); }}
      .w .bx {{ position: absolute; inset: 0; border-radius: 0.18em; background: {st["box"]}; opacity: 0; transform-origin: 0% 50%; }}
      .s-ligne .w.hl .tx, .s-karaoke .w.hl .tx {{ color: {st["green"]}; }}
      .s-surlignage .w.hl .tx {{ -webkit-text-stroke: 0; text-shadow: none; }}
      .s-karaoke .w .tx {{ -webkit-text-stroke-color: rgba(14, 26, 23, 0.62); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}" data-fps="{edit["canvas"]["fps"]}">
{chr(10).join(shots)}
{chr(10).join(cap_html)}
      <div id="whiteout"></div>
{outro}
      <audio id="soundtrack" src="assets/{soundtrack}" data-start="0" data-duration="{total}" data-track-index="3" data-volume="1"></audio>
    </div>
    <script>
      (function () {{
        const E = {json.dumps({"clips": [{k: c[k] for k in ("id", "start", "dur", "zoom", "push", "fx", "fy")} for c in clips], "end": end, "fadeWhite": 0.3}, separators=(",", ":"))};
        const vars = (window.__hyperframes && window.__hyperframes.getVariables) ? window.__hyperframes.getVariables() : {{}};
        const style = vars.captionStyle || "{st["captions"]}";
        const root = document.getElementById("root");
        root.classList.add("s-" + style);
        const tl = gsap.timeline({{ paused: true }});

        // Light zooms: each clip holds its framing and pushes in slowly.
        E.clips.forEach(function (c) {{
          const inner = document.getElementById("i-" + c.id);
          gsap.set(inner, {{ transformOrigin: c.fx + "% " + c.fy + "%" }});
          tl.fromTo(inner, {{ scale: c.zoom }}, {{ scale: c.zoom * (1 + c.push), duration: c.dur, ease: "none" }}, c.start);
        }});

        // Captions: fit on one line, soft entrance, style-specific word treatment.
        document.querySelectorAll(".cap").forEach(function (cap) {{
          const line = cap.querySelector(".cap-line");
          const max = {W} - 2 * 70;
          const w = line.scrollWidth;
          if (w > max) cap.querySelector(".cap-fit").style.transform = "scale(" + (max / w).toFixed(3) + ")";
          const t0 = parseFloat(cap.getAttribute("data-start"));
          const t1 = t0 + parseFloat(cap.getAttribute("data-duration"));
          tl.fromTo(line, {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.14, ease: "power2.out" }}, t0);
          const words = Array.from(cap.querySelectorAll(".w"));
          words.forEach(function (wd, i) {{
            const t = parseFloat(wd.getAttribute("data-t"));
            const bx = wd.querySelector(".bx");
            if (style === "surlignage" && wd.classList.contains("hl")) {{
              tl.fromTo(bx, {{ opacity: 1, scaleX: 0 }}, {{ opacity: 1, scaleX: 1, duration: 0.18, ease: "power3.out" }}, Math.max(t0, t));
            }} else if (style === "karaoke") {{
              const next = i + 1 < words.length ? parseFloat(words[i + 1].getAttribute("data-t")) : t1;
              tl.fromTo(bx, {{ opacity: 0, scale: 0.86 }}, {{ opacity: 1, scale: 1, duration: 0.08, ease: "power2.out" }}, Math.max(t0, t));
              tl.to(bx, {{ opacity: 0, duration: 0.05, ease: "none" }}, Math.max(t0, next) - 0.02);
              if (wd.classList.contains("hl")) {{  // green word turns white while it sits on the green box
                const tx = wd.querySelector(".tx");
                tl.set(tx, {{ color: "#ffffff" }}, Math.max(t0, t));
                tl.set(tx, {{ color: "{st["green"]}" }}, Math.max(t0, next) - 0.02);
              }}
            }}
          }});
        }});

        // Into the outro: a short fade to white (the outro opens on white).
        tl.fromTo("#whiteout", {{ opacity: 0 }}, {{ opacity: 1, duration: E.fadeWhite, ease: "power1.in" }}, E.end - E.fadeWhite);
        tl.set({{}}, {{}}, {total});
        window.__timelines["main"] = tl;
      }})();
    </script>
  </body>
</html>
"""
    path.write_text(html)


def load(path):
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    assert sr == SR, (path, sr)
    return np.repeat(x, 2, axis=1) if x.shape[1] == 1 else x


def loudnorm(src, dst, I=-14, TP=-1.0):
    f = f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af", f, "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    f2 = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample={SR}")
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(src), "-af", f2, "-c:a", "pcm_s24le", str(dst)], check=True)


def audio(edit, clips, end, total):
    a = ROOT / "assets"
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(a / "footage.mp4"), "-vn", "-ac", "2", "-ar", str(SR),
                    str(a / "_voice_src.wav")], check=True)
    src = load(a / "_voice_src.wav")
    n = int(round(total * SR))
    voice = np.zeros((n, 2), np.float32)
    for c in clips:
        seg = src[int(c["in"] * SR):int(c["out"] * SR)].copy()
        k = int(0.008 * SR)
        seg[:k] *= np.linspace(0, 1, k)[:, None]
        seg[-k:] *= np.linspace(1, 0, k)[:, None]
        i0 = int(round(c["start"] * SR))
        voice[i0:i0 + len(seg)] += seg[: n - i0]
    tail = int(0.12 * SR)
    i_end = int(end * SR)
    voice[i_end - tail:i_end] *= np.linspace(1, 0, tail)[:, None]
    sfx = np.zeros((n, 2), np.float32)
    if edit["outro"]["enabled"]:
        # the outro's sound effects ride on its own audio track
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(a / "outro.mp4"), "-vn", "-ac", "2", "-ar", str(SR),
                        str(a / "_outro_sfx.wav")], check=True)
        x = load(a / "_outro_sfx.wav")
        sfx[i_end:i_end + len(x)] += x[: n - i_end]
    # music bed: light, under the voice, gone by 1.4 s into the outro
    spec = {"style": "light", "duration": round(end + 1.4, 3), "sections": [[0.0, round(end + 1.4, 3), 1]],
            "impacts": [], "risers": [], "stops": [], "fills": [], "fade_out": 1.6}
    json.dump(spec, open(a / "music_spec.json", "w"))
    subprocess.run([sys.executable, str(SONGS), str(a / "music_spec.json"), str(a / "music.wav")], check=True, cwd=SONGS.parent)
    m = load(a / "music.wav")[:n]
    music = np.zeros((n, 2), np.float32)
    music[: len(m)] = m * edit["music"]["volume"]
    fi = int(0.6 * SR)
    music[:fi] *= np.linspace(0, 1, fi)[:, None]
    for name, mix in (("soundtrack.wav", voice + music + sfx), ("soundtrack-voix.wav", voice + sfx)):
        sf.write(a / "_premix.wav", mix, SR, subtype="FLOAT")
        loudnorm(a / "_premix.wav", a / name)
    for f in ("_premix.wav", "_voice_src.wav", "_outro_sfx.wav"):
        (a / f).unlink()


def main():
    edit = json.load(open(ROOT / "edit.json"))
    clips, end = timeline(edit)
    total = round(end + (edit["outro"]["duration"] if edit["outro"]["enabled"] else 0.0), 3)
    soundtrack = "soundtrack-voix.wav" if "--sans-musique" in sys.argv or not edit["music"]["enabled"] else "soundtrack.wav"
    write_html(edit, clips, end, total, soundtrack, ROOT / "index.html")
    print(f"{len(clips)} clips, {len(edit['captions'])} caption lines, {end:.2f}s + outro = {total:.2f}s")
    if "--no-audio" not in sys.argv:
        audio(edit, clips, end, total)
        print("soundtracks written")


if __name__ == "__main__":
    main()
