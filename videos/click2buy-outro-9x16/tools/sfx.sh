#!/usr/bin/env bash
# Rebuild assets/sfx.wav: sound effects only (no music), one per appearance in the logo animation.
#   0.000 whoosh                     the pin falls in
#   0.310 impact-bass-1 (hit 0.36 s) the pin lands (tail faded out)
#   0.520 pop (transient 0.63 s)     the "2" pops inside the pin
#   0.740 whoosh-short x2, L / R     CLICK opens to the left, BUY to the right
#   0.975 whoosh-short, reversed     "By MarketConnect" is drawn in (peaks as its letters converge)
#   1.550 click                      the signature locks in place
# Same sound palette and loudness as the LLM Monitor 9:16 outro; peak-normalised to -1.5 dBFS.
# Run from the project root.
set -euo pipefail
SFX=../llm-monitor-promo/assets/sfx
OUT=assets/sfx.wav
TMP=$(mktemp -d)
F="aresample=48000,aformat=sample_fmts=flt:channel_layouts=stereo"
ffmpeg -hide_banner -v error -y \
  -i $SFX/whoosh.mp3 -i $SFX/impact-bass-1.mp3 -i $SFX/pop.mp3 -i $SFX/whoosh-short.mp3 -i $SFX/whoosh-short.mp3 \
  -i $SFX/whoosh-short.mp3 -i $SFX/click.mp3 \
  -filter_complex "[0:a]$F,volume=0.55[a0];\
[1:a]$F,volume=0.2,afade=t=out:st=0.25:d=0.6,adelay=310|310[a1];\
[2:a]$F,volume=1.15,adelay=520|520[a2];\
[3:a]$F,volume=0.42,pan=stereo|c0=0.9*c0|c1=0.35*c1,adelay=740|740[a3];\
[4:a]$F,volume=0.42,pan=stereo|c0=0.35*c0|c1=0.9*c1,adelay=780|780[a4];\
[5:a]$F,areverse,volume=0.45,adelay=975|975[a5];\
[6:a]$F,volume=1.4,adelay=1550|1550[a6];\
[a0][a1][a2][a3][a4][a5][a6]amix=inputs=7:normalize=0:duration=longest,apad=whole_dur=6.067,atrim=0:6.067[m]" \
  -map "[m]" -c:a pcm_f32le -ar 48000 "$TMP/raw.wav"
PEAK=$(ffmpeg -hide_banner -i "$TMP/raw.wav" -af volumedetect -f null - 2>&1 | awk '/max_volume/ {print $5}')
GAIN=$(python3 -c "print(round(-1.5 - ($PEAK), 2))")
ffmpeg -hide_banner -v error -y -i "$TMP/raw.wav" -af "volume=${GAIN}dB" -c:a pcm_s24le "$OUT"
rm -rf "$TMP"
echo "$OUT written (gain ${GAIN} dB)"
