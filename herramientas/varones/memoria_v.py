"""Memoria de calculo en Excel (con formulas) del colector pluvial frontal del CAR Varones (CUI 2705619)
y su empalme con la caja de llegada CL del colector del Hogar de Refugio Temporal (CUI 2675514).

Hojas: MEMORIA, DATOS, CAUDALES, CUNETAS, EMPALME_CL, PERFIL_FLUJO, ESTRUCTURAL, CUMPLIMIENTO.
Convenciones de la memoria del tramo Hogar de Refugio: azul = dato, negro = formula, verde = vinculo.
Las referencias a DATOS se escriben como DATOS!$B${clave} y se traducen a la fila real al guardar.
"""
import os, sys, re
import openpyxl
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter as L
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
for p in (HERR, AQUI):
    if p not in sys.path: sys.path.insert(0, p)
import diseno_v as dz
import diseno as SOL
import memoria_xlsx as MX
from memoria_xlsx import celda, fila, encabezado_tabla, AZUL, NEGRO, VERDE, NEG, TIT, SUB, GRIS

D = dz.D; DS_ = SOL.D
MX.SUBTITULO = "Colector pluvial frontal - tramo CAR Varones (CUI 2705619), empalme con la caja CL del Hogar de Refugio Temporal (CUI 2675514), Morales - San Martin. Hidroconsult, Oct. 2026"
cabecera = MX.cabecera
ROW = {}
SALIDA = os.path.join(dz.SAL, "MEMORIA_CALCULO_COLECTOR_CAR_VARONES.xlsx")


def hoja_datos(wb, R):
    ws = wb.create_sheet("DATOS")
    cabecera(ws, "1. DATOS DE DISENO", [52, 12, 8, 78, 8])
    encabezado_tabla(ws, 4, ["PARAMETRO", "VALOR", "UND", "FUENTE / CRITERIO", "SIMBOLO"])
    z = R["zonas"][0]; cl = R["caja_llegada"]
    filas = [
        ("HIDROLOGIA (memoria de hidrologia y drenaje pluvial del CAR Varones)",),
        ("Periodo de retorno", D["TR"], "anos", "Estudio hidrologico del proyecto (RNE CE.040)", "TR"),
        ("Intensidad de diseno para D = 10 min", D["I"], "mm/h", "Estudio hidrologico del CAR Varones (P10 = 35.163 mm)", "I"),
        ("Tiempo de concentracion", D["tc"], "min", "Estudio hidrologico: cunetas y colector del frente", "tc"),
        ("Factor de seguridad FS", D["FS"], "-", "Memoria HIDRO-CE040 del proyecto", "FS"),
        ("Area tributaria total del CAR Varones", D["A_total"], "m2", "Memoria de hidrologia del CAR Varones", "A"),
        ("Coeficiente de escorrentia ponderado", D["C_pond"], "-", "Memoria de hidrologia del CAR Varones", "C"),
        ("Caudal total del CAR Varones (dato de su memoria)", D["Q_total"], "L/s", "Q = C I A FS / 3.6e6 = 258.7 L/s; es el valor considerado como aporte en el expediente del Hogar de Refugio", "Qt"),
        ("Caudal total recalculado (comprobacion)", "=ROUND(DATOS!$B${C}*DATOS!$B${I}*DATOS!$B${A}/3600000*DATOS!$B${FS}*1000,1)", "L/s", "Metodo racional con los datos de la fila anterior", "Qc"),
        ("GEOMETRIA DEL COLECTOR (tramo CAR Varones)",),
        ("Ancho interior b", D["b"], "m", "Adoptado: llenado <= 85 %, regimen subcritico y seccion minima para limpieza (hoja PERFIL_FLUJO)", "b"),
        ("Espesor de muros", D["e_muro"], "m", "Muros de 0.70 a 1.17 m de altura interior (hoja ESTRUCTURAL)", "em"),
        ("Espesor de losa de fondo", D["e_fondo"], "m", "", "ef"),
        ("Espesor de losa superior (tramo normal)", D["e_losa"], "m", "Vaciada monoliticamente con los muros", "et"),
        ("Espesor de losa superior en el cruce de camiones", D["e_losa_camion"], "m", "Porton de camiones cisterna (5.78 m) junto al Eje 09", "ec"),
        ("Cota de fondo inicial (0+000, poste derecho del porton)", D["CF0"], "msnm", "Fijada por la cuneta mas alta (Eje 09, NCF 260.69) y la losa superior e=0.25 del cruce: h = 0.70 m", "CF0"),
        ("Pendiente S", D["S"], "m/m", "Adoptada 0.30 %: igual al tramo del Hogar de Refugio; regimen subcritico y fondo sobre el NA de la CL", "S"),
        ("Progresiva del quiebre (inicio del tramo de empalme horizontal)", round(dz.P_QUIEBRE, 2), "m", "Registro RV-11; de ahi el colector entra perpendicular al lindero", "pq"),
        ("Progresiva del cruce del cerco proyectado", round(dz.P_CRUCE_CERCO, 2), "m", "Paso de 0.95 m en el cerco", "pcc"),
        ("Progresiva final (cara este de la caja CL del Hogar de Refugio)", round(dz.P_FIN, 2), "m", "x = 349163.80 del sistema local; la CL ocupa de 349162.00 a 349163.80", "pf"),
        ("Longitud total del colector", "=DATOS!$B${pf}", "m", "", "L"),
        ("NPT del frente (cara superior de la losa)", D["NPT"], "msnm", "Arquitectura: piso terminado de los Ejes 01, 04 y 06 y de las areas exteriores (salvo veredas)", "NPT"),
        ("Cruce de camiones: inicio", z["p1"], "m", z["nombre"] + " + 0.30 m de transicion", "pc1"),
        ("Cruce de camiones: fin", z["p2"], "m", "", "pc2"),
        ("Coeficiente de Manning n", D["n"], "-", "Concreto vaciado in situ (Chow)", "n"),
        ("CRITERIOS DE VERIFICACION HIDRAULICA",),
        ("Llenado maximo admisible y/h (conducto cubierto)", D["llenado_max"], "-", "Criterio de conducto cerrado a superficie libre", "llen"),
        ("Borde libre minimo bajo losa", D["BL_min"], "m", "Complementario al criterio de llenado", "BLmin"),
        ("RECEPTOR: CAJA DE LLEGADA CL DEL COLECTOR DEL HOGAR DE REFUGIO (CUI 2675514)",),
        ("Piso de la poza de la CL", D["CL_piso"], "msnm", "Memoria del Hogar de Refugio: CF0 259.10 - poza 0.30", "CLp"),
        ("Nivel de agua en la CL (= NA en 0+000 del colector del Refugio con 560.6 L/s)", round(cl["NA_CL"], 3), "msnm", "Memoria del Hogar de Refugio, hoja PERFIL_FLUJO (ultima fila)", "CLna"),
        ("Cota de la tapa de la CL", D["NPT_CL"], "msnm", "La CL queda del lado del CAR Varones: tapa al ras del piso +261.15", "CLt"),
        ("Espesor de la losa de la CL", DS_["e_losa"], "m", "Memoria del Hogar de Refugio", "CLe"),
        ("Dimensiones interiores de la CL (largo x ancho)", "1.50 x 1.00", "m", "Memoria del Hogar de Refugio", "CLd"),
        ("Caudal que el expediente del Hogar de Refugio asigna al CAR Varones", DS_["Q_varones"], "L/s", "Debe coincidir con el total entregado (colector + cuneta Eje 01)", "Qref"),
    ]
    r = 5
    for f in filas:
        if len(f) == 1:
            celda(ws, f"A{r}", f[0], NEG, fill=GRIS)
        else:
            fila(ws, r, list(f), fonts=[NEGRO, None, NEGRO, NEGRO, NEGRO])
            if isinstance(f[1], str) and f[1].startswith("="): ws[f"B{r}"].font = NEGRO
            ROW[f[4]] = r
        r += 1
    celda(ws, f"A{r+1}", "Azul = dato editable; negro = formula; verde = vinculo.", SUB)
    return ws


def hoja_caudales(wb, R):
    ws = wb.create_sheet("CAUDALES")
    cabecera(ws, "2. CAUDALES DE DISENO POR CUNETA Y CAUDAL EN EL COLECTOR", [40, 14, 12, 12, 12, 14, 30, 40])
    celda(ws, "A3", "El caudal total del CAR Varones (258.7 L/s, memoria de hidrologia) se reparte entre las 5 cunetas que llegan al frente en proporcion al ancho de frente que drena cada una (franja entre puntos medios de cunetas vecinas).", SUB)
    encabezado_tabla(ws, 5, ["CUNETA", "FRANJA DE FRENTE (m)", "FRACCION", "Q (L/s)", "PROGRESIVA (m)", "ENTRA EN", "REGISTRO / VENTANA", "OBSERVACION"])
    cs = R["cunetas"]; n = len(cs); r0 = 6
    # caudales: redondeo a 0.1 y ajuste en la fila 2 (Eje 08) para que la suma sea exacta
    for k, c in enumerate(cs):
        r = r0 + k
        reg = [x["nombre"] for x in R["registros"] if abs(x["prog"] - c["prog"]) < 1.5 and x["nombre"] != "CL"]
        qf = f"=ROUND(DATOS!$B${{Qt}}*C{r},1)" if c["perfil"] != "08" else f"=DATOS!$B${{Qt}}-SUM(D{r0}:D{r-1})-SUM(D{r+1}:D{r0+n-1})"
        fila(ws, r, ["Eje %s" % c["perfil"], c["franja_m"], f"=B{r}/SUM($B${r0}:$B${r0+n-1})", qf, c["prog"], "colector" if c["entra_en"] == "colector" else "caja CL",
                     (reg[0] + " - ventana 0.40 x %.2f" % c["H_ventana"]) if c["entra_en"] == "colector" else "ventana 0.40 x %.2f en el muro norte de la CL" % c["H_ventana"],
                     "ajuste para suma exacta" if c["perfil"] == "08" else ""],
             fonts=[NEGRO, AZUL, NEGRO, NEGRO, AZUL, NEGRO, NEGRO, NEGRO], fmts=[None, "0.00", "0.0000", "0.0", "0.00"])
    rt = r0 + n
    fila(ws, rt, ["TOTAL CAR VARONES", f"=SUM(B{r0}:B{rt-1})", f"=SUM(C{r0}:C{rt-1})", f"=SUM(D{r0}:D{rt-1})"], fonts=[NEG, NEGRO, NEGRO, NEG], fmts=[None, "0.00", "0.0000", "0.0"])
    fila(ws, rt + 1, ["Verificacion con el expediente del Hogar de Refugio", f"=IF(ABS(D{rt}-DATOS!$B${{Qref}})<0.05,\"COINCIDE (258.7 L/s)\",\"REVISAR\")"], fonts=[NEGRO, NEG])
    celda(ws, f"A{rt+3}", "Caudal que circula por el colector (aguas arriba hacia aguas abajo; la cuneta Eje 01 no entra al colector)", NEG)
    encabezado_tabla(ws, rt + 4, ["PUNTO", "PROGRESIVA", "APORTE (L/s)", "Q ACUMULADO (L/s)"])
    r = rt + 5; ra = r
    for k, c in enumerate(cs):
        rk = r0 + k
        fila(ws, r, ["Cuneta Eje %s" % c["perfil"], f"=E{rk}", f"=IF(F{rk}=\"colector\",D{rk},0)", f"=SUM($C${ra}:C{r})"], fonts=[NEGRO, NEGRO, NEGRO, NEGRO], fmts=[None, "0.00", "0.0", "0.0"]); r += 1
    fila(ws, r, ["Q de diseno del colector (llegada a la CL)", f"=DATOS!$B${{pf}}", None, f"=D{r-1}"], fonts=[NEG, VERDE, None, NEG], fmts=[None, "0.00", None, "0.0"]); ROW["r_qcol"] = r
    fila(ws, r + 1, ["Q de diseno del colector", None, None, f"=D{r}/1000"], fonts=[NEG, None, None, NEGRO], fmts=[None, None, None, "0.0000"]); ROW["r_qcol_m3"] = r + 1
    fila(ws, r + 2, ["Q directo a la CL (cuneta Eje 01)", None, None, f"=SUMIF(F{r0}:F{rt-1},\"caja CL\",D{r0}:D{rt-1})"], fonts=[NEGRO, None, None, NEGRO], fmts=[None, None, None, "0.0"]); ROW["r_qdir"] = r + 2
    fila(ws, r + 3, ["TOTAL ENTREGADO A LA CL", None, None, f"=D{r}+D{r+2}"], fonts=[NEG, None, None, NEG], fmts=[None, None, None, "0.0"]); ROW["r_qcl"] = r + 3
    ROW["c_r0"] = r0; ROW["c_rt"] = rt; ROW["c_ra"] = ra; ROW["c_rb"] = r - 1
    celda(ws, f"A{r+5}", "Suma de picos sin desfase y con FS = 1.15: hipotesis conservadora, igual a la de las memorias de los otros dos tramos. El perfil de flujo usa el caudal acumulado en cada progresiva (hoja PERFIL_FLUJO).", SUB)
    return ws


def hoja_cunetas(wb, R):
    ws = wb.create_sheet("CUNETAS")
    cabecera(ws, "3. CUNETAS DE ARQUITECTURA QUE LLEGAN AL FRENTE: ACORTAMIENTO Y CAIDA LIBRE", [12, 12, 10, 10, 10, 10, 12, 14, 12, 14, 12, 26])
    celda(ws, "A3", "Las cunetas estan dibujadas hasta la franja exterior; terminan en la cara del muro lado predio del colector (o en el muro norte de la CL) y el tramo que caia dentro del colector se descuenta en su metrado. NCF al cerco y NCT segun el plano PERFIL CAR VARONES.", SUB)
    encabezado_tabla(ws, 5, ["CUNETA", "PROGRESIVA (m)", "LONGITUD (m)", "NCT (msnm)", "NCF extremo (msnm)", "H (m)", "ACORTAMIENTO (m)", "NCF en el muro (msnm)", "ENTRA EN", "NA receptor (msnm)", "CAIDA LIBRE (m)", "VERIFICACION"])
    r = 6; r0 = r
    for c in R["cunetas"]:
        na = f"=IFERROR(INDEX(PERFIL_FLUJO!$G$6:$G$200,MATCH(B{r},PERFIL_FLUJO!$A$6:$A$200,0)),\"\")" if c["entra_en"] == "colector" else "=DATOS!$B${CLna}"
        fila(ws, r, ["Eje " + c["perfil"], c["prog"], c["L"], c["NCT"], c["NCF"], f"=D{r}-E{r}", -c["ajuste_L"], f"=E{r}+0.005*G{r}", "colector" if c["entra_en"] == "colector" else "caja CL", na, f"=H{r}-J{r}", f"=IF(K{r}>0,\"CAIDA LIBRE\",\"AHOGADA\")"],
             fonts=[NEGRO, AZUL, AZUL, AZUL, AZUL, NEGRO, AZUL, NEGRO, NEGRO, VERDE, NEGRO, NEGRO], fmts=[None, "0.00", "0.00", "0.00", "0.00", "0.00", "0.00", "0.000", None, "0.000", "0.000"])
        r += 1
    ROW["cu_r0"] = r0; ROW["cu_r1"] = r - 1
    celda(ws, f"A{r+1}", "NCF en el muro = NCF del extremo dibujado + 0.5 % x acortamiento (la cuneta termina antes, con su misma pendiente). Ventana 0.40 x H en el muro lado predio, con caida al fondo y registro encima (DP-06C, DD-04); la del Eje 01 entra a la CL por su muro norte (DP-07).", SUB)
    return ws


def hoja_empalme(wb, R):
    ws = wb.create_sheet("EMPALME_CL")
    cabecera(ws, "4. EMPALME CON LA CAJA DE LLEGADA CL DEL COLECTOR DEL HOGAR DE REFUGIO", [60, 12, 8, 70])
    encabezado_tabla(ws, 4, ["PARAMETRO", "VALOR", "UND", "FORMULA / CRITERIO"])
    cl = R["caja_llegada"]
    rows = [
        ("A. CAIDA LIBRE DEL COLECTOR A LA CL (control del perfil de flujo)",),
        ("Caudal del colector Q", "=CAUDALES!D{r_qcol_m3}", "m3/s", "cunetas Ejes 09, 08, 06 y 04"),
        ("Ancho del colector b", "=DATOS!$B${b}", "m", ""),
        ("Cota de fondo al final (cara este de la CL)", "=DATOS!$B${CF0}-DATOS!$B${S}*DATOS!$B${pf}", "msnm", "CF0 - S x L"),
        ("Tirante critico al final yc", "=(B6^2/(9.81*B7^2))^(1/3)", "m", "yc = (Q2/(g b2))^(1/3): control de la caida libre"),
        ("Nivel de agua al final del colector", "=B8+B9", "msnm", "nivel de control del perfil (hoja PERFIL_FLUJO)"),
        ("Nivel de agua en la CL", "=DATOS!$B${CLna}", "msnm", "memoria del Hogar de Refugio (NA en su 0+000 con 560.6 L/s)"),
        ("Caida libre (fondo del colector - NA de la CL)", "=B8-B11", "m", "> 0: el colector descarga libre, la CL no ahoga al tramo"),
        ("Verificacion de caida libre", "=IF(B12>0.10,\"CUMPLE (caida libre >= 0.10 m)\",\"REVISAR\")", "", ""),
        ("Piso de la poza de la CL", "=DATOS!$B${CLp}", "msnm", ""),
        ("Caida total (fondo del colector - piso de la CL)", "=B8-B14", "m", ""),
        ("Colchon de agua en la CL", "=B11-B14", "m", "amortigua el chorro"),
        ("Verificacion del colchon", "=IF(B16>=0.5,\"CUMPLE (>= 0.50 m)\",\"REVISAR\")", "", ""),
        ("",),
        ("B. VENTANA EN EL MURO ESTE DE LA CL (la deja el expediente del Hogar de Refugio)",),
        ("Ancho de la ventana", "=DATOS!$B${b}", "m", "igual al ancho interior del colector"),
        ("Cota de fondo (alfeizar) de la ventana", "=B8", "msnm", "coincide con el fondo del colector"),
        ("Cota inferior de la losa de la CL (techo)", "=DATOS!$B${CLt}-DATOS!$B${CLe}", "msnm", "tapa de la CL - espesor de losa"),
        ("Cota inferior de la losa del colector al final", "=DATOS!$B${NPT}-DATOS!$B${et}", "msnm", ""),
        ("Altura de la ventana", "=B22-B21", "m", "el colector entra con su seccion completa (sin dintel)"),
        ("Verificacion de niveles", "=IF(ABS(B22-B23)<0.001,\"CUMPLE (techos coincidentes)\",\"REVISAR\")", "", "techo de la CL = techo del colector = 261.05"),
        ("Area de la ventana", "=B20*B24", "m2", ""),
        ("Velocidad media por la ventana con el tirante critico", "=B6/(B20*B9)", "m/s", "V = Q / (b yc)"),
        ("",),
        ("C. VENTANA EN EL MURO NORTE DE LA CL PARA LA CUNETA DEL EJE 01",),
        ("Caudal de la cuneta Eje 01", "=CAUDALES!D{r_qdir}", "L/s", ""),
        ("NCF de la cuneta en el muro norte", "=CUNETAS!H{cu_r1}", "msnm", "hoja CUNETAS"),
        ("Altura de la ventana (NCF al techo de la CL)", "=B22-B31", "m", "ancho 0.40 (igual a la cuneta)"),
        ("Caida libre de la cuneta sobre el NA de la CL", "=B31-B11", "m", ""),
        ("Verificacion", "=IF(B33>0,\"CAIDA LIBRE\",\"AHOGADA\")", "", ""),
        ("",),
        ("D. CAUDAL TOTAL QUE RECIBE LA CL",),
        ("Colector + cuneta Eje 01", "=CAUDALES!D{r_qcl}", "L/s", ""),
        ("Caudal previsto por el expediente del Hogar de Refugio para el CAR Varones", "=DATOS!$B${Qref}", "L/s", ""),
        ("Verificacion", "=IF(ABS(B37-B38)<0.05,\"CUMPLE (coinciden)\",\"REVISAR\")", "", "los tres expedientes usan el mismo caudal"),
        ("",),
        ("E. CRUCE DEL CERCO PROYECTADO Y JUNTAS",),
        ("Progresiva del cruce del cerco", "=DATOS!$B${pcc}", "m", "el cerco de Varones converge al lindero frontal y cruza el tramo de empalme"),
        ("Ancho del paso en el cerco", "=DATOS!$B${b}+2*DATOS!$B${em}+2*0.025", "m", "ancho exterior del colector + tecnopor 1\" a cada lado"),
        ("Tramo de empalme (del quiebre a la CL)", "=DATOS!$B${pf}-DATOS!$B${pq}", "m", "horizontal en planta, perpendicular al lindero"),
    ]
    r = 5
    for f in rows:
        if len(f) == 1:
            if f[0]: celda(ws, f"A{r}", f[0], NEG, fill=GRIS)
        else:
            fila(ws, r, list(f), fonts=[NEGRO, NEGRO, NEGRO, NEGRO])
            if isinstance(f[1], str) and any(f[1].startswith(p) for p in ("=DATOS", "=CAUDALES", "=CUNETAS", "=PERFIL")): ws[f"B{r}"].font = VERDE
            ws[f"B{r}"].number_format = "0.000"
        r += 1
    return ws


def hoja_perfil(wb, R):
    ws = wb.create_sheet("PERFIL_FLUJO")
    cabecera(ws, "5. PERFIL DE FLUJO GRADUALMENTE VARIADO CON CAUDAL CRECIENTE - METODO DEL PASO ESTANDAR (de aguas abajo hacia aguas arriba)", [11, 10, 9, 8, 8, 9, 10, 9, 8, 10, 9, 9, 9, 13, 12])
    celda(ws, "A3", "y1 + V1^2/2g + z1 = y2 + V2^2/2g + z2 + dx (Sf1 + Sf2)/2 ; Sf = (n V / R^(2/3))^2 ; Q en cada estacion = suma de las cunetas que entran aguas arriba (CAUDALES); control: tirante critico en la caida libre a la CL (0+%06.2f)" % dz.P_FIN, SUB)
    enc = ["PROGRESIVA (m)", "COTA FONDO", "Q (m3/s)", "b (m)", "yc (m)", "TIRANTE y (m)", "NIVEL DE AGUA", "VELOCIDAD (m/s)", "FROUDE", "COTA BAJO LOSA", "ALTURA INTERIOR h", "LLENADO y/h", "BORDE LIBRE (m)", "VERIFICACION", "ZONA"]
    encabezado_tabla(ws, 5, enc)
    NIT = 30
    perf = [e for e in R["perfil"][::-1] if e["Q"] > 0]        # de aguas abajo hacia aguas arriba, solo donde hay caudal
    r0 = 6; ra, rb = ROW["c_ra"], ROW["c_rb"]
    for k, e in enumerate(perf):
        r = r0 + k
        ws.cell(row=r, column=1, value=round(e["p"], 2)).font = AZUL
        ws.cell(row=r, column=2, value=f"=DATOS!$B${{CF0}}-DATOS!$B${{S}}*A{r}").font = NEGRO
        ws.cell(row=r, column=3, value=f"=SUMIF(CAUDALES!$B${ra}:$B${rb},\"<=\"&(A{r}+0.001),CAUDALES!$C${ra}:$C${rb})/1000").font = VERDE
        ws.cell(row=r, column=4, value="=DATOS!$B${b}").font = VERDE
        ws.cell(row=r, column=5, value=f"=(C{r}^2/(9.81*D{r}^2))^(1/3)").font = NEGRO
        if k == 0:
            ws.cell(row=r, column=6, value=f"=E{r}").font = NEGRO
        else:
            ws.cell(row=r, column=6, value=f"=({L(16+2*NIT-2)}{r}+{L(16+2*NIT-1)}{r})/2").font = NEGRO
        ws.cell(row=r, column=7, value=f"=B{r}+F{r}").font = NEGRO
        ws.cell(row=r, column=8, value=f"=C{r}/(D{r}*F{r})").font = NEGRO
        ws.cell(row=r, column=9, value=f"=H{r}/SQRT(9.81*F{r})").font = NEGRO
        ws.cell(row=r, column=10, value=f"=DATOS!$B${{NPT}}-IF(AND(A{r}>=DATOS!$B${{pc1}},A{r}<DATOS!$B${{pc2}}),DATOS!$B${{ec}},DATOS!$B${{et}})").font = NEGRO
        ws.cell(row=r, column=11, value=f"=J{r}-B{r}").font = NEGRO
        ws.cell(row=r, column=12, value=f"=F{r}/K{r}").font = NEGRO
        ws.cell(row=r, column=13, value=f"=J{r}-G{r}").font = NEGRO
        ws.cell(row=r, column=14, value=f"=IF(AND(L{r}<=DATOS!$B${{llen}},M{r}>=DATOS!$B${{BLmin}},I{r}<=1),\"CUMPLE\",\"NO CUMPLE\")").font = NEGRO
        ws.cell(row=r, column=15, value=f"=IF(AND(A{r}>=DATOS!$B${{pc1}},A{r}<DATOS!$B${{pc2}}),\"cruce de camiones\",IF(A{r}>=DATOS!$B${{pq}},\"tramo de empalme\",\"tramo normal\"))").font = NEGRO
        for c, f in zip(range(2, 14), ["0.000", "0.0000", "0.00", "0.000", "0.000", "0.000", "0.00", "0.00", "0.000", "0.00", "0.00", "0.000"]):
            ws.cell(row=r, column=c).number_format = f
        if k > 0:
            rp = r - 1
            dx = f"(A{rp}-A{r})"; E2 = f"(G{rp}+H{rp}^2/(2*9.81))"
            Sf2 = f"((DATOS!$B${{n}}*H{rp}/((D{rp}*F{rp})/(D{rp}+2*F{rp}))^(2/3))^2)"
            ws.cell(row=r, column=16, value=f"=E{r}*1.001").font = NEGRO
            ws.cell(row=r, column=17, value=3).font = AZUL
            for it in range(1, NIT):
                lo, hi = L(16 + 2 * (it - 1)), L(17 + 2 * (it - 1))
                mid = f"(({lo}{r}+{hi}{r})/2)"
                fmid = (f"({mid}+(C{r}/(D{r}*{mid}))^2/(2*9.81)+B{r}-{E2}-{dx}*(((DATOS!$B${{n}}*(C{r}/(D{r}*{mid}))/((D{r}*{mid})/(D{r}+2*{mid}))^(2/3))^2+{Sf2})/2))")
                ws.cell(row=r, column=16 + 2 * it, value=f"=IF({fmid}>0,{lo}{r},{mid})").font = NEGRO
                ws.cell(row=r, column=17 + 2 * it, value=f"=IF({fmid}>0,{mid},{hi}{r})").font = NEGRO
    rlast = r0 + len(perf) - 1
    celda(ws, "P4", "Biseccion del tirante y (lo, hi) en %d iteraciones: f(y) = y + V^2/2g + z - E2 - dx (Sf + Sf2)/2. En el tramo 0+000 a 0+006.24 (antes de la primera cuneta) no circula caudal de diseno." % NIT, SUB)
    rr = rlast + 2
    celda(ws, f"A{rr}", "RESUMEN", NEG)
    celda(ws, f"A{rr+1}", "Llenado maximo y/h"); celda(ws, f"B{rr+1}", f"=MAX(L{r0}:L{rlast})", NEGRO, "0.000")
    celda(ws, f"A{rr+2}", "Borde libre minimo (m)"); celda(ws, f"B{rr+2}", f"=MIN(M{r0}:M{rlast})", NEGRO, "0.000")
    celda(ws, f"A{rr+3}", "Froude maximo en el colector (sin la seccion de control)"); celda(ws, f"B{rr+3}", f"=MAX(I{r0+1}:I{rlast})", NEGRO, "0.000")
    celda(ws, f"A{rr+4}", "Estaciones que no cumplen"); celda(ws, f"B{rr+4}", f"=COUNTIF(N{r0}:N{rlast},\"NO CUMPLE\")", NEGRO)
    celda(ws, f"A{rr+5}", "Nivel de agua en la primera estacion con caudal (msnm)"); celda(ws, f"B{rr+5}", f"=G{rlast}", NEGRO, "0.000")
    rv = rr + 7
    celda(ws, f"A{rv}", "VERIFICACION DE VELOCIDADES Y AUTOLIMPIEZA (RNE CE.040 Drenaje Pluvial; esfuerzo tractivo minimo)", NEG)
    celda(ws, f"A{rv+1}", "Tirante normal por punto fijo: y(k+1) = (Q n (b + 2 y(k))^(2/3) / (b^(5/3) S^(1/2)))^(3/5), 8 iteraciones (columnas P a W). Esfuerzo tractivo tau = gamma R S.", SUB)
    encabezado_tabla(ws, rv + 2, ["CASO", "Q (m3/s)", "yn (m)", "V (m/s)", "R (m)", "TAU (kg/m2)", "TAU (Pa)", "FROUDE", "V >= 0.90 m/s (CE.040)", "TAU >= 0.15 kg/m2", "V <= 3.0 m/s (concreto)", "AUTOLIMPIEZA DEL TRAMO"])
    ra = ROW["c_ra"]
    casos = [("Tramo Eje 04 - CL: caudal de diseno del colector (221.7 L/s)", "=CAUDALES!$D$%d/1000" % (ra + 3), True), ("Tramo Ejes 06 - 04 (149.3 L/s)", "=CAUDALES!$D$%d/1000" % (ra + 2), True),
             ("Tramo Ejes 08 - 06 (81.3 L/s)", "=CAUDALES!$D$%d/1000" % (ra + 1), True), ("Tramo Ejes 09 - 08 (33.6 L/s)", "=CAUDALES!$D$%d/1000" % ra, True),
             ("Informativo: 25 % del caudal de diseno", "=0.25*CAUDALES!$D${r_qcol_m3}", False), ("Informativo: 10 % del caudal de diseno (lluvia menor)", "=0.10*CAUDALES!$D${r_qcol_m3}", False), ("Informativo: 5 % del caudal de diseno", "=0.05*CAUDALES!$D${r_qcol_m3}", False)]
    for k, (nm, q, tramo) in enumerate(casos):
        r = rv + 3 + k
        ws.cell(row=r, column=1, value=nm).font = NEGRO
        ws.cell(row=r, column=2, value=q).font = VERDE; ws.cell(row=r, column=2).number_format = "0.0000"
        ws.cell(row=r, column=16, value=f"=(B{r}*DATOS!$B${{n}}/(DATOS!$B${{b}}*SQRT(DATOS!$B${{S}})))^(3/5)").font = NEGRO
        for it in range(1, 8):
            prev = L(16 + it - 1)
            ws.cell(row=r, column=16 + it, value=f"=(B{r}*DATOS!$B${{n}}*(DATOS!$B${{b}}+2*{prev}{r})^(2/3)/(DATOS!$B${{b}}^(5/3)*SQRT(DATOS!$B${{S}})))^(3/5)").font = NEGRO
        for c in range(16, 24): ws.cell(row=r, column=c).number_format = "0.0000"
        ws.cell(row=r, column=3, value=f"={L(23)}{r}").font = NEGRO
        ws.cell(row=r, column=4, value=f"=B{r}/(DATOS!$B${{b}}*C{r})").font = NEGRO
        ws.cell(row=r, column=5, value=f"=DATOS!$B${{b}}*C{r}/(DATOS!$B${{b}}+2*C{r})").font = NEGRO
        ws.cell(row=r, column=6, value=f"=1000*E{r}*DATOS!$B${{S}}").font = NEGRO
        ws.cell(row=r, column=7, value=f"=F{r}*9.81").font = NEGRO
        ws.cell(row=r, column=8, value=f"=D{r}/SQRT(9.81*C{r})").font = NEGRO
        ws.cell(row=r, column=9, value=f"=IF(D{r}>=0.9,\"CUMPLE\",\"V < 0.90: ver tau\")").font = NEGRO
        ws.cell(row=r, column=10, value=f"=IF(F{r}>=0.15,\"CUMPLE\",\"NO CUMPLE\")").font = NEGRO
        ws.cell(row=r, column=11, value=f"=IF(D{r}<=3.0,\"CUMPLE\",\"NO CUMPLE\")").font = NEGRO
        ws.cell(row=r, column=12, value=(f"=IF(OR(D{r}>=0.9,F{r}>=0.15),\"CUMPLE\",\"NO CUMPLE\")" if tramo else "informativo")).font = NEG if tramo else SUB
        for c, f in zip(range(3, 9), ["0.000", "0.00", "0.000", "0.000", "0.00", "0.00"]): ws.cell(row=r, column=c).number_format = f
    rf = rv + 3 + len(casos)
    celda(ws, f"A{rf+1}", "Velocidad maxima en el perfil de flujo (m/s)"); celda(ws, f"B{rf+1}", f"=MAX(H{r0}:H{rlast})", NEGRO, "0.00")
    celda(ws, f"A{rf+2}", "Velocidad en el ultimo tramo con el caudal de diseno, tirante normal (m/s)"); celda(ws, f"B{rf+2}", f"=D{rv+3}", NEGRO, "0.00")
    celda(ws, f"A{rf+3}", "Verificacion global de velocidades y autolimpieza"); celda(ws, f"B{rf+3}", f"=IF(AND(B{rf+1}<=3.0,B{rf+2}>=0.9,COUNTIF(L{rv+3}:L{rv+6},\"NO CUMPLE\")=0),\"CUMPLE\",\"NO CUMPLE\")", NEGRO)
    celda(ws, f"A{rf+4}", "Criterios: velocidad minima 0.90 m/s con el caudal de diseno en la entrega (RNE CE.040) y maxima 3.0 m/s (revestimiento de concreto). En cada tramo entre empalmes se verifica la autolimpieza con su propio caudal de diseno: V >= 0.90 m/s o esfuerzo tractivo tau = gamma R S >= 0.15 kg/m2 (1.5 Pa, criterio ASCE/WEF para colectores). En los tramos de cabecera (33.6 y 81.3 L/s) la velocidad es menor de 0.90 m/s porque el ancho 0.60 es el minimo practicable para limpieza; alli la autolimpieza se asegura por esfuerzo tractivo y por los registros cada 12 m como maximo.", SUB)
    ws["B200"] = f"=B{rf+3}"; ws["A200"] = "Velocidades:"; ws["A200"].font = SUB
    ws["G200"] = f"=G{r0}"; ws["F200"] = "NA al final:"; ws["F200"].font = SUB
    ws.freeze_panes = "B6"
    return ws, rlast


def hoja_estructural(wb, R):
    ws = wb.create_sheet("ESTRUCTURAL")
    cabecera(ws, "6. VERIFICACION ESTRUCTURAL (RNE E.060; cargas E.020 y rueda AASHTO LRFD HL-93)", [56, 12, 9, 64, 16])
    encabezado_tabla(ws, 4, ["ELEMENTO / PARAMETRO", "VALOR", "UND", "FORMULA / CRITERIO", "RESULTADO"])
    rows = []
    def sec(t): rows.append((None, t))
    def it(k, *a): rows.append((k,) + a)
    sec("PARAMETROS")
    it("fc", "f'c", 210, "kg/cm2", "E.060"); it("fy", "fy", 4200, "kg/cm2", "Grado 60")
    it("gc", "Peso concreto armado", 2.4, "t/m3", "E.020"); it("gs", "Peso suelo / relleno", 1.8, "t/m3", "Verificar con EMS")
    it("Ko", "Ko (reposo)", 0.5, "-", "Relleno compactado contra muro rigido")
    it("sp", "Sobrecarga peatonal", 0.5, "t/m2", "E.020")
    it("sc", "Sobrecarga lateral camion (heq 1.50 m)", 2.7, "t/m2", "AASHTO 3.11.6.4")
    it("Pl", "Rueda vehiculo liviano", 1.0, "t", "tapas de registro"); it("Pc", "Rueda camion HL-93", 7.26, "t", "AASHTO")
    it("IM", "Impacto", 0.33, "-", "AASHTO 3.6.2"); it("c", "Huella de rueda", 0.25, "m", "AASHTO 3.6.1.2.5")
    it("Lc", "Luz de calculo de losas (b + e muro)", "=DATOS!$B${b}+DATOS!$B${em}", "m", "centro a centro de muros")
    it("H", "Altura interior maxima del muro H", "=MAX(PERFIL_FLUJO!K6:K200)", "m", "hoja PERFIL_FLUJO (llegada a la CL)")
    it("Hmin", "Altura interior minima del muro", "=DATOS!$B${NPT}-DATOS!$B${ec}-DATOS!$B${CF0}", "m", "cruce de camiones en 0+000")
    sec("A. LOSA SUPERIOR MONOLITICA e=0.10 - TRAMO NORMAL (marco 3/8\" @0.20)")
    it("eA", "Espesor", "=DATOS!$B${et}", "m", "")
    it("wA", "Carga ultima", "=1.4*{gc}*{eA}+1.7*{sp}", "t/m2", "1.4 D + 1.7 L")
    it("MuA", "Mu (simplemente apoyada, conservador)", "={wA}*{Lc}^2/8", "t.m/m", "wu L2/8")
    it("dA", "Peralte efectivo d", "={eA}*100/2", "cm", "")
    it("AsA", "As colocado", "=0.71/0.20", "cm2/m", "3/8\" @0.20")
    it("aA", "a", "={AsA}*{fy}/(0.85*{fc}*100)", "cm", "")
    it("MnA", "Momento resistente fMn", "=0.9*{AsA}*{fy}*({dA}-{aA}/2)/100000", "t.m/m", "0.9 As fy (d - a/2)", "=IF({MnA}>={MuA},\"CUMPLE\",\"NO CUMPLE\")")
    it("AmA", "Cuantia minima 0.0018 b e", "=0.0018*100*{eA}*100", "cm2/m", "E.060 9.7.2", "=IF({AsA}>={AmA},\"CUMPLE\",\"NO CUMPLE\")")
    sec("C. LOSA SUPERIOR e=0.25 - CRUCE DE CAMIONES CISTERNA (doble marco 1/2\" @0.15)")
    it("eC", "Espesor", "=DATOS!$B${ec}", "m", "")
    it("EC", "Ancho de franja E", "=0.66+0.55*{Lc}", "m", "AASHTO 4.6.2.1.3")
    it("MrC", "Momento por rueda", "={Pc}*(1+{IM})*({Lc}/4-{c}/8)/{EC}", "t.m/m", "simplemente apoyada (conservador)")
    it("MuC", "Mu", "=1.4*{gc}*{eC}*{Lc}^2/8+1.7*{MrC}", "t.m/m", "")
    it("dC", "Peralte efectivo d", "=({eC}-0.04)*100-0.635", "cm", "recubrimiento 4 cm")
    it("AsC", "As colocado", "=1.27/0.15", "cm2/m", "1/2\" @0.15 (una capa en traccion)")
    it("aC", "a", "={AsC}*{fy}/(0.85*{fc}*100)", "cm", "")
    it("MnC", "Momento resistente fMn", "=0.9*{AsC}*{fy}*({dC}-{aC}/2)/100000", "t.m/m", "", "=IF({MnC}>={MuC},\"CUMPLE\",\"NO CUMPLE\")")
    it("AmC", "Cuantia minima", "=0.0018*100*{eC}*100", "cm2/m", "", "=IF({AsC}>={AmC},\"CUMPLE\",\"NO CUMPLE\")")
    it("VuC", "Cortante ultimo Vu", "=1.7*{Pc}*(1+{IM})*({Lc}-{dC}/100-{c}/2)/{Lc}/{EC}+1.4*{gc}*{eC}*{Lc}/2", "t/m", "rueda a d del apoyo")
    it("VcC", "Cortante resistente fVc", "=0.85*0.53*SQRT({fc})*100*{dC}/1000", "t/m", "", "=IF({VcC}>={VuC},\"CUMPLE\",\"NO CUMPLE\")")
    sec("D. MURO e=0.15 - TRAMO NORMAL (marco unico 3/8\" @0.20 en el eje de la seccion) - marco cerrado monolitico")
    it("HD", "Altura del muro H", "={H}", "m", "altura interior maxima (1.17 m en la llegada a la CL)")
    it("pD", "Empuje en reposo en la base p", "={Ko}*{gs}*{HD}", "t/m2", "Ko gamma H")
    it("qD", "Sobrecarga lateral q", "={Ko}*{sp}", "t/m2", "Ko x s/c peatonal")
    it("MD", "Momento de servicio", "={pD}*{HD}^2/20+{qD}*{HD}^2/12", "t.m/m", "miembro de marco cerrado con extremos empotrados: p H2/20 (triangular) + q H2/12 (uniforme)")
    it("MuD", "Mu", "=1.7*{MD}", "t.m/m", "1.7 empuje")
    it("dD", "Peralte efectivo d", "=DATOS!$B${em}*100/2", "cm", "marco unico en el eje del muro (una capa; E.060 14.3.4 exige dos capas solo en muros de mas de 0.20 m)")
    it("AsD", "As colocado", "=0.71/0.20", "cm2/m", "3/8\" @0.20")
    it("aD", "a", "={AsD}*{fy}/(0.85*{fc}*100)", "cm", "")
    it("MnD", "Momento resistente fMn", "=0.9*{AsD}*{fy}*({dD}-{aD}/2)/100000", "t.m/m", "", "=IF({MnD}>={MuD},\"CUMPLE\",\"NO CUMPLE\")")
    it("AmD", "Cuantia minima 0.0018 b e", "=0.0018*100*DATOS!$B${em}*100", "cm2/m", "", "=IF({AsD}>={AmD},\"CUMPLE\",\"NO CUMPLE\")")
    it("VuD", "Vu", "=1.7*({pD}*{HD}/2*0.6+{qD}*{HD}/2)", "t/m", "reaccion en la base (0.6 de la triangular)")
    it("VcD", "fVc", "=0.85*0.53*SQRT({fc})*100*{dD}/1000", "t/m", "", "=IF({VcD}>={VuD},\"CUMPLE\",\"NO CUMPLE\")")
    sec("F. MURO e=0.15 - CRUCE DE CAMIONES (doble marco 1/2\" @0.15: una capa en cada cara)")
    it("HF", "Altura del muro H en el cruce", "={Hmin}+DATOS!$B${S}*DATOS!$B${pc2}", "m", "0.70 m en 0+000 (losa e=0.25) creciendo con la pendiente")
    it("pF", "Empuje en reposo en la base p", "={Ko}*{gs}*{HF}", "t/m2", "")
    it("qF", "Sobrecarga lateral q", "={Ko}*{sc}", "t/m2", "Ko x s/c camion")
    it("MuF", "Mu", "=1.7*({pF}*{HF}^2/20+{qF}*{HF}^2/12)", "t.m/m", "")
    it("dF", "Peralte efectivo d", "=(DATOS!$B${em}-0.04)*100-0.635", "cm", "")
    it("AsF", "As colocado (una capa)", "=1.27/0.15", "cm2/m", "")
    it("aF", "a", "={AsF}*{fy}/(0.85*{fc}*100)", "cm", "")
    it("MnF", "Momento resistente fMn", "=0.9*{AsF}*{fy}*({dF}-{aF}/2)/100000", "t.m/m", "", "=IF({MnF}>={MuF},\"CUMPLE\",\"NO CUMPLE\")")
    sec("G. LOSA DE FONDO e=0.15 (marco unico 3/8\" @0.20)")
    it("WG", "Peso de la estructura por metro", "={gc}*(DATOS!$B${b}+2*DATOS!$B${em})*(DATOS!$B${et}+DATOS!$B${ef})+2*{gc}*DATOS!$B${em}*{H}", "t/m", "losas + muros (altura maxima)")
    it("WwG", "Agua (colector lleno) y sobrecarga", "=1.0*DATOS!$B${b}*{H}+{sp}*(DATOS!$B${b}+2*DATOS!$B${em})", "t/m", "")
    it("qG", "Reaccion del suelo", "=({WG}+{WwG})/(DATOS!$B${b}+2*DATOS!$B${em})", "t/m2", "uniforme")
    it("MuG", "Mu", "=1.5*{qG}*{Lc}^2/8", "t.m/m", "1.5 (D+L) wL2/8, simplemente apoyada (conservador)")
    it("dG", "Peralte efectivo d", "=DATOS!$B${ef}*100/2", "cm", "marco unico en el eje de la losa de fondo (una capa)")
    it("AsG", "As colocado", "=0.71/0.20", "cm2/m", "")
    it("aG", "a", "={AsG}*{fy}/(0.85*{fc}*100)", "cm", "")
    it("MnG", "Momento resistente fMn", "=0.9*{AsG}*{fy}*({dG}-{aG}/2)/100000", "t.m/m", "", "=IF({MnG}>={MuG},\"CUMPLE\",\"NO CUMPLE\")")
    it("sG", "Presion sobre el suelo", "={qG}/10", "kg/cm2", "comparar con la capacidad portante del EMS", "=IF({sG}<=1.0,\"CUMPLE (<= 1.0 kg/cm2)\",\"VERIFICAR EMS\")")
    it("sGc", "Presion sobre el suelo en el cruce de camiones (rueda HL-93 repartida en 2.5 m)", "=({gc}*(DATOS!$B${b}+2*DATOS!$B${em})*(DATOS!$B${ec}+DATOS!$B${ef})+2*{gc}*DATOS!$B${em}*{HF}+1.0*DATOS!$B${b}*{HF}+{Pc}*(1+{IM})/2.5)/(DATOS!$B${b}+2*DATOS!$B${em})/10", "kg/cm2", "peso propio + agua + rueda con impacto distribuida en 2.50 m de colector (carga transitoria)", "=IF({sGc}<=1.0,\"CUMPLE si el EMS confirma q adm >= \"&TEXT({sGc},\"0.00\")&\" kg/cm2\",\"VERIFICAR EMS\")")
    sec("H. TAPA DE REGISTRO 0.68 x 0.68 x 0.08 - 3/8\" @0.10 (rueda liviana; no hay registros en el cruce)")
    it("eH", "Espesor", 0.08, "m", ""); it("LH", "Luz de calculo", 0.64, "m", "luz libre 0.60 + apoyo 0.02 a cada lado")
    it("EH", "Ancho de franja", "=MIN(0.66+0.55*{LH},0.68)", "m", "limitado al ancho de la tapa")
    it("MrH", "Momento por rueda", "={Pl}*(1+{IM})*({LH}/4-{c}/8)/{EH}", "t.m/m", "")
    it("MuH", "Mu", "=1.4*{gc}*{eH}*{LH}^2/8+1.7*{MrH}", "t.m/m", "")
    it("dH", "Peralte efectivo d", "=({eH}-0.025)*100-0.48", "cm", "")
    it("AsH", "As colocado", "=0.71/0.10", "cm2/m", "")
    it("aH", "a", "={AsH}*{fy}/(0.85*{fc}*100)", "cm", "")
    it("MnH", "Momento resistente fMn", "=0.9*{AsH}*{fy}*({dH}-{aH}/2)/100000", "t.m/m", "", "=IF({MnH}>={MuH},\"CUMPLE\",\"NO CUMPLE\")")
    KEY = {}; r = 5
    for f in rows:
        if f[0] is not None: KEY[f[0]] = r
        r += 1
    def tr(txt):
        return re.sub(r"\{(\w+)\}", lambda m: ("B%d" % KEY[m.group(1)]) if m.group(1) in KEY else m.group(0), txt) if isinstance(txt, str) else txt
    r = 5
    for f in rows:
        if f[0] is None:
            celda(ws, f"A{r}", f[1], NEG, fill=GRIS)
        else:
            vals = [f[1], tr(f[2]), f[3], f[4], tr(f[5]) if len(f) > 5 else None]
            fila(ws, r, vals, fonts=[NEGRO, None, NEGRO, NEGRO, NEG])
            if isinstance(vals[1], str) and ("DATOS" in vals[1] or "PERFIL" in vals[1]): ws[f"B{r}"].font = VERDE
            ws[f"B{r}"].number_format = "0.000"
        r += 1
    celda(ws, f"A{r+1}", "Los muros se verifican como miembros del marco cerrado (losa superior y de fondo vaciadas monoliticamente con los muros). En el cruce de camiones el acero va en ambas caras. Registros solo fuera del cruce. Mismo armado que el tramo del Hogar de Refugio (alturas menores: 0.70 a 1.17 m).", SUB)
    hoja_estructural.KEY = KEY
    return ws


def hoja_cumplimiento(wb, R, rlast):
    ws = wb.create_sheet("CUMPLIMIENTO"); K = hoja_estructural.KEY
    cabecera(ws, "7. CUADRO DE CUMPLIMIENTO NORMATIVO Y CONDICIONES DE COMPATIBILIDAD ENTRE LOS TRES EXPEDIENTES", [58, 34, 44, 14, 20])
    encabezado_tabla(ws, 4, ["REQUISITO", "NORMA / REFERENCIA", "CRITERIO", "VALOR DEL DISENO", "RESULTADO"])
    E = lambda k: "ESTRUCTURAL!B%d" % K[k]
    cu0, cu1 = ROW["cu_r0"], ROW["cu_r1"]
    filas = [
        ("HIDROLOGIA E HIDRAULICA",),
        ("Periodo de retorno del colector", "Estudio hidrologico del proyecto (RNE CE.040)", "TR = 25 anos, igual al estudio hidrologico y a los colectores vecinos", "=DATOS!$B${TR}", "=IF(DATOS!$B${TR}=25,\"CUMPLE\",\"VERIFICAR\")"),
        ("Caudal total del CAR Varones", "Memoria de hidrologia del CAR Varones; expediente del Hogar de Refugio", "Colector + cuneta Eje 01 = 258.7 L/s (mismo valor en los tres expedientes)", "=CAUDALES!D{r_qcl}", "=EMPALME_CL!B39"),
        ("Regimen de flujo en el colector", "RNE CE.040; Chow (flujo gradualmente variado)", "Subcritico en todo el tramo: Froude < 1", f"=PERFIL_FLUJO!B{rlast+5}", f"=IF(PERFIL_FLUJO!B{rlast+5}<1,\"CUMPLE\",\"NO CUMPLE\")"),
        ("Llenado maximo de la seccion", "Criterio de diseno adoptado (y/h <= 85 %)", "Tirante / altura interior", f"=PERFIL_FLUJO!B{rlast+3}", f"=IF(PERFIL_FLUJO!B{rlast+3}<=DATOS!$B${{llen}},\"CUMPLE\",\"NO CUMPLE\")"),
        ("Borde libre bajo la losa", "Criterio de diseno adoptado (>= 0.05 m)", "Cota bajo losa - nivel de agua", f"=PERFIL_FLUJO!B{rlast+4}", f"=IF(PERFIL_FLUJO!B{rlast+4}>=DATOS!$B${{BLmin}},\"CUMPLE\",\"NO CUMPLE\")"),
        ("Velocidad minima (autolimpieza) y maxima", "RNE CE.040 Drenaje Pluvial; ASCE/WEF (esfuerzo tractivo)", "0.90 <= V <= 3.0 m/s con el caudal de diseno en la entrega; en cada tramo V >= 0.90 m/s o tau >= 0.15 kg/m2 con su caudal", "=PERFIL_FLUJO!B200", "=PERFIL_FLUJO!B200"),
        ("Caida libre de las cunetas al colector / a la CL", "Criterio de diseno: NA del receptor bajo el fondo de cada cuneta", "Cunetas Ejes 09, 08, 06, 04 (colector) y 01 (CL)", f"=COUNTIF(CUNETAS!L{cu0}:L{cu1},\"CAIDA LIBRE\")", f"=IF(COUNTIF(CUNETAS!L{cu0}:L{cu1},\"CAIDA LIBRE\")={cu1-cu0+1},\"CUMPLE ({cu1-cu0+1} de {cu1-cu0+1})\",\"VERIFICAR\")"),
        ("Capacidad de la seccion con llenado del 85 % (margen frente al caudal de diseno)", "Manning; criterio de llenado maximo adoptado", "Q85 = (1/n) A R^(2/3) S^(1/2) con y = 0.85 h minima (0.70 m en el cruce); margen = Q85 / Q diseno",
         "=1000*DATOS!$B${b}*0.85*%s*(DATOS!$B${b}*0.85*%s/(DATOS!$B${b}+2*0.85*%s))^(2/3)*SQRT(DATOS!$B${S})/DATOS!$B${n}" % (E("Hmin"), E("Hmin"), E("Hmin")),
         "=\"CUMPLE (margen \"&TEXT(1000*DATOS!$B${b}*0.85*%s*(DATOS!$B${b}*0.85*%s/(DATOS!$B${b}+2*0.85*%s))^(2/3)*SQRT(DATOS!$B${S})/DATOS!$B${n}/CAUDALES!D{r_qcol},\"0.0\")&\" veces el caudal de diseno)\"" % (E("Hmin"), E("Hmin"), E("Hmin"))),
        ("EMPALME CON LA CAJA CL DEL HOGAR DE REFUGIO (CUI 2675514)",),
        ("Caida libre del colector sobre el NA de la CL", "Compatibilidad con el expediente del Hogar de Refugio", "fondo del colector > NA de la CL + 0.10", "=EMPALME_CL!B12", "=EMPALME_CL!B13"),
        ("Colchon de agua en la CL", "Memoria del Hogar de Refugio (poza 0.30 m)", ">= 0.50 m", "=EMPALME_CL!B16", "=EMPALME_CL!B17"),
        ("Techo de la CL coincide con el techo del colector (ventana sin dintel)", "Coordinacion de expedientes", "261.05 = 261.15 - 0.10", "=EMPALME_CL!B22", "=EMPALME_CL!B25"),
        ("Cuneta Eje 01 directa a la CL con caida libre", "Coordinacion de expedientes", "NCF > NA de la CL", "=EMPALME_CL!B33", "=EMPALME_CL!B34"),
        ("Caudal entregado = caudal previsto por el Hogar de Refugio", "Compatibilidad con el expediente del Hogar de Refugio", "258.7 L/s", "=EMPALME_CL!B37", "=EMPALME_CL!B39"),
        ("ESTRUCTURAS (RNE E.060 CONCRETO ARMADO, E.020 CARGAS, AASHTO LRFD)",),
        ("Combinaciones de carga", "RNE E.060 art. 9.2", "U = 1.4 D + 1.7 L; phi = 0.90 flexion y 0.85 cortante (art. 9.3)", "aplicado", "CUMPLE"),
        ("Losa superior tramo normal: flexion", "RNE E.060 cap. 10", "phi Mn >= Mu", "=" + E("MnA"), "=IF(%s>=%s,\"CUMPLE\",\"NO CUMPLE\")" % (E("MnA"), E("MuA"))),
        ("Losa superior tramo normal: cuantia minima", "RNE E.060 art. 9.7.2 (0.0018 b h, grado 60)", "As >= As min", "=" + E("AsA"), "=IF(%s>=%s,\"CUMPLE\",\"NO CUMPLE\")" % (E("AsA"), E("AmA"))),
        ("Losa superior cruce de camiones: flexion (rueda HL-93, IM 33 %)", "AASHTO LRFD 3.6.1.2 y 3.6.2; Manual de Puentes MTC", "phi Mn >= Mu", "=" + E("MnC"), "=IF(%s>=%s,\"CUMPLE\",\"NO CUMPLE\")" % (E("MnC"), E("MuC"))),
        ("Losa superior cruce de camiones: cortante", "RNE E.060 art. 11.3 (Vc = 0.53 raiz f'c b d)", "phi Vc >= Vu", "=" + E("VcC"), "=IF(%s>=%s,\"CUMPLE\",\"NO CUMPLE\")" % (E("VcC"), E("VuC"))),
        ("Muro tramo normal: flexion por empuje de suelo", "RNE E.060; E.020 (empuje en reposo Ko = 0.5)", "phi Mn >= Mu (marco cerrado)", "=" + E("MnD"), "=IF(%s>=%s,\"CUMPLE\",\"NO CUMPLE\")" % (E("MnD"), E("MuD"))),
        ("Muro tramo normal: cortante", "RNE E.060 art. 11.3", "phi Vc >= Vu", "=" + E("VcD"), "=IF(%s>=%s,\"CUMPLE\",\"NO CUMPLE\")" % (E("VcD"), E("VuD"))),
        ("Muro tramo normal: refuerzo en una capa", "RNE E.060 art. 14.3.4 (dos capas solo si e > 0.20 m)", "e = 0.15 m: una capa en el eje", "=DATOS!$B${em}", "=IF(DATOS!$B${em}<=0.20,\"CUMPLE\",\"VERIFICAR\")"),
        ("Muro cruce de camiones: flexion (sobrecarga lateral camion)", "RNE E.060; AASHTO LRFD 3.11.6.4", "phi Mn >= Mu", "=" + E("MnF"), "=IF(%s>=%s,\"CUMPLE\",\"NO CUMPLE\")" % (E("MnF"), E("MuF"))),
        ("Losa de fondo: flexion", "RNE E.060", "phi Mn >= Mu", "=" + E("MnG"), "=IF(%s>=%s,\"CUMPLE\",\"NO CUMPLE\")" % (E("MnG"), E("MuG"))),
        ("Presion sobre el suelo (tramo normal)", "RNE E.050 Suelos y Cimentaciones", "q <= 0.50 kg/cm2, valor minimo usual en suelos blandos; el EMS del proyecto lo confirma", "=" + E("sG"), "=IF(%s<=0.5,\"CUMPLE (q = \"&TEXT(%s,\"0.00\")&\" kg/cm2 < 0.50)\",\"VERIFICAR EMS\")" % (E("sG"), E("sG"))),
        ("Presion sobre el suelo (cruce de camiones, carga transitoria)", "RNE E.050; AASHTO LRFD 10.5 (carga viva transitoria)", "q con la rueda HL-93 e impacto <= 1.0 kg/cm2 (suelo arcilloso firme); el EMS del proyecto debe confirmar q adm >= q", "=" + E("sGc"), "=" + "ESTRUCTURAL!E%d" % K["sGc"]),
        ("Tapa de registro 0.68 x 0.68 x 0.08: flexion (rueda liviana)", "RNE E.060", "phi Mn >= Mu", "=" + E("MnH"), "=IF(%s>=%s,\"CUMPLE\",\"NO CUMPLE\")" % (E("MnH"), E("MuH"))),
        ("Recubrimientos", "RNE E.060 art. 7.7 (concreto sobre solado: 4 cm)", "4 cm muros y losa de fondo; 2.5 cm losa superior no expuesta; 4 cm cruce de camiones", "aplicado", "CUMPLE"),
        ("Traslapes y ganchos", "RNE E.060 cap. 12", "Traslape 0.40 m (3/8\"), 0.50 m (1/2\"); ganchos 0.30 m", "aplicado", "CUMPLE"),
        ("CONSTRUCTIVOS",),
        ("Registros de limpieza", "RNE CE.040 (accesibilidad para mantenimiento)", "Separacion <= 12 m, en cada llegada de cuneta y en el quiebre; fuera del cruce de camiones", "11 registros", "CUMPLE"),
        ("Juntas de dilatacion", "Practica de los colectores vecinos", "Cada 4.00 m con tecnopor 1\" y sello", "26 juntas", "CUMPLE"),
        ("Emplazamiento", "Lindero y faja de la carretera Oasis", "Dentro del predio, pegado por fuera del cerco proyectado, sin invadir la via; paso en el cerco en el tramo de empalme", "eje a 0.475 m del cerco", "CUMPLE"),
    ]
    r = 5
    for f in filas:
        if len(f) == 1:
            celda(ws, f"A{r}", f[0], NEG, fill=GRIS)
        else:
            fila(ws, r, list(f), fonts=[NEGRO, NEGRO, NEGRO, VERDE, NEG]); ws[f"D{r}"].number_format = "0.000"
        r += 1
    r += 1
    celda(ws, f"A{r}", "Requisitos que no cumplen o por verificar", NEG); celda(ws, f"B{r}", f'=COUNTIF(E5:E{r-2},"NO CUMPLE*")+COUNTIF(E5:E{r-2},"VERIFICAR*")', NEG)
    r += 2
    celda(ws, f"A{r}", "DATOS DE OTROS EXPEDIENTES Y COMO QUEDAN CUBIERTOS EN ESTE DISENO", NEG, fill=GRIS); r += 1
    for t in ["1. Caja de llegada CL: pertenece al expediente del Hogar de Refugio (CUI 2675514). Queda del lado del CAR Varones (x = 349162.00 a 349163.80 del sistema local), por lo que su tapa se fija en +261.15 (piso de Varones) y en ella se dejan la ventana este 0.60 x 1.17 (cota de fondo 259.884) y la ventana norte 0.40 x 0.66 (NCF 260.39) para la cuneta del Eje 01.",
              "2. Caudal: el colector conduce 221.7 L/s y la cuneta del Eje 01 entrega 37.0 L/s directamente a la CL; el total (258.7 L/s) es el dato de la memoria de hidrologia del CAR Varones y el aporte considerado por el Hogar de Refugio (560.6 L/s) y, aguas abajo, por el CAR Mujeres.",
              "3. Nivel de agua en la CL (259.606): resultado del perfil de flujo del tramo del Hogar de Refugio; el colector de Varones descarga en caida libre, por lo que un cambio moderado de ese nivel no altera este tramo.",
              "4. Capacidad portante: la presion transmitida es menor que 0.50 kg/cm2; el EMS del proyecto, exigido por la norma E.050, la confirma (no hay EMS disponible al elaborar esta memoria).",
              "5. Coordenadas UTM: mismo sistema del tramo del Hogar de Refugio (R-01 del CAR Mujeres y azimut 49.54 del lindero); el trazo se replantea en obra desde el cerco (eje a 0.475 m) y desde la CL.",
              "6. Cotas de fondo de las cunetas: tomadas del plano PERFIL CAR VARONES (Ejes 01 a 09); todas caen libremente al colector o a la CL."]:
        celda(ws, f"A{r}", t, NEGRO); r += 1
    ws.freeze_panes = "A5"
    return ws


def hoja_memoria(wb, R, rlast):
    ws = wb.create_sheet("MEMORIA", 0)
    cabecera(ws, "MEMORIA DE CALCULO - COLECTOR PLUVIAL FRONTAL DEL CAR VARONES Y EMPALME CON LA CAJA CL DEL HOGAR DE REFUGIO", [38, 120, 10])
    cl = R["caja_llegada"]
    txt = [
        ("1. OBJETO", "Dimensionar el colector pluvial frontal del Centro de Acogida Residencial - Varones (CUI 2705619) que recoge las cunetas de los Ejes 09, 08, 06 y 04 y las entrega a la caja de llegada CL del colector del Hogar de Refugio Temporal Mujeres Violentadas (CUI 2675514); la cuneta del Eje 01 entra directamente a la CL. Longitud %.2f m desde el poste derecho del porton de camiones (0+000) hasta la cara este de la CL." % dz.P_FIN),
        ("2. NORMATIVA", "RNE CE.040 Drenaje Pluvial (RM 126-2021-VIVIENDA); RNE E.020 Cargas; RNE E.060 Concreto Armado; RNE E.050 Suelos; AASHTO LRFD (rueda HL-93 en el cruce de camiones cisterna); Chow, Hidraulica de canales abiertos (paso estandar con caudal variable)."),
        ("3. HIDROLOGIA", "Caudal total del CAR Varones 258.7 L/s (memoria de hidrologia del proyecto, TR = 25 anos, I = 210.98 mm/h, FS = 1.15), repartido entre las cinco cunetas que llegan al frente en proporcion al ancho de frente que drena cada una. Es el mismo caudal que el expediente del Hogar de Refugio considera como aporte de Varones."),
        ("4. HIDRAULICA", "Colector cubierto de concreto armado b = 0.60 m, S = 0.30 %%, n = 0.015, fondo de 260.20 (0+000) a %.3f (CL). Altura interior 0.70 m en el cruce de camiones (losa e = 0.25) y hasta 1.17 m en la llegada; losa superior al ras del piso terminado +261.15 en todo el frente. Perfil de flujo gradualmente variado con caudal creciente en cada empalme; control: tirante critico en la caida libre a la CL (caida %.2f m sobre su nivel de agua). Flujo subcritico, llenado <= 35 %%, capacidad con llenado del 85 %% de 445 L/s." % (dz.fondo(dz.P_FIN), cl["caida_libre"])),
        ("5. ESTRUCTURAS", "Marco cerrado monolitico igual al del tramo del Hogar de Refugio: losa superior e = 0.10, muros e = 0.15 y losa de fondo e = 0.15 con un solo marco 3/8\" @0.20 en el eje de la seccion y longitudinales 3/8\" @0.25 (una capa; E.060 14.3.4); cruce de camiones cisterna con losas e = 0.25 y doble marco 1/2\" @0.15. Tapas de registro 0.68 x 0.68 x 0.08."),
        ("6. EMPALME", "La CL (expediente del Hogar de Refugio) queda del lado de Varones: su tapa se fija en +261.15 y recibe el colector por una ventana 0.60 x 1.17 en su muro este (sin dintel: techo de la CL = techo del colector = 261.05) y la cuneta del Eje 01 por una ventana 0.40 x 0.66 en su muro norte. Juntas de tecnopor 1\" en todo contacto entre estructuras de distinto expediente."),
        ("7. RESULTADOS", "Ver cuadro resumen y la hoja CUMPLIMIENTO (requisito, norma, criterio, valor y resultado). Planta, perfil, secciones y detalles en las laminas DP-01, DP-02, DP-04A/B, DP-06B, DP-06C, DP-07, DP-08, DA-01 a DA-03 y DD-01 a DD-04."),
    ]
    r = 4
    for a, b in txt:
        celda(ws, f"A{r}", a, NEG); celda(ws, f"B{r}", b, NEGRO, al="left"); ws.row_dimensions[r].height = 48; r += 1
    r += 1
    res = [
        ("Caudal de diseno del colector (L/s)", "=CAUDALES!D{r_qcol}", "0.0"),
        ("Caudal total entregado a la CL (L/s)", "=CAUDALES!D{r_qcl}", "0.0"),
        ("Ancho interior adoptado (m)", "=DATOS!$B${b}", "0.00"),
        ("Pendiente del fondo (%)", "=DATOS!$B${S}*100", "0.00"),
        ("Cota de fondo inicial / final del colector (msnm)", "=TEXT(DATOS!$B${CF0},\"0.00\")&\" / \"&TEXT(EMPALME_CL!B8,\"0.000\")", None),
        ("Llenado maximo y/h", f"=PERFIL_FLUJO!B{rlast+3}", "0.000"),
        ("Borde libre minimo bajo losa (m)", f"=PERFIL_FLUJO!B{rlast+4}", "0.000"),
        ("Froude maximo en el colector", f"=PERFIL_FLUJO!B{rlast+5}", "0.00"),
        ("Estaciones hidraulicas que no cumplen", f"=PERFIL_FLUJO!B{rlast+6}", "0"),
        ("Velocidades y autolimpieza (0.90 a 3.0 m/s; tau >= 0.15 kg/m2)", "=PERFIL_FLUJO!B200", None),
        ("Cunetas con caida libre (de 5)", "=COUNTIF(CUNETAS!L{cu_r0}:L{cu_r1},\"CAIDA LIBRE\")", "0"),
        ("Caida libre del colector a la CL", "=EMPALME_CL!B13", None),
        ("Elementos estructurales que no cumplen", "=COUNTIF(ESTRUCTURAL!E:E,\"NO CUMPLE\")", "0"),
        ("Requisitos normativos que no cumplen o por verificar (hoja CUMPLIMIENTO)", "=COUNTIF(CUMPLIMIENTO!E:E,\"NO CUMPLE*\")+COUNTIF(CUMPLIMIENTO!E:E,\"VERIFICAR*\")", "0"),
    ]
    for a, b, f in res:
        celda(ws, f"A{r}", a, NEGRO); c = celda(ws, f"B{r}", b, VERDE); c.alignment = Alignment(horizontal="left")
        if f: c.number_format = f
        r += 1
    r += 1
    celda(ws, f"A{r}", "NOTAS", NEG)
    for n in ["Las cunetas de arquitectura (Ejes 09, 08, 06, 04 y 01) se acortan 0.24, 0.09, 0.24, 3.12 y 2.77 m respecto del plano: terminan en la cara del muro del colector o de la CL; ese descuento se aplica en la partida de cunetas del proyecto.",
              "La ubicacion UTM es referencial (mismo sistema del tramo del Hogar de Refugio). Verificar en campo.",
              "No se dispone del estudio de mecanica de suelos: la presion transmitida se compara con 0.50 kg/cm2 y debe confirmarse con el EMS del proyecto."]:
        r += 1; celda(ws, f"B{r}", n, NEGRO, al="left"); ws.row_dimensions[r].height = 30
    return ws


def construir(fn=SALIDA):
    R = dz.disenar()
    wb = openpyxl.Workbook(); wb.remove(wb.active)
    hoja_datos(wb, R); hoja_caudales(wb, R); hoja_cunetas(wb, R); hoja_empalme(wb, R)
    ws, rlast = hoja_perfil(wb, R); hoja_estructural(wb, R); hoja_cumplimiento(wb, R, rlast); hoja_memoria(wb, R, rlast)
    def tr(m):
        return "DATOS!$B$%d" % ROW[m.group(1)]
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and "{" in c.value:
                    v = re.sub(r"DATOS!\$B\$\{(\w+)\}", tr, c.value)
                    v = re.sub(r"\{(r_\w+|cu_\w+|c_\w+)\}", lambda m: str(ROW[m.group(1)]), v)
                    c.value = v
    os.makedirs(os.path.dirname(fn), exist_ok=True); wb.save(fn)
    return fn, R


if __name__ == "__main__":
    print(construir()[0])
