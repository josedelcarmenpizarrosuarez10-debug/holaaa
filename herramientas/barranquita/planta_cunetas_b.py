"""Cunetas en planta a escala real (1 unidad = 1 m) con el estilo de las laminas del usuario:
- cuneta con rejilla: bordes exterior (0.60) e interior (0.40) en celeste y platinas de la rejilla cada 0.10 m;
- cuneta tapada: bordes exterior e interior en verde (sin rejilla) y tapas de inspeccion 0.60 x 0.60 en azul;
- sentido del agua: flechas rojas en cada tramo y en cada quiebre a 45 grados.
Los contornos de cada sistema se unen (shapely) para que los empalmes queden limpios, sin lineas cruzadas.
"""
import math
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
import diseno_b as DS

BT, BI, EM = DS.B_TOT / 2, DS.B_INT / 2, DS.E_MURO      # 0.30, 0.20, 0.10
PASO_PLATINA = 0.10            # platinas de la rejilla en planta (simbolo a escala real)
PASO_FLECHA = 5.0              # una flecha roja cada 5 m de tramo recto
TAPA = 0.60                    # tapa de inspeccion 0.60 x 0.60 (ancho total de la cuneta)
MAX_TAPAS = 10.0               # distancia maxima entre tapas de inspeccion en un tramo tapado
CAPAS = [("CUN-REJ-BORDE", 4, "CONTINUOUS"), ("CUN-REJ-PLATINA", 4, "CONTINUOUS"), ("CUN-TAP-BORDE", 3, "CONTINUOUS"),
         ("CUN-FLUJO", 1, "CONTINUOUS"), ("CUN-TAPA-INSP", 5, "CONTINUOUS")]
RGB = {"CUN-REJ-BORDE": (0, 170, 230), "CUN-REJ-PLATINA": (120, 205, 240), "CUN-TAP-BORDE": (0, 150, 0),
       "CUN-FLUJO": (230, 0, 0), "CUN-TAPA-INSP": (0, 0, 230)}


def capas(doc, color_rgb):
    for n, c, lt in CAPAS:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt); ly.rgb = RGB[n]
        color_rgb[n] = RGB[n]


def _u(a, b):
    L = math.dist(a, b); return ((b[0] - a[0]) / L, (b[1] - a[1]) / L)


def eje_pts(R, r):
    """Eje de la cuneta; si termina en una descarga se prolonga 0.075 m hasta la cara exterior del cerco."""
    pts = [tuple(R["nudos"][n]) for n in r["nudos"]]
    if r["nudos"][-1] in DS.DESCARGAS:
        u = _u(pts[-2], pts[-1]); pts[-1] = (pts[-1][0] + u[0] * 0.075, pts[-1][1] + u[1] * 0.075)
    return pts


def _tapado(tap, s):
    return any(a - 1e-6 <= s <= b + 1e-6 for a, b in tap)


def _franja(pts, d, recorte_ini=0.0):
    """Franja de media anchura d a lo largo de pts (extremos planos, esquinas en inglete)."""
    ln = LineString(pts)
    if recorte_ini > 0: ln = LineString(_desde(pts, recorte_ini))
    return ln.buffer(d, cap_style=2, join_style=2, mitre_limit=5.0)


def _desde(pts, s0):
    ln = LineString(pts); p = ln.interpolate(s0); acc = 0.0; out = [(p.x, p.y)]
    for i in range(len(pts) - 1):
        acc += math.dist(pts[i], pts[i + 1])
        if acc > s0 + 1e-9: out.append(pts[i + 1])
    return out


def _anillos(g):
    gs = getattr(g, "geoms", [g])
    for p in gs:
        if p.is_empty: continue
        yield list(p.exterior.coords)
        for h in p.interiors: yield list(h.coords)


TAPAS = []                     # tapas de inspeccion dibujadas en la planta general (eje, progresiva, x, y, ux, uy)


def dibujar(lam, R, ramales):
    """Dibuja las cunetas de una lista de ramales (un sistema). Devuelve las tapas de inspeccion [(eje, s, x, y)]."""
    nudo_eje = {}
    for r in ramales:
        for n in r["nudos"]: nudo_eje.setdefault(n, set()).add(r["codigo"])
    ejes = [{"cod": r["codigo"], "pts": eje_pts(R, r), "tap": r["tapados"],
             "ini": len(nudo_eje.get(r["nudos"][0], ())) == 1,                       # nace en un cabezal (muro de 0.10)
             "recibe": [c for c in nudo_eje.get(r["nudos"][-1], ()) if c != r["codigo"]],
             "empalmes": [tuple(R["nudos"][n]) for n in r["nudos"][1:-1] if len(nudo_eje.get(n, ())) > 1],
             "descarga": r["nudos"][-1] in DS.DESCARGAS} for r in ramales]
    _dibujar(lam, ejes)
    t = _tapas(lam, ejes); TAPAS.extend(t); return t


def dibujar_tramos(lam, ejes):
    """Mismo dibujo para tramos sueltos (detalle de una descarga, 1/25): ejes = [{cod, pts, tap, ini, recibe}]."""
    _dibujar(lam, ejes, FLECHA_DET)


FLECHA_PL = (0.70, 0.30, 0.13, 0.07)     # flecha de la planta general 1/250: largo, punta, media punta, grosor (m)
FLECHA_DET = (0.40, 0.14, 0.06, 0.025)   # flecha de los detalles 1/25


def _dibujar(lam, ejes, ft=FLECHA_PL):
    lineas = {e["cod"]: LineString(e["pts"]) for e in ejes}
    ext = unary_union([_franja(e["pts"], BT) for e in ejes])
    ints = unary_union([_franja(e["pts"], BI, EM if e["ini"] else 0.0) for e in ejes])
    # bordes: cada pedazo toma el estado (tapado / rejilla) del eje mas cercano
    def estado(x, y):
        pt = Point(x, y); e = min(ejes, key=lambda e: lineas[e["cod"]].distance(pt))
        return _tapado(e["tap"], lineas[e["cod"]].project(pt))
    for g in (ext, ints):
        for anillo in _anillos(g):
            cur, est = [anillo[0]], None
            for a, b in zip(anillo[:-1], anillo[1:]):
                L = math.dist(a, b); n = max(1, int(L / 0.25))
                for k in range(n):                                   # el estado puede cambiar dentro de un lado largo
                    p = (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
                    q = (a[0] + (b[0] - a[0]) * (k + 0.5) / n, a[1] + (b[1] - a[1]) * (k + 0.5) / n)
                    e = estado(*q)
                    if est is not None and e != est:
                        lam.poli(cur, "CUN-TAP-BORDE" if est else "CUN-REJ-BORDE"); cur = [cur[-1]]
                    cur.append(p); est = e
            if len(cur) > 1: lam.poli(cur, "CUN-TAP-BORDE" if est else "CUN-REJ-BORDE")
    # platinas de la rejilla (solo en los tramos abiertos); el eje que llega no las repite dentro de la cuneta que lo recibe
    for e in ejes:
        ln = lineas[e["cod"]]
        recibe = [lineas[c] for c in e["recibe"] if c in lineas]
        s = (EM if e["ini"] else 0.0) + PASO_PLATINA / 2
        while s < ln.length - 0.02:
            if not _tapado(e["tap"], s):
                p = ln.interpolate(s); q = ln.interpolate(min(ln.length, s + 0.01)); o = ln.interpolate(max(0.0, s - 0.01))
                ux, uy = _u((o.x, o.y), (q.x, q.y))
                if not any(x.distance(p) < BT + 0.02 for x in recibe):
                    lam.linea((p.x - uy * BI, p.y + ux * BI), (p.x + uy * BI, p.y - ux * BI), "CUN-REJ-PLATINA")
            s += PASO_PLATINA
    # flechas rojas de flujo
    for e in ejes:
        pts = e["pts"]
        for a, b in zip(pts[:-1], pts[1:]):
            L = math.dist(a, b)
            if L < 0.4: continue
            u = _u(a, b)
            n = max(1, int(L // PASO_FLECHA)) if L >= 2.0 else 1
            for j in range(n):
                flecha(lam, (a[0] + u[0] * (j + 0.5) * L / n, a[1] + u[1] * (j + 0.5) * L / n), u, *ft)


def _tapas(lam, ejes):
    """Tapas de inspeccion en los tramos tapados: inicio y fin, empalmes y a MAX_TAPAS como maximo."""
    tapas = []
    for e in ejes:
        ln = LineString(e["pts"]); L = ln.length
        pos = []
        for a, b in e["tap"]:
            a2 = a + (0.0 if a > 0.01 else EM)
            if b >= L - 0.08:
                b2 = L - (0.075 + 0.15 + TAPA / 2 if e["descarga"] else BT + TAPA / 2)   # lejos del cerco o de la cuneta que recibe
            else:
                b2 = b
            i0, i1 = a2 + TAPA / 2 + 0.10, b2 - TAPA / 2 - 0.10
            if i1 < i0:
                if b2 - a2 >= TAPA + 0.10: pos.append((a2 + b2) / 2)
                continue
            n = max(1, math.ceil((i1 - i0) / MAX_TAPAS))
            pos += [i0 + (i1 - i0) * k / n for k in range(n + 1)] if i1 - i0 > 0.5 else [(i0 + i1) / 2]
        for pe in e["empalmes"]:                                            # empalmes dentro de un tramo tapado
            sN = ln.project(Point(pe))
            if _tapado(e["tap"], sN) and all(abs(sN - p) > 2.0 for p in pos): pos.append(sN)
        for s in sorted(pos):
            p = ln.interpolate(s); q = ln.interpolate(min(L, s + 0.01)); o = ln.interpolate(max(0.0, s - 0.01))
            u = _u((o.x, o.y), (q.x, q.y)); tapa(lam, (p.x, p.y), u)
            tapas.append((e["cod"], round(s, 2), p.x, p.y, u[0], u[1]))
    return tapas


def flecha(lam, c, u, largo=0.70, t=0.30, w=0.13, g=0.07):
    """Flecha roja gruesa dentro de la cuneta (largo, punta t, media punta w y grosor g en m)."""
    a = (c[0] - u[0] * largo / 2, c[1] - u[1] * largo / 2); b = (c[0] + u[0] * largo / 2, c[1] + u[1] * largo / 2)
    base = (b[0] - u[0] * t, b[1] - u[1] * t)
    lam.poli([a, base], "CUN-FLUJO", ancho=g)
    lam.solido([b, (base[0] - u[1] * w, base[1] + u[0] * w), (base[0] + u[1] * w, base[1] - u[0] * w), (base[0] + u[1] * w, base[1] - u[0] * w)], "CUN-FLUJO")


def tapa(lam, c, u):
    """Tapa de inspeccion 0.60 x 0.60 (concreto removible) con sus dos asas."""
    n = (-u[1], u[0]); h = TAPA / 2
    q = [(c[0] + sx * u[0] * h + sy * n[0] * h, c[1] + sx * u[1] * h + sy * n[1] * h) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    lam.poli(q, "CUN-TAPA-INSP", cerrada=True, ancho=0.03)
    for sx in (-0.17, 0.17):
        m = (c[0] + u[0] * sx, c[1] + u[1] * sx)
        lam.poli([(m[0] - n[0] * 0.07, m[1] - n[1] * 0.07), (m[0] + n[0] * 0.07, m[1] + n[1] * 0.07)], "CUN-TAPA-INSP", ancho=0.025)
