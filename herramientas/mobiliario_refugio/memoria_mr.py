# -*- coding: utf-8 -*-
"""Memoria descriptiva de equipamiento y mobiliario - Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514), en Word.

Con los datos del plano (láminas EM-01 a EM-07, lee_plano_mr.py) y las cantidades del metrado (datos_mr.py): generalidades,
criterios de diseño del equipamiento por tipo de usuario, equipamiento de cada edificación y ambiente con su planta, características
de equipos, mobiliario e implementos por familia (fichas_mr.py), sustento de las cantidades, resumen, y suministro, instalación y
mantenimiento. Formato de las memorias del expediente (memoria_descriptiva_refugio.Memoria) y carátula del Hogar de Refugio.

Uso: python3 herramientas/mobiliario_refugio/memoria_mr.py
Salida: entregables/MEMORIA_DESCRIPTIVA_EQUIPAMIENTO_Y_MOBILIARIO_HOGAR_REFUGIO.docx
"""
import os
import sys
from collections import OrderedDict

from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml.ns import qn
from docx.shared import Cm

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI)
for d in (AQUI, os.path.join(HER, 'varones', 'senalizacion'), HER):
    sys.path.insert(0, d)
import datos_mr as D  # noqa: E402
import fichas_mr as F  # noqa: E402
import memoria_descriptiva_refugio as R  # noqa: E402
import caratulas_refugio as CR  # noqa: E402  (datos y foto del Hogar de Refugio en el motor de carátulas)
import memoria_se as MS  # noqa: E402

V = CR.V
SALIDA = os.path.join(D.SAL, 'MEMORIA_DESCRIPTIVA_EQUIPAMIENTO_Y_MOBILIARIO_HOGAR_REFUGIO.docx')
FIG = os.path.join(D.SAL, 'figuras_mobiliario')
TEXTO_ED = {
    'E-01': 'Concentra la dirección y la atención especializada del hogar: dirección general con su SS.HH., secretaría y área de '
            'bienvenida, sala de espera, sala de visita, sala de reuniones, asistencia social, psicología, área legal, oficina de '
            'monitoreo, administración, data center y servicios higiénicos. Se equipa con escritorios, sillas, armarios, archivadores, '
            'computadoras e impresoras; la sala de reuniones con mesa de reuniones, proyector, ecran y pizarra; la sala de visita y el '
            'área de bienvenida con un rincón infantil (exhibidor de libros, atril, cojines y piso encastrable) para las niñas y los '
            'niños que acompañan a sus madres.',
    'E-02': 'Almacén de donaciones con armarios y estantes metálicos, y tópico con camilla, biombo, silla de ruedas, escalera de dos '
            'peldaños, botiquín, coche multiusos e implementos médicos, con su SS.HH.',
    'E-03': 'Mantenimiento: almacén general y de limpieza con estantes metálicos, y almacenamiento de residuos sólidos con '
            'contenedores; maestranza, tablero eléctrico, subestación y grupo electrógeno sin mobiliario.',
    'E-04': 'Talleres productivos para la autonomía económica de las residentes (costura, bisutería y repostería), terapia grupal, '
            'cuarto de cámaras de videovigilancia, archivo y depósito, y servicios higiénicos con cuarto de limpieza.',
    'E-05': 'Módulo de enseñanza para la continuidad educativa de las hijas e hijos, lavandería, SUM-comedor, cocina con alacena y '
            'despensa, y módulo infantil con juegos y material blando.',
    'E-06': 'Habitaciones especial, dobles y simples con camarotes, camas de dos plazas, escritorios, sillas, armarios y veladores, '
            'y los servicios higiénicos de las habitaciones.',
    'E-07': 'Segundo bloque de habitaciones especial, dobles y simples, con camarotes, camas de dos plazas y camas cuna para las '
            'niñas y los niños pequeños, y sus servicios higiénicos.',
    'E-08': 'Tercer bloque de habitaciones especial, dobles y simples, con su mobiliario y sus servicios higiénicos.',
    'E-09': 'Vestidores con servicios higiénicos y almacén de implementos deportivos con estantes metálicos, canastilla para pelotas '
            'e implementos de básquet, vóley, fútbol, atletismo, gimnasia y box.',
}


def prosa(its):
    """Lista en texto de los ítems de un ambiente: descripción, código y cantidad."""
    par = ['%s (%s), %d und' % (it['des'].lower().rstrip('.'), it['cod'], it['cant']) for it in its if it['cant']]
    return '; '.join(par) + '.' if par else 'sin equipamiento.'


def pagina(M, apaisada):
    """Nueva sección vertical u horizontal, con el mismo encabezado y numeración continua."""
    sec = M.d.add_section(WD_SECTION.NEW_PAGE)
    for pg in sec._sectPr.findall(qn('w:pgNumType')):
        sec._sectPr.remove(pg)
    a, b = Cm(21.0), Cm(29.7)
    sec.orientation = WD_ORIENT.LANDSCAPE if apaisada else WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = (b, a) if apaisada else (a, b)
    sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = (Cm(2.0), Cm(2.0), Cm(2.0), Cm(1.6)) if apaisada else \
        (Cm(3.0), Cm(2.0), Cm(2.5), Cm(2.0))
    return sec


def figura_planta(M, ed):
    ruta = os.path.join(FIG, 'planta_%s.png' % ed)
    if not os.path.exists(ruta):
        raise FileNotFoundError(ruta + ' (correr vistas_mr.py)')
    from PIL import Image
    w, h = Image.open(ruta).size
    tit = 'Planta de equipamiento y mobiliario de %s - %s, con los códigos rotulados' % (ed, D.EDIFICACIONES[ed])
    fte = 'Fuente: Lámina %s de equipamiento y mobiliario.' % D.LAMINA[ed]
    if w / h > 1.25:
        pagina(M, True)
        MS.figura(M, ruta, tit, min(25.5, 14.6 * w / h), fte)
        pagina(M, False)
    else:
        MS.figura(M, ruta, tit, min(M.ancho, 20.5 * w / h), fte)


def generar():
    P = D.plano(); A = D.ambientes(P); cat = D.catalogo(P)
    if D.comprobacion(P)[1]:
        raise ValueError('cantidades distintas a la planta')
    M = R.Memoria()
    s0 = M.d.sections[0]; s0.left_margin = s0.right_margin = Cm(2.0); s0.top_margin = Cm(2.3); s0.bottom_margin = Cm(1.2)
    V.C.SERVICIO = 'EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:'
    V.COLOR, V.COLOR_SUB = '7B1E2B', 'F2D7DB'                    # especialidad de arquitectura: guinda
    foto = V.foto(); V.escudo()
    V.caratula(M.d, foto, 'MEMORIA DESCRIPTIVA', D.ESPECIALIDAD)
    MS.D = D                                                     # encabezado con el nombre y el CUI del hogar
    MS.encabezado(M, 'MEMORIA DESCRIPTIVA - EQUIPAMIENTO Y MOBILIARIO')
    R.indice(M)
    W = M.ancho
    items = [f for f in cat if f['tipo'] == 'item']

    # ================================================================== 1
    M.t1('GENERALIDADES')
    M.t2('Introducción')
    M.par('La presente memoria descriptiva corresponde a la especialidad de arquitectura, en su componente de equipamiento y '
          'mobiliario, del expediente técnico del proyecto “%s”, con CUI N.° %s.' % (D.PROYECTO, D.CUI))
    M.par('Describe los equipos, el mobiliario y los implementos de cada ambiente del Hogar de Refugio Temporal, los criterios con '
          'que se seleccionaron, sus características técnicas y las cantidades del metrado, de acuerdo con las láminas EM-01 a EM-07 '
          'de equipamiento y mobiliario.')
    M.t2('Antecedentes')
    M.par('El Hogar de Refugio Temporal brinda protección, albergue, alimentación y atención multidisciplinaria a mujeres víctimas de '
          'violencia en situación de riesgo de feminicidio o que peligre su integridad o su salud física o mental, y a sus hijas e '
          'hijos, en el marco de la Ley N.° 30364. Funciona las 24 horas: las residentes viven en el local con sus hijas e hijos en '
          'habitaciones especial, dobles y simples, y reciben atención psicológica, social y legal, talleres productivos para su '
          'autonomía económica, terapia grupal y servicios de alimentación y lavandería; las niñas y los niños cuentan con un módulo '
          'de enseñanza y un módulo infantil. El equipamiento debe ser seguro, durable, fácil de limpiar y adecuado a cada usuario, '
          'y debe brindar un entorno acogedor y digno.')
    M.t2('Nombre del proyecto y CUI')
    M.par('“%s”.' % D.PROYECTO, neg=True); M.par('Código único de inversiones (CUI): N.° %s.' % D.CUI)
    M.t2('Ubicación')
    MS.tabla(M, 'Ubicación', ['COMPONENTE', 'UBICACIÓN'], [['Departamento / región', 'San Martín'], ['Provincia', 'San Martín'],
                                                          ['Distrito', 'Morales'],
                                                          ['Sector', 'Predio rural Los Mangos, frente a la carretera Oasis']],
             [6.0, W - 6.0], izq=(0, 1))
    M.t2('Objetivos')
    MS.etiq(M, 'Objetivo general', 'Definir el equipamiento y el mobiliario de cada ambiente del Hogar de Refugio Temporal para que '
            'cumpla su función de protección, albergue y atención integral en condiciones de seguridad, privacidad, comodidad y '
            'dignidad para las residentes, sus hijas e hijos y el personal.')
    MS.etiq(M, 'Objetivos específicos', 'Dimensionar el equipamiento según el uso de cada ambiente; adecuar el mobiliario a sus '
            'usuarios; establecer sus características técnicas, materiales y acabados; y cuantificarlo en el metrado con su '
            'codificación (E equipos, M mobiliario, K implementos).')
    M.t2('Normatividad')
    MS.vines(M, ['Ley N.° 30364, Ley para prevenir, sancionar y erradicar la violencia contra las mujeres y los integrantes del grupo '
                 'familiar, y su Reglamento (D.S. N.° 009-2016-MIMP).',
                 'R.M. N.° 150-2016-MIMP, Lineamientos para la atención y funcionamiento de los Hogares de Refugio Temporal.',
                 'Reglamento Nacional de Edificaciones: Norma A.010 Condiciones Generales de Diseño; Norma A.090 Servicios Comunales; '
                 'Norma A.120 Accesibilidad Universal en Edificaciones; Norma A.130 Requisitos de Seguridad; Norma EM.010 Instalaciones '
                 'Eléctricas Interiores.',
                 'NTP 900.058 Gestión de residuos. Código de colores para el almacenamiento de residuos sólidos.',
                 'Normas del fabricante y certificados de calidad de equipos y electrodomésticos; registro sanitario (DIGEMID) para los '
                 'implementos médicos del tópico.'])
    M.t2('Alcance y láminas')
    MS.tabla(M, 'Láminas de equipamiento y mobiliario', ['LÁMINA', 'CONTENIDO', 'ESCALA'],
             [[l['codigo'], D.cap(l['titulo']).replace('edificacion', 'edificación'), l['escala']] for l in P['laminas']],
             [2.4, W - 4.8, 2.4], izq=(1,))

    # ================================================================== 2
    M.t1('CRITERIOS DE DISEÑO DEL EQUIPAMIENTO')
    M.t2('Según el usuario')
    MS.etiq(M, 'Residentes (E-06 a E-08)', 'habitaciones con camarote o cama de dos plazas, escritorio, silla, armario y velador, '
            'para que cada familia tenga un espacio propio y privado.')
    MS.etiq(M, 'Niñas y niños (E-05 y E-07)', 'módulo de enseñanza con mesas y sillas regulables en altura (M3 y M4), proyector '
            'interactivo y pizarra; módulo infantil con juegos de material blando, cojines y piso encastrable; camas cuna para los más '
            'pequeños; sin piezas pequeñas ni aristas.')
    MS.etiq(M, 'Talleres productivos (E-04)', 'máquinas de corte textil, mesas de corte y maniquíes en costura; mesas de trabajo en '
            'bisutería; cocinas industriales, horno microondas, licuadora, refrigeradora y mobiliario de acero inoxidable en '
            'repostería; mesas y taburetes en terapia grupal.')
    MS.etiq(M, 'Personal y atención especializada (E-01 y E-02)', 'oficinas con escritorio, silla, archivador, armario y computadora; '
            'tópico con camilla, biombo e implementos médicos; salas de espera y de visita con sofás y sillones.')
    MS.etiq(M, 'Personas con discapacidad', 'silla de ruedas en el tópico; servicios higiénicos accesibles con dispensadores a altura '
            'alcanzable (Norma A.120).')
    M.t2('Seguridad, durabilidad e higiene')
    MS.vines(M, ['Cantos redondeados, sin aristas ni tornillos salientes; muebles altos (armarios, estantes y archivadores) y camarotes '
                 'fijados a la pared para evitar su volteo en un sismo.',
                 'Materiales resistentes a la humedad del clima cálido y húmedo de Morales: melamina resistente a la humedad con cantos '
                 'de PVC, metal con pintura electrostática, acero inoxidable en cocina, repostería y tópico.',
                 'Superficies lavables y no porosas en cocina, tópico y servicios higiénicos; contenedores de residuos con tapa y código '
                 'de colores.',
                 'Equipos eléctricos de 220 V con garantía y conexión a las instalaciones del proyecto.'])
    M.t2('Codificación')
    M.par('Cada elemento lleva el código de las láminas de equipamiento y mobiliario: E para equipos, M para mobiliario y K para '
          'implementos. El mismo código se usa en la planta, en el cuadro de cada ambiente, en el metrado y en las especificaciones '
          'técnicas. Los extintores de los pasadizos pertenecen a la partida de seguridad y señalización.')

    # ================================================================== 3
    M.t1('EQUIPAMIENTO POR EDIFICACIÓN')
    por_ed = OrderedDict()
    for ed, amb, its in A:
        por_ed.setdefault(ed, []).append((amb, its))
    M.par('Para cada edificación se describe el equipamiento de cada ambiente con su código y su cantidad, tal como está dibujado y '
          'rotulado en la planta de la lámina; la tabla resume las cantidades del metrado y la figura muestra la planta con los códigos.')
    for ed, ambs in por_ed.items():
        M.t2('%s  %s' % (ed, D.EDIFICACIONES[ed]))
        M.par(TEXTO_ED[ed])
        filas = []
        for amb, its in ambs:
            MS.etiq(M, D.cap(amb), prosa(its))
            filas += [[D.cap(amb), it['cod'], D.cap(it['des'])[:95], it['cant']] for it in its]
        MS.tabla(M, 'Equipamiento y mobiliario de %s (lámina %s)' % (ed, D.LAMINA[ed]), ['AMBIENTE', 'CÓD.', 'DESCRIPCIÓN', 'CANT.'],
                 filas, [3.6, 1.3, W - 6.3, 1.4], tam=8, izq=(0, 2))
        figura_planta(M, ed)

    # ================================================================== 4
    M.t1('CARACTERÍSTICAS DE LOS EQUIPOS, EL MOBILIARIO Y LOS IMPLEMENTOS')
    M.par('Cada partida se agrupa en su familia, con las características comunes de materiales y acabados; la tabla indica en qué '
          'edificaciones va y su cantidad total. Las características de cada partida se detallan en las especificaciones técnicas.')
    donde = OrderedDict()
    for ed, amb, its in A:
        for it in its:
            donde.setdefault(it['clave'], OrderedDict()).setdefault(ed, 0)
            donde[it['clave']][ed] += it['cant']
    donde = {k: ', '.join('%s (%d)' % (e, n) for e, n in v.items()) for k, v in donde.items()}
    fam = OrderedDict()
    for f in items:
        fam.setdefault(F.familia(f['clave']), []).append(f)
    for k, fs in fam.items():
        x = F.FAMILIAS[k]
        M.t2(x['nombre'])
        MS.vines(M, x['mat'])
        MS.tabla(M, x['nombre'], ['CÓD.', 'DESCRIPCIÓN', 'UBICACIÓN', 'CANT.'],
                 [[f['cod'], D.cap(f['desc']), donde.get(f['clave'], ''), f['total']] for f in fs],
                 [1.3, W - 7.9, 5.2, 1.4], tam=8, izq=(1, 2))

    # ================================================================== 5
    M.t1('SUSTENTO DE LAS CANTIDADES')
    em = sum(it['cant'] for ed, amb, its in A for it in its if it['grupo'] in 'EM')
    M.par('Las cantidades del metrado se obtuvieron del equipamiento de cada ambiente de las láminas EM-01 a EM-07 y se comprobaron '
          'contando, por edificación, cada código escrito en la planta: textos sueltos, directrices y textos dentro de bloques. En '
          'equipos (E) y mobiliario (M) las cantidades del metrado son iguales a lo rotulado en las nueve edificaciones (%d und). En '
          'los implementos (K), que la planta rotula una vez por tipo, rige la cantidad del equipamiento de cada ambiente.' % em)
    filas = []
    for ed in D.EDIFICACIONES:
        n = {g: sum(it['cant'] for e, a, its in A if e == ed for it in its if it['grupo'] == g) for g in 'EMK'}
        filas.append([ed, D.EDIFICACIONES[ed], D.LAMINA[ed], n['E'], n['M'], n['K']])
    filas.append(['', 'TOTAL', '', sum(r[3] for r in filas), sum(r[4] for r in filas), sum(r[5] for r in filas)])
    MS.tabla(M, 'Unidades por edificación', ['EDIF.', 'EDIFICACIÓN', 'LÁMINA', 'EQUIPOS', 'MOBILIARIO', 'IMPLEMENTOS'], filas,
             [1.3, W - 9.3, 1.8, 2.0, 2.2, 2.0], tam=8, izq=(1,), colores={(len(filas) - 1, k): 'F2E6E8' for k in range(6)})
    camas = {k: sum(it['cant'] for e, a, its in A for it in its if it['clave'] == k) for k in ('M64', 'M78', 'M79')}
    M.par('En las habitaciones de E-06, E-07 y E-08 hay %d camarotes (dos camas cada uno), %d camas de dos plazas y %d camas cuna, '
          'con sus colchones.' % (camas['M64'], camas['M78'], camas['M79']))

    # ================================================================== 6
    M.t1('RESUMEN GENERAL')
    filas = []
    for g, nombre in D.GRUPOS.items():
        fs = [f for f in items if f['g'] == g]
        filas.append([D.cap(nombre), len(fs), sum(f['total'] for f in fs)])
    filas.append(['TOTAL', sum(r[1] for r in filas), sum(r[2] for r in filas)])
    MS.tabla(M, 'Resumen del equipamiento y mobiliario', ['GRUPO', 'PARTIDAS', 'UNIDADES'], filas, [W - 6.0, 3.0, 3.0], izq=(0,),
             colores={(len(filas) - 1, k): 'F2E6E8' for k in range(3)})
    M.par('El detalle por partida, por edificación y por ambiente está en el metrado de equipamiento y mobiliario (hojas RESUMEN, '
          'METRADO POR AMBIENTE y POR EDIFICACIÓN), y las condiciones de suministro de cada partida en las especificaciones técnicas.')

    # ================================================================== 7
    M.t1('SUMINISTRO, INSTALACIÓN Y MANTENIMIENTO')
    MS.vines(M, ['Antes de la compra o fabricación, el contratista presenta a la Supervisión fichas técnicas, catálogos o muestras de cada '
                 'partida para su aprobación.',
                 'Los muebles se entregan armados, limpios y en su ambiente; los altos y los camarotes se fijan a la pared; los equipos '
                 'se instalan y prueban en presencia de la Supervisión, con sus garantías y manuales.',
                 'La entrega se hace por ambiente, con acta que indique código, cantidad y estado, y con los números de serie de los equipos.',
                 'El hogar programa el mantenimiento: limpieza diaria del mobiliario, revisión semestral de bisagras, correderas, ruedas y '
                 'fijaciones, y mantenimiento de los equipos según el fabricante.'])
    M.d.core_properties.author = ''
    M.d.core_properties.title = 'Memoria descriptiva - Equipamiento y mobiliario - Hogar de Refugio Temporal'
    M.d.save(SALIDA)
    import indice_word
    indice_word.llenar([SALIDA])                                # índice lleno para imprimir
    return SALIDA


if __name__ == '__main__':
    print(generar())
