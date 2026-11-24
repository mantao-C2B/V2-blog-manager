# LLM Monitor — AI Shelf au salon Tech4Retail (9:16)

Rushes : « Main Edittest 1 vidéo LLM.mp4 » (Drive), Guillaume face caméra, 4K vertical, 30 s.
Montage : coupes à chaque phrase avec cadrages alternés et zooms lents, sous-titres une ligne
(Instrument Sans, mots clés en vert), musique légère sous la voix, outro logo 9:16 (sons seuls).

## Livrables (renders/, non versionnés)

- `LLM-Monitor_AI-Shelf_9x16_musique.mp4` — version principale.
- `LLM-Monitor_AI-Shelf_9x16_sans-musique.mp4` — voix + sons de l'outro.
- `…_musique_style-surlignage.mp4`, `…_musique_style-mot-actif.mp4` — styles de sous-titres proposés.

## Éditeur en ligne

https://claude.ai/artifact/Y8MAVFYtnjyyKJnD2ozUsY — sous-titres (texte, mots en vert, timing), coupes,
zooms, style, musique, outro ; enregistrement automatique ; export MP4 dans le navigateur (Chrome/Edge).
Source : `editor/editor.template.html` ; `python3 tools/make_editor.py` assemble `editor/index.html`
(edit.json intégré comme montage d'origine) et `editor/media/`.

## Chaîne HyperFrames

```bash
python3 tools/make_edit.py   # edit.json : coupes, cadrages, sous-titres (depuis tools/transcript.json)
python3 tools/build.py       # index.html + musique + bandes-son (-14 LUFS)
bash tools/render_all.sh     # les 4 rendus
```

`edit.json` est le format commun à HyperFrames et à l'éditeur : un montage enregistré dans l'éditeur
(document `montage/courant` de l'artefact) peut être recopié dans `edit.json` puis rendu ici.
Médias de travail : `../_source2/` (non versionné) — `work_1440.mp4` (rendu) et `web_1080.mp4` (éditeur),
voix nettoyée, normalisée à -16 LUFS.

## Réutiliser pour une autre vidéo

Ce projet a servi de base au modèle `../_modele-montage-9x16/` (mêmes scripts, rendus identiques sur cette
vidéo, coupes automatiques par phrase) et à la procédure `.claude/skills/montage-video-9x16/SKILL.md`.
