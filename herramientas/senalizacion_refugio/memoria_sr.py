# -*- coding: utf-8 -*-
"""Memoria descriptiva de evacuación y señalización - Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514), en Word.

Estructura de la memoria de evacuación y señalización de arquitectura del hogar y de la del CAR Varones (memoria_se.py), con
los datos de este hogar: generalidades, descripción del hogar con los ambientes de cada edificación leídos del plano, componentes
del plan con los peligros por edificación, población y ocupación, medios de evacuación, organización para emergencias
(comité, director, mantenimiento, brigadas y personal), protocolos ante sismo, incendio, lluvias, fuga de gas, corte de energía
e intento de ingreso no autorizado, procedimiento de evacuación con directorio, protección contra incendio, señalización con la
clasificación de la NTP 399.010-1, la simbología con la imagen de cada señal, una ficha por señal y la distribución por
edificación con sus plantas, mantenimiento, conclusiones y láminas.

Datos: plano de señalización de la arquitecta (lee_plano_sr.py), cantidades del metrado (datos_sr.py), imágenes de las
señales (senales_sr.py) y vistas de la planta (vistas_sr.py).

Uso: python3 herramientas/senalizacion_refugio/memoria_sr.py
Salida: entregables/MEMORIA_DESCRIPTIVA_EVACUACION_Y_SENALIZACION_HOGAR_REFUGIO.docx
"""
import os
import re
import sys

from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI); RAIZ = os.path.dirname(HER)
for d in (AQUI, os.path.join(HER, 'varones', 'senalizacion'), HER):
    sys.path.insert(0, d)
import datos_sr as D  # noqa: E402
import senales_sr as SR  # noqa: E402
import memoria_descriptiva_refugio as R  # noqa: E402
import caratulas_refugio as CR  # noqa: E402  (datos y foto del Hogar de Refugio en el motor de carátulas)
import memoria_se as MS  # noqa: E402  (tablas, figuras, viñetas y encabezado de las memorias de señalización)

V = CR.V
MS.D = D                                                     # encabezado con el nombre y el CUI del hogar
tabla, figura, sub, vines, etiq = MS.tabla, MS.figura, MS.sub, MS.vines, MS.etiq
SALIDA = os.path.join(D.SAL, 'MEMORIA_DESCRIPTIVA_EVACUACION_Y_SENALIZACION_HOGAR_REFUGIO.docx')
FIG = os.path.join(D.SAL, 'figuras_senalizacion')
MAPAS = os.path.join(RAIZ, 'insumos/katiuska/senalizacion/mapas')      # mapas de ubicación del Perú, la región y la provincia
UTM = (345690, 9282804)                      # frente del predio (UTM WGS 84 18 S, referencial; memoria de evacuación de arquitectura)
NPT_FRENTE = 260.60
LS = D.LS
ROSA = 'F2E6E8'

# nombres de ambientes del plano con su escritura correcta
NOMBRE = {'TALLER DE RESPOSTERÍA': 'Taller de repostería', 'DISPENSA': 'Despensa', 'SS.HH DISCP.': 'SS.HH. discapacitados',
          'SS.HH MUJERES': 'SS.HH. mujeres', 'SS.HH VARONES': 'SS.HH. varones', 'SUB ESTACIÓN': 'Subestación',
          'ALMACEN DE DONACIONES': 'Almacén de donaciones', 'ALMACEN GENERAL Y DE LIMPIEZA': 'Almacén general y de limpieza',
          'ALMACENAMIENTO DE RESIDUOS SOLIDOS': 'Almacenamiento de residuos sólidos', 'TOPICO': 'Tópico', 'SUM/COMEDOR': 'SUM-comedor'}
FUERA = {'VEREDA', 'HALL', 'PASADIZO', 'COTA', 'CIRCULACIÓN', 'CIRCULACION'}

PELIGROS = [
    ('E-01 Administración', 'Data center, archivo, oficinas y salas de espera y de visitas', 'Incendio de origen eléctrico (clase A y C); '
     'afluencia de visitantes', 'Extintores PQS, detectores de humo, luces de emergencia, salidas y dirección de evacuación señalizadas'),
    ('E-02 Almacén de donaciones y tópico', 'Almacén con ropa, colchones y víveres donados; tópico con medicamentos', 'Incendio clase A por '
     'carga combustible almacenada', 'Extintores PQS, detectores de humo, luces de emergencia'),
    ('E-03 Mantenimiento', 'Tablero eléctrico, subestación, grupo electrógeno, maestranza, almacén de limpieza y residuos sólidos',
     'Riesgo eléctrico; incendio clase B y C (combustible del grupo electrógeno); productos químicos', 'Señales de atención riesgo eléctrico, '
     'extintores PQS, detectores de humo, acceso solo del personal'),
    ('E-04 Talleres', 'Talleres de costura, bisutería y repostería, terapia grupal, cuarto de cámaras, archivo y depósito',
     'Incendio clase A (telas, papel) y eléctrico; concentración de personas en los talleres', 'Extintores PQS, detectores de humo, '
     'luces de emergencia, letreros de aforo, salidas señalizadas'),
    ('E-05 SUM-comedor, cocina y módulos', 'Cocina con gas licuado, despensa y alacena, SUM-comedor, lavandería, módulo de enseñanza y '
     'módulo infantil', 'Incendio por gas y aceites de cocina (clase B y K); fuga de gas; mayor concentración de personas; niñas y '
     'niños pequeños', 'Extintores PQS, detectores de humo, luces de emergencia, varias salidas a las circulaciones exteriores'),
    ('E-06 a E-08 Habitaciones', 'Habitaciones simples, dobles, triples y especial con sus servicios higiénicos', 'Incendio nocturno; '
     'evacuación de mujeres dormidas con niñas y niños pequeños, gestantes o con discapacidad', 'Detectores de humo, luces de emergencia '
     'en las habitaciones, zonas seguras internas, extintores PQS, salidas directas a las circulaciones exteriores'),
    ('E-09 Vestidores y almacén deportivo', 'Vestidores con SS.HH. y almacén de implementos deportivos', 'Caídas por piso mojado; '
     'incendio clase A', 'Extintor PQS, señales de SS.HH., luces de emergencia'),
    ('Exteriores', 'Garita de control, patios cívico y de juegos, biohuerto, estacionamientos, patio de maniobras, PTAR, cisterna y '
     'tanque elevado', 'Tránsito vehicular; caídas; intento de ingreso no autorizado', 'Control de accesos en la garita, puntos '
     'ecológicos, áreas abiertas para la concentración lejos de fachadas, cables y árboles'),
]
DIRECTORIO = [('Cuerpo General de Bomberos Voluntarios del Perú', '116'), ('Policía Nacional del Perú', '105'),
              ('Sistema de Atención Médica Móvil de Urgencia (SAMU)', '106'), ('Defensa Civil (INDECI)', '115'),
              ('Línea de orientación en salud (MINSA)', '113'), ('Línea 100 - violencia contra la mujer y los integrantes del grupo familiar', '100')]


def amb_txt(a):
    return NOMBRE.get(a) or R_cap(a)


def R_cap(t):
    t = t[:1].upper() + t[1:].lower()
    for a, b in ((r'ss\.hh\.?', 'SS.HH.'), (r'\bsum\b', 'SUM'), (r'tipo 1\b', 'tipo I'), (r'tipo 2\b', 'tipo II')):
        t = re.sub(a, b, t, flags=re.I)
    return t


def ficha(M, p, img):
    """Ficha de una señal o equipo: imagen a la izquierda y sus datos a la derecha."""
    W = M.ancho
    t = M.d.add_table(rows=1, cols=2); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    an = (4.6, W - 4.6)
    for gc, w in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), an):
        gc.set(qn('w:w'), str(int(w * 567)))
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    c0, c1 = t.rows[0].cells
    c0.width, c1.width = Cm(an[0]), Cm(an[1])
    c0.vertical_alignment = c1.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    q = c0.paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    from PIL import Image
    w, h = Image.open(img).size
    q.add_run().add_picture(img, width=Cm(min(4.0, 5.2 * w / h)))
    q = c1.paragraphs[0]; q.paragraph_format.space_after = Pt(2)
    M.run(q, '01.%s  %s' % (p['item'], p['desc']), 9.5, True, color=R.GRANATE)
    lugares = ', '.join('%s (%d)' % (c, n) for c, n in p['por'].items() if n) or \
        'según la lámina %s, en los tableros y ambientes eléctricos' % LS
    for et, v in (('Función', p['uso']), ('Dimensiones', p['dim']), ('Material', p['material']), ('Altura de instalación', p['altura']),
                  ('Cantidad', '%d und' % p['total']), ('Ubicación', lugares)):
        r = c1.add_paragraph(); r.paragraph_format.space_after = Pt(1)
        M.run(r, et + ': ', 9, True); M.run(r, v, 9)
    sp = M.d.add_paragraph(); sp.paragraph_format.space_after = Pt(4)


def generar():
    P = D.plano(); pts = D.partidas(P); Pb = D.POBLACION
    err = D.comprobacion(P)
    if err:
        raise ValueError('; '.join(err))
    por = {p['clave']: p for p in pts if p['und'] and not p['desc'].startswith('EXTINTOR DE')}
    q = {k: v['total'] for k, v in por.items()}
    ext = next(p for p in pts if p['desc'].startswith('EXTINTOR DE'))
    eds = D.edificaciones(P)
    img = SR.generar()

    M = R.Memoria()
    s0 = M.d.sections[0]; s0.left_margin = s0.right_margin = Cm(2.0); s0.top_margin = Cm(2.3); s0.bottom_margin = Cm(1.2)
    V.C.SERVICIO = 'EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:'
    V.COLOR, V.COLOR_SUB = '7B1E2B', 'F2D7DB'                    # especialidad de arquitectura: guinda
    V.FECHA = 'OCTUBRE - 2026'                                   # la del plano de señalización (y de las especificaciones)
    foto = V.foto(); V.escudo()
    V.caratula(M.d, foto, 'MEMORIA DESCRIPTIVA', D.ESPECIALIDAD)
    MS.encabezado(M, 'MEMORIA DESCRIPTIVA - EVACUACIÓN Y SEÑALIZACIÓN')
    R.indice(M)
    W = M.ancho

    # ================================================================== 1 GENERALIDADES
    M.t1('GENERALIDADES')
    M.t2('Introducción')
    M.par('La presente memoria descriptiva corresponde a la especialidad de arquitectura, en su componente de señalización y '
          'seguridad, del expediente técnico a nivel de ejecución de obra del proyecto “%s”, con CUI N.° %s.' % (D.PROYECTO, D.CUI))
    M.par('Describe la población y la ocupación del hogar, los medios de evacuación, la organización para responder ante emergencias, '
          'los protocolos de actuación, los equipos de protección contra incendio y la señalización de seguridad de cada edificación, '
          'de acuerdo con la lámina %s (%s) y con la lámina %s (%s) del grupo de evacuación y señalización del índice de planos de '
          'arquitectura.' % (LS, D.LAMINA_S[1].lower(), D.LAMINA_E[0], D.LAMINA_E[1].lower()))
    M.par('El planteamiento se rige por la seguridad integral de las personas que viven y trabajan en el hogar, la accesibilidad '
          'universal y la condición de sus residentes: mujeres víctimas de violencia, en muchos casos con sus hijas e hijos, que '
          'residen en el local de manera temporal y cuya ubicación e identidad deben mantenerse en reserva.')
    M.t2('Antecedentes y justificación técnica')
    M.par('El Hogar de Refugio Temporal es un servicio de protección que brinda alojamiento, alimentación, atención psicológica, '
          'social y legal y actividades de recuperación a mujeres víctimas de violencia en situación de riesgo de feminicidio o cuya '
          'integridad o salud física o mental esté en peligro, y a sus hijas e hijos. La provincia de San Martín no cuenta con un hogar '
          'de refugio donde acoger a estas mujeres.')
    M.par('En respuesta a esta necesidad, el Gobierno Regional San Martín, mediante la Gerencia Territorial Bajo Mayo - Tarapoto, ha '
          'impulsado el presente expediente técnico. Por funcionar las 24 horas, con residentes y niñas y niños que duermen en el '
          'local, la seguridad ante sismos e incendios, la evacuación ordenada y el control de los accesos son condiciones de diseño '
          'y no solo de funcionamiento.')
    M.t2('Nombre del proyecto y CUI')
    M.par('“%s”.' % D.PROYECTO, neg=True)
    M.par('Código único de inversiones (CUI): N.° %s.' % D.CUI)
    M.t2('Ubicación')
    M.par('El hogar se ubica en el predio rural Los Mangos, frente a la carretera Oasis, en el distrito de Morales, junto al CAR '
          'Varones (CUI 2705619) y al CAR Mujeres (CUI 2717013):')
    tabla(M, 'Ubicación política y geográfica', ['COMPONENTE', 'UBICACIÓN / DENOMINACIÓN'], [
        ['Departamento / región', 'San Martín'], ['Provincia', 'San Martín'], ['Distrito', 'Morales'],
        ['Sector', 'Predio rural Los Mangos, frente a la carretera Oasis'],
        ['Coordenadas UTM (WGS 84, zona 18 S)', 'E %s, N %s (referenciales, frente del predio)' % (
            format(UTM[0], ',').replace(',', ' '), format(UTM[1], ',').replace(',', ' '))],
        ['Altitud', '%.2f m s. n. m. (piso terminado del frente del predio)' % NPT_FRENTE]], [6.0, W - 6.0], izq=(0, 1))
    mapas = [(os.path.join(MAPAS, 'MAPA_PERU.jpg'), 'Perú'), (os.path.join(MAPAS, 'MAPA_REGION_SAN_MARTIN.jpg'), 'Región San Martín'),
             (os.path.join(MAPAS, 'MAPA_PROVINCIA_SAN_MARTIN.png'), 'Provincia de San Martín - distrito de Morales')]
    if all(os.path.exists(m) for m, _ in mapas):
        tabla(M, 'Mapas de ubicación', [t for _, t in mapas], [[('img', m, 4.6) for m, _ in mapas]], [W / 3] * 3,
              fuente_txt='Fuente: Cartografía referencial del expediente.')
    figura(M, foto, V.LEYENDA, 15.0, 'Fuente: Expediente técnico del proyecto.')
    M.t2('Accesibilidad y vías de conexión')
    M.par('El acceso al predio se realiza desde la ciudad de Tarapoto por vías asfaltadas y afirmadas hasta la carretera Oasis, frente '
          'a la cual está el ingreso del hogar, con su garita de control.')
    tabla(M, 'Vías de acceso', ['TRAMO', 'TIPO DE VÍA', 'DISTANCIA', 'TIEMPO', 'TRANSPORTE'], [
        ['Lima - Tarapoto', 'Vía aérea comercial', '620 km aprox.', '1 h 15 min', 'Avión comercial'],
        ['Tarapoto - Morales (carretera Oasis)', 'Terrestre asfaltada / afirmada', '5.0 km aprox.', '15 min', 'Vehículo motorizado / mototaxi']],
        [4.0, 3.8, 2.6, 2.2, W - 12.6], izq=(0,))
    M.par('La cercanía a la ciudad de Tarapoto permite la llegada del Cuerpo General de Bomberos Voluntarios, de la Policía Nacional y '
          'de las ambulancias en tiempos cortos; el patio de maniobras permite el ingreso de vehículos de emergencia.')
    M.t2('Objetivos')
    etiq(M, 'Objetivo general', 'Definir la señalización de seguridad, los medios de protección contra incendio y la organización para '
         'emergencias del Hogar de Refugio Temporal, de modo que todas las personas puedan alcanzar un lugar seguro en forma ordenada, '
         'rápida y guiada ante un sismo, un incendio u otra emergencia.')
    etiq(M, 'Objetivos específicos (señalización)', 'Definir cada señal de seguridad (forma, color, pictograma, dimensiones, material, '
         'braille y altura) según la NTP 399.010-1 y la Norma A.120, y su ubicación en cada edificación.')
    etiq(M, 'Objetivos específicos (protección)', 'Dotar al hogar de extintores, detección de humo e iluminación de emergencia acordes '
         'con los peligros de cada ambiente.')
    etiq(M, 'Objetivos específicos (organización)', 'Establecer la organización del hogar para emergencias (comité, brigadas y '
         'responsabilidades del personal) y los protocolos de actuación, con atención a las niñas y los niños, al horario nocturno y a '
         'la reserva de la identidad de las residentes.')
    M.t2('Normatividad')
    M.par('El desarrollo de la especialidad se sujeta a la normativa legal y técnica vigente en el Perú:')
    vines(M, ['Reglamento Nacional de Edificaciones (RNE): Norma A.010 Condiciones Generales de Diseño; Norma A.090 Servicios Comunales; '
              'Norma A.120 Accesibilidad Universal en Edificaciones; Norma A.130 Requisitos de Seguridad; Norma EM.010 Instalaciones '
              'Eléctricas Interiores.',
              'NTP 399.010-1 Señales de seguridad. Colores, símbolos, formas y dimensiones de señales de seguridad. Parte 1: Reglas para '
              'el diseño de las señales de seguridad y franjas de seguridad.',
              'NTP 350.043-1 Extintores portátiles. Selección, distribución, inspección, mantenimiento, recarga y prueba hidrostática '
              '(versión vigente).',
              'D.S. N.° 002-2018-PCM, Reglamento de Inspecciones Técnicas de Seguridad en Edificaciones (ITSE).',
              'Ley N.° 29664, Ley del Sistema Nacional de Gestión del Riesgo de Desastres (SINAGERD), y su reglamento.',
              'Ley N.° 30364, Ley para prevenir, sancionar y erradicar la violencia contra las mujeres y los integrantes del grupo '
              'familiar, y su reglamento (D.S. N.° 009-2016-MIMP).',
              'Normas NFPA de referencia: NFPA 10 (extintores portátiles), NFPA 72 (detección y alarma de incendios) y NFPA 101 '
              '(código de seguridad humana).'])
    M.t2('Alcance y documentos')
    M.par('Comprende las nueve edificaciones del hogar (E-01 a E-09) y los exteriores (garita de control, patios, estacionamientos y '
          'circulaciones). Las cantidades son las del metrado de evacuación y señalización, que cuenta cada símbolo dibujado en la '
          'planta de la lámina %s; las características de cada partida se detallan en las especificaciones técnicas de la '
          'especialidad.' % LS)

    # ================================================================== 2 DESCRIPCIÓN DEL HOGAR
    M.t1('DESCRIPCIÓN DEL HOGAR DE REFUGIO TEMPORAL')
    M.t2('Características generales')
    M.par('El hogar funciona en forma permanente, las 24 horas del día. Sus nueve edificaciones son de un solo nivel, sin escaleras '
          'ni rampas en las rutas de evacuación: cada ambiente sale directamente a las circulaciones exteriores techadas, a los patios '
          'y a las áreas abiertas del predio. Las edificaciones de administración, mantenimiento y talleres se ubican hacia el ingreso; '
          'el SUM-comedor y los módulos de enseñanza e infantil, al centro, junto al patio cívico y al patio de juegos; las tres '
          'edificaciones de habitaciones, hacia el fondo del predio, junto a la losa deportiva.')
    M.t2('Zonificación')
    tabla(M, 'Zonificación del hogar', ['ZONA', 'EDIFICACIONES Y AMBIENTES', 'USUARIO DIRECTO'], [
        ['Zona administrativa', 'E-01: área de bienvenida, sala de espera, sala de visitas, secretaría, dirección general, '
         'administración, sala de reuniones, oficina de monitoreo, data center y SS.HH.', 'Dirección, personal administrativo, '
         'visitantes autorizados'],
        ['Zona de asistencia técnica especializada', 'E-01: psicología, asistencia social y área legal; E-02: tópico; E-04: talleres de '
         'costura, bisutería y repostería, terapia grupal; E-05: módulo de enseñanza y módulo infantil',
         'Psicólogo(a), trabajador(a) social, abogado(a), instructores de talleres, residentes y sus hijas e hijos'],
        ['Zona residencial', 'E-06, E-07 y E-08: habitaciones simples, dobles, triples y especial con sus servicios higiénicos (23 '
         'habitaciones, 113 plazas)', 'Mujeres residentes y sus hijas e hijos'],
        ['Zona de alimentación', 'E-05: SUM-comedor, cocina, despensa y alacena, lavandería', 'Personal de cocina, residentes'],
        ['Zona de almacén y mantenimiento', 'E-02: almacén de donaciones; E-03: almacén general y de limpieza, residuos sólidos, '
         'maestranza, tablero eléctrico, subestación y grupo electrógeno; E-04: cuarto de cámaras de videovigilancia, archivo y depósito',
         'Personal de mantenimiento, logística y vigilancia'],
        ['Zona deportiva y exteriores', 'E-09: vestidores y almacén de implementos deportivos; losa deportiva, patio cívico, patio de '
         'juegos, biohuerto, estacionamientos, patio de maniobras, garita de control, PTAR, cisterna y tanque elevado',
         'Residentes, personal de vigilancia y mantenimiento, proveedores']],
        [3.6, W - 7.6, 4.0], tam=8.5, izq=(0, 1, 2))
    M.t2('Edificaciones y ambientes')
    M.par('Ambientes de cada edificación según la planta general de la lámina %s:' % LS)
    filas = []
    for cod, nombre in eds:
        if cod == 'EXT':
            continue
        a = [x for x in P['ambientes'].get(cod, {}) if x not in FUERA]
        if cod == 'E-09' and not a:
            nom = 'Vestidores con SS.HH. y almacén de implementos deportivos'
        else:
            vistos = []
            for x in sorted(a):
                n = P['ambientes'][cod][x]
                t = amb_txt(x) + (' (%d)' % n if n > 1 else '')
                vistos.append(t)
            nom = ', '.join(vistos)
        filas.append([cod, nombre, nom])
    tabla(M, 'Edificaciones y ambientes (planta general)', ['CÓDIGO', 'EDIFICACIÓN', 'AMBIENTES'], filas, [1.8, 4.2, W - 6.0], tam=8.5,
          izq=(1, 2))

    # ================================================================== 3 COMPONENTES DEL PLAN
    M.t1('COMPONENTES DEL PLAN DE SEGURIDAD')
    M.t2('Métodos y procedimientos de mitigación de riesgos')
    M.par('Los métodos operacionales y espaciales del hogar están orientados a prevenir, reducir y mitigar los riesgos que puedan '
          'afectar la integridad física, emocional y psicológica de las residentes, de sus hijas e hijos y del personal:')
    for et, t in (('Organización y uso de los espacios', 'habitaciones agrupadas en tres edificaciones con salida directa a las '
                   'circulaciones exteriores; atención especializada y talleres separados de la zona residencial.'),
                  ('Horarios y actividades', 'horarios de alimentación, atención, talleres y descanso que eviten aglomeraciones y '
                   'mantengan libres los pasadizos, las salidas y las rutas de evacuación.'),
                  ('Condiciones físico-ambientales', 'ventilación e iluminación natural, protección contra la humedad y la lluvia, y '
                   'circulaciones exteriores techadas con pisos antideslizantes.'),
                  ('Equipamiento y mobiliario', 'mobiliario estable y fijado a muros (armarios, estantes, archivadores y camarotes), sin '
                   'aristas peligrosas, con materiales de buen comportamiento frente al fuego.'),
                  ('Seguridad y control de accesos', 'cerco perimétrico, garita de control en el ingreso, registro de visitas, '
                   'videovigilancia y reserva de la ubicación y de la identidad de las residentes.'),
                  ('Prevención y respuesta ante emergencias', 'señalización de seguridad, extintores, detección de humo, iluminación '
                   'de emergencia, salidas accesibles y simulacros periódicos, también nocturnos.'),
                  ('Protección de las residentes', 'atención a mujeres gestantes, con discapacidad o con niñas y niños pequeños, y '
                   'acompañamiento emocional con enfoque sensible al trauma después de cada evento.')):
        etiq(M, et, t)
    M.t2('Identificación de peligros por edificación')
    M.par('A partir de los ambientes de cada edificación se identifican los peligros principales y las medidas de seguridad del proyecto:')
    tabla(M, 'Peligros y medidas por edificación', ['EDIFICACIÓN', 'AMBIENTES CRÍTICOS', 'PELIGRO PRINCIPAL', 'MEDIDAS DEL PROYECTO'],
          [list(x) for x in PELIGROS], [3.0, 3.8, 3.8, W - 10.6], tam=8, izq=(0, 1, 2, 3))
    M.t2('Planos del sistema de seguridad')
    vines(M, ['Lámina %s, %s (escala %s): ubicación de cada señal y equipo de seguridad en las nueve edificaciones y en exteriores, '
              'con la leyenda de símbolos, alturas y cantidades.' % (LS, D.LAMINA_S[1].lower(), D.LAMINA_S[2]),
              'Lámina %s, %s (escala %s): %d rutas de evacuación con su longitud y %d zonas de evacuación exteriores con su aforo.' % (D.LAMINA_E + (len(D.rutas()), len(D.zonas())))])
    M.par('Forman parte de este plan la población y la ocupación del hogar, el metrado y las especificaciones técnicas de evacuación '
          'y señalización.')

    # ================================================================== 4 OCUPACIÓN
    M.t1('DENSIDAD DE OCUPACIÓN Y AFORO')
    M.t2('Población del hogar')
    M.par('Para la evacuación, el número de ocupantes de las habitaciones es el de sus camas (Norma A.030, art. 5): las 23 habitaciones '
          'suman %d plazas para mujeres con sus hijas e hijos. Se suman %d personas de personal (administración, atención '
          'especializada, cocina, mantenimiento y vigilancia) y %d usuarios temporales (visitas autorizadas, participantes de talleres y '
          'de la sala de reuniones, personal eventual), con lo que la capacidad máxima simultánea del hogar es de %d personas.' % (
              Pb['residentes'], Pb['personal'], Pb['temporales'], Pb['maxima']))
    tabla(M, 'Plazas de la zona residencial', ['HABITACIÓN', 'CANT.', 'PLAZAS POR HABITACIÓN', 'PLAZAS'],
          [[a, n, c, n * c] for a, n, c in D.PLAZAS] + [['TOTAL', sum(n for _, n, _ in D.PLAZAS), '', Pb['residentes']]],
          [W - 9.0, 2.0, 4.5, 2.5], izq=(0,), colores={(len(D.PLAZAS), k): ROSA for k in range(4)})
    tabla(M, 'Población del hogar', ['POBLACIÓN', 'DETALLE', 'PERSONAS'], [
        ['Residentes', 'Mujeres con sus hijas e hijos (plazas de las habitaciones)', Pb['residentes']],
        ['Personal', 'Administración, atención especializada, cocina, mantenimiento y vigilancia', Pb['personal']],
        ['Permanentes', 'Residentes + personal', Pb['permanentes']],
        ['Temporales', 'Visitas, talleres, sala de reuniones y personal eventual', Pb['temporales']],
        ['CAPACIDAD MÁXIMA', 'Permanentes + temporales', Pb['maxima']]], [3.6, W - 6.0, 2.4], izq=(0, 1),
        colores={(4, 0): ROSA, (4, 1): ROSA, (4, 2): ROSA})
    sub(M, 'Personal')
    M.par('Son las personas que permanecen en el hogar en turnos de trabajo: dirección y administración, profesionales de atención '
          '(psicología, asistencia social, área legal y tópico), instructores de talleres y personal de cocina, limpieza, mantenimiento '
          'y vigilancia. Conocen las instalaciones, las salidas y las zonas seguras y conducen la evacuación.')
    sub(M, 'Residentes')
    M.par('Mujeres víctimas de violencia y sus hijas e hijos. Entre ellas puede haber gestantes, mujeres con discapacidad y niñas y '
          'niños pequeños que necesitan ser conducidos de la mano; de noche se encuentran dormidas, por lo que la detección temprana '
          'y la iluminación de emergencia son esenciales.')
    sub(M, 'Personas ajenas al hogar')
    M.par('Visitantes que permanecen poco tiempo (familiares autorizados, profesionales de instituciones vinculadas, proveedores) y '
          'que no necesariamente conocen los sistemas de seguridad: durante su visita están a cargo del personal que los recibe y no '
          'ingresan a la zona residencial.')
    M.t2('Índices de ocupación')
    M.par('El aforo de cada ambiente se establece con los índices de ocupación del RNE según su uso:')
    tabla(M, 'Índices de ocupación', ['AMBIENTE', 'NORMA DE REFERENCIA', 'ÍNDICE'], [
        ['Oficinas administrativas', 'RNE A.090, art. 11', '10.0 m²/persona'],
        ['Habitaciones de las residentes', 'RNE A.030, art. 5 (número de camas)', 'según camas'],
        ['Sala de reuniones', 'RNE A.090, art. 11', '1.0 m²/persona'],
        ['Talleres y actividades grupales', 'RNE A.090, art. 11, uso semejante', '1.0 m²/persona*'],
        ['Sala de espera y recepción', 'RNE A.090, art. 11, uso semejante', '1.0 m²/persona*'],
        ['Cocina y áreas de servicio', 'RNE A.070, por analogía', '9.3 m²/persona*'],
        ['Almacenes y depósitos', 'RNE A.070, por analogía', '40.0 m²/persona*'],
        ['Estacionamientos', 'RNE A.090, art. 11', '16.0 m²/persona']], [6.0, W - 9.0, 3.0], izq=(0, 1))
    M.par('(*) Índice adoptado por analogía con un uso semejante, al no figurar el ambiente en forma expresa en la norma citada.', 9, cur=True)
    M.t2('Letreros de aforo')
    M.par('El aforo de cada ambiente se publica en un letrero de aforo junto a su ingreso: la lámina %s ubica %d letreros en las '
          'edificaciones E-01 a E-08. El número de personas de cada letrero es el aforo de su ambiente según el cálculo de aforo de '
          'arquitectura.' % (LS, q['LETRERO DE AFORO']))

    # ================================================================== 5 MEDIOS DE EVACUACIÓN
    M.t1('MEDIOS DE EVACUACIÓN')
    M.t2('Criterios de diseño')
    vines(M, ['Evacuación horizontal: todas las edificaciones son de un nivel y cada ambiente sale directamente al exterior.',
              'Las rutas van por las circulaciones exteriores y los patios, sin cruzar zonas de riesgo (cocina, subestación, grupo '
              'electrógeno, tanque elevado ni PTAR), y terminan en las zonas de evacuación exteriores de la lámina %s.' % D.LAMINA_E[0],
              'El recorrido desde la puerta más alejada hasta un lugar seguro no supera %.0f m, distancia máxima de recorrido en '
              'edificaciones sin rociadores (Norma A.130).' % D.D_MAX,
              'Las puertas de los ambientes de mayor ocupación abren en el sentido de la evacuación y no se cierran con llave mientras '
              'haya personas en el interior.',
              'Las salidas se señalizan con %d señales de salida y el sentido de la evacuación con %d señales de dirección de '
              'evacuación, fotoluminiscentes, y se iluminan con %d unidades de luces de emergencia.' % (
                  q['SALIDA CON'], q['DIRECCIÓN DE EVACUACIÓN'], q['UNIDAD DE LUCES'])])
    M.t2('Ancho de puertas y pasajes')
    M.par('Según la Norma A.130, el ancho libre de los medios de evacuación se calcula multiplicando el número de ocupantes por 0.005 m, '
          'sin ser menor que los mínimos normativos: 0.90 m en puertas de evacuación (1.00 m en las de uso de personas con discapacidad, '
          'Norma A.120) y 1.20 m en pasajes de circulación (Norma A.010). Con la capacidad máxima del hogar (%d personas) el ancho total '
          'requerido es de %.2f m, que se reparte entre las %d salidas señalizadas de las nueve edificaciones: en cada ambiente rige el '
          'mínimo normativo.' % (Pb['maxima'], Pb['maxima'] * 0.005, q['SALIDA CON']))
    vines(M, ['Habitaciones de las residentes: puerta de acceso y salida de 1.20 m; puertas de servicios higiénicos de 1.00 m.',
              'Zona administrativa: puertas de acceso de 1.00 m, incluidas las de los servicios higiénicos para personas con discapacidad.',
              'Pasajes de circulación: 1.20 m de ancho libre como mínimo.'])
    M.t2('Rutas de evacuación')
    rts = D.rutas(); E = D.evac()
    from collections import Counter
    cr = Counter(r['ed'] for r in rts)
    M.par('La lámina %s define %d rutas de evacuación, numeradas de la RUTA 01 a la RUTA %02d, cada una con su longitud, desde la puerta '
          'de cada ambiente (punto de partida señalado en la planta) hasta una zona de evacuación exterior. Todas son horizontales, '
          'por las circulaciones exteriores techadas y los patios, y miden entre %.2f m y %.2f m: ninguna supera el recorrido máximo de '
          '%.0f m de la Norma A.130.' % (D.LAMINA_E[0], len(rts), len(rts), min(r['L'] for r in rts), max(r['L'] for r in rts), D.D_MAX))
    filas = []
    for cod, nombre in eds:
        rr = [r for r in rts if r['ed'] == cod]
        if rr:
            filas.append([cod, nombre, len(rr), '%.2f' % min(r['L'] for r in rr), '%.2f' % max(r['L'] for r in rr)])
    filas.append(['TOTAL', '', len(rts), '%.2f' % min(r['L'] for r in rts), '%.2f' % max(r['L'] for r in rts)])
    tabla(M, 'Rutas de evacuación por edificación (lámina %s)' % D.LAMINA_E[0], ['CÓDIGO', 'EDIFICACIÓN', 'RUTAS', 'L MÍN. (m)', 'L MÁX. (m)'],
          filas, [1.8, W - 9.0, 2.2, 2.5, 2.5], izq=(1,), colores={(len(filas) - 1, k): ROSA for k in range(5)})
    M.t2('Tiempos de evacuación')
    M.par('Conforme al artículo 25 de la Norma A.130, el cálculo del tiempo de evacuación es referencial. El tiempo de desplazamiento '
          'es la longitud de la ruta entre la velocidad de marcha: %.2f m/s para grupos con niñas y niños pequeños o personas con '
          'movilidad reducida y %.2f m/s para adultos. La ruta más larga, de %.2f m, se recorre en %.0f s a la velocidad más baja: toda la '
          'población puede alcanzar una zona de evacuación en poco más de un minuto.' % (D.V_EVAC[0], D.V_EVAC[1], max(r['L'] for r in rts),
                                                                                        max(r['L'] for r in rts) / D.V_EVAC[0]))
    filas = [['RUTA %02d' % r['n'], r['ed'], '%.2f' % r['L'], '%.0f' % r['t1'], '%.0f' % r['t2'], 'cumple' if r['cumple'] else 'no cumple']
             for r in rts]
    tabla(M, 'Rutas de evacuación: longitud y tiempo de desplazamiento (referencial)', ['RUTA', 'ORIGEN', 'L (m)',
          't a %.2f m/s (s)' % D.V_EVAC[0], 't a %.2f m/s (s)' % D.V_EVAC[1], 'L ≤ 45 m'], filas, [2.4, 2.2, 2.2, 3.0, 3.0, W - 12.8], tam=8)
    M.t2('Zonas seguras internas')
    M.par('Dentro de los ambientes se señalizan %d zonas seguras en caso de sismo (junto a columnas y muros estructurales, lejos de '
          'ventanas y de mobiliario que pueda caer), para el repliegue durante el movimiento cuando no es posible salir de inmediato.'
          % q['ZONA SEGURA EN'])
    M.t2('Zonas de evacuación exteriores')
    zs = D.zonas(); re_, ri_ = D.radios(); a = D.area_zona()
    M.par('Al final de las rutas se ubican %d zonas de evacuación en caso de emergencia, pintadas en el piso de concreto de los patios y '
          'áreas abiertas como un anillo amarillo de %.2f m de diámetro exterior y %.2f m de ancho, lejos de fachadas, cables, árboles, '
          'del tanque elevado y de elementos que puedan caer. La lámina %s indica el aforo de cada zona; en conjunto reciben %d '
          'personas.' % (len(zs), 2 * re_, re_ - ri_, D.LAMINA_E[0], sum(z['aforo'] for z in zs)))
    tabla(M, 'Zonas de evacuación en caso de emergencia (lámina %s)' % D.LAMINA_E[0], ['ZONA', 'UBICACIÓN (edificación más cercana)',
          'AFORO (personas)', 'ÁREA PINTADA (m²)'],
          [[z['numero'], '%s %s' % (z['cerca'], D.EDIFICACIONES[z['cerca']]), z['aforo'], '%.2f' % a] for z in zs] +
          [['TOTAL', '', sum(z['aforo'] for z in zs), '%.2f' % (len(zs) * a)]], [1.6, W - 8.2, 3.2, 3.4], tam=8.5, izq=(1,),
          colores={(len(zs), k): ROSA for k in range(4)})
    figura(M, os.path.join(FIG, 'planta_evacuacion.png'), 'Planta general de evacuación (lámina %s)' % D.LAMINA_E[0], 12.5,
           'Fuente: Lámina %s del expediente de arquitectura.' % D.LAMINA_E[0])

    # ================================================================== 6 ORGANIZACIÓN PARA EMERGENCIAS
    M.t1('ORGANIZACIÓN PARA EMERGENCIAS')
    M.t2('Alcances')
    M.par('La administración y el personal del hogar están organizados para prevenir, responder y actuar de manera oportuna ante '
          'emergencias que pongan en peligro la vida, la integridad física y la salud de las residentes, de sus hijas e hijos, del '
          'personal y de los visitantes, y para proteger la infraestructura, los bienes y el entorno del hogar. Para ello se conforma '
          'un Comité de Seguridad y se organizan brigadas de emergencia, responsables de las acciones preventivas y de respuesta del '
          'Plan de Contingencia.')
    M.par('Por la naturaleza del servicio, las acciones de emergencia se desarrollan con un enfoque de derechos humanos, de género y '
          'de atención sensible al trauma: se evita exponer a las residentes a situaciones de riesgo o de revictimización y se protege '
          'la reserva de su ubicación y de su identidad. Como el hogar funciona las 24 horas, en cada turno, incluido el nocturno, '
          'debe haber personal capacitado de cada brigada.')
    M.par('Las emergencias que podrían presentarse se clasifican según su origen:')
    etiq(M, 'Naturales', 'sismos, lluvias intensas, inundaciones, vientos fuertes y descargas eléctricas atmosféricas.')
    etiq(M, 'Tecnológicas o antrópicas', 'incendios, cortocircuitos, fugas de gas en la cocina, fallas de las instalaciones eléctricas y '
         'sanitarias, accidentes e intoxicaciones.')
    etiq(M, 'Sociales y de seguridad', 'amenazas externas, intentos de ingreso no autorizado o cualquier evento que comprometa la '
         'protección de las residentes.')
    M.t2('Comité de Seguridad')
    M.par('Es responsable de formular, implementar, supervisar y actualizar el Plan de Contingencia del hogar y de conformar, capacitar '
          'y supervisar las brigadas. Lo integran, según la organización del hogar:')
    etiq(M, 'Director(a) del hogar (director de emergencias)', 'dirige y coordina la respuesta, activa los protocolos y articula con los '
         'servicios externos de emergencia.')
    etiq(M, 'Responsable de mantenimiento y seguridad', 'verifica las condiciones de la infraestructura, las instalaciones y los equipos '
         'de emergencia y coordina su mantenimiento.')
    etiq(M, 'Responsable de atención y protección de las residentes', 'coordina la protección de las mujeres y de sus hijas e hijos '
         'durante la emergencia, según sus necesidades particulares.')
    etiq(M, 'Jefe(a) de brigadas', 'organiza y supervisa las brigadas de lucha contra incendio, primeros auxilios y evacuación.')
    sub(M, 'Funciones del Comité de Seguridad')
    vines(M, ['Elaborar, difundir y actualizar el Plan de Contingencia del hogar.',
              'Identificar y evaluar los peligros y riesgos que puedan afectar a las residentes, al personal, a la infraestructura y al entorno.',
              'Programar la capacitación del personal en prevención, evacuación, primeros auxilios y uso de extintores.',
              'Organizar simulacros de evacuación (al menos dos al año, uno nocturno), evaluar sus resultados y aplicar las mejoras.',
              'Supervisar la señalización, las salidas, las rutas de evacuación, las zonas seguras y las condiciones de accesibilidad.',
              'Coordinar la inspección y el mantenimiento de los extintores, los detectores de humo y las luces de emergencia.',
              'Coordinar con el Cuerpo de Bomberos, los servicios de salud, la Policía Nacional, Defensa Civil y la municipalidad, '
              'resguardando la confidencialidad de la ubicación del hogar.',
              'Evaluar cada emergencia o simulacro, elaborar el informe y actualizar los procedimientos.',
              'Verificar que las medidas de seguridad se mantengan conforme a los planos aprobados para la Inspección Técnica de Seguridad '
              'en Edificaciones (ITSE).'])
    M.t2('Director de emergencias')
    M.par('Es el responsable de planificar las acciones para hacer frente a las emergencias e interviene antes, durante y después de un '
          'siniestro. Vela por que el hogar cuente con el equipamiento operativo y por que las brigadas estén conformadas por personal '
          'seleccionado y capacitado. Supervisa en forma permanente que:')
    vines(M, ['Los %d extintores estén cargados, señalizados y libres de obstáculos.' % ext['total'],
              'Los %d detectores de humo y las %d unidades de luces de emergencia estén en funcionamiento.' % (q['DETECTOR DE HUMO'], q['UNIDAD DE LUCES']),
              'El botiquín de primeros auxilios del tópico esté implementado; se disponga de radios portátiles y linternas.',
              'Los pasadizos, las salidas y las rutas permanezcan libres de obstáculos.',
              'El directorio telefónico de emergencia esté actualizado y a la vista en la administración, la garita y cada edificación de '
              'habitaciones.'])
    M.t2('Encargado de mantenimiento y seguridad')
    M.par('Su labor es preventiva: asegura que el sistema de prevención y control de incendios esté plenamente operativo. Ante una '
          'emergencia:')
    vines(M, ['Ordena el corte de energía eléctrica del área afectada desde el tablero eléctrico de mantenimiento (E-03).',
              'Cierra la llave general del gas de la cocina (E-05) si la emergencia lo requiere.',
              'Da aviso a todo el personal y moviliza a las brigadas al perímetro del evento.',
              'Facilita el acceso de los bomberos al predio por el patio de maniobras.',
              'Vela por que equipos, señales y condiciones del inmueble se mantengan conforme a los planos aprobados.'])
    M.t2('Brigadas de emergencia')
    M.par('Están conformadas por personal seleccionado por sus condiciones físicas y psicológicas y capacitado para actuar en '
          'siniestros. Cada brigada tiene un jefe, un subjefe (alterno) y brigadistas, presentes en todos los turnos:')
    tabla(M, 'Brigadas de emergencia', ['BRIGADA', 'INTEGRANTES POR TURNO', 'EQUIPO', 'FUNCIONES PRINCIPALES'], [
        ['Contra incendios', 'Personal de mantenimiento, vigilancia y cocina', 'Extintores PQS, linterna, EPP',
         'Conocer tableros, llaves de gas y agua y extintores; atacar amagos de incendio; dar la alarma; ordenar la evacuación si la '
         'situación es crítica; transferir el mando a los bomberos.'],
        ['Primeros auxilios', 'Personal del tópico, psicología y asistencia social', 'Botiquín, camilla, directorio telefónico',
         'Brindar primeros auxilios y contención emocional; trasladar heridos graves; llamar a SAMU, bomberos y policía.'],
        ['Evacuación', 'Personal de atención y de vigilancia de cada edificación', 'Silbato, chaleco, linterna, lista de residentes',
         'Conducir a las residentes y a sus hijas e hijos a las zonas de evacuación; abrir las puertas de salida; contar a las personas; '
         'verificar que nadie quede en los ambientes.']], [3.2, 3.6, 3.2, W - 10.0], tam=8.5, izq=(0, 1, 2, 3))
    sub(M, 'Brigada de evacuación')
    vines(M, ['Conocer la distribución de los ambientes, las salidas, las zonas seguras internas y las zonas de evacuación de la lámina %s.' % D.LAMINA_E[0],
              'Ayudar primero a las mujeres con niñas y niños pequeños, gestantes o con discapacidad.',
              'Llevar la lista de residentes de su edificación y hacer el conteo en la zona de evacuación.',
              'Revisar habitaciones, servicios higiénicos y depósitos antes de salir y ser los últimos en abandonar la edificación.',
              'Brindar contención emocional durante y después de la evacuación.'])
    M.t2('Responsabilidades del personal')
    vines(M, ['Cumplir y hacer cumplir las disposiciones de seguridad del Plan de Contingencia y del reglamento interno del hogar.',
              'Velar por la integridad de las residentes, de sus hijas e hijos, de sus compañeros y de los visitantes.',
              'No bloquear tableros eléctricos, extintores ni señales de seguridad; no cerrar con llave las puertas de salida con personas dentro.',
              'No dejar muebles, bultos ni materiales en pasadizos y rutas; no improvisar conexiones eléctricas.',
              'Mantener la cocina limpia de grasa y la válvula del gas cerrada al terminar la jornada.',
              'Controlar el ingreso y la salida de personas y no revelar la ubicación ni la identidad de las residentes.'])

    # ================================================================== 7 PROTOCOLOS
    M.t1('PROTOCOLOS DE ACTUACIÓN')
    M.t2('Ante sismos')
    sub(M, 'Antes (fase preventiva)')
    vines(M, ['Conocer las salidas, las zonas seguras internas y las zonas de evacuación de cada edificación.',
              'Fijar a los muros los armarios, estantes, archivadores y camarotes; no colocar objetos pesados en alto.',
              'Identificar la ubicación del tablero eléctrico, de la llave de agua y de la llave general del gas.',
              'Mantener libres pasadizos, circulaciones y salidas; realizar simulacros periódicos, también nocturnos.'])
    sub(M, 'Durante (fase de respuesta)')
    vines(M, ['Mantener la calma y transmitir serenidad; la fase más intensa dura entre 20 y 40 segundos.',
              'Si no es posible salir de inmediato, replegarse en las zonas seguras internas señalizadas, lejos de ventanas.',
              'En exteriores, alejarse de fachadas, del cerco, de postes, del tanque elevado y de árboles.'])
    sub(M, 'Después (fase de rehabilitación)')
    vines(M, ['Evacuar por las salidas señaladas hacia las zonas de evacuación, sin correr, sin empujar y sin gritar.',
              'Contar a las residentes, a sus hijas e hijos y al personal; reportar ausencias.',
              'Inspeccionar daños en estructuras e instalaciones eléctricas, sanitarias y de gas antes de reingresar.',
              'Atender a los heridos y brindar contención emocional.'])
    M.t2('Ante incendios')
    sub(M, 'Antes (fase preventiva)')
    vines(M, ['Vigilar calentamientos en tomacorrientes, interruptores y tableros; reportar olor a quemado.',
              'Almacenar productos de limpieza y combustibles en envases cerrados y fuera del alcance de las niñas y los niños.',
              'Mantener la cocina limpia de grasa, el cilindro y las mangueras del gas en buen estado y la válvula cerrada fuera de uso.',
              'Mantener los extintores señalizados, cargados y libres de obstáculos.'])
    sub(M, 'Durante (fase de respuesta)')
    vines(M, ['Dar la alarma a viva voz a los ambientes vecinos al sonar un detector o al ver humo o fuego.',
              'Usar el extintor solo si el fuego es incipiente y se cuenta con capacitación, con la salida a la espalda.',
              'Cortar la energía eléctrica y cerrar la llave del gas.', 'Evacuar los ambientes con humo desplazándose agachado, cubriendo '
              'nariz y boca con un paño húmedo; tocar las puertas antes de abrirlas.', 'No regresar por objetos personales; llamar al '
              'Cuerpo de Bomberos (116).'])
    sub(M, 'Uso del extintor')
    vines(M, ['Retirar el pasador de seguridad.', 'Apuntar la boquilla a la base del fuego.', 'Presionar la manija.',
              'Barrer de lado a lado la base de las llamas hasta extinguirlas.', 'En equipos eléctricos no usar agua.'])
    sub(M, 'Después (fase de rehabilitación)')
    vines(M, ['No reingresar hasta que los bomberos lo autoricen.', 'Recargar los extintores usados y reponer el botiquín.'])
    M.t2('Ante lluvias intensas')
    vines(M, ['Mantener limpias las canaletas, montantes, cunetas y rejillas del drenaje pluvial antes de la temporada de lluvias.',
              'Ante tormentas eléctricas, suspender las actividades en la losa deportiva y los patios.',
              'Si el agua ingresa a un ambiente, cortar la energía de ese circuito y trasladar a las personas a otra edificación.'])
    M.t2('Ante fuga de gas en la cocina')
    vines(M, ['Cerrar la válvula del cilindro y la llave general; no accionar interruptores ni encender fuego.',
              'Ventilar abriendo puertas y ventanas; evacuar la cocina y el SUM-comedor.', 'Llamar a los bomberos si el olor persiste.'])
    M.t2('Ante corte de energía')
    vines(M, ['Las unidades de luces de emergencia se encienden automáticamente e iluminan salidas, circulaciones y habitaciones.',
              'El personal de turno recorre las habitaciones con linterna y tranquiliza a las residentes y a sus hijas e hijos.',
              'El encargado de mantenimiento verifica el tablero eléctrico y el grupo electrógeno (E-03).'])
    M.t2('Ante un intento de ingreso no autorizado')
    vines(M, ['El personal de la garita no permite el ingreso, no confirma la presencia de ninguna residente y llama a la Policía '
              'Nacional (105).', 'Las residentes y sus hijas e hijos se repliegan en las habitaciones o en el ambiente que indique la '
              'dirección, lejos del ingreso.', 'La dirección registra el hecho y evalúa con las autoridades las medidas de protección.'])

    # ================================================================== 8 PROCEDIMIENTO DE EVACUACIÓN
    M.t1('PROCEDIMIENTO DE EVACUACIÓN')
    M.t2('Detección y alarma')
    M.par('Al detectarse una emergencia (detector de humo o aviso del personal), el director de emergencias evalúa la situación y '
          'dispone la evacuación inmediata si hay peligro para las personas, la llamada a los servicios de emergencia y, sin riesgos '
          'mayores, la atención de los heridos y la neutralización de la emergencia con los medios del hogar.')
    M.t2('Desarrollo de la evacuación')
    vines(M, ['Evacuar con rapidez y orden, sin correr, sin gritar y sin provocar pánico, siguiendo las señales de dirección de evacuación.',
              'Las niñas y los niños pequeños salen tomados de la mano de su madre o de un adulto del personal.',
              'Los responsables son los últimos en salir, después de revisar habitaciones, servicios higiénicos, depósitos y oficinas.',
              'Controlar el tránsito de vehículos en el patio de maniobras y los estacionamientos.',
              'En la zona de evacuación, contar a todas las personas con la lista de residentes y de personal.'])
    M.t2('Llamadas de emergencia')
    M.par('Asegurada la evacuación, se llama a los servicios de emergencia con calma y brevedad, indicando la ubicación (predio rural Los '
          'Mangos, frente a la carretera Oasis, Morales) y lo ocurrido, sin dar datos de las residentes.')
    tabla(M, 'Directorio de emergencias', ['INSTITUCIÓN', 'TELÉFONO'], [[a, b] for a, b in DIRECTORIO], [W - 3.0, 3.0], izq=(0,))
    M.t2('Fin de la emergencia')
    M.par('Neutralizada la emergencia y con autorización de la ayuda externa, se evalúan los daños, se restablecen las actividades, se '
          'investigan las causas y se proponen medidas correctivas; el Comité de Seguridad registra lo actuado y actualiza el plan.')

    # ================================================================== 9 PROTECCIÓN CONTRA INCENDIO
    M.t1('PROTECCIÓN CONTRA INCENDIO Y EMERGENCIA')
    M.t2('Extintores portátiles')
    M.par('Se instalan %d extintores de polvo químico seco (PQS) multipropósito tipo ABC de 9 kg, para fuegos de clase A, B y C, uno por '
          'cada señal de ubicación de extintor de la lámina %s. Cada extintor se cuelga en su soporte con la parte superior a no más de '
          '1.50 m del piso, visible, de libre acceso, con su señal encima y su tarjeta de control, y se selecciona, inspecciona y recarga '
          'según la NTP 350.043-1.' % (ext['total'], LS))
    filas = [[c, n, ext['por'].get(c, 0)] for c, n in eds if ext['por'].get(c)]
    filas.append(['TOTAL', '', ext['total']])
    tabla(M, 'Distribución de extintores (lámina %s)' % LS, ['CÓDIGO', 'EDIFICACIÓN', 'PQS 9 kg'], filas, [2.0, W - 4.8, 2.8], izq=(1,),
          colores={(len(filas) - 1, k): ROSA for k in range(3)})
    M.t2('Detección de humo')
    M.par('Se instalan %d detectores de humo fotoeléctricos en el techo de los ambientes de las nueve edificaciones y de la garita, de '
          'modo que un incendio, también nocturno, se detecte en su inicio. Su alimentación y su conexión corresponden a las '
          'instalaciones eléctricas del proyecto.' % q['DETECTOR DE HUMO'])
    M.t2('Iluminación de emergencia')
    M.par('Se instalan %d unidades de luces de emergencia autónomas a 2.10 m del piso, en salidas, circulaciones, habitaciones y '
          'ambientes, con autonomía mínima de 90 minutos y encendido automático al cortarse la energía (Norma A.130).' % q['UNIDAD DE LUCES'])
    M.t2('Riesgo eléctrico y residuos')
    M.par('Se señalizan con la señal de atención riesgo eléctrico %d tableros y ambientes eléctricos, y con la señal de punto ecológico '
          'los %d puntos de acopio selectivo de residuos sólidos de los exteriores.' % (q['ATENCIÓN RIESGO'], q['PUNTO ECOL']))

    # ================================================================== 10 SEÑALIZACIÓN
    M.t1('SEÑALIZACIÓN DE SEGURIDAD')
    M.t2('Definición y clasificación')
    M.par('Señal de seguridad es la que, por la combinación de una forma geométrica y un color, proporciona una indicación general '
          'relativa a la seguridad y que, con un símbolo gráfico o un texto, proporciona una indicación particular. Según la NTP '
          '399.010-1 se clasifican en:')
    etiq(M, 'Señales de evacuación y emergencia', 'indican las salidas, el sentido de la evacuación y las zonas seguras. Color verde, '
         'forma cuadrada o rectangular.')
    etiq(M, 'Señales de equipos contra incendio', 'ubican e identifican los equipos de protección contra incendio (extintores). Color '
         'rojo, forma cuadrada o rectangular.')
    etiq(M, 'Señales de advertencia', 'advierten un peligro (riesgo eléctrico). Color amarillo, forma triangular con borde negro.')
    etiq(M, 'Señales informativas', 'informan sobre servicios e instalaciones (servicios higiénicos, punto ecológico, aforo). Color azul o verde.')
    tabla(M, 'Formas y colores de seguridad (NTP 399.010-1)', ['TIPO', 'FORMA', 'COLOR DE SEGURIDAD', 'CONTRASTE', 'PICTOGRAMA', 'EJEMPLOS DEL PROYECTO'], [
        ['Evacuación y emergencia', 'Cuadrado / rectángulo', 'Verde', 'Blanco', 'Blanco', 'Salida, dirección de evacuación, zona segura, punto ecológico'],
        ['Equipos contra incendio', 'Cuadrado / rectángulo', 'Rojo', 'Blanco', 'Blanco', 'Extintor PQS'],
        ['Advertencia', 'Triángulo equilátero', 'Amarillo', 'Negro', 'Negro', 'Atención riesgo eléctrico'],
        ['Información', 'Cuadrado / rectángulo', 'Azul', 'Blanco', 'Blanco', 'SS.HH., aforo']],
        [3.0, 2.6, 2.2, 1.8, 2.0, W - 11.6], tam=8, izq=(0, 5),
        colores={(0, 2): '00874B', (1, 2): 'CC141E', (2, 2): 'FFCD00', (3, 2): '004696'})
    M.t2('Criterios de instalación')
    vines(M, ['Las señales de evacuación y de equipos contra incendio son fotoluminiscentes, para que se vean sin energía eléctrica.',
              'Las señales indicadas con braille llevan una placa de acrílico con su texto en braille (Norma A.120).',
              'La altura de instalación se mide desde el piso terminado hasta el borde inferior de la señal; la señal de extintor va encima '
              'del equipo, a 1.80 m, visible por sobre el extintor.',
              'Las señales se instalan sobre superficies terminadas, firmes y niveladas, y no deben quedar tapadas por puertas abiertas, '
              'muebles ni equipos.'])
    M.t2('Descripción de la simbología utilizada en el proyecto')
    M.par('La simbología es la de la leyenda de la lámina %s. Cada señal se muestra tal como se fabrica (forma, color, pictograma, '
          'texto y placa en braille), con su cantidad, que es la dibujada en la planta:' % LS)
    filas = []
    for p in pts:
        if not p['und']:
            continue
        filas.append([('img', img[p['item']], 1.9), R_cap(p['desc'].replace(' CON BRAILLE', '')).replace('pqs', 'PQS').replace(' abc', ' ABC')
                      .replace('(pqs)', '(PQS)'), p['uso'], p['dim'], p['altura'], p['total']])
    tabla(M, 'Simbología del proyecto (lámina %s)' % LS, ['SEÑAL', 'DENOMINACIÓN', 'DESCRIPCIÓN', 'DIMENSIONES', 'ALTURA', 'CANT.'],
          filas, [2.3, 3.4, W - 10.9, 2.3, 1.7, 1.2], tam=8, izq=(1, 2))
    M.t2('Ficha de cada señal')
    M.par('Para la fabricación, la instalación y la supervisión, cada señal y equipo tiene su ficha con la función, las dimensiones, el '
          'material, la altura, la cantidad y las edificaciones donde se ubica (E-01 a E-09; EXT = exteriores):')
    for p in pts:
        if p['und'] is None:
            sub(M, '01.%s  %s' % (p['item'], p['desc'].capitalize()))
            continue
        ficha(M, p, img[p['item']])
    M.t2('Distribución por edificación')
    cols = [('SALIDA CON', 'Salida'), ('DIRECCIÓN DE EVACUACIÓN', 'Direc.'), ('ZONA SEGURA EN', 'Zona seg.'), ('LETRERO DE AFORO', 'Aforo'),
            ('SEÑAL DE UBICACIÓN DE EXTINTOR PQS', 'Extintor'), ('SEÑALES DE SERVICIOS', 'SS.HH.'), ('UNIDAD DE LUCES', 'Luces'),
            ('DETECTOR DE HUMO', 'Detector')]
    filas = []
    for cod, nombre in eds:
        fila = [cod]
        for clave, _ in cols:
            n = sum(por[k]['por'].get(cod, 0) for k in por if k.startswith(clave))
            fila.append(n or '—')
        filas.append(fila)
    filas.append(['TOTAL'] + [sum(f[k] for f in filas if f[k] != '—') for k in range(1, len(cols) + 1)])
    tabla(M, 'Señales y equipos principales por edificación (planta de %s)' % LS, ['EDIF.'] + [c[1] for c in cols], filas,
          [1.6] + [(W - 1.6) / len(cols)] * len(cols), tam=8.5, colores={(len(filas) - 1, k): ROSA for k in range(len(cols) + 1)})
    M.par('Además, %d señales de atención riesgo eléctrico en los tableros y ambientes eléctricos y %d señales de punto ecológico en '
          'exteriores. El detalle de todas las partidas por edificación está en la hoja METRADO del metrado de señalización y '
          'seguridad.' % (q['ATENCIÓN RIESGO'], q['PUNTO ECOL']))
    figura(M, os.path.join(FIG, 'planta_general.png'), 'Planta general de señalización (lámina %s)' % LS, 13.0,
           'Fuente: Lámina %s del expediente de arquitectura.' % LS)
    from PIL import Image
    for cod, nombre in eds:
        ruta = os.path.join(FIG, 'planta_%s.png' % cod)
        if cod == 'EXT' or not os.path.exists(ruta):
            continue
        w, h = Image.open(ruta).size
        figura(M, ruta, 'Señalización de %s %s' % (cod, nombre.lower() if not nombre.startswith('SUM') else nombre), min(W, 19.0 * w / h),
               'Fuente: Lámina %s del expediente de arquitectura.' % LS)

    # ================================================================== 11 MANTENIMIENTO
    M.t1('MANTENIMIENTO, INSPECCIÓN Y SIMULACROS')
    tabla(M, 'Programa de inspección y mantenimiento', ['ELEMENTO', 'ACTIVIDAD', 'FRECUENCIA', 'RESPONSABLE'], [
        ['Extintores', 'Inspección visual (presión, precinto, acceso, tarjeta)', 'Mensual', 'Mantenimiento y seguridad'],
        ['Extintores', 'Mantenimiento y recarga por empresa certificada', 'Anual o después de cada uso', 'Dirección'],
        ['Luces de emergencia', 'Prueba de encendido y autonomía', 'Mensual / semestral (90 min)', 'Mantenimiento'],
        ['Detectores de humo', 'Prueba funcional y limpieza', 'Trimestral', 'Mantenimiento'],
        ['Señales de seguridad', 'Verificación de estado, fijación y fotoluminiscencia', 'Semestral', 'Comité de Seguridad'],
        ['Botiquín del tópico', 'Reposición de insumos y control de vencimientos', 'Mensual', 'Brigada de primeros auxilios'],
        ['Instalación de gas de la cocina', 'Revisión de mangueras, reguladores y válvulas', 'Mensual', 'Mantenimiento'],
        ['Simulacros de evacuación', 'Simulacro diurno y nocturno con registro de tiempos', 'Semestral', 'Comité de Seguridad']],
        [3.6, W - 10.6, 3.6, 3.4], tam=8.5, izq=(0, 1, 2, 3))

    # ================================================================== 12 CONCLUSIONES
    M.t1('CONCLUSIONES Y RECOMENDACIONES')
    n_sen = sum(p['total'] for p in pts if p['und'] and p['item'][:2] in ('01', '02', '03', '04'))
    vines(M, ['Todas las edificaciones del hogar son de un nivel y evacúan en forma horizontal y directa al exterior, por %d salidas '
              'señalizadas, con %d señales de dirección de evacuación.' % (q['SALIDA CON'], q['DIRECCIÓN DE EVACUACIÓN']),
              'Las %d rutas de evacuación de la lámina %s miden como máximo %.2f m, por debajo de los %.0f m de la Norma A.130, y terminan '
              'en %d zonas de evacuación exteriores.' % (len(D.rutas()), D.LAMINA_E[0], max(r['L'] for r in D.rutas()), D.D_MAX, len(D.zonas())),
              'La capacidad máxima simultánea del hogar es de %d personas (%d residentes, %d de personal y %d temporales).' % (
                  Pb['maxima'], Pb['residentes'], Pb['personal'], Pb['temporales']),
              'El proyecto cuenta con %d señales de seguridad, %d extintores PQS de 9 kg, %d detectores de humo y %d unidades de luces de '
              'emergencia, distribuidos según la lámina %s.' % (n_sen, ext['total'], q['DETECTOR DE HUMO'], q['UNIDAD DE LUCES'], LS),
              'Se recomienda conformar el Comité de Seguridad y las brigadas desde el inicio del funcionamiento, con personal capacitado '
              'en todos los turnos, y realizar simulacros semestrales, uno de ellos nocturno.',
              'Se recomienda mantener la señalización, los equipos y las rutas conforme a las láminas aprobadas, condición para la '
              'Inspección Técnica de Seguridad en Edificaciones.'])

    # ================================================================== 13 LÁMINAS
    M.t1('LÁMINAS Y DOCUMENTOS')
    tabla(M, 'Láminas de evacuación y señalización', ['LÁMINA', 'DESCRIPCIÓN', 'ESCALA'], [[a, b, c] for a, b, c in D.LAMINAS],
          [3.0, W - 5.4, 2.4], izq=(1,))
    M.par('Forman parte de la especialidad, con las mismas cantidades y características: el metrado de evacuación y señalización '
          '(Excel) y las especificaciones técnicas de evacuación y señalización (Word).')
    M.d.core_properties.author = ''; M.d.core_properties.title = 'Memoria descriptiva - Evacuación y señalización - Hogar de Refugio Temporal'
    M.d.save(SALIDA)
    return SALIDA


if __name__ == '__main__':
    print(generar())
