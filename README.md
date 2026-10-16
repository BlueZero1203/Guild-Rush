# Guild Rush

TCG 1v1 : deux guildes se disputent les trésors d'un même donjon. Prototype jouable sur TCG Arena.

- **Règles** : [`livret/livret.md`](livret/livret.md) (version mise en page : `livret/livret.html`).
- **Decks préconstruits** : [`livret/decks.md`](livret/decks.md), générés par `tools/decks.py` (un par Gardien).
- **Bible** (source de vérité) : [`bible/`](bible/) — glossaire, règles core, factions, cartes (`03_cartes.csv`), journal des décisions, donjon (`05_donjon_mine.csv`).
- **TCG Arena** : `gamefile.json` (à importer), `cards.json`, `decks.json` et `img/` sont lus depuis la branche `main`.

## Mettre à jour les cartes

Après une modif de `bible/03_cartes.csv` ou `bible/05_donjon_mine.csv` :

```
python3 tools/from_bible.py
```

Le script régénère `cards.json`, les images des cartes, les jetons et l'aide de `gamefile.json`, puis signale les decks de `decks.json` qui ne respectent plus la règle de deck. Les anciens scripts (`generate.py`, `board_layout.py`, `format_v2.py`, `format_v3.py`) restent pour l'historique du plateau ; `generate.py` fournit le dessin des cartes.
