# -*- coding: utf-8 -*-
"""Carátulas de tomos (I a X) y lomos de archivador en PowerPoint - CAR Varones, Hogar de Refugio y CAR Mujeres.

Un modelo de diseño distinto por proyecto (no se mezclan entre proyectos):
  - CAR Varones (CUI 2705619): modelo 1, banda lateral azul marino y dorado;
  - Hogar de Refugio Temporal (CUI 2675514): modelo 2, foto a todo el ancho con sello circular, verde y champán;
  - CAR Mujeres (CUI 2717013): modelo 3, marco clásico doble, ciruela y dorado.
Carátulas: hoja A4 vertical, una por tomo (Tomo I a Tomo X), con una tabla editable "CONTENIDO DEL TOMO" (clic en la celda y escribir;
también se puede llenar a mano).
Lomos: archivador de palanca tamaño oficio, lomo ancho (6.3 x 27.6 cm) y lomo delgado (4.0 x 27.6 cm), 3 por hoja A4 con
líneas de corte; cada lomo con escudo, número de tomo, tabla editable "CONTENIDO" y nombre completo del proyecto con su CUI
en vertical. Colores: guinda y dorado en los tres proyectos.

Uso: python3 herramientas/caratulas_tomos_pptx.py
Salidas: entregables_varones/, entregables/ y entregables_mujeres/  CARATULAS_TOMOS_I_AL_X_*.pptx y LOMOS_ARCHIVADORES_OFICIO_*.pptx
"""
import os

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Cm, Pt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESCUDO = os.path.join(RAIZ, 'entregables_varones/figuras_caratula/escudo_gore_san_martin.png')
SERIF, SANS = 'Cambria', 'Calibri'
ROMANOS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
ENTIDAD = 'GOBIERNO REGIONAL SAN MARTÍN'
GERENCIA = 'GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO'
UBICACION = 'MORALES - SAN MARTÍN - SAN MARTÍN'

GUINDA, DORADO, CREMA = '6B1F2E', 'C5A15A', 'FBF6F2'           # guinda (pedido de la usuaria) con dorado
PROYECTOS = [
    dict(clave='CAR_VARONES', modelo=1, carpeta='entregables_varones', cui='2705619', fecha='SETIEMBRE - 2026',
         corto='CENTRO DE ACOGIDA RESIDENCIAL - VARONES',
         foto='entregables_varones/figuras_caratula/foto_proyecto_car_varones.jpg',
         nombre='“CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO '
                'DE PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES DISTRITO DE MORALES DE LA PROVINCIA DE SAN MARTÍN DEL '
                'DEPARTAMENTO DE SAN MARTÍN”',
         c1=GUINDA, c2=DORADO, c3=CREMA),
    dict(clave='HOGAR_REFUGIO', modelo=2, carpeta='entregables', cui='2675514', fecha='SETIEMBRE - 2026',
         corto='HOGAR DE REFUGIO TEMPORAL',
         foto='entregables/figuras_caratula/foto_proyecto_hogar_refugio.jpg',
         nombre='“CREACIÓN DEL SERVICIO DE PROTECCIÓN A MUJERES VÍCTIMAS DE VIOLENCIA EN SITUACIÓN DE RIESGO DE FEMINICIDIO O '
                'PELIGRE SU INTEGRIDAD Y/O SALUD FÍSICA Y/O MENTAL EN HOGAR DE REFUGIO TEMPORAL DISTRITO DE MORALES DE LA '
                'PROVINCIA DE SAN MARTÍN DEL DEPARTAMENTO DE SAN MARTÍN”',
         c1=GUINDA, c2=DORADO, c3=CREMA),
    dict(clave='CAR_MUJERES', modelo=3, carpeta='entregables_mujeres', cui='2717013', fecha='SEPTIEMBRE - 2026',
         corto='CENTRO DE ACOGIDA RESIDENCIAL - MUJERES',
         foto='entregables_mujeres/figuras_caratula/vista_3d_car.jpg',
         nombre='“CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO '
                'DE PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - MUJERES DISTRITO DE MORALES DE LA PROVINCIA DE SAN MARTÍN DEL '
                'DEPARTAMENTO DE SAN MARTÍN”',
         c1=GUINDA, c2=DORADO, c3=CREMA),
]
BLANCO, GRIS, GRIS_CLARO = 'FFFFFF', '595959', 'BFBFBF'


# ------------------------------------------------------------------ piezas
def rgb(h):
    return RGBColor.from_string(h)


def rect(sl, x, y, w, h, fill=None, line=None, lw=0.75, forma=MSO_SHAPE.RECTANGLE, dash=None, alpha=None, nombre=None):
    s = sl.shapes.add_shape(forma, Cm(x), Cm(y), Cm(w), Cm(h))
    st = s._element.find(qn('p:style'))                        # sin el estilo del tema (sombra y contorno por defecto)
    if st is not None:
        s._element.remove(st)
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = rgb(fill)
        if alpha is not None:                                   # opacidad en % (100 = opaco)
            clr = s.fill._xPr.find(qn('a:solidFill')).find(qn('a:srgbClr'))
            etree.SubElement(clr, qn('a:alpha')).set('val', str(int(alpha * 1000)))
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line); s.line.width = Pt(lw)
        if dash:
            s.line.dash_style = dash
    else:
        s.line.fill.background()
    if nombre:
        s.name = nombre
    return s


def texto(sl, x, y, w, h, partes, size=11, color='000000', font=SANS, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
          esp=0, rot=0, interl=None, nombre=None):
    """partes: texto, o lista de párrafos; cada párrafo: texto o lista de (texto, {size, color, font, bold, esp})."""
    tb = sl.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Cm(0.05); tf.margin_top = tf.margin_bottom = Cm(0.02)
    pars = partes if isinstance(partes, list) else [partes]
    for i, par in enumerate(pars):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if interl:
            p.line_spacing = interl
        runs = par if isinstance(par, list) else [(par, {})]
        for t, o in runs:
            r = p.add_run(); r.text = t
            f = r.font; f.name = o.get('font', font); f.size = Pt(o.get('size', size)); f.bold = o.get('bold', bold)
            f.color.rgb = rgb(o.get('color', color))
            e = o.get('esp', esp)
            if e:
                r._r.get_or_add_rPr().set('spc', str(int(e * 100)))
    if rot:
        tb.rotation = rot
    if nombre:
        tb.name = nombre
    return tb


def foto(sl, ruta, x, y, w, h):
    """Imagen recortada al tamaño del recuadro (sin deformar)."""
    W, H = Image.open(ruta).size
    p = sl.shapes.add_picture(ruta, Cm(x), Cm(y), Cm(w), Cm(h))
    r_img, r_box = W / H, w / h
    if r_img > r_box:
        c = (1 - r_box / r_img) / 2; p.crop_left = p.crop_right = c
    else:
        c = (1 - r_img / r_box) / 2; p.crop_top = p.crop_bottom = c
    return p


def escudo(sl, cx, y, alto, circulo=None):
    """Escudo del Gobierno Regional centrado en cx; con círculo blanco detrás si va sobre fondo oscuro."""
    W, H = Image.open(ESCUDO).size
    ancho = alto * W / H
    if circulo:
        d = alto * 1.28
        rect(sl, cx - d / 2, y - (d - alto) / 2, d, d, fill=BLANCO, line=circulo, lw=1.25, forma=MSO_SHAPE.OVAL)
    sl.shapes.add_picture(ESCUDO, Cm(cx - ancho / 2), Cm(y), Cm(ancho), Cm(alto))


def borde_celda(cell, fondo, linea, lw=0.5):
    """Relleno y bordes de una celda (en el orden del esquema: bordes y luego relleno)."""
    tcPr = cell._tc.get_or_add_tcPr()
    for ch in list(tcPr):
        tcPr.remove(ch)
    for lado in ('lnL', 'lnR', 'lnT', 'lnB'):
        ln = etree.SubElement(tcPr, qn('a:' + lado), w=str(int(Pt(lw))), cap='flat', cmpd='sng', algn='ctr')
        sf = etree.SubElement(ln, qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr'), val=linea)
        etree.SubElement(ln, qn('a:prstDash'), val='solid')
    sf = etree.SubElement(tcPr, qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr'), val=fondo)


def letra_celda(cell, txt, size, color, bold=False, align=PP_ALIGN.LEFT, esp=0):
    """Texto de la celda y formato para lo que se escriba después (endParaRPr)."""
    cell.margin_left = cell.margin_right = Cm(0.15); cell.margin_top = cell.margin_bottom = Cm(0.03)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = cell.text_frame.paragraphs[0]; p.alignment = align
    if txt:
        r = p.add_run(); r.text = txt
        f = r.font; f.name = SANS; f.size = Pt(size); f.bold = bold; f.color.rgb = rgb(color)
        if esp:
            r._r.get_or_add_rPr().set('spc', str(int(esp * 100)))
    e = p._p.get_or_add_endParaRPr(); e.set('lang', 'es-PE'); e.set('sz', str(int(size * 100))); e.set('b', '1' if bold else '0')
    sf = etree.SubElement(e, qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr'), val=color)
    etree.SubElement(e, qn('a:latin'), typeface=SANS)


def tabla(sl, x, y, w, h, P, titulo, paso, numerada, size_t, size_c, hdr=0.8):
    """Tabla editable para escribir el contenido (clic en la celda y escribir); encabezado guinda, filas con borde fino."""
    n = int(round((h - hdr) / paso - 0.49))
    cols = 2 if numerada else 1
    gf = sl.shapes.add_table(n + 1, cols, Cm(x), Cm(y), Cm(w), Cm(hdr + n * paso))
    gf.name = 'Contenido (escriba en las celdas)'
    tbl = gf.table
    tblPr = tbl._tbl.tblPr
    tblPr.set('firstRow', '0'); tblPr.set('bandRow', '0')
    for ch in list(tblPr):
        tblPr.remove(ch)                                           # sin estilo de tabla del tema
    anchos = [1.0, w - 1.0] if numerada else [w]
    for i, a in enumerate(anchos):
        tbl.columns[i].width = Cm(a)
    tbl.rows[0].height = Cm(hdr)
    for r in range(1, n + 1):
        tbl.rows[r].height = Cm(paso)
    linea = 'C9A9AE'
    if numerada:
        tbl.cell(0, 0).merge(tbl.cell(0, 1))
    for c in range(cols):
        borde_celda(tbl.cell(0, c), P['c1'], P['c1'])
    letra_celda(tbl.cell(0, 0), titulo, size_t, BLANCO, bold=True, align=PP_ALIGN.CENTER, esp=1.5)
    for r in range(1, n + 1):
        if numerada:
            borde_celda(tbl.cell(r, 0), 'F4E8EA', linea)
            letra_celda(tbl.cell(r, 0), str(r), size_c, P['c1'], bold=True, align=PP_ALIGN.CENTER)
        c = cols - 1
        borde_celda(tbl.cell(r, c), BLANCO, linea)
        letra_celda(tbl.cell(r, c), '', size_c, '262626')
    return gf


def nueva(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    return sl


def presentacion():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Cm(21.0), Cm(29.7)
    return prs


# ------------------------------------------------------------------ carátulas
def caratula_1(sl, P, n):
    """Modelo 1: banda lateral con el número del tomo, foto y recuadro de contenido."""
    c1, c2, c3 = P['c1'], P['c2'], P['c3']
    rect(sl, 0, 0, 21, 29.7, fill=BLANCO)
    rect(sl, 0, 0, 4.6, 29.7, fill=c1)
    rect(sl, 4.6, 0, 0.12, 29.7, fill=c2)
    escudo(sl, 2.3, 1.45, 2.5, circulo=c2)
    texto(sl, 2.3 - 8.5, 13.2 - 0.9, 17, 1.8, 'EXPEDIENTE TÉCNICO', size=24, color=BLANCO, font=SERIF, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE, esp=6, rot=270)
    rect(sl, 0.9, 22.6, 2.8, 0.05, fill=c2)
    texto(sl, 0, 22.9, 4.6, 0.8, 'TOMO', size=13, color=c2, bold=True, align=PP_ALIGN.CENTER, esp=4)
    texto(sl, 0, 23.7, 4.6, 3.2, ROMANOS[n], size=60 if len(ROMANOS[n]) < 4 else 46, color=BLANCO, font=SERIF, bold=True,
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rect(sl, 0.9, 27.2, 2.8, 0.05, fill=c2)
    x, w = 5.6, 14.3
    texto(sl, x, 1.1, w, 0.8, ENTIDAD, size=14, color=c1, bold=True, esp=1.5)
    texto(sl, x, 1.85, w, 0.7, GERENCIA, size=10.5, color=GRIS, esp=0.8)
    rect(sl, x, 2.75, w, 0.05, fill=c2)
    texto(sl, x, 3.05, w, 0.6, 'EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:', size=9.5, color=GRIS, bold=True, esp=0.5)
    texto(sl, x, 3.65, w, 3.8, P['nombre'], size=12.5, color=c1, font=SERIF, bold=True, align=PP_ALIGN.JUSTIFY)
    texto(sl, x, 7.55, w, 0.7, 'CUI N° ' + P['cui'], size=13, color=c2, bold=True, esp=1)
    foto(sl, os.path.join(RAIZ, P['foto']), x, 8.5, w, w * 9 / 16)
    rect(sl, x, 8.5, w, w * 9 / 16, line=c2, lw=1.5)
    y = 8.5 + w * 9 / 16
    texto(sl, x, y + 0.45, w, 1.6, [[('TOMO ', dict(size=30, color=c1)), (ROMANOS[n], dict(size=30, color=c2))]], font=SERIF,
          bold=True, anchor=MSO_ANCHOR.MIDDLE)
    yc = y + 2.35; hc = 26.75 - yc
    tabla(sl, x, yc, w, hc, P, 'CONTENIDO DEL TOMO', 0.78, True, 11, 10.5)
    rect(sl, x, 27.25, w, 0.03, fill=c2)
    texto(sl, x, 27.45, w * 0.6, 0.7, UBICACION, size=10.5, color=c1, bold=True, esp=0.5)
    texto(sl, x + w * 0.4, 27.45, w * 0.6, 0.7, P['fecha'], size=10.5, color=c1, bold=True, align=PP_ALIGN.RIGHT, esp=0.5)


def caratula_2(sl, P, n):
    """Modelo 2: foto a todo el ancho, sello circular con el tomo, recuadro de contenido y pie de color."""
    c1, c2, c3 = P['c1'], P['c2'], P['c3']
    rect(sl, 0, 0, 21, 29.7, fill=BLANCO)
    foto(sl, os.path.join(RAIZ, P['foto']), 0, 0, 21, 12.2)
    rect(sl, 0, 0, 21, 2.9, fill=c1, alpha=88)
    escudo(sl, 1.9, 0.45, 2.0, circulo=c2)
    texto(sl, 3.5, 0.55, 16.5, 0.9, ENTIDAD, size=15, color=BLANCO, bold=True, esp=1.5)
    texto(sl, 3.5, 1.4, 16.5, 0.8, GERENCIA, size=11, color=c2, bold=True, esp=0.8)
    rect(sl, 0, 12.2, 21, 0.14, fill=c2)
    d = 5.0
    rect(sl, 10.5 - d / 2, 12.27 - d / 2, d, d, fill=c1, line=c2, lw=3, forma=MSO_SHAPE.OVAL)
    texto(sl, 10.5 - d / 2, 12.27 - d / 2 + 0.75, d, 0.8, 'TOMO', size=13, color=c2, bold=True, align=PP_ALIGN.CENTER, esp=4)
    texto(sl, 10.5 - d / 2, 12.27 - d / 2 + 1.45, d, 2.6, ROMANOS[n], size=50 if len(ROMANOS[n]) < 4 else 38, color=BLANCO,
          font=SERIF, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    texto(sl, 1.5, 15.1, 18, 0.8, 'EXPEDIENTE TÉCNICO', size=15, color=c1, bold=True, align=PP_ALIGN.CENTER, esp=4)
    rect(sl, 7.5, 15.95, 6, 0.05, fill=c2)
    texto(sl, 1.8, 16.2, 17.4, 3.4, P['nombre'], size=12, color='2B2B2B', font=SERIF, bold=True, align=PP_ALIGN.CENTER)
    texto(sl, 1.5, 19.55, 18, 0.7, 'CUI N° ' + P['cui'], size=13, color=c1, bold=True, align=PP_ALIGN.CENTER, esp=1)
    yc, hc = 20.5, 6.1
    tabla(sl, 1.8, yc, 17.4, hc, P, 'CONTENIDO DEL TOMO', 0.75, True, 11, 10.5)
    rect(sl, 0, 27.3, 21, 2.4, fill=c1)
    rect(sl, 0, 27.3, 21, 0.1, fill=c2)
    texto(sl, 0, 27.75, 21, 0.7, UBICACION, size=12, color=BLANCO, bold=True, align=PP_ALIGN.CENTER, esp=1.5)
    texto(sl, 0, 28.45, 21, 0.7, P['fecha'], size=11, color=c2, bold=True, align=PP_ALIGN.CENTER, esp=1.5)


def caratula_3(sl, P, n):
    """Modelo 3: marco doble clásico, escudo centrado, foto con placa del tomo y recuadro de contenido."""
    c1, c2, c3 = P['c1'], P['c2'], P['c3']
    rect(sl, 0, 0, 21, 29.7, fill=c3)
    rect(sl, 0.7, 0.7, 19.6, 28.3, line=c1, lw=2.5)
    rect(sl, 0.98, 0.98, 19.04, 27.74, line=c2, lw=0.75)
    escudo(sl, 10.5, 1.45, 2.3)
    texto(sl, 1.5, 3.95, 18, 0.8, ENTIDAD, size=15, color=c1, font=SERIF, bold=True, align=PP_ALIGN.CENTER, esp=1.5)
    texto(sl, 1.5, 4.7, 18, 0.7, GERENCIA, size=10.5, color=GRIS, align=PP_ALIGN.CENTER, esp=0.8)
    rect(sl, 6.6, 5.72, 3.4, 0.03, fill=c2); rect(sl, 11.0, 5.72, 3.4, 0.03, fill=c2)
    rect(sl, 10.5 - 0.17, 5.565, 0.34, 0.34, fill=c2, forma=MSO_SHAPE.DIAMOND)
    texto(sl, 1.5, 6.05, 18, 0.7, 'EXPEDIENTE TÉCNICO', size=12, color=c2, bold=True, align=PP_ALIGN.CENTER, esp=4)
    texto(sl, 2.2, 6.75, 16.6, 3.5, P['nombre'], size=12, color=c1, font=SERIF, bold=True, align=PP_ALIGN.CENTER)
    texto(sl, 1.5, 10.2, 18, 0.7, 'CUI N° ' + P['cui'], size=12.5, color=c1, bold=True, align=PP_ALIGN.CENTER, esp=1)
    fw, fh = 14.6, 14.6 * 9 / 16; fx, fy = 10.5 - fw / 2, 11.15
    rect(sl, fx - 0.18, fy - 0.18, fw + 0.36, fh + 0.36, line=c2, lw=0.75)
    foto(sl, os.path.join(RAIZ, P['foto']), fx, fy, fw, fh)
    pw, ph = 7.6, 1.9
    rect(sl, 10.5 - pw / 2, fy + fh - ph / 2, pw, ph, fill=c1, line=c2, lw=1.5)
    texto(sl, 10.5 - pw / 2, fy + fh - ph / 2, pw, ph, 'TOMO ' + ROMANOS[n], size=28, color=c3, font=SERIF, bold=True,
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, esp=2)
    yc = fy + fh + ph / 2 + 0.7; hc = 26.9 - yc
    rect(sl, 2.2 - 0.12, yc - 0.12, 16.6 + 0.24, hc + 0.24, line=c2, lw=0.75)
    tabla(sl, 2.2, yc, 16.6, hc, P, 'CONTENIDO DEL TOMO', 0.72, True, 11, 10.5)
    texto(sl, 1.5, 27.3, 18, 0.7, [[(UBICACION, {}), ('   ◆   ', dict(color=c2)), (P['fecha'], {})]], size=10.5, color=c1,
          bold=True, align=PP_ALIGN.CENTER, esp=1)


CARATULA = {1: caratula_1, 2: caratula_2, 3: caratula_3}


# ------------------------------------------------------------------ lomos
def lomo(sl, P, x, y, w, h, n):
    """Lomo de archivador: escudo, tomo, recuadro de contenido, nombre del proyecto en vertical y pie."""
    c1, c2, c3, m = P['c1'], P['c2'], P['c3'], P['modelo']
    ancho = w > 5
    rect(sl, x, y, w, h, fill=c3 if m == 3 else BLANCO)
    hh = 3.5 if ancho else 3.0
    rect(sl, x, y, w, hh, fill=c1)
    rect(sl, x, y + hh, w, 0.1, fill=c2)
    escudo(sl, x + w / 2, y + 0.35, 1.75 if ancho else 1.35, circulo=c2)
    texto(sl, x + 0.1, y + (2.55 if ancho else 2.05), w - 0.2, 0.9, ['GOBIERNO REGIONAL', 'SAN MARTÍN'], size=8 if ancho else 6.5,
          color=BLANCO, bold=True, align=PP_ALIGN.CENTER, esp=0.5)
    yt = y + hh + 0.25
    texto(sl, x, yt, w, 0.6, 'TOMO', size=12 if ancho else 10, color=c2, bold=True, align=PP_ALIGN.CENTER, esp=3)
    num = ROMANOS[n] if n is not None else ''
    texto(sl, x, yt + 0.55, w, 2.2, num, size=(44 if ancho else 30) if len(num) < 4 else (34 if ancho else 22), color=c1,
          font=SERIF, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if n is None:                                                  # lomo de reserva: renglón para escribir el número
        rect(sl, x + w * 0.25, yt + 2.2, w * 0.5, 0.025, fill=GRIS_CLARO)
    rect(sl, x + w * 0.3, yt + 2.95, w * 0.4, 0.05, fill=c2)
    yc = yt + 3.25; hc = 10.2
    tabla(sl, x + 0.3, yc, w - 0.6, hc, P, 'CONTENIDO', 0.68, False, 9 if ancho else 7.5, 9 if ancho else 7.5, hdr=0.65)
    yv = yc + hc + 0.3; hv = y + h - 1.5 - yv                       # nombre completo del proyecto y CUI en vertical
    rect(sl, x + 0.3, yv, w - 0.6, hv, fill=c1 if m == 2 else c3 if m == 3 else 'F7EEEF', line=c2 if m == 3 else None)
    col = BLANCO if m == 2 else c1
    texto(sl, x + w / 2 - hv / 2 + 0.15, yv + hv / 2 - (w - 0.8) / 2, hv - 0.3, w - 0.8,
          [[(P['nombre'], dict(size=10.5 if ancho else 7.5, color=col, font=SERIF, bold=True))],
           [('CUI N° ' + P['cui'], dict(size=11 if ancho else 8, color=c2, bold=True, esp=1))]],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, rot=270)
    rect(sl, x, y + h - 1.2, w, 1.2, fill=c1)
    rect(sl, x, y + h - 1.2, w, 0.08, fill=c2)
    texto(sl, x, y + h - 1.12, w, 1.1, ['EXPEDIENTE TÉCNICO', P['fecha'].split()[-1]], size=7.5 if ancho else 6, color=BLANCO,
          bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, esp=0.5)
    rect(sl, x, y, w, h, line='7F7F7F', lw=0.5, dash=MSO_LINE.DASH, nombre='Línea de corte')


def hoja_lomos(prs, P, w, tomos, titulo):
    sl = nueva(prs)
    h, sep = 27.6, 0.35
    x0 = (21 - (3 * w + 2 * sep)) / 2; y0 = (29.7 - h) / 2
    for i, n in enumerate(tomos):
        lomo(sl, P, x0 + i * (w + sep), y0, w, h, n)
    for i in range(3):                                             # marcas de corte en los bordes de la hoja
        for xx in (x0 + i * (w + sep), x0 + i * (w + sep) + w):
            rect(sl, xx - 0.005, 0.15, 0.01, y0 - 0.3, fill='7F7F7F'); rect(sl, xx - 0.005, y0 + h + 0.15, 0.01, y0 - 0.3, fill='7F7F7F')
    texto(sl, 0.3, 29.7 - 0.45, 20.4, 0.4, titulo + ' - recortar por la línea discontinua', size=6.5, color='7F7F7F',
          align=PP_ALIGN.CENTER)


def generar():
    out = []
    for P in PROYECTOS:
        prs = presentacion()
        for n in range(10):
            CARATULA[P['modelo']](nueva(prs), P, n)
        prs.core_properties.title = 'Carátulas de tomos - ' + P['corto']; prs.core_properties.author = ''
        ruta = os.path.join(RAIZ, P['carpeta'], 'CARATULAS_TOMOS_I_AL_X_%s.pptx' % P['clave'])
        prs.save(ruta); out.append(ruta)
        prs = presentacion()
        grupos = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, None, None]]
        for w, nom in ((6.3, 'Lomo ancho 6.3 cm'), (4.0, 'Lomo delgado 4.0 cm')):
            for g in grupos:
                hoja_lomos(prs, P, w, g, '%s - archivador oficio - %s' % (nom, P['corto']))
        prs.core_properties.title = 'Lomos de archivador - ' + P['corto']; prs.core_properties.author = ''
        ruta = os.path.join(RAIZ, P['carpeta'], 'LOMOS_ARCHIVADORES_OFICIO_%s.pptx' % P['clave'])
        prs.save(ruta); out.append(ruta)
    return out


if __name__ == '__main__':
    for r in generar():
        print(r)
