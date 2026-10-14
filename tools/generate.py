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
    "Test": ((34, 44, 60), (110, 130, 160)),
    "Monstre": ((80, 30, 30), (190, 70, 60)),
    "Boss": ((55, 15, 15), (225, 60, 40)),
    "Relique": ((70, 58, 22), (225, 190, 70)),
    "Energie": ((18, 55, 66), (70, 195, 210)),
}
TYPE_LABEL = {"Gardien": "Gardien", "Unite": "Unité", "Sort": "Sort", "Baril": "Baril",
              "Monstre": "Monstre", "Boss": "Boss", "Relique": "Relique", "Tresor": "Trésor",
              "Energie": "Énergie", "Alcool": "Alcool"}


def C(id, name, type, cost, faction, text="", power=None, hp=None, legal=3, token=False):
    return dict(id=id, name=name, type=type, cost=cost, faction=faction, text=text,
                power=power, hp=hp, legal=legal, token=token)


IVR = "Ivrognes"
CARDS = [
    # --- Ivrognes : Guss et son baril ---
    C("guss", "Guss le tavernier", "Gardien", 0, IVR,
      "**Maître de guilde** : à chaque tour, si le baril est endommagé, Guss le soigne complètement. "
      "**Patron du bar** : quand Guss défend le Camp, tes défenseurs ont +1 Puissance. "
      "**Coup de torchon** : la première unité qui attaque Guss pendant un raid est Sonnée.",
      3, 7, legal=1),
    C("baril", "Le baril", "Baril", 0, IVR,
      "Un seul baril, posé dans une salle au premier Crépuscule ; ne rentre jamais au Camp. "
      "**Aura** : tes unités de sa salle ont +1 Puissance. **Encaisser** : il peut prendre les dégâts "
      "d'une de tes unités de sa salle. **Tirer une pinte** : 1 fois par tour, retire-lui 1 PV pour piocher "
      "1 carte de la Cave. **Explosion** à 0 PV : 1 dégât à tout ce qui est dans la salle.",
      0, 6, legal=1),
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
      "Expulse une unité adverse d'une salle : elle retourne en Expédition, Sonnée."),
    C("ma-tournee", "C'EST MA TOURNÉE !", "Sort", 5, IVR,
      "Toutes tes unités en jeu sont soignées et gagnent +1/+1 jusqu'à la fin du tour. "
      "Tes blessées du Camp reviennent en Expédition. +1 Puissance de plus si ton baril est intact. "
      "**Signature** : 1 exemplaire max.", legal=1),
    # --- Ivrognes : la Cave (Réserve de faction) ---
    C("biere", "Bière blonde", "Alcool", 0, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat). +1 Puissance.", legal=3),
    C("cidre", "Cidre", "Alcool", 0, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat). +1 PV.", legal=2),
    C("hydromel", "Hydromel", "Alcool", 1, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat). +2 PV et soigne 2 PV en s'attachant.", legal=2),
    C("rhum", "Rhum", "Alcool", 1, IVR,
      "**Alcool** (sur ton unité dans la salle du baril, même en combat). +2 Puissance. **Gueule de bois** : à la Nuit, l'unité est Sonnée pour le tour suivant.", legal=1),
    C("whisky", "Whisky tourbé", "Alcool", 1, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat). L'unité ne peut pas être Sonnée.", legal=1),
    C("vin-chaud", "Vin chaud", "Alcool", 1, IVR, "**Alcool** (sur ton unité dans la salle du baril, même en combat). Soigne complètement l'unité en s'attachant.", legal=1),
    C("absinthe", "Absinthe", "Alcool", 1, IVR,
      "**Alcool** (sur ton unité dans la salle du baril, même en combat). +3 Puissance. Au début de ton tour suivant, l'unité perd 2 PV.", legal=1),
    C("liqueur-feu", "Liqueur de feu", "Alcool", 1, IVR,
      "**Alcool** (sur ton unité dans la salle du baril, même en combat). Quand l'unité meurt : 2 dégâts à chaque ennemi de sa salle.", legal=1),
    # --- Cartes de test (en attendant les Druides) ---
    C("gardien-druide", "Druide (nom temporaire)", "Gardien", 0, "Test",
      "Passif : à chaque monstre tué, récolte un ingrédient.", 2, 8, legal=1),
    C("unite-a", "Unité test A", "Unite", 1, "Test", "Unité de base.", 2, 3, legal=8),
    C("unite-b", "Unité test B", "Unite", 2, "Test", "Unité de base.", 3, 2, legal=8),
    C("unite-c", "Unité test C", "Unite", 3, "Test", "Unité de base.", 3, 5, legal=8),
    C("unite-d", "Unité test D", "Unite", 4, "Test", "Unité de base.", 5, 4, legal=8),
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


def rich_lines(draw, text, fnt, fnt_b, max_w):
    """Découpe un texte avec **gras** en lignes de segments (mot, gras?)."""
    words = []
    for i, part in enumerate(re.split(r"\*\*", text)):
        for w in part.split():
            words.append((w, i % 2 == 1))
    lines, cur, cur_w = [], [], 0
    space = draw.textlength(" ", font=fnt)
    for w, b in words:
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
