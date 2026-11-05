# -*- coding: utf-8 -*-
"""Utilidades para armar en Blender el modelo de un proyecto a escala real (1 unidad = 1 m).
No trae datos de ningún proyecto: colores, medidas y contornos los pasa el generador de cada obra.
Requiere Blender 4.2 LTS o similar y shapely en el Python de Blender.
Uso, dentro del generador del proyecto:
    import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import base_escena as B
"""
import math
import random

import bpy
from mathutils import Matrix, Quaternion, Vector
from shapely.geometry import MultiPoint, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

MATS = {}


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(r, g, b, a=1.0):
    """Color del cuadro de acabados (RGB 0-255, sRGB) al espacio lineal de Blender."""
    return (_lin(r), _lin(g), _lin(b), a)


def nueva_escena():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MATS.clear()
    return bpy.context.scene


def coleccion(nombre, padre=None):
    c = bpy.data.collections.new(nombre)
    (padre.children if padre else bpy.context.scene.collection.children).link(c)
    return c


# ------------------------------------------------------------------ materiales
def _nodos(nombre):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt = m.node_tree
    MATS[nombre] = m
    return m, nt.nodes, nt.links, nt.nodes['Principled BSDF']


def _ruido(N, Lk, tc, escala, detalle=4.0, rug=0.5):
    n = N.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = escala; n.inputs['Detail'].default_value = detalle; n.inputs['Roughness'].default_value = rug
    Lk.new(tc.outputs['Object'], n.inputs['Vector'])
    return n


def _rango(N, a0, a1, b0=0.0, b1=1.0):
    r = N.new('ShaderNodeMapRange')
    r.inputs['From Min'].default_value = a0; r.inputs['From Max'].default_value = a1
    r.inputs['To Min'].default_value = b0; r.inputs['To Max'].default_value = b1
    return r


def mat_simple(nombre, color, rug=0.5, metal=0.0, brillo=None):
    """Plásticos, metales, madera lisa. brillo = Specular IOR Level (bajar en pasto y hojas para que no se vean pálidos)."""
    m, N, Lk, p = _nodos(nombre)
    p.inputs['Base Color'].default_value = color; p.inputs['Roughness'].default_value = rug; p.inputs['Metallic'].default_value = metal
    if brillo is not None:
        p.inputs['Specular IOR Level'].default_value = brillo
    return m


def mat_pintura(nombre, color, rug=0.85):
    """Pintura sobre tarrajeo: variación leve de tono, grano fino y canto suavizado."""
    m, N, Lk, p = _nodos(nombre)
    tc = N.new('ShaderNodeTexCoord')
    gr = _ruido(N, Lk, tc, 90, 12); man = _ruido(N, Lk, tc, 0.9, 4)
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    mx.inputs[6].default_value = color; mx.inputs[7].default_value = tuple(c * 0.9 for c in color[:3]) + (1,)
    p.inputs['Base Color'].default_value = color                       # el FBX lleva este color aunque la entrada esté enlazada
    Lk.new(man.outputs['Fac'], mx.inputs[0]); Lk.new(mx.outputs[2], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rug
    bv = N.new('ShaderNodeBevel'); bv.samples = 2; bv.inputs['Radius'].default_value = 0.012
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.12; bm.inputs['Distance'].default_value = 0.004
    Lk.new(gr.outputs['Fac'], bm.inputs['Height']); Lk.new(bv.outputs['Normal'], bm.inputs['Normal']); Lk.new(bm.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_vidrio(nombre='vidrio', color=(35, 52, 62)):
    """Vidrio oscuro opaco con reflejo: sin interiores modelados se ve mejor que uno transparente."""
    m = mat_simple(nombre, rgb(*color), rug=0.04)
    m.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.9
    return m


def mat_calamina(nombre, color, direccion='X', paso_nervio=0.45):
    """Cobertura ondulada: el nervio va en relieve con ondas perpendiculares a la caída del techo.
    direccion = eje a lo largo del cual se repiten las ondas ('X', 'Y' o 'Z')."""
    m, N, Lk, p = _nodos(nombre)
    p.inputs['Base Color'].default_value = color; p.inputs['Metallic'].default_value = 0.5
    tc = N.new('ShaderNodeTexCoord')
    w = N.new('ShaderNodeTexWave'); w.wave_type = 'BANDS'; w.bands_direction = direccion; w.wave_profile = 'SIN'
    w.inputs['Scale'].default_value = 1.0 / paso_nervio; w.inputs['Distortion'].default_value = 0.0
    Lk.new(tc.outputs['Object'], w.inputs['Vector'])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.55; bm.inputs['Distance'].default_value = 0.03
    Lk.new(w.outputs['Fac'], bm.inputs['Height']); Lk.new(bm.outputs['Normal'], p.inputs['Normal'])
    ra = _rango(N, 0.0, 1.0, 0.34, 0.52); Lk.new(_ruido(N, Lk, tc, 0.4).outputs['Fac'], ra.inputs['Value']); Lk.new(ra.outputs['Result'], p.inputs['Roughness'])
    return m


def mat_concreto(nombre, color=(186, 182, 174), juntas=None, agregado=0.12):
    """Concreto con manchas, agregado fino y juntas opcionales cada `juntas` m (alineadas al origen del objeto)."""
    m, N, Lk, p = _nodos(nombre)
    tc = N.new('ShaderNodeTexCoord')
    cr = N.new('ShaderNodeValToRGB'); b_ = rgb(*color); p.inputs['Base Color'].default_value = b_
    cr.color_ramp.elements[0].color = tuple(c * 0.7 for c in b_[:3]) + (1,); cr.color_ramp.elements[1].color = b_
    Lk.new(_ruido(N, Lk, tc, 3.0, 12, 0.65).outputs['Fac'], cr.inputs['Fac'])
    vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 180; Lk.new(tc.outputs['Object'], vo.inputs['Vector'])
    vm = _rango(N, 0.0, 0.25, 1.0 - agregado, 1.0); Lk.new(vo.outputs['Distance'], vm.inputs['Value'])
    cb = N.new('ShaderNodeCombineColor'); [Lk.new(vm.outputs['Result'], cb.inputs[i]) for i in range(3)]
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1
    Lk.new(cr.outputs['Color'], mx.inputs[6]); Lk.new(cb.outputs['Color'], mx.inputs[7]); sal = mx.outputs[2]
    if juntas:
        br = N.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 1.0 / juntas; br.offset = 0.0
        br.inputs['Brick Width'].default_value = 1.0; br.inputs['Row Height'].default_value = 1.0; br.inputs['Mortar Size'].default_value = 0.012
        for k_ in ('Color1', 'Color2'):
            br.inputs[k_].default_value = (1, 1, 1, 1)
        br.inputs['Mortar'].default_value = (0.45, 0.45, 0.45, 1); Lk.new(tc.outputs['Object'], br.inputs['Vector'])
        mj = N.new('ShaderNodeMix'); mj.data_type = 'RGBA'; mj.blend_type = 'MULTIPLY'; mj.inputs[0].default_value = 1
        Lk.new(sal, mj.inputs[6]); Lk.new(br.outputs['Color'], mj.inputs[7]); sal = mj.outputs[2]
    Lk.new(sal, p.inputs['Base Color']); p.inputs['Roughness'].default_value = 0.9
    return m


def mat_pasto(nombre='pasto', imagen=None, escala=0.22):
    """Pasto sin cuadrícula: dos capas de la textura, una girada y a otra escala, mezcladas por manchas, y color poco saturado.
    Sin imagen usa ruido: sirve de lejos; para vistas peatonales conviene una textura de pasto de uso libre."""
    m, N, Lk, p = _nodos(nombre)
    p.inputs['Base Color'].default_value = rgb(72, 92, 40)
    tc = N.new('ShaderNodeTexCoord')
    if imagen:
        img = bpy.data.images.load(imagen)
        capas = []
        for esc_, giro in ((escala, 0.0), (escala * 0.61, 0.65)):
            mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (esc_, esc_, esc_); mp.inputs['Rotation'].default_value = (0, 0, giro)
            Lk.new(tc.outputs['Object'], mp.inputs['Vector'])
            im = N.new('ShaderNodeTexImage'); im.image = img; Lk.new(mp.outputs['Vector'], im.inputs['Vector']); capas.append(im.outputs['Color'])
        rm = N.new('ShaderNodeValToRGB'); rm.color_ramp.elements[0].position = 0.42; rm.color_ramp.elements[1].position = 0.58
        Lk.new(_ruido(N, Lk, tc, 0.17, 6).outputs['Fac'], rm.inputs['Fac'])
        mc = N.new('ShaderNodeMix'); mc.data_type = 'RGBA'; Lk.new(rm.outputs['Color'], mc.inputs[0]); Lk.new(capas[0], mc.inputs[6]); Lk.new(capas[1], mc.inputs[7])
        hs = N.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = 0.72; hs.inputs['Value'].default_value = 0.86
        Lk.new(mc.outputs[2], hs.inputs['Color']); base = hs.outputs['Color']; relieve = mc.outputs[2]
    else:
        cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = rgb(52, 74, 30); cr.color_ramp.elements[1].color = rgb(92, 112, 48)
        fino = _ruido(N, Lk, tc, 40, 10); Lk.new(fino.outputs['Fac'], cr.inputs['Fac']); base = cr.outputs['Color']; relieve = fino.outputs['Fac']
    tn = N.new('ShaderNodeValToRGB'); tn.color_ramp.elements[0].color = (0.42, 0.50, 0.30, 1); tn.color_ramp.elements[1].color = (0.85, 0.88, 0.72, 1)
    Lk.new(_ruido(N, Lk, tc, 0.08).outputs['Fac'], tn.inputs['Fac'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1
    Lk.new(base, mx.inputs[6]); Lk.new(tn.outputs['Color'], mx.inputs[7]); Lk.new(mx.outputs[2], p.inputs['Base Color'])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.5; Lk.new(relieve, bm.inputs['Height']); Lk.new(bm.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Roughness'].default_value = 0.9; p.inputs['Specular IOR Level'].default_value = 0.15
    return m


# ------------------------------------------------------------------ geometría
def obj_mesh(nombre, verts, caras, mat, col=None):
    me = bpy.data.meshes.new(nombre); me.from_pydata(verts, [], caras); me.validate(); me.update()
    o = bpy.data.objects.new(nombre, me); (col or bpy.context.scene.collection).objects.link(o)
    if mat:
        me.materials.append(MATS[mat] if isinstance(mat, str) else mat)
    return o


def caja(nombre, x0, y0, z0, x1, y1, z1, mat, col=None):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return obj_mesh(nombre, v, f, mat, col)


def prisma(nombre, poligono, z0, z1, mat, col=None):
    """Extruye un polígono de shapely (también con huecos o múltiple) entre z0 y z1, con su tapa triangulada."""
    vs, fs = [], []
    for g in getattr(poligono, 'geoms', [poligono]):
        if g.geom_type != 'Polygon' or g.area < 1e-6:
            continue
        for t in _triangular(g):
            i = len(vs); vs += [(x, y, z1) for x, y in t]; fs.append((i, i + 1, i + 2))
            i = len(vs); vs += [(x, y, z0) for x, y in t]; fs.append((i + 2, i + 1, i))
        for an in [g.exterior] + list(g.interiors):
            c = list(an.coords)[:-1]
            if not an.is_ccw:
                c = c[::-1]
            if an is not g.exterior:
                c = c[::-1]
            for a, b in zip(c, c[1:] + c[:1]):
                i = len(vs); vs += [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]; fs.append((i, i + 1, i + 2, i + 3))
    return obj_mesh(nombre, vs, fs, mat, col) if fs else None


def _triangular(g):
    """Triángulos de un polígono con huecos, en sentido antihorario, recortados a su contorno exacto."""
    from shapely.ops import triangulate
    pts = list(g.exterior.coords) + [q for r in g.interiors for q in r.coords]
    sal = []
    for t in triangulate(MultiPoint(pts)):
        if g.contains(t.representative_point()):
            sal.append(list(orient(t).exterior.coords)[:3])
    area = sum(Polygon(t).area for t in sal)
    if abs(area - g.area) > 1e-3 * max(g.area, 1.0):                   # contorno cóncavo: triangular sus partes recortadas
        sal = []
        for t in triangulate(MultiPoint(pts)):
            r = t.intersection(g)
            for q in getattr(r, 'geoms', [r]):
                if q.geom_type == 'Polygon' and q.area > 1e-9:
                    cq = list(orient(q).exterior.coords)[:-1]
                    sal += [[cq[0], cq[i], cq[i + 1]] for i in range(1, len(cq) - 1)]
    return sal


class Malla:
    """Acumula cajas por material y crea un solo objeto por material: miles de muros y vanos sin miles de objetos."""
    def __init__(self, nombre, col=None):
        self.nombre, self.col, self.d = nombre, col, {}

    def caja(self, mat, x0, y0, z0, x1, y1, z1):
        if x1 - x0 < 1e-4 or y1 - y0 < 1e-4 or z1 - z0 < 1e-4:
            return
        vs, fs = self.d.setdefault(mat, ([], [])); i = len(vs)
        vs.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
        fs.extend([(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7), (i, i + 1, i + 5, i + 4), (i + 1, i + 2, i + 6, i + 5),
                   (i + 2, i + 3, i + 7, i + 6), (i + 3, i, i + 4, i + 7)])

    def crear(self):
        return [obj_mesh('%s_%s' % (self.nombre, m), vs, fs, m, self.col) for m, (vs, fs) in self.d.items()]


def piso_exacto(nombre, lote, huecos, z, mat, col=None, paso=0.5, espesor=0.10):
    """Piso del lote con los huecos (áreas verdes, edificaciones) recortados a su contorno exacto.
    No excluir celdas por su centro: eso deja bordes en escalones donde el plano dibuja una diagonal."""
    zona = lote.difference(unary_union(huecos)) if huecos else lote
    vs, fs = [], []
    x0, y0, x1, y1 = lote.bounds
    for i in range(int((x1 - x0) / paso) + 1):
        for j in range(int((y1 - y0) / paso) + 1):
            c = box(x0 + i * paso, y0 + j * paso, x0 + (i + 1) * paso, y0 + (j + 1) * paso).intersection(zona)
            for g in getattr(c, 'geoms', [c]):
                if g.geom_type == 'Polygon' and g.area > 1e-6:
                    e = list(orient(g).exterior.coords)[:-1]
                    fs.append(tuple(range(len(vs), len(vs) + len(e)))); vs += [(a, b, z) for a, b in e]
    o = obj_mesh(nombre, vs, fs, mat, col)
    m = o.modifiers.new('espesor', 'SOLIDIFY'); m.thickness = espesor; m.offset = -1
    return o


def suavizar_cilindros(prefijos):
    """Costado suave y tapas planas: con todo suavizado un tacho o una rueda se ven como huevos."""
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name.startswith(tuple(prefijos)):
            for p in o.data.polygons:
                p.use_smooth = len(p.vertices) == 4


# ------------------------------------------------------------------ árboles
def prototipos_arbol(col_proto, cantidad=4, semilla=5):
    """Árboles con follaje de hojas sueltas, que se plantan como instancias (no gastan memoria).
    Devuelve [(colección, radio máximo real de la copa)]. El radio incluye las hojas más salidas: con él se comprueba que no toquen nada."""
    rl = random.Random(semilla)
    mt = mat_simple('tronco', rgb(74, 58, 44), rug=0.9)
    mh = bpy.data.materials.new('hoja'); mh.use_nodes = True; Nh = mh.node_tree.nodes; Lh = mh.node_tree.links
    ph = Nh['Principled BSDF']; cr = Nh.new('ShaderNodeValToRGB'); ph.inputs['Base Color'].default_value = rgb(84, 118, 46)
    cr.color_ramp.elements[0].color = rgb(44, 82, 30); cr.color_ramp.elements[1].color = rgb(126, 156, 62)
    Lh.new(Nh.new('ShaderNodeNewGeometry').outputs['Random Per Island'], cr.inputs['Fac']); Lh.new(cr.outputs['Color'], ph.inputs['Base Color'])
    ph.inputs['Roughness'].default_value = 0.62; ph.inputs['Specular IOR Level'].default_value = 0.25
    MATS['hoja'] = mh
    hoja = [(0.03 * math.cos(a * 0.628), 0.06 * math.sin(a * 0.628), 0.0) for a in range(10)]
    sal = []
    for k in range(cantidad):
        c = bpy.data.collections.new('arbol_%d' % k); col_proto.children.link(c)
        off = Vector((k * 25.0, -1500.0, -60.0)); c.instance_offset = off
        alto = [3.0, 3.6, 2.6, 4.2][k % 4]; rad = [2.2, 2.8, 1.8, 3.2][k % 4]
        bpy.ops.mesh.primitive_cone_add(radius1=0.24, radius2=0.1, depth=alto + rad * 0.8, location=tuple(off + Vector((0, 0, (alto + rad * 0.8) / 2))))
        tr = bpy.context.active_object; tr.name = 'tronco'; tr.data.materials.append(mt); tr.data.shade_smooth()
        for u in list(tr.users_collection):
            u.objects.unlink(tr)
        c.objects.link(tr)
        copas = []
        for j in range(9):
            a = j * 2 * math.pi / 9 + rl.random(); rr = rad * (0.38 + rl.random() * 0.3)
            cen = (math.cos(a) * rad * 0.55, math.sin(a) * rad * 0.55, alto + rad * (0.25 + rl.random() * 0.55))
            copas.append((cen, rr) if j else ((0, 0, alto + rad * 0.85), rad * 0.62))
        vs, fs = [], []
        for (cn, rr) in copas:
            for _ in range(int(10000 * rr ** 2)):
                d = Vector((rl.gauss(0, 1), rl.gauss(0, 1), rl.gauss(0, 1))).normalized()
                ond = 0.16 * (math.sin(d.x * 5.1 + k) * math.sin(d.y * 4.3 + 1.3 * k) + math.sin(d.z * 6.7 + 2.1 * k) * math.cos(d.x * 3.3))   # copa irregular
                pos = Vector(cn) + off + d * (rr * (0.60 + 0.42 * rl.random() ** 0.6 + ond))
                q = Quaternion((rl.gauss(0, 1), rl.gauss(0, 1), rl.gauss(0, 1), rl.gauss(0, 1))).normalized()
                M = Matrix.Translation(pos) @ q.to_matrix().to_4x4() @ Matrix.Scale(rl.uniform(0.75, 1.45), 4)
                b0 = len(vs); vs += [tuple(M @ Vector(h)) for h in hoja]; fs.append(tuple(range(b0, b0 + len(hoja))))
            bpy.ops.mesh.primitive_ico_sphere_add(                     # núcleo oscuro para que la copa no se transparente
                subdivisions=3, radius=rr * 0.62, location=tuple(Vector(cn) + off))
            s = bpy.context.active_object; s.name = 'nucleo_copa'; s.data.shade_smooth()
            if 'nucleo_copa' not in MATS:
                mat_simple('nucleo_copa', rgb(22, 40, 16), rug=0.9)
            s.data.materials.append(MATS['nucleo_copa'])
            for u in list(s.users_collection):
                u.objects.unlink(s)
            c.objects.link(s)
        me = bpy.data.meshes.new('follaje'); me.from_pydata(vs, [], fs); me.update(); me.materials.append(mh)
        c.objects.link(bpy.data.objects.new('follaje', me))
        sal.append((c, max(math.hypot(cn[0], cn[1]) + 1.34 * rr for cn, rr in copas)))
    return sal


def plantar_arboles(posiciones, prototipos, obstaculos, col, semilla=11, escala_min=0.42, nombre='arbol'):
    """Planta árboles sin que ninguna copa toque `obstaculos` (polígono de shapely con coberturas, cerco y demás).
    Reduce la copa hasta que quepa; si no cabe con escala_min, no lo pone. Devuelve (plantados, descartados)."""
    rl = random.Random(semilla); hechos, fuera = [], []
    for i, (x, y) in enumerate(posiciones):
        libre = (obstaculos.distance(Point(x, y)) - 0.25) if obstaculos is not None else 99.0
        cl, rad = min(prototipos, key=lambda t: t[1]) if libre < 3.5 else prototipos[i % len(prototipos)]
        s = min(rl.uniform(0.85, 1.25), libre / rad)
        if s < escala_min:
            fuera.append((x, y)); continue
        e = bpy.data.objects.new(nombre, None); e.instance_type = 'COLLECTION'; e.instance_collection = cl
        e.location = (x, y, 0); e.rotation_euler = (0, 0, rl.uniform(0, 6.28)); e.scale = (s, s, s); col.objects.link(e)
        hechos.append((x, y, round(s, 3), round(rad * s, 2)))
    return hechos, fuera


# ------------------------------------------------------------------ cielo y tono
def mundo(elev=45.0, rot=210.0, luz_cielo=0.22, sol=0.23, cielo_camara=1.15, nubes=True):
    """Cielo físico en dos ramas: lo que ve la cámara y lo que ilumina la escena, para ajustarlos por separado.
    sol = intensidad del disco solar (bajarla da colores más fieles). La luz blanca de las nubes rellena las sombras."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('cielo'); sc.world = w; w.use_nodes = True
    N, Lk = w.node_tree.nodes, w.node_tree.links
    sky = N.new('ShaderNodeTexSky'); sky.name = 'Sky Texture'; sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(elev); sky.sun_rotation = math.radians(rot)
    sky.altitude = 150; sky.air_density = 1.0; sky.dust_density = 0.6; sky.ozone_density = 1.4; sky.sun_intensity = sol
    luz = N['Background']; Lk.new(sky.outputs['Color'], luz.inputs['Color']); luz.inputs['Strength'].default_value = luz_cielo
    cam = N.new('ShaderNodeBackground'); Lk.new(sky.outputs['Color'], cam.inputs['Color']); cam.inputs['Strength'].default_value = cielo_camara
    s_luz, s_cam = luz.outputs['Background'], cam.outputs['Background']
    if nubes:
        tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Generated'], sp.inputs['Vector'])
        z = N.new('ShaderNodeMath'); z.inputs[1].default_value = 0.14; Lk.new(sp.outputs['Z'], z.inputs[0])
        dx = N.new('ShaderNodeMath'); dx.operation = 'DIVIDE'; Lk.new(sp.outputs['X'], dx.inputs[0]); Lk.new(z.outputs[0], dx.inputs[1])
        dy = N.new('ShaderNodeMath'); dy.operation = 'DIVIDE'; Lk.new(sp.outputs['Y'], dy.inputs[0]); Lk.new(z.outputs[0], dy.inputs[1])
        cb = N.new('ShaderNodeCombineXYZ'); Lk.new(dx.outputs[0], cb.inputs['X']); Lk.new(dy.outputs[0], cb.inputs['Y'])
        no = N.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value = 0.55; no.inputs['Detail'].default_value = 12; no.inputs['Roughness'].default_value = 0.56
        Lk.new(cb.outputs['Vector'], no.inputs['Vector'])
        r1 = _rango(N, 0.47, 0.60); Lk.new(no.outputs['Fac'], r1.inputs['Value'])
        r2 = _rango(N, 0.0, 0.10); Lk.new(sp.outputs['Z'], r2.inputs['Value'])
        ma = N.new('ShaderNodeMath'); ma.operation = 'MULTIPLY'; Lk.new(r1.outputs[0], ma.inputs[0]); Lk.new(r2.outputs[0], ma.inputs[1])
        for fu, v_ in (('luz', 2.6), ('cam', 3.2)):
            bn = N.new('ShaderNodeBackground'); bn.inputs['Color'].default_value = (1.0, 0.99, 0.97, 1); bn.inputs['Strength'].default_value = v_
            mz = N.new('ShaderNodeMixShader'); Lk.new(ma.outputs[0], mz.inputs['Fac'])
            Lk.new(s_luz if fu == 'luz' else s_cam, mz.inputs[1]); Lk.new(bn.outputs['Background'], mz.inputs[2])
            if fu == 'luz':
                s_luz = mz.outputs[0]
            else:
                s_cam = mz.outputs[0]
    lp = N.new('ShaderNodeLightPath'); ms = N.new('ShaderNodeMixShader')
    Lk.new(lp.outputs['Is Camera Ray'], ms.inputs['Fac']); Lk.new(s_luz, ms.inputs[1]); Lk.new(s_cam, ms.inputs[2])
    Lk.new(ms.outputs[0], N['World Output'].inputs['Surface'])
    return w


def ajustes_render(muestras=64):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.samples = muestras; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 10; sc.cycles.diffuse_bounces = 5; sc.cycles.glossy_bounces = 3; sc.cycles.transparent_max_bounces = 12
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03; sc.cycles.use_light_tree = True
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - High Contrast'; sc.view_settings.exposure = -1.0
    sc.render.resolution_x = 1920; sc.render.resolution_y = 1080


def guardar(ruta):
    bpy.ops.wm.save_as_mainfile(filepath=ruta)
