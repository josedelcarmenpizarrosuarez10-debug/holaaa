# -*- coding: utf-8 -*-
"""Prepara un .blend para llevarlo a Lumion: exporta FBX (y DAE si esta versión de Blender lo trae) y las tablas de apoyo.
Uso: blender -b modelo.blend --factory-startup -P exporta_lumion.py -- <carpeta> <nombre> [vistas.json] [prefijos_excluidos]
prefijos_excluidos, separados por coma: objetos que no van (por defecto los árboles, que se reemplazan por los de Lumion).
Salidas en <carpeta>:
  <nombre>.fbx, texturas copiadas junto a él; <nombre>.dae si se puede
  materiales_lumion.csv : material, color RGB y objetos que lo usan (Lumion agrupa las superficies por nombre de material)
  arboles_lumion.csv    : x, y, escala y radio de copa de cada árbol, para plantar los de la biblioteca en el mismo sitio
  vistas_lumion.csv     : posición y mira de las vistas aprobadas
Lumion no da soporte oficial a Blender: probar la importación en su equipo y conservar los nombres de material entre exportaciones.
"""
import csv
import json
import math
import os
import sys

import bpy
from mathutils import Vector


def srgb(c):
    c = max(0.0, min(1.0, c))
    return round(255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055))


def color_material(m):
    p = m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
    if p is None:
        return ''
    return '%d-%d-%d' % tuple(srgb(c) for c in p.inputs['Base Color'].default_value[:3])


def tiene_procedural(m):
    return any(n.bl_idname.startswith('ShaderNodeTex') and n.bl_idname != 'ShaderNodeTexImage' for n in m.node_tree.nodes) if m.use_nodes else False


def caja_mundo(objs):
    pts = [o.matrix_world @ Vector(q) for o in objs for q in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    sal, nombre = a[0], a[1]; os.makedirs(sal, exist_ok=True)
    vistas = a[2] if len(a) > 2 and a[2] != '-' else None
    excl = tuple(a[3].split(',')) if len(a) > 3 else ('arbol', 'tronco', 'follaje', 'nucleo_copa')

    # árboles: posiciones aparte, sin geometría en el modelo
    arboles = [o for o in bpy.data.objects if o.type == 'EMPTY' and o.instance_type == 'COLLECTION' and o.name.startswith('arbol')]
    with open(os.path.join(sal, 'arboles_lumion.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(['x (m)', 'y (m)', 'escala'])
        for o in arboles:
            w.writerow([round(o.location.x, 2), round(o.location.y, 2), round(o.scale.x, 3)])

    # visibles = lo que queda en la escena activa y no está excluido ni fuera del terreno (prototipos)
    objs = [o for o in bpy.context.view_layer.objects if o.type == 'MESH' and not o.name.startswith(excl) and o.matrix_world.translation.y > -1000
            and not any(c.name.startswith(('arbol_', 'Prototipos')) for c in o.users_collection)]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    usos = {}
    for o in objs:
        for s in o.material_slots:
            if s.material:
                usos.setdefault(s.material.name, (s.material, []))[1].append(o.name)
    with open(os.path.join(sal, 'materiales_lumion.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(['material', 'color RGB que llega', 'objetos', 'textura de nodos (no pasa a Lumion)', 'acabado asignado en Lumion (a llenar)'])
        for n, (m, l) in sorted(usos.items()):
            w.writerow([n, color_material(m), len(l), 'sí' if tiene_procedural(m) else 'no', ''])

    lo, hi = caja_mundo(objs)
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    print('caja del modelo (m):', [round(q, 2) for q in lo], [round(q, 2) for q in hi], flush=True)
    if math.hypot(cx, cy) > 1000:
        print('AVISO: el modelo está a %.0f m del origen. El punto de inserción de Lumion es el 0,0,0 de Blender: usar coordenadas locales.' % math.hypot(cx, cy), flush=True)

    ruta = os.path.join(sal, nombre + '.fbx')
    bpy.ops.export_scene.fbx(filepath=ruta, use_selection=True, object_types={'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='FACE',
                             path_mode='COPY', embed_textures=False, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', bake_anim=False)
    print('FBX', ruta, os.path.getsize(ruta), flush=True)
    if hasattr(bpy.ops.wm, 'collada_export'):
        try:
            bpy.ops.wm.collada_export(filepath=os.path.join(sal, nombre + '.dae'), selected=True, apply_modifiers=True, triangulate=False)
            print('DAE', os.path.getsize(os.path.join(sal, nombre + '.dae')), flush=True)
        except (RuntimeError, AttributeError) as ex:
            print('DAE no disponible:', ex, flush=True)

    # marcas: un poste de 4 m por árbol, en el mismo sistema de coordenadas, para plantar los de la biblioteca sobre ellos
    if arboles:
        vs, fs = [], []
        for o in arboles:
            x, y, n = o.location.x, o.location.y, 8
            b = len(vs)
            vs += [(x + 0.25 * math.cos(i * 2 * math.pi / n), y + 0.25 * math.sin(i * 2 * math.pi / n), z) for z in (0.0, 4.0) for i in range(n)]
            fs += [(b + i, b + (i + 1) % n, b + n + (i + 1) % n, b + n + i) for i in range(n)] + [tuple(b + n + i for i in range(n))]
        me = bpy.data.meshes.new('marca_arbol'); me.from_pydata(vs, [], fs); me.update()
        ma = bpy.data.materials.new('marca_arbol'); ma.use_nodes = True
        ma.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1.0, 0.02, 0.6, 1.0)
        me.materials.append(ma)
        mo = bpy.data.objects.new('marca_arbol', me); bpy.context.scene.collection.objects.link(mo)
        bpy.ops.object.select_all(action='DESELECT'); mo.select_set(True); bpy.context.view_layer.objects.active = mo
        bpy.ops.export_scene.fbx(filepath=os.path.join(sal, nombre + '_marcas_arboles.fbx'), use_selection=True, object_types={'MESH'},
                                 apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', bake_anim=False)

    if vistas:
        conf = json.load(open(vistas, encoding='utf-8'))
        with open(os.path.join(sal, 'vistas_lumion.csv'), 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';'); w.writerow(['vista', 'x', 'y', 'z', 'mira x', 'mira y', 'mira z', 'focal mm', 'sol elev', 'sol rumbo'])
            for n, v in conf['vistas'].items():
                w.writerow([n, *v['pos'], *v['mira'], v['focal'], v.get('sol_elev', ''), v.get('sol_rot', '')])
    print('listo', len(objs), 'objetos', len(usos), 'materiales', len(arboles), 'arboles', flush=True)
