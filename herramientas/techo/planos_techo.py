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
import dxf_base as B
import dxf_layouts as L
from ezdxf.enums import TextEntityAlignment as TA

if 5 not in B.ESCALAS: B.ESCALAS.append(5)
CAPAS_EXTRA = [("PLANCHA-GALV", 5, "CONTINUOUS", 40), ("PLATINA", 140, "CONTINUOUS", 50), ("PERNOS", 34, "CONTINUOUS", 25),
               ("TUBERIA-PVC", 3, "CONTINUOUS", 35), ("TUBERIA-OCULTA", 3, "HIDDEN", 25), ("COBERTURA", 8, "CONTINUOUS", 30),
               ("MURO", 8, "CONTINUOUS", 25)]

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
CB, CH, PEST = 0.25, 0.20, 0.05            # canaleta: fondo, alto, pestana (METRADO CANALETAS)
EPL = 0.0254 / 8                            # platina 1" x 1/8": espesor
ANP = 0.0254                                # ancho de la platina
OREJA = 0.10                                # orejas del soporte (desarrollo 0.85 = 0.25 + 2 x 0.20 + 2 x 0.10)
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
    v.concreto([(-0.42, 0.10), (0.0, 0.10), (0.0, 0.10 + ALERO_E), (-0.42, 0.10 + ALERO_E)])          # alero / viga de borde
    v.pl([(-0.42, 0.08), (-0.42, 0.32)], "MURO")                                                      # corte del alero
    v.pl([(-0.42, 0.42 - 0.0), (-0.20, 0.42 - 0.022), (0.13, 0.42 - 0.055)], "COBERTURA", ancho=0.004)   # TR4 (pendiente 10 %)
    v.rect(-0.30, 0.30, -0.22, 0.40 - 0.010, "COBERTURA")                                             # apoyo / correa
    # canaleta (plancha 0.9 mm)
    v.pl([(xi, CH + PEST), (xi, 0.0), (xo, 0.0), (xo, CH), (xo - PEST, CH)], "PLANCHA-GALV", ancho=0.0012)
    lam.relleno([v(xi + 0.001, 0.001), v(xo - 0.001, 0.001), v(xo - 0.001, 0.055), v(xi + 0.001, 0.055)], "AGUA-RELLENO")
    v.ln((xi + 0.01, 0.055), (xo - 0.01, 0.055), "AGUA")
    # soporte de platina
    c = EPL / 2
    v.pl([(c, CH + OREJA), (c, -c), (xo + c, -c), (xo + c, CH + c), (xo + c - OREJA, CH + c)], "PLATINA", ancho=EPL)
    perno(v, CH + 0.075, c, 0.0635); perno(v, CH + 0.025, c, 0.0635)
    v.rect(xo - 0.075, CH + c, xo - 0.071, CH + 0.018, "PERNOS"); v.rect(CB / 2 - 0.002, -0.016, CB / 2 + 0.002, 0.004, "PERNOS")
    lam.texto(v(-0.20, 0.215), "ALERO O VIGA DE BORDE", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto(v(-0.20, 0.185), "DE CONCRETO (SEGUN ESTRUCTURAS)", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    v.cota((xi, 0.0), (xo, 0.0), -9); v.cota((xo, 0.0), (xo, CH), 8, False)
    v.cota((xi, CH), (xi, CH + PEST), -7, False); v.cota((xo - PEST, CH), (xo, CH), 9)
    v.cota((c, CH), (c, CH + OREJA), -16, False, "0.10")
    lam.juntar_llamadas()
    xt = v(0.36, 0)[0]
    for (u, w), t in (((0.05, 0.395), ["Cobertura de aluzinc TR4 e = 0.40 mm (vuela 0.13 m sobre la canaleta)"]),
                      ((c, CH + 0.075), ["Perno de expansion 1/4\" x 2 1/2\" con tarugo (2 por soporte)"]),
                      ((xi + 0.002, CH + 0.04), ["Pestana interior 0.05 contra el alero"]),
                      ((xo - 0.03, CH + 0.003), ["Pestana exterior 0.05 doblada hacia adentro + oreja del soporte",
                                                 "con tornillo autorroscante 1/4\" x 3/4\""]),
                      ((xo - 0.01, 0.12), ["Canaleta de plancha de acero galvanizado e = 0.9 mm (ASTM A653)"]),
                      ((xo + c, 0.06), ["Soporte de platina F°G° 1\" x 1/8\" @0.60 m (desarrollo 0.85 m)"]),
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
    lam.titulo_vista(450 + Ltot / f / 2, 470 - 32, "B. DESARROLLO DEL SOPORTE DE PLATINA F°G° 1\" x 1/8\"", "ESC. 1/5 - L = 0.85 m por soporte", 150)

    # ---------------- C. tapa lateral
    v = V(lam, 460, 330)
    v.pl([(0, CH + PEST), (0, 0), (CB, 0), (CB, CH), (CB - PEST, CH)], "PLANCHA-GALV", ancho=0.0012)
    v.pl([(-0.02, CH + PEST), (-0.02, -0.02), (CB + 0.02, -0.02), (CB + 0.02, CH)], "PLANCHA-GALV")
    lam.relleno([v(0, 0), v(CB, 0), v(CB, CH), v(CB - PEST, CH), v(0, CH)], "ISO-TAPA")
    for k in range(5): remache(v, (-0.01, 0.02 + k * 0.05)); remache(v, (CB + 0.01, 0.02 + k * 0.04))
    for k in range(6): remache(v, (0.0 + k * 0.05, -0.01))
    v.cota((0, -0.02), (CB, -0.02), -8); v.cota((CB + 0.02, 0), (CB + 0.02, CH), 8, False)
    v.cota((-0.02, -0.02), (0, -0.02), -16, True, "0.02")
    lam.juntar_llamadas()
    for (u, w), t in (((CB / 2, 0.12), ["Tapa de plancha galvanizada e = 0.9 mm con la seccion de la canaleta"]),
                      ((-0.02, 0.10), ["Pestana perimetral 0.02 hacia afuera, remachada"]),
                      ((-0.01, 0.17), ["Remache pop 1/8\" @0.05 + cordon de sellador de poliuretano"])):
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
        for k in range(4): remache(v, (x, 0.025 + k * 0.05))
    v.cota((0.40, CH), (0.45, CH), 8, True, "0.05")
    v.cota((0.0, 0.0), (0.0, CH), -8, False)
    lam.juntar_llamadas()
    for (u, w), t in (((0.4125, 0.125), ["2 filas de remaches pop 1/8\" @0.05 en todo el perimetro (26 por union)"]),
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
        "1. Canaleta de plancha de acero galvanizado e = 0.9 mm, seccion interior 0.25 x 0.20 m con pestanas de 0.05 m, en tramos de 2.44 m.",
        "2. Pendiente de la canaleta S = 1.00 % hacia las boquillas (memoria hidrologica); verificar con nivel antes de fijar.",
        "3. Soportes de platina F°G° 1\" x 1/8\" @0.60 m (hoja METRADO CANALETAS: soportes = L / 0.60 + 1 por canaleta).",
        "4. Abrazaderas F°G° @1.50 m en el montante; colgadores junto a cada codo del desvio bajo el alero.",
        "5. Cortes y perforaciones del galvanizado: dos manos de pintura rica en zinc.",
        "6. Las dimensiones del alero, la viga de borde y la cobertura son referenciales: ver planos de arquitectura y estructuras.",
    ], hmm=1.6, ancho_mm=180)
    return lam


# ================================================================== DR-02 (1/20)
def dr02(doc, ox, oy, P):
    lam = B.Lamina(doc, ox, oy, 10, "DR-02", "ELEVACION DE CANALETA Y CORTE DEL MONTANTE PLUVIAL",
                   "CANALETA EN EL ALERO, BOQUILLA, MONTANTE PVC 4\", FALSA COLUMNA, DADO Y SALIDA A LA CUNETA - " + P["nombre"])
    f = lam.f
    # ---------------- H. elevacion frontal de la canaleta (vista desde afuera)
    Lc = 3.00; x0mm, y0mm = 490, 475
    v = V(lam, x0mm, y0mm)
    caida = Lc * S_CAN / 100
    v.concreto([(-0.10, CH + 0.10), (Lc + 0.25, CH + 0.10), (Lc + 0.25, CH + 0.10 + ALERO_E), (-0.10, CH + 0.10 + ALERO_E)])
    v.pl([(-0.10, CH + 0.10 + ALERO_E + 0.10), (Lc + 0.25, CH + 0.10 + ALERO_E + 0.07)], "COBERTURA", ancho=0.005)
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
    lam.texto(v(-0.08, CH + 0.10 + ALERO_E + 0.125), "Cobertura de aluzinc TR4 e = 0.40 mm", 2.0, "TEXTOS")
    lam.texto(v(Lc / 2, CH + 0.10 + ALERO_E / 2), "ALERO O VIGA DE BORDE DE CONCRETO (SEGUN ESTRUCTURAS)", 2.0, "TEXTOS", TA.MIDDLE_CENTER)
    lam.titulo_vista(x0mm + Lc / f / 2, y0mm + 80, "H. ELEVACION FRONTAL DE LA CANALETA", "ESC. 1/10 - vista desde afuera", 120)

    # ---------------- I. corte del montante (alero, desvio, bajada, falsa columna, dado, salida)
    x0mm, y0mm = 75, 95
    v = V(lam, x0mm, y0mm)
    z_al = 3.00                                     # fondo del alero sobre el piso terminado (tipico)
    xa = ALERO_V                                    # cara exterior del alero
    xt = FC[1] / 2                                  # eje del montante (centro de la falsa columna)
    xcu = xa + 1.30; r = DT / 2                     # cuneta de llegada (referencia) y radio del tubo
    v.pl([(-0.25, -0.40), (-0.25, z_al + ALERO_E)], "MURO"); v.pl([(0.0, 0.0), (0.0, z_al)], "MURO")
    lam.texto(v(-0.125, 1.9), "MURO", 2.2, "TEXTOS", TA.MIDDLE_CENTER)
    v.concreto([(-0.25, z_al), (xa, z_al), (xa, z_al + ALERO_E), (-0.25, z_al + ALERO_E)])
    v.pl([(-0.40, z_al + ALERO_E + 0.14), (xa + 0.13, z_al + ALERO_E + 0.06)], "COBERTURA", ancho=0.01)
    v.ln((-0.30, 0.0), (xcu + 0.85, 0.0), "TERRENO")
    lam.nivel(v(xcu + 0.75, 0.0), 0.0, "NPT +0.00", 1)
    # canaleta en la cara del alero
    zc = z_al - 0.10
    xi = xa + EPL; xo = xi + CB
    v.pl([(xi, zc + CH + PEST), (xi, zc), (xo, zc), (xo, zc + CH), (xo - PEST, zc + CH)], "PLANCHA-GALV", ancho=0.006)
    v.pl([(xa + EPL / 2, zc + CH + OREJA), (xa + EPL / 2, zc), (xo + EPL / 2, zc), (xo + EPL / 2, zc + CH)], "PLATINA", ancho=0.006)
    xb = xi + 0.07                                  # boquilla
    zcodo1 = zc - 0.30
    # tubo: contorno exterior e interior de cada tramo (codos a escuadra)
    v.pl([(xb - r, zc), (xb - r, zcodo1 + r), (xt + r, zcodo1 + r), (xt + r, FC[2])], "TUBERIA-PVC", ancho=0.003)
    v.pl([(xb + r, zc), (xb + r, zcodo1 - r), (xt - r, zcodo1 - r), (xt - r, FC[2])], "TUBERIA-PVC", ancho=0.003)
    v.pl([(xt + r, FC[2]), (xt + r, -0.20 + r), (xcu + 0.10, -0.20 + r)], "TUBERIA-OCULTA")
    v.pl([(xt - r, FC[2]), (xt - r, -0.20 - r), (xcu + 0.10, -0.20 - r)], "TUBERIA-OCULTA")
    # colgadores: varilla roscada desde el fondo del alero y banda alrededor del tubo
    for x in (xb - 0.15, xt + 0.15):
        v.pl([(x, zcodo1 + r + 0.006), (x, z_al)], "PERNOS", ancho=0.0095)
        v.rect(x - 0.0127, zcodo1 - r - 0.004, x + 0.0127, zcodo1 + r + 0.006, "PLATINA")
    # falsa columna y dado
    v.concreto([(0.0, 0.0), (FC[1], 0.0), (FC[1], FC[2]), (0.0, FC[2])])
    v.concreto([(xt - DADO[0] / 2, -DADO[2]), (xt + DADO[0] / 2, -DADO[2]), (xt + DADO[0] / 2, 0.0), (xt - DADO[0] / 2, 0.0)])
    for s in (-1, 1): v.ln((xt + s * DT / 2, -0.20 + DT / 2 * (0 if s < 0 else 1)), (xt + s * DT / 2, FC[2]), "TUBERIA-OCULTA")
    # abrazaderas
    za = [1.45, 2.45]
    for z in za: v.rect(xt + DT / 2, z - ANP / 2, xt + DT / 2 + 0.008, z + ANP / 2, "PLATINA"); v.ln((0.0, z), (xt + DT / 2, z), "PLATINA")
    # cuneta (referencia)
    v.pl([(xcu, 0.0), (xcu, -0.50), (xcu + 0.60, -0.50), (xcu + 0.60, 0.0)], "CUNETA"); v.pl([(xcu + 0.10, 0.0), (xcu + 0.10, -0.40), (xcu + 0.50, -0.40), (xcu + 0.50, 0.0)], "CUNETA")
    v.ln((xa + 0.80, -0.34), (xa + 0.80, -0.06), "CORTES"); v.ln((xa + 0.84, -0.34), (xa + 0.84, -0.06), "CORTES")
    # cotas
    v.cota((0.0, z_al), (xa, z_al), 8, True)
    v.cota((0.0, 0.0), (0.0, FC[2]), -9, False); v.cota((xt - DADO[0] / 2, -DADO[2]), (xt - DADO[0] / 2, 0.0), -9, False)
    v.cota((xt + DADO[0] / 2, -DADO[2]), (xt - DADO[0] / 2, -DADO[2]), -6, True)
    v.cota((xt + DT / 2 + 0.01, za[0]), (xt + DT / 2 + 0.01, za[1]), 6, False, "<= 1.50")
    v.cota((xa + CB + 0.05, 0.0), (xa + CB + 0.05, z_al), 12, False, "variable (3.00 tipico)")
    lam.juntar_llamadas()
    xtx = v(xcu + 0.95, 0)[0]
    for (u, w), t in (((xa + 0.10, zc + 0.10), ["Canaleta 0.25 x 0.20 con soporte @0.60 (ver DR-01, detalle A)"]),
                      ((xb, zc - 0.10), ["Boquilla Ø 0.10 y montante PVC 4\""]),
                      ((xb - 0.15, z_al - 0.10), ["Colgador F°G° con varilla roscada 3/8\" (uno junto a cada codo)"]),
                      ((xt + 0.25, zcodo1), ["Desvio bajo el alero con codos PVC 4\" x 90°"]),
                      ((xt + DT / 2 + 0.004, za[1]), ["Abrazadera F°G° @1.50 m (ver DR-01, detalle F)"]),
                      ((FC[1], 0.90), ["Falsa columna de concreto f'c = 175 kg/cm2 de 0.20 x 0.15 x 1.30 m",
                                       "(4 Ø 3/8\" y estribos Ø 3/8\" @0.15 segun metrado)"]),
                      ((xt + DADO[0] / 2, -0.15), ["Dado de concreto f'c = 140 kg/cm2 de 0.40 x 0.40 x 0.35 m con codo PVC 4\" x 90°"]),
                      ((xcu + 0.10, -0.25), ["Salida PVC 4\" hasta la cuneta (longitud segun metrado de montantes)"])):
        lam.llamada(v(u, w), (xtx, v(0, w)[1]), t, 2.0)
    lam.volcar_llamadas()
    lam.titulo_vista(x0mm + 100, y0mm - 58, "I. CORTE DEL MONTANTE PLUVIAL TIPICO", "ESC. 1/10 - del alero a la cuneta", 130)
    lam.notas(470, 330, "NOTAS", [
        "1. Montante de tuberia PVC-U para desague 4\" (NTP 399.003), uniones con cemento solvente; 3 codos de 90° por montante (metrado).",
        "2. La longitud de cada montante es la de la hoja METRADO MONTANTES (6.16 a 11.00 m segun edificacion); el corte I es tipico.",
        "3. Abrazaderas @1.50 m como maximo; colgadores junto a cada codo del desvio (2 por montante en edificaciones).",
        "4. La falsa columna protege el tramo inferior del montante; el codo de salida queda dentro del dado.",
        "5. Altura del alero, vuelo y cobertura segun planos de arquitectura y estructuras de cada edificacion.",
    ], hmm=1.8, ancho_mm=350)
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
