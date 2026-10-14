"""Plateau 'papillon' : rangée de monstres au centre, une colonne par salle (BF n du joueur sous/sur Monstre n).
Construit sections.layout, sharedZone et les sections de gamefile.json. Idempotent.
Usage: python3 tools/board_layout.py
Largeurs en % de la largeur du plateau (s'adapte à tout écran) ; hauteurs des cartes en vh."""
import json, urllib.parse
P='gamefile.json'
g=json.load(open(P))
G=g['gameplay']['Standard']
S=G['sections']
D=S['sectionsDict']

COLW,GAP,RW,LM=15,1.2,7,9
TOTAL=LM+4*COLW+3*GAP+GAP+RW+2*(GAP+RW)

C={ 'bf':(240,200,60),'camp':(255,205,160),'ener':(175,85,205),'pile':(245,150,30),
    'exp':(70,170,100),'gard':(245,170,60),'monstre':(225,70,50),'boss':(225,70,50),'neutre':(150,150,150)}

def label(txt,bottom=False):
    svg=("<svg xmlns='http://www.w3.org/2000/svg' width='400' height='22'><text x='0' y='15' "
         "font-family='Arial,sans-serif' font-size='12' font-weight='700' letter-spacing='1' "
         "fill='rgba(255,255,255,0.40)'>%s</text></svg>")%txt
    return 'url("data:image/svg+xml,%s")'%urllib.parse.quote(svg,safe="'/:=, ")

def node(sec,w,col,lab=None,ml=0,pile=False):
    r,gg,b=C[col]
    st={'width':'%s%%'%w,'flex':'0 0 auto','borderRadius':'6px',
        'backgroundColor':'rgba(%d,%d,%d,0.20)'%(r,gg,b),'border':'1px solid rgba(%d,%d,%d,0.55)'%(r,gg,b)}
    if ml: st['marginLeft']='%s%%'%ml
    if lab:
        st['backgroundImage']=label(lab); st['backgroundRepeat']='no-repeat'
        st['backgroundPosition']='left 4px bottom 1px' if pile else 'left 22px top 3px'
    return {'section':sec,'style':st}

def row(content,left=LM,right=0,sym=True):
    first=content[0]['style']; first['marginLeft']='%s%%'%round(left+float(first.get('marginLeft','0%').rstrip('%')),2)
    r={'direction':'row','content':content,'style':{'justifyContent':'center','marginRight':'%s%%'%right} if right else {'justifyContent':'center'}}
    # marge de droite portée par le dernier élément pour égaliser les largeurs
    if right: content[-1]['style']['marginRight']='%s%%'%round(right,2); r['style'].pop('marginRight')
    if sym: r['isSymmetricalForOpponents']=True
    return r

# Colonnes : [Donjon][S1][S2][S3][S4][Boss][Pioche][Défausse] ; chaque rangée remplit toute la largeur.
R=lambda x: round(x,2)
# --- rangée A : salles BF1..4 | Gardien (sous Boss + pioche) | Réserve (sous la défausse) ---
A=[node('BF%d'%i,COLW,'bf','EXPÉDITION %d'%i,ml=(GAP if i>1 else 0)) for i in range(1,5)]
A.append(node('Gardien',R(2*RW+GAP),'gard','GARDIEN · BARIL / LIVRE',ml=GAP))
A.append(node('Reserve',RW,'pile','RÉSERVE',pile=True,ml=GAP))
# --- rangée B : pioche énergie + énergie (sous S1-S2) | pioche reliques + Camp jusqu'au bout ---
H2=2*COLW+GAP
B=[node('PiocheEnergie',RW,'ener','PIOCHE',pile=True),
   node('Energie',R(H2-RW-GAP),'ener','ÉNERGIE',ml=GAP),
   node('Relique',RW,'camp','RELIQUES',pile=True,ml=GAP)]
B.append(node('Camp',R(TOTAL-LM-RW-GAP-(H2-RW-GAP)-GAP-RW-GAP),'camp','CAMP · RENFORTS, BLESSÉES, RELIQUES',ml=GAP))
S['layout']={'direction':'column','content':[row(A), row(B)]}
S['layout']['content'][1]['style']['marginBottom']='12vh'

# --- zone partagée : monstres 1..4, boss, pile de monstres, cimetière ---
M=[{'section':'Donjon','style':{'width':'%s%%'%LM,'overflow':'visible'}}]
for i in range(1,5):
    M.append(node('Salle%d'%i,COLW,'monstre','MONSTRE %d'%i,ml=(LM if i==1 else GAP)))
M.append(node('Boss',RW,'boss','BOSS',ml=GAP))
M.append(node('Monstres',RW,'neutre','PIOCHE',pile=True,ml=GAP))
M.append(node('CimetiereMonstres',RW,'neutre','DÉFAUSSE',pile=True,ml=GAP))
S['sharedZone']={'height':14,'layout':{'direction':'column','content':[{'direction':'row','content':M,'style':{'justifyContent':'center'}}]}}

# --- sections ---
for k in list(D):
    if k in ('Reliques',) or (k.startswith('Salle') and k[-1] in 'HI'):
        D.pop(k)
for i in range(1,5):
    D['BF%d'%i]={'isHidden':'no','height':14,'alignment':'CENTER','displayedTitle':'Expédition %d'%i,'logWhenPlayed':True}
    D['Salle%d'%i].update({'height':13,'displayedTitle':'Monstre salle %d'%i})
for k,h in (('Gardien',14),('Camp',14),('Energie',14),('PiocheEnergie',14),('Relique',14),('Reserve',14),            ('Boss',13),('Monstres',13),('CimetiereMonstres',13)):
    D[k]['height']=h
D.pop('Expedition',None)
D['Camp']['displayedTitle']='Camp (blessées, reliques)'
D['Camp']['alignment']='START'; D['Energie']['alignment']='START'
bp=D['Donjon']; bp['height']=13
st=bp['blueprint']['props']['style']
st.update({'left':'0','width':'100%','top':'8%','height':'200%','backgroundColor':'rgba(255,255,255,0.05)','border':'1px solid rgba(255,255,255,0.18)'})

# les reliques et trésors se jouent au Camp
for m in ('autoPlayFromHand','autoPlayFromStack'):
    for k in ('Relique','Tresor'):
        if k in S[m]: S[m][k]='Camp'
    S[m]['Unite']='Camp'   # une unité invoquée arrive au Camp, épuisée

g['customHelp']=g['customHelp'].replace(
 "Ta zone : Expédition, Camp (blessées) et Gardien en haut ; Énergie et sa pioche, Reliques et sa pioche, Réserve en bas.\nAu centre : Salles 1 à 4 (1 monstre par salle, 3 unités max par joueur et par salle, jetons compris), Boss, deck et cimetière des monstres, panneau Donjon.",
 "Plateau en papillon : les monstres sont au centre (Monstre 1 à 4, Boss, pioche et défausse des monstres, panneau Donjon à gauche). Chaque joueur a une Salle sous (ou au-dessus de) chaque monstre : 3 unités max par salle, jetons compris. Ta zone : Salles 1-4 et Gardien ; Énergie (avec sa pioche), Camp (blessées et reliques, avec la pioche de reliques) et Réserve ; les Salles sont l'Expédition.")
json.dump(g,open(P,'w'),ensure_ascii=False,indent=2)
print('ok total',TOTAL)

# panneau Donjon : on ne garde que « Étage suivant » (plus de boutons Réserve)
def strip(n):
    if isinstance(n,dict):
        for k,v in n.items():
            if isinstance(v,list): n[k]=[x for x in v if not (isinstance(x,dict) and (x.get('props',{}) or {}).get('data-gr')=='res')]
            for v in n.values(): strip(v)
    elif isinstance(n,list):
        for x in n: strip(x)
g=json.load(open(P)); strip(g['gameplay']['Standard']['sections']['sectionsDict']['Donjon'])
g['customHelp']=g['customHelp'].replace(", ou utilise les boutons « Ta Réserve » du panneau Donjon (piocher 1, piocher 3, mélanger).",". Pour piocher 3 (Cueillette), clique la pile trois fois, puis clic droit sur la pile > Mélanger.").replace(" et Réserve ; Expédition en bas."," et Réserve.").replace(" et Réserve ; les Salles sont l'Expédition."," et Réserve ; les Salles sont l'Expédition.")
json.dump(g,open(P,'w'),ensure_ascii=False,indent=2)

# règle : unités invoquées au Camp (épuisées), puis envoyées dans une Expédition 1-4 face au monstre
g=json.load(open(P))
h=g['customHelp']
h=h.replace("Chaque joueur a une Salle sous (ou au-dessus de) chaque monstre : 3 unités max par salle, jetons compris. Ta zone : Salles 1-4 et Gardien ; Énergie (avec sa pioche), Camp (blessées et reliques, avec la pioche de reliques) et Réserve.",
 "Chaque joueur a une Expédition sous (ou au-dessus de) chaque monstre : 3 unités max par Expédition, jetons compris. Ta zone : Expéditions 1-4, Gardien et Réserve ; Énergie (avec sa pioche), pioche de reliques et Camp.\nUnités : une unité invoquée arrive au Camp, épuisée (incline-la). Redressée, tu l'envoies dans une Expédition 1-4 pour affronter le monstre de cette colonne. Blessée, elle revient au Camp. Les reliques se jouent aussi au Camp.")
h=h.replace("dans la salle du baril","dans l'Expédition du baril")
g['customHelp']=h
json.dump(g,open(P,'w'),ensure_ascii=False,indent=2)
