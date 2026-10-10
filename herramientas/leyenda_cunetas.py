"""Leyenda y especificaciones tecnicas para las laminas de secciones transversales de cunetas (CAR Varones, CUI 2705619).

Se dibuja a escala real (1 unidad = 1 m) con la misma altura de letra de las secciones del plano del proyectista
(llamadas 0.031 m, titulos 0.038 m), como BLOQUE "LEYENDA_ESPEC_CUNETAS" insertado en (0, 0): se copia y pega
al lado de las secciones, o se inserta con INSERT y se escala si la lamina tiene otra escala de impresion.
Datos: hojas CONCRETO EN CUNETAS, METRADO ACERO, METRADO DE CURADO, METRADO DE REJILLAS, METRADO JUNTA DE
DILATACION y METRADO LLORADEROS de la planilla vigente; secciones 40, 41 y 43 del perfil de cunetas.
"""
import os, sys, textwrap
import ezdxf
from ezdxf.enums import TextEntityAlignment as TA
import openpyxl

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANILLA = os.path.join(RAIZ, "insumos", "metrados_vigentes", "METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx")
SALIDA = os.path.join(RAIZ, "entregables_varones", "LEYENDA_ESPECIFICACIONES_SECCIONES_CUNETAS_CAR_VARONES.dxf")

HT, HS, HB = 0.050, 0.036, 0.028          # titulo, subtitulo, texto (m)
INTER = 1.55                              # interlineado
C_ABI, C_TAP, C_LONG, C_TRA, C_LLAM, C_TXT, C_TIT = 5, 84, 5, 6, 1, 7, 160


def datos():
    wb = openpyxl.load_workbook(PLANILLA, data_only=True)
    H = {}
    for r in wb["METRADO DE CURADO"].iter_rows(min_row=6, values_only=True):
        if r and isinstance(r[0], int) and r[3] in ("ABIERTA", "TAPADA"):
            H.setdefault(r[3], []).extend([r[6], r[7]])
    res = {}
    for r in wb["RESUMEN"].iter_rows(values_only=True):
        if r and isinstance(r[0], str) and r[0].startswith("01.04.03"):
            res[r[0]] = (r[1], r[2], r[3])
    junta = 3.00
    for r in wb["METRADO JUNTA DE DILATACION"].iter_rows(values_only=True):
        if r and isinstance(r[0], str) and r[0].startswith("Espaciamiento entre juntas"):
            junta = r[1]
    return dict(H={k: (min(v), max(v)) for k, v in H.items()}, junta=junta, res=res)


class Hoja:
    def __init__(self, blk):
        self.b = blk

    def t(self, x, y, s, h=HB, color=C_TXT, capa="LEY-TEXTO", estilo="ARIAL", al=TA.LEFT):
        e = self.b.add_text(s, height=h, dxfattribs={"layer": capa, "color": color, "style": estilo})
        e.set_placement((x, y), align=al)
        return e

    def parrafo(self, x, y, s, ancho, h=HB, sangria=""):
        """Texto partido al ancho (m); devuelve la y siguiente."""
        n = max(20, int(ancho / (h * 0.68)))
        lineas = textwrap.wrap(s, n, subsequent_indent=sangria)
        for ln in lineas:
            self.t(x, y, ln, h); y -= h * INTER
        return y

    def titulo(self, x, y, s, h=HS, ancho=None):
        self.t(x, y, s, h, C_TIT, "LEY-TITULO", "ARIAL-N")
        if ancho:
            self.b.add_line((x, y - h * 0.35), (x + ancho, y - h * 0.35), dxfattribs={"layer": "LEY-TITULO", "color": C_TIT})
        return y - h * 2.0

    def ln(self, a, b, color, capa="LEY-SIMBOLO", lw=None):
        at = {"layer": capa, "color": color}
        if lw: at["lineweight"] = lw
        self.b.add_line(a, b, dxfattribs=at)

    def poli(self, pts, color, capa="LEY-SIMBOLO", cerrada=False, lw=None):
        at = {"layer": capa, "color": color}
        if lw: at["lineweight"] = lw
        self.b.add_lwpolyline(pts, close=cerrada, dxfattribs=at)

    def relleno(self, pts, rgb, patron=None, escala=0.01, color=8):
        h = self.b.add_hatch(color=color, dxfattribs={"layer": "LEY-RELLENO"})
        if patron:
            h.set_pattern_fill(patron, scale=escala, color=color)
        else:
            h.set_solid_fill(color=color, rgb=rgb)
        h.paths.add_polyline_path(pts, is_closed=True)
        return h

    def punto(self, c, r, color):
        h = self.b.add_hatch(color=color, dxfattribs={"layer": "LEY-SIMBOLO"})
        h.paths.add_edge_path().add_arc(c, r, 0, 360)
        self.b.add_circle(c, r, dxfattribs={"layer": "LEY-SIMBOLO", "color": color})


def construir():
    D = datos(); H = D["H"]; J = D["junta"]
    doc = ezdxf.new("R2013", setup=True); doc.header["$INSUNITS"] = 6
    doc.styles.add("ARIAL", font="arial.ttf"); doc.styles.add("ARIAL-N", font="arialbd.ttf")
    for n, c in (("LEY-TEXTO", 7), ("LEY-TITULO", 160), ("LEY-SIMBOLO", 7), ("LEY-RELLENO", 8), ("LEY-MARCO", 250), ("LEY-COTA", 94)):
        doc.layers.add(n, color=c)
    blk = doc.blocks.new("LEYENDA_ESPEC_CUNETAS")
    S = Hoja(blk)

    W, X1, X2, X3 = 3.96, 0.06, 1.38, 2.70           # ancho total y origen de las 3 columnas
    AC = 1.20                                          # ancho util de cada columna
    YT = 2.12                                          # borde superior del cuadro
    # ---------------------------------------------------------------- titulo general
    S.t(W / 2, YT - 0.085, "LEYENDA Y ESPECIFICACIONES TECNICAS - SECCIONES TRANSVERSALES DE CUNETAS", HT, C_TIT, "LEY-TITULO", "ARIAL-N", TA.MIDDLE_CENTER)
    S.t(W / 2, YT - 0.150, "CAR VARONES - CUI N.° 2705619 - cunetas de concreto armado abiertas (con rejilla) y tapadas (con losa superior)", HB, C_TXT, al=TA.MIDDLE_CENTER)
    YC = YT - 0.20
    S.ln((0, YC), (W, YC), 250, "LEY-MARCO")
    for x in (X2 - 0.06, X3 - 0.06):
        S.ln((x, YC), (x, 0), 250, "LEY-MARCO")

    # ---------------------------------------------------------------- columna 1: leyenda de simbolos
    y = S.titulo(X1, YC - 0.07, "LEYENDA", ancho=0.30)
    xs, xt = X1, X1 + 0.30                              # simbolo 0.26 m de ancho; texto a su derecha
    ANT = AC - 0.30

    def fila(dibujo, txt, alto=0.10):
        nonlocal y
        yc = y - alto / 2 + HB * 0.4
        dibujo(yc)
        y2 = S.parrafo(xt, y, txt, ANT)
        y = min(y2, y - alto) - 0.035

    def concreto(color):
        def d(yc):
            pts = [(xs, yc - 0.045), (xs + 0.26, yc - 0.045), (xs + 0.26, yc + 0.045), (xs, yc + 0.045)]
            S.relleno(pts, (226, 226, 226), color=254)
            S.poli(pts, color, cerrada=True, lw=50)
        return d
    fila(concreto(C_ABI), "Concreto f'c = 175 kg/cm² - CUNETA ABIERTA con rejilla metalica movil (contorno azul)")
    fila(concreto(C_TAP), "Concreto f'c = 175 kg/cm² - CUNETA TAPADA con losa superior e = 0.10 m (contorno verde)")

    def long_(yc):
        for k in range(4): S.punto((xs + 0.035 + k * 0.063, yc), 0.012, C_LONG)
    fila(long_, "Acero longitudinal Ø 3/8\" fy = 4200 kg/cm² (barra en seccion); separacion segun cada seccion")

    def tra(yc):
        S.poli([(xs + 0.01, yc + 0.045), (xs + 0.01, yc - 0.040), (xs + 0.25, yc - 0.040), (xs + 0.25, yc + 0.045)], C_TRA, lw=35)
    fila(tra, "Acero transversal Ø 3/8\" @0.25 m: en U en la cuneta abierta; estribo cerrado (U + barra de la losa superior) en la tapada")

    def junta(yc):
        pts = [(xs + 0.115, yc - 0.05), (xs + 0.145, yc - 0.05), (xs + 0.145, yc + 0.05), (xs + 0.115, yc + 0.05)]
        S.relleno(pts, None, "AR-SAND", 0.012, 8); S.poli(pts, 7, cerrada=True)
    fila(junta, "Junta asfaltica e = 1\" entre la cuneta y el piso o vereda adyacente; junta de dilatacion e = 1\" en muros cada %.2f m" % J)

    def rejilla(yc):
        S.poli([(xs, yc + 0.012), (xs + 0.26, yc + 0.012), (xs + 0.26, yc - 0.012), (xs, yc - 0.012)], 1, cerrada=True, lw=35)
        for x in (xs, xs + 0.235):
            S.poli([(x, yc - 0.035), (x, yc - 0.012), (x + 0.025, yc - 0.012)], C_ABI, lw=25)
    fila(rejilla, "Rejilla metalica movil: platinas de 1\" x 3/16\" de canto sobre angulo de 1\" x 1\" x 3/16\", en el rebaje de 0.05 m del muro")

    def piso(yc):
        pts = [(xs, yc - 0.045), (xs + 0.26, yc - 0.045), (xs + 0.26, yc + 0.045), (xs, yc + 0.045)]
        S.relleno(pts, None, "AR-CONC", 0.012, 8); S.poli(pts, 7, cerrada=True)
    fila(piso, "Piso, vereda o losa adyacente existente o proyectada (referencia, no forma parte de la cuneta)")

    def llor(yc):
        S.poli([(xs + 0.02, yc + 0.019), (xs + 0.20, yc + 0.019), (xs + 0.20, yc - 0.019), (xs + 0.02, yc - 0.019)], 7, cerrada=True)
        S.relleno([(xs + 0.02, yc + 0.019), (xs + 0.20, yc + 0.019), (xs + 0.20, yc - 0.019), (xs + 0.02, yc - 0.019)], (180, 214, 246), color=151)
        S.b.add_circle((xs + 0.215, yc), 0.04, dxfattribs={"layer": "LEY-SIMBOLO", "color": 42})
    fila(llor, "Lloradero PVC Ø 3\" @1.50 m con filtro de grava y geotextil: solo en el muro colindante con area verde")

    def llam(yc):
        S.ln((xs + 0.01, yc - 0.03), (xs + 0.11, yc + 0.03), C_LLAM, "LEY-COTA")
        S.ln((xs + 0.11, yc + 0.03), (xs + 0.26, yc + 0.03), C_LLAM, "LEY-COTA")
        S.t(xs + 0.12, yc + 0.042, "Ø3/8\"@0.25", HB * 0.72, C_LLAM)
    fila(llam, "Rotulo de acero: diametro @ separacion en metros (Transversal / Longitudinal)")

    def cota(yc):
        S.ln((xs, yc), (xs + 0.26, yc), 94, "LEY-COTA")
        for x in (xs, xs + 0.26):
            S.ln((x - 0.012, yc - 0.012), (x + 0.012, yc + 0.012), 94, "LEY-COTA"); S.ln((x, yc - 0.03), (x, yc + 0.03), 94, "LEY-COTA")
        S.t(xs + 0.13, yc + 0.012, "0.40", HB * 0.8, 7, al=TA.BOTTOM_CENTER)
    fila(cota, "Cotas y espesores en metros; diametros de barras en pulgadas", 0.08)

    y -= 0.02
    y = S.titulo(X1, y, "NOMENCLATURA DEL PERFIL", ancho=0.62)
    for a, b in (("NCT", "nivel de la corona de la cuneta (borde superior, terreno terminado)"),
                 ("NCF", "cota de fondo interior de la cuneta"),
                 ("H", "altura interior de la cuneta = NCT - NCF (variable)"),
                 ("EM / EL", "espesor de muro / espesor de losa de fondo = 0.10 m"),
                 ("S", "pendiente longitudinal de la cuneta (%)")):
        S.t(X1, y, a, HB, C_TIT, estilo="ARIAL-N")
        y = S.parrafo(X1 + 0.17, y, b, AC - 0.17) - 0.01
    y_col1 = y

    # ---------------------------------------------------------------- columna 2: cuadro tipo y especificaciones 1-5
    y = S.titulo(X2, YC - 0.07, "CUADRO DE SECCIONES TIPO", ancho=0.66)
    cab = ["ELEMENTO", "ABIERTA", "TAPADA"]
    filas = [["Ancho interior b", "0.40", "0.40"], ["Espesor de muros EM", "0.10", "0.10"], ["Losa de fondo EL", "0.10", "0.10"],
             ["Losa superior", "-", "0.10"], ["Ancho exterior", "0.60", "0.60"],
             ["Altura interior H", "%.2f a %.2f" % H["ABIERTA"], "%.2f a %.2f" % H["TAPADA"]],
             ["Solado f'c = 100", "e = 4\"", "e = 4\""], ["Acero longitudinal", "Ø3/8\" @0.17-0.25", "Ø3/8\" @0.17-0.25"],
             ["Acero transversal", "Ø3/8\" @0.25 (U)", "Ø3/8\" @0.25 (cerrado)"], ["Rejilla movil", "si", "no"],
             ["Tapa de inspeccion", "-", "0.60 x 0.60"]]
    anchos = [0.40, 0.40, 0.40]; fh = HB * 1.75
    yy = y + HB * 0.6
    for i, fl in enumerate([cab] + filas):
        x = X2
        for j, v in enumerate(fl):
            if i == 0:
                S.t(x + anchos[j] / 2, yy - fh / 2, v, HB * 0.9, C_TIT, estilo="ARIAL-N", al=TA.MIDDLE_CENTER)
            else:
                S.t(x + (0.02 if j == 0 else anchos[j] / 2), yy - fh / 2, v, HB * 0.85, al=TA.MIDDLE_LEFT if j == 0 else TA.MIDDLE_CENTER)
            x += anchos[j]
        S.ln((X2, yy), (X2 + sum(anchos), yy), 8, "LEY-MARCO"); yy -= fh
    S.ln((X2, yy), (X2 + sum(anchos), yy), 8, "LEY-MARCO")
    x = X2
    for a in [0] + anchos:
        x += a; S.ln((x, y + HB * 0.6), (x, yy), 8, "LEY-MARCO")
    y = S.parrafo(X2, yy - HB * 1.3, "Altura interior H de cada tramo: hoja METRADO DE CURADO; separacion de las barras: rotulo de cada seccion.", AC, HB * 0.8) - HB * 1.2

    y = S.titulo(X2, y, "ESPECIFICACIONES TECNICAS", ancho=0.70)
    ESP = [
        ("1. CONCRETO", [
            "f'c = 175 kg/cm² a los 28 dias en muros, losa de fondo y losa superior de las cunetas; cemento Portland tipo I (NTP 334.009).",
            "Agregado grueso: piedra chancada de 1/2\" (tamano maximo 1/5 del espesor de 0.10 m); asentamiento de 3\" a 4\".",
            "Vaciado en capas, vibrado con vibrador de 1\" sin tocar el encofrado; losa superior monolitica con los muros."]),
        ("2. SOLADO", [
            "Concreto f'c = 100 kg/cm², e = 4\" (0.10 m), sobre el fondo refinado y compactado, antes de armar la losa de fondo."]),
        ("3. ACERO DE REFUERZO", [
            "Barras corrugadas fy = 4200 kg/cm², grado 60 (ASTM A615 / NTP 341.031); peso Ø 3/8\" = 0.56 kg/m.",
            "Las barras longitudinales se interrumpen a ambos lados de cada junta de dilatacion; no la atraviesan."]),
        ("4. RECUBRIMIENTOS", [
            "0.025 m en las caras interiores (agua) y en la losa superior; 0.04 m en las caras en contacto con el terreno."]),
        ("5. EMPALMES Y GANCHOS", [
            "Traslape de barras Ø 3/8\": 0.60 m como minimo, alternados (empalme clase B, Norma E.060, 12.15).",
            "Ganchos estandar de 90° y diametros de doblado segun la Norma E.060, capitulo 7; doblado en frio."]),
    ]
    for tit, ps in ESP:
        S.t(X2, y, tit, HB, C_TIT, estilo="ARIAL-N"); y -= HB * INTER
        for p in ps:
            y = S.parrafo(X2, y, "- " + p, AC, sangria="  ")
        y -= 0.015
    y_col2 = y

    # ---------------------------------------------------------------- columna 3: especificaciones 6-13
    y = YC - 0.07
    ESP2 = [
        ("6. ENCOFRADO Y DESENCOFRADO", [
            "Encofrado de madera o triplay, a plomo y alineado, con juntas selladas para no perder lechada.",
            "Desencofrado: costados de muros a las 24 h como minimo; fondo de la losa superior a los 7 dias."]),
        ("7. CURADO", [
            "Con agua o curador quimico (ASTM C309) durante 7 dias como minimo, desde el fraguado inicial."]),
        ("8. JUNTAS", [
            "Junta de dilatacion e = 1\" en los dos muros de la cuneta cada %.2f m y en los cambios de direccion, rellena con sellador asfaltico hasta el ras." % J,
            "Junta asfaltica e = 1\" en todo el contacto de la cuneta con el piso, vereda o losa adyacente (ver secciones)."]),
        ("9. REJILLA METALICA MOVIL (CUNETA ABIERTA)", [
            "Platinas de 1\" x 3/16\" de canto, transversales al eje, @1\" entre ejes, soldadas a un marco de angulo de 1\" x 1\" x 3/16\".",
            "Modulos removibles de 1.00 m, apoyados en el rebaje de 0.05 m del borde de los muros; anticorrosivo y esmalte."]),
        ("10. CUNETA TAPADA", [
            "Losa superior de concreto armado e = 0.10 m vaciada con los muros; tapas de inspeccion de 0.60 x 0.60 x 0.10 m donde indica la planta."]),
        ("11. LLORADEROS", [
            "Tubo PVC-U Ø 3\" (NTP 399.003) de 0.30 m @1.50 m a media altura del muro, con S = 0.5 % hacia la cuneta y filtro de grava 20-40 mm de 0.30 x 0.30 x 0.30 m envuelto en geotextil.",
            "Solo en los muros colindantes con area verde (hoja METRADO LLORADEROS)."]),
        ("12. PENDIENTE Y COTAS DE FONDO", [
            "Pendiente minima S = 0.50 % hacia la descarga; cotas de fondo (NCF) segun el perfil longitudinal de cada eje.",
            "Verificar las cotas de fondo con nivel antes de vaciar la losa de fondo."]),
        ("13. RELLENO", [
            "Material propio seleccionado en capas de 0.15 m, compactado a ambos lados a la vez al 95 % del Proctor modificado (NTP 339.141)."]),
        ("14. NORMAS", [
            "RNE: E.060 Concreto Armado, OS.060 Drenaje Pluvial Urbano, IS.010 Instalaciones Sanitarias; normas NTP citadas."]),
    ]
    for tit, ps in ESP2:
        S.t(X3, y, tit, HB, C_TIT, estilo="ARIAL-N"); y -= HB * INTER
        for p in ps:
            y = S.parrafo(X3, y, "- " + p, AC, sangria="  ")
        y -= 0.015
    y_col3 = y

    # ---------------------------------------------------------------- marco ajustado al contenido
    yb = min(y_col1, y_col2, y_col3) - 0.04
    for e in list(blk.query("LINE")):
        if e.dxf.layer == "LEY-MARCO" and abs(e.dxf.end.y) < 1e-9 and abs(e.dxf.start.x - e.dxf.end.x) < 1e-9:
            e.dxf.end = (e.dxf.end.x, yb)
    blk.add_lwpolyline([(0, yb), (W, yb), (W, YT), (0, YT)], close=True, dxfattribs={"layer": "LEY-MARCO", "color": 250, "lineweight": 50})
    msp = doc.modelspace()
    msp.add_blockref("LEYENDA_ESPEC_CUNETAS", (0, 0), dxfattribs={"layer": "0"})
    aud = doc.audit()
    doc.saveas(SALIDA)
    return SALIDA, (0, yb, W, YT), len(aud.errors)


if __name__ == "__main__":
    f, caja, err = construir()
    print(f, "caja", [round(v, 3) for v in caja], "errores", err)
