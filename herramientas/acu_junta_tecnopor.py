"""ACU de la partida 01.04.04.06.02 JUNTA E=1" CON TECNOPOR ENTRE COLECTOR Y PISO ADYACENTE (Hogar de Refugio Temporal -
Mujeres Violentadas, CUI 2675514). Excel aparte con formulas. Ratios de la hoja COLECTOR INSUMOS de la planilla vigente
(tecnopor 1" 0.15 m2/m, peon 0.10 hh/m) y desglose del metrado de la hoja COLECTOR JUNTAS Y EMPALMES.
"""
import os, warnings
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(RAIZ, "insumos", "metrados_vigentes", "METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx")
SAL = os.path.join(RAIZ, "entregables", "ACU_JUNTA_TECNOPOR_COLECTOR_CERCO_HOGAR_REFUGIO.xlsx")
AZUL, CELESTE, AMARILLO, VERDE = "1F4E79", "DDEBF7", "FFF2CC", "E2EFDA"


def datos():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(PLAN, data_only=True)
    res = {r[0]: r for r in wb["RESUMEN"].iter_rows(values_only=True) if r and r[0]}
    part = res["01.04.04.06.02"]
    ci = wb["COLECTOR INSUMOS"]
    f0 = next(r for r in range(1, ci.max_row + 1) if str(ci["B%d" % r].value).startswith("01.04.04.06.02"))
    rt, rp = ci["G%d" % f0].value, ci["G%d" % (f0 + 1)].value
    tramos, dentro = [], False
    for r in wb["COLECTOR JUNTAS Y EMPALMES"].iter_rows(values_only=True):
        v = [x for x in r if x not in (None, "")]
        if not v: continue
        if isinstance(v[0], str) and v[0].upper().startswith("JUNTA") and "TECNOPOR" in v[0].upper() and "DILATACION" not in v[0].upper(): dentro = True; continue
        if dentro and isinstance(v[0], str) and v[0].upper().startswith("TOTAL"): break
        if dentro and isinstance(v[0], int): tramos.append(v[1:7])
    p_peon = wb["ACU TAPA REGISTRO"]["F71"].value
    a = wb["ACU TAPA REGISTRO"]
    assert "SELLADOR" in str(ci["E%d" % (f0 + 2)].value).upper() and str(ci["E%d" % (f0 + 3)].value) == "Operario"
    precio = {a["B%d" % r].value: a["F%d" % r].value for r in range(68, 94) if a["B%d" % r].value}
    return dict(cod=part[0], desc=part[1], und=part[2], met=part[3], rt=rt, rp=rp, tramos=tramos, p_peon=p_peon,
                rs=ci["G%d" % (f0 + 2)].value, ro=ci["G%d" % (f0 + 3)].value, p_oper=precio["Operario"], p_arena=precio["Arena gruesa"])


def construir():
    D = datos()
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "ACU JUNTA TECNOPOR"
    fino = Side(style="thin", color="808080"); borde = Border(left=fino, right=fino, top=fino, bottom=fino)
    for col, w in zip("ABCDEFGH", (6, 50, 9, 12, 13, 12, 13, 64)): ws.column_dimensions[col].width = w

    def c(ref, v, fill=None, b=False, h="center", fmt=None, color="000000"):
        x = ws[ref]; x.value = v; x.font = Font(name="Arial", size=10, bold=b, color=color)
        x.alignment = Alignment(horizontal=h, vertical="center", wrap_text=True); x.border = borde
        if fill: x.fill = PatternFill("solid", fgColor=fill)
        if fmt: x.number_format = fmt

    def fila(r, texto, fill=CELESTE, b=True, color="000000", alto=None):
        ws.merge_cells("A%d:H%d" % (r, r)); c("A%d" % r, texto, fill, b, "left", color=color)
        for col in "BCDEFGH": ws["%s%d" % (col, r)].border = borde
        if alto: ws.row_dimensions[r].height = alto

    def cab(r, textos):
        for col, t in zip("ABCDEFGH", textos): c("%s%d" % (col, r), t, AZUL, True, color="FFFFFF")

    fila(1, "ANALISIS DE COSTO UNITARIO - %s %s" % (D["cod"], D["desc"]), AZUL, color="FFFFFF", alto=30)
    fila(2, "PROYECTO: HOGAR DE REFUGIO TEMPORAL - MUJERES VIOLENTADAS, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N.° 2675514", None, False)
    fila(3, "Junta de 1\" (25 mm) de plancha de poliestireno expandido (tecnopor) con sello asfaltico superficial de 1\" x 2\" (RC-250 + arena) entre el colector y el cerco perimetrico (no hay vereda exterior): contacto con el "
            "cimiento del cerco, bordes de la losa superior y bordes de las cajas CL y CC segun el desglose del metrado, de modo que cada estructura trabaje en forma independiente. "
            "Celda amarilla = dato; verde = formula. Precios sin IGV, referenciales.", None, False, alto=44)

    # ---- 1. sustento del metrado
    fila(5, "1. METRADO DE LA PARTIDA (hoja COLECTOR JUNTAS Y EMPALMES de la planilla)")
    cab(6, ("N°", "ELEMENTO", "VECES", "LONGITUD (m)", "PARCIAL (m)", None, None, "PROGRESIVA / SUSTENTO"))
    r = 7
    for i, (el, prog, veces, lon, par, sus) in enumerate(D["tramos"]):
        c("A%d" % r, i + 1); c("B%d" % r, el, h="left"); c("C%d" % r, veces, fmt="0"); c("D%d" % r, lon, AMARILLO, fmt="0.000")
        c("E%d" % r, "=C%d*D%d" % (r, r), VERDE, fmt="0.000"); c("F%d" % r, None); c("G%d" % r, None); c("H%d" % r, "%s - %s" % (prog, sus), h="left")
        r += 1
    r_tot = r
    c("A%d" % r, None, CELESTE); c("B%d" % r, "TOTAL JUNTA DE TECNOPOR (m)", CELESTE, True, "left")
    for col in "CDFGH": c("%s%d" % (col, r), None, CELESTE)
    c("E%d" % r, "=SUM(E7:E%d)" % (r - 1), CELESTE, True, fmt="0.000")
    c("H%d" % r, "Valor del RESUMEN: %.3f m" % D["met"], CELESTE, h="left")

    # ---- 2. datos del analisis
    r += 2; fila(r, "2. DATOS DEL ANALISIS"); r += 1
    cab(r, ("N°", "DATO", "UND", "VALOR", None, None, None, "SUSTENTO")); r += 1
    r0 = r
    dts = [("Espesor de la junta", "pulg", 1, "Partida: junta e = 1\" (25 mm)"),
           ("Tecnopor por metro de junta", "m2/m", D["rt"], "COLECTOR INSUMOS fila 72: altura promedio de contacto 0.15 m (losa superior 0.10 m en tramo normal y 0.25 m en cruces, y contacto con el cimiento del cerco)"),
           ("Area de una plancha de tecnopor 1\" (1.20 x 2.40 m)", "m2", 2.88, "Medida comercial de plancha"),
           ("Planchas por metro de junta", "pln/m", "=D%d/D%d" % (r0 + 1, r0 + 2), "formula"),
           ("Rendimiento: m de junta por dia (cuadrilla 1 peon)", "m/dia", "=8/COLECTOR_PEON", "COLECTOR INSUMOS fila 73: peon 0.10 hh/m -> 8 / 0.10 = 80 m/dia; corte de planchas en tiras y fijacion al encofrado o al concreto existente antes del vaciado"),
           ("Mezcla de sello asfaltico por metro de junta (1\" x 2\")", "m3/m", D["rs"], "COLECTOR INSUMOS fila 74: 0.0254 x 0.0508 = 0.0013 m3/m; sello superficial en la cara expuesta (EG-2013 510.02 c; procedimiento: RC-250 + arena en juntas de 1\" x 2\")"),
           ("Asfalto liquido RC-250 por m3 de mezcla", "gal/m3", 50, "Criterio: mezcla de ~2,000 kg/m3 con ~9 % de asfalto en peso = 180 kg / 3.6 kg/gal = 50 gal/m3"),
           ("Arena gruesa por m3 de mezcla", "m3/m3", 1.05, "Criterio: arena suelta con 5 % de desperdicio"),
           ("Operario de sellado por metro de junta", "hh/m", D["ro"], "COLECTOR INSUMOS fila 75: 0.05 hh/m (sellado de ~160 m por dia: limpieza, calentado y mezcla, colocacion compactando con tacos)")]
    for i, (t, u, v, s) in enumerate(dts):
        rr = r + i
        if isinstance(v, str) and "COLECTOR_PEON" in v: v = "=8/%s" % D["rp"]
        c("A%d" % rr, i + 1); c("B%d" % rr, t, h="left"); c("C%d" % rr, u)
        c("D%d" % rr, v, VERDE if isinstance(v, str) else AMARILLO, fmt="0.0000" if u not in ("pulg", "m/dia", "gal/m3", "m3/m3") else "0.00"); c("H%d" % rr, s, h="left")
        for col in "EFG": c("%s%d" % (col, rr), None)
    R_TEC, R_PLN, R_REND, R_SEL, R_RC, R_AR, R_OP = r0 + 1, r0 + 3, r0 + 4, r0 + 5, r0 + 6, r0 + 7, r0 + 8
    r += len(dts) + 1

    # ---- 3. analisis de costo unitario
    fila(r, "3. ANALISIS DE COSTO UNITARIO"); r += 1
    for k, (et, v, nota) in enumerate((("Partida", "%s %s" % (D["cod"], D["desc"]), ""), ("Unidad", D["und"], ""),
                                        ("Metrado", "=E%d" % r_tot, "suma del desglose (seccion 1)"),
                                        ("Rendimiento (m/dia)", "=D%d" % R_REND, "seccion 2"))):
        rr = r + k
        c("A%d" % rr, et, CELESTE, True, "left"); c("B%d" % rr, v, None, k == 0, "left", fmt="0.00" if k >= 2 else None)
        for col in "CDEFG": c("%s%d" % (col, rr), None)
        c("H%d" % rr, nota, h="left")
    R_MET, R_REN = r + 2, r + 3
    r += 5
    cab(r, ("N°", "RECURSO", "UND", "CUADRILLA", "CANTIDAD", "PRECIO S/", "PARCIAL S/", "SUSTENTO / FUENTE")); r += 1
    fila(r, "MANO DE OBRA"); r += 1
    c("A%d" % r, 1); c("B%d" % r, "Peon", h="left"); c("C%d" % r, "hh"); c("D%d" % r, 1, AMARILLO, fmt="0.00")
    c("E%d" % r, "=D%d*8/$B$%d" % (r, R_REN), VERDE, fmt="0.0000"); c("F%d" % r, D["p_peon"], AMARILLO, fmt="0.00")
    c("G%d" % r, "=E%d*F%d" % (r, r), VERDE, fmt="0.00")
    c("H%d" % r, "Mismo costo hh de peon de la ACU TAPA REGISTRO de la planilla (CAPECO 2026 oficial: S/ 20.54 hh)", h="left")
    R_MO = r; r += 1
    c("A%d" % r, 2); c("B%d" % r, "Operario (sellado asfaltico)", h="left"); c("C%d" % r, "hh"); c("D%d" % r, "=D%d*$B$%d/8" % (R_OP, R_REN), VERDE, fmt="0.00")
    c("E%d" % r, "=D%d*8/$B$%d" % (r, R_REN), VERDE, fmt="0.0000"); c("F%d" % r, D["p_oper"], AMARILLO, fmt="0.00")
    c("G%d" % r, "=E%d*F%d" % (r, r), VERDE, fmt="0.00")
    c("H%d" % r, "Cuadrilla = 0.05 hh/m x rendimiento / 8; costo hh de operario de la ACU TAPA REGISTRO (CAPECO 2026 oficial: S/ 28.95 hh)", h="left")
    R_MO2 = r; r += 1
    c("A%d" % r, None, CELESTE); c("B%d" % r, "Subtotal mano de obra", CELESTE, True, "left")
    for col in "CDEFH": c("%s%d" % (col, r), None, CELESTE)
    c("G%d" % r, "=G%d+G%d" % (R_MO, R_MO2), CELESTE, True, fmt="0.00"); R_SMO = r; r += 1
    fila(r, "MATERIALES"); r += 1
    c("A%d" % r, 3); c("B%d" % r, "Plancha de tecnopor (poliestireno expandido) 1\" x 1.20 x 2.40 m", h="left"); c("C%d" % r, "pln")
    c("D%d" % r, None); c("E%d" % r, "=D%d" % R_PLN, VERDE, fmt="0.0000"); c("F%d" % r, 12.63, AMARILLO, fmt="0.00")
    c("G%d" % r, "=E%d*F%d" % (r, r), VERDE, fmt="0.00")
    c("H%d" % r, "Estimado: plancha DIPROPOR 2\" x 1.20 x 2.40 a S/ 28.90 con IGV en Sodimac Peru; la de 1\" ~ la mitad = S/ 14.90 con IGV -> 14.90 / 1.18 = 12.63 sin IGV. Confirmar con cotizacion", h="left")
    R_MAT = r; r += 1
    c("A%d" % r, 4); c("B%d" % r, "Asfalto liquido RC-250", h="left"); c("C%d" % r, "gal"); c("D%d" % r, None)
    c("E%d" % r, "=D%d*D%d" % (R_SEL, R_RC), VERDE, fmt="0.0000"); c("F%d" % r, 20.00, AMARILLO, fmt="0.00"); c("G%d" % r, "=E%d*F%d" % (r, r), VERDE, fmt="0.00")
    c("H%d" % r, "ESTIMADO, POR COTIZAR: no hay precio publicado; pedir cotizacion a PETROPERU o distribuidor (balde 5 gal o cilindro 55 gal)", h="left")
    R_RCM = r; r += 1
    c("A%d" % r, 5); c("B%d" % r, "Arena gruesa", h="left"); c("C%d" % r, "m3"); c("D%d" % r, None)
    c("E%d" % r, "=D%d*D%d" % (R_SEL, R_AR), VERDE, fmt="0.0000"); c("F%d" % r, D["p_arena"], AMARILLO, fmt="0.00"); c("G%d" % r, "=E%d*F%d" % (r, r), VERDE, fmt="0.00")
    c("H%d" % r, "Mismo precio de arena gruesa de la ACU TAPA REGISTRO de la planilla", h="left")
    R_ARM = r; r += 1
    c("A%d" % r, None, CELESTE); c("B%d" % r, "Subtotal materiales", CELESTE, True, "left")
    for col in "CDEFH": c("%s%d" % (col, r), None, CELESTE)
    c("G%d" % r, "=G%d+G%d+G%d" % (R_MAT, R_RCM, R_ARM), CELESTE, True, fmt="0.00"); R_SMA = r; r += 1
    fila(r, "EQUIPOS Y HERRAMIENTAS"); r += 1
    c("A%d" % r, 6); c("B%d" % r, "Herramientas manuales (cuchilla, regla, wincha, tacos de madera y recipiente para calentar el asfalto)", h="left"); c("C%d" % r, "%mo"); c("D%d" % r, None)
    c("E%d" % r, 0.03, AMARILLO, fmt="0.00%"); c("F%d" % r, "=G%d" % R_SMO, VERDE, fmt="0.00"); c("G%d" % r, "=E%d*F%d" % (r, r), VERDE, fmt="0.00")
    c("H%d" % r, "3 % del costo de mano de obra (criterio de las demas ACU de la planilla)", h="left")
    R_EQ = r; r += 1
    c("A%d" % r, None, CELESTE); c("B%d" % r, "Subtotal equipos y herramientas", CELESTE, True, "left")
    for col in "CDEFH": c("%s%d" % (col, r), None, CELESTE)
    c("G%d" % r, "=G%d" % R_EQ, CELESTE, True, fmt="0.00"); R_SEQ = r; r += 1
    ws.merge_cells("A%d:F%d" % (r, r)); c("A%d" % r, "COSTO UNITARIO DIRECTO (S/ por m)", AZUL, True, "left", color="FFFFFF")
    for col in "BCDEF": ws["%s%d" % (col, r)].border = borde
    c("G%d" % r, "=G%d+G%d+G%d" % (R_SMO, R_SMA, R_SEQ), AZUL, True, fmt="0.00", color="FFFFFF"); c("H%d" % r, None, AZUL)
    R_CU = r; r += 1
    ws.merge_cells("A%d:F%d" % (r, r)); c("A%d" % r, "COSTO DIRECTO DE LA PARTIDA (metrado x costo unitario)", CELESTE, True, "left")
    for col in "BCDEF": ws["%s%d" % (col, r)].border = borde
    c("G%d" % r, "=G%d*B%d" % (R_CU, R_MET), CELESTE, True, fmt="#,##0.00"); c("H%d" % r, "S/ sin IGV", CELESTE, h="left")
    r += 2
    fila(r, "INSUMOS TOTALES DE LA PARTIDA"); r += 1
    cab(r, ("N°", "INSUMO", "UND", "POR m", "METRADO (m)", "TOTAL", "A COMPRAR", "OBSERVACION")); r += 1
    for i, (t, u, rref, compra, obs) in enumerate((("Plancha de tecnopor 1\" x 1.20 x 2.40 m", "pln", "E%d" % R_MAT, "=ROUNDUP(F{r},0)", "planchas enteras; se cortan en tiras de la altura de cada contacto"),
                                                   ("Tecnopor (area)", "m2", "D%d" % R_TEC, None, "area neta de junta"),
                                                   ("Asfalto liquido RC-250", "gal", "E%d" % R_RCM, "=ROUNDUP(F{r},0)", "galones enteros"),
                                                   ("Arena gruesa", "m3", "E%d" % R_ARM, None, "arena limpia, seca"),
                                                   ("Peon", "hh", "E%d" % R_MO, None, "%.1f dias de 1 peon" % (D["met"] * D["rp"] / 8)),
                                                   ("Operario", "hh", "E%d" % R_MO2, None, "%.1f dias de 1 operario" % (D["met"] * D["ro"] / 8)))):
        c("A%d" % r, i + 1); c("B%d" % r, t, h="left"); c("C%d" % r, u); c("D%d" % r, "=" + rref, VERDE, fmt="0.0000")
        c("E%d" % r, "=B%d" % R_MET, VERDE, fmt="0.000"); c("F%d" % r, "=D%d*E%d" % (r, r), VERDE, fmt="0.00")
        c("G%d" % r, compra.format(r=r) if compra else None, VERDE if compra else None, fmt="0"); c("H%d" % r, obs, h="left")
        r += 1
    r += 1
    fila(r, "PROCEDIMIENTO", CELESTE); r += 1
    for t in ("1. Cortar las planchas de 1\" en tiras de la altura de cada contacto (borde de losa superior, cimiento del cerco, bordes de cajas).",
              "2. Fijar las tiras contra la cara del concreto existente o del encofrado antes del vaciado, continuas y sin huecos, 2\" por debajo de la superficie terminada (caja del sello).",
              "3. Vaciar el concreto sin desplazar el tecnopor.",
              "4. Sello: limpiar y secar la caja de 1\" x 2\"; calentar el RC-250, mezclarlo con la arena y colocarlo compactando con tacos de madera hasta el ras; retirar lo que salpique al concreto.",
              "5. Medicion: metro lineal de junta terminada (tecnopor + sello), segun el desglose de la seccion 1."):
        fila(r, t, None, False); r += 1
    ws.freeze_panes = "A5"
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(SAL)
    return SAL


if __name__ == "__main__":
    print(construir())
