"""CAR Mujeres (CUI 2717013): memoria de calculo del colector pluvial frontal en PDF, con el estilo visual de la
memoria HIDRO-CE040 (titulo serif, recuadro de formulas, tablas con encabezado celeste, bloque de diseno final).

Fuente: insumos/wilma/MEMORIA_CALCULO_COLECTOR_CAR_MUJERES_3_PROYECTOS.xlsx (hojas MEMORIA, DATOS, CAUDALES, SALIDA,
PERFIL_FLUJO, ESTRUCTURAL). El libro se recalcula con LibreOffice y se copian sus valores sin cambiarlos; solo se da
formato (y tildes a los textos). El HTML se imprime a PDF A4 con Chromium (Playwright de node).
Uso: python3 herramientas/mujeres/memoria_pdf_m.py
"""
import os, re, sys, html, json, shutil, subprocess, tempfile
import openpyxl

AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
XLSX = os.path.join(RAIZ, "insumos", "wilma", "MEMORIA_CALCULO_COLECTOR_CAR_MUJERES_3_PROYECTOS.xlsx")
SALIDA = os.path.join(RAIZ, "entregables_mujeres", "MEMORIA_CALCULO_COLECTOR_CAR_MUJERES.pdf")
PROYECTO = ("“CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO "
            "DE PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - MUJERES DISTRITO DE MORALES DE LA PROVINCIA DE SAN MARTÍN DEL "
            "DEPARTAMENTO DE SAN MARTÍN”, con CUI N.° 2717013 · SAN MARTIN - SAN MARTIN - MORALES · octubre 2026")

# ------------------------------------------------------------------ tildes (los textos del libro van sin tildes)
TILDES = {
    "calculo": "cálculo", "CALCULO": "CÁLCULO", "diseno": "diseño", "Diseno": "Diseño", "DISENO": "DISEÑO", "anos": "años",
    "Precipitacion": "Precipitación", "precipitacion": "precipitación", "precipitaciones": "precipitaciones",
    "Analisis": "Análisis", "analisis": "análisis", "estadistico": "estadístico", "concentracion": "concentración",
    "GEOMETRIA": "GEOMETRÍA", "Topografia": "Topografía", "via": "vía", "monolitica": "monolítica", "MONOLITICA": "MONOLÍTICA",
    "VERIFICACION": "VERIFICACIÓN", "Verificacion": "Verificación", "verificacion": "verificación", "HIDRAULICA": "HIDRÁULICA",
    "hidraulica": "hidráulica", "hidraulicas": "hidráulicas", "maximo": "máximo", "Maximo": "Máximo", "minimo": "mínimo",
    "minima": "mínima", "Formula": "Fórmula", "FORMULA": "FÓRMULA", "critico": "crítico", "hipotesis": "hipótesis",
    "METODO": "MÉTODO", "Metodo": "Método", "metodo": "método", "Ecuacion": "Ecuación", "biseccion": "bisección",
    "Cuantia": "Cuantía", "cuantia": "cuantía", "Flexion": "Flexión", "flexion": "flexión", "Reaccion": "Reacción",
    "Presion": "Presión", "PRESION": "PRESIÓN", "ultimo": "último", "ultima": "última", "camion": "camión",
    "PARAMETROS": "PARÁMETROS", "PARAMETRO": "PARÁMETRO", "SIMBOLO": "SÍMBOLO", "numero": "número", "HIDROLOGIA": "HIDROLOGÍA",
    "economicas": "económicas", "estandar": "estándar", "ESTANDAR": "ESTÁNDAR", "energia": "energía", "Segun": "Según",
    "seccion": "sección", "secciones": "secciones", "estacion": "estación", "conduccion": "conducción", "tecnica": "técnica",
    "region": "región", "dinamica": "dinámica", "Crta": "Crta", "CAMION": "CAMIÓN", "Cortante": "Cortante",
    "Huella": "Huella", "AREA": "ÁREA", "Area": "Área", "PONDERADO": "PONDERADO", "Hogar de Refugio M. Violentadas": "Hogar de Refugio M. Violentadas",
    "salida": "salida", "rebalsa": "rebalsa", "linea": "línea", "electrica": "eléctrica", "basicas": "básicas",
    "util": "útil", "valido": "válido", "unica": "única", "unico": "único", "Huelga": "Huelga", "tambien": "también",
    "mas": "más", "ademas": "además", "areas": "áreas", "formulas": "fórmulas", "Hidrologia": "Hidrología", "Hidraulica": "Hidráulica", "Normativa": "Normativa", "duracion": "duración", "Periodo": "Período", "edificaciones": "edificaciones", "Codigo": "Código", "codigo": "código", "Pagina": "Página", "metrica": "métrica",
}
FRASES = {": ver abajo (se actualizan con las formulas).": ": ver «Resultados de la verificación».", "<=": "≤", ">=": "≥", "salida esta controlada": "salida está controlada", "por la una (2.91 m)": "por la uña (2.91 m)", "el mas desfavorable": "el más desfavorable", "caso mas": "caso más"}
_RX = re.compile(r"\b(" + "|".join(sorted(map(re.escape, TILDES), key=len, reverse=True)) + r")\b")


def tilde(s):
    if not isinstance(s, str): return s
    for a, b in FRASES.items(): s = s.replace(a, b)
    return _RX.sub(lambda m: TILDES[m.group(1)], s)


def esc(s): return html.escape(tilde(s) if isinstance(s, str) else ("" if s is None else str(s)))


def fmt(v):
    """Formato general de un valor del libro: enteros sin decimales, el resto con 3-4 cifras significativas utiles."""
    if v is None: return ""
    if isinstance(v, str): return esc(v)
    if abs(v - round(v)) < 1e-9: return "%d" % round(v)
    a = abs(v)
    if 250 <= a <= 300: return "%.3f" % v          # cotas (msnm): al milimetro
    if a >= 100: return "%.2f" % v
    if a >= 1: return "%.3f" % v
    return "%.4f" % v if a < 0.01 else "%.3f" % v


# ------------------------------------------------------------------ lectura del libro recalculado
def libro():
    tmp = tempfile.mkdtemp()
    shutil.copy(XLSX, os.path.join(tmp, "m.xlsx"))
    subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", os.path.join(tmp, "c"), os.path.join(tmp, "m.xlsx")],
                   check=True, capture_output=True)
    wb = openpyxl.load_workbook(os.path.join(tmp, "c", "m.xlsx"), data_only=True)
    shutil.rmtree(tmp)
    return wb


def filas(ws, r0, r1, c1=5):
    return [[ws.cell(r, c).value for c in range(1, c1 + 1)] for r in range(r0, r1 + 1)]


# ------------------------------------------------------------------ piezas de HTML
def tabla(cab, rows, cls="", anchos=None, alinear=None):
    col = "".join('<col style="width:%s">' % a for a in anchos) if anchos else ""
    th = "".join("<th>%s</th>" % esc(c) for c in cab)
    trs = []
    for r in rows:
        if isinstance(r, tuple) and r and r[0] == "__grupo__":
            trs.append('<tr class="grupo"><td colspan="%d">%s</td></tr>' % (len(cab), esc(r[1]))); continue
        tds = []
        for j, c in enumerate(r):
            al = (alinear or {}).get(j, "")
            if isinstance(c, str) and c.strip().upper() in ("CUMPLE", "NO CUMPLE"):
                k = "ok" if c.strip().upper() == "CUMPLE" else "no"
                tds.append('<td class="%s"><span class="badge %s">%s</span></td>' % (al, k, c.strip().upper()))
            else:
                tds.append('<td class="%s">%s</td>' % (al, c if isinstance(c, str) and c.startswith("<") else (esc(c) if isinstance(c, str) else fmt(c))))
        trs.append("<tr>%s</tr>" % "".join(tds))
    return '<table class="%s">%s<thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (cls, "<colgroup>%s</colgroup>" % col if col else "", th, "".join(trs))


def frac(a, b): return '<span class="fr"><span>%s</span><span>%s</span></span>' % (a, b)


def formulas(lineas): return '<div class="formulas">%s</div>' % "".join('<div class="fl">%s</div>' % l for l in lineas)


def perfil_svg(rows):
    """Perfil longitudinal: fondo, nivel de agua y techo disponible (cara inferior de la losa) por progresiva."""
    pts = [(r[0], r[1], r[5], r[8]) for r in rows if isinstance(r[0], (int, float))]
    W, H, ml, mr, mt, mb = 720, 230, 52, 26, 14, 34
    xs = [p[0] for p in pts]; zmin = min(p[1] for p in pts) - 0.05; zmax = max(p[3] for p in pts) + 0.08
    X = lambda x: ml + (x - min(xs)) / (max(xs) - min(xs)) * (W - ml - mr)
    Y = lambda z: mt + (zmax - z) / (zmax - zmin) * (H - mt - mb)
    pol = lambda k: " ".join("%.1f,%.1f" % (X(p[0]), Y(p[k])) for p in pts)
    agua = pol(2) + " " + " ".join("%.1f,%.1f" % (X(p[0]), Y(p[1])) for p in reversed(pts))
    g = []
    z = round(zmin + 0.05, 1)
    while z <= zmax:
        g.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" class="gr"/><text x="%d" y="%.1f" class="ax" text-anchor="end">%.1f</text>'
                 % (ml, W - mr, Y(z), Y(z), ml - 6, Y(z) + 3, z)); z = round(z + 0.1, 1)
    for x in range(0, 141, 20):
        g.append('<line x1="%.1f" x2="%.1f" y1="%d" y2="%d" class="gr"/><text x="%.1f" y="%d" class="ax" text-anchor="middle">%s</text>'
                 % (X(x), X(x), mt, H - mb, X(x), H - mb + 14, "0+%03d" % x))
    return ('<svg viewBox="0 0 %d %d" class="perfil" xmlns="http://www.w3.org/2000/svg">%s'
            '<polygon points="%s" class="aguaf"/><polyline points="%s" class="techo"/><polyline points="%s" class="agua"/>'
            '<polyline points="%s" class="fondo"/><text x="%d" y="%d" class="ax" text-anchor="middle">Progresiva (m)</text>'
            '<text x="12" y="%d" class="ax" transform="rotate(-90 12 %d)" text-anchor="middle">Cota (msnm)</text></svg>'
            % (W, H, "".join(g), agua, pol(3), pol(2), pol(1), (ml + W - mr) // 2, H - 4, H // 2, H // 2))


CSS = """
@page { size: A4; margin: 15mm 14mm 17mm 14mm; }
* { box-sizing: border-box; }
body { font-family: 'Liberation Sans', Arial, Helvetica, sans-serif; font-size: 9.6pt; color: #1d2329; line-height: 1.42; margin: 0; }
h1 { font-family: 'DejaVu Serif', Georgia, serif; font-size: 21pt; font-weight: 700; margin: 0 0 4px; color: #11161b; letter-spacing: -0.2px; }
.proy { font-size: 7.9pt; color: #4b555e; text-transform: none; margin: 0 0 6px; line-height: 1.35; }
.meta { font-size: 9.4pt; margin: 4px 0 10px; color: #3a434b; }
.meta b { color: #11161b; }
h2 { font-size: 12.2pt; margin: 16px 0 6px; color: #11161b; page-break-after: avoid; }
h2 .n { color: #2a6f73; margin-right: 6px; }
h3 { font-size: 10.4pt; margin: 12px 0 5px; color: #11161b; page-break-after: avoid; }
p { margin: 0 0 6px; }
.small { font-size: 8.4pt; color: #3a434b; }
.formulas { background: #eef3f6; border-radius: 2px; padding: 9px 12px; margin: 6px 0 10px; font-family: 'DejaVu Serif', 'Liberation Serif', serif; font-size: 9.6pt; page-break-inside: avoid; }
.formulas .fl { margin: 5px 0; line-height: 1.7; }
.formulas sub, .formulas sup, th sub { font-size: 68%; line-height: 0; position: relative; vertical-align: baseline; }
.formulas sub, th sub { bottom: -0.3em; } .formulas sup { bottom: 0.55em; }
.fr { display: inline-flex; flex-direction: column; align-items: center; vertical-align: middle; margin: 0 3px; font-size: 9pt; }
.fr span:first-child { border-bottom: 1px solid #1d2329; padding: 0 3px 1px; }
.fr span:last-child { padding: 1px 3px 0; }
table { width: 100%; border-collapse: collapse; margin: 4px 0 8px; font-size: 8.7pt; page-break-inside: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #e9f1f5; color: #1d2329; font-weight: 700; text-align: left; padding: 5px 7px; border: 1px solid #d3dee5; }
td { padding: 4.5px 7px; border: 1px solid #dfe7ec; vertical-align: top; }
td.r, th.r { text-align: right; } td.c { text-align: center; }
tr.grupo td { background: #f5f8fa; font-weight: 700; color: #2a6f73; font-size: 8.4pt; letter-spacing: .3px; }
table.perf { font-size: 7.1pt; } table.perf td, table.perf th { padding: 2.6px 4px; text-align: right; } table.perf td:nth-last-child(-n+2), table.perf th:nth-last-child(-n+2) { text-align: left; }
.badge { display: inline-block; font-size: 7.4pt; font-weight: 700; padding: 1px 6px; border-radius: 8px; letter-spacing: .3px; }
.badge.ok { background: #e3f3ea; color: #1e6b43; } .badge.no { background: #fbe4e4; color: #9b1c1c; }
.final { border-left: 4px solid #2a6f73; padding: 2px 0 2px 12px; margin: 10px 0 10px; page-break-inside: avoid; }
.final h3 { margin-top: 2px; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 6px 0 4px; }
.kpi { background: #f5f8fa; border: 1px solid #dfe7ec; border-radius: 3px; padding: 7px 9px; }
.kpi .v { font-family: 'DejaVu Serif', serif; font-size: 12.5pt; white-space: nowrap; font-weight: 700; color: #11161b; }
.kpi .l { font-size: 7.6pt; color: #4b555e; }
.perfil { width: 100%; height: auto; margin: 4px 0 2px; }
.perfil .gr { stroke: #e3eaee; stroke-width: 1; } .perfil .ax { font-size: 9px; fill: #4b555e; font-family: 'Liberation Sans', sans-serif; }
.perfil .fondo { fill: none; stroke: #5b6670; stroke-width: 2; } .perfil .techo { fill: none; stroke: #9aa6ad; stroke-width: 1.4; stroke-dasharray: 5 3; }
.perfil .agua { fill: none; stroke: #2b8cbf; stroke-width: 1.8; } .perfil .aguaf { fill: #cfe8f3; opacity: .85; }
.ley { display: flex; gap: 16px; font-size: 8pt; color: #3a434b; margin: 0 0 8px; }
.ley i { display: inline-block; width: 16px; height: 0; border-top: 2px solid; vertical-align: middle; margin-right: 5px; }
.firma { border-top: 1px solid #c9d3d9; margin-top: 18px; padding-top: 8px; font-size: 9pt; color: #3a434b; page-break-inside: avoid; }
.salto { page-break-before: always; }
.bloque { page-break-inside: avoid; }
.ref { font-size: 8.4pt; color: #3a434b; margin-top: 6px; }
"""


def construir():
    wb = libro()
    M, DA, CA, SA, PF, ES = (wb[k] for k in ("MEMORIA", "DATOS", "CAUDALES", "SALIDA", "PERFIL_FLUJO", "ESTRUCTURAL"))
    v = lambda ws, ref: ws[ref].value
    out = []
    # ---------------------------------------------------------- 0. encabezado y memoria descriptiva
    out.append('<h1>Memoria de cálculo del colector pluvial frontal</h1><div class="proy">%s</div>' % esc(PROYECTO))
    out.append('<div class="meta"><b>TRAMO CAR MUJERES</b> · 0+000 a 0+139.08 · dimensionado para recibir CAR Varones (CUI 2705619) '
               'y Hogar de Refugio (CUI 2675514) · RNE CE.040</div>')
    out.append('<div class="kpis">%s</div>' % "".join(
        '<div class="kpi"><div class="v">%s</div><div class="l">%s</div></div>' % (a, b) for a, b in (
            ("%.1f L/s" % v(M, "B11"), "Caudal total en la salida"), ("%.3f msnm" % v(M, "B12"), "Nivel de control en la salida"),
            ("%.3f" % v(M, "B14"), "Llenado máximo y/h (admisible 0.85)"), ("%.3f m" % v(M, "B15"), "Borde libre mínimo bajo tapa (mín. 0.05)"))))
    out.append("<h2>Datos y metodología</h2>")
    for r in range(4, 10):
        out.append("<p><b>%s.</b> %s</p>" % (esc(v(M, "A%d" % r).split(". ", 1)[1].capitalize()), esc(v(M, "B%d" % r))))
    res = [[tilde(v(M, "A%d" % r)), v(M, "B%d" % r)] for r in range(11, 18)]
    out.append('<div class="final"><h3>Resultados de la verificación</h3>%s</div>' % tabla(
        ["Resultado", "Valor"], [[a, ("%.3f" % b if isinstance(b, float) and b < 10 else fmt(b))] for a, b in res], anchos=["70%", "30%"], alinear={1: "r"}))
    out.append('<p class="ref"><b>Nota.</b> %s</p>' % esc(v(M, "B19")))
    # ---------------------------------------------------------- 1. datos de diseno
    out.append('<h2 class="salto"><span class="n">1.</span>Datos de diseño</h2>')
    out.append(formulas(["b = ln(P<sub>20</sub> / P<sub>10</sub>) / ln 2", "I = P<sub>10</sub> · (t<sub>c</sub> / 10)<sup>b</sup> / (t<sub>c</sub> / 60) &nbsp;[mm/h]"]))
    rows = []
    for r in range(5, 34):
        a, b, c, d, e = (DA.cell(r, k).value for k in range(1, 6))
        if a is None: continue
        if b is None and c is None and d is None: rows.append(("__grupo__", a)); continue
        rows.append([tilde(a), b, c or "", tilde(d or ""), e or ""])
    out.append(tabla(["Parámetro", "Valor", "Und", "Fuente / criterio", "Símbolo"], rows, anchos=["33%", "11%", "8%", "40%", "8%"], alinear={1: "r"}))
    # ---------------------------------------------------------- 2. caudales
    out.append('<h2><span class="n">2.</span>Caudales de diseño: método racional</h2>')
    out.append(formulas(["Q = C · I · A · FS / 3 600 000 &nbsp;[m<sup>3</sup>/s] &nbsp;(I en mm/h, A en m<sup>2</sup>); &nbsp;C ponderado = Σ(C·A) / ΣA"]))
    rows = [[tilde(a), b, c, d, e, f, tilde(g or ""), tilde(h or "")] for a, b, c, d, e, f, g, h in filas(CA, 5, 8, 8)]
    out.append(tabla(["Proyecto", "Área (m²)", "C × A (m²)", "C pond.", "I (mm/h)", "Q (L/s)", "Ingresa al colector en", "Fuente"], rows,
                     anchos=["21%", "9%", "10%", "7%", "8%", "8%", "19%", "18%"], alinear={1: "r", 2: "r", 3: "r", 4: "r", 5: "r"}))
    out.append("<h3>%s</h3>" % esc(v(CA, "A10")))
    rows = [[tilde(a), "0+%06.2f" % b, c, d] for a, b, c, d in filas(CA, 12, 15, 4)]
    out.append(tabla(["Punto", "Progresiva", "Aporte (L/s)", "Q acumulado (L/s)"], rows, anchos=["46%", "16%", "19%", "19%"], alinear={1: "r", 2: "r", 3: "r"}))
    out.append('<p class="small">%s</p>' % esc(v(CA, "A17")))
    # ---------------------------------------------------------- 3. salida
    out.append('<h2><span class="n">3.</span>Condición de control en la salida</h2>')
    out.append(formulas(["H = (Q / (C<sub>w</sub> · L<sub>w</sub>))<sup>2/3</sup>; &nbsp;NA<sub>vertido</sub> = cresta + H",
                         "y<sub>c</sub> = (Q<sup>2</sup> / (g · b<sup>2</sup>))<sup>1/3</sup>; &nbsp;NA<sub>crítico</sub> = CF<sub>salida</sub> + y<sub>c</sub>; &nbsp;NA<sub>control</sub> = máx(NA<sub>vertido</sub>, NA<sub>crítico</sub>)"]))
    rows = [[tilde(a), b, c, tilde(d or "")] for a, b, c, d in filas(SA, 5, 10, 4)]
    out.append(tabla(["Parámetro", "Valor", "Und", "Fórmula"], rows, anchos=["38%", "14%", "10%", "38%"], alinear={1: "r"}))
    out.append('<p class="small">%s</p>' % esc(v(SA, "A12")))
    # ---------------------------------------------------------- 4. perfil de flujo
    out.append('<h2><span class="n">4.</span>Perfil de flujo gradualmente variado: método del paso estándar</h2>')
    out.append("<p>Cálculo desde la salida hacia aguas arriba. El tirante de cada estación se resuelve por bisección.</p>")
    out.append(formulas(["y<sub>2</sub> + V<sub>2</sub><sup>2</sup>/2g + z<sub>2</sub> = y<sub>1</sub> + V<sub>1</sub><sup>2</sup>/2g + z<sub>1</sub> + (S<sub>f1</sub> + S<sub>f2</sub>)/2 · Δx",
                         "S<sub>f</sub> = (n · V / R<sup>2/3</sup>)<sup>2</sup>; &nbsp;Fr = V / √(g · y); &nbsp;llenado = y / h; &nbsp;BL = techo − NA"]))
    pr = [[PF.cell(r, c).value for c in range(1, 15)] for r in range(5, 80)]
    pr = [r for r in pr if isinstance(r[0], (int, float))]
    out.append(perfil_svg(pr))
    out.append('<div class="ley"><span><i style="border-color:#5b6670"></i>Cota de fondo</span><span><i style="border-color:#2b8cbf"></i>Nivel de agua</span>'
               '<span><i style="border-color:#9aa6ad;border-top-style:dashed"></i>Techo disponible (cara inferior de la losa)</span></div>')
    rows = [["%.2f" % r[0], "%.3f" % r[1], "%.3f" % r[2], "%.3f" % r[3], "%.3f" % r[4], "%.3f" % r[5], "%.3f" % r[6], "%.3f" % r[7],
             "%.3f" % r[8], "%.3f" % r[9], "%.3f" % r[10], "%.3f" % r[11], r[12], tilde(r[13])] for r in pr]
    out.append(tabla(["Prog. (m)", "Cota fondo", "Q (m³/s)", "y<sub>c</sub> (m)", "y (m)", "Nivel agua", "V (m/s)", "Fr", "Techo",
                      "h (m)", "y/h", "BL (m)", "Verif.", "Tramo"], rows, cls="perf").replace("&lt;sub&gt;", "<sub>").replace("&lt;/sub&gt;", "</sub>"))
    out.append('<div class="final"><h3>Resumen del perfil</h3>%s</div>' % tabla(
        ["Resultado", "Valor"], [[tilde(v(PF, "A%d" % r)), ("%.3f" % v(PF, "B%d" % r)) if r < 84 else "%d" % v(PF, "B84")] for r in (82, 83, 84)],
        anchos=["70%", "30%"], alinear={1: "r"}))
    # ---------------------------------------------------------- 5. estructural
    out.append('<h2 class="salto"><span class="n">5.</span>Verificación estructural</h2>')
    out.append("<p>%s</p>" % esc(v(ES, "A1").split(" (", 1)[1].rstrip(")").replace("RNE E.060, cargas E.020 / rueda AASHTO LRFD",
                                                                                     "Concreto armado según RNE E.060; cargas según RNE E.020 y rueda de diseño AASHTO LRFD.")))
    out.append(formulas(["w<sub>u</sub> = 1.4 D + 1.7 L; &nbsp;M<sub>u</sub> = w<sub>u</sub> L<sup>2</sup>/8 &nbsp;(losa simplemente apoyada, conservador)",
                         "M<sub>rueda</sub> = P (1 + IM) (L/4 − c/8) / E; &nbsp;a = A<sub>s</sub> f<sub>y</sub> / (0.85 f'<sub>c</sub> b); &nbsp;φM<sub>n</sub> = 0.9 A<sub>s</sub> f<sub>y</sub> (d − a/2) ≥ M<sub>u</sub>",
                         "A<sub>s,mín</sub> = 0.0018 · b · e &nbsp;(E.060 9.7.2); &nbsp;φV<sub>c</sub> ≥ V<sub>u</sub>"]))
    bloques, act = [], None
    for r in range(5, 134):
        a, b, c, d, e = (ES.cell(r, k).value for k in range(1, 6))
        if a is None: continue
        if b is None and c is None and d is None and e is None:
            t = tilde(a)
            if act and ("(cont.)" in t or t.lower().endswith("- flexión")):
                act[1].append(("__grupo__", "Flexión")); continue
            act = [t, []]; bloques.append(act); continue
        act[1].append([tilde(a), b, c or "", tilde(d or ""), e or ""])
    for t, rows in bloques:
        cab = "Parámetros generales" if t.upper().startswith("PAR") else t
        out.append('<div class="bloque"><h3>%s</h3>%s</div>' % (esc(cab), tabla(["Elemento / parámetro", "Valor", "Und", "Fórmula / criterio", "Resultado"], rows,
                                                                            anchos=["34%", "11%", "9%", "34%", "12%"], alinear={1: "r"})))
    # ---------------------------------------------------------- resumen final y firma
    filas_res = []
    for t, rows in bloques[1:]:
        ok = [r for r in rows if not isinstance(r, tuple) and isinstance(r[4], str) and r[4]]
        if ok: filas_res.append([t, "%d verificaci%s" % (len(ok), "ón" if len(ok) == 1 else "ones"), "CUMPLE" if all(r[4].upper() == "CUMPLE" for r in ok) else "NO CUMPLE"])
    out.append('<div class="final salto"><h3>Cuadro conjunto de verificaciones</h3>%s</div>' % tabla(["Elemento", "Comprobaciones", "Resultado"], filas_res, anchos=["68%", "18%", "14%"]))
    out.append('<div class="final"><h3>Diseño adoptado</h3><p>%s</p></div>' % esc(v(M, "B9").split(" Llenado maximo")[0]))
    out.append('<p class="ref">Referencia: RNE CE.040 Drenaje Pluvial (RM N.° 126-2021-VIVIENDA); RNE E.020 Cargas; RNE E.060 Concreto Armado; '
               'AASHTO LRFD para la carga de rueda en cruces vehiculares. Dimensiones sujetas a la aprobación del proyectista.</p>')
    out.append('<div class="firma">Profesional responsable: ______________________________ · CIP ____________ · Firma: ______________________</div>')
    return "<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Memoria de cálculo - colector pluvial CAR Mujeres</title><style>%s</style></head><body>%s</body></html>" % (CSS, "".join(out))


PDF_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await p.pdf({ path: process.argv[3], format: 'A4', printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
    headerTemplate: '<div style="font-size:7px;width:100%;padding:0 14mm;color:#7a858d;font-family:Liberation Sans,Arial;display:flex;justify-content:space-between"><span>Memoria de cálculo · Colector pluvial frontal · CAR Mujeres (CUI 2717013)</span><span>Drenaje pluvial · RNE CE.040</span></div>',
    footerTemplate: '<div style="font-size:7px;width:100%;padding:0 14mm;color:#7a858d;font-family:Liberation Sans,Arial;display:flex;justify-content:space-between"><span>Colector pluvial frontal · tramo CAR Mujeres 0+000 a 0+139.08</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>' });
  await b.close();
})();
"""


if __name__ == "__main__":
    doc = construir()
    tmp = os.path.join(RAIZ, "entregables_mujeres", "_tmp"); os.makedirs(tmp, exist_ok=True)
    fh = os.path.join(tmp, "memoria_calculo_colector.html"); open(fh, "w", encoding="utf-8").write(doc)
    fj = os.path.join(tmp, "pdf.js"); open(fj, "w").write(PDF_JS)
    subprocess.run(["node", fj, fh, SALIDA], check=True, cwd=RAIZ)
    print(os.path.relpath(SALIDA, RAIZ))
