"""Laminas de detalles constructivos de la red de cunetas (todo a escala real: 1 unidad = 1 m).

Medidas de conocimiento/07_componentes_complementarios.md (las mismas de los expedientes de CAR Varones, CUI 2705619; Hogar de
Refugio, CUI 2675514; CAR Mujeres, CUI 2717013 e I.E. N.° 0590 Barranquita, C.I. 468901):
- Lamina 1 (1/5): rejilla metalica movil (modulo de 1.00 m, 39 platinas 1" x 3/16" @1" soldadas a 2 angulos L 1" x 1" x 3/16",
  apoyada en el rebaje de 0.05 x 1"), tapa de inspeccion 0.60 x 0.60 x 0.10 (parrilla 3/8" en ambos sentidos, 2 asas embutidas),
  junta de dilatacion e = 1" en toda la seccion en U cada 3.00 m (tecnopor 1" + sellador asfaltico 1" x 2" RC-250 + arena en la
  cara interior; acero interrumpido a 0.05 m) y junta cuneta - piso.
- Lamina 2 (1/5): lloradero (tubo PVC 3" de 0.30 m a media altura del muro que da a area verde, 8 perforaciones 3/8", caja
  filtrante 0.30 x 0.30 x 0.30 de grava 20-40 mm envuelta en geotextil), falsa columna 0.20 x 0.15 con el montante 4" en la
  esquina (4 barras 3/8" y estribos 3/8" @0.15), canaleta galvanizada 0.25 x 0.20 con su soporte de platina 1" x 1/8" y
  sumidero (rejilla 0.25 x 0.25 de 9 platinas, marco L 1" x 1" x 3/16", caja 0.45 x 0.45, salida PVC 4" con un codo de 90).
- Lamina 3 (1/10): montante en elevacion (canaleta, boquilla, desvio bajo el alero con colgadores, bajada con abrazaderas,
  falsa columna de 1.30 m, dado 0.40 x 0.40 x 0.35 con el codo de salida y tubo a la cuneta) y muro con lloraderos @1.50 m.
Las medidas que dependen del proyecto (ancho libre b, altura de alero, separacion de lloraderos) vienen del diseno.
"""
import math

from ezdxf.enums import TextEntityAlignment as TA

from . import dxf_base as B

IN = 0.0254
CAPAS = [("DET-TECNOPOR", 40, "CONTINUOUS", (250, 236, 200)), ("DET-SELLADOR", 250, "CONTINUOUS", (60, 60, 60)),
         ("DET-GRAVA", 34, "CONTINUOUS", (210, 190, 160)), ("DET-GEOTEXTIL", 94, "DASHED", None), ("DET-PVC", 140, "CONTINUOUS", (190, 215, 240)),
         ("DET-METAL", 32, "CONTINUOUS", (150, 150, 160)), ("DET-TERRENO", 8, "CONTINUOUS", (225, 215, 195)), ("DET-PISO", 8, "CONTINUOUS", (238, 238, 238)),
         ("DET-CORTE", 6, "DASHDOT", None)]


def capas(doc):
    for n, c, lt, rgb in CAPAS:
        if n in doc.layers: continue
        if lt not in doc.linetypes: lt = "CONTINUOUS"
        ly = doc.layers.add(n, color=c, linetype=lt)
        if rgb: B.COLOR_RGB[n] = rgb


class Vista:
    """Origen de una vista en la lamina (mm de papel) y dibujo en metros reales desde ese origen."""
    def __init__(self, lam, xmm, ymm):
        self.lam = lam; self.O = lam.P(xmm, ymm)

    def p(self, x, y): return (self.O[0] + x, self.O[1] + y)
    def pts(self, L): return [self.p(x, y) for x, y in L]
    def poli(self, L, capa, cerrada=True, **kw): return self.lam.poli(self.pts(L), capa, cerrada=cerrada, **kw)
    def rect(self, x0, y0, x1, y1, capa): return self.lam.poli(self.pts([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), capa, cerrada=True)
    def lleno(self, L, capa_relleno, capa_borde=None):
        self.lam.relleno(self.pts(L), capa_relleno)
        if capa_borde: self.poli(L, capa_borde)
    def linea(self, a, b, capa): return self.lam.linea(self.p(*a), self.p(*b), capa)
    def circ(self, c, r, capa): return self.lam.circulo(self.p(*c), r, capa)
    def barra(self, c):                         # barra de 3/8" vista en seccion (diametro real)
        self.lam.bloque("ACERO-38", self.p(*c), 1.0, capa="ACERO-PUNTOS")
    def cota(self, a, b, d_mm, horizontal=True, texto=None):
        return self.lam.cota(self.p(*a), self.p(*b), d_mm, horizontal, texto)
    def texto(self, c, t, hmm=1.8, al=TA.MIDDLE_CENTER, capa="TEXTOS"): return self.lam.texto(self.p(*c), t, hmm, capa, al)


def titulo(lam, xmm, ymm, t, sub, ancho=None):
    lam.titulo_vista(xmm, ymm, t, sub, ancho_mm=ancho or max(60, 2.9 * len(t)))


def llamadas(lam, V, items, xt_mm, ytop_mm, ybot_mm, hmm=1.7, al=TA.LEFT):
    """items: [((x, y) en metros de la vista, [lineas])]: columna de textos sin cruces."""
    lam.columna_llamadas([(V.p(*p), l) for p, l in items], lam.P(xt_mm, 0)[0], lam.P(0, ytop_mm)[1], lam.P(0, ybot_mm)[1], hmm, al)


def u_seccion(V, b, H, em, ef, sol=0.10, tapa=False, rebaje=True):
    """Seccion en U de la cuneta con solado (origen: esquina inferior izquierda de la losa de fondo)."""
    W = b + 2 * em
    V.lleno([(-0.05, -sol), (W + 0.05, -sol), (W + 0.05, 0), (-0.05, 0)], "SEC-SOLADO", "CONCRETO")
    r = 0.05 if rebaje and not tapa else 0.0; rh = IN if r else 0.0
    U = [(0, 0), (W, 0), (W, ef + H), (W - em + r, ef + H), (W - em + r, ef + H - rh), (W - em, ef + H - rh), (W - em, ef), (em, ef),
         (em, ef + H - rh), (em - r, ef + H - rh), (em - r, ef + H), (0, ef + H)]
    V.lleno(U, "CONCRETO-ACHURADO", "CONCRETO")
    return W


# ============================================================================================== lamina 1
def lamina_cuneta(doc, codigo, ox, oy, P, b):
    em, ef = P["e_muro"], P["e_fondo"]; W = b + 2 * em
    lam = B.Lamina(doc, ox, oy, 5, codigo, "DETALLES DE CUNETA: REJILLA, TAPA DE INSPECCION Y JUNTAS",
                   "REJILLA METALICA MOVIL, TAPA 0.60 x 0.60 x 0.10, JUNTA DE DILATACION E = 1\" Y JUNTA CUNETA - PISO - ESC. 1/5")
    # ---------------------------------------------------------------- rejilla: planta de un modulo
    L, Wm = 0.997, b + 2 * 0.05 - 2 * 0.0015
    V = Vista(lam, 40, 445)
    titulo(lam, 40 + L * 100, 572, "REJILLA METALICA - PLANTA DE UN MODULO", "ESC. 1/5")
    V.rect(0, 0, L, Wm, "DET-METAL")
    for y0 in (0.0, Wm - IN): V.lleno([(0, y0), (L, y0), (L, y0 + IN), (0, y0 + IN)], "DET-METAL", "MARCO-METALICO")
    n = 39; x0 = (L - (n - 1) * IN) / 2
    for k in range(n):
        x = x0 + k * IN; V.rect(x - 0.0024, IN, x + 0.0024, Wm - IN, "MARCO-METALICO")
    V.cota((0, 0), (L, 0), -8, True, "%.3f" % L)
    V.cota((L, 0), (L, Wm), 8, False, "%.3f" % Wm)
    V.linea((L / 2, -0.06), (L / 2, Wm + 0.06), "DET-CORTE")
    V.texto((L / 2 + 0.03, Wm + 0.05), "A", 3.0); V.texto((L / 2 + 0.03, -0.05), "A", 3.0)
    llamadas(lam, V, [((x0 + 5 * IN, IN + 0.02), ["39 PLATINAS 1\" x 3/16\" DE CANTO @1\" ENTRE EJES", "(abertura libre 0.021 m), L = %.3f m" % (Wm - 2 * IN)]),
                      ((x0 + 22 * IN, IN / 2), ["ANGULO L 1\" x 1\" x 3/16\" (2 por modulo)", "platinas soldadas a tope, 2 cordones E6011 1/8\""])],
             60, 425, 410)
    # ---------------------------------------------------------------- rejilla: corte A-A
    V = Vista(lam, 300, 450)
    titulo(lam, 300 + W * 100, 572, "CORTE A-A", "REJILLA EN EL REBAJE DE LOS MUROS - ESC. 1/5", 70)
    h = 0.25
    for xa, s in ((0.0, 1), (W, -1)):
        xm = xa + s * em
        pol = [(xa, 0), (xa + s * em, 0), (xa + s * em, h - IN), (xa + s * 0.05, h - IN), (xa + s * 0.05, h), (xa, h)]
        V.lleno(pol, "CONCRETO-ACHURADO", "CONCRETO")
        V.linea((xa - s * 0.02, 0), (xa + s * (em + 0.02), 0), "CONCRETO-OCULTO")
    x1 = 0.05 + 0.0015
    for xa, s in ((x1, 1), (W - x1, -1)):
        V.lleno([(xa, h - IN), (xa + s * IN, h - IN), (xa + s * IN, h - IN + 0.0048), (xa, h - IN + 0.0048)], "DET-METAL", "MARCO-METALICO")
        V.lleno([(xa + s * (IN - 0.0048), h - IN), (xa + s * IN, h - IN), (xa + s * IN, h), (xa + s * (IN - 0.0048), h)], "DET-METAL", "MARCO-METALICO")
    V.lleno([(x1 + IN, h - IN), (W - x1 - IN, h - IN), (W - x1 - IN, h), (x1 + IN, h)], "DET-METAL", "MARCO-METALICO")
    V.cota((em, 0.05), (em + b, 0.05), -6, True, "%.2f" % b)
    V.cota((0, h), (W, h), 9, True, "%.2f" % W)
    V.cota((0, h), (0.05, h), 4, True, "0.05")
    llamadas(lam, V, [((W / 2, h - IN / 2), ["PLATINA 1\" x 3/16\" (corte a lo largo)"]),
                      ((W - x1 - IN / 2, h - IN), ["ANGULO L 1\" x 1\" x 3/16\": ala horizontal", "en el rebaje y ala vertical hacia la cuneta"]),
                      ((W - 0.025, h - IN), ["REBAJE 0.05 x 1\" en el borde interior", "de cada muro (listones al vaciar)"])],
             300 + W * 200 + 12, 520, 470)
    # ---------------------------------------------------------------- tapa de inspeccion: planta
    T, et, rec = P.get("tapa_lado", 0.60), 0.10, 0.025
    V = Vista(lam, 45, 240)
    titulo(lam, 45 + T * 100, 385, "TAPA DE INSPECCION %.2f x %.2f x %.2f - PLANTA" % (T, T, et), "ESC. 1/5", 110)
    V.lleno([(0, 0), (T, 0), (T, T), (0, T)], "CONCRETO-ACHURADO", "CONCRETO")
    nb = round((T - 2 * rec) / 0.15) + 1; sep = (T - 2 * rec) / (nb - 1)
    for k in range(nb):
        c = rec + k * sep
        V.linea((rec, c), (T - rec, c), "ACERO"); V.linea((c, rec), (c, T - rec), "ACERO-LONG")
    for yc in (0.10, T - 0.10):
        V.rect(T / 2 - 0.09, yc - 0.03, T / 2 + 0.09, yc + 0.03, "CONCRETO")
        V.poli([(T / 2 - 0.06, yc), (T / 2 - 0.06, yc + 0.012), (T / 2 + 0.06, yc + 0.012), (T / 2 + 0.06, yc)], "ACERO", cerrada=False)
    V.cota((0, 0), (T, 0), -8, True, "%.2f" % T); V.cota((T, 0), (T, T), 8, False, "%.2f" % T)
    V.linea((-0.05, T / 2), (T + 0.05, T / 2), "DET-CORTE"); V.texto((-0.08, T / 2 + 0.03), "B", 3.0); V.texto((T + 0.08, T / 2 + 0.03), "B", 3.0)
    llamadas(lam, V, [((rec + sep, T - rec - sep / 2), ["PARRILLA SIMPLE 3/8\" en ambos sentidos", "%d + %d barras de %.2f m, recubrimiento %.3f" % (nb, nb, T - 2 * rec, rec)]),
                      ((T / 2 + 0.05, T - 0.10), ["ASA DE FIERRO LISO 3/8\" embutida en bolsillo", "0.18 x 0.06 x 0.03 (no sobresale del piso)"])],
             45 + T * 200 + 14, 350, 300)
    # ---------------------------------------------------------------- tapa de inspeccion: corte B-B sobre la cuneta tapada
    V = Vista(lam, 340, 250)
    Ht = 0.30
    titulo(lam, 340 + W * 100, 385, "CORTE B-B", "TAPA SOBRE EL TRAMO TAPADO - ESC. 1/5", 70)
    W_ = u_seccion(V, b, Ht, em, ef, tapa=True)
    yt = ef + Ht
    V.lleno([(0.0025, yt), (W - 0.0025, yt), (W - 0.0025, yt + et), (0.0025, yt + et)], "CONCRETO-ACHURADO", "CONCRETO")
    for k in range(nb):
        V.barra((rec + k * sep * W / T, yt + rec + 0.005))
    V.linea((rec, yt + rec + 0.014), (W - rec, yt + rec + 0.014), "ACERO")
    V.cota((W, 0), (W, ef), 6, False, "%.2f" % ef); V.cota((W, ef), (W, yt), 6, False, "%.2f" % Ht)
    V.cota((W, yt), (W, yt + et), 6, False, "%.2f" % et)
    V.cota((0, -0.10), (W, -0.10), -6, True, "%.2f" % W)
    llamadas(lam, V, [((W / 2, yt + et * 0.7), ["TAPA DE CONCRETO ARMADO f'c = 175 kg/cm2,", "al ras del piso terminado, holgura 5 mm"]),
                      ((em / 2, yt - 0.05), ["MUROS Y LOSA DE FONDO DE %.2f m" % em]),
                      ((W / 2, -0.05), ["SOLADO f'c = 100 kg/cm2 E = 0.10"])],
             340 + W * 200 + 12, 350, 270)
    # ---------------------------------------------------------------- junta de dilatacion: seccion en la junta
    H = 0.50
    V = Vista(lam, 590, 240)
    titulo(lam, 590 + W * 100, 385, "JUNTA DE DILATACION - SECCION EN LA JUNTA", "TECNOPOR 1\" EN TODA LA U - ESC. 1/5", 100)
    V.lleno([(-0.05, -0.10), (W + 0.05, -0.10), (W + 0.05, 0), (-0.05, 0)], "SEC-SOLADO", "CONCRETO")
    U = [(0, 0), (W, 0), (W, ef + H), (W - em, ef + H), (W - em, ef), (em, ef), (em, ef + H), (0, ef + H)]
    V.lleno(U, "DET-TECNOPOR", "CONCRETO")
    s = 0.05
    banda = [(em, ef + H), (em, ef), (W - em, ef), (W - em, ef + H), (W - em - s, ef + H), (W - em - s, ef + s), (em + s, ef + s), (em + s, ef + H)]
    V.lleno(banda, "DET-SELLADOR", "DET-SELLADOR")
    V.cota((0, 0), (0, ef + H), -6, False, "H + %.2f" % ef)
    V.cota((0, -0.10), (W, -0.10), -6, True, "%.2f" % W)
    llamadas(lam, V, [((W / 2, ef / 2), ["PLANCHA DE TECNOPOR 1\" en toda la seccion", "en U (muros y losa de fondo) cada 3.00 m"]),
                      ((W - em - s / 2, ef + H * 0.6), ["SELLADOR ASFALTICO 1\" x 2\" (RC-250 + arena", "gruesa) en la cara interior, al ras"]),
                      ((W + 0.03, -0.05), ["El solado se vacia corrido"])],
             590 + W * 200 + 12, 350, 280)
    # ---------------------------------------------------------------- junta: planta de un tramo con la junta
    V = Vista(lam, 45, 40)
    Lj = 0.80
    titulo(lam, 45 + Lj * 100, 205, "JUNTA DE DILATACION - PLANTA", "ACERO LONGITUDINAL INTERRUMPIDO A 0.05 m DE LA JUNTA - ESC. 1/5", 120)
    for y0 in (0.0, W - em):
        V.lleno([(0, y0), (Lj / 2 - IN / 2, y0), (Lj / 2 - IN / 2, y0 + em), (0, y0 + em)], "CONCRETO-ACHURADO", "CONCRETO")
        V.lleno([(Lj / 2 + IN / 2, y0), (Lj, y0), (Lj, y0 + em), (Lj / 2 + IN / 2, y0 + em)], "CONCRETO-ACHURADO", "CONCRETO")
    V.lleno([(Lj / 2 - IN / 2, 0), (Lj / 2 + IN / 2, 0), (Lj / 2 + IN / 2, W), (Lj / 2 - IN / 2, W)], "DET-TECNOPOR", "CONCRETO")
    for y0 in (em, W - em - 0.05):
        V.lleno([(Lj / 2 - IN / 2, y0), (Lj / 2 + IN / 2, y0), (Lj / 2 + IN / 2, y0 + 0.05), (Lj / 2 - IN / 2, y0 + 0.05)], "DET-SELLADOR", "DET-SELLADOR")
    for yb in (0.04, W - 0.04):
        V.linea((0, yb), (Lj / 2 - IN / 2 - 0.05, yb), "ACERO-LONG"); V.linea((Lj / 2 + IN / 2 + 0.05, yb), (Lj, yb), "ACERO-LONG")
    V.rect(0, em, Lj, W - em, "CONCRETO-OCULTO")
    V.cota((Lj / 2 - IN / 2 - 0.05, 0.04), (Lj / 2 - IN / 2, 0.04), -10, True, "0.05")
    V.cota((0, W), (Lj, W), 6, True, "%.2f" % Lj)
    llamadas(lam, V, [((Lj / 2, W / 2), ["JUNTA E = 1\" CADA 3.00 m y en los cambios de direccion"]),
                      ((Lj / 2 + IN / 2 + 0.10, W - 0.04), ["Acero longitudinal 3/8\": no atraviesa la junta"])],
             45 + Lj * 200 + 12, 150, 110)
    # ---------------------------------------------------------------- junta cuneta - piso
    V = Vista(lam, 650, 460)
    titulo(lam, 650 - 0.10 * 200, 572, "JUNTA CUNETA - PISO", "TECNOPOR 1\" Y SELLADOR 1\" x 2\" - ESC. 1/5", 70)
    hm = 0.25
    V.lleno([(0, 0), (em, 0), (em, hm - IN), (em - 0.05, hm - IN), (em - 0.05, hm), (0, hm)], "CONCRETO-ACHURADO", "CONCRETO")
    V.lleno([(-IN, 0.05), (0, 0.05), (0, hm), (-IN, hm)], "DET-TECNOPOR", "CONCRETO")
    V.lleno([(-IN, hm - 0.05), (0, hm - 0.05), (0, hm), (-IN, hm)], "DET-SELLADOR", "DET-SELLADOR")
    V.lleno([(-0.45, hm - 0.10), (-IN, hm - 0.10), (-IN, hm), (-0.45, hm)], "DET-PISO", "CONCRETO")
    V.lleno([(-0.45, 0.05), (-IN, 0.05), (-IN, hm - 0.10), (-0.45, hm - 0.10)], "DET-TERRENO", "TERRENO")
    V.cota((-IN, hm), (0, hm), 6, True, "1\"")
    llamadas(lam, V, [((-IN / 2, hm - 0.025), ["SELLADOR ASFALTICO 1\" x 2\" al ras del piso"]),
                      ((-IN / 2, 0.12), ["TECNOPOR 1\" en todo el espesor del piso"]),
                      ((-0.25, hm - 0.05), ["PISO, VEREDA O PATIO ADYACENTE"]),
                      ((em / 2, 0.10), ["MURO DE LA CUNETA (borde al ras del piso)"])],
             650 + em * 200 + 12, 545, 470)
    lam.notas(330, 200, "NOTAS", [
        "1. Medidas en metros; escala real 1/5. Ancho libre b = %.2f m (el de cada eje en el cuadro de ejes); muros y losa de fondo de %.2f m." % (b, em),
        "2. Rejilla: modulos removibles de 1.00 m (0.997 fabricado, 3 mm entre modulos), acero A36, 2 manos de anticorrosivo y 2 de esmalte; ~20 kg/m.",
        "3. Tapa de inspeccion: concreto f'c = 175 kg/cm2, molde sobre base plana, curado 7 dias; al inicio y fin de cada tramo tapado, en empalmes y a 10 m como maximo.",
        "4. Juntas de dilatacion cada 3.00 m en toda la seccion en U (EG-2013, seccion 510); junta cuneta - piso solo donde la cuneta colinda con piso, vereda o patio.",
    ], hmm=1.8, ancho_mm=300)
    return lam


# ============================================================================================== lamina 2
def lamina_complementos(doc, codigo, ox, oy, P, b, sep_llor):
    em, ef = P["e_muro"], P["e_fondo"]; W = b + 2 * em
    lam = B.Lamina(doc, ox, oy, 5, codigo, "DETALLES: LLORADERO, FALSA COLUMNA, CANALETA Y SUMIDERO",
                   "LLORADERO PVC 3\" CON CAJA FILTRANTE, MONTANTE 4\" EN FALSA COLUMNA, CANALETA 0.25 x 0.20 Y SUMIDERO 0.25 x 0.25 - ESC. 1/5")
    # ---------------------------------------------------------------- lloradero: corte
    H = 0.50
    V = Vista(lam, 160, 395)
    titulo(lam, 160 + W * 100 - 15, 572, "LLORADERO - CORTE", "MURO QUE DA A AREA VERDE - ESC. 1/5", 70)
    V.lleno([(-0.55, -0.10), (0, -0.10), (0, ef + H + 0.05), (-0.55, ef + H + 0.05)], "DET-TERRENO", "TERRENO")
    u_seccion(V, b, H, em, ef)
    yc = ef + H / 2
    V.lleno([(-0.30, yc - 0.15), (0, yc - 0.15), (0, yc + 0.15), (-0.30, yc + 0.15)], "DET-GRAVA", "DET-GRAVA")
    V.poli([(-0.31, yc - 0.16), (0, yc - 0.16), (0, yc + 0.16), (-0.31, yc + 0.16)], "DET-GEOTEXTIL")
    r = 0.0381; dz = 0.0015
    V.lleno([(-0.20, yc - r + dz), (em, yc - r), (em, yc + r), (-0.20, yc + r + dz)], "DET-PVC", "DET-PVC")
    for k in range(4): V.circ((-0.18 + k * 0.05, yc - r * 0.5), 0.0048, "DET-PVC")
    V.linea((-0.62, ef + H + 0.05), (0.0, ef + H + 0.05), "TERRENO")
    V.cota((W, ef), (W, yc), 6, False, "H/2"); V.cota((-0.30, yc + 0.17), (0, yc + 0.17), 6, True, "0.30")
    V.cota((-0.20, yc - 0.20), (em, yc - 0.20), -6, True, "0.30")
    llamadas(lam, V, [((-0.25, yc + 0.10), ["CAJA FILTRANTE 0.30 x 0.30 x 0.30 de grava 20-40 mm", "lavada, envuelta en geotextil no tejido (traslape 0.10)"]),
                      ((-0.10, yc - r * 0.5), ["TUBO PVC 3\" L = 0.30 m (0.10 en el muro + 0.20 en el filtro),", "8 perforaciones 3/8\", S = 0.5 % hacia la cuneta"]),
                      ((-0.40, ef + H + 0.05), ["AREA VERDE (terreno natural)"])],
             160 + W * 200 + 14, 545, 470)
    # ---------------------------------------------------------------- falsa columna en la esquina: planta
    V = Vista(lam, 470, 415)
    titulo(lam, 470 + 0.35 * 200, 576, "MONTANTE EN FALSA COLUMNA - PLANTA", "EN LA ESQUINA DE LA EDIFICACION - ESC. 1/5", 110)
    em_, col = 0.15, 0.25
    V.lleno([(0, 0), (col, 0), (col, col), (0, col)], "CONCRETO-ACHURADO", "CONCRETO")
    V.poli([(col, 0), (0.75, 0), (0.75, em_), (col, em_)], "CONCRETO", cerrada=True)
    V.poli([(0, col), (0, 0.65), (em_, 0.65), (em_, col)], "CONCRETO", cerrada=True)
    fx, fy = col + 0.02, -0.15
    V.lleno([(fx, fy), (fx + 0.20, fy), (fx + 0.20, 0), (fx, 0)], "CONCRETO-ACHURADO", "CONCRETO")
    cx, cy = fx + 0.10, fy + 0.075
    V.circ((cx, cy), 0.1143 / 2, "DET-PVC"); V.circ((cx, cy), 0.1143 / 2 - 0.003, "DET-PVC")
    for dx, dy in ((0.03, 0.03), (0.17, 0.03), (0.03, 0.12), (0.17, 0.12)): V.barra((fx + dx, fy + dy))
    V.poli([(fx + 0.02, fy + 0.02), (fx + 0.18, fy + 0.02), (fx + 0.18, fy + 0.13), (fx + 0.02, fy + 0.13)], "ACERO")
    V.cota((fx, fy), (fx + 0.20, fy), -6, True, "0.20"); V.cota((fx + 0.20, fy), (fx + 0.20, 0), 6, False, "0.15")
    llamadas(lam, V, [((cx + 0.03, cy + 0.03), ["MONTANTE PVC 4\" (Ø ext. 0.114)"]),
                      ((fx + 0.17, fy + 0.03), ["4 Ø 3/8\" y estribos Ø 3/8\" @0.15, recubrimiento 0.02"]),
                      ((fx + 0.10, -0.01), ["FALSA COLUMNA 0.20 x 0.15 x 1.30, f'c = 175 kg/cm2,", "adosada al muro junto a la columna de la esquina"]),
                      ((col / 2, col / 2), ["COLUMNA Y MUROS DE LA EDIFICACION (referencial)"])],
             470 + 0.80 * 200, 545, 455)
    # ---------------------------------------------------------------- canaleta con soporte: corte
    V = Vista(lam, 90, 200)
    cb, ch, pe = 0.25, 0.20, 0.05
    titulo(lam, 90 + 0.25 * 200, 330, "CANALETA 0.25 x 0.20 - CORTE", "PLANCHA GALVANIZADA 0.9 mm Y SOPORTE 1\" x 1/8\" @0.60 - ESC. 1/5", 120)
    V.lleno([(cb + 0.06, ch - 0.05), (cb + 0.35, ch - 0.05), (cb + 0.35, ch + 0.10), (cb + 0.06, ch + 0.10)], "CONCRETO-ACHURADO", "CONCRETO")
    V.poli([(-pe, ch), (0, ch), (0, 0), (cb, 0), (cb, ch), (cb + pe, ch)], "DET-METAL", cerrada=False, ancho=0.0009 * 3)
    g = 0.0032
    V.poli([(-0.10, ch + g), (-g, ch + g), (-g, -g), (cb + g, -g), (cb + g, ch + 0.10), (cb + 0.06, ch + 0.10)], "MARCO-METALICO", cerrada=False, ancho=g)
    V.linea((cb + 0.40, ch + 0.13), (-0.06, ch + 0.02), "DET-METAL")
    V.cota((0, -0.05), (cb, -0.05), -6, True, "%.2f" % cb); V.cota((-0.08, 0), (-0.08, ch), -6, False, "%.2f" % ch)
    llamadas(lam, V, [((cb / 2, 0.003), ["PLANCHA DE ACERO GALVANIZADO e = 0.9 mm,", "pestanas de 0.05, S = 1 % hacia las boquillas"]),
                      ((cb + g, ch / 2), ["SOPORTE DE PLATINA F°G° 1\" x 1/8\" @0.60 m,", "2 pernos de expansion 1/4\" por soporte"]),
                      ((cb + 0.25, ch + 0.10), ["ALERO O VIGA DE BORDE (referencial)"]),
                      ((0.10, ch + 0.05), ["COBERTURA (vuela sobre la canaleta)"])],
             90 + 0.55 * 200, 315, 190)
    # ---------------------------------------------------------------- sumidero: planta
    c, rj = 0.45, 0.25
    V = Vista(lam, 420, 252)
    titulo(lam, 420 + c * 100, 368, "SUMIDERO - PLANTA", "REJILLA 0.25 x 0.25, CAJA 0.45 x 0.45 - ESC. 1/5", 80)
    V.lleno([(0, 0), (c, 0), (c, c), (0, c)], "CONCRETO-ACHURADO", "CONCRETO")
    a0 = (c - rj) / 2
    V.lleno([(a0, a0), (a0 + rj, a0), (a0 + rj, a0 + rj), (a0, a0 + rj)], "DET-METAL", "MARCO-METALICO")
    for k in range(1, 10):
        x = a0 + k * rj / 10; V.rect(x - 0.0024, a0 + 0.004, x + 0.0024, a0 + rj - 0.004, "MARCO-METALICO")
    V.cota((0, 0), (c, 0), -6, True, "%.2f" % c); V.cota((a0, c), (a0 + rj, c), 6, True, "%.2f" % rj)
    llamadas(lam, V, [((a0 + rj / 2 + 0.01, a0 + rj / 2), ["REJILLA DE 9 PLATINAS 1\" x 3/16\" @0.025,", "removible, sobre marco L 1\" x 1\" x 3/16\""]),
                      ((c - 0.03, 0.03), ["CAJA DE CONCRETO f'c = 140 kg/cm2"])],
             420 + c * 200 + 12, 335, 285)
    # ---------------------------------------------------------------- sumidero: corte
    V = Vista(lam, 420, 120)
    titulo(lam, 420 + 0.50 * 200, 225, "SUMIDERO - CORTE", "SALIDA PVC 4\" CON UN CODO DE 90 (SIN SIFON) - ESC. 1/5", 100)
    yP = 0.36; r4 = 0.0571; xs = c / 2
    for x0_, x1_ in ((-0.12, 0.0), (c, c + 0.55)):
        V.lleno([(x0_, yP - 0.10), (x1_, yP - 0.10), (x1_, yP), (x0_, yP)], "DET-PISO", "CONCRETO")
    hcaja = lam.relleno(V.pts([(0, yP - 0.26), (c, yP - 0.26), (c, yP), (0, yP)]), "CONCRETO-ACHURADO")
    hueco = [(a0, yP), (a0, yP - 0.10), (xs - r4, yP - 0.13), (xs - r4, yP - 0.26), (xs + r4, yP - 0.26), (xs + r4, yP - 0.13), (a0 + rj, yP - 0.10), (a0 + rj, yP)]
    hcaja.paths.add_polyline_path(V.pts(hueco), is_closed=True)
    V.poli([(0, yP - 0.26), (c, yP - 0.26), (c, yP), (0, yP)], "CONCRETO"); V.poli(hueco, "CONCRETO")
    V.lleno([(a0, yP - IN), (a0 + rj, yP - IN), (a0 + rj, yP), (a0, yP)], "DET-METAL", "MARCO-METALICO")
    yc = yP - 0.26 - r4          # eje del tubo horizontal
    tubo = [(xs - r4, yP - 0.13), (xs + r4, yP - 0.13), (xs + r4, yc + r4), (c + 0.55, yc + r4 - 0.01 * (c + 0.55 - xs)),
            (c + 0.55, yc - r4 - 0.01 * (c + 0.55 - xs)), (xs, yc - r4), (xs - r4, yc)]
    V.lleno(tubo, "DET-PVC", "DET-PVC")
    V.cota((c, yP), (c, yP - 0.10), 6, False, "0.10")
    llamadas(lam, V, [((a0 + rj / 2, yP - IN / 2), ["REJILLA AL RAS DEL PISO TERMINADO (punto bajo)"]),
                      ((xs, yP - 0.18), ["SALIDA PVC 4\" Y CODO 90 (un solo codo)"]),
                      ((c + 0.40, yc), ["TUBERIA PVC 4\" a la cuneta mas cercana, S = 1 % (minimo 0.5 %),", "llega sobre el nivel del agua + 0.05"])],
             420 + (c + 0.55) * 200 + 8, 205, 130)
    lam.notas(45, 110, "NOTAS", [
        "1. Medidas en metros; escala real 1/5. Lloraderos solo en el muro que da a area verde, @%.2f m a media altura; reemplazan a los drenes franceses." % sep_llor,
        "2. Montantes siempre de PVC 4\" (3 o 4 por lado si el area lo pide), en las esquinas de las edificaciones; dado 0.40 x 0.40 x 0.35 f'c = 140 kg/cm2 con el codo de salida.",
        "3. Canaleta: tramos de 2.44 m traslapados 0.05 con 2 filas de remaches pop 1/8\" y sellador; 2 tapas laterales por canaleta; 1 boquilla por montante.",
        "4. Sumideros solo en areas libres sin cobertura (patios, estacionamiento); nunca en areas verdes, veredas ni bajo techo.",
    ], hmm=1.8, ancho_mm=330)
    return lam


# ============================================================================================== lamina 3
def lamina_elevaciones(doc, codigo, ox, oy, P, b, alero, sep_llor):
    em, ef = P["e_muro"], P["e_fondo"]; W = b + 2 * em
    lam = B.Lamina(doc, ox, oy, 10, codigo, "DETALLES: MONTANTE EN ELEVACION Y MURO CON LLORADEROS",
                   "RECORRIDO DEL MONTANTE PVC 4\" DESDE LA CANALETA HASTA LA CUNETA Y LLORADEROS @%.2f m - ESC. 1/10" % sep_llor)
    # ---------------------------------------------------------------- montante: elevacion
    V = Vista(lam, 90, 140)
    titulo(lam, 90 + 75, 572, "MONTANTE PVC 4\" - ELEVACION", "DESDE LA CANALETA HASTA LA CUNETA - ESC. 1/10", 110)
    V.lleno([(-0.25, 0), (0, 0), (0, alero + 0.25), (-0.25, alero + 0.25)], "CONCRETO-ACHURADO", "CONCRETO")
    V.lleno([(0, alero), (0.60, alero), (0.60, alero + 0.15), (0, alero + 0.15)], "CONCRETO-ACHURADO", "CONCRETO")
    V.linea((-0.10, alero + 0.32), (0.80, alero + 0.20), "DET-METAL")
    V.poli([(0.60, alero + 0.15), (0.60, alero - 0.05), (0.85, alero - 0.05), (0.85, alero + 0.15)], "DET-METAL", cerrada=False)
    d = 0.1143; x_b = 0.725; xp = 0.03 + d / 2
    V.lleno([(x_b - d / 2, alero - 0.05), (x_b + d / 2, alero - 0.05), (x_b + d / 2, alero - 0.30), (x_b - d / 2, alero - 0.30)], "DET-PVC", "DET-PVC")
    yd = alero - 0.30 - d / 2
    V.lleno([(xp - d / 2, yd - d / 2), (x_b + d / 2, yd - d / 2), (x_b + d / 2, yd + d / 2), (xp - d / 2, yd + d / 2)], "DET-PVC", "DET-PVC")
    V.lleno([(xp - d / 2, -0.20), (xp + d / 2, -0.20), (xp + d / 2, yd - d / 2), (xp - d / 2, yd - d / 2)], "DET-PVC", "DET-PVC")
    V.lleno([(0, 0), (0.20, 0), (0.20, 1.30), (0, 1.30)], "CONCRETO-ACHURADO", "CONCRETO")
    V.lleno([(xp - d / 2, 0), (xp + d / 2, 0), (xp + d / 2, 1.30), (xp - d / 2, 1.30)], "DET-PVC", "CONCRETO-OCULTO")
    V.lleno([(-0.10, -0.35), (0.30, -0.35), (0.30, 0), (-0.10, 0)], "CONCRETO-ACHURADO", "CONCRETO")
    xc = 1.20
    V.lleno([(xp - d / 2, -0.20 - d), (xc, -0.20 - d - 0.01 * (xc - xp)), (xc, -0.20 - 0.01 * (xc - xp)), (xp + d / 2, -0.20)], "DET-PVC", "DET-PVC")
    V.linea((-0.40, 0), (xc + W + 0.30, 0), "TERRENO")
    V.lleno([(xc, -0.20 - d - 0.25), (xc + W, -0.20 - d - 0.25), (xc + W, 0), (xc + W - em, 0), (xc + W - em, -0.20 - d - 0.15),
             (xc + em, -0.20 - d - 0.15), (xc + em, 0), (xc, 0)], "CONCRETO-ACHURADO", "CONCRETO")
    for ya in (1.60, min(alero - 0.60, 1.60 + 1.50), ):
        V.rect(xp - d / 2 - 0.01, ya - 0.015, xp + d / 2 + 0.01, ya + 0.015, "MARCO-METALICO")
    for xg in (xp + 0.20, x_b - 0.15):
        V.linea((xg, yd + d / 2), (xg, alero), "MARCO-METALICO")
    V.cota((-0.25, 0), (-0.25, alero), -10, False, "%.2f" % alero)
    V.cota((0.20, 0), (0.20, 1.30), 8, False, "1.30")
    V.cota((-0.10, -0.35), (0.30, -0.35), -6, True, "0.40")
    lam.nivel(V.p(-0.40, 0), 0, "NPT", -1)
    llamadas(lam, V, [((0.80, alero + 0.05), ["CANALETA 0.25 x 0.20, S = 1 %"]),
                      ((x_b, alero - 0.20), ["BOQUILLA Ø 0.10 Y NIPLE PVC 4\""]),
                      ((xp + 0.20, yd + 0.10), ["DESVIO BAJO EL ALERO CON 2 CODOS 90", "y 2 COLGADORES F°G° (varilla 3/8\")"]),
                      ((xp + d / 2, 2.20), ["MONTANTE PVC 4\" ADOSADO AL MURO,", "ABRAZADERAS F°G° (1 cada 4.00 m, minimo 1)"]),
                      ((0.20, 0.80), ["FALSA COLUMNA 0.20 x 0.15 x 1.30"]),
                      ((0.25, -0.20), ["DADO 0.40 x 0.40 x 0.35 f'c = 140 kg/cm2", "con el codo de salida 90"]),
                      ((xc - 0.30, -0.27), ["TUBO PVC 4\" ENTERRADO HASTA LA CUNETA (max. 5 m),", "S = 1 %, sobre el nivel del agua + 0.05"])],
             90 + (1.20 + W) * 100 + 14, 535, 125)
    # ---------------------------------------------------------------- muro con lloraderos: elevacion
    Lm = 4.50; Hm = 0.60
    V = Vista(lam, 375, 450)
    titulo(lam, 375 + Lm * 50, 560, "MURO CON LLORADEROS - ELEVACION DESDE EL AREA VERDE", "TRAMO DE %.2f m - ESC. 1/10" % Lm, 140)
    V.lleno([(0, 0), (Lm, 0), (Lm, Hm), (0, Hm)], "CONCRETO-ACHURADO", "CONCRETO")
    V.linea((3.00, 0), (3.00, Hm), "DET-TECNOPOR")
    xs = [sep_llor / 2 + k * sep_llor for k in range(int(Lm / sep_llor + 1e-9))]
    for x in xs:
        V.circ((x, Hm / 2), 0.0381, "DET-PVC")
        V.poli([(x - 0.15, Hm / 2 - 0.15), (x + 0.15, Hm / 2 - 0.15), (x + 0.15, Hm / 2 + 0.15), (x - 0.15, Hm / 2 + 0.15)], "DET-GEOTEXTIL")
    V.cota((0, 0), (xs[0], 0), -6, True, "%.2f" % xs[0])
    for a, c_ in zip(xs[:-1], xs[1:]): V.cota((a, 0), (c_, 0), -6, True, "%.2f" % (c_ - a))
    V.cota((0, Hm), (3.00, Hm), 6, True, "3.00")
    llamadas(lam, V, [((xs[0], Hm / 2), ["LLORADERO PVC 3\" a media altura del muro"]),
                      ((xs[1] + 0.15, Hm / 2 + 0.15), ["CAJA FILTRANTE 0.30 x 0.30 (grava y geotextil)", "detras del muro, en el area verde"]),
                      ((3.00, Hm * 0.8), ["JUNTA DE DILATACION E = 1\" (cada 3.00 m); los", "lloraderos quedan a 0.30 m o mas de la junta"])],
             395, 425, 385)
    lam.notas(470, 330, "NOTAS", [
        "1. Medidas en metros; escala real 1/10. Altura de alero de %.2f m (editable por edificacion en el proyecto)." % alero,
        "2. Recorrido del montante: boquilla, niple, codo 90, desvio bajo el alero, codo 90, bajada adosada al muro, falsa columna, codo de",
        "   salida dentro del dado y tubo PVC 4\" a la cuneta (3 codos de 90 por montante).",
        "3. Prueba de escurrimiento con agua antes de vaciar la falsa columna; plomo +-5 mm.",
        "4. Lloraderos: N. por tramo = REDONDEAR.MAS(L / %.2f); solo donde el muro da a area verde (cuadro de lloraderos)." % sep_llor,
    ], hmm=1.8, ancho_mm=350)
    return lam


def laminas(doc, ox, oy, sep, num0, pref, P, secciones, alero=3.50, con_techo=True, con_suelo=True):
    """Agrega las 3 laminas de detalles a partir de (ox, oy), con 'sep' m entre laminas. Devuelve las laminas."""
    capas(doc)
    b = max([s.get("b_adoptado", s.get("b", P["b_int"])) for s in secciones] or [P["b_int"]])
    w5 = 841 * 5 / 1000.0 + sep
    out = [lamina_cuneta(doc, "%s-%02d" % (pref, num0), ox, oy, P, b)]
    out.append(lamina_complementos(doc, "%s-%02d" % (pref, num0 + 1), ox + w5, oy, P, b, P["llor_sep"]))
    out.append(lamina_elevaciones(doc, "%s-%02d" % (pref, num0 + 2), ox + 2 * w5, oy, P, b, alero, P["llor_sep"]))
    return out
