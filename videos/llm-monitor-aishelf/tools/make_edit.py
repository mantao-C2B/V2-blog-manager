"""Write the first edit.json from the transcript: cut points, framings and one-line captions.

edit.json is the single description of the edit. tools/build.py turns it into the HyperFrames
composition, and the web editor (editor/index.html) reads and writes the same structure.
All caption times are SOURCE seconds, so captions follow the clips when cuts move.

  python3 tools/make_edit.py        (run from the project root; overwrites edit.json)
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# One cut per sentence; framings alternate so each cut reads as a deliberate punch-in.
# (source in, source out, zoom, slow push added over the clip)
SEGMENTS = [
    (0.00, 1.76, 1.00, 0.04),   # Salut, c'est Guillaume de LLM Monitor.
    (1.76, 5.89, 1.12, 0.03),   # Chez LLM Monitor ... au quotidien,
    (5.89, 8.29, 1.00, 0.04),   # que ce soit Claude, Gemini ou ChatGPT.
    (8.29, 11.75, 1.15, 0.03),  # Mais aujourd'hui ... distributeurs.
    (11.75, 15.91, 1.00, 0.04), # Et pour savoir ... votre marque,
    (15.91, 19.38, 1.12, 0.03), # les concurrents ... l'outil AI Shelf.
    (19.38, 24.02, 1.00, 0.05), # AI Shelf, nous vous le présenterons ... stand V19,
    (24.02, 26.20, 1.15, 0.02), # les 30 novembre et 1er décembre.
    (26.20, 29.85, 1.05, 0.06), # Venez nous rendre visite ... le lien est en commentaire.
]
FOCAL = (50, 30)  # face, in % of the frame

KEYWORDS = {
    "llm", "monitor", "visibilité", "ia", "claude", "gemini", "chatgpt", "clients", "chatbots", "distributeurs",
    "positionnement", "marque", "concurrents", "ai", "shelf", "tech4retail", "stand", "v19", "30", "novembre",
    "1er", "décembre", "badges", "commentaire",
}
MAX_CHARS = 24


def words():
    out = []
    for seg in json.load(open(ROOT / "tools" / "transcript.json")):
        for w in seg["words"]:
            t = w["w"].strip()
            if not t:
                continue
            if out and (t[0] in "'’-" or out[-1]["w"].endswith("'")):
                out[-1]["w"] += t
                out[-1]["e"] = w["e"]
                continue
            out.append({"w": t, "s": w["s"], "e": w["e"]})
    return out


def clean(t):
    return t.rstrip(".,;:")


# Names that never break across two caption lines.
BOUND = [("LLM", "Monitor"), ("AI", "Shelf"), ("30", "novembre"), ("1er", "décembre"), ("stand", "V19")]


def phrases(ws):
    """Split at punctuation, then fold one-word stubs ("Salut,") into the next phrase."""
    out, cur = [], []
    for w in ws:
        cur.append(w)
        if w["w"][-1] in ".,;:?!":
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    merged = []
    for ph in out:
        if merged and len(merged[-1]) == 1 and len(clean(merged[-1][0]["w"])) <= 8:
            merged[-1] = merged[-1] + ph
        else:
            merged.append(ph)
    return merged


def tokens(ph):
    """Words with bound names glued together (one caption token, first word's timing)."""
    out = []
    for w in ph:
        if out and any(clean(out[-1]["parts"][-1]["w"]) == x and clean(w["w"]) == y for x, y in BOUND):
            out[-1]["parts"].append(w)
            continue
        out.append({"parts": [w]})
    return out


def lines(toks):
    """Balanced split of a phrase into lines of at most MAX_CHARS."""
    text = lambda ts: " ".join(clean(p["w"]) for t in ts for p in t["parts"])
    total = len(text(toks))
    n = max(1, -(-total // MAX_CHARS))
    while True:
        target = total / n
        res, cur = [], []
        for t in toks:
            if cur and len(text(cur + [t])) > target + 4 and len(res) < n - 1:
                res.append(cur)
                cur = []
            cur.append(t)
        res.append(cur)
        if all(len(text(r)) <= MAX_CHARS for r in res) or n > 6:
            return res
        n += 1


def main():
    end = SEGMENTS[-1][1]
    ws = [w for w in words() if w["s"] < end - 0.05]
    caps = []
    for ph in phrases(ws):
        for ln in lines(tokens(ph)):
            parts = [p for t in ln for p in t["parts"]]
            caps.append({
                "start": round(parts[0]["s"], 2),
                "end": round(min(parts[-1]["e"] + 0.2, end), 2),
                "words": [{"w": clean(p["w"]), "t": round(p["s"], 2), "hl": clean(p["w"]).lower() in KEYWORDS} for p in parts],
            })
    for a, b in zip(caps, caps[1:]):
        a["end"] = round(min(a["end"], b["start"]), 2)
    edit = {
        "version": 1,
        "canvas": {"w": 1080, "h": 1920, "fps": 25},
        "segments": [{"in": a, "out": b, "zoom": z, "push": p, "fx": FOCAL[0], "fy": FOCAL[1]} for a, b, z, p in SEGMENTS],
        "captions": caps,
        "style": {"captions": "ligne", "size": 70, "y": 0.665, "green": "#2EBE9B", "box": "#117D67"},
        "music": {"enabled": True, "volume": 0.14},
        "outro": {"enabled": True, "duration": 6.067},
    }
    json.dump(edit, open(ROOT / "edit.json", "w"), ensure_ascii=False, indent=1)
    print(f"edit.json: {len(SEGMENTS)} clips, {len(caps)} caption lines, {end:.2f}s + outro")
    for c in caps:
        print(f"  {c['start']:6.2f}-{c['end']:6.2f}  " + " ".join(("[" + w["w"] + "]") if w["hl"] else w["w"] for w in c["words"]))


if __name__ == "__main__":
    main()
