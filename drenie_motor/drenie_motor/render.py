"""Vista previa PNG de cada lamina del juego de planos (LAMINA_<codigo>.png), en colores sobre fondo blanco.

Se lee el DXF una vez y cada lamina dibuja solo las entidades cuyo recuadro cae en su marco (mucho mas rapido que dibujar
todo el modelo por lamina).
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf import bbox
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration, LineweightPolicy
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


def laminas_png(doc, marcos, salida, dpi=90, ancho_in=23.4):
    msp = doc.modelspace()
    cache = bbox.Cache()
    cajas = []
    for e in msp:
        try:
            ex = bbox.extents([e], fast=True, cache=cache)
        except Exception:
            continue
        if ex.has_data: cajas.append((e, ex.extmin.x, ex.extmin.y, ex.extmax.x, ex.extmax.y))
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR,
                        lineweight_policy=LineweightPolicy.ABSOLUTE, min_lineweight=0.08)
    out = []
    for m in marcos:
        x0, y0, x1, y1 = m["x0"], m["y0"], m["x1"], m["y1"]
        ents = {e.dxf.handle for e, a, b, c, d in cajas if c >= x0 and a <= x1 and d >= y0 and b <= y1}
        ctx = RenderContext(doc); ctx.set_current_layout(msp)
        fig = plt.figure(figsize=(ancho_in, ancho_in * (y1 - y0) / (x1 - x0))); ax = fig.add_axes([0, 0, 1, 1])
        fe = Frontend(ctx, MatplotlibBackend(ax), config=cfg)
        fe.draw_layout(msp, finalize=False, filter_func=lambda e: e.dxf.handle in ents)
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal", adjustable="box"); ax.axis("off")
        ruta = os.path.join(salida, "LAMINA_%s.png" % m["codigo"])
        fig.savefig(ruta, dpi=dpi, facecolor="white"); plt.close(fig)
        out.append(ruta)
    return out
