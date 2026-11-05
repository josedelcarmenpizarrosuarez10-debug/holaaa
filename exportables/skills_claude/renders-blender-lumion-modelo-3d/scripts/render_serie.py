# -*- coding: utf-8 -*-
"""Renderiza las vistas de un archivo JSON sobre un .blend ya armado.
Uso: blender -b modelo.blend --factory-startup -P render_serie.py -- vistas.json <carpeta> <muestras> <ancho> [vista1,vista2]

vistas.json:
{"sufijo": "_NOMBRE_PROYECTO",
 "vistas": {"A1_aerea_frontal": {"pos": [x, y, z], "mira": [x, y, z], "focal": 41, "sol_elev": 42, "sol_rot": 205},
            "PL1_planta_general": {"pos": [cx, cy, 150], "mira": [cx, cy, 0], "focal": 0, "escala": 135, "vertical": true,
                                   "sol_elev": 72, "sol_rot": 200, "ocultar": []}}}
focal 0 = planta ortográfica; escala = metros del lado mayor del cuadro. La rotación del sol es el rumbo desde donde viene
(205 = suroeste, 25 = noreste). "ocultar" = prefijos de objetos que no salen en esa vista.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector


def activar_gpu(sc):
    try:
        pr = bpy.context.preferences.addons['cycles'].preferences
    except KeyError:
        return None
    for tipo in ('OPTIX', 'CUDA', 'HIP', 'ONEAPI'):
        try:
            pr.compute_device_type = tipo; pr.get_devices()
        except TypeError:
            continue
        gpus = [d for d in pr.devices if d.type == tipo]
        if gpus:
            for d in pr.devices:
                d.use = d.type == tipo
            sc.cycles.device = 'GPU'
            return tipo, [d.name for d in gpus]
    return None


def camara(sc, v):
    cam = bpy.data.objects.get('Camara')
    if cam is None:
        cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara')); sc.collection.objects.link(cam)
    cam.location = v['pos']
    d = Vector(v['mira']) - Vector(v['pos']); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if v['focal'] == 0:
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = v['escala']
    else:
        cam.data.type = 'PERSP'; cam.data.lens = v['focal']
    cam.data.clip_start = 0.1; cam.data.clip_end = 2000
    sc.camera = cam
    sky = sc.world.node_tree.nodes.get('Sky Texture')
    if sky:
        sky.sun_elevation = math.radians(v.get('sol_elev', 45)); sky.sun_rotation = math.radians(v.get('sol_rot', 210))
        # con sol bajo llega poca luz directa: se sube la luz de cielo
        sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5 if v.get('sol_elev', 45) < 15 else 0.22
    pref = tuple(v.get('ocultar', ()))
    for o in bpy.data.objects:
        if o.type in ('MESH', 'EMPTY', 'CURVE', 'FONT') and o.name != 'Camara':
            o.hide_render = bool(pref) and o.name.startswith(pref)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    conf = json.load(open(a[0], encoding='utf-8'))
    sal = a[1]; os.makedirs(sal, exist_ok=True)
    muestras = int(a[2]) if len(a) > 2 else 64
    ancho = int(a[3]) if len(a) > 3 else 1280
    nombres = a[4].split(',') if len(a) > 4 else list(conf['vistas'])
    sc = bpy.context.scene
    print('GPU:', activar_gpu(sc), flush=True)
    sc.cycles.samples = muestras
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
    for n in nombres:
        v = conf['vistas'][n]
        camara(sc, v)
        sc.render.resolution_x, sc.render.resolution_y = (int(ancho * 9 / 16), ancho) if v.get('vertical') else (ancho, int(ancho * 9 / 16))
        sc.render.filepath = os.path.join(sal, n.upper() + conf.get('sufijo', '') + '.jpg')
        bpy.ops.render.render(write_still=True)
        print('listo', n, flush=True)
