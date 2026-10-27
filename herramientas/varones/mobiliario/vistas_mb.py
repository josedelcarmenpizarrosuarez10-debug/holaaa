# -*- coding: utf-8 -*-
"""Vistas (PNG) de la planta de equipamiento y mobiliario de cada edificación del CAR Varones, para la memoria descriptiva.

La caja de cada planta es el contorno de sus muros: capas de muros y columnas del modelo y bloques de módulo (MODULOB222,
BLOQUEDORMITORIOS, MODULOCCARSSS, ETBE, ...), asignados a la edificación igual que las etiquetas (lee_plano_mb.edificacion_de);
si una edificación no tiene muros reconocibles se usa el contorno de su mobiliario. Se dibuja con el motor de ezdxf (muros
rellenos, aparatos, mobiliario, directrices y etiquetas de código tal como en la lámina), pero solo con las entidades que tocan
la caja: el dibujo de todo el modelo agota la memoria.

Uso: python3 herramientas/varones/mobiliario/vistas_mb.py [E-01 E-02 ...]   (sin argumentos: todas)
Salida: entregables_varones/figuras_mobiliario/planta_E-nn.png
"""
import os
import sys
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from ezdxf import bbox  # noqa: E402
from ezdxf.addons.drawing import Frontend, RenderContext  # noqa: E402
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration  # noqa: E402
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import lee_plano_mb as LP  # noqa: E402
import datos_mb as D  # noqa: E402

FIG = os.path.join(D.SAL, 'figuras_mobiliario')
CAPAS_MURO = ('MURO', 'A-WALL', 'A-WALL-PATT', 'COLUMNAS', 'Muro Bajo', '0_TABIQUES MELAMINE')
MARGEN = 0.8                                                     # m alrededor de los muros (etiquetas y directrices)
ANCHA = 1.6                                                      # relación ancho/alto desde la que la planta va en hoja apaisada


def _une(c, b):
    return [min(c[0], b.extmin.x), min(c[1], b.extmin.y), max(c[2], b.extmax.x), max(c[3], b.extmax.y)]


def contornos(msp):
    """Contorno de cada entidad del modelo (se calcula una sola vez: es lo más lento)."""
    out = []
    for e in msp:
        if e.dxf.layer == LP.CAPA_CUADROS:
            continue
        try:
            b = bbox.extents([e], fast=True)
        except Exception:
            continue
        if b.has_data and max(b.size.x, b.size.y) < 200:
            out.append((e, b))
    return out


def cajas(EB, pl):
    muros = {}; mob = defaultdict(list)
    for e, b in EB:
        t = e.dxftype()
        if e.dxf.layer == '.' or max(b.size.x, b.size.y) > 60:
            continue
        ed = LP.edificacion_de(b.center.x, b.center.y, pl)
        if ed == '?':
            continue
        if e.dxf.layer in CAPAS_MURO or (t == 'INSERT' and max(b.size.x, b.size.y) > 4 and e.dxf.layer != '0_VANOS'):
            muros[ed] = _une(muros.get(ed, [1e9, 1e9, -1e9, -1e9]), b)
        elif t in ('LINE', 'LWPOLYLINE', 'ARC', 'INSERT', 'HATCH'):
            mob[ed] += [(b.extmin.x, b.extmin.y), (b.extmax.x, b.extmax.y)]
    out = {}
    for ed in set(muros) | set(mob):
        if ed in muros:
            c = muros[ed]
        else:                                                    # sin muros: contorno del mobiliario sin el 1 % extremo
            xs = sorted(q[0] for q in mob[ed]); ys = sorted(q[1] for q in mob[ed]); k = max(1, len(xs) // 100)
            c = [xs[k], ys[k], xs[-1 - k], ys[-1 - k]]
        out[ed] = (c[0] - MARGEN, c[1] - MARGEN, c[2] + MARGEN, c[3] + MARGEN)
    return out


def _sin_blanco(entidad, prop):
    """Lo dibujado en blanco (directrices y etiquetas de la capa 09) se pasa a negro; los demás colores quedan como en la lámina."""
    col = (prop.color or '')[:7].lower()
    if len(col) == 7 and all(int(col[i:i + 2], 16) > 0xE6 for i in (1, 3, 5)):
        prop.color = '#000000' + prop.color[7:]


def dibujar(doc, EB, c, ruta):
    sel = [e for e, b in EB if b.extmin.x < c[2] and b.extmax.x > c[0] and b.extmin.y < c[3] and b.extmax.y > c[1]]
    w, h = c[2] - c[0], c[3] - c[1]; ancho = 18.0
    fig = plt.figure(figsize=(ancho, ancho * h / w)); ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR, min_lineweight=0.2,
                        hatching_timeout=5.0)
    be = MatplotlibBackend(ax)
    fr = Frontend(RenderContext(doc), be, config=cfg)
    fr.push_property_override_function(_sin_blanco)
    fr.draw_entities(sel)
    be.finalize()
    fig.set_size_inches(ancho, ancho * h / w)                    # el motor reajusta la figura: se restituye la proporción de la caja
    ax.set_position([0, 0, 1, 1]); ax.set_aspect('auto'); ax.set_xlim(c[0], c[2]); ax.set_ylim(c[1], c[3]); ax.axis('off')
    fig.savefig(ruta, dpi=170 if w / h > ANCHA else 200, facecolor='white'); plt.close(fig)
    return len(sel)


def generar(solo=None):
    doc = LP.abrir(); msp = doc.modelspace(); P = D.plano()
    os.makedirs(FIG, exist_ok=True)
    EB = contornos(msp); cj = cajas(EB, P['plantas'])
    for ed, c in sorted(cj.items()):
        if solo and ed not in solo:
            continue
        n = dibujar(doc, EB, c, os.path.join(FIG, 'planta_%s.png' % ed))
        print(ed, tuple(round(v, 1) for v in c), n)
    return cj


if __name__ == '__main__':
    generar(sys.argv[1:] or None)
