# -*- coding: utf-8 -*-
"""Vistas (PNG) de la planta de equipamiento y mobiliario de cada edificación del CAR Varones, para la memoria descriptiva.

La caja de cada planta es el contorno de su dibujo (líneas, arcos, bloques y sombreados, sin los cuadros), asignado a
la edificación igual que las etiquetas (lee_plano_mb.edificacion_de). Dibujo con el renderizador liviano de la señalización
(senalizacion/vistas_se.Lienzo): el render completo de ezdxf no hace falta para estas vistas.

Uso: python3 herramientas/varones/mobiliario/vistas_mb.py
Salida: entregables_varones/figuras_mobiliario/planta_E-nn.png
"""
import os
import sys
from collections import defaultdict

from ezdxf import bbox

AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'senalizacion'))
import lee_plano_mb as LP  # noqa: E402
import vistas_se as VS  # noqa: E402
import datos_mb as D  # noqa: E402

FIG = os.path.join(D.SAL, 'figuras_mobiliario')
# plantas pegadas a los cuadros de otra lámina: caja medida en el dibujo
CAJAS_FIJAS = {'E-03': (2571.0, 734.3, 2579.6, 748.6), 'E-10': (2583.8, 754.4, 2591.2, 768.6)}


def cajas(msp, pl):
    pts = defaultdict(list)
    for e in msp:
        if e.dxf.layer in (LP.CAPA_CUADROS, '.') or e.dxftype() not in ('LINE', 'LWPOLYLINE', 'ARC', 'INSERT', 'HATCH'):
            continue
        try:
            b = bbox.extents([e])
        except Exception:
            continue
        if not b.has_data or max(b.size.x, b.size.y) > 40:
            continue
        ed = LP.edificacion_de(b.center.x, b.center.y, pl)
        if ed != '?':
            pts[ed] += [(b.extmin.x, b.extmin.y), (b.extmax.x, b.extmax.y)]
    out = {}
    for ed, p in pts.items():
        xs = sorted(q[0] for q in p); ys = sorted(q[1] for q in p)
        k = max(1, len(xs) // 100); m = 0.5                         # descarta el 1 % extremo (directrices, ejes sueltos)
        out[ed] = (xs[k] - m, ys[k] - m, xs[-1 - k] + m, ys[-1 - k] + m)
    return out


def generar():
    doc = LP.abrir(); msp = doc.modelspace(); P = D.plano()
    os.makedirs(FIG, exist_ok=True)
    cj = cajas(msp, P['plantas']); cj.update(CAJAS_FIJAS)
    ents = list(msp)
    for ed, c in sorted(cj.items()):
        L = VS.Lienzo(c)
        for e in ents:
            L.entidad(e)
        w = c[2] - c[0]
        L.guardar(os.path.join(FIG, 'planta_%s.png' % ed), ancho_pulg=16 if w > 15 else 9, dpi=160)
        print(ed, tuple(round(v, 1) for v in c))
    return cj


if __name__ == '__main__':
    generar()
