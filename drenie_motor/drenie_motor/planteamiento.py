"""Planteamiento automatico de cunetas para edificaciones y losa deportiva (usuario, 25-10-2026).

El agua de cada techo baja por su canaleta a los montantes de las esquinas; de cada dado sale un tubo de 4" embebido que debe
llegar a una cuneta (maximo 5 m). Por eso la cuneta puede ir a lo largo del alero (paralela) o por los lados cortos del techo
(transversal, como en el CAR Varones, CUI 2705619): lo que importa es que el tubo de cada montante llegue.
Para cada techo se prueban los lados de su contorno (desplazados fuera de la proyeccion del techo) y todas sus combinaciones; se
elige la que deja todos sus montantes al alcance con menos cuneta nueva, aprovechando las cunetas que ya hay (las del proyectista
y las de los techos vecinos). Menos cuneta larga: menos profundidad y descargas que si llegan.
Modos (proyecto "planteamiento"): "completar" (por defecto: solo agrega cuneta donde un montante no llega a las lineas del
proyectista), "automatico" (plantea todo desde cero, sin las lineas del proyectista) y "no".
"""
import itertools
import math

from shapely.geometry import LineString, Point
from shapely.ops import nearest_points, unary_union

from . import techo

PARAM = {"dist_alero": 0.30, "cubierta": 0.50, "empalme": 1.00, "pedazo_min": 0.80, "prolongar_max": 80.0, "tol_rayo": 0.60, "cerca_descarga": 3.0}


def _lineas(g):
    if g.is_empty: return []
    if g.geom_type == "LineString": return [g]
    return [x for x in getattr(g, "geoms", []) if x.geom_type == "LineString"]


def _paralelo(a, b, tol=20.0):
    (ax0, ay0), (ax1, ay1) = a.coords[0], a.coords[-1]; (bx0, by0), (bx1, by1) = b.coords[0], b.coords[-1]
    ua = math.atan2(ay1 - ay0, ax1 - ax0); ub = math.atan2(by1 - by0, bx1 - bx0)
    d = abs((ua - ub + math.pi / 2) % math.pi - math.pi / 2)
    return d < math.radians(tol)


def _empalmar(ls, red, d):
    """Lleva cada extremo de la linea al punto mas cercano de la red si queda a menos de d (empalme en T o en esquina)."""
    if red.is_empty: return ls
    cs = list(ls.coords)
    for i in (0, -1):
        p = Point(cs[i])
        if 1e-6 < red.distance(p) <= d:
            q = red.interpolate(red.project(p)) if red.geom_type == "LineString" else min(
                (g.interpolate(g.project(p)) for g in _lineas(red)), key=lambda x: x.distance(p))
            cs[i] = (q.x, q.y)
    return LineString(cs)


def _alinear(pz, lineas, tol=0.60):
    """Si la cuneta nueva es paralela a otra que ya existe y esta a menos de tol, se pone exactamente en su alineamiento
    (sin escalones de centimetros entre las cunetas de dos techos vecinos)."""
    for g in lineas:
        for seg in [LineString(c) for c in zip(g.coords[:-1], g.coords[1:])]:
            if seg.length < 0.5 or not _paralelo(pz, seg, 5.0) or seg.distance(pz) > tol: continue
            (ax, ay), (bx, by) = seg.coords[0], seg.coords[-1]; L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L

            def proy(p):
                t = (p[0] - ax) * ux + (p[1] - ay) * uy
                return (ax + ux * t, ay + uy * t)
            return LineString([proy(c) for c in pz.coords])
    return pz


def proponer(S, P, I, cfg, ejes):
    """Devuelve (lineas nuevas [[(x, y), ...]], informe por techo, avisos)."""
    modo = cfg.get("planteamiento", "completar")
    if modo == "no": return [], [], []
    pp = dict(PARAM); pp.update(cfg.get("planteamiento_parametros", {}))
    lados, _, K = techo.ubicar(S, P, I, cfg)
    tmax = K["tc"]["tubo_max"]
    alcance = tmax                  # al eje de la cuneta (conservador: el tubo se mide hasta su cara interior, y la red recorta pases y chaflanes)
    base = [LineString(e) for e in ejes if len(e) > 1]          # el motor ya paso solo las lineas que valen en cada modo
    techos = {}
    for l in lados:
        t = techos.setdefault(l["techo"], {"pol": [], "aleros": [], "montantes": []})
        t["pol"].append(l["ag"].get("techo_poligono") or l["ag"]["poligono"]); t["aleros"].append(l["alero"])
        t["montantes"] += [c for c, V, h in l["pos"]]
    for t in techos.values(): t["pol"] = unary_union(t["pol"])
    interior = S.interior
    elegidas, informe, avisos = [], [], []
    for nombre, t in sorted(techos.items(), key=lambda kv: -kv[1]["pol"].area):
        red = unary_union(base + elegidas)
        falta = [p for p in t["montantes"] if red.is_empty or red.distance(Point(p)) > alcance]
        if not falta:
            informe.append({"techo": nombre, "montantes": len(t["montantes"]), "decision": "ya cubierto",
                            "razon": "todos sus montantes llegan a una cuneta existente a %.1f m o menos" % tmax}); continue
        otros = unary_union([o["pol"] for k, o in techos.items() if k != nombre])
        # la cuneta no entra en otro techo, pero si puede ir en el espacio entre dos techos vecinos (la comparten)
        obst = otros.buffer(-0.05) if not otros.is_empty else otros
        rect = t["pol"].minimum_rotated_rectangle.buffer(pp["dist_alero"], join_style=2)
        cs = list(rect.exterior.coords)[:4]
        lados_c = []
        for i in range(4):
            s = LineString([cs[i], cs[(i + 1) % 4]])
            tipo = "a lo largo del alero" if any(_paralelo(s, a) for a in t["aleros"]) else "transversal"
            g = s.intersection(interior)
            if not obst.is_empty: g = g.difference(obst)
            piezas = [x for x in _lineas(g) if x.length >= pp["pedazo_min"]]
            if not piezas: continue
            lados_c.append({"linea": unary_union(piezas), "piezas": piezas, "tipo": tipo, "L": s.length})
        cubre = red.buffer(pp["cubierta"]) if not red.is_empty else None

        def nueva(x):
            return x["linea"].length - (x["linea"].intersection(cubre).length if cubre is not None else 0.0)
        opciones = []
        for k in range(1, len(lados_c) + 1):
            for sub in itertools.combinations(lados_c, k):
                u = unary_union([red] + [x["linea"] for x in sub]) if not red.is_empty else unary_union([x["linea"] for x in sub])
                if all(u.distance(Point(p)) <= alcance for p in t["montantes"]):
                    tipos = {x["tipo"] for x in sub}
                    opciones.append({"lados": sub, "nueva_m": sum(nueva(x) for x in sub), "n": k,
                                     "tipo": tipos.pop() if len(tipos) == 1 else "mixta"})
        if not opciones:
            avisos.append("%s: ninguna combinacion de cunetas alrededor del techo deja a sus %d montantes a %.1f m o menos (el cerco u "
                          "otras edificaciones lo impiden); plantear esa cuneta a mano." % (nombre, len(t["montantes"]), tmax))
            informe.append({"techo": nombre, "montantes": len(t["montantes"]), "decision": "sin solucion automatica"}); continue
        opciones.sort(key=lambda o: (round(o["nueva_m"], 1), o["n"], o["tipo"] != "transversal"))
        mejor = opciones[0]
        por_tipo = {}
        for o in opciones: por_tipo.setdefault(o["tipo"], o)
        for x in mejor["lados"]:
            g = x["linea"].difference(cubre) if cubre is not None else x["linea"]
            for pz in _lineas(g):
                if pz.length < pp["pedazo_min"]: continue
                pz = _alinear(pz, base + elegidas)
                pz = _empalmar(pz, unary_union(base + elegidas + [y["linea"] for y in mejor["lados"] if y is not x]), pp["empalme"])
                elegidas.append(pz)
        comp = "; ".join("%s %.1f m nuevos" % (k, o["nueva_m"]) for k, o in sorted(por_tipo.items()))
        informe.append({"techo": nombre, "montantes": len(t["montantes"]), "sin_cuneta_antes": len(falta), "decision": mejor["tipo"],
                        "nueva_m": round(mejor["nueva_m"], 2), "opciones": {k: round(o["nueva_m"], 2) for k, o in por_tipo.items()},
                        "razon": "menor cuneta nueva que deja todos sus montantes a %.1f m o menos (%s)" % (tmax, comp)})
    elegidas, prol = _prolongar(S, cfg, pp, base, elegidas, techos, P)
    if prol:
        informe.append({"techo": "-", "decision": "prolongaciones", "nueva_m": round(sum(x.length for x in prol), 2),
                        "razon": "%d cunetas prolongadas en linea recta hacia las descargas hasta otra cuneta o el cerco junto a una "
                                 "descarga (ejes rectos, como los traza el proyectista)" % len(prol)})
    return [[(round(x, 3), round(y, 3)) for x, y in l.coords] for l in elegidas], informe, avisos


def _prolongar(S, cfg, pp, base, elegidas, techos, P=None):
    """Cada cuneta planteada se prolonga en linea recta por su extremo de aguas abajo (hacia las descargas indicadas o, sin
    ellas, hacia el terreno mas bajo) hasta encontrar otra cuneta o el cerco junto a una descarga, sin entrar en ningun techo."""
    desc = [Point(d["x"], d["y"]) for d in (cfg.get("descargas") or [])]
    techos_u = unary_union([t["pol"] for t in techos.values()]).buffer(-0.05)
    borde = S.interior.exterior
    T = getattr(S, "T", None)

    def bajo(a, b):
        """True si ir de a hacia b es ir aguas abajo."""
        if desc: return min(b.distance(d) for d in desc) < min(a.distance(d) for d in desc) - 0.5
        if T is None: return False
        za, zb = T.z(a.x, a.y), T.z(b.x, b.y)
        return zb < za - 0.05

    nuevas = []
    hechas = set()
    for i in [k for _ in range(2) for k in range(len(elegidas))]:
        if i in hechas: continue
        ln = elegidas[i]
        cs = list(ln.coords)
        mejor = None
        for e, o in ((cs[-1], cs[-2]), (cs[0], cs[1])):
            E = Point(e); dx, dy = e[0] - o[0], e[1] - o[1]; L = math.hypot(dx, dy)
            if L < 1e-6: continue
            ux, uy = dx / L, dy / L
            rayo = LineString([(e[0] + ux * 0.05, e[1] + uy * 0.05), (e[0] + ux * pp["prolongar_max"], e[1] + uy * pp["prolongar_max"])])
            golpes = []
            # otra cuneta en la direccion del rayo (con tolerancia: lineas casi alineadas se empalman en su extremo)
            for g in base + [x for j, x in enumerate(elegidas) if j != i] + nuevas:
                if g.distance(E) < 0.05 or rayo.distance(g) > pp["tol_rayo"]: continue
                x = rayo.intersection(g)
                pts = [x] if x.geom_type == "Point" else [q for q in getattr(x, "geoms", []) if q.geom_type == "Point"]
                if not pts:
                    a, b = nearest_points(rayo, g); pts = [b]
                for p in pts: golpes.append((E.distance(p), p, False))
            x = rayo.intersection(borde)
            for p in ([x] if x.geom_type == "Point" else [q for q in getattr(x, "geoms", []) if q.geom_type == "Point"]):
                golpes.append((E.distance(p), p, True))
            if not golpes: continue
            d, H, es_borde = min(golpes, key=lambda z: z[0])
            # se empalma en un nudo que ya existe si esta a menos de 0.60 m (sin tramos de centimetros entre dos llegadas)
            anclas = [Point(c) for g in base + elegidas + nuevas for c in (g.coords[0], g.coords[-1])] + [Point(t.coords[-1]) for t in nuevas]
            cerca = [a for a in anclas if 1e-6 < a.distance(H) <= pp["tol_rayo"] and a.distance(E) > 0.05]
            if cerca and not es_borde: H = min(cerca, key=lambda a: a.distance(H)); d = E.distance(H)
            if es_borde:
                if desc:
                    if not any(H.distance(q) <= pp["cerca_descarga"] + 0.60 for q in desc): continue
                else:
                    # sin descargas indicadas: llega al cerco solo donde el terreno exterior queda bajo su cota de fondo
                    if T is None or P is None: continue
                    ze = T.z(H.x + ux * 1.5, H.y + uy * 1.5)
                    cf = S.rasante(H.x, H.y) - P["h0"] - P["S0"] * (ln.length + E.distance(H))
                    if not (ze == ze) or ze > cf - P["desc_margen"]: continue
            tramo = LineString([e, (H.x, H.y)])
            if tramo.length < 0.3 or (not techos_u.is_empty and tramo.intersection(techos_u).length > 0.05): continue
            if not (es_borde and not desc) and not bajo(E, H): continue     # al cerco basta que el terreno exterior quede bajo la C.F.
            if mejor is None or d < mejor[0]: mejor = (d, tramo)
        if mejor: nuevas.append(mejor[1]); hechas.add(i)
    return elegidas + nuevas, nuevas
