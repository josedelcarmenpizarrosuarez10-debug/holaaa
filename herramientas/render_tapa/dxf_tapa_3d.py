"""Lamina DP-06D: registro de limpieza con tapa 0.68 x 0.68 c/marco y contramarco - COMPONENTES, en DXF.
Cuatro isometricos en color (registro armado, despiece, corte por el registro y armado interior de la tapa), con
llamadas numeradas, cuadro de componentes y datos clave. Misma geometria del modelo 3D (modelo.py) y del contramarco
del proyecto (variable CONTRAMARCO; Hogar de Refugio: L 1 1/2" x 1 1/2" x 1/8").
Escala real (1 unidad = 1 m), lamina A1 a 1/10; las vistas 3 y 4 se dibujan al doble (ESC. 1/5).
Uso: python3 herramientas/render_tapa/dxf_tapa_3d.py   -> entregables/PLANO_DP-06D_ISOMETRICOS_TAPA_REGISTRO_HOGAR_REFUGIO.dxf
"""
import os, sys, math
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
for p in (AQUI, HERR, os.path.join(HERR, "techo")):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np
from ezdxf.enums import TextEntityAlignment as TA
import dxf_base as B
import dxf_layouts as L
from iso3d import Escena, proy
from modelo import modelo, CM_TXT, CM_KGM, CM_L, LUZ, ET, BI, BW, MURO_APOYO, GANCHO
# proyecto (por defecto el Hogar de Refugio; CAR Varones: herramientas/varones/planos_v.py fija COLECTOR_B, N_REG y PROY_DP06D)
N_REG = int(os.environ.get("N_REG", "10"))
PROY_TXT = os.environ.get("PROY_DP06D", "Hogar de Refugio Temporal \"Mujeres Violentadas\" (CUI 2675514)")
XM = BI + BW                                  # cara exterior del muro

SAL = os.path.join(RAIZ, "entregables", "PLANO_DP-06D_ISOMETRICOS_TAPA_REGISTRO_HOGAR_REFUGIO.dxf")
COL = {"concreto": (196, 194, 188), "tapa": (176, 174, 168), "angulo": (48, 52, 60), "acero": (138, 88, 58), "liso": (128, 124, 118)}
AZ, NAR, CEL = (31, 78, 121), (192, 80, 20), (235, 241, 248)
YC = -0.125                                   # plano del corte (linea de anclajes)
CAPAS = [("ISO-3D", 7, "CONTINUOUS", 13), ("ISO-3D-ARISTAS", 250, "CONTINUOUS", 13), ("PANEL", 5, "CONTINUOUS", 35),
         ("PANEL-FONDO", 5, "CONTINUOUS", 13), ("LLAMADAS-NUM", 30, "CONTINUOUS", 25)]


# ------------------------------------------------------------------ transformaciones y recortes
def rot90(p):                                 # vista desde (+x, -y, +z): giro de 90 grados alrededor de z
    return np.array([-p[1], p[0], p[2]])


def recorte_caja(b, R):
    if R is None: return b
    c = [max(b[0], R[0]), min(b[1], R[1]), max(b[2], R[2]), min(b[3], R[3]), max(b[4], R[4]), min(b[5], R[5])]
    return c if c[0] < c[1] - 1e-9 and c[2] < c[3] - 1e-9 and c[4] < c[5] - 1e-9 else None


def recorte_seg(a, b, R):
    if R is None: return a, b
    t0, t1 = 0.0, 1.0; d = b - a
    for k in range(3):
        lo, hi = R[2 * k], R[2 * k + 1]
        if abs(d[k]) < 1e-12:
            if a[k] < lo - 1e-9 or a[k] > hi + 1e-9: return None
            continue
        u0, u1 = (lo - a[k]) / d[k], (hi - a[k]) / d[k]
        if u0 > u1: u0, u1 = u1, u0
        t0, t1 = max(t0, u0), min(t1, u1)
        if t0 > t1 - 1e-9: return None
    return a + t0 * d, a + t1 * d


# ------------------------------------------------------------------ solido como union de cajas (sin costuras)
COL_CORTE = {"concreto": (226, 210, 176), "tapa": (216, 200, 168), "angulo": (96, 102, 116)}


def solido(E, cajas, T, paso, relleno=True, cortes=()):
    """Dibuja la union de cajas alineadas [(caja, material)]: en cada plano se quitan las caras en contacto (normales
    opuestas) y las aristas entre caras vecinas del mismo material; las caras sobre un plano de corte llevan el color
    de seccion. T transforma los puntos (giro, escala, desplazamiento)."""
    planos = {}
    for b, mat in cajas:
        for ax in range(3):
            o = [i for i in range(3) if i != ax]
            for sg, c in ((-1, b[2 * ax]), (1, b[2 * ax + 1])):
                planos.setdefault((ax, round(c, 6)), []).append((sg, b[2 * o[0]], b[2 * o[0] + 1], b[2 * o[1]], b[2 * o[1] + 1], mat))
    for (ax, c), lst in planos.items():
        o = [i for i in range(3) if i != ax]
        es_corte = any(ax == k and abs(c - v) < 1e-6 for k, v in cortes)
        us = sorted({round(v, 6) for r in lst for v in r[1:3]}); vs = sorted({round(v, 6) for r in lst for v in r[3:5]})
        nu, nv = len(us) - 1, len(vs) - 1
        vis = {}
        for i in range(nu):
            for j in range(nv):
                um, vm = (us[i] + us[i + 1]) / 2, (vs[j] + vs[j + 1]) / 2
                pos = [r for r in lst if r[0] > 0 and r[1] <= um <= r[2] and r[3] <= vm <= r[4]]
                neg = [r for r in lst if r[0] < 0 and r[1] <= um <= r[2] and r[3] <= vm <= r[4]]
                if bool(pos) != bool(neg): vis[i, j] = (1, pos[0][5]) if pos else (-1, neg[0][5])
        for (i, j), (sg, mat) in vis.items():
            def pt(u, v):
                p = [0.0, 0.0, 0.0]; p[ax] = c; p[o[0]] = u; p[o[1]] = v; return T(np.array(p))
            p0, p1, p2, p3 = pt(us[i], vs[j]), pt(us[i + 1], vs[j]), pt(us[i + 1], vs[j + 1]), pt(us[i], vs[j + 1])
            vecino = lambda a, b: vis.get((a, b)) == (sg, mat)
            bordes = (not vecino(i, j - 1), not vecino(i + 1, j), not vecino(i, j + 1), not vecino(i - 1, j))
            rgb = COL_CORTE.get(mat, COL[mat]) if es_corte else COL[mat]
            E.quad(p0, p1, p2, p3, rgb, paso, relleno=relleno, bordes=bordes)


def cajas_de(P, claves, R=None, dz=0.0):
    out = []
    for k in claves:
        for b in P[k].boxes:
            c = recorte_caja(b, R)
            if c: out.append(([c[0], c[1], c[2], c[3], c[4] + dz, c[5] + dz], P[k].mat))
    return out


def parte(E, P, k, T, R=None, dz=0.0, paso=0.04, relleno=True, n=8, cortes=(), sesgo=0.0):
    cajas = cajas_de(P, [k], R, dz)
    if cajas: solido(E, cajas, T, paso, relleno, cortes)
    barras(E, P, k, T, R, dz, n, sesgo)


def barras(E, P, k, T, R=None, dz=0.0, n=8, sesgo=0.0):
    i0 = len(E.caras); rgb = COL[P[k].mat]
    for a, b, d in P[k].bars:
        s = recorte_seg(np.asarray(a, float), np.asarray(b, float), R)
        if s is None or np.linalg.norm(s[1] - s[0]) < 1e-4: continue
        a2, b2 = s[0] + [0, 0, dz], s[1] + [0, 0, dz]
        E.cilindro(T(a2), T(b2), d / 2 * T.k, rgb, n=n, tapas=True, paso=0.05 * T.k)
    if sesgo:                                                # barras cortadas: su seccion queda delante de la cara del corte
        E.caras[i0:] = [(c[0], c[1], c[2], c[3] + sesgo, c[4], c[5]) for c in E.caras[i0:]]


class Tr:
    def __init__(self, k=1.0, girar=True): self.k, self.girar = k, girar
    def __call__(self, p):
        p = np.asarray(p, float)
        return (rot90(p) if self.girar else p) * self.k


def extension(E):
    pts = np.array([proy(p) for c in E.caras for p in c[0]])
    return pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max()


# ------------------------------------------------------------------ escenas
def escena(nv, P):
    E = Escena()
    if nv == 1:                                              # registro armado: un solo solido (losa, tapa y angulos)
        T = Tr(1.0); R = (-1, 1, -0.75, 0.75, -0.65, 0.01)
        solido(E, cajas_de(P, ("losa", "engrosado", "muros", "contramarco", "tapa", "marco"), R), T, 0.03)
        barras(E, P, "asas", T, (-1, 1, -1, 1, -0.03, 0.01), sesgo=0.01)            # agarraderas dentro del bolsillo
    elif nv == 2:                                            # despiece
        T = Tr(1.0); R = (-1, 1, -0.45, 0.45, -0.38, 0.01)
        OFF = {"contramarco": 0.17, "anclajes": 0.17, "parrilla": 0.33, "asas": 0.45, "tapa": 0.58, "marco": 0.76}
        solido(E, cajas_de(P, ("losa", "engrosado", "muros"), R), T, 0.05)
        for g, k in enumerate(("contramarco", "anclajes", "parrilla", "asas", "tapa", "marco")):
            E.g = g + 1; parte(E, P, k, T, None, dz=OFF[k], paso=0.03)
    elif nv == 3:                                            # corte por la linea de anclajes
        yc, xc = YC + 0.006, 0.50
        T = Tr(2.0, girar=False); R = (-0.12, xc, -0.30, yc, -0.40, 0.01); cortes = ((1, yc), (0, xc))
        solido(E, cajas_de(P, ("losa", "engrosado", "muros", "contramarco", "tapa", "marco"), R), T, 0.015, cortes=cortes)
        Rb = (-0.12, xc + 0.001, yc - 0.015, yc, -0.40, 0.01)      # solo lo que asoma en la cara del corte
        for k in ("refuerzo", "anclajes", "parrilla"): barras(E, P, k, T, Rb, n=12, sesgo=0.02)
        barras(E, P, "refuerzo", T, (xc - 0.015, xc + 0.001, -0.30, yc, -0.40, 0.01), n=12, sesgo=0.02)
    else:                                                    # tapa con concreto transparente
        T = Tr(2.0)
        parte(E, P, "tapa", T, None, paso=0.20, relleno=False)
        for k in ("parrilla", "asas"): barras(E, P, k, T, None, n=10)
        E.g = 1; parte(E, P, "marco", T, None, paso=0.04)
    return E, T


# llamadas: (clave, punto del modelo, desplazamiento del globo en mm)
LLAM = {
    1: [("1", (-0.45, -0.55, 0), (-16, 12)), ("9", (0.20, -0.325, 0.0), (-6, -18)), ("8", (-0.1, -0.1, 0), (-20, -6)),
        ("7", (0.0, 0.22, -0.01), (16, 14)), ("10", (XM, -0.2, -0.35), (16, -10))],
    2: [("1", (-0.45, -0.40, 0), (-18, 10)), ("4", (0.33, -0.33, 0.17 - 0.08), (22, -6)), ("5", ((0.38, -0.125, 0.17 - 0.20) if MURO_APOYO else (0.44, -0.125, 0.17 - 0.07)), (24, 2)),
        ("6", (0.2, -0.31, 0.33 - 0.045), (-30, -6)), ("7", (0.155, -0.22, 0.45 - 0.06), (24, -4)), ("8", (0.34, -0.2, 0.58 - 0.04), (24, 2)),
        ("9", (0.34, -0.34, 0.76), (22, 4)), ("10", (XM, -0.3, -0.30), (18, -8))],
    3: [("1", (0.45, -0.22, 0.0), (8, 20)), (("cm", (0.40, YC, -0.22), (-40, -4)) if MURO_APOYO else ("2", (0.42, YC, -0.17), (-36, -4))), ("3", (0.40, YC, -0.045), (-30, 6)),
        ("4", (0.348, YC, -0.11), (10, -22)), ("5", ((0.375, YC, -0.20) if MURO_APOYO else (0.44, YC, -0.07)), (-22, 18)), ("6", (0.0, YC, -0.0545), (12, 22)),
        ("8", (0.15, YC, -0.03), (10, 24)), ("9", (0.338, YC, -0.025), (-16, 24)), ("10", (XM - 0.03 if MURO_APOYO else 0.47, YC, -0.30), (20, -12)),
        ("ap", (0.32, YC, -0.082), (-36, -26)), ("hg", (0.345, YC, -0.003), (26, 26))],
    4: [("6", (-0.31, -0.2, -0.055), (-22, 14)), ("7", (0.06, -0.22, -0.015), (12, -22)), ("8", (-0.2, -0.34, -0.06), (-16, -14)),
        ("9", (0.34, 0.1, 0.0), (22, -8)), ("h", (-0.12, 0.22, -0.06), (-24, 20))],
}
LAB = {"cm": "cabeza del muro", "ap": "asiento %.3f" % CM_L, "hg": "holgura 1 cm", "h": "bolsillo del asa"}
TIT = {1: ("1. REGISTRO ARMADO (vista general)", "ESC. 1/10"), 2: ("2. DESPIECE: CADA COMPONENTE SEPARADO", "ESC. 1/10 - orden de armado de abajo hacia arriba"),
       3: ("3. CORTE POR EL REGISTRO: APOYO DE LA TAPA Y REFUERZOS", "ESC. 1/5 - corte por la linea de anclajes"),
       4: ("4. TAPA: ARMADO INTERIOR (concreto transparente)", "ESC. 1/5")}
# paneles (mm del papel): x0, y0, x1, y1
PAN = {1: (27, 343, 426, 562), 2: (430, 343, 829, 562), 3: (27, 116, 426, 337), 4: (430, 116, 829, 337)}


def solido2d(lam, pts, rgb, capa="PANEL-FONDO"):
    e = lam.msp.add_solid([pts[0], pts[1], pts[3], pts[2]], dxfattribs={"layer": capa}); e.rgb = rgb


def panel(lam, nv):
    x0, y0, x1, y1 = PAN[nv]; hb = 9
    solido2d(lam, [lam.P(x0, y1 - hb), lam.P(x1, y1 - hb), lam.P(x1, y1), lam.P(x0, y1)], CEL)
    lam.rect(*lam.P(x0, y0), *lam.P(x1, y1), "PANEL"); lam.linea(lam.P(x0, y1 - hb), lam.P(x1, y1 - hb), "PANEL")
    t, s = TIT[nv]
    lam.texto(lam.P(x0 + 3, y1 - hb / 2), t, 3.4, "TITULOS", TA.MIDDLE_LEFT)
    lam.texto(lam.P(x1 - 3, y1 - hb / 2), s, 2.2, "TEXTOS", TA.MIDDLE_RIGHT)
    return x0, y0, x1, y1 - hb


def globo(lam, q, d_mm, clave):
    f = lam.f; c = (q[0] + d_mm[0] * f, q[1] + d_mm[1] * f)
    lam.circulo(q, 0.8 * f, "LLAMADAS-NUM")
    if clave in LAB:
        t = LAB[clave]; w = (len(t) * 1.75 + 5) * f; h = 6 * f
        dx = -w / 2 if True else 0
        lam.linea(q, c, "LLAMADAS-NUM")
        pts = [(c[0] - w / 2, c[1] - h / 2), (c[0] + w / 2, c[1] - h / 2), (c[0] + w / 2, c[1] + h / 2), (c[0] - w / 2, c[1] + h / 2)]
        solido2d(lam, pts, (255, 255, 255), "LLAMADAS-NUM"); lam.poli(pts, "LLAMADAS-NUM", cerrada=True, const_width=0.35 * f)
        lam.texto(c, t, 2.6, "LLAMADAS-NUM", TA.MIDDLE_CENTER)
    else:
        r = 4.0 * f; v = np.array(c) - np.array(q); L_ = np.linalg.norm(v)
        lam.linea(q, tuple(np.array(c) - v / L_ * r), "LLAMADAS-NUM")
        n = 24; pts = [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        for i in range(1, n - 1): solido2d(lam, [pts[0], pts[i], pts[i + 1], pts[i + 1]], (255, 255, 255), "LLAMADAS-NUM")
        lam.poli(pts, "LLAMADAS-NUM", cerrada=True, const_width=0.45 * f)
        lam.texto(c, clave, 3.0, "LLAMADAS-NUM", TA.MIDDLE_CENTER)


def vista(lam, P, nv):
    x0, y0, x1, y1 = panel(lam, nv)
    E, T = escena(nv, P)
    a, b, c, d = extension(E)
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    ox = xc - (a + b) / 2 / lam.f; oy = yc - (c + d) / 2 / lam.f
    if (b - a) / lam.f > x1 - x0 - 50 or (d - c) / lam.f > y1 - y0 - 6:
        print("aviso: la vista %d no entra en su panel (%.0f x %.0f mm)" % (nv, (b - a) / lam.f, (d - c) / lam.f))
    P2 = E.dibujar(lam, ox, oy, capa_rel="ISO-3D", capa_ar="ISO-3D-ARISTAS")
    for clave, p3, dm in LLAM[nv]:
        globo(lam, P2(T(np.array(p3, float))), dm, clave)


COMP = [("1", "Losa superior del colector e = 0.10 m, concreto f'c=210: abertura 0.70 x 0.70 m en todo su espesor"),
        ("2", "Borde engrosado 0.15 x 0.10 m bajo la losa, solo en los 2 lados transversales, entre muros (2 x %.2f m: %.3f m3); en los lados largos el asiento es la cabeza del muro" % (2 * BI, 4 * BI * 0.015)
              if MURO_APOYO else "Borde engrosado 0.15 x 0.10 m bajo la losa, alrededor de la abertura (0.045 m3)"),
        ("3", "Refuerzo de borde: 2 barras de 1/2\" por lado, L = 1.40 m (8 barras, 11.1 kg); las transversales con ganchos de %.2f m dentro de los muros" % GANCHO),
        ("4", "Contramarco angulo %s: asiento de la tapa a 0.08 bajo el piso (2.80 m, %.1f kg)" % (CM_TXT, 2.80 * CM_KGM)),
        ("5", "Anclajes de 3/8\" L = 0.20 m soldados al contramarco (8 und): en los lados largos bajan dentro del muro" if MURO_APOYO else "Anclajes de 3/8\" L = 0.20 m soldados al contramarco e inclinados hacia la losa (8 und)"),
        ("6", "Parrilla de la tapa: 7 + 7 barras de 3/8\" @ 0.10 m, L = 0.62 m, recubrimiento 2.5 cm (4.9 kg)"),
        ("7", "Asas: 2 barras de 3/8\" liso de 0.40 m, embutidas en bolsillo (no sobresalen del piso)"),
        ("8", "Tapa de concreto f'c=210: 0.68 x 0.68 x 0.08 m (0.037 m3)"),
        ("9", "Marco de tapa angulo L 1 1/2\" x 1 1/2\" x 1/8\", 0.68 x 0.68 exterior (2.72 m, 5.0 kg)"),
        ("10", "Muros del colector e = 0.15 m (ancho interior %.2f m)" % (2 * BI))]


def datos():
    ala = CM_TXT.split(" x ")[0][2:]
    pint = 2.80 * (0.152 if "1/2" in ala else 0.203) + 2.72 * 0.152
    return ["Holgura entre marco y contramarco: (0.70 - 0.68) / 2 = 1 cm por lado",
            "La tapa asienta sobre el ala del contramarco (%s = %.1f cm por lado)" % (ala, CM_L * 100),
            "Luz libre entre alas del contramarco: %.2f x %.2f m" % (2 * LUZ, 2 * LUZ),
            "Peso de la tapa: 0.037 m3 x 2,400 kg/m3 + marco 5.0 kg = 94 kg aprox.",
            "Se levanta entre 2 operarios con ganchos en las 2 asas",
            "Tapa a ras del piso terminado: no hay resaltes ni tropiezos",
            "Angulos con pintura anticorrosiva y esmalte (%.2f m2 por registro)" % pint,
            "Registros fuera de los cruces vehiculares (carga peatonal): %d und" % N_REG]


def cuadro_inferior(lam):
    y1, y0 = 110, 13
    for (xa, xb, tit) in ((27, 400, "COMPONENTES (cantidades por registro)"), (404, 642, "DATOS CLAVE")):
        solido2d(lam, [lam.P(xa, y1 - 7), lam.P(xb, y1 - 7), lam.P(xb, y1), lam.P(xa, y1)], AZ)
        lam.rect(*lam.P(xa, y0), *lam.P(xb, y1), "PANEL")
        lam.texto(lam.P(xa + 3, y1 - 3.5), tit, 3.0, "TITULOS-BLANCO", TA.MIDDLE_LEFT)
    f = lam.f
    for i, (n, t) in enumerate(COMP):
        y = y1 - 12 - i * 8.5; c = lam.P(33, y); r = 3.0 * f
        lam.poli([(c[0] + r * math.cos(2 * math.pi * k / 20), c[1] + r * math.sin(2 * math.pi * k / 20)) for k in range(20)], "LLAMADAS-NUM", cerrada=True, const_width=0.3 * f)
        lam.texto(c, n, 2.2, "LLAMADAS-NUM", TA.MIDDLE_CENTER)
        lam.texto(lam.P(39, y), t, 2.15, "TEXTOS", TA.MIDDLE_LEFT)
    for i, t in enumerate(datos()):
        y = y1 - 12 - i * 8.5
        p = [lam.P(408, y - 1.2), lam.P(410.4, y - 1.2), lam.P(410.4, y + 1.2), lam.P(408, y + 1.2)]
        solido2d(lam, p, NAR, "LLAMADAS-NUM")
        lam.texto(lam.P(413, y), t, 2.15, "TEXTOS", TA.MIDDLE_LEFT)


def lamina(doc, ox, oy):
    for nm, c, lt, lw in CAPAS + [("TITULOS-BLANCO", 7, "CONTINUOUS", 25)]:
        if nm not in doc.layers:
            ly = doc.layers.add(nm, color=c, linetype=lt); ly.dxf.lineweight = lw
    B.COLOR_RGB.update({"LLAMADAS-NUM": NAR, "PANEL": AZ})
    lam = B.Lamina(doc, ox, oy, 10, "DP-06D", "REGISTRO DE LIMPIEZA CON TAPA 0.68 x 0.68 C/MARCO Y CONTRAMARCO - COMPONENTES",
                   "ISOMETRICOS: REGISTRO ARMADO, DESPIECE, CORTE Y ARMADO DE LA TAPA - CONTRAMARCO %s - ESC. INDICADAS" % CM_TXT.replace(" ", ""),
                   escala_txt="INDICADA")
    for nm, rgb in (("LLAMADAS-NUM", NAR), ("PANEL", AZ), ("TITULOS-BLANCO", (255, 255, 255))):
        doc.layers.get(nm).rgb = rgb
    solido2d(lam, [lam.P(27, 566), lam.P(829, 566), lam.P(829, 582), lam.P(27, 582)], AZ)
    lam.texto(lam.P(31, 577), "REGISTRO DE LIMPIEZA CON TAPA 0.68 x 0.68 C/MARCO Y CONTRAMARCO - COMPONENTES", 5.0, "TITULOS-BLANCO", TA.MIDDLE_LEFT)
    lam.texto(lam.P(31, 569.5), "Colector pluvial frontal - %s - contramarco %s - complementa la lamina DP-06B" % (PROY_TXT, CM_TXT),
              2.4, "TITULOS-BLANCO", TA.MIDDLE_LEFT)
    P = modelo()
    for nv in (1, 2, 3, 4): vista(lam, P, nv)
    cuadro_inferior(lam)
    lam.texto(lam.P(639, 16), "Medidas en metros salvo indicacion. Ref.: lamina DP-06B y metrado del colector.", 1.8, "TEXTOS", TA.MIDDLE_RIGHT)
    return lam


if __name__ == "__main__":
    doc = B.nuevo_documento()
    lam = lamina(doc, 0.0, 0.0)
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: -1 for e in msp.query("HATCH")})
    L.presentaciones(doc, {"DP-06D": lam})
    print("errores de auditoria:", len(doc.audit().errors))
    doc.saveas(SAL)
    print(SAL, len(msp))
