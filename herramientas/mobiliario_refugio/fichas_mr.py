# -*- coding: utf-8 -*-
"""Características técnicas por familia de equipo, mueble e implemento del Hogar de Refugio Temporal (CUI 2675514): las usan la
memoria descriptiva y las especificaciones técnicas, para que digan lo mismo. Parte de las familias del CAR Varones
(varones/mobiliario/fichas_mb.py, mismo catálogo de códigos de la arquitectura) y ajusta las propias del hogar: camarotes y
camas, taller de costura y los usuarios (mujeres, sus hijas e hijos)."""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'varones', 'mobiliario'))
import fichas_mb as F0  # noqa: E402

FAMILIAS = copy.deepcopy(F0.FAMILIAS)
FAMILIAS.pop('gas')
FAMILIAS['electro']['mat'] = [
    'Equipos nuevos, de marca reconocida, 220 V - 60 Hz, con garantía no menor de un año y servicio técnico en la región.',
    'Lavadoras de 20 kg de carga superior con tina de acero inoxidable; refrigeradoras de 315 L no frost; hornos microondas de 31 L; '
    'licuadoras de 1.5 L con vaso de vidrio; cocinas industriales de 2 hornillas de fierro fundido con quemadores de alta presión '
    'para gas licuado; relojes de pared de 30 cm de diámetro.']
FAMILIAS['silla']['nombre'] = 'Sillas y mesas de madera y metal'
FAMILIAS['silla']['mat'] = [
    'Estructura de tubo de acero LAC de 1" x 1/16" (o el indicado), soldado, con pintura en polvo electrostática horneada.',
    'Asiento, respaldo y tableros de madera tornillo o contraplacado de 18 mm, lijados, con cantos redondeados, sellador y barniz '
    'poliuretano; mesas de madera con tablero de 25 mm y faldón de refuerzo.',
    'Tapones de polipropileno en las patas. Las piezas regulables (M3, M4 y el taburete M35) tienen regulación de altura con pernos '
    'y perillas.']
FAMILIAS['cama'] = dict(
    nombre='Camarotes, camas y veladores',
    mat=['Camarote de una plaza y media (dos camas superpuestas) de madera tornillo cepillada o estructura metálica con pintura '
         'electrostática, con baranda de protección en la cama superior, escalera fija y tarima de listones; cama de dos plazas y '
         'cama cuna de una plaza con tarima incluida.',
         'Colchón de espuma de alta densidad con forro lavable para cada plaza, incluido en la partida.',
         'Velador de madera tornillo de 0.45 x 0.50 m con cajón, cantos redondeados y acabado en barniz poliuretano.'],
    proc=['Armar en la habitación según la lámina; fijar el camarote a la pared y verificar que no queden aristas ni tornillos salientes.'],
    ctrl=['Estructura firme, sin balanceo; baranda y escalera fijas; madera sin rajaduras; colchones de la medida de la tarima.'])
FAMILIAS['taller'] = dict(
    nombre='Máquinas y mobiliario del taller de costura',
    mat=['Máquina de corte textil eléctrica, 220 V - 60 Hz, con cuchilla y guarda de protección, base para mesa de corte, garantía '
         'no menor de un año y servicio técnico en la región.',
         'Maniquí de costura de busto ajustable, de fibra o espuma forrada, con pedestal metálico regulable.',
         'Mesa de corte textil de 0.80 x 1.50 x 0.75 m con tablero de melamina de 25 mm y estructura metálica con pintura electrostática.'],
    proc=['Verificar con la Supervisión la marca y el modelo de la máquina antes de la compra.',
          'Instalar cada máquina sobre su mesa M16 del taller de costura, conectarla a un tomacorriente con línea a tierra y probarla.'],
    ctrl=['Funcionamiento de la máquina en la prueba de entrega; guarda de protección instalada; mesas niveladas y firmes.'])
FAMILIAS['implemento']['mat'] = [
    'Implementos nuevos, de material no tóxico y resistente al uso intensivo, de las medidas y pesos indicados (pelotas oficiales por '
    'número, jabalinas, bala y disco de las masas indicadas, colchoneta forrada, piso encastrable de goma de 25 mm).',
    'Juegos del módulo infantil (tobogán con escalador, piscina de pelotas, juego de teatro, cojines) de plástico o espuma de alta '
    'densidad con forro lavable, sin piezas pequeñas desprendibles, aptos para niñas y niños pequeños.']

POR_CODIGO = {
    'E1': 'informatica', 'E2': 'informatica', 'E3': 'informatica', 'E6': 'informatica', 'E7': 'informatica', 'E9': 'informatica',
    'E18': 'informatica', 'E4': 'electro', 'E5': 'electro', 'E13': 'electro', 'E16': 'electro', 'E17': 'electro', 'E19': 'electro',
    'E10': 'taller', 'M9': 'taller', 'M16-T': 'taller',
    'M3': 'silla', 'M4': 'silla', 'M7': 'silla', 'M8': 'silla', 'M16': 'silla', 'M19': 'silla', 'M22': 'silla', 'M23': 'silla',
    'M35': 'silla', 'M21': 'melamina', 'M28': 'melamina', 'M31': 'melamina', 'M36': 'melamina', 'M37': 'melamina', 'M39': 'melamina',
    'M54': 'melamina', 'M56': 'melamina', 'M57': 'melamina', 'M13': 'metal', 'M51': 'metal', 'M64-C': 'metal', 'M26': 'inox',
    'M52': 'inox', 'M73': 'inox', 'M64': 'cama', 'M78': 'cama', 'M79': 'cama', 'M61': 'cama', 'M32': 'tapizado', 'M34': 'tapizado',
    'M63': 'tapizado', 'M69': 'pizarra', 'M60': 'higiene', 'M62': 'higiene', 'M75': 'higiene', 'M76': 'higiene', 'M77': 'higiene',
    'M20': 'topico', 'M27': 'topico', 'M65': 'topico', 'M67': 'topico', 'M70': 'topico', 'M71': 'topico', 'M15': 'otros', 'M68': 'otros',
}
FAMILIAS['otros']['mat'] = ['Atril de mesa de madera para dibujo y pintura, con inclinación regulable; parihuelas de madera tornillo de '
                            '0.90 x 0.50 x 0.20 m para el almacenaje sobre el piso.']


def familia(clave, ambiente=''):
    """Familia de una partida por su clave del metrado (código, M16-T, M64-C o K:edificación:ambiente:código)."""
    if clave in POR_CODIGO:
        return POR_CODIGO[clave]
    if clave.startswith('K:'):
        return 'topico' if 'TÓPICO' in clave else 'implemento'
    raise KeyError('partida sin familia: ' + clave)
