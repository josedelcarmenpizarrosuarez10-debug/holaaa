# -*- coding: utf-8 -*-
"""Análisis de incompatibilidades de ubicación - Hogar de Refugio Temporal para mujeres víctimas de violencia (CUI 2675514).

Base: el cuadro de incompatibilidades de la arquitecta (insumos/solange/sustento_normativo/ANALISIS_INCOMPATIBILIDADES_UBICACION_BORRADOR.docx,
18 incompatibilidades del cuadro de la Norma Técnica "Criterios Generales de Diseño para Infraestructura Educativa",
R.V.M. N.° 010-2022-MINEDU), con su resultado de campo (CUMPLE en las 18). Se conserva cada resultado y se ordena el documento:
marco normativo del proyecto (A.090 art. 3, A.040 art. 7 b), método (área de influencia medida desde el lindero), cuadro con la
distancia o el criterio de cada dispositivo, usos colindantes y conclusiones. Arreglos de forma: "I.E." y "UP" pasan a "predio
del Hogar de Refugio"; Decreto Ley N.° 25844 (Ley de Concesiones Eléctricas); Ley Orgánica de Municipalidades; aeródromo con la
distancia al aeropuerto de Tarapoto.
Lo que la arquitecta debe confirmar va en una nota interna aparte (no forma parte del expediente).

Uso: python3 herramientas/incompatibilidades_refugio.py
Salida: entregables/ANALISIS_INCOMPATIBILIDADES_UBICACION_HOGAR_REFUGIO.docx (expediente)
        entregables/MATRIZ_INCOMPATIBILIDADES_UBICACION_HOGAR_REFUGIO.xlsx (expediente)
        entregables/revision_interna/INCOMPATIBILIDADES_CORREGIDO_Y_POR_REVISAR_HOGAR_REFUGIO.docx (uso interno)
"""
import os
import subprocess
import sys
import tempfile

import openpyxl
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
for d in (AQUI, os.path.join(AQUI, 'varones')):
    sys.path.insert(0, d)
import sustento_normativo_refugio as SN  # noqa: E402  (encabezado, pie, viñetas con etiqueta, carátula configurada)
R, V = SN.R, SN.V

SALIDA = os.path.join(RAIZ, 'entregables/ANALISIS_INCOMPATIBILIDADES_UBICACION_HOGAR_REFUGIO.docx')
SALIDA_X = os.path.join(RAIZ, 'entregables/MATRIZ_INCOMPATIBILIDADES_UBICACION_HOGAR_REFUGIO.xlsx')
SALIDA_N = os.path.join(RAIZ, 'entregables/revision_interna/INCOMPATIBILIDADES_CORREGIDO_Y_POR_REVISAR_HOGAR_REFUGIO.docx')
CUI = R.CUI
RVM = 'R.V.M. N.° 010-2022-MINEDU'
# nombres del servicio en la matriz Excel (el CAR Varones los cambia en varones/incompatibilidades_v.py)
SERV, SERV_CORTO, HOJA2, RES2 = 'HOGAR DE REFUGIO TEMPORAL', 'HOGAR DE REFUGIO', 'CONDICIONES HOGAR', 'condiciones propias del hogar'

# Aeropuerto de Tarapoto: distancia desde la ubicación UTM referencial del predio (E 345 749, N 9 282 885, WGS84 18S)
AERO_KM, AERO_OESTE_KM = 3.5, 2.4

# (incompatibilidad, dispositivo legal, distancia mínima en m o None, criterio, condición encontrada)
CUADRO = [
    ('Velatorios y cementerios', 'D.S. N.° 003-94-SA, Reglamento de la Ley de Cementerios y Servicios Funerarios', 150, '',
     'No existen velatorios ni cementerios a menos de 150 m del predio.'),
    ('Establecimientos de salud', 'R.M. N.° 045-2015/MINSA, NTS N.° 113-MINSA/DGIEM-V.01 "Infraestructura y equipamiento de los '
     'establecimientos de salud del Primer Nivel de Atención", y R.M. N.° 862-2015/MINSA, NTS N.° 119-MINSA/DGIEM-V.01 '
     '"Infraestructura y equipamiento de los establecimientos de salud del Tercer Nivel de Atención"', 100, '',
     'El establecimiento de salud de la localidad se encuentra a más de 100 m del predio y forma parte de los servicios de apoyo '
     'cercanos que requiere el hogar.'),
    ('Plantas envasadoras de gas licuado de petróleo (GLP)', 'D.S. N.° 027-94-EM, Reglamento de Seguridad para Instalaciones y '
     'Transporte de Gas Licuado de Petróleo', 100, '', 'No existen plantas envasadoras de GLP en el entorno del predio.'),
    ('Estaciones de servicio, puestos de venta de combustibles (grifos), gasocentros y establecimientos de venta al público de GNV',
     'D.S. N.° 054-93-EM (modificado por el D.S. N.° 037-2007-EM), Reglamento de Seguridad para Establecimientos de Venta al '
     'Público de Combustibles Derivados de Hidrocarburos', 50, '',
     'No existen estaciones de servicio, grifos ni gasocentros a menos de 50 m del predio.'),
    ('Locales de comercialización y consumo de bebidas alcohólicas', 'Ley N.° 28681, Ley que regula la comercialización, consumo y '
     'publicidad de bebidas alcohólicas, y su Reglamento (D.S. N.° 012-2009-SA)', 100, '',
     'No existen locales de venta y consumo de bebidas alcohólicas a menos de 100 m del predio, lo que favorece la tranquilidad y '
     'la seguridad de las residentes.'),
    ('Plantas de abastecimiento de combustibles líquidos y otros productos derivados de los hidrocarburos', 'D.S. N.° 045-2001-EM, '
     'Reglamento para la Comercialización de Combustibles Líquidos y otros Productos Derivados de los Hidrocarburos', 100, '',
     'No existen plantas de abastecimiento de combustibles ni de derivados de hidrocarburos.'),
    ('Fajas marginales de las fuentes de agua, naturales o artificiales', 'D.S. N.° 001-2010-AG, Reglamento de la Ley N.° 29338, '
     'Ley de Recursos Hídricos', None, 'Faja marginal de cada fuente de agua',
     'No existen fuentes de agua naturales ni artificiales colindantes; el predio no ocupa fajas marginales.'),
    ('Sistema de transporte de hidrocarburos por ductos', 'D.S. N.° 081-2007-EM (modificado por el D.S. N.° 007-2012-EM), '
     'Reglamento de Transporte de Hidrocarburos por Ductos', 200, '', 'No existe sistema de transporte de hidrocarburos por ductos.'),
    ('Pozos para la exploración y explotación de hidrocarburos', 'D.S. N.° 032-2004-EM, Reglamento de las Actividades de '
     'Exploración y Explotación de Hidrocarburos', None, 'Área de las instalaciones de exploración y explotación',
     'No existen actividades de exploración ni de explotación de hidrocarburos.'),
    ('Aeródromos', 'D.S. N.° 050-2001-MTC, Reglamento de la Ley de Aeronáutica Civil, y sus modificatorias', None,
     'Superficies limitadoras de obstáculos',
     'El aeropuerto de Tarapoto está a unos %.1f km, al costado del eje de la pista 17/35 (unos %.1f km al oeste), fuera de las '
     'superficies de aproximación y despegue; las edificaciones del hogar son de baja altura.' % (AERO_KM, AERO_OESTE_KM)),
    ('Servidumbre de líneas aéreas de instalaciones eléctricas', 'R.M. N.° 214-2011-MEM/DM, Código Nacional de Electricidad '
     '(Suministro 2011)', None, 'Faja de servidumbre según la tensión de la línea',
     'No existen líneas aéreas cuya faja de servidumbre ocupe el predio.'),
    ('Servidumbre de electroductos', 'Decreto Ley N.° 25844, Ley de Concesiones Eléctricas, y sus modificatorias', None,
     'Servidumbre impuesta sobre el predio', 'No existen electroductos ni servidumbres eléctricas impuestas sobre el predio.'),
    ('Restricciones radioeléctricas en áreas de uso público próximas a una estación radioeléctrica', 'R.M. N.° 120-2005-MTC/03, '
     'Norma Técnica sobre Restricciones Radioeléctricas en Áreas de Uso Público', None, 'Límites de exposición de la norma',
     'No existen estaciones radioeléctricas que afecten el predio; se cumple la R.M. N.° 120-2005-MTC/03.'),
    ('Plantas de tratamiento de aguas residuales', 'D.S. N.° 011-2006-VIVIENDA, Norma OS.090 "Plantas de tratamiento de aguas '
     'residuales" del RNE', None, 'Distancia de la planta a la zona habitada',
     'No existen plantas de tratamiento de aguas residuales de terceros en el entorno del predio.'),
    ('Faja de terreno lateral y colindante al derecho de vía', 'D.S. N.° 034-2008-MTC, Reglamento Nacional de Gestión de '
     'Infraestructura Vial', None, 'Derecho de vía y faja de propiedad restringida',
     'El predio no está en área restringida; el cerco y las obras, incluido el colector pluvial frontal, quedan dentro del lindero, '
     'sin ocupar la faja de la carretera Oasis.'),
    ('Zonas restringidas colindantes a las vías ferroviarias', 'D.S. N.° 032-2005-MTC, Reglamento Nacional de Ferrocarriles', None,
     'Zona restringida de la vía férrea', 'No existe vía ferroviaria en la zona.'),
    ('Casinos y máquinas tragamonedas', 'Ley N.° 27153, Ley que regula la explotación de los juegos de casino y máquinas '
     'tragamonedas, y sus modificatorias', None, 'Distancia de la ley y de la ordenanza municipal',
     'No existen casinos ni salas de máquinas tragamonedas en el entorno del predio.'),
    ('Hostales, peñas, discotecas, video-pubs, bingos y salas de billar', 'Ley N.° 27972, Ley Orgánica de Municipalidades, art. 79 '
     '(organización del espacio físico y uso del suelo)', None, 'Zonificación y licencias municipales',
     'No existen hostales, peñas, discotecas, video-pubs, bingos ni salas de billar en el entorno del predio; el entorno es '
     'tranquilo, como lo requiere un hogar de refugio.'),
]

NORMAS = [
    ('Ley N.° 30364 y su Reglamento (D.S. N.° 009-2016-MIMP y modificatorias)', 'Marco del servicio de Hogares de Refugio '
     'Temporal: protección, albergue y atención de mujeres víctimas de violencia y de sus hijas e hijos.'),
    ('R.M. N.° 150-2016-MIMP', 'Lineamientos para la atención y funcionamiento de los Hogares de Refugio Temporal.'),
    ('RNE, Norma A.090 Servicios Comunales, art. 3', 'Las edificaciones de servicios comunales se ubicarán en los lugares señalados '
     'en los Planes de Desarrollo Urbano, o en zonas compatibles con la zonificación vigente.'),
    ('RNE, Norma A.090, art. 4', 'Los proyectos que supongan una concentración de público de más de 500 personas deberán contar con '
     'un estudio de impacto vial.'),
    ('RNE, Norma A.040 Educación (R.M. N.° 068-2020-VIVIENDA), art. 7 b)', 'Ubicación evitando las incompatibilidades de uso '
     'establecidas en la normativa vigente y/o adoptar las alternativas de solución, respecto de su ubicación. Se aplica a los '
     'ambientes educativos del hogar (módulo infantil y módulo de enseñanza).'),
    ('%s, Norma Técnica "Criterios Generales de Diseño para Infraestructura Educativa"' % RVM, 'Cuadro de incompatibilidades de uso '
     'del terreno, que reúne los dispositivos legales sectoriales y sus distancias; se adopta como lista de verificación.'),
    ('R.V.M. N.° 208-2019-MINEDU, art. 8 c)', 'Para la adecuada selección del terreno se deben tomar en cuenta las condiciones del '
     'terreno, así como su disponibilidad, establecidas en la N.T. Criterios Generales.'),
    ('Lineamientos ONU-Habitat / CONAVIM (2016), numeral 2.1', 'Ubicación en una zona tranquila, no aislada, con servicios e '
     'instituciones de apoyo cercanos, alumbrado público, transporte público y accesos alternativos; numerales 2.2 a 2.8: '
     'recinto cercado, reserva del uso, seguridad, accesos y servicios básicos.'),
]

# Condiciones de ubicación propias de un Hogar de Refugio Temporal: (condición, fuente, cómo la cumple el predio o el proyecto)
CONDICIONES = [
    ('Ubicación en zona compatible con la zonificación vigente', 'RNE A.090, art. 3',
     'Predio rural Los Mangos, de propiedad del Gobierno Regional, destinado a servicios de protección social del Estado junto con el '
     'CAR Varones y el CAR Mujeres.'),
    ('Zona tranquila y no aislada', 'Lineamientos ONU-Habitat / CONAVIM, num. 2.1',
     'Entorno urbano de Morales y Tarapoto, con frente a la carretera Oasis y colindante con otros servicios de protección; sin bares, '
     'discotecas ni casinos en el entorno (Cuadro N.° 1, filas 5, 17 y 18).'),
    ('Servicios e instituciones de apoyo cercanos (salud, seguridad y justicia)', 'Lineamientos, num. 2.1',
     'Servicios de salud, seguridad y justicia del distrito de Morales y de la ciudad de Tarapoto en el entorno urbano; el '
     'establecimiento de salud de la localidad está a más de 100 m (Cuadro N.° 1, fila 2).'),
    ('Accesos vehicular y peatonal, sin estudio de impacto vial', 'Lineamientos, num. 2.1 y 2.6; RNE A.090, art. 4',
     'Acceso por la carretera Oasis, con ingreso principal y de servicio controlados. La población del hogar es menor de 500 personas, '
     'por lo que la A.090 (art. 4) no exige estudio de impacto vial.'),
    ('Seguridad frente a agresiones externas', 'Lineamientos, num. 2.4',
     'Recinto con cerco perimétrico, caseta de control en los accesos y cuarto de cámaras del circuito cerrado de vigilancia.'),
    ('Reserva del uso y privacidad de las residentes', 'Lineamientos, num. 2.2 y 2.3',
     'Conjunto de edificaciones dentro de un recinto cercado, sin anuncios que revelen el uso; los predios colindantes son servicios '
     'del Estado de acceso restringido.'),
    ('Servicios básicos', 'Lineamientos, num. 2.8; RNE A.040, art. 7 d)',
     'El proyecto contempla cisterna y tanque elevado, tratamiento de aguas residuales, subestación eléctrica, grupo electrógeno y '
     'drenaje pluvial.'),
    ('Protección frente a lluvias intensas', 'RNE OS.060 (drenaje pluvial urbano)',
     'Drenaje pluvial del predio con colector frontal y cunetas, dimensionado con la hidrología del expediente; las obras quedan dentro '
     'del lindero.'),
]

COLINDANTES = [
    ('Frente', 'Carretera Oasis', 'Vía de acceso al predio; el cerco y el colector pluvial frontal quedan dentro del lindero.'),
    ('Lateral (aguas arriba)', 'CAR Varones (CUI 2705619)', 'Servicio de protección a niñas, niños y adolescentes; uso compatible.'),
    ('Lateral (aguas abajo)', 'CAR Mujeres (CUI 2717013)', 'Servicio de protección a niñas, niños y adolescentes; uso compatible.'),
]


def seccion(M, apaisada):
    """Nueva sección (horizontal o vertical) que sigue la numeración y el encabezado de la anterior."""
    ant = M.d.sections[-1]
    sec = M.d.add_section(WD_SECTION.NEW_PAGE)
    for pg in sec._sectPr.findall(qn('w:pgNumType')):
        sec._sectPr.remove(pg)
    cor, lar = sorted((ant.page_width, ant.page_height))
    sec.orientation = WD_ORIENT.LANDSCAPE if apaisada else WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = (lar, cor) if apaisada else (cor, lar)
    if apaisada:
        sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(2.0), Cm(2.5), Cm(2.0)
    else:
        sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(3.0), Cm(2.0), Cm(2.5), Cm(2.0)
    M.ancho = (sec.page_width - sec.left_margin - sec.right_margin) / 360000.0


def dist(x):
    return 'No menor de %d m' % x[2] if x[2] else x[3]


# --------------------------------------------------------------------------------------------------------------- Word (expediente)
def generar_docx():
    M = R.Memoria()
    V.C.SERVICIO = 'EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:'; V.FECHA = 'OCTUBRE - 2026'
    foto = V.foto(); V.escudo()
    V.caratula(M.d, foto, 'INCOMPATIBILIDADES', 'DE UBICACIÓN DEL PROYECTO - ESPECIALIDAD: ARQUITECTURA')
    SN.encabezado(M, 'INCOMPATIBILIDADES DE UBICACIÓN - ARQUITECTURA')
    W = M.ancho

    M.t1('GENERALIDADES')
    M.t2('Objeto')
    M.par('El presente análisis verifica que el terreno del proyecto “%s”, con CUI N.° %s, es apto para un Hogar de Refugio Temporal: '
          'que no presenta incompatibilidades de uso por cercanía a actividades, instalaciones o servidumbres reguladas por la normativa '
          'vigente, y que reúne las condiciones de ubicación que requiere este servicio de protección.' % (R.CR_PROY, CUI))
    M.t2('El servicio y sus exigencias de ubicación')
    M.par('El Hogar de Refugio Temporal brinda protección, albergue, alimentación y atención multidisciplinaria a mujeres víctimas de '
          'violencia en situación de riesgo de feminicidio, y a sus hijas e hijos, en el marco de la Ley N.° 30364 y su Reglamento. Por '
          'la naturaleza del servicio, su ubicación debe garantizar la seguridad de las residentes, la reserva del uso, un entorno '
          'tranquilo y no aislado, y la cercanía a los servicios de salud, seguridad y justicia. Al residir en él niñas y niños, debe '
          'además evitar las actividades e instalaciones que la normativa sectorial considera incompatibles con su permanencia.')
    M.t2('Ubicación del predio')
    M.par(R.UBIC + ', con frente a la carretera Oasis y en el entorno urbano de Morales y Tarapoto. Coordenadas UTM referenciales '
          '(WGS84, zona 18 Sur): E 345 749, N 9 282 885.')
    M.tabla('Usos colindantes del predio', ['LADO', 'COLINDANTE', 'USO Y COMPATIBILIDAD'], [list(c) for c in COLINDANTES],
            [3.2, 4.4, W - 7.6], tam=8.5, izq=(0, 1, 2))
    M.par('El predio forma parte de un conjunto de servicios de protección del Estado (CAR Varones, Hogar de Refugio Temporal y CAR '
          'Mujeres), usos de la misma naturaleza y compatibles entre sí.')

    M.t1('MARCO NORMATIVO')
    M.par('La ubicación del Hogar de Refugio Temporal se verifica con las normas asignadas al proyecto:')
    M.tabla('Normas que rigen la ubicación del proyecto', ['NORMA', 'DISPOSICIÓN'], [list(n) for n in NORMAS], [5.6, W - 5.6], tam=8.5,
            izq=(0, 1))
    M.par('No existe una relación de incompatibilidades de uso propia de los hogares de refugio. Por ello se toma la relación de '
          'dispositivos legales sectoriales que reúne la N.T. Criterios Generales de Diseño (%s), a la que remiten la Norma A.040 y la '
          'R.V.M. N.° 208-2019-MINEDU para los locales con permanencia de niñas y niños, y se complementa con las condiciones de '
          'ubicación que los lineamientos para refugios establecen para este servicio.' % RVM)

    M.t1('METODOLOGÍA')
    for t in ('Incompatibilidades por cercanía (Cuadro N.° 1): se define el área de influencia del predio como la franja medida desde '
              'el lindero con la distancia que fija cada dispositivo legal: 50 m (estaciones de servicio), 100 m (establecimientos de '
              'salud, GLP, bebidas alcohólicas y plantas de combustibles), 150 m (velatorios y cementerios) y 200 m (ductos de '
              'hidrocarburos). Para las que no tienen distancia fija (fajas marginales, servidumbres eléctricas, aeródromos, vías, '
              'restricciones radioeléctricas y usos regulados por la municipalidad) se verifica que la restricción no alcance al predio.',
              'Condiciones propias del hogar (Cuadro N.° 2): se verifica cada condición de ubicación de los lineamientos y del RNE con las '
              'características del predio y del programa arquitectónico.',
              'Se reconoce el entorno del predio y se revisa la cartografía y las imágenes satelitales de la zona.',
              'Cada punto se califica como CUMPLE cuando la actividad o restricción no existe dentro del área de influencia, o cuando el '
              'predio y el proyecto satisfacen la condición.'):
        M.vin(t)

    seccion(M, apaisada=True); W2 = M.ancho                        # cuadros en hoja horizontal
    M.t1('INCOMPATIBILIDADES DE UBICACIÓN POR CERCANÍA')
    filas = [[str(k), x[0], x[1], dist(x), x[4], 'CUMPLE'] for k, x in enumerate(CUADRO, 1)]
    M.tabla('Cuadro N.° 1: incompatibilidades de uso del terreno por cercanía - Hogar de Refugio Temporal (relación de la %s)' % RVM,
            ['N.°', 'INCOMPATIBILIDAD POR CERCANÍA', 'DISPOSITIVO LEGAL', 'DISTANCIA O CRITERIO', 'CONDICIÓN DEL PREDIO', 'ESTADO'],
            filas, [0.9, 5.0, 7.6, 3.0, W2 - 18.2, 1.7], tam=8, izq=(1, 2, 3, 4))
    for fila in M.d.tables[-1].rows:
        fila._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    M.t1('CONDICIONES DE UBICACIÓN PROPIAS DEL HOGAR DE REFUGIO')
    filas = [[str(k), c[0], c[1], c[2], 'CUMPLE'] for k, c in enumerate(CONDICIONES, 1)]
    M.tabla('Cuadro N.° 2: condiciones de ubicación del Hogar de Refugio Temporal (lineamientos para refugios y RNE)',
            ['N.°', 'CONDICIÓN DE UBICACIÓN', 'FUENTE', 'CÓMO LA CUMPLE EL PREDIO O EL PROYECTO', 'ESTADO'],
            filas, [0.9, 5.4, 4.6, W2 - 12.6, 1.7], tam=8, izq=(1, 2, 3))
    for fila in M.d.tables[-1].rows:
        fila._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    seccion(M, apaisada=False)

    M.t1('CONCLUSIONES')
    for t in ('El predio cumple las %d condiciones del Cuadro N.° 1: no existen dentro de su área de influencia las actividades, '
              'instalaciones ni servidumbres que la normativa sectorial considera incompatibles con la permanencia de mujeres, niñas '
              'y niños.' % len(CUADRO),
              'El predio y el proyecto cumplen las %d condiciones de ubicación propias del Hogar de Refugio Temporal (Cuadro N.° 2): '
              'zona compatible, tranquila y no aislada, con servicios de apoyo cercanos, accesos controlados, seguridad perimetral, '
              'reserva del uso, servicios básicos y drenaje pluvial.' % len(CONDICIONES),
              'La ubicación cumple la Norma A.090 (arts. 3 y 4) y la Norma A.040 (art. 7 b): el hogar se emplaza en una zona compatible, '
              'sin incompatibilidades de uso y sin necesidad de estudio de impacto vial.',
              'Los colindantes (CAR Varones y CAR Mujeres) son servicios de protección de la misma naturaleza, y la carretera Oasis da '
              'acceso al predio sin que las obras ocupen su faja.',
              'Por lo expuesto, el terreno es apto para el Hogar de Refugio Temporal para mujeres víctimas de violencia.'):
        M.vin(t)
    M.d.core_properties.author = ''
    M.d.core_properties.title = 'Análisis de incompatibilidades de ubicación - Hogar de Refugio Temporal'
    M.d.save(SALIDA)
    return SALIDA


# --------------------------------------------------------------------------------------------------------------- Excel (expediente)
def generar_xlsx():
    wb = openpyxl.Workbook()
    G = R.GRANATE; th = Side(style='thin', color='999999'); B = Border(left=th, right=th, top=th, bottom=th)
    cab_f = PatternFill('solid', fgColor=G); cab_t = Font(bold=True, color='FFFFFF', name='Arial', size=9)
    nf = Font(name='Arial', size=9); bf = Font(name='Arial', size=9, bold=True)
    al = Alignment(wrap_text=True, vertical='center'); ac = Alignment(wrap_text=True, vertical='center', horizontal='center')

    def cab(ws, fila, textos, anchos):
        for j, (t, w) in enumerate(zip(textos, anchos), 1):
            c = ws.cell(fila, j, t); c.fill = cab_f; c.font = cab_t; c.alignment = ac; c.border = B
            ws.column_dimensions[get_column_letter(j)].width = w
        ws.row_dimensions[fila].height = 32

    def titulo(ws, t):
        ws['A1'] = t; ws['A1'].font = Font(name='Arial', size=12, bold=True, color=G)
        ws['A2'] = 'Proyecto: “%s”, CUI N.° %s' % (R.CR_PROY, CUI); ws['A2'].font = nf

    ws = wb.active; ws.title = 'MATRIZ'
    titulo(ws, 'MATRIZ DE INCOMPATIBILIDADES DE UBICACIÓN (CUADRO DE LA %s)' % RVM)
    cab(ws, 4, ['N.°', 'INCOMPATIBILIDAD POR CERCANÍA', 'DISPOSITIVO LEGAL', 'DISTANCIA MÍNIMA (m)', 'CRITERIO (SIN DISTANCIA FIJA)',
                '¿EXISTE DENTRO DEL ÁREA DE INFLUENCIA?', 'CONDICIÓN DEL PREDIO', 'ESTADO'], [5, 32, 48, 11, 24, 14, 50, 11])
    r0 = 5
    for k, x in enumerate(CUADRO):
        r = r0 + k
        for j, v in enumerate([k + 1, x[0], x[1], x[2], x[3] or None, 'NO', x[4]], 1):
            c = ws.cell(r, j, v); c.font = nf; c.border = B; c.alignment = ac if j in (1, 4, 6) else al
        c = ws.cell(r, 8, '=IF(F%d="NO","CUMPLE","NO CUMPLE")' % r); c.font = bf; c.border = B; c.alignment = ac
    r1 = r0 + len(CUADRO) - 1
    ws.freeze_panes = 'C5'

    w2 = wb.create_sheet('AREA DE INFLUENCIA')
    titulo(w2, 'ÁREA DE INFLUENCIA MEDIDA DESDE EL LINDERO')
    cab(w2, 4, ['DISTANCIA (m)', 'N.° DE INCOMPATIBILIDADES', 'INCOMPATIBILIDADES'], [14, 16, 90])
    radios = sorted({x[2] for x in CUADRO if x[2]})
    for i, d in enumerate(radios):
        r = 5 + i
        w2.cell(r, 1, d); w2.cell(r, 2, '=COUNTIF(MATRIZ!D%d:D%d,A%d)' % (r0, r1, r))
        w2.cell(r, 3, '; '.join(x[0] for x in CUADRO if x[2] == d))
        for j in (1, 2, 3):
            w2.cell(r, j).font = nf; w2.cell(r, j).border = B; w2.cell(r, j).alignment = ac if j < 3 else al
    r = 5 + len(radios)
    w2.cell(r, 1, 'Sin distancia fija'); w2.cell(r, 2, '=COUNTBLANK(MATRIZ!D%d:D%d)' % (r0, r1))
    w2.cell(r, 3, '; '.join(x[0] for x in CUADRO if not x[2]))
    for j in (1, 2, 3):
        w2.cell(r, j).font = nf; w2.cell(r, j).border = B; w2.cell(r, j).alignment = ac if j < 3 else al

    w4 = wb.create_sheet(HOJA2)
    titulo(w4, 'CONDICIONES DE UBICACIÓN PROPIAS DEL ' + SERV)
    cab(w4, 4, ['N.°', 'CONDICIÓN DE UBICACIÓN', 'FUENTE', '¿EL PREDIO O EL PROYECTO LA SATISFACE?', 'CÓMO LA CUMPLE', 'ESTADO'],
        [5, 40, 30, 14, 70, 11])
    q0 = 5
    for k, c_ in enumerate(CONDICIONES):
        r = q0 + k
        for j, v in enumerate([k + 1, c_[0], c_[1], 'SÍ', c_[2]], 1):
            c = w4.cell(r, j, v); c.font = nf; c.border = B; c.alignment = ac if j in (1, 4) else al
        c = w4.cell(r, 6, '=IF(D%d="SÍ","CUMPLE","NO CUMPLE")' % r); c.font = bf; c.border = B; c.alignment = ac
    q1 = q0 + len(CONDICIONES) - 1

    w3 = wb.create_sheet('RESUMEN')
    titulo(w3, 'RESUMEN DEL ANÁLISIS DE UBICACIÓN')
    cab(w3, 4, ['CONCEPTO', 'EVALUADOS', 'CUMPLE', 'NO CUMPLE'], [58, 12, 12, 12])
    for i, (t, h, a, b, col) in enumerate((('Cuadro N.° 1: incompatibilidades por cercanía', 'MATRIZ', r0, r1, 'H'),
                                           ('Cuadro N.° 2: ' + RES2, "'%s'" % HOJA2, q0, q1, 'F'))):
        r = 5 + i
        w3.cell(r, 1, t).font = nf
        w3.cell(r, 2, '=COUNTA(%s!B%d:B%d)' % (h, a, b)); w3.cell(r, 3, '=COUNTIF(%s!%s%d:%s%d,"CUMPLE")' % (h, col, a, col, b))
        w3.cell(r, 4, '=COUNTIF(%s!%s%d:%s%d,"NO CUMPLE")' % (h, col, a, col, b))
        for j in range(1, 5):
            w3.cell(r, j).border = B
            if j > 1:
                w3.cell(r, j).font = bf; w3.cell(r, j).alignment = ac
    w3.cell(8, 1, 'RESULTADO').font = bf
    c = w3.cell(8, 2, '=IF(SUM(D5:D6)=0,"TERRENO APTO PARA EL %s","REVISAR")' % SERV_CORTO); c.font = bf
    w3.merge_cells('B8:D8'); w3.cell(8, 1).border = B; c.border = B
    wb.properties.creator = ''; wb.properties.title = 'Matriz de incompatibilidades de ubicación - ' + SERV.capitalize()
    wb.save(SALIDA_X)
    with tempfile.TemporaryDirectory() as tmp:                     # recalcular las fórmulas con LibreOffice
        subprocess.run(['soffice', '--headless', '--convert-to', 'xlsx', '--outdir', tmp, SALIDA_X],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        out = os.path.join(tmp, os.path.basename(SALIDA_X))
        if os.path.exists(out):
            os.replace(out, SALIDA_X)
    return SALIDA_X


# --------------------------------------------------------------------------------------------- nota interna para la arquitecta
def generar_interno():
    import docx
    from docx.shared import Pt
    d = docx.Document(); s = d.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = d.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    M = R.Memoria(); M.d = d
    if d.paragraphs:
        d.paragraphs[0]._p.getparent().remove(d.paragraphs[0]._p)
    W = (s.page_width - s.left_margin - s.right_margin) / 360000.0; M.ancho = W
    M.par('INCOMPATIBILIDADES DE UBICACIÓN: CORREGIDO Y PUNTOS PARA CONFIRMAR', 12.5, True, color=R.GRANATE, centro=True, despues=2)
    M.par('Hogar de Refugio Temporal - CUI N.° %s  |  Documento de trabajo, no forma parte del expediente' % CUI, 9, color=R.GRIS,
          centro=True, despues=10)
    M.par('El borrador era el cuadro de incompatibilidades de un local educativo. El análisis se rehízo para el Hogar de Refugio: '
          'las 18 incompatibilidades por cercanía quedan en CUMPLE, como en el borrador, y se agregó un segundo cuadro con las '
          'condiciones de ubicación propias de un hogar de refugio. Este documento indica lo ajustado y lo que conviene confirmar.')

    def sec(t):
        M.par(t, 11, True, color=R.GRANATE, antes=8, despues=4)

    sec('1. YA AJUSTADO EN EL ANÁLISIS')
    M.tabla('Ajustes de redacción y citas', ['N.°', 'EN EL BORRADOR', 'EN EL ANÁLISIS'], [
        ['2, 4, 5, 10, 13, 14, 15, 17, 18', '"I.E.", "UP" y "área definida para la UP" (texto de un proyecto educativo)',
         '"predio" y "entorno del predio" del Hogar de Refugio'],
        ['12', 'Decreto Ley N.° 25884', 'Decreto Ley N.° 25844, Ley de Concesiones Eléctricas'],
        ['18', 'Ley Orgánica de Municipales', 'Ley N.° 27972, Ley Orgánica de Municipalidades'],
        ['13', '"cuando una Institución Educativa se encuentre próximo"', 'restricciones en áreas de uso público próximas a una estación'],
        ['10', 'No se encontró dentro del área definida', 'Aeropuerto de Tarapoto a unos %.1f km, al costado de la pista 17/35; '
         'edificaciones de baja altura (sigue CUMPLE)' % AERO_KM],
        ['15', 'El área no se encuentra en área restringida', 'Se agrega que el cerco y el colector pluvial frontal quedan dentro del '
         'lindero, sin ocupar la faja de la carretera Oasis'],
        ['Todos', 'Distancia dentro del texto del dispositivo', 'Columna aparte "DISTANCIA O CRITERIO"'],
    ], [2.6, 6.0, W - 8.6], tam=8.5, izq=(1, 2))
    M.par('Se añadieron: la descripción del servicio y sus exigencias de ubicación; el marco normativo del proyecto (Ley N.° 30364 y '
          'su Reglamento, R.M. N.° 150-2016-MIMP, A.090 arts. 3 y 4, A.040 art. 7 b, R.V.M. N.° 208-2019 art. 8 c y lineamientos para '
          'refugios); el Cuadro N.° 2 con %d condiciones propias del hogar (zona compatible, tranquila y no aislada, servicios de '
          'apoyo, accesos, seguridad, reserva del uso, servicios básicos y drenaje); los usos colindantes y las conclusiones.'
          % len(CONDICIONES), despues=4)

    sec('2. PARA CONFIRMAR')
    M.tabla('Puntos para confirmar', ['TEMA', 'QUÉ CONFIRMAR', 'POR QUÉ'], [
        ['Versión de la norma MINEDU', 'Si el proyecto debe citar la R.V.M. N.° 010-2022-MINEDU (con su modificatoria R.V.M. N.° '
         '020-2023-MINEDU) o la R.V.M. N.° 068-2025-MINEDU del 27-06-2025, que aprueba una norma técnica con el mismo nombre.',
         'Un evaluador puede observar la cita de una norma reemplazada; si cambia, el número del cuadro se ajusta en un solo lugar.'],
        ['Aeródromo (fila 10)', 'La distancia al aeropuerto (unos %.1f km) sale de la ubicación UTM referencial; confirmar con la '
         'ubicación real y, si la entidad lo pide, con las superficies limitadoras de CORPAC.' % AERO_KM,
         'El predio queda dentro del radio de la superficie horizontal interna (4 km); con edificaciones bajas no hay restricción.'],
        ['Líneas eléctricas (filas 11 y 12)', 'Si por la carretera Oasis pasa una red de media tensión junto al frente del predio.',
         'Si existe, indicar que las edificaciones guardan la distancia de seguridad del CNE Suministro 2011.'],
        ['PTAR propia (fila 14)', 'La PTAR del programa (152 m²) es del propio hogar; confirmar su distancia a dormitorios y '
         'ambientes según el sistema de tratamiento que defina la especialidad sanitaria.',
         'El cuadro trata de plantas de terceros; un evaluador puede preguntar por la propia.'],
        ['Establecimiento de salud (fila 2)', 'Nombre y distancia del puesto o centro de salud más cercano.',
         'Dar la distancia medida refuerza el CUMPLE.'],
        ['Zonificación (Cuadro 2, fila 1)', 'Certificado de zonificación y vías o de parámetros urbanísticos de la Municipalidad '
         'Distrital de Morales que indique que el uso es compatible.', 'Es el documento que acredita la A.090 art. 3.'],
        ['Servicios de apoyo (Cuadro 2, fila 3)', 'Nombre y distancia de la comisaría, el Centro Emergencia Mujer, la fiscalía o el '
         'juzgado y el centro de salud más cercanos; paradero de transporte público y alumbrado en la carretera Oasis.',
         'El cuadro los menciona en general; con nombres y distancias el sustento es más sólido.'],
        ['Privacidad (Cuadro 2, fila 6)', 'Altura de las edificaciones colindantes (CAR Varones y CAR Mujeres) y si alguna permite '
         'ver el interior del hogar.', 'Los lineamientos piden evitar edificaciones altas desde donde se observe el interior.'],
        ['Sustento gráfico', 'Adjuntar una imagen satelital o un plano con el área de influencia de 50, 100, 150 y 200 m desde el lindero.',
         'Es el respaldo habitual del cuadro; se puede preparar en DXF sobre la planta general.'],
    ], [3.2, 7.4, W - 10.6], tam=8.5, izq=(0, 1, 2))
    d.core_properties.author = ''
    d.core_properties.title = 'Incompatibilidades de ubicación: corregido y puntos para confirmar - Hogar de Refugio'
    os.makedirs(os.path.dirname(SALIDA_N), exist_ok=True)
    d.save(SALIDA_N)
    return SALIDA_N


if __name__ == '__main__':
    print(generar_docx()); print(generar_xlsx()); print(generar_interno())
