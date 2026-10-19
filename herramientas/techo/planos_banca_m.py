"""Isometricos del drenaje pluvial de la BANCA DE JARDINERIA (detalle de banca tipo 01) - CAR MUJERES (CUI 2717013).

Fuente: DETALLE_DE_BANCA_TIPO_01.dxf (planta, planta de techo, corte A-A y elevaciones E1/E2, esc. 1/25, dibujado a escala
real) y la indicacion del proyectista para la canaleta: 0.18 de ancho x 0.20 de alto. La red pluvial se compatibiliza con la
de las edificaciones del CAR Mujeres (laminas DR-01 a DR-06): tubo PVC-U 4", codos de 90 grados, abrazadera F°G° y falsa
columna de concreto 0.20 x 0.15 x 1.30.
Escala real (1 unidad = 1 m). DB-01 a 1/15 (banca completa) y DB-02 a 1/5 (canaleta, sumidero y bajada).
Uso: python3 herramientas/techo/planos_banca_m.py
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
for _e in (5, 15):
    if _e not in B.ESCALAS: B.ESCALAS.append(_e)

# ------------------------------------------------------------------ geometria (m) del detalle de banca tipo 01
# x: largo de la banca (techo 2.00); y: fondo (techo 2.40, la canaleta en el borde bajo y = 2.40); z: sobre el NPT de la circulacion
AX, AY = 2.00, 2.40                     # planta de techo
CB, CH = 0.18, 0.20                     # canaleta de aluzinc: ancho x alto interiores (indicacion del proyectista)
YC0 = AY + 0.01                         # cara interior posterior de la canaleta (detras queda el borde del techo)
YC1 = YC0 + CB
ZB = 2.385                              # fondo de la canaleta en el sumidero (corte A-A)
S_CAN = 1.00                            # pendiente hacia el sumidero (%), como la red de techo del CAR Mujeres
VUELO = 0.05                            # la cobertura entra 0.05 en la canaleta (gotero)
PEND = 0.125                            # pendiente de la cobertura (0.30 en 2.40)
Z_COB0 = 2.997                          # cara superior de la cobertura en y = 0 (NPT 262.50 = +3.00)
E_COB = 0.03                            # alto de la onda del panel
COL = [(0.25, 0.35), (1.65, 1.75)]      # columnas metalicas 4" x 10" (0.10 en x)
YCOL = (1.80, 2.05)                     # 0.25 en y
JARDIN = -0.15                          # jardin 0.15 bajo la circulacion (corte A-A)
XS = 1.70                               # eje del sumidero y de la bajada (columna derecha)
FC = (0.20, 0.15, 1.30)                 # falsa columna (CAR Mujeres): 0.20 x 0.15 x 1.30
YFC = (YCOL[1], YCOL[1] + FC[1])        # entre la columna y la canaleta
YT = (YFC[0] + YFC[1]) / 2              # eje de la bajada (centrada en la falsa columna)
ZFC = (JARDIN, JARDIN + FC[2])
ZH = 2.13                               # eje del tramo horizontal bajo la canaleta (corte A-A)
ZSAL = -0.35                            # eje de la salida enterrada
R_CODO, CAMP = 0.08, 0.05
DT = T.DT                               # PVC 4": 0.114
ZABR = 1.75                             # abrazadera (corte A-A)
SOPS = [0.10, 0.70, 1.30, 1.90]         # soportes de platina @0.60
s = S_CAN / 100.0
zc = lambda x: ZB + s * abs(XS - x)     # fondo de la canaleta (baja hacia el sumidero desde los dos lados)
zcob = lambda y: Z_COB0 - PEND * y      # cara superior de la cobertura
zvig = lambda y: Z_COB0 - E_COB - 0.076 - PEND * y   # cara superior de la viga 2" x 2"

ALUZ, PLAT, CAB = (204, 210, 218), T.PLAT, T.CAB
PVC, ACC, ABRZ, CONC = T.PVC, T.ACC, T.ABRZ, T.CONC
METAL, MADERA, PISO, TIERRA, CUPULA = (120, 128, 140), (196, 150, 98), (224, 222, 214), (206, 222, 184), (90, 96, 104)


def tubo(E, a, b):
    E.cilindro(a, b, DT / 2, PVC, n=20, paso=0.10)


def codo(E, Pq, a, b):
    E.codo(Pq, a, b, R_CODO, DT / 2, ACC, campana=CAMP)


def abrazadera(E, z, x, yw, yt):
    """Abrazadera de platina F°G° 1" x 1/8" sobre el tubo vertical (x, yt), fijada a la cara y = yw de la columna metalica."""
    r = DT / 2; h = T.ANP / 2; e = T.EPL
    E.cilindro((x, yt, z - h), (x, yt, z + h), r + 0.004, ABRZ, n=20, tapas=False)
    for sg in (-1, 1):
        x1, x2 = sorted((x + sg * (r + 0.004), x + sg * (r + 0.004 + e)))
        E.caja(x1, yw + e, z - h, x2, yt, z + h, ABRZ, 0.05)
        x3, x4 = sorted((x + sg * (r + 0.004), x + sg * 0.05))
        E.caja(x3, yw, z - h, x4, yw + e, z + h, ABRZ, 0.05)
        E.prisma_hex((x + sg * 0.045, yw + e, z), (0, 1, 0), 0.0111, 0.0043, CAB)      # perno autorroscante a la columna


def cupula(E, x, y, z):
    """Sumidero tipo cupula 4" sobre la abertura del fondo: aro, barras verticales y tapa."""
    r0 = 0.052
    E.cilindro((x, y, z), (x, y, z + 0.008), r0 + 0.012, CUPULA, n=24, tapas=True, paso=1.0)            # aro de asiento
    for k in range(10):
        a = 2 * np.pi * k / 10
        p0 = (x + r0 * np.cos(a), y + r0 * np.sin(a), z + 0.008)
        p1 = (x + 0.020 * np.cos(a), y + 0.020 * np.sin(a), z + 0.075)
        E.cilindro(p0, p1, 0.0035, CUPULA, n=6, tapas=False, paso=1.0)
    E.disco((x, y, z + 0.075), (0, 0, 1), 0.024, CUPULA, n=16)
    for zz, rr in ((0.03, 0.044), (0.055, 0.031)):
        E.cilindro((x, y, z + zz), (x, y, z + zz + 0.004), rr, CUPULA, n=20, tapas=False, paso=1.0)


def canaleta(E, x0=0.0, x1=AX, sops=True):
    Q = E.quad; e = 0.0006
    E.g = 5
    Q((x0, YC0, zc(x0)), (x1, YC0, zc(x1)), (x1, YC0, zc(x1) + CH + 0.06), (x0, YC0, zc(x0) + CH + 0.06), ALUZ, 0.06)   # cara posterior
    Q((x0, YC0, zc(x0) + CH + 0.06), (x1, YC0, zc(x1) + CH + 0.06), (x1, YC0 - 0.10, zc(x1) + CH + 0.075),
      (x0, YC0 - 0.10, zc(x0) + CH + 0.075), ALUZ, 0.06)                                                           # ala bajo la cobertura
    # fondo en dos tramos (pendiente hacia el sumidero)
    for a, b in ((x0, min(XS, x1)), (max(XS, x0), x1)):
        if b - a > 1e-6: Q((a, YC0, zc(a)), (b, YC0, zc(b)), (b, YC1, zc(b)), (a, YC1, zc(a)), ALUZ, 0.06)
    E.g = 7
    for a, b in ((x0, min(XS, x1)), (max(XS, x0), x1)):
        if b - a > 1e-6: Q((a, YC1, zc(a)), (b, YC1, zc(b)), (b, YC1, zc(b) + CH), (a, YC1, zc(a) + CH), ALUZ, 0.06)   # cara frontal
    Q((x0, YC1 - 0.015, zc(x0) + CH), (x1, YC1 - 0.015, zc(x1) + CH), (x1, YC1, zc(x1) + CH), (x0, YC1, zc(x0) + CH), ALUZ, 0.06)
    for xt in (x0, x1):                                                                                           # tapas laterales
        if xt in (0.0, AX):
            E.cara([(xt, YC0, zc(xt)), (xt, YC1, zc(xt)), (xt, YC1, zc(xt) + CH), (xt, YC0, zc(xt) + CH + 0.06)], (226, 230, 236))
    if sops:
        for xs in SOPS:
            if not (x0 <= xs <= x1): continue
            z = zc(xs); w = T.ANP / 2; ep = T.EPL
            E.g = 4; E.caja(xs - w, YC0 - ep, z - ep, xs + w, YC1 + ep, z, PLAT, 0.03)              # bajo el fondo
            E.caja(xs - w, YC0 - ep, z - ep, xs + w, YC0, z + CH + 0.06, PLAT, 0.03)                 # cara posterior
            E.g = 8; E.caja(xs - w, YC1, z - ep, xs + w, YC1 + ep, z + CH, PLAT, 0.03)               # cara frontal
            E.caja(xs - w, YC1 - 0.03, z + CH, xs + w, YC1 + ep, z + CH + ep, PLAT, 0.03)            # oreja sobre el borde
    E.g = 6
    cupula(E, XS, (YC0 + YC1) / 2, zc(XS) + e)


def bajada(E, hasta_salida=True, z_min=None):
    yb = (YC0 + YC1) / 2; r = R_CODO + CAMP
    E.g = 3
    tubo(E, (XS, yb, zc(XS) - 0.002), (XS, yb, ZH + r))                                   # niple del sumidero
    codo(E, (XS, yb, ZH), (0, 0, -1), (0, -1, 0))
    tubo(E, (XS, yb - r, ZH), (XS, YT + r, ZH))                                             # tramo bajo la canaleta (corte A-A)
    codo(E, (XS, YT, ZH), (0, -1, 0), (0, 0, -1))
    zfin = ZFC[1] if z_min is None else max(z_min, ZFC[1])
    tubo(E, (XS, YT, ZH - r), (XS, YT, zfin))                                               # bajada vista
    if hasta_salida:
        E.g = 1
        tubo(E, (XS, YT, ZFC[1]), (XS, YT, ZSAL + r))                                       # dentro de la falsa columna
        codo(E, (XS, YT, ZSAL), (0, 0, -1), (0, 1, 0))
        tubo(E, (XS, YT + r, ZSAL), (XS, AY + 0.55, ZSAL))                                  # salida enterrada
    E.g = 9
    if (z_min is None) or ZABR > z_min: abrazadera(E, ZABR, XS, YCOL[1], YT)


def escena_banca():
    E = Escena(); Q = E.quad
    # piso de la circulacion y jardin (grupo 0)
    E.g = 0
    Q((-0.30, -0.45, 0.0), (AX + 0.30, -0.45, 0.0), (AX + 0.30, YCOL[0], 0.0), (-0.30, YCOL[0], 0.0), PISO, 0.40)
    Q((-0.30, YCOL[0], JARDIN), (AX + 0.30, YCOL[0], JARDIN), (AX + 0.30, AY + 0.65, JARDIN), (-0.30, AY + 0.65, JARDIN), TIERRA, 0.40)
    Q((-0.30, YCOL[0], JARDIN), (AX + 0.30, YCOL[0], JARDIN), (AX + 0.30, YCOL[0], 0.0), (-0.30, YCOL[0], 0.0), PISO, 0.40)
    bajada(E)                                                                                   # tramo enterrado (grupo 1) y visto
    # falsa columna (grupo 2: tapa el tramo interior)
    E.g = 2
    E.caja(XS - FC[0] / 2, YFC[0], ZFC[0], XS + FC[0] / 2, YFC[1], ZFC[1], CONC, paso=0.12)
    # columnas, asiento, celosia y estructura del techo (grupo 2)
    for xa, xb in COL:
        E.caja(xa, YCOL[0], JARDIN, xb, YCOL[1], zvig((YCOL[0] + YCOL[1]) / 2) - 0.051, METAL, paso=0.30)
        xm = (xa + xb) / 2
        E.caja(xm - 0.025, 1.35, 0.375, xm + 0.025, YCOL[0], 0.45, METAL, paso=0.20)           # mensula de tubo 2" x 3"
    E.caja(COL[0][1], 1.35, 0.45, COL[1][0], YCOL[0], 0.50, MADERA, paso=0.20)                   # asiento de madera
    for k in range(9):                                                                          # celosia de madera
        z0 = 0.62 + 0.22 * k
        E.caja(COL[0][1], 1.90, z0, COL[1][0], 1.95, z0 + 0.12, MADERA, paso=0.25)
    for xa, xb in COL:                                                                          # vigas 2" x 2" inclinadas
        xm = (xa + xb) / 2
        E.quad((xm - 0.025, 0.0, zvig(0.0)), (xm + 0.025, 0.0, zvig(0.0)), (xm + 0.025, AY, zvig(AY)), (xm - 0.025, AY, zvig(AY)), METAL, 0.30)
        E.quad((xm + 0.025, 0.0, zvig(0.0) - 0.05), (xm + 0.025, AY, zvig(AY) - 0.05), (xm + 0.025, AY, zvig(AY)), (xm + 0.025, 0.0, zvig(0.0)), METAL, 0.30)
    for yc in (0.05, 0.85, 1.65, AY - 0.05):                                                    # correas 2" x 3"
        z = zvig(yc)
        E.caja(-0.0, yc - 0.025, z, AX, yc + 0.025, z + 0.076, METAL, paso=0.30)
    canaleta(E)
    # cobertura de panel (solo contorno y ondas, para ver la estructura y la canaleta)
    E.g = 10
    y1 = AY + VUELO
    E.quad((0, 0, zcob(0)), (AX, 0, zcob(0)), (AX, y1, zcob(y1)), (0, y1, zcob(y1)), (0, 0, 0), 3.0, relleno=False)
    for k in range(1, 10):
        x = AX * k / 10
        E.cara([(x, 0, zcob(0)), (x, y1, zcob(y1))], (0, 0, 0), [True, False], relleno=False)
    return E


LEYENDA = [(ALUZ, "Canaleta de aluzinc 0.18 x 0.20 (ancho x alto interiores)"), (CUPULA, "Sumidero tipo cupula 4\""),
           (PVC, "Tubo PVC-U 4\" (niple, tramo bajo canaleta, bajada y salida)"), (ACC, "Codos PVC 4\" x 90° con campanas (3)"),
           (ABRZ, "Abrazadera F°G° 1\" x 1/8\" a la columna"), (PLAT, "Soporte de platina F°G° 1\" x 1/8\" @0.60"),
           (CONC, "Falsa columna de concreto f'c = 175 kg/cm2"), (METAL, "Estructura metalica de la banca (referencia)"),
           (MADERA, "Asiento y celosia de madera (referencia)")]


def db01(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 15, "DB-01", "ISOMETRICO DEL DRENAJE PLUVIAL DE LA BANCA DE JARDINERIA",
                   "BANCA TIPO 01: CANALETA, SUMIDERO CUPULA, BAJADA PVC 4\", FALSA COLUMNA Y SALIDA - " + P["nombre"])
    E = escena_banca()
    P2 = E.dibujar(lam, 245, 335)
    yb = (YC0 + YC1) / 2
    items = [((0.60, 0.80, zcob(0.80)), ["Cobertura de panel metalico de aluzinc e = 0.35 mm (solo contorno)", "vuela 0.05 m dentro de la canaleta"]),
             ((0.80, YC1, zc(0.80) + 0.12), ["Canaleta de aluzinc 0.18 x 0.20 (ancho x alto interiores), L = 2.00 m,",
                                              "con tapas en los extremos; S = 1 % hacia el sumidero"]),
             ((SOPS[2], YC1 + T.EPL, zc(SOPS[2]) + 0.08), ["Soporte de platina F°G° 1\" x 1/8\" @0.60 (4 soportes)"]),
             ((XS, yb, zc(XS) + 0.06), ["Sumidero tipo cupula 4\" en el fondo de la canaleta"]),
             ((XS, (yb + YT) / 2, ZH + DT / 2), ["Codos PVC 4\" x 90° y tramo bajo la canaleta"]),
             ((XS + DT / 2, YT, ZABR + 0.02), ["Abrazadera F°G° 1\" x 1/8\" fijada a la columna metalica"]),
             ((XS + DT / 2, YT, 1.45), ["Bajada PVC-U 4\" adosada a la columna 4\" x 10\""]),
             ((XS + FC[0] / 2, YFC[1], 0.55), ["Falsa columna 0.20 x 0.15 x 1.30, f'c = 175 kg/cm2 (protege la bajada)"]),
             ((XS, AY + 0.35, ZSAL + DT / 2), ["Codo de salida y tubo PVC 4\" enterrado hacia la cuneta", "o caja mas cercana (definir en la planta de drenaje)"]),
             ((0.80, 1.35, 0.50), ["Asiento de madera sobre mensulas de tubo 2\" x 3\" (referencia)"]),
             ((COL[0][0], (YCOL[0] + YCOL[1]) / 2, 1.20), ["Columna metalica de tubo rectangular 4\" x 10\" x 3 mm (referencia)"]),
             ((1.00, AY + 0.50, JARDIN), ["Jardin (0.15 bajo la circulacion)"])]
    T._llamadas(lam, P2, items, 420)
    lam.titulo_vista(250, 52, "ISOMETRICO DE LA BANCA DE JARDINERIA TIPO 01", "ESC. 1/15 - se mira desde el jardin; la cobertura se dibuja solo en contorno", 170)
    T.leyenda_colores(lam, 640, 560, LEYENDA)
    lam.notas(640, 470, "NOTAS", [
        "1. Base: detalle de banca tipo 01 (planta, planta de techo, corte A-A y elevaciones E1 y E2, esc. 1/25).",
        "2. Canaleta de aluzinc con seccion interior 0.18 de ancho x 0.20 de alto, del largo del techo (2.00 m).",
        "3. Pendiente de la canaleta S = 1 % hacia el sumidero, igual que la red de techo del CAR Mujeres (laminas DR).",
        "4. Bajada de PVC-U 4\" (NTP 399.003) con 3 codos de 90 grados; uniones con cemento solvente.",
        "5. Falsa columna 0.20 x 0.15 x 1.30 de concreto f'c = 175 kg/cm2, como en las bajadas de las edificaciones.",
        "6. El tubo enterrado se dibuja sobre el terreno para que se vea su recorrido.",
    ], hmm=1.8, ancho_mm=190)
    return lam


def escena_detalle():
    E = Escena()
    x0 = 1.25
    # columna y falsa columna de referencia (cortadas)
    E.g = 2
    E.caja(COL[1][0], YCOL[0], 1.55, COL[1][1], YCOL[1], zvig(YCOL[1]) - 0.051, METAL, paso=0.10)
    for yc in (AY - 0.05,):
        z = zvig(yc); E.caja(x0, yc - 0.025, z, AX, yc + 0.025, z + 0.076, METAL, paso=0.10)
    xm = (COL[1][0] + COL[1][1]) / 2
    E.quad((xm - 0.025, 1.80, zvig(1.80)), (xm + 0.025, 1.80, zvig(1.80)), (xm + 0.025, AY, zvig(AY)), (xm - 0.025, AY, zvig(AY)), METAL, 0.10)
    canaleta(E, x0, AX)
    bajada(E, hasta_salida=False, z_min=1.55)
    E.g = 10
    y1 = AY + VUELO
    E.quad((x0, 1.85, zcob(1.85)), (AX, 1.85, zcob(1.85)), (AX, y1, zcob(y1)), (x0, y1, zcob(y1)), (0, 0, 0), 3.0, relleno=False)
    for k in range(1, 4):
        x = x0 + (AX - x0) * k / 4
        E.cara([(x, 1.85, zcob(1.85)), (x, y1, zcob(y1))], (0, 0, 0), [True, False], relleno=False)
    return E


def seccion_canaleta(lam, xmm, ymm):
    """Corte transversal de la canaleta por el sumidero (esc. 1/5) con sus cotas."""
    O = lam.P(xmm, ymm)
    p = lambda y, z: (O[0] + (y - YC0), O[1] + (z - ZB))
    lam.poli([p(YC0 - 0.10, ZB + CH + 0.075), p(YC0, ZB + CH + 0.06), p(YC0, ZB), p(YC1, ZB), p(YC1, ZB + CH), p(YC1 - 0.015, ZB + CH)], "PLANCHA-GALV")
    ep = T.EPL                                                                                  # soporte de platina
    lam.poli([p(YC0 - ep, ZB + CH + 0.06), p(YC0 - ep, ZB - ep), p(YC1 + ep, ZB - ep), p(YC1 + ep, ZB + CH + ep), p(YC1 - 0.03, ZB + CH + ep)], "PLATINA")
    yc = YC0 + CB / 2
    for dy in (-0.052, 0.052):                                                                  # cupula
        lam.linea(p(yc + dy, ZB + 0.008), p(yc + dy * 0.4, ZB + 0.075), "TUBO-PVC")
    lam.linea(p(yc - 0.064, ZB + 0.008), p(yc + 0.064, ZB + 0.008), "TUBO-PVC")
    lam.linea(p(yc - 0.021, ZB + 0.075), p(yc + 0.021, ZB + 0.075), "TUBO-PVC")
    for dy in (-DT / 2, DT / 2): lam.linea(p(yc + dy, ZB), p(yc + dy, ZB - 0.12), "TUBO-PVC")    # niple
    lam.poli([p(YC0 - 0.16, zcob(YC0 - 0.16)), p(AY + VUELO, zcob(AY + VUELO))], "COBERTURA")
    lam.cota(p(YC0, ZB - 0.06), p(YC1, ZB - 0.06), 6, True, "0.18")
    lam.cota(p(YC1, ZB), p(YC1, ZB + CH), 10, False, "0.20")
    lam.cota(p(AY, zcob(AY)), p(AY + VUELO, zcob(AY)), 8, True, "0.05")
    xt = lam.P(xmm + 75, 0)[0]
    for (y, z), txt in (((AY + 0.02, zcob(AY + 0.02)), "Cobertura: vuelo 0.05 dentro de la canaleta"),
                        ((YC0 - 0.06, ZB + CH + 0.068), "Ala posterior bajo la cobertura (0.10)"),
                        ((YC1, ZB + 0.17), "Canaleta de aluzinc 0.18 x 0.20 (interiores)"),
                        ((YC1 + ep, ZB + 0.10), "Soporte de platina F°G° 1\" x 1/8\""),
                        ((yc + 0.03, ZB + 0.03), "Sumidero tipo cupula 4\""),
                        ((yc + DT / 2, ZB - 0.08), "Niple PVC 4\" al codo")):
        q = p(y, z); lam.llamada(q, (xt, q[1]), [txt], 2.0)
    lam.titulo_vista(xmm + 20, ymm - 45, "CORTE DE LA CANALETA", "ESC. 1/5 - por el sumidero", 70)


def db02(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 5, "DB-02", "DETALLE ISOMETRICO DE CANALETA, SUMIDERO Y BAJADA DE LA BANCA",
                   "BANCA DE JARDINERIA TIPO 01 - EXTREMO DE LA CANALETA SOBRE LA FALSA COLUMNA - " + P["nombre"])
    E = escena_detalle()
    P2 = E.dibujar(lam, 330, 205)
    yb = (YC0 + YC1) / 2
    items = [((1.55, 2.05, zcob(2.05)), ["Cobertura de panel de aluzinc (contorno): vuela 0.05 dentro de la canaleta"]),
             ((1.50, YC0 - 0.05, zc(1.50) + CH + 0.07), ["Ala posterior de la canaleta bajo la cobertura (0.10)"]),
             ((1.45, YC1, zc(1.45) + 0.12), ["Canaleta de aluzinc 0.18 x 0.20 (ancho x alto interiores), S = 1 %"]),
             ((SOPS[3], YC1 + T.EPL, zc(SOPS[3]) + 0.10), ["Soporte de platina F°G° 1\" x 1/8\" @0.60 con oreja sobre el borde"]),
             ((AX, (YC0 + YC1) / 2, zc(AX) + 0.10), ["Tapa lateral de aluzinc remachada y sellada"]),
             ((XS + 0.03, yb, zc(XS) + 0.06), ["Sumidero tipo cupula 4\" sobre la abertura del fondo"]),
             ((XS + DT / 2, yb, ZH + 0.15), ["Niple PVC 4\" bajo el sumidero"]),
             ((XS, (yb + YT) / 2, ZH + DT / 2), ["Tramo PVC 4\" bajo la canaleta"]),
             ((XS + DT / 2 * 0.7, YT, ZH - 0.06), ["Codos PVC 4\" x 90° con campanas"]),
             ((XS + DT / 2 + 0.004, YT, ZABR), ["Abrazadera F°G° 1\" x 1/8\" con 2 pernos a la columna"]),
             ((XS + DT / 2, YT, 1.62), ["Bajada PVC-U 4\" (cortada): continua a la falsa columna (ver DB-01)"]),
             ((COL[1][0], YCOL[0], 1.70), ["Columna metalica 4\" x 10\" (cortada)"])]
    T._llamadas(lam, P2, items, 545)
    lam.titulo_vista(300, 52, "ISOMETRICO DEL EXTREMO DE LA CANALETA", "ESC. 1/5 - canaleta, sumidero, codos y bajada hasta la falsa columna", 170)
    seccion_canaleta(lam, 70, 500)
    return lam


def construir():
    B.PROYECTO = P["proyecto"]; B.UBICACION = P["ubicacion"]
    doc = B.nuevo_documento()
    for n, c, lt, lw in T.CAPAS_EXTRA:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt); ly.dxf.lineweight = lw
    laminas = {"DB-01": db01(doc, 0.0, 0.0), "DB-02": db02(doc, 14.0, 0.0)}
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: -1 for e in msp.query("HATCH SOLID")})
    L.presentaciones(doc, laminas)
    au = doc.audit(); doc.saveas(SAL)
    print("%s (%d errores de auditoria)" % (os.path.relpath(SAL, RAIZ), len(au.errors)))
    return laminas


if __name__ == "__main__":
    construir()
