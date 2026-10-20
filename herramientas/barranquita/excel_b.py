"""Cuadro de tramos del planteamiento preliminar de cunetas - I.E. N.° 0590, Barranquita (Excel con formulas).
Lee entregables_barranquita/_calc/diseno.json. Uso: python3 herramientas/barranquita/excel_b.py
"""
import os, sys, json
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL

SAL = os.path.join(RAIZ, "entregables_barranquita", "CUADRO_TRAMOS_CUNETAS_IE0590_BARRANQUITA.xlsx")
AZUL, AMA, VER, GRIS = "1F4E79", "FFF2CC", "E2EFDA", "F2F2F2"
_b = Side(style="thin", color="808080"); BOR = Border(left=_b, right=_b, top=_b, bottom=_b)
F = lambda **k: Font(name="Arial", size=k.pop("size", 9), **k)
PROY = ("MEJORAMIENTO Y AMPLIACION DEL SERVICIO DE EDUCACION PRIMARIA EN LA I.E. N.° 0590, DISTRITO DE BARRANQUITA, PROVINCIA DE LAMAS, "
        "DEPARTAMENTO DE SAN MARTIN - C.I. N.° 468901")
SIS = {1: "SISTEMA 1 - OESTE (descarga D1)", 2: "SISTEMA 2 - FRENTE SUR (descarga D3)", 3: "SISTEMA 3 - NOR-ESTE (descarga D2)",
       4: "SISTEMA 4 - INGRESO SUR-ESTE (descarga D4)"}


def cab(ws, fila, textos, anchos=None):
    for j, t in enumerate(textos, 1):
        c = ws.cell(fila, j, t); c.font = F(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor=AZUL)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = BOR
    ws.row_dimensions[fila].height = 30
    if anchos:
        for j, w in enumerate(anchos, 1): ws.column_dimensions[CL(j)].width = w


def titulo(ws, t, ncol):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol); ws["A1"] = t
    ws["A1"].font = F(bold=True, size=12, color=AZUL); ws["A1"].alignment = Alignment(horizontal="center")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncol); ws["A2"] = PROY
    ws["A2"].font = F(size=8); ws["A2"].alignment = Alignment(horizontal="center", wrap_text=True); ws.row_dimensions[2].height = 24


def main():
    R = json.load(open(os.path.join(RAIZ, "entregables_barranquita", "_calc", "diseno.json")))
    c = R["criterios"]; nom = R["nombre"]
    wb = Workbook()
    # ---- criterios
    wc = wb.active; wc.title = "CRITERIOS"
    titulo(wc, "CRITERIOS DEL PLANTEAMIENTO PRELIMINAR DE CUNETAS", 4)
    cab(wc, 4, ["PARAMETRO", "VALOR", "UND", "OBSERVACION"], [52, 12, 8, 70])
    par = [("Ancho libre de la cuneta (b)", c["b_int"], "m", "Seccion rectangular de concreto"),
           ("Espesor de muros", c["muro"], "m", "Ancho total = b + 2 muros"),
           ("Ancho total", "=B5+2*B6", "m", "Criterio del usuario: 0.60 m"),
           ("Profundidad al inicio de cada ramal", c["h0"], "m", "Criterio del usuario"),
           ("Profundidad minima", c["hmin"], "m", "Donde el terreno cae mas que la cuneta"),
           ("Pendiente de la cota de fondo", c["S"], "m/m", "0.5 %; mayor donde el terreno cae mas"),
           ("NTN de la plataforma de los bloques", c["ntn_plataforma"], "m", "Rotulos NTN del plano de arquitectura"),
           ("Coeficiente de Manning (concreto)", c["n_manning"], "", "Para la capacidad de cada tramo"),
           ("Borde libre", c["borde_libre"], "m", "Tirante maximo = h - borde libre")]
    for i, (t, v, u, o) in enumerate(par, 5):
        wc.cell(i, 1, t).font = F(); cc = wc.cell(i, 2, v); cc.font = F(bold=True); cc.fill = PatternFill("solid", fgColor=VER if isinstance(v, str) else AMA)
        wc.cell(i, 3, u).font = F(); wc.cell(i, 4, o).font = F()
        for j in range(1, 5): wc.cell(i, j).border = BOR
    wc.cell(15, 1, "Celda amarilla = dato; celda verde = formula. Los cambios de criterio se reflejan en las capacidades (hoja TRAMOS); "
                   "las cotas de fondo vienen del trazo (rehacer el calculo si cambian h inicial o S).").font = F(italic=True, size=8)
    # ---- tramos
    wt = wb.create_sheet("TRAMOS")
    titulo(wt, "CUADRO DE TRAMOS DE CUNETAS - COTAS DE FONDO, PROFUNDIDADES, PENDIENTES Y CAPACIDAD", 17)
    cab(wt, 4, ["SISTEMA", "RAMAL", "DE", "A", "L (m)", "RASANTE DE", "RASANTE A", "COTA DE FONDO DE", "COTA DE FONDO A", "h DE (m)", "h A (m)",
                "S (%)", "TAPADO (m)", "CON REJILLA (m)", "TIRANTE MAX. (m)", "Q CAPACIDAD (l/s)", "DESCRIPCION DEL RAMAL"],
        [9, 8, 7, 7, 9, 11, 11, 13, 13, 9, 9, 8, 10, 11, 11, 12, 60])
    f = 5
    for r in R["ramales"]:
        for t in r["tramos"]:
            vals = [r["sistema"], r["codigo"], nom[t["de"]], nom[t["a"]], t["L"], t["ras_de"], t["ras_a"], t["cf_de"], t["cf_a"],
                    "=F%d-H%d" % (f, f), "=G%d-I%d" % (f, f), "=100*(H%d-I%d)/E%d" % (f, f, f), t["L_tapado"], "=E%d-M%d" % (f, f),
                    "=MAX(MIN(J%d,K%d)-CRITERIOS!$B$13,0.01)" % (f, f),
                    "=1000*CRITERIOS!$B$5*O{0}*((CRITERIOS!$B$5*O{0})/(CRITERIOS!$B$5+2*O{0}))^(2/3)*SQRT(MAX(L{0}/100,CRITERIOS!$B$10))/CRITERIOS!$B$12".format(f),
                    r["descripcion"]]
            for j, v in enumerate(vals, 1):
                cc = wt.cell(f, j, v); cc.font = F(); cc.border = BOR
                cc.alignment = Alignment(horizontal="left" if j == 17 else "center", vertical="center")
                if j in (6, 7, 10, 11, 13, 14, 15): cc.number_format = "0.00"
                if j in (8, 9): cc.number_format = "0.000"
                if j == 5: cc.number_format = "0.00"
                if j in (12,): cc.number_format = "0.00"
                if j == 16: cc.number_format = "0.0"
                if isinstance(v, str) and v.startswith("="): cc.fill = PatternFill("solid", fgColor=VER)
            f += 1
    ft = f - 1
    wt.cell(f, 4, "TOTAL").font = F(bold=True)
    for j, col in ((5, "E"), (13, "M"), (14, "N")):
        cc = wt.cell(f, j, "=SUM(%s5:%s%d)" % (col, col, ft)); cc.font = F(bold=True); cc.number_format = "0.00"; cc.fill = PatternFill("solid", fgColor=VER); cc.border = BOR
    wt.freeze_panes = "E5"
    # ---- nudos
    wn = wb.create_sheet("NUDOS")
    titulo(wn, "NUDOS DE LA RED (COORDENADAS UTM WGS84 DEL PLANO DE ARQUITECTURA)", 5)
    cab(wn, 4, ["NUDO", "ESTE (m)", "NORTE (m)", "RAMALES QUE PASAN", "DESCARGA / OBSERVACION"], [9, 14, 15, 28, 70])
    pasa = {}
    for r in R["ramales"]:
        for n in r["nudos"]: pasa.setdefault(n, []).append(r["codigo"])
    orden = sorted(nom, key=lambda n: (nom[n].startswith("D"), nom[n]))
    for i, n in enumerate(orden, 5):
        x, y = R["nudos"][n]
        for j, v in enumerate([nom[n], x, y, ", ".join(pasa[n]), R["descargas"].get(n, "")], 1):
            cc = wn.cell(i, j, v); cc.font = F(bold=nom[n].startswith("D")); cc.border = BOR
            if j in (2, 3): cc.number_format = "0.000"
    # ---- resumen
    wr = wb.create_sheet("RESUMEN", 0)
    titulo(wr, "RESUMEN DEL PLANTEAMIENTO PRELIMINAR DE CUNETAS POR SISTEMA", 6)
    cab(wr, 4, ["SISTEMA", "LONGITUD (m)", "CON REJILLA (m)", "TAPADO (m)", "h MAXIMA (m)", "DESCARGA"], [48, 14, 15, 13, 13, 70])
    for i, k in enumerate((1, 2, 3, 4), 5):
        d = {1: "D1", 2: "D3", 3: "D2", 4: "D4"}[k]
        vals = [SIS[k], "=SUMIF(TRAMOS!$A$5:$A$%d,%d,TRAMOS!$E$5:$E$%d)" % (ft, k, ft), "=SUMIF(TRAMOS!$A$5:$A$%d,%d,TRAMOS!$N$5:$N$%d)" % (ft, k, ft),
                "=SUMIF(TRAMOS!$A$5:$A$%d,%d,TRAMOS!$M$5:$M$%d)" % (ft, k, ft),
                max(max(t["h_max"] for t in r["tramos"]) for r in R["ramales"] if r["sistema"] == k), d + ": " + R["descargas"][d]]
        for j, v in enumerate(vals, 1):
            cc = wr.cell(i, j, v); cc.font = F(); cc.border = BOR
            if j in (2, 3, 4, 5): cc.number_format = "0.00"; cc.alignment = Alignment(horizontal="center")
            if isinstance(v, str) and v.startswith("="): cc.fill = PatternFill("solid", fgColor=VER)
    wr.cell(9, 1, "TOTAL").font = F(bold=True)
    for j, col in ((2, "B"), (3, "C"), (4, "D")):
        cc = wr.cell(9, j, "=SUM(%s5:%s8)" % (col, col)); cc.font = F(bold=True); cc.number_format = "0.00"; cc.fill = PatternFill("solid", fgColor=VER); cc.border = BOR
    notas = ["Planteamiento preliminar sobre los ejes de cunetas del plano PLANTA_GENERAL_590_2 (capas 0_ CUNETAS y 0_REJILLA).",
             "Sentidos de flujo y descargas segun las curvas de nivel C-TOPO del mismo plano. Techos a dos aguas: cada alero descarga a su lado.",
             "Rasante: NTN +184.50 en la plataforma de los bloques; terreno de las curvas en el resto (monticulo de 185.5 recortado a +184.50).",
             "D1, D2 y D4 salen a la superficie del terreno por gravedad; D3 entrega al punto bajo del Jr. Alfonso Ugarte (183.00): confirmar su evacuacion.",
             "Tramos de fuerte pendiente con V > 3.0 m/s: gradas de concreto (hoja HIDRAULICA). Verificacion completa en la hoja VERIFICACION.",
             "Ver planos PLANTEAMIENTO_CUNETAS_IE0590_BARRANQUITA.dxf: DC-01 planta, DC-02 cuadro y secciones, DC-03 a DC-06 perfiles, DC-07 y DC-08 isometricos, DC-09 y DC-10 cortes."]
    wr.cell(11, 1, "NOTAS").font = F(bold=True, color=AZUL)
    for i, t in enumerate(notas, 12):
        wr.cell(i, 1, "%d. %s" % (i - 11, t)).font = F(size=8)
    # ---- verificacion (10 comprobaciones) e hidraulica con el caudal de diseno
    Vf = json.load(open(os.path.join(RAIZ, "entregables_barranquita", "_calc", "verificacion.json")))
    wv = wb.create_sheet("VERIFICACION", 1)
    titulo(wv, "VERIFICACION DEL PLANTEAMIENTO (10 COMPROBACIONES)", 4)
    cab(wv, 4, ["N.", "COMPROBACION", "RESULTADO", "DETALLE"], [5, 62, 22, 120])
    for i, c_ in enumerate(Vf["comprobaciones"], 5):
        for j, v in enumerate([c_["n"], c_["comprobacion"], c_["estado"], c_["detalle"]], 1):
            cc = wv.cell(i, j, v); cc.font = F(bold=(j == 3)); cc.border = BOR; cc.alignment = Alignment(wrap_text=True, vertical="top")
            if j == 3: cc.fill = PatternFill("solid", fgColor=VER if c_["estado"] == "CUMPLE" else AMA)
        wv.row_dimensions[i].height = 15 * max(1, len(str(c_["detalle"])) // 95 + 1)
    r0 = 5 + len(Vf["comprobaciones"]) + 1
    wv.cell(r0, 2, "DESCARGAS").font = F(bold=True, color=AZUL)
    cab(wv, r0 + 1, ["", "DESCARGA", "COTA DE FONDO", "SALIDA POR GRAVEDAD"])
    for i, d in enumerate(Vf["descargas"], r0 + 2):
        txt = ("sale a la superficie del terreno a %.1f m (corte maximo %.2f m)" % (d["sale_a_m"], d["corte_max"])) if d["sale_a_m"] is not None else \
              "terreno plano: entrega al %s" % d["receptor"]
        for j, v in enumerate(["", d["D"], d["cf"], txt], 1):
            cc = wv.cell(i, j, v); cc.font = F(); cc.border = BOR
    h = Vf["hidrologia"]
    wh = wb.create_sheet("HIDRAULICA", 3)
    titulo(wh, "CAUDAL DE DISENO, TIRANTE Y VELOCIDAD POR TRAMO (REFERENCIAL)", 13)
    par = [("C (escorrentia)", h["C"]), ("I (mm/h)", h["I"]), ("Factor de seguridad", h["FS"]), ("Velocidad maxima (m/s)", 3.0)]
    for i, (t, v) in enumerate(par, 4):
        wh.cell(i, 1, t).font = F(); cc = wh.cell(i, 2, v); cc.font = F(bold=True); cc.fill = PatternFill("solid", fgColor=AMA); cc.border = BOR
    wh.cell(8, 1, "I: tc = %.0f min, TR = 25 anos, P10 = %.2f mm (estacion usada en el Hogar de Refugio - Morales); reemplazar por la del proyecto. "
                  "Area tributaria: cada m2 dentro del cerco a la cuneta mas cercana." % (h["tc"], h["P10"])).font = F(italic=True, size=8)
    cab(wh, 10, ["RAMAL", "DE", "A", "AREA (m2)", "Q (l/s)", "S (%)", "TIRANTE y (m)", "h (m)", "BORDE LIBRE (m)", "V (m/s)", "CAPACIDAD", "VELOCIDAD", "OBSERVACION"],
        [9, 7, 7, 11, 10, 8, 12, 8, 13, 9, 12, 12, 46])
    for i, fh in enumerate(Vf["hidraulica"], 11):
        vals = [fh["ramal"], fh["de"], fh["a"], fh["A_m2"], "=1000*$B$4*$B$5*D%d/3600000*$B$6" % i, fh["S"], fh["y"], fh["h"], "=H%d-G%d" % (i, i),
                fh["V"], '=IF(I%d>=0.05,"CUMPLE","NO CUMPLE")' % i, '=IF(J%d<=$B$7,"CUMPLE","GRADAS")' % i,
                "gradas de concreto (escalones) en este tramo" if fh["vel"] != "CUMPLE" else ""]
        for j, v in enumerate(vals, 1):
            cc = wh.cell(i, j, v); cc.font = F(); cc.border = BOR; cc.alignment = Alignment(horizontal="center" if j < 13 else "left")
            if j in (7, 9): cc.number_format = "0.000"
            if j in (5, 10): cc.number_format = "0.00"
            if isinstance(v, str) and v.startswith("="): cc.fill = PatternFill("solid", fgColor=VER)
    wh.freeze_panes = "D11"
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False; ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1
        ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.page_setup.fitToHeight = 0
    wb.save(SAL); print(SAL)


if __name__ == "__main__":
    main()
