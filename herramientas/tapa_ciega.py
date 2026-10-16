"""Tapa de registro CIEGA de concreto armado (sin marco ni contramarco metalico) en las planillas del Hogar de Refugio
Temporal (CUI 2675514) y del CAR Varones (CUI 2705619).

Detalle (lamina DP-06B rev. 02): tapa de concreto armado f'c=210 de 0.68 x 0.68 x 0.08 vaciada aparte en obra, parrilla 3/8"
@0.10 en ambos sentidos, 2 asas de fierro liso 1/2" en cajuelas y cantos biselados; se apoya en un rebaje de concreto de
0.70 x 0.70 x 0.08 de la losa (holgura 0.01 por lado) sobre el borde engrosado; luz libre del registro 0.60 x 0.60.
Se eliminan del metrado el contramarco, el marco, los angulos, sus anclajes, la soldadura y la pintura.

Hojas que cambia (edicion directa del XML, conserva formato): COLECTOR PARAMETROS, COLECTOR REGISTROS Y TAPAS,
COLECTOR ACERO, COLECTOR CONCRETO (descuento de la abertura: rebaje 0.70 x 0.08 + luz 0.60 en el resto), COLECTOR INSUMOS,
PLANILLA GENERAL DE METRADOS, RESUMEN; se rehacen ACU TAPA REGISTRO y DESAGREGADO TAPA REGISTRO, y las ACU que tomaban de
ella precios de cemento, arena y agua pasan a sus nuevas filas.
Uso: python3 herramientas/tapa_ciega.py <planilla.xlsx>
"""
import sys, os, re, html
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular
from acu_juntas_refugio import Hoja, encabezado, acu, estilo_amarillo4

CP, RT, CA, CC, CI, PG, RS, AT, DT = ("COLECTOR PARAMETROS", "COLECTOR REGISTROS Y TAPAS", "COLECTOR ACERO", "COLECTOR CONCRETO",
                                      "COLECTOR INSUMOS", "PLANILLA GENERAL DE METRADOS", "RESUMEN", "ACU TAPA REGISTRO",
                                      "DESAGREGADO TAPA REGISTRO")
NOMBRE = "TAPA DE REGISTRO CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08"
q = lambda h, c: "'%s'!%s" % (h, c)


def filas(L, hoja, col="B"):
    """{fila: texto} de las celdas de texto de una columna."""
    out = {}
    for m in re.finditer(r'<c r="%s(\d+)"[^>]*t="s"[^>]*><v>(\d+)</v></c>' % col, L.hoja(hoja)):
        out[int(m.group(1))] = L.txt(int(m.group(2)))
    return out


def buscar(L, hoja, texto, col="B", exacto=False):
    hall = [r for r, t in filas(L, hoja, col).items() if (t == texto if exacto else texto.lower() in t.lower())]
    assert len(hall) == 1, (hoja, texto, hall)
    return hall[0]


def vaciar(L, hoja, ref):
    if L.celda(hoja, ref): L.poner(hoja, ref, "", None)


def cambios(L):
    assert "contramarco" in L.leer(RT, "B%d" % (buscar(L, RT, "METRADO DE LAS PARTIDAS DE REGISTROS", "A") + 2)).lower(), "la planilla ya tiene la tapa ciega"
    # ------------------------------------------------------------------ parametros
    p = {k: buscar(L, CP, t) for k, t in (("n", "Numero de registros de limpieza con tapa"), ("lado", "Lado de la tapa de concreto"),
                                          ("esp", "Espesor de la tapa"), ("ab", "Lado de la abertura en la losa"),
                                          ("pcm", "Perimetro del contramarco"), ("pmt", "Perimetro del marco de tapa"),
                                          ("wcm", "(contramarco)"), ("wmt", "angulo L 1 1/2\"x1 1/2\"x1/8\" (marco de tapa)"),
                                          ("dcm", "del contramarco (4 caras)"), ("dmt", "del marco de tapa (4 caras)"))}
    P = lambda k: "'%s'!$C$%d" % (CP, p[k])
    nuevos = [("ab", "Lado del rebaje de asiento de la tapa en la losa (0.70 x 0.70 x 0.08)", 0.70, "m", "Lamina DP-06B rev. 02 (tapa ciega)"),
              ("pcm", "Luz libre del registro bajo el rebaje (0.60 x 0.60)", 0.60, "m", "Lamina DP-06B rev. 02"),
              ("pmt", "Perimetro del encofrado lateral de la tapa (4 x 0.68)", 2.72, "m", "Lamina DP-06B rev. 02"),
              ("wcm", "Asas de izaje por tapa (fierro liso 1/2\" en cajuelas)", 2, "und", "Lamina DP-06B rev. 02"),
              ("wmt", "Desarrollo de cada asa de fierro liso 1/2\"", 0.50, "m", "Lamina DP-06B rev. 02: agarre 0.15 + 2 patas de 0.11 con gancho de 0.065"),
              ("dcm", "Holgura entre la tapa y el rebaje (cada lado)", 0.01, "m", "Lamina DP-06B rev. 02"),
              ("dmt", "Bisel de los cantos superiores de la tapa", 0.01, "m", "Lamina DP-06B rev. 02")]
    for k, t, v, u, s in nuevos:
        r = p[k]; L.texto(CP, "B%d" % r, t); L.num(CP, "C%d" % r, v); L.texto(CP, "D%d" % r, u); L.texto(CP, "E%d" % r, s)
    L.texto(CP, "E%d" % p["lado"], "Lamina DP-06B rev. 02 (tapa ciega de concreto armado)")
    L.texto(CP, "E%d" % p["esp"], "Lamina DP-06B rev. 02 (= profundidad del rebaje)")
    # ------------------------------------------------------------------ acero de registros y tapas
    a = {k: buscar(L, CA, t) for k, t in (("borde", "Refuerzo de borde de la abertura"), ("parr", "Parrilla de la tapa de concreto"),
                                          ("asas", "Asas de la tapa"), ("anc", "Anclajes del contramarco"))}
    w12 = re.search(r"<f[^>]*>(.*?)</f>", L.celda(CA, "I%d" % a["borde"]).group(0)).group(1)
    r = a["asas"]
    L.texto(CA, "B%d" % r, "Asas de izaje de la tapa (en cajuelas)"); L.texto(CA, "C%d" % r, '1/2" liso'); L.texto(CA, "D%d" % r, "U")
    L.formula(CA, "E%d" % r, P("wcm")); L.formula(CA, "G%d" % r, P("wmt")); L.formula(CA, "I%d" % r, html.unescape(w12))
    L.texto(CA, "V%d" % r, 'DP-06B rev. 02: 2 asas de fierro liso 1/2" por tapa, desarrollo 0.50')
    for c in "ABCDEFGHIUV":
        vaciar(L, CA, "%s%d" % (c, a["anc"]))
    L.texto(CA, "V%d" % a["parr"], 'DP-06B rev. 02: 7 + 7 barras de 3/8" @0.10, L = 0.62')
    fila_res = buscar(L, CA, "ACERO DE REFUERZO EN TAPAS, BORDES Y ANCLAJES")
    L.texto(CA, "B%d" % fila_res, "ACERO DE REFUERZO EN TAPAS, BORDES Y ASAS")
    # ------------------------------------------------------------------ concreto: descuento de la abertura (rebaje + luz)
    for r_, t in filas(L, CC).items():
        if "descuento" in t.lower() and "abertura" in t.lower():
            L.texto(CC, "B%d" % r_, t.replace("descuento de la abertura", "descuento del rebaje y de la abertura")
                                     .replace("descuento aberturas de registro", "descuento de rebajes y aberturas de registro"))
            L.texto(CC, "C%d" % r_, "rebaje 0.70 x 0.70 x 0.08 + luz 0.60 x 0.60 en el resto (e equivalente)")
            e = re.search(r"<f[^>]*>(.*?)</f>", L.celda(CC, "F%d" % r_).group(0)).group(1)
            L.formula(CC, "F%d" % r_, "%s+(%s-%s)*(%s/%s)^2" % (P("esp"), html.unescape(e), P("esp"), P("pcm"), P("ab")))
    # ------------------------------------------------------------------ registros y tapas: componentes de la partida
    tot = buscar(L, RT, "TOTAL DE REGISTROS CON TAPA", "A"); E = "E%d" % tot
    r0 = buscar(L, RT, "METRADO DE LAS PARTIDAS DE REGISTROS", "A") + 2
    comp = [
        (NOMBRE + " (vaciada aparte en obra)", "und", "1 por registro", "=" + E, "DP-06B rev. 02"),
        ("ENCOFRADO LATERAL DE LA TAPA (molde de madera)", "m2", "registros x 4 x 0.68 x 0.08", "=%s*%s*%s" % (E, P("pmt"), P("esp")), "DP-06B rev. 02"),
        ('ACERO EN TAPAS: PARRILLA 3/8" Y ASAS 1/2" LISO', "kg", "hoja COLECTOR ACERO", "=%s+%s" % (q(CA, "U%d" % a["parr"]), q(CA, "U%d" % a["asas"])), "DP-06B rev. 02; COLECTOR ACERO"),
        ("CONCRETO f'c=210 EN TAPAS", "m3", "registros x 0.68 x 0.68 x 0.08", "=%s*%s*%s*%s" % (E, P("lado"), P("lado"), P("esp")), "DP-06B rev. 02"),
        ("ASIENTO DE LA TAPA: REBAJE DE CONCRETO 0.70 x 0.70 x 0.08 EN LA LOSA", "und", "1 por registro (concreto incluido en la losa)", "=" + E, "DP-06B rev. 02; COLECTOR CONCRETO"),
        ("COLOCACION DE LA TAPA EN EL REBAJE (izaje con las asas)", "und", "1 por registro", "=" + E, "DP-06B rev. 02"),
    ]
    for i, (t, u, cal, f, s) in enumerate(comp):
        rr = r0 + i
        L.texto(RT, "B%d" % rr, t); L.texto(RT, "C%d" % rr, u); L.texto(RT, "D%d" % rr, cal); L.formula(RT, "E%d" % rr, f[1:]); L.texto(RT, "F%d" % rr, s)
    L.texto(RT, "A7", "Lamina DP-01 (ubicacion) y DP-06B rev. 02 (detalle): tapa ciega de concreto armado 0.68 x 0.68 x 0.08, vaciada aparte en obra, "
                      "con 2 asas de fierro liso 1/2\", apoyada en un rebaje de concreto de 0.70 x 0.70 x 0.08 de la losa (luz libre 0.60 x 0.60). "
                      "Sin marco ni contramarco metalico.")
    R = {k: "E%d" % (r0 + i) for i, k in enumerate(("tapa", "enc", "acero", "conc", "asiento", "coloc"))}
    # ------------------------------------------------------------------ insumos: bloques de angulos y pintura
    b1 = buscar(L, CI, "01.04.04.05.01 TAPA DE REGISTRO: angulos"); b2 = buscar(L, CI, "01.04.04.05.01 TAPA DE REGISTRO: pintura")
    L.texto(CI, "B%d" % b1, "01.04.04.05.01 TAPA DE REGISTRO: encofrado lateral de la tapa (molde de madera, 6 usos)"); L.texto(CI, "C%d" % b1, "m2")
    L.formula(CI, "D%d" % b1, q(RT, R["enc"]))
    for i, (ins, u, k) in enumerate((("Madera tornillo", "p2", 4.24 / 6), ("Clavos 3\"", "kg", 0.20 / 6), ("Operario", "hh", 0.8), ("Oficial", "hh", 0.8))):
        rr = b1 + i; L.texto(CI, "E%d" % rr, ins); L.texto(CI, "F%d" % rr, u); L.num(CI, "G%d" % rr, round(k, 4)); L.formula(CI, "H%d" % rr, "G%d*$D$%d" % (rr, b1))
    L.texto(CI, "B%d" % b2, "01.04.04.05.01 TAPA DE REGISTRO: colocacion de la tapa en el rebaje y curado"); L.texto(CI, "C%d" % b2, "und")
    L.formula(CI, "D%d" % b2, q(RT, R["coloc"]))
    for i, (ins, u, k) in enumerate((("Operario", "hh", 1.0), ("Peon", "hh", 1.0), ("Agua", "m3", 0.01))):
        rr = b2 + i; L.texto(CI, "E%d" % rr, ins); L.texto(CI, "F%d" % rr, u); L.num(CI, "G%d" % rr, k); L.formula(CI, "H%d" % rr, "G%d*$D$%d" % (rr, b2))
    for rr in range(b2 + 3, b2 + 5):
        for c in "ABCDEFGH":
            vaciar(L, CI, "%s%d" % (c, rr))
    # ------------------------------------------------------------------ planilla general y resumen
    pg = buscar(L, PG, "01.04.04.05.01", "A", exacto=True)
    L.texto(PG, "B%d" % pg, NOMBRE)
    fp = filas(L, PG)
    rc = [r_ for r_, t in fp.items() if pg < r_ < pg + 8 and t.startswith("Cada tapa incluye")]
    assert len(rc) == 1, rc
    L.texto(PG, "B%d" % rc[0], "Cada tapa: concreto armado f'c=210 de 0.68 x 0.68 x 0.08 vaciado aparte en obra, parrilla 3/8\" @0.10, 2 asas de fierro liso 1/2\", "
                               "asiento en rebaje de concreto 0.70 x 0.70 x 0.08 de la losa (luz libre 0.60 x 0.60) y refuerzo de borde 4 x 2 barras de 1/2\". "
                               "Sin marco ni contramarco metalico.")
    rt_ = rc[0] + 1
    assert "Totales para" in (re.search(r"<f[^>]*>(.*?)</f>", L.celda(PG, "B%d" % rt_).group(0)) or [None, ""])[1], "fila de totales"
    L.formula(PG, "B%d" % rt_, '"Totales para "&K%d&" tapas: concreto "&TEXT(%s,"0.000")&" m3; acero de tapas y asas "&TEXT(%s,"0.00")&" kg; encofrado "&TEXT(%s,"0.00")&" m2"'
              % (pg, q(RT, R["conc"]), q(RT, R["acero"]), q(RT, R["enc"])))
    L.x[PG] = re.sub(r'(<c r="B%d" s="\d+") t="n"' % rt_, r'\1 t="str"', L.x[PG])
    rr = [r_ for r_, t in filas(L, RS).items() if "TAPA DE REGISTRO 0.68x0.68" in t]
    for r_ in rr: L.texto(RS, "B%d" % r_, NOMBRE)
    return p, a, R, tot, r0


def precios_actuales(L):
    """Precios sin IGV y fuentes vigentes de la ACU TAPA REGISTRO, por insumo."""
    out = {}
    for r_, t in filas(L, AT).items():
        if r_ < 60: continue
        m = L.celda(AT, "F%d" % r_)
        v = re.search(r"<v>(.*?)</v>", m.group(0)) if m else None
        f = re.search(r"<f[^>]*>(.*?)</f>", m.group(0)) if m else None
        h = L.leer(AT, "H%d" % r_) if L.celda(AT, "H%d" % r_) else ""
        out[t] = (("=" + html.unescape(f.group(1))) if f else float(v.group(1)) if v else None, h)
    return out


def acu_tapa(L, Y4, p, a, R, tot, plantilla, pre):
    P = lambda k: "'%s'!$C$%d" % (CP, p[k])
    H = Hoja(L, Y4)
    encabezado(H, "ANALISIS DE COSTO UNITARIO - " + NOMBRE,
               "Partida de Delphin 01.04.04.06.05.01 %s (metrado 01.04.04.05.01, hojas COLECTOR REGISTROS Y TAPAS y COLECTOR ACERO). Tapa ciega de concreto "
               "armado vaciada aparte en obra sobre tablero, con parrilla 3/8\" @0.10, 2 asas de fierro liso 1/2\" en cajuelas y cantos biselados; se coloca en el "
               "rebaje de concreto de 0.70 x 0.70 x 0.08 de la losa (el rebaje y el borde engrosado se metran con el concreto del colector). Incluye el refuerzo "
               "de borde de la abertura (2 barras de 1/2\" por lado). Sin marco ni contramarco metalico. Celda amarilla = dato; verde = formula. Precios sin IGV." % NOMBRE,
               plantilla)
    H.banda("1. CANTIDADES POR TAPA (hojas COLECTOR PARAMETROS, COLECTOR REGISTROS Y TAPAS y COLECTOR ACERO)", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "CONCEPTO", "UND", "VALOR", None, None, None, "SUSTENTO"))], 31.5)
    datos = [("n", "Numero de tapas (registros)", "und", "=" + q(RT, "E%d" % tot), "COLECTOR REGISTROS Y TAPAS"),
             ("conc", "Concreto f'c=210 por tapa: 0.68 x 0.68 x 0.08", "m3", "=%s^2*%s" % (P("lado"), P("esp")), "DP-06B rev. 02"),
             ("enc", "Encofrado lateral por tapa: 4 x 0.68 x 0.08 (molde de madera)", "m2", "=%s*%s" % (P("pmt"), P("esp")), "DP-06B rev. 02"),
             ("tab", "Tablero de vaciado: 0.80 x 0.80 x 1\" = 6.89 p2 en 6 usos", "p2", 1.15, "criterio de obra"),
             ("parr", "Acero 3/8\" de la parrilla por tapa (7 + 7 barras, L = 0.62)", "kg", "=%s/%s" % (q(CA, "U%d" % a["parr"]), q(CA, "F%d" % a["parr"])), "COLECTOR ACERO"),
             ("borde", "Acero 1/2\" de borde de la abertura por registro (8 barras, L = 1.40)", "kg", "=%s/%s" % (q(CA, "U%d" % a["borde"]), q(CA, "F%d" % a["borde"])), "COLECTOR ACERO"),
             ("asas", "Fierro liso 1/2\" de las 2 asas por tapa (desarrollo 0.50 c/u)", "kg", "=%s/%s" % (q(CA, "U%d" % a["asas"]), q(CA, "F%d" % a["asas"])), "COLECTOR ACERO"),
             ("des", "Desperdicio de acero", "-", 0.05, "criterio"),
             ("rc", "Cemento por m3 de concreto f'c=210", "bol/m3", "=" + q(CI, "G10"), "COLECTOR INSUMOS (diseno de mezcla)"),
             ("ra", "Arena gruesa por m3", "m3/m3", "=" + q(CI, "G11"), "COLECTOR INSUMOS"),
             ("rp", "Piedra chancada 1/2\" por m3", "m3/m3", "=" + q(CI, "G12"), "COLECTOR INSUMOS"),
             ("rw", "Agua por m3 (mezcla) + curado de la tapa (0.01 m3)", "m3/m3", "=" + q(CI, "G13"), "COLECTOR INSUMOS"),
             ("hc", "Mano de obra del concreto: operario / oficial / peon por m3", "hh/m3", "=" + q(CI, "G16"), "COLECTOR INSUMOS (0.8 / 0.8 / 6.4)"),
             ("hpc", "Peon por m3 de concreto", "hh/m3", "=" + q(CI, "G18"), "COLECTOR INSUMOS"),
             ("ha", "Mano de obra del acero: operario / oficial por kg", "hh/kg", "=" + q(CI, "G44"), "COLECTOR INSUMOS"),
             ("he", "Mano de obra del encofrado: operario / oficial por m2", "hh/m2", 0.8, "COLECTOR INSUMOS (encofrado)"),
             ("hco", "Colocacion de la tapa en el rebaje: operario + peon", "hh/und", 1.0, "criterio de obra: 1 hh por tapa"),
             ]
    D = {}
    for n, (k, t, u, v, s) in enumerate(datos, 1):
        st = 306 if isinstance(v, str) else Y4
        r_ = H.fila([("A", 283, n), ("B", 149, t), ("C", 285, u), ("D", st, v), ("E", 295, None), ("F", 295, None), ("G", 295, None), ("H", 149, s)], 31.5)
        D[k] = "$D$%d" % r_
    ac = "(%s+%s+%s)" % (D["parr"], D["borde"], D["asas"])
    HH = lambda c: "='COSTO HORA HOMBRE 2026'!$G$%d" % {"Operario": 11, "Oficial": 12, "Peon": 13}[c]
    FH = "hoja COSTO HORA HOMBRE 2026 (tabla oficial CAPECO - FTCCP 2026)"
    pr = lambda ins: pre[ins][0]
    fu = lambda ins: pre[ins][1]
    mo = [("Operario", "hh", "=%s*%s+%s*%s+%s*%s+%s" % (D["conc"], D["hc"], ac, D["ha"], D["enc"], D["he"], D["hco"]), HH("Operario"), FH),
          ("Oficial", "hh", "=%s*%s+%s*%s+%s*%s" % (D["conc"], D["hc"], ac, D["ha"], D["enc"], D["he"]), HH("Oficial"), FH),
          ("Peon", "hh", "=%s*%s+%s" % (D["conc"], D["hpc"], D["hco"]), HH("Peon"), FH)]
    mat = [("Cemento Portland tipo I", "bol", "=%s*%s" % (D["conc"], D["rc"]), pr("Cemento Portland tipo I"), fu("Cemento Portland tipo I")),
           ("Arena gruesa", "m3", "=%s*%s" % (D["conc"], D["ra"]), pr("Arena gruesa"), fu("Arena gruesa")),
           ('Piedra chancada 1/2"', "m3", "=%s*%s" % (D["conc"], D["rp"]), pr('Piedra chancada 1/2"'), fu('Piedra chancada 1/2"')),
           ("Agua", "m3", "=%s*%s+0.01" % (D["conc"], D["rw"]), pr("Agua"), fu("Agua")),
           ("Madera tornillo", "p2", "=%s*4.24/6+%s" % (D["enc"], D["tab"]), pr("Madera tornillo"), fu("Madera tornillo")),
           ("Acero corrugado fy=4200", "kg", "=(%s+%s)*(1+%s)" % (D["parr"], D["borde"], D["des"]), pr("Acero corrugado fy=4200"), fu("Acero corrugado fy=4200")),
           ('Fierro liso 1/2" (asas)', "kg", "=%s*(1+%s)" % (D["asas"], D["des"]), pr("Acero corrugado fy=4200"),
            "mismo precio por kg del acero corrugado (referencial): " + fu("Acero corrugado fy=4200")),
           ("Alambre negro N 16", "kg", "=%s*0.06" % ac, pr("Alambre negro N 16"), fu("Alambre negro N 16"))]
    acu(H, "01.04.04.06.05.01 " + NOMBRE, "01.04.04.05.01 (hoja COLECTOR REGISTROS Y TAPAS)", "und", "=" + q(RT, R["tapa"]), mo, mat,
        "und/dia, cuadrilla de 1 operario", por="TAPA",
        herr="3 % del costo de mano de obra (incluye mezcla y vibrado manual del concreto de la tapa)")
    L.F[L.ruta[AT]] = H.xml(plantilla).encode(); L.x.pop(AT, None)
    return D


def desagregado(L, Y4, p, a, R, tot, r0reg, plantilla_dt):
    P = lambda k: "'%s'!$C$%d" % (CP, p[k])
    H = Hoja(L, Y4)
    encabezado(H, "DESAGREGADO DE LA PARTIDA 01.04.04.05.01 - " + NOMBRE,
               "La partida se mide por unidad de registro. Cada tapa ciega de concreto armado se vacia aparte en obra y se coloca en el rebaje de 0.70 x 0.70 x 0.08 "
               "de la losa (luz libre 0.60 x 0.60). Sin marco ni contramarco metalico. Componentes tomados de las hojas COLECTOR REGISTROS Y TAPAS y COLECTOR ACERO.",
               plantilla_dt)
    H.banda("A. UBICACION DE LOS REGISTROS", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "REGISTRO", "PROGRESIVA", "UBICACION", None, "CANT. (und)", "SUSTENTO", None))], 31.5)
    hdr = [r_ for r_, t in filas(L, RT).items() if t == "REGISTRO" and r_ < tot][0]
    ra = H.r + 1
    for i, r_ in enumerate(range(hdr + 1, tot), 1):
        H.fila([("A", 283, i), ("B", 295, "=+" + q(RT, "B%d" % r_)), ("C", 295, "=+" + q(RT, "C%d" % r_)), ("D", 149, "=+" + q(RT, "D%d" % r_)),
                ("E", 295, None), ("F", 290, "=+" + q(RT, "E%d" % r_)), ("G", 149, "=+" + q(RT, "F%d" % r_)), ("H", 295, None)])
    rn = H.fila([("A", 21, None), ("B", 294, "TOTAL DE REGISTROS (und de la partida)"), ("C", 295, None), ("D", 295, None), ("E", 295, None),
                 ("F", 296, "=SUM(F%d:F%d)" % (ra, H.r)), ("G", 295, None), ("H", 295, None)])
    H.banda("B. COMPONENTES DE UNA TAPA DE REGISTRO Y TOTAL DE LA PARTIDA", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "COMPONENTE", "UND", "POR REGISTRO", "N° REGISTROS", "TOTAL", "SUSTENTO", None))], 31.5)
    sub = {}
    def grupo(titulo, items, clave):
        H.banda(titulo, desde="B"); g0 = H.r + 1
        for n, (t, u, v, s) in items:
            r_ = H.r + 1
            H.fila([("A", 283, n), ("B", 149, t), ("C", 285, u), ("D", 306, v), ("E", 290, "=+$F$%d" % rn), ("F", 290, "=D%d*E%d" % (r_, r_)), ("G", 149, s), ("H", 295, None)], 31.5)
        sub[clave] = H.fila([("A", 21, None), ("B", 294, "Subtotal " + titulo.lower()), ("C", 285, items[0][1][1]), ("D", 290, "=SUM(D%d:D%d)" % (g0, H.r)),
                             ("E", 295, None), ("F", 296, "=SUM(F%d:F%d)" % (g0, H.r)), ("G", 295, None), ("H", 295, None)])
    grupo("CONCRETO", [(1, ("Tapa ciega de concreto f'c=210: 0.68 x 0.68 x 0.08", "m3", "=%s^2*%s" % (P("lado"), P("esp")), "lamina DP-06B rev. 02"))], "conc")
    grupo("ENCOFRADO", [(2, ("Encofrado lateral de la tapa: 4 x 0.68 x 0.08 (molde de madera)", "m2", "=%s*%s" % (P("pmt"), P("esp")), "lamina DP-06B rev. 02"))], "enc")
    grupo("ACERO DE REFUERZO", [
        (3, ('Parrilla de la tapa: 7 + 7 barras 3/8" @0.10, L = 0.62', "kg", "=%s/%s" % (q(CA, "U%d" % a["parr"]), q(CA, "F%d" % a["parr"])), "COLECTOR ACERO fila %d" % a["parr"])),
        (4, ('Asas de izaje: 2 barras de fierro liso 1/2", desarrollo 0.50', "kg", "=%s/%s" % (q(CA, "U%d" % a["asas"]), q(CA, "F%d" % a["asas"])), "COLECTOR ACERO fila %d" % a["asas"])),
        (5, ('Refuerzo de borde de la abertura: 8 barras 1/2", L = 1.40', "kg", "=%s/%s" % (q(CA, "U%d" % a["borde"]), q(CA, "F%d" % a["borde"])), "COLECTOR ACERO fila %d" % a["borde"]))], "acero")
    H.banda("C. CONTROL CON EL METRADO DE LOS COMPONENTES (hojas del colector)", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", (None, "COMPONENTE", "UND", None, "ESTA HOJA", "HOJA DEL COLECTOR", "CONTROL", None))], 31.5)
    for t, u, aqui, alla in (("Concreto en tapas", "m3", "F%d" % sub["conc"], q(RT, R["conc"])),
                             ("Encofrado lateral de tapas", "m2", "F%d" % sub["enc"], q(RT, R["enc"])),
                             ("Acero en tapas, asas y bordes", "kg", "F%d" % sub["acero"], "%s+%s" % (q(CA, "U%d" % a["borde"]), q(RT, R["acero"])))):
        r_ = H.r + 1
        H.fila([("A", 21, None), ("B", 149, t), ("C", 285, u), ("D", 295, None), ("E", 290, "=+" + aqui), ("F", 290, "=" + alla),
                ("G", 295, '=IF(ABS(E%d-F%d)<0.0005,"CONFORME","REVISAR")' % (r_, r_)), ("H", 295, None)])
    H.banda("No hay angulos, soldadura ni pintura: la tapa es ciega de concreto armado (lamina DP-06B rev. 02). El rebaje de asiento y el borde engrosado "
            "de la abertura se metran con el concreto de la losa del colector (hoja COLECTOR CONCRETO).", 281, 33, salto=1)
    L.F[L.ruta[DT]] = H.xml(plantilla_dt).encode(); L.x.pop(DT, None)


def construir(f):
    L = Libro(f)
    plantilla = L.hoja(AT); plantilla_dt = L.hoja(DT)
    pre = precios_actuales(L)
    viejas = {r_: t for r_, t in filas(L, AT).items() if r_ > 60}
    Y4 = estilo_amarillo4(L)
    p, a, R, tot, r0 = cambios(L)
    acu_tapa(L, Y4, p, a, R, tot, plantilla, pre)
    desagregado(L, Y4, p, a, R, tot, r0, plantilla_dt)
    # otras ACU que leian precios de la ACU TAPA REGISTRO: se apuntan a la fila nueva del mismo insumo
    nuevas = {}
    for m in re.finditer(r'<c r="B(\d+)"[^>]*t="s"[^>]*><v>(\d+)</v></c>', L.F[L.ruta[AT]].decode()):
        nuevas.setdefault(L.txt(int(m.group(2))), int(m.group(1)))
    nuevas = {t: r_ for t, r_ in nuevas.items() if r_ > 40}
    for hoja in list(L.ruta):
        if hoja in (AT, DT): continue
        x = L.hoja(hoja)
        def rep(m):
            fila = int(m.group(2)); ins = viejas.get(fila)
            assert ins in nuevas, (hoja, fila, ins)
            return "%sF%d" % (m.group(1), nuevas[ins])
        y = re.sub(r"(&apos;ACU TAPA REGISTRO&apos;!\$?|'ACU TAPA REGISTRO'!\$?)F\$?(\d+)", rep, x)
        if y != x: L.x[hoja] = y
    L.guardar(f)
    return recalcular(f, list(L.ruta))


if __name__ == "__main__":
    print("celdas recalculadas:", construir(sys.argv[1]))
