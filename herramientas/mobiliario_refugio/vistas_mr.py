# -*- coding: utf-8 -*-
"""Vistas (PNG) de la planta de equipamiento y mobiliario de cada edificación del Hogar de Refugio Temporal (CUI 2675514), para
la memoria descriptiva, tal como en las láminas EM-01 a EM-07 (muros, aparatos, mobiliario y etiquetas de código).

Se dibujan solo las entidades que tocan la caja de cada planta (el dibujo de todo el modelo agota la memoria). Las cajas van en
coordenadas UTM del plano (escala 1/50); EM-02 tiene dos plantas (E-02 arriba, E-03 abajo) y EM-07 dos (E-08 y E-09).

Uso: python3 herramientas/mobiliario_refugio/vistas_mr.py [E-01 E-02 ...]   (sin argumentos: todas)
Salida: entregables/figuras_mobiliario/planta_E-nn.png
"""
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from ezdxf import bbox  # noqa: E402
from ezdxf.addons.drawing import Frontend, RenderContext  # noqa: E402
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration  # noqa: E402
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import lee_plano_mr as LP  # noqa: E402
import datos_mr as D  # noqa: E402

FIG = os.path.join(D.SAL, 'figuras_mobiliario')
CAJAS = {'E-01': (348074.0, 9281760.0, 348096.0, 9281786.0), 'E-02': (348141.0, 9281771.6, 348156.5, 9281786.8),
         'E-03': (348140.5, 9281759.6, 348162.5, 9281770.2), 'E-04': (348191.0, 9281753.0, 348207.0, 9281793.0),
         'E-05': (348227.0, 9281753.0, 348246.0, 9281793.0), 'E-06': (348076.0, 9281711.0, 348101.5, 9281727.0),
         'E-07': (348137.0, 9281688.0, 348152.5, 9281727.0), 'E-08': (348178.0, 9281712.0, 348203.6, 9281729.0),
         'E-09': (348203.4, 9281712.0, 348213.0, 9281729.0)}


def _sin_blanco(entidad, prop):
    """Lo dibujado en blanco (directrices y etiquetas) se pasa a negro; los demás colores quedan como en la lámina."""
    col = (prop.color or '')[:7].lower()
    if len(col) == 7 and all(int(col[i:i + 2], 16) > 0xE6 for i in (1, 3, 5)):
        prop.color = '#000000' + prop.color[7:]


def generar(solo=None):
    doc = LP.abrir(); msp = doc.modelspace()
    os.makedirs(FIG, exist_ok=True)
    EB = []
    for e in msp:
        if e.dxf.layer == LP.CAPAS_CUADRO[0]:
            continue
        try:
            b = bbox.extents([e], fast=True)
        except Exception:
            continue
        if b.has_data and max(b.size.x, b.size.y) < 100:
            EB.append((e, b))
    for ed, c in CAJAS.items():
        if solo and ed not in solo:
            continue
        es = [e for e, b in EB if b.extmin.x < c[2] and b.extmax.x > c[0] and b.extmin.y < c[3] and b.extmax.y > c[1]]
        w, h = c[2] - c[0], c[3] - c[1]; ancho = 18.0
        fig = plt.figure(figsize=(ancho, ancho * h / w)); ax = fig.add_axes([0, 0, 1, 1])
        cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR, min_lineweight=0.15,
                            hatching_timeout=3.0)
        be = MatplotlibBackend(ax); fr = Frontend(RenderContext(doc), be, config=cfg); fr.push_property_override_function(_sin_blanco)
        fr.draw_entities(es); be.finalize()
        fig.set_size_inches(ancho, ancho * h / w); ax.set_position([0, 0, 1, 1]); ax.set_aspect('auto')
        ax.set_xlim(c[0], c[2]); ax.set_ylim(c[1], c[3]); ax.axis('off')
        fig.savefig(os.path.join(FIG, 'planta_%s.png' % ed), dpi=150, facecolor='white'); plt.close(fig)
        print(ed, len(es), flush=True)


if __name__ == '__main__':
    generar(sys.argv[1:] or None)
