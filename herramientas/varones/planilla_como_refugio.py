"""CAR Varones (Katiuska, CUI 2705619): la planilla de metrados toma los NOMBRES y la ESTRUCTURA de partidas del Hogar de
Refugio Temporal (CUI 2675514, estructura Delphin), con las CANTIDADES propias de Varones. Parte A (esta funcion `parte_a`):

1. Nombres de partidas iguales a los del Refugio (RESUMEN y PLANILLA GENERAL); unidad m en rejilla y junta de cunetas.
2. Concreto del colector en una sola partida 01.04.04.04.01 CONCRETO f'c=210 kg/cm2 PARA COLECTOR (losa de fondo + muros +
   losa superior); encofrado, acero, acabado (VEREDA) y curado pasan a .02 a .05.
3. Registros: las 7 partidas de componentes pasan a 01.04.04.05.01 TAPA DE REGISTRO 0.68x0.68 C/MARCO Y CONTRAMARCO (und).
4. Contramarco L 1 1/2"x1 1/2"x1/8" (antes L 2"x2"x3/16"), como en el Refugio: cambia el peso de angulos de la tapa.
5. Juntas del colector con sellador asfaltico 1" x 2" (RC-250 + arena). A ambos lados del colector hay terreno natural: la
   partida 01.04.04.06.02 queda solo con el contacto del colector con la caja CL.
6. Junta de dilatacion de cunetas (01.04.03.04.03.03) en toda la seccion en U (2 muros + fondo), EG-2013 MTC Seccion 510.
7. COLECTOR INSUMOS con el mismo orden de filas que el Refugio (lija y thinner por separado; juntas con sellador asfaltico).
La parte B (hojas de ACU, desagregados y costo de la hora-hombre) esta en portar_hojas_v.py.
Edicion directa del XML (conserva formato, logos y formulas). Uso: python3 herramientas/varones/planilla_como_refugio.py <planilla.xlsx>
"""
import sys, os, re, html
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); sys.path.insert(0, HERR)
from angulo_contramarco_refugio import Libro, recalcular

RS, PG = "RESUMEN", "PLANILLA GENERAL DE METRADOS"
CP, RT, CJ, CI, CA = "COLECTOR PARAMETROS", "COLECTOR REGISTROS Y TAPAS", "COLECTOR JUNTAS Y EMPALMES", "COLECTOR INSUMOS", "COLECTOR ACERO"
MJ = "METRADO JUNTA DE DILATACION"
L15 = 'L 1 1/2"x1 1/2"x1/8"'; L2 = 'L 2"x2"x3/16"'

# ------------------------------------------------------------------ nombres (codigo: nombre del Refugio)
NOMBRES = {
    "01.04.03.02.04": "RELLENO COMPACTADO C/MATERIAL PROPIO SELECCIONADO",
    "01.04.03.02.05": "ELIMINACIÓN DE MATERIAL EXCEDENTE D<1Km",
    "01.04.03.04.02.01": "CONCRETO f'c=175 kg/cm2 PARA CUNETAS",
    "01.04.03.04.02.02": "ENCOFRADO Y DESENCOFRADO DE CUNETAS",
    "01.04.03.04.03.01": "REJILLA METALICA P/CUNETA C/PL 1''x 3/16'' Y ANGULO 1'' x 1'' x 3/16'', S/DETALLE",
    "01.04.03.05.01.01": "MONTANTE CON TUBERÍA PVC DE 4\"",
    "01.04.03.05.02.01": "TUBERIA DESAGÜE PVC-CP Ø4\"",
    "01.04.03.05.02.03": "CODO DESAGÜE PVC Ø4\" x 90°",
    "01.04.03.05.02.04": "TEE SANITARIA DESAGÜE PVC Ø4\"",
    "01.04.04.02.01": "EXCAVACIÓN MANUAL DE ZANJAS P/COLECTOR",
    "01.04.04.02.03": "RELLENO COMPACTADO C/MATERIAL PROPIO SELECCIONADO",
    "01.04.04.02.04": "ELIMINACIÓN DE MATERIAL EXCEDENTE D<1Km",
    "01.04.04.03.01": "CONCRETO f'c=100 kg/cm2 PARA SOLADO E=2''",
}
UNIDAD_M = ("01.04.03.04.03.01", "01.04.03.04.03.03")
COLECTOR = [  # (codigo nuevo, nombre, fila de la PLANILLA)
    ("01.04.04.04.01", "CONCRETO f'c=210 kg/cm2 PARA COLECTOR", 176),
    ("01.04.04.04.02", "ENCOFRADO Y DESENCOFRADO DE COLECTOR", 190),
    ("01.04.04.04.03", "ACERO f'y=4200 kg/cm2 PARA COLECTOR", 194),
    ("01.04.04.04.04", "ACABADO FROTACHADO DE LOSA SUPERIOR (VEREDA)", 198),
    ("01.04.04.04.05", "CURADO DE CONCRETO EN COLECTOR", 202),
    ("01.04.04.05.01", "TAPA DE REGISTRO 0.68x0.68 C/MARCO Y CONTRAMARCO", 207),
    ("01.04.04.06", "JUNTAS", 214),
    ("01.04.04.06.01", "JUNTA DE DILATACION E=1\" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR", 215),
    ("01.04.04.06.02", "JUNTA E=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CAJA CL", 216),
]


# ------------------------------------------------------------------ utilidades sobre el XML
def vaciar(L, nom, ref):
    x = L.hoja(nom); m = L.celda(nom, ref); assert m, (nom, ref)
    s = re.search(r' s="(\d+)"', m.group(0)); s = ' s="%s"' % s.group(1) if s else ""
    L.x[nom] = x[:m.start()] + '<c r="%s"%s/>' % (ref, s) + x[m.end():]


def estilo(L, nom, ref):
    m = L.celda(nom, ref); s = re.search(r' s="(\d+)"', m.group(0)) if m else None
    return s.group(1) if s else None


def poner_estilo(L, nom, ref, st):
    x = L.hoja(nom); m = L.celda(nom, ref); assert m, (nom, ref)
    c = re.sub(r' s="\d+"', "", m.group(0), count=1)
    c = c.replace('<c r="%s"' % ref, '<c r="%s" s="%s"' % (ref, st), 1)
    L.x[nom] = x[:m.start()] + c + x[m.end():]


def estilo_fila(L, nom, origen, destino, cols):
    for c in cols:
        st = estilo(L, nom, "%s%d" % (c, origen))
        if st is not None and L.celda(nom, "%s%d" % (c, destino)): poner_estilo(L, nom, "%s%d" % (c, destino), st)


def fila_de(L, nom, col, valor, desde=1, hasta=400):
    for r in range(desde, hasta + 1):
        m = L.celda(nom, "%s%d" % (col, r))
        if m and L.leer(nom, "%s%d" % (col, r)) == valor: return r
    raise KeyError((nom, col, valor))


def formula_txt(L, nom, ref, f):
    """Formula de texto (t="str")."""
    x = L.hoja(nom); m = L.celda(nom, ref); assert m, (nom, ref)
    s = re.search(r' s="(\d+)"', m.group(0)); s = ' s="%s"' % s.group(1) if s else ""
    L.x[nom] = x[:m.start()] + '<c r="%s"%s t="str"><f aca="false">%s</f><v></v></c>' % (ref, s, html.escape(f, quote=False)) + x[m.end():]


def borrar_filas_resumen(L, filas):
    """Quita filas del RESUMEN y sube las de abajo (el RESUMEN solo tiene formulas hacia la PLANILLA)."""
    x = L.hoja(RS); filas = sorted(filas)
    x = re.sub(r'<row r="(\d+)"[^>]*>.*?</row>', lambda m: "" if int(m.group(1)) in filas else m.group(0), x, flags=re.S)
    def nueva(r): return r - sum(1 for f in filas if f < r)
    def rowfix(m):
        r = int(m.group(1)); body = m.group(0); n = nueva(r)
        if n == r: return body
        body = re.sub(r'<row r="%d"' % r, '<row r="%d"' % n, body)
        return re.sub(r'(<c r="[A-Z]+)%d"' % r, lambda k: '%s%d"' % (k.group(1), n), body)
    x = re.sub(r'<row r="(\d+)"[^>]*>.*?</row>', rowfix, x, flags=re.S)
    x = re.sub(r'<dimension ref="A1:([A-Z]+)(\d+)"/>', lambda m: '<dimension ref="A1:%s%d"/>' % (m.group(1), nueva(int(m.group(2)))), x)
    L.x[RS] = x


# ------------------------------------------------------------------ parte A
def parte_a(f):
    L = Libro(f)
    assert L.leer(RS, "B66") == "CONCRETO f'c=210 kg/cm2 EN MUROS", "la planilla ya fue modificada"
    # 1. nombres en RESUMEN y PLANILLA
    for nom, ccol, dcol, ucol in ((RS, "A", "B", "C"), (PG, "A", "B", "L")):
        for cod, txt in NOMBRES.items():
            L.texto(nom, "%s%d" % (dcol, fila_de(L, nom, ccol, cod)), txt)
        for cod in UNIDAD_M:
            L.texto(nom, "%s%d" % (ucol, fila_de(L, nom, ccol, cod)), "m")
    # 2. concreto unificado (PLANILLA): partida 176 con todo el sustento; 180 y 184 quedan como subtitulos
    L.texto(PG, "B176", COLECTOR[0][1]); L.formula(PG, "K176", "SUM(J177:J189)")
    for r, sub in ((180, "Muros:"), (184, "Losa superior (incluye bordes de registro):")):
        vaciar(L, PG, "A%d" % r); L.texto(PG, "B%d" % r, sub); vaciar(L, PG, "K%d" % r); vaciar(L, PG, "L%d" % r)
        estilo_fila(L, PG, 177, r, "AKL")
    for r in (177, 178, 179):
        L.texto(PG, "B%d" % r, "Losa de fondo - " + L.leer(PG, "B%d" % r))
    for cod, txt, r in COLECTOR:
        L.texto(PG, "A%d" % r, cod); L.texto(PG, "B%d" % r, txt)
    # 3. registros: una partida por und con su sustento
    L.formula(PG, "K207", "SUM(J208:J208)"); L.texto(PG, "L207", "und")
    for r in range(208, 214):
        for c in "ACDEFGHIJKL": vaciar(L, PG, "%s%d" % (c, r))
        estilo_fila(L, PG, 177, r, "ABCDEFGHIJKL")
    L.texto(PG, "B208", "Registros en la losa del colector (RV-01 a RV-11)"); L.num(PG, "C208", 1)
    L.formula(PG, "J208", "SUM('%s'!E10:E20)" % RT)
    L.texto(PG, "B209", "Cada tapa incluye: contramarco %s con 8 anclajes, marco %s, tapa de concreto armado 0.68 x 0.68 x 0.08 con parrilla y asas, refuerzo de borde y pintura" % (L15, L15))
    formula_txt(L, PG, "B210", "\"Totales para \"&K207&\" tapas: angulos \"&TEXT('%s'!E27,\"0.00\")&\" kg; concreto \"&TEXT('%s'!E29,\"0.00\")&\" m3; acero \"&TEXT('%s'!I25,\"0.00\")&\" kg; pintura \"&TEXT('%s'!E30,\"0.00\")&\" m2\"" % (RT, RT, CA, RT))
    L.texto(PG, "B211", "Desagregado por componente: ver hoja DESAGREGADO TAPA REGISTRO")
    for r, h in ((207, 31), (208, 31), (209, 46.5), (210, 46.5), (211, 15.5)):
        x = L.hoja(PG); m = re.search(r'<row r="%d"[^>]*>' % r, x); t = m.group(0)
        t2 = re.sub(r' ht="[\d.]+"', ' ht="%s"' % h, t) if ' ht="' in t else t.replace('<row r="%d"' % r, '<row r="%d" ht="%s"' % (r, h))
        t2 = t2 if 'customHeight="true"' in t2 else t2.replace('customHeight="false"', 'customHeight="true"') if 'customHeight=' in t2 else t2.replace('<row ', '<row customHeight="true" ', 1)
        L.x[PG] = x[:m.start()] + t2 + x[m.end():]
    # 5. juntas del colector
    L.formula(PG, "K216", "+'%s'!F17" % CJ)
    # RESUMEN: codigos y nombres; se quitan muros, losa superior y los 6 componentes de la tapa
    for cod, txt, r in COLECTOR:
        rr = {176: 65, 190: 68, 194: 69, 198: 70, 202: 71, 207: 73, 214: 80, 215: 81, 216: 82}[r]
        L.texto(RS, "A%d" % rr, cod); L.texto(RS, "B%d" % rr, txt)
        if r != 214: L.formula(RS, "D%d" % rr, "+'%s'!K%d" % (PG, r))
    borrar_filas_resumen(L, [66, 67, 74, 75, 76, 77, 78, 79])
    # 4. contramarco L 1 1/2"x1 1/2"x1/8"
    L.texto(CP, "B34", "Perimetro del contramarco %s (4 x 0.70)" % L15)
    L.texto(CP, "B36", "Peso del angulo %s (contramarco)" % L15); L.num(CP, "C36", 1.83)
    L.texto(CP, "B37", "Peso del angulo %s (marco de tapa)" % L15)
    L.texto(CP, "B38", "Desarrollo pintado del angulo 1 1/2\"x1 1/2\" del contramarco (4 caras)"); L.num(CP, "C38", 0.152); L.texto(CP, "E38", "4 x 0.0381 m")
    L.texto(CP, "B39", "Desarrollo pintado del angulo 1 1/2\"x1 1/2\" del marco de tapa (4 caras)")
    L.cambiar(RT, "A7", L2, L15); L.cambiar(RT, "B25", L2, L15)
    L.texto(RT, "D27", "registros x (2.80 x 1.83 + 2.72 x 1.83)"); L.texto(RT, "D30", "registros x (2.80 x 0.152 + 2.72 x 0.152)")
    # 5. hoja de juntas del colector: terreno natural a ambos lados; queda la junta con la caja CL
    L.texto(CJ, "A7", "Laminas DP-01, DP-02, DP-06C, DP-07 y DD-03. Junta de dilatacion de 1\" cada 4.00 m en todo el perimetro de la seccion (tecnopor de 1\" en todo el "
                      "perimetro + sellador asfaltico RC-250 con arena de 1\" x 2\" en la cara expuesta, EG-2013 MTC). A ambos lados del colector hay terreno natural (sin piso): "
                      "no lleva junta longitudinal; la losa superior sirve de vereda. Junta de tecnopor de 1\" con sellador asfaltico en el contacto con la caja CL. Empalme de cada "
                      "cuneta por ventana en el muro lado predio con caida libre al fondo (sin dintel adicional).")
    L.texto(CJ, "A10", "JUNTA DE DILATACION e=1\" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR (perimetro = 2 x ancho exterior + 2 x (e fondo + h max + e losa))")
    L.texto(CJ, "A14", "JUNTA e=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CAJA CL (a ambos lados del colector hay terreno natural: no lleva junta longitudinal)")
    L.texto(CJ, "B15", "Bordes de la losa: terreno natural a ambos lados (sin piso): no lleva junta"); L.texto(CJ, "C15", "-"); L.num(CJ, "D15", 0)
    L.texto(CJ, "G15", "DP-04 y DD-03")
    L.texto(CJ, "G16", "DP-07 y DD-03: tecnopor y sellador en todo el contacto colector - CL")
    L.texto(CJ, "A17", "TOTAL JUNTA CON LA CAJA CL (m)")
    # 6. junta de cunetas en toda la seccion en U
    assert L.leer(MJ, "I13") in ("2", "2.0") and L.leer(MJ, "B21") == "EJE 09"
    L.texto(MJ, "A1", "PLANILLA DE METRADOS - JUNTA DE DILATACIÓN E=1\" (0.0254 m) CON SELLADOR ASFÁLTICO EN CUNETAS: TODA LA SECCIÓN (2 MUROS + LOSA DE FONDO)")
    L.texto(MJ, "A10", "Ancho interior del fondo (m)")
    x = L.hoja(MJ); m = L.celda(MJ, "B10"); st = re.search(r' s="(\d+)"', L.celda(MJ, "B9").group(0)).group(1)
    L.x[MJ] = x[:m.start()] + '<c r="B10" s="%s" t="n"><v>0.4</v></c>' % st + x[m.end():]
    L.texto(MJ, "I11", "LONG. POR\nJUNTA (m)\n2 muros + fondo"); L.texto(MJ, "J11", "PARCIAL\n(ml)")
    for r in range(13, 22):
        L.formula(MJ, "I%d" % r, "$B$9*F%d+$B$10" % r); L.formula(MJ, "J%d" % r, "H%d*I%d" % (r, r))
    notas = ["NOTAS:",
             "1. EG-2013 MTC, Seccion 510 (cunetas revestidas de concreto): la junta corta toda la seccion en U, es decir los dos muros y la losa de fondo, para que cada paño de 3.00 m trabaje independiente.",
             "2. Longitud por junta = 2 x altura del muro (area del muro / longitud del eje, hoja CONCRETO EN CUNETAS) + ancho interior del fondo 0.40 m.",
             "3. Junta e = 1\" (0.0254 m): tecnopor de 1\" en todo el espesor y sellador asfaltico (RC-250 + arena) en la cara interior; se mide en metros lineales de junta sellada. Detalle en la lamina DJ-01."]
    x = L.hoja(MJ); assert not re.search(r'<row r="2[3-6]"[ >]', x)
    sa = re.search(r' s="(\d+)"', L.celda(MJ, "A10").group(0)).group(1)
    x = x.replace("</sheetData>", "".join('<row r="%d" customHeight="true" ht="%s"><c r="A%d" s="%s" t="s"><v>%d</v></c></row>' % (23 + i, "15" if i == 0 else "27", 23 + i, sa, L.sid(t))
                                          for i, t in enumerate(notas)) + "</sheetData>")
    x = x.replace("</mergeCells>", "".join('<mergeCell ref="A%d:J%d"/>' % (23 + i, 23 + i) for i in range(len(notas))) + "</mergeCells>")
    x = re.sub(r'<mergeCells count="(\d+)"', lambda m: '<mergeCells count="%d"' % (int(m.group(1)) + len(notas)), x)
    x = re.sub(r'<dimension ref="A1:([A-Z]+)\d+"/>', lambda m: '<dimension ref="A1:%s%d"/>' % (m.group(1), 22 + len(notas)), x)
    L.x[MJ] = x
    # 7. COLECTOR INSUMOS con el orden del Refugio
    for r, txt, d in ((10, "01.04.04.04.01 CONCRETO f'c=210 PARA COLECTOR - losa de fondo", "SUM('%s'!J177:J179)" % PG),
                      (19, "01.04.04.04.01 CONCRETO f'c=210 PARA COLECTOR - muros", "SUM('%s'!J181:J183)" % PG),
                      (28, "01.04.04.04.01 CONCRETO f'c=210 PARA COLECTOR - losa superior", "SUM('%s'!J185:J189)" % PG),
                      (37, "01.04.04.04.02 ENCOFRADO Y DESENCOFRADO DE COLECTOR", "'%s'!K190" % PG),
                      (42, "01.04.04.04.03 ACERO f'y=4200 PARA COLECTOR", "'%s'!K194" % PG),
                      (60, "01.04.04.05.01 TAPA DE REGISTRO: angulos (marco y contramarco)", "'%s'!E27" % RT),
                      (64, "01.04.04.05.01 TAPA DE REGISTRO: pintura en angulos", "'%s'!E30" % RT)):
        L.texto(CI, "B%d" % r, txt); L.formula(CI, "D%d" % r, d)
    L.texto(CI, "E60", "Angulo %s (incluye corte y soldadura)" % L15)
    L.desplazar(CI, 67, 73, 1); L.insertar_copia(CI, 66, 67)
    L.texto(CI, "E66", "Lija para fierro N° 80"); L.texto(CI, "F66", "und"); L.num(CI, "G66", 0.25)
    L.texto(CI, "E67", "Thinner acrilico"); L.texto(CI, "F67", "gal"); L.num(CI, "G67", 0.024); L.formula(CI, "H67", "G67*$D$64")
    L.insertar_copia(CI, 74, 75); L.insertar_copia(CI, 74, 76)
    L.texto(CI, "B69", "01.04.04.06.01 JUNTA DE DILATACION e=1\" CON TECNOPOR Y SELLADOR ASFALTICO")
    L.formula(CI, "G69", "'ACU JUNTA DILATACION'!$D$14*(1+'ACU JUNTA DILATACION'!$D$15)")
    L.texto(CI, "E70", "Sellador asfaltico: asfalto liquido RC-250 + arena gruesa (sello de 1\" x 2\")"); L.texto(CI, "F70", "m3"); L.formula(CI, "G70", "'ACU JUNTA DILATACION'!$D$20")
    L.texto(CI, "B73", "01.04.04.06.02 JUNTA e=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CAJA CL")
    L.formula(CI, "G73", "'ACU JUNTA CAJA CL'!$D$14*(1+'ACU JUNTA CAJA CL'!$D$15)")
    for r, e, u, g in ((74, "Sellador asfaltico: asfalto liquido RC-250 + arena gruesa (sello de 1\" x 2\")", "m3", "'ACU JUNTA CAJA CL'!$D$20"),
                       (75, "Operario", "hh", 0.2), (76, "Peon", "hh", 0.2)):
        L.texto(CI, "E%d" % r, e); L.texto(CI, "F%d" % r, u)
        L.formula(CI, "G%d" % r, g) if isinstance(g, str) else L.num(CI, "G%d" % r, g)
        L.formula(CI, "H%d" % r, "G%d*$D$73" % r)
    L.guardar(f)


if __name__ == "__main__":
    parte_a(sys.argv[1])
    print("parte A lista")
