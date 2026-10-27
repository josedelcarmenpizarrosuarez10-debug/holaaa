# -*- coding: utf-8 -*-
"""Vistas previas (PNG) de las plantas de las láminas SE-S-01 y SE-E-01 para la memoria descriptiva.

El plano de la arquitecta es pesado (sombreados de pisos, curvas de nivel, mobiliario): el render completo de ezdxf supera la
memoria disponible. Aquí se dibuja directo con matplotlib: líneas, polilíneas, arcos y círculos de todo el espacio modelo de la
zona (bloques explotados), rellenos sólidos solo en los símbolos (bloques < 3 m) y textos; colores del plano sobre fondo blanco.
Las cajas son las de lee_plano_se.py (planta y leyenda de cada lámina).

Uso: python3 herramientas/varones/senalizacion/vistas_se.py
Salida: entregables_varones/figuras_senalizacion/SE-S-01.png y SE-E-01.png
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


def generar():
    doc = LP.abrir(); msp = doc.modelspace()
    os.makedirs(FIG, exist_ok=True); out = []
    for cod, caja in VISTAS.items():
        L = Lienzo(caja)
        for e in msp:
            L.entidad(e)
        out.append(L.guardar(os.path.join(FIG, cod + '.png')))
        print(cod, len(L.seg), len(L.pol), len(L.tx))
    return out


if __name__ == '__main__':
    print(generar())
