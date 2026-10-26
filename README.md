# Contourage

Visionneuse et éditeur de contours pour un scanner tête et cou, avec les volumes cibles anatomocliniques (CTV) :

- **CTV tumoraux** : « CTV structures » péritumoraux de Lapeyre M. et al. (GORTEC), *Cancer/Radiothérapie* 2005;9:261–270 — 25 structures (cavité buccale et oropharynx, espaces profonds, base du crâne).
- **CTV ganglionnaires** : niveaux de Grégoire V. et al., *Radiotherapy and Oncology* 2014;110:172–181 (consensus DAHANCA, EORTC, HKNPCSG, NCIC CTG, NCRI, RTOG, TROG) — niveaux Ia, Ib, II, III, V, VIa, VIb (partiel), VIIa, VIIb, VIII, IX, Xa, Xb.

Les CTV sont tracés du côté gauche du patient (droite de l'image) ; l'appli en crée au chargement une copie en miroir pour le côté droit (suffixe `_d`), par symétrie autour de la ligne médiane située entre x = 109 et x = 110. Les structures médianes (Ia, VIa, VIb, palais dur, sinus sphénoïdal, voile) ne sont pas dupliquées.

> Contours indicatifs, à visée pédagogique et de recherche. Ils ne sont pas validés cliniquement et ne doivent pas servir à planifier un traitement.

## Utilisation

Ouvrir `index.html` via un serveur web (les fichiers de `data/` sont chargés par `fetch`, ce qui ne fonctionne pas en ouvrant le fichier directement depuis le disque) :

```bash
python3 -m http.server 8000
# puis http://localhost:8000
```

L'appli peut aussi être servie par GitHub Pages depuis la racine du dépôt.

- Trois vues liées (axiale, coronale, sagittale), défilement à la molette, fenêtrages abdominal (W 400 / L 40), tissus mous, os et large.
- Liste des structures par groupe (tumoraux / ganglionnaires) ; cliquer sur un nom centre les vues sur la structure.
- **Mode édition** : pinceau et gomme (rayon 1–12 mm), option pour ne pas peindre l'air ni l'os, copie de la coupe voisine, vider la coupe, effacer toute la structure (avec confirmation), annulation (Ctrl+Z), retour au contour initial. Raccourcis : P pinceau, G gomme, `[` et `]` rayon.
- **Volumes composites** : l'URL peut demander la somme de plusieurs sous-CTV, affichée en tête de liste. C'est ainsi que *RCP ORL de poche* ouvre la visionneuse pour un cas :

  ```
  index.html?cas=Oropharynx · T1 N1 · côté gauche&ctv_t_br=amygdale_g,pilier_ant_g&ctv_n_br=n_II_g,n_III_g
  ```

  `ctv_t_br` (CTV T bas risque, en rouge) et `ctv_n_br` (CTV N bas risque, en cyan) listent des identifiants de structures suivis de `_g` ou `_d` pour le côté (sans suffixe pour une structure médiane). Sans paramètre, l'atlas complet est affiché. Un sous-CTV encore vide est signalé « à contourer » dans le bandeau du cas.
- Les contours modifiés sont gardés dans le navigateur (`localStorage`). **Exporter les contours** produit un fichier JSON réimportable avec **Importer…**.

## Données

| Fichier | Contenu |
|---|---|
| `data/ct.txt` | Volume CT du patient 123, recadré à 230 × 224 × 64 voxels de 1 × 1 × 3 mm, uint8 encodé en base64, ordre x puis y puis z (orientation LPS : x vers la gauche du patient, y vers l'arrière, z vers le haut). |
| `data/ctv.json` | Dimensions, espacement et, pour chaque structure, groupe, nom, couleur, boîte englobante `[x0,x1,y0,y1,z0,z1]` et masque binaire empaqueté (bits, ordre little-endian, base64). |
| `data/ctv_a_contourer.json` | Structures citées par les recommandations de *RCP ORL de poche* mais absentes de l'atlas (larynx, hypopharynx, sinus, fosses nasales, lèvre, parotide…) : créées vides, des deux côtés sauf si `median`, à contourer avec le mode édition. Fichier séparé pour ne pas être écrasé par `scripts/export.py`. |
| `data/contours_reference.json` | Contours de référence corrigés manuellement dans la visionneuse (export « Exporter les contours »). Ils remplacent au chargement les contours de l'atlas, leurs copies en miroir et les structures vides ; « Revenir au contour initial » ramène à ces contours. Pour les mettre à jour, remplacer ce fichier par un nouvel export. |

Les intensités du jeu source sont normalisées sur 0–255 et non en unités Hounsfield. Les valeurs HU affichées sont estimées par une correspondance linéaire calibrée sur la graisse et les tissus mous : `HU ≈ -100 + 26,4 × (v - 71)`.

Le champ s'arrête au cartilage cricoïde : les niveaux IVa, IVb et Vc sont hors champ, et seul le début de VIb est visible.

## Scripts

Les contours initiaux ont été tracés sur des coupes clés puis interpolés (interpolation de forme par cartes de distance signée), avec exclusion de l'air et de l'os selon la structure.

- `scripts/structs.py` — définition des structures : polygones sur coupes clés, mode d'exclusion, exclusions entre niveaux.
- `scripts/build.py` — génération des masques (`python3 scripts/build.py ct.nii.gz out/`).
- `scripts/export.py` — export vers `data/` (`python3 scripts/export.py ct.nii.gz out/ data/`).
- `scripts/overlay.py` — images de contrôle des contours sur des coupes données.
- `scripts/inspect.py` — dimensions et intensités d'un dossier de volumes NIfTI.

Dépendances : `numpy`, `scipy`, `scikit-image`, `nibabel`, `matplotlib`.

## Crédits et licence des données

Images : « Head Neck CBCT CT datasets », Huazhong University of Science and Technology, Zenodo, 2024, [doi:10.5281/zenodo.13231287](https://doi.org/10.5281/zenodo.13231287), licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Les images ont été modifiées : recadrage, réencodage et superposition de contours.

Les atlas de référence (Lapeyre 2005, Grégoire 2014) ne sont pas inclus dans ce dépôt ; seules leurs références sont citées.
