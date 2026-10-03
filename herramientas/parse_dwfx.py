import re, pickle, glob, html
D=glob.glob('x/dwf/documents/*/sections/com.autodesk.dwf.ePlot_*/')[0]
w2x=open(D+'A93D1DDD-BDEE-40FF-A9E2-3A2093F92239.xml',encoding='utf8').read()
PFX='N83AF80A6B7714E18853674EF1594FA5B_'
layers={int(m.group(2)):html.unescape(m.group(1)) for m in re.finditer(r'<Layer Name="([^"]*)" Number="(\d+)"',w2x)}
# estado capa por refName
states=[]
for m in re.finditer(r'<RenditionSync refName="'+PFX+r'(\d+)">(.*?)</RenditionSync>',w2x,re.S):
    lm=re.search(r'<Layer (?:Name="[^"]*" )?Number="(\d+)"',m.group(2))
    if lm: states.append((int(m.group(1)),int(lm.group(1))))
states.sort()
import bisect
keys=[s[0] for s in states]
def layer_of(n):
    i=bisect.bisect_right(keys,n)-1
    return layers.get(states[i][1],'?') if i>=0 else '?'
fp=open(D+'FixedPage.fpage',encoding='utf8').read()
X0=2147470577-158.3464568; Y0=546+9139.03937
def tomodel(fx,fy):
    wx=fx+X0; wy=Y0-fy
    return (wx-2144864562)/7.477337232,(wy+69400838.82)/7.477361723
tok=re.compile(r'([MmLlHhVvZzCcQqAa])|(-?\d*\.?\d+(?:[eE][-+]?\d+)?)')
def parse(data):
    polys=[];cur=[];x=y=0;sx=sy=0;cmd=None;nums=[]
    toks=tok.findall(data)
    i=0
    def flush():
        nonlocal cur
        if len(cur)>1: polys.append(cur)
        cur=[]
    while i<len(toks):
        c,n=toks[i]
        if c:
            cmd=c;i+=1
            if cmd in 'Zz':
                if cur: cur.append(cur[0]); flush()
                x,y=sx,sy
            continue
        # read numbers for cmd
        def num(k):
            return float(toks[i+k][1])
        if cmd in 'Mm':
            nx,ny=num(0),num(1); i+=2
            if cmd=='m': nx+=x;ny+=y
            flush(); x,y=nx,ny; sx,sy=x,y; cur=[(x,y)]; cmd='L' if cmd=='M' else 'l'
        elif cmd in 'Ll':
            nx,ny=num(0),num(1); i+=2
            if cmd=='l': nx+=x;ny+=y
            x,y=nx,ny; cur.append((x,y))
        elif cmd in 'Hh':
            nx=num(0); i+=1
            if cmd=='h': nx+=x
            x=nx; cur.append((x,y))
        elif cmd in 'Vv':
            ny=num(0); i+=1
            if cmd=='v': ny+=y
            y=ny; cur.append((x,y))
        elif cmd in 'Cc':
            pts=[num(k) for k in range(6)]; i+=6
            if cmd=='c': pts=[pts[k]+(x if k%2==0 else y) for k in range(6)]
            x,y=pts[4],pts[5]; cur.append((x,y))
        elif cmd in 'Qq':
            pts=[num(k) for k in range(4)]; i+=4
            if cmd=='q': pts=[pts[k]+(x if k%2==0 else y) for k in range(4)]
            x,y=pts[2],pts[3]; cur.append((x,y))
        elif cmd in 'Aa':
            pts=[num(k) for k in range(7)]; i+=7
            nx,ny=pts[5],pts[6]
            if cmd=='a': nx+=x;ny+=y
            x,y=nx,ny; cur.append((x,y))
        else: i+=1
    flush(); return polys
ents=[]
for m in re.finditer(r'<Path Name="'+PFX+r'(\d+)"([^>]*)Data="([^"]*)"',fp):
    n=int(m.group(1)); attrs=m.group(2)
    fill='Fill=' in attrs; stroke=re.search(r'Stroke="(#[0-9A-Fa-f]+)"',attrs)
    for poly in parse(m.group(3)):
        ents.append((n,layer_of(n),fill,stroke.group(1) if stroke else None,[tomodel(*p) for p in poly]))
pickle.dump((layers,ents),open('dwfx.pkl','wb'))
import collections
cnt=collections.Counter(e[1] for e in ents); print(len(ents),'polilineas')
xs=[p[0] for e in ents for p in e[4]]; ys=[p[1] for e in ents for p in e[4]]
print('extension modelo E',min(xs),max(xs),'N',min(ys),max(ys))
for l,c in cnt.most_common(): 
    E=[p for e in ents if e[1]==l for p in e[4]]
    print(f'{c:6d} {l:35s} E {min(p[0] for p in E):.1f}-{max(p[0] for p in E):.1f} N {min(p[1] for p in E):.1f}-{max(p[1] for p in E):.1f}')
