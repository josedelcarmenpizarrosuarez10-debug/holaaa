# -*- coding: utf-8 -*-
"""Crea o actualiza el libro de datos del proyecto (DATOS_PROYECTO.xlsx) a partir del presupuesto exportado de S10 en PDF.
Solo se toman ítem, descripción, unidad y metrado (los precios no se usan en el PSST).

Uso:  python3 importar_s10.py <presupuesto_S10.pdf> <DATOS_PROYECTO.xlsx>
Si el libro ya existe, solo se reemplaza la hoja PARTIDAS; las demás hojas (PROYECTO, PERSONAL, EMERGENCIA) se conservan.
Sin PDF:  python3 importar_s10.py --plantilla <DATOS_PROYECTO.xlsx>   crea el libro vacío para llenar a mano."""
import os, re, subprocess, sys
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

CAMPOS = [  # campo, descripción, ejemplo
    ("codigo", "Código corto para nombrar los archivos", "SM107"),
    ("nombre", "Nombre del proyecto de inversión", ""),
    ("cui", "Código único de inversiones (CUI)", ""),
    ("entidad", "Entidad", ""),
    ("unidad_ejecutora", "Unidad ejecutora / órgano a cargo", ""),
    ("ubicacion", "Ubicación (distrito, provincia, departamento)", ""),
    ("tipo_obra", "Tipo de obra (vial, edificación, saneamiento, drenaje, puente, electrificación, otro)", "vial"),
    ("descripcion", "Descripción breve de la obra (metas principales)", ""),
    ("plazo_dias", "Plazo de ejecución en días calendario", "720"),
    ("modalidad", "Modalidad de ejecución", "Por contrata"),
    ("altitud_msnm", "Altitud media de la obra (msnm)", ""),
    ("clima", "Clima (texto)", ""),
    ("condiciones", "Condiciones del lugar separadas por coma: selva, altura, cauces, zona_poblada, transito", ""),
    ("jornada", "Jornada de trabajo", "Lunes a sábado de 07:00 a 17:00 (48 h semanales)"),
    ("ejecutor", "Empresa ejecutora (dejar en blanco hasta la adjudicación)", ""),
    ("fecha", "Mes y año del documento", ""),
    ("encabezado_1", "Primera línea de la portada (entidad)", ""),
    ("encabezado_2", "Segunda línea de la portada (dependencia)", ""),
]
AZUL = "1F4E79"; AMARILLO = "FFF2CC"
_b = Side(style="thin", color="999999"); BORDE = Border(left=_b, right=_b, top=_b, bottom=_b)


def _cab(ws, fila, textos, anchos):
    for j, (t, w) in enumerate(zip(textos, anchos), 1):
        c = ws.cell(fila, j, t); c.font = Font(bold=True, color="FFFFFF", name="Arial", size=9)
        c.fill = PatternFill("solid", fgColor=AZUL); c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = BORDE
        ws.column_dimensions[chr(64 + j)].width = w


def leer_pdf(pdf):
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    filas, ult = [], None
    for ln in txt.splitlines():
        s = ln.strip()
        if not s or re.match(r"^(S10|Presupuesto|Subpresupuesto|Cliente|Lugar|Item|Fecha|Costo Directo|SON :|Página)", s) or s.startswith('"'):
            ult = None if s.startswith(("S10", "Fecha")) else ult; continue
        m = re.match(r"^(\d+(?:\.\d+)+|\d+)\s{2,}(.*)$", s)
        if m:
            item, resto = m.group(1), m.group(2)
            cols = re.split(r"\s{2,}", resto)
            num = lambda t: re.fullmatch(r"-?[\d,]+\.\d+", t or "") is not None
            if len(cols) >= 4 and num(cols[-3]):          # partida: desc, und, metrado, precio, parcial
                desc = " ".join(cols[:-4]) if len(cols) > 4 else cols[0]
                und = cols[-4] if len(cols) > 4 else ""
                if len(cols) == 4: desc, und = cols[0], ""
                filas.append([item, desc.strip(), und.strip(), float(cols[-3].replace(",", ""))])
            else:                                           # título: desc, parcial
                filas.append([item, " ".join(c for c in cols if not num(c)).strip(), "", None])
            ult = filas[-1]
        elif ult is not None and not re.search(r"\d[\d,]*\.\d{2}$", s) and len(ln) - len(ln.lstrip()) > 8:
            ult[1] = (ult[1] + " " + s).strip()            # descripción que continúa en la línea siguiente
    return filas


def escribir_partidas(wb, filas):
    if "PARTIDAS" in wb.sheetnames: del wb["PARTIDAS"]
    ws = wb.create_sheet("PARTIDAS", 1)
    _cab(ws, 1, ["ÍTEM", "DESCRIPCIÓN", "UND.", "METRADO"], [14, 80, 8, 14])
    for i, f in enumerate(filas, 2):
        for j, v in enumerate(f, 1):
            c = ws.cell(i, j, v); c.font = Font(name="Arial", size=9, bold=not f[2]); c.border = BORDE
            if j == 4: c.number_format = "#,##0.00"
    ws.freeze_panes = "A2"


def plantilla(ruta):
    wb = Workbook(); ws = wb.active; ws.title = "PROYECTO"
    _cab(ws, 1, ["CAMPO", "DESCRIPCIÓN", "VALOR"], [18, 60, 90])
    for i, (k, d, e) in enumerate(CAMPOS, 2):
        ws.cell(i, 1, k).font = Font(name="Arial", size=9, bold=True); ws.cell(i, 2, d).font = Font(name="Arial", size=9)
        c = ws.cell(i, 3, e); c.fill = PatternFill("solid", fgColor=AMARILLO); c.font = Font(name="Arial", size=9)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        for j in (1, 2, 3): ws.cell(i, j).border = BORDE
    escribir_partidas(wb, [])
    ws = wb.create_sheet("PERSONAL"); _cab(ws, 1, ["MES", "TRABAJADORES (promedio)", "ETAPA / ACTIVIDADES PRINCIPALES"], [8, 14, 70])
    ws = wb.create_sheet("EMERGENCIA"); _cab(ws, 1, ["INSTITUCIÓN", "UBICACIÓN / DISTANCIA", "TELÉFONO"], [55, 45, 18])
    for i, (a, b, c) in enumerate([("Central de emergencias de la Policía Nacional del Perú", "Nacional", "105"),
                                   ("Cuerpo General de Bomberos Voluntarios del Perú", "Nacional", "116"),
                                   ("SAMU - Sistema de Atención Móvil de Urgencias (MINSA)", "Nacional", "106")], 2):
        for j, v in enumerate((a, b, c), 1): ws.cell(i, j, v).border = BORDE
    wb.save(ruta)


if __name__ == "__main__":
    if sys.argv[1] == "--plantilla":
        plantilla(sys.argv[2]); print("plantilla", sys.argv[2]); sys.exit()
    pdf, xlsx = sys.argv[1], sys.argv[2]
    if not os.path.exists(xlsx): plantilla(xlsx)
    filas = leer_pdf(pdf); wb = load_workbook(xlsx); escribir_partidas(wb, filas); wb.save(xlsx)
    print(xlsx, "partidas:", sum(1 for f in filas if f[2]), "títulos:", sum(1 for f in filas if not f[2]))
