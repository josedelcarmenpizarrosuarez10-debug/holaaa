# -*- coding: utf-8 -*-
"""Lectura del plano de evacuación del Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514), lámina SE-E-01 del índice
de planos de arquitectura. Complementa la lectura del plano de señalización (lee_plano_sr.py): evacuación y señalización son una
sola especialidad.

Fuente: "PLANO DE EVACUACION HOGAR REFUGIO TEMPORAL" de la arquitecta, comprimido en
insumos/solange/senalizacion/PLANO_DE_EVACUACION_HOGAR_REFUGIO_TEMPORAL.zip (no se edita). Misma planta y mismas coordenadas UTM
que el plano de señalización.

Qué se lee del espacio modelo:
  - rutas de evacuación: rótulos "RUTA n / DISTANCIA: L m" (número, longitud y ubicación), el punto de partida de cada ruta
    (bloque "fgd", círculo rojo con X en la puerta) y la edificación de origen (contornos de lee_plano_sr);
  - polilíneas de la capa "RUTA 1" (trazo de las rutas);
  - zonas de evacuación en caso de emergencia: círculos de 4.30 m de diámetro con anillo de 0.15 m (bloques "nmkggs" y "mkbvbs"
    y un par de círculos sueltos), su número (rótulo "ZONA DE EVACUACIÓN EN CASO DE EMERGENCIA nn") y su aforo ("AFORO: n
    PERSONAS", en el bloque o como texto suelto);
  - flechas de llegada a las zonas (bloque "lflvmflvm"), la garita (bloque "OE-01") y el rótulo de la lámina.

Uso: python3 herramientas/senalizacion_refugio/lee_plano_ev.py
Salida: entregables/_calc/evacuacion_plano.json
"""
import json
import math
import os
import re
import sys
import tempfile
import zipfile

import ezdxf
from ezdxf import bbox

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import lee_plano_sr as LP  # noqa: E402  (terreno, contornos de las edificaciones y asignación)

ZIP = os.path.join(RAIZ, 'insumos/solange/senalizacion/PLANO_DE_EVACUACION_HOGAR_REFUGIO_TEMPORAL.zip')
SALIDA = os.path.join(RAIZ, 'entregables/_calc/evacuacion_plano.json')
SENAL = os.path.join(RAIZ, 'entregables/_calc/senalizacion_plano.json')
ZONAS = ('nmkggs', 'mkbvbs')


def abrir():
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(ZIP) as zf:
        nombre = next(n for n in zf.namelist() if n.lower().endswith('.dxf'))
        zf.extract(nombre, tmp)
    return ezdxf.readfile(os.path.join(tmp, nombre))


def texto(e):
    return re.sub(r'[ \t]+', ' ', (e.dxf.text if e.dxftype() == 'TEXT' else e.plain_text())).strip()


def leer():
    doc = abrir(); msp = doc.modelspace()
    eds = json.load(open(SENAL, encoding='utf-8'))['edificaciones']
    tx = [(texto(e), e.dxf.insert.x, e.dxf.insert.y, e.dxf.layer) for e in msp.query('TEXT MTEXT')
          if LP.dentro((e.dxf.insert.x, e.dxf.insert.y), LP.SITIO)]
    # rutas
    rutas = []
    for s, x, y, _ in tx:
        m = re.match(r'RUTA\s*(\d+)\s*DISTANCIA:\s*([\d.]+)\s*m', s.replace('\n', ' '))
        if m:
            rutas.append(dict(n=int(m.group(1)), L=float(m.group(2)), x=round(x, 3), y=round(y, 3)))
    partidas = []
    for e in msp.query('INSERT[name=="fgd"]'):
        b = bbox.extents([e]); partidas.append((round(b.center.x, 3), round(b.center.y, 3)))
    for r in rutas:
        p = min(partidas, key=lambda q: math.hypot(q[0] - r['x'], q[1] - r['y'])) if partidas else None
        r['inicio'] = p; r['d_inicio'] = round(math.hypot(p[0] - r['x'], p[1] - r['y']), 2) if p else None
        r['edificacion'] = LP.edificacion_de(p[0], p[1], eds) if p else None
    # trazo de las rutas
    pl = []
    for e in msp.query('LWPOLYLINE[layer=="RUTA 1"]'):
        pts = list(e.get_points('xy'))
        L = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))
        pl.append(dict(L=round(L, 2), pts=[[round(a, 3), round(b, 3)] for a, b in pts], ini=[round(v, 2) for v in pts[0]], fin=[round(v, 2) for v in pts[-1]],
                       dentro=bool(LP.dentro(pts[0], LP.SITIO)), ancho=round(e.dxf.get('const_width', 0) or 0, 3), color=e.dxf.get('color', 256)))
    # zonas de evacuación
    zonas = []
    for e in msp.query('INSERT'):
        if e.dxf.name in ZONAS:
            b = bbox.extents([e])
            af = [texto(v) for v in e.virtual_entities() if v.dxftype() in ('TEXT', 'MTEXT')]
            rs = sorted({round(v.dxf.radius, 3) for v in e.virtual_entities() if v.dxftype() == 'CIRCLE'})
            zonas.append(dict(bloque=e.dxf.name, x=round(b.center.x, 3), y=round(b.center.y, 3), diametro=round(b.size.x, 3), radios=rs,
                              aforo_txt=af))
    sueltos = [e for e in msp.query('CIRCLE') if LP.dentro((e.dxf.center.x, e.dxf.center.y), LP.SITIO)]
    if sueltos:
        c = sueltos[0].dxf.center
        zonas.append(dict(bloque='CIRCLE', x=round(c.x, 3), y=round(c.y, 3), diametro=round(2 * max(e.dxf.radius for e in sueltos), 3),
                          radios=sorted(round(e.dxf.radius, 3) for e in sueltos), aforo_txt=[]))
    rot = [(s, x, y) for s, x, y, _ in tx if s.upper().startswith('ZONA DE EVACUACI')]
    afo = [(int(re.search(r'(\d+)', s).group(1)), x, y) for s, x, y, _ in tx if s.upper().startswith('AFORO:')]
    for z in zonas:
        n = min(rot, key=lambda t: math.hypot(t[1] - z['x'], t[2] - z['y']))
        z['numero'] = re.search(r'(\d+)\s*$', n[0]).group(1); z['d_rotulo'] = round(math.hypot(n[1] - z['x'], n[2] - z['y']), 2)
        if z['aforo_txt']:
            z['aforo'] = int(re.search(r'(\d+)', z['aforo_txt'][0]).group(1)); z['aforo_fuente'] = 'bloque'
        else:
            a = min(afo, key=lambda t: math.hypot(t[1] - z['x'], t[2] - z['y']))
            z['aforo'] = a[0]; z['aforo_fuente'] = 'texto a %.2f m' % math.hypot(a[1] - z['x'], a[2] - z['y'])
        z['cerca'] = min(eds, key=lambda e: max(e['caja'][0] - z['x'], 0, z['x'] - e['caja'][2]) ** 2 +
                         max(e['caja'][1] - z['y'], 0, z['y'] - e['caja'][3]) ** 2)['codigo']
    zonas.sort(key=lambda z: (int(z['numero']), -z['y']))
    flechas = len([e for e in msp.query('INSERT[name=="lflvmflvm"]')])
    garita = []
    for e in msp.query('INSERT[name=="OE-01"]'):
        garita = [texto(v) for v in e.virtual_entities() if v.dxftype() in ('TEXT', 'MTEXT')]
    rotulo = [texto(e) for e in doc.blocks['WOLSWOSLWOSL'] if e.dxftype() in ('TEXT', 'MTEXT')]
    capas = sorted({e.dxf.layer for e in msp})
    return dict(fuente=os.path.relpath(ZIP, RAIZ), rutas=sorted(rutas, key=lambda r: r['n']), n_inicios=len(partidas),
                polilineas_ruta=pl, zonas=zonas, flechas_llegada=flechas, garita=garita, rotulo=rotulo,
                rotulos_zona=[s for s, _, _ in rot], textos_aforo=[a[0] for a in afo], capas=capas)


if __name__ == '__main__':
    D = leer()
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump(D, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ns = [r['n'] for r in D['rutas']]
    print('rutas', len(ns), 'numeros', min(ns), max(ns), 'faltan', sorted(set(range(1, max(ns) + 1)) - set(ns)),
          'repetidos', sorted({n for n in ns if ns.count(n) > 1}), 'L max', max(r['L'] for r in D['rutas']), 'suma', round(sum(r['L'] for r in D['rutas']), 2))
    print('inicios', D['n_inicios'], 'd_inicio max', max(r['d_inicio'] for r in D['rutas']))
    from collections import Counter
    print('rutas por edificacion', Counter(r['edificacion'] for r in D['rutas']))
    print('polilineas', len(D['polilineas_ruta']), 'dentro', sum(p['dentro'] for p in D['polilineas_ruta']), 'L', round(sum(p['L'] for p in D['polilineas_ruta']), 2),
          Counter(p['ancho'] for p in D['polilineas_ruta']))
    for z in D['zonas']:
        print(z['numero'], z['bloque'], z['x'], z['y'], z['diametro'], z['radios'], z['aforo'], z['aforo_fuente'], z['d_rotulo'], z['cerca'])
    print('flechas', D['flechas_llegada'], 'garita', D['garita'])
    print([t for t in D['rotulo'] if 'LAM' in t.upper() or '-0' in t or 'EVAC' in t.upper()])
    print(SALIDA)
