# Vidéo motion design LLM Monitor — notes de reprise

Projet HyperFrames : `videos/llm-monitor-promo/`. Tout ce qui a été décidé est dans les fichiers du projet :

- `BRIEF.md` : demande, contraintes, choix faits (durée, marques fictives, chiffres harmonisés).
- `STORYBOARD.md` : les 9 plans (structure du storyboard CEO v3), timings, intentions de motion.
- `VOICEOVER.md` : voix off calée 80 s avec timecodes + version d'origine du CEO.
- `frame.md` : charte vidéo officielle (guide logo + site).
- `references/` : storyboard CEO, guide logo, captures du site et de la démo.

## Rendu

```bash
cd videos/llm-monitor-promo
npx hyperframes check                                   # gate qualité (doit passer)
npx hyperframes render --fps 25 --quality high -o renders/LLM-Monitor_promo_80s_1080p25.mp4
npx hyperframes render --fps 25 --quality high --variables '{"subtitles":true}' -o renders/LLM-Monitor_promo_80s_1080p25_sous-titres.mp4
```

## Son

`bash tools/build_audio.sh` régénère `assets/audio/soundtrack.wav` (musique synthétisée `tools/music.py` + effets `tools/sfx.py`, -15 LUFS). Les stems `music.wav` / `sfx.wav` sont produits au passage (non versionnés).

## Points techniques

- `cdn.jsdelivr.net` est bloqué dans cette session : GSAP est servi en local (`assets/vendor/gsap.min.js`).
- Les sous-compositions déclarent leurs `@font-face` en local (exigence du lint) ; `assets/brand.css` porte les tokens.
- `assets/kit.js` : symbole officiel (géométrie du guide), lockup au bon ratio, logos des IA, helpers d'animation seek-safe.
- Le domaine llm-monitor.com est bloqué par la politique réseau de la session : la DA vient des PDF fournis.
