"""Drenaje pluvial de la BANCA DE JARDINERIA (detalle de banca tipo 01) - CAR MUJERES (CUI 2717013).

Fiel al dibujo DETALLE_DE_BANCA_TIPO_01.dxf (planta, planta de techo, corte A-A y elevaciones E1/E2, dibujado a escala real):
todas las medidas se leen del corte A-A y de la planta; la canaleta es de 0.18 de ancho x 0.20 de alto (indicacion del proyectista).
  DB-01  isometrico de la banca con su red pluvial (1/15)
  DB-02  isometrico del extremo de la canaleta, corte de la canaleta y seccion de la falsa columna (1/5)
  DB-03  corte A-A (lateral) y corte B-B (frontal) del drenaje pluvial con cotas y niveles (1/10)
Escala real (1 unidad = 1 m). Uso: python3 herramientas/techo/planos_banca_m.py
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
sys.path.insert(0, HERR); sys.path.insert(0, AQUI)
import numpy as np
from iso3d import Escena
import dxf_base as B
import dxf_layouts as L
from ezdxf.enums import TextEntityAlignment as TA
import planos_techo as T

P = T.PROY["mujeres"]
SAL = os.path.join(RAIZ, "entregables_mujeres", "PLANOS_ISOMETRICO_BANCA_JARDINERIA_CAR_MUJERES.dxf")
for _e in (5, 10, 15):
    if _e not in B.ESCALAS: B.ESCALAS.append(_e)
CAPAS_BANCA = [("ESTRUCTURA-METALICA", 8, "CONTINUOUS", 35), ("METAL-RELL", 8, "CONTINUOUS", 13), ("MADERA", 32, "CONTINUOUS", 25),
               ("MADERA-RELL", 32, "CONTINUOUS", 13), ("JARDIN", 94, "CONTINUOUS", 25)]
B.COLOR_RGB.update({"METAL-RELL": (150, 156, 166), "MADERA-RELL": (214, 178, 132), "GALV-RELL": (226, 231, 238)})

# ------------------------------------------------------------------ geometria (m), leida del corte A-A y de la planta
# x: largo de la banca (techo 2.00, la bajada en la columna derecha); y: fondo (techo 2.40, borde bajo con la canaleta en y = 2.40)
# z: sobre el NPT 259.50 de la circulacion (NPT 262.50 = +3.00)
AX, AY = 2.00, 2.40
CB, CH = 0.18, 0.20                     # canaleta de aluzinc: ancho x alto interiores
YC0 = AY + 0.01                         # cara interior posterior de la canaleta
YC1 = YC0 + CB                          # cara interior frontal
ALA = 0.10                              # ala posterior apoyada sobre la viga, bajo la cobertura
ZB = 2.385                              # fondo de la canaleta en el sumidero
S_CAN = 0.50                            # pendiente del plano (S = 0.5 %) hacia el sumidero
VUELO = 0.013                           # la cobertura termina sobre la cara posterior de la canaleta (corte A-A)
PEND = 0.125                            # cobertura: 0.30 de caida en 2.40
Z_COB0 = 2.997                          # cara superior de la cobertura en y = 0
E_COB = 0.03
COL = [(0.25, 0.35), (1.65, 1.75)]      # columnas de tubo rectangular 4" x 10" x 3 mm (0.10 en x, 0.25 en y)
YCOL = (1.80, 2.05)
JARDIN = -0.15                          # jardin 0.15 bajo la circulacion
XS = 1.70                               # eje del sumidero y de la bajada (eje de la columna derecha)
FCX, FCY = 0.20, 0.15                   # falsa columna CL-01 (planta): 0.20 x 0.15
YFC = (YCOL[1], YCOL[1] + FCY)          # contra la cara de la columna, del lado de la canaleta
ZFC = (JARDIN, 1.05)                    # dibujada de -0.15 a +1.05 (corte A-A y elevacion E2)
YT = YCOL[1] + 0.0655                   # eje de la bajada (planta: 0.0655 desde la cara de la columna)
YSUM = (YC0 + YC1) / 2                  # eje del sumidero
ZH = 2.129                              # eje del tramo horizontal bajo la canaleta
R_CODO, CAMP = 0.055, 0.045             # codo PVC 4" x 90 (radio de eje y campana): 0.10 del eje al extremo
UN = (0.063, 0.051)                     # union PVC 4": radio exterior y largo
Z_UN1 = 2.233                           # union bajo el sumidero (2.233 a 2.284)
Z_UN2 = 2.029                           # union bajo el segundo codo (1.973 a 2.024)
Y_COLG = AY - 0.088                     # colgador sobre el tramo horizontal
ZABR = 1.77                             # abrazadera a la columna
DT = T.DT                               # PVC 4": diametro exterior 0.114
SOPS = [0.10, 0.70, 1.30, 1.90]         # soportes de platina @0.60
SEAT = (1.194, YCOL[0], 0.45, 0.50)     # asiento: y0, y1, z0, z1 (0.606 de fondo; +0.50)
LISTONES = [0.58 + 0.30 * k for k in range(6)]   # celosia (elevacion E2): listones de 0.20 @0.30
s = S_CAN / 100.0
zc = lambda x: ZB + s * abs(XS - x)
zcob = lambda y: Z_COB0 - PEND * y
zvig = lambda y: Z_COB0 - E_COB - 0.076 - PEND * y      # cara superior de la viga 2" x 2" (2.59 en el borde)

ALUZ, PLAT, CAB, ROSCA, COLG = (204, 210, 218), T.PLAT, T.CAB, T.ROSCA, T.COLG
PVC, ACC, ABRZ, CONC = T.PVC, T.ACC, T.ABRZ, T.CONC
METAL, MADERA, PISO, TIERRA, CUPULA, UNION = (120, 128, 140), (196, 150, 98), (224, 222, 214), (206, 222, 184), (90, 96, 104), (96, 140, 210)


# ================================================================== modelo 3D
def tubo(E, a, b):
    E.cilindro(a, b, DT / 2, PVC, n=20, paso=0.10)


def union3d(E, z, x, y):
    E.cilindro((x, y, z), (x, y, z + UN[1]), UN[0], UNION, n=20, tapas=False, paso=1.0)


def abrazadera(E, z, x, yw, yt):
    """Abrazadera de platina F°G° 1" x 1/8" sobre el tubo vertical (x, yt) fijada a la cara y = yw de la columna."""
    r = DT / 2; h = T.ANP / 2; e = T.EPL
    E.cilindro((x, yt, z - h), (x, yt, z + h), r + 0.004, ABRZ, n=20, tapas=False)
    for sg in (-1, 1):
        x1, x2 = sorted((x + sg * (r + 0.004), x + sg * (r + 0.004 + e)))
        E.caja(x1, yw + e, z - h, x2, yt, z + h, ABRZ, 0.05)
        x3, x4 = sorted((x + sg * (r + 0.004), x + sg * 0.05))
        E.caja(x3, yw, z - h, x4, yw + e, z + h, ABRZ, 0.05)
        E.prisma_hex((x + sg * 0.045, yw + e, z), (0, 1, 0), 0.0111, 0.0043, CAB)


def colgador(E, x, y, zt, z_viga):
    """Colgador del corte A-A: banda de F°G° sobre el tubo, varilla roscada 3/8" con tuerca y contratuerca hasta la viga."""
    r = DT / 2
    E.cilindro((x, y, zt + r + 0.008), (x, y, z_viga), 0.0048, ROSCA, n=8, paso=0.08, anillos=0.004)
    E.prisma_hex((x, y, zt + r + 0.008), (0, 0, 1), 0.0143, 0.008, CAB)
    E.prisma_hex((x, y, zt + r + 0.020), (0, 0, 1), 0.0143, 0.008, CAB)
    E.prisma_hex((x, y, z_viga - 0.008), (0, 0, 1), 0.0143, 0.008, CAB)
    E.cilindro((x, y - 0.025, zt), (x, y + 0.025, zt), r + 0.006, COLG, n=20, tapas=False)
    E.caja(x - 0.006, y - 0.025, zt + r + 0.002, x + 0.006, y + 0.025, zt + r + 0.010, COLG, 0.05)


def cupula(E, x, y, z):
    r0 = 0.052
    E.cilindro((x, y, z), (x, y, z + 0.008), r0 + 0.012, CUPULA, n=24, tapas=True, paso=1.0)
    for k in range(10):
        a = 2 * np.pi * k / 10
        E.cilindro((x + r0 * np.cos(a), y + r0 * np.sin(a), z + 0.008), (x + 0.02 * np.cos(a), y + 0.02 * np.sin(a), z + 0.075),
                   0.0035, CUPULA, n=6, tapas=False, paso=1.0)
    E.disco((x, y, z + 0.075), (0, 0, 1), 0.024, CUPULA, n=16)
    for zz, rr in ((0.03, 0.044), (0.055, 0.031)):
        E.cilindro((x, y, z + zz), (x, y, z + zz + 0.004), rr, CUPULA, n=20, tapas=False, paso=1.0)


def canaleta(E, x0=0.0, x1=AX):
    Q = E.quad
    tramos = [(a, b) for a, b in ((x0, min(XS, x1)), (max(XS, x0), x1)) if b - a > 1e-6]
    E.g = 5
    for a, b in tramos:
        Q((a, YC0, zc(a)), (b, YC0, zc(b)), (b, YC0, zc(b) + CH), (a, YC0, zc(a) + CH), ALUZ, 0.06)                 # cara posterior
        Q((a, YC0, zc(a) + CH), (b, YC0, zc(b) + CH), (b, YC0 - ALA, zc(b) + CH + 0.012), (a, YC0 - ALA, zc(a) + CH + 0.012), ALUZ, 0.06)
        Q((a, YC0, zc(a)), (b, YC0, zc(b)), (b, YC1, zc(b)), (a, YC1, zc(a)), ALUZ, 0.06)                           # fondo
    E.g = 7
    for a, b in tramos:
        Q((a, YC1, zc(a)), (b, YC1, zc(b)), (b, YC1, zc(b) + CH), (a, YC1, zc(a) + CH), ALUZ, 0.06)                 # cara frontal
        Q((a, YC1 - 0.015, zc(a) + CH), (b, YC1 - 0.015, zc(b) + CH), (b, YC1, zc(b) + CH), (a, YC1, zc(a) + CH), ALUZ, 0.06)
    for xt in (x0, x1):
        if xt in (0.0, AX):
            E.cara([(xt, YC0, zc(xt)), (xt, YC1, zc(xt)), (xt, YC1, zc(xt) + CH), (xt, YC0, zc(xt) + CH)], (226, 230, 236))
    for xs in SOPS:
        if not (x0 <= xs <= x1): continue
        z = zc(xs); w = T.ANP / 2; ep = T.EPL
        E.g = 4; E.caja(xs - w, YC0 - ep, z - ep, xs + w, YC1 + ep, z, PLAT, 0.03)
        E.caja(xs - w, YC0 - ep, z - ep, xs + w, YC0, z + CH, PLAT, 0.03)
        E.g = 8; E.caja(xs - w, YC1, z - ep, xs + w, YC1 + ep, z + CH, PLAT, 0.03)
        E.caja(xs - w, YC1 - 0.03, z + CH, xs + w, YC1 + ep, z + CH + ep, PLAT, 0.03)
    E.g = 6
    cupula(E, XS, YSUM, zc(XS) + 0.0006)


def bajada(E, z_min=None):
    r = R_CODO + CAMP
    E.g = 3
    tubo(E, (XS, YSUM, zc(XS) - 0.010), (XS, YSUM, Z_UN1 + UN[1]))                     # niple del sumidero
    union3d(E, Z_UN1, XS, YSUM)
    E.codo((XS, YSUM, ZH), (0, 0, -1), (0, -1, 0), R_CODO, DT / 2, ACC, campana=CAMP)
    tubo(E, (XS, YSUM - r, ZH), (XS, YT + r, ZH))                                       # tramo bajo la canaleta
    E.codo((XS, YT, ZH), (0, -1, 0), (0, 0, -1), R_CODO, DT / 2, ACC, campana=CAMP)
    union3d(E, Z_UN2 - UN[1], XS, YT)
    zfin = ZFC[1] if z_min is None else max(z_min, ZFC[1])
    tubo(E, (XS, YT, Z_UN2 - UN[1]), (XS, YT, zfin))                                     # bajada vista
    if z_min is None:
        E.g = 1; tubo(E, (XS, YT, ZFC[1]), (XS, YT, ZFC[0]))                             # dentro de la falsa columna
    E.g = 9
    if (z_min is None) or ZABR > z_min: abrazadera(E, ZABR, XS, YCOL[1], YT)
    colgador(E, XS, Y_COLG, ZH, zvig(Y_COLG) - 0.05)


def estructura(E, xr=(0.0, AX), yr=(0.0, AY), zmin=JARDIN, seat=True):
    E.g = 2
    for xa, xb in COL:
        if xb < xr[0] or xa > xr[1]: continue
        E.caja(xa, YCOL[0], zmin, xb, YCOL[1], zvig((YCOL[0] + YCOL[1]) / 2) - 0.05, METAL, paso=0.30)
        if seat:
            xm = (xa + xb) / 2
            E.caja(xm - 0.025, SEAT[0], SEAT[2] - 0.075, xm + 0.025, YCOL[0], SEAT[2], METAL, paso=0.20)
    if seat:
        E.caja(COL[0][1], SEAT[0], SEAT[2], COL[1][0], SEAT[1], SEAT[3], MADERA, paso=0.20)
        for z0 in LISTONES:
            E.caja(COL[0][1], 1.90, z0, COL[1][0], 1.95, z0 + 0.20, MADERA, paso=0.25)
    for xa, xb in COL:
        xm = (xa + xb) / 2
        if xm < xr[0] or xm > xr[1]: continue
        y0, y1 = yr
        E.quad((xm - 0.025, y0, zvig(y0)), (xm + 0.025, y0, zvig(y0)), (xm + 0.025, y1, zvig(y1)), (xm - 0.025, y1, zvig(y1)), METAL, 0.30)
        E.quad((xm + 0.025, y0, zvig(y0) - 0.05), (xm + 0.025, y1, zvig(y1) - 0.05), (xm + 0.025, y1, zvig(y1)), (xm + 0.025, y0, zvig(y0)), METAL, 0.30)
    for yc in (0.05, 0.85, 1.65, AY - 0.05):
        if yr[0] <= yc <= yr[1]:
            z = zvig(yc); E.caja(xr[0], yc - 0.025, z, xr[1], yc + 0.025, z + 0.076, METAL, paso=0.30)


def cobertura(E, xr=(0.0, AX), y0=0.0, n=10):
    E.g = 10; y1 = AY + VUELO
    E.quad((xr[0], y0, zcob(y0)), (xr[1], y0, zcob(y0)), (xr[1], y1, zcob(y1)), (xr[0], y1, zcob(y1)), (0, 0, 0), 3.0, relleno=False)
    for k in range(1, n):
        x = xr[0] + (xr[1] - xr[0]) * k / n
        E.cara([(x, y0, zcob(y0)), (x, y1, zcob(y1))], (0, 0, 0), [True, False], relleno=False)


def escena_banca():
    E = Escena(); Q = E.quad
    E.g = 0
    Q((-0.30, -0.45, 0.0), (AX + 0.30, -0.45, 0.0), (AX + 0.30, YCOL[0], 0.0), (-0.30, YCOL[0], 0.0), PISO, 0.40)
    Q((-0.30, YCOL[0], JARDIN), (AX + 0.30, YCOL[0], JARDIN), (AX + 0.30, AY + 0.65, JARDIN), (-0.30, AY + 0.65, JARDIN), TIERRA, 0.40)
    Q((-0.30, YCOL[0], JARDIN), (AX + 0.30, YCOL[0], JARDIN), (AX + 0.30, YCOL[0], 0.0), (-0.30, YCOL[0], 0.0), PISO, 0.40)
    bajada(E)
    E.g = 2
    E.caja(XS - FCX / 2, YFC[0], ZFC[0], XS + FCX / 2, YFC[1], ZFC[1], CONC, paso=0.12)
    estructura(E)
    canaleta(E)
    cobertura(E)
    return E


LEYENDA = [(ALUZ, "Canaleta de aluzinc 0.18 x 0.20 (ancho x alto interiores)"), (CUPULA, "Sumidero tipo cupula 4\""),
           (PVC, "Tubo PVC 4\" (niple, tramo bajo la canaleta y bajada)"), (ACC, "Codos PVC 4\" x 90° con campanas (2)"),
           (UNION, "Uniones PVC 4\" (2)"), (COLG, "Colgador F°G° con varilla roscada 3/8\" a la viga"),
           (ABRZ, "Abrazadera F°G° 1\" x 1/8\" a la columna"), (PLAT, "Soporte de platina F°G° 1\" x 1/8\" @0.60"),
           (CONC, "Falsa columna de drenaje pluvial CL-01"), (METAL, "Estructura metalica de la banca"),
           (MADERA, "Asiento y celosia de madera")]


def db01(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 15, "DB-01", "ISOMETRICO DEL DRENAJE PLUVIAL DE LA BANCA DE JARDINERIA",
                   "BANCA TIPO 01: CANALETA, SUMIDERO CUPULA 4\", COLGADOR, BAJADA PVC 4\" Y FALSA COLUMNA CL-01 - " + P["nombre"])
    E = escena_banca()
    P2 = E.dibujar(lam, 245, 335)
    items = [((0.60, 0.80, zcob(0.80)), ["Cobertura de panel metalico aluzinc e = 0.35 mm, A = 1 m (solo contorno)"]),
             ((0.80, 1.65, zvig(1.65) + 0.076), ["Correa metalica: tubo rectangular 2\" x 3\" x 3 mm"]),
             ((0.80, YC1, zc(0.80) + 0.12), ["Canaleta de aluzinc 0.18 x 0.20 (ancho x alto interiores), L = 2.00 m, S = 0.5 %"]),
             ((SOPS[2], YC1 + T.EPL, zc(SOPS[2]) + 0.08), ["Soporte de platina F°G° 1\" x 1/8\" @0.60 (4 soportes)"]),
             ((XS, YSUM, zc(XS) + 0.06), ["Sumidero tipo cupula 4\" en el fondo de la canaleta"]),
             ((XS, Y_COLG, ZH + 0.15), ["Colgador F°G° con varilla roscada 3/8\" a la viga metalica 2\" x 2\""]),
             ((XS, (YSUM + YT) / 2 - 0.05, ZH - DT / 2), ["Codos PVC 4\" x 90°, uniones y tramo bajo la canaleta"]),
             ((XS + DT / 2, YT, ZABR + 0.02), ["Abrazadera F°G° 1\" x 1/8\" fijada a la columna"]),
             ((XS + DT / 2, YT, 1.40), ["Bajada PVC 4\" adosada a la columna metalica 4\" x 10\" x 3 mm"]),
             ((XS + FCX / 2, YFC[1], 0.55), ["Falsa columna de drenaje pluvial CL-01 de 0.20 x 0.15 (de -0.15 a +1.05)"]),
             ((0.80, SEAT[0], SEAT[3]), ["Asiento de madera sobre tubo rectangular 2\" x 3\" x 3 mm"]),
             ((0.80, 1.90, LISTONES[3] + 0.10), ["Celosia de madera"]),
             ((1.00, AY + 0.50, JARDIN), ["Jardin (0.15 bajo la circulacion)"])]
    T._llamadas(lam, P2, items, 420)
    lam.titulo_vista(250, 52, "ISOMETRICO DE LA BANCA DE JARDINERIA TIPO 01", "ESC. 1/15 - se mira desde el jardin; la cobertura se dibuja solo en contorno", 170)
    T.leyenda_colores(lam, 640, 560, LEYENDA)
    lam.notas(640, 455, "NOTAS", [
        "1. Medidas del detalle de banca tipo 01 (planta, planta de techo, corte A-A y elevaciones E1 y E2).",
        "2. Canaleta de aluzinc de 0.18 de ancho x 0.20 de alto interiores, del largo del techo (2.00 m), S = 0.5 %.",
        "3. Recorrido de la bajada segun el corte A-A: sumidero cupula, union, codo, tramo con colgador, codo, union y bajada.",
        "4. Cortes A-A y B-B con cotas y niveles en la lamina DB-03; extremo de la canaleta en DB-02.",
    ], hmm=1.8, ancho_mm=190)
    return lam


# ================================================================== DB-02 (1/5)
def escena_detalle():
    E = Escena(); x0 = 1.25
    E.g = 2
    E.caja(COL[1][0], YCOL[0], 1.55, COL[1][1], YCOL[1], zvig(YCOL[1]) - 0.05, METAL, paso=0.10)
    estructura(E, xr=(x0, AX), yr=(1.80, AY), zmin=1.55, seat=False)
    E.g = 2
    E.caja(COL[1][0], YCOL[0], 1.55, COL[1][1], YCOL[1], zvig(YCOL[1]) - 0.05, METAL, paso=0.10)
    canaleta(E, x0, AX)
    bajada(E, z_min=1.55)
    cobertura(E, xr=(x0, AX), y0=1.85, n=4)
    return E


def seccion_canaleta(lam, xmm, ymm):
    O = lam.P(xmm, ymm)
    p = lambda y, z: (O[0] + (y - YC0), O[1] + (z - ZB))
    lam.relleno([p(YC0, ZB), p(YC1, ZB), p(YC1, ZB + CH), p(YC0, ZB + CH)], "GALV-RELL")
    lam.poli([p(YC0 - ALA, ZB + CH + 0.012), p(YC0, ZB + CH), p(YC0, ZB), p(YC1, ZB), p(YC1, ZB + CH), p(YC1 - 0.015, ZB + CH)], "PLANCHA-GALV", ancho=0.002)
    ep = T.EPL
    lam.poli([p(YC0 - ep, ZB + CH), p(YC0 - ep, ZB - ep), p(YC1 + ep, ZB - ep), p(YC1 + ep, ZB + CH + ep), p(YC1 - 0.03, ZB + CH + ep)], "PLATINA")
    yc = YSUM
    for dy in (-0.052, 0.052): lam.linea(p(yc + dy, ZB + 0.008), p(yc + dy * 0.4, ZB + 0.075), "TUBO-PVC")
    lam.linea(p(yc - 0.064, ZB + 0.008), p(yc + 0.064, ZB + 0.008), "TUBO-PVC")
    lam.linea(p(yc - 0.021, ZB + 0.075), p(yc + 0.021, ZB + 0.075), "TUBO-PVC")
    for dy in (-DT / 2, DT / 2): lam.linea(p(yc + dy, ZB), p(yc + dy, Z_UN1 + UN[1]), "TUBO-PVC")
    lam.poli([p(YC0 - 0.20, zcob(YC0 - 0.20)), p(AY + VUELO, zcob(AY + VUELO)), p(AY + VUELO, zcob(AY + VUELO) - E_COB),
              p(YC0 - 0.20, zcob(YC0 - 0.20) - E_COB)], "COBERTURA")
    lam.poli([p(YC0 - 0.20, zvig(YC0 - 0.20 + 0.01)), p(AY, zvig(AY)), p(AY, zvig(AY) - 0.05), p(YC0 - 0.20, zvig(YC0 - 0.19) - 0.05)], "ESTRUCTURA-METALICA")
    lam.cota(p(YC0, ZB - 0.06), p(YC1, ZB - 0.06), 6, True, "0.18")
    lam.cota(p(YC1, ZB), p(YC1, ZB + CH), 10, False, "0.20")
    lam.cota(p(YC0 - ALA, ZB + CH + 0.012), p(YC0, ZB + CH + 0.012), 14, True, "0.10")
    xt = lam.P(xmm + 75, 0)[0]; lam.juntar_llamadas()
    for (y, z), txt in (((AY + 0.005, zcob(AY + 0.005) - 0.01), "Cobertura de aluzinc e = 0.35 mm"),
                        ((YC0 - 0.19, zvig(YC0 - 0.19) - 0.04), "Viga metalica tubo 2\" x 2\" x 3 mm"),
                        ((YC0 - 0.06, ZB + CH + 0.008), "Ala posterior sobre la viga (0.10)"),
                        ((YC1, ZB + 0.17), "Canaleta de aluzinc 0.18 x 0.20 (interiores)"),
                        ((YC1 + ep, ZB + 0.10), "Soporte de platina F°G° 1\" x 1/8\""),
                        ((yc + 0.03, ZB + 0.03), "Sumidero tipo cupula 4\""),
                        ((yc + DT / 2, ZB - 0.07), "Niple PVC 4\" a la union")):
        q = p(y, z); lam.llamada(q, (xt, q[1]), [txt], 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(xmm + 30, ymm - 45, "CORTE DE LA CANALETA", "ESC. 1/5 - por el sumidero (corte A-A)", 80)


def seccion_falsa_columna(lam, xmm, ymm):
    """Seccion horizontal C-C de la falsa columna (planta) a 1/5."""
    O = lam.P(xmm, ymm)
    p = lambda x, y: (O[0] + (x - XS), O[1] + (y - YCOL[0]))
    lam.relleno([p(COL[1][0], YCOL[0]), p(COL[1][1], YCOL[0]), p(COL[1][1], YCOL[1]), p(COL[1][0], YCOL[1])], "METAL-RELL")
    lam.poli([p(COL[1][0], YCOL[0]), p(COL[1][1], YCOL[0]), p(COL[1][1], YCOL[1]), p(COL[1][0], YCOL[1])], "ESTRUCTURA-METALICA", cerrada=True)
    pts = [p(XS - FCX / 2, YFC[0]), p(XS + FCX / 2, YFC[0]), p(XS + FCX / 2, YFC[1]), p(XS - FCX / 2, YFC[1])]
    lam.relleno(pts, "CONCRETO-ACHURADO"); lam.poli(pts, "CONCRETO", cerrada=True)
    lam.relleno([(c[0] + DT / 2 * np.cos(a), c[1] + DT / 2 * np.sin(a)) for c in [p(XS, YT)] for a in np.linspace(0, 2 * np.pi, 33)[:-1]], "TUBO-RELL")
    lam.circulo(p(XS, YT), DT / 2, "TUBO-PVC"); lam.circulo(p(XS, YT), DT / 2 - 0.004, "TUBO-PVC")
    lam.cota(p(XS - FCX / 2, YFC[1]), p(XS + FCX / 2, YFC[1]), 8, True, "0.20")
    lam.cota(p(XS + FCX / 2, YFC[0]), p(XS + FCX / 2, YFC[1]), 8, False, "0.15")
    lam.cota(p(COL[1][1], YCOL[0]), p(COL[1][1], YCOL[1]), 4, False, "0.25")
    lam.cota(p(COL[1][0], YCOL[0]), p(COL[1][1], YCOL[0]), -6, True, "0.10")
    lam.cota(p(XS - FCX / 2, YCOL[1]), p(XS - FCX / 2, YT), -6, False, "0.07")
    xt = lam.P(xmm + 60, 0)[0]; lam.juntar_llamadas()
    for (x, y), txt in (((XS + 0.07, YFC[1] - 0.02), "Falsa columna CL-01 de concreto 0.20 x 0.15"),
                        ((XS, YT + DT / 2), "Bajada PVC 4\" (Ø ext. 0.114)"),
                        ((COL[1][1], (YCOL[0] + YCOL[1]) / 2), "Columna metalica 4\" x 10\" x 3 mm")):
        q = p(x, y); lam.llamada(q, (xt, q[1]), [txt], 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(xmm + 30, ymm - 25, "SECCION C-C DE LA FALSA COLUMNA", "ESC. 1/5 - planta", 90)


def db02(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 5, "DB-02", "DETALLE ISOMETRICO DE CANALETA, SUMIDERO, COLGADOR Y BAJADA DE LA BANCA",
                   "BANCA DE JARDINERIA TIPO 01 - EXTREMO DE LA CANALETA SOBRE LA COLUMNA DERECHA - " + P["nombre"])
    E = escena_detalle()
    P2 = E.dibujar(lam, 330, 205)
    items = [((1.55, 2.05, zcob(2.05)), ["Cobertura de panel aluzinc (contorno)"]),
             ((1.50, YC0 - 0.05, zc(1.50) + CH + 0.006), ["Ala posterior de la canaleta sobre la viga (0.10)"]),
             ((1.45, YC1, zc(1.45) + 0.12), ["Canaleta de aluzinc 0.18 x 0.20 (ancho x alto interiores), S = 0.5 %"]),
             ((SOPS[3], YC1 + T.EPL, zc(SOPS[3]) + 0.10), ["Soporte de platina F°G° 1\" x 1/8\" @0.60 con oreja sobre el borde"]),
             ((AX, YSUM, zc(AX) + 0.10), ["Tapa lateral de aluzinc remachada y sellada"]),
             ((XS + 0.03, YSUM, zc(XS) + 0.06), ["Sumidero tipo cupula 4\""]),
             ((XS + UN[0], YSUM, Z_UN1 + 0.025), ["Niple y union PVC 4\" bajo el sumidero"]),
             ((XS, Y_COLG, zvig(Y_COLG) - 0.12), ["Colgador F°G°: varilla roscada 3/8\" con tuercas, colgada de la viga 2\" x 2\""]),
             ((XS, Y_COLG + 0.02, ZH - DT / 2 - 0.006), ["Banda del colgador sobre el tramo PVC 4\""]),
             ((XS + DT / 2 * 0.7, YT, ZH - 0.05), ["Codos PVC 4\" x 90° con campanas"]),
             ((XS + UN[0], YT, Z_UN2 - 0.025), ["Union PVC 4\" bajo el segundo codo"]),
             ((XS + DT / 2 + 0.004, YT, ZABR), ["Abrazadera F°G° 1\" x 1/8\" con 2 pernos a la columna"]),
             ((XS + DT / 2, YT, 1.60), ["Bajada PVC 4\" (cortada): sigue a la falsa columna CL-01"]),
             ((COL[1][0], YCOL[0], 1.70), ["Columna metalica 4\" x 10\" x 3 mm (cortada)"])]
    T._llamadas(lam, P2, items, 545)
    lam.titulo_vista(300, 52, "ISOMETRICO DEL EXTREMO DE LA CANALETA", "ESC. 1/5 - canaleta, sumidero, colgador, codos y bajada", 170)
    seccion_canaleta(lam, 70, 500)
    seccion_falsa_columna(lam, 640, 470)
    return lam


# ================================================================== DB-03 (1/10): cortes 2D
def tubo_v(v, x, z0, z1, oculto=False):
    T.tubo2d(v, (x, z0), (x, z1), oculto=oculto)


def corte_aa(lam, xmm, ymm):
    """Corte A-A por el eje de la bajada (x = 1.70). Horizontal: h = 2.70 - y (canaleta a la izquierda, como el corte del plano)."""
    v = T.V(lam, xmm, ymm); H = lambda y: 2.70 - y; r = DT / 2; rc = R_CODO + CAMP
    hmax = H(1.05)
    # jardin, piso de circulacion
    v.pl([(H(AY + 0.25), JARDIN), (H(YCOL[0]), JARDIN), (H(YCOL[0]), 0.0), (hmax, 0.0)], "TERRENO")
    # columna y falsa columna
    lam.relleno([v(H(YCOL[1]), JARDIN), v(H(YCOL[0]), JARDIN), v(H(YCOL[0]), zvig(YCOL[0]) - 0.05), v(H(YCOL[1]), zvig(YCOL[1]) - 0.05)], "METAL-RELL")
    v.pl([(H(YCOL[1]), JARDIN), (H(YCOL[0]), JARDIN), (H(YCOL[0]), zvig(YCOL[0]) - 0.05), (H(YCOL[1]), zvig(YCOL[1]) - 0.05)], "ESTRUCTURA-METALICA", True)
    v.concreto([(H(YFC[1]), ZFC[0]), (H(YFC[0]), ZFC[0]), (H(YFC[0]), ZFC[1]), (H(YFC[1]), ZFC[1])])
    # asiento y mensula (referencia)
    pts = [(H(SEAT[1]), SEAT[2]), (H(SEAT[0]), SEAT[2]), (H(SEAT[0]), SEAT[3]), (H(SEAT[1]), SEAT[3])]
    lam.relleno([v(*q) for q in pts], "MADERA-RELL"); v.pl(pts, "MADERA", True)
    v.pl([(H(SEAT[1]), SEAT[2] - 0.075), (H(SEAT[0] + 0.05), SEAT[2] - 0.075), (H(SEAT[0] + 0.05), SEAT[2])], "ESTRUCTURA-METALICA")
    # viga 2" x 2", correa, cobertura (hasta h = hmax, linea de corte)
    v.pl([(H(AY), zvig(AY)), (hmax, zvig(1.05)), (hmax, zvig(1.05) - 0.05), (H(AY), zvig(AY) - 0.05)], "ESTRUCTURA-METALICA", True)
    for yc in (AY - 0.05, 1.65):
        v.rect(H(yc + 0.025), zvig(yc), H(yc - 0.025), zvig(yc) + 0.076, "ESTRUCTURA-METALICA")
    v.pl([(H(AY + VUELO), zcob(AY + VUELO)), (hmax, zcob(1.05)), (hmax, zcob(1.05) - E_COB), (H(AY + VUELO), zcob(AY + VUELO) - E_COB)], "COBERTURA", True)
    v.ln((hmax, zcob(1.05) + 0.05), (hmax, zvig(1.05) - 0.10), "CORTES")
    # canaleta
    lam.relleno([v(H(YC1), ZB), v(H(YC0), ZB), v(H(YC0), ZB + CH), v(H(YC1), ZB + CH)], "GALV-RELL")
    v.pl([(H(YC1 - 0.015), ZB + CH), (H(YC1), ZB + CH), (H(YC1), ZB), (H(YC0), ZB), (H(YC0), ZB + CH), (H(YC0 - ALA), ZB + CH + 0.012)], "PLANCHA-GALV", ancho=0.003)
    for dy in (-0.052, 0.052): v.ln((H(YSUM + dy), ZB + 0.008), (H(YSUM + dy * 0.4), ZB + 0.075), "TUBO-PVC")
    v.ln((H(YSUM + 0.021), ZB + 0.075), (H(YSUM - 0.021), ZB + 0.075), "TUBO-PVC")
    # tuberia: niple, union, codo, tramo, codo, union, bajada, tramo oculto en la falsa columna
    tubo_v(v, H(YSUM), ZB, Z_UN1 + UN[1])
    v.rect(H(YSUM) - UN[0], Z_UN1, H(YSUM) + UN[0], Z_UN1 + UN[1], "ACCESORIO-PVC")
    T.codo2d(v, (H(YSUM), ZH), (0, -1), (1, 0), R_CODO, r, camp=CAMP)
    T.tubo2d(v, (H(YSUM) + rc, ZH), (H(YT) - rc, ZH))
    T.codo2d(v, (H(YT), ZH), (1, 0), (0, -1), R_CODO, r, camp=CAMP)
    v.rect(H(YT) - UN[0], Z_UN2 - UN[1], H(YT) + UN[0], Z_UN2, "ACCESORIO-PVC")
    tubo_v(v, H(YT), Z_UN2 - UN[1], ZFC[1])
    tubo_v(v, H(YT), ZFC[1], ZFC[0], oculto=True)
    # colgador y abrazadera
    hc = H(Y_COLG); zv = zvig(Y_COLG) - 0.05
    v.pl([(hc, ZH + r + 0.008), (hc, zv)], "COLGADOR", ancho=0.0095)
    lam.relleno([v(hc - 0.025, ZH - r - 0.006), v(hc + 0.025, ZH - r - 0.006), v(hc + 0.025, ZH + r + 0.008), v(hc - 0.025, ZH + r + 0.008)], "COLG-RELL")
    v.rect(hc - 0.025, ZH - r - 0.006, hc + 0.025, ZH + r + 0.008, "COLGADOR")
    lam.relleno([v(H(YT) - r - 0.004, ZABR - T.ANP / 2), v(H(YCOL[1]), ZABR - T.ANP / 2), v(H(YCOL[1]), ZABR + T.ANP / 2), v(H(YT) - r - 0.004, ZABR + T.ANP / 2)], "ABRZ-RELL")
    v.rect(H(YT) - r - 0.004, ZABR - T.ANP / 2, H(YCOL[1]), ZABR + T.ANP / 2, "ABRAZADERA")
    # niveles
    for z, t, h in ((0.0, "NPT +0.00 (259.50)", hmax - 0.05), (JARDIN, "-0.15 JARDIN", H(AY + 0.25)), (ZFC[1], "+1.05", H(YFC[1]) - 0.06),
                    (ZB, "+2.385 FONDO", H(YC0) + 0.03), (3.00, "NPT +3.00 (262.50)", hmax - 0.10)):
        lam.nivel(v(h, z), z, t, 1, 1.8)
    # cotas
    v.cota((H(YC1), ZB), (H(YC0), ZB), -6, True, "0.18")
    v.cota((H(YC1), ZB), (H(YC1), ZB + CH), -6, False, "0.20")
    v.cota((H(YFC[1]), ZFC[0]), (H(YFC[0]), ZFC[0]), -6, True, "0.15")
    v.cota((H(YCOL[1]), JARDIN), (H(YCOL[0]), JARDIN), -11, True, "0.25")
    v.cota((H(YFC[1]) - 0.02, ZFC[0]), (H(YFC[1]) - 0.02, ZFC[1]), -4, False, "1.20")
    v.cota((H(YT) + 0.11, ZFC[1]), (H(YT) + 0.11, ZABR), 0, False, "0.72")
    v.cota((H(YT) + 0.11, ZABR), (H(YT) + 0.11, ZH), 0, False, "0.36")
    v.cota((H(YSUM), ZH - r - 0.03), (H(YT), ZH - r - 0.03), -6, True, "0.38")
    v.cota((H(SEAT[0]), 0.0), (H(SEAT[0]), SEAT[3]), 6, False, "0.50")
    lam.juntar_llamadas()
    xtx = v(hmax + 0.12, 0)[0]
    for (u, w), t in (((H(AY - 0.10), zcob(AY - 0.10)), ["Cobertura panel aluzinc e = 0.35 mm"]),
                      ((H(AY - 0.30), zvig(AY - 0.30) - 0.025), ["Viga metalica tubo 2\" x 2\" x 3 mm"]),
                      ((H(YSUM), ZB + 0.06), ["Sumidero tipo cupula 4\""]),
                      ((H(YC1), ZB + 0.15), ["Canaleta de aluzinc 0.18 x 0.20, S = 0.5 %"]),
                      ((hc, ZH + 0.15), ["Colgador F°G° con varilla roscada 3/8\""]),
                      ((H(YSUM) + 0.05, ZH - 0.05), ["Codos PVC 4\" x 90° y uniones"]),
                      ((H(YT) - r - 0.004, ZABR), ["Abrazadera F°G° 1\" x 1/8\" a la columna"]),
                      ((H(YT) - r, 1.40), ["Bajada PVC 4\""]),
                      ((H(YCOL[0]) - 0.02, 1.60), ["Columna metalica 4\" x 10\" x 3 mm"]),
                      ((H(YFC[1]), 0.50), ["Falsa columna CL-01 0.20 x 0.15"]),
                      ((H(SEAT[0] + 0.30), SEAT[3]), ["Asiento de madera"])):
        lam.llamada(v(u, w), (xtx, v(0, w)[1]), t, 1.9)
    lam.volcar_llamadas()
    lam.titulo_vista(xmm + 85, ymm - 45, "CORTE A-A (LATERAL)", "ESC. 1/10 - por el eje de la bajada", 110)


def corte_bb(lam, xmm, ymm):
    """Corte B-B frontal (vista desde el jardin, plano y = 2.12 por la bajada): x a la derecha, z hacia arriba."""
    v = T.V(lam, xmm, ymm); r = DT / 2
    v.pl([(-0.30, JARDIN), (AX + 0.30, JARDIN)], "TERRENO")
    lam.texto(v(-0.15, JARDIN + 0.04), "JARDIN", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    v.pl([(-0.30, 0.0), (AX + 0.30, 0.0)], "CONCRETO-OCULTO")
    # columnas (en corte) y celosia/asiento detras (contorno)
    for xa, xb in COL:
        zt = zvig(YT) - 0.05
        lam.relleno([v(xa, JARDIN), v(xb, JARDIN), v(xb, zt), v(xa, zt)], "METAL-RELL")
        v.pl([(xa, JARDIN), (xb, JARDIN), (xb, zt), (xa, zt)], "ESTRUCTURA-METALICA", True)
        xm = (xa + xb) / 2
        v.rect(xm - 0.025, zt, xm + 0.025, zt + 0.05, "ESTRUCTURA-METALICA")              # viga 2" x 2" en seccion
    for z0 in LISTONES: v.rect(COL[0][1], z0, COL[1][0], z0 + 0.20, "MADERA")
    v.rect(COL[0][1], SEAT[2], COL[1][0], SEAT[3], "MADERA")
    # correa del borde, cobertura y canaleta en elevacion (pendiente hacia el sumidero)
    zcr = zvig(AY - 0.05)
    v.rect(0.0, zcr, AX, zcr + 0.076, "ESTRUCTURA-METALICA")
    v.pl([(0.0, zcob(AY + VUELO)), (AX, zcob(AY + VUELO))], "COBERTURA", ancho=0.006)
    lam.relleno([v(0.0, zc(0.0)), v(XS, zc(XS)), v(AX, zc(AX)), v(AX, zc(AX) + CH), v(XS, zc(XS) + CH), v(0.0, zc(0.0) + CH)], "GALV-RELL")
    v.pl([(0.0, zc(0.0) + CH), (0.0, zc(0.0)), (XS, zc(XS)), (AX, zc(AX)), (AX, zc(AX) + CH), (XS, zc(XS) + CH), (0.0, zc(0.0) + CH)], "PLANCHA-GALV", ancho=0.003)
    for xs in SOPS: v.pl([(xs, zc(xs) - T.EPL), (xs, zc(xs) + CH)], "PLATINA", ancho=T.ANP)
    lam.flecha(v(0.55, zc(0.55) + 0.12), v(1.35, zc(1.35) + 0.12), "FLUJO", 3.0)
    lam.texto(v(0.95, zc(0.95) + 0.15), "S = 0.5 %", 2.0, "TEXTOS", TA.MIDDLE_CENTER)
    # bajada vista de frente: niple, union, codos (el tramo horizontal va hacia la columna), union, bajada
    tubo_v(v, XS, zc(XS), Z_UN1 + UN[1])
    v.rect(XS - UN[0], Z_UN1, XS + UN[0], Z_UN1 + UN[1], "ACCESORIO-PVC")
    zc1, zc2 = ZH + R_CODO + CAMP, ZH - R_CODO - CAMP
    lam.relleno([v(XS - r - 0.007, zc2), v(XS + r + 0.007, zc2), v(XS + r + 0.007, Z_UN1), v(XS - r - 0.007, Z_UN1)], "ACCES-RELL")
    v.rect(XS - r - 0.007, zc2, XS + r + 0.007, Z_UN1, "ACCESORIO-PVC")
    v.circ((XS, ZH), r, "ACCESORIO-PVC")
    v.rect(XS - UN[0], Z_UN2 - UN[1], XS + UN[0], Z_UN2, "ACCESORIO-PVC")
    tubo_v(v, XS, Z_UN2 - UN[1], ZFC[1])
    # colgador (detras del tramo) y abrazadera
    v.pl([(XS, ZH + r + 0.008), (XS, zvig(Y_COLG) - 0.05)], "COLGADOR", ancho=0.0095)
    lam.relleno([v(XS - r - 0.004, ZABR - T.ANP / 2), v(XS + r + 0.004, ZABR - T.ANP / 2), v(XS + r + 0.004, ZABR + T.ANP / 2), v(XS - r - 0.004, ZABR + T.ANP / 2)], "ABRZ-RELL")
    v.rect(XS - r - 0.004, ZABR - T.ANP / 2, XS + r + 0.004, ZABR + T.ANP / 2, "ABRAZADERA")
    for sg in (-1, 1): v.rect(XS + sg * (r + 0.004), ZABR - 0.005, XS + sg * 0.05, ZABR + 0.005, "ABRAZADERA")
    # falsa columna en corte con la bajada oculta
    v.concreto([(XS - FCX / 2, ZFC[0]), (XS + FCX / 2, ZFC[0]), (XS + FCX / 2, ZFC[1]), (XS - FCX / 2, ZFC[1])])
    tubo_v(v, XS, ZFC[1], ZFC[0], oculto=True)
    # niveles y cotas
    for z, t, x in ((0.0, "NPT +0.00", -0.25), (ZFC[1], "+1.05", AX + 0.12), (ZB, "+2.385", AX + 0.12), (3.00, "NPT +3.00", -0.25)):
        lam.nivel(v(x, z), z, t, 1 if x > 1 else -1, 1.8)
    v.cota((0.0, zc(0.0) + CH + 0.08), (AX, zc(AX) + CH + 0.08), 10, True, "2.00")
    v.cota((XS, zc(XS) + CH), (AX, zc(AX) + CH), 4, True, "0.30")
    v.cota((COL[0][0], JARDIN - 0.06), (COL[1][1], JARDIN - 0.06), -6, True, "1.50")
    v.cota((COL[0][1], SEAT[3] + 0.04), (COL[1][0], SEAT[3] + 0.04), 0, True, "1.30")
    v.cota((XS - FCX / 2, ZFC[0] - 0.02), (XS + FCX / 2, ZFC[0] - 0.02), -14, True, "0.20")
    v.cota((XS + FCX / 2 + 0.03, ZFC[0]), (XS + FCX / 2 + 0.03, ZFC[1]), 6, False, "1.20")
    lam.juntar_llamadas()
    xtx = v(AX + 0.42, 0)[0]
    for (u, w), t in (((0.40, zcob(AY + VUELO)), ["Cobertura panel aluzinc e = 0.35 mm"]),
                      ((0.25, zcr + 0.04), ["Correa tubo rectangular 2\" x 3\" x 3 mm"]),
                      ((SOPS[1], zc(SOPS[1]) + 0.10), ["Soporte de platina F°G° 1\" x 1/8\" @0.60"]),
                      ((1.10, zc(1.10) + 0.05), ["Canaleta de aluzinc 0.18 x 0.20, L = 2.00, S = 0.5 %"]),
                      ((AX, zc(AX) + 0.10), ["Tapa lateral de aluzinc"]),
                      ((XS + r, zc(XS) - 0.03), ["Sumidero cupula 4\", niple y union PVC 4\""]),
                      ((XS, ZH + 0.25), ["Colgador F°G° con varilla roscada 3/8\""]),
                      ((XS + r + 0.007, ZH), ["Codos PVC 4\" x 90° (el tramo horizontal va a la columna)"]),
                      ((XS + r + 0.004, ZABR), ["Abrazadera F°G° 1\" x 1/8\""]),
                      ((XS + r, 1.40), ["Bajada PVC 4\""]),
                      ((XS + FCX / 2, 0.60), ["Falsa columna CL-01 0.20 x 0.15 (bajada oculta)"]),
                      ((COL[0][0], 2.00), ["Columna metalica 4\" x 10\" x 3 mm"]),
                      ((1.00, LISTONES[2] + 0.10), ["Celosia de madera (detras)"])):
        lam.llamada(v(u, w), (xtx, v(0, w)[1]), t, 1.9)
    lam.volcar_llamadas()
    lam.titulo_vista(xmm + 100, ymm - 45, "CORTE B-B (FRONTAL)", "ESC. 1/10 - visto desde el jardin, por el eje de la bajada", 130)


def db03(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 10, "DB-03", "CORTES A-A Y B-B DEL DRENAJE PLUVIAL DE LA BANCA DE JARDINERIA",
                   "BANCA TIPO 01: CANALETA, SUMIDERO, COLGADOR, BAJADA PVC 4\" Y FALSA COLUMNA CL-01 - " + P["nombre"])
    corte_aa(lam, 45, 140)
    corte_bb(lam, 395, 140)
    return lam


def construir():
    B.PROYECTO = P["proyecto"]; B.UBICACION = P["ubicacion"]
    doc = B.nuevo_documento()
    for n, c, lt, lw in T.CAPAS_EXTRA + CAPAS_BANCA:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt); ly.dxf.lineweight = lw
    laminas = {"DB-01": db01(doc, 0.0, 0.0), "DB-02": db02(doc, 14.0, 0.0), "DB-03": db03(doc, 0.0, -10.0)}
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: -1 for e in msp.query("HATCH SOLID")})
    L.presentaciones(doc, laminas)
    au = doc.audit(); doc.saveas(SAL)
    print("%s (%d errores de auditoria)" % (os.path.relpath(SAL, RAIZ), len(au.errors)))
    return laminas


if __name__ == "__main__":
    construir()
