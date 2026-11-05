# -*- coding: utf-8 -*-
"""Levanta en Blender el modelo.json de lee_planos.py: edificaciones con sus muros, vanos, vigas, columnas, cubiertas y cierres,
y el terreno con piso recortado, áreas verdes, cerco y árboles que no tocan nada.
Los colores salen de acabados.json (ver acabados_plantilla.json), con el cuadro de acabados de la arquitecta: el que falta se pregunta.

Uso directo:
    blender -b --factory-startup --python levanta_modelo.py -- modelo.json acabados.json modelo.blend
Lo que el lector no cubre (pórtico, tanque, bancas, juegos, instalaciones...) se agrega lámina por lámina en un generador propio:
    import levanta_modelo as L
    ctx = L.levantar(json.load(open('modelo.json')), json.load(open('acabados.json')))
    B.caja('tanque', ..., L.material('muro'), ctx['colecciones']['exteriores'])
    L.terminar(ctx, 'modelo.blend')
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_escena as B  # noqa: E402
from shapely.affinity import rotate  # noqa: E402
from shapely.geometry import Polygon, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

OBLIGATORIOS = ('muro', 'columna', 'viga', 'cobertura')
_ROLES = {}


def materiales(ac):
    faltan = [k for k in OBLIGATORIOS if k not in ac]
    if faltan:
        raise SystemExit('Faltan en acabados.json: %s. Tomarlos del cuadro de acabados o preguntarlos; no se suponen.' % ', '.join(faltan))
    # lo que el cuadro no pide en color propio toma uno ya dado o un neutro, y se avisa
    neutros = dict(piso=dict(nombre='concreto_piso', tipo='concreto', rgb=[186, 182, 174]), vereda=dict(nombre='concreto_vereda', tipo='concreto', rgb=[186, 182, 174]),
                   puerta=dict(nombre='puerta', tipo='simple', rgb=[110, 78, 50], rug=0.6), marco=dict(nombre='marco', tipo='simple', rgb=[180, 182, 185], rug=0.35, metal=0.8),
                   vidrio=dict(nombre='vidrio', tipo='vidrio'), pasto=dict(nombre='pasto', tipo='pasto'), terreno=dict(nombre='terreno', tipo='pasto'))
    d = dict(neutros); d.update(ac)
    usados = [k for k in neutros if k not in ac]
    if usados:
        print('Sin dato en acabados.json, con color neutro (confirmar): %s' % ', '.join(usados), flush=True)
    d.setdefault('cierre', d['muro'])
    d.setdefault('losa', d['piso'])
    _ROLES.clear()
    for rol, q in d.items():
        if not isinstance(q, dict) or rol in ('cerco', 'arboles', 'cielo') and 'rgb' not in q:
            continue
        if rol == 'cobertura':
            for eje_, onda in (('y', 'Y'), ('x', 'X')):                # ondas a lo largo de la caída: cada sentido tiene su material
                nom = '%s_%s' % (q.get('nombre', 'cobertura'), eje_)
                if q.get('tipo', 'calamina') == 'calamina':
                    B.mat_calamina(nom, B.rgb(*q['rgb']), onda)
                else:
                    B.mat_pintura(nom, B.rgb(*q['rgb']))
                _ROLES['cobertura_' + eje_] = nom
            continue
        nom = q.get('nombre', rol); ti = q.get('tipo', 'pintura')
        if nom not in B.MATS:
            if ti == 'pintura':
                B.mat_pintura(nom, B.rgb(*q['rgb']))
            elif ti == 'concreto':
                B.mat_concreto(nom, tuple(q['rgb']), juntas=q.get('juntas'))
            elif ti == 'vidrio':
                B.mat_vidrio(nom, tuple(q.get('rgb', (35, 52, 62))))
            elif ti == 'pasto':
                B.mat_pasto(nom, q.get('imagen'))
            else:
                B.mat_simple(nom, B.rgb(*q['rgb']), rug=q.get('rug', 0.6), metal=q.get('metal', 0.0))
        _ROLES[rol] = nom
    return d


def material(rol):
    return B.MATS[_ROLES[rol]]


def _anfitrion(muros, v):
    mejor = None
    for i, w in enumerate(muros):
        h = abs(w[1] - w[3]) < 1e-6
        if (v['o'] == 'H') != h:
            continue
        d, c, a, b = (abs(w[1] - v['y']), v['x'], min(w[0], w[2]), max(w[0], w[2])) if h else (abs(w[0] - v['x']), v['y'], min(w[1], w[3]), max(w[1], w[3]))
        if d < 0.06 and a - 0.01 <= c - v['ancho'] / 2 and c + v['ancho'] / 2 <= b + 0.01 and (mejor is None or d < mejor[0]):
            mejor = (d, i)
    return None if mejor is None else mejor[1]


def _restar(iv, a, b):
    out = []
    for z0, z1 in iv:
        if b <= z0 or a >= z1:
            out.append((z0, z1)); continue
        if a > z0:
            out.append((z0, a))
        if b < z1:
            out.append((b, z1))
    return out


def _cubierta(t, cod, col, n):
    """Malla de una cubierta; 0.05 m sobre su cara inferior, con espesor."""
    x0, y0, x1, y1 = t['rect']; b = t['base']; e_ = 0.05; ti = t.get('tipo', 'dos_aguas'); p = t.get('pend', 0.0)
    if ti == 'plana':
        return B.caja('%s_losa_%d' % (cod, n), x0, y0, b, x1, y1, b + 0.15, material('losa'), col)
    if ti == 'un_agua':
        al = t.get('alto', 'x1')
        z = lambda x, y: b + e_ + p * {'x0': x1 - x, 'x1': x - x0, 'y0': y1 - y, 'y1': y - y0}[al]
        v = [(q[0], q[1], z(*q)) for q in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        o = B.obj_mesh('%s_techo_%d' % (cod, n), v, [(0, 1, 2, 3)], material('cobertura_y' if al[0] == 'x' else 'cobertura_x'), col)
    elif ti == 'cuatro_aguas':
        w, l = x1 - x0, y1 - y0; zr = b + e_ + p * min(w, l) / 2
        if l >= w:
            xm = (x0 + x1) / 2; a_, c_ = (xm, y0 + w / 2, zr), (xm, y1 - w / 2, zr)
            v = [(x0, y0, b + e_), (x1, y0, b + e_), (x1, y1, b + e_), (x0, y1, b + e_), a_, c_]
            f = [(0, 1, 4), (1, 2, 5, 4), (2, 3, 5), (3, 0, 4, 5)]
        else:
            ym = (y0 + y1) / 2; a_, c_ = (x0 + l / 2, ym, zr), (x1 - l / 2, ym, zr)
            v = [(x0, y0, b + e_), (x1, y0, b + e_), (x1, y1, b + e_), (x0, y1, b + e_), a_, c_]
            f = [(0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)]
        o = B.obj_mesh('%s_techo_%d' % (cod, n), v, f, material('cobertura_y' if l >= w else 'cobertura_x'), col)
    elif t.get('eje') == 'y':
        xm = (x0 + x1) / 2; zr = b + p * (xm - x0) + e_
        v = [(x0, y0, b + e_), (xm, y0, zr), (xm, y1, zr), (x0, y1, b + e_), (x1, y0, b + e_), (x1, y1, b + e_)]
        o = B.obj_mesh('%s_techo_%d' % (cod, n), v, [(0, 1, 2, 3), (1, 4, 5, 2)], material('cobertura_y'), col)
    else:
        ym = (y0 + y1) / 2; zr = b + p * (ym - y0) + e_
        v = [(x0, y0, b + e_), (x1, y0, b + e_), (x1, ym, zr), (x0, ym, zr), (x1, y1, b + e_), (x0, y1, b + e_)]
        o = B.obj_mesh('%s_techo_%d' % (cod, n), v, [(0, 1, 2, 3), (3, 2, 4, 5)], material('cobertura_x'), col)
    m = o.modifiers.new('espesor', 'SOLIDIFY'); m.thickness = e_
    return o


def edificio(m, padre):
    cod = m['cod']; col = B.coleccion(cod, padre); M = B.Malla(cod, col); npt = m['npt']; R = _ROLES
    wx0, wy0, wx1, wy1 = m['contorno_muros']; cxm, cym = (wx0 + wx1) / 2, (wy0 + wy1) / 2
    ve = m.get('vereda') or 0
    M.caja(R['vereda'] if ve else R['piso'], wx0 - ve, wy0 - ve, 0, wx1 + ve, wy1 + ve, npt)
    vanos = {}
    for tipo, lst in (('p', m['puertas']), ('v', m['ventanas'])):
        for v in lst:
            i = _anfitrion(m['muros'], v)
            if i is not None:
                vanos.setdefault(i, []).append((tipo, v))
    for i, (x0, y0, x1, y1, esp, z0, z1, ext) in enumerate(m['muros']):
        fondo = m['vigas'][i][5]; h = abs(y0 - y1) < 1e-6
        c = y0 if h else x0; s0, s1 = sorted((x0, x1)) if h else sorted((y0, y1))
        sal = 1 if c > (cym if h else cxm) else -1
        P = (lambda a, b, t0, t1, za, zb, mat: M.caja(mat, a, c + t0, za, b, c + t1, zb)) if h else (lambda a, b, t0, t1, za, zb, mat: M.caja(mat, c + t0, a, za, c + t1, b, zb))
        hue = []
        for tipo, v in vanos.get(i, []):
            s = v['x'] if h else v['y']; a, b = s - v['ancho'] / 2, s + v['ancho'] / 2
            zt = min(v['sill'] + v['alto'], fondo)
            if tipo == 'p':
                ztop = fondo if (v.get('sobreluz') and fondo - zt > 0.2) else zt
                hue.append((a, b, z0, ztop))
                P(a, b, -0.02, 0.02, z0, zt, R['vidrio'] if v.get('vidrio') else R['puerta'])
                for (aa, bb, za, zb) in ((a, a + 0.05, z0, zt), (b - 0.05, b, z0, zt), (a, b, zt - 0.05, zt)):
                    P(aa, bb, -esp / 2, esp / 2, za, zb, R['marco'])
                if v.get('vidrio'):
                    P(s - 0.02, s + 0.02, -0.03, 0.03, z0, zt, R['marco'])
                if ztop > zt:
                    P(a, b, -0.01, 0.01, zt, ztop, R['vidrio']); P(a, b, -0.03, 0.03, ztop - 0.04, ztop, R['marco'])
            else:
                zs = v['sill']; hue.append((a, b, zs, zt))
                P(a, b, -0.01, 0.01, zs, zt, R['vidrio'])
                for (aa, bb, za, zb) in ((a, a + 0.05, zs, zt), (b - 0.05, b, zs, zt), (a, b, zs, zs + 0.05), (a, b, zt - 0.05, zt)):
                    P(aa, bb, -0.035, 0.035, za, zb, R['marco'])
                n_ = max(1, int(round(v['ancho'] / 1.0)))
                for k in range(1, n_):
                    sk = a + (b - a) * k / n_; P(sk - 0.025, sk + 0.025, -0.035, 0.035, zs, zt, R['marco'])
                if ext:
                    t0, t1 = (esp / 2, esp / 2 + 0.05) if sal > 0 else (-esp / 2 - 0.05, -esp / 2)
                    P(a - 0.03, b + 0.03, t0, t1, zs - 0.05, zs, R['marco'])
        cortes = sorted({s0, s1} | {q for hh in hue for q in hh[:2] if s0 < q < s1})
        for a, b in zip(cortes, cortes[1:]):                            # muro en franjas verticales, sin los vanos
            llenos = [(z0, fondo)]
            for (ha, hb, za, zb) in hue:
                if ha <= a + 1e-6 and b <= hb + 1e-6:
                    llenos = _restar(llenos, za, zb)
            for za, zb in llenos:
                P(a, b, -esp / 2, esp / 2, za, zb, R['muro'])
    for (x0, y0, x1, y1, w_, z0, z1) in m['vigas']:
        if abs(y0 - y1) < 1e-6:
            M.caja(R['viga'], min(x0, x1), y0 - w_ / 2, z0, max(x0, x1), y0 + w_ / 2, z1)
        else:
            M.caja(R['viga'], x0 - w_ / 2, min(y0, y1), z0, x0 + w_ / 2, max(y0, y1), z1)
    for (x, y, b_, h_, z0, z1) in m['columnas']:
        M.caja(R['columna'], x - b_ / 2 - 0.01, y - h_ / 2 - 0.01, z0, x + b_ / 2 + 0.01, y + h_ / 2 + 0.01, z1)
    if m.get('alto_muro_bajo'):
        for (x0, y0, x1, y1, e_) in m.get('muros_bajos', []):
            if abs(y0 - y1) < 1e-6:
                M.caja(R['muro'], min(x0, x1), y0 - e_ / 2, npt, max(x0, x1), y0 + e_ / 2, npt + m['alto_muro_bajo'])
            else:
                M.caja(R['muro'], x0 - e_ / 2, min(y0, y1), npt, x0 + e_ / 2, max(y0, y1), npt + m['alto_muro_bajo'])
    elif m.get('muros_bajos'):
        print('%s: %d muros bajos sin "alto_muro_bajo": no se levantan' % (cod, len(m['muros_bajos'])), flush=True)
    for c_ in m['cierres']:
        M.placa(R['cierre'], c_['pol'], c_['esp'])
    objs = M.crear() + [_cubierta(t, cod, col, n) for n, t in enumerate(m['techos'])]
    g = m.get('giro') or 0
    for o in objs:                                                      # el lector trabaja en el marco de la edificación
        o.rotation_euler = (0, 0, math.radians(-g))
    return objs


def huella(m):
    """Contorno en planta de la cubierta y de los muros, en coordenadas del lote."""
    g = box(*m['contorno_muros']).buffer(m.get('vereda') or 0, join_style=2)
    t = unary_union([box(*q['rect']) for q in m['techos']] + [g])
    return rotate(g, -(m.get('giro') or 0), origin=(0, 0)), rotate(t, -(m.get('giro') or 0), origin=(0, 0))


def _poligonos(lista):
    return unary_union([Polygon(e, h).buffer(0) for e, h in lista]) if lista else Polygon()


def levantar(mo, ac):
    B.nueva_escena()
    d = materiales(ac)
    CE, CT, CX, CA = B.coleccion('Edificaciones'), B.coleccion('Terreno'), B.coleccion('Exteriores'), B.coleccion('Arboles')
    for m in mo['edificios']:
        edificio(m, CE)
    huellas = [huella(m) for m in mo['edificios']]
    lote = _poligonos(mo.get('lote', []))
    verdes = {k: _poligonos(v) for k, v in mo.get('pisos', {}).items()}
    todo = lote if not lote.is_empty else unary_union([t for _, t in huellas]).buffer(15)
    x0, y0, x1, y1 = todo.bounds
    B.caja('terreno', x0 - 300, y0 - 300, -0.2, x1 + 300, y1 + 300, 0, material('terreno'), CT)
    huecos = [g for g, _ in huellas] + [g for g in verdes.values() if not g.is_empty]
    if not lote.is_empty:
        B.piso_exacto('piso_lote', lote, huecos, 0.08, material('piso'), CT)
    else:
        print('Sin lote: el piso no se arma. Indicar la capa o "lote_puntos" en proyecto.json', flush=True)
    for nom, g in verdes.items():
        if g.is_empty:
            continue
        mat = material(nom) if nom in _ROLES else material('pasto')
        B.prisma('piso_' + nom, g, 0, 0.05, mat, CT)
    obst = [t for _, t in huellas]
    cf = d.get('cerco')
    if cf and not lote.is_empty:
        franja = lote.exterior.buffer(cf['espesor'] / 2, cap_style=2, join_style=2)
        B.prisma('cerco', franja, 0, cf['altura'], material('cerco'), CX)
        obst.append(franja)
    pos = ac.get('arboles') or []
    res = dict(plantados=[], descartados=[])
    if pos:
        protos = B.prototipos_arbol(B.coleccion('Prototipos (fuera del terreno)'))
        res['plantados'], res['descartados'] = B.plantar_arboles([tuple(q) for q in pos], protos, unary_union(obst), CA)
        print('árboles plantados %d, descartados %d %s' % (len(res['plantados']), len(res['descartados']), res['descartados']), flush=True)
    B.mundo(); B.ajustes_render()
    return dict(colecciones=dict(edificaciones=CE, terreno=CT, exteriores=CX, arboles=CA), obstaculos=unary_union(obst), arboles=res, lote=lote)


def terminar(ctx, ruta):
    B.guardar(ruta)
    print('guardado', ruta, flush=True)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    ctx = levantar(json.load(open(a[0], encoding='utf-8')), json.load(open(a[1], encoding='utf-8')))
    terminar(ctx, a[2])
