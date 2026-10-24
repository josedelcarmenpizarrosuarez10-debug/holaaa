"""Modelo de terreno (TIN lineal) con las curvas de nivel del plano.

La cota de cada curva se toma de su elevacion en el DXF. Si las curvas vienen a cota 0 (dibujo plano), se toma del rotulo de
texto que esta sobre la curva y las curvas sin rotulo (intermedias) se deducen entre las dos rotuladas vecinas con la
equidistancia. Las curvas sin cota posible se descartan y se reportan: nunca se inventa una cota.
"""
import math
import re

import numpy as np
from scipy.interpolate import LinearNDInterpolator
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

from . import geom

NUM = re.compile(r"^\s*[+]?(\d{1,5}(?:[.,]\d+)?)\s*$")


def _equidistancia(zs):
    d = sorted({round(abs(a - b), 3) for a in zs for b in zs if abs(a - b) > 1e-6})
    return d[0] if d else None


def curvas(B, cfg):
    """Lista de (z, LineString) y un reporte de lo leido."""
    sel = cfg["curvas"]
    zmin, zmax = cfg.get("z_min", -500.0), cfg.get("z_max", 9000.0)
    ents = geom.seleccionar(B, sel)
    lineas = [LineString(e[0]) for e in ents if len(e[0]) >= 2]
    elev = [e[3] for e in ents if len(e[0]) >= 2]
    rep = {"curvas_leidas": len(lineas)}
    z = [v if (v is not None and abs(v) > 1e-9 and zmin <= v <= zmax) else None for v in elev]
    rep["con_elevacion"] = sum(1 for v in z if v is not None)
    if rep["con_elevacion"] < 0.5 * len(lineas):
        # cotas por rotulos de texto
        tsel = cfg.get("curvas_texto", sel)
        tx = []
        for capa, s, x, y, h, col in geom.textos(B, tsel):
            m = NUM.match(s.replace(" ", ""))
            if m:
                v = float(m.group(1).replace(",", "."))
                if zmin <= v <= zmax: tx.append((v, Point(x, y), h))
        arbol = STRtree(lineas)
        z = [None] * len(lineas)
        for v, p, h in tx:
            i = int(arbol.nearest(p))
            if lineas[i].distance(p) <= max(1.0, 2.5 * (h or 0.3)): z[i] = v
        rep["rotulos"] = len(tx)
        rep["con_rotulo"] = sum(1 for v in z if v is not None)
        eq = cfg.get("equidistancia") or _equidistancia([v for v in z if v is not None])
        rep["equidistancia"] = eq
        # curvas intermedias: entre dos rotuladas vecinas que difieren en 2 x equidistancia
        for vuelta in range(6):
            nuevo = 0
            con = [(i, v) for i, v in enumerate(z) if v is not None]
            if not con or not eq: break
            for i, v in enumerate(z):
                if v is not None: continue
                p = lineas[i].interpolate(0.5, normalized=True)
                cerca = sorted(((lineas[j].distance(p), zz) for j, zz in con), key=lambda e: e[0])
                if len(cerca) < 2: continue
                d1, z1 = cerca[0]
                z2 = next((zz for d, zz in cerca[1:] if abs(zz - z1) > 1e-6), None)
                if z2 is None: continue
                if abs(abs(z2 - z1) - 2 * eq) < 1e-6: z[i] = (z1 + z2) / 2.0; nuevo += 1
                elif abs(abs(z2 - z1) - eq) < 1e-6 and d1 > 0:
                    # entre una curva de z1 y otra de z2 a una equidistancia: la intermedia sigue la tendencia (z1 - (z2 - z1))
                    pass
            if not nuevo: break
        rep["deducidas"] = sum(1 for v in z if v is not None) - rep["con_rotulo"]
    out = [(v, L) for v, L in zip(z, lineas) if v is not None]
    rep["usadas"] = len(out)
    rep["descartadas"] = len(lineas) - len(out)
    if out:
        rep["z_min"] = round(min(v for v, L in out), 2); rep["z_max"] = round(max(v for v, L in out), 2)
    return out, rep


class Terreno:
    """z(x, y) por triangulacion lineal de los vertices de las curvas (NaN fuera del area con curvas)."""

    def __init__(self, cur):
        P, Z = [], []
        for v, L in cur:
            for x, y in L.coords: P.append((x, y)); Z.append(v)
        if len(P) < 3: raise ValueError("No hay curvas de nivel con cota para armar el terreno")
        self.f = LinearNDInterpolator(np.array(P), np.array(Z))

    def z(self, x, y):
        return float(self.f(x, y))

    def zv(self, P):
        P = np.asarray(P)
        return self.f(P[:, 0], P[:, 1])
