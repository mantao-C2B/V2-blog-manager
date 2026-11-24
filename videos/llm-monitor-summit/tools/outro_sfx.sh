#!/usr/bin/env bash
# Rebuild outro-logo-9x16/assets/sfx.wav: sound effects only, one per appearance in the logo animation.
#   0.000 impact-bass-2 + whoosh  symbol draws in (impact tail faded out by 1.05 s)
#   0.405 pop                     pupil pops
#   0.600 whoosh-short            "LLM Monitor" rises
#   0.975 whoosh-short, reversed  "By MarketConnect" is drawn in (peaks as its letters converge)
#   1.550 click                   the signature locks in place
# Gains even out the files' very different loudness; the mix is then peak-normalised to -1.5 dBFS.
# Run from videos/llm-monitor-summit.
set -euo pipefail
SFX=../llm-monitor-promo/assets/sfx
OUT=outro-logo-9x16/assets/sfx.wav
TMP=$(mktemp -d)
F="aresample=48000,aformat=sample_fmts=flt:channel_layouts=stereo"
ffmpeg -hide_banner -v error -y \
  -i $SFX/impact-bass-2.mp3 -i $SFX/whoosh.mp3 -i $SFX/pop.mp3 -i $SFX/whoosh-short.mp3 -i $SFX/whoosh-short.mp3 -i $SFX/click.mp3 \
  -filter_complex "[0:a]$F,volume=0.19,afade=t=out:st=0.45:d=0.6[a0];[1:a]$F,volume=0.65[a1];[2:a]$F,volume=1.15,adelay=405|405[a2];\
[3:a]$F,volume=0.51,adelay=600|600[a3];[4:a]$F,areverse,volume=0.45,adelay=975|975[a4];[5:a]$F,volume=1.4,adelay=1550|1550[a5];\
[a0][a1][a2][a3][a4][a5]amix=inputs=6:normalize=0:duration=longest,apad=whole_dur=6.067,atrim=0:6.067[m]" \
  -map "[m]" -c:a pcm_f32le -ar 48000 "$TMP/raw.wav"
PEAK=$(ffmpeg -hide_banner -i "$TMP/raw.wav" -af volumedetect -f null - 2>&1 | awk '/max_volume/ {print $5}')
GAIN=$(python3 -c "print(round(-1.5 - ($PEAK), 2))")
ffmpeg -hide_banner -v error -y -i "$TMP/raw.wav" -af "volume=${GAIN}dB" -c:a pcm_s24le "$OUT"
rm -rf "$TMP"
echo "$OUT written (gain ${GAIN} dB)"
