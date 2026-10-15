"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): hojas ACU JUNTA DILATACION y ACU JUNTA CERCO dentro de la
planilla vigente, con el formato de la ACU TAPA REGISTRO (cantidades por metro + analisis en formato Delphin).

Las cantidades por metro salen de la lamina DD-03 (tecnopor de 1" y sellador asfaltico 1" x 2" de RC-250 + arena) y de la hoja
COLECTOR JUNTAS Y EMPALMES; la hoja COLECTOR INSUMOS pasa a leer de estas ACU el tecnopor y la mezcla del sellador. La mano de
obra sale de COLECTOR INSUMOS y su costo hora-hombre de la ACU TAPA REGISTRO. Edicion directa del XML (conserva formato e
imagenes); no cambia ninguna cantidad de metrado. Uso: python3 herramientas/acu_juntas_refugio.py <planilla.xlsx>
"""
import sys, os, re, html, zipfile, shutil
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular

PT, PR = 13.90, 17.70            # plancha de tecnopor 1" x 1.20 x 2.40 (Sodimac Peru) y RC-250 por galon (Conselva), con IGV
F_TEC = "Sodimac Peru: plancha de poliestireno expandido 1\" x 1.20 x 2.40 m (Dipropor) S/ 13.90 con IGV"
F_RC = "Conselva: asfalto liquido RC-250 por galon S/ 17.70 con IGV (Petroperu publica su lista ex planta; confirmar en Tarapoto)"
CJ, CI, AT = "'COLECTOR JUNTAS Y EMPALMES'!", "'COLECTOR INSUMOS'!", "'ACU TAPA REGISTRO'!"


class Hoja:
    """Compone el XML de una hoja nueva con los estilos de la ACU TAPA REGISTRO."""
    def __init__(self, L, s4):
        self.L, self.s4, self.filas, self.merges, self.r = L, s4, [], [], 0

    def c(self, ref, st, v):
        if v is None: return '<c r="%s" s="%d"/>' % (ref, st)
        if isinstance(v, str) and v.startswith("="):
            return '<c r="%s" s="%d" t="n"><f aca="false">%s</f><v>0</v></c>' % (ref, st, html.escape(v[1:], quote=False))
        if isinstance(v, str): return '<c r="%s" s="%d" t="s"><v>%d</v></c>' % (ref, st, self.L.sid(v))
        return '<c r="%s" s="%d" t="n"><v>%s</v></c>' % (ref, st, repr(float(v)))

    def fila(self, celdas, ht=19.5, salto=0):
        self.r += 1 + salto; r = self.r
        xs = "".join(self.c("%s%d" % (col, r), st, v) for col, st, v in celdas)
        self.filas.append('<row r="%d" customFormat="false" ht="%s" hidden="false" customHeight="true" outlineLevel="0" collapsed="false">%s</row>' % (r, ht, xs))
        return r

    def banda(self, texto, st=294, ht=19.5, salto=0, desde="A"):
        cols = "ABCDEFGH"; i = cols.index(desde)
        r = self.fila([(k, st if k >= desde else 21, texto if k == desde else None) for k in cols], ht, salto)
        self.merges.append("%s%d:H%d" % (desde, r, r)); return r

    def xml(self, plantilla):
        i, j = plantilla.index("<sheetData>"), plantilla.index("</sheetData>")
        cab = plantilla[:i].replace('topLeftCell="A7"', 'topLeftCell="A1"').replace('tabSelected="true"', 'tabSelected="false"')
        cab = re.sub(r'<dimension ref="[^"]+"/>', '<dimension ref="A1:H%d"/>' % self.r, cab)
        cola = plantilla[j:]
        cola = re.sub(r"<mergeCells.*?</mergeCells>", '<mergeCells count="%d">%s</mergeCells>' % (len(self.merges), "".join('<mergeCell ref="%s"/>' % m for m in self.merges)), cola, flags=re.S)
        return cab + "<sheetData>" + "".join(self.filas) + cola


def encabezado(H, titulo, nota, plantilla):
    H.banda(titulo, 277, 27)
    for r in (2, 3, 4, 5):                                   # entidad, proyecto, ubicacion y fecha (de RESUMEN)
        fila = re.search(r'<row r="%d"[ >].*?</row>' % r, plantilla, re.S).group(0)
        H.r += 1; H.filas.append(fila); H.merges += ["A%d:B%d" % (r, r), "C%d:H%d" % (r, r)]
    H.banda(nota, 281, 66, salto=1)


def tabla_datos(H, Y4, titulo, datos):
    """datos: (concepto, und, valor o formula, sustento); devuelve {clave: celda D}."""
    H.banda(titulo, salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "CONCEPTO", "UND", "VALOR", None, None, None, "SUSTENTO"))], 31.5)
    ref = {}
    for n, (clave, t, u, v, s) in enumerate(datos, 1):
        st = 306 if isinstance(v, str) else Y4
        r = H.fila([("A", 283, n), ("B", 149, t), ("C", 285, u), ("D", st, v), ("E", 295, None), ("F", 295, None), ("G", 295, None), ("H", 149, s)], 31.5)
        ref[clave] = "$D$%d" % r
    return ref


def acu(H, partida, metrado_txt, und, metrado, mo, mat, nota_rend, rend=None, por="M",
        herr="3 % del costo de mano de obra (incluye recipiente para calentar el asfalto)"):
    """Analisis en formato Delphin: mo y mat = [(recurso, und, cantidad (formula), precio, fuente)]."""
    H.banda("2. ANALISIS DE COSTO UNITARIO (formato Delphin)", salto=1)
    for t, v, st in (("Partida", partida, 295), ("Partida del metrado", metrado_txt, 295), ("Unidad", und, 295), ("Metrado", metrado, 290)):
        r = H.fila([("A", 294, t), ("B", 294, None), ("C", st, v)] + [(k, st, None) for k in "DEFGH"]); H.merges += ["A%d:B%d" % (r, r), "C%d:H%d" % (r, r)]
        if t == "Metrado": r_met = r
    r_rend = H.r + 1; r_op = r_rend + 3                      # el operario (o el primer recurso de mano de obra) define el rendimiento
    r = H.fila([("A", 294, "Rendimiento (%s)" % nota_rend), ("B", 294, None), ("C", 290, rend or "=8/E%d" % r_op)] + [(k, 290, None) for k in "DEFGH"]); H.merges += ["A%d:B%d" % (r, r), "C%d:H%d" % (r, r)]
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "RECURSO", "UND", "CUADRILLA", "CANTIDAD POR " + por, "PRECIO S/", "PARCIAL S/", "FUENTE DEL PRECIO"))], 31.5)
    n = 0; sub = {}
    for grupo, items in (("MANO DE OBRA", mo), ("MATERIALES", mat)):
        H.banda(grupo, desde="B"); r0 = H.r + 1
        for rec, u, q, p, f in items:
            n += 1; r = H.r + 1
            cuad = "=E%d*$C$%d/8" % (r, r_rend) if grupo == "MANO DE OBRA" else None
            H.fila([("A", 283, n), ("B", 295, rec), ("C", 285, u), ("D", 306 if cuad else 295, cuad), ("E", 306, q), ("F", 289 if not isinstance(p, str) else 290, p),
                    ("G", 290, "=E%d*F%d" % (r, r)), ("H", 149, f)], 31.5 if len(f) > 60 else 19.5)
        sub[grupo] = H.fila([("A", 21, None), ("B", 294, "Subtotal " + grupo.lower())] + [(k, 295, None) for k in "CDEF"] + [("G", 296, "=SUM(G%d:G%d)" % (r0, H.r)), ("H", 295, None)])
    H.banda("EQUIPOS", desde="B"); n += 1; r = H.r + 1
    H.fila([("A", 283, n), ("B", 295, "Herramientas manuales"), ("C", 285, "%mo"), ("D", 295, None), ("E", 284, 0.03), ("F", 290, "=+G%d" % sub["MANO DE OBRA"]),
            ("G", 290, "=E%d*F%d" % (r, r)), ("H", 149, herr)])
    sub["EQUIPOS"] = H.fila([("A", 21, None), ("B", 294, "Subtotal equipos")] + [(k, 295, None) for k in "CDEF"] + [("G", 296, "=SUM(G%d:G%d)" % (r, r)), ("H", 295, None)])
    rcu = H.fila([("A", 294, "COSTO UNITARIO DIRECTO (S/ por %s)" % und)] + [(k, 294, None) for k in "BCDEF"] +
                 [("G", 296, "=+G%d+G%d+G%d" % (sub["MANO DE OBRA"], sub["MATERIALES"], sub["EQUIPOS"])), ("H", 295, None)], 21.75)
    rp = H.fila([("A", 294, "COSTO DIRECTO DE LA PARTIDA (metrado x costo unitario, S/)")] + [(k, 294, None) for k in "BCDEF"] +
                [("G", 296, "=G%d*C%d" % (rcu, r_met)), ("H", 295, None)], 21.75)
    H.merges += ["A%d:F%d" % (rcu, rcu), "A%d:F%d" % (rp, rp)]


def agregar_hoja(L, nombre, xml):
    n = max(int(re.search(r"sheet(\d+)\.xml", v).group(1)) for v in L.ruta.values()) + 1
    ruta = "xl/worksheets/sheet%d.xml" % n
    wb = L.F["xl/workbook.xml"].decode(); rels = L.F["xl/_rels/workbook.xml.rels"].decode(); ct = L.F["[Content_Types].xml"].decode()
    sid = max(int(v) for v in re.findall(r'sheetId="(\d+)"', wb)) + 1; rid = "rId%d" % (max(int(v) for v in re.findall(r'Id="rId(\d+)"', rels)) + 1)
    wb = wb.replace("</sheets>", '<sheet name="%s" sheetId="%d" state="visible" r:id="%s"/></sheets>' % (nombre, sid, rid))
    rels = rels.replace("</Relationships>", '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/></Relationships>' % (rid, n))
    ct = ct.replace("</Types>", '<Override PartName="/%s" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>' % ruta)
    L.F["xl/workbook.xml"], L.F["xl/_rels/workbook.xml.rels"], L.F["[Content_Types].xml"] = wb.encode(), rels.encode(), ct.encode()
    L.F[ruta] = xml.encode(); L.infos.append(zipfile.ZipInfo(ruta, date_time=L.infos[0].date_time)); L.infos[-1].compress_type = zipfile.ZIP_DEFLATED
    L.ruta[nombre] = ruta


def estilo_amarillo4(L):
    """Agrega un formato de celda amarillo con 4 decimales (copia del estilo 284 con el formato 0.0000)."""
    s = L.F["xl/styles.xml"].decode(); i, j = s.index("<cellXfs"), s.index("</cellXfs>")
    xfs = re.findall(r"<xf [^>]*?(?:/>|>.*?</xf>)", s[i:j], re.S)
    nuevo = xfs[284].replace('numFmtId="173"', 'numFmtId="170"')
    s = s[:j] + nuevo + s[j:]
    s = re.sub(r'<cellXfs count="\d+"', '<cellXfs count="%d"' % (len(xfs) + 1), s, count=1)
    L.F["xl/styles.xml"] = s.encode(); return len(xfs)


def construir(f):
    L = Libro(f)
    assert "ACU JUNTA DILATACION" not in L.ruta, "las hojas ya existen"
    plantilla = L.hoja("ACU TAPA REGISTRO"); Y4 = estilo_amarillo4(L)
    PRE = lambda p: "=%s/1.18" % repr(p)
    # ---------------------------------------------------------------- junta de dilatacion
    H = Hoja(L, Y4)
    encabezado(H, "ANALISIS DE COSTO UNITARIO - JUNTA DE DILATACION E=1\" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR",
               "Partida de Delphin 01.04.04.06.01 JUNTA DE DILATACION E=1\" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR (metrado 01.04.04.06.01, hoja COLECTOR JUNTAS Y EMPALMES). "
               "Se mide por metro de junta a lo largo del perimetro de la seccion. Cantidades de la lamina DD-03: plancha de tecnopor de 1\" en toda la seccion y sellador asfaltico 1\" x 2\" "
               "(asfalto liquido RC-250 + arena gruesa) en las caras interiores y en la cara superior (EG-2013 MTC, 510). Celda amarilla = dato; verde = formula. Precios sin IGV.", plantilla)
    D = tabla_datos(H, Y4, "1. CANTIDADES POR METRO DE JUNTA (lamina DD-03 y hoja COLECTOR JUNTAS Y EMPALMES)", [
        ("per", "Perimetro de la seccion en cada junta: 2 x 1.10 + 2 x (0.15 + 1.61 + 0.10)", "m", "=" + CJ + "E11", "COLECTOR JUNTAS Y EMPALMES fila 11; DD-03 A"),
        ("n", "Numero de juntas de dilatacion (cada 4.00 m)", "und", "=" + CJ + "D11", "COLECTOR JUNTAS Y EMPALMES fila 11; DD-03 E"),
        ("atec", "Area de tecnopor por junta: seccion 1.10 x 1.86 menos el hueco 0.80 x 1.61", "m2", "=1.10*(0.15+1.61+0.10)-0.80*1.61", "DD-03, cuadro de componentes"),
        ("tec", "Tecnopor por metro de junta (area neta)", "m2/m", "=D%d/D%d", "formula"),
        ("desp", "Desperdicio por el corte del anillo en planchas de 1.20 x 2.40", "-", 0.10, "criterio: recortes del hueco interior y de las esquinas"),
        ("pl", "Area de una plancha de tecnopor 1\" (1.20 x 2.40 m)", "m2", 2.88, "medida comercial"),
        ("pln", "Planchas de tecnopor por metro de junta", "pln/m", "=D%d*(1+D%d)/D%d", "formula"),
        ("ls", "Longitud sellada por junta: caras interiores 2 x 1.61 + 0.80 y cara superior 1.10", "m", "=2*1.61+0.80+1.10", "DD-03, cuadro de componentes"),
        ("as", "Seccion del sellador 1\" x 2\" (0.0254 x 0.0508)", "m2", "=0.0254*0.0508", "DD-03 B; EG-2013 510.02 c"),
        ("mez", "Mezcla de sellador por metro de junta", "m3/m", "=D%d*D%d/D%d", "formula"),
        ("rc", "Asfalto liquido RC-250 por m3 de mezcla", "gal/m3", 50, "criterio: mezcla de ~2,000 kg/m3 con ~9 % de asfalto = 180 kg / 3.6 kg/gal"),
        ("ar", "Arena gruesa por m3 de mezcla", "m3/m3", 1.05, "criterio: arena suelta con 5 % de desperdicio"),
        ("op", "Operario por metro de junta (colocacion del tecnopor y sellado)", "hh/m", "=" + CI + "G71", "COLECTOR INSUMOS fila 71"),
        ("pe", "Peon por metro de junta", "hh/m", "=" + CI + "G72", "COLECTOR INSUMOS fila 72"),
    ])
    k = lambda c: int(D[c].split("$")[-1])
    fix = {"tec": "=D%d/D%d" % (k("atec"), k("per")), "pln": "=D%d*(1+D%d)/D%d" % (k("tec"), k("desp"), k("pl")), "mez": "=D%d*D%d/D%d" % (k("as"), k("ls"), k("per"))}
    for c_, fml in fix.items():
        r = k(c_)
        H.filas = [re.sub(r'(<c r="D%d" s="306" t="n"><f aca="false">)[^<]*(</f>)' % r, lambda m, f=fml: m.group(1) + html.escape(f[1:], quote=False) + m.group(2), x) for x in H.filas]
    acu(H, "01.04.04.06.01 JUNTA DE DILATACION E=1\" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR", "01.04.04.06.01 (hoja COLECTOR JUNTAS Y EMPALMES)", "m", "=" + CJ + "F12",
        [("Operario", "hh", "=" + D["op"], "=" + AT + "F69", "costo hora-hombre de la ACU TAPA REGISTRO"), ("Peon", "hh", "=" + D["pe"], "=" + AT + "F71", "costo hora-hombre de la ACU TAPA REGISTRO")],
        [("Plancha de tecnopor 1\" x 1.20 x 2.40 m", "pln", "=" + D["pln"], PRE(PT), F_TEC),
         ("Asfalto liquido RC-250", "gal", "=%s*%s" % (D["mez"], D["rc"]), PRE(PR), F_RC),
         ("Arena gruesa", "m3", "=%s*%s" % (D["mez"], D["ar"]), "=" + AT + "F77", "precio de la ACU TAPA REGISTRO (Agregados Tarapoto, Morales)")],
        "m/dia, cuadrilla de 1 operario")
    agregar_hoja(L, "ACU JUNTA DILATACION", H.xml(plantilla)); DD = D
    # ---------------------------------------------------------------- junta con el cerco
    H = Hoja(L, Y4)
    encabezado(H, "ANALISIS DE COSTO UNITARIO - JUNTA E=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO",
               "Partida de Delphin 01.04.04.06.02 JUNTA E=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO (metrado 01.04.04.06.02, hoja COLECTOR JUNTAS Y EMPALMES). "
               "Cantidades de la lamina DD-03: plancha de tecnopor de 1\" de 0.90 m de altura contra el cimiento del cerco y de 0.10 m en el borde de la losa con el piso adyacente (un solo lado, lado via), con sellador "
               "asfaltico 1\" x 2\" (RC-250 + arena) en la cara superior. Celda amarilla = dato; verde = formula. Precios sin IGV.", plantilla)
    D = tabla_datos(H, Y4, "1. CANTIDADES POR METRO DE JUNTA (lamina DD-03 y hoja COLECTOR JUNTAS Y EMPALMES)", [
        ("lc", "Junta contra el cimiento del cerco (0+000.00 a 0+058.81)", "m", "=" + CJ + "F15", "COLECTOR JUNTAS Y EMPALMES fila 15"),
        ("hc", "Altura de la plancha contra el cerco", "m", 0.90, "DD-03 C"),
        ("lb", "Junta en el borde de la losa con el piso adyacente, un lado (colector y cajas CL y CC)", "m", "=%sF16+%sF17+%sF18" % (CJ, CJ, CJ), "COLECTOR JUNTAS Y EMPALMES filas 16 a 18"),
        ("hb", "Altura de la plancha en el borde de la losa", "m", 0.10, "DD-03 D"),
        ("lt", "Longitud total de la partida", "m", "=" + CJ + "F19", "COLECTOR JUNTAS Y EMPALMES fila 19"),
        ("tec", "Tecnopor por metro de junta (promedio ponderado)", "m2/m", "=(D1*D2+D3*D4)/D5", "formula"),
        ("desp", "Desperdicio por el corte en tiras", "-", 0.05, "criterio"),
        ("pl", "Area de una plancha de tecnopor 1\" (1.20 x 2.40 m)", "m2", 2.88, "medida comercial"),
        ("pln", "Planchas de tecnopor por metro de junta", "pln/m", "=D1", "formula"),
        ("mez", "Mezcla de sellador por metro de junta: 1\" x 2\" en la cara superior (0.0254 x 0.0508)", "m3/m", "=0.0254*0.0508", "DD-03 C y D; EG-2013 510.02 c"),
        ("rc", "Asfalto liquido RC-250 por m3 de mezcla", "gal/m3", 50, "criterio: mezcla de ~2,000 kg/m3 con ~9 % de asfalto = 180 kg / 3.6 kg/gal"),
        ("ar", "Arena gruesa por m3 de mezcla", "m3/m3", 1.05, "criterio: arena suelta con 5 % de desperdicio"),
        ("pe", "Peon por metro de junta (corte y colocacion de las tiras)", "hh/m", "=" + CI + "G74", "COLECTOR INSUMOS fila 74"),
        ("op", "Operario por metro de junta (sellado)", "hh/m", "=" + CI + "G76", "COLECTOR INSUMOS fila 76"),
    ])
    k = lambda c: int(D[c].split("$")[-1])
    fix = {"tec": "=(D%d*D%d+D%d*D%d)/D%d" % (k("lc"), k("hc"), k("lb"), k("hb"), k("lt")), "pln": "=D%d*(1+D%d)/D%d" % (k("tec"), k("desp"), k("pl"))}
    for c_, fml in fix.items():
        r = k(c_)
        H.filas = [re.sub(r'(<c r="D%d" s="306" t="n"><f aca="false">)[^<]*(</f>)' % r, lambda m, f=fml: m.group(1) + html.escape(f[1:], quote=False) + m.group(2), x) for x in H.filas]
    acu(H, "01.04.04.06.02 JUNTA E=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO", "01.04.04.06.02 (hoja COLECTOR JUNTAS Y EMPALMES)", "m", "=" + CJ + "F19",
        [("Operario", "hh", "=" + D["op"], "=" + AT + "F69", "costo hora-hombre de la ACU TAPA REGISTRO"), ("Peon", "hh", "=" + D["pe"], "=" + AT + "F71", "costo hora-hombre de la ACU TAPA REGISTRO")],
        [("Plancha de tecnopor 1\" x 1.20 x 2.40 m", "pln", "=" + D["pln"], PRE(PT), F_TEC),
         ("Asfalto liquido RC-250", "gal", "=%s*%s" % (D["mez"], D["rc"]), PRE(PR), F_RC),
         ("Arena gruesa", "m3", "=%s*%s" % (D["mez"], D["ar"]), "=" + AT + "F77", "precio de la ACU TAPA REGISTRO (Agregados Tarapoto, Morales)")],
        "m/dia, operario de sellado")
    agregar_hoja(L, "ACU JUNTA CERCO", H.xml(plantilla)); DC = D
    # ---------------------------------------------------------------- COLECTOR INSUMOS lee de las ACU
    q = lambda h, c: "'%s'!%s" % (h, c)
    assert L.leer("COLECTOR INSUMOS", "E69").startswith("Tecnopor") and L.leer("COLECTOR INSUMOS", "E73").startswith("Tecnopor")
    L.formula("COLECTOR INSUMOS", "G69", "%s*(1+%s)" % (q("ACU JUNTA DILATACION", DD["tec"]), q("ACU JUNTA DILATACION", DD["desp"])))
    L.formula("COLECTOR INSUMOS", "G70", q("ACU JUNTA DILATACION", DD["mez"]))
    L.formula("COLECTOR INSUMOS", "G73", "%s*(1+%s)" % (q("ACU JUNTA CERCO", DC["tec"]), q("ACU JUNTA CERCO", DC["desp"])))
    L.formula("COLECTOR INSUMOS", "G75", q("ACU JUNTA CERCO", DC["mez"]))
    for ref in ("G69", "G70", "G73", "G75"):                      # verde: ya no es dato sino formula
        L.x["COLECTOR INSUMOS"] = re.sub(r'(<c r="%s" s=")\d+(")' % ref, r"\g<1>306\g<2>", L.x["COLECTOR INSUMOS"])
    L.guardar(f)
    return recalcular(f, ["ACU JUNTA DILATACION", "ACU JUNTA CERCO", "COLECTOR INSUMOS"])


if __name__ == "__main__":
    print("celdas recalculadas:", construir(sys.argv[1]))
