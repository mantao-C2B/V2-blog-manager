# Modèle de montage 9:16 — face caméra LLM Monitor / Click2Buy

Modèle réutilisable tiré du montage « AI Shelf » (`../llm-monitor-aishelf/`), décliné pour Click2Buy
(`../click2buy-sequence03/`). La marque se choisit dans `project.json` (`"brand"`) ; tout ce qui en dépend
(police, couleurs, contour, outro, musique, couleurs et logo de l'interface) est dans `tools/brands.json`.

| | `llm-monitor` | `click2buy` |
| --- | --- | --- |
| Sous-titres | Instrument Sans, blanc avec contour foncé | Poppins (police de « By MarketConnect »), blanc sans contour |
| Mots clés | vert menthe #2EBE9B, surlignage vert produit #117D67 | surlignage orange BUY #E95531 (orange CLICK #F39134 au choix) |
| Musique | oui (versions avec et sans) | non : voix + sons de l'outro |
| Outro | `assets/outro.mp4` | `assets/outro-click2buy.mp4` |
| Rendus | 4 (musique, sans musique, surlignage, mot prononcé) | 1 (style du montage) |

Pour une vidéo verticale face caméra, il produit :

- un montage propre : un plan par phrase avec cadrages alternés (100 / 112 / 115 %) et zooms lents ;
- des sous-titres sur une ligne aux couleurs de la marque, trois styles (ligne, surlignage, mot prononcé) ;
  deux mots clés qui se suivent (« LLM Monitor ») partagent un seul surlignage ;
- pour LLM Monitor, une musique légère originale sous la voix (`tools/songs.py`, style `light`), versions
  avec et sans musique ;
- l'outro logo 9:16 de la marque sur fond blanc, avec ses effets sonores ;
- **l'interface de montage** (`editor/`) : une page publiée comme artefact claude.ai où l'on corrige les
  sous-titres, passe des mots en vert, ajuste coupes et zooms, change le style, la musique et l'outro,
  avec enregistrement automatique et export MP4 dans le navigateur.

## Nouveau projet

```bash
cd videos
cp -r _modele-montage-9x16 llm-monitor-<sujet>
cd llm-monitor-<sujet>
cp project.example.json project.json          # marque, titre, slug, mots clés, noms à ne pas couper…
mkdir -p ../_sources/<sujet> && echo '*' > ../_sources/<sujet>/.gitignore
# rushes dans ../_sources/<sujet>/raw.mp4 (Drive : curl "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t")
bash tools/prepare.sh ../_sources/<sujet>/raw.mp4     # copies de travail + transcription (large-v3)
python3 tools/make_edit.py                    # edit.json : coupes + sous-titres ; relire la liste imprimée
python3 tools/build.py                        # index.html + musique + bandes-son (-14 LUFS)
npx hyperframes check                         # 0 erreur attendue (avertissements de structure normaux)
bash tools/render_all.sh                      # MP4 dans renders/ (4 pour LLM Monitor, 1 pour Click2Buy)
python3 tools/make_editor.py                  # editor/index.html + editor/media/
```

Puis publier l'interface (outil Artifact) : `file_path` = `editor/index.html`, `files` =
`media/footage.mp4`, `media/outro.mp4` et, pour une marque avec musique, `media/music.mp3` (depuis `editor/media/`),
`capabilities` = `{"db": {}, "user": {}, "downloads": true}`, `icon` = `film`.

## Réglages (`project.json`)

| Clé | Rôle |
| --- | --- |
| `brand` | `llm-monitor` ou `click2buy` (voir `tools/brands.json`) |
| `slug`, `title`, `subtitle` | noms des fichiers exportés, titre de l'interface |
| `keywords` | mots passés en vert (minuscules, sans ponctuation) |
| `bound` | paires de mots jamais séparées sur deux lignes (`["AI","Shelf"]`, `["stand","V19"]`) |
| `segments` | `null` = une coupe par phrase ; sinon liste `[début, fin]` en secondes de la prise |
| `end` | coupe tout ce qui suit (prise ratée, phrase répétée en fin de rush) |
| `zooms`, `pushes`, `focal` | cadrages successifs, zoom lent par plan, point de zoom (% de l'image, visage) |
| `max_chars` | longueur max d'une ligne de sous-titre (24 pour 1080 px de large) |
| `caption_style`, `caption_size`, `caption_y` | style par défaut (`ligne`, `surlignage`, `karaoke`), taille, hauteur |
| `music_volume`, `outro` | niveau de la musique (0,14 ≈ -12 dB sous la voix, marques avec musique), outro oui/non |

## Ce qui est déjà réglé (et pourquoi)

- Médias de l'interface chargés en mémoire (blob) : le déplacement image par image ne dépend pas du serveur.
- Export : WebCodecs + mp4-muxer, H.264 ; son AAC (Mac/Windows) ou Opus (Linux). Chrome ou Edge sur ordinateur.
- Une seule composition racine HyperFrames (`index.html`) : la version sans musique se fait par `--sans-musique`.
- Mots « fantômes » de Whisper (durée nulle, ex. une phrase répétée après la fin) ignorés à la découpe.
