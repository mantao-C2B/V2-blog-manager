#!/usr/bin/env bash
# Render the delivered versions (run from the project root, after tools/build.py has written the soundtracks).
#   brand with music (LLM Monitor): with music, without music, highlight style, spoken-word style
#   brand without music (Click2Buy): the edit's own caption style, voice + outro sound effects
set -euo pipefail
HF="npx --yes hyperframes@0.8.181"
out=renders
SLUG=$(python3 -c "import json;print(json.load(open('project.json'))['slug'])")
MUSIC=$(python3 -c "import json;p=json.load(open('project.json'));print(json.load(open('tools/brands.json'))[p.get('brand','llm-monitor')]['music'])")
python3 tools/build.py --no-audio
if [ "$MUSIC" = "True" ]; then
  $HF render --quality high -o $out/${SLUG}_9x16_musique.mp4
  $HF render --quality high --variables '{"captionStyle":"surlignage"}' -o $out/${SLUG}_9x16_musique_style-surlignage.mp4
  $HF render --quality high --variables '{"captionStyle":"karaoke"}' -o $out/${SLUG}_9x16_musique_style-mot-actif.mp4
  python3 tools/build.py --no-audio --sans-musique
  $HF render --quality high -o $out/${SLUG}_9x16_sans-musique.mp4
  python3 tools/build.py --no-audio
else
  $HF render --quality high -o $out/${SLUG}_9x16.mp4
fi
echo "renders done"
