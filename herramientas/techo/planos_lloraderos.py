"""Laminas de detalle de instalacion de lloraderos en cunetas colindantes con area verde (CAR Varones y Hogar de Refugio).

Escala real (1 unidad = 1 m). DL-01 (1/10): isometrico de un tramo de cuneta con tres lloraderos @1.50 m mostrados en las
tres etapas de instalacion, y elevacion del muro desde el area verde. DL-02 (1/5): corte transversal, detalle del tubo
perforado, isometrico explosionado, procedimiento y desagregado de materiales por lloradero con el total del proyecto.
Datos: hoja METRADO LLORADEROS y ACU de lloraderos (tubo PVC Ø 3" de 0.30 m, filtro 0.30 x 0.30 x 0.30 m, geotextil
6 caras + 10 %, mortero de sellado 0.0005 m3), especificacion de lloraderos (S = 0.5 %, perforaciones Ø 3/8").
Uso: python3 herramientas/techo/planos_lloraderos.py [varones refugio]
"""
import os, sys, math, random, warnings
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
sys.path.insert(0, HERR); sys.path.insert(0, AQUI)
import openpyxl
import numpy as np
from iso3d import Escena
import dxf_base as B
import dxf_layouts as L
from ezdxf.enums import TextEntityAlignment as TA
from planos_techo import PROY as PT, CAPAS_EXTRA, V, tubo2d, leyenda_colores, _llamadas, PVC, CONC

for _e in (5, 10):
    if _e not in B.ESCALAS: B.ESCALAS.append(_e)
CAPAS_EXTRA = CAPAS_EXTRA + [("GEOTEXTIL", 150, "CONTINUOUS", 50), ("GEO-RELL", 150, "CONTINUOUS", 13),
                             ("GRAVA", 250, "CONTINUOUS", 18), ("GRAVA-RELL", 8, "CONTINUOUS", 13), ("OCULTO", 8, "HIDDEN", 18),
                             ("TERRENO-RELL", 33, "CONTINUOUS", 13), ("PERFORACION", 250, "CONTINUOUS", 18)]
B.COLOR_RGB.update({"GEO-RELL": (214, 236, 242), "GRAVA-RELL": (196, 186, 166), "TERRENO-RELL": (236, 222, 200)})
SAL = {"varones": ("entregables_varones", "CAR_VARONES", "vistas_previas"), "refugio": ("entregables", "HOGAR_REFUGIO", "vistas_previas_red_techo")}

# ------------------------------------------------------------------ geometria (m)
B_IN, E_M, H_IN = 0.40, 0.10, 0.50          # cuneta: ancho interior, espesor muros/losa, altura interior dibujada (variable)
Y_IN, Y_EX = E_M + B_IN, 2 * E_M + B_IN     # cara interior y exterior del muro colindante con el area verde
Z_TOP = E_M + H_IN                          # corona del muro
ZL = E_M + H_IN / 2                         # eje del lloradero: media altura
F = 0.30                                    # filtro localizado (cubo)
LT, DLL = 0.30, 0.076                       # tubo PVC 3": largo y diametro
S_LL = 0.5                                  # pendiente del lloradero hacia la cuneta (%)
SEP, LTR, XJ = 1.50, 4.50, 3.00             # espaciamiento, largo del tramo dibujado, junta de dilatacion
XS = [0.75, 2.25, 3.75]                     # lloraderos del tramo
N_PERF, P_PERF, D_PERF = 4, 0.05, 0.0095    # perforaciones por fila, paso y diametro (3/8")
GRAVA = [(150, 140, 125), (172, 162, 142), (128, 122, 112), (188, 178, 158), (160, 150, 135)]
GEO, TUBO, PERF_C, JUNTA_C, MURO = (214, 236, 242), PVC, (52, 56, 62), (70, 70, 70), (214, 214, 208)

# materiales por lloradero (ACU de lloraderos)
DESAG = [("Tubo PVC-U Ø 3\" (76 mm) para desague, NTP 399.003", "m", LT, "0.10 en el muro + 0.20 dentro del filtro"),
         ("Perforaciones Ø 3/8\" en el tramo del filtro", "und", 2 * N_PERF, "2 filas a 120° @0.05"),
         ("Grava filtrante (ripio) 20 a 40 mm", "m3", F ** 3 * 1.10, "0.027 m3 + 10 % de desperdicio"),
         ("Geotextil no tejido clase 2", "m2", 6 * F * F * 1.10, "6 caras del cubo + 10 % de traslapes"),
         ("Mortero 1:3 de sellado alrededor del tubo", "m3", 0.0005, "anillo de 0.02 m en las dos caras del muro"),
         ("Excavacion local del hueco del filtro", "m3", F ** 3, "incluida en la mano de obra del ACU")]


def metrado(P):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ws = openpyxl.load_workbook(os.path.join(RAIZ, "insumos", "metrados_vigentes", P["planilla"]), data_only=True)["METRADO LLORADEROS"]
    for r in ws.iter_rows(values_only=True):
        v = [c for c in r if c not in (None, "")]
        if v and isinstance(v[0], str) and v[0].upper().startswith("TOTAL DE LLORADEROS"):
            return dict(L=v[1], n=v[2])
    raise ValueError("sin total en METRADO LLORADEROS")


# ================================================================== piezas 3D
def grava_cara(E, o, u, v, a, b, rnd, dens=900):
    """Cara de grava: fondo y piedras (discos) sobre el rectangulo o + s u + t v (u, v unitarios)."""
    o, u, v = (np.asarray(x, float) for x in (o, u, v)); n = np.cross(u, v)
    E.quad(o, o + u * a, o + u * a + v * b, o + v * b, (112, 106, 98), 0.06)
    for _ in range(int(dens * a * b)):
        c = o + u * rnd.uniform(0.012, a - 0.012) + v * rnd.uniform(0.012, b - 0.012) + n * 0.0015
        E.disco(c, n, rnd.uniform(0.008, 0.016), rnd.choice(GRAVA), n=8, sesgo=0.004)


def cubo_grava(E, x0, y0, z0, rnd, dens=900):
    """Cubo de grava de lado F con origen en la esquina (x0, y0, z0); se dibujan las tres caras visibles."""
    grava_cara(E, (x0, y0, z0 + F), (1, 0, 0), (0, 1, 0), F, F, rnd, dens)          # arriba
    grava_cara(E, (x0 + F, y0, z0), (0, 1, 0), (0, 0, 1), F, F, rnd, dens)          # +x
    grava_cara(E, (x0, y0 + F, z0), (1, 0, 0), (0, 0, 1), F, F, rnd, dens)          # +y


def tubo_perforado(E, xc, y0, y1, z0, z1, perforado_desde):
    """Tubo PVC 3" de (xc, y0, z0) a (xc, y1, z1) con dos filas de perforaciones desde y = perforado_desde."""
    E.cilindro((xc, y0, z0), (xc, y1, z1), DLL / 2, TUBO, n=18, paso=0.06)
    r = DLL / 2
    for ang in (-30, -150):                                  # dos filas a 120° (simetricas respecto al fondo)
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for k in range(N_PERF):
            y = perforado_desde + 0.025 + k * P_PERF
            if not (min(y0, y1) < y < max(y0, y1)): continue
            z = z0 + (z1 - z0) * (y - y0) / (y1 - y0)
            p = (xc + r * c * 1.01, y, z + r * s * 1.01)
            E.disco(p, (c, 0, s), D_PERF / 2, PERF_C, n=8, sesgo=0.003)


def cuneta3d(E):
    tramos = [(0.0, XJ - 0.0125), (XJ + 0.0125, LTR)]
    E.g = 0
    for xa, xb in tramos:
        E.caja(xa, 0.0, 0.0, xb, Y_EX, E_M, MURO, paso=0.30)                       # losa de fondo
        E.caja(xa, 0.0, E_M, xb, E_M, Z_TOP, MURO, paso=0.30)                      # muro lejano
    E.caja(XJ - 0.0125, 0.0, 0.0, XJ + 0.0125, E_M, Z_TOP, JUNTA_C, paso=0.30)
    E.caja(XJ - 0.0125, 0.0, 0.0, XJ + 0.0125, Y_EX, E_M, JUNTA_C, paso=0.30)
    E.g = 1
    for xa, xb in tramos:
        E.caja(xa, Y_IN, E_M, xb, Y_EX, Z_TOP, MURO, paso=0.30)                    # muro colindante con el area verde
    E.caja(XJ - 0.0125, Y_IN, E_M, XJ + 0.0125, Y_EX, Z_TOP, JUNTA_C, paso=0.30)


def escena_tramo():
    rnd = random.Random(11); E = Escena()
    cuneta3d(E)
    dz = LT * S_LL / 100
    for i, xc in enumerate(XS):
        x0, y0, z0 = xc - F / 2, Y_EX, ZL - F / 2
        E.g = 2
        if i < 2:                                                                  # etapas 1 y 2: hueco forrado, geotextil abierto
            E.quad((x0, y0, z0), (x0 + F, y0, z0), (x0 + F, y0 + F, z0), (x0, y0 + F, z0), GEO, 0.08)              # fondo
            E.quad((x0, y0, z0), (x0, y0 + F, z0), (x0, y0 + F, z0 + F), (x0, y0, z0 + F), GEO, 0.08)              # cara -x
            E.quad((x0, y0, z0 + F), (x0 + F, y0, z0 + F), (x0 + F, y0 - 0.0, z0 + F + 0.12), (x0, y0, z0 + F + 0.12), GEO, 0.08)
            E.quad((x0 + F, y0 + F, z0), (x0 + F + 0.12, y0 + F, z0 - 0.06), (x0 + F + 0.12, y0, z0 - 0.06), (x0 + F, y0, z0), GEO, 0.08)  # solapa +x abierta
            E.quad((x0, y0 + F, z0), (x0 + F, y0 + F, z0), (x0 + F, y0 + F + 0.12, z0 - 0.06), (x0, y0 + F + 0.12, z0 - 0.06), GEO, 0.08)  # solapa +y abierta
        E.g = 3
        tubo_perforado(E, xc, Y_EX, Y_IN + LT, ZL + E_M * S_LL / 100, ZL + dz, Y_EX)
        E.disco((xc, Y_EX + 0.0008, ZL + E_M * S_LL / 100), (0, 1, 0), DLL / 2 + 0.012, (150, 150, 146), n=18)       # anillo de mortero
        E.g = 4
        if i == 1:
            cubo_grava(E, x0, y0, z0, rnd)
        if i == 2:
            g = 0.006
            E.caja(x0 - g, y0, z0 - g, x0 + F + g, y0 + F + g, z0 + F + g, GEO, paso=0.08)
            E.quad((x0 - g, y0 + 0.02, z0 + F + g + 0.0005), (x0 + F + g, y0 + 0.02, z0 + F + g + 0.0005),
                   (x0 + F + g, y0 + 0.12, z0 + F + g + 0.0005), (x0 - g, y0 + 0.12, z0 + F + g + 0.0005), (196, 222, 230), 0.08)   # traslape
    return E


# ================================================================== DL-01
LEY = [(MURO, "Cuneta de concreto f'c = 175 kg/cm2 (muro colindante con area verde)"), (TUBO, "Tubo PVC-U Ø 3\" perforado (lloradero)"),
       (PERF_C, "Perforaciones Ø 3/8\" (2 filas a 120° @0.05)"), (GRAVA[1], "Grava filtrante 20 a 40 mm"),
       (GEO, "Geotextil no tejido clase 2"), (JUNTA_C, "Junta de dilatacion e = 1\" con sellador asfaltico")]


def dl01(doc, ox, oy, P, M):
    lam = B.Lamina(doc, ox, oy, 10, "DL-01", "ISOMETRICO DE INSTALACION DE LLORADEROS EN CUNETAS",
                   "TRAMO JUNTO A AREA VERDE: LLORADEROS @1.50 m EN 3 ETAPAS Y ELEVACION - " + P["nombre"])
    E = escena_tramo()
    P2 = E.dibujar(lam, 115, 512)
    x0 = lambda i: XS[i] - F / 2
    items = [((x0(0) + 0.05, Y_EX + 0.05, ZL - F / 2), ["ETAPA 1: hueco de 0.30 x 0.30 x 0.30 forrado con geotextil; tubo perforado colocado"]),
             ((XS[0], Y_EX + 0.10, ZL + 0.02), ["Tubo PVC-U Ø 3\" perforado: 0.20 m dentro del filtro, S = 0.5 % hacia la cuneta"]),
             ((x0(1) + F, Y_EX + F / 2, ZL), ["ETAPA 2: grava filtrante 20 a 40 mm colocada sin danar el geotextil"]),
             ((x0(2) + F, Y_EX + F / 2, ZL + 0.05), ["ETAPA 3: geotextil cerrado con traslape de 0.10 m; luego relleno compactado"]),
             ((XJ, Y_EX, Z_TOP - 0.05), ["Junta de dilatacion cada 3.00 m: lloraderos a no menos de 0.30 m de ella"]),
             ((LTR, Y_IN + 0.05, Z_TOP), ["Muro de cuneta colindante con area verde (corona = terreno terminado)"]),
             ((LTR - 0.2, 0.05, E_M), ["Cuneta de concreto: el agua del terreno sale por los lloraderos"])]
    _llamadas(lam, P2, items, 560, hmm=2.0)
    lam.titulo_vista(120, 330, "ISOMETRICO DEL TRAMO CON LLORADEROS", "ESC. 1/10 - terreno y rejilla no dibujados para ver el filtro", 150)
    # ---------------- elevacion del muro desde el area verde
    v = V(lam, 45, 175)
    v.concreto([(0, 0), (XJ - 0.0125, 0), (XJ - 0.0125, Z_TOP), (0, Z_TOP)])
    v.concreto([(XJ + 0.0125, 0), (LTR, 0), (LTR, Z_TOP), (XJ + 0.0125, Z_TOP)])
    v.ln((XJ - 0.0125, 0), (XJ - 0.0125, Z_TOP), "CONCRETO"); v.ln((XJ + 0.0125, 0), (XJ + 0.0125, Z_TOP), "CONCRETO")
    v.ln((-0.15, Z_TOP), (LTR + 0.15, Z_TOP), "TERRENO")
    for xc in XS:
        sq = [(xc - F / 2, ZL - F / 2), (xc + F / 2, ZL - F / 2), (xc + F / 2, ZL + F / 2), (xc - F / 2, ZL + F / 2)]
        lam.relleno([v(*p) for p in sq], "GRAVA-RELL"); v.pl(sq, "GEOTEXTIL", True)
        lam.relleno([v(xc + DLL / 2 * math.cos(t), ZL + DLL / 2 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 24)], "TUBO-RELL")
        v.circ((xc, ZL), DLL / 2, "TUBO-PVC")
    v.cota((0, Z_TOP), (XS[0], Z_TOP), 8, texto="0.75")
    v.cota((XS[0], Z_TOP), (XS[1], Z_TOP), 8, texto="1.50"); v.cota((XS[1], Z_TOP), (XS[2], Z_TOP), 8, texto="1.50")
    v.cota((XS[1], Z_TOP), (XJ, Z_TOP), 15, texto="0.75 (>= 0.30)")
    v.cota((LTR, E_M), (LTR, ZL), 10, horizontal=False, texto="H/2")
    v.cota((LTR, 0), (LTR, E_M), 10, horizontal=False, texto="0.10")
    v.cota((XS[2] - F / 2, ZL - F / 2), (XS[2] + F / 2, ZL - F / 2), -5, texto="0.30")
    lam.juntar_llamadas()
    for p, t in (((XS[2] + F / 2, ZL + 0.08), ["Filtro 0.30 x 0.30 x 0.30 m con geotextil"]), ((XS[2] + DLL / 2, ZL), ["Lloradero PVC Ø 3\" a media altura"]),
                 ((LTR, 0.05), ["Losa de fondo; junta de dilatacion cada 3.00 m"])):
        lam.llamada(v(*p), (lam.P(530, 0)[0], v(*p)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(270, 135, "ELEVACION DEL MURO DESDE EL AREA VERDE", "ESC. 1/10 - tramo tipico; ubicacion de cada tramo en la hoja METRADO LLORADEROS", 150)
    leyenda_colores(lam, 640, 230, LEY)
    lam.notas(640, 172, "NOTAS", [
        "1. Lloraderos solo en los muros colindantes con area verde: %d und en %.2f m de muro (hoja METRADO LLORADEROS)." % (M["n"], M["L"]),
        "2. Espaciamiento L = 1.50 m, a media altura del muro; si ambos muros dan al area verde, se colocan en los dos.",
        "3. Detalle del corte, del tubo perforado y desagregado de materiales en la lamina DL-02.",
    ], hmm=1.8, ancho_mm=180)
    return lam


# ================================================================== DL-02
def dl02(doc, ox, oy, P, M):
    lam = B.Lamina(doc, ox, oy, 5, "DL-02", "DETALLE DE LLORADERO: CORTE, TUBO PERFORADO Y DESAGREGADO",
                   "CORTE TRANSVERSAL, TUBO PVC Ø 3\" PERFORADO, ISOMETRICO EXPLOSIONADO, PROCEDIMIENTO Y MATERIALES - " + P["nombre"])
    # ---------------- A. corte transversal (u = distancia desde la cara exterior del muro lejano, v = z)
    v = V(lam, 70, 395)
    XT = Y_EX + F + 0.18
    v.l.relleno([v(*p) for p in [(Y_EX, -0.20), (XT, -0.20), (XT, Z_TOP), (Y_EX, Z_TOP)]], "TERRENO-RELL")
    v.ln((Y_EX, Z_TOP), (XT, Z_TOP), "TERRENO")
    v.concreto([(0, 0), (Y_EX, 0), (Y_EX, Z_TOP), (Y_IN, Z_TOP), (Y_IN, E_M), (E_M, E_M), (E_M, Z_TOP), (0, Z_TOP)])
    v.l.relleno([v(*p) for p in [(0, -0.10), (Y_EX, -0.10), (Y_EX, 0), (0, 0)]], "GRAVA-RELL"); v.pl([(0, -0.10), (Y_EX, -0.10), (Y_EX, 0), (0, 0)], "CONCRETO", True)
    sq = [(Y_EX, ZL - F / 2), (Y_EX + F, ZL - F / 2), (Y_EX + F, ZL + F / 2), (Y_EX, ZL + F / 2)]
    lam.relleno([v(*p) for p in sq], "GRAVA-RELL")
    rnd = random.Random(5)
    for _ in range(70):
        c = (Y_EX + rnd.uniform(0.015, F - 0.015), ZL - F / 2 + rnd.uniform(0.015, F - 0.015))
        if abs(c[1] - ZL) < DLL / 2 + 0.012 and c[0] < Y_IN + LT - Y_IN + Y_EX: continue
        v.circ(c, rnd.uniform(0.007, 0.013), "GRAVA")
    g = 0.005
    v.pl([(Y_EX, ZL - F / 2 - g), (Y_EX + F + g, ZL - F / 2 - g), (Y_EX + F + g, ZL + F / 2 + g), (Y_EX, ZL + F / 2 + g)], "GEOTEXTIL")
    dz = LT * S_LL / 100
    tubo2d(v, (Y_IN, ZL), (Y_IN + LT, ZL + dz), DLL / 2)
    for k in range(N_PERF):
        u = Y_EX + 0.025 + k * P_PERF
        for s in (-1, 1):
            v.circ((u, ZL + dz * (u - Y_IN) / LT + s * DLL / 4), D_PERF / 2, "PERFORACION")
    v.ln((Y_IN - 0.02, ZL - 0.06), (Y_IN - 0.15, ZL - 0.06), "LLAMADAS")
    lam.flecha(v(Y_IN - 0.05, ZL - 0.06), v(Y_IN - 0.15, ZL - 0.06), "LLAMADAS")
    lam.texto(v(Y_IN - 0.10, ZL - 0.04), "S = 0.5 %", 2.0, "TEXTOS", TA.BOTTOM_CENTER)
    v.cota((0, -0.10), (E_M, -0.10), -7, texto="0.10"); v.cota((E_M, -0.10), (Y_IN, -0.10), -7, texto="0.40")
    v.cota((Y_IN, -0.10), (Y_EX, -0.10), -7, texto="0.10")
    v.cota((Y_EX, ZL + F / 2), (Y_EX + F, ZL + F / 2), 8, texto="0.30")
    v.cota((Y_EX + F, ZL - F / 2), (Y_EX + F, ZL + F / 2), 12, horizontal=False, texto="0.30")
    v.cota((Y_IN, ZL - F / 2 - 0.04), (Y_IN + LT, ZL - F / 2 - 0.04), -4, texto="L = 0.30")
    v.cota((E_M + 0.06, E_M), (E_M + 0.06, ZL), 0.1, horizontal=False, texto="H/2")
    v.cota((E_M + 0.20, E_M), (E_M + 0.20, Z_TOP), 0.1, horizontal=False, texto="H variable")
    lam.juntar_llamadas()
    for p, t in (((XT - 0.05, Z_TOP), ["Area verde: terreno natural con cobertura vegetal"]),
                 ((Y_EX + F + g, ZL + 0.10), ["Geotextil no tejido clase 2 (traslapes de 0.10 m)"]),
                 ((Y_EX + 0.22, ZL + 0.09), ["Grava filtrante 20 a 40 mm, limpia y lavada"]),
                 ((Y_EX + 0.10, ZL + DLL / 2), ["Tubo PVC-U Ø 3\": tramo de 0.20 m perforado dentro del filtro"]),
                 ((Y_IN + 0.05, ZL - DLL / 2), ["Tramo de 0.10 m en el muro, sellado con mortero 1:3"]),
                 ((Y_EX - 0.03, 0.18), ["Muro y losa de cuneta f'c = 175 kg/cm2, e = 0.10 m"]),
                 ((XT - 0.08, ZL - F / 2 - 0.08), ["Relleno compactado con material propio"]),
                 ((Y_EX - 0.1, -0.05), ["Solado f'c = 100 kg/cm2, e = 4\""])):
        lam.llamada(v(*p), (lam.P(300, 0)[0], v(*p)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(175, 330, "CORTE TRANSVERSAL DE LA CUNETA", "ESC. 1/5 - lloradero en el muro colindante con area verde", 120)

    # ---------------- B. tubo perforado (elevacion y seccion)
    w = V(lam, 60, 225)
    tubo2d(w, (0, 0), (LT, 0), DLL / 2)
    w.ln((E_M, -DLL / 2 - 0.01), (E_M, DLL / 2 + 0.01), "OCULTO")
    for k in range(N_PERF):
        u = E_M + 0.025 + k * P_PERF
        for s in (-1, 1): w.circ((u, s * DLL / 4), D_PERF / 2, "PERFORACION")
    w.cota((0, DLL / 2), (E_M, DLL / 2), 6, texto="0.10 (muro)"); w.cota((E_M, DLL / 2), (LT, DLL / 2), 6, texto="0.20 perforado")
    w.cota((0, -DLL / 2), (LT, -DLL / 2), -7, texto="0.30")
    w.cota((E_M + 0.025, -DLL / 2), (E_M + 0.075, -DLL / 2), -14, texto="@0.05")
    c = (LT + 0.16, 0.0)
    w.circ(c, DLL / 2, "TUBO-PVC")
    for ang in (-30, -150):
        a = math.radians(ang)
        w.ln((c[0] + 0.6 * DLL / 2 * math.cos(a), c[1] + 0.6 * DLL / 2 * math.sin(a)), (c[0] + 1.25 * DLL / 2 * math.cos(a), c[1] + 1.25 * DLL / 2 * math.sin(a)), "PERFORACION")
    w.ln((c[0], c[1]), (c[0], c[1] - DLL / 2 - 0.02), "OCULTO")
    lam.texto(w(c[0], c[1] - DLL / 2 - 0.045), "120°", 2.0, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto(w(c[0], c[1] + DLL / 2 + 0.025), "SECCION", 2.0, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto(w(LT / 2, -DLL / 2 - 0.105), "%d perforaciones Ø 3/8\": 2 filas a 120° (simetricas respecto al fondo), %d por fila" % (2 * N_PERF, N_PERF), 2.0, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(110, 150, "TUBO PVC-U Ø 3\" PERFORADO", "ESC. 1/5", 90)

    # ---------------- C. isometrico explosionado
    rnd = random.Random(3); E = Escena()
    E.g = 0; E.caja(-0.15, 0.0, 0.0, 0.15, E_M, 0.45, MURO, paso=0.10)                                        # 1. muro con el pase
    E.disco((0, E_M + 0.0008, 0.225), (0, 1, 0), DLL / 2 + 0.012, (150, 150, 146), n=18)
    E.disco((0, E_M + 0.0012, 0.225), (0, 1, 0), DLL / 2, (40, 44, 50), n=18)
    E.g = 1; tubo_perforado(E, 0.0, 0.22, 0.52, 0.225, 0.2265, 0.32)                                        # 2. tubo perforado
    E.g = 2; cubo_grava(E, 0.72, 0.12, 0.08, rnd, 700)                                                      # 3. grava
    E.g = 3                                                                                                 # 4. geotextil abierto (fondo + 4 solapas)
    gx, gy, gz = 1.38, 0.06, 0.30
    E.quad((gx, gy, gz), (gx + F, gy, gz), (gx + F, gy + F, gz), (gx, gy + F, gz), GEO, 0.08)
    E.quad((gx, gy, gz), (gx, gy + F, gz), (gx - 0.08, gy + F, gz + 0.14), (gx - 0.08, gy, gz + 0.14), GEO, 0.08)
    E.quad((gx, gy, gz), (gx + F, gy, gz), (gx + F, gy - 0.08, gz + 0.14), (gx, gy - 0.08, gz + 0.14), GEO, 0.08)
    E.quad((gx + F, gy, gz), (gx + F, gy + F, gz), (gx + F + 0.12, gy + F, gz + 0.04), (gx + F + 0.12, gy, gz + 0.04), GEO, 0.08)
    E.quad((gx, gy + F, gz), (gx + F, gy + F, gz), (gx + F, gy + F + 0.12, gz + 0.04), (gx, gy + F + 0.12, gz + 0.04), GEO, 0.08)
    P2 = E.dibujar(lam, 300, 255)
    _llamadas(lam, P2, [((0.15, E_M, 0.40), ["1. Muro de cuneta con el pase del tubo (mortero 1:3)"]),
                        ((0.0, 0.42, 0.225 + DLL / 2), ["2. Tubo PVC-U Ø 3\" de 0.30 m con 8 perforaciones Ø 3/8\""]),
                        ((0.72 + F, 0.12 + F / 2, 0.08 + F), ["3. Grava 20 a 40 mm: 0.027 m3 por lloradero"]),
                        ((gx + F + 0.12, gy + F / 2, gz + 0.04), ["4. Geotextil clase 2: 0.59 m2, se cierra sobre la grava"])], 655, hmm=1.9)
    lam.titulo_vista(410, 95, "ISOMETRICO EXPLOSIONADO DE UN LLORADERO", "ESC. 1/5 - piezas por separado", 120)

    # ---------------- D. desagregado y procedimiento
    n = M["n"]
    filas = [(d, u, ("%.4f" % q if u == "m3" else "%.2f" % q) if u != "und" else "%d" % q,
              ("%.2f" % (q * n) if u != "und" else "%d" % (q * n)) + " " + u, s) for d, u, q, s in DESAG]
    yb = lam.tabla(565, 565, ["MATERIAL", "UND", "POR LLORADERO", "TOTAL (%d und)" % n, "CRITERIO"], filas, [70, 10, 22, 26, 56],
                   hmm=1.7, alto_mm=5.4, titulo="DESAGREGADO DE MATERIALES POR LLORADERO")
    lam.notas(565, yb - 6, "PROCEDIMIENTO DE INSTALACION", [
        "1. Antes del vaciado del muro, fijar al encofrado el tubo PVC Ø 3\" de 0.30 m, ya perforado, a media altura, con S = 0.5 % hacia la cuneta y sus extremos tapados.",
        "2. Vaciar el muro; al desencofrar, destapar el tubo y sellar su contorno con mortero 1:3 en las dos caras si quedo holgura.",
        "3. Excavar en el lado del terreno el hueco de 0.30 x 0.30 x 0.30 m centrado en el tubo y forrarlo con el geotextil, dejando las solapas afuera.",
        "4. Llenar con grava 20 a 40 mm limpia, acomodandola alrededor del tramo perforado sin romper el geotextil.",
        "5. Cerrar el geotextil por encima con traslape de 0.10 m y rellenar y compactar el terreno en capas de 0.15 m.",
        "6. Prueba: al verter agua sobre el filtro debe salir por el lloradero dentro de la cuneta; se repara el que no drene.",
    ], hmm=1.7, ancho_mm=195)
    return lam


def construir(clave):
    P = dict(PT[clave]); carpeta, suf, _ = SAL[clave]
    B.PROYECTO = P["proyecto"]; B.UBICACION = P["ubicacion"]
    doc = B.nuevo_documento()
    for nm, c, lt, lw in CAPAS_EXTRA:
        if nm not in doc.layers:
            ly = doc.layers.add(nm, color=c, linetype=lt); ly.dxf.lineweight = lw
    M = metrado(P)
    laminas = {"DL-01": dl01(doc, 0.0, 0.0, P, M), "DL-02": dl02(doc, 10.0, 0.0, P, M)}
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: -1 for e in msp.query("HATCH")})        # solo rellenos 2D al fondo; los SOLID del isometrico van en su orden
    L.presentaciones(doc, laminas)
    err = len(doc.audit().errors)
    sal = os.path.join(RAIZ, carpeta, "PLANOS_DETALLE_LLORADEROS_%s.dxf" % suf)
    doc.saveas(sal)
    print("%s: DL-01, DL-02 (%d errores de auditoria) -> %s | %s" % (clave, err, os.path.relpath(sal, RAIZ), M))
    return sal


if __name__ == "__main__":
    for k in (sys.argv[1:] or SAL):
        construir(k)
