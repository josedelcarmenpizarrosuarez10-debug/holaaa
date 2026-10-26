"""Arma limites_peru.json desde el límite distrital del INEI (un solo archivo: distritos con su UBIGEO).

Uso:
    python herramientas_mapas/limites_censo.py distritos.shp|.zip|.geojson [--fuente "..."] [--fuente-corta "..."]

Los distritos se toman con su forma real; las provincias y los departamentos se arman uniendo sus distritos, así los
bordes de los tres niveles calzan exactos. Los nombres con tildes y las capitales se conservan de limites_peru.json
cuando el ubigeo ya existía; los nuevos se escriben con armar_limites._titulo. Los países vecinos no cambian.
La simplificación es menor que un píxel de cada mapa (distritos ~30 m, provincias ~65 m, departamentos ~165 m).
"""
import argparse
import json
import os
import sys
import time

from shapely.geometry import Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from herramientas_mapas.armar_limites import _titulo, leer  # noqa: E402

RUTA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "drenie_motor", "limites_peru.json")
TOL = {"departamentos": 0.0015, "provincias": 0.0006, "distritos": 0.0003}     # grados


def _anillos(g, tol):
    """Geometría compacta (ver ubicacion.decodificar): enteros en 1e-5 grados (~1 m), cada punto como diferencia con el anterior;
    anillos separados por «;» y polígonos por «|»."""
    g = g.buffer(0).simplify(tol, preserve_topology=True)
    polis = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if not isinstance(p, Polygon) or p.is_empty or p.area < tol * tol * 4: continue
        anillos = [p.exterior.coords] + [h.coords for h in p.interiors if Polygon(h).area > tol * tol * 4]
        txt = []
        for c in anillos:
            v, x0, y0 = [], 0, 0
            for x, y in c:
                xi, yi = int(round(x * 1e5)), int(round(y * 1e5)); v += [xi - x0, yi - y0]; x0, y0 = xi, yi
            txt.append(",".join(map(str, v)))
        polis.append(";".join(txt))
    return "|".join(polis)


def _puntos(g):
    return g.count(",") // 2 + 1 if g else 0


def _campo(p, *nombres):
    for n in nombres:
        for k, v in p.items():
            if k.upper() == n: return str(v).strip()
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("distritos")
    ap.add_argument("--fuente", default="INEI, límites distritales del Censo Nacional 2025 (vía GEO GPS Perú)")
    ap.add_argument("--fuente-corta", default="Límites: INEI (Censo 2025)")
    a = ap.parse_args()
    t0 = time.time()
    viejo = json.load(open(RUTA, encoding="utf-8"))
    nombre = {x["u"]: x["n"] for k in ("departamentos", "provincias", "distritos") for x in viejo[k]}
    capital = {x["u"]: x.get("cap", "") for x in viejo["distritos"]}
    dist, nom_prov, nom_dep = {}, {}, {}
    for g, p in leer(a.distritos):
        u = _campo(p, "UBIGEO", "IDDIST", "CODDIST").zfill(6)
        if len(u) != 6 or not u.isdigit(): print("  sin ubigeo:", p); continue
        dist[u] = unary_union([dist[u], g]) if u in dist else g
        nombre.setdefault(u, _titulo(_campo(p, "DISTRITO", "NOMBDIST")))
        nom_prov.setdefault(u[:4], _titulo(_campo(p, "PROVINCIA", "NOMBPROV")))
        nom_dep.setdefault(u[:2], _titulo(_campo(p, "DEPARTAMEN", "DEPARTAMENTO", "NOMBDEP")))
    print("distritos leídos: %d (%.0f s)" % (len(dist), time.time() - t0))
    provs = {}
    for u, g in dist.items(): provs.setdefault(u[:4], []).append(g)
    provs = {u: unary_union(gs) for u, gs in provs.items()}
    deps = {}
    for u, g in provs.items(): deps.setdefault(u[:2], []).append(g)
    deps = {u: unary_union(gs) for u, gs in deps.items()}
    print("provincias: %d, departamentos: %d (%.0f s)" % (len(provs), len(deps), time.time() - t0))
    L = {"fuente": a.fuente + "; países: Natural Earth (dominio público)", "fuente_corta": a.fuente_corta,
         "nota": "Distritos con su forma real; provincias y departamentos unidos desde sus distritos (bordes coincidentes).",
         "departamentos": [{"u": u, "n": nombre.get(u) or nom_dep[u], "g": _anillos(deps[u], TOL["departamentos"])} for u in sorted(deps)],
         "provincias": [{"u": u, "n": nombre.get(u) or nom_prov[u], "g": _anillos(provs[u], TOL["provincias"])} for u in sorted(provs)],
         "distritos": [{"u": u, "n": nombre.get(u), "cap": capital.get(u, ""), "g": _anillos(dist[u], TOL["distritos"])} for u in sorted(dist)],
         "paises": viejo["paises"], "formato": "e5d"}
    for k in ("departamentos", "provincias", "distritos"):
        print("  %s: %d, %d puntos" % (k, len(L[k]), sum(_puntos(x["g"]) for x in L[k])))
    json.dump(L, open(RUTA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("OK · %s (%.1f MB, %.0f s)" % (RUTA, os.path.getsize(RUTA) / 1e6, time.time() - t0))


if __name__ == "__main__":
    main()
