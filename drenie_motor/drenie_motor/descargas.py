"""Detalle de las descargas por el cerco (una lamina por descarga), para cualquier proyecto de DrenIE.

Portado del generador de la I.E. N.° 0590 Barranquita (C.I. 468901, herramientas/barranquita/descargas_b.py): mismos dibujos,
con los datos del diseno del proyecto (red con cotas, ancho del eje que sale, cerco, terreno y niveles).

Una lamina A1 por descarga (D1 a D4), solo de la esquina de salida:
- PLANTA de detalle (1/25): ultimo tramo del eje que sale (con sus quiebres a 45 grados), ejes que llegan, rejilla, tramo tapado,
  pase bajo el cerco, curvas de nivel exteriores y sentido del agua.
- PERFIL LONGITUDINAL (1/25, H = V): losa de fondo, borde (NCT), losa tapa, agua de diseno, pase por el cimiento del cerco,
  terreno natural exterior y perfilado; recuadros de seccion y guitarra.
- ISOMETRICO (1/50): solo esa esquina, cada elemento en su capa (piso, terreno, concreto, losa, rejilla, cerco, agua); caras ocultas
  eliminadas para que el dibujo se lea limpio.
No cambia ninguna cota. Lo usa planos.dxf_planos.
"""
import math
import numpy as np
from ezdxf.enums import TextEntityAlignment as TA

from . import dxf_base as B
from . import planta_lamina as PLT


class _Datos:
    """Lo que el dibujo toma del proyecto (antes: diseno_b, terreno_b y planta_cunetas_b de Barranquita)."""
    CERCO, DESCARGAS, B_INT, B_TOT, NIVELES = [], [], 0.40, 0.60, ""
    TAPAS = []
    _z, _curvas = None, []

    def modelo(self): return self._z
    def curvas(self): return self._curvas


DS = T = _Datos()

ESC = 25                     # toda la lamina a 1/25: planta, perfil e isometrico a escala real (1 unidad = 1 m)
ESC_ISO = ESC_PL = ESC
LW, EXT = 6.0, 2.5           # metros de cuneta antes del cerco y de terreno exterior (perfil)
LPL, LISO = 4.0, 3.0         # metros de cuneta que se ven en la planta y en el isometrico
EXT_ISO = 1.75               # metros de terreno exterior en el isometrico
BI, BT = DS.B_INT / 2, DS.B_TOT / 2           # media luz y medio ancho exterior del eje que sale (se fijan por descarga)
EL = 0.10
CAPAS = [("DET-MURO", 250, "CONTINUOUS"), ("DET-LOSA", 8, "CONTINUOUS"), ("DET-REJILLA", 1, "CONTINUOUS"), ("DET-CERCO", 1, "CONTINUOUS"),
         ("DET-CURVAS", 33, "DASHED"), ("DET-AGUA", 150, "CONTINUOUS"), ("DET-NCT", 5, "CONTINUOUS"), ("DET-TAPA", 3, "CONTINUOUS"),
         ("DET-FONDO", 6, "CONTINUOUS"), ("DET-TERRENO", 32, "DASHED"), ("DET-PERFILADO", 1, "DASHED"), ("DET-CIMIENTO", 8, "CONTINUOUS"),
         ("DET-SECCION", 1, "CONTINUOUS"), ("ISOD-PISO", 9, "CONTINUOUS"), ("ISOD-TERRENO", 94, "CONTINUOUS"), ("ISOD-SUP", 254, "CONTINUOUS"),
         ("ISOD-INT", 252, "CONTINUOUS"), ("ISOD-FONDO", 253, "CONTINUOUS"), ("ISOD-LOSA", 8, "CONTINUOUS"), ("ISOD-REJILLA", 1, "CONTINUOUS"),
         ("ISOD-CERCO", 14, "CONTINUOUS"), ("ISOD-AGUA", 150, "CONTINUOUS"), ("ISOD-HUECO", 250, "CONTINUOUS"), ("ISOD-ARISTA", 8, "CONTINUOUS")]
RGB = {"DET-MURO": (215, 215, 215), "DET-LOSA": (165, 165, 165), "DET-CERCO": (225, 120, 120), "DET-AGUA": (190, 222, 245),
       "DET-CIMIENTO": (200, 200, 200), "ISOD-PISO": (243, 240, 232), "ISOD-TERRENO": (214, 226, 196), "ISOD-SUP": (236, 236, 236),
       "ISOD-INT": (196, 196, 196), "ISOD-FONDO": (176, 176, 176), "ISOD-LOSA": (150, 150, 150), "ISOD-CERCO": (232, 190, 190),
       "ISOD-AGUA": (130, 190, 240), "ISOD-HUECO": (60, 60, 60)}


def capas(doc):
    for n, c, lt in CAPAS:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt)
            if n in RGB: ly.rgb = RGB[n]
    for n, rgb in RGB.items(): B.COLOR_RGB[n] = rgb


# ----------------------------------------------------------------------------- geometria
def _u(a, b):
    L = math.dist(a, b); return ((b[0] - a[0]) / L, (b[1] - a[1]) / L)


def _perp(u): return (-u[1], u[0])


def offset(poly, d):
    """Polilinea desplazada d a la izquierda, con inglete en los quiebres."""
    out = []
    for i, p in enumerate(poly):
        if i == 0: n = _perp(_u(poly[0], poly[1]))
        elif i == len(poly) - 1: n = _perp(_u(poly[-2], poly[-1]))
        else:
            n1, n2 = _perp(_u(poly[i - 1], p)), _perp(_u(p, poly[i + 1]))
            m = (n1[0] + n2[0], n1[1] + n2[1]); Lm = math.hypot(*m); m = (m[0] / Lm, m[1] / Lm)
            k = 1.0 / max(0.3, m[0] * n1[0] + m[1] * n1[1]); n = (m[0] * k, m[1] * k)
        out.append((p[0] + n[0] * d, p[1] + n[1] * d))
    return out


def _acum(poly):
    s = [0.0]
    for a, b in zip(poly[:-1], poly[1:]): s.append(s[-1] + math.dist(a, b))
    return s


def _en(poly, s_list, s):
    """Punto y direccion en la abscisa s de la polilinea."""
    for i in range(1, len(poly)):
        if s <= s_list[i] + 1e-9 or i == len(poly) - 1:
            t = 0 if s_list[i] == s_list[i - 1] else (s - s_list[i - 1]) / (s_list[i] - s_list[i - 1])
            a, b = poly[i - 1], poly[i]
            return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), _u(a, b)


def _sub(poly, s_list, s0, s1):
    """Tramo de polilinea entre s0 y s1 (con sus vertices interiores)."""
    out = [_en(poly, s_list, s0)[0]]
    for p, s in zip(poly, s_list):
        if s0 + 1e-6 < s < s1 - 1e-6: out.append(p)
    out.append(_en(poly, s_list, s1)[0]); return out


def _valor(P, s):
    for i in range(1, len(P)):
        if P[i][0] >= s - 1e-9:
            a, b = P[i - 1], P[i]; t = 0 if b[0] == a[0] else (s - a[0]) / (b[0] - a[0])
            return a[1] + t * (b[1] - a[1]), a[2] + t * (b[2] - a[2])
    return P[-1][1], P[-1][2]


def datos(R, V, D):
    r = next(x for x in R["ramales"] if x["nudos"][-1] == D)
    N = {k: tuple(v) for k, v in R["nudos"].items()}; nom = {k: k for k in N}
    poly = [N[n] for n in r["nudos"]]; sl = _acum(poly); L = sl[-1]
    s_a = max(0.0, L - LW)
    # la cuneta termina en la cara exterior del cerco (0.075 m pasando el eje del cerco)
    u = _u(poly[-2], poly[-1])
    cuneta = _sub(poly, sl, s_a, L) + [(poly[-1][0] + u[0] * 0.075, poly[-1][1] + u[1] * 0.075)]
    nodos = [(s, n) for s, n in zip(sl, r["nudos"]) if s >= s_a - 1e-6]
    llegan = []
    for r2 in R["ramales"]:
        if r2 is r: continue
        fin = r2["nudos"][-1]
        if fin in r["nudos"]:
            sN = sl[r["nudos"].index(fin)]
            if sN >= s_a - 1e-6:
                p2 = [N[n] for n in r2["nudos"]]; s2 = _acum(p2)
                llegan.append({"eje": r2["codigo"], "nudo": fin, "s": sN, "poly": _sub(p2, s2, max(0, s2[-1] - 3.0), s2[-1]), "r": r2})
    dsc = next(x for x in V["descargas"] if x["D"] == D)
    hid = [f for f in V["hidraulica"] if f["eje"] == r["codigo"]]
    y = hid[-1]["y"] if hid else 0.05
    z = T.modelo()
    ext = [(d, z(poly[-1][0] + u[0] * d, poly[-1][1] + u[1] * d)) for d in np.arange(0.0, EXT + 0.01, 0.25)]
    ext = [(d, zz) for d, zz in ext if np.isfinite(zz)]
    return {"D": D, "r": r, "poly": poly, "sl": sl, "L": L, "s_a": s_a, "cuneta": cuneta, "u": u, "nodos": nodos, "llegan": llegan,
            "nom": nom, "dsc": dsc, "y": y, "ext": ext, "z": z, "Q": hid[-1]["Q_ls"] if hid else 0.0}


PL_VENT = (107, 345, 388, 560)        # ventana de la planta en la lamina (mm): x0, y0, x1, y1 (rotulos a los lados)
MG_PL = 0.6                            # margen alrededor de la cuneta en la planta (m)


def _caja_pl(d):
    xs = [p[0] for p in d["cuneta"]] + [p[0] for ll in d["llegan"] for p in ll["poly"]]
    ys = [p[1] for p in d["cuneta"]] + [p[1] for ll in d["llegan"] for p in ll["poly"]]
    return min(xs) - MG_PL, max(xs) + MG_PL, min(ys) - MG_PL, max(ys) + MG_PL


def _planta_que_entra(d):
    """Recorte mas largo (4.0 m a 2.0 m) cuya planta a escala real entra en la ventana de la lamina."""
    wmax, hmax = (PL_VENT[2] - PL_VENT[0]) * ESC / 1000, (PL_VENT[3] - PL_VENT[1] - 15) * ESC / 1000
    for lc in (LPL, 3.5, 3.0, 2.5, 2.0):
        dp = _recorte(d, lc, min(2.0, lc / 2 + 0.5))
        x0, x1, y0, y1 = _caja_pl(dp)
        if x1 - x0 <= wmax and y1 - y0 <= hmax: return dp
    return dp


def _recorte(d, lc, lleg):
    """Misma descarga mostrando solo los ultimos lc m del eje y lleg m de cada eje que llega."""
    poly = d["poly"]; sl = _acum(poly); L = d["L"]
    s_a = max(0.0, L - lc)
    llegan = []
    for ll in d["llegan"]:
        if ll["s"] < s_a - 1e-6: continue
        pl = ll["poly"]; s2 = _acum(pl)
        llegan.append({**ll, "poly": _sub(pl, s2, max(0.0, s2[-1] - lleg), s2[-1])})
    return {**d, "s_a": s_a, "cuneta": _sub(poly, sl, s_a, L) + [d["cuneta"][-1]],
            "nodos": [(s, n) for s, n in d["nodos"] if s >= s_a - 1e-6], "llegan": llegan}


# ----------------------------------------------------------------------------- planta 1/25
def _paredes(lam, poly, M, capa="DET-MURO"):
    for sg in (1, -1):
        a, b = offset(poly, sg * BT), offset(poly, sg * BI)
        pts = [M(p) for p in a + b[::-1]]
        lam.relleno(pts, capa); lam.poli(pts, "CONCRETO", cerrada=True)


def planta(lam, d, cx, cy):
    f = lam.f; poly = d["cuneta"]
    bx0, bx1, by0, by1 = _caja_pl(d)
    c0 = ((bx0 + bx1) / 2, (by0 + by1) / 2)
    o = lam.P(cx, cy); kp = ESC / ESC_PL                 # kp = 1: escala real
    M = lambda p: (o[0] + kp * (p[0] - c0[0]), o[1] + kp * (p[1] - c0[1]))
    xd, yd = d["poly"][-1]; u = d["u"]
    # curvas de nivel alrededor (afuera del cerco se ven; adentro el piso esta nivelado)
    from matplotlib.path import Path
    ce = Path(DS.CERCO)
    dentro = lambda p: bx0 <= p[0] <= bx1 and by0 <= p[1] <= by1
    for zc, pts in T.curvas():
        tramo = []
        for p in pts + [None]:
            if p is not None and bx0 < p[0] < bx1 and by0 < p[1] < by1 and not ce.contains_point(p): tramo.append(p); continue
            if len(tramo) > 2:
                lam.poli([M(q) for q in tramo], "DET-CURVAS")
                lam.texto(M(tramo[len(tramo) // 2]), "%.1f" % zc, 1.3, "CURVAS-TXT" if "CURVAS-TXT" in lam.doc.layers else "TEXTOS", TA.MIDDLE_CENTER)
            tramo = []
    # cerco (muro de 0.15 m) en un radio de 4 m
    for i in range(len(DS.CERCO)):
        a, b = DS.CERCO[i], DS.CERCO[(i + 1) % len(DS.CERCO)]
        L = math.dist(a, b); pts = []
        for k in range(int(L / 0.1) + 1):
            p = (a[0] + (b[0] - a[0]) * k * 0.1 / L, a[1] + (b[1] - a[1]) * k * 0.1 / L)
            if dentro(p): pts.append(p)
            elif len(pts) > 1: break
        if len(pts) > 1:
            w = [M(p) for p in offset(pts, 0.075) + offset(pts, -0.075)[::-1]]
            lam.relleno(w, "DET-CERCO"); lam.poli(w, "DET-CERCO", cerrada=True)
    # cunetas con el mismo dibujo de la planta general (escala real): rejilla en celeste, tapado en verde, flechas rojas
    r = d["r"]; sl = _acum(poly)
    s_off = d["s_a"]
    tap = [(max(a, s_off) - s_off, min(b, d["L"]) - s_off) for a, b in r["tapados"] if b > s_off]
    if tap and tap[-1][1] >= d["L"] - s_off - 0.01: tap[-1] = (tap[-1][0], sl[-1])
    abiertos, s0 = [], 0.0
    for a, b in tap:
        if a > s0 + 0.05: abiertos.append((s0, a))
        s0 = b
    if s0 < sl[-1] - 0.05: abiertos.append((s0, sl[-1]))
    ejes = [{"cod": r["codigo"], "pts": [M(p) for p in poly], "tap": tap, "ini": s_off < 0.01, "recibe": [], "b": 2 * BI}]
    for ll in d["llegan"]:
        pl = ll["poly"]; s2 = _acum(pl); ini2 = ll["r"]["L"] - s2[-1]
        ejes.append({"cod": ll["eje"], "pts": [M(p) for p in pl], "recibe": [r["codigo"]], "ini": ini2 < 0.01, "b": ll.get("b", 2 * BI),
                     "tap": [(max(a, ini2) - ini2, b - ini2) for a, b in ll["r"]["tapados"] if b > ini2]})
    PLT.dibujar_ejes(lam, ejes, BT - BI, (0.40, 0.14, 0.06, 0.025))
    for t in DS.TAPAS:                                     # las mismas tapas de inspeccion de la planta general
        if bx0 <= t["x"] <= bx1 and by0 <= t["y"] <= by1 and t["eje"] in [e["cod"] for e in ejes]: PLT.tapa(lam, M((t["x"], t["y"])), t["u"])
    # agua afuera
    pa = M((xd + u[0] * 0.2, yd + u[1] * 0.2)); pb = M((xd + u[0] * 1.3, yd + u[1] * 1.3))
    lam.flecha(pa, pb, "FLUJO", tam_mm=4.0)
    # rotulos: en dos columnas fuera del dibujo (izquierda / derecha), sin cruces
    nom = d["nom"]; it = []
    it.append((M(_en(poly, sl, 1.0)[0]), [d["r"]["codigo"] + " (sale por %s)" % d["D"], "cuneta %.2f m: muros %.2f + %.2f libres" % (2 * BT, BT - BI, 2 * BI)]))
    for ll in d["llegan"]:
        it.append((M(ll["poly"][0]), ["Llega " + ll["eje"]]))
    if tap:
        a, b = tap[-1]
        it.append((M(_en(poly, sl, (a + b) / 2)[0]), ["TRAMO TAPADO: LOSA e = 0.10 m", "pase bajo el cerco (cimiento)"]))
    if abiertos:
        a, b = abiertos[0]
        it.append((M(_en(poly, sl, min(b - 0.3, a + 1.5))[0]), ["REJILLA MOVIL DE PLATINAS 1\" x 3/16\""]))
    it.append((pb, ["AGUA AL TERRENO NATURAL"]))
    it.append((M((xd, yd)), ["DESCARGA %s: C.F. %.3f" % (d["D"], d["dsc"]["cf"])]))
    pc = M((xd + _perp(u)[0] * 1.2, yd + _perp(u)[1] * 1.2))
    it.append((pc, ["MURO DEL CERCO PERIMETRICO e = 0.15"]))
    X0, Y0 = M((bx0, by0)); X1, Y1 = M((bx1, by1))
    xm = (X0 + X1) / 2
    izq = [i for i in it if i[0][0] < xm]; der = [i for i in it if i[0][0] >= xm]
    yt, yb = min(Y1 - 8 * f, lam.P(0, PL_VENT[3] - 10)[1]), max(Y0 + 8 * f, lam.P(0, PL_VENT[1] + 5)[1])
    lam.columna_llamadas(izq, X0 - 10 * f, yt, yb, hmm=1.8, al=TA.RIGHT)
    lam.columna_llamadas(der, X1 + 10 * f, yt, yb, hmm=1.8)
    puestos = []
    for s, n in d["nodos"]:
        if "~" in n or n in DS.DESCARGAS: continue
        p = M(dict(zip(d["r"]["nudos"], d["poly"]))[n]); lam.circulo(p, 0.12 * kp, "NUDOS")
        if any(math.dist(p, q) < 9 * f for q in puestos): continue          # nudos muy juntos: un solo rotulo
        puestos.append(p); lam.texto((p[0] + 2 * f, p[1] + 2 * f), nom[n], 1.5, "TEXTOS", TA.LEFT)
    # norte
    pn = lam.P(40, PL_VENT[3] - 12)
    lam.flecha((pn[0], pn[1] - 8 * f), (pn[0], pn[1] + 4 * f), "TEXTOS", tam_mm=3.0)
    lam.texto((pn[0], pn[1] + 6 * f), "N", 2.4, "TITULOS", TA.BOTTOM_CENTER)
    return M


# ----------------------------------------------------------------------------- perfil longitudinal 1/25
def perfil(lam, d, x0mm, y0mm):
    f = lam.f; r = d["r"]; P = r["perfil"]; s_a, L = d["s_a"], d["L"]
    seg = [[s_a, *_valor(P, s_a)]] + [p for p in P if p[0] > s_a + 1e-6]
    zfmin = min(p[2] for p in seg)
    zmin = max(min(zfmin - 0.45, min(z for _, z in d["ext"]) - 0.1), zfmin - 0.95)     # el talud exterior se corta a ~1 m bajo la C.F.
    filas = ["Progresiva (m)", "Borde NCT", "Cota de fondo NCF", "Altura H (m)", "Terreno natural"]
    AF = 6.5; yg = y0mm; yg1 = yg + AF * len(filas)
    xd0 = x0mm + 36
    X = lambda s: lam.P(xd0 + (s - s_a) / f, 0)[0]
    Yz = lambda z: lam.P(0, yg1 + 14 + (z - zmin) / f)[1]
    xfin = X(L + EXT)
    for i, t in enumerate(filas + [None]):
        yy = yg1 - i * AF
        lam.linea(lam.P(x0mm, yy), (xfin, lam.P(0, yy)[1]), "GUITARRA")
        if t: lam.texto(lam.P(xd0 - 2, yy - AF / 2), t, 1.5, "TEXTOS", TA.MIDDLE_RIGHT)
    lam.linea(lam.P(xd0, yg), lam.P(xd0, yg1), "GUITARRA")
    # piso interior (NPT) y losa de fondo (corte), solado
    tap = [(max(a, s_a), min(b, L)) for a, b in r["tapados"] if b > s_a]
    lam.poli([(X(p[0]), Yz(p[1])) for p in seg], "ARQ-BASE")
    fondo = [(X(p[0]), Yz(p[2])) for p in seg] + [(X(L + 0.075), Yz(seg[-1][2]))]
    bajo = [(X(p[0]), Yz(p[2] - EL)) for p in seg] + [(X(L + 0.075), Yz(seg[-1][2] - EL))]
    lam.relleno(fondo + bajo[::-1], "CONCRETO-ACHURADO"); lam.poli(fondo + bajo[::-1], "DET-FONDO", cerrada=True)
    sol = [(x, y - 0.05) for x, y in bajo]
    lam.poli(sol, "SOLADO")
    # agua de diseno
    agua = [(X(p[0]), Yz(p[2] + d["y"])) for p in seg] + [(X(L + 0.075), Yz(seg[-1][2] + d["y"]))]
    lam.relleno(fondo[:-1] + [fondo[-1]] + agua[::-1], "DET-AGUA"); lam.poli(agua, "AGUA")
    # borde (NCT): azul abierto; tapado: losa cortada (verde)
    abiertos, s0 = [], s_a
    for a, b in tap:
        if a > s0 + 0.05: abiertos.append((s0, a))
        s0 = b
    if s0 < L - 0.05: abiertos.append((s0, L))
    for a, b in abiertos:
        lam.linea((X(a), Yz(_valor(P, a)[0])), (X(b), Yz(_valor(P, b)[0])), "DET-NCT")
        lam.linea((X(a), Yz(_valor(P, a)[0]) + 0.0254), (X(b), Yz(_valor(P, b)[0]) + 0.0254), "DET-REJILLA")
    for a, b in tap:
        b2 = L + 0.075 if b >= L - 0.01 else b
        nct = _valor(P, a)[0]
        q = [(X(a), Yz(nct)), (X(b2), Yz(nct)), (X(b2), Yz(nct - 0.10)), (X(a), Yz(nct - 0.10))]
        lam.relleno(q, "CONCRETO-ACHURADO"); lam.poli(q, "DET-TAPA", cerrada=True)
    # cerco: muro cortado (0.15) sobre el pase y cimiento corrido bajo el pase
    nctL, ncfL = _valor(P, L)
    xm0, xm1 = X(L - 0.075), X(L + 0.075)
    muro = [(xm0, Yz(nctL)), (xm1, Yz(nctL)), (xm1, Yz(nctL + 0.40)), (xm0, Yz(nctL + 0.40))]
    lam.relleno(muro, "DET-CERCO"); lam.poli(muro, "DET-CERCO", cerrada=True)
    zc0 = ncfL - EL - 0.05; zc1 = zc0 - 0.40
    cim = [(X(L - 0.20), Yz(zc0)), (X(L + 0.20), Yz(zc0)), (X(L + 0.20), Yz(zc1)), (X(L - 0.20), Yz(zc1))]
    lam.relleno(cim, "DET-CIMIENTO"); lam.poli(cim, "DET-CIMIENTO", cerrada=True)
    # terreno natural exterior y perfilado
    ter = [(X(L + dd), Yz(max(zz, zmin + 0.05))) for dd, zz in d["ext"]]
    if len(ter) > 1: lam.poli(ter, "DET-TERRENO")
    if min(z for _, z in d["ext"]) < zmin + 0.05:
        lam.texto((X(L + EXT), Yz(zmin + 0.05) - 2 * f), "el talud sigue bajando hasta %.2f" % min(z for _, z in d["ext"]), 1.4, "TEXTOS", TA.TOP_RIGHT)
    dsc = d["dsc"]; sale = dsc.get("sale_a_m") or 0.5
    zsal = max(next((zz for dd, zz in d["ext"] if dd >= sale - 1e-6), ncfL - 0.05), zmin + 0.05)
    lam.poli([(X(L + 0.075), Yz(ncfL)), (X(L + sale), Yz(min(zsal, ncfL - 0.05)))], "DET-PERFILADO")
    lam.flecha((X(L + 0.25), Yz(ncfL + 0.12)), (X(L + min(EXT, sale + 1.0)), Yz(min(zsal, ncfL) + 0.05)), "FLUJO", tam_mm=3.5)
    # cotas y rotulos
    lam.llamada((X(L + 0.075), Yz(nctL + 0.30)), (X(L) + 26 * f, Yz(nctL + 0.30)), ["MURO DEL CERCO e = 0.15 (CORTADO)"], hmm=1.6)
    lam.llamada((X(L + 0.1), Yz(zc0 - 0.2)), (X(L) + 30 * f, max(Yz(zc1 - 0.15), Yz(zmin) + 10 * f)), ["CIMIENTO DEL CERCO BAJO EL PASE", "(dimensiones segun estructuras)"], hmm=1.6)
    lam.llamada((X(L + sale / 2), Yz((ncfL + zsal) / 2)), (X(L + EXT) + 6 * f, Yz(ncfL - 0.15)),
                ["PERFILADO DEL TERRENO NATURAL (sin obra)", "terreno bajo la C.F. a %.1f m del cerco" % sale], hmm=1.6)
    lam.llamada((X(L + EXT - 0.3), Yz(max(d["ext"][-2][1], zmin + 0.05))), (X(L + EXT) + 6 * f, Yz(ncfL + 0.35)), ["TERRENO NATURAL (curvas de nivel)"], hmm=1.6)
    lam.llamada((X(s_a + 0.8), Yz(seg[1][2] + d["y"] / 2)), (X(s_a + 0.8) + 10 * f, Yz(zfmin - 0.35)),
                ["AGUA DE DISENO: Q = %.1f l/s, tirante %.2f m" % (d["Q"], d["y"])], hmm=1.6)
    # secciones: inicio de la vista, empalmes, inicio de tapado y descarga
    est = [(s_a, "Viene de %s" % prog(s_a))]
    for ll in d["llegan"]: est.append((ll["s"], "Llega " + ll["eje"]))
    for a, b in tap:
        if a > s_a + 0.05: est.append((a, "Inicio de tapado"))
    est.append((L, "Descarga " + d["D"]))
    est.sort()
    ult = -1e9; ytope = 0.0
    for k, (s, nota) in enumerate(est):
        nct, ncf = _valor(P, s); xs = X(s)
        lam.linea((xs, Yz(nct)), (xs, Yz(ncf - EL)), "DET-SECCION")
        lam.linea((xs, lam.P(0, yg)[1]), (xs, lam.P(0, yg1)[1]), "GUITARRA")
        lin = ["NCT: %.2f" % nct, "NCF: %.3f" % ncf, " H: %.2f m" % (nct - ncf), nota]
        w = 30.0; alto = 2.4 + 3.6 * len(lin)
        xc = max(xs + 0, ult + (w + 3) * f); ult = xc
        yb = Yz(nct) + 0.62 + 6 * f
        lam.rect(xc - w / 2 * f, yb, xc + w / 2 * f, yb + alto * f, "PERF-CAJA")
        for i, t in enumerate(lin):
            lam.texto((xc - w / 2 * f + 1.3 * f, yb + (alto - 2.8 - 3.6 * i) * f), t, 1.4 if i < 3 else 1.15, "TEXTOS", TA.MIDDLE_LEFT)
        lam.flecha((xc, yb), (xs, Yz(nct)), "PERF-CAJA", tam_mm=2.0)
        ytope = max(ytope, (yb - lam.oy) / f + alto)
        for i, v in enumerate(["%.2f" % s, "%.2f" % nct, "%.3f" % ncf, "%.2f" % (nct - ncf)]):
            lam.texto((xs + 1.0 * f, lam.P(0, yg1 - (i + 0.5) * AF)[1]), v, 1.05, "TEXTOS", TA.MIDDLE_LEFT)
    for dd, zz in d["ext"]:
        if dd > 0.01 and abs(dd * 2 - round(dd * 2)) < 1e-6:
            xs = X(L + dd)
            lam.texto((xs + 1.0 * f, lam.P(0, yg1 - 4.5 * AF)[1]), "%.2f" % zz, 1.05, "TEXTOS", TA.MIDDLE_LEFT)
            lam.linea((xs, lam.P(0, yg)[1]), (xs, lam.P(0, yg + AF)[1]), "GUITARRA")
    # progresivas cada metro
    k = math.ceil(s_a)
    while k <= L - 0.4:
        lam.linea((X(k), lam.P(0, yg1)[1]), (X(k), lam.P(0, yg1 + 2)[1]), "GUITARRA")
        lam.texto((X(k), lam.P(0, yg1 + 3)[1]), "0+%06.2f" % k, 1.3, "TEXTOS", TA.BOTTOM_CENTER)
        k += 1
    lam.texto((X(L), lam.P(0, yg1 + 3)[1]), "CERCO 0+%06.2f" % L, 1.3, "TEXTOS", TA.BOTTOM_CENTER)
    for dd in range(1, int(EXT) + 1):
        lam.linea((X(L + dd), lam.P(0, yg1)[1]), (X(L + dd), lam.P(0, yg1 + 2)[1]), "GUITARRA")
        lam.texto((X(L + dd), lam.P(0, yg1 + 3)[1]), "+%.2f m" % dd, 1.3, "TEXTOS", TA.BOTTOM_CENTER)
    return ytope


def prog(s): return "0+%06.2f" % s


# ----------------------------------------------------------------------------- isometrico 1/25
class Iso:
    """Proyeccion isometrica con el eje x local en el sentido de salida del agua (hacia el observador, abajo a la derecha)."""
    C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))

    def __init__(self, origen, u):
        self.o, self.u, self.n = origen, u, _perp(u)
        self.cam = np.array([1.0, 1.0, 1.2]) / np.linalg.norm([1.0, 1.0, 1.2])

    def local(self, p):
        dx, dy = p[0] - self.o[0], p[1] - self.o[1]
        return (dx * self.u[0] + dy * self.u[1], -(dx * self.n[0] + dy * self.n[1]))

    def mundo(self, x, y):
        return (self.o[0] + self.u[0] * x - self.n[0] * y, self.o[1] + self.u[1] * x - self.n[1] * y)

    def P(self, x, y, z):
        return ((x - y) * self.C30, z - (x + y) * self.S30)

    def prof(self, pts3):
        return float(np.mean([self.cam[0] * p[0] + self.cam[1] * p[1] + self.cam[2] * (p[2] - 180.0) for p in pts3]))


def isometrico(lam, d, cx, cy):
    f = lam.f; k = ESC / ESC_ISO
    r = d["r"]; P = r["perfil"]; L, s_a = d["L"], d["s_a"]
    xd, yd = d["poly"][-1]; u = d["u"]
    iso = Iso((xd, yd), u)
    z0 = _valor(P, L)[0]
    loc = [iso.local(p) for p in d["cuneta"]]
    sl = _acum(d["cuneta"])
    caras = []                                 # (grupo, profundidad, capa, puntos3d)
    def cara(g, capa, pts):
        caras.append((g, iso.prof(pts), capa, pts))
    # piso interior nivelado y terreno exterior (fondo del dibujo)
    xs = [p[0] for p in loc]; ys = [p[1] for p in loc]
    xmin, ymin, ymax = min(xs) - 0.6, min(ys) - 0.9, max(ys) + 0.9
    cara(0, "ISOD-PISO", [(xmin, ymin, z0), (-0.075, ymin, z0), (-0.075, ymax, z0), (xmin, ymax, z0)])
    dsc = d["dsc"]; sale = dsc.get("sale_a_m") or 0.5; ncfL = _valor(P, L)[1]
    def zt(x, y):
        w = iso.mundo(x, y); z = d["z"](*w)
        if abs(y) < 0.35:                                  # perfilado frente a la salida
            zsal = d["z"](*iso.mundo(sale, 0.0))
            zp = ncfL + (min(zsal, ncfL - 0.05) - ncfL) * min(1.0, max(0.0, x) / max(sale, 0.1))
            z = min(z, zp)
        return z
    gx = np.arange(0.075, EXT_ISO + 0.01, 0.25); gy = np.arange(ymin, ymax + 0.01, 0.30)
    for i in range(len(gx) - 1):
        for j in range(len(gy) - 1):
            q = [(gx[i], gy[j]), (gx[i + 1], gy[j]), (gx[i + 1], gy[j + 1]), (gx[i], gy[j + 1])]
            cara(0, "ISOD-TERRENO", [(x, y, zt(x, y)) for x, y in q])
    # agua sobre el terreno exterior
    for i in range(len(gx) - 1):
        q = [(gx[i], -0.15), (gx[i + 1], -0.15), (gx[i + 1], 0.15), (gx[i], 0.15)]
        cara(0.5, "ISOD-AGUA", [(x, y, zt(x, 0.0) + 0.01) for x, y in q])
    # cuneta: fondo, agua, caras interiores visibles, coronas de muro, losa tapa
    tap = [(max(a, s_a) - s_a, (min(b, L) - s_a) if b < L - 0.01 else sl[-1]) for a, b in r["tapados"] if b > s_a]
    def es_tap(s): return any(a - 1e-6 <= s <= b + 1e-6 for a, b in tap)
    cort = sorted(set([round(x, 4) for x in sl] + [round(v, 4) for a, b in tap for v in (a, b)]))
    pts = [iso.local(_en(d["cuneta"], sl, s)[0]) for s in cort]
    zf = [_valor(P, min(s + s_a, L))[1] for s in cort]; zn = [_valor(P, min(s + s_a, L))[0] for s in cort]
    oI = {sg: offset(pts, sg * BI) for sg in (1, -1)}; oE = {sg: offset(pts, sg * BT) for sg in (1, -1)}
    for i in range(len(pts) - 1):
        sm = (cort[i] + cort[i + 1]) / 2
        a1, b1, a2, b2 = oI[1][i], oI[1][i + 1], oI[-1][i + 1], oI[-1][i]
        cara(1, "ISOD-FONDO", [(a1[0], a1[1], zf[i]), (b1[0], b1[1], zf[i + 1]), (a2[0], a2[1], zf[i + 1]), (b2[0], b2[1], zf[i])])
        cara(1, "ISOD-AGUA", [(a1[0], a1[1], zf[i] + d["y"]), (b1[0], b1[1], zf[i + 1] + d["y"]), (a2[0], a2[1], zf[i + 1] + d["y"]), (b2[0], b2[1], zf[i] + d["y"])])
        t = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]); Lt = math.hypot(*t); t = (t[0] / Lt, t[1] / Lt); nrm = _perp(t)
        for sg in (1, -1):
            hacia = (-sg * nrm[0], -sg * nrm[1])         # normal de la cara interior (hacia el centro del canal)
            if hacia[0] * iso.cam[0] + hacia[1] * iso.cam[1] > 0:
                p, q = oI[sg][i], oI[sg][i + 1]
                cara(1, "ISOD-INT", [(p[0], p[1], zf[i]), (q[0], q[1], zf[i + 1]), (q[0], q[1], zn[i + 1]), (p[0], p[1], zn[i])])
            p1, q1, q2, p2 = oI[sg][i], oI[sg][i + 1], oE[sg][i + 1], oE[sg][i]
            cara(2, "ISOD-SUP", [(p1[0], p1[1], zn[i]), (q1[0], q1[1], zn[i + 1]), (q2[0], q2[1], zn[i + 1]), (p2[0], p2[1], zn[i])])
        if es_tap(sm):
            e1, e2, e3, e4 = oE[1][i], oE[1][i + 1], oE[-1][i + 1], oE[-1][i]
            cara(3, "ISOD-LOSA", [(e1[0], e1[1], zn[i] + 0.001), (e2[0], e2[1], zn[i + 1] + 0.001), (e3[0], e3[1], zn[i + 1] + 0.001), (e4[0], e4[1], zn[i] + 0.001)])
    # cara de salida (vista desde afuera): concreto con el hueco del canal
    e1, e2 = oE[1][-1], oE[-1][-1]; i1, i2 = oI[1][-1], oI[-1][-1]
    zfL, znL = zf[-1], zn[-1]
    cara(4, "ISOD-SUP", [(e1[0], e1[1], zfL - EL), (e2[0], e2[1], zfL - EL), (e2[0], e2[1], znL), (e1[0], e1[1], znL)])
    techo = znL - (0.10 if es_tap(sl[-1] - 0.01) else 0.0)
    cara(4.1, "ISOD-HUECO", [(i1[0], i1[1], zfL), (i2[0], i2[1], zfL), (i2[0], i2[1], techo), (i1[0], i1[1], techo)])
    cara(4.2, "ISOD-AGUA", [(i1[0], i1[1], zfL), (i2[0], i2[1], zfL), (i2[0], i2[1], zfL + d["y"]), (i1[0], i1[1], zfL + d["y"])])
    # muro del cerco (tramo corto, cortado a 0.40 m) sobre el pase
    hm = 0.40; c0, c1 = ymin + 0.2, ymax - 0.2
    for q in ([(-0.075, c0), (0.075, c0), (0.075, c1), (-0.075, c1)],):
        cara(5, "ISOD-CERCO", [(x, y, z0 + hm) for x, y in q])
    cara(5, "ISOD-CERCO", [(0.075, c0, z0), (0.075, c1, z0), (0.075, c1, z0 + hm), (0.075, c0, z0 + hm)])
    cara(5, "ISOD-CERCO", [(-0.075, c1, z0), (0.075, c1, z0), (0.075, c1, z0 + hm), (-0.075, c1, z0 + hm)])
    # dibujo (de atras hacia adelante dentro de cada grupo)
    o = lam.P(cx, cy)
    W = lambda p3: (o[0] + k * iso.P(p3[0], p3[1], p3[2] - z0)[0], o[1] + k * iso.P(p3[0], p3[1], p3[2] - z0)[1])
    for g, pr, capa, p3 in sorted(caras, key=lambda c: (c[0], c[1])):
        q = [W(p) for p in p3]
        lam.relleno(q, capa); lam.poli(q, "ISOD-ARISTA", cerrada=True)
    # rejilla en los tramos abiertos y ejes que llegan (lineas sobre la corona)
    for i in range(len(pts) - 1):
        if es_tap((cort[i] + cort[i + 1]) / 2): continue
        a, b = cort[i], cort[i + 1]; s = a + 0.05
        while s < b:
            p, t = _en(d["cuneta"], sl, s); n = _perp(t)
            pa = iso.local((p[0] + n[0] * BI, p[1] + n[1] * BI)); pb = iso.local((p[0] - n[0] * BI, p[1] - n[1] * BI))
            zz = _valor(P, min(s + s_a, L))[0]
            lam.linea(W((pa[0], pa[1], zz)), W((pb[0], pb[1], zz)), "ISOD-REJILLA"); s += 0.10
    for ll in d["llegan"]:                      # eje que llega: corona y rejilla (solo trazo sobre el piso)
        pl = ll["poly"]; s2 = _acum(pl); zz = ll["r"]["perfil"][-1][1]
        for sg in (1, -1):
            lam.poli([W((*iso.local(p), zz)) for p in offset(pl, sg * BT)[:-1]], "CONCRETO")
            lam.poli([W((*iso.local(p), zz)) for p in offset(pl, sg * BI)[:-1]], "CONCRETO")
        s = 0.05
        while s < s2[-1] - 0.7:
            p, t = _en(pl, s2, s); n = _perp(t)
            lam.linea(W((*iso.local((p[0] + n[0] * BI, p[1] + n[1] * BI)), zz)), W((*iso.local((p[0] - n[0] * BI, p[1] - n[1] * BI)), zz)), "ISOD-REJILLA")
            s += 0.10
        pt = W((*iso.local(pl[0]), zz))
        lam.llamada(pt, (pt[0] - 22 * f, pt[1] + 14 * f), ["Llega " + ll["eje"]], hmm=1.8)
    # llamadas
    pt = W((*loc[0], _valor(P, s_a)[0])); lam.llamada(pt, (pt[0] - 30 * f, min(pt[1] + 26 * f, lam.P(0, 556)[1])), [r["codigo"] + " (rejilla en tramo abierto)"], hmm=1.8)
    pt = W((0.075, (c0 + c1) / 2 + 0.3, z0 + hm)); lam.llamada(pt, (pt[0] + 20 * f, pt[1] + 30 * f), ["MURO DEL CERCO (CORTADO)", "pase de la cuneta bajo el cerco"], hmm=1.8)
    pt = W(((e1[0] + e2[0]) / 2, (e1[1] + e2[1]) / 2, zfL)); lam.llamada(pt, (pt[0] + 34 * f, pt[1] - 6 * f), ["SALIDA %s: C.F. %.3f" % (d["D"], dsc["cf"])], hmm=1.8)
    pt = W((1.6, 0.0, zt(1.6, 0.0))); lam.llamada(pt, (pt[0] + 18 * f, pt[1] - 26 * f), ["AGUA SOBRE EL TERRENO NATURAL", "(perfilado %.1f m, sin obra)" % sale], hmm=1.8)
    if tap:
        a, b = tap[-1]; p = iso.local(_en(d["cuneta"], sl, (a + b) / 2)[0]); pt = W((p[0], p[1], _valor(P, L)[0]))
        lam.llamada(pt, (pt[0] - 40 * f, pt[1] - 30 * f), ["LOSA TAPA e = 0.10 m"], hmm=1.8)


# ----------------------------------------------------------------------------- laminas
def _nota_salida(d):
    """Nota propia de cada descarga segun el terreno de afuera (talud o perfilado)."""
    zt = [z for _, z in d["ext"]]
    if not zt: return []
    cf = d["dsc"]["cf"]; caida = cf - min(zt)
    if caida > 1.0:
        return ["6. Afuera el terreno baja %.1f m en talud (hasta %.2f): se recomienda proteger la entrega al pie del cerco contra la erosion "
                "(emboquillado de piedra), a definir con el propietario del terreno exterior." % (caida, min(zt))]
    if zt[0] > cf - 0.02:
        return ["6. El terreno al pie del cerco esta a %.2f: perfilar %.2f m en los primeros %.1f m para que el agua salga libre." % (zt[0], zt[0] - cf + 0.05, 0.5)]
    return []


def laminas(doc, R, V, ox, oy, sep, num0, pref, sitio, terreno, curvas, anchos, P, tapas, niveles):
    """Una lamina 1/25 por descarga. R: red con cotas; anchos {(eje, de, a): b}; tapas: planta_lamina.tapas_de."""
    global BI, BT
    capas(doc)
    DS.CERCO = [tuple(p) for p in list(sitio.cerco.exterior.coords)[:-1]]
    DS.DESCARGAS = sorted({r["nudos"][-1] for r in R["ramales"] if r["nudos"][-1].startswith("D")})
    DS.TAPAS = tapas; DS._z = terreno.z
    DS._curvas = [(zc, list(L.coords)) for zc, L in curvas]
    DS.NIVELES = niveles
    out = []
    for i, D in enumerate(DS.DESCARGAS):
        r = next(x for x in R["ramales"] if x["nudos"][-1] == D); t0 = r["tramos"][0]
        b = anchos.get((r["codigo"], t0["de"], t0["a"]), P["b_int"]); BI, BT = b / 2, b / 2 + P["e_muro"]
        d = datos(R, V, D)
        for ll in d["llegan"]:
            t2 = ll["r"]["tramos"][0]; ll["b"] = anchos.get((ll["eje"], t2["de"], t2["a"]), b)
        lam = B.Lamina(doc, ox + i * sep, oy, ESC, "%s-%02d" % (pref, num0 + i), "DETALLE DE LA DESCARGA %s POR EL CERCO" % D,
                       "PLANTA, PERFIL LONGITUDINAL E ISOMETRICO - ESC. 1/%d (ESCALA REAL)" % ESC)
        dp, di = _planta_que_entra(d), _recorte(d, LISO, 1.5)
        lam.titulo_vista(220, 578, "PLANTA DE LA DESCARGA %s" % D, "ESC. 1/%d - ultimos %.1f m del %s" % (ESC_PL, dp["L"] - dp["s_a"], d["r"]["codigo"]), 150)
        planta(lam, dp, (PL_VENT[0] + PL_VENT[2]) / 2, (PL_VENT[1] + PL_VENT[3] - 15) / 2)
        lam.titulo_vista(630, 578, "ISOMETRICO DE LA DESCARGA %s" % D, "ESC. 1/%d - vista desde afuera del cerco" % ESC_ISO, 150)
        isometrico(lam, di, 640, 455)
        yt = perfil(lam, d, 30, 128)
        lam.titulo_vista(330, yt + 12, "PERFIL LONGITUDINAL DE LA DESCARGA %s" % D, "ESC. H = V = 1/%d - por el eje del %s" % (ESC, d["r"]["codigo"]), 170)
        lam.notas(30, 100, "NOTAS", [
            "1. Interior del cerco: " + (DS.NIVELES or "borde de cuneta al ras del piso terminado") + ".",
            "2. La cuneta cruza el cerco tapada (losa e = 0.10 m) y entrega al terreno natural; fuera del cerco no se construye, solo se perfila el terreno.",
            "3. Quiebres a 45 grados en planta en cada cambio de direccion; los ejes que llegan entran en diagonal.",
            "4. Cimiento del cerco: se mantiene bajo el pase de la cuneta (dimensiones y refuerzo segun el proyecto de estructuras).",
            "5. Cotas en m s. n. m.; NCT = borde de cuneta, NCF = cota de fondo, H = NCT - NCF."] + _nota_salida(d), hmm=1.6, ancho_mm=590)
        out.append(lam)
    return out
