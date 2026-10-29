# -*- coding: utf-8 -*-
"""Especificaciones técnicas de evacuación y señalización - Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514).

Motor y formato de las especificaciones del expediente (JSON -> herramientas/especificaciones/docx_espec.js): carátula con la
foto del hogar, índice, generalidades y una ficha por partida (descripción con la imagen de la señal, materiales, equipos y
herramientas, procedimiento, control de calidad, seguridad, unidad, método de medición y forma de pago). Partidas, numeración,
unidades y cantidades = las del metrado (metrado_sr.py / datos_sr.py), en el mismo orden. Mismo contenido técnico que las
especificaciones de señalización del CAR Varones, con lo propio del hogar (lámina SE-S-02, extintor de 9 kg, dirección de
evacuación, señales de SS.HH. de 0.20 x 0.30 m).

Uso: python3 herramientas/senalizacion_refugio/espec_sr.py
Salida: entregables/ESPECIFICACIONES_TECNICAS_EVACUACION_Y_SENALIZACION_HOGAR_REFUGIO.docx
"""
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI)
for d in (AQUI, HER):
    sys.path.insert(0, d)
import datos_sr as D  # noqa: E402
import senales_sr as SR  # noqa: E402
import caratulas_refugio as CR  # noqa: E402  (foto y leyenda del Hogar de Refugio)

V = CR.V
ESP = os.path.join(HER, 'especificaciones')
JSON = os.path.join(ESP, '_json', 'refugio_senalizacion.json')
SALIDA = os.path.join(D.SAL, 'ESPECIFICACIONES_TECNICAS_EVACUACION_Y_SENALIZACION_HOGAR_REFUGIO.docx')
LS = D.LS


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
              'para ejecutar la partida según esta especificación y la lámina %s. Cantidad del metrado: %d und.' % (LS, cant))]


def ficha(desc, mat, equ, proc, ctrl, seg, medicion, cant):
    desc, mat, equ, proc, ctrl, seg, medicion = ([x] if isinstance(x[0], str) else x for x in (desc, mat, equ, proc, ctrl, seg, medicion))
    return [['DESCRIPCIÓN', desc], ['MATERIALES', mat], ['EQUIPOS Y HERRAMIENTAS', equ], ['PROCEDIMIENTO DE EJECUCIÓN', proc],
            ['CONTROL DE CALIDAD Y TOLERANCIAS', ctrl], ['SEGURIDAD Y SALUD EN EL TRABAJO', seg],
            ['UNIDAD DE MEDIDA', [p('La unidad de medida es la unidad (und).')]], ['MÉTODO DE MEDICIÓN', medicion],
            ['FORMA DE PAGO', pago(cant)]]


def minus(desc):
    s = desc.lower()
    for a, b in (('pqs', 'PQS'), (' abc', ' ABC'), ('9 kg', '9 kg')):
        s = s.replace(a, b)
    return s


def lugares(pt):
    return ', '.join(('%s (%d)' % (c, n)) for c, n in pt['por'].items() if n)


def ubicacion_txt(pt):
    if pt['sin_ubicar']:
        return ('según la lámina %s, en los tableros y ambientes eléctricos que indica, en coordinación con el plano de '
                'instalaciones eléctricas' % LS)
    return 'según la planta de la lámina %s (%s)' % (LS, lugares(pt))


def senal(pt):
    foto = 'fotoluminiscente' in pt['material']
    braille = 'braille' in pt['material']
    desc = [p('Comprende el suministro e instalación de la %s, de %s, con el pictograma, los colores y la forma de la NTP 399.010-1%s. '
              '%s Se instala %s, a %s del piso terminado (borde inferior de la señal), %s.' % (
                  minus(pt['desc']), pt['dim'], ' y el texto en braille (Norma A.120)' if braille else '', pt['uso'],
                  ubicacion_txt(pt), pt['altura'],
                  'visible desde la ruta de evacuación y sin obstáculos delante' if foto else 'en un lugar visible'))]
    mat = [pt['material'] + '.',
           'Vinil %s de alta calidad, resistente a la humedad y a los rayos ultravioleta; colores de seguridad según la NTP 399.010-1.' % (
               'fotoluminiscente con luminancia que permita leer la señal en la oscuridad después de un corte de energía' if foto else 'adhesivo impreso')]
    if braille:
        mat.append('Placa de acrílico de 2 mm con la leyenda de la señal en braille grado 1 en relieve, pegada en la parte inferior de la señal.')
    if pt['desc'].startswith('LETRERO DE AFORO'):
        mat.append('El número de personas de cada letrero es el aforo de su ambiente según el cálculo de aforo de arquitectura; '
                   'el contratista lo confirmará con la Supervisión antes de la impresión.')
    mat.append('Fijación: tarugos de PVC de 1/4" y tornillos autorroscantes de acero inoxidable en muros de albañilería o concreto; en '
               'superficies de vidrio, drywall o metal, cinta doble contacto de alta adherencia o pegamento de contacto.')
    equ = l('Taladro percutor con broca para concreto de 1/4", destornillador, nivel de mano, wincha, lápiz y escalera de tijera.')
    proc = l('Verificar en la lámina %s la ubicación de cada señal y marcarla en obra con la Supervisión.' % LS,
             'Limpiar y secar la superficie de apoyo; debe estar terminada (tarrajeada y pintada).',
             'Presentar la señal con el nivel a la altura indicada (%s al borde inferior) y marcar las perforaciones.' % pt['altura'],
             'Perforar, colocar los tarugos y fijar la señal con los tornillos sin deformar la lámina%s.' % (
                 '; colocar la placa de braille' if braille else ''),
             'Retirar la película protectora y limpiar la superficie de la señal.')
    ctrl = l('Señales sin fisuras, burbujas ni decoloraciones, con colores, pictograma y dimensiones según la NTP 399.010-1.',
             'Tolerancia de altura: ± 2 cm; señal nivelada y firme.',
             ('Lectura de la placa de braille completa y legible.' if braille else 'Flecha orientada en el sentido de la evacuación.')
             + (' Comprobar con la luz apagada que la señal se vea.' if foto else ''))
    med = [p('Se contará el número de señales suministradas e instaladas a satisfacción de la Supervisión, %s.' % (
        'según la leyenda de la lámina %s y su ubicación en obra' % LS if pt['sin_ubicar'] else 'según la planta de la lámina %s y la hoja METRADO' % LS))]
    return ficha(desc, l(*mat), equ, proc, ctrl, SEG_ALTURA, med, pt['total'])


def extintor(pt):
    desc = [p('Comprende el suministro e instalación del %s, nuevo, con certificación de calidad, en las edificaciones %s, junto a su '
              'señal de ubicación. %s' % (minus(pt['desc']), lugares(pt), pt['uso']))]
    mat = l('Extintor portátil de polvo químico seco multipropósito (fosfato monoamónico al 75 % como mínimo), 9 kg, clasificación '
            'ABC, cilindro de acero pintado de rojo, válvula de bronce o aluminio con manómetro, manguera, pasador de seguridad y precinto.',
            'Soporte metálico de pared con tarugos y pernos; tarjeta de control de inspección y recarga.',
            'Selección, distribución, inspección, mantenimiento y recarga según la NTP 350.043-1 (versión vigente).')
    equ = l('Taladro percutor, nivel, wincha y destornillador.')
    proc = l('Ubicar el extintor en el lugar de su señal en la lámina %s, en un sitio visible, de libre acceso y cerca de la salida.' % LS,
             'Fijar el soporte de pared de modo que la parte superior del extintor quede a no más de 1.50 m del piso y su base a no '
             'menos de 0.10 m.', 'Colgar el extintor con la etiqueta de instrucciones hacia afuera y colocar la tarjeta de control.',
             'Instalar la señal de ubicación de extintor encima del equipo (partida 01.02.01).')
    ctrl = l('Verificar el certificado del fabricante y la fecha de carga; manómetro en la zona verde.',
             'Precinto y pasador de seguridad intactos; soporte firme.', 'Altura de colgado según la NTP 350.043-1.')
    med = [p('Se contará el número de extintores suministrados e instalados a satisfacción de la Supervisión, uno por cada señal de '
             'ubicación de extintor de la planta de la lámina %s.' % LS)]
    return ficha(desc, mat, equ, proc, ctrl, l(EPP, 'Manipular el extintor con el pasador puesto; no golpear el cilindro.'), med, pt['total'])


def luces(pt):
    desc = [p('Comprende el suministro e instalación de las unidades de luces de emergencia autónomas en salidas, circulaciones, '
              'habitaciones y ambientes, a %s del piso, según la planta de la lámina %s (%s). Se encienden automáticamente al cortarse '
              'la energía y dan iluminación a las rutas de evacuación durante al menos 90 minutos (Norma A.130).' % (pt['altura'], LS, lugares(pt)))]
    mat = l('Unidad de luces de emergencia de dos faros LED orientables, batería recargable libre de mantenimiento, autonomía mínima '
            'de 90 minutos, alimentación 220 V - 60 Hz, cargador automático, indicador de carga y botón de prueba, con certificación.',
            'Soporte, tarugos y tornillos; tomacorriente o conexión al circuito de alumbrado según el proyecto de instalaciones eléctricas.')
    equ = l('Taladro percutor, destornilladores, alicates, multímetro, nivel y escalera de tijera.')
    proc = l('Ubicar cada unidad según la lámina %s.' % LS, 'Fijar el soporte a %s del piso y montar el equipo nivelado.' % pt['altura'],
             'Conectar el equipo al circuito previsto en el proyecto de instalaciones eléctricas.',
             'Cargar la batería 24 horas antes de la prueba de funcionamiento.')
    ctrl = l('Prueba de corte de energía: encendido automático y autonomía de 90 minutos.', 'Faros orientados hacia la ruta y la salida.')
    med = [p('Se contará el número de unidades suministradas, instaladas y probadas, según la planta de la lámina %s.' % LS)]
    seg = l(EPP, 'Usar escalera de tijera en buen estado o andamio estable para trabajar sobre 1.80 m.',
            'Trabajos eléctricos sin tensión, con bloqueo y etiquetado del circuito, por personal calificado.')
    return ficha(desc, mat, equ, proc, ctrl, seg, med, pt['total'])


def detector(pt):
    desc = [p('Comprende el suministro e instalación de los detectores de humo en el techo de los ambientes, según la planta de la '
              'lámina %s (%s), para detectar el humo en su etapa inicial y dar aviso sonoro. Su alimentación y, de ser el caso, su '
              'conexión a un panel de alarma corresponden a las instalaciones eléctricas del proyecto.' % (LS, lugares(pt)))]
    mat = l('Detector de humo fotoeléctrico con base de montaje, alarma sonora incorporada, LED indicador y certificación (UL o '
            'equivalente); compatible con el sistema de alarma del proyecto de instalaciones eléctricas, si lo hubiera.',
            'Tarugos, tornillos y caja octogonal donde lo indique el proyecto eléctrico.')
    equ = l('Taladro percutor, destornilladores, escalera de tijera, aerosol de prueba de humo.')
    proc = l('Ubicar cada detector según la lámina %s, en el techo, a no menos de 0.10 m de muros y lejos de las salidas de aire.' % LS,
             'Fijar la base, conectar y montar el detector.', 'Probar cada detector con aerosol de prueba y verificar su alarma.')
    ctrl = l('Respuesta de cada detector en la prueba de humo; LED de funcionamiento activo.')
    med = [p('Se contará el número de detectores suministrados, instalados y probados, según la planta de la lámina %s.' % LS)]
    return ficha(desc, mat, equ, proc, ctrl, SEG_ALTURA, med, pt['total'])


def zona(pt):
    """Pintura de las zonas de evacuación en caso de emergencia (lámina SE-E-01), medida en m²."""
    re_, ri_ = D.radios(); a = D.area_zona(); n = pt['n_zonas']; le = D.LAMINA_E[0]
    desc = [p('Comprende el trazo y el pintado en el piso de concreto de las %d zonas de evacuación en caso de emergencia de la lámina '
              '%s: un anillo de %.2f m de diámetro exterior y %.2f m de ancho de línea, de pintura de tránsito color amarillo, con el '
              'número de la zona y su aforo. Cada anillo tiene %.4f m² de pintura (π x (%.2f² - %.2f²)); en total, %.2f m². %s' % (
                  n, le, 2 * re_, re_ - ri_, a, re_, ri_, pt['total'], pt['uso']))]
    mat = l('Pintura de tránsito a base de resina acrílica o alquídica, color amarillo, de secado rápido, resistente a la abrasión y a '
            'los rayos ultravioleta.', 'Diluyente recomendado por el fabricante.', 'Cinta de enmascarar de 1" y plantillas para los números.')
    equ = l('Cordel y estaca para el trazo desde el centro, tiza, wincha, rodillo, brochas, escobillas y soplador o escoba.')
    proc = l('Ubicar el centro de cada zona según la lámina %s y marcarlo con la Supervisión.' % le,
             'Limpiar el piso: sin polvo, grasa ni humedad; el concreto debe tener al menos 28 días.',
             'Trazar el círculo exterior (r = %.2f m) y el interior (r = %.2f m) con cordel desde el centro y enmascarar los bordes.' % (re_, ri_),
             'Aplicar dos manos de pintura, la segunda después del secado de la primera; pintar el número de la zona y su aforo.',
             'Retirar la cinta y proteger del tránsito hasta el secado total.')
    ctrl = l('Radio exterior de %.2f m (± 2 cm) y ancho de línea de %.2f m (± 0.5 cm); bordes nítidos y color uniforme.' % (re_, re_ - ri_),
             'Pintura sin desprendimientos ni zonas sin cubrir; números legibles.')
    seg = l(EPP, 'Señalizar el área de trabajo; respirador para vapores orgánicos al aplicar la pintura; materiales lejos de fuentes de calor.')
    return [['DESCRIPCIÓN', desc], ['MATERIALES', [mat]], ['EQUIPOS Y HERRAMIENTAS', [equ]], ['PROCEDIMIENTO DE EJECUCIÓN', [proc]],
            ['CONTROL DE CALIDAD Y TOLERANCIAS', [ctrl]], ['SEGURIDAD Y SALUD EN EL TRABAJO', [seg]],
            ['UNIDAD DE MEDIDA', [p('La unidad de medida es el metro cuadrado (m²) de anillo pintado.')]],
            ['MÉTODO DE MEDICIÓN', [p('Se medirá el área de los anillos pintados y recibidos a satisfacción de la Supervisión: número de '
                                      'zonas por el área de cada anillo, según la lámina %s y la hoja ZONAS DE EVACUACIÓN del metrado.' % le)]],
            ['FORMA DE PAGO', [p('El pago se efectuará al precio unitario del presupuesto por metro cuadrado (m²), de acuerdo con el avance '
                                 'valorizado y con la conformidad de la Supervisión. Dicho precio constituye compensación total por la mano '
                                 'de obra, los materiales, el equipo, las herramientas y todo imprevisto necesario. Cantidad del metrado: '
                                 '%.2f m².' % pt['total'])]]]


def generalidades(pts):
    filas = [['01.' + x['item'], x['desc'], x['und'], str(x['total'])] for x in pts if x['und']]
    return [
        ['GENERALIDADES', [
            p('Las presentes especificaciones técnicas definen la calidad de los materiales, el procedimiento de instalación, los '
              'controles, la seguridad, la unidad de medida, el método de medición y la forma de pago de cada partida de evacuación '
              'y señalización del proyecto “%s”, con CUI N.° %s.' % (D.PROYECTO, D.CUI)),
            p('Comprenden las señales de evacuación y emergencia, de equipos contra incendio, de advertencia e informativas, los '
              'extintores portátiles, las unidades de luces de emergencia, los detectores de humo y las zonas de evacuación pintadas '
              'en el piso de las nueve edificaciones y de los exteriores, según las láminas %s (%s) y %s (%s).' % (
                  LS, D.LAMINA_S[1].lower(), D.LAMINA_E[0], D.LAMINA_E[1].lower())),
            p('La numeración, la descripción, la unidad y la cantidad de cada partida son las del metrado de señalización y '
              'seguridad (hoja RESUMEN, ítem 01). La memoria descriptiva, las láminas y el metrado forman parte de este documento.')]],
        ['UBICACIÓN', [p('Entidad: Gobierno Regional San Martín - Gerencia Territorial Bajo Mayo - Tarapoto. Ubicación: %s.' % D.UBICACION),
                       p('Clima cálido y lluvioso: las señales exteriores serán resistentes a la humedad y a los rayos ultravioleta.')]],
        ['NORMAS APLICABLES', [
            p('En todo lo no previsto en estas especificaciones rigen, en su versión vigente:'),
            l('Reglamento Nacional de Edificaciones: Normas A.010, A.090 Servicios Comunales, A.120 Accesibilidad Universal en '
              'Edificaciones, A.130 Requisitos de Seguridad, EM.010 Instalaciones Eléctricas Interiores y G.050 Seguridad durante la '
              'Construcción.',
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
              'Las señales indicadas "con braille" llevan su texto en braille en una placa de acrílico (Norma A.120).',
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
    pts = D.partidas()
    img = SR.generar()
    partidas = []
    for x in [dict(item='', desc='EVACUACIÓN Y SEÑALIZACIÓN', und=None)] + pts:
        cod = '01' + ('.' + x['item'] if x['item'] else '')
        it = dict(codigo=cod, desc=x['desc'], und=x['und'] or '', nivel=len(cod.split('.')) - 1)
        if x['und']:
            d = x['desc']
            if d.startswith('EXTINTOR'): it['secciones'] = extintor(x)
            elif d.startswith('UNIDAD DE LUCES'): it['secciones'] = luces(x)
            elif d.startswith('DETECTOR'): it['secciones'] = detector(x)
            elif x.get('bloques') == 'ZONAS': it['secciones'] = zona(x)
            else: it['secciones'] = senal(x)
            ruta = img[x['item']]
            from PIL import Image
            w, h = Image.open(ruta).size; alto = 170 if h >= w else 120
            it['secciones'][0][1].insert(0, ['i', ruta, int(alto * w / h), alto])
        partidas.append(it)
    from PIL import Image
    foto = V.foto(); w, h = Image.open(foto).size
    doc = dict(proyecto=D.PROYECTO, cui=D.CUI, corto=D.CORTO, entidad=D.ENTIDAD,
               especialidad=D.ESPECIALIDAD, ubicacion='SAN MARTÍN - SAN MARTÍN - MORALES', fecha=D.FECHA,
               cabecera='ESPECIFICACIONES TÉCNICAS - EVACUACIÓN Y SEÑALIZACIÓN', titulo_doc='Especificaciones técnicas - Evacuación y señalización',
               caratula=dict(entidad='GOBIERNO REGIONAL SAN MARTÍN', gerencia=D.ENTIDAD,
                             expediente='EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:', proyecto='“%s”' % D.PROYECTO,
                             ci='CUI N.° %s' % D.CUI, foto=foto, proporcion=h / w, leyenda=V.LEYENDA,
                             titulo='ESPECIFICACIONES TÉCNICAS', subtitulo='EVACUACIÓN Y SEÑALIZACIÓN',
                             especialidad='ESPECIALIDAD: ' + D.ESPECIALIDAD, ubicacion=D.UBICACION, fecha=D.FECHA),
               generalidades=generalidades(pts), partidas=partidas)
    os.makedirs(os.path.dirname(JSON), exist_ok=True)
    json.dump(doc, open(JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    subprocess.run(['node', os.path.join(ESP, 'docx_espec.js'), JSON, SALIDA], check=True, cwd=ESP)
    import indice_word
    indice_word.llenar([SALIDA])                                # índice lleno para imprimir
    return SALIDA


if __name__ == '__main__':
    print(construir())
