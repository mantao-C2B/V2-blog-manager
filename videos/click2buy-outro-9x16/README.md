# Outro logo Click2Buy — 9:16

Pendant de l'outro LLM Monitor (`../llm-monitor-summit/outro-logo-9x16/`) : 1080x1920, fond blanc,
6,07 s, effets sonores seuls (pas de musique, pas de carillon).

Rendu : `renders/Click2Buy_outro-logo_fond-blanc_9x16_sfx.mp4` (non versionné).

## Animation

| Temps | Image | Son |
| --- | --- | --- |
| 0,00 → 0,36 s | l'épingle tombe et se pose (léger écrasement, ondes au sol) | whoosh, impact grave à 0,36 s |
| 0,60 s | le « 2 » apparaît dans l'épingle | pop |
| 0,80 s | CLICK s'ouvre vers la gauche, BUY vers la droite, depuis l'épingle | deux whooshs courts, gauche / droite |
| 1,30 s | « By MarketConnect » : les lettres se rassemblent et deviennent nettes | whoosh inversé, clic à 1,55 s |
| 2,40 s | une onde discrète autour de l'épingle, puis lent zoom avant jusqu'à la fin | — |

## Refaire

```bash
python3 -I tools/split_logo.py    # assets/logo-source.png -> un PNG par forme dans assets/logo/ (+ layers.json)
bash tools/sfx.sh                 # assets/sfx.wav (sons de ../llm-monitor-promo/assets/sfx)
npx hyperframes check
npx hyperframes render --quality high -o renders/Click2Buy_outro-logo_fond-blanc_9x16_sfx.mp4
```

Le logo n'est jamais redessiné : chaque calque est découpé dans l'image fournie, et leur recomposition
redonne le logo au pixel près. Si le logo change, remplacer `assets/logo-source.png`, relancer
`split_logo.py` et recopier les positions de `layers.json` dans `LAYERS` (index.html).
