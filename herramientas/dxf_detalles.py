"""Laminas de detalle constructivo por partida (DD-01 a DD-04): registros (rebaje de asiento y tapa ciega),
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
L2 = (MC.CM["ala"], MC.CM["esp"])  # angulo del contramarco segun el proyecto (metrado_calc.CM)
CMT = MC.CM["txt"]; CORDON = '3/16"' if MC.CM["esp"] > 0.004 else '1/8"'
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
TXT_DD04_SUB = "6 EMPALMES (EJES 01, 02, 06, 07, 11 Y 12): LA CUNETA SE METRA HASTA EL MURO DEL COLECTOR - ESC. INDICADAS"
TXT_DD03_C = "ESC. 1/10 - tramo 0+000.00 a 0+058.81 (pegado al cerco)"
CON_CERCO = True
MODO_DD03 = "cerco"      # "cerco" (Hogar de Refugio) o "caja_cl" (CAR Varones: terreno natural a ambos lados, junta solo con la CL)
TIT_DD03_C = "C. JUNTA LONGITUDINAL DE TECNOPOR Y SELLADOR CONTRA EL CERCO" if MC.SELLO["en_tecnopor"] else "C. JUNTA DE TECNOPOR CONTRA EL CERCO"
N_EMPALMES_TXT = "6 und"
EJ_DD04 = 11.27
TXT_DD04_CUNETA = "(Ejes 11 y 12 prolongadas hasta el muro)"
SUB_N_REG = "10 REGISTROS"; SUB_N_TAPAS = "10 TAPAS"; SUB_N_JUNTAS = "17 JUNTAS"     # cantidades en los subtitulos
PARTIDA_EMPALME = None     # el empalme no tiene partida propia en la planilla Delphin (solo detalle constructivo); texto de la partida si la tuviera
ANCHO_PROC_DD03 = 262      # ancho del procedimiento de la DD-03 (no invade la tabla de ubicacion)
NOTA4_DD03 = ("4. Junta longitudinal (02): plancha de 1\" x 0.90 pegada al cimiento del cerco antes de vaciar el muro, de 0+000.00 a 0+058.81, con sellador asfaltico 1\" x 2\" en la"
              " cara superior. Al lado via hay terreno natural: no lleva junta (la losa del colector sirve de vereda).")


def f2(v): return "%.2f" % v
def f3(v): return "%.3f" % v


# ============================================================================= DD-01 rebaje de asiento (tapa ciega)
REB, LUZ_L = 0.70, 0.60                       # rebaje 0.70 x 0.70 x 0.08 y luz libre 0.60 x 0.60 (lamina DP-06B rev. 02)
ASA_C = dict(agarre=0.15, pata=0.02, gancho=0.15)    # asa de fierro liso 1/2": desarrollo 0.49 (se toma 0.50)
CAJ_C = dict(largo=0.19, ancho=0.06, prof=0.03)      # cajuela del asa
YA_C = 0.20                                    # eje de las asas


def dd01(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 10, "DD-01", "DETALLE CONSTRUCTIVO: REBAJE DE ASIENTO DE LA TAPA CIEGA Y REFUERZO DE BORDE DEL REGISTRO",
                   "PARTIDA 01.04.04.05.01 TAPA CIEGA 0.68x0.68x0.08 (ASIENTO EN LA LOSA) - %s - ESC. INDICADAS" % SUB_N_REG)
    lam.juntar_llamadas()
    a, u = REB / 2, LUZ_L / 2
    MURO = D["b"] <= LUZ_L + 1e-6        # colector tan angosto como la luz (CAR Varones): los muros son el asiento en los lados largos
    bi, xe = D["b"] / 2, D["b"] / 2 + D["e_muro"]
    # ---------------- A. planta del rebaje (1/5)
    k = 2.0; ox_, oy_ = lam.P(150, 430)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    s_ = 0.55; sx_ = xe if MURO else s_
    lam.rect(*P(-sx_, -s_), *P(sx_, s_), "CONCRETO")
    if MURO:
        for s in (-1, 1):
            lam.linea(P(s * bi, -s_), P(s * bi, s_), "CONCRETO-OCULTO")
            lam.rect(*P(-bi, s * u), *P(bi, s * 0.45), "CONCRETO-OCULTO")
    else:
        xs = min(0.45, bi)
        lam.rect(*P(-xs, -0.45), *P(xs, 0.45), "CONCRETO-OCULTO")
    lam.rect(*P(-a, -a), *P(a, a), "CONCRETO", const_width=0.004)
    lam.rect(*P(-a + 0.01, -a + 0.01), *P(a - 0.01, a - 0.01), "CONCRETO")          # chaflan
    lam.rect(*P(-u, -u), *P(u, u), "REGISTRO", const_width=0.004)
    asiento = [P(-a, -a), P(a, -a), P(a, a), P(-a, a)]
    for s in (-1, 1):
        for d in (0.40,):
            lam.linea(P(s * d, -s_), P(s * d, s_), "ACERO-LONG"); lam.linea(P(-(xe - 0.04 if MURO else s_), s * d), P(xe - 0.04 if MURO else s_, s * d), "ACERO-LONG")
    lam.cota(P(-u, -s_), P(u, -s_), -4, texto="0.60 (luz libre)")
    lam.cota(P(-a, -s_), P(a, -s_), -9, texto="0.70 (rebaje)")
    if MURO: lam.cota(P(-bi, -s_), P(bi, -s_), -14, texto="%.2f (interior del colector)" % D["b"])
    else: lam.cota(P(-0.45, -s_), P(0.45, -s_), -14, texto="0.90 (borde engrosado)")
    lam.cota(P(s_ if not MURO else xe, u), P(s_ if not MURO else xe, a), 5, horizontal=False, texto="0.05")
    xt = 290
    LL(lam, P(a - 0.03, 0.30), xt, 540, ["rebaje 0.70 x 0.70 x 0.08 formado en la losa (asiento de la tapa ciega)"])
    LL(lam, P(0.0, (a + u) / 2), xt, 515, ["asiento de concreto plano y nivelado: 0.05 por lado, a 0.08 bajo el NPT"])
    LL(lam, P(-0.20, 0.0), xt, 490, ["luz libre 0.60 x 0.60 (acceso al colector)"])
    LL(lam, P(0.40, -0.48), xt, 465, ["refuerzo de borde: 2 barras 1/2\" por lado, L = 1.40" + ("; las transversales con ganchos dentro de los muros" if MURO else "")])
    if MURO:
        LL(lam, P(0.20, -0.40), xt, 440, ["borde engrosado 0.15 x 0.10 solo entre muros (2 lados); en la partida de concreto del colector"])
        LL(lam, P(xe - 0.03, 0.45), xt, 415, ["muro del colector e = %.2f: en los lados largos el asiento queda sobre la cabeza del muro" % D["e_muro"]])
    else:
        LL(lam, P(0.42, -0.42), xt, 440, ["borde engrosado 0.15 x 0.10 bajo la losa (en la partida de concreto del colector)"])
    LL(lam, P(-a + 0.005, a - 0.005), xt, 390 if MURO else 415, ["chaflan 1 x 1 cm en la arista superior del rebaje"])
    lam.titulo_vista(150, 290, "A. REBAJE DE ASIENTO - PLANTA (sin tapa)", "ESC. 1/5 - " + TXT_REG_A, 150)
    # ---------------- B. seccion del asiento (1/2)
    k = 5.0; ox_, oy_ = lam.P(560, 470)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    conc = [P(0.01, 0), P(0.30, 0), P(0.30, -0.10), P(0.10, -0.10), P(0.10, -0.20), P(-0.05, -0.20), P(-0.05, -ET), P(0, -ET), P(0, -0.01)]
    hatch_conc(lam, conc, 0.8)
    tapa = [P(-0.30, -ET), P(-HOLG, -ET), P(-HOLG, -0.01), P(-HOLG - 0.01, 0), P(-0.30, 0)]
    lam.poli(tapa, "REGISTRO-TAPA", cerrada=True); lam.achurado(tapa, escala_mm=0.6)
    punto_barra(lam, P(0.05, -0.045), D12, k); punto_barra(lam, P(0.05, -0.155), D12, k)
    barra(lam, P(0.14, -0.05), P(0.30, -0.05), D38, k)
    lam.poli([P(-0.30, 0), P(-HOLG - 0.01, 0)], "TERRENO", ancho=0.002); lam.poli([P(0.01, 0), P(0.30, 0)], "TERRENO", ancho=0.002)
    lam.nivel(P(0.22, 0), D["NPT"], texto="NPT +%.2f" % D["NPT"])
    lam.cota(P(-0.05, -ET), P(0, -ET), -5, texto="0.05")
    lam.cota(P(0.30, -ET), P(0.30, 0), 5, horizontal=False, texto="0.08"); lam.cota(P(0.30, -0.10), P(0.30, -ET), 5, horizontal=False, texto="0.02")
    lam.cota(P(0.30, -0.20), P(0.30, -0.10), 11, horizontal=False, texto="0.10"); lam.cota(P(0.30, -0.10), P(0.30, 0), 11, horizontal=False, texto="0.10")
    lam.cota(P(-HOLG, 0), P(0, 0), 5, texto="1 cm")
    xt = 735
    LL(lam, P(-0.025, -ET), xt, 560, ["asiento de concreto: 0.05 por lado,", "a 0.08 bajo el NPT"])
    LL(lam, P(0.0, -0.04), xt, 540, ["cara del rebaje 0.70 (vertical, lisa)"])
    LL(lam, P(0.05, -0.155), xt, 520, ["refuerzo de borde 2 x 1/2\" (DP-06B)"])
    LL(lam, P(0.22, -0.05), xt, 500, ["marcos del colector 3/8\" (DP-04)"])
    LL(lam, P(0.005, -0.005), xt, 480, ["chaflan 1 x 1 cm en la arista", "del rebaje"])
    LL(lam, P(0.05, -0.17), xt, 460, ["borde engrosado 0.15 x 0.10"])
    LL(lam, P(-0.15, -ET / 2), xt, 440, ["tapa ciega 0.68 x 0.08 (DD-02),", "holgura 1 cm por lado"])
    lam.titulo_vista(560, 325, "B. SECCION DEL ASIENTO DE LA TAPA", "ESC. 1/2 - la tapa queda al ras del NPT; sin marco ni contramarco metalico", 190)
    # ---------------- C. cajon de madera para formar el rebaje y la luz (1/5)
    k = 2.0; ox_, oy_ = lam.P(150, 225)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    e1 = 0.019                                         # tabla de 3/4"
    for x0_, x1_, z0_, z1_ in ((-a, a, -ET, 0), (-u, u, -0.20, -ET)):
        for pts in ([P(x0_, z0_), P(x0_ + e1, z0_), P(x0_ + e1, z1_), P(x0_, z1_)], [P(x1_ - e1, z0_), P(x1_, z0_), P(x1_, z1_), P(x1_ - e1, z1_)]):
            lam.poli(pts, "RELLENO", cerrada=True); lam.relleno(pts, "RELLENO")
    for pts in ([P(-a, 0), P(-a + 0.01, 0), P(-a, -0.01)], [P(a, 0), P(a - 0.01, 0), P(a, -0.01)]):
        lam.poli(pts, "RELLENO", cerrada=True)
    lam.rect(*P(-a + e1, -ET + 0.005), *P(a - e1, -ET + 0.005 + e1), "RELLENO")
    lam.linea(P(-0.65, -0.20), P(0.65, -0.20), "CONCRETO-OCULTO"); lam.texto(P(0.66, -0.20), "fondo del encofrado de la losa", 1.6, "TEXTOS", TA.MIDDLE_LEFT)
    lam.linea(P(-0.65, 0), P(0.65, 0), "TERRENO"); lam.texto(P(0.66, 0), "NPT", 1.6, "TEXTOS", TA.MIDDLE_LEFT)
    lam.cota(P(-a, 0), P(a, 0), 6, texto="0.70"); lam.cota(P(-u, -0.20), P(u, -0.20), -6, texto="0.60")
    lam.cota(P(-a, -ET), P(-a, 0), -6, horizontal=False, texto="0.08"); lam.cota(P(-u, -0.20), P(-u, -ET), -6, horizontal=False, texto="0.12")
    lam.texto(P(0, -0.10), "cajon inferior 0.60 x 0.60 x 0.12", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto(P(0, -0.035), "cajon superior 0.70 x 0.70 x 0.08", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(150, 160, "C. CAJON DE MADERA PARA EL REBAJE Y LA LUZ", "ESC. 1/5 - tablas de 3/4\" con desmoldante; reutilizable", 150)
    # ---------------- procedimiento, cuadro y leyenda
    lam.notas(330, 255, "PROCEDIMIENTO", [
        "1. Habilitar el refuerzo de borde: 2 barras de 1/2\" por lado, L = 1.40" + (" (las transversales con ganchos dentro de los muros)" if MURO else "") + ", amarradas a los marcos del colector.",
        "2. Armar el cajon de madera de dos niveles: inferior 0.60 x 0.60 x 0.12 (luz libre y borde engrosado) y superior 0.70 x 0.70 x 0.08 (rebaje), con tira de chaflan 1 x 1 cm.",
        "3. Aplicar desmoldante y fijar el cajon al encofrado de la losa, a plomo y nivelado, con la cara superior del cajon superior al nivel del NPT.",
        "4. Vaciar la losa y el borde engrosado con concreto f'c = 210 kg/cm2; vibrar alrededor del cajon y frotachar el asiento plano y nivelado (0.05 por lado).",
        "5. Retirar el cajon a las 24 h y curar 7 dias. Verificar el rebaje (0.70 x 0.70, tolerancia +/- 5 mm) y el nivel del asiento antes de colocar la tapa ciega (DD-02).",
        "6. No hay marco ni contramarco metalico: no se suelda ni se pinta; la tapa se apoya directamente en el concreto del asiento."], 1.8)
    n = MC.registros()["n"]
    v_eng = MC.BORDE_PERIM * 0.015; a_caj = 4 * REB * ET + 4 * LUZ_L * 0.12
    filas = [["Refuerzo de borde 2 x 1/2\" por lado, L = 1.40 (8 barras)", "m / kg", "%.2f / %.2f" % (11.2, 11.2 * MC.PESO["1/2"]), "%.2f / %.2f" % (n * 11.2, n * 11.2 * MC.PESO["1/2"]), "01.04.04.05.01 (desagregado: acero; DP-06B)"],
             [("Borde engrosado 0.15 x 0.10, perimetro %.2f m (2 lados, entre muros)" if MURO else "Borde engrosado 0.15 x 0.10, perimetro medio %.2f m") % MC.BORDE_PERIM, "m3", f3(v_eng), f2(n * v_eng), "01.04.04.04.01 CONCRETO PARA COLECTOR (ya incluido)"],
             ["Asiento: losa entre 0.60 y 0.70 en los 0.02 inferiores", "m3", f3((REB ** 2 - LUZ_L ** 2) * 0.02), f3(n * (REB ** 2 - LUZ_L ** 2) * 0.02), "01.04.04.04.01 CONCRETO PARA COLECTOR (ya incluido)"],
             ["Cajon de madera de 2 niveles (caras 4 x 0.70 x 0.08 + 4 x 0.60 x 0.12)", "m2", f3(a_caj), f3(a_caj), "1 cajon reutilizable (encofrado del colector)"],
             ["Colocacion de la tapa en el rebaje", "und", "1", "%d" % n, "01.04.04.05.01 TAPA DE REGISTRO (und)"]]
    cuadro(lam, 330, 200, "CUADRO DE COMPONENTES DEL ASIENTO POR REGISTRO (1 und) Y TOTAL (%d und)" % n, filas)
    lam.leyenda2(560, 150, [("linea2", "ACERO-LONG", "refuerzo de borde 1/2\" (proyeccion)"), ("concreto", "CONCRETO", "concreto f'c=210 de la losa"),
                            ("relleno", "RELLENO", "cajon de madera (encofrado)"), ("rect", "REGISTRO-TAPA", "tapa ciega (referencia, ver DD-02)")], 1.8)
    lam.volcar_llamadas()
    return lam


# ============================================================================= DD-02 tapa ciega
def dd02(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 10, "DD-02", "DETALLE CONSTRUCTIVO: TAPA CIEGA DE CONCRETO ARMADO 0.68 x 0.68 x 0.08 - FABRICACION EN OBRA Y COLOCACION",
                   "PARTIDA 01.04.04.05.01 TAPA CIEGA 0.68x0.68x0.08 SIN MARCO METALICO - %s - ESC. INDICADAS" % SUB_N_TAPAS)
    lam.juntar_llamadas()
    a = TAPA / 2; w = ASA_C["agarre"] / 2; g = ASA_C["gancho"]; pt = ASA_C["pata"]
    # ---------------- A. planta de la tapa (1/5)
    k = 2.0; ox_, oy_ = lam.P(150, 430)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    lam.rect(*P(-a, -a), *P(a, a), "REGISTRO-TAPA", const_width=0.004)
    lam.rect(*P(-a + 0.01, -a + 0.01), *P(a - 0.01, a - 0.01), "REGISTRO-TAPA")
    for i in range(7):
        d = -0.30 + i * 0.10
        barra(lam, P(-0.31, d), P(0.31, d), D38, k); barra(lam, P(d, -0.31), P(d, 0.31), D38, k, "ACERO-LONG")
    for ya in (-YA_C, YA_C):
        lam.rect(*P(-CAJ_C["largo"] / 2, ya - CAJ_C["ancho"] / 2), *P(CAJ_C["largo"] / 2, ya + CAJ_C["ancho"] / 2), "CONCRETO-OCULTO")
        barra(lam, P(-w, ya), P(w, ya), D12, k, "MARCO-METALICO")
        barra(lam, P(-w - g, ya + 0.012), P(-w, ya + 0.012), D12, k, "CONCRETO-OCULTO"); barra(lam, P(w, ya + 0.012), P(w + g, ya + 0.012), D12, k, "CONCRETO-OCULTO")
    lam.cota(P(-a, -a), P(a, -a), -6, texto="0.68"); lam.cota(P(-0.31, -a), P(0.31, -a), -11, texto="0.62 (barras)")
    lam.cota(P(a, -a), P(a, a), 6, horizontal=False, texto="0.68"); lam.cota(P(a, 0), P(a, YA_C), 12, horizontal=False, texto="0.20")
    lam.cota(P(-0.30, a), P(-0.20, a), 5, texto="0.10"); lam.cota(P(-a, a), P(-0.30, a), 5, texto="0.04")
    xt = 265
    LL(lam, P(a - 0.005, 0.25), xt, 530, ["cantos superiores biselados 1 x 1 cm", "(tapa ciega: sin marco metalico)"])
    LL(lam, P(0.20, 0.08), xt, 500, ["parrilla 7 + 7 barras 3/8\" @0.10, L = 0.62,", "recubrimiento 2.5 cm"])
    LL(lam, P(0.03, YA_C), xt, 470, ["asa de fierro liso 1/2\" (2 und) en cajuela 0.19 x 0.06 x 0.03,", "no sobresale; ganchos amarrados a la parrilla"])
    lam.titulo_vista(150, 335, "A. TAPA CIEGA - PLANTA (armado)", "ESC. 1/5 - " + TXT_REG_B, 150)
    # ---------------- B. corte de la tapa por el asa (1/2)
    k = 5.0; ox_, oy_ = lam.P(520, 490)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    cj = CAJ_C["largo"] / 2; pr = CAJ_C["prof"]
    tapa = [P(-a, 0), P(a, 0), P(a, ET - 0.01), P(a - 0.01, ET), P(cj, ET), P(cj, ET - pr), P(-cj, ET - pr), P(-cj, ET), P(-a + 0.01, ET), P(-a, ET - 0.01)]
    lam.poli(tapa, "REGISTRO-TAPA", cerrada=True, ancho=0.003); lam.achurado(tapa, escala_mm=0.8)
    for i in range(7): punto_barra(lam, P(-0.30 + i * 0.10, 0.025 + D38 * 1.5), D38, k)
    barra(lam, P(-0.31, 0.025), P(0.31, 0.025), D38, k, "ACERO-LONG")
    za = ET - 0.015
    lam.poli([P(-w - g, za - pt), P(-w, za - pt), P(-w, za), P(w, za), P(w, za - pt), P(w + g, za - pt)], "MARCO-METALICO", ancho=D12 * k)
    lam.cota(P(-a, 0), P(a, 0), -6, texto="0.68"); lam.cota(P(a, 0), P(a, ET), 8, horizontal=False, texto="0.08"); lam.cota(P(a, 0), P(a, 0.025), 4, horizontal=False, texto="0.025")
    lam.cota(P(-cj, ET), P(cj, ET), 5, texto="0.19"); lam.cota(P(-a, ET), P(-a + 0.01, ET), 5, texto="bisel 0.01")
    xt = 700
    LL(lam, P(a - 0.004, ET - 0.004), xt, 560, ["canto biselado 1 x 1 cm"])
    LL(lam, P(0.20, 0.025), xt, 540, ["parrilla 3/8\" @0.10 ambos sentidos,", "recubrimiento inferior 2.5 cm"])
    LL(lam, P(w + 0.06, za - pt), xt, 515, ["asa 1/2\" liso: agarre 0.15, patas 0.02,", "ganchos de 0.15 sobre la parrilla (L = 0.50)"])
    LL(lam, P(0.0, ET - 0.01), xt, 490, ["cajuela 0.19 x 0.06 x 0.03 (taco de madera", "o tecnopor en el vaciado)"])
    lam.titulo_vista(520, 445, "B. TAPA CIEGA - CORTE POR EL ASA", "ESC. 1/2", 140)
    # ---------------- C. asa (1/2)
    k = 5.0; ox_, oy_ = lam.P(470, 395)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    pts = [P(-w - g, -pt), P(-w, -pt), P(-w, 0), P(w, 0), P(w, -pt), P(w + g, -pt)]
    lam.poli(pts, "MARCO-METALICO", ancho=D12 * k)
    lam.cota(P(-w, 0), P(w, 0), 6, texto="0.15"); lam.cota(P(w + g, -pt), P(w + g, 0), 6, horizontal=False, texto="0.02")
    lam.cota(P(w, -pt), P(w + g, -pt), -5, texto="0.15")
    lam.texto(lam.P(470, 368), "asa de fierro liso 1/2\": desarrollo 0.15 + 2 x 0.02 + 2 x 0.15 = 0.49 m (se toma 0.50); 2 por tapa", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(470, 355, "C. ASA DE IZAJE", "ESC. 1/2", 120)
    # ---------------- D. molde de fabricacion (1/5)
    k = 2.0; ox_, oy_ = lam.P(690, 400)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    e1 = 0.019
    lam.rect(*P(-0.42, -0.025), *P(0.42, 0), "RELLENO"); lam.relleno([P(-0.42, -0.025), P(0.42, -0.025), P(0.42, 0), P(-0.42, 0)], "RELLENO")
    for s in (-1, 1):
        pts = [P(s * a, 0), P(s * (a + e1), 0), P(s * (a + e1), ET), P(s * a, ET)]
        lam.poli(pts, "RELLENO", cerrada=True); lam.relleno(pts, "RELLENO")
        lam.poli([P(s * a, ET), P(s * (a - 0.01), ET), P(s * a, ET - 0.01)], "RELLENO", cerrada=True)
    lam.rect(*P(-a, 0), *P(a, ET), "REGISTRO-TAPA")
    lam.rect(*P(-cj, ET - pr), *P(cj, ET), "RELLENO")
    lam.cota(P(-a, ET), P(a, ET), 6, texto="0.68 (interior del molde)"); lam.cota(P(a + e1, 0), P(a + e1, ET), 5, horizontal=False, texto="0.08")
    lam.texto(P(0, -0.06), "tablero de vaciado 0.80 x 0.80 (base nivelada)", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(690, 355, "D. MOLDE DE FABRICACION", "ESC. 1/5 - madera con desmoldante", 120)
    # ---------------- E. colocacion en el rebaje (1/5)
    k = 2.0; ox_, oy_ = lam.P(150, 225)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    for s in (-1, 1):
        hatch_conc(lam, [P(s * (REB / 2 + 0.01), 0), P(s * 0.55, 0), P(s * 0.55, -0.10), P(s * 0.45, -0.10), P(s * 0.45, -0.20), P(s * LUZ_L / 2, -0.20),
                         P(s * LUZ_L / 2, -ET), P(s * REB / 2, -ET), P(s * REB / 2, -0.01)], 0.6)
    tp = [P(-a, -ET), P(a, -ET), P(a, -0.01), P(a - 0.01, 0), P(-a + 0.01, 0), P(-a, -0.01)]
    lam.poli(tp, "REGISTRO-TAPA", cerrada=True); lam.achurado(tp, escala_mm=0.6)
    lam.cota(P(-REB / 2, 0), P(REB / 2, 0), 6, texto="0.70"); lam.cota(P(-LUZ_L / 2, -0.20), P(LUZ_L / 2, -0.20), -6, texto="0.60")
    lam.cota(P(a, 0), P(REB / 2, 0), 12, texto="1 cm")
    lam.texto(P(0, 0.13), "la tapa se baja con 2 ganchos en las asas y asienta en el rebaje, al ras del NPT", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(150, 160, "E. COLOCACION DE LA TAPA EN EL REBAJE", "ESC. 1/5 - sin mortero ni sello (tapa removible)", 150)
    # ---------------- procedimiento, cuadro, leyenda
    lam.notas(330, 300, "PROCEDIMIENTO DE FABRICACION Y COLOCACION", [
        "1. Molde: tablero de 0.80 x 0.80 nivelado y molde lateral de madera de 0.68 x 0.68 x 0.08 interior, con tiras de chaflan 1 x 1 cm y desmoldante; reutilizable.",
        "2. Parrilla: 7 + 7 barras 3/8\" de 0.62 m @0.10, amarradas con alambre N 16, sobre dados de concreto de 2.5 cm (recubrimiento).",
        "3. Asas: 2 barras de fierro liso 1/2\" (agarre 0.15, patas 0.02 y ganchos de 0.15) amarradas sobre la parrilla; tacos de 0.19 x 0.06 x 0.03 para las cajuelas.",
        "4. Vaciado con concreto f'c = 210 kg/cm2, piedra de 1/2\", vibrado; acabado superior frotachado al mismo nivel de la vereda.",
        "5. Desmoldar a las 24 h y curar 7 dias con agua; la tapa no lleva marco ni contramarco metalico (no se suelda ni se pinta).",
        "6. Colocar la tapa en el rebaje de la losa (DD-01) con 2 operarios y ganchos en las asas: holgura 1 cm por lado, al ras del NPT. Marcar el numero de registro."], 1.8)
    n = MC.registros()["n"]
    L_p = 14 * 0.62; kg_p = L_p * MC.PESO["3/8"]; L_a = 2 * 0.50; kg_a = L_a * MC.PESO["1/2"]; vol = TAPA * TAPA * ET; enc = 4 * TAPA * ET
    filas = [["Concreto f'c = 210 kg/cm2 (0.68 x 0.68 x 0.08)", "m3", f3(vol), f2(n * vol), "01.04.04.05.01 (desagregado: concreto)"],
             ["Parrilla 3/8\" corrugado, 14 barras de 0.62 m", "m / kg", "%.2f / %.2f" % (L_p, kg_p), "%.2f / %.2f" % (n * L_p, n * kg_p), "01.04.04.05.01 (desagregado: acero)"],
             ["Asas de fierro liso 1/2\", 2 und de 0.50 m", "m / kg", "%.2f / %.2f" % (L_a, kg_a), "%.2f / %.2f" % (n * L_a, n * kg_a), "01.04.04.05.01 (desagregado: acero)"],
             ["Encofrado lateral de la tapa (4 x 0.68 x 0.08)", "m2", f3(enc), f2(n * enc), "01.04.04.05.01 (desagregado: encofrado)"],
             ["Alambre negro N 16 (0.06 kg por kg de acero)", "kg", "%.2f" % (0.06 * (kg_p + kg_a)), f2(n * 0.06 * (kg_p + kg_a)), "insumo del ACU"],
             ["Tablero de vaciado 0.80 x 0.80 (reutilizable 6 veces)", "p2", "1.15", f2(n * 1.15), "insumo del ACU"],
             ["Fabricacion, curado y colocacion de la tapa", "und", "1", "%d" % n, "01.04.04.05.01 TAPA DE REGISTRO (und)"]]
    cuadro(lam, 330, 245, "CUADRO DE COMPONENTES POR TAPA CIEGA (1 und) Y TOTAL (%d und)" % n, filas)
    lam.leyenda2(560, 180, [("linea2", "MARCO-METALICO", "asa de fierro liso 1/2\""), ("linea2", "ACERO", "barra 3/8\" (sentido X)"), ("linea2", "ACERO-LONG", "barra 3/8\" (sentido Y)"),
                            ("concreto", "CONCRETO", "concreto f'c=210 de la tapa"), ("relleno", "RELLENO", "molde / taco de madera")], 1.8)
    lam.volcar_llamadas()
    return lam


# ============================================================================= DD-03 juntas
def dd03(doc, ox, oy, R, T):
    SL = MC.SELLO; ASF = SL["clave"] == "asfaltico"; pr = SL["prof"]
    lam = B.Lamina(doc, ox, oy, 10, "DD-03", "DETALLE CONSTRUCTIVO: JUNTAS E=1\" CON TECNOPOR Y SELLADOR ASFALTICO (COLECTOR Y %s)" % ("CAJA CL" if MODO_DD03 == "caja_cl" else "CERCO") if ASF else "DETALLE CONSTRUCTIVO: JUNTA DE DILATACION E=1\" CON SELLADOR Y JUNTAS DE TECNOPOR",
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
    LL(lam, P(b / 2, ef + h * 0.45), xt, 450, [("sellador asfaltico 1\" x 2\" (RC-250 + arena) en" if ASF else "sello elastomerico de poliuretano 1\" x 1\" en"), "las caras interiores (2 x h + %.2f)" % b])
    LL(lam, P(0.2, ef + h + et), xt, 420, ["sello %s en la cara superior (%.2f)," % (SL["txt"], be), "enrasado con el acabado de la losa"])
    lam.titulo_vista(130, 262, "A. JUNTA DE DILATACION - SECCION TRANSVERSAL", "ESC. 1/10 - perimetro = 2 x %.2f + 2 x (%.2f + h + %.2f) = %.2f m (h = %.2f)" % (be, ef, et, per_j, h), 185)
    # ---------------- B. detalle de la junta (1/2)
    k = 5.0; ox_, oy_ = lam.P(560, 470)
    P = lambda x, y: (ox_ + x * k, oy_ + y * k)
    izq = [P(-0.25, 0), P(-e_j / 2, 0), P(-e_j / 2, em), P(-0.25, em)]; der = [P(e_j / 2, 0), P(0.25, 0), P(0.25, em), P(e_j / 2, em)]
    hatch_conc(lam, izq, 0.8); hatch_conc(lam, der, 0.8)
    tecnopor(lam, [P(-e_j / 2, 0), P(e_j / 2, 0), P(e_j / 2, em - pr), P(-e_j / 2, em - pr)])
    lam.relleno([P(-e_j / 2, em - pr), P(e_j / 2, em - pr), P(e_j / 2, em), P(-e_j / 2, em)], "CORTES")
    barra(lam, P(-0.25, em / 2), P(-e_j / 2 - 0.05, em / 2), D38, k, "ACERO-LONG"); barra(lam, P(e_j / 2 + 0.05, em / 2), P(0.25, em / 2), D38, k, "ACERO-LONG")
    for x in (-0.20, -e_j / 2 - 0.08, e_j / 2 + 0.08, 0.20): punto_barra(lam, P(x, em / 2), D38, k)
    lam.cota(P(-e_j / 2, 0), P(e_j / 2, 0), -6, texto="1\" (25 mm)"); lam.cota(P(e_j / 2, 0), P(e_j / 2 + 0.05, 0), -11, texto="0.05")
    lam.cota(P(0.25, em - pr), P(0.25, em), 6, horizontal=False, texto="%d mm" % round(pr * 1000)); lam.cota(P(0.25, 0), P(0.25, em - pr), 6, horizontal=False, texto="%.3f" % (em - pr))
    lam.texto(P(0, em + 0.025), "CARA INTERIOR (agua)", 1.8, "TEXTOS", TA.MIDDLE_CENTER); lam.texto(P(-0.12, -0.035), "CARA EXTERIOR (terreno)", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    xt = 700
    LL(lam, P(0, em - pr / 2), xt, 560, ["sellador asfaltico 1\" x 2\" (25 x 50 mm): asfalto liquido", "RC-250 + arena gruesa, compactado hasta el ras (EG-2013 MTC)"] if ASF else
       ["sello de poliuretano (Sikaflex 1a o similar)", "25 x 25 mm sobre imprimante; caras limpias y secas"])
    LL(lam, P(0, (em - pr) / 2), xt, 535, ["tecnopor de 1\" (densidad 15 kg/m3) en todo", "el espesor, retirado %d mm en la cara interior" % round(pr * 1000)])
    LL(lam, P(-0.10, em / 2), xt, 510, ["barras longitudinales 3/8\" interrumpidas", "a 0.05 de la junta (no la cruzan)"])
    LL(lam, P(0.20, em / 2), xt, 485, ["marcos 3/8\" a cada lado de la junta", "(DP-04 y DP-08)"])
    lam.titulo_vista(560, 435, "B. DETALLE DE LA JUNTA DE DILATACION", "ESC. 1/2 - corte longitudinal por el muro (igual en las losas)", 170)
    # ---------------- C. junta con la caja CL: corte longitudinal por el eje (1/10)
    if MODO_DD03 == "caja_cl":
        k = 1.0; ox_, oy_ = lam.P(360, 90)
        P = lambda x, y: (ox_ + x * k, oy_ + y * k)
        zs = ef + h + et; ecl = 0.15; LC = 1.10
        hatch_conc(lam, [P(-LC, 0), P(0, 0), P(0, ef), P(-LC, ef)], 0.5); hatch_conc(lam, [P(-LC, ef + h), P(0, ef + h), P(0, zs), P(-LC, zs)], 0.5)
        lam.rect(*P(-LC, ef), *P(0, ef + h), "CONCRETO-OCULTO"); lam.rect(*P(-LC - 0.05, -0.05), *P(0, 0), "SOLADO")
        for z0, z1 in ((0, ef), (ef + h, zs)):
            tecnopor(lam, [P(0, z0), P(e_j, z0), P(e_j, z1), P(0, z1)])
        for z0, z1 in ((ef - pr, ef), (ef + h, ef + h + pr), (zs - pr, zs)):
            lam.relleno([P(0, z0), P(e_j, z0), P(e_j, z1), P(0, z1)], "CORTES")
        xw = e_j
        hatch_conc(lam, [P(xw, -0.45), P(xw + ecl, -0.45), P(xw + ecl, ef), P(xw, ef)], 0.5)
        hatch_conc(lam, [P(xw, ef + h), P(xw + ecl, ef + h), P(xw + ecl, zs), P(xw, zs)], 0.5)
        hatch_conc(lam, [P(xw + ecl, -0.45), P(xw + 0.75, -0.45), P(xw + 0.75, -0.30), P(xw + ecl, -0.30)], 0.5)
        lam.poli([P(xw + ecl, zs), P(xw + 0.75, zs)], "TERRENO", ancho=0.002); lam.poli([P(-LC - 0.3, zs), P(0, zs)], "TERRENO", ancho=0.002)
        lam.nivel(P(-0.8, zs), D["NPT"], texto="NPT +%.2f (losa = vereda)" % D["NPT"], lado=-1)
        lam.texto(P(-LC / 2, ef + h / 2), "COLECTOR CAR VARONES", 1.7, "TEXTOS", TA.MIDDLE_CENTER)
        lam.texto(P(xw + 0.45, -0.15), "CAJA CL", 1.7, "TEXTOS", TA.MIDDLE_CENTER)
        lam.cota(P(xw + ecl, ef), P(xw + ecl, ef + h), 8, horizontal=False, texto="ventana %.2f" % h)
        lam.cota(P(0, -0.05), P(e_j, -0.05), -6, texto="1\""); lam.cota(P(xw, -0.45), P(xw + ecl, -0.45), -6, texto="0.15")
        LL(lam, P(e_j / 2, ef - 0.08), 455, 104, ["plancha de tecnopor de 1\" en todo el contacto del", "colector con el muro este de la CL (seccion completa)"])
        lam.llamada(P(e_j / 2, ef + h + pr / 2), lam.P(420, 304), ["sellador asfaltico 1\" x 2\" (RC-250 + arena) en las caras", "interiores y en la cara superior, a ras"], 1.8, al=TA.RIGHT)
        lam.llamada(P(xw + ecl / 2, zs - 0.2), lam.P(420, 286), ["muro este de la caja CL (Hogar de Refugio, CUI 2675514)", "con ventana %.2f x %.2f para el colector" % (b, h)], 1.8, al=TA.RIGHT)
        lam.llamada(P(-0.6, ef / 2), lam.P(232, 100), ["losa de fondo del colector e = %.2f" % ef], 1.8, al=TA.RIGHT)
    else:
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
        tecnopor(lam, [P(em, zs - 0.9), P(xc, zs - 0.9), P(xc, zs - (pr if ASF else 0)), P(em, zs - (pr if ASF else 0))])
        if ASF: lam.relleno([P(em, zs - pr), P(xc, zs - pr), P(xc, zs), P(em, zs)], "CORTES")
        lam.poli([P(-0.4, zs), P(0, zs)], "TERRENO", ancho=0.002); lam.nivel(P(-0.25, zs), D["NPT"], texto="NPT +%.2f" % D["NPT"], lado=-1)
        lam.cota(P(em, zs - 0.9), P(xc, zs - 0.9), -6, texto="1\""); lam.cota(P(xc + 0.45, zs - 0.9), P(xc + 0.45, zs), 6, horizontal=False, texto="0.90")
        if CON_CERCO: lam.texto(P(-0.17, ef + h / 2), "INTERIOR DEL COLECTOR", 1.6, "TEXTOS", TA.MIDDLE_CENTER, rot=90)
        else: lam.texto(P(-0.17, ef + h / 2 + 0.03), "INTERIOR", 1.6, "TEXTOS", TA.MIDDLE_CENTER); lam.texto(P(-0.17, ef + h / 2 - 0.03), "DEL COLECTOR", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
        xt = 430
        if CON_CERCO:
            LL(lam, P(xc + 0.07, zs + 0.3), xt, 318, ["muro del cerco existente"])
            LL(lam, P(em + D["junta_cerco"] / 2, zs - 0.45), xt, 300, ["tecnopor de 1\" entre el muro lado predio y el", "cimiento del cerco: altura 0.90 (0.90 m2 por metro)"])
            if ASF: LL(lam, P(em + D["junta_cerco"] / 2, zs - pr / 2), xt, 336, ["sellador asfaltico 1\" x 2\" (RC-250 + arena)", "en la cara superior, a ras de la losa"])
            LL(lam, P(xc + 0.2, zs - 0.75), xt, 282, ["cimiento del cerco (no se toca; se protege", "durante la excavacion)"])
        else:
            LL(lam, P(xc + 0.6, zs - 0.05), 485, 122, ["piso terminado adyacente (+%.2f); no hay cerco" % D["NPT"]])
            LL(lam, P(em + D["junta_cerco"] / 2, zs - 0.05), 485, 106, ["tecnopor de 1\" entre la losa superior y el piso", "adyacente, a ambos lados del colector"])
        LL(lam, P(em / 2, zs - 1.2), xt if CON_CERCO else 485, 264 if CON_CERCO else 84, ["muro del colector e = 0.15 vaciado contra la", "plancha (encofrado perdido)"])
    lam.titulo_vista(360, 25, TIT_DD03_C, TXT_DD03_C, 170)
    # ---------------- D. seccion del colector: lados del colector (1/25)
    if MODO_DD03 == "caja_cl":
        k = 0.4; ox_, oy_ = lam.P(600, 308)
        P = lambda x, y: (ox_ + x * k, oy_ + y * k)
        zs = ef + h + et
        for q in ([(0, 0), (be, 0), (be, ef), (0, ef)], [(0, ef), (em, ef), (em, ef + h), (0, ef + h)], [(be - em, ef), (be, ef), (be, ef + h), (be - em, ef + h)],
                  [(0, ef + h), (be, ef + h), (be, zs), (0, zs)]):
            hatch_conc(lam, [P(*v) for v in q], 0.4)
        lam.rect(*P(-0.05, -0.05), *P(be + 0.05, 0), "SOLADO")
        for x0, x1 in ((-0.70, 0), (be, be + 0.70)):
            t_ = [P(x0, zs - 0.45), P(x1, zs - 0.45), P(x1, zs), P(x0, zs)]
            lam.achurado(t_, "TERRENO-ACHURADO", escala_mm=0.6); lam.poli([P(x0, zs), P(x1, zs)], "TERRENO", ancho=0.003)
        lam.texto(P(-0.35, zs + 0.12), "TERRENO NATURAL", 1.7, "TEXTOS", TA.MIDDLE_CENTER); lam.texto(P(be + 0.35, zs + 0.12), "TERRENO NATURAL", 1.7, "TEXTOS", TA.MIDDLE_CENTER)
        lam.texto(P(be / 2, ef + h / 2), "INTERIOR", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
        lam.cota(P(0, -0.05), P(be, -0.05), -5, texto="%.2f" % be)
        LL(lam, P(be / 2, zs - et / 2), 700, 392, ["losa superior del colector: sirve de vereda (+%.2f)" % D["NPT"]])
        LL(lam, P(-0.35, zs - 0.20), 700, 374, ["a ambos lados: terreno natural (sin piso):", "NO lleva junta longitudinal (relleno compactado)"])
        LL(lam, P(be + 0.35, zs - 0.20), 700, 356, ["la unica junta del colector con otra estructura", "es la de la caja CL (vista C)"])
        lam.titulo_vista(645, 289, "D. SECCION: TERRENO NATURAL A AMBOS LADOS", "ESC. 1/25 - sin junta longitudinal", 190)
    elif J["L_tecnopor_piso"] <= 0:
        k = 0.4; ox_, oy_ = lam.P(592, 308)
        P = lambda x, y: (ox_ + x * k, oy_ + y * k)
        zs = ef + h + et; xc = be + e_j
        for q in ([(0, 0), (be, 0), (be, ef), (0, ef)], [(0, ef), (em, ef), (em, ef + h), (0, ef + h)], [(be - em, ef), (be, ef), (be, ef + h), (be - em, ef + h)],
                  [(0, ef + h), (be, ef + h), (be, zs), (0, zs)]):
            hatch_conc(lam, [P(*v) for v in q], 0.4)
        lam.rect(*P(-0.05, -0.05), *P(be + 0.05, 0), "SOLADO")
        tecnopor(lam, [P(be, zs - 0.90), P(xc, zs - 0.90), P(xc, zs - pr), P(be, zs - pr)])
        lam.relleno([P(be, zs - pr), P(xc, zs - pr), P(xc, zs), P(be, zs)], "CORTES")
        cer1 = [P(xc, zs - 0.6), P(xc + 0.15, zs - 0.6), P(xc + 0.15, zs + 0.6), P(xc, zs + 0.6)]; cer2 = [P(xc, zs - 0.9), P(xc + 0.40, zs - 0.9), P(xc + 0.40, zs - 0.6), P(xc, zs - 0.6)]
        for c_ in (cer1, cer2): lam.poli(c_, "CERCO", cerrada=True); lam.achurado(c_, "TERRENO-ACHURADO", escala_mm=0.4)
        tierra = [P(-0.70, zs - 0.45), P(0, zs - 0.45), P(0, zs), P(-0.70, zs)]
        lam.achurado(tierra, "TERRENO-ACHURADO", escala_mm=0.6); lam.poli([P(-0.70, zs), P(0, zs)], "TERRENO", ancho=0.003)
        lam.texto(P(-0.35, zs + 0.12), "LADO VIA", 1.8, "TEXTOS", TA.MIDDLE_CENTER); lam.texto(P(xc + 0.30, zs + 0.75), "LADO PREDIO", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
        lam.texto(P(be / 2, ef + h / 2), "INTERIOR", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
        lam.cota(P(0, -0.05), P(be, -0.05), -5, texto="%.2f" % be); lam.cota(P(xc + 0.45, zs - 0.90), P(xc + 0.45, zs), 6, horizontal=False, texto="0.90")
        LL(lam, P(be + e_j / 2, zs - 0.45), 700, 410, ["JUNTA LONGITUDINAL: tecnopor 1\" de 0.90 m de altura + sellador", "asfaltico 1\" x 2\" arriba, de 0+000.00 a 0+058.81 (pegado al cerco)"])
        LL(lam, P(xc + 0.07, zs + 0.40), 700, 392, ["cerco perimetrico existente y su cimiento (no se tocan)"])
        LL(lam, P(-0.35, zs - 0.20), 700, 374, ["LADO VIA: terreno natural (sin piso):", "NO lleva junta (relleno compactado contra el muro)"])
        LL(lam, P(be / 2, zs - et / 2), 700, 356, ["losa superior del colector: sirve de vereda (+%.2f)" % D["NPT"]])
        lam.titulo_vista(645, 289, "D. SECCION: JUNTA LONGITUDINAL SOLO CONTRA EL CERCO", "ESC. 1/25 - al lado via hay terreno natural (sin junta)", 190)
    else:
        # ---------------- D. junta de tecnopor en el borde de la losa con el piso (1/5)
        k = 2.0; ox_, oy_ = lam.P(560, 330)
        P = lambda x, y: (ox_ + x * k, oy_ + y * k)
        hatch_conc(lam, [P(-0.6, 0), P(0, 0), P(0, et), P(-0.6, et)], 0.6)
        piso = [P(e_j, 0), P(0.6, 0), P(0.6, et), P(e_j, et)]; lam.poli(piso, "TERRENO", cerrada=True); lam.achurado(piso, "TERRENO-ACHURADO", escala_mm=0.5)
        tecnopor(lam, [P(0, 0), P(e_j, 0), P(e_j, et - (pr if ASF else 0)), P(0, et - (pr if ASF else 0))])
        if ASF:
            lam.relleno([P(0, et - pr), P(e_j, et - pr), P(e_j, et), P(0, et)], "CORTES")
            LL(lam, P(e_j / 2, et - pr / 2), 700, 385, ["sellador asfaltico 1\" x 2\" (RC-250 + arena)", "en la cara superior, a ras del piso"])
        lam.rect(*P(-0.6, -0.12), *P(0.6, 0), "RELLENO"); lam.texto(P(0, -0.06), "relleno compactado / muro del colector", 1.6, "TEXTOS", TA.MIDDLE_CENTER)
        lam.cota(P(0, 0), P(e_j, 0), -6, texto="1\""); lam.cota(P(0.6, 0), P(0.6, et), 6, horizontal=False, texto="0.10")
        lam.texto(P(-0.3, et + 0.03), "LOSA SUPERIOR DEL COLECTOR", 1.7, "TEXTOS", TA.MIDDLE_CENTER); lam.texto(P(0.33, et + 0.03), "PISO ADYACENTE (lado via)" if CON_CERCO else "PISO ADYACENTE (retiro)", 1.7, "TEXTOS", TA.MIDDLE_CENTER)
        LL(lam, P(e_j / 2, et / 2), 700, 365, ["tecnopor de 1\" en el espesor del piso (0.10):", "0.10 m2 por metro; " + ("lado via del colector y cajas" if CON_CERCO else "ambos lados del colector y cajas")])
        lam.titulo_vista(560, 290, "D. JUNTA DE TECNOPOR Y SELLADOR EN EL BORDE DE LA LOSA" if ASF else "D. JUNTA DE TECNOPOR EN EL BORDE DE LA LOSA", "ESC. 1/5", 170)
    # ---------------- E. ubicacion de las juntas de dilatacion
    progs = ["0+%06.2f" % (4.0 * (i + 1)) for i in range(J["n"])]
    ncol = max(2, -(-len(progs) // 9))
    filas = [[progs[i + 9 * c] if i + 9 * c < len(progs) else "" for c in range(ncol)] for i in range(9)]
    xu = 688 if MODO_DD03 == "caja_cl" else 700
    lam.tabla(xu, 245, ["JUNTA (prog.)"] * ncol, filas, [40] * ncol if ncol == 2 else [32] * ncol, 1.7, 4.4, "UBICACION DE LAS %d JUNTAS (planta y perfil)" % J["n"])
    lam.texto(lam.P(xu, 195), TXT_JUNTA_CAJAS[0], 1.6, "TEXTOS-NOTAS"); lam.texto(lam.P(xu, 191), TXT_JUNTA_CAJAS[1], 1.6, "TEXTOS-NOTAS")
    # ---------------- cuadro, procedimiento, leyenda
    per = J["L_dilat"] / J["n"]; a_tec = be * (ef + h + et) - b * h; sello = 2 * h + b + be; As = SL["ancho"] * SL["prof"]
    filas = [["Plancha de tecnopor 1\" (seccion %.2f x %.2f menos el hueco %.2f x %.2f)" % (be, ef + h + et, b, h), "m2", "%.3f (%.3f/m)" % (a_tec, a_tec / per), f2(J["n"] * a_tec), "01.04.04.06.01 (por metro de junta: perimetro %.2f m)" % per],
             *([["Sellador asfaltico 1\" x 2\" (caras interiores 2h + %.2f y superior %.2f)" % (b, be), "m", "%.2f (%.3f/m)" % (sello, sello / per), f2(J["n"] * sello), "01.04.04.06.01: %.5f m3 de mezcla por m de junta" % (As * sello / per)],
                ["Mezcla del sellador: 0.025 x 0.050 x longitud sellada", "m3", "%.4f" % (As * sello), "%.3f" % (J["n"] * As * sello), "RC-250 %.0f gal/m3 + arena gruesa %.2f m3/m3" % (MC.RC_GAL_M3, MC.ARENA_M3_M3)]] if ASF else
               [["Sello de poliuretano 25 x 25 mm (caras interiores 2h + %.2f y superior %.2f)" % (b, be), "m", "%.2f (%.3f/m)" % (sello, sello / per), f2(J["n"] * sello), "01.04.04.06.01: 0.63 L por metro de sello (aprox. 0.75 kg)"],
                ["Imprimante para el sello (0.10 L por metro de cordon)", "L", f2(sello * 0.10), f2(J["n"] * sello * 0.10), "insumo del ACU"]]),
             (["Tecnopor 1\" contra el cerco (junta longitudinal): altura 0.90 x %.2f m" % J["L_tecnopor_cerco"], "m2", "0.90 por m", f2(0.90 * J["L_tecnopor_cerco"]), "01.04.04.06.02 (tramo pegado al cerco)"] if CON_CERCO else
              ["Tecnopor 1\" en el contacto con la caja CL (seccion del colector menos el hueco)", "m2", f2(a_tec), f2(a_tec), "01.04.04.06.02 (empalme con la CL)"]),
             *([["Tecnopor 1\" en el borde de la losa con el piso: altura 0.10 x %.2f m" % J["L_tecnopor_piso"], "m2", "0.10 por m", f2(0.10 * J["L_tecnopor_piso"]), "01.04.04.06.02 (" + ("un lado: lado via del colector y cajas" if CON_CERCO else "ambos lados del colector y cajas") + ")"]]
               if J["L_tecnopor_piso"] > 0 else [])]
    if ASF and MODO_DD03 == "caja_cl":
        filas.append(["Sellador asfaltico 1\" x 2\" en la junta con la caja CL (caras interiores 2h + %.2f y superior %.2f)" % (b, be), "m3", "%.4f" % (As * sello), "%.4f" % (As * sello), "01.04.04.06.02 (contacto con la CL)"])
    elif ASF:
        L02 = J["L_tecnopor_cerco"] + J["L_tecnopor_piso"]
        filas.append(["Sellador asfaltico 1\" x 2\" en la cara superior de las juntas (02): %.2f m" % L02, "m3", "%.5f por m" % As, "%.3f" % (As * L02), "01.04.04.06.02 (" + ("cerco y bordes de losa" if J["L_tecnopor_piso"] > 0 else "junta longitudinal con el cerco") + ")"])
    cuadro(lam, 430, 165, "COMPONENTES POR JUNTA DE DILATACION (perimetro %.2f m) Y TOTAL (%d und); JUNTAS DE TECNOPOR POR METRO" % (per, J["n"]), filas, (104, 12, 30, 22, 78))
    lam.notas(430, 225, "PROCEDIMIENTO", [
        "1. Marcar las juntas cada 4.00 m (cuadro). Cortar la plancha de tecnopor a la forma de la seccion (anillo %.2f x %.2f con hueco %.2f x h) y fijarla al concreto ya vaciado." % (be, ef + h + et, b),
        "2. Vaciar el tramo siguiente contra la plancha. El acero longitudinal termina a 0.05 de cada lado; los marcos se colocan a cada lado de la junta.",
        ("3. Retirar 2\" (50 mm) de tecnopor en las caras interiores y en la cara superior; limpiar y secar; calentar el asfalto liquido RC-250, mezclarlo con arena gruesa "
         "y colocarlo compactando con tacos de madera hasta el ras (EG-2013 MTC)." if ASF else
         "3. Retirar 25 mm de tecnopor en las caras interiores y en la cara superior; limpiar, imprimar y aplicar el sello de poliuretano 25 x 25 mm con pistola; alisar."),
        NOTA4_DD03], 1.8, ancho_mm=ANCHO_PROC_DD03)
    lam.leyenda2(60, 235, [("concreto", "CONCRETO", "concreto f'c=210"), ("rect", "JUNTAS", "tecnopor 1\""), ("relleno", "CORTES", SL["ley"])] + ([("rect", "CERCO", "cerco existente")] if CON_CERCO else []) + [("linea2", "ACERO-LONG", "barra longitudinal 3/8\""), ("rect", "RELLENO", "relleno compactado")], 1.8)
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
    LL(lam, P(xq - e_j / 2, zc - 0.112), xt, 385, ["sellador asfaltico 1\" x 2\" (RC-250 + arena) en el", "contorno exterior de la junta"] if MC.SELLO["clave"] == "asfaltico" else ["sello elastomerico 25 x 25 mm en el contorno", "exterior de la junta"])
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
    if PARTIDA_EMPALME:
        lam.tabla(430, 270, ["CUNETA", "PROG.", "NCF LLEGA (msnm)", "H CUNETA (m)", "Hv VENTANA (m)", "ENCOF. CAJON (m2)", "ACERO BORDE 3/8\" (kg)", "TECNOPOR (m2)", "SELLO (m)"], filas, [22, 22, 26, 22, 24, 26, 30, 24, 20], 1.6, 4.4, "CUADRO DE EMPALMES: DIMENSIONES Y COMPONENTES POR CUNETA (DP-06C)")
    else:
        lam.tabla(430, 270, ["CUNETA", "PROG.", "NCF LLEGA (msnm)", "H CUNETA (m)", "Hv VENTANA (m)"], [f_[:5] for f_ in filas], [30, 30, 34, 30, 32], 1.7, 4.8, "CUADRO DE EMPALMES: DIMENSIONES POR CUNETA (DP-06C)")
    n = len(cun); hvm = sum(float(f[4]) for f in filas) / n; tot = lambda j: sum(float(f[j]) for f in filas)
    filas2 = [["Cajon de encofrado de la ventana 0.40 x Hv x 0.15 (madera, 2 usos)", "m2", f2(tot(5) / n), f2(tot(5)), "01.04.04.06.03 EMPALME (und)"],
              ["Refuerzo de borde 3/8\": 4 verticales (Hv + 0.60) + 2 horizontales de 1.00", "kg", f2(tot(6) / n), f2(tot(6)), "01.04.04.06.03 EMPALME (und)"],
              ["Tecnopor 1\" en el contorno de la cuneta (0.60 + 2 x H)", "m2", f2(tot(7) / n), f2(tot(7)), "01.04.04.06.03 EMPALME (und)"],
              [("Sellador asfaltico 1\" x 2\" en el contorno exterior" if MC.SELLO["clave"] == "asfaltico" else "Sello elastomerico 25 x 25 mm en el contorno exterior"), "m", f2(tot(8) / n), f2(tot(8)), "01.04.04.06.03 EMPALME (und)"],
              ["Acabado pulido del fondo (mortero 1:3, e = 1 cm) %.2f x 1.00" % b, "m2", f2(b), f2(b * n), "01.04.04.06.03 EMPALME (und)"],
              ["Perfilado y resane de los bordes de la ventana (mortero 1:3)", "m", f2(2 * 0.40 + 2 * hvm), f2(n * (2 * 0.40 + 2 * hvm)), "01.04.04.06.03 EMPALME (und)"],
              ["Registro de limpieza encima del empalme", "und", "1", "%d" % n, "01.04.04.05.01 TAPA DE REGISTRO (DD-01 y DD-02)"]]
    if PARTIDA_EMPALME:
        filas2 = [f_[:4] + [PARTIDA_EMPALME] if f_[4].startswith("01.04.04.06.03") else f_ for f_ in filas2]
        cuadro(lam, 430, 222, "CUADRO DE COMPONENTES POR EMPALME (promedio) Y TOTAL (%d und)" % n, filas2, (100, 12, 24, 22, 60))
    lam.notas(430, 172 if PARTIDA_EMPALME else 225, "PROCEDIMIENTO", [
        "1. Al armar el muro lado predio, colocar el refuerzo de borde (4 verticales y 2 horizontales) y el cajon de 0.40 x Hv con su fondo en la cota NCF de la cuneta (cuadro).",
        "2. Vaciar el muro y la losa superior monoliticos; retirar el cajon a los 2 dias, perfilar y resanar los bordes de la ventana.",
        "3. Empalmar la cuneta (o su prolongacion) contra el muro con la plancha de tecnopor de 1\" en todo su contorno; sellar el contorno exterior con " + ("sellador asfaltico 1\" x 2\" (RC-250 + arena)." if MC.SELLO["clave"] == "asfaltico" else "poliuretano."),
        "4. Pulir el fondo del colector en 1.00 m bajo la caida. Colocar el registro de limpieza sobre el empalme (DD-01 y DD-02)."], 1.8)
    lam.leyenda2(300, 115, [("concreto", "CONCRETO", "concreto del colector f'c=210"), ("rect", "TERRENO-ACHURADO", "cuneta existente (arquitectura)"), ("relleno", "ISO-CUNETA", "ventana de empalme"), ("rect", "JUNTAS", "tecnopor 1\""), ("relleno", "CORTES", "sellador asfaltico 1\" x 2\" / acabado pulido" if MC.SELLO["clave"] == "asfaltico" else "sello elastomerico / acabado pulido"), ("linea2", "ACERO", "marcos 3/8\""), ("linea2", "ACERO-LONG", "refuerzo de borde 3/8\""), ("linea", "AGUA", "agua")], 1.8, ancho_col=120, filas_col=4)
    lam.volcar_llamadas()
    return lam


def todas(doc, ox, oy, R, T):
    return [dd01(doc, ox, oy, R, T), dd02(doc, ox + 30, oy, R, T), dd03(doc, ox + 60, oy, R, T), dd04(doc, ox + 90, oy, R, T)]
