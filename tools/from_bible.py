#!/usr/bin/env python3
"""Génère cards.json, les images des cartes et l'aide de gamefile.json depuis la bible.

Source unique : bible/03_cartes.csv (cartes des guildes) et bible/05_donjon_mine.csv (donjon).
Remplace les listes codées en dur de generate.py ; on garde son dessin de carte (draw_card).
Langues : chaque carte est dessinée en français (img/cards/<id>.png) et en anglais (<id>-en.png) ;
cards.json donne le nom et l'image par langue ({"en": …, "fr": …}) et translations.json traduit l'aide,
les types, les zones et les jetons. Chaque joueur choisit sa langue dans les Options de TCG Arena.
Les textes anglais viennent de bible/en/ ; une ligne dont le français a changé depuis sa traduction
est signalée « à retraduire » et reste en français en attendant.
Usage : python3 tools/from_bible.py   (depuis la racine du dépôt)
"""
import csv
import hashlib
import json
import os
import re
import sys
import urllib.parse

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as gen  # noqa: E402  (dessin des cartes, palette, cartes communes)

ROOT = gen.ROOT
BASE = gen.BASE
BIBLE = os.path.join(ROOT, "bible")
BIBLE_EN = os.path.join(BIBLE, "en")
LANGS = ("fr", "en")
A_RETRADUIRE = []

gen.PALETTE["Mages"] = ((30, 34, 70), (130, 140, 230))
TYPES = {"Unité": "Unite", "Sort": "Sort", "Gardien": "Gardien", "Terrain": "Terrain"}


MOTS_SEULS = {"fr": ("Réflexe.", "Portée.", "Rapide.", "Protecteur.", "Éclaireur.", "Bluff.", "Jeton."),
              "en": ("Reflex.", "Reach.", "Swift.", "Protector.", "Scout.", "Bluff.", "Token.")}
DEUX_POINTS = {"fr": " : ", "en": ": "}


def rich(texte, lang="fr"):
    """« Moment : effet / Moment : effet » → une ligne par effet, le moment en gras (en anglais « Moment: effet »)."""
    lignes = []
    dp = DEUX_POINTS[lang]
    for seg in texte.split(" / "):
        seg = seg.strip()
        kws = []
        for kw in MOTS_SEULS[lang]:
            if seg.startswith(kw + " "):
                kws.append(f"**{kw}**")
                seg = seg[len(kw) + 1:]
        if kws:
            seg = " ".join(kws) + " " + seg
            lignes.append(seg)
            continue
        tete, sep, reste = seg.partition(dp)
        if sep and len(tete) <= 45:
            lignes.append(f"**{tete}{dp.rstrip()}** {reste}")
        elif seg.endswith(".") and len(seg) <= 20:   # mot-clé seul (« Rapide. », « Protecteur. »)
            lignes.append(f"**{seg}**")
        else:
            lignes.append(seg)
    return "\n".join(lignes)


TERRAIN = {"fr": (("Niv. 2 :", "Niv. 3 :"), "**Encaisser. À 0 PV :**", "**Encaisser.**\n**À 0 PV :**"),
           "en": (("Lvl 2:", "Lvl 3:"), "**Soak. At 0 HP:**", "**Soak.**\n**At 0 HP:**")}


def terrain_rich(texte, lang="fr"):
    t = rich(texte, lang)
    nivs, encaisser, coupe = TERRAIN[lang]
    for niv in nivs:
        t = t.replace(f". {niv}", f".\n**{niv}**")
    t = t.replace(encaisser, coupe)
    fin = DEUX_POINTS[lang].rstrip()
    return "\n".join(f"**{l}**" if l.endswith(fin) and not l.endswith("**") else l for l in t.split("\n"))


# --- Lexique : définitions tirées du glossaire (bible/00_glossaire.md, bible/en/00_glossaire_en.md),
# rappelées sur les cartes et dans l'aide ---
LEX_CFG = {
    "fr": dict(fichier=os.path.join(BIBLE, "00_glossaire.md"), etat="état",
               sections=("Mots-clés", "États (jetons)", "Ressources"),
               en_plus={"Mêlée", "Repli", "Pillage", "Blessé", "Lever le camp", "Signature"},
               sans_rappel={"Arrivée", "Dernier souffle", "Combat", "Tue un monstre", "Sort lancé", "Révélé", "Retrait",
                            "Énergie", "Trésors", "Carte au trésor", "Rapide (état)"}),
    "en": dict(fichier=os.path.join(BIBLE_EN, "00_glossaire_en.md"), etat="state",
               sections=("Keywords", "States (tokens)", "Resources"),
               en_plus={"Brawl", "Fall back", "Plunder", "Wounded", "Break camp", "Signature"},
               sans_rappel={"Arrival", "Last breath", "Combat", "Monster kill", "Spellcast", "Revealed", "Withdrawal",
                            "Energy", "Treasure", "Treasure map", "Swift (state)"}),
}
TERME = re.compile(r"\*\*([^*]+)\*\*(?:\s*\([^)]*\))?\s*:\s*")


def lexique(lang="fr"):
    """{terme: définition}, dans l'ordre du glossaire, pour les sections utiles en partie."""
    cfg = LEX_CFG[lang]
    lex, section = {}, ""
    for ligne in open(cfg["fichier"], encoding="utf-8"):
        if ligne.startswith("## "):
            section = ligne[3:].strip()
            continue
        if not ligne.startswith("- **"):
            continue
        morceaux = TERME.split(ligne[2:].strip())   # ["", terme, déf, terme, déf, ...]
        for terme, defi in zip(morceaux[1::2], morceaux[2::2]):
            if section in cfg["sections"] or terme in cfg["en_plus"]:
                if terme in lex:   # « Rapide » existe en mot-clé et en état : on garde le mot-clé
                    terme = f"{terme} ({cfg['etat']})"
                lex[terme] = defi.strip()
    return lex


LEXIQUES = {lang: lexique(lang) for lang in LANGS}
LEXIQUE = LEXIQUES["fr"]


def court(defi, n=170):
    """Définition phrase par phrase tant qu'elle reste courte ; sans ses apartés « (…) » si ça en garde plus."""
    def coupe(txt):
        phrases = re.split(r"(?<=\.)\s+", txt)
        out, k = phrases[0], 1
        for ph in phrases[1:]:
            if len(out) + 1 + len(ph) > n:
                break
            out, k = out + " " + ph, k + 1
        return k, out if out.endswith(".") else out + "."
    avec, sans = coupe(defi), coupe(re.sub(r"\s*\([^)]*\)", "", defi))
    return sans[1] if sans[0] > avec[0] else avec[1]


def motif(terme):
    # 1re lettre insensible à la casse (« lever le camp ») ; accords (Sonnée, Pièges) ; « Sonne » le verbe.
    t = re.escape(terme)
    t = f"[{terme[0].upper()}{terme[0].lower()}]{t[1:]}"
    if terme == "Sonné":
        return re.compile(r"\bSonn(?:e|é|ée|és|ées|ent)\b")
    if terme == "Stunned":
        return re.compile(r"\b[Ss]tun(?:s|ned)?\b")
    return re.compile(rf"(?<![\w-]){t}(?:e|s|es)?(?![\w-])")


MOTIFS = {lang: {t: motif(t) for t in lex if t not in LEX_CFG[lang]["sans_rappel"]} for lang, lex in LEXIQUES.items()}


def rappels_pour(texte, lang="fr"):
    """Mots-clés du lexique présents dans le texte, sauf ceux que la carte définit elle-même (« Bluff : … »)."""
    texte = texte.replace("**", "")
    dp = DEUX_POINTS[lang]
    out = []
    for terme, m in MOTIFS[lang].items():
        if m.search(texte) and f"{terme}{dp.rstrip()}" not in texte:
            out.append(f"**{terme}**{dp}{court(LEXIQUES[lang][terme])}" if lang == "fr"
                       else f"**{terme}:** {court(LEXIQUES[lang][terme])}")
    return out


def invoque(texte):
    t = texte.lower()
    return [j for j in ("pousse", "loup") if j in t and "jeton." not in t]


def lire_csv(chemin):
    with open(chemin, encoding="utf-8") as fh:
        return {r["id"]: r for r in csv.DictReader(fh)}


TR_CARTES = lire_csv(os.path.join(BIBLE_EN, "03_cartes_en.csv"))
TR_DONJON = lire_csv(os.path.join(BIBLE_EN, "05_donjon_mine_en.csv"))


def traduction(table, r, champs):
    """Ligne anglaise de la carte si elle traduit bien le français actuel ; sinon None (signalée « à retraduire »)."""
    tr = table.get(r["id"])
    if tr and all(tr[f"fr_{ch}"] == r[ch] for ch in champs):
        return tr
    A_RETRADUIRE.append(r["id"])
    return None


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
            tr = traduction(TR_CARTES, r, ("nom", "texte"))
            nom_en, texte_en, lang_en = (tr["nom"], tr["texte"], "en") if tr else (r["nom"], r["texte"], "fr")
            c["en"] = dict(name=nom_en, text=rich(texte_en, lang_en))
            if typ == "Terrain":
                # Recto verso : « recto || verso ». Recto illustré (ce que l'adversaire doit lire), verso = menu.
                recto, _, verso = r["texte"].partition(" || ")
                c["text"] = terrain_rich(recto)
                c["recto"] = True
                c["hp_terrain"] = pv
                recto_en, _, verso_en = texte_en.partition(" || ")
                c["en"]["text"] = terrain_rich(recto_en, lang_en)
                if verso:
                    c["back"] = dict(text=terrain_rich(verso), recto=False, big="MENU")
                    c["en"]["back"] = dict(text=terrain_rich(verso_en, lang_en))
            out.append(c)
    return out


def cartes_donjon():
    out = []
    with open(os.path.join(BIBLE, "05_donjon_mine.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            tr = traduction(TR_DONJON, r, ("nom", "texte", "evolue_nom", "evo_texte"))
            en = tr or dict(r)
            lang_en = "en" if tr else "fr"
            if r["type"] == "Relique":
                c = gen.C(r["id"], r["nom"], "Relique", 0, "Relique", rich(r["texte"]), legal=False, token=True)
                c["en"] = dict(name=en["nom"], text=rich(en["texte"], lang_en))
                out.append(c)
                continue
            c = gen.C(r["id"], r["nom"], r["type"], 0, gen.MINE, rich(r["texte"]), int(r["P"]), int(r["PV"]),
                      legal=False, token=True, tresors=int(r["tresors"]), relique=r["relique"] == "oui")
            c["en"] = dict(name=en["nom"], text=rich(en["texte"], lang_en))
            if r["evolue_nom"]:
                c["back"] = dict(name=r["evolue_nom"], power=int(r["evo_P"]), hp=int(r["evo_PV"]),
                                 tresors=int(r["evo_tresors"]), text=rich(r["evo_texte"]))
                c["en"]["back"] = dict(name=en["evolue_nom"], text=rich(en["evo_texte"], lang_en))
            out.append(c)
    return out


def communes():
    com = {c["id"]: c for c in gen.CARDS if c["id"] in ("energie", "carte-tresor")}
    com["carte-tresor"]["text"] = ("**Rattrapage.** Arrive à la fin de la manche 1 au Camp du joueur qui a le moins de trésors.\n"
                                   "**Retrait :** +1 trésor si tu es mené.\n"
                                   "**Raid :** un raid réussi peut la prendre à la place du 1er trésor volé.")
    com["carte-tresor"]["en"] = dict(name="Treasure Map", text=(
        "**Comeback.** Arrives at the end of round 1 in the Camp of the player with the least treasure.\n"
        "**Withdrawal:** +1 treasure if you're behind.\n"
        "**Raid:** a successful raid can take it instead of the 1st stolen treasure."))
    com["energie"]["en"] = dict(name="Energy", text=(
        "Tap it to pay 1.\nAll untap at your Rest.\nMax: 3 in round 1, +1 per round, 6 at most."))
    return list(com.values())


# Libellés dessinés sur les cartes anglaises (generate.py a les libellés français)
DESSIN_EN = dict(
    LABELS={"evolue_big": "EVOLVED", "relique": "◆ RELIC", "illus": "art to come", "evolue": " (evolved)",
            "tresor": ("treasure", "treasure"), "P": "PWR", "PV": "HP"},
    TYPE_LABEL={"Gardien": "Guardian", "Unite": "Unit", "Sort": "Spell", "Terrain": "Terrain", "Monstre": "Monster",
                "Boss": "Boss", "Relique": "Relic", "Tresor": "Treasure", "Energie": "Energy", "Menu": "Menu"},
    FACTION_LABEL={"Ivrognes": "Drunkards", "Druides": "Druids", "Mages": "Mages", gen.MINE: "Goblin Mine"},
)


def dessiner(c, chemin, lang):
    """Dessine la carte c dans la langue voulue (les libellés de generate.py sont remplacés le temps du dessin)."""
    if lang == "fr":
        return gen.draw_card(c, chemin)
    sauve = {k: getattr(gen, k) for k in DESSIN_EN}
    try:
        for k, v in DESSIN_EN.items():
            setattr(gen, k, dict(getattr(gen, k), **v))
        gen.draw_card(c, chemin)
    finally:
        for k, v in sauve.items():
            setattr(gen, k, v)


def par_langue(fr, en):
    return {"en": en, "fr": fr}


def ecrire_cartes(cards_list):
    out_dir = os.path.join(ROOT, "img", "cards")
    os.makedirs(out_dir, exist_ok=True)
    cards = {}
    for c in cards_list:
        en = c.get("en") or dict(name=c["name"], text=c["text"])
        versions = {"fr": dict(c), "en": dict(c, name=en["name"], text=en["text"])}
        suffixe = {"fr": "", "en": "-en"}
        noms, images, noms_b, images_b = {}, {}, {}, {}
        for lang, v in versions.items():
            v["rappels"] = rappels_pour(v["text"], lang)
            dessiner(v, os.path.join(out_dir, f"{c['id']}{suffixe[lang]}.png"), lang)
            noms[lang], images[lang] = v["name"], f"{BASE}/img/cards/{c['id']}{suffixe[lang]}.png"
            if c.get("back"):
                back = dict(c["back"], **(en.get("back") or {})) if lang == "en" else c["back"]
                b = dict(v, **back, verso=True, back=None)
                b["rappels"] = rappels_pour(b["text"], lang)
                dessiner(b, os.path.join(out_dir, f"{c['id']}-verso{suffixe[lang]}.png"), lang)
                noms_b[lang], images_b[lang] = b["name"], f"{BASE}/img/cards/{c['id']}-verso{suffixe[lang]}.png"
        nom = par_langue(noms["fr"], noms["en"])
        e = {"id": c["id"], "face": {"front": {"name": {"name": nom}, "type": c["type"], "cost": c["cost"],
                                               "image": par_langue(images["fr"], images["en"])}},
             "name": nom, "type": c["type"], "cost": c["cost"], "faction": c["faction"]}
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
            e["face"]["back"] = {"name": {"name": par_langue(noms_b["fr"], noms_b["en"])}, "type": c["type"], "cost": 0,
                                 "image": par_langue(images_b["fr"], images_b["en"])}
        if c.get("tresors") is not None:
            e["tresors"] = c["tresors"]
        cards[c["id"]] = e
    with open(os.path.join(ROOT, "cards.json"), "w", encoding="utf-8") as fh:
        json.dump(cards, fh, ensure_ascii=False, indent=2)
    for fn in os.listdir(out_dir):
        if fn.endswith(".png") and fn[:-4].removesuffix("-en").removesuffix("-verso") not in cards:
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


AIDE_EN = [  # à garder en phase avec AIDE
    "Guild Rush (proto) · dungeon: Goblin Mine. Full rules: livret/en/livret.md in the repository.",
    "Goal: the most treasure. End: a player at 12 treasure at the end of a round, or boss killed (end of that turn). Tie: the boss killer, then the most monsters killed.",
    "Board: 4 rooms in a row (neighbor = ±1), one monster each. Facing each room, one Expedition per player (3 units max, tokens included). The Camp touches all your Expeditions, no limit; it isn't a room.",
    "Turn: Rest (energy to max, 3 then +1 per round up to 6; draw 1; heal Recovering units; Guardian passive) → Scheme (Scouts, face-down Bluff, break camp) → Assault → Withdrawal (treasure to the counter, Terrain level).",
    "Assault: a unit you play arrives directly in the Expedition you want or in the Camp (TCG Arena puts it in Exp. 1: drag it). A unit in play moves once per turn (neighboring Expedition, Camp, or from the Camp to any Expedition). Wounded: only toward the Camp (Recovering).",
    "Combat (optional), room by room: Duel (announce it in the chat; the opponent answers first, then Reflex / Terrain bonus / pass; 2 passes = strikes). Then the monster strikes 1 attacker chosen by the opponent, your attackers strike together, then (Brawl) the enemy units. 1 strike per unit per turn.",
    "Killing blow: the killer (controller of the last damage) takes all the treasure and the relic. Fall back: after a lost Brawl, your units that attacked may return to the Camp. A spell is cast in a room where you have a unit (Reach: or neighboring).",
    "Raid (from round 2, 1 per Assault): after a kill in a room, your units in that room attack the enemy Camp. Success if more raiders than standing defenders (Guardian included): 1 treasure stolen, +1 if the Guardian is Knocked out.",
    "Monster killed: the host puts it in “Defeated monsters”, the killer adds its treasure (gold badge) to their counter. Relic icon: “Take the relic” in the Dungeon panel. Automatic: empty rooms refilled at the start of each turn; evolution at the end of the round.",
    "Terrain: starts next to the Guardian, drag it to an Expedition on your 1st Assault. Lvl 1 when placed, +1 at Withdrawal if it didn't move (3 max, lvl 3 = Stronghold). Break camp: neighboring Expedition, -1 level. Destroyed by the opponent: +1 treasure for them (plunder), comes back at lvl 1 on your next Assault.",
    "Counter = Treasure. HP and Power: card counters (right click > Toggle counter 1 = HP, key C; counter 2 = Power, Ctrl C). Tokens: Sap, Arcana, Wager, Level 1-3, states (Stunned, Poisoned, Swift, Unflinching, Tipsy, Hangover, Backlash, Snared, Recovering, Aegis, Trap, Glyph).",
    "Deck: 1 Guardian + 1 Terrain of its faction + 30 cards of the faction, including 20 min. from the Guardian's pool (3 copies max, Signature 1). TCG Arena doesn't check the rule of 20.",
    "Sprout and Wolf tokens: right click on the card that summons them.",
    "Language: Options menu (English / Français).",
]

# Textes affichés par TCG Arena (types, factions, zones, jetons, format, decks) : clé = texte du gamefile / de cards.json.
UI_EN = {
    "Gardien": "Guardian", "Unite": "Unit", "Sort": "Spell", "Terrain": "Terrain", "Monstre": "Monster", "Boss": "Boss",
    "Relique": "Relic", "Tresor": "Treasure", "Energie": "Energy",
    "Ivrognes": "Drunkards", "Druides": "Druids", "Mages": "Mages", "Mine des Gobelins": "Goblin Mine",
    "faction": "faction", "gardien": "guardian",
    "Proto (cartes de test)": "Proto (test cards)", "Compteur = Trésors": "Counter = Treasure",
    "Camp (blessées, reliques)": "Camp (wounded, relics)", "Monstre salle 1": "Room 1 monster",
    "Monstre salle 2": "Room 2 monster", "Monstre salle 3": "Room 3 monster", "Monstre salle 4": "Room 4 monster",
    "Boss (entre quand la pioche est vide)": "Boss (enters when the deck is empty)", "Pioche de monstres": "Monster deck",
    "Monstres vaincus": "Defeated monsters", "Énergie": "Energy", "Donjon": "Dungeon",
    "Expédition 1": "Expedition 1", "Expédition 2": "Expedition 2", "Expédition 3": "Expedition 3",
    "Expédition 4": "Expedition 4", "Coulisse": "Backstage",
    "Sève": "Sap", "Niveau 1": "Level 1", "Niveau 2": "Level 2", "Niveau 3 (Fief)": "Level 3 (Stronghold)",
    "Sonné : ne frappe pas à son prochain combat": "Stunned: doesn't strike in its next combat",
    "Empoisonné : perd 1 PV à chaque Repos de son propriétaire, jusqu'à être soigné":
        "Poisoned: loses 1 HP at each of its owner's Rests, until healed",
    "Rapide (gagné ce tour)": "Swift (gained this turn)",
    "Insensible : ne peut pas être Sonné ce tour (Whisky)": "Unflinching: can't be Stunned this turn (Whisky)",
    "Ivre : a bu un alcool ce tour (un 2e = Sonné)": "Tipsy: drank a drink this turn (a 2nd = Stunned)",
    "Gueule de bois : Sonné jusqu'à la fin de ton prochain tour (Rhum)": "Hangover: Stunned until the end of your next turn (Rum)",
    "Contrecoup : perd 2 PV à ton prochain Repos (Absinthe)": "Backlash: loses 2 HP at your next Rest (Absinthe)",
    "Entravé : ne peut pas changer de salle (Toile)": "Snared: can't change room (Web)",
    "En soin : blessé au Camp, soigné à ton prochain Repos puis reste au Camp ce tour":
        "Recovering: wounded in the Camp, healed at your next Rest then stays in the Camp that turn",
    "Piège (Éclaireur), face cachée ; Leurre possible": "Trap (Scout), face down; Decoy possible",
    "Arcane (Mages) : jetons sur le cercle, payent les Incantations": "Arcana (Mages): tokens on the circle, pay for Incantations",
    "Mise (Tonneau des paris) : 3 Mises = 1 trésor au Retrait": "Wager (Betting Keg): 3 Wagers = 1 treasure at Withdrawal",
    "Égide : ignore le prochain coup reçu": "Aegis: ignores the next hit received",
    "Glyphe (Mages) : 1 dégât et Sonné à la 1re unité adverse qui entre ou attaque ici":
        "Glyph (Mages): 1 damage and Stunned to the 1st enemy unit that enters or attacks here",
    "Ivrognes de Guss — La Taverne": "Guss's Drunkards — The Tavern", "Ivrognes de Rosa — Poudrière": "Rosa's Drunkards — Powder Keg",
    "Ivrognes de Robin — Tapis vert": "Robin's Drunkards — Green Felt",
    "Druides de Cernun — Bosquet ancien": "Cernun's Druids — Ancient Grove", "Druides de Belladone — Ronces": "Belladonna's Druids — Brambles",
    "Druides de Sylve — La Meute": "Sylve's Druids — The Pack", "Mages de Soffia — Arcanes": "Soffia's Mages — Arcana",
    "Mages d'Orsin — Runes": "Orsin's Mages — Runes", "Mages d'Ignis — Brasier": "Ignis's Mages — Blaze",
}
UI_FR = {"Unite": "Unité", "Tresor": "Trésor", "Energie": "Énergie"}   # le reste du gamefile est déjà en français

# Étiquettes dessinées sur le plateau (fond SVG des zones) : bilingues, TCG Arena ne les traduit pas.
ETIQUETTES = {"EXPÉDITION": "EXP.", "MONSTRE": "MONSTRE · MONSTER", "GARDIEN": "GARDIEN · GUARDIAN",
              "ÉNERGIE": "ÉNERGIE · ENERGY", "PIOCHE": "PIOCHE · DECK", "DÉFAUSSE": "DÉFAUSSE · DISCARD",
              "CAMP · DÉFENSEURS, BLESSÉES, RELIQUES": "CAMP · DEFENDERS / DÉFENSEURS"}


def etiquette(m):
    txt = urllib.parse.unquote(m.group(1))
    for fr, bi in ETIQUETTES.items():
        if txt == fr or txt.startswith(fr + " ") and txt[len(fr) + 1:].isdigit():
            txt = bi + txt[len(fr):]
            break
    return "%3E" + urllib.parse.quote(txt, safe=" ,/") + "%3C/text%3E"


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
    aide_fr = "\n".join(AIDE + ["", "LEXIQUE (bible/00_glossaire.md ; rappelé en bas des cartes qui l'utilisent)"]
                        + [f"{t} : {d}" for t, d in LEXIQUES["fr"].items() if t in MOTIFS["fr"]])
    aide_en = "\n".join(AIDE_EN + ["", "GLOSSARY (bible/en/00_glossaire_en.md; recalled at the bottom of the cards that use it)"]
                        + [f"{t}: {d}" for t, d in LEXIQUES["en"].items() if t in MOTIFS["en"]])
    g["customHelp"] = aide_en
    g["translationsUrl"] = f"{BASE}/translations.json"
    if "gardien" not in g["deckBuilding"]["mainFilters"]:
        g["deckBuilding"]["mainFilters"].insert(1, "gardien")
    G["sections"] = json.loads(re.sub(r"%3E((?:(?!%3[CE]).)*?)%3C/text%3E", etiquette,
                                      json.dumps(G["sections"], ensure_ascii=False)))
    json.dump(g, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    tr = {"additionalLanguages": ["fr"],
          "en": {"Interface": UI_EN, "UI text": {"translations.customHelp": aide_en}},
          "fr": {"Interface": UI_FR, "UI text": {"translations.customHelp": aide_fr}}}
    json.dump(tr, open(os.path.join(ROOT, "translations.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


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


def verifier_glossaire():
    """Signale si le glossaire français a changé depuis la traduction anglaise (empreinte en tête de 00_glossaire_en.md)."""
    sha = hashlib.sha1(open(os.path.join(BIBLE, "00_glossaire.md"), "rb").read()).hexdigest()
    if sha not in open(LEX_CFG["en"]["fichier"], encoding="utf-8").read():
        print(f"  ! bible/en/00_glossaire_en.md : à retraduire (00_glossaire.md a changé ; nouvelle empreinte {sha})")


def main():
    cards = ecrire_cartes(cartes_guildes() + cartes_donjon() + communes())
    maj_gamefile()
    print(len(cards), "cartes (fr + en)")
    if A_RETRADUIRE:
        print(f"  ! à retraduire dans bible/en/ (affichées en français en attendant) : {', '.join(A_RETRADUIRE)}")
    verifier_glossaire()
    verifier_decks(cards)


if __name__ == "__main__":
    main()
