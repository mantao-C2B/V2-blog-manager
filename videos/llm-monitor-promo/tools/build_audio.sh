#!/usr/bin/env bash
# Rebuild the soundtrack: synthesised music + placed SFX, limited and normalised to -15 LUFS / -1.5 dBTP.
# Run from the project root: bash tools/build_audio.sh
set -euo pipefail
python3 tools/music.py assets/audio/music.wav
python3 tools/sfx.py assets/sfx assets/audio/sfx.wav
MIX="[0:a][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.89:attack=3:release=60:level=disabled"
STATS=$(ffmpeg -hide_banner -nostats -i assets/audio/music.wav -i assets/audio/sfx.wav \
  -filter_complex "$MIX,loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/{/,/}/p')
get() { echo "$STATS" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -hide_banner -v error -y -i assets/audio/music.wav -i assets/audio/sfx.wav -filter_complex \
  "$MIX,loudnorm=I=-15:TP=-1.5:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true,aresample=48000" \
  -c:a pcm_s24le assets/audio/soundtrack.wav
echo "soundtrack.wav rebuilt"
