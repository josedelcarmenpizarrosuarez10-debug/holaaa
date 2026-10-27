# -*- coding: utf-8 -*-
"""Especificaciones técnicas de evacuación y señalización - CAR Varones (CUI 2705619).

Mismo motor y formato de las especificaciones del expediente (JSON -> herramientas/especificaciones/docx_espec.js): carátula
con la foto del proyecto, índice, capítulo I de generalidades y capítulo II con una ficha por partida (descripción,
materiales, equipos y herramientas, procedimiento, control de calidad, seguridad, unidad, método de medición y forma de pago).
Las partidas (código, descripción, unidad y cantidad) son las del metrado (metrado_se.py / datos_se.py), en el mismo orden.

Uso: python3 herramientas/varones/senalizacion/espec_se.py
Salida: entregables_varones/ESPECIFICACIONES_TECNICAS_EVACUACION_Y_SENALIZACION_CAR_VARONES.docx
"""
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__)); VAR = os.path.dirname(AQUI); HER = os.path.dirname(VAR)
for d in (AQUI, VAR):
    sys.path.insert(0, d)
import datos_se as D  # noqa: E402
import caratulas_v as V  # noqa: E402

ESP = os.path.join(HER, 'especificaciones')
JSON = os.path.join(ESP, '_json', 'varones_senalizacion.json')
SALIDA = os.path.join(D.SAL, 'ESPECIFICACIONES_TECNICAS_EVACUACION_Y_SENALIZACION_CAR_VARONES.docx')


def p(t): return ['p', t]
def l(*it): return ['l', list(it)]
def t(cab, filas, pesos=None): return ['t', cab, filas] + ([pesos] if pesos else [])


EPP = ('Uso obligatorio de equipo de protección personal: casco, lentes de seguridad, guantes y calzado de seguridad '
       '(D.S. N.° 011-2019-TR y Norma G.050).')
SEG_ALTURA = l(EPP, 'Para instalar a más de 1.80 m usar escalera de tijera en buen estado o andamio estable; no trabajar sobre muebles.',
               'Taladro con cable y enchufe en buen estado, conectado a tablero con interruptor diferencial; protección auditiva al perforar concreto.')


def pago(cant):
    return [p('El pago se efectuará al precio unitario del presupuesto por unidad (und), de acuerdo con el avance valorizado y con '
              'la conformidad de la Supervisión. Dicho precio y pago constituye compensación total por la mano de obra (incluidas las '
              'leyes sociales), los materiales, el equipo, las herramientas, el transporte, la instalación y todo imprevisto necesario '
              'para ejecutar la partida según esta especificación y la lámina SE-S-01. Cantidad del metrado: %d und.' % cant)]


def ficha(desc, mat, equ, proc, ctrl, seg, medicion, cant):
    desc, mat, equ, proc, ctrl, seg, medicion = ([x] if isinstance(x[0], str) else x for x in (desc, mat, equ, proc, ctrl, seg, medicion))
    return [['DESCRIPCIÓN', desc], ['MATERIALES', mat], ['EQUIPOS Y HERRAMIENTAS', equ], ['PROCEDIMIENTO DE EJECUCIÓN', proc],
            ['CONTROL DE CALIDAD Y TOLERANCIAS', ctrl], ['SEGURIDAD Y SALUD EN EL TRABAJO', seg],
            ['UNIDAD DE MEDIDA', [p('La unidad de medida es la unidad (und).')]], ['MÉTODO DE MEDICIÓN', medicion],
            ['FORMA DE PAGO', pago(cant)]]


def minus(desc):
    s = desc.lower()
    for a, b in (('pqs', 'PQS'), ('co2', 'CO2'), (' abc', ' ABC'), ('ss.hh.', 'SS.HH.')):
        s = s.replace(a, b)
    return s


def ubicacion_txt(pt):
    if pt['sin_ubicar']:
        return ('según la lámina SE-S-01, en los tableros, ambientes técnicos y equipos de alarma que indica, en coordinación con '
                'el plano de instalaciones eléctricas')
    eds = [c for c, n in pt['por'].items() if n]
    return 'según la planta de la lámina SE-S-01 (%s)' % ', '.join(eds)


def senal(pt):
    foto = 'fotoluminiscente' in pt['material']
    desc = [p('Comprende el suministro e instalación de la %s, de %s, con el pictograma, los colores y la forma de la NTP 399.010-1 '
              'y el texto en braille (Norma A.120). %s Se instala %s, a %s del piso terminado (borde inferior de la señal), %s.' % (
                  minus(pt['desc']), pt['dim'], pt['uso'],
                  ubicacion_txt(pt), pt['altura'],
                  'visible desde la ruta de evacuación y sin obstáculos delante' if foto else 'en un lugar visible'))]
    mat = l(pt['material'] + '.',
            'Vinil %s de alta calidad, resistente a la humedad y a los rayos ultravioleta; colores de seguridad según la NTP 399.010-1.' % (
                'fotoluminiscente con luminancia que permita leer la señal en la oscuridad después de un corte de energía' if foto else 'adhesivo impreso'),
            'Placa de acrílico de 2 mm con la leyenda de la señal en braille grado 1 en relieve, pegada en la parte inferior de la señal.',
            'Fijación: tarugos de PVC de 1/4" y tornillos autorroscantes de acero inoxidable en muros de albañilería o concreto; en '
            'superficies de vidrio, drywall o metal, cinta doble contacto de alta adherencia o pegamento de contacto.')
    equ = l('Taladro percutor con broca para concreto de 1/4", destornillador, nivel de mano, wincha, lápiz y escalera de tijera.')
    proc = l('Verificar en la lámina SE-S-01 la ubicación de cada señal y marcarla en obra con la Supervisión.',
             'Limpiar y secar la superficie de apoyo; debe estar terminada (tarrajeada y pintada).',
             'Presentar la señal con el nivel a la altura indicada (%s al borde inferior) y marcar las perforaciones.' % pt['altura'],
             'Perforar, colocar los tarugos y fijar la señal con los tornillos sin deformar la lámina; colocar la placa de braille.',
             'Retirar la película protectora y limpiar la superficie de la señal.')
    ctrl = l('Señales sin fisuras, burbujas ni decoloraciones, con colores, pictograma y dimensiones según la NTP 399.010-1.',
             'Tolerancia de altura: ± 2 cm; señal nivelada y firme.',
             'Lectura de la placa de braille completa y legible.' + (' Comprobar con la luz apagada que la señal se vea.' if foto else ''))
    med = [p('Se contará el número de señales suministradas e instaladas a satisfacción de la Supervisión, %s.' % (
        'según la leyenda de la lámina SE-S-01 y su ubicación en obra' if pt['sin_ubicar'] else 'según la planta de la lámina SE-S-01 y la hoja METRADO'))]
    return ficha(desc, mat, equ, proc, ctrl, SEG_ALTURA, med, pt['total'])


def zona_reunion(pt):
    z = D.zona_segura()
    desc = [p('Comprende el trazo y pintado en el piso de concreto de las zonas de reunión exteriores (zonas seguras externas) S1 a S%d '
              'de la lámina SE-E-01: un círculo de %.2f m de radio con una línea de %.2f m de ancho, de %s color amarillo, y la '
              'letra S con su número en el centro. Cada círculo tiene %.2f m de perímetro y %.2f m² de pintura.' % (
                  pt['total'], z['radio'], z['ancho'], z['pintura'], z['perimetro'], z['area']))]
    mat = l('Pintura de tránsito a base de resina acrílica o alquídica, color amarillo, de secado rápido.', 'Diluyente recomendado por el fabricante.',
            'Cinta de enmascarar de 1" y plantillas para la letra y el número.')
    equ = l('Compás de trazo (cordel y estaca al centro), tiza, wincha, rodillo, brochas, escobillas y soplador o escoba.')
    proc = l('Ubicar el centro de cada zona según la lámina SE-E-01 y marcarlo con la Supervisión.',
             'Limpiar el piso: sin polvo, grasa ni humedad; el concreto debe tener al menos 28 días.',
             'Trazar el círculo exterior (r = %.2f m) y el interior (r = %.2f m) con cordel desde el centro; enmascarar los bordes.' % (z['radio'], z['radio'] - z['ancho']),
             'Aplicar dos manos de pintura, la segunda después del secado de la primera; pintar la letra S y el número.',
             'Retirar la cinta y proteger del tránsito hasta el secado total.')
    ctrl = l('Radio de %.2f m (± 2 cm) y ancho de línea de %.2f m (± 0.5 cm); bordes nítidos y color uniforme.' % (z['radio'], z['ancho']),
             'Pintura sin desprendimientos ni zonas sin cubrir.')
    seg = l(EPP, 'Señalizar el área de trabajo; respirador para vapores orgánicos al aplicar la pintura; materiales lejos de fuentes de calor.')
    med = [p('Se contará el número de zonas de reunión pintadas (círculos completos con su letra y número), según la lámina SE-E-01 y la '
             'hoja ZONAS DE REUNIÓN del metrado.')]
    return ficha(desc, mat, equ, proc, ctrl, seg, med, pt['total'])


def extintor(pt):
    pqs = 'PQS' in pt['desc']
    lugares = ', '.join(c for c, n in pt['por'].items() if n)
    desc = [p('Comprende el suministro e instalación del %s, nuevo, con certificación de calidad, en las edificaciones %s, junto a '
              'su señal de ubicación. %s' % (minus(pt['desc']),
                                              lugares, pt['uso']))]
    mat = l(('Extintor portátil de polvo químico seco multipropósito (fosfato monoamónico al 75 % como mínimo), 6 kg, clasificación '
             'ABC, cilindro de acero pintado de rojo, válvula de bronce o aluminio con manómetro, manguera, pasador de seguridad y precinto.')
            if pqs else
            ('Extintor portátil de dióxido de carbono de 10 lb, clasificación BC, cilindro de acero sin costura, válvula de descarga, '
             'manguera con difusor (corneta), pasador de seguridad y precinto.'),
            'Soporte metálico de pared con tarugos y pernos; tarjeta de control de inspección y recarga.',
            'Selección, distribución, inspección, mantenimiento y recarga según la NTP 350.043-1 (versión vigente).')
    equ = l('Taladro percutor, nivel, wincha y destornillador.')
    proc = l('Ubicar el extintor en el lugar de su señal en la lámina SE-S-01, en un sitio visible, de libre acceso y cerca de la salida.',
             'Fijar el soporte de pared de modo que la parte superior del extintor quede a no más de 1.50 m del piso y su base a no '
             'menos de 0.10 m.', 'Colgar el extintor con la etiqueta de instrucciones hacia afuera y colocar la tarjeta de control.',
             'Instalar la señal de ubicación de extintor encima del equipo (partida de señales de equipos contra incendio).')
    ctrl = l('Verificar el certificado del fabricante y la fecha de carga; manómetro en la zona verde (PQS) o peso del agente (CO2).',
             'Precinto y pasador de seguridad intactos; soporte firme.', 'Altura de colgado según la NTP 350.043-1.')
    med = [p('Se contará el número de extintores suministrados e instalados a satisfacción de la Supervisión, uno por cada señal de '
             'ubicación de extintor de la planta de la lámina SE-S-01.')]
    return ficha(desc, mat, equ, proc, ctrl, l(EPP, 'Manipular el extintor con el pasador puesto; no golpear el cilindro.'), med, pt['total'])


def luces(pt):
    desc = [p('Comprende el suministro e instalación de las unidades de luces de emergencia autónomas en salidas, circulaciones y '
              'ambientes, a %s del piso, según la planta de la lámina SE-S-01. Se encienden automáticamente al cortarse la energía y '
              'dan iluminación a las rutas de evacuación durante al menos 90 minutos (Norma A.130).' % pt['altura'])]
    mat = l('Unidad de luces de emergencia de dos faros LED orientables, batería recargable libre de mantenimiento, autonomía mínima '
            'de 90 minutos, alimentación 220 V - 60 Hz, cargador automático, indicador de carga y botón de prueba, con certificación.',
            'Soporte, tarugos y tornillos; tomacorriente o conexión al circuito de alumbrado según el proyecto de instalaciones eléctricas.')
    equ = l('Taladro percutor, destornilladores, alicates, multímetro, nivel y escalera de tijera.')
    proc = l('Ubicar cada unidad según la lámina SE-S-01.', 'Fijar el soporte a %s del piso y montar el equipo nivelado.' % pt['altura'],
             'Conectar el equipo al circuito previsto en el proyecto de instalaciones eléctricas.',
             'Cargar la batería 24 horas antes de la prueba de funcionamiento.')
    ctrl = l('Prueba de corte de energía: encendido automático y autonomía de 90 minutos.', 'Faros orientados hacia la ruta y la salida.')
    med = [p('Se contará el número de unidades suministradas, instaladas y probadas, según la planta de la lámina SE-S-01.')]
    seg = l(EPP, 'Usar escalera de tijera en buen estado o andamio estable para trabajar sobre 1.80 m.',
            'Trabajos eléctricos sin tensión, con bloqueo y etiquetado del circuito, por personal calificado.')
    return ficha(desc, mat, equ, proc, ctrl, seg, med, pt['total'])


def detector(pt):
    desc = [p('Comprende el suministro e instalación de los detectores de humo en el techo de los ambientes, según la planta de la '
              'lámina SE-S-01, para detectar el humo en su etapa inicial y activar la alarma del centro. Su cableado a la central de '
              'alarma corresponde a las instalaciones eléctricas del proyecto.')]
    mat = l('Detector de humo fotoeléctrico con base de montaje, LED indicador y certificación (UL o equivalente), compatible con la '
            'central de alarma del proyecto.', 'Tarugos, tornillos y caja octogonal donde lo indique el proyecto eléctrico.')
    equ = l('Taladro percutor, destornilladores, escalera de tijera, aerosol de prueba de humo.')
    proc = l('Ubicar cada detector según la lámina SE-S-01, en el techo, a no menos de 0.10 m de muros y lejos de las salidas de aire.',
             'Fijar la base, conectar y montar el detector.', 'Probar cada detector con aerosol de prueba y verificar la señal en la central.')
    ctrl = l('Respuesta de cada detector en la prueba de humo; LED de funcionamiento activo.')
    med = [p('Se contará el número de detectores suministrados, instalados y probados, según la planta de la lámina SE-S-01.')]
    return ficha(desc, mat, equ, proc, ctrl, SEG_ALTURA, med, pt['total'])


def generalidades(P, pts):
    filas = [['01.' + x['item'], x['desc'], x['und'], str(x['total'])] for x in pts if x['und']]
    return [
        ['GENERALIDADES', [
            p('Las presentes especificaciones técnicas definen la calidad de los materiales, el procedimiento de instalación, los '
              'controles, la seguridad, la unidad de medida, el método de medición y la forma de pago de cada partida de evacuación y '
              'señalización del proyecto “%s”, con CUI N.° %s.' % (D.PROYECTO, D.CUI)),
            p('Comprenden las señales de evacuación y emergencia, de equipos contra incendio, de advertencia, de prohibición e '
              'informativas, las zonas de reunión pintadas en el piso, los extintores portátiles, las unidades de luces de emergencia '
              'y los detectores de humo, según las láminas SE-S-01 (plano de señalización) y SE-E-01 (plano de evacuación).'),
            p('La numeración, la descripción, la unidad y la cantidad de cada partida son las del metrado de evacuación y señalización '
              '(hoja RESUMEN, ítem 01). La memoria descriptiva, las láminas y el metrado forman parte de este documento.')]],
        ['UBICACIÓN', [p('Entidad: Gerencia Territorial Bajo Mayo - Dirección de Infraestructura. Ubicación: %s.' % D.UBICACION),
                       p('Clima cálido y lluvioso: las señales exteriores serán resistentes a la humedad y a los rayos ultravioleta.')]],
        ['NORMAS APLICABLES', [
            p('En todo lo no previsto en estas especificaciones rigen, en su versión vigente:'),
            l('Reglamento Nacional de Edificaciones: Normas A.010, A.120 Accesibilidad Universal en Edificaciones, A.130 Requisitos de '
              'Seguridad, EM.010 Instalaciones Eléctricas Interiores y G.050 Seguridad durante la Construcción.',
              'NTP 399.010-1 Señales de seguridad. Colores, símbolos, formas y dimensiones de señales de seguridad. Parte 1: Reglas para '
              'el diseño de las señales de seguridad y franjas de seguridad.',
              'NTP 350.043-1 Extintores portátiles. Selección, distribución, inspección, mantenimiento, recarga y prueba hidrostática.',
              'D.S. N.° 002-2018-PCM, Reglamento de Inspecciones Técnicas de Seguridad en Edificaciones; D.S. N.° 011-2019-TR.',
              'NFPA 10, NFPA 72 y NFPA 101 como referencia.'),
            p('Si hubiera discrepancia entre documentos, prevalecen en este orden: láminas, especificaciones técnicas, memoria '
              'descriptiva y metrado; las discrepancias se anotarán en el cuaderno de obra y las resolverá la Supervisión.')]],
        ['MATERIALES Y CONDICIONES GENERALES', [
            p('Todos los materiales y equipos serán nuevos, de primera calidad y con certificado del fabricante. La Supervisión '
              'aprobará una muestra de cada tipo de señal antes de su fabricación en serie.'),
            l('Señales de evacuación, de emergencia y de equipos contra incendio: fotoluminiscentes, para verse sin energía eléctrica.',
              'Todas las señales llevan el texto en braille en una placa de acrílico (Norma A.120).',
              'Alturas de instalación (borde inferior de la señal sobre el piso terminado): las de la tabla de partidas; la señal de '
              'extintor va encima del equipo, a 1.80 m.',
              'Las señales se instalan sobre superficies terminadas y no deben quedar tapadas por puertas abiertas, muebles ni equipos.')]],
        ['PARTIDAS Y CANTIDADES', [p('Partidas del metrado de evacuación y señalización:'), t(['ITEM', 'DESCRIPCIÓN', 'UND', 'CANT.'], filas, [13, 67, 9, 11])]],
        ['RECEPCIÓN Y MANTENIMIENTO', [
            l('La Supervisión recibirá las partidas con la verificación de cantidad, ubicación, altura, fijación y funcionamiento '
              '(luces de emergencia, detectores y extintores).',
              'El contratista entregará los certificados de los equipos, las tarjetas de control de los extintores y las '
              'instrucciones de mantenimiento del fabricante.')]],
    ]


def construir():
    P = D.plano(); pts = D.partidas(P)
    partidas = []
    for x in [dict(item='', desc='SEÑALIZACIÓN, EVACUACIÓN Y SEGURIDAD', und=None)] + pts:
        cod = '01' + ('.' + x['item'] if x['item'] else '')
        it = dict(codigo=cod, desc=x['desc'], und=x['und'] or '', nivel=len(cod.split('.')) - 1)
        if x['und']:
            d = x['desc']
            if d.startswith('ZONA DE REUNI'): it['secciones'] = zona_reunion(x)
            elif d.startswith('EXTINTOR'): it['secciones'] = extintor(x)
            elif d.startswith('UNIDAD DE LUCES'): it['secciones'] = luces(x)
            elif d.startswith('DETECTOR'): it['secciones'] = detector(x)
            else: it['secciones'] = senal(x)
        partidas.append(it)
    from PIL import Image
    img = V.foto(); w, h = Image.open(img).size
    doc = dict(proyecto=D.PROYECTO, cui=D.CUI, corto=D.CORTO, entidad='GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO',
               especialidad=D.ESPECIALIDAD, ubicacion='SAN MARTÍN - SAN MARTÍN - MORALES', fecha=D.FECHA,
               cabecera='ESPECIFICACIONES TÉCNICAS - EVACUACIÓN Y SEÑALIZACIÓN', titulo_doc='Especificaciones técnicas - Evacuación y señalización',
               caratula=dict(entidad='GOBIERNO REGIONAL SAN MARTÍN', gerencia='GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO',
                             expediente='EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:', proyecto='“%s”' % D.PROYECTO,
                             ci='CUI N.° %s' % D.CUI, foto=img, proporcion=h / w, leyenda=V.LEYENDA,
                             titulo='ESPECIFICACIONES TÉCNICAS', subtitulo='EVACUACIÓN Y SEÑALIZACIÓN',
                             especialidad='ESPECIALIDAD: ' + D.ESPECIALIDAD, ubicacion=D.UBICACION, fecha=D.FECHA),
               generalidades=generalidades(P, pts), partidas=partidas)
    os.makedirs(os.path.dirname(JSON), exist_ok=True)
    json.dump(doc, open(JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    subprocess.run(['node', os.path.join(ESP, 'docx_espec.js'), JSON, SALIDA], check=True, cwd=ESP)
    return SALIDA


if __name__ == '__main__':
    print(construir())
