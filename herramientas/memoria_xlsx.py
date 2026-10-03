"""Memoria de calculo en Excel (con formulas) del colector pluvial frontal, tramo
Hogar de Refugio Temporal Mujeres Violentadas (CUI 2675514).

Mismas hojas y convenciones que la memoria del tramo CAR Mujeres:
  MEMORIA, DATOS, CAUDALES, CUNETAS, EMPALME, PERFIL_FLUJO, ESTRUCTURAL.
Las formulas se guardan con nombres en ingles (SUM, IF, ROUND...) y separador ",":
Excel en espanol las muestra como SUMA, SI, REDONDEAR con ";".
Azul = dato editable; negro = formula; verde = vinculo a otra hoja.
"""
import os, sys, json
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import diseno as dz

AZUL = Font(name="Arial", size=9, color="0000FF")
NEGRO = Font(name="Arial", size=9)
VERDE = Font(name="Arial", size=9, color="008000")
NEG = Font(name="Arial", size=9, bold=True)
TIT = Font(name="Arial", size=12, bold=True)
SUB = Font(name="Arial", size=9, italic=True, color="555555")
GRIS = PatternFill("solid", fgColor="EEEEEE")
BORDE = Border(*(Side(style="thin", color="999999"),) * 4)
SUBTITULO = "Colector pluvial frontal - tramo Hogar de Refugio Temporal Mujeres Violentadas (CUI 2675514), Morales - San Martin. Hidroconsult, Oct. 2026"


def celda(ws, ref, valor, font=NEGRO, fmt=None, bold=False, fill=None, al=None):
    c = ws[ref]; c.value = valor; c.font = NEG if bold else font
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    if al: c.alignment = Alignment(horizontal=al, vertical="center", wrap_text=True)
    return c


def fila(ws, r, valores, fonts=None, fmts=None):
    for j, v in enumerate(valores):
        if v is None: continue
        c = ws.cell(row=r, column=j + 1, value=v)
        f = (fonts[j] if fonts and j < len(fonts) and fonts[j] else None)
        c.font = f or (AZUL if isinstance(v, (int, float)) and not isinstance(v, bool) else NEGRO)
        if fmts and j < len(fmts) and fmts[j]: c.number_format = fmts[j]


def cabecera(ws, titulo, anchos):
    celda(ws, "A1", titulo, TIT); celda(ws, "A2", SUBTITULO, SUB)
    for i, a in enumerate(anchos): ws.column_dimensions[L(i + 1)].width = a


def encabezado_tabla(ws, r, textos):
    for j, t in enumerate(textos):
        c = ws.cell(row=r, column=j + 1, value=t); c.font = NEG; c.fill = GRIS; c.border = BORDE
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


# ----------------------------------------------------------------------------
def hoja_datos(wb, R):
    ws = wb.create_sheet("DATOS"); D = dz.D
    cabecera(ws, "1. DATOS DE DISENO", [46, 12, 8, 70, 8])
    encabezado_tabla(ws, 4, ["PARAMETRO", "VALOR", "UND", "FUENTE / CRITERIO", "SIMBOLO"])
    filas = [
        ("HIDROLOGIA",),
        ("Periodo de retorno", D["TR"], "anos", "Analisis estadistico de precipitaciones (memoria HIDRO-CE040 del proyecto)", "TR"),
        ("Precipitacion de diseno D=10 min", D["P10"], "mm", "Dick-Peschke, P24 = 121.81 mm", "P10"),
        ("Precipitacion de diseno D=20 min", D["P20"], "mm", "Dick-Peschke", "P20"),
        ("Tiempo de concentracion en el colector", D["tc"], "min", "10 min de entrada + recorrido en cunetas y colector", "tc"),
        ("Exponente de la curva P-D", "=LN(B8/B7)/LN(2)", "-", "b = ln(P20/P10)/ln 2", "bx"),
        ("Intensidad de diseno I", "=B7*(B9/10)^B10/(B9/60)", "mm/h", "I = P10 (tc/10)^b / (tc/60)", "I"),
        ("Factor de seguridad FS", D["FS"], "-", "Memorias de calculo HIDRO-CE040", "FS"),
        ("GEOMETRIA DEL COLECTOR (tramo Hogar de Refugio)",),
        ("Ancho interior b", D["b"], "m", "Adoptado: llenado <= 85 % y regimen subcritico (hoja PERFIL_FLUJO)", "b"),
        ("Espesor de muros", D["e_muro"], "m", "Muros de 1.40 a 1.65 m de altura interior (hoja ESTRUCTURAL)", "em"),
        ("Espesor de losa de fondo", D["e_fondo"], "m", "", "ef"),
        ("Espesor de losa superior (tramo normal y porton de motos)", D["e_losa"], "m", "Vaciada monoliticamente con los muros", "et"),
        ("Espesor de losa superior en cruce de camiones", D["e_losa_camion"], "m", "Ingreso vehicular OE-01 (cisterna al PTAR)", "ec"),
        ("Cota de fondo inicial (0+000, caja de llegada)", D["CF0"], "msnm", "Fijada por las cunetas de arquitectura: la mas baja llega con NCF 259.70 (Eje 02)", "CF0"),
        ("Pendiente S", D["S"], "m/m", "Adoptada 0.30 %: regimen subcritico (F = 0.60) y fondo sobre el R-01 del receptor", "S"),
        ("Progresiva del quiebre 1 (45 grados)", round(dz.P_B1, 2), "m", "Salida del frente hacia el lindero", "pq1"),
        ("Progresiva del quiebre 2 (45 grados)", round(dz.P_B2, 2), "m", "", "pq2"),
        ("Progresiva del brink de la caida (fin del colector b=0.80)", round(dz.P_BRINK, 2), "m", "Inicio de la poza de disipacion", "pb"),
        ("Progresiva de entrega (0+000 del tramo CAR Mujeres)", round(dz.P_FIN, 2), "m", "Cara aguas arriba del registro R-01 del receptor", "pf"),
        ("Longitud total del tramo", "=B23", "m", "", "L"),
        ("NPT del frente (cara superior de la losa)", D["NPT"], "msnm", "Arquitectura: NT 260.50 + NPT 0.10 (estacionamientos e ingresos)", "NPT"),
        ("Cruce de camiones: inicio", R["zonas"][0]["p1"], "m", R["zonas"][0]["nombre"] + " + 0.30 m a cada lado", "pc1"),
        ("Cruce de camiones: fin", R["zonas"][0]["p2"], "m", "", "pc2"),
        ("Cruce de motos: inicio", R["zonas"][1]["p1"], "m", R["zonas"][1]["nombre"] + ", tramo de 2.00 m", "pm1"),
        ("Cruce de motos: fin", R["zonas"][1]["p2"], "m", "", "pm2"),
        ("Coeficiente de Manning n", D["n"], "-", "Concreto vaciado in situ (Chow)", "n"),
        ("CRITERIOS DE VERIFICACION HIDRAULICA",),
        ("Llenado maximo admisible y/h (conducto cubierto)", D["llenado_max"], "-", "Criterio de conducto cerrado a superficie libre", "llen"),
        ("Borde libre minimo bajo losa", D["BL_min"], "m", "Complementario al criterio de llenado", "BLmin"),
        ("RECEPTOR: COLECTOR DEL CAR MUJERES (CUI 2717013)",),
        ("Cota de fondo del receptor en su 0+000 (R-01)", D["CF_R01"], "msnm", "Plano DP-01 del tramo CAR Mujeres", "CFr"),
        ("Nivel de agua del receptor en su 0+000", D["NA_R01"], "msnm", "Memoria del tramo CAR Mujeres (Q = 626 L/s en 0+000)", "NAr"),
        ("Ancho interior del receptor", D["b_wilma"], "m", "", "br"),
        ("APORTE EXTERNO: COLECTOR DEL CAR VARONES (CUI 2705619)",),
        ("Cota de fondo de llegada (referencial, por confirmar)", D["CF_varones_sup"], "msnm", "Supuesta: 260.69 - 0.5 % x 102.36 m. Dato de la memoria del proyecto CUI 2705619", "CFv"),
        ("CAJAS",),
        ("Caja de llegada CL: profundidad de poza bajo el fondo", D["CL_poza"], "m", "Colchon de agua para la caida del aporte externo", "pcl"),
        ("Caja de caida CC: profundidad de poza bajo el fondo del receptor", D["CC_poza_prof"], "m", "Poza de disipacion deprimida", "pcc"),
        ("Caja de caida CC: longitud de poza", D["CC_poza_largo"], "m", "", "Lcc"),
        ("Caja de caida CC: ancho de poza", D["CC_ancho"], "m", "Igual al ancho del receptor", "bcc"),
    ]
    r = 5
    for f in filas:
        if len(f) == 1:
            celda(ws, f"A{r}", f[0], NEG, fill=GRIS)
        else:
            fila(ws, r, list(f), fonts=[NEGRO, None, NEGRO, NEGRO, NEGRO])
            if isinstance(f[1], str) and f[1].startswith("="): ws[f"B{r}"].font = NEGRO
        r += 1
    celda(ws, f"A{r+1}", "Azul = dato editable; negro = formula; verde = vinculo.", SUB)
    return ws


def hoja_caudales(wb, R):
    ws = wb.create_sheet("CAUDALES"); D = dz.D
    cabecera(ws, "2. CAUDALES DE DISENO - METODO RACIONAL Q = C I A FS", [44, 12, 12, 12, 10, 10, 34, 34])
    encabezado_tabla(ws, 4, ["PROYECTO", "AREA (m2)", "C x A (m2)", "C PONDERADO", "I (mm/h)", "Q (L/s)", "INGRESA AL COLECTOR EN", "FUENTE"])
    fila(ws, 5, ["CAR Varones (CUI 2705619) - aporte externo", D["A_varones"], D["CA_varones"], "=C5/B5", "=DATOS!$B$11", "=C5*E5/3600000*DATOS!$B$12*1000", "Caja de llegada CL (0+000)", "Memoria HIDRO-CE040 del proyecto, dato no validado"],
         fonts=[NEGRO, AZUL, AZUL, NEGRO, VERDE, NEGRO, NEGRO, NEGRO], fmts=[None, "0.00", "0.0000", "0.000", "0.00", "0.0"])
    fila(ws, 6, ["Hogar de Refugio Temporal M. Violentadas (CUI 2675514)", D["A_refugio"], D["CA_refugio"], "=C6/B6", "=DATOS!$B$11", "=C6*E6/3600000*DATOS!$B$12*1000", "Cunetas Ejes 01, 02, 06, 07, 11 y 12", "Memoria HIDRO-CE040, 12 fichas"],
         fonts=[NEGRO, AZUL, AZUL, NEGRO, VERDE, NEGRO, NEGRO, NEGRO], fmts=[None, "0.00", "0.0000", "0.000", "0.00", "0.0"])
    fila(ws, 7, ["TOTAL ENTREGADO AL CAR MUJERES", "=SUM(B5:B6)", "=SUM(C5:C6)", "=C7/B7", None, "=SUM(F5:F6)"], fonts=[NEG, NEGRO, NEGRO, NEGRO, None, NEG], fmts=[None, "0.00", "0.0000", "0.000", None, "0.0"])
    celda(ws, "A9", "Caudal de diseno adoptado (valores de las memorias de cada proyecto)", NEG)
    fila(ws, 10, ["CAR Varones", D["Q_varones"], "L/s"], fonts=[NEGRO, AZUL, NEGRO])
    fila(ws, 11, ["Hogar de Refugio", D["Q_refugio"], "L/s"], fonts=[NEGRO, AZUL, NEGRO])
    fila(ws, 12, ["Q de diseno del tramo", "=B10+B11", "L/s"], fonts=[NEG, NEG, NEGRO]); ws["B12"].number_format = "0.0"
    fila(ws, 13, ["Q de diseno del tramo", "=B12/1000", "m3/s"], fonts=[NEGRO, NEGRO, NEGRO]); ws["B13"].number_format = "0.0000"
    celda(ws, "A15", "Caudal que circula por el tramo (de aguas arriba hacia aguas abajo)", NEG)
    encabezado_tabla(ws, 16, ["PUNTO", "PROGRESIVA", "APORTE (L/s)", "Q ACUMULADO (L/s)"])
    pts = [("Caja de llegada CL (CAR Varones)", 0.0, "=B10")]
    for c in R["cunetas"]:
        pts.append((f"Cuneta {c['nombre']} - perfil {c['perfil']}", c["prog"], "=B11/6"))
    r = 17
    for i, (nm, p, ap) in enumerate(pts):
        fila(ws, r, [nm, p, ap, f"=SUM($C$17:C{r})"], fonts=[NEGRO, AZUL, NEGRO, NEGRO], fmts=[None, "0.00", "0.0", "0.0"]); r += 1
    celda(ws, f"A{r+1}", "Suma de picos sin desfase de tiempos y con FS = 1.15: hipotesis conservadora. El reparto del aporte del Refugio entre sus 6 cunetas es nominal; el perfil se verifica con el caudal total en todo el tramo.", SUB)
    return ws


def hoja_cunetas(wb, R):
    ws = wb.create_sheet("CUNETAS")
    cabecera(ws, "3. CUNETAS DE ARQUITECTURA QUE LLEGAN AL COLECTOR", [30, 10, 10, 10, 10, 10, 12, 12, 14, 14, 14, 30])
    encabezado_tabla(ws, 4, ["CUNETA (perfil de arquitectura)", "PERFIL", "PROGRESIVA (m)", "LONGITUD (m)", "NCT (msnm)", "NCF al cerco (msnm)", "H al cerco (m)", "PROLONG. (m)", "NCF en el muro (msnm)", "NA del colector (msnm)", "CAIDA LIBRE (m)", "VERIFICACION"])
    r = 5
    for c in R["cunetas"]:
        fila(ws, r, [c["nombre"], c["perfil"], c["prog"], c["L"], c["NCT"], c["NCF"], f"=E{r}-F{r}", c["prolong"], f"=F{r}-0.005*H{r}",
                     f"=IFERROR(INDEX(PERFIL_FLUJO!$G$6:$G$200,MATCH(C{r},PERFIL_FLUJO!$A$6:$A$200,0)),\"\")", f"=I{r}-J{r}",
                     f"=IF(K{r}>0,\"CAIDA LIBRE\",\"AHOGADA\")"],
             fonts=[NEGRO, AZUL, AZUL, AZUL, AZUL, AZUL, NEGRO, AZUL, NEGRO, VERDE, NEGRO, NEGRO],
             fmts=[None, None, "0.00", "0.00", "0.00", "0.00", "0.00", "0.00", "0.000", "0.000", "0.000"])
        r += 1
    celda(ws, f"A{r+1}", "Seccion de las cunetas: 0.40 x H, muros 0.10, pendiente 0.5 % (plano de arquitectura, perfiles 01 a 12). Las prolongaciones fuera del cerco mantienen la misma pendiente. El empalme es por ventana 0.40 x H en el muro lado predio, con caida al fondo del colector y registro encima (lamina DP-06).", SUB)
    return ws


def hoja_empalme(wb, R):
    ws = wb.create_sheet("EMPALME"); D = dz.D
    cabecera(ws, "4. CAJA DE LLEGADA (0+000) Y CAJA DE CAIDA EN LA ENTREGA AL CAR MUJERES", [52, 12, 8, 60])
    encabezado_tabla(ws, 4, ["PARAMETRO", "VALOR", "UND", "FORMULA / CRITERIO"])
    rows = [
        ("A. CAJA DE CAIDA CC - ENTREGA AL REGISTRO R-01 DEL CAR MUJERES",),
        ("Caudal Q", "=CAUDALES!B13", "m3/s", ""),
        ("Ancho del colector en el brink b", "=DATOS!B14", "m", ""),
        ("Cota de fondo en el brink", "=DATOS!B19-DATOS!B20*DATOS!B23", "msnm", "CF0 - S x pb"),
        ("Tirante critico en el brink yc", "=(B6^2/(9.81*B7^2))^(1/3)", "m", "yc = (Q2/(g b2))^(1/3): control de la caida libre"),
        ("Nivel de agua en el brink", "=B8+B9", "msnm", "nivel de control del perfil de flujo (hoja PERFIL_FLUJO)"),
        ("Piso de la poza", "=DATOS!B37-DATOS!B45", "msnm", "fondo del receptor - profundidad de poza"),
        ("Caida total (brink a piso de poza)", "=B8-B11", "m", ""),
        ("Energia al pie respecto al piso E1", "=B12+1.5*B9", "m", "E1 = caida + 1.5 yc (sin perdidas, conservador)"),
        ("Tirante al pie y1", "=B13-B14^2/(2*9.81)", "m", "resuelto por iteracion: y1 + V1^2/2g = E1 (ver B14)"),
        ("Velocidad al pie V1", "=B6/(B7*B15)", "m/s", "V1 = Q/(b y1), iteracion circular habilitada"),
        ("Froude al pie F1", "=B15/SQRT(9.81*B14)", "-", ""),
        ("Tirante conjugado y2", "=B14/2*(SQRT(1+8*B16^2)-1)", "m", "resalto hidraulico en el ancho b (conservador: no considera la expansion a 1.50 m)"),
        ("Tirante disponible en la poza", "=DATOS!B38-B11", "m", "NA del receptor - piso de la poza"),
        ("Verificacion del resalto", "=IF(B18>=B17,\"RESALTO AHOGADO - CUMPLE\",\"REVISAR PROFUNDIDAD DE POZA\")", "", "el receptor ahoga el resalto dentro de la poza"),
        ("Longitud de resalto 6 y2", "=6*B17", "m", "referencia (resalto libre)"),
        ("Longitud de poza adoptada", "=DATOS!B46", "m", "con umbral de salida de 0.40 m hasta el fondo del receptor; resalto ahogado"),
        ("Verificacion de longitud", "=IF(B21>=0.8*B20,\"CUMPLE (resalto ahogado)\",\"AMPLIAR POZA\")", "", "poza >= 0.8 x 6 y2 para resalto ahogado (USBR)"),
        ("Nivel de agua en el receptor", "=DATOS!B38", "msnm", "regimen subcritico aguas abajo del umbral (F = 0.67 en el receptor)"),
        ("",),
        ("B. CAJA DE LLEGADA CL (0+000) - CAIDA DEL APORTE DE CAR VARONES",),
        ("Cota de fondo de llegada del aporte externo", "=DATOS!B41", "msnm", "referencial, por confirmar con el proyecto CUI 2705619"),
        ("Piso de la poza de la caja", "=DATOS!B19-DATOS!B44", "msnm", "CF0 - profundidad de poza"),
        ("Caida del aporte externo", "=B26-B27", "m", ""),
        ("Nivel de agua en la caja (= inicio del colector)", "=PERFIL_FLUJO!G200", "msnm", "nivel de agua en 0+000 (hoja PERFIL_FLUJO, ultima fila)"),
        ("Colchon de agua en la poza", "=B29-B27", "m", "amortigua el chorro de 259 L/s"),
        ("Verificacion", "=IF(B30>=0.5,\"CUMPLE (colchon >= 0.50 m)\",\"REVISAR\")", "", ""),
        ("Dimensiones interiores de la caja", "1.50 x 1.00", "m", "largo x ancho; profundidad hasta el piso de poza"),
    ]
    r = 5
    for f in rows:
        if len(f) == 1:
            if f[0]: celda(ws, f"A{r}", f[0], NEG, fill=GRIS)
        else:
            fila(ws, r, list(f), fonts=[NEGRO, NEGRO, NEGRO, NEGRO])
            if isinstance(f[1], str) and f[1].startswith("=DATOS") or (isinstance(f[1], str) and f[1].startswith("=CAUDALES")) or (isinstance(f[1], str) and f[1].startswith("=PERFIL")):
                ws[f"B{r}"].font = VERDE
            ws[f"B{r}"].number_format = "0.000"
        r += 1
    # y1 por iteracion circular: B14 y B15 se referencian mutuamente; ponemos valor inicial por bisección en Python
    ws["B14"].value = round(R["poza"]["y1"], 4); ws["B14"].font = AZUL
    ws["D14"].value = "y1 resuelto en Python (y1 + (Q/(b y1))^2/2g = E1); verificar: B14 + B15^2/19.62 = B13"
    celda(ws, f"A{r}", "Verificacion de y1: y1 + V1^2/2g", NEGRO); celda(ws, f"B{r}", "=B14+B15^2/(2*9.81)", NEGRO, "0.000"); celda(ws, f"C{r}", "m", NEGRO); celda(ws, f"D{r}", "debe ser igual a E1 (B13)", NEGRO)
    return ws


def hoja_perfil(wb, R):
    ws = wb.create_sheet("PERFIL_FLUJO"); D = dz.D
    cabecera(ws, "5. PERFIL DE FLUJO GRADUALMENTE VARIADO - METODO DEL PASO ESTANDAR (de aguas abajo hacia aguas arriba)", [11, 10, 9, 8, 8, 9, 10, 9, 8, 10, 9, 9, 9, 13, 10])
    celda(ws, "A3", "Ecuacion de energia entre estaciones: y1 + V1^2/2g + z1 = y2 + V2^2/2g + z2 + dx (Sf1 + Sf2)/2 ; Sf = (n V / R^(2/3))^2 ; control: tirante critico en el brink de la caida (0+%06.2f)" % dz.P_BRINK, SUB)
    enc = ["PROGRESIVA (m)", "COTA FONDO", "Q (m3/s)", "b (m)", "yc (m)", "TIRANTE y (m)", "NIVEL DE AGUA", "VELOCIDAD (m/s)", "FROUDE", "COTA BAJO LOSA", "ALTURA INTERIOR h", "LLENADO y/h", "BORDE LIBRE (m)", "VERIFICACION", "ZONA"]
    encabezado_tabla(ws, 5, enc)
    NIT = 30
    perf = R["perfil"][::-1]            # de aguas abajo (brink) hacia aguas arriba
    r0 = 6
    for k, e in enumerate(perf):
        r = r0 + k
        ws.cell(row=r, column=1, value=round(e["p"], 2)).font = AZUL
        ws.cell(row=r, column=2, value=f"=DATOS!$B$19-DATOS!$B$20*A{r}").font = NEGRO
        ws.cell(row=r, column=3, value="=CAUDALES!$B$13").font = VERDE
        ws.cell(row=r, column=4, value="=DATOS!$B$14").font = VERDE
        ws.cell(row=r, column=5, value=f"=(C{r}^2/(9.81*D{r}^2))^(1/3)").font = NEGRO
        if k == 0:
            ws.cell(row=r, column=6, value=f"=E{r}").font = NEGRO
        else:
            ws.cell(row=r, column=6, value=f"=({L(16+2*NIT-2)}{r}+{L(16+2*NIT-1)}{r})/2").font = NEGRO
        ws.cell(row=r, column=7, value=f"=B{r}+F{r}").font = NEGRO
        ws.cell(row=r, column=8, value=f"=C{r}/(D{r}*F{r})").font = NEGRO
        ws.cell(row=r, column=9, value=f"=H{r}/SQRT(9.81*F{r})").font = NEGRO
        ws.cell(row=r, column=10, value=f"=DATOS!$B$25-IF(AND(A{r}>=DATOS!$B$26,A{r}<DATOS!$B$27),DATOS!$B$18,DATOS!$B$17)").font = NEGRO
        ws.cell(row=r, column=11, value=f"=J{r}-B{r}").font = NEGRO
        ws.cell(row=r, column=12, value=f"=F{r}/K{r}").font = NEGRO
        ws.cell(row=r, column=13, value=f"=J{r}-G{r}").font = NEGRO
        ws.cell(row=r, column=14, value=f"=IF(AND(L{r}<=DATOS!$B$33,M{r}>=DATOS!$B$34,I{r}<=1),\"CUMPLE\",\"NO CUMPLE\")").font = NEGRO
        ws.cell(row=r, column=15, value=f"=IF(AND(A{r}>=DATOS!$B$26,A{r}<DATOS!$B$27),\"cruce de camiones\",IF(AND(A{r}>=DATOS!$B$28,A{r}<DATOS!$B$29),\"cruce de motos\",\"tramo normal\"))").font = NEGRO
        for c, f in zip(range(2, 14), ["0.000", "0.0000", "0.00", "0.000", "0.000", "0.000", "0.00", "0.00", "0.000", "0.00", "0.00", "0.000"]):
            ws.cell(row=r, column=c).number_format = f
        if k > 0:
            rp = r - 1  # fila aguas abajo (ya resuelta)
            # columnas de iteracion: P=lo0, Q=hi0, R=lo1, S=hi1, ...
            dx = f"(A{rp}-A{r})"
            E2 = f"(G{rp}+H{rp}^2/(2*9.81))"
            Sf2 = f"((DATOS!$B$32*H{rp}/((D{rp}*F{rp})/(D{rp}+2*F{rp}))^(2/3))^2)"
            ws.cell(row=r, column=16, value=f"=E{r}*1.001").font = NEGRO
            ws.cell(row=r, column=17, value=3).font = AZUL
            for it in range(1, NIT):
                lo, hi = L(16 + 2 * (it - 1)), L(17 + 2 * (it - 1))
                mid = f"(({lo}{r}+{hi}{r})/2)"
                fmid = (f"({mid}+(C{r}/(D{r}*{mid}))^2/(2*9.81)+B{r}-{E2}-{dx}*(((DATOS!$B$32*(C{r}/(D{r}*{mid}))/((D{r}*{mid})/(D{r}+2*{mid}))^(2/3))^2+{Sf2})/2))")
                ws.cell(row=r, column=16 + 2 * it, value=f"=IF({fmid}>0,{lo}{r},{mid})").font = NEGRO
                ws.cell(row=r, column=17 + 2 * it, value=f"=IF({fmid}>0,{mid},{hi}{r})").font = NEGRO
    rlast = r0 + len(perf) - 1
    celda(ws, "P4", "Biseccion del tirante y (lo, hi) en %d iteraciones: f(y) = y + V^2/2g + z - E2 - dx (Sf + Sf2)/2" % NIT, SUB)
    # resumen
    rr = rlast + 2
    celda(ws, f"A{rr}", "RESUMEN", NEG)
    celda(ws, f"A{rr+1}", "Llenado maximo y/h"); celda(ws, f"B{rr+1}", f"=MAX(L{r0}:L{rlast})", NEGRO, "0.000")
    celda(ws, f"A{rr+2}", "Borde libre minimo (m)"); celda(ws, f"B{rr+2}", f"=MIN(M{r0}:M{rlast})", NEGRO, "0.000")
    celda(ws, f"A{rr+3}", "Froude maximo en el colector (sin el brink)"); celda(ws, f"B{rr+3}", f"=MAX(I{r0+1}:I{rlast})", NEGRO, "0.000")
    celda(ws, f"A{rr+4}", "Estaciones que no cumplen"); celda(ws, f"B{rr+4}", f"=COUNTIF(N{r0}:N{rlast},\"NO CUMPLE\")", NEGRO)
    celda(ws, f"A{rr+5}", "Nivel de agua en 0+000 (msnm)"); celda(ws, f"B{rr+5}", f"=G{rlast}", NEGRO, "0.000")
    # G200: referencia fija usada por EMPALME -> copiamos
    ws["G200"] = f"=G{rlast}"; ws["G200"].font = NEGRO; ws["F200"] = "NA en 0+000:"; ws["F200"].font = SUB
    ws.freeze_panes = "B6"
    return ws, rlast


def hoja_estructural(wb, R):
    ws = wb.create_sheet("ESTRUCTURAL"); D = dz.D
    cabecera(ws, "6. VERIFICACION ESTRUCTURAL (RNE E.060; cargas E.020 y rueda AASHTO LRFD HL-93)", [56, 12, 9, 64, 14])
    encabezado_tabla(ws, 4, ["ELEMENTO / PARAMETRO", "VALOR", "UND", "FORMULA / CRITERIO", "RESULTADO"])
    rows = []
    def sec(t): rows.append((t,))
    def it(*a): rows.append(a)
    sec("PARAMETROS")
    it("f'c", 210, "kg/cm2", "E.060"); it("fy", 4200, "kg/cm2", "Grado 60")
    it("Peso concreto armado", 2.4, "t/m3", "E.020"); it("Peso suelo / relleno", 1.8, "t/m3", "Verificar con EMS")
    it("Ko (reposo)", 0.5, "-", "Relleno compactado contra muro rigido")
    it("Sobrecarga peatonal", 0.5, "t/m2", "E.020"); it("Sobrecarga lateral vehiculo liviano", 1.0, "t/m2", "")
    it("Sobrecarga lateral camion (heq 1.50 m)", 2.7, "t/m2", "AASHTO 3.11.6.4")
    it("Rueda vehiculo liviano / moto", 1.0, "t", ""); it("Rueda camion HL-93", 7.26, "t", "AASHTO")
    it("Impacto", 0.33, "-", "AASHTO 3.6.2"); it("Huella de rueda", 0.25, "m", "AASHTO 3.6.1.2.5")
    it("Luz de calculo de losas (b + apoyo)", "=DATOS!$B$14+0.15", "m", "b + e muro (centro a centro aprox.)")
    it("Altura interior maxima del muro H", "=MAX(PERFIL_FLUJO!K6:K200)", "m", "hoja PERFIL_FLUJO")
    it("Altura interior minima del muro", "=MIN(PERFIL_FLUJO!K6:K200)", "m", "")
    # A losa superior vereda
    sec("A. LOSA SUPERIOR MONOLITICA e=0.10 - TRAMO NORMAL (marco 3/8\" @0.20)")
    it("Espesor", "=DATOS!$B$17", "m", "")
    it("Carga ultima", "=1.4*B8*B21+1.7*B11", "t/m2", "1.4 D + 1.7 L")
    it("Mu (simplemente apoyada, conservador)", "=B22*B18^2/8", "t.m/m", "wu L2/8")
    it("Peralte efectivo d", "=B21*100/2", "cm", "")
    it("As colocado", "=0.71/0.20", "cm2/m", "3/8\" @0.20")
    it("a", "=B25*B7/(0.85*B6*100)", "cm", "")
    it("Momento resistente fMn", "=0.9*B25*B7*(B24-B26/2)/100000", "t.m/m", "0.9 As fy (d - a/2)", "=IF(B27>=B23,\"CUMPLE\",\"NO CUMPLE\")")
    it("Cuantia minima 0.0018 b e", "=0.0018*100*B21*100", "cm2/m", "E.060 9.7.2", "=IF(B25>=B28,\"CUMPLE\",\"NO CUMPLE\")")
    # B losa cruce motos
    sec("B. LOSA SUPERIOR MONOLITICA e=0.10 - CRUCE DE MOTOS (marco 3/8\" @0.15)")
    it("Espesor", "=DATOS!$B$17", "m", "")
    it("Ancho de franja E", "=0.66+0.55*B18", "m", "AASHTO 4.6.2.1.3")
    it("Momento por rueda", "=B14*(1+B16)*(B18/4-B17/8)/B31", "t.m/m", "P (1+IM) (L/4 - c/8) / E")
    it("Mu", "=1.4*B8*B30*B18^2/8+1.7*B32", "t.m/m", "1.4 MD + 1.7 ML")
    it("Peralte efectivo d", "=B30*100/2", "cm", "")
    it("As colocado", "=0.71/0.15", "cm2/m", "3/8\" @0.15")
    it("a", "=B35*B7/(0.85*B6*100)", "cm", "")
    it("Momento resistente fMn", "=0.9*B35*B7*(B34-B36/2)/100000", "t.m/m", "", "=IF(B37>=B33,\"CUMPLE\",\"NO CUMPLE\")")
    it("Cuantia minima", "=0.0018*100*B30*100", "cm2/m", "E.060 9.7.2", "=IF(B35>=B38,\"CUMPLE\",\"NO CUMPLE\")")
    # C losa cruce camiones
    sec("C. LOSA SUPERIOR e=0.20 - CRUCE DE CAMIONES (doble marco 1/2\" @0.15)")
    it("Espesor", "=DATOS!$B$18", "m", "")
    it("Ancho de franja E", "=0.66+0.55*B18", "m", "AASHTO 4.6.2.1.3")
    it("Momento por rueda", "=B15*(1+B16)*(B18/4-B17/8)/B42", "t.m/m", "simplemente apoyada (conservador)")
    it("Mu", "=1.4*B8*B41*B18^2/8+1.7*B43", "t.m/m", "")
    it("Peralte efectivo d", "=(B41-0.04)*100-0.635", "cm", "recubrimiento 4 cm")
    it("As colocado", "=1.27/0.15", "cm2/m", "1/2\" @0.15 (una capa en traccion)")
    it("a", "=B46*B7/(0.85*B6*100)", "cm", "")
    it("Momento resistente fMn", "=0.9*B46*B7*(B45-B47/2)/100000", "t.m/m", "", "=IF(B48>=B44,\"CUMPLE\",\"NO CUMPLE\")")
    it("Cuantia minima", "=0.0018*100*B41*100", "cm2/m", "", "=IF(B46>=B49,\"CUMPLE\",\"NO CUMPLE\")")
    it("Cortante ultimo Vu", "=1.7*B15*(1+B16)*(B18-B45/100-B17/2)/B18/B42+1.4*B8*B41*B18/2", "t/m", "rueda a d del apoyo")
    it("Cortante resistente fVc", "=0.85*0.53*SQRT(B6)*100*B45/1000", "t/m", "", "=IF(B51>=B50,\"CUMPLE\",\"NO CUMPLE\")")
    # D muro tramo normal
    sec("D. MURO e=0.15 - TRAMO NORMAL (marco 3/8\" @0.20) - marco cerrado monolitico")
    it("Altura del muro H", "=B19", "m", "altura interior maxima")
    it("Empuje en reposo en la base p", "=B10*B9*B53", "t/m2", "Ko gamma H")
    it("Sobrecarga lateral q", "=B10*B11", "t/m2", "Ko x s/c peatonal")
    it("Momento de servicio", "=B54*B53^2/20+B55*B53^2/12", "t.m/m", "miembro de marco cerrado con extremos empotrados: p H2/20 (triangular) + q H2/12 (uniforme)")
    it("Mu", "=1.7*B56", "t.m/m", "1.7 empuje")
    it("Peralte efectivo d", "=(DATOS!$B$15-0.04)*100-0.48", "cm", "recubrimiento 4 cm")
    it("As colocado", "=0.71/0.20", "cm2/m", "3/8\" @0.20")
    it("a", "=B59*B7/(0.85*B6*100)", "cm", "")
    it("Momento resistente fMn", "=0.9*B59*B7*(B58-B60/2)/100000", "t.m/m", "", "=IF(B61>=B57,\"CUMPLE\",\"NO CUMPLE\")")
    it("Cuantia minima 0.0018 b e", "=0.0018*100*DATOS!$B$15*100", "cm2/m", "", "=IF(B59>=B62,\"CUMPLE\",\"NO CUMPLE\")")
    it("Vu", "=1.7*(B54*B53/2*0.6+B55*B53/2)", "t/m", "reaccion en la base (0.6 de la triangular)")
    it("fVc", "=0.85*0.53*SQRT(B6)*100*B58/1000", "t/m", "", "=IF(B64>=B63,\"CUMPLE\",\"NO CUMPLE\")")
    # E muro cruce motos
    sec("E. MURO e=0.15 - CRUCE DE MOTOS (marco 3/8\" @0.15)")
    it("Altura del muro H", "=B19", "m", "")
    it("Empuje en reposo en la base p", "=B10*B9*B66", "t/m2", "")
    it("Sobrecarga lateral q", "=B10*B12", "t/m2", "Ko x s/c vehiculo liviano")
    it("Mu", "=1.7*(B67*B66^2/20+B68*B66^2/12)", "t.m/m", "")
    it("As colocado", "=0.71/0.15", "cm2/m", "")
    it("a", "=B70*B7/(0.85*B6*100)", "cm", "")
    it("Momento resistente fMn", "=0.9*B70*B7*(B58-B71/2)/100000", "t.m/m", "", "=IF(B72>=B69,\"CUMPLE\",\"NO CUMPLE\")")
    # F muro cruce camiones
    sec("F. MURO e=0.15 - CRUCE DE CAMIONES (doble marco 1/2\" @0.15)")
    it("Altura del muro H", "=B19", "m", "")
    it("Empuje en reposo en la base p", "=B10*B9*B74", "t/m2", "")
    it("Sobrecarga lateral q", "=B10*B13", "t/m2", "Ko x s/c camion")
    it("Mu", "=1.7*(B75*B74^2/20+B76*B74^2/12)", "t.m/m", "")
    it("Peralte efectivo d", "=(DATOS!$B$15-0.04)*100-0.635", "cm", "")
    it("As colocado (una capa)", "=1.27/0.15", "cm2/m", "")
    it("a", "=B79*B7/(0.85*B6*100)", "cm", "")
    it("Momento resistente fMn", "=0.9*B79*B7*(B78-B80/2)/100000", "t.m/m", "", "=IF(B81>=B77,\"CUMPLE\",\"NO CUMPLE\")")
    # G losa de fondo
    sec("G. LOSA DE FONDO e=0.15 (marco 3/8\" @0.20)")
    it("Peso de la estructura por metro", "=B8*(DATOS!$B$14+2*DATOS!$B$15)*(DATOS!$B$17+DATOS!$B$16)+2*B8*DATOS!$B$15*B19", "t/m", "losas + muros (altura maxima)")
    it("Agua (colector lleno) y sobrecarga", "=1.0*DATOS!$B$14*B19+B11*(DATOS!$B$14+2*DATOS!$B$15)", "t/m", "")
    it("Reaccion del suelo", "=(B83+B84)/(DATOS!$B$14+2*DATOS!$B$15)", "t/m2", "uniforme")
    it("Mu", "=1.5*B85*B18^2/8", "t.m/m", "1.5 (D+L) wL2/8, simplemente apoyada (conservador)")
    it("Peralte efectivo d", "=(DATOS!$B$16-0.04)*100-0.48", "cm", "")
    it("As colocado", "=0.71/0.20", "cm2/m", "")
    it("a", "=B88*B7/(0.85*B6*100)", "cm", "")
    it("Momento resistente fMn", "=0.9*B88*B7*(B87-B89/2)/100000", "t.m/m", "", "=IF(B90>=B86,\"CUMPLE\",\"NO CUMPLE\")")
    it("Presion sobre el suelo", "=B85", "t/m2", "comparar con la capacidad portante del EMS", "=IF(B91<=1.0,\"CUMPLE (<= 1.0 kg/cm2)\",\"VERIFICAR EMS\")")
    # H tapa
    sec("H. TAPA DE REGISTRO 0.68 x 0.68 x 0.08 - 3/8\" @0.10 (rueda liviana; no hay registros en los cruces)")
    it("Espesor", 0.08, "m", ""); it("Luz de calculo", 0.64, "m", "luz libre 0.60 + apoyo 0.02 a cada lado")
    it("Ancho de franja", "=MIN(0.66+0.55*B94,0.68)", "m", "limitado al ancho de la tapa")
    it("Momento por rueda", "=B14*(1+B16)*(B94/4-B17/8)/B95", "t.m/m", "")
    it("Mu", "=1.4*B8*B93*B94^2/8+1.7*B96", "t.m/m", "")
    it("Peralte efectivo d", "=(B93-0.025)*100-0.48", "cm", "")
    it("As colocado", "=0.71/0.10", "cm2/m", "")
    it("a", "=B99*B7/(0.85*B6*100)", "cm", "")
    it("Momento resistente fMn", "=0.9*B99*B7*(B98-B100/2)/100000", "t.m/m", "", "=IF(B101>=B97,\"CUMPLE\",\"NO CUMPLE\")")
    r = 5
    for f in rows:
        if len(f) == 1:
            celda(ws, f"A{r}", f[0], NEG, fill=GRIS)
        else:
            vals = list(f) + [None] * (5 - len(f))
            fila(ws, r, vals, fonts=[NEGRO, None, NEGRO, NEGRO, NEG])
            if isinstance(vals[1], str) and (vals[1].startswith("=DATOS") or vals[1].startswith("=PERFIL") or vals[1].startswith("=MAX(PERFIL") or vals[1].startswith("=MIN(PERFIL")):
                ws[f"B{r}"].font = VERDE
            ws[f"B{r}"].number_format = "0.000"
        r += 1
    celda(ws, f"A{r+1}", "Los muros se verifican como miembros del marco cerrado (losa superior y de fondo vaciadas monoliticamente). En los cruces, el acero indicado va en ambas caras. Registros solo fuera de los cruces vehiculares.", SUB)
    return ws


def hoja_memoria(wb, R, rlast):
    ws = wb.create_sheet("MEMORIA", 0); D = dz.D
    cabecera(ws, "MEMORIA DE CALCULO - COLECTOR PLUVIAL TRAMO HOGAR DE REFUGIO TEMPORAL MUJERES VIOLENTADAS", [38, 120, 10])
    txt = [
        ("1. OBJETO", "Dimensionar el tramo del colector pluvial frontal que recibe el aporte del CAR Varones (CUI 2705619, dato de su memoria) y las seis cunetas del Hogar de Refugio Temporal Mujeres Violentadas (CUI 2675514), y lo entrega al registro R-01 del colector del CAR Mujeres (CUI 2717013). Longitud %.2f m, de la caja de llegada (0+000, limite con CAR Varones) a la caja de caida en el limite con CAR Mujeres." % dz.P_FIN),
        ("2. NORMATIVA", "RNE CE.040 Drenaje Pluvial (RM 126-2021-VIVIENDA); RNE E.020 Cargas; RNE E.060 Concreto Armado; AASHTO LRFD (rueda HL-93 en el cruce de camiones); Chow, Hidraulica de canales abiertos (paso estandar)."),
        ("3. HIDROLOGIA", "Metodo Racional con los coeficientes y areas de las memorias HIDRO-CE040 de cada proyecto, TR = 25 anos, tc = 15 min, I = 155.66 mm/h, FS = 1.15. Q = 258.7 + 301.9 = 560.6 L/s."),
        ("4. HIDRAULICA", "Colector cubierto de concreto armado b = 0.80 m, S = 0.30 %, n = 0.015. El fondo inicial (259.10) queda bajo las cunetas de arquitectura (NCF 259.70 a 260.12) y el fondo final (258.89) sobre el R-01 del receptor (258.72). La entrega es por caja de caida con poza de disipacion deprimida 0.40 m, ahogada por el tirante del receptor; el control del perfil es el tirante critico en el brink y el flujo en el colector es subcritico (F <= 0.90). El aporte externo cae en una caja de llegada con colchon de agua."),
        ("5. ESTRUCTURAS", "Losa superior e = 0.10 (tramo normal y cruce de motos) y e = 0.20 en el cruce de camiones; muros e = 0.15 (altura interior 1.40 a 1.65 m) como marco cerrado monolitico; losa de fondo e = 0.15; tapas de registro 0.68 x 0.68 x 0.08."),
        ("6. RESULTADOS", "Ver cuadro resumen. Secciones, acero y detalles en las laminas DP-01 a DP-10 y DA-01 a DA-03."),
    ]
    r = 4
    for a, b in txt:
        celda(ws, f"A{r}", a, NEG); celda(ws, f"B{r}", b, NEGRO, al="left"); ws.row_dimensions[r].height = 42; r += 1
    r += 1
    res = [
        ("Caudal de diseno del tramo (L/s)", "=CAUDALES!B12", "0.0"),
        ("Intensidad de diseno (mm/h)", "=DATOS!B11", "0.00"),
        ("Ancho interior adoptado (m)", "=DATOS!B14", "0.00"),
        ("Pendiente del fondo (%)", "=DATOS!B20*100", "0.00"),
        ("Cota de fondo inicial / final del colector (msnm)", f"=TEXT(DATOS!B19,\"0.00\")&\" / \"&TEXT(EMPALME!B8,\"0.00\")", None),
        ("Llenado maximo y/h", f"=PERFIL_FLUJO!B{rlast+3}", "0.000"),
        ("Borde libre minimo bajo losa (m)", f"=PERFIL_FLUJO!B{rlast+4}", "0.000"),
        ("Froude maximo en el colector", f"=PERFIL_FLUJO!B{rlast+5}", "0.00"),
        ("Estaciones hidraulicas que no cumplen", f"=PERFIL_FLUJO!B{rlast+6}", "0"),
        ("Cunetas con caida libre al colector (de 6)", "=COUNTIF(CUNETAS!L5:L10,\"CAIDA LIBRE\")", "0"),
        ("Resalto en la poza de la caja de caida", "=EMPALME!B19", None),
        ("Elementos estructurales que no cumplen", "=COUNTIF(ESTRUCTURAL!E:E,\"NO CUMPLE\")", "0"),
    ]
    for a, b, f in res:
        celda(ws, f"A{r}", a, NEGRO); c = celda(ws, f"B{r}", b, VERDE); c.alignment = Alignment(horizontal="left")
        if f: c.number_format = f
        r += 1
    r += 1
    celda(ws, f"A{r}", "NOTAS", NEG)
    notas = ["La cota de llegada del CAR Varones (260.18) es un supuesto (260.69 - 0.5 % x 102.36 m) y debe confirmarse con el proyecto CUI 2705619; solo afecta a la altura de la caida en la caja de llegada.",
             "La ubicacion UTM es referencial: el plano de arquitectura se georreferencio haciendo coincidir el R-01 del CAR Mujeres con la esquina sur-oeste del frente y el rumbo del lindero (azimut 49.54). Verificar en campo.",
             "Las cunetas de arquitectura se toman como dato (perfiles 01 a 12 del plano PLANTA GENERAL REFUGIO, version 03-10-2026)."]
    for n in notas:
        r += 1; celda(ws, f"B{r}", n, NEGRO, al="left"); ws.row_dimensions[r].height = 30
    return ws


def construir(fn=os.path.join(RAIZ, "entregables", "MEMORIA_CALCULO_COLECTOR_HOGAR_REFUGIO.xlsx")):
    R = dz.disenar()
    wb = openpyxl.Workbook(); wb.remove(wb.active)
    hoja_datos(wb, R); hoja_caudales(wb, R); hoja_cunetas(wb, R); hoja_empalme(wb, R)
    ws, rlast = hoja_perfil(wb, R); hoja_estructural(wb, R); hoja_memoria(wb, R, rlast)
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False
    os.makedirs(os.path.dirname(fn), exist_ok=True); wb.save(fn)
    return fn, R


if __name__ == "__main__":
    print(construir()[0])
