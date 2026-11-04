# -*- coding: utf-8 -*-
"""Modelo 3D del Hogar de Refugio Temporal (CUI 2675514) en Blender, a partir de la planta general y las elevaciones de la
arquitecta (escena.json) y de las edificaciones leídas de los planos (edificaciones_revit.json, de lee_edificaciones.py). Colores de muros: TP-1 RGB 123-31-45, TP-2 RGB 125-133-139, TP-3 RAL 9010."""
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
    p.inputs['Base Color'].default_value = rgb(188, 191, 194); p.inputs['Metallic'].default_value = 0.6
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


def mat_imagen(nombre, ruta, escala, rug=0.9, tinte=None, bump=0.2, sin_cuadricula=False):
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (escala, escala, escala)
    Lk.new(tc.outputs['Object'], mp.inputs['Vector'])
    im = N.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(ruta)
    Lk.new(mp.outputs['Vector'], im.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.08
    Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    col_ = im.outputs['Color']
    if sin_cuadricula:                                                 # segunda capa girada y a otra escala, mezclada por manchas
        mp2 = N.new('ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (escala * 0.61, escala * 0.61, escala * 0.61)
        mp2.inputs['Rotation'].default_value = (0, 0, 0.65); Lk.new(tc.outputs['Object'], mp2.inputs['Vector'])
        im2 = N.new('ShaderNodeTexImage'); im2.image = im.image; Lk.new(mp2.outputs['Vector'], im2.inputs['Vector'])
        nm = N.new('ShaderNodeTexNoise'); nm.inputs['Scale'].default_value = 0.17; nm.inputs['Detail'].default_value = 6
        Lk.new(tc.outputs['Object'], nm.inputs['Vector'])
        rm = N.new('ShaderNodeValToRGB'); rm.color_ramp.elements[0].position = 0.42; rm.color_ramp.elements[1].position = 0.58
        Lk.new(nm.outputs['Fac'], rm.inputs['Fac'])
        mc = N.new('ShaderNodeMix'); mc.data_type = 'RGBA'; Lk.new(rm.outputs['Color'], mc.inputs[0])
        Lk.new(im.outputs['Color'], mc.inputs[6]); Lk.new(im2.outputs['Color'], mc.inputs[7])
        hs = N.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = 0.72; hs.inputs['Value'].default_value = 0.86
        Lk.new(mc.outputs[2], hs.inputs['Color']); col_ = hs.outputs['Color']
    Lk.new(col_, mix.inputs[6])
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
mat_imagen('pasto', os.path.join(A, 'grasslight-big.jpg'), 0.22, tinte=((0.42, 0.50, 0.30, 1), (0.85, 0.88, 0.72, 1)), bump=0.5, sin_cuadricula=True)
MATS['pasto'].node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.15
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
PTAR_R = (63.205, 56.844, 70.205, 78.669)                              # recinto PTAR: tierra o hierba, sin piso de concreto (usuaria, 03-11-2026)
D['veredas'] = [p_ for p_ in D['veredas'] if not (len(p_) >= 3 and abs(min(q_[0] for q_ in p_) - PTAR_R[0]) < 0.1 and abs(max(q_[1] for q_ in p_) - PTAR_R[3]) < 0.1)]
for i, pol in enumerate(D['veredas']):
    prisma('vereda_%d' % i, pol, 0.0, 0.10 + 0.002 * i, 'vereda', CT)
from shapely.geometry import Polygon as _SP, box as _SB, Point as _Pt
from shapely.ops import unary_union as _UU
from shapely.geometry.polygon import orient as _orient
VERDES = _UU([_SP(e_, i_).buffer(0) for e_, i_ in D['verdes']] + [_SB(*PTAR_R)])
LOTE = _SB(1.05, 18.0, 71.76, 131.21)
mat_concreto('pavimento', (186, 182, 174), agregado=0.12, juntas=1.5)
_vs, _fs, _ix = [], [], {}
_p = 0.5
for _i in range(int((LOTE.bounds[2] - LOTE.bounds[0]) / _p) + 1):
    for _j in range(int((LOTE.bounds[3] - LOTE.bounds[1]) / _p) + 1):
        _cx, _cy = LOTE.bounds[0] + (_i + 0.5) * _p, LOTE.bounds[1] + (_j + 0.5) * _p
        if _cx > LOTE.bounds[2] or _cy > LOTE.bounds[3]:
            continue
        _x0, _y0 = LOTE.bounds[0] + _i * _p, LOTE.bounds[1] + _j * _p
        _cel = _SB(_x0, _y0, _x0 + _p, _y0 + _p).difference(VERDES)    # recortada al contorno exacto del área verde (bordes diagonales del plano)
        if _cel.area < 1e-6:
            continue
        if _cel.area < _p * _p - 1e-6:
            for _g in getattr(_cel, 'geoms', [_cel]):
                if _g.geom_type == 'Polygon' and _g.area > 1e-6:
                    _ext = list(_orient(_g).exterior.coords)[:-1]
                    _fs.append(tuple(range(len(_vs), len(_vs) + len(_ext)))); _vs += [(x_, y_, 0.08) for x_, y_ in _ext]
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
# Leídas de los planos de la arquitecta por lee_edificaciones.py (edificaciones_revit.json, el mismo dato del modelo Revit):
# muros reales exteriores e interiores con su espesor hasta el fondo de viga, vigas TP-1 al nivel de los cortes, columnas con
# su sección, puertas y ventanas en su vano con el ancho, alto y alféizar del cuadro de vanos de los DT, sobreluces, cubiertas
# con el contorno de la PG-02 (pendiente 30 %), hastiales TP-3, nave alta del SUM y sobretecho con celosías de la administración.
CE = coleccion('Edificaciones')
VOL = 1.5                                                           # alero medio (solo para las piezas que aún lo usan)
ER = {m['cod']: m for m in json.load(open(os.path.join(AQUI, 'edificaciones_revit.json'), encoding='utf-8'))['edificios']}
PEND = 0.30


class Malla:
    """Acumula cajas por material y crea un solo objeto por material (muchos muros y vanos sin miles de objetos)."""
    def __init__(self, nombre, col):
        self.nombre, self.col, self.d = nombre, col, {}

    def caja(self, mat, x0, y0, z0, x1, y1, z1):
        if x1 - x0 < 1e-4 or y1 - y0 < 1e-4 or z1 - z0 < 1e-4:
            return
        vs, fs = self.d.setdefault(mat, ([], [])); i = len(vs)
        vs.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
        fs.extend([(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7), (i, i + 1, i + 5, i + 4), (i + 1, i + 2, i + 6, i + 5),
                   (i + 2, i + 3, i + 7, i + 6), (i + 3, i, i + 4, i + 7)])

    def placa(self, mat, pts, esp):
        """Placa plana (polígono convexo en un plano vertical) con espesor, centrada en el plano."""
        p = [Vector(q) for q in pts]
        n = (p[1] - p[0]).cross(p[2] - p[1])
        if n.length < 1e-6:
            n = (p[2] - p[0]).cross(p[3] - p[0])
        n.normalize(); vs, fs = self.d.setdefault(mat, ([], [])); i = len(vs); k = len(p)
        vs.extend([tuple(q - n * esp / 2) for q in p] + [tuple(q + n * esp / 2) for q in p])
        fs.append(tuple(range(i + k - 1, i - 1, -1))); fs.append(tuple(range(i + k, i + 2 * k)))
        for j in range(k):
            fs.append((i + j, i + (j + 1) % k, i + k + (j + 1) % k, i + k + j))

    def crear(self):
        for mat, (vs, fs) in self.d.items():
            o = obj_mesh('%s_%s' % (self.nombre, mat), vs, fs, mat, self.col)
            me = o.data; me.validate(); me.update()


def anfitrion(muros, v):
    mejor = None
    for i, w in enumerate(muros):
        h = abs(w[1] - w[3]) < 1e-6
        if (v['o'] == 'H') != h:
            continue
        d, c, a, b = (abs(w[1] - v['y']), v['x'], min(w[0], w[2]), max(w[0], w[2])) if h else (abs(w[0] - v['x']), v['y'], min(w[1], w[3]), max(w[1], w[3]))
        if d < 0.06 and a - 0.01 <= c - v['ancho'] / 2 and c + v['ancho'] / 2 <= b + 0.01 and (mejor is None or d < mejor[0]):
            mejor = (d, i)
    return None if mejor is None else mejor[1]


def restar(intervalos, a, b):
    """Intervalos (z0, z1) menos [a, b]."""
    out = []
    for z0, z1 in intervalos:
        if b <= z0 or a >= z1:
            out.append((z0, z1)); continue
        if a > z0: out.append((z0, a))
        if b < z1: out.append((b, z1))
    return out


def edificio(m):
    cod = m['cod']; col = coleccion(cod); M = Malla(cod, col); npt = m['npt']
    wx0, wy0, wx1, wy1 = m['contorno_muros']; cxm, cym = (wx0 + wx1) / 2, (wy0 + wy1) / 2
    p_ = m['piso']; M.caja('vereda', p_[0], p_[1], 0, p_[2], p_[3], npt)
    vanos = {}
    for tipo, lst in (('p', m['puertas']), ('v', m['ventanas'])):
        for v in lst:
            i = anfitrion(m['muros'], v)
            if i is not None:
                vanos.setdefault(i, []).append((tipo, v))
    for i, (x0, y0, x1, y1, esp, z0, z1, ext) in enumerate(m['muros']):
        fondo = m['vigas'][i][5]; h = abs(y0 - y1) < 1e-6
        c = y0 if h else x0; s0, s1 = sorted((x0, x1)) if h else sorted((y0, y1))
        sal = (1 if c > (cym if h else cxm) else -1)                  # lado exterior del muro (hacia afuera de la edificación)
        B = (lambda a, b, t0, t1, za, zb, mat: M.caja(mat, a, c + t0, za, b, c + t1, zb)) if h else \
            (lambda a, b, t0, t1, za, zb, mat: M.caja(mat, c + t0, a, za, c + t1, b, zb))
        huecos = []                                                   # (s0, s1, z0, z1) de cada vano en este muro
        for tipo, v in vanos.get(i, []):
            s = v['x'] if h else v['y']; a, b = s - v['ancho'] / 2, s + v['ancho'] / 2
            zt = min(v['sill'] + v['alto'], fondo)
            if tipo == 'p':
                ztop = fondo if (v['sobreluz'] and fondo - zt > 0.2) else zt
                huecos.append((a, b, z0, ztop))
                mat_h = 'vidrio' if v['vidrio'] else 'puerta'
                B(a, b, -0.02, 0.02, z0, zt, mat_h)                        # hoja
                for (aa, bb, za, zb) in ((a, a + 0.05, z0, zt), (b - 0.05, b, z0, zt), (a, b, zt - 0.05, zt)):
                    B(aa, bb, -esp / 2, esp / 2, za, zb, 'aluminio' if v['vidrio'] else 'madera')
                if v['vidrio']:
                    B(s - 0.02, s + 0.02, -0.03, 0.03, z0, zt, 'aluminio')
                if ztop > zt:                                                # sobreluz fija
                    B(a, b, -0.01, 0.01, zt, ztop, 'vidrio')
                    B(a, b, -0.03, 0.03, ztop - 0.04, ztop, 'aluminio')
            else:
                zs = v['sill']; huecos.append((a, b, zs, zt))
                B(a, b, -0.01, 0.01, zs, zt, 'vidrio')
                for (aa, bb, za, zb) in ((a, a + 0.05, zs, zt), (b - 0.05, b, zs, zt), (a, b, zs, zs + 0.05), (a, b, zt - 0.05, zt)):
                    B(aa, bb, -0.035, 0.035, za, zb, 'aluminio')
                n_ = max(1, int(round(v['ancho'] / 1.0)))                       # parantes de las hojas corredizas
                for k in range(1, n_):
                    sk = a + (b - a) * k / n_; B(sk - 0.025, sk + 0.025, -0.035, 0.035, zs, zt, 'aluminio')
                if v['alto'] > 1.2:                                          # travesaño
                    zm = zs + v['alto'] * 0.62; B(a, b, -0.03, 0.03, zm - 0.02, zm + 0.02, 'aluminio')
                if ext:                                                       # alféizar exterior
                    t0, t1 = (esp / 2, esp / 2 + 0.05) if sal > 0 else (-esp / 2 - 0.05, -esp / 2)
                    B(a - 0.03, b + 0.03, t0, t1, zs - 0.05, zs, 'concreto_gris')
        cortes = sorted({s0, s1} | {q for hh in huecos for q in hh[:2] if s0 < q < s1})
        for a, b in zip(cortes, cortes[1:]):                                   # muro en franjas verticales, sin los vanos
            llenos = [(z0, fondo)]
            for (ha, hb, za, zb) in huecos:
                if ha <= a + 1e-6 and b <= hb + 1e-6:
                    llenos = restar(llenos, za, zb)
            for za, zb in llenos:
                B(a, b, -esp / 2, esp / 2, za, zb, 'TP2')
    for (x0, y0, x1, y1, w_, z0, z1) in m['vigas']:
        if abs(y0 - y1) < 1e-6: M.caja('TP1', min(x0, x1), y0 - w_ / 2, z0, max(x0, x1), y0 + w_ / 2, z1)
        else: M.caja('TP1', x0 - w_ / 2, min(y0, y1), z0, x0 + w_ / 2, max(y0, y1), z1)
    for (x, y, b, h_, z0, z1) in m['columnas']:
        M.caja('TP1', x - b / 2 - 0.01, y - h_ / 2 - 0.01, z0, x + b / 2 + 0.01, y + h_ / 2 + 0.01, z1)
    for hp in m['hastiales']:
        M.placa('TP3', hp, 0.15)
    # cubiertas a dos aguas: borde del alero al nivel de viga, pendiente 30 %; cierre TP-3 sobre la viga en los muros largos
    for t in m['techos']:
        rx0, ry0, rx1, ry1 = t['rect']; base = t['base']; eje = t['eje']; e_ = 0.05
        if eje == 'y':
            xm = (rx0 + rx1) / 2; zr = base + PEND * (xm - rx0)
            v = [(rx0, ry0, base + e_), (xm, ry0, zr + e_), (xm, ry1, zr + e_), (rx0, ry1, base + e_), (rx1, ry0, base + e_), (rx1, ry1, base + e_)]
            f = [(0, 1, 2, 3), (1, 4, 5, 2)]
            to = obj_mesh(cod + '_techo', v, f, 'calamina_y', col)
            M.caja('aluminio_claro', xm - 0.2, ry0, zr + e_ - 0.01, xm + 0.2, ry1, zr + e_ + 0.05)
            if not t.get('sobretecho'):
                for xx in (rx0, rx1):
                    M.caja('canaleta_galv', xx - 0.12, ry0, base - 0.18, xx + 0.12, ry1, base + 0.02)
                ya, yb = max(ry0, wy0), min(ry1, wy1)
                for xw, xr in ((wx0 + 0.075, rx0), (wx1 - 0.075, rx1)):
                    M.caja('TP3', xw - 0.075, ya, base, xw + 0.075, yb, base + PEND * (abs(xw - xr) - 0.075) + 0.02)
        else:
            ym = (ry0 + ry1) / 2; zr = base + PEND * (ym - ry0)
            v = [(rx0, ry0, base + e_), (rx1, ry0, base + e_), (rx1, ym, zr + e_), (rx0, ym, zr + e_), (rx1, ry1, base + e_), (rx0, ry1, base + e_)]
            f = [(0, 1, 2, 3), (3, 2, 4, 5)]
            to = obj_mesh(cod + '_techo', v, f, 'calamina_x', col)
            M.caja('aluminio_claro', rx0, ym - 0.2, zr + e_ - 0.01, rx1, ym + 0.2, zr + e_ + 0.05)
            if not t.get('sobretecho'):
                for yy in (ry0, ry1):
                    M.caja('canaleta_galv', rx0, yy - 0.12, base - 0.18, rx1, yy + 0.12, base + 0.02)
                xa, xb = max(rx0, wx0), min(rx1, wx1)
                for yw, yr in ((wy0 + 0.075, ry0), (wy1 - 0.075, ry1)):
                    M.caja('TP3', xa, yw - 0.075, base, xb, yw + 0.075, base + PEND * (abs(yw - yr) - 0.075) + 0.02)
        mod = to.modifiers.new('esp', 'SOLIDIFY'); mod.thickness = e_
    # celosías del sobretecho (E-01): lamas horizontales TP-1 dentro de cada paño
    for pol in m['celosias']:
        xs = [q[0] for q in pol]; ys = [q[1] for q in pol]
        plano_y = max(ys) - min(ys) < 1e-3
        uz = _SP([((q[0] if plano_y else q[1]), q[2]) for q in pol]).buffer(0)
        u0, z0_, u1, z1_ = uz.bounds; c = ys[0] if plano_y else xs[0]
        z = z0_ + 0.04
        while z < z1_ - 0.06:
            g = uz.intersection(_SB(u0 - 1, z, u1 + 1, z + 0.05))
            if not g.is_empty:
                a, _, b, _ = g.bounds
                if plano_y: M.caja('TP1', a, c - 0.04, z, b, c + 0.04, z + 0.05)
                else: M.caja('TP1', c - 0.04, a, z, c + 0.04, b, z + 0.05)
            z += 0.11
    M.crear()


for e in D['edificios']:
    edificio(ER[e['cod']])

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


def mat_plancha(nombre, color):
    """Plancha metálica pintada (portones y paños del OE-01): llena, sin vanos, con nervaduras horizontales."""
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    p.inputs['Base Color'].default_value = color; p.inputs['Metallic'].default_value = 0.55; p.inputs['Roughness'].default_value = 0.42
    tc = N.new('ShaderNodeTexCoord'); w = N.new('ShaderNodeTexWave'); w.wave_type = 'BANDS'; w.bands_direction = 'Z'
    w.wave_profile = 'SAW'; w.inputs['Scale'].default_value = 1.6; Lk.new(tc.outputs['Object'], w.inputs['Vector'])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.35; bm.inputs['Distance'].default_value = 0.01
    Lk.new(w.outputs['Fac'], bm.inputs['Height']); Lk.new(bm.outputs['Normal'], p.inputs['Normal'])
    MATS[nombre] = m
    return m


mat_plancha('plancha_metalica', rgb(58, 60, 63))


def celosia(nombre, xa, xb, za, zb, y, paso=0.09):
    """Paño metálico lleno (sin rejilla), con marco."""
    caja(nombre, xa, y - 0.02, za, xb, y + 0.02, zb, 'plancha_metalica', CO)
    caja(nombre + '_marco', xa, y - 0.03, za, xb, y + 0.03, za + 0.04, 'negro', CO)
    caja(nombre + '_marco', xa, y - 0.03, zb - 0.04, xb, y + 0.03, zb, 'negro', CO)


def porton(nombre, xa, xb, zb, y, hojas=2):
    """Portón metálico de planchas llenas (sin rejas ni vanos), con marco de tubo y división de hojas."""
    ancho = (xb - xa) / hojas
    for h in range(hojas):
        a, b = xa + h * ancho + 0.01, xa + (h + 1) * ancho - 0.01
        caja(nombre + '_plancha', a + 0.04, y - 0.015, 0.09, b - 0.04, y + 0.015, zb - 0.04, 'plancha_metalica', CO)
        caja(nombre + '_m', a, y - 0.03, 0.05, b, y + 0.03, 0.1, 'negro', CO)
        caja(nombre + '_m', a, y - 0.03, zb - 0.05, b, y + 0.03, zb, 'negro', CO)
        caja(nombre + '_m', a, y - 0.03, 0.05, a + 0.05, y + 0.03, zb, 'negro', CO)
        caja(nombre + '_m', b - 0.05, y - 0.03, 0.05, b, y + 0.03, zb, 'negro', CO)
        caja(nombre + '_m', a, y - 0.03, zb / 2 - 0.025, b, y + 0.03, zb / 2 + 0.025, 'negro', CO)       # travesaño
        caja(nombre + '_manija', (b - 0.12 if h == 0 else a + 0.06), y - 0.06, 1.0, (b - 0.06 if h == 0 else a + 0.12), y - 0.03, 1.15, 'acero', CO)


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
fnt = bpy.data.fonts.load(next(f for f in ('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',   # Liberation Serif
                                            'C:/Windows/Fonts/timesi.ttf') if os.path.exists(f)))         # o Times New Roman
tx = bpy.data.curves.new('letrero', 'FONT'); tx.body = 'HOGAR DE REFUGIO TEMPORAL'; tx.font = fnt; tx.size = 0.52
tx.extrude = 0.025; tx.align_x = 'CENTER'; tx.align_y = 'CENTER'
lt = bpy.data.objects.new('letrero', tx); CO.objects.link(lt)
lt.location = ((gx0 + gx1) / 2, yf - 0.1, 5.52); lt.rotation_euler = (math.pi / 2, 0, 0)
lt.data.materials.append(MATS['aluminio_claro'])

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
    x0, y0, x1, y1 = e['rect']; a0, b0, a1, b1 = ER[e['cod']]['contorno_muros']; ze = ER[e['cod']]['techos'][0]['base']
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

# ------------------------------------------------------------------ OC-05 biohuerto (lámina OC-05, ubicada con la PG)
# Cerco de malla olímpica 9.60 x 25.85 con postes de tubo FºGº 2" a +1.50 y puerta PM de dos hojas al este; cobertura de
# vivero: 6 bóvedas de tubo (R 2.55, cuerda 4.05, flecha 1.00, clave +2.52) sobre 7 pórticos de 3 postes a +1.50, con malla
# raschel; 6 camas de 6.50 x 2.00 con hortalizas; piso de piedra laja (NPT +0.10).
CB = coleccion('Biohuerto')
EXTRAS_SIN_ARBOL = []                                               # otras coberturas exteriores (las agregan sus secciones)


def mat_malla(nombre, eje, paso=0.0508, hilo=0.12):
    """Malla olímpica (cocos de 2") como material con transparencia: rombos de alambre galvanizado."""
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    p.inputs['Base Color'].default_value = rgb(176, 180, 182); p.inputs['Metallic'].default_value = 0.85; p.inputs['Roughness'].default_value = 0.35
    tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Object'], sp.inputs['Vector'])
    h = sp.outputs['X'] if eje == 'x' else sp.outputs['Y']
    mx = []
    for signo in (1, -1):
        a = N.new('ShaderNodeMath'); a.operation = 'MULTIPLY_ADD'; Lk.new(h, a.inputs[0]); a.inputs[1].default_value = signo
        Lk.new(sp.outputs['Z'], a.inputs[2])
        b = N.new('ShaderNodeMath'); b.operation = 'DIVIDE'; Lk.new(a.outputs[0], b.inputs[0]); b.inputs[1].default_value = paso
        f = N.new('ShaderNodeMath'); f.operation = 'FRACT'; Lk.new(b.outputs[0], f.inputs[0])
        c = N.new('ShaderNodeMath'); c.operation = 'LESS_THAN'; Lk.new(f.outputs[0], c.inputs[0]); c.inputs[1].default_value = hilo
        mx.append(c)
    s_ = N.new('ShaderNodeMath'); s_.operation = 'MAXIMUM'; Lk.new(mx[0].outputs[0], s_.inputs[0]); Lk.new(mx[1].outputs[0], s_.inputs[1])
    Lk.new(s_.outputs[0], p.inputs['Alpha'])
    MATS[nombre] = m
    return m


def mat_raschel(nombre):
    """Malla raschel negra (sombra ~65 %): semitransparente, tejido fino."""
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    p.inputs['Base Color'].default_value = rgb(28, 30, 30); p.inputs['Roughness'].default_value = 0.8
    tc = N.new('ShaderNodeTexCoord'); w = N.new('ShaderNodeTexWave'); w.wave_type = 'BANDS'; w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 60; Lk.new(tc.outputs['Object'], w.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.55; mr.inputs['To Max'].default_value = 0.8
    Lk.new(w.outputs['Fac'], mr.inputs['Value']); Lk.new(mr.outputs['Result'], p.inputs['Alpha'])
    MATS[nombre] = m
    return m


mat_malla('malla_x', 'x'); mat_malla('malla_y', 'y'); mat_raschel('raschel')
mat_concreto('piedra_laja', (150, 140, 124), escala=1.6, agregado=0.35, juntas=0.45)
mat_concreto('tierra_cultivo', (78, 58, 40), escala=14.0, agregado=0.4)
mat_hojas('hortaliza', rgb(60, 120, 40), rgb(130, 170, 70))
BX0, BY0, BX1, BY1 = 2.71, 48.775, 12.31, 74.625; ZB = 0.10


def curva(nombre, pts, r, mat, col=CB):
    cv = bpy.data.curves.new(nombre, 'CURVE'); cv.dimensions = '3D'; sp = cv.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, q in enumerate(pts):
        sp.points[i].co = (q[0], q[1], q[2], 1)
    cv.bevel_depth = r; cv.bevel_resolution = 2
    o = bpy.data.objects.new(nombre, cv); col.objects.link(o); o.data.materials.append(MATS[mat])
    return o


caja('bio_piso', BX0, BY0, 0.0, BX1, BY1, ZB, 'piedra_laja', CB)
for k in range(6):                                                    # camas de cultivo y hortalizas en hileras
    ya = 50.73 + 4.0 * k
    caja('bio_cama', 4.26, ya, ZB, 10.76, ya + 2.0, ZB + 0.12, 'tierra_cultivo', CB)
    for i in range(13):
        for j in range(4):
            cx, cy = 4.5 + i * 0.5, ya + 0.3 + j * 0.47
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.13 + 0.05 * ((i * 7 + j * 3 + k) % 3) / 2, location=(cx, cy, ZB + 0.18))
            o = bpy.context.active_object; o.name = 'bio_hortaliza'; o.scale = (1, 1, 0.65)
            o.data.materials.append(MATS['hortaliza']); bpy.context.collection.objects.unlink(o); CB.objects.link(o)
# cerco: postes 2" a +1.50 con dado, paños de malla con marco de ángulo de +0.20 a +1.45
PX = [2.79, 5.14, 7.49, 9.88, 12.23]; PY = [48.85, 51.74, 54.59, 57.44, 60.29, 63.14, 65.99, 68.84, 71.69, 74.54]
postes = {(x, y) for x in (2.79, 12.23) for y in PY} | {(x, y) for y in (48.85, 74.54) for x in PX}
for (x, y) in postes:
    caja('bio_dado', x - 0.1, y - 0.1, 0.0, x + 0.1, y + 0.1, 0.2, 'concreto_gris', CB)
    tubo('bio_poste', (x, y, 0.2), (x, y, 1.60), 0.03, 'galvanizado', CB)
for lado in ('O', 'E', 'S', 'N'):
    if lado in ('O', 'E'):
        xx = 2.79 if lado == 'O' else 12.23
        for ya, yb in zip(PY, PY[1:]):
            if lado == 'E' and yb <= 51.74:                               # vano de la puerta PM (y 49.05 a 51.55)
                continue
            caja('bio_malla', xx - 0.004, ya + 0.05, 0.2, xx + 0.004, yb - 0.05, 1.55, 'malla_y', CB)
            for zz in (0.2, 1.55):
                caja('bio_marco', xx - 0.015, ya + 0.04, zz - 0.015, xx + 0.015, yb - 0.04, zz + 0.015, 'galvanizado', CB)
    else:
        yy = 48.85 if lado == 'S' else 74.54
        for xa, xb in zip(PX, PX[1:]):
            caja('bio_malla', xa + 0.05, yy - 0.004, 0.2, xb - 0.05, yy + 0.004, 1.55, 'malla_x', CB)
            for zz in (0.2, 1.55):
                caja('bio_marco', xa + 0.04, yy - 0.015, zz - 0.015, xb - 0.04, yy + 0.015, zz + 0.015, 'galvanizado', CB)
for ya, yb in ((49.07, 50.15), (50.15, 51.53)):                       # puerta PM de dos hojas (tubo 1 1/2" + malla)
    caja('bio_puerta_malla', 12.226, ya + 0.04, 0.2, 12.234, yb - 0.04, 1.55, 'malla_y', CB)
    for zz in (0.18, 1.57):
        caja('bio_puerta_marco', 12.21, ya, zz - 0.02, 12.25, yb, zz + 0.02, 'galvanizado', CB)
    for yv in (ya, yb):
        caja('bio_puerta_marco', 12.21, yv - 0.02, 0.18, 12.25, yv + 0.02, 1.57, 'galvanizado', CB)
# vivero: 21 postes a +1.50, 18 arcos, correas y malla raschel sobre las 6 bóvedas
VX = [3.81, 7.52, 11.23]; VY = [49.72 + 4.0 * k for k in range(7)]
for x in VX:
    for y in VY:
        caja('vivero_dado', x - 0.2, y - 0.2, 0.0, x + 0.2, y + 0.2, ZB + 0.005, 'concreto_gris', CB)
        tubo('vivero_poste', (x, y, ZB), (x, y, ZB + 1.50), 0.03, 'galvanizado', CB)


def z_boveda(t):                                                      # t = distancia al centro de la bóveda (m)
    return ZB + 2.525 - 2.55 + math.sqrt(max(2.55 ** 2 - t * t, 0))


for k in range(6):
    yc = VY[k] + 2.0
    arco = [(0, yc + 2.025 * math.cos(math.pi * i / 16), 0) for i in range(17)]
    for x in VX:
        curva('vivero_arco', [(x, y, z_boveda(y - yc)) for _, y, _ in arco], 0.025, 'galvanizado')
    for dy in (-1.95, -1.2, -0.55, 0.0, 0.55, 1.2, 1.95):              # correas longitudinales (+1.50, +2.06, +2.40, +2.51)
        z = z_boveda(dy); tubo('vivero_correa', (3.76, yc + dy, z), (11.26, yc + dy, z), 0.017, 'galvanizado', CB)
    vs, fs = [], []                                                    # malla raschel sobre la bóveda
    for i in range(17):
        y = yc - 2.025 + 4.05 * i / 16; z = z_boveda(y - yc) + 0.03
        vs += [(3.76, y, z), (11.26, y, z)]
    for i in range(16):
        fs.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    obj_mesh('vivero_raschel', vs, fs, 'raschel', CB)
    for x in (3.76, 11.26):                                            # testeros de raschel (de +1.50 a la bóveda)
        pts = [(x, VY[k], ZB + 1.50)] + [(x, yc - 2.0 + 4.0 * i / 12, z_boveda(-2.0 + 4.0 * i / 12) + 0.02) for i in range(13)] + [(x, VY[k + 1], ZB + 1.50)]
        obj_mesh('vivero_raschel_testero', pts, [tuple(range(len(pts)))], 'raschel', CB)

# ------------------------------------------------------------------ OC-02 punto ecológico (4 unidades de la PG, lámina OC-02)
# Techo a cuatro aguas de aluzinc TR4 rojo teja 4.80 x 1.80 (alero +2.16, cumbrera +2.73 de 3.00), 2 postes 4"x4" negros a
# +2.60 separados 3.00, 4 tachos de Ø 0.60 x 0.905 en cuna: papel (celeste), orgánico (verde oscuro), plástico (naranja),
# vidrio (verde claro).
mat_simple('rojo_teja', rgb(150, 52, 38), rug=0.45, metal=0.5)
mat_simple('negro_ral9005', rgb(14, 14, 16), rug=0.4, metal=0.5)
for nom_, c_ in (('tacho_papel', (90, 170, 220)), ('tacho_organico', (26, 92, 44)), ('tacho_plastico', (236, 128, 30)), ('tacho_vidrio', (120, 190, 70))):
    mat_simple(nom_, rgb(*c_), rug=0.5, metal=0.1)
for (cx, cy, eje) in ((38.563, 46.555, 'x'), (38.44, 33.645, 'x'), (33.897, 110.377, 'y'), (47.067, 110.256, 'y')):
    U = (lambda u, v: (cx + u, cy + v)) if eje == 'x' else (lambda u, v: (cx + v, cy + u))
    z0 = 0.10
    for u in (-1.5, 1.5):
        x, y = U(u, 0); caja('ecologico_poste', x - 0.05, y - 0.05, z0, x + 0.05, y + 0.05, z0 + 2.60, 'negro_ral9005', CO)
        caja('ecologico_placa', x - 0.125, y - 0.125, z0, x + 0.125, y + 0.125, z0 + 0.012, 'negro_ral9005', CO)
    a, b = U(-1.5, -0.02), U(1.5, 0.02); caja('ecologico_barra', min(a[0], b[0]), min(a[1], b[1]), z0 + 0.43, max(a[0], b[0]), max(a[1], b[1]), z0 + 0.46, 'negro_ral9005', CO)
    for k, m_ in enumerate(('tacho_papel', 'tacho_organico', 'tacho_plastico', 'tacho_vidrio')):
        x, y = U(-1.05 + 0.70 * k, 0)
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.30, depth=0.905, location=(x, y, z0 + 0.215 + 0.4525))
        o = bpy.context.active_object; o.name = 'ecologico_tacho'; o.data.materials.append(MATS[m_]); bpy.ops.object.shade_smooth()
        bpy.context.collection.objects.unlink(o); CO.objects.link(o)
        caja('ecologico_cuna', x - 0.31, y - 0.31, z0 + 0.20, x + 0.31, y + 0.31, z0 + 0.23, 'negro_ral9005', CO)
    ze, zr = z0 + 2.16, z0 + 2.73                                       # techo a cuatro aguas
    P_ = [U(-2.4, -0.9), U(2.4, -0.9), U(2.4, 0.9), U(-2.4, 0.9), U(-1.5, 0), U(1.5, 0)]
    v = [(p[0], p[1], ze) for p in P_[:4]] + [(P_[4][0], P_[4][1], zr), (P_[5][0], P_[5][1], zr)]
    o = obj_mesh('ecologico_techo', v, [(0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)], 'rojo_teja', CO)
    o.modifiers.new('esp', 'SOLIDIFY').thickness = 0.03

# ------------------------------------------------------------------ OE-02 / OE-03 estacionamientos
# Cobertura de panel aluzinc TR4 e = 40 mm a una caída hacia el cerco, sobre tubos y columnas de concreto, con las plazas de la
# lámina y los vehículos de la PG (12 motos 1.20 x 2.40, 6 autos 2.50 x 5.00). Alturas = cota absoluta; piso +0.10.
CV = coleccion('Estacionamientos')
MV = Malla('estac', CV)
YC = 18.0                                                             # cara interior del cerco frontal
mat_calamina('aluzinc_tr4', 'X')
for n_ in MATS['aluzinc_tr4'].node_tree.nodes:
    if n_.type == 'TEX_WAVE':
        n_.inputs['Scale'].default_value = 2 * math.pi / (20 * 0.25)  # nervios del TR4 a 0.25 m
mat_concreto('piso_p05', (172, 169, 162), agregado=0.1)
mat_simple('bruna', rgb(92, 91, 88), rug=0.9)
mat_simple('panel_inferior', rgb(205, 207, 208), rug=0.55)


def lamina(nombre, x0, x1, perfil, mat, esp, col=CV):
    """Lámina barrida en x con un perfil (s, h); s = distancia al cerco."""
    fs = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(perfil) - 1)]
    o = obj_mesh(nombre, [(x, YC + s, h) for s, h in perfil for x in (x0, x1)], fs, mat, col); o.data.shade_smooth()
    inf = []
    for i, (s, h) in enumerate(perfil):                                # cara inferior, a esp bajo la superior
        a_, b_ = perfil[max(i - 1, 0)], perfil[min(i + 1, len(perfil) - 1)]
        ds, dh = b_[0] - a_[0], b_[1] - a_[1]; L_ = math.hypot(ds, dh)
        inf.append((s + esp * dh / L_, h - esp * ds / L_))
    obj_mesh(nombre + '_inf', [(x, YC + s, h) for s, h in inf for x in (x0, x1)], fs, 'panel_inferior', col).data.shade_smooth()
    pr = perfil + inf[::-1]                                            # cantos
    for x in (x0, x1):
        obj_mesh(nombre + '_canto', [(x, YC + s, h) for s, h in pr], [tuple(range(len(pr)))], 'panel_inferior', col)
    return o


def arco_pts(cs, ch, r, a0, a1, n):
    return [(cs + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), ch + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# --- motos (OE-02)
MX0, MX1 = 12.842, 27.442
MV.caja('piso_p05', MX0, YC, 0.0, MX1, 20.41, 0.10)
for k in range(13):
    x = 12.939 + 1.20 * k
    MV.caja('bruna', x - 0.006, YC, 0.10, x + 0.006, 20.41, 0.102)
MV.caja('concreto_gris', MX0, 22.87, 0.0, MX1, 22.98, 0.13)            # sardinel H = 0.10
CM_, HM_ = 1.211, 2.513                                               # centro de la curva de la cobertura
TG10 = math.tan(math.radians(10))


def perfil_moto(r, s_fin):
    """Faldón o tubo vertical + curva de radio r + recta al 17.6 %, concéntricos."""
    a_ = arco_pts(CM_, HM_, r, 180, 100, 14)
    return a_ + [(s_fin, a_[-1][1] + TG10 * (s_fin - a_[-1][0]))]


lamina('motos_cobertura', MX0, MX1, [(0.0, 1.58)] + perfil_moto(1.211, 2.908), 'aluzinc_tr4', 0.04)
for x in (12.842, 15.742, 18.642, 21.542, 24.442, 27.242):             # columna 0.20 x 0.20 a +1.30 y tubo Ø 3"
    MV.caja('TP1', x, 18.069, 0.10, x + 0.20, 18.269, 1.30)
    t_ = perfil_moto(1.0445, 2.88)
    curva('motos_tubo', [(x + 0.10, YC + t_[0][0], 1.30)] + [(x + 0.10, YC + s, h) for s, h in t_], 0.0381, 'acero', CV)
p_ = perfil_moto(1.15, 2.93)
for sc_ in (0.23, 0.56, 1.03, 1.62, 2.21, 2.80):                       # 6 correas de la planta
    h_ = next(p_[i][1] + (p_[i + 1][1] - p_[i][1]) * (sc_ - p_[i][0]) / (p_[i + 1][0] - p_[i][0]) for i in range(len(p_) - 1) if p_[i][0] <= sc_ <= p_[i + 1][0])
    tubo('motos_correa', (MX0, YC + sc_, h_), (MX1, YC + sc_, h_), 0.0254, 'acero', CV)

# --- autos (OE-03): la cobertura es un arco convexo de R 15.18 m de +2.23 junto al cerco a +4.00 en el borde libre
AX0, AX1 = 51.790, 66.859
MV.caja('piso_p05', AX0, YC, 0.0, AX1, 23.0, 0.10)
for x in (54.44, 56.94, 59.44, 61.94, 64.44):
    MV.caja('bruna', x - 0.006, YC, 0.10, x + 0.006, 23.0, 0.102)
R_A, CS_A, CH_A = 15.18, 7.315, -11.07


def h_auto(s):
    return CH_A + math.sqrt(R_A ** 2 - (s - CS_A) ** 2)


lamina('autos_cobertura', AX0, AX1, [(0.275 * i, h_auto(0.275 * i)) for i in range(21)], 'aluzinc_tr4', 0.04)
for sc_ in (0.09, 0.75, 2.32, 3.95, 5.39):                             # 5 correas de tubo 2"
    tubo('autos_correa', (AX0, YC + sc_, h_auto(sc_) - 0.05), (AX1, YC + sc_, h_auto(sc_) - 0.05), 0.0254, 'acero', CV)
for x in (51.89, 56.89, 61.89, 66.759):                                # 4 ejes: columna 0.20 x 0.30 a +1.70, tubo 4" y árbol de tubos 2"
    MV.caja('TP1', x - 0.10, 18.851, 0.10, x + 0.10, 19.151, 1.70)
    tubo('autos_tubo4', (x, YC + 1.0, 1.70), (x, YC + 1.0, 1.90), 0.0508, 'acero', CV)
    tubo('autos_tubo2', (x, YC + 1.0, 1.90), (x, YC + 1.0, h_auto(1.0) - 0.10), 0.0254, 'acero', CV)
    tubo('autos_tubo2', (x, YC + 1.0, 1.90), (x, YC + 2.165, h_auto(2.165) - 0.10), 0.0254, 'acero', CV)
    tubo('autos_tubo2', (x, YC + 1.0, 1.90), (x, YC + 0.173, h_auto(0.173) - 0.10), 0.0254, 'acero', CV)
    for dx in (-0.035, 0.035):                                         # viga doble siguiendo la cobertura
        curva('autos_viga', [(x + dx, YC + 0.275 * i, h_auto(0.275 * i) - 0.10) for i in range(21)], 0.025, 'acero', CV)


def mat_auto(nombre, color):
    m = bpy.data.materials.new(nombre); nt, N, Lk, p = nodos(m)
    p.inputs['Base Color'].default_value = color; p.inputs['Metallic'].default_value = 0.45; p.inputs['Roughness'].default_value = 0.28
    p.inputs['Coat Weight'].default_value = 1.0; p.inputs['Coat Roughness'].default_value = 0.05
    MATS[nombre] = m


mat_simple('caucho', rgb(20, 20, 21), rug=0.85)
mat_simple('auto_vidrio', rgb(18, 24, 28), rug=0.03, metal=0.1)
mat_simple('auto_trim', rgb(14, 14, 15), rug=0.55)
mat_simple('auto_faro', rgb(225, 228, 228), rug=0.08, metal=0.6)
mat_simple('auto_piloto', rgb(135, 12, 14), rug=0.12)
mat_simple('aro', rgb(178, 180, 182), rug=0.25, metal=0.9)
PINTURAS = (('auto_blanco', (232, 232, 230)), ('auto_plata', (150, 153, 156)), ('auto_grafito', (48, 50, 54)), ('auto_vino', (104, 22, 30)),
            ('auto_azul', (28, 44, 74)), ('auto_perla', (214, 210, 200)))
for n_, c_ in PINTURAS:
    mat_auto(n_, rgb(*c_))
for n_, c_ in (('moto_negra', (18, 18, 20)), ('moto_roja', (150, 22, 24)), ('moto_azul', (22, 54, 118))):
    mat_auto(n_, rgb(*c_))
# estaciones del auto a lo largo: u, fondo, cintura, techo, medio ancho cuerpo, medio ancho techo
EST_AUTO = [(0.00, 0.40, 0.80, 0.87, 0.78, 0.68), (0.05, 0.33, 0.90, 0.98, 0.86, 0.76), (0.32, 0.25, 0.97, 1.04, 0.89, 0.80), (0.78, 0.22, 0.98, 1.07, 0.90, 0.80),
            (1.30, 0.21, 0.97, 1.37, 0.90, 0.72), (1.72, 0.21, 0.96, 1.44, 0.90, 0.71), (2.00, 0.21, 0.96, 1.445, 0.90, 0.71), (2.06, 0.21, 0.96, 1.445, 0.90, 0.71),
            (2.40, 0.21, 0.95, 1.44, 0.90, 0.71), (2.76, 0.21, 0.94, 1.36, 0.90, 0.74), (3.38, 0.21, 0.90, 0.98, 0.90, 0.82), (3.92, 0.23, 0.83, 0.90, 0.88, 0.78),
            (4.30, 0.27, 0.74, 0.79, 0.84, 0.72), (4.39, 0.33, 0.68, 0.71, 0.78, 0.64)]
L_AUTO = 4.39


def auto(cx, cy, ang, pintura):
    """Sedán de 4.39 x 1.80 armado por secciones; el frente queda en la dirección ang (grados)."""
    vs, fs, mf = [], [], []
    for u, zb, zc, zt, w, wt in EST_AUTO:
        der = [(0, zb), (0.75 * w, zb), (w, zb + 0.10), (w, (zb + 0.10 + zc) / 2), (0.98 * w, zc), (wt, zc + 0.85 * (zt - zc)), (0.74 * wt, zt)]
        anillo = der + [(0, zt + 0.012)] + [(-a, b) for a, b in reversed(der[1:])]
        vs += [(u - L_AUTO / 2, a, b) for a, b in anillo]
    nr = 14
    for i in range(len(EST_AUTO) - 1):
        u0 = EST_AUTO[i][0]
        for j in range(nr):
            fs.append((i * nr + j, (i + 1) * nr + j, (i + 1) * nr + (j + 1) % nr, i * nr + (j + 1) % nr))
            j_ = j if j < 7 else 13 - j                                # 0-6 = franja del lado derecho, espejo en el izquierdo
            m_ = 0
            if j_ == 4 and 0.78 <= u0 < 3.38:                          # lunas laterales, parante central
                m_ = 2 if u0 == 2.00 else 1
            elif j_ in (5, 6) and (0.78 <= u0 < 1.30 or 2.76 <= u0 < 3.38):  # parabrisas y luna posterior
                m_ = 1
            elif j_ in (0, 1):                                         # bajos
                m_ = 2
            mf.append(m_)
    fs.append(tuple(range(nr - 1, -1, -1))); mf.append(0)
    n_ = len(EST_AUTO) - 1
    fs.append(tuple(n_ * nr + j for j in range(nr))); mf.append(0)
    M_ = Matrix.Translation((cx, cy, 0.10)) @ Matrix.Rotation(math.radians(ang), 4, 'Z')
    o = obj_mesh('auto', vs, fs, pintura, CV)
    for q in ('auto_vidrio', 'auto_trim', 'auto_faro', 'auto_piloto'):
        o.data.materials.append(MATS[q])
    for p_, m_ in zip(o.data.polygons, mf):
        p_.material_index = m_
    o.data.shade_smooth(); o.modifiers.new('sub', 'SUBSURF').levels = 2; o.modifiers['sub'].render_levels = 2
    o.matrix_basis = M_
    for ue in (-L_AUTO / 2 + 0.86, -L_AUTO / 2 + 3.50):                # ruedas y pasos de rueda
        for s_ in (-1, 1):
            arco = [(ue + 0.38 * math.cos(math.radians(a_)), 0.38 * math.sin(math.radians(a_)) + 0.32) for a_ in range(-30, 211, 15)]
            arco = [(a_, max(b_, 0.20)) for a_, b_ in arco]
            obj_mesh('auto_paso', [(a_, s_ * 0.888, b_) for a_, b_ in arco], [tuple(range(len(arco)))], 'auto_trim', CV).matrix_basis = M_
            for r_, e_, zm, v_ in ((0.32, 0.215, 'caucho', 0.785), (0.19, 0.02, 'aro', 0.895), (0.05, 0.02, 'auto_trim', 0.905)):
                bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r_, depth=e_, location=(ue, s_ * v_, 0.32), rotation=(math.pi / 2, 0, 0))
                w_ = bpy.context.active_object; w_.name = 'auto_rueda'; w_.data.materials.append(MATS[zm]); w_.data.shade_smooth()
                bpy.context.collection.objects.unlink(w_); CV.objects.link(w_); w_.matrix_basis = M_ @ w_.matrix_basis
    for s_ in (-1, 1):                                                 # espejos
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1.0, location=(-L_AUTO / 2 + 3.12, s_ * 0.98, 0.99), scale=(0.05, 0.09, 0.06))
        e_ = bpy.context.active_object; e_.name = 'auto_espejo'; e_.data.materials.append(MATS[pintura]); e_.data.shade_smooth()
        bpy.context.collection.objects.unlink(e_); CV.objects.link(e_); e_.matrix_basis = M_ @ e_.matrix_basis
    ur, uf = -L_AUTO / 2 - 0.012, L_AUTO / 2 - 0.012                   # frente y posterior: placas, pilotos, faros, parrilla y parachoques
    P_AUTO = [(ur - 0.01, -0.24, 0.56, ur + 0.03, 0.24, 0.68, 'blanco'), (uf - 0.03, -0.24, 0.38, uf + 0.03, 0.24, 0.50, 'blanco'),
              (ur - 0.01, -0.74, 0.40, ur + 0.05, 0.74, 0.50, 'auto_trim'), (uf - 0.03, -0.70, 0.36, uf + 0.03, 0.70, 0.37, 'auto_trim'),
              (uf - 0.03, -0.40, 0.53, uf + 0.03, 0.40, 0.64, 'auto_trim')]
    for s_ in (-1, 1):
        P_AUTO += [(ur - 0.005, s_ * 0.38 - 0.0, 0.70, ur + 0.05, s_ * 0.74, 0.80, 'auto_piloto'), (uf - 0.04, s_ * 0.44, 0.56, uf + 0.018, s_ * 0.74, 0.65, 'auto_faro')]
    for a_, b_, c_, d_, e_, f_, m_ in P_AUTO:
        caja('auto_pieza', a_, min(b_, e_), c_, d_, max(b_, e_), f_, m_, CV).matrix_basis = M_


def elipsoide(nombre, c_, sx, sy, sz, mat, M_):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=1.0, location=c_, scale=(sx, sy, sz))
    e_ = bpy.context.active_object; e_.name = nombre; e_.data.materials.append(MATS[mat]); e_.data.shade_smooth()
    bpy.context.collection.objects.unlink(e_); CV.objects.link(e_); e_.matrix_basis = M_ @ e_.matrix_basis
    return e_


def moto(cx, cy, ang, pintura):
    """Moto de 2.015 m apoyada en su pata; el frente queda en la dirección ang (grados)."""
    M_ = Matrix.Translation((cx, cy, 0.10)) @ Matrix.Rotation(math.radians(ang), 4, 'Z') @ Matrix.Rotation(math.radians(-5), 4, 'X')
    pieza = []
    for ue in (-0.70, 0.70):                                           # ruedas
        bpy.ops.mesh.primitive_torus_add(major_segments=36, minor_segments=12, major_radius=0.265, minor_radius=0.045, location=(ue, 0, 0.31), rotation=(math.pi / 2, 0, 0))
        w_ = bpy.context.active_object; w_.name = 'moto_llanta'; w_.data.materials.append(MATS['caucho']); w_.data.shade_smooth(); pieza.append(w_)
        bpy.ops.mesh.primitive_torus_add(major_segments=36, minor_segments=8, major_radius=0.222, minor_radius=0.012, location=(ue, 0, 0.31), rotation=(math.pi / 2, 0, 0))
        w_ = bpy.context.active_object; w_.name = 'moto_aro'; w_.data.materials.append(MATS['aro']); w_.data.shade_smooth(); pieza.append(w_)
        for r_ in range(16):                                           # rayos
            a_ = r_ * math.pi / 8; d_ = 0.022 if r_ % 2 else -0.022
            curva('moto_rayo', [tuple(M_ @ Vector(q)) for q in ((ue + 0.045 * math.cos(a_), d_, 0.31 + 0.045 * math.sin(a_)), (ue + 0.215 * math.cos(a_ + 0.3), 0, 0.31 + 0.215 * math.sin(a_ + 0.3)))], 0.0028, 'aro', CV)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.05, depth=0.10, location=(ue, 0, 0.31), rotation=(math.pi / 2, 0, 0))
        w_ = bpy.context.active_object; w_.name = 'moto_cubo'; w_.data.materials.append(MATS['auto_trim']); w_.data.shade_smooth(); pieza.append(w_)
    for w_ in pieza:
        bpy.context.collection.objects.unlink(w_); CV.objects.link(w_); w_.matrix_basis = M_ @ w_.matrix_basis
    for s_ in (-1, 1):                                                 # horquilla y brazo posterior
        curva('moto_horquilla', [tuple(M_ @ Vector(q)) for q in ((0.70, s_ * 0.085, 0.31), (0.47, s_ * 0.085, 0.92))], 0.022, 'aro', CV)
        curva('moto_basculante', [tuple(M_ @ Vector(q)) for q in ((-0.70, s_ * 0.085, 0.31), (-0.08, s_ * 0.06, 0.40))], 0.02, 'auto_trim', CV)
        elipsoide('moto_espejo', (0.40, s_ * 0.27, 1.24), 0.02, 0.05, 0.035, 'auto_trim', M_)
        curva('moto_espejo_brazo', [tuple(M_ @ Vector(q)) for q in ((0.43, s_ * 0.24, 1.06), (0.40, s_ * 0.27, 1.22))], 0.006, 'auto_trim', CV)
    curva('moto_manillar', [tuple(M_ @ Vector(q)) for q in ((0.42, -0.36, 1.06), (0.45, -0.14, 1.02), (0.45, 0.14, 1.02), (0.42, 0.36, 1.06))], 0.012, 'aro', CV)
    for s_ in (-1, 1):
        curva('moto_puno', [tuple(M_ @ Vector(q)) for q in ((0.43, s_ * 0.27, 1.05), (0.42, s_ * 0.37, 1.06))], 0.018, 'caucho', CV)
    curva('moto_chasis', [tuple(M_ @ Vector(q)) for q in ((0.47, 0, 0.90), (0.20, 0, 0.72), (0.02, 0, 0.42), (-0.20, 0, 0.42), (-0.30, 0, 0.72), (-0.62, 0, 0.82))], 0.022, 'auto_trim', CV)
    elipsoide('moto_tanque', (0.17, 0, 0.87), 0.30, 0.145, 0.13, pintura, M_)
    for s_ in (-1, 1):
        elipsoide('moto_tapa_lateral', (-0.20, s_ * 0.085, 0.68), 0.20, 0.035, 0.12, pintura, M_)
    elipsoide('moto_asiento', (-0.28, 0, 0.84), 0.38, 0.135, 0.07, 'caucho', M_)
    elipsoide('moto_cola', (-0.62, 0, 0.88), 0.17, 0.085, 0.055, pintura, M_)
    elipsoide('moto_piloto', (-0.78, 0, 0.88), 0.02, 0.05, 0.025, 'auto_piloto', M_)
    elipsoide('moto_faro', (0.56, 0, 0.92), 0.07, 0.075, 0.075, 'auto_faro', M_)
    elipsoide('moto_guarda_del', (0.70, 0, 0.60), 0.20, 0.06, 0.025, pintura, M_)
    elipsoide('moto_guarda_tras', (-0.74, 0, 0.62), 0.20, 0.065, 0.025, pintura, M_)
    elipsoide('moto_motor', (0.05, 0, 0.50), 0.25, 0.14, 0.20, 'auto_trim', M_)
    elipsoide('moto_carter', (0.05, 0, 0.47), 0.12, 0.155, 0.12, 'aro', M_)
    curva('moto_escape', [tuple(M_ @ Vector(q)) for q in ((0.10, 0.12, 0.38), (-0.20, 0.15, 0.36), (-0.82, 0.16, 0.55))], 0.038, 'aro', CV)
    curva('moto_pata', [tuple(Matrix.Translation((cx, cy, 0.10)) @ Matrix.Rotation(math.radians(ang), 4, 'Z') @ Vector(q)) for q in ((-0.08, 0.05, 0.38), (-0.12, 0.27, 0.01))], 0.012, 'auto_trim', CV)


for i, cx_ in enumerate((53.088, 55.588, 58.088, 60.588, 63.088, 65.588)):  # bloques AUDI-P de la PG (trompa al cerco)
    auto(cx_, 20.409, 90.85 + 180, PINTURAS[i][0])
for i, cx_ in enumerate((13.485, 14.685, 15.885, 17.085, 18.285, 19.485, 20.685, 21.885, 23.085, 24.285, 25.455, 26.655)):  # bloques de la PG, 5 cm al norte de las columnas
    moto(cx_, 19.291, 270, ('moto_negra', 'moto_roja', 'moto_azul')[i % 3])
MV.crear()

# ------------------------------------------------------------------ OE-06 tanque elevado y cuarto de bombas
# Torre de concreto de 3.38 x 3.38 centrada en la huella de la PG; las cotas de la lámina van sobre el N.P.T. del cuarto (+0.15).
CTQ = coleccion('Tanque elevado')
MT = Malla('tanque', CTQ)
QX, QY, QZ = 6.526, 27.959, 0.15
mat_simple('pastelero', rgb(168, 92, 66), rug=0.9)
MT.caja('vereda', QX - 2.705, QY - 2.705, 0.0, QX + 2.705, QY + 2.705, QZ)      # vereda de 1.00 m
for sx in (-1, 1):
    for sy in (-1, 1):
        a_, b_ = QX + sx * 1.44, QY + sy * 1.44
        MT.caja('TP1', a_ - 0.265, b_ - 0.265, QZ, a_ + 0.265, b_ + 0.265, QZ + 11.00)
for z0_, z1_ in ((2.70, 3.14), (5.41, 5.84), (8.10, 8.53), (10.80, 11.23)):      # vigas 0.25 x 0.40 tarrajeadas
    for s_ in (-1, 1):
        MT.caja('TP1', QX - 1.175, QY + s_ * 1.44 - 0.14, QZ + z0_, QX + 1.175, QY + s_ * 1.44 + 0.14, QZ + z1_)
        MT.caja('TP1', QX + s_ * 1.44 - 0.14, QY - 1.175, QZ + z0_, QX + s_ * 1.44 + 0.14, QY + 1.175, QZ + z1_)
MT.caja('pastelero', QX - 1.30, QY - 1.30, QZ + 3.14, QX + 1.30, QY + 1.30, QZ + 3.19)      # techo del cuarto
MT.caja('TP1', QX - 1.705, QY - 1.705, QZ + 11.00, QX + 1.705, QY + 1.705, QZ + 12.83)       # cuerpo del tanque
MT.caja('TP1', QX - 1.765, QY - 1.765, QZ + 12.83, QX + 1.765, QY + 1.765, QZ + 13.01)       # losa superior 3.53
MT.caja('pastelero', QX - 1.765, QY - 1.765, QZ + 13.01, QX + 1.765, QY + 1.765, QZ + 13.06)
MT.caja('plancha_metalica', QX + 0.30, QY - 0.43, QZ + 13.06, QX + 1.16, QY + 0.43, QZ + 13.17)   # tapa del tanque
# cuarto de bombas: ladrillo tarrajeado 0.13 entre columnas, contrazócalo 0.20, puerta P-20 y ventanas V-79 con rejilla
PD0, PD1 = QX + 0.175, QX + 0.975                                      # puerta metálica 0.80 x 2.10
for s_ in (-1, 1):
    a_, b_ = QY + s_ * 1.44 - 0.065, QY + s_ * 1.44 + 0.065
    if s_ == 1:
        MT.caja('TP3', QX - 1.175, a_, QZ, QX + 1.175, b_, QZ + 2.10)
        MT.caja('TP1', QX - 1.175, b_, QZ, QX + 1.175, b_ + 0.005, QZ + 0.20)
    else:
        MT.caja('TP3', QX - 1.175, a_, QZ, PD0, b_, QZ + 2.10); MT.caja('TP3', PD1, a_, QZ, QX + 1.175, b_, QZ + 2.10)
        MT.caja('TP1', QX - 1.175, a_ - 0.005, QZ, PD0, a_, QZ + 0.20); MT.caja('TP1', PD1, a_ - 0.005, QZ, QX + 1.175, a_, QZ + 0.20)
        MT.caja('plancha_metalica', PD0, QY - 1.44 - 0.02, QZ, PD1, QY - 1.44 + 0.02, QZ + 2.10)
    MT.caja('negro', QX - 1.175, a_, QZ + 2.10, QX + 1.175, a_ + 0.03, QZ + 2.14); MT.caja('negro', QX - 1.175, a_, QZ + 2.66, QX + 1.175, a_ + 0.03, QZ + 2.70)
    for k in range(20):
        x = QX - 1.13 + k * 0.118
        MT.caja('plancha_metalica', x, a_, QZ + 2.14, x + 0.045, a_ + 0.03, QZ + 2.66)
    MT.caja('TP3', QX + s_ * 1.44 - 0.065, QY - 1.175, QZ, QX + s_ * 1.44 + 0.065, QY + 1.175, QZ + 2.70)
    MT.caja('TP1', QX + s_ * (1.44 + 0.065), QY - 1.175, QZ, QX + s_ * (1.44 + 0.07), QY + 1.175, QZ + 0.20) if s_ == 1 else MT.caja('TP1', QX - 1.51, QY - 1.175, QZ, QX - 1.505, QY + 1.175, QZ + 0.20)
MT.caja('concreto_gris', QX + 1.705, QY - 0.30, 0.15, QX + 2.205, QY + 0.30, 0.40)     # caja de reboses
MT.crear()
EY = QY + 1.80                                                         # escalera de gato en la cara norte, de +2.55 a +13.30
for s_ in (-1, 1):
    tubo('gato_parante', (QX + s_ * 0.30, EY, QZ + 2.55), (QX + s_ * 0.30, EY, QZ + 13.70), 0.015, 'negro_ral9005', CTQ)
    for z_ in (3.0, 5.6, 8.3, 11.0, 13.0):
        tubo('gato_anclaje', (QX + s_ * 0.30, QY + 1.57, QZ + z_), (QX + s_ * 0.30, EY, QZ + z_), 0.012, 'negro_ral9005', CTQ)
for k in range(43):
    z_ = QZ + 2.65 + k * 0.25
    tubo('gato_peldano', (QX - 0.30, EY, z_), (QX + 0.30, EY, z_), 0.0095, 'negro_ral9005', CTQ)

# ------------------------------------------------------------------ OE-04 patio de descarga y de maniobras
# Losa de concreto f'c 175 (P-05) sin techo ni cerco, con el contorno de la lámina; la etiqueta OE-04 del plano no es un objeto.
PATIO = [(56.685, 55.074), (56.685, 41.899), (61.826, 41.899)] + [(61.826 + 3.025 * math.cos(math.radians(90 - a_)), 38.874 + 3.025 * math.sin(math.radians(90 - a_))) for a_ in range(10, 91, 10)]
PATIO += [(64.851, 34.428), (71.0, 34.428), (71.0, 55.074)]
prisma('patio_descarga', PATIO, 0.0, 0.10, 'piso_p05', CO)
EXTRAS_SIN_ARBOL.append(_SP(PATIO).buffer(0))

# ------------------------------------------------------------------ OE-07 PTAR
# Recinto de malla olímpica de 7.00 x 21.825, sin techo: dados, postes Ø 2", marco con malla, brazos a 45° con 3 alambres, portón PM
# de dos hojas al sur. El piso es tierra o hierba: del tanque de 3 cámaras y de los 2 pozos enterrados solo asoman sus tapas.
CP = coleccion('PTAR')
ZP = 0.15
PX0, PX1, PY0, PY1 = 63.305, 70.105, 56.944, 78.569
LADOS = [('O', [(PX0, 56.844 + 2.1625 * k + 0.10) for k in range(11)], -1), ('E', [(PX1, 56.844 + 2.1625 * k + 0.10) for k in range(11)], 1),
         ('N', [(PX0, PY1), (65.555, PY1), (67.855, PY1), (PX1, PY1)], 1), ('S', [(PX0, PY0), (65.105, PY0), (67.355, PY0), (PX1, PY0)], -1)]
for lado, pts_, s_ in LADOS:
    vert = lado in ('O', 'E')
    for x, y in pts_:
        caja('ptar_dado', x - 0.10, y - 0.10, 0.0, x + 0.10, y + 0.10, ZP + 0.10, 'concreto_gris', CP)
        tubo('ptar_poste', (x, y, ZP + 0.10), (x, y, ZP + 2.55), 0.03, 'galvanizado', CP)
        z_ = (x + s_ * 0.27, y) if vert else (x, y + s_ * 0.27)
        tubo('ptar_brazo', (x, y, ZP + 2.55), (z_[0], z_[1], ZP + 2.90), 0.016, 'galvanizado', CP)
    for (xa, ya), (xb, yb) in zip(pts_, pts_[1:]):
        if lado == 'S' and xa == 67.355:                               # vano del portón PM
            continue
        if vert:
            caja('ptar_malla', xa - 0.004, ya + 0.05, ZP + 0.10, xa + 0.004, yb - 0.05, ZP + 2.50, 'malla_y', CP)
            for zz in (ZP + 0.10, ZP + 2.50):
                caja('ptar_marco', xa - 0.015, ya + 0.04, zz - 0.015, xa + 0.015, yb - 0.04, zz + 0.015, 'galvanizado', CP)
        else:
            caja('ptar_malla', xa + 0.05, ya - 0.004, ZP + 0.10, xb - 0.05, ya + 0.004, ZP + 2.50, 'malla_x', CP)
            for zz in (ZP + 0.10, ZP + 2.50):
                caja('ptar_marco', xa + 0.04, ya - 0.015, zz - 0.015, xb - 0.04, ya + 0.015, zz + 0.015, 'galvanizado', CP)
    a_, b_ = pts_[0], pts_[-1]
    for h_ in (2.60, 2.70, 2.80):                                      # 3 alambres en los brazos
        d_ = s_ * 0.27 * (h_ - 2.55) / 0.35
        p0_ = (a_[0] + d_, a_[1], ZP + h_) if vert else (a_[0], a_[1] + d_, ZP + h_)
        p1_ = (b_[0] + d_, b_[1], ZP + h_) if vert else (b_[0], b_[1] + d_, ZP + h_)
        tubo('ptar_alambre', p0_, p1_, 0.004, 'galvanizado', CP)
for xa, xb in ((67.455, 68.73), (68.73, 70.005)):                      # portón PM: 2 hojas de tubo FG 1 1/2" y malla
    caja('ptar_porton_malla', xa + 0.03, PY0 - 0.004, ZP + 0.10, xb - 0.03, PY0 + 0.004, ZP + 2.50, 'malla_x', CP)
    for zz in (ZP + 0.08, ZP + 0.88, ZP + 1.68, ZP + 2.50):
        caja('ptar_porton', xa, PY0 - 0.02, zz - 0.02, xb, PY0 + 0.02, zz + 0.02, 'galvanizado', CP)
    for xv in (xa + 0.02, xb - 0.02):
        caja('ptar_porton', xv - 0.02, PY0 - 0.02, ZP + 0.06, xv + 0.02, PY0 + 0.02, ZP + 2.52, 'galvanizado', CP)
for y0_ in (75.424, 72.384):
    caja('ptar_tapa', 66.159, y0_, -0.02, 67.299, y0_ + 1.14, 0.06, 'concreto', CP)
caja('ptar_tapa', 66.445, 73.713, -0.02, 67.015, 74.283, 0.06, 'concreto', CP)
caja('ptar_caja', 66.573, 66.655, -0.02, 66.887, 67.206, 0.06, 'concreto_gris', CP)
for cx_, cy_ in ((64.650, 65.007), (68.810, 65.007)):                  # pozos enterrados: tapa de 0.806 girada 45°
    caja_c('ptar_pozo_tapa', cx_, cy_, 0.02, 0.806, 0.806, 0.08, 'concreto', math.radians(45), CP)
EXTRAS_SIN_ARBOL.append(_SB(63.2, 56.84, 70.21, 78.67))

# ------------------------------------------------------------------ OE-05 cerco perimétrico
# Muro M-2 de 0.16 tarrajeado sobre sobrecimiento de concreto expuesto (+0.50), viga de amarre hasta +3.20 y coronación de ladrillo
# pastelero hasta +3.23; cara exterior TP-1 con buñas de 5 cm; cara interior con paños TP-1 y columnas C-1 (ejes de la PG) y viga
# en concreto expuesto; juntas JDE-1 de 2.5 cm cada 8.80 m. Vano libre del OE-01 en x 31.285 a 45.09.
CC = coleccion('Cerco')
MC = Malla('cerco', CC)
mat_concreto('concreto_visto', (168, 166, 160), escala=2.0, agregado=0.08)
COLS_CERCO = json.load(open(os.path.join(AQUI, 'cerco_columnas.json'), encoding='utf-8'))
XO, XE, YF, YN = 1.076, 71.762, 18.001, 131.212                       # caras interiores (OE-05; el lado oeste es levemente oblicuo: promedio)
LADOS_C = {'S': (lambda t, n: (t, YF - n), [(XO - 0.16, 31.285), (45.09, XE + 0.16)]), 'N': (lambda t, n: (t, YN + n), [(XO - 0.16, XE + 0.16)]),
           'O': (lambda t, n: (XO - n, t), [(YF - 0.16, YN + 0.16)]), 'E': (lambda t, n: (XE + n, t), [(YF - 0.16, YN + 0.16)])}
BANDAS = ((0.55, 1.30), (1.35, 2.10), (2.15, 2.95), (3.00, 3.20))
BUNAS = ((0.50, 0.55), (1.30, 1.35), (2.10, 2.15), (2.95, 3.00))
for lado, (F_, tramos) in LADOS_C.items():
    def bloque(t0, t1, n0, n1, z0, z1, mat):
        (x0_, y0_), (x1_, y1_) = F_(t0, n0), F_(t1, n1)
        MC.caja(mat, min(x0_, x1_), min(y0_, y1_), z0, max(x0_, x1_), max(y0_, y1_), z1)
    for ta, tb in tramos:
        bloque(ta, tb, 0.0, 0.16, 0.0, 0.50, 'concreto_visto')
        for z0_, z1_ in BANDAS:
            bloque(ta, tb, 0.08, 0.16, z0_, z1_, 'TP1')
        for z0_, z1_ in BUNAS:
            bloque(ta, tb, 0.08, 0.15, z0_, z1_, 'TP1')
        bloque(ta, tb, 0.0, 0.08, 2.95, 3.20, 'concreto_visto')
        bloque(ta, tb, -0.04, 0.20, 3.20, 3.23, 'pastelero')
        cols_ = sorted(t for t in COLS_CERCO[lado] if ta <= t <= tb)
        borde = ta
        for t in cols_:
            bloque(borde, t - 0.125, 0.0, 0.08, 0.50, 2.95, 'TP1'); bloque(t - 0.125, t + 0.125, 0.0, 0.08, 0.50, 2.95, 'concreto_visto')
            borde = t + 0.125
        bloque(borde, tb, 0.0, 0.08, 0.50, 2.95, 'TP1')
        for a_, b_ in zip(cols_, cols_[1:]):                           # junta JDE-1 entre columnas pareadas
            if b_ - a_ < 0.40:
                t = (a_ + b_) / 2; bloque(t - 0.0125, t + 0.0125, 0.158, 0.1605, 0.0, 3.20, 'negro')
MC.crear()

# ------------------------------------------------------------------ OC-03 patio cívico y astas
# Piso de concreto frotachado y bruñado en módulos de 1.50, 4 jardineras en L con 2 árboles, 8 bancas 0.45 x 1.80 y plataforma de
# 2.65 x 1.50 con 2 astas de tres tramos (Ø 4", 3", 2") hasta 8.68 m. Sin pérgola ni techo (indicación de la usuaria, 03-11-2026).
CPC = coleccion('Patio civico')
MP = Malla('patio', CPC)
PCX0, PCY0, PCX1, PCY1 = 28.185, 54.389, 41.685, 70.889
ZC = 0.15                                                             # N.P.T. del patio
mat_concreto('patio_p4', (178, 175, 168), agregado=0.1, juntas=1.5)
caja('patio_piso', PCX0, PCY0, 0.0, PCX1, PCY1, ZC, 'patio_p4', CPC)
N_ARB_OC01 = len(JARD_ARB)                                            # arbustos de OC-01, bajo su cobertura
SX_, SY_ = (PCX0 + PCX1), (PCY0 + PCY1)                                # espejos de la jardinera del noroeste
# Contornos de la lámina (capa 1-TEXTURA PISOS): el sardinel de 0.10 rodea cada banca por detrás; la banca da al patio con su cara al
# ras del contorno exterior y la jardinera queda detrás de ella.
JE_ = [(29.685, 69.389), (29.685, 68.939), (29.235, 68.939), (29.235, 67.139), (29.685, 67.139), (29.685, 66.389), (28.185, 66.389), (28.185, 70.889),
       (32.685, 70.889), (32.685, 69.389), (31.913, 69.389), (31.913, 69.839), (30.113, 69.839), (30.113, 69.389)]
JI_ = [(32.013, 69.489), (32.013, 69.939), (30.013, 69.939), (30.013, 69.489), (29.585, 69.489), (29.585, 69.039), (29.135, 69.039), (29.135, 67.039),
       (29.585, 67.039), (29.585, 66.489), (28.285, 66.489), (28.285, 70.789), (32.585, 70.789), (32.585, 69.489)]
GE_, GI_ = _SP(JE_).buffer(0), _SP(JI_).buffer(0)
XS_ = sorted({q[0] for q in JE_ + JI_}); YS_ = sorted({q[1] for q in JE_ + JI_})
mat_concreto('terrazo', (158, 156, 150), escala=6.0, agregado=0.3)
MATS['terrazo'].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.3
for fx, fy in ((0, 0), (1, 0), (0, 1), (1, 1)):
    Q_ = lambda x, y: (SX_ - x if fx else x, SY_ - y if fy else y)
    for xa_, xb_ in zip(XS_, XS_[1:]):
        for ya_, yb_ in zip(YS_, YS_[1:]):
            c_ = _Pt((xa_ + xb_) / 2, (ya_ + yb_) / 2)
            if not GE_.contains(c_):
                continue
            p0_, p1_ = Q_(xa_, ya_), Q_(xb_, yb_)
            a_, b_, c1_, d1_ = min(p0_[0], p1_[0]), min(p0_[1], p1_[1]), max(p0_[0], p1_[0]), max(p0_[1], p1_[1])
            if GI_.contains(c_):
                MP.caja('pasto', a_, b_, ZC, c1_, d1_, ZC + 0.20)      # tierra y pasto NJT +0.20
            else:
                MP.caja('TP3', a_, b_, ZC, c1_, d1_, ZC + 0.55)        # sardinel NST +0.55
    for a_, b_, c_, d_ in ((29.235, 67.139, 29.685, 68.939), (30.113, 69.389, 31.913, 69.839)):       # bancas 0.45 x 1.80 de terrazo, H 0.50
        p0_, p1_ = Q_(a_, b_), Q_(c_, d_)
        MP.caja('terrazo', min(p0_[0], p1_[0]), min(p0_[1], p1_[1]), ZC, max(p0_[0], p1_[0]), max(p0_[1], p1_[1]), ZC + 0.50)
    for q_ in ((28.72, 67.8), (31.0, 70.36)):                          # árboles Tecoma
        JARD_ARB.append((*Q_(*q_), ZC + 0.20))
MP.caja('concreto_visto', 40.185, 61.314, ZC, 41.685, 63.964, ZC + 0.15)      # plataforma de las astas
for ya_ in (63.214, 62.064):
    xa_ = 40.935
    MP.caja('concreto_visto', xa_ - 0.20, ya_ - 0.20, ZC + 0.15, xa_ + 0.20, ya_ + 0.20, ZC + 0.50)
    MP.caja('concreto_visto', xa_ - 0.125, ya_ - 0.125, ZC + 0.50, xa_ + 0.125, ya_ + 0.125, ZC + 0.80)
    for z0_, z1_, r_ in ((0.775, 3.275, 0.0571), (3.275, 3.475, 0.0640), (3.475, 5.975, 0.0445), (5.975, 6.175, 0.0520), (6.175, 8.675, 0.0302)):
        tubo('asta', (xa_, ya_, ZC + z0_), (xa_, ya_, ZC + z1_), r_, 'aluminio_claro', CPC).data.shade_smooth()
    elipsoide('asta_remate', (xa_, ya_, ZC + 8.74), 0.03, 0.03, 0.06, 'aluminio_claro', Matrix.Identity(4))
    tubo('asta_tapa', (xa_, ya_, ZC + 8.675), (xa_, ya_, ZC + 8.69), 0.045, 'aluminio_claro', CPC)
FX_, FY_ = 40.935 + 0.035, 63.214                                      # bandera del Perú en el asta norte
for j, m_ in enumerate(('bandera_roja', 'bandera_blanca', 'bandera_roja')):
    vs, fs = [], []
    for i in range(9):
        u_ = j * 0.5 + i * 0.5 / 8
        for z_ in (ZC + 7.55, ZC + 8.55):
            vs.append((FX_ - u_, FY_ + 0.07 * u_ * math.sin(u_ * 4.5), z_ - 0.03 * u_))
    fs = [(2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1) for i in range(8)]
    obj_mesh('bandera', vs, fs, m_, CPC).data.shade_smooth()
MP.crear()
EXTRAS_SIN_ARBOL.append(_SB(PCX0, PCY0, PCX1, PCY1))

# ------------------------------------------------------------------ árboles
CA = coleccion('Arboles')
PROTO = []
COPAS = {}
bpy.ops.mesh.primitive_circle_add(vertices=10, radius=0.5, fill_type='NGON', location=(0, -500, -50))
HOJA = bpy.context.active_object; HOJA.name = 'hoja'; HOJA.scale = (0.06, 0.12, 1)
bpy.ops.object.transform_apply(scale=True)
mh = bpy.data.materials.new('hoja_mat'); mh.use_nodes = True; Nh = mh.node_tree.nodes; Lh = mh.node_tree.links
ph = Nh['Principled BSDF']; oi = Nh.new('ShaderNodeObjectInfo'); crh = Nh.new('ShaderNodeValToRGB')
crh.color_ramp.elements[0].color = rgb(44, 82, 30); crh.color_ramp.elements[1].color = rgb(126, 156, 62)
geoh = Nh.new('ShaderNodeNewGeometry'); Lh.new(geoh.outputs['Random Per Island'], crh.inputs['Fac']); Lh.new(crh.outputs['Color'], ph.inputs['Base Color'])
ph.inputs['Roughness'].default_value = 0.62; ph.inputs['Specular IOR Level'].default_value = 0.25; ph.inputs['Subsurface Weight'].default_value = 0.0
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
        n = int(10000 * rr ** 2)
        for _ in range(n):
            d = Vector((rl.gauss(0, 1), rl.gauss(0, 1), rl.gauss(0, 1))).normalized()
            ond = 0.16 * (math.sin(d.x * 5.1 + k) * math.sin(d.y * 4.3 + 1.3 * k) + math.sin(d.z * 6.7 + 2.1 * k) * math.cos(d.x * 3.3))   # copa irregular
            r = rr * (0.60 + 0.42 * rl.random() ** 0.6 + ond)
            pos = Vector(c) + off + d * r
            q = Quaternion((rl.gauss(0, 1), rl.gauss(0, 1), rl.gauss(0, 1), rl.gauss(0, 1))).normalized()
            sz = rl.uniform(0.75, 1.45)
            M = Matrix.Translation(pos) @ q.to_matrix().to_4x4() @ Matrix.Scale(sz, 4)
            b0 = len(vs); vs += [tuple(M @ cc) for cc in hv]; fs += [tuple(b0 + i for i in f_) for f_ in hf]
    me = bpy.data.meshes.new('follaje'); me.from_pydata(vs, [], fs); me.update()
    ob = bpy.data.objects.new('follaje', me); col.objects.link(ob); ob.data.materials.append(HOJA.data.materials[0])
    print('follaje', col.name, len(fs))
# Árboles del lote: los dibujados en la planta general (arquitecta) + los de relleno solo si caen en área verde. Ninguno puede
# tocar una cobertura: la copa se reduce hasta que quepa y, si no cabe, el árbol no se pone.
ARB_PLANO = [tuple(p) for p in D['arboles']] + [(7.52, 44.98), (7.52, 39.49), (7.52, 33.51), (6.70, 21.48), (28.75, 19.21), (69.21, 20.28)]
ARB_RELLENO = [(2.5, 46), (28, 60), (29, 90), (52, 90), (48.5, 114), (60, 112)]
TECHADOS = [_SB(*t['rect']) for m_ in ER.values() for t in m_['techos']] + [_SB(*D[k_]) for k_ in ('autos', 'motos', 'losa', 'garita', 'tanque', 'oc04')]
TECHADOS += [_SB(BX0, BY0, BX1, BY1)] + [_Pt(c_[0], c_[1]).buffer(2.6) for c_ in ((38.563, 46.555), (38.44, 33.645), (33.897, 110.377), (47.067, 110.256))]
TECHADOS += EXTRAS_SIN_ARBOL
TECHADOS.append(_SB(1.076, 18.001, 71.762, 131.212).exterior.buffer(0.16))      # cerco OE-05: ninguna copa lo cruza
TECHADOS = _UU(TECHADOS)
RAD_COPA = [max(math.hypot(c_[0], c_[1]) + 1.34 * r_ for c_, r_ in COPAS[k_]) for k_ in range(4)]   # radio máximo real del follaje de cada prototipo
POS_LOTE = []
for x_, y_ in ARB_PLANO + [q_ for q_ in ARB_RELLENO if VERDES.contains(_Pt(*q_))]:
    if any(math.hypot(x_ - a_, y_ - b_) < 2.0 for a_, b_, *_ in POS_LOTE):
        continue
    POS_LOTE.append((x_, y_, TECHADOS.distance(_Pt(x_, y_)) - 0.25))
print('arboles del lote', len(POS_LOTE), [(round(a_, 1), round(b_, 1), round(c_, 2)) for a_, b_, c_ in POS_LOTE])
POS_ARBOLES = []
rng = random.Random(3)
for _ in range(1400):                                               # vegetación del entorno
    r_ = 20 + rng.random() ** 0.7 * 520; a_ = rng.uniform(0, 6.283)
    x = 36 + r_ * math.cos(a_); y = 75 + r_ * math.sin(a_)
    if 4 < y < 20 or (-6 < x < 78 and 14 < y < 138):
        continue
    POS_ARBOLES.append((x, y))
rl_ = random.Random(11)
for i, (x, y, libre) in enumerate(POS_LOTE):
    k_ = i % 4 if libre > 3.5 else 2                                 # en sitios estrechos, la copa menor
    s = min(rl_.uniform(0.85, 1.25), libre / RAD_COPA[k_])
    if s < 0.42:                                                     # no cabe sin tocar una cobertura
        print('arbol sin espacio, no se pone', round(x, 1), round(y, 1)); continue
    e = bpy.data.objects.new('arbol', None); e.instance_type = 'COLLECTION'; e.instance_collection = PROTO[k_]
    e.location = (x, y, 0); e.rotation_euler = (0, 0, rl_.uniform(0, 6.28)); e.scale = (s, s, s); CA.objects.link(e)
for i, (x, y) in enumerate(POS_ARBOLES):
    e = bpy.data.objects.new('arbol', None); e.instance_type = 'COLLECTION'; e.instance_collection = PROTO[i % 4]
    e.location = (x, y, 0); e.rotation_euler = (0, 0, rng.uniform(0, 6.28)); s = rng.uniform(0.85, 1.35); e.scale = (s, s, s)
    CA.objects.link(e)
for i, p_ in enumerate(JARD_ARB):                                   # arbustos de OC-01 (no llegan a su cobertura) y árboles Tecoma del patio
    k_, s = (2, 0.25) if i < N_ARB_OC01 else (i % 4, 0.34)
    e = bpy.data.objects.new('arbol_jardinera', None); e.instance_type = 'COLLECTION'; e.instance_collection = PROTO[k_]
    e.location = p_; e.rotation_euler = (0, 0, rng.uniform(0, 6.28)); e.scale = (s, s, s); CA.objects.link(e)

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
duro.append(SBox(BX0 - 0.1, BY0 - 0.1, BX1 + 0.1, BY1 + 0.1))                  # biohuerto: piedra laja y camas
duro.append(SBox(PCX0 - 0.1, PCY0 - 0.1, PCX1 + 0.1, PCY1 + 0.1))              # patio cívico
duro.append(SPoly(PATIO).buffer(0.1))
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
sky.altitude = 150; sky.air_density = 1.0; sky.dust_density = 0.6; sky.ozone_density = 1.4; sky.sun_intensity = 0.23
bg = N['Background']; Lk.new(sky.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 0.22
bg2 = N.new('ShaderNodeBackground'); Lk.new(sky.outputs['Color'], bg2.inputs['Color']); bg2.inputs['Strength'].default_value = 1.15
lp = N.new('ShaderNodeLightPath'); ms = N.new('ShaderNodeMixShader')
tcw = N.new('ShaderNodeTexCoord'); sw = N.new('ShaderNodeSeparateXYZ'); Lk.new(tcw.outputs['Generated'], sw.inputs['Vector'])
zw = N.new('ShaderNodeMath'); zw.inputs[1].default_value = 0.14; Lk.new(sw.outputs['Z'], zw.inputs[0])
xw_ = N.new('ShaderNodeMath'); xw_.operation = 'DIVIDE'; Lk.new(sw.outputs['X'], xw_.inputs[0]); Lk.new(zw.outputs[0], xw_.inputs[1])
yw_ = N.new('ShaderNodeMath'); yw_.operation = 'DIVIDE'; Lk.new(sw.outputs['Y'], yw_.inputs[0]); Lk.new(zw.outputs[0], yw_.inputs[1])
cw = N.new('ShaderNodeCombineXYZ'); Lk.new(xw_.outputs[0], cw.inputs['X']); Lk.new(yw_.outputs[0], cw.inputs['Y'])
nw = N.new('ShaderNodeTexNoise'); nw.inputs['Scale'].default_value = 0.55; nw.inputs['Detail'].default_value = 12; nw.inputs['Roughness'].default_value = 0.56
Lk.new(cw.outputs['Vector'], nw.inputs['Vector'])
rw = N.new('ShaderNodeMapRange'); rw.inputs['From Min'].default_value = 0.53; rw.inputs['From Max'].default_value = 0.68; Lk.new(nw.outputs['Fac'], rw.inputs['Value'])
hw = N.new('ShaderNodeMapRange'); hw.inputs['From Min'].default_value = 0.0; hw.inputs['From Max'].default_value = 0.10; Lk.new(sw.outputs['Z'], hw.inputs['Value'])
mw = N.new('ShaderNodeMath'); mw.operation = 'MULTIPLY'; Lk.new(rw.outputs[0], mw.inputs[0]); Lk.new(hw.outputs[0], mw.inputs[1])
bgn = N.new('ShaderNodeBackground'); bgn.inputs['Color'].default_value = (1.0, 0.99, 0.97, 1); bgn.inputs['Strength'].default_value = 2.6   # nubes
msn = N.new('ShaderNodeMixShader'); Lk.new(mw.outputs[0], msn.inputs['Fac']); Lk.new(bg.outputs['Background'], msn.inputs[1]); Lk.new(bgn.outputs['Background'], msn.inputs[2])
Lk.new(lp.outputs['Is Camera Ray'], ms.inputs['Fac']); Lk.new(msn.outputs['Shader'], ms.inputs[1]); Lk.new(bg2.outputs['Background'], ms.inputs[2])
Lk.new(ms.outputs['Shader'], N['World Output'].inputs['Surface'])
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 64; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 10; sc.cycles.diffuse_bounces = 5; sc.cycles.glossy_bounces = 3; sc.cycles.transparent_max_bounces = 12
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03; sc.cycles.use_light_tree = True
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - High Contrast'; sc.view_settings.exposure = -1.0
sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.render.film_transparent = False
sc.view_layers[0].use_pass_mist = True
w.mist_settings.start = 60; w.mist_settings.depth = 900; w.mist_settings.falloff = 'QUADRATIC'
sc.use_nodes = True; T = sc.node_tree; T.nodes.clear()
rl = T.nodes.new('CompositorNodeRLayers'); mx = T.nodes.new('CompositorNodeMixRGB'); co = T.nodes.new('CompositorNodeComposite')
mx.inputs[2].default_value = (0.30, 0.36, 0.44, 1)
mm = T.nodes.new('CompositorNodeMath'); mm.operation = 'MULTIPLY'; mm.inputs[1].default_value = 0.55
T.links.new(rl.outputs['Mist'], mm.inputs[0]); T.links.new(mm.outputs[0], mx.inputs[0])
T.links.new(rl.outputs['Image'], mx.inputs[1]); T.links.new(mx.outputs[0], co.inputs['Image'])
for o in bpy.data.objects:                                            # cilindros: costado suave y tapas planas
    if o.type == 'MESH' and o.name.startswith(('ecologico_tacho', 'auto_rueda', 'moto_cubo', 'asta', 'ptar_pozo')):
        for p_ in o.data.polygons:
            p_.use_smooth = len(p_.vertices) == 4
sc.frame_set(28)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, 'refugio.blend'))
print('escena guardada', len(bpy.data.objects), 'objetos')
