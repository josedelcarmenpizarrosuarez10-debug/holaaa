"""Isometricos 3D de la red de cunetas - I.E. N.° 0590, Barranquita.

Solo las cunetas, sobre todo el terreno y todas las veredas (sin edificaciones): vista desde el sur y vista desde el norte
(escala 1/350) y detalle de las tres descargas por el cerco (escala 1/75); codigos de lamina correlativos (planos_b.py). Escala real, sin exageracion vertical.
- Terreno: dentro del cerco la rasante de diseno (plataforma +184.50 y, donde el terreno natural es mas bajo, el terreno
  natural); fuera del cerco el terreno natural del modelo de curvas C-TOPO. Curvas de nivel cada 0.50 m sobre el terreno.
- Veredas del plano (capa 0_VEREDAS) 0.10 m sobre la rasante.
- Cunetas: canal de 0.40 x h con muros de 0.10 (corona con el color de su sistema), fondo a la cota de fondo de diseno,
  tramos tapados con losa gris, gradas en rojo, rejillas (solo en el detalle) y la poza de salida de D2.
- Cerco perimetrico (limite de intervencion) como sardinel rojo con el pase de cada descarga; fuera del cerco solo el agua.
Lo usa planos_b.py.
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

XC, YC, ZC = 354895.0, 9249832.0, 182.0
CAJA = (354801.0, 9249772.0, 354990.0, 9249896.0)        # cerco + ~12 m de terreno exterior
RGB_SIS = {1: (40, 90, 225), 2: (215, 45, 200), 3: (25, 150, 60)}
RGB = {"ISO-S1": RGB_SIS[1], "ISO-S2": RGB_SIS[2], "ISO-S3": RGB_SIS[3], "ISO-TAP": (150, 150, 150), "ISO-GRAD": (225, 30, 30),
       "ISO-FONDO": (110, 110, 110), "ISO-MURO-INT": (200, 196, 188), "ISO-REJ": (60, 60, 60), "ISO-AGUA-D": (40, 120, 230),
       "ISO-PLAT": (226, 222, 210), "ISO-TERR": (196, 214, 170), "ISO-VER": (248, 248, 246), "ISO-CERCO": (200, 30, 30),
       "ISO-POZA": (175, 175, 175), "ISO-CURVAS": (150, 120, 85), "ISO-VER-BORDE": (120, 120, 120)}
NOM = {1: "SISTEMA 1 - OESTE (D1)", 2: "SISTEMA 2 - FRENTE SUR (D3)", 3: "SISTEMA 3 - NOR-ESTE (D2)"}
COL_TXT = {1: 5, 2: 6, 3: 94}
H_VER, H_CERCO, E_CERCO = 0.10, 0.30, 0.15
COD_DET = "DC-10"                                          # lamina del detalle de descargas (la fija planos_b.py)


class EnBloque:
    """Lo que se dibuja dentro del with va a un bloque de AutoCAD (coordenadas reales) insertado en (0, 0)."""
    def __init__(self, lam, nombre, capa="0"): self.lam, self.nombre, self.capa = lam, nombre, capa

    def __enter__(self):
        self.prev = self.lam.msp; self.lam.msp = self.lam.doc.blocks.new(self.nombre); return self

    def __exit__(self, *a):
        self.lam.msp = self.prev; self.prev.add_blockref(self.nombre, (0, 0), dxfattribs={"layer": self.capa})


def c(capa):
    """Color de cara con su capa (r, g, b, capa): el dibujo pone cada solido en la capa de lo que representa."""
    return RGB[capa] + (capa,)


class Vista:
    """giro en grados: el observador mira desde el angulo 45 - giro (157.5: desde el sur-suroeste; -22.5: desde el
    nor-noreste). (xc, yc, zc): punto del terreno que va al origen del dibujo."""
    def __init__(self, giro, xc=XC, yc=YC, zc=ZC):
        self.c, self.s = math.cos(math.radians(giro)), math.sin(math.radians(giro)); self.o = (xc, yc, zc)

    def L(self, x, y, z):
        dx, dy = x - self.o[0], y - self.o[1]
        u, v = dx * self.c - dy * self.s, dx * self.s + dy * self.c
        return (v, u, z - self.o[2])   # iso3d.proy dibuja en espejo: se intercambian ejes para que la planta no salga invertida

    def ve(self, p_mundo, n_mundo):
        """True si la cara con normal n_mundo (hacia afuera de la cara visible) mira al observador."""
        a = np.array(self.L(*p_mundo)); b = np.array(self.L(p_mundo[0] + n_mundo[0], p_mundo[1] + n_mundo[1], p_mundo[2] + n_mundo[2]))
        return float((b - a) @ iso3d.VISTA) > 1e-9


def dibujar(E, lam, xmm, ymm, capa_ar="ISO-ARISTAS", color_ar=8):
    """Igual que iso3d.Escena.dibujar (pintor con sombreado), pero cada cara va a su capa (4.o elemento del color)."""
    O = lam.P(xmm, ymm); msp = lam.msp
    P2 = lambda p: (O[0] + iso3d.proy(p)[0], O[1] + iso3d.proy(p)[1])
    orden = sorted(E.caras, key=lambda f: (f[5], float(sum(p.sum() for p in f[0]) / len(f[0])) + f[3]))
    for pts, rgb, bordes, _, relleno, _g in orden:
        capa = rgb[3]
        if relleno and len(pts) >= 3:
            n = np.cross(pts[1] - pts[0], pts[2] - pts[0]); nn = np.linalg.norm(n); k = 1.0
            if nn > 1e-12:
                n = n / nn
                if n @ iso3d.VISTA < 0: n = -n
                k = 0.62 + 0.38 * max(0.0, float(n @ iso3d.LUZ))
            col = tuple(int(max(0, min(255, v * k))) for v in rgb[:3])
            q = [P2(p) for p in pts]
            tris = [(q[0], q[1], q[3], q[2])] if len(q) == 4 else [(q[0], q[i], q[i + 1]) for i in range(1, len(q) - 1)]
            for tr in tris:
                e = msp.add_solid(list(tr), dxfattribs={"layer": capa}); e.rgb = col
        for i, bd in enumerate(bordes):
            if bd and (len(pts) > 2 or i == 0):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                at = {"layer": capa_ar, "color": color_ar} if relleno else {"layer": capa}
                msp.add_line(P2(a), P2(b), dxfattribs=at)
    return P2


def triangular(q):
    """Triangulacion de un poligono simple (recorte de orejas)."""
    q = [tuple(p) for p in q]
    if len(q) > 3 and math.dist(q[0], q[-1]) < 1e-6: q = q[:-1]
    A = sum(q[i][0] * q[(i + 1) % len(q)][1] - q[(i + 1) % len(q)][0] * q[i][1] for i in range(len(q)))
    if A < 0: q = q[::-1]
    idx = list(range(len(q))); out = []
    cr = lambda a, b, p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    guard = 0
    while len(idx) > 3 and guard < 5000:
        guard += 1; hecho = False
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, p = q[i0], q[i1], q[i2]
            if cr(a, b, p) <= 1e-12: continue
            if any(j not in (i0, i1, i2) and cr(a, b, q[j]) >= 0 and cr(b, p, q[j]) >= 0 and cr(p, a, q[j]) >= 0 for j in idx): continue
            out.append((a, b, p)); idx.pop(k); hecho = True; break
        if not hecho: break
    if len(idx) == 3: out.append(tuple(q[i] for i in idx))
    return out


# ----------------------------------------------------------------------------- geometria de cada ramal
def geometria(R, V):
    """Por ramal: polilinea, perfil (s, rasante, fondo), tapados, gradas, aberturas por empalmes y recortes de extremos."""
    nom = R["nombre"]; grad = {(f["ramal"], f["de"], f["a"]) for f in V["hidraulica"] if f["vel"] != "CUMPLE"}
    ram = {r["codigo"]: r for r in R["ramales"]}
    G = {}
    for r in R["ramales"]:
        xy = [tuple(R["nudos"][n]) for n in r["nudos"]]
        sn = [0.0]
        for i in range(len(xy) - 1): sn.append(sn[-1] + math.dist(xy[i], xy[i + 1]))
        P = np.array(r["perfil"]); acc = 0.0; gr = []
        for t in r["tramos"]:
            if (r["codigo"], nom[t["de"]], nom[t["a"]]) in grad: gr.append((acc, acc + t["L"]))
            acc += t["L"]
        G[r["codigo"]] = {"r": r, "xy": xy, "sn": sn, "P": P, "tap": [tuple(t) for t in r["tapados"]], "grad": gr, "aber": [], "fin": sn[-1]}
    w = DS.B_TOT / 2
    for c_, g in G.items():                      # empalme: el ramal termina en la cara del muro del que lo recibe y este se abre
        fin = g["r"]["nudos"][-1]
        for c2, g2 in G.items():
            if c2 == c_ or fin not in g2["r"]["nudos"][1:]: continue
            k = g2["r"]["nudos"].index(fin); s2 = g2["sn"][k]
            p, u = pos(g2, s2 - 0.01)
            a = g["xy"][-2]; lado = 1 if (u[0] * (a[1] - p[1]) - u[1] * (a[0] - p[0])) > 0 else -1
            b = g["xy"][-1]; ua = ((b[0] - a[0]), (b[1] - a[1])); La = math.hypot(*ua); ua = (ua[0] / La, ua[1] / La)
            seno = abs(u[0] * ua[1] - u[1] * ua[0]) or 1.0
            g["fin"] = g["sn"][-1] - w / seno
            g2["aber"].append((s2 - DS.B_INT / 2 / seno, s2 + DS.B_INT / 2 / seno, lado))
    return G


def pos(g, s):
    """Punto del eje y direccion a la distancia s (en un nudo intermedio: direccion de la bisectriz)."""
    xy, sn = g["xy"], g["sn"]
    for i in range(len(xy) - 1):
        if s <= sn[i + 1] + 1e-9 or i == len(xy) - 2:
            L = sn[i + 1] - sn[i]; t = 0 if L == 0 else (s - sn[i]) / L
            u = ((xy[i + 1][0] - xy[i][0]) / L, (xy[i + 1][1] - xy[i][1]) / L)
            return (xy[i][0] + t * (xy[i + 1][0] - xy[i][0]), xy[i][1] + t * (xy[i + 1][1] - xy[i][1])), u


def lado(g, s, d):
    """Punto a la distancia d a la izquierda del eje (d < 0: derecha), con inglete en los quiebres."""
    xy, sn = g["xy"], g["sn"]
    for i in range(1, len(xy) - 1):
        if abs(s - sn[i]) < 1e-6:
            a, b, c_ = xy[i - 1], xy[i], xy[i + 1]
            u1 = np.subtract(b, a) / math.dist(a, b); u2 = np.subtract(c_, b) / math.dist(b, c_)
            n1 = np.array([-u1[1], u1[0]]); n2 = np.array([-u2[1], u2[0]]); nb = n1 + n2
            if np.linalg.norm(nb) < 1e-6: nb = n1
            nb = nb / np.linalg.norm(nb); k = 1.0 / max(0.3, float(nb @ n1))
            return (b[0] + nb[0] * d * k, b[1] + nb[1] * d * k)
    p, u = pos(g, s)
    return (p[0] - u[1] * d, p[1] + u[0] * d)


def rf(g, s):
    P = g["P"]
    return float(np.interp(s, P[:, 0], P[:, 1])), float(np.interp(s, P[:, 0], P[:, 2]))


def cunetas(E, R, V, vis, caja=None, paso=1.0, detalle=False):
    """Cunetas en 3D: fondo, muros interiores, coronas, tapados, gradas y (en detalle) rejillas."""
    L = vis.L; G = geometria(R, V); wi, wt = DS.B_INT / 2, DS.B_TOT / 2
    def en_caja(p):
        return caja is None or (caja[0] <= p[0] <= caja[2] and caja[1] <= p[1] <= caja[3])
    for cod, g in G.items():
        sis = g["r"]["sistema"]; col = c("ISO-S%d" % sis); fin = g["fin"]
        c_fondo = c("ISO-FONDO") if detalle else tuple(int(v * 0.55) for v in RGB_SIS[sis]) + ("ISO-S%d" % sis,)
        c_muro = c("ISO-MURO-INT") if detalle else tuple(int(v + (255 - v) * 0.45) for v in RGB_SIS[sis]) + ("ISO-S%d" % sis,)
        cortes = set(np.arange(0.0, fin, paso).tolist()) | set(s for s in g["sn"] if s < fin) | {fin}
        for a, b in g["tap"] + g["grad"]: cortes |= {a, b}
        for a, b, _ in g["aber"]: cortes |= {a, b}
        es_poza = g["r"]["nudos"][-1] in DS.POZA
        if es_poza: s_poza = fin - DS.POZA_DIM[1]; cortes.add(s_poza)
        ss = sorted(x for x in cortes if 0 <= x <= fin)
        ss = [x for i, x in enumerate(ss) if i == 0 or x - ss[i - 1] > 1e-3]
        for i in range(len(ss) - 1):
            s0, s1 = ss[i], ss[i + 1]; sm = (s0 + s1) / 2
            if not (en_caja(pos(g, s0)[0]) and en_caja(pos(g, s1)[0])): continue
            (r0, f0), (r1, f1) = rf(g, s0), rf(g, s1)
            tap = any(a - 1e-6 <= sm <= b + 1e-6 for a, b in g["tap"]); gra = any(a <= sm <= b for a, b in g["grad"])
            poza = es_poza and sm > s_poza
            wl = DS.POZA_DIM[0] / 2 if poza else wi
            if poza: f0 = f1 = rf(g, fin)[1]                 # fondo de la poza horizontal a la cota de fondo de llegada
            Pt = lambda s, d, z: L(*lado(g, s, d), z)
            # fondo (en gradas: escalones de 0.15 m); bajo la losa de un tapado no se ve nada
            if tap and detalle and not poza: pass
            elif gra and detalle:
                n = max(1, int(round((f0 - f1) / 0.15)))
                for k in range(n):
                    za = f0 - (f0 - f1) * k / n; sa = s0 + (s1 - s0) * k / n; sb = s0 + (s1 - s0) * (k + 1) / n
                    E.cara([Pt(sa, wl, za), Pt(sb, wl, za), Pt(sb, -wl, za), Pt(sa, -wl, za)], c("ISO-GRAD"), bordes=[False, True, False, True])
                    zb = f0 - (f0 - f1) * (k + 1) / n
                    E.cara([Pt(sb, wl, za), Pt(sb, -wl, za), Pt(sb, -wl, zb), Pt(sb, wl, zb)], c("ISO-GRAD"))
            else:
                E.cara([Pt(s0, wl, f0), Pt(s1, wl, f1), Pt(s1, -wl, f1), Pt(s0, -wl, f0)], c("ISO-GRAD") if gra else c_fondo,
                       bordes=[False] * 4)
            # muros interiores: solo la cara que mira al observador (la otra queda detras del canal)
            for sg in (1, -1):
                if any(a - 1e-6 <= sm <= b + 1e-6 and ld == sg for a, b, ld in g["aber"]): continue
                if tap and detalle and not poza: continue
                p0 = lado(g, s0, sg * wl); p1 = lado(g, s1, sg * wl); pc = lado(g, sm, 0)
                pm = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
                if vis.ve((pm[0], pm[1], (r0 + f0) / 2), (pc[0] - pm[0], pc[1] - pm[1], 0)):
                    E.cara([Pt(s0, sg * wl, f0), Pt(s1, sg * wl, f1), Pt(s1, sg * wl, r1), Pt(s0, sg * wl, r0)], c_muro,
                           bordes=[False, False, True, False])
                if not tap:
                    E.cara([Pt(s0, sg * wl, r0), Pt(s1, sg * wl, r1), Pt(s1, sg * (wl + 0.10), r1), Pt(s0, sg * (wl + 0.10), r0)],
                           c("ISO-POZA") if poza else (c("ISO-GRAD") if gra and not detalle else col), bordes=[True, False, True, False])
            if tap and not poza:
                E.cara([Pt(s0, wt, r0 + 0.01), Pt(s1, wt, r1 + 0.01), Pt(s1, -wt, r1 + 0.01), Pt(s0, -wt, r0 + 0.01)], c("ISO-TAP"),
                       bordes=[True, False, True, False], sesgo=0.05)
            elif detalle:                                # rejilla: platinas transversales cada 0.10 m (tambien sobre la poza)
                s = s0 + 0.05
                while s < s1:
                    rr = rf(g, s)[0]
                    E.cara([Pt(s - 0.0125, wl, rr), Pt(s + 0.0125, wl, rr), Pt(s + 0.0125, -wl, rr), Pt(s - 0.0125, -wl, rr)], c("ISO-REJ"),
                           bordes=[False] * 4, sesgo=0.02)
                    s += 0.10
            if poza:                                     # espejo de agua de la poza hasta el nivel de rebalse
                zr = r1 - 0.03
                E.cara([Pt(s0, wl, zr), Pt(s1, wl, zr), Pt(s1, -wl, zr), Pt(s0, -wl, zr)], c("ISO-AGUA-D"), bordes=[False] * 4)
        # cabezal de inicio (el extremo final o empalma o sale por el cerco)
        if not any(g["r"]["nudos"][0] in g2["r"]["nudos"][1:] for g2 in G.values()) and en_caja(g["xy"][0]):
            r0, f0 = rf(g, 0.0); p, u = pos(g, 0.0)
            Pt = lambda s, d, z: L(*lado(g, s, d), z)
            if vis.ve((p[0], p[1], (r0 + f0) / 2), (u[0], u[1], 0)):
                E.cara([Pt(0.0, wi, f0), Pt(0.0, -wi, f0), Pt(0.0, -wi, r0), Pt(0.0, wi, r0)], c_muro)
            q = [lado(g, 0.0, wt), lado(g, 0.0, -wt)]; q += [(q[1][0] - u[0] * 0.10, q[1][1] - u[1] * 0.10), (q[0][0] - u[0] * 0.10, q[0][1] - u[1] * 0.10)]
            E.cara([L(x, y, r0) for x, y in q], col)
        if es_poza and en_caja(g["xy"][-1]):             # muro frontal de la poza: rebalsa por su corona (nivel del terreno)
            r1, f1 = rf(g, fin); p, u = pos(g, fin); wl = DS.POZA_DIM[0] / 2
            Pt = lambda s, d, z: L(*lado(g, s, d), z)
            E.cara([Pt(fin, wl, f1), Pt(fin, -wl, f1), Pt(fin, -wl, r1), Pt(fin, wl, r1)], c("ISO-POZA"), sesgo=-0.05)
    return G


def terreno(E, vis, caja, paso, ver_malla=False):
    """Malla del terreno (dentro del cerco: rasante de diseno; fuera: terreno natural) y veredas a +0.10."""
    L = vis.L; ras = DS.rasante_fn(); ce = Path(DS.CERCO)
    x0, y0, x1, y1 = caja
    xs = np.arange(x0, x1 + 1e-6, paso); ys = np.arange(y0, y1 + 1e-6, paso)
    Z = np.array([[ras(x, y) for x in xs] for y in ys])
    VER = DS.veredas() if ver_malla else []
    E.g = 0
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            zz = [Z[j, i], Z[j, i + 1], Z[j + 1, i + 1], Z[j + 1, i]]
            if not all(np.isfinite(zz)): continue
            xy = [(xs[i], ys[j]), (xs[i + 1], ys[j]), (xs[i + 1], ys[j + 1]), (xs[i], ys[j + 1])]
            pm = ((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2); dentro = ce.contains_point(pm)
            if VER and any(v.contains_point(pm) for v in VER):
                E.g = 0.5; E.cara([L(p[0], p[1], z + H_VER) for p, z in zip(xy, zz)], c("ISO-VER"), bordes=[False] * 4); E.g = 0
                continue
            E.cara([L(p[0], p[1], z) for p, z in zip(xy, zz)], c("ISO-PLAT") if dentro else c("ISO-TERR"), bordes=[False] * 4)
    # curvas de nivel cada 0.50 m donde el terreno es el natural
    E.g = 0.4
    for z, pts in T.curvas():
        for a, b in zip(pts[:-1], pts[1:]):
            if not (x0 <= a[0] <= x1 and y0 <= a[1] <= y1 and x0 <= b[0] <= x1 and y0 <= b[1] <= y1): continue
            if abs(ras(*a) - z) < 0.03 and abs(ras(*b) - z) < 0.03:
                E.cara([L(a[0], a[1], z + 0.02), L(b[0], b[1], z + 0.02)], c("ISO-CURVAS"), bordes=[True, False], relleno=False)
    # veredas
    for pth in ([] if ver_malla else DS.veredas()):
        q = [tuple(v) for v in pth.vertices]
        if not any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in q): continue
        E.g = 0.5
        for tr in triangular(q):
            E.cara([L(p[0], p[1], ras(*p) + H_VER) for p in tr], c("ISO-VER"), bordes=[False] * 3)
        E.g = 0.6
        if math.dist(q[0], q[-1]) < 1e-6: q = q[:-1]
        E.cara([L(p[0], p[1], ras(*p) + H_VER + 0.01) for p in q], c("ISO-VER-BORDE"), relleno=False)
    return ras


def cerco(E, R, vis, caja=None):
    """Sardinel rojo sobre el eje del cerco (limite de intervencion), abierto en el pase de cada descarga."""
    L = vis.L; ras = DS.rasante_fn(); ce = DS.CERCO; n = len(ce)
    pases = [tuple(R["nudos"][d]) for d in ("D1", "D2", "D3")]
    E.g = 2
    for k in range(n):
        a, b = ce[k], ce[(k + 1) % n]; Lg = math.dist(a, b)
        if Lg < 0.05: continue
        u = ((b[0] - a[0]) / Lg, (b[1] - a[1]) / Lg); m = max(1, int(math.ceil(Lg / 1.0)))
        for i in range(m):
            p = (a[0] + u[0] * Lg * i / m, a[1] + u[1] * Lg * i / m); q = (a[0] + u[0] * Lg * (i + 1) / m, a[1] + u[1] * Lg * (i + 1) / m)
            if caja and not all(caja[0] <= w[0] <= caja[2] and caja[1] <= w[1] <= caja[3] for w in (p, q)): continue
            pm = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if any(math.dist(pm, d) < DS.B_TOT / 2 + 0.3 for d in pases): continue
            e = E_CERCO / 2; nrm = (-u[1] * e, u[0] * e)
            zp = ras(p[0] - nrm[0] * 4, p[1] - nrm[1] * 4); zq = ras(q[0] - nrm[0] * 4, q[1] - nrm[1] * 4)   # cota del lado interior
            if not (np.isfinite(zp) and np.isfinite(zq)): continue
            for sg in (1, -1):
                E.cara([L(p[0] + sg * nrm[0], p[1] + sg * nrm[1], zp - 0.3), L(q[0] + sg * nrm[0], q[1] + sg * nrm[1], zq - 0.3),
                        L(q[0] + sg * nrm[0], q[1] + sg * nrm[1], zq + H_CERCO), L(p[0] + sg * nrm[0], p[1] + sg * nrm[1], zp + H_CERCO)],
                       c("ISO-CERCO"), bordes=[False] * 4)
            E.cara([L(p[0] + nrm[0], p[1] + nrm[1], zp + H_CERCO), L(q[0] + nrm[0], q[1] + nrm[1], zq + H_CERCO),
                    L(q[0] - nrm[0], q[1] - nrm[1], zq + H_CERCO), L(p[0] - nrm[0], p[1] - nrm[1], zp + H_CERCO)], c("ISO-CERCO"),
                   bordes=[True, False, True, False])


def salida(R, V, D):
    """Recorrido del agua fuera del cerco (sobre el terreno natural): lista de puntos 3D desde la descarga."""
    zt = T.modelo(); x, y = R["nudos"][D]; d = next(v for v in V["descargas"] if v["D"] == D)
    u = DS.DIR_SALIDA.get(D)
    if u is None:
        rr = next(r for r in R["ramales"] if r["nudos"][-1] == D); a = R["nudos"][rr["nudos"][-2]]; Lg = math.dist(a, (x, y))
        u = ((x - a[0]) / Lg, (y - a[1]) / Lg)
    largo = max(6.0, (d["sale_a_m"] or 4.0) + 3.0); pts = []
    for k in range(0, int(largo / 0.5) + 1):
        dd = 0.5 * k; px, py = x + u[0] * dd, y + u[1] * dd; z = zt(px, py)
        if not np.isfinite(z): break
        pts.append((px, py, z + 0.04))
    return u, pts


def agua(E, R, V, vis, caja=None, solo=None):
    L = vis.L; out = {}
    E.g = 1
    for d in V["descargas"]:
        D = d["D"]
        if solo and D != solo: continue
        u, pts = salida(R, V, D)
        if caja: pts = [p for p in pts if caja[0] <= p[0] <= caja[2] and caja[1] <= p[1] <= caja[3]]
        out[D] = pts; w = 0.20
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]; ww = w + 0.25 * i / max(1, len(pts) - 1)
            E.cara([L(a[0] - u[1] * ww, a[1] + u[0] * ww, a[2]), L(b[0] - u[1] * ww, b[1] + u[0] * ww, b[2]),
                    L(b[0] + u[1] * ww, b[1] - u[0] * ww, b[2]), L(a[0] + u[1] * ww, a[1] - u[0] * ww, a[2])], c("ISO-AGUA-D"),
                   bordes=[False] * 4, sesgo=0.05)
    return out


# ----------------------------------------------------------------------------- laminas
def capas_iso(doc):
    for n, rgb in RGB.items():
        if n not in doc.layers:
            ly = doc.layers.add(n, color=7); ly.rgb = rgb
        B.COLOR_RGB[n] = rgb
    if "ISO-ARISTAS" not in doc.layers: doc.layers.add("ISO-ARISTAS", color=8)


def rosa(lam, vis, P2, xmm, ymm):
    o = lam.P(xmm, ymm); x, y, z = vis.o
    for ang, t in ((0, "E"), (90, "N")):
        dx, dy = math.cos(math.radians(ang)) * 12 * lam.f / 0.35, math.sin(math.radians(ang)) * 12 * lam.f / 0.35
        a, b = P2(vis.L(x, y, z)), P2(vis.L(x + dx, y + dy, z))
        v = (b[0] - a[0], b[1] - a[1]); q = (o[0] + v[0], o[1] + v[1])
        lam.flecha(o, q, "TEXTOS", tam_mm=3.0); lam.texto((q[0] + v[0] * 0.3, q[1] + v[1] * 0.3), t, 3.0, "TITULOS", TA.MIDDLE_CENTER)


def leyenda(lam, xmm, ymm, detalle=False):
    items = [("relleno", "ISO-S%d" % k, "Cuneta del " + NOM[k].lower().replace("(d", "(D")) for k in (1, 2, 3)]
    items += [("relleno", "ISO-TAP", "Tramo tapado con losa (cruce de vereda, atrio, pase)"), ("relleno", "ISO-GRAD", "Gradas de concreto (V > 3 m/s)"),
              ("relleno", "ISO-FONDO", "Fondo de cuneta (cota de fondo de diseno)")]
    if detalle: items += [("relleno", "ISO-REJ", "Rejilla de platinas (tramos abiertos)"), ("relleno", "ISO-POZA", "Poza de salida D2 (rebalse a nivel del terreno)")]
    items += [("relleno", "ISO-AGUA-D", "Agua que sale por el cerco al terreno natural"), ("relleno", "ISO-CERCO", "Cerco perimetrico = limite de intervencion"),
              ("relleno", "ISO-VER", "Veredas (+0.10 sobre la rasante)"), ("relleno", "ISO-PLAT", "Terreno terminado dentro del cerco (NTN +184.50)"),
              ("relleno", "ISO-TERR", "Terreno natural fuera del cerco"), ("linea", "ISO-CURVAS", "Curvas de nivel cada 0.50 m (C-TOPO)")]
    lam.leyenda2(xmm, ymm, items, hmm=1.8)


def isometrico(doc, R, V, ox, oy, codigo, giro, titulo, sub):
    lam = B.Lamina(doc, ox, oy, 350, codigo, titulo, sub, escala_txt="1/350 (H = V)")
    ymm = 255 if giro > 90 else 300
    vis = Vista(giro)
    Et = iso3d.Escena(); terreno(Et, vis, CAJA, 1.0)
    Ec = iso3d.Escena(); Ec.g = 1; cunetas(Ec, R, V, vis, None, paso=2.0); fl = agua(Ec, R, V, vis); cerco(Ec, R, vis)
    with EnBloque(lam, "ISO_TERRENO_VEREDAS_" + codigo.replace("-", "")):
        P2 = dibujar(Et, lam, 420, ymm)
    with EnBloque(lam, "ISO_CUNETAS_" + codigo.replace("-", "")):
        dibujar(Ec, lam, 420, ymm)
    # rotulos: descargas y sistemas
    usados = []
    for d in V["descargas"]:
        D = d["D"]; pts = fl[D]
        if len(pts) < 2: continue
        pa, pb = P2(vis.L(*pts[-2])), P2(vis.L(*pts[-1])); lam.flecha(pa, pb, "LLAMADAS", tam_mm=4.0)
        txt = ["%s: %s  C.F. %.3f" % (D, "POZA DE SALIDA" if d["tipo"] == "poza" else "PASE EN EL CIMIENTO DEL CERCO", d["cf"])]
        txt.append(("rebalsa a %.2f; el fondo exterior baja 0.25 m a %.1f m" % (d["nivel_rebalse"], d["sale_a_m"])) if d["tipo"] == "poza"
                   else ("el terreno exterior queda bajo la C.F. a %.1f m del cerco" % d["sale_a_m"]))
        p0 = P2(vis.L(*pts[0])); dx = 1 if (pb[0] - p0[0]) >= 0 else -1
        pt = (p0[0] + dx * 30 * lam.f, p0[1] + 26 * lam.f)
        while any(abs(pt[1] - q[1]) < 10 * lam.f and abs(pt[0] - q[0]) < 120 * lam.f for q in usados): pt = (pt[0], pt[1] + 11 * lam.f)
        usados.append(pt)
        lam.llamada(p0, pt, txt, hmm=2.2, al=TA.LEFT if dx > 0 else TA.RIGHT)
    for k in (1, 2, 3):
        rr = [r for r in R["ramales"] if r["sistema"] == k]; pts = [R["nudos"][n] for r in rr for n in r["nudos"]]
        cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        pc = P2(vis.L(cx, cy, 190.0))
        lam.texto(pc, NOM[k], 3.0, "TITULOS", TA.MIDDLE_CENTER, color=COL_TXT[k])
    rosa(lam, vis, P2, 790, 540)
    leyenda(lam, 25, 578)
    lam.notas(25, 110, "NOTAS", [
        "1. Isometrico a escala real 1/350 (sin exageracion vertical): solo las cunetas sobre el terreno y las veredas; las edificaciones no se dibujan.",
        "2. Las cunetas quedan dentro del cerco perimetrico (limite de intervencion); fuera del cerco solo se indica el agua sobre el terreno natural.",
        "3. Cuneta: 0.40 m libre, muros de 0.10 m (0.60 m total); rejilla en los tramos abiertos (ver %s)" % COD_DET + "; cotas de fondo en DC-02 y perfiles.",
        "4. Terreno: dentro del cerco la rasante de diseno (plataforma +184.50); fuera, el terreno natural de las curvas C-TOPO del plano."],
        hmm=1.6, ancho_mm=300)
    return lam


def detalles(doc, R, V, ox, oy, codigo="DC-10"):
    """Detalle: isometricos de las tres descargas a 1/75, con rejillas, tapados, gradas, poza y el agua fuera del cerco."""
    lam = B.Lamina(doc, ox, oy, 75, codigo, "DETALLE ISOMETRICO DE LAS DESCARGAS POR EL CERCO (D1, D2 Y D3)",
                   "CUNETAS DENTRO DEL CERCO, PASE O POZA EN EL CERCO Y SALIDA DEL AGUA AL TERRENO NATURAL - ESCALA REAL", escala_txt="1/75 (H = V)")
    xs = {"D1": 150, "D3": 425, "D2": 690}; half = 5.5; ymm = 330
    for D in ("D1", "D3", "D2"):
        d = next(v for v in V["descargas"] if v["D"] == D); x, y = R["nudos"][D]
        rr = next(r for r in R["ramales"] if r["nudos"][-1] == D); a = R["nudos"][rr["nudos"][-2]]
        u = DS.DIR_SALIDA.get(D) or ((x - a[0]) / math.dist(a, (x, y)), (y - a[1]) / math.dist(a, (x, y)))
        beta = math.degrees(math.atan2(u[1], u[0])); giro = 45 - (beta + 180 + 35)
        cx, cy = x - u[0] * 1.5, y - u[1] * 1.5
        caja = (cx - half, cy - half, cx + half, cy + half)
        vis = Vista(giro, cx, cy, DS.rasante_fn()(x - u[0], y - u[1]))
        Et = iso3d.Escena(); terreno(Et, vis, caja, 0.5, ver_malla=True)
        Ec = iso3d.Escena(); Ec.g = 1; cunetas(Ec, R, V, vis, caja, paso=0.5, detalle=True)
        fl = agua(Ec, R, V, vis, caja, solo=D)
        cerco(Ec, R, vis, caja)
        with EnBloque(lam, "ISO_DETALLE_" + D):
            P2 = dibujar(Et, lam, xs[D], ymm)
        with EnBloque(lam, "ISO_DETALLE_CUNETAS_" + D):
            dibujar(Ec, lam, xs[D], ymm)
        lam.titulo_vista(xs[D], 520, "DESCARGA %s - %s" % (D, "POZA DE SALIDA" if d["tipo"] == "poza" else "PASE EN EL CERCO"),
                         "Ramal %s - C.F. %.3f - el observador mira en el sentido del agua" % (rr["codigo"], d["cf"]), ancho_mm=150)
        pts = fl[D]
        if len(pts) >= 2:
            pa, pb = P2(vis.L(*pts[-2])), P2(vis.L(*pts[-1])); lam.flecha(pa, pb, "LLAMADAS", tam_mm=5.0)
        p0 = P2(vis.L(x, y, rr["perfil"][-1][1] + 0.1))
        txt = (["POZA DE SALIDA %.2f x %.2f m (interior)" % DS.POZA_DIM, "fondo C.F. %.3f; rebalsa a %.2f (nivel del terreno)" % (d["cf"], d["nivel_rebalse"]),
                "afuera el fondo de la hondonada no sube; baja 0.25 m a %.1f m" % d["sale_a_m"]] if d["tipo"] == "poza" else
               ["PASE EN EL CIMIENTO DEL CERCO (tramo tapado)", "C.F. %.3f en el eje del cerco" % d["cf"],
                "terreno exterior bajo la C.F. a %.1f m (solo perfilado)" % d["sale_a_m"]])
        px = (p0[0] - lam.ox) / lam.f
        lam.llamada(p0, lam.P(min(max(px - 15, xs[D] - 125), xs[D] + 20), 440), txt, hmm=2.2)
        import textwrap
        lam.textos(lam.P(xs[D] - 120, 190), textwrap.wrap("Receptor: " + d["receptor"], 70), 1.9, "TEXTOS")
        rosa(lam, vis, P2, xs[D] + 85, 150)
    lam.leyenda2(25, 70, [("relleno", "ISO-S1", "Cuneta sistema 1"), ("relleno", "ISO-S2", "Cuneta sistema 2"), ("relleno", "ISO-S3", "Cuneta sistema 3"),
                          ("relleno", "ISO-TAP", "Tapado (losa)"), ("relleno", "ISO-REJ", "Rejilla de platinas"), ("relleno", "ISO-GRAD", "Gradas"),
                          ("relleno", "ISO-POZA", "Poza de salida D2"), ("relleno", "ISO-AGUA-D", "Agua fuera del cerco"), ("relleno", "ISO-CERCO", "Cerco = limite"),
                          ("relleno", "ISO-VER", "Vereda (+0.10)"), ("relleno", "ISO-PLAT", "Terreno terminado"), ("relleno", "ISO-TERR", "Terreno natural")],
                 hmm=1.6, ancho_col=75, filas_col=3)
    return lam


def rf_nudo(R, r, D):
    return r["perfil"][-1][1]

