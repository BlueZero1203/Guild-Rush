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
g['deckBuilding']['formats'][0]['customCategories'] = ['Gardien', 'Terrain']
g['deckBuilding']['deckRulesets']['Proto']['categories'] = [
    {'category': 'Gardien', 'min': 1, 'max': 1, 'ignoreTotalCount': True},
    {'category': 'Terrain', 'min': 1, 'max': 1, 'ignoreTotalCount': True}]
S['categoriesAlreadyOnBoard'] = ['Gardien->Gardien', 'Terrain->Gardien']

# --- sections : plus de Réserve ; Terrain dans l'Expédition 1 (à déplacer), Menu près du Gardien ---
D.pop('Reserve', None)
for m in ('autoPlayFromHand', 'autoPlayFromStack'):
    for k in ('Alcool', 'Ingredient', 'Baril', 'Recettes'):
        S[m].pop(k, None)
    S[m].pop('Menu', None)
    S[m]['Terrain'] = 'BF1'
D['Gardien']['displayedTitle'] = 'Gardien'

# --- jetons à poser sur les cartes (glisser depuis le panneau des jetons) ---
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def jeton(nom, txt, coul):
    im = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, 116, 116), fill=coul, outline=(255, 255, 255), width=5)
    lignes = txt.split('|')
    size = 40
    while size > 12:
        f = ImageFont.truetype(FB, size)
        if max(d.textlength(l, font=f) for l in lignes) <= 92 and size * 1.15 * len(lignes) <= 84:
            break
        size -= 1
    y0 = 60 - (len(lignes) - 1) * size * 0.58
    for k, l in enumerate(lignes):
        d.text((60, y0 + k * size * 1.16), l, font=f, fill=(255, 255, 255), anchor='mm')
    im.save(f'img/tokens/{nom}.png')
JETONS = [  # id, nom affiché, texte, couleur
    ('Seve', 'Sève', 'SÈVE', (60, 150, 70)),
    ('Niv1', 'Niveau 1', 'NIV|1', (200, 150, 30)), ('Niv2', 'Niveau 2', 'NIV|2', (215, 130, 20)),
    ('Niv3', 'Niveau 3 (Fief)', 'NIV|3', (230, 100, 10)),
    ('Sonne', 'Sonné', 'SONNÉ', (120, 70, 170)), ('Rapide', 'Rapide', 'RAPIDE', (30, 150, 190)),
    ('PlusP', '+1 Puissance', '+1|P', (190, 50, 45)), ('PlusPV', '+1 PV', '+1|PV', (40, 90, 190)),
    ('Biere', 'Bière (+1 P)', 'BIÈRE', (205, 160, 40)), ('Cidre', 'Cidre (+2 PV)', 'CIDRE', (150, 170, 50)),
    ('Rhum', 'Rhum (+2 P, Sonnée ensuite)', 'RHUM', (140, 70, 30)), ('Whisky', 'Whisky (pas Sonnée)', 'WHISKY', (170, 110, 40)),
    ('Absinthe', 'Absinthe (+3 P, -2 PV au Repos)', 'ABSIN|THE', (70, 150, 60)),
    ('Piege', 'Piège', 'PIÈGE', (90, 90, 90)),
]
for tid, _, txt, coul in JETONS:
    jeton(tid.lower(), txt, coul)
for old in ('seve.png', 'niveau.png'):
    if os.path.exists('img/tokens/' + old) and old[:-4] not in [t[0].lower() for t in JETONS]:
        os.remove('img/tokens/' + old)
G['draggableTokens'] = [{'id': 'Degat', 'name': 'Dégât', 'image': BASE + '/img/tokens/degat.png'}] + [
    {'id': tid, 'name': nom, 'image': BASE + '/img/tokens/' + tid.lower() + '.png'} for tid, nom, _, _ in JETONS]
for t in G.get('tokens', []):
    t['image'] = BASE + '/img/tokens/' + t['image'].rsplit('/', 1)[1]

# --- aide ---
h = g['customHelp'].split('\n')
h = [l for l in h if not l.startswith('Réserve (8 cartes)') and not l.startswith('Jetons Pousse')]
h = [l.replace('Expéditions 1-4, Gardien, Réserve ; Énergie et Camp', 'Expéditions 1-4, Gardien ; Énergie et Camp')
      .replace('chacun joue une carte Rapide ou instantanée ou passe', 'chacun joue une carte Rapide, ou un bonus de son Terrain si le Duel a lieu dans sa salle, ou passe').replace('Jetons Dégât et Baril à poser sur les cartes.', 'Jetons (panneau des jetons, à glisser sur les cartes) : Dégât, Sève, Niveau 1-3, Sonné, Rapide, +1 Puissance, +1 PV, alcools, Piège.') for l in h]
h += [
    "Deck : 1 Gardien + 1 Terrain de la même faction (n'importe lequel) + 30 cartes. Le Terrain commence à côté du Gardien : glisse-le dans l'Expédition voulue à ton 1er Assaut. Il porte les bonus de la guilde (alcools, recettes) et leur prix.",
    "Bonus du Terrain : à ton Assaut, ou pendant n'importe quel Duel dans la salle de ton Terrain (même au tour adverse). Ils visent tes unités de cette salle. Pose un jeton d'effet pour t'en souvenir.",
    "Niveau : jeton Niv 1 à la pose. À ton Retrait, +1 s'il était déjà à sa place au début du tour (3 max). Niv. 1 bonus de lieu, niv. 2 ressource renforcée, niv. 3 Fief (+1 trésor par monstre tué ici). Lever le camp (Stratagème) : Expédition voisine, -1 niveau.",
    "Le Terrain a des PV, ne frappe pas, ne bloque pas les raids. Une unité adverse qui combat dans sa salle peut l'attaquer. Détruit par l'adversaire : +1 trésor pour lui (pillage) ; il revient au niveau 1 à ton Assaut suivant.",
    "Ivrognes : tirer une pinte = jetons Dégât sur le baril (1 PV, 2 pour un alcool fort) + jeton de l'alcool sur l'unité. 2 pintes par tour, 3 au niveau 2. Dernière tournée : la pinte peut vider le baril, qui explose (sans pillage). Guss soigne 2 PV au Repos.",
    "Druides : jetons Sève sur ton bosquet (4 max), +1 à ton Repos (+2 au niveau 2). 1 recette par tour, payée en Sève. Bosquet détruit : tu perds la moitié de ta Sève.",
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
    L['Terrain'] = [{'id': 'baril-chene' if d['id'] == 'precon-ivrognes' else 'bosquet', 'count': 1}]
    L['categoriesOrder'] = ['Gardien', 'Terrain', 'Unite', 'Sort']
    if d['id'] == 'precon-druides':
        sorts = [e for e in L['Sort'] if e['id'] != 'transplantation']
        for e in sorts:
            if e['id'] == 'croissance':
                e['count'] = 2
        L['Sort'] = sorts + [{'id': 'transplantation', 'count': 1}]
    assert sum(e['count'] for k in ('Unite', 'Sort') for e in L[k]) == 30, d['id']
json.dump(dk, open('decks.json', 'w'), ensure_ascii=False, indent=2)
print('format v3 (Terrains) ok')
