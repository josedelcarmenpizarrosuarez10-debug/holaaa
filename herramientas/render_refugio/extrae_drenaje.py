# -*- coding: utf-8 -*-
"""Agrega a escena.json lo que faltaba de la planta general PG 01 de la arquitecta (Hogar de Refugio, CUI 2675514):
- cunetas: achurados de la capa 1-CUNETAS (bloque "red drenaje") (cuneta de 0.40 con rejilla, todas con rejilla segun el metrado: 510.11 m);
- oc01: los 3 juegos de jardinera + banca + pergola OC-01 (bloque GHDDDHFHD), con su rotacion;
- juegos: equipos del bloque OC-04 (columpios, tobogan, sube y baja) y su piso (achurado AR-SAND = arena);
- colector: registros del colector frontal (diseno del drenaje, entregables/_calc/diseno.json).
Coordenadas locales de la escena: E - 349090, N - 9281900 (mismo origen de la planta de drenaje).
Uso: python3.11 extrae_drenaje.py "<PG 01-PG 02 PLANTA GENERAL.dxf>" <diseno.json>"""
import json, os, sys
import ezdxf
from ezdxf import bbox

AQUI = os.path.dirname(os.path.abspath(__file__))
E0, N0 = 349090.0, 9281900.0
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
D = json.load(open(os.path.join(AQUI, 'escena.json')))


def caja(ents):
    b = bbox.extents(ents)
    return [b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y]


def local(r):
    if r[0] > 1e5 or r[1] > 1e6:                                                # el bloque OC-04 queda en UTM al explotarlo
        return [r[0] - E0, r[1] - N0, r[2] - E0, r[3] - N0]
    return r


def en_lote(r):
    return -5 < r[0] < 80 and 0 < r[1] < 140


# Las cunetas estan dentro del bloque "red drenaje" y los bloques del sitio ya se exploraron con su transformacion
# (hatches_pg.json y bloques_sitio.json, sacados de este mismo DXF en coordenadas de la escena).
H = json.load(open(os.path.join(AQUI, 'hatches_pg.json')))
B = json.load(open(os.path.join(AQUI, 'bloques_sitio.json')))
cun = []
for pol in H['1-CUNETAS']:
    xs = [q[0] for q in pol[0]]; ys = [q[1] for q in pol[0]]
    r = [min(xs), min(ys), max(xs), max(ys)]
    if en_lote(r):
        cun.append([round(v, 3) for v in r])
D['cunetas'] = cun
D['oc01'] = [dict(bb=e['bb'], rot=e['rot']) for e in B['GHDDDHFHD'] if en_lote(e['bb'])]
jg = []
for e in msp.query('INSERT[name=="OC-04"]'):
    r = local(caja([e]))
    if not en_lote(r):
        continue
    for v in e.virtual_entities():
        if v.dxftype() == 'INSERT':
            jg.append(dict(n=v.dxf.name, bb=[round(x, 3) for x in local(caja([v]))], rot=round(v.dxf.rotation, 2)))
        if v.dxftype() == 'HATCH':
            D['oc04_piso'] = v.dxf.pattern_name                   # AR-SAND
D['juegos'] = jg
dz = json.load(open(sys.argv[2]))
g = dz['geom']
D['colector'] = dict(y_eje=round(g['Y_EJE'] - N0, 3), y_cerco=round(g['Y_CERCO'] - N0, 3), x_ne=round(g['X_NE'] - E0, 3),
                     p_quiebre=round(g['P_B1'], 3), b=dz['datos']['b'], e_muro=dz['datos']['e_muro'],
                     registros=[dict(n=r['nombre'], p=r['prog']) for r in dz['registros'] if r['prog'] <= g['P_B1'] + 0.01])
json.dump(D, open(os.path.join(AQUI, 'escena.json'), 'w'), ensure_ascii=False)
print(len(cun), 'cunetas', len(D['oc01']), 'OC-01', len(jg), 'juegos', D.get('oc04_piso'), len(D['colector']['registros']), 'registros')

# ---------------------------------------------------------------- red de cunetas del plano de drenaje del usuario
# red_drenaje_usuario.json: bloque "red drenaje" del DXF "PLANTA GENERAL - MUJERES VIOLENTADAS" (02-11-2026) explotado en
# coordenadas locales (E - 349090, N - 9281900): achurados de cuneta, cadenas de flechas de sentido de flujo (*U), 17 tapas
# de inspeccion y 30 sumideros con rejilla. Los ejes 01 a 12 (insumos/solange/EJES_CUNETAS_REFUGIO.json) se ajustan a la
# posicion dibujada (centro de la cadena de flechas) cuando difieren menos de 0.15 m.
RAIZ = os.environ.get('RAIZ_REPO', '/home/user/holaaa')
R = json.load(open(os.path.join(AQUI, 'red_drenaje_usuario.json')))
EJ = json.load(open(os.path.join(RAIZ, 'insumos/solange/EJES_CUNETAS_REFUGIO.json')))
ver, hor = [], []
for u in R['u']:
    x0, y0, x1, y1 = u['bb']
    (ver if (y1 - y0) > (x1 - x0) else hor).append(((x0 + x1) / 2 if (y1 - y0) > (x1 - x0) else (y0 + y1) / 2, u['bb']))


def ajusta(v, lista, lo, hi, idx):
    for c, bb in lista:
        if abs(c - v) < 0.15 and bb[idx] - 0.5 < hi and bb[idx + 2] + 0.5 > lo:
            return round(c, 3)
    return v


ejes = {}
for k, pts in EJ.items():
    P = [[x - E0, y - N0] for x, y in pts]
    for i in range(len(P) - 1):
        (xa, ya), (xb, yb) = P[i], P[i + 1]
        if abs(xa - xb) < 1e-6:                                   # tramo vertical
            c = ajusta(xa, ver, min(ya, yb), max(ya, yb), 1); P[i][0] = P[i + 1][0] = c
        elif abs(ya - yb) < 1e-6:
            c = ajusta(ya, hor, min(xa, xb), max(xa, xb), 0); P[i][1] = P[i + 1][1] = c
    ejes[k] = P
D['ejes_cuneta'] = ejes
D['tapas_inspeccion'] = [t['bb'] for t in R['tapas']]
D['sumideros'] = R['sumideros']
D['cunetas_frente'] = [r for r in D['cunetas'] if r[3] < 19.0]
json.dump(D, open(os.path.join(AQUI, 'escena.json'), 'w'), ensure_ascii=False)
print('ejes', {k: len(v) for k, v in ejes.items()}, len(D['tapas_inspeccion']), 'tapas', len(D['sumideros']), 'sumideros')
