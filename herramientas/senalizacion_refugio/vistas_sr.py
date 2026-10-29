# -*- coding: utf-8 -*-
"""Vistas previas (PNG) de la planta de señalización del Hogar de Refugio Temporal (CUI 2675514).

Dibujo directo con matplotlib (motor Lienzo de varones/senalizacion/vistas_se.py: líneas, arcos y textos del espacio modelo con
los bloques explotados, rellenos solo en los símbolos), porque el render completo de ezdxf del DXF de 292 MB no termina.
  - planta_general.png: planta general de señalización (todo el terreno);
  - planta_E-0n.png: cada edificación con un margen de 2.5 m, para la memoria;
  - conteo.png: planta general con un círculo de color sobre cada símbolo contado en el metrado (para la nota de observaciones).

Uso: python3 herramientas/senalizacion_refugio/vistas_sr.py   (lee el DXF: 3 a 6 minutos)
Salida: entregables/figuras_senalizacion/
"""
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection, PolyCollection  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI)
for d in (AQUI, os.path.join(HER, 'varones', 'senalizacion')):
    sys.path.insert(0, d)
import lee_plano_sr as LP  # noqa: E402
import datos_sr as D  # noqa: E402
import vistas_se as VS  # noqa: E402

FIG = os.path.join(D.SAL, 'figuras_senalizacion')
GENERAL = (349088.0, 9281915.0, 349164.0, 9282033.0)
MARGEN = 2.5
# color de cada partida en la figura de conteo
COLORES = {'salida': '#00873C', 'SALIDA 2': '#2DB34A', 'A$C3C91529B': '#0B6E4F', 'A$C6B5B2E50': '#5B2C83', 'extintor1': '#D7191C',
           '*U2820': '#1F5FA8', 'sdsadsa': '#1F5FA8', 'sshhhombres': '#1F5FA8', 'sshhmujeres': '#1F5FA8', 'punto.ecologico': '#7A5C00',
           'LE': '#E66101', 'A$C7A2016C2': '#E66101', 'sensorhumo': '#7B3294'}


def guardar_con_marcas(L, ruta, marcas, ancho_pulg=20, dpi=150):
    """Como Lienzo.guardar, con círculos de color sobre los símbolos contados y su leyenda."""
    c = L.caja; w, h = c[2] - c[0], c[3] - c[1]
    fig = plt.figure(figsize=(ancho_pulg, ancho_pulg * h / w)); ax = fig.add_axes([0, 0, 1, 1])
    if L.pol:
        ax.add_collection(PolyCollection(L.pol, facecolors=[(0.75, 0.75, 0.75)] * len(L.pol), edgecolors='none', zorder=1))
    ax.add_collection(LineCollection(L.seg, colors=[(0.55, 0.55, 0.55)] * len(L.seg), linewidths=0.2, zorder=2))
    vistos = {}
    for nombre, pos, color, etiqueta in marcas:
        xs = [p[0] for p in pos]; ys = [p[1] for p in pos]
        s = ax.scatter(xs, ys, s=70, facecolors='none', edgecolors=color, linewidths=1.6, zorder=4)
        vistos.setdefault(etiqueta, s)
    ax.legend(list(vistos.values()), list(vistos.keys()), loc='upper left', fontsize=13, frameon=True, framealpha=0.95)
    ax.set_xlim(c[0], c[2]); ax.set_ylim(c[1], c[3]); ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(ruta, dpi=dpi, facecolor='white'); plt.close(fig)
    return ruta


def generar():
    doc, _ = LP.abrir(); msp = doc.modelspace()
    P = D.plano()
    os.makedirs(FIG, exist_ok=True); out = []
    cajas = [('planta_general', GENERAL, 20)] + [
        ('planta_%s' % e['codigo'], (e['caja'][0] - MARGEN, e['caja'][1] - MARGEN, e['caja'][2] + MARGEN, e['caja'][3] + MARGEN), 12)
        for e in P['edificaciones']]
    for nombre, caja, pulg in cajas:
        L = VS.Lienzo(caja)
        for e in msp:
            L.entidad(e)
        out.append(L.guardar(os.path.join(FIG, nombre + '.png'), ancho_pulg=pulg, dpi=150))
        print(nombre, len(L.seg), len(L.pol), len(L.tx), flush=True)
        if nombre == 'planta_general':
            marcas = []
            for p in D.partidas(P):
                if not p['und'] or not p['bloques'] or p['desc'].startswith('EXTINTOR DE'):
                    continue
                for b in p['bloques']:
                    et = p['desc'].replace(' CON BRAILLE', '').capitalize() + ' (%d)' % p['total']
                    marcas.append((b, P['bloques'][b]['posiciones'], COLORES[b], et))
            out.append(guardar_con_marcas(L, os.path.join(FIG, 'conteo.png'), marcas))
    for lay in doc.layouts:                                        # ventanas de la presentación: qué parte del modelo muestran
        if lay.name == 'Model':
            continue
        for v in lay.query('VIEWPORT'):
            print('VENTANA', lay.name, 'centro', tuple(round(x, 1) for x in v.dxf.view_center_point),
                  'objetivo', tuple(round(x, 1) for x in v.dxf.view_target_point), 'alto', round(v.dxf.view_height, 1),
                  'giro', round(v.dxf.view_twist_angle, 2), 'dir', tuple(round(x, 3) for x in v.dxf.view_direction_vector))
    return out


if __name__ == '__main__':
    for r in generar():
        print(r)
