"""Excel aparte con 6 hojas del metrado vigente: mismo formato, formulas reemplazadas por sus valores
(las hojas de origen no van en este libro)."""
import zipfile, re, sys, html, posixpath
import openpyxl

src, calc, dst = sys.argv[1:4]
KEEP = ['RESUMEN', 'DESAGREGADO TAPA REGISTRO', 'ACU CANALETAS', 'ACU TAPA REGISTRO', 'COLECTOR INSUMOS', 'COLECTOR REGISTROS Y TAPAS']
z = zipfile.ZipFile(src); F = {n: z.read(n) for n in z.namelist()}; infos = {i.filename: i for i in z.infolist()}
vals = openpyxl.load_workbook(calc, data_only=True)

w = F['xl/workbook.xml'].decode()
sheets = re.findall(r'<sheet name="([^"]*)" sheetId="(\d+)"(?: state="\w+")? r:id="([^"]+)"/>', w)
rels = F['xl/_rels/workbook.xml.rels'].decode()
target = {rid: 'xl/' + t for rid, t in re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels)}
info = {html.unescape(n): (sid, rid) for n, sid, rid in sheets}
old_index = {html.unescape(n): i for i, (n, _, _) in enumerate(sheets)}

def a_valor(xml, ws):
    def rep(m):
        cell = m.group(0); ref = m.group(1)
        if '<f' not in cell: return cell
        s = re.search(r' s="(\d+)"', cell); s = s.group(0) if s else ''
        v = ws[ref].value
        if v is None: return '<c r="%s"%s/>' % (ref, s)
        if isinstance(v, bool): return '<c r="%s"%s t="b"><v>%d</v></c>' % (ref, s, v)
        if isinstance(v, (int, float)): return '<c r="%s"%s><v>%s</v></c>' % (ref, s, repr(v))
        if hasattr(v, 'toordinal'):
            import datetime
            d = (v - datetime.datetime(1899, 12, 30)).days if isinstance(v, datetime.datetime) else (v - datetime.date(1899, 12, 30)).days
            return '<c r="%s"%s><v>%d</v></c>' % (ref, s, d)
        return '<c r="%s"%s t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, s, html.escape(str(v), quote=False))
    return re.sub(r'<c r="([A-Z]+\d+)"[^>]*?(?:/>|>.*?</c>)', rep, xml, flags=re.S)

keep_parts = set()
def agregar(part):
    if part in keep_parts or part not in F: return
    keep_parts.add(part)
    rp = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
    if rp in F:
        keep_parts.add(rp)
        for t, mode in re.findall(r'Target="([^"]+)"(?: TargetMode="(\w+)")?', F[rp].decode()):
            if mode != 'External': agregar(posixpath.normpath(posixpath.join(posixpath.dirname(part), t)))

nuevas = []; dn = []
for k, nombre in enumerate(KEEP):
    sid, rid = info[nombre]; part = target[rid]
    F[part] = a_valor(F[part].decode(), vals[nombre]).encode()
    agregar(part)
    nuevas.append('<sheet name="%s" sheetId="%s" r:id="%s"/>' % (html.escape(nombre), sid, rid))
    for m in re.finditer(r'<definedName name="(_xlnm\.Print_(?:Area|Titles))" localSheetId="%d">(.*?)</definedName>' % old_index[nombre], w):
        dn.append('<definedName name="%s" localSheetId="%d">%s</definedName>' % (m.group(1), k, m.group(2)))
w = re.sub(r'<sheets>.*?</sheets>', '<sheets>%s</sheets>' % ''.join(nuevas), w, flags=re.S)
w = re.sub(r'<definedNames>.*?</definedNames>', ('<definedNames>%s</definedNames>' % ''.join(dn)) if dn else '', w, flags=re.S)
w = re.sub(r' activeTab="\d+"', '', w); w = re.sub(r' firstSheet="\d+"', '', w)
F['xl/workbook.xml'] = w.encode()
kept_rids = {info[n][1] for n in KEEP}
def rel_ok(m):
    rid = m.group(1)
    return m.group(0) if (rid in kept_rids or 'worksheet"' not in m.group(0)) else ''
rels = re.sub(r'<Relationship Id="([^"]+)"[^>]*/>', rel_ok, rels)
F['xl/_rels/workbook.xml.rels'] = rels.encode()
for t, mode in re.findall(r'Target="([^"]+)"(?: TargetMode="(\w+)")?', rels):
    if mode != 'External': agregar(posixpath.normpath(posixpath.join('xl', t)))

quitar = [n for n in F if n.startswith(('xl/worksheets/', 'xl/drawings/', 'xl/comments', 'xl/tables/', 'xl/printerSettings/', 'xl/media/', 'xl/threadedComments', 'xl/persons'))
          and n not in keep_parts]
for n in quitar: del F[n]
ct = F['[Content_Types].xml'].decode()
ct = re.sub(r'<Override PartName="/([^"]+)"[^>]*/>', lambda m: m.group(0) if m.group(1) in F else '', ct)
F['[Content_Types].xml'] = ct.encode()
app = F['docProps/app.xml'].decode()
app = re.sub(r'<HeadingPairs>.*?</HeadingPairs>', '<HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Hojas de c&#225;lculo</vt:lpstr></vt:variant><vt:variant><vt:i4>%d</vt:i4></vt:variant></vt:vector></HeadingPairs>' % len(KEEP), app, flags=re.S)
app = re.sub(r'<TitlesOfParts>.*?</TitlesOfParts>', '<TitlesOfParts><vt:vector size="%d" baseType="lpstr">%s</vt:vector></TitlesOfParts>' % (len(KEEP), ''.join('<vt:lpstr>%s</vt:lpstr>' % html.escape(n) for n in KEEP)), app, flags=re.S)
F['docProps/app.xml'] = app.encode()
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as o:
    for n in z.namelist():
        if n in F: o.writestr(infos[n], F[n])
print('ok, quitadas', len(quitar), 'partes')
