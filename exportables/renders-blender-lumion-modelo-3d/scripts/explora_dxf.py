# -*- coding: utf-8 -*-
"""Primer paso con un DXF desconocido: lista capas, bloques con atributos, tramas, tablas y contornos grandes, y propone
qué capa es cada cosa según su nombre y su geometría. No modifica nada. Las propuestas se confirman antes de leer.
Uso: python explora_dxf.py plano.dxf [--ventana x0 y0 x1 y1] [--plantilla salida.json]
--ventana: solo los bloques insertados en esa zona (si el archivo trae varias copias de la planta)
--plantilla: escribe un proyecto.json a completar con las capas propuestas"""
import argparse
import collections
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lee_planos import aristas, eje, leer, muros_de_caras, poligono_de_anillos, union_intervalos  # noqa: E402

PALABRAS = {
    'muro': r'MURO|WALL|TABIQUE|ALBA[NÑ]', 'muro_bajo': r'MUROS? BAJO|PARAPETO', 'columna': r'COLUMNAS?\b|\bCOLUMNS?\b', 'columneta': r'COLUMNETA',
    'vano': r'VANO|VIDRIO|VENTANA|WINDOW|GLASS', 'techo': r'PROYECC|TECHO|COBERT|CUBIERTA|CUMBRER|ROOF', 'lote': r'CERCO|LINDERO|PERIMETR|L[IÍ]MITE|TERRENO|LOTE',
    'verde': r'PASTO|HIER[BV]A|GRASS|VERDE|JARD[IÍ]N|GRASS', 'arena': r'SAND|ARENA|GRAVA',
}
EXCLUIR_MURO = r'BAJO|EJE|COTA|TEXT|ACHUR|HATCH|MOBIL|CUNETA|RUTA'


def origen_sugerido(xs, ys):
    """Redondo y cercano a la mediana, para que las copias lejanas no lo desplacen."""
    return [math.floor(xs[len(xs) // 2] / 100) * 100, math.floor(ys[len(ys) // 2] / 100) * 100]


def resumen(P):
    cap = collections.defaultdict(lambda: dict(n=0, L=0.0, orto=0.0, cerrados=0))
    for L, b, p in P['lineas']:
        c = cap[L]; c['n'] += 1
        for a_, b_ in aristas(p):
            d = math.hypot(b_[0] - a_[0], b_[1] - a_[1]); c['L'] += d
            if eje(a_, b_):
                c['orto'] += d
        if len(p) > 3 and math.hypot(p[0][0] - p[-1][0], p[0][1] - p[-1][1]) < 0.01:
            c['cerrados'] += 1
    return cap


def pares(segs, e=(0.07, 0.42)):
    """Parte de las caras que forma pares a distancia de muro: lo que distingue una capa de muros reales."""
    if len(segs) > 40000:
        segs = segs[:40000]
    L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs if eje(a, b))
    if L < 1:
        return 0.0, {}
    tr = muros_de_caras(segs, e[0], e[1])
    esp = collections.Counter()
    for m in tr:
        esp[m['e']] += m['t1'] - m['t0']
    return min(1.0, 2 * sum(m['t1'] - m['t0'] for m in tr) / L), esp


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument('dxf'); ap.add_argument('--ventana', nargs=4, type=float); ap.add_argument('--plantilla')
    a = ap.parse_args()
    P = leer(a.dxf, a.ventana)
    print('Entidades del espacio modelo:', ', '.join('%s %d' % kv for kv in sorted(P['cuentas'].items(), key=lambda kv: -kv[1])[:10]))
    xs = sorted(q[0] for L, b, p in P['lineas'] for q in p[:1]); ys = sorted(q[1] for L, b, p in P['lineas'] for q in p[:1])
    if xs:
        n = len(xs)
        print('Extensión (percentiles 1-99): E %.1f a %.1f, N %.1f a %.1f (m)' % (xs[n // 100], xs[-n // 100 - 1], ys[n // 100], ys[-n // 100 - 1]))
        print('Origen local sugerido, redondo: %s (el archivo puede traer copias: confirmar con la zona de la planta)' % origen_sugerido(xs, ys))
    cap = resumen(P)
    print('\nCapas con más líneas (n, longitud m, % ortogonal, contornos cerrados):')
    for k, c in sorted(cap.items(), key=lambda kv: -kv[1]['L'])[:45]:
        print('  %-38s %7d %10.0f %4.0f%% %6d' % (k[:38], c['n'], c['L'], 100 * c['orto'] / max(c['L'], 1), c['cerrados']))

    capas_t = collections.Counter()
    area_t = collections.Counter()
    for L, b, an in P['tramas']:
        capas_t[L] += 1
        try:
            area_t[L] += poligono_de_anillos(an).area
        except Exception:
            pass
    if capas_t:
        print('\nTramas por capa (cantidad, área m2):')
        for k, n in capas_t.most_common(30):
            print('  %-38s %6d %10.1f' % (k[:38], n, area_t[k]))

    bl = collections.defaultdict(lambda: [0, set()])
    for n, x, y, at, b in P['inds']:
        bl[n][0] += 1; bl[n][1] |= set(at)
    if bl:
        print('\nBloques con atributos (posibles indicadores de puertas y ventanas):')
        for k, v in sorted(bl.items(), key=lambda kv: -kv[1][0])[:25]:
            ej = next((at for n, x, y, at, b in P['inds'] if n == k), {})
            print('  %-34s %5d  %s' % (k[:34], v[0], ', '.join('%s=%s' % kv for kv in list(ej.items())[:5])))
    print('\nTablas de AutoCAD: %d%s' % (len(P['tablas']), '' if P['tablas'] else '  (si hay cuadro de vanos dibujado con líneas, pasarlo a CSV)'))
    for x, y, c in P['tablas'][:6]:
        print('  ', ' | '.join(s for _, _, s in c[:9])[:130])
    tv = [s for L, b, x, y, s in P['textos'] if re.match(r'^[PV]-?\s?\d+[A-Z]?$', s.strip().upper())]
    if tv:
        print('\nTextos con forma de código de vano: %d. Ejemplos: %s' % (len(tv), ', '.join(sorted(set(tv))[:15])))
    ti = [s for L, b, x, y, s in P['textos'] if b is None and re.match(r'^(PLANTA|CORTE|ELEVACI)', s.strip().upper())]
    if ti:
        print('\nTítulos de láminas: %d. Ejemplos: %s' % (len(ti), ' / '.join(sorted(set(ti))[:8])[:300]))

    # propuestas
    prop = collections.defaultdict(list)
    for k, c in cap.items():
        K = k.upper()
        for rol, rx in PALABRAS.items():
            if rol not in ('verde', 'arena') and re.search(rx, K) and c['L'] > 1:
                if rol == 'muro' and re.search(EXCLUIR_MURO, K):
                    continue
                if rol == 'columna' and re.search(r'CERCO|PERIM|ACHUR', K):
                    continue
                if rol == 'lote' and re.search(r'COLUMN', K):
                    continue
                prop[rol].append(k)
    for k in capas_t:
        for rol in ('verde', 'arena'):
            if re.search(PALABRAS[rol], k.upper()):
                prop[rol].append(k)
    segs_de = collections.defaultdict(list)
    for L, b, p in P['lineas']:
        if L in prop['muro'] or cap[L]['orto'] > 50:
            segs_de[L].extend(aristas(p))
    print('\nCapas que forman pares a distancia de muro (0.07 a 0.42 m):')
    cand = []
    for k, sg in sorted(segs_de.items(), key=lambda kv: -cap[kv[0]]['orto'])[:14]:
        f, esp = pares(sg)
        if f >= 0.25:
            cand.append(k)
            print('  %-38s %3.0f%% espesores: %s' % (k[:38], 100 * f, ', '.join('%.2f' % e_ for e_, _ in esp.most_common(4))))
    prop['muro_por_geometria'] = cand
    # módulos como bloques con los muros en una capa genérica: se piden como 'BLOQUE|CAPA'
    por_bloque = collections.defaultdict(list)
    for L, b, p in P['lineas']:
        if b is not None and not re.search(PALABRAS['muro'], L.upper()):
            por_bloque[(b, L)].extend(aristas(p))
    en_bloque = []
    for (b, L), sg in por_bloque.items():
        if sum(math.hypot(q[0] - a_[0], q[1] - a_[1]) for a_, q in sg if eje(a_, q)) < 30 or not re.fullmatch(r'0|DEFPOINTS|.{0,2}', L.upper()):
            continue
        f, esp = pares(sg)
        if f >= 0.7:
            en_bloque.append('%s|%s' % (b, L))
            print('  %-38s %3.0f%% espesores: %s  (bloque|capa)' % (('%s|%s' % (b, L))[:38], 100 * f, ', '.join('%.2f' % e_ for e_, _ in esp.most_common(4))))
    prop['muro_en_bloque'] = sorted(en_bloque)
    print('\nPROPUESTA (confirmar con el usuario o en una planta de control):')
    for rol in ('muro', 'muro_por_geometria', 'muro_en_bloque', 'muro_bajo', 'columna', 'columneta', 'vano', 'techo', 'lote', 'verde', 'arena'):
        print('  %-20s %s' % (rol, sorted(set(prop[rol]))))
    if a.plantilla:
        muros_ = sorted(set(prop['muro']) & set(cand)) or sorted(set(prop['muro']))
        pl = dict(proyecto='', cui='', origen=origen_sugerido(xs, ys) if xs else None,
                  planta_general=dict(archivo=os.path.abspath(a.dxf), ventana=a.ventana),
                  capas=dict(muro=muros_, muro_bajo=sorted(set(prop['muro_bajo'])), columna=sorted(set(prop['columna'])), columneta=sorted(set(prop['columneta'])),
                             vano=sorted(set(prop['vano'])), techo=sorted(set(prop['techo'])), lote=sorted(set(prop['lote']))),
                  pisos=dict(verde=sorted(set(prop['verde'])), arena=sorted(set(prop['arena']))),
                  espesor_muro=[0.07, 0.42], vanos={}, edificaciones=[])
        json.dump(pl, open(a.plantilla, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\nPlantilla escrita en', a.plantilla)


if __name__ == '__main__':
    principal()
