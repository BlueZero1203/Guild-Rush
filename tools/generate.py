#!/usr/bin/env python3
"""Génère cards.json et les images des cartes pour TCG Arena (proto Guild Rush).

Usage : python3 tools/generate.py   (depuis la racine du dépôt)
Les URL d'images pointent vers le dépôt GitHub (raw.githubusercontent.com).
"""
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://raw.githubusercontent.com/BlueZero1203/Guild-Rush/" + os.environ.get("GR_REF", "main")
W, H = 500, 700
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


# Couleurs (fond, cadre) par famille de carte
PALETTE = {
    "Ivrognes": ((62, 40, 22), (214, 150, 60)),
    "Druides": ((24, 52, 30), (120, 190, 90)),
    "Test": ((34, 44, 60), (110, 130, 160)),
    "Monstre": ((80, 30, 30), (190, 70, 60)),
    "Boss": ((55, 15, 15), (225, 60, 40)),
    "Relique": ((70, 58, 22), (225, 190, 70)),
    "Energie": ((18, 55, 66), (70, 195, 210)),
}
TYPE_LABEL = {"Gardien": "Gardien", "Unite": "Unité", "Sort": "Sort", "Baril": "Baril",
              "Monstre": "Monstre", "Boss": "Boss", "Relique": "Relique", "Tresor": "Trésor",
              "Energie": "Énergie", "Alcool": "Alcool",
              "Ingredient": "Ingrédient", "Recettes": "Recettes"}


def C(id, name, type, cost, faction, text="", power=None, hp=None, legal=3, token=False, tokens=None,
      tresors=None, relique=False, back=None):
    return dict(id=id, name=name, type=type, cost=cost, faction=faction, text=text,
                power=power, hp=hp, legal=legal, token=token, tokens=tokens or [],
                tresors=tresors, relique=relique, back=back)


IVR = "Ivrognes"
DRU = "Druides"
CARDS = [
    # --- Ivrognes : Guss et son baril ---
    C("guss", "Guss le tavernier", "Gardien", 0, IVR,
      "**Maître de guilde** : à chaque tour, si le baril est endommagé, Guss le soigne complètement. "
      "**Patron du bar** : quand Guss défend le Camp, tes défenseurs ont +1 Puissance. "
      "**Coup de torchon** : la première unité qui attaque Guss pendant un raid est Sonnée.",
      3, 7, legal=1, tokens=["baril-chene"]),
    # --- Ivrognes : unités ---
    C("habitue", "Habitué du bar", "Unite", 1, IVR, "**Près du baril** : +1 PV.", 1, 2),
    C("serveuse", "Serveuse", "Unite", 2, IVR, "**Arrivée** : une de tes unités gagne +1/+1.", 1, 3),
    C("poker", "Joueurs de poker", "Unite", 2, IVR,
      "**Bluff** : se pose face cachée dans une salle au Midi, révélés au Crépuscule.", 2, 2),
    C("porteur", "Porteur de tonneaux", "Unite", 2, IVR,
      "**Arrivée** : déplace ton baril dans la salle de cette unité.", 2, 2),
    C("barde", "Barde éméché", "Unite", 2, IVR, "Tes autres unités de sa salle ont +1 Puissance.", 1, 2),
    C("soldat-ivre", "Soldat ivre", "Unite", 3, IVR, "Il a bu, il cogne.", 4, 4),
    C("videur", "Videur", "Unite", 3, IVR,
      "**Protecteur**. Peut défendre le Camp même s'il est en salle.", 2, 5),
    C("cracheur", "Cracheur de feu", "Unite", 3, IVR,
      "**Arrivée, près du baril** : 1 dégât à chaque ennemi de la salle.", 2, 3),
    C("brute", "Brute de taverne", "Unite", 4, IVR,
      "**Arrivée** : Sonne une unité ou un monstre de sa salle.", 4, 4),
    C("champion", "Champion de bras de fer", "Unite", 5, IVR,
      "**Près du baril** : +2 Puissance et ne peut pas être Sonné.", 5, 6),
    # --- Ivrognes : sorts ---
    C("grosse-pinte", "Grosse pinte", "Sort", 1, IVR, "Une unité gagne +2/+2 jusqu'à la fin du tour."),
    C("jet-chaises", "Jet de chaises", "Sort", 2, IVR, "2 dégâts à une cible, qui est Sonnée."),
    C("roule-baril", "Roulé de baril", "Sort", 2, IVR,
      "Déplace ton baril vers une autre salle, puis 2 dégâts à chaque ennemi de la salle d'arrivée."),
    C("viree-bar", "Virée du bar", "Sort", 3, IVR,
      "Expulse une unité adverse d'une salle : elle retourne au Camp, Sonnée."),
    C("ma-tournee", "C'EST MA TOURNÉE !", "Sort", 5, IVR,
      "Toutes tes unités en jeu sont soignées et gagnent +1/+1 jusqu'à la fin du tour. "
      "Tes blessées du Camp reviennent en Expédition. +1 Puissance de plus si ton baril est intact. "
      "**Signature** : 1 exemplaire max.", legal=1),
    # --- Ivrognes : la Cave (Réserve de faction) ---
    C("biere", "Bière blonde", "Alcool", 0, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat ; **Mélange** : 2 alcools = Sonnée au prochain combat). +1 Puissance.", legal=3),
    C("cidre", "Cidre", "Alcool", 0, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat ; **Mélange** : 2 alcools = Sonnée au prochain combat). +1 PV.", legal=2),
    C("hydromel", "Hydromel", "Alcool", 1, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat ; **Mélange** : 2 alcools = Sonnée au prochain combat). +2 PV et soigne 2 PV en s'attachant.", legal=2),
    C("rhum", "Rhum", "Alcool", 1, IVR,
      "**Alcool** (sur ton unité dans la salle du baril, même en combat ; **Mélange** : 2 alcools = Sonnée au prochain combat). +2 Puissance. **Gueule de bois** : à la Nuit, l'unité est Sonnée pour le tour suivant.", legal=1),
    C("whisky", "Whisky tourbé", "Alcool", 1, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat ; **Mélange** : 2 alcools = Sonnée au prochain combat). L'unité ne peut pas être Sonnée.", legal=1),
    C("vin-chaud", "Vin chaud", "Alcool", 1, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat ; **Mélange** : 2 alcools = Sonnée au prochain combat). Soigne complètement l'unité en s'attachant.", legal=1),
    C("absinthe", "Absinthe", "Alcool", 1, IVR,
      "**Alcool** (sur ton unité dans la salle du baril, même en combat ; **Mélange** : 2 alcools = Sonnée au prochain combat). +3 Puissance. Au début de ton tour suivant, l'unité perd 2 PV.", legal=1),
    C("liqueur-feu", "Liqueur de feu", "Alcool", 1, IVR,
      "**Alcool** (sur ton unité dans la salle du baril, même en combat ; **Mélange** : 2 alcools = Sonnée au prochain combat). Quand l'unité meurt : 2 dégâts à chaque ennemi de sa salle.", legal=1),
    # --- Druides : Cernun et son livre ---
    C("cernun", "Cernun", "Gardien", 0, DRU,
      "**Maître de guilde** : à chaque Aube, **Cueillette** : pioche 3 ingrédients du Garde-manger, "
      "garde-en 2 sous Cernun (panier de 4 max), remets le 3e dans le Garde-manger et mélange. Chaque monstre tué par tes unités : "
      "+1 ingrédient. **Cuisine** : au début du Crépuscule, 1 recette du Livre. "
      "**Bosquet** : quand Cernun défend le Camp, invoque 2 Pousses qui défendent avec lui.",
      2, 7, legal=1, tokens=["livre-ancien", "pousse"]),
    # --- Druides : le Garde-manger (Réserve de faction) ---
    C("champignon", "Champignon", "Ingredient", 0, DRU, "**Ingrédient**. Seul, il ne fait rien : il se cuisine avec le Livre de recettes."),
    C("baies", "Baies", "Ingredient", 0, DRU, "**Ingrédient**. Seules, elles ne font rien : elles se cuisinent avec le Livre de recettes."),
    C("racine", "Racine", "Ingredient", 0, DRU, "**Ingrédient**. Seule, elle ne fait rien : elle se cuisine avec le Livre de recettes."),
    C("miel", "Miel", "Ingredient", 0, DRU, "**Ingrédient**. Seul, il ne fait rien : il se cuisine avec le Livre de recettes."),
    C("herbes", "Herbes", "Ingredient", 0, DRU, "**Ingrédient**. Seules, elles ne font rien : elles se cuisinent avec le Livre de recettes."),
    # --- Druides : unités ---
    C("lutin", "Lutin des mousses", "Unite", 1, DRU, "**Arrivée** : invoque une Pousse (1/1) à côté de lui.", 1, 1, tokens=["pousse"]),
    C("chouette", "Chouette guetteuse", "Unite", 1, DRU,
      "**Arrivée** : pioche 2 ingrédients, garde-en 1 dans ton panier, remets l'autre et mélange le Garde-manger.", 1, 2),
    C("cueilleuse", "Cueilleuse", "Unite", 2, DRU,
      "**Nuit** : si elle est dans une salle, pioche 1 ingrédient (dans ton panier).", 1, 3),
    C("invocateur", "Invocateur de la clairière", "Unite", 2, DRU,
      "**Combat** : invoque une Pousse dans sa salle.", 0, 3, tokens=["pousse"]),
    C("chamane", "Chamane des racines", "Unite", 2, DRU,
      "**Combat** : tes autres unités de sa salle ont +1 Puissance.", 0, 4),
    C("dryade", "Dryade fleurie", "Unite", 2, DRU,
      "**Dernier souffle** : invoque 2 Pousses à sa place.", 1, 2, tokens=["pousse"]),
    C("meneuse", "Meneuse de loups", "Unite", 3, DRU, "**Arrivée** : invoque un Loup (2/1).", 2, 3, tokens=["loup"]),
    C("saule", "Esprit du saule", "Unite", 3, DRU,
      "**Protecteur**. Quand une de tes autres unités de sa salle meurt, invoque une Pousse.", 1, 5, tokens=["pousse"]),
    C("sanglier", "Sanglier furieux", "Unite", 3, DRU, "**Rapide**.", 3, 3),
    C("vieux-chene", "Vieux chêne", "Unite", 4, DRU, "Tes Pousses et tes Loups de sa salle ont +1/+1.", 3, 6),
    # --- Druides : sorts ---
    C("lianes", "Lianes", "Sort", 1, DRU, "**Rapide**. Une unité ou un monstre est Sonné."),
    C("croissance", "Croissance soudaine", "Sort", 1, DRU, "**Rapide**. Une de tes unités gagne +2/+2 jusqu'à la fin du tour."),
    C("appel-meute", "Appel de la meute", "Sort", 2, DRU,
      "Invoque 2 Loups (2/1), chacun dans une salle où tu as une unité.", tokens=["loup"]),
    C("spores", "Pluie de spores", "Sort", 3, DRU,
      "1 dégât à chaque ennemi d'une salle (unités adverses et monstre). Invoque une Pousse par ennemi tué.",
      tokens=["pousse"]),
    C("eveil-foret", "Éveil de la forêt", "Sort", 5, DRU,
      "Invoque une Pousse dans chaque salle. Toutes tes unités gagnent +1/+1 jusqu'à la fin du tour. "
      "Pioche 1 ingrédient. **Signature** : 1 exemplaire max.", legal=1, tokens=["pousse"]),
    # --- Druides : jetons ---
    C("pousse", "Pousse", "Unite", 0, DRU, "**Jeton** (esprit de la forêt). Compte dans la limite de 3 unités par salle.",
      1, 1, legal=False, token=True),
    C("loup", "Loup", "Unite", 0, DRU, "**Jeton** (bête). Compte dans la limite de 3 unités par salle.",
      2, 1, legal=False, token=True),
    # --- Communes ---
    C("carte-tresor", "Carte au trésor", "Tresor", 0, "Relique",
      "Option de comeback (à tester). +1 trésor à chaque Retrait de son porteur. Gardée au Camp, volable par raid.", legal=False, token=True),
    C("energie", "Énergie", "Energie", 0, "Energie",
      "Incline-la pour payer 1.\nToutes se redressent à ton Repos.\nMax : 3 à la manche 1, +1 par manche, 6 au plus.", legal=False, token=True),
]


# --- Gardiens supplémentaires et fiches (jetons, pas dans les decks) ---
CARDS += [
    C("rosa", "Rosa la brasseuse", "Gardien", 0, IVR, "", 3, 6, legal=1, tokens=["baril-explosif"]),
    C("belladone", "Belladone", "Gardien", 0, DRU, "", 1, 6, legal=1, tokens=["livre-empoisonneur"]),
    C("sylve", "Sylve", "Gardien", 0, DRU, "", 2, 5, legal=1, tokens=["livre-secret", "loup"]),
    C("baril-chene", "Baril de chêne", "Baril", 0, IVR, "", 0, 6, legal=False, token=True),
    C("baril-explosif", "Baril explosif", "Baril", 0, IVR, "", 0, 4, legal=False, token=True),
    C("livre-ancien", "Livre ancien", "Recettes", 0, DRU, "", legal=False, token=True),
    C("livre-empoisonneur", "Livre empoisonneur", "Recettes", 0, DRU, "", legal=False, token=True),
    C("livre-secret", "Livre secret", "Recettes", 0, DRU, "", legal=False, token=True),
]
_BAR = ("**Aura :** tes unités de sa salle ont +1 Puissance.\n**Encaisser :** prend les dégâts d'une de tes unités de sa salle.\n"
        "**Tirer une pinte :** 1 fois par tour, perds 1 PV pour piocher 1 carte de ta Réserve.\n")

# Textes de cartes (une ligne par effet, le moment en gras)
TEXTS = {
 "habitue": "**Près du baril :** +1 PV.",
 "serveuse": "**Arrivée :** une de tes unités gagne +1/+1.",
 "poker": "**Bluff :** se pose face cachée au Stratagème, révélée à l'Assaut.",
 "porteur": "**Arrivée :** déplace ton baril dans la salle de cette unité.",
 "barde": "**Dans sa salle :** tes autres unités ont +1 Puissance.",
 "videur": "**Protecteur.**\n**Défense :** peut défendre le Camp même s'il est en salle.",
 "cracheur": "**Arrivée, près du baril :** 1 dégât à chaque ennemi de la salle.",
 "brute": "**Arrivée :** Sonne une unité ou un monstre de sa salle.",
 "champion": "**Près du baril :** +2 Puissance et ne peut pas être Sonné.",
 "grosse-pinte": "Une unité gagne +2/+2 ce tour.",
 "ma-tournee": "Tes unités en jeu sont soignées et gagnent +1/+1 ce tour (+1 Puissance de plus si ton baril est intact).\nTes blessées du Camp reviennent en Expédition.\n**Signature :** 1 exemplaire max.",
 "biere": "**Alcool.** +1 Puissance.",
 "cidre": "**Alcool.** +1 PV.",
 "hydromel": "**Alcool.** +2 PV et soigne 2 PV.",
 "rhum": "**Alcool.** +2 Puissance.\n**Retrait :** l'unité est Sonnée le tour suivant.",
 "whisky": "**Alcool.** L'unité ne peut pas être Sonnée.",
 "vin-chaud": "**Alcool.** Soigne complètement l'unité.",
 "absinthe": "**Alcool.** +3 Puissance.\n**Ton tour suivant :** l'unité perd 2 PV.",
 "liqueur-feu": "**Alcool.**\n**Dernier souffle :** 2 dégâts à chaque ennemi de sa salle.",
 "cernun": "**Livre ancien** (fiche liée) : recettes de buff.\n**Repos :** Cueillette. Pioche 3 cartes de ta Réserve, remets-en 1 (mélange), garde 2 sous Cernun (4 max).\n**Assaut :** cuisine 1 recette.\n**Monstre tué :** pioche 1 carte de ta Réserve.\n**Défense du Camp :** invoque 2 Pousses.",
 "champignon": "**Ingrédient.** Seul, il ne fait rien : cuisine-le avec le Livre.",
 "baies": "**Ingrédient.** Seules, elles ne font rien : cuisine-les avec le Livre.",
 "racine": "**Ingrédient.** Seule, elle ne fait rien : cuisine-la avec le Livre.",
 "miel": "**Ingrédient.** Seul, il ne fait rien : cuisine-le avec le Livre.",
 "herbes": "**Ingrédient.** Seules, elles ne font rien : cuisine-les avec le Livre.",
 "lutin": "**Arrivée :** invoque une Pousse.",
 "chouette": "**Arrivée :** pioche 2 cartes de ta Réserve, garde-en 1, remets l'autre et mélange.",
 "cueilleuse": "**Retrait :** si elle est en Expédition, pioche 1 carte de ta Réserve.",
 "invocateur": "**Combat :** invoque une Pousse dans sa salle.",
 "chamane": "**Combat :** tes autres unités de sa salle ont +1 Puissance.",
 "dryade": "**Dernier souffle :** invoque 2 Pousses.",
 "meneuse": "**Arrivée :** invoque un Loup.",
 "saule": "**Protecteur.**\n**Allié mort dans sa salle :** invoque une Pousse.",
 "sanglier": "**Rapide.**",
 "vieux-chene": "**Dans sa salle :** tes Pousses et Loups ont +1/+1.",
 "lianes": "**Rapide.** Sonne une unité ou un monstre.",
 "croissance": "**Rapide.** Une de tes unités gagne +2/+2 ce tour.",
 "appel-meute": "Invoque 2 Loups, chacun dans une salle où tu as une unité.",
 "spores": "1 dégât à chaque ennemi d'une salle. Invoque une Pousse par ennemi tué.",
 "eveil-foret": "Invoque une Pousse dans chaque salle.\nTes unités gagnent +1/+1 ce tour.\nPioche 1 carte de ta Réserve.\n**Signature :** 1 exemplaire max.",
 "pousse": "**Jeton.** Compte dans la limite de 3 unités par salle.",
 "loup": "**Jeton.** Compte dans la limite de 3 unités par salle.",
 "jet-chaises": "2 dégâts à une cible, qui est Sonnée.",
 "rosa": "**Baril explosif** (jeton 4 PV, voir fiche) : pose-le dans une salle au 1er Assaut.\n**Repos :** soigne 2 PV au baril.\n**Tirer une pinte :** regarde 2 cartes de ta Réserve, prends-en 1, remets l'autre et mélange.\n**Défense du Camp :** 1 dégât à chaque attaquant.",
 "belladone": "**Livre empoisonneur** (fiche liée) : recettes qui blessent.\n**Repos :** Cueillette. Pioche 2 cartes de ta Réserve, garde-les sous Belladone (4 max).\n**Assaut :** cuisine 1 recette.\n**Défense du Camp :** la première unité qui attaque Belladone est Sonnée.",
 "sylve": "**Livre secret** (fiche liée) : chaque recette donne Rapide.\n**Repos :** Cueillette. Pioche 2 cartes de ta Réserve, garde-les sous Sylve (4 max).\n**Stratagème :** choisis ta recette face cachée.\n**Assaut :** révèle-la et cuisine-la.",
 "livre-ancien": "**Assaut :** 1 recette par tour, instantanée (même en Duel), effet ce tour. Les cartes utilisées retournent dans ta Réserve (mélange).\n**Soupe de racines** (Racine + Champignon) : tes unités +2 PV.\n**Tarte aux baies** (Baies + Miel) : tes unités +1 Puissance.\n**Tisane des bois** (Herbes + Miel) : soigne une salle, ses unités ne sont pas Sonnées.\n**Poêlée des esprits** (Champignon + Herbes + Baies) : 1 Pousse par salle où tu as une unité.\n**Banquet de Cernun** (4 ingrédients différents) : tes unités +2/+2.",
 "livre-empoisonneur": "**Assaut :** 1 recette par tour, instantanée (même en Duel). Les cartes utilisées retournent dans ta Réserve (mélange).\n**Sève amère** (Racine + Champignon) : 1 dégât à chaque ennemi d'une salle.\n**Brouet de baies** (Baies + Miel) : 2 dégâts à une cible, qui est Sonnée.\n**Fumée d'herbes** (Herbes + Champignon) : les ennemis d'une salle sont Sonnés.\n**Philtre noir** (3 ingrédients différents) : 2 dégâts à chaque ennemi d'une salle.",
 "livre-secret": "**Stratagème :** 1 recette face cachée. **Assaut :** révèle-la et cuisine-la. Les cartes utilisées retournent dans ta Réserve (mélange).\n**Pain de route** (Racine + Miel) : tes unités gagnent Rapide.\n**Infusion vive** (Herbes + Baies) : Rapide et +1 Puissance.\n**Festin de l'ombre** (3 ingrédients différents) : Rapide et +1/+1.\n**Rapide :** une unité peut changer de salle après son combat.",
 "guss": "**Baril de chêne** (jeton 6 PV, voir fiche) : pose-le dans une salle au 1er Assaut.\n**Repos :** soigne complètement le baril.\n**Défense du Camp :** tes défenseurs ont +1 Puissance.\n**Raid :** la première unité qui attaque Guss est Sonnée."
}

TEXTS["baril-chene"] = _BAR + "**À 0 PV :** 1 dégât à tout ce qui est dans la salle.\nUn seul baril ; il ne rentre jamais au Camp."
TEXTS["baril-explosif"] = _BAR + "**À 0 PV :** 3 dégâts à tout ce qui est dans la salle.\nUn seul baril ; il ne rentre jamais au Camp."
for _c in CARDS:
    if _c["id"] in TEXTS:
        _c["text"] = TEXTS[_c["id"]]


# --- Donjons préconstruits : 8 monstres (recto normal / verso évolué), 1 boss, 3 reliques ---
MINE = "Mine des Gobelins"


def M(id, name, p, pv, tr, text, vname, vp, vpv, vtr, vtext, relique=False):
    """Monstre recto/verso. Le verso est la face évoluée (même carte, retournée)."""
    return C(id, name, "Monstre", 0, MINE, text, p, pv, legal=False, token=True, tresors=tr, relique=relique,
             back=dict(name=vname, power=vp, hp=vpv, tresors=vtr, text=vtext))


CARDS += [
    M("gobelin", "Gobelin fouineur", 2, 3, 1, "Il fouille, il mord, il s'enfuit avec ce qu'il trouve.",
      "Hobgobelin", 3, 5, 2, "Plus grand, plus méchant, plus riche."),
    M("rat", "Rat des galeries", 1, 3, 1, "**Embuscade :** 1 dégât à chaque unité de sa salle.",
      "Rat géant", 2, 5, 2, "**Morsure :** une unité qu'il blesse est Sonnée."),
    M("archer", "Archer gobelin", 2, 2, 1, "**Embuscade :** 2 dégâts à une unité de sa salle (guilde la plus riche d'abord).",
      "Tireur gobelin", 3, 4, 2, "**Combat :** 1 dégât à la première unité qui l'attaque, avant le coup."),
    M("chaman", "Chaman gobelin", 1, 4, 2, "**Les autres monstres** ont +1 Puissance.",
      "Grand chaman", 2, 6, 3, "**Les autres monstres** ont +1/+1.", relique=True),
    M("araignee", "Araignée des puits", 2, 4, 2, "**Embuscade :** une unité de sa salle est Sonnée.",
      "Reine araignée", 3, 6, 3, "**Toile :** les unités de sa salle ne peuvent pas changer de salle.", relique=True),
    M("golem", "Golem de minerai", 2, 7, 2, "**Carapace :** chaque attaque lui inflige 1 dégât de moins.",
      "Golem de cristal", 3, 9, 3, "**Carapace :** chaque attaque lui inflige 1 dégât de moins."),
    M("contremaitre", "Contremaître hobgobelin", 3, 5, 2, "Il compte les pépites. Et les doigts.",
      "Chef de guerre", 4, 7, 4, "**Riposte :** frappe aussi une 2e unité de la salle.", relique=True),
    M("troll", "Troll des mines", 4, 6, 3, "**Régénération :** au Retrait, il est soigné complètement.",
      "Troll ancien", 5, 8, 4, "**Régénération :** au Retrait, il est soigné complètement."),
    C("grombak", "Grombak, roi gobelin", "Boss", 0, MINE,
      "Entre quand la pioche de monstres est vide.\n**Enragé :** à 9 PV ou moins, +2 Puissance.\n"
      "**Fin :** sa mort termine la partie à la fin du tour.", 6, 18, legal=False, token=True, tresors=6),
    C("lanterne", "Lanterne du mineur", "Relique", 0, MINE,
      "**Stratagème :** regarde le monstre du dessus de la pioche ; tu peux le mettre en dessous (bouton « Dessus → dessous » du panneau Donjon).",
      legal=False, token=True),
    C("pioche-runique", "Pioche runique", "Relique", 0, MINE,
      "**Assaut :** ta première unité qui attaque un monstre a +2 Puissance pour ce combat.",
      legal=False, token=True),
    C("bourse", "Bourse du contremaître", "Relique", 0, MINE,
      "**Retrait :** si tu as tué au moins un monstre ce tour, +1 trésor.",
      legal=False, token=True),
]
DONJONS = {"mine": {"nom": MINE, "monstres": ["gobelin", "rat", "archer", "chaman", "araignee", "golem",
                                               "contremaitre", "troll"],
                    "boss": "grombak", "reliques": ["lanterne", "pioche-runique", "bourse"]}}

# --- Format Terrains (2026-10-15) : plus de Réserve. Le Gardien vient avec un Terrain et un Menu ---
# L'ancien système (alcools et ingrédients en cartes) est sur la branche archive-reserve.
CARDS = [c for c in CARDS if c["type"] not in ("Alcool", "Ingredient")]
TYPE_LABEL.update({"Terrain": "Terrain", "Menu": "Menu"})
PALETTE.update({"Terrain": ((58, 50, 34), (205, 170, 95)), "Menu": ((40, 36, 52), (170, 150, 210))})
CARDS = [c for c in CARDS if c["type"] != "Recettes"]   # les Livres sont fusionnés dans les bosquets
CARDS += [
    C("bosquet", "Bosquet ancien", "Terrain", 0, DRU, "", 0, 5, legal=1),
    C("bosquet-poison", "Bosquet empoisonné", "Terrain", 0, DRU, "", 0, 5, legal=1),
    C("bosquet-ombre", "Bosquet d'ombre", "Terrain", 0, DRU, "", 0, 3, legal=1),
    C("transplantation", "Transplantation", "Sort", 2, DRU, ""),
]
_NIV = ""
_PINTES = ("**Pinte** (ton Assaut ou Duel ici), 2 par tour (3 au niv. 2) :\n"
           "**1 PV :** Bière +1 P · Cidre +2 PV · Hydromel soigne 2.\n"
           "**2 PV :** Rhum +2 P, Sonnée au tour suivant · Whisky pas Sonnée · Absinthe +3 P, -2 PV à ton Repos.\n"
           "**Mélange :** 2 alcools le même tour = Sonnée.\n**Dernière tournée :** la pinte peut vider le baril.")
_FORET = ("**Niv. 1, Sous-bois :** 4 de tes unités ici au lieu de 3. **Niv. 2 :** +2 Sève au Repos. **Niv. 3, Fief :** +1 trésor par monstre tué ici.\n"
          "**Sève** : jetons sur ce bosquet (4 max). 1 recette par tour (ton Assaut ou Duel ici).\n")
NEW = {
 "baril-chene": _NIV + "**Niv. 1, Aura :** tes unités ici +1 P. **Niv. 3, Fief :** +1 trésor par monstre tué ici.\n"
   "**Encaisser** les dégâts d'une de tes unités ici. **À 0 PV :** 1 dégât à tout ce qui est dans la salle.\n" + _PINTES,
 "baril-explosif": _NIV + "**Niv. 1, Aura :** tes unités ici +1 P. **Niv. 3, Fief :** +1 trésor par monstre tué ici.\n"
   "**Encaisser** les dégâts d'une de tes unités ici. **À 0 PV :** 3 dégâts à tout ce qui est dans la salle.\n" + _PINTES,
 "bosquet": _NIV + _FORET + "**2 Soupe de racines :** +2 PV ce tour.\n**2 Tarte aux baies :** +1 P ce tour.\n"
   "**2 Tisane des bois :** soin, pas Sonnées.\n**3 Poêlée des esprits :** 1 Pousse ici et dans chaque salle voisine où tu as une unité.\n"
   "**4 Banquet :** toutes tes unités +2/+2 ce tour.",
 "bosquet-poison": _NIV + _FORET + "**2 Sève amère :** 1 dégât à chaque ennemi d'ici, qui est Empoisonné.\n**2 Brouet de baies :** 2 dégâts à une cible d'ici, Sonnée.\n"
   "**3 Fumée d'herbes :** les ennemis d'ici sont Sonnés.\n**4 Philtre noir :** 2 dégâts à chaque ennemi d'une salle.",
 "bosquet-ombre": _NIV + _FORET + "**Rapide :** ses recettes se jouent dans n'importe quel Duel.\n"
   "**1 Pain de route :** tes unités d'ici gagnent Rapide.\n**1 Infusion vive :** une unité, Rapide et +1 P.\n"
   "**2 Festin de l'ombre :** tes unités d'ici, Rapide et +1/+1.",
 "guss": "**Repos :** soigne 2 PV à ton baril.\n**Défense du Camp :** tes défenseurs ont +1 Puissance.\n**Raid :** la première unité qui attaque Guss est Sonnée.",
 "rosa": "**Repos :** soigne 2 PV à ton baril.\n**Pinte :** 2 alcools à 1 PV pour une seule pinte.\n**Défense du Camp :** 1 dégât à chaque attaquant.",
 "cernun": "**Repos :** +1 Sève (Cueillette).\n**Récolte :** +1 Sève par monstre tué par tes unités.\n**Défense du Camp :** invoque 2 Pousses.",
 "belladone": "**Repos :** +1 Sève (Cueillette).\n**Défense du Camp :** la première unité qui attaque Belladone est Sonnée.",
 "sylve": "**Repos :** +1 Sève (Cueillette).\n**Nomade :** lever le camp ne fait pas perdre de niveau à ton bosquet.",
 "habitue": "**Dans la Taverne :** +1 PV.",
 "champion": "**Dans la Taverne :** +2 Puissance et ne peut pas être Sonné.",
 "cracheur": "**Arrivée, dans la Taverne :** 1 dégât à chaque ennemi de la salle.",
 "porteur": "**Arrivée :** déplace ton baril dans l'Expédition de cette unité, sans perte de niveau.",
 "roule-baril": "Déplace ton baril dans une autre de tes Expéditions, sans perte de niveau, puis 2 dégâts à chaque ennemi de la salle d'arrivée.",
 "ma-tournee": "Tes unités en jeu sont soignées et gagnent +1/+1 ce tour.\nTes blessées du Camp reviennent en Expédition.\nChaque unité de la Taverne boit une Bière gratuite.\n**Signature :** 1 exemplaire max.",
 "chouette": "**Arrivée :** +1 Sève.",
 "cueilleuse": "**Retrait :** si elle est dans la Forêt, +1 Sève.",
 "eveil-foret": "Invoque une Pousse dans chaque salle.\nTes unités gagnent +1/+1 ce tour. +2 Sève.\nToutes tes Expéditions comptent comme Forêt ce tour.\n**Signature :** 1 exemplaire max.",
 "transplantation": "Déplace ton bosquet dans une autre de tes Expéditions, sans perte de niveau.",
}
TOKS = {"guss": [], "rosa": [], "cernun": ["pousse"], "belladone": [], "sylve": ["loup"]}
for _c in CARDS:
    if _c["id"] in NEW:
        _c["text"] = NEW[_c["id"]]
    if _c["id"] in TOKS:
        _c["tokens"] = TOKS[_c["id"]]
    if _c["type"] == "Baril":   # les barils deviennent des Terrains, à mettre dans le deck (1 par deck)
        _c["type"] = "Terrain"
        _c["token"], _c["legal"] = False, 1



def rich_lines(draw, text, fnt, fnt_b, max_w):
    """Découpe un texte avec **gras** en lignes de segments (mot, gras?)."""
    words = []
    for i, part in enumerate(re.split(r"\*\*", text)):
        for j, chunk in enumerate(part.split("\n")):
            if j:
                words.append(("\n", False))
            for w in chunk.split():
                words.append((w, i % 2 == 1))
    lines, cur, cur_w = [], [], 0
    space = draw.textlength(" ", font=fnt)
    for w, b in words:
        if w == "\n":
            if cur:
                lines.append(cur)
            cur, cur_w = [], 0
            continue
        ww = draw.textlength(w, font=fnt_b if b else fnt)
        add = ww if not cur else ww + space
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(w, b)], ww
        else:
            cur.append((w, b))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def draw_card(c, path):
    pal_key = c["faction"] if c["faction"] in PALETTE else c["type"]
    if c["type"] in ("Monstre", "Boss", "Energie"):
        pal_key = c["type"]
    bg, frame = PALETTE.get(pal_key, PALETTE["Test"])
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 6, W - 7, H - 7), radius=26, outline=frame, width=8)

    # Titre
    d.rounded_rectangle((24, 22, W - 25, 100), radius=16, fill=frame)
    tf = font(30, True)
    while d.textlength(c["name"], font=tf) > W - 150 and tf.size > 16:
        tf = font(tf.size - 1, True)
    d.text((W // 2 + (0 if c["type"] in ("Terrain", "Menu") else 24), 61), c["name"], font=tf, fill=(20, 14, 10), anchor="mm")
    fiche = c["type"] in ("Terrain", "Menu") and not c.get("recto")   # recto d'un Terrain : illustré
    top = 168 if fiche else 330   # bas de l'illustration (plus de place pour le texte des fiches)
    # Coût (ou trésors pour un monstre : pastille dorée ; rien pour une fiche)
    if fiche or c["type"] == "Terrain":
        pass
    elif c.get("tresors") is not None:
        d.ellipse((30, 28, 94, 92), fill=(232, 186, 60), outline="white", width=3)
        d.text((62, 60), str(c["tresors"]), font=font(34, True), fill=(40, 25, 5), anchor="mm")
    else:
        d.ellipse((30, 28, 94, 92), fill=(15, 15, 25), outline="white", width=3)
        d.text((62, 60), str(c["cost"]), font=font(34, True), fill="white", anchor="mm")

    # Illustration (placeholder)
    d.rounded_rectangle((24, 114, W - 25, top), radius=14, fill=(12, 10, 10))
    big = c.get("big") or ("ÉVOLUÉ" if c.get("verso") else TYPE_LABEL[c["type"]].upper())
    d.text((W // 2, 136 if fiche else 205), big, font=font(30 if fiche else 44, True), fill=frame, anchor="mm")
    if c.get("relique"):
        d.rounded_rectangle((W - 190, 122, W - 33, 160), radius=10, fill=(225, 190, 70))
        d.text((W - 111, 141), "◆ RELIQUE", font=font(20, True), fill=(40, 25, 5), anchor="mm")
    fac = c["faction"] if c["type"] not in ("Monstre", "Boss", "Energie", "Relique") and c["faction"] != "Relique" else ""
    if fac:
        d.text((W // 2, 160 if fiche else 260), fac.upper(), font=font(16 if fiche else 22, True), fill=(200, 200, 205), anchor="mm")
    if not fiche:
        d.text((W // 2, 300), "illustration à venir", font=font(17), fill=(120, 120, 130), anchor="mm")

    # Ligne de type
    tl = TYPE_LABEL[c["type"]] + (f" — {c['faction']}" if fac else "")
    if c.get("tresors") is not None:
        tl = TYPE_LABEL[c["type"]] + (" évolué" if c.get("verso") else "") + f" — {c['tresors']} trésor" + ("s" if c["tresors"] > 1 else "")
    d.text((30, top + 16), tl, font=font(22, True), fill=frame)

    # Texte de règles (taille auto)
    box_bottom = H - 112 if c["power"] is not None or c.get("recto") else H - 36
    size = 24
    while True:
        f, fb = font(size), font(size, True)
        lines = rich_lines(d, c["text"], f, fb, W - 64)
        lh = int(size * 1.3)
        if top + 54 + len(lines) * lh <= box_bottom or size <= 14:
            break
        size -= 1
    y = top + 54
    for line in lines:
        x = 32
        for w, b in line:
            fnt = fb if b else f
            d.text((x, y), w, font=fnt, fill="white")
            x += d.textlength(w + " ", font=fnt)
        y += lh

    # Stats
    if c["power"] is not None:
        for (x0, label) in ((24, f"P {c['power']}"), (W - 154, f"PV {c['hp']}")):
            d.rounded_rectangle((x0, H - 98, x0 + 130, H - 28), radius=14, fill=(15, 15, 25),
                                outline="white", width=3)
            d.text((x0 + 65, H - 63), label, font=font(34, True), fill="white", anchor="mm")
    elif c.get("recto"):
        d.rounded_rectangle((W - 154, H - 98, W - 24, H - 28), radius=14, fill=(15, 15, 25), outline="white", width=3)
        d.text((W - 89, H - 63), f"PV {c['hp_terrain']}", font=font(34, True), fill="white", anchor="mm")
    img.save(path, optimize=True)


def main():
    out_dir = os.path.join(ROOT, "img", "cards")
    os.makedirs(out_dir, exist_ok=True)
    cards = {}
    for c in CARDS:
        draw_card(c, os.path.join(out_dir, f"{c['id']}.png"))
        img = f"{BASE}/img/cards/{c['id']}.png"
        front = {"name": {"name": c["name"]}, "type": c["type"], "cost": c["cost"], "image": img}
        e = {"id": c["id"], "face": {"front": front}, "name": c["name"], "type": c["type"],
             "cost": c["cost"], "faction": c["faction"]}
        if not c["token"]:  # les jetons sont déjà exclus du deck : pas de marque « illégal » en jeu
            e["_legal"] = {"PROTO": c["legal"]}
        if c["power"] is not None:
            e["power"], e["hp"] = c["power"], c["hp"]
        if c["token"]:
            e["isToken"] = True
        if c["tokens"]:
            e["tokens"] = c["tokens"]
        if c.get("back"):
            b = dict(c, **c["back"], verso=True, back=None)
            draw_card(b, os.path.join(out_dir, f"{c['id']}-verso.png"))
            e["face"]["back"] = {"name": {"name": b["name"]}, "type": c["type"], "cost": 0,
                                 "image": f"{BASE}/img/cards/{c['id']}-verso.png"}
        if c.get("tresors") is not None:
            e["tresors"] = c["tresors"]
        cards[c["id"]] = e
    with open(os.path.join(ROOT, "cards.json"), "w", encoding="utf-8") as fh:
        json.dump(cards, fh, ensure_ascii=False, indent=2)
    # nettoie les images de cartes qui n'existent plus
    for fn in os.listdir(out_dir):
        if fn.endswith(".png") and fn[:-4].removesuffix("-verso") not in cards:
            os.remove(os.path.join(out_dir, fn))
    print(len(cards), "cartes")


if __name__ == "__main__":
    main()
