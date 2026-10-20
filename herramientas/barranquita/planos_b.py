"""Planos del planteamiento preliminar de cunetas - I.E. N.° 0590, Barranquita (Lamas - San Martin).

DC-00 indice; DC-01 planta general de cunetas (1/250, coordenadas UTM reales); DC-02 cuadro de tramos y secciones tipicas
(1/5); DC-03... perfiles longitudinales (1/100, horizontal = vertical).
Lee entregables_barranquita/_calc/diseno.json (diseno_b.py) y la base del sitio (insumos/barranquita/base_sitio.pkl).
Uso: python3 herramientas/barranquita/planos_b.py
"""
import os, sys, json, math
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI); sys.path.insert(0, os.path.dirname(AQUI))
import dxf_base as B
import dxf_layouts as LY
from ezdxf.enums import TextEntityAlignment as TA
import terreno_b as T
import diseno_b as DS

SAL = os.path.join(RAIZ, "entregables_barranquita", "PLANTEAMIENTO_CUNETAS_IE0590_BARRANQUITA.dxf")
CALC = os.path.join(RAIZ, "entregables_barranquita", "_calc")

B.PROYECTO = ("MEJORAMIENTO Y AMPLIACION DEL SERVICIO DE EDUCACION PRIMARIA EN LA I.E. N.° 0590, DISTRITO DE BARRANQUITA,",
              "PROVINCIA DE LAMAS, DEPARTAMENTO DE SAN MARTIN - C.I. N.° 468901")
B.UBICACION = "UBICACION: I.E. N.° 0590 - BARRANQUITA - LAMAS - SAN MARTIN"
B.ESPECIALIDAD = "ESPECIALIDAD: DRENAJE PLUVIAL - CUNETAS (PLANTEAMIENTO PRELIMINAR)"
B.ENTIDAD = "ENTIDAD:"
B.ELABORADO = ""
B.FECHA = "OCT. 2026"

DIR_DESCARGA = {"D2": (-0.7071, 0.7071)}      # D2 sale de lado, hacia la hondonada natural (no sigue por la cuneta)
COL_SIS = {1: 5, 2: 6, 3: 94, 4: 30}
NOM_SIS = {1: "SISTEMA 1 - OESTE (descarga D1)", 2: "SISTEMA 2 - FRENTE SUR (descarga D3)", 3: "SISTEMA 3 - NOR-ESTE (descarga D2)",
           4: "SISTEMA 4 - INGRESO SUR-ESTE (descarga D4)"}
CAPAS_EXTRA = [("CURVAS", 33, "CONTINUOUS"), ("CURVAS-TXT", 33, "CONTINUOUS"), ("ARQ-TECHO", 8, "CONTINUOUS"), ("ARQ-VEREDA", 9, "CONTINUOUS"),
               ("CUNETA-S1", 5, "CONTINUOUS"), ("CUNETA-S2", 6, "CONTINUOUS"), ("CUNETA-S3", 94, "CONTINUOUS"), ("CUNETA-S4", 30, "CONTINUOUS"),
               ("CUNETA-REJILLA", 254, "CONTINUOUS"), ("CUNETA-REJ-LIN", 8, "CONTINUOUS"), ("CUNETA-TAPADO", 252, "CONTINUOUS"),
               ("FLUJO-C", 7, "CONTINUOUS"), ("NUDOS", 7, "CONTINUOUS"), ("DESCARGA", 1, "CONTINUOUS"), ("MURO-CONT", 6, "CONTINUOUS")]
RGB_EXTRA = {"CURVAS": (176, 136, 96), "CURVAS-TXT": (150, 110, 70), "CUNETA-REJILLA": (232, 232, 232), "CUNETA-TAPADO": (160, 160, 160)}


def preparar(doc):
    for n, c, lt in CAPAS_EXTRA:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt)
            if n in RGB_EXTRA: ly.rgb = RGB_EXTRA[n]
    for n, rgb in RGB_EXTRA.items(): B.COLOR_RGB[n] = rgb
    for n, g in (("CUNETA-S1", 35), ("CUNETA-S2", 35), ("CUNETA-S3", 35), ("CUNETA-S4", 35), ("CURVAS", 13), ("ARQ-TECHO", 13),
                 ("ARQ-VEREDA", 9), ("DESCARGA", 35)):
        doc.layers.get(n).dxf.lineweight = g


# ----------------------------------------------------------------------------- utilidades
def puntos_ramal(R, nudos):
    return [tuple(R["nudos"][n]) for n in nudos]


def a_lo_largo(pts, s):
    """Punto y direccion a la distancia s del inicio de la polilinea pts."""
    acc = 0.0
    for i in range(len(pts) - 1):
        L = math.dist(pts[i], pts[i + 1])
        if acc + L >= s or i == len(pts) - 2:
            t = 0 if L == 0 else min(1, max(0, (s - acc) / L))
            ux, uy = (pts[i + 1][0] - pts[i][0]) / L, (pts[i + 1][1] - pts[i][1]) / L
            return (pts[i][0] + t * (pts[i + 1][0] - pts[i][0]), pts[i][1] + t * (pts[i + 1][1] - pts[i][1])), (ux, uy)
        acc += L


def tramo_pts(pts, s0, s1):
    out = [a_lo_largo(pts, s0)[0]]; acc = 0.0
    for i in range(len(pts) - 1):
        acc += math.dist(pts[i], pts[i + 1])
        if s0 < acc < s1: out.append(pts[i + 1])
    out.append(a_lo_largo(pts, s1)[0]); return out


class Etiquetas:
    """Coloca textos cortos junto a un punto sin pisar otros textos (8 posiciones de prueba)."""
    def __init__(self, lam): self.lam, self.cajas = lam, []

    def libre(self, c):
        return all(c[2] < o[0] or c[0] > o[2] or c[3] < o[1] or c[1] > o[3] for o in self.cajas)

    def poner(self, p, txt, hmm=1.8, capa="TEXTOS", color=None, d_mm=2.2, fijo=False):
        f = self.lam.f; h = hmm * B.K_TXT.get(capa, 1.0) * f; w = len(txt) * 0.62 * h
        cand = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        for k in range(1, 4):
            for sx, sy in cand:
                d = d_mm * f * k
                x = p[0] + sx * d - (w if sx < 0 else (w / 2 if sx == 0 else 0)); y = p[1] + sy * d - (h if sy < 0 else (h / 2 if sy == 0 else 0))
                c = (x - 0.3 * f, y - 0.3 * f, x + w + 0.3 * f, y + h + 0.3 * f)
                if self.libre(c) or fijo:
                    self.cajas.append(c); self.lam.texto((x, y), txt, hmm, capa, TA.BOTTOM_LEFT, color=color)
                    if k > 1: self.lam.linea(p, (x if sx >= 0 else x + w, y + h / 2), "LLAMADAS")
                    return
        x, y = p[0] + d_mm * f, p[1] + d_mm * f; self.cajas.append((x, y, x + w, y + h)); self.lam.texto((x, y), txt, hmm, capa, TA.BOTTOM_LEFT, color=color)


# ----------------------------------------------------------------------------- DC-01 planta general
def base_sitio(lam, G, caja):
    x0, y0, x1, y1 = caja
    def dentro(pts): return any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in pts)
    for capa_src, capa, solo_cerrada in (("0_VEREDAS", "ARQ-VEREDA", False), ("0_PROYECCIONES 1", "ARQ-TECHO", False), ("0_MUROS 1", "ARQ-BASE", False),
                                         ("MUROS-02", "ARQ-BASE", False), ("2", "CERCO", False), ("MURO DE CONTENCION", "MURO-CONT", False)):
        for pts, cl, b in G["geo"].get(capa_src, []):
            if len(pts) > 1 and dentro(pts):
                lam.poli([(p[0], p[1]) for p in pts], capa, cerrada=cl)
    # curvas de nivel (cada 0.50 m) con su cota en las de metro entero
    for z, pts in T.curvas(G):
        pts = [p for p in pts if x0 - 5 <= p[0] <= x1 + 5 and y0 - 5 <= p[1] <= y1 + 5]
        if len(pts) < 2: continue
        lam.poli(pts, "CURVAS")
        if abs(z - round(z)) < 1e-6 and len(pts) > 20:
            for k in (len(pts) // 3, 2 * len(pts) // 3):
                p, q = pts[k], pts[min(k + 2, len(pts) - 1)]
                if x0 + 3 < p[0] < x1 - 3 and y0 + 3 < p[1] < y1 - 3:
                    ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
                    if ang > 90: ang -= 180
                    if ang < -90: ang += 180
                    lam.texto(p, "%.0f" % z, 1.5, "CURVAS-TXT", TA.MIDDLE_CENTER, rot=ang)


def dc01(doc, R):
    f = 0.25
    caja = (354806.0, 9249776.0, 354988.0, 9249889.0)
    ox, oy = caja[0] - 30 * f, caja[3] - 578 * f
    lam = B.Lamina(doc, ox, oy, 250, "DC-01", "PLANTA GENERAL DE CUNETAS - PLANTEAMIENTO PRELIMINAR",
                   "TRAZO, SENTIDO DE FLUJO, REJILLAS, TRAMOS TAPADOS Y DESCARGAS - COORDENADAS UTM WGS84")
    G = T.cargar()
    base_sitio(lam, G, caja)
    ram = R["ramales"]; tap = {r["codigo"]: r["tapados"] for r in ram}
    # bandas: exterior 0.60 (color del sistema) y luego interior 0.40 (rejilla o tapado)
    for r in ram:
        pts = puntos_ramal(R, r["nudos"])
        lam.poli(pts, "CUNETA-S%d" % r["sistema"], ancho=DS.B_TOT)
    for r in ram:
        pts = puntos_ramal(R, r["nudos"])
        lam.poli(pts, "CUNETA-REJILLA", ancho=DS.B_INT)
        Ltot = r["L"]; s = 0.5
        while s < Ltot - 0.3:                                  # barras de la rejilla cada 0.50 m (simbolo)
            p, (ux, uy) = a_lo_largo(pts, s)
            lam.linea((p[0] - uy * 0.18, p[1] + ux * 0.18), (p[0] + uy * 0.18, p[1] - ux * 0.18), "CUNETA-REJ-LIN"); s += 0.5
        for s0, s1 in tap[r["codigo"]]:
            lam.poli(tramo_pts(pts, s0, s1), "CUNETA-TAPADO", ancho=DS.B_TOT)
    # flechas de flujo
    for r in ram:
        pts = puntos_ramal(R, r["nudos"])
        for i in range(len(pts) - 1):
            L = math.dist(pts[i], pts[i + 1])
            if L < 4: continue
            n = max(1, int(L // 18))
            for k in range(n):
                s_mid = (k + 0.5) * L / n; ux, uy = (pts[i + 1][0] - pts[i][0]) / L, (pts[i + 1][1] - pts[i][1]) / L
                c = (pts[i][0] + ux * s_mid, pts[i][1] + uy * s_mid)
                lam.flecha((c[0] - ux * 0.9, c[1] - uy * 0.9), (c[0] + ux * 0.9, c[1] + uy * 0.9), "FLUJO-C", tam_mm=2.6)
    # nudos y etiquetas
    E = Etiquetas(lam); nom = R["nombre"]
    for n, xy in R["nudos"].items():
        if n.startswith("D"): continue
        lam.circulo(tuple(xy), 0.30, "NUDOS")
    for r in ram:                                              # codigo del ramal junto a su tramo mas largo
        pts = puntos_ramal(R, r["nudos"]); i = max(range(len(pts) - 1), key=lambda k: math.dist(pts[k], pts[k + 1]))
        L = math.dist(pts[i], pts[i + 1]); ux, uy = (pts[i + 1][0] - pts[i][0]) / L, (pts[i + 1][1] - pts[i][1]) / L
        c = (pts[i][0] + ux * L * 0.62, pts[i][1] + uy * L * 0.62)
        E.poner((c[0] - uy * 0.8, c[1] + ux * 0.8), r["codigo"], 2.0, "TEXTOS", color=COL_SIS[r["sistema"]], d_mm=1.5)
    for n, xy in R["nudos"].items():
        if not n.startswith("D"): E.poner(tuple(xy), nom[n], 1.45, "TEXTOS", d_mm=1.6)
    # descargas (una etiqueta por descarga, en el ramal principal que llega)
    hechas = set()
    for r in sorted(ram, key=lambda r: -r["L"]):
        fin = r["nudos"][-1]
        if not fin.startswith("D") or fin in hechas: continue
        hechas.add(fin)
        pts = puntos_ramal(R, r["nudos"]); a, b = pts[-2], pts[-1]; L = math.dist(a, b); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        if fin in DIR_DESCARGA: ux, uy = DIR_DESCARGA[fin]
        q = (b[0] + ux * 4.0, b[1] + uy * 4.0)
        lam.poli([b, q], "DESCARGA", ancho=0.25); lam.flecha(b, (q[0] + ux * 0.8, q[1] + uy * 0.8), "DESCARGA", tam_mm=4.0)
        E.poner(q, fin, 3.0, "TITULOS", color=1, d_mm=1.5)
    lam.bloque("SIMB-NORTE", lam.P(785, 548))
    # leyenda, notas y cuadro de descargas (franja inferior)
    items = [("linea2", "CUNETA-S%d" % k, NOM_SIS[k]) for k in (1, 2, 3, 4)]
    items += [("relleno", "CUNETA-REJILLA", "Cuneta 0.60 m (0.40 libre) con rejilla metalica"), ("relleno", "CUNETA-TAPADO", "Tramo tapado (losa) - cruce de vereda / ingreso"),
              ("linea", "FLUJO-C", "Sentido del flujo"), ("linea2", "DESCARGA", "Descarga (D1 a D4)"), ("linea", "CURVAS", "Curva de nivel cada 0.50 m (C-TOPO)"),
              ("linea", "ARQ-TECHO", "Proyeccion de techos (a dos aguas)"), ("linea", "CERCO", "Cerco perimetrico")]
    lam.leyenda2(30, 128, items, hmm=1.7, ancho_col=118, filas_col=6)
    filas = [[k, v.split(":")[0], v.split(":", 1)[1].strip() if ":" in v else ""] for k, v in R["descargas"].items()]
    lam.tabla(30, 72, ["DESC.", "UBICACION", "RECEPTOR"], filas, [14, 70, 140], hmm=1.5, alto_mm=4.6, titulo="DESCARGAS")
    c = R["criterios"]
    lam.notas(275, 72, "CRITERIOS DEL PLANTEAMIENTO", [
        "1. Cuneta rectangular de concreto: ancho total %.2f m = muros de %.2f m + %.2f m libres; losa de fondo de 0.10 m." % (c["b_tot"], c["muro"], c["b_int"]),
        "2. Profundidad al inicio de cada ramal %.2f m; minima %.2f m donde el terreno cae mas que la cuneta; cota de fondo con S = %.1f %%." % (c["h0"], c["hmin"], 100 * c["S"]),
        "3. Rasante: NTN +184.50 en la plataforma de los bloques; terreno de las curvas C-TOPO en el resto (monticulo recortado a +184.50).",
        "4. Techos a dos aguas: cada alero descarga a la cuneta de su lado. Rejilla en tramos abiertos; losa tapa en cruces de vereda e ingresos.",
        "5. Cotas de fondo, profundidades y pendientes por tramo en la lamina DC-02 y en los perfiles DC-03 en adelante.",
        "6. Planteamiento preliminar: confirmar receptores de D3 y D4 y verificar caudales con la hidrologia del proyecto."], hmm=1.5, ancho_mm=355)
    return lam


# ----------------------------------------------------------------------------- DC-02 cuadro y secciones (1/5)
def seccion(lam, x0, y0, h, tapado, titulo):
    """Seccion transversal en (x0, y0) = borde inferior izquierdo exterior (m de modelo)."""
    e, b, ef = DS.E_MURO, DS.B_INT, 0.10
    W = 2 * e + b; H = h + ef
    if tapado:                                   # muros rebajados 0.10 para la losa tapa al nivel de la vereda
        cont = [(x0, y0), (x0 + W, y0), (x0 + W, y0 + H - 0.10), (x0 + e + b, y0 + H - 0.10), (x0 + e + b, y0 + ef), (x0 + e, y0 + ef),
                (x0 + e, y0 + H - 0.10), (x0, y0 + H - 0.10)]
    else:
        cont = [(x0, y0), (x0 + W, y0), (x0 + W, y0 + H), (x0 + e + b, y0 + H), (x0 + e + b, y0 + ef), (x0 + e, y0 + ef), (x0 + e, y0 + H), (x0, y0 + H)]
    lam.relleno(cont, "CONCRETO-ACHURADO"); lam.poli(cont, "CONCRETO", cerrada=True)
    # terreno a los lados
    for xa, xb in ((x0 - 0.30, x0), (x0 + W, x0 + W + 0.30)):
        lam.linea((xa, y0 + H), (xb, y0 + H), "TERRENO")
    if tapado:
        losa = [(x0, y0 + H - 0.10), (x0 + W, y0 + H - 0.10), (x0 + W, y0 + H), (x0, y0 + H)]
        lam.relleno(losa, "CONCRETO-ACHURADO"); lam.poli(losa, "CONCRETO", cerrada=True)
        for xb in (x0 + 0.08, x0 + W - 0.08):
            lam.bloque("ACERO-38", (xb, y0 + H - 0.05), 1.0)
        lam.linea((x0 + 0.03, y0 + H - 0.075), (x0 + W - 0.03, y0 + H - 0.075), "ACERO")
    else:
        a = 0.0254; t = 0.0048
        for xa, sg in ((x0 + e, 1), (x0 + e + b, -1)):        # angulos 1" x 1" x 3/16" del marco y rejilla de platinas
            lam.poli([(xa, y0 + H - a), (xa, y0 + H), (xa + sg * a, y0 + H)], "MARCO-METALICO")
        lam.rect(x0 + e + 0.003, y0 + H - a, x0 + e + b - 0.003, y0 + H - a + 0.0048, "MARCO-METALICO")
        k = 0
        while x0 + e + 0.03 + k * 0.035 < x0 + e + b - 0.02:
            xp = x0 + e + 0.03 + k * 0.035; lam.rect(xp, y0 + H - a, xp + t, y0 + H, "MARCO-METALICO"); k += 1
    # agua
    ya = y0 + ef + max(0.05, h - DS.BL - 0.10)
    lam.linea((x0 + e + 0.01, ya), (x0 + e + b - 0.01, ya), "AGUA")
    lam.cota((x0, y0), (x0 + W, y0), -12, True)
    lam.cota((x0 + e, y0 + ef), (x0 + e + b, y0 + ef), 8 if not tapado else 6, True)
    lam.cota((x0, y0), (x0 + e, y0), -20, True)
    lam.cota((x0, y0), (x0, y0 + ef), -10, False)
    lam.cota((x0 + W, y0 + ef), (x0 + W, y0 + H), 10, False, texto="h = %.2f (variable)" % h if not tapado else "<>")
    lam.texto((x0 + W / 2, y0 + H + 0.16), titulo, 3.4, "TITULOS", TA.MIDDLE_CENTER)
    lam.texto((x0 + W / 2, y0 + H + 0.11), "ESC. 1/5", 2.2, "TEXTOS", TA.MIDDLE_CENTER)


def dc02(doc, R, ox, oy):
    lam = B.Lamina(doc, ox, oy, 5, "DC-02", "CUADRO DE TRAMOS Y SECCIONES TIPICAS DE CUNETA",
                   "COTAS DE FONDO, PROFUNDIDADES Y PENDIENTES POR TRAMO - SECCION CON REJILLA Y SECCION TAPADA", escala_txt="INDICADA")
    nom = R["nombre"]; filas = []
    for r in R["ramales"]:
        for t in r["tramos"]:
            filas.append([r["codigo"], nom[t["de"]], nom[t["a"]], "%.2f" % t["L"], "%.2f" % t["ras_de"], "%.2f" % t["ras_a"], "%.3f" % t["cf_de"],
                          "%.3f" % t["cf_a"], "%.2f" % t["h_de"], "%.2f" % t["h_a"], "%.2f" % (100 * t["S"]), "%.2f" % t["L_tapado"]])
    cab = ["RAMAL", "DE", "A", "L (m)", "RAS. DE", "RAS. A", "C.F. DE", "C.F. A", "h DE", "h A", "S (%)", "TAPADO (m)"]
    anch = [16, 14, 14, 17, 20, 20, 21, 21, 14, 14, 15, 20]
    mitad = (len(filas) + 1) // 2
    lam.tabla(30, 566, cab, filas[:mitad], anch, hmm=1.8, alto_mm=5.6, titulo="CUADRO DE TRAMOS (C.F. = COTA DE FONDO, RAS. = RASANTE, h = PROFUNDIDAD)")
    lam.tabla(30 + sum(anch) + 10, 566, cab, filas[mitad:], anch, hmm=1.8, alto_mm=5.6)
    # resumen por sistema
    res = []
    for k in (1, 2, 3, 4):
        rr = [r for r in R["ramales"] if r["sistema"] == k]
        L = sum(r["L"] for r in rr); Lt = sum(t["L_tapado"] for r in rr for t in r["tramos"])
        hx = max(t["h_max"] for r in rr for t in r["tramos"])
        res.append([NOM_SIS[k], "%d" % len(rr), "%.2f" % L, "%.2f" % (L - Lt), "%.2f" % Lt, "%.2f" % hx])
    Lt = sum(float(x[2]) for x in res); res.append(["TOTAL", "%d" % len(R["ramales"]), "%.2f" % Lt, "%.2f" % sum(float(x[3]) for x in res),
                                                   "%.2f" % sum(float(x[4]) for x in res), "%.2f" % max(float(x[5]) for x in res[:4])])
    lam.tabla(30, 128, ["SISTEMA", "RAMALES", "LONGITUD (m)", "CON REJILLA (m)", "TAPADO (m)", "h MAX (m)"], res, [86, 20, 28, 32, 26, 22],
              hmm=1.8, alto_mm=5.6, titulo="RESUMEN POR SISTEMA")
    # secciones tipicas a 1/5 debajo de los cuadros
    seccion(lam, *lam.P(300, 172), 0.30, False, "SECCION TIPICA CON REJILLA")
    seccion(lam, *lam.P(520, 172), 0.30, True, "SECCION EN TRAMO TAPADO")
    lam.notas(300, 128, "NOTAS DE LAS SECCIONES", [
        "1. Concreto f'c = 175 kg/cm2 en muros y losa de fondo; juntas de dilatacion cada 3.00 m con sellador asfaltico.",
        "2. Rejilla metalica: platinas 1\" x 3/16\" sobre marco de angulo 1\" x 1\" x 3/16\" anclado a los muros.",
        "3. Tramo tapado: losa de concreto armado e = 0.10 m (acero 3/8\") apoyada en el rebaje de los muros, al nivel de la vereda.",
        "4. h = profundidad libre desde la rasante hasta la cota de fondo: 0.30 m al inicio; variable segun el cuadro de tramos.",
        "5. Secciones dibujadas con h = 0.30 m; los valores de cada tramo estan en el cuadro y en los perfiles."], hmm=1.6, ancho_mm=330)
    return lam


# ----------------------------------------------------------------------------- perfiles 1/100
ANCHO_FR = 74.0          # m de perfil por franja


def piezas(R):
    out = []
    for r in R["ramales"]:
        L = r["L"]; n = max(1, int(math.ceil(L / ANCHO_FR))); paso = L / n
        for k in range(n): out.append((r, k * paso, (k + 1) * paso, n > 1))
    return out


def perfil(lam, r, s0, s1, xmm, ymm_base, alto_mm, R):
    """Perfil del ramal r entre s0 y s1 con su guitarra; xmm, ymm_base = esquina inferior izquierda de la guitarra (mm)."""
    f = lam.f; P = r["perfil"]; nom = R["nombre"]
    seg = [p for p in P if s0 - 1e-6 <= p[0] <= s1 + 1e-6]
    zmin = min(p[2] for p in seg) - 0.20; zmax = max(p[1] for p in seg) + 0.30
    zref = math.floor(zmin * 2) / 2
    filas = ["PROGRESIVA (m)", "RASANTE", "COTA DE FONDO", "PROFUNDIDAD h", "PENDIENTE S (%)"]
    alto_g = 6.5; y_g = ymm_base; y0d = y_g + alto_g * len(filas) + 6       # el dibujo empieza sobre la guitarra
    X = lambda s: lam.P(xmm + 32 + (s - s0) / f, 0)[0]
    Yz = lambda z: lam.P(0, y0d + (z - zref) / f)[1]
    # guitarra
    xg1 = xmm + 32 + (s1 - s0) / f
    for i, t in enumerate(filas):
        yy = y_g + alto_g * (len(filas) - i)
        lam.linea(lam.P(xmm, yy), lam.P(xg1, yy), "GUITARRA")
        lam.texto(lam.P(xmm + 1, yy - alto_g / 2), t, 1.45, "TEXTOS", TA.MIDDLE_LEFT)
    lam.linea(lam.P(xmm, y_g), lam.P(xg1, y_g), "GUITARRA"); lam.linea(lam.P(xmm, y_g), lam.P(xmm, y_g + alto_g * len(filas)), "GUITARRA")
    lam.linea(lam.P(xmm + 30, y_g), lam.P(xmm + 30, y_g + alto_g * len(filas)), "GUITARRA")
    # dibujo: concreto de la losa de fondo y muros (vista), rasante y fondo
    fondo = [(X(p[0]), Yz(p[2])) for p in seg]; ras = [(X(p[0]), Yz(p[1])) for p in seg]
    bajo = [(X(p[0]), Yz(p[2] - 0.10)) for p in seg]
    lam.relleno(fondo + bajo[::-1], "CONCRETO-ACHURADO"); lam.poli(fondo, "CONCRETO"); lam.poli(bajo, "CONCRETO")
    lam.poli(ras, "TERRENO")
    for s_a, s_b in r["tapados"]:
        a, b = max(s_a, s0), min(s_b, s1)
        if b - a > 0.3:
            pts = [(X(p[0]), Yz(p[1])) for p in seg if a <= p[0] <= b]
            if len(pts) > 1:
                low = [(x, y - 0.10) for x, y in pts]
                lam.relleno(pts + low[::-1], "CONCRETO-ACHURADO"); lam.poli(pts + low[::-1], "CONCRETO", cerrada=True)
    # eje de cotas
    z = zref
    while z <= zmax + 0.01:
        lam.linea((X(s0) - 1.5 * f, Yz(z)), (X(s0), Yz(z)), "GRILLA")
        lam.texto((X(s0) - 2.0 * f, Yz(z)), "%.2f" % z, 1.3, "TEXTOS", TA.MIDDLE_RIGHT)
        z += 0.5
    lam.linea((X(s0), Yz(zref)), (X(s0), Yz(zmax)), "GRILLA")
    # estaciones: nudos + cada 10 m
    est = []
    acc = 0.0; tr = r["tramos"]
    nodos = [(0.0, tr[0]["de"])]
    for t in tr: acc += t["L"]; nodos.append((acc, t["a"]))
    for sN, n in nodos:
        if s0 - 1e-6 <= sN <= s1 + 1e-6: est.append((sN, n))
    for sx in (s0, s1):
        if all(abs(sx - e[0]) > 1.0 for e in est): est.append((sx, None))
    k = math.ceil(s0 / 10) * 10
    while k < s1 - 1e-6:
        if all(abs(k - e[0]) > 3.0 for e in est): est.append((k, None))
        k += 10
    est.sort()
    def val(sv):
        best = min(seg, key=lambda p: abs(p[0] - sv)); return best
    ult = -1e9
    for sv, n in est:
        p = val(sv); xs = X(sv)
        lam.linea((xs, Yz(p[2])), (xs, lam.P(0, y_g + alto_g * len(filas))[1]), "GRILLA")
        if n:
            lam.linea((xs, Yz(p[1])), (xs, Yz(p[1]) + 4 * f), "TEXTOS")
            lam.texto((xs, Yz(p[1]) + 4.6 * f), nom[n], 1.6, "TEXTOS", TA.BOTTOM_CENTER)
        if (xs - ult) / f < 6.5: continue
        ult = xs
        for i, v in enumerate(["%.2f" % sv, "%.2f" % p[1], "%.3f" % p[2], "%.2f" % (p[1] - p[2])]):
            lam.texto((xs, lam.P(0, y_g + alto_g * (len(filas) - i - 0.5))[1]), v, 1.25, "TEXTOS", TA.MIDDLE_CENTER)
    # pendiente por tramo
    acc = 0.0
    for t in tr:
        a, b = acc, acc + t["L"]; acc = b
        a2, b2 = max(a, s0), min(b, s1)
        if b2 - a2 > 0.5:
            lam.texto(((X(a2) + X(b2)) / 2, lam.P(0, y_g + alto_g * 0.5)[1]), "%.2f" % (100 * t["S"]), 1.25, "TEXTOS", TA.MIDDLE_CENTER)
            lam.linea((X(b2), lam.P(0, y_g)[1]), (X(b2), lam.P(0, y_g + alto_g)[1]), "GUITARRA")
    tit = "PERFIL %s - %s" % (r["codigo"], r["descripcion"].upper())
    if s0 > 0 or s1 < r["L"] - 0.01: tit += "  (PROG. %.2f A %.2f)" % (s0, s1)
    lam.texto(lam.P(xmm, y0d + (zmax - zref) / f + 7), tit, 2.4, "TITULOS", TA.LEFT)
    return y0d + (zmax - zref) / f + 12


def perfiles(doc, R, ox0, oy0, sep):
    """Reparte los perfiles en laminas A1 (4 franjas por lamina)."""
    pz = piezas(R); lams = []; k = 0; num = 3
    franjas = []
    cur, ancho = [], 0.0
    for p in pz:
        L = p[2] - p[1]
        if ancho + L + (8 if cur else 0) > ANCHO_FR and cur:
            franjas.append(cur); cur, ancho = [], 0.0
        cur.append(p); ancho += L + (8 if len(cur) > 1 else 0)
    if cur: franjas.append(cur)
    # alto de cada franja segun el desnivel
    def alto(fr):
        return max((max(q[1] for q in p[0]["perfil"] if p[1] <= q[0] <= p[2]) - min(q[2] for q in p[0]["perfil"] if p[1] <= q[0] <= p[2]) + 0.8) * 10
                   for p in fr) + 6.5 * 5 + 22
    i = 0
    while i < len(franjas):
        ox = ox0 + (num - 3) * sep
        lam = B.Lamina(doc, ox, oy0, 100, "DC-%02d" % num, "PERFILES LONGITUDINALES DE CUNETAS",
                       "RASANTE, COTA DE FONDO, PROFUNDIDAD Y PENDIENTE POR RAMAL - ESC. H = V = 1/100")
        ytop = 580; usados = []
        while i < len(franjas):
            a = alto(franjas[i])
            ybase = ytop - a
            limite = 108 if True else 12
            if ybase < limite: break
            x = 30
            for (r, s0, s1, part) in franjas[i]:
                perfil(lam, r, s0, s1, x, ybase, a, R)
                x += 32 + (s1 - s0) * 10 + 8 * 10 / 10 * 1.0 + 10
            ytop = ybase - 4; i += 1
        lams.append(lam); num += 1
    return lams


def indice(doc, ox, oy, lista):
    lam = B.Lamina(doc, ox, oy, 25, "DC-00", "INDICE DE LAMINAS - PLANTEAMIENTO PRELIMINAR DE CUNETAS",
                   "RELACION DE LAMINAS, FORMATO DE PAPEL Y ESCALA - IMPRIMIR CADA PRESENTACION A ESCALA 1:1", formato="A3", escala_txt="S/E")
    filas = [[str(i + 1), cod, tit, form, esc] for i, (cod, tit, form, esc) in enumerate(lista)]
    yb = lam.tabla(30, 277, ["N.", "LAMINA", "DESCRIPCION", "FORMATO", "ESCALA"], filas, [10, 20, 268, 40, 32], hmm=1.7, alto_mm=6.0,
                   titulo="INDICE DE LAMINAS")
    lam.notas(30, yb - 8, "NOTAS DE IMPRESION", [
        "1. Cada lamina tiene su presentacion (pestana) con el papel ISO full bleed indicado y la ventana bloqueada a su escala.",
        "2. Imprimir desde la pestana de la lamina: area = presentacion, escala 1:1, centrado.",
        "3. Coordenadas de la planta en UTM (las del plano de arquitectura PLANTA_GENERAL_590_2)."], hmm=1.6, ancho_mm=330)
    return lam


def construir():
    if 5 not in B.ESCALAS: B.ESCALAS.append(5)
    R = json.load(open(os.path.join(CALC, "diseno.json")))
    doc = B.nuevo_documento(); preparar(doc)
    lams = {}
    l1 = dc01(doc, R); lams["DC-01"] = l1
    ox2, oy2 = l1.ox, l1.oy - 594 * 0.25 - 60
    l2 = dc02(doc, R, ox2, oy2); lams["DC-02"] = l2
    lp = perfiles(doc, R, ox2 + 841 * 0.005 + 20, oy2, 841 * 0.1 + 15)
    for l in lp: lams[l.codigo] = l
    ind = [("DC-01", "PLANTA GENERAL DE CUNETAS - PLANTEAMIENTO PRELIMINAR", "A1", "1/250"),
           ("DC-02", "CUADRO DE TRAMOS Y SECCIONES TIPICAS DE CUNETA", "A1", "1/5")] + \
          [(l.codigo, "PERFILES LONGITUDINALES DE CUNETAS", "A1", "1/100") for l in lp]
    l0 = indice(doc, l1.ox - 420 * 0.025 - 20, l1.oy, ind); lams = {"DC-00": l0, **lams}
    LY.presentaciones(doc, lams)
    doc.audit(); doc.saveas(SAL)
    cajas = {k: [l.ox, l.oy, l.ox + l.W * l.f, l.oy + l.H * l.f] for k, l in lams.items()}
    json.dump(cajas, open(os.path.join(CALC, "laminas.json"), "w"), indent=1)
    print(SAL); print(cajas)


if __name__ == "__main__":
    construir()
