"""CAR Mujeres (Wilma, CUI 2717013): agrega a la planilla general vigente solo los 4 items de la canaleta de los techos de las
bancas de jardineria tipo 01 (canaleta, tapa lateral, soporte y boquilla), con una hoja nueva de metrado.

- Hoja nueva METRADO CANALETA BANCAS (formato de METRADO CANALETAS), despues de METRADO CANALETAS.
- PLANILLA GENERAL DE METRADOS: subtitulo 1.4.4.5.4 RED DE RECOLECCION TECHO DE BANCAS DE JARDINERIA despues de ACCESORIOS.
- RESUMEN: el mismo subtitulo y los 4 items antes de 1.4.4.6 COLECTOR PLUVIAL FRONTAL; ademas la fila del CODO DESAGUE PVC
  4" x 45 (PLANILLA 1.4.4.5.3.2, de METRADO MONTANTES) que faltaba, con la numeracion de ACCESORIOS igual a la PLANILLA.
No cambia ningun otro valor: las filas siguientes solo bajan y sus referencias se corrigen.
Uso: python3 herramientas/mujeres/bancas_en_planilla_m.py
"""
import sys, os, re, html, shutil, zipfile
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.dirname(AQUI))
from angulo_contramarco_refugio import Libro, recalcular

ENT = os.path.join(RAIZ, "insumos", "wilma", "vigente_09-10-2026", "METRADO_DRENAJE_PLUVIAL_CAR_MUJERES_09-10-2026.xlsx")
SAL = os.path.join(RAIZ, "entregables_mujeres", "METRADO_DRENAJE_PLUVIAL_CAR_MUJERES_09-10-2026_CON_BANCAS.xlsx")
RES, PG, MC, NB = "RESUMEN", "PLANILLA GENERAL DE METRADOS", "METRADO CANALETAS", "METRADO CANALETA BANCAS"
N_TECHOS = 16
SUB = "RED DE RECOLECCION TECHO DE BANCAS DE JARDINERIA"
# (descripcion, und, columna total en la hoja nueva, fila de PLANILLA que se copia, fila de RESUMEN que se copia)
ITEMS = [("CANALETA DE PLANCHA DE ALUZINC e=0.50mm, SECCION INTERIOR 0.18 m (ANCHO) x 0.20 m (ALTO)", "m", "E", 148, 39),
         ("TAPA LATERAL DE PLANCHA DE ALUZINC e=0.50mm P/CANALETA", "und", "G", 150, 41),
         ("SOPORTE DE PLATINA F°G° 1\" x 1/8\" P/CANALETA", "und", "I", 149, 40),
         ("BOQUILLA DE PLANCHA DE ALUZINC e=0.50mm P/CONEXION DE CANALETA A TUBERIA PVC 4\"", "und", "K", 151, 42)]
DP, DR = 6, 5            # filas que bajan en PLANILLA (desde la 165) y en RESUMEN (desde la 52)


def hoja_bancas(L):
    """XML de la hoja nueva con los estilos de METRADO CANALETAS."""
    pl = L.hoja(MC); filas, merges = [], []
    def c(ref, st, v=None):
        if v is None: return '<c r="%s" s="%d"/>' % (ref, st)
        if isinstance(v, str) and v.startswith("="): return '<c r="%s" s="%d"><f>%s</f><v>0</v></c>' % (ref, st, html.escape(v[1:], quote=False))
        if isinstance(v, str): return '<c r="%s" s="%d" t="s"><v>%d</v></c>' % (ref, st, L.sid(v))
        return '<c r="%s" s="%d"><v>%s</v></c>' % (ref, st, repr(v))
    def fila(r, ht, celdas):
        filas.append('<row r="%d" spans="2:11" ht="%s" customHeight="1">%s</row>' % (r, ht, "".join(c("%s%d" % (t[0], r), *t[1:]) for t in celdas)))
    def copia(r):
        filas.append(re.search(r'<row r="%d"[ >].*?</row>' % r, pl, re.S).group(0))
    fila(2, 24, [("B", 215, "METRADO DE CANALETA DE TECHO - BANCAS DE JARDINERIA TIPO 01")] + [(k, 216) for k in "CDEFGHIJK"]); merges.append("B2:K2")
    for r in (3, 4, 5, 6): copia(r); merges.append("C%d:K%d" % (r, r))
    fila(8, 33, [("B", 219, "CANALETA DE PLANCHA DE ALUZINC e=0.50mm - TECHO DE BANCAS A UNA AGUA (UN TRAMO POR TECHO, SIN UNIONES)")]
         + [(k, 213) for k in "CDEFGHIJ"] + [("K", 214)]); merges.append("B8:K8")
    fila(9, 42, [("B", 217, "EDIFICACIÓN"), ("C", 217, "N° DE TECHOS"), ("D", 217, "CANALETA 0.18 x 0.20 m"), ("E", 214),
                 ("F", 217, "TAPA LATERAL"), ("G", 214), ("H", 217, "SOPORTE PLATINA F°G° 1\" x 1/8\""), ("I", 214),
                 ("J", 217, "BOQUILLA A TUBERIA PVC Ø4\""), ("K", 214)])
    merges += ["B9:B10", "C9:C10", "D9:E9", "F9:G9", "H9:I9", "J9:K9"]
    fila(10, 31, [("B", 220), ("C", 220), ("D", 94, "LONGITUD (m)"), ("E", 94, "TOTAL (m)")] +
         [(k, 94, t) for k, t in zip("FGHIJK", ("CANTIDAD", "TOTAL (und)") * 3)])
    fila(11, 23.25, [("B", 97, "Bancas tipo 01"), ("C", 88, N_TECHOS), ("D", 71, 2.0), ("E", 192, "=C11*D11"),
                     ("F", 88, "=$F$19"), ("G", 193, "=C11*F11"), ("H", 88, "=$F$20"), ("I", 193, "=C11*H11"),
                     ("J", 88, "=$F$21"), ("K", 193, "=C11*J11")])
    fila(12, 23.25, [("B", 100, "TOTAL"), ("C", 100, "=SUM(C11:C11)"), ("D", 100), ("E", 194, "=SUM(E11:E11)"), ("F", 100),
                     ("G", 100, "=SUM(G11:G11)"), ("H", 100), ("I", 100, "=SUM(I11:I11)"), ("J", 100), ("K", 100, "=SUM(K11:K11)")])
    fila(14, 15.5, [("B", 211, "PARÁMETROS DE CÁLCULO - CANALETA DE BANCAS")] + [(k, 207) for k in "CDEFGHIJ"] + [("K", 208)]); merges.append("B14:K14")
    fila(15, 15.5, [("B", 210, "DESCRIPCIÓN"), ("C", 207), ("D", 207), ("E", 208), ("F", 195, "VALOR"), ("G", 195, "UNIDAD"),
                    ("H", 210, "CRITERIO"), ("I", 207), ("J", 207), ("K", 208)]); merges += ["B15:E15", "H15:K15"]
    par = [("Ancho interior de canaleta", 0.18, "m", 196, "Detalle de banca tipo 01"),
           ("Altura interior de canaleta", 0.20, "m", 196, "Detalle de banca tipo 01"),
           ("Espesor de plancha de aluzinc", 0.5, "mm", 198, "Canaleta, tapas y boquilla"),
           ("Tapas laterales por canaleta", 2, "und", 199, "Una en cada extremo del tramo"),
           ("Soportes por canaleta", 2, "und", 199, "A 0.40 m de cada extremo"),
           ("Boquillas por canaleta", 1, "und", 199, "Una salida a la tubería PVC Ø4\"")]
    for r, (t, v, u, st, cr) in enumerate(par, 16):
        fila(r, 18, [("B", 209, t), ("C", 207), ("D", 207), ("E", 208), ("F", st, v), ("G", 197, u), ("H", 209, cr), ("I", 207), ("J", 207), ("K", 208)])
        merges += ["B%d:E%d" % (r, r), "H%d:K%d" % (r, r)]
    i, j = pl.index("<sheetData>"), pl.index("</sheetData>")
    cab = re.sub(r' xr:uid="\{[^}]+\}"', "", pl[:i])
    cab = re.sub(r'<dimension ref="[^"]+"/>', '<dimension ref="B2:K21"/>', cab)
    cab = re.sub(r"<sheetViews>.*?</sheetViews>", '<sheetViews><sheetView showGridLines="0" view="pageBreakPreview" zoomScaleNormal="100" '
                 'zoomScaleSheetLayoutView="100" workbookViewId="0"><selection activeCell="C11" sqref="C11"/></sheetView></sheetViews>', cab, flags=re.S)
    cola = pl[j:]
    cola = re.sub(r"<mergeCells.*?</mergeCells>", '<mergeCells count="%d">%s</mergeCells>' % (len(merges), "".join('<mergeCell ref="%s"/>' % m for m in merges)), cola, flags=re.S)
    cola = re.sub(r' r:id="rId\d+"', "", cola).replace("<legacyDrawing/>", "")
    return cab + "<sheetData>" + "".join(filas) + cola


def agregar_hoja_despues(L, nombre, xml, despues):
    n = max(int(re.search(r"sheet(\d+)\.xml", v).group(1)) for v in L.ruta.values()) + 1; ruta = "xl/worksheets/sheet%d.xml" % n
    wb = L.F["xl/workbook.xml"].decode(); rels = L.F["xl/_rels/workbook.xml.rels"].decode(); ct = L.F["[Content_Types].xml"].decode()
    sid = max(int(v) for v in re.findall(r'sheetId="(\d+)"', wb)) + 1; rid = "rId%d" % (max(int(v) for v in re.findall(r'Id="rId(\d+)"', rels)) + 1)
    hojas = re.findall(r'<sheet name="([^"]+)"', wb); pos = [html.unescape(h) for h in hojas].index(despues) + 1
    for m in reversed(list(re.finditer(r'localSheetId="(\d+)"', wb))):          # las hojas que siguen corren un lugar
        k = int(m.group(1))
        if k >= pos: wb = wb[:m.start(1)] + str(k + 1) + wb[m.end(1):]
    m = re.search(r'<sheet name="%s"[^>]*/>' % re.escape(html.escape(despues, quote=True)), wb)
    wb = wb[:m.end()] + '<sheet name="%s" sheetId="%d" r:id="%s"/>' % (nombre, sid, rid) + wb[m.end():]
    wb = wb.replace("</definedNames>", "<definedName name=\"_xlnm.Print_Area\" localSheetId=\"%d\">'%s'!$B$2:$K$21</definedName></definedNames>" % (pos, nombre))
    rels = rels.replace("</Relationships>", '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/></Relationships>' % (rid, n))
    ct = ct.replace("</Types>", '<Override PartName="/%s" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>' % ruta)
    L.F["xl/workbook.xml"], L.F["xl/_rels/workbook.xml.rels"], L.F["[Content_Types].xml"] = wb.encode(), rels.encode(), ct.encode()
    L.F[ruta] = xml.encode(); zi = zipfile.ZipInfo(ruta, date_time=L.infos[0].date_time); zi.compress_type = zipfile.ZIP_DEFLATED
    L.infos.append(zi); L.ruta[nombre] = ruta


def sin_calcchain(L):
    """Excel reconstruye la cadena de calculo al abrir; se quita porque las filas cambian de lugar."""
    L.infos = [i for i in L.infos if i.filename != "xl/calcChain.xml"]; L.F.pop("xl/calcChain.xml", None)
    L.F["[Content_Types].xml"] = re.sub(r'<Override PartName="/xl/calcChain.xml"[^>]*/>', "", L.F["[Content_Types].xml"].decode()).encode()
    L.F["xl/_rels/workbook.xml.rels"] = re.sub(r'<Relationship [^>]*calcChain[^>]*/>', "", L.F["xl/_rels/workbook.xml.rels"].decode()).encode()


def altura(L, nom, r, ht):
    L.x[nom] = re.sub(r'(<row r="%d"[^>]*? ht=")[\d.]+"' % r, r'\g<1>%s"' % ht, L.hoja(nom), count=1)


def main():
    shutil.copy(ENT, SAL); L = Libro(SAL)
    assert L.leer(PG, "B159") == "ACCESORIOS" and L.leer(PG, "A165") == "1.4.4.6" and L.leer(RES, "A52") == "1.4.4.6", "la planilla no es la esperada"
    sin_calcchain(L)
    agregar_hoja_despues(L, NB, hoja_bancas(L), MC)
    # ---- PLANILLA GENERAL: filas 164 (vacia) a 170 (vacia); lo de la 165 en adelante baja 6 filas
    L.desplazar(PG, 165, 320, DP)
    L.insertar_copia(PG, 158, 164); L.insertar_copia(PG, 159, 165)
    L.texto(PG, "A165", "1.4.4.5.4"); L.texto(PG, "B165", SUB)
    for k, (d, u, col, rp, _) in enumerate(ITEMS):
        r = 166 + k; L.insertar_copia(PG, rp, r)
        L.texto(PG, "A%d" % r, "1.4.4.5.4.%d" % (k + 1)); L.texto(PG, "B%d" % r, d); L.texto(PG, "L%d" % r, u)
        L.formula(PG, "K%d" % r, "+'%s'!%s12" % (NB, col))
    L.x[PG] = L.x[PG].replace('<dimension ref="A2:L320"/>', '<dimension ref="A2:L%d"/>' % (320 + DP))
    L.x[PG] = re.sub(r'<mergeCells count="(\d+)">', lambda m: '<mergeCells count="%d"><mergeCell ref="B165:L165"/>' % (int(m.group(1)) + 1), L.x[PG])
    altura(L, PG, 166, 62)
    # ---- RESUMEN: filas 52 a 56; lo de la 52 en adelante baja 5 filas
    L.desplazar(RES, 52, 79, DR)
    L.insertar_copia(RES, 48, 52); L.texto(RES, "A52", "1.4.4.5.4"); L.texto(RES, "B52", SUB)
    for k, (d, u, col, _, rr) in enumerate(ITEMS):
        r = 53 + k; L.insertar_copia(RES, rr, r)
        L.texto(RES, "A%d" % r, "1.4.4.5.4.%d" % (k + 1)); L.texto(RES, "B%d" % r, d); L.texto(RES, "C%d" % r, u)
        L.formula(RES, "D%d" % r, "+'%s'!K%d" % (PG, 166 + k))
    altura(L, RES, 53, 29.5)
    def mov(m):                                              # referencias del RESUMEN a filas de PLANILLA que bajaron
        r = int(m.group(2)); return m.group(1) + str(r + DP if r >= 165 else r)
    partes = re.split(r'(<row r="5[3-6]"[ >].*?</row>)', L.x[RES], flags=re.S)       # las filas nuevas ya apuntan bien
    for i, p in enumerate(partes):
        if not re.match(r'<row r="5[3-6]"', p):
            partes[i] = re.sub(r"((?:&apos;|')PLANILLA GENERAL DE METRADOS(?:&apos;|')!\$?[A-Z]+\$?)(\d+)", mov, p)
    L.x[RES] = "".join(partes).replace('<dimension ref="A1:E79"/>', '<dimension ref="A1:E%d"/>' % (79 + DR))
    # ---- RESUMEN: codo 45 (fila 50) que faltaba; colgador y abrazadera toman la numeracion de la PLANILLA
    L.desplazar(RES, 50, 79 + DR, 1); L.insertar_copia(RES, 49, 50)
    assert L.leer(PG, "A161") == "1.4.4.5.3.2" and "45" in L.leer(PG, "B161")
    L.texto(RES, "A50", "1.4.4.5.3.2"); L.texto(RES, "B50", L.leer(PG, "B161")); L.formula(RES, "D50", "+'%s'!K161" % PG)
    L.texto(RES, "A51", "1.4.4.5.3.3"); L.texto(RES, "A52", "1.4.4.5.3.4")
    L.x[RES] = L.x[RES].replace('<dimension ref="A1:E%d"/>' % (79 + DR), '<dimension ref="A1:E%d"/>' % (80 + DR))
    wb = L.F["xl/workbook.xml"].decode()
    wb = wb.replace("'PLANILLA GENERAL DE METRADOS'!$A$1:$L$320", "'PLANILLA GENERAL DE METRADOS'!$A$1:$L$%d" % (320 + DP))
    wb = wb.replace("RESUMEN!$A$1:$D$79", "RESUMEN!$A$1:$D$%d" % (80 + DR))
    L.F["xl/workbook.xml"] = wb.encode()
    L.guardar(SAL)
    print("valores recalculados:", recalcular(SAL, [RES, PG, NB])); print(SAL)


if __name__ == "__main__":
    main()
