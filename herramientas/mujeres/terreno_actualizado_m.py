# -*- coding: utf-8 -*-
"""CAR Mujeres (CUI 2717013): actualiza el área y el perímetro del terreno en los Word ya entregados, sin tocar nada más.

Dato nuevo: cuadro de datos técnicos del plano de ubicación (vértices A-I, UTM WGS84 18 S), 13-11-2026:
AREA 10,424.72 m² (1.04247 ha), PERIMETRO 414.69 ml (comprobado con las coordenadas: 10,424.67 m² y 414.69 m).
Antes los documentos decían 6,999.98 m² y 336.89 m. El área libre del cuadro de áreas pasa a 10,424.72 - 3,654.58 = 6,770.14 m².
No se cambia el 0.70 ha del estudio topográfico (es la plantación de plátano, 20 % del predio matriz), ni las áreas de drenaje.

Documentos (se editan en su sitio, en entregables_mujeres/): memoria hidrológica con colector, memoria descriptiva general,
memoria descriptiva (descripción del proyecto) y plan de SST. El cambio es solo de texto dentro de cada párrafo o celda.

Uso: python3 herramientas/mujeres/terreno_actualizado_m.py
"""
import os

import docx
from docx.oxml.ns import qn

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENT = os.path.join(RAIZ, 'entregables_mujeres')
# Por pedido del usuario (13-11) solo hidrología y PSST; las memorias descriptivas quedan como estaban hasta que él lo indique
# (para incluirlas: 'MEMORIA_DESCRIPTIVA_GENERAL_CAR_MUJERES.docx', 'MEMORIA_DESCRIPTIVA_DESCRIPCION_DEL_PROYECTO_CAR_MUJERES.docx').
DOCS = ['MEMORIA_HIDROLOGICA_CAR_MUJERES_CON_COLECTOR.docx', 'PLAN_DE_SST_CAR_MUJERES_2026.docx']
AREA, PERIM, LIBRE = '10,424.72', '414.69', '6,770.14'
CAMBIOS = [   # (texto anterior, texto nuevo) dentro del párrafo
    ('6,999.98m², con un perímetro de 336.89 m', AREA + ' m², con un perímetro de ' + PERIM + ' m'),
    ('6,999.98 m² y 336.89 m de perímetro', AREA + ' m² y ' + PERIM + ' m de perímetro'),
    ('tiene nueve lados, 10,424.72 m² y 414.69 m de perímetro; dentro de él, el lote asignado al Centro de Acogida Residencial '
     'según los planos del expediente es de 10,424.72 m² y 414.69 m de perímetro.',
     'tiene nueve lados, 10,424.72 m² y 414.69 m de perímetro, y corresponde al terreno del Centro de Acogida Residencial '
     'según el plano de ubicación del expediente.'),
    ('lote de 6,999.98 m²', 'lote de ' + AREA + ' m²'),
    ('terreno de 6,999.98 m² del Predio', 'terreno de ' + AREA + ' m² del Predio'),
]
CELDAS = {'6,999.98': AREA, '3,345.40': LIBRE}   # celdas del cuadro de áreas (texto exacto)


def reemplazar(p, viejo, nuevo):
    """Reemplaza en el párrafo aunque el texto esté partido en varios runs; conserva el formato del primer run tocado."""
    ts = list(p.iter(qn('w:t')))
    texto = ''.join(t.text or '' for t in ts)
    i = texto.find(viejo)
    if i < 0:
        return 0
    j = i + len(viejo)
    pos = 0
    primero = None
    for t in ts:
        s = t.text or ''
        a, b = pos, pos + len(s)
        pos = b
        if b <= i or a >= j:
            continue
        ini, fin = max(i, a) - a, min(j, b) - a
        if primero is None:
            t.text = s[:ini] + nuevo + s[fin:]
            primero = t
        else:
            t.text = s[fin:]
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return 1


def actualizar(ruta):
    d = docx.Document(ruta)
    n = 0
    for p in d.element.body.iter(qn('w:p')):
        for viejo, nuevo in CAMBIOS:
            while reemplazar(p, viejo, nuevo):
                n += 1
        texto = ''.join(t.text or '' for t in p.iter(qn('w:t'))).strip()
        if texto in CELDAS:
            n += reemplazar(p, texto, CELDAS[texto])
    d.save(ruta)
    return n


if __name__ == '__main__':
    for f in DOCS:
        print('%-66s %d cambios' % (f, actualizar(os.path.join(ENT, f))))
