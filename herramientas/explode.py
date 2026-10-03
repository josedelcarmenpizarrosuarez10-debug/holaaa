import ezdxf, pickle, collections
from ezdxf.math import Matrix44
import sys; doc=ezdxf.readfile(sys.argv[1]); msp=doc.modelspace()
out=[]
def pts_of(e):
    t=e.dxftype()
    if t=='LWPOLYLINE': return [(p[0],p[1]) for p in e.get_points()]
    if t=='POLYLINE': return [(v.dxf.location.x,v.dxf.location.y) for v in e.vertices]
    if t=='LINE': return [(e.dxf.start.x,e.dxf.start.y),(e.dxf.end.x,e.dxf.end.y)]
    if t in('TEXT','MTEXT','INSERT','CIRCLE','ARC','POINT'):
        p=e.dxf.insert if t in('TEXT','MTEXT','INSERT') else e.dxf.center if t in('CIRCLE','ARC') else e.dxf.location
        return [(p.x,p.y)]
    return None
def walk(ents,depth,blk):
    for e in ents:
        t=e.dxftype()
        if t=='INSERT':
            if depth<6:
                try: walk(list(e.virtual_entities()),depth+1,e.dxf.name)
                except Exception as ex: pass
            p=pts_of(e); out.append((e.dxf.layer,'INSERT:'+e.dxf.name,p,' | '.join(f'{a.dxf.tag}={a.dxf.text}' for a in e.attribs) if e.attribs else '',blk))
            continue
        p=pts_of(e)
        if p is None: continue
        txt=e.dxf.text if t=='TEXT' else e.text if t=='MTEXT' else ''
        out.append((e.dxf.layer,t,p,txt,blk))
walk(list(msp),0,'')
pickle.dump(out,open(sys.argv[2],'wb'))
print(len(out),'entidades planas'); print(collections.Counter(o[1].split(':')[0] for o in out))
