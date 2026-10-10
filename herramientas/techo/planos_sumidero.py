"""Laminas de detalle de la caja sumidero de piso (rejilla 0.25 x 0.25, marco de angulo, anclajes, caja de 0.10 m,
salida PVC 4" con un solo codo de 90 grados hacia la cuneta; sin trampa) para CAR Varones, Hogar de Refugio y CAR Mujeres.

Escala real (1 unidad = 1 m), laminas a 1/5. DS-01: isometrico del conjunto. DS-02: corte, planta de la rejilla,
isometrico explosionado y desagregado de materiales por sumidero con el total del proyecto.
Datos: detalle de caja sumidero de los planos (rejilla de platinas 1" x 3/16" de 0.25 m, marco L 1" x 1" x 3/16",
anclajes 3" x 3/8", caja de 0.10 m) y hoja METRADO EN PISO (SUMIDERO) de cada planilla (valores guardados).
Uso: python3 herramientas/techo/planos_sumidero.py [varones refugio mujeres]
"""
import os, sys, math, warnings
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
sys.path.insert(0, HERR); sys.path.insert(0, AQUI)
import openpyxl
import numpy as np
from iso3d import Escena
import dxf_base as B
import dxf_layouts as L
from ezdxf.enums import TextEntityAlignment as TA
from planos_techo import (PROY as PT, CAPAS_EXTRA, V, tubo2d, codo2d, leyenda_colores, _llamadas, tubo3d,
                          PVC, ACC, CONC, ROSCA, DT)

CAPAS_EXTRA = CAPAS_EXTRA + [("REJILLA", 250, "CONTINUOUS", 35), ("REJ-RELL", 250, "CONTINUOUS", 13),
                             ("MARCO-RELL", 5, "CONTINUOUS", 13), ("OCULTO", 8, "HIDDEN", 18)]
B.COLOR_RGB.update({"REJ-RELL": (84, 90, 104), "MARCO-RELL": (140, 156, 182)})

SAL = {"varones": ("entregables_varones", "CAR_VARONES"), "refugio": ("entregables", "HOGAR_REFUGIO"), "mujeres": ("entregables_mujeres", "CAR_MUJERES")}

# ------------------------------------------------------------------ geometria (m)
RJ = 0.25                       # rejilla de 0.25 x 0.25 (detalle de los planos)
PH, PE = 0.0254, 0.0048         # platina 1" x 3/16": altura (de canto) y espesor
N_INT, PASO = 9, 0.025          # platinas interiores de la rejilla y paso entre ejes (abertura libre ~ 0.020)
LA, EA = 0.0254, 0.0048         # angulo L 1" x 1" x 3/16"
MI = RJ + 0.004                 # interior del marco (holgura de 2 mm por lado)
XV = MI / 2 + EA                # cara exterior del ala vertical
XH = XV - LA                    # borde del ala horizontal (asiento de la rejilla) = pared de la caja
ZA = -(PH + EA)                 # cara inferior del ala horizontal
CE, ZF = 0.45, -0.20            # caja de concreto: exterior 0.45 x 0.45, fondo exterior
ZP, ZO = -0.10, -0.13           # caja: profundidad en la pared (0.10 m bajo el piso) y en la salida (fondo inclinado)
RO = DT / 2                     # salida de 4"
R, CP = 0.10, 0.05              # codo de 90: radio de eje y campana
ZT = -0.32                      # eje del tubo horizontal bajo el sumidero
S_TUB = 1.0                     # pendiente minima de la tuberia de 4" (IS.010)
YCU = 0.90                      # cara interior del muro de la cuneta (tramo tipico; la longitud real es variable)
ANCL = 0.075                    # anclaje 3" x 3/8"

REJ, MARC = (84, 90, 104), (140, 156, 182)
ACERO_P, ANG_P, VAR_P = 0.0254 * 0.00476 * 7850, 1.73, 0.56      # kg/m: platina 1" x 3/16", L 1" x 1" x 3/16", Ø 3/8"


def platinas_y():
    return [-RJ / 2 + PE / 2, RJ / 2 - PE / 2] + [(k - (N_INT - 1) / 2) * PASO for k in range(N_INT)]


def metrado(P):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(os.path.join(RAIZ, "insumos", "metrados_vigentes", P["planilla"]), data_only=True)
    M = {}
    for r in wb["RESUMEN"].iter_rows(values_only=True):
        if not r[0] or not isinstance(r[3], (int, float)): continue
        d = str(r[1]).upper()
        if d.startswith("SUMIDERO"): M["sum"] = (str(r[0]), r[3])
        elif d.startswith("TUBERIA DESAG") or d.startswith("TUBERÍA DESAG"): M["tub"] = (str(r[0]), r[3])
        elif d.startswith("CODO") and ("05.02." in str(r[0]) or ".5.2." in str(r[0])): M["codo"] = (str(r[0]), r[3])   # red de piso, no accesorios de techo
        elif d.startswith("TEE"): M["tee"] = (str(r[0]), r[3])
    return M


def desagregado():
    """Materiales por sumidero (geometria del detalle)."""
    L_plat = 4 * RJ + N_INT * (RJ - 2 * PE)
    L_ang = 4 * (MI + EA)
    area = L_plat * 2 * (PH + PE) + L_ang * 4 * LA
    V_caja = CE * CE * (-ZF) - (2 * XV) ** 2 * (-ZA) - (2 * XH) ** 2 * (ZA - ZP) - (2 * XH) ** 2 * (ZP - ZO) / 3
    return [("Platina 1\" x 3/16\" (rejilla: marco + %d platinas)" % N_INT, "m", L_plat, L_plat * ACERO_P),
            ("Angulo L 1\" x 1\" x 3/16\" (marco)", "m", L_ang, L_ang * ANG_P),
            ("Anclaje de fierro 3/8\" x 3\" (8 und soldados al marco)", "m", 8 * ANCL, 8 * ANCL * VAR_P),
            ("Pintura anticorrosiva + 2 manos de esmalte", "m2", area, None),
            ("Concreto f'c = 140 kg/cm2 de la caja (0.45 x 0.45 x 0.20)", "m3", V_caja, None),
            ("Mortero 1:4 para el fondo inclinado y el asentado", "m3", 0.004, None)]


# ================================================================== escenas 3D
def marco3d(E, z0=0.0):
    for sx in (-1, 1):
        E.caja(sx * MI / 2 if sx > 0 else -XV, -XV, z0 + ZA, XV if sx > 0 else -MI / 2, XV, z0, MARC, 0.05)            # ala vertical en x
        E.caja(XH if sx > 0 else -XV, -XV, z0 + ZA, XV if sx > 0 else -XH, XV, z0 - PH, MARC, 0.05)                     # ala horizontal
        E.caja(-XV, MI / 2 if sx > 0 else -XV, z0 + ZA, XV, XV if sx > 0 else -MI / 2, z0, MARC, 0.05)
        E.caja(-XV, XH if sx > 0 else -XV, z0 + ZA, XV, XV if sx > 0 else -XH, z0 - PH, MARC, 0.05)
    s2 = math.sqrt(0.5)
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for t in (-0.07, 0.07):
            c = np.array([sx * XV + (t if sx == 0 else 0), sy * XV + (t if sy == 0 else 0), z0 + ZA / 2])
            if sx == 0: c[0] = t
            if sy == 0: c[1] = t
            d = np.array([sx * s2, sy * s2, -s2])
            E.cilindro(c, c + d * ANCL, 0.0048, ROSCA, n=10, paso=0.1)


def rejilla3d(E, z0=0.0):
    a = RJ / 2
    E.caja(-a, -a, z0 - PH, a, -a + PE, z0, REJ, 0.05); E.caja(-a, a - PE, z0 - PH, a, a, z0, REJ, 0.05)
    E.caja(-a, -a, z0 - PH, -a + PE, a, z0, REJ, 0.05); E.caja(a - PE, -a, z0 - PH, a, a, z0, REJ, 0.05)
    for y in platinas_y()[2:]:
        E.caja(-a + PE, y - PE / 2, z0 - PH, a - PE, y + PE / 2, z0, REJ, 0.05)


def caja3d(E, z0=0.0, transparente=True):
    E.caja(-CE / 2, -CE / 2, z0 + ZF, CE / 2, CE / 2, z0, CONC, paso=0.15, relleno=not transparente)
    # interior: paredes hasta 0.10 y fondo inclinado hacia la salida (se ven por la rejilla)
    h = XH
    for (p, q) in (((-h, -h), (h, -h)), ((h, -h), (h, h)), ((h, h), (-h, h)), ((-h, h), (-h, -h))):
        E.quad((p[0], p[1], z0 + ZP), (q[0], q[1], z0 + ZP), (q[0], q[1], z0 + ZA), (p[0], p[1], z0 + ZA), (214, 214, 206), 0.06)
        E.quad((p[0], p[1], z0 + ZP), (q[0], q[1], z0 + ZP), (q[0] * RO / h, q[1] * RO / h, z0 + ZO), (p[0] * RO / h, p[1] * RO / h, z0 + ZO), (196, 196, 188), 0.06)
    E.disco((0, 0, z0 + ZO + 0.001), (0, 0, 1), RO - 0.006, (60, 64, 70), n=22)


def escena_conjunto():
    E = Escena()
    E.g = 0
    E.caja(-0.50, -0.50, -0.10, 0.50, 0.75, 0.0, CONC, paso=0.5, relleno=False)                 # piso de concreto (transparente)
    for y0, y1 in ((0.80, YCU), (YCU + 0.40, YCU + 0.50)):                                       # cuneta (transparente)
        E.caja(-0.30, y0, -0.50, 0.30, y1, 0.0, CONC, paso=0.5, relleno=False)
    E.caja(-0.30, 0.80, -0.60, 0.30, YCU + 0.50, -0.50, CONC, paso=0.5, relleno=False)
    E.g = 1; caja3d(E)
    E.g = 2
    tubo3d(E, (0, 0, ZO + 0.01), (0, 0, ZT + R + CP))
    E.codo((0, 0, ZT), (0, 0, -1), (0, 1, 0), R, DT / 2, ACC)
    caida = S_TUB / 100 * (YCU - R - CP)
    E.cilindro((0, R + CP, ZT), (0, YCU, ZT - caida), DT / 2, PVC, n=20, paso=0.10)
    E.g = 3; marco3d(E)
    E.g = 4; rejilla3d(E)
    return E, caida


# ================================================================== DS-01: isometrico del conjunto
LEY = [(REJ, "Rejilla de platinas 1\" x 3/16\" (0.25 x 0.25)"), (MARC, "Marco de angulo L 1\" x 1\" x 3/16\""),
       (ROSCA, "Anclajes de fierro 3/8\" x 3\" soldados al marco"), (PVC, "Tubo PVC-U 4\" (salida y tuberia a la cuneta)"),
       (ACC, "Codo PVC-U 4\" x 90° con campanas"), (CONC, "Concreto: caja, piso y cuneta (transparente)")]


def ds01(doc, ox, oy, P, M):
    lam = B.Lamina(doc, ox, oy, 5, "DS-01", "ISOMETRICO DE LA CAJA SUMIDERO DE PISO",
                   "REJILLA 0.25 x 0.25, MARCO, ANCLAJES, CAJA, SALIDA PVC 4\" CON CODO DE 90° HACIA LA CUNETA - " + P["nombre"])
    E, caida = escena_conjunto()
    P2 = E.dibujar(lam, 330, 405)
    items = [((0.0, 0.10, 0.0), ["Rejilla metalica de platinas 1\" x 3/16\" de canto, 0.25 x 0.25 m, removible"]),
             ((XV, 0.06, 0.0), ["Marco de angulo L 1\" x 1\" x 3/16\" al ras del piso terminado"]),
             ((0.0, 0.50, 0.0), ["Piso de concreto con pendiente hacia el sumidero (punto bajo)"]),
             ((XV + 0.035, -0.07, ZA / 2 - 0.035), ["Anclajes de fierro 3/8\" x 3\" (2 por lado) soldados al marco"]),
             ((CE / 2, 0.0, -0.10), ["Caja de concreto f'c = 140 kg/cm2: 0.10 m de profundidad, fondo inclinado a la salida"]),
             ((0.0, -RO, ZO - 0.02), ["Salida PVC-U 4\" en el centro del fondo de la caja"]),
             ((0.0, 0.0, ZT - R - DT / 2), ["Codo PVC-U 4\" x 90° (sin trampa ni sifon)"]),
             ((0.0, 0.50, ZT - 0.006 + DT / 2), ["Tuberia PVC-U 4\" con S = %.1f %% minimo hacia la cuneta (longitud variable)" % S_TUB]),
             ((0.30, 0.85, -0.25), ["Descarga en el muro de la cuneta, sobre su fondo"])]
    _llamadas(lam, P2, items, 585)
    lam.titulo_vista(300, 92, "ISOMETRICO DEL CONJUNTO", "ESC. 1/5 - concreto dibujado transparente", 130)
    leyenda_colores(lam, 590, 228, LEY)
    lam.notas(590, 172, "NOTAS", [
        "1. El sumidero se ubica en el punto bajo del piso; el piso tiene pendiente hacia el, y el marco queda al ras del piso terminado.",
        "2. La salida es directa: tubo PVC-U 4\" vertical y un codo de 90° hacia la tuberia de 4\" que descarga en la cuneta. No lleva trampa ni sifon.",
        "3. Tuberia PVC-U para desague de 4\" (NTP 399.003) con pendiente minima de %.1f %%; la longitud y el recorrido de cada sumidero son los de la planta de drenaje." % S_TUB,
        "4. Detalle del corte, la planta de la rejilla y el desagregado de materiales en la lamina DS-02.",
    ], hmm=1.8, ancho_mm=225)
    return lam


# ================================================================== DS-02: corte, planta, explosionado y desagregado
def ds02(doc, ox, oy, P, M):
    lam = B.Lamina(doc, ox, oy, 5, "DS-02", "DETALLE DE CAJA SUMIDERO DE PISO: CORTE, PLANTA Y DESAGREGADO",
                   "CORTE A-A, PLANTA DE LA REJILLA, ISOMETRICO EXPLOSIONADO Y MATERIALES POR SUMIDERO - " + P["nombre"])
    # ---------------- A. corte A-A (u = y, v = z)
    v = V(lam, 125, 480)
    lam.juntar_llamadas()
    for s in (-1, 1):
        caja = [(s * CE / 2, 0), (s * XV, 0), (s * XV, ZA), (s * XH, ZA), (s * XH, ZP), (s * RO, ZO), (s * RO, ZF), (s * CE / 2, ZF)]
        v.concreto(caja)
    v.concreto([(-0.35, -0.10), (-CE / 2, -0.10), (-CE / 2, 0), (-0.35, 0)])
    v.concreto([(CE / 2, -0.10), (0.75, -0.10), (0.75, 0), (CE / 2, 0)])
    v.concreto([(0.80, -0.60), (YCU + 0.50, -0.60), (YCU + 0.50, 0), (YCU + 0.40, 0), (YCU + 0.40, -0.50), (YCU, -0.50), (YCU, 0), (0.80, 0)])
    for s in (-1, 1):                                                       # marco (angulo cortado)
        ang = [(s * MI / 2, 0), (s * XV, 0), (s * XV, ZA), (s * XH, ZA), (s * XH, -PH), (s * MI / 2, -PH)]
        lam.relleno([v(*p) for p in ang], "MARCO-RELL"); v.pl(ang, "PLATINA", True)
        a0 = np.array([s * XV, ZA / 2]); d = np.array([s * math.sqrt(0.5), -math.sqrt(0.5)])
        v.ln(tuple(a0), tuple(a0 + d * ANCL), "PERNOS")
    for y in platinas_y():                                                  # platinas de la rejilla cortadas
        pl = [(y - PE / 2, -PH), (y + PE / 2, -PH), (y + PE / 2, 0), (y - PE / 2, 0)]
        lam.relleno([v(*p) for p in pl], "REJ-RELL"); v.pl(pl, "REJILLA", True)
    caida = S_TUB / 100 * (YCU - R - CP)
    tubo2d(v, (0, ZO + 0.01), (0, ZT + R + CP))
    codo2d(v, (0, ZT), (0, -1), (1, 0), R)
    tubo2d(v, (R + CP, ZT), (YCU, ZT - caida))
    v.ln((-0.42, 0), (-0.35, 0), "TERRENO"); v.ln((0.75, 0), (0.80, 0), "TERRENO")
    v.cota((-RJ / 2, 0), (RJ / 2, 0), 9, texto="0.25")
    v.cota((-CE / 2, 0), (CE / 2, 0), 17, texto="0.45")
    v.cota((-CE / 2 - 0.0, 0), (-CE / 2, ZP), -10, horizontal=False, texto="0.10")
    v.cota((-CE / 2, ZP), (-CE / 2, ZF), -10, horizontal=False, texto="0.10")
    v.cota((R + CP, ZT - 0.10), (YCU, ZT - 0.10), -6, texto="L variable (planta de drenaje)")
    lam.texto(v(0.48, ZT + 0.075), "S = %.1f %% min." % S_TUB, 2.2, "TEXTOS", TA.MIDDLE_CENTER)
    lam.flecha(v(0.36, ZT + 0.05), v(0.62, ZT + 0.048), "LLAMADAS")
    for p, t in (((0.0, -0.005), ["Rejilla 0.25 x 0.25: platinas 1\" x 3/16\" de canto"]),
                 ((-XV, ZA / 2), ["Marco L 1\" x 1\" x 3/16\" y anclajes 3/8\" x 3\""]),
                 ((-0.15, ZP + 0.02), ["Caja de concreto f'c = 140 kg/cm2, 0.10 m bajo el piso, fondo inclinado"]),
                 ((0.0, -0.15), ["Salida PVC-U 4\""]),
                 ((-0.05, ZT - 0.02), ["Codo PVC-U 4\" x 90° (sin trampa)"]),
                 ((0.55, ZT - 0.004 + DT / 2), ["Tuberia PVC-U 4\" hacia la cuneta"]),
                 ((0.85, -0.40), ["Cuneta de concreto (descarga sobre el fondo)"])):
        lam.llamada(v(*p), (lam.P(440, 0)[0], v(*p)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(230, 340, "CORTE A-A", "ESC. 1/5 - salida directa con un codo de 90°", 100)

    # ---------------- B. planta de la rejilla
    w = V(lam, 115, 215)
    a = RJ / 2
    w.rect(-XV, -XV, XV, XV, "PLATINA"); w.rect(-MI / 2, -MI / 2, MI / 2, MI / 2, "PLATINA")
    for y in platinas_y()[:2]:
        pl = [(-a, y - PE / 2), (a, y - PE / 2), (a, y + PE / 2), (-a, y + PE / 2)]
        lam.relleno([w(*p) for p in pl], "REJ-RELL")
    for x in (-a + PE / 2, a - PE / 2):
        pl = [(x - PE / 2, -a), (x + PE / 2, -a), (x + PE / 2, a), (x - PE / 2, a)]
        lam.relleno([w(*p) for p in pl], "REJ-RELL")
    for y in platinas_y()[2:]:
        pl = [(-a + PE, y - PE / 2), (a - PE, y - PE / 2), (a - PE, y + PE / 2), (-a + PE, y + PE / 2)]
        lam.relleno([w(*p) for p in pl], "REJ-RELL"); w.pl(pl, "REJILLA", True)
    w.rect(-CE / 2, -CE / 2, CE / 2, CE / 2, "OCULTO")
    w.circ((0, 0), RO, "OCULTO")
    s2 = math.sqrt(0.5) * ANCL
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for t in (-0.07, 0.07):
            c = (sx * XV + (t if sx == 0 else 0), sy * XV + (t if sy == 0 else 0))
            w.ln(c, (c[0] + sx * s2, c[1] + sy * s2), "PERNOS")
    w.cota((-a, a), (a, a), 10, texto="0.25"); w.cota((a, -a), (a, a), 18, horizontal=False, texto="0.25")
    w.cota((-CE / 2, -CE / 2), (CE / 2, -CE / 2), -6, texto="0.45")
    lam.juntar_llamadas()
    for p, t in (((0.0, PASO * 2), ["%d platinas interiores @0.025 (abertura 0.020)" % N_INT]),
                 ((XV, -0.03), ["Marco L 1\" x 1\" x 3/16\" (interior 0.254)"]),
                 ((XV + s2, 0.07 + s2 * 0), ["8 anclajes 3/8\" x 3\" a 45° hacia el concreto"]),
                 ((0.0, -RO), ["Salida Ø 4\" (oculta)"]),
                 ((CE / 2, -0.15), ["Caja de concreto 0.45 x 0.45 (oculta)"])):
        lam.llamada(w(*p), (lam.P(185, 0)[0], w(*p)[1]), t, 1.9)
    lam.volcar_llamadas()
    lam.titulo_vista(130, 130, "PLANTA DE LA REJILLA", "ESC. 1/5", 70)

    # ---------------- C. isometrico explosionado
    E = Escena()
    E.g = 0; caja3d(E, 0.0)
    E.g = 1; tubo3d(E, (0, 0, ZO + 0.01), (0, 0, ZT + R + CP)); E.codo((0, 0, ZT), (0, 0, -1), (0, 1, 0), R, DT / 2, ACC)
    tubo3d(E, (0, R + CP, ZT), (0, 0.42, ZT))
    E.g = 2; marco3d(E, 0.16)
    E.g = 3; rejilla3d(E, 0.30)
    P2 = E.dibujar(lam, 445, 255)
    _llamadas(lam, P2, [((0, a, 0.30), ["1. Rejilla (se retira para limpieza)"]),
                        ((XV, 0.05, 0.16), ["2. Marco con anclajes, se embebe al vaciar la caja"]),
                        ((CE / 2, 0.0, -0.05), ["3. Caja de concreto con fondo inclinado"]),
                        ((0, 0, ZT - R - DT / 2), ["4. Salida 4\" + codo de 90° + tuberia a la cuneta"])], 530, hmm=1.9)
    lam.titulo_vista(440, 95, "ISOMETRICO EXPLOSIONADO", "ESC. 1/5 - orden de armado", 100)

    # ---------------- D. desagregado de materiales
    n = M.get("sum", ("", 0))[1]
    filas = []
    for d, u, q, kg in desagregado():
        filas.append((d, u, "%.3f" % q if u == "m3" else "%.2f" % q, "%.2f" % kg if kg else "-",
                      ("%.2f" % (q * n) if u != "m3" else "%.3f" % (q * n)) + " " + u, ("%.1f kg" % (kg * n)) if kg else "-"))
    filas.append(("Acero total (platina + angulo + anclajes)", "kg", "", "%.2f" % sum(r[3] for r in desagregado() if r[3]), "",
                  "%.1f kg" % (n * sum(r[3] for r in desagregado() if r[3]))))
    yb = lam.tabla(565, 565, ["MATERIAL", "UND", "CANT./SUM.", "KG/SUM.", "TOTAL (%d und)" % n, "KG TOTAL"], filas,
                   [92, 12, 20, 18, 30, 22], hmm=1.8, alto_mm=5.4, titulo="DESAGREGADO DE MATERIALES POR SUMIDERO")
    cod = lambda k: M.get(k, ("-", 0))
    lam.notas(565, yb - 6, "NOTAS", [
        "1. Partida %s SUMIDERO METALICO C/PLATINA 1\" X 3/16\": %d und (hoja METRADO EN PISO). La tuberia de 4\" (%.2f m) y los codos de 90° (%d und) "
        "se pagan en sus propias partidas, no dentro del sumidero." % (cod("sum")[0], n, cod("tub")[1], cod("codo")[1]),
        "2. Pesos: platina 1\" x 3/16\" = %.3f kg/m, angulo L 1\" x 1\" x 3/16\" = %.2f kg/m, Ø 3/8\" = %.2f kg/m. Soldadura E6011 1/8\" en todos los encuentros." % (ACERO_P, ANG_P, VAR_P),
        "3. Acero A36 con anticorrosivo y esmalte; la rejilla se apoya en el ala del marco sin soldar, para poder retirarla.",
        "4. Salida directa con un codo de 90° (sin trampa): reemplaza la trampa del detalle anterior.",
    ], hmm=1.7, ancho_mm=200)
    return lam


def construir(clave):
    P = dict(PT[clave]); carpeta, suf = SAL[clave]
    B.PROYECTO = P["proyecto"]; B.UBICACION = P["ubicacion"]
    doc = B.nuevo_documento()
    for nm, c, lt, lw in CAPAS_EXTRA:
        if nm not in doc.layers:
            ly = doc.layers.add(nm, color=c, linetype=lt); ly.dxf.lineweight = lw
    M = metrado(P)
    laminas = {"DS-01": ds01(doc, 0.0, 0.0, P, M), "DS-02": ds02(doc, 6.0, 0.0, P, M)}
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: -1 for e in msp.query("HATCH")})        # solo rellenos 2D al fondo; los SOLID del isometrico van en su orden
    L.presentaciones(doc, laminas)
    err = len(doc.audit().errors)
    sal = os.path.join(RAIZ, carpeta, "PLANOS_DETALLE_SUMIDERO_PISO_%s.dxf" % suf)
    doc.saveas(sal)
    print("%s: DS-01, DS-02 (%d errores de auditoria) -> %s | %s" % (clave, err, os.path.relpath(sal, RAIZ), M))
    return sal


if __name__ == "__main__":
    for k in (sys.argv[1:] or SAL):
        construir(k)
