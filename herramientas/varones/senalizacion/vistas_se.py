# -*- coding: utf-8 -*-
"""Vistas (PNG) de las láminas SE-S-01 (señalización) y SE-E-01 (evacuación) para la memoria descriptiva.

Planta general de cada lámina y una vista ampliada de cada edificación en las dos láminas (cajas de lee_plano_se.py; SE-E-01 es la
misma planta desplazada DY_E en Y). Se dibuja con el motor de ezdxf (muros, rellenos, símbolos, rutas, flechas y textos tal como en
la lámina) pero solo con las entidades que tocan cada caja y sin las curvas de nivel: el dibujo de todo el modelo agota la memoria.
Lo blanco se pasa a negro para el fondo blanco; los demás colores quedan como en la lámina.
La clase Lienzo (dibujo liviano con matplotlib) queda para los símbolos de la leyenda (senales_img.py).

Uso: python3 herramientas/varones/senalizacion/vistas_se.py [SE-S-01 SE-E-01 E-01 ...]   (sin argumentos: todas)
Salida: entregables_varones/figuras_senalizacion/SE-S-01.png, SE-E-01.png, SE-S-01_E-nn.png y SE-E-01_E-nn.png
"""
import math
import os
import sys

import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection, PolyCollection  # noqa: E402
from ezdxf import bbox  # noqa: E402
from ezdxf.colors import aci2rgb  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import lee_plano_se as LP  # noqa: E402
import datos_se as D  # noqa: E402

FIG = os.path.join(D.SAL, 'figuras_senalizacion')
VISTAS = {'SE-S-01': (2846, 1698, 3035, 1829), 'SE-E-01': (2847, 1903, 3036, 2034)}
CAPAS_FUERA = ('CURVAS', 'C-TOPO', 'TOPO')            # curvas de nivel: recargan la vista sin aportar


def color(e, padre_rgb):
    try:
        if e.dxf.hasattr('true_color'):
            return tuple(c / 255 for c in e.rgb)
        aci = e.dxf.color
        if aci in (0, 256):
            if aci == 0 and padre_rgb:
                return padre_rgb
            capa = e.doc.layers.get(e.dxf.layer) if e.doc else None
            aci = capa.color if capa else 7
        if aci in (7, 255):
            return (0, 0, 0)
        r, g, b = aci2rgb(abs(aci))
        if r > 230 and g > 230:                         # amarillo y blanco: se oscurecen para fondo blanco
            return (0.55, 0.50, 0.0)
        return (r / 255, g / 255, b / 255)
    except Exception:
        return (0.3, 0.3, 0.3)


class Lienzo:
    def __init__(self, caja):
        self.caja = caja; self.seg = []; self.col = []; self.pol = []; self.pcol = []; self.tx = []

    def dentro(self, x, y, m=5):
        c = self.caja
        return c[0] - m <= x <= c[2] + m and c[1] - m <= y <= c[3] + m

    def linea(self, pts, rgb):
        pts = [(p[0], p[1]) for p in pts]
        if len(pts) < 2 or not any(self.dentro(*p) for p in pts):
            return
        self.seg.append(pts); self.col.append(rgb)

    def entidad(self, e, rgb_padre=None, simbolo=False, prof=0):
        t = e.dxftype()
        if any(k in e.dxf.layer.upper() for k in CAPAS_FUERA):
            return
        rgb = color(e, rgb_padre)
        try:
            if t == 'LINE':
                self.linea([e.dxf.start, e.dxf.end], rgb)
            elif t in ('LWPOLYLINE', 'POLYLINE'):
                pts = [(v[0], v[1]) for v in e.flattening(0.02)] if hasattr(e, 'flattening') else [(v[0], v[1]) for v in e.points()]
                self.linea(pts, rgb)
            elif t in ('CIRCLE', 'ARC', 'ELLIPSE', 'SPLINE'):
                self.linea([(v.x, v.y) for v in e.flattening(0.02)], rgb)
            elif t == 'HATCH' and simbolo:
                for path in e.paths.rendering_paths(e.dxf.hatch_style):
                    pass
                from ezdxf.render import hatching  # noqa
                from ezdxf import path as P
                for pa in P.from_hatch(e):
                    pts = [(v.x, v.y) for v in pa.flattening(0.02)]
                    if len(pts) > 2 and any(self.dentro(*q) for q in pts):
                        self.pol.append(pts); self.pcol.append(rgb)
            elif t in ('TEXT', 'MTEXT', 'ATTRIB'):
                s = e.dxf.text if t != 'MTEXT' else e.plain_text()
                p = e.dxf.insert
                if self.dentro(p.x, p.y, 0) and s.strip():
                    h = e.dxf.get('height', None) or e.dxf.get('char_height', 0.2) or 0.2
                    rot = e.dxf.get('rotation', 0) or 0
                    self.tx.append((p.x, p.y, s.strip(), h, rot, rgb))
            elif t == 'INSERT' and prof < 5:
                try:
                    b = bbox.extents([e]); 
                    if not b.has_data:
                        return
                    if b.extmax.x < self.caja[0] or b.extmin.x > self.caja[2] or b.extmax.y < self.caja[1] or b.extmin.y > self.caja[3]:
                        return
                    sim = max(b.size.x, b.size.y) < 3
                except Exception:
                    sim = False
                for a in e.attribs:
                    self.entidad(a, rgb, simbolo or sim, prof + 1)
                for v in e.virtual_entities():
                    self.entidad(v, rgb, simbolo or sim, prof + 1)
        except Exception:
            pass

    def guardar(self, ruta, ancho_pulg=20, dpi=150):
        c = self.caja; w, h = c[2] - c[0], c[3] - c[1]
        fig = plt.figure(figsize=(ancho_pulg, ancho_pulg * h / w)); ax = fig.add_axes([0, 0, 1, 1])
        esc = ancho_pulg * 72 / w                       # puntos tipográficos por metro
        if self.pol:
            ax.add_collection(PolyCollection(self.pol, facecolors=self.pcol, edgecolors='none', zorder=1))
        ax.add_collection(LineCollection(self.seg, colors=self.col, linewidths=0.25, zorder=2))
        for x, y, s, hh, rot, rgb in self.tx:
            tam = hh * esc * 1.25
            if tam >= 1.6:
                ax.text(x, y, s, fontsize=tam, rotation=rot, color=rgb, va='bottom', ha='left', zorder=3, family='DejaVu Sans')
        ax.set_xlim(c[0], c[2]); ax.set_ylim(c[1], c[3]); ax.set_aspect('equal'); ax.axis('off')
        fig.savefig(ruta, dpi=dpi, facecolor='white'); plt.close(fig)
        return ruta


MARGEN_ED = 2.5                                         # m alrededor de cada edificación (señalización)
MARGEN_EV = 6.0                                         # m en evacuación: la ruta hasta el exterior


def contornos(msp):
    """Contorno de cada entidad del modelo, sin curvas de nivel (se calcula una sola vez: es lo más lento)."""
    out = []
    for e in msp:
        if any(k in e.dxf.layer.upper() for k in CAPAS_FUERA):
            continue
        try:
            b = bbox.extents([e], fast=True)
        except Exception:
            continue
        if b.has_data and max(b.size.x, b.size.y) < 400:
            out.append((e, b))
    return out


def _sin_blanco(entidad, prop):
    """Blanco a negro y amarillo claro a ocre (textos de nivel), para el fondo blanco."""
    col = (prop.color or '')[:7].lower()
    if len(col) != 7:
        return
    r, g, b = (int(col[i:i + 2], 16) for i in (1, 3, 5))
    if min(r, g, b) > 0xE6:
        prop.color = '#000000' + prop.color[7:]
    elif r > 0xE0 and g > 0xE0 and b < 0x80:
        prop.color = '#8c7a00' + prop.color[7:]


def dibujar(doc, EB, c, ruta, ancho=18.0, dpi=200):
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    sel = [e for e, b in EB if b.extmin.x < c[2] and b.extmax.x > c[0] and b.extmin.y < c[3] and b.extmax.y > c[1]]
    w, h = c[2] - c[0], c[3] - c[1]
    fig = plt.figure(figsize=(ancho, ancho * h / w)); ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR, min_lineweight=0.15,
                        hatching_timeout=5.0)
    be = MatplotlibBackend(ax)
    fr = Frontend(RenderContext(doc), be, config=cfg)
    fr.push_property_override_function(_sin_blanco)
    fr.draw_entities(sel)
    be.finalize()
    fig.set_size_inches(ancho, ancho * h / w)
    ax.set_position([0, 0, 1, 1]); ax.set_aspect('auto'); ax.set_xlim(c[0], c[2]); ax.set_ylim(c[1], c[3]); ax.axis('off')
    fig.savefig(ruta, dpi=dpi, facecolor='white'); plt.close(fig)
    return len(sel)


def cajas():
    """Cajas de las vistas: plantas generales y cada edificación en SE-S-01 y en SE-E-01."""
    P = D.plano(); out = {'SE-S-01': LP.PLANTA_S, 'SE-E-01': LP.PLANTA_E}
    for e in P['edificaciones']:
        x0, y0, x1, y1 = e['caja']; m = MARGEN_ED; n = MARGEN_EV
        out['SE-S-01_' + e['codigo']] = (x0 - m, y0 - m, x1 + m, y1 + m)
        out['SE-E-01_' + e['codigo']] = (x0 - n, y0 - n + LP.DY_E, x1 + n, y1 + n + LP.DY_E)
    return out


def generar(solo=None):
    doc = LP.abrir(); msp = doc.modelspace()
    os.makedirs(FIG, exist_ok=True); EB = contornos(msp); out = []
    for cod, c in cajas().items():
        if solo and not any(cod == s or cod.endswith('_' + s) for s in solo):
            continue
        general = '_' not in cod
        n = dibujar(doc, EB, c, os.path.join(FIG, cod + '.png'), ancho=24.0 if general else 18.0, dpi=250 if general else 200)
        out.append(cod); print(cod, tuple(round(v, 1) for v in c), n)
    return out


if __name__ == '__main__':
    generar(sys.argv[1:] or None)
