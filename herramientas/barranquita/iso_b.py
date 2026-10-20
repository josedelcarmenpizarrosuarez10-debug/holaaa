"""Isometricos de la red de cunetas - I.E. N.° 0590, Barranquita (DC-07 vista desde el sur-oeste, DC-08 desde el nor-este).

Escala real (sin exageracion vertical): terreno terminado (plataforma +184.50 dentro del cerco, curvas C-TOPO fuera),
bloques con techo a dos aguas (cumbrera en el eje largo), cunetas con el color de su sistema, tramos tapados, gradas y
descargas con la flecha del agua hasta el terreno natural. Lo usa planos_b.py.
"""
import os, sys, math
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI); sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "techo"))
import dxf_base as B
from ezdxf.enums import TextEntityAlignment as TA
from matplotlib.path import Path
import iso3d
import terreno_b as T
import diseno_b as DS

XC, YC, ZC = 354897.0, 9249832.0, 180.0
CAJA = (354800.0, 9249772.0, 354992.0, 9249892.0)
RGB_SIS = {1: (40, 90, 225), 2: (215, 45, 200), 3: (25, 150, 60), 4: (245, 140, 20)}
RGB_TAP, RGB_GRAD, RGB_AGUA = (150, 150, 150), (225, 30, 30), (40, 120, 230)
RGB_TERR, RGB_PLAT, RGB_MURO, RGB_TECHO = (196, 214, 170), (226, 222, 210), (238, 234, 226), (190, 92, 70)
NPT, H_ALERO, H_CUMB = 184.65, 3.00, 1.10
NOM = {1: "SISTEMA 1 - OESTE", 2: "SISTEMA 2 - FRENTE SUR", 3: "SISTEMA 3 - NOR-ESTE", 4: "SISTEMA 4 - INGRESO SUR-ESTE"}


def bloques(G):
    """Contornos de techo (0_PROYECCIONES 1) cerrados y de mas de 30 m2, uno por bloque (el mayor de cada par)."""
    out = []
    for pts, cl, b in G["geo"]["0_PROYECCIONES 1"]:
        q = [(p[0], p[1]) for p in pts]
        if len(q) > 2 and math.dist(q[0], q[-1]) < 0.05: q = q[:-1]; cl = True
        if not cl or len(q) < 4: continue
        A = abs(sum(q[i][0] * q[i + 1][1] - q[i + 1][0] * q[i][1] for i in range(-1, len(q) - 1))) / 2
        if A < 30: continue
        c = (sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q))
        dup = [o for o in out if math.dist(o[1], c) < 1.5]
        if dup:
            if A > dup[0][2]: out.remove(dup[0])
            else: continue
        out.append((q, c, A, b))
    return out


class Vista:
    """giro en grados: el observador mira desde el azimut 45 - giro (157.5: desde el sur-suroeste; -22.5: desde el nor-noreste).
    Se evita 0 y 45 grados para que los bloques ortogonales y los pabellones a 45 grados no queden de canto."""
    def __init__(self, giro):
        self.c, self.s = math.cos(math.radians(giro)), math.sin(math.radians(giro))

    def L(self, x, y, z):
        dx, dy = x - XC, y - YC
        u, v = dx * self.c - dy * self.s, dx * self.s + dy * self.c
        return (v, u, z - ZC)          # iso3d.proj dibuja en espejo (x a la derecha mirando desde +x+y): se intercambian ejes


def isometrico(doc, R, V, ox, oy, codigo, giro, titulo, sub):
    lam = B.Lamina(doc, ox, oy, 350, codigo, titulo, sub, escala_txt="1/350 (H = V)")
    G = T.cargar(); ras = DS.rasante_fn(); vis = Vista(giro); L = vis.L
    E = iso3d.Escena(); ce = Path(DS.CERCO)
    # --- terreno terminado (malla de 2 m)
    x0, y0, x1, y1 = CAJA; paso = 2.0
    xs = np.arange(x0, x1 + 0.1, paso); ys = np.arange(y0, y1 + 0.1, paso)
    Z = np.array([[ras(x, y) for x in xs] for y in ys])
    E.g = 0
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            zz = [Z[j, i], Z[j, i + 1], Z[j + 1, i + 1], Z[j + 1, i]]
            if not all(np.isfinite(zz)): continue
            xy = [(xs[i], ys[j]), (xs[i + 1], ys[j]), (xs[i + 1], ys[j + 1]), (xs[i], ys[j + 1])]
            dentro = ce.contains_point(((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2))
            E.cara([L(p[0], p[1], z) for p, z in zip(xy, zz)], RGB_PLAT if dentro else RGB_TERR, bordes=[False] * 4)
    # --- cunetas (banda de 0.60 sobre la rasante, color del sistema; tapados en gris; gradas en rojo)
    E.g = 1
    nom = R["nombre"]; grad = {(f["ramal"], f["de"], f["a"]) for f in V["hidraulica"] if f["vel"] != "CUMPLE"}
    for r in R["ramales"]:
        xy = [tuple(R["nudos"][n]) for n in r["nudos"]]; P = r["perfil"]
        tramos = []; acc = 0.0
        for t in r["tramos"]:
            tramos.append((acc, acc + t["L"], (r["codigo"], nom[t["de"]], nom[t["a"]]) in grad)); acc += t["L"]
        def pos(s):
            a = 0.0
            for i in range(len(xy) - 1):
                Lg = math.dist(xy[i], xy[i + 1])
                if a + Lg >= s - 1e-9 or i == len(xy) - 2:
                    t = 0 if Lg == 0 else min(1, (s - a) / Lg); u = ((xy[i + 1][0] - xy[i][0]) / Lg, (xy[i + 1][1] - xy[i][1]) / Lg)
                    return (xy[i][0] + t * (xy[i + 1][0] - xy[i][0]), xy[i][1] + t * (xy[i + 1][1] - xy[i][1])), u
                a += Lg
        for k in range(0, len(P) - 1, 2):
            s0, s1 = P[k][0], P[min(k + 2, len(P) - 1)][0]
            if s1 - s0 < 0.05: continue
            (pa, ua), (pb, ub) = pos(s0), pos(s1)
            za, zb = P[k][1] + 0.03, P[min(k + 2, len(P) - 1)][1] + 0.03
            sm = (s0 + s1) / 2
            col = RGB_SIS[r["sistema"]]
            if any(a <= sm <= b for a, b in r["tapados"]): col = RGB_TAP
            if any(a <= sm <= b and g for a, b, g in tramos): col = RGB_GRAD
            w = DS.B_TOT / 2
            E.cara([L(pa[0] - ua[1] * w, pa[1] + ua[0] * w, za), L(pb[0] - ub[1] * w, pb[1] + ub[0] * w, zb),
                    L(pb[0] + ub[1] * w, pb[1] - ub[0] * w, zb), L(pa[0] + ua[1] * w, pa[1] - ua[0] * w, za)], col, bordes=[False] * 4)
    # --- descargas: canal de salida y flecha del agua sobre el terreno
    zt = T.modelo(); flechas = []
    for d in V["descargas"]:
        D = d["D"]; x, y = R["nudos"][D]
        u = {"D2": (-0.7071, 0.7071), "D3": (0.0, -1.0), "D4": (-0.7071, -0.7071)}.get(D)
        if u is None:
            rr = next(r for r in R["ramales"] if r["nudos"][-1] == D); a = R["nudos"][rr["nudos"][-2]]; Lg = math.dist(a, (x, y))
            u = ((x - a[0]) / Lg, (y - a[1]) / Lg)
        pts = []
        for k in range(0, 21):
            dd = 0.6 * k; px, py = x + u[0] * dd, y + u[1] * dd; z = zt(px, py)
            if not np.isfinite(z): break
            pts.append((px, py, z + 0.08))
        flechas.append((D, pts))
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]; w = 0.45
            E.cara([L(a[0] - u[1] * w, a[1] + u[0] * w, a[2]), L(b[0] - u[1] * w, b[1] + u[0] * w, b[2]),
                    L(b[0] + u[1] * w, b[1] - u[0] * w, b[2]), L(a[0] + u[1] * w, a[1] - u[0] * w, a[2])], RGB_AGUA, bordes=[False] * 4)
    # --- bloques con techo a dos aguas
    E.g = 2
    for q, c, A, nombre in bloques(G):
        z0, z1 = DS.NTN_PLAT, NPT + H_ALERO
        n = len(q)
        for i in range(n):
            a, b = q[i], q[(i + 1) % n]
            E.quad(L(a[0], a[1], z0), L(b[0], b[1], z0), L(b[0], b[1], z1), L(a[0], a[1], z1), RGB_MURO, paso=2.0)
        if n == 4:
            l01, l12 = math.dist(q[0], q[1]), math.dist(q[1], q[2])
            if l01 >= l12: a0, a1, b0, b1 = q[0], q[1], q[3], q[2]          # cumbrera paralela a q0-q1
            else: a0, a1, b0, b1 = q[1], q[2], q[0], q[3]
            m0 = ((a0[0] + b0[0]) / 2, (a0[1] + b0[1]) / 2); m1 = ((a1[0] + b1[0]) / 2, (a1[1] + b1[1]) / 2); zc = z1 + H_CUMB
            E.quad(L(*a0, z1), L(*a1, z1), L(*m1, zc), L(*m0, zc), RGB_TECHO, paso=2.0)
            E.quad(L(*b0, z1), L(*b1, z1), L(*m1, zc), L(*m0, zc), RGB_TECHO, paso=2.0)
            E.cara([L(*a0, z1), L(*b0, z1), L(*m0, zc)], RGB_MURO); E.cara([L(*a1, z1), L(*b1, z1), L(*m1, zc)], RGB_MURO)
        else:
            E.cara([L(p[0], p[1], z1) for p in q], RGB_TECHO)
    P2 = E.dibujar(lam, 420, 300, capa_rel="ISO-CONCRETO-SUP", capa_ar="ISO-ARISTAS", color_ar=8)
    # --- rotulos: descargas y sistemas
    for D, pts in flechas:
        if len(pts) < 2: continue
        a, b = pts[-2], pts[-1]; pa, pb = P2(L(*a)), P2(L(*b))
        lam.flecha(pa, pb, "DESCARGA", tam_mm=5.0)
        dd = next(d for d in V["descargas"] if d["D"] == D)
        txt = ["%s  C.F. %.3f" % (D, dd["cf"]), ("sale al terreno a %.1f m" % dd["sale_a_m"]) if dd["sale_a_m"] is not None else "al punto bajo del Jr. Alfonso Ugarte"]
        p0 = P2(L(*pts[0]))
        lam.llamada(p0, (p0[0] + 14 * lam.f, p0[1] + 22 * lam.f), txt, hmm=2.4)
    for k in (1, 2, 3, 4):
        rr = [r for r in R["ramales"] if r["sistema"] == k]
        pts = [R["nudos"][n] for r in rr for n in r["nudos"]]
        c = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
        pc = P2(L(c[0], c[1], 186.5))
        lam.texto(pc, NOM[k], 3.0, "TITULOS", TA.MIDDLE_CENTER, color={1: 5, 2: 6, 3: 94, 4: 30}[k])
    # rosa de orientacion
    o = lam.P(770, 520)
    for ang, t in ((0, "E"), (90, "N")):
        dx, dy = math.cos(math.radians(ang)) * 12, math.sin(math.radians(ang)) * 12
        a, b = P2(L(XC, YC, ZC)), P2(L(XC + dx, YC + dy, ZC))
        v = (b[0] - a[0], b[1] - a[1]); q = (o[0] + v[0], o[1] + v[1])
        lam.flecha(o, q, "TEXTOS", tam_mm=3.0); lam.texto((q[0] + v[0] * 0.25, q[1] + v[1] * 0.25), t, 3.0, "TITULOS", TA.MIDDLE_CENTER)
    items = [("relleno", "ISO-S%d" % k, NOM[k]) for k in (1, 2, 3, 4)] + [("relleno", "ISO-TAP", "Tramo tapado (losa)"), ("relleno", "ISO-GRAD", "Gradas (pendiente fuerte)"),
             ("relleno", "ISO-AGUA-D", "Descarga: agua hacia el terreno natural"), ("relleno", "ISO-PLAT", "Plataforma (NTN +184.50) dentro del cerco"),
             ("relleno", "ISO-TERR", "Terreno natural (curvas C-TOPO)"), ("relleno", "ISO-TECHO", "Techos a dos aguas (bloques, NPT +184.65)")]
    lam.leyenda2(30, 575, items, hmm=1.8)
    lam.notas(30, 120, "NOTAS", ["1. Isometrico a escala real 1/350, sin exageracion vertical; coordenadas y cotas del plano PLANTA_GENERAL_590_2.",
                                 "2. Las cunetas (0.60 m) se dibujan como banda sobre la rasante; cotas de fondo y profundidades en DC-02 y perfiles.",
                                 "3. Altura de bloques referencial: alero a 3.00 m sobre el NPT y cumbrera 1.10 m mas arriba."], hmm=1.6, ancho_mm=330)
    return lam


def capas_iso(doc):
    for n, rgb in (("ISO-S1", RGB_SIS[1]), ("ISO-S2", RGB_SIS[2]), ("ISO-S3", RGB_SIS[3]), ("ISO-S4", RGB_SIS[4]), ("ISO-TAP", RGB_TAP),
                   ("ISO-GRAD", RGB_GRAD), ("ISO-AGUA-D", RGB_AGUA), ("ISO-PLAT", RGB_PLAT), ("ISO-TERR", RGB_TERR), ("ISO-TECHO", RGB_TECHO)):
        if n not in doc.layers:
            ly = doc.layers.add(n, color=7); ly.rgb = rgb
        B.COLOR_RGB[n] = rgb
