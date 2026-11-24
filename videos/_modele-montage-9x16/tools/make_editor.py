"""Assemble the web editor: editor/index.html (edit.json embedded as the original edit) + editor/media/.

  python3 tools/make_editor.py      (run from the project root, after tools/build.py)
editor/media/footage.mp4 is the light 1080x1920 copy made by tools/prepare.sh (assets/web.mp4, cleaned
voice, under the 15 MB file limit of an artifact); the editor plays it, and exports from it or from the
original 4K file the viewer picks on their own computer. Publish editor/index.html as an artifact with
the files of editor/media/ (see README.md). Fonts, palette, logo, labels and the outro come from the
project's brand (project.json "brand", tools/brands.json); a brand without music has no music.mp3.
"""

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ED = ROOT / "editor"
MEDIA = ED / "media"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def palette_css(b):
    ui = b["ui"]
    var = lambda d: " ".join(f"--{k}: {v};" for k, v in d.items())
    fonts = (f'--font-ui: {ui["font_ui"]}; --font-title: {ui["font_title"]}; '
             f'--font-data: "IBM Plex Mono", ui-monospace, Menlo, monospace; --title-spacing: {ui["title_spacing"]}; --r: 12px;')
    return (f'/* Layout: editing desk — vertical preview on the left, the edit\'s controls on the right, timeline under both.\n'
            f'   {ui["comment"]} */\n'
            f':root {{ {var(ui["light"])} {fonts} }}\n'
            f'@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ {var(ui["dark"])} color-scheme: dark; }} }}\n'
            f':root[data-theme="dark"] {{ {var(ui["dark"])} color-scheme: dark; }}')


def demo_css(b):
    stroke = lambda a: f" -webkit-text-stroke: 0.6px rgba(14,26,23,{a});" if b["outline"] else ""
    return (f'.style-card .demo {{ font-family: "{b["caption_font"]["family"]}", sans-serif; }}\n'
            f'.demo .k {{ color: {b["text_color"]};{stroke(".6")} }}\n'
            f'.demo .b {{ background: {b["box_color"]}; border-radius: 4px; padding: 1px 4px; }}\n'
            f'.demo span {{{stroke(".5")} }}')


def options(pairs):
    return "".join(f'<option value="{v}">{esc(label)}</option>' for v, label in pairs)


def main():
    edit = json.load(open(ROOT / "edit.json"))
    proj = json.load(open(ROOT / "project.json"))
    brand = json.load(open(ROOT / "tools" / "brands.json"))[proj.get("brand", "llm-monitor")]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(ROOT / "assets" / "web.mp4")], capture_output=True, text=True, check=True).stdout)
    config = {"title": proj["title"], "subtitle": proj["subtitle"], "slug": proj["slug"], "keywords": proj["keywords"],
              "sourceDuration": round(dur, 3)}
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    # BRAND is read by the page script (canvas font, outline, music, wording)
    brand_js = {"name": brand["name"], "font": brand["caption_font"]["family"], "weight": brand["caption_font"]["weight"],
                "outline": brand["outline"], "music": brand["music"], "hlWord": brand["hl_word"]}
    sub = {
        "__UI_FONTS_LINK__": brand["ui"]["fonts_link"],
        "__PALETTE_CSS__": palette_css(brand),
        "__DEMO_CSS__": demo_css(brand),
        "__LOGO_SVG__": brand["ui"]["logo_svg"],
        "__HL_WORD__": esc(brand["hl_word"]),
        "__STYLE_HINT__": esc(brand["style_hint"]),
        "__CARD_LIGNE__": esc(brand["styles"]["ligne"][1]),
        "__CARD_SURLIGNAGE__": esc(brand["styles"]["surlignage"][1]),
        "__CARD_KARAOKE__": esc(brand["styles"]["karaoke"][1]),
        "__BOX_COLOR_LABEL__": esc(brand["box_color_label"]),
        "__BOX_COLOR_OPTIONS__": options(brand["box_colors"]),
        "__TEXT_COLOR_LABEL__": esc(brand["text_color_label"]),
        "__TEXT_COLOR_OPTIONS__": options(brand["text_colors"]),
        "__SOUND_TAB__": "Musique et outro" if brand["music"] else "Outro",
        "__MUSIC_HIDDEN__": "" if brand["music"] else " hidden",
        "__OUTRO_LABEL__": esc(brand["outro_label"]),
        "__EDIT_JSON__": js(edit),
        "__CONFIG_JSON__": js(config),
        "__BRAND_JSON__": js(brand_js),
        "__TITLE__": esc(proj["title"]),
        "__SUBTITLE__": esc(proj["subtitle"]),
    }
    html = (ED / "editor.template.html").read_text()
    for k, v in sub.items():
        html = html.replace(k, v)
    left = [k for k in sub if k in html]
    assert not left, left
    (ED / "index.html").write_text(html)
    MEDIA.mkdir(exist_ok=True)
    for f in MEDIA.iterdir():
        f.unlink()
    shutil.copyfile(ROOT / "assets" / "web.mp4", MEDIA / "footage.mp4")
    shutil.copyfile(ROOT / brand["outro"], MEDIA / "outro.mp4")
    if brand["music"]:
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(ROOT / "assets" / "music.wav"),
                        "-c:a", "libmp3lame", "-b:a", "192k", str(MEDIA / "music.mp3")], check=True)
    for f in sorted(MEDIA.iterdir()):
        print(f"{f.name}: {f.stat().st_size / 1e6:.1f} MB")
    print("editor/index.html written")


if __name__ == "__main__":
    main()
