"""Drenaje pluvial de la OC-01 (jardinera + banca + pergola) - HOGAR DE REFUGIO TEMPORAL (CUI 2675514).

Fiel al plano del usuario OC-01_-_BANCA_CON_PERGOLA.dxf (planta de techos, corte A-A y elevacion E1, escala real):
tres techos a una agua (3.79, 4.21 y 3.79 de largo por 2.40 de fondo), cada uno con su canaleta y una salida en el punto
que el plano marca como "sumidero 4\" tipo cupula"; a pedido del usuario la cupula se reemplaza por una BOQUILLA de plancha
(como en la banca tipo 01). Canaleta de plancha galvanizada e = 0.50 mm, 0.18 de ancho x 0.21 de alto (indicacion del
usuario), S = 0.5 % hacia la boquilla, con 2 soportes (sujetadores) por canaleta y tapas en los dos extremos.
La bajada sigue el corte A-A: boquilla, niple, codo, tramo bajo la canaleta con colgador, codo, bajada adosada a la columna
con abrazadera y falsa columna de drenaje pluvial CL-01 (+1.05 a -0.15).
  DO-01  isometrico general de la OC-01 con las tres canaletas y sus bajadas (1/30) y planta de techos (1/50)
  DO-02  isometrico de la salida de la canaleta (boquilla, codos, colgador, bajada) y corte de la canaleta (1/5)
Escala real (1 unidad = 1 m). Uso: python3 herramientas/techo/planos_oc01_refugio.py
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
sys.path.insert(0, HERR); sys.path.insert(0, AQUI)
from iso3d import Escena
import dxf_base as B
import dxf_layouts as L
from ezdxf.enums import TextEntityAlignment as TA
import planos_techo as T

P = T.PROY["refugio"]
SAL = os.path.join(RAIZ, "entregables", "PLANOS_DRENAJE_OC-01_BANCA_PERGOLA_HOGAR_REFUGIO.dxf")
for _e in (5, 30):
    if _e not in B.ESCALAS: B.ESCALAS.append(_e)
CAPAS_OC = [("ESTRUCTURA-METALICA", 8, "CONTINUOUS", 35), ("METAL-RELL", 8, "CONTINUOUS", 13), ("JARDIN", 94, "CONTINUOUS", 25)]
B.COLOR_RGB.update({"METAL-RELL": (150, 156, 166), "GALV-RELL": (226, 231, 238)})

# ------------------------------------------------------------------ geometria (m), del plano OC-01
# x: a lo largo de los techos (0 = extremo izquierdo de la planta de techos); y: hacia el norte (0 = borde sur de los techos laterales)
# z: sobre el piso terminado de la circulacion (+0.00); jardinera a -0.15
CB, CH = 0.18, 0.21                     # canaleta de plancha galvanizada e = 0.50 mm: ancho x alto interiores (usuario)
ALA = 0.10                              # ala posterior apoyada sobre la viga, bajo la cobertura
S_CAN = 0.50                            # pendiente de la canaleta hacia la boquilla (%)
ZB0 = 2.55                              # fondo de la canaleta en la boquilla (borde superior +2.76, bajo la cobertura; corte A-A)
Z_COB = 2.855                           # cara superior de la cobertura en el borde bajo (corte A-A)
PEND = 0.125                            # cobertura: 0.30 de subida en 2.40 de fondo (corte A-A)
E_COB, H_COR, H_VIG = 0.03, 0.05, 0.075 # cobertura, correa 2" x 2" y viga
VUELO = 0.013                           # la cobertura termina sobre la cara posterior de la canaleta
YCOL = (1.81, 2.06)                     # columnas 0.10 x 0.25 (todas en la linea de la banca)
JARDIN = -0.15
FCX, FCY, ZFC = 0.20, 0.15, (-0.15, 1.05)   # falsa columna CL-01 (corte A-A: +1.05 a -0.15)
DT = T.DT
R_CODO, CAMP = 0.055, 0.045             # codo PVC 4" x 90 (radio de eje y campana)
BRIDA, DB_, LC = 0.16, 0.10, 0.15       # boquilla: brida 0.16 x 0.16, cuello Ø 0.10 x 0.15
ZH = ZB0 - 0.256                        # eje del tramo bajo la canaleta (corte A-A)
ZC_TOP, ZC_BOT = ZH + R_CODO + CAMP, ZH - R_CODO - CAMP
ZABR = 1.80                             # abrazadera a la columna
s = S_CAN / 100.0

# techos: x0, x1, borde de la canaleta (y), sentido hacia la canaleta (d), eje de la salida (xs), columnas (eje x),
# vigas (eje x) y correas (distancia al borde bajo)
TECHOS = [
    dict(n="T-1", x0=0.00, x1=3.79, borde=2.40, d=+1, xs=0.147, cols=[0.147, 3.627], vig=[0.148 + 0.873 * k for k in range(5)],
         cor=[0.369, 1.019, 1.669, 2.319]),
    dict(n="T-2", x0=3.79, x1=8.00, borde=1.212, d=-1, xs=3.939, cols=[3.939, 7.839], vig=[3.937 + 0.978 * k for k in range(5)],
         cor=[0.569, 1.019, 1.669, 2.319]),
    dict(n="T-3", x0=8.00, x1=11.79, borde=2.40, d=+1, xs=11.649, cols=[8.162, 11.649], vig=[8.150 + 0.8737 * k for k in range(5)],
         cor=[0.369, 1.019, 1.669, 2.319]),
]
FONDO = 2.40
for R in TECHOS:
    R["L"] = R["x1"] - R["x0"]
    R["sop"] = [R["x0"] + a for a in (round(0.207 * R["L"] / 0.05) * 0.05, R["L"] - round(0.207 * R["L"] / 0.05) * 0.05)]
    R["yb"] = R["borde"] + R["d"] * 0.01                  # cara posterior (interior) de la canaleta
    R["yf"] = R["yb"] + R["d"] * CB                       # cara frontal
    R["ys"] = R["yb"] + R["d"] * CB / 2                   # eje de la boquilla
    yface = YCOL[1] if R["d"] > 0 else YCOL[0]            # cara de la columna del lado de la canaleta
    R["yw"] = yface
    R["yt"] = yface + R["d"] * 0.0655                     # eje de la bajada (0.0655 de la cara de la columna)
    R["yfc"] = tuple(sorted((yface, yface + R["d"] * FCY)))
    R["ycolg"] = (R["ys"] + R["yt"]) / 2

GALV, PLAT, CAB, ROSCA, COLG = (210, 214, 222), T.PLAT, T.CAB, T.ROSCA, T.COLG
PVC, ACC, ABRZ, CONC = T.PVC, T.ACC, T.ABRZ, T.CONC
METAL, PISO, TIERRA = (120, 128, 140), (224, 222, 214), (206, 222, 184)


def zc(R, x):
    return ZB0 + s * abs(x - R["xs"])


def dist(R, y):
    """Distancia horizontal desde el borde bajo (canaleta) hacia el interior del techo."""
    return (R["borde"] - y) * R["d"]


def zcob(R, y):
    return Z_COB + PEND * dist(R, y)


def zvig(R, y):
    return zcob(R, y) - E_COB - H_COR                      # cara superior de las vigas


def yr(R):
    """Extremos en y del techo (lado alto, lado de la canaleta)."""
    return R["borde"] - R["d"] * FONDO, R["borde"] + R["d"] * VUELO


def caja(E, x0, y0, z0, x1, y1, z1, rgb, paso=0.05):
    E.caja(min(x0, x1), min(y0, y1), min(z0, z1), max(x0, x1), max(y0, y1), max(z0, z1), rgb, paso)


# ================================================================== modelo 3D
def tubo(E, a, b):
    E.cilindro(a, b, DT / 2, PVC, n=20, paso=0.10)


def boquilla(E, x, y, z):
    """Boquilla de plancha galvanizada e = 0.50 mm: abertura Ø 0.10, brida 0.16 x 0.16 con 8 remaches, cuello Ø 0.10 x 0.15."""
    E.disco((x, y, z + 0.0005), (0, 0, 1), DB_ / 2, (70, 74, 80), n=24, sesgo=0.02)
    d = BRIDA / 2 - 0.015
    for dx, dy in ((-d, -d), (0, -d), (d, -d), (-d, 0), (d, 0), (-d, d), (0, d), (d, d)):
        E.disco((x + dx, y + dy, z + 0.0006), (0, 0, 1), 0.0032, T.REM, sesgo=0.02)
    E.g = 1
    h = BRIDA / 2
    E.quad((x - h, y - h, z - 0.0012), (x + h, y - h, z - 0.0012), (x + h, y + h, z - 0.0012), (x - h, y + h, z - 0.0012), GALV, 0.05)
    E.cilindro((x, y, z - 0.0012), (x, y, z - LC), DB_ / 2, GALV, n=24, tapas=False, paso=0.05)


def canaleta(E, R, xa=None, xb=None):
    Q = E.quad; d = R["d"]; yb, yf = R["yb"], R["yf"]
    xa = R["x0"] if xa is None else xa; xb = R["x1"] if xb is None else xb
    tramos = [(a, b) for a, b in ((xa, min(R["xs"], xb)), (max(R["xs"], xa), xb)) if b - a > 1e-6]
    z = lambda x: zc(R, x)
    E.g = 5
    for a, b in tramos:
        Q((a, yb, z(a)), (b, yb, z(b)), (b, yb, z(b) + CH), (a, yb, z(a) + CH), GALV, 0.08)                         # cara posterior
        Q((a, yb, z(a) + CH), (b, yb, z(b) + CH), (b, yb - d * ALA, z(b) + CH + 0.012), (a, yb - d * ALA, z(a) + CH + 0.012), GALV, 0.08)
        Q((a, yb, z(a)), (b, yb, z(b)), (b, yf, z(b)), (a, yf, z(a)), GALV, 0.08)                                   # fondo
    E.g = 7
    for a, b in tramos:
        Q((a, yf, z(a)), (b, yf, z(b)), (b, yf, z(b) + CH), (a, yf, z(a) + CH), GALV, 0.08)                         # cara frontal
        Q((a, yf - d * 0.015, z(a) + CH), (b, yf - d * 0.015, z(b) + CH), (b, yf, z(b) + CH), (a, yf, z(a) + CH), GALV, 0.08)
    for xt in (xa, xb):
        if abs(xt - R["x0"]) < 1e-6 or abs(xt - R["x1"]) < 1e-6:                                                    # tapas
            E.cara([(xt, yb, z(xt)), (xt, yf, z(xt)), (xt, yf, z(xt) + CH), (xt, yb, z(xt) + CH)], (232, 235, 240))
    w, ep = T.ANP / 2, T.EPL
    for xs in R["sop"]:
        if not (xa <= xs <= xb): continue
        zz = z(xs)
        E.g = 4; caja(E, xs - w, yb - d * ep, zz - ep, xs + w, yf + d * ep, zz, PLAT, 0.03)
        caja(E, xs - w, yb - d * ep, zz - ep, xs + w, yb, zz + CH, PLAT, 0.03)
        E.g = 8; caja(E, xs - w, yf, zz - ep, xs + w, yf + d * ep, zz + CH, PLAT, 0.03)
        caja(E, xs - w, yf - d * 0.03, zz + CH, xs + w, yf + d * ep, zz + CH + ep, PLAT, 0.03)
    if xa <= R["xs"] <= xb:
        E.g = 6; boquilla(E, R["xs"], R["ys"], zc(R, R["xs"]))


def abrazadera(E, z, x, yw, yt):
    """Abrazadera de platina F°G° 1" x 1/8" sobre la bajada (x, yt), fijada a la cara y = yw de la columna."""
    r = DT / 2; h = T.ANP / 2; e = T.EPL; sg_y = 1 if yt > yw else -1
    E.cilindro((x, yt, z - h), (x, yt, z + h), r + 0.004, ABRZ, n=20, tapas=False)
    for sg in (-1, 1):
        caja(E, x + sg * (r + 0.004), yw + sg_y * e, z - h, x + sg * (r + 0.004 + e), yt, z + h, ABRZ, 0.05)
        caja(E, x + sg * (r + 0.004), yw, z - h, x + sg * 0.05, yw + sg_y * e, z + h, ABRZ, 0.05)
        E.prisma_hex((x + sg * 0.045, yw + sg_y * e, z), (0, sg_y, 0), 0.0111, 0.0043, CAB)


def colgador(E, x, y, zt, z_viga):
    r = DT / 2
    E.cilindro((x, y, zt + r + 0.008), (x, y, z_viga), 0.0048, ROSCA, n=8, paso=0.08, anillos=0.004)
    for zz in (zt + r + 0.008, zt + r + 0.020, z_viga - 0.008):
        E.prisma_hex((x, y, zz), (0, 0, 1), 0.0143, 0.008, CAB)
    E.cilindro((x, y - 0.025, zt), (x, y + 0.025, zt), r + 0.006, COLG, n=20, tapas=False)
    E.caja(x - 0.006, y - 0.025, zt + r + 0.002, x + 0.006, y + 0.025, zt + r + 0.010, COLG, 0.05)


def bajada(E, R, z_min=None):
    x, ys, yt = R["xs"], R["ys"], R["yt"]; h = 1 if yt > ys else -1; r = R_CODO + CAMP
    E.g = 3
    tubo(E, (x, ys, zc(R, x) - 0.010), (x, ys, ZC_TOP))                                    # niple con el cuello de la boquilla
    E.codo((x, ys, ZH), (0, 0, -1), (0, h, 0), R_CODO, DT / 2, ACC, campana=CAMP)
    tubo(E, (x, ys + h * r, ZH), (x, yt - h * r, ZH))                                        # tramo bajo la canaleta
    E.codo((x, yt, ZH), (0, h, 0), (0, 0, -1), R_CODO, DT / 2, ACC, campana=CAMP)
    zfin = ZFC[1] if z_min is None else max(z_min, ZFC[1])
    tubo(E, (x, yt, ZC_BOT), (x, yt, zfin))                                                  # bajada adosada a la columna
    if z_min is None:
        E.g = 1; tubo(E, (x, yt, ZFC[1]), (x, yt, ZFC[0]))                                   # dentro de la falsa columna
        E.g = 2; caja(E, x - FCX / 2, R["yfc"][0], ZFC[0], x + FCX / 2, R["yfc"][1], ZFC[1], CONC, paso=0.12)
    E.g = 9
    if z_min is None or ZABR > z_min:
        abrazadera(E, ZABR, x, R["yw"], yt)
    colgador(E, x, R["ycolg"], ZH, zvig(R, R["ycolg"]) - H_VIG)


def estructura(E, R, xr=None, zmin=JARDIN, ylim=None):
    """Columnas 0.10 x 0.25, vigas a lo largo de la pendiente y correas 2" x 2" bajo la cobertura (ylim: recorte en y)."""
    xr = xr or (R["x0"], R["x1"]); ya, yc = yr(R)
    if ylim: ya = max(ya, ylim) if R["d"] > 0 else min(ya, ylim)
    E.g = 2
    for xc in R["cols"]:
        if xr[0] - 0.06 <= xc <= xr[1] + 0.06:
            ym = (YCOL[0] + YCOL[1]) / 2
            caja(E, xc - 0.05, YCOL[0], zmin, xc + 0.05, YCOL[1], zvig(R, ym) - H_VIG, METAL, paso=0.40)
    for xv in R["vig"]:
        if xr[0] <= xv <= xr[1]:
            y0, y1 = ya, R["borde"]
            E.quad((xv - 0.0375, y0, zvig(R, y0)), (xv + 0.0375, y0, zvig(R, y0)), (xv + 0.0375, y1, zvig(R, y1)), (xv - 0.0375, y1, zvig(R, y1)), METAL, 0.40)
            E.quad((xv + 0.0375, y0, zvig(R, y0) - H_VIG), (xv + 0.0375, y1, zvig(R, y1) - H_VIG), (xv + 0.0375, y1, zvig(R, y1)), (xv + 0.0375, y0, zvig(R, y0)), METAL, 0.40)
    for c in R["cor"]:
        y = R["borde"] - R["d"] * c
        if ylim and (y - ya) * R["d"] < 0: continue
        z = zvig(R, y)
        caja(E, xr[0], y - 0.025, z, xr[1], y + 0.025, z + H_COR, METAL, paso=0.40)


def cobertura(E, R, xr=None, n=None, ylim=None):
    xr = xr or (R["x0"], R["x1"]); y0, y1 = yr(R)
    if ylim: y0 = ylim
    n = n or max(2, int(round((xr[1] - xr[0]) / 0.40)))
    E.g = 10
    E.quad((xr[0], y0, zcob(R, y0)), (xr[1], y0, zcob(R, y0)), (xr[1], y1, zcob(R, y1)), (xr[0], y1, zcob(R, y1)), (0, 0, 0), 3.0, relleno=False)
    for k in range(1, n):
        x = xr[0] + (xr[1] - xr[0]) * k / n
        E.cara([(x, y0, zcob(R, y0)), (x, y1, zcob(R, y1))], (0, 0, 0), [True, False], relleno=False)


def escena_general():
    E = Escena(); Q = E.quad
    E.g = 0
    X0, X1 = -0.30, 12.09
    Q((X0, -0.40, 0.0), (X1, -0.40, 0.0), (X1, 1.55, 0.0), (X0, 1.55, 0.0), PISO, 0.80)                 # circulacion
    Q((X0, 1.55, JARDIN), (X1, 1.55, JARDIN), (X1, 2.35, JARDIN), (X0, 2.35, JARDIN), TIERRA, 0.80)      # jardinera
    Q((X0, 1.55, JARDIN), (X1, 1.55, JARDIN), (X1, 1.55, 0.0), (X0, 1.55, 0.0), PISO, 0.80)
    Q((X0, 2.35, 0.0), (X1, 2.35, 0.0), (X1, 3.95, 0.0), (X0, 3.95, 0.0), PISO, 0.80)
    for R in TECHOS:
        bajada(E, R)
    for R in TECHOS:
        estructura(E, R)
    for R in TECHOS:
        canaleta(E, R)
    for R in TECHOS:
        cobertura(E, R)
    return E


LEYENDA = [(GALV, "Canaleta, tapas y boquilla de plancha galvanizada e = 0.50 mm"),
           (PLAT, "Soporte (sujetador) de platina F°G° 1\" x 1/8\" - 2 por canaleta"),
           (PVC, "Tubo PVC 4\" (niple, tramo bajo la canaleta y bajada)"), (ACC, "Codos PVC 4\" x 90° con campanas (2 por salida)"),
           (COLG, "Colgador F°G° con varilla roscada 3/8\" a la viga"), (ABRZ, "Abrazadera F°G° 1\" x 1/8\" a la columna"),
           (CONC, "Falsa columna de drenaje pluvial CL-01"), (METAL, "Estructura metalica de la pergola (columnas, vigas y correas)")]


def planta_techos(lam, xmm, ymm, esc=50):
    """Planta de techos a 1/50 dentro de la lamina: canaletas, boquillas, soportes y sentido del flujo."""
    f = 1000.0 / esc
    p = lambda x, y: lam.P(xmm + x * f, ymm + y * f)
    for R in TECHOS:
        ya, yc = yr(R)
        y_lo, y_hi = min(ya, R["borde"]), max(ya, R["borde"])
        lam.poli([p(R["x0"], y_lo), p(R["x1"], y_lo), p(R["x1"], y_hi), p(R["x0"], y_hi)], "COBERTURA", cerrada=True)
        for xv in R["vig"]:
            lam.linea(p(xv, y_lo), p(xv, y_hi), "ARQ-BASE")
        y_o = R["borde"] + R["d"] * (0.01 + CB + 0.002)
        pts = [p(R["x0"], R["borde"]), p(R["x1"], R["borde"]), p(R["x1"], y_o), p(R["x0"], y_o)]
        lam.relleno(pts, "GALV-RELL"); lam.poli(pts, "PLANCHA-GALV", cerrada=True)
        for xs in R["sop"]:
            lam.linea(p(xs, R["borde"]), p(xs, y_o), "PLATINA")
        lam.circulo(p(R["xs"], R["ys"]), DB_ / 2 * f * lam.esc / 1000, "PLANCHA-GALV")          # radio en el modelo de la lamina
        lam.rect(*p(R["xs"] - BRIDA / 2, R["ys"] - BRIDA / 2), *p(R["xs"] + BRIDA / 2, R["ys"] + BRIDA / 2), "PLANCHA-GALV")
        for xc in R["cols"]:
            lam.relleno([p(xc - 0.05, YCOL[0]), p(xc + 0.05, YCOL[0]), p(xc + 0.05, YCOL[1]), p(xc - 0.05, YCOL[1])], "METAL-RELL")
        # flujo hacia la boquilla
        xm = (R["x0"] + R["x1"]) / 2
        a, b = (xm + 0.6, xm - 0.6) if R["xs"] < xm else (xm - 0.6, xm + 0.6)
        lam.flecha(p(a, y_o + R["d"] * 0.16), p(b, y_o + R["d"] * 0.16), "FLUJO", 2.2)
        lam.texto(p(xm, y_o + R["d"] * (0.30 if R["d"] > 0 else 0.42)), "CANALETA %s  L = %.2f  S = 0.5 %%" % (R["n"], R["L"]), 1.8, "TEXTOS", TA.MIDDLE_CENTER)
        lam.texto(p(R["xs"], R["ys"] - R["d"] * 0.45), "BOQUILLA Ø 4\"", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
        ym = (y_lo + y_hi) / 2
        lam.texto(p(xm, ym), "COBERTURA ALUZINC e = 0.35 mm, S = 10 %", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(xmm + 118, ymm - 14, "PLANTA DE TECHOS OC-01", "ESC. 1/50 - la cupula del plano se reemplaza por boquilla Ø 4\"", 120)


def do01(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 30, "DO-01", "ISOMETRICO DEL DRENAJE PLUVIAL DE LA OC-01 (JARDINERA + BANCA + PERGOLA)",
                   "TRES TECHOS: CANALETAS 0.18 x 0.21 DE PLANCHA GALVANIZADA, BOQUILLAS 4\" Y BAJADAS PVC 4\" - " + P["nombre"])
    E = escena_general()
    P2 = E.dibujar(lam, 270, 330)
    R1, R2, R3 = TECHOS
    items = [((1.60, 0.70, zcob(R1, 0.70)), ["Cobertura de panel metalico aluzinc e = 0.35 mm, S = 10 % (solo contorno)"]),
             ((2.00, R1["yf"], zc(R1, 2.00) + 0.15), ["Canaleta T-1 de plancha galvanizada e = 0.50 mm, 0.18 x 0.21, L = 3.79 m, S = 0.5 %"]),
             ((R1["sop"][1], R1["yf"], zc(R1, R1["sop"][1]) + 0.10), ["2 soportes de platina F°G° 1\" x 1/8\" por canaleta"]),
             ((R1["xs"], R1["ys"], zc(R1, R1["xs"])), ["Boquilla Ø 4\" (reemplaza al sumidero tipo cupula)"]),
             ((R1["x0"], R1["ys"], zc(R1, R1["x0"]) + 0.10), ["Tapa de plancha galvanizada en cada extremo"]),
             ((R1["xs"], R1["yt"], 1.50), ["Bajada PVC 4\" adosada a la columna, con abrazadera F°G°"]),
             ((R1["xs"] + FCX / 2, R1["yfc"][1], 0.50), ["Falsa columna de drenaje pluvial CL-01 (+1.05 a -0.15)"]),
             ((6.00, R2["yf"], zc(R2, 6.00) + 0.10), ["Canaleta T-2 (techo central, lado sur), L = 4.21 m, S = 0.5 %"]),
             ((R2["xs"], R2["ycolg"], ZH + 0.06), ["Colgador F°G° con varilla roscada 3/8\" a la viga"]),
             ((R2["xs"], R2["yt"], 1.40), ["Codos PVC 4\" x 90° y bajada del techo central"]),
             ((10.00, R3["yf"], zc(R3, 10.00) + 0.15), ["Canaleta T-3, L = 3.79 m, S = 0.5 %; boquilla en el extremo derecho"]),
             ((9.00, 2.00, 0.0), ["Jardinera (-0.15) y circulacion (+0.00)"])]
    T._llamadas(lam, P2, items, 620, hmm=1.9)
    lam.titulo_vista(240, 60, "ISOMETRICO GENERAL DE LA OC-01", "ESC. 1/30 - canaletas, boquillas y bajadas de los tres techos", 170)
    T.leyenda_colores(lam, 600, 560, LEYENDA)
    planta_techos(lam, 30, 470)
    lam.notas(35, 235, "NOTAS", [
        "1. Medidas del plano OC-01 (planta de techos, corte A-A y elevacion E1). Canaleta 0.18 de ancho x 0.21 de alto interiores.",
        "2. Canaleta, tapas y boquilla de plancha galvanizada e = 0.50 mm; un tramo por techo (3.79, 4.21 y 3.79 m), S = 0.5 % hacia la boquilla.",
        "3. 2 soportes (sujetadores) de platina por canaleta, a 0.80 m (T-1, T-3) y 0.85 m (T-2) de cada extremo.",
        "4. El sumidero tipo cupula del plano se reemplaza por boquilla de plancha Ø 4\". Detalle de la salida en DO-02.",
    ], hmm=1.7, ancho_mm=165)
    return lam


# ================================================================== DO-02 (1/5)
def escena_salida():
    R = TECHOS[0]; x0, x1 = R["x0"], 0.95
    E = Escena()
    estructura(E, R, xr=(x0, x1), zmin=1.70, ylim=1.60)
    canaleta(E, R, x0, x1)
    bajada(E, R, z_min=1.70)
    cobertura(E, R, xr=(x0, x1), n=3, ylim=1.60)
    return E


def seccion_canaleta(lam, xmm, ymm):
    R = TECHOS[0]; O = lam.P(xmm, ymm); yb, yf = R["yb"], R["yf"]; ZB = ZB0
    p = lambda y, z: (O[0] + (y - yb), O[1] + (z - ZB))
    lam.relleno([p(yb, ZB), p(yf, ZB), p(yf, ZB + CH), p(yb, ZB + CH)], "GALV-RELL")
    lam.poli([p(yb - ALA, ZB + CH + 0.012), p(yb, ZB + CH), p(yb, ZB), p(yf, ZB), p(yf, ZB + CH), p(yf - 0.015, ZB + CH)], "PLANCHA-GALV", ancho=0.002)
    ep = T.EPL
    lam.poli([p(yb - ep, ZB + CH), p(yb - ep, ZB - ep), p(yf + ep, ZB - ep), p(yf + ep, ZB + CH + ep), p(yf - 0.03, ZB + CH + ep)], "PLATINA")
    yc = R["ys"]
    for dy in (-DT / 2, DT / 2): lam.linea(p(yc + dy, ZB), p(yc + dy, ZC_TOP), "TUBO-PVC")
    for dy in (-DB_ / 2, DB_ / 2): lam.linea(p(yc + dy, ZB), p(yc + dy, ZB - LC), "TUBERIA-OCULTA")
    lam.poli([p(yc - BRIDA / 2, ZB - 0.003), p(yc + BRIDA / 2, ZB - 0.003)], "PLANCHA-GALV", ancho=0.003)
    ya = yb - 0.25
    lam.poli([p(ya, zcob(R, ya)), p(R["borde"] + VUELO, zcob(R, R["borde"] + VUELO)), p(R["borde"] + VUELO, zcob(R, R["borde"] + VUELO) - E_COB),
              p(ya, zcob(R, ya) - E_COB)], "COBERTURA")
    lam.poli([p(ya, zvig(R, ya)), p(R["borde"], zvig(R, R["borde"])), p(R["borde"], zvig(R, R["borde"]) - H_VIG), p(ya, zvig(R, ya) - H_VIG)], "ESTRUCTURA-METALICA")
    lam.cota(p(yb, ZB - 0.06), p(yf, ZB - 0.06), 6, True, "0.18")
    lam.cota(p(yf, ZB), p(yf, ZB + CH), 10, False, "0.21")
    lam.cota(p(yb - ALA, ZB + CH + 0.012), p(yb, ZB + CH + 0.012), 14, True, "0.10")
    xt = lam.P(xmm + 75, 0)[0]; lam.juntar_llamadas()
    for (y, z), txt in (((R["borde"] + 0.005, zcob(R, R["borde"] + 0.005) - 0.01), "Cobertura aluzinc e = 0.35 mm"),
                        ((yb - 0.20, zvig(R, yb - 0.20) - 0.04), "Viga metalica de la pergola"),
                        ((yb - 0.06, ZB + CH + 0.008), "Ala posterior sobre la viga (0.10)"),
                        ((yf, ZB + 0.17), "Canaleta galvanizada e = 0.50 mm, 0.18 x 0.21 (interiores)"),
                        ((yf + ep, ZB + 0.10), "Soporte de platina F°G° 1\" x 1/8\""),
                        ((yc + BRIDA / 2 - 0.01, ZB - 0.004), "Boquilla: brida 0.16 x 0.16 remachada y sellada"),
                        ((yc + DB_ / 2, ZB - 0.10), "Cuello Ø 0.10 x 0.15 dentro del niple PVC 4\"")):
        q = p(y, z); lam.llamada(q, (xt, q[1]), [txt], 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(xmm + 30, ymm - 45, "CORTE DE LA CANALETA", "ESC. 1/5 - por la boquilla (corte A-A)", 80)


def do02(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 5, "DO-02", "DETALLE ISOMETRICO DE LA SALIDA DE LA CANALETA DE LA OC-01",
                   "BOQUILLA 4\", NIPLE, CODOS, COLGADOR, ABRAZADERA Y BAJADA PVC 4\" (TIPICO DE LAS 3 SALIDAS) - " + P["nombre"])
    R = TECHOS[0]
    E = escena_salida()
    P2 = E.dibujar(lam, 752, 146)
    xs, ys, yt = R["xs"], R["ys"], R["yt"]
    items = [((0.60, 2.10, zcob(R, 2.10)), ["Cobertura de panel aluzinc (contorno)"]),
             ((0.50, R["yb"] - 0.05, zc(R, 0.70) + CH + 0.006), ["Ala posterior de la canaleta sobre la viga (0.10)"]),
             ((0.62, R["yf"], zc(R, 0.62) + 0.12), ["Canaleta de plancha galvanizada e = 0.50 mm, 0.18 x 0.21 (interiores), S = 0.5 %"]),
             ((R["sop"][0], R["yf"] + T.EPL, zc(R, R["sop"][0]) + 0.12), ["Soporte de platina F°G° 1\" x 1/8\" (2 por canaleta)"]),
             ((R["x0"], ys, zc(R, R["x0"]) + 0.10), ["Tapa de plancha galvanizada e = 0.50 mm remachada y sellada"]),
             ((xs + 0.03, ys, zc(R, xs)), ["Boquilla Ø 4\": abertura Ø 0.10, brida 0.16 x 0.16 con 8 remaches (en lugar de la cupula)"]),
             ((xs + DT / 2, ys, (ZB0 + ZC_TOP) / 2), ["Niple PVC 4\" con el cuello de la boquilla adentro"]),
             ((xs, R["ycolg"], zvig(R, R["ycolg"]) - H_VIG - 0.10), ["Colgador F°G°: varilla roscada 3/8\" con tuercas, colgada de la viga"]),
             ((xs + DT / 2 * 0.7, yt, ZH - 0.05), ["Codos PVC 4\" x 90° con campanas"]),
             ((xs + DT / 2 + 0.004, yt, ZABR), ["Abrazadera F°G° 1\" x 1/8\" con 2 pernos a la columna"]),
             ((xs + DT / 2, yt, 1.72), ["Bajada PVC 4\" (cortada): sigue a la falsa columna CL-01"]),
             ((R["cols"][0] + 0.05, YCOL[0], 1.85), ["Columna metalica de la pergola (cortada)"])]
    T._llamadas(lam, P2, items, 655)
    lam.titulo_vista(380, 118, "ISOMETRICO DE LA SALIDA (TECHO T-1)", "ESC. 1/5 - igual en T-2 (tramo bajo la canaleta 0.63) y T-3 (0.37)", 190)
    seccion_canaleta(lam, 95, 400)
    return lam


def construir():
    B.PROYECTO = P["proyecto"]; B.UBICACION = P["ubicacion"]
    doc = B.nuevo_documento()
    for n, c, lt, lw in T.CAPAS_EXTRA + CAPAS_OC:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt); ly.dxf.lineweight = lw
    laminas = {"DO-01": do01(doc, 0.0, 0.0), "DO-02": do02(doc, 30.0, 0.0)}
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: -1 for e in msp.query("HATCH SOLID")})
    L.presentaciones(doc, laminas)
    au = doc.audit(); doc.saveas(SAL)
    print("%s (%d errores de auditoria)" % (os.path.relpath(SAL, RAIZ), len(au.errors)))
    return laminas


if __name__ == "__main__":
    construir()
