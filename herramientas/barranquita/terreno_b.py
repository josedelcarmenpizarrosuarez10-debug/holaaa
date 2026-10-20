"""Modelo de terreno (TIN lineal) a partir de las curvas de nivel C-TOPO del plano PLANTA_GENERAL_590_2 (I.E. 0590, Barranquita).
Base: insumos/barranquita/base_sitio.pkl = geometria de la copia real del sitio (coordenadas UTM), extraida del DXF del usuario
(332 MB, no se versiona) con los bloques explotados a coordenadas reales."""
import os, pickle, numpy as np
from scipy.interpolate import LinearNDInterpolator
AQUI = os.path.dirname(os.path.abspath(__file__))
GEO = os.environ.get("BQ_GEO", os.path.join(os.path.dirname(os.path.dirname(AQUI)), "insumos", "barranquita", "base_sitio.pkl"))
X0, X1, Y0, Y1 = 354700, 355000, 9249700, 9250140      # copia real del sitio (la que esta sobre la topografia)


def cargar():
    return pickle.load(open(GEO, "rb"))


def curvas(G=None):
    G = G or cargar()
    out = []
    for pts, cl, b in G["geo"]["C-TOPO"]:
        z = pts[0][2]
        if z > 100 and X0 < pts[0][0] < X1 and Y0 < pts[0][1] < Y1: out.append((z, [(p[0], p[1]) for p in pts]))
    return out


def modelo(G=None):
    P, Z = [], []
    for z, pts in curvas(G):
        for p in pts: P.append(p); Z.append(z)
    f = LinearNDInterpolator(np.array(P), np.array(Z))
    return lambda x, y: float(f(x, y))
