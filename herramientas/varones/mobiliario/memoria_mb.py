# -*- coding: utf-8 -*-
"""Memoria descriptiva de equipamiento y mobiliario - CAR Varones (CUI 2705619), en Word.

Con los datos del plano (cuadros de equipamiento de las láminas MB-01 a MB-09, lee_plano_mb.py) y las cantidades adoptadas del
metrado (datos_mb.py): generalidades, criterios de diseño del equipamiento por tipo de usuario, equipamiento de cada edificación
y ambiente con su planta, descripción de equipos, mobiliario e implementos por familia (fichas_mb.py), resumen general,
instalación, entrega y mantenimiento, y láminas. Formato y carátula de las memorias del CAR Varones.

Uso: python3 herramientas/varones/mobiliario/memoria_mb.py
Salida: entregables_varones/MEMORIA_DESCRIPTIVA_EQUIPAMIENTO_Y_MOBILIARIO_CAR_VARONES.docx
"""
import os
import sys
from collections import OrderedDict

from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml.ns import qn
from docx.shared import Cm

AQUI = os.path.dirname(os.path.abspath(__file__)); VAR = os.path.dirname(AQUI); HER = os.path.dirname(VAR)
for d in (AQUI, os.path.join(VAR, 'senalizacion'), VAR, HER):
    sys.path.insert(0, d)
import datos_mb as D  # noqa: E402
import fichas_mb as F  # noqa: E402
import memoria_descriptiva_refugio as R  # noqa: E402
import caratulas_v as V  # noqa: E402
import memoria_se as MS  # noqa: E402

SALIDA = os.path.join(D.SAL, 'MEMORIA_DESCRIPTIVA_EQUIPAMIENTO_Y_MOBILIARIO_CAR_VARONES.docx')
FIG = os.path.join(D.SAL, 'figuras_mobiliario')
TEXTO_ED = {
    'E-01': 'Concentra la dirección y la atención especializada del centro: dirección general, secretaría y sala de espera, sala de '
            'reuniones, trabajo social, asesoría legal, psicología, consultorio de nutrición, educador, monitoreo y tópico. Se equipa con '
            'escritorios con credenza, sillas, archivadores, armarios, computadoras e impresoras; la sala de reuniones con mesa para 10 '
            'personas, proyector y pizarra; el tópico con camilla, biombo, silla de ruedas, botiquín, coche multiusos e implementos médicos.',
    'E-02': 'Vestidores de la losa deportiva con sus servicios higiénicos y el almacén de implementos deportivos, con estantes '
            'metálicos, canastilla móvil y los implementos de básquet, vóley, fútbol, atletismo, gimnasia y box.',
    'E-03': 'Módulo de las madres sustitutas: dormitorio con camas y armarios, servicios higiénicos y lavandería con depósito.',
    'E-04': 'Vivienda de adolescentes de 12 a 17 años: oficina de entrevista y estar, salón de estudios con escritorios y computadoras, '
            'dormitorio de la madre con baño, dormitorios con camas y armarios, servicios higiénicos y lavandería con depósito.',
    'E-05': 'Segunda vivienda de adolescentes de 12 a 17 años, con el mismo equipamiento que E-04.',
    'E-06': 'Vivienda de niños de 3 a 5 años: oficina de entrevista y estar, salón de psicomotricidad con juegos y material blando, '
            'dormitorio de la madre, dormitorios, servicios higiénicos y lavandería.',
    'E-07': 'Vivienda de niños de 6 a 11 años: oficina de entrevista y estar, taller de arte con mesas y sillas regulables, proyector '
            'interactivo y pizarra, dormitorio de la madre, dormitorios con camas y credenzas, servicios higiénicos y lavandería.',
    'E-08': 'Sala de usos múltiples y comedor para toda la población del centro, con mesas de trabajo, sillas regulables, proyector y '
            'ecran; cocina con su lavandería, equipos y mobiliario de acero inoxidable; almacén de cocina y cuarto de gas; depósito y '
            'almacén general; residuos sólidos y servicios higiénicos de personal.',
    'E-09': 'Servicios higiénicos públicos, con cestos y dispensadores.',
    'E-10': 'Servicios generales: maestranza con contenedores de residuos.',
}


def nota_completa(cod, nota):
    """Motivo de una corrección; los "Ídem" se reemplazan por el motivo completo del mismo código."""
    if not nota.startswith('Ídem'):
        return nota
    for e, a, c, q, m in D.CORRECCIONES:
        if c == cod and not m.startswith('Ídem'):
            return m
    return nota


def prosa(its):
    """Lista en texto de los ítems de un ambiente: cantidad, descripción y código."""
    par = []
    for it in its:
        if it['grupo'] == 'S' or not it['cant']:
            continue
        par.append('%d %s (%s)' % (it['cant'], it['des'].lower().rstrip('.'), it['cod']))
    return '; '.join(par) + '.' if par else 'sin equipamiento en el cuadro.'


def pagina(M, apaisada):
    """Nueva sección (salto de página) vertical u horizontal, con el mismo encabezado y numeración continua."""
    sec = M.d.add_section(WD_SECTION.NEW_PAGE)
    for pg in sec._sectPr.findall(qn('w:pgNumType')):             # la copia de la sección anterior reiniciaría la numeración
        sec._sectPr.remove(pg)
    a, b = Cm(21.0), Cm(29.7)
    sec.orientation = WD_ORIENT.LANDSCAPE if apaisada else WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = (b, a) if apaisada else (a, b)
    sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = (Cm(2.0), Cm(2.0), Cm(2.0), Cm(1.6)) if apaisada else \
        (Cm(3.0), Cm(2.0), Cm(2.5), Cm(2.0))
    return sec


def figura_planta(M, ed, lam):
    ruta = os.path.join(FIG, 'planta_%s.png' % ed)
    if not os.path.exists(ruta):
        return
    from PIL import Image
    w, h = Image.open(ruta).size
    tit = 'Planta de equipamiento y mobiliario de %s, con los códigos rotulados' % ed
    fte = 'Fuente: Lámina %s de equipamiento y mobiliario.' % (', '.join(lam) or 'MB')
    if w / h > 1.25:                                             # planta alargada: hoja horizontal a todo el ancho
        pagina(M, True)
        MS.figura(M, ruta, tit, min(25.5, 14.6 * w / h), fte)
        pagina(M, False)
    else:
        MS.figura(M, ruta, tit, min(M.ancho, 21.5 * w / h), fte)


def generar():
    P = D.plano(); A = D.ambientes(P); cat = D.catalogo(P)
    M = R.Memoria()
    s0 = M.d.sections[0]; s0.left_margin = s0.right_margin = Cm(2.0); s0.top_margin = Cm(2.3); s0.bottom_margin = Cm(1.2)
    V.C.SERVICIO = 'EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:'
    foto = V.foto(); V.escudo()
    V.caratula(M.d, foto, 'MEMORIA DESCRIPTIVA', D.ESPECIALIDAD)
    MS.encabezado(M, 'MEMORIA DESCRIPTIVA - EQUIPAMIENTO Y MOBILIARIO')
    R.indice(M)
    W = M.ancho
    items = [f for f in cat if f['tipo'] == 'item']
    tot = {f['clave']: f for f in items}

    # ================================================================== 1
    M.t1('GENERALIDADES')
    M.t2('Introducción')
    M.par('La presente memoria descriptiva corresponde a la especialidad de arquitectura, en su componente de equipamiento y '
          'mobiliario, del expediente técnico del proyecto “%s”, con CUI N.° %s.' % (D.PROYECTO, D.CUI))
    M.par('Describe los equipos, el mobiliario y los implementos de cada ambiente del Centro de Acogida Residencial (CAR) Varones, '
          'los criterios con que se seleccionaron, sus características técnicas y las cantidades del metrado, de acuerdo con las '
          'láminas MB-01 a MB-09 de equipamiento y mobiliario.')
    M.t2('Antecedentes')
    M.par('El CAR Varones brinda alojamiento, alimentación, cuidado, educación y atención integral a niños y adolescentes varones de 3 '
          'a 17 años sin cuidados parentales o en riesgo de perderlos. Funciona las 24 horas, con residentes que viven en el local '
          'organizados por grupos de edad en cuatro viviendas, un módulo de madres sustitutas, administración con atención '
          'especializada, sala de usos múltiples con comedor y cocina, vestidores y almacén deportivo, servicios higiénicos públicos y '
          'servicios generales. El equipamiento debe ser seguro, durable, fácil de limpiar y adecuado a la edad de sus usuarios.')
    M.t2('Nombre del proyecto y CUI')
    M.par('“%s”.' % D.PROYECTO, neg=True); M.par('Código único de inversiones (CUI): N.° %s.' % D.CUI)
    M.t2('Ubicación')
    MS.tabla(M, 'Ubicación', ['COMPONENTE', 'UBICACIÓN'], [['Departamento / región', 'San Martín'], ['Provincia', 'San Martín'],
                                                          ['Distrito', 'Morales'], ['Sector', 'Predio rural Los Mangos, frente a la carretera Oasis']],
             [6.0, W - 6.0], izq=(0, 1))
    M.t2('Objetivos')
    MS.etiq(M, 'Objetivo general', 'Definir el equipamiento y el mobiliario de cada ambiente del CAR Varones para que cumpla su función '
            'de acogida, cuidado y atención integral en condiciones de seguridad, comodidad y dignidad para los residentes y el personal.')
    MS.etiq(M, 'Objetivos específicos', 'Dimensionar el equipamiento según la población y el uso de cada ambiente; adecuar el '
            'mobiliario a la edad de los usuarios; establecer sus características técnicas, materiales y acabados; y cuantificarlo en '
            'el metrado con su codificación (E equipos, M mobiliario, K implementos).')
    M.t2('Normatividad')
    MS.vines(M, ['Decreto Legislativo N.° 1297, para la protección de niñas, niños y adolescentes sin cuidados parentales o en riesgo de '
                 'perderlos, y su Reglamento (D.S. N.° 001-2018-MIMP).',
                 'Reglamento Nacional de Edificaciones: Norma A.010 Condiciones Generales de Diseño; Norma A.090 Servicios Comunales; '
                 'Norma A.120 Accesibilidad Universal en Edificaciones; Norma A.130 Requisitos de Seguridad; Norma EM.010 Instalaciones '
                 'Eléctricas Interiores.',
                 'NTP 900.058 Gestión de residuos. Código de colores para el almacenamiento de residuos sólidos.',
                 'Normas del fabricante y certificados de calidad de equipos y electrodomésticos; registro sanitario (DIGEMID) para los '
                 'implementos médicos.'])
    M.t2('Alcance y láminas')
    MS.tabla(M, 'Láminas de equipamiento y mobiliario', ['LÁMINA', 'CONTENIDO', 'ESCALA'],
             [[l['codigo'], l['titulo'].capitalize().replace('edificación', 'edificación'), l['escala']] for l in P['laminas']],
             [2.4, W - 4.8, 2.4], izq=(1,))

    # ================================================================== 2
    M.t1('CRITERIOS DE DISEÑO DEL EQUIPAMIENTO')
    M.t2('Según el usuario')
    MS.etiq(M, 'Niños de 3 a 5 años (E-06)', 'mobiliario bajo y liviano, juegos de psicomotricidad de material blando, piso encastrable '
            'y cojines; sin piezas pequeñas ni aristas.')
    MS.etiq(M, 'Niños de 6 a 11 años (E-07)', 'taller de arte con mesas y sillas regulables en altura (M03 y M04), proyector interactivo y '
            'pizarra; muebles para mochilas.')
    MS.etiq(M, 'Adolescentes de 12 a 17 años (E-04 y E-05)', 'salón de estudios con escritorios y computadoras; dormitorios con cama y '
            'armario por residente.')
    MS.etiq(M, 'Madres sustitutas y personal', 'dormitorio con cama de dos plazas, escritorio y velador en cada vivienda; oficinas con '
            'escritorio, silla, archivador y computadora.')
    MS.etiq(M, 'Personas con discapacidad', 'silla de ruedas en el tópico; servicios higiénicos accesibles con dispensadores a altura alcanzable.')
    M.t2('Seguridad, durabilidad e higiene')
    MS.vines(M, ['Cantos redondeados, sin aristas ni tornillos salientes; muebles altos (armarios, estantes, archivadores y casilleros) '
                 'fijados a la pared para evitar su volteo en un sismo.',
                 'Materiales resistentes a la humedad del clima cálido y húmedo de Morales: melamina resistente a la humedad con cantos '
                 'de PVC, metal con pintura electrostática, acero inoxidable en cocina y tópico.',
                 'Superficies lavables y no porosas en cocina, tópico y servicios higiénicos; contenedores de residuos con tapa y código de colores.',
                 'Equipos eléctricos de 220 V con garantía y conexión a las instalaciones del proyecto; balones de gas en un cuarto ventilado.'])
    M.t2('Codificación')
    M.par('Cada elemento lleva el código de los cuadros de equipamiento de las láminas: E para equipos, M para mobiliario y K para '
          'implementos. El mismo código se usa en la planta, en el cuadro de cada ambiente, en el metrado y en las especificaciones técnicas.')

    # ================================================================== 3
    M.t1('EQUIPAMIENTO POR EDIFICACIÓN')
    por_ed = OrderedDict()
    for ed, amb, its in A:
        por_ed.setdefault(ed, []).append((amb, its))
    M.par('Para cada edificación se describe el equipamiento de cada ambiente con su código y su cantidad, tal como está rotulado en '
          'la planta de la lámina; la tabla resume las cantidades del metrado y la figura muestra la planta con los códigos.')
    for ed, ambs in por_ed.items():
        M.t2('%s  %s' % (ed, D.EDIFICACIONES.get(ed, '')))
        M.par(TEXTO_ED.get(ed, ''))
        filas = []; notas = []
        for amb, its in ambs:
            MS.etiq(M, amb.capitalize(), prosa(its))
            for it in its:
                if it['grupo'] == 'S' or not it['cant']:
                    continue
                filas.append([amb.capitalize(), it['cod'], it['des'].capitalize()[:95], it['cant']])
                if it['nota']:
                    n = '%s, %s: %s' % (amb.capitalize(), it['cod'], nota_completa(it['cod'], it['nota']))
                    if n not in notas:
                        notas.append(n)
        lam = [l['codigo'] for l in P['laminas'] if ed[-2:] in l['titulo']]
        MS.tabla(M, 'Equipamiento y mobiliario de %s (lámina %s)' % (ed, ', '.join(lam) or '—'), ['AMBIENTE', 'CÓD.', 'DESCRIPCIÓN', 'CANT.'],
                 filas, [3.6, 1.3, W - 6.3, 1.4], tam=8, izq=(0, 2))
        if notas:
            MS.sub(M, 'Cantidades ajustadas a la planta de %s' % ed)
            MS.vines(M, notas)
        figura_planta(M, ed, lam)

    # ================================================================== 4
    M.t1('CARACTERÍSTICAS DE LOS EQUIPOS, EL MOBILIARIO Y LOS IMPLEMENTOS')
    M.par('Cada partida se agrupa en su familia, con las características comunes de materiales y acabados; la tabla indica en qué '
          'edificaciones va y su cantidad total. Las características de cada partida se detallan en las especificaciones técnicas.')
    donde = OrderedDict()
    for ed, amb, its in A:
        for it in its:
            if it['grupo'] != 'S' and it['cant']:
                donde.setdefault(it['clave'], OrderedDict()).setdefault(ed, 0)
                donde[it['clave']][ed] += it['cant']
    donde = {k: ', '.join('%s (%d)' % (e, n) for e, n in v.items()) for k, v in donde.items()}
    fam = OrderedDict()
    for f in items:
        amb = f['desc'] if f['g'] == 'K' else ''
        k = F.familia(f['cod'], f['desc'], next((s['desc'] for s in cat if s['tipo'] == 'sub' and False), ''))
        if f['g'] == 'K':
            sub = [s for s in cat if s['tipo'] in ('sub', 'item') and s['g'] == 'K']
            cur = None
            for s in sub:
                if s['tipo'] == 'sub':
                    cur = s['desc']
                if s is f:
                    break
            k = 'topico' if cur and 'TOPICO' in cur.upper() else 'implemento'
        fam.setdefault(k, []).append(f)
    for k, fs in fam.items():
        x = F.FAMILIAS[k]
        M.t2(x['nombre'])
        MS.vines(M, x['mat'])
        MS.tabla(M, x['nombre'], ['CÓD.', 'DESCRIPCIÓN', 'UBICACIÓN', 'CANT.'],
                 [[f['cod'], f['desc'].capitalize(), donde.get(f['clave'], ''), f['total']] for f in fs],
                 [1.3, W - 7.9, 5.2, 1.4], tam=8, izq=(1, 2))

    # ================================================================== 5
    M.t1('COMPATIBILIZACIÓN DEL PLANO CON EL METRADO')
    M.par('Las cantidades del metrado se obtuvieron de los cuadros de equipamiento de cada ambiente (láminas MB-01 a MB-09) y se '
          'comprobaron contando, por edificación, cada código escrito en la planta: textos sueltos, directrices y textos dentro de bloques. '
          'En equipos (E) y mobiliario (M) las cantidades adoptadas coinciden con lo rotulado en las diez edificaciones (%d und). En los '
          'implementos (K) la planta rotula un solo ejemplar por tipo, por lo que rigen los cuadros.' % sum(
              it['cant'] for ed, amb, its in A for it in its if it['grupo'] in 'EM'))
    filas = []
    for ed, amb, its in A:
        for it in its:
            if it['nota'] and it['grupo'] in 'EMK':
                filas.append([ed, amb.capitalize(), it['cod'], it['cuadro'] or 0, it['cant'], nota_completa(it['cod'], it['nota'])])
    MS.tabla(M, 'Cantidades ajustadas a lo dibujado y rotulado en la planta', ['EDIF.', 'AMBIENTE', 'CÓD.', 'CUADRO', 'METRADO', 'MOTIVO'],
             filas, [1.3, 3.0, 1.2, 1.8, 2.0, W - 9.3], tam=8, izq=(1, 5))
    M.t2('Observaciones al plano')
    M.par('Se deben corregir en las láminas para que los cuadros digan lo mismo que la planta y el metrado:')
    MS.vines(M, ['%s: %s' % (l, t) for l, t in D.OBS_PLANO])

    # ================================================================== 6
    M.t1('RESUMEN GENERAL')
    filas = []
    for g, nombre in D.GRUPOS.items():
        fs = [f for f in items if f['g'] == g]
        filas.append([nombre.capitalize(), len(fs), sum(f['total'] for f in fs)])
    filas.append(['TOTAL', sum(r[1] for r in filas), sum(r[2] for r in filas)])
    MS.tabla(M, 'Resumen del equipamiento y mobiliario', ['GRUPO', 'PARTIDAS', 'UNIDADES'], filas, [W - 6.0, 3.0, 3.0], izq=(0,),
             colores={(len(filas) - 1, k): 'F2E6E8' for k in range(3)})
    M.par('El detalle por partida, por edificación y por ambiente está en el metrado de equipamiento y mobiliario (hojas RESUMEN y '
          'METRADO POR AMBIENTE), y las condiciones de suministro de cada partida en las especificaciones técnicas.')

    # ================================================================== 7
    M.t1('SUMINISTRO, INSTALACIÓN Y MANTENIMIENTO')
    MS.vines(M, ['Antes de la compra o fabricación, el contratista presenta a la Supervisión fichas técnicas, catálogos o muestras de cada '
                 'partida para su aprobación.',
                 'Los muebles se entregan armados, limpios y en su ambiente; los altos se fijan a la pared; los equipos se instalan y '
                 'prueban en presencia de la Supervisión, con sus garantías y manuales.',
                 'La entrega se hace por ambiente, con acta que indique código, cantidad y estado, y con los números de serie de los equipos.',
                 'El centro programa el mantenimiento: limpieza diaria del mobiliario, revisión semestral de bisagras, correderas, ruedas y '
                 'fijaciones, y mantenimiento de los equipos según el fabricante.'])
    M.d.core_properties.author = ''; M.d.core_properties.title = 'Memoria descriptiva - Equipamiento y mobiliario - CAR Varones'
    M.d.save(SALIDA)
    return SALIDA


if __name__ == '__main__':
    print(generar())
