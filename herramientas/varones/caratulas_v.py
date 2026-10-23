# -*- coding: utf-8 -*-
"""Carátulas de los documentos de drenaje pluvial - CAR Varones (CUI 2705619): una carátula por documento, cada una en su Word.

Mismo diseño que las carátulas del CAR Mujeres (mujeres/caratulas_m.py): entidad con el escudo del Gobierno Regional San Martín,
servicio, proyecto con CUI, foto del proyecto, franja granate con el título del documento y bloque de ubicación con la fecha.
Foto del proyecto: la que entregó la usuaria (insumos/katiuska/FOTO_PROYECTO_CAR_VARONES.jpg), en todas las carátulas.
Sin nombre ni CIP del proyectista. Documentos = los de la carpeta de entrega de la usuaria, más la de planos.

Uso: python3 herramientas/varones/caratulas_v.py
Salida: entregables_varones/caratulas/CARATULA_*.docx
"""
import os
import shutil
import sys

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'mujeres'))
import caratulas_m as C  # noqa: E402  (mismas piezas: tablas sin bordes, franja, párrafos)

FOTO = os.path.join(RAIZ, 'insumos/katiuska/FOTO_PROYECTO_CAR_VARONES.jpg')
FIG = os.path.join(RAIZ, 'entregables_varones/figuras_caratula')
ESCUDO = os.path.join(FIG, 'escudo_gore_san_martin.png')        # copia del escudo de las carátulas del CAR Mujeres
SALIDA = os.path.join(RAIZ, 'entregables_varones/caratulas')
PROYECTO = ('“CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO '
            'DE PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES DISTRITO DE MORALES DE LA PROVINCIA DE SAN MARTÍN DEL '
            'DEPARTAMENTO DE SAN MARTÍN”')
CUI = 'CUI N° 2705619'
FECHA = 'OCTUBRE - 2026'
ESP = C.ESPECIALIDAD
DOCUMENTOS = [   # (archivo, título, subtítulo) en el orden de la carpeta de entrega de la usuaria
    ('CARATULA_ESPECIFICACIONES_TECNICAS', 'ESPECIFICACIONES TÉCNICAS', ESP),
    ('CARATULA_MEMORIA_DE_CALCULO_DRENAJE_PLUVIAL', 'MEMORIA DE CÁLCULO', 'DRENAJE PLUVIAL: CANALETAS, MONTANTES Y CUNETAS - ' + ESP),
    ('CARATULA_MEMORIA_DE_CALCULO_COLECTOR', 'MEMORIA DE CÁLCULO', 'COLECTOR PLUVIAL FRONTAL - ' + ESP),
    ('CARATULA_MEMORIA_DESCRIPTIVA', 'MEMORIA DESCRIPTIVA', ESP),
    ('CARATULA_MEMORIA_HIDROLOGICA', 'MEMORIA HIDROLÓGICA', 'HIDROLOGÍA Y DRENAJE PLUVIAL CON COLECTOR FRONTAL - ' + ESP),
    ('CARATULA_METRADOS', 'METRADOS', ESP),
    ('CARATULA_PLANOS', 'PLANOS', 'LÁMINAS DPLV-01 A DPLV-44 - ' + ESP),
]
ANCHO = C.ANCHO


def foto():
    """Foto del proyecto a 16:9, reducida para el Word (el original de la usuaria no se toca)."""
    from PIL import Image
    os.makedirs(FIG, exist_ok=True)
    ruta = os.path.join(FIG, 'foto_proyecto_car_varones.jpg')
    im = Image.open(FOTO).convert('RGB')
    im.thumbnail((1600, 1600)); im.save(ruta, quality=90, optimize=True)
    return ruta


def caratula(d, img, titulo, subtitulo):
    par = C._par
    # ---- entidad con escudo
    tb = d.add_table(rows=1, cols=2); C._sin_bordes(tb); tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    C._anchos(tb, (2.6, ANCHO - 2.6))
    c0, c1 = tb.rows[0].cells
    c0.vertical_alignment = c1.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    par(c0.paragraphs[0]).add_run().add_picture(ESCUDO, width=Cm(2.2))
    par(c1.paragraphs[0], C.ENTIDAD, 17, True, C.GRANATE, centro=False, sep=10)
    C._linea(par(c1, C.GERENCIA, 10.5, True, C.GRIS, centro=False, despues=2, sep=6))
    # ---- servicio y proyecto
    par(d, C.SERVICIO, 11, True, C.GRANATE, antes=26, despues=8)
    par(d, PROYECTO, 10, True, despues=3, esp=1.05)
    par(d, CUI, 11.5, True, C.GRANATE, despues=22)
    # ---- foto del proyecto
    tb = d.add_table(rows=1, cols=1); C._sin_bordes(tb); tb.alignment = WD_TABLE_ALIGNMENT.CENTER; C._anchos(tb, (ANCHO,))
    par(tb.rows[0].cells[0].paragraphs[0]).add_run().add_picture(img, width=Cm(ANCHO))
    par(d, 'Vista del Centro de Acogida Residencial - Varones', 8, False, C.GRIS, cursiva=True, antes=3, despues=22)
    # ---- franja con el título del documento
    tb = d.add_table(rows=1, cols=1); tb.alignment = WD_TABLE_ALIGNMENT.CENTER; C._anchos(tb, (ANCHO,))
    c = tb.rows[0].cells[0]; C._sombra(c, C.GRANATE); C._bordes(c)
    par(c.paragraphs[0], titulo, 26, True, 'FFFFFF', antes=16, despues=4, sep=8)
    lineas = subtitulo.split(' - ')                                  # cada parte del subtítulo en su línea
    for k, t in enumerate(lineas):
        par(c, t, 11, True, 'F2D7DB', despues=16 if k == len(lineas) - 1 else 2, sep=4)
    # ---- ubicación y fecha
    tb = d.add_table(rows=1, cols=2); C._sin_bordes(tb); tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    C._anchos(tb, (ANCHO / 2, ANCHO / 2))
    c0, c1 = tb.rows[0].cells
    c0.vertical_alignment = c1.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    C._bordes(c0, left=(24, C.GRANATE))
    par(c0.paragraphs[0], '   UBICACIÓN DEL PROYECTO', 10, True, C.GRANATE, centro=False, antes=34, despues=4, sep=6)
    for etq, val in (('Distrito', 'Morales'), ('Provincia', 'San Martín'), ('Departamento', 'San Martín')):
        p = par(c0, '   %s:  ' % etq, 10, False, C.GRIS, centro=False, despues=2)
        r = p.add_run(val); r.font.size = Pt(10); r.bold = True; r.font.name = 'Arial'
    C._bordes(c1, left=(24, C.GRANATE))
    par(c1.paragraphs[0], '   FECHA', 10, True, C.GRANATE, centro=False, antes=34, despues=4, sep=6)
    par(c1, '   ' + FECHA, 15, True, C.GRANATE, centro=False, despues=2, sep=6)


def documento():
    d = docx.Document()
    st = d.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial'); st.paragraph_format.space_after = Pt(0)
    s = d.sections[0]; s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = Cm(2.3); s.bottom_margin = Cm(1.2)
    if d.paragraphs:
        d.element.body.remove(d.paragraphs[0]._p)
    return d


def generar():
    img = foto()
    if os.path.isdir(SALIDA):
        shutil.rmtree(SALIDA)
    os.makedirs(SALIDA)
    salidas = []
    for archivo, titulo, sub in DOCUMENTOS:
        d = documento()
        caratula(d, img, titulo, sub)
        # el último párrafo del cuerpo queda mínimo para que la carátula no pase a una segunda página
        p = d.add_paragraph(); rpr = OxmlElement('w:rPr'); sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '2'); rpr.append(sz)
        p._p.get_or_add_pPr().append(rpr)
        d.core_properties.author = ''
        d.core_properties.title = 'Carátula - %s - Drenaje pluvial CAR Varones' % titulo.capitalize()
        ruta = os.path.join(SALIDA, archivo + '_CAR_VARONES.docx'); d.save(ruta); salidas.append(ruta)
    return salidas


if __name__ == '__main__':
    for r in generar():
        print(os.path.relpath(r, RAIZ))
