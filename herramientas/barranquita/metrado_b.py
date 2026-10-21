"""Metrado de drenaje pluvial (red de cunetas) de la I.E. N.° 0590 Barranquita (C.I. 468901), con formulas.

Partidas con nombres y estructura Delphin del metrado de drenaje pluvial del CAR Mujeres (CUI 2717013); cantidades propias
de este proyecto (cantidades_b.py: perfiles de cada eje, tramos tapados, tapas de inspeccion y descargas).
Hojas: RESUMEN, PLANILLA GENERAL DE METRADOS (por eje, con formulas), METRADO ACERO y PARAMETROS.
"""
import os, sys, json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import cantidades_b as Q

SAL = os.path.join(RAIZ, "entregables_barranquita", "METRADO_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.xlsx")
ENTIDAD = "GOBIERNO REGIONAL SAN MARTIN - GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO"
PROYECTO = ("“MEJORAMIENTO Y AMPLIACIÓN DEL SERVICIO DE EDUCACIÓN PRIMARIA EN I.E. N° 0590 DISTRITO DE BARRANQUITA DE LA "
            "PROVINCIA DE LAMAS DEL DEPARTAMENTO DE SAN MARTÍN” - C.I. N° 468901")
UBIC = "SAN MARTIN - LAMAS - BARRANQUITA"
FECHA = "OCTUBRE 2026"
_b = Side(style="thin", color="808080"); BOR = Border(left=_b, right=_b, top=_b, bottom=_b)
F = lambda **k: Font(name="Arial", size=k.pop("size", 9), **k)
AZ, GR, AM = "DDEBF7", "F2F2F2", "FFF2CC"

# ---------------------------------------------------------------------------- parametros (celda B de la hoja PARAMETROS)
PAR = [("Ancho exterior de la cuneta (m)", Q.BT, "be"), ("Luz libre interior (m)", Q.B, "b"), ("Espesor de muros (m)", Q.E, "em"),
       ("Espesor de losa de fondo (m)", Q.EF, "ef"), ("Espesor de losa tapa en tramos tapados (m)", Q.ET, "et"),
       ("Espesor de solado f'c = 100 kg/cm2 (m)", Q.SOLADO, "sol"), ("Sobreancho de excavacion a cada lado (m)", Q.SOBREANCHO, "sa"),
       ("Ancho de excavacion (m)", "=B5+2*B11", "bexc"), ("Profundidad adicional bajo la cota de fondo: losa + solado (m)", "=B8+B10", "hadd"),
       ("Factor de esponjamiento para eliminacion", Q.ESPONJ, "esp"), ("Junta de dilatacion en la seccion en U cada (m)", Q.JUNTA_CADA, "jc"),
       ("Recubrimiento del acero (m)", Q.REC, "rec"), ("Peso de la barra de 3/8\" (kg/m)", Q.KG38, "kg"),
       ("Separacion de las U de 3/8\" (m)", Q.SEP_T, "st"), ("Separacion de barras longitudinales de 3/8\" (m)", Q.SEP_L, "sl"),
       ("Profundidad minima con acero (m): h >= 0.40 o tramo tapado", Q.H_ACERO, "hac"), ("Tapa de inspeccion: lado (m)", Q.TAPA[0], "tl"),
       ("Tapa de inspeccion: espesor (m)", Q.TAPA[2], "te")]
P = {k: "PARAMETROS!$B$%d" % (5 + i) for i, (_, _, k) in enumerate(PAR)}


def cab_doc(ws, titulo, ncol):
    ws.cell(2, 1, titulo).font = F(size=12, bold=True)
    for i, (k, v) in enumerate((("ENTIDAD", ENTIDAD), ("PROYECTO", PROYECTO), ("UBICACIÓN", UBIC), ("FECHA", FECHA))):
        ws.cell(3 + i, 1, k).font = F(bold=True); c = ws.cell(3 + i, 2, v); c.font = F(); c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=3 + i, start_column=2, end_row=3 + i, end_column=ncol)
    ws.row_dimensions[4].height = 36


def construir():
    q = Q.por_eje(); dsc = Q.descargas()
    wb = Workbook()
    wr = wb.active; wr.title = "RESUMEN"
    wp = wb.create_sheet("PLANILLA GENERAL DE METRADOS"); wa = wb.create_sheet("METRADO ACERO"); wq = wb.create_sheet("PARAMETROS")
    # ---- PARAMETROS
    cab_doc(wq, "PARAMETROS DEL METRADO - RED DE CUNETAS", 3)
    for i, (t, v, k) in enumerate(PAR):
        wq.cell(5 + i, 1, t).font = F(); c = wq.cell(5 + i, 2, v); c.font = F(bold=True); c.fill = PatternFill("solid", fgColor=AM); c.border = BOR
        c.number_format = "0.00"
    wq.cell(5 + len(PAR) + 1, 1, "Fuente: planos DC-01 a DC-19 (secciones tipicas DC-02, perfiles DC-03 a DC-11, secciones DC-12 a DC-14, descargas DC-16 a DC-19).").font = F(italic=True)
    wq.column_dimensions["A"].width = 62; wq.column_dimensions["B"].width = 12
    # ---- METRADO ACERO (por eje)
    cab_doc(wa, "ACERO f'y = 4200 kg/cm2 PARA CUNETAS - BARRAS DE 3/8\"", 12)
    hdr = ["EJE", "LONG. CON ACERO (m)", "h PROM. CON ACERO (m)", "LONG. TAPADA (m)", "LONG. U (m)", "N° DE U", "N° BARRAS LONG.",
           "kg U", "kg LONGIT.", "kg LOSA TAPA", "TOTAL (kg)"]
    for j, t in enumerate(hdr, 1):
        c = wa.cell(8, j, t); c.font = F(bold=True); c.fill = PatternFill("solid", fgColor=AZ); c.border = BOR; c.alignment = Alignment(wrap_text=True, horizontal="center")
    fila_acero = {}
    for i, x in enumerate(q):
        r = 9 + i; fila_acero[x["eje"]] = r
        vals = [x["eje"], x["L_acero"], x["h_acero"], x["L_tapado"],
                "=IF(B{r}>0,2*(C{r}+{ef}-2*{rec})+({be}-2*{rec})+0.2,0)".format(r=r, **P),
                "=IF(B{r}>0,B{r}/{st},0)".format(r=r, **P),
                "=IF(B{r}>0,2*(CEILING(ROUND(C{r}/{sl},6),1)+1)+(CEILING(ROUND(({be}-2*{rec})/{sl},6),1)+1),0)".format(r=r, **P),
                "=F{r}*E{r}*{kg}".format(r=r, **P), "=G{r}*B{r}*{kg}".format(r=r, **P),
                "=IF(B{r}>0,(D{r}/{sl})*({be}-2*{rec}+0.2)*{kg}+3*D{r}*{kg},0)".format(r=r, **P), "=H{r}+I{r}+J{r}".format(r=r)]
        for j, v in enumerate(vals, 1):
            c = wa.cell(r, j, v); c.font = F(); c.border = BOR
            if j > 1: c.number_format = "0.00"
    rt = 9 + len(q)
    wa.cell(rt, 1, "TOTAL").font = F(bold=True); c = wa.cell(rt, 11, "=SUM(K9:K%d)" % (rt - 1)); c.font = F(bold=True); c.number_format = "0.00"; c.border = BOR
    wa.cell(rt + 2, 1, "Acero solo donde h >= 0.40 m (de la rejilla al fondo) o en tramo tapado; con h < 0.40 m la cuneta es de concreto simple. "
            "U de 3/8\" @0.25 m con ganchos de 0.10 m; longitudinales de 3/8\" @0.20 m en muros y losa de fondo; losa tapa: 3/8\" @0.20 m transversal y 3 barras longitudinales.").font = F(italic=True)
    for j, w in enumerate([10, 13, 13, 12, 10, 9, 11, 11, 11, 11, 12], 1): wa.column_dimensions[CL(j)].width = w
    # ---- PLANILLA GENERAL
    cab_doc(wp, "PLANILLA GENERAL DE METRADOS - DRENAJE PLUVIAL", 12)
    hdr = ["ITEM", "DESCRIPCION", "Nº DE VECES", "LARGO", "ANCHO", "ALTURA", "FACT.", "AREA", "VOLUMEN", "PARCIAL", "TOTAL", "UND"]
    for j, t in enumerate(hdr, 1):
        c = wp.cell(8, j, t); c.font = F(bold=True); c.fill = PatternFill("solid", fgColor=AZ); c.border = BOR; c.alignment = Alignment(horizontal="center")
    row = [9]; resumen = []
    def titulo(item, desc):
        r = row[0]; wp.cell(r, 1, item).font = F(bold=True); wp.cell(r, 2, desc).font = F(bold=True)
        for j in range(1, 13): wp.cell(r, j).fill = PatternFill("solid", fgColor=GR)
        resumen.append((item, desc, None, None)); row[0] += 1
    def partida(item, desc, und, filas, total=None):
        r0 = row[0]; wp.cell(r0, 1, item).font = F(bold=True); wp.cell(r0, 2, desc).font = F(bold=True); wp.cell(r0, 12, und).font = F(bold=True)
        row[0] += 1; ri = row[0]
        for f in filas:
            r = row[0]; d, C_, D_, E_, F_, G_, form = f
            for j, v in ((2, d), (3, C_), (4, D_), (5, E_), (6, F_), (7, G_)):
                if v is not None:
                    if isinstance(v, str) and v.startswith("="): v = v.format(r=r, **P)
                    c = wp.cell(r, j, v); c.font = F(); c.number_format = "0.00" if j > 2 else "@"
            c = wp.cell(r, 10, form.format(r=r, **P)); c.font = F(); c.number_format = "0.00"
            row[0] += 1
        c = wp.cell(r0, 11, total if total else "=SUM(J%d:J%d)" % (ri, row[0] - 1)); c.font = F(bold=True); c.number_format = "0.00"; c.border = BOR
        resumen.append((item, desc, und, "='PLANILLA GENERAL DE METRADOS'!K%d" % r0)); return r0
    L = lambda x: x["L"]
    titulo("01", "SISTEMA DE DRENAJE PLUVIAL - RED DE CUNETAS")
    titulo("01.01", "TRABAJOS PRELIMINARES")
    partida("01.01.01", "LIMPIEZA MANUAL DE TERRENO", "m²", [(x["eje"], 1, L(x), "={bexc}", None, None, "=C{r}*D{r}*E{r}") for x in q])
    partida("01.01.02", "TRAZO, NIVELES Y REPLANTEO PRELIMINAR", "m²", [(x["eje"], 1, L(x), "={bexc}", None, None, "=C{r}*D{r}*E{r}") for x in q])
    titulo("01.02", "MOVIMIENTO DE TIERRAS")
    r_exc = partida("01.02.01", "EXCAVACIÓN MANUAL DE ZANJAS P/CUNETAS", "m³",
                    [(x["eje"] + " (h prom. %.3f m)" % x["h_prom"], 1, L(x), "={bexc}", x["h_prom"], None, "=C{r}*D{r}*E{r}*(F{r}+{ef}+{sol})") for x in q])
    partida("01.02.02", "REFINE, NIVELACIÓN Y COMPACTACIÓN EN TERRENO NORMAL", "m²", [(x["eje"], 1, L(x), "={be}", None, None, "=C{r}*D{r}*E{r}") for x in q])
    r_rel = partida("01.02.03", "RELLENO COMPACTADO C/MATERIAL PROPIO SELECCIONADO", "m³",
                    [(x["eje"] + " (a los lados de la cuneta)", 1, L(x), "={bexc}-{be}", x["h_prom"], None, "=C{r}*D{r}*E{r}*(F{r}+{ef}+{sol})") for x in q])
    partida("01.02.04", "ELIMINACIÓN DE MATERIAL EXCEDENTE D<1Km", "m³",
            [("(Excavacion - relleno) x esponjamiento", None, None, None, None, "={esp}", "=(K%d-K%d)*G{r}" % (r_exc, r_rel))])
    partida("01.02.05", "PERFILADO MANUAL DE TERRENO EN DESCARGAS", "m²",
            [("Descarga %s (C.F. %.3f)" % (d["D"], d["cf"]), 1, d["sale_a_m"], "={be}", None, None, "=C{r}*D{r}*E{r}") for d in dsc])
    titulo("01.03", "OBRAS DE CONCRETO SIMPLE")
    partida("01.03.01", "CONCRETO f'c=100 kg/cm2 PARA SOLADO E=4''", "m²", [(x["eje"], 1, L(x), "={be}", None, None, "=C{r}*D{r}*E{r}") for x in q])
    titulo("01.04", "OBRAS DE CONCRETO ARMADO")
    titulo("01.04.01", "CUNETAS")
    filas = []
    for x in q:
        hw = round(x["area_muro"] / x["L"], 3)
        filas += [(x["eje"] + " muros (h libre prom. %.3f m)" % hw, 2, L(x), "={em}", hw, None, "=C{r}*D{r}*E{r}*F{r}"),
                  (x["eje"] + " losa de fondo", 1, L(x), "={be}", "={ef}", None, "=C{r}*D{r}*E{r}*F{r}")]
        if x["L_tapado"] > 0:
            filas.append((x["eje"] + " losa tapa (tramo tapado)", 1, x["L_tapado"], "={be}", "={et}", None, "=C{r}*D{r}*E{r}*F{r}"))
        if x["tapas"]:
            filas.append((x["eje"] + " descuento tapas de inspeccion", -x["tapas"], "={tl}", "={tl}", "={te}", None, "=C{r}*D{r}*E{r}*F{r}"))
    partida("01.04.01.01", "CONCRETO f'c=175 kg/cm2 PARA CUNETAS", "m³", filas)
    filas = []
    for x in q:
        hw = round(x["area_muro"] / x["L"], 3)
        filas += [(x["eje"] + " caras interiores de muros", 2, L(x), None, hw, None, "=C{r}*D{r}*F{r}"),
                  (x["eje"] + " caras exteriores de muros", 2, L(x), None, "=%s+{ef}" % hw, None, "=C{r}*D{r}*F{r}")]
        if x["L_tapado"] > 0:
            filas.append((x["eje"] + " fondo y cantos de losa tapa", 1, x["L_tapado"], "={b}+2*{et}", None, None, "=C{r}*D{r}*E{r}"))
    partida("01.04.01.02", "ENCOFRADO Y DESENCOFRADO DE CUNETAS", "m²", filas)
    partida("01.04.01.03", "ACERO f'y=4200 kg/cm2 PARA CUNETA", "kg",
            [(x["eje"] + " (hoja METRADO ACERO)", None, None, None, None, None, "='METRADO ACERO'!K%d" % fila_acero[x["eje"]]) for x in q])
    filas = []
    for x in q:
        hw = round(x["area_muro"] / x["L"], 3)
        filas += [(x["eje"] + " caras interiores de muros", 2, L(x), None, hw, None, "=C{r}*D{r}*F{r}"),
                  (x["eje"] + " fondo interior", 1, L(x), "={b}", None, None, "=C{r}*D{r}*E{r}")]
        filas.append((x["eje"] + " coronas de muro (tramo con rejilla)", 2, x["L_rejilla"], "={em}", None, None, "=C{r}*D{r}*E{r}"))
        if x["L_tapado"] > 0:
            filas.append((x["eje"] + " losa tapa", 1, x["L_tapado"], "={be}", None, None, "=C{r}*D{r}*E{r}"))
    partida("01.04.01.04", "CURADO DE CONCRETO EN CUNETA", "m²", filas)
    titulo("01.04.02", "VARIOS")
    partida("01.04.02.01", "REJILLA METALICA P/CUNETA C/PL 1''x 3/16'' Y ANGULO 1'' x 1'' x 3/16''", "m",
            [(x["eje"] + " (tramos abiertos)", 1, x["L_rejilla"], None, None, None, "=C{r}*D{r}") for x in q if x["L_rejilla"] > 0])
    partida("01.04.02.02", "TAPA DE INSPECCION 0.60m x 0.60m", "und",
            [(x["eje"] + " (tramos tapados)", x["tapas"], None, None, None, None, "=C{r}") for x in q if x["tapas"]])
    partida("01.04.02.03", "JUNTA DE DILATACION E=1\" CON SELLADOR ASFALTO", "m",
            [(x["eje"] + " (seccion en U cada 3.00 m)", x["n_juntas"], "=2*(%s+{ef})+{be}" % x["h_prom"], None, None, None, "=C{r}*D{r}")
             for x in q if x["n_juntas"]])
    partida("01.04.02.04", "JUNTA E=1\" CON SELLADOR ASFALTICO ENTRE CUNETA Y PISO ADYACENTE", "m",
            [(x["eje"] + " (bordes junto a piso o vereda)", 1, x["junta_piso"], None, None, None, "=C{r}*D{r}") for x in q if x["junta_piso"] > 0])
    for j, w in enumerate([12, 58, 9, 9, 9, 9, 8, 9, 9, 11, 12, 6], 1): wp.column_dimensions[CL(j)].width = w
    # ---- RESUMEN
    cab_doc(wr, "RESUMEN METRADOS DE DRENAJE PLUVIAL", 4)
    for j, t in enumerate(["Item", "Descripción", "Unid.", "Total."], 1):
        c = wr.cell(8, j, t); c.font = F(bold=True); c.fill = PatternFill("solid", fgColor=AZ); c.border = BOR
    for i, (it, d, u, f) in enumerate(resumen):
        r = 9 + i
        for j, v in enumerate([it, d, u, f], 1):
            c = wr.cell(r, j, v); c.font = F(bold=f is None); c.border = BOR
            if j == 4: c.number_format = "#,##0.00"
            if f is None: c.fill = PatternFill("solid", fgColor=GR)
    wr.column_dimensions["A"].width = 13; wr.column_dimensions["B"].width = 72; wr.column_dimensions["C"].width = 7; wr.column_dimensions["D"].width = 13
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False; ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1
        ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.page_setup.fitToHeight = 0
    wb.save(SAL); print(SAL)
    return resumen


if __name__ == "__main__":
    construir()
