"""Hogar de Refugio Temporal Mujeres Violentadas (CUI 2675514): memoria de calculo del colector pluvial frontal en PDF,
con el mismo estilo visual de la memoria del CAR Mujeres (herramientas/mujeres/memoria_pdf_m.py).

Fuente: entregables/MEMORIA_CALCULO_COLECTOR_HOGAR_REFUGIO.xlsx (hojas MEMORIA, DATOS, CAUDALES, CUNETAS, EMPALME,
PERFIL_FLUJO, ESTRUCTURAL, CUMPLIMIENTO). El libro se recalcula con LibreOffice y se copian sus valores sin cambiarlos;
solo se da formato (tildes, superindices) y se reemplazan las referencias a celdas por referencias a las secciones.
Uso: python3 herramientas/memoria_pdf_refugio.py
"""
import os, re, sys, shutil, subprocess

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(AQUI, "mujeres"))
import memoria_pdf_m as MM  # noqa: E402  (mismas piezas de HTML y CSS)
from memoria_pdf_m import tabla, formulas, fmt, CSS  # noqa: E402

XLSX = os.path.join(RAIZ, "entregables", "MEMORIA_CALCULO_COLECTOR_HOGAR_REFUGIO.xlsx")
SALIDA = os.path.join(RAIZ, "entregables", "MEMORIA_CALCULO_COLECTOR_HOGAR_REFUGIO.pdf")
PROYECTO = ("Hogar de Refugio Temporal Mujeres Violentadas, con CUI N.° 2675514 · SAN MARTÍN - SAN MARTÍN - MORALES · octubre 2026")

MM.TILDES.update({
    "caida": "caída", "Caida": "Caída", "CAIDA": "CAÍDA", "Energia": "Energía", "Porton": "Portón", "porton": "portón",
    "Colchon": "Colchón", "colchon": "colchón", "disipacion": "disipación", "Disipacion": "Disipación", "regimen": "régimen",
    "Regimen": "Régimen", "subcritico": "subcrítico", "Subcritico": "Subcrítico", "hidraulico": "hidráulico", "Hidraulico": "Hidráulico",
    "limite": "límite", "Ubicacion": "Ubicación", "ubicacion": "ubicación", "Separacion": "Separación", "separacion": "separación",
    "dilatacion": "dilatación", "Practica": "Práctica", "georreferencio": "georreferenció", "version": "versión", "Biseccion": "Bisección",
    "iteracion": "iteración", "maxima": "máxima", "Maxima": "Máxima", "Minima": "Mínima", "Minimo": "Mínimo", "monolitico": "monolítico",
    "monoliticamente": "monolíticamente", "Seccion": "Sección", "SECCION": "SECCIÓN", "raiz": "raíz", "vehiculo": "vehículo",
    "segun": "según", "fisica": "física", "expansion": "expansión", "rigido": "rígido", "Proteccion": "Protección", "Tecnico": "Técnico",
    "arquitectonico": "arquitectónico", "perimetrica": "perimétrica", "aproximacion": "aproximación", "Disenos": "Diseños",
    "ENERGIA": "ENERGÍA", "VELOCIDADES": "VELOCIDADES", "CRUCE": "CRUCE", "MONOLITICO": "MONOLÍTICO", "CONSTRUCCION": "CONSTRUCCIÓN",
    "Ingenieria": "Ingeniería", "Maximo": "Máximo", "metodos": "métodos", "teorico": "teórico", "dias": "días", "Prolongacion": "Prolongación",
    "Jr": "Jr", "proposito": "propósito", "Cuantia": "Cuantía", "ultimo": "último", "Caudal": "Caudal", "Linea": "Línea",
    "tipica": "típica", "electricos": "eléctricos", "Electrica": "Eléctrica", "Transicion": "Transición", "transicion": "transición",
    "conexion": "conexión", "Conexion": "Conexión", "Recepcion": "Recepción", "recepcion": "recepción", "estan": "están",
    "debera": "deberá", "seran": "serán", "sera": "será", "podra": "podrá", "Numero": "Número", "Analisis": "Análisis",
})
MM.FRASES.update({
    "y1 resuelto en Python (y1 + (Q/(b y1))^2/2g = E1); verificar: B14 + B15^2/19.62 = B13": "y1 resuelto por iteración de y1 + (Q/(b y1))^2/2g = E1",
    "debe ser igual a E1 (B13)": "debe ser igual a E1", ", 8 iteraciones (columnas P a W)": ", 8 iteraciones",
    "Ver cuadro resumen y la hoja CUMPLIMIENTO (requisito, norma, criterio, valor y resultado).":
        "Ver «Resultados de la verificación» y el cuadro de cumplimiento normativo de la sección 7 (requisito, norma, criterio, valor y resultado).",
    "(hoja PERFIL_FLUJO)": "(sección 5)", "hoja PERFIL_FLUJO, ultima fila": "perfil de flujo, sección 5", "hoja PERFIL_FLUJO": "perfil de flujo, sección 5",
    "(hoja ESTRUCTURAL)": "(sección 6)", "(hoja CUMPLIMIENTO)": "(sección 7)", "(ver fila del cuadro)": "(ver el cuadro de la sección 7)",
    ", dato no validado": " (dato de su expediente)", "hoja C. P diseno": "precipitación de diseño",
    "^2": "²", "^3": "³", "Q2/(g b2)": "Q²/(g b²)", "wL2/8": "wL²/8", "wu L2/8": "wu L²/8", "p H2/20": "p H²/20", "q H2/12": "q H²/12",
    "y como quedan": "y cómo quedan", "Y COMO QUEDAN": "Y CÓMO QUEDAN", "fMn": "φMn", "fVc": "φVc", "phi Mn": "φMn", "phi Vc": "φVc",
    "phi = ": "φ = ", "tau = gamma R S": "τ = γ R S", "Ko gamma H": "Ko γ H", "tau ≥": "τ ≥",
})
MM.TILDES.update({"presion": "presión", "variacion": "variación", "posicion": "posición", "reaccion": "reacción", "traccion": "tracción",
                  "hidrologico": "hidrológico", "Hidrologico": "Hidrológico"})
MM._RX = re.compile(r"\b(" + "|".join(sorted(map(re.escape, MM.TILDES), key=len, reverse=True)) + r")\b")
_tilde0 = MM.tilde
_UN = re.compile(r"\b(c?m)([23])\b")


def tilde(t):
    t = _tilde0(t)
    return _UN.sub(lambda m: m.group(1) + ("²" if m.group(2) == "2" else "³"), t) if isinstance(t, str) else t


MM.tilde = tilde
esc = MM.esc


def perfil_svg(pts):
    """pts: (progresiva, cota de fondo, nivel de agua, techo disponible) ordenados por progresiva."""
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
                 % (ml, W - mr, Y(z), Y(z), ml - 6, Y(z) + 3, z)); z = round(z + 0.2, 1)
    for x in range(int(-(-min(xs) // 10)) * 10, int(max(xs) + 0.5) + 1, 10):
        g.append('<line x1="%.1f" x2="%.1f" y1="%d" y2="%d" class="gr"/><text x="%.1f" y="%d" class="ax" text-anchor="middle">%s</text>'
                 % (X(x), X(x), mt, H - mb, X(x), H - mb + 14, "0+%03d" % x))
    return ('<svg viewBox="0 0 %d %d" class="perfil" xmlns="http://www.w3.org/2000/svg">%s'
            '<polygon points="%s" class="aguaf"/><polyline points="%s" class="techo"/><polyline points="%s" class="agua"/>'
            '<polyline points="%s" class="fondo"/><text x="%d" y="%d" class="ax" text-anchor="middle">Progresiva (m)</text>'
            '<text x="12" y="%d" class="ax" transform="rotate(-90 12 %d)" text-anchor="middle">Cota (msnm)</text></svg>'
            % (W, H, "".join(g), agua, pol(3), pol(2), pol(1), (ml + W - mr) // 2, H - 4, H // 2, H // 2))


def und(u):
    return tilde(u) if isinstance(u, str) else (u or "")


def tabla_param(ws, r0, r1, cab=("Parámetro", "Valor", "Und", "Fuente / criterio", "Símbolo"), ncol=5, anchos=None):
    """Tabla parametro / valor / und / criterio con filas de grupo (solo columna A) y notas largas."""
    rows, notas = [], []
    for r in range(r0, r1 + 1):
        vals = [ws.cell(r, c).value for c in range(1, ncol + 1)]
        if vals[0] is None: continue
        if all(x is None for x in vals[1:]):
            if len(vals[0]) > 90: notas.append(vals[0]); continue
            rows.append(("__grupo__", vals[0])); continue
        fila = [tilde(vals[0]), vals[1], und(vals[2])] + [tilde(x) if isinstance(x, str) else (x if x is not None else "") for x in vals[3:]]
        rows.append(fila)
    t = tabla(list(cab), rows, anchos=anchos, alinear={1: "r"})
    return t + "".join('<p class="small">%s</p>' % esc(n) for n in notas)


def construir():
    MM.XLSX = XLSX
    wb = MM.libro()
    M, DA, CA, CU, EM, PF, ES, CP = (wb[k] for k in ("MEMORIA", "DATOS", "CAUDALES", "CUNETAS", "EMPALME", "PERFIL_FLUJO", "ESTRUCTURAL", "CUMPLIMIENTO"))
    v = lambda ws, ref: ws[ref].value
    out = []
    # ---------------------------------------------------------- 0. encabezado y memoria descriptiva
    out.append('<h1>Memoria de cálculo del colector pluvial frontal</h1><div class="proy">%s</div>' % esc(PROYECTO))
    out.append('<div class="meta"><b>TRAMO HOGAR DE REFUGIO</b> · 0+000 a 0+073.39 · recibe el CAR Varones (CUI 2705619) y entrega al '
               'registro R-01 del CAR Mujeres (CUI 2717013) · RNE CE.040</div>')
    out.append('<div class="kpis">%s</div>' % "".join(
        '<div class="kpi"><div class="v">%s</div><div class="l">%s</div></div>' % (a, b) for a, b in (
            ("%.1f L/s" % v(M, "B11"), "Caudal de diseño del tramo"), ("%.3f" % v(M, "B16"), "Llenado máximo y/h (admisible 0.85)"),
            ("%.3f m" % v(M, "B17"), "Borde libre mínimo bajo losa (mín. 0.05)"), ("%.3f" % v(M, "B18"), "Froude máximo (régimen subcrítico)"))))
    out.append("<h2>Datos y metodología</h2>")
    for r in range(4, 10):
        out.append("<p><b>%s.</b> %s</p>" % (esc(v(M, "A%d" % r).split(". ", 1)[1].capitalize()), esc(v(M, "B%d" % r))))
    res = []
    for r in range(11, 25):
        b = v(M, "B%d" % r)
        if isinstance(b, float):
            b = "%.1f" % b if b > 100 else ("%.3f" % b)
        res.append([tilde(v(M, "A%d" % r)), b if isinstance(b, str) else fmt(b)])
    out.append('<div class="final"><h3>Resultados de la verificación</h3>%s</div>' % tabla(["Resultado", "Valor"], res, anchos=["68%", "32%"], alinear={1: "r"}))
    out.append('<p class="ref"><b>Notas.</b></p>' + "".join('<p class="ref">%s</p>' % esc(v(M, "B%d" % r)) for r in range(27, 30)))
    # ---------------------------------------------------------- 1. datos de diseno
    out.append('<h2><span class="n">1.</span>Datos de diseño</h2>')
    out.append(formulas(["b = ln(P<sub>20</sub> / P<sub>10</sub>) / ln 2", "I = P<sub>10</sub> · (t<sub>c</sub> / 10)<sup>b</sup> / (t<sub>c</sub> / 60) &nbsp;[mm/h]"]))
    out.append(tabla_param(DA, 5, 50, anchos=["33%", "11%", "8%", "40%", "8%"]))
    # ---------------------------------------------------------- 2. caudales
    out.append('<h2><span class="n">2.</span>Caudales de diseño: método racional</h2>')
    out.append(formulas(["Q = C · I · A · FS / 3 600 000 &nbsp;[m<sup>3</sup>/s] &nbsp;(I en mm/h, A en m<sup>2</sup>); &nbsp;C ponderado = Σ(C·A) / ΣA"]))
    rows = []
    for a, b, c, d, e, f, g, h in MM.filas(CA, 5, 7, 8):
        rows.append([tilde(a), b, c, "%.3f" % d, "%.2f" % e if e else "", "%.1f" % f, tilde(g or ""), tilde(h or "")])
    out.append(tabla(["Proyecto", "Área (m²)", "C × A (m²)", "C pond.", "I (mm/h)", "Q (L/s)", "Ingresa al colector en", "Fuente"], rows,
                     anchos=["21%", "9%", "10%", "7%", "8%", "8%", "17%", "20%"], alinear={1: "r", 2: "r", 3: "r", 4: "r", 5: "r"}))
    out.append("<h3>%s</h3>" % esc(v(CA, "A9")))
    out.append(tabla(["Aporte", "Caudal", "Und"], [[tilde(a), "%.1f" % b if b > 1 else "%.4f" % b, und(c)] for a, b, c in MM.filas(CA, 10, 13, 3)],
                     anchos=["60%", "22%", "18%"], alinear={1: "r"}))
    out.append("<h3>%s</h3>" % esc(v(CA, "A15")))
    rows = [[tilde(a), "0+%06.2f" % b, "%.1f" % c, "%.1f" % d] for a, b, c, d in MM.filas(CA, 17, 23, 4)]
    out.append(tabla(["Punto", "Progresiva", "Aporte (L/s)", "Q acumulado (L/s)"], rows, anchos=["46%", "16%", "19%", "19%"], alinear={1: "r", 2: "r", 3: "r"}))
    out.append('<p class="small">%s</p>' % esc(v(CA, "A25")))
    # ---------------------------------------------------------- 3. cunetas
    out.append('<h2><span class="n">3.</span>Cunetas de arquitectura que llegan al colector</h2>')
    out.append(formulas(["NCF<sub>muro</sub> = NCF<sub>cerco</sub> − 0.005 · prolongación; &nbsp;caída libre = NCF<sub>muro</sub> − NA<sub>colector</sub> &gt; 0"]))
    rows = []
    for r in MM.filas(CU, 5, 10, 12):
        rows.append([tilde(r[0]), r[1], "%.2f" % r[2], "%.2f" % r[3], "%.3f" % r[4], "%.3f" % r[5], "%.2f" % r[6], "%.2f" % r[7],
                     "%.3f" % r[8], "%.3f" % r[9], "%.3f" % r[10], tilde(r[11])])
    out.append(tabla(["Cuneta", "Perfil", "Prog. (m)", "Long. (m)", "NCT", "NCF cerco", "H cerco (m)", "Prolong. (m)", "NCF muro",
                      "NA colector", "Caída libre (m)", "Verificación"], rows, cls="perf cun"))
    out.append('<p class="small">%s</p>' % esc(v(CU, "A12")))
    # ---------------------------------------------------------- 4. cajas
    out.append('<h2><span class="n">4.</span>Caja de llegada (0+000) y caja de caída en la entrega al CAR Mujeres</h2>')
    out.append(formulas(["y<sub>c</sub> = (Q<sup>2</sup> / (g · b<sup>2</sup>))<sup>1/3</sup>; &nbsp;E<sub>1</sub> = caída + 1.5 y<sub>c</sub>; &nbsp;"
                         "y<sub>1</sub> + (Q / (b · y<sub>1</sub>))<sup>2</sup> / 2g = E<sub>1</sub>",
                         "F<sub>1</sub> = V<sub>1</sub> / √(g · y<sub>1</sub>); &nbsp;y<sub>2</sub> = y<sub>1</sub>/2 · (√(1 + 8 F<sub>1</sub><sup>2</sup>) − 1); "
                         "&nbsp;resalto ahogado si y<sub>2</sub> &lt; tirante disponible en la poza"]))
    for r0, r1 in ((5, 23), (25, 33)):
        out.append('<div class="bloque"><h3>%s</h3>%s</div>' % (esc(v(EM, "A%d" % r0)).capitalize() if False else esc(v(EM, "A%d" % r0)),
                                                                 tabla_param(EM, r0 + 1, r1, cab=("Parámetro", "Valor", "Und", "Fórmula / criterio"), ncol=4,
                                                                             anchos=["36%", "16%", "8%", "40%"])))
    # ---------------------------------------------------------- 5. perfil de flujo
    out.append('<h2><span class="n">5.</span>Perfil de flujo gradualmente variado: método del paso estándar</h2>')
    out.append("<p>Cálculo desde el brink de la caída (0+069.89, tirante crítico) hacia aguas arriba. El tirante de cada estación se "
               "resuelve por bisección en 30 iteraciones.</p>")
    out.append(formulas(["y<sub>2</sub> + V<sub>2</sub><sup>2</sup>/2g + z<sub>2</sub> = y<sub>1</sub> + V<sub>1</sub><sup>2</sup>/2g + z<sub>1</sub> + (S<sub>f1</sub> + S<sub>f2</sub>)/2 · Δx",
                         "S<sub>f</sub> = (n · V / R<sup>2/3</sup>)<sup>2</sup>; &nbsp;Fr = V / √(g · y); &nbsp;llenado = y / h; &nbsp;BL = techo − NA"]))
    pr = [[PF.cell(r, c).value for c in range(1, 16)] for r in range(6, 91)]
    pr = [r for r in pr if isinstance(r[0], (int, float))]
    out.append(perfil_svg(sorted([(r[0], r[1], r[6], r[9]) for r in pr], key=lambda p: (p[0], p[2]))))
    out.append('<div class="ley"><span><i style="border-color:#5b6670"></i>Cota de fondo</span><span><i style="border-color:#2b8cbf"></i>Nivel de agua</span>'
               '<span><i style="border-color:#9aa6ad;border-top-style:dashed"></i>Techo disponible (cara inferior de la losa)</span></div>')
    rows = [["%.2f" % r[0], "%.3f" % r[1], "%.3f" % r[2], "%.3f" % r[4], "%.3f" % r[5], "%.3f" % r[6], "%.3f" % r[7], "%.3f" % r[8],
             "%.3f" % r[9], "%.3f" % r[10], "%.3f" % r[11], "%.3f" % r[12], r[13], tilde(r[14])] for r in pr]
    out.append(tabla(["Prog. (m)", "Cota fondo", "Q (m³/s)", "y<sub>c</sub> (m)", "y (m)", "Nivel agua", "V (m/s)", "Fr", "Techo",
                      "h (m)", "y/h", "BL (m)", "Verif.", "Zona"], rows, cls="perf").replace("&lt;sub&gt;", "<sub>").replace("&lt;/sub&gt;", "</sub>"))
    out.append('<div class="final"><h3>Resumen del perfil</h3>%s</div>' % tabla(
        ["Resultado", "Valor"], [[tilde(v(PF, "A%d" % r)), ("%d" % v(PF, "B%d" % r)) if r == 96 else "%.3f" % v(PF, "B%d" % r)] for r in range(93, 98)],
        anchos=["70%", "30%"], alinear={1: "r"}))
    out.append('<div class="bloque"><h3>%s</h3>' % esc(v(PF, "A99")))
    out.append('<p class="small">%s</p>' % esc(v(PF, "A100")))
    rows = []
    for r in MM.filas(PF, 102, 108, 11):
        rows.append([tilde(r[0])] + ["%.4f" % r[1], "%.3f" % r[2], "%.3f" % r[3], "%.3f" % r[4], "%.3f" % r[5], "%.2f" % r[6], "%.3f" % r[7]] +
                    [tilde(x) for x in r[8:11]])
    out.append(tabla(["Caso", "Q (m³/s)", "y<sub>n</sub> (m)", "V (m/s)", "R (m)", "τ (kg/m²)", "τ (Pa)", "Fr", "V ≥ 0.90 m/s", "τ ≥ 0.15 kg/m²", "V ≤ 3.0 m/s"],
                     rows, cls="perf").replace("&lt;sub&gt;", "<sub>").replace("&lt;/sub&gt;", "</sub>"))
    out.append(tabla(["Resultado", "Valor"], [[tilde(v(PF, "A%d" % r)), "%.3f" % v(PF, "B%d" % r) if isinstance(v(PF, "B%d" % r), float) else tilde(v(PF, "B%d" % r))]
                                             for r in (110, 111, 112)], anchos=["70%", "30%"], alinear={1: "r"}))
    out.append('<p class="small">%s</p></div>' % esc(v(PF, "A113")))
    # ---------------------------------------------------------- 6. estructural
    out.append('<h2><span class="n">6.</span>Verificación estructural</h2>')
    out.append("<p>Concreto armado según RNE E.060; cargas según RNE E.020 y rueda de diseño AASHTO LRFD HL-93.</p>")
    out.append(formulas(["w<sub>u</sub> = 1.4 D + 1.7 L; &nbsp;M<sub>u</sub> = w<sub>u</sub> L<sup>2</sup>/8 &nbsp;(losa simplemente apoyada, conservador)",
                         "M<sub>rueda</sub> = P (1 + IM) (L/4 − c/8) / E; &nbsp;a = A<sub>s</sub> f<sub>y</sub> / (0.85 f'<sub>c</sub> b); &nbsp;φM<sub>n</sub> = 0.9 A<sub>s</sub> f<sub>y</sub> (d − a/2) ≥ M<sub>u</sub>",
                         "Muro (marco cerrado, extremos empotrados): M = p H<sup>2</sup>/20 + q H<sup>2</sup>/12; &nbsp;A<sub>s,mín</sub> = 0.0018 · b · e &nbsp;(E.060 9.7.2); &nbsp;φV<sub>c</sub> ≥ V<sub>u</sub>"]))
    bloques, act = [], None
    for r in range(5, 102):
        a, b, c, d, e = (ES.cell(r, k).value for k in range(1, 6))
        if a is None: continue
        if b is None and c is None and d is None and e is None:
            act = [tilde(a), []]; bloques.append(act); continue
        act[1].append([tilde(a), b, und(c), tilde(d or ""), tilde(e or "")])
    for t, rows in bloques:
        cab = "Parámetros generales" if t.upper().startswith("PAR") else t
        out.append('<div class="bloque"><h3>%s</h3>%s</div>' % (esc(cab), tabla(["Elemento / parámetro", "Valor", "Und", "Fórmula / criterio", "Resultado"], rows,
                                                                            anchos=["32%", "11%", "8%", "35%", "14%"], alinear={1: "r"})))
    out.append('<p class="small">%s</p>' % esc(v(ES, "A103")))
    filas_res = []
    for t, rows in bloques[1:]:
        ok = [r for r in rows if isinstance(r[4], str) and r[4]]
        if ok:
            filas_res.append([t, "%d verificaci%s" % (len(ok), "ón" if len(ok) == 1 else "ones"),
                              "CUMPLE" if all(r[4].upper().startswith("CUMPLE") for r in ok) else "NO CUMPLE"])
    out.append('<div class="final"><h3>Cuadro conjunto de verificaciones estructurales</h3>%s</div>' % tabla(["Elemento", "Comprobaciones", "Resultado"], filas_res,
                                                                                                         anchos=["68%", "18%", "14%"]))
    # ---------------------------------------------------------- 7. cumplimiento
    out.append('<h2><span class="n">7.</span>Cuadro de cumplimiento normativo y condiciones de compatibilidad</h2>')
    rows = []
    for r in range(5, 45):
        a, b, c, d, e = (CP.cell(r, k).value for k in range(1, 6))
        if a is None: continue
        if b is None and c is None: rows.append(("__grupo__", a)); continue
        if isinstance(d, float): d = "%.1f" % d if d > 100 else "%.3f" % d
        if isinstance(d, str) and d.upper().startswith(("CUMPLE", "RESALTO")) and d == e: d = "—"
        rows.append([tilde(a), tilde(b), tilde(c), tilde(d) if isinstance(d, str) else fmt(d), tilde(e)])
    out.append(tabla(["Requisito", "Norma / referencia", "Criterio", "Valor del diseño", "Resultado"], rows,
                     anchos=["24%", "21%", "27%", "12%", "16%"], alinear={3: "r"}).replace("<td class=\"\">CUMPLE", "<td class=\"\">CUMPLE"))
    out.append('<p><b>%s: %d</b></p>' % (esc(v(CP, "A46")), v(CP, "B46")))
    out.append('<div class="final"><h3>%s</h3>%s</div>' % (esc(v(CP, "A48").capitalize()), "".join("<p>%s</p>" % esc(v(CP, "A%d" % r)) for r in range(49, 54))))
    # ---------------------------------------------------------- diseno adoptado y firma
    out.append('<div class="final"><h3>Diseño adoptado</h3><p>%s</p><p>%s</p></div>' % (esc(v(M, "B7")), esc(v(M, "B8"))))
    out.append('<p class="ref">Referencia: RNE CE.040 Drenaje Pluvial (RM N.° 126-2021-VIVIENDA); RNE E.020 Cargas; RNE E.060 Concreto Armado; '
               'RNE E.050 Suelos y Cimentaciones; AASHTO LRFD para la carga de rueda en el cruce de camiones; Chow, Hidráulica de canales abiertos. '
               'Dimensiones sujetas a la aprobación del proyectista.</p>')
    out.append('<div class="firma">Profesional responsable: ______________________________ · CIP ____________ · Firma: ______________________</div>')
    return ("<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Memoria de cálculo - colector pluvial Hogar de Refugio</title>"
            "<style>%s .badge{white-space:nowrap} table.cun td:first-child, table.cun th:first-child{text-align:left}</style></head><body>%s</body></html>" % (CSS, "".join(out)))


PDF_JS = MM.PDF_JS.replace("CAR Mujeres (CUI 2717013)", "Hogar de Refugio Temporal (CUI 2675514)").replace(
    "tramo CAR Mujeres 0+000 a 0+139.08", "tramo Hogar de Refugio 0+000 a 0+073.39")


if __name__ == "__main__":
    doc = construir()
    tmp = os.path.join(RAIZ, "entregables", "_tmp", "pdf_refugio"); os.makedirs(tmp, exist_ok=True)
    fh = os.path.join(tmp, "memoria_calculo_colector.html"); open(fh, "w", encoding="utf-8").write(doc)
    fj = os.path.join(tmp, "pdf.js"); open(fj, "w").write(PDF_JS)
    subprocess.run(["node", fj, fh, SALIDA], check=True, cwd=RAIZ)
    shutil.rmtree(tmp, ignore_errors=True)
    print(os.path.relpath(SALIDA, RAIZ))
