# Guild Rush

TCG 1v1 : deux guildes se disputent les trésors d'un même donjon. Prototype jouable sur TCG Arena.

- **Règles** : [`livret/livret.md`](livret/livret.md) (version mise en page : `livret/livret.html`). En anglais : [`livret/en/`](livret/en/).
- **Decks préconstruits** : [`livret/decks.md`](livret/decks.md), générés par `tools/decks.py` (un par Gardien).
- **Bible** (source de vérité) : [`bible/`](bible/) — glossaire, règles core, factions, cartes (`03_cartes.csv`), journal des décisions, donjon (`05_donjon_mine.csv`).
- **TCG Arena** : `gamefile.json` (à importer), `cards.json`, `decks.json` et `img/` sont lus depuis la branche `main`.

## Mettre à jour les cartes

Après une modif de `bible/03_cartes.csv` ou `bible/05_donjon_mine.csv` :

```
python3 tools/from_bible.py
```

Le script régénère `cards.json`, les images des cartes, les jetons et l'aide de `gamefile.json`, puis signale les decks de `decks.json` qui ne respectent plus la règle de deck.

Les définitions des mots-clés et états viennent de `bible/00_glossaire.md` : chaque carte rappelle en petit, sous son texte, ceux qu'elle utilise (s'il reste de la place), et l'aide de `gamefile.json` (menu Help) contient le lexique complet. Après une modif du glossaire, relancer le script. Les anciens scripts (`generate.py`, `board_layout.py`, `format_v2.py`, `format_v3.py`) restent pour l'historique du plateau ; `generate.py` fournit le dessin des cartes.

## Français / anglais

Un seul jeu dans TCG Arena : chaque joueur choisit sa langue dans **Options** (English / Français), et un joueur FR peut affronter un joueur EN. Chaque carte existe en deux images (`img/cards/<id>.png` et `<id>-en.png`) ; `cards.json` donne le nom et l'image par langue, `translations.json` traduit l'aide, les types, les zones et les jetons.

La bible française fait foi. Les textes anglais sont dans [`bible/en/`](bible/en/) : `03_cartes_en.csv` et `05_donjon_mine_en.csv` (chaque ligne garde le texte français qu'elle traduit, colonnes `fr_…`), `00_glossaire_en.md` (empreinte du glossaire français en tête). Quand une carte française change, `from_bible.py` la signale « à retraduire » et l'affiche en français dans la version anglaise en attendant ; on corrige la ligne anglaise (texte et colonnes `fr_…`) puis on relance le script. L'aide anglaise est dans `AIDE_EN` (`tools/from_bible.py`), à côté de l'aide française.
