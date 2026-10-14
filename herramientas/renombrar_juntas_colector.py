"""Hogar de Refugio (Mujeres Violentadas, CUI 2675514): renombra las dos partidas de juntas del colector y cambia el sello
elastomerico por sellador asfaltico (tecnopor en toda la seccion + sello asfaltico superficial, EG-2013 510.02 c y 438.02 e 3),
editando el XML de la planilla para conservar formato e imagenes. No cambia ninguna cantidad de metrado.
Uso: python3 herramientas/renombrar_juntas_colector.py <xlsx>
"""
import sys, zipfile, re, html, shutil, os

NOMBRES = {
    'JUNTA DE DILATACION E=1" CON TECNOPOR Y SELLADOR ELASTOMERICO': 'JUNTA DE DILATACION E=1" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR',
    'JUNTA E=1" CON TECNOPOR ENTRE COLECTOR Y PISO ADYACENTE': 'JUNTA E=1" CON TECNOPOR ENTRE COLECTOR Y CERCO PERIMETRICO',
    'JUNTA DE DILATACION e=1" CON TECNOPOR Y SELLADOR ELASTOMERICO (perimetro = 2 x ancho exterior + 2 x (e fondo + h max + e losa))':
        'JUNTA DE DILATACION e=1" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR (perimetro = 2 x ancho exterior + 2 x (e fondo + h max + e losa))',
    'JUNTA DE TECNOPOR e=1" ENTRE COLECTOR, CERCO Y PISO ADYACENTE': 'JUNTA e=1" CON TECNOPOR ENTRE COLECTOR Y CERCO PERIMETRICO',
    '01.04.04.06.01 JUNTA DE DILATACION e=1" CON SELLADOR': '01.04.04.06.01 JUNTA DE DILATACION e=1" CON TECNOPOR Y SELLADOR ASFALTICO',
    '01.04.04.06.02 JUNTA DE TECNOPOR e=1"': '01.04.04.06.02 JUNTA e=1" CON TECNOPOR ENTRE COLECTOR Y CERCO PERIMETRICO',
    'Sello elastomerico de poliuretano': 'Sellador asfaltico: asfalto liquido RC-250 + arena gruesa (sello de 1" x 2")',
}
NOTA = ("(tecnopor + sellador elastomerico)",
        "(tecnopor de 1\" en todo el perimetro + sellador asfaltico RC-250 con arena de 1\" x 2\" en la cara expuesta, EG-2013 secc. 510.02 c y 438.02 e 3)")
SELLO_M3 = round(0.0254 * 0.0508, 4)          # m3 de mezcla de sello por m de junta (1" x 2")


def main(f):
    z = zipfile.ZipFile(f); files = {n: z.read(n) for n in z.namelist()}; z.close()
    ss = files["xl/sharedStrings.xml"].decode()
    n = 0
    def rep(m):
        nonlocal n
        si = m.group(0); t = html.unescape("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S)))
        nuevo = NOMBRES.get(t)
        if nuevo is None and NOTA[0] in t: nuevo = t.replace(*NOTA)
        if nuevo is None: return si
        n += 1
        return '<si><t xml:space="preserve">%s</t></si>' % html.escape(nuevo, quote=False)
    ss = re.sub(r"<si>.*?</si>", rep, ss, flags=re.S)
    files["xl/sharedStrings.xml"] = ss.encode()
    # insumo del sello en COLECTOR INSUMOS: unidad m3 y cantidad por m de junta
    wb = files["xl/workbook.xml"].decode(); rels = files["xl/_rels/workbook.xml.rels"].decode()
    rid = re.search(r'<sheet name="COLECTOR INSUMOS"[^>]*r:id="([^"]+)"', wb).group(1)
    tgt = (re.search(r'Id="%s"[^>]*Target="([^"]+)"' % rid, rels) or re.search(r'Target="([^"]+)"[^>]*Id="%s"' % rid, rels)).group(1)
    p = "xl/" + tgt.lstrip("/").replace("xl/", "")
    x = files[p].decode()
    d68 = float(re.search(r'<c r="D68"[^>]*>.*?<v>([^<]+)</v>', x, re.S).group(1))
    x, k1 = re.subn(r'<c r="F69"( s="\d+")?[^>]*?(/>|>.*?</c>)', lambda m: '<c r="F69"%s t="inlineStr"><is><t>m3</t></is></c>' % (m.group(1) or ""), x, count=1, flags=re.S)
    x, k2 = re.subn(r'(<c r="G69"[^>]*>)(?:<f[^>]*>.*?</f>)?<v>[^<]*</v>', lambda m: m.group(1) + "<v>%s</v>" % SELLO_M3, x, count=1, flags=re.S)
    x, k3 = re.subn(r'(<c r="H69"[^>]*><f[^>]*>[^<]*</f>)<v>[^<]*</v>', lambda m: m.group(1) + "<v>%s</v>" % (SELLO_M3 * d68), x, count=1, flags=re.S)
    files[p] = x.encode()
    wbx = re.sub(r"<calcPr([^>]*?)/>", lambda m: "<calcPr%s fullCalcOnLoad=\"1\"/>" % m.group(1).replace(' fullCalcOnLoad="1"', ""), wb, count=1)
    files["xl/workbook.xml"] = wbx.encode()
    tmp = f + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        zo.writestr("[Content_Types].xml", files.pop("[Content_Types].xml"))
        for k, v in files.items(): zo.writestr(k, v)
    shutil.move(tmp, f)
    print("textos cambiados:", n, "| celdas del sello:", k1, k2, k3, "| sello m3/m:", SELLO_M3, "x", d68, "m")


if __name__ == "__main__":
    main(sys.argv[1])
