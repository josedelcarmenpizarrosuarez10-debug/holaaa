# -*- coding: utf-8 -*-
"""Nota interna (no va al expediente) de señalización y seguridad del Hogar de Refugio Temporal (CUI 2675514): lectura del
plano de la arquitecta, cotejo leyenda / planta / metrado, criterio de cada cantidad adoptada, observaciones que se deben
corregir en el plano y puntos para confirmar.

Uso: python3 herramientas/senalizacion_refugio/nota_sr.py
Salida: entregables/revision_interna/REVISION_SENALIZACION_Y_SEGURIDAD_HOGAR_REFUGIO.docx
"""
import os
import sys

import docx
from docx.shared import Cm, Pt

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI)
for d in (AQUI, HER, os.path.join(HER, 'varones', 'senalizacion')):
    sys.path.insert(0, d)
import datos_sr as D  # noqa: E402
import incompatibilidades_refugio as IR  # noqa: E402  (formato de las notas internas)
import memoria_se as MS  # noqa: E402

SALIDA = os.path.join(D.SAL, 'revision_interna/REVISION_SENALIZACION_Y_SEGURIDAD_HOGAR_REFUGIO.docx')
FIG = os.path.join(D.SAL, 'figuras_senalizacion')
LS = D.LS


def observaciones(P):
    rot = P['rotulo']
    proy = next((t for t in rot if 'I.E. 292' in t), '')
    cui_otro = proy.split('CUI')[-1].strip() if 'CUI' in proy else ''
    pts = {p['clave']: p for p in D.partidas(P) if p['und']}
    ole = D.ole_senal(P)
    dt = P['bloques']['sensorhumo']['fuera_del_terreno']
    return [
        ('Rótulo', 'El rótulo de la lámina es de otro proyecto: “Mejoramiento y ampliación del servicio de educación inicial y '
         'primaria en la I.E. 292 ... distrito de La Banda de Shilcayo” (CUI %s), lámina “S-01” y “01-02”, distrito Banda de '
         'Shilcayo, con el coordinador y la especialista de ese proyecto.' % cui_otro,
         'Poner el nombre del proyecto del hogar con el CUI 2675514, distrito de Morales, y el código de la lámina del índice de '
         'planos de arquitectura: %s %s.' % (LS, D.LAMINA_S[1].upper())),
        ('Código de lámina', 'La memoria de evacuación de arquitectura cita “lámina SE-S-01” para evacuación y “lámina SE-E-02” para '
         'señalización; el índice de planos de arquitectura dice %s %s y %s %s.' % (D.LAMINA_E[0], D.LAMINA_E[1], LS, D.LAMINA_S[1]),
         'Usar en el rótulo y en la memoria los códigos del índice (%s evacuación, %s señalización).' % (D.LAMINA_E[0], LS)),
        ('Zona segura en caso de sismo', 'La leyenda indica 210; en la planta hay %d señales.' % pts['ZONA SEGURA EN']['total'],
         'Corregir la leyenda a %d.' % pts['ZONA SEGURA EN']['total']),
        ('Extintor PQS', 'La leyenda indica 44 señales de ubicación de extintor PQS; en la planta hay %d (bloque “extintor1”, que '
         'contiene al símbolo de la leyenda). La memoria de evacuación de arquitectura indica 33 extintores PQS de 9 kg.' % pts[
             'SEÑAL DE UBICACIÓN DE EXTINTOR PQS']['total'],
         'Corregir la leyenda a 33 e indicar en ella el equipo: extintor PQS tipo ABC de 9 kg.'),
        ('Altura de la señal de extintor', 'La leyenda da 1.20 m a las señales de extintor: el extintor de 9 kg se cuelga con su parte '
         'superior a no más de 1.50 m (NTP 350.043-1) y la señal va encima del equipo, de modo que a 1.20 m quedaría tapada.',
         'Corregir la altura a 1.80 m (borde inferior de la señal), la adoptada en el metrado y las especificaciones.'),
        ('Unidad de luces de emergencia', 'La leyenda indica 77, que son los bloques “LE”; además hay 38 bloques “A$C7A2016C2” con el '
         'mismo dibujo (es el símbolo de la leyenda y el bloque “LE” lo contiene), casi todos en las habitaciones (E-06: 10, E-07: '
         '15, E-08: 10, E-05: 2, E-02: 1). Total dibujado: %d.' % pts['UNIDAD DE LUCES']['total'],
         'Corregir la leyenda a %d (se metran todas las dibujadas) y usar un solo nombre de bloque.' % pts['UNIDAD DE LUCES']['total']),
        ('Detector de humo', 'La leyenda indica 68; dentro del terreno hay %d. La copia restante está suelta fuera del dibujo, en '
         'E %.1f N %.1f (coordenadas del doble de las del terreno), y no se metra.' % (pts['DETECTOR DE HUMO']['total'], dt[0][0], dt[0][1]),
         'Borrar la copia suelta y corregir la leyenda a %d.' % pts['DETECTOR DE HUMO']['total']),
        ('Punto ecológico', 'La leyenda indica 00, pero en los exteriores hay %d puntos ecológicos dibujados (cuatro contenedores cada '
         'uno).' % pts['PUNTO ECOL']['total'], 'Corregir la leyenda a %d.' % pts['PUNTO ECOL']['total']),
        ('Atención riesgo eléctrico', 'La señal no es un bloque: es una imagen pegada (OLE). El DXF guarda solo su tamaño, no su '
         'posición, por lo que no se puede ubicar ni asignar a cada edificación. En el espacio modelo hay %d imágenes iguales '
         '(%.2f x %.2f m); la leyenda indica 38.' % (len(ole), ole[0]['ancho'], ole[0]['alto']),
         'Reemplazar las imágenes por un bloque de señal (así se cuentan y ubican) y confirmar la cantidad: el metrado toma las %d '
         'imágenes; si una es copia sobrante, bajar a 38 en el metrado y en la leyenda.' % len(ole)),
        ('Letreros de aforo', 'Los %d letreros de aforo de la planta tienen el texto “__ PERSONAS”, sin el número de personas.' % pts[
            'LETRERO DE AFORO']['total'], 'Indicar en la lámina el aforo de cada ambiente (cálculo de aforo de arquitectura) para '
         'imprimir cada letrero con su número.'),
        ('Luces de emergencia “con braille”', 'La leyenda describe la unidad de luces de emergencia “con braille”; es un equipo de '
         'iluminación y no lleva texto en braille.', 'Quitar “con braille” de esa fila (la partida del metrado es “unidad de luces de '
         'emergencia”).'),
        ('Detección y alarma', 'Se dibujan %d detectores de humo, pero las filas de central de alarma, panel de alarma, pulsador '
         '(alarma contra incendios) y avisador sonoro están en 00; la memoria de arquitectura menciona “detección y alarma contra '
         'incendio”.' % pts['DETECTOR DE HUMO']['total'],
         'Definir con instalaciones eléctricas si los detectores son autónomos con alarma propia (como se especificó) o van a una '
         'central con pulsadores y avisadores; en ese caso dibujarlos y metrarlos.'),
        ('Bloques con otro nombre', 'Varios símbolos de la planta no son el bloque de la leyenda: salida (“salida” / “swkiswkis”), '
         'SS.HH. PHD (“sdsadsa” / “15”), extintor (“extintor1”, que contiene a “*U2804”), luces (“LE” y “A$C7A2016C2”), aforo '
         '(“A$C6B5B2E50”, que contiene a “dtjrtj”).', 'Usar en la planta el mismo bloque de la leyenda, para que la selección rápida '
         'de AutoCAD dé las cantidades de la leyenda.'),
        ('Ortografía', 'Leyenda: “ALARMA CONTRA INCEDIOS”; ambientes: “TALLER DE RESPOSTERÍA”, “DISPENSA”.',
         'Corregir a “INCENDIOS”, “REPOSTERÍA” y “DESPENSA”.'),
        ('Lámina de evacuación', 'No se recibió la lámina %s (rutas de evacuación y zonas de reunión); la fila “zona de reuniones” de '
         'la leyenda está en 00. La memoria de evacuación de arquitectura describe la zona de evacuación como un círculo amarillo '
         'de 4.30 m de diámetro exterior con línea de 0.15 m.' % D.LAMINA_E[0],
         'Entregar la lámina %s; con ella se agrega la partida de zonas de reunión pintadas en el piso (número de círculos) y la '
         'longitud de las rutas a la memoria.' % D.LAMINA_E[0]),
        ('Población', 'La memoria de evacuación de arquitectura indica 41 residentes; la tabla de plazas de la memoria descriptiva de '
         'arquitectura suma 113 plazas en 23 habitaciones (ocupantes para la evacuación = camas, A.030 art. 5).',
         'Usar 113 residentes (capacidad máxima 305 personas con 62 de personal y 130 temporales), como en la memoria de señalización.'),
    ]


def generar():
    P = D.plano(); pts = D.partidas(P)
    R = IR.R
    d = docx.Document(); s = d.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = d.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    M = R.Memoria(); M.d = d
    if d.paragraphs:
        d.paragraphs[0]._p.getparent().remove(d.paragraphs[0]._p)
    W = (s.page_width - s.left_margin - s.right_margin) / 360000.0; M.ancho = W
    M.par('SEÑALIZACIÓN Y SEGURIDAD: LECTURA DEL PLANO, COTEJO CON LA LEYENDA Y OBSERVACIONES', 12.5, True, color=R.GRANATE,
          centro=True, despues=2)
    M.par('Hogar de Refugio Temporal - Mujeres Violentadas - CUI N.° %s  |  Documento de trabajo, no forma parte del expediente' % D.CUI,
          9, color=R.GRIS, centro=True, despues=10)
    n_ole = len(D.ole_senal(P))
    M.par('Se leyó el DXF del plano de señalización de la arquitecta (292 MB): la leyenda de 27 filas, cada símbolo de señal dibujado '
          'en la planta (posición = centro de su contorno) y la edificación donde cae (contorno del bloque de cada edificación de la '
          'planta general, con 0.60 m de margen), los símbolos fuera del terreno, las imágenes pegadas (%d de la señal de riesgo '
          'eléctrico) y el rótulo. Se revisó que no hubiera símbolos superpuestos (ninguno a menos de 0.10 m de otro igual) y que la '
          'presentación A1 muestre la planta a escala 1/150. El metrado toma lo dibujado en la planta; donde la leyenda no coincide, '
          'se corrige la leyenda.' % n_ole)

    def sec(t):
        M.par(t, 11, True, color=R.GRANATE, antes=8, despues=4)

    sec('1. COTEJO DE LA LEYENDA CON LA PLANTA Y EL METRADO')
    filas = []
    for p in pts:
        if not p['und']:
            continue
        dif = p['total'] - p['leyenda']
        filas.append([p['item'], p['desc'].replace(' CON BRAILLE', '').capitalize().replace('pqs', 'PQS').replace('(pqs)', '(PQS)')
                      .replace(' abc', ' ABC'), p['leyenda'], p['total'], ('%+d' % dif) if dif else 'conforme'])
    filas.append(['', 'TOTAL', sum(f[2] for f in filas), sum(f[3] for f in filas), ''])
    MS.tabla(M, 'Cantidades: leyenda de la lámina, planta y metrado', ['ITEM', 'PARTIDA', 'LEYENDA', 'METRADO', 'DIFERENCIA'], filas,
             [1.4, W - 8.2, 2.0, 2.2, 2.6], tam=8.5, izq=(1,))
    M.par('El extintor (05.01) es uno por cada señal de ubicación de extintor. Las demás filas de la leyenda (avisador sonoro, escalera '
          'de salida, extintores CO2 y K, alarma, barra antipánico, botiquín, riesgo de descarga, prohibido el ingreso, sensor de '
          'temperatura, pozo a tierra, central y panel de alarma y zona de reuniones) están en 00 y no tienen símbolos en la planta: '
          'no se metran.', despues=4)

    sec('2. OBSERVACIONES QUE SE DEBEN CORREGIR EN EL PLANO')
    MS.tabla(M, 'Observaciones al plano de señalización', ['N.°', 'TEMA', 'OBSERVACIÓN', 'CORRECCIÓN'],
             [[k, a, b, c] for k, (a, b, c) in enumerate(observaciones(P), 1)], [0.9, 2.8, (W - 3.7) * 0.55, (W - 3.7) * 0.45],
             tam=8, izq=(1, 2, 3))

    sec('3. PARA CONFIRMAR CON LA ARQUITECTA')
    MS.tabla(M, 'Puntos para confirmar', ['TEMA', 'QUÉ CONFIRMAR', 'POR QUÉ'], [
        ['Extintor de la cocina', 'La cocina (E-05) solo tiene extintores PQS; la leyenda tiene la fila de extintor clase K en 00.',
         'Para fuegos de aceites y grasas de cocina conviene un extintor clase K; si se agrega, dibujarlo y metrarlo.'],
        ['Botiquín', 'La fila de botiquín de primeros auxilios está en 00.', 'El tópico (E-02) tiene botiquín en el mobiliario; '
         'conviene señalizarlo.'],
        ['Braille en señales altas', 'Salida, dirección de evacuación y aforo van a 2.10 m, fuera del alcance de la mano.',
         'Para que el braille sea útil, su placa puede ir en el muro junto a la puerta, a una altura accesible.'],
        ['Garita', 'En exteriores, al sur de la administración, hay una señal de SS.HH. mixto y un detector de humo.',
         'Se asumen en la garita de control con su SS.HH.; confirmar.'],
        ['Habitaciones', 'Los rótulos de ambientes de la planta suman 24 habitaciones (4 “simple tipo 2”); el programa tiene 23 (3 '
         'simples tipo II).', 'Revisar si un rótulo está repetido; la población se tomó del programa (113 plazas).'],
    ], [3.0, 7.2, W - 10.2], tam=8.5, izq=(0, 1, 2))

    d.add_page_break()
    sec('4. SÍMBOLOS CONTADOS EN LA PLANTA')
    M.par('Cada círculo de color marca un símbolo contado en el metrado (las señales de riesgo eléctrico no se pueden marcar porque '
          'el DXF no trae su posición):', despues=4)
    MS.figura(M, os.path.join(FIG, 'conteo.png'), 'Símbolos contados en la planta de la lámina %s' % LS, 14.5, 'Fuente: plano de señalización de la arquitecta.')
    d.core_properties.author = ''
    d.core_properties.title = 'Señalización y seguridad: lectura del plano y observaciones - Hogar de Refugio'
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    d.save(SALIDA)
    return SALIDA


if __name__ == '__main__':
    print(generar())
