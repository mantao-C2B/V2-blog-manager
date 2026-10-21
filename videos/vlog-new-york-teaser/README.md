# Teaser vlog New York — « New York, New York » (56,9 s)

Mêmes rushes que l'intro (`VLOG NEW YORK GOOD.mp4`), musique : Frank Sinatra, *New York, New York*. Montage cut uniquement (pas de motion design), 58 plans + 2 noirs, chaque coupe posée sur un coup de batterie, de basse ou de cuivres du morceau (écart moyen mesuré : 21 ms, moins d'une image).

## Le morceau, remonté

L'orchestre n'est pas au métronome (95 à 117 BPM, ralenti final) : les coupes suivent les coups réellement joués, repérés sur les pistes séparées (Demucs) et les paroles transcrites au mot (Whisper).

| Teaser | Morceau | Passage |
| --- | --- | --- |
| 0:00 → 0:25.2 | 0:00.3 → 0:25.5 | Les 4 coups de baguette, le vamp instrumental, « Start spreading the news, I'm leaving today » |
| 0:25.2 → 0:25.7 | — | Un temps de silence, image noire (le saut par-dessus la caméra ferme l'objectif juste avant) |
| 0:25.7 → 0:56.9 | 2:54.3 → 3:25.5 | Le final : « If I can make it there, I'm gonna make it anywhere, it's up to you, New York, New York » jusqu'au dernier coup d'orchestre |

Le saut du couplet (ré majeur) au final (mi bémol) reproduit la montée d'un demi-ton que le morceau fait lui-même ; le temps de silence la rend volontaire.

## Déroulé

| Temps | Musique | Images |
| --- | --- | --- |
| 0:00 | Coups de baguette | 4 flashs : écrans de Times Square, Empire State, Statue, taxi dans la vapeur |
| 0:01.2 | L'orchestre entre | Times Square de nuit, puis 1 plan tous les 2 temps (Brooklyn, DUMBO, hot-dog, Top of the Rock, school bus, pompiers) |
| 0:09.9 | Vamp | 1 plan par temps (métro, Grand Central, vapeur, Times Square) |
| 0:14.3 | Fin du vamp | 1 plan par demi-temps, 8 plans en 2 s |
| 0:16.4 | « Start spreading the news » | Ferry, Grand Central, métro, water taxi |
| 0:23.0 | Réponse des cuivres | Bras ouverts devant la Statue, course et saut par-dessus la caméra → noir |
| 0:25.7 | « If I can make it there » | Jumelles de l'Empire State, vélo, gospel, Broadway |
| 0:30.3 | « I'm gonna make it anywhere » | 1 plan par temps : confettis, PSG, acrobates, Yankees, pizza |
| 0:34.5 | « It's up to you » | Lui dans l'hélico (la respiration avant l'explosion) |
| 0:37.2 | Coup d'orchestre, « New York! » | Hélico : Midtown, Downtown, la Statue vue du ciel |
| 0:41.0 | « New York! » | Central Park depuis l'hélico, Times Square sous la pluie, pont de Brooklyn |
| 0:46.0 | « New Yooork » tenu | Central Park, vélo, ferry, puis la vue panoramique sur tout l'accord final |
| 0:54.5 | Dernier coup d'orchestre | Noir (place pour ton titre) |

## Voix off (optionnelle)

Le teaser tient sans voix off : Sinatra chante presque tout du long. Si tu en ajoutes une, garde-la dans les trous du morceau :

- **0:03.4 → 0:09.5** (vamp instrumental) : « On est partis à New York… » (0:03.4) « …et on n'était pas prêts. » (0:06.7)
- **0:24.2 → 0:25.6** (pendant la course, l'orchestre se tait) : « Accroche-toi. »
- **0:54.6 → 0:56.5** (noir final) : « New York. Le vlog. Dispo maintenant. »

Une version sans la voix de Sinatra (`Teaser_NYC_sinatra-sans-voix.mp4`) est fournie si tu veux une voix off continue, mais le morceau perd beaucoup sans lui.

## Droits

L'enregistrement de Sinatra est protégé : sur YouTube, Content ID le détectera (revendication, monétisation reversée aux ayants droit, voire blocage dans certains pays). Ça vaut aussi pour la version sans voix.

## Rebuild

```bash
python3 -m demucs -n htdemucs -o stems sinatra.wav       # pistes séparées (repérage + version sans voix)
python3 tools/make_edit.py                                # écrit edit.json depuis la liste des plans
python3 tools/build.py --source "VLOG NEW YORK GOOD.mp4" --music sinatra.wav \
    --music-alt sinatra_sans_voix.wav --out renders
```

`tools/make_edit.py` porte la liste des plans en temps du morceau ; `tools/build.py` réutilise le rendu image par image de l'intro (`../vlog-new-york-intro/tools/build.py`). Sorties : les deux MP4, les musiques montées en WAV, `Teaser_NYC.edl` (CMX 3600) et `plans.tsv`.
