#!/usr/bin/env python3
"""Génère cards.json, les images des cartes et l'aide de gamefile.json depuis la bible.

Source unique : bible/03_cartes.csv (cartes des guildes) et bible/05_donjon_mine.csv (donjon).
Remplace les listes codées en dur de generate.py ; on garde son dessin de carte (draw_card).
Usage : python3 tools/from_bible.py   (depuis la racine du dépôt)
"""
import csv
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as gen  # noqa: E402  (dessin des cartes, palette, cartes communes)

ROOT = gen.ROOT
BASE = gen.BASE
BIBLE = os.path.join(ROOT, "bible")

gen.PALETTE["Mages"] = ((30, 34, 70), (130, 140, 230))
TYPES = {"Unité": "Unite", "Sort": "Sort", "Gardien": "Gardien", "Terrain": "Terrain"}


def rich(texte):
    """« Moment : effet / Moment : effet » → une ligne par effet, le moment en gras."""
    lignes = []
    for seg in texte.split(" / "):
        seg = seg.strip()
        kws = []
        for kw in ("Réflexe.", "Portée.", "Rapide.", "Protecteur.", "Éclaireur.", "Bluff.", "Jeton."):
            if seg.startswith(kw + " "):
                kws.append(f"**{kw}**")
                seg = seg[len(kw) + 1:]
        if kws:
            seg = " ".join(kws) + " " + seg
            lignes.append(seg)
            continue
        tete, sep, reste = seg.partition(" : ")
        if sep and len(tete) <= 45:
            lignes.append(f"**{tete} :** {reste}")
        elif seg.endswith(".") and len(seg) <= 20:   # mot-clé seul (« Rapide. », « Protecteur. »)
            lignes.append(f"**{seg}**")
        else:
            lignes.append(seg)
    return "\n".join(lignes)


def invoque(texte):
    t = texte.lower()
    return [j for j in ("pousse", "loup") if j in t and "jeton." not in t]


def cartes_guildes():
    out = []
    with open(os.path.join(BIBLE, "03_cartes.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            jeton = r["max"] == "jeton"
            typ = TYPES[r["type"]]
            p = int(r["P"]) if r["P"] else None
            pv = int(r["PV"]) if r["PV"] else None
            if typ == "Terrain":
                p = None  # le Terrain ne frappe pas : on affiche ses PV dans le titre de type
            c = gen.C(r["id"], r["nom"], typ, int(r["cout"] or 0), r["faction"], rich(r["texte"]),
                      p, pv, legal=False if jeton else int(r["max"]), token=jeton, tokens=invoque(r["texte"]))
            c["gardien"] = r["gardien"]
            if typ == "Terrain":
                t = c["text"]
                for niv in ("Niv. 2 :", "Niv. 3, Fief :"):
                    t = t.replace(f". {niv}", f".\n**{niv}**")
                t = t.replace("\nPinte (", "\n**Pinte** (")
                c["text"] = f"**{pv} PV.**\n" + t
                c["hp_terrain"] = pv
            out.append(c)
    return out


def cartes_donjon():
    out = []
    with open(os.path.join(BIBLE, "05_donjon_mine.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["type"] == "Relique":
                out.append(gen.C(r["id"], r["nom"], "Relique", 0, "Relique", rich(r["texte"]), legal=False, token=True))
                continue
            c = gen.C(r["id"], r["nom"], r["type"], 0, gen.MINE, rich(r["texte"]), int(r["P"]), int(r["PV"]),
                      legal=False, token=True, tresors=int(r["tresors"]), relique=r["relique"] == "oui")
            if r["evolue_nom"]:
                c["back"] = dict(name=r["evolue_nom"], power=int(r["evo_P"]), hp=int(r["evo_PV"]),
                                 tresors=int(r["evo_tresors"]), text=rich(r["evo_texte"]))
            out.append(c)
    return out


def communes():
    com = {c["id"]: c for c in gen.CARDS if c["id"] in ("energie", "carte-tresor")}
    com["carte-tresor"]["text"] = ("**Rattrapage.** Arrive à la fin de la manche 1 au Camp du joueur qui a le moins de trésors.\n"
                                   "**Retrait :** +1 trésor si tu es mené.\n"
                                   "**Raid :** un raid réussi peut la prendre à la place du 1er trésor volé.")
    return list(com.values())


def ecrire_cartes(cards_list):
    out_dir = os.path.join(ROOT, "img", "cards")
    os.makedirs(out_dir, exist_ok=True)
    cards = {}
    for c in cards_list:
        gen.draw_card(c, os.path.join(out_dir, f"{c['id']}.png"))
        img = f"{BASE}/img/cards/{c['id']}.png"
        e = {"id": c["id"], "face": {"front": {"name": {"name": c["name"]}, "type": c["type"], "cost": c["cost"], "image": img}},
             "name": c["name"], "type": c["type"], "cost": c["cost"], "faction": c["faction"]}
        if c.get("gardien"):
            e["gardien"] = c["gardien"]
        if not c["token"]:
            e["_legal"] = {"PROTO": c["legal"]}
        if c["power"] is not None:
            e["power"], e["hp"] = c["power"], c["hp"]
        elif c.get("hp_terrain"):
            e["hp"] = c["hp_terrain"]
        if c["token"]:
            e["isToken"] = True
        if c["tokens"]:
            e["tokens"] = c["tokens"]
        if c.get("back"):
            b = dict(c, **c["back"], verso=True, back=None)
            gen.draw_card(b, os.path.join(out_dir, f"{c['id']}-verso.png"))
            e["face"]["back"] = {"name": {"name": b["name"]}, "type": c["type"], "cost": 0,
                                 "image": f"{BASE}/img/cards/{c['id']}-verso.png"}
        if c.get("tresors") is not None:
            e["tresors"] = c["tresors"]
        cards[c["id"]] = e
    with open(os.path.join(ROOT, "cards.json"), "w", encoding="utf-8") as fh:
        json.dump(cards, fh, ensure_ascii=False, indent=2)
    for fn in os.listdir(out_dir):
        if fn.endswith(".png") and fn[:-4].removesuffix("-verso") not in cards:
            os.remove(os.path.join(out_dir, fn))
    return cards


# --- jetons à glisser sur les cartes (même style que format_v3) ---
JETONS_NEUFS = [
    ("Arcane", "Arcane (Mages) : jetons sur le cercle, payent les Incantations", "ARCANE", (80, 90, 190)),
    ("Mise", "Mise (Tonneau des paris) : 3 Mises = 1 trésor au Retrait", "MISE", (200, 160, 30)),
    ("Egide", "Égide : ignore le prochain coup reçu", "ÉGIDE", (90, 160, 200)),
    ("Glyphe", "Glyphe (Mages) : 1 dégât et Sonné à la 1re unité adverse qui entre ou attaque ici", "GLY|PHE", (110, 60, 180)),
]
NOMS = {  # libellés à jour des jetons existants
    "Sonne": "Sonné : ne frappe pas à son prochain combat",
    "GueuleDeBois": "Gueule de bois : Sonné jusqu'à la fin de ton prochain tour (Rhum)",
    "EnSoin": "En soin : blessé au Camp, soigné à ton prochain Repos puis reste au Camp ce tour",
    "Piege": "Piège (Éclaireur), face cachée ; Leurre possible",
}


def jeton(nom, txt, coul):
    im = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, 116, 116), fill=coul, outline=(255, 255, 255), width=5)
    lignes = txt.split("|")
    size = 40
    while size > 12:
        f = ImageFont.truetype(gen.FONT_B, size)
        if max(d.textlength(lg, font=f) for lg in lignes) <= 92 and size * 1.15 * len(lignes) <= 84:
            break
        size -= 1
    y0 = 60 - (len(lignes) - 1) * size * 0.58
    for k, lg in enumerate(lignes):
        d.text((60, y0 + k * size * 1.16), lg, font=f, fill=(255, 255, 255), anchor="mm")
    im.save(os.path.join(ROOT, "img", "tokens", f"{nom}.png"))


AIDE = [
    "Guild Rush (proto) · donjon : Mine des Gobelins. Règles complètes : livret/livret.md du dépôt.",
    "But : le plus de trésors. Fin : un joueur à 12 trésors en fin de manche, ou boss tué (fin de ce tour). Égalité : tueur du boss, puis le plus de monstres tués.",
    "Plateau : 4 salles en ligne (voisine = ±1), un monstre chacune. Face à chaque salle, une Expédition par joueur (3 unités max, jetons compris). Le Camp touche toutes tes Expéditions, sans limite ; ce n'est pas une salle.",
    "Tour : Repos (énergie au max, 3 puis +1 par manche jusqu'à 6 ; pioche 1 ; soin des unités En soin ; passif du Gardien) → Stratagème (Éclaireurs, Bluff face cachée, lever le camp) → Assaut → Retrait (trésors au compteur, niveau du Terrain).",
    "Assaut : une unité posée arrive directement dans l'Expédition voulue ou au Camp (TCG Arena la pose en Exp. 1 : glisse-la). Une unité en jeu se déplace 1 fois par tour (Expédition voisine, Camp, ou du Camp vers n'importe quelle Expédition). Blessée : seulement vers le Camp (En soin).",
    "Combat (optionnel), salle par salle : Duel (annonce-le dans le chat ; l'adversaire répond d'abord, puis Réflexe / bonus de Terrain / passe ; 2 passes = frappes). Puis le monstre frappe 1 attaquant choisi par l'adversaire, tes attaquants frappent ensemble, puis (Mêlée) les unités adverses. 1 frappe par unité et par tour.",
    "Coup de grâce : le tueur (contrôleur du dernier dégât) prend tous les trésors et la relique. Repli : après une Mêlée perdue, tes unités qui ont attaqué peuvent rentrer au Camp. Un sort se lance dans une salle où tu as une unité (Portée : ou voisine).",
    "Raid (dès la manche 2, 1 par Assaut) : après un kill dans une salle, tes unités de cette salle attaquent le Camp adverse. Réussi si plus de raiders que de défenseurs debout (Gardien compris) : 1 trésor volé, +1 si le Gardien est Assommé.",
    "Monstre tué : l'hôte le met dans « Monstres vaincus », le tueur ajoute ses trésors (pastille dorée) à son compteur. Icône Relique : « Prendre la relique » dans le panneau Donjon. Automatique : salles vides remplies au début de chaque tour ; évolution en fin de manche.",
    "Terrain : commence à côté du Gardien, glisse-le dans une Expédition à ton 1er Assaut. Niv 1 à la pose, +1 au Retrait s'il n'a pas bougé (3 max, niv. 3 = Fief). Lever le camp : Expédition voisine, -1 niveau. Détruit par l'adversaire : +1 trésor pour lui (pillage), revient au niv. 1 à ton Assaut suivant.",
    "Compteur = Trésors. PV et Puissance : compteurs de la carte (clic droit > Toggle counter 1 = PV, touche C ; counter 2 = Puissance, Ctrl C). Jetons : Sève, Arcane, Mise, Niveau 1-3, états (Sonné, Empoisonné, Rapide, Insensible, Ivre, Gueule de bois, Contrecoup, Entravé, En soin, Égide, Piège, Glyphe).",
    "Deck : 1 Gardien + 1 Terrain de sa faction + 30 cartes de la faction, dont 20 min. du pool du Gardien (3 ex. max, Signature 1). TCG Arena ne vérifie pas la règle des 20.",
    "Jetons Pousse et Loup : clic droit sur la carte qui les invoque.",
]


def maj_gamefile():
    p = os.path.join(ROOT, "gamefile.json")
    g = json.load(open(p, encoding="utf-8"))
    G = g["gameplay"]["Standard"]
    toks = [t for t in G["draggableTokens"] if t["id"] not in {j[0] for j in JETONS_NEUFS}]
    for t in toks:
        t["name"] = NOMS.get(t["id"], t["name"])
    for tid, nom, txt, coul in JETONS_NEUFS:
        jeton(tid.lower(), txt, coul)
        toks.append({"id": tid, "name": nom, "image": f"{BASE}/img/tokens/{tid.lower()}.png"})
    G["draggableTokens"] = toks
    g["customHelp"] = "\n".join(AIDE)
    if "gardien" not in g["deckBuilding"]["mainFilters"]:
        g["deckBuilding"]["mainFilters"].insert(1, "gardien")
    json.dump(g, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def verifier_decks(cards):
    """Signale les decks de decks.json qui ne respectent plus la règle de deck de la bible."""
    for d in json.load(open(os.path.join(ROOT, "decks.json"), encoding="utf-8")):
        L = d["deckList"]
        g = L["Gardien"][0]["id"]
        main = [e for k in ("Unite", "Sort") for e in L.get(k, [])]
        manq = [e["id"] for e in main + L["Terrain"] if e["id"] not in cards]
        pool = sum(e["count"] for e in main if cards.get(e["id"], {}).get("gardien") == g)
        if manq or pool < 20:
            print(f"  ! {d['id']} : {pool} cartes du pool de {g} (20 min.)" + (f", cartes inconnues {manq}" if manq else ""))


def main():
    cards = ecrire_cartes(cartes_guildes() + cartes_donjon() + communes())
    maj_gamefile()
    print(len(cards), "cartes")
    verifier_decks(cards)


if __name__ == "__main__":
    main()
