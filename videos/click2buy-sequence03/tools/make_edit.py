"""Write the first edit.json from project.json + the transcript: cut points, framings, one-line captions.

edit.json is the single description of the edit. tools/build.py turns it into the HyperFrames
composition, and the web editor (editor/) reads and writes the same structure.
Caption times are SOURCE seconds, so captions follow the clips when cuts move.

  python3 tools/make_edit.py        (run from the project root; overwrites edit.json)

Cuts: by default one clip per sentence (a cut in the pause after . ! ?, and after a comma once a clip
runs past 3.5 s with 2 s of the sentence still to come), clips under 1.2 s merged forward. project.json "segments" can list
[in, out] pairs instead. Framings cycle through "zooms", slow pushes through "pushes".
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = json.load(open(ROOT / "project.json"))
BRAND = json.load(open(ROOT / "tools" / "brands.json"))[P.get("brand", "llm-monitor")]
KEYWORDS = {k.lower() for k in P["keywords"]}
BOUND = [tuple(b) for b in P.get("bound", [])]
MAX_CHARS = P.get("max_chars", 24)


def words():
    out = []
    for seg in json.load(open(ROOT / "tools" / "transcript.json")):
        for w in seg["words"]:
            t = w["w"].strip()
            if not t or w["e"] - w["s"] < 0.01:  # zero-length words are Whisper ghosts
                continue
            # glue elisions (l' + 'équipe) and lone punctuation ("Hello" + "!") to the word before
            if out and (t[0] in "'’-" or out[-1]["w"].endswith("'") or all(ch in "!?.,;:…" for ch in t)):
                out[-1]["w"] += t
                out[-1]["e"] = w["e"]
                continue
            out.append({"w": t, "s": w["s"], "e": w["e"]})
    return out


def clean(t):
    return t.rstrip(".,;:!… ")


def auto_segments(ws):
    cuts, start = [], max(0.0, ws[0]["s"] - 0.12)
    for i, w in enumerate(ws[:-1]):
        nxt = ws[i + 1]
        end_of_sentence = w["w"][-1] in ".!?"
        # a comma cut only when the clip already runs long and the sentence still has 2 s to go
        sentence_end = next((x["e"] for x in ws[i + 1:] if x["w"][-1] in ".!?"), ws[-1]["e"])
        long_clause = w["w"][-1] in ",;:" and w["e"] - start > 3.5 and sentence_end - w["e"] > 2.0
        if (end_of_sentence or long_clause) and w["e"] - start >= 1.2:
            cut = round((w["e"] + nxt["s"]) / 2, 2)
            cuts.append((round(start, 2), cut))
            start = cut
    cuts.append((round(start, 2), round(ws[-1]["e"] + 0.15, 2)))
    return cuts


def phrases(ws):
    """Split at punctuation, then fold one-word stubs ("Salut,") into the next phrase ("Hello !" stays alone)."""
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
        if merged and len(merged[-1]) == 1 and len(clean(merged[-1][0]["w"])) <= 8 and merged[-1][0]["w"][-1] not in "!?":
            merged[-1] = merged[-1] + ph
        else:
            merged.append(ph)
    return merged


def tokens(ph):
    """Words with bound names glued together (they never break across two caption lines)."""
    out = []
    for w in ph:
        if out and any(clean(out[-1]["parts"][-1]["w"]) == x and clean(w["w"]) == y for x, y in BOUND):
            out[-1]["parts"].append(w)
            continue
        out.append({"parts": [w]})
    return out


# Words a caption line should not end on (they belong with the word after them).
STOP = {"à", "a", "au", "aux", "de", "du", "des", "d'", "le", "la", "les", "l'", "un", "une", "et", "ou", "pour", "avec",
        "sur", "dans", "en", "par", "qu'on", "que", "qui", "nos", "vos", "notre", "votre", "ce", "cette", "son", "sa",
        "ses", "mon", "ma", "mes", "comment", "on", "nous", "vous", "je", "tu", "il", "elle", "ils", "très", "plus"}


def lines(toks):
    """Split a phrase into lines of at most MAX_CHARS: fewest lines, even lengths, no line ending on a small word."""
    text = lambda ts: " ".join(clean(p["w"]) for t in ts for p in t["parts"])
    n = len(toks)
    best, prev = [0.0] + [float("inf")] * n, [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            L = len(text(toks[i:j]))
            if L > MAX_CHARS and j - i > 1:
                break
            cost = 400 + (MAX_CHARS - L) ** 2
            if j < n and clean(toks[j - 1]["parts"][-1]["w"]).lower() in STOP:
                cost += 300
            if best[i] + cost < best[j]:
                best[j], prev[j] = best[i] + cost, i
    out, j = [], n
    while j > 0:
        out.append(toks[prev[j]:j])
        j = prev[j]
    return out[::-1]


def main():
    ws = words()
    segs = [tuple(s) for s in P["segments"]] if P.get("segments") else auto_segments(ws)
    if P.get("end"):
        segs = [(a, min(b, P["end"])) for a, b in segs if a < P["end"]]
    end = segs[-1][1]
    ws = [w for w in ws if w["s"] < end - 0.05]
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
    zooms, pushes, (fx, fy) = P["zooms"], P["pushes"], P["focal"]
    edit = {
        "version": 1,
        "canvas": P["canvas"],
        "segments": [{"in": a, "out": b, "zoom": zooms[i % len(zooms)], "push": pushes[i % len(pushes)], "fx": fx, "fy": fy}
                     for i, (a, b) in enumerate(segs)],
        "captions": caps,
        "style": {"captions": P.get("caption_style", "ligne"), "size": P.get("caption_size", 70), "y": P.get("caption_y", 0.665),
                  "green": BRAND["text_color"], "box": BRAND["box_color"]},
        "music": {"enabled": BRAND["music"], "volume": P.get("music_volume", 0.14)},
        "outro": {"enabled": bool(P.get("outro", True)), "duration": 6.067},
    }
    json.dump(edit, open(ROOT / "edit.json", "w"), ensure_ascii=False, indent=1)
    print(f"edit.json: {len(segs)} clips, {len(caps)} caption lines, {end:.2f}s + outro")
    for c in caps:
        print(f"  {c['start']:6.2f}-{c['end']:6.2f}  " + " ".join(("[" + w["w"] + "]") if w["hl"] else w["w"] for w in c["words"]))


if __name__ == "__main__":
    main()
