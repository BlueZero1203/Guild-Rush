"""Plateau 'papillon' : rangée de monstres au centre, une colonne par salle (BF n du joueur sous/sur Monstre n).
Construit sections.layout, sharedZone et les sections de gamefile.json. Idempotent.
Usage: python3 tools/board_layout.py
Unités : vh. Colonne de salle 12, écart 1, colonne de droite 9, marge gauche (panneau Donjon) 15."""
import json, urllib.parse
P='gamefile.json'
g=json.load(open(P))
G=g['gameplay']['Standard']
S=G['sections']
D=S['sectionsDict']

COLW,GAP,RW,LM=12,1,9,15
TOTAL=LM+4*COLW+3*GAP+GAP+RW+2*(GAP+RW)   # largeur de la rangée centrale = 96

C={ 'bf':(240,200,60),'camp':(255,205,160),'ener':(175,85,205),'pile':(245,150,30),
    'exp':(70,170,100),'gard':(245,170,60),'monstre':(225,70,50),'boss':(225,70,50),'neutre':(150,150,150)}

def label(txt,bottom=False):
    svg=("<svg xmlns='http://www.w3.org/2000/svg' width='400' height='22'><text x='0' y='15' "
         "font-family='Arial,sans-serif' font-size='12' font-weight='700' letter-spacing='1' "
         "fill='rgba(255,255,255,0.40)'>%s</text></svg>")%txt
    return 'url("data:image/svg+xml,%s")'%urllib.parse.quote(svg,safe="'/:=, ")

def node(sec,w,col,lab=None,ml=0,pile=False):
    r,gg,b=C[col]
    st={'width':'%svh'%w,'flex':'0 0 auto','borderRadius':'6px',
        'backgroundColor':'rgba(%d,%d,%d,0.20)'%(r,gg,b),'border':'1px solid rgba(%d,%d,%d,0.55)'%(r,gg,b)}
    if ml: st['marginLeft']='%svh'%ml
    if lab:
        st['backgroundImage']=label(lab); st['backgroundRepeat']='no-repeat'
        st['backgroundPosition']='left 4px bottom 1px' if pile else 'left 22px top 3px'
    return {'section':sec,'style':st}

def row(content,left=LM,right=0,sym=True):
    first=content[0]['style']; first['marginLeft']='%svh'%(left+float(first.get('marginLeft','0vh')[:-2]))
    r={'direction':'row','content':content,'style':{'justifyContent':'center','marginRight':'%svh'%right} if right else {'justifyContent':'center'}}
    # marge de droite portée par le dernier élément pour égaliser les largeurs
    if right: content[-1]['style']['marginRight']='%svh'%right; r['style'].pop('marginRight')
    if sym: r['isSymmetricalForOpponents']=True
    return r

# --- rangée A : salles BF1..4 + Gardien (largeur 76 -> marge droite 20) ---
A=[node('BF%d'%i,COLW,'bf','SALLE %d'%i,ml=(GAP if i>1 else 0)) for i in range(1,5)]
A.append(node('Gardien',RW,'gard','GARDIEN',ml=GAP))
# --- rangée B : pile énergie + énergie | camp + pile reliques | réserve ---
B=[node('PiocheEnergie',RW,'ener','PIOCHE',pile=True,ml=0),
   node('Energie',2*COLW+GAP-RW-GAP,'ener','ÉNERGIE',ml=GAP),
   node('Camp',2*COLW+GAP-RW-GAP,'camp','CAMP · RELIQUES',ml=GAP),
   node('Relique',RW,'camp','RELIQUES',pile=True,ml=GAP),
   node('Reserve',RW,'pile','RÉSERVE',pile=True,ml=GAP)]
# --- rangée C : expédition sur toute la largeur ---
Cn=[node('Expedition',2*(2*COLW+GAP)+GAP+RW+GAP,'exp','EXPÉDITION')]
wA=LM+4*COLW+3*GAP+GAP+RW
S['layout']={'direction':'column','content':[
    row(A,right=TOTAL-wA), row(B,right=TOTAL-wA), row(Cn,right=TOTAL-(LM+Cn[0]['style']['width'] and 0)-0 if False else TOTAL-wA)]}
# la rangée C n'est pas symétrique (une seule zone)
S['layout']['content'][2].pop('isSymmetricalForOpponents',None)

# --- zone partagée : monstres 1..4, boss, pile de monstres, cimetière ---
M=[{'section':'Donjon','style':{'width':'%svh'%(LM-1),'overflow':'visible'}}]
for i in range(1,5):
    M.append(node('Salle%d'%i,COLW,'monstre','MONSTRE %d'%i,ml=(LM if i==1 else GAP)))
M.append(node('Boss',RW,'boss','BOSS',ml=GAP))
M.append(node('Monstres',RW,'neutre','PIOCHE',pile=True,ml=GAP))
M.append(node('CimetiereMonstres',RW,'neutre','DÉFAUSSE',pile=True,ml=GAP))
S['sharedZone']={'height':12,'layout':{'direction':'column','content':[{'direction':'row','content':M,'style':{'justifyContent':'center'}}]}}

# --- sections ---
for k in list(D):
    if k in ('Reliques',) or (k.startswith('Salle') and k[-1] in 'HI'):
        D.pop(k)
for i in range(1,5):
    D['BF%d'%i]={'isHidden':'no','height':12,'alignment':'CENTER','displayedTitle':'Salle %d'%i,'logWhenPlayed':True}
    D['Salle%d'%i].update({'height':11,'displayedTitle':'Monstre salle %d'%i})
for k,h in (('Gardien',12),('Camp',12),('Energie',12),('PiocheEnergie',12),('Relique',12),('Reserve',12),('Expedition',13),
            ('Boss',11),('Monstres',11),('CimetiereMonstres',11)):
    D[k]['height']=h
D['Camp']['displayedTitle']='Camp (blessées, reliques)'
D['Camp']['alignment']='START'; D['Energie']['alignment']='START'
bp=D['Donjon']; bp['height']=11
st=bp['blueprint']['props']['style']
st.update({'left':'0','width':'100%','top':'8%','height':'300%','backgroundColor':'rgba(255,255,255,0.05)','border':'1px solid rgba(255,255,255,0.18)'})

# les reliques et trésors se jouent au Camp
for m in ('autoPlayFromHand','autoPlayFromStack'):
    for k in ('Relique','Tresor'):
        if k in S[m]: S[m][k]='Camp'

g['customHelp']=g['customHelp'].replace(
 "Ta zone : Expédition, Camp (blessées) et Gardien en haut ; Énergie et sa pioche, Reliques et sa pioche, Réserve en bas.\nAu centre : Salles 1 à 4 (1 monstre par salle, 3 unités max par joueur et par salle, jetons compris), Boss, deck et cimetière des monstres, panneau Donjon.",
 "Plateau en papillon : les monstres sont au centre (Monstre 1 à 4, Boss, pioche et défausse des monstres, panneau Donjon à gauche). Chaque joueur a une Salle sous (ou au-dessus de) chaque monstre : 3 unités max par salle, jetons compris. Ta zone : Salles 1-4 et Gardien ; Énergie (avec sa pioche), Camp (blessées et reliques, avec la pioche de reliques) et Réserve ; Expédition en bas.")
json.dump(g,open(P,'w'),ensure_ascii=False,indent=2)
print('ok total',TOTAL)
