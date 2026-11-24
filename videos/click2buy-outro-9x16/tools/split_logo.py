"""Split the supplied Click2Buy logo (assets/logo-source.png, 2000x1125 RGBA) into animatable layers.

Each connected shape becomes a cropped transparent PNG in assets/logo/, and assets/logo/layers.json lists
them with their position in the source image, so index.html places them exactly where they sit in the logo.

Groups (by colour and place):
  click  orange letters left of the pin (C L I C K)
  pin    red location pin (ring + tip)
  two    orange "2" inside the pin
  buy    red letters right of the pin (B U Y)
  tag    red "By MarketConnect" under BUY

  python3 -I tools/split_logo.py        (run from the project root)
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(sys.argv[0]).resolve().parent.parent
SRC = ROOT / "assets" / "logo-source.png"
OUT = ROOT / "assets" / "logo"

im = np.array(Image.open(SRC).convert("RGBA"))
alpha = im[:, :, 3].astype(int)
mask = alpha > 8
labels, n = ndimage.label(mask, structure=np.ones((3, 3)))
objs = ndimage.find_objects(labels)

layers = []
for i, sl in enumerate(objs, start=1):
    ys, xs = sl
    comp = labels[sl] == i
    area = int(comp.sum())
    if area < 40:  # specks of anti-aliasing
        continue
    px = im[sl][comp & (alpha[sl] > 200)][:, :3].astype(int)
    orange = px.size and np.median(px[:, 1]) > 117
    x0, x1, y0, y1 = xs.start, xs.stop, ys.start, ys.stop
    cx = (x0 + x1) / 2
    if orange:
        group = "click" if cx < 912 else "two"
    elif y0 > 660:
        group = "tag"
    elif x1 - x0 > 250 and cx < 1240:
        group = "pin"
    else:
        group = "buy"
    layers.append({"group": group, "x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0), "label": i, "area": area})

OUT.mkdir(parents=True, exist_ok=True)
for f in OUT.glob("*.png"):
    f.unlink()
counts = {}
for L in sorted(layers, key=lambda L: (L["group"], L["x"])):
    k = counts.get(L["group"], 0)
    counts[L["group"]] = k + 1
    L["id"] = f"{L['group']}-{k}"
    pad = 2
    y0, y1 = max(0, L["y"] - pad), min(im.shape[0], L["y"] + L["h"] + pad)
    x0, x1 = max(0, L["x"] - pad), min(im.shape[1], L["x"] + L["w"] + pad)
    keep = labels[y0:y1, x0:x1] == L["label"]
    # keep the soft anti-aliased fringe that touches the shape (alpha <= 8 pixels next to it)
    keep = ndimage.binary_dilation(keep, iterations=2) & (alpha[y0:y1, x0:x1] > 0) | keep
    crop = im[y0:y1, x0:x1].copy()
    crop[~keep] = 0
    Image.fromarray(crop).save(OUT / f"{L['id']}.png", optimize=True)
    L.update({"x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0), "src": f"assets/logo/{L['id']}.png"})
    del L["label"]

layers.sort(key=lambda L: (L["group"], L["x"]))
json.dump({"source": [im.shape[1], im.shape[0]], "layers": layers}, open(OUT / "layers.json", "w"), indent=1)
print(counts)
for L in layers:
    print(f"  {L['id']:8s} x {L['x']:4d} y {L['y']:4d}  {L['w']:4d}x{L['h']:<4d} area {L['area']}")
