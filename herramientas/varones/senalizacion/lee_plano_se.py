# -*- coding: utf-8 -*-
"""Lectura del plano final de evacuación y señalización del CAR Varones (CUI 2705619).

Fuente: plano EVACUACION Y SEGURIDAD OK de la arquitecta (láminas SE-S-01 señalización y SE-E-01 evacuación), guardado
comprimido en insumos/katiuska/senalizacion/EVACUACION_Y_SEGURIDAD_OK_CAR_VARONES.zip (no se edita).

Qué se lee (todo del espacio modelo, a escala real):
  - la leyenda de SE-S-01: símbolo (bloque), descripción, altura de instalación y cantidad, fila por fila;
  - cada símbolo de señal dibujado en la planta de SE-S-01 (los bloques tienen la geometría desplazada del punto de
    inserción: la posición es el centro de su contorno) y la edificación donde cae;
  - de SE-E-01: rutas de evacuación (número, ambiente, longitud), zonas seguras pintadas S1 a S13 (círculos) y aforos.
Las señales de la leyenda que en el DXF son imágenes pegadas (OLE: avisador sonoro, atención riesgo eléctrico, riesgo de
descarga eléctrica y prohibido el ingreso) no exportan su ubicación; para ellas vale la cantidad de la leyenda.

Uso: python3 herramientas/varones/senalizacion/lee_plano_se.py
Salida: entregables_varones/_calc/senalizacion_plano.json
"""
import json
import os
import re
import sys
import tempfile
import zipfile
from collections import Counter

import ezdxf
from ezdxf import bbox

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(AQUI)))
ZIP = os.path.join(RAIZ, 'insumos/katiuska/senalizacion/EVACUACION_Y_SEGURIDAD_OK_CAR_VARONES.zip')
SALIDA = os.path.join(RAIZ, 'entregables_varones/_calc/senalizacion_plano.json')

# zonas del espacio modelo (m): planta de SE-S-01, su leyenda, planta de SE-E-01 y su leyenda
PLANTA_S = (2847, 1699, 2994, 1828)
LEYENDA_S = (3020, 1736, 3034, 1789.5)
PLANTA_E = (2848, 1904, 2991, 2033)
LEYENDA_E = (3005, 1930, 3060, 2000)
DY_E = 1949.38 - 1743.49          # SE-E-01 es la misma planta desplazada en Y (rótulo O.EXTERIOR 01 en ambas)

# edificaciones: bloque de la planta general y rótulo del plano (EDIFICACION 01 a 10)
EDIFICACIONES = [
    ('E-01', 'DMINISTRACNOE', 'Administración'),
    ('E-02', 'VESTIDORES', 'Vestidores de la losa deportiva'),
    ('E-03', 'MODULO MADRES', 'Módulo de madres sustitutas'),
    ('E-04', 'MODUL 12 17 AÑIS 2', 'Módulo de 12 a 17 años (1)'),
    ('E-05', 'MODULO 12 - 17 AÑOS', 'Módulo de 12 a 17 años (2)'),
    ('E-06', 'MODILI 3 - 5 AÑOS', 'Módulo de 3 a 5 años'),
    ('E-07', 'DULO 6 - 11 AÑOS', 'Módulo de 6 a 11 años'),
    ('E-08', 'SUM', 'SUM y cocina'),
    ('E-09', 'BAÑOS PUCLOSOS4', 'SS.HH. público'),
    ('E-10', 'SERVOCNOWINCW', 'Servicios generales'),
]
EXTERIOR = ('EXT', 'Obras exteriores y complementarias (patios, ingresos, losa deportiva y circulaciones)')
# bloque de la planta que no es el de la leyenda (la señal de SS.HH. PHD de la planta es otro bloque)
ALIAS_PLANTA = {'15': ['15', 'sdsadsa']}


def dentro(c, z):
    return z[0] <= c[0] <= z[2] and z[1] <= c[1] <= z[3]


def abrir():
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(ZIP) as zf:
        nombre = next(n for n in zf.namelist() if n.lower().endswith('.dxf'))
        zf.extract(nombre, tmp)
    return ezdxf.readfile(os.path.join(tmp, nombre))


def textos(msp, z, prof_max=0):
    out = []

    def ver(e, prof):
        t = e.dxftype()
        if t in ('TEXT', 'MTEXT'):
            s = e.dxf.text if t == 'TEXT' else e.plain_text()
            s = re.sub(r'[ \t]+', ' ', s).strip()
            p = e.dxf.insert
            if dentro((p.x, p.y), z):
                out.append(dict(texto=s, x=round(p.x, 3), y=round(p.y, 3), capa=e.dxf.layer))
        elif t == 'INSERT' and prof < prof_max:
            try:
                for v in e.virtual_entities():
                    ver(v, prof + 1)
            except Exception:
                pass
    for e in msp:
        ver(e, 0)
    return out


def simbolos(msp, cache):
    """Bloques de tamaño de señal (< 6 m) con su centro, en el primer nivel del espacio modelo."""
    out = []
    for e in msp.query('INSERT'):
        try:
            b = bbox.extents([e], cache=cache)
        except Exception:
            continue
        if not b.has_data or max(b.size.x, b.size.y) >= 6:
            continue
        out.append(dict(bloque=e.dxf.name, x=round(b.center.x, 3), y=round(b.center.y, 3)))
    return out


def edificios(msp, cache):
    out = []
    for cod, blk, nombre in EDIFICACIONES:
        e = next(e for e in msp.query('INSERT') if e.dxf.name == blk and dentro(bbox.extents([e], cache=cache).center, PLANTA_S))
        b = bbox.extents([e], cache=cache)
        out.append(dict(codigo=cod, nombre=nombre, bloque=blk, caja=[round(v, 3) for v in (b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y)]))
    return out


def edificacion_de(x, y, eds, margen=0.60):
    """Edificación cuyo contorno (con un margen para las señales de fachada) contiene el punto; la de menor área si hay varias."""
    cand = [e for e in eds if e['caja'][0] - margen <= x <= e['caja'][2] + margen and e['caja'][1] - margen <= y <= e['caja'][3] + margen]
    if not cand:
        return EXTERIOR[0]
    return min(cand, key=lambda e: (e['caja'][2] - e['caja'][0]) * (e['caja'][3] - e['caja'][1]))['codigo']


def leyenda_s(msp, syms):
    """Filas de la leyenda de SE-S-01: cada fila tiene descripción, altura y cantidad en su misma altura Y."""
    tx = [t for t in textos(msp, (3020, 1736, 3034, 1786.0)) if t['capa'] == '2']
    desc = [t for t in tx if 3024 <= t['x'] <= 3027.5 and t['texto'] != 'DESCRIPCIÓN']
    filas = []
    for d in sorted(desc, key=lambda t: -t['y']):
        alt = [t for t in tx if 3029 <= t['x'] <= 3030.5 and abs(t['y'] - d['y']) < 0.6]          # sin altura: punto ecológico
        can = min((t for t in tx if 3031.5 <= t['x'] <= 3032.5), key=lambda t: abs(t['y'] - d['y']))
        blk = [s for s in syms if dentro((s['x'], s['y']), (3021.5, d['y'] - 0.8, 3024.6, d['y'] + 0.8))]
        filas.append(dict(descripcion=re.sub(r'\s+', ' ', d['texto'].replace('\n', ' ')).strip(), altura=(alt[0]['texto'] if alt else None),
                          cantidad=int(can['texto']), bloque=(min(blk, key=lambda s: abs(s['y'] - d['y']))['bloque'] if blk else None)))
    return filas


def evacuacion(msp):
    tx = textos(msp, PLANTA_E)
    rutas = {}
    for t in tx:
        m = re.match(r'RUTA\s*(\d+)\s*-?\s*([\d.]+)\s*ml', t['texto'])
        if m:
            rutas.setdefault(int(m.group(1)), []).append(dict(L=float(m.group(2)), x=t['x'], y=round(t['y'] - DY_E, 3)))
    zonas = sorted((dict(nombre=t['texto'], x=t['x'], y=round(t['y'] - DY_E, 3)) for t in tx if re.match(r'^S\d+$', t['texto'])),
                   key=lambda z: int(z['nombre'][1:]))
    circ = [e for e in msp.query('CIRCLE') if abs(e.dxf.radius - 1.50) < 0.01 and dentro((e.dxf.center.x, e.dxf.center.y), PLANTA_E)]
    aforos = [dict(personas=int(re.search(r'(\d+)', t['texto']).group(1)), x=t['x'], y=round(t['y'] - DY_E, 3))
              for t in tx if t['texto'].startswith('AFORO:')]
    ley = textos(msp, LEYENDA_E)
    nombres = {}
    for t in ley:
        m = re.match(r'Ruta de Evacuacion (\d+)', t['texto'])
        if m:
            amb = min((u for u in ley if u['capa'] == t['capa'] and u['y'] < t['y'] and abs(u['x'] - t['x']) < 0.3 and not u['texto'].startswith('Ruta')),
                      key=lambda u: t['y'] - u['y'])
            nombres[int(m.group(1))] = amb['texto'].rstrip('.')
    zs = next(t['texto'] for t in ley if t['texto'].startswith('Radio de'))
    return dict(rutas=rutas, rutas_leyenda=nombres, zonas_seguras=zonas, circulos_zona_segura=len(circ),
                radio_zona_segura=1.50, leyenda_zona_segura=re.sub(r'\s+', ' ', zs), aforos=aforos)


def rotulos(doc):
    out = {}
    for lay in doc.layouts:
        if lay.name == 'Model':
            continue
        tx = {re.sub(r'\s+', ' ', (e.dxf.text if e.dxftype() == 'TEXT' else e.plain_text())).strip() for e in lay.query('TEXT MTEXT')}
        cod = next((t for t in tx if re.match(r'^SE-[SE]-\d\d$', t)), None)
        if cod:
            out[cod] = dict(presentacion=lay.name, plano=next(t for t in tx if t.startswith('PLANO DE')),
                            escala=next(t for t in tx if re.match(r'^1/\d+$', t)), fecha=next(t for t in tx if re.search(r'20\d\d$', t)))
    return out


def ole():
    """Imágenes pegadas (OLE2FRAME) del espacio modelo: el DXF no trae su posición."""
    n = 0
    with zipfile.ZipFile(ZIP) as zf:
        nombre = next(x for x in zf.namelist() if x.lower().endswith('.dxf'))
        lineas = zf.read(nombre).decode('utf-8', 'replace').splitlines()
    for i in range(len(lineas) - 6):
        if lineas[i].strip() == '0' and lineas[i + 1].strip() == 'OLE2FRAME':
            j = i + 2; propietario = None; papel = False
            while lineas[j].strip() != '0':
                if lineas[j].strip() == '330': propietario = lineas[j + 1].strip()
                if lineas[j].strip() == '67': papel = True
                j += 2
            n += (propietario == '1F' and not papel)
    return n


def ambientes(msp, cache, eds):
    """Nombres de ambiente (capa 0_TEXTOS 2 de los bloques de la planta general) por edificación y en exteriores."""
    tx = []

    def ver(e, prof):
        t = e.dxftype()
        if t in ('TEXT', 'MTEXT'):
            s = re.sub(r'\s+', ' ', e.dxf.text if t == 'TEXT' else e.plain_text()).strip(); p = e.dxf.insert
            if e.dxf.layer == '0_TEXTOS 2' and dentro((p.x, p.y), PLANTA_S) and re.search('[A-ZÁÉÍÓÚ]{2}', s):
                tx.append((s, p.x, p.y))
        elif t == 'INSERT' and prof < 4:
            try:
                b = bbox.extents([e], cache=cache)
                if not b.has_data or not (b.extmax.x > PLANTA_S[0] and b.extmin.x < PLANTA_S[2] and b.extmax.y > PLANTA_S[1] and b.extmin.y < PLANTA_S[3]):
                    return
                for v in e.virtual_entities():
                    ver(v, prof + 1)
            except Exception:
                pass
    for e in msp:
        ver(e, 0)
    out = {}
    for s, x, y in tx:
        cod = edificacion_de(x, y, eds, margen=0.0)
        out.setdefault(cod, Counter())[s] += 1
    return {k: dict(v) for k, v in out.items()}


def leer():
    doc = abrir(); msp = doc.modelspace(); cache = bbox.Cache()
    syms = simbolos(msp, cache)
    eds = edificios(msp, cache)
    ley = leyenda_s(msp, syms)
    planta = [s for s in syms if dentro((s['x'], s['y']), PLANTA_S)]
    for f in ley:
        nombres = ALIAS_PLANTA.get(f['bloque'], [f['bloque']]) if f['bloque'] else []
        pos = [s for s in planta if s['bloque'] in nombres]
        f['planta'] = len(pos) if f['bloque'] else None
        f['por_edificacion'] = dict(Counter(edificacion_de(s['x'], s['y'], eds) for s in pos)) if f['bloque'] else None
        f['posiciones'] = [[s['x'], s['y']] for s in pos]
    ev = evacuacion(msp)
    for a in ev['aforos']:
        a['edificacion'] = edificacion_de(a['x'], a['y'], eds, margen=0.0)
    amb = ambientes(msp, cache, eds)
    rot = {t['texto']: [t['x'], t['y']] for t in textos(msp, PLANTA_S) if re.match(r'^(EDIFICACION \d\d|O\.(EXTERIOR|COMPLEMENTARIA) \d\d)$', t['texto'])}
    return dict(fuente=os.path.relpath(ZIP, RAIZ), laminas=rotulos(doc), edificaciones=eds, exterior=dict(codigo=EXTERIOR[0], nombre=EXTERIOR[1]),
                rotulos_planta=rot, ambientes=amb, leyenda=ley, evacuacion=ev, ole_espacio_modelo=ole())


if __name__ == '__main__':
    D = leer()
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump(D, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for f in D['leyenda']:
        print('%-62s %5s ley %3d planta %4s  %s' % (f['descripcion'][:62], f['altura'], f['cantidad'], f['planta'], f['por_edificacion']))
    print('rutas', {k: [r['L'] for r in v] for k, v in sorted(D['evacuacion']['rutas'].items())})
    print('zonas seguras', len(D['evacuacion']['zonas_seguras']), 'circulos', D['evacuacion']['circulos_zona_segura'], 'OLE', D['ole_espacio_modelo'])
    print('aforos', [(a['personas'], a['edificacion']) for a in D['evacuacion']['aforos']])
    print(D['laminas'])
    print(SALIDA)
