# -*- coding: utf-8 -*-
"""Encabezado y pie de página para las Especificaciones Técnicas del CAR Mujeres (CUI 2717013), en Word.

Estilo de la carátula E del CAR Mujeres (guinda y dorado): escudo del Gobierno Regional, entidad y gerencia, bloque guinda con
"ESPECIFICACIONES TÉCNICAS" y el CUI, filete doble guinda y dorado, y el nombre completo del proyecto en una línea fina; pie con
filete dorado, nombre corto del proyecto y "Página X de Y" en un recuadro guinda. Hoja A4; el cuerpo queda libre para pegar el
texto (o copiar el encabezado a otro Word: doble clic en el encabezado, Ctrl+A, Ctrl+C).

Uso: python3 herramientas/mujeres/encabezado_espec_m.py
Salida: entregables_mujeres/ENCABEZADO_ESPECIFICACIONES_TECNICAS_CAR_MUJERES.docx
"""
import os

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
ESCUDO = os.path.join(RAIZ, 'entregables_varones/figuras_caratula/escudo_gore_san_martin.png')
SALIDA = os.path.join(RAIZ, 'entregables_mujeres/ENCABEZADO_ESPECIFICACIONES_TECNICAS_CAR_MUJERES.docx')
GUINDA, DORADO, GRIS, CREMA = '6B1F2E', 'C5A15A', '595959', 'FBF6F2'
ENTIDAD = 'GOBIERNO REGIONAL SAN MARTÍN'
GERENCIA = 'GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO'
CUI = '2717013'
CORTO = 'CENTRO DE ACOGIDA RESIDENCIAL - MUJERES'
NOMBRE = ('“CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE '
          'PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - MUJERES DISTRITO DE MORALES DE LA PROVINCIA DE SAN MARTÍN DEL DEPARTAMENTO '
          'DE SAN MARTÍN”')


def run(p, txt, tam, neg=False, color=None, esp=0, ital=False, fuente='Arial'):
    r = p.add_run(txt); r.font.size = Pt(tam); r.font.bold = neg; r.font.italic = ital; r.font.name = fuente
    r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), fuente)
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    if esp:
        sp = OxmlElement('w:spacing'); sp.set(qn('w:val'), str(int(esp * 20))); r._element.get_or_add_rPr().append(sp)
    return r


def formato(p, antes=0, despues=0, centro=None, interlineado=1.0):
    pf = p.paragraph_format; pf.space_before = Pt(antes); pf.space_after = Pt(despues); pf.line_spacing = interlineado
    if centro is not None:
        p.alignment = centro


def sombra(celda, color):
    tcPr = celda._tc.get_or_add_tcPr(); s = OxmlElement('w:shd')
    s.set(qn('w:val'), 'clear'); s.set(qn('w:color'), 'auto'); s.set(qn('w:fill'), color); tcPr.append(s)


def sin_bordes(tabla):
    tblPr = tabla._tbl.tblPr; b = OxmlElement('w:tblBorders')
    for lado in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement('w:' + lado); e.set(qn('w:val'), 'nil'); b.append(e)
    tblPr.append(b)


def margenes_celda(celda, izq=0.15, der=0.15, arr=0.05, aba=0.05):
    tcPr = celda._tc.get_or_add_tcPr(); m = OxmlElement('w:tcMar')
    for lado, v in (('left', izq), ('right', der), ('top', arr), ('bottom', aba)):
        e = OxmlElement('w:' + lado); e.set(qn('w:w'), str(int(v * 567))); e.set(qn('w:type'), 'dxa'); m.append(e)
    tcPr.append(m)


def filete(p, color, grosor, espacio=0, lado='bottom'):
    pPr = p._p.get_or_add_pPr(); bdr = pPr.find(qn('w:pBdr'))
    if bdr is None:
        bdr = OxmlElement('w:pBdr'); pPr.append(bdr)
    e = OxmlElement('w:' + lado); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(grosor)); e.set(qn('w:space'), str(espacio))
    e.set(qn('w:color'), color); bdr.append(e)


def campo(p, codigo, tam, color, neg=True):
    for tipo, txt in (('begin', None), (None, codigo), ('separate', None), (None, '1'), ('end', None)):
        r = p.add_run(); r.font.size = Pt(tam); r.font.bold = neg; r.font.name = 'Arial'; r.font.color.rgb = RGBColor.from_string(color)
        if tipo:
            fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), tipo); r._element.append(fc)
        elif txt == codigo:
            it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = ' %s ' % codigo; r._element.append(it)
        else:
            t = OxmlElement('w:t'); t.text = txt; r._element.append(t)


def ancho_columnas(tabla, anchos):
    for gc, w in zip(tabla._tbl.tblGrid.findall(qn('w:gridCol')), anchos):
        gc.set(qn('w:w'), str(int(w * 567)))
    for fila in tabla.rows:
        for c, w in zip(fila.cells, anchos):
            c.width = Cm(w)


def generar():
    d = docx.Document()
    s = d.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin, s.right_margin, s.top_margin, s.bottom_margin = Cm(2.5), Cm(2.0), Cm(4.4), Cm(2.2)
    s.header_distance, s.footer_distance = Cm(0.8), Cm(0.8)
    st = d.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    st.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'Arial')
    util = 21.0 - 2.5 - 2.0

    # ---------------- encabezado
    hd = s.header; p0 = hd.paragraphs[0]; formato(p0); p0._p.getparent().remove(p0._p)
    t = hd.add_table(rows=1, cols=3, width=Cm(util)); sin_bordes(t); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    anchos = (2.0, util - 2.0 - 5.6, 5.6); ancho_columnas(t, anchos)
    c0, c1, c2 = t.rows[0].cells
    for c in (c0, c1, c2):
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p = c0.paragraphs[0]; formato(p, centro=WD_ALIGN_PARAGRAPH.CENTER); p.add_run().add_picture(ESCUDO, height=Cm(1.75))
    margenes_celda(c1, 0.25, 0.2)
    p = c1.paragraphs[0]; formato(p); run(p, ENTIDAD, 11, True, GUINDA, esp=1.2)
    p = c1.add_paragraph(); formato(p, 1); run(p, GERENCIA, 7.5, True, GRIS, esp=0.4)
    p = c1.add_paragraph(); formato(p, 3); run(p, CORTO, 8, True, DORADO, esp=0.6)
    sombra(c2, GUINDA); margenes_celda(c2, 0.25, 0.25, 0.12, 0.12)
    p = c2.paragraphs[0]; formato(p, centro=WD_ALIGN_PARAGRAPH.CENTER); run(p, 'ESPECIFICACIONES', 11, True, 'FFFFFF', esp=0.6)
    p = c2.add_paragraph(); formato(p, 0, 2, WD_ALIGN_PARAGRAPH.CENTER); run(p, 'TÉCNICAS', 11, True, 'FFFFFF', esp=3.2)
    p = c2.add_paragraph(); formato(p, 0, 0, WD_ALIGN_PARAGRAPH.CENTER); filete(p, DORADO, 6, 1, 'top')
    run(p, 'CUI N.° ' + CUI, 8.5, True, DORADO, esp=1)
    p = hd.add_paragraph(); formato(p, 0, 0); filete(p, GUINDA, 18, 0); run(p, '', 2)       # filete doble guinda + dorado
    p = hd.add_paragraph(); formato(p, 0, 0); filete(p, DORADO, 6, 1); run(p, '', 1)
    p = hd.add_paragraph(); formato(p, 3, 0, WD_ALIGN_PARAGRAPH.CENTER)
    run(p, NOMBRE, 6, False, GRIS, ital=True)

    # ---------------- pie
    ft = s.footer; p0 = ft.paragraphs[0]; p0._p.getparent().remove(p0._p)
    p = ft.add_paragraph(); formato(p, 0, 3); filete(p, DORADO, 6, 0); run(p, '', 1)
    t2 = ft.add_table(rows=1, cols=2, width=Cm(util)); sin_bordes(t2); t2.autofit = False; ancho_columnas(t2, (util - 3.4, 3.4))
    a, b = t2.rows[0].cells
    for c in (a, b):
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p = a.paragraphs[0]; formato(p); run(p, 'Especificaciones técnicas  ', 7.5, True, GUINDA); run(p, '|  CAR Mujeres - Morales, San Martín  |  CUI N.° ' + CUI, 7.5, False, GRIS)
    sombra(b, GUINDA); margenes_celda(b, 0.1, 0.1, 0.06, 0.06)
    p = b.paragraphs[0]; formato(p, centro=WD_ALIGN_PARAGRAPH.CENTER)
    run(p, 'Página ', 7.5, False, 'FFFFFF'); campo(p, 'PAGE', 7.5, 'FFFFFF'); run(p, ' de ', 7.5, False, 'FFFFFF'); campo(p, 'NUMPAGES', 7.5, 'FFFFFF')

    # ---------------- cuerpo (libre)
    cp = d.paragraphs[0] if d.paragraphs else d.add_paragraph(); formato(cp, 0, 6); run(cp, '', 10)
    d.core_properties.author = ''; d.core_properties.title = 'Especificaciones técnicas - CAR Mujeres (CUI 2717013)'
    d.save(SALIDA)
    return SALIDA


if __name__ == '__main__':
    print(generar())
