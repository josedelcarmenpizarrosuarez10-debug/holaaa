# -*- coding: utf-8 -*-
"""Carátulas de los documentos de drenaje pluvial - CAR Mujeres (CUI 2717013), todas en un solo Word.

Usa la carátula de los documentos del proyecto (insumos/wilma/MEMORIA_IISS_CAR_MUJERES.docx, solo lectura):
encabezado con logo y nombre del proyecto, recuadro con el título del documento, la línea del servicio
("SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL EXPEDIENTE TÉCNICO DE PI:"), el nombre del
proyecto y la fecha; la misma carátula de la memoria descriptiva (memoria_descriptiva_m.py).
Una página por documento, en el orden de la carpeta de entrega del usuario.

Uso: python3 herramientas/mujeres/caratulas_m.py
Salida: entregables_mujeres/CARATULAS_DRENAJE_PLUVIAL_CAR_MUJERES.docx
"""
import copy
import os

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANTILLA = os.path.join(RAIZ, 'insumos/wilma/MEMORIA_IISS_CAR_MUJERES.docx')
SALIDA = os.path.join(RAIZ, 'entregables_mujeres/CARATULAS_DRENAJE_PLUVIAL_CAR_MUJERES.docx')
SERVICIO = 'SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL EXPEDIENTE TÉCNICO DE PI:'

# (línea 1, línea 2, línea 3 subrayada) del recuadro de cada carátula
DOCUMENTOS = [
    ('METRADOS', ' DE LA ESPECIALIDAD DE ', 'DRENAJE PLUVIAL'),
    ('MEMORIA HIDROLÓGICA', ' DE LA ESPECIALIDAD DE ', 'DRENAJE PLUVIAL'),
    ('MEMORIA DESCRIPTIVA ', ' DE LA ESPECIALIDAD DE ', 'DRENAJE PLUVIAL'),
    ('MEMORIA DE CÁLCULO', 'DE LA ESPECIALIDAD DE DRENAJE PLUVIAL', 'COLECTOR PLUVIAL FRONTAL'),
    ('MEMORIA DE CÁLCULO', 'DE LA ESPECIALIDAD DE DRENAJE PLUVIAL', 'DRENAJE PLUVIAL INTERNO'),
    ('ESPECIFICACIONES TÉCNICAS', ' DE LA ESPECIALIDAD DE ', 'DRENAJE PLUVIAL'),
]
N_CARATULA = 34          # párrafos 0 a 33 de la plantilla: la carátula (el 33 es la fecha)
P_SERVICIO = 19


def _poner(p, texto):
    """Deja el texto en el primer run del párrafo (conserva su formato) y borra los demás runs."""
    runs = p.findall(qn('w:r'))
    runs[0].find(qn('w:t')).text = texto
    runs[0].find(qn('w:t')).set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    for r in runs[1:]:
        p.remove(r)


def generar():
    d = docx.Document(PLANTILLA)
    body = d.element.body
    elems = list(body)
    caratula = elems[:N_CARATULA]
    sect = copy.deepcopy(next(e for e in elems if e.find('.//' + qn('w:sectPr')) is not None).find('.//' + qn('w:sectPr')))
    for el in elems:
        body.remove(el)
    nid = 1000
    for k, lineas in enumerate(DOCUMENTOS):
        for i, el in enumerate(caratula):
            c = copy.deepcopy(el)
            for bm in c.findall('.//' + qn('w:bookmarkStart')) + c.findall('.//' + qn('w:bookmarkEnd')):
                bm.getparent().remove(bm)
            for tb in c.iter(qn('w:txbxContent')):                 # recuadro del título (DrawingML y VML)
                for p, t in zip(tb.findall(qn('w:p')), lineas):
                    _poner(p, t)
            for dp in c.iter('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr'):
                nid += 1; dp.set('id', str(nid))
            if i == P_SERVICIO:
                _poner(c, SERVICIO)
            if i == 0 and k > 0:                                     # cada carátula en su página
                pPr = c.find(qn('w:pPr'))
                if pPr is None:
                    pPr = OxmlElement('w:pPr'); c.insert(0, pPr)
                pos = sum(1 for ch in pPr if ch.tag in (qn('w:pStyle'), qn('w:keepNext'), qn('w:keepLines')))
                pPr.insert(pos, OxmlElement('w:pageBreakBefore'))
            body.append(c)
    body.append(sect)
    for s in d.sections:
        for h in (s.header, s.first_page_header):
            for t in h._element.iter(qn('w:t')):
                if t.text == 'INSTALACIONES SANITARAS SANITARIAS':
                    t.text = 'DRENAJE PLUVIAL'
    d.core_properties.author = ''
    d.core_properties.title = 'Carátulas - Drenaje pluvial CAR Mujeres'
    d.save(SALIDA)
    return SALIDA


if __name__ == '__main__':
    print(generar())
