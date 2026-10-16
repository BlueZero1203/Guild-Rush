#!/usr/bin/env python3
"""Decks préconstruits : un par Gardien (1 Gardien + son Terrain + 30 cartes, 20 min. de son pool).

Usage : python3 tools/decks.py   (après tools/from_bible.py, qui écrit cards.json)
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# id, titre, Gardien, Terrain, {carte: exemplaires}
DECKS = [
    ("precon-guss", "Ivrognes de Guss — La Taverne", "guss", "baril-chene", {
        "gamin": 2, "contrebandier": 2, "barde": 2, "poker": 2, "porteur": 2, "serveuse": 3,
        "soldat-ivre": 3, "sentinelle-ivre": 2, "brute": 2, "cuisinier": 2,
        "grosse-pinte": 3, "jet-chaises": 3, "ma-tournee": 1, "videur": 1}),
    ("precon-rosa", "Ivrognes de Rosa — Poudrière", "rosa", "baril-explosif", {
        "habitue": 3, "garcon-cave": 2, "tonnelier": 2, "pilier": 2, "cracheur": 3, "videur": 2,
        "gardienne-fut": 2, "videuse-chef": 2, "champion": 1, "ours": 1,
        "roule-baril": 2, "viree-bar": 1, "fermeture": 2, "jet-chaises": 2, "serveuse": 2, "grosse-pinte": 1}),
    ("precon-robin", "Ivrognes de Robin — Tapis vert", "robin", "tonneau-paris", {
        "parieur": 3, "pickpocket": 2, "lanceuse": 3, "credit": 2, "tricheur": 2, "croupier": 2,
        "mercenaire": 2, "duelliste": 2, "flambeur": 2, "gagnant": 1,
        "double-rien": 3, "coup-monte": 2, "tapis": 2, "jet-chaises": 2}),
    ("precon-cernun", "Druides de Cernun — Bosquet ancien", "cernun", "bosquet", {
        "chouette": 2, "lutin": 3, "semeuse": 2, "chamane": 2, "cueilleuse": 2, "herboriste": 2,
        "greffeur": 2, "ours-clairiere": 2, "vieux-chene": 2, "cerf": 2,
        "croissance": 3, "recolte": 2, "eveil-foret": 1, "dryade": 2, "lianes": 1}),
    ("precon-belladone", "Druides de Belladone — Ronces", "belladone", "bosquet-poison", {
        "crapaud": 2, "araignee-ronces": 2, "pisteuse": 2, "dryade": 2, "invocateur": 2, "ronce-garde": 2,
        "mur-ronces": 2, "saule": 2, "sorciere": 2, "mandragore": 2,
        "lianes": 3, "spores": 2, "enchevetrement": 2, "lutin": 2, "croissance": 1}),
    ("precon-sylve", "Druides de Sylve — La Meute", "sylve", "bosquet-ombre", {
        "renard": 2, "louveteau": 3, "faucon": 2, "chasseresse": 3, "lynx": 2, "meneuse": 3,
        "sanglier": 2, "loup-alpha": 2, "ours-enrage": 1, "loup-blanc": 1,
        "appel-meute": 3, "hallali": 2, "transplantation": 1, "croissance": 2, "lutin": 1}),
    ("precon-soffia", "Mages de Soffia — Arcanes", "soffia", "cercle", {
        "apprenti": 3, "bibliothecaire": 2, "adepte": 2, "etudiante": 2, "garde-tour": 2, "familier": 2,
        "enchanteur": 2, "mage-bataille": 2, "mage-errant": 2, "sentinelle-cristal": 1,
        "projectile": 3, "dissipation": 2, "convergence": 1, "trait-feu": 2, "bouclier-runique": 2}),
    ("precon-orsin", "Mages d'Orsin — Runes", "orsin", "sanctuaire", {
        "scribe": 3, "veilleur": 2, "graveur": 2, "acolyte": 2, "sentinelle-runique": 3, "tisseuse": 2,
        "portier": 2, "statue": 1, "maitre-glyphes": 2, "colosse": 1,
        "bouclier-runique": 3, "repulsion": 2, "citadelle": 1, "projectile": 2, "mage-bataille": 2}),
    ("precon-ignis", "Mages d'Ignis — Brasier", "ignis", "foyer", {
        "feu-follet": 2, "novice-feu": 3, "jongleur": 2, "salamandre": 2, "pyromane": 2, "embraseuse": 2,
        "elementaire": 2, "mage-cendres": 2, "phenix": 2, "incarnation": 1,
        "trait-feu": 3, "boule-feu": 2, "meteore": 1, "projectile": 3, "dissipation": 1}),
]


def main():
    cards = json.load(open(os.path.join(ROOT, "cards.json"), encoding="utf-8"))
    out = []
    for did, title, gardien, terrain, liste in DECKS:
        fac = cards[gardien]["faction"]
        assert cards[terrain]["type"] == "Terrain" and cards[terrain]["faction"] == fac, did
        for cid, n in liste.items():
            c = cards[cid]
            assert c["faction"] == fac and c["type"] in ("Unite", "Sort"), (did, cid)
            assert n <= c["_legal"]["PROTO"], (did, cid, "max")
        total = sum(liste.values())
        pool = sum(n for cid, n in liste.items() if cards[cid].get("gardien") == gardien)
        assert total == 30 and pool >= 20, (did, total, pool)
        L = {"categoriesOrder": ["Gardien", "Terrain", "Unite", "Sort"],
             "Gardien": [{"id": gardien, "count": 1}], "Terrain": [{"id": terrain, "count": 1}],
             "Unite": [{"id": k, "count": v} for k, v in liste.items() if cards[k]["type"] == "Unite"],
             "Sort": [{"id": k, "count": v} for k, v in liste.items() if cards[k]["type"] == "Sort"],
             "Sideboard": [], "_maybeboard": []}
        out.append({"id": did, "title": title, "format": "Proto (cartes de test)", "deckList": L})
        print(f"{did}: 30 cartes, {pool} du pool")
    json.dump(out, open(os.path.join(ROOT, "decks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
