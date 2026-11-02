# -*- coding: utf-8 -*-
"""Modelo 3D del Hogar de Refugio Temporal (CUI 2675514) en Blender, a partir de la planta general y las elevaciones de la
arquitecta (escena.json). Colores de muros: TP-1 RGB 123-31-45, TP-2 RGB 125-133-139, TP-3 RAL 9010."""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector, Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(AQUI, 'escena.json')))
A = os.path.join(AQUI, 'assets')
random.seed(7)


def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(r, g, b, a=1.0):
    return (lin(r), lin(g), lin(b), a)


TP1, TP2, TP3 = rgb(123, 31, 45), rgb(125, 133, 139), rgb(241, 236, 225)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ------------------------------------------------------------------ materiales
MATS = {}


def nodos(m):
    m.use_nodes = True
    nt = m.node_tree
    return nt, nt.nodes, nt.links, nt.nodes['Principled BSDF']


def biselar(N, Lk, p, altura=None, fuerza=0.1, dist=0.01, radio=0.012):
    """Canto biselado (luz en las aristas) + relieve fino, hacia la normal del material."""
    bv = N.new('ShaderNodeBevel'); bv.samples = 2; bv.inputs['Radius'].default_value = radio
    if altura is None:
        Lk.new(bv.outputs['Normal'], p.inputs['Normal']); return
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = fuerza; bm.inputs['Distance'].default_value = dist
    Lk.new(altura, bm.inputs['Height']); Lk.new(bv.outputs['Normal'], bm.inputs['Normal']); Lk.new(bm.outputs['Normal'], p.inputs['Normal'])


def mat_pintura(nombre, color, rug=0.85, rugosidad_bump=0.12):
    """Pintura sobre tarrajeo: grano fino, variación de tono, suciedad al pie del muro y en rincones, canto biselado."""
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    tc = N.new('ShaderNodeTexCoord'); geo = N.new('ShaderNodeNewGeometry')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 90; nz.inputs['Detail'].default_value = 12
    Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    nz2 = N.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 0.9; nz2.inputs['Detail'].default_value = 4
    Lk.new(tc.outputs['Object'], nz2.inputs['Vector'])
    c1 = N.new('ShaderNodeMix'); c1.data_type = 'RGBA'
    c1.inputs[6].default_value = color; c1.inputs[7].default_value = tuple(c * 0.9 for c in color[:3]) + (1,)
    Lk.new(nz2.outputs['Fac'], c1.inputs[0])
    # suciedad: al pie (z < 0.7 m) y con manchas
    sep = N.new('ShaderNodeSeparateXYZ'); Lk.new(geo.outputs['Position'], sep.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.1; mr.inputs['From Max'].default_value = 0.9
    mr.inputs['To Min'].default_value = 0.55; mr.inputs['To Max'].default_value = 0.0
    Lk.new(sep.outputs['Z'], mr.inputs['Value'])
    nz3 = N.new('ShaderNodeTexNoise'); nz3.inputs['Scale'].default_value = 6; nz3.inputs['Detail'].default_value = 8
    Lk.new(tc.outputs['Object'], nz3.inputs['Vector'])
    mm = N.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; Lk.new(mr.outputs['Result'], mm.inputs[0]); Lk.new(nz3.outputs['Fac'], mm.inputs[1])
    sm = N.new('ShaderNodeMath'); sm.operation = 'ADD'; sm.use_clamp = True; Lk.new(mm.outputs[0], sm.inputs[0]); sm.inputs[1].default_value = 0.0
    c2 = N.new('ShaderNodeMix'); c2.data_type = 'RGBA'; Lk.new(sm.outputs[0], c2.inputs[0])
    Lk.new(c1.outputs[2], c2.inputs[6]); c2.inputs[7].default_value = rgb(78, 70, 60)
    Lk.new(c2.outputs[2], p.inputs['Base Color'])
    rr = N.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = rug - 0.08; rr.inputs['To Max'].default_value = min(rug + 0.08, 1)
    Lk.new(nz2.outputs['Fac'], rr.inputs['Value']); Lk.new(rr.outputs['Result'], p.inputs['Roughness'])
    biselar(N, Lk, p, nz.outputs['Fac'], fuerza=rugosidad_bump, dist=0.004)
    MATS[nombre] = m
    return m


def mat_simple(nombre, color, rug=0.5, metal=0.0, emis=None):
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    p.inputs['Base Color'].default_value = color; p.inputs['Roughness'].default_value = rug; p.inputs['Metallic'].default_value = metal
    if emis:
        p.inputs['Emission Color'].default_value = emis; p.inputs['Emission Strength'].default_value = 3
    MATS[nombre] = m
    return m


def mat_calamina(nombre, direccion):
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    p.inputs['Base Color'].default_value = rgb(196, 200, 204); p.inputs['Metallic'].default_value = 0.85
    p.inputs['Roughness'].default_value = 0.32
    tc = N.new('ShaderNodeTexCoord'); w = N.new('ShaderNodeTexWave'); w.wave_type = 'BANDS'; w.bands_direction = direccion
    w.wave_profile = 'SIN'; w.inputs['Scale'].default_value = 2.2
    Lk.new(tc.outputs['Object'], w.inputs['Vector'])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.55; bm.inputs['Distance'].default_value = 0.03
    Lk.new(w.outputs['Fac'], bm.inputs['Height']); Lk.new(bm.outputs['Normal'], p.inputs['Normal'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.4
    Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = N.new('ShaderNodeMapRange'); ramp.inputs['To Min'].default_value = 0.22; ramp.inputs['To Max'].default_value = 0.42
    Lk.new(nz.outputs['Fac'], ramp.inputs['Value']); Lk.new(ramp.outputs['Result'], p.inputs['Roughness'])
    MATS[nombre] = m
    return m


def mat_imagen(nombre, ruta, escala, rug=0.9, tinte=None, bump=0.2):
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (escala, escala, escala)
    Lk.new(tc.outputs['Object'], mp.inputs['Vector'])
    im = N.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(ruta)
    Lk.new(mp.outputs['Vector'], im.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.08
    Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    Lk.new(im.outputs['Color'], mix.inputs[6])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = tinte[0] if tinte else (0.8, 0.8, 0.8, 1)
    cr.color_ramp.elements[1].color = tinte[1] if tinte else (1, 1, 1, 1)
    Lk.new(nz.outputs['Fac'], cr.inputs['Fac']); Lk.new(cr.outputs['Color'], mix.inputs[7]); mix.inputs[0].default_value = 1
    Lk.new(mix.outputs[2], p.inputs['Base Color'])
    bmp = N.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = bump
    Lk.new(im.outputs['Color'], bmp.inputs['Height']); Lk.new(bmp.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Roughness'].default_value = rug
    MATS[nombre] = m
    return m


def mat_concreto(nombre, base=(178, 176, 170), escala=3.0, agregado=0.0, juntas=None):
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = escala
    nz.inputs['Detail'].default_value = 12; nz.inputs['Roughness'].default_value = 0.65; Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB')
    b_ = rgb(*base); cr.color_ramp.elements[0].color = tuple(c * 0.7 for c in b_[:3]) + (1,); cr.color_ramp.elements[1].color = b_
    Lk.new(nz.outputs['Fac'], cr.inputs['Fac'])
    vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 180; Lk.new(tc.outputs['Object'], vo.inputs['Vector'])
    cr2 = N.new('ShaderNodeMix'); cr2.data_type = 'RGBA'; cr2.blend_type = 'MULTIPLY'
    vm = N.new('ShaderNodeMapRange'); vm.inputs['From Min'].default_value = 0.0; vm.inputs['From Max'].default_value = 0.25
    vm.inputs['To Min'].default_value = 1.0 - agregado; vm.inputs['To Max'].default_value = 1.0
    Lk.new(vo.outputs['Distance'], vm.inputs['Value'])
    cmb = N.new('ShaderNodeCombineColor'); [Lk.new(vm.outputs['Result'], cmb.inputs[i]) for i in range(3)]
    Lk.new(cr.outputs['Color'], cr2.inputs[6]); Lk.new(cmb.outputs['Color'], cr2.inputs[7]); cr2.inputs[0].default_value = 1
    salida = cr2.outputs[2]
    if juntas:                                                      # bruñas / juntas cada n m
        br = N.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 1.0 / juntas; br.offset = 0.0
        br.inputs['Brick Width'].default_value = 1.0; br.inputs['Row Height'].default_value = 1.0; br.inputs['Mortar Size'].default_value = 0.012
        br.inputs['Color1'].default_value = (1, 1, 1, 1); br.inputs['Color2'].default_value = (1, 1, 1, 1); br.inputs['Mortar'].default_value = (0.45, 0.45, 0.45, 1)
        Lk.new(tc.outputs['Object'], br.inputs['Vector'])
        mj = N.new('ShaderNodeMix'); mj.data_type = 'RGBA'; mj.blend_type = 'MULTIPLY'; mj.inputs[0].default_value = 1
        Lk.new(salida, mj.inputs[6]); Lk.new(br.outputs['Color'], mj.inputs[7]); salida = mj.outputs[2]
    Lk.new(salida, p.inputs['Base Color'])
    nz2 = N.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 150; nz2.inputs['Detail'].default_value = 10
    Lk.new(tc.outputs['Object'], nz2.inputs['Vector'])
    p.inputs['Roughness'].default_value = 0.9
    biselar(N, Lk, p, nz2.outputs['Fac'], fuerza=0.18, dist=0.006, radio=0.01)
    MATS[nombre] = m
    return m


def mat_adoquin(nombre):
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    tc = N.new('ShaderNodeTexCoord'); br = N.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = rgb(150, 92, 74); br.inputs['Color2'].default_value = rgb(120, 70, 58)
    br.inputs['Mortar'].default_value = rgb(170, 165, 155); br.inputs['Scale'].default_value = 3.0
    br.inputs['Mortar Size'].default_value = 0.015; br.inputs['Brick Width'].default_value = 0.5; br.inputs['Row Height'].default_value = 0.25
    Lk.new(tc.outputs['Object'], br.inputs['Vector'])
    Lk.new(br.outputs['Color'], p.inputs['Base Color'])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.4
    Lk.new(br.outputs['Fac'], bm.inputs['Height']); Lk.new(bm.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Roughness'].default_value = 0.8
    MATS[nombre] = m
    return m


def mat_hojas(nombre, c1, c2):
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6
    nz.inputs['Detail'].default_value = 6; Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = c1; cr.color_ramp.elements[1].color = c2
    Lk.new(nz.outputs['Fac'], cr.inputs['Fac']); Lk.new(cr.outputs['Color'], p.inputs['Base Color'])
    vor = N.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 40; Lk.new(tc.outputs['Object'], vor.inputs['Vector'])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.9
    Lk.new(vor.outputs['Distance'], bm.inputs['Height']); Lk.new(bm.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Roughness'].default_value = 0.6
    MATS[nombre] = m
    return m


mat_pintura('TP3', TP3); mat_pintura('TP2', TP2); mat_pintura('TP1', TP1, rug=0.8)
mat_pintura('TP1_acrilica', TP1, rug=0.55)
mat_calamina('calamina_x', 'X'); mat_calamina('calamina_y', 'Y')
mat_simple('vidrio', rgb(35, 52, 62), rug=0.04)
MATS['vidrio'].node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.9
mat_simple('aluminio', rgb(70, 72, 75), rug=0.35, metal=0.9)
mat_simple('aluminio_claro', rgb(200, 200, 198), rug=0.3, metal=0.9)
mat_simple('canaleta_galv', rgb(176, 180, 182), rug=0.35, metal=0.85)
mat_simple('acero', rgb(110, 115, 120), rug=0.4, metal=0.8)
mat_simple('puerta', rgb(92, 64, 45), rug=0.5)
mat_simple('negro', rgb(20, 20, 22), rug=0.5)
mat_simple('blanco', rgb(240, 240, 238), rug=0.4)
mat_simple('madera', rgb(118, 78, 48), rug=0.6)
mat_simple('tronco', rgb(80, 62, 48), rug=0.9)
mat_simple('caucho_rojo', rgb(170, 60, 50), rug=0.9); mat_simple('caucho_verde', rgb(60, 130, 70), rug=0.9)
mat_simple('juego_amarillo', rgb(240, 190, 30), rug=0.4); mat_simple('juego_azul', rgb(30, 100, 200), rug=0.4)
mat_simple('cancha', rgb(46, 110, 92), rug=0.6); mat_simple('cancha_borde', rgb(150, 62, 52), rug=0.6)
mat_simple('linea', rgb(245, 245, 240), rug=0.6)
mat_simple('bandera_roja', rgb(200, 16, 46), rug=0.7); mat_simple('bandera_blanca', rgb(245, 245, 245), rug=0.7)
mat_concreto('concreto'); mat_concreto('vereda', (190, 186, 178), agregado=0.15, juntas=2.0); mat_concreto('asfalto', (52, 52, 54), 1.2, agregado=0.45)
mat_concreto('concreto_gris', (150, 150, 148))
mat_adoquin('adoquin')
mat_imagen('pasto', os.path.join(A, 'grasslight-big.jpg'), 0.22, tinte=((0.42, 0.50, 0.30, 1), (0.85, 0.88, 0.72, 1)), bump=0.5)
mat_hojas('hojas1', rgb(40, 78, 30), rgb(92, 130, 48)); mat_hojas('hojas2', rgb(30, 64, 28), rgb(70, 110, 40))
mat_hojas('hojas3', rgb(52, 90, 36), rgb(120, 150, 60))
mat_simple('hojas_int', rgb(18, 34, 14), rug=0.9)

# ------------------------------------------------------------------ geometría


def obj_mesh(nombre, verts, caras, mat, col=None):
    me = bpy.data.meshes.new(nombre); me.from_pydata(verts, [], caras); me.update()
    o = bpy.data.objects.new(nombre, me); (col or sc.collection).objects.link(o)
    if mat:
        o.data.materials.append(MATS[mat] if isinstance(mat, str) else mat)
    return o


def caja(nombre, x0, y0, z0, x1, y1, z1, mat, col=None):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return obj_mesh(nombre, v, f, mat, col)


def caja_c(nombre, cx, cy, cz, sx, sy, sz, mat, rotz=0, col=None):
    o = caja(nombre, -sx / 2, -sy / 2, -sz / 2, sx / 2, sy / 2, sz / 2, mat, col)
    o.location = (cx, cy, cz); o.rotation_euler = (0, 0, rotz)
    return o


def prisma(nombre, pts, z0, z1, mat, col=None):
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z0)) for x, y in pts]
    if len(pts) > 2 and (pts[0][0] - pts[-1][0]) ** 2 + (pts[0][1] - pts[-1][1]) ** 2 < 1e-6:
        bm.verts.remove(vs[-1]); vs = vs[:-1]
    try:
        f = bm.faces.new(vs)
    except ValueError:
        bm.free(); return None
    bmesh.ops.recalc_face_normals(bm, faces=[f])
    if f.normal.z > 0:
        f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, z1 - z0), verts=nv)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me); (col or sc.collection).objects.link(o); o.data.materials.append(MATS[mat])
    return o


def coleccion(nombre):
    c = bpy.data.collections.new(nombre); sc.collection.children.link(c)
    return c


# ------------------------------------------------------------------ terreno, calle y veredas
CT = coleccion('Terreno')
obj_mesh('suelo', [(-2500, -2500, -0.02), (2600, -2500, -0.02), (2600, 2600, -0.02), (-2500, 2600, -0.02)], [(0, 1, 2, 3)], 'pasto', CT)
c = D['calle']
caja('pista', c['pista'][0] - 200, c['pista'][1], -0.02, c['pista'][2] + 200, c['pista'][3], 0.02, 'asfalto', CT)
caja('vereda_ext', c['vereda_ext'][0] - 200, c['vereda_ext'][1], -0.02, c['vereda_ext'][2] + 200, c['vereda_ext'][3], 0.15, 'vereda', CT)
caja('vereda_otra', c['vereda_otra'][0] - 200, c['vereda_otra'][1], -0.02, c['vereda_otra'][2] + 200, c['vereda_otra'][3], 0.15, 'vereda', CT)
caja('sardinel', -230, 15.7, -0.02, 340, 15.85, 0.17, 'blanco', CT)
for xx in range(-220, 330, 6):                                            # líneas de carril
    caja('linea_carril', xx, 12.22, 0.02, xx + 3, 12.38, 0.025, 'linea', CT)
for i, pol in enumerate(D['veredas']):
    prisma('vereda_%d' % i, pol, 0.0, 0.10 + 0.002 * i, 'vereda', CT)
from shapely.geometry import Polygon as _SP, box as _SB, Point as _Pt
from shapely.ops import unary_union as _UU
VERDES = _UU([_SP(e_, i_).buffer(0) for e_, i_ in D['verdes']])
LOTE = _SB(1.05, 18.0, 71.76, 131.21)
mat_concreto('pavimento', (186, 182, 174), agregado=0.12, juntas=1.5)
_vs, _fs, _ix = [], [], {}
_p = 0.5
for _i in range(int((LOTE.bounds[2] - LOTE.bounds[0]) / _p) + 1):
    for _j in range(int((LOTE.bounds[3] - LOTE.bounds[1]) / _p) + 1):
        _cx, _cy = LOTE.bounds[0] + (_i + 0.5) * _p, LOTE.bounds[1] + (_j + 0.5) * _p
        if _cx > LOTE.bounds[2] or _cy > LOTE.bounds[3] or VERDES.contains(_Pt(_cx, _cy)):
            continue
        q = []
        for (a, b) in ((_i, _j), (_i + 1, _j), (_i + 1, _j + 1), (_i, _j + 1)):
            if (a, b) not in _ix:
                _ix[(a, b)] = len(_vs); _vs.append((LOTE.bounds[0] + a * _p, LOTE.bounds[1] + b * _p, 0.08))
            q.append(_ix[(a, b)])
        _fs.append(tuple(q))
_pav = obj_mesh('pavimento_concreto', _vs, _fs, 'pavimento', CT)
_m = _pav.modifiers.new('esp', 'SOLIDIFY'); _m.thickness = 0.1; _m.offset = -1
print('pavimento m2', len(_fs) * _p * _p)

# ------------------------------------------------------------------ edificaciones
CE = coleccion('Edificaciones')
VOL, H_MURO, Z_TECHO, PEND = 1.5, 3.3, 3.75, 0.28


def ventana(nombre, x, y, z0, ancho, alto, normal, col):
    """Ventana sobre la cara del muro: vidrio, marco de aluminio y alféizar."""
    nx, ny = normal; e = 0.03
    if nx == 0:                                         # muro paralelo a x
        caja(nombre + '_vid', x - ancho / 2, y + ny * e - 0.01, z0, x + ancho / 2, y + ny * e + 0.01, z0 + alto, 'vidrio', col)
        for xa, xb, za, zb in ((x - ancho / 2 - 0.05, x - ancho / 2, z0, z0 + alto), (x + ancho / 2, x + ancho / 2 + 0.05, z0, z0 + alto),
                               (x - ancho / 2, x + ancho / 2, z0 + alto, z0 + alto + 0.05), (x - 0.025, x + 0.025, z0, z0 + alto)):
            caja(nombre + '_m', xa, y + ny * 0.06 - 0.02, za, xb, y + ny * 0.06 + 0.02, zb, 'aluminio', col)
        caja(nombre + '_alf', x - ancho / 2 - 0.08, y, z0 - 0.06, x + ancho / 2 + 0.08, y + ny * 0.12, z0, 'concreto_gris', col)
    else:
        caja(nombre + '_vid', x + nx * e - 0.01, y - ancho / 2, z0, x + nx * e + 0.01, y + ancho / 2, z0 + alto, 'vidrio', col)
        for ya, yb, za, zb in ((y - ancho / 2 - 0.05, y - ancho / 2, z0, z0 + alto), (y + ancho / 2, y + ancho / 2 + 0.05, z0, z0 + alto),
                               (y - ancho / 2, y + ancho / 2, z0 + alto, z0 + alto + 0.05), (y - 0.025, y + 0.025, z0, z0 + alto)):
            caja(nombre + '_m', x + nx * 0.06 - 0.02, ya, za, x + nx * 0.06 + 0.02, yb, zb, 'aluminio', col)
        caja(nombre + '_alf', x, y - ancho / 2 - 0.08, z0 - 0.06, x + nx * 0.12, y + ancho / 2 + 0.08, z0, 'concreto_gris', col)


def puerta(nombre, x, y, ancho, normal, col, mat='puerta', alto=2.3):
    nx, ny = normal
    if nx == 0:
        caja(nombre, x - ancho / 2, y - 0.02 + ny * 0.03, 0.15, x + ancho / 2, y + 0.02 + ny * 0.03, alto, mat, col)
        caja(nombre + '_marco', x - ancho / 2 - 0.08, y + ny * 0.05 - 0.02, alto, x + ancho / 2 + 0.08, y + ny * 0.05 + 0.02, alto + 0.08, 'TP1', col)
    else:
        caja(nombre, x - 0.02 + nx * 0.03, y - ancho / 2, 0.15, x + 0.02 + nx * 0.03, y + ancho / 2, alto, mat, col)
        caja(nombre + '_marco', x + nx * 0.05 - 0.02, y - ancho / 2 - 0.08, alto, x + nx * 0.05 + 0.02, y + ancho / 2 + 0.08, alto + 0.08, 'TP1', col)


def edificio(e):
    x0, y0, x1, y1 = e['rect']; eje = e['cumbrera']; cod = e['cod']
    col = coleccion(cod)
    a0, b0, a1, b1 = x0 + VOL, y0 + VOL, x1 - VOL, y1 - VOL               # muros
    caja(cod + '_piso', a0 - 1.2, b0 - 1.2, 0, a1 + 1.2, b1 + 1.2, 0.15, 'vereda', col)
    caja(cod + '_muro', a0, b0, 0.15, a1, b1, H_MURO, 'TP2', col)
    caja(cod + '_zocalo', a0 - 0.02, b0 - 0.02, 0.15, a1 + 0.02, b1 + 0.02, 0.45, 'concreto_gris', col)
    caja(cod + '_viga', a0 - 0.04, b0 - 0.04, H_MURO, a1 + 0.04, b1 + 0.04, Z_TECHO, 'TP1', col)
    # columnas en esquinas y cada ~3.6 m
    for (xa, ya, xb, yb) in ((a0, b0, a1, b0), (a0, b1, a1, b1), (a0, b0, a0, b1), (a1, b0, a1, b1)):
        L = math.hypot(xb - xa, yb - ya); n = max(1, round(L / 3.6))
        for i in range(n + 1):
            t = i / n; cx, cy = xa + (xb - xa) * t, ya + (yb - ya) * t
            caja(cod + '_col', cx - 0.16, cy - 0.16, 0.15, cx + 0.16, cy + 0.16, H_MURO, 'TP1', col)
    # ventanas y puertas
    largo_x = (eje == 'y')
    for (xa, ya, xb, yb, nrm) in ((a0, b0, a1, b0, (0, -1)), (a0, b1, a1, b1, (0, 1)), (a0, b0, a0, b1, (-1, 0)), (a1, b0, a1, b1, (1, 0))):
        L = math.hypot(xb - xa, yb - ya); n = max(1, round(L / 3.6)); paso = L / n
        es_largo = (nrm[0] != 0) == largo_x
        for i in range(n):
            t = (i + 0.5) / n; cx, cy = xa + (xb - xa) * t, ya + (yb - ya) * t
            if es_largo:
                if i % 3 == 1 and L > 8:
                    puerta(cod + '_p%d' % i, cx, cy, 1.0, nrm, col)
                    ventana(cod + '_vt%d' % i, cx, cy, 2.45, 1.0, 0.5, nrm, col)
                else:
                    ventana(cod + '_v%d' % i, cx, cy, 1.05, paso * 0.58, 1.35, nrm, col)
            else:
                if i == n // 2:
                    puerta(cod + '_pp', cx, cy, 1.8 if cod in ('E-01', 'E-05') else 1.0, nrm, col,
                           mat='vidrio' if cod in ('E-01', 'E-05') else 'puerta', alto=2.5)
                else:
                    ventana(cod + '_vg%d' % i, cx, cy, 1.05, paso * 0.5, 1.35, nrm, col)
    # techo a dos aguas
    if eje == 'y':
        cxm = (x0 + x1) / 2; semi = (a1 - a0) / 2
        zr = Z_TECHO + PEND * semi; ze = Z_TECHO - PEND * VOL
        v = [(x0, y0, ze), (cxm, y0, zr), (cxm, y1, zr), (x0, y1, ze), (x1, y0, ze), (x1, y1, ze)]
        f = [(0, 1, 2, 3), (1, 4, 5, 2)]
        t = obj_mesh(cod + '_techo', v, f, 'calamina_x' if False else 'calamina_y', col)
        caja(cod + '_cumbrera', cxm - 0.2, y0, zr - 0.02, cxm + 0.2, y1, zr + 0.06, 'aluminio_claro', col)
        tri = [(a0, Z_TECHO), (cxm, zr), (a1, Z_TECHO)]
        for yy, s in ((b0, -1), (b1, 1)):
            vv = [(x, yy, z) for x, z in tri] + [(x, yy - s * 0.2, z) for x, z in tri]
            obj_mesh(cod + '_hastial', vv, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (0, 2, 5, 3)], 'TP3', col)
            caja(cod + '_canal', x0, yy + s * VOL - 0.06, ze - 0.12, x1, yy + s * VOL + 0.06, ze, 'TP1_acrilica', col) if False else None
        for xx in (x0, x1):
            caja(cod + '_canaleta', xx - 0.12, y0, ze - 0.2, xx + 0.12, y1, ze, 'canaleta_galv', col)
    else:
        cym = (y0 + y1) / 2; semi = (b1 - b0) / 2
        zr = Z_TECHO + PEND * semi; ze = Z_TECHO - PEND * VOL
        v = [(x0, y0, ze), (x1, y0, ze), (x1, cym, zr), (x0, cym, zr), (x1, y1, ze), (x0, y1, ze)]
        f = [(0, 1, 2, 3), (3, 2, 4, 5)]
        obj_mesh(cod + '_techo', v, f, 'calamina_x', col)
        caja(cod + '_cumbrera', x0, cym - 0.2, zr - 0.02, x1, cym + 0.2, zr + 0.06, 'aluminio_claro', col)
        tri = [(b0, Z_TECHO), (cym, zr), (b1, Z_TECHO)]
        for xx, s in ((a0, -1), (a1, 1)):
            vv = [(xx, y, z) for y, z in tri] + [(xx - s * 0.2, y, z) for y, z in tri]
            obj_mesh(cod + '_hastial', vv, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (0, 2, 5, 3)], 'TP3', col)
        for yy in (y0, y1):
            caja(cod + '_canaleta', x0, yy - 0.12, ze - 0.2, x1, yy + 0.12, ze, 'canaleta_galv', col)
    # solidificar techo
    t = bpy.data.objects[cod + '_techo']; mod = t.modifiers.new('esp', 'SOLIDIFY'); mod.thickness = 0.05


for e in D['edificios']:
    edificio(e)

# letrero del E-01 (administración)
# ------------------------------------------------------------------ losa deportiva con techo en arco
CL = coleccion('Losa deportiva')
x0, y0, x1, y1 = D['losa']
caja('losa', x0, y0, 0, x1, y1, 0.12, 'cancha_borde', CL)
cx0, cy0, cx1, cy1 = x0 + 1.5, y0 + 1.6, x1 - 1.5, y1 - 1.6
caja('cancha', cx0, cy0, 0.12, cx1, cy1, 0.125, 'cancha', CL)
lw = 0.08; zl = 0.127
for (a, b, c_, d) in ((cx0, cy0, cx1, cy0 + lw), (cx0, cy1 - lw, cx1, cy1), (cx0, cy0, cx0 + lw, cy1), (cx1 - lw, cy0, cx1, cy1),
                      (cx0, (cy0 + cy1) / 2 - lw / 2, cx1, (cy0 + cy1) / 2 + lw / 2)):
    caja('linea_cancha', a, b, 0.125, c_, d, zl, 'linea', CL)
mx, my = (cx0 + cx1) / 2, (cy0 + cy1) / 2
bpy.ops.mesh.primitive_torus_add(major_radius=3.0, minor_radius=0.04, location=(mx, my, 0.125))
t = bpy.context.active_object; t.scale = (1, 1, 0.05); t.data.materials.append(MATS['linea'])
bpy.context.collection.objects.unlink(t); CL.objects.link(t)
for yy, s in ((cy0, 1), (cy1, -1)):
    caja('area', mx - 3.5, min(yy, yy + s * 6), 0.125, mx + 3.5, max(yy, yy + s * 6), zl, 'cancha_borde', CL)
    for (a, b, c_, d) in ((mx - 3.5, min(yy, yy + s * 6), mx - 3.5 + lw, max(yy, yy + s * 6)),
                          (mx + 3.5 - lw, min(yy, yy + s * 6), mx + 3.5, max(yy, yy + s * 6)),
                          (mx - 3.5, yy + s * 6 - lw / 2, mx + 3.5, yy + s * 6 + lw / 2)):
        caja('linea_area', a, b, zl, c_, d, zl + 0.002, 'linea', CL)
    # arco de futsal + tablero de básquet
    for xx in (mx - 1.5, mx + 1.5):
        caja('poste_arco', xx - 0.04, yy - s * 0.05 - 0.04, 0.12, xx + 0.04, yy - s * 0.05 + 0.04, 2.12, 'blanco', CL)
    caja('travesano', mx - 1.54, yy - s * 0.05 - 0.04, 2.08, mx + 1.54, yy - s * 0.05 + 0.04, 2.16, 'blanco', CL)
    caja('poste_basquet', mx - 0.08, yy - s * 1.4 - 0.08, 0.12, mx + 0.08, yy - s * 1.4 + 0.08, 3.4, 'acero', CL)
    caja('tablero', mx - 0.9, yy - s * 0.3 - 0.02, 2.9, mx + 0.9, yy - s * 0.3 + 0.02, 3.95, 'blanco', CL)
    caja('brazo', mx - 0.05, min(yy - s * 1.4, yy - s * 0.3), 3.3, mx + 0.05, max(yy - s * 1.4, yy - s * 0.3), 3.4, 'acero', CL)
# estructura: columnas y arcos
H_COL, FLECHA = 6.0, 4.2
n_p = 7
yy_list = [y0 + (y1 - y0) * i / (n_p - 1) for i in range(n_p)]
span = x1 - x0; R = (span ** 2 / 4 + FLECHA ** 2) / (2 * FLECHA); xc = (x0 + x1) / 2; zc = H_COL + FLECHA - R


def z_arco(x):
    return zc + math.sqrt(max(R ** 2 - (x - xc) ** 2, 0))


for yy in yy_list:
    for xx in (x0, x1):
        caja('columna_losa', xx - 0.18, yy - 0.18, 0.12, xx + 0.18, yy + 0.18, H_COL, 'acero', CL)
    # arco reticulado: cuerda superior e inferior
    N = 40
    for k, dz in ((0, 0.0), (1, -0.6)):
        pts = []
        for i in range(N + 1):
            x = x0 + span * i / N; pts.append((x, yy, z_arco(x) + dz - 0.05))
        cv = bpy.data.curves.new('arco', 'CURVE'); cv.dimensions = '3D'; sp = cv.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (p[0], p[1], p[2], 1)
        cv.bevel_depth = 0.07 if k == 0 else 0.05
        o = bpy.data.objects.new('arco', cv); CL.objects.link(o); o.data.materials.append(MATS['acero'])
    for i in range(1, 20):                                          # diagonales
        xa = x0 + span * (i - 0.5) / 20; xb = x0 + span * i / 20
        za = z_arco(xa) - 0.65; zb = z_arco(xb) - 0.05
        cv = bpy.data.curves.new('diag', 'CURVE'); cv.dimensions = '3D'; sp = cv.splines.new('POLY'); sp.points.add(1)
        sp.points[0].co = (xa, yy, za, 1); sp.points[1].co = (xb, yy, zb, 1); cv.bevel_depth = 0.025
        o = bpy.data.objects.new('diag', cv); CL.objects.link(o); o.data.materials.append(MATS['acero'])
# cubierta curva
N = 48; vs = []; fs = []
for j, yy in enumerate((y0 - 0.8, y1 + 0.8)):
    for i in range(N + 1):
        x = x0 - 0.6 + (span + 1.2) * i / N
        vs.append((x, yy, z_arco(min(max(x, x0), x1)) - (0.25 if x < x0 or x > x1 else 0) + 0.02))
for i in range(N):
    fs.append((i, i + 1, N + 1 + i + 1, N + 1 + i))
cub = obj_mesh('cubierta_losa', vs, fs, 'calamina_y', CL)
cub.modifiers.new('esp', 'SOLIDIFY').thickness = 0.04
for xx in (x0, x1):                                                 # vigas longitudinales
    caja('viga_long', xx - 0.15, y0, H_COL - 0.3, xx + 0.15, y1, H_COL, 'acero', CL)

# ------------------------------------------------------------------ garita, estacionamientos, tanque
CO = coleccion('Obras exteriores')
gx0, gy0, gx1, gy1 = D['garita']
# Pórtico de ingreso OE-01 (detalle de la arquitecta): frente 13.75 m en vanos de 2.08 + 4.89 + 1.96 + 4.82; viga +4.18;
# parapeto con letras de +5.09 a +5.95; techo a una agua S = 30 % de +5.72 (frente) a +4.19 (fondo); muros M-1/M-2 en TP-2.
FX = [0.0, 2.08, 6.97, 8.93, 13.75]
yf, yb = gy0, gy1
X = lambda d: gx0 + d * (gx1 - gx0) / 13.75


def celosia(nombre, xa, xb, za, zb, y, paso=0.09):
    n = int((zb - za) / paso)
    for k in range(n):
        z = za + (k + 0.5) * (zb - za) / n
        caja(nombre, xa, y - 0.02, z - 0.025, xb, y + 0.02, z + 0.02, 'acero', CO)
    caja(nombre + '_marco', xa, y - 0.03, za, xb, y + 0.03, za + 0.04, 'negro', CO)
    caja(nombre + '_marco', xa, y - 0.03, zb - 0.04, xb, y + 0.03, zb, 'negro', CO)


def porton(nombre, xa, xb, zb, y, hojas=2):
    ancho = (xb - xa) / hojas
    for h in range(hojas):
        a, b = xa + h * ancho + 0.02, xa + (h + 1) * ancho - 0.02
        caja(nombre + '_m', a, y - 0.03, 0.05, b, y + 0.03, 0.1, 'negro', CO)
        caja(nombre + '_m', a, y - 0.03, zb - 0.05, b, y + 0.03, zb, 'negro', CO)
        caja(nombre + '_m', a, y - 0.03, 0.05, a + 0.05, y + 0.03, zb, 'negro', CO)
        caja(nombre + '_m', b - 0.05, y - 0.03, 0.05, b, y + 0.03, zb, 'negro', CO)
        n = int((zb - 0.15) / 0.1)
        for k in range(n):
            z = 0.12 + k * 0.1
            caja(nombre + '_l', a + 0.05, y - 0.015, z, b - 0.05, y + 0.015, z + 0.07, 'acero', CO)


caja('oe01_piso', gx0 - 0.5, yf - 0.6, 0, gx1 + 0.5, yb + 0.6, 0.05, 'vereda', CO)
for d in FX:                                                         # columnas C-1
    cx = X(min(max(d, 0.14), 13.61))
    caja('oe01_col', cx - 0.13, yf, 0.05, cx + 0.13, yf + 0.4, 4.18, 'TP1', CO)
    caja('oe01_col_post', cx - 0.13, yb - 0.4, 0.05, cx + 0.13, yb, 4.18, 'TP1', CO)
caja('oe01_viga', gx0, yf, 4.18, gx1, yf + 0.4, 4.71, 'TP1', CO)               # VG-1
caja('oe01_cielo', gx0, yf + 0.05, 4.71, gx1, yf + 0.4, 5.09, 'TP2', CO)        # CR-1
caja('oe01_parapeto', gx0 - 0.05, yf - 0.05, 5.09, gx1 + 0.05, yf + 0.3, 5.95, 'TP3', CO)  # PL-2
caja('oe01_viga_post', gx0, yb - 0.4, 3.55, gx1, yb, 4.19, 'TP1', CO)
caja('oe01_parapeto_post', gx0 - 0.05, yb - 0.25, 4.19, gx1 + 0.05, yb + 0.05, 4.79, 'TP3', CO)
for xx in (gx0, gx1):                                                # muros laterales en TP-2
    s = 1 if xx == gx0 else -1
    v = [(xx, yf, 0.05), (xx, yb, 0.05), (xx, yb, 4.19), (xx, yf, 5.72)]
    o = obj_mesh('oe01_lateral', v + [(x + s * 0.2, y, z) for x, y, z in v],
                 [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'TP2', CO)
v = [(gx0, yf + 0.3, 5.72), (gx1, yf + 0.3, 5.72), (gx1, yb - 0.2, 4.19), (gx0, yb - 0.2, 4.19)]   # losa inclinada + aluzinc
o = obj_mesh('oe01_techo', v, [(0, 1, 2, 3)], 'calamina_x', CO); o.modifiers.new('esp', 'SOLIDIFY').thickness = 0.2
# vano 1 (2.08): portón peatonal de dos hojas + celosía
porton('oe01_porton_peatonal', X(0.27), X(1.95), 2.85, yf + 0.2)
celosia('oe01_celosia1', X(0.27), X(1.95), 2.95, 4.15, yf + 0.2)
# vano 2 (4.89): muro M-1 en TP-2 con ventana de celosía; detrás SS.HH. y caseta
caja('oe01_muro_m1', X(2.21), yf + 0.15, 0.05, X(6.84), yb - 0.15, 4.18, 'TP2', CO)
caja('oe01_zocalo', X(2.21) - 0.01, yf + 0.14, 0.05, X(6.84) + 0.01, yf + 0.2, 0.45, 'concreto_gris', CO)
celosia('oe01_ventana', X(5.6), X(6.6), 1.2, 2.5, yf + 0.13, paso=0.07)
# vano 3 (1.96): puerta de la caseta + celosía
porton('oe01_puerta', X(7.1), X(8.8), 2.4, yf + 0.2, hojas=1)
celosia('oe01_celosia3', X(7.1), X(8.8), 2.95, 4.15, yf + 0.2)
caja('oe01_caseta', X(7.0), yf + 0.3, 0.05, X(8.9), yb - 0.15, 3.5, 'TP2', CO)
# vano 4 (4.82): portón vehicular de dos hojas + celosía en tres paños
porton('oe01_porton_vehicular', X(9.06), X(13.49), 2.85, yf + 0.2)
for k in range(3):
    a = X(9.06) + k * (X(13.49) - X(9.06)) / 3
    celosia('oe01_celosia4', a + 0.03, a + (X(13.49) - X(9.06)) / 3 - 0.03, 2.95, 4.15, yf + 0.2)
# letras suspendidas de acero color aluminio (0.40 m), centradas en el parapeto
fnt = bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf')
tx = bpy.data.curves.new('letrero', 'FONT'); tx.body = 'HOGAR DE REFUGIO TEMPORAL'; tx.font = fnt; tx.size = 0.52
tx.extrude = 0.025; tx.align_x = 'CENTER'; tx.align_y = 'CENTER'
lt = bpy.data.objects.new('letrero', tx); CO.objects.link(lt)
lt.location = ((gx0 + gx1) / 2, yf - 0.1, 5.52); lt.rotation_euler = (math.pi / 2, 0, 0)
lt.data.materials.append(MATS['aluminio_claro'])
for nom, (ax0, ay0, ax1, ay1) in (('autos', D['autos']), ('motos', D['motos'])):
    for xx in (ax0 + 0.3, (ax0 + ax1) / 2, ax1 - 0.3):
        for yy in (ay0 + 0.3, ay1 - 0.3):
            caja('poste_' + nom, xx - 0.06, yy - 0.06, 0.1, xx + 0.06, yy + 0.06, 2.7, 'acero', CO)
    v = [(ax0, ay0, 2.65), (ax1, ay0, 2.65), (ax1, ay1, 2.95), (ax0, ay1, 2.95)]
    o = obj_mesh('techo_' + nom, v, [(0, 1, 2, 3)], 'calamina_y', CO); o.modifiers.new('esp', 'SOLIDIFY').thickness = 0.04
    caja('losa_' + nom, ax0, ay0, 0, ax1, ay1, 0.1, 'concreto_gris', CO)
tx0, ty0, tx1, ty1 = D['tanque']
for xx in (tx0 + 0.2, tx1 - 0.2):
    for yy in (ty0 + 0.2, ty1 - 0.2):
        caja('tanque_col', xx - 0.2, yy - 0.2, 0, xx + 0.2, yy + 0.2, 11.0, 'concreto_gris', CO)
for zz in (3.6, 7.2):
    caja('tanque_viga', tx0, ty0 + 0.05, zz, tx1, ty0 + 0.35, zz + 0.4, 'concreto_gris', CO)
    caja('tanque_viga', tx0, ty1 - 0.35, zz, tx1, ty1 - 0.05, zz + 0.4, 'concreto_gris', CO)
    caja('tanque_viga', tx0 + 0.05, ty0, zz, tx0 + 0.35, ty1, zz + 0.4, 'concreto_gris', CO)
    caja('tanque_viga', tx1 - 0.35, ty0, zz, tx1 - 0.05, ty1, zz + 0.4, 'concreto_gris', CO)
caja('tanque_losa', tx0 - 0.3, ty0 - 0.3, 11.0, tx1 + 0.3, ty1 + 0.3, 11.25, 'concreto_gris', CO)
for yy in ((ty0 + ty1) / 2 - 1.2, (ty0 + ty1) / 2 + 1.2):
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=1.9, location=((tx0 + tx1) / 2, yy, 12.2))
    o = bpy.context.active_object; o.data.materials.append(MATS['negro']); bpy.context.collection.objects.unlink(o); CO.objects.link(o)
    bpy.ops.object.shade_smooth()

# ------------------------------------------------------------------ cerco perimétrico
XO, XE, YF, YN = 1.05, 71.76, 18.0, 131.21                          # borde exterior del terreno (cerco perimétrico)
TRAMOS = [((XO, YF), (gx0, YF)), ((gx1, YF), (XE, YF)),              # frente: dos tramos hasta los costados del pórtico OE-01
          ((XE, YF), (XE, YN)), ((XE, YN), (XO, YN)), ((XO, YN), (XO, YF))]
for (xa, ya), (xb, yb) in TRAMOS:
    L = math.hypot(xb - xa, yb - ya)
    if L < 0.5:
        continue
    ang = math.atan2(yb - ya, xb - xa); cx, cy = (xa + xb) / 2, (ya + yb) / 2
    frontal = ya < 19.5 and yb < 19.5
    if frontal:
        caja_c('cerco_base', cx, cy, 0.3, L, 0.2, 0.6, 'TP3', ang, CO)
        nb = int(L / 0.14)
        for k in range(nb):
            t = (k + 0.5) / nb; bx, by = xa + (xb - xa) * t, ya + (yb - ya) * t
            caja_c('reja', bx, by, 1.45, 0.04, 0.04, 1.7, 'blanco', ang, CO)
        caja_c('pasamano', cx, cy, 2.3, L, 0.08, 0.06, 'blanco', ang, CO)
        nc = max(1, round(L / 3.0))
        for k in range(nc + 1):
            t = k / nc; bx, by = xa + (xb - xa) * t, ya + (yb - ya) * t
            caja_c('columna_cerco', bx, by, 1.25, 0.3, 0.3, 2.5, 'TP1', ang, CO)
    else:
        caja_c('cerco_muro', cx, cy, 1.2, L, 0.15, 2.4, 'TP3', ang, CO)
        caja_c('cerco_zocalo', cx, cy, 0.3, L, 0.17, 0.6, 'TP2', ang, CO)
        caja_c('cerco_remate', cx, cy, 2.43, L, 0.25, 0.06, 'concreto_gris', ang, CO)
        nc = max(1, round(L / 3.0))
        for k in range(nc + 1):
            t = k / nc; bx, by = xa + (xb - xa) * t, ya + (yb - ya) * t
            caja_c('columna_cerco', bx, by, 1.25, 0.28, 0.28, 2.5, 'TP2', ang, CO)

# ------------------------------------------------------------------ plaza con pérgola, juegos, asta
px0, py0, px1, py1 = D['plaza']
caja('plaza_piso', px0, py0, 0, px1, py1, 0.12, 'adoquin', CO)
for xx in [px0 + 0.2 + i * ((px1 - px0 - 0.4) / 3) for i in range(4)]:
    for yy in [py0 + 0.2 + i * ((py1 - py0 - 0.4) / 4) for i in range(5)]:
        caja('pergola_poste', xx - 0.1, yy - 0.1, 0.12, xx + 0.1, yy + 0.1, 3.0, 'madera', CO)
for i in range(int((py1 - py0) / 1.5) + 1):
    yy = py0 + i * 1.5
    caja('pergola_viga', px0 - 0.3, yy - 0.06, 3.0, px1 + 0.3, yy + 0.06, 3.25, 'madera', CO)
for i in range(int((px1 - px0) / 0.5) + 1):
    xx = px0 + i * 0.5
    caja('pergola_liston', xx - 0.03, py0 - 0.3, 3.25, xx + 0.03, py1 + 0.3, 3.37, 'madera', CO)
for b in D['bancas']:
    (bx, by), r = b['p'], math.radians(b['rot'])
    caja_c('banca_base', bx, by, 0.22, 1.6, 0.4, 0.3, 'concreto_gris', r, CO)
    caja_c('banca_asiento', bx, by, 0.42, 1.8, 0.45, 0.06, 'madera', r, CO)
ax0, ay0, ax1, ay1 = D['asta']
for k in range(3):
    xx = ax0 + 0.4 + k * 0.7
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=8.0, location=(xx, (ay0 + ay1) / 2, 4.0))
    o = bpy.context.active_object; o.data.materials.append(MATS['aluminio_claro']); bpy.context.collection.objects.unlink(o); CO.objects.link(o)
    if k == 1:                                                     # bandera del Perú
        for j, m_ in enumerate(('bandera_roja', 'bandera_blanca', 'bandera_roja')):
            caja('bandera', xx + 0.05 + j * 0.5, (ay0 + ay1) / 2 - 0.01, 6.7, xx + 0.05 + (j + 1) * 0.5, (ay0 + ay1) / 2 + 0.01, 7.7, m_, CO)
caja('asta_base', ax0, ay0, 0, ax1, ay1, 0.35, 'concreto_gris', CO)
# ------------------------------------------------------------------ juegos infantiles OC-04 (piso de arena AR-SAND del plano)
mat_concreto('arena', (198, 168, 120), escala=60.0, agregado=0.45)
mat_simple('juego_rojo', rgb(200, 45, 40), rug=0.35); mat_simple('juego_verde', rgb(40, 150, 70), rug=0.4)
mat_simple('plastico_amarillo', rgb(245, 196, 30), rug=0.25)
ox0, oy0, ox1, oy1 = D['oc04']
caja('juegos_arena', ox0, oy0, 0, ox1, oy1, 0.13, 'arena', CO)
for (a0, b0, a1, b1) in ((ox0 - 0.15, oy0 - 0.15, ox1 + 0.15, oy0), (ox0 - 0.15, oy1, ox1 + 0.15, oy1 + 0.15),
                         (ox0 - 0.15, oy0, ox0, oy1), (ox1, oy0, ox1 + 0.15, oy1)):
    caja('juegos_sardinel', a0, b0, 0, a1, b1, 0.26, 'concreto_gris', CO)


def tubo(nombre, p0, p1, r, mat, col=CO):
    """Tubo metálico entre dos puntos (cilindro orientado)."""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=d.length, location=(p0 + p1) / 2)
    o = bpy.context.active_object; o.name = nombre
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(MATS[mat]); bpy.context.collection.objects.unlink(o); col.objects.link(o)
    return o


ZA = 0.13                                                          # nivel de la arena
for j in D['juegos']:
    x0, y0, x1, y1 = j['bb']; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    largo_x = (x1 - x0) >= (y1 - y0)
    if j['n'] == 'COLUMPIO':                                       # pórtico en A con dos asientos
        for xe in (x0 + 0.1, x1 - 0.1):
            for dy in (-0.42, 0.42):
                tubo('columpio_pata', (xe, cy + dy, ZA), (xe, cy, 2.35), 0.04, 'juego_rojo')
        tubo('columpio_viga', (x0 + 0.1, cy, 2.35), (x1 - 0.1, cy, 2.35), 0.05, 'juego_rojo')
        for xs in (cx - 0.75, cx + 0.75):
            caja('columpio_asiento', xs - 0.23, cy - 0.11, 0.48, xs + 0.23, cy + 0.11, 0.52, 'plastico_amarillo', CO)
            for dx in (-0.2, 0.2):
                tubo('cadena', (xs + dx, cy, 0.52), (xs + dx, cy, 2.33), 0.008, 'acero')
    elif j['n'] == 'TBGAN':                                        # escalera, plataforma y resbaladera
        xa, xb = x0 + 0.2, x1 - 0.2; ya = y0 + 0.15; yp0, yp1 = y0 + 0.75, y0 + 1.55
        for xx in (xa, xb):
            tubo('tobogan_escalera', (xx, ya, ZA), (xx, yp0, 1.45), 0.035, 'juego_azul')
            for yy in (yp0, yp1):
                tubo('tobogan_poste', (xx, yy, ZA), (xx, yy, 2.4), 0.04, 'juego_azul')
        for k in range(1, 6):
            t = k / 6; tubo('peldano', (xa, ya + (yp0 - ya) * t, ZA + (1.45 - ZA) * t), (xb, ya + (yp0 - ya) * t, ZA + (1.45 - ZA) * t), 0.02, 'acero')
        caja('tobogan_plataforma', xa, yp0, 1.40, xb, yp1, 1.48, 'juego_rojo', CO)
        caja('tobogan_techo', xa - 0.1, yp0 - 0.1, 2.40, xb + 0.1, yp1 + 0.1, 2.48, 'juego_verde', CO)
        for xx in (xa, xb):
            tubo('baranda', (xx, yp0, 2.0), (xx, yp1, 2.0), 0.025, 'juego_azul')
        w = 0.5; xm = cx
        v = [(xm - w / 2, yp1, 1.46), (xm + w / 2, yp1, 1.46), (xm + w / 2, y1 - 0.45, 0.42), (xm - w / 2, y1 - 0.45, 0.42),
             (xm - w / 2, y1 - 0.05, 0.32), (xm + w / 2, y1 - 0.05, 0.32)]
        o = obj_mesh('resbaladera', v, [(0, 1, 2, 3), (3, 2, 5, 4)], 'plastico_amarillo', CO)
        o.modifiers.new('esp', 'SOLIDIFY').thickness = 0.03
        for s_ in (-1, 1):
            obj_mesh('resbaladera_borde', [(xm + s_ * w / 2, yp1, 1.46), (xm + s_ * w / 2, y1 - 0.45, 0.42), (xm + s_ * w / 2, y1 - 0.05, 0.32),
                                           (xm + s_ * w / 2, y1 - 0.05, 0.47), (xm + s_ * w / 2, y1 - 0.45, 0.57), (xm + s_ * w / 2, yp1, 1.61)],
                     [(0, 1, 4, 5), (1, 2, 3, 4)], 'plastico_amarillo', CO).modifiers.new('esp', 'SOLIDIFY').thickness = 0.03
    else:                                                          # sube y baja (uno o dos balancines)
        corto = (y1 - y0) if largo_x else (x1 - x0)
        n = 2 if corto > 1.5 else 1
        for k in range(n):
            f = (k + 0.5) / n
            if largo_x:
                yy = y0 + corto * f; a, b = (x0 + 0.1, yy, 0.30), (x1 - 0.1, yy, 0.78); piv = (cx, yy)
            else:
                xx = x0 + corto * f; a, b = (xx, y0 + 0.1, 0.30), (xx, y1 - 0.1, 0.78); piv = (xx, cy)
            caja_c('balancin_base', piv[0], piv[1], ZA + 0.22, 0.35, 0.35, 0.44, 'juego_azul', 0, CO)
            av = Vector(a); bv = Vector(b); d = bv - av
            o = caja_c('balancin_tabla', *((av + bv) / 2), d.length, 0.28, 0.05, 'juego_rojo', 0, CO)
            o.rotation_euler = d.to_track_quat('X', 'Z').to_euler()
            for e_ in (0.12, 0.88):
                pe = av + d * e_
                tubo('balancin_manija', pe + Vector((0, 0, 0.03)), pe + Vector((0, 0, 0.45)), 0.022, 'plastico_amarillo')

# ------------------------------------------------------------------ cunetas con rejilla (capa 1-CUNETAS) y colector frontal
mat_simple('galvanizado', rgb(168, 172, 174), rug=0.38, metal=0.85)
mat_simple('pvc', rgb(205, 205, 200), rug=0.4)
mat_concreto('cuneta_fondo', (34, 34, 33), escala=8.0, agregado=0.2)
mat_concreto('concreto_cuneta', (196, 194, 188), agregado=0.1)
CDR = coleccion('Drenaje')
VER = _UU([_SP(p).buffer(0) for p in D['veredas'] if len(p) >= 3])
_bv, _bf = [], []


def _barra(x0, y0, z0, x1, y1, z1):
    i = len(_bv)
    _bv.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
    _bf.extend([(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7), (i, i + 1, i + 5, i + 4), (i + 1, i + 2, i + 6, i + 5),
                (i + 2, i + 3, i + 7, i + 6), (i + 3, i, i + 4, i + 7)])


# Red de cunetas tal cual el plano de drenaje (bloque "red drenaje" del DXF PLANTA GENERAL - MUJERES VIOLENTADAS): ejes 01 a
# 12 con interior 0.40, muros de 0.10 y rejilla de platinas 1" x 3/16" @ 0.025 con angulo de marco; tapas de inspeccion,
# sumideros con rejilla y las cunetas del frente achuradas en el mismo bloque.
PISOS = _UU([_SB(e['rect'][0] + VOL - 1.2, e['rect'][1] + VOL - 1.2, e['rect'][2] - VOL + 1.2, e['rect'][3] - VOL + 1.2) for e in D['edificios']])
_mv, _mf, _fv, _ff = [], [], [], []


def _orientada(lv, lf, P, d, n, s0, s1, t0, t1, z0, z1):
    """Caja orientada: s a lo largo de d, t a lo largo de n (en metros)."""
    i = len(lv)
    for (s, t) in ((s0, t0), (s1, t0), (s1, t1), (s0, t1)):
        lv.append((P[0] + d[0] * s + n[0] * t, P[1] + d[1] * s + n[1] * t, z0))
    for (s, t) in ((s0, t0), (s1, t0), (s1, t1), (s0, t1)):
        lv.append((P[0] + d[0] * s + n[0] * t, P[1] + d[1] * s + n[1] * t, z1))
    lf.extend([(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7), (i, i + 1, i + 5, i + 4), (i + 1, i + 2, i + 6, i + 5),
               (i + 2, i + 3, i + 7, i + 6), (i + 3, i, i + 4, i + 7)])


def _nivel(geom):
    if PISOS.intersection(geom).area > 0.02:
        return 0.158
    return 0.118 if VER.intersection(geom).area > 0.02 else 0.092


def cuneta(A, B, w=0.20, e_=0.10, ext=True):
    dx, dy = B[0] - A[0], B[1] - A[1]; L = math.hypot(dx, dy)
    if L < 1e-3:
        return 0
    d = (dx / L, dy / L); n = (-d[1], d[0]); x0 = -(w + e_) if ext else 0; x1 = L + (w + e_ if ext else 0)
    zt = _nivel(_SP([(A[0] + n[0] * 0.3, A[1] + n[1] * 0.3), (B[0] + n[0] * 0.3, B[1] + n[1] * 0.3),
                     (B[0] - n[0] * 0.3, B[1] - n[1] * 0.3), (A[0] - n[0] * 0.3, A[1] - n[1] * 0.3)]))
    _orientada(_mv, _mf, A, d, n, x0, x1, w, w + e_, -0.02, zt)          # muros
    _orientada(_mv, _mf, A, d, n, x0, x1, -w - e_, -w, -0.02, zt)
    _orientada(_fv, _ff, A, d, n, x0, x1, -w, w, -0.02, zt - 0.03)       # fondo (agua y sombra)
    zb = zt - 0.0254
    _orientada(_bv, _bf, A, d, n, x0 + e_, x1 - e_, w - 0.025, w, zb, zt)    # ángulo del marco
    _orientada(_bv, _bf, A, d, n, x0 + e_, x1 - e_, -w, -w + 0.025, zb, zt)
    s = x0 + e_ + 0.0125
    while s < x1 - e_:
        _orientada(_bv, _bf, A, d, n, s - 0.0024, s + 0.0024, -w + 0.025, w - 0.025, zb, zt - 0.001); s += 0.025
    return L


L_cun = 0
for k_, pts in D['ejes_cuneta'].items():
    for A_, B_ in zip(pts, pts[1:]):
        L_cun += cuneta(A_, B_)
for (x0, y0, x1, y1) in D['cunetas_frente']:                       # cunetas del frente (achurado del mismo bloque)
    if (x1 - x0) >= (y1 - y0):
        L_cun += cuneta(((x0), (y0 + y1) / 2), (x1, (y0 + y1) / 2), w=(y1 - y0) / 2, ext=False)
    else:
        L_cun += cuneta(((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), w=(x1 - x0) / 2, ext=False)
obj_mesh('cunetas_muros', _mv, _mf, 'concreto_cuneta', CDR)
obj_mesh('cunetas_fondo', _fv, _ff, 'cuneta_fondo', CDR)
_bv2, _bf2 = [], []
for (x0, y0, x1, y1) in D['sumideros']:                            # sumideros con rejilla 0.25 x 0.25
    zt = _nivel(_SB(x0 - 0.05, y0 - 0.05, x1 + 0.05, y1 + 0.05)) + 0.002
    caja('sumidero_fondo', x0, y0, -0.02, x1, y1, zt - 0.03, 'cuneta_fondo', CDR)
    for (a0, b0, a1, b1) in ((x0 - 0.02, y0 - 0.02, x1 + 0.02, y0), (x0 - 0.02, y1, x1 + 0.02, y1 + 0.02), (x0 - 0.02, y0, x0, y1), (x1, y0, x1 + 0.02, y1)):
        _barra(a0, b0, zt - 0.0254, a1, b1, zt)
    k = x0 + 0.025
    while k < x1 - 0.01:
        _barra(k - 0.0024, y0, zt - 0.0254, k + 0.0024, y1, zt - 0.001); k += 0.025
obj_mesh('rejillas_cunetas', _bv, _bf, 'galvanizado', CDR)
mat_concreto('tapa_inspeccion', (150, 148, 142), escala=6.0, agregado=0.25)
for (x0, y0, x1, y1) in D['tapas_inspeccion']:                     # tapas de inspección de concreto sobre la cuneta
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    zt = _nivel(_SB(cx - 0.3, cy - 0.3, cx + 0.3, cy + 0.3))
    caja('tapa_insp_junta', cx - 0.32, cy - 0.32, zt - 0.01, cx + 0.32, cy + 0.32, zt + 0.004, 'negro', CDR)
    caja('tapa_inspeccion', cx - 0.30, cy - 0.30, zt - 0.01, cx + 0.30, cy + 0.30, zt + 0.012, 'tapa_inspeccion', CDR)
    for dd in (-0.15, 0.15):
        caja('tapa_insp_asa', cx + dd - 0.04, cy - 0.012, zt + 0.012, cx + dd + 0.04, cy + 0.012, zt + 0.016, 'acero', CDR)
print('cunetas con rejilla m', round(L_cun, 2), 'sumideros', len(D['sumideros']), 'tapas', len(D['tapas_inspeccion']))
# montantes PVC 4" en las esquinas de cada edificación (símbolo del plano): boquilla, desvío bajo el alero, bajada adosada
# al muro y falsa columna de concreto hasta +1.05
N_mont = 0
for e in D['edificios']:
    x0, y0, x1, y1 = e['rect']; a0, b0, a1, b1 = x0 + VOL, y0 + VOL, x1 - VOL, y1 - VOL; ze = Z_TECHO - PEND * VOL
    if e['cumbrera'] == 'y':
        pts = [(x0 + 0.12, a0 - 0.09, b0 + 0.35, 'x'), (x0 + 0.12, a0 - 0.09, b1 - 0.35, 'x'),
               (x1 - 0.12, a1 + 0.09, b0 + 0.35, 'x'), (x1 - 0.12, a1 + 0.09, b1 - 0.35, 'x')]
    else:
        pts = [(y0 + 0.12, b0 - 0.09, a0 + 0.35, 'y'), (y0 + 0.12, b0 - 0.09, a1 - 0.35, 'y'),
               (y1 - 0.12, b1 + 0.09, a0 + 0.35, 'y'), (y1 - 0.12, b1 + 0.09, a1 - 0.35, 'y')]
    for (c_can, c_muro, c_l, eje_) in pts:
        P = (lambda c, l: (c, l)) if eje_ == 'x' else (lambda c, l: (l, c))
        p1, p2 = P(c_can, c_l), P(c_muro, c_l)
        tubo('montante_boquilla', (*p1, ze - 0.2), (*p1, ze - 0.42), 0.055, 'pvc')
        tubo('montante_desvio', (*p1, ze - 0.42), (*p2, ze - 0.42), 0.055, 'pvc')
        tubo('montante_bajada', (*p2, ze - 0.42), (*p2, 1.05), 0.055, 'pvc')
        for zz in (1.8, 2.7):
            tubo('montante_abrazadera', (*p2, zz), (*p2, zz + 0.04), 0.062, 'galvanizado')
        caja_c('falsa_columna', p2[0], p2[1], 0.15 + 0.45, 0.25, 0.25, 0.90, 'concreto_gris', 0, CDR)
        N_mont += 1
print('montantes', N_mont)
C_ = D['colector']                                                 # losa-vereda del colector b 0.80 y tapas ciegas
ye, yc, xne = C_['y_eje'], C_['y_cerco'], C_['x_ne']
ya_ = ye - C_['b'] / 2 - C_['e_muro']
caja('colector_losa', xne - C_['p_quiebre'] - 0.3, ya_, 0.15, xne + 0.3, yc, 0.162, 'concreto_cuneta', CDR)
mat_concreto('tapa_concreto', (112, 110, 104), escala=6.0, agregado=0.3)
for yj in (ya_, yc - 0.0254):                                      # juntas de 1" (vereda-colector y colector-cerco)
    caja('junta_colector', xne - C_['p_quiebre'] - 0.3, yj, 0.15, xne + 0.3, yj + 0.0254, 0.164, 'negro', CDR)
xj = xne
while xj > xne - C_['p_quiebre']:                                  # juntas transversales de la losa
    caja('junta_losa', xj - 0.0127, ya_, 0.15, xj + 0.0127, yc, 0.1635, 'negro', CDR); xj -= 3.0
for r in C_['registros']:
    xr = xne - r['p']
    caja('tapa_junta', xr - 0.345, ye - 0.495, 0.161, xr + 0.345, ye + 0.495, 0.164, 'negro', CDR)
    caja('tapa_ciega', xr - 0.31, ye - 0.46, 0.161, xr + 0.31, ye + 0.46, 0.170, 'tapa_concreto', CDR)
    for dy in (-0.25, 0.25):
        caja('tapa_asa', xr - 0.04, ye + dy - 0.012, 0.168, xr + 0.04, ye + dy + 0.012, 0.172, 'acero', CDR)

# ------------------------------------------------------------------ OC-01 jardinera + banca + pérgola (3 juegos, lámina OC-01)
mat_simple('estructura_acero', rgb(38, 38, 40), rug=0.45, metal=0.6)
mat_concreto('tierra_jardinera', (92, 70, 50), escala=20.0, agregado=0.3)
mat_simple('arbusto', rgb(48, 96, 38), rug=0.8)
MODS = [(0.0, 3.79, -1, 0.15), (3.79, 8.00, 1, 3.94), (8.00, 11.79, -1, 11.65)]   # (u0, u1, lado de la banca, salida de la canaleta)
Z_BAJO, Z_ALTO = 2.70, 3.16
JARD = []
JARD_ARB = []
for J in D['oc01']:
    x0, y0, x1, y1 = J['bb']; c0 = Vector(((x0 + x1) / 2, (y0 + y1) / 2, 0)); th = math.radians(J['rot'])
    ru = Vector((math.cos(th), math.sin(th), 0)); rv = Vector((-math.sin(th), math.cos(th), 0)); Lt = 11.79

    def W(u, v, z=0.0):
        return c0 + ru * (u - Lt / 2) + rv * v + Vector((0, 0, z))

    def pieza(nombre, u0, v0, z0, u1, v1, z1, mat):
        cc = W((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2)
        return caja_c(nombre, cc.x, cc.y, cc.z, abs(u1 - u0), abs(v1 - v0), abs(z1 - z0), mat, th, CO)

    pieza('jardinera', -0.1, -0.6, 0.0, Lt + 0.1, 0.6, 0.45, 'concreto_gris')
    pieza('jardinera_tierra', 0.0, -0.5, 0.40, Lt, 0.5, 0.455, 'tierra_jardinera')
    JARD.append(_SP([tuple(W(u, v))[:2] for u, v in ((0.05, -0.45), (Lt - 0.05, -0.45), (Lt - 0.05, 0.45), (0.05, 0.45))]))
    cal = 'calamina_x' if abs(math.cos(th)) > 0.5 else 'calamina_y'
    for (u0, u1, s, us) in MODS:
        vb, va = -s * 0.6, s * 1.8                                  # borde bajo (canaleta) y borde alto
        zc = Z_BAJO + (Z_ALTO - Z_BAJO) * (1.2 / 2.4)               # altura en la línea de columnas (v = s*0.6)
        for uc in (u0 + 0.18, u1 - 0.18):
            pieza('oc01_columna', uc - 0.05, s * 0.6 - 0.125, 0.0, uc + 0.05, s * 0.6 + 0.125, zc, 'estructura_acero')
        pieza('oc01_viga', u0 + 0.05, s * 0.6 - 0.05, zc - 0.12, u1 - 0.05, s * 0.6 + 0.05, zc, 'estructura_acero')
        for uc in (u0 + 0.18, u1 - 0.18):                           # vigas inclinadas bajo la cobertura
            a, b = W(uc, vb, Z_BAJO - 0.06), W(uc, va, Z_ALTO - 0.06); d = b - a
            o = caja_c('oc01_correa', *((a + b) / 2), d.length, 0.05, 0.10, 'estructura_acero', 0, CO)
            o.rotation_euler = d.to_track_quat('X', 'Z').to_euler()
        vs_ = [tuple(W(u0, vb, Z_BAJO)), tuple(W(u1, vb, Z_BAJO)), tuple(W(u1, va, Z_ALTO)), tuple(W(u0, va, Z_ALTO))]
        o = obj_mesh('oc01_cobertura_aluzinc', vs_, [(0, 1, 2, 3)], cal, CO); o.modifiers.new('esp', 'SOLIDIFY').thickness = 0.03
        pieza('oc01_canaleta', u0, vb - s * 0.0, Z_BAJO - 0.21, u1, vb - s * 0.18, Z_BAJO + 0.01, 'galvanizado')
        pv = W(us, vb - s * 0.09)                                    # bajada Ø4" y falsa columna CL-01
        tubo('oc01_bajada', (pv.x, pv.y, Z_BAJO - 0.21), (pv.x, pv.y, 1.05), 0.055, 'pvc')
        pieza('oc01_falsa_columna', us - 0.1, vb - s * 0.09 - 0.1, 0.0, us + 0.1, vb - s * 0.09 + 0.1, 1.05, 'concreto_gris')
        for k in range(6):                                           # celosía de madera (respaldo)
            zz = 1.05 + k * 0.24
            pieza('oc01_celosia', u0 + 0.25, s * 0.6 - 0.02, zz, u1 - 0.25, s * 0.6 + 0.02, zz + 0.14, 'madera')
        for k in range(5):                                           # asiento de madera
            vv = s * (0.70 + k * 0.09)
            pieza('oc01_asiento', u0 + 0.15, vv - 0.035, 0.44, u1 - 0.15, vv + 0.035, 0.48, 'madera')
        for uc in (u0 + 0.25, (u0 + u1) / 2, u1 - 0.25):
            pieza('oc01_pata', uc - 0.025, s * 0.66, 0.0, uc + 0.025, s * 1.12, 0.44, 'estructura_acero')
        if s > 0:                                                    # dos arbolitos en la jardinera central (elevación E1)
            JARD_ARB.extend([W(u0 + 1.25, 0.0, 0.45), W(u1 - 1.25, 0.0, 0.45)])

# ------------------------------------------------------------------ árboles
CA = coleccion('Arboles')
PROTO = []
COPAS = {}
bpy.ops.mesh.primitive_circle_add(vertices=10, radius=0.5, fill_type='NGON', location=(0, -500, -50))
HOJA = bpy.context.active_object; HOJA.name = 'hoja'; HOJA.scale = (0.12, 0.24, 1)
bpy.ops.object.transform_apply(scale=True)
mh = bpy.data.materials.new('hoja_mat'); mh.use_nodes = True; Nh = mh.node_tree.nodes; Lh = mh.node_tree.links
ph = Nh['Principled BSDF']; oi = Nh.new('ShaderNodeObjectInfo'); crh = Nh.new('ShaderNodeValToRGB')
crh.color_ramp.elements[0].color = rgb(52, 92, 34); crh.color_ramp.elements[1].color = rgb(150, 178, 70)
geoh = Nh.new('ShaderNodeNewGeometry'); Lh.new(geoh.outputs['Random Per Island'], crh.inputs['Fac']); Lh.new(crh.outputs['Color'], ph.inputs['Base Color'])
ph.inputs['Roughness'].default_value = 0.42; ph.inputs['Subsurface Weight'].default_value = 0.0
ph.inputs['Transmission Weight'].default_value = 0.0
ph.inputs['Subsurface Radius'].default_value = (0.2, 0.4, 0.1)
HOJA.data.materials.append(mh)
for k in range(8):
    col = bpy.data.collections.new('arbol_%d' % k)
    cerca = k < 4
    hgt = [3.0, 3.6, 2.6, 4.2][k % 4]; rad = [2.2, 2.8, 1.8, 3.2][k % 4]
    bpy.ops.mesh.primitive_cone_add(radius1=0.24, radius2=0.1, depth=hgt + rad * 0.8, location=(0, 0, (hgt + rad * 0.8) / 2))
    tr = bpy.context.active_object; tr.data.materials.append(MATS['tronco']); bpy.context.collection.objects.unlink(tr); col.objects.link(tr)
    for j in range(4):                                             # ramas
        a = j * 1.57 + 0.4
        bpy.ops.mesh.primitive_cone_add(radius1=0.09, radius2=0.03, depth=rad * 0.9,
                                        location=(math.cos(a) * rad * 0.25, math.sin(a) * rad * 0.25, hgt + 0.3),
                                        rotation=(0.9 * math.sin(a + 1.57) * -1, 0.9 * math.cos(a + 1.57) * 0, a))
        b = bpy.context.active_object; b.rotation_euler = (0, 0.9, a); b.data.materials.append(MATS['tronco'])
        bpy.context.collection.objects.unlink(b); col.objects.link(b)
    for j in range(9):
        ang = j * 2 * math.pi / 9 + random.random()
        rr = rad * (0.38 + random.random() * 0.3)
        cx, cy, cz = math.cos(ang) * rad * 0.55, math.sin(ang) * rad * 0.55, hgt + rad * (0.25 + random.random() * 0.55)
        if j == 0:
            cx, cy, cz, rr = 0, 0, hgt + rad * 0.85, rad * 0.62
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=rr, location=(cx, cy, cz))
        s = bpy.context.active_object
        d = s.modifiers.new('desp', 'DISPLACE'); tx_ = bpy.data.textures.new('nube%d%d' % (k, j), 'CLOUDS')
        tx_.noise_scale = 0.35; d.texture = tx_; d.strength = 0.7; d.texture_coords = 'GLOBAL'
        s.data.materials.append(MATS['hojas%d' % (1 + (k + j) % 3)])
        if not cerca:
            s.scale = (0.9, 0.9, 0.9); bpy.ops.object.shade_smooth()
            bpy.context.collection.objects.unlink(s); col.objects.link(s); continue
        s.data.materials[0] = MATS['hojas_int']; s.scale = (0.45, 0.45, 0.45)
        COPAS.setdefault(k, []).append(((cx, cy, cz), rr))
        bpy.ops.object.shade_smooth()
        bpy.context.collection.objects.unlink(s); col.objects.link(s); continue
        ps = s.modifiers.new('hojas', 'PARTICLE_SYSTEM').particle_system.settings
        ps.type = 'HAIR'; ps.count = int(2600 * rr ** 2); ps.hair_length = 0.3; ps.render_type = 'OBJECT'; ps.instance_object = HOJA
        ps.particle_size = 1.0; ps.size_random = 0.5; ps.use_rotations = True; ps.rotation_mode = 'NOR'
        ps.phase_factor_random = 2.0; ps.rotation_factor_random = 0.6; ps.use_advanced_hair = True
        s.scale = (0.9, 0.9, 0.9)
        bpy.ops.object.shade_smooth()
        bpy.context.collection.objects.unlink(s); col.objects.link(s)
    PROTO.append(col)
CPROTO = coleccion('Prototipos (fuera del terreno)')
for k, col in enumerate(PROTO):                                   # en la escena para que se calculen las hojas
    CPROTO.children.link(col)
    off = Vector((k * 25.0, -1500.0, -60.0))
    for o in col.objects:
        if o.parent is None:
            o.location = o.location + off
    col.instance_offset = off
_cen = sum((v.co for v in HOJA.data.vertices), Vector()) / len(HOJA.data.vertices)
hv = [v.co - _cen for v in HOJA.data.vertices]; hf = [list(p.vertices) for p in HOJA.data.polygons]
from mathutils import Quaternion
rl = random.Random(5)
for k, col in enumerate(PROTO[:4]):                                # follaje: hojas sueltas en el volumen de cada copa
    off = col.instance_offset; vs, fs = [], []
    for (c, rr) in COPAS.get(k, []):
        n = int(3200 * rr ** 2)
        for _ in range(n):
            d = Vector((rl.gauss(0, 1), rl.gauss(0, 1), rl.gauss(0, 1))).normalized()
            r = rr * (0.62 + 0.45 * rl.random() ** 0.6)
            pos = Vector(c) + off + d * r
            q = Quaternion((rl.gauss(0, 1), rl.gauss(0, 1), rl.gauss(0, 1), rl.gauss(0, 1))).normalized()
            sz = rl.uniform(0.75, 1.45)
            M = Matrix.Translation(pos) @ q.to_matrix().to_4x4() @ Matrix.Scale(sz, 4)
            b0 = len(vs); vs += [tuple(M @ cc) for cc in hv]; fs += [tuple(b0 + i for i in f_) for f_ in hf]
    me = bpy.data.meshes.new('follaje'); me.from_pydata(vs, [], fs); me.update()
    ob = bpy.data.objects.new('follaje', me); col.objects.link(ob); ob.data.materials.append(HOJA.data.materials[0])
    print('follaje', col.name, len(fs))
POS_ARBOLES = [tuple(p) for p in D['arboles']]
POS_ARBOLES += [(6.0, 52), (6.0, 60), (6.0, 68), (2.5, 46), (66, 33), (66, 45), (66, 56), (66, 70), (66, 82),
                (28, 60), (29, 90), (52, 90), (48.5, 114), (60, 112), (28.8, 18.8), (58, 19.3)]
rng = random.Random(3)
for _ in range(1400):                                               # vegetación del entorno
    r_ = 20 + rng.random() ** 0.7 * 520; a_ = rng.uniform(0, 6.283)
    x = 36 + r_ * math.cos(a_); y = 75 + r_ * math.sin(a_)
    if 4 < y < 20 or (-6 < x < 78 and 14 < y < 138):
        continue
    POS_ARBOLES.append((x, y))
for i, (x, y) in enumerate(POS_ARBOLES):
    lejos = math.hypot(x - 36, y - 75) > 95
    e = bpy.data.objects.new('arbol', None); e.instance_type = 'COLLECTION'; e.instance_collection = PROTO[i % 4 + (4 if lejos else 0)]
    e.location = (x, y, 0); e.rotation_euler = (0, 0, rng.uniform(0, 6.28)); s = rng.uniform(0.85, 1.35); e.scale = (s, s, s)
    CA.objects.link(e)
for i, p_ in enumerate(JARD_ARB):                                   # arbolitos de las jardineras OC-01
    e = bpy.data.objects.new('arbol_jardinera', None); e.instance_type = 'COLLECTION'; e.instance_collection = PROTO[i % 4]
    e.location = p_; e.rotation_euler = (0, 0, rng.uniform(0, 6.28)); e.scale = (0.34, 0.34, 0.34); CA.objects.link(e)

# ------------------------------------------------------------------ pasto en 3D (matas de hojas instanciadas)
from shapely.geometry import Polygon as SPoly, box as SBox, Point as SPt
from shapely.ops import unary_union
CG = coleccion('Pasto')
mg = bpy.data.materials.new('pasto_hoja'); mg.use_nodes = True; Ng = mg.node_tree.nodes; Lg = mg.node_tree.links
pg = Ng['Principled BSDF']; oig = Ng.new('ShaderNodeObjectInfo'); crg = Ng.new('ShaderNodeValToRGB')
crg.color_ramp.elements[0].color = rgb(58, 86, 30); crg.color_ramp.elements[1].color = rgb(128, 150, 62)
el = crg.color_ramp.elements.new(0.85); el.color = rgb(150, 140, 80)                  # algunas hojas secas
Lg.new(oig.outputs['Random'], crg.inputs['Fac'])
grd = Ng.new('ShaderNodeTexCoord'); sepg = Ng.new('ShaderNodeSeparateXYZ'); Lg.new(grd.outputs['Generated'], sepg.inputs['Vector'])
mixg = Ng.new('ShaderNodeMix'); mixg.data_type = 'RGBA'; mixg.blend_type = 'MULTIPLY'
mrg = Ng.new('ShaderNodeMapRange'); mrg.inputs['To Min'].default_value = 0.35; mrg.inputs['To Max'].default_value = 1.0
Lg.new(sepg.outputs['Z'], mrg.inputs['Value']); cmbg = Ng.new('ShaderNodeCombineColor')
for i in range(3):
    Lg.new(mrg.outputs['Result'], cmbg.inputs[i])
Lg.new(crg.outputs['Color'], mixg.inputs[6]); Lg.new(cmbg.outputs['Color'], mixg.inputs[7]); mixg.inputs[0].default_value = 1
Lg.new(mixg.outputs[2], pg.inputs['Base Color'])
pg.inputs['Roughness'].default_value = 0.5; pg.inputs['Subsurface Weight'].default_value = 0.0
pg.inputs['Subsurface Radius'].default_value = (0.1, 0.3, 0.05)
# mata de 14 hojas curvas
rg = random.Random(11); vs = []; fs = []
for k in range(14):
    a = rg.uniform(0, 6.283); r0 = rg.uniform(0, 0.05); h = rg.uniform(0.09, 0.2); w = rg.uniform(0.004, 0.007)
    inc = rg.uniform(0.02, 0.09); bx, by = math.cos(a) * r0, math.sin(a) * r0; dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    base = len(vs)
    for j in range(4):
        t = j / 3.0; ww = w * (1 - t * 0.9)
        cx_, cy_, cz_ = bx + dx * inc * t * t, by + dy * inc * t * t, h * t
        vs += [(cx_ - px * ww, cy_ - py * ww, cz_), (cx_ + px * ww, cy_ + py * ww, cz_)]
    for j in range(3):
        fs.append((base + 2 * j, base + 2 * j + 1, base + 2 * j + 3, base + 2 * j + 2))
mata = obj_mesh('mata_pasto', [(x, y, z - 500) for x, y, z in vs], fs, mg, CG)
mata.data.materials[0] = mg
for v in mata.data.vertices:
    v.co.z += 500
mata.location = (0, -800, 0)
duro = [SBox(e['rect'][0] + 0.25, e['rect'][1] + 0.25, e['rect'][2] - 0.25, e['rect'][3] - 0.25) for e in D['edificios']]
duro += [SPoly(p).buffer(0.05) for p in D['veredas'] if len(p) >= 3]
for k in ('losa', 'garita', 'autos', 'motos', 'tanque', 'plaza', 'oc04', 'asta'):
    r_ = D[k]; duro.append(SBox(r_[0] - 0.3, r_[1] - 0.3, r_[2] + 0.3, r_[3] + 0.3))
duro = unary_union([g.buffer(0) for g in duro])
from shapely.geometry import LineString as _SL                       # sin pasto sobre las cunetas
duro = duro.union(unary_union([_SL(p_).buffer(0.32, cap_style=2, join_style=2) for p_ in D['ejes_cuneta'].values()]))
lote_ = SPoly(D['limite']).convex_hull
zonas = [VERDES.buffer(-0.05).difference(duro), SBox(-45, -30, 120, 6.6), SBox(-45, 18.2, 1.0, 80), SBox(71.9, 18.2, 110, 80)]


def emisor(nombre, zona, paso=0.5, z=0.0):
    x0_, y0_, x1_, y1_ = zona.bounds; vs = []; fs = []; idx = {}
    nx_, ny_ = int((x1_ - x0_) / paso) + 1, int((y1_ - y0_) / paso) + 1
    for i in range(nx_):
        for j in range(ny_):
            cx_, cy_ = x0_ + (i + 0.5) * paso, y0_ + (j + 0.5) * paso
            if not zona.contains(SPt(cx_, cy_)):
                continue
            q = []
            for (a, b) in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
                if (a, b) not in idx:
                    idx[(a, b)] = len(vs); vs.append((x0_ + a * paso, y0_ + b * paso, 0.0))
                q.append(idx[(a, b)])
            fs.append(tuple(q))
    o = obj_mesh(nombre, vs, fs, 'pasto', CG)
    area = len(fs) * paso * paso
    ps_ = o.modifiers.new('pasto', 'PARTICLE_SYSTEM').particle_system.settings
    ps_.type = 'HAIR'; ps_.count = int(area * 34); ps_.hair_length = 0.2; ps_.render_type = 'OBJECT'; ps_.instance_object = mata
    ps_.particle_size = 1.0; ps_.size_random = 0.45; ps_.use_rotations = True; ps_.rotation_mode = 'GLOB_Z'
    ps_.phase_factor_random = 2.0; ps_.rotation_factor_random = 0.08; ps_.use_even_distribution = True; ps_.emit_from = 'FACE'
    o.show_instancer_for_render = False
    o.location.z = z
    return area


print('zonas', [round(z.area) for z in zonas])
tot = sum(emisor('pasto_%d' % i, z) for i, z in enumerate(zonas) if not z.is_empty)
print('pasto m2', round(tot))
for i_, zj in enumerate(JARD):
    emisor('pasto_jardinera_%d' % i_, zj, paso=0.15, z=0.455)

# ------------------------------------------------------------------ personas
CP = coleccion('Personas')
PERS = {}


def importa(nombre, archivo, accion=None, frame=None, alto=1.68):
    col = bpy.data.collections.new('persona_' + nombre)
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(A, archivo))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    for o in nuevos:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
    for o in list(nuevos):                                     # esfera auxiliar del esqueleto (forma de hueso): fuera
        if o.type == 'MESH' and o.name.startswith('Icosphere') and not o.modifiers:
            bpy.data.objects.remove(o); nuevos.remove(o)
    raiz = [o for o in nuevos if o.parent is None]
    arm = [o for o in nuevos if o.type == 'ARMATURE']
    if arm and accion:
        ac = next((a for a in bpy.data.actions if a.name.startswith(accion)), None)
        if ac:
            arm[0].animation_data_create(); arm[0].animation_data.action = ac
    bpy.context.view_layer.update()
    zs = []
    for o in nuevos:
        if o.type == 'MESH':
            for v in o.bound_box:
                zs.append((o.matrix_world @ Vector(v)).z)
    h = (max(zs) - min(zs)) if zs else 1
    for r in raiz:
        r.scale = tuple(s * alto / h for s in r.scale)
    PERS[nombre] = col
    return col


try:
    importa('mujer', 'Michelle.glb', 'SambaDance', alto=1.62)
    importa('hombre', 'readyplayer.me.glb', None, alto=1.72)
    importa('maniqui', 'Xbot.glb', 'idle', alto=1.70)
    importa('caminante', 'CesiumMan.glb', 'Anim_0', alto=1.70)
except Exception as ex:
    print('personas: error', ex)
for o in bpy.data.objects:                                       # ropa del maniquí en colores
    if o.name.startswith('Beta_Surface'):
        m = mat_simple('ropa_maniqui', rgb(60, 90, 140), rug=0.6); o.data.materials.clear(); o.data.materials.append(m)
GENTE = [('mujer', 1.0, (38, 21, 0.15), 200), ('hombre', 1.0, (36, 19.6, 0.15), 160), ('mujer', 0.72, (37, 20.2, 0.15), 190),
         ('maniqui', 1.0, (33, 40, 0.15), 90), ('mujer', 1.0, (31, 58, 0.12), 30), ('caminante', 1.0, (35, 62, 0.12), 210),
         ('mujer', 0.66, (32.2, 82.6, 0.13), 10), ('maniqui', 0.62, (36.4, 81.2, 0.13), 160), ('mujer', 0.7, (38.6, 83.4, 0.13), 300),
         ('hombre', 0.65, (12, 105, 0.13), 40), ('maniqui', 0.68, (16, 112, 0.13), 200), ('mujer', 0.7, (19, 100, 0.13), 120),
         ('caminante', 0.66, (9, 118, 0.13), 300), ('mujer', 1.0, (5, 98, 0.12), 80), ('hombre', 1.0, (42, 50, 0.10), 250),
         ('mujer', 1.0, (52, 92.5, 0.10), 180), ('maniqui', 1.0, (61, 110, 0.10), 270), ('mujer', 0.7, (28.3, 64, 0.12), 60),
         ('caminante', 1.0, (20, 47, 0.10), 0), ('mujer', 1.0, (39, 16.3, 0.16), 100),
         ('mujer', 0.62, (33.6, 81.0, 0.13), 200), ('maniqui', 0.58, (40.9, 82.6, 0.13), 250), ('hombre', 0.6, (36.5, 86.9, 0.13), 140),
         ('mujer', 1.0, (29.2, 78.6, 0.13), 70), ('mujer', 0.66, (14, 108, 0.13), 260), ('caminante', 0.6, (18, 117, 0.13), 110),
         ('maniqui', 0.64, (10, 101, 0.13), 30), ('mujer', 1.0, (24.8, 110, 0.13), 270), ('mujer', 0.95, (34.5, 64.5, 0.12), 300),
         ('hombre', 0.95, (31.5, 60.5, 0.12), 80), ('mujer', 0.68, (35.6, 59.2, 0.12), 20), ('mujer', 1.0, (58.5, 60, 0.12), 180),
         ('caminante', 1.0, (49, 46, 0.10), 230), ('mujer', 0.7, (50.0, 45.2, 0.10), 220), ('mujer', 1.0, (27.5, 41, 0.12), 90)]
for i, (n, s, p, r) in enumerate([]):                               # sin personas (pedido del usuario, 02-11-2026)
    if n not in PERS:
        continue
    e = bpy.data.objects.new('persona', None); e.instance_type = 'COLLECTION'; e.instance_collection = PERS[n]
    e.location = p; e.rotation_euler = (0, 0, math.radians(r)); e.scale = (s, s, s); CP.objects.link(e)

# ------------------------------------------------------------------ cielo, sol y render
w = bpy.data.worlds.new('cielo'); sc.world = w; w.use_nodes = True
N = w.node_tree.nodes; Lk = w.node_tree.links
sky = N.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(215)
sky.altitude = 150; sky.air_density = 1.0; sky.dust_density = 0.6; sky.ozone_density = 1.4; sky.sun_intensity = 0.55
bg = N['Background']; Lk.new(sky.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 0.22
bg2 = N.new('ShaderNodeBackground'); Lk.new(sky.outputs['Color'], bg2.inputs['Color']); bg2.inputs['Strength'].default_value = 0.5
lp = N.new('ShaderNodeLightPath'); ms = N.new('ShaderNodeMixShader')
Lk.new(lp.outputs['Is Camera Ray'], ms.inputs['Fac']); Lk.new(bg.outputs['Background'], ms.inputs[1]); Lk.new(bg2.outputs['Background'], ms.inputs[2])
Lk.new(ms.outputs['Shader'], N['World Output'].inputs['Surface'])
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 64; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 5; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transparent_max_bounces = 2
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03; sc.cycles.use_light_tree = True
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'; sc.view_settings.exposure = -1.9
sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.render.film_transparent = False
sc.view_layers[0].use_pass_mist = True
w.mist_settings.start = 60; w.mist_settings.depth = 900; w.mist_settings.falloff = 'QUADRATIC'
sc.use_nodes = True; T = sc.node_tree; T.nodes.clear()
rl = T.nodes.new('CompositorNodeRLayers'); mx = T.nodes.new('CompositorNodeMixRGB'); co = T.nodes.new('CompositorNodeComposite')
mx.inputs[2].default_value = (0.30, 0.36, 0.44, 1)
mm = T.nodes.new('CompositorNodeMath'); mm.operation = 'MULTIPLY'; mm.inputs[1].default_value = 0.55
T.links.new(rl.outputs['Mist'], mm.inputs[0]); T.links.new(mm.outputs[0], mx.inputs[0])
T.links.new(rl.outputs['Image'], mx.inputs[1]); T.links.new(mx.outputs[0], co.inputs['Image'])
sc.frame_set(28)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, 'refugio.blend'))
print('escena guardada', len(bpy.data.objects), 'objetos')
