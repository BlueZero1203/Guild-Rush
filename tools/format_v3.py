"""Format Terrains (2026-10-15) : plus de Réserve ; le Gardien vient avec un Terrain et un Menu.
Ordre : generate.py, board_layout.py, format_v2.py, puis  python3 tools/format_v3.py
L'ancien système est sur la branche archive-reserve."""
import json, os
from PIL import Image, ImageDraw, ImageFont

P = 'gamefile.json'
REF = os.environ.get('GR_REF', 'main')
BASE = 'https://raw.githubusercontent.com/BlueZero1203/Guild-Rush/' + REF
g = json.load(open(P))
G = g['gameplay']['Standard']
S = G['sections']
D = S['sectionsDict']

# --- construction : 1 Gardien + 30 cartes, c'est tout ---
g['deckBuilding']['formats'][0]['customCategories'] = ['Gardien']
g['deckBuilding']['deckRulesets']['Proto']['categories'] = [
    {'category': 'Gardien', 'min': 1, 'max': 1, 'ignoreTotalCount': True}]
S['categoriesAlreadyOnBoard'] = ['Gardien->Gardien']

# --- sections : plus de Réserve ; Terrain dans l'Expédition 1 (à déplacer), Menu près du Gardien ---
D.pop('Reserve', None)
for m in ('autoPlayFromHand', 'autoPlayFromStack'):
    for k in ('Alcool', 'Ingredient', 'Baril', 'Recettes'):
        S[m].pop(k, None)
    S[m]['Terrain'] = 'BF1'
    S[m]['Menu'] = 'Gardien'
D['Gardien']['displayedTitle'] = 'Gardien et Menu'

# --- jetons à poser sur les cartes : Dégât, Sève, Niveau ---
def jeton(nom, txt, coul):
    im = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, 116, 116), fill=coul, outline=(255, 255, 255), width=5)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
    d.text((60, 62), txt, font=f, fill=(255, 255, 255), anchor='mm')
    im.save(f'img/tokens/{nom}.png')
jeton('seve', 'S', (60, 150, 70))
jeton('niveau', 'N', (200, 150, 30))
G['draggableTokens'] = [t for t in G['draggableTokens'] if t['id'] not in ('Baril', 'Seve', 'Niveau')] + [
    {'id': 'Seve', 'name': 'Sève', 'image': BASE + '/img/tokens/seve.png'},
    {'id': 'Niveau', 'name': 'Niveau', 'image': BASE + '/img/tokens/niveau.png'}]
for t in G['draggableTokens'] + G.get('tokens', []):
    t['image'] = BASE + '/img/tokens/' + t['image'].rsplit('/', 1)[1]

# --- aide ---
h = g['customHelp'].split('\n')
h = [l for l in h if not l.startswith('Réserve (8 cartes)') and not l.startswith('Jetons Pousse')]
h = [l.replace('Expéditions 1-4, Gardien, Réserve ; Énergie et Camp', 'Expéditions 1-4, Gardien et son Menu ; Énergie et Camp')
      .replace('chacun joue une carte Rapide ou instantanée ou passe', 'chacun joue une carte Rapide ou un effet de son Menu, ou passe').replace('Jetons Dégât et Baril à poser sur les cartes.', 'Jetons Dégât, Sève et Niveau à poser sur les cartes.') for l in h]
h += [
    "Gardien : clic droit dessus pour créer son Terrain (baril, bosquet) et son Menu (Carte des alcools, Livre). Le Menu va près du Gardien ; le Terrain arrive dans l'Expédition 1 : glisse-le dans l'Expédition voulue au 1er Assaut.",
    "Terrain : son niveau se note avec un jeton Niveau ou le compteur de la carte (clic droit > Toggle counter, touche C) ; +1 à chacun de tes Retraits s'il est debout (3 max). Niv. 1 bonus de lieu, niv. 2 ressource renforcée, niv. 3 Fief (+1 trésor par monstre tué ici). Lever le camp (Stratagème) : Expédition voisine, -1 niveau. Détruit par l'adversaire : il pille 1 trésor ; le Terrain revient au niveau 1 à ton Assaut suivant.",
    "Ivrognes : tirer une pinte = jetons Dégât sur le baril (1 PV, 2 pour un alcool fort), annonce l'alcool dans le chat. 2 pintes par tour, 3 au niveau 2. Guss soigne 2 PV au Repos.",
    "Druides : la Sève = jetons Sève ou compteur sur ton Livre (4 max), +1 à ton Repos (+2 au niveau 2). 1 recette par tour, payée en Sève. Bosquet détruit : tu perds la moitié de ta Sève.",
    "Jetons Pousse et Loup : clic droit sur la carte qui les invoque.",
]
g['customHelp'] = '\n'.join(h)
json.dump(g, open(P, 'w'), ensure_ascii=False, indent=2)

# --- decks préconstruits : plus de Réserve ; Transplantation chez les Druides ---
dk = json.load(open('decks.json'))
for d in dk:
    L = d['deckList']
    for k in ('Alcool', 'Ingredient', 'Relique'):
        L.pop(k, None)
    L['categoriesOrder'] = [c for c in L['categoriesOrder'] if c in ('Gardien', 'Unite', 'Sort')]
    if d['id'] == 'precon-druides':
        sorts = [e for e in L['Sort'] if e['id'] != 'transplantation']
        for e in sorts:
            if e['id'] == 'croissance':
                e['count'] = 2
        L['Sort'] = sorts + [{'id': 'transplantation', 'count': 1}]
    assert sum(e['count'] for k in ('Unite', 'Sort') for e in L[k]) == 30, d['id']
json.dump(dk, open('decks.json', 'w'), ensure_ascii=False, indent=2)
print('format v3 (Terrains) ok')
