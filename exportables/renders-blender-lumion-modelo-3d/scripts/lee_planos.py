# -*- coding: utf-8 -*-
"""Lee los DXF de arquitectura de cualquier proyecto y entrega el modelo en datos: muros, vigas, columnas, puertas, ventanas,
cubiertas, cierres bajo cubierta, áreas verdes y lote, con plantas de control y una lista de avisos para revisar.
No trae datos de ningún proyecto: capas, niveles y códigos van en proyecto.json (ver proyecto_plantilla.json).
Una capa también puede pedirse como 'BLOQUE|CAPA' si solo sirve dentro de un bloque.

Uso (Python normal, con ezdxf, shapely, numpy y matplotlib):
    python lee_planos.py proyecto.json --detecta      # propone las edificaciones y una planta numerada; luego se completan los datos
    python lee_planos.py proyecto.json                # lee y escribe modelo.json + control/*.png + control/AVISOS.txt

Límites conocidos, que se avisan en vez de disimularse:
- Muros rectos y ortogonales entre sí dentro de cada edificación (la edificación puede estar girada). Los diagonales y curvos no se levantan.
- Cuadro de vanos en una tabla de AutoCAD o en un CSV: si está dibujado con líneas y textos, pasarlo a CSV.
- Ningún nivel se supone: lo que falta en proyecto.json detiene la lectura y se le pregunta al usuario.
- Depende del orden del plano: con los muros en capa propia la lectura es exacta; si están mezclados con muebles o pisos (por ejemplo, la capa 0
  de un bloque), el aviso "NO MODELAR AÚN" lo señala y primero hay que separarlos en el CAD.
"""
import argparse
import collections
import csv
import hashlib
import json
import logging
import math
import os
import pickle
import re
import sys

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import polygonize, unary_union

logging.getLogger('ezdxf').setLevel(logging.CRITICAL)                 # avisa miles de veces por datos de bloque que aquí no se usan
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
r3 = lambda v: round(float(v), 3)


def en_capas(L, b, lista):
    """Una capa del plano, o 'BLOQUE|CAPA' cuando la capa solo sirve dentro de un bloque (muros en la capa 0 de un módulo)."""
    return L in lista or (b is not None and '%s|%s' % (b, L) in lista)
ROLES_NIVEL = ('npt', 'viga', 'fondo_viga')


# ================================================================== lectura del DXF (con caché)
def _leer(fichero, ventana=None, prof_max=5):
    import ezdxf
    from ezdxf import path as ezpath
    doc = ezdxf.readfile(fichero); msp = doc.modelspace()
    lineas, arcos, textos, inds, tablas, tramas, cuentas = [], [], [], [], [], [], collections.Counter()

    def fuera(p):
        return ventana is not None and not (ventana[0] <= p[0] <= ventana[2] and ventana[1] <= p[1] <= ventana[3])

    def rec(ents, blk, prof):
        for e in ents:
            t = e.dxftype()
            try:
                if prof == 0:
                    cuentas[t] += 1
                if t == 'INSERT':
                    if prof == 0 and fuera(e.dxf.insert):
                        continue
                    n = e.dxf.name
                    if e.attribs:
                        at = {a.dxf.tag: a.dxf.text.strip() for a in e.attribs}
                        inds.append((n, e.dxf.insert[0], e.dxf.insert[1], at, blk))
                    if prof < prof_max:
                        rec(e.virtual_entities(), blk or n, prof + 1)
                elif t == 'LINE':
                    lineas.append((e.dxf.layer, blk, [(e.dxf.start[0], e.dxf.start[1]), (e.dxf.end[0], e.dxf.end[1])]))
                elif t == 'LWPOLYLINE':
                    p = [(q[0], q[1]) for q in e.get_points('xy')]
                    if e.closed and p:
                        p.append(p[0])
                    lineas.append((e.dxf.layer, blk, p))
                elif t == 'POLYLINE':
                    p = [(v.dxf.location[0], v.dxf.location[1]) for v in e.vertices]
                    if e.is_closed and p:
                        p.append(p[0])
                    lineas.append((e.dxf.layer, blk, p))
                elif t == 'ARC':
                    c = e.dxf.center
                    arcos.append((e.dxf.layer, blk, c[0], c[1], e.dxf.radius, e.dxf.start_angle, e.dxf.end_angle))
                elif t in ('TEXT', 'MTEXT'):
                    s = e.plain_text() if t == 'MTEXT' else e.dxf.text
                    textos.append((e.dxf.layer, blk, e.dxf.insert[0], e.dxf.insert[1], s.strip().replace('\n', ' ')))
                elif t == 'HATCH':
                    an = []
                    for q in ezpath.from_hatch(e):
                        v = [(a[0], a[1]) for a in q.flattening(0.03)]
                        if len(v) >= 3:
                            an.append(v)
                    if an:
                        tramas.append((e.dxf.layer, blk, an))
                elif t == 'ACAD_TABLE' and prof == 0:
                    celdas = []
                    for v in e.virtual_entities():
                        if v.dxftype() in ('TEXT', 'MTEXT'):
                            s = v.plain_text() if v.dxftype() == 'MTEXT' else v.dxf.text
                            celdas.append((v.dxf.insert[0], v.dxf.insert[1], s.strip().replace('\n', ' ')))
                    tablas.append((e.dxf.insert[0], e.dxf.insert[1], celdas))
            except Exception:
                pass
    rec(msp, None, 0)
    return dict(lineas=lineas, arcos=arcos, textos=textos, inds=inds, tablas=tablas, tramas=tramas, cuentas=dict(cuentas))


def leer(fichero, ventana=None):
    """Los DXF pueden pesar cientos de MB: lo leído se guarda junto a ellos y se reutiliza mientras el archivo no cambie."""
    d_ = os.environ.get('CACHE_LECTOR') or os.path.join(os.path.dirname(os.path.abspath(fichero)), '_cache_lector')
    os.makedirs(d_, exist_ok=True)
    clave = hashlib.md5(repr(ventana).encode()).hexdigest()[:6]
    c = os.path.join(d_, os.path.basename(fichero) + '.' + clave + '.pkl')
    if os.path.exists(c) and os.path.getmtime(c) > os.path.getmtime(fichero):
        return pickle.load(open(c, 'rb'))
    print('leyendo', os.path.basename(fichero), '...', flush=True)
    d = _leer(fichero, ventana)
    pickle.dump(d, open(c, 'wb'))
    return d


# ================================================================== cuadro de vanos
def norm(c):
    m = re.match(r'^([PVMA-Z]{1,2})\s*-?\s*0*(\d+)([A-Z]?)$', c.strip().upper())
    return '%s-%d%s' % (m.group(1), int(m.group(2)), m.group(3)) if m else c.strip().upper()


def _numero(s):
    s = s.replace(',', '.').strip()
    return float(s) if re.match(r'^\d+(\.\d+)?$', s) else None


def cuadro_dxf(tablas, cf):
    """{'cod. edificación' o '*': {'P-1': dict(cant, ancho, alto, alf, obs)}} desde tablas de AutoCAD."""
    out = {}
    col = cf.get('columnas', ['codigo', 'cant', 'ancho', 'alto', 'alf'])
    rx = cf.get('codigo_regex', r'^[PVM]-?\d+[A-Z]?$')
    for _, _, celdas in tablas:
        filas = collections.defaultdict(list)
        for x, y, s in celdas:
            filas[round(y, 2)].append((x, s))
        filas = [[s for x, s in sorted(v)] for k, v in sorted(filas.items(), reverse=True)]
        cod = '*'
        if cf.get('titulo_regex'):
            m = next((re.search(cf['titulo_regex'], f[0]) for f in filas if f and re.search(cf['titulo_regex'], f[0])), None)
            if m is None:
                continue
            cod = cf.get('edificacion', 'E-%02d') % int(m.group(1))
        d = out.setdefault(cod, {})
        for f in filas:
            if len(f) >= len(col) and re.match(rx, f[0].strip().upper()):
                v = dict(zip(col, f))
                try:
                    cant = int(float(v.get('cant', '0')))
                except ValueError:
                    continue
                d[norm(f[0])] = dict(cant=cant, ancho=_numero(v.get('ancho', '')), alto=_numero(v.get('alto', '')),
                                     alf=_numero(v.get('alf', '')), obs=f[-1])
    return out


def cuadro_csv(ruta):
    """CSV separado por ; o , con columnas edificacion (o * para todas), codigo, cant, ancho, alto, alf, obs."""
    out = {}
    txt = open(ruta, encoding='utf-8-sig').read()
    for f in csv.DictReader(txt.splitlines(), delimiter=';' if ';' in txt.split('\n')[0] else ','):
        d = out.setdefault((f.get('edificacion') or '*').strip(), {})
        d[norm(f['codigo'])] = dict(cant=int(float(f.get('cant') or 0)), ancho=_numero(f.get('ancho') or ''), alto=_numero(f.get('alto') or ''),
                                    alf=_numero(f.get('alf') or ''), obs=(f.get('obs') or '').strip())
    return out


# ================================================================== geometría básica
def aristas(pts):
    for a, b in zip(pts, pts[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 0.01:
            yield a, b


def eje(a, b, tol=0.01):
    dx, dy = b[0] - a[0], b[1] - a[1]
    if abs(dy) <= tol * max(1, abs(dx)) and abs(dy) < 0.02:
        return 'H'
    if abs(dx) <= tol * max(1, abs(dy)) and abs(dx) < 0.02:
        return 'V'
    return None


def girar(p, g):
    """Gira alrededor del origen local; g en grados. Con g = 0 no cambia el punto."""
    if not g:
        return p
    c, s = math.cos(math.radians(g)), math.sin(math.radians(g))
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def giro_dominante(segs):
    """Ángulo de los muros respecto de los ejes (grados, entre -45 y 45), ponderado por longitud."""
    h = collections.Counter()
    for a, b in segs:
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L > 0.3:
            ang = (math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + 45) % 90 - 45
            h[round(ang * 4) / 4] += L
    if not h:
        return 0.0
    pico = h.most_common(1)[0][0]
    num = den = 0.0
    for a, b in segs:
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = (math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + 45) % 90 - 45
        if L > 0.3 and abs(ang - pico) <= 0.3:
            num += ang * L; den += L
    g = num / den if den else pico
    return round(g, 4) if abs(g) >= 0.05 else 0.0


def union_intervalos(iv, tol=0.003):
    iv = sorted(iv); out = []
    for a, b in iv:
        if out and a <= out[-1][1] + tol:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def muros_de_caras(segs, e_min=0.07, e_max=0.42):
    """Empareja las caras paralelas de los muros -> tramos dict(o, c = eje, t0, t1, e = espesor)."""
    out = []
    for o in ('H', 'V'):
        niveles = collections.defaultdict(list)
        for a, b in segs:
            if eje(a, b) != o:
                continue
            if o == 'H':
                niveles[round((a[1] + b[1]) / 2, 3)].append((min(a[0], b[0]), max(a[0], b[0])))
            else:
                niveles[round((a[0] + b[0]) / 2, 3)].append((min(a[1], b[1]), max(a[1], b[1])))
        ks = sorted(niveles); libre = {k: union_intervalos(niveles[k]) for k in ks}
        for i, k in enumerate(ks):
            for (a, b) in list(libre[k]):
                resto = [(a, b)]
                for k2 in ks[i + 1:]:
                    d = k2 - k
                    if d < e_min:
                        continue
                    if d > e_max:
                        break
                    nuevo = []
                    for (ra, rb) in resto:
                        for (c, dd) in libre[k2]:
                            s, t = max(ra, c), min(rb, dd)
                            if t - s >= 0.05:
                                out.append(dict(o=o, c=round((k + k2) / 2, 3), t0=round(s, 3), t1=round(t, 3), e=round(d, 2)))
                        cort = [(max(ra, c), min(rb, dd)) for (c, dd) in libre[k2] if min(rb, dd) - max(ra, c) >= 0.05]
                        pos = ra
                        for s, t in sorted(cort):
                            if s - pos > 0.05:
                                nuevo.append((pos, s))
                            pos = max(pos, t)
                        if rb - pos > 0.05:
                            nuevo.append((pos, rb))
                    resto = nuevo
                    if not resto:
                        break
    return out


def rect_muro(m):
    h = m['e'] / 2
    return box(m['t0'], m['c'] - h, m['t1'], m['c'] + h) if m['o'] == 'H' else box(m['c'] - h, m['t0'], m['c'] + h, m['t1'])


def piezas_cerradas(segs, a_min, a_max, lado_max=1.2):
    """Columnas y columnetas: componentes conexas de las líneas de la capa -> rectángulo envolvente."""
    if not segs:
        return []
    g = unary_union([LineString([a, b]).buffer(0.004) for a, b in segs])
    out = []
    for p in getattr(g, 'geoms', [g]):
        x0, y0, x1, y1 = p.bounds
        if a_min <= (x1 - x0) * (y1 - y0) <= a_max and max(x1 - x0, y1 - y0) < lado_max:
            out.append([r3(x0 + 0.004), r3(y0 + 0.004), r3(x1 - 0.004), r3(y1 - 0.004)])
    return out


def fusionar(muros, solidos, tol_hueco=0.02, hueco_max=0.6):
    """Une los tramos colineales del mismo espesor cuando el hueco entre ellos lo ocupa una columna o columneta."""
    grupos = collections.defaultdict(list)
    for m in muros:
        grupos[(m['o'], round(m['c'] / 0.02) * 0.02, m['e'])].append(m)
    out = []
    for (o, c, e), ms in grupos.items():
        ms = sorted(ms, key=lambda m: m['t0']); cur = dict(ms[0])
        for m in ms[1:]:
            hueco = m['t0'] - cur['t1']
            une = hueco <= tol_hueco
            if not une and hueco <= hueco_max:
                g = box(cur['t1'], c - e / 2, m['t0'], c + e / 2) if o == 'H' else box(c - e / 2, cur['t1'], c + e / 2, m['t0'])
                une = solidos.intersection(g).area >= 0.8 * g.area
            if une:
                cur['t1'] = max(cur['t1'], m['t1'])
            else:
                out.append(cur); cur = dict(m)
        out.append(cur)
    return out


def extender_a_columnetas(muros, ctas):
    for m in muros:
        for _ in range(3):
            cambio = False
            for c in ctas:
                a0, a1, b0, b1 = (c[0], c[2], c[1], c[3]) if m['o'] == 'H' else (c[1], c[3], c[0], c[2])
                if not (b0 - 0.02 <= m['c'] <= b1 + 0.02):
                    continue
                if abs(a1 - m['t0']) < 0.03 and a0 < m['t0']:
                    m['t0'] = r3(a0); cambio = True
                if abs(a0 - m['t1']) < 0.03 and a1 > m['t1']:
                    m['t1'] = r3(a1); cambio = True
            if not cambio:
                break
    return muros


def huecos(muros, cols, l_min=0.5, l_max=3.4):
    """Vanos sin muro en la línea de cada corrida: desde un extremo hasta el siguiente sólido."""
    solidos = [rect_muro(m) for m in muros] + [box(*c) for c in cols]
    out = {}
    for i, m in enumerate(muros):
        h = m['e'] / 2 - 0.01
        for lado in (1, -1):
            t = m['t1'] if lado == 1 else m['t0']
            a, b = (t, t + lado * l_max)
            g = (box(min(a, b), m['c'] - h, max(a, b), m['c'] + h) if m['o'] == 'H' else box(m['c'] - h, min(a, b), m['c'] + h, max(a, b)))
            mejor = None
            for j, s in enumerate(solidos):
                if j == i or not s.intersects(g):
                    continue
                x0, y0, x1, y1 = s.intersection(g).bounds
                d = ((x0 if lado == 1 else x1) if m['o'] == 'H' else (y0 if lado == 1 else y1)) - t
                d = d * lado
                if d > 0.02 and (mejor is None or d < mejor):
                    mejor = d
            if mejor is not None and l_min <= mejor <= l_max:
                t0, t1 = sorted((t, t + lado * mejor))
                out[(m['o'], round(m['c'], 2), round(t0, 2), round(t1, 2))] = dict(o=m['o'], c=m['c'], t0=r3(t0), t1=r3(t1), e=m['e'])
    return list(out.values())


def restar(iv, cortes):
    out = []
    for s, t in iv:
        pos = s
        for a, b in sorted(cortes):
            if b <= pos or a >= t:
                continue
            if a > pos:
                out.append((pos, a))
            pos = max(pos, b)
        if t > pos:
            out.append((pos, t))
    return out


def ventanas_en_muros(muros, segs, piezas, l_min=0.35):
    """Líneas de vano paralelas dentro de la franja de cada corrida -> tramos de ventana, cortados en columnas."""
    out = []
    for i, m in enumerate(muros):
        iv = []
        for a, b in segs:
            if eje(a, b) != m['o']:
                continue
            k = (a[1] + b[1]) / 2 if m['o'] == 'H' else (a[0] + b[0]) / 2
            if abs(k - m['c']) > m['e'] / 2 + 0.03:
                continue
            s, t = sorted((a[0], b[0]) if m['o'] == 'H' else (a[1], b[1]))
            s, t = max(s, m['t0']), min(t, m['t1'])
            if t - s > 0.05:
                iv.append((s, t))
        cortes = []
        for c in piezas:
            a0, a1, b0, b1 = (c[0], c[2], c[1], c[3]) if m['o'] == 'H' else (c[1], c[3], c[0], c[2])
            if b0 - 0.02 <= m['c'] <= b1 + 0.02:
                cortes.append((a0, a1))
        for s, t in restar(union_intervalos(iv, tol=0.08), cortes):
            if t - s >= l_min:
                out.append(dict(muro=i, o=m['o'], c=m['c'], t0=r3(s), t1=r3(t), e=m['e']))
    return out


def proyectar(muros, x, y, d_max, holgura=0.3):
    mejor = None
    for i, m in enumerate(muros):
        t, d = (x, abs(y - m['c'])) if m['o'] == 'H' else (y, abs(x - m['c']))
        if m['t0'] - holgura <= t <= m['t1'] + holgura and d <= d_max and (mejor is None or d < mejor[2]):
            mejor = (i, min(max(t, m['t0']), m['t1']), d)
    return mejor


def en_linea(muros, cols, x, y, w, d_max=1.6, l_max=7.0):
    """Indicador sin vano ni muro: línea de muro más cercana y tramo libre entre sólidos que contiene la proyección."""
    lineas = {}
    for m in muros:
        k = (m['o'], round(m['c'], 2))
        if k not in lineas or m['e'] > lineas[k]:
            lineas[k] = m['e']
    mejor = None
    for (o, c), e in lineas.items():
        t, d = (x, abs(y - c)) if o == 'H' else (y, abs(x - c))
        if d > d_max:
            continue
        sol = []
        for m in muros:
            if m['o'] == o and abs(m['c'] - c) < 0.05:
                sol.append((m['t0'], m['t1']))
            elif m['o'] != o and m['t0'] - 0.35 <= c <= m['t1'] + 0.35:
                sol.append((m['c'] - m['e'] / 2, m['c'] + m['e'] / 2))
        for q in cols:
            a0, a1, b0, b1 = (q[0], q[2], q[1], q[3]) if o == 'H' else (q[1], q[3], q[0], q[2])
            if b0 - 0.05 <= c <= b1 + 0.05:
                sol.append((a0, a1))
        if any(a - 0.01 <= t <= b + 0.01 for a, b in sol):
            continue
        izq = max([b for a, b in sol if b <= t], default=None); der = min([a for a, b in sol if a >= t], default=None)
        if izq is None and der is not None and der - t <= w + 0.6:
            izq = der - w - 0.2
        if der is None and izq is not None and t - izq <= w + 0.6:
            der = izq + w + 0.2
        if izq is None or der is None or der - izq > l_max or der - izq < w:
            continue
        if der - izq > w + 1.2:
            t = min(max(t, izq + w / 2 + 0.1), der - w / 2 - 0.1); izq, der = t - w / 2 - 0.1, t + w / 2 + 0.1
        if mejor is None or d < mejor[0]:
            mejor = (d, (o, c, e, r3(izq), r3(der)))
    return mejor and mejor[1]


def anfitrion(muros, o, x, y):
    for i, m in enumerate(muros):
        if m['o'] != o:
            continue
        t, k = (x, y) if o == 'H' else (y, x)
        if abs(k - m['c']) <= m['e'] / 2 + 0.02 and m['t0'] - 0.01 <= t <= m['t1'] + 0.01:
            return i
    return None


def centro(v):
    t = (v['t0'] + v['t1']) / 2
    return (t, v['c']) if v['o'] == 'H' else (v['c'], t)


def asignar(vanos, inds, cuadro, d_max, dw_max):
    """Empareja cada vano con el indicador más cercano de ancho compatible."""
    pares = []
    for i, v in enumerate(vanos):
        L = v['t1'] - v['t0']; cx, cy = centro(v)
        for j, (cod, x, y) in enumerate(inds):
            w = cuadro.get(cod, {}).get('ancho')
            dw = abs(w - L) if w else 0.3
            d = math.hypot(x - cx, y - cy)
            if d <= d_max and dw <= dw_max:
                pares.append((d + 2 * dw, i, j))
    usados_v, usados_i, asig = set(), set(), {}
    for c, i, j in sorted(pares):
        if i in usados_v or j in usados_i:
            continue
        usados_v.add(i); usados_i.add(j); asig[i] = j
    return asig, [j for j in range(len(inds)) if j not in usados_i]


def traslacion(pa, pb, paso=0.02):
    """Votación de las diferencias pb - pa: coloca una planta de otra lámina sobre la planta general."""
    pa = np.array(pa); pb = np.array(pb)
    d = (pb[None, :, :] - pa[:, None, :]).reshape(-1, 2)
    k = np.round(d / paso).astype(np.int64)
    u, n = np.unique(k, axis=0, return_counts=True)
    i = int(np.argmax(n)); c = u[i] * paso
    sel = np.all(np.abs(d - c) <= paso, axis=1)
    return float(d[sel, 0].mean()), float(d[sel, 1].mean()), int(n[i])


# ================================================================== terreno
def poligono_de_anillos(anillos):
    """Anillos de una trama: los interiores restan (par e impar)."""
    pol = []
    for a in anillos:
        try:
            p = Polygon(a).buffer(0)
        except Exception:
            continue
        if p.area > 1e-4:
            pol.append(p)
    r = Polygon()
    for p in sorted(pol, key=lambda q: -q.area):
        r = r.symmetric_difference(p)
    return r


def a_lista(g):
    """Polígonos de shapely a [[exterior, [huecos]]] para el JSON."""
    out = []
    for p in getattr(g, 'geoms', [g]):
        if p.geom_type == 'Polygon' and p.area > 1e-3:
            out.append([[[r3(x), r3(y)] for x, y in p.exterior.coords[:-1]], [[[r3(x), r3(y)] for x, y in q.coords[:-1]] for q in p.interiors]])
    return out


def lote_de_capas(lineas, capas, cerca):
    """Contorno del lote desde sus capas, dentro de 'cerca' (el archivo puede traer copias de la planta).
    Prueba en orden: contorno cerrado, líneas que se cierran, franja de dos líneas del cerco y, si queda abierto, envolvente.
    Devuelve (polígono, criterio)."""
    segs = [LineString(p) for L, b, p in lineas if en_capas(L, b, capas) and len(p) >= 2 and all(cerca.contains(Point(q)) for q in p)]
    if not segs:
        return None, ''
    env = unary_union(segs).convex_hull
    util = lambda g: g.area >= 0.5 * env.area
    c1 = [Polygon(s.coords).buffer(0) for s in segs if s.is_ring and len(s.coords) >= 4]
    if c1 and util(max(c1, key=lambda p: p.area)):
        return max(c1, key=lambda p: p.area), 'contorno cerrado'
    c2 = list(polygonize(unary_union(segs)))
    if c2 and util(max(c2, key=lambda p: p.area)):
        return max(c2, key=lambda p: p.area), 'líneas cerradas'
    b_ = unary_union([s.buffer(0.3) for s in segs])
    c3 = [Polygon(p.exterior) for p in getattr(b_, 'geoms', [b_]) if p.interiors]
    if c3 and util(max(c3, key=lambda p: p.area)):
        return max(c3, key=lambda p: p.area).buffer(-0.3), 'franja del cerco'
    return env, 'envolvente: el cerco del plano no cierra'


# ================================================================== lectura de una edificación
def indicadores(fuente, cf, zona_mundo, tr, g):
    """Puertas y ventanas señaladas en la planta -> [(código, x, y)] en el marco de la edificación."""
    ip, iv = [], []
    dx, dy = tr
    for n, x, y, at, b in fuente['inds']:
        X, Y = x + dx, y + dy
        if not zona_mundo.contains(Point(X, Y)):
            continue
        for clave, lista in (('puerta', ip), ('ventana', iv)):
            c = cf.get(clave) or {}
            if c.get('bloque') and c['bloque'] in n:
                num = at.get(c.get('atr_numero', ''), '')
                let = at.get(c['atr_letra'], c.get('letra', '')) if c.get('atr_letra') else c.get('letra', '')
                lista.append((norm('%s-%s' % (let, num)),) + girar((X, Y), g))
    if cf.get('texto_regex'):
        for L, b, x, y, s in fuente['textos']:
            X, Y = x + dx, y + dy
            if re.match(cf['texto_regex'], s.strip().upper()) and zona_mundo.contains(Point(X, Y)):
                c = norm(s)
                (iv if c.startswith('V') else ip).append((c,) + girar((X, Y), g))
    return ip, iv


def leer_edificacion(e, P, C, pg_lin, pg_arc, plantas, tit, cu):
    cod = e['cod']; x0, y0, x1, y1 = e['zona']; cap = C['capas']; g = e.get('giro', 'auto')
    zona = box(x0 - 0.4, y0 - 0.4, x1 + 0.4, y1 + 0.4)
    dentro = lambda p: zona.contains(Point(p[0], p[1]))
    mundo = collections.defaultdict(list)
    for L, b, p in pg_lin:
        if all(dentro(q) for q in p):
            mundo[L].extend(aristas(p))
            if b is not None:
                mundo['%s|%s' % (b, L)].extend(aristas(p))
    f = lambda clave: [ab for L in cap.get(clave, []) for ab in mundo[L]]
    caras_m = f('muro')
    if g == 'auto':
        g = -giro_dominante(caras_m)
    rot = lambda ab: (girar(ab[0], g), girar(ab[1], g))
    capas = {k: [rot(ab) for ab in f(k)] for k in ('muro', 'muro_bajo', 'columna', 'columneta', 'vano', 'techo')}
    obs = []

    pr = [q for ab in capas['techo'] for q in ab]
    if pr:
        xs, ys = [q[0] for q in pr], [q[1] for q in pr]
        techo = [r3(min(xs)), r3(min(ys)), r3(max(xs)), r3(max(ys))]
    else:
        esq = [girar(q, g) for q in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        techo = [r3(min(q[0] for q in esq)), r3(min(q[1] for q in esq)), r3(max(q[0] for q in esq)), r3(max(q[1] for q in esq))]
        obs.append('%s: sin líneas de la capa de techo en la zona; se usó la zona como contorno de la cubierta' % cod)

    ca, cm = C.get('columna', {}).get('area', [0.03, 0.5]), C.get('columna', {}).get('lado_max', 1.2)
    ta = C.get('columneta', {}).get('area', [0.008, 0.2])
    cols = piezas_cerradas(capas['columna'], ca[0], ca[1], cm)
    ctas = piezas_cerradas(capas['columneta'], ta[0], ta[1])
    solidos = unary_union([box(*c) for c in cols + ctas]) if cols + ctas else Polygon()
    em = C.get('espesor_muro', [0.07, 0.42])
    caras = capas['muro']
    tramos = muros_de_caras(caras, em[0], em[1])
    muros = fusionar(tramos, solidos)
    muros = extender_a_columnetas([m for m in muros if m['t1'] - m['t0'] >= 0.12], ctas)
    muros = fusionar(muros, solidos)
    bajos = [m for m in muros_de_caras(capas['muro_bajo'], em[0], em[1]) if m['t1'] - m['t0'] >= 0.12]

    # lo que no se puede levantar se dice
    L_tot = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in caras)
    L_dia = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in caras if eje(a, b) is None)
    if L_dia > 0.5:
        obs.append('%s: %.1f m de caras de muro diagonales o curvas no se levantan (de %.1f m); modelarlas en el generador del proyecto' % (cod, L_dia, L_tot))
    L_par = 2 * sum(m['t1'] - m['t0'] for m in tramos)
    if L_tot - L_dia > 1 and L_par < 0.6 * (L_tot - L_dia):
        obs.append('%s: solo %.0f %% de las caras de muro forman pares dentro del rango de espesores %s; revisar capa y rango'
                   % (cod, 100 * L_par / (L_tot - L_dia), em))
    if not muros:
        obs.append('%s: no se encontró ningún muro; revisar la capa de muros y la zona' % cod)
    # capa mezclada: muebles, pisos o tarrajeo leídos como muro. Una edificación real ronda 0.2 a 0.5 m de muro por m2 de planta
    L_m = [m['t1'] - m['t0'] for m in muros]
    area_t = max((techo[2] - techo[0]) * (techo[3] - techo[1]), 1)
    dens = sum(L_m) / area_t; cortos = sum(q < 0.5 for q in L_m) / max(len(L_m), 1)
    mezclada = dens > 0.7 or (len(L_m) >= 10 and cortos > 0.3)
    if mezclada:
        obs.append('%s: NO MODELAR AÚN: %.2f m de muro por m2 y %.0f %% de tramos cortos; la capa trae más que muros. Pasar los muros a una capa propia en el CAD o indicar otra capa'
                   % (cod, dens, 100 * cortos))

    vanos_h = huecos(muros, cols, l_max=C.get('vano_max', 3.6))
    vent = ventanas_en_muros(muros, capas['vano'], cols + ctas)

    # arcos de giro de puerta, por si no hay indicadores
    arcos = []
    for L, b, cx, cy, r_, a0, a1 in pg_arc:
        if 0.55 <= r_ <= 1.30 and 80 <= (a1 - a0) % 360 <= 95 and dentro((cx, cy)):
            arcos.append(girar((cx, cy), g) + (r_,))

    # indicadores, de la planta general o de otra lámina colocada por votación
    cf = C.get('vanos', {}); tr = None; desplaz = (0.0, 0.0); ox, oy = C['origen']
    ip, iv_ = [], []
    z_mundo = box(x0 - 2.5, y0 - 2.5, x1 + 2.5, y1 + 2.5)
    if plantas is not None:
        A = plantas
        t_ = tit.get(cod)
        if t_:
            cj = cf['planta'].get('caja_titulo', [-32, -3, 32, 48])
            pa = [q for L, b, p in A['lineas'] if p and L in cf['planta']['capas_muro'] for q in p
                  if cj[0] < q[0] - t_[0] < cj[2] and cj[1] < q[1] - t_[1] < cj[3]]
            pb = sorted(set((round(q[0], 3), round(q[1], 3)) for ab in caras_m for q in ab))
            pa = sorted(set((round(x, 3), round(y, 3)) for x, y in pa))
            if len(pa) > 6000:
                pa = pa[::len(pa) // 6000 + 1]
            if pa and pb:
                dx, dy, votos = traslacion(pa, pb)
                tr = dict(dx=dx, dy=dy, votos=votos, n_pg=len(pb)); desplaz = (dx, dy)
                if votos < 0.3 * len(pb):
                    obs.append('%s: la planta de detalle coincide poco con la planta general (%d de %d puntos); revisar puertas y ventanas' % (cod, votos, len(pb)))
        else:
            obs.append('%s: no se halló el título de su planta de detalle; sin indicadores de puertas y ventanas' % cod)
        if tr:
            ip, iv_ = indicadores(A, cf, z_mundo, desplaz, g)
    elif cf.get('puerta') or cf.get('ventana') or cf.get('texto_regex'):
        fuente = dict(inds=[(n, x - ox, y - oy, at, b) for n, x, y, at, b in P['inds']], textos=[(L, b, x - ox, y - oy, s) for L, b, x, y, s in P['textos']])
        ip, iv_ = indicadores(fuente, cf, z_mundo, (0.0, 0.0), g)

    cuadro = dict(cu.get('*', {})); cuadro.update(cu.get(cod, {}))
    dfl = cf.get('defecto', {})
    sl_rx, vd_rx, vd_no = cf.get('sobreluz_regex'), cf.get('vidrio_regex'), cf.get('vidrio_excluye_regex')

    def falta_medida(cod_, cual):
        obs.append('%s: %s sin %s en el cuadro ni en "vanos.defecto"; no se coloca: preguntar' % (cod, cod_, cual))

    def tipo_de(c, ancho_med, clase):
        if c in cuadro:
            return c, dict(cuadro[c], ref=c), False
        cand = [(abs((v['ancho'] or 0) - ancho_med), k, v) for k, v in cuadro.items() if k[0] in clase]
        if not cand:
            es_p = 'P' in clase
            return c, dict(cant=0, ancho=ancho_med, alto=dfl.get('puerta_alto' if es_p else 'ventana_alto'), alf=dfl.get('ventana_alf'), obs='', ref=None), True
        _, k, v = min(cand)
        return c, dict(v, ancho=r3(ancho_med), ref=k), True

    puertas, nuevos, ventanas = [], [], []
    tiene_ind = bool(ip or iv_)
    # puertas: vano detectado con indicador compatible; si no, sobre la línea de muro más cercana
    a_p, sin_p = asignar(vanos_h, ip, cuadro, 2.6, 0.45)
    for i, j in a_p.items():
        v = vanos_h[i]; cx, cy = centro(v); L = v['t1'] - v['t0']
        c, d, raro = tipo_de(ip[j][0], L, 'PM')
        if not d['alto']:
            falta_medida(c, 'alto'); continue
        w = min(d['ancho'] or L, L - 0.02)
        puertas.append(dict(cod=c, x=r3(cx), y=r3(cy), o=v['o'], ancho=r3(w), alto=d['alto'], obs=d['obs'], via='vano'))
        nuevos.append(dict(o=v['o'], c=v['c'], t0=v['t0'], t1=v['t1'], e=v['e']))
        if raro:
            obs.append('%s: indicador %s no figura en el cuadro de vanos; se usó el ancho del vano (%.2f)' % (cod, c, L))
    for j in sin_p:
        c0, x, y = ip[j]
        c, d, raro = tipo_de(c0, dfl.get('puerta_ancho') or 0.9, 'PM'); w = d['ancho'] or dfl.get('puerta_ancho') or 0.9
        if not d['alto']:
            falta_medida(c0, 'alto'); continue
        ln = en_linea(muros + nuevos, cols, x, y, w)
        if ln:
            o, cc, e_, t0, t1 = ln; t = (t0 + t1) / 2; w = min(w, t1 - t0 - 0.02)
            nuevos.append(dict(o=o, c=cc, t0=t0, t1=t1, e=e_))
            px, py = (t, cc) if o == 'H' else (cc, t)
            puertas.append(dict(cod=c, x=r3(px), y=r3(py), o=o, ancho=r3(w), alto=d['alto'], obs=d['obs'], via='linea'))
            continue
        pr_ = proyectar(muros, x, y, 1.6)
        if pr_ is None:
            obs.append('%s: indicador %s en (%.2f, %.2f) sin muro cercano; no se coloca' % (cod, c0, x, y)); continue
        i, t, _ = pr_; m = muros[i]
        t = min(max(t, m['t0'] + w / 2 + 0.02), m['t1'] - w / 2 - 0.02)
        px, py = (t, m['c']) if m['o'] == 'H' else (m['c'], t)
        puertas.append(dict(cod=c, x=r3(px), y=r3(py), o=m['o'], ancho=r3(w), alto=d['alto'], obs=d['obs'], via='proyeccion'))
    # sin indicadores: puerta medida donde hay vano con arco de giro cerca
    if not tiene_ind and dfl.get('puerta_alto'):
        for v in vanos_h:
            cx, cy = centro(v)
            if any(math.hypot(a[0] - cx, a[1] - cy) <= a[2] + 0.6 for a in arcos):
                puertas.append(dict(cod='P?', x=r3(cx), y=r3(cy), o=v['o'], ancho=r3(v['t1'] - v['t0'] - 0.02), alto=dfl['puerta_alto'], obs='', via='medido'))
                nuevos.append(dict(o=v['o'], c=v['c'], t0=v['t0'], t1=v['t1'], e=v['e']))
    muros = fusionar(muros + nuevos, solidos)

    a_v, sin_v = asignar(vent, iv_, cuadro, 3.2, 0.7)
    for i, j in a_v.items():
        v = vent[i]; cx, cy = centro(v); L = v['t1'] - v['t0']
        c, d, raro = tipo_de(iv_[j][0], L, 'V')
        if not d['alto'] or d['alf'] is None and dfl.get('ventana_alf') is None:
            falta_medida(c, 'alto o alféizar'); continue
        w = min(d['ancho'] or L, L + 0.05)
        ventanas.append(dict(cod=c, x=r3(cx), y=r3(cy), o=v['o'], ancho=r3(w), alto=d['alto'], alf=d['alf'] if d['alf'] is not None else dfl['ventana_alf'], via='vano'))
        if raro:
            obs.append('%s: indicador %s no figura en el cuadro de vanos; ancho del vano %.2f y alto/alféizar de %s' % (cod, c, L, d.get('ref')))
    for j in sin_v:
        c0, x, y = iv_[j]; pr_ = proyectar(muros, x, y, 3.2)
        if pr_ is None:
            obs.append('%s: indicador %s en (%.2f, %.2f) sin muro cercano; no se coloca' % (cod, c0, x, y)); continue
        i, t, _ = pr_; m = muros[i]
        c, d, raro = tipo_de(c0, dfl.get('ventana_ancho') or 1.5, 'V')
        if not d['alto'] or d['alf'] is None and dfl.get('ventana_alf') is None:
            falta_medida(c0, 'alto o alféizar'); continue
        w = d['ancho'] or dfl.get('ventana_ancho') or 1.5
        t = min(max(t, m['t0'] + w / 2 + 0.02), m['t1'] - w / 2 - 0.02)
        px, py = (t, m['c']) if m['o'] == 'H' else (m['c'], t)
        ventanas.append(dict(cod=c, x=r3(px), y=r3(py), o=m['o'], ancho=r3(w), alto=d['alto'], alf=d['alf'] if d['alf'] is not None else dfl['ventana_alf'], via='proyeccion'))
    usados = set(a_v)
    falta = collections.Counter({k: d['cant'] for k, d in cuadro.items() if k[0] == 'V'})
    for v in ventanas:
        falta[v['cod']] -= 1
    for i, v in enumerate(vent):
        if i in usados:
            continue
        L = v['t1'] - v['t0']
        cand = [(abs(cuadro[k]['ancho'] - L), k) for k, n in falta.items() if n > 0 and cuadro[k]['ancho'] and abs(cuadro[k]['ancho'] - L) <= 0.25]
        cx, cy = centro(v)
        if cand:
            _, k = min(cand); falta[k] -= 1; d = cuadro[k]
            ventanas.append(dict(cod=k, x=r3(cx), y=r3(cy), o=v['o'], ancho=r3(min(d['ancho'], L + 0.05)), alto=d['alto'], alf=d['alf'], via='cuadro'))
            obs.append('%s: %s colocada en un vano de ventana sin indicador (ancho %.2f), según el cuadro de vanos' % (cod, k, L))
        elif not tiene_ind and dfl.get('ventana_alto') and dfl.get('ventana_alf') is not None:
            ventanas.append(dict(cod='V?', x=r3(cx), y=r3(cy), o=v['o'], ancho=r3(L), alto=dfl['ventana_alto'], alf=dfl['ventana_alf'], via='medido'))
    if not tiene_ind and (puertas or ventanas):
        obs.append('%s: sin indicadores: %d puertas y %d ventanas medidas en planta, con la altura de "vanos.defecto"; confirmar con la arquitecta' % (cod, len(puertas), len(ventanas)))
    elif not tiene_ind:
        obs.append('%s: sin indicadores ni "vanos.defecto": no se colocaron puertas ni ventanas' % cod)
    for p in puertas:
        p['sobreluz'] = bool(sl_rx and re.search(sl_rx, p['obs'], re.I))
        p['vidrio'] = bool(vd_rx and re.search(vd_rx, p['obs'], re.I)) and not (vd_no and re.search(vd_no, p['obs'], re.I))

    def tramo(v):
        t = v['x'] if v['o'] == 'H' else v['y']
        return (t - v['ancho'] / 2, t + v['ancho'] / 2)

    def altura(v):
        return (0.0, v['alto'] + (9 if v.get('sobreluz') else 0)) if 'alf' not in v else (v['alf'], v['alf'] + v['alto'])
    aceptados = []
    for lista, nom in ((puertas, 'puerta'), (ventanas, 'ventana')):
        limpio = []
        for v in sorted(lista, key=lambda v: v['via'] != 'vano'):
            h = anfitrion(muros, v['o'], v['x'], v['y']); v['muro'] = h
            if h is None:
                obs.append('%s: %s %s sin muro anfitrión; no se coloca' % (cod, nom, v['cod'])); continue
            choca = [u for u in aceptados if u['muro'] == h and min(tramo(u)[1], tramo(v)[1]) - max(tramo(u)[0], tramo(v)[0]) > 0.05]
            for u in list(choca):
                if 'alf' in v and 'alf' not in u and v['alf'] >= u['alto'] - 0.01:
                    if u['sobreluz']:
                        obs.append('%s: %s sin sobreluz por la ventana alta %s' % (cod, u['cod'], v['cod']))
                    u['sobreluz'] = False; choca.remove(u)
                elif min(altura(u)[1], altura(v)[1]) - max(altura(u)[0], altura(v)[0]) <= 0.01:
                    choca.remove(u)
            if choca:
                obs.append('%s: %s %s se superpone con %s; no se coloca' % (cod, nom, v['cod'], choca[0]['cod'])); continue
            limpio.append(v); aceptados.append(v)
        lista[:] = limpio
    cnt = collections.Counter(v['cod'] for v in puertas + ventanas)
    for k, d in sorted(cuadro.items()):
        if (cod in cu and k in cu[cod]) and cnt.get(k, 0) != d['cant']:
            obs.append('%s: %s colocadas %d, cuadro de vanos %d' % (cod, k, cnt.get(k, 0), d['cant']))
    return dict(cod=cod, nombre=e.get('nombre', ''), giro=g, techo=techo, mezclada=mezclada, muros=muros, bajos=bajos, columnas=cols, columnetas=ctas, tr=tr, ind_p=ip, ind_v=iv_,
                puertas=puertas, ventanas=ventanas, obs=obs, huecos=vanos_h, tramos_ventana=vent)


# ================================================================== alturas, cubiertas y cierres
def z_inf(t, x, y):
    """Altura de la cara inferior de la cubierta t en el punto (x, y)."""
    x0, y0, x1, y1 = t['rect']; p = t.get('pend', 0.0); ti = t.get('tipo', 'dos_aguas')
    if ti == 'plana':
        return t['base']
    if ti == 'un_agua':                                                # alta en 'alto': 'x0', 'x1', 'y0' o 'y1'
        d = {'x0': x1 - x, 'x1': x - x0, 'y0': y1 - y, 'y1': y - y0}[t.get('alto', 'x1')]
        return t['base'] + p * d
    if ti == 'cuatro_aguas':
        return t['base'] + p * min(x - x0, x1 - x, y - y0, y1 - y)
    return t['base'] + p * (min(x - x0, x1 - x) if t['eje'] == 'y' else min(y - y0, y1 - y))


def cierre(t, o, c, a0, a1, zw):
    """Polígono entre el tope del muro y la cubierta, en el plano del muro. o = 'H' (y = c) o 'V' (x = c)."""
    x0, y0, x1, y1 = t['rect']
    q = [a0, a1]
    if t.get('tipo') == 'cuatro_aguas':
        m_ = min(x1 - x0, y1 - y0) / 2
        q += [(x0 if o == 'H' else y0) + m_, (x1 if o == 'H' else y1) - m_]
    elif t.get('tipo', 'dos_aguas') == 'dos_aguas':
        q.append((x0 + x1) / 2 if o == 'H' else (y0 + y1) / 2)
    q = sorted({r3(v) for v in q if a0 - 1e-6 <= v <= a1 + 1e-6})
    P = lambda a, z: [r3(a), r3(c), r3(z)] if o == 'H' else [r3(c), r3(a), r3(z)]
    alto = [(a, z_inf(t, a, c) if o == 'H' else z_inf(t, c, a)) for a in q]
    if max(z for a, z in alto) - zw < 0.03:
        return None
    arriba = [(a, max(z - 0.02, zw)) for a, z in alto]
    pol = [P(a0, zw)] + [P(a, z) for a, z in arriba] + [P(a1, zw)]
    return [q for i, q in enumerate(pol) if q != pol[i - 1]]             # sin puntos repetidos donde la cubierta nace al ras del muro


def modelo(r, e):
    """Muros, vigas, columnas, vanos, cubiertas y cierres de una edificación, con sus niveles de proyecto.json."""
    falta = [k for k in ROLES_NIVEL if e.get(k) is None]
    if falta:
        raise SystemExit('Faltan en %s: %s. Tomarlos de los cortes o preguntarlos; no se suponen.' % (r['cod'], ', '.join(falta)))
    npt, zv, fv = e['npt'], e['viga'], e['fondo_viga']; cuerpos = e.get('cuerpos', [])
    rects = [rect_muro(m) for m in r['muros']] + [box(*c) for c in r['columnas']]
    if not rects:
        return None
    wx0, wy0, wx1, wy1 = unary_union(rects).bounds

    def cuerpo_de(xa, ya, xb, yb, tol):
        for c in cuerpos:
            q = c['zona']
            if q[0] - tol <= min(xa, xb) and max(xa, xb) <= q[2] + tol and q[1] - tol <= min(ya, yb) and max(ya, yb) <= q[3] + tol:
                return c
        return None
    muros, vigas = [], []
    for m in r['muros']:
        piezas = [(m['t0'], m['t1'])]
        for c in cuerpos:
            for corte in ((c['zona'][1], c['zona'][3]) if m['o'] == 'V' else (c['zona'][0], c['zona'][2])):
                piezas = [q for a, b in piezas for q in (((a, corte), (corte, b)) if a < corte < b else ((a, b),))]
        for a, b in piezas:
            p0, p1 = ((a, m['c']), (b, m['c'])) if m['o'] == 'H' else ((m['c'], a), (m['c'], b))
            cu_ = cuerpo_de(p0[0], p0[1], p1[0], p1[1], 0.3)
            z1, fo = (cu_['viga'], cu_['fondo_viga']) if cu_ else (zv, fv)
            ext = (m['o'] == 'H' and min(abs(m['c'] - wy0), abs(m['c'] - wy1)) < 0.35) or (m['o'] == 'V' and min(abs(m['c'] - wx0), abs(m['c'] - wx1)) < 0.35)
            muros.append([r3(p0[0]), r3(p0[1]), r3(p1[0]), r3(p1[1]), m['e'], npt, r3(z1), bool(ext)])
            vigas.append([r3(p0[0]), r3(p0[1]), r3(p1[0]), r3(p1[1]), r3(m['e'] + 0.02), r3(fo), r3(z1)])
    cols = []
    for c in r['columnas']:
        cx, cy = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
        cu_ = cuerpo_de(cx, cy, cx, cy, 0.4)
        cols.append([r3(cx), r3(cy), r3(c[2] - c[0]), r3(c[3] - c[1]), npt, r3(cu_['viga'] if cu_ else zv)])
    puertas = [dict(cod=p['cod'], x=p['x'], y=p['y'], o=p['o'], ancho=p['ancho'], alto=p['alto'], sill=npt, sobreluz=p['sobreluz'], vidrio=p['vidrio'], via=p['via']) for p in r['puertas']]
    ventanas = [dict(cod=v['cod'], x=v['x'], y=v['y'], o=v['o'], ancho=v['ancho'], alto=v['alto'], sill=r3(npt + v['alf']), via=v['via']) for v in r['ventanas']]

    tipo = e.get('cubierta', 'dos_aguas')
    if e.get('cubiertas'):
        techos = [dict(t, rect=[r3(v) for v in t['rect']], base=r3(t['base'])) for t in e['cubiertas']]
    else:
        if tipo != 'plana' and e.get('pendiente') is None:
            raise SystemExit('Falta en %s: pendiente (o "cubierta": "plana"). Tomarla de los cortes o preguntarla.' % r['cod'])
        if tipo == 'dos_aguas' and e.get('cumbrera') not in ('x', 'y'):
            raise SystemExit('Falta en %s: cumbrera ("x" o "y"). Revisar la planta de techos.' % r['cod'])
        t = dict(rect=[r3(v) for v in r['techo']], base=r3(zv), pend=e.get('pendiente', 0.0), eje=e.get('cumbrera'), tipo=tipo)
        if tipo == 'un_agua':
            t['alto'] = e.get('lado_alto', 'x1')
        techos = [t]

    cierres = []
    for t in techos:
        if t.get('sobretecho') or t.get('tipo') == 'plana':
            continue
        tx0, ty0, tx1, ty1 = t['rect']
        planos = collections.defaultdict(list)                           # muros de la cubierta por plano
        for w in muros:
            o = 'H' if abs(w[1] - w[3]) < 1e-6 else 'V'; c = w[1] if o == 'H' else w[0]
            a, b = sorted((w[0], w[2])) if o == 'H' else sorted((w[1], w[3]))
            if not ((ty0 <= c <= ty1) if o == 'H' else (tx0 <= c <= tx1)):
                continue
            ini, fin = (tx0, tx1) if o == 'H' else (ty0, ty1)
            a, b = max(a, ini), min(b, fin)
            if b - a > 0.1:
                planos[(o, round(c, 2))].append((a, b, w[4], w[6]))
        for o in ('H', 'V'):
            ini, fin = (tx0, tx1) if o == 'H' else (ty0, ty1)
            gr = sorted(k for k in planos if k[0] == o)
            buenos = []
            for k in gr:
                cob = sum(b - a for a, b in union_intervalos([(a, b) for a, b, _, _ in planos[k]]))
                if cob >= 0.5 * (fin - ini):
                    buenos.append(k)
            for k in (buenos[0], buenos[-1]) if len(buenos) > 1 else buenos:
                a_ = min(a for a, b, _, _ in planos[k]); b_ = max(b for a, b, _, _ in planos[k])
                esp = max(x[2] for x in planos[k]); zw = max(x[3] for x in planos[k])
                pol = cierre(t, k[0], k[1], a_, b_, zw)
                if pol:
                    cierres.append(dict(pol=pol, esp=esp))
    cumbreras = []
    for t in techos:
        x0_, y0_, x1_, y1_ = t['rect']
        cumbreras.append(r3(max(z_inf(t, a_, b_) for a_, b_ in (((x0_ + x1_) / 2, (y0_ + y1_) / 2), (x0_, y0_), (x1_, y0_), (x1_, y1_), (x0_, y1_)))))
    obs = list(r['obs'])
    if e.get('techo_rotulado') is not None and cumbreras and abs(max(cumbreras) - e['techo_rotulado']) > 0.10:
        obs.append('%s: la cumbrera calculada es +%.2f y la rotulada en los cortes +%.2f; por confirmar con la arquitecta' % (r['cod'], max(cumbreras), e['techo_rotulado']))
    return dict(cod=r['cod'], nombre=r['nombre'], giro=r['giro'], npt=npt, vereda=e.get('vereda_perimetral', 0), alto_muro_bajo=e.get('alto_muro_bajo'), contorno_muros=[r3(wx0), r3(wy0), r3(wx1), r3(wy1)], techo=r['techo'],
                muros=muros, vigas=vigas, columnas=cols, puertas=puertas, ventanas=ventanas, techos=techos, cierres=cierres,
                muros_bajos=[[r3(m['t0'] if m['o'] == 'H' else m['c']), r3(m['c'] if m['o'] == 'H' else m['t0']), r3(m['t1'] if m['o'] == 'H' else m['c']),
                              r3(m['c'] if m['o'] == 'H' else m['t1']), m['e']] for m in r['bajos']],
                cumbreras_calculadas=cumbreras, obs=obs)


# ================================================================== detección y controles
def detecta(P, C, salida):
    """Propone las edificaciones: grupos de líneas de muro. Los datos de cada una los completa quien conoce los cortes."""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    ox, oy = C['origen']; cap = C['capas']
    segs = []
    for L, b, p in P['lineas']:
        if en_capas(L, b, cap.get('muro', [])) and p:
            q = [(x - ox, y - oy) for x, y in p]
            segs.extend(aristas(q))
    v = C.get('ventana_local')
    if v:
        segs = [s for s in segs if v[0] <= s[0][0] <= v[2] and v[1] <= s[0][1] <= v[3]]
    if not segs:
        raise SystemExit('Ninguna línea en las capas de muro %s. Revisar con explora_dxf.py.' % cap.get('muro'))
    g = unary_union([LineString(s).buffer(0.8) for s in segs])
    grupos = sorted([p for p in getattr(g, 'geoms', [g]) if p.area > C.get('area_min_edificacion', 12)], key=lambda p: (-p.bounds[1], p.bounds[0]))
    techos = [((a[0] - ox, a[1] - oy), (b[0] - ox, b[1] - oy)) for L, b_, p in P['lineas'] if en_capas(L, b_, cap.get('techo', [])) and p for a, b in aristas(p)]
    prop = []
    fig, ax = plt.subplots(figsize=(11, 14))
    for a, b in segs:
        ax.plot([a[0], b[0]], [a[1], b[1]], color='0.35', lw=0.3)
    for i, p in enumerate(grupos, 1):
        x0, y0, x1, y1 = p.buffer(-0.7).bounds
        rx0, ry0, rx1, ry1 = x0, y0, x1, y1
        cerca = [q for s in techos for q in s if x0 - 2.2 <= q[0] <= x1 + 2.2 and y0 - 2.2 <= q[1] <= y1 + 2.2]
        if cerca:
            rx0, ry0 = min([x0] + [q[0] for q in cerca]), min([y0] + [q[1] for q in cerca]); rx1, ry1 = max([x1] + [q[0] for q in cerca]), max([y1] + [q[1] for q in cerca])
        cum, conf = None, 'sin dato'
        ls = [s for s in techos if rx0 <= s[0][0] <= rx1 and ry0 <= s[0][1] <= ry1 and rx0 <= s[1][0] <= rx1 and ry0 <= s[1][1] <= ry1]
        en_y = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in ls if eje(a, b) == 'V' and abs((a[0] + b[0]) / 2 - (rx0 + rx1) / 2) < 0.4)
        en_x = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in ls if eje(a, b) == 'H' and abs((a[1] + b[1]) / 2 - (ry0 + ry1) / 2) < 0.4)
        if en_y > en_x and en_y > 0:
            cum, conf = 'y', 'línea central en la capa de techo'
        elif en_x > en_y:
            cum, conf = 'x', 'línea central en la capa de techo'
        elif (rx1 - rx0) != (ry1 - ry0):
            cum, conf = ('y' if ry1 - ry0 > rx1 - rx0 else 'x'), 'lado largo: confirmar'
        prop.append(dict(cod='E-%02d' % i, nombre='', zona=[r3(rx0), r3(ry0), r3(rx1), r3(ry1)], cumbrera=cum, cumbrera_criterio=conf,
                         npt=None, viga=None, fondo_viga=None, pendiente=None))
        ax.add_patch(plt.Rectangle((rx0, ry0), rx1 - rx0, ry1 - ry0, fill=False, ec='#c0392b', lw=1))
        ax.text((rx0 + rx1) / 2, (ry0 + ry1) / 2, str(i), color='#c0392b', fontsize=13, ha='center', va='center')
    ax.set_aspect('equal'); ax.set_title('Edificaciones propuestas: comprobar número y contorno')
    os.makedirs(salida, exist_ok=True)
    fig.savefig(os.path.join(salida, 'PROPUESTA_EDIFICACIONES.png'), dpi=120, bbox_inches='tight'); plt.close(fig)
    json.dump(prop, open(os.path.join(salida, 'edificaciones_propuestas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%d edificaciones propuestas en %s' % (len(prop), salida))
    for q in prop:
        print(' ', q['cod'], q['zona'], 'cumbrera', q['cumbrera'], '(%s)' % q['cumbrera_criterio'])


def vista(m, ruta):
    """Planta de control: muros, columnas, puertas (verde) y ventanas (rojo) con su código."""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    x0, y0, x1, y1 = m['techo']
    fig, ax = plt.subplots(figsize=(13, 13 * (y1 - y0) / max(x1 - x0, 1) + 1.2))
    ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ls='--', lw=0.8, ec='0.5'))
    for w in m['muros']:
        a = LineString([(w[0], w[1]), (w[2], w[3])]).buffer(w[4] / 2, cap_style=2)
        ax.fill(*a.exterior.xy, color='0.25' if w[7] else '0.55', lw=0)
    for c in m['columnas']:
        ax.add_patch(plt.Rectangle((c[0] - c[2] / 2, c[1] - c[3] / 2), c[2], c[3], color='#7b1f2d'))
    for lst, col in ((m['puertas'], '#1f7a3a'), (m['ventanas'], '#c0392b')):
        for v in lst:
            h = v['ancho'] / 2; o = v['o']
            ax.add_patch(plt.Rectangle((v['x'] - h, v['y'] - 0.14) if o == 'H' else (v['x'] - 0.14, v['y'] - h), 2 * h if o == 'H' else 0.28, 0.28 if o == 'H' else 2 * h, color=col, alpha=0.8))
            ax.text(v['x'], v['y'] + (0.22 if o == 'H' else 0), v['cod'], fontsize=6.5, ha='center', va='bottom' if o == 'H' else 'center', rotation=0 if o == 'H' else 90, color=col)
    for t in m['techos']:
        a, b, c, d = t['rect']
        if t.get('tipo', 'dos_aguas') == 'dos_aguas':
            if t['eje'] == 'y':
                ax.plot([(a + c) / 2] * 2, [b, d], color='#e67e22', lw=1, ls='-.')
            else:
                ax.plot([a, c], [(b + d) / 2] * 2, color='#e67e22', lw=1, ls='-.')
    ax.set_aspect('equal'); ax.set_xlim(x0 - 0.5, x1 + 0.5); ax.set_ylim(y0 - 0.5, y1 + 0.5)
    ax.set_title('%s %s: muros, columnas, puertas (verde), ventanas (rojo), cumbrera (naranja)%s' % (m['cod'], m['nombre'], '; girada %.2f°' % -m['giro'] if m['giro'] else ''), fontsize=10)
    ax.tick_params(labelsize=7); fig.savefig(ruta, dpi=110, bbox_inches='tight'); plt.close(fig)


# ================================================================== principal
def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument('config'); ap.add_argument('--detecta', action='store_true')
    a = ap.parse_args()
    C = json.load(open(a.config, encoding='utf-8'))
    base = os.path.dirname(os.path.abspath(a.config))
    ruta = lambda f: f if os.path.isabs(f) else os.path.join(base, f)
    ctrl = ruta(C.get('carpeta_control', 'control')); os.makedirs(ctrl, exist_ok=True)
    pg = C['planta_general']
    P = leer(ruta(pg['archivo']), pg.get('ventana'))
    if a.detecta:
        return detecta(P, C, ctrl)
    if not C.get('edificaciones'):
        raise SystemExit('proyecto.json sin "edificaciones". Correr primero con --detecta y completar los datos.')
    ox, oy = C['origen']
    pg_lin = [(L, b, [(q[0] - ox, q[1] - oy) for q in p]) for L, b, p in P['lineas'] if p]
    # columnas achuradas: el contorno de la trama cuenta como líneas de la capa
    solidas = C['capas'].get('columna', []) + C['capas'].get('columneta', [])
    for L, b, an in P['tramas']:
        if en_capas(L, b, solidas):
            pg_lin.extend((L, b, [(x - ox, y - oy) for x, y in q] + [(q[0][0] - ox, q[0][1] - oy)]) for q in an)
    pg_arc = [(L, b, cx - ox, cy - oy, r_, a0, a1) for L, b, cx, cy, r_, a0, a1 in P['arcos']]

    cf = C.get('vanos', {})
    cu, dif_cuadros = {}, []
    q_ = cf.get('cuadro')
    if q_:
        if q_['archivo'].lower().endswith('.csv'):
            cu = cuadro_csv(ruta(q_['archivo']))
        else:
            cu = cuadro_dxf(leer(ruta(q_['archivo']))['tablas'], q_)
            if not cu:
                print('AVISO: no se halló un cuadro de vanos en tablas de AutoCAD: pasarlo a CSV.')
    plantas, tit = None, {}
    if cf.get('planta'):
        plantas = leer(ruta(cf['planta']['archivo']))
        rx = cf['planta']['titulo_regex']; fmt = cf['planta'].get('edificacion', 'E-%02d')
        for L, b, x, y, s in plantas['textos']:
            m = re.match(rx, s)
            if m and b is None:
                tit[fmt % int(m.group(1))] = (x, y)
        if q_ and cf.get('cotejar_cuadro_de_planta'):
            cu2 = cuadro_dxf(plantas['tablas'], q_)
            for cod in sorted(set(cu) | set(cu2)):
                for k in sorted(set(cu.get(cod, {})) | set(cu2.get(cod, {}))):
                    x_, y_ = cu2.get(cod, {}).get(k), cu.get(cod, {}).get(k)
                    if x_ is None or y_ is None or any(x_[c] != y_[c] for c in ('cant', 'ancho', 'alto', 'alf')):
                        dif_cuadros.append('%s %s: cuadro de detalle %s / cuadro de la planta %s' % (cod, k, y_ and (y_['cant'], y_['ancho'], y_['alto'], y_['alf']), x_ and (x_['cant'], x_['ancho'], x_['alto'], x_['alf'])))

    edif, avisos = [], []
    faltan = {e['cod']: [k for k in ROLES_NIVEL if e.get(k) is None] for e in C['edificaciones']}
    faltan = {k: v for k, v in faltan.items() if v}
    if faltan:
        raise SystemExit('Faltan niveles de los cortes (no se suponen): ' + '; '.join('%s: %s' % (k, ', '.join(v)) for k, v in faltan.items()))
    for e in C['edificaciones']:
        r = leer_edificacion(e, P, C, pg_lin, pg_arc, plantas, tit, cu)
        m = modelo(r, e)
        if m is None:
            avisos.extend(r['obs'] + ['%s: sin muros ni columnas: no se levanta' % r['cod']]); continue
        edif.append(m); avisos.extend(m['obs'])
        vista(m, os.path.join(ctrl, 'PLANTA_CONTROL_%s.png' % m['cod'].replace('/', '-')))
        if r['mezclada']:
            print('  OJO %s: capa de muros mezclada, ver AVISOS' % m['cod'])
        print('%s: giro %.2f°, muros %d, columnas %d, puertas %d (ind. %d), ventanas %d (ind. %d), cubiertas %d, cierres %d, cumbrera %s (rotulada %s)'
              % (m['cod'], -m['giro'], len(m['muros']), len(m['columnas']), len(m['puertas']), len(r['ind_p']), len(m['ventanas']), len(r['ind_v']),
                 len(m['techos']), len(m['cierres']), m['cumbreras_calculadas'], e.get('techo_rotulado')), flush=True)

    capas = C['capas']; lote = None
    zs = [e['zona'] for e in C['edificaciones']]
    margen = C.get('margen_lote', 60)
    cerca = box(min(z[0] for z in zs) - margen, min(z[1] for z in zs) - margen, max(z[2] for z in zs) + margen, max(z[3] for z in zs) + margen)
    if C.get('lote_puntos'):
        lote = Polygon(C['lote_puntos']).buffer(0)
    elif capas.get('lote'):
        lote, crit = lote_de_capas(pg_lin, capas['lote'], cerca)
        if lote is None:
            avisos.append('Lote: ninguna línea en las capas %s cerca de las edificaciones; indicar "lote_puntos"' % capas['lote'])
        else:
            print('lote: %.1f m2 (%s)' % (lote.area, crit))
            if crit.startswith('envolvente'):
                avisos.append('Lote: %s; contorno aproximado. Revisarlo o indicar "lote_puntos"' % crit)
    pisos = {}
    for nom, cps in C.get('pisos', {}).items():
        pol = []
        for L, b, an in P['tramas']:
            if en_capas(L, b, cps):
                g_ = poligono_de_anillos([[(x - ox, y - oy) for x, y in q] for q in an])
                if not g_.is_empty and g_.intersects(lote if lote is not None else cerca):
                    pol.append(g_)
        u = unary_union(pol).buffer(0) if pol else Polygon()
        if lote is not None and not u.is_empty:
            u = u.intersection(lote)                                    # lo que el achurado dibuja fuera del lote no es de la obra
        pisos[nom] = a_lista(u)
        print('piso %s: %.1f m2 en %d tramas' % (nom, u.area, len(pol)))
        if not pol:
            avisos.append('Piso "%s": ninguna trama en las capas %s' % (nom, cps))
    res = dict(proyecto=C.get('proyecto', ''), cui=C.get('cui', ''), origen=C['origen'], unidades='metros', diferencias_cuadros=dif_cuadros,
               lote=a_lista(lote) if lote is not None else [], pisos=pisos, edificios=edif)
    json.dump(res, open(ruta(C.get('salida', 'modelo.json')), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(ctrl, 'AVISOS.txt'), 'w', encoding='utf-8') as f:
        f.write('Por revisar antes de modelar (%s). %d avisos.\n\n' % (C.get('proyecto', ''), len(avisos) + len(dif_cuadros)))
        f.write('\n'.join(avisos + dif_cuadros) + '\n')
    print('\n%d avisos en %s' % (len(avisos) + len(dif_cuadros), os.path.join(ctrl, 'AVISOS.txt')))


if __name__ == '__main__':
    sys.exit(principal())
