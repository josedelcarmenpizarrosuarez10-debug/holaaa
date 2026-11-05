# -*- coding: utf-8 -*-
"""Ejemplo mínimo con datos inventados, solo para comprobar la instalación y servir de plantilla.
Uso: blender -b --factory-startup --python ejemplo_escena.py -- <salida.blend>
Sus medidas y colores no corresponden a ningún proyecto: en una obra real todo sale de sus láminas."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_escena as B
from shapely.geometry import Polygon, box

salida = sys.argv[sys.argv.index('--') + 1]
B.nueva_escena()
CT, CE, CA = B.coleccion('Terreno'), B.coleccion('Edificaciones'), B.coleccion('Arboles')
PROTO = B.coleccion('Prototipos (fuera del terreno)')

B.mat_pintura('muro', B.rgb(150, 150, 150)); B.mat_pintura('columna', B.rgb(90, 60, 60))
B.mat_concreto('piso', juntas=1.5); B.mat_pasto('pasto'); B.mat_calamina('cobertura', B.rgb(188, 191, 194), 'X')
B.mat_simple('asfalto', B.rgb(52, 50, 48), rug=0.85); B.mat_vidrio()

LOTE = box(0, 0, 40, 30)
VERDE = Polygon([(0, 0), (9, 0), (5, 11), (0, 8)])                    # área verde con borde diagonal: no debe salir en escalones
EDIF = box(14, 8, 32, 18)

B.caja('terreno', -200, -200, -0.2, 240, 230, 0, 'pasto', CT)
B.caja('calle', -200, -9, 0, 240, -3, 0.01, 'asfalto', CT)
B.piso_exacto('piso_concreto', LOTE, [VERDE, EDIF], 0.08, 'piso', CT)

M = B.Malla('edificio', CE)
for x in (14, 20, 26, 31.7):
    M.caja('columna', x, 8, 0, x + 0.3, 8.3, 3.2); M.caja('columna', x, 17.7, 0, x + 0.3, 18, 3.2)
M.caja('muro', 14, 8.05, 0, 32, 8.2, 3.2); M.caja('muro', 14, 17.8, 0, 32, 17.95, 3.2)
M.caja('muro', 14.05, 8, 0, 14.2, 18, 3.2); M.caja('muro', 31.8, 8, 0, 31.95, 18, 3.2)
M.caja('vidrio', 16, 8.0, 1.0, 19, 8.04, 2.5); M.caja('vidrio', 22, 8.0, 1.0, 25, 8.04, 2.5)
M.crear()
vs = [(13, 7, 3.2), (33, 7, 3.2), (33, 13, 5.0), (13, 13, 5.0), (13, 19, 3.2), (33, 19, 3.2)]    # cubierta a dos aguas
B.obj_mesh('cubierta', vs, [(0, 1, 2, 3), (3, 2, 5, 4)], 'cobertura', CE)

CERCO = LOTE.exterior.buffer(0.08)
B.prisma('cerco', CERCO, 0, 3.0, 'columna', CE)

OBST = EDIF.buffer(1.0).union(CERCO)
protos = B.prototipos_arbol(PROTO, cantidad=2)
hechos, fuera = B.plantar_arboles([(4, 4), (0.6, 0.6), (10, 25)], protos, OBST, CA)
print('arboles', hechos, 'descartados', fuera)

B.mundo(); B.ajustes_render()
B.guardar(salida)
print('guardado', salida)
