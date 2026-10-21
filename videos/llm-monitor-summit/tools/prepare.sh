#!/usr/bin/env bash
# Prepare the media every version needs, from the raw rushes.
#   bash tools/prepare.sh            (run from videos/llm-monitor-summit)
# Input : ../_source/raw.mp4  (Drive: "vidéo test sans montage_CLAUDE.mp4", 3840x2160, 30 fps, 5 min 45)
# Output: ../_source/work_1440.mp4   graded 2560x1440 working copy (hard-linked as vX/assets/footage.mp4)
#         assets_shared/speech.wav   cleaned speech / room sound, 48 kHz
#         assets_shared/sfx/*.wav    SFX converted from ../llm-monitor-promo/assets/sfx (Pixabay licence)
set -euo pipefail
SRC=../_source/raw.mp4
WORK=../_source/work_1440.mp4

# The show floor is lit magenta: correct it on the salon / booth / outro ranges only.
SALON="between(t,27.1,62.4)+between(t,76.6,153.5)+between(t,306.3,346)"
if [ ! -f "$WORK" ]; then
  ffmpeg -hide_banner -v error -y -i "$SRC" -vf \
    "scale=2560:1440:flags=lanczos,colorbalance=rs=-0.03:gs=0.02:bs=-0.05:rm=-0.04:gm=0.06:bm=-0.08:rh=-0.02:gh=0.03:bh=-0.05:enable='$SALON',eq=saturation=0.92:contrast=1.04:enable='$SALON'" \
    -c:v libx264 -preset fast -crf 17 -g 15 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k -ar 48000 "$WORK"
fi

mkdir -p assets_shared/sfx
ffmpeg -hide_banner -v error -y -i "$SRC" -vn \
  -af "highpass=f=85,afftdn=nf=-28:nr=10,acompressor=threshold=-24dB:ratio=2.5:attack=8:release=140:makeup=1.5" \
  -ar 48000 -ac 2 -c:a pcm_s16le assets_shared/speech.wav
for f in ../llm-monitor-promo/assets/sfx/*.mp3; do
  ffmpeg -hide_banner -v error -y -i "$f" -ar 48000 -ac 2 "assets_shared/sfx/$(basename "${f%.mp3}").wav"
done

for v in v1-vlog v2-aftermovie v3-insights; do
  mkdir -p "$v/assets/vendor" "$v/assets/fonts"
  cp ../llm-monitor-promo/assets/vendor/gsap.min.js "$v/assets/vendor/"
  cp ../llm-monitor-promo/assets/fonts/*.woff2 "$v/assets/fonts/"
  cp ../llm-monitor-promo/assets/kit.js "$v/assets/kit.js"
  ln -f "$WORK" "$v/assets/footage.mp4"
done
echo "media ready"
