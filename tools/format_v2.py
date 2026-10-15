"""Nouveau format (2026-10-15) : donjon préconstruit, énergie par manche, deck 30, Réserve 8.
À lancer après generate.py et board_layout.py :  python3 tools/format_v2.py
Idempotent : réécrit entièrement les parties concernées de gamefile.json et decks.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate import DONJONS  # noqa: E402

P = 'gamefile.json'
g = json.load(open(P))
G = g['gameplay']['Standard']
S = G['sections']
D = S['sectionsDict']
DJ = DONJONS['mine']
SALLES = ['Salle1', 'Salle2', 'Salle3', 'Salle4']

# --- Lanterne : le monstre du dessus passe sous la pioche ---
# La pioche de monstres est dans la zone partagée : c'est l'hôte qui en garde l'ordre, et les boutons « To bottom »
# du simulateur y sont annulés. On passe donc par un script exécuté chez l'hôte, via une section cachée « Coulisse ».
DESSOUS = ("const n=(cards.Monstres??[]).length;"
           "if(n<2){functions.chatLog('Lanterne : rien à réordonner.');}else{"
           "await functions.drawFromExtraDeck('Monstres',1,false,'Coulisse');"
           "for(let i=0;i<n-1;i++){await functions.drawFromExtraDeck('Monstres',1,true,'Coulisse');}"
           "for(let i=0;i<n;i++){await functions.drawFromExtraDeck('Coulisse',1,true,'Monstres');}"
           "functions.chatLog('Lanterne : le monstre du dessus est passé sous la pioche.');"
           "await functions.repositionCards();}")
LANTERNE_CLICK = ("const d=game.data.Donjon;"
                  "if(!game.isHost){d.lanterne=Date.now();functions.chatLog('Lanterne : demande envoyée à l’hôte.');return;}"
                  "d.lanterne=Date.now();d.lanterneFait=d.lanterne;" + DESSOUS)
ON_UPDATE = ("if(!game.isHost)return;const d=game.data.Donjon;"
             "if(d.lanterne&&d.lanterne!==d.lanterneFait){d.lanterneFait=d.lanterne;" + DESSOUS + "}")


# --- construction de deck : 30 cartes, 1 Gardien, Réserve de 8, plus de reliques dans les decks ---
fmt = g['deckBuilding']['formats'][0]
fmt['customCategories'] = ['Gardien', 'Alcool', 'Ingredient']
g['deckBuilding']['deckRulesets']['Proto'] = {
    'checkCardLegality': True,
    'general': {'min': 30, 'max': 30, 'maxPerCard': 3},
    'categories': [
        {'category': 'Gardien', 'min': 1, 'max': 1, 'ignoreTotalCount': True},
        {'category': 'Alcool', 'min': 0, 'max': 8, 'ignoreTotalCount': True},
        {'category': 'Ingredient', 'min': 0, 'max': 8, 'ignoreTotalCount': True},
    ]}
S['categoriesAlreadyOnBoard'] = ['Gardien->Gardien', 'Alcool->Reserve', 'Ingredient->Reserve']
for m in ('autoPlayFromHand', 'autoPlayFromStack'):
    S[m]['Monstre'] = 'Salle1'
    S[m]['Relique'] = 'Camp'

# --- sections : plus de pioche d'énergie ni de pioche de reliques ---
for k in ('PiocheEnergie', 'Relique'):
    D.pop(k, None)
D['Energie']['keepTappedNewTurn'] = True   # c'est le script du Repos qui redresse (et ajoute) l'énergie
if 'Reserve' in D: D['Reserve']['displayedTitle'] = 'Réserve'
D['Boss']['displayedTitle'] = 'Boss (entre quand la pioche est vide)'
D['Monstres']['displayedTitle'] = 'Pioche de monstres'
D['CimetiereMonstres']['displayedTitle'] = 'Monstres vaincus'

# --- mise en place : 3 énergies chacun ; le donjon chez l'hôte ---
setup0 = [{'createCardId': 'energie', 'count': 3, 'destination': 'Energie'},
          {'createCardId': DJ['boss'], 'count': 1, 'destination': 'Boss', 'overrideState': {'isHidden': 'no'}}]
setup0 += [{'createCardId': m, 'count': 1, 'destination': 'Monstres'} for m in DJ['monstres']]
G['beforeGameStart']['initialBoardSetup'] = {'0': setup0,
                                             '1': [{'createCardId': 'energie', 'count': 3, 'destination': 'Energie'}]}

# --- panneau Donjon ---
REL_NOMS = {'lanterne': 'Lanterne du mineur', 'pioche-runique': 'Pioche runique', 'bourse': 'Bourse du contremaître'}
dj = D['Donjon']
dj['defaultValue'] = {'nom': DJ['nom'], 'manche': 1, 'pioche': 4, 'boss': False,
                      'arrivee': {s: 0 for s in SALLES}, 'reliques': list(DJ['reliques'])}
txt = {'type': 'div', 'props': {'style': {'fontSize': '0.85em', 'opacity': '0.85'}}}
dj['blueprint']['children'] = [
    {'type': 'div', 'props': {'style': {'fontSize': '1.0em', 'fontWeight': 'bold'}},
     'children': '{{ game.data.Donjon.nom }}'},
    {'type': 'div', 'props': {'style': {'fontSize': '1.15em', 'fontWeight': 'bold', 'color': '#f0c040'}},
     'children': 'Manche {{ game.data.Donjon.manche }}'},
    dict(txt, children="{{ game.data.Donjon.boss ? 'Le boss est entré !' : 'Pioche : ' + game.data.Donjon.pioche + ' monstre(s)' }}"),
    dict(txt, children="Reliques : {{ (game.data.Donjon.reliques || []).length }} / 3"),
    {'type': 'button', 'props': {'className': 'btn btn-warning btn-sm'},
     'onClick': ("const d=game.data.Donjon;const r=d.reliques||[];"
                 "if(!r.length){functions.chatLog('Plus aucune relique dans le donjon.');return;}"
                 "const id=r[0];d.reliques=r.slice(1);"
                 "await functions.createCard(id,'Camp');"
                 "functions.chatLog('Relique gagnée : '+(%s[id]||id)+' (au Camp).');"
                 "await functions.repositionCards();") % json.dumps(REL_NOMS, ensure_ascii=False),
     'children': 'Prendre la relique'},
    {'type': 'button', 'props': {'className': 'btn btn-secondary btn-sm', 'title': "Lanterne : le monstre du dessus de la pioche passe en dessous"},
     'onClick': LANTERNE_CLICK, 'children': 'Dessus → dessous'},
]

ON_READY = ("if(!game.isHost)return;\n"
            "await functions.shuffleSection('Monstres');\n"
            "const d=game.data.Donjon;\n"
            "for(const s of ['Salle1','Salle2','Salle3','Salle4']){await functions.drawFromExtraDeck('Monstres',1,false,s);d.arrivee[s]=0;}\n"
            "d.manche=1;d.pioche=4;d.boss=false;\n"
            "const r=[...(d.reliques||[])];for(let i=r.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[r[i],r[j]]=[r[j],r[i]];}d.reliques=r;\n"
            "functions.chatLog('Mine des Gobelins : 4 monstres dans les salles, 4 dans la pioche, puis Grombak.');\n"
            "await functions.repositionCards();")

ON_TURN = """const n=game.turn?.count??1, tp=game.turn?.totalPlayers||2;
const m=Math.ceil(n/tp);
if(game.turn?.isMyTurn){
  const max=Math.min(6,2+m);
  const en=cards.Energie??[];
  for(let i=en.length;i<max;i++){await functions.createCard('energie','Energie');}
  const t=en.filter(c=>c.isTapped);
  if(t.length){await functions.updateCards(t,{isTapped:false});}
  functions.chatLog('Repos (manche '+m+') : énergie '+max+' / '+max+'.');
}
if(game.isHost && n>1){
  const d=game.data.Donjon; d.arrivee=d.arrivee||{};
  const pm=Math.ceil((n-1)/tp);
  const salles=['Salle1','Salle2','Salle3','Salle4'];
  let pioche=(cards.Monstres??[]).length; const boss=(cards.Boss??[])[0];
  for(const s of salles){
    if((cards[s]??[]).length) continue;
    if(pioche>0){await functions.drawFromExtraDeck('Monstres',1,false,s);pioche--;d.arrivee[s]=pm;functions.chatLog('Retrait : un monstre entre dans la salle '+s.slice(-1)+'.');}
    else if(boss && !d.boss){await functions.moveCard(boss,s);d.boss=true;d.arrivee[s]=pm;functions.chatLog('Retrait : le boss entre dans la salle '+s.slice(-1)+' !');}
  }
  if(m>pm){
    const evo=[];
    for(const s of salles){for(const c of (cards[s]??[])){
      if(!c.isFlipped && (d.arrivee[s]??0)<pm && functions.getCardData(c)?.type==='Monstre') evo.push(c);}}
    if(evo.length){await functions.updateCards(evo,{isFlipped:true});functions.chatLog('Fin de manche '+pm+' : '+evo.length+' monstre(s) évoluent.');}
    d.manche=m;
  }
  d.pioche=pioche;
  await functions.repositionCards();
}"""
dj['events'] = {'onPlayersReady': ON_READY, 'onNewTurn': ON_TURN, 'onUpdate': ON_UPDATE}
D['Coulisse'] = {'isHidden': 'yes', 'height': 1, 'alignment': 'DECK', 'displayedTitle': 'Coulisse'}

# --- aide ---
g['customHelp'] = "\n".join([
    "Guild Rush (proto) · donjon : Mine des Gobelins. Fin : boss vaincu (fin de ce tour) ou un joueur à 12 trésors en fin de manche.",
    "Plateau : 4 monstres au centre, pioche de monstres, boss, monstres vaincus, panneau Donjon. En face de chaque monstre, une Expédition par joueur (3 unités max, jetons compris). Ta zone : Expéditions 1-4, Gardien, Réserve ; Énergie et Camp.",
    "Ton tour : Repos (automatique : énergie au max, +1 par manche jusqu'à 6 ; pioche 1 ; passif du Gardien) → Stratagème (Éclaireurs, cartes face cachée) → Assaut → Retrait (trésors sur ton compteur, soins au Camp).",
    "Assaut : pose tes unités (elles arrivent dans l'Expédition 1 : déplace-les dans l'Expédition voulue ou au Camp). Une unité intacte déjà en jeu peut aller dans une Expédition voisine ou au Camp, une fois par tour. Puis attaque salle par salle : chaque attaque ouvre un Duel (annonce-le dans le chat). L'adversaire répond en premier, puis chacun joue une carte Rapide ou instantanée ou passe ; deux passes = combat. Les deux joueurs dans la salle : mêlée (le monstre frappe d'abord, coup de grâce). Puis 1 raid au plus.",
    "Monstre tué : l'hôte le met dans « Monstres vaincus », le tueur ajoute ses trésors (pastille dorée) à son compteur. Icône Relique : clique « Prendre la relique » dans le panneau Donjon.",
    "Automatique au début de chaque tour : les salles vides reçoivent le monstre suivant (puis le boss quand la pioche est vide) ; en fin de manche, les monstres en jeu depuis une manche entière se retournent sur leur face évoluée.",
    "Compteur = Trésors. Jetons Dégât et Baril à poser sur les cartes.",
    "Réserve (8 cartes) : clique sur la pile pour piocher 1 carte ; clic droit pour la mélanger. Ivrognes : tire une pinte (1 PV du baril) pour piocher, 1 fois par tour ; un alcool s'attache à ton unité près du baril, même en Duel. Druides : Cueillette au Repos, 1 recette à l'Assaut.",
    "Jetons Pousse et Loup, baril et Livre : clic droit sur la carte qui les crée (ou sur le Gardien).",
])
json.dump(g, open(P, 'w'), ensure_ascii=False, indent=2)

# --- decks préconstruits : Réserve de 8, plus de reliques ---
dk = json.load(open('decks.json'))
RES = {'precon-ivrognes': ('Alcool', [('biere', 2), ('cidre', 1), ('hydromel', 1), ('rhum', 1), ('whisky', 1),
                                     ('vin-chaud', 1), ('absinthe', 1)]),
       'precon-druides': ('Ingredient', [('champignon', 2), ('baies', 2), ('miel', 2), ('racine', 1), ('herbes', 1)])}
for d in dk:
    L = d['deckList']
    L.pop('Relique', None)
    L['categoriesOrder'] = [c for c in L['categoriesOrder'] if c != 'Relique']
    cat, lst = RES[d['id']]
    L[cat] = [{'id': i, 'count': n} for i, n in lst]
    assert sum(e['count'] for e in L[cat]) == 8
    assert sum(e['count'] for k in ('Unite', 'Sort') for e in L[k]) == 30
json.dump(dk, open('decks.json', 'w'), ensure_ascii=False, indent=2)
print('format v2 ok')

# --- branche des fichiers (GR_REF=nom-de-branche pour tester sans toucher main) ---
REF = os.environ.get('GR_REF', 'main')
g = json.load(open(P))
base = 'https://raw.githubusercontent.com/BlueZero1203/Guild-Rush/' + REF
g['cards']['dataUrl'] = base + '/cards.json'
g['cards']['cardBack'] = base + '/img/back.png'
g['defaultRessources']['decksUrl'] = base + '/decks.json'
json.dump(g, open(P, 'w'), ensure_ascii=False, indent=2)
