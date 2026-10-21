"""Word-level transcript of the rushes (faster-whisper large-v3, French) with spelling fixes."""

import json
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

FIX = {
    "Cloud": "Claude", "Cloud,": "Claude,", "Mariel": "Marvel", "Geminich,": "Gemini,", "HGPT,": "ChatGPT,",
    "Gémini,": "Gemini,", "Chartes": "Chat", "tâche": "Chat", "Tchad": "Chat", "LL": "LLM", "Jpt": "GPT",
}
HIGHLIGHT = {
    "llm", "monitor", "chatgpt", "gemini", "claude", "ia", "ia.", "geo", "seo", "visibilité", "concurrents",
    "linkedin", "summit", "150", "000", "conférence", "étude", "cités", "disneyland", "marvel", "décathlon",
    "intelligences", "artificielles", "ceo", "salon", "monitor.", "concurrents.", "4", "quatre", "chiffres",
}


# large-v3 dropped "Il y a beaucoup de gens" (316.2 s); words and timings from the medium model.
PATCH = [("Il", 316.12, 316.22), ("y", 316.22, 316.27), ("a", 316.27, 316.36), ("beaucoup", 316.36, 316.54),
         ("de", 316.54, 316.62), ("gens", 316.62, 316.74), ("qui", 316.76, 316.82)]


def load_words():
    data = json.load(open(TOOLS / "transcript.json"))
    words = []
    for seg in data:
        for w in seg["words"]:
            txt = w["w"].strip()
            if not txt:
                continue
            if 316.0 <= w["s"] < 316.8:
                continue
            words.append({"w": FIX.get(txt, txt), "s": w["s"], "e": w["e"]})
    words += [{"w": w, "s": a, "e": b} for (w, a, b) in PATCH]
    words.sort(key=lambda w: w["s"])
    # merge "chat GPT" / "Chat GPT" -> ChatGPT
    joined = []
    for w in words:
        if joined and (w["w"][:1] in ("'", "’", "-") or joined[-1]["w"].endswith("'")):
            joined[-1]["w"] += w["w"]
            joined[-1]["e"] = w["e"]
            continue
        joined.append(w)
    words = joined
    # keep "150 000" and "SEO & GEO" on one caption token
    merged = []
    for w in words:
        prev = merged[-1] if merged else None
        if prev and w["w"].rstrip(".,") == "000" and prev["w"].isdigit():
            prev["w"] += "\u00a0" + w["w"]
            prev["e"] = w["e"]
            continue
        if prev and prev["w"].endswith("\u00a0&") or (prev and w["w"] == "&" and prev["w"].upper() == "SEO"):
            prev["w"] += "\u00a0" + w["w"]
            prev["e"] = w["e"]
            continue
        merged.append(w)
    words = merged
    out = []
    for w in words:
        if out and out[-1]["w"].lower() in ("chat", "le chat") and w["w"].upper().startswith("GPT"):
            out[-1]["w"] = "ChatGPT" + w["w"][3:]
            out[-1]["e"] = w["e"]
            continue
        out.append(w)
    return out


WORDS = load_words()


def words_in(a, b):
    return [w for w in WORDS if w["s"] >= a - 0.02 and w["e"] <= b + 0.08]


