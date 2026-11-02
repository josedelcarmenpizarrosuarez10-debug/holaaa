# -*- coding: utf-8 -*-
"""Carátulas de tomos (I a X) y lomos de archivador en PowerPoint - CAR Varones, Hogar de Refugio y CAR Mujeres.

Un modelo de diseño distinto por proyecto (no se mezclan entre proyectos), fondo blanco con guinda y dorado solo en letras,
líneas finas y detalles (la usuaria no quiere bloques de color):
  - CAR Varones (CUI 2705619): modelo 1, centrado con línea fina guinda a la izquierda;
  - Hogar de Refugio Temporal (CUI 2675514): modelo 2, alineado a la izquierda con número de tomo grande;
  - CAR Mujeres (CUI 2717013): modelo 3, marco doble fino y ornamentos.
Carátulas: hoja A4 vertical, una por tomo (Tomo I a Tomo X), sin contenido (el contenido se escribe en los lomos).
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
        borde_celda(tbl.cell(0, c), 'F6ECEE', P['c1'])
    letra_celda(tbl.cell(0, 0), titulo, size_t, P['c1'], bold=True, align=PP_ALIGN.CENTER, esp=1.5)
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


# ------------------------------------------------------------------ carátulas (sin contenido: el contenido va en los lomos)
# Fondo blanco; el guinda solo en letras, líneas finas y detalles (pedido de la usuaria: sin tanto color).
def ornamento(sl, cx, y, c2, largo=3.2):
    rect(sl, cx - 0.35 - largo, y, largo, 0.025, fill=c2); rect(sl, cx + 0.35, y, largo, 0.025, fill=c2)
    rect(sl, cx - 0.13, y - 0.12, 0.26, 0.26, fill=c2, forma=MSO_SHAPE.DIAMOND)


def caratula_1(sl, P, n):
    """Modelo 1: centrado, línea fina guinda a la izquierda, foto con filete dorado y tomo entre líneas."""
    c1, c2 = P['c1'], P['c2']
    rect(sl, 0, 0, 21, 29.7, fill=BLANCO)
    rect(sl, 1.2, 1.2, 0.08, 27.3, fill=c1); rect(sl, 1.45, 1.2, 0.025, 27.3, fill=c2)
    cx = 11.2
    escudo(sl, cx, 1.5, 2.2)
    texto(sl, 2.2, 3.85, 18, 0.8, ENTIDAD, size=15, color=c1, bold=True, align=PP_ALIGN.CENTER, esp=2)
    texto(sl, 2.2, 4.55, 18, 0.7, GERENCIA, size=10.5, color=GRIS, align=PP_ALIGN.CENTER, esp=1)
    ornamento(sl, cx, 5.55, c2)
    texto(sl, 2.2, 6.0, 18, 1.0, 'EXPEDIENTE TÉCNICO', size=22, color=c1, font=SERIF, align=PP_ALIGN.CENTER, esp=4)
    texto(sl, 3.0, 7.25, 16.4, 3.4, P['nombre'], size=12, color='333333', font=SERIF, bold=True, align=PP_ALIGN.CENTER)
    texto(sl, 2.2, 10.6, 18, 0.7, 'CUI N° ' + P['cui'], size=13, color=c1, bold=True, align=PP_ALIGN.CENTER, esp=1.5)
    fw = 15.0; fh = fw * 9 / 16; fx, fy = cx - fw / 2, 11.75
    foto(sl, os.path.join(RAIZ, P['foto']), fx, fy, fw, fh)
    rect(sl, fx - 0.2, fy - 0.2, fw + 0.4, fh + 0.4, line=c2, lw=0.75)
    yt = fy + fh + 2.3
    texto(sl, cx - 5, yt, 10, 1.8, 'TOMO ' + ROMANOS[n], size=40, color=c1, font=SERIF, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE, esp=3)
    rect(sl, 3.0, yt + 0.9, 3.3, 0.025, fill=c2); rect(sl, cx + 5 - 0.6 + 0.3, yt + 0.9, 3.3, 0.025, fill=c2)
    rect(sl, 3.0, 27.45, 16.4, 0.02, fill=GRIS_CLARO)
    texto(sl, 2.2, 27.6, 18, 0.6, [[(UBICACION, {}), ('    ·    ', dict(color=c2)), (P['fecha'], {})]], size=10, color=GRIS,
          align=PP_ALIGN.CENTER, esp=1)


def caratula_2(sl, P, n):
    """Modelo 2: alineado a la izquierda, encabezado con escudo, filete guinda vertical junto al título y número grande abajo."""
    c1, c2 = P['c1'], P['c2']
    rect(sl, 0, 0, 21, 29.7, fill=BLANCO)
    x = 2.2; w = 16.6
    escudo(sl, x + 0.95, 1.5, 1.9)
    texto(sl, x + 2.3, 1.75, w - 2.3, 0.75, ENTIDAD, size=14, color=c1, bold=True, esp=1.5)
    texto(sl, x + 2.3, 2.45, w - 2.3, 0.7, GERENCIA, size=10.5, color=GRIS, esp=0.8)
    rect(sl, x, 3.85, w, 0.03, fill=c1)
    rect(sl, x, 5.0, 0.12, 6.0, fill=c1)
    texto(sl, x + 0.55, 4.85, w - 0.6, 0.9, 'EXPEDIENTE TÉCNICO', size=20, color=c1, font=SERIF, bold=True, esp=3)
    texto(sl, x + 0.55, 5.9, w - 0.6, 3.6, P['nombre'], size=12, color='333333', font=SERIF, align=PP_ALIGN.JUSTIFY)
    texto(sl, x + 0.55, 10.0, w - 0.6, 0.7, 'CUI N° ' + P['cui'], size=13, color=c2, bold=True, esp=1.5)
    fh = w * 9 / 16
    foto(sl, os.path.join(RAIZ, P['foto']), x, 11.8, w, fh)
    yt = 11.8 + fh + 0.9
    texto(sl, x, yt, 8, 0.7, 'TOMO', size=14, color=c2, bold=True, esp=4)
    texto(sl, x, yt + 0.55, 12, 2.6, ROMANOS[n], size=66, color=c1, font=SERIF, anchor=MSO_ANCHOR.TOP)
    rect(sl, x, 27.2, w, 0.03, fill=c1)
    texto(sl, x, 27.4, w / 2, 0.6, UBICACION, size=10, color=GRIS, esp=1)
    texto(sl, x + w / 2, 27.4, w / 2, 0.6, P['fecha'], size=10, color=GRIS, align=PP_ALIGN.RIGHT, esp=1)


def caratula_3(sl, P, n):
    """Modelo 3: marco doble fino, todo centrado, foto rectangular y tomo con ornamentos."""
    c1, c2 = P['c1'], P['c2']
    rect(sl, 0, 0, 21, 29.7, fill=BLANCO)
    rect(sl, 1.0, 1.0, 19.0, 27.7, line=c1, lw=1.25)
    rect(sl, 1.25, 1.25, 18.5, 27.2, line=c2, lw=0.5)
    escudo(sl, 10.5, 2.0, 2.3)
    texto(sl, 1.5, 4.45, 18, 0.8, ENTIDAD, size=15, color=c1, font=SERIF, bold=True, align=PP_ALIGN.CENTER, esp=2)
    texto(sl, 1.5, 5.2, 18, 0.7, GERENCIA, size=10.5, color=GRIS, align=PP_ALIGN.CENTER, esp=1)
    fw = 13.6; fh = fw * 9 / 16; fy = 6.5
    foto(sl, os.path.join(RAIZ, P['foto']), 10.5 - fw / 2, fy, fw, fh)
    y = fy + fh + 0.7
    texto(sl, 1.5, y, 18, 0.7, 'EXPEDIENTE TÉCNICO', size=13, color=c2, bold=True, align=PP_ALIGN.CENTER, esp=5)
    texto(sl, 2.6, y + 0.8, 15.8, 3.4, P['nombre'], size=12, color=c1, font=SERIF, bold=True, align=PP_ALIGN.CENTER)
    texto(sl, 1.5, y + 4.2, 18, 0.7, 'CUI N° ' + P['cui'], size=13, color='333333', bold=True, align=PP_ALIGN.CENTER, esp=1.5)
    yt = y + 5.6
    ornamento(sl, 10.5, yt, c2, largo=2.4)
    texto(sl, 1.5, yt + 0.35, 18, 1.8, 'TOMO ' + ROMANOS[n], size=32, color=c1, font=SERIF, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE, esp=3)
    ornamento(sl, 10.5, yt + 2.5, c2, largo=2.4)
    texto(sl, 1.5, 27.0, 18, 0.6, [[(UBICACION, {}), ('   ◆   ', dict(color=c2)), (P['fecha'], {})]], size=10, color=GRIS,
          align=PP_ALIGN.CENTER, esp=1)


CARATULA = {1: caratula_1, 2: caratula_2, 3: caratula_3}


# ------------------------------------------------------------------ lomos
def lomo(sl, P, x, y, w, h, n):
    """Lomo de archivador en fondo blanco: escudo, tomo, tabla de contenido, nombre completo con CUI en vertical y pie."""
    c1, c2 = P['c1'], P['c2']
    ancho = w > 5
    rect(sl, x, y, w, h, fill=BLANCO)
    rect(sl, x, y, w, 0.28, fill=c1)
    escudo(sl, x + w / 2, y + 0.6, 1.6 if ancho else 1.25)
    texto(sl, x + 0.1, y + (2.3 if ancho else 1.95), w - 0.2, 0.9, ['GOBIERNO REGIONAL', 'SAN MARTÍN'], size=8 if ancho else 6.5,
          color=c1, bold=True, align=PP_ALIGN.CENTER, esp=0.5)
    rect(sl, x + w * 0.2, y + 3.25, w * 0.6, 0.025, fill=c2)
    yt = y + 3.45
    texto(sl, x, yt, w, 0.6, 'TOMO', size=11 if ancho else 9, color=c2, bold=True, align=PP_ALIGN.CENTER, esp=3)
    num = ROMANOS[n] if n is not None else ''
    texto(sl, x, yt + 0.5, w, 2.2, num, size=(44 if ancho else 30) if len(num) < 4 else (34 if ancho else 22), color=c1,
          font=SERIF, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if n is None:                                                  # lomo de reserva: renglón para escribir el número
        rect(sl, x + w * 0.25, yt + 2.2, w * 0.5, 0.025, fill=GRIS_CLARO)
    rect(sl, x + w * 0.2, yt + 2.9, w * 0.6, 0.025, fill=c2)
    yc = yt + 3.2; hc = 10.2
    tabla(sl, x + 0.3, yc, w - 0.6, hc, P, 'CONTENIDO', 0.68, False, 9 if ancho else 7.5, 9 if ancho else 7.5, hdr=0.65)
    yv = yc + hc + 0.3; hv = y + h - 1.4 - yv                       # nombre completo del proyecto y CUI en vertical
    rect(sl, x + 0.3, yv, w - 0.6, hv, line=c2, lw=0.5)
    texto(sl, x + w / 2 - hv / 2 + 0.15, yv + hv / 2 - (w - 0.8) / 2, hv - 0.3, w - 0.8,
          [[(P['nombre'], dict(size=10.5 if ancho else 7.5, color=c1, font=SERIF, bold=True))],
           [('CUI N° ' + P['cui'], dict(size=11 if ancho else 8, color=c2, bold=True, esp=1))]],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, rot=270)
    texto(sl, x, y + h - 1.15, w, 0.85, ['EXPEDIENTE TÉCNICO', P['fecha'].split()[-1]], size=7.5 if ancho else 6, color=c1,
          bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, esp=0.5)
    rect(sl, x, y + h - 0.28, w, 0.28, fill=c1)
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
