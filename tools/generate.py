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
BASE = "https://raw.githubusercontent.com/BlueZero1203/Guild-Rush/main"
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


def C(id, name, type, cost, faction, text="", power=None, hp=None, legal=3, token=False, tokens=None):
    return dict(id=id, name=name, type=type, cost=cost, faction=faction, text=text,
                power=power, hp=hp, legal=legal, token=token, tokens=tokens or [])


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
    C("relique-test", "Relique test", "Relique", 0, "Relique",
      "Passif de relique (à définir). Gardée au Camp, volable par raid.", legal=3),
    C("carte-tresor", "Carte au trésor", "Tresor", 0, "Relique",
      "Prise par le premier joueur qui tue un monstre (crée-la avec le panneau des jetons). +1 trésor à chaque Nuit. Gardée au Camp, volable par raid.", legal=False, token=True),
    C("energie", "Énergie", "Energie", 0, "Energie",
      "Incline-la pour payer 1. 1 seule se redresse par tour.", legal=False, token=True),
    # --- Donjon ---
    C("monstre-1", "Monstre test 1", "Monstre", 0, "Monstre", "Valeur : 1 trésor.", 2, 3, legal=False, token=True),
    C("monstre-2", "Monstre test 2", "Monstre", 0, "Monstre", "Valeur : 2 trésors.", 3, 5, legal=False, token=True),
    C("monstre-3", "Monstre test 3", "Monstre", 0, "Monstre", "Valeur : 2 trésors.", 4, 6, legal=False, token=True),
    C("monstre-4", "Monstre test 4", "Monstre", 0, "Monstre", "Valeur : 3 trésors.", 5, 8, legal=False, token=True),
    C("boss-test", "Boss test", "Boss", 0, "Boss",
      "Frappe d'abord la guilde qui a le plus de trésors.", 8, 20, legal=False, token=True),
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
        "**Tirer une pinte :** 1 fois par tour, perds 1 PV pour piocher 1 carte de la Cave.\n")

# Textes de cartes (une ligne par effet, le moment en gras)
TEXTS = {
 "habitue": "**Près du baril :** +1 PV.",
 "serveuse": "**Arrivée :** une de tes unités gagne +1/+1.",
 "poker": "**Bluff :** se pose face cachée au Midi, révélée au Crépuscule.",
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
 "rhum": "**Alcool.** +2 Puissance.\n**Nuit :** l'unité est Sonnée le tour suivant.",
 "whisky": "**Alcool.** L'unité ne peut pas être Sonnée.",
 "vin-chaud": "**Alcool.** Soigne complètement l'unité.",
 "absinthe": "**Alcool.** +3 Puissance.\n**Ton tour suivant :** l'unité perd 2 PV.",
 "liqueur-feu": "**Alcool.**\n**Dernier souffle :** 2 dégâts à chaque ennemi de sa salle.",
 "cernun": "**Livre ancien** (fiche liée) : recettes de buff.\n**Aube :** Cueillette. Pioche 3 ingrédients, défausse-en 1 dans ta Réserve (mélange), garde 2 sous Cernun (4 max).\n**Crépuscule :** cuisine 1 recette.\n**Monstre tué :** +1 ingrédient.\n**Défense du Camp :** invoque 2 Pousses.",
 "champignon": "**Ingrédient.** Seul, il ne fait rien : cuisine-le avec le Livre.",
 "baies": "**Ingrédient.** Seules, elles ne font rien : cuisine-les avec le Livre.",
 "racine": "**Ingrédient.** Seule, elle ne fait rien : cuisine-la avec le Livre.",
 "miel": "**Ingrédient.** Seul, il ne fait rien : cuisine-le avec le Livre.",
 "herbes": "**Ingrédient.** Seules, elles ne font rien : cuisine-les avec le Livre.",
 "lutin": "**Arrivée :** invoque une Pousse.",
 "chouette": "**Arrivée :** pioche 2 ingrédients, garde-en 1, remets l'autre et mélange.",
 "cueilleuse": "**Nuit :** si elle est en salle, pioche 1 ingrédient.",
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
 "eveil-foret": "Invoque une Pousse dans chaque salle.\nTes unités gagnent +1/+1 ce tour.\nPioche 1 ingrédient.\n**Signature :** 1 exemplaire max.",
 "pousse": "**Jeton.** Compte dans la limite de 3 unités par salle.",
 "loup": "**Jeton.** Compte dans la limite de 3 unités par salle.",
 "jet-chaises": "2 dégâts à une cible, qui est Sonnée.",
 "rosa": "**Baril explosif** (jeton 4 PV, voir fiche) : pose-le dans une salle au 1er Crépuscule.\n**Aube :** soigne 2 PV au baril.\n**Tirer une pinte :** regarde 2 cartes de la Cave, prends-en 1, remets l'autre et mélange.\n**Défense du Camp :** 1 dégât à chaque attaquant.",
 "belladone": "**Livre empoisonneur** (fiche liée) : recettes qui blessent.\n**Aube :** Cueillette. Pioche 2 ingrédients, garde-les sous Belladone (4 max).\n**Crépuscule :** cuisine 1 recette.\n**Défense du Camp :** la première unité qui attaque Belladone est Sonnée.",
 "sylve": "**Livre secret** (fiche liée) : chaque recette donne Rapide.\n**Aube :** Cueillette. Pioche 2 ingrédients, garde-les sous Sylve (4 max).\n**Midi :** choisis ta recette face cachée.\n**Crépuscule :** révèle-la et cuisine-la.",
 "livre-ancien": "**Crépuscule :** 1 recette par tour, effet ce tour. Les ingrédients retournent dans la Réserve (mélange).\n**Soupe de racines** (Racine + Champignon) : tes unités +2 PV.\n**Tarte aux baies** (Baies + Miel) : tes unités +1 Puissance.\n**Tisane des bois** (Herbes + Miel) : soigne une salle, ses unités ne sont pas Sonnées.\n**Poêlée des esprits** (Champignon + Herbes + Baies) : 1 Pousse par salle où tu as une unité.\n**Banquet de Cernun** (4 ingrédients différents) : tes unités +2/+2.",
 "livre-empoisonneur": "**Crépuscule :** 1 recette par tour. Les ingrédients retournent dans la Réserve (mélange).\n**Sève amère** (Racine + Champignon) : 1 dégât à chaque ennemi d'une salle.\n**Brouet de baies** (Baies + Miel) : 2 dégâts à une cible, qui est Sonnée.\n**Fumée d'herbes** (Herbes + Champignon) : les ennemis d'une salle sont Sonnés.\n**Philtre noir** (3 ingrédients différents) : 2 dégâts à chaque ennemi d'une salle.",
 "livre-secret": "**Midi :** 1 recette face cachée. **Crépuscule :** révèle-la et cuisine-la. Les ingrédients retournent dans la Réserve (mélange).\n**Pain de route** (Racine + Miel) : tes unités gagnent Rapide.\n**Infusion vive** (Herbes + Baies) : Rapide et +1 Puissance.\n**Festin de l'ombre** (3 ingrédients différents) : Rapide et +1/+1.\n**Rapide :** une unité peut changer de salle après son combat.",
 "guss": "**Baril de chêne** (jeton 6 PV, voir fiche) : pose-le dans une salle au 1er Crépuscule.\n**Aube :** soigne complètement le baril.\n**Défense du Camp :** tes défenseurs ont +1 Puissance.\n**Raid :** la première unité qui attaque Guss est Sonnée."
}

TEXTS["baril-chene"] = _BAR + "**À 0 PV :** 1 dégât à tout ce qui est dans la salle.\nUn seul baril ; il ne rentre jamais au Camp."
TEXTS["baril-explosif"] = _BAR + "**À 0 PV :** 3 dégâts à tout ce qui est dans la salle.\nUn seul baril ; il ne rentre jamais au Camp."
for _c in CARDS:
    if _c["id"] in TEXTS:
        _c["text"] = TEXTS[_c["id"]]


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
    d.text((W // 2 + 24, 61), c["name"], font=tf, fill=(20, 14, 10), anchor="mm")
    # Coût
    d.ellipse((30, 28, 94, 92), fill=(15, 15, 25), outline="white", width=3)
    d.text((62, 60), str(c["cost"]), font=font(34, True), fill="white", anchor="mm")

    # Illustration (placeholder)
    d.rounded_rectangle((24, 114, W - 25, 330), radius=14, fill=(12, 10, 10))
    d.text((W // 2, 205), TYPE_LABEL[c["type"]].upper(), font=font(44, True), fill=frame, anchor="mm")
    fac = c["faction"] if c["faction"] not in ("Monstre", "Boss", "Energie", "Relique") else ""
    if fac:
        d.text((W // 2, 260), fac.upper(), font=font(22, True), fill=(200, 200, 205), anchor="mm")
    d.text((W // 2, 300), "illustration à venir", font=font(17), fill=(120, 120, 130), anchor="mm")

    # Ligne de type
    tl = TYPE_LABEL[c["type"]] + (f" — {c['faction']}" if fac else "")
    d.text((30, 346), tl, font=font(22, True), fill=frame)

    # Texte de règles (taille auto)
    box_bottom = H - 112 if c["power"] is not None else H - 36
    size = 24
    while True:
        f, fb = font(size), font(size, True)
        lines = rich_lines(d, c["text"], f, fb, W - 64)
        lh = int(size * 1.3)
        if 384 + len(lines) * lh <= box_bottom or size <= 14:
            break
        size -= 1
    y = 384
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
        cards[c["id"]] = e
    with open(os.path.join(ROOT, "cards.json"), "w", encoding="utf-8") as fh:
        json.dump(cards, fh, ensure_ascii=False, indent=2)
    # nettoie les images de cartes qui n'existent plus
    for fn in os.listdir(out_dir):
        if fn.endswith(".png") and fn[:-4] not in cards:
            os.remove(os.path.join(out_dir, fn))
    print(len(cards), "cartes")


if __name__ == "__main__":
    main()
