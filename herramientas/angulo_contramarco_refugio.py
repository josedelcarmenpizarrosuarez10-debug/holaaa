"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): contramarco de la tapa de registro con angulo
L 1 1/2"x1 1/2"x1/8" (antes L 2"x2"x3/16"), lija y thinner desagregados y precios cotizados en la ACU TAPA REGISTRO.
Sustento: entregables/COTIZACION_PRECIOS_ACU_TAPA_REGISTRO_HOGAR_REFUGIO.xlsx (hoja 2 ANGULOS: verificacion).

Edicion directa del XML (conserva formato e imagenes):
- COLECTOR PARAMETROS: peso 1.83 kg/m y desarrollo pintado 0.152 m2/m del contramarco.
- COLECTOR REGISTROS Y TAPAS, DESAGREGADO TAPA REGISTRO, PLANILLA GENERAL: nombres del contramarco.
- COLECTOR INSUMOS: "Lija y thinner" (glb) pasa a lija (0.25 und/m2) y thinner (0.024 gal/m2): se inserta la fila 67.
- ACU TAPA REGISTRO: idem en el desglose (se inserta la fila 53) y en el formato Delphin un solo angulo, lija y
  thinner por separado y los precios cotizados.
Los valores en cache se recalculan con LibreOffice sobre una copia y se escriben en el XML (Excel recalcula al abrir).
"""
import sys, os, zipfile, re, html, shutil, subprocess, tempfile
import openpyxl

ANG = 'L 1 1/2"x1 1/2"x1/8"'; VIEJO = 'L 2"x2"x3/16"'
DELPHIN = [  # fila, insumo, und, precio S/ sin IGV, fuente
    (74, 'Angulo L 1 1/2"x1 1/2"x1/8"', "kg", 3.08, "Sodimac Peru: barra de 6 m (10.98 kg) S/ 39.90 con IGV"),
    (75, 'Soldadura cellocord E6011 1/8"', "kg", 18.63, "Sodimac Peru: caja de 5 kg S/ 109.90 con IGV"),
    (76, "Cemento Portland tipo I", "bol", 30.93, "Cemento Pacasmayo tipo I 42.5 kg: S/ 36.50 con IGV"),
    (77, "Arena gruesa", "m3", 40.68, "Agregados Tarapoto (Morales): S/ 48.00 el m3"),
    (78, 'Piedra chancada 1/2"', "m3", 101.69, 'Por cotizar en Tarapoto: no hay precio publicado de la piedra de 1/2"'),
    (79, "Agua", "m3", 8.33, "EMAPA San Martin: tarifa comercial de 30 m3 a mas, agua 6.80 + alcantarillado 1.53"),
    (80, "Madera tornillo", "p2", 4.41, "Maderas del Norte: S/ 5.20 el p2 con IGV"),
    (81, "Acero corrugado fy=4200", "kg", 3.44, 'Sodimac Peru, Aceros Arequipa: 1/2" x 9 m S/ 36.50 y 3/8" x 9 m S/ 20.35 con IGV (ponderado)'),
    (82, "Alambre negro N 16", "kg", 5.08, "Sodimac Peru: rollo de 10 kg S/ 59.90 con IGV"),
    (83, "Pintura anticorrosiva", "gal", 44.92, "Promart: anticorrosivo Vencedor 1 gl S/ 53.00 con IGV"),
    (84, "Esmalte sintetico", "gal", 48.31, "Promart: esmalte sintetico CPP 1 gl S/ 57.00 con IGV"),
    (85, "Lija para fierro N° 80", "und", 2.12, "Sodimac Peru: lija para fierro 3M grano 80 S/ 2.50 con IGV"),
    (86, "Thinner acrilico", "gal", 35.65, "Sodimac Peru: thinner acrilico TOPEX 3.5 L S/ 38.90 con IGV"),
    (90, "Mezcladora 9-11 p3", "hm", 12.71, "Konstrutecnia: S/ 15.00 la hora-maquina con IGV"),
    (91, "Vibrador de concreto", "hm", 11.02, "Konstrutecnia: S/ 13.00 la hora-maquina con IGV"),
    (92, "Maquina de soldar 250 A", "hm", 8.00, "Por cotizar en Tarapoto: no hay tarifa publicada"),
]
LIJA, THIN = 0.25, 0.024     # und/m2 y gal/m2 (ver DESAGREGADO_LIJA_THINNER_TAPA_REGISTRO_HOGAR_REFUGIO.xlsx)


class Libro:
    def __init__(self, f):
        z = zipfile.ZipFile(f); self.infos = z.infolist(); self.F = {n: z.read(n) for n in z.namelist()}; z.close()
        ss = self.F["xl/sharedStrings.xml"].decode()
        self.ss_head, self.ss_tail = ss[:ss.index("<si>")], ss[ss.rindex("</si>") + 5:]
        self.sis = re.findall(r"<si>.*?</si>", ss, re.S)
        wb = self.F["xl/workbook.xml"].decode(); rels = self.F["xl/_rels/workbook.xml.rels"].decode()
        self.ruta = {}
        for nom, rid in re.findall(r'<sheet name="([^"]+)"[^>]*r:id="([^"]+)"', wb):
            t = re.search(r'Id="%s"[^>]*Target="([^"]+)"' % rid, rels).group(1)
            self.ruta[html.unescape(nom)] = "xl/" + t
        self.x = {}

    def hoja(self, nom):
        if nom not in self.x: self.x[nom] = self.F[self.ruta[nom]].decode()
        return self.x[nom]

    def txt(self, i): return html.unescape("".join(re.findall(r"<t[^>]*>(.*?)</t>", self.sis[i], re.S)))

    def sid(self, t):
        for i, s in enumerate(self.sis):
            if re.fullmatch(r'<si><t(?: xml:space="preserve")?>(.*?)</t></si>', s, re.S) and self.txt(i) == t: return i
        self.sis.append('<si><t xml:space="preserve">%s</t></si>' % html.escape(t, quote=False)); return len(self.sis) - 1

    def celda(self, nom, ref):
        return re.search(r'<c r="%s"(?= |>|/)[^>]*?(/>|>.*?</c>)' % ref, self.hoja(nom), re.S)

    def leer(self, nom, ref):
        m = self.celda(nom, ref); assert m, (nom, ref)
        v = re.search(r"<v>(.*?)</v>", m.group(0))
        return self.txt(int(v.group(1))) if 't="s"' in m.group(0) else (v.group(1) if v else None)

    def poner(self, nom, ref, inner, t):
        x = self.hoja(nom); m = self.celda(nom, ref); assert m, (nom, ref)
        s = re.search(r' s="(\d+)"', m.group(0)); s = ' s="%s"' % s.group(1) if s else ""
        self.x[nom] = x[:m.start()] + '<c r="%s"%s%s>%s</c>' % (ref, s, ' t="%s"' % t if t else "", inner) + x[m.end():]

    def texto(self, nom, ref, t): self.poner(nom, ref, "<v>%d</v>" % self.sid(t), "s")
    def num(self, nom, ref, v): self.poner(nom, ref, "<v>%s</v>" % repr(float(v)), "n")
    def formula(self, nom, ref, f): self.poner(nom, ref, '<f aca="false">%s</f><v>0</v>' % html.escape(f, quote=False), "n")

    def cambiar(self, nom, ref, viejo, nuevo):
        t = self.leer(nom, ref); assert viejo in t, (nom, ref, t); self.texto(nom, ref, t.replace(viejo, nuevo))

    def desplazar(self, nom, desde, hasta, d=1):
        """Baja d filas las filas desde..hasta (debajo debe haber filas libres) y corrige las referencias de la hoja."""
        x = self.hoja(nom)
        def ref(m):
            r = int(m.group(2)); return m.group(1) + str(r + d if desde <= r <= hasta else r)
        TOK = re.compile(r"((?:&apos;.*?&apos;|'[^']*'|[A-Za-z_][\w.]*)!)?(\$?[A-Z]{1,3}\$?)(\d+)(?::(\$?[A-Z]{1,3}\$?)(\d+))?(?![\d(\w])")
        def tok(m):
            if m.group(1): return m.group(0)                      # referencia a otra hoja: no cambia
            def mv(r): r = int(r); return str(r + d if desde <= r <= hasta else r)
            t = m.group(2) + mv(m.group(3))
            if m.group(4): t += ":" + m.group(4) + mv(m.group(5))
            return t
        def fx(m):                                               # formula y rango ref="..." de las formulas compartidas
            f = re.sub(r'ref="([^"]+)"', lambda r: 'ref="%s"' % TOK.sub(tok, r.group(1)), m.group(1))
            return f + TOK.sub(tok, m.group(2)) + m.group(3)
        x = re.sub(r"(<f(?:\s[^>/]*)?>)(.*?)(</f>)", fx, x, flags=re.S)
        for r in range(hasta, desde - 1, -1):
            m = re.search(r'<row r="%d"[ >].*?</row>' % r, x, re.S)
            if not m: continue
            row = re.sub(r'(<row r=")%d"' % r, r'\g<1>%d"' % (r + d), m.group(0))
            row = re.sub(r'(<c r="[A-Z]+)%d"' % r, r'\g<1>%d"' % (r + d), row)
            x = x[:m.start()] + row + x[m.end():]
        x = re.sub(r'<mergeCell ref="([A-Z]+)(\d+):([A-Z]+)(\d+)"/>',
                   lambda m: '<mergeCell ref="%s%d:%s%d"/>' % (m.group(1), int(m.group(2)) + (d if desde <= int(m.group(2)) <= hasta else 0),
                                                              m.group(3), int(m.group(4)) + (d if desde <= int(m.group(4)) <= hasta else 0)), x)
        self.x[nom] = x

    def insertar_copia(self, nom, origen, nueva):
        """Inserta la fila `nueva` (libre) como copia de la fila `origen`, justo despues de la fila nueva-1."""
        x = self.hoja(nom)
        assert not re.search(r'<row r="%d"[ >]' % nueva, x), "la fila %d no esta libre" % nueva
        row = re.search(r'<row r="%d"[ >].*?</row>' % origen, x, re.S).group(0)
        row = re.sub(r'(<row r=")%d"' % origen, r'\g<1>%d"' % nueva, row)
        row = re.sub(r'(<c r="[A-Z]+)%d"' % origen, r'\g<1>%d"' % nueva, row)
        prev = re.search(r'<row r="%d"[ >].*?</row>' % (nueva - 1), x, re.S)
        self.x[nom] = x[:prev.end()] + row + x[prev.end():]

    def guardar(self, f):
        self.F["xl/sharedStrings.xml"] = (re.sub(r'uniqueCount="\d+"', 'uniqueCount="%d"' % len(self.sis), self.ss_head)
                                          + "".join(self.sis) + self.ss_tail).encode()
        for nom, x in self.x.items(): self.F[self.ruta[nom]] = x.encode()
        tmp = f + ".tmp"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
            for i in self.infos: zo.writestr(i, self.F[i.filename])
        shutil.move(tmp, f)


def cambios(L):
    CP, RT, DT, CI, AC, PG = ("COLECTOR PARAMETROS", "COLECTOR REGISTROS Y TAPAS", "DESAGREGADO TAPA REGISTRO", "COLECTOR INSUMOS",
                              "ACU TAPA REGISTRO", "PLANILLA GENERAL DE METRADOS")
    assert L.leer(AC, "B22") == 'Angulo L 2"x2"x3/16"', "la planilla ya fue modificada"
    # ---- parametros
    L.cambiar(CP, "B36", VIEJO, ANG); L.texto(CP, "B38", 'Peso del angulo %s (contramarco)' % ANG); L.num(CP, "C38", 1.83)
    L.texto(CP, "B39", 'Peso del angulo %s (marco de tapa)' % ANG)
    L.texto(CP, "B40", 'Desarrollo pintado del angulo 1 1/2"x1 1/2" del contramarco (4 caras)'); L.num(CP, "C40", 0.152); L.texto(CP, "E40", "4 x 0.0381 m")
    L.texto(CP, "B41", 'Desarrollo pintado del angulo 1 1/2"x1 1/2" del marco de tapa (4 caras)')
    # ---- registros y tapas, desagregado, planilla
    L.cambiar(RT, "A7", VIEJO, ANG); L.cambiar(RT, "B23", VIEJO, ANG)
    L.texto(RT, "D25", "registros x (2.80 x 1.83 + 2.72 x 1.83)"); L.texto(RT, "D28", "registros x (2.80 x 0.152 + 2.72 x 0.152)")
    L.texto(DT, "B25", 'Contramarco: angulo %s, 4 x 0.70 = 2.80 m x 1.83 kg/m' % ANG)
    L.texto(DT, "B38", "Anticorrosivo y esmalte en angulos: 2.80 x 0.152 + 2.72 x 0.152")
    for r in range(300, 330):
        try: t = L.leer(PG, "B%d" % r)
        except AssertionError: continue
        if t and VIEJO in t: L.cambiar(PG, "B%d" % r, VIEJO, ANG)
    # ---- insumos: lija y thinner por separado (fila 67 nueva)
    L.texto(CI, "E60", 'Angulo %s (incluye corte y soldadura)' % ANG)
    L.desplazar(CI, 67, 75); L.insertar_copia(CI, 66, 67)
    L.texto(CI, "E66", "Lija para fierro N° 80"); L.texto(CI, "F66", "und"); L.num(CI, "G66", LIJA)
    L.texto(CI, "E67", "Thinner acrilico"); L.texto(CI, "F67", "gal"); L.num(CI, "G67", THIN); L.formula(CI, "H67", "G67*$D$64")
    L.x[CI] = re.sub(r'<dimension ref="A1:([A-Z]+)75"/>', r'<dimension ref="A1:\g<1>76"/>', L.x[CI])
    # ---- ACU: desglose
    L.texto(AC, "B11", "Contramarco metalico %s con anclajes" % ANG)
    L.texto(AC, "H13", "2.80 x 1.83 + 2.72 x 1.83 = 10.10 kg por tapa"); L.texto(AC, "H17", "2.80 x 0.152 + 2.72 x 0.152 = 0.84 m2 por tapa")
    L.texto(AC, "B22", "Angulo " + ANG); L.texto(AC, "H22", "Contramarco 4 x 0.70 = 2.80 m x 1.83 kg/m; 5 % de desperdicio (COLECTOR INSUMOS)")
    L.desplazar(AC, 53, 59); L.insertar_copia(AC, 52, 53)
    L.texto(AC, "B52", "Lija para fierro N° 80"); L.texto(AC, "C52", "und"); L.texto(AC, "H52", "COLECTOR INSUMOS: 1 pliego cada 4 m2")
    L.texto(AC, "B53", "Thinner acrilico"); L.texto(AC, "C53", "gal")
    L.formula(AC, "E53", "+'COLECTOR INSUMOS'!G67"); L.formula(AC, "F53", "D53*E53"); L.formula(AC, "G53", "F53*SUMIF($B$68:$B$93,B53,$F$68:$F$93)")
    L.texto(AC, "H53", "COLECTOR INSUMOS: 15 % del volumen de pintura (dilucion y limpieza)")
    L.formula(AC, "E54", "+'COLECTOR INSUMOS'!G68")
    # ---- ACU: formato Delphin
    for r, ins, u, p, fte in DELPHIN:
        L.texto(AC, "B%d" % r, ins); L.texto(AC, "C%d" % r, u); L.num(AC, "F%d" % r, p); L.texto(AC, "H%d" % r, fte)
    L.cambiar(AC, "A7", "Precios sin IGV, referenciales: al pasar a Delphin rigen los de la base de precios del presupuesto.",
              "Precios sin IGV obtenidos de precios publicados (octubre 2026), con su fuente en la columna H; los marcados \"por cotizar\" deben confirmarse en Tarapoto.")
    L.x[AC] = re.sub(r'<dimension ref="A1:([A-Z]+)96"/>', r'<dimension ref="A1:\g<1>96"/>', L.x[AC])
    return [CP, RT, DT, CI, AC, PG]


def recalcular(f, hojas):
    """Calcula con LibreOffice sobre una copia y escribe los valores en cache de las celdas con formula."""
    tmp = tempfile.mkdtemp(); src = os.path.join(tmp, "sin_cache", os.path.basename(f)); os.makedirs(os.path.dirname(src))
    with zipfile.ZipFile(f) as zi, zipfile.ZipFile(src, "w", zipfile.ZIP_DEFLATED) as zo:     # sin valores en cache: LibreOffice calcula todo
        for i in zi.infolist():
            b = zi.read(i.filename)
            if i.filename.startswith("xl/worksheets/sheet"):
                b = re.sub(r"(<f(?:\s[^>]*?)?(?:/>|>.*?</f>))<v>.*?</v>", r"\1", b.decode(), flags=re.S).encode()
            zo.writestr(i, b)
    subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", tmp, src], check=True, capture_output=True)
    wv = openpyxl.load_workbook(os.path.join(tmp, os.path.basename(f)), data_only=True)
    L = Libro(f); cambios_v = 0
    for nom in hojas:
        x = L.hoja(nom); ws = wv[nom]
        def rep(m):
            nonlocal cambios_v
            ref, attrs, f_ = m.group(1), m.group(2), m.group(3)
            v = ws[ref].value
            if v is None or (isinstance(v, str) and v.startswith("#")): return m.group(0)
            if not isinstance(v, (str, int, float)) or isinstance(v, bool): return m.group(0)
            if isinstance(v, str):
                attrs = re.sub(r' t="\w+"', "", attrs) + ' t="str"'; vv = html.escape(v, quote=False)
            else:
                attrs = re.sub(r' t="\w+"', "", attrs) + ' t="n"'; vv = repr(float(v))
            cambios_v += 1
            return '<c r="%s"%s>%s<v>%s</v></c>' % (ref, attrs, f_, vv)
        L.x[nom] = re.sub(r'<c r="([A-Z]+\d+)"([^>/]*)>(<f(?:\s[^>]*?)?(?:/>|>.*?</f>))(?:<v>.*?</v>)?</c>', rep, x, flags=re.S)
    L.guardar(f); shutil.rmtree(tmp)
    return cambios_v


if __name__ == "__main__":
    f = sys.argv[1]
    L = Libro(f); hojas = cambios(L); L.guardar(f)
    print("celdas recalculadas:", recalcular(f, hojas))
