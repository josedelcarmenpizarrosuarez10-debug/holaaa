"""Mejora limites_peru.json con límites de forma real del Instituto Geográfico Nacional (IGN).

Uso:
    python herramientas_mapas/limites_ign.py provincias.geojson [distritos.geojson] [--fuente "..."]

provincias.geojson: provincias del IGN (geoBoundaries PER ADM2, o el shapefile/GeoJSON de «Límites de Perú» del IGN en HDX).
distritos.geojson (opcional): distritos del IGN (HDX, nivel 3).
Cada polígono nuevo se asigna a su provincia o distrito de limites_peru.json por superposición (no depende de cómo vengan
escritos los nombres); los departamentos se rehacen uniendo sus provincias. La simplificación es la mínima que el dibujo
necesita (menos de un píxel en cada mapa), así se conserva la forma real.
"""
import argparse
import json
import os
import sys

from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from herramientas_mapas.armar_limites import leer as leer_capa  # noqa: E402

RUTA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "drenie_motor", "limites_peru.json")
TOL = {"departamentos": 0.0015, "provincias": 0.0006, "distritos": 0.00025}     # grados (0.0006 ~ 65 m)


def _geom(g):
    gg = json.loads(g) if isinstance(g, str) else g
    polis = [Polygon(a[0], a[1:]) for a in gg if len(a[0]) >= 4]
    return MultiPolygon(polis) if len(polis) > 1 else polis[0]


def _anillos(g, tol):
    g = g.buffer(0).simplify(tol, preserve_topology=True)
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if not isinstance(p, Polygon) or p.is_empty or p.area < tol * tol * 4: continue
        out.append([[[round(x, 5), round(y, 5)] for x, y in p.exterior.coords]] +
                   [[[round(x, 5), round(y, 5)] for x, y in r.coords] for r in p.interiors])
    return out


def asignar(nuevos, viejos, nivel):
    """nuevos: lista de geometrías; viejos: entradas de limites_peru.json. Devuelve {u: geometría nueva} por mayor superposición."""
    from shapely.strtree import STRtree
    vg = [_geom(x["g"]).buffer(0) for x in viejos]
    arbol = STRtree(vg); por_u = {}
    for g in nuevos:
        g = g.buffer(0)
        cands = arbol.query(g)
        mejor = max(cands, key=lambda i: vg[i].intersection(g).area, default=None)
        if mejor is None or vg[mejor].intersection(g).area < 0.3 * min(vg[mejor].area, g.area):
            print("  sin pareja en %s: polígono de %.4f grados²" % (nivel, g.area)); continue
        u = viejos[mejor]["u"]
        por_u[u] = unary_union([por_u[u], g]) if u in por_u else g
    return por_u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("provincias"); ap.add_argument("distritos", nargs="?")
    ap.add_argument("--fuente", default="Departamentos y provincias: Instituto Geográfico Nacional (IGN), vía OCHA ROLAC y geoBoundaries (CC BY 3.0 IGO)")
    a = ap.parse_args()
    L = json.load(open(RUTA, encoding="utf-8"))
    provs = asignar([g for g, _ in leer_capa(a.provincias)], L["provincias"], "provincias")
    print("provincias con forma real: %d de %d" % (len(provs), len({x["u"] for x in L["provincias"]})))
    vistos = set()          # el archivo censal trae alguna provincia partida en dos entradas con el mismo código
    L["provincias"] = [x for x in L["provincias"] if not (x["u"] in provs and (x["u"] in vistos or vistos.add(x["u"])))]
    for x in L["provincias"]:
        if x["u"] in provs: x["g"] = _anillos(provs[x["u"]], TOL["provincias"])
    for x in L["departamentos"]:
        partes = [g for u, g in provs.items() if u[:2] == x["u"]]
        if partes: x["g"] = _anillos(unary_union(partes), TOL["departamentos"])
    if a.distritos:
        dists = asignar([g for g, _ in leer_capa(a.distritos)], [x for x in L["distritos"] if x.get("g")], "distritos")
        print("distritos con forma real: %d de %d" % (len(dists), len(L["distritos"])))
        for x in L["distritos"]:
            if x["u"] in dists: x["g"] = _anillos(dists[x["u"]], TOL["distritos"])
    L["fuente_corta"] = "Límites: IGN" + ("" if a.distritos else "; distritos: INEI 2007")
    L["fuente"] = a.fuente + ("" if a.distritos else "; distritos: INEI 2007 (límites censales)") + "; países: Natural Earth (dominio público)"
    json.dump(L, open(RUTA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("OK · %s (%.1f MB)" % (RUTA, os.path.getsize(RUTA) / 1e6))


if __name__ == "__main__":
    main()
