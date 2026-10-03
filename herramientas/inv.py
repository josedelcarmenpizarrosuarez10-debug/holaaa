import ezdxf, sys, collections
fn=sys.argv[1]; doc=ezdxf.readfile(fn); msp=doc.modelspace()
print('==',fn,doc.dxfversion,'unidades',doc.header.get('$INSUNITS'))
print('capas',len(doc.layers),':',', '.join(l.dxf.name for l in doc.layers)[:3000])
print('bloques:',', '.join(b.name for b in doc.blocks if not b.name.startswith('*'))[:2000])
c=collections.Counter(e.dxftype() for e in msp); print('entidades',dict(c))
print('layouts',[l.name for l in doc.layouts])
ext=ezdxf.bbox.extents(msp,fast=True) if hasattr(ezdxf,'bbox') else None
try:
    from ezdxf import bbox; b=bbox.extents(msp,fast=True); print('extension',b.extmin,b.extmax)
except Exception as e: print('bbox err',e)
txt=[]
for e in msp:
    if e.dxftype() in('TEXT','MTEXT'):
        t=e.dxf.text if e.dxftype()=='TEXT' else e.text
        txt.append((e.dxf.layer,t.strip(),(round(e.dxf.insert.x,2),round(e.dxf.insert.y,2))))
print('textos',len(txt))
import pickle; pickle.dump(txt,open(fn+'.txt.pkl','wb'))
for l,t,p in txt[:int(sys.argv[2]) if len(sys.argv)>2 else 400]: print(' ',l,'|',t[:90],'|',p)
