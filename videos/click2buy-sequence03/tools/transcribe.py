"""Word-level French transcript with faster-whisper.

  python3 tools/transcribe.py audio16k.wav out.json [model]     (model: large-v3 by default)
audio16k.wav: mono 16 kHz WAV (ffmpeg -i video.mp4 -vn -ac 1 -ar 16000 audio16k.wav).
"""

import json
import sys

import soundfile as sf
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
model_name = sys.argv[3] if len(sys.argv) > 3 else "large-v3"
model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
audio, sr = sf.read(src, dtype="float32")
assert sr == 16000, "expects 16 kHz mono audio"
segs, _ = model.transcribe(
    audio, language="fr", word_timestamps=True, vad_filter=True, beam_size=5,
    initial_prompt="LLM Monitor, Market Connect, SEO, GEO, ChatGPT, Gemini, Claude, Perplexity, visibilité dans les IA.",
)
res = []
for s in segs:
    res.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)}
                          for w in (s.words or [])]})
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
