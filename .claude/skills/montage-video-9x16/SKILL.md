---
name: montage-video-9x16
description: Monter une vidéo verticale face caméra (LLM Monitor ou Click2Buy / Market Connect, LinkedIn) à partir d'un lien Drive ou d'un fichier — coupes et zooms légers, sous-titres une ligne aux couleurs de la marque (mots clés en vert LLM Monitor ou surlignés en orange Click2Buy), musique légère (LLM Monitor), outro logo 9:16 de la marque, rendus MP4 et une interface de montage publiée (artefact) que l'utilisateur modifie et exporte seul. À utiliser dès qu'on donne une nouvelle vidéo à monter « comme la vidéo AI Shelf » ou « comme la vidéo Tech4Retail », « avec l'interface de montage », ou une vidéo verticale de Guillaume, Maxence ou de l'équipe à sous-titrer et habiller.
---

# Montage vidéo 9:16 avec interface d'édition

Le modèle complet est dans `videos/_modele-montage-9x16/` (lire son `README.md`). La marque se règle dans
`project.json` (`"brand": "llm-monitor"` ou `"click2buy"`), ses paramètres sont dans `tools/brands.json`.
Exemples de référence : `videos/llm-monitor-aishelf/` (interface https://claude.ai/artifact/Y8MAVFYtnjyyKJnD2ozUsY)
et `videos/click2buy-sequence03/` (Click2Buy, sans musique).

## Déroulé

1. **Rushes.** Lien Drive → `mcp__Google_Drive__get_file_metadata` (taille, nom), puis téléchargement direct :
   `curl -sS -L -o raw.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`
   dans `videos/_sources/<sujet>/` (dossier ignoré par git). Vérifier avec `ffprobe` : vertical 9:16 attendu.
2. **Projet.** `cp -r videos/_modele-montage-9x16 videos/<marque>-<sujet>`, puis `project.json` depuis
   `project.example.json` : marque, slug, titre, sous-titre (intervenant, contexte), mots clés, paires `bound`.
3. **Préparation.** `pip install faster-whisper scipy soundfile` si absent (relancer pip avec `--default-timeout=30`
   s'il se bloque), puis `bash tools/prepare.sh <raw.mp4>`. Lire `tools/transcript.json` : corriger les noms propres
   et repérer une fin de prise ratée (`end`).
4. **Découpe.** `python3 tools/make_edit.py` ; relire les lignes imprimées (mots verts entre crochets). Ajuster
   `keywords`, `bound`, `segments` ou `end` dans `project.json` et relancer jusqu'à ce que la découpe soit propre.
5. **Composition et son.** `python3 tools/build.py`, `npx hyperframes check`, puis `npx hyperframes snapshot --at …`
   sur 3-4 moments : sous-titres lisibles, zooms cadrés sur le visage (`focal`), fondu blanc vers l'outro.
6. **Rendus.** `bash tools/render_all.sh` (≈ 2-3 min par version) : LLM Monitor = avec musique, sans musique,
   surlignage, mot prononcé ; Click2Buy = une version (style du montage). Contrôler chaque MP4 (`ffprobe`, planche
   d'images, ≈ -14 LUFS) puis les envoyer (`SendUserFile`).
7. **Interface.** `python3 tools/make_editor.py`, puis publier avec l'outil Artifact : `file_path`
   `editor/index.html`, `files` {`media/footage.mp4`, `media/outro.mp4`, + `media/music.mp3` si la marque a une
   musique} depuis `editor/media/`,
   `capabilities` `{"db": {}, "user": {}, "downloads": true}`, `icon` `film`. Une fois publiée,
   `ArtifactData list` sur la collection `montage` (vide au départ : la page part du montage d'origine).
8. **Livraison.** Les vidéos, le lien de l'interface, ce qu'on peut y modifier, les points à vérifier
   (noms propres, dates). Commit + push des fichiers du projet (pas les médias).

## Charte (guide logo LLM Monitor)

- Sous-titres : Instrument Sans 700 (police de texte ; Sora réservée au nom et aux titres), blanc, une ligne.
- Mots clés en vert menthe #2EBE9B avec contour foncé (menthe = fond sombre uniquement) ; surlignage = aplat
  vert produit #117D67, texte blanc. Aucune autre teinte.
- Outro : `assets/outro.mp4` (logo empilé « LLM Monitor / By MarketConnect » sur blanc, sons sans musique).

## Charte Click2Buy

- Sous-titres : Poppins 700 (police de « By MarketConnect »), blanc, **sans contour** (demandé par l'utilisateur).
- Mots clés surlignés en orange BUY #E95531 (choisi par l'utilisateur ; l'orange CLICK #F39134 reste au choix
  dans l'interface). Pas de musique : voix + sons de l'outro.
- Outro : `assets/outro-click2buy.mp4` (épingle qui tombe, « 2 », CLICK / BUY, signature ; sans ondes), tiré de
  `videos/click2buy-outro-9x16/`.

## Pièges déjà rencontrés

- Le premier rendu de sous-titres blancs manquait de contraste sur un vêtement clair : le contour foncé est
  indispensable.
- Interface : sans chargement en blob, l'export sortait une image figée sur un serveur sans requêtes partielles.
  Pour la tester en local, l'envelopper dans `<meta charset=utf-8>` (sinon accents cassés) ; Chrome est dans
  `/usr/bin/google-chrome` (playwright-core).
- HyperFrames refuse deux compositions racine : ne jamais laisser une seconde page HTML avec
  `data-composition-id` à la racine du projet.
- Whisper large-v3 peut sauter une courte phrase : comparer avec le modèle `medium` en cas de doute.
