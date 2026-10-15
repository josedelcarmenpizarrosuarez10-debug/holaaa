"""CAR Varones (CUI 2705619), parte B: copia a la planilla de Varones las hojas de analisis del Hogar de Refugio (CUI 2675514)
con sus formatos, y enlaza cada formula a las celdas equivalentes de Varones:
  ACU TAPA REGISTRO, ACU CANALETAS, DESAGREGADO TAPA REGISTRO (11 registros), ACU JUNTA DILATACION, ACU JUNTA CAJA CL,
  DESAGREGADO LLORADEROS (34 tramos), COSTO HORA HOMBRE 2026 y ACU LLORADEROS.
Requiere la parte A (planilla_como_refugio.py): COLECTOR INSUMOS con el mismo orden de filas que el Refugio.
Los estilos de celda (fuentes, rellenos, bordes y formatos numericos) se copian al libro de Varones; los textos se copian tal cual.
Uso: python3 herramientas/varones/portar_hojas_v.py <planilla_refugio.xlsx> <planilla_varones.xlsx>
"""
import sys, os, re, html
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); sys.path.insert(0, HERR)
from angulo_contramarco_refugio import Libro, recalcular
from acu_juntas_refugio import agregar_hoja

RT, CP, CA, CI, CJ, MC, PG, ML, DL = ("'COLECTOR REGISTROS Y TAPAS'", "'COLECTOR PARAMETROS'", "'COLECTOR ACERO'", "'COLECTOR INSUMOS'",
                                      "'COLECTOR JUNTAS Y EMPALMES'", "'METRADO CANALETAS'", "'PLANILLA GENERAL DE METRADOS'", "'METRADO LLORADEROS'",
                                      "'DESAGREGADO LLORADEROS'")


# ===================================================================== estilos
class Estilos:
    def __init__(self, LR, LV):
        self.R = LR.F["xl/styles.xml"].decode(); self.V = LV.F["xl/styles.xml"].decode(); self.LV = LV; self.cache = {}
        self.Rp = {k: self._lista(self.R, k) for k in ("fonts", "fills", "borders", "cellXfs")}
        self.Rnf = dict(re.findall(r'<numFmt numFmtId="(\d+)" formatCode="([^"]*)"/>', self.R))

    @staticmethod
    def _bloque(s, k):
        m = re.search(r"<%s[^>]*>(.*?)</%s>" % (k, k), s, re.S); return m
    def _lista(self, s, k):
        tag = {"fonts": "font", "fills": "fill", "borders": "border", "cellXfs": "xf"}[k]
        m = self._bloque(s, k)
        return re.findall(r"<%s(?: [^>]*)?(?:/>|>.*?</%s>)" % (tag, tag), m.group(1), re.S)

    def _agregar(self, k, item):
        lst = self._lista(self.V, k)
        if item in lst: return lst.index(item)
        m = self._bloque(self.V, k)
        nuevo = m.group(1) + item
        cab = re.match(r"<%s[^>]*>" % k, self.V[m.start():]).group(0)
        cab2 = re.sub(r'count="\d+"', 'count="%d"' % (len(lst) + 1), cab)
        self.V = self.V[:m.start()] + cab2 + nuevo + "</%s>" % k + self.V[m.end():]
        return len(lst)

    def _numfmt(self, i):
        i = int(i)
        if i < 164: return i
        code = self.Rnf[str(i)]
        vv = dict((c, n) for n, c in re.findall(r'<numFmt numFmtId="(\d+)" formatCode="([^"]*)"/>', self.V))
        if code in vv: return int(vv[code])
        ids = [int(n) for n in re.findall(r'<numFmt numFmtId="(\d+)"', self.V)] or [163]
        nid = max(max(ids), 163) + 1
        if "<numFmts" in self.V:
            m = re.search(r"<numFmts[^>]*>(.*?)</numFmts>", self.V, re.S)
            n = len(re.findall(r"<numFmt ", m.group(1))) + 1
            self.V = self.V[:m.start()] + '<numFmts count="%d">' % n + m.group(1) + '<numFmt numFmtId="%d" formatCode="%s"/>' % (nid, code) + "</numFmts>" + self.V[m.end():]
        else:
            self.V = self.V.replace("<fonts", '<numFmts count="1"><numFmt numFmtId="%d" formatCode="%s"/></numFmts><fonts' % (nid, code), 1)
        return nid

    def mapa(self, s):
        s = int(s)
        if s in self.cache: return self.cache[s]
        xf = self.Rp["cellXfs"][s]
        a = dict(re.findall(r'(\w+)="([^"]*)"', re.match(r"<xf[^>]*?/?>", xf).group(0)))
        a["fontId"] = str(self._agregar("fonts", self.Rp["fonts"][int(a.get("fontId", 0))]))
        a["fillId"] = str(self._agregar("fills", self.Rp["fills"][int(a.get("fillId", 0))]))
        a["borderId"] = str(self._agregar("borders", self.Rp["borders"][int(a.get("borderId", 0))]))
        a["numFmtId"] = str(self._numfmt(a.get("numFmtId", 0))); a["xfId"] = "0"
        cab = "<xf " + " ".join('%s="%s"' % kv for kv in a.items())
        m = re.match(r"<xf[^>]*?(/?)>", xf)
        nuevo = cab + ("/>" if m.group(1) == "/" else ">" + xf[m.end():])
        self.cache[s] = self._agregar("cellXfs", nuevo)
        return self.cache[s]

    def guardar(self): self.LV.F["xl/styles.xml"] = self.V.encode()


# ===================================================================== copia de hojas
def copiar(LR, LV, E, origen, destino, remap=None, textos=None):
    x = LR.hoja(origen)
    x = re.sub(r'(<c r="[A-Z]+\d+"[^>]*?) s="(\d+)"', lambda m: '%s s="%d"' % (m.group(1), E.mapa(m.group(2))), x)
    x = re.sub(r'(<row [^>]*?) s="(\d+)"', lambda m: '%s s="%d"' % (m.group(1), E.mapa(m.group(2))), x)
    x = re.sub(r'(<col [^>]*?) style="(\d+)"', lambda m: '%s style="%d"' % (m.group(1), E.mapa(m.group(2))), x)
    def cad(m):
        si = LR.sis[int(m.group(2))]
        if si not in LV.sis: LV.sis.append(si)
        return '%s<v>%d</v></c>' % (m.group(1), LV.sis.index(si))
    x = re.sub(r'(<c r="[A-Z]+\d+"[^>]*t="s"[^>]*>)<v>(\d+)</v></c>', cad, x)
    if remap:
        def fx(m):
            f = html.unescape(m.group(2)); f2 = remap(f)
            return m.group(1) + html.escape(f2, quote=False) + "</f>"
        x = re.sub(r"(<f[^>]*>)(.*?)</f>", fx, x, flags=re.S)
    x = re.sub(r"(<f[^>]*>.*?</f>)<v>.*?</v>", r"\1<v>0</v>", x, flags=re.S)
    agregar_hoja(LV, destino, x)
    for ref, t in (textos or {}).items():
        LV.texto(destino, ref, t)


def refs(mapa):
    """remap de formulas: mapa = {hoja: funcion(col, fila) -> (col, fila)}."""
    TOK = re.compile(r"('[^']+'|[A-Z][A-Z ]*)!(\$?)([A-Z]+)(\$?)(\d+)")
    def f(form):
        def rep(m):
            h = m.group(1)
            if h not in mapa: return m.group(0)
            c, r = mapa[h](m.group(3), int(m.group(5)))
            return "%s!%s%s%s%d" % (h, m.group(2), c, m.group(4), r)
        return TOK.sub(rep, form)
    return f


def fila(f):
    return lambda c, r: (c, f(r))


def construir(fr, fv):
    LR, LV = Libro(fr), Libro(fv)
    assert "ACU TAPA REGISTRO" not in LV.ruta and LV.leer(CI.strip("'"), "E67") == "Thinner acrilico", "falta la parte A o ya se copio"
    E = Estilos(LR, LV)
    cp = fila(lambda r: r - 2 if 30 <= r <= 41 else r)                       # COLECTOR PARAMETROS: filas 32..41 del Refugio = 30..39
    rt = fila(lambda r: {19: 21}.get(r, r + 2 if 23 <= r <= 28 else r))      # registros: total 19 -> 21; partidas 23..28 -> 25..30
    ca = fila(lambda r: {41: 25}.get(r, r - 16 if 33 <= r <= 36 else r))     # acero de tapas 33..36 -> 17..20; resumen 41 -> 25
    # ---------------- COSTO HORA HOMBRE 2026
    copiar(LR, LV, E, "COSTO HORA HOMBRE 2026", "COSTO HORA HOMBRE 2026")
    # ---------------- ACU TAPA REGISTRO
    copiar(LR, LV, E, "ACU TAPA REGISTRO", "ACU TAPA REGISTRO", refs({RT: rt, CA: ca, CP: cp}),
           {"H16": "Hoja COLECTOR ACERO, filas 17 a 20",
            "C63": "01.04.04.05.01 TAPA DE REGISTRO (11 und); componentes en la hoja DESAGREGADO TAPA REGISTRO"})
    # ---------------- ACU CANALETAS
    copiar(LR, LV, E, "ACU CANALETAS", "ACU CANALETAS",
           refs({MC: fila(lambda r: r + 3 if 45 <= r <= 52 else r), PG: fila(lambda r: r - 24 if 149 <= r <= 152 else r)}),
           {"H%d" % (11 + i): "METRADO CANALETAS F%d" % (48 + i) for i in (0, 1, 2, 4, 5)})
    # ---------------- DESAGREGADO TAPA REGISTRO: 9 registros del Refugio -> 11 de Varones
    D = "DESAGREGADO TAPA REGISTRO"
    copiar(LR, LV, E, D, D, refs({RT: rt, CA: ca, CP: cp}),
           {"G32": "COLECTOR ACERO fila 18", "G33": "COLECTOR ACERO fila 19", "G34": "COLECTOR ACERO fila 20", "G35": "COLECTOR ACERO fila 17"})
    LV.desplazar(D, 20, 60, 2); LV.insertar_copia(D, 19, 20); LV.insertar_copia(D, 19, 21)
    for i in range(11):
        r = 11 + i; rr = 10 + i
        LV.num(D, "A%d" % r, i + 1)
        for c, cc in (("B", "B"), ("C", "C"), ("D", "D"), ("F", "E"), ("G", "F")):
            LV.formula(D, "%s%d" % (c, r), "+%s!%s%d" % (RT, cc, rr))
    LV.formula(D, "F22", "SUM(F11:F21)")
    x = LV.hoja(D)
    x = x.replace("</mergeCells>", '<mergeCell ref="D20:E20"/><mergeCell ref="D21:E21"/></mergeCells>')
    x = re.sub(r'<mergeCells count="(\d+)"', lambda m: '<mergeCells count="%d"' % (int(m.group(1)) + 2), x); LV.x[D] = x
    for c in "BCDFG":                                              # celdas de texto con formula: t="str"
        for r in range(11, 22):
            LV.x[D] = re.sub(r'(<c r="%s%d"[^>]*?) t="n"' % (c, r), r'\1 t="str"', LV.x[D]) if c in "BCDG" else LV.x[D]
    # ---------------- ACU JUNTA DILATACION (seccion de Varones: ancho exterior 0.90, h max 1.17, interior 0.60)
    J = "ACU JUNTA DILATACION"
    copiar(LR, LV, E, J, J, None, {
        "B11": "Perimetro de la seccion en cada junta: 2 x 0.90 + 2 x (0.15 + 1.17 + 0.10)",
        "B13": "Area de tecnopor por junta: seccion 0.90 x 1.42 menos el hueco 0.60 x 1.17",
        "B18": "Longitud sellada por junta: caras interiores 2 x 1.17 + 0.60 y cara superior 0.90"})
    LV.formula(J, "D13", "0.90*(0.15+1.17+0.10)-0.60*1.17"); LV.formula(J, "D18", "2*1.17+0.60+0.90")
    # ---------------- ACU JUNTA CAJA CL (misma seccion; una junta en el contacto con el muro este de la CL)
    K = "ACU JUNTA CAJA CL"
    copiar(LR, LV, E, J, K, refs({CJ: fila(lambda r: {11: 16, 12: 17}.get(r, r)), CI: fila(lambda r: {71: 75, 72: 76}.get(r, r))}), {
        "A1": "ANALISIS DE COSTO UNITARIO - JUNTA E=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CAJA CL",
        "A7": "Partida de Delphin 01.04.04.06.02 JUNTA E=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CAJA CL (metrado 01.04.04.06.02, hoja COLECTOR JUNTAS Y "
              "EMPALMES). Se mide por metro de junta a lo largo del perimetro de la seccion, en el contacto del colector con el muro este de la caja CL. Cantidades de la "
              "lamina DD-03: plancha de tecnopor de 1\" en toda la seccion y sellador asfaltico 1\" x 2\" (RC-250 + arena) en las caras interiores y en la cara superior. "
              "A ambos lados del colector hay terreno natural: no lleva junta longitudinal. Celda amarilla = dato; verde = formula. Precios sin IGV.",
        "B11": "Perimetro de la seccion en el contacto con la caja CL: 2 x 0.90 + 2 x (0.15 + 1.17 + 0.10)",
        "H11": "COLECTOR JUNTAS Y EMPALMES fila 16; DD-03", "B12": "Numero de juntas en el contacto con la caja CL", "H12": "COLECTOR JUNTAS Y EMPALMES fila 16",
        "B13": "Area de tecnopor de la junta: seccion 0.90 x 1.42 menos el hueco 0.60 x 1.17",
        "B18": "Longitud sellada: caras interiores 2 x 1.17 + 0.60 y cara superior 0.90",
        "H23": "COLECTOR INSUMOS fila 75", "H24": "COLECTOR INSUMOS fila 76",
        "C27": "01.04.04.06.02 JUNTA E=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CAJA CL", "C28": "01.04.04.06.02 (hoja COLECTOR JUNTAS Y EMPALMES)"})
    LV.formula(K, "D11", "+%s!E16" % CJ); LV.formula(K, "D12", "+%s!D16" % CJ)
    LV.formula(K, "D13", "0.90*(0.15+1.17+0.10)-0.60*1.17"); LV.formula(K, "D18", "2*1.17+0.60+0.90")
    LV.formula(K, "C30", "+%s!F17" % CJ)
    # ---------------- DESAGREGADO LLORADEROS: 12 tramos del Refugio -> 34 de Varones (METRADO LLORADEROS filas 7 a 40)
    G = "DESAGREGADO LLORADEROS"; n = 34; extra = n - 12
    copiar(LR, LV, E, G, G)
    LV.desplazar(G, 23, 80, extra)
    for k in range(extra): LV.insertar_copia(G, 22, 23 + k)
    for i in range(n):
        r = 11 + i; rr = 7 + i
        LV.num(G, "A%d" % r, i + 1)
        LV.formula(G, "B%d" % r, "%s!B%d&\": \"&%s!C%d" % (ML, rr, ML, rr)); LV.formula(G, "C%d" % r, "%s!D%d" % (ML, rr))
        for c, cc in (("D", "E"), ("E", "F"), ("F", "G")): LV.formula(G, "%s%d" % (c, r), "%s!%s%d" % (ML, cc, rr))
        LV.x[G] = re.sub(r'(<c r="[BC]%d"[^>]*?) t="n"' % r, r'\1 t="str"', LV.x[G])
    rt_ = 11 + n
    LV.formula(G, "D%d" % rt_, "SUM(D11:D%d)" % (rt_ - 1)); LV.formula(G, "F%d" % rt_, "SUM(F11:F%d)" % (rt_ - 1))
    # ---------------- ACU LLORADEROS
    copiar(LR, LV, E, "ACU LLORADEROS", "ACU LLORADEROS", refs({DL: fila(lambda r: r + extra if r >= 23 else r)}),
           {"H11": "DESAGREGADO LLORADEROS fila %d" % (23 + extra), "H12": "DESAGREGADO LLORADEROS fila %d (DL-02 B)" % (37 + extra),
            "H14": "DESAGREGADO LLORADEROS fila %d (DL-02 A)" % (40 + extra), "H15": "DESAGREGADO LLORADEROS fila %d (DL-01 etapa 3)" % (41 + extra),
            "H17": "DESAGREGADO LLORADEROS fila %d (DL-02)" % (42 + extra)})
    E.guardar()
    LV.guardar(fv)
    return recalcular(fv, list(LV.ruta))


if __name__ == "__main__":
    print("celdas recalculadas:", construir(sys.argv[1], sys.argv[2]))
