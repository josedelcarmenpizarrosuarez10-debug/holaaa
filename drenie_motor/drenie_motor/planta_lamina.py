"""Lamina de planta general de cunetas (DC-01) y lamina de cuadros (DC-02), en el estilo de las laminas de Barranquita.

DC-01: arquitectura de fondo (techos, veredas, muros), curvas de nivel, limite de intervencion (cerco), cunetas a escala real con
el ancho de cada eje (bordes exterior e interior; rejilla con sus platinas en celeste; tapados en verde con tapas de inspeccion
0.60 x 0.60), flechas rojas de flujo, lloraderos (tubo y caja filtrante) del lado del area verde, nudos, codigo de cada eje,
descargas, norte, leyenda, cuadro de descargas y criterios. Escala elegida para que el cerco entre en la lamina A1.
DC-02: cuadro de ejes (sector, longitud, caudal, ancho libre y total, profundidades, excavacion), cuadro de descargas con su
caudal y cuadro de tramos con lloraderos.
Todo en bloques de AutoCAD por tema y en coordenadas reales (UTM). 1 unidad = 1 m.
"""
import math

from ezdxf.enums import TextEntityAlignment as TA
from shapely.geometry import LineString, Point
from shapely.ops import substring, unary_union

from . import dxf_base as B

ESCALAS = [100, 125, 150, 200, 250, 300, 400, 500, 750, 1000]
PASO_PLATINA = 0.10
PASO_FLECHA = 5.0
TAPA = 0.60
MAX_TAPAS = 10.0
CAPAS = [("CURVAS", 33, "CONTINUOUS"), ("CURVAS-TXT", 33, "CONTINUOUS"), ("ARQ-TECHO", 8, "CONTINUOUS"), ("ARQ-VEREDA", 9, "CONTINUOUS"),
         ("ARQ-MURO", 8, "CONTINUOUS"), ("LIMITE-INTERV", 1, "DASHED"), ("NUDOS", 7, "CONTINUOUS"), ("DESCARGA", 1, "CONTINUOUS"),
         ("CUN-REJ-BORDE", 4, "CONTINUOUS"), ("CUN-REJ-PLATINA", 4, "CONTINUOUS"), ("CUN-TAP-BORDE", 3, "CONTINUOUS"),
         ("CUN-FLUJO", 1, "CONTINUOUS"), ("CUN-TAPA-INSP", 5, "CONTINUOUS"), ("LLORADERO", 3, "CONTINUOUS"), ("EJE-ROTULO", 5, "CONTINUOUS"),
         ("CANALETA", 30, "CONTINUOUS"), ("MONTANTE", 6, "CONTINUOUS"), ("MONTANTE-SALIDA", 6, "DASHED"),
         ("MONTANTE-TUBO", 4, "CONTINUOUS"), ("FALSA-COLUMNA", 5, "CONTINUOUS"), ("SUMIDERO", 1, "CONTINUOUS"),
         ("SUMIDERO-TUBO", 1, "DASHED")]
RGB = {"CURVAS": (176, 136, 96), "CURVAS-TXT": (150, 110, 70), "CUN-REJ-BORDE": (0, 170, 230), "CUN-REJ-PLATINA": (120, 205, 240),
       "CUN-TAP-BORDE": (0, 150, 0), "CUN-FLUJO": (230, 0, 0), "CUN-TAPA-INSP": (0, 0, 230), "LLORADERO": (0, 140, 60),
       "CANALETA": (230, 130, 0), "MONTANTE": (255, 0, 255), "MONTANTE-SALIDA": (190, 0, 190), "MONTANTE-TUBO": (0, 230, 230),
       "FALSA-COLUMNA": (0, 120, 255), "SUMIDERO": (200, 0, 0), "SUMIDERO-TUBO": (200, 0, 0)}
GROSOR = {"LIMITE-INTERV": 70, "CURVAS": 13, "ARQ-TECHO": 13, "ARQ-VEREDA": 9, "ARQ-MURO": 13, "DESCARGA": 35, "CUN-REJ-BORDE": 30,
          "CUN-TAP-BORDE": 30}


def capas(doc):
    for n, c, lt in CAPAS:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt)
            if n in RGB: ly.rgb = RGB[n]
        if n in GROSOR: doc.layers.get(n).dxf.lineweight = GROSOR[n]
    for n, rgb in RGB.items(): B.COLOR_RGB[n] = rgb


class EnBloque:
    """Lo que se dibuja dentro del with va a un bloque de AutoCAD (coordenadas reales) insertado en (0, 0)."""
    def __init__(self, lam, nombre, capa="0"): self.lam, self.nombre, self.capa = lam, nombre, capa

    def __enter__(self):
        self.prev = self.lam.msp
        if self.nombre in self.lam.doc.blocks: self.lam.doc.blocks.delete_block(self.nombre, safe=False)
        self.lam.msp = self.lam.doc.blocks.new(self.nombre); return self

    def __exit__(self, *a):
        self.lam.msp = self.prev; self.prev.add_blockref(self.nombre, (0, 0), dxfattribs={"layer": self.capa})


class Etiquetas:
    """Textos cortos junto a un punto sin pisar otros textos (8 posiciones de prueba)."""
    def __init__(self, lam): self.lam, self.cajas = lam, []

    def libre(self, c): return all(c[2] < o[0] or c[0] > o[2] or c[3] < o[1] or c[1] > o[3] for o in self.cajas)

    def poner(self, p, txt, hmm=1.8, capa="TEXTOS", color=None, d_mm=2.2):
        f = self.lam.f; h = hmm * B.K_TXT.get(capa, 1.0) * f; w = len(txt) * 0.62 * h
        for k in range(1, 4):
            for sx, sy in [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                d = d_mm * f * k
                x = p[0] + sx * d - (w if sx < 0 else (w / 2 if sx == 0 else 0)); y = p[1] + sy * d - (h if sy < 0 else (h / 2 if sy == 0 else 0))
                c = (x - 0.3 * f, y - 0.3 * f, x + w + 0.3 * f, y + h + 0.3 * f)
                if self.libre(c):
                    self.cajas.append(c); self.lam.texto((x, y), txt, hmm, capa, TA.BOTTOM_LEFT, color=color)
                    if k > 1: self.lam.linea(p, (x if sx >= 0 else x + w, y + h / 2), "LLAMADAS")
                    return
        x, y = p[0] + d_mm * f, p[1] + d_mm * f; self.cajas.append((x, y, x + w, y + h)); self.lam.texto((x, y), txt, hmm, capa, TA.BOTTOM_LEFT, color=color)


def _u(a, b):
    L = math.dist(a, b) or 1.0; return ((b[0] - a[0]) / L, (b[1] - a[1]) / L)


def _tap(tap, s): return any(a - 1e-6 <= s <= b + 1e-6 for a, b in tap)


def _anillos(g):
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.is_empty or not hasattr(p, "exterior"): continue
        out.append(list(p.exterior.coords)); out += [list(h.coords) for h in p.interiors]
    return out


def flecha(lam, c, u, largo=0.70, t=0.30, w=0.13, g=0.07):
    a = (c[0] - u[0] * largo / 2, c[1] - u[1] * largo / 2); b = (c[0] + u[0] * largo / 2, c[1] + u[1] * largo / 2)
    base = (b[0] - u[0] * t, b[1] - u[1] * t)
    lam.poli([a, base], "CUN-FLUJO", ancho=g)
    lam.solido([b, (base[0] - u[1] * w, base[1] + u[0] * w), (base[0] + u[1] * w, base[1] - u[0] * w), (base[0] + u[1] * w, base[1] - u[0] * w)], "CUN-FLUJO")


def tapa(lam, c, u):
    n = (-u[1], u[0]); h = TAPA / 2
    q = [(c[0] + sx * u[0] * h + sy * n[0] * h, c[1] + sx * u[1] * h + sy * n[1] * h) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    lam.poli(q, "CUN-TAPA-INSP", cerrada=True, ancho=0.03)
    for sx in (-0.17, 0.17):
        m = (c[0] + u[0] * sx, c[1] + u[1] * sx)
        lam.poli([(m[0] - n[0] * 0.07, m[1] - n[1] * 0.07), (m[0] + n[0] * 0.07, m[1] + n[1] * 0.07)], "CUN-TAPA-INSP", ancho=0.025)


def montante(lam, m, largo=0.20, ancho=0.15):
    """Montante en planta como en los planos del usuario: falsa columna adosada al muro en la esquina de la edificacion (azul),
    tubo PVC 4" (cian) y el concreto que lo envuelve (magenta)."""
    V = m["esquina"]; u = m["a_lo_largo"]; nv = m["hacia_alero"]
    P = lambda a, b: (V[0] + u[0] * a + nv[0] * b, V[1] + u[1] * a + nv[1] * b)
    lam.poli([P(0, 0), P(largo, 0), P(largo, ancho), P(0, ancho)], "FALSA-COLUMNA", cerrada=True)
    c = (m["x"], m["y"]); r = 0.1143 / 2
    lam.circulo(c, r, "MONTANTE-TUBO")
    lam.circulo(c, r + 0.012, "MONTANTE")


def cunetas(lam, R, descargas, anchos, P):
    """Cunetas a escala real con el ancho de cada eje. Devuelve el numero de tapas de inspeccion."""
    Nn = R["nudos"]; EM = P["e_muro"]
    nudo_eje = {}
    for r in R["ramales"]:
        for n in r["nudos"]: nudo_eje.setdefault(n, set()).add(r["codigo"])
    ejes = []
    for r in R["ramales"]:
        t0 = r["tramos"][0]; b = anchos.get((r["codigo"], t0["de"], t0["a"]), P["b_int"])
        ejes.append({"cod": r["codigo"], "pts": [tuple(Nn[n]) for n in r["nudos"]], "tap": r["tapados"], "b": b,
                     "ini": len(nudo_eje.get(r["nudos"][0], ())) == 1, "descarga": r["nudos"][-1] in descargas,
                     "recibe": [c for c in nudo_eje.get(r["nudos"][-1], ()) if c != r["codigo"]],
                     "empalmes": [tuple(Nn[n]) for n in r["nudos"][1:-1] if len(nudo_eje.get(n, ())) > 1]})
    lineas = {e["cod"]: LineString(e["pts"]) for e in ejes}

    def franja(e, d, ini=0.0):
        ln = lineas[e["cod"]]
        if ini > 0 and ln.length > ini: ln = substring(ln, ini, ln.length)
        return ln.buffer(d, cap_style=2, join_style=2)
    ext = unary_union([franja(e, e["b"] / 2 + EM) for e in ejes])
    ints = unary_union([franja(e, e["b"] / 2, EM if e["ini"] else 0.0) for e in ejes])

    def estado(x, y):
        pt = Point(x, y); e = min(ejes, key=lambda e: lineas[e["cod"]].distance(pt))
        return _tap(e["tap"], lineas[e["cod"]].project(pt))
    for g in (ext, ints):
        for anillo in _anillos(g):
            cur, est = [anillo[0]], None
            for a, b in zip(anillo[:-1], anillo[1:]):
                L = math.dist(a, b); n = max(1, int(L / 0.25))
                for k in range(n):
                    p = (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
                    q = (a[0] + (b[0] - a[0]) * (k + 0.5) / n, a[1] + (b[1] - a[1]) * (k + 0.5) / n)
                    e_ = estado(*q)
                    if est is not None and e_ != est:
                        lam.poli(cur, "CUN-TAP-BORDE" if est else "CUN-REJ-BORDE"); cur = [cur[-1]]
                    cur.append(p); est = e_
            if len(cur) > 1: lam.poli(cur, "CUN-TAP-BORDE" if est else "CUN-REJ-BORDE")
    for e in ejes:                                                   # platinas de la rejilla
        ln = lineas[e["cod"]]; BI = e["b"] / 2
        recibe = [(lineas[c], next(x["b"] for x in ejes if x["cod"] == c) / 2 + EM) for c in e["recibe"] if c in lineas]
        s = (EM if e["ini"] else 0.0) + PASO_PLATINA / 2
        while s < ln.length - 0.02:
            if not _tap(e["tap"], s):
                p = ln.interpolate(s); q = ln.interpolate(min(ln.length, s + 0.01)); o = ln.interpolate(max(0.0, s - 0.01))
                ux, uy = _u((o.x, o.y), (q.x, q.y))
                if not any(x.distance(p) < d + 0.02 for x, d in recibe):
                    lam.linea((p.x - uy * BI, p.y + ux * BI), (p.x + uy * BI, p.y - ux * BI), "CUN-REJ-PLATINA")
            s += PASO_PLATINA
    for e in ejes:                                                   # flechas de flujo
        pts = e["pts"]
        for a, b in zip(pts[:-1], pts[1:]):
            L = math.dist(a, b)
            if L < 0.4: continue
            u = _u(a, b); n = max(1, int(L // PASO_FLECHA)) if L >= 2.0 else 1
            for j in range(n): flecha(lam, (a[0] + u[0] * (j + 0.5) * L / n, a[1] + u[1] * (j + 0.5) * L / n), u)
    ntapas = 0
    for e in ejes:                                                   # tapas de inspeccion en los tapados
        ln = lineas[e["cod"]]; L = ln.length; BT = e["b"] / 2 + EM; pos = []
        for a, b in e["tap"]:
            a2 = a + (0.0 if a > 0.01 else EM)
            b2 = (L - (0.075 + 0.15 + TAPA / 2 if e["descarga"] else BT + TAPA / 2)) if b >= L - 0.08 else b
            i0, i1 = a2 + TAPA / 2 + 0.10, b2 - TAPA / 2 - 0.10
            if i1 < i0:
                if b2 - a2 >= TAPA + 0.10: pos.append((a2 + b2) / 2)
                continue
            n = max(1, math.ceil((i1 - i0) / MAX_TAPAS))
            pos += [i0 + (i1 - i0) * k / n for k in range(n + 1)] if i1 - i0 > 0.5 else [(i0 + i1) / 2]
        for pe in e["empalmes"]:
            sN = ln.project(Point(pe))
            if _tap(e["tap"], sN) and all(abs(sN - p) > 2.0 for p in pos): pos.append(sN)
        for s in sorted(pos):
            p = ln.interpolate(s); q = ln.interpolate(min(L, s + 0.01)); o = ln.interpolate(max(0.0, s - 0.01))
            tapa(lam, (p.x, p.y), _u((o.x, o.y), (q.x, q.y))); ntapas += 1
    return ntapas


def escala_para(caja, ancho_mm=790.0, alto_mm=448.0):
    w, h = caja[2] - caja[0], caja[3] - caja[1]
    return next((e for e in ESCALAS if w / (e / 1000.0) <= ancho_mm and h / (e / 1000.0) <= alto_mm), ESCALAS[-1])


def dc01(doc, codigo, R, red, sitio, curvas, P, anchos, V, lloraderos, proyecto, techos=None, sums=None):
    ce = sitio.cerco; x0, y0, x1, y1 = ce.bounds
    caja = (x0 - 6, y0 - 6, x1 + 6, y1 + 6)
    esc = escala_para(caja); f = esc / 1000.0
    cx, cy = (caja[0] + caja[2]) / 2, (caja[1] + caja[3]) / 2
    ox, oy = cx - 430 * f, cy - 357 * f
    lam = B.Lamina(doc, ox, oy, esc, codigo, "PLANTA GENERAL DE CUNETAS",
                   "TRAZO, SENTIDO DE FLUJO, REJILLAS, TRAMOS TAPADOS, LLORADEROS Y DESCARGAS - COORDENADAS UTM WGS84")
    vx0, vy0 = lam.P(27, 130); vx1, vy1 = lam.P(831, 588)            # zona de dibujo (modelo)
    def dentro(pts): return any(vx0 <= p[0] <= vx1 and vy0 <= p[1] <= vy1 for p in pts)
    with EnBloque(lam, "ARQUITECTURA_BASE", "ARQ-TECHO"):
        for g, capa in ((sitio.veredas_plano, "ARQ-VEREDA"), (sitio.techos_plano, "ARQ-TECHO"), (sitio.muros, "ARQ-MURO")):
            for an in _anillos(g) if g is not None and not g.is_empty else []:
                if dentro(an): lam.poli(an, capa, cerrada=True)
    with EnBloque(lam, "CURVAS_DE_NIVEL", "CURVAS"):
        for z, L in curvas:
            pts = [p for p in L.coords if vx0 <= p[0] <= vx1 and vy0 <= p[1] <= vy1]
            if len(pts) < 2: continue
            lam.poli(pts, "CURVAS")
            if abs(z - round(z)) < 1e-6 and len(pts) > 20:
                for k in (len(pts) // 3, 2 * len(pts) // 3):
                    p, q = pts[k], pts[min(k + 2, len(pts) - 1)]
                    ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
                    if ang > 90: ang -= 180
                    if ang < -90: ang += 180
                    lam.texto(p, "%.0f" % z, 1.5, "CURVAS-TXT", TA.MIDDLE_CENTER, rot=ang)
    with EnBloque(lam, "LIMITE_DE_INTERVENCION", "LIMITE-INTERV"):
        lam.poli(list(ce.exterior.coords), "LIMITE-INTERV", cerrada=True, ancho=0.35 * f / 0.25)
    with EnBloque(lam, "CUNETAS", "CUN-REJ-BORDE"):
        ntapas = cunetas(lam, R, set(red.descargas), anchos, P)
    with EnBloque(lam, "LLORADEROS", "LLORADERO"):
        for q in lloraderos:
            x, y, nx, ny, ux, uy = q["x"], q["y"], q["nx"], q["ny"], q["ux"], q["uy"]
            lam.linea((x - nx * P["e_muro"], y - ny * P["e_muro"]), (x + nx * 0.05, y + ny * 0.05), "LLORADERO")
            c = [(x + nx * dn + ux * du, y + ny * dn + uy * du) for dn, du in ((0.0, -0.15), (0.30, -0.15), (0.30, 0.15), (0.0, 0.15))]
            lam.poli(c, "LLORADERO", cerrada=True)
    if techos:
        with EnBloque(lam, "CANALETAS_Y_MONTANTES", "CANALETA"):
            for l in techos["lados"]:
                lam.poli([tuple(c) for c in l["alero"]], "CANALETA", ancho=techos["criterios"]["parametros"]["canaleta_b"])
            tcp = techos["criterios"]["parametros"]
            for m in techos["montantes"]:
                montante(lam, m, tcp["fc_largo"], tcp["fc_ancho"])
                if m["hacia"]: lam.linea((m["x"], m["y"]), tuple(m["hacia"]), "MONTANTE-SALIDA")
    if sums and sums["sumideros"]:
        from . import sumideros as SMD
        with EnBloque(lam, "SUMIDEROS", "SUMIDERO"):
            SMD.dibujar(lam, sums)
    Nn = R["nudos"]; D = set(red.descargas)
    with EnBloque(lam, "ROTULOS_RED", "NUDOS"):
        E = Etiquetas(lam)
        empalmes = {r["nudos"][-1] for r in R["ramales"]}
        rotular = lambda n: n not in D and ("~" not in n or n in empalmes)
        for n, xy in Nn.items():
            if rotular(n): lam.circulo(tuple(xy), 0.30, "NUDOS")
        for r in R["ramales"]:
            pts = [tuple(Nn[n]) for n in r["nudos"]]
            i = max(range(len(pts) - 1), key=lambda k: math.dist(pts[k], pts[k + 1]))
            L = math.dist(pts[i], pts[i + 1]); ux, uy = _u(pts[i], pts[i + 1])
            c = (pts[i][0] + ux * L * 0.62, pts[i][1] + uy * L * 0.62)
            t0 = r["tramos"][0]; b = anchos.get((r["codigo"], t0["de"], t0["a"]), P["b_int"])
            E.poner((c[0] - uy * 0.8, c[1] + ux * 0.8), "%s (b %.2f)" % (r["codigo"], b), 2.0, "TEXTOS", color=5, d_mm=1.5)
        for n, xy in Nn.items():
            if rotular(n): E.poner(tuple(xy), n, 1.45, "TEXTOS", d_mm=1.6)
        for m in (techos or {}).get("montantes", []): E.poner((m["x"], m["y"]), m["montante"], 1.3, "TEXTOS", color=6, d_mm=1.4)
        for m in (sums or {}).get("sumideros", []): E.poner((m["x"], m["y"]), m["sumidero"], 1.4, "TEXTOS", color=1, d_mm=1.4)
        hechas = set()
        for r in sorted(R["ramales"], key=lambda r: -r["L"]):
            fin = r["nudos"][-1]
            if fin not in D or fin in hechas: continue
            hechas.add(fin)
            pts = [tuple(Nn[n]) for n in r["nudos"]]; a, b = pts[-2], pts[-1]; ux, uy = _u(a, b)
            q = (b[0] + ux * 4.0, b[1] + uy * 4.0)
            lam.poli([b, q], "DESCARGA", ancho=0.25); lam.flecha(b, (q[0] + ux * 0.8, q[1] + uy * 0.8), "DESCARGA", tam_mm=4.0)
            E.poner(q, fin, 3.0, "TITULOS", color=1, d_mm=1.5)
    lam.bloque("SIMB-NORTE", lam.P(800, 555))
    bs = sorted(set(anchos.values()))
    items = [("linea", "CUN-REJ-BORDE", "Cuneta con rejilla (%s)" % ", ".join("%.2f libre / %.2f total" % (b, b + 2 * P["e_muro"]) for b in bs)),
             ("linea", "CUN-TAP-BORDE", "Cuneta tapada: losa e = %.2f m" % P["e_tapa"]),
             ("rect", "CUN-TAPA-INSP", "Tapa de inspeccion 0.60 x 0.60 (%d und)" % ntapas),
             ("linea2", "CUN-FLUJO", "Sentido del flujo"),
             ("rect", "LLORADERO", "Lloradero PVC 3\" @ %.2f m con caja filtrante 0.30 x 0.30 (%d und)" % (P["llor_sep"], len(lloraderos))),
             ("linea2", "DESCARGA", "Descarga por el cerco (salida por gravedad)")] + ([
             ("linea2", "CANALETA", "Canaleta galvanizada %.2f x %.2f, S = 1 %% (%.1f m)" % (techos["criterios"]["parametros"]["canaleta_b"], techos["criterios"]["parametros"]["canaleta_h"], techos["metrado"]["canaleta_m"])),
             ("rect", "FALSA-COLUMNA", "Montante PVC 4\" en falsa columna 0.20 x 0.15 en la esquina, y su salida a la cuneta (%d und)" % techos["metrado"]["montantes_und"])] if techos else []) + ([
             ("rect", "SUMIDERO", "Sumidero 0.25 x 0.25 (caja 0.45) y tuberia PVC 4\" a la cuneta, solo en areas libres sin cobertura (%d und)" % sums["metrado"]["sumideros_und"])]
             if sums and sums["sumideros"] else []) + [
             ("linea", "CURVAS", "Curva de nivel"), ("linea", "ARQ-TECHO", "Proyeccion de techos"),
             ("linea", "ARQ-VEREDA", "Veredas y pisos (arquitectura)"), ("linea2", "LIMITE-INTERV", "Limite de intervencion = cerco perimetrico")]
    lam.leyenda2(30, 126, items, hmm=1.6, ancho_col=150, filas_col=7 if (sums and sums["sumideros"]) else (6 if techos else 5))
    est = {d["D"]: d for d in V["descargas"]}
    qd = {}
    for fl in V["hidraulica"]:
        if fl["a"] in D: qd[fl["a"]] = max(qd.get(fl["a"], 0), fl["Q_ls"])
    filas = [[k, "%.3f" % est[k]["cf"], "%.1f" % qd.get(k, 0), "terreno exterior bajo la C.F. a %.2f m del cerco" % est[k]["sale_a_m"]
              if est[k]["sale_a_m"] is not None else "REVISAR"] for k in sorted(est)]
    lam.tabla(345, 126, ["DESC.", "C.F.", "Q (l/s)", "SALIDA POR GRAVEDAD"], filas, [14, 18, 16, 90], hmm=1.5, alto_mm=4.6, titulo="DESCARGAS")
    niv = ("borde de cuneta %+.2f al ras del piso" % sitio.borde) if sitio.borde is not None else "borde de cuneta al nivel del terreno"
    lam.notas(30, 68 if (sums and sums["sumideros"]) else (74 if techos else 78), "CRITERIOS", [
        "1. Cuneta rectangular de concreto: muros y losa de fondo de %.2f m; ancho libre de %.2f a %.2f m de 5 en 5 cm segun el caudal; una sola medida por sector (descarga)." % (P["e_muro"], P["b_int"], P.get("b_max", P["b_int"])),
        "2. Profundidad libre al inicio de cada eje %.2f m; cota de fondo con pendiente minima de %.1f %%; %s." % (P["h0"], 100 * P["S0"], niv),
        "3. Rejilla metalica en tramos abiertos; losa tapa de %.2f m en cruces de vereda e ingresos, con tapas de inspeccion 0.60 x 0.60 a %.0f m como maximo." % (P["e_tapa"], MAX_TAPAS),
        "4. Toda la red dentro del cerco; el agua sale por gravedad por un pase en el cimiento; ninguna cuneta queda enterrada.",
        "5. Lloraderos solo en el muro que da a area verde. Perfiles, secciones y cuadros en las laminas siguientes."], hmm=1.45, ancho_mm=600)
    return lam


def _tabla_partida(lam, x, ytop, ybot, cab, filas, anchos, titulo, hmm=1.9, alto=5.6):
    """Tabla en una o mas columnas si no entra en el alto disponible. Devuelve x final."""
    por_col = max(1, int((ytop - ybot) / alto) - 2)
    W = sum(anchos)
    for k in range(0, max(1, len(filas)), por_col):
        lam.tabla(x, ytop, cab, filas[k:k + por_col], anchos, hmm=hmm, alto_mm=alto, titulo=titulo if k == 0 else titulo + " (cont.)")
        x += W + 8
    return x


def dc02(doc, codigo, ox, oy, secciones, V, LLt, P, techos=None, sums=None):
    lam = B.Lamina(doc, ox, oy, 50, codigo, "CUADROS DE EJES, DESCARGAS Y LLORADEROS",
                   "SECCION ADOPTADA, CAUDAL, PROFUNDIDADES Y EXCAVACION POR EJE; TRAMOS CON LLORADEROS", escala_txt="S/E")
    filas = [[s["sector"], s["eje"], "%.2f" % s["L_m"], "%.1f" % s["Q_max_ls"], "%.2f" % s["b"], "%.2f" % (s["b"] + 2 * P["e_muro"]),
              "%.2f" % s["h_min"], "%.2f" % s["h_max"], "%.2f" % s["excavacion_max"]] for s in secciones]
    x = _tabla_partida(lam, 30, 575, 135, ["SECTOR", "EJE", "L (m)", "Q MAX (l/s)", "b LIBRE", "TOTAL", "h MIN", "h MAX", "EXCAV."],
                       filas, [20, 22, 20, 25, 20, 20, 19, 19, 20], "CUADRO DE EJES (medidas en m)")
    # descargas: ejes y caudal que sale
    por = {}
    for s in secciones: por.setdefault(s["sector"], []).append(s)
    qd = {}
    for fl in V["hidraulica"]:
        if fl["a"] == fl["sector"]: qd[fl["sector"]] = max(qd.get(fl["sector"], 0), fl["Q_ls"])
    est = {d["D"]: d for d in V["descargas"]}
    fd = [[k, len(v), "%.1f" % sum(s["L_m"] for s in v), "%.1f" % qd.get(k, 0), "%.3f" % est[k]["cf"] if k in est else "-",
           "%.2f" % v[0]["b"]] for k, v in sorted(por.items())]
    y = lam.tabla(x + 2, 575, ["DESC.", "EJES", "L (m)", "Q (l/s)", "C.F.", "b LIBRE"], fd, [18, 15, 20, 20, 22, 20], hmm=1.9, alto_mm=5.6,
                  titulo="DESCARGAS")
    fl = [[i + 1, t["eje"], "%s-%s" % (t["de"], t["a"]), t["lado"].upper(), "%.2f" % t["prog_desde"], "%.2f" % t["prog_hasta"], "%.2f" % t["L_m"], t["n"]]
          for i, t in enumerate(LLt)]
    if fl: fl.append(["", "TOTAL", "", "", "", "", "%.2f" % sum(t["L_m"] for t in LLt), sum(t["n"] for t in LLt)])
    xt = _tabla_partida(lam, x + 2, y - 14, 135, ["N.", "EJE", "TRAMO", "LADO", "DESDE", "HASTA", "L (m)", "N. LLOR."],
                   fl, [11, 20, 32, 25, 20, 20, 18, 18], "LLORADEROS (muro junto a area verde, @ %.2f m)" % P["llor_sep"])
    if techos:
        ft = [[l["techo"], l["lado"].replace("Lado ", ""), "%.1f" % l["A_m2"], "%.2f" % l["L_canaleta_m"], "%.2f" % l["Q_ls"], l["montantes"],
               "%.3f" % l["tirante_m"], ", ".join(dict.fromkeys(x["cuneta"].replace("SIN CUNETA CERCANA", "SIN CUNETA") for x in techos["montantes"] if x["montante"] in l["ids"]))[:24]]
              for l in techos["lados"]]
        m = techos["metrado"]
        ft.append(["TOTAL", "", "", "%.2f" % m["canaleta_m"], "", m["montantes_und"], "", ""])
        xt = _tabla_partida(lam, xt, 575, 135, ["TECHO", "LADO", "AREA (m2)", "CANALETA (m)", "Q (l/s)", "MONT.", "TIRANTE", "DESCARGA A"],
                       ft, [16, 11, 18, 20, 16, 12, 16, 34], "CANALETAS Y MONTANTES PVC 4\" POR TECHO")
    if sums and sums["sumideros"]:
        fs = [[x["sumidero"], "%.1f" % x["A_m2"], "%.2f" % x["Q_ls"], x["cuneta"], "%.2f" % x["L_tubo_m"], "%.3f" % x["z_llegada"], "%.3f" % x["cf_cuneta"]]
              for x in sums["sumideros"]]
        fs.append(["TOTAL", "", "", "", "%.2f" % sums["metrado"]["tuberia_4_m"], "", ""])
        _tabla_partida(lam, xt, 575, 135, ["SUMIDERO", "AREA (m2)", "Q (l/s)", "CUNETA", "TUBO 4\" (m)", "LLEGADA", "C.F."],
                       fs, [18, 16, 14, 16, 18, 18, 18], "SUMIDEROS (areas libres)")
    lam.notas(30, 120, "NOTAS", [
        "1. b LIBRE = ancho libre interior; TOTAL = b + 2 muros de %.2f m; h = altura libre (de la cota de fondo al borde); EXCAV. = h + losa de fondo %.2f + solado %.2f." % (P["e_muro"], P["e_fondo"], P["e_solado"]),
        "2. Una sola medida por sector (ejes que salen por la misma descarga): la mayor que pide cualquiera de sus tramos.",
        "3. Lloraderos: tubo PVC 3\" a media altura del muro, con caja filtrante de 0.30 x 0.30 de grava envuelta en geotextil; N. = REDONDEAR.MAS(L / %.2f)." % P["llor_sep"]] + ([
        "4. Canaletas galvanizadas S = 1 %%, Manning n = 0.013, borde libre 0.05 m; montantes PVC 4\" por Wyly-Eaton (rs = 0.25): un montante atiende %.1f m2 de techo; salida PVC a la cuneta mas cercana." % techos["criterios"]["A_por_montante_4_m2"]] if techos else []),
        hmm=1.5, ancho_mm=600)
    return lam
