"""Terrenos de prueba inventados para la bateria de DrenIE: cada uno es un plano DXF como el que entrega un cliente (cerco,
techos, curvas de nivel con su cota) y su proyecto.json en modo de planteamiento automatico, sin lineas ni descargas dadas.

Casos difíciles a proposito: edificios pegados entre si o al cerco, losa deportiva grande, techos en L, cercos con esquina
cortada o lado inclinado, sitio girado, terrenos casi planos o con mucha pendiente, lluvias fuertes.

Uso: python3 pruebas/sitios.py [n] [semilla_inicial]  -> pruebas/sitios/S01 ... (no se versionan)
"""
import json
import math
import os
import random
import sys

import ezdxf
import numpy as np
from shapely.affinity import rotate, translate
from shapely.geometry import Polygon, box

AQUI = os.path.dirname(os.path.abspath(__file__))


def _cerco(rnd, W, H):
    tipo = rnd.choice(["rect", "corte", "inclinado"])
    if tipo == "rect": return Polygon([(0, 0), (W, 0), (W, H), (0, H)]), tipo
    if tipo == "corte":
        c = rnd.uniform(8, 18); return Polygon([(0, 0), (W - c, 0), (W, c), (W, H), (0, H)]), tipo
    d = rnd.uniform(6, 20); return Polygon([(0, d), (W, 0), (W, H), (0, H)]), tipo


def _techos(rnd, cerco):
    """Edificios rectangulares y en L, una losa deportiva a veces; algunos pegados entre si o cerca del cerco."""
    minx, miny, maxx, maxy = cerco.bounds
    out = []
    pedidos = []
    if rnd.random() < 0.6: pedidos.append(("losa", rnd.uniform(26, 36), rnd.uniform(16, 24)))
    for _ in range(rnd.randint(3, 8)):
        k = rnd.random()
        if k < 0.55: pedidos.append(("modulo", rnd.uniform(18, 30), rnd.uniform(8, 14)))
        elif k < 0.8: pedidos.append(("chico", rnd.uniform(6, 12), rnd.uniform(5, 9)))
        else: pedidos.append(("L", rnd.uniform(16, 24), rnd.uniform(14, 20)))
    for tipo, a, b in pedidos:
        for _ in range(200):
            if rnd.random() < 0.5: a, b = b, a
            x = rnd.uniform(minx + 1.0, maxx - a - 1.0); y = rnd.uniform(miny + 1.0, maxy - b - 1.0)
            if tipo == "L":
                t = min(a, b) * 0.45
                p = Polygon([(x, y), (x + a, y), (x + a, y + t), (x + t, y + t), (x + t, y + b), (x, y + b)])
            else:
                p = box(x, y, x + a, y + b)
            # dentro del cerco con 1 a 6 m de margen (a veces muy cerca del cerco a proposito)
            marg = 0.8 if rnd.random() < 0.15 else rnd.uniform(2.5, 6.0)
            if not cerco.buffer(-marg).contains(p): continue
            # pegado al vecino (0 m) o con pasadizo de 3 m o mas
            if any(p.intersects(q.buffer(-0.01)) for q in out): continue
            if any(0.01 < p.distance(q) < 3.0 for q in out) and rnd.random() < 0.7: continue
            out.append(p); break
    return out


def _curvas(rnd, cerco, ang):
    minx, miny, maxx, maxy = cerco.buffer(35).bounds
    s = rnd.choice([0.005, 0.01, 0.02, 0.04, 0.07])               # pendiente del terreno natural
    th = rnd.uniform(0, 2 * math.pi); gx, gy = s * math.cos(th), s * math.sin(th)
    z0 = rnd.uniform(150, 400); amp = rnd.uniform(0.0, 0.4)
    xs = np.arange(minx, maxx, 1.0); ys = np.arange(miny, maxy, 1.0); X, Y = np.meshgrid(xs, ys)
    Z = z0 + gx * (X - minx) + gy * (Y - miny) + amp * np.sin(X / 17.0) * np.cos(Y / 13.0)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    niveles = np.arange(math.floor(Z.min() * 2) / 2, Z.max() + 0.5, 0.5)
    cs = plt.contour(X, Y, Z, levels=niveles); plt.close("all")
    lineas = []
    for z, segs in zip(cs.levels, cs.allsegs):
        for sg in segs:
            if len(sg) >= 2: lineas.append((float(z), [(float(a), float(b)) for a, b in sg]))
    c = cerco.centroid
    zc = float(z0 + gx * (c.x - minx) + gy * (c.y - miny))
    return lineas, zc, s


def generar(k, semilla):
    rnd = random.Random(semilla)
    W, H = rnd.uniform(55, 120), rnd.uniform(50, 110)
    cerco, tcerco = _cerco(rnd, W, H)
    techos = _techos(rnd, cerco)
    ang = rnd.choice([0, 0, 0, 15, 30, 40])
    E0, N0 = 350000.0 + 1000 * k, 9280000.0
    tr = lambda g: translate(rotate(g, ang, origin=(0, 0)), E0, N0)
    cerco_t = tr(cerco); techos_t = [tr(t) for t in techos]
    curvas, zc, pend = _curvas(rnd, cerco_t, ang)
    d = os.path.join(AQUI, "sitios", "S%02d" % k); os.makedirs(d, exist_ok=True)
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for capa in ("CERCO", "TECHOS", "CURVAS"): doc.layers.add(capa)
    msp.add_lwpolyline(list(cerco_t.exterior.coords)[:-1], close=True, dxfattribs={"layer": "CERCO"})
    for t in techos_t: msp.add_lwpolyline(list(t.exterior.coords)[:-1], close=True, dxfattribs={"layer": "TECHOS"})
    for z, pts in curvas: msp.add_lwpolyline(pts, dxfattribs={"layer": "CURVAS", "elevation": z})
    doc.saveas(os.path.join(d, "PLANO.dxf"))
    npt = round(zc + 0.10, 2)
    cfg = {"proyecto": {"nombre": "SITIO DE PRUEBA S%02d" % k, "nombre_corto": "Sitio de prueba S%02d" % k, "codigo": "PRUEBA %02d" % k},
           "dxf": "PLANO.dxf", "salida": "salida",
           "capas": {"curvas": {"capa": "CURVAS"}, "equidistancia": 0.5, "cerco": {"capa": "CERCO"}, "techos": "TECHOS"},
           "niveles": {"modo": "nivelado", "npt": npt, "borde_cuneta": npt, "area_verde": round(npt - 0.05, 2)},
           "lluvia": {"I_mmh": round(rnd.uniform(150, 300), 2)},
           "superficies_cfg": {"por_defecto": "verde"}, "planteamiento": "automatico",
           "_prueba": {"semilla": semilla, "cerco": tcerco, "giro": ang, "pendiente_terreno": pend, "techos": len(techos)}}
    json.dump(cfg, open(os.path.join(d, "proyecto.json"), "w"), indent=1, ensure_ascii=False)
    return d, cfg["_prueba"]


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    s0 = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    for k in range(1, n + 1):
        d, info = generar(k, s0 + k)
        print(d, info)
