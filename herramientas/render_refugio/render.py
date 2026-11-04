# -*- coding: utf-8 -*-
"""Renders del Hogar de Refugio: abre refugio.blend, pone cada cámara y renderiza.
Uso: python3.11 render.py <nombre|todas|serie_planos> [muestras] [ancho]  (o blender -b -P render.py -- ...)"""
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
    '08_patio_civico': ((44, 54, 1.7), (33, 66, 2.0), 20, 45, 230),
    '09_juegos_infantiles': ((26.9, 78.2, 1.6), (36, 83.5, 0.7), 20, 45, 230),
    '10_pabellon_habitaciones': ((79, 92, 8.5), (60, 113, 2.0), 24, 35, 250),
    '11_administracion': ((36, 56, 1.7), (22, 38, 2.6), 22, 40, 120),
    '12_sum': ((42.6, 72.5, 1.7), (50, 63, 2.4), 20, 40, 300),
    '13_vista_aerea_lateral': ((130, 40, 45), (36, 76, 0), 30, 35, 250),
    '14_vista_aerea_atardecer': ((-60, 20, 40), (36, 80, 0), 32, 4, 255),
    '15_tanque_estacionamiento': ((-2, 4, 2.0), (10, 26, 4.5), 22, 38, 200),
    '16_bancas_oc01': ((44.5, 68.8, 1.65), (34, 74.6, 1.6), 22, 40, 230),
    '17_cunetas_rejilla': ((44.6, 33.5, 1.55), (43.75, 52, 0.0), 24, 45, 230),
    '18_colector_frontal': ((55.5, 15.4, 1.6), (49.0, 17.3, 0.0), 22, 38, 200),
    '19_planta_red_drenaje': ((36.4, 74.6, 150), (36.4, 74.61, 0), 0, 75, 200, 127),
    '20_cunetas_patio_aerea': ((38.4, 26.0, 5.5), (39.5, 46, 0), 24, 42, 220),
    '22_fachada_perspectiva': ((27.0, 9.5, 1.65), (38.6, 18.5, 3.4), 22, 34, 160),
    '21_montante_cuneta': ((35.0, 89.3, 1.6), (32.0, 92.8, 1.5), 22, 40, 230),
}

# Serie con las edificaciones de los planos (03-11-2026): 7 aéreas, 2 de fachada, 2 peatonales entre edificaciones y 4 más
SERIE_PLANOS = {
    'A1_aerea_frontal_suroeste': ((-46, -44, 60), (28.4, 50.3, 0), 41, 42, 205),
    'A2_aerea_frontal_sureste': ((116, -42, 58), (44.4, 49.6, 0), 40, 40, 160),
    'A3_aerea_posterior_noreste': ((124, 196, 62), (41.1, 92.8, 0), 42.5, 42, 25),
    'A4_aerea_posterior_noroeste': ((-52, 190, 58), (27.2, 96.9, 0), 40.5, 40, 320),
    'A5_aerea_lateral_este': ((175, 72, 58), (37.7, 74, 0), 30, 36, 100),
    'A6_aerea_alta_frontal': ((36, -84, 128), (36.6, 63.6, 0), 49, 55, 190),
    'A7_aerea_atardecer_oeste': ((-92, 28, 46), (20.3, 71.7, 0), 35, 14, 262),
    'F1_fachada_principal': ((38.2, 1.5, 1.65), (38.2, 25, 3.6), 20, 34, 185),
    'F2_fachada_perspectiva': ((24.5, 8.6, 1.65), (39.0, 18.8, 3.6), 22, 34, 160),
    'P1_peatonal_eje_central': ((41.6, 25.4, 1.65), (37.5, 62, 2.4), 22, 34, 300),
    'P2_peatonal_entre_pabellones': ((29.0, 106.2, 1.65), (62.0, 109.6, 2.6), 20, 52, 140),
    'O1_patio_civico': ((42.6, 52.8, 1.7), (32.0, 66.0, 2.2), 20, 45, 230),
    'O2_administracion': ((35.0, 53.2, 1.7), (20.0, 38.0, 3.0), 22, 40, 120),
    'O3_sum_juegos': ((31.0, 72.6, 1.7), (52.0, 74.0, 3.0), 20, 44, 300),
    'O4_losa_deportiva': ((48, 140, 9), (15, 108, 4), 26, 38, 160),
    'E1_estacionamiento_autos': ((46.6, 27.5, 1.7), (60.5, 20.2, 1.7), 24, 62, 330),
    'E2_estacionamiento_motos': ((9.5, 23.6, 1.7), (21.0, 19.3, 1.2), 24, 62, 330),
    'B1_biohuerto': ((3.3, 49.4, 1.6), (8.5, 72, 1.0), 20, 58, 300),
    'B2_aerea_biohuerto': ((-14.0, 40.0, 22.0), (8.0, 62.0, 0.0), 28, 55, 250),
    'T1_tanque_elevado': ((11.5, 20.0, 1.7), (6.5, 28.0, 7.0), 16, 50, 120),
    'D1_patio_descarga_ptar': ((60.0, 52.0, 1.7), (67.5, 68.0, 1.5), 20, 55, 250),
    'PL1_planta_general': ((36.4, 74.1, 150), (36.4, 74.11, 0), 0, 72, 200, 135),
}
CAMARAS.update(SERIE_PLANOS)

# vista técnica en planta: sin coberturas ni árboles para que se vea toda la red de drenaje (las canaletas se mantienen)
OCULTAR = {'19_planta_red_drenaje': ('_techo', '_viga', '_cumbrera', '_hastial', 'techo_', 'cubierta_losa', 'arco', 'diag', 'viga_long', 'travesano',
                                     'oc01_cobertura', 'oc01_correa', 'pergola_liston', 'pergola_viga', 'arbol', 'tobogan_techo')}


def poner_camara(nombre):
    sc = bpy.context.scene
    pos, mira, focal, elev, rot = CAMARAS[nombre][:5]
    escala = CAMARAS[nombre][5] if len(CAMARAS[nombre]) > 5 else 222
    claves = OCULTAR.get(nombre, ())
    for o in bpy.data.objects:
        o.hide_render = any(o.name.startswith(k) or (k[0] == '_' and k in o.name) for k in claves) if o.type in ('MESH', 'EMPTY', 'CURVE', 'FONT') and o.name != 'Camara' else o.hide_render
    cam = bpy.data.objects.get('Camara')
    if cam is None:
        cd = bpy.data.cameras.new('Camara'); cam = bpy.data.objects.new('Camara', cd); sc.collection.objects.link(cam)
    cam.location = pos
    d = Vector(mira) - Vector(pos); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if focal == 0:                                                   # planta: proyección ortogonal
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = escala
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
    ARG = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]   # bpy de pip o blender -b -P render.py -- ...
    nombres = list(SERIE_PLANOS) if ARG[0] == 'serie_planos' else list(CAMARAS) if ARG[0] == 'todas' else ARG[0].split(',')
    try:                                                               # GPU (OptiX o CUDA) si hay tarjeta NVIDIA
        pr = bpy.context.preferences.addons['cycles'].preferences
        for tipo in ('OPTIX', 'CUDA'):
            pr.compute_device_type = tipo; pr.get_devices()
            gpus = [d for d in pr.devices if d.type == tipo]
            if gpus:
                for d in pr.devices: d.use = d.type == tipo
                sc.cycles.device = 'GPU'; print('GPU', tipo, [d.name for d in gpus], flush=True); break
    except Exception as ex:
        print('sin GPU:', ex)
    JPG = os.environ.get('FORMATO_RENDERS', 'PNG').upper() == 'JPG'
    if JPG:
        sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
    sc.cycles.samples = int(ARG[1]) if len(ARG) > 1 else 96
    ancho = int(ARG[2]) if len(ARG) > 2 else 1920
    sc.render.resolution_x = ancho; sc.render.resolution_y = int(ancho * 9 / 16)
    sc.cycles.threads = os.cpu_count(); sc.render.threads_mode = 'FIXED'; sc.render.threads = os.cpu_count()
    VERTICAL = ('19_planta_red_drenaje', 'PL1_planta_general')         # plantas en formato vertical, como el plano
    for n in nombres:
        poner_camara(n)
        if n in VERTICAL:
            sc.render.resolution_x = int(ancho * 9 / 16); sc.render.resolution_y = ancho
        else:
            sc.render.resolution_x = ancho; sc.render.resolution_y = int(ancho * 9 / 16)
        archivo = (n.upper() + '_HOGAR_REFUGIO') if n in SERIE_PLANOS else n      # mismo estilo de nombre de los entregables
        sc.render.filepath = os.path.join(SAL, archivo + ('.jpg' if JPG else '.png'))
        bpy.ops.render.render(write_still=True)
        print('listo', n, flush=True)
