"""Applique le design 'coupe de donjon' au plateau (couleurs par fonction, bordures, torches, panneau Donjon à gauche).
Usage: python3 tools/style_board.py  (modifie gamefile.json en place, idempotent)"""
import json, re, copy
P='gamefile.json'
g=json.load(open(P))
S=g['gameplay']['Standard']['sections']

COL={ # nom de section -> (r,g,b)
 'Expedition':(70,170,100),'Camp':(230,120,60),'Gardien':(235,195,80),
 'Energie':(60,190,210),'Reliques':(165,110,220),'Reserve':(80,120,230),
 'Boss':(225,60,40),
}
HOST=(70,130,190); GUEST=(210,90,130); MID=(150,140,130)
for i in '1234':
    COL['Salle%sH'%i]=HOST; COL['Salle%sI'%i]=GUEST; COL['Salle%s'%i]=MID

def rgba(c,a): return 'rgba(%d,%d,%d,%s)'%(c+(a,))

def restyle(node):
    sec=node.get('section')
    st=node.get('style')
    if sec and st is not None and sec in COL:
        c=COL[sec]
        label=st.get('_label') or st.get('backgroundImage','')
        m=re.match(r'(url\("data:image/svg\+xml,.*?"\))',label)
        lab=m.group(1) if m else None
        st['_label']=lab
        mid = sec.startswith('Salle') and not sec.endswith(('H','I'))
        layers=[]
        if lab: layers.append(lab)
        if mid: layers.append('radial-gradient(circle at 50% 28%, rgba(255,170,60,0.28), rgba(255,170,60,0) 65%)')
        layers.append('linear-gradient(180deg, %s, %s)'%(rgba(c,0.06),rgba(c,0.20)))
        st['backgroundImage']=', '.join(layers)
        st['backgroundRepeat']=', '.join(['no-repeat']*len(layers))
        pos=[]
        if lab: pos.append('left 22px top 3px')
        if mid: pos.append('center')
        pos.append('center')
        st['backgroundPosition']=', '.join(pos)
        st['backgroundColor']=rgba(c,0.22 if sec!='Gardien' else 0.30)
        st['border']='1px solid '+rgba(c,0.6 if sec=='Gardien' else 0.45)
        st['boxShadow']='inset 0 0 14px '+rgba(c,0.30)
        st['borderRadius']='8px'
    for ch in node.get('content',[]) if isinstance(node.get('content'),list) else []:
        restyle(ch)

restyle(S['layout'])
restyle(S['sharedZone']['layout'])
# nettoie la clé technique
def clean(n):
    if isinstance(n,dict):
        if isinstance(n.get('style'),dict): n['style'].pop('_label',None)
        for c in (n.get('content') if isinstance(n.get('content'),list) else []): clean(c)
clean(S['layout']); clean(S['sharedZone']['layout'])
# --- panneau Donjon à gauche des salles ---
L=S['sharedZone']['layout']['content']
r1,r2=L[0]['content'],L[1]['content']
names=lambda r:[ (x.get('section') or 'grp') for x in r]
if names(r1)[-1]=='Donjon':
    donjon=r1.pop()
    g1,g2,boss,mon=r1
    donjon['style']={'width':'14%','overflow':'visible'}
    g1['style']['width']='33%'; g2['style']['width']='33%'
    boss['style']['width']='10%'; mon['style']['width']='10%'
    r1[:]=[donjon,g1,g2,boss,mon]
    g3,g4,cim=r2
    g3['style']['width']='33%'; g3['style']['marginLeft']='14%'; g4['style']['width']='33%'
    cim['style']['width']='10%'; cim['style']['marginRight']='10%'
bp=S['sectionsDict']['Donjon']['blueprint']
bs=bp['props']['style']
bs['left']='0'; bs['width']='100%'; bs['height']='200%'
json.dump(g,open(P,'w'),ensure_ascii=False,indent=2)
print('ok')
