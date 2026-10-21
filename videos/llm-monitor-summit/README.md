# LLM Monitor au SEO & GEO Summit — 3 montages LinkedIn

Rushes : « vidéo test sans montage_CLAUDE.mp4 » (Drive), filmés les 15 et 16 octobre 2026 à Disneyland Paris.
Trois projets HyperFrames, un par version :

| Version | Dossier | Format | Durée | Angle |
| --- | --- | --- | --- | --- |
| 1 · Le vlog | `v1-vlog/` | 16:9, 1920×1080 | 2 min 28 | Le récit complet : intro de Maxence, salon, stand, interview de Guillaume, conférence, conclusion |
| 2 · L'aftermovie | `v2-aftermovie/` | 4:5, 1080×1350 | 49 s | Rythmé sur la musique (128 BPM), typographie cinétique, deux phrases parlées |
| 3 · Les enseignements | `v3-insights/` | 1:1, 1080×1080 | 56 s | Post d'expertise : « ChatGPT préfère vos concurrents ! », 3 enseignements de l'étude |

Chaque dossier contient `BRIEF.md` (demande et choix), `STORYBOARD.md` (liste des plans, généré) et `index.html` (généré).

## Chaîne de fabrication

```bash
cd videos/llm-monitor-summit
bash tools/prepare.sh                 # copie de travail étalonnée, voix nettoyée, SFX, polices, GSAP
python3 tools/build.py v1             # (v2, v3) découpe → index.html, STORYBOARD.md, musique, bande-son mixée
cd v1-vlog && npx hyperframes check   # contrôle (lint, mise en page, contraste)
npx hyperframes render --quality high -o renders/LLM-Monitor_SEO-GEO-Summit_v1-vlog.mp4
```

- `tools/versions.py` — **source de vérité des coupes** : timecodes source, cadrages, transitions, motion design, effets sonores, structure musicale.
- `tools/build.py` — place les plans, génère les sous-titres mot à mot depuis `tools/transcript.json` (faster-whisper large-v3, corrigé dans `tools/transcript.py`), écrit la composition et mixe la bande-son (voix normalisée, ambiance, musique baissée sous la parole, SFX, −14 LUFS / −1 dBTP).
- `tools/engine.js` + `tools/edit.css` — moteur de motion design aux couleurs LLM Monitor (charte : `../llm-monitor-promo/frame.md`) : bandeaux nom/fonction, tag de lieu, cartons de chapitre, logos des IA, compteur, carte chiffre clé, liste « À faire », citation, carton de fin, sous-titres karaoké.
- `tools/music_engine.py` + `tools/songs.py` — musiques originales synthétisées en code (aucun droit à payer), coupées à l'image : chaque section repart sur un temps fort aligné avec les coupes.

Non versionnés (lourds, régénérables) : rushes et copie de travail (`../_source/`), `assets_shared/`, `*/assets/footage.mp4`, `*/assets/*.wav`, `*/renders/`.

## Points à valider avant publication

- Orthographe « Maxence Antao » (déduite de l'audio).
- Maxence dit « plus de 150 000 conversations » ; la slide titre de la conférence dit « 130 000 réponses d'IA ». Le compteur de la version 1 reprend les mots de Maxence.
- Le 11 % et « 1 fois sur 9 » viennent de la slide « Quand l'IA parle de vous, utilise-t-elle votre site ? ».
