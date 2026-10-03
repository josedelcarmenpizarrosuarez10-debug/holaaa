"""Cotas del terreno existente (superficie TOPO FINAL, LandXML) a lo largo del eje."""
import os, sys, json, pickle, numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import diseno as dz
from scipy.interpolate import LinearNDInterpolator

def cargar_tin(pkl=os.path.join(RAIZ, 'entregables', '_calc', 'topo.pkl')):
    if not os.path.exists(pkl):
        import zipfile, xml.etree.ElementTree as ET
        z = zipfile.ZipFile(os.path.join(RAIZ, 'insumos', 'topografia', 'TOPO_FINAL_landxml.zip'))
        f = z.open(z.namelist()[0]); ns = '{http://www.landxml.org/schema/LandXML-1.2}'
        pts = []
        for ev, el in ET.iterparse(f, events=('end',)):
            if el.tag == ns + 'P' and el.get('id'):
                n, e, zz = map(float, el.text.split()); pts.append((e, n, zz)); el.clear()
            elif el.tag in (ns + 'F', ns + 'CgPoint'): el.clear()
        P = np.array(pts); os.makedirs(os.path.dirname(pkl), exist_ok=True); pickle.dump(P, open(pkl, 'wb'))
    return pickle.load(open(pkl, 'rb'))

def interpolador(P, E0, E1, N0, N1):
    m = (P[:, 0] > E0) & (P[:, 0] < E1) & (P[:, 1] > N0) & (P[:, 1] < N1)
    Q = P[m]; return LinearNDInterpolator(Q[:, :2], Q[:, 2])

def main():
    P = cargar_tin()
    pts = [dz.local_a_utm(*dz.eje_local(p)[:2]) for p in np.arange(0, dz.P_FIN + 0.01, 0.5)]
    E = [p[0] for p in pts]; N = [p[1] for p in pts]
    f = interpolador(P, min(E) - 60, max(E) + 60, min(N) - 60, max(N) + 60)
    out = []
    for p in np.arange(0, dz.P_FIN + 0.01, 0.5):
        x, y, az = dz.eje_local(p); e, n = dz.local_a_utm(x, y)
        out.append(dict(p=round(float(p), 2), E=round(e, 3), N=round(n, 3), z=round(float(f(e, n)), 3)))
    fn = os.path.join(RAIZ, 'entregables', '_calc', 'terreno.json')
    json.dump(out, open(fn, 'w'), indent=0)
    zs = [o['z'] for o in out]; print('terreno a lo largo del eje: min %.2f max %.2f (NPT %.2f)' % (min(zs), max(zs), dz.D['NPT']))
    for o in out[::20]: print('  0+%06.2f  E %.3f N %.3f  z %.3f' % (o['p'], o['E'], o['N'], o['z']))
    return out
if __name__ == '__main__': main()
