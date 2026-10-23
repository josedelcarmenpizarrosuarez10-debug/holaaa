# -*- coding: utf-8 -*-
"""Carátulas de los documentos de drenaje pluvial - Hogar de Refugio Temporal Mujeres Violentadas (CUI 2675514), todas en un
solo Word, una por página.

Mismo motor y diseño que las carátulas del CAR Varones (varones/caratulas_v.py): escudo del logo del Gobierno Regional San Martín,
servicio, proyecto con CUI (nombre tal como el rótulo de las láminas DPL), foto del proyecto entregada por la usuaria
(insumos/solange/FOTO_PROYECTO_HOGAR_REFUGIO.jpg), franja granate con el título y ubicación con la fecha de los rótulos.
Documentos = los de la carpeta de entrega de la usuaria (sin el índice de planos) más la carátula de planos.

Uso: python3 herramientas/caratulas_refugio.py
Salida: entregables/CARATULAS_DRENAJE_PLUVIAL_HOGAR_REFUGIO.docx (imágenes en entregables/figuras_caratula/)
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(AQUI, 'varones'))
import caratulas_v as V  # noqa: E402

V.FOTO = os.path.join(RAIZ, 'insumos/solange/FOTO_PROYECTO_HOGAR_REFUGIO.jpg')
V.FIG = os.path.join(RAIZ, 'entregables/figuras_caratula')
V.ESCUDO = os.path.join(V.FIG, 'escudo_gore_san_martin.png')
V.SALIDA = os.path.join(RAIZ, 'entregables/CARATULAS_DRENAJE_PLUVIAL_HOGAR_REFUGIO.docx')
V.PROYECTO = ('“CREACIÓN DEL SERVICIO DE PROTECCIÓN A MUJERES VÍCTIMAS DE VIOLENCIA EN SITUACIÓN DE RIESGO DE FEMINICIDIO O '
              'PELIGRE SU INTEGRIDAD Y/O SALUD FÍSICA Y/O MENTAL EN HOGAR DE REFUGIO TEMPORAL DISTRITO DE MORALES DE LA '
              'PROVINCIA DE SAN MARTÍN DEL DEPARTAMENTO DE SAN MARTÍN”')
V.CUI = 'CUI N° 2675514'
V.FECHA = 'SETIEMBRE - 2026'                                    # la de los rótulos de las láminas DPL
V.LEYENDA = 'Vista del Hogar de Refugio Temporal'
V.COLOR, V.COLOR_SUB = '1E5E3B', 'D6EEDD'                       # verde (pedido de la usuaria), distinto del granate de Varones
V.TITULO = 'Carátulas - Drenaje pluvial Hogar de Refugio Temporal'
ESP = V.ESP
V.DOCUMENTOS = [   # (título, subtítulo) en el orden de la carpeta de entrega de la usuaria; sin el índice de planos
    ('ESPECIFICACIONES TÉCNICAS', ESP),
    ('MEMORIA DE CÁLCULO', 'DRENAJE PLUVIAL: CANALETAS, MONTANTES Y CUNETAS - ' + ESP),
    ('MEMORIA DE CÁLCULO', 'COLECTOR PLUVIAL FRONTAL - ' + ESP),
    ('MEMORIA DESCRIPTIVA', ESP),
    ('MEMORIA HIDROLÓGICA', 'HIDROLOGÍA Y DRENAJE PLUVIAL CON COLECTOR FRONTAL - ' + ESP),
    ('METRADOS', ESP),
    ('PLANOS', 'LÁMINAS DPL-01 A DPL-42 - ' + ESP),
]

if __name__ == '__main__':
    print(os.path.relpath(V.generar(), RAIZ))
