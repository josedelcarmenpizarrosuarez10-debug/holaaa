# -*- coding: utf-8 -*-
"""Lectura del plano de señalización del Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514).

Fuente: "PLANO DE SEÑALIZACION HOGAR REFUGIO TEMPORAL" de la arquitecta, guardado comprimido en
insumos/solange/senalizacion/PLANO_DE_SENALIZACION_HOGAR_REFUGIO_TEMPORAL.zip (no se edita). El DXF pesa 292 MB: la lectura
tarda 1 a 2 minutos.

Qué se lee (todo del espacio modelo, a escala real, coordenadas UTM):
  - la leyenda (bloque "assas"): símbolo, descripción, altura de instalación y cantidad de cada fila;
  - cada símbolo de señal dibujado en la planta (posición = centro de su contorno) y la edificación donde cae (contorno del
    bloque de la planta general de cada edificación, con 0.60 m de margen para las señales de fachada);
  - los símbolos de señal que están fuera del terreno (copias sueltas que no se metran);
  - las imágenes pegadas (OLE2FRAME): el DXF solo trae su tamaño, no su posición ni su contenido;
  - el rótulo de la lámina (bloque "WOLSWOSLWOSL") y las presentaciones;
  - los textos de ambientes de cada bloque de edificación y los círculos que podrían ser zonas de reunión.

Uso: python3 herramientas/senalizacion_refugio/lee_plano_sr.py
Salida: entregables/_calc/senalizacion_plano.json
"""
import json
import math
import os
import re
import tempfile
import zipfile
from collections import Counter

import ezdxf
from ezdxf import bbox

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
ZIP = os.path.join(RAIZ, 'insumos/solange/senalizacion/PLANO_DE_SENALIZACION_HOGAR_REFUGIO_TEMPORAL.zip')
SALIDA = os.path.join(RAIZ, 'entregables/_calc/senalizacion_plano.json')

SITIO = (349085, 9281910, 349170, 9282040)        # terreno del Hogar de Refugio (UTM WGS 84, 18 S)
LEYENDA = 'assas'
ROTULO = 'WOLSWOSLWOSL'
# edificación -> bloque de la planta general (rótulos EDIF. 01 a EDIF. 09 del plano)
EDIFICACIONES = [('E-01', 'ADMIII PLATA GG'), ('E-02', 'edf 2 pg bloque'), ('E-03', 'bloque 03 pg'), ('E-04', 'bloque pg edf 04'),
                 ('E-05', 'bloque sum pg'), ('E-06', 'EDF 06 PG BLOQUE'), ('E-07', 'BLOQUE EDF 07 PG'), ('E-08', 'BLOQUE EDF 08 PG'),
                 ('E-09', 'VEREDAA PG EDF 09')]
EXTERIOR = 'EXT'
# bloques de señal de la planta (los de la leyenda tienen otro nombre en varios casos)
SENALES = ['salida', 'A$C3C91529B', '*U2820', 'sdsadsa', 'sshhhombres', 'sshhmujeres', 'extintor1', 'sensorhumo', 'LE',
           'A$C7A2016C2', 'A$C6B5B2E50', 'SALIDA 2', 'punto.ecologico']


def dentro(c, z, m=0.0):
    return z[0] - m <= c[0] <= z[2] + m and z[1] - m <= c[1] <= z[3] + m


def abrir():
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(ZIP) as zf:
        nombre = next(n for n in zf.namelist() if n.lower().endswith('.dxf'))
        zf.extract(nombre, tmp)
    return ezdxf.readfile(os.path.join(tmp, nombre)), os.path.join(tmp, nombre)


def limpio(s):
    return re.sub(r'\s+', ' ', s.replace('\n', ' ')).strip()


def texto(e):
    return limpio(e.dxf.text if e.dxftype() in ('TEXT', 'ATTRIB', 'ATTDEF') else e.plain_text())


def leyenda(doc, cache):
    """Filas de la leyenda: descripción, altura y cantidad en la misma altura Y; símbolo = bloque a la izquierda en esa Y."""
    blk = doc.blocks[LEYENDA]
    tx = [(texto(e), e.dxf.insert.x, e.dxf.insert.y) for e in blk if e.dxftype() in ('TEXT', 'MTEXT')]
    sims = []
    for e in blk.query('INSERT'):
        b = bbox.extents([e], cache=cache)
        if b.has_data:
            sims.append((e.dxf.name, b.center.y))
    n_ole = len(blk.query('OLE2FRAME'))
    desc = [t for t in tx if -9.0 <= t[1] <= -7.3 and t[2] < 51.5]
    filas = []
    for d, x, y in sorted(desc, key=lambda t: -t[2]):
        alt = [t for t in tx if -3.7 <= t[1] <= -3.0 and abs(t[2] - y) < 0.6]
        can = [t for t in tx if -1.5 <= t[1] <= -1.0 and abs(t[2] - y) < 0.6]
        s = [n for n, yy in sims if abs(yy - y) < 0.9]
        filas.append(dict(descripcion=d, altura=(alt[0][0] if alt else None), cantidad=(int(can[0][0]) if can else None),
                          bloque=(s[0] if s else None), y=round(y, 3)))
    return filas, n_ole


def anidados(doc, nombres):
    out = {}
    for n in nombres:
        b = doc.blocks.get(n)
        if b is not None:
            out[n] = dict(Counter(e.dxftype() for e in b)), [e.dxf.name for e in b.query('INSERT')]
    return out


def planta(msp, cache):
    """Inserciones de tamaño de señal (< 6 m): dentro del terreno y fuera de él."""
    dentro_s, fuera = [], []
    for e in msp.query('INSERT'):
        try:
            b = bbox.extents([e], cache=cache)
        except Exception:
            continue
        if not b.has_data or max(b.size.x, b.size.y) >= 6:
            continue
        r = dict(bloque=e.dxf.name, capa=e.dxf.layer, x=round(b.center.x, 3), y=round(b.center.y, 3),
                 w=round(b.size.x, 3), h=round(b.size.y, 3), handle=e.dxf.handle)
        (dentro_s if dentro((r['x'], r['y']), SITIO) else fuera).append(r)
    return dentro_s, fuera


def edificios(msp, cache):
    out = []
    for cod, blk in EDIFICACIONES:
        e = next(e for e in msp.query('INSERT') if e.dxf.name == blk)
        b = bbox.extents([e], cache=cache)
        out.append(dict(codigo=cod, bloque=blk, caja=[round(v, 3) for v in (b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y)]))
    return out


def edificacion_de(x, y, eds, margen=0.60):
    cand = [e for e in eds if dentro((x, y), e['caja'], margen)]
    if not cand:
        return EXTERIOR
    return min(cand, key=lambda e: (e['caja'][2] - e['caja'][0]) * (e['caja'][3] - e['caja'][1]))['codigo']


def ambientes(msp, eds):
    """Textos de ambientes dentro de los bloques de cada edificación (un nivel de anidamiento)."""
    out = {}
    for ed in eds:
        e = next(e for e in msp.query('INSERT') if e.dxf.name == ed['bloque'])
        c = Counter()

        def ver(v, prof):
            if v.dxftype() in ('TEXT', 'MTEXT'):
                s = texto(v)
                if re.search('[A-ZÁÉÍÓÚÑ]{3}', s) and not re.match(r'^(NPT|NT|N\.P\.T|EDIF)', s):
                    c[s] += 1
            elif v.dxftype() == 'INSERT' and prof < 2:
                try:
                    for w in v.virtual_entities():
                        ver(w, prof + 1)
                except Exception:
                    pass
        for v in e.virtual_entities():
            ver(v, 0)
        out[ed['codigo']] = dict(c)
    return out


def ole(ruta):
    """Imágenes pegadas (OLE2FRAME): propietario (1F = espacio modelo) y tamaño (ancho 41, alto 42 del XDATA OLEBEGIN)."""
    out = []
    with open(ruta, encoding='utf-8', errors='replace') as f:
        lineas = [x.rstrip('\r\n') for x in f]
    for i in range(len(lineas) - 1):
        if lineas[i].strip() == '0' and lineas[i + 1].strip() == 'OLE2FRAME':
            j = i + 2; r = dict(handle=None, propietario=None, capa=None, ancho=None, alto=None, datos=0)
            while lineas[j].strip() != '0':
                cod, val = lineas[j].strip(), lineas[j + 1].strip()
                if cod == '5': r['handle'] = val
                elif cod == '330': r['propietario'] = val
                elif cod == '8': r['capa'] = val
                elif cod == '310': r['datos'] += len(val) // 2
                elif cod == '1070' and val in ('41', '42') and lineas[j + 2].strip() == '1040':
                    r['ancho' if val == '41' else 'alto'] = round(float(lineas[j + 3].strip()), 4)
                j += 2
            out.append(r)
    return out


def rotulo(doc):
    blk = doc.blocks[ROTULO]
    tx = sorted(((texto(e), e.dxf.insert.x, e.dxf.insert.y) for e in blk if e.dxftype() in ('TEXT', 'MTEXT')), key=lambda t: (-t[2], t[1]))
    return [t[0] for t in tx]


def presentaciones(doc):
    out = []
    for lay in doc.layouts:
        if lay.name == 'Model':
            continue
        out.append(dict(nombre=lay.name, bloques=sorted({e.dxf.name for e in lay.query('INSERT')}),
                        ventanas=[dict(centro=[round(v.dxf.view_center_point.x, 1), round(v.dxf.view_center_point.y, 1)],
                                       alto=round(v.dxf.view_height, 1)) for v in lay.query('VIEWPORT')]))
    return out


def circulos(msp):
    return [dict(x=round(e.dxf.center.x, 2), y=round(e.dxf.center.y, 2), r=round(e.dxf.radius, 3), capa=e.dxf.layer)
            for e in msp.query('CIRCLE') if dentro((e.dxf.center.x, e.dxf.center.y), SITIO) and 1.0 <= e.dxf.radius <= 3.0]


def duplicados(pos, tol=0.10):
    n = 0
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            n += math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1]) < tol
    return n


def leer():
    doc, ruta = abrir(); msp = doc.modelspace(); cache = bbox.Cache()
    eds = edificios(msp, cache)
    ley, n_ole_ley = leyenda(doc, cache)
    sitio, fuera = planta(msp, cache)
    blq = {}
    for n in SENALES:
        pos = [s for s in sitio if s['bloque'] == n]
        blq[n] = dict(cantidad=len(pos), por_edificacion=dict(Counter(edificacion_de(s['x'], s['y'], eds) for s in pos)),
                      capas=dict(Counter(s['capa'] for s in pos)), tamanos=dict(Counter('%.2f x %.2f' % (s['w'], s['h']) for s in pos)),
                      duplicados=duplicados([(s['x'], s['y']) for s in pos]), posiciones=[[s['x'], s['y']] for s in pos],
                      fuera_del_terreno=[[s['x'], s['y']] for s in fuera if s['bloque'] == n])
    otros = Counter(s['bloque'] for s in sitio if s['bloque'] not in SENALES)
    ol = ole(ruta)
    return dict(fuente=os.path.relpath(ZIP, RAIZ), sitio=SITIO, rotulo=rotulo(doc), presentaciones=presentaciones(doc),
                edificaciones=eds, leyenda=ley, ole_en_leyenda=n_ole_ley, bloques=blq, otros_bloques_en_planta=dict(otros),
                anidados=anidados(doc, SENALES + [f['bloque'] for f in ley if f['bloque']]),
                ole=ol, ambientes=ambientes(msp, eds), circulos=circulos(msp))


if __name__ == '__main__':
    D = leer()
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump(D, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for f in D['leyenda']:
        print('%-60s %6s %5s  %s' % (f['descripcion'][:60], f['altura'], f['cantidad'], f['bloque']))
    for n, b in D['bloques'].items():
        print('%-14s %4d dup %d fuera %d %s %s' % (n, b['cantidad'], b['duplicados'], len(b['fuera_del_terreno']), b['por_edificacion'], b['tamanos']))
    print('OLE', Counter((o['propietario'], o['ancho'], o['alto']) for o in D['ole']))
    print('anidados', {k: v[1] for k, v in D['anidados'].items() if v[1]})
    print('rotulo', D['rotulo'])
    print('circulos', len(D['circulos']), Counter(c['r'] for c in D['circulos']).most_common(5))
    print(SALIDA)
