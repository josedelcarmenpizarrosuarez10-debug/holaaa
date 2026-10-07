"""Une las 7 partidas de registros (01.04.04.05.01 a .07) en una sola por und y agrega la hoja
DESAGREGADO TAPA REGISTRO. Edicion XML sobre el metrado vigente; solo se tocan las celdas indicadas."""
import zipfile, re, sys, html, json

src, dst = sys.argv[1], sys.argv[2]
cache = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
z = zipfile.ZipFile(src); F = {n: z.read(n) for n in z.namelist()}; infos = z.infolist()
NOMBRE = "TAPA DE REGISTRO 0.68x0.68 C/MARCO Y CONTRAMARCO"
RT = "'COLECTOR REGISTROS Y TAPAS'!"; CA = "'COLECTOR ACERO'!"; CP = "'COLECTOR PARAMETROS'!"; P = "'PLANILLA GENERAL DE METRADOS'!"
HOJA = "DESAGREGADO TAPA REGISTRO"

ss = F['xl/sharedStrings.xml'].decode()
sis = re.findall(r'<si>.*?</si>', ss, re.S)
def txt(i): return html.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', sis[i], re.S)))
def sid(t):
    for i, s in enumerate(sis):
        if re.fullmatch(r'<si><t(?: xml:space="preserve")?>(.*?)</t></si>', s, re.S) and txt(i) == t: return i
    sis.append('<si><t xml:space="preserve">%s</t></si>' % html.escape(t, quote=False)); return len(sis) - 1
def setcell(x, ref, inner, t='s', style=None):
    m = re.search(r'<c r="%s"( s="\d+")?( t="\w+")?(/>|>.*?</c>)' % ref, x); assert m, ref
    s = ' s="%s"' % style if style is not None else (m.group(1) or '')
    rep = '<c r="%s"%s/>' % (ref, s) if inner is None else '<c r="%s"%s%s>%s</c>' % (ref, s, ' t="%s"' % t if t else '', inner)
    return x[:m.start()] + rep + x[m.end():]
def sstr(x, ref, t, style=None): return setcell(x, ref, '<v>%d</v>' % sid(t), 's', style)
def form(x, ref, f, v=None, style=None, tipo=None):
    return setcell(x, ref, '<f>%s</f>%s' % (html.escape(f, quote=False), '' if v is None else '<v>%s</v>' % v), tipo, style)

# ---------------- PLANILLA (sheet2)
x = F['xl/worksheets/sheet2.xml'].decode()
x = sstr(x, 'B312', NOMBRE); x = form(x, 'K312', 'SUM(J313:J315)', 10)
det = [(313, 'Registros en la losa del colector (RS-01 a RS-07)', 'SUM(%sE11:E17)' % RT, 7),
       (314, 'Caja de llegada CL (1 registro)', '+%sE10' % RT, 1),
       (315, 'Caja de caida CC (2 registros)', '+%sE18' % RT, 2)]
for r, t, f, v in det:
    x = setcell(x, 'A%d' % r, None, style=28); x = sstr(x, 'B%d' % r, t, 28); x = setcell(x, 'C%d' % r, '<v>1</v>', None, 29)
    for c in 'DEFGHI': x = setcell(x, '%s%d' % (c, r), None, style=29)
    x = form(x, 'J%d' % r, f, v, 29); x = setcell(x, 'K%d' % r, None, style=29); x = setcell(x, 'L%d' % r, None, style=28)
for r in (316, 317, 318):
    x = setcell(x, 'A%d' % r, None, style=28)
    for c in 'CDEFGHIJK': x = setcell(x, '%s%d' % (c, r), None, style=29)
    x = setcell(x, 'L%d' % r, None, style=28)
x = sstr(x, 'B316', 'Cada tapa incluye: contramarco L 2"x2"x3/16" con 8 anclajes, marco L 1 1/2"x1 1/2"x1/8", tapa de concreto armado 0.68 x 0.68 x 0.08 con parrilla y asas, refuerzo de borde y pintura', 28)
x = form(x, 'B317', '"Totales para "&K312&" tapas: angulos "&TEXT(%sE25,"0.00")&" kg; concreto "&TEXT(%sE27,"0.00")&" m3; acero "&TEXT(%sI41,"0.00")&" kg; pintura "&TEXT(%sE28,"0.00")&" m2"' % (RT, RT, CA, RT),
         None, 28, 'str')
x = sstr(x, 'B318', 'Desagregado por componente: ver hoja %s' % HOJA, 28)
for r, h in ((312, 31), (313, 15.5), (314, 15.5), (315, 15.5), (316, 46.5), (317, 31), (318, 15.5)):
    x = re.sub(r'(<row r="%d"[^>]*?) ht="[\d.]+"' % r, r'\1 ht="%s"' % h, x)
F['xl/worksheets/sheet2.xml'] = x.encode()

# ---------------- RESUMEN (sheet1): fila 71 = partida unica; se quitan 72-77; 78-80 suben a 72-74
x = F['xl/worksheets/sheet1.xml'].decode()
x = sstr(x, 'B71', NOMBRE)
x = re.sub(r'<row r="7[2-7]"[^>]*>.*?</row>', '', x)
def rowfix(m):
    r = int(m.group(1)); body = m.group(0)
    if r < 78: return body
    body = re.sub(r'<row r="%d"' % r, '<row r="%d"' % (r - 6), body)
    return re.sub(r'(<c r="[A-Z]+)%d"' % r, lambda k: '%s%d"' % (k.group(1), r - 6), body)
x = re.sub(r'<row r="(\d+)"[^>]*>.*?</row>', rowfix, x)
x = x.replace('<dimension ref="A1:E80"/>', '<dimension ref="A1:E74"/>')
F['xl/worksheets/sheet1.xml'] = x.encode()

# ---------------- COLECTOR INSUMOS (sheet22): referencias a la fuente
x = F['xl/worksheets/sheet22.xml'].decode()
x = x.replace("<f>'PLANILLA GENERAL DE METRADOS'!K314</f>", "<f>%sE25</f>" % html.escape(RT, quote=False))
x = x.replace("<f>'PLANILLA GENERAL DE METRADOS'!K318</f>", "<f>%sE28</f>" % html.escape(RT, quote=False))
x = sstr(x, 'B60', '01.04.04.05.01 TAPA DE REGISTRO: angulos (marco y contramarco)')
x = sstr(x, 'B64', '01.04.04.05.01 TAPA DE REGISTRO: pintura en angulos')
F['xl/worksheets/sheet22.xml'] = x.encode()

# ---------------- ACU TAPA REGISTRO (sheet23): enlaces a la fuente y textos
x = F['xl/worksheets/sheet23.xml'].decode()
fuentes = {'K312': RT + 'E23', 'K313': RT + 'E24', 'K314': RT + 'E25', 'K315': RT + 'E26', 'K316': RT + 'E27', 'K317': CA + 'I41', 'K318': RT + 'E28'}
for k, v in fuentes.items():
    x = x.replace("<f>+'PLANILLA GENERAL DE METRADOS'!%s</f>" % k, "<f>+%s</f>" % html.escape(v, quote=False))
for a, b in (("armado con los componentes que este metrado lleva por separado (partidas 01.04.04.05.01 a 01.04.04.05.07)",
              "partida 01.04.04.05.01 del metrado; componentes desagregados en la hoja DESAGREGADO TAPA REGISTRO"),
             ("01.04.04.05.01 a 01.04.04.05.07 (contramarco, marco, angulos, tapa, concreto, acero y pintura)",
              "01.04.04.05.01 TAPA DE REGISTRO (10 und); componentes en la hoja DESAGREGADO TAPA REGISTRO"),
             ('>PARTIDA DEL METRADO<', '>COMPONENTE<'), ('>Agrupa del metrado<', '>Partida del metrado<')):
    assert a in x, a[:40]; x = x.replace(a, b)
for i, c in enumerate(('contramarco', 'marco', 'angulos', 'tapa', 'concreto', 'acero', 'pintura')):
    x = x.replace('>01.04.04.05.0%d<' % (i + 1), '>%s<' % c)
F['xl/worksheets/sheet23.xml'] = x.encode()

# ---------------- hoja nueva DESAGREGADO TAPA REGISTRO (sheet25)
G2, G4, TC, UN, HD, SEC, TOT, TW, NOTE = 208, 361, 200, 203, 199, 353, 213, 364, 351
rows, heights, merges = {}, {}, []
def put(r, col, kind, val, s): rows.setdefault(r, {})[col] = (kind, val, s)
def T(r, col, t, s=TW): put(r, col, 's', t, s)
def N(r, col, v, s): put(r, col, 'n', v, s)
def Fm(r, col, f, s): put(r, col, 'f', f, s)
def E(r, col, s): put(r, col, 'e', None, s)
COLS = 'ABCDEFG'
T(1, 'A', 'DESAGREGADO DE LA PARTIDA 01.04.04.05.01 - ' + NOMBRE, 349)
for c in 'BCDEF': E(1, c, 348)
E(1, 'G', 346); merges.append('A1:G1'); heights[1] = 30
for r, lab, ref, hgt in ((2, 1, 'B4', 25), (3, 3, 'B5', 59), (4, 5, 'B6', 25), (5, 7, 'B7', 25)):
    put(r, 'A', 'si', lab, 345); E(r, 'B', 346); Fm(r, 'C', '+RESUMEN!' + ref, 350 if r == 5 else 347)
    for c in 'DEF': E(r, c, 348)
    E(r, 'G', 346); merges += ['A%d:B%d' % (r, r), 'C%d:G%d' % (r, r)]; heights[r] = hgt
T(7, 'A', 'La partida se mide por unidad de registro (tapa con marco y contramarco). Esta hoja muestra donde va cada registro y lo que '
          'lleva cada uno; las cantidades salen de las hojas COLECTOR PARAMETROS, COLECTOR REGISTROS Y TAPAS y COLECTOR ACERO (lamina DP-06B).', NOTE)
for c in 'BCDEFG': E(7, c, 212)
merges.append('A7:G7'); heights[7] = 48
# A. ubicacion
r = 9; T(r, 'A', 'A. UBICACION DE LOS REGISTROS', SEC); [E(r, c, SEC) for c in 'BCDEFG']; merges.append('A9:G9')
r = 10
for c, h in zip(COLS, ('N°', 'REGISTRO', 'PROGRESIVA', 'UBICACION', '', 'CANT. (und)', 'SUSTENTO')): T(r, c, h, HD)
merges.append('D10:E10'); heights[10] = 22
for i in range(9):
    rr = 11 + i; s = 10 + i
    N(rr, 'A', i + 1, TC); Fm(rr, 'B', '+%sB%d' % (RT, s), TC); Fm(rr, 'C', '+%sC%d' % (RT, s), TC)
    Fm(rr, 'D', '+%sD%d' % (RT, s), TW); E(rr, 'E', TW); merges.append('D%d:E%d' % (rr, rr))
    Fm(rr, 'F', '+%sE%d' % (RT, s), G2); Fm(rr, 'G', '+%sF%d' % (RT, s), TC); heights[rr] = 31
rr = 20; T(rr, 'B', 'TOTAL DE REGISTROS (und de la partida)', SEC); [E(rr, c, 212) for c in 'ACDEG']; Fm(rr, 'F', 'SUM(F11:F19)', TOT); RTOT = 'F20'
# B. componentes
r = 22; T(r, 'A', 'B. COMPONENTES DE UNA TAPA DE REGISTRO Y TOTAL DE LA PARTIDA', SEC); [E(r, c, SEC) for c in 'BCDEFG']; merges.append('A22:G22')
r = 23
for c, h in zip(COLS, ('N°', 'COMPONENTE', 'UND', 'POR REGISTRO', 'N° REGISTROS', 'TOTAL', 'SUSTENTO')): T(r, c, h, HD)
heights[23] = 22
n = '$' + RTOT[0] + '$' + RTOT[1:]
comp = [
    ('ANGULOS METALICOS', None),
    ('Contramarco: angulo L 2"x2"x3/16", 4 x 0.70 = 2.80 m x 3.63 kg/m', 'kg', '%sC36*%sC38' % (CP, CP), 'lamina DP-06B; esquinas a 45 grados soldadas'),
    ('Marco de tapa: angulo L 1 1/2"x1 1/2"x1/8", 4 x 0.68 = 2.72 m x 1.83 kg/m', 'kg', '%sC37*%sC39' % (CP, CP), 'lamina DP-06B; sirve de encofrado de la tapa'),
    ('SUB', 'kg', 'angulos'),
    ('CONCRETO', None),
    ("Tapa de concreto f'c=210: 0.68 x 0.68 x 0.08", 'm3', '%sC33*%sC33*%sC34' % (CP, CP, CP), 'lamina DP-06B'),
    ('SUB', 'm3', 'concreto'),
    ('ACERO DE REFUERZO fy=4200', None),
    ('Parrilla de la tapa: 7 + 7 barras 3/8" @0.10, L = 0.62', 'kg', '%sU34/%sF34' % (CA, CA), 'COLECTOR ACERO fila 34'),
    ('Asas de la tapa: 2 barras 3/8" liso, desarrollo 0.40', 'kg', '%sU35/%sF35' % (CA, CA), 'COLECTOR ACERO fila 35'),
    ('Anclajes del contramarco: 8 barras 3/8", L = 0.20', 'kg', '%sU36/%sF36' % (CA, CA), 'COLECTOR ACERO fila 36'),
    ('Refuerzo de borde de la abertura: 8 barras 1/2", L = 1.40', 'kg', '%sU33/%sF33' % (CA, CA), 'COLECTOR ACERO fila 33'),
    ('SUB', 'kg', 'acero'),
    ('PINTURA', None),
    ('Anticorrosivo y esmalte en angulos: 2.80 x 0.203 + 2.72 x 0.152', 'm2', '%sC36*%sC40+%sC37*%sC41' % (CP, CP, CP, CP), '4 caras de cada angulo'),
    ('SUB', 'm2', 'pintura')]
r = 24; g0 = None; subs = {}
k = 0
for it in comp:
    if it[1] is None:
        E(r, 'A', 198); T(r, 'B', it[0], SEC); [E(r, c, SEC) for c in 'CDEFG']; merges.append('B%d:G%d' % (r, r)); g0 = r + 1
    elif it[0] == 'SUB':
        E(r, 'A', 198); T(r, 'B', 'Subtotal ' + it[2], 353); T(r, 'C', it[1], UN)
        Fm(r, 'D', 'SUM(D%d:D%d)' % (g0, r - 1), 365); E(r, 'E', 212); Fm(r, 'F', 'SUM(F%d:F%d)' % (g0, r - 1), TOT); E(r, 'G', 212); subs[it[2]] = r
    else:
        k += 1; nom, u, f, sus = it
        N(r, 'A', k, TC); T(r, 'B', nom, TW); T(r, 'C', u, UN); Fm(r, 'D', f, G4); Fm(r, 'E', '+' + n, TC)
        Fm(r, 'F', 'D%d*E%d' % (r, r), G4); T(r, 'G', sus, TW); heights[r] = 31
    r += 1
# C. control
r += 1; T(r, 'A', 'C. CONTROL CON EL METRADO DE LOS COMPONENTES (hojas del colector)', SEC); [E(r, c, SEC) for c in 'BCDEFG']; merges.append('A%d:G%d' % (r, r)); r += 1
for c, h in zip(COLS, ('', 'COMPONENTE', 'UND', '', 'ESTA HOJA', 'HOJA DEL COLECTOR', 'CONTROL')): T(r, c, h, HD)
r += 1
for nom, u, key, srcf in (('Angulos (marco y contramarco)', 'kg', 'angulos', RT + 'E25'), ('Concreto en tapas', 'm3', 'concreto', RT + 'E27'),
                          ('Acero en tapas, bordes y anclajes', 'kg', 'acero', CA + 'I41'), ('Pintura en angulos', 'm2', 'pintura', RT + 'E28')):
    E(r, 'A', 198); T(r, 'B', nom, TW); T(r, 'C', u, UN); E(r, 'D', 212); Fm(r, 'E', '+F%d' % subs[key], G4); Fm(r, 'F', '+' + srcf, G4)
    Fm(r, 'G', 'IF(ABS(E%d-F%d)<0.001,"CONFORME","REVISAR")' % (r, r), TC); r += 1
LAST = r - 1

def cell(ref, k, v, s):
    if k == 'e': return '<c r="%s" s="%d"/>' % (ref, s)
    if k == 'n': return '<c r="%s" s="%d"><v>%s</v></c>' % (ref, s, repr(v))
    if k == 'si': return '<c r="%s" s="%d" t="s"><v>%d</v></c>' % (ref, s, v)
    if k == 's': return '<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, s, html.escape(v, quote=False))
    cv = cache.get(HOJA + '!' + ref)
    if isinstance(cv, str): return '<c r="%s" s="%d" t="str"><f>%s</f><v>%s</v></c>' % (ref, s, html.escape(v, quote=False), html.escape(cv, quote=False))
    return '<c r="%s" s="%d"><f>%s</f>%s</c>' % (ref, s, html.escape(v, quote=False), '' if cv is None else '<v>%s</v>' % repr(cv))
xr = ['<row r="%d" spans="1:7" ht="%s" customHeight="1">%s</row>' % (rr, heights.get(rr, 20), ''.join(cell('%s%d' % (c, rr), *rows[rr][c]) for c in COLS if c in rows[rr])) for rr in sorted(rows)]
ws = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
      '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
      '<sheetPr><pageSetUpPr fitToPage="1"/></sheetPr><dimension ref="A1:G%d"/>' % LAST +
      '<sheetViews><sheetView showGridLines="0" workbookViewId="0"/></sheetViews><sheetFormatPr defaultRowHeight="14.5"/>'
      '<cols><col min="1" max="1" width="6" customWidth="1"/><col min="2" max="2" width="58" customWidth="1"/><col min="3" max="3" width="12" customWidth="1"/>'
      '<col min="4" max="6" width="14" customWidth="1"/><col min="7" max="7" width="40" customWidth="1"/></cols>'
      '<sheetData>%s</sheetData>' % ''.join(xr) +
      '<mergeCells count="%d">%s</mergeCells>' % (len(merges), ''.join('<mergeCell ref="%s"/>' % m for m in merges)) +
      '<pageMargins left="0.5" right="0.5" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>'
      '<pageSetup paperSize="9" orientation="portrait" fitToWidth="1" fitToHeight="0"/></worksheet>')
F['xl/worksheets/sheet25.xml'] = ws.encode()

w = F['xl/workbook.xml'].decode()
assert 'RESUMEN!$A$1:$D$80' in w
w = w.replace('RESUMEN!$A$1:$D$80', 'RESUMEN!$A$1:$D$74')
w = w.replace('<sheet name="ACU CANALETAS" sheetId="24" r:id="rIdACU2"/>', '<sheet name="ACU CANALETAS" sheetId="24" r:id="rIdACU2"/><sheet name="%s" sheetId="25" r:id="rIdDES1"/>' % HOJA)
w = w.replace('</definedNames>', '<definedName name="_xlnm.Print_Area" localSheetId="24">\'%s\'!$A$1:$G$%d</definedName></definedNames>' % (HOJA, LAST))
assert HOJA in w
F['xl/workbook.xml'] = w.encode()
F['xl/_rels/workbook.xml.rels'] = F['xl/_rels/workbook.xml.rels'].decode().replace('</Relationships>', '<Relationship Id="rIdDES1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet25.xml"/></Relationships>').encode()
ct = F['[Content_Types].xml'].decode(); a = '<Override PartName="/xl/worksheets/sheet24.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
assert a in ct; F['[Content_Types].xml'] = ct.replace(a, a + a.replace('sheet24', 'sheet25')).encode()
app = F['docProps/app.xml'].decode()
app = app.replace('<vt:i4>24</vt:i4>', '<vt:i4>25</vt:i4>', 1)
app = re.sub(r'<vt:vector size="(\d+)" baseType="lpstr">', lambda m: '<vt:vector size="%d" baseType="lpstr">' % (int(m.group(1)) + 1), app, 1)
app = app.replace('<vt:lpstr>ACU CANALETAS</vt:lpstr>', '<vt:lpstr>ACU CANALETAS</vt:lpstr><vt:lpstr>%s</vt:lpstr>' % HOJA, 1)
F['docProps/app.xml'] = app.encode()
w = F['xl/workbook.xml'].decode()
F['xl/workbook.xml'] = w.replace('<calcPr calcId="191029"/>', '<calcPr calcId="191029" fullCalcOnLoad="1"/>').encode()

head = re.search(r'<sst[^>]*>', ss).group(0)
F['xl/sharedStrings.xml'] = (ss[:ss.index(head)] + re.sub(r'uniqueCount="\d+"', 'uniqueCount="%d"' % len(sis), head) + ''.join(sis) + '</sst>').encode()
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as o:
    for i in infos: o.writestr(i, F[i.filename])
    o.writestr('xl/worksheets/sheet25.xml', F['xl/worksheets/sheet25.xml'])
print('ok', LAST)
