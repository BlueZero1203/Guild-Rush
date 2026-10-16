#!/usr/bin/env python3
"""Test des langues TCG Arena : 3 cartes avec nom et image par langue (en / fr). À supprimer après le test."""
import copy, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import from_bible as fb  # noqa: E402

RAW = "https://raw.githubusercontent.com/BlueZero1203/Guild-Rush/test-langues/test-langues"
EN = {
    "guss": ("Guss the Innkeeper", "Rest: heal 2 HP on your barrel. / Dish of the day: at Stratagem, choose an alcohol at 1 HP; your first pint of that alcohol costs 0 HP this turn. / Camp defense: your defenders have +1 Power."),
    "serveuse": ("Barmaid", "Arrival: one of your units gets +1/+1."),
    "grosse-pinte": ("Big Pint", "A unit gets +2/+2 this turn."),
}
here = os.path.dirname(os.path.abspath(__file__))
src = {c["id"]: c for c in fb.cartes_guildes() if c["id"] in EN}
cards = json.load(open(os.path.join(here, "..", "cards.json"), encoding="utf-8"))
for cid, (nom, texte) in EN.items():
    c = copy.deepcopy(src[cid])
    c["name"], c["text"], c["rappels"] = nom, fb.rich(texte), []
    fb.gen.draw_card(c, os.path.join(here, "img", f"{cid}-en.png"))
    e = cards[cid]
    fr_img = e["face"]["front"]["image"]
    e["face"]["front"]["image"] = {"en": f"{RAW}/img/{cid}-en.png", "fr": fr_img}
    e["face"]["front"]["name"]["name"] = {"en": nom, "fr": e["name"]}
    e["name"] = {"en": nom, "fr": e["name"]}
json.dump(cards, open(os.path.join(here, "cards.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

g = json.load(open(os.path.join(here, "..", "gamefile.json"), encoding="utf-8"))
g["name"] = "Guild Rush (test langues)"
g["cards"]["dataUrl"] = f"{RAW}/cards.json"
g["translationsUrl"] = f"{RAW}/translations.json"
json.dump(g, open(os.path.join(here, "gamefile.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

tr = {"additionalLanguages": ["fr"],
      "en": {"Types": {"Unite": "Unit", "Sort": "Spell", "Gardien": "Guardian"},
             "UI text": {"translations.customHelp": "ENGLISH HELP (test). If you read this, the help follows the language."}},
      "fr": {"Types": {"Unite": "Unité", "Sort": "Sort", "Gardien": "Gardien"},
             "UI text": {"translations.customHelp": "AIDE EN FRANÇAIS (test). Si tu lis ceci, l'aide suit la langue."}}}
json.dump(tr, open(os.path.join(here, "translations.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok")
