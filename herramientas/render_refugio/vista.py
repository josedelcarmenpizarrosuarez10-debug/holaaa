import sys, os, time
sys.path.insert(0,'/home/user/holaaa/herramientas/varones/senalizacion')
import ezdxf, vistas_se as VS
from ezdxf import bbox
f, png = sys.argv[1], sys.argv[2]
t=time.time(); doc=ezdxf.readfile(f); msp=doc.modelspace(); print('leido',round(time.time()-t))
if len(sys.argv)>3: caja=tuple(float(v) for v in sys.argv[3:7])
else:
    xs=[];ys=[]
    for e in msp.query('LINE LWPOLYLINE'):
        try:
            if e.dxftype()=='LINE': pts=[e.dxf.start,e.dxf.end]
            else: pts=list(e.get_points('xy'))
            for p in pts: xs.append(p[0]); ys.append(p[1])
        except Exception: pass
    xs.sort(); ys.sort(); n=len(xs)
    caja=(xs[int(n*0.01)],ys[int(n*0.01)],xs[int(n*0.99)],ys[int(n*0.99)])
print('caja',[round(v,1) for v in caja])
L=VS.Lienzo(caja)
for e in msp: L.entidad(e)
L.guardar(png, ancho_pulg=float(os.environ.get("ANCHO",24)), dpi=int(os.environ.get("DPI",90)))
print('ok', round(time.time()-t))
