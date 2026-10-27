# -*- coding: utf-8 -*-
"""Memoria descriptiva de drenaje pluvial - CAR Mujeres (CUI 2717013).

Toma la carátula, el bloque de información, los estilos y los logos de la memoria
de instalaciones sanitarias del mismo proyecto (insumos/wilma/MEMORIA_IISS_CAR_MUJERES.docx)
y desarrolla el contenido de drenaje pluvial, coherente con:
  - la memoria hidrológica con el capítulo del colector,
  - el juego de 46 planos (insumos/wilma/LISTA_PLANOS_ANDFY_MUJERES.txt),
  - el metrado vigente (RESUMEN y hojas por eje; solo lectura).

Uso:
  python3 herramientas/mujeres/memoria_descriptiva_m.py figuras <carpeta_pdf_planos>
      recorta las figuras de los planos (sin rótulo) en entregables_mujeres/figuras_memoria_descriptiva/
  python3 herramientas/mujeres/memoria_descriptiva_m.py
      genera entregables_mujeres/MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL_CAR_MUJERES.docx
"""
import copy
import os
import re
import subprocess
import sys
import warnings

import docx
import openpyxl
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANTILLA = os.path.join(RAIZ, 'insumos/wilma/MEMORIA_IISS_CAR_MUJERES.docx')
METRADO = os.path.join(RAIZ, 'entregables_mujeres/METRADO_DRENAJE_PLUVIAL_CAR_MUJERES_09-10-2026_CON_BANCAS.xlsx')
LISTA = os.path.join(RAIZ, 'insumos/wilma/LISTA_PLANOS_ANDFY_MUJERES.txt')
FIG = os.path.join(RAIZ, 'entregables_mujeres/figuras_memoria_descriptiva')
SALIDA = os.path.join(RAIZ, 'entregables_mujeres/MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL_CAR_MUJERES.docx')
FUENTE = 'Swis721 Cn BT'

# ----------------------------------------------------------------------------------------
# Figuras: (archivo, lámina, recorte x0, y0, x1, y1 en fracción de la hoja, dpi)
# El recorte deja fuera el rótulo de cada lámina.
FIGURAS = {
    'RGDPLV-01': ('01', (0.03, 0.06, 0.98, 0.93), 55),
    'PCPLV-01': ('19', (0.04, 0.38, 0.97, 0.70), 75),
    'STP-CG': ('28', (0.05, 0.07, 0.97, 0.63), 120),
    'D-RL': ('29', (0.01, 0.01, 0.99, 0.80), 90),
    'D-ECC': ('32', (0.03, 0.02, 0.98, 0.62), 120),
    'ESDAE-01': ('33', (0.05, 0.05, 0.80, 0.75), 95),
}


def figuras(carpeta):
    from PIL import Image
    os.makedirs(FIG, exist_ok=True)
    tmp = os.path.join(FIG, '_tmp')
    for cod, (num, (x0, y0, x1, y1), dpi) in FIGURAS.items():
        pdf = [f for f in os.listdir(carpeta) if f.startswith(num + ' ') and f.lower().endswith('.pdf')][0]
        subprocess.run(['pdftoppm', '-png', '-r', str(dpi), '-singlefile', os.path.join(carpeta, pdf), tmp], check=True)
        im = Image.open(tmp + '.png').convert('RGB')
        w, h = im.size
        im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
        if im.width > 2400:
            im = im.resize((2400, int(im.height * 2400 / im.width)), Image.LANCZOS)
        im.save(os.path.join(FIG, cod + '.jpg'), quality=88)
        os.remove(tmp + '.png')
        print(cod, im.size)


# ----------------------------------------------------------------------------------------
# Datos del metrado (solo lectura)

def leer_metrado():
    warnings.filterwarnings('ignore')
    wb = openpyxl.load_workbook(METRADO, data_only=True)
    res = []
    for r in wb['RESUMEN'].iter_rows(values_only=True):
        if isinstance(r[0], str) and r[0].startswith('1.4.4'):
            res.append((r[0], r[1], r[2], r[3]))
    ejes = {}
    for r in wb['METRADO DE CURADO'].iter_rows(min_row=7, values_only=True):
        if isinstance(r[1], str) and r[1].startswith('EJE'):
            e = ejes.setdefault(r[1], {'abierto': 0.0, 'tapado': 0.0, 'h': []})
            e['abierto' if r[3] == 'ABIERTA' else 'tapado'] += r[4]
            e['h'] += [r[6], r[7]]
    return res, ejes


def leer_planos():
    planos = []
    for ln in open(LISTA, encoding='utf-8').read().splitlines()[1:]:
        if '|' in ln:
            a, lam = ln.split('|')
            planos.append((a.split()[0], lam.strip()))
    return planos


TITULOS = {
    'RGDPLV-01': 'Red general de drenaje pluvial',
    'ST-DPLV-01': 'Secciones transversales de cunetas (1 de 4)',
    'ST-DPLV-02': 'Secciones transversales de cunetas (2 de 4)',
    'ST-DPLV-03': 'Secciones transversales de cunetas (3 de 4)',
    'ST-DPLV-04': 'Secciones transversales de cunetas (4 de 4)',
    'PL-DPLV-01': 'Perfiles longitudinales de cunetas',
    'IM-ING-DPLV 01': 'Detalle de instalación de montante pluvial – Ingreso 01',
    'IM-ING-DPLV 02': 'Detalle de instalación de montante pluvial – Ingreso 02',
    'PCPLV-01': 'Planta del colector pluvial',
    'PLGC-01': 'Perfil longitudinal general del colector',
    'PLDT-CG T01 03': 'Perfil longitudinal detallado del colector – tramos 01 a 03',
    'PLDT-CG T04 06': 'Perfil longitudinal detallado del colector – tramos 04 a 06',
    'PLDT-CG T07 09': 'Perfil longitudinal detallado del colector – tramos 07 a 09',
    'ST-CG-01': 'Secciones transversales del colector (1 de 2)',
    'ST-CG-02': 'Secciones transversales del colector (2 de 2)',
    'ISM-ST-01': 'Isométricos de las secciones transversales del colector (1 de 2)',
    'ISM-ST-02': 'Isométricos de las secciones transversales del colector (2 de 2)',
    'STP-CG': 'Secciones típicas del colector',
    'D-RL': 'Detalle del registro de limpieza – tapa ciega 0.68 × 0.68 × 0.08 m en rebaje',
    'IC-01': 'Isométricos constructivos del colector',
    'DCTSA-01': 'Detalles de canaleta de techo, soporte y accesorios',
    'D-ECC': 'Detalle del empalme de cuneta al colector y de la junta de dilatación',
    'ESDAE-01': 'Estructura de salida con dos aleros y emboquillado',
    'ISM-MPLV': 'Isométrico del montante pluvial típico',
    'DS-01': 'Caja sumidero de piso: isométrico y detalle (corte, planta y desagregado)',
    'DFC-MPLV-01': 'Detalle de falsa columna para montante pluvial',
    'IDP-BJ': 'Isométrico del drenaje pluvial de la banca de jardinería',
}


def titulo_plano(lam, i_dicbcb):
    if lam.startswith('IM-DPLV'):
        return 'Detalle de instalación de montante pluvial – Edificación %s' % lam.split()[-1]
    if lam.startswith('DT-RDTJ'):
        return 'Detalle de red de drenaje de techo de jardineras (%s de 7)' % int(lam[-2:])
    if lam == 'DI-CBCB':
        return ('Detalle isométrico de canaleta, boquilla, colgador y bajada de la banca' if i_dicbcb == 0 else
                'Cortes A-A y B-B del drenaje pluvial de la banca de jardinería')
    return TITULOS[lam]


# ----------------------------------------------------------------------------------------
# Utilidades de edición del Word

def _limpiar(p):
    """Quita runs, marcadores y revisiones del párrafo, dejando su pPr."""
    for ch in list(p):
        if ch.tag != qn('w:pPr'):
            p.remove(ch)


def _run(modelo_rpr, texto, negrita=None):
    r = docx.oxml.OxmlElement('w:r')
    if modelo_rpr is not None:
        rpr = copy.deepcopy(modelo_rpr)
        for b in rpr.findall(qn('w:b')) + rpr.findall(qn('w:bCs')):
            rpr.remove(b)
        if negrita:
            pos = 1 if rpr.find(qn('w:rFonts')) is not None else 0
            rpr.insert(pos, docx.oxml.OxmlElement('w:bCs'))
            rpr.insert(pos, docx.oxml.OxmlElement('w:b'))
        r.append(rpr)
    t = docx.oxml.OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = texto
    r.append(t)
    return r


class Escritor:
    def __init__(self, d, modelos):
        self.d = d
        self.m = modelos
        self.ancla = d.element.body.find(qn('w:sectPr'))
        self.cap = 2       # ANTECEDENTES (1) y UBICACIÓN (2) vienen de la plantilla
        self.sub = 0
        self.ntab = 0
        self.nfig = 0
        self.toc = []      # (número, título, marcador)

    def _poner(self, el):
        self.ancla.addprevious(el)
        return el

    def _parrafo(self, clave, segmentos, negrita_base=None):
        p = copy.deepcopy(self.m[clave])
        rpr0 = p.find(qn('w:r') + '/' + qn('w:rPr'))
        rpr0 = copy.deepcopy(rpr0) if rpr0 is not None else None
        _limpiar(p)
        if isinstance(segmentos, str):
            segmentos = [(segmentos, negrita_base)]
        for txt, b in segmentos:
            p.append(_run(rpr0, txt, b))
        return self._poner(p)

    def vacio(self):
        return self._poner(copy.deepcopy(self.m['vacio']))

    def capitulo(self, texto):
        self.cap += 1
        self.sub = 0
        p = self._parrafo('h1', texto)
        marca = '_TocDP%02d' % self.cap
        marcar(p, marca, 900 + self.cap)
        self.toc.append((self.cap, texto, marca))
        mantener(p)
        mantener(self.vacio())

    def subtitulo(self, texto):
        self.sub += 1
        mantener(self._parrafo('sub', '%d.%d %s' % (self.cap, self.sub, texto), True))
        mantener(self.vacio())

    def subsub(self, texto):
        self._parrafo('cuerpo', texto, True)

    def p(self, texto):
        """Párrafo de cuerpo; '**x**' marca negritas."""
        seg = [(s, i % 2 == 1) for i, s in enumerate(re.split(r'\*\*', texto)) if s]
        return self._parrafo('cuerpo', seg)

    def viñetas(self, items):
        for it in items:
            seg = [(s, i % 2 == 1) for i, s in enumerate(re.split(r'\*\*', it)) if s]
            self._parrafo('vineta', seg)
        self.vacio()

    def leyenda(self, texto):
        p = self._parrafo('cuerpo', texto, True)
        ppr = p.find(qn('w:pPr'))
        jc = ppr.find(qn('w:jc'))
        jc.set(qn('w:val'), 'center')
        sp = ppr.find(qn('w:spacing'))
        sp.set(qn('w:after'), '60')
        sp.set(qn('w:before'), '120')
        mantener(p)
        return p

    def fuente(self, texto):
        p = self._parrafo('cuerpo', texto)
        for sz in p.iter(qn('w:sz')):
            sz.set(qn('w:val'), '18')
        for sz in p.iter(qn('w:szCs')):
            sz.set(qn('w:val'), '18')
        return p

    def tabla(self, titulo, cab, filas, anchos, alin=None, fuente=None, total=False):
        self.ntab += 1
        self.leyenda('Tabla N.° %02d: %s' % (self.ntab, titulo))
        t = self.d.add_table(rows=1 + len(filas), cols=len(cab))
        t.style = self.d.styles['Table Grid']
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        lay = docx.oxml.OxmlElement('w:tblLayout')
        lay.set(qn('w:type'), 'fixed')
        t._tbl.tblPr.append(lay)
        for j, w in enumerate(anchos):
            t.columns[j].width = Cm(w)
        alin = alin or ['c'] * len(cab)
        for i, fila in enumerate([cab] + filas):
            for j, val in enumerate(fila):
                c = t.cell(i, j)
                c.width = Cm(anchos[j])
                par = c.paragraphs[0]
                par.paragraph_format.space_after = Pt(0)
                par.paragraph_format.space_before = Pt(0)
                par.alignment = (WD_ALIGN_PARAGRAPH.CENTER if (i == 0 or alin[j] == 'c') else
                                 WD_ALIGN_PARAGRAPH.RIGHT if alin[j] == 'r' else WD_ALIGN_PARAGRAPH.LEFT)
                r = par.add_run(str(val))
                r.font.name = FUENTE
                r._element.rPr.rFonts.set(qn('w:hAnsi'), FUENTE)
                r.font.size = Pt(9)
                negr = i == 0 or (total and i == len(filas))
                r.bold = negr
                tcpr = c._tc.get_or_add_tcPr()
                va = docx.oxml.OxmlElement('w:vAlign')
                va.set(qn('w:val'), 'center')
                tcpr.append(va)
                if i == 0 or (total and i == len(filas)):
                    sh = docx.oxml.OxmlElement('w:shd')
                    sh.set(qn('w:val'), 'clear')
                    sh.set(qn('w:color'), 'auto')
                    sh.set(qn('w:fill'), 'D9D9D9' if i == 0 else 'F2F2F2')
                    tcpr.append(sh)
        trpr = t.rows[0]._tr.get_or_add_trPr()
        th = docx.oxml.OxmlElement('w:tblHeader')
        trpr.append(th)
        if fuente:
            self.fuente(fuente)
        self.vacio()
        return t

    def figura(self, cod, titulo, ancho=15.0):
        ruta = os.path.join(FIG, cod + '.jpg')
        if not os.path.exists(ruta):
            return
        self.nfig += 1
        self.d.add_picture(ruta, width=Cm(ancho))
        pic = self.d.paragraphs[-1]
        pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pic.paragraph_format.keep_with_next = True
        self.leyenda('Figura N.° %02d: %s (lámina %s)' % (self.nfig, titulo, cod))
        self.vacio()


def poner_texto(p, texto):
    """Reemplaza el texto de un párrafo existente conservando el formato del primer run con texto."""
    runs = [r for r in p.runs if r.text.strip()]
    if not runs:
        return
    queda = runs[0]._element
    runs[0].text = texto
    for r in p.runs:
        if r._element is not queda and r._element.find(qn('w:drawing')) is None:
            r._element.getparent().remove(r._element)


def mantener(p):
    """Conservar con el siguiente (títulos, leyendas)."""
    ppr = p.find(qn('w:pPr'))
    if ppr.find(qn('w:keepNext')) is None:
        k = docx.oxml.OxmlElement('w:keepNext')
        ps = ppr.find(qn('w:pStyle'))
        if ps is not None:
            ps.addnext(k)
        else:
            ppr.insert(0, k)
    return p


def marcar(p, nombre, ident):
    a = docx.oxml.OxmlElement('w:bookmarkStart')
    a.set(qn('w:id'), str(ident))
    a.set(qn('w:name'), nombre)
    b = docx.oxml.OxmlElement('w:bookmarkEnd')
    b.set(qn('w:id'), str(ident))
    p.find(qn('w:pPr')).addnext(a)
    p.append(b)


def reemplazar_exacto(raiz, tabla):
    for t in raiz.iter(qn('w:t')):
        if t.text in tabla:
            t.text = tabla[t.text]


def indice(d, entradas, paginas):
    """Rehace la tabla de contenido (campo TOC) con los capítulos y sus páginas."""
    sdt = d.element.body.find(qn('w:sdt'))
    cont = sdt.find(qn('w:sdtContent'))
    ps = cont.findall(qn('w:p'))
    titulo, primera, modelo = ps[0], ps[1], ps[2]
    campo = [r for r in primera.findall(qn('w:r'))][:3]          # begin, instrText, separate
    campo = [copy.deepcopy(r) for r in campo]
    for t in campo[1].iter(qn('w:instrText')):
        t.text = ' TOC \\o "1-1" \\h \\z \\u '
    for r in campo:
        for h in r.iter(qn('w:highlight')):
            h.getparent().remove(h)
    for p in ps[1:]:
        cont.remove(p)
    ultimo = titulo
    for i, (num, txt, marca) in enumerate(entradas):
        p = copy.deepcopy(modelo)
        hl = p.find(qn('w:hyperlink'))
        hl.set(qn('w:anchor'), marca)
        ts = list(hl.iter(qn('w:t')))
        ts[0].text = '%d.' % num
        ts[1].text = txt
        ts[2].text = str(paginas.get(marca, ''))
        for it in hl.iter(qn('w:instrText')):
            it.text = ' PAGEREF %s \\h ' % marca
        if i == 0:
            for r in reversed(campo):
                p.find(qn('w:pPr')).addnext(r)
        ultimo.addnext(p)
        ultimo = p
    fin = copy.deepcopy(campo[0])
    for fc in fin.iter(qn('w:fldChar')):
        fc.set(qn('w:fldCharType'), 'end')
    ultimo.append(fin)


def paginas_pdf(pdf, entradas):
    """Página de cada capítulo en el PDF de control (después del índice)."""
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    res = {}
    for pg in range(4, n + 1):
        txt = subprocess.run(['pdftotext', '-f', str(pg), '-l', str(pg), '-layout', pdf, '-'],
                             capture_output=True, text=True).stdout
        for num, t, marca in entradas:
            if marca not in res and re.search(r'^\s*%d\.\s*%s\s*$' % (num, re.escape(t.strip().rstrip(':'))), txt, re.M):
                res[marca] = pg
    return res


def f2(x):
    return '{:,.2f}'.format(x)


# ----------------------------------------------------------------------------------------

def generar(paginas=None):
    resumen, ejes = leer_metrado()
    planos = leer_planos()
    d = docx.Document(PLANTILLA)
    P = d.paragraphs
    body = d.element.body
    nombre = P[42].text.strip()

    # Carátula, recuadro del título y encabezado
    reemplazar_exacto(body, {'INSTALACIONES SANITARIAS': 'DRENAJE PLUVIAL'})
    for s in d.sections:
        for h in (s.header, s.first_page_header, s.even_page_header):
            if not h.is_linked_to_previous:
                reemplazar_exacto(h._element, {'INSTALACIONES SANITARAS SANITARIAS': 'DRENAJE PLUVIAL'})
    marcas_plantilla = [(1, P[64].text.strip(), P[64]._p.find(qn('w:bookmarkStart')).get(qn('w:name'))),
                        (2, P[79].text.strip(), P[79]._p.find(qn('w:bookmarkStart')).get(qn('w:name')))]
    poner_texto(P[19], 'SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL EXPEDIENTE TÉCNICO DE PI:')
    poner_texto(P[36], 'MEMORIA DESCRIPTIVA DE DRENAJE PLUVIAL')

    modelos = {
        'h1': copy.deepcopy(P[79]._p), 'sub': copy.deepcopy(P[66]._p), 'cuerpo': copy.deepcopy(P[68]._p),
        'vineta': copy.deepcopy(P[77]._p), 'vacio': copy.deepcopy(P[67]._p),
    }
    for el in modelos['h1'].iter():
        pass
    for m in modelos.values():
        for bm in m.findall(qn('w:bookmarkStart')) + m.findall(qn('w:bookmarkEnd')):
            m.remove(bm)
    sect_cuerpo = copy.deepcopy(P[345]._p.find(qn('w:pPr')).find(qn('w:sectPr')))

    # 1.1 Introducción (párrafos 68 a 72) y 1.2 Normas (77 y 78)
    intro = [
        'La presente memoria descriptiva corresponde al sistema de drenaje pluvial del proyecto %s Describe '
        'los componentes que captan, conducen y evacúan las aguas de lluvia de las cubiertas, veredas, patios y '
        'áreas libres del Centro de Acogida Residencial, desde los techos hasta la entrega final sobre la berma de '
        'la Carretera Oasis.' % nombre.rstrip('.'),
        'El distrito de Morales presenta lluvias tropicales intensas y de corta duración. Sin un sistema adecuado, '
        'el escurrimiento sobre techos y pavimentos produciría empozamientos, humedad en muros y deterioro de pisos '
        'y accesos, con afectación de la seguridad y de la habitabilidad de la población acogida.',
        'El sistema se ha dimensionado con los parámetros del Estudio Hidrológico y de Drenaje Pluvial del proyecto '
        '(estación CO “Tarapoto”, período de retorno de 25 años) y se desarrolla en el juego de 46 planos de drenaje '
        'pluvial, en las especificaciones técnicas y en el metrado del proyecto, con los cuales la presente memoria '
        'guarda correspondencia.',
        'Por la topografía del sector, el colector pluvial frontal del CAR Mujeres recibe además las aguas pluviales '
        'de dos proyectos colindantes ubicados aguas arriba: CAR Varones (CUI 2705619) y Hogar de Refugio Temporal '
        'para Mujeres Víctimas de Violencia (CUI 2675514). Sus caudales se consideran aportes externos y se toman '
        'como dato de sus respectivas memorias de cálculo.',
        'El drenaje pluvial se ha diseñado con criterios de funcionamiento por gravedad, durabilidad, seguridad de '
        'los usuarios y facilidad de operación y mantenimiento, y queda íntegramente dentro del lindero del predio.',
    ]
    for p, t in zip(P[68:73], intro):
        poner_texto(p, t)

    normas = [
        [('Reglamento Nacional de Edificaciones, D.S. N.° 011-2006-VIVIENDA y modificatorias.', None)],
        [('Norma Técnica ', None), ('CE.040 “Drenaje Pluvial”', True), (', aprobada mediante R.M. N.° 126-2021-VIVIENDA.', None)],
        [('Norma ', None), ('IS.010', True), (' “Instalaciones Sanitarias para Edificaciones”.', None)],
        [('Norma ', None), ('E.020', True), (' “Cargas”.', None)],
        [('Norma ', None), ('E.050', True), (' “Suelos y Cimentaciones”.', None)],
        [('Norma ', None), ('E.060', True), (' “Concreto Armado”.', None)],
        [('Manual de Hidrología, Hidráulica y Drenaje del Ministerio de Transportes y Comunicaciones (referencia metodológica complementaria).', None)],
        [('AASHTO LRFD Bridge Design Specifications, para las cargas de rueda en los cruces vehiculares del colector.', None)],
    ]
    modelo_norma = P[77]._p
    rpr_n = copy.deepcopy(modelo_norma.find(qn('w:r') + '/' + qn('w:rPr')))
    previo = P[76]._p
    for segs in normas:
        np_ = copy.deepcopy(modelo_norma)
        _limpiar(np_)
        for t, b in segs:
            np_.append(_run(rpr_n, t, b))
        previo.addnext(np_)
        previo = np_
    for p in (P[77], P[78]):
        p._p.getparent().remove(p._p)

    # Ubicación: se agrega acceso y referencia de coordenadas después de "ZONA"
    zona = P[87]._p
    for t in reversed([
        'ACCESO: desde el área urbana de Morales por la carretera Fernando Belaúnde Terry hasta el sector El Tumi; '
        'luego por una trocha carrozable de unos 340 m, conectada con la vía de Evitamiento. El frente sur del predio '
        'da a la Carretera Oasis, donde se ubica el colector pluvial frontal.',
        'COORDENADAS DE REFERENCIA (UTM WGS84, zona 18 Sur): registro R-01 del colector, E 345 666.974 y '
        'N 9 282 776.560; salida del colector, E 345 550.345 y N 9 282 705.120.',
    ]):
        np_ = copy.deepcopy(modelos['cuerpo'])
        rpr = copy.deepcopy(np_.find(qn('w:r') + '/' + qn('w:rPr')))
        _limpiar(np_)
        np_.append(_run(rpr, t))
        zona.addnext(np_)

    # Se elimina el contenido sanitario (desde FINALIDAD hasta el final) y se deja la sección del cuerpo
    inicio = P[89]._p
    hijos = list(body)
    i0 = hijos.index(inicio)
    for el in hijos[i0:]:
        body.remove(el)
    body.append(sect_cuerpo)

    W = Escritor(d, modelos)

    # 3. FINALIDAD Y OBJETIVOS ------------------------------------------------------------
    W.capitulo('FINALIDAD Y OBJETIVOS DEL PROYECTO')
    W.subtitulo('FINALIDAD')
    W.p('Dotar al Centro de Acogida Residencial de un sistema de drenaje pluvial que capte, conduzca y evacúe por '
        'gravedad las aguas de lluvia de la edificación y de sus áreas exteriores, sin empozamientos ni ingreso de '
        'agua a los ambientes, y que entregue el caudal total al exterior desde una estructura ubicada dentro del '
        'lindero del predio.')
    W.vacio()
    W.subtitulo('OBJETIVOS')
    W.viñetas([
        'Captar el agua de las cubiertas mediante canaletas de plancha galvanizada y conducirla por montantes de '
        'PVC Ø 4" hasta las cunetas de piso.',
        'Recolectar el escurrimiento de veredas, patios y pasadizos mediante cunetas de concreto armado con rejilla '
        'metálica y sumideros de piso.',
        'Conducir el caudal de las cunetas al colector pluvial frontal, estructura cubierta que recorre el frente del '
        'predio bajo la vereda, paralela a la Carretera Oasis.',
        'Recibir en el colector los aportes de CAR Varones (CUI 2705619) y del Hogar de Refugio Temporal para '
        'Mujeres Víctimas de Violencia (CUI 2675514), sin una segunda estructura paralela en el mismo frente.',
        'Evacuar el caudal total de diseño (822.9 L/s) mediante una estructura de salida con aleros y emboquillado '
        'de piedra, protegida contra la erosión.',
        'Facilitar la inspección y la limpieza del sistema mediante registros con tapa removible, tapas de '
        'inspección y rejillas desmontables.',
    ])

    # 4. SITUACIÓN ACTUAL -----------------------------------------------------------------
    W.capitulo('SITUACIÓN ACTUAL')
    W.p('El área destinada al proyecto corresponde a un terreno sin edificaciones ni infraestructura de drenaje '
        'pluvial. Las aguas de lluvia escurren superficialmente según la pendiente natural del terreno, en dirección '
        'al frente sur del predio, sobre la Carretera Oasis; asimismo, se reporta escurrimiento pluvial por el '
        'margen derecho del terreno.')
    W.p('Frente al predio no se dispone de un sistema público de alcantarillado pluvial al cual conectar las aguas '
        'de la edificación. La entrega se realiza sobre la berma de la Carretera Oasis, cuya cresta (258.54 m s. n. m.) '
        'controla el nivel del agua en la salida del colector.')
    W.p('Los terrenos de CAR Varones y del Hogar de Refugio Temporal, ubicados aguas arriba, drenan hacia el frente '
        'del CAR Mujeres. Por ello, el proyecto contempla un sistema de drenaje pluvial completo, desde la captación '
        'en los techos hasta la descarga final, con capacidad para recibir esos aportes.')
    W.vacio()

    # 5. PARÁMETROS DE DISEÑO -------------------------------------------------------------
    W.capitulo('PARÁMETROS Y CRITERIOS DE DISEÑO')
    W.p('Los parámetros hidrológicos e hidráulicos provienen del Estudio Hidrológico y de Drenaje Pluvial del '
        'proyecto y se resumen a continuación:')
    W.tabla('Parámetros de diseño del sistema de drenaje pluvial',
            ['Parámetro', 'Valor adoptado', 'Criterio o fuente'],
            [['Estación pluviométrica', 'CO “Tarapoto” (SENAMHI), 1999–2024', 'Serie de 26 años'],
             ['Distribución de mejor ajuste', 'Log-Normal (D = 0.0894)', 'Prueba de Kolmogorov-Smirnov'],
             ['Período de retorno', '25 años', 'Numeral 11.1 de la Norma CE.040'],
             ['Precipitación máxima en 24 h', '121.81 mm', 'Distribución Log-Normal, T = 25 años'],
             ['Intensidad: canaletas, montantes, sumideros y cunetas', '210.98 mm/h', 'Dick-Peschke, D = 10 min'],
             ['Intensidad: colector pluvial frontal', '155.66 mm/h', 'Dick-Peschke, tc = 10 + 3 + 2 = 15 min'],
             ['Coeficiente de escorrentía de elementos menores', 'C = 0.88', 'Concreto y techo (Tabla 1.a, Anexo I, CE.040)'],
             ['Coeficiente ponderado del predio (colector)', 'C = 0.704', 'Σ C·A / A por tipo de superficie'],
             ['Factor de seguridad', '1.15', 'Margen frente a variaciones de la lluvia'],
             ['Método de cálculo de caudales', 'Racional: Q = C·I·A / 3 600', 'Q en L/s, I en mm/h, A en m²'],
             ['Rugosidad de Manning', 'n = 0.013 canaletas; n = 0.015 cunetas y colector', 'Plancha galvanizada / concreto in situ'],
             ['Pendiente mínima', 'Canaletas 1.0 %; cunetas 0.5 %; colector 0.302 %', 'Funcionamiento por gravedad'],
             ['Diámetro de montante', 'PVC Ø 4" (requerido 2.468" a 3.821")', 'Ecuación de Wyly-Eaton']],
            [5.2, 4.9, 5.0], alin=['l', 'c', 'l'],
            fuente='Fuente: Estudio Hidrológico y de Drenaje Pluvial del CAR Mujeres (CUI 2717013).')
    W.p('La intensidad de **210.98 mm/h**, correspondiente a una duración de 10 minutos, se aplica a los elementos '
        'de captación y conducción menores (canaletas, montantes, sumideros y cunetas). Para el colector pluvial '
        'frontal, cuyo tiempo de concentración es de 15 minutos (10 minutos de entrada, 3 minutos de recorrido en '
        'las cunetas y 2 minutos en el colector), corresponde la intensidad de **155.66 mm/h**, conforme a lo '
        'sustentado en el estudio hidrológico.')
    W.p('Las superficies del predio y sus coeficientes de escorrentía son las siguientes:')
    W.tabla('Superficies del predio y coeficientes de escorrentía',
            ['Tipo de superficie', 'Área (m²)', 'Participación (%)', 'C (T = 25 años)'],
            [['Techos y coberturas TR4', '3,654.58', '48.79', '0.88'],
             ['Áreas libres de concreto frotachado', '816.87', '10.91', '0.88'],
             ['Estacionamiento pavimentado', '812.65', '10.85', '0.86'],
             ['Áreas verdes', '2,206.56', '29.46', '0.29 – 0.40'],
             ['Total de superficies identificadas', '7,490.66', '100.00', '—']],
            [6.0, 2.9, 3.0, 3.1], alin=['l', 'r', 'r', 'c'], total=True,
            fuente='Fuente: Estudio Hidrológico y de Drenaje Pluvial del CAR Mujeres. Para el colector se emplea '
                   'el área de 7,491.56 m² de las fichas de áreas aportantes.')

    # 6. DESCRIPCIÓN DEL SISTEMA ----------------------------------------------------------
    m = {it: (desc, und, q) for it, desc, und, q in resumen}
    W.capitulo('DESCRIPCIÓN DEL SISTEMA DE DRENAJE PLUVIAL')
    W.subtitulo('ESQUEMA GENERAL')
    W.p('El sistema funciona íntegramente por gravedad y sigue la secuencia: **techo → canaleta → montante → '
        'cuneta → colector pluvial frontal → estructura de salida**. Las áreas libres pavimentadas drenan '
        'directamente a las cunetas mediante sus rejillas o mediante sumideros de piso conectados con tubería '
        'de PVC.')
    W.p('Para el dimensionamiento se han considerado 13 sectores de aporte: la losa deportiva, las edificaciones '
        '01 a 10 y las guardianías 1 y 2. Los caudales de techo por descarga varían entre 1.277 y 6.145 L/s y los '
        'caudales en las cunetas entre 3.156 y 42.993 L/s. La red general se muestra en la lámina RGDPLV-01.')
    W.figura('RGDPLV-01', 'Red general de drenaje pluvial del CAR Mujeres', ancho=14.5)

    W.subtitulo('CANALETAS DE TECHO')
    W.p('Las cubiertas descargan en canaletas de plancha de acero galvanizado de 0.9 mm de espesor, sección '
        '0.25 m × 0.20 m, con pendiente mínima de 1.0 % hacia las boquillas de conexión a los montantes. Las '
        'canaletas se fijan con soportes de platina de fierro galvanizado de 1" × 1/8" y se cierran en sus extremos '
        'con tapas laterales de plancha galvanizada. La verificación hidráulica de cada sector se presenta en el '
        'estudio hidrológico y los detalles en la lámina DCTSA-01.')
    W.viñetas([
        'Canaleta de plancha galvanizada e = 0.9 mm, 0.25 m × 0.20 m: **%s m**.' % f2(m['1.4.4.5.1.3'][2]),
        'Soportes de platina F°G° 1" × 1/8": **%d und**; tapas laterales: **%d und**; boquillas a montante Ø 4": **%d und**.'
        % (m['1.4.4.5.1.4'][2], m['1.4.4.5.1.5'][2], m['1.4.4.5.1.6'][2]),
    ])

    W.subtitulo('MONTANTES PLUVIALES Y FALSAS COLUMNAS')
    W.p('Los montantes conducen verticalmente el agua de las canaletas hasta las cunetas. Con la ecuación de '
        'Wyly-Eaton se obtienen diámetros requeridos de 2.468" a 3.821"; se adopta tubería de **PVC Ø 4"** en todos '
        'los sectores. Los montantes se sujetan a la estructura con abrazaderas de fierro galvanizado y, en su parte '
        'inferior, quedan protegidos por una falsa columna de concreto f\'c = 175 kg/cm² de 0.20 m × 0.15 m × 1.30 m. '
        'La instalación de cada edificación se detalla en las láminas IM-DPLV 01 a 10, IM-ING-DPLV 01 y 02, '
        'ISM-MPLV y DFC-MPLV-01.')
    W.viñetas([
        'Montante de tubería PVC Ø 4": **%s m**.' % f2(m['1.4.4.5.1.1'][2]),
        'Falsa columna para montante de 0.20 m × 0.15 m × 1.30 m: **%d und** (concreto %s m³, encofrado %s m², acero %s kg).'
        % (m['1.4.4.5.1.2'][2], f2(m['1.4.4.5.1.2.1'][2]), f2(m['1.4.4.5.1.2.2'][2]), f2(m['1.4.4.5.1.2.3'][2])),
        'Accesorios: %d codos PVC Ø 4" × 90°, %d codos × 45°, %d colgadores y %d abrazaderas de F°G°.'
        % (m['1.4.4.5.3.1'][2], m['1.4.4.5.3.2'][2], m['1.4.4.5.3.3'][2], m['1.4.4.5.3.4'][2]),
    ])

    W.subtitulo('DRENAJE DE TECHOS DE JARDINERAS Y BANCAS')
    W.p('Los techos de las jardineras y de las bancas de jardinería cuentan con canaletas de plancha de aluzinc de '
        '0.50 mm, de sección interior 0.18 m (ancho) × 0.20 m (alto), con tapas laterales, soportes de platina y '
        'boquillas de conexión a tubería PVC Ø 4", que entregan a la red de piso. Los detalles se presentan en las '
        'láminas DT-RDTJ-01 a 07, IDP-BJ y DI-CBCB.')
    W.viñetas([
        'Canaleta de aluzinc 0.18 m × 0.20 m: **%s m**; tapas laterales: **%d und**; soportes: **%d und**; boquillas: **%d und**.'
        % (f2(m['1.4.4.5.4.1'][2]), m['1.4.4.5.4.2'][2], m['1.4.4.5.4.3'][2], m['1.4.4.5.4.4'][2]),
    ])

    W.subtitulo('SUMIDEROS Y RED DE PISO')
    W.p('En patios, pasadizos y áreas pavimentadas alejadas de las cunetas se ubican sumideros metálicos con '
        'platina de 1" × 3/16", alojados en cajas de concreto y conectados a las cunetas mediante tubería de PVC-CP '
        'Ø 4". El detalle de la caja sumidero (isométrico, corte, planta y desagregado de materiales) se muestra en '
        'las láminas DS-01 y DS-02.')
    W.viñetas([
        'Sumidero metálico con platina 1" × 3/16": **%d und**.' % m['1.4.4.5.2.2'][2],
        'Tubería PVC-CP Ø 4": **%s m**, con %d codos de 90° y %d tees de 4".'
        % (f2(m['1.4.4.5.2.1'][2]), m['1.4.4.5.2.3'][2], m['1.4.4.5.2.4'][2]),
    ])

    W.subtitulo('CUNETAS DE CONCRETO ARMADO')
    W.p('Las cunetas recorren los costados de las edificaciones y de las áreas pavimentadas. Son de sección '
        'rectangular en concreto armado f\'c = 175 kg/cm², con ancho libre de 0.40 m, muros y losa de fondo de 0.10 m '
        '(ancho exterior 0.60 m), acero de refuerzo de 3/8" y solado de concreto f\'c = 100 kg/cm². Su pendiente '
        'longitudinal mínima es de 0.5 %, por lo que la altura interior aumenta desde 0.25 m en los inicios hasta '
        '0.88 m en los tramos finales. La sección de diseño es de 0.40 m × 0.30 m en edificaciones y guardianías y '
        'de 0.40 m × 0.25 m en la losa deportiva.')
    W.p('En los tramos abiertos se coloca rejilla metálica de platina de 1" × 3/16" con marco de ángulo de 1" × 1" '
        '× 3/16"; en los cruces de ingreso y de circulación la cuneta es tapada con losa de concreto armado. Las '
        'cunetas tienen juntas de dilatación de 1" con sellador asfáltico cada 3.00 m y tapas de inspección de '
        '0.60 m × 0.60 m. Las secciones y perfiles se muestran en las láminas ST-DPLV-01 a 04 y PL-DPLV-01.')
    W.p('Las cunetas de los Ejes 02, 07, 10 y 12 entregan al colector pluvial frontal en los registros R-01, R-05, '
        'R-06 y R-07; las demás cunetas descargan en ellas según el sentido de flujo indicado en la lámina RGDPLV-01.')
    filas = []
    tot = [0, 0, 0]
    for e in sorted(ejes, key=lambda s: int(s.split()[1])):
        v = ejes[e]
        lt = v['abierto'] + v['tapado']
        tot = [tot[0] + lt, tot[1] + v['abierto'], tot[2] + v['tapado']]
        filas.append(['Eje %02d' % int(e.split()[1]), f2(lt), f2(v['abierto']), f2(v['tapado']) if v['tapado'] else '—',
                      '%.2f – %.2f' % (min(v['h']), max(v['h']))])
    filas.append(['TOTAL', f2(tot[0]), f2(tot[1]), f2(tot[2]), '—'])
    W.tabla('Cunetas de concreto armado por eje',
            ['Cuneta', 'Longitud (m)', 'Tramo abierto con rejilla (m)', 'Tramo tapado (m)', 'Altura interior (m)'],
            filas, [2.4, 2.6, 3.6, 3.0, 3.4], alin=['c', 'r', 'r', 'r', 'c'], total=True,
            fuente='Fuente: metrado de drenaje pluvial del proyecto (hojas de curado y rejillas).')

    # 7. COLECTOR PLUVIAL FRONTAL ---------------------------------------------------------
    W.capitulo('COLECTOR PLUVIAL FRONTAL')
    W.subtitulo('DESCRIPCIÓN GENERAL')
    W.p('El colector pluvial frontal recorre el frente del predio paralelo a la Carretera Oasis. Recibe las cunetas '
        'de los Ejes 02, 07, 10 y 12 y los aportes externos de los proyectos colindantes. Se emplaza íntegramente '
        'dentro del lindero del predio, bajo la vereda frontal, con su eje a 0.85 m del lindero y sin ocupar la '
        'Carretera Oasis. Sus características principales son:')
    W.viñetas([
        '**Longitud:** 139.08 m, desde el Eje 02 (0+000.00) hasta la estructura de salida (0+139.08).',
        '**Sección:** rectangular de concreto armado f\'c = 210 kg/cm², con ancho interior b = 1.50 m.',
        '**Cotas de fondo:** 258.72 m s. n. m. en el Eje 02 y 258.30 m s. n. m. en la salida, con pendiente uniforme S = 0.302 %.',
        '**Colector cubierto:** losa superior vaciada monolíticamente con los muros, que sirve de vereda, con 15 registros de limpieza.',
        '**Tramo en vereda (0+000.00 a 0+078.42):** losa superior a nivel de vereda (NPT +259.25), con altura interior de 0.43 a 0.67 m.',
        '**Tramo final (0+078.42 a 0+139.08):** fuera de la vereda, con altura interior constante de 0.60 m.',
        '**Estructura de salida:** dos aleros a 45°, emboquillado de piedra y uña de concreto ciclópeo, con descarga hacia la berma de la Carretera Oasis.',
    ])
    W.figura('PCPLV-01', 'Planta del colector pluvial frontal')

    W.subtitulo('SECCIONES DEL COLECTOR')
    W.p('El espesor de los elementos y el refuerzo varían según la carga que actúa sobre la losa superior '
        '(peatonal en la vereda, autos en los estacionamientos y camión en el ingreso secundario):')
    W.tabla('Secciones del colector pluvial frontal',
            ['Zona', 'Progresivas', 'Muros / losa de fondo / losa superior (m)', 'Altura interior (m)', 'Refuerzo'],
            [['Vereda', '0+000.00 – 0+078.42 (fuera de cruces)', '0.10 / 0.10 / 0.10', '0.43 – 0.67', 'Marco 3/8" @ 0.20; long. 3/8" @ 0.25'],
             ['Cruce de autos', '0+002.74 – 0+018.45 y 0+035.04 – 0+051.86', '0.10 / 0.10 / 0.10', 'Variable', 'Marco 3/8" @ 0.15'],
             ['Cruce de camiones', '0+054.00 – 0+060.00', '0.15 / 0.20 / 0.20', 'Variable', 'Doble marco 1/2" @ 0.15; long. 3/8" @ 0.20'],
             ['Tramo final', '0+078.42 – 0+139.08', '0.10 / 0.10 / 0.10', '0.60', 'Marco 3/8" @ 0.20; long. 3/8" @ 0.25']],
            [2.4, 3.6, 3.2, 2.1, 3.8], alin=['l', 'c', 'c', 'c', 'l'],
            fuente='Fuente: láminas STP-CG, ST-CG-01 y ST-CG-02. Solado de concreto f\'c = 100 kg/cm², e = 0.05 m, en todo el recorrido.')
    W.figura('STP-CG', 'Secciones típicas del colector')

    W.subtitulo('REGISTROS DE LIMPIEZA')
    W.p('El colector cuenta con 15 registros de limpieza (R-01 a R-15) ubicados en cada empalme de cuneta, en los '
        'quiebres y a 12.00 m como máximo entre sí. Cada registro tiene una **tapa ciega** de concreto armado '
        'f\'c = 210 kg/cm² de 0.68 m × 0.68 m × 0.08 m, con parrilla de 3/8" @ 0.10 m y borde engrosado de '
        '0.15 m × 0.10 m con 2 Ø 1/2" por lado, asentada en un rebaje de 0.70 m × 0.70 m × 0.08 m de la losa '
        'superior (asiento de 0.05 m y holgura de 1 cm por lado), sin marco ni contramarco metálico. Para su '
        'retiro dispone de 2 asas de fierro liso de 1/2" alojadas en cajuelas de 0.19 m × 0.06 m × 0.03 m; su peso '
        'aproximado es de 89 kg. El detalle se presenta en la lámina D-RL.')
    reg = [('R-01', '0+000.00', '345666.974', '9282776.560', '258.720', '259.250'),
           ('R-02', '0+009.49', '345659.754', '9282770.402', '258.691', '259.250'),
           ('R-03', '0+018.98', '345652.535', '9282764.241', '258.663', '259.250'),
           ('R-04', '0+028.46', '345645.351', '9282758.056', '258.634', '259.250'),
           ('R-05', '0+037.95', '345638.159', '9282751.865', '258.605', '259.250'),
           ('R-06', '0+049.38', '345629.496', '9282744.408', '258.571', '259.250'),
           ('R-07', '0+060.15', '345621.036', '9282737.745', '258.538', '259.250'),
           ('R-08', '0+069.28', '345613.827', '9282732.143', '258.511', '259.250'),
           ('R-09', '0+078.42', '345606.610', '9282726.535', '258.483', '259.183'),
           ('R-10', '0+087.77', '345598.252', '9282722.343', '258.455', '259.155'),
           ('R-11', '0+097.12', '345589.894', '9282718.152', '258.427', '259.127'),
           ('R-12', '0+106.47', '345581.537', '9282713.960', '258.398', '259.098'),
           ('R-13', '0+115.83', '345572.843', '9282710.496', '258.370', '259.070'),
           ('R-14', '0+126.45', '345562.679', '9282707.418', '258.338', '259.038'),
           ('R-15', '0+137.08', '345552.349', '9282705.156', '258.306', '259.006'),
           ('Salida', '0+139.08', '345550.345', '9282705.120', '258.300', '—')]
    W.tabla('Registros de limpieza y salida del colector',
            ['Punto', 'Progresiva', 'Este (m)', 'Norte (m)', 'Cota de fondo', 'Cota de tapa'],
            [list(r) for r in reg], [1.8, 2.2, 2.8, 3.0, 2.6, 2.6],
            fuente='Fuente: lámina PCPLV-01. Coordenadas UTM WGS84, zona 18 Sur; cotas en m s. n. m.; cota de tapa = cara superior de la tapa (NPT).')
    W.figura('D-RL', 'Registro de limpieza con tapa ciega en rebaje')

    W.subtitulo('EMPALMES DE CUNETAS AL COLECTOR')
    W.p('Cada cuneta entrega al colector bajo un registro, a través de una ventana de 0.40 m × 0.30 m abierta en '
        'el muro del lado del predio. La cota de fondo de la cuneta queda por encima de la cota de fondo del colector, '
        'de modo que el agua cae libremente sin remanso hacia la cuneta:')
    W.tabla('Empalmes de cunetas al colector',
            ['Cuneta', 'Registro', 'Progresiva', 'Cota de fondo de cuneta', 'Cota de fondo del colector', 'Caída (m)'],
            [['Eje 02', 'R-01', '0+000.00', '258.73', '258.720', '0.01'],
             ['Eje 07', 'R-05', '0+037.95', '258.74', '258.605', '0.13'],
             ['Eje 10', 'R-06', '0+049.38', '258.74', '258.571', '0.17'],
             ['Eje 12', 'R-07', '0+060.15', '258.80', '258.538', '0.26']],
            [2.0, 2.0, 2.4, 3.2, 3.2, 2.2],
            fuente='Fuente: lámina D-ECC. Cotas en m s. n. m.')
    W.figura('D-ECC', 'Empalme de cuneta al colector y junta de dilatación')

    W.subtitulo('JUNTAS')
    W.viñetas([
        '**Juntas de dilatación** de 1" con sellador asfáltico cada 4.00 m a lo largo del colector (33 und), '
        'en muros, losa de fondo y losa superior: **%s m**.' % f2(m['1.4.4.6.5.2'][2]),
        '**Junta de 1" con tecnopor** entre la losa superior del colector y el piso adyacente, en el tramo de vereda: '
        '**%s m**.' % f2(m['1.4.4.6.5.3'][2]),
    ])

    W.subtitulo('FUNCIONAMIENTO HIDRÁULICO')
    W.p('La capacidad del colector se verificó con la ecuación de Manning (n = 0.015) y con el perfil de flujo '
        'gradualmente variado, considerando el caudal acumulado en cada empalme:')
    W.tabla('Caudal acumulado en el colector',
            ['Punto', 'Progresiva', 'Aporte (L/s)', 'Caudal acumulado (L/s)'],
            [['Eje 02 (aportes externos + Eje 02)', '0+000.00', '626.2', '626.2'],
             ['Eje 07', '0+037.95', '65.6', '691.8'],
             ['Eje 10', '0+049.38', '65.6', '757.4'],
             ['Eje 12 hasta la salida', '0+060.15', '65.6', '822.9']],
            [5.6, 2.8, 2.8, 3.8], alin=['l', 'c', 'r', 'r'],
            fuente='Fuente: Estudio Hidrológico y de Drenaje Pluvial del CAR Mujeres, capítulo del colector.')
    W.p('En la salida, el agua vierte sobre la berma hasta la cresta de la Carretera Oasis (258.54 m s. n. m.), que '
        'actúa como vertedero de cresta ancha (ancho efectivo 4.00 m, C = 1.70) y fija el nivel del agua en '
        '258.785 m s. n. m. (carga H = 0.245 m). Con esa condición, el flujo es **subcrítico** en todo el recorrido '
        '(número de Froude de 0.51 a 0.74), con velocidades de 1.02 a 1.43 m/s, un llenado máximo de 81.5 % de la '
        'altura interior y un borde libre mínimo de 0.087 m en el Eje 02. En el cruce de camiones (0+054.00 a 0+060.00) la '
        'cara inferior de la losa desciende 0.10 m por su mayor espesor y el borde libre mínimo es de 0.091 m.')
    W.tabla('Perfil de cotas de fondo y nivel de agua',
            ['Punto', 'Progresiva', 'Cota de fondo', 'Nivel de agua'],
            [['Eje 02', '0+000.00', '258.720', '259.063'], ['Eje 07', '0+037.95', '258.605', '259.000'],
             ['Eje 10', '0+049.38', '258.571', '258.966'], ['Eje 12', '0+060.15', '258.538', '258.923'],
             ['Inicio del tramo final', '0+078.42', '258.483', '258.877'], ['—', '0+116.00', '258.370', '258.810'],
             ['Salida', '0+139.08', '258.300', '258.785']],
            [4.4, 3.2, 3.4, 3.4], alin=['l', 'c', 'c', 'c'],
            fuente='Fuente: Estudio Hidrológico y de Drenaje Pluvial; láminas PLGC-01 y PLDT-CG. Cotas en m s. n. m.')

    W.subtitulo('ESTRUCTURA DE SALIDA')
    W.p('La descarga se resuelve con dos aleros de concreto armado f\'c = 210 kg/cm² a 45° (e = 0.15 m, longitud '
        '1.00 m y altura de 0.70 m en el cabezal a 0.45 m en el extremo), monolíticos con el extremo del colector; '
        'un emboquillado de piedra de 0.20 m de espesor con concreto f\'c = 140 kg/cm² entre los aleros; y una uña de '
        'concreto ciclópeo f\'c = 140 kg/cm² + 30 % P.M. de 0.35 m × 0.65 m en el extremo, que protege la estructura '
        'contra la socavación. Los últimos 4.00 m del colector se desvían 0.85 m hacia el interior para que toda la '
        'estructura quede dentro del lindero. El detalle se presenta en la lámina ESDAE-01.')
    W.p('El cruce de las aguas hacia el otro lado de la Carretera Oasis (badén o alcantarilla) queda fuera del alcance '
        'del presente proyecto, que entrega el caudal sobre la berma dentro del lindero; su solución corresponde a la '
        'entidad a cargo de la vía.')
    W.figura('ESDAE-01', 'Estructura de salida con dos aleros y emboquillado')

    W.subtitulo('VERIFICACIÓN ESTRUCTURAL')
    W.p('Los elementos del colector se verificaron a flexión y corte según la Norma E.060. Las cargas se tomaron de '
        'la Norma E.020 (sobrecarga peatonal en la vereda) y de la AASHTO LRFD para las cargas de rueda en los '
        'cruces vehiculares: auto en los estacionamientos y camión HL-93 en el ingreso secundario. La presión '
        'máxima de contacto sobre el suelo, en el cruce de camiones con el canal lleno, es de 0.37 kg/cm², inferior '
        'a la capacidad admisible considerada de 0.80 kg/cm².')
    W.vacio()

    # 8. APORTES EXTERNOS -----------------------------------------------------------------
    W.capitulo('APORTES DE PROYECTOS COLINDANTES')
    W.p('Aguas arriba del colector se ubican los proyectos CAR Varones (CUI 2705619) y Hogar de Refugio Temporal '
        'para Mujeres Víctimas de Violencia (CUI 2675514). Ambos constituyen inversiones independientes del presente '
        'proyecto, con expedientes técnicos propios. Como la topografía conduce sus aguas pluviales hacia el frente '
        'del CAR Mujeres, el colector se ha dimensionado para recibirlas, con el fin de evitar una segunda estructura '
        'paralela en el mismo frente.')
    W.p('Los caudales de esos proyectos se toman como dato de sus memorias de cálculo de drenaje pluvial, con la '
        'misma intensidad de diseño del colector (155.66 mm/h) y el mismo factor de seguridad (1.15):')
    W.tabla('Caudales que recibe el colector pluvial frontal',
            ['Proyecto', 'Área (m²)', 'C ponderado', 'Q (L/s)', 'Ingreso al colector'],
            [['CAR Varones (CUI 2705619) – aporte externo', '6,752.03', '0.771', '258.7', 'Eje 02 (0+000.00)'],
             ['Hogar de Refugio Temporal (CUI 2675514) – aporte externo', '7,520.41', '0.807', '301.9', 'Eje 02 (0+000.00)'],
             ['CAR Mujeres (CUI 2717013) – presente proyecto', '7,491.56', '0.704', '262.3', 'Ejes 02, 07, 10 y 12'],
             ['TOTAL EN LA SALIDA', '21,764.00', '0.760', '822.9', '—']],
            [5.8, 2.2, 2.0, 1.8, 3.2], alin=['l', 'r', 'c', 'r', 'c'], total=True,
            fuente='Fuente: Estudio Hidrológico y de Drenaje Pluvial del CAR Mujeres; memorias de cálculo de CAR Varones y del Hogar de Refugio Temporal.')
    W.p('Los dos aportes externos suman **560.7 L/s** (258.7 + 301.9 L/s), que llegan juntos al registro R-01 '
        '(Eje 02). Las condiciones de entrega que deberán respetar esos proyectos son las siguientes:')
    W.viñetas([
        'Entrega en el registro R-01 (Eje 02, 0+000.00), con cota de fondo de llegada igual o mayor que 258.72 m s. n. m.',
        'Caudal conjunto de entrega no mayor que 560.7 L/s.',
        'Cualquier cambio en las áreas, coeficientes o cotas de esos proyectos deberá comunicarse para verificar nuevamente el colector.',
    ])

    # 9. METAS FÍSICAS --------------------------------------------------------------------
    W.capitulo('METAS FÍSICAS')
    W.p('Las metas físicas del sistema de drenaje pluvial corresponden al metrado del proyecto:')
    for titulo, pref in (('Metas físicas del sistema de drenaje pluvial (cunetas y redes)', None),
                         ('Metas físicas del colector pluvial frontal', '1.4.4.6')):
        filas = []
        for it, desc, und, q in resumen:
            es_col = it.startswith('1.4.4.6')
            if (pref and not es_col) or (not pref and es_col) or it in ('1.4.4', '1.4.4.6'):
                continue
            if und is None:
                filas.append([it, desc, '', ''])
            else:
                filas.append([it, desc, und, f2(q)])
        t = W.tabla(titulo, ['Ítem', 'Descripción', 'Und.', 'Metrado'], filas, [2.7, 9.0, 1.3, 2.0],
                    alin=['l', 'l', 'c', 'r'], fuente='Fuente: metrado de drenaje pluvial del proyecto (hoja RESUMEN).')
        for i, f in enumerate(filas, start=1):
            if f[2] == '':
                for c in t.rows[i].cells:
                    for r in c.paragraphs[0].runs:
                        r.bold = True

    # 10. OPERACIÓN Y MANTENIMIENTO -------------------------------------------------------
    W.capitulo('OPERACIÓN Y MANTENIMIENTO')
    W.viñetas([
        'Limpiar canaletas, boquillas y montantes antes del inicio de la temporada de lluvias y después de cada lluvia intensa, retirando hojas y sedimentos.',
        'Retirar periódicamente las rejillas de las cunetas y las rejillas de los sumideros para limpiar los sedimentos acumulados.',
        'Inspeccionar el colector al menos dos veces al año a través de los registros de limpieza; las tapas ciegas se retiran con sus asas, entre dos personas y con herramienta adecuada, y se recolocan limpiando el asiento del rebaje.',
        'Revisar el estado del sellador de las juntas de dilatación y reponerlo cuando presente desprendimientos o fisuras.',
        'Mantener libre de obstáculos y de vegetación la estructura de salida y la berma de la Carretera Oasis, y reponer las piedras del emboquillado que se desprendan.',
        'No arrojar residuos sólidos ni desmonte a las cunetas, sumideros o registros, ni conectar al sistema pluvial descargas de aguas residuales.',
    ])

    # 11. CONCLUSIONES --------------------------------------------------------------------
    W.capitulo('CONCLUSIONES')
    W.viñetas([
        'El proyecto cuenta con un sistema integral de drenaje pluvial que funciona por gravedad desde los techos hasta la descarga final, dentro del lindero del predio.',
        'Las canaletas de plancha galvanizada de 0.25 m × 0.20 m y los montantes de PVC Ø 4" tienen capacidad para los caudales de techo calculados con la intensidad de 210.98 mm/h y el factor de seguridad de 1.15.',
        'Las cunetas de concreto armado de 0.40 m de ancho libre, con pendiente mínima de 0.5 %%, conducen el agua de techos y pavimentos hasta el colector, con un total de %s m en 12 ejes.' % f2(tot[0]),
        'El colector pluvial frontal de 1.50 m de ancho y 139.08 m de longitud conduce 822.9 L/s, incluidos los aportes de CAR Varones (258.7 L/s) y del Hogar de Refugio Temporal (301.9 L/s), en flujo subcrítico, con un llenado máximo de 81.5 % y un borde libre mínimo de 0.087 m.',
        'Los 15 registros de limpieza con tapa ciega en rebaje permiten la inspección y la limpieza del colector en toda su longitud.',
        'La estructura de salida con aleros, emboquillado de piedra y uña de concreto ciclópeo protege la descarga contra la erosión y queda dentro del lindero del predio.',
    ])

    # 12. RECOMENDACIONES -----------------------------------------------------------------
    W.capitulo('RECOMENDACIONES')
    W.viñetas([
        'Verificar con control topográfico la pendiente mínima de 1.0 % en canaletas, 0.5 % en cunetas y 0.302 % en el colector, así como las cotas de fondo de los empalmes, evitando contrapendientes.',
        'Confirmar con el Estudio de Mecánica de Suelos la capacidad portante (≥ 0.80 kg/cm²) y que el nivel freático se encuentra por debajo del fondo de la excavación del colector.',
        'Confirmar el ingreso de camiones por el acceso secundario, condición considerada en el diseño de la sección reforzada del colector.',
        'Comunicar a la entidad a cargo de la Carretera Oasis el caudal de entrega (822.9 L/s) y el punto de descarga, para que evalúe el cruce de las aguas bajo o sobre la vía (badén o alcantarilla), que queda fuera del alcance del proyecto.',
        'No elevar la cota de la berma ni de la calzada de la Carretera Oasis frente a la salida sin evaluar nuevamente el colector, ya que su cresta controla el nivel del agua.',
        'Coordinar con los proyectos CAR Varones y Hogar de Refugio Temporal la ejecución de sus entregas en el registro R-01, respetando la cota de fondo y el caudal indicados.',
        'Efectuar una prueba de escurrimiento con suministro controlado de agua en los puntos altos, verificando que el flujo llegue a los puntos de descarga sin empozamientos, filtraciones ni desbordes.',
        'Ejecutar los trabajos de acuerdo con los planos, las especificaciones técnicas y el metrado del proyecto; cualquier modificación deberá ser evaluada y aprobada antes de su ejecución.',
    ])

    # 13. RELACIÓN DE PLANOS --------------------------------------------------------------
    W.capitulo('RELACIÓN DE PLANOS')
    W.p('Los planos que conforman el proyecto de drenaje pluvial son los siguientes:')
    filas, k = [], 0
    for n, lam in planos:
        filas.append([n, lam, titulo_plano(lam, k)])
        if lam == 'DI-CBCB':
            k += 1
    W.tabla('Relación de planos de drenaje pluvial', ['N.°', 'Lámina', 'Descripción'], filas, [1.2, 3.4, 10.4],
            alin=['c', 'c', 'l'])

    # 14. ANEXOS --------------------------------------------------------------------------
    W.capitulo('ANEXOS')
    W.viñetas([
        'ANEXO 01: Estudio Hidrológico y de Drenaje Pluvial (incluye el capítulo del colector pluvial frontal).',
        'ANEXO 02: Memoria de cálculo del colector pluvial frontal.',
        'ANEXO 03: Especificaciones técnicas de drenaje pluvial.',
        'ANEXO 04: Metrado de drenaje pluvial.',
        'ANEXO 05: Planos de drenaje pluvial.',
    ])

    W.toc = marcas_plantilla + W.toc
    indice(d, W.toc, paginas or {})
    cp = d.core_properties
    cp.author = ''
    cp.last_modified_by = ''
    cp.title = 'Memoria descriptiva de drenaje pluvial - CAR Mujeres'
    cp.comments = ''
    d.save(SALIDA)
    print('guardado', SALIDA, '| tablas', W.ntab, '| figuras', W.nfig)
    return W.toc


def control_pdf():
    import tempfile
    tmp = tempfile.mkdtemp()
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', tmp, SALIDA],
                   capture_output=True, timeout=300)
    return os.path.join(tmp, os.path.basename(SALIDA)[:-5] + '.pdf')


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'figuras':
        figuras(sys.argv[2])
    else:
        toc = generar()
        pags = paginas_pdf(control_pdf(), toc)
        generar(pags)
        print('indice:', pags)
