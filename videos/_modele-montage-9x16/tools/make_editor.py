"""Assemble the web editor: editor/index.html (edit.json embedded as the original edit) + editor/media/.

  python3 tools/make_editor.py      (run from the project root, after tools/build.py)
editor/media/footage.mp4 is the light 1080x1920 copy made by tools/prepare.sh (assets/web.mp4, cleaned
voice, under the 15 MB file limit of an artifact); the editor plays it, and exports from it or from the
original 4K file the viewer picks on their own computer. Publish editor/index.html as an artifact with
the three files of editor/media/ (see README.md).
"""

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ED = ROOT / "editor"
MEDIA = ED / "media"


def main():
    edit = json.load(open(ROOT / "edit.json"))
    proj = json.load(open(ROOT / "project.json"))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(ROOT / "assets" / "web.mp4")], capture_output=True, text=True, check=True).stdout)
    config = {"title": proj["title"], "subtitle": proj["subtitle"], "slug": proj["slug"], "keywords": proj["keywords"],
              "sourceDuration": round(dur, 3)}
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = (ED / "editor.template.html").read_text()
    html = (html.replace("__EDIT_JSON__", js(edit)).replace("__CONFIG_JSON__", js(config))
                .replace("__TITLE__", esc(proj["title"])).replace("__SUBTITLE__", esc(proj["subtitle"])))
    (ED / "index.html").write_text(html)
    MEDIA.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "assets" / "web.mp4", MEDIA / "footage.mp4")
    shutil.copyfile(ROOT / "assets" / "outro.mp4", MEDIA / "outro.mp4")
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(ROOT / "assets" / "music.wav"),
                    "-c:a", "libmp3lame", "-b:a", "192k", str(MEDIA / "music.mp3")], check=True)
    for f in sorted(MEDIA.iterdir()):
        print(f"{f.name}: {f.stat().st_size / 1e6:.1f} MB")
    print("editor/index.html written")


if __name__ == "__main__":
    main()
