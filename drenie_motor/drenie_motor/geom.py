"""Utilidades geometricas y seleccion de entidades de la base del sitio."""
import math

from shapely.geometry import LineString, Polygon, Point, MultiPolygon
from shapely.ops import polygonize, unary_union


def _coincide(sel, capa, color):
    if sel is None: return False
    if isinstance(sel, (list, tuple)): return any(_coincide(s, capa, color) for s in sel)
    if isinstance(sel, str): return capa == sel
    if "capa" in sel and capa != sel["capa"]: return False
    if "color" in sel and color != sel["color"]: return False
    return True


def seleccionar(B, sel):
    """Polilineas de la base que cumplen la seleccion: "CAPA", {"capa": "CAPA", "color": 6} o una lista de ellas."""
    out = []
    for capa, ents in B["geo"].items():
        for pts, cl, col, z in ents:
            if _coincide(sel, capa, col): out.append((pts, cl, col, z))
    return out


def textos(B, sel):
    return [t for t in B["txt"] if _coincide(sel, t[0], t[5])]


def poligonos(ents, area_min=0.05):
    """Poligonos de una seleccion: las polilineas cerradas y las caras que forman las lineas abiertas."""
    pols, lineas = [], []
    for pts, cl, col, z in ents:
        if cl and len(pts) >= 3:
            p = Polygon(pts).buffer(0)
            if p.area > area_min: pols.append(p)
        else:
            lineas.append(LineString(pts))
    if lineas:
        for p in polygonize(unary_union(lineas)):
            if p.area > area_min: pols.append(p)
    return pols


def poligonos_tolerantes(ents, tol=0.05, area_min=2.0, rellenar=True):
    """Caras que forman las lineas aunque no cierren exactamente: se cierran separaciones de hasta 2 x tol (como en
    Barranquita con 0_PROYECCIONES 1). Con rellenar, cada contorno se toma lleno (sin los huecos de lineas interiores)."""
    lineas = [LineString(list(p) + ([p[0]] if cl else [])) for p, cl, col, z in ents if len(p) >= 2]
    if not lineas: return []
    red = unary_union(lineas).buffer(tol, join_style=2)
    caras = []
    for g in (red.geoms if hasattr(red, "geoms") else [red]):
        for h in g.interiors:
            c = Polygon(h).buffer(tol, join_style=2)          # se devuelve el ancho de la linea a la cara
            if c.area >= area_min: caras.append(c)
    if not caras: return []
    u = unary_union(caras)
    if rellenar:
        u = unary_union([Polygon(p.exterior) for p in (u.geoms if hasattr(u, "geoms") else [u])])
    return [p for p in (u.geoms if hasattr(u, "geoms") else [u]) if p.area >= area_min]


def union(pols):
    if not pols: return MultiPolygon()
    return unary_union([p.buffer(0) for p in pols])


def dist(a, b): return math.hypot(b[0] - a[0], b[1] - a[1])


def unit(a, b):
    L = dist(a, b)
    return ((b[0] - a[0]) / L, (b[1] - a[1]) / L), L


def giro(a, b, c):
    """Angulo de cambio de direccion en b (grados): 0 = sigue recto."""
    u = (b[0] - a[0], b[1] - a[1]); v = (c[0] - b[0], c[1] - b[1])
    cs = (u[0] * v[0] + u[1] * v[1]) / (math.hypot(*u) * math.hypot(*v))
    return math.degrees(math.acos(max(-1.0, min(1.0, cs))))


def area_firmada(pts):
    n = len(pts)
    return sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)) / 2.0
