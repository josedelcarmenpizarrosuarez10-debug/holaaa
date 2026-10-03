"""Agrega la partida 01.04.04 COLECTOR PLUVIAL FRONTAL a la planilla de metrados del proyecto,
sin tocar lo existente. Hojas nuevas, con el mismo formato de la planilla (cabecera azul con letra blanca,
Arial Narrow, celdas de dato en amarillo claro, celdas de formula en verde claro, totales en barra azul oscuro):
  COLECTOR PARAMETROS, COLECTOR MOV. TIERRAS, COLECTOR CONCRETO, COLECTOR ENCOFRADO, COLECTOR ACERO,
  COLECTOR REGISTROS Y TAPAS, COLECTOR JUNTAS Y EMPALMES, COLECTOR INSUMOS.
Cada medida lleva su sustento (lamina y criterio). La PLANILLA GENERAL y el RESUMEN reciben la partida
01.04.04 al final, con filas que apuntan a esas hojas.
Al final reinyecta las imagenes de encabezado (VML) que openpyxl descarta y compara antes/despues.
"""
import os, sys, re, copy, zipfile, shutil
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.styles.colors import Color
from openpyxl.utils import get_column_letter as L
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import diseno as dz, metrado_calc as MC

ORIG = os.path.join(RAIZ, "insumos", "solange", "METRADO_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS_v2.xlsx")
SALIDA = os.path.join(RAIZ, "entregables", "METRADO_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS_CON_COLECTOR.xlsx")
PG = "PLANILLA GENERAL DE METRADOS"
D = dz.D

# ----------------------------------------------------------------------------- formato de la planilla
FN = "Arial Narrow"
AZUL = Color(theme=4, tint=-0.249977111117893)          # cabeceras (igual a METRADO DE CURADO / METRADO ACERO)
F_CAB = PatternFill("solid", fgColor=AZUL)
F_DATO = PatternFill("solid", fgColor="FFF2CC")          # dato de entrada (planos / memoria)
F_FORM = PatternFill("solid", fgColor="F0F7E8")          # celda calculada
F_UND = PatternFill("solid", fgColor="F2F2F2")           # unidad
F_TIPO = PatternFill("solid", fgColor="E4DFEC")          # tipo / zona
F_TOT = PatternFill("solid", fgColor="F4B183")           # total de la fila
F_BARRA = PatternFill("solid", fgColor="17365D")         # barra de totales
F_SUB = PatternFill("solid", fgColor="D9EAF7")           # subtitulos
THIN = Side(style="thin"); BD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
NOMBRES = {"PAR": "COLECTOR PARAMETROS", "MT": "COLECTOR MOV. TIERRAS", "CO": "COLECTOR CONCRETO", "EN": "COLECTOR ENCOFRADO",
           "AC": "COLECTOR ACERO", "RT": "COLECTOR REGISTROS Y TAPAS", "JE": "COLECTOR JUNTAS Y EMPALMES", "IN": "COLECTOR INSUMOS"}
Q = {k: "'%s'" % v for k, v in NOMBRES.items()}


def celda(ws, r, c, v, tipo="txt", nf=None, size=12, bold=None, al="center", wrap=False):
    cell = ws.cell(row=r, column=c, value=v)
    color = None; fill = None; b = bool(bold)
    if tipo == "cab": fill = F_CAB; color = "FFFFFF"; b = True; wrap = True
    elif tipo == "barra": fill = F_BARRA; color = "FFFFFF"; b = True
    elif tipo == "dato": fill = F_DATO
    elif tipo == "form": fill = F_FORM
    elif tipo == "und": fill = F_UND
    elif tipo == "tipo": fill = F_TIPO; b = True
    elif tipo == "tot": fill = F_TOT; b = True
    elif tipo == "sub": fill = F_SUB; b = True
    elif tipo == "sust": al = "left"; wrap = True; size = min(size, 11)
    elif tipo == "auto":
        if isinstance(v, str) and v.startswith("="): fill = F_FORM
        elif isinstance(v, (int, float)): fill = F_DATO
    if bold is not None: b = bold
    cell.font = Font(name=FN, size=size, bold=b, color=color)
    if fill is not None: cell.fill = fill
    cell.border = BD
    cell.alignment = Alignment(horizontal=al, vertical="center", wrap_text=wrap)
    if nf: cell.number_format = nf
    elif isinstance(v, float) or (isinstance(v, str) and v.startswith("=")): cell.number_format = "0.00"
    return cell


def cabecera(ws, titulo, ncols, subtitulo=None):
    """Bloque de cabecera igual al de las hojas de la planilla: titulo, ENTIDAD, PROYECTO, UBICACION, FECHA."""
    ncols = max(ncols, 6)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    celda(ws, 1, 1, titulo, "cab", size=16); ws.row_dimensions[1].height = 27
    for j in range(2, ncols + 1): ws.cell(row=1, column=j).fill = F_CAB
    datos = [("ENTIDAD", "=+RESUMEN!B4", 25), ("PROYECTO", "=+RESUMEN!B5", 59), ("UBICACIÓN", "=+RESUMEN!B6", 25), ("FECHA", "=+RESUMEN!B7", 25)]
    for i, (k, f, h) in enumerate(datos):
        r = 2 + i
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2); ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=ncols)
        celda(ws, r, 1, k, "txt", size=14, bold=True); ws.cell(row=r, column=2).border = BD
        celda(ws, r, 3, f, "txt", size=14, al="left", wrap=True, nf="mmm-yy" if k == "FECHA" else "General")
        for j in range(4, ncols + 1): ws.cell(row=r, column=j).border = BD
        ws.row_dimensions[r].height = h
    r = 6
    if subtitulo:
        ws.merge_cells(start_row=7, start_column=1, end_row=7, end_column=ncols)
        celda(ws, 7, 1, subtitulo, "sub", size=12, al="left", wrap=True); ws.row_dimensions[7].height = 48
        for j in range(2, ncols + 1): ws.cell(row=7, column=j).border = BD
        r = 8
    return r + 1


def encabezado(ws, r, cols, alto=48):
    """cols: lista de (titulo, ancho, tipo, formato). Devuelve dict titulo -> letra."""
    letras = {}
    for j, (t, w, tipo, nf) in enumerate(cols):
        celda(ws, r, j + 1, t, "cab", size=12); ws.column_dimensions[L(j + 1)].width = w; letras[t] = L(j + 1)
    ws.row_dimensions[r].height = alto
    return letras


def fila(ws, r, cols, vals, alto=None):
    for j, ((t, w, tipo, nf), v) in enumerate(zip(cols, vals)):
        if v is None:
            c = ws.cell(row=r, column=j + 1); c.border = BD; continue
        celda(ws, r, j + 1, v, tipo, nf=nf)
    if alto: ws.row_dimensions[r].height = alto


def barra_total(ws, r, ncols, texto, sumas, nf="0.00"):
    """Fila de totales en barra azul oscuro. sumas: dict letra -> formula."""
    for j in range(1, ncols + 1): celda(ws, r, j, None, "barra")
    celda(ws, r, 1, texto, "barra", al="left")
    for col, f in sumas.items(): celda(ws, r, openpyxl.utils.column_index_from_string(col), f, "barra", nf=nf)
    ws.row_dimensions[r].height = 22


def subtitulo(ws, r, ncols, texto):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
    celda(ws, r, 1, texto, "sub", al="left")
    for j in range(2, ncols + 1): ws.cell(row=r, column=j).border = BD; ws.cell(row=r, column=j).fill = F_SUB
    ws.row_dimensions[r].height = 20


def nota(ws, r, ncols, texto, alto=34):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
    c = ws.cell(row=r, column=1, value=texto); c.font = Font(name=FN, size=11, italic=True); c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[r].height = alto


def prog(p):
    return "0+%06.2f" % p


# ----------------------------------------------------------------------------- PARAMETROS
PARAMETROS = [
    # clave, descripcion, valor, unidad, sustento
    ("b", "Ancho interior del colector b", D["b"], "m", "Lamina DP-04 (secciones); memoria de calculo, hoja DATOS"),
    ("em", "Espesor de muros", D["e_muro"], "m", "Lamina DP-04; memoria, hoja ESTRUCTURAL"),
    ("ef", "Espesor de losa de fondo", D["e_fondo"], "m", "Lamina DP-04"),
    ("et", "Espesor de losa superior (tramo normal y cruce de motos)", D["e_losa"], "m", "Lamina DP-04 (secciones A y B)"),
    ("etc", "Espesor de losa superior (cruce de camiones)", D["e_losa_camion"], "m", "Lamina DP-04 (seccion C); memoria, hoja ESTRUCTURAL (carga HL-93)"),
    ("es", "Espesor de solado", D["e_solado"], "m", "Lamina DP-04 y DA-02"),
    ("NPT", "Nivel de piso terminado del frente (cara superior de la losa)", D["NPT"], "msnm", "Lamina DP-02 (perfil) y plano de arquitectura"),
    ("sob", "Sobreancho de excavacion a cada lado del colector", MC.SOBREEXC, "m", "Lamina DA-01: zanja de 1.60 m (1.10 + 2 x 0.25)"),
    ("fr", "Franja de relleno de nivelacion del retiro, lado via", MC.FRANJA_RELLENO, "m", "Lamina DA-01, nota 2"),
    ("rec", "Recubrimiento del acero", MC.RECUB, "m", "Norma E.060, tabla 7.7.1 (concreto en contacto con el suelo)"),
    ("p38", "Peso de la barra de 3/8\"", MC.PESO["3/8"], "kg/m", "Igual a PARAMETROS!B10 de esta planilla"),
    ("p12", "Peso de la barra de 1/2\"", MC.PESO["1/2"], "kg/m", "Catalogo del fabricante (0.994 kg/m)"),
    ("tr", "Traslape de barras longitudinales", MC.TRASLAPE, "m", "Norma E.060, 12.15 (clase B, 3/8\"): 0.40 m"),
    ("lb", "Longitud comercial de barra", MC.L_BARRA, "m", "Igual a PARAMETROS!B11 de esta planilla"),
    ("gan", "Ganchos de cierre del marco (2 x 0.15)", MC.GANCHO, "m", "Lamina DP-08, cuadro de doblado"),
    ("esp", "Factor de esponjamiento", "=PARAMETROS!$B$16", "-", "Igual a PARAMETROS!B16 de esta planilla"),
    ("s_n", "Espaciamiento de marcos en tramo normal", 0.20, "m", "Lamina DP-04 (seccion A) y DP-08"),
    ("s_c", "Espaciamiento de marcos en cruces (motos y camiones)", 0.15, "m", "Lamina DP-04 (secciones B y C) y DP-08"),
    ("sl_n", "Espaciamiento de barras longitudinales (normal y motos)", 0.25, "m", "Lamina DP-04 y DP-08"),
    ("sl_c", "Espaciamiento de barras longitudinales (camiones)", 0.20, "m", "Lamina DP-04 (seccion C) y DP-08"),
    ("ms", "Malla de las cajas: espaciamiento 3/8\" ambas caras", MC.MALLA_S, "m", "Lamina DP-07"),
    ("mt", "Factor por traslapes y ganchos de la malla", MC.MALLA_TRASLAPE, "-", "10 % (traslape 0.40 cada 9.00 m y ganchos de esquina 0.40)"),
    ("nreg", "Numero de registros de limpieza con tapa", MC.registros()["n"], "und", "Lamina DP-01 (RS-01 a RS-07) + 1 en CL + 2 en CC = 10; hoja COLECTOR REGISTROS Y TAPAS"),
    ("tl", "Lado de la tapa de concreto", 0.68, "m", "Lamina DP-06B"),
    ("te", "Espesor de la tapa", 0.08, "m", "Lamina DP-06B"),
    ("ab", "Lado de la abertura en la losa (luz del contramarco)", 0.70, "m", "Lamina DP-06B"),
    ("pcm", "Perimetro del contramarco L 2\"x2\"x3/16\" (4 x 0.70)", 2.80, "m", "Lamina DP-06B"),
    ("pm", "Perimetro del marco de tapa L 1 1/2\"x1 1/2\"x1/8\" (4 x 0.68)", 2.72, "m", "Lamina DP-06B"),
    ("ka", "Peso del angulo L 2\"x2\"x3/16\"", MC.ANG["2x2x3/16"], "kg/m", "Catalogo del fabricante"),
    ("kb", "Peso del angulo L 1 1/2\"x1 1/2\"x1/8\"", MC.ANG["1.5x1.5x1/8"], "kg/m", "Catalogo del fabricante"),
    ("da", "Desarrollo pintado del angulo 2\"x2\" (4 caras)", 0.203, "m2/m", "4 x 0.0508 m"),
    ("db", "Desarrollo pintado del angulo 1 1/2\"x1 1/2\" (4 caras)", 0.152, "m2/m", "4 x 0.0381 m"),
    ("bp", "Borde engrosado de la abertura: perimetro medio", 3.00, "m", "Lamina DP-06B (4 x 0.75)"),
    ("bs", "Borde engrosado: seccion (0.15 x 0.10)", 0.15 * 0.10, "m2", "Lamina DP-06B"),
    ("CL_L", "Caja de llegada CL: largo interior", D["CL_largo"], "m", "Lamina DP-07"),
    ("CL_B", "Caja de llegada CL: ancho interior", D["CL_ancho"], "m", "Lamina DP-07"),
    ("CL_pz", "Caja de llegada CL: profundidad de la poza bajo el fondo del colector", D["CL_poza"], "m", "Lamina DP-07"),
    ("CF0", "Cota de fondo del colector en el arranque (0+000)", D["CF0"], "msnm", "Lamina DP-02; memoria, hoja PERFIL_FLUJO"),
    ("CL_v", "Caja de llegada CL: ancho de la ventana de llegada del colector CAR Varones", 0.80, "m", "Lamina DP-07 (corte)"),
    ("CC_L", "Caja de caida CC: largo interior de la poza", D["CC_poza_largo"], "m", "Lamina DP-07"),
    ("CC_B", "Caja de caida CC: ancho interior", D["CC_ancho"], "m", "Lamina DP-07"),
    ("CC_pz", "Caja de caida CC: profundidad de la poza bajo el fondo del receptor R-01", D["CC_poza_prof"], "m", "Lamina DP-07"),
    ("CFR", "Cota de fondo del receptor R-01 (CAR Mujeres, CUI 2717013)", D["CF_R01"], "msnm", "Memoria del colector CAR Mujeres"),
    ("NAR", "Nivel de agua en el receptor R-01", D["NA_R01"], "msnm", "Memoria del colector CAR Mujeres"),
    ("CFB", "Cota de fondo del colector en la caida (0+%06.2f)" % dz.P_BRINK, round(dz.fondo(dz.P_BRINK), 3), "msnm", "Lamina DP-02; memoria, hoja PERFIL_FLUJO"),
    ("CC_v", "Caja de caida CC: ancho de la ventana de salida al receptor", 1.50, "m", "Lamina DP-07 (corte)"),
    ("CC_ua", "Umbral de la caja de caida: ancho", 0.25, "m", "Lamina DP-07"),
    ("CC_uh", "Umbral de la caja de caida: alto", 0.40, "m", "Lamina DP-07"),
    ("jd", "Espaciamiento de juntas de dilatacion", 4.00, "m", "Lamina DP-01, nota 5; DP-03"),
    ("hmax", "Altura interior maxima del colector (para el perimetro de la junta)", 1.61, "m", "Lamina DP-02 (perfil)"),
    ("PB", "Progresiva de la caida al receptor (fin del colector)", round(dz.P_BRINK, 3), "m", "Lamina DP-01"),
    ("PB1", "Progresiva del primer quiebre (fin del tramo pegado al cerco)", round(dz.P_B1, 3), "m", "Lamina DP-01"),
]


def hoja_parametros(wb):
    ws = wb.create_sheet(NOMBRES["PAR"])
    cols = [("N°", 5, "txt", None), ("PARAMETRO", 62, "txt", None), ("VALOR", 12, "auto", "0.000"), ("UND", 8, "und", None), ("SUSTENTO (lamina / norma / criterio)", 70, "sust", None)]
    r = cabecera(ws, "COLECTOR PLUVIAL FRONTAL - PARAMETROS DE METRADO", len(cols),
                 "Tramo Hogar de Refugio Temporal (CUI 2675514), empalme con el colector de CAR Mujeres (CUI 2717013). Valores tomados de los planos DP-01 a DP-10 y DA-01 a DA-03 y de la memoria de calculo del colector. Celda amarilla = dato; verde = formula.")
    encabezado(ws, r, cols, 30)
    P = {}
    for i, (k, desc, v, u, sus) in enumerate(PARAMETROS):
        rr = r + 1 + i
        fila(ws, rr, cols, [i + 1, desc, v, u, sus]); ws.cell(row=rr, column=2).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        P[k] = "%s!$C$%d" % (Q["PAR"], rr)
    return ws, P


# ----------------------------------------------------------------------------- MOVIMIENTO DE TIERRAS
def hoja_mov_tierras(wb, segs, P):
    ws = wb.create_sheet(NOMBRES["MT"])
    cols = [("N°", 5, "txt", None), ("TRAMO", 24, "txt", None), ("ZONA", 11, "tipo", None), ("PROG. INICIO", 11, "txt", None), ("PROG. FIN", 11, "txt", None),
            ("LONGITUD (m)", 11, "auto", "0.00"), ("ALTURA INTERIOR h (m)", 11, "dato", "0.000"), ("e LOSA SUP. (m)", 10, "auto", "0.00"), ("ANCHO EXT. b + 2e (m)", 11, "form", "0.00"),
            ("ANCHO DE ZANJA (m)", 11, "form", "0.00"), ("Hz: TERRENO - FONDO DE SOLADO (m)", 13, "dato", "0.000"), ("NPT - TERRENO (m)", 11, "dato", "0.000"),
            ("LIMPIEZA Y TRAZO (m2)", 12, "form", "0.00"), ("EXCAVACION (m3)", 12, "form", "0.00"), ("REFINE Y NIVELACION (m2)", 12, "form", "0.00"),
            ("RELLENO LATERAL DE ZANJA (m3)", 12, "form", "0.00"), ("RELLENO FRANJA DE NIVELACION (m3)", 12, "form", "0.00"), ("SUSTENTO", 46, "sust", None)]
    n = len(cols)
    r = cabecera(ws, "COLECTOR PLUVIAL FRONTAL - METRADO DE MOVIMIENTO DE TIERRAS", n,
                 "Criterio (lamina DA-01): LIMPIEZA Y TRAZO = ancho de zanja x L.  EXCAVACION = ancho de zanja x Hz x L, con Hz = terreno existente (topografia) - fondo del solado.  "
                 "REFINE = (ancho exterior + 0.10) x L (fondo del solado).  RELLENO LATERAL = 2 x sobreancho x Hz x L.  RELLENO FRANJA = 1.00 x (NPT - terreno) x L (nivelacion del retiro lado via).  "
                 "h y Hz son valores medios ponderados del tramo (perfil DP-02 y topografia); el detalle cada 2.00 m esta en la memoria de calculo.")
    le = encabezado(ws, r, cols); r0 = r + 1
    b, em, es, sob, fr = P["b"], P["em"], P["es"], P["sob"], P["fr"]
    filas = []
    for i, s in enumerate(segs):
        rr = r0 + i; R = str(rr)
        vals = [i + 1, s["nombre"], s["zona"], prog(s["p1"]), prog(s["p2"]), round(s["p2"] - s["p1"], 2), s["h"], s["et"], "=%s+2*%s" % (b, em), "=I%s+2*%s" % (R, sob),
                s["Hz"], s["dnpt"], "=J%s*F%s" % (R, R), "=J%s*K%s*F%s" % (R, R, R), "=(I%s+0.10)*F%s" % (R, R), "=2*%s*K%s*F%s" % (sob, R, R), "=%s*L%s*F%s" % (fr, R, R),
                "DP-01 (planta), DP-02 (perfil: fondo y terreno), DP-04 (seccion), DA-01 (criterio)"]
        fila(ws, rr, cols, vals, 30); filas.append(rr)
    rt = r0 + len(segs)
    barra_total(ws, rt, n, "TOTAL COLECTOR (tramos)", {c: "=SUM(%s%d:%s%d)" % (c, r0, c, rt - 1) for c in "FMNOPQ"})
    # cajas
    rc = rt + 2
    subtitulo(ws, rc, n, "CAJAS DE LLEGADA (CL) Y DE CAIDA (CC) - lamina DP-07. Excavacion en planta = (largo int. + 2e + 2 x sobreancho) x (ancho int. + 2e + 2 x sobreancho); Hz = terreno - fondo del solado. Relleno = excavacion - volumen exterior de la caja (hasta el terreno).")
    cols_c = [("N°", 5, "txt", None), ("CAJA", 24, "txt", None), ("PROG.", 11, "txt", None), ("LARGO INT. (m)", 11, "auto", "0.00"), ("ANCHO INT. (m)", 11, "auto", "0.00"),
              ("ALTURA INT. H (m)", 11, "form", "0.000"), ("COTA DE PISO (msnm)", 11, "form", "0.000"), ("TERRENO (msnm)", 10, "dato", "0.000"), ("LARGO EXC. (m)", 11, "form", "0.00"),
              ("ANCHO EXC. (m)", 11, "form", "0.00"), ("Hz (m)", 13, "form", "0.000"), ("VOL. EXTERIOR CAJA (m3)", 11, "form", "0.00"),
              ("LIMPIEZA Y TRAZO (m2)", 12, "form", "0.00"), ("EXCAVACION (m3)", 12, "form", "0.00"), ("REFINE Y NIVELACION (m2)", 12, "form", "0.00"),
              ("RELLENO LATERAL (m3)", 12, "form", "0.00"), ("RELLENO FRANJA (m3)", 12, "form", "0.00"), ("SUSTENTO", 46, "sust", None)]
    encabezado(ws, rc + 1, cols_c)
    C = MC.cajas(); ps, zs = MC.terreno()
    import numpy as np
    terr = {"CL": round(float(np.interp(0.0, ps, zs)), 3), "CC": round(float(np.interp(dz.P_FIN - 1.0, ps, zs)), 3)}
    fc = {}
    for i, k in enumerate(("CL", "CC")):
        rr = rc + 2 + i; R = str(rr); c_ = C[k]
        piso = "=%s-%s" % (P["CF0"], P["CL_pz"]) if k == "CL" else "=%s-%s" % (P["CFR"], P["CC_pz"])
        vals = [i + 1, c_["nombre"], prog(0.0 if k == "CL" else dz.P_BRINK), "=%s" % P[k + "_L"], "=%s" % P[k + "_B"], "=%s-%s-G%s" % (P["NPT"], P["et"], R), piso, terr[k],
                "=D%s+2*%s+2*%s" % (R, em, sob), "=E%s+2*%s+2*%s" % (R, em, sob), "=H%s-(G%s-%s-%s)" % (R, R, P["ef"], es),
                "=(D%s+2*%s)*(E%s+2*%s)*(F%s+%s+%s+%s)" % (R, em, R, em, R, P["et"], P["ef"], es),
                "=I%s*J%s" % (R, R), "=I%s*J%s*K%s" % (R, R, R), "=(D%s+2*%s+0.10)*(E%s+2*%s+0.10)" % (R, em, R, em), "=MAX(0,N%s-L%s)" % (R, R), 0.0,
                "DP-07 (planta y cortes de la caja), DP-02 (cotas), DA-01"]
        fila(ws, rr, cols_c, vals, 30); fc[k] = rr
    rtc = rc + 4
    barra_total(ws, rtc, n, "TOTAL CAJAS", {c: "=SUM(%s%d:%s%d)" % (c, rc + 2, c, rtc - 1) for c in "MNOPQ"})
    # resumen de partidas
    rr = rtc + 2
    subtitulo(ws, rr, n, "RESUMEN PARA LA PLANILLA GENERAL (partidas 01.04.04.01 y 01.04.04.02)")
    cols_r = [("N°", 5, "txt", None), ("PARTIDA", 24, "txt", None), ("", 11, "txt", None), ("", 11, "txt", None), ("", 11, "txt", None), ("UND", 11, "und", None), ("TRAMOS", 11, "form", "0.00"), ("CAJAS", 10, "form", "0.00"), ("TOTAL", 11, "tot", "0.00")]
    res = [("LIMPIEZA MANUAL DE TERRENO / TRAZO Y REPLANTEO", "m2", "M"), ("EXCAVACION MANUAL DE ZANJAS", "m3", "N"), ("REFINE, NIVELACION Y COMPACTACION", "m2", "O"), ("RELLENO COMPACTADO (lateral + franja + cajas)", "m3", None)]
    R_ = {}
    for i, (t, u, col) in enumerate(res):
        r_ = rr + 1 + i; R = str(r_)
        if col: vals = [i + 1, t, None, None, None, u, "=%s%d" % (col, rt), "=%s%d" % (col, rtc), "=G%s+H%s" % (R, R)]
        else: vals = [i + 1, t, None, None, None, u, "=P%d+Q%d" % (rt, rt), "=P%d+Q%d" % (rtc, rtc), "=G%s+H%s" % (R, R)]
        fila(ws, r_, cols_r, vals, 22); ws.merge_cells(start_row=r_, start_column=2, end_row=r_, end_column=5); ws.cell(row=r_, column=2).alignment = Alignment(horizontal="left", vertical="center")
        R_[t] = r_
    r_ = rr + 1 + len(res); R = str(r_)
    fila(ws, r_, cols_r, [len(res) + 1, "ELIMINACION DE MATERIAL EXCEDENTE = (excavacion - relleno) x esponjamiento", None, None, None, "m3", "=(I%d-I%d)" % (rr + 2, rr + 4), "=%s" % P["esp"], "=G%s*H%s" % (R, R)], 22)
    ws.merge_cells(start_row=r_, start_column=2, end_row=r_, end_column=5); ws.cell(row=r_, column=2).alignment = Alignment(horizontal="left", vertical="center")
    nota(ws, r_ + 2, n, "Nota: las prolongaciones de las cunetas de los Ejes 11 y 12 (1.88 y 5.39 m hasta el muro del colector) no forman parte de esta partida; se metran dentro de las partidas de cunetas del proyecto.")
    ws.freeze_panes = ws.cell(row=r0, column=3)
    return ws, dict(filas=filas, rt=rt, cajas=fc, rtc=rtc, elim=r_, letras=le)


# ----------------------------------------------------------------------------- CONCRETO
def hoja_concreto(wb, segs, P, mt):
    ws = wb.create_sheet(NOMBRES["CO"])
    cols = [("N°", 5, "txt", None), ("TRAMO", 24, "txt", None), ("ZONA", 11, "tipo", None), ("LONGITUD (m)", 11, "form", "0.00"), ("ALTURA INTERIOR h (m)", 11, "form", "0.000"),
            ("e LOSA SUP. (m)", 10, "form", "0.00"), ("ANCHO EXT. (m)", 10, "form", "0.00"), ("SOLADO f'c=100 (m2)", 12, "form", "0.00"), ("LOSA DE FONDO (m3)", 12, "form", "0.00"),
            ("MUROS (m3)", 12, "form", "0.00"), ("LOSA SUPERIOR (m3)", 12, "form", "0.00"), ("ACABADO DE LOSA SUP. (m2)", 12, "form", "0.00"), ("CURADO (m2)", 12, "form", "0.00"), ("SUSTENTO", 46, "sust", None)]
    n = len(cols)
    r = cabecera(ws, "COLECTOR PLUVIAL FRONTAL - METRADO DE CONCRETO SIMPLE Y ARMADO", n,
                 "Criterio (lamina DA-02): SOLADO = (ancho exterior + 0.10) x L.  LOSA DE FONDO = ancho exterior x e fondo x L.  MUROS = 2 x e muro x h x L.  LOSA SUPERIOR = ancho exterior x e losa x L.  "
                 "ACABADO = ancho exterior x L (losa superior frotachada y brunada).  CURADO = 2 caras interiores de muros (2 x h x L) + fondo interior (b x L) + losa superior (ancho exterior x L), igual al criterio de la hoja METRADO DE CURADO.")
    encabezado(ws, r, cols); r0 = r + 1
    MT = Q["MT"]; b, em, ef, es = P["b"], P["em"], P["ef"], P["es"]
    filas = []
    for i, s in enumerate(segs):
        rr = r0 + i; R = str(rr); rm = mt["filas"][i]
        vals = [i + 1, s["nombre"], s["zona"], "=%s!F%d" % (MT, rm), "=%s!G%d" % (MT, rm), "=%s!H%d" % (MT, rm), "=%s!I%d" % (MT, rm),
                "=(G%s+0.10)*D%s" % (R, R), "=G%s*%s*D%s" % (R, ef, R), "=2*%s*E%s*D%s" % (em, R, R), "=G%s*F%s*D%s" % (R, R, R), "=G%s*D%s" % (R, R), "=(2*E%s+%s+G%s)*D%s" % (R, b, R, R),
                "DP-04 (secciones A, B, C), DP-02 (h por tramo), DA-02 (areas por metro)"]
        fila(ws, rr, cols, vals, 30); filas.append(rr)
    rt = r0 + len(segs)
    barra_total(ws, rt, n, "TOTAL COLECTOR (tramos)", {c: "=SUM(%s%d:%s%d)" % (c, r0, c, rt - 1) for c in "DHIJKLM"})
    # cajas: por elemento
    rc = rt + 2
    subtitulo(ws, rc, n, "CAJAS CL Y CC POR ELEMENTO - lamina DP-07 (dimensiones interiores de la hoja COLECTOR MOV. TIERRAS; e muro = e fondo = 0.15; losa superior e = 0.10)")
    cols_c = [("N°", 5, "txt", None), ("CAJA / ELEMENTO", 24, "txt", None), ("DETALLE", 11, "txt", None), ("LARGO (m)", 11, "auto", "0.00"), ("ANCHO (m)", 11, "auto", "0.00"), ("ALTO / ESPESOR (m)", 10, "auto", "0.000"),
              ("VECES", 10, "auto", "0"), ("SOLADO (m2)", 12, "form", "0.00"), ("LOSA DE FONDO (m3)", 12, "form", "0.00"), ("MUROS (m3)", 12, "form", "0.00"), ("LOSA SUPERIOR (m3)", 12, "form", "0.00"),
              ("ACABADO (m2)", 12, "form", "0.00"), ("CURADO (m2)", 12, "form", "0.00"), ("SUSTENTO", 46, "sust", None)]
    encabezado(ws, rc + 1, cols_c)
    rr = rc + 2; fc = {}
    for k in ("CL", "CC"):
        rm = mt["cajas"][k]; Li = "%s!D%d" % (MT, rm); Bi = "%s!E%d" % (MT, rm); H = "%s!F%d" % (MT, rm)
        r_ini = rr
        def el(desc, det, largo, ancho, alto, veces, col, sus, extra=None):
            nonlocal rr
            R = str(rr); vals = [None, desc, det, largo, ancho, alto, veces, None, None, None, None, None, None, sus]
            f = "=D%s*E%s*F%s*G%s" % (R, R, R, R) if extra is None else extra
            vals[col] = f
            fila(ws, rr, cols_c, vals, 30); ws.cell(row=rr, column=2).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True); rr += 1
        nombre = C_NOMBRES[k]
        el(nombre + ": solado", "fondo + 0.05/lado", "=%s+2*%s+0.10" % (Li, em), "=%s+2*%s+0.10" % (Bi, em), 1, 1, 7, "DP-07: solado f'c=100 e=0.05 bajo la losa de fondo", "=D%d*E%d" % (rr, rr))
        el(nombre + ": losa de fondo", "exterior x e", "=%s+2*%s" % (Li, em), "=%s+2*%s" % (Bi, em), "=%s" % ef, 1, 8, "DP-07: losa de fondo e=0.15 (ancho exterior)")
        if k == "CC":
            el(nombre + ": umbral de la poza", "0.25 x 0.40", "=%s" % Bi, "=%s" % P["CC_ua"], "=%s" % P["CC_uh"], 1, 8, "DP-07: umbral 0.25 x 0.40 en el fondo, borde de la poza")
        nmur = 2 if k == "CL" else 1
        el(nombre + ": muros largos", "exterior x e x H", "=%s+2*%s" % (Li, em), "=%s" % em, "=%s" % H, 2, 9, "DP-07: dos muros largos de e=0.15, altura interior H")
        el(nombre + ": muros cortos", "interior x e x H", "=%s" % Bi, "=%s" % em, "=%s" % H, nmur, 9, "DP-07: muro(s) de cierre; en CC el lado de llegada lo cierra el colector" if k == "CC" else "DP-07: dos muros de cierre de e=0.15")
        if k == "CL":
            el(nombre + ": descuento ventana de llegada", "ancho x alto x e", "=%s" % P["CL_v"], "=%s" % em, "=%s-%s-%s" % (P["NPT"], P["et"], P["CF0"]), -1, 9, "DP-07 (corte): ventana del colector de CAR Varones hasta la losa")
            el(nombre + ": murete del escalon de la poza", "ancho x e x desnivel", "=%s" % Bi, "=%s" % em, "=%s" % P["CL_pz"], 1, 9, "DP-07 (corte): murete e=0.15 entre el fondo del colector y el piso de la poza")
        else:
            el(nombre + ": descuento ventana de salida", "ancho x alto x e", "=%s" % P["CC_v"], "=%s" % em, "=%s+0.50-%s" % (P["NAR"], P["CFR"]), -1, 9, "DP-07 (corte): ventana de salida al receptor R-01 (0.50 m sobre el nivel de agua)")
            el(nombre + ": murete del escalon de la poza", "ancho x e x desnivel", "=%s" % Bi, "=%s" % em, "=%s-(%s-%s)" % (P["CFB"], P["CFR"], P["CC_pz"]), 1, 9, "DP-07 (corte): murete e=0.15 entre el fondo del colector y el piso de la poza")
        el(nombre + ": losa superior", "exterior x e", "=%s+2*%s" % (Li, em), "=%s+2*%s" % (Bi, em), "=%s" % P["et"], 1, 10, "DP-07: losa superior e=0.10 a nivel del piso terminado")
        el(nombre + ": descuento aberturas de registro", "0.70 x 0.70 x e", "=%s" % P["ab"], "=%s" % P["ab"], "=%s" % P["et"], -1 if k == "CL" else -2, 10, "DP-06B: %d abertura(s) de registro en la losa" % (1 if k == "CL" else 2))
        el(nombre + ": acabado de losa superior", "exterior", "=%s+2*%s" % (Li, em), "=%s+2*%s" % (Bi, em), 1, 1, 11, "DP-07: losa superior frotachada y brunada", "=D%d*E%d" % (rr, rr))
        el(nombre + ": curado", "caras int. + fondo + losa", "=2*(%s+%s)" % (Li, Bi), "=%s" % H, 1, 1, 12, "Caras interiores de muros (perimetro x H) + fondo interior + losa superior", "=D%d*E%d+%s*%s+(%s+2*%s)*(%s+2*%s)" % (rr, rr, Li, Bi, Li, em, Bi, em))
        fc[k] = (r_ini, rr - 1)
    # registros: borde engrosado y descuento de aberturas en la losa del colector
    subtitulo(ws, rr, n, "REGISTROS DE LIMPIEZA EN LA LOSA DEL COLECTOR - lamina DP-06B (borde engrosado 0.15 x 0.10 alrededor de la abertura; descuento de la abertura 0.70 x 0.70 en la losa superior)"); rr += 1
    rreg = rr
    fila(ws, rr, cols_c, [None, "Registros: borde engrosado de la abertura", "perimetro x seccion", "=%s" % P["bp"], "=%s" % P["bs"], 1, "=%s" % P["nreg"], None, None, None, "=D%d*E%d*F%d*G%d" % (rr, rr, rr, rr), None, None, "DP-06B: borde engrosado en los 10 registros (7 en la losa del colector, 1 en CL y 2 en CC)"], 30); rr += 1
    fila(ws, rr, cols_c, [None, "Registros RS-01 a RS-07: descuento de la abertura en la losa superior", "0.70 x 0.70 x e", "=%s" % P["ab"], "=%s" % P["ab"], "=%s" % P["et"], "=-(%s-3)" % P["nreg"], None, None, None, "=D%d*E%d*F%d*G%d" % (rr, rr, rr, rr), None, None, "DP-06B"], 30); rr += 1
    rtc = rr
    barra_total(ws, rtc, n, "TOTAL CAJAS Y REGISTROS", {c: "=SUM(%s%d:%s%d)" % (c, rc + 2, c, rtc - 1) for c in "HIJKLM"})
    rr = rtc + 2
    subtitulo(ws, rr, n, "RESUMEN PARA LA PLANILLA GENERAL (partidas 01.04.04.03 y 01.04.04.04)")
    cols_r = [("N°", 5, "txt", None), ("PARTIDA", 24, "txt", None), ("", 11, "txt", None), ("", 11, "txt", None), ("", 11, "txt", None), ("UND", 10, "und", None), ("TRAMOS", 10, "form", "0.00"), ("CAJAS Y REGISTROS", 12, "form", "0.00"), ("TOTAL", 12, "tot", "0.00")]
    res = [("CONCRETO f'c=100 PARA SOLADO e=0.05", "m2", "H"), ("CONCRETO f'c=210 EN LOSA DE FONDO", "m3", "I"), ("CONCRETO f'c=210 EN MUROS", "m3", "J"), ("CONCRETO f'c=210 EN LOSA SUPERIOR", "m3", "K"),
           ("ACABADO FROTACHADO Y BRUÑADO DE LOSA SUPERIOR", "m2", "L"), ("CURADO DE CONCRETO", "m2", "M")]
    R_ = {}
    for i, (t, u, col) in enumerate(res):
        r_ = rr + 1 + i; R = str(r_)
        fila(ws, r_, cols_r, [i + 1, t, None, None, None, u, "=%s%d" % (col, rt), "=%s%d" % (col, rtc), "=G%s+H%s" % (R, R)], 22)
        ws.merge_cells(start_row=r_, start_column=2, end_row=r_, end_column=5); ws.cell(row=r_, column=2).alignment = Alignment(horizontal="left", vertical="center")
        R_[col] = r_
    ws.freeze_panes = ws.cell(row=r0, column=3)
    return ws, dict(filas=filas, rt=rt, cajas=fc, rtc=rtc, reg=rreg, res=R_)


C_NOMBRES = {"CL": "Caja de llegada CL", "CC": "Caja de caida CC"}


# ----------------------------------------------------------------------------- ENCOFRADO
def hoja_encofrado(wb, segs, P, mt):
    ws = wb.create_sheet(NOMBRES["EN"])
    cols = [("N°", 5, "txt", None), ("TRAMO", 24, "txt", None), ("ZONA", 11, "tipo", None), ("LONGITUD (m)", 11, "form", "0.00"), ("ALTURA INTERIOR h (m)", 11, "form", "0.000"),
            ("e LOSA SUP. (m)", 10, "form", "0.00"), ("ANCHO INT. b (m)", 10, "form", "0.00"), ("CARAS INTERIORES DE MUROS 2 x h x L (m2)", 13, "form", "0.00"),
            ("CARAS EXTERIORES 2 x (e fondo + h + e losa) x L (m2)", 14, "form", "0.00"), ("FONDO DE LOSA SUPERIOR b x L (m2)", 13, "form", "0.00"), ("TOTAL ENCOFRADO (m2)", 12, "tot", "0.00"), ("SUSTENTO", 46, "sust", None)]
    n = len(cols)
    r = cabecera(ws, "COLECTOR PLUVIAL FRONTAL - METRADO DE ENCOFRADO Y DESENCOFRADO", n,
                 "Criterio (lamina DA-02): se encofran las dos caras interiores de los muros, las dos caras exteriores en toda la altura del cajon (losa de fondo + muro + losa superior) y el fondo de la losa superior (ancho interior b). "
                 "La losa de fondo se vacia sobre el solado y la cara superior de la losa queda libre (acabado).")
    encabezado(ws, r, cols); r0 = r + 1
    MT = Q["MT"]; b, em, ef = P["b"], P["em"], P["ef"]
    filas = []
    for i, s in enumerate(segs):
        rr = r0 + i; R = str(rr); rm = mt["filas"][i]
        vals = [i + 1, s["nombre"], s["zona"], "=%s!F%d" % (MT, rm), "=%s!G%d" % (MT, rm), "=%s!H%d" % (MT, rm), "=%s" % b,
                "=2*E%s*D%s" % (R, R), "=2*(%s+E%s+F%s)*D%s" % (ef, R, R, R), "=G%s*D%s" % (R, R), "=SUM(H%s:J%s)" % (R, R), "DP-04 (secciones), DA-02 (areas por metro)"]
        fila(ws, rr, cols, vals, 30); filas.append(rr)
    rt = r0 + len(segs)
    barra_total(ws, rt, n, "TOTAL COLECTOR (tramos)", {c: "=SUM(%s%d:%s%d)" % (c, r0, c, rt - 1) for c in "DHIJK"})
    rc = rt + 2
    subtitulo(ws, rc, n, "CAJAS CL Y CC - lamina DP-07: caras interiores y exteriores de muros (perimetro x H, dos caras), fondo de la losa superior (interior) y, en CC, caras del umbral y del murete de la poza")
    cols_c = [("N°", 5, "txt", None), ("CAJA / ELEMENTO", 24, "txt", None), ("DETALLE", 11, "txt", None), ("LARGO (m)", 11, "auto", "0.00"), ("ALTO (m)", 11, "auto", "0.000"), ("CARAS", 10, "auto", "0"), ("", 10, "txt", None), ("", 13, "txt", None), ("", 14, "txt", None), ("", 13, "txt", None), ("AREA (m2)", 12, "form", "0.00"), ("SUSTENTO", 46, "sust", None)]
    encabezado(ws, rc + 1, cols_c)
    rr = rc + 2; fc = {}
    for k in ("CL", "CC"):
        rm = mt["cajas"][k]; Li = "%s!D%d" % (MT, rm); Bi = "%s!E%d" % (MT, rm); H = "%s!F%d" % (MT, rm); r_ini = rr
        def el(desc, det, largo, alto, caras, sus):
            nonlocal rr
            fila(ws, rr, cols_c, [None, desc, det, largo, alto, caras, None, None, None, None, "=D%d*E%d*F%d" % (rr, rr, rr), sus], 30)
            ws.cell(row=rr, column=2).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True); rr += 1
        nm = C_NOMBRES[k]
        el(nm + ": muros, cara interior y exterior", "perimetro int. x H", "=2*(%s+%s)" % (Li, Bi), "=%s" % H, 2, "DP-07: muros e=0.15 encofrados por ambas caras")
        el(nm + ": fondo de la losa superior", "interior", "=%s" % Li, "=%s" % Bi, 1, "DP-07: losa superior e=0.10 encofrada por debajo")
        if k == "CC":
            el(nm + ": caras del umbral de la poza", "2 caras x ancho", "=%s" % Bi, "=%s" % P["CC_uh"], 2, "DP-07: umbral 0.25 x 0.40")
            el(nm + ": cara del murete de la poza", "ancho x desnivel", "=%s" % Bi, "=%s-(%s-%s)" % (P["CFB"], P["CFR"], P["CC_pz"]), 1, "DP-07 (corte): murete entre el fondo del colector y el piso de la poza")
        else:
            el(nm + ": cara del murete de la poza", "ancho x desnivel", "=%s" % Bi, "=%s" % P["CL_pz"], 1, "DP-07 (corte): murete entre el fondo del colector y el piso de la poza")
        fc[k] = (r_ini, rr - 1)
    rtc = rr
    barra_total(ws, rtc, n, "TOTAL CAJAS", {"K": "=SUM(K%d:K%d)" % (rc + 2, rtc - 1)})
    rr = rtc + 2
    subtitulo(ws, rr, n, "RESUMEN PARA LA PLANILLA GENERAL (partida 01.04.04.04.04)")
    cols_r = [("N°", 5, "txt", None), ("PARTIDA", 24, "txt", None), ("", 11, "txt", None), ("", 11, "txt", None), ("", 11, "txt", None), ("UND", 10, "und", None), ("TRAMOS", 10, "form", "0.00"), ("CAJAS", 13, "form", "0.00"), ("TOTAL", 14, "tot", "0.00")]
    r_ = rr + 1
    fila(ws, r_, cols_r, [1, "ENCOFRADO Y DESENCOFRADO NORMAL EN COLECTOR Y CAJAS", None, None, None, "m2", "=K%d" % rt, "=K%d" % rtc, "=G%d+H%d" % (r_, r_)], 22)
    ws.merge_cells(start_row=r_, start_column=2, end_row=r_, end_column=5); ws.cell(row=r_, column=2).alignment = Alignment(horizontal="left", vertical="center")
    ws.freeze_panes = ws.cell(row=r0, column=3)
    return ws, dict(filas=filas, rt=rt, cajas=fc, rtc=rtc, res=r_)


# ----------------------------------------------------------------------------- ACERO
def hoja_acero(wb, segs, P, mt):
    ws = wb.create_sheet(NOMBRES["AC"])
    cols = [("N°", 5, "txt", None), ("TRAMO", 24, "txt", None), ("ZONA", 11, "tipo", None), ("LONGITUD (m)", 10, "form", "0.00"), ("ALTURA INTERIOR h (m)", 10, "form", "0.000"), ("e LOSA SUP. (m)", 9, "form", "0.00"), ("ANCHO EXT. (m)", 9, "form", "0.00"),
            ("ESPAC. MARCOS s (m)", 9, "form", "0.00"), ("CAPAS (1 = marco unico; 2 = ext. + int.)", 11, "dato", "0"), ("DIAM. MARCOS", 9, "tipo", None), ("N° DE JUEGOS (L / s, redondeado arriba)", 11, "form", "0"),
            ("PERIMETRO MARCO 1 (m)", 11, "form", "0.000"), ("PERIMETRO MARCO 2 (m)", 11, "form", "0.000"), ("LONGITUD DE MARCOS (m)", 11, "form", "0.00"), ("PESO (kg/m)", 9, "form", "0.000"), ("ACERO EN MARCOS (kg)", 11, "form", "0.00"),
            ("ESPAC. LONGIT. (m)", 9, "form", "0.00"), ("N° BARRAS LONGIT. (perimetro / espac.)", 11, "form", "0"), ("LONGITUD LONGIT. CON TRASLAPE (m)", 12, "form", "0.00"), ("ACERO LONGIT. 3/8\" (kg)", 11, "form", "0.00"), ("TOTAL (kg)", 11, "tot", "0.00"), ("SUSTENTO", 44, "sust", None)]
    n = len(cols)
    r = cabecera(ws, "COLECTOR PLUVIAL FRONTAL - METRADO DE ACERO DE REFUERZO fy=4200 kg/cm2", n,
                 "Criterio (laminas DP-04 y DP-08, norma E.060 14.3.4): tramo normal y cruce de motos llevan un solo marco cerrado en el eje de muros y losas (perimetro = 2 x (ancho ext. - e) + 2 x (e fondo/2 + h + e losa/2) + ganchos); "
                 "el cruce de camiones lleva marco exterior + marco interior de 1/2\" (perimetros con recubrimiento 0.04). Barras longitudinales 3/8\" en cada marco, con traslape de 0.40 cada 9.00 m. Peso: 3/8\" = 0.56 kg/m, 1/2\" = 0.994 kg/m.")
    encabezado(ws, r, cols, 60); r0 = r + 1
    MT = Q["MT"]; b, em, ef, rec, gan, p38, p12, tr, lb = P["b"], P["em"], P["ef"], P["rec"], P["gan"], P["p38"], P["p12"], P["tr"], P["lb"]
    filas = []
    for i, s in enumerate(segs):
        rr = r0 + i; R = str(rr); rm = mt["filas"][i]
        sp = "=%s" % (P["s_n"] if s["zona"] == "NORMAL" else P["s_c"]); sl = "=%s" % (P["sl_c"] if s["zona"] == "CAMION" else P["sl_n"])
        vals = [i + 1, s["nombre"], s["zona"], "=%s!F%d" % (MT, rm), "=%s!G%d" % (MT, rm), "=%s!H%d" % (MT, rm), "=%s!I%d" % (MT, rm), sp, s["capas"], s["marcos_dia"] + '"', "=ROUNDUP(D%s/H%s,0)" % (R, R),
                "=IF(I%s=2,2*(G%s-2*%s)+2*(%s+E%s+F%s-2*%s)+%s,2*(G%s-%s)+2*(%s/2+E%s+F%s/2)+%s)" % (R, R, rec, ef, R, R, rec, gan, R, em, ef, R, R, gan),
                "=IF(I%s=2,2*(%s+2*(%s-%s))+2*(E%s+2*(%s-%s))+%s,0)" % (R, b, em, rec, R, em, rec, gan),
                "=K%s*(L%s+M%s)" % (R, R, R), "=IF(J%s=\"1/2\"\"\",%s,%s)" % (R, p12, p38), "=N%s*O%s" % (R, R),
                sl, "=ROUND(L%s/Q%s,0)+IF(M%s>0,ROUND(M%s/Q%s,0),0)" % (R, R, R, R, R), "=R%s*D%s*(1+%s/%s)" % (R, R, tr, lb), "=S%s*%s" % (R, p38), "=P%s+T%s" % (R, R),
                "DP-04 (seccion %s), DP-08 (cuadro de doblado), DA-03" % {"NORMAL": "A", "MOTOS": "B", "CAMION": "C"}[s["zona"]]]
        fila(ws, rr, cols, vals, 30); filas.append(rr)
    rt = r0 + len(segs)
    barra_total(ws, rt, n, "TOTAL COLECTOR (tramos)", {c: "=SUM(%s%d:%s%d)" % (c, r0, c, rt - 1) for c in "DNPSTU"})
    # cajas: malla por paño
    rc = rt + 2
    subtitulo(ws, rc, n, "CAJAS CL Y CC - lamina DP-07: malla 3/8\" @0.20 en ambas caras de losas y muros. Por paño: barras = (L1 / s + 1) x L2 + (L2 / s + 1) x L1, por el numero de caras y el factor de traslapes y ganchos")
    cols_c = [("N°", 5, "txt", None), ("CAJA / PAÑO", 24, "txt", None), ("DETALLE", 11, "txt", None), ("L1 (m)", 10, "auto", "0.00"), ("L2 (m)", 10, "auto", "0.000"), ("ESPAC. s (m)", 9, "form", "0.00"), ("CARAS", 9, "auto", "0"), ("PAÑOS IGUALES", 9, "auto", "0"),
              ("BARRAS (m)", 11, "form", "0.00"), ("FACTOR TRASLAPE", 9, "form", "0.00"), ("PESO (kg/m)", 11, "form", "0.000"), ("", 11, "txt", None), ("", 11, "txt", None), ("", 11, "txt", None), ("", 9, "txt", None),
              ("", 11, "txt", None), ("", 9, "txt", None), ("", 11, "txt", None), ("", 12, "txt", None), ("", 11, "txt", None), ("ACERO (kg)", 11, "tot", "0.00"), ("SUSTENTO", 44, "sust", None)]
    encabezado(ws, rc + 1, cols_c, 60)
    rr = rc + 2; fc = {}
    for k in ("CL", "CC"):
        rm = mt["cajas"][k]; Li = "%s!D%d" % (MT, rm); Bi = "%s!E%d" % (MT, rm); H = "%s!F%d" % (MT, rm); r_ini = rr
        def el(desc, det, l1, l2, caras, panos, sus):
            nonlocal rr
            R = str(rr)
            fila(ws, rr, cols_c, [None, desc, det, l1, l2, "=%s" % P["ms"], caras, panos, "=((D%s/F%s+1)*E%s+(E%s/F%s+1)*D%s)*G%s*H%s" % (R, R, R, R, R, R, R, R), "=%s" % P["mt"], "=%s" % p38] + [None] * 9 + ["=I%s*J%s*K%s" % (R, R, R), sus], 30)
            ws.cell(row=rr, column=2).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True); rr += 1
        nm = C_NOMBRES[k]
        el(nm + ": losa de fondo", "exterior", "=%s+2*%s" % (Li, em), "=%s+2*%s" % (Bi, em), 2, 1, "DP-07: malla 3/8\" @0.20 ambas caras")
        el(nm + ": losa superior", "exterior", "=%s+2*%s" % (Li, em), "=%s+2*%s" % (Bi, em), 2, 1, "DP-07: malla 3/8\" @0.20 ambas caras")
        el(nm + ": muros largos", "exterior x H", "=%s+2*%s" % (Li, em), "=%s" % H, 2, 2, "DP-07: dos muros largos, malla ambas caras")
        el(nm + ": muros cortos", "interior x H", "=%s" % Bi, "=%s" % H, 2, 2 if k == "CL" else 1, "DP-07: muro(s) de cierre, malla ambas caras")
        fc[k] = (r_ini, rr - 1)
    rtc = rr
    barra_total(ws, rtc, n, "TOTAL CAJAS", {"U": "=SUM(U%d:U%d)" % (rc + 2, rtc - 1)})
    # registros y tapas
    rg = rtc + 2
    subtitulo(ws, rg, n, "REGISTROS DE LIMPIEZA Y TAPAS - lamina DP-06B: refuerzo de borde de la abertura, parrilla de la tapa, asas y anclajes del contramarco (cantidad de registros de la hoja COLECTOR REGISTROS Y TAPAS)")
    cols_g = [("N°", 5, "txt", None), ("ELEMENTO", 24, "txt", None), ("DIAM.", 11, "tipo", None), ("FORMA", 10, "txt", None), ("PIEZAS POR REGISTRO", 10, "auto", "0"), ("REGISTROS", 9, "form", "0"), ("LONG. POR PIEZA (m)", 9, "auto", "0.00"), ("LONG. TOTAL (m)", 9, "form", "0.00"), ("PESO (kg/m)", 11, "form", "0.000")] + [("", 9, "txt", None)] * 11 + [("ACERO (kg)", 11, "tot", "0.00"), ("SUSTENTO", 44, "sust", None)]
    encabezado(ws, rg + 1, cols_g, 40)
    reg = [("Refuerzo de borde de la abertura", '1/2"', "recta", 8, 1.40, p12, "DP-06B: 2 barras de 1/2\" por lado, L = 1.40"),
           ("Parrilla de la tapa de concreto", '3/8"', "recta", 14, 0.62, p38, "DP-06B: 7 + 7 barras 3/8\" @0.10"),
           ("Asas de la tapa", '3/8" liso', "U", 2, 0.40, p38, "DP-06B: 2 asas de 0.40 desarrollado"),
           ("Anclajes del contramarco", '3/8"', "L", 8, 0.20, p38, "DP-06B: 8 anclajes de 0.20 soldados al angulo")]
    rr = rg + 2
    for i, (desc, dia, forma, piezas, lp, peso, sus) in enumerate(reg):
        R = str(rr)
        fila(ws, rr, cols_g, [i + 1, desc, dia, forma, piezas, "=%s" % P["nreg"], lp, "=E%s*F%s*G%s" % (R, R, R), "=%s" % peso] + [None] * 11 + ["=H%s*I%s" % (R, R), sus], 30)
        ws.cell(row=rr, column=2).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True); rr += 1
    rtg = rr
    barra_total(ws, rtg, n, "TOTAL REGISTROS Y TAPAS", {"U": "=SUM(U%d:U%d)" % (rg + 2, rtg - 1)})
    # resumen
    rr = rtg + 2
    subtitulo(ws, rr, n, "RESUMEN PARA LA PLANILLA GENERAL (partidas 01.04.04.04.05 y 01.04.04.05.06)")
    cols_r = [("N°", 5, "txt", None), ("PARTIDA", 24, "txt", None), ("", 11, "txt", None), ("", 10, "txt", None), ("", 10, "txt", None), ("UND", 9, "und", None), ("3/8\" (kg)", 9, "form", "0.00"), ("1/2\" (kg)", 9, "form", "0.00"), ("TOTAL (kg)", 11, "tot", "0.00")]
    r1 = rr + 1
    fila(ws, r1, cols_r, [1, "ACERO DE REFUERZO EN COLECTOR Y CAJAS", None, None, None, "kg", "=SUMIF(J%d:J%d,\"3/8\"\"\",P%d:P%d)+T%d+U%d" % (r0, rt - 1, r0, rt - 1, rt, rtc), "=SUMIF(J%d:J%d,\"1/2\"\"\",P%d:P%d)" % (r0, rt - 1, r0, rt - 1), "=U%d+U%d" % (rt, rtc)], 22)
    r2 = rr + 2
    fila(ws, r2, cols_r, [2, "ACERO DE REFUERZO EN TAPAS, BORDES Y ANCLAJES", None, None, None, "kg", "=SUMIF(C%d:C%d,\"3/8*\",U%d:U%d)" % (rg + 2, rtg - 1, rg + 2, rtg - 1), "=SUMIF(C%d:C%d,\"1/2*\",U%d:U%d)" % (rg + 2, rtg - 1, rg + 2, rtg - 1), "=U%d" % rtg], 22)
    for r_ in (r1, r2):
        ws.merge_cells(start_row=r_, start_column=2, end_row=r_, end_column=5); ws.cell(row=r_, column=2).alignment = Alignment(horizontal="left", vertical="center")
    ws.freeze_panes = ws.cell(row=r0, column=3)
    return ws, dict(filas=filas, rt=rt, cajas=fc, rtc=rtc, rtg=rtg, colector=r1, registros=r2)


# ----------------------------------------------------------------------------- REGISTROS Y TAPAS
def hoja_registros(wb, P):
    ws = wb.create_sheet(NOMBRES["RT"])
    cols = [("N°", 5, "txt", None), ("REGISTRO", 16, "txt", None), ("PROGRESIVA", 12, "txt", None), ("UBICACION", 40, "txt", None), ("TAPA 0.68 x 0.68 (und)", 12, "auto", "0"), ("SUSTENTO", 50, "sust", None)]
    n = len(cols)
    r = cabecera(ws, "COLECTOR PLUVIAL FRONTAL - REGISTROS DE LIMPIEZA Y TAPAS", n,
                 "Lamina DP-01 (ubicacion) y DP-06B (detalle): contramarco L 2\"x2\"x3/16\" anclado a la losa, marco L 1 1/2\"x1 1/2\"x1/8\" soldado a la tapa, tapa de concreto armado 0.68 x 0.68 x 0.08 con parrilla 3/8\" @0.10 y asas; borde engrosado 0.15 x 0.10 alrededor de la abertura de 0.70 x 0.70.")
    encabezado(ws, r, cols, 30); r0 = r + 1
    lista = [("CL", 0.0, "Caja de llegada (empalme con CAR Varones y cuneta Eje 01)", "DP-07")]
    lista += [(x["nombre"], x["prog"], "Registro en la losa del colector; %s" % ("empalme cuneta" if any(abs(c["prog"] - x["prog"]) < 0.5 for c in dz.CUNETAS) else "limpieza / quiebre"), "DP-01, DP-06B") for x in dz.REGISTROS if x["tipo"] == "registro"]
    lista += [("CC (2)", dz.P_BRINK, "Caja de caida: dos registros sobre la poza", "DP-07")]
    rr = r0
    for i, (nm, p, ub, sus) in enumerate(lista):
        fila(ws, rr, cols, [i + 1, nm, prog(p), ub, 2 if nm.startswith("CC") else 1, sus], 24); ws.cell(row=rr, column=4).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True); rr += 1
    rt = rr
    barra_total(ws, rt, n, "TOTAL DE REGISTROS CON TAPA", {"E": "=SUM(E%d:E%d)" % (r0, rt - 1)}, nf="0")
    rr = rt + 2
    subtitulo(ws, rr, n, "METRADO DE LAS PARTIDAS DE REGISTROS (cantidad = total de registros; dimensiones de la hoja COLECTOR PARAMETROS)")
    cols_m = [("N°", 5, "txt", None), ("PARTIDA", 16, "txt", None), ("UND", 12, "und", None), ("CALCULO", 40, "txt", None), ("TOTAL", 12, "tot", "0.00"), ("SUSTENTO", 50, "sust", None)]
    encabezado(ws, rr + 1, cols_m, 30)
    N = "=E%d" % rt
    items = [("contramarco", "CONTRAMARCO METALICO L 2\"x2\"x3/16\" CON ANCLAJES", "und", "1 por registro", "=E%d" % rt, "DP-06B"),
             ("marco", "MARCO METALICO DE TAPA L 1 1/2\"x1 1/2\"x1/8\"", "und", "1 por tapa", "=E%d" % rt, "DP-06B"),
             ("angulos", "ANGULOS METALICOS P/MARCO Y CONTRAMARCO", "kg", "registros x (2.80 x 3.63 + 2.72 x 1.83)", "=E%d*(%s*%s+%s*%s)" % (rt, P["pcm"], P["ka"], P["pm"], P["kb"]), "DP-06B; pesos de catalogo"),
             ("tapa", "TAPA DE CONCRETO ARMADO 0.68 x 0.68 x 0.08", "und", "1 por registro", "=E%d" % rt, "DP-06B"),
             ("conc_tapa", "CONCRETO f'c=210 EN TAPAS", "m3", "registros x 0.68 x 0.68 x 0.08", "=E%d*%s*%s*%s" % (rt, P["tl"], P["tl"], P["te"]), "DP-06B"),
             ("pintura", "PINTURA ANTICORROSIVA Y ESMALTE EN ANGULOS", "m2", "registros x (2.80 x 0.203 + 2.72 x 0.152)", "=E%d*(%s*%s+%s*%s)" % (rt, P["pcm"], P["da"], P["pm"], P["db"]), "4 caras de cada angulo")]
    refs = {}; rr = rr + 2
    for i, (k, desc, u, calc, f, sus) in enumerate(items):
        fila(ws, rr, cols_m, [i + 1, desc, u, calc, f, sus], 30)
        ws.cell(row=rr, column=2).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True); ws.column_dimensions["B"].width = 40
        refs[k] = rr; rr += 1
    return ws, dict(n=rt, refs=refs)


# ----------------------------------------------------------------------------- JUNTAS Y EMPALMES
def hoja_juntas(wb, P, mt):
    ws = wb.create_sheet(NOMBRES["JE"])
    cols = [("N°", 5, "txt", None), ("ELEMENTO", 44, "txt", None), ("PROGRESIVA / DETALLE", 22, "txt", None), ("VECES", 9, "auto", "0"), ("LONGITUD (m)", 12, "auto", "0.00"), ("PARCIAL (m)", 12, "form", "0.00"), ("SUSTENTO", 52, "sust", None)]
    n = len(cols)
    r = cabecera(ws, "COLECTOR PLUVIAL FRONTAL - JUNTAS Y EMPALMES DE CUNETAS", n,
                 "Lamina DP-01 (nota 5), DP-03 y DP-06C. Junta de dilatacion de 1\" cada 4.00 m en todo el perimetro de la seccion (tecnopor + sellador elastomerico). Junta de tecnopor de 1\" entre el colector y el cimiento del cerco, y entre el borde de la losa y el piso adyacente. "
                 "Empalme de cada cuneta por ventana en el muro lado predio con caida libre al fondo (sin dintel adicional).")
    encabezado(ws, r, cols, 30); r0 = r + 1
    J = MC.juntas(); rr = r0
    subtitulo(ws, rr, n, "JUNTA DE DILATACION e=1\" CON TECNOPOR Y SELLADOR ELASTOMERICO (perimetro = 2 x ancho exterior + 2 x (e fondo + h max + e losa))"); rr += 1
    MT = Q["MT"]
    be = "(%s+2*%s)" % (P["b"], P["em"])
    r_jd = rr
    fila(ws, rr, cols, [1, "Juntas de dilatacion cada 4.00 m entre 0+004.00 y 0+%06.2f" % (J["n"] * 4), "=\"n = ENTERO(\"&TEXT(%s,\"0.00\")&\" / 4.00)\"" % P["PB"], "=INT(%s/%s)" % (P["PB"], P["jd"]), "=2*%s+2*(%s+%s+%s)" % (be, P["ef"], P["hmax"], P["et"]), "=D%d*E%d" % (rr, rr), "DP-01 nota 5; DP-03 (juntas en el perfil); perimetro de la seccion"], 30); rr += 1
    rt1 = rr; barra_total(ws, rt1, n, "TOTAL JUNTA DE DILATACION (m)", {"F": "=SUM(F%d:F%d)" % (r_jd, rt1 - 1)}); rr += 2
    subtitulo(ws, rr, n, "JUNTA DE TECNOPOR e=1\" ENTRE COLECTOR, CERCO Y PISO ADYACENTE"); rr += 1
    r_jt = rr
    fila(ws, rr, cols, [1, "Contra el cimiento del cerco (tramo pegado al cerco, 0+000 a primer quiebre)", "=\"0+000.00 a 0+\"&TEXT(%s,\"000.00\")" % P["PB1"], 1, "=%s" % P["PB1"], "=D%d*E%d" % (rr, rr), "DP-01, DP-04 (junta entre muro y cimiento del cerco)"], 30); rr += 1
    fila(ws, rr, cols, [2, "Borde de la losa con el piso adyacente: colector (ambos lados)", "=\"2 x 0+\"&TEXT(%s,\"000.00\")" % P["PB"], 2, "=%s" % P["PB"], "=D%d*E%d" % (rr, rr), "DP-04: junta de tecnopor en el borde de la losa superior"], 30); rr += 1
    fila(ws, rr, cols, [3, "Borde de la losa con el piso adyacente: caja CL (ambos lados)", "2 x (largo exterior + 0.30)", 2, "=%s!D%d+2*%s+0.30" % (MT, mt["cajas"]["CL"], P["em"]), "=D%d*E%d" % (rr, rr), "DP-07"], 30); rr += 1
    fila(ws, rr, cols, [4, "Borde de la losa con el piso adyacente: caja CC (ambos lados)", "2 x (largo exterior + 0.30)", 2, "=%s!D%d+2*%s+0.30" % (MT, mt["cajas"]["CC"], P["em"]), "=D%d*E%d" % (rr, rr), "DP-07"], 30); rr += 1
    rt2 = rr; barra_total(ws, rt2, n, "TOTAL JUNTA DE TECNOPOR (m)", {"F": "=SUM(F%d:F%d)" % (r_jt, rt2 - 1)}); rr += 2
    subtitulo(ws, rr, n, "EMPALME DE CUNETA AL COLECTOR (ventana 0.40 x H en el muro lado predio, caida libre y registro encima) - lamina DP-06C"); rr += 1
    r_e = rr
    for i, c in enumerate(dz.CUNETAS):
        fila(ws, rr, cols, [i + 1, "Cuneta %s, perfil %s" % (c["nombre"], c["perfil"]), prog(c["prog"]), 1, None, "=D%d" % rr, "DP-06C (cuadro de empalmes); DP-01"], 24); ws.cell(row=rr, column=6).number_format = "0"; rr += 1
    rt3 = rr; barra_total(ws, rt3, n, "TOTAL EMPALMES (und)", {"F": "=SUM(F%d:F%d)" % (r_e, rt3 - 1)}, nf="0")
    nota(ws, rt3 + 2, n, "Nota: las cunetas de los Ejes 11 y 12 terminan antes del cerco y se prolongan 1.88 y 5.39 m hasta el muro del colector con su misma seccion (DP-06C). Esa prolongacion se metra en las partidas de cunetas del proyecto; aqui solo se cuenta la ventana de empalme.")
    for rr_ in range(r0, rt3 + 1): ws.cell(row=rr_, column=2).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    return ws, dict(dilat=rt1, tecnopor=rt2, empalmes=rt3)


# ----------------------------------------------------------------------------- INSUMOS
def hoja_insumos(wb, pg_refs):
    """Desglose de insumos por partida (rendimientos editables) para los analisis de costos unitarios."""
    ws = wb.create_sheet(NOMBRES["IN"])
    cols = [("N°", 5, "txt", None), ("PARTIDA", 44, "txt", None), ("UND", 8, "und", None), ("METRADO", 12, "form", "0.00"), ("INSUMO", 44, "txt", None), ("UND INSUMO", 10, "und", None), ("CANTIDAD POR UND DE PARTIDA", 14, "dato", "0.000"), ("CANTIDAD TOTAL", 14, "tot", "0.00")]
    n = len(cols)
    r = cabecera(ws, "COLECTOR PLUVIAL FRONTAL - DESGLOSE DE INSUMOS POR PARTIDA", n,
                 "Rendimientos unitarios referenciales (celdas amarillas, editar segun el analisis de costos unitarios adoptado). El metrado se toma de la PLANILLA GENERAL DE METRADOS.")
    encabezado(ws, r, cols, 40)
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
    rr = r + 1; i = 0
    for item, desc, und, ins in grupos:
        rp = pg_refs.get(item); i += 1; r_ini = rr
        for k, (inm, iu, q) in enumerate(ins):
            fila(ws, rr, cols, [i if k == 0 else None, "%s %s" % (item, desc) if k == 0 else None, und if k == 0 else None, "=%s!K%d" % (PGq, rp) if (k == 0 and rp) else None, inm, iu, q, "=G%d*$D$%d" % (rr, r_ini)], 20)
            ws.cell(row=rr, column=2).alignment = Alignment(horizontal="left", vertical="center"); ws.cell(row=rr, column=5).alignment = Alignment(horizontal="left", vertical="center")
            rr += 1
    return ws


# ----------------------------------------------------------------------------- PLANILLA GENERAL y RESUMEN
def copiar_estilo(src, dst):
    dst.font = copy.copy(src.font); dst.fill = copy.copy(src.fill); dst.border = copy.copy(src.border)
    dst.alignment = copy.copy(src.alignment); dst.number_format = src.number_format


def fila_estilo(ws, r, r_ref, ncols=12):
    for c in range(1, ncols + 1):
        copiar_estilo(ws.cell(row=r_ref, column=c), ws.cell(row=r, column=c))


class Planilla:
    """Escribe filas en la PLANILLA GENERAL con el formato de las filas de referencia (9 madre, 10 titulo, 11 partida, 12 detalle)."""
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


def construir():
    wb = openpyxl.load_workbook(ORIG)
    ws = wb[PG]
    segs = MC.segmentos()
    wsP, P = hoja_parametros(wb)
    wsM, mt = hoja_mov_tierras(wb, segs, P)
    wsC, co = hoja_concreto(wb, segs, P, mt)
    wsE, en = hoja_encofrado(wb, segs, P, mt)
    wsA, ac = hoja_acero(wb, segs, P, mt)
    wsR, rg = hoja_registros(wb, P)
    wsJ, je = hoja_juntas(wb, P, mt)
    MT, CO, EN, AC, RT, JE = Q["MT"], Q["CO"], Q["EN"], Q["AC"], Q["RT"], Q["JE"]
    ult = max(c.row for row in ws.iter_rows() for c in row if c.value is not None)
    pl = Planilla(ws, ult + 2)
    pl.madre("01.04.04", "COLECTOR PLUVIAL FRONTAL (TRAMO HOGAR DE REFUGIO - EMPALME CON CAR MUJERES)")
    def det(hoja, filas, col, nombres, extra=""):
        return [("%s%s" % (nm, extra), 1, None, None, None, "=%s!%s%d" % (hoja, col, r)) for nm, r in zip(nombres, filas)]
    nom_t = ["%s (%s - %s)" % (s["nombre"].capitalize(), prog(s["p1"]), prog(s["p2"])) for s in segs]
    nom_c = ["Caja de llegada CL", "Caja de caida CC"]
    fcm = [mt["cajas"]["CL"], mt["cajas"]["CC"]]
    def rango(hoja, col, a, b, nm):
        return [(nm, 1, None, None, None, "=SUM(%s!%s%d:%s%d)" % (hoja, col, a, col, b))]
    pl.titulo("01.04.04.01", "TRABAJOS PRELIMINARES")
    pl.partida("01.04.04.01.01", "LIMPIEZA MANUAL DE TERRENO", "m²", det(MT, mt["filas"], "M", nom_t) + det(MT, fcm, "M", nom_c))
    pl.partida("01.04.04.01.02", "TRAZO, NIVELES Y REPLANTEO PRELIMINAR", "m²", det(MT, mt["filas"], "M", nom_t) + det(MT, fcm, "M", nom_c))
    pl.titulo("01.04.04.02", "MOVIMIENTO DE TIERRAS")
    pl.partida("01.04.04.02.01", "EXCAVACIÓN MANUAL DE ZANJAS P/COLECTOR (ancho 1.60 m)", "m³", det(MT, mt["filas"], "N", nom_t) + det(MT, fcm, "N", nom_c))
    pl.partida("01.04.04.02.02", "REFINE, NIVELACIÓN Y COMPACTACIÓN EN TERRENO NORMAL", "m²", det(MT, mt["filas"], "O", nom_t) + det(MT, fcm, "O", nom_c))
    r_rell = pl.partida("01.04.04.02.03", "RELLENO COMPACTADO CON MATERIAL PROPIO SELECCIONADO (incluye nivelacion del retiro y base de cajas)", "m³",
                        det(MT, mt["filas"], "P", nom_t, " - lateral de zanja") + det(MT, mt["filas"], "Q", nom_t, " - franja de nivelacion") + det(MT, fcm, "P", nom_c))
    r_exc = pl.refs["01.04.04.02.01"]
    pl.partida("01.04.04.02.04", "ELIMINACIÓN DE MATERIAL EXCEDENTE", "m³", [("Excavacion de zanjas y cajas", 1, None, None, None, "=K%d" % r_exc), ("Relleno compactado (se descuenta)", -1, None, None, None, "=-K%d" % r_rell)])
    ws.cell(row=pl.refs["01.04.04.02.04"], column=11, value="=SUM(J%d:J%d)*PARAMETROS!$B$16" % (pl.refs["01.04.04.02.04"] + 1, pl.refs["01.04.04.02.04"] + 2))
    pl.titulo("01.04.04.03", "OBRAS DE CONCRETO SIMPLE")
    cl_, cc_ = co["cajas"]["CL"], co["cajas"]["CC"]
    pl.partida("01.04.04.03.01", "CONCRETO f'c=100 kg/cm2 PARA SOLADO E=2\" (0.05 m)", "m²", det(CO, co["filas"], "H", nom_t) + rango(CO, "H", cl_[0], cl_[1], "Caja de llegada CL") + rango(CO, "H", cc_[0], cc_[1], "Caja de caida CC"))
    pl.titulo("01.04.04.04", "OBRAS DE CONCRETO ARMADO - COLECTOR Y CAJAS")
    pl.partida("01.04.04.04.01", "CONCRETO f'c=210 kg/cm2 EN LOSA DE FONDO", "m³", det(CO, co["filas"], "I", nom_t) + rango(CO, "I", cl_[0], cl_[1], "Caja de llegada CL") + rango(CO, "I", cc_[0], cc_[1], "Caja de caida CC (incluye umbral)"))
    pl.partida("01.04.04.04.02", "CONCRETO f'c=210 kg/cm2 EN MUROS", "m³", det(CO, co["filas"], "J", nom_t) + rango(CO, "J", cl_[0], cl_[1], "Caja de llegada CL (muros, murete, descuento de ventana)") + rango(CO, "J", cc_[0], cc_[1], "Caja de caida CC (muros, murete, descuento de ventana)"))
    pl.partida("01.04.04.04.03", "CONCRETO f'c=210 kg/cm2 EN LOSA SUPERIOR (incluye bordes de registro)", "m³", det(CO, co["filas"], "K", nom_t) + rango(CO, "K", cl_[0], cl_[1], "Caja de llegada CL (descuento de abertura)") + rango(CO, "K", cc_[0], cc_[1], "Caja de caida CC (descuento de aberturas)")
                + [("Bordes engrosados de abertura de registros RS-01 a RS-07", 1, None, None, None, "=%s!K%d" % (CO, co["reg"])), ("Descuento de aberturas de registro 0.70 x 0.70 x 0.10", 1, None, None, None, "=%s!K%d" % (CO, co["reg"] + 1))])
    e_cl, e_cc = en["cajas"]["CL"], en["cajas"]["CC"]
    pl.partida("01.04.04.04.04", "ENCOFRADO Y DESENCOFRADO NORMAL EN COLECTOR Y CAJAS", "m²", det(EN, en["filas"], "K", nom_t) + rango(EN, "K", e_cl[0], e_cl[1], "Caja de llegada CL") + rango(EN, "K", e_cc[0], e_cc[1], "Caja de caida CC"))
    a_cl, a_cc = ac["cajas"]["CL"], ac["cajas"]["CC"]
    pl.partida("01.04.04.04.05", "ACERO DE REFUERZO fy=4200 kg/cm2 EN COLECTOR Y CAJAS", "kg", det(AC, ac["filas"], "U", nom_t) + rango(AC, "U", a_cl[0], a_cl[1], "Caja de llegada CL (malla 3/8\" @0.20 ambas caras)") + rango(AC, "U", a_cc[0], a_cc[1], "Caja de caida CC (malla 3/8\" @0.20 ambas caras)"))
    pl.partida("01.04.04.04.06", "ACABADO FROTACHADO Y BRUÑADO DE LOSA SUPERIOR", "m²", det(CO, co["filas"], "L", nom_t) + rango(CO, "L", cl_[0], cl_[1], "Caja de llegada CL") + rango(CO, "L", cc_[0], cc_[1], "Caja de caida CC"))
    pl.partida("01.04.04.04.07", "CURADO DE CONCRETO EN COLECTOR Y CAJAS", "m²", det(CO, co["filas"], "M", nom_t) + rango(CO, "M", cl_[0], cl_[1], "Caja de llegada CL") + rango(CO, "M", cc_[0], cc_[1], "Caja de caida CC"))
    pl.titulo("01.04.04.05", "REGISTROS DE LIMPIEZA Y TAPAS")
    rf = rg["refs"]
    pl.partida("01.04.04.05.01", "CONTRAMARCO METALICO L 2\"x2\"x3/16\" CON ANCLAJES", "und", None, total="=+%s!E%d" % (RT, rf["contramarco"]))
    pl.partida("01.04.04.05.02", "MARCO METALICO DE TAPA L 1 1/2\"x1 1/2\"x1/8\"", "und", None, total="=+%s!E%d" % (RT, rf["marco"]))
    pl.partida("01.04.04.05.03", "ANGULOS METALICOS P/MARCO Y CONTRAMARCO (incluye soldadura)", "kg", None, total="=+%s!E%d" % (RT, rf["angulos"]))
    pl.partida("01.04.04.05.04", "TAPA DE CONCRETO ARMADO 0.68 x 0.68 x 0.08 m (incluye acero y asas)", "und", None, total="=+%s!E%d" % (RT, rf["tapa"]))
    pl.partida("01.04.04.05.05", "CONCRETO f'c=210 kg/cm2 EN TAPAS", "m³", None, total="=+%s!E%d" % (RT, rf["conc_tapa"]))
    pl.partida("01.04.04.05.06", "ACERO DE REFUERZO fy=4200 kg/cm2 EN TAPAS, BORDES Y ANCLAJES", "kg", None, total="=+%s!I%d" % (AC, ac["registros"]))
    pl.partida("01.04.04.05.07", "PINTURA ANTICORROSIVA Y ESMALTE EN ANGULOS", "m²", None, total="=+%s!E%d" % (RT, rf["pintura"]))
    pl.titulo("01.04.04.06", "JUNTAS Y EMPALMES")
    pl.partida("01.04.04.06.01", "JUNTA DE DILATACION E=1\" CON TECNOPOR Y SELLADOR ELASTOMERICO", "m", None, total="=+%s!F%d" % (JE, je["dilat"]))
    pl.partida("01.04.04.06.02", "JUNTA DE TECNOPOR E=1\" ENTRE COLECTOR, CERCO Y PISO ADYACENTE", "m", None, total="=+%s!F%d" % (JE, je["tecnopor"]))
    pl.partida("01.04.04.06.03", "EMPALME DE CUNETA AL COLECTOR (ventana en muro y caida)", "und", None, total="=+%s!F%d" % (JE, je["empalmes"]))
    hoja_insumos(wb, pl.refs)
    # RESUMEN
    wr = wb["RESUMEN"]; ultr = max(c.row for row in wr.iter_rows() for c in row if c.value is not None)
    r = ultr + 2
    def res_row(item, desc, und, rp, ref_r):
        for c in range(1, 6): copiar_estilo(wr.cell(row=ref_r, column=c), wr.cell(row=r, column=c))
        wr.cell(row=r, column=1, value=item); wr.cell(row=r, column=2, value=desc)
        if und: wr.cell(row=r, column=3, value=und); wr.cell(row=r, column=4, value="=+'%s'!K%d" % (PG, rp))
    res_row("01.04.04", "COLECTOR PLUVIAL FRONTAL (TRAMO HOGAR DE REFUGIO - EMPALME CON CAR MUJERES)", None, None, 9); r += 1
    for rr_ in range(ult + 2, pl.r):
        item = ws.cell(row=rr_, column=1).value; desc = ws.cell(row=rr_, column=2).value; und = ws.cell(row=rr_, column=12).value
        if not item or item == "01.04.04": continue
        if und: res_row(item, desc, und, rr_, 11)
        else: res_row(item, desc, None, None, 10)
        r += 1
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
                if v2 != c.value and not (c.value == "" and v2 is None): d.append((c.coordinate, c.value, v2))   # '' y celda vacia son lo mismo
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
