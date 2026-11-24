"""Assemble the web editor: editor/index.html (edit.json embedded as the original edit) + editor/media/.

  python3 tools/make_editor.py      (run from the project root, after tools/build.py)
editor/media/footage.mp4 is the light 1080x1920 copy (web_1080.mp4, cleaned voice); the editor plays it,
and exports from it or from the original 4K file the viewer picks on their own computer.
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
    blob = json.dumps(edit, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    html = (ED / "editor.template.html").read_text().replace("__EDIT_JSON__", blob)
    (ED / "index.html").write_text(html)
    MEDIA.mkdir(exist_ok=True)
    shutil.copyfile(ROOT.parent / "_source2" / "web_1080.mp4", MEDIA / "footage.mp4")
    shutil.copyfile(ROOT / "assets" / "outro.mp4", MEDIA / "outro.mp4")
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(ROOT / "assets" / "music.wav"),
                    "-c:a", "libmp3lame", "-b:a", "192k", str(MEDIA / "music.mp3")], check=True)
    for f in sorted(MEDIA.iterdir()):
        print(f"{f.name}: {f.stat().st_size / 1e6:.1f} MB")
    print("editor/index.html written")


if __name__ == "__main__":
    main()
