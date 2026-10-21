"""Planos del planteamiento preliminar de cunetas - I.E. N.° 0590, Barranquita (Lamas - San Martin).

DC-00 indice; DC-01 planta general de cunetas (1/250, coordenadas UTM reales); DC-02 cuadro de tramos y secciones tipicas
(1/5); DC-03... perfiles longitudinales por eje (1/50, H = V) y secciones transversales (1/20) de perfiles_b.py.
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
import cortes_b as CT
import perfiles_b as PB
import descargas_b as DB
import planta_cunetas_b as PC

SAL = os.path.join(RAIZ, "entregables_barranquita", "PLANTEAMIENTO_CUNETAS_IE0590_BARRANQUITA.dxf")
CALC = os.path.join(RAIZ, "entregables_barranquita", "_calc")

B.PROYECTO = ("MEJORAMIENTO Y AMPLIACION DEL SERVICIO DE EDUCACION PRIMARIA EN LA I.E. N.° 0590, DISTRITO DE BARRANQUITA,",
              "PROVINCIA DE LAMAS, DEPARTAMENTO DE SAN MARTIN - C.I. N.° 468901")
B.UBICACION = "UBICACION: I.E. N.° 0590 - BARRANQUITA - LAMAS - SAN MARTIN"
B.ESPECIALIDAD = "ESPECIALIDAD: DRENAJE PLUVIAL - CUNETAS (PLANTEAMIENTO PRELIMINAR)"
B.ENTIDAD = "ENTIDAD:"
B.ELABORADO = ""
B.FECHA = "OCT. 2026"

DIR_DESCARGA = DS.DIR_SALIDA                   # D2: el agua sale de lado, por el fondo de la hondonada natural
COL_SIS = {1: 5, 2: 6, 3: 94, 4: 30}
SIS = sorted(DS.SISTEMAS)
NOM_BLQ = {k: "SISTEMA_%d_%s" % (k, v[0].replace(" Y ", "_").replace(" ", "_").replace("-", "")) for k, v in DS.SISTEMAS.items()}
NOM_SIS = {k: "SISTEMA %d - %s (descarga %s)" % (k, v[0], v[1]) for k, v in DS.SISTEMAS.items()}
LISTA_D = ", ".join(sorted(DS.DESCARGAS)[:-1]) + " Y " + sorted(DS.DESCARGAS)[-1]       # "D1, D2, D3 Y D4"
CAPAS_EXTRA = [("CURVAS", 33, "CONTINUOUS"), ("CURVAS-TXT", 33, "CONTINUOUS"), ("ARQ-TECHO", 8, "CONTINUOUS"), ("ARQ-VEREDA", 9, "CONTINUOUS"),
               ("CUNETA-S1", 5, "CONTINUOUS"), ("CUNETA-S2", 6, "CONTINUOUS"), ("CUNETA-S3", 94, "CONTINUOUS"), ("CUNETA-S4", 30, "CONTINUOUS"),
               ("CUNETA-REJILLA", 254, "CONTINUOUS"), ("CUNETA-REJ-LIN", 8, "CONTINUOUS"), ("CUNETA-TAPADO", 252, "CONTINUOUS"),
               ("FLUJO-C", 7, "CONTINUOUS"), ("LIMITE-INTERV", 1, "DASHED"), ("POZA", 8, "CONTINUOUS"), ("CUNETA-GRADAS", 1, "CONTINUOUS"), ("NUDOS", 7, "CONTINUOUS"), ("DESCARGA", 1, "CONTINUOUS"), ("MURO-CONT", 6, "CONTINUOUS")]
RGB_EXTRA = {"CURVAS": (176, 136, 96), "CURVAS-TXT": (150, 110, 70), "CUNETA-REJILLA": (232, 232, 232), "CUNETA-TAPADO": (160, 160, 160)}


DS_NIV = "Interior del cerco nivelado: pisos y pasadizos NPT +184.65; borde de cuneta +184.65 (al ras del piso); areas verdes +184.60; patio de maniobra +184.50 (cuneta al ras, con rejilla)."

def preparar(doc):
    for n, c, lt in CAPAS_EXTRA:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt)
            if n in RGB_EXTRA: ly.rgb = RGB_EXTRA[n]
    for n, rgb in RGB_EXTRA.items(): B.COLOR_RGB[n] = rgb
    PC.capas(doc, B.COLOR_RGB)
    for n, g in (("CUNETA-S1", 35), ("CUNETA-S2", 35), ("CUNETA-S3", 35), ("CUNETA-S4", 35), ("LIMITE-INTERV", 70), ("CURVAS", 13), ("ARQ-TECHO", 13),
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


class EnBloque:
    """Todo lo que se dibuja dentro del with va a un bloque de AutoCAD (coordenadas reales) insertado en (0, 0)."""
    def __init__(self, lam, nombre, capa="0"): self.lam, self.nombre, self.capa = lam, nombre, capa

    def __enter__(self):
        self.prev = self.lam.msp; self.lam.msp = self.lam.doc.blocks.new(self.nombre); return self

    def __exit__(self, *a):
        self.lam.msp = self.prev; self.prev.add_blockref(self.nombre, (0, 0), dxfattribs={"layer": self.capa})


def gradas_de(V):
    """Tramos con V > 3.0 m/s (verificacion): se resuelven con gradas de concreto."""
    return {(f["ramal"], f["de"], f["a"]) for f in V["hidraulica"] if f["vel"] != "CUMPLE"}


# ----------------------------------------------------------------------------- DC-01 planta general
def base_sitio(lam, G, caja):
    x0, y0, x1, y1 = caja
    def dentro(pts): return any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in pts)
    with EnBloque(lam, "ARQUITECTURA_BASE", "ARQ-BASE"):
        for capa_src, capa, solo_cerrada in (("0_VEREDAS", "ARQ-VEREDA", False), ("0_PROYECCIONES 1", "ARQ-TECHO", False), ("0_MUROS 1", "ARQ-BASE", False),
                                             ("MUROS-02", "ARQ-BASE", False), ("2", "CERCO", False), ("MURO DE CONTENCION", "MURO-CONT", False)):
            for pts, cl, b in G["geo"].get(capa_src, []):
                if len(pts) > 1 and dentro(pts):
                    lam.poli([(p[0], p[1]) for p in pts], capa, cerrada=cl)
    with EnBloque(lam, "CURVAS_DE_NIVEL", "CURVAS"):
        curvas_nivel(lam, G, caja)


def curvas_nivel(lam, G, caja):
    """Curvas de nivel (cada 0.50 m) con su cota en las de metro entero."""
    x0, y0, x1, y1 = caja
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


def dc01(doc, R, V):
    f = 0.25
    caja = (354806.0, 9249776.0, 354988.0, 9249889.0)
    ox, oy = caja[0] - 30 * f, caja[3] - 578 * f
    lam = B.Lamina(doc, ox, oy, 250, "DC-01", "PLANTA GENERAL DE CUNETAS - PLANTEAMIENTO PRELIMINAR",
                   "TRAZO, SENTIDO DE FLUJO, REJILLAS, TRAMOS TAPADOS Y DESCARGAS - COORDENADAS UTM WGS84")
    G = T.cargar()
    base_sitio(lam, G, caja)
    with EnBloque(lam, "LIMITE_DE_INTERVENCION", "LIMITE-INTERV"):     # cerco perimetrico confirmado
        lam.poli(DS.CERCO, "LIMITE-INTERV", cerrada=True, ancho=0.35)
    ram = R["ramales"]; tap = {r["codigo"]: r["tapados"] for r in ram}; nom = R["nombre"]; grad = gradas_de(V)
    PC.TAPAS.clear()
    for k in SIS:
        with EnBloque(lam, "CUNETAS_" + NOM_BLQ[k], "CUNETA-S%d" % k):
            rr = [r for r in ram if r["sistema"] == k]
            PC.dibujar(lam, R, rr)                # escala real: bordes 0.60 / 0.40, rejilla, tapado, flechas y tapas
            for r in rr:
                pts = puntos_ramal(R, r["nudos"]); acc = 0.0
                for t in r["tramos"]:
                    if (r["codigo"], nom[t["de"]], nom[t["a"]]) in grad:
                        s = acc + 0.25
                        while s < acc + t["L"] - 0.1:          # gradas: escalones cada 0.50 m
                            p, (ux, uy) = a_lo_largo(pts, s)
                            lam.poli([(p[0] - uy * 0.28, p[1] + ux * 0.28), (p[0] + uy * 0.28, p[1] - ux * 0.28)], "CUNETA-GRADAS", ancho=0.12); s += 0.5
                    acc += t["L"]
    # nudos, rotulos y descargas (bloque ROTULOS_RED)
    with EnBloque(lam, "ROTULOS_RED", "NUDOS"):
        E = Etiquetas(lam)
        empalmes = {r["nudos"][-1] for r in ram}
        rotular = lambda n: n not in DS.DESCARGAS and ("~" not in n or n in empalmes)   # los quiebres a 45 no se rotulan
        for n, xy in R["nudos"].items():
            if not rotular(n): continue
            lam.circulo(tuple(xy), 0.30, "NUDOS")
        for r in ram:                                          # codigo del eje junto a su tramo mas largo
            pts = puntos_ramal(R, r["nudos"]); i = max(range(len(pts) - 1), key=lambda k: math.dist(pts[k], pts[k + 1]))
            L = math.dist(pts[i], pts[i + 1]); ux, uy = (pts[i + 1][0] - pts[i][0]) / L, (pts[i + 1][1] - pts[i][1]) / L
            c = (pts[i][0] + ux * L * 0.62, pts[i][1] + uy * L * 0.62)
            E.poner((c[0] - uy * 0.8, c[1] + ux * 0.8), r["codigo"], 2.0, "TEXTOS", color=COL_SIS[r["sistema"]], d_mm=1.5)
        for n, xy in R["nudos"].items():
            if rotular(n): E.poner(tuple(xy), nom[n], 1.45, "TEXTOS", d_mm=1.6)
        hechas = set()
        for r in sorted(ram, key=lambda r: -r["L"]):
            fin = r["nudos"][-1]
            if fin not in DS.DESCARGAS or fin in hechas: continue
            hechas.add(fin)
            pts = puntos_ramal(R, r["nudos"]); a, b = pts[-2], pts[-1]; L = math.dist(a, b); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            if fin in DIR_DESCARGA: ux, uy = DIR_DESCARGA[fin]
            q = (b[0] + ux * 4.0, b[1] + uy * 4.0)
            lam.poli([b, q], "DESCARGA", ancho=0.25); lam.flecha(b, (q[0] + ux * 0.8, q[1] + uy * 0.8), "DESCARGA", tam_mm=4.0)
            E.poner(q, fin, 3.0, "TITULOS", color=1, d_mm=1.5)
            if fin in DS.POZA:                                 # poza de salida al final del ramal, junto al cerco
                bp, lp = DS.POZA_DIM; ax, ay = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                e = DS.E_MURO; w = bp / 2 + e
                q4 = [(b[0] - ay * w, b[1] + ax * w), (b[0] + ay * w, b[1] - ax * w),
                      (b[0] + ay * w - ax * (lp + e), b[1] - ax * w - ay * (lp + e)), (b[0] - ay * w - ax * (lp + e), b[1] + ax * w - ay * (lp + e))]
                lam.poli(q4, "POZA", cerrada=True, ancho=0.05)
                E.poner(q4[2], "POZA DE SALIDA %.2f x %.2f" % (bp, lp), 1.5, "TEXTOS", color=1, d_mm=1.4)
        for (c_, de, a_) in sorted(grad):                    # rotulo GRADAS junto a cada tramo
            r = next(x for x in ram if x["codigo"] == c_); inv = {v: k for k, v in nom.items()}
            pa, pb = R["nudos"][inv[de]], R["nudos"][inv[a_]]
            E.poner(((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2), "GRADAS", 1.6, "TEXTOS", color=1, d_mm=1.4)
    lam.bloque("SIMB-NORTE", lam.P(785, 548))
    # leyenda, notas y cuadro de descargas (franja inferior)
    items = [("linea2", "CUNETA-S%d" % k, "Rotulo de eje: " + NOM_SIS[k]) for k in SIS]
    items += [("linea", "CUN-REJ-BORDE", "Cuneta con rejilla: 0.60 m = muros 0.10 + 0.40 libres (platinas cada 0.10 m)"),
              ("linea", "CUN-TAP-BORDE", "Cuneta tapada: losa e = 0.10 m (veredas, ingresos, patio y pase por el cerco)"),
              ("rect", "CUN-TAPA-INSP", "Tapa de inspeccion 0.60 x 0.60 (%d en total)" % len(PC.TAPAS))] + \
             [("linea2", "CUNETA-GRADAS", "Gradas de concreto (pendiente fuerte, V > 3 m/s)")] * bool(grad) + [
              ("linea2", "CUN-FLUJO", "Sentido del flujo (escala real)"), ("linea2", "DESCARGA", "Descarga %s a %s: agua sobre el terreno natural" % (min(DS.DESCARGAS), max(DS.DESCARGAS))), ("linea", "CURVAS", "Curva de nivel cada 0.50 m (C-TOPO)"),
              ("linea", "ARQ-TECHO", "Proyeccion de techos (a dos aguas)"), ("linea", "CERCO", "Cerco perimetrico (plano de arquitectura)"),
              ("linea2", "LIMITE-INTERV", "Limite de intervencion = cerco perimetrico")] + [("linea", "POZA", "Poza de salida (%s)" % ", ".join(sorted(DS.POZA)))] * bool(DS.POZA)
    lam.leyenda2(30, 128, items, hmm=1.7, ancho_col=118, filas_col=6)
    est = {d["D"]: d for d in V["descargas"]}
    filas = [[k, "%.3f" % est[k]["cf"], v.split(":")[0], ("poza: rebalsa a %.2f; afuera baja 0.25 m a %.1f m" % (est[k]["nivel_rebalse"], est[k]["sale_a_m"]))
              if est[k]["tipo"] == "poza" else ("pase en el cimiento; terreno bajo C.F. a %.1f m" % est[k]["sale_a_m"])] for k, v in sorted(R["descargas"].items())]
    lam.tabla(30, 72, ["DESC.", "C.F.", "UBICACION", "SALIDA POR GRAVEDAD"], filas, [14, 18, 112, 80], hmm=1.5, alto_mm=4.6, titulo="DESCARGAS")
    c = R["criterios"]
    lam.notas(275, 72, "CRITERIOS DEL PLANTEAMIENTO", [
        "1. Cuneta rectangular de concreto: ancho total %.2f m = muros de %.2f m + %.2f m libres; losa de fondo de 0.10 m." % (c["b_tot"], c["muro"], c["b_int"]),
        "2. Profundidad al inicio de cada eje %.2f m; minima %.2f m donde el terreno cae mas que la cuneta; cota de fondo con S = %.1f %%." % (c["h0"], c["hmin"], 100 * c["S"]),
        "3. %s" % DS_NIV,
        "4. Techos a dos aguas: cada alero descarga a la cuneta de su lado. Rejilla en tramos abiertos; losa tapa en cruces de vereda e ingresos.",
        "   Tramos tapados: tapa de inspeccion 0.60 x 0.60 al inicio y al final, en cada empalme y a %.0f m como maximo entre tapas." % PC.MAX_TAPAS,
        "5. Cotas de fondo, profundidades y pendientes por tramo en la lamina DC-02 y en los perfiles DC-03 en adelante.",
        "6. Todas las cunetas quedan dentro del cerco (limite de intervencion). %s salen por un pase en el cimiento del cerco%s."
        % (", ".join(d["D"] for d in V["descargas"] if d["tipo"] == "pase"), "".join("; %s por una poza que rebalsa al terreno" % d["D"] for d in V["descargas"] if d["tipo"] == "poza")),
        "7. Fuera del cerco no hay obra: el agua sigue por el terreno natural (%s)." % "; ".join(
            "%s perfilado de %.1f m donde el terreno queda sobre la C.F." % (d["D"], d["sale_a_m"]) for d in V["descargas"] if d["tipo"] == "pase"),
        "8. Ejes de cuneta: lineas magenta del plano ULTIMA VERSION (lados de cada bloque: techos a dos aguas) y uniones hasta las descargas.",
        "9. Bloques de AutoCAD: ARQUITECTURA_BASE, CURVAS_DE_NIVEL, LIMITE_DE_INTERVENCION, CUNETAS_SISTEMA_1 a %d (uno por sector) y ROTULOS_RED." % max(SIS)], hmm=1.5, ancho_mm=355)
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
    cab = ["EJE", "DE", "A", "L (m)", "RAS. DE", "RAS. A", "C.F. DE", "C.F. A", "h DE", "h A", "S (%)", "TAPADO (m)"]
    anch = [16, 14, 14, 17, 20, 20, 21, 21, 14, 14, 15, 20]
    mitad = (len(filas) + 1) // 2
    lam.tabla(30, 566, cab, filas[:mitad], anch, hmm=1.8, alto_mm=5.6, titulo="CUADRO DE TRAMOS (C.F. = COTA DE FONDO, RAS. = RASANTE, h = PROFUNDIDAD)")
    lam.tabla(30 + sum(anch) + 10, 566, cab, filas[mitad:], anch, hmm=1.8, alto_mm=5.6)
    # resumen por sistema
    res = []
    for k in SIS:
        rr = [r for r in R["ramales"] if r["sistema"] == k]
        L = sum(r["L"] for r in rr); Lt = sum(t["L_tapado"] for r in rr for t in r["tramos"])
        hx = max(t["h_max"] for r in rr for t in r["tramos"])
        res.append([NOM_SIS[k], "%d" % len(rr), "%.2f" % L, "%.2f" % (L - Lt), "%.2f" % Lt, "%.2f" % hx])
    Lt = sum(float(x[2]) for x in res); res.append(["TOTAL", "%d" % len(R["ramales"]), "%.2f" % Lt, "%.2f" % sum(float(x[3]) for x in res),
                                                   "%.2f" % sum(float(x[4]) for x in res), "%.2f" % max(float(x[5]) for x in res[:len(SIS)])])
    lam.tabla(30, 128, ["SISTEMA", "EJES", "LONGITUD (m)", "CON REJILLA (m)", "TAPADO (m)", "h MAX (m)"], res, [86, 20, 28, 32, 26, 22],
              hmm=1.8, alto_mm=5.6, titulo="RESUMEN POR SISTEMA")
    # secciones tipicas a 1/5 debajo de los cuadros
    seccion(lam, *lam.P(300, 172), 0.30, False, "SECCION TIPICA CON REJILLA")
    seccion(lam, *lam.P(520, 172), 0.40, True, "SECCION EN TRAMO TAPADO")
    lam.notas(300, 128, "NOTAS DE LAS SECCIONES", [
        "1. Concreto f'c = 175 kg/cm2 en muros y losa de fondo; juntas de dilatacion cada 3.00 m con sellador asfaltico.",
        "2. Rejilla metalica: platinas 1\" x 3/16\" sobre marco de angulo 1\" x 1\" x 3/16\" anclado a los muros.",
        "3. Tramo tapado: losa de concreto armado e = 0.10 m (acero 3/8\") apoyada en el rebaje de los muros, al nivel de la vereda.",
        "4. h = profundidad libre desde la rasante hasta la cota de fondo: 0.30 m al inicio; variable segun el cuadro de tramos.",
        "5. Secciones dibujadas con h = 0.30 m (rejilla) y h = 0.40 m (tapada: 0.30 libre bajo la losa; minimo 0.25 libre); valores de cada tramo en el cuadro y los perfiles.",
        "6. Acero solo en cunetas con h >= 0.40 m (de la rejilla al fondo) y en tramos tapados; con h < 0.40 m, concreto simple. Corte de cada seccion en DC-12 en adelante."], hmm=1.6, ancho_mm=330)
    return lam


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
    V = json.load(open(os.path.join(CALC, "verificacion.json")))
    l1 = dc01(doc, R, V); lams["DC-01"] = l1
    ox2, oy2 = l1.ox, l1.oy - 594 * 0.25 - 60
    l2 = dc02(doc, R, ox2, oy2); lams["DC-02"] = l2
    SEC = PB.secciones(R); PB.capas(doc)
    lp = PB.perfiles(doc, R, SEC, ox2 + 841 * 0.005 + 20, oy2, 841 * PB.ESC_P / 1000 + 15, 3)
    xs = ox2 + 841 * 0.005 + 20 + len(lp) * (841 * PB.ESC_P / 1000 + 15)
    lsec = PB.cortes(doc, SEC, xs, oy2, 841 * PB.ESC_S / 1000 + 15, 3 + len(lp))
    for l in lp + lsec: lams[l.codigo] = l
    oyi = l1.oy + 594 * 0.25 + 60
    k0 = 3 + len(lp) + len(lsec); C = lambda i: "DC-%02d" % (k0 + i)    # laminas correlativas despues de perfiles y secciones
    CT.capas(doc)
    l10 = CT.dc10(doc, R, V, l1.ox, oyi, C(0)); lams[C(0)] = l10
    ld = DB.laminas(doc, R, V, l10.ox + 841 * 0.25 + 30, oyi, 841 * DB.ESC / 1000 + 15, k0 + 1)
    for l in ld: lams[l.codigo] = l
    ind = [("DC-01", "PLANTA GENERAL DE CUNETAS - PLANTEAMIENTO PRELIMINAR", "A1", "1/250"),
           ("DC-02", "CUADRO DE TRAMOS Y SECCIONES TIPICAS DE CUNETA", "A1", "1/5")] + \
          [(l.codigo, "PERFILES LONGITUDINALES DE CUNETAS POR EJE", "A1", "1/%d" % PB.ESC_P) for l in lp] + \
          [(l.codigo, "SECCIONES TRANSVERSALES DE CUNETAS", "A1", "1/%d" % PB.ESC_S) for l in lsec] + \
          [(C(0), "CORTES GENERALES DEL TERRENO Y LA RED", "A1", "1/250")] + \
          [(l.codigo, l.titulo, "A1", "INDICADA") for l in ld]
    l0 = indice(doc, l1.ox - 420 * 0.025 - 20, l1.oy, ind); lams = {"DC-00": l0, **lams}
    LY.presentaciones(doc, lams)
    doc.audit(); doc.saveas(SAL)
    cajas = {k: [l.ox, l.oy, l.ox + l.W * l.f, l.oy + l.H * l.f] for k, l in lams.items()}
    json.dump(cajas, open(os.path.join(CALC, "laminas.json"), "w"), indent=1)
    json.dump(ind, open(os.path.join(CALC, "indice.json"), "w"), indent=1, ensure_ascii=False)
    json.dump([{"eje": e, "progresiva": s_, "x": round(x, 3), "y": round(y, 3)} for e, s_, x, y, *_ in PC.TAPAS],
              open(os.path.join(CALC, "tapas.json"), "w"), indent=1)
    json.dump({e: [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in x.items()} for x in l] for e, l in SEC.items()},
              open(os.path.join(CALC, "secciones.json"), "w"), indent=1, ensure_ascii=False)
    print(SAL); print(cajas)


if __name__ == "__main__":
    construir()
