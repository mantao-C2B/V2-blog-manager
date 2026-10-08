# Vidéo motion design LLM Monitor — notes de reprise

Fichier de passation entre sessions. Le brief définitif ira dans `BRIEF.md` du projet HyperFrames une fois créé.

## Demande (confirmée par l'utilisateur)

- Vidéo publicitaire en motion design pour LLM Monitor (https://www.llm-monitor.com/), pièce de portfolio pour convaincre des entreprises.
- Durée : entre 1:10 et 1:20.
- Garder la même DA que le site.
- Uniquement HyperFrames pour l'image (pas de génération vidéo ou d'images par d'autres outils). Zooms, illustrations, animations : viser impressionnant.
- Diffusion : site web et télés en boucle sur des salons pros → compréhensible avec et sans le son, boucle invisible.
- Textes à l'écran en français.
- L'utilisateur enregistre lui-même la voix off par-dessus → fournir le texte de voix off calé avec timecodes.
- Musique + effets sonores : à générer.
- Inspiration : vidéo sur Drive « vidéo inspi pour LLM Monitor » (.mov, 42 Mo), id `1yWtivpvhYzsSo5PPjydZ7aT0ZUBaxsby`. Style à reprendre et à dépasser.
- L'utilisateur doit encore envoyer son premier jet d'idées (« assez complet, à respecter »).

## Défauts proposés (non contredits)

- 16:9, 1920×1080 (4K possible).
- Validation en deux temps : découpage scène par scène, puis storyboard avec croquis, puis rendu.

## État technique (session du 2026-10-08)

- Skills HyperFrames installés dans `.claude/skills/` (CLI 0.8.141).
- Rendu local OK après `npx hyperframes browser ensure`.
- `cdn.jsdelivr.net` est bloqué : servir GSAP et les autres librairies en local (`npm pack gsap@3.14.2`, copier `dist/gsap.min.js` dans `vendor/`).
- Google Fonts et `generativelanguage.googleapis.com` passent.
- Bloqués par la politique réseau : `llm-monitor.com`, `www.llm-monitor.com`, `drive.google.com`, `drive.usercontent.google.com`, `huggingface.co`, `api.heygen.com`.
- Le connecteur Google Drive refuse les fichiers de plus de 10 Mo.
- Effets sonores : bibliothèque intégrée à `media-use` (19 sons).
- Musique : Lyria (Gemini) si `GEMINI_API_KEY` est fourni ; sinon composition par synthèse en code, calée sur le montage.
