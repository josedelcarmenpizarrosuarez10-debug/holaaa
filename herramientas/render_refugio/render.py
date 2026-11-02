# -*- coding: utf-8 -*-
"""Renders del Hogar de Refugio: abre refugio.blend, pone cada cámara y renderiza.
Uso: python3.11 render.py <nombre|todas> [muestras] [ancho]"""
import bpy, math, os, sys
from mathutils import Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
SAL = os.path.join(AQUI, os.environ.get('SALIDA_RENDERS', 'renders')); os.makedirs(SAL, exist_ok=True)

# nombre: (posición de la cámara, punto al que mira, distancia focal mm, elevación del sol, rotación del sol)
CAMARAS = {
    '01_vista_aerea_frontal': ((-38, -48, 52), (36, 72, 0), 30, 40, 200),
    '02_vista_aerea_posterior': ((118, 190, 58), (36, 72, 0), 30, 42, 20),
    '03_planta_general': ((36.5, 72.0, 150), (36.5, 72.01, 0), 0, 72, 200),
    '04_fachada_principal': ((38.2, 1.5, 1.65), (38.2, 25, 3.6), 20, 34, 185),
    '05_ingreso_garita': ((47, 7.5, 1.65), (37.5, 17, 3.2), 22, 32, 200),
    '06_losa_deportiva_exterior': ((48, 140, 9), (15, 108, 4), 26, 38, 160),
    '07_losa_deportiva_interior': ((22, 96, 1.7), (12, 118, 3.0), 18, 45, 140),
    '08_patio_central_pergola': ((44, 54, 1.7), (33, 66, 2.0), 20, 45, 230),
    '09_juegos_infantiles': ((27.5, 73.5, 1.6), (36, 84, 1.0), 20, 45, 230),
    '10_pabellon_habitaciones': ((79, 92, 8.5), (60, 113, 2.0), 24, 35, 250),
    '11_administracion': ((36, 56, 1.7), (22, 38, 2.6), 22, 40, 120),
    '12_sum': ((42.6, 72.5, 1.7), (50, 63, 2.4), 20, 40, 300),
    '13_vista_aerea_lateral': ((130, 40, 45), (36, 76, 0), 30, 35, 250),
    '14_vista_aerea_atardecer': ((-60, 20, 40), (36, 80, 0), 32, 4, 255),
    '15_tanque_estacionamiento': ((-2, 4, 2.0), (10, 26, 4.5), 22, 38, 200),
}


def poner_camara(nombre):
    sc = bpy.context.scene
    pos, mira, focal, elev, rot = CAMARAS[nombre]
    cam = bpy.data.objects.get('Camara')
    if cam is None:
        cd = bpy.data.cameras.new('Camara'); cam = bpy.data.objects.new('Camara', cd); sc.collection.objects.link(cam)
    cam.location = pos
    d = Vector(mira) - Vector(pos); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if focal == 0:                                                   # planta: proyección ortogonal
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = 222
    else:
        cam.data.type = 'PERSP'; cam.data.lens = focal
    cam.data.clip_end = 2000; cam.data.clip_start = 0.1
    sc.camera = cam
    sky = sc.world.node_tree.nodes['Sky Texture']
    sky.sun_elevation = math.radians(elev); sky.sun_rotation = math.radians(rot)
    sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5 if elev < 15 else 0.22


if __name__ == '__main__':
    bpy.ops.wm.open_mainfile(filepath=os.path.join(AQUI, 'refugio.blend'))
    sc = bpy.context.scene
    nombres = list(CAMARAS) if sys.argv[1] == 'todas' else sys.argv[1].split(',')
    sc.cycles.samples = int(sys.argv[2]) if len(sys.argv) > 2 else 96
    ancho = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
    sc.render.resolution_x = ancho; sc.render.resolution_y = int(ancho * 9 / 16)
    sc.cycles.threads = os.cpu_count(); sc.render.threads_mode = 'FIXED'; sc.render.threads = os.cpu_count()
    for n in nombres:
        poner_camara(n)
        sc.render.filepath = os.path.join(SAL, n + '.png')
        bpy.ops.render.render(write_still=True)
        print('listo', n, flush=True)
