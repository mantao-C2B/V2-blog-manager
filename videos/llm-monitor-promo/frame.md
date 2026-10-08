---
name: LLM Monitor — charte vidéo
status: official
source: "references/Guide_Logo_LLM_Monitor.pdf (v1.0, sept. 2026) + references/screens_site_demo.pdf (home page et démo produit)"
colors:
  ink: "#0E1A17"            # Encre — nom du logo, texte principal sur clair
  green: "#117D67"          # Vert produit — picto sur clair, accents et boutons sur clair
  mint: "#2EBE9B"           # Vert menthe — uniquement sur fond sombre, jamais sur blanc
  white: "#FFFFFF"
  sable: "#ECEEEB"          # fond autorisé du logo, fond de l'app
  canvas: "#F5F6F3"         # toile claire de la vidéo (sable éclairci)
  line: "#E1E5E0"
  ink-soft: "#4E5A56"
  ink-faint: "#8B9692"
  mint-soft: "#E4F3EE"      # pilules et lignes surlignées sur clair (app)
  navy-900: "#15223A"       # fonds sombres du site (hero, footer)
  navy-800: "#1E3149"
  teal-600: "#3F7F76"       # fin du dégradé du hero
  coral: "#D9785F"          # point de vigilance, score faible (app)
  coral-soft: "#FBEAE5"
typography:
  display: { family: "Instrument Serif", weights: [400], usage: "grandes phrases d'émotion, comme le hero du site" }
  title: { family: "Sora", weights: [600], tracking: "-0.035em", usage: "nom du logo et titres uniquement" }
  body: { family: "Instrument Sans", weights: [400, 500, 600], usage: "texte courant, interfaces" }
  data: { family: "IBM Plex Mono", weights: [400, 500], usage: "libellés techniques en capitales espacées, chiffres, mentions" }
logo:
  symbol: '<rect x="20" y="20" width="60" height="60" rx="8" transform="rotate(45 50 50)" stroke-width="7.2" stroke-linecap="round" stroke-dasharray="34.6 21.885" stroke-dashoffset="-4.7"/> + <circle cx="50" cy="50" r="10.6"/> (viewBox 0 0 100 100)'
  lockup: "gap 0.22 X, nom Sora 600 à 0.58 X, approche -0.035em, symbole centré sur la hauteur de capitale, zone de protection 0.5 X"
  on-light: "picto #117D67, nom #0E1A17"
  on-dark: "picto #2EBE9B, nom #FFFFFF"
  animation: "symbole seul : quarts de tour cubic-bezier(.7,0,.3,1) + pupille qui respire ; balayage (dashoffset -4.7 → -61.185) ; tracé (dasharray 2 54.485 → 34.6 21.885)"
  never: "étirer, recolorer, faire tourner le lockup, ombre, contour, dégradé, retaper le nom dans une autre police"
components:
  card-light: "blanc, rayon 24px, bordure 2px #E1E5E0, ombre douce 0 30px 70px rgba(14,26,23,0.10)"
  card-glass: "sur sombre : fond rgba(255,255,255,0.07), bordure 2px rgba(255,255,255,0.14), rayon 28px, reflet haut"
  label: "IBM Plex Mono 500, capitales, interlettrage 0.08em, #8B9692 sur clair / rgba(255,255,255,0.6) sur sombre"
  highlight-row: "fond #E4F3EE, filet gauche 4px #117D67, nom en #117D67 + badge VOTRE MARQUE"
---

## Overview

Deux mondes, comme le site : le monde de la marque, sombre (dégradé navy → vert sarcelle du hero, verre dépoli, accents menthe), et le monde du produit, clair (toile sable claire, cartes blanches nettes, libellés mono, vert produit). On bascule de l'un à l'autre par la pupille du logo, qui s'ouvre ou se referme comme un iris.

## The Frame

- Un message principal par plan. Peu de texte, contrastes forts.
- Les grandes phrases d'émotion en Instrument Serif (comme « Pilotez votre visibilité dans les IA. ») ; les titres de chapitre en Sora 600 ; les interfaces en Instrument Sans ; les libellés et chiffres techniques en IBM Plex Mono.
- La mire (le symbole) est l'outil de mise au point du film : elle se verrouille sur ce qui compte, puis la caméra plonge dedans.
- Zone sous-titres réservée en bas (y ≥ 960 px) : aucun contenu clé dedans.
- Toutes les données sont des exemples fictifs, signalés par une pastille « EXEMPLE FICTIF ».

## Do / Don't

- Do : menthe seulement sur sombre, vert produit sur clair ; mouvements de caméra fluides ; chiffres qui comptent puis se figent pour la lecture.
- Don't : effets gadgets (glitch, flare), logo tourné/ombré/recoloré, menthe sur blanc, plus d'une police expressive par plan.
