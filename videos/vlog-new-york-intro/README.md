# Intro vlog New York — montage cut sur la musique (50,5 s)

Source : `VLOG NEW YORK GOOD.mp4` (Google Drive, 2 min 16, 1080p30) = 70 plans dans le désordre + une musique. Pas de motion design : seulement l'ordre des plans, calé sur le temps.

- `edit.json` : les 43 plans retenus (plan source, point d'entrée, temps de début et de fin dans la grille musicale) et les réglages musique.
- `VOIX_OFF.md` : script de voix off calé au dixième de seconde, variantes, conseils de mixage.
- `voiceover.json` : le même script en données, pour générer la voix témoin.
- `tools/build.py` : rendu image par image + musiques montées + EDL + liste des plans.
- `tools/tts_guide.py` : voix témoin (Piper, voix `fr_FR-tom-medium`).

## Musique

170 BPM (ressenti 85), premier temps à 1,393 s. Structure : nappe (0 → 1,4), intro batterie (→ 8,5), montée basse (→ 14,1), puis phrases de 32 temps, cassure à 59,3 s dans le morceau d'origine. Pour tenir sous la minute, une phrase entière (14,09 → 25,40 s du morceau) est retirée : le raccord tombe sur un temps fort, la grille rythmique reste continue (écart mesuré 12 ms). L'intro se termine sur la cassure (batterie qui s'arrête), avec 2,5 s de queue en fondu.

La musique contient une voix chantée continue à partir de 14 s : elle est séparée avec Demucs (`htdemucs`, deux stems) pour obtenir une version instrumentale qui laisse la place à la voix off.

## Rebuild

```bash
# dépendances : ffmpeg, numpy, soundfile ; demucs et piper-tts pour les étapes optionnelles
ffmpeg -i "VLOG NEW YORK GOOD.mp4" -vn -t 126 -ac 2 -ar 44100 music.wav
python3 -m demucs -n htdemucs --two-stems=vocals -o stems music.wav
python3 tools/tts_guide.py --model fr_FR-tom-medium.onnx --out vo_guide.wav
python3 tools/build.py --source "VLOG NEW YORK GOOD.mp4" --music music.wav \
    --instrumental stems/htdemucs/music/no_vocals.wav --vo vo_guide.wav --out renders
```

`build.py` vérifie que chaque plan reste dans les limites de son plan source et que chaque segment a le bon nombre d'images. `--reuse-picture` ne refait que le son et les muxages.

Sorties : `Intro_NYC_instru.mp4` (prêt pour la voix off), `Intro_NYC_musique-originale.mp4`, `Intro_NYC_instru+voix-temoin.mp4`, les WAV de musique montée, `Intro_NYC.edl` (CMX 3600, 30 i/s, timeline à 01:00:00:00) et `plans.tsv`.
