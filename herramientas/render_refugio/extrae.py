import ezdxf, json, sys, collections
from shapely.geometry import Polygon
doc=ezdxf.readfile("dxf/PG 01-PG 02 PLANTA GENERAL.dxf"); msp=doc.modelspace()
out=[]
def poly(e, M=None):
    pts=[(p[0],p[1]) for p in e.get_points('xy')]
    if M is not None: pts=[tuple(M.transform((x,y,0)))[:2] for x,y in pts]
    return pts
def recorre(ents, M=None, capa_padre=None, blk=None, prof=0):
    for e in ents:
        t=e.dxftype()
        if t=='INSERT' and prof<4:
            try:
                for v in e.virtual_entities():
                    recorre([v], None, e.dxf.layer, e.dxf.name if blk is None else blk, prof+1)
            except Exception: pass
        elif t=='LWPOLYLINE':
            pts=poly(e)
            if len(pts)>=3 and (e.closed or (abs(pts[0][0]-pts[-1][0])<0.01 and abs(pts[0][1]-pts[-1][1])<0.01)):
                try: P=Polygon(pts)
                except Exception: continue
                if P.is_valid and P.area>8:
                    b=P.bounds
                    out.append(dict(capa=e.dxf.layer, padre=capa_padre, blk=blk, area=round(P.area,2), bbox=[round(v,2) for v in b], pts=[[round(x,3),round(y,3)] for x,y in pts]))
recorre(msp)
json.dump(out, open('poligonos_pg.json','w'))
c=collections.Counter((o['capa'],o['blk']) for o in out)
for k,v in c.most_common(60): print(v,k)
ys=sorted(o['bbox'][1] for o in out); print(ys[0], ys[-1])
