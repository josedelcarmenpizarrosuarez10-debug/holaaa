"""Agrega la partida 01.04.04 COLECTOR PLUVIAL FRONTAL a la planilla de metrados del usuario,
sin tocar lo existente. Nuevas hojas: COLECTOR TRAMOS, COLECTOR ACERO, COLECTOR TAPAS, COLECTOR INSUMOS.
Al final reinyecta las imagenes de encabezado (VML) que openpyxl descarta y compara antes/despues.
"""
import os, sys, re, copy, zipfile, shutil, io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import diseno as dz, metrado_calc as MC

ORIG = os.path.join(RAIZ, "insumos", "solange", "METRADO_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS.xlsx")
SALIDA = os.path.join(RAIZ, "entregables", "METRADO_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS_CON_COLECTOR.xlsx")
PG = "PLANILLA GENERAL DE METRADOS"
D = dz.D


def copiar_estilo(src, dst):
    dst.font = copy.copy(src.font); dst.fill = copy.copy(src.fill); dst.border = copy.copy(src.border)
    dst.alignment = copy.copy(src.alignment); dst.number_format = src.number_format


def fila_estilo(ws, r, r_ref, ncols=12):
    for c in range(1, ncols + 1):
        copiar_estilo(ws.cell(row=r_ref, column=c), ws.cell(row=r, column=c))


class Planilla:
    """Escribe filas en la PLANILLA GENERAL con el formato de las filas de referencia."""
    def __init__(self, ws, r0):
        self.ws = ws; self.r = r0
        self.REF_MADRE, self.REF_TIT, self.REF_PART, self.REF_DET = 9, 10, 11, 12
        self.refs = {}

    def madre(self, item, desc):
        fila_estilo(self.ws, self.r, self.REF_MADRE); self.ws.cell(row=self.r, column=1, value=item); self.ws.cell(row=self.r, column=2, value=desc); self.r += 1

    def titulo(self, item, desc):
        fila_estilo(self.ws, self.r, self.REF_TIT); self.ws.cell(row=self.r, column=1, value=item); self.ws.cell(row=self.r, column=2, value=desc); self.r += 1

    def partida(self, item, desc, und, detalles=None, total=None):
        """detalles: lista de (descripcion, veces, largo, ancho, alto, parcial_formula_o_None). total: formula directa para K."""
        rp = self.r; fila_estilo(self.ws, rp, self.REF_PART)
        ws = self.ws; ws.cell(row=rp, column=1, value=item); ws.cell(row=rp, column=2, value=desc); ws.cell(row=rp, column=12, value=und)
        self.r += 1
        if detalles:
            r1 = self.r
            for d in detalles:
                fila_estilo(ws, self.r, self.REF_DET)
                desc_, veces, largo, ancho, alto, parcial = d
                ws.cell(row=self.r, column=2, value=desc_)
                for col, v in ((3, veces), (4, largo), (5, ancho), (6, alto)):
                    if v is not None: ws.cell(row=self.r, column=col, value=v)
                if parcial is None:
                    f = "=C{r}" + "".join("*%s{r}" % L(c) for c, v in ((4, largo), (5, ancho), (6, alto)) if v is not None)
                    parcial = f.replace("{r}", str(self.r))
                ws.cell(row=self.r, column=10, value=parcial)
                self.r += 1
            ws.cell(row=rp, column=11, value="=SUM(J%d:J%d)" % (r1, self.r - 1))
        else:
            ws.cell(row=rp, column=11, value=total)
        self.refs[item] = rp
        return rp


def segmentos():
    return MC.segmentos()


def hoja_tramos(wb, segs):
    ws = wb.create_sheet("COLECTOR TRAMOS")
    bold = Font(name="Arial Narrow", size=12, bold=True); nor = Font(name="Arial Narrow", size=12); azul = Font(name="Arial Narrow", size=12, color="0000FF")
    fill = PatternFill("solid", fgColor="FFF2CC"); thin = Side(style="thin"); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws["A1"] = "COLECTOR PLUVIAL FRONTAL - TRAMO HOGAR DE REFUGIO (CUI 2675514): CALCULO POR TRAMOS"; ws["A1"].font = bold
    ws["A2"] = "Secciones medias por tramo. Azul = dato (de la memoria de calculo y la superficie topografica); negro = formula."; ws["A2"].font = nor
    # parametros
    par = [("Ancho interior b", D["b"], "m"), ("Espesor de muros", D["e_muro"], "m"), ("Espesor losa de fondo", D["e_fondo"], "m"), ("Espesor losa superior (normal y motos)", D["e_losa"], "m"),
           ("Espesor losa superior (camiones)", D["e_losa_camion"], "m"), ("Espesor de solado", D["e_solado"], "m"), ("Sobreancho de excavacion por lado", MC.SOBREEXC, "m"),
           ("Franja de relleno de nivelacion lado via", MC.FRANJA_RELLENO, "m"), ("Recubrimiento", MC.RECUB, "m"), ("Peso acero 3/8\"", MC.PESO["3/8"], "kg/m"), ("Peso acero 1/2\"", MC.PESO["1/2"], "kg/m"),
           ("Traslape", MC.TRASLAPE, "m"), ("Longitud de barra", MC.L_BARRA, "m"), ("Gancho de marco", 0.30, "m")]
    ws["A4"] = "PARAMETROS"; ws["A4"].font = bold
    P = {}
    for i, (n, v, u) in enumerate(par):
        r = 5 + i; ws.cell(row=r, column=1, value=n).font = nor; c = ws.cell(row=r, column=2, value=v); c.font = azul; c.number_format = "0.000"; ws.cell(row=r, column=3, value=u).font = nor
        P[n] = "$B$%d" % r
    b, em, ef, et, etc, es, sob, fr, rec, p38, p12, tr, lb, gan = [P[n] for n, _, _ in par]
    r0 = 5 + len(par) + 2
    enc = ["TRAMO", "PROG. INICIO", "PROG. FIN", "LONGITUD (m)", "ZONA", "e LOSA SUP. (m)", "ALTURA INT. h (m)", "Hz EXCAV. (m)", "NPT - TERRENO (m)", "ANCHO EXT. (m)", "ANCHO ZANJA (m)",
           "TRAZO (m2)", "EXCAVACION (m3)", "REFINE (m2)", "RELLENO LATERAL (m3)", "RELLENO FRANJA (m3)", "SOLADO (m2)", "C. LOSA FONDO (m3)", "C. MUROS (m3)", "C. LOSA SUP. (m3)", "ENCOFRADO (m2)", "ACABADO (m2)",
           "ESPAC. MARCOS (m)", "CAPAS (1 = marco unico en el eje; 2 = ext. + int.)", "DIAM. MARCOS", "N JUEGOS DE MARCOS", "PERIM. MARCO 1 (m)", "PERIM. MARCO 2 (m)", "ACERO MARCOS (kg)", "ESPAC. LONG. (m)", "N BARRAS LONG.", "ACERO LONG. (kg)"]
    for j, h in enumerate(enc):
        c = ws.cell(row=r0, column=j + 1, value=h); c.font = bold; c.fill = fill; c.border = bd; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[r0].height = 45
    for i, s in enumerate(segs):
        r = r0 + 1 + i; R = str(r)
        vals = [s["nombre"], round(s["p1"], 2), round(s["p2"], 2), "=C%s-B%s" % (R, R), s["zona"], round(s["et"], 2), round(s["h"], 3), round(s["Hz"], 3), round(s["dnpt"], 3),
                "=%s+2*%s" % (b, em), "=J%s+2*%s" % (R, sob),
                "=K%s*D%s" % (R, R), "=K%s*H%s*D%s" % (R, R, R), "=(J%s+0.10)*D%s" % (R, R), "=2*%s*H%s*D%s" % (sob, R, R), "=%s*I%s*D%s" % (fr, R, R), "=(J%s+0.10)*D%s" % (R, R),
                "=J%s*%s*D%s" % (R, ef, R), "=2*%s*G%s*D%s" % (em, R, R), "=J%s*F%s*D%s" % (R, R, R), "=D%s*(2*G%s+2*(%s+G%s+F%s)+%s)" % (R, R, ef, R, R, b), "=J%s*D%s" % (R, R),
                s["s"], s["capas"], s["marcos_dia"] + '"', "=ROUNDUP(D%s/W%s,0)" % (R, R),
                "=IF(X%s=2,2*(J%s-2*%s)+2*(%s+G%s+F%s-2*%s)+%s,2*(J%s-%s)+2*(%s/2+G%s+F%s/2)+%s)" % (R, R, rec, ef, R, R, rec, gan, R, em, ef, R, R, gan),
                "=IF(X%s=2,2*(%s+2*(%s-%s))+2*(G%s+2*(%s-%s))+%s,0)" % (R, b, em, rec, R, em, rec, gan), "=Z%s*(AA%s+AB%s)*IF(Y%s=\"1/2\"\"\",%s,%s)" % (R, R, R, R, p12, p38),
                s["sl"], "=ROUND(AA%s/AD%s,0)+IF(AB%s>0,ROUND(AB%s/AD%s,0),0)" % (R, R, R, R, R), "=AE%s*D%s*(1+%s/%s)*%s" % (R, R, tr, lb, p38)]
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v); c.border = bd
            c.font = azul if (isinstance(v, (int, float)) and not isinstance(v, bool)) else nor
            if j >= 1 and j not in (4, 24): c.number_format = "0.00" if j not in (6, 7, 8) else "0.000"
    rt = r0 + 1 + len(segs)
    ws.cell(row=rt, column=1, value="TOTAL COLECTOR").font = bold
    for j in range(3, 32):
        col = L(j + 1)
        if j in (4, 5, 6, 7, 8, 9, 10, 22, 23, 24, 26, 27, 29): continue
        c = ws.cell(row=rt, column=j + 1, value="=SUM(%s%d:%s%d)" % (col, r0 + 1, col, rt - 1)); c.font = bold; c.border = bd; c.number_format = "0.00"
    ws.column_dimensions["A"].width = 30
    for j in range(2, 33): ws.column_dimensions[L(j)].width = 13
    ws.freeze_panes = ws.cell(row=r0 + 1, column=2)
    # cajas y prolongaciones (valores de la memoria, con formulas simples)
    C = MC.cajas(); Pr = MC.prolongaciones(); rc = rt + 3
    ws.cell(row=rc, column=1, value="CAJAS Y PROLONGACIONES DE CUNETA (geometria de las laminas DP-06C y DP-07)").font = bold
    enc2 = ["ELEMENTO", "LARGO INT. (m)", "ANCHO INT. (m)", "ALTURA (m)", "Hz EXCAV. (m)", "EXCAVACION (m3)", "SOLADO (m2)", "C. LOSA FONDO (m3)", "C. MUROS (m3)", "C. LOSA SUP. (m3)", "ENCOFRADO (m2)", "ACERO 3/8 (kg)", "ACABADO (m2)", "RELLENO (m3)"]
    for j, h in enumerate(enc2):
        c = ws.cell(row=rc + 1, column=j + 1, value=h); c.font = bold; c.fill = fill; c.border = bd; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[rc + 1].height = 35
    filas = {}
    for i, k in enumerate(("CL", "CC")):
        c_ = C[k]; r = rc + 2 + i; R = str(r)
        Hz = c_["excav"] / ((c_["Li"] + 2 * D["e_muro"] + 2 * MC.SOBREEXC) * (c_["Bi"] + 2 * D["e_muro"] + 2 * MC.SOBREEXC))
        vals = [c_["nombre"], c_["Li"], c_["Bi"], round(c_["H"], 2), round(Hz, 3), "=(B%s+2*%s+2*%s)*(C%s+2*%s+2*%s)*E%s" % (R, em, sob, R, em, sob, R), "=(B%s+2*%s+0.1)*(C%s+2*%s+0.1)" % (R, em, R, em),
                round(c_["c_fondo"], 3), round(c_["c_muros"], 3), round(c_["c_losa"], 3), round(c_["encof"], 2), round(c_["acero_kg"], 1), round(c_["acabado"], 2), round(c_["relleno"], 2)]
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v); c.border = bd; c.font = azul if isinstance(v, (int, float)) else nor; c.number_format = "0.00"
        filas[k] = r
    for i, p in enumerate(Pr):
        r = rc + 4 + i; R = str(r)
        vals = ["Prolongacion cuneta %s (0.40 x H, muros 0.10)" % p["cuneta"].split(" (")[0], round(p["L"], 2), 0.40, round(p["H"], 2), round(p["H"] + 0.15, 2), "=0.90*B%s*E%s" % (R, R), "=0.70*B%s" % R,
                None, "=B%s*(0.60*0.10+2*0.10*(D%s-0.10))" % (R, R), None, "=B%s*(2*(D%s-0.10)+2*D%s)" % (R, R, R), round(p["acero_kg"], 1), "=0.60*B%s" % R, None]
        for j, v in enumerate(vals):
            if v is None: continue
            c = ws.cell(row=r, column=j + 1, value=v); c.border = bd; c.font = azul if isinstance(v, (int, float)) else nor; c.number_format = "0.00"
        filas["P%d" % i] = r
    return ws, r0, rt, filas


def hoja_acero(wb, rt_tramos, filas_cajas):
    ws = wb.create_sheet("COLECTOR ACERO")
    bold = Font(name="Arial Narrow", size=12, bold=True); nor = Font(name="Arial Narrow", size=12); azul = Font(name="Arial Narrow", size=12, color="0000FF")
    fill = PatternFill("solid", fgColor="FFF2CC"); thin = Side(style="thin"); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws["A1"] = "COLECTOR PLUVIAL FRONTAL: PLANILLA DE ACERO (despiece)"; ws["A1"].font = bold
    enc = ["ELEMENTO", "DIAM.", "FORMA", "N PIEZAS", "LONG. POR PIEZA (m)", "LONG. TOTAL (m)", "PESO (kg/m)", "PESO (kg)", "OBSERVACION"]
    for j, h in enumerate(enc):
        c = ws.cell(row=3, column=j + 1, value=h); c.font = bold; c.fill = fill; c.border = bd; c.alignment = Alignment(horizontal="center", wrap_text=True)
    T = "'COLECTOR TRAMOS'"; Rg = MC.registros(); n = Rg["n"]
    rows = [
        ("Colector: marcos cerrados (marco unico en tramo normal y motos; doble en camiones)", "3/8\" y 1/2\"", "cerrado", None, None, "=SUMPRODUCT(%s!Z%d:Z%d,%s!AA%d:AA%d+%s!AB%d:AB%d)" % (T, 22, rt_tramos - 1, T, 22, rt_tramos - 1, T, 22, rt_tramos - 1), None, "=%s!AC%d" % (T, rt_tramos), "hoja COLECTOR TRAMOS (peso segun diametro por tramo)"),
        ("Colector: barras longitudinales", "3/8\"", "recta con traslape", None, None, "=%s!AF%d/%s!$B$14" % (T, rt_tramos, T), "=%s!$B$14" % T, "=F5*G5", "incluye traslape 0.40 cada 9.00 m"),
        ("Cajas CL y CC: malla 3/8\" @0.20 ambas caras", "3/8\"", "malla", None, None, "=(%s!L%d+%s!L%d)/%s!$B$14" % (T, filas_cajas["CL"], T, filas_cajas["CC"], T), "=%s!$B$14" % T, "=F6*G6", "hoja COLECTOR TRAMOS, cuadro de cajas"),
        ("Registros: refuerzo de borde de abertura", "1/2\"", "recta", "=%d*8" % n, 1.40, "=D7*E7", "=%s!$B$15" % T, "=F7*G7", "2 barras por lado, L=1.40"),
        ("Tapas de registro: parrilla", "3/8\"", "recta", "=%d*14" % n, 0.62, "=D8*E8", "=%s!$B$14" % T, "=F8*G8", "7 + 7 barras @0.10"),
        ("Tapas de registro: asas", "3/8\" liso", "U", "=%d*2" % n, 0.40, "=D9*E9", "=%s!$B$14" % T, "=F9*G9", ""),
        ("Anclajes de contramarco", "3/8\"", "L", "=%d*8" % n, 0.20, "=D10*E10", "=%s!$B$14" % T, "=F10*G10", "soldados al angulo"),
        ("Prolongacion de cunetas Ejes 11 y 12", "3/8\"", "U + rectas", None, None, "=(%s!L%d+%s!L%d)/%s!$B$14" % (T, filas_cajas["P0"], T, filas_cajas["P1"], T), "=%s!$B$14" % T, "=F11*G11", "@0.20"),
    ]
    for i, row in enumerate(rows):
        r = 4 + i
        for j, v in enumerate(row):
            if v is None: continue
            c = ws.cell(row=r, column=j + 1, value=v); c.border = bd; c.font = azul if isinstance(v, (int, float)) else nor
            if j in (4, 5, 6, 7): c.number_format = "0.00"
    r = 4 + len(rows)
    ws.cell(row=r + 1, column=1, value="TOTAL ACERO COLECTOR Y CAJAS (partida 01.04.04.04.05)").font = bold; c = ws.cell(row=r + 1, column=8, value="=SUM(H4:H6)"); c.font = bold; c.number_format = "0.00"
    ws.cell(row=r + 2, column=1, value="TOTAL ACERO EN REGISTROS Y TAPAS (partida 01.04.04.05.06)").font = bold; c = ws.cell(row=r + 2, column=8, value="=SUM(H7:H10)"); c.font = bold; c.number_format = "0.00"
    ws.cell(row=r + 3, column=1, value="TOTAL ACERO EN PROLONGACION DE CUNETAS (partida 01.04.04.06.06)").font = bold; c = ws.cell(row=r + 3, column=8, value="=H11"); c.font = bold; c.number_format = "0.00"
    ws.cell(row=r + 4, column=1, value="TOTAL ACERO").font = bold; c = ws.cell(row=r + 4, column=8, value="=SUM(H4:H11)"); c.font = bold; c.number_format = "0.00"
    ws.column_dimensions["A"].width = 52; ws.column_dimensions["C"].width = 18; ws.column_dimensions["E"].width = 18; ws.column_dimensions["F"].width = 16; ws.column_dimensions["I"].width = 44
    return ws, {"colector": r + 1, "registros": r + 2, "cunetas": r + 3}


def hoja_tapas(wb):
    ws = wb.create_sheet("COLECTOR TAPAS")
    bold = Font(name="Arial Narrow", size=12, bold=True); nor = Font(name="Arial Narrow", size=12); azul = Font(name="Arial Narrow", size=12, color="0000FF")
    fill = PatternFill("solid", fgColor="FFF2CC"); thin = Side(style="thin"); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws["A1"] = "COLECTOR PLUVIAL FRONTAL: REGISTROS DE LIMPIEZA Y TAPAS (lamina DP-06B)"; ws["A1"].font = bold
    par = [("Numero de registros (RS-01 a RS-07 + CL + 2 en CC)", MC.registros()["n"], "und"), ("Lado de tapa", 0.68, "m"), ("Espesor de tapa", 0.08, "m"), ("Perimetro de contramarco (4 x 0.70)", 2.80, "m"),
           ("Perimetro de marco de tapa (4 x 0.68)", 2.72, "m"), ("Peso angulo L 2\"x2\"x3/16\"", 3.63, "kg/m"), ("Peso angulo L 1 1/2\"x1 1/2\"x1/8\"", 1.83, "kg/m"),
           ("Desarrollo pintado contramarco", 0.203, "m2/m"), ("Desarrollo pintado marco", 0.152, "m2/m"), ("Borde engrosado: perimetro x seccion", 3.00 * 0.15 * 0.10, "m3/und")]
    for i, (n_, v, u) in enumerate(par):
        r = 3 + i; ws.cell(row=r, column=1, value=n_).font = nor; c = ws.cell(row=r, column=2, value=v); c.font = azul; c.number_format = "0.000"; ws.cell(row=r, column=3, value=u).font = nor
    r0 = 3 + len(par) + 1
    enc = ["PARTIDA", "UND", "N VECES", "LARGO", "ANCHO", "ALTO", "PARCIAL", "OBSERVACION"]
    for j, h in enumerate(enc):
        c = ws.cell(row=r0, column=j + 1, value=h); c.font = bold; c.fill = fill; c.border = bd
    rows = [("Contramarco metalico L 2\"x2\"x3/16\" con anclajes", "und", "=$B$3", None, None, None, "=C%d", ""),
            ("Marco metalico de tapa L 1 1/2\"x1 1/2\"x1/8\"", "und", "=$B$3", None, None, None, "=C%d", ""),
            ("Angulos metalicos (kg)", "kg", "=$B$3", None, None, None, "=C%d*($B$6*$B$8+$B$7*$B$9)", "contramarco + marco"),
            ("Tapa de concreto armado 0.68 x 0.68 x 0.08", "und", "=$B$3", None, None, None, "=C%d", ""),
            ("Concreto f'c=210 en tapas", "m3", "=$B$3", "=$B$4", "=$B$4", "=$B$5", "=C%d*D%d*E%d*F%d", ""),
            ("Concreto f'c=210 en borde engrosado de abertura", "m3", "=$B$3", None, None, None, "=C%d*$B$12", "incluido en losa superior"),
            ("Pintura anticorrosiva y esmalte en angulos", "m2", "=$B$3", None, None, None, "=C%d*($B$6*$B$10+$B$7*$B$11)", "")]
    for i, row in enumerate(rows):
        r = r0 + 1 + i
        for j, v in enumerate(row):
            if v is None: continue
            if isinstance(v, str) and "%d" in v: v = v.replace("%d", str(r))
            c = ws.cell(row=r, column=j + 1, value=v); c.border = bd; c.font = nor; c.number_format = "0.00"
    ws.column_dimensions["A"].width = 52; ws.column_dimensions["H"].width = 30
    return ws, {k: r0 + 1 + i for i, k in enumerate(("contramarco", "marco", "angulos", "tapa", "conc_tapa", "borde", "pintura"))}


def hoja_insumos(wb, pg_refs):
    """Desglose de insumos por partida (rendimientos editables en azul) para los analisis de costos unitarios."""
    ws = wb.create_sheet("COLECTOR INSUMOS")
    bold = Font(name="Arial Narrow", size=12, bold=True); nor = Font(name="Arial Narrow", size=12); azul = Font(name="Arial Narrow", size=12, color="0000FF")
    fill = PatternFill("solid", fgColor="FFF2CC"); thin = Side(style="thin"); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws["A1"] = "COLECTOR PLUVIAL FRONTAL: DESGLOSE DE INSUMOS POR PARTIDA (para los analisis de costos unitarios)"; ws["A1"].font = bold
    ws["A2"] = "Rendimientos unitarios en azul (referenciales, editar segun el ACU adoptado). Metrado tomado de la PLANILLA GENERAL DE METRADOS."; ws["A2"].font = nor
    enc = ["PARTIDA", "UND", "METRADO", "INSUMO", "UND INSUMO", "CANTIDAD POR UND", "CANTIDAD TOTAL"]
    for j, h in enumerate(enc):
        c = ws.cell(row=4, column=j + 1, value=h); c.font = bold; c.fill = fill; c.border = bd
    PGq = "'%s'" % PG
    grupos = [
        ("01.04.04.04.01", "CONCRETO f'c=210 - losa de fondo", "m3", [("Cemento Portland tipo I", "bol", 9.73), ("Arena gruesa", "m3", 0.52), ("Piedra chancada 1/2\"", "m3", 0.53), ("Agua", "m3", 0.186), ("Mezcladora 9-11 p3", "hm", 0.80), ("Vibrador de concreto", "hm", 0.80), ("Operario", "hh", 0.80), ("Oficial", "hh", 0.80), ("Peon", "hh", 6.40)]),
        ("01.04.04.04.02", "CONCRETO f'c=210 - muros", "m3", [("Cemento Portland tipo I", "bol", 9.73), ("Arena gruesa", "m3", 0.52), ("Piedra chancada 1/2\"", "m3", 0.53), ("Agua", "m3", 0.186), ("Mezcladora 9-11 p3", "hm", 1.00), ("Vibrador de concreto", "hm", 1.00), ("Operario", "hh", 1.00), ("Oficial", "hh", 1.00), ("Peon", "hh", 8.00)]),
        ("01.04.04.04.03", "CONCRETO f'c=210 - losa superior", "m3", [("Cemento Portland tipo I", "bol", 9.73), ("Arena gruesa", "m3", 0.52), ("Piedra chancada 1/2\"", "m3", 0.53), ("Agua", "m3", 0.186), ("Mezcladora 9-11 p3", "hm", 0.80), ("Vibrador de concreto", "hm", 0.80), ("Operario", "hh", 0.80), ("Oficial", "hh", 0.80), ("Peon", "hh", 6.40)]),
        ("01.04.04.04.04", "ENCOFRADO Y DESENCOFRADO", "m2", [("Madera tornillo", "p2", 4.24), ("Clavos 3\"", "kg", 0.20), ("Alambre negro N 8", "kg", 0.20), ("Operario", "hh", 0.80), ("Oficial", "hh", 0.80)]),
        ("01.04.04.04.05", "ACERO DE REFUERZO fy=4200", "kg", [("Acero corrugado fy=4200 (incluye 5 % desperdicio)", "kg", 1.05), ("Alambre negro N 16", "kg", 0.06), ("Operario", "hh", 0.032), ("Oficial", "hh", 0.032)]),
        ("01.04.04.03.01", "SOLADO f'c=100 e=0.05", "m2", [("Cemento Portland tipo I", "bol", 0.30), ("Hormigon", "m3", 0.064), ("Agua", "m3", 0.01), ("Operario", "hh", 0.10), ("Peon", "hh", 0.40)]),
        ("01.04.04.02.01", "EXCAVACION MANUAL DE ZANJAS", "m3", [("Peon", "hh", 2.67), ("Herramientas manuales", "%mo", 0.03)]),
        ("01.04.04.02.03", "RELLENO COMPACTADO CON MATERIAL PROPIO", "m3", [("Agua", "m3", 0.05), ("Compactador vibratorio tipo plancha", "hm", 0.40), ("Operario", "hh", 0.40), ("Peon", "hh", 1.60)]),
        ("01.04.04.02.04", "ELIMINACION DE MATERIAL EXCEDENTE", "m3", [("Volquete 6 m3", "hm", 0.133), ("Cargador frontal", "hm", 0.033), ("Peon", "hh", 0.133)]),
        ("01.04.04.05.03", "ANGULOS METALICOS (marco y contramarco)", "kg", [("Angulo de acero (incluye corte y soldadura)", "kg", 1.05), ("Soldadura cellocord", "kg", 0.03), ("Operario", "hh", 0.10), ("Oficial", "hh", 0.10)]),
        ("01.04.04.05.07", "PINTURA ANTICORROSIVA Y ESMALTE", "m2", [("Pintura anticorrosiva", "gal", 0.08), ("Esmalte sintetico", "gal", 0.08), ("Lija y thinner", "glb", 0.05), ("Operario", "hh", 0.40)]),
        ("01.04.04.06.01", "JUNTA DE DILATACION e=1\" CON SELLADOR", "m", [("Tecnopor 1\"", "m2", 0.25), ("Sello elastomerico de poliuretano", "kg", 0.35), ("Operario", "hh", 0.20), ("Peon", "hh", 0.20)]),
        ("01.04.04.06.02", "JUNTA DE TECNOPOR e=1\"", "m", [("Tecnopor 1\"", "m2", 0.15), ("Peon", "hh", 0.10)]),
    ]
    r = 5
    for item, desc, und, ins in grupos:
        rp = pg_refs.get(item)
        for k, (inm, iu, q) in enumerate(ins):
            ws.cell(row=r, column=1, value=desc if k == 0 else "").font = bold if k == 0 else nor
            ws.cell(row=r, column=2, value=und if k == 0 else "").font = nor
            if k == 0 and rp: c = ws.cell(row=r, column=3, value="=%s!K%d" % (PGq, rp)); c.font = nor; c.number_format = "0.00"
            ws.cell(row=r, column=4, value=inm).font = nor; ws.cell(row=r, column=5, value=iu).font = nor
            c = ws.cell(row=r, column=6, value=q); c.font = azul; c.number_format = "0.000"
            c = ws.cell(row=r, column=7, value="=F%d*$C$%d" % (r, r - k)); c.font = nor; c.number_format = "0.00"
            for j in range(1, 8): ws.cell(row=r, column=j).border = bd
            r += 1
        r += 1
    ws.column_dimensions["A"].width = 44; ws.column_dimensions["D"].width = 44; ws.column_dimensions["F"].width = 18; ws.column_dimensions["G"].width = 18
    return ws


def construir():
    wb = openpyxl.load_workbook(ORIG)
    ws = wb[PG]
    segs = segmentos()
    wsT, r0, rt, filas = hoja_tramos(wb, segs)
    wsA, acero = hoja_acero(wb, rt, filas)
    wsP, tapas = hoja_tapas(wb)
    T = "'COLECTOR TRAMOS'"; A = "'COLECTOR ACERO'"; TP = "'COLECTOR TAPAS'"
    # ultima fila usada de la planilla
    ult = max(c.row for row in ws.iter_rows() for c in row if c.value is not None)
    pl = Planilla(ws, ult + 2)
    pl.madre("01.04.04", "COLECTOR PLUVIAL FRONTAL (TRAMO HOGAR DE REFUGIO - EMPALME CON CAR MUJERES)")
    pl.titulo("01.04.04.01", "TRABAJOS PRELIMINARES")
    rs = list(range(r0 + 1, rt)); cl, cc, p0, p1 = filas["CL"], filas["CC"], filas["P0"], filas["P1"]
    def det_tramos(col, desc_extra=""):
        return [("%s (%s - %s)%s" % (s["nombre"].capitalize(), "0+%06.2f" % s["p1"], "0+%06.2f" % s["p2"], desc_extra), 1, None, None, None, "=%s!%s%d" % (T, col, r)) for s, r in zip(segs, rs)]
    pl.partida("01.04.04.01.01", "LIMPIEZA MANUAL DE TERRENO", "m²", det_tramos("L") + [("Caja de llegada CL", 1, None, None, None, "=%s!G%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!G%d" % (T, cc))])
    pl.partida("01.04.04.01.02", "TRAZO, NIVELES Y REPLANTEO PRELIMINAR", "m²", det_tramos("L") + [("Caja de llegada CL", 1, None, None, None, "=%s!G%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!G%d" % (T, cc))])
    pl.titulo("01.04.04.02", "MOVIMIENTO DE TIERRAS")
    pl.partida("01.04.04.02.01", "EXCAVACIÓN MANUAL DE ZANJAS P/COLECTOR (ancho 1.60 m)", "m³", det_tramos("M") + [("Caja de llegada CL", 1, None, None, None, "=%s!F%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!F%d" % (T, cc)),
                                                                                          ("Prolongacion cuneta Eje 11", 1, None, None, None, "=%s!F%d" % (T, p0)), ("Prolongacion cuneta Eje 12", 1, None, None, None, "=%s!F%d" % (T, p1))])
    pl.partida("01.04.04.02.02", "REFINE, NIVELACIÓN Y COMPACTACIÓN EN TERRENO NORMAL", "m²", det_tramos("N") + [("Caja de llegada CL", 1, None, None, None, "=%s!G%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!G%d" % (T, cc))])
    r_rell = pl.partida("01.04.04.02.03", "RELLENO COMPACTADO CON MATERIAL PROPIO SELECCIONADO (incluye nivelacion del retiro y base de cajas)", "m³",
                        det_tramos("O", " - lateral de zanja") + det_tramos("P", " - franja de nivelacion") + [("Caja de llegada CL", 1, None, None, None, "=%s!N%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!N%d" % (T, cc))])
    r_exc = pl.refs["01.04.04.02.01"]
    pl.partida("01.04.04.02.04", "ELIMINACIÓN DE MATERIAL EXCEDENTE", "m³", [("Excavacion de zanjas y cajas", 1, None, None, None, "=K%d" % r_exc), ("Relleno compactado (se descuenta)", -1, None, None, None, "=-K%d" % r_rell)],)
    ws.cell(row=pl.refs["01.04.04.02.04"], column=11, value="=SUM(J%d:J%d)*PARAMETROS!$B$16" % (pl.refs["01.04.04.02.04"] + 1, pl.refs["01.04.04.02.04"] + 2))
    pl.titulo("01.04.04.03", "OBRAS DE CONCRETO SIMPLE")
    pl.partida("01.04.04.03.01", "CONCRETO f'c=100 kg/cm2 PARA SOLADO E=2\" (0.05 m)", "m²", det_tramos("Q") + [("Caja de llegada CL", 1, None, None, None, "=%s!G%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!G%d" % (T, cc)),
                                                                                           ("Prolongacion cuneta Eje 11", 1, None, None, None, "=%s!G%d" % (T, p0)), ("Prolongacion cuneta Eje 12", 1, None, None, None, "=%s!G%d" % (T, p1))])
    pl.titulo("01.04.04.04", "OBRAS DE CONCRETO ARMADO - COLECTOR Y CAJAS")
    pl.partida("01.04.04.04.01", "CONCRETO f'c=210 kg/cm2 EN LOSA DE FONDO", "m³", det_tramos("R") + [("Caja de llegada CL", 1, None, None, None, "=%s!H%d" % (T, cl)), ("Caja de caida CC (incluye umbral)", 1, None, None, None, "=%s!H%d" % (T, cc))])
    pl.partida("01.04.04.04.02", "CONCRETO f'c=210 kg/cm2 EN MUROS", "m³", det_tramos("S") + [("Caja de llegada CL", 1, None, None, None, "=%s!I%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!I%d" % (T, cc))])
    pl.partida("01.04.04.04.03", "CONCRETO f'c=210 kg/cm2 EN LOSA SUPERIOR (incluye bordes de registro)", "m³", det_tramos("T") + [("Caja de llegada CL", 1, None, None, None, "=%s!J%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!J%d" % (T, cc)),
                                                                                                                      ("Bordes engrosados de abertura de registros", 1, None, None, None, "=%s!G%d" % (TP, tapas["borde"])), ("Descuento de aberturas de registro 0.70 x 0.70 x 0.10", -1, None, None, None, "=-%s!$B$3*0.70*0.70*0.10" % TP)])
    pl.partida("01.04.04.04.04", "ENCOFRADO Y DESENCOFRADO NORMAL EN COLECTOR Y CAJAS", "m²", det_tramos("U") + [("Caja de llegada CL", 1, None, None, None, "=%s!K%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!K%d" % (T, cc))])
    pl.partida("01.04.04.04.05", "ACERO DE REFUERZO fy=4200 kg/cm2 EN COLECTOR Y CAJAS", "kg", None, total="=+%s!H%d" % (A, acero["colector"]))
    pl.partida("01.04.04.04.06", "ACABADO FROTACHADO Y BRUÑADO DE LOSA SUPERIOR", "m²", det_tramos("V") + [("Caja de llegada CL", 1, None, None, None, "=%s!M%d" % (T, cl)), ("Caja de caida CC", 1, None, None, None, "=%s!M%d" % (T, cc))])
    pl.partida("01.04.04.04.07", "CURADO DE CONCRETO EN COLECTOR Y CAJAS", "m²", [("Losa superior (igual al acabado)", 1, None, None, None, "=K%d" % pl.refs["01.04.04.04.06"]), ("Caras exteriores de muros (2 x altura x longitud)", 1, None, None, None, "=2*(%s!$B$7+%s!$B$8+%s!G%d)*%s!D%d" % (T, T, T, rt - 1 if False else r0 + 1, T, rt) if False else "=0.5*%s!U%d" % (T, rt))])
    pl.titulo("01.04.04.05", "REGISTROS DE LIMPIEZA Y TAPAS")
    pl.partida("01.04.04.05.01", "CONTRAMARCO METALICO L 2\"x2\"x3/16\" CON ANCLAJES", "und", None, total="=+%s!G%d" % (TP, tapas["contramarco"]))
    pl.partida("01.04.04.05.02", "MARCO METALICO DE TAPA L 1 1/2\"x1 1/2\"x1/8\"", "und", None, total="=+%s!G%d" % (TP, tapas["marco"]))
    pl.partida("01.04.04.05.03", "ANGULOS METALICOS P/MARCO Y CONTRAMARCO (incluye soldadura)", "kg", None, total="=+%s!G%d" % (TP, tapas["angulos"]))
    pl.partida("01.04.04.05.04", "TAPA DE CONCRETO ARMADO 0.68 x 0.68 x 0.08 m (incluye acero y asas)", "und", None, total="=+%s!G%d" % (TP, tapas["tapa"]))
    pl.partida("01.04.04.05.05", "CONCRETO f'c=210 kg/cm2 EN TAPAS", "m³", None, total="=+%s!G%d" % (TP, tapas["conc_tapa"]))
    pl.partida("01.04.04.05.06", "ACERO DE REFUERZO fy=4200 kg/cm2 EN TAPAS, BORDES Y ANCLAJES", "kg", None, total="=+%s!H%d" % (A, acero["registros"]))
    pl.partida("01.04.04.05.07", "PINTURA ANTICORROSIVA Y ESMALTE EN ANGULOS", "m²", None, total="=+%s!G%d" % (TP, tapas["pintura"]))
    pl.titulo("01.04.04.06", "JUNTAS, EMPALMES Y PROLONGACION DE CUNETAS")
    J = MC.juntas()
    pl.partida("01.04.04.06.01", "JUNTA DE DILATACION E=1\" CON TECNOPOR Y SELLADOR ELASTOMERICO", "m", [("Juntas cada 4.00 m (perimetro de la seccion)", J["n"], round(J["L_dilat"] / J["n"], 2), None, None, None)])
    pl.partida("01.04.04.06.02", "JUNTA DE TECNOPOR E=1\" ENTRE COLECTOR, CERCO Y PISO ADYACENTE", "m", [("Contra el cimiento del cerco (tramo pegado al cerco)", 1, round(J["L_tecnopor_cerco"], 2), None, None, None), ("Borde de losa con el piso adyacente (ambos lados, colector y cajas)", 1, round(J["L_tecnopor_piso"], 2), None, None, None)])
    pl.partida("01.04.04.06.03", "EMPALME DE CUNETA AL COLECTOR (ventana en muro y caida)", "und", [("Cunetas Ejes 01, 02, 06, 07, 11 y 12", len(dz.CUNETAS), None, None, None, "=C%d")])
    rr = pl.refs["01.04.04.06.03"] + 1; ws.cell(row=rr, column=10, value="=C%d" % rr)
    pl.partida("01.04.04.06.04", "CONCRETO f'c=210 kg/cm2 EN PROLONGACION DE CUNETAS 0.40 x H", "m³", [("Prolongacion cuneta Eje 11", 1, None, None, None, "=%s!I%d" % (T, p0)), ("Prolongacion cuneta Eje 12", 1, None, None, None, "=%s!I%d" % (T, p1))])
    pl.partida("01.04.04.06.05", "ENCOFRADO Y DESENCOFRADO EN PROLONGACION DE CUNETAS", "m²", [("Prolongacion cuneta Eje 11", 1, None, None, None, "=%s!K%d" % (T, p0)), ("Prolongacion cuneta Eje 12", 1, None, None, None, "=%s!K%d" % (T, p1))])
    pl.partida("01.04.04.06.06", "ACERO DE REFUERZO fy=4200 kg/cm2 EN PROLONGACION DE CUNETAS", "kg", None, total="=+%s!H%d" % (A, acero["cunetas"]))
    pl.partida("01.04.04.06.07", "TAPA DE CONCRETO EN PROLONGACION DE CUNETAS (losa 0.60 x 0.08)", "m²", [("Prolongacion cuneta Eje 11", 1, None, None, None, "=%s!M%d" % (T, p0)), ("Prolongacion cuneta Eje 12", 1, None, None, None, "=%s!M%d" % (T, p1))])
    hoja_insumos(wb, pl.refs)
    # RESUMEN
    wr = wb["RESUMEN"]; ultr = max(c.row for row in wr.iter_rows() for c in row if c.value is not None)
    r = ultr + 2
    def res_row(item, desc, und, rp, ref_r):
        for c in range(1, 6): copiar_estilo(wr.cell(row=ref_r, column=c), wr.cell(row=r, column=c))
        wr.cell(row=r, column=1, value=item); wr.cell(row=r, column=2, value=desc)
        if und: wr.cell(row=r, column=3, value=und); wr.cell(row=r, column=4, value="=+'%s'!K%d" % (PG, rp))
    for item, desc in [("01.04.04", "COLECTOR PLUVIAL FRONTAL (TRAMO HOGAR DE REFUGIO - EMPALME CON CAR MUJERES)")]:
        res_row(item, desc, None, None, 9); r += 1
    for rp_item in sorted(pl.refs, key=lambda k: [int(x) for x in k.split(".")]):
        pass
    for rr_ in range(ult + 2, pl.r):
        item = ws.cell(row=rr_, column=1).value; desc = ws.cell(row=rr_, column=2).value; und = ws.cell(row=rr_, column=12).value
        if not item or item == "01.04.04": continue
        if und: res_row(item, desc, und, rr_, 11)
        else: res_row(item, desc, None, None, 10)
        r += 1
    # guardar
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True); wb.save(SALIDA)
    reinyectar_vml(ORIG, SALIDA)
    return SALIDA, (ult + 2, pl.r - 1), (ultr + 2, r - 1)


# ----------------------------------------------------------------------------
def _rels_hojas(rels_xml):
    """rId -> worksheets/sheetN.xml, sin depender del orden de los atributos."""
    out = {}
    for el in re.findall(r'<Relationship [^>]*>', rels_xml):
        mi = re.search(r'Id="(rId\d+)"', el); mt = re.search(r'Target="/?(?:xl/)?(worksheets/sheet\d+\.xml)"', el)
        if mi and mt: out[mi.group(1)] = mt.group(1)
    return out


def reinyectar_vml(orig, nuevo):
    """openpyxl descarta las imagenes de encabezado (legacyDrawingHF). Se copian de vuelta."""
    zo = zipfile.ZipFile(orig); zn = zipfile.ZipFile(nuevo)
    wbx = zo.read("xl/workbook.xml").decode("utf8"); rels = zo.read("xl/_rels/workbook.xml.rels").decode("utf8")
    nombre_por_rid = dict((m[1], m[0]) for m in re.findall(r'<sheet [^>]*name="([^"]*)"[^>]*r:id="(rId\d+)"', wbx))
    target_por_rid = _rels_hojas(rels)
    hojas_orig = {nombre_por_rid[k]: v for k, v in target_por_rid.items() if k in nombre_por_rid}
    wbn = zn.read("xl/workbook.xml").decode("utf8"); relsn = zn.read("xl/_rels/workbook.xml.rels").decode("utf8")
    nombre_por_rid_n = dict((m[1], m[0]) for m in re.findall(r'<sheet [^>]*name="([^"]*)"[^>]*r:id="(rId\d+)"', wbn))
    target_por_rid_n = _rels_hojas(relsn)
    hojas_nuevo = {nombre_por_rid_n[k]: v for k, v in target_por_rid_n.items() if k in nombre_por_rid_n}
    extra = {}; parches = {}
    for nombre, tgt in hojas_orig.items():
        sx = zo.read("xl/" + tgt).decode("utf8")
        m = re.search(r'<legacyDrawingHF r:id="(rId\d+)"\s*/>', sx)
        if not m or nombre not in hojas_nuevo: continue
        relp = "xl/worksheets/_rels/" + tgt.split("/")[-1] + ".rels"
        rx = zo.read(relp).decode("utf8")
        mt = re.search(r'<Relationship Id="%s"[^>]*Target="([^"]*)"' % m.group(1), rx)
        vml = mt.group(1).replace("../", "xl/")
        extra[vml] = zo.read(vml)
        vrel = vml.replace("drawings/", "drawings/_rels/") + ".rels"
        if vrel in zo.namelist():
            extra[vrel] = zo.read(vrel)
            for img in re.findall(r'Target="([^"]*)"', zo.read(vrel).decode("utf8")):
                extra[img.replace("../", "xl/")] = zo.read(img.replace("../", "xl/"))
        parches[hojas_nuevo[nombre]] = vml
    if not parches:
        return
    tmp = nuevo + ".tmp"; zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    ct_extra = ''
    for n in zn.namelist():
        data = zn.read(n)
        if n == "[Content_Types].xml":
            s = data.decode("utf8")
            if 'Extension="vml"' not in s: s = s.replace("</Types>", '<Default Extension="vml" ContentType="application/vnd.openxmlformats-officedocument.vmlDrawing"/></Types>')
            if 'Extension="jpeg"' not in s: s = s.replace("</Types>", '<Default Extension="jpeg" ContentType="image/jpeg"/></Types>')
            if 'Extension="png"' not in s: s = s.replace("</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')
            data = s.encode("utf8")
        for tgt, vml in parches.items():
            if n == "xl/" + tgt:
                s = data.decode("utf8")
                rid = "rIdHF1"
                tag = '<legacyDrawingHF r:id="%s"/>' % rid
                if "<legacyDrawingHF" not in s:
                    for anchor in ("</headerFooter>", "/>" if False else None):
                        pass
                    if "</headerFooter>" in s: s = s.replace("</headerFooter>", "</headerFooter>" + tag, 1)
                    elif "<tableParts" in s: s = s.replace("<tableParts", tag + "<tableParts", 1)
                    elif "<extLst" in s: s = s.replace("<extLst", tag + "<extLst", 1)
                    else: s = s.replace("</worksheet>", tag + "</worksheet>")
                if 'xmlns:r=' not in s.split(">", 2)[1] + s.split(">", 2)[0]:
                    s = re.sub(r'<worksheet\b', '<worksheet xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"', s, count=1)
                data = s.encode("utf8")
                relp = "xl/worksheets/_rels/" + tgt.split("/")[-1] + ".rels"
                rel = '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/vmlDrawing" Target="../%s"/>' % (rid, vml.replace("xl/", ""))
                if relp in zn.namelist():
                    rs = zn.read(relp).decode("utf8").replace("</Relationships>", rel + "</Relationships>")
                else:
                    rs = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + rel + "</Relationships>"
                extra[relp] = rs.encode("utf8")
        if n in extra: continue
        zout.writestr(n, data)
    for n, d in extra.items(): zout.writestr(n, d)
    zout.close(); zn.close(); shutil.move(tmp, nuevo)


def comparar(orig, nuevo, fn_informe):
    """Compara celda a celda las hojas originales; informa filas y hojas nuevas."""
    wo = openpyxl.load_workbook(orig); wn = openpyxl.load_workbook(nuevo)
    lineas = ["COMPARACION ANTES / DESPUES - %s" % os.path.basename(nuevo), ""]
    difs = 0
    for ws in wo.worksheets:
        wsn = wn[ws.title]; n = 0; d = []
        for row in ws.iter_rows():
            for c in row:
                if c.value is None: continue
                n += 1
                v2 = wsn[c.coordinate].value
                if v2 != c.value: d.append((c.coordinate, c.value, v2))
        difs += len(d)
        lineas.append("Hoja %-32s celdas originales con contenido: %5d  modificadas: %d" % (ws.title, n, len(d)))
        for x in d[:20]: lineas.append("    %s: %r -> %r" % x)
    lineas.append(""); lineas.append("Hojas nuevas: " + ", ".join(s for s in wn.sheetnames if s not in wo.sheetnames))
    lineas.append("Resultado: %s" % ("SIN CAMBIOS en el contenido original" if difs == 0 else "%d celdas originales cambiaron (revisar)" % difs))
    open(fn_informe, "w", encoding="utf8").write("\n".join(lineas)); return difs, lineas


if __name__ == "__main__":
    fn, (a, b), (c, d) = construir()
    print(fn); print("PLANILLA GENERAL: filas nuevas %d a %d; RESUMEN: filas nuevas %d a %d" % (a, b, c, d))
    difs, lineas = comparar(ORIG, fn, os.path.join(RAIZ, "entregables", "METRADO_COMPARACION_ANTES_DESPUES.txt"))
    print("\n".join(lineas))
