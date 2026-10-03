"""Laminas DP-04 (secciones con acero), DP-05 (isometricos de secciones) y DP-06 (detalles tipicos)."""
import os, sys, math
import numpy as np
from ezdxf.enums import TextEntityAlignment as TA
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import diseno as dz
import dxf_base as B
from dxf_planta import prog_txt, perfil_en, terreno_en

D = dz.D
ACERO = {  # tipo: (marco, long, losa_sup e, muro e, descripcion)
    "NORMAL": ('marco 3/8" @0.20', 'long. 3/8" @0.25', D["e_losa"], D["e_muro"], "TRAMO NORMAL"),
    "MOTOS": ('marco 3/8" @0.15', 'long. 3/8" @0.25', D["e_losa"], D["e_muro"], "CRUCE DE MOTOS"),
    "CAMION": ('doble marco 1/2" @0.15', 'long. 3/8" @0.20', D["e_losa_camion"], D["e_muro"], "CRUCE DE CAMIONES"),
}
SECCIONES = [(0.50, "S-01"), (10.0, "S-02"), (20.0, "S-03"), (28.8, "S-04"), (40.0, "S-05"), (50.0, "S-06"), (60.0, "S-07"), (68.5, "S-08")]


def geometria(p):
    tipo = dz.zona(p); pp = min(p, dz.P_BRINK)
    cf = dz.fondo(pp); techo = dz.techo(p); h = techo - cf
    return dict(tipo=tipo, cf=cf, techo=techo, h=h, et=ACERO[tipo][2], em=ACERO[tipo][3])


def seccion(lam, xmm, ymm, p, R, T, esc_txt="1/25", nombre=None, con_cerco=True, hmm_txt=1.8, dist_cota=6, llamadas=True, dx_ll=0.80):
    """Seccion transversal mirando aguas abajo: izquierda = lado via (lindero), derecha = lado predio (cerco).
    Origen (xmm, ymm) = fondo del solado en el eje. Cotas por fuera (abajo y derecha), llamadas con flecha a la izquierda."""
    g = geometria(p); f = lam.f
    cx, cy = lam.P(xmm, ymm)
    be = D["b"] + 2 * g["em"]; b = D["b"]; ef = D["e_fondo"]; es = D["e_solado"]; em = g["em"]; et = g["et"]; h = g["h"]
    z0 = cy + es; zf = z0 + ef; zt = zf + h; zs = zt + et
    xl, xr = cx - be / 2, cx + be / 2
    # solado y concreto
    lam.rect(xl - 0.05, cy, xr + 0.05, z0, "SOLADO")
    lam.rect(xl, z0, xr, zs, "CONCRETO", const_width=0.004)
    lam.rect(xl + em, zf, xr - em, zt, "CONCRETO", const_width=0.004)
    for pts in ([(xl, z0), (xr, z0), (xr, zf), (xl, zf)], [(xl, zt), (xr, zt), (xr, zs), (xl, zs)],
                [(xl, zf), (xl + em, zf), (xl + em, zt), (xl, zt)], [(xr - em, zf), (xr, zf), (xr, zt), (xr - em, zt)]):
        lam.achurado(pts, escala_mm=0.5)
    # acero transversal (marco cerrado, rojo) y longitudinal (circulos azules sobre el marco)
    r = 0.04
    if g["tipo"] == "CAMION":
        rects = [(xl + r, z0 + r, xr - r, zs - r), (xl + em - r, zf - r, xr - em + r, zt + r)]
    else:
        rects = [(xl + em / 2, (z0 + zf) / 2, xr - em / 2, (zt + zs) / 2)]
    sep = 0.20 if g["tipo"] == "CAMION" else 0.25
    circ = []
    for (x1, y1, x2, y2) in rects:
        lam.rect(x1, y1, x2, y2, "ACERO")
        for (ax, ay, bx, by) in ((x1, y1, x2, y1), (x1, y2, x2, y2), (x1, y1, x1, y2), (x2, y1, x2, y2)):
            L = math.hypot(bx - ax, by - ay); n = max(1, int(round(L / sep)))
            for k in range(n + 1):
                t = k / n; pt = (ax + (bx - ax) * t, ay + (by - ay) * t)
                if pt not in circ: circ.append(pt); lam.bloque("ACERO-38", pt, 1.0)   # longitudinales 3/8" (en todas las zonas)
    # agua
    na = perfil_en(R, p, "NA"); y = na - g["cf"]
    lam.linea((xl + em, zf + y), (xr - em, zf + y), "AGUA"); lam.bloque("SIMB-AGUA", (cx, zf + y), f)
    # piso terminado a ambos lados y terreno existente lado via
    lam.poli([(xl - 1.0, zs), (xl, zs)], "TERRENO", ancho=0.3 * f); lam.poli([(xr, zs), (xr + 1.0, zs)], "TERRENO", ancho=0.3 * f)
    zterr = zs - (D["NPT"] - terreno_en(T, p))
    lam.poli([(xl - 1.0, zterr - 0.03), (xl - 0.5, zterr), (xl - 0.15, zterr + 0.02)], "TERRENO-EXISTENTE")
    lam.poli([(xl - 1.0, zterr - 0.03), (xl - 0.25, zterr - 0.03), (xl - 0.25, cy - 0.05), (xr + 0.25, cy - 0.05), (xr + 0.25, zs - 0.9)], "EXCAVACION")
    # cerco perimetrico al lado predio, con junta de tecnopor 1"
    xc = xr + D["junta_cerco"]
    if con_cerco:
        lam.rect(xc, zs - 0.6, xc + 0.15, zs + 0.6, "CERCO"); lam.rect(xc, zs - 0.9, xc + 0.40, zs - 0.6, "CERCO")
        lam.achurado([(xc, zs - 0.6), (xc + 0.15, zs - 0.6), (xc + 0.15, zs + 0.6), (xc, zs + 0.6)], "TERRENO-ACHURADO", escala_mm=0.4)
        lam.achurado([(xc, zs - 0.9), (xc + 0.40, zs - 0.9), (xc + 0.40, zs - 0.6), (xc, zs - 0.6)], "TERRENO-ACHURADO", escala_mm=0.4)
        lam.relleno([(xr, zs - 0.9), (xc, zs - 0.9), (xc, zs), (xr, zs)], "JUNTAS")
        lam.texto((xc + 0.22, zs + 0.12), "CERCO EXISTENTE", 1.5, "TEXTOS", TA.LEFT, rot=90)
    # cotas: abajo (parciales y total) y a la derecha (parciales y total), fuera del cerco
    lam.cota((xl, cy), (xl + em, cy), -dist_cota); lam.cota((xl + em, cy), (xr - em, cy), -dist_cota); lam.cota((xr - em, cy), (xr, cy), -dist_cota)
    lam.cota((xl, cy), (xr, cy), -2.2 * dist_cota)
    xd = (xc + 0.45) if con_cerco else (xr + 0.10)
    lam.linea((xr, z0), (xd, z0), "GUITARRA"); lam.linea((xr, zf), (xd, zf), "GUITARRA"); lam.linea((xr, zt), (xd, zt), "GUITARRA"); lam.linea((xr, zs), (xd, zs), "GUITARRA")
    lam.cota((xd, z0), (xd, zf), dist_cota * 0.6, horizontal=False); lam.cota((xd, zf), (xd, zt), dist_cota * 0.6, horizontal=False); lam.cota((xd, zt), (xd, zs), dist_cota * 0.6, horizontal=False)
    lam.cota((xd, z0), (xd, zs), dist_cota * 1.8, horizontal=False)
    lam.nivel((cx + 0.12, zf), g["cf"], texto="CF %.3f" % g["cf"], lado=1, hmm=1.6)
    # llamadas con flecha, ordenadas de arriba hacia abajo (no se cruzan)
    if llamadas:
        xt = xl - dx_ll
        filas = [("NPT +%.2f: losa superior e=%.2f (monolitica)" % (D["NPT"], et), (xl + em + 0.06, zs - et / 2)),
                 ("terreno existente %.2f" % terreno_en(T, p), (xl - 0.45, zterr)),
                 ("%s: acero transversal" % ACERO[g["tipo"]][0] + (" (ambas caras)" if g["tipo"] == "CAMION" else ""), (rects[0][0], zt - 0.12)),
                 ("%s: acero longitudinal" % ACERO[g["tipo"]][1], (rects[0][0], zt - 0.42)),
                 ("muro e=%.2f, h=%.2f" % (em, h), (xl + em / 2, zt - 0.75)),
                 ("NA %.3f (Q=%.1f L/s)" % (na, R["Q"]), (xl + em + 0.10, zf + y)),
                 ("losa de fondo e=%.2f" % ef, (xl - 0.02, zf - ef / 2)),
                 ("solado f'c=100 e=%.2f" % es, (xl - 0.06, cy + es / 2))]
        filas.sort(key=lambda fr: -fr[1][1])
        ytop, ybot = zs + 0.25, cy - 0.05
        for k, (txt, anc) in enumerate(filas):
            lam.llamada(anc, (xt, ytop - k * (ytop - ybot) / (len(filas) - 1)), [txt], hmm_txt, al=TA.RIGHT)
        lam.texto((xl - 0.6, zs + 0.55), "LADO VIA (LINDERO)", 1.6, "TEXTOS"); lam.texto((xr + 0.55, zs + 0.55), "LADO PREDIO", 1.6, "TEXTOS")
    return dict(cx=cx, cy=cy, zs=zs, zf=zf, zt=zt, xl=xl, xr=xr, g=g)


def dp04(doc, ox, oy, R, T):
    lams = []
    for k in range(2):
        lam = B.Lamina(doc, ox + k * 30, oy, 25, "DP-04%s" % "AB"[k], "SECCIONES TRANSVERSALES DEL COLECTOR",
                       "SECCIONES %s CON DISTRIBUCION DE ACERO - ESC. 1/25" % ("S-01 A S-04" if k == 0 else "S-05 A S-08"))
        for j, (p, nm) in enumerate(SECCIONES[k * 4:(k + 1) * 4]):
            xmm = 150 + j * 185; ymm = 300
            seccion(lam, xmm, ymm, p, R, T)
            g = geometria(p)
            lam.titulo_vista(xmm + 10, ymm - 60, "SECCION %s" % nm, "PROG. %s - CF %.3f - %s - ESC. 1/25" % (prog_txt(p), g["cf"], ACERO[g["tipo"]][4]), 100)
        lam.leyenda(32, 150, [("achurado", "CONCRETO-ACHURADO", "concreto armado f'c=210 kg/cm2"), ("rect", "SOLADO", "solado f'c=100 kg/cm2"),
                              ("linea", "ACERO", "acero transversal: marco cerrado (rojo)"), ("bloque:ACERO-38", "ACERO-PUNTOS", "acero longitudinal 3/8\" (circulo a diametro real)"),
                              ("linea", "AGUA", "nivel de agua de diseno"), ("linea2", "TERRENO", "piso terminado +260.60"),
                              ("linea", "TERRENO-EXISTENTE", "terreno existente"), ("linea", "EXCAVACION", "limite de excavacion"), ("rect", "CERCO", "cerco perimetrico existente")], 1.8)
        lam.notas(300, 150, "NOTAS", ["1. Altura interior h segun el perfil longitudinal (1.40 m en 0+000 a 1.61 m en el brink).",
                                        "2. Tramo normal y cruce de motos: un solo marco cerrado en el eje de muros y losas (una capa, E.060 14.3.4); recubrimiento minimo 0.04 m en muros y losa de fondo y 0.025 m en la losa superior.",
                                        "3. Junta de tecnopor de 1\" entre el muro lado predio y el cimiento del cerco; junta de 1\" entre la losa superior y el piso adyacente.",
                                        "4. El cruce de camiones (S-04) lleva losas e=0.25 y doble marco de 1/2\" @0.15 (marco exterior e interior, recubrimiento 0.04); el cruce de motos (S-05) marco unico de 3/8\" @0.15.",
                                        "5. Los registros no se ubican dentro de los cruces vehiculares."], 1.7)
        lams.append(lam)
    return lams


# ----------------------------------------------------------------------------
def iso_colector(lam, xmm, ymm, p, R, L=1.0, esc=1.0, con_tapa=True, con_agua=True, etiquetas=None):
    """Isometrico de un tramo de colector de longitud L (eje y) con la seccion en la cara frontal."""
    g = geometria(p); be = D["b"] + 2 * g["em"]; b = D["b"]; ef = D["e_fondo"]; e = g["em"]; h = g["h"]; et = g["et"]
    o = lam.P(xmm, ymm)
    T = lambda x, y, z: (o[0] + B.iso(x, y, z)[0] * esc, o[1] + B.iso(x, y, z)[1] * esc)
    kw = dict(origen=o, esc=esc)
    # fondo
    B.caja_iso(lam, 0, 0, 0, be, L, ef, **kw)
    # cara interior del muro izquierdo (visible)
    pts = [T(e, 0, ef), T(e, L, ef), T(e, L, ef + h), T(e, 0, ef + h)]
    lam.solido([pts[0], pts[1], pts[3], pts[2]], "ISO-CONCRETO-LAT2"); lam.poli(pts, "ISO-ARISTAS", cerrada=True)
    # muro izquierdo y derecho
    B.caja_iso(lam, 0, 0, ef, e, L, h, **kw)
    if con_agua:
        y = perfil_en(R, p, "NA") - g["cf"]
        pa = [T(e, 0, ef + y), T(be - e, 0, ef + y), T(be - e, L, ef + y), T(e, L, ef + y)]
        lam.solido([pa[0], pa[1], pa[3], pa[2]], "ISO-AGUA"); lam.poli(pa, "ISO-ARISTAS", cerrada=True)
    B.caja_iso(lam, be - e, 0, ef, e, L, h, **kw)
    # losa superior
    B.caja_iso(lam, 0, 0, ef + h, be, L, et, capas=("ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2"), **kw)
    if con_tapa and L >= 1.0:
        tx, ty = be / 2 - 0.34, L / 2 - 0.34
        B.caja_iso(lam, tx, ty, ef + h + et, 0.68, 0.68, 0.012, capas=("ISO-TAPA", "ISO-TAPA", "ISO-TAPA"), **kw)
    # acero en la cara de corte (frontal, y = L): marco
    r = 0.04
    if g["tipo"] == "CAMION":
        m = [T(r, L, r), T(be - r, L, r), T(be - r, L, ef + h + et - r), T(r, L, ef + h + et - r)]
        lam.poli(m, "ACERO", cerrada=True)
        m2 = [T(e - r, L, ef - r), T(be - e + r, L, ef - r), T(be - e + r, L, ef + h + r), T(e - r, L, ef + h + r)]
        lam.poli(m2, "ACERO", cerrada=True)
    else:
        m = [T(e / 2, L, ef / 2), T(be - e / 2, L, ef / 2), T(be - e / 2, L, ef + h + et / 2), T(e / 2, L, ef + h + et / 2)]
        lam.poli(m, "ACERO", cerrada=True)
    # acero longitudinal: puntos sobre el marco en la cara de corte
    sep = 0.20 if g["tipo"] == "CAMION" else 0.25
    if g["tipo"] == "CAMION":
        lazos = [[(r, r), (be - r, r), (be - r, ef + h + et - r), (r, ef + h + et - r)], [(e - r, ef - r), (be - e + r, ef - r), (be - e + r, ef + h + r), (e - r, ef + h + r)]]
    else:
        lazos = [[(e / 2, ef / 2), (be - e / 2, ef / 2), (be - e / 2, ef + h + et / 2), (e / 2, ef + h + et / 2)]]
    for lazo in lazos:
        for (x1, z1), (x2, z2) in zip(lazo, lazo[1:] + lazo[:1]):
            Ls = math.hypot(x2 - x1, z2 - z1); n = max(1, int(Ls / sep))
            for k in range(n + 1):
                t = k / n; x, z = x1 + (x2 - x1) * t, z1 + (z2 - z1) * t
                lam.bloque("ACERO-38", T(x, L, z), 1.0 * esc)
    if etiquetas:
        lam.textos(T(be + 0.3, 0, ef + h + et + 0.1), etiquetas, 1.8)
    return T


def dp05(doc, ox, oy, R, T):
    lams = []
    for k in range(2):
        lam = B.Lamina(doc, ox + k * 30, oy, 25, "DP-05%s" % "AB"[k], "ISOMETRICOS DE LAS SECCIONES TRANSVERSALES",
                       "SECCIONES %s - TRAMOS DE 1.00 m CON REGISTRO Y ACERO EN LA CARA DE CORTE" % ("S-01 A S-04" if k == 0 else "S-05 A S-08"))
        for j, (p, nm) in enumerate(SECCIONES[k * 4:(k + 1) * 4]):
            xmm = 90 + j * 185; ymm = 300; g = geometria(p)
            iso_colector(lam, xmm, ymm, p, R, 1.0, 1.0, etiquetas=["CF %.3f" % g["cf"], "losa superior %.2f" % D["NPT"], "NA %.3f" % perfil_en(R, p, "NA"),
                                                                     ACERO[g["tipo"]][0], ACERO[g["tipo"]][1], "registro: tapa 0.68 x 0.68, luz 0.60", "h interior %.2f m" % g["h"]])
            lam.titulo_vista(xmm + 30, ymm - 60, "ISOMETRICO %s" % nm, "PROG. %s - interior 0.80 x %.2f m - %s" % (prog_txt(p), g["h"], ACERO[g["tipo"]][4]), 100)
        lam.leyenda(32, 150, [("relleno", "ISO-CONCRETO-SUP", "concreto armado (cara superior)"), ("relleno", "ISO-CONCRETO-LAT1", "concreto armado (cara frontal / corte)"),
                              ("relleno", "ISO-CONCRETO-LAT2", "concreto armado (cara lateral)"), ("relleno", "ISO-TAPA", "tapa de registro removible"),
                              ("relleno", "ISO-AGUA", "agua (nivel de diseno)"), ("linea", "ACERO", "acero en la cara de corte")], 1.8)
        lam.notas(300, 150, "NOTAS", ["1. Vistas isometricas sin escala; medidas reales en las laminas DP-04 y DP-06.", "2. Se muestra 1.00 m de colector cortado en la progresiva indicada."], 1.7)
        lams.append(lam)
    return lams


# ----------------------------------------------------------------------------
def dp06a(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 10, "DP-06A", "DETALLES TIPICOS DEL COLECTOR", "SECCIONES TIPICAS: TRAMO NORMAL, CRUCE DE MOTOS, CRUCE DE CAMIONES Y TRAMO DIAGONAL - ESC. 1/10")
    casos = [(10.0, "A-A: TRAMO NORMAL"), (40.0, "B-B: CRUCE DE MOTOS"), (28.8, "C-C: CRUCE DE CAMIONES")]
    for j, (p, nm) in enumerate(casos):
        xmm = 165 + j * 268; ymm = 300
        seccion(lam, xmm, ymm, p, R, T, esc_txt="1/10", con_cerco=True, hmm_txt=1.6, dist_cota=8, dx_ll=0.12)
        g = geometria(p)
        lam.titulo_vista(xmm + 40, ymm - 45, "SECCION TIPICA %s" % nm, "ESC. 1/10 - h segun perfil (aqui %.2f m, prog. %s)" % (g["h"], prog_txt(p)), 150)
    lam.leyenda(32, 110, [("achurado", "CONCRETO-ACHURADO", "concreto armado f'c=210 kg/cm2"), ("rect", "SOLADO", "solado f'c=100 kg/cm2 e=0.05"),
                          ("linea", "ACERO", "acero transversal: marco cerrado (rojo)"), ("bloque:ACERO-38", "ACERO-PUNTOS", "acero longitudinal 3/8\" visto en la cara de corte"), ("linea", "AGUA", "nivel de agua de diseno"),
                          ("rect", "CERCO", "cerco perimetrico existente"), ("linea", "JUNTAS", "junta de tecnopor 1\"")], 1.8)
    lam.notas(300, 110, "NOTAS", ["1. Muros e=0.15 en todo el tramo; losa de fondo e=0.15; losa superior e=0.10 (e=0.25 en el cruce de camiones).",
                                    "2. Tramo normal y motos: marco unico en el eje de la seccion. En el cruce de camiones el acero va en ambas caras (doble marco 1/2\" @0.15) y la losa superior es e=0.25.",
                                    "3. El tramo diagonal (quiebres a 45 grados) tiene la seccion tipica A-A; en las esquinas las barras llevan ganchos de 0.40 m (ver DP-09).",
                                    "4. Empalme de las cunetas: ver DP-06C. Registro, tapa y junta: ver DP-06B."], 1.7)
    return lam


def dp06b(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 10, "DP-06B", "DETALLES DE REGISTRO DE LIMPIEZA, TAPA, MARCO Y CONTRAMARCO", "REGISTRO CON TAPA REMOVIBLE, ANGULOS METALICOS, EMPALME DE CUNETA Y JUNTA DE DILATACION")
    f = lam.f
    # A. registro planta (eje de colector horizontal), b_ext 1.10
    ox_, oy_ = lam.P(120, 430); be = D["b_ext"]
    lam.rect(ox_ - 1.0, oy_ - be / 2, ox_ + 1.0, oy_ + be / 2, "CONCRETO")
    lam.rect(ox_ - 1.0, oy_ - D["b"] / 2, ox_ + 1.0, oy_ + D["b"] / 2, "CONCRETO-OCULTO")
    lam.rect(ox_ - 0.35, oy_ - 0.35, ox_ + 0.35, oy_ + 0.35, "MARCO-METALICO", const_width=0.006)
    lam.rect(ox_ - 0.34, oy_ - 0.34, ox_ + 0.34, oy_ + 0.34, "REGISTRO-TAPA")
    lam.rect(ox_ - 0.30, oy_ - 0.30, ox_ + 0.30, oy_ + 0.30, "REGISTRO")
    lam.rect(ox_ - 0.45, oy_ - 0.45, ox_ + 0.45, oy_ + 0.45, "CONCRETO-OCULTO")
    lam.achurado([(ox_ - 0.34, oy_ - 0.34), (ox_ + 0.34, oy_ - 0.34), (ox_ + 0.34, oy_ + 0.34), (ox_ - 0.34, oy_ + 0.34)], escala_mm=0.6)
    lam.circulo((ox_ - 0.12, oy_), 0.012, "MARCO-METALICO"); lam.circulo((ox_ + 0.12, oy_), 0.012, "MARCO-METALICO")
    for k in range(8):
        a = math.radians(45 * k); lam.bloque("ACERO-12", (ox_ + 0.40 * math.cos(a), oy_ + 0.40 * math.sin(a)), 1.0)
    lam.linea((ox_ - 1.0, oy_), (ox_ + 1.0, oy_), "EJE-COLECTOR")
    lam.cota((ox_ - 0.35, oy_ - be / 2), (ox_ + 0.35, oy_ - be / 2), -8, texto="0.70")
    lam.cota((ox_ - 0.30, oy_ - be / 2), (ox_ + 0.30, oy_ - be / 2), -4, texto="0.60")
    lam.cota((ox_ - 0.45, oy_ - be / 2), (ox_ + 0.45, oy_ - be / 2), -12, texto="0.90")
    lam.cota((ox_ + 1.0, oy_ - be / 2), (ox_ + 1.0, oy_ + be / 2), 6, horizontal=False)
    lam.cota((ox_ + 1.0, oy_ - 0.34), (ox_ + 1.0, oy_ + 0.34), 10, horizontal=False)
    xt = ox_ + 1.3
    lam.llamada((ox_ + 0.35, oy_ + 0.33), (xt, oy_ + 0.55), ['contramarco: angulo L 2"x2"x3/16" (perimetro 0.70 x 0.70)'], 1.8)
    lam.llamada((ox_ + 0.34, oy_ + 0.2), (xt, oy_ + 0.40), ['marco de tapa: angulo L 1 1/2"x1 1/2"x1/8" (0.68 x 0.68)'], 1.8)
    lam.llamada((ox_ + 0.25, oy_ + 0.08), (xt, oy_ + 0.25), ["tapa de concreto armado 0.68 x 0.68 x 0.08 (removible)"], 1.8)
    lam.llamada((ox_ + 0.40, oy_ + 0.05), (xt, oy_ + 0.10), ['anclajes 3/8" L=0.20 soldados (2 por lado)'], 1.8)
    lam.llamada((ox_ + 0.12, oy_), (xt, oy_ - 0.05), ['asas: 2 de 3/8" liso, embutidas'], 1.8)
    lam.llamada((ox_ + 0.40 * 0.707, oy_ - 0.40 * 0.707), (xt, oy_ - 0.22), ['refuerzo de borde: 2 barras 1/2" por lado, L=1.40'], 1.8)
    lam.llamada((ox_ + 0.45, oy_ - 0.45), (xt, oy_ - 0.38), ["borde engrosado 0.15 x 0.10 bajo la losa (oculto)"], 1.8)
    lam.titulo_vista(120, 352, "A. REGISTRO DE LIMPIEZA - PLANTA", "ESC. 1/10 - 7 und (RS-01 a RS-07) + 3 en las cajas CL y CC", 120)
    # B. corte por el registro
    ox_, oy_ = lam.P(120, 150); h = 1.50; et = D["e_losa"]; em = D["e_muro"]; ef = D["e_fondo"]
    xl, xr = ox_ - be / 2, ox_ + be / 2; zb = oy_; zf = zb + ef; zt = zf + h; zs = zt + et
    lam.rect(xl, zb, xr, zs, "CONCRETO", const_width=0.004); lam.rect(xl + em, zf, xr - em, zt, "CONCRETO-OCULTO")
    # abertura 0.70 en la losa con borde engrosado 0.15x0.10
    lam.poli([(xl + em, zt), (ox_ - 0.45, zt), (ox_ - 0.45, zt - 0.10), (ox_ - 0.35, zt - 0.10), (ox_ - 0.35, zs - 0.08), (ox_ - 0.35, zs)], "CONCRETO")
    lam.poli([(xr - em, zt), (ox_ + 0.45, zt), (ox_ + 0.45, zt - 0.10), (ox_ + 0.35, zt - 0.10), (ox_ + 0.35, zs - 0.08), (ox_ + 0.35, zs)], "CONCRETO")
    for pts in ([(xl, zb), (xr, zb), (xr, zf), (xl, zf)], [(xl, zf), (xl + em, zf), (xl + em, zs), (xl, zs)], [(xr - em, zf), (xr, zf), (xr, zs), (xr - em, zs)],
                [(xl + em, zt), (ox_ - 0.45, zt), (ox_ - 0.45, zt - 0.10), (ox_ - 0.35, zt - 0.10), (ox_ - 0.35, zs), (xl + em, zs)],
                [(xr - em, zt), (ox_ + 0.45, zt), (ox_ + 0.45, zt - 0.10), (ox_ + 0.35, zt - 0.10), (ox_ + 0.35, zs), (xr - em, zs)]):
        lam.achurado(pts, escala_mm=0.5)
    lam.rect(ox_ - 0.34, zs - 0.08, ox_ + 0.34, zs, "REGISTRO-TAPA"); lam.achurado([(ox_ - 0.34, zs - 0.08), (ox_ + 0.34, zs - 0.08), (ox_ + 0.34, zs), (ox_ - 0.34, zs)], escala_mm=0.4)
    lam.poli([(ox_ - 0.35, zs - 0.08), (ox_ - 0.35, zs), (ox_ - 0.30, zs)], "MARCO-METALICO", ancho=0.006); lam.poli([(ox_ + 0.35, zs - 0.08), (ox_ + 0.35, zs), (ox_ + 0.30, zs)], "MARCO-METALICO", ancho=0.006)
    lam.poli([(xl - 0.6, zs), (xl, zs)], "TERRENO", ancho=0.3 * f); lam.poli([(xr, zs), (xr + 0.6, zs)], "TERRENO", ancho=0.3 * f)
    lam.nivel((xr + 0.3, zs), D["NPT"], texto="NPT +260.60")
    lam.nivel((ox_, zf), 0, texto="CF (ver perfil)")
    lam.cota((ox_ - 0.35, zs), (ox_ + 0.35, zs), 10, texto="0.70"); lam.cota((ox_ - 0.30, zt), (ox_ + 0.30, zt), -6, texto="0.60")
    lam.cota((xl, zt), (xl, zs), -6, horizontal=False); lam.cota((xl, zf), (xl, zt), -6, horizontal=False, texto="h"); lam.cota((xl, zb), (xl, zf), -6, horizontal=False)
    lam.cota((xl, zb), (xr, zb), -8)
    lam.circulo((ox_ + 0.35, zs - 0.04), 0.07, "CORTES"); lam.texto((ox_ + 0.45, zs + 0.06), "DET. 1", 1.8, "CORTES")
    lam.titulo_vista(120, 132, "B. CORTE A-A POR EL REGISTRO", "ESC. 1/10", 120)
    # C. detalle apoyo de tapa 1/2.5 (dibujado a escala 4x respecto a 1/10)
    ox_, oy_ = lam.P(400, 250); k = 4.0
    lam.poli([(ox_, oy_), (ox_ + 0.35 * k, oy_), (ox_ + 0.35 * k, oy_ + 0.20 * k), (ox_ + 0.03 * k, oy_ + 0.20 * k), (ox_ + 0.03 * k, oy_ + 0.12 * k), (ox_, oy_ + 0.12 * k)], "CONCRETO", cerrada=True)
    lam.achurado([(ox_, oy_), (ox_ + 0.35 * k, oy_), (ox_ + 0.35 * k, oy_ + 0.20 * k), (ox_ + 0.03 * k, oy_ + 0.20 * k), (ox_ + 0.03 * k, oy_ + 0.12 * k), (ox_, oy_ + 0.12 * k)], escala_mm=1.5)
    lam.poli([(ox_ - 0.0, oy_ + 0.12 * k), (ox_ + 0.03 * k, oy_ + 0.12 * k), (ox_ + 0.03 * k, oy_ + 0.20 * k)], "MARCO-METALICO", ancho=0.012)   # contramarco L
    lam.poli([(ox_ - 0.30 * k, oy_ + 0.125 * k), (ox_ - 0.005 * k, oy_ + 0.125 * k), (ox_ - 0.005 * k, oy_ + 0.20 * k)], "MARCO-METALICO", ancho=0.010)  # marco de tapa L
    lam.rect(ox_ - 0.30 * k, oy_ + 0.125 * k, ox_ - 0.01 * k, oy_ + 0.20 * k, "REGISTRO-TAPA"); lam.achurado([(ox_ - 0.30 * k, oy_ + 0.125 * k), (ox_ - 0.01 * k, oy_ + 0.125 * k), (ox_ - 0.01 * k, oy_ + 0.20 * k), (ox_ - 0.30 * k, oy_ + 0.20 * k)], escala_mm=1.5)
    lam.poli([(ox_ + 0.03 * k, oy_ + 0.16 * k), (ox_ + 0.23 * k, oy_ + 0.16 * k)], "ACERO", ancho=0.01); lam.bloque("ACERO-12", (ox_ + 0.20 * k, oy_ + 0.05 * k), k)
    xt = ox_ + 0.45 * k
    lam.llamada((ox_ + 0.03 * k, oy_ + 0.18 * k), (xt, oy_ + 0.30 * k), ['contramarco L 2"x2"x3/16" (enrasado con NPT)'], 1.8)
    lam.llamada((ox_ - 0.005 * k, oy_ + 0.18 * k), (xt, oy_ + 0.24 * k), ['marco de tapa L 1 1/2"x1 1/2"x1/8"'], 1.8)
    lam.llamada((ox_ + 0.15 * k, oy_ + 0.16 * k), (xt, oy_ + 0.16 * k), ['anclaje 3/8" L=0.20 soldado c/0.25'], 1.8)
    lam.llamada((ox_ + 0.01 * k, oy_ + 0.13 * k), (xt, oy_ + 0.09 * k), ["holgura 5 mm entre marco y contramarco; apoyo 0.05"], 1.8)
    lam.llamada((ox_ + 0.20 * k, oy_ + 0.05 * k), (xt, oy_ + 0.02 * k), ['refuerzo de borde 1/2"'], 1.8)
    lam.cota((ox_ - 0.30 * k, oy_ + 0.20 * k), (ox_ - 0.01 * k, oy_ + 0.20 * k), 6, texto="0.29 (media tapa)"); lam.cota((ox_, oy_ + 0.12 * k), (ox_ + 0.03 * k, oy_ + 0.12 * k), -5, texto='2" (50.8 mm)')
    lam.cota((ox_ + 0.35 * k, oy_), (ox_ + 0.35 * k, oy_ + 0.20 * k), 6, horizontal=False, texto="0.20")
    lam.titulo_vista(430, 215, "C. DETALLE 1: APOYO DE TAPA", "ESC. 1/2.5", 120)
    # D. tapa armado y corte
    ox_, oy_ = lam.P(650, 470)
    lam.rect(ox_, oy_, ox_ + 0.68, oy_ + 0.68, "REGISTRO-TAPA", const_width=0.004)
    for k2 in range(7):
        d = 0.04 + k2 * 0.10
        lam.linea((ox_ + 0.03, oy_ + d), (ox_ + 0.65, oy_ + d), "ACERO"); lam.linea((ox_ + d, oy_ + 0.03), (ox_ + d, oy_ + 0.65), "ACERO")
    lam.circulo((ox_ + 0.22, oy_ + 0.34), 0.015, "MARCO-METALICO"); lam.circulo((ox_ + 0.46, oy_ + 0.34), 0.015, "MARCO-METALICO")
    lam.cota((ox_, oy_), (ox_ + 0.68, oy_), -6); lam.cota((ox_ + 0.68, oy_), (ox_ + 0.68, oy_ + 0.68), 6, horizontal=False)
    lam.cota((ox_ + 0.04, oy_ + 0.68), (ox_ + 0.14, oy_ + 0.68), 5, texto="0.10")
    lam.titulo_vista(684, 450, "D. TAPA - ARMADO", '7 + 7 barras 3/8" @0.10, L=0.62; asas 3/8" liso', 100)
    ox2, oy2 = lam.P(650, 390)
    lam.rect(ox2, oy2, ox2 + 0.68, oy2 + 0.08, "REGISTRO-TAPA", const_width=0.004); lam.achurado([(ox2, oy2), (ox2 + 0.68, oy2), (ox2 + 0.68, oy2 + 0.08), (ox2, oy2 + 0.08)], escala_mm=0.5)
    lam.linea((ox2 + 0.03, oy2 + 0.025), (ox2 + 0.65, oy2 + 0.025), "ACERO"); lam.poli([(ox2 + 0.22, oy2 + 0.08), (ox2 + 0.22, oy2 + 0.03), (ox2 + 0.30, oy2 + 0.03), (ox2 + 0.30, oy2 + 0.08)], "MARCO-METALICO")
    lam.cota((ox2, oy2), (ox2 + 0.68, oy2), -6); lam.cota((ox2 + 0.68, oy2), (ox2 + 0.68, oy2 + 0.08), 6, horizontal=False)
    lam.titulo_vista(684, 365, "D. TAPA - CORTE", "concreto f'c=210 kg/cm2 - peso aprox. 95 kg", 100)
    # F. junta de dilatacion
    ox_, oy_ = lam.P(330, 490)
    lam.rect(ox_ - 0.6, oy_, ox_ - 0.0127, oy_ + 0.15, "CONCRETO"); lam.rect(ox_ + 0.0127, oy_, ox_ + 0.6, oy_ + 0.15, "CONCRETO")
    lam.achurado([(ox_ - 0.6, oy_), (ox_ - 0.0127, oy_), (ox_ - 0.0127, oy_ + 0.15), (ox_ - 0.6, oy_ + 0.15)], escala_mm=0.5)
    lam.achurado([(ox_ + 0.0127, oy_), (ox_ + 0.6, oy_), (ox_ + 0.6, oy_ + 0.15), (ox_ + 0.0127, oy_ + 0.15)], escala_mm=0.5)
    lam.rect(ox_ - 0.0127, oy_, ox_ + 0.0127, oy_ + 0.125, "JUNTAS"); lam.relleno([(ox_ - 0.0127, oy_ + 0.125), (ox_ + 0.0127, oy_ + 0.125), (ox_ + 0.0127, oy_ + 0.15), (ox_ - 0.0127, oy_ + 0.15)], "RELLENO")
    lam.llamada((ox_, oy_ + 0.14), (ox_ + 0.75, oy_ + 0.30), ['sello asfaltico 1" x 1"'], 1.8)
    lam.llamada((ox_, oy_ + 0.07), (ox_ + 0.75, oy_ + 0.22), ['relleno de tecnopor (poliestireno expandido) 1"'], 1.8)
    lam.cota((ox_ - 0.0127, oy_ + 0.15), (ox_ + 0.0127, oy_ + 0.15), 5, texto='1"')
    lam.titulo_vista(330, 460, "F. JUNTA DE DILATACION CADA 4.00 m", "ESC. 1/5 aprox. - en muros, losa de fondo y losa superior", 120)
    lam.leyenda(480, 100, [("achurado", "CONCRETO-ACHURADO", "concreto armado f'c=210 kg/cm2"), ("linea2", "MARCO-METALICO", "angulos metalicos (marco y contramarco)"),
                          ("rect", "REGISTRO-TAPA", "tapa removible"), ("linea", "ACERO", "acero de refuerzo"), ("linea", "JUNTAS", "junta de dilatacion / tecnopor")], 1.8)
    lam.notas(300, 100, "MATERIALES POR REGISTRO", ['Contramarco angulo L 2"x2"x3/16": 4 x 0.70 = 2.80 m (10.2 kg); anclajes 3/8" L=0.20: 8 und', 'Marco de tapa angulo L 1 1/2"x1 1/2"x1/8": 4 x 0.68 = 2.72 m (5.0 kg)',
                                                     'Acero tapa 3/8" @0.10: 14 x 0.62 = 8.68 m (4.9 kg); asas 3/8" liso: 2 x 0.40 m', "Concreto tapa f'c=210: 0.68 x 0.68 x 0.08 = 0.037 m3",
                                                     'Refuerzo de borde 1/2": 8 x 1.40 = 11.20 m (11.1 kg); borde engrosado: perimetro 3.00 x 0.15 x 0.10 = 0.045 m3'], 1.7)
    return lam


def dp06c(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 10, "DP-06C", "DETALLE DEL EMPALME DE CUNETA AL COLECTOR", "VENTANA EN EL MURO LADO PREDIO, CAIDA AL FONDO, JUNTAS Y REGISTRO - CUNETAS EJES 01, 02, 06, 07, 11 Y 12 - ESC. 1/10")
    f = lam.f; be = D["b_ext"]
    # E1. planta
    ox_, oy_ = lam.P(230, 400)
    lam.rect(ox_ - 1.5, oy_ - be / 2, ox_ + 1.5, oy_ + be / 2, "CONCRETO", const_width=0.004); lam.rect(ox_ - 1.5, oy_ - D["b"] / 2, ox_ + 1.5, oy_ + D["b"] / 2, "CONCRETO-OCULTO")
    lam.linea((ox_ - 1.5, oy_), (ox_ + 1.5, oy_), "EJE-COLECTOR")
    lam.rect(ox_ - 0.30, oy_ + D["b"] / 2, ox_ + 0.30, oy_ + be / 2 + 1.2, "CUNETA"); lam.rect(ox_ - 0.20, oy_ + D["b"] / 2, ox_ + 0.20, oy_ + be / 2 + 1.2, "CUNETA-OCULTA")
    lam.rect(ox_ - 0.20, oy_ + D["b"] / 2, ox_ + 0.20, oy_ + be / 2, "CONCRETO-OCULTO")   # ventana en el muro
    yc_ = oy_ + be / 2 + D["junta_cerco"]
    lam.linea((ox_ - 0.35, yc_), (ox_ + 0.35, yc_), "JUNTAS"); lam.linea((ox_ - 0.35, yc_ + 0.15), (ox_ + 0.35, yc_ + 0.15), "JUNTAS")
    lam.rect(ox_ - 1.5, yc_, ox_ - 0.30, yc_ + 0.15, "CERCO"); lam.rect(ox_ + 0.30, yc_, ox_ + 1.5, yc_ + 0.15, "CERCO")
    lam.achurado([(ox_ - 1.5, yc_), (ox_ - 0.30, yc_), (ox_ - 0.30, yc_ + 0.15), (ox_ - 1.5, yc_ + 0.15)], "TERRENO-ACHURADO", escala_mm=0.4)
    lam.achurado([(ox_ + 0.30, yc_), (ox_ + 1.5, yc_), (ox_ + 1.5, yc_ + 0.15), (ox_ + 0.30, yc_ + 0.15)], "TERRENO-ACHURADO", escala_mm=0.4)
    lam.rect(ox_ - 0.35, oy_ - 0.35, ox_ + 0.35, oy_ + 0.35, "MARCO-METALICO", const_width=0.006); lam.rect(ox_ - 0.30, oy_ - 0.30, ox_ + 0.30, oy_ + 0.30, "REGISTRO")
    lam.bloque("SIMB-FLECHA", (ox_, oy_ + be / 2 + 0.8), f, rot=-90, capa="FLUJO"); lam.bloque("SIMB-FLECHA", (ox_ - 1.0, oy_), f, rot=180, capa="FLUJO")
    xt = ox_ + 1.7
    lam.llamada((ox_ + 0.3, oy_ + be / 2 + 1.0), (xt, oy_ + be / 2 + 1.15), ["cuneta de arquitectura 0.40 x H, muros 0.10 (NCF segun perfil 01 a 12)"], 1.8)
    lam.llamada((ox_ + 0.3, yc_ + 0.07), (xt, oy_ + be / 2 + 0.85), ["paso por el cerco existente: abertura 0.60 (cuneta con sus muros); junta de tecnopor 1\" a ambos lados"], 1.8)
    lam.llamada((ox_ + 0.2, oy_ + be / 2 - 0.07), (xt, oy_ + be / 2 + 0.55), ["ventana 0.40 x H en el muro lado predio del colector (sin losa de cierre: caida libre)"], 1.8)
    lam.llamada((ox_ + 0.35, oy_ + 0.2), (xt, oy_ + 0.25), ["registro de limpieza encima del empalme (tapa 0.68 x 0.68)"], 1.8)
    lam.llamada((ox_ + 1.2, oy_ - be / 2), (xt, oy_ - 0.2), ["colector b = 0.80, muros e = 0.15"], 1.8)
    lam.textos((xt, oy_ - 0.65), ["NOTA: las cunetas de los Ejes 11 y 12 se prolongan 1.88 y 5.39 m hasta el muro del colector con su misma seccion;", "esa prolongacion se metra en la partida de cunetas del proyecto (no forma parte de la partida 01.04.04 del colector)."], 1.8)
    lam.cota((ox_ - 0.20, oy_ + be / 2 + 1.2), (ox_ + 0.20, oy_ + be / 2 + 1.2), 8, texto="0.40"); lam.cota((ox_ - 0.30, oy_ + be / 2 + 1.2), (ox_ + 0.30, oy_ + be / 2 + 1.2), 14, texto="0.60")
    lam.cota((ox_ - 1.5, oy_ - be / 2), (ox_ - 1.5, oy_ + be / 2), -8, horizontal=False); lam.cota((ox_ - 1.5, oy_ - D["b"] / 2), (ox_ - 1.5, oy_ + D["b"] / 2), -4, horizontal=False)
    lam.cota((ox_ - 0.35, oy_ - be / 2), (ox_ + 0.35, oy_ - be / 2), -8, texto="0.70")
    lam.titulo_vista(230, 300, "E1. EMPALME DE CUNETA - PLANTA", "ESC. 1/10 - losa superior retirada para mostrar la ventana", 140)
    # E2. corte transversal por el empalme (mirando aguas abajo): colector + ventana + cuneta + cerco
    p = 11.27; g = geometria(p); ef = D["e_fondo"]; es = D["e_solado"]; em = g["em"]; et = g["et"]; h = g["h"]
    ox_, oy_ = lam.P(230, 60); cy = oy_; z0 = cy + es; zf = z0 + ef; zt = zf + h; zs = zt + et
    xl, xr = ox_ - be / 2, ox_ + be / 2
    lam.rect(xl - 0.05, cy, xr + 0.05, z0, "SOLADO")
    # muro izquierdo completo, muro derecho con ventana (de zf+... hasta zt): la cuneta llega con NCF
    NCF = [c for c in R["cunetas"] if abs(c["prog"] - p) < 0.5][0]["NCF_fin"]; zc = zf + (NCF - g["cf"]); H = 260.60 - NCF
    lam.poli([(xl, z0), (xr, z0), (xr, zc - 0.10), (xr - em, zc - 0.10), (xr - em, zf), (xl + em, zf), (xl + em, zt), (xr - em, zt), (xr - em, zt), (xr, zt), (xr, zs), (xl, zs)], "CONCRETO", cerrada=True, ancho=0.004)
    for pts in ([(xl, z0), (xr, z0), (xr, zf), (xl, zf)], [(xl, zf), (xl + em, zf), (xl + em, zs), (xl, zs)], [(xr - em, zf), (xr, zf), (xr, zc - 0.10), (xr - em, zc - 0.10)],
                [(xl + em, zt), (xr, zt), (xr, zs), (xl + em, zs)]):
        lam.achurado(pts, escala_mm=0.5)
    # cuneta: fondo a NCF, muros 0.10, altura H hasta NPT
    xq = xr + D["junta_cerco"]
    lam.poli([(xq, zc - 0.10), (xq + 0.9, zc - 0.10), (xq + 0.9, zs), (xq + 0.8, zs), (xq + 0.8, zc), (xq, zc)], "CUNETA", cerrada=False, ancho=0.004)
    lam.achurado([(xq, zc - 0.10), (xq + 0.9, zc - 0.10), (xq + 0.9, zc), (xq, zc)], "TERRENO-ACHURADO", escala_mm=0.4)
    lam.achurado([(xq + 0.8, zc), (xq + 0.9, zc), (xq + 0.9, zs), (xq + 0.8, zs)], "TERRENO-ACHURADO", escala_mm=0.4)
    lam.linea((xq, zc + 0.05), (xq + 0.8, zc + 0.05), "AGUA")
    lam.poli([(xr, zc - 0.10), (xr, zs)], "JUNTAS")
    lam.poli([(xr - em, zc), (xr - em + 0.05, zc + 0.02)], "FLUJO"); lam.bloque("SIMB-FLECHA", (xr - 0.35, zc + 0.15), f * 0.8, rot=-135, capa="FLUJO")
    y = perfil_en(R, p, "NA") - g["cf"]; lam.linea((xl + em, zf + y), (xr - em, zf + y), "AGUA"); lam.bloque("SIMB-AGUA", (ox_, zf + y), f)
    lam.poli([(xl - 0.8, zs), (xl, zs)], "TERRENO", ancho=0.3 * f); lam.poli([(xq + 0.9, zs), (xq + 1.6, zs), (xq + 1.6, zs)], "TERRENO", ancho=0.3 * f)
    lam.nivel((xl - 0.5, zs), D["NPT"], texto="NPT +260.60", lado=-1); lam.nivel((xq + 0.4, zc), NCF, texto="NCF cuneta (ej. %.2f)" % NCF, lado=1)
    lam.nivel((ox_, zf), g["cf"], texto="CF colector (ej. %.3f)" % g["cf"], lado=1, hmm=1.6)
    lam.cota((xq, zc), (xq + 0.8, zc), -6, texto="0.40"); lam.cota((xq + 0.9, zc), (xq + 0.9, zs), 6, horizontal=False, texto="H")
    lam.cota((xr - em, zc), (xr - em, zt), 4, horizontal=False, texto="ventana"); lam.cota((xl, cy), (xr, cy), -8)
    lam.cota((xr, zc - 0.10), (xq, zc - 0.10), -14, texto='1"')
    xt = xq + 1.8
    lam.llamada((xr, zc + 0.6), (xt, zs + 0.1), ["junta de tecnopor 1\" entre colector, cuneta y cerco"], 1.8)
    lam.llamada((xr - em / 2, zc + 0.3), (xt, zs - 0.3), ["ventana 0.40 x (zt - NCF) en el muro lado predio; sin dintel adicional (losa superior monolitica)"], 1.8)
    lam.llamada((xq + 0.4, zc + 0.05), (xt, zs - 0.7), ["cuneta 0.40 x H: llega con su NCF y vierte en caida libre al colector"], 1.8)
    lam.llamada((ox_, zf + y), (xt, zs - 1.1), ["NA del colector siempre bajo el fondo de la cuneta (ver hoja CUNETAS de la memoria)"], 1.8)
    lam.llamada((ox_ + 0.2, zf + 0.02), (xt, zf - 0.1), ["caida libre al fondo: losa de fondo con acabado pulido en 1.00 m"], 1.8)
    lam.titulo_vista(230, 20, "E2. EMPALME DE CUNETA - CORTE TRANSVERSAL (MIRANDO AGUAS ABAJO)", "ESC. 1/10 - ejemplo cuneta Eje 02 (0+011.27); en las demas varia H y la cota de fondo", 220)
    lam.leyenda(610, 300, [("achurado", "CONCRETO-ACHURADO", "concreto armado del colector f'c=210"), ("achurado", "TERRENO-ACHURADO", "cuneta y cerco existentes (arquitectura)"),
                           ("linea", "CUNETA", "cuneta de arquitectura"), ("linea", "JUNTAS", "junta de tecnopor 1\""), ("linea", "AGUA", "nivel de agua"), ("bloque:SIMB-FLECHA", "FLUJO", "sentido del flujo")], 1.8)
    lam.notas(610, 220, "CUADRO DE EMPALMES", ["CUNETA      PROG.       NCF LLEGA   H VENTANA  REGISTRO"] + ["%-10s  %s   %.2f       %.2f       %s" % (c["nombre"].split(" (")[0], prog_txt(c["prog"]), c["NCF_fin"], D["NPT"] - D["e_losa"] - c["NCF_fin"], [r["nombre"] for r in R["registros"] if abs(r["prog"] - c["prog"]) < 1.5][0] if any(abs(r["prog"] - c["prog"]) < 1.5 for r in R["registros"]) else "RS-06*") for c in R["cunetas"]] + ["* cuneta Eje 11: entra al tramo diagonal junto al registro RS-06; cuneta Eje 12: entra a la caja de caida CC."], 1.7)
    return lam


def todas(doc, ox, oy, R, T):
    out = []
    out += dp04(doc, ox, oy, R, T)
    out += dp05(doc, ox + 70, oy, R, T)
    out.append(dp06a(doc, ox + 140, oy, R, T))
    out.append(dp06b(doc, ox + 155, oy, R, T))
    out.append(dp06c(doc, ox + 170, oy, R, T))
    return out
