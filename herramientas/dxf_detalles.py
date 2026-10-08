"""Laminas de detalle constructivo por partida (DD-01 a DD-04): registros (contramarco, marco, tapa),
juntas (dilatacion y tecnopor) y empalme de cuneta. Cada lamina lleva despiece, dimensiones, procedimiento
y un cuadro de componentes por unidad para el analisis de costos unitarios.

Lamina base 1/10 (f = 0.01 m/mm). Cada vista se dibuja con un factor k = 10 / escala_de_la_vista
(1/10 -> k = 1, 1/5 -> k = 2, 1/2 -> k = 5, 1/1 -> k = 10); las cotas llevan el texto real.
Los textos de las llamadas se ubican en mm de papel (columna a la derecha de cada vista, ordenada de arriba
hacia abajo como los puntos que senalan) para que las lineas no se crucen.
"""
import math, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import diseno as dz, dxf_base as B, metrado_calc as MC
from ezdxf.enums import TextEntityAlignment as TA

D = dz.D
IN = 0.0254
L2 = (2 * IN, 3 / 16 * IN)          # angulo 2" x 2" x 3/16" : 50.8 x 4.76 mm
L15 = (1.5 * IN, 1 / 8 * IN)        # angulo 1 1/2" x 1 1/2" x 1/8" : 38.1 x 3.18 mm
D38 = 0.0095; D12 = 0.0127
AB = 0.70        # abertura en la losa (luz entre caras de concreto)
TAPA = 0.68; ET = 0.08
HOLG = 0.01        # (0.70 - 0.68) / 2
ASA = dict(ancho=0.12, pata=0.025, gancho=0.115)     # desarrollo 0.12 + 2 x 0.025 + 2 x 0.115 = 0.40
CAJ = dict(largo=0.18, ancho=0.06, prof=0.03)        # cajuela del asa


def L_sec(lam, p, leg, t, k, dx=1, dy=1, capa="MARCO-METALICO"):
    """Seccion de angulo L: vertice en p; alas de longitud leg hacia dx (horizontal) y dy (vertical)."""
    x, y = p
    pts = [(x, y), (x + dx * leg * k, y), (x + dx * leg * k, y + dy * t * k), (x + dx * t * k, y + dy * t * k), (x + dx * t * k, y + dy * leg * k), (x, y + dy * leg * k)]
    lam.poli(pts, capa, cerrada=True); lam.relleno(pts, capa)
    return pts


def barra(lam, p1, p2, dia, k, capa="ACERO"):
    lam.poli([p1, p2], capa, ancho=dia * k)


def punto_barra(lam, p, dia, k):
    lam.bloque("ACERO-38" if dia < 0.011 else "ACERO-12", p, k)


def hatch_conc(lam, pts, esc=0.5):
    lam.poli(pts, "CONCRETO", cerrada=True, ancho=0.003)
    lam.achurado(pts, escala_mm=esc)


def tecnopor(lam, pts):
    lam.poli(pts, "JUNTAS", cerrada=True)
    lam.achurado(pts, "JUNTAS", patron="ANSI37", escala_mm=0.35)


def LL(lam, p_obj, xt, yt, lineas):
    lam.llamada(p_obj, lam.P(xt, yt), lineas, 1.8)


def cuadro(lam, xmm, ymm, titulo, filas, anchos=(96, 14, 24, 26, 70), cab=("COMPONENTE", "UND", "CANT. / UND", "x TOTAL", "PARTIDA / OBSERVACION")):
    return lam.tabla(xmm, ymm, list(cab), filas, list(anchos), 1.7, 4.6, titulo)


TXT_REG_A = "1 por registro: 7 en la losa del colector, 1 en CL y 2 en CC"
TXT_REG_B = "10 und (RS-01 a RS-07, CL y 2 en CC)"
TXT_JUNTA_CAJAS = ("Las cajas CL y CC llevan tecnopor en su contacto", "con el colector (en el perimetro de la caja).")
TXT_DD04_SUB = "PARTIDA 01.04.04.06.03 - 6 EMPALMES (CUNETAS EJES 01, 02, 06, 07, 11 Y 12) - ESC. INDICADAS"
TXT_DD03_C = "ESC. 1/10 - tramo 0+000.00 a 0+058.81 (pegado al cerco)"
CON_CERCO = True
TIT_DD03_C = "C. JUNTA DE TECNOPOR CONTRA EL CERCO"
N_EMPALMES_TXT = "6 und"
EJ_DD04 = 11.27
TXT_DD04_CUNETA = "(Ejes 11 y 12 prolongadas hasta el muro)"
SUB_N_REG = "10 REGISTROS"; SUB_N_TAPAS = "10 TAPAS"; SUB_N_JUNTAS = "17 JUNTAS"     # cantidades en los subtitulos
ANCHO_PROC_DD03 = None     # ancho del procedimiento de la DD-03 (None: hasta el borde)
NOTA4_DD03 = "4. Juntas de tecnopor (02): plancha de 1\" pegada al cimiento del cerco antes de vaciar el muro; plancha de 1\" x 0.10 en el borde de la losa antes de vaciar el piso."


def f2(v): return "%.2f" % v
def f3(v): return "%.3f" % v


# ============================================================================= DD-01 contramarco
def dd01(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 10, "DD-01", "DETALLE CONSTRUCTIVO: CONTRAMARCO METALICO L 2\"x2\"x3/16\" CON ANCLAJES",
                   "PARTIDAS 01.04.04.05.01, 01.04.04.05.03 (parte) y 01.04.04.05.06 (parte) - %s - ESC. INDICADAS" % SUB_N_REG)
    lam.juntar_llamadas()
    leg, t = L2
    # ---------------- A. planta del contramarco (1/5)
    k = 2.0; ox_, oy_ = lam.P(150, 430)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    a = AB / 2; s_ = 0.55
    lam.rect(*P(-s_, -s_), *P(s_, s_), "CONCRETO")                                   # losa alrededor
    lam.rect(*P(-a - 0.10, -a - 0.10), *P(a + 0.10, a + 0.10), "CONCRETO-OCULTO")    # borde engrosado (oculto)
    for s in (-1, 1):
        lam.rect(*P(s * a, -a), *P(s * (a + t), a), "MARCO-METALICO"); lam.rect(*P(-a, s * a), *P(a, s * (a + t)), "MARCO-METALICO")
    lam.rect(*P(-a, -a), *P(a, a), "MARCO-METALICO", const_width=0.004)
    lam.rect(*P(-a + leg, -a + leg), *P(a - leg, a - leg), "MARCO-METALICO", const_width=0.004)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        lam.linea(P(sx * (a + t), sy * (a + t)), P(sx * (a - leg), sy * (a - leg)), "MARCO-METALICO")
    for s in (-1, 1):
        for u in (-0.175, 0.175):
            barra(lam, P(s * (a + t), u), P(s * (a + t + 0.20), u), D38, k); barra(lam, P(u, s * (a + t)), P(u, s * (a + t + 0.20)), D38, k)
    for s in (-1, 1):
        for d in (a + 0.04, a + 0.075):
            lam.linea(P(s * d, -s_), P(s * d, s_), "ACERO-LONG"); lam.linea(P(-s_, s * d), P(s_, s * d), "ACERO-LONG")
    lam.cota(P(-a + leg, -s_), P(a - leg, -s_), -4, texto="0.60 (luz libre entre alas)")
    lam.cota(P(-a, -s_), P(a, -s_), -9, texto="0.70 (luz entre caras de concreto)")
    lam.cota(P(-a - 0.10, -s_), P(a + 0.10, -s_), -14, texto="0.90 (borde engrosado)")
    lam.cota(P(s_, -0.175), P(s_, 0.175), 5, horizontal=False, texto="0.35")
    lam.cota(P(s_, 0.175), P(s_, a + t), 5, horizontal=False, texto="0.175"); lam.cota(P(s_, -a - t), P(s_, -0.175), 5, horizontal=False, texto="0.175")
    xt = 290
    LL(lam, P(a + t / 2, 0.30), xt, 540, ["ala vertical del angulo L 2\"x2\"x3/16\" pegada a la cara de la abertura"])
    LL(lam, P(a - leg / 2, 0.10), xt, 515, ["ala horizontal hacia adentro: asiento de la tapa (2\" = 50.8 mm)"])
    LL(lam, P(a + 0.12, 0.175 + 0.03), xt, 490, ["anclaje 3/8\" L = 0.20 soldado al ala vertical, 2 por lado (8 por registro)"])
    LL(lam, P(a + 0.04, -0.40), xt, 465, ["refuerzo de borde: 2 barras 1/2\" por lado, L = 1.40 (DP-06B)"])
    LL(lam, P(a + 0.10, -0.46), xt, 440, ["borde engrosado 0.15 x 0.10 bajo la losa (en la partida de losa superior)"])
    LL(lam, P(a - leg / 2, -a + leg / 2), xt, 415, ["esquina a inglete de 45 soldada (4 por registro)"])
    lam.titulo_vista(150, 290, "A. CONTRAMARCO - PLANTA", "ESC. 1/5 - " + TXT_REG_A, 150)
    # ---------------- B. seccion del contramarco colocado (1/2)
    k = 5.0; ox_, oy_ = lam.P(560, 470)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    conc = [P(0, 0), P(0.30, 0), P(0.30, -0.10), P(0.10, -0.10), P(0.10, -0.20), P(-0.05, -0.20), P(-0.05, -ET - t), P(-t, -ET - t), P(-t, -ET - leg), P(0, -ET - leg)]
    hatch_conc(lam, conc, 0.8)
    L_sec(lam, P(0, -ET), leg, t, k, dx=-1, dy=-1)                                     # angulo invertido
    barra(lam, P(0, -0.115), P(0.18, -0.025), D38, k)                                  # anclaje inclinado hacia la losa
    lam.solido([P(0, -0.107), P(0.012, -0.107), P(0.012, -0.123), P(0, -0.123)], "MARCO-METALICO")
    punto_barra(lam, P(0.05, -0.16), D12, k); punto_barra(lam, P(0.085, -0.16), D12, k)
    barra(lam, P(0.14, -0.05), P(0.30, -0.05), D38, k)
    tapa = [P(-0.30, -ET), P(-HOLG, -ET), P(-HOLG, 0), P(-0.30, 0)]
    lam.poli(tapa, "REGISTRO-TAPA", cerrada=True); lam.achurado(tapa, escala_mm=0.6)
    L_sec(lam, P(-HOLG, -ET), L15[0], L15[1], k, dx=-1, dy=1)
    lam.linea(P(0, -0.01), P(0.01, 0), "CONCRETO")
    lam.poli([P(-0.30, 0), P(-HOLG, 0)], "TERRENO", ancho=0.002); lam.poli([P(0, 0), P(0.30, 0)], "TERRENO", ancho=0.002)
    lam.nivel(P(0.22, 0), D["NPT"], texto="NPT +%.2f" % D["NPT"])
    lam.cota(P(-leg + t, -ET), P(t, -ET), -5, texto='2"')
    lam.cota(P(0.30, -ET - leg), P(0.30, -ET), 5, horizontal=False, texto='2"'); lam.cota(P(0.30, -ET), P(0.30, 0), 5, horizontal=False, texto="0.08")
    lam.cota(P(0.30, -0.20), P(0.30, -0.10), 11, horizontal=False, texto="0.10"); lam.cota(P(0.30, -0.10), P(0.30, 0), 11, horizontal=False, texto="0.10")
    lam.cota(P(0, -0.20), P(0.18, -0.20), -6, texto="0.18 (anclaje en proyeccion)"); lam.cota(P(-HOLG, 0), P(0, 0), 5, texto="1 cm")
    xt = 735
    LL(lam, P(-leg / 2, -ET - t / 2), xt, 560, ["ala horizontal: asiento de la tapa,", "a 0.08 bajo el NPT"])
    LL(lam, P(-t / 2, -ET - leg / 2), xt, 540, ["ala vertical embutida, cara exterior", "al ras de la abertura"])
    LL(lam, P(0.09, -0.07), xt, 520, ["anclaje 3/8\" L = 0.20 inclinado hacia la losa;", "cordon 3/16\" x 25 mm a ambos lados"])
    LL(lam, P(0.0675, -0.16), xt, 500, ["refuerzo de borde 2 x 1/2\" (DP-06B)"])
    LL(lam, P(0.22, -0.05), xt, 480, ["marcos del colector 3/8\" (DP-04)"])
    LL(lam, P(0.005, -0.005), xt, 460, ["chaflan 1 x 1 cm en la arista", "de la abertura"])
    LL(lam, P(-0.15, -ET / 2), xt, 440, ["tapa 0.68 x 0.08 con su marco (DD-02),", "holgura 1 cm por lado"])
    lam.titulo_vista(560, 325, "B. SECCION DEL CONTRAMARCO COLOCADO", "ESC. 1/2 - angulo con el ala vertical hacia abajo; la tapa queda al ras del NPT", 190)
    # ---------------- C. despiece (1/5)
    k = 2.0; ox_, oy_ = lam.P(60, 245)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    for i in range(4):
        y = -i * 0.10
        pts = [P(0, y), P(AB + 2 * t, y), P(AB + 2 * t - leg - t, y - leg), P(leg + t, y - leg)]
        lam.poli(pts, "MARCO-METALICO", cerrada=True); lam.relleno(pts, "MARCO-METALICO")
        lam.texto(P(AB + 2 * t + 0.05, y - leg / 2), "P%d: angulo L 2\"x2\"x3/16\" x 0.71 (ingletes 45)" % (i + 1), 1.8, "TEXTOS", TA.MIDDLE_LEFT)
    lam.cota(P(0, 0), P(AB + 2 * t, 0), 5, texto="0.71")
    lam.cota(P(0, -0.30 - leg), P(leg + t, -0.30 - leg), -5, texto="0.055")
    y0 = -0.47
    for i in range(8):
        x = 0.05 + i * 0.12
        barra(lam, P(x, y0), P(x, y0 - 0.20), D38, k); lam.texto(P(x, y0 - 0.23), "A%d" % (i + 1), 1.6, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto(P(1.05, y0 - 0.10), "A1 a A8: anclajes 3/8\" corrugado L = 0.20 (8 por registro)", 1.8, "TEXTOS", TA.MIDDLE_LEFT)
    lam.cota(P(0.05, y0 - 0.20), P(0.05, y0), -6, horizontal=False, texto="0.20")
    lam.titulo_vista(150, 85, "C. DESPIECE DEL CONTRAMARCO", "ESC. 1/5 - 4 angulos + 8 anclajes por registro", 150)
    # ---------------- procedimiento, cuadro y leyenda
    lam.notas(330, 255, "PROCEDIMIENTO", [
        "1. Cortar 4 piezas de angulo L 2\"x2\"x3/16\" de 0.71 m con los extremos a inglete de 45 y armar el cuadro de 0.70 x 0.70 (medida exterior de las alas verticales).",
        "2. Soldar las 4 esquinas con electrodo E6011 de 1/8\" (cordon 3/16\" por ambas caras); verificar escuadra (diagonales iguales) y planitud.",
        "3. Soldar 8 anclajes 3/8\" L = 0.20 a la cara exterior del ala vertical (2 por lado, a 0.175 de las esquinas), inclinados hacia la losa; cordon 3/16\" x 25 mm a ambos lados.",
        "4. Limpiar escoria; 2 manos de anticorrosivo epoxico y 2 de esmalte sintetico (partida 01.04.04.05.07), salvo en la zona de los anclajes.",
        "5. Fijar el contramarco al encofrado de la losa con el asiento a 0.08 bajo el NPT, nivelado y amarrado al refuerzo de borde; vaciar la losa con el borde engrosado.",
        "6. Al desencofrar, retirar rebabas; la tapa con su marco debe asentar en las 4 alas con holgura de 1 cm por lado."], 1.8)
    n = MC.registros()["n"]
    L_ang = 4 * (AB + 2 * t); kg_ang = L_ang * MC.ANG["2x2x3/16"]; L_anc = 8 * 0.20; kg_anc = L_anc * MC.PESO["3/8"]; L_cord = 4 * 2 * leg + 8 * 2 * 0.025
    filas = [["Angulo L 2\"x2\"x3/16\" (4 piezas de 0.71 m, 3.63 kg/m)", "m / kg", "%.2f / %.2f" % (L_ang, kg_ang), "%.2f / %.2f" % (n * L_ang, n * kg_ang), "01.04.04.05.03 ANGULOS METALICOS (kg)"],
             ["Anclajes 3/8\" corrugado L = 0.20 (8 und, 0.56 kg/m)", "m / kg", "%.2f / %.2f" % (L_anc, kg_anc), "%.2f / %.2f" % (n * L_anc, n * kg_anc), "01.04.04.05.06 ACERO EN TAPAS, BORDES Y ANCLAJES"],
             ["Cordon de soldadura 3/16\" (4 esquinas x 2 caras + 8 anclajes x 2 lados)", "m", f2(L_cord), f2(n * L_cord), "electrodo E6011 1/8\": aprox. 0.12 kg por registro"],
             ["Refuerzo de borde de la abertura 2 x 1/2\" por lado, L = 1.40 (8 barras)", "m / kg", "%.2f / %.2f" % (11.2, 11.2 * MC.PESO["1/2"]), "%.2f / %.2f" % (n * 11.2, n * 11.2 * MC.PESO["1/2"]), "01.04.04.05.06 (ver DP-06B)"],
             ["Borde engrosado 0.15 x 0.10, perimetro medio 3.00 m", "m3", f3(0.045), f2(n * 0.045), "01.04.04.04.03 LOSA SUPERIOR (ya incluido)"],
             ["Pintura anticorrosiva + esmalte (desarrollo 0.203 m2/m x 2.80 m)", "m2", f2(2.80 * 0.203), f2(n * 2.80 * 0.203), "01.04.04.05.07 PINTURA (parte)"],
             ["Mano de obra de habilitacion, soldadura y colocacion", "und", "1", "%d" % n, "01.04.04.05.01 CONTRAMARCO (und)"]]
    cuadro(lam, 330, 200, "CUADRO DE COMPONENTES POR CONTRAMARCO (1 und) Y TOTAL (%d und)" % MC.registros()["n"], filas)
    lam.leyenda2(560, 150, [("relleno", "MARCO-METALICO", "angulo metalico"), ("linea2", "ACERO", "anclaje 3/8\""), ("linea2", "ACERO-LONG", "refuerzo de borde 1/2\" (proyeccion)"), ("concreto", "CONCRETO", "concreto f'c=210"), ("rect", "REGISTRO-TAPA", "tapa (referencia, ver DD-02)")], 1.8)
    lam.volcar_llamadas()
    return lam


# ============================================================================= DD-02 marco y tapa
def dd02(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 10, "DD-02", "DETALLE CONSTRUCTIVO: MARCO METALICO L 1 1/2\"x1 1/2\"x1/8\" Y TAPA DE CONCRETO ARMADO 0.68 x 0.68 x 0.08",
                   "PARTIDAS 01.04.04.05.02, .05.03 (parte), .05.04, .05.05, .05.06 (parte) y .05.07 - %s - ESC. INDICADAS" % SUB_N_TAPAS)
    lam.juntar_llamadas()
    leg, t = L15; a = TAPA / 2
    # ---------------- A. planta de la tapa (1/5)
    k = 2.0; ox_, oy_ = lam.P(150, 430)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    lam.rect(*P(-a, -a), *P(a, a), "REGISTRO-TAPA", const_width=0.004)
    lam.rect(*P(-a + leg, -a + leg), *P(a - leg, a - leg), "MARCO-METALICO")
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)): lam.linea(P(sx * a, sy * a), P(sx * (a - leg), sy * (a - leg)), "MARCO-METALICO")
    for i in range(7):
        d = -0.30 + i * 0.10
        barra(lam, P(-0.31, d), P(0.31, d), D38, k); barra(lam, P(d, -0.31), P(d, 0.31), D38, k, "ACERO-LONG")
    for xa in (-0.15, 0.15):
        lam.rect(*P(xa - CAJ["largo"] / 2, -CAJ["ancho"] / 2), *P(xa + CAJ["largo"] / 2, CAJ["ancho"] / 2), "CONCRETO-OCULTO")
        barra(lam, P(xa - ASA["ancho"] / 2, 0), P(xa + ASA["ancho"] / 2, 0), D38, k, "MARCO-METALICO")
        barra(lam, P(xa - ASA["ancho"] / 2 - ASA["gancho"], 0.012), P(xa - ASA["ancho"] / 2, 0.012), D38, k, "CONCRETO-OCULTO")
        barra(lam, P(xa + ASA["ancho"] / 2, 0.012), P(xa + ASA["ancho"] / 2 + ASA["gancho"], 0.012), D38, k, "CONCRETO-OCULTO")
    lam.cota(P(-a, -a), P(a, -a), -6, texto="0.68"); lam.cota(P(-0.31, -a), P(0.31, -a), -11, texto="0.62 (barras)")
    lam.cota(P(a, -a), P(a, a), 6, horizontal=False, texto="0.68")
    lam.cota(P(-0.30, a), P(-0.20, a), 5, texto="0.10"); lam.cota(P(-a, a), P(-0.30, a), 5, texto="0.04")
    xt = 265
    LL(lam, P(a - leg / 2, 0.25), xt, 530, ["marco perimetral: angulo L 1 1/2\"x1 1/2\"x1/8\",", "ala horizontal bajo la tapa (proyeccion)"])
    LL(lam, P(0.20, 0.20), xt, 500, ["parrilla 7 + 7 barras 3/8\" @0.10, L = 0.62;", "extremos soldados por puntos al ala vertical del marco"])
    LL(lam, P(0.15 + 0.03, 0.0), xt, 470, ["asa en U de 3/8\" liso (2 und) en cajuela 0.18 x 0.06 x 0.03", "para que no sobresalga; ganchos amarrados a la parrilla"])
    LL(lam, P(a - leg / 2, -a + leg / 2), xt, 440, ["esquina a inglete de 45 soldada"])
    lam.titulo_vista(150, 335, "A. TAPA DE CONCRETO ARMADO - PLANTA (armado)", "ESC. 1/5 - " + TXT_REG_B, 150)
    # ---------------- B. corte de la tapa (1/2)
    k = 5.0; ox_, oy_ = lam.P(520, 490)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    tapa = [P(-a, 0), P(a, 0), P(a, ET), P(-a, ET)]
    lam.poli(tapa, "REGISTRO-TAPA", cerrada=True, ancho=0.003); lam.achurado(tapa, escala_mm=0.8)
    L_sec(lam, P(-a, 0), leg, t, k, dx=1, dy=1); L_sec(lam, P(a, 0), leg, t, k, dx=-1, dy=1)
    for i in range(7): punto_barra(lam, P(-0.30 + i * 0.10, 0.03), D38, k)
    barra(lam, P(-0.31, 0.03 + D38), P(0.31, 0.03 + D38), D38, k, "ACERO-LONG")
    xa = -0.15; yt = ET - CAJ["prof"] - 0.008
    caj = [P(xa - CAJ["largo"] / 2, ET), P(xa + CAJ["largo"] / 2, ET), P(xa + CAJ["largo"] / 2, ET - CAJ["prof"]), P(xa - CAJ["largo"] / 2, ET - CAJ["prof"])]
    lam.solido([caj[0], caj[1], caj[3], caj[2]], "ISO-TAPA"); lam.poli(caj, "REGISTRO-TAPA", cerrada=True)
    w = ASA["ancho"] / 2
    lam.poli([P(xa - w - ASA["gancho"], yt - ASA["pata"]), P(xa - w, yt - ASA["pata"]), P(xa - w, yt), P(xa + w, yt), P(xa + w, yt - ASA["pata"]), P(xa + w + ASA["gancho"], yt - ASA["pata"])], "MARCO-METALICO", ancho=D38 * k)
    lam.cota(P(-a, 0), P(a, 0), -6, texto="0.68"); lam.cota(P(a, 0), P(a, ET), 8, horizontal=False, texto="0.08"); lam.cota(P(a, 0), P(a, 0.03), 4, horizontal=False, texto="0.03")
    lam.cota(P(-a, 0), P(-a + leg, 0), -11, texto='1 1/2"'); lam.cota(P(xa - CAJ["largo"] / 2, ET), P(xa + CAJ["largo"] / 2, ET), 5, texto="0.18")
    xt = 700
    LL(lam, P(a - leg / 2, t / 2), xt, 560, ["marco L 1 1/2\"x1 1/2\"x1/8\": ala vertical al ras", "del canto, ala horizontal embutida en el fondo"])
    LL(lam, P(0.20, 0.03), xt, 535, ["parrilla 3/8\" @0.10 ambos sentidos,", "recubrimiento inferior 0.03"])
    LL(lam, P(xa + w + 0.05, yt - ASA["pata"]), xt, 510, ["asa 3/8\" liso: ancho 0.12, patas 0.025,", "ganchos de 0.115 bajo la parrilla (L = 0.40)"])
    LL(lam, P(xa, ET - 0.015), xt, 485, ["cajuela 0.18 x 0.06 x 0.03 (molde de madera", "o tecnopor en el vaciado)"])
    lam.titulo_vista(520, 445, "B. TAPA - CORTE", "ESC. 1/2", 120)
    # ---------------- C. asa (1/2)
    k = 5.0; ox_, oy_ = lam.P(470, 395)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    pts = [P(-w - ASA["gancho"], -ASA["pata"]), P(-w, -ASA["pata"]), P(-w, 0), P(w, 0), P(w, -ASA["pata"]), P(w + ASA["gancho"], -ASA["pata"])]
    lam.poli(pts, "MARCO-METALICO", ancho=D38 * k)
    lam.cota(P(-w, 0), P(w, 0), 6, texto="0.12"); lam.cota(P(w + ASA["gancho"], -ASA["pata"]), P(w + ASA["gancho"], 0), 6, horizontal=False, texto="0.025")
    lam.cota(P(w, -ASA["pata"]), P(w + ASA["gancho"], -ASA["pata"]), -5, texto="0.115")
    lam.texto(lam.P(470, 368), "asa 3/8\" liso: desarrollo L = 0.12 + 2 x 0.025 + 2 x 0.115 = 0.40 m; 2 por tapa", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(470, 355, "C. ASA DE IZAJE", "ESC. 1/2", 120)
    # ---------------- D. secciones de los angulos (1/1)
    k = 10.0; ox_, oy_ = lam.P(650, 385)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    L_sec(lam, P(0, 0), L2[0], L2[1], k); lam.cota(P(0, 0), P(L2[0], 0), -5, texto="50.8 mm"); lam.cota(P(L2[0], 0), P(L2[0], L2[1]), 5, horizontal=False, texto="4.8 mm")
    lam.texto(P(0, L2[0] + 0.012), "L 2\"x2\"x3/16\" (contramarco) 3.63 kg/m", 1.7, "TEXTOS")
    L_sec(lam, P(0.10, 0), L15[0], L15[1], k); lam.cota(P(0.10, 0), P(0.10 + L15[0], 0), -5, texto="38.1 mm"); lam.cota(P(0.10 + L15[0], 0), P(0.10 + L15[0], L15[1]), 5, horizontal=False, texto="3.2 mm")
    lam.texto(P(0.10, L15[0] + 0.012), "L 1 1/2\"x1 1/2\"x1/8\" (marco) 1.83 kg/m", 1.7, "TEXTOS")
    lam.titulo_vista(700, 355, "D. SECCIONES DE LOS ANGULOS", "ESC. 1/1", 100)
    # ---------------- E. despiece del marco y la parrilla (1/5)
    k = 2.0; ox_, oy_ = lam.P(60, 255)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    for i in range(4):
        y = -i * 0.08
        pts = [P(0, y), P(TAPA, y), P(TAPA - leg, y - leg), P(leg, y - leg)]
        lam.poli(pts, "MARCO-METALICO", cerrada=True); lam.relleno(pts, "MARCO-METALICO")
        lam.texto(P(TAPA + 0.05, y - leg / 2), "M%d: angulo L 1 1/2\"x1 1/2\"x1/8\" x 0.68 (ingletes 45)" % (i + 1), 1.8, "TEXTOS", TA.MIDDLE_LEFT)
    lam.cota(P(0, 0), P(TAPA, 0), 5, texto="0.68")
    y0 = -0.40
    for i in range(7): barra(lam, P(0.05 + i * 0.10, y0), P(0.05 + i * 0.10, y0 - 0.31), D38, k)
    lam.texto(P(0.80, y0 - 0.15), "B1 a B14: 14 barras 3/8\" L = 0.62 (7 en cada sentido)", 1.8, "TEXTOS", TA.MIDDLE_LEFT)
    lam.cota(P(0.05, y0 - 0.31), P(0.05, y0), -6, horizontal=False, texto="0.62")
    lam.titulo_vista(150, 95, "E. DESPIECE DEL MARCO Y DE LA PARRILLA", "ESC. 1/5 (barras acortadas en el dibujo)", 150)
    # ---------------- procedimiento, cuadro, leyenda
    lam.notas(330, 300, "PROCEDIMIENTO DE FABRICACION", [
        "1. Marco: 4 piezas de angulo L 1 1/2\"x1 1/2\"x1/8\" de 0.68 m a inglete 45, soldadas en las esquinas (E6011 1/8\"); medida exterior 0.68 x 0.68.",
        "2. Parrilla: 7 + 7 barras 3/8\" de 0.62 m @0.10, amarradas con alambre N 16 y soldadas por puntos en sus extremos al ala vertical del marco (28 puntos).",
        "3. Asas: 2 barras lisas 3/8\" en U (0.12 x 0.025, ganchos 0.115) amarradas bajo la parrilla; cajuela de 0.18 x 0.06 x 0.03 con molde para que no sobresalgan.",
        "4. Vaciado en molde metalico o de madera sobre superficie plana, con el marco como encofrado lateral: concreto f'c = 210 kg/cm2, piedra de 1/2\", vibrado.",
        "5. Curado humedo 7 dias; desmoldar a los 2 dias. Acabado superior frotachado. Pintar el marco con 2 manos de anticorrosivo y 2 de esmalte.",
        "6. Colocar sobre el contramarco (DD-01): holgura 1 cm por lado; la tapa queda al ras del NPT. Marcar el numero de registro en la tapa."], 1.8)
    n = MC.registros()["n"]
    L_m = 4 * TAPA; kg_m = L_m * MC.ANG["1.5x1.5x1/8"]; L_p = 14 * 0.62; kg_p = L_p * MC.PESO["3/8"]; L_a = 2 * 0.40; kg_a = L_a * MC.PESO["3/8"]; vol = TAPA * TAPA * ET
    filas = [["Concreto f'c = 210 kg/cm2 (0.68 x 0.68 x 0.08)", "m3", f3(vol), f2(n * vol), "01.04.04.05.05 CONCRETO EN TAPAS"],
             ["Parrilla 3/8\" corrugado, 14 barras de 0.62 m", "m / kg", "%.2f / %.2f" % (L_p, kg_p), "%.2f / %.2f" % (n * L_p, n * kg_p), "01.04.04.05.06 ACERO EN TAPAS, BORDES Y ANCLAJES"],
             ["Asas 3/8\" liso, 2 und de 0.40 m", "m / kg", "%.2f / %.2f" % (L_a, kg_a), "%.2f / %.2f" % (n * L_a, n * kg_a), "01.04.04.05.06"],
             ["Angulo L 1 1/2\"x1 1/2\"x1/8\" (4 piezas de 0.68 m, 1.83 kg/m)", "m / kg", "%.2f / %.2f" % (L_m, kg_m), "%.2f / %.2f" % (n * L_m, n * kg_m), "01.04.04.05.03 ANGULOS METALICOS (kg)"],
             ["Alambre negro N 16 (amarres) / soldadura por puntos (28)", "kg", "0.10 / 0.05", "%.2f / %.2f" % (n * 0.10, n * 0.05), "insumo del ACU"],
             ["Molde: fondo 0.68 x 0.68 + cajuelas (reutilizable 10 veces)", "m2", f2(TAPA * TAPA), f2(TAPA * TAPA), "insumo del ACU (1 molde)"],
             ["Pintura anticorrosiva + esmalte del marco (0.152 m2/m x 2.72 m)", "m2", f2(2.72 * 0.152), f2(n * 2.72 * 0.152), "01.04.04.05.07 PINTURA (parte)"],
             ["Pintura total por registro: contramarco 0.57 + marco 0.41", "m2", f2(2.80 * 0.203 + 2.72 * 0.152), f2(n * (2.80 * 0.203 + 2.72 * 0.152)), "01.04.04.05.07 PINTURA (total)"],
             ["Fabricacion, curado y colocacion de la tapa", "und", "1", "%d" % n, "01.04.04.05.04 TAPA (und); marco: 01.04.04.05.02 (und)"]]
    cuadro(lam, 330, 245, "CUADRO DE COMPONENTES POR TAPA CON MARCO (1 und) Y TOTAL (%d und)" % MC.registros()["n"], filas)
    lam.leyenda2(560, 180, [("relleno", "MARCO-METALICO", "angulo metalico / asa"), ("linea2", "ACERO", "barra 3/8\" (sentido X)"), ("linea2", "ACERO-LONG", "barra 3/8\" (sentido Y)"), ("concreto", "CONCRETO", "concreto f'c=210 de la tapa"), ("relleno", "ISO-TAPA", "cajuela del asa")], 1.8)
    lam.volcar_llamadas()
    return lam


# ============================================================================= DD-03 juntas
def dd03(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 10, "DD-03", "DETALLE CONSTRUCTIVO: JUNTA DE DILATACION E=1\" CON SELLADOR Y JUNTAS DE TECNOPOR",
                   "PARTIDAS 01.04.04.06.01 y 01.04.04.06.02 - %s DE DILATACION CADA 4.00 m - ESC. INDICADAS" % SUB_N_JUNTAS)
    lam.juntar_llamadas()
    b, em, ef, et = D["b"], D["e_muro"], D["e_fondo"], D["e_losa"]; be = b + 2 * em; h = round(max(e["h"] for e in R["perfil"] if e.get("zona") != "CAMION"), 2); J = MC.juntas(); e_j = 0.025; per_j = J["L_dilat"] / J["n"]
    # ---------------- A. seccion del colector en la junta (1/10)
    k = 1.0; ox_, oy_ = lam.P(130, 300)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    ext = [P(-be / 2, 0), P(be / 2, 0), P(be / 2, ef + h + et), P(-be / 2, ef + h + et)]; intr = [P(-b / 2, ef), P(b / 2, ef), P(b / 2, ef + h), P(-b / 2, ef + h)]
    lam.poli(ext, "CONCRETO", cerrada=True, ancho=0.004); lam.poli(intr, "CONCRETO", cerrada=True, ancho=0.004)
    hh = lam.msp.add_hatch(dxfattribs={"layer": "JUNTAS"}); hh.set_pattern_fill("ANSI37", scale=0.35 * lam.f * 10, angle=0)
    hh.paths.add_polyline_path(ext, is_closed=True); hh.paths.add_polyline_path(intr, is_closed=True, flags=0)
    lam.poli([P(-b / 2, ef + h), P(-b / 2, ef), P(b / 2, ef), P(b / 2, ef + h)], "CORTES", ancho=0.025)
    lam.poli([P(-be / 2, ef + h + et), P(be / 2, ef + h + et)], "CORTES", ancho=0.025)
    lam.rect(*P(-0.8, -0.05), *P(0.8, 0), "SOLADO")
    lam.cota(P(-b / 2, -0.05), P(b / 2, -0.05), -5, texto="%.2f" % b); lam.cota(P(-be / 2, -0.05), P(be / 2, -0.05), -10, texto="%.2f" % be)
    lam.cota(P(be / 2, 0), P(be / 2, ef), 6, horizontal=False, texto="0.15"); lam.cota(P(be / 2, ef), P(be / 2, ef + h), 6, horizontal=False, texto="h max = %.2f" % h)
    lam.cota(P(be / 2, ef + h), P(be / 2, ef + h + et), 6, horizontal=False, texto="0.10")
    xt = 215
    LL(lam, P(be / 2 - em / 2, ef + h * 0.8), xt, 480, ["plancha de tecnopor de 1\" (25 mm) en toda la", "seccion: 2 muros, losa de fondo y losa superior"])
    LL(lam, P(b / 2, ef + h * 0.45), xt, 450, ["sello elastomerico de poliuretano 1\" x 1\" en", "las caras interiores (2 x h + %.2f)" % b])
    LL(lam, P(0.2, ef + h + et), xt, 420, ["sello 1\" x 1\" en la cara superior (%.2f)," % be, "enrasado con el acabado de la losa"])
    lam.titulo_vista(130, 262, "A. JUNTA DE DILATACION - SECCION TRANSVERSAL", "ESC. 1/10 - perimetro = 2 x %.2f + 2 x (%.2f + h + %.2f) = %.2f m (h = %.2f)" % (be, ef, et, per_j, h), 185)
    # ---------------- B. detalle de la junta (1/2)
    k = 5.0; ox_, oy_ = lam.P(560, 470)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    izq = [P(-0.25, 0), P(-e_j / 2, 0), P(-e_j / 2, em), P(-0.25, em)]; der = [P(e_j / 2, 0), P(0.25, 0), P(0.25, em), P(e_j / 2, em)]
    hatch_conc(lam, izq, 0.8); hatch_conc(lam, der, 0.8)
    tecnopor(lam, [P(-e_j / 2, 0), P(e_j / 2, 0), P(e_j / 2, em - 0.025), P(-e_j / 2, em - 0.025)])
    lam.relleno([P(-e_j / 2, em - 0.025), P(e_j / 2, em - 0.025), P(e_j / 2, em), P(-e_j / 2, em)], "CORTES")
    barra(lam, P(-0.25, em / 2), P(-e_j / 2 - 0.05, em / 2), D38, k, "ACERO-LONG"); barra(lam, P(e_j / 2 + 0.05, em / 2), P(0.25, em / 2), D38, k, "ACERO-LONG")
    for x in (-0.20, -e_j / 2 - 0.08, e_j / 2 + 0.08, 0.20): punto_barra(lam, P(x, em / 2), D38, k)
    lam.cota(P(-e_j / 2, 0), P(e_j / 2, 0), -6, texto="1\" (25 mm)"); lam.cota(P(e_j / 2, 0), P(e_j / 2 + 0.05, 0), -11, texto="0.05")
    lam.cota(P(0.25, em - 0.025), P(0.25, em), 6, horizontal=False, texto="25 mm"); lam.cota(P(0.25, 0), P(0.25, em - 0.025), 6, horizontal=False, texto="0.125")
    lam.texto(P(0, em + 0.025), "CARA INTERIOR (agua)", 1.8, "TEXTOS", TA.MIDDLE_CENTER); lam.texto(P(-0.12, -0.035), "CARA EXTERIOR (terreno)", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    xt = 700
    LL(lam, P(0, em - 0.012), xt, 560, ["sello de poliuretano (Sikaflex 1a o similar)", "25 x 25 mm sobre imprimante; caras limpias y secas"])
    LL(lam, P(0, em / 2), xt, 535, ["tecnopor de 1\" (densidad 15 kg/m3) en todo", "el espesor, retirado 25 mm en la cara interior"])
    LL(lam, P(-0.10, em / 2), xt, 510, ["barras longitudinales 3/8\" interrumpidas", "a 0.05 de la junta (no la cruzan)"])
    LL(lam, P(0.20, em / 2), xt, 485, ["marcos 3/8\" a cada lado de la junta", "(DP-04 y DP-08)"])
    lam.titulo_vista(560, 435, "B. DETALLE DE LA JUNTA DE DILATACION", "ESC. 1/2 - corte longitudinal por el muro (igual en las losas)", 170)
    # ---------------- C. junta de tecnopor contra el cerco (1/10)
    k = 1.0; ox_, oy_ = lam.P(330, 55)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    zs = ef + h + et; xc = em + D["junta_cerco"]
    hatch_conc(lam, [P(0, 0), P(em, 0), P(em, zs), P(0, zs)], 0.5); lam.rect(*P(-0.35, ef), *P(0, ef + h), "CONCRETO-OCULTO")
    cerco1 = [P(xc, zs - 0.6), P(xc + 0.15, zs - 0.6), P(xc + 0.15, zs + 0.6), P(xc, zs + 0.6)]; cerco2 = [P(xc, zs - 0.9), P(xc + 0.40, zs - 0.9), P(xc + 0.40, zs - 0.6), P(xc, zs - 0.6)]
    for c_ in (cerco1, cerco2):
        if CON_CERCO: lam.poli(c_, "CERCO", cerrada=True); lam.achurado(c_, "TERRENO-ACHURADO", escala_mm=0.4)
    if not CON_CERCO:
        lam.poli([P(xc, zs), P(xc + 1.2, zs)], "TERRENO", ancho=0.003); lam.poli([P(xc, zs - 0.10), P(xc + 1.2, zs - 0.10)], "TERRENO-EXISTENTE")
    tecnopor(lam, [P(em, zs - 0.9), P(xc, zs - 0.9), P(xc, zs), P(em, zs)])
    lam.poli([P(-0.4, zs), P(0, zs)], "TERRENO", ancho=0.002); lam.nivel(P(-0.25, zs), D["NPT"], texto="NPT +%.2f" % D["NPT"], lado=-1)
    lam.cota(P(em, zs - 0.9), P(xc, zs - 0.9), -6, texto="1\""); lam.cota(P(xc + 0.45, zs - 0.9), P(xc + 0.45, zs), 6, horizontal=False, texto="0.90")
    if CON_CERCO: lam.texto(P(-0.17, ef + h / 2), "INTERIOR DEL COLECTOR", 1.6, "TEXTOS", TA.MIDDLE_CENTER, rot=90)
    else: lam.texto(P(-0.17, ef + h / 2 + 0.03), "INTERIOR", 1.6, "TEXTOS", TA.MIDDLE_CENTER); lam.texto(P(-0.17, ef + h / 2 - 0.03), "DEL COLECTOR", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
    xt = 430
    if CON_CERCO:
        LL(lam, P(xc + 0.07, zs + 0.3), xt, 318, ["muro del cerco existente"])
        LL(lam, P(em + D["junta_cerco"] / 2, zs - 0.45), xt, 300, ["tecnopor de 1\" entre el muro lado predio y el", "cimiento del cerco: altura 0.90 (0.90 m2 por metro)"])
        LL(lam, P(xc + 0.2, zs - 0.75), xt, 282, ["cimiento del cerco (no se toca; se protege", "durante la excavacion)"])
    else:
        LL(lam, P(xc + 0.6, zs - 0.05), 485, 122, ["piso terminado adyacente (+%.2f); no hay cerco" % D["NPT"]])
        LL(lam, P(em + D["junta_cerco"] / 2, zs - 0.05), 485, 106, ["tecnopor de 1\" entre la losa superior y el piso", "adyacente, a ambos lados del colector"])
    LL(lam, P(em / 2, zs - 1.2), xt if CON_CERCO else 485, 264 if CON_CERCO else 84, ["muro del colector e = 0.15 vaciado contra la", "plancha (encofrado perdido)"])
    lam.titulo_vista(360, 25, TIT_DD03_C, TXT_DD03_C, 170)
    # ---------------- D. junta de tecnopor en el borde de la losa con el piso (1/5)
    k = 2.0; ox_, oy_ = lam.P(560, 330)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    hatch_conc(lam, [P(-0.6, 0), P(0, 0), P(0, et), P(-0.6, et)], 0.6)
    piso = [P(e_j, 0), P(0.6, 0), P(0.6, et), P(e_j, et)]; lam.poli(piso, "TERRENO", cerrada=True); lam.achurado(piso, "TERRENO-ACHURADO", escala_mm=0.5)
    tecnopor(lam, [P(0, 0), P(e_j, 0), P(e_j, et), P(0, et)])
    lam.rect(*P(-0.6, -0.12), *P(0.6, 0), "RELLENO"); lam.texto(P(0, -0.06), "relleno compactado / muro del colector", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
    lam.cota(P(0, 0), P(e_j, 0), -6, texto="1\""); lam.cota(P(0.6, 0), P(0.6, et), 6, horizontal=False, texto="0.10")
    lam.texto(P(-0.3, et + 0.03), "LOSA SUPERIOR DEL COLECTOR", 1.7, "TEXTOS", TA.MIDDLE_CENTER); lam.texto(P(0.33, et + 0.03), "PISO ADYACENTE (retiro)", 1.7, "TEXTOS", TA.MIDDLE_CENTER)
    LL(lam, P(e_j / 2, et / 2), 700, 365, ["tecnopor de 1\" en el espesor del piso (0.10):", "0.10 m2 por metro; ambos lados del colector y cajas"])
    lam.titulo_vista(560, 290, "D. JUNTA DE TECNOPOR EN EL BORDE DE LA LOSA", "ESC. 1/5", 150)
    # ---------------- E. ubicacion de las juntas de dilatacion
    progs = ["0+%06.2f" % (4.0 * (i + 1)) for i in range(J["n"])]
    ncol = max(2, -(-len(progs) // 9))
    filas = [[progs[i + 9 * c] if i + 9 * c < len(progs) else "" for c in range(ncol)] for i in range(9)]
    lam.tabla(700, 245, ["JUNTA (prog.)"] * ncol, filas, [40] * ncol if ncol == 2 else [32] * ncol, 1.7, 4.4, "UBICACION DE LAS %d JUNTAS (planta y perfil)" % J["n"])
    lam.texto(lam.P(700, 195), TXT_JUNTA_CAJAS[0], 1.6, "TEXTOS-NOTAS"); lam.texto(lam.P(700, 191), TXT_JUNTA_CAJAS[1], 1.6, "TEXTOS-NOTAS")
    # ---------------- cuadro, procedimiento, leyenda
    per = J["L_dilat"] / J["n"]; a_tec = be * (ef + h + et) - b * h; sello = 2 * h + b + be
    filas = [["Plancha de tecnopor 1\" (seccion %.2f x %.2f menos el hueco %.2f x %.2f)" % (be, ef + h + et, b, h), "m2", "%.3f (%.3f/m)" % (a_tec, a_tec / per), f2(J["n"] * a_tec), "01.04.04.06.01 (por metro de junta: perimetro %.2f m)" % per],
             ["Sello de poliuretano 25 x 25 mm (caras interiores 2h + %.2f y superior %.2f)" % (b, be), "m", "%.2f (%.3f/m)" % (sello, sello / per), f2(J["n"] * sello), "01.04.04.06.01: 0.63 L por metro de sello (aprox. 0.75 kg)"],
             ["Imprimante para el sello (0.10 L por metro de cordon)", "L", f2(sello * 0.10), f2(J["n"] * sello * 0.10), "insumo del ACU"],
             (["Tecnopor 1\" contra el cerco: altura 0.90 x %.2f m" % J["L_tecnopor_cerco"], "m2", "0.90 por m", f2(0.90 * J["L_tecnopor_cerco"]), "01.04.04.06.02 (tramo pegado al cerco)"] if CON_CERCO else
              ["Tecnopor 1\" en el contacto con la caja CL (seccion del colector menos el hueco)", "m2", f2(a_tec), f2(a_tec), "01.04.04.06.02 (empalme con la CL)"]),
             ["Tecnopor 1\" en el borde de la losa con el piso: altura 0.10 x %.2f m" % J["L_tecnopor_piso"], "m2", "0.10 por m", f2(0.10 * J["L_tecnopor_piso"]), "01.04.04.06.02 (ambos lados del colector y cajas)"]]
    cuadro(lam, 430, 165, "COMPONENTES POR JUNTA DE DILATACION (perimetro %.2f m) Y TOTAL (%d und); JUNTAS DE TECNOPOR POR METRO" % (per, J["n"]), filas, (104, 12, 30, 22, 78))
    lam.notas(430, 225, "PROCEDIMIENTO", [
        "1. Marcar las juntas cada 4.00 m (cuadro). Cortar la plancha de tecnopor a la forma de la seccion (anillo %.2f x %.2f con hueco %.2f x h) y fijarla al concreto ya vaciado." % (be, ef + h + et, b),
        "2. Vaciar el tramo siguiente contra la plancha. El acero longitudinal termina a 0.05 de cada lado; los marcos se colocan a cada lado de la junta.",
        "3. Retirar 25 mm de tecnopor en las caras interiores y en la cara superior; limpiar, imprimar y aplicar el sello de poliuretano 25 x 25 mm con pistola; alisar.",
        NOTA4_DD03], 1.8, ancho_mm=ANCHO_PROC_DD03)
    lam.leyenda2(60, 235, [("concreto", "CONCRETO", "concreto f'c=210"), ("rect", "JUNTAS", "tecnopor 1\""), ("relleno", "CORTES", "sello elastomerico")] + ([("rect", "CERCO", "cerco existente")] if CON_CERCO else []) + [("linea2", "ACERO-LONG", "barra longitudinal 3/8\""), ("rect", "RELLENO", "relleno compactado")], 1.8)
    lam.volcar_llamadas()
    return lam


# ============================================================================= DD-04 empalme de cuneta
def dd04(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 10, "DD-04", "DETALLE CONSTRUCTIVO: EMPALME DE CUNETA AL COLECTOR (VENTANA EN MURO Y CAIDA)",
                   TXT_DD04_SUB)
    b, em, ef, et = D["b"], D["e_muro"], D["e_fondo"], D["e_losa"]; be = b + 2 * em
    cun = [c for c in R["cunetas"] if c.get("entra_en", "colector") == "colector"]; ej = min(cun, key=lambda c: abs(c["prog"] - EJ_DD04)); Hc = ej["H"]; NCF = ej["NCF_fin"]; cf = dz.fondo(ej["prog"]); h = dz.techo(ej["prog"]) - cf; zc = ef + (NCF - cf); Hv = ef + h - zc; e_j = 0.025
    lam.juntar_llamadas()
    # ---------------- A. elevacion interior del muro con la ventana (1/10)
    k = 1.0; ox_, oy_ = lam.P(150, 330)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    lam.poli([P(-0.9, 0), P(0.9, 0), P(0.9, ef + h + et), P(-0.9, ef + h + et)], "CONCRETO", cerrada=True, ancho=0.003)
    for pts in ([P(-0.9, 0), P(0.9, 0), P(0.9, ef), P(-0.9, ef)], [P(-0.9, ef + h), P(0.9, ef + h), P(0.9, ef + h + et), P(-0.9, ef + h + et)]): lam.achurado(pts, escala_mm=0.6)
    lam.rect(*P(-0.20, zc), *P(0.20, ef + h), "CUNETA", const_width=0.004)
    lam.relleno([P(-0.20, zc), P(0.20, zc), P(0.20, ef + h), P(-0.20, ef + h)], "ISO-CUNETA")
    for i in range(-4, 5):
        x = i * 0.20
        if abs(x) < 0.25:
            barra(lam, P(x, ef - 0.05), P(x, zc - 0.05), D38, k); barra(lam, P(x, zc - 0.05), P(x + 0.10, zc - 0.05), D38, k)
        else:
            barra(lam, P(x, ef - 0.05), P(x, ef + h + 0.05), D38, k)
    for s in (-1, 1):
        for d in (0.24, 0.28): barra(lam, P(s * d, zc - 0.30), P(s * d, ef + h + 0.05), D38, k, "ACERO-LONG")
    for d in (0.04, 0.08): barra(lam, P(-0.50, zc - d), P(0.50, zc - d), D38, k, "ACERO-LONG")
    lam.cota(P(-0.20, 0), P(0.20, 0), -6, texto="0.40"); lam.cota(P(-0.50, 0), P(0.50, 0), -11, texto="1.00 (barras horizontales)")
    lam.cota(P(0.9, zc), P(0.9, ef + h), 6, horizontal=False, texto="Hv = %.2f (var.)" % Hv); lam.cota(P(0.9, ef), P(0.9, zc), 6, horizontal=False, texto="%.2f" % (zc - ef))
    lam.cota(P(0.9, ef + h), P(0.9, ef + h + et), 6, horizontal=False, texto="0.10")
    lam.nivel(P(-0.65, zc), NCF, texto="NCF %.2f" % NCF, lado=-1); lam.nivel(P(-0.65, ef), cf, texto="CF %.3f" % cf, lado=-1)
    xt = 270
    LL(lam, P(0.26, ef + h - 0.25), xt, 500, ["refuerzo de borde: 2 barras 3/8\" verticales a cada", "lado, L = Hv + 0.60 (anclaje 0.30 abajo, gancho en la losa)"])
    LL(lam, P(0, (zc + ef + h) / 2), xt, 475, ["ventana 0.40 x Hv dejada en el vaciado (cajon de", "encofrado); llega hasta la losa superior, sin dintel"])
    LL(lam, P(-0.6, ef + h + et / 2), xt, 450, ["losa superior monolitica: hace de dintel (luz 0.40)"])
    LL(lam, P(0.05, zc - 0.05), xt, 425, ["marcos 3/8\" interrumpidos en la ventana:", "gancho de 0.10 bajo el alfeizar"])
    LL(lam, P(0.35, zc - 0.06), xt, 400, ["2 barras 3/8\" horizontales bajo el alfeizar, L = 1.00"])
    lam.titulo_vista(150, 295, "A. VENTANA DE EMPALME - ELEVACION INTERIOR", "ESC. 1/10 - ejemplo cuneta Eje %s (0+%06.2f); Hv de cada cuneta en el cuadro" % (ej["perfil"], ej["prog"]), 185)
    # ---------------- B. corte por el empalme (1/10)
    k = 1.0; ox_, oy_ = lam.P(520, 330)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    xl, xr = -be / 2, be / 2; zf = ef; zt = ef + h; zs = zt + et
    hatch_conc(lam, [P(xl, 0), P(xr, 0), P(xr, zf), P(xl, zf)], 0.6)
    hatch_conc(lam, [P(xl, zf), P(xl + em, zf), P(xl + em, zs), P(xl, zs)], 0.6)
    hatch_conc(lam, [P(xr - em, zf), P(xr, zf), P(xr, zc), P(xr - em, zc)], 0.6)
    hatch_conc(lam, [P(xl + em, zt), P(xr, zt), P(xr, zs), P(xl + em, zs)], 0.6)
    lam.rect(*P(xl, -0.05), *P(xr, 0), "SOLADO")
    xq = xr + e_j
    fondo_c = [P(xq, zc - 0.10), P(xq + 1.0, zc - 0.10), P(xq + 1.0, zc), P(xq, zc)]; lam.poli(fondo_c, "CUNETA", cerrada=True); lam.achurado(fondo_c, "TERRENO-ACHURADO", escala_mm=0.4)
    lam.poli([P(xq, zc), P(xq, zc + Hc), P(xq + 1.0, zc + Hc), P(xq + 1.0, zc)], "CUNETA-OCULTA")
    lam.poli([P(xq, zs), P(xq + 1.0, zs)], "TERRENO", ancho=0.002)
    tecnopor(lam, [P(xr, zc - 0.10), P(xq, zc - 0.10), P(xq, zs), P(xr, zs)])
    lam.relleno([P(xr, zc - 0.125), P(xq, zc - 0.125), P(xq, zc - 0.10), P(xr, zc - 0.10)], "CORTES")
    lam.poli([P(xq + 1.0, zc + 0.12), P(xq, zc + 0.10), P(xr - em, zc + 0.08)], "AGUA")
    lam.flecha(P(xr - em - 0.05, zc + 0.05), P(xr - em - 0.35, zf + 0.05), "AGUA")
    lam.poli([P(xl + em, zf + 0.35), P(xr - em, zf + 0.35)], "AGUA")
    for d in (0.04, 0.08): punto_barra(lam, P(xr - em / 2, zc - d), D38, k)
    lam.poli([P(xr - em - 1.0 + em, zf), P(xr - em, zf)], "CORTES", ancho=0.015)
    lam.nivel(P(xq + 0.6, zc), NCF, texto="NCF %.2f" % NCF); lam.nivel(P(xl + 0.25, zf + 0.35), 0, texto="NA colector"); lam.nivel(P(xq + 0.6, zs), D["NPT"], texto="NPT +%.2f" % D["NPT"])
    lam.cota(P(xr + 1.1, zc), P(xr + 1.1, zt), 6, horizontal=False, texto="Hv"); lam.cota(P(xr, zc - 0.10), P(xq, zc - 0.10), -6, texto="1\"")
    lam.cota(P(xl, -0.05), P(xr, -0.05), -8, texto="%.2f" % be); lam.cota(P(xl + em, -0.05), P(xr - em, -0.05), -4, texto="%.2f" % b)
    xt = 690
    LL(lam, P(xq + 0.5, zs), xt, 505, ["piso terminado del predio"])
    LL(lam, P(xq - e_j / 2, zc + 0.6), xt, 485, ["junta de tecnopor 1\" entre el extremo de la", "cuneta y el muro, en todo el contorno (0.60 + 2 x Hc)"])
    LL(lam, P(xq + 0.5, zc + 0.11), xt, 460, ["cuneta de arquitectura 0.40 x H, muros 0.10", TXT_DD04_CUNETA])
    LL(lam, P(xr - em, zc + 0.06), xt, 435, ["caida libre: la cuneta queda siempre por encima", "del nivel de agua del colector"])
    LL(lam, P(xr - em / 2, zc - 0.06), xt, 410, ["barras horizontales de borde bajo el alfeizar"])
    LL(lam, P(xq - e_j / 2, zc - 0.112), xt, 385, ["sello elastomerico 25 x 25 mm en el contorno", "exterior de la junta"])
    LL(lam, P(xr - em - 0.5, zf), xt, 360, ["fondo con acabado pulido (mortero 1:3, 1 cm)", "en 1.00 m bajo la caida; sin dado disipador"])
    lam.titulo_vista(560, 295, "B. CORTE POR EL EMPALME (mirando aguas abajo)", "ESC. 1/10 - ejemplo Eje %s; registro de limpieza encima (DD-01 y DD-02)" % ej["perfil"], 185)
    # ---------------- C. planta del empalme (1/5)
    k = 2.0; ox_, oy_ = lam.P(150, 150)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    hatch_conc(lam, [P(-0.6, -em), P(-0.20, -em), P(-0.20, 0), P(-0.6, 0)], 0.6); hatch_conc(lam, [P(0.20, -em), P(0.6, -em), P(0.6, 0), P(0.20, 0)], 0.6)
    lam.rect(*P(-0.20, -em), *P(0.20, 0), "CUNETA-OCULTA"); lam.relleno([P(-0.20, -em), P(0.20, -em), P(0.20, 0), P(-0.20, 0)], "ISO-CUNETA")
    lam.rect(*P(-0.6, -em - 0.35), *P(0.6, -em), "CONCRETO-OCULTO"); lam.texto(P(0, -em - 0.25), "INTERIOR DEL COLECTOR (b = %.2f)" % b, 1.7, "TEXTOS", TA.MIDDLE_CENTER)
    yq = e_j
    for s in (-1, 1):
        pts = [P(s * 0.20, yq), P(s * 0.30, yq), P(s * 0.30, yq + 0.50), P(s * 0.20, yq + 0.50)]; lam.poli(pts, "CUNETA", cerrada=True); lam.achurado(pts, "TERRENO-ACHURADO", escala_mm=0.4)
    tecnopor(lam, [P(-0.30, 0), P(0.30, 0), P(0.30, yq), P(-0.30, yq)])
    lam.bloque("SIMB-FLECHA", P(0, 0.30), 2.0 * lam.f, rot=-90, capa="FLUJO")
    lam.rect(*P(-0.22, -em - 0.02), *P(0.22, 0.02), "EXCAVACION")
    for s in (-1, 1):
        for d in (0.24, 0.28): punto_barra(lam, P(s * d, -em / 2), D38, k)
    lam.cota(P(-0.20, -em - 0.35), P(0.20, -em - 0.35), -5, texto="0.40"); lam.cota(P(-0.30, -em - 0.35), P(0.30, -em - 0.35), -10, texto="0.60")
    lam.cota(P(0.6, -em), P(0.6, 0), 6, horizontal=False, texto="0.15"); lam.cota(P(0.30, 0), P(0.30, yq), 8, texto="1\"")
    xt = 285
    LL(lam, P(0.25, yq + 0.35), xt, 250, ["muro de la cuneta 0.10"])
    LL(lam, P(0, yq / 2), xt, 228, ["junta de tecnopor 1\" + sello en el contorno exterior"])
    LL(lam, P(0, -em / 2), xt, 206, ["ventana 0.40 formada con cajon de madera", "0.40 x Hv x 0.15 (se retira al desencofrar)"])
    LL(lam, P(0.26, -em / 2), xt, 182, ["refuerzo vertical de borde 2 x 3/8\" a cada lado"])
    lam.titulo_vista(150, 38, "C. EMPALME - PLANTA (losa superior retirada)", "ESC. 1/5", 150)
    # ---------------- D. cuadros
    filas = []
    for c in cun:
        hvp = dz.techo(c["prog"]) - c["NCF_fin"]
        filas.append(["Eje %s" % c["perfil"], "0+%06.2f" % c["prog"], "%.2f" % c["NCF_fin"], "%.2f" % c["H"], "%.2f" % hvp, "%.2f" % ((2 * 0.40 + 2 * hvp) * em), "%.2f" % ((4 * (hvp + 0.60) + 2 * 1.00) * MC.PESO["3/8"]), "%.2f" % ((0.60 + 2 * c["H"]) * e_j), "%.2f" % (0.60 + 2 * c["H"])])
    lam.tabla(430, 270, ["CUNETA", "PROG.", "NCF LLEGA (msnm)", "H CUNETA (m)", "Hv VENTANA (m)", "ENCOF. CAJON (m2)", "ACERO BORDE 3/8\" (kg)", "TECNOPOR (m2)", "SELLO (m)"], filas, [22, 22, 26, 22, 24, 26, 30, 24, 20], 1.6, 4.4, "CUADRO DE EMPALMES: DIMENSIONES Y COMPONENTES POR CUNETA (DP-06C)")
    n = len(cun); hvm = sum(float(f[4]) for f in filas) / n; tot = lambda j: sum(float(f[j]) for f in filas)
    filas2 = [["Cajon de encofrado de la ventana 0.40 x Hv x 0.15 (madera, 2 usos)", "m2", f2(tot(5) / n), f2(tot(5)), "01.04.04.06.03 EMPALME (und)"],
              ["Refuerzo de borde 3/8\": 4 verticales (Hv + 0.60) + 2 horizontales de 1.00", "kg", f2(tot(6) / n), f2(tot(6)), "01.04.04.06.03 EMPALME (und)"],
              ["Tecnopor 1\" en el contorno de la cuneta (0.60 + 2 x H)", "m2", f2(tot(7) / n), f2(tot(7)), "01.04.04.06.03 EMPALME (und)"],
              ["Sello elastomerico 25 x 25 mm en el contorno exterior", "m", f2(tot(8) / n), f2(tot(8)), "01.04.04.06.03 EMPALME (und)"],
              ["Acabado pulido del fondo (mortero 1:3, e = 1 cm) %.2f x 1.00" % b, "m2", f2(b), f2(b * n), "01.04.04.06.03 EMPALME (und)"],
              ["Perfilado y resane de los bordes de la ventana (mortero 1:3)", "m", f2(2 * 0.40 + 2 * hvm), f2(n * (2 * 0.40 + 2 * hvm)), "01.04.04.06.03 EMPALME (und)"],
              ["Registro de limpieza encima del empalme", "und", "1", "%d" % n, "partidas 01.04.04.05.xx (DD-01 y DD-02)"]]
    cuadro(lam, 430, 222, "CUADRO DE COMPONENTES POR EMPALME (promedio) Y TOTAL (%d und)" % n, filas2, (100, 12, 24, 22, 60))
    lam.notas(430, 172, "PROCEDIMIENTO", [
        "1. Al armar el muro lado predio, colocar el refuerzo de borde (4 verticales y 2 horizontales) y el cajon de 0.40 x Hv con su fondo en la cota NCF de la cuneta (cuadro).",
        "2. Vaciar el muro y la losa superior monoliticos; retirar el cajon a los 2 dias, perfilar y resanar los bordes de la ventana.",
        "3. Empalmar la cuneta (o su prolongacion) contra el muro con la plancha de tecnopor de 1\" en todo su contorno; sellar el contorno exterior con poliuretano.",
        "4. Pulir el fondo del colector en 1.00 m bajo la caida. Colocar el registro de limpieza sobre el empalme (DD-01 y DD-02)."], 1.8)
    lam.leyenda2(300, 115, [("concreto", "CONCRETO", "concreto del colector f'c=210"), ("rect", "TERRENO-ACHURADO", "cuneta existente (arquitectura)"), ("relleno", "ISO-CUNETA", "ventana de empalme"), ("rect", "JUNTAS", "tecnopor 1\""), ("relleno", "CORTES", "sello elastomerico / acabado pulido"), ("linea2", "ACERO", "marcos 3/8\""), ("linea2", "ACERO-LONG", "refuerzo de borde 3/8\""), ("linea", "AGUA", "agua")], 1.8, ancho_col=120, filas_col=4)
    lam.volcar_llamadas()
    return lam


def todas(doc, ox, oy, R, T):
    return [dd01(doc, ox, oy, R, T), dd02(doc, ox + 30, oy, R, T), dd03(doc, ox + 60, oy, R, T), dd04(doc, ox + 90, oy, R, T)]
