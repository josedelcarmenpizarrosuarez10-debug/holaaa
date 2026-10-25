"""Terreno de prueba con plataformas (PL1): plataforma alta (NPT +101.30) y plataforma baja (+100.00) separadas por un muro de
contención de 1.30 m; dentro de la baja, un patio a +99.60 (0.40 m más abajo: caída corta); una rampa entre la alta y la baja,
y una escalera por la que no puede pasar ninguna cuneta. El terreno baja hacia el sur, donde sale el agua.

Uso: python3 pruebas/plataformas.py  -> pruebas/sitios/PL1/ (PLANO.dxf y proyecto.json; no se versiona)
"""
import json
import os

import ezdxf
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))


def generar():
    d = os.path.join(AQUI, "sitios", "PL1"); os.makedirs(d, exist_ok=True)
    E0, N0 = 360000.0, 9281000.0
    P = lambda pts: [(E0 + x, N0 + y) for x, y in pts]
    cerco = P([(0, 0), (70, 0), (70, 50), (0, 50)])
    techos = [P([(8, 33), (30, 33), (30, 43), (8, 43)]), P([(40, 32), (60, 32), (60, 42), (40, 42)]),
              P([(8, 6), (26, 6), (26, 15), (8, 15)])]
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for capa in ("CERCO", "TECHOS", "CURVAS"): doc.layers.add(capa)
    msp.add_lwpolyline(cerco, close=True, dxfattribs={"layer": "CERCO"})
    for t in techos: msp.add_lwpolyline(t, close=True, dxfattribs={"layer": "TECHOS"})
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    xs = np.arange(-30, 101, 1.0); ys = np.arange(-30, 81, 1.0); X, Y = np.meshgrid(xs, ys)
    Z = 98.6 + 0.05 * Y
    cs = plt.contour(X + E0, Y + N0, Z, levels=np.arange(97.0, 103.0, 0.5)); plt.close("all")
    for z, segs in zip(cs.levels, cs.allsegs):
        for sg in segs:
            if len(sg) >= 2: msp.add_lwpolyline([(float(a), float(b)) for a, b in sg], dxfattribs={"layer": "CURVAS", "elevation": float(z)})
    doc.saveas(os.path.join(d, "PLANO.dxf"))
    niveles = {"modo": "nivelado", "npt": 100.00, "borde_cuneta": 100.00, "area_verde": 99.95,
               "plataformas": [{"nombre": "Plataforma alta", "poligono": P([(0, 25), (70, 25), (70, 50), (0, 50)]), "npt": 101.30},
                               {"nombre": "Plataforma baja", "poligono": P([(0, 0), (45, 0), (45, 25), (0, 25)]), "npt": 100.00},
                               {"nombre": "Patio bajo", "poligono": P([(45, 0), (70, 0), (70, 25), (45, 25)]), "npt": 99.60}],
               "rampas": [{"nombre": "Rampa", "poligono": P([(31, 21), (37, 21), (37, 29), (31, 29)]), "inicio": P([(34, 29)])[0],
                           "fin": P([(34, 21)])[0], "npt_inicio": 101.30, "npt_fin": 100.00}],
               "escaleras": [{"nombre": "Escalera", "poligono": P([(10, 23), (14, 23), (14, 27), (10, 27)])}]}
    cfg = {"proyecto": {"nombre": "SITIO DE PRUEBA CON PLATAFORMAS PL1", "nombre_corto": "Sitio de prueba PL1", "codigo": "PRUEBA PL1"},
           "dxf": "PLANO.dxf", "salida": "salida",
           "capas": {"curvas": {"capa": "CURVAS"}, "equidistancia": 0.5, "cerco": {"capa": "CERCO"}, "techos": "TECHOS"},
           "niveles": niveles, "lluvia": {"I_mmh": 180.0}, "superficies_cfg": {"por_defecto": "verde"}, "planteamiento": "automatico"}
    json.dump(cfg, open(os.path.join(d, "proyecto.json"), "w"), indent=1, ensure_ascii=False)
    return d


def generar2():
    """PL2: tres plataformas escalonadas hacia el sur (+101.00, +100.70 y +100.00: caída corta de 0.30 m y caja de caída de
    0.70 m) y un estacionamiento en la plataforma baja (cuneta siempre tapada, tapa vehicular)."""
    d = os.path.join(AQUI, "sitios", "PL2"); os.makedirs(d, exist_ok=True)
    E0, N0 = 362000.0, 9282000.0
    P = lambda pts: [(E0 + x, N0 + y) for x, y in pts]
    cerco = P([(0, 0), (60, 0), (60, 75), (0, 75)])
    techos = [P([(10, 58), (40, 58), (40, 68), (10, 68)]), P([(10, 33), (40, 33), (40, 43), (10, 43)])]
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for capa in ("CERCO", "TECHOS", "CURVAS"): doc.layers.add(capa)
    msp.add_lwpolyline(cerco, close=True, dxfattribs={"layer": "CERCO"})
    for t in techos: msp.add_lwpolyline(t, close=True, dxfattribs={"layer": "TECHOS"})
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    xs = np.arange(-30, 91, 1.0); ys = np.arange(-30, 106, 1.0); X, Y = np.meshgrid(xs, ys)
    Z = 98.8 + 0.03 * Y
    cs = plt.contour(X + E0, Y + N0, Z, levels=np.arange(97.0, 103.0, 0.5)); plt.close("all")
    for z, segs in zip(cs.levels, cs.allsegs):
        for sg in segs:
            if len(sg) >= 2: msp.add_lwpolyline([(float(a), float(b)) for a, b in sg], dxfattribs={"layer": "CURVAS", "elevation": float(z)})
    doc.saveas(os.path.join(d, "PLANO.dxf"))
    niveles = {"modo": "nivelado", "npt": 100.00, "borde_cuneta": 100.00, "area_verde": 99.95,
               "plataformas": [{"nombre": "Plataforma 1", "poligono": P([(0, 50), (60, 50), (60, 75), (0, 75)]), "npt": 101.00},
                               {"nombre": "Plataforma 2", "poligono": P([(0, 25), (60, 25), (60, 50), (0, 50)]), "npt": 100.70},
                               {"nombre": "Plataforma 3", "poligono": P([(0, 0), (60, 0), (60, 25), (0, 25)]), "npt": 100.00}]}
    cfg = {"proyecto": {"nombre": "SITIO DE PRUEBA CON PLATAFORMAS PL2", "nombre_corto": "Sitio de prueba PL2", "codigo": "PRUEBA PL2"},
           "dxf": "PLANO.dxf", "salida": "salida",
           "capas": {"curvas": {"capa": "CURVAS"}, "equidistancia": 0.5, "cerco": {"capa": "CERCO"}, "techos": "TECHOS"},
           "superficies": [{"nombre": "Estacionamiento", "tipo": "estacionamiento", "poligono": P([(2, 2), (58, 2), (58, 16), (2, 16)])}],
           "niveles": niveles, "lluvia": {"I_mmh": 180.0}, "superficies_cfg": {"por_defecto": "verde"}, "planteamiento": "automatico"}
    json.dump(cfg, open(os.path.join(d, "proyecto.json"), "w"), indent=1, ensure_ascii=False)
    return d


if __name__ == "__main__":
    print(generar()); print(generar2())
