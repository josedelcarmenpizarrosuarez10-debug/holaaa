"""Planos DXF del colector pluvial frontal del CAR Mujeres (CUI 2717013), con el estilo del juego del Hogar de Refugio.

Rehace las 15 laminas del plano original (DP-01 a DP-10) ordenadas, a escala real (1 unidad = 1 m) y con la misma
geometria del metrado y de la planilla del presupuesto (partidas 1.4.4.6): b = 1.50, cotas de fondo 258.72 a 258.30,
NPT 259.25 hasta 0+078.42 y h = 0.60 en el tramo final, cruces de autos y de camiones, 15 registros, 33 juntas,
4 empalmes de cuneta y estructura de salida con dos aleros.

Uso: python3 planos_m.py [codigos separados por coma]
"""
import os, sys, json, math, unicodedata
from ezdxf.enums import TextEntityAlignment as TA
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
for p in (HERR, AQUI):
    if p not in sys.path: sys.path.insert(0, p)
import dxf_base as B
import datos_m as dz
from dxf_planta import recortar

B.PROYECTO = ("CREACION DEL SERVICIO DE PROTECCION INTEGRAL A NINAS, NINOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE PERDERLOS",
              "EN CENTRO DE ACOGIDA RESIDENCIAL - MUJERES, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2717013")
B.UBICACION = "UBICACION: PREDIO RURAL LOS MANGOS - MORALES - SAN MARTIN - SAN MARTIN"
SALIDA = os.path.join(dz.SAL, "PLANOS_COLECTOR_PLUVIAL_CAR_MUJERES.dxf")
LAMINAS = {}
pt = dz.prog_txt
ROJO, AZUL, VERDE, NARANJA, MAGENTA, GRIS = 1, 5, 94, 30, 6, 8


def ascii_(s):
    s = s.replace("Ã?", "I").replace("Ã’", "O").replace("NÂ°", "N.")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


# ============================================================================== DP-01 PLANTA
def dp01(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 200, "DP-01", "PLANTA DEL COLECTOR PLUVIAL",
                   "TRAMO CAR MUJERES (0+000.00 - 0+139.08) - TRAZO, REGISTROS, CRUCES, EMPALMES DE CUNETA Y SALIDA")
    f = lam.f; BS = dz.BASE
    win = (lam.ox + 27 * f, lam.oy + 112 * f, lam.ox + 829 * f, lam.oy + 582 * f)
    # --- base de arquitectura recortada a la ventana
    for a in BS["arq"]:
        if a[0] == "L":
            for seg in recortar([tuple(q) for q in a[1]], win): lam.poli(seg, "ARQ-BASE")
        elif a[0] == "C" and win[0] < a[1][0] < win[2] and win[1] < a[1][1] < win[3]:
            lam.circulo(a[1], a[2], "ARQ-BASE")
        elif a[0] == "A" and win[0] < a[1][0] < win[2] and win[1] < a[1][1] < win[3]:
            lam.msp.add_arc(a[1], a[2], a[3], a[4], dxfattribs={"layer": "ARQ-BASE"})
    for x, y, rot, hh, t in BS["arq_textos"]:
        if win[0] < x < win[2] and win[1] < y < win[3] and t not in ("01", "02") and not (t == "CARRETERA OASIS" and x > -500):
            e = lam.msp.add_text(ascii_(t), height=max(hh, 1.6 * f), dxfattribs={"layer": "ARQ-TEXTO", "rotation": rot})
            e.set_placement((x, y), align=TA.LEFT)
    # --- colector: relleno de la losa, muros, caras interiores, eje
    pp = [i * 0.5 for i in range(int(dz.L * 2) + 1)] + [dz.L]
    poli = [dz.lateral(p, dz.b_ext(p) / 2) for p in pp] + [dz.lateral(p, -dz.b_ext(p) / 2) for p in reversed(pp)]
    lam.relleno(poli, "CONCRETO-ACHURADO")
    for pl in BS["CONCRETO"]: lam.poli(pl, "CONCRETO")
    for pl in BS["CONCRETO-OCULTO"]: lam.poli(pl, "CONCRETO-OCULTO")
    lam.poli(dz.EJE, "EJE-COLECTOR")
    for pl in BS["JUNTAS"]: lam.poli(pl, "JUNTAS")
    for pl in BS["CRUCE-VEHICULAR"]: lam.poli(pl, "CRUCE-VEHICULAR")
    for pl in BS["CUNETA"]: lam.poli(pl, "CUNETA")
    for pl in BS["CUNETA-OCULTA"]: lam.poli(pl, "CUNETA-OCULTA")
    for pl in BS["LINDERO"]: lam.poli(pl, "LINDERO")
    for pl in BS["EMBOQUILLADO"]: lam.poli(pl, "POZA", cerrada=True)
    for x, y, r in BS["piedras"]: lam.circulo((x, y), r, "ISO-PIEDRA")
    for x, y, rot in BS["registros"]: lam.bloque("REGISTRO-PLANTA", (x, y), 1.0, rot)
    for p in (6.0, 27.0, 45.0, 66.0, 92.0, 120.0):
        x, y, az = dz.eje_local(p); lam.bloque("SIMB-FLECHA", (x, y), f, az)
    # --- cortes S-01 a S-15 (lado del predio, junto al muro)
    for n, p in dz.SECCIONES:
        a, c = dz.lateral(p, -dz.b_ext(p) / 2 - 0.35), dz.lateral(p, dz.b_ext(p) / 2 + 0.35)
        lam.poli([a, c], "CORTES", ancho=0.35 * f)
        az = dz.eje_local(p)[2]
        q = dz.lateral(p, dz.b_ext(p) / 2 + 0.75)
        lam.texto(q, "S-%02d" % n, 1.5, "CORTES", TA.BOTTOM_CENTER, rot=az + 180 if 90 < (az % 360) < 270 else az)
    # --- etiquetas en la franja inferior (lado de la via): registros, cuneta que llega, cruces y salida
    cun = {r: (e, ncf) for e, r, ncf in dz.CUNETAS}
    ets = []
    for r, (x, y, rot) in zip(dz.REGISTROS, BS["registros"]):
        ls = ["%s  %s" % (r["nombre"], pt(r["prog"])), "CF %.3f  CT %.3f" % (r["cf"], r["ct"])]
        if r["nombre"] in cun:
            e, ncf = cun[r["nombre"]]; ls.append("cuneta %s (NCF %.2f)" % (e, ncf))
        ets.append((x, y, ls, 7))
    for (a, c), pm in zip(dz.AUTOS, (14.2, 43.6)):
        x, y, _ = dz.eje_local(pm)
        ets.append((x, y, ["CRUCE DE AUTOS", "%s - %s" % (pt(a), pt(c)), "marcos 3/8\" @0.15"], NARANJA))
    x, y, _ = dz.eje_local(55.6)
    ets.append((x, y, ["CRUCE DE CAMIONES", "%s - %s" % (pt(54), pt(60)), "e = 0.15/0.20, 2 marcos 1/2\""], NARANJA))
    x, y, _ = dz.eje_local(dz.L)
    ets.append((x - 0.6, y + 0.2, ["SALIDA  %s" % pt(dz.L), "CF 258.300", "aleros a 45 grados (DP-07)"], 7))
    lam.franja(ets, lam.oy + 236 * f, abajo=True, hmm=1.6, xmin_mm=28, xmax_mm=828)
    # --- llegada (aguas arriba de R-01) y textos generales
    x1, y1, _ = dz.eje_local(0.0)
    lam.flecha((x1 + 14.0, y1), (x1 + 1.0, y1), "FLUJO", 3.0)
    lam.textos(lam.P(826, (y1 - lam.oy) / f + 16), ["LLEGADA DEL COLECTOR DE", "CAR VARONES Y HOGAR DE REFUGIO", "Q = %.1f L/s (registro R-01)" % dz.Q_LLEGADA],
               1.7, "TEXTOS", al=TA.RIGHT)
    lam.textos(lam.P(30, 452), ["COLECTOR CUBIERTO DE CONCRETO ARMADO f'c=210 kg/cm2:  b = 1.50 m,  S = 0.30 %,",
                                "h = 0.43 a 0.67 m en el tramo en vereda (0+000.00 - 0+078.42) y h = 0.60 m en el tramo final;",
                                "losa superior a nivel de vereda NPT +259.25 hasta 0+078.42."], 1.9, "TEXTOS")
    lam.bloque("SIMB-NORTE", lam.P(800, 548), f, BS["norte_rot"])
    # --- cuadro de coordenadas
    filas = [[r["nombre"], pt(r["prog"]), r["E"], r["N"], "%.3f" % r["cf"], "%.3f" % r["ct"]] for r in dz.REGISTROS]
    s = dz.SALIDA_UTM; filas.append([s[0], s[1], s[2], s[3], s[4], "-"])
    yf = lam.tabla(30, 572, ["PUNTO", "PROGRESIVA", "ESTE", "NORTE", "COTA FONDO", "COTA TAPA"], filas, [16, 22, 26, 28, 22, 22],
                   hmm=1.7, alto_mm=4.4, titulo="CUADRO DE COORDENADAS DE REGISTROS Y SALIDA")
    lam.texto(lam.P(30, yf - 4), "Coordenadas UTM WGS84 - Zona 18 Sur. Cota tapa = cara superior de la tapa (NPT).", 1.6, "TEXTOS-NOTAS")
    # --- leyenda y notas
    lam.leyenda2(30, 100, [
        ("concreto", "CONCRETO", "colector cubierto (losa superior)"), ("discontinua", "CONCRETO-OCULTO", "cara interior de muros (bajo la losa)"),
        ("linea", "EJE-COLECTOR", "eje del colector"), ("rect", "REGISTRO", "registro de limpieza con tapa 0.68 x 0.68"),
        ("discontinua", "JUNTAS", "junta de dilatacion e = 1\" (33 und)"), ("rect", "CRUCE-VEHICULAR", "cruce vehicular (autos / camiones)"),
        ("linea2", "CUNETA", "cuneta que llega al colector (4 und)"), ("linea", "LINDERO", "lindero del predio"),
        ("linea2", "CORTES", "corte de seccion S-01 a S-15 (DP-04)"), ("bloque:SIMB-FLECHA", "0", "sentido del flujo"),
        ("linea", "ARQ-BASE", "arquitectura (referencia)")], hmm=1.9, ancho_col=95, filas_col=6)
    lam.notas(232, 100, "NOTAS", [
        "1. Colector de concreto armado f'c=210 kg/cm2, losa superior vaciada monolitica con los muros en todo su recorrido.",
        "2. Todo el colector queda dentro del lindero; el muro del lado de la via se vacia contra el terreno.",
        "3. Registros de limpieza con tapa removible en cada eje de cuneta, quiebre y a 12.00 m como maximo (15 und, DP-06B).",
        "4. Cotas en m.s.n.m.; progresivas a lo largo del eje del colector desde el registro R-01 (Eje 02).",
        "5. Secciones en DP-04 y DP-06A, perfiles en DP-02 y DP-03, salida en DP-07, acero en DP-08."], hmm=1.8, ancho_mm=405)
    return lam


# ============================================================================== PERFILES (DP-02 y DP-03)
def _estaciones(p1, p2, paso, sep_min):
    """progresivas de la guitarra: registros, cambios de zona y cada `paso` m (se omite la que cae a menos de sep_min m)."""
    fijos = [r["prog"] for r in dz.REGISTROS if p1 - 1e-6 <= r["prog"] <= p2 + 1e-6]
    fijos += [q for q in (dz.AUTOS[0] + dz.AUTOS[1] + dz.CAMION + (dz.P_VER, dz.L)) if p1 - 1e-6 <= q <= p2 + 1e-6]
    fijos += [p1, p2]
    out = []
    for q in sorted(set(round(v, 2) for v in fijos)):
        if all(abs(q - o) >= sep_min for o in out): out.append(q)
        elif q in [round(r["prog"], 2) for r in dz.REGISTROS]:
            out = [o for o in out if abs(q - o) >= sep_min] + [q]
    if paso:
        k = math.ceil(p1 / paso) * paso
        while k <= p2 + 1e-6:
            if all(abs(k - o) >= sep_min for o in out): out.append(round(k, 2))
            k += paso
    return sorted(out)


def zlim(p1, p2):
    pp = [p1 + (p2 - p1) * i / 40 for i in range(41)]
    zmin = math.floor((min(dz.CF(q) - dz.esp(q)[1] - dz.E_SOLADO for q in pp) - 0.05) * 10) / 10
    zmax = math.ceil((max(max(dz.terreno(q), dz.techo(q)) for q in pp) + 0.05) * 10) / 10
    return zmin, zmax


def perfil(lam, xmm, ymm, p1, p2, detalle=True, titulo=None, paso=5.0):
    """Perfil longitudinal a escala real (H = V) entre p1 y p2. (xmm, ymm): papel, a la altura de zmin del tramo
    (borde inferior del dibujo); la guitarra va debajo y la franja de etiquetas encima."""
    f = lam.f
    zmin, zmax = zlim(p1, p2); zref = zmin
    X = lambda p: lam.ox + xmm * f + (p - p1)
    Y = lambda z: lam.oy + ymm * f + (z - zref)
    ps = sorted(set([p1, p2] + [q for q in (dz.AUTOS[0] + dz.AUTOS[1] + dz.CAMION + (dz.P_VER,)) if p1 < q < p2]
                    + [p1 + i * 0.25 for i in range(int((p2 - p1) / 0.25) + 1)]))
    def tramo_pts(fz, pp):
        out = []
        for q in pp:
            out.append((X(q), Y(fz(q))))
        return out
    # cortes de geometria (escalones en los cambios de espesor / fin de vereda)
    cortes = [q for q in (dz.CAMION + (dz.P_VER,)) if p1 < q < p2]
    def poli_por_tramos(fz_top, fz_bot):
        pols = []; lim = [p1] + cortes + [p2]
        for a, c in zip(lim[:-1], lim[1:]):
            pp = [q for q in ps if a - 1e-9 <= q <= c + 1e-9]
            eps = 1e-4
            top = [(X(q), Y(fz_top(min(max(q, a + eps), c - eps)))) for q in pp]
            bot = [(X(q), Y(fz_bot(min(max(q, a + eps), c - eps)))) for q in reversed(pp)]
            pols.append(top + bot)
        return pols
    techo = dz.techo
    sof = lambda q: dz.CF(q) + dz.h(q)
    fondo_ext = lambda q: dz.CF(q) - dz.esp(q)[1]
    # agua (relleno celeste y linea)
    agua = [(X(q), Y(dz.NA(q))) for q in ps] + [(X(q), Y(dz.CF(q))) for q in reversed(ps)]
    lam.relleno(agua, "AGUA-RELLENO")
    lam.poli([(X(q), Y(dz.NA(q))) for q in ps], "AGUA")
    # concreto: losa superior (con el hueco de cada registro) y losa de fondo cortadas
    huecos = [(r["prog"] - dz.REB / 2, r["prog"] + dz.REB / 2) for r in dz.REGISTROS]
    def segmentos(a, c):
        segs = [(a, c)]
        for h1, h2 in huecos:
            nuevo = []
            for u, v in segs:
                if h2 <= u or h1 >= v: nuevo.append((u, v)); continue
                if u < h1: nuevo.append((u, h1))
                if h2 < v: nuevo.append((h2, v))
            segs = nuevo
        return [sg for sg in segs if sg[1] - sg[0] > 1e-3]
    lim = [p1] + cortes + [p2]
    sup = []
    for a, c in zip(lim[:-1], lim[1:]):
        for u, v in segmentos(a, c):
            pp = sorted(set([u, v] + [q for q in ps if u < q < v])); e_ = 1e-4
            fz = lambda q: min(max(q, a + e_), c - e_)
            sup.append([(X(q), Y(techo(fz(q)))) for q in pp] + [(X(q), Y(sof(fz(q)))) for q in reversed(pp)])
    for pl in sup + poli_por_tramos(lambda q: dz.CF(q), fondo_ext):
        lam.relleno(pl, "CONCRETO-ACHURADO"); lam.poli(pl, "CONCRETO", cerrada=True)
    for pl in poli_por_tramos(fondo_ext, lambda q: fondo_ext(q) - dz.E_SOLADO):
        lam.poli(pl, "SOLADO", cerrada=True)
    # registros: ceja de apoyo 0.05 a 0.08 bajo la tapa, luz libre 0.60, borde engrosado 0.15 x 0.10 y tapa 0.68 x 0.08
    for r in dz.REGISTROS:
        q = r["prog"]
        if not (p1 - 0.5 <= q <= p2 + 0.5): continue
        zt = r["ct"]; zl = zt - dz.esp(q)[2]
        for s_ in (-1, 1):
            xs = [q + s_ * d for d in (0.30, 0.35, 0.35, 0.45, 0.45, 0.30)]
            if not all(p1 - 1e-6 <= x_ <= p2 + 1e-6 for x_ in xs): continue
            zs = [zt - dz.E_TAPA, zt - dz.E_TAPA, zl, zl, zl - dz.ENG_H, zl - dz.ENG_H]
            pl = [(X(x_), Y(z_)) for x_, z_ in zip(xs, zs)]
            lam.relleno(pl, "CONCRETO-ACHURADO"); lam.poli(pl, "CONCRETO", cerrada=True)
        if p1 <= q - 0.34 and q + 0.34 <= p2:
            tapa = [(X(q - 0.34), Y(zt)), (X(q + 0.34), Y(zt)), (X(q + 0.34), Y(zt - dz.E_TAPA)), (X(q - 0.34), Y(zt - dz.E_TAPA))]
            lam.relleno(tapa, "ISO-TAPA"); lam.poli(tapa, "REGISTRO", cerrada=True)
    # cuneta que llega: ventana 0.40 x 0.30 en el muro del lado del predio (se ve en el fondo del corte)
    regp = {r["nombre"]: r["prog"] for r in dz.REGISTROS}
    for e, rn, ncf in dz.CUNETAS:
        q = regp[rn]
        if p1 <= q - 0.2 and q + 0.2 <= p2:
            zt_ = min(ncf + 0.30, sof(q))
            lam.rect(X(q - 0.20), Y(ncf), X(q + 0.20), Y(zt_), "CUNETA-OCULTA")
            lam.flecha((X(q + 0.05), Y(ncf + 0.02)), (X(q + 0.05), Y(dz.CF(q) + 0.04)), "FLUJO", 1.6)
    # juntas de dilatacion
    for q in dz.JUNTAS:
        if p1 < q < p2: lam.linea((X(q), Y(techo(q) + 0.02)), (X(q), Y(fondo_ext(q) - 0.02)), "JUNTAS")
    # acero (solo detalle): barras longitudinales y marcos vistos en el corte (puntos a diametro real)
    if detalle:
        for a, c in zip([p1] + cortes, cortes + [p2]):
            m = (a + c) / 2; ac = dz.acero(m); em, ef, es = dz.esp(m)
            if ac["doble"]:
                ys_top = [lambda q, es=es: techo(q) - 0.045, lambda q, es=es: techo(q) - es + 0.045]
                ys_bot = [lambda q, ef=ef: dz.CF(q) - 0.045, lambda q, ef=ef: dz.CF(q) - ef + 0.045]
            else:
                ys_top = [lambda q, es=es: techo(q) - es / 2]; ys_bot = [lambda q, ef=ef: dz.CF(q) - ef / 2]
            pp = [q for q in ps if a <= q <= c]
            for fy in ys_top + ys_bot:
                lam.poli([(X(q), Y(fy(q))) for q in (a + 0.03, c - 0.03)] if False else [(X(q), Y(fy(q))) for q in pp], "ACERO-LONG")
            q = a + ac["sep"] / 2; blk = "ACERO-12" if ac["doble"] else "ACERO-38"
            while q < c - 0.02:
                for fy in ys_top + ys_bot: lam.bloque(blk, (X(q), Y(fy(q))), 1.0)
                q += ac["sep"]
    # NPT / terreno natural
    lam.poli([(X(q), Y(dz.terreno(q))) for q in ps], "TERRENO-EXISTENTE")
    # escala de cotas a la izquierda
    xg = X(p1) - 4.0 * f
    dzs = 0.1 if detalle else 0.5
    k0 = math.ceil(zmin / dzs - 1e-6); k1 = math.floor(zmax / dzs + 1e-6)
    for k in range(k0, k1 + 1):
        z = k * dzs
        lam.linea((xg, Y(z)), (xg + 2 * f, Y(z)), "GRILLA")
        if detalle and k % 2: continue
        lam.texto((xg - 0.8 * f, Y(z)), "%.2f" % z, 1.5, "TEXTOS", TA.MIDDLE_RIGHT)
    lam.linea((xg + 2 * f, Y(zmin)), (xg + 2 * f, Y(zmax)), "GRILLA")
    # guitarra
    est = _estaciones(p1, p2, paso, 0.75 if detalle else 2.6)
    filas = [("PROGRESIVA", lambda q: pt(q)), ("TERRENO NATURAL", lambda q: "%.3f" % dz.terreno(q)),
             ("CARA SUP. DE LOSA", lambda q: "%.3f" % _ct(q)), ("COTA DE FONDO", lambda q: "%.3f" % dz.CF(q)),
             ("NIVEL DE AGUA", lambda q: "%.3f" % dz.NA(q)), ("ALTURA INTERIOR h", lambda q: "%.2f" % _h(q))]
    if detalle: filas.append(("PROF. EXCAVACION", lambda q: "%.2f" % ((dz.NPT if q <= dz.P_VER else dz.terreno(q)) - (dz.CF(q) - dz.esp(q)[1] - dz.E_SOLADO))))
    alto = 6.0 if detalle else 5.2
    yg0 = ymm - 4.0
    x0g = xmm - 44.0; x1g = xmm + (p2 - p1) / f
    for i in range(len(filas) + 1):
        lam.linea(lam.P(x0g, yg0 - i * alto), lam.P(x1g, yg0 - i * alto), "GUITARRA")
    lam.linea(lam.P(x0g, yg0), lam.P(x0g, yg0 - len(filas) * alto), "GUITARRA")
    lam.linea(lam.P(xmm - 6.0, yg0), lam.P(xmm - 6.0, yg0 - len(filas) * alto), "GUITARRA")
    lam.linea(lam.P(x1g, yg0), lam.P(x1g, yg0 - len(filas) * alto), "GUITARRA")
    for i, (nom, fn) in enumerate(filas):
        yc = yg0 - (i + 0.5) * alto
        lam.texto(lam.P(x0g + 1.5, yc), nom, 1.6, "TEXTOS", TA.MIDDLE_LEFT)
        for q in est:
            lam.texto((X(q), lam.oy + yc * f), fn(q), 1.45 if detalle else 1.35, "TEXTOS", TA.MIDDLE_CENTER)
    for q in est:
        lam.linea((X(q), lam.oy + yg0 * f), (X(q), Y(dz.CF(q) - dz.esp(q)[1] - dz.E_SOLADO)), "GRILLA")
    # franja de etiquetas encima del perfil
    cun = {r: (e, ncf) for e, r, ncf in dz.CUNETAS}
    ets = []
    for r in dz.REGISTROS:
        q = r["prog"]
        if p1 - 1e-6 <= q <= p2 + 1e-6:
            ls = ["REGISTRO %s  %s" % (r["nombre"], pt(q)), "tapa CT %.3f" % r["ct"]]
            if r["nombre"] in cun: ls[1] += " - cuneta %s (NCF %.2f)" % cun[r["nombre"]]
            if abs(q - dz.P_VER) < 0.01: ls.append("fin del tramo en vereda; sigue h = 0.60 m")
            if not detalle and r["nombre"] == "R-15": ls.append("salida %s: aleros y emboquillado (DP-07)" % pt(dz.L))
            ets.append((X(q), Y(r["ct"]), ls, 7))
    for (a, c), nom in ((dz.AUTOS[0], "CRUCE DE AUTOS"), (dz.AUTOS[1], "CRUCE DE AUTOS"), (dz.CAMION, "CRUCE DE CAMIONES")):
        a_, c_ = max(a, p1), min(c, p2)
        if a_ < c_:
            yb = Y(techo(a_) + 0.12)
            lam.poli([(X(a_), yb), (X(c_), yb)], "CRUCE-VEHICULAR", ancho=0.8 * f)
            for q in (a_, c_): lam.linea((X(q), yb - 0.06), (X(q), yb + 0.06), "CRUCE-VEHICULAR")
            sub = "%s - %s" % (pt(a), pt(c)) + (": losas 0.20, muros 0.15" if "CAMION" in nom else ": marcos @0.15")
            ets.append((X((a_ + c_) / 2), yb, [nom, sub], NARANJA))
    if detalle and p2 >= dz.L - 0.01:
        ets.append((X(dz.L), Y(dz.techo(dz.L)), ["SALIDA %s" % pt(dz.L), "aleros y emboquillado (DP-07)"], 7))
    ytop = Y(max(max(dz.terreno(q), techo(q)) for q in ps) + 0.25)
    yf = lam.franja(ets, ytop, abajo=False, hmm=1.6, xmin_mm=xmm - 40, xmax_mm=x1g + 2)
    if titulo:
        lam.texto((lam.ox + (xmm - 44) * f, yf + 3.0 * f), titulo, 3.0, "TITULOS", TA.BOTTOM_LEFT)
    return yg0 - len(filas) * alto


def _ct(q):
    """cara superior de losa en la guitarra (en el registro: cota de tapa del cuadro)"""
    for r in dz.REGISTROS:
        if abs(r["prog"] - q) < 1e-6: return r["ct"]
    return dz.techo(q)


def _h(q):
    return dz.h(q)


LEY_PERFIL = [("concreto", "CONCRETO", "concreto armado f'c=210 cortado"), ("rect", "SOLADO", "solado f'c=100 e = 0.05"),
              ("relleno", "AGUA-RELLENO", "agua con el caudal de diseno"), ("discontinua", "TERRENO-EXISTENTE", "terreno natural (TIN)"),
              ("relleno", "ISO-TAPA", "tapa de registro 0.68 x 0.08"), ("discontinua", "JUNTAS", "junta de dilatacion e = 1\""),
              ("rect", "CUNETA-OCULTA", "ventana de llegada de cuneta 0.40 x 0.30"), ("linea2", "CRUCE-VEHICULAR", "tramo de cruce vehicular")]


def alto_perfil(p1, p2, f):
    zmin, zmax = zlim(p1, p2); return (zmax - zmin) / f


def dp02(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 100, "DP-02", "PERFIL LONGITUDINAL GENERAL DEL COLECTOR",
                   "ESCALA REAL (H = V) - 0+000.00 A 0+139.08 - NIVEL DE AGUA DE DISENO Y COTAS EN REGISTROS")
    y = 530 - alto_perfil(0, 70, lam.f)
    yb = perfil(lam, 72, y, 0.0, 70.0, detalle=False, titulo="PERFIL 1: 0+000.00 A 0+070.00", paso=None)
    y = yb - 62 - alto_perfil(70, dz.L, lam.f)
    yb = perfil(lam, 72, y, 70.0, dz.L, detalle=False, titulo="PERFIL 2: 0+070.00 A 0+139.08", paso=None)
    # cuadro hidraulico por tramos (memoria de calculo)
    filas = []
    lims = [0.0, 37.95, 49.38, 60.15, dz.L]
    nom = ["R-01 (Eje 02) - R-05", "R-05 (Eje 07) - R-06", "R-06 (Eje 10) - R-07", "R-07 (Eje 12) - SALIDA"]
    for k in range(4):
        rows = [r for r in dz.FLUJO if lims[k] + 1e-6 < r[0] <= lims[k + 1] + 1e-6] if k else [r for r in dz.FLUJO if r[0] <= lims[1] + 1e-6]
        rows = [r for r in rows if not (k < 3 and abs(r[0] - lims[k + 1]) < 1e-6)] or rows
        q = rows[0][2] * 1000
        filas.append([nom[k], "%s - %s" % (pt(lims[k]), pt(lims[k + 1])), "%.1f" % q, "%.2f - %.2f" % (min(r[3] for r in rows), max(r[3] for r in rows)),
                      "%.2f - %.2f" % (min(r[5] for r in rows), max(r[5] for r in rows)), "%.2f" % max(r[6] for r in rows),
                      "%.0f %%" % (100 * max(r[7] for r in rows)), "%.3f" % min(r[8] for r in rows)])
    lam.tabla(30, yb - 18, ["TRAMO", "PROGRESIVAS", "Q (L/s)", "TIRANTE y (m)", "VELOCIDAD (m/s)", "FROUDE MAX.", "LLENADO MAX.", "BORDE LIBRE MIN. (m)"],
              filas, [52, 48, 22, 34, 36, 26, 28, 38], hmm=1.8, alto_mm=6.0, titulo="CUADRO HIDRAULICO POR TRAMOS (FLUJO GRADUALMENTE VARIADO, TR = 25 ANOS)")
    lam.leyenda2(30, 100, LEY_PERFIL, hmm=1.9, ancho_col=100, filas_col=4)
    lam.notas(250, 100, "NOTAS", [
        "1. Perfil a escala real: horizontal = vertical = 1/100. Cotas en m.s.n.m.",
        "2. Nivel de agua del perfil de flujo gradualmente variado (memoria de calculo); el caudal crece en cada cuneta que llega.",
        "3. Cara superior de la losa = NPT de vereda +259.25 hasta 0+078.42; tramo final con h = 0.60 m.",
        "4. Perfil detallado por tramos con acero, registros y juntas en las laminas DP-03A, DP-03B y DP-03C."], hmm=1.8, ancho_mm=390)
    return lam


TRAMOS_DP03 = [round(dz.L * k / 9, 2) for k in range(10)]


def dp03(doc, ox, oy):
    out = []
    for k, cod in enumerate(("DP-03A", "DP-03B", "DP-03C")):
        tr = TRAMOS_DP03[3 * k: 3 * k + 4]
        lam = B.Lamina(doc, ox + k * 25.0, oy, 25, cod, "PERFIL LONGITUDINAL DETALLADO DEL COLECTOR",
                       "TRAMOS %d A %d (%s - %s) - ESCALA REAL (H = V) - ACERO, REGISTROS, JUNTAS Y EMPALMES" % (3 * k + 1, 3 * k + 3, pt(tr[0]), pt(tr[-1])))
        altos = [alto_perfil(tr[j], tr[j + 1], lam.f) for j in range(3)]
        gap = max(0.0, (575 - 112 - sum(altos) - 3 * 86) / 2)
        ytop = 575
        for j in range(3):
            a, c = tr[j], tr[j + 1]
            y = ytop - 38 - altos[j]
            yb = perfil(lam, 72, y, a, c, detalle=True, titulo="TRAMO %d: %s A %s" % (3 * k + j + 1, pt(a), pt(c)), paso=2.5)
            ytop = yb - gap
        yl = lam.leyenda2(700, 575, LEY_PERFIL + [("bloque:ACERO-38", "ACERO-PUNTOS", "marco cortado (3/8\" o 1/2\")"),
                                                  ("linea", "ACERO-LONG", "barras longitudinales 3/8\"")], hmm=1.6)
        lam.notas(700, yl - 8, "NOTAS", [
            "1. Escala real H = V = 1/25; cotas en m.s.n.m.",
            "2. Marcos 3/8\" @0.20 en vereda y tramo final, @0.15 en cruces de autos; 2 marcos 1/2\" @0.15 en cruce de camiones.",
            "3. Barras longitudinales 3/8\" @0.25 (@0.20 en cruce de camiones), traslape 0.40 m.",
            "4. Juntas de dilatacion cada 4.00 m y en los extremos del cruce de camiones (33 und).",
            "5. Ventana de cuneta 0.40 x 0.30 en el muro del lado del predio, bajo el registro (DP-06B).",
            "6. Registro: rebaje 0.70 x 0.08, luz 0.60 y borde engrosado 0.15 x 0.10 (DP-06B)."], hmm=1.6, ancho_mm=128)
        out.append(lam)
    return out


# ============================================================================== SECCIONES (DP-04 y DP-06A)
D38, D12 = 0.0095, 0.0127


def seccion(lam, cx, cy, p, detalle=False, num=None, xt=None):
    """Seccion transversal a escala real en la progresiva p. (cx, cy): eje del colector a la cota de fondo (modelo).
    Lado de la via (lindero) a la izquierda, lado del predio a la derecha. xt: x de la columna de llamadas."""
    f = lam.f
    em, ef, es = dz.esp(p); hh = dz.h(p); bi = dz.b / 2; K = dz.b_ext(p) / 2
    z = lambda v: cy + (v - dz.CF(p))
    cf = dz.CF(p); top = cf + hh + es; bot = cf - ef
    # solado y concreto (una sola pieza: U + losa superior monolitica)
    lam.rect(cx - K - 0.05, z(bot - dz.E_SOLADO), cx + K + 0.05, z(bot), "SOLADO")
    ext = [(cx - K, z(bot)), (cx + K, z(bot)), (cx + K, z(top)), (cx - K, z(top))]
    inn = [(cx - bi, z(cf)), (cx + bi, z(cf)), (cx + bi, z(cf + hh)), (cx - bi, z(cf + hh))]
    hch = lam.msp.add_hatch(dxfattribs={"layer": "CONCRETO-ACHURADO"}); hch.rgb = B.COLOR_RGB["CONCRETO-ACHURADO"]
    hch.set_solid_fill(rgb=B.COLOR_RGB["CONCRETO-ACHURADO"])
    hch.paths.add_polyline_path(ext, is_closed=True, flags=1); hch.paths.add_polyline_path(inn, is_closed=True, flags=16)
    lam.poli(ext, "CONCRETO", cerrada=True); lam.poli(inn, "CONCRETO", cerrada=True)
    # agua
    na = dz.NA(p)
    lam.relleno([(cx - bi, z(cf)), (cx + bi, z(cf)), (cx + bi, z(na)), (cx - bi, z(na))], "AGUA-RELLENO")
    lam.linea((cx - bi, z(na)), (cx + bi, z(na)), "AGUA")
    lam.bloque("SIMB-AGUA", (cx + bi * 0.45, z(na)), f)
    # terreno natural (TIN, referencia), vereda del lado del predio y suelo contra el muro del lado de la via
    ter = dz.terreno(p); pis = dz.NPT if p <= dz.P_VER else ter
    ext_l = 0.35 if f < 0.015 else 0.55
    lam.poli([(cx - K - ext_l, z(ter)), (cx + K + ext_l, z(ter))], "TERRENO-EXISTENTE")
    if p <= dz.P_VER:
        lam.poli([(cx + K + 0.025, z(pis)), (cx + K + ext_l, z(pis))], "TERRENO")
        lam.rect(cx + K, z(top - 0.10), cx + K + 0.025, z(top), "JUNTAS")
    yy = z(min(ter, top) - 0.04)
    while yy > z(bot - dz.E_SOLADO) + 0.03:
        lam.linea((cx - K, yy), (cx - K - 0.05, yy - 0.05), "TERRENO"); yy -= 0.12
    # acero
    ac = dz.acero(p)
    def marco(x0, y0, x1, y1, d, blk):
        lam.poli([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "ACERO", cerrada=True, ancho=d)
        g = 6 * d + 0.03                                   # ganchos a 135 grados en la esquina superior del lado de la via
        lam.poli([(x0, y1 - 0.0), (x0 + g * 0.7, y1 - g * 0.7)], "ACERO", ancho=d)
        lam.poli([(x0, y1), (x0 + g * 0.7, y1 - g * 0.7 + 0.0)], "ACERO", ancho=d)
    def barras(xa, xb, ya, yb, n, blk):
        for i in range(n):
            t = i / max(n - 1, 1)
            lam.bloque(blk, (xa + t * (xb - xa), ya + t * (yb - ya)), 1.0)
    pos = {}
    if not ac["doble"]:
        r = D38
        x0, x1 = cx - bi - em / 2, cx + bi + em / 2; y0, y1 = z(cf - ef / 2), z(top - es / 2)
        marco(x0, y0, x1, y1, r, "ACERO-38")
        o = r                                              # barras apoyadas por dentro del marco
        barras(x0 + o, x1 - o, y1 - o, y1 - o, 8, "ACERO-38"); barras(x0 + o, x1 - o, y0 + o, y0 + o, 8, "ACERO-38")
        n = ac["n_muro"]
        if n:
            dy = (y1 - y0) / (n + 1)
            for xm in (x0 + o, x1 - o): barras(xm, xm, y0 + dy, y1 - dy, n, "ACERO-38")
        pos = dict(marco=(x1, (y0 + y1) / 2), sup=((x0 + x1) / 2 + 0.1143, y1 - o), inf=((x0 + x1) / 2 - 0.1143, y0 + o),
                   muro=(x1 - o, y0 + dy) if n else (x1 - o, (y0 + y1) / 2), nlong=16 + 2 * n)
    else:
        r = D12; c = 0.045
        xo0, xo1, yo0, yo1 = cx - K + c, cx + K - c, z(bot + c), z(top - c)
        xi0, xi1, yi0, yi1 = cx - bi - c, cx + bi + c, z(cf - c), z(cf + hh + c)
        marco(xo0, yo0, xo1, yo1, r, "ACERO-12"); marco(xi0, yi0, xi1, yi1, r, "ACERO-12")
        o = (D12 + D38) / 2
        no = math.ceil(round((2 * K - 0.09) / 0.2, 6)) + 1; ni = math.ceil(round((dz.b + 0.09) / 0.2, 6)) + 1
        nwo = max(math.ceil(round((hh + 0.31) / 0.2, 6)) - 1, 0); nwi = max(math.ceil(round((hh + 0.09) / 0.2, 6)) - 1, 0)
        barras(xo0 + o, xo1 - o, yo1 - o, yo1 - o, no, "ACERO-38"); barras(xo0 + o, xo1 - o, yo0 + o, yo0 + o, no, "ACERO-38")
        barras(xi0 - o, xi1 + o, yi1 + o, yi1 + o, ni, "ACERO-38"); barras(xi0 - o, xi1 + o, yi0 - o, yi0 - o, ni, "ACERO-38")
        for xm, ya, yb, n in ((xo0 + o, yo0, yo1, nwo), (xo1 - o, yo0, yo1, nwo), (xi0 - o, yi0, yi1, nwi), (xi1 + o, yi0, yi1, nwi)):
            if n:
                dy = (yb - ya) / (n + 1); barras(xm, xm, ya + dy, yb - dy, n, "ACERO-38")
        pos = dict(marco=(xo1, (yo0 + yo1) / 2), marco_i=(xi1, (yi0 + yi1) / 2 + 0.1), sup=(cx + 0.05, yo1 - o), inf=(cx - 0.05, yi0 - o),
                   muro=(xo1 - o, yo0 + (yo1 - yo0) / (nwo + 1)), nlong=2 * no + 2 * ni + 2 * nwo + 2 * nwi)
    # cotas
    lam.cota((cx - bi, z(cf + hh)), (cx + bi, z(cf + hh)), -3.5 if not detalle else -5)
    lam.cota((cx - K, z(bot - dz.E_SOLADO)), (cx + K, z(bot - dz.E_SOLADO)), -6 if not detalle else -9)
    if detalle:
        lam.cota((cx - K, z(bot)), (cx - bi, z(bot)), -3.5); lam.cota((cx + bi, z(bot)), (cx + K, z(bot)), -3.5)
    xl = cx - K
    lam.cota((xl, z(bot)), (xl, z(cf)), -5, horizontal=False)
    lam.cota((xl, z(cf)), (xl, z(cf + hh)), -5, horizontal=False)
    lam.cota((xl, z(cf + hh)), (xl, z(top)), -5, horizontal=False)
    lam.cota((xl, z(bot - dz.E_SOLADO)), (xl, z(top)), -12, horizontal=False)
    # niveles
    lam.nivel((cx - bi + 0.12, z(cf)), cf, "CF %.3f" % cf, hmm=1.6)
    lam.nivel((cx + 0.10, z(top)), top, ("NPT +%.2f" % top) if p <= dz.P_VER else ("losa +%.3f" % top), hmm=1.6)
    lam.texto((cx + K + ext_l, z(ter) + 1.0 * f), "TIN %.2f" % ter, 1.4, "TEXTOS", TA.BOTTOM_RIGHT)
    yl = z(bot - dz.E_SOLADO) - (13.0 if detalle else 10.5) * f
    lam.texto((cx - K, yl), "LADO VIA (LINDERO)", 1.5, "TEXTOS", TA.TOP_LEFT)
    lam.texto((cx + K, yl), "LADO PREDIO", 1.5, "TEXTOS", TA.TOP_RIGHT)
    # llamadas en columna (sin cruces)
    if xt is None: xt = cx + K + 0.20 + 30 * f
    mt = ac["marco"]; sep = ac["sep"]
    its = [((cx + 0.40, z(top - es * 0.25)), ["losa superior e = %.2f" % es, "vaciada monolitica con los muros"]),
           ((cx - bi - 0.02, z(na)), ["NA %.3f (Q = %.0f L/s)" % (na, dz.Q(p))]),
           (pos["marco"], ["%smarco %s @%.2f" % ("2 " if ac["doble"] else "", mt, sep) + (" (ext. e int.)" if ac["doble"] else "")]),
           (pos["muro"], ["%d barras long. 3/8\" @%.2f" % (pos["nlong"], ac["long_sep"])]),
           ((cx + 0.40, z(cf - ef * 0.6)), ["losa de fondo e = %.2f" % ef]),
           ((cx + K - 0.02, z(bot - dz.E_SOLADO / 2)), ["solado f'c=100 e = 0.05"])]
    if p <= dz.P_VER: its.insert(1, ((cx + K + 0.012, z(top - 0.05)), ["junta 1\" tecnopor con la vereda"]))
    lam.columna_llamadas(its, xt, z(top) + 4 * f, z(bot - dz.E_SOLADO) - 2 * f, 1.6 if not detalle else 1.8)
    return (cx - K, yl - 4 * f, cx + K, max(z(top), z(ter)))


def dp04(doc, ox, oy):
    out = []
    grupos = (("DP-04A", dz.SECCIONES[:8]), ("DP-04B", dz.SECCIONES[8:]))
    for k, (cod, secs) in enumerate(grupos):
        n1, n2 = secs[0][0], secs[-1][0]
        lam = B.Lamina(doc, ox + k * 20.0, oy, 20, cod, "SECCIONES TRANSVERSALES DEL COLECTOR",
                       "SECCIONES S-%02d A S-%02d CON DISTRIBUCION DE ACERO - ESC. 1/20" % (n1, n2))
        f = lam.f
        for i, (n, p) in enumerate(secs):
            col, fila = i % 4, i // 4
            cxm = 30 + 46 + col * 201; cym = 450 - fila * 225
            cx, cy = lam.P(cxm, cym)
            bb = seccion(lam, cx, cy, p, num=n, xt=cx + 1.10 + 30 * f)
            lam.titulo_vista(cxm + 45, (bb[1] - lam.oy) / f - 6, "SECCION S-%02d" % n,
                             "PROG. %s - CF %.3f - %s - ESC. 1/20" % (pt(p), dz.CF(p), dz.tramo_txt(p)), ancho_mm=80)
        if len(secs) < 8:
            filas = []
            for n, p in dz.SECCIONES:
                em, ef, es = dz.esp(p); ac = dz.acero(p)
                filas.append(["S-%02d" % n, pt(p), dz.tramo_txt(p).replace("CRUCE VEHICULAR (AUTOS)", "CRUCE DE AUTOS"), "%.2f" % dz.h(p),
                              "%.2f / %.2f / %.2f" % (em, ef, es), ("2 x " if ac["doble"] else "") + "%s @%.2f" % (ac["marco"], ac["sep"])])
            lam.tabla(640, 318, ["SECCION", "PROGRESIVA", "TRAMO", "h", "MURO/FONDO/LOSA", "MARCOS"], filas, [16, 22, 46, 12, 34, 32],
                      hmm=1.6, alto_mm=4.6, titulo="CUADRO DE SECCIONES S-01 A S-15")
        lam.leyenda2(30, 100, [("concreto", "CONCRETO", "concreto armado f'c=210 kg/cm2"), ("rect", "SOLADO", "solado f'c=100 kg/cm2 e = 0.05"),
                               ("linea2", "ACERO", "marco de acero (barra cerrada con ganchos)"), ("bloque:ACERO-38", "ACERO-PUNTOS", "barra longitudinal (diametro real)"),
                               ("relleno", "AGUA-RELLENO", "agua con el caudal de diseno"), ("linea", "TERRENO", "vereda (NPT) y suelo contra el muro"),
                               ("discontinua", "TERRENO-EXISTENTE", "terreno natural en el eje (TIN)"), ("rect", "JUNTAS", "junta 1\" con tecnopor (lado predio)")], hmm=1.9, ancho_col=110, filas_col=4)
        lam.notas(262, 100, "NOTAS", [
            "1. Escala real 1/20; cotas en m. Recubrimiento: acero centrado en elementos de 0.10 m; 4.5 cm al eje en el cruce de camiones.",
            "2. Altura interior h segun el perfil longitudinal (DP-02 y DP-03); seccion tipica con detalles en DP-06A.",
            "3. Marcos 3/8\" @0.20 en vereda y tramo final, @0.15 en cruces de autos; 2 marcos 1/2\" @0.15 en cruce de camiones.",
            "4. El muro del lado de la via se vacia contra el terreno; junta de tecnopor 1\" con la vereda en el tramo 0+000 - 0+078.42."],
            hmm=1.7, ancho_mm=375)
        out.append(lam)
    return out


def dp06a(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 10, "DP-06A", "SECCIONES TIPICAS DEL COLECTOR",
                   "VEREDA, CRUCE DE AUTOS, CRUCE DE CAMIONES Y TRAMO FINAL - ARMADO Y ESPESORES - ESC. 1/10")
    f = lam.f
    tipos = [("A-A", 20.0, "TRAMO EN VEREDA (h variable 0.43 a 0.67)"), ("B-B", 10.0, "CRUCE DE AUTOS (marcos @0.15)"),
             ("C-C", 57.0, "CRUCE DE CAMIONES (muros 0.15, losas 0.20)"), ("D-D", 100.0, "TRAMO FINAL (h = 0.60)")]
    for i, (let, p, sub) in enumerate(tipos):
        col, fila = i % 2, i // 2
        cxm = 150 + col * 405; cym = 430 - fila * 255
        cx, cy = lam.P(cxm, cym)
        bb = seccion(lam, cx, cy, p, detalle=True, xt=cx + dz.b_ext(p) / 2 + 0.30 + 40 * f)
        lam.titulo_vista(cxm + 80, (bb[1] - lam.oy) / f - 6, "SECCION TIPICA %s" % let, "%s - ejemplo en %s, h = %.2f - ESC. 1/10" % (sub, pt(p), dz.h(p)), ancho_mm=120)
    lam.leyenda2(30, 100, [("concreto", "CONCRETO", "concreto armado f'c=210 kg/cm2"), ("rect", "SOLADO", "solado f'c=100 kg/cm2 e = 0.05"),
                           ("linea2", "ACERO", "marco de acero (con ganchos a 135 grados)"), ("bloque:ACERO-38", "ACERO-PUNTOS", "barra longitudinal 3/8\""),
                           ("relleno", "AGUA-RELLENO", "agua con el caudal de diseno"), ("linea", "TERRENO", "vereda (NPT) y suelo contra el muro"),
                           ("discontinua", "TERRENO-EXISTENTE", "terreno natural en el eje (TIN)"), ("rect", "JUNTAS", "junta 1\" con tecnopor")],
                 hmm=1.9, ancho_col=110, filas_col=4)
    lam.notas(262, 100, "NOTAS", [
        "1. Concreto f'c=210 kg/cm2 en losa de fondo, muros y losa superior (vaciado monolitico); acero fy=4200 kg/cm2.",
        "2. Marcos con ganchos a 135 grados de 6 diametros; traslape de barras longitudinales 0.40 m (3/8\").",
        "3. En el cruce de camiones (0+054.00 - 0+060.00) muros de 0.15 y losas de 0.20 con doble marco 1/2\" @0.15.",
        "4. La altura interior de cada seccion se toma del perfil longitudinal (DP-03); las cotas de estas vistas son del ejemplo indicado."],
        hmm=1.7, ancho_mm=375)
    return lam


# ============================================================================== DP-06B (registro) y DP-06C (empalme y junta)
def dp06b(doc, ox, oy):
    """La lamina detallada de dxf_tapa_m.py (papel A1 en mm) insertada a escala 1/10 en su sitio, con el rotulo del juego."""
    import subprocess, tempfile, ezdxf
    from ezdxf.addons import Importer
    from ezdxf.math import Matrix44
    lam = B.Lamina(doc, ox, oy, 10, "DP-06B", "DETALLE DE REGISTRO DE LIMPIEZA - TAPA 0.68 x 0.68 C/MARCO Y CONTRAMARCO",
                   "PLANTA, CORTE, ASIENTO EN REBAJE, ARMADO, CONTRAMARCO, PERFILES, ISOMETRICO Y MATERIALES - ESC. INDICADAS")
    fuente = os.path.join(tempfile.gettempdir(), "dp06b_mujeres_fuente.dxf")
    subprocess.run([sys.executable, os.path.join(AQUI, "dxf_tapa_m.py"), fuente], check=True, capture_output=True)
    src = ezdxf.readfile(fuente); sm = src.modelspace()
    for d in list(sm.query("DIMENSION")): d.explode()
    def fuera(e):
        if e.dxf.layer in ("LAMINA", "MEMBRETE"): return True
        try:
            p = e.dxf.insert
            return p.x >= 588 and p.y <= 92
        except Exception:
            return False
    ents = [e for e in sm if not fuera(e)]
    msp = doc.modelspace(); antes = {e.dxf.handle for e in msp}
    imp = Importer(src, doc); imp.import_entities(ents, msp); imp.finalize()
    M = Matrix44.chain(Matrix44.translate(-15, -12, 0), Matrix44.scale(0.984), Matrix44.translate(27, 12, 0),
                       Matrix44.scale(lam.f), Matrix44.translate(lam.ox, lam.oy, 0))
    for e in msp:
        if e.dxf.handle not in antes:
            e.transform(M)
    return lam


# ============================================================================== DP-05 ISOMETRICOS DE SECCIONES
def _hatch_rgb(lam, pts, capa, huecos=()):
    h = lam.msp.add_hatch(dxfattribs={"layer": capa}); rgb = B.COLOR_RGB[capa]; h.rgb = rgb; h.set_solid_fill(rgb=rgb)
    h.paths.add_polyline_path(pts, is_closed=True, flags=1)
    for hp in huecos: h.paths.add_polyline_path(hp, is_closed=True, flags=16)
    return h


def iso_seccion(lam, o, p, Ls=1.2, llamadas=True, xt=None):
    """Tramo de colector de longitud Ls cortado en la progresiva p (cara frontal = seccion), a escala real.
    o: punto del modelo donde cae el eje a la cota de fondo en la cara de corte."""
    f = lam.f
    em, ef, es = dz.esp(p); hh = dz.h(p); bi = dz.b / 2; K = dz.b_ext(p) / 2; cf = dz.CF(p)
    bot, top, na = cf - ef, cf + hh + es, dz.NA(p)
    def T(x, y, z):
        u, v = B.iso(x, y - Ls, z - cf)
        return (o[0] + u, o[1] + v)
    def cara(pts3, capa, aristas=True):
        pts = [T(*q) for q in pts3]
        lam.solido([pts[0], pts[1], pts[3], pts[2]], capa)
        if aristas: lam.poli(pts, "ISO-ARISTAS", cerrada=True)
        return pts
    # orden de pintado: solado, interior visto por la boca, caras exteriores y al final la cara de corte
    sb, st = bot - dz.E_SOLADO, bot
    cara([(K + .05, 0, sb), (K + .05, Ls, sb), (K + .05, Ls, st), (K + .05, 0, st)], "ISO-CONCRETO-LAT2")
    cara([(-K - .05, Ls, sb), (K + .05, Ls, sb), (K + .05, Ls, st), (-K - .05, Ls, st)], "ISO-CONCRETO-LAT1")
    cara([(-bi, 0, cf), (-bi, Ls, cf), (-bi, Ls, cf + hh), (-bi, 0, cf + hh)], "ISO-CONCRETO-LAT2")
    cara([(-bi, 0, cf), (bi, 0, cf), (bi, Ls, cf), (-bi, Ls, cf)], "ISO-CONCRETO-SUP")
    cara([(-bi, 0, na), (bi, 0, na), (bi, Ls, na), (-bi, Ls, na)], "ISO-AGUA")
    cara([(K, 0, bot), (K, Ls, bot), (K, Ls, top), (K, 0, top)], "ISO-CONCRETO-LAT2")
    cara([(-K, 0, top), (K, 0, top), (K, Ls, top), (-K, Ls, top)], "ISO-CONCRETO-SUP")
    # cara de corte (anillo de concreto) y agua en el corte
    ext = [T(-K, Ls, bot), T(K, Ls, bot), T(K, Ls, top), T(-K, Ls, top)]
    inn = [T(-bi, Ls, cf), T(bi, Ls, cf), T(bi, Ls, cf + hh), T(-bi, Ls, cf + hh)]
    _hatch_rgb(lam, ext, "ISO-CONCRETO-LAT1", [inn]); lam.poli(ext, "ISO-ARISTAS", cerrada=True); lam.poli(inn, "ISO-ARISTAS", cerrada=True)
    wa = [T(-bi, Ls, cf), T(bi, Ls, cf), T(bi, Ls, na), T(-bi, Ls, na)]
    _hatch_rgb(lam, wa, "AGUA-RELLENO"); lam.poli([wa[3], wa[2]], "AGUA")
    # acero en la cara de corte
    ac = dz.acero(p)
    def marco(x0, z0, x1, z1, d):
        lam.poli([T(x0, Ls, z0), T(x1, Ls, z0), T(x1, Ls, z1), T(x0, Ls, z1)], "ACERO", cerrada=True, ancho=d)
    if not ac["doble"]:
        x0, x1, z0, z1 = -bi - em / 2, bi + em / 2, cf - ef / 2, top - es / 2
        marco(x0, z0, x1, z1, D38); pm = T(x1, Ls, (z0 + z1) / 2)
        for i in range(8):
            xx = x0 + D38 + i * (x1 - x0 - 2 * D38) / 7
            for zz in (z0 + D38, z1 - D38): lam.bloque("ACERO-38", T(xx, Ls, zz), 1.0)
        n = ac["n_muro"]
        for k in range(n):
            zz = z0 + (z1 - z0) * (k + 1) / (n + 1)
            for xx in (x0 + D38, x1 - D38): lam.bloque("ACERO-38", T(xx, Ls, zz), 1.0)
        pl = T(x1 - D38, Ls, z0 + (z1 - z0) / (n + 1)); nl = 16 + 2 * n
    else:
        c = 0.045
        marco(-K + c, bot + c, K - c, top - c, D12); marco(-bi - c, cf - c, bi + c, cf + hh + c, D12)
        pm = T(K - c, Ls, (bot + top) / 2); pl = T(K - c - 0.011, Ls, cf + 0.15); nl = 50
        for i in range(10):
            xx = -K + c + 0.011 + i * (2 * K - 2 * c - 0.022) / 9
            for zz in (bot + c + 0.011, top - c - 0.011): lam.bloque("ACERO-38", T(xx, Ls, zz), 1.0)
    # cotas sobre la cara de corte
    if llamadas:
        lam.juntar_llamadas()
        xt = xt if xt is not None else T(K, 0, top)[0] + 12 * f
        y0 = T(-K, Ls, top)[1] + 20 * f; dy = 7.2 * f
        its = [(T(0.2, Ls * 0.5, top), ["losa superior e = %.2f" % es]), (T(-bi + 0.3, Ls, na), ["agua NA %.3f" % na]),
               (pm, [("2 marcos " if ac["doble"] else "marco ") + "%s @%.2f" % (ac["marco"], ac["sep"])]),
               (pl, ["%d barras long. 3/8\" @%.2f" % (nl, ac["long_sep"])]), (T(K, Ls * 0.5, (bot + cf) / 2 + 0.1), ["muro e = %.2f" % em]),
               (T(0.3, Ls, bot + ef / 2), ["losa de fondo e = %.2f" % ef]), (T(K + 0.05, Ls * 0.6, sb + 0.02), ["solado e = 0.05"])]
        lam._col = None
        lam.columna_llamadas(its, xt, y0, y0 - dy * (len(its) - 1), 1.6)
    return T


def dp05(doc, ox, oy):
    out = []
    grupos = (("DP-05A", dz.SECCIONES[:8]), ("DP-05B", dz.SECCIONES[8:]))
    for k, (cod, secs) in enumerate(grupos):
        n1, n2 = secs[0][0], secs[-1][0]
        lam = B.Lamina(doc, ox + k * 25.0, oy, 25, cod, "ISOMETRICOS DE LAS SECCIONES TRANSVERSALES",
                       "SECCIONES S-%02d A S-%02d - TRAMO DE 1.20 m CORTADO EN CADA SECCION, CON ACERO Y AGUA DE DISENO - ESC. 1/25" % (n1, n2))
        f = lam.f
        for i, (n, p) in enumerate(secs):
            col, fila = i % 4, i // 4
            cxm = 30 + 62 + col * 201; cym = 405 - fila * 230
            T = iso_seccion(lam, lam.P(cxm, cym), p, xt=lam.P(cxm + 70, 0)[0])
            lam.titulo_vista(cxm + 40, cym - 62, "ISOMETRICO S-%02d" % n,
                             "PROG. %s - interior %.2f x %.2f m - %s" % (pt(p), dz.b, dz.h(p), dz.tramo_txt(p)), ancho_mm=80)
        lam.leyenda2(30, 100, [("relleno", "ISO-CONCRETO-SUP", "concreto: cara superior"), ("relleno", "ISO-CONCRETO-LAT1", "concreto: cara de corte (seccion)"),
                               ("relleno", "ISO-CONCRETO-LAT2", "concreto: caras laterales"), ("relleno", "AGUA-RELLENO", "agua con el caudal de diseno"),
                               ("linea2", "ACERO", "marco de acero en la cara de corte"), ("bloque:ACERO-38", "ACERO-PUNTOS", "barra longitudinal (diametro real)")],
                     hmm=1.9, ancho_col=110, filas_col=3)
        lam.notas(262, 100, "NOTAS", [
            "1. Isometricos a escala real 1/25 (sin exageracion vertical); el tramo dibujado tiene 1.20 m de largo.",
            "2. La cara de corte coincide con la seccion transversal de la lamina DP-04 en la misma progresiva.",
            "3. Lado de la via a la izquierda y lado del predio a la derecha de cada isometrico."], hmm=1.7, ancho_mm=375)
        out.append(lam)
    return out


# ============================================================================== DP-06C EMPALME DE CUNETA Y JUNTA DE DILATACION
def dp06c(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 10, "DP-06C", "DETALLE DEL EMPALME DE CUNETA AL COLECTOR Y DE LA JUNTA DE DILATACION",
                   "EJES 02, 07, 10 Y 12 (4 und): PLANTA, CORTE POR LA CUNETA, VENTANA EN EL MURO Y JUNTA e = 1\" - ESC. INDICADAS")
    f = lam.f; bi, K, e = dz.b / 2, dz.b_ext(10) / 2, 0.10
    p_ej = 37.95; cf = dz.CF(p_ej); hh = dz.h(p_ej); top = dz.techo(p_ej); ncf = 258.74
    # ---------------- E1 planta (eje del colector horizontal; la cuneta llega desde el predio, arriba)
    o = lam.P(150, 392)
    X = lambda u: o[0] + u; Y = lambda v: o[1] + v
    L = 0.95
    lam.relleno([(X(-L), Y(-K)), (X(L), Y(-K)), (X(L), Y(K)), (X(-L), Y(K))], "CONCRETO-ACHURADO")
    for v in (-K, K): lam.linea((X(-L), Y(v)), (X(L), Y(v)), "CONCRETO")
    for v in (-bi, bi): lam.linea((X(-L), Y(v)), (X(L), Y(v)), "CONCRETO-OCULTO")
    lam.linea((X(-L - 0.1), Y(0)), (X(L + 0.1), Y(0)), "EJE-COLECTOR")
    lam.bloque("REGISTRO-PLANTA", (X(0), Y(0)), 1.0)
    lam.rect(X(-0.30), Y(K + 0.025), X(0.30), Y(K + 0.70), "CUNETA"); lam.rect(X(-0.20), Y(K + 0.025), X(0.20), Y(K + 0.70), "CUNETA-OCULTA")
    lam.rect(X(-0.20), Y(bi), X(0.20), Y(K), "CONCRETO-OCULTO")
    lam.rect(X(-0.30), Y(K), X(0.30), Y(K + 0.025), "JUNTAS")
    lam.flecha((X(0.0), Y(K + 0.62)), (X(0.0), Y(K + 0.12)), "FLUJO", 3.0)
    lam.flecha((X(0.45), Y(-0.20)), (X(0.85), Y(-0.20)), "FLUJO", 3.0)
    lam.cota((X(-0.20), Y(K + 0.70)), (X(0.20), Y(K + 0.70)), 6); lam.cota((X(-0.30), Y(K + 0.70)), (X(0.30), Y(K + 0.70)), 13)
    lam.cota((X(L), Y(-K)), (X(L), Y(K)), 8, horizontal=False)
    lam.cota((X(L), Y(-bi)), (X(L), Y(bi)), 16, horizontal=False)
    lam.juntar_llamadas()
    xt = lam.P(275, 0)[0]
    lam.llamada((X(0.25), Y(K + 0.5)), (xt, Y(K + 0.65)), ["cuneta 0.40 m que llega del eje (rejilla a nivel de vereda)"], 1.8)
    lam.llamada((X(0.10), Y(bi + 0.05)), (xt, Y(K + 0.6)), ["ventana 0.40 x 0.30 en el muro del lado del predio"], 1.8)
    lam.llamada((X(0.28), Y(K + 0.012)), (xt, Y(K + 0.3)), ["junta 1\" con sello elastomerico entre cuneta y colector"], 1.8)
    lam.llamada((X(0.25), Y(0.25)), (xt, Y(0.0)), ["registro de limpieza encima del empalme (DP-06B)"], 1.8)
    lam.llamada((X(-0.70), Y(-0.45)), (xt, Y(-0.5)), ["losa superior del colector (vereda)"], 1.8)
    lam.volcar_llamadas()
    lam.titulo_vista(150, 288, "E1. PLANTA DEL EMPALME", "ESC. 1/10 - ejemplo: Eje 07 en el registro R-05 (0+037.95)", ancho_mm=150)
    # ---------------- E2 corte por el eje de la cuneta (transversal al colector)
    o = lam.P(130, 205)
    X = lambda u: o[0] + u; Z = lambda z: o[1] + (z - cf)
    bot = cf - 0.10
    ext = [(X(-K), Z(bot)), (X(K), Z(bot)), (X(K), Z(top)), (X(-K), Z(top))]
    inn = [(X(-bi), Z(cf)), (X(bi), Z(cf)), (X(bi), Z(cf + hh)), (X(-bi), Z(cf + hh))]
    ven = [(X(bi), Z(ncf)), (X(K), Z(ncf)), (X(K), Z(ncf + 0.30)), (X(bi), Z(ncf + 0.30))]
    h_ = lam.msp.add_hatch(dxfattribs={"layer": "CONCRETO-ACHURADO"}); h_.rgb = B.COLOR_RGB["CONCRETO-ACHURADO"]; h_.set_solid_fill(rgb=B.COLOR_RGB["CONCRETO-ACHURADO"])
    h_.paths.add_polyline_path(ext, is_closed=True, flags=1); h_.paths.add_polyline_path(inn, is_closed=True, flags=16)
    lam.poli(ext, "CONCRETO", cerrada=True); lam.poli(inn, "CONCRETO", cerrada=True)
    lam.relleno(ven, "AGUA-RELLENO"); lam.poli(ven, "CONCRETO", cerrada=True)
    lam.rect(X(-K - 0.05), Z(bot - 0.05), X(K + 0.05), Z(bot), "SOLADO")
    # registro encima (tapa en el rebaje)
    lam.rect(X(-0.34), Z(top - 0.08), X(0.34), Z(top), "REGISTRO")
    # cuneta (referencia): interior 0.40 de alto H hasta la vereda, piso en NCF, muros 0.10
    xc0 = K + 0.025; xc1 = xc0 + 1.10
    lam.poli([(X(xc0), Z(ncf)), (X(xc1), Z(ncf + 0.004))], "CUNETA")
    lam.poli([(X(xc0), Z(ncf - 0.10)), (X(xc1), Z(ncf - 0.10))], "CUNETA")
    lam.poli([(X(xc0), Z(top)), (X(xc1), Z(top))], "TERRENO")
    lam.rect(X(K), Z(ncf - 0.10), X(xc0), Z(top), "JUNTAS")
    lam.relleno([(X(K), Z(ncf)), (X(xc1), Z(ncf)), (X(xc1), Z(ncf + 0.06)), (X(K), Z(ncf + 0.06))], "AGUA-RELLENO")
    lam.flecha((X(bi + 0.02), Z(ncf + 0.03)), (X(bi - 0.12), Z(cf + 0.05)), "FLUJO", 2.5)
    na = dz.NA(p_ej)
    lam.relleno([(X(-bi), Z(cf)), (X(bi), Z(cf)), (X(bi), Z(na)), (X(-bi), Z(na))], "AGUA-RELLENO")
    lam.cota((X(K), Z(ncf)), (X(K), Z(ncf + 0.30)), 14, horizontal=False)
    lam.cota((X(-K), Z(cf)), (X(-K), Z(ncf)), -6, horizontal=False)
    lam.cota((X(-K), Z(bot)), (X(K), Z(bot)), -8)
    lam.nivel((X(xc0 + 0.6), Z(ncf)), ncf, "NCF %.2f" % ncf, hmm=1.7)
    lam.nivel((X(-0.4), Z(cf)), cf, "CF %.3f" % cf, hmm=1.7)
    lam.nivel((X(-0.55), Z(top)), top, "NPT +%.2f" % top, hmm=1.7)
    lam.juntar_llamadas()
    xt = lam.P(330, 0)[0]
    lam.llamada((X(K - 0.05), Z(ncf + 0.20)), (xt, Z(top + 0.10)), ["ventana 0.40 x 0.30 dejada al vaciar el muro"], 1.8)
    lam.llamada((X(K + 0.012), Z(ncf + 0.25)), (xt, Z(top)), ["junta 1\": poliestireno + sello elastomerico"], 1.8)
    lam.llamada((X(bi - 0.05), Z(cf + 0.20)), (xt, Z(cf + 0.3)), ["caida libre al fondo del colector"], 1.8)
    lam.llamada((X(0.0), Z(top - 0.04)), (xt, Z(top + 0.2)), ["tapa del registro (DP-06B)"], 1.8)
    lam.volcar_llamadas()
    lam.titulo_vista(150, 160, "E2. CORTE POR EL EJE DE LA CUNETA", "ESC. 1/10 - cotas del Eje 07 (R-05)", ancho_mm=150)
    # ---------------- E3 vista del muro del lado del predio (elevacion interior) con la ventana
    o = lam.P(520, 440); X = lambda u: o[0] + u; Z = lambda z: o[1] + (z - cf)
    lam.relleno([(X(-1.0), Z(cf)), (X(1.0), Z(cf)), (X(1.0), Z(cf + hh)), (X(-1.0), Z(cf + hh))], "CONCRETO-ACHURADO")
    lam.rect(X(-1.0), Z(cf), X(1.0), Z(cf + hh), "CONCRETO")
    lam.rect(X(-0.20), Z(ncf), X(0.20), Z(ncf + 0.30), "CONCRETO"); lam.relleno([(X(-0.20), Z(ncf)), (X(0.20), Z(ncf)), (X(0.20), Z(ncf + 0.30)), (X(-0.20), Z(ncf + 0.30))], "AGUA-RELLENO")
    for xx in (-0.20, 0.20):
        for zz in (ncf - 0.04, ncf + 0.34): pass
    lam.linea((X(-0.40), Z(ncf - 0.05)), (X(0.40), Z(ncf - 0.05)), "ACERO"); lam.linea((X(-0.40), Z(ncf + 0.35)), (X(0.40), Z(ncf + 0.35)), "ACERO")
    lam.cota((X(-0.20), Z(cf + hh)), (X(0.20), Z(cf + hh)), 6)
    lam.cota((X(0.20), Z(ncf)), (X(0.20), Z(ncf + 0.30)), 10, horizontal=False)
    lam.cota((X(1.0), Z(cf)), (X(1.0), Z(cf + hh)), 8, horizontal=False)
    lam.llamada((X(0.35), Z(ncf + 0.35)), lam.P(660, 470), ["2 barras 3/8\" adicionales L = 0.80 sobre y bajo la ventana"], 1.8)
    lam.titulo_vista(520, 380, "E3. VISTA DEL MURO CON LA VENTANA", "ESC. 1/10 - cara interior del muro del lado del predio", ancho_mm=150)
    # ---------------- J junta de dilatacion (corte por el muro)
    o = lam.P(470, 230); X = lambda u: o[0] + u; Y = lambda v: o[1] + v
    for s_ in (-1, 1):
        a0 = 0.0127 * s_; a1 = 0.45 * s_
        pl = [(X(min(a0, a1)), Y(0)), (X(max(a0, a1)), Y(0)), (X(max(a0, a1)), Y(0.10)), (X(min(a0, a1)), Y(0.10))]
        lam.relleno(pl, "CONCRETO-ACHURADO"); lam.poli(pl, "CONCRETO", cerrada=True)
    lam.rect(X(-0.0127), Y(0.0), X(0.0127), Y(0.085), "JUNTAS")
    lam.rect(X(-0.0127), Y(0.085), X(0.0127), Y(0.10), "CORTES")
    lam.cota((X(-0.0127), Y(0.10)), (X(0.0127), Y(0.10)), 8, texto='1"')
    lam.cota((X(0.45), Y(0)), (X(0.45), Y(0.10)), 8, horizontal=False)
    lam.juntar_llamadas()
    lam.llamada((X(0.0), Y(0.04)), lam.P(560, 250), ["relleno de poliestireno expandido e = 1\""], 1.8)
    lam.llamada((X(0.0), Y(0.093)), lam.P(560, 262), ["sello elastomerico de poliuretano 1.5 cm"], 1.8)
    lam.volcar_llamadas()
    lam.titulo_vista(470, 200, "J. JUNTA DE DILATACION", "ESC. 1/10 - en muros, losa de fondo y losa superior (33 und)", ancho_mm=150)
    # cuadro de empalmes
    regp = {r["nombre"]: r["prog"] for r in dz.REGISTROS}
    filas = [[e_, rn, pt(regp[rn]), "%.2f" % n_, "%.3f" % dz.CF(regp[rn]), "%.2f" % (n_ - dz.CF(regp[rn]))] for e_, rn, n_ in dz.CUNETAS]
    lam.tabla(640, 560, ["CUNETA", "REGISTRO", "PROGRESIVA", "NCF", "CF COLECTOR", "CAIDA (m)"], filas, [24, 22, 26, 20, 28, 24],
              hmm=1.8, alto_mm=6.0, titulo="CUADRO DE EMPALMES DE CUNETA (4 und)")
    lam.notas(640, 500, "NOTAS", [
        "1. La ventana 0.40 x 0.30 se deja al vaciar el muro del lado del predio, centrada bajo el registro.",
        "2. El piso de la ventana coincide con la cota de fondo de la cuneta (NCF); el agua cae libre al colector.",
        "3. Juntas de dilatacion e = 1\" cada 4.00 m y en los extremos del cruce de camiones: 33 und.",
        "4. Junta de tecnopor 1\" entre la losa del colector y la vereda en el tramo 0+000 - 0+078.42."], hmm=1.7, ancho_mm=185)
    lam.leyenda2(30, 100, [("concreto", "CONCRETO", "concreto armado del colector"), ("rect", "CUNETA", "cuneta que llega (referencia)"),
                           ("rect", "JUNTAS", "junta e = 1\""), ("relleno", "AGUA-RELLENO", "agua"),
                           ("discontinua", "CONCRETO-OCULTO", "cara oculta / ventana en planta"), ("bloque:SIMB-FLECHA", "0", "sentido del flujo")],
                 hmm=1.9, ancho_col=110, filas_col=3)
    return lam


# ============================================================================== DP-07 ESTRUCTURA DE SALIDA
def _piedras(lam, pts_poly, xs, ys, r):
    """piedras del emboquillado dentro de un poligono (patron fijo)"""
    from ezdxf.math import is_point_in_polygon_2d, Vec2
    pol = [Vec2(p) for p in pts_poly]
    k = 0
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            q = (x + (0.5 * r if j % 2 else 0), y)
            if is_point_in_polygon_2d(Vec2(q), pol) == 1:
                lam.circulo(q, r * (0.75 + 0.25 * ((i * 7 + j * 3) % 4) / 3), "ISO-PIEDRA"); k += 1


def dp07(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 25, "DP-07", "ESTRUCTURA DE SALIDA CON DOS ALEROS Y EMBOQUILLADO",
                   "PLANTA, ELEVACION FRONTAL, CORTES A-A Y B-B, ARMADO Y CUADRO DE METRADOS - PROG. 0+139.08 - DENTRO DEL LINDERO")
    f = lam.f; bi, K = dz.b / 2, dz.b_ext(dz.L) / 2
    cf = dz.CFS; top = cf + dz.H_FIN + 0.10; na = dz.NA(dz.L)
    av, e = dz.AL_AV, dz.AL_E; vf = bi + av                       # 0.707 de avance; ancho final 2.914
    s2 = math.sqrt(0.5); nx, ny = -s2 * e, s2 * e                  # normal exterior del alero (lado +v)
    zt = (258.30 - dz.ZAP_H + 0.0)                                 # cara superior de la zapata = 258.10
    # ---------------- PLANTA (flujo hacia la izquierda, como en DP-01; predio arriba)
    o = lam.P(205, 452); X = lambda u: o[0] - u; Y = lambda v: o[1] + v
    Pp = lambda u, v: (X(u), Y(v))
    for sv in (-1, 1):
        lam.poli([Pp(-1.30, sv * K), Pp(0, sv * K)], "CONCRETO")
        lam.poli([Pp(-1.30, sv * bi), Pp(0, sv * bi)], "CONCRETO-OCULTO")
        al = [Pp(0, sv * bi), Pp(av, sv * vf), Pp(av + nx, sv * (vf + ny)), Pp(nx, sv * (bi + ny))]
        lam.relleno(al, "CONCRETO-ACHURADO"); lam.poli(al, "CONCRETO", cerrada=True)
        za = 0.45 * s2
        lam.poli([Pp(0, sv * bi), Pp(av, sv * vf), Pp(av - za, sv * (vf + za)), Pp(-za, sv * (bi + za)), Pp(0, sv * bi)], "CONCRETO-OCULTO")
    lam.relleno([Pp(-1.30, -K), Pp(0, -K), Pp(0, K), Pp(-1.30, K)], "CONCRETO-ACHURADO")
    lam.poli([Pp(0, -K), Pp(0, K)], "CONCRETO")
    for sv in (-1, 1): lam.poli([Pp(-1.30, sv * (K + 0.05)), Pp(-1.38, sv * 0.2 * 0 + sv * (K + 0.05))], "CONCRETO") if False else None
    lam.poli([Pp(-1.30, -K - 0.08), Pp(-1.30, -0.05), Pp(-1.34, 0.0), Pp(-1.26, 0.05), Pp(-1.30, 0.10), Pp(-1.30, K + 0.08)], "CONCRETO")
    emb = [Pp(0, -bi), Pp(av, -vf), Pp(av, vf), Pp(0, bi)]
    lam.poli(emb, "POZA", cerrada=True)
    _piedras(lam, emb, [X(u) for u in [0.06 + 0.12 * i for i in range(7)]], [Y(v) for v in [-1.45 + 0.12 * j for j in range(25)]], 0.045)
    una = [Pp(av, -dz.ANCHO_FIN / 2 - 0.15), Pp(av + dz.UNA_B1, -dz.ANCHO_FIN / 2 - 0.15), Pp(av + dz.UNA_B1, dz.ANCHO_FIN / 2 + 0.15), Pp(av, dz.ANCHO_FIN / 2 + 0.15)]
    lam.relleno(una, "ISO-PIEDRA"); lam.poli(una, "POZA", cerrada=True)
    lam.poli([Pp(-1.45, 0), Pp(av + 0.6, 0)], "EJE-COLECTOR")
    lam.flecha(Pp(-0.9, 0.25), Pp(-0.2, 0.25), "FLUJO", 3.0) if False else lam.flecha(Pp(-1.0, 0.30), Pp(-0.35, 0.30), "FLUJO", 3.0)
    lam.flecha(Pp(0.25, 0.30), Pp(1.30, 0.30), "FLUJO", 3.0)
    # cortes: A-A por el eje, B-B perpendicular al alero superior (por su punto medio)
    def marca(p, q, let):
        dx, dy = q[0] - p[0], q[1] - p[1]; Lm = math.hypot(dx, dy); ux, uy = dx / Lm, dy / Lm
        for (c, sg) in ((p, -1), (q, 1)):
            c2 = (c[0] + sg * ux * 5 * f, c[1] + sg * uy * 5 * f)
            lam.poli([c, c2], "CORTES", ancho=0.5 * f)
            lam.texto((c2[0] + sg * ux * 2.5 * f, c2[1] + sg * uy * 2.5 * f), let, 3.0, "CORTES", TA.MIDDLE_CENTER)
        lam.linea(p, q, "CORTES") if False else None
    marca(Pp(-1.25, 0.0), Pp(av + dz.UNA_B1 + 0.30, 0.0), "A")
    mu, mv = av / 2, bi + av / 2
    marca(Pp(mu + 0.25 * s2, mv - 0.25 * s2), Pp(mu - 0.75 * s2, mv + 0.75 * s2), "B")
    # cotas
    lam.cota(Pp(0, -bi), Pp(0, bi), 14, horizontal=False) if False else lam.cota(Pp(-0.6, -bi), Pp(-0.6, bi), -0.0001, horizontal=False)
    lam.cota(Pp(av, -vf), Pp(av, vf), 0.0001, horizontal=False)
    lam.cota(Pp(av, -vf), Pp(0, -vf), -10)
    lam.cota(Pp(av + dz.UNA_B1, -dz.ANCHO_FIN / 2 - 0.15), Pp(av, -dz.ANCHO_FIN / 2 - 0.15), -18)
    lam.cota(Pp(av + dz.UNA_B1, -dz.ANCHO_FIN / 2 - 0.15), Pp(av + dz.UNA_B1, dz.ANCHO_FIN / 2 + 0.15), 8, horizontal=False)
    lam.cota(Pp(0, bi), Pp(av, vf), 6, angulo=True)
    lam.texto(Pp(-0.65, K + 0.15), "LADO PREDIO", 1.6, "TEXTOS", TA.BOTTOM_CENTER)
    lam.texto(Pp(-0.65, -K - 0.15), "LADO VIA (LINDERO)", 1.6, "TEXTOS", TA.TOP_CENTER)
    lam.juntar_llamadas()
    xt = lam.P(262, 0)[0]
    lam.llamada(Pp(av * 0.5 - 0.05, vf * 0.7 + 0.05), (xt, Y(1.75)), ["alero de concreto armado e = 0.15, L = 1.00 a 45 grados"], 1.7)
    lam.llamada(Pp(av - 0.45 * s2 + 0.05, vf + 0.25), (xt, Y(1.35)), ["zapata del alero 0.45 x 0.20 (oculta)"], 1.7)
    lam.llamada(Pp(0.35, -0.3), (xt, Y(0.6)), ["emboquillado de piedra e = 0.20 con concreto f'c=140"], 1.7)
    lam.llamada(Pp(av + 0.17, -1.2), (xt, Y(-0.4)), ["una de concreto ciclopeo f'c=140 + 30% P.M."], 1.7)
    lam.llamada(Pp(-0.6, -0.55), (xt, Y(-1.2)), ["fin del colector cubierto (losa superior +259.00)"], 1.7)
    lam.volcar_llamadas()
    lam.titulo_vista(150, 362, "PLANTA", "PROG. 0+139.08 - CF 258.30 - ESC. 1/25", ancho_mm=110)
    # ---------------- ELEVACION FRONTAL (mirando hacia aguas arriba; el predio queda a la izquierda)
    o = lam.P(560, 450); Xe = lambda v: o[0] - v; Ze = lambda z: o[1] + (z - cf)
    ext = [(Xe(-K), Ze(cf - 0.10)), (Xe(K), Ze(cf - 0.10)), (Xe(K), Ze(top)), (Xe(-K), Ze(top))]
    inn = [(Xe(-bi), Ze(cf)), (Xe(bi), Ze(cf)), (Xe(bi), Ze(cf + dz.H_FIN)), (Xe(-bi), Ze(cf + dz.H_FIN))]
    _hatch_rgb(lam, ext, "CONCRETO-ACHURADO", [inn]); lam.poli(ext, "CONCRETO", cerrada=True); lam.poli(inn, "CONCRETO", cerrada=True)
    lam.relleno([(Xe(-bi), Ze(cf)), (Xe(bi), Ze(cf)), (Xe(bi), Ze(na)), (Xe(-bi), Ze(na))], "AGUA-RELLENO")
    for sv in (-1, 1):
        al = [(Xe(sv * bi), Ze(cf)), (Xe(sv * vf), Ze(cf)), (Xe(sv * (vf + ny)), Ze(cf)), (Xe(sv * (vf + ny)), Ze(cf + dz.AL_H1)),
              (Xe(sv * vf), Ze(cf + dz.AL_H1)), (Xe(sv * K), Ze(cf + dz.AL_H0 - (K - bi) / av * (dz.AL_H0 - dz.AL_H1))), (Xe(sv * K), Ze(top))]
        lam.relleno(al, "ISO-CONCRETO-LAT1"); lam.poli(al, "CONCRETO", cerrada=True)
        lam.poli([(Xe(sv * vf), Ze(cf)), (Xe(sv * vf), Ze(cf + dz.AL_H1))], "CONCRETO")
        lam.poli([(Xe(sv * bi), Ze(zt - dz.ZAP_H)), (Xe(sv * (vf + 0.45 * s2)), Ze(zt - dz.ZAP_H)), (Xe(sv * (vf + 0.45 * s2)), Ze(zt)), (Xe(sv * bi), Ze(zt))], "CONCRETO-OCULTO")
    lam.poli([(Xe(-vf - 0.4), Ze(cf)), (Xe(vf + 0.4), Ze(cf))], "TERRENO")
    hw = dz.ANCHO_FIN / 2 + 0.15
    lam.poli([(Xe(-hw), Ze(cf)), (Xe(-hw), Ze(cf - dz.UNA_H)), (Xe(hw), Ze(cf - dz.UNA_H)), (Xe(hw), Ze(cf))], "CONCRETO-OCULTO")
    lam.cota((Xe(bi), Ze(cf)), (Xe(-bi), Ze(cf)), -4)
    lam.cota((Xe(vf), Ze(cf - dz.UNA_H)), (Xe(-vf), Ze(cf - dz.UNA_H)), -6)
    lam.cota((Xe(-vf - ny), Ze(cf)), (Xe(-vf - ny), Ze(cf + dz.AL_H1)), -6, horizontal=False)
    lam.cota((Xe(-K), Ze(cf)), (Xe(-K), Ze(top)), -14, horizontal=False) if False else None
    lam.cota((Xe(hw), Ze(cf)), (Xe(hw), Ze(cf - dz.UNA_H)), 8, horizontal=False)
    lam.nivel((Xe(0.35), Ze(top)), top, "losa +%.2f" % top, hmm=1.7)
    lam.nivel((Xe(-0.30), Ze(cf)), cf, "CF %.2f" % cf, hmm=1.7)
    lam.nivel((Xe(0.40), Ze(na)), na, "NA %.3f" % na, hmm=1.6)
    lam.texto((Xe(vf + 0.45), Ze(cf + 0.05)), "berma de la Crta. Oasis (cresta 258.54)", 1.6, "TEXTOS", TA.BOTTOM_RIGHT) if False else \
        lam.texto((Xe(-vf - 0.40), Ze(cf - 0.03)), "berma (cresta de la via 258.54)", 1.5, "TEXTOS", TA.TOP_RIGHT)
    lam.texto((Xe(vf + 0.30), Ze(top + 0.12)), "LADO PREDIO", 1.6, "TEXTOS", TA.BOTTOM_LEFT)
    lam.texto((Xe(-vf - 0.30), Ze(top + 0.12)), "LADO VIA", 1.6, "TEXTOS", TA.BOTTOM_RIGHT)
    lam.titulo_vista(560, 392, "ELEVACION FRONTAL", "mirando hacia aguas arriba - ESC. 1/25", ancho_mm=110)
    # ---------------- CORTE A-A por el eje
    o = lam.P(205, 235); Xa = lambda u: o[0] - u; Za = lambda z: o[1] + (z - cf)
    for z1, z2, capa in ((cf - 0.10, cf, "C"), (cf + dz.H_FIN, top, "C")):
        pl = [(Xa(-1.20), Za(z1)), (Xa(0), Za(z1)), (Xa(0), Za(z2)), (Xa(-1.20), Za(z2))]
        lam.relleno(pl, "CONCRETO-ACHURADO"); lam.poli(pl, "CONCRETO", cerrada=True)
    lam.rect(Xa(-1.20), Za(cf - 0.15), Xa(0), Za(cf - 0.10), "SOLADO")
    lam.relleno([(Xa(-1.20), Za(cf)), (Xa(av), Za(cf)), (Xa(av), Za(na)), (Xa(-1.20), Za(na))], "AGUA-RELLENO") if False else \
        lam.relleno([(Xa(-1.20), Za(cf)), (Xa(0), Za(cf)), (Xa(0), Za(na)), (Xa(-1.20), Za(na))], "AGUA-RELLENO")
    lam.poli([(Xa(-1.20), Za(na)), (Xa(0.0), Za(na)), (Xa(av), Za(cf + 0.10)), (Xa(av + 0.6), Za(cf + 0.06))], "AGUA")
    for zz in (cf - 0.18, top + 0.03):
        lam.poli([(Xa(-1.20), Za(zz)), (Xa(-1.20), Za(zz + 0.08)), (Xa(-1.24), Za(zz + 0.10)), (Xa(-1.16), Za(zz + 0.14)), (Xa(-1.20), Za(zz + 0.16))], "CONCRETO") if False else None
    emb = [(Xa(0), Za(cf - dz.EMB_E)), (Xa(av), Za(cf - dz.EMB_E)), (Xa(av), Za(cf)), (Xa(0), Za(cf))]
    lam.poli(emb, "POZA", cerrada=True)
    _piedras(lam, emb, [Xa(u) for u in [0.05 + 0.11 * i for i in range(7)]], [Za(z) for z in (cf - 0.06, cf - 0.14)], 0.04)
    lam.rect(Xa(0), Za(cf - dz.EMB_E - dz.AFIRM_E), Xa(av), Za(cf - dz.EMB_E), "SOLADO")
    una = [(Xa(av), Za(cf)), (Xa(av + dz.UNA_B1), Za(cf)), (Xa(av + dz.UNA_B2), Za(cf - dz.UNA_H)), (Xa(av), Za(cf - dz.UNA_H))]
    lam.relleno(una, "ISO-PIEDRA"); lam.poli(una, "POZA", cerrada=True)
    alv = [(Xa(0), Za(cf)), (Xa(0), Za(cf + dz.AL_H0)), (Xa(av), Za(cf + dz.AL_H1)), (Xa(av), Za(cf))]
    lam.poli(alv, "CONCRETO", cerrada=False)
    lam.poli([(Xa(0), Za(zt - dz.ZAP_H)), (Xa(av), Za(zt - dz.ZAP_H)), (Xa(av), Za(cf - dz.EMB_E - dz.AFIRM_E))], "CONCRETO-OCULTO")
    lam.poli([(Xa(av + dz.UNA_B1), Za(cf)), (Xa(av + 1.0), Za(cf + 0.04)), (Xa(av + 1.4), Za(cf + 0.06))], "TERRENO")
    lam.cota((Xa(av), Za(cf)), (Xa(0), Za(cf)), 10 + 0 * f) if False else lam.cota((Xa(av), Za(cf - 0.30)), (Xa(0), Za(cf - 0.30)), -8)
    lam.cota((Xa(av + dz.UNA_B1), Za(cf)), (Xa(av), Za(cf)), 20)
    lam.cota((Xa(av + dz.UNA_B1), Za(cf - dz.UNA_H)), (Xa(av + dz.UNA_B1), Za(cf)), -6, horizontal=False)
    lam.cota((Xa(-0.15), Za(cf)), (Xa(-0.15), Za(top)), 6, horizontal=False) if False else None
    lam.cota((Xa(av), Za(cf)), (Xa(av), Za(cf + dz.AL_H1)), -4, horizontal=False)
    lam.cota((Xa(0), Za(cf)), (Xa(0), Za(cf + dz.AL_H0)), 4, horizontal=False)
    lam.nivel((Xa(-0.6), Za(top)), top, "losa +%.2f" % top, hmm=1.6)
    lam.nivel((Xa(-0.9), Za(cf)), cf, "CF %.2f" % cf, hmm=1.6)
    lam.nivel((Xa(av + 0.30), Za(cf - dz.UNA_H)), cf - dz.UNA_H, "%.2f" % (cf - dz.UNA_H), hmm=1.6)
    lam.juntar_llamadas()
    xt = lam.P(262, 0)[0]
    lam.llamada((Xa(av * 0.6), Za(cf + 0.45)), (xt, Za(top + 0.15)), ["alero (en elevacion): altura 0.70 a 0.45 sobre el piso"], 1.7)
    lam.llamada((Xa(0.35), Za(cf - 0.10)), (xt, Za(cf + 0.05)), ["emboquillado e = 0.20 sobre afirmado e = 0.10"], 1.7)
    lam.llamada((Xa(av + 0.15), Za(cf - 0.40)), (xt, Za(cf - 0.30)), ["una trapecial 0.35 / 0.15 x 0.65, L = 3.21 m"], 1.7)
    lam.llamada((Xa(av + 1.0), Za(cf + 0.04)), (xt, Za(cf - 0.62)), ["el agua vierte sobre la berma de la via"], 1.7)
    lam.volcar_llamadas()
    lam.titulo_vista(150, 150, "CORTE A-A", "por el eje del colector - ESC. 1/25", ancho_mm=110)
    # ---------------- CORTE B-B alero tipico
    o = lam.P(470, 240); Xb = lambda w: o[0] + w; Zb = lambda z: o[1] + (z - cf)
    hm = (dz.AL_H0 + dz.AL_H1) / 2
    mu_ = [(Xb(0), Zb(zt)), (Xb(e), Zb(zt)), (Xb(e), Zb(cf + hm)), (Xb(0), Zb(cf + hm))]
    zp = [(Xb(0), Zb(zt - dz.ZAP_H)), (Xb(dz.ZAP_B), Zb(zt - dz.ZAP_H)), (Xb(dz.ZAP_B), Zb(zt)), (Xb(0), Zb(zt))]
    for pl in (mu_, zp): lam.relleno(pl, "CONCRETO-ACHURADO"); lam.poli(pl, "CONCRETO", cerrada=True)
    emb = [(Xb(-0.60), Zb(cf - dz.EMB_E)), (Xb(0), Zb(cf - dz.EMB_E)), (Xb(0), Zb(cf)), (Xb(-0.60), Zb(cf))]
    lam.poli(emb, "POZA", cerrada=True)
    _piedras(lam, emb, [Xb(-0.55 + 0.11 * i) for i in range(6)], [Zb(z) for z in (cf - 0.06, cf - 0.14)], 0.04)
    lam.rect(Xb(-0.60), Zb(cf - dz.EMB_E - dz.AFIRM_E), Xb(0), Zb(cf - dz.EMB_E), "SOLADO")
    lam.poli([(Xb(e), Zb(zt + 0.40)), (Xb(0.85), Zb(zt + 0.40))], "TERRENO")
    for xx in (0.25, 0.45, 0.65): lam.linea((Xb(xx), Zb(zt + 0.40)), (Xb(xx - 0.05), Zb(zt + 0.35)), "TERRENO")
    # acero: L @0.20 (vertical + zapata), horizontales y longitudinales de zapata
    xv = e / 2
    lam.poli([(Xb(xv), Zb(cf + hm - 0.04)), (Xb(xv), Zb(zt - dz.ZAP_H + 0.05)), (Xb(dz.ZAP_B - 0.05), Zb(zt - dz.ZAP_H + 0.05))], "ACERO", ancho=D38)
    for k in range(5):
        lam.bloque("ACERO-38", (Xb(xv + 0.012), Zb(zt + 0.08 + k * (cf + hm - zt - 0.16) / 4)), 1.0)
    for xx in (0.08, 0.22, 0.37): lam.bloque("ACERO-38", (Xb(xx), Zb(zt - dz.ZAP_H + 0.062)), 1.0)
    lam.cota((Xb(0), Zb(cf + hm)), (Xb(e), Zb(cf + hm)), 6)
    lam.cota((Xb(0), Zb(zt - dz.ZAP_H)), (Xb(dz.ZAP_B), Zb(zt - dz.ZAP_H)), -6)
    lam.cota((Xb(dz.ZAP_B), Zb(zt - dz.ZAP_H)), (Xb(dz.ZAP_B), Zb(zt)), 6, horizontal=False)
    lam.cota((Xb(e), Zb(cf)), (Xb(e), Zb(cf + hm)), 14, horizontal=False, texto="0.70 a 0.45")
    lam.cota((Xb(-0.60), Zb(cf - dz.EMB_E - dz.AFIRM_E)), (Xb(-0.60), Zb(cf - dz.EMB_E)), -5, horizontal=False)
    lam.cota((Xb(-0.60), Zb(cf - dz.EMB_E)), (Xb(-0.60), Zb(cf)), -5, horizontal=False)
    lam.juntar_llamadas()
    xt = lam.P(520, 0)[0]
    lam.llamada((Xb(xv), Zb(cf + 0.30)), (xt, Zb(cf + hm + 0.10)), ["3/8\" @0.20 en L (vertical + zapata), L = 1.38"], 1.7)
    lam.llamada((Xb(xv + 0.012), Zb(zt + 0.08)), (xt, Zb(cf + 0.30)), ["horizontales 3/8\" @0.20 (5 por alero)"], 1.7)
    lam.llamada((Xb(0.22), Zb(zt - dz.ZAP_H + 0.062)), (xt, Zb(cf + 0.05)), ["3 barras 3/8\" longitudinales en la zapata"], 1.7)
    lam.llamada((Xb(0.6), Zb(zt + 0.40)), (xt, Zb(cf - 0.20)), ["relleno compactado sobre la zapata (lado exterior)"], 1.7)
    lam.volcar_llamadas()
    lam.titulo_vista(470, 150, "CORTE B-B", "alero tipico, perpendicular al alero - ESC. 1/25", ancho_mm=110)
    # ---------------- cuadros con los valores de la planilla del presupuesto
    part, acero, tot = dz.planilla()
    from decimal import Decimal, ROUND_HALF_UP
    r2 = lambda v: str(Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    filas = [[c, d, u, r2(v)] for c, d, u, v in part
             if c.startswith(("1.4.4.6.4.2.", "1.4.4.6.3.2"))]
    lam.tabla(632, 575, ["PARTIDA", "DESCRIPCION", "UND", "METRADO"], filas, [24, 120, 12, 18], hmm=1.6, alto_mm=5.5,
              titulo="METRADO DE LA ESTRUCTURA DE SALIDA (PRESUPUESTO)")
    fa = [[a["elemento"].replace("Aleros: ", ""), a["diam"], a["forma"], "%d" % a["n"], r2(a["L"]), r2(a["kg"])] for a in acero
          if str(a["partida"]).startswith("1.4.4.6.4.2.3")]
    fa.append(["TOTAL ACERO DE ALEROS", "", "", "", "", r2(tot.get("TOTAL ACERO ALEROS (1.4.4.6.4.2.3)", 0))])
    lam.tabla(632, 500, ["ELEMENTO", "DIAM.", "FORMA", "N.", "L (m)", "kg"], fa, [72, 14, 16, 12, 18, 22], hmm=1.6, alto_mm=5.5,
              titulo="DESPIECE DE ACERO DE LOS ALEROS")
    lam.leyenda2(30, 100, [("concreto", "CONCRETO", "concreto armado f'c=210 (colector y aleros)"), ("relleno", "ISO-PIEDRA", "una de concreto ciclopeo f'c=140 + 30% P.M."),
                           ("rect", "POZA", "emboquillado de piedra e = 0.20"), ("rect", "SOLADO", "afirmado e = 0.10 / solado"),
                           ("relleno", "AGUA-RELLENO", "agua con el caudal de diseno"), ("discontinua", "CONCRETO-OCULTO", "zapata y una ocultas"),
                           ("linea2", "ACERO", "acero de refuerzo 3/8\""), ("bloque:SIMB-FLECHA", "0", "sentido del flujo")],
                 hmm=1.9, ancho_col=115, filas_col=4)
    lam.notas(270, 100, "NOTAS", [
        "1. Toda la estructura de salida queda dentro del lindero; el agua vierte sobre la berma de la Crta. Oasis.",
        "2. Aleros monoliticos con el extremo del colector; altura 0.70 en el cabezal y 0.45 en el extremo, sobre el piso.",
        "3. Los metrados del cuadro son los de la planilla del presupuesto (partidas 1.4.4.6.3.2 y 1.4.4.6.4.2)."], hmm=1.7, ancho_mm=365)
    return lam


# ============================================================================== DP-08 CUADROS, ESPECIFICACIONES Y NOTAS
def dp08(doc, ox, oy):
    from decimal import Decimal, ROUND_HALF_UP
    r2 = lambda v, d="0.01": str(Decimal(str(v)).quantize(Decimal(d), rounding=ROUND_HALF_UP))
    lam = B.Lamina(doc, ox, oy, 25, "DP-08", "CUADROS DE ACERO Y DE METRADOS, ESPECIFICACIONES TECNICAS Y NOTAS",
                   "VALORES DE LA PLANILLA DEL PRESUPUESTO (PARTIDAS 1.4.4.6) - FIGURAS DE MARCOS ESC. 1/25 - GROSORES DE IMPRESION")
    f = lam.f
    part, acero, tot = dz.planilla()
    # ---------------- cuadro de acero
    filas = [[a["partida"], a["elemento"], r2(a["n"]), r2(a["L"]), a["diam"], a["forma"], r2(a["Lt"]), r2(a["kg"])] for a in acero]
    filas.append(["", "TOTAL ACERO COLECTOR (1.4.4.6.4.1.3)", "", "", "", "", "", r2(tot["TOTAL ACERO COLECTOR (1.4.4.6.4.1.3)"])])
    filas.append(["", "TOTAL ACERO ALEROS (1.4.4.6.4.2.3)", "", "", "", "", "", r2(tot["TOTAL ACERO ALEROS (1.4.4.6.4.2.3)"])])
    filas.append(["", "ACERO EN REGISTROS (incluido en 1.4.4.6.5.1)", "", "", "", "", "", r2(tot["ACERO EN REGISTROS (incluido en 1.4.4.6.5.1)"])])
    yb = lam.tabla(30, 572, ["PARTIDA", "ELEMENTO", "N. PIEZAS", "L PIEZA (m)", "DIAM.", "FORMA", "L TOTAL (m)", "PESO (kg)"], filas,
                   [26, 92, 20, 22, 14, 18, 24, 22], hmm=1.7, alto_mm=5.2, titulo="CUADRO DE ACERO DEL COLECTOR, REGISTROS Y ALEROS")
    lam.texto(lam.P(30, yb - 4), "N. de piezas y longitudes medias ponderadas de la planilla de metrados (marcos con ganchos; barras de 9 m con traslape 0.40 m).",
              1.6, "TEXTOS-NOTAS")
    # ---------------- figuras de los marcos (1/25)
    def marco_fig(xmm, ymm, w, hgt, d, txt_w, txt_h, titulo, sub, ytit=None):
        x0, y0 = lam.P(xmm, ymm)
        lam.poli([(x0, y0), (x0 + w, y0), (x0 + w, y0 + hgt), (x0, y0 + hgt)], "ACERO", cerrada=True, ancho=max(d, 0.35 * f))
        g = 0.09
        lam.poli([(x0, y0 + hgt), (x0 + g * 0.7, y0 + hgt - g * 0.7)], "ACERO", ancho=max(d, 0.35 * f))
        lam.poli([(x0 + 0.02, y0 + hgt), (x0 + 0.02 + g * 0.7, y0 + hgt - g * 0.7)], "ACERO", ancho=max(d, 0.35 * f))
        lam.cota((x0, y0), (x0 + w, y0), -6, texto=txt_w)
        lam.cota((x0 + w, y0), (x0 + w, y0 + hgt), 6, horizontal=False, texto=txt_h)
        lam.titulo_vista(xmm + w / f / 2, (ytit if ytit is not None else ymm) - 18, titulo, sub, ancho_mm=max(70, w / f))
    yfig = yb - 62
    marco_fig(50, yfig, 1.60, 0.55, D38, "1.60", "h + 0.10", "MARCO 3/8\"", "@0.20 vereda y final, @0.15 autos")
    marco_fig(160, yfig, 1.71, 0.81, D12, "1.71", "h + 0.31", "MARCO EXTERIOR 1/2\"", "cruce de camiones @0.15")
    marco_fig(285, yfig + 0.11 / f, 1.59, 0.59, D12, "1.59", "h + 0.09", "MARCO INTERIOR 1/2\"", "cruce de camiones @0.15", ytit=yfig)
    marco_fig(220, yfig + 0.11 / f, 1.59, 0.59, D12, "1.59", "h + 0.09", "", None) if False else None
    lam.texto(lam.P(30, yfig - 34), "Ganchos a 135 grados de 6 diametros en la esquina superior del lado de la via; h = altura interior del tramo (DP-03).", 1.7, "TEXTOS-NOTAS")
    # ---------------- partidas del presupuesto (lado derecho)
    fp = [[c, d[:62], u, r2(v) if v is not None else ""] for c, d, u, v in part]
    lam.tabla(456, 572, ["ITEM", "DESCRIPCION", "UND", "METRADO"], fp, [26, 122, 12, 22], hmm=1.6, alto_mm=4.6,
              titulo="PARTIDAS DEL COLECTOR EN EL PRESUPUESTO (1.4.4.6)")
    # ---------------- especificaciones tecnicas
    lam.notas(456, 430, "ESPECIFICACIONES TECNICAS", [
        "CONCRETO ARMADO: f'c = 210 kg/cm2 en colector, aleros de salida y tapas.",
        "CONCRETO SIMPLE: solado f'c = 100 kg/cm2 e = 0.05; una ciclopea f'c = 140 kg/cm2 + 30 % P.M.",
        "EMBOQUILLADO: piedra mediana 6\" a 8\" asentada con concreto f'c = 140 kg/cm2, e = 0.20 sobre afirmado e = 0.10.",
        "ACERO DE REFUERZO: fy = 4200 kg/cm2 (grado 60), corrugado; asas de tapa en acero liso 3/8\".",
        "RECUBRIMIENTOS: malla centrada en elementos de 0.10; 4.5 cm al eje en cruce de camiones; 2.5 cm en tapas.",
        "TRASLAPES: 3/8\" = 0.40 m; 1/2\" = 0.50 m, alternados.",
        "LOSA SUPERIOR: vaciada monoliticamente con los muros; acabado frotachado en el tramo de vereda.",
        "REGISTROS: contramarco L 2\"x2\"x3/16\" y marco L 1 1/2\"x1 1/2\"x1/8\" con anclajes; pintura anticorrosiva y esmalte.",
        "JUNTAS: e = 1\" cada 4.00 m y en el cruce de camiones; poliestireno expandido y sello elastomerico.",
        "CURADO: humedo minimo 7 dias; no transitar sobre la losa antes de 14 dias.",
        "RELLENO: material propio seleccionado en capas de 0.15 m al 95 % del Proctor modificado.",
        "MURO LADO VIA: vaciado contra el terreno (sin encofrado exterior)."], hmm=1.6, ancho_mm=372)
    # ---------------- grosores de impresion (CTB) por capa
    filas = [["CONCRETO", "250 (gris)", "0.50"], ["ACERO (marcos)", "1 (rojo)", "0.35"], ["ACERO-LONG", "5 (azul)", "0.35"],
             ["MARCO-METALICO / angulos", "32 / 5", "0.40"], ["CUNETA", "3 (verde)", "0.35"], ["COTAS", "94 (verde osc.)", "0.18"],
             ["LLAMADAS", "30 (naranja)", "0.18"], ["AGUA", "150 (celeste)", "0.25"], ["TITULOS", "160 (azul)", "0.35"],
             ["ARQ-BASE (referencia)", "8 (gris)", "0.13"]]
    lam.tabla(30, 255, ["CAPA", "COLOR", "GROSOR (mm)"], filas, [70, 36, 24], hmm=1.6, alto_mm=4.4, titulo="GROSORES DE IMPRESION POR CAPA")
    lam.notas(30, 100, "NOTAS GENERALES", [
        "1. Dimensiones en metros y cotas en m.s.n.m., salvo indicacion.",
        "2. El colector se dimensiona para 823 L/s en la salida (CAR Varones, Hogar de Refugio y CAR Mujeres; TR 25 anos).",
        "3. Verificacion hidraulica y estructural segun la memoria de calculo del proyecto (RNE CE.040, E.020, E.060).",
        "4. Los metrados de esta lamina son los de la planilla del presupuesto; los planos no modifican cantidades.",
        "5. Confirmar la capacidad portante con el estudio de mecanica de suelos antes del vaciado."], hmm=1.7, ancho_mm=400)
    return lam


# ============================================================================== DP-09 ISOMETRICOS CONSTRUCTIVOS
def _cara(lam, T, pts3, capa, aristas=True):
    pts = [T(*q) for q in pts3]
    if len(pts) == 4: lam.solido([pts[0], pts[1], pts[3], pts[2]], capa)
    else: _hatch_rgb(lam, pts, capa)
    if aristas: lam.poli(pts, "ISO-ARISTAS", cerrada=True)
    return pts


def _caja(lam, T, x0, x1, y0, y1, z0, z1, capas=("ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2")):
    _cara(lam, T, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], capas[2])
    _cara(lam, T, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], capas[1])
    _cara(lam, T, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], capas[0])


def dp09(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 25, "DP-09", "ISOMETRICOS CONSTRUCTIVOS",
                   "COLECTOR A NIVEL DE VEREDA, REGISTRO DE LIMPIEZA, EMPALME DE CUNETA Y ESTRUCTURA DE SALIDA - ESC. 1/25 (ESCALA REAL)")
    f = lam.f; bi = dz.b / 2
    # ---------------- 1. colector a nivel de vereda (tramo de 2.40 m con junta y vereda adyacente)
    p = 20.0; K = dz.b_ext(p) / 2; cf = dz.CF(p); top = dz.techo(p); Ls = 2.4
    o = lam.P(150, 430)
    T = iso_seccion(lam, o, p, Ls=Ls, llamadas=False)
    _caja(lam, T, K + 0.025, K + 1.0, 0, Ls, top - 0.10, top, ("ISO-CUNETA", "ISO-CUNETA", "ISO-CUNETA"))
    _cara(lam, T, [(K, 0, top), (K + 0.025, 0, top), (K + 0.025, Ls, top), (K, Ls, top)], "ISO-TAPA")
    lam.poli([T(-K, 1.2, top), T(K, 1.2, top), T(K, 1.2, cf - 0.10)], "JUNTAS")
    lam.juntar_llamadas(); xt = lam.P(255, 0)[0]
    lam.llamada(T(0.2, 0.6, top), (xt, lam.P(0, 545)[1]), ["losa superior del colector = vereda (NPT +259.25)"], 1.7)
    lam.llamada(T(0.4, 1.2, top), (xt, lam.P(0, 533)[1]), ["junta de dilatacion cada 4.00 m (sello elastomerico)"], 1.7)
    lam.llamada(T(K + 0.5, 1.0, top), (xt, lam.P(0, 521)[1]), ["piso adyacente del predio"], 1.7)
    lam.llamada(T(K + 0.012, 2.0, top), (xt, lam.P(0, 509)[1]), ["junta 1\" con tecnopor entre colector y piso"], 1.7)
    lam.llamada(T(0.0, Ls, dz.NA(p) - 0.05), (xt, lam.P(0, 497)[1]), ["agua de diseno (tirante 0.34 a 0.47 m)"], 1.7)
    lam.llamada(T(-K, Ls, top - 0.3), (xt, lam.P(0, 485)[1]), ["muro lado via vaciado contra el terreno"], 1.7)
    lam.llamada(T(0.4, Ls, cf - 0.05), (xt, lam.P(0, 473)[1]), ["losa de fondo e = 0.10 sobre solado e = 0.05"], 1.7)
    lam.volcar_llamadas()
    lam.titulo_vista(200, 330, "ISOMETRICO 1: COLECTOR A NIVEL DE VEREDA", "tramo tipico de 2.40 m en vereda - ESC. 1/25", ancho_mm=160)
    # ---------------- 2. registro de limpieza (vista explotada)
    p = 37.95; K = dz.b_ext(p) / 2; cf = dz.CF(p); top = dz.techo(p); Ls = 1.6; yc = 0.8
    o = lam.P(560, 410)
    def T2(x, y, z):
        u, v = B.iso(x, y - Ls, z - cf); return (o[0] + u, o[1] + v)
    r, l_ = dz.REB / 2, dz.LUZ / 2
    _cara(lam, T2, [(K, 0, cf - 0.10), (K, Ls, cf - 0.10), (K, Ls, top), (K, 0, top)], "ISO-CONCRETO-LAT2")
    _cara(lam, T2, [(-K, Ls, cf - 0.10), (K, Ls, cf - 0.10), (K, Ls, top), (-K, Ls, top)], "ISO-CONCRETO-LAT1")
    ext = [T2(-K, 0, top), T2(K, 0, top), T2(K, Ls, top), T2(-K, Ls, top)]
    hol = [T2(-r, yc - r, top), T2(r, yc - r, top), T2(r, yc + r, top), T2(-r, yc + r, top)]
    _hatch_rgb(lam, ext, "ISO-CONCRETO-SUP", [hol]); lam.poli(ext, "ISO-ARISTAS", cerrada=True); lam.poli(hol, "ISO-ARISTAS", cerrada=True)
    _cara(lam, T2, [(-r, yc - r, top - dz.E_TAPA), (r, yc - r, top - dz.E_TAPA), (r, yc + r, top - dz.E_TAPA), (-r, yc + r, top - dz.E_TAPA)], "ISO-CONCRETO-LAT2")
    _cara(lam, T2, [(-l_, yc - l_, top - dz.E_TAPA), (l_, yc - l_, top - dz.E_TAPA), (l_, yc + l_, top - dz.E_TAPA), (-l_, yc + l_, top - dz.E_TAPA)], "ISO-AGUA")
    _cara(lam, T2, [(-r, yc + r, top - dz.E_TAPA), (r, yc + r, top - dz.E_TAPA), (r, yc + r, top), (-r, yc + r, top)], "ISO-CONCRETO-LAT1") if False else None
    zc = top + 0.30
    for a, b_ in ((r + 0.051, r - 0.005), ):
        lam.poli([T2(-a, yc - a, zc), T2(a, yc - a, zc), T2(a, yc + a, zc), T2(-a, yc + a, zc)], "MARCO-METALICO", cerrada=True)
        lam.poli([T2(-b_, yc - b_, zc), T2(b_, yc - b_, zc), T2(b_, yc + b_, zc), T2(-b_, yc + b_, zc)], "MARCO-METALICO", cerrada=True)
        lam.poli([T2(-b_, yc - b_, zc - 0.05), T2(b_, yc - b_, zc - 0.05), T2(b_, yc + b_, zc - 0.05)], "MARCO-METALICO")
    zt_ = top + 0.62; t_ = dz.TAPA / 2
    _caja(lam, T2, -t_, t_, yc - t_, yc + t_, zt_ - dz.E_TAPA, zt_, ("ISO-TAPA", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2"))
    lam.poli([T2(-t_, yc - t_, zt_ + 0.002), T2(t_, yc - t_, zt_ + 0.002), T2(t_, yc + t_, zt_ + 0.002), T2(-t_, yc + t_, zt_ + 0.002)], "MARCO-METALICO", cerrada=True)
    for yy in (yc - 0.22, yc + 0.22):
        lam.poli([T2(-0.08, yy - 0.025, zt_), T2(0.08, yy - 0.025, zt_), T2(0.08, yy + 0.025, zt_), T2(-0.08, yy + 0.025, zt_)], "ISO-ARISTAS", cerrada=True)
    for q in ((-t_, yc - t_), (t_, yc - t_), (t_, yc + t_)):
        lam.linea(T2(q[0], q[1], zt_ - dz.E_TAPA - 0.02), T2(q[0], q[1], top + 0.02), "CORTES") if False else lam.linea(T2(q[0], q[1], zt_ - dz.E_TAPA - 0.02), T2(q[0], q[1], zc + 0.04), "GRILLA")
    lam.juntar_llamadas(); xt = lam.P(668, 0)[0]
    lam.llamada(T2(t_, yc, zt_), (xt, lam.P(0, 545)[1]), ["tapa de concreto 0.68 x 0.68 x 0.08 con marco L 1 1/2\""], 1.7)
    lam.llamada(T2(r + 0.03, yc, zc), (xt, lam.P(0, 533)[1]), ["contramarco L 2\"x2\"x3/16\" con anclajes 3/8\""], 1.7)
    lam.llamada(T2(r, yc - r * 0.2, top - 0.04), (xt, lam.P(0, 521)[1]), ["rebaje 0.70 x 0.08: la tapa apoya en la ceja de 0.05"], 1.7)
    lam.llamada(T2(0.0, yc, top - dz.E_TAPA), (xt, lam.P(0, 509)[1]), ["luz libre 0.60 x 0.60 (borde engrosado 0.15 x 0.10 bajo la losa)"], 1.7)
    lam.llamada(T2(K - 0.3, 0.3, top), (xt, lam.P(0, 497)[1]), ["losa superior e = 0.10"], 1.7)
    lam.volcar_llamadas()
    lam.titulo_vista(600, 330, "ISOMETRICO 2: REGISTRO DE LIMPIEZA", "vista explotada - colocacion del contramarco y la tapa - ESC. 1/25", ancho_mm=160)
    # ---------------- 3. empalme de cuneta (losa superior cortada para ver el interior)
    p = 37.95; K = dz.b_ext(p) / 2; cf = dz.CF(p); top = dz.techo(p); Ls = 1.6; yc = 0.8; ncf = 258.74
    o = lam.P(130, 190)
    T3 = iso_seccion(lam, o, p, Ls=Ls, llamadas=False)
    _cara(lam, T3, [(K, yc - 0.20, ncf), (K, yc + 0.20, ncf), (K, yc + 0.20, ncf + 0.30), (K, yc - 0.20, ncf + 0.30)], "ISO-AGUA")
    xc0, xc1 = K + 0.025, K + 1.4
    _cara(lam, T3, [(xc0, yc - 0.30, ncf - 0.10), (xc1, yc - 0.30, ncf - 0.10), (xc1, yc + 0.30, ncf - 0.10), (xc0, yc + 0.30, ncf - 0.10)], "ISO-CUNETA")
    _cara(lam, T3, [(xc0, yc - 0.20, ncf), (xc1, yc - 0.20, ncf), (xc1, yc + 0.20, ncf), (xc0, yc + 0.20, ncf)], "ISO-AGUA")
    _cara(lam, T3, [(xc0, yc + 0.20, ncf), (xc1, yc + 0.20, ncf), (xc1, yc + 0.20, top), (xc0, yc + 0.20, top)], "ISO-CUNETA")
    _cara(lam, T3, [(xc0, yc + 0.30, ncf - 0.10), (xc1, yc + 0.30, ncf - 0.10), (xc1, yc + 0.30, top), (xc0, yc + 0.30, top)], "ISO-CUNETA")
    _cara(lam, T3, [(xc1, yc - 0.30, ncf - 0.10), (xc1, yc + 0.30, ncf - 0.10), (xc1, yc + 0.30, top), (xc1, yc - 0.30, top)], "ISO-CUNETA")
    _cara(lam, T3, [(xc0, yc + 0.20, top), (xc1, yc + 0.20, top), (xc1, yc + 0.30, top), (xc0, yc + 0.30, top)], "ISO-CUNETA")
    lam.flecha(T3(xc1 - 0.2, yc, ncf + 0.03), T3(K + 0.1, yc, ncf + 0.03), "FLUJO", 2.5)
    lam.juntar_llamadas(); xt = lam.P(255, 0)[0]
    lam.llamada(T3(xc1 - 0.3, yc + 0.3, top - 0.1), (xt, lam.P(0, 305)[1]), ["cuneta 0.40 que llega del eje (Ejes 02, 07, 10 y 12)"], 1.7)
    lam.llamada(T3(K, yc, ncf + 0.15), (xt, lam.P(0, 293)[1]), ["ventana 0.40 x 0.30 en el muro del lado del predio"], 1.7)
    lam.llamada(T3(K + 0.012, yc + 0.25, top - 0.2), (xt, lam.P(0, 281)[1]), ["junta 1\" entre cuneta y colector"], 1.7)
    lam.llamada(T3(0.0, Ls, dz.NA(p) - 0.05), (xt, lam.P(0, 269)[1]), ["agua de diseno en el colector"], 1.7)
    lam.volcar_llamadas()
    lam.titulo_vista(200, 112, "ISOMETRICO 3: EMPALME DE CUNETA", "ventana en el muro y caida al colector, bajo un registro - ESC. 1/25", ancho_mm=160)
    # ---------------- 4. estructura de salida (vista girada 25 grados; caras ordenadas por profundidad)
    o = lam.P(585, 205); cf = dz.CFS; K = dz.b_ext(dz.L) / 2; top = cf + dz.H_FIN + 0.10; naS = dz.NA(dz.L)
    av = dz.AL_AV; vf = bi + av; s2 = math.sqrt(0.5); e = dz.AL_E
    th = math.radians(-28.0); ct_, st_ = math.cos(th), math.sin(th)
    def R3(x, y, z): return (x * ct_ - y * st_, x * st_ + y * ct_, z)
    def T4(x, y, z):
        xr, yr, zr = R3(x, y, z); u, v = B.iso(xr, yr, zr - cf); return (o[0] + u, o[1] + v)
    caras = []
    def prisma(pl, z0, ztop, capa_sup, capa_lat, capa_lat2=None):
        """pl: poligono en planta (x = lateral, y = flujo hacia el observador); ztop: cota o lista de cotas por vertice"""
        n = len(pl); zt_ = ztop if isinstance(ztop, list) else [ztop] * n
        cx = sum(q[0] for q in pl) / n; cy = sum(q[1] for q in pl) / n
        caras.append(([(q[0], q[1], zt_[i]) for i, q in enumerate(pl)], capa_sup, (0, 0, 1)))
        for i in range(n):
            p1, p2 = pl[i], pl[(i + 1) % n]
            nx_, ny_ = (p2[1] - p1[1]), -(p2[0] - p1[0])
            mx, my = (p1[0] + p2[0]) / 2 - cx, (p1[1] + p2[1]) / 2 - cy
            if nx_ * mx + ny_ * my < 0: nx_, ny_ = -nx_, -ny_
            caras.append(([(p1[0], p1[1], z0), (p2[0], p2[1], z0), (p2[0], p2[1], zt_[(i + 1) % n]), (p1[0], p1[1], zt_[i])],
                          capa_lat if abs(nx_) < abs(ny_) else (capa_lat2 or capa_lat), (nx_, ny_, 0)))
    L0 = -1.6
    rect = lambda x0, x1, y0, y1: [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    prisma(rect(-K, K, L0, 0), cf - 0.10, cf, "ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2")
    for sv in (-1, 1):
        prisma(rect(min(sv * bi, sv * K), max(sv * bi, sv * K), L0, 0), cf, cf + dz.H_FIN, "ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2")
    prisma(rect(-bi, bi, L0, 0), cf, naS, "ISO-AGUA", "AGUA-RELLENO")
    prisma(rect(-K, K, L0, 0), cf + dz.H_FIN, top, "ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2")
    prisma([(-bi, 0), (bi, 0), (vf, av), (-vf, av)], cf - dz.EMB_E, cf, "ISO-PIEDRA", "ISO-PIEDRA")
    hw = dz.ANCHO_FIN / 2 + 0.15
    prisma(rect(-hw, hw, av, av + dz.UNA_B1), cf - dz.UNA_H, cf, "ISO-PIEDRA", "ISO-PIEDRA")
    for sv in (-1, 1):
        a0 = (sv * bi, 0.0); a1 = (sv * vf, av); n_ = (sv * s2 * e, -s2 * e)
        b0 = (a0[0] + n_[0], a0[1] + n_[1]); b1 = (a1[0] + n_[0], a1[1] + n_[1])
        h0, h1 = cf + dz.AL_H0, cf + dz.AL_H1
        prisma([a0, a1, b1, b0], cf, [h0, h1, h1, h0], "ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2")
    vis = []
    for pts3, capa, nrm in caras:
        nr = R3(nrm[0], nrm[1], nrm[2])
        if nr[0] + nr[1] + nr[2] <= 1e-9: continue
        rp = [R3(*q) for q in pts3]
        prof = sum(q[0] + q[1] + q[2] for q in rp) / len(rp)
        vis.append((prof, pts3, capa))
    for prof, pts3, capa in sorted(vis, key=lambda c: c[0]):
        pp = [T4(*q) for q in pts3]
        if len(pp) == 4: lam.solido([pp[0], pp[1], pp[3], pp[2]], capa)
        else: _hatch_rgb(lam, pp, capa if capa in B.COLOR_RGB else "ISO-PIEDRA")
        lam.poli(pp, "ISO-ARISTAS", cerrada=True)
    _piedras(lam, [T4(-bi, 0, cf), T4(bi, 0, cf), T4(vf, av, cf), T4(-vf, av, cf)],
             [T4(0, 0, cf)[0] + (i - 12) * 0.09 for i in range(25)], [T4(0, 0, cf)[1] + (j - 6) * 0.07 for j in range(13)], 0.03)
    lam.juntar_llamadas(); xt = lam.P(668, 0)[0]
    lam.llamada(T4(vf - 0.1, av - 0.1, cf + dz.AL_H1), (xt, lam.P(0, 305)[1]), ["alero e = 0.15, L = 1.00 a 45 grados (h 0.70 a 0.45)"], 1.7)
    lam.llamada(T4(0.0, av * 0.5, cf), (xt, lam.P(0, 293)[1]), ["emboquillado de piedra e = 0.20"], 1.7)
    lam.llamada(T4(0.6, av + 0.17, cf), (xt, lam.P(0, 281)[1]), ["una de concreto ciclopeo (0.35 x 0.65)"], 1.7)
    lam.llamada(T4(0.3, -0.8, top), (xt, lam.P(0, 269)[1]), ["fin del colector cubierto (losa +259.00)"], 1.7)
    lam.llamada(T4(0.0, -0.5, dz.NA(dz.L)), (xt, lam.P(0, 257)[1]), ["agua de diseno (NA 258.785)"], 1.7)
    lam.volcar_llamadas()
    lam.titulo_vista(600, 112, "ISOMETRICO 4: ESTRUCTURA DE SALIDA", "PROG. 0+139.08 - CF 258.30 - dentro del lindero - ESC. 1/25", ancho_mm=160)
    lam.leyenda2(30, 100, [("relleno", "ISO-CONCRETO-SUP", "concreto armado (cara superior)"), ("relleno", "ISO-CONCRETO-LAT2", "concreto armado (caras laterales)"),
                           ("relleno", "ISO-TAPA", "tapa de registro / junta de tecnopor"), ("relleno", "AGUA-RELLENO", "agua"),
                           ("relleno", "ISO-CUNETA", "cuneta que llega / piso adyacente"), ("linea2", "MARCO-METALICO", "marco y contramarco metalico"),
                           ("relleno", "ISO-PIEDRA", "emboquillado y una de piedra")], hmm=1.9, ancho_col=115, filas_col=4)
    return lam


# ============================================================================== DP-10 ISOMETRICO GENERAL
def dp10(doc, ox, oy):
    lam = B.Lamina(doc, ox, oy, 200, "DP-10", "ISOMETRICO GENERAL DEL COLECTOR PLUVIAL",
                   "VISTA DE CONJUNTO A ESCALA REAL (SIN EXAGERACION VERTICAL): COLECTOR CUBIERTO, REGISTROS, EMPALMES DE CUNETA Y SALIDA")
    f = lam.f
    x0, y0, _ = dz.eje_local(0.0)
    o = lam.P(745, 235)
    def T(x, y, z):
        u, v = B.iso(x - x0, y - y0, z - dz.NPT); return (o[0] + u, o[1] + v)
    caras = []
    dp = 1.0; ps = [i * dp for i in range(int(dz.L / dp))] + [dz.L]
    def lat(p, d): return dz.lateral(p, d)
    for a, c in zip(ps[:-1], ps[1:]):
        Ka, Kc = dz.b_ext(a + 1e-3) / 2, dz.b_ext(c - 1e-3) / 2
        ta, tc = dz.techo(a + 1e-3), dz.techo(c - 1e-3)
        ba, bc = dz.CF(a) - dz.esp(a + 1e-3)[1], dz.CF(c) - dz.esp(c - 1e-3)[1]
        pa_n, pc_n, pa_s, pc_s = lat(a, Ka), lat(c, Kc), lat(a, -Ka), lat(c, -Kc)
        prof = ((pa_n[0] + pc_n[0]) / 2 + (pa_n[1] + pc_n[1]) / 2)
        caras.append((prof, [(pa_n[0], pa_n[1], ba), (pc_n[0], pc_n[1], bc), (pc_n[0], pc_n[1], tc), (pa_n[0], pa_n[1], ta)], "ISO-CONCRETO-LAT2"))
        caras.append((prof + 0.01, [(pa_s[0], pa_s[1], ta), (pc_s[0], pc_s[1], tc), (pc_n[0], pc_n[1], tc), (pa_n[0], pa_n[1], ta)], "ISO-CONCRETO-SUP"))
    # extremo de llegada (R-01, cara hacia +x)
    pa_n, pa_s = lat(0, dz.b_ext(0) / 2), lat(0, -dz.b_ext(0) / 2)
    caras.append((pa_n[0] + pa_n[1] + 5, [(pa_s[0], pa_s[1], dz.CF(0) - 0.10), (pa_n[0], pa_n[1], dz.CF(0) - 0.10), (pa_n[0], pa_n[1], dz.NPT), (pa_s[0], pa_s[1], dz.NPT)], "ISO-CONCRETO-LAT1"))
    for prof, pts, capa in sorted(caras, key=lambda c: c[0]):
        pp = [T(*q) for q in pts]
        lam.solido([pp[0], pp[1], pp[3], pp[2]], capa)
    # aristas superiores y juntas
    for d in (1, -1):
        lam.poli([T(*lat(p, d * dz.b_ext(p) / 2), dz.techo(p)) for p in ps], "ISO-ARISTAS")
    lam.poli([T(*lat(p, dz.b_ext(p) / 2), dz.CF(p) - dz.esp(p)[1]) for p in ps], "ISO-ARISTAS")
    for q in dz.JUNTAS:
        lam.poli([T(*lat(q, -dz.b_ext(q) / 2), dz.techo(q)), T(*lat(q, dz.b_ext(q) / 2), dz.techo(q)), T(*lat(q, dz.b_ext(q) / 2), dz.CF(q) - dz.esp(q)[1])], "JUNTAS")
    # cruces vehiculares (franja naranja sobre la losa)
    for a, c in list(dz.AUTOS) + [dz.CAMION]:
        for d in (dz.b_ext(a) / 2 + 0.02, -dz.b_ext(a) / 2 - 0.02):
            lam.poli([T(*lat(p, d), dz.techo(p) + 0.01) for p in [a + (c - a) * i / 10 for i in range(11)]], "CRUCE-VEHICULAR", ancho=0.4 * f)
    # registros (tapas) y cunetas
    regp = {r["nombre"]: r for r in dz.REGISTROS}
    for r in dz.REGISTROS:
        p = r["prog"]; az = math.radians(dz.eje_local(p)[2]); t = dz.TAPA / 2
        ux, uy = math.cos(az), math.sin(az); vx, vy = -uy, ux
        x, y, _ = dz.eje_local(p)
        q = [(x + sx * t * ux + sy * t * vx, y + sx * t * uy + sy * t * vy) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        pp = [T(qx, qy, r["ct"] + 0.005) for qx, qy in q]
        lam.solido([pp[0], pp[1], pp[3], pp[2]], "ISO-TAPA"); lam.poli(pp, "REGISTRO", cerrada=True)
    for e_, rn, ncf in dz.CUNETAS:
        p = regp[rn]["prog"]; K = dz.b_ext(p) / 2
        a, b_ = lat(p - 0.3, K + 0.025), lat(p + 0.3, K + 0.025)
        a2, b2 = lat(p - 0.3, K + 2.4), lat(p + 0.3, K + 2.4)
        for pts, capa in (([(a[0], a[1], ncf - 0.1), (a2[0], a2[1], ncf - 0.1), (a2[0], a2[1], dz.NPT), (a[0], a[1], dz.NPT)], "ISO-CUNETA"),
                          ([(a[0], a[1], dz.NPT), (a2[0], a2[1], dz.NPT), (b2[0], b2[1], dz.NPT), (b_[0], b_[1], dz.NPT)], "ISO-CUNETA")):
            pp = [T(*q) for q in pts]; lam.solido([pp[0], pp[1], pp[3], pp[2]], capa); lam.poli(pp, "ISO-ARISTAS", cerrada=True)
    # salida: aleros y emboquillado (planta original)
    for pl in dz.BASE["CONCRETO"]:
        if pl[0][0] < -561.0:
            lam.poli([T(x, y, dz.CFS + 0.70) for x, y in pl], "ISO-ARISTAS")
    for pl in dz.BASE["EMBOQUILLADO"]:
        pp = [T(x, y, dz.CFS) for x, y in pl]; _hatch_rgb(lam, pp, "ISO-PIEDRA"); lam.poli(pp, "ISO-ARISTAS", cerrada=True)
    # etiquetas junto a cada registro (debajo, con linea corta)
    for r in dz.REGISTROS:
        x, y, _ = dz.eje_local(r["prog"]); u = T(x, y, r["ct"])
        ls = ["%s  %s" % (r["nombre"], pt(r["prog"]))]
        for e_, rn, ncf in dz.CUNETAS:
            if rn == r["nombre"]: ls.append("cuneta %s" % e_)
        yb = u[1] + 12 * f + 3.4 * f * (len(ls) - 1)
        lam.linea(u, (u[0], yb), "LLAMADAS"); lam.circulo(u, 0.6 * f, "LLAMADAS")
        for i, t in enumerate(ls):
            lam.texto((u[0] + 0.8 * f, yb - i * 3.4 * f), t, 1.6, "TEXTOS", TA.BOTTOM_LEFT)
    x, y, _ = dz.eje_local(dz.L); u = T(x, y, dz.CFS)
    lam.linea(u, (u[0], u[1] + 14 * f), "LLAMADAS")
    lam.textos((u[0] + 0.8 * f, u[1] + 18 * f), ["SALIDA %s" % pt(dz.L), "aleros y emboquillado (DP-07)"], 1.6, "TEXTOS")
    x, y, _ = dz.eje_local(0.0); u = T(x, y, dz.NPT)
    lam.textos((u[0] + 3 * f, u[1] + 22 * f), ["INICIO 0+000.00 (R-01)", "llegada de CAR Varones y", "Hogar de Refugio (560.6 L/s)"], 1.8, "TEXTOS")
    lam.leyenda2(30, 100, [("relleno", "ISO-CONCRETO-SUP", "losa superior del colector"), ("relleno", "ISO-CONCRETO-LAT2", "muro del lado del predio"),
                           ("relleno", "ISO-TAPA", "tapa de registro (15 und)"), ("relleno", "ISO-CUNETA", "cuneta que llega (4 und)"),
                           ("linea2", "CRUCE-VEHICULAR", "cruce vehicular (autos y camiones)"), ("discontinua", "JUNTAS", "junta de dilatacion (33 und)"),
                           ("relleno", "ISO-PIEDRA", "emboquillado de la salida")], hmm=1.9, ancho_col=110, filas_col=4)
    lam.notas(262, 100, "NOTAS", [
        "1. Isometrico de conjunto a escala real 1/200, sin exageracion vertical; vista desde el lado del predio.",
        "2. Medidas y cotas en las laminas DP-01 a DP-09."], hmm=1.7, ancho_mm=370)
    return lam


# ============================================================================== armado del documento
def construir(solo=None):
    doc = B.nuevo_documento()
    hacer = lambda c: solo is None or c in solo
    if hacer("DP-01"):
        LAMINAS["DP-01"] = dp01(doc, -572.6, -35.4)
    if hacer("DP-02"):
        LAMINAS["DP-02"] = dp02(doc, 0.0, 0.0)
    if any(hacer(c) for c in ("DP-03A", "DP-03B", "DP-03C")):
        for l in dp03(doc, 100.0, 0.0): LAMINAS[l.codigo] = l
    if any(hacer(c) for c in ("DP-04A", "DP-04B")):
        for l in dp04(doc, 200.0, 0.0): LAMINAS[l.codigo] = l
    if any(hacer(c) for c in ("DP-05A", "DP-05B")):
        for l in dp05(doc, 245.0, 0.0): LAMINAS[l.codigo] = l
    if hacer("DP-06A"):
        LAMINAS["DP-06A"] = dp06a(doc, 295.0, 0.0)
    if hacer("DP-06B"):
        LAMINAS["DP-06B"] = dp06b(doc, 305.0, 0.0)
    if hacer("DP-06C"):
        LAMINAS["DP-06C"] = dp06c(doc, 315.0, 0.0)
    if hacer("DP-07"):
        LAMINAS["DP-07"] = dp07(doc, 330.0, 0.0)
    if hacer("DP-08"):
        LAMINAS["DP-08"] = dp08(doc, 355.0, 0.0)
    if hacer("DP-09"):
        LAMINAS["DP-09"] = dp09(doc, 380.0, 0.0)
    if hacer("DP-10"):
        LAMINAS["DP-10"] = dp10(doc, 410.0, 0.0)
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: "1" for e in msp.query("HATCH") if e.dxf.layer in ("CONCRETO-ACHURADO", "AGUA-RELLENO")})
    os.makedirs(dz.SAL, exist_ok=True)
    doc.saveas(SALIDA)
    cajas = {k: (l.ox, l.oy, l.ox + 841 * l.f, l.oy + 594 * l.f) for k, l in LAMINAS.items()}
    json.dump(cajas, open(os.path.join(dz.SAL, "laminas.json"), "w"), indent=1)
    return SALIDA, cajas


if __name__ == "__main__":
    solo = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    fn, cajas = construir(solo)
    print(fn); [print(" ", k, [round(v, 2) for v in c]) for k, c in cajas.items()]
