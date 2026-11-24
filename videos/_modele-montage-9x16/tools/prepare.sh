#!/usr/bin/env bash
# Prepare a vertical talking-head video for this template (run from the project root).
#   bash tools/prepare.sh path/to/raw.mp4 [end_seconds]
# Writes (all git-ignored):
#   assets/footage.mp4   1440x2560 working copy for the HyperFrames render (cleaned voice, -16 LUFS)
#   assets/web.mp4       1080x1920 light copy for the web editor (≈3 Mb/s, must stay under 15 MB)
#   tools/audio16k.wav   mono 16 kHz audio, then tools/transcript.json (faster-whisper large-v3)
set -euo pipefail
RAW="$1"
FPS=$(python3 -c "import json;print(json.load(open('project.json'))['canvas']['fps'])")
TRIM=()
if [ "${2:-}" != "" ]; then TRIM=(-t "$2"); fi
VOICE="highpass=f=80,afftdn=nf=-30:nr=8,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=150:makeup=1,loudnorm=I=-16:TP=-1.5:LRA=7"
ffmpeg -hide_banner -v error -y -i "$RAW" "${TRIM[@]}" -vf "scale=1440:2560:force_original_aspect_ratio=increase:flags=lanczos,crop=1440:2560" \
  -af "$VOICE" -c:v libx264 -preset medium -crf 16 -g 12 -pix_fmt yuv420p -r "$FPS" -movflags +faststart -c:a aac -b:a 256k -ar 48000 assets/footage.mp4
ffmpeg -hide_banner -v error -y -i "$RAW" "${TRIM[@]}" -vf "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920" \
  -af "$VOICE" -c:v libx264 -preset slow -b:v 3000k -maxrate 3800k -bufsize 6000k -g 25 -pix_fmt yuv420p -r "$FPS" -movflags +faststart \
  -c:a aac -b:a 128k -ar 48000 assets/web.mp4
SIZE=$(stat -c %s assets/web.mp4)
if [ "$SIZE" -gt 15000000 ]; then echo "assets/web.mp4 is over 15 MB: lower -b:v in tools/prepare.sh" >&2; exit 1; fi
ffmpeg -hide_banner -v error -y -i "$RAW" "${TRIM[@]}" -vn -ac 1 -ar 16000 tools/audio16k.wav
python3 -I tools/transcribe.py tools/audio16k.wav tools/transcript.json large-v3
echo "footage ready; transcript in tools/transcript.json"
