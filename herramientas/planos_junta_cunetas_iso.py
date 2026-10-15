"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): laminas DJ-02 y DJ-03 de las cunetas de piso.

DJ-02 (1/10): proceso constructivo de la junta de dilatacion e = 1" en toda la seccion en U, en cuatro isometricos 3D:
  1 vaciado del pano 1 hasta la junta; 2 plancha de tecnopor 1" en U; 3 acero y vaciado del pano 2 contra la plancha;
  4 sellador asfaltico 1" x 2" en la cara interior y rejilla colocada (corte parcial del muro cercano para ver el interior).
DJ-03: rejilla metalica movil de la partida 01.04.03.04.03.01 (platinas 1" x 3/16" de canto @1" y angulos L 1" x 1" x 3/16"),
  modulos de 1.00 m apoyados en el rebaje de 0.05 x 1" del borde interior de cada muro (seccion de cuneta del plano de
  arquitectura: interior 0.40, muros 0.10, rejilla de 0.497 m de ancho a ras del borde superior).
Escala real (1 unidad = 1 m); las vistas ampliadas se dibujan con su factor e indican su escala.
"""
import os, sys, math
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI); sys.path.insert(0, os.path.join(AQUI, "techo"))
import numpy as np
import dxf_base as B
from ezdxf.enums import TextEntityAlignment as TA
from iso3d import Escena
from dxf_detalles import hatch_conc, tecnopor, barra, punto_barra, D38

IN = 0.0254; T16 = 3 / 16 * IN                       # 1" y 3/16"
BI, EM, EL, HD, ES = 0.40, 0.10, 0.10, 0.50, 0.10     # cuneta: interior, muros, losa de fondo, altura interior dibujada, solado
BE = BI + 2 * EM
RB, RP = 0.05, IN                                     # rebaje para la rejilla: ancho y profundidad
EJ, PR = IN, 2 * IN                                   # junta 1" y sellador 2"
MOD, HOLG = 1.00, 0.0015                              # modulo de rejilla y holgura lateral
W_MOD = BI + 2 * RB - 2 * HOLG                        # 0.497
L_MOD = MOD - 0.003                                   # 3 mm entre modulos
PASO = IN                                             # platinas @1" entre ejes
N_PL = int(round(MOD / PASO))                         # 39 platinas por modulo (1.00 m / 1")
L_PL = W_MOD - 2 * IN                                 # platina entre las alas verticales de los angulos
KG_PL = IN * T16 * 7850                               # 0.95 kg/m
KG_L = 1.73                                           # L 1" x 1" x 3/16" (kg/m)
C_CON, C_TEC, C_SEL, C_ACE, C_SOL, C_MET, C_TIE = (205, 205, 200), (246, 246, 238), (40, 40, 40), (200, 45, 45), (170, 164, 152), (92, 104, 120), (196, 170, 128)


class S:
    """Escena con factor de escala k (vistas a otra escala dentro de la lamina)."""
    def __init__(self, k=1.0):
        self.E, self.k = Escena(), k
    def caja(self, x0, y0, z0, x1, y1, z1, rgb, paso=0.05):
        k = self.k; self.E.caja(x0 * k, y0 * k, z0 * k, x1 * k, y1 * k, z1 * k, rgb, paso * max(k, 1.0))
    def barra(self, a, b, rgb=C_ACE, r=D38 / 2):
        k = self.k; self.E.cilindro(tuple(v * k for v in a), tuple(v * k for v in b), r * k, rgb, n=6, tapas=False, paso=0.2)
    def grupo(self, g): self.E.g = g
    def dibujar(self, lam, xmm, ymm):
        P2 = self.E.dibujar(lam, xmm, ymm); k = self.k
        return lambda p: P2(tuple(v * k for v in p))


# ===================================================================== cuneta en U (con rebaje para la rejilla)
def cuneta(S_, x0, x1, rgb=C_CON, sin_cercano=None):
    """Losa de fondo y muros entre x0 y x1; sin_cercano=(a, b): tramo sin el muro cercano (y alto), corte parcial."""
    S_.caja(x0, 0, 0, x1, BE, EL, rgb)
    zt, zr = EL + HD, EL + HD - RP
    S_.caja(x0, 0, EL, x1, EM, zr, rgb); S_.caja(x0, 0, zr, x1, EM - RB, zt, rgb)            # muro lejano (y = 0)
    tramos = [(x0, x1)]
    if sin_cercano:
        a, b = max(x0, sin_cercano[0]), min(x1, sin_cercano[1])
        tramos = [t for t in ((x0, a), (b, x1)) if t[1] - t[0] > 1e-6] if a < b else [(x0, x1)]
    for xa, xb in tramos:                                                                     # muro cercano (y = BE)
        S_.caja(xa, BE - EM, EL, xb, BE, zr, rgb); S_.caja(xa, BE - EM + RB, zr, xb, BE, zt, rgb)


def plancha_u(S_, x, rgb=C_TEC, retiro=0.0, cercano=True):
    """Plancha de tecnopor 1" en toda la seccion en U (x .. x + 1"), retirada `retiro` desde la cara interior."""
    zt = EL + HD
    S_.caja(x, 0, 0, x + EJ, BE, EL - retiro, rgb)                                            # fondo
    S_.caja(x, 0, EL - retiro, x + EJ, EM - retiro, zt - RP, rgb); S_.caja(x, 0, zt - RP, x + EJ, EM - RB, zt, rgb)
    if cercano:
        S_.caja(x, BE - EM + retiro, EL - retiro, x + EJ, BE, zt - RP, rgb); S_.caja(x, BE - EM + RB, zt - RP, x + EJ, BE, zt, rgb)


def sellador_u(S_, x, cercano=True):
    zt = EL + HD
    S_.caja(x, EM - PR, EL - PR, x + EJ, BE - EM + PR, EL, C_SEL)                             # fondo (cara interior)
    S_.caja(x, EM - PR, EL, x + EJ, EM, zt - RP, C_SEL)
    if cercano: S_.caja(x, BE - EM, EL, x + EJ, BE - EM + PR, zt - RP, C_SEL)


def acero_pano(S_, x0, x1):
    """Acero 3/8": longitudinales @0.20 aprox. (fondo y muros) interrumpidos a 0.05 de las caras y U transversales @0.25."""
    r = 0.045
    xs = np.arange(x0 + 0.10, x1 - 0.05, 0.25)
    for x in xs:                                                                               # U transversal
        pts = [(x, r, EL + HD - 0.05), (x, r, r), (x, BE - r, r), (x, BE - r, EL + HD - 0.05)]
        for a, b in zip(pts[:-1], pts[1:]): S_.barra(a, b)
    for y in (0.15, 0.30, 0.45):
        S_.barra((x0 + 0.05, y, r), (x1 - 0.05, y, r), (40, 70, 200))
    for z in (0.30, 0.50):
        S_.barra((x0 + 0.05, r, z), (x1 - 0.05, r, z), (40, 70, 200)); S_.barra((x0 + 0.05, BE - r, z), (x1 - 0.05, BE - r, z), (40, 70, 200))


def solado(S_, x0, x1):
    S_.caja(x0, -0.05, -ES, x1, BE + 0.05, 0, C_SOL)


def modulo_rejilla(S_, x0, y0, z0, L=L_MOD):
    """Modulo de rejilla con origen en la esquina (x0, y0, z0): angulos con el ala horizontal hacia afuera, platinas de canto."""
    for ya, ys in ((y0, 1), (y0 + W_MOD, -1)):
        yh = sorted([ya, ya + ys * IN]); yv = sorted([ya + ys * (IN - T16), ya + ys * IN])
        S_.caja(x0, yh[0], z0, x0 + L, yh[1], z0 + T16, C_MET, 0.10)                            # ala horizontal
        S_.caja(x0, yv[0], z0, x0 + L, yv[1], z0 + IN, C_MET, 0.10)                             # ala vertical
    for i in range(int(round(L / PASO))):
        x = x0 + PASO / 2 + i * PASO
        S_.caja(x - T16 / 2, y0 + IN, z0, x + T16 / 2, y0 + W_MOD - IN, z0 + IN, C_MET, 0.10)


# ===================================================================== DJ-02
def dj02(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 10, "DJ-02", "JUNTA DE DILATACION EN CUNETAS: PROCESO CONSTRUCTIVO EN ISOMETRICO",
                   "PARTIDA 01.04.03.04.03.03 - JUNTA E=1\" EN TODA LA SECCION EN U CADA 3.00 m - 4 ETAPAS - ESC. 1/10")
    XJ, L2 = 0.80, 1.60                           # junta y largo del tramo dibujado
    zt = EL + HD
    etapas = []
    # 1. pano 1 vaciado
    s = S(); s.grupo(0); solado(s, 0, L2); s.grupo(1); cuneta(s, 0, XJ); etapas.append((s, [
        ((XJ, BE - EM / 2, zt - 0.2), "cara del pano 1 a plomo (tapa de encofrado en U retirada)"),
        ((XJ - 0.05, 0.30, EL), "acero longitudinal del pano 1 termina a 0.05 de la cara (dentro del concreto)"),
        ((L2 * 0.8, BE + 0.05, -ES / 2), "solado f'c=100, e=4\", corrido (sin junta)")],
        "1. VACIADO DEL PANO 1", "muros y losa de fondo hasta la junta; desencofrar la tapa"))
    # 2. plancha de tecnopor en U
    s = S(); s.grupo(0); solado(s, 0, L2); s.grupo(1); cuneta(s, 0, XJ); s.grupo(2); plancha_u(s, XJ); etapas.append((s, [
        ((XJ + EJ, BE - EM / 2, zt - 0.25), "plancha de tecnopor 1\" cortada en U: 2 muros + fondo"),
        ((XJ + EJ, 0.30, EL / 2), "pegada a la cara del pano 1, a ras del borde y del rebaje"),
        ((XJ + EJ, BE - EM / 2, 0.02), "cubre tambien la losa de fondo")],
        "2. PLANCHA DE TECNOPOR 1\" EN TODA LA SECCION", "se corta con la forma de la U y se fija al concreto"))
    # 3. acero del pano 2
    s = S(); s.grupo(0); solado(s, 0, L2); s.grupo(1); cuneta(s, 0, XJ); s.grupo(2); plancha_u(s, XJ); s.grupo(3); acero_pano(s, XJ + EJ, L2); etapas.append((s, [
        ((XJ + EJ + 0.35, BE - 0.045, zt - 0.05), "U transversal 3/8\" @0.25"),
        ((XJ + EJ + 0.05, 0.30, 0.045), "longitudinal 3/8\" a 0.05 de la plancha: NO cruza la junta"),
        ((XJ + EJ, BE - EM / 2, zt - 0.3), "vaciar el pano 2 contra la plancha (encofrado perdido)")],
        "3. ACERO Y VACIADO DEL PANO 2", "el acero de un pano no pasa al otro"))
    # 4. sellado y rejilla (corte parcial del muro cercano)
    s = S(); s.grupo(0); solado(s, 0, L2); s.grupo(1)
    cuneta(s, 0, XJ, sin_cercano=(0.35, 9)); cuneta(s, XJ + EJ, L2, sin_cercano=(-9, 1.25))
    plancha_u(s, XJ, retiro=PR, cercano=False); sellador_u(s, XJ, cercano=False)
    s.grupo(4); modulo_rejilla(s, 1.25 - L_MOD / 2 + 0.25, EM - RB + HOLG, zt - RP, L=0.60)
    etapas.append((s, [
        ((XJ + EJ / 2, EM - PR / 2, EL + 0.25), "sellador asfaltico 1\" x 2\" (RC-250 + arena) en la cara interior"),
        ((XJ + EJ / 2, 0.30, EL - 0.01), "tambien en el fondo: junta sellada muro - fondo - muro"),
        ((1.25, BE - EM / 2, zt), "rejilla en el rebaje 0.05 x 1\" (lamina DJ-03)"),
        ((0.35, BE - EM / 2, zt - 0.2), "muro cercano cortado para ver el interior")],
        "4. SELLADO Y REJILLA", "retirar 2\" de tecnopor, sellar compactando y colocar la rejilla"))
    pos = [(70, 520), (340, 520), (70, 270), (340, 270)]
    for (s, lls, tit, sub), (x, y) in zip(etapas, pos):
        P2 = s.dibujar(lam, x, y)
        lam.juntar_llamadas()
        for i, (p3, t) in enumerate(lls):
            q = P2(p3); lam.llamada(q, lam.P(x + 112, y + 52 - i * 11), [t], 1.8)
        lam.volcar_llamadas()
        lam.titulo_vista(x + 75, y - 127, tit, sub, 200)
    lam.notas(585, 560, "SECUENCIA (EG-2013 MTC, SECCION 510)", [
        "1. Vaciar el pano 1 de la cuneta (losa de fondo y muros) hasta la junta, con tapa de encofrado en U; el acero longitudinal termina a 0.05 m de la cara.",
        "2. Desencofrar la tapa y pegar la plancha de tecnopor de 1\" cortada con la forma de la U: cubre los 2 muros y la losa de fondo, a ras del borde y del rebaje.",
        "3. Armar el acero del pano 2 (U transversal 3/8\" @0.25 y longitudinales 3/8\") sin cruzar la junta y vaciar contra la plancha.",
        "4. Retirar 2\" (50 mm) de tecnopor en la cara interior de los muros y del fondo; limpiar y secar; calentar el RC-250, mezclarlo con arena gruesa y compactarlo con tacos hasta el ras.",
        "5. Colocar la rejilla en el rebaje (lamina DJ-03). La junta queda continua y alineada: muro - fondo - muro.",
        "6. Juntas cada 3.00 m y en los cambios de direccion; longitud por junta = 2 x H + 0.40 (lamina DJ-01). El solado se vacia corrido.",
    ], hmm=1.8, ancho_mm=235)
    from planos_techo import leyenda_colores
    leyenda_colores(lam, 585, 400, [(C_CON, "concreto f'c = 175 kg/cm2 de la cuneta"), (C_TEC, "plancha de tecnopor 1\""), (C_SEL, "sellador asfaltico 1\" x 2\" (RC-250 + arena)"),
                                    (C_ACE, "acero transversal 3/8\" (U)"), ((40, 70, 200), "acero longitudinal 3/8\""), (C_MET, "rejilla metalica movil"), (C_SOL, "solado f'c = 100 kg/cm2")])
    return lam


# ===================================================================== DJ-03
def dj03(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 10, "DJ-03", "REJILLA METALICA MOVIL EN CUNETA DE PISO: DETALLE, DESPIECE E ISOMETRICOS",
                   "PARTIDA 01.04.03.04.03.01 - PLATINAS 1\" x 3/16\" @1\" Y ANGULOS L 1\" x 1\" x 3/16\" - MODULOS DE 1.00 m - ESC. INDICADAS")
    zt = EL + HD
    # ---------------- A. isometrico del modulo (1/5)
    s = S(2.0); modulo_rejilla(s, 0, 0, 0)
    P2 = s.dibujar(lam, 110, 563)
    lam.juntar_llamadas()
    for i, (p, t) in enumerate((((0.6, 0, IN), ["angulo L 1\" x 1\" x 3/16\" (2 por modulo, L = 1.00 m)"]),
                                ((0.30, W_MOD / 2, IN), ["platinas 1\" x 3/16\" de canto @1\" entre ejes (%d por modulo)" % N_PL]),
                                ((L_MOD, W_MOD, 0), ["ala horizontal del angulo: apoyo en el rebaje"]))):
        lam.llamada(P2(p), lam.P(215, 575 - i * 9), t, 1.8)
    lam.volcar_llamadas()
    lam.titulo_vista(140, 398, "A. ISOMETRICO DE UN MODULO", "ESC. 1/5 - modulo de 1.00 x 0.497 m (%.1f kg)" % (N_PL * L_PL * KG_PL + 2 * L_MOD * KG_L), 150)
    # ---------------- B. colocacion en la cuneta (1/10)
    s = S(1.0); s.grupo(0); solado(s, 0, 2.2); s.grupo(1); cuneta(s, 0, 2.2)
    s.grupo(2); modulo_rejilla(s, 0.10, EM - RB + HOLG, zt - RP); s.grupo(3); modulo_rejilla(s, 1.15, EM - RB + HOLG, zt - RP + 0.25)
    P2 = s.dibujar(lam, 430, 512)
    lam.juntar_llamadas()
    for i, (p, t) in enumerate((((1.65, EM - RB + W_MOD / 2, zt + 0.25 + IN), ["modulo removible: se levanta para limpiar la cuneta"]),
                                ((0.6, EM - RB / 2, zt - RP), ["rebaje 0.05 x 1\" en el borde interior de cada muro"]),
                                ((0.6, EM - RB + W_MOD / 2, zt), ["rejilla a ras del borde superior de la cuneta"]),
                                ((2.2, BE / 2, EL / 2), ["cuneta: interior 0.40, muros y losa de 0.10"]))):
        lam.llamada(P2(p), lam.P(640, 575 - i * 9), t, 1.8)
    lam.volcar_llamadas()
    lam.titulo_vista(700, 515, "B. COLOCACION EN LA CUNETA", "ESC. 1/10 - modulos de 1.00 m, holgura de 3 mm entre modulos", 170)
    # ---------------- C. seccion transversal en el rebaje (1/2), medio ancho
    k = 5.0; O = lam.P(110, 290)
    P = lambda y, z: (O[0] + y * k, O[1] + (z - (zt - 0.10)) * k)       # muestra desde 0.10 bajo el borde
    z0 = zt - 0.10
    hatch_conc(lam, [P(0, z0), P(EM, z0), P(EM, zt - RP), P(EM - RB, zt - RP), P(EM - RB, zt), P(0, zt)], 0.8)
    lam.poli([P(-0.12, zt), P(-IN, zt)], "TERRENO", ancho=0.003)
    lam.relleno([P(-IN, z0), P(0, z0), P(0, zt), P(-IN, zt)], "CORTES")
    y0 = EM - RB + HOLG
    ang = [P(y0, zt - RP), P(y0 + IN, zt - RP), P(y0 + IN, zt), P(y0 + IN - T16, zt), P(y0 + IN - T16, zt - RP + T16), P(y0, zt - RP + T16)]
    lam.poli(ang, "MARCO-METALICO", cerrada=True); lam.relleno(ang, "MARCO-METALICO")
    lam.poli([P(y0 + IN, zt - RP), P(EM + 0.12, zt - RP), P(EM + 0.12, zt), P(y0 + IN, zt)], "MARCO-METALICO", cerrada=True)
    lam.texto(P(EM + 0.06, zt + 0.012), "platinas 1\" x 3/16\" (vista)", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.cota(P(EM - RB, zt), P(EM, zt), 6, texto="0.05"); lam.cota(P(0, zt), P(EM - RB, zt), 6, texto="0.05")
    lam.cota(P(EM + 0.12, zt - RP), P(EM + 0.12, zt), 5, horizontal=False, texto="1\"")
    lam.cota(P(EM - RB, zt - RP), P(y0, zt - RP), -12, texto="1.5 mm")
    lam.texto(P(EM / 2, z0 + 0.03), "MURO DE CUNETA e = 0.10", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.juntar_llamadas()
    for i, (p, t) in enumerate(((P(y0 + IN / 2, zt - RP + T16 / 2), ["angulo L 1\" x 1\" x 3/16\": ala horizontal apoyada en el rebaje,", "ala vertical hacia la cuneta"]),
                                (P(-IN / 2, zt - 0.03), ["junta asfaltica e = 1\" con el piso o terreno adyacente"]),
                                (P(EM - RB / 2, zt - RP), ["rebaje 0.05 x 1\" (se forma al vaciar el muro)"]))):
        lam.llamada(p, lam.P(285, 330 - i * 12), t, 1.8)
    lam.volcar_llamadas()
    lam.titulo_vista(150, 262, "C. SECCION DEL APOYO DE LA REJILLA", "ESC. 1/2 - igual en el muro opuesto (simetrico)", 160)
    # ---------------- D. planta del modulo (1/5)
    k = 2.0; O = lam.P(400, 250)
    Pp = lambda x, y: (O[0] + x * k, O[1] + y * k)
    lam.poli([Pp(0, 0), Pp(L_MOD, 0), Pp(L_MOD, W_MOD), Pp(0, W_MOD)], "MARCO-METALICO", cerrada=True)
    for yy in (IN, W_MOD - IN): lam.linea(Pp(0, yy), Pp(L_MOD, yy), "MARCO-METALICO")
    for i in range(N_PL):
        x = PASO / 2 + i * PASO
        lam.relleno([Pp(x - T16 / 2, IN), Pp(x + T16 / 2, IN), Pp(x + T16 / 2, W_MOD - IN), Pp(x - T16 / 2, W_MOD - IN)], "MARCO-METALICO")
    lam.cota(Pp(0, W_MOD), Pp(L_MOD, W_MOD), 6, texto="1.00 (modulo; 0.997 fabricado)")
    lam.cota(Pp(L_MOD, 0), Pp(L_MOD, W_MOD), 6, horizontal=False, texto="0.497")
    lam.cota(Pp(PASO / 2, 0), Pp(PASO * 1.5, 0), -6, texto="@1\"")
    lam.texto(Pp(L_MOD / 2, -0.06), "%d platinas de 1\" x 3/16\" x %.3f m por modulo; abertura libre 0.021 m" % (N_PL, L_PL), 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(500, 222, "D. PLANTA DEL MODULO", "ESC. 1/5 - B-B: corte longitudinal (vista E)", 150)
    # ---------------- E. corte longitudinal B-B (1/2), tramo de 0.15 m
    k = 5.0; O = lam.P(400, 160)
    Pe = lambda x, z: (O[0] + x * k, O[1] + z * k)
    lam.poli([Pe(0, 0), Pe(0.15, 0)], "MARCO-METALICO", ancho=T16 * k)
    lam.texto(Pe(0.155, T16 / 2), "ala horizontal del angulo (bajo las platinas)", 1.6, "TEXTOS", TA.MIDDLE_LEFT)
    for i in range(6):
        x = PASO / 2 + i * PASO
        r = [Pe(x - T16 / 2, 0), Pe(x + T16 / 2, 0), Pe(x + T16 / 2, IN), Pe(x - T16 / 2, IN)]
        lam.relleno(r, "MARCO-METALICO"); lam.poli(r, "MARCO-METALICO", cerrada=True)
    lam.cota(Pe(PASO / 2, IN), Pe(PASO * 1.5, IN), 6, texto="1\""); lam.cota(Pe(PASO * 1.5 + T16 / 2, 0), Pe(PASO * 2.5 - T16 / 2, 0), -6, texto="0.021")
    lam.cota(Pe(0, 0), Pe(0, IN), -8, horizontal=False, texto="1\"")
    lam.titulo_vista(460, 135, "E. CORTE B-B", "ESC. 1/2 - platinas de canto soldadas a los angulos", 120)
    # ---------------- F. despiece y notas
    kg_mod = N_PL * L_PL * KG_PL + 2 * L_MOD * KG_L
    pint = N_PL * L_PL * 2 * (IN + T16) + 2 * L_MOD * 4 * IN
    filas = [["Angulo L 1\" x 1\" x 3/16\" (1.73 kg/m)", "m", "%.3f" % (2 * L_MOD), "%.2f" % (2 * L_MOD * KG_L), "lados largos del modulo"],
             ["Platina 1\" x 3/16\" (%.3f kg/m)" % KG_PL, "m", "%.2f" % (N_PL * L_PL), "%.2f" % (N_PL * L_PL * KG_PL), "%d piezas de %.3f m @1\"" % (N_PL, L_PL)],
             ["Peso de un modulo (1.00 m de rejilla)", "kg", "-", "%.2f" % kg_mod, "= kg por metro de rejilla"],
             ["Cordones de soldadura E6011 1/8\" (2 por platina)", "und", "%d" % (2 * N_PL), "-", "cordon de 1\" en cada extremo"],
             ["Pintura anticorrosiva y esmalte (2 + 2 manos)", "m2", "%.2f" % pint, "-", "superficie de platinas y angulos"]]
    lam.tabla(630, 345, ["MATERIAL POR MODULO", "UND", "CANTIDAD", "kg", "OBSERVACION"], filas, [62, 10, 18, 14, 50], hmm=1.7, alto_mm=4.8,
              titulo="F. DESPIECE DE UN MODULO DE REJILLA")
    lam.notas(630, 298, "NOTAS", [
        "1. Rejilla metalica movil en los tramos abiertos de las cunetas de piso (hoja METRADO DE REJILLAS); se mide por metro a lo largo del eje.",
        "2. Modulos removibles de 1.00 m: 2 angulos L 1\" x 1\" x 3/16\" y %d platinas 1\" x 3/16\" de canto @1\" entre ejes, soldadas a tope al ala vertical del angulo." % N_PL,
        "3. Rebaje de 0.05 x 1\" en el borde interior de cada muro, formado con listones al vaciar; la rejilla queda a ras del borde superior.",
        "4. Acero A36; soldadura E6011 1/8\"; esmerilar, limpiar y pintar con 2 manos de anticorrosivo y 2 de esmalte.",
        "5. Colocar los modulos sin cojear, con 3 mm de holgura entre modulos y 1.5 mm a cada lado; no se fijan al concreto (son removibles).",
    ], hmm=1.7, ancho_mm=185)
    return lam
