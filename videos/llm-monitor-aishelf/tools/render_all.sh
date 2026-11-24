#!/usr/bin/env bash
# Render the delivered versions (run from the project root, after tools/build.py has written the soundtracks).
set -euo pipefail
HF="npx --yes hyperframes@0.8.181"
out=renders
python3 tools/build.py --no-audio
$HF render --quality high -o $out/LLM-Monitor_AI-Shelf_9x16_musique.mp4
$HF render --quality high --variables '{"captionStyle":"surlignage"}' -o $out/LLM-Monitor_AI-Shelf_9x16_musique_style-surlignage.mp4
$HF render --quality high --variables '{"captionStyle":"karaoke"}' -o $out/LLM-Monitor_AI-Shelf_9x16_musique_style-mot-actif.mp4
python3 tools/build.py --no-audio --sans-musique
$HF render --quality high -o $out/LLM-Monitor_AI-Shelf_9x16_sans-musique.mp4
python3 tools/build.py --no-audio
echo "renders done"
