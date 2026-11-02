# -*- coding: utf-8 -*-
"""Explota el bloque "red drenaje" del plano de drenaje pluvial del usuario (PLANTA GENERAL - MUJERES VIOLENTADAS.dxf,
Hogar de Refugio Temporal, CUI 2675514) y guarda en coordenadas locales de la escena (E - 349090, N - 9281900):
achurados de cuneta, lineas y polilineas de la capa 0_ CUNETAS, cadenas de flechas de sentido de flujo (*U), tapas de
inspeccion (bloque TAPA INSPECCION), textos y los sumideros con rejilla (bloque SUMIIIDERR) de la planta.
Uso: python3.11 -I extrae_red_usuario.py "<PLANTA GENERAL - MUJERES VIOLENTADAS.dxf>" red_drenaje_usuario.json"""
import collections, json, sys
import ezdxf
from ezdxf import bbox, path

E0, N0 = 349090.0, 9281900.0
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()


def L(p):
    return [round(p[0] - E0, 3), round(p[1] - N0, 3)]


red = [e for e in msp.query('INSERT[name=="red drenaje"]') if e.dxf.insert.y > 9281900][0]   # copia de la planta general
out = dict(hatch=[], lineas=[], polis=[], u=[], tapas=[], textos=[])
for v in red.virtual_entities():
    t = v.dxftype()
    if t == 'HATCH':
        rings = [[L(q) for q in path.from_hatch_boundary_path(bp).flattening(0.01)] for bp in v.paths]
        out['hatch'].append(dict(layer=v.dxf.layer, color=v.dxf.color, pattern=v.dxf.pattern_name, rings=rings))
    elif t == 'LINE' and v.dxf.layer == '0_ CUNETAS':
        out['lineas'].append([L(v.dxf.start), L(v.dxf.end), v.dxf.color])
    elif t in ('LWPOLYLINE', 'POLYLINE') and v.dxf.layer == '0_ CUNETAS':
        out['polis'].append(dict(pts=[L(q) for q in path.make_path(v).flattening(0.01)], color=v.dxf.color))
    elif t == 'INSERT':
        bb = bbox.extents([v])
        d = dict(n=v.dxf.name, p=L(v.dxf.insert), rot=v.dxf.rotation, bb=L(bb.extmin) + L(bb.extmax))
        if v.dxf.name.startswith('*U'):                              # cadena de flechas de sentido de flujo
            d['tipos'] = collections.Counter(x.dxftype() for x in v.virtual_entities()).most_common()
            out['u'].append(d)
        else:
            out['tapas'].append(d)
    elif t == 'TEXT':
        out['textos'].append([v.dxf.text, L(v.dxf.insert)])
out['sumideros'] = []
for e in msp.query('INSERT[name=="SUMIIIDERR"]'):
    bb = bbox.extents([e])
    if 9281900 < bb.extmin.y < 9282040:
        out['sumideros'].append(L(bb.extmin) + L(bb.extmax))
json.dump(out, open(sys.argv[2], 'w'))
print({k: len(v) for k, v in out.items()})
