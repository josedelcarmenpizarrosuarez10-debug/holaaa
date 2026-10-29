"""Planos DXF del drenaje vial (PLANOS_DRENAJE_VIAL.dxf), a escala real (1 unidad = 1 m), con vista previa PNG de cada lámina.

VD-01..  Diagrama de drenaje: eje de la vía por progresivas con cunetas, alcantarillas de alivio y de paso y badenes.
VD-..    Secciones típicas de cuneta (1/20), con su revestimiento, berma de recepción y talud de corte.
VD-..    Alcantarillas típicas (1/50): perfil longitudinal con cabezales, cama, relleno y protección de piedra; elevación del cabezal.
VD-..    Badenes (1/50) y cuadro de obras de arte y drenaje.
Las medidas que el MTC deja sin valor (cabezal, cama, protección) son las típicas editables de la biblioteca (criterio del proyectista).
"""
import math

from ezdxf.enums import TextEntityAlignment as TA
from shapely.geometry import LineString

from . import dxf_base as B, normas, render
from .vial import progresiva

W, H = B.Lamina.A1
ZONA = (35.0, 120.0, 826.0, 580.0)          # zona de dibujo libre del rótulo (mm de papel)


def _v(clave):
    return float(normas.dato(clave)["valor"])


def _txt_sec(s):
    if s["tipo"] == "triangular": return "TRIANGULAR d = %.2f m, a = %.2f m" % (s["d"], float(s["a"]))
    if s["tipo"] == "trapezoidal": return "TRAPEZOIDAL b = %.2f m, d = %.2f m" % (s["b"], s["d"])
    return "RECTANGULAR b = %.2f m, d = %.2f m" % (s["b"], s["d"])


def _clave_sec(c):
    s = c["seccion"]
    return (s["tipo"], round(s["d"], 3), round(float(s.get("a") or s.get("b") or 0), 3), round(s.get("z2", 0), 3), c["revestimiento"])


# ------------------------------------------------------------------------------------------------ diagrama
def diagrama(doc, R, ox, oy, codigo):
    """Diagrama de drenaje en franjas por progresiva. Devuelve las láminas dibujadas [(codigo, ox, oy)]."""
    obras = [(c["prog_ini"], c["prog_fin"]) for c in R["cunetas"]] + [(a["prog"], a["prog"]) for a in R["alcantarillas"] + R["badenes"]]
    p0 = math.floor(min(a for a, _ in obras) / 100.0) * 100; p1 = math.ceil(max(b for _, b in obras) / 100.0) * 100
    largo = max(100.0, p1 - p0)
    ancho = 760.0                                            # mm de papel por franja
    esc = next((e for e in (500, 1000, 2000, 2500, 5000, 10000) if largo / (e / 1000.0) <= 3 * ancho), 10000)
    por_franja = ancho * esc / 1000.0
    franjas = [(p0 + k * por_franja, min(p1, p0 + (k + 1) * por_franja)) for k in range(int(math.ceil(largo / por_franja - 1e-9)))]
    out = []
    for i in range(0, len(franjas), 3):
        n = len(out); lam = B.Lamina(doc, ox + n * (W + 60) * esc / 1000.0, oy, esc, "%s-%02d" % (codigo, n + 1) if len(franjas) > 3 else codigo,
                                     "DIAGRAMA DE DRENAJE DE LA VÍA", "CUNETAS, ALCANTARILLAS Y BADENES POR PROGRESIVA")
        grupo = franjas[i:i + 3]
        for k, (a, b) in enumerate(grupo):
            ymm = 520 - k * (330 / max(1, len(grupo) - 1) if len(grupo) > 1 else 0)
            _franja(lam, R, a, b, 40.0, ymm)
        lam.leyenda(40, 125, [("linea", "EJE-COLECTOR", "Eje de la vía"), ("linea", "CUNETA", "Cuneta (flecha: sentido del flujo)"),
                              ("linea", "CORTES", "Alcantarilla de paso de quebrada"), ("linea", "FLUJO", "Alcantarilla de alivio"),
                              ("linea", "POZA", "Badén")])
        out.append((lam.codigo, lam.ox, lam.oy, esc))
    return out


def _franja(lam, R, a, b, xmm, ymm):
    f = lam.f
    X = lambda p: lam.ox + xmm * f + (p - a)                  # progresiva -> x del modelo (escala real)
    y0 = lam.oy + ymm * f
    lam.linea((X(a), y0), (X(b), y0), "EJE-COLECTOR")
    paso = 100 if (b - a) / 100 <= 40 else 500
    p = math.ceil(a / paso) * paso
    while p <= b + 1e-6:
        lam.linea((X(p), y0 - 2 * f), (X(p), y0 + 2 * f), "PROGRESIVAS")
        lam.texto((X(p), y0 - 4.5 * f), progresiva(p)[:-3], 1.8, "PROGRESIVAS", TA.TOP_CENTER)
        p += paso
    dy = {"izquierdo": 12.0, "derecho": -12.0}
    for c in R["cunetas"]:
        s, e = max(a, c["prog_ini"]), min(b, c["prog_fin"])
        if e <= s: continue
        yc = y0 + dy.get(c["lado"], 12.0) * f
        lam.poli([(X(s), yc), (X(e), yc)], "CUNETA", ancho=0.6 * f)
        for t in c["tramos"]:
            ts, te = max(s, t["desde"]), min(e, t["hasta"])
            if te - ts < 6 * f: continue
            m = (ts + te) / 2; sg = 1 if t["descarga_en"] >= t["hasta"] - 1e-6 else -1
            lam.flecha((X(m - sg * 3 * f), yc), (X(m + sg * 3 * f), yc), "FLUJO", 2.0)
        lam.texto((X(s) + 1 * f, yc + (2.0 if dy.get(c["lado"], 12) > 0 else -2.0) * f), "%s  %s" % (c["id"], _txt_sec(c["seccion"])), 1.6, "TEXTOS",
                  TA.BOTTOM_LEFT if dy.get(c["lado"], 12) > 0 else TA.TOP_LEFT)
    k = 0
    for o in sorted(R["alcantarillas"] + R["badenes"], key=lambda o: o["prog"]):
        if not (a - 1e-6 <= o["prog"] <= b + 1e-6): continue
        x = X(o["prog"]); es_b = "conducto" not in o
        capa = "POZA" if es_b else ("FLUJO" if o["tipo"] == "alivio" else "CORTES")
        if es_b: lam.poli([(x - 2 * f, y0 + 16 * f), (x - 1 * f, y0 - 16 * f), (x + 1 * f, y0 - 16 * f), (x + 2 * f, y0 + 16 * f)], capa, cerrada=True)
        else:
            lam.poli([(x, y0 + 16 * f), (x, y0 - 16 * f)], capa, ancho=(0.9 if o["tipo"] != "alivio" else 0.5) * f)
            lam.circulo((x, y0 - 16 * f), 1.0 * f, capa)
        alto = 20 + 9 * (k % 3); k += 1
        txt = "%s %s  %s" % (o["id"], progresiva(o["prog"]), "BADÉN" if es_b else o["conducto"])
        lam.linea((x, y0 + 16 * f), (x, y0 + alto * f), "LLAMADAS")
        lam.texto((x + 0.8 * f, y0 + alto * f), txt, 1.7, "TEXTOS", TA.BOTTOM_LEFT)
    lam.texto((lam.ox + xmm * f, y0 + 48 * f), "DE %s A %s" % (progresiva(a), progresiva(b)), 2.6, "TITULOS")


# ------------------------------------------------------------------------------------------------ secciones de cuneta
def _perfil_cuneta(s):
    d = s["d"]
    if s["tipo"] == "triangular": return [(0, 0), (s["z1"] * d, -d), (s["z1"] * d + s["z2"] * d, 0)]
    if s["tipo"] == "trapezoidal": return [(0, 0), (s["z1"] * d, -d), (s["z1"] * d + s["b"], -d), (s["z1"] * d + s["b"] + s["z2"] * d, 0)]
    return [(0, 0), (0, -d), (s["b"], -d), (s["b"], 0)]


def seccion_cuneta(lam, c, ids, xmm, ymm, tipo=1):
    """Sección típica a escala real con origen en el borde de la rasante (xmm, ymm del papel)."""
    s = c["seccion"]; f = lam.f; ox, oy = lam.P(xmm, ymm)
    T = lambda p: (ox + p[0], oy + p[1])
    e = float(str(normas.dato("vial_cuneta_revestimiento")["valor"]).split("e = ")[1].split(" ")[0]) if c["revestimiento"] == "concreto" else 0.0
    pts = _perfil_cuneta(s); xe = pts[-1][0]; berma = _v("vial_cuneta_berma"); zc = s.get("z2", 0.5) or 0.5
    # calzada, berma de recepción y talud de corte
    lam.poli([T((-1.6, 0)), T((0, 0))], "VIA", ancho=0.4 * f)
    lam.texto(T((-0.8, 0.06)), "CALZADA / BERMA", 1.8, "TEXTOS", TA.BOTTOM_CENTER)
    lam.poli([T((xe, 0)), T((xe + berma, 0)), T((xe + berma + zc * 1.0, 1.0))], "TERRENO")
    lam.texto(T((xe + berma / 2, 0.06)), "BERMA %.2f" % berma, 1.6, "TEXTOS", TA.BOTTOM_CENTER)
    lam.texto(T((xe + berma + zc * 0.5 + 0.08, 0.5)), "TALUD DE CORTE 1:%g" % zc, 1.6, "TEXTOS", TA.MIDDLE_LEFT)
    if e > 0:
        off = list(LineString(pts).offset_curve(-e).coords)
        poly = [T(p) for p in pts] + [T(p) for p in reversed(off)]
        lam.relleno(poly, "CONCRETO-ACHURADO"); lam.poli(poly, "CONCRETO", cerrada=True)
    lam.poli([T(p) for p in pts], "CUNETA")
    yc = max(t["tirante"] or 0 for t in c["tramos"]) - s["d"]   # nivel del agua del mayor caudal de diseño
    ag = LineString([(-1, yc), (xe + 1, yc)]).intersection(LineString(pts))
    xs = sorted(p.x for p in getattr(ag, "geoms", [ag]) if hasattr(p, "x"))
    if len(xs) >= 2:
        lam.linea(T((xs[0], yc)), T((xs[-1], yc)), "AGUA"); lam.bloque("SIMB-AGUA", T(((xs[0] + xs[-1]) / 2, yc)), capa="AGUA-SIMBOLO")
    # cotas
    if s["tipo"] == "triangular":
        lam.cota(T((0, 0)), T((pts[1][0], 0)), 10, texto="a = %.2f" % float(s["a"]))
        lam.cota(T((pts[1][0], -s["d"])), T((pts[1][0], 0)), -8, horizontal=False, texto="d = %.2f" % s["d"])
        lam.texto(T((pts[1][0] / 2 - 0.05, -s["d"] / 2)), "1:%g" % round(s["z1"], 2), 1.6, "TEXTOS", TA.MIDDLE_RIGHT)
        lam.texto(T((pts[1][0] + s["z2"] * s["d"] / 2 + 0.06, -s["d"] / 2)), "1:%g" % round(s["z2"], 2), 1.6, "TEXTOS", TA.MIDDLE_LEFT)
    else:
        lam.cota(T((pts[1][0], -s["d"])), T((pts[2][0], -s["d"])), -8, texto="b = %.2f" % s.get("b", 0))
        lam.cota(T((pts[0][0], -s["d"])), T((pts[0][0], 0)), -8, horizontal=False, texto="d = %.2f" % s["d"])
    lam.cota(T((xe, 0)), T((xe + berma, 0)), 16, texto="%.2f" % berma)
    if e > 0:
        lam.llamada(T(((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2 - e)), T((pts[1][0] - 0.2, -s["d"] - 0.35)),
                    ["CONCRETO f'c = 175 kg/cm²", "e = %.3f m" % e], 1.7, al=TA.RIGHT)
    lam.titulo_vista(xmm + (xe / 2) / f, ymm - (s["d"] + 0.75) / f, "SECCIÓN TÍPICA DE CUNETA – TIPO %d" % tipo,
                     "%s · %s · ESC. 1/%d" % (", ".join(ids), _txt_sec(s), lam.esc), ancho_mm=110)


def laminas_cunetas(doc, R, ox, oy, codigo):
    grupos = {}
    for c in R["cunetas"]: grupos.setdefault(_clave_sec(c), []).append(c)
    out = []; lista = list(grupos.values())
    esc = 10 if len(lista) == 1 else 20                      # una sola sección: a 1/10, más grande
    for n in range(0, len(lista), 4):
        lam = B.Lamina(doc, ox + len(out) * (W + 60) * esc / 1000.0, oy, esc, "%s-%02d" % (codigo, len(out) + 1) if len(lista) > 4 else codigo,
                       "SECCIONES TÍPICAS DE CUNETAS", "REVESTIMIENTO, BERMA DE RECEPCIÓN Y TALUD DE CORTE")
        for k, g in enumerate(lista[n:n + 4]):
            if esc == 10: seccion_cuneta(lam, g[0], [c["id"] for c in g], 230, 420, n + k + 1)
            else: seccion_cuneta(lam, g[0], [c["id"] for c in g], 140 + (k % 2) * 330, 470 - (k // 2) * 200, n + k + 1)
        lam.notas(40, 160, "NOTAS", [
            "1. Medidas en metros. Ancho «a» desde el borde de la rasante hasta la vertical del vértice; profundidad «d» desde el borde de la rasante (MTC, Figura N.° 27).",
            "2. Revestimiento de concreto f'c = 175 kg/cm², e = 0.075 m (MTC, numeral 4.1.2.1 e). Juntas %s." % normas.dato("vial_cuneta_junta")["valor"],
            "3. Berma exterior de recepción de 0.60 m entre la cuneta y el pie del talud de corte (MTC, numeral 4.1.2.1 c).",
            "4. Nivel de agua dibujado: tirante con la capacidad de diseño. Mantenimiento antes y después del período de lluvias."], ancho_mm=590)
        out.append((lam.codigo, lam.ox, lam.oy, esc))
    return out


# ------------------------------------------------------------------------------------------------ alcantarillas
def _tipo_alc(a):
    s = a["seccion"]
    return (s["tipo"], round(s.get("D") or s.get("h"), 3), round(s.get("b", 0), 3), s.get("celdas", 1))


def alcantarilla_tipica(lam, a, ids, xmm, ymm):
    s = a["seccion"]; f = lam.f
    D = s.get("D") or s["h"]; circ = s["tipo"] == "circular"; nc = s.get("celdas", 1)
    L = a["longitud"] or 8.0; S = a["pendiente"]
    t = _v("vial_cab_espesor"); sc = _v("vial_cab_sobre_clave"); cim = _v("vial_cab_cimiento"); cama = _v("vial_cama"); rel = _v("vial_relleno_min")
    Lp = max(1.5, 1.5 * D); ep = 0.30
    ox, oy = lam.P(xmm, ymm)
    T = lambda x, z: (ox + x, oy + z)
    zi = lambda x: -S * x                                       # cota de fondo relativa (entrada = 0)
    # tubo o marco
    lam.poli([T(0, zi(0)), T(L, zi(L))], "CONCRETO" if not circ else "CUNETA", ancho=0.3 * f)
    lam.poli([T(0, zi(0) + D), T(L, zi(L) + D)], "CONCRETO" if not circ else "CUNETA", ancho=0.3 * f)
    y = a["tirante"]
    lam.linea(T(0, zi(0) + y), T(L, zi(L) + y), "AGUA")
    lam.flecha(T(L * 0.45, zi(L * 0.45) + y * 0.5), T(L * 0.55, zi(L * 0.55) + y * 0.5), "FLUJO", 2.5)
    # cama de apoyo
    poly = [T(0, zi(0)), T(L, zi(L)), T(L, zi(L) - cama), T(0, zi(0) - cama)]
    lam.achurado(poly, "TERRENO-ACHURADO", "AR-SAND", 0.4); lam.poli(poly, "RELLENO", cerrada=True)
    # cabezales
    for x0, x1 in ((-t, 0), (L, L + t)):
        xm = (x0 + x1) / 2
        z0, z1 = zi(max(0, min(L, xm))) - cim, zi(max(0, min(L, xm))) + D + sc
        pts = [T(x0, z0), T(x1, z0), T(x1, z1), T(x0, z1)]
        lam.relleno(pts, "CONCRETO-ACHURADO"); lam.poli(pts, "CONCRETO", cerrada=True)
    # relleno y rasante
    zr = D + max(rel, 0.60)
    zc1 = zi(0) + D + sc; zc2 = zi(L) + D + sc
    talud = 1.5
    xa = (zr - zc1) * talud; xb = L - (zr - zc2) * talud
    if xb > xa:
        lam.poli([T(0, zc1), T(xa, zr), T(xb, zr), T(L, zc2)], "TERRENO", ancho=0.25 * f)
        lam.texto(T((xa + xb) / 2, zr + 0.08), "RASANTE", 1.8, "TEXTOS", TA.BOTTOM_CENTER)
    else:
        lam.poli([T(0, zc1), T(L, zc2)], "TERRENO")
    # protección de piedra a la entrada y a la salida, con uña
    for xs, xe, z in ((-t - Lp, -t, zi(0)), (L + t, L + t + Lp, zi(L))):
        pts = [T(xs, z), T(xe, z), T(xe, z - ep), T(xs, z - ep)]
        lam.achurado(pts, "TERRENO-ACHURADO", "GRAVEL", 0.5); lam.poli(pts, "POZA", cerrada=True)
        xu = xs if xs < 0 else xe - 0.3
        lam.poli([T(xu, z - ep), T(xu + 0.3, z - ep), T(xu + 0.3, z - ep - 0.5), T(xu, z - ep - 0.5)], "POZA", cerrada=True)
        lam.poli([T(xs - 1.0 if xs < 0 else xe, z), T(xs if xs < 0 else xe + 1.0, z)], "TERRENO-EXISTENTE")
    # cotas y llamadas
    lam.cota(T(0, zi(0) - cim - 0.2), T(L, zi(L) - cim - 0.2), -10, texto="L = %.2f" % L, angulo=math.degrees(math.atan(-S)))
    lam.cota(T(-t, zi(0)), T(-t, zi(0) + D), -14, horizontal=False, texto="%s = %.3f" % ("D" if circ else "h", D))
    lam.cota(T(L + t + Lp, zi(L)), T(L + t, zi(L)), 10, texto="%.2f" % Lp)
    lam.llamada(T(L * 0.25, zi(L * 0.25) - cama / 2), T(L * 0.25, zi(L * 0.25) - cim - 1.4),
                ["CAMA DE GRAVA ARENOSA e = %.2f m" % cama], 1.8)
    lam.llamada(T(L + t + Lp / 2, zi(L) - ep / 2), T(L + t + Lp * 0.6, zi(L) - 1.4),
                ["PIEDRA EMBOQUILLADA e = %.2f m" % ep, "d50 ≥ %.2f m (V = %.2f m/s)" % (a["d50_salida"], a["V"])], 1.8)
    lam.llamada(T(L + t / 2, zi(L) + D + sc), T(L + t + 0.6, zi(L) + D + sc + 1.0), ["CABEZAL DE CONCRETO f'c = 210 kg/cm²", "e = %.2f m" % t], 1.8)
    lam.texto(T(L * 0.5, zi(L * 0.5) + D + 0.15), "%s · S = %.1f %%" % (a["conducto"], 100 * S), 2.0, "TEXTOS", TA.BOTTOM_CENTER)
    lam.titulo_vista(xmm + (L / 2) / f, ymm - (cim + 2.6) / f, "PERFIL LONGITUDINAL – %s" % a["conducto"].upper(),
                     "%s · ESC. 1/%d" % (", ".join(ids), lam.esc), ancho_mm=120)
    # elevación del cabezal (aguas abajo)
    sep = max(0.40, min(1.00, D / 2)) if circ else 0.30
    ancho = nc * (D if circ else s["b"]) + (nc - 1) * sep + 2 * 0.60
    ex = ox + L + t + Lp + 3.0 + 1.5; ez = oy + zi(L)
    E = lambda x, z: (ex + x, ez + z)
    hcab = D + sc
    wall = [E(0, -cim), E(ancho, -cim), E(ancho, hcab), E(0, hcab)]
    lam.relleno(wall, "CONCRETO-ACHURADO"); lam.poli(wall, "CONCRETO", cerrada=True)
    for lado in (-1, 1):
        x0 = 0 if lado < 0 else ancho
        ala = [E(x0, -cim), E(x0 + lado * 1.2, -cim), E(x0 + lado * 1.2, 0.30), E(x0, hcab)]
        lam.relleno(ala, "CONCRETO-ACHURADO"); lam.poli(ala, "CONCRETO", cerrada=True)
    x = 0.60
    for _ in range(nc):
        if circ:
            lam.circulo(E(x + D / 2, D / 2), D / 2, "CUNETA")
            x += D + sep
        else:
            lam.rect(*E(x, 0), *E(x + s["b"], D), "CUNETA"); x += s["b"] + sep
    lam.linea(E(-2.0, 0), E(ancho + 2.0, 0), "TERRENO-EXISTENTE")
    lam.cota(E(0, hcab), E(ancho, hcab), 8, texto="%.2f" % ancho)
    lam.cota(E(ancho + 1.2, -cim), E(ancho + 1.2, hcab), 8, horizontal=False, texto="%.2f" % (hcab + cim))
    lam.titulo_vista((ex + ancho / 2 - lam.ox) / f, (ez - cim - 1.0 - lam.oy) / f, "ELEVACIÓN DEL CABEZAL", "ESC. 1/%d" % lam.esc, ancho_mm=70)


def laminas_alcantarillas(doc, R, ox, oy, codigo):
    grupos = {}
    for a in R["alcantarillas"]: grupos.setdefault(_tipo_alc(a), []).append(a)
    out = []; lista = sorted(grupos.values(), key=lambda g: _tipo_alc(g[0]))
    for n in range(0, len(lista), 2):
        lam = B.Lamina(doc, ox + len(out) * (W + 60) * 0.05, oy, 50, "%s-%02d" % (codigo, len(out) + 1) if len(lista) > 2 else codigo,
                       "ALCANTARILLAS TÍPICAS", "PERFIL LONGITUDINAL Y ELEVACIÓN DEL CABEZAL")
        for k, g in enumerate(lista[n:n + 2]):
            a = max(g, key=lambda x: x["longitud"] or 0)
            alcantarilla_tipica(lam, a, [x["id"] for x in g], 120, 470 - k * 200)
        lam.notas(40, 140, "NOTAS", [
            "1. Medidas en metros. Cabezal, cama, relleno mínimo y protección: medidas típicas editables (criterio del proyectista; la Lámina N.° 02 del MTC no las fija).",
            "2. Tirante de diseño ≤ 75 % de la altura (borde libre del 25 %, MTC 4.1.1.3.7 b). Protección a la salida con d50 ≥ V²/(3.1 g) (ecuación 49).",
            "3. Relleno mínimo sobre la clave %.2f m: confirmar con el fabricante de la TMC según la carga vehicular y el calibre." % _v("vial_relleno_min")],
            ancho_mm=590)
        out.append((lam.codigo, lam.ox, lam.oy, 50))
    return out


# ------------------------------------------------------------------------------------------------ badenes y cuadro
def lamina_badenes(doc, R, ox, oy, codigo):
    out = []
    for n in range(0, len(R["badenes"]), 2):
        lam = B.Lamina(doc, ox + len(out) * (W + 60) * 0.05, oy, 50, "%s-%02d" % (codigo, len(out) + 1) if len(R["badenes"]) > 2 else codigo,
                       "BADENES", "SECCIÓN TRANSVERSAL AL FLUJO (a lo largo del eje de la vía)")
        for k, b in enumerate(R["badenes"][n:n + 2]):
            s = b["seccion"]; hz = b["profundidad"]; z = s["z1"]
            ox_, oy_ = lam.P(80, 460 - k * 200)
            T = lambda x, y: (ox_ + x, oy_ + y)
            pts = [(0, hz), (z * hz, 0), (z * hz + s["b"], 0), (2 * z * hz + s["b"], hz)]
            off = list(LineString(pts).offset_curve(-0.20).coords)
            poly = [T(*p) for p in pts] + [T(*p) for p in reversed(off)]
            lam.relleno(poly, "CONCRETO-ACHURADO"); lam.poli(poly, "CONCRETO", cerrada=True)
            lam.poli([T(-2, hz), T(0, hz)], "VIA", ancho=0.4 * lam.f); lam.poli([T(2 * z * hz + s["b"], hz), T(2 * z * hz + s["b"] + 2, hz)], "VIA", ancho=0.4 * lam.f)
            if b["tirante"]:
                y = b["tirante"]; lam.linea(T(z * hz - z * y, y), T(z * hz + s["b"] + z * y, y), "AGUA")
                lam.bloque("SIMB-AGUA", T(z * hz + s["b"] / 2, y), capa="AGUA-SIMBOLO")
                lam.cota(T(2 * z * hz + s["b"] + 2, y), T(2 * z * hz + s["b"] + 2, hz), 6, horizontal=False, texto="BL = %.2f" % b["borde_libre"])
            lam.cota(T(z * hz, 0), T(z * hz + s["b"], 0), -10, texto="b = %.2f" % s["b"])
            lam.cota(T(0, 0), T(0, hz), -10, horizontal=False, texto="h = %.2f" % hz)
            lam.texto(T(z * hz / 2 - 0.3, hz / 2), "1:%g" % z, 1.8, "TEXTOS", TA.MIDDLE_RIGHT)
            lam.titulo_vista(80 + (z * hz + s["b"] / 2) / lam.f, 460 - k * 200 - 22, "%s – BADÉN %s" % (b["id"], progresiva(b["prog"])),
                             "Q = %.2f m³/s · pendiente transversal %.1f %% · losa de concreto e = 0.20 m · ESC. 1/%d" % (b["Q"], 100 * b["pendiente_transversal"], lam.esc), ancho_mm=130)
        lam.notas(40, 140, "NOTAS", ["1. Medidas en metros. Borde libre de 0.30 a 0.50 m y pendiente transversal de 2 a 3 % (MTC, numeral 4.1.1.4.1).",
                                     "2. Uñas de cimentación y protección contra la socavación a la entrada y a la salida, y losas de aproximación (MTC 4.1.1.4).",
                                     "3. Espesor de la losa: medida típica editable."], ancho_mm=590)
        out.append((lam.codigo, lam.ox, lam.oy, 50))
    return out


def lamina_cuadro(doc, R, ox, oy, codigo):
    lam = B.Lamina(doc, ox, oy, 100, codigo, "CUADRO DE OBRAS DE ARTE Y DRENAJE", "CUNETAS, ALCANTARILLAS Y BADENES", escala_txt="S/E")
    y = lam.tabla(35, 560, ["CUNETA", "LADO", "DESDE", "HASTA", "L (m)", "S (%)", "SECCIÓN", "REVEST.", "Q MÁX. (m³/s)", "V MÁX. (m/s)", "DESCARGAS EN"],
                  [[c["id"], c["lado"].upper(), progresiva(c["prog_ini"]), progresiva(c["prog_fin"]), "%.2f" % c["longitud"], "%.2f" % (100 * c["pendiente"]),
                    _txt_sec(c["seccion"]), c["revestimiento"].upper(), "%.3f" % max(t["Q"] for t in c["tramos"]), "%.2f" % max(t["V"] or 0 for t in c["tramos"]),
                    ", ".join(progresiva(t["descarga_en"]) for t in c["tramos"])] for c in R["cunetas"]],
                  [30, 30, 34, 34, 24, 20, 96, 30, 34, 32, 150], hmm=2.4, alto_mm=6.5, titulo="CUADRO DE CUNETAS")
    y = lam.tabla(35, y - 18, ["OBRA", "PROGRESIVA", "TIPO", "SECCIÓN", "L (m)", "S (%)", "Q (m³/s)", "y/D", "V (m/s)", "d50 SALIDA (m)", "T (años)", "ESTADO"],
                  [[a["id"], progresiva(a["prog"]), "ALIVIO" if a["tipo"] == "alivio" else "PASO DE QUEBRADA", a["conducto"].upper(),
                    "%.2f" % (a["longitud"] or 0), "%.1f" % (100 * a["pendiente"]), "%.3f" % a["Q"], "%.2f" % a["tirante_rel"], "%.2f" % a["V"],
                    "%.2f" % a["d50_salida"], a["periodo"]["T"], a["estado"]] for a in R["alcantarillas"]],
                  [28, 36, 50, 62, 22, 22, 30, 22, 26, 36, 26, 34], hmm=2.4, alto_mm=6.5, titulo="CUADRO DE ALCANTARILLAS")
    if R["badenes"]:
        lam.tabla(35, y - 18, ["OBRA", "PROGRESIVA", "SECCIÓN", "Q (m³/s)", "TIRANTE (m)", "BORDE LIBRE (m)", "ESTADO"],
                  [[b["id"], progresiva(b["prog"]), "b = %.2f, z = %g, h = %.2f" % (b["seccion"]["b"], b["seccion"]["z1"], b["profundidad"]),
                    "%.3f" % b["Q"], "%.3f" % (b["tirante"] or 0), "%.2f" % (b["borde_libre"] or 0), b["estado"]] for b in R["badenes"]],
                  [28, 36, 84, 30, 34, 40, 34], hmm=2.4, alto_mm=6.5, titulo="CUADRO DE BADENES")
    return [(lam.codigo, lam.ox, lam.oy, 100)]


# ------------------------------------------------------------------------------------------------ juego completo
def planos(R, ruta_dxf, carpeta_png=None):
    from . import planos as PL
    PL.rotulo_de({**R["proyecto"], "especialidad": "DRENAJE VIAL"})
    doc = B.nuevo_documento(); PL.capas(doc)
    laminas = []
    x = 0.0
    for fn, cod in ((diagrama, "VD-01"), (laminas_cunetas, "VD-02"), (laminas_alcantarillas, "VD-03"), (lamina_badenes, "VD-04"), (lamina_cuadro, "VD-05")):
        if fn is lamina_badenes and not R["badenes"]: continue
        if fn is laminas_cunetas and not R["cunetas"]: continue
        if fn is laminas_alcantarillas and not R["alcantarillas"]: continue
        if fn is diagrama and not (R["cunetas"] or R["alcantarillas"] or R["badenes"]): continue
        hechas = fn(doc, R, x, 0.0, cod)
        for c, lx, ly, esc in hechas:
            laminas.append({"codigo": c, "x0": lx, "y0": ly, "x1": lx + W * esc / 1000.0, "y1": ly + H * esc / 1000.0})
        x = max(l["x1"] for l in laminas) + 50.0
    B.guardar(doc, ruta_dxf)
    pngs = render.laminas_png(doc, laminas, carpeta_png) if carpeta_png else []
    return {"dxf": ruta_dxf, "laminas": [l["codigo"] for l in laminas], "png": pngs}
