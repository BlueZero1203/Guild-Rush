"""Design 'épuré' du plateau : zones à la taille des cartes (unités vh), centre réduit, couleurs sobres.
Usage: python3 tools/style_board.py  (modifie gamefile.json en place, idempotent)"""
import json, re
P='gamefile.json'
g=json.load(open(P))
S=g['gameplay']['Standard']
SEC=S['sections']

# couleur par fonction (r,g,b)
COL={'Expedition':(70,170,100),'Camp':(230,130,70),'Gardien':(235,195,80),'Energie':(60,190,210),
     'Reliques':(165,110,220),'Reserve':(90,130,235),'Boss':(225,70,50)}
HOST=(80,140,200); GUEST=(205,100,135); MID=(150,150,150)
for i in '1234':
    COL['Salle%sH'%i]=HOST; COL['Salle%sI'%i]=GUEST; COL['Salle%s'%i]=MID

# largeur : (vh, repli en %) ; None = flexible (prend la place restante)
W={'Expedition':None,'Camp':('30vh','24%'),'Gardien':('14vh','10%'),
   'Energie':None,'PiocheEnergie':('11vh','8%'),'Reliques':('22vh','18%'),'Relique':('11vh','8%'),'Reserve':('11vh','8%')}
for i in '1234':
    W['Salle%sH'%i]=('14vh','38%'); W['Salle%s'%i]=('9vh','24%'); W['Salle%sI'%i]=('14vh','38%')
PILES=('PiocheEnergie','Relique','Reserve','Monstres','CimetiereMonstres')

def mn(a,b): return 'min(%s, %s)'%(a,b)

def label_of(st):
    src=st.get('_label') or st.get('backgroundImage','')
    m=re.match(r'(url\("data:image/svg\+xml,.*?"\))',src)
    lab=m.group(1) if m else None
    if lab:
        lab=lab.replace('0.55','0.38')
    return lab

def style(sec,old):
    lab=label_of(old)
    st={'borderRadius':'6px'}
    if lab:
        st['backgroundImage']=lab; st['backgroundRepeat']='no-repeat'
        st['backgroundPosition']='left 22px top 3px' if sec not in PILES else old.get('backgroundPosition','left 4px bottom 1px')
        if sec in PILES: st['backgroundPosition']='left 4px bottom 1px'
    st['_label']=old.get('_label') or old.get('backgroundImage')
    if sec in COL:
        c=COL[sec]
        st['backgroundColor']='rgba(%d,%d,%d,0.10)'%c
        st['border']='1px solid rgba(%d,%d,%d,0.35)'%c
    w=W.get(sec,'keep')
    if w is None:
        st['flex']='1 1 0'; st['minWidth']='0'
    elif w!='keep':
        st['width']=mn(*w); st['flex']='0 0 auto'
    return st

def walk(node,keep_widths=False):
    if not isinstance(node,dict): return
    sec=node.get('section')
    if sec and isinstance(node.get('style'),dict) and (sec in COL or sec in W or sec in PILES):
        old=node['style']
        new=style(sec,old)
        for k in ('marginLeft','marginRight'):
            if k in old and sec in ('Salle1H',): pass
        node['style']=new
    for c in node.get('content',[]) if isinstance(node.get('content'),list) else []:
        walk(c)

walk(SEC['layout'])
# lignes joueur : tout à gauche, hauteur propre
SEC['layout']['content'][1]['content'][-1]['style'].pop('marginRight',None)

# ---- zone partagée ----
sz=SEC['sharedZone']
sz['height']=24
L=sz['layout']['content']
r1,r2=L[0]['content'],L[1]['content']
walk(sz['layout'])
def nm(r): return [(x.get('section') or 'grp') for x in r]
if 'Donjon' in nm(r1):
    donjon=r1.pop(nm(r1).index('Donjon'))
    donjon['style']={'width':'15vh','overflow':'visible'}
    g1,g2,boss,mon=r1
    for grp in (g1,g2):
        grp['style']={'flex':'0 0 auto','width':mn('37vh','33%')}
    g1['style']['marginLeft']=mn('15vh','13%')
    g2['style']['marginLeft']='2vh'
    for p in (boss,mon):
        p['style']['width']=mn('9vh','9%'); p['style']['flex']='0 0 auto'
    r1[:]=[donjon,g1,g2,boss,mon]
    g3,g4,cim=r2
    g3['style']={'flex':'0 0 auto','width':mn('37vh','33%'),'marginLeft':mn('15vh','13%')}
    g4['style']={'flex':'0 0 auto','width':mn('37vh','33%'),'marginLeft':'2vh'}
    cim['style']['width']=mn('9vh','9%'); cim['style']['flex']='0 0 auto'
    cim['style']['marginLeft']='2vh'; cim['style']['marginRight']='7vh'
# centrer le contenu des deux rangées
for r in L: r['style']={**r.get('style',{}),'justifyContent':'center'}

# hauteurs de carte (vh) : centre réduit
D=SEC['sectionsDict']
for k in ['Salle%d'%i for i in range(1,5)]+['Salle%dH'%i for i in range(1,5)]+['Salle%dI'%i for i in range(1,5)]+['Boss','Monstres','CimetiereMonstres']:
    D[k]['height']=11

# panneau Donjon sobre
bs=D['Donjon']['blueprint']['props']['style']
bs.update({'left':'0','width':'100%','height':'200%','backgroundColor':'rgba(255,255,255,0.05)','border':'1px solid rgba(255,255,255,0.18)'})

def clean(n):
    if isinstance(n,dict):
        if isinstance(n.get('style'),dict): n['style'].pop('_label',None)
        for c in (n.get('content') if isinstance(n.get('content'),list) else []): clean(c)
clean(SEC['layout']); clean(sz['layout'])
json.dump(g,open(P,'w'),ensure_ascii=False,indent=2)
print('ok')
