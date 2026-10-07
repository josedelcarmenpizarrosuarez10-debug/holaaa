"""Agrega la hoja 'ACU CANALETAS' (4 analisis de costos unitarios) al final del metrado vigente.
Edicion XML; no toca las demas hojas. Reusa los estilos agregados con la hoja ACU TAPA REGISTRO."""
import zipfile, re, sys, html, json

src, dst = sys.argv[1], sys.argv[2]
cache = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
z = zipfile.ZipFile(src); F = {n: z.read(n) for n in z.namelist()}; infos = z.infolist()
SHEET = 'ACU CANALETAS'
P = "'PLANILLA GENERAL DE METRADOS'!"; MC = "'METRADO CANALETAS'!"

st = F['xl/styles.xml'].decode()
assert '<cellXfs count="366">' in st, 'estilos de la hoja ACU TAPA REGISTRO no encontrados'
G2, G4, Y2, Y3, Y4, TW, TC, UN, HD, SEC, TOT, NOTE = 208, 361, 362, 202, 363, 364, 200, 203, 199, 353, 213, 351

rows, heights, merges = {}, {}, []
def put(r, col, kind, val, s): rows.setdefault(r, {})[col] = (kind, val, s)
def T(r, col, t, s=TW): put(r, col, 's', t, s)
def N(r, col, v, s): put(r, col, 'n', v, s)
def Fm(r, col, f, s): put(r, col, 'f', f, s)
def E(r, col, s): put(r, col, 'e', None, s)
COLS = 'ABCDEFGH'

# ---------- encabezado
T(1, 'A', 'ANALISIS DE COSTOS UNITARIOS - CANALETAS DE TECHO DE PLANCHA GALVANIZADA', 349)
for c in 'BCDEFG': E(1, c, 348)
E(1, 'H', 346); merges.append('A1:H1'); heights[1] = 27
for r, lab, ref, hgt in ((2, 1, 'B4', 25), (3, 3, 'B5', 59), (4, 5, 'B6', 25), (5, 7, 'B7', 25)):
    put(r, 'A', 'si', lab, 345); E(r, 'B', 346); Fm(r, 'C', '+RESUMEN!' + ref, 350 if r == 5 else 347)
    for c in 'DEFG': E(r, c, 348)
    E(r, 'H', 346); merges += ['A%d:B%d' % (r, r), 'C%d:H%d' % (r, r)]; heights[r] = hgt
T(7, 'A', "Analisis de las partidas 01.04.03.05.01.03 a 01.04.03.05.01.06 (red de recoleccion de techo). Las cantidades de insumos "
          "salen de los parametros de la hoja METRADO CANALETAS (seccion 0.25 x 0.20, pestana 0.05, plancha e=0.9 mm, soportes @0.60). "
          "Celda amarilla = dato (cuadrilla, rendimiento, aporte o precio); verde = formula. Precios sin IGV, referenciales: "
          "al pasar a Delphin rigen los de la base de precios del presupuesto.", NOTE)
for c in 'BCDEFGH': E(7, c, 212)
merges.append('A7:H7'); heights[7] = 66

# ---------- datos de calculo (enlazados al metrado)
r = 9
T(r, 'A', 'DATOS DE CALCULO (de la hoja METRADO CANALETAS y de catalogo)', SEC); [E(r, c, SEC) for c in 'BCDEFGH']; merges.append('A%d:H%d' % (r, r))
r += 1
for c, h in zip(COLS, ('N°', 'DATO', 'UND', 'VALOR', '', '', '', 'SUSTENTO')): T(r, c, h, HD)
heights[r] = 22
datos = [('fondo', 'Fondo interior de la canaleta', 'm', MC + 'F45', 'METRADO CANALETAS F45'),
         ('alto', 'Altura interior de la canaleta', 'm', MC + 'F46', 'METRADO CANALETAS F46'),
         ('pest', 'Pestana superior (cada lado)', 'm', MC + 'F47', 'METRADO CANALETAS F47'),
         ('des', 'Desarrollo de plancha por metro de canaleta', 'm2/m', MC + 'F48', 'fondo + 2 alturas + 2 pestanas'),
         ('esp', 'Espesor de plancha galvanizada', 'mm', MC + 'F49', 'METRADO CANALETAS F49'),
         ('sep', 'Separacion de soportes', 'm', MC + 'F50', 'METRADO CANALETAS F50'),
         ('pplan', 'Peso de la plancha galvanizada', 'kg/m2', 'D{esp}*7.85+0.3', 'espesor x 7.85 kg/m2 por mm + zinc (0.3 kg/m2)'),
         ('lpl', 'Largo de la plancha comercial (1.22 x 2.44)', 'm', 2.44, 'catalogo; la canaleta se fabrica en tramos de 2.44 m'),
         ('tras', 'Traslape entre tramos', 'm', 0.05, 'criterio de obra (remachado y sellado)'),
         ('lsop', 'Desarrollo de la platina de un soporte', 'm', 'D{fondo}+2*D{alto}+2*0.10', 'abraza la canaleta (fondo + 2 lados) + 2 orejas de fijacion de 0.10'),
         ('pplat', 'Peso de la platina 1" x 1/8"', 'kg/m', 0.633, '25.4 x 3.18 mm x 7.85 = 0.633 kg/m'),
         ('lbar', 'Largo de la platina comercial', 'm', 6.0, 'catalogo')]
R = {}
for i, (k, nom, u, v, sus) in enumerate(datos):
    r += 1; R[k] = r
for i, (k, nom, u, v, sus) in enumerate(datos):
    rr = R[k]
    N(rr, 'A', i + 1, TC); T(rr, 'B', nom, 212); T(rr, 'C', u, UN)
    if isinstance(v, str):
        Fm(rr, 'D', ('+' + v) if '!' in v else v.format(**{kk: R[kk] for kk in R}), G4)
    else:
        N(rr, 'D', v, Y4)
    for c in 'EFG': E(rr, c, 212)
    T(rr, 'H', sus); heights[rr] = 20
D = lambda k: '$D$%d' % R[k]

# ---------- un ACU
FMO = 'CAPECO: costo hora-hombre 2024-2025 llevado al jornal basico 2025-2026'
FMAT = 'Mercado Tarapoto 2026, sin IGV (referencial)'
res = []
def acu(r, num, codigo, nombre, und, metr, rend, cuad, mats, sus_rend):
    T(r, 'A', 'ACU %d: %s %s' % (num, codigo, nombre), SEC); [E(r, c, SEC) for c in 'BCDEFGH']; merges.append('A%d:H%d' % (r, r)); heights[r] = 22
    r += 1
    info = [('Unidad', und, None), ('Metrado', None, '+' + P + metr), ('Rendimiento (%s/dia)' % und, None, rend)]
    ri = {}
    for lab, txt, f in info:
        T(r, 'A', lab, SEC); E(r, 'B', SEC); merges.append('A%d:B%d' % (r, r))
        if txt: T(r, 'C', txt, 212)
        elif isinstance(f, (int, float)): N(r, 'C', f, Y2)
        else: Fm(r, 'C', f, G2)
        E(r, 'D', 212)
        if lab.startswith('Rendimiento'): T(r, 'E', sus_rend, 212); [E(r, c, 212) for c in 'FGH']; merges.append('E%d:H%d' % (r, r))
        else: [E(r, c, 212) for c in 'EFGH']
        ri[lab.split(' ')[0]] = r; heights[r] = 20; r += 1
    rr_rend = ri['Rendimiento']; rr_met = ri['Metrado']
    for c, h in zip(COLS, ('N°', 'RECURSO', 'UND', 'CUADRILLA', 'CANTIDAD', 'PRECIO S/', 'PARCIAL S/', 'SUSTENTO / FUENTE')): T(r, c, h, HD)
    heights[r] = 32; r += 1
    n = 0; sub = {}
    grupos = [('MANO DE OBRA', [(nom, 'hh', ('cuad', cq), pr, FMO) for nom, cq, pr in cuad]),
              ('MATERIALES', mats),
              ('EQUIPOS', [('Herramientas manuales', '%mo', ('pct', 0.05), None, '5 % del costo de mano de obra (hojalateria)')])]
    for gname, items in grupos:
        E(r, 'A', 198); T(r, 'B', gname, SEC); [E(r, c, SEC) for c in 'CDEFGH']; merges.append('B%d:H%d' % (r, r)); r += 1
        g0 = r
        for nom, u, q, pr, fuente in items:
            n += 1; N(r, 'A', n, TC); T(r, 'B', nom, 212); T(r, 'C', u, UN)
            kind, val = q
            if kind == 'cuad':
                N(r, 'D', val, Y3); Fm(r, 'E', 'D%d*8/$C$%d' % (r, rr_rend), G4); N(r, 'F', pr, Y2)
            elif kind == 'pct':
                E(r, 'D', 212); N(r, 'E', val, Y3); Fm(r, 'F', '+G%d' % sub['MANO DE OBRA'], G2)
            elif kind == 'f':
                E(r, 'D', 212); Fm(r, 'E', val, G4); N(r, 'F', pr, Y2)
            else:
                E(r, 'D', 212); N(r, 'E', val, Y4); N(r, 'F', pr, Y2)
            Fm(r, 'G', 'E%d*F%d' % (r, r), G2); T(r, 'H', fuente); heights[r] = 32 if len(fuente) > 48 else 20
            r += 1
        E(r, 'A', 198); T(r, 'B', 'Subtotal ' + gname.lower(), 353); [E(r, c, 212) for c in 'CDEF']
        Fm(r, 'G', 'SUM(G%d:G%d)' % (g0, r - 1), TOT); E(r, 'H', 212); sub[gname] = r; r += 1
    T(r, 'A', 'COSTO UNITARIO DIRECTO (S/ por %s)' % und, SEC); [E(r, c, SEC) for c in 'BCDEF']; merges.append('A%d:F%d' % (r, r))
    Fm(r, 'G', '+' + '+'.join('G%d' % sub[g] for g, _ in grupos), TOT); E(r, 'H', 212); rcu = r; heights[r] = 22; r += 1
    T(r, 'A', 'COSTO DIRECTO DE LA PARTIDA (metrado x costo unitario)', SEC); [E(r, c, SEC) for c in 'BCDEF']; merges.append('A%d:F%d' % (r, r))
    Fm(r, 'G', 'G%d*C%d' % (rcu, rr_met), TOT); E(r, 'H', 212); heights[r] = 22
    res.append((codigo, nombre, und, rr_met, rcu, r))
    return r + 2

r = R[datos[-1][0]] + 3
OP, PE = 30.42, 20.79
PLAN = 26.95; PLAT = 6.36; REM = 0.10; SIL = 21.19; PERNO = 1.02; TORN = 0.25
r = acu(r, 1, '01.04.03.05.01.03', 'CANALETA DE PLANCHA DE ACERO GALVANIZADO e=0.9mm, SECCION 0.25m x 0.20m', 'm', 'K148', 25,
        [('Operario (hojalatero)', 1, OP), ('Peon', 1, PE)],
        [('Plancha de acero galvanizado e=0.9 mm', 'm2', ('f', '%s*(1+%s/%s)*1.05' % (D('des'), D('tras'), D('lpl'))), PLAN,
          'desarrollo x (1 + traslape/2.44) x 1.05 desperdicio; ' + FMAT),
         ('Remache pop 1/8"', 'und', ('f', '2*(%s+2*%s)/0.05/%s' % (D('fondo'), D('alto'), D('lpl'))), REM,
          '2 filas a @0.05 en cada traslape (cada 2.44 m)'),
         ('Sellador de poliuretano (cartucho 300 ml)', 'und', ('f', '(%s+2*%s)/%s/8' % (D('fondo'), D('alto'), D('lpl'))), SIL,
          '1 cartucho = 8 m de cordon de 6 mm; una junta (0.65 m) cada 2.44 m')],
        'fabricacion (corte y doblado en obra), remachado, sellado y colocacion sobre los soportes; cuadrilla 1 op + 1 peon')
r = acu(r, 2, '01.04.03.05.01.04', 'SOPORTE DE PLATINA F°G° 1" x 1/8" P/CANALETA', 'und', 'K149', 40,
        [('Operario', 1, OP), ('Peon', 0.5, PE)],
        [('Platina de fierro galvanizado 1" x 1/8"', 'm', ('f', '%s*1.05' % D('lsop')), PLAT, 'desarrollo del soporte x 1.05 desperdicio; ' + FMAT),
         ('Perno de expansion 1/4" x 2 1/2" con tarugo', 'und', ('v', 2), PERNO, '2 por soporte (una oreja a cada lado)'),
         ('Tornillo autorroscante 1/4" x 3/4" (soporte a canaleta)', 'und', ('v', 2), TORN, '2 por soporte')],
        'corte, doblado en U con orejas, perforado y fijacion al alero o viga; cuadrilla 1 op + 0.5 peon')
r = acu(r, 3, '01.04.03.05.01.05', 'TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA', 'und', 'K150', 30,
        [('Operario (hojalatero)', 1, OP), ('Peon', 0.5, PE)],
        [('Plancha de acero galvanizado e=0.9 mm', 'm2', ('f', '(%s*%s+2*(%s+%s)*0.03)*1.10' % (D('fondo'), D('alto'), D('fondo'), D('alto'))), PLAN,
          'tapa 0.25 x 0.20 + pestana de 0.03 en el contorno, 10 % desperdicio'),
         ('Remache pop 1/8"', 'und', ('v', 6), REM, '6 por tapa'),
         ('Sellador de poliuretano (cartucho 300 ml)', 'und', ('f', '(%s+2*%s)/8' % (D('fondo'), D('alto'))), SIL, 'contorno de la tapa (0.65 m) / 8 m por cartucho')],
        'trazo, corte, doblez de pestanas, remachado y sellado en el extremo de la canaleta; cuadrilla 1 op + 0.5 peon')
r = acu(r, 4, '01.04.03.05.01.06', 'BOQUILLA DE PLANCHA GALVANIZADA P/CONEXION DE CANALETA A MONTANTE Ø4"', 'und', 'K151', 16,
        [('Operario (hojalatero)', 1, OP), ('Peon', 0.5, PE)],
        [('Plancha de acero galvanizado e=0.9 mm', 'm2', ('f', '(PI()*0.1016*0.15+0.20*0.20)*1.15'), PLAN,
          'tubo de 4" x 0.15 m (embone en el montante) + brida 0.20 x 0.20 en el fondo de la canaleta; 15 % desperdicio'),
         ('Remache pop 1/8"', 'und', ('v', 8), REM, '8 por boquilla (brida al fondo de la canaleta)'),
         ('Sellador de poliuretano (cartucho 300 ml)', 'und', ('f', '(4*0.20+PI()*0.1016)/8'), SIL, 'contorno de la brida + embone (1.12 m) / 8 m por cartucho')],
        'corte de la abertura en el fondo, fabricacion del tubo y la brida, remachado, sellado y embone al montante; cuadrilla 1 op + 0.5 peon')

# ---------- resumen
T(r, 'A', 'RESUMEN DE COSTOS DIRECTOS (referencial)', SEC); [E(r, c, SEC) for c in 'BCDEFGH']; merges.append('A%d:H%d' % (r, r)); r += 1
for c, h in zip(COLS, ('', 'PARTIDA', 'UND', 'METRADO', 'C.U. S/', 'PARCIAL S/', '', '')): T(r, c, h, HD)
r += 1; r0 = r
for cod, nom, und, rm, rcu, rct in res:
    T(r, 'A', cod, TW); T(r, 'B', nom, TW); T(r, 'C', und, UN); Fm(r, 'D', '+C%d' % rm, G2); Fm(r, 'E', '+G%d' % rcu, G2); Fm(r, 'F', '+G%d' % rct, G2)
    E(r, 'G', 212); E(r, 'H', 212); heights[r] = 32; r += 1
T(r, 'B', 'TOTAL CANALETAS (costo directo)', 353); [E(r, c, 212) for c in 'ACDEGH']; Fm(r, 'F', 'SUM(F%d:F%d)' % (r0, r - 1), TOT)
LAST = r

def cell(ref, k, v, s):
    if k == 'e': return '<c r="%s" s="%d"/>' % (ref, s)
    if k == 'n': return '<c r="%s" s="%d"><v>%s</v></c>' % (ref, s, repr(v))
    if k == 'si': return '<c r="%s" s="%d" t="s"><v>%d</v></c>' % (ref, s, v)
    if k == 's': return '<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, s, html.escape(v, quote=False))
    cv = cache.get(ref)
    if isinstance(cv, str): return '<c r="%s" s="%d" t="str"><f>%s</f><v>%s</v></c>' % (ref, s, html.escape(v, quote=False), html.escape(cv, quote=False))
    return '<c r="%s" s="%d"><f>%s</f>%s</c>' % (ref, s, html.escape(v, quote=False), '' if cv is None else '<v>%s</v>' % repr(cv))
xr = []
for rr in sorted(rows):
    cs = ''.join(cell('%s%d' % (c, rr), *rows[rr][c]) for c in COLS if c in rows[rr])
    xr.append('<row r="%d" spans="1:8" ht="%s" customHeight="1">%s</row>' % (rr, heights.get(rr, 20), cs))
ws = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
      '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
      '<sheetPr><pageSetUpPr fitToPage="1"/></sheetPr><dimension ref="A1:H%d"/>' % LAST +
      '<sheetViews><sheetView showGridLines="0" workbookViewId="0"/></sheetViews><sheetFormatPr defaultRowHeight="14.5"/>'
      '<cols><col min="1" max="1" width="16" customWidth="1"/><col min="2" max="2" width="48" customWidth="1"/><col min="3" max="3" width="8" customWidth="1"/>'
      '<col min="4" max="7" width="13" customWidth="1"/><col min="8" max="8" width="46" customWidth="1"/></cols>'
      '<sheetData>%s</sheetData>' % ''.join(xr) +
      '<mergeCells count="%d">%s</mergeCells>' % (len(merges), ''.join('<mergeCell ref="%s"/>' % m for m in merges)) +
      '<pageMargins left="0.5" right="0.5" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>'
      '<pageSetup paperSize="9" orientation="portrait" fitToWidth="1" fitToHeight="0"/></worksheet>')
F['xl/worksheets/sheet24.xml'] = ws.encode()
w = F['xl/workbook.xml'].decode()
w = w.replace('<sheet name="ACU TAPA REGISTRO" sheetId="23" r:id="rIdACU1"/>',
              '<sheet name="ACU TAPA REGISTRO" sheetId="23" r:id="rIdACU1"/><sheet name="%s" sheetId="24" r:id="rIdACU2"/>' % SHEET)
w = w.replace('</definedNames>', '<definedName name="_xlnm.Print_Area" localSheetId="23">\'%s\'!$A$1:$H$%d</definedName></definedNames>' % (SHEET, LAST))
F['xl/workbook.xml'] = w.encode()
F['xl/_rels/workbook.xml.rels'] = F['xl/_rels/workbook.xml.rels'].decode().replace('</Relationships>', '<Relationship Id="rIdACU2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet24.xml"/></Relationships>').encode()
F['[Content_Types].xml'] = F['[Content_Types].xml'].decode().replace('<Override PartName="/xl/worksheets/sheet23.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>',
    '<Override PartName="/xl/worksheets/sheet23.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet24.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>').encode()
app = F['docProps/app.xml'].decode()
app = app.replace('<vt:i4>23</vt:i4>', '<vt:i4>24</vt:i4>', 1)
app = re.sub(r'<vt:vector size="(\d+)" baseType="lpstr">', lambda m: '<vt:vector size="%d" baseType="lpstr">' % (int(m.group(1)) + 1), app, 1)
app = app.replace('<vt:lpstr>ACU TAPA REGISTRO</vt:lpstr>', '<vt:lpstr>ACU TAPA REGISTRO</vt:lpstr><vt:lpstr>%s</vt:lpstr>' % SHEET, 1)
F['docProps/app.xml'] = app.encode()
for k in ('xl/workbook.xml', 'xl/_rels/workbook.xml.rels', '[Content_Types].xml'):
    assert b'sheet24' in F[k] or b'ACU CANALETAS' in F[k], k
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as o:
    for i in infos: o.writestr(i, F[i.filename])
    o.writestr('xl/worksheets/sheet24.xml', F['xl/worksheets/sheet24.xml'])
print(json.dumps({'last': LAST, 'res': res}))
