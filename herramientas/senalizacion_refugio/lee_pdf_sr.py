# -*- coding: utf-8 -*-
"""Ubicación de las señales de ATENCIÓN RIESGO ELÉCTRICO del Hogar de Refugio Temporal (CUI 2675514) a partir del PDF de la lámina
de señalización (SE-S-02).

En el DXF esas señales son imágenes pegadas (OLE) que no guardan su posición; en el PDF impreso de la lámina (A1, escala 1/150) cada
imagen queda en su lugar. Se calibra la hoja con los rótulos "EDIF. 01" a "EDIF. 09" (posición conocida en el DXF; ajuste lineal
por mínimos cuadrados), se pasa el centro de cada imagen de la señal a coordenadas UTM y se asigna a su edificación con el mismo
criterio de lee_plano_sr. También se cuentan, como comprobación independiente del DXF, las palabras de las señales que el PDF
trae como texto (zona segura, aforo, extintor, discapacitados).

Uso: python3 herramientas/senalizacion_refugio/lee_pdf_sr.py
Entrada: insumos/solange/senalizacion/PLANO_DE_SENALIZACION_HOGAR_REFUGIO_TEMPORAL_A1.pdf (no se modifica)
Salida: entregables/_calc/senalizacion_pdf.json
"""
import json
import os
import sys
from collections import Counter

import numpy as np
import pymupdf

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import lee_plano_sr as LP  # noqa: E402

PDF = os.path.join(RAIZ, 'insumos/solange/senalizacion/PLANO_DE_SENALIZACION_HOGAR_REFUGIO_TEMPORAL_A1.pdf')
PLANO = os.path.join(RAIZ, 'entregables/_calc/senalizacion_plano.json')
SALIDA = os.path.join(RAIZ, 'entregables/_calc/senalizacion_pdf.json')
# rótulos de edificación del DXF (punto de inserción, capa 1-TEXTO SIMBOLOS)
EDIF = {'01': (349110.77, 9281950.78), '02': (349138.94, 9281956.10), '03': (349138.99, 9281940.07), '04': (349109.17, 9281989.22),
        '05': (349139.87, 9281989.38), '06': (349131.20, 9282005.11), '07': (349152.99, 9282029.82), '08': (349133.96, 9282029.82),
        '09': (349096.51, 9281989.27)}
TAM_SENAL = (17.25, 25.75)      # pt: 0.90 x 1.36 m a escala 1/150 (tamaño de la imagen de la señal en el DXF)


def leer():
    p = pymupdf.open(PDF)[0]
    w = p.get_text('words')
    A, B = [], []
    for i, x in enumerate(w[:-1]):
        if x[4] == 'EDIF.' and w[i + 1][4] in EDIF:
            A.append([x[0], x[3], 1.0]); B.append(EDIF[w[i + 1][4]])
    A = np.array(A); B = np.array(B)
    cx = np.linalg.lstsq(A, B[:, 0], rcond=None)[0]; cy = np.linalg.lstsq(A, B[:, 1], rcond=None)[0]
    resid = float(np.abs(np.c_[A @ cx - B[:, 0], A @ cy - B[:, 1]]).max())
    # imágenes con el tamaño de la señal en la planta (las de la leyenda son mayores)
    info = p.get_image_info(xrefs=True)
    sen = [i for i in info if abs((i['bbox'][2] - i['bbox'][0]) - TAM_SENAL[0]) < 0.6 and abs((i['bbox'][3] - i['bbox'][1]) - TAM_SENAL[1]) < 0.6]
    eds = json.load(open(PLANO, encoding='utf-8'))['edificaciones']
    pos = []
    for i in sen:
        b = i['bbox']; u, v = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        X = cx[0] * u + cx[1] * v + cx[2]; Y = cy[0] * u + cy[1] * v + cy[2]
        pos.append(dict(x=round(X, 3), y=round(Y, 3), edificacion=LP.edificacion_de(X, Y, eds), imagen=i['xref']))
    palabras = Counter(x[4] for x in w)
    return dict(fuente=os.path.relpath(PDF, RAIZ), calibracion=dict(rotulos=len(A), escala_pt_m=round(1 / cx[0], 3), residuo_max_m=round(resid, 2)),
                riesgo_electrico=pos, riesgo_por_edificacion=dict(sorted(Counter(q['edificacion'] for q in pos).items())),
                imagenes_tipo=sorted({q['imagen'] for q in pos}),
                comprobacion_texto={k: palabras.get(k, 0) for k in ('SISMOS', 'AFORO', 'EXTINTOR', 'PQS', 'DISCAPACITADOS', 'SALIDA')})


if __name__ == '__main__':
    D = leer()
    json.dump(D, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(D['riesgo_electrico']), D['riesgo_por_edificacion'], D['calibracion'], D['comprobacion_texto'])
    print(SALIDA)
