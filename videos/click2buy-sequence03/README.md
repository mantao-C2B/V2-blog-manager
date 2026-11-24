# Click2Buy — invitation Tech4Retail (9:16)

Montage de « Sequence 03 » (23 s, face caméra) : invitation au salon Tech4Retail avec LLM Monitor, stand V19.
Fait avec le modèle `../_modele-montage-9x16/` (marque `click2buy`, voir son `README.md`).

- Sous-titres sur une ligne en Poppins, blanc sans contour ; mots clés surlignés en orange BUY #E95531
  (Tech4Retail, LLM Monitor, innovations, IA, invitations, V19).
- Un plan par phrase, cadrages alternés (100 / 112 / 115 %) et zoom lent.
- Pas de musique : voix nettoyée, puis fondu blanc vers l'outro Click2Buy et ses effets sonores.
- Rendu : `renders/Click2Buy_Tech4Retail_9x16.mp4` (non versionné). Rushes : `../_sources/c2b-sequence03/raw.mp4`.

Interface de montage : `editor/index.html` publiée comme artefact (sous-titres, coupes et zooms, style,
orange du surlignage, outro ; export MP4 dans le navigateur).

```bash
bash tools/prepare.sh ../_sources/c2b-sequence03/raw.mp4
python3 tools/make_edit.py && python3 tools/build.py
bash tools/render_all.sh
python3 tools/make_editor.py
```
