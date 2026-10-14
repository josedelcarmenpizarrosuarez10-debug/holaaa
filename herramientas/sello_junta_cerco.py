"""Hogar de Refugio (CUI 2675514): la partida 01.04.04.06.02 tambien lleva sellador asfaltico (tecnopor de 1" + sello
asfaltico RC-250 con arena de 1" x 2" en la cara expuesta, como la junta de dilatacion del colector).
Renombra la partida y agrega en COLECTOR INSUMOS las filas 74 (sello) y 75 (operario), copiando el formato de las filas
69 y 70. Edicion directa del XML: conserva formato e imagenes; no cambia ninguna cantidad de metrado.
"""
import sys, zipfile, re, html, shutil

NOMBRES = {
    'JUNTA E=1" CON TECNOPOR ENTRE COLECTOR Y CERCO PERIMETRICO': 'JUNTA E=1" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO',
    'JUNTA e=1" CON TECNOPOR ENTRE COLECTOR Y CERCO PERIMETRICO': 'JUNTA e=1" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO',
    '01.04.04.06.02 JUNTA e=1" CON TECNOPOR ENTRE COLECTOR Y CERCO PERIMETRICO': '01.04.04.06.02 JUNTA e=1" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO',
}
SELLO, OPER = 0.0013, 0.05       # m3 de mezcla por m (1" x 2") ; hh de operario por m (sellado ~160 m/dia)


def hoja(files, nombre):
    wb = files["xl/workbook.xml"].decode(); rels = files["xl/_rels/workbook.xml.rels"].decode()
    rid = re.search(r'<sheet name="%s"[^>]*r:id="([^"]+)"' % re.escape(nombre), wb).group(1)
    t = (re.search(r'Id="%s"[^>]*Target="([^"]+)"' % rid, rels) or re.search(r'Target="([^"]+)"[^>]*Id="%s"' % rid, rels)).group(1)
    return "xl/" + t.lstrip("/").replace("xl/", "")


def main(f):
    z = zipfile.ZipFile(f); files = {n: z.read(n) for n in z.namelist()}; z.close()
    ss = files["xl/sharedStrings.xml"].decode(); n = 0
    def rep(m):
        nonlocal n
        t = html.unescape("".join(re.findall(r"<t[^>]*>(.*?)</t>", m.group(0), re.S)))
        if t not in NOMBRES: return m.group(0)
        n += 1; return '<si><t xml:space="preserve">%s</t></si>' % html.escape(NOMBRES[t], quote=False)
    files["xl/sharedStrings.xml"] = re.sub(r"<si>.*?</si>", rep, ss, flags=re.S).encode()
    p = hoja(files, "COLECTOR INSUMOS"); x = files[p].decode()
    if '<row r="74"' in x: raise SystemExit("las filas 74/75 ya existen")
    d72 = float(re.search(r'<c r="D72"[^>]*>.*?<v>([^<]+)</v>', x, re.S).group(1))
    r69 = re.search(r'<row r="69".*?</row>', x, re.S).group(0); r70 = re.search(r'<row r="70".*?</row>', x, re.S).group(0)
    def nueva(row, a, b, g):
        row = row.replace('r="%d"' % a, 'r="%d"' % b)
        row = re.sub(r'r="([A-Z]+)%d"' % a, lambda m: 'r="%s%d"' % (m.group(1), b), row)
        row = row.replace("G%d*$D$68" % a, "G%d*$D$72" % b)
        row = re.sub(r'(<c r="G%d"[^>]*>)<v>[^<]*</v>' % b, lambda m: m.group(1) + "<v>%s</v>" % g, row)
        row = re.sub(r'(<c r="H%d"[^>]*><f[^>]*>[^<]*</f>)<v>[^<]*</v>' % b, lambda m: m.group(1) + "<v>%s</v>" % (g * d72), row)
        return row
    r73 = re.search(r'<row r="73".*?</row>', x, re.S)
    x = x[:r73.end()] + nueva(r69, 69, 74, SELLO) + nueva(r70, 70, 75, OPER) + x[r73.end():]
    x = re.sub(r'<dimension ref="A1:([A-Z]+)73"/>', r'<dimension ref="A1:\g<1>75"/>', x)
    files[p] = x.encode()
    tmp = f + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        zo.writestr("[Content_Types].xml", files.pop("[Content_Types].xml"))
        for k, v in files.items(): zo.writestr(k, v)
    shutil.move(tmp, f)
    print("nombres:", n, "| filas 74-75 agregadas | metrado", d72, "m -> sello", round(SELLO * d72, 4), "m3, operario", round(OPER * d72, 2), "hh")


if __name__ == "__main__":
    main(sys.argv[1])
