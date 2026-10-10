"""Laminas de detalle de la red de recoleccion de techo (canaleta, soporte de platina, tapa lateral, boquilla,
montante, abrazaderas, colgadores, falsa columna y dado) para CAR Varones, Hogar de Refugio y CAR Mujeres.

Escala real (1 unidad = 1 m). DR-01 a 1/5 (detalles de la canaleta y sus accesorios) y DR-02 a 1/20 (elevacion de
la canaleta y corte del montante hasta la cuneta). Datos: metrado de cada proyecto (hojas METRADO CANALETAS y
METRADO MONTANTES), detalle de abrazadera de F°G° y de falsa columna de los planos de drenaje, memoria hidrologica
(canaletas S = 1.00 %). Los cuadros de metrado se leen de la planilla vigente de cada proyecto (no se recalculan).
Uso: python3 herramientas/techo/planos_techo.py
"""
import os, sys, math, warnings
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
sys.path.insert(0, HERR)
import openpyxl
import numpy as np
from iso3d import Escena
import dxf_base as B
import dxf_layouts as L
from ezdxf.enums import TextEntityAlignment as TA

for _e in (1, 5):
    if _e not in B.ESCALAS: B.ESCALAS.append(_e)
CAPAS_EXTRA = [("PLANCHA-GALV", 5, "CONTINUOUS", 40), ("PLATINA", 140, "CONTINUOUS", 50), ("PERNOS", 34, "CONTINUOUS", 25),
               ("TUBERIA-PVC", 3, "CONTINUOUS", 35), ("TUBERIA-OCULTA", 3, "HIDDEN", 25), ("COBERTURA", 8, "CONTINUOUS", 30),
               ("MURO", 8, "CONTINUOUS", 25), ("TUBO-PVC", 151, "CONTINUOUS", 35), ("ACCESORIO-PVC", 5, "CONTINUOUS", 40),
               ("COLGADOR", 30, "CONTINUOUS", 35), ("ABRAZADERA", 1, "CONTINUOUS", 35), ("TUBO-RELL", 151, "CONTINUOUS", 13),
               ("ACCES-RELL", 5, "CONTINUOUS", 13), ("COLG-RELL", 30, "CONTINUOUS", 13), ("ABRZ-RELL", 1, "CONTINUOUS", 13), ("GALV-RELL", 8, "CONTINUOUS", 13)]
B.COLOR_RGB.update({"TUBO-RELL": (196, 224, 250), "ACCES-RELL": (120, 150, 215), "COLG-RELL": (246, 186, 110),
                    "ABRZ-RELL": (236, 130, 130), "GALV-RELL": (226, 231, 238)})

PROY = {
    "varones": dict(nombre="CAR VARONES", cui="2705619", planilla="METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx",
                    salida=os.path.join(RAIZ, "entregables_varones", "PLANOS_DETALLE_RED_TECHO_CAR_VARONES.dxf"),
                    proyecto=("CREACION DEL SERVICIO DE PROTECCION INTEGRAL A NINAS, NINOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE PERDERLOS",
                              "EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2705619"),
                    ubicacion="UBICACION: PREDIO ALDEA INFANTIL VIRGEN DEL PILAR - MORALES - SAN MARTIN - SAN MARTIN"),
    "refugio": dict(nombre="HOGAR DE REFUGIO TEMPORAL", cui="2675514", planilla="METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx",
                    salida=os.path.join(RAIZ, "entregables", "PLANOS_DETALLE_RED_TECHO_HOGAR_REFUGIO.dxf"),
                    proyecto=B.PROYECTO, ubicacion=B.UBICACION),
    "mujeres": dict(nombre="CAR MUJERES", cui="2717013", planilla="METRADO_DRENAJE_PLUVIAL_CAR_MUJERES.xlsx",
                    salida=os.path.join(RAIZ, "entregables_mujeres", "PLANOS_DETALLE_RED_TECHO_CAR_MUJERES.dxf"),
                    proyecto=("CREACION DEL SERVICIO DE PROTECCION INTEGRAL A NINAS, NINOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE PERDERLOS",
                              "EN CENTRO DE ACOGIDA RESIDENCIAL - MUJERES, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2717013"),
                    ubicacion="UBICACION: PREDIO RURAL LOS MANGOS - MORALES - SAN MARTIN - SAN MARTIN"),
}

# ------------------------------------------------------------------ geometria (m), de los metrados y detalles
CB, CH, PEST = 0.20, 0.25, 0.05            # canaleta: ancho (fondo) 0.20 y alto 0.25 (indicacion del proyectista), pestana 0.05
EPL = 0.0254 / 8                            # platina 1" x 1/8": espesor
ANP = 0.0254                                # ancho de la platina
OREJA = 0.10                                # orejas del soporte (desarrollo = fondo + 2 lados + 2 orejas)
AL0 = CH - OREJA                            # fondo del alero sobre el fondo de la canaleta (oreja interior al ras del alero)
DES_SOP = 2 * OREJA + CB + 2 * CH           # desarrollo del soporte (0.90 m)
REM_UNION = int(round(2 * (CB + 2 * CH) / 0.05))   # remaches por union: 2 filas @0.05 en el perimetro (28)
SEC = "0.20 x 0.25"                         # ancho x alto
SEP_SOP = 0.60                              # soportes @0.60
DT = 0.114                                  # tubo PVC 4" (diametro exterior)
DB = 0.100                                  # cuello de la boquilla (entra en el montante)
ALERO_E, ALERO_V = 0.20, 0.60               # alero o viga de borde de concreto: espesor y vuelo desde el muro (tipico)
FC = (0.20, 0.15, 1.30); DADO = (0.40, 0.40, 0.35)
S_CAN = 1.00                                # pendiente de canaleta (memoria hidrologica)


def metrado(P):
    """Partidas de la red de techo y accesorios de la planilla vigente (valores guardados)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ws = openpyxl.load_workbook(os.path.join(RAIZ, "insumos", "metrados_vigentes", P["planilla"]), data_only=True)["RESUMEN"]
    claves = ("MONTANTE", "FALSA COLUMNA P/MONTANTE", "CANALETA DE PLANCHA", "SOPORTE DE PLATINA", "TAPA LATERAL", "BOQUILLA",
              "CODO DESAG", "COLGADOR", "ABRAZADERA")
    out = []
    for r in ws.iter_rows(values_only=True):
        if not r[0] or r[3] is None or not isinstance(r[3], (int, float)): continue
        d = str(r[1]).upper()
        if any(d.startswith(k) or (k in d and k in ("CODO DESAG", "COLGADOR", "ABRAZADERA")) for k in claves):
            if "CODO" in d and "Ø4" not in d.replace(" ", ""): continue
            out.append((str(r[0]), str(r[1])[:58], r[2] or "", r[3]))
    vistos, res = set(), []
    for o in out:                                   # el codo aparece en la red de piso y en accesorios: quedarse con accesorios
        if "CODO" in o[1].upper() and ("05.02." in o[0] or ".5.2." in o[0]): continue
        if o[0] in vistos: continue
        vistos.add(o[0]); res.append(o)
    return res


class V:
    """Vista: origen en papel (mm) y geometria relativa en metros (escala real)."""
    def __init__(self, lam, xmm, ymm):
        self.l = lam; self.O = lam.P(xmm, ymm)
    def __call__(self, u, v): return (self.O[0] + u, self.O[1] + v)
    def pl(self, pts, capa, cerrada=False, ancho=0.0): return self.l.poli([self(*p) for p in pts], capa, cerrada, ancho)
    def ln(self, a, b, capa): return self.l.linea(self(*a), self(*b), capa)
    def rect(self, u1, v1, u2, v2, capa): return self.l.rect(*self(u1, v1), *self(u2, v2), capa)
    def concreto(self, pts):
        self.l.relleno([self(*p) for p in pts], "CONCRETO-ACHURADO"); self.pl(pts, "CONCRETO", True)
    def circ(self, c, r, capa): return self.l.circulo(self(*c), r, capa)
    def cota(self, a, b, dmm, horizontal=True, texto=None, angulo=None): return self.l.cota(self(*a), self(*b), dmm, horizontal, texto, angulo=angulo)


def remache(v, c, capa="PERNOS"):
    v.circ(c, 0.0016, capa)


def perno(v, y, x0, largo, capa="PERNOS"):
    """Perno de expansion horizontal entrando hacia -x desde x0 (cabeza en x0)."""
    v.rect(x0, y - 0.0055, x0 + 0.004, y + 0.0055, capa)
    v.pl([(x0, y + 0.0032), (x0 - largo, y + 0.0032), (x0 - largo, y - 0.0032), (x0, y - 0.0032)], capa)


# ================================================================== DR-01 (1/5)
def dr01(doc, ox, oy, P, met):
    lam = B.Lamina(doc, ox, oy, 5, "DR-01", "DETALLES DE CANALETA DE TECHO, SOPORTE Y ACCESORIOS",
                   "SECCION, SOPORTE DE PLATINA, TAPA LATERAL, BOQUILLA, UNION, ABRAZADERA Y COLGADOR - " + P["nombre"])
    f = lam.f
    # ---------------- A. seccion tipica
    v = V(lam, 150, 335)
    xi = EPL; xo = xi + CB
    za1 = AL0 + ALERO_E
    v.concreto([(-0.42, AL0), (0.0, AL0), (0.0, za1), (-0.42, za1)])                                # alero / viga de borde
    v.pl([(-0.42, AL0 - 0.02), (-0.42, za1 + 0.02)], "MURO")                                          # corte del alero
    v.pl([(-0.42, za1 + 0.12), (-0.20, za1 + 0.098), (0.13, za1 + 0.065)], "COBERTURA", ancho=0.004)   # TR4 (pendiente 10 %)
    v.rect(-0.30, za1, -0.22, za1 + 0.09, "COBERTURA")                                               # apoyo / correa
    # canaleta (plancha 0.9 mm)
    v.pl([(xi, CH + PEST), (xi, 0.0), (xo, 0.0), (xo, CH), (xo - PEST, CH)], "PLANCHA-GALV", ancho=0.0012)
    lam.relleno([v(xi + 0.001, 0.001), v(xo - 0.001, 0.001), v(xo - 0.001, 0.055), v(xi + 0.001, 0.055)], "AGUA-RELLENO")
    v.ln((xi + 0.01, 0.055), (xo - 0.01, 0.055), "AGUA")
    # soporte de platina
    c = EPL / 2
    v.pl([(c, CH + OREJA), (c, -c), (xo + c, -c), (xo + c, CH + c), (xo + c - OREJA, CH + c)], "PLATINA", ancho=EPL)
    perno(v, CH + 0.075, c, 0.0635); perno(v, CH + 0.025, c, 0.0635)
    v.rect(xo - 0.075, CH + c, xo - 0.071, CH + 0.018, "PERNOS"); v.rect(CB / 2 - 0.002, -0.016, CB / 2 + 0.002, 0.004, "PERNOS")
    lam.texto(v(-0.20, AL0 + 0.115), "ALERO O VIGA DE BORDE", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto(v(-0.20, AL0 + 0.085), "DE CONCRETO (SEGUN ESTRUCTURAS)", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    v.cota((xi, 0.0), (xo, 0.0), -9); v.cota((xo, 0.0), (xo, CH), 8, False)
    v.cota((xi, CH), (xi, CH + PEST), -7, False); v.cota((xo - PEST, CH), (xo, CH), 9)
    v.cota((c, CH), (c, CH + OREJA), -16, False, "0.10")
    lam.juntar_llamadas()
    xt = v(0.36, 0)[0]
    for (u, w), t in (((0.05, za1 + 0.072), ["Cobertura de aluzinc TR4 e = 0.40 mm (vuela 0.13 m sobre la canaleta)"]),
                      ((c, CH + 0.075), ["Perno de expansion 1/4\" x 2 1/2\" con tarugo (2 por soporte)"]),
                      ((xi + 0.002, CH + 0.04), ["Pestana interior 0.05 contra el alero"]),
                      ((xo - 0.03, CH + 0.003), ["Pestana exterior 0.05 doblada hacia adentro + oreja del soporte",
                                                 "con tornillo autorroscante 1/4\" x 3/4\""]),
                      ((xo - 0.01, 0.14), ["Canaleta de plancha galvanizada e = 0.9 mm, %s (ancho x alto)" % SEC]),
                      ((xo + c, 0.06), ["Soporte de platina F°G° 1\" x 1/8\" @0.60 m (desarrollo %.2f m)" % DES_SOP]),
                      ((0.06, 0.04), ["Agua de lluvia: pendiente de la canaleta S = %.2f %% hacia la boquilla" % S_CAN]),
                      ((CB / 2, -0.012), ["Tornillo autorroscante 1/4\" x 3/4\" en el fondo"])):
        lam.llamada(v(u, w), (xt, v(0, w)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(150 + 25, 335 - 32, "A. SECCION TIPICA DE CANALETA CON SOPORTE", "ESC. 1/5", 120)

    # ---------------- B. desarrollo del soporte (platina estirada)
    v = V(lam, 450, 470)
    Ltot = 2 * OREJA + CB + 2 * CH
    v.rect(0, 0, Ltot, ANP, "PLATINA")
    lam.relleno([v(0, 0), v(Ltot, 0), v(Ltot, ANP), v(0, ANP)], "ISO-CONCRETO-LAT1")
    dob = [OREJA + CH, OREJA + CH + CB, OREJA + 2 * CH + CB]
    for x in dob: v.ln((x, -0.012), (x, ANP + 0.012), "CORTES")
    for x in (0.025, 0.075): v.circ((x, ANP / 2), 0.004, "PERNOS")
    for x in (OREJA + CH + CB / 2, Ltot - 0.07): v.circ((x, ANP / 2), 0.003, "PERNOS")
    xs = [0.0, OREJA, OREJA + CH, OREJA + CH + CB, OREJA + 2 * CH + CB, Ltot]
    for a, b in zip(xs[:-1], xs[1:]): v.cota((a, 0), (b, 0), -8)
    v.cota((0, 0), (Ltot, 0), -16)
    v.cota((Ltot, 0), (Ltot, ANP), 8, False, "1\"")
    for x, t in ((OREJA / 2, "OREJA INT."), (OREJA + CH / 2, "LADO INT."), (OREJA + CH + CB / 2, "FONDO"),
                 (OREJA + 1.5 * CH + CB, "LADO EXT."), (Ltot - OREJA / 2, "OREJA EXT.")):
        lam.texto(v(x, ANP + 0.022), t, 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto(v(Ltot / 2, ANP + 0.055), "Dobleces a 90 grados en las lineas indicadas; perforaciones de 5/16\" (pernos) y 1/4\" (tornillos)", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(450 + Ltot / f / 2, 470 - 32, "B. DESARROLLO DEL SOPORTE DE PLATINA F°G° 1\" x 1/8\"", "ESC. 1/5 - L = %.2f m por soporte" % DES_SOP, 150)

    # ---------------- C. tapa lateral
    v = V(lam, 460, 330)
    v.pl([(0, CH + PEST), (0, 0), (CB, 0), (CB, CH), (CB - PEST, CH)], "PLANCHA-GALV", ancho=0.0012)
    v.pl([(-0.03, CH + PEST), (-0.03, -0.03), (CB + 0.03, -0.03), (CB + 0.03, CH)], "PLANCHA-GALV")
    lam.relleno([v(0, 0), v(CB, 0), v(CB, CH), v(CB - PEST, CH), v(0, CH)], "ISO-TAPA")
    for (x, y) in ((-0.015, 0.08), (-0.015, 0.17), (CB + 0.015, 0.08), (CB + 0.015, 0.17), (0.06, -0.015), (0.14, -0.015)): remache(v, (x, y))
    v.cota((0, -0.03), (CB, -0.03), -8); v.cota((CB + 0.03, 0), (CB + 0.03, CH), 8, False)
    v.cota((-0.03, -0.03), (0, -0.03), -16, True, "0.03")
    lam.juntar_llamadas()
    for (u, w), t in (((CB / 2, 0.12), ["Tapa de plancha galvanizada e = 0.9 mm con la seccion de la canaleta"]),
                      ((-0.03, 0.10), ["Pestana perimetral 0.03 que entra en la canaleta"]),
                      ((-0.015, 0.14), ["6 remaches pop 1/8\" por tapa (2 por lado) + cordon de sellador"])):
        lam.llamada(v(u, w), (v(0.33, 0)[0], v(0, w)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(460 + 25, 330 - 30, "C. TAPA LATERAL (EXTREMOS)", "ESC. 1/5 - 2 por canaleta", 80)

    # ---------------- D. boquilla: corte y planta
    v = V(lam, 95, 200)
    v.pl([(-0.03, 0.0), (0.05, 0.0)], "PLANCHA-GALV", ancho=0.0012); v.pl([(0.15, 0.0), (0.23, 0.0)], "PLANCHA-GALV", ancho=0.0012)
    v.pl([(0.0, -0.002), (0.05, -0.002), (0.05, -0.15)], "PLANCHA-GALV", ancho=0.0010)
    v.pl([(0.20, -0.002), (0.15, -0.002), (0.15, -0.15)], "PLANCHA-GALV", ancho=0.0010)
    xm = 0.10                                                           # eje del montante
    v.pl([(xm - DT / 2, -0.06), (xm - DT / 2, -0.24)], "TUBERIA-PVC", ancho=0.004); v.pl([(xm + DT / 2, -0.06), (xm + DT / 2, -0.24)], "TUBERIA-PVC", ancho=0.004)
    for x in (0.01, 0.03, 0.17, 0.19): remache(v, (x, 0.0))
    v.cota((0.0, -0.002), (0.20, -0.002), 12, True, "0.20")
    v.cota((0.05, -0.15), (0.15, -0.15), -6, True, "Ø 0.10")
    v.cota((0.05, -0.002), (0.05, -0.15), -14, False)
    lam.juntar_llamadas()
    for (u, w), t in (((0.22, 0.0), ["Fondo de la canaleta (abertura Ø 0.10 en el punto bajo)"]),
                      ((0.18, -0.002), ["Brida de 0.20 x 0.20 remachada (8 remaches) y sellada"]),
                      ((0.15, -0.10), ["Cuello de plancha galvanizada Ø 0.10 x 0.15 que entra en el montante"]),
                      ((xm + DT / 2, -0.20), ["Montante de tuberia PVC 4\" (campana arriba)"])):
        lam.llamada(v(u, w), (v(0.33, 0)[0], v(0, w)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(95 + 22, 200 - 58, "D. BOQUILLA A MONTANTE Ø 4\" - CORTE", "ESC. 1/5", 90)
    v = V(lam, 300, 150)
    v.rect(0, 0, 0.20, 0.20, "PLANCHA-GALV"); v.circ((0.10, 0.10), DB / 2, "PLANCHA-GALV")
    for x, y in ((0.02, 0.02), (0.10, 0.02), (0.18, 0.02), (0.02, 0.10), (0.18, 0.10), (0.02, 0.18), (0.10, 0.18), (0.18, 0.18)): remache(v, (x, y))
    v.cota((0, 0), (0.20, 0), -8); v.cota((0.20, 0), (0.20, 0.20), 8, False)
    lam.titulo_vista(300 + 20, 150 - 16, "D'. BOQUILLA - PLANTA DE LA BRIDA", "ESC. 1/5 - 8 remaches pop 1/8\"", 80)

    # ---------------- E. union de tramos (vista del lado exterior)
    v = V(lam, 470, 185)
    v.pl([(0.0, 0.0), (0.45, 0.0), (0.45, CH), (0.0, CH)], "PLANCHA-GALV")
    v.pl([(0.40, -0.004), (0.85, -0.004), (0.85, CH + 0.004), (0.40, CH + 0.004)], "PLANCHA-GALV")
    lam.relleno([v(0.40, 0), v(0.45, 0), v(0.45, CH), v(0.40, CH)], "ISO-CONCRETO-LAT1")
    for x in (0.4125, 0.4375):
        for k in range(int(CH / 0.05)): remache(v, (x, 0.025 + k * 0.05))
    v.cota((0.40, CH), (0.45, CH), 8, True, "0.05")
    v.cota((0.0, 0.0), (0.0, CH), -8, False)
    lam.juntar_llamadas()
    for (u, w), t in (((0.4125, 0.125), ["2 filas de remaches pop 1/8\" @0.05 en todo el perimetro (%d por union)" % REM_UNION]),
                      ((0.44, 0.035), ["Traslape 0.05 con cordon de sellador de poliuretano;", "el tramo de aguas arriba va por dentro del de aguas abajo"])):
        lam.llamada(v(u, w), (v(0.92, 0)[0], v(0, w)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(470 + 42, 185 - 22, "E. UNION DE TRAMOS DE CANALETA (CADA 2.44 m)", "ESC. 1/5 - vista del lado exterior", 120)

    # ---------------- F. abrazadera de F°G° (montante)
    v = V(lam, 115, 75)
    r_i = DT / 2 + 0.0254 / 8                                         # diametro interior 1/4" mayor que el tubo
    v.concreto([(-0.13, 0.0), (0.13, 0.0), (0.13, -0.08), (-0.13, -0.08)])          # muro / columna
    v.circ((0, r_i + 0.0), DT / 2, "TUBERIA-PVC")
    pts = [(-0.11, 0.0016), (-r_i - 0.0016, 0.0016)]
    pts += [(math.cos(a) * (r_i + 0.0016), r_i + math.sin(a) * (r_i + 0.0016)) for a in [math.pi + k * math.pi / 24 for k in range(0, 25)][::-1]][::-1]
    v.pl([(-0.11, 0.0016), (-r_i - 0.0016, 0.0016)] + [(math.cos(math.pi - k * math.pi / 24) * (r_i + 0.0016), r_i + math.sin(math.pi - k * math.pi / 24) * (r_i + 0.0016)) for k in range(25)] + [(r_i + 0.0016, 0.0016), (0.11, 0.0016)], "PLATINA", ancho=EPL)
    for x in (-0.09, 0.09):
        v.pl([(x - 0.003, 0.004), (x - 0.003, -0.055), (x, -0.06), (x + 0.003, -0.055), (x + 0.003, 0.004)], "PERNOS")
        v.rect(x - 0.008, 0.0032, x + 0.008, 0.008, "PERNOS")
    v.cota((-0.11, 0.0), (0.11, 0.0), -16, True)
    lam.juntar_llamadas()
    for (u, w), t in (((0.0, r_i + DT / 2), ["Montante de tuberia PVC 4\" (Ø ext. 0.114)"]),
                      ((r_i * 0.7, r_i + r_i * 0.7), ["Abrazadera de platina F°G° e = 1/8\" con 2 orejas, @1.50 m;",
                                                       "diametro interior 1/4\" mayor que el tubo"]),
                      ((0.09, -0.03), ["Tirafon 2\" x 1/4\" (55 x 6 mm) en tarugo plastico con estrias 2\" x 1/2\""])):
        lam.llamada(v(u, w), (v(0.20, 0)[0], v(0, w)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(115 + 30, 75 - 22, "F. ABRAZADERA DE F°G° EN MONTANTE", "ESC. 1/5 - corte horizontal", 90)

    # ---------------- G. colgador
    v = V(lam, 300, 30)
    v.concreto([(-0.12, 0.30), (0.12, 0.30), (0.12, 0.38), (-0.12, 0.38)])           # fondo del alero
    v.circ((0, 0.10), DT / 2, "TUBERIA-PVC")
    v.circ((0, 0.10), DT / 2 + 0.003, "PLATINA")
    v.pl([(0, 0.10 + DT / 2 + 0.003), (0, 0.36)], "PERNOS", ancho=0.0095)
    v.rect(-0.012, 0.10 + DT / 2 + 0.003, 0.012, 0.10 + DT / 2 + 0.015, "PERNOS")
    v.cota((0.0, 0.10 + DT / 2), (0.0, 0.30), 18, False)
    lam.juntar_llamadas()
    for (u, w), t in (((0.0, 0.34), ["Anclaje de expansion 3/8\" en el fondo del alero"]),
                      ((0.0, 0.25), ["Varilla roscada F°G° 3/8\" con tuerca y contratuerca"]),
                      ((DT / 2 + 0.003, 0.10), ["Colgador F°G° tipo abrazadera para tubo 4\"; uno junto a cada codo del desvio"])):
        lam.llamada(v(u, w), (v(0.16, 0)[0], v(0, w)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(300 + 12, 30 - 6 + 2, "G. COLGADOR F°G° (DESVIO BAJO EL ALERO)", "ESC. 1/5", 90)

    # ---------------- cuadro de metrado y notas
    filas = [(c, d[:44], u, ("%.2f" % m) if isinstance(m, float) and m % 1 else "%d" % m) for c, d, u, m in met]
    yb = lam.tabla(646, 560, ["PARTIDA", "DESCRIPCION", "UND", "METRADO"], filas, [30, 104, 12, 22], hmm=1.7, alto_mm=4.6,
                   titulo="METRADO DE LA RED DE TECHO (PLANILLA)")
    lam.notas(646, yb - 6, "NOTAS", [
        "1. Canaleta de plancha de acero galvanizado e = 0.9 mm, seccion interior 0.20 (ancho) x 0.25 (alto) m con pestanas de 0.05 m, en tramos de 2.44 m.",
        "2. Pendiente de la canaleta S = 1.00 % hacia las boquillas (memoria hidrologica); verificar con nivel antes de fijar.",
        "3. Soportes de platina F°G° 1\" x 1/8\" @0.60 m (hoja METRADO CANALETAS: soportes = L / 0.60 + 1 por canaleta).",
        "4. Abrazaderas F°G° @1.50 m en el montante; colgadores junto a cada codo del desvio bajo el alero.",
        "5. Cortes y perforaciones del galvanizado: dos manos de pintura rica en zinc.",
        "6. Las dimensiones del alero, la viga de borde y la cobertura son referenciales: ver planos de arquitectura y estructuras.",
    ], hmm=1.6, ancho_mm=180)
    return lam


def ruta():
    """Recorrido tipico del montante (comun al corte DR-02 y a los isometricos): y = distancia desde la cara del muro, z = altura."""
    z_al = 3.00; xa = ALERO_V; zc = z_al - AL0; yi = xa + EPL
    return dict(z_al=z_al, xa=xa, zc=zc, yi=yi, yo=yi + CB, yb=yi + CB / 2, ztop=zc - 0.06, zc1=zc - 0.45, yt=FC[1] / 2, zs=-0.20,
                ycu=xa + 0.60, R=0.10, camp=0.05, colg=[yi + CB / 2 - 0.22, FC[1] / 2 + 0.24], abr=[1.45, 2.15])


def tubo2d(v, p, q, r=DT / 2, oculto=False):
    p, q = np.asarray(p, float), np.asarray(q, float); d = q - p; L = np.linalg.norm(d)
    if L < 1e-6: return
    n = np.array([-d[1], d[0]]) / L * r
    pts = [p + n, q + n, q - n, p - n]
    if not oculto: v.l.relleno([v(*x) for x in pts], "TUBO-RELL")
    capa = "TUBERIA-OCULTA" if oculto else "TUBO-PVC"
    v.ln(tuple(p + n), tuple(q + n), capa); v.ln(tuple(p - n), tuple(q - n), capa)


def codo2d(v, P, a, b, R, r=DT / 2, oculto=False, camp=0.05):
    """Codo de 90 grados en el plano del corte: arcos interior y exterior y las dos campanas."""
    P, a, b = (np.asarray(x, float) for x in (P, a, b))
    S = P - a * R; C = S + b * R
    ext, inn = [], []
    for k in range(17):
        th = math.pi / 2 * k / 16; u = -b * math.cos(th) + a * math.sin(th)
        ext.append(C + (R + r) * u); inn.append(C + (R - r) * u)
    capa = "TUBERIA-OCULTA" if oculto else "ACCESORIO-PVC"
    if not oculto: v.l.relleno([v(*x) for x in ext + inn[::-1]], "ACCES-RELL")
    v.pl([tuple(x) for x in ext], capa); v.pl([tuple(x) for x in inn], capa)
    for base, d in ((S, -a), (P + b * R, b)):
        n = np.array([-d[1], d[0]]) * (r + 0.008)
        pts = [base + n, base + n + d * camp, base - n + d * camp, base - n]
        if not oculto: v.l.relleno([v(*x) for x in pts], "ACCES-RELL")
        v.pl([tuple(x) for x in pts], capa, True)


def leyenda_colores(lam, xmm, ymm, items, titulo="COLORES DE LOS ELEMENTOS"):
    lam.texto(lam.P(xmm, ymm), titulo, 3.0, "TITULOS")
    for k, (rgb, txt) in enumerate(items):
        y = ymm - 9 - k * 7.5
        p = [lam.P(xmm, y - 2), lam.P(xmm + 14, y - 2), lam.P(xmm + 14, y + 2.6), lam.P(xmm, y + 2.6)]
        e = lam.msp.add_solid([p[0], p[1], p[3], p[2]], dxfattribs={"layer": "LEYENDA"}); e.rgb = rgb
        lam.poli(p, "LEYENDA", cerrada=True)
        lam.texto(lam.P(xmm + 17, y + 0.3), txt, 2.0, "LEYENDA", TA.MIDDLE_LEFT)


# ================================================================== DR-02 (1/20)
def dr02(doc, ox, oy, P):
    lam = B.Lamina(doc, ox, oy, 10, "DR-02", "ELEVACION DE CANALETA Y CORTE DEL MONTANTE PLUVIAL",
                   "CANALETA EN EL ALERO, BOQUILLA, MONTANTE PVC 4\", FALSA COLUMNA, DADO Y SALIDA A LA CUNETA - " + P["nombre"])
    f = lam.f
    # ---------------- H. elevacion frontal de la canaleta (vista desde afuera)
    Lc = 3.00; x0mm, y0mm = 490, 475
    v = V(lam, x0mm, y0mm)
    caida = Lc * S_CAN / 100
    za1 = AL0 + ALERO_E
    v.concreto([(-0.10, CH + 0.012), (Lc + 0.25, CH + 0.012), (Lc + 0.25, za1), (-0.10, za1)])
    v.ln((-0.10, AL0), (0.0, AL0), "CONCRETO-OCULTO"); v.ln((Lc, AL0), (Lc + 0.25, AL0), "CONCRETO")
    v.pl([(-0.10, za1 + 0.10), (Lc + 0.25, za1 + 0.07)], "COBERTURA", ancho=0.005)
    # canaleta con pendiente: fondo de y = caida (izquierda, extremo alto) a 0 (derecha, boquilla)
    v.pl([(0, caida), (Lc, 0), (Lc, CH), (0, CH + caida), (0, caida)], "PLANCHA-GALV", ancho=0.004)
    n = int(Lc / SEP_SOP) + 1
    for k in range(n):
        x = k * SEP_SOP; yb = caida * (1 - x / Lc)
        v.pl([(x, yb - EPL), (x, yb + CH)], "PLATINA", ancho=ANP)
    v.pl([(Lc - 0.15 - DB / 2, 0), (Lc - 0.15 - DB / 2, -0.15)], "PLANCHA-GALV"); v.pl([(Lc - 0.15 + DB / 2, 0), (Lc - 0.15 + DB / 2, -0.15)], "PLANCHA-GALV")
    xm = Lc - 0.15
    for s in (-1, 1): v.pl([(xm + s * DT / 2, -0.06), (xm + s * DT / 2, -0.55)], "TUBERIA-PVC", ancho=0.004)
    v.ln((xm - 0.10, -0.55), (xm + 0.10, -0.55), "CORTES")
    for x in (2 * SEP_SOP, 3 * SEP_SOP):
        v.cota((x, CH + caida * (1 - x / Lc)), (x + SEP_SOP, CH + caida * (1 - (x + SEP_SOP) / Lc)), 30, True, "0.60")
    v.cota((0, -0.08), (Lc, -0.08), -6, True, "L = variable (se muestra 3.00 m)")
    lam.flecha(v(0.9, CH / 2 + 0.02), v(2.1, CH / 2 + 0.008), "FLUJO", 3.0)
    lam.texto(v(1.5, CH / 2 + 0.05), "S = %.2f %%" % S_CAN, 2.4, "TEXTOS", TA.MIDDLE_CENTER)
    items = [(v(0.0, 0)[0], v(0, CH / 2)[1], ["Tapa lateral (extremo alto)"], None),
             (v(0.6, 0)[0], v(0, 0.02)[1], ["Soporte platina F°G° @0.60"], None),
             (v(xm, 0)[0], v(0, -0.30)[1], ["Boquilla y montante PVC 4\" (corte I)"], None)]
    lam.franja(items, v(0, -0.62)[1], abajo=True, hmm=2.0, xmin_mm=440, xmax_mm=828)
    lam.texto(v(-0.08, za1 + 0.125), "Cobertura de aluzinc TR4 e = 0.40 mm", 2.0, "TEXTOS")
    lam.texto(v(Lc / 2, (CH + za1) / 2 + 0.006), "ALERO O VIGA DE BORDE DE CONCRETO (SEGUN ESTRUCTURAS)", 2.0, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(x0mm + Lc / f / 2, y0mm + 80, "H. ELEVACION FRONTAL DE LA CANALETA", "ESC. 1/10 - vista desde afuera", 120)

    # ---------------- I. corte del montante (alero, desvio, bajada, falsa columna, dado, salida)
    x0mm, y0mm = 75, 95
    v = V(lam, x0mm, y0mm)
    g = ruta(); r = DT / 2; R = g["R"]; cp = g["camp"]
    z_al, xa, xt, ycu, zc, zc1, zs, yb = g["z_al"], g["xa"], g["yt"], g["ycu"], g["zc"], g["zc1"], g["zs"], g["yb"]
    v.pl([(-0.25, -0.40), (-0.25, z_al + ALERO_E)], "MURO"); v.pl([(0.0, 0.0), (0.0, z_al)], "MURO")
    lam.texto(v(-0.125, 1.9), "MURO", 2.2, "TEXTOS", TA.MIDDLE_CENTER)
    v.concreto([(-0.25, z_al), (xa, z_al), (xa, z_al + ALERO_E), (-0.25, z_al + ALERO_E)])
    v.pl([(-0.40, z_al + ALERO_E + 0.14), (xa + 0.13, z_al + ALERO_E + 0.06)], "COBERTURA", ancho=0.01)
    v.ln((-0.30, 0.0), (ycu + 0.85, 0.0), "TERRENO")
    lam.nivel(v(ycu + 0.75, 0.0), 0.0, "NPT +0.00", 1)
    # canaleta y soporte en la cara del alero
    xi = xa + EPL; xo = xi + CB
    lam.relleno([v(xi, zc), v(xo, zc), v(xo, zc + CH), v(xi, zc + CH)], "GALV-RELL")
    v.pl([(xi, zc + CH + PEST), (xi, zc), (xo, zc), (xo, zc + CH), (xo - PEST, zc + CH)], "PLANCHA-GALV", ancho=0.006)
    v.pl([(xa + EPL / 2, zc + CH + OREJA), (xa + EPL / 2, zc), (xo + EPL / 2, zc), (xo + EPL / 2, zc + CH)], "PLATINA", ancho=0.006)
    # boquilla: cuello de plancha que entra en el montante
    for sx in (-1, 1): v.ln((yb + sx * DB / 2, zc), (yb + sx * DB / 2, zc - 0.15), "PLANCHA-GALV")
    # montante: tubos (celeste) y codos con campanas (azul)
    tubo2d(v, (yb, g["ztop"]), (yb, zc1 + R + cp))
    codo2d(v, (yb, zc1), (0, -1), (-1, 0), R, r)
    tubo2d(v, (yb - R - cp, zc1), (xt + R + cp, zc1))
    codo2d(v, (xt, zc1), (-1, 0), (0, -1), R, r)
    tubo2d(v, (xt, zc1 - R - cp), (xt, FC[2]))
    tubo2d(v, (xt, FC[2]), (xt, zs + R + cp), oculto=True)
    codo2d(v, (xt, zs), (0, -1), (1, 0), R, r, oculto=True)
    tubo2d(v, (xt + R + cp, zs), (xt + DADO[0] / 2, zs), oculto=True)
    tubo2d(v, (xt + DADO[0] / 2, zs), (ycu + 0.05, zs))
    # colgadores: anclaje en el alero, varilla roscada, tuerca y banda alrededor del tubo
    for y in g["colg"]:
        v.rect(y - 0.008, z_al, y + 0.008, z_al + 0.04, "COLGADOR")
        v.pl([(y, zc1 + r + 0.008), (y, z_al)], "COLGADOR", ancho=0.0095)
        v.rect(y - 0.0072, zc1 + r + 0.008, y + 0.0072, zc1 + r + 0.016, "COLGADOR")
        lam.relleno([v(y - 0.015, zc1 - r - 0.006), v(y + 0.015, zc1 - r - 0.006), v(y + 0.015, zc1 + r + 0.008), v(y - 0.015, zc1 + r + 0.008)], "COLG-RELL")
        v.rect(y - 0.015, zc1 - r - 0.006, y + 0.015, zc1 + r + 0.008, "COLGADOR")
    # falsa columna y dado
    v.concreto([(0.0, 0.0), (FC[1], 0.0), (FC[1], FC[2]), (0.0, FC[2])])
    v.concreto([(xt - DADO[0] / 2, -DADO[2]), (xt + DADO[0] / 2, -DADO[2]), (xt + DADO[0] / 2, 0.0), (xt - DADO[0] / 2, 0.0)])
    # abrazaderas: banda alrededor del tubo, oreja contra el muro y tirafon
    for z in g["abr"]:
        lam.relleno([v(0.0, z - ANP / 2), v(xt + r + 0.004, z - ANP / 2), v(xt + r + 0.004, z + ANP / 2), v(0.0, z + ANP / 2)], "ABRZ-RELL")
        v.rect(0.0, z - ANP / 2, xt + r + 0.004, z + ANP / 2, "ABRAZADERA")
        v.rect(-0.05, z - 0.003, 0.0, z + 0.003, "PERNOS")
    # cuneta (referencia)
    v.pl([(ycu, 0.0), (ycu, -0.50), (ycu + 0.60, -0.50), (ycu + 0.60, 0.0)], "CUNETA"); v.pl([(ycu + 0.10, 0.0), (ycu + 0.10, -0.40), (ycu + 0.50, -0.40), (ycu + 0.50, 0.0)], "CUNETA")
    # cotas
    v.cota((0.0, z_al), (xa, z_al), 8, True)
    v.cota((0.0, 0.0), (0.0, FC[2]), -9, False); v.cota((xt - DADO[0] / 2, -DADO[2]), (xt - DADO[0] / 2, 0.0), -9, False)
    v.cota((xt + DADO[0] / 2, -DADO[2]), (xt - DADO[0] / 2, -DADO[2]), -6, True)
    v.cota((xt + r + 0.01, g["abr"][0]), (xt + r + 0.01, g["abr"][1]), 6, False, "<= 1.50")
    v.cota((xa + CB + 0.05, 0.0), (xa + CB + 0.05, z_al), 12, False, "variable (3.00 tipico)")
    lam.juntar_llamadas()
    xtx = v(ycu + 0.95, 0)[0]
    for (u, w), t in (((xa + 0.10, zc + 0.12), ["Canaleta %s con soporte @0.60 (ver DR-01, detalle A)" % SEC]),
                      ((yb + DB / 2, zc - 0.10), ["Boquilla Ø 0.10 dentro del montante PVC 4\""]),
                      ((g["colg"][0], z_al - 0.15), ["Colgador F°G°: anclaje 3/8\", varilla roscada 3/8\" y banda (uno junto a cada codo)"]),
                      ((yb - R * 0.3, zc1 - R * 0.3), ["Codo PVC 4\" x 90° con campanas (3 por montante)"]),
                      ((g["colg"][1] + 0.08, zc1 + r), ["Tubo PVC 4\" del desvio bajo el alero"]),
                      ((xt + r, g["abr"][1]), ["Abrazadera F°G° e = 1/8\" con tirafon y tarugo, @1.50 m (DR-01, F)"]),
                      ((xt + r, 1.80), ["Tubo PVC-U 4\" (montante) adosado al muro"]),
                      ((FC[1], 0.90), ["Falsa columna de concreto f'c = 175 kg/cm2 de 0.20 x 0.15 x 1.30 m"]),
                      ((xt + DADO[0] / 2, -0.12), ["Dado de concreto f'c = 140 kg/cm2 de 0.40 x 0.40 x 0.35 m con codo PVC 4\" x 90°"]),
                      ((ycu + 0.05, zs), ["Salida PVC 4\" hasta la cuneta (longitud segun metrado de montantes)"])):
        lam.llamada(v(u, w), (xtx, v(0, w)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(x0mm + 100, y0mm - 58, "I. CORTE DEL MONTANTE PLUVIAL TIPICO", "ESC. 1/10 - del alero a la cuneta", 130)
    leyenda_colores(lam, 470, 200, [((180, 214, 246), "Tubo PVC-U 4\" (montante, desvio y salida)"), ((60, 100, 190), "Codos PVC 4\" x 90° con campanas"),
                                    ((236, 150, 50), "Colgador F°G° (banda, varilla roscada y anclaje)"), ((214, 70, 70), "Abrazadera F°G° con tirafones"),
                                    ((226, 226, 226), "Concreto: alero, falsa columna y dado"), ((214, 220, 230), "Canaleta y soporte galvanizados")])
    lam.notas(470, 330, "NOTAS", [
        "1. Montante de tuberia PVC-U para desague 4\" (NTP 399.003), uniones con cemento solvente; 3 codos de 90° por montante (metrado).",
        "2. La longitud de cada montante es la de la hoja METRADO MONTANTES (6.16 a 11.00 m segun edificacion); el corte I es tipico.",
        "3. Abrazaderas @1.50 m como maximo; colgadores junto a cada codo del desvio (2 por montante en edificaciones).",
        "4. La falsa columna protege el tramo inferior del montante; el codo de salida queda dentro del dado.",
        "5. Altura del alero, vuelo y cobertura segun planos de arquitectura y estructuras de cada edificacion.",
    ], hmm=1.8, ancho_mm=350)
    return lam


# ================================================================== isometricos (DR-03, DR-04, DR-05)
GALV, PLAT, CAB, REM = (200, 207, 216), (146, 160, 178), (92, 94, 102), (120, 122, 128)
PVC, CONC, TAR, ROSCA, MURO_C = (180, 214, 246), (220, 220, 214), (238, 196, 112), (168, 170, 176), (232, 226, 214)
ACC, COLG, ABRZ, DADO_C = (60, 100, 190), (236, 150, 50), (214, 70, 70), (186, 186, 182)


def _llamadas(lam, P2, items, xt_mm, hmm=2.0):
    lam.juntar_llamadas()
    for p3, txt in items:
        q = P2(p3)
        lam.llamada(q, (lam.P(xt_mm, 0)[0], q[1]), txt, hmm)
    lam.volcar_llamadas()


def escena_canaleta(L=1.50):
    E = Escena(); s = S_CAN / 100.0
    z0 = lambda x: s * x                                    # sube hacia la tapa (x = L); la boquilla queda en el extremo bajo
    xi, xo = EPL, EPL + CB; Q = E.quad
    # alero o viga de borde (grupo 0: atras de todo)
    E.g = 0
    E.caja(-0.05, -0.20, AL0, L + 0.05, 0.0, AL0 + ALERO_E, CONC, paso=0.06)
    # canaleta (plancha 0.9 mm): fondo, lados y pestanas
    E.g = 2; Q((0, xi, z0(0)), (L, xi, z0(L)), (L, xi, z0(L) + CH + PEST), (0, xi, z0(0) + CH + PEST), GALV, 0.04)
    E.g = 3; Q((0, xi, z0(0)), (L, xi, z0(L)), (L, xo, z0(L)), (0, xo, z0(0)), GALV, 0.04)
    E.g = 4; Q((0, xo, z0(0)), (L, xo, z0(L)), (L, xo, z0(L) + CH), (0, xo, z0(0) + CH), GALV, 0.04)
    Q((0, xo - PEST, z0(0) + CH), (L, xo - PEST, z0(L) + CH), (L, xo, z0(L) + CH), (0, xo, z0(0) + CH), GALV, 0.04)
    # union de tramos (x = 1.10): borde del tramo de aguas abajo, 2 filas de remaches
    xu = 1.10
    for a, b in (((xu, xi, z0(xu)), (xu, xo, z0(xu))), ((xu, xo, z0(xu)), (xu, xo, z0(xu) + CH)), ((xu, xi, z0(xu)), (xu, xi, z0(xu) + CH + PEST))):
        E.cara([a, b], GALV, [True, False], sesgo=0.01, relleno=False)
    for xr in (xu - 0.0125, xu - 0.0375):
        E.g = 4
        for k in range(int(CH / 0.05)): E.disco((xr, xo + 0.0006, z0(xr) + 0.025 + 0.05 * k), (0, 1, 0), 0.0032, REM, sesgo=0.01)
        E.g = 3
        for k in range(int(CB / 0.05)): E.disco((xr, xi + 0.025 + 0.05 * k, z0(xr) + 0.0006), (0, 0, 1), 0.0032, REM, sesgo=0.01)
    # soportes de platina @0.60 con pernos y tornillos
    sops = [0.25, 0.85, 1.45]
    for xs in sops:
        z = z0(xs); w = ANP / 2
        E.g = 1
        E.caja(xs - w, 0.0, z - EPL, xs + w, EPL, z + CH + OREJA, PLAT, 0.03)
        E.caja(xs - w, 0.0, z - EPL, xs + w, xo + EPL, z, PLAT, 0.03)
        E.prisma_hex((xs, xi + CB / 2, z - EPL - 0.0006), (0, 0, -1), 0.0079, 0.0035, CAB)
        E.g = 5
        E.caja(xs - w, xo, z - EPL, xs + w, xo + EPL, z + CH + EPL, PLAT, 0.03)
        E.caja(xs - w, xo + EPL - OREJA, z + CH + 0.0009, xs + w, xo + EPL, z + CH + 0.0009 + EPL, PLAT, 0.03)
        for zp in (z + CH + 0.075, z + CH + 0.025):                    # pernos de expansion (cabeza hacia la canaleta)
            E.disco((xs, xi + 0.0012, zp), (0, 1, 0), 0.0085, CAB, sesgo=0.004)
            E.prisma_hex((xs, xi + 0.0016, zp), (0, 1, 0), 0.0111, 0.0043, CAB)
        E.disco((xs, xo - 0.025, z + CH + 0.0009 + EPL + 0.0004), (0, 0, 1), 0.0075, CAB, sesgo=0.004)
        E.prisma_hex((xs, xo - 0.025, z + CH + 0.0009 + EPL + 0.0006), (0, 0, 1), 0.0079, 0.0035, CAB)
    # tapa lateral en x = L con 6 remaches
    zL = z0(L); E.g = 6
    E.cara([(L + 0.0009, xi, zL), (L + 0.0009, xo, zL), (L + 0.0009, xo, zL + CH), (L + 0.0009, xo - PEST, zL + CH),
            (L + 0.0009, xi, zL + CH)], (226, 230, 236))
    E.cara([(L + 0.0009, xi, zL + CH), (L + 0.0009, xi + 0.02, zL + CH), (L + 0.0009, xi + 0.02, zL + CH + PEST), (L + 0.0009, xi, zL + CH + PEST)], (226, 230, 236))
    for zr in (0.08, 0.17): E.disco((L - 0.015, xo + 0.0006, zL + zr), (0, 1, 0), 0.0032, REM, sesgo=0.01)
    E.g = 1
    for yr in (0.06, 0.14): E.disco((L - 0.015, xi + yr, zL - 0.0006), (0, 0, -1), 0.0032, REM)
    # boquilla (extremo bajo): abertura, 8 remaches de la brida, cuello y montante
    xb, yb = 0.15, xi + CB / 2; zb = z0(xb); E.g = 3
    E.disco((xb, yb, zb + 0.0005), (0, 0, 1), DB / 2, (70, 74, 80), n=24, sesgo=0.02)
    for dx, dy in ((-0.08, -0.08), (0, -0.08), (0.08, -0.08), (-0.08, 0), (0.08, 0), (-0.08, 0.08), (0, 0.08), (0.08, 0.08)):
        E.disco((xb + dx, yb + dy, zb + 0.0006), (0, 0, 1), 0.0032, REM, sesgo=0.02)
    E.g = 1
    Q((xb - 0.10, yb - 0.10, zb - 0.0012), (xb + 0.10, yb - 0.10, zb - 0.0012), (xb + 0.10, yb + 0.10, zb - 0.0012), (xb - 0.10, yb + 0.10, zb - 0.0012), GALV, 0.05)
    E.cilindro((xb, yb, zb - 0.0012), (xb, yb, zb - 0.15), DB / 2, GALV, n=24, tapas=False, paso=0.05)
    E.cilindro((xb, yb, zb - 0.06), (xb, yb, zb - 0.50), DT / 2, PVC, n=24, tapas=True, paso=0.06)
    return E, dict(xi=xi, xo=xo, z0=z0, sops=sops, xu=xu, xb=xb, yb=yb, L=L)


def dr03(doc, ox, oy, P):
    lam = B.Lamina(doc, ox, oy, 5, "DR-03", "ISOMETRICO DE CANALETA, SOPORTES, PERNOS, TAPA Y BOQUILLA",
                   "TRAMO TIPICO DE 1.50 m CON TODAS SUS FIJACIONES SEGUN EL ACU - " + P["nombre"])
    E, g = escena_canaleta()
    xmm, ymm = 250, 330
    P2 = E.dibujar(lam, xmm, ymm)
    z0, xi, xo = g["z0"], g["xi"], g["xo"]; xs = g["sops"][1]; xs2 = g["sops"][2]; L = g["L"]
    items = [((0.60, -0.10, 0.30), ["Alero o viga de borde de concreto (segun estructuras)"]),
             ((xs2, 0.0, z0(xs2) + CH + OREJA), ["Oreja interior del soporte (0.10) contra el alero"]),
             ((xs, xi + 0.004, z0(xs) + CH + 0.075), ["2 pernos de expansion 1/4\" x 2 1/2\" con tarugo por soporte (ACU)"]),
             ((xs, xo - 0.025, z0(xs) + CH + 0.006), ["Tornillo autorroscante 1/4\" x 3/4\" en la oreja exterior",
                                                      "(2 por soporte: oreja y fondo, ACU)"]),
             ((xs, xo + EPL, z0(xs) + 0.10), ["Soporte de platina F°G° 1\" x 1/8\" @0.60 (desarrollo %.2f m)" % DES_SOP]),
             ((g["xu"] - 0.025, xo, z0(g["xu"]) + 0.10), ["Union de tramos cada 2.44 m: traslape 0.05, 2 filas de remaches",
                                                         "pop 1/8\" @0.05 (%d por union) y sellador de poliuretano" % REM_UNION]),
             ((0.70, xo, z0(0.70) + 0.12), ["Canaleta de plancha galvanizada e = 0.9 mm, %s (ancho x alto), S = 1 %%" % SEC]),
             ((L, xi + 0.15, z0(L) + 0.10), ["Tapa lateral con pestana 0.03: 6 remaches pop 1/8\" y sellador (ACU)"]),
             ((g["xb"] + 0.08, g["yb"] + 0.08, z0(g["xb"])), ["Boquilla: brida 0.20 x 0.20 con 8 remaches pop 1/8\" y sellador"]),
             ((g["xb"] + DT / 2, g["yb"], z0(g["xb"]) - 0.30), ["Cuello Ø 4\" x 0.15 dentro del montante PVC 4\""])]
    _llamadas(lam, P2, items, 590)
    lam.titulo_vista(330, 70, "ISOMETRICO DEL TRAMO TIPICO DE CANALETA", "ESC. 1/5 - la cobertura TR4 no se dibuja para ver el interior", 160)
    lam.notas(40, 560, "LECTURA DEL ISOMETRICO", [
        "Se mira desde afuera y desde arriba. La canaleta baja hacia la boquilla con S = 1 % (memoria hidrologica).",
        "Las fijaciones se dibujan a su medida real: cabeza hexagonal de perno 7/16\" (11 mm), tornillo 5/16\" (8 mm), remache 1/8\".",
        "Cantidades por unidad y totales del proyecto en la lamina DR-05.",
    ], hmm=1.8, ancho_mm=330)
    return lam


def tubo3d(E, a, b, g=None):
    if g is not None: E.g = g
    E.cilindro(a, b, DT / 2, PVC, n=20, paso=0.10)


def colgador3d(E, y, zt, z_al, x=0.0, eje_tubo="y"):
    """Colgador sobre un tubo horizontal (eje del tubo en z = zt): anclaje, varilla roscada, tuercas y banda."""
    r = DT / 2
    E.cilindro((x, y, z_al), (x, y, z_al + 0.04), 0.008, ROSCA, n=10)                                  # anclaje de expansion
    E.cilindro((x, y, zt + r + 0.008), (x, y, z_al), 0.0048, ROSCA, n=8, paso=0.08, anillos=0.004)    # varilla roscada 3/8"
    E.prisma_hex((x, y, zt + r + 0.008), (0, 0, 1), 0.0143, 0.008, CAB)                                # tuerca
    E.prisma_hex((x, y, zt + r + 0.020), (0, 0, 1), 0.0143, 0.008, CAB)                                # contratuerca
    if eje_tubo == "y": E.cilindro((x, y - 0.015, zt), (x, y + 0.015, zt), r + 0.006, COLG, n=20, tapas=False)
    else: E.cilindro((x - 0.015, y, zt), (x + 0.015, y, zt), r + 0.006, COLG, n=20, tapas=False)
    E.caja(x - 0.006, y - 0.015, zt + r + 0.002, x + 0.006, y + 0.015, zt + r + 0.010, COLG, 0.05)    # oreja de la banda


def abrazadera3d(E, z, yt, x=0.0):
    """Abrazadera de platina F°G° e = 1/8" sobre tubo vertical en (x, yt): anillo, patas, orejas en el muro y 2 tirafones."""
    r = DT / 2; h = ANP / 2
    E.cilindro((x, yt, z - h), (x, yt, z + h), r + 0.004, ABRZ, n=20, tapas=False)
    for s in (-1, 1):
        x1, x2 = sorted((x + s * (r + 0.004), x + s * (r + 0.004 + EPL)))
        E.caja(x1, EPL, z - h, x2, yt, z + h, ABRZ, 0.05)
        x3, x4 = sorted((x + s * (r + 0.004), x + s * (r + 0.05)))
        E.caja(x3, 0.0, z - h, x4, EPL, z + h, ABRZ, 0.05)
        E.prisma_hex((x + s * (r + 0.028), EPL, z), (0, 1, 0), 0.0111, 0.0043, CAB)


def escena_montante():
    E = Escena(); g = ruta(); r = DT / 2; R, cp = g["R"], g["camp"]
    z_al, xa, yi, yo, zc, yb, zc1, yt, zs, ycu = (g[k] for k in ("z_al", "xa", "yi", "yo", "zc", "yb", "zc1", "yt", "zs", "ycu"))
    X0, X1 = -0.45, 0.55
    E.g = 0; E.caja(X0, -0.15, 0.0, X1, 0.0, z_al, MURO_C, paso=0.25)                        # muro
    E.g = 1; E.caja(X0, -0.15, z_al, X1, xa, z_al + ALERO_E, CONC, paso=0.20)                 # alero
    E.quad((X0, 0.0, 0.0), (X1, 0.0, 0.0), (X1, ycu + 0.75, 0.0), (X0, ycu + 0.75, 0.0), (0, 0, 0), 3.0, relleno=False)
    # canaleta y soportes
    Q = E.quad; E.g = 3; ca, cb = -0.45, 0.13          # extremo con tapa junto a la boquilla: deja ver el desvio
    Q((ca, yi, zc), (cb, yi, zc), (cb, yi, zc + CH + PEST), (ca, yi, zc + CH + PEST), GALV, 0.08)
    Q((ca, yi, zc), (cb, yi, zc), (cb, yo, zc), (ca, yo, zc), GALV, 0.08)
    Q((ca, yo, zc), (cb, yo, zc), (cb, yo, zc + CH), (ca, yo, zc + CH), GALV, 0.08)
    E.cara([(cb, yi, zc), (cb, yo, zc), (cb, yo, zc + CH), (cb, yi, zc + CH)], (226, 230, 236))
    for xs in (-0.30,):
        E.caja(xs - ANP / 2, xa, zc - EPL, xs + ANP / 2, yo + EPL, zc, PLAT, 0.05)
        E.caja(xs - ANP / 2, yo, zc - EPL, xs + ANP / 2, yo + EPL, zc + CH, PLAT, 0.05)
    # montante: tubos celestes, codos azules con campanas
    E.g = 2
    E.cilindro((0, yb, zc), (0, yb, zc - 0.15), DB / 2, GALV, n=18, tapas=False)               # cuello de la boquilla
    tubo3d(E, (0, yb, g["ztop"]), (0, yb, zc1 + R + cp))
    E.codo((0, yb, zc1), (0, 0, -1), (0, -1, 0), R, r, ACC)
    tubo3d(E, (0, yb - R - cp, zc1), (0, yt + R + cp, zc1))
    E.codo((0, yt, zc1), (0, -1, 0), (0, 0, -1), R, r, ACC)
    for y in g["colg"]: colgador3d(E, y, zc1, z_al)
    tubo3d(E, (0, yt, FC[2]), (0, yt, zs + R + cp))
    E.codo((0, yt, zs), (0, 0, -1), (0, 1, 0), R, r, ACC)
    tubo3d(E, (0, yt + R + cp, zs), (0, yt + DADO[1] / 2, zs))
    E.g = 4
    tubo3d(E, (0, yt, zc1 - R - cp), (0, yt, FC[2]))
    tubo3d(E, (0, yt + DADO[1] / 2, zs), (0, ycu, zs))
    E.g = 5
    for z in g["abr"]: abrazadera3d(E, z, yt)
    # falsa columna, dado y cuneta
    E.g = 3
    E.caja(-FC[0] / 2, 0.0, 0.0, FC[0] / 2, FC[1], FC[2], CONC, paso=0.12)
    E.caja(-DADO[0] / 2, yt - DADO[1] / 2, -DADO[2], DADO[0] / 2, yt + DADO[1] / 2, 0.0, DADO_C, paso=0.12)
    E.caja(X0, ycu, -0.50, X1, ycu + 0.60, -0.40, CONC, paso=0.15)
    E.caja(X0, ycu, -0.40, X1, ycu + 0.10, 0.0, CONC, paso=0.15)
    E.caja(X0, ycu + 0.50, -0.40, X1, ycu + 0.60, 0.0, CONC, paso=0.15)
    return E, g


LEY_MONT = [(PVC, "Tubo PVC-U 4\" (montante, desvio y salida)"), (ACC, "Codos PVC 4\" x 90° con campanas"),
            (COLG, "Colgador F°G°: banda, varilla roscada 3/8\" y anclaje"), (ABRZ, "Abrazadera F°G° e = 1/8\" con tirafones"),
            (CONC, "Concreto: alero, falsa columna y cuneta"), (DADO_C, "Dado de concreto f'c = 140 kg/cm2"),
            (GALV, "Canaleta galvanizada"), (PLAT, "Soporte de platina F°G°")]


def dr04(doc, ox, oy, P):
    lam = B.Lamina(doc, ox, oy, 15, "DR-04", "ISOMETRICO DEL MONTANTE PLUVIAL TIPICO",
                   "CANALETA, BOQUILLA, CODOS, DESVIO CON COLGADORES, ABRAZADERAS, FALSA COLUMNA, DADO Y SALIDA - " + P["nombre"])
    E, g = escena_montante()
    P2 = E.dibujar(lam, 215, 200)
    items = [((0.10, -0.075, g["z_al"] + ALERO_E), ["Alero o viga de borde de concreto"]),
             ((-0.20, g["yo"], g["zc"] + 0.12), ["Canaleta %s con soportes @0.60 y tapa en el extremo (DR-03)" % SEC]),
             ((0.0, g["yb"] + DT / 2, g["zc1"] + 0.20), ["Boquilla y tubo PVC 4\""]),
             ((0.0, g["colg"][0], g["zc1"] + 0.25), ["Colgador F°G° con varilla roscada 3/8\" y banda (DR-06)"]),
             ((0.0, g["yb"] - g["R"] * 0.3, g["zc1"] - g["R"] * 0.7), ["Codo PVC 4\" x 90° con campanas (3 por montante)"]),
             ((0.09, EPL + 0.004, g["abr"][1]), ["Abrazadera F°G° con 2 tirafones, @1.50 m (DR-06)"]),
             ((0.0, g["yt"] + DT / 2, 1.75), ["Montante PVC-U 4\" adosado al muro"]),
             ((FC[0] / 2, FC[1], 0.80), ["Falsa columna 0.20 x 0.15 x 1.30, f'c = 175 kg/cm2"]),
             ((DADO[0] / 2, g["yt"] + DADO[1] / 2, -0.15), ["Dado 0.40 x 0.40 x 0.35, f'c = 140 kg/cm2, con codo de salida"]),
             ((0.0, 0.70, g["zs"] + DT / 2), ["Salida PVC 4\" hasta la cuneta (terreno no dibujado)"]),
             ((0.45, g["ycu"] + 0.30, 0.0), ["Cuneta de concreto (referencia)"])]
    _llamadas(lam, P2, items, 330)
    lam.titulo_vista(250, 45, "ISOMETRICO DEL MONTANTE PLUVIAL TIPICO", "ESC. 1/15 - del alero a la cuneta", 150)
    leyenda_colores(lam, 560, 300, LEY_MONT)
    lam.notas(560, 520, "NOTAS", [
        "1. Tramo tipico: la longitud de cada montante y su salida es la de la hoja METRADO MONTANTES.",
        "2. 3 codos PVC 4\" x 90 grados por montante; 2 colgadores en el desvio; abrazaderas @1.50 m.",
        "3. El alero se dibuja macizo; el terreno no se dibuja para ver el dado y la salida.",
    ], hmm=1.8, ancho_mm=250)
    return lam


def dr06(doc, ox, oy, P):
    lam = B.Lamina(doc, ox, oy, 5, "DR-06", "DETALLES 3D DE LOS ELEMENTOS DEL MONTANTE",
                   "CODO CON CAMPANAS, COLGADOR, ABRAZADERA, BOQUILLA Y DADO CON CODO DE SALIDA - " + P["nombre"])
    r = DT / 2; R, cp = 0.10, 0.05; yt = FC[1] / 2
    # 1. codo 90° con campanas
    E = Escena(); E.g = 2
    tubo3d(E, (0, 0, 0.30), (0, 0, R + cp)); E.codo((0, 0, 0), (0, 0, -1), (0, 1, 0), R, r, ACC); tubo3d(E, (0, R + cp, 0), (0, 0.32, 0))
    P2 = E.dibujar(lam, 100, 420)
    _llamadas(lam, P2, [((0, 0, 0.22), ["Tubo PVC-U 4\" (Ø ext. 0.114)"]), ((0, -0.03, R + 0.02), ["Campana: el tubo entra 0.05 con cemento solvente"]),
                        ((0, 0.04, -0.06), ["Codo PVC-U 4\" x 90° (NTP 399.003)"])], 175)
    lam.titulo_vista(130, 330, "1. CODO PVC 4\" x 90° CON CAMPANAS", "ESC. 1/5", 100)
    # 2. colgador montado en el desvio, bajo el alero
    E = Escena(); E.g = 0
    E.caja(-0.15, -0.15, 0.32, 0.15, 0.15, 0.40, CONC, paso=0.1, relleno=False)
    E.g = 2; tubo3d(E, (0, -0.22, 0), (0, 0.22, 0)); colgador3d(E, 0.0, 0.0, 0.32)
    P2 = E.dibujar(lam, 370, 410)
    _llamadas(lam, P2, [((0, 0, 0.35), ["Anclaje de expansion 3/8\" en el fondo del alero"]), ((0, 0, 0.22), ["Varilla roscada F°G° 3/8\""]),
                        ((0, 0, r + 0.02), ["Tuerca, contratuerca y oreja de la banda"]), ((0, 0.015, -r - 0.006), ["Banda F°G° alrededor del tubo PVC 4\""])], 445)
    lam.titulo_vista(400, 330, "2. COLGADOR F°G° (DESVIO BAJO EL ALERO)", "ESC. 1/5 - uno junto a cada codo", 110)
    # 3. abrazadera en el muro
    E = Escena(); E.g = 0; E.caja(-0.16, -0.10, 0.0, 0.16, 0.0, 0.42, MURO_C, paso=0.1)
    E.g = 2; tubo3d(E, (0, yt, 0.0), (0, yt, 0.42)); E.g = 5; abrazadera3d(E, 0.21, yt)
    P2 = E.dibujar(lam, 625, 410)
    _llamadas(lam, P2, [((0, yt + r, 0.33), ["Montante PVC-U 4\" adosado al muro"]),
                        ((0, yt + r + 0.004, 0.21), ["Anillo de platina F°G° e = 1/8\" (Ø int. 1/4\" mayor)"]),
                        ((r + 0.028, EPL, 0.21), ["Oreja con tirafon 2\" x 1/4\" en tarugo 2\" x 1/2\""])], 700)
    lam.titulo_vista(650, 330, "3. ABRAZADERA F°G° EN EL MURO", "ESC. 1/5 - @1.50 m como maximo", 110)
    # 4. boquilla en el montante
    E = Escena(); E.g = 3
    E.quad((-0.15, 0, 0), (0.15, 0, 0), (0.15, CB, 0), (-0.15, CB, 0), GALV, 0.04)
    E.quad((-0.15, 0, 0), (0.15, 0, 0), (0.15, 0, CH), (-0.15, 0, CH), GALV, 0.04)
    E.disco((0, CB / 2, 0.0005), (0, 0, 1), DB / 2, (70, 74, 80), n=24, sesgo=0.02)
    for dx, dy in ((-0.08, -0.08), (0, -0.08), (0.08, -0.08), (-0.08, 0), (0.08, 0), (-0.08, 0.08), (0, 0.08), (0.08, 0.08)):
        E.disco((dx, CB / 2 + dy * 0.9, 0.0006), (0, 0, 1), 0.0032, REM, sesgo=0.02)
    E.g = 1
    E.cilindro((0, CB / 2, 0), (0, CB / 2, -0.15), DB / 2, GALV, n=24, tapas=False)
    E.cilindro((0, CB / 2, -0.06), (0, CB / 2, -0.02), r + 0.007, ACC, n=24, tapas=False)
    tubo3d(E, (0, CB / 2, -0.06), (0, CB / 2, -0.32))
    P2 = E.dibujar(lam, 110, 210)
    _llamadas(lam, P2, [((0.10, CB / 2, 0.0), ["Fondo de la canaleta con brida 0.20 x 0.20 y 8 remaches"]),
                        ((0, CB / 2 + DB / 2, -0.04), ["Cuello Ø 0.10 x 0.15 dentro de la campana del montante"]),
                        ((0, CB / 2 + r, -0.25), ["Montante PVC-U 4\""])], 190)
    lam.titulo_vista(140, 105, "4. BOQUILLA A MONTANTE", "ESC. 1/5", 90)
    # 5. dado con codo de salida (concreto transparente)
    E = Escena(); E.g = 1
    E.caja(-FC[0] / 2, 0.0, 0.0, FC[0] / 2, FC[1], 0.35, CONC, paso=0.1, relleno=False)
    E.caja(-DADO[0] / 2, yt - DADO[1] / 2, -DADO[2], DADO[0] / 2, yt + DADO[1] / 2, 0.0, DADO_C, paso=0.1, relleno=False)
    E.g = 2
    tubo3d(E, (0, yt, 0.35), (0, yt, -0.20 + R + cp)); E.codo((0, yt, -0.20), (0, 0, -1), (0, 1, 0), R, r, ACC)
    tubo3d(E, (0, yt + R + cp, -0.20), (0, yt + 0.55, -0.20))
    P2 = E.dibujar(lam, 400, 200)
    _llamadas(lam, P2, [((FC[0] / 2, FC[1], 0.25), ["Falsa columna 0.20 x 0.15 (base, transparente)"]),
                        ((0, yt, 0.10), ["Montante PVC 4\" dentro de la falsa columna"]),
                        ((DADO[0] / 2, yt + DADO[1] / 2, -0.10), ["Dado 0.40 x 0.40 x 0.35 f'c = 140 kg/cm2"]),
                        ((0, yt + 0.02, -0.20 - r), ["Codo PVC 4\" x 90° dentro del dado"]),
                        ((0, yt + 0.45, -0.20 + r), ["Salida PVC 4\" hacia la cuneta"])], 500)
    lam.titulo_vista(430, 75, "5. DADO CON CODO DE SALIDA", "ESC. 1/5 - concreto dibujado transparente", 110)
    leyenda_colores(lam, 650, 280, LEY_MONT[:6])
    return lam


def _perno_exp(E, c):
    x, y, z = c
    E.cilindro((x, y, z), (x, y, z + 0.0635), 0.003175, ROSCA, n=12, paso=0.02, anillos=0.00127 * 2)
    E.cilindro((x, y, z), (x, y, z + 0.040), 0.0050, TAR, n=14, paso=0.02, anillos=0.005)
    E.disco((x, y, z + 0.0635), (0, 0, 1), 0.008, CAB); E.prisma_hex((x, y, z + 0.0637), (0, 0, 1), 0.0111, 0.0043, CAB)


def dr05(doc, ox, oy, P, met):
    lam = B.Lamina(doc, ox, oy, 1, "DR-05", "FIJACIONES DE LA RED DE TECHO: ISOMETRICOS Y CANTIDADES",
                   "PERNOS, TORNILLOS, REMACHES, TIRAFONES, VARILLA ROSCADA Y ANCLAJES SEGUN EL ACU - " + P["nombre"], escala_txt="1/1")
    piezas = []
    E = Escena(); _perno_exp(E, (0, 0, 0)); piezas.append((E, 70, 430, "1. PERNO DE EXPANSION 1/4\" x 2 1/2\" CON TARUGO",
                                                       ["Soporte de canaleta: 2 por soporte (ACU)", "cabeza hexagonal 7/16\", arandela, camisa 40 mm"]))
    E = Escena()
    E.cilindro((0, 0, 0.003), (0, 0, 0.019), 0.003175, ROSCA, n=12, paso=0.01, anillos=0.0018)
    E.cilindro((0, 0, 0.0), (0, 0, 0.003), 0.0016, ROSCA, n=10)
    E.disco((0, 0, 0.019), (0, 0, 1), 0.006, CAB); E.prisma_hex((0, 0, 0.0192), (0, 0, 1), 0.0079, 0.0035, CAB)
    piezas.append((E, 270, 430, "2. TORNILLO AUTORROSCANTE 1/4\" x 3/4\"", ["Soporte a canaleta: 2 por soporte (oreja y fondo)", "cabeza hexagonal 5/16\" con arandela"]))
    E = Escena()
    E.cilindro((0, 0, 0), (0, 0, 0.010), 0.0016, (190, 192, 198), n=12); E.disco((0, 0, 0.010), (0, 0, 1), 0.0032, REM)
    E.cilindro((0, 0, 0.010), (0, 0, 0.035), 0.0009, ROSCA, n=8); E.cilindro((0, 0, -0.002), (0, 0, 0.0), 0.0013, ROSCA, n=8)
    piezas.append((E, 450, 430, "3. REMACHE POP 1/8\" (ANTES DE REMACHAR)", ["Uniones %d c/u (seccion %s), tapa 6, boquilla 8" % (REM_UNION, SEC), "cuerpo 3.2 x 10 mm, cabeza 6.4 mm, mandril"]))
    E = Escena()
    E.cilindro((0, 0, 0), (0, 0, 0.0508), 0.003175, ROSCA, n=12, paso=0.02, anillos=0.0025)
    E.prisma_hex((0, 0, 0.0508), (0, 0, 1), 0.0111, 0.0043, CAB)
    E.cilindro((0.03, 0, 0), (0.03, 0, 0.0508), 0.00635, TAR, n=14, paso=0.02, anillos=0.004)
    piezas.append((E, 640, 430, "4. TIRAFON 2\" x 1/4\" Y TARUGO 2\" x 1/2\"", ["Abrazadera del montante: 2 por abrazadera", "tarugo plastico con estrias (al lado)"]))
    E = Escena()
    E.cilindro((0, 0, 0), (0, 0, 0.12), 0.00476, ROSCA, n=12, paso=0.03, anillos=0.0016)
    for zz in (0.010, 0.020): E.prisma_hex((0, 0, zz), (0, 0, 1), 0.0143, 0.0080, CAB)
    E.disco((0, 0, 0.0098), (0, 0, 1), 0.0105, CAB)
    E.cilindro((0, 0, 0.085), (0, 0, 0.125), 0.008, ROSCA, n=14, paso=0.02, anillos=0.006)
    piezas.append((E, 90, 190, "5. COLGADOR: VARILLA ROSCADA 3/8\" Y ANCLAJE 3/8\"", ["Tuerca, contratuerca y arandela abajo;", "anclaje de expansion arriba (fondo del alero)"]))
    E = Escena(); E.caja(0, 0, 0, 0.06, ANP, EPL, PLAT, 0.01)
    E.cilindro((0.02, ANP / 2, -0.0005), (0.02, ANP / 2, EPL + 0.0005), 0.004, (60, 62, 66), n=12)
    piezas.append((E, 270, 262, "6. PLATINA F°G° 1\" x 1/8\" (SOPORTE Y ABRAZADERA)", ["25.4 x 3.18 mm, 0.633 kg/m", "perforacion 5/16\" para el perno"]))
    for E, x, y, tit, sub in piezas:
        E.dibujar(lam, x, y)
        yt = y - 28 if not tit.startswith("6.") else y - 68          # la platina se extiende hacia abajo: titulo debajo
        lam.texto(lam.P(x - 30, yt), tit, 2.4, "TITULOS")
        for k, t in enumerate(sub): lam.texto(lam.P(x - 30, yt - 6 - 5 * k), t, 1.8, "TEXTOS")
    # cantidades: por unidad (ACU) y total del proyecto con el metrado de la planilla
    M = {}
    for c, d, u, m in met:
        du = d.upper()
        for k in ("CANALETA", "SOPORTE", "TAPA LATERAL", "BOQUILLA", "COLGADOR", "ABRAZADERA"):
            if du.startswith(k) or (k in ("COLGADOR", "ABRAZADERA") and k in du): M[k] = m
    can, sop, tap, boq = M.get("CANALETA", 0), M.get("SOPORTE", 0), M.get("TAPA LATERAL", 0), M.get("BOQUILLA", 0)
    col, abz = M.get("COLGADOR", 0), M.get("ABRAZADERA", 0)
    rem_can = can * 2 * (CB + 2 * CH) / 0.05 / 2.44
    sell = can * (CB + 2 * CH) / 2.44 / 8 + tap * 0.65 / 8 + boq * 1.12 / 8
    filas = [("Perno de expansion 1/4\" x 2 1/2\" c/tarugo", "soporte", "2", "%d sop." % sop, "%d" % (2 * sop)),
             ("Tornillo autorroscante 1/4\" x 3/4\"", "soporte", "2", "%d sop." % sop, "%d" % (2 * sop)),
             ("Remache pop 1/8\" (uniones de canaleta)", "m de canaleta", "%.2f" % (REM_UNION / 2.44), "%.2f m" % can, "%d" % math.ceil(rem_can)),
             ("Remache pop 1/8\" (tapas laterales)", "tapa", "6", "%d tapas" % tap, "%d" % (6 * tap)),
             ("Remache pop 1/8\" (boquillas)", "boquilla", "8", "%d boq." % boq, "%d" % (8 * boq)),
             ("Sellador de poliuretano, cartucho 300 ml", "uniones, tapas, boquillas", "ver ACU", "-", "%.1f" % sell),
             ("Tirafon 2\" x 1/4\" + tarugo 2\" x 1/2\"", "abrazadera", "2", "%d abr." % abz, "%d" % (2 * abz)),
             ("Varilla roscada 3/8\" + anclaje + 2 tuercas + arandela", "colgador", "1 juego", "%d col." % col, "%d" % col)]
    yb = lam.tabla(430, 290, ["FIJACION", "POR", "CANT./UND", "METRADO", "TOTAL"], filas, [95, 42, 20, 26, 20], hmm=1.8, alto_mm=5.6,
                   titulo="FIJACIONES POR UNIDAD (ACU) Y TOTAL DEL PROYECTO")
    lam.notas(430, yb - 6, "NOTAS", [
        "1. Cantidades por unidad del ACU CANALETAS; remaches de union con la seccion 0.20 x 0.25: %d por union cada 2.44 m (el ACU tiene 26, de la seccion 0.25 x 0.20)." % REM_UNION,
        "2. Abrazadera y colgador segun el detalle del plano de drenaje y la especificacion tecnica (no tienen ACU propio en la planilla).",
        "3. Totales = cantidad por unidad x metrado de la planilla; el sellador se da en cartuchos de 300 ml (8 m de cordon de 6 mm).",
        "4. Todas las piezas metalicas galvanizadas; cortes y perforaciones con pintura rica en zinc.",
    ], hmm=1.7, ancho_mm=200)
    return lam


def construir(clave):
    P = PROY[clave]
    B.PROYECTO = P["proyecto"]; B.UBICACION = P["ubicacion"]
    doc = B.nuevo_documento()
    for n, c, lt, lw in CAPAS_EXTRA:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt); ly.dxf.lineweight = lw
    met = metrado(P)
    laminas = {}
    laminas["DR-01"] = dr01(doc, 0.0, 0.0, P, met)
    laminas["DR-02"] = dr02(doc, 0.0, -20.0, P)
    laminas["DR-03"] = dr03(doc, 10.0, 0.0, P)
    laminas["DR-04"] = dr04(doc, 10.0, -20.0, P)
    laminas["DR-05"] = dr05(doc, 0.0, 5.0, P, met)
    laminas["DR-06"] = dr06(doc, 20.0, 0.0, P)
    for e in doc.modelspace().query("HATCH"):        # rellenos al fondo
        pass
    msp = doc.modelspace()
    fondo = {e.dxf.handle: -1 for e in msp.query("HATCH SOLID")}
    msp.set_redraw_order(fondo)
    L.presentaciones(doc, laminas)
    auditor = doc.audit()
    doc.saveas(P["salida"])
    print("%s: %s (%d errores de auditoria) -> %s" % (clave, ", ".join(laminas), len(auditor.errors), os.path.relpath(P["salida"], RAIZ)))
    return laminas


if __name__ == "__main__":
    for k in (sys.argv[1:] or PROY):
        construir(k)
