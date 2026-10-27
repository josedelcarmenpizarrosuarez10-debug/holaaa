# -*- coding: utf-8 -*-
"""Memoria descriptiva de evacuación y señalización - CAR Varones (CUI 2705619), en Word.

Estructura del ejemplo del usuario (memoria de evacuación y señalización del Hogar de Refugio Temporal) adaptada a un centro de
acogida residencial de niños y adolescentes varones y ampliada: generalidades con ubicación, accesos, objetivos y normas;
descripción del centro con los ambientes de cada edificación leídos del plano; componentes del plan con la identificación de
peligros por edificación; población y cálculo de aforo; medios de evacuación (ancho de puertas y pasajes, rutas, tiempos y zonas
seguras); organización para emergencias (comité, director, mantenimiento, brigadas y personal); protocolos ante sismo, incendio,
lluvias intensas, fuga de gas y corte de energía; procedimiento de evacuación con directorio de emergencias; protección contra
incendio y señalización con la clasificación de la NTP 399.010-1, la tabla de simbología con la imagen de cada señal y una ficha
por señal; distribución por edificación; mantenimiento e inspección; conclusiones y láminas.

Datos: plano final de la arquitecta (lee_plano_se.py), cantidades del metrado (datos_se.py), imágenes de las señales
(senales_img.py) y vistas de las láminas (vistas_se.py). Incluye las correcciones M-01 a M-06.

Uso: python3 herramientas/varones/senalizacion/memoria_se.py
Salida: entregables_varones/MEMORIA_DESCRIPTIVA_EVACUACION_Y_SENALIZACION_CAR_VARONES.docx
"""
import math
import os
import sys

from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

AQUI = os.path.dirname(os.path.abspath(__file__)); VAR = os.path.dirname(AQUI); HER = os.path.dirname(VAR)
RAIZ = os.path.dirname(HER)
for d in (AQUI, VAR, HER):
    sys.path.insert(0, d)
import datos_se as D  # noqa: E402
import memoria_descriptiva_refugio as R  # noqa: E402
import caratulas_v as V  # noqa: E402
import senales_img as SI  # noqa: E402

SALIDA = os.path.join(D.SAL, 'MEMORIA_DESCRIPTIVA_EVACUACION_Y_SENALIZACION_CAR_VARONES.docx')
FIG = os.path.join(D.SAL, 'figuras_senalizacion')
MAPAS = os.path.join(RAIZ, 'insumos/katiuska/senalizacion/mapas')
UTM = (345749, 9282885)                     # centro del frente del predio (UTM WGS 84 18 S, referencial: colector del CAR Varones)
NPT_FRENTE = 261.15                          # piso terminado del frente (colector del CAR Varones)

OBRAS = [('O.C. 01', 'Obra complementaria', 'Patio principal'), ('O.C. 02', 'Obra complementaria', 'Losa deportiva'),
         ('O.C. 03', 'Obra complementaria', 'Patio de maniobras'), ('O.C. 04', 'Obra complementaria', 'Patio de juegos'),
         ('O.E. 01', 'Obra exterior', 'Cerco perimétrico con ingreso principal e ingreso al patio de maniobras'),
         ('O.E. 02', 'Obra exterior', 'Tanque elevado y cisterna'), ('O.E. 03', 'Obra exterior', 'Ingreso principal'),
         ('O.E. 04', 'Obra exterior', 'Caseta de control'), ('O.E. 05', 'Obra exterior', 'Zona de pozo séptico'),
         ('O.E. 06', 'Obra exterior', 'Área de sembríos'), ('O.E. 07', 'Obra exterior', 'Veredas y circulación posterior de los módulos')]

# peligros por edificación (ambientes del plano) y medidas del proyecto
PELIGROS = [
    ('E-01 Administración', 'Equipos de cómputo y data center; archivo de papel; tópico', 'Incendio de origen eléctrico (clase A y C)',
     'Extintor PQS, detectores de humo, central de alarma, luces de emergencia, botiquín'),
    ('E-02 Vestidores', 'Vestidores y almacén de implementos deportivos', 'Caídas por piso mojado; incendio clase A',
     'Extintor PQS, salidas señalizadas, luces de emergencia'),
    ('E-03 Módulo de madres', 'Dormitorio, lavandería y depósito', 'Incendio nocturno; evacuación de personas dormidas',
     'Detectores de humo, alarma, extintor PQS, luces de emergencia'),
    ('E-04 a E-07 Módulos', 'Dormitorios, closets, estar, salón de estudios o taller, lavandería', 'Incendio nocturno; evacuación de '
     'niños pequeños (3 a 5 años) y adolescentes', 'Detectores de humo en cada ambiente, alarma, extintor PQS, luces de emergencia, '
     'zonas seguras internas, salidas a las circulaciones exteriores'),
    ('E-08 SUM y cocina', 'Cocina con cuarto de gas, comedor, almacenes y residuos sólidos', 'Incendio por gas licuado y aceites '
     '(clase B y K); fuga de gas; mayor concentración de personas (66)', 'Extintores PQS y CO2, detectores de humo, alarma, '
     'dos salidas, rutas 03, 04 y 05, zonas de reunión S3, S4 y S5'),
    ('E-09 SS.HH. público', 'Servicios higiénicos de hombres, mujeres y discapacitados', 'Caídas; persona con movilidad reducida',
     'Señal de SS.HH. accesible, luces de emergencia, alarma'),
    ('E-10 Servicios generales', 'Tablero general, subestación, grupo electrógeno, maestranza, cuarto de limpieza',
     'Riesgo eléctrico y de descarga; incendio clase C; combustible del grupo electrógeno', 'Señales de riesgo eléctrico, de descarga y '
     'de prohibido el ingreso, detectores de humo, luces de emergencia'),
    ('Obras exteriores', 'Tanque elevado y cisterna, pozo séptico, losa deportiva, estacionamiento, caseta de control',
     'Caídas, gases del pozo séptico, tránsito vehicular en el patio de maniobras', 'Zonas de reunión exteriores S1 a S13 lejos de '
     'fachadas, señal de aforo en la caseta, control del tránsito durante la evacuación'),
]
DIRECTORIO = [('Cuerpo General de Bomberos Voluntarios del Perú', '116'), ('Policía Nacional del Perú', '105'),
              ('Sistema de Atención Médica Móvil de Urgencia (SAMU)', '106'), ('Defensa Civil (INDECI)', '115'),
              ('Línea de orientación en salud (MINSA)', '113'), ('Línea de atención a la violencia familiar y sexual', '100')]


# ---------------------------------------------------------------------------------------------- Word: piezas propias
def encabezado(M, titulo='MEMORIA DESCRIPTIVA - EVACUACIÓN Y SEÑALIZACIÓN'):
    sec = M.d.add_section(WD_SECTION.NEW_PAGE)
    sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(3.0), Cm(2.0), Cm(2.5), Cm(2.0)
    sec.header.is_linked_to_previous = False; sec.footer.is_linked_to_previous = False
    pg = OxmlElement('w:pgNumType'); pg.set(qn('w:start'), '1'); sec._sectPr.append(pg)
    h = sec.header.paragraphs[0]; h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    M.run(h, titulo, 8.5, True, color=R.GRANATE)
    M.run(h, '   |   %s - CUI N.° %s' % (D.CORTO, D.CUI), 8.5, color=R.GRANATE)
    b = OxmlElement('w:pBdr'); e = OxmlElement('w:bottom')
    for k, v in (('val', 'single'), ('sz', '8'), ('space', '2'), ('color', R.GRANATE)):
        e.set(qn('w:' + k), v)
    b.append(e); h._p.get_or_add_pPr().insert(1, b)
    f = sec.footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    M.run(f, 'Página ', 8.5, color=R.GRIS)
    for tipo in ('begin', 'instr', 'separate', 'txt', 'end'):
        r = M.run(f, '', 8.5, color=R.GRIS)
        if tipo == 'instr':
            it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = 'PAGE'; r._r.append(it)
        elif tipo == 'txt':
            r.text = '1'
        else:
            fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), tipo); r._r.append(fc)


def sombra(c, color):
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), color)
    tcPr = c._tc.get_or_add_tcPr(); va = tcPr.find(qn('w:vAlign'))
    va.addprevious(sh) if va is not None else tcPr.append(sh)


def tabla(M, titulo, cab, filas, anchos, tam=9, izq=(), colores=None, img_alto=None, fuente_txt='Fuente: Elaboración propia.'):
    """Tabla con encabezado granate; celdas de texto, de imagen (('img', ruta, ancho_cm)) o con color de fondo."""
    M.nt += 1; M.leyenda('Tabla N.° %02d: %s' % (M.nt, titulo))
    t = M.d.add_table(rows=1, cols=len(cab)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for gc, w in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), anchos):
        gc.set(qn('w:w'), str(int(w * 567)))
    e = OxmlElement('w:tblHeader'); e.set(qn('w:val'), 'true'); t.rows[0]._tr.get_or_add_trPr().append(e)
    for k, fila in enumerate([cab] + filas):
        celdas = t.rows[0].cells if k == 0 else t.add_row().cells
        if k:
            t.rows[-1]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for j, (c, v) in enumerate(zip(celdas, fila)):
            c.width = Cm(anchos[j]); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            q = c.paragraphs[0]; q.paragraph_format.space_after = Pt(1); q.paragraph_format.space_before = Pt(1)
            q.alignment = WD_ALIGN_PARAGRAPH.LEFT if (j in izq and k > 0) else WD_ALIGN_PARAGRAPH.CENTER
            if isinstance(v, tuple) and v and v[0] == 'img':
                q.add_run().add_picture(v[1], width=Cm(v[2]))
            else:
                M.run(q, str(v), tam, neg=(k == 0), color='FFFFFF' if k == 0 else None)
            if k == 0:
                sombra(c, R.GRANATE)
            elif colores and (k - 1, j) in colores:
                sombra(c, colores[(k - 1, j)])
    M.fuente(fuente_txt)
    return t


def figura(M, ruta, titulo, ancho=16.0, fuente_txt='Fuente: Elaboración propia.'):
    if not os.path.exists(ruta):
        return
    M.nf += 1; M.leyenda('Figura N.° %02d: %s' % (M.nf, titulo))
    p = M.par(centro=True, despues=2); p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(ruta, width=Cm(ancho))
    M.fuente(fuente_txt)


def sub(M, txt):
    """Subtítulo de tercer nivel (negrita granate, sin numeración del índice)."""
    p = M.par(txt, 11, True, color=R.GRANATE, antes=6, despues=3); p.paragraph_format.keep_with_next = True
    return p


def vines(M, lista):
    for t in lista:
        M.vin(t)


def etiq(M, etiqueta, texto):
    p = M.par(despues=3, sangria=0.9); p.paragraph_format.first_line_indent = Cm(-0.45)
    M.run(p, '•  ' + etiqueta + ': ', neg=True); M.run(p, texto)


def ficha(M, p, img):
    """Ficha de una señal: imagen a la izquierda y sus datos a la derecha."""
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
    lugares = ', '.join('%s (%d)' % (c, n) for c, n in p['por'].items() if n) or ('según la lámina SE-S-01 (tableros y equipos de alarma)'
                                                                                   if p['sin_ubicar'] else '—')
    for et, v in (('Función', p['uso']), ('Dimensiones', p['dim']), ('Material', p['material']), ('Altura de instalación', p['altura']),
                  ('Cantidad', '%d und' % p['total']), ('Ubicación', lugares)):
        r = c1.add_paragraph(); r.paragraph_format.space_after = Pt(1)
        M.run(r, et + ': ', 9, True); M.run(r, v, 9)
    sp = M.d.add_paragraph(); sp.paragraph_format.space_after = Pt(4)


# ---------------------------------------------------------------------------------------------- contenido
def generar():
    P = D.plano(); pts = D.partidas(P); Pb = D.POBLACION; rutas = D.rutas(P); zs = D.zonas(P); z = D.zona_segura()
    por = {p['clave']: p for p in pts if p['und']}
    q = {k: v['total'] for k, v in por.items()}
    eds = D.edificaciones(P); amb = P['ambientes']
    SI.generar()                                                     # imágenes de las señales (rápido, sin el DXF)
    img = {p['item']: os.path.join(FIG, 'senal_%s.png' % SI.nombre(p['desc'])) for p in pts if p['und']}

    M = R.Memoria()
    s0 = M.d.sections[0]; s0.left_margin = s0.right_margin = Cm(2.0); s0.top_margin = Cm(2.3); s0.bottom_margin = Cm(1.2)
    V.C.SERVICIO = 'EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:'
    foto = V.foto(); V.escudo()
    V.caratula(M.d, foto, 'MEMORIA DESCRIPTIVA', D.ESPECIALIDAD)
    encabezado(M)
    R.indice(M)
    W = M.ancho

    # ================================================================== 1 GENERALIDADES
    M.t1('GENERALIDADES')
    M.t2('Introducción')
    M.par('La presente memoria descriptiva corresponde a la especialidad de arquitectura, en su componente de evacuación y '
          'señalización de seguridad, del expediente técnico a nivel de ejecución de obra del proyecto “%s”, con CUI N.° %s.' % (D.PROYECTO, D.CUI))
    M.par('Describe el planteamiento de evacuación (rutas, salidas, zonas seguras internas y zonas de reunión exteriores), la '
          'densidad de ocupación y el aforo, el cálculo de los medios de evacuación, la organización del centro para responder ante '
          'emergencias, los protocolos de actuación, los equipos de protección contra incendio y la señalización de seguridad de cada '
          'edificación, de acuerdo con las láminas SE-E-01 (plano de evacuación) y SE-S-01 (plano de señalización).')
    M.par('El planteamiento se rige por la seguridad integral de las personas que viven y trabajan en el centro, la accesibilidad '
          'universal y la atención a la condición de sus residentes: niños y adolescentes varones de 3 a 17 años que residen en el '
          'local de manera permanente y que, en una emergencia, dependen de la conducción del personal.')
    M.t2('Antecedentes y justificación técnica')
    M.par('El Centro de Acogida Residencial (CAR) es un servicio de protección especial que brinda alojamiento, alimentación, cuidado, '
          'educación y atención integral a niñas, niños y adolescentes sin cuidados parentales o en riesgo de perderlos, mientras se '
          'define su situación familiar. La región San Martín requiere un centro de acogida residencial para varones con '
          'infraestructura adecuada, segura y accesible.')
    M.par('En respuesta a esta necesidad, el Gobierno Regional San Martín, mediante la Gerencia Territorial Bajo Mayo - Tarapoto, ha '
          'impulsado el presente expediente técnico para la creación del CAR Varones, con ambientes de residencia organizados por '
          'grupos de edad (3 a 5 años, 6 a 11 años y dos módulos de 12 a 17 años), un módulo de madres sustitutas, administración con '
          'atención psicológica, social, legal y de salud, SUM y cocina, servicios higiénicos públicos, servicios generales y obras '
          'exteriores. Por funcionar las 24 horas, con residentes que duermen en el local, la seguridad ante sismos e incendios y la '
          'evacuación ordenada de los niños son condiciones de diseño y no solo de funcionamiento.')
    M.t2('Nombre del proyecto y CUI')
    M.par('“%s”.' % D.PROYECTO, neg=True)
    M.par('Código único de inversiones (CUI): N.° %s.' % D.CUI)
    M.t2('Ubicación')
    M.par('El CAR Varones se ubica en el predio rural Los Mangos, frente a la carretera Oasis, en el distrito de Morales, junto al '
          'Hogar de Refugio Temporal (CUI 2675514) y al CAR Mujeres (CUI 2717013):')
    tabla(M, 'Ubicación política y geográfica', ['COMPONENTE', 'UBICACIÓN / DENOMINACIÓN'], [
        ['Departamento / región', 'San Martín'], ['Provincia', 'San Martín'], ['Distrito', 'Morales'],
        ['Sector', 'Predio rural Los Mangos, frente a la carretera Oasis'],
        ['Coordenadas UTM (WGS 84, zona 18 S)', 'E %s, N %s (referenciales, centro del frente del predio)' % (
            format(UTM[0], ',').replace(',', ' '), format(UTM[1], ',').replace(',', ' '))],
        ['Altitud', '%.2f m s. n. m. (piso terminado del frente del predio)' % NPT_FRENTE]], [6.0, W - 6.0], izq=(0, 1))
    mapas = [(os.path.join(MAPAS, 'MAPA_PERU.jpg'), 'Perú'), (os.path.join(MAPAS, 'MAPA_REGION_SAN_MARTIN.jpg'), 'Región San Martín'),
             (os.path.join(MAPAS, 'MAPA_PROVINCIA_SAN_MARTIN.png'), 'Provincia de San Martín - distrito de Morales')]
    if all(os.path.exists(m) for m, _ in mapas):
        tabla(M, 'Mapas de ubicación', [t for _, t in mapas], [[('img', m, 4.6) for m, _ in mapas]], [W / 3] * 3,
              fuente_txt='Fuente: Cartografía referencial del expediente.')
    figura(M, foto, 'Vista del Centro de Acogida Residencial - Varones', 15.0, 'Fuente: Expediente técnico del proyecto.')
    M.t2('Accesibilidad y vías de conexión')
    M.par('El acceso al predio se realiza desde la ciudad de Tarapoto por vías asfaltadas y afirmadas hasta la carretera Oasis, frente '
          'a la cual están el ingreso principal y el ingreso al patio de maniobras del centro.')
    tabla(M, 'Vías de acceso', ['TRAMO', 'TIPO DE VÍA', 'DISTANCIA', 'TIEMPO', 'TRANSPORTE'], [
        ['Lima - Tarapoto', 'Vía aérea comercial', '620 km aprox.', '1 h 15 min', 'Avión comercial'],
        ['Tarapoto - Morales (carretera Oasis)', 'Terrestre asfaltada / afirmada', '5.0 km aprox.', '15 min', 'Vehículo motorizado / mototaxi']],
        [4.0, 3.8, 2.6, 2.2, W - 12.6], izq=(0,))
    M.par('La cercanía a la ciudad de Tarapoto permite la llegada del Cuerpo General de Bomberos Voluntarios, de la Policía Nacional y '
          'de las ambulancias en tiempos cortos; el ingreso al patio de maniobras permite el acceso de vehículos de emergencia.')
    M.t2('Objetivos')
    etiq(M, 'Objetivo general', 'Definir el planteamiento de evacuación, la señalización de seguridad y los medios de protección '
         'contra incendio del CAR Varones, de modo que todos los ocupantes puedan alcanzar un lugar seguro en forma ordenada, rápida y '
         'guiada ante un sismo, un incendio u otra emergencia.')
    etiq(M, 'Objetivos específicos (seguridad)', 'Diseñar las rutas de evacuación, las salidas y las zonas seguras internas y externas, '
         'y dimensionar los medios de evacuación según la Norma A.130.')
    etiq(M, 'Objetivos específicos (señalización)', 'Definir cada señal de seguridad (forma, color, pictograma, dimensiones, material, '
         'braille y altura) según la NTP 399.010-1 y la Norma A.120, y su ubicación en cada edificación.')
    etiq(M, 'Objetivos específicos (protección)', 'Dotar al centro de extintores, detección y alarma de incendio e iluminación de '
         'emergencia acordes con los peligros de cada ambiente.')
    etiq(M, 'Objetivos específicos (organización)', 'Establecer la organización del centro para emergencias (comité, brigadas y '
         'responsabilidades del personal) y los protocolos de actuación, con atención especial a los niños pequeños y al horario nocturno.')
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
              'Normas NFPA de referencia: NFPA 10 (extintores portátiles), NFPA 72 (detección y alarma de incendios) y NFPA 101 '
              '(código de seguridad humana).'])
    M.t2('Alcance y documentos')
    M.par('Comprende las diez edificaciones del centro (E-01 a E-10), las obras complementarias O.C. 01 a O.C. 04 y las obras '
          'exteriores O.E. 01 a O.E. 07. Las cantidades son las del metrado de evacuación y señalización y las características de '
          'cada partida se detallan en las especificaciones técnicas de la especialidad; las láminas, la memoria, el metrado y las '
          'especificaciones dicen lo mismo.')

    # ================================================================== 2 DESCRIPCIÓN DEL CENTRO
    M.t1('DESCRIPCIÓN DEL CENTRO DE ACOGIDA')
    M.t2('Características generales')
    M.par('El centro funciona en forma permanente, las 24 horas del día. Todas sus edificaciones son de un solo nivel, sin escaleras ni '
          'rampas en las rutas de evacuación: cada ambiente sale directamente a las circulaciones exteriores, a los patios y a las zonas '
          'de reunión. Las edificaciones se organizan alrededor del patio principal y de la losa deportiva, con el SUM y la cocina, la '
          'administración, los servicios higiénicos públicos y los servicios generales hacia el frente (carretera Oasis) y los módulos '
          'de residencia hacia el fondo del predio.')
    M.t2('Zonificación')
    M.par('La zonificación responde a las actividades del centro: residencia por grupos de edad, atención especializada y '
          'administración, alimentación y usos múltiples, servicios y obras exteriores.')
    tabla(M, 'Zonificación del centro', ['ZONA', 'EDIFICACIONES Y AMBIENTES', 'USUARIO DIRECTO'], [
        ['Zona administrativa y de atención especializada', 'E-01: dirección general, secretaría y sala de espera, sala de reuniones, '
         'trabajo social, asesoría legal, psicología, consultorio de nutrición, tópico, educador, monitoreo, data center y SS.HH.',
         'Director(a), personal administrativo, psicólogo(a), trabajador(a) social, abogado(a), nutricionista, visitantes autorizados'],
        ['Zona residencial', 'E-04 y E-05 (12 a 17 años), E-06 (3 a 5 años) y E-07 (6 a 11 años): dormitorios, closets, dormitorio de '
         'la madre, terraza o estar, oficina de entrevista, salón de estudios, taller de arte o salón de psicomotricidad, lavandería, '
         'almacén y SS.HH.; E-03: módulo de madres sustitutas', 'Niños y adolescentes residentes, madres sustitutas y educadores'],
        ['Zona de alimentación y usos múltiples', 'E-08: SUM y/o comedor, cocina, cuarto de gas, almacenes de cocina y de donaciones, '
         'lavandería de cocina, depósitos, residuos sólidos y SS.HH. de personal', 'Residentes, personal de cocina y todo el personal en '
         'actividades comunes'],
        ['Zona deportiva y recreativa', 'O.C. 02 losa deportiva, E-02 vestidores, O.C. 01 patio principal, O.C. 04 patio de juegos',
         'Residentes y personal'],
        ['Zona de servicios', 'E-09 SS.HH. público (hombres, mujeres y discapacitados); E-10 tablero general, subestación, grupo '
         'electrógeno, maestranza y cuarto de limpieza', 'Visitantes, personal de mantenimiento y técnicos'],
        ['Zona de obras exteriores', 'Cerco perimétrico e ingresos, caseta de control, tanque elevado y cisterna, pozo séptico, patio '
         'de maniobras, estacionamiento, área de sembríos y circulaciones', 'Personal de vigilancia y mantenimiento, proveedores, visitantes']],
        [3.6, W - 7.6, 4.0], tam=8.5, izq=(0, 1, 2))
    M.t2('Edificaciones y ambientes')
    M.par('Ambientes de cada edificación según la planta general de las láminas SE-S-01 y SE-E-01:')
    filas = []
    for cod, nombre in eds:
        if cod == 'EXT':
            continue
        nom = sorted(a.title().replace('Ss.Hh', 'SS.HH.').replace('Y/O', 'y/o').replace('W.C', 'W.C.') for a in amb.get(cod, {})
                     if a not in ('PASADIZO', 'CIRCULACION', 'CIRCULACIÓN', 'VEREDA', 'HALL', 'INGRESO'))
        filas.append([cod, nombre, ', '.join(nom)])
    tabla(M, 'Edificaciones y ambientes (planta general)', ['CÓDIGO', 'EDIFICACIÓN', 'AMBIENTES'], filas, [1.8, 4.2, W - 6.0], tam=8.5, izq=(1, 2))
    M.t2('Obras complementarias y exteriores')
    tabla(M, 'Obras complementarias y obras exteriores', ['CÓDIGO', 'TIPO', 'DESCRIPCIÓN'], [list(o) for o in OBRAS], [2.4, 3.6, W - 6.0], izq=(2,))

    # ================================================================== 3 COMPONENTES DEL PLAN
    M.t1('COMPONENTES DEL PLAN DE SEGURIDAD')
    M.t2('Métodos y procedimientos de mitigación de riesgos')
    M.par('Los métodos operacionales y espaciales del centro están orientados a prevenir, reducir y mitigar los riesgos que puedan '
          'afectar la integridad física y emocional de los residentes y del personal:')
    for et, t in (('Organización y uso de los espacios', 'residencia separada por grupos de edad, cada módulo con su salida directa a '
                   'las circulaciones exteriores y con la madre o el educador durmiendo en el mismo módulo.'),
                  ('Horarios y actividades', 'horarios de alimentación, estudio, talleres, deporte y descanso que eviten aglomeraciones y '
                   'mantengan libres los pasadizos, las salidas y las rutas de evacuación.'),
                  ('Condiciones físico-ambientales', 'ventilación e iluminación natural, protección contra la humedad y la lluvia, y '
                   'circulaciones exteriores techadas o con veredas de concreto antideslizantes.'),
                  ('Equipamiento y mobiliario', 'mobiliario estable y fijado a muros (closets, estantes y archivos), sin aristas '
                   'peligrosas, con materiales de buen comportamiento frente al fuego.'),
                  ('Seguridad y control de accesos', 'cerco perimétrico, caseta de control en el ingreso principal, registro de visitas '
                   'y reserva de la identidad de los residentes.'),
                  ('Prevención y respuesta ante emergencias', 'señalización de seguridad, extintores, detección y alarma, iluminación de '
                   'emergencia, rutas accesibles y simulacros periódicos, también nocturnos.'),
                  ('Protección de los residentes', 'conducción de los niños de 3 a 5 años por un adulto, atención a residentes con '
                   'discapacidad o movilidad reducida y acompañamiento emocional después de cada evento.')):
        etiq(M, et, t)
    M.t2('Identificación de peligros por edificación')
    M.par('A partir de los ambientes de cada edificación se identifican los peligros principales y las medidas de seguridad del proyecto:')
    tabla(M, 'Peligros y medidas por edificación', ['EDIFICACIÓN', 'AMBIENTES CRÍTICOS', 'PELIGRO PRINCIPAL', 'MEDIDAS DEL PROYECTO'],
          [list(x) for x in PELIGROS], [3.0, 3.8, 3.8, W - 10.6], tam=8, izq=(0, 1, 2, 3))
    M.t2('Planos del sistema de seguridad')
    vines(M, ['Lámina SE-E-01, plano de evacuación (escala 1/150): rutas de evacuación RUTA 01 a RUTA 13 con su longitud, zonas de '
              'reunión S1 a S13, aforo de cada ambiente e instrucciones en caso de evacuación.',
              'Lámina SE-S-01, plano de señalización (escala 1/150): ubicación de cada señal y equipo de seguridad en las diez '
              'edificaciones y en exteriores, con la leyenda de símbolos, alturas y cantidades.'])
    M.par('Forman parte de este plan el cálculo de aforo, el cálculo de los medios de evacuación, el metrado y las especificaciones '
          'técnicas de evacuación y señalización.')

    # ================================================================== 4 OCUPACIÓN Y AFORO
    M.t1('DENSIDAD DE OCUPACIÓN Y CÁLCULO DE AFORO')
    M.t2('Población del centro')
    M.par('La población permanente es de %d personas: %d residentes y %d personas de personal (%d madres sustitutas, %d de personal '
          'administrativo y %d de personal de apoyo). Se suman los usuarios temporales (visitas, familiares autorizados y personal '
          'eventual), %d personas, con lo que la capacidad máxima simultánea es de %d personas, igual al aforo del SUM, el ambiente de '
          'mayor capacidad, donde puede reunirse toda la población del centro.' % (
              Pb['permanentes'], Pb['residentes'], Pb['personal'], Pb['madres'], Pb['administrativos'], Pb['apoyo'], Pb['temporales'], Pb['maxima']))
    tabla(M, 'Población del centro', ['POBLACIÓN', 'DETALLE', 'PERSONAS'], [
        ['Personal', 'Madres sustitutas', Pb['madres']], ['Personal', 'Personal administrativo', Pb['administrativos']],
        ['Personal', 'Personal de apoyo', Pb['apoyo']], ['Personal', 'Subtotal', Pb['personal']],
        ['Residentes', 'Niños y adolescentes varones (cuatro módulos de 10)', Pb['residentes']],
        ['Permanentes', 'Personal + residentes', Pb['permanentes']], ['Temporales', 'Visitas y personal eventual', Pb['temporales']],
        ['CAPACIDAD MÁXIMA', 'Permanentes + temporales', Pb['maxima']]], [3.6, W - 6.0, 2.4], izq=(0, 1),
        colores={(7, 0): 'F2E6E8', (7, 1): 'F2E6E8', (7, 2): 'F2E6E8'})
    sub(M, 'Personal')
    M.par('Son las personas que permanecen en el centro en turnos de trabajo: madres sustitutas, educadores, personal administrativo, '
          'profesionales de atención (psicología, trabajo social, asesoría legal, nutrición y tópico) y personal de cocina, limpieza, '
          'mantenimiento y vigilancia. Conocen las instalaciones, las rutas y las zonas seguras y conducen la evacuación.')
    sub(M, 'Residentes')
    M.par('Niños y adolescentes varones de 3 a 17 años. Los menores de 6 años necesitan ser conducidos de la mano; los mayores siguen '
          'las indicaciones del personal. De noche se encuentran dormidos, por lo que la alarma y la iluminación de emergencia son '
          'esenciales.')
    sub(M, 'Personas ajenas al centro')
    M.par('Visitantes que permanecen poco tiempo (familiares autorizados, profesionales de instituciones vinculadas, proveedores) y '
          'que no necesariamente conocen los sistemas de seguridad: durante su visita están a cargo del personal que los recibe.')
    M.t2('Índices de ocupación')
    M.par('El aforo de cada ambiente se establece con los índices de ocupación del RNE (Normas A.090 y A.130) según su uso:')
    tabla(M, 'Índices de ocupación adoptados', ['AMBIENTE', 'NORMA DE REFERENCIA', 'ÍNDICE'], [
        ['Oficinas administrativas y de atención', 'RNE A.090', '10.0 m²/persona'],
        ['Dormitorios y residencia', 'RNE A.090, por analogía con albergues', '6.0 m²/persona*'],
        ['Sala de reuniones, SUM y comedor', 'RNE A.090', '1.0 m²/persona'],
        ['Talleres, salón de estudios y psicomotricidad', 'RNE A.090, uso semejante', '1.0 m²/persona*'],
        ['Cocina y áreas de servicio', 'RNE A.070, por analogía', '9.3 m²/persona*'],
        ['Almacenes y depósitos', 'RNE A.070, por analogía', '40.0 m²/persona*'],
        ['Vestidores y servicios higiénicos', 'Uso complementario', 'según aparatos*']], [6.0, W - 9.0, 3.0], izq=(0, 1))
    M.par('(*) Índice adoptado por analogía con un uso semejante, al no figurar el ambiente en forma expresa en la norma citada.', 9, cur=True)
    M.t2('Aforo por edificación')
    M.par('El aforo resultante de cada edificación figura en la lámina SE-E-01 y se publica en el letrero de aforo de su ingreso '
          '(%d letreros):' % q['LETRERO DE AFORO'])
    tabla(M, 'Aforo por edificación (lámina SE-E-01)', ['CÓDIGO', 'AMBIENTE', 'AFORO (personas)'],
          [[c, a, n] for c, a, n in D.aforos(P)], [2.4, W - 6.0, 3.6], izq=(1,))
    M.par('Los aforos de los módulos (11 personas: 10 residentes y la madre o el educador), del módulo de madres (5) y de la '
          'administración (11) coinciden con la población del centro; el SUM, con 66 personas, recibe a toda la población en las '
          'actividades comunes y define la capacidad máxima simultánea.')

    # ================================================================== 5 MEDIOS DE EVACUACIÓN
    M.t1('MEDIOS DE EVACUACIÓN')
    M.t2('Criterios de diseño')
    vines(M, ['Evacuación horizontal: todas las edificaciones son de un nivel y cada ambiente sale directamente al exterior.',
              'Las rutas se trazan por circulaciones exteriores y patios, sin cruzar zonas de riesgo (cocina, cuarto de gas, tanque '
              'elevado, servicios generales ni pozo séptico), y terminan en una zona de reunión exterior.',
              'El recorrido desde la puerta más alejada hasta la zona de reunión no supera %.0f m, distancia máxima de recorrido en '
              'edificaciones sin rociadores (Norma A.130).' % D.D_MAX,
              'Las puertas de los ambientes de mayor aforo (SUM, módulos y administración) abren en el sentido de la evacuación y no se '
              'cierran con llave mientras haya personas en el interior.',
              'Las rutas y salidas se señalizan con señales fotoluminiscentes y se iluminan con unidades de luces de emergencia.'])
    M.t2('Cálculo del ancho de puertas y pasajes')
    M.par('Según la Norma A.130, el ancho libre de los medios de evacuación se calcula multiplicando el número de ocupantes por 0.005 m, '
          'sin ser menor que los mínimos normativos: 0.90 m en puertas de evacuación (1.00 m en las de uso de personas con discapacidad, '
          'Norma A.120) y 1.20 m en pasajes de circulación (Norma A.010).')
    filas = []
    for cod, a, n in D.aforos(P):
        req = n * 0.005
        filas.append([cod, a, n, '%.3f' % req, '0.90', 'cumple: rige el mínimo'])
    tabla(M, 'Ancho requerido de las puertas de evacuación (Norma A.130)', ['CÓDIGO', 'AMBIENTE', 'AFORO', 'ANCHO CALC. (m)', 'MÍNIMO (m)', 'RESULTADO'],
          filas, [1.6, W - 11.0, 1.6, 2.6, 2.2, 3.0], tam=8.5, izq=(1,))
    M.par('En todos los casos el ancho calculado es menor que el mínimo normativo, por lo que rige este último: las puertas de '
          'evacuación tendrán un ancho libre no menor de 0.90 m (1.00 m en los servicios higiénicos accesibles y puertas principales '
          'según el cuadro de vanos de arquitectura) y los pasajes de circulación no menor de 1.20 m. El SUM, con 66 personas, '
          'requiere 0.33 m y cuenta con dos salidas.')
    M.t2('Rutas de evacuación')
    M.par('La lámina SE-E-01 define trece rutas de evacuación con su longitud, desde cada edificación hasta su zona de reunión:')
    tabla(M, 'Rutas de evacuación (lámina SE-E-01)', ['RUTA', 'AMBIENTE QUE EVACÚA', 'LONGITUD (m)', 'L ≤ 45 m'],
          [['RUTA %02d' % r['n'], r['ambiente'], '%.2f' % r['L'], 'cumple' if r['cumple'] else 'no cumple'] for r in rutas],
          [2.4, W - 7.8, 3.0, 2.4], izq=(1,))
    M.t2('Tiempos de evacuación')
    M.par('Conforme a la Norma A.130, el cálculo del tiempo de evacuación es referencial. El tiempo de desplazamiento se estima como la '
          'longitud de la ruta entre la velocidad de marcha: %.2f m/s para grupos con niños pequeños o personas con movilidad reducida '
          'y 1.00 m/s para adolescentes y adultos.' % D.V_EVAC)
    tabla(M, 'Tiempo de desplazamiento por ruta (referencial)', ['RUTA', 'AMBIENTE', 'L (m)', 't a %.2f m/s (s)' % D.V_EVAC, 't a 1.00 m/s (s)'],
          [['RUTA %02d' % r['n'], r['ambiente'], '%.2f' % r['L'], '%.0f' % (r['L'] / D.V_EVAC), '%.0f' % r['L']] for r in rutas],
          [2.2, W - 10.0, 2.2, 2.8, 2.8], izq=(1,))
    Lm = max(r['L'] for r in rutas)
    M.par('El recorrido más largo, %.2f m (ruta 03, SUM y cocina), se cubre en %.0f s con la velocidad más baja: toda la población puede '
          'alcanzar una zona de reunión exterior en poco más de un minuto desde que inicia la evacuación.' % (Lm, Lm / D.V_EVAC))
    M.t2('Zonas seguras internas')
    M.par('Dentro de los ambientes se señalizan %d zonas seguras en caso de sismo (junto a columnas y muros estructurales, lejos de '
          'ventanas y de mobiliario que pueda caer), para el repliegue durante el movimiento cuando no es posible salir de inmediato.' % q['ZONA SEGURA EN'])
    M.t2('Zonas de reunión exteriores')
    cap = math.pi * z['radio'] ** 2 / 0.5
    M.par('Al final de las rutas se ubican %d zonas de reunión S1 a S%d, pintadas en el piso de concreto como un círculo de %.2f m de radio '
          'con una línea de %.2f m de %s color amarillo, lejos de fachadas, cables, árboles y elementos que puedan caer. Cada círculo '
          'tiene %.2f m² de superficie, para unas %.0f personas a 0.50 m² por persona: en conjunto, %.0f personas, más del doble de la '
          'capacidad máxima del centro (%d).' % (len(zs), len(zs), z['radio'], z['ancho'], z['pintura'], math.pi * z['radio'] ** 2, cap,
                                               cap * len(zs), Pb['maxima']))
    tabla(M, 'Zonas de reunión exteriores (lámina SE-E-01)', ['ZONA', 'UBICACIÓN (edificación más cercana)', 'RADIO (m)', 'ÁREA (m²)'],
          [['S%d' % int(x['nombre'][1:]), x['cerca'], '%.2f' % z['radio'], '%.2f' % (math.pi * z['radio'] ** 2)] for x in zs],
          [1.8, W - 6.6, 2.2, 2.6], izq=(1,))
    figura(M, os.path.join(FIG, 'SE-E-01.png'), 'Plano de evacuación (lámina SE-E-01)', 16.0,
           'Fuente: Lámina SE-E-01 del expediente de arquitectura (evacuación y señalización).')

    # ================================================================== 6 ORGANIZACIÓN PARA EMERGENCIAS
    M.t1('ORGANIZACIÓN PARA EMERGENCIAS')
    M.t2('Alcances')
    M.par('La dirección y el personal del CAR están organizados para prevenir, responder y actuar de manera oportuna ante emergencias que '
          'pongan en peligro la vida, la integridad física y la salud de los residentes, del personal y de los visitantes, y para proteger '
          'la infraestructura, los bienes y el entorno del centro. Para ello se conforma un Comité de Seguridad y se organizan brigadas de '
          'emergencia, responsables de las acciones preventivas y de respuesta del Plan de Contingencia.')
    M.par('Por la naturaleza del servicio, las acciones de emergencia se desarrollan con un enfoque de protección de la niñez y '
          'atención sensible al trauma: se evita exponer a los residentes a situaciones de riesgo o de revictimización y se protege la '
          'reserva de su identidad. Como el centro funciona las 24 horas, en cada turno, incluido el nocturno, debe haber personal '
          'capacitado de cada brigada.')
    M.par('Las emergencias que podrían presentarse se clasifican según su origen:')
    etiq(M, 'Naturales', 'sismos, lluvias intensas, inundaciones, vientos fuertes y descargas eléctricas atmosféricas.')
    etiq(M, 'Tecnológicas o antrópicas', 'incendios, cortocircuitos, fugas de gas en la cocina, fallas de las instalaciones eléctricas y '
         'sanitarias, accidentes e intoxicaciones.')
    etiq(M, 'Sociales y de seguridad', 'intentos de ingreso no autorizado, fuga de residentes, amenazas externas o cualquier evento que '
         'comprometa la protección de los niños.')
    M.t2('Comité de Seguridad')
    M.par('Es responsable de formular, implementar, supervisar y actualizar el Plan de Contingencia del centro y de conformar, capacitar y '
          'supervisar las brigadas. Lo integran, según la organización del CAR:')
    etiq(M, 'Director(a) del CAR (director de emergencias)', 'dirige y coordina la respuesta, activa los protocolos y articula con los '
         'servicios externos de emergencia.')
    etiq(M, 'Responsable de mantenimiento y seguridad', 'verifica las condiciones de la infraestructura, las instalaciones y los equipos '
         'de emergencia y coordina su mantenimiento.')
    etiq(M, 'Coordinador(a) de madres sustitutas y educadores', 'coordina la protección y la conducción de los residentes de cada módulo '
         'durante la emergencia.')
    etiq(M, 'Jefe(a) de brigadas', 'organiza y supervisa las brigadas de lucha contra incendio, primeros auxilios y evacuación.')
    sub(M, 'Funciones del Comité de Seguridad')
    vines(M, ['Elaborar, difundir y actualizar el Plan de Contingencia del centro.',
              'Identificar y evaluar los peligros y riesgos que puedan afectar a los residentes, al personal, a la infraestructura y al entorno.',
              'Programar la capacitación del personal en prevención, evacuación, primeros auxilios, uso de extintores y conducción de niños.',
              'Organizar simulacros de evacuación (al menos dos al año, uno nocturno), evaluar sus resultados y aplicar las mejoras.',
              'Supervisar la señalización, las rutas de evacuación, las salidas, las zonas seguras y las condiciones de accesibilidad.',
              'Coordinar la inspección y el mantenimiento de los extintores, la central de alarma, los pulsadores, los avisadores, los '
              'detectores de humo y las luces de emergencia.',
              'Coordinar con el Cuerpo de Bomberos, los servicios de salud, la Policía Nacional, Defensa Civil y la municipalidad.',
              'Evaluar cada emergencia o simulacro, elaborar el informe y actualizar los procedimientos.',
              'Verificar que las medidas de seguridad se mantengan conforme a los planos aprobados para la Inspección Técnica de Seguridad '
              'en Edificaciones (ITSE).'])
    M.t2('Director de emergencias')
    M.par('Es el responsable de planificar las acciones para hacer frente a las emergencias e interviene antes, durante y después de un '
          'siniestro. Vela por que el centro cuente con el equipamiento operativo, por que las instalaciones estén acondicionadas y por '
          'que las brigadas estén conformadas por personal seleccionado y capacitado. Supervisa en forma permanente que:')
    vines(M, ['Todo el equipo contra incendio esté operativo (%d extintores, central de alarma, pulsadores y avisadores).' % (q['SEÑAL DE UBICACIÓN DE EXTINTOR PQS'] + q['SEÑAL DE UBICACIÓN DE EXTINTOR CO2']),
              'Los %d botiquines de primeros auxilios estén implementados.' % q['BOTIQUIN'],
              'Se disponga de radios portátiles, linternas y de las %d unidades de luces de emergencia en funcionamiento.' % q['UNIDAD DE LUCES'],
              'Los pasadizos, las salidas y las rutas permanezcan libres de obstáculos.',
              'El directorio telefónico de emergencia esté actualizado y a la vista en la administración, la caseta de control y cada módulo.'])
    M.t2('Encargado de mantenimiento y seguridad')
    M.par('Su labor es preventiva: asegura que el sistema de prevención y control de incendios esté plenamente operativo. Al activarse una '
          'alarma:')
    vines(M, ['Ordena el corte de energía eléctrica del área afectada y de las colindantes desde el tablero general (E-10).',
              'Cierra la llave general del gas de la cocina (E-08) si la emergencia lo requiere.',
              'Da aviso a todo el personal y moviliza a las brigadas al perímetro del evento.',
              'Facilita el acceso de los bomberos al predio por el ingreso del patio de maniobras y a las tomas de agua.',
              'Vela por que equipos, señales y condiciones del inmueble se mantengan conforme a los planos aprobados; cualquier cambio no '
              'autorizado invalida el certificado de ITSE y debe informarse por escrito a la dirección.'])
    M.t2('Brigadas de emergencia')
    M.par('Están conformadas por personal seleccionado por sus condiciones físicas y psicológicas y capacitado para actuar en siniestros. '
          'Cada brigada tiene un jefe, un subjefe (alterno, que lo reemplaza con las mismas funciones) y brigadistas, presentes en todos '
          'los turnos:')
    tabla(M, 'Brigadas de emergencia', ['BRIGADA', 'INTEGRANTES POR TURNO', 'EQUIPO', 'FUNCIONES PRINCIPALES'], [
        ['Contra incendios y de emergencia', 'Personal de mantenimiento, vigilancia y cocina', 'Extintores PQS y CO2, linterna, EPP',
         'Conocer tableros, llaves de gas y agua y extintores; atacar amagos de incendio; activar la alarma; ordenar la evacuación si la '
         'situación es crítica; transferir el mando a los bomberos.'],
        ['Logística y primeros auxilios', 'Personal del tópico, administrativo y de nutrición', 'Botiquines, camilla, directorio telefónico',
         'Brindar primeros auxilios; abastecer los botiquines; trasladar heridos graves; llamar a SAMU, bomberos y policía.'],
        ['Evacuación', 'Madres sustitutas, educadores y personal de cada módulo', 'Silbato, chaleco, linterna, lista de residentes',
         'Conducir a los residentes por las rutas a las zonas de reunión; abrir las puertas de salida; contar a los niños; verificar que '
         'nadie quede en los ambientes.']], [3.2, 3.6, 3.2, W - 10.0], tam=8.5, izq=(0, 1, 2, 3))
    sub(M, 'Jefe de brigada')
    vines(M, ['Comunicar de inmediato la emergencia al director de emergencias.', 'Verificar que los brigadistas estén capacitados y entrenados.',
              'Dirigir las acciones en el lugar de los hechos y coordinar con las demás brigadas.'])
    sub(M, 'Brigada de evacuación')
    vines(M, ['Conocer la distribución de los ambientes, las rutas, las zonas seguras internas y las zonas de reunión S1 a S13 de la lámina SE-E-01.',
              'Conducir primero a los niños de 3 a 5 años (E-06), tomados de la mano, y luego a los demás grupos.',
              'Llevar la lista de residentes de su módulo y hacer el conteo en la zona de reunión.',
              'Revisar dormitorios, servicios higiénicos y depósitos antes de salir y ser los últimos en abandonar el módulo.',
              'Contener emocionalmente a los niños durante y después de la evacuación.'])
    M.t2('Responsabilidades del personal')
    sub(M, 'Personal en general')
    vines(M, ['Cumplir y hacer cumplir las disposiciones de seguridad del Plan de Contingencia y del reglamento interno del centro.',
              'Velar por la integridad de los residentes, de sus compañeros y de los visitantes, y por el inmueble y su equipamiento.',
              'Actuar con eficiencia y calma en sismos, incendios u otras emergencias, según la brigada a la que pertenezcan.',
              'Controlar el ingreso y la salida de personas; no permitir la presencia de terceros no autorizados en los ambientes.'])
    sub(M, 'Personal en situaciones rutinarias')
    M.par('Todo el personal se comporta como observador de seguridad, informa los actos y condiciones inseguras y cumple estas disposiciones:')
    vines(M, ['No fumar en el centro.', 'No dejar equipos encendidos ni grifos abiertos cuando no se usan.',
              'No bloquear tableros eléctricos, extintores, pulsadores, avisadores, la central de alarma ni las señales de seguridad.',
              'No cerrar con llave ni trabar las puertas de salida mientras haya personas en el ambiente.',
              'No dejar muebles, bultos, maceteros ni materiales en pasadizos y rutas; fijar los armarios a la pared.',
              'No improvisar conexiones eléctricas ni usar extensiones o adaptadores múltiples.',
              'Mantener la cocina limpia de grasa y la válvula del gas cerrada al terminar la jornada.',
              'Conocer el Plan de Contingencia, las rutas de su área y el manejo de los extintores.'])

    # ================================================================== 7 PROTOCOLOS
    M.t1('PROTOCOLOS DE ACTUACIÓN')
    M.t2('Ante sismos')
    M.par('Objetivo: aplicar los procedimientos de seguridad antes, durante y después de un sismo en el CAR Varones.')
    sub(M, 'Antes (fase preventiva)')
    vines(M, ['Conocer el plano de evacuación, las zonas seguras internas, las salidas y las zonas de reunión de cada edificación.',
              'Fijar a los muros los closets, estantes, archiveros y equipos que puedan caer; no colocar objetos pesados en alto.',
              'Revisar los vidrios de puertas y ventanas; aplicar lámina de seguridad donde se requiera.',
              'Identificar la ubicación del tablero general, de la llave de agua y de la llave general del gas.',
              'Mantener libres pasadizos, circulaciones y salidas.', 'Realizar simulacros periódicos, también en horario nocturno.',
              'Tener a la vista el directorio de emergencias y una mochila de emergencia en cada módulo.'])
    sub(M, 'Durante (fase de respuesta)')
    vines(M, ['Mantener la calma y transmitir serenidad a los niños; la fase más intensa dura entre 20 y 40 segundos.',
              'Si no es posible salir de inmediato, replegarse en las zonas seguras internas señalizadas, lejos de ventanas.',
              'En exteriores, alejarse de fachadas, del cerco, de postes, del tanque elevado y de árboles.',
              'Despejar las vías para la acción de las brigadas.', 'Priorizar la autoprotección y la conducción de los niños pequeños.'])
    sub(M, 'Después (fase de rehabilitación)')
    vines(M, ['Esperar réplicas y mantenerse alerta.',
              'Evacuar por las rutas señaladas hacia las zonas de reunión, sin correr, sin empujar y sin gritar, bajo la dirección del '
              'director de emergencias.', 'Contar a los residentes y al personal en cada zona de reunión y reportar ausencias.',
              'Inspeccionar daños en estructuras, instalaciones eléctricas, sanitarias y de gas antes de reingresar.',
              'Reportar fugas, cortocircuitos o amagos de incendio; usar el teléfono solo para emergencias.',
              'Atender a los heridos y brindar contención emocional a los niños.'])
    M.t2('Ante incendios')
    M.par('Objetivo: establecer las pautas de prevención, control y respuesta ante un amago o fuego activo, salvaguardando a los residentes.')
    sub(M, 'Antes (fase preventiva)')
    vines(M, ['Vigilar calentamientos en tomacorrientes, interruptores y tableros; reportar olor a quemado.',
              'Almacenar productos de limpieza y combustibles en envases cerrados, en ambientes ventilados y bajo llave, fuera del alcance '
              'de los niños.', 'Mantener la cocina limpia de grasa, el cilindro y las mangueras del gas en buen estado y la válvula cerrada '
              'fuera de uso.', 'Mantener los extintores señalizados, cargados y libres de obstáculos.',
              'Prohibir velas, fósforos y encendedores en los módulos de residencia.'])
    sub(M, 'Durante (fase de respuesta)')
    vines(M, ['Activar la alarma con el pulsador más cercano y avisar a viva voz a los ambientes vecinos.',
              'Usar el extintor solo si el fuego es incipiente y se cuenta con capacitación, con la salida a la espalda.',
              'Cortar la energía eléctrica y cerrar la llave del gas.', 'Evacuar de inmediato los ambientes con humo; desplazarse agachado, '
              'cerca del piso, cubriendo nariz y boca con un paño húmedo.', 'Tocar las puertas con el dorso de la mano antes de abrirlas; si '
              'están calientes, no abrirlas.', 'No regresar por objetos personales; llamar al Cuerpo de Bomberos (116).',
              'Si se queda atrapado, cerrar la puerta, sellar las rendijas con trapos húmedos y hacerse ver desde la ventana.'])
    sub(M, 'Uso del extintor')
    vines(M, ['Retirar el pasador de seguridad.', 'Apuntar la boquilla a la base del fuego.', 'Presionar la manija.',
              'Barrer de lado a lado la base de las llamas hasta extinguirlas.',
              'En equipos eléctricos usar CO2 o PQS, nunca agua; en grasa de cocina no usar agua.'])
    sub(M, 'Después (fase de rehabilitación)')
    vines(M, ['No reingresar hasta que los bomberos o la autoridad competente lo autoricen.',
              'Colaborar con la inspección y el perímetro de seguridad.', 'Recargar los extintores usados y reponer lo consumido de los botiquines.',
              'Atender y acompañar a los afectados.'])
    M.t2('Ante lluvias intensas e inundaciones')
    vines(M, ['Mantener limpias las canaletas, montantes, cunetas y rejillas del drenaje pluvial antes de la temporada de lluvias.',
              'Ante tormentas eléctricas, suspender las actividades en la losa deportiva y los patios.',
              'Si el agua ingresa a un ambiente, cortar la energía de ese circuito y trasladar a los residentes a otra edificación.'])
    M.t2('Ante fuga de gas en la cocina')
    vines(M, ['Cerrar la válvula del cilindro y la llave general; no accionar interruptores ni encender fuego.',
              'Ventilar abriendo puertas y ventanas; evacuar la cocina y el SUM por las rutas 03, 04 y 05.',
              'Llamar a los bomberos si el olor persiste.'])
    M.t2('Ante corte de energía')
    vines(M, ['Las unidades de luces de emergencia se encienden automáticamente e iluminan las rutas y salidas.',
              'El personal de turno recorre los módulos con linterna y tranquiliza a los niños.',
              'El encargado de mantenimiento verifica el tablero general y el grupo electrógeno (E-10).'])

    # ================================================================== 8 PROCEDIMIENTO DE EVACUACIÓN
    M.t1('PROCEDIMIENTO DE EVACUACIÓN')
    M.t2('Fase de detección y alarma')
    M.par('Al detectar una emergencia (detector de humo, pulsador de alarma o aviso del personal), el director de emergencias evalúa la '
          'situación y dispone, según el caso:')
    vines(M, ['La evacuación inmediata, si hay peligro para los residentes y el personal.', 'La llamada a los bomberos y demás servicios de emergencia.',
              'Si hay heridos o atrapados, asegurar primero la evacuación de los demás ocupantes y luego, sin riesgos mayores, el rescate y la '
              'atención de las víctimas hasta la llegada de la ayuda externa.',
              'La neutralización de la emergencia con los medios del centro, si puede hacerse sin riesgo.'])
    M.t2('Desarrollo de la evacuación')
    vines(M, ['Evacuar con rapidez y orden, sin correr, sin gritar y sin provocar pánico.',
              'Seguir la ruta asignada a cada edificación en la lámina SE-E-01 hasta su zona de reunión; cambiarla solo si está bloqueada.',
              'Los niños de 3 a 5 años salen tomados de la mano de un adulto; los demás grupos, en fila detrás de su madre o educador.',
              'Si hay humo, salir agachados; si el fuego impide la salida por la puerta, salir por la ventana cuando sea seguro.',
              'Los responsables son los últimos en salir, después de revisar dormitorios, servicios higiénicos, depósitos y oficinas, y '
              'cierran las puertas al salir.', 'Controlar el tránsito de vehículos en el patio de maniobras y el estacionamiento.',
              'En la zona de reunión, contar a todos con la lista de residentes y de personal e informar de inmediato las ausencias.'])
    M.t2('Instrucciones en caso de evacuación (lámina SE-E-01)')
    vines(M, ['Mantenga la calma; no entre en pánico.', 'Avise inmediatamente de la emergencia a la persona responsable más cercana.',
              'No se entretenga recogiendo objetos personales.', 'En caso de incendio y humo intenso, gatee pegado a la pared.',
              'Siga la señalización de evacuación hasta las zonas seguras indicadas en el plano.', 'Por ninguna razón regrese al interior de la edificación.'])
    M.t2('Llamadas de emergencia')
    M.par('Asegurada la evacuación, se llama a los servicios de emergencia con calma y brevedad, indicando la ubicación exacta (CAR '
          'Varones, predio rural Los Mangos, frente a la carretera Oasis, Morales), las vías de acceso y lo ocurrido; a su llegada se les '
          'informa la situación y se colabora con ellos.')
    tabla(M, 'Directorio de emergencias', ['INSTITUCIÓN', 'TELÉFONO'], [[a, b] for a, b in DIRECTORIO], [W - 3.0, 3.0], izq=(0,))
    M.t2('Asistencia a heridos y neutralización')
    vines(M, ['Prestar primeros auxilios con los botiquines del centro hasta la llegada de la ayuda externa y gestionar el traslado al '
              'establecimiento de salud más cercano.', 'Desconectar la energía, retirar materiales combustibles y no ingresar a recintos con fuego.',
              'En caso de electrocución, cortar la corriente antes de tocar al afectado; si no respira, iniciar la reanimación cardiopulmonar.',
              'Si se prenden las ropas de una persona, impedir que corra, hacerla rodar en el suelo o cubrirla con una manta.'])
    M.t2('Fin de la emergencia')
    M.par('Neutralizada la emergencia y con autorización de la ayuda externa, se evalúan los daños, se restablecen las actividades, se '
          'investigan las causas y se proponen medidas correctivas; el Comité de Seguridad registra lo actuado y actualiza el plan.')

    # ================================================================== 9 PROTECCIÓN CONTRA INCENDIO
    M.t1('PROTECCIÓN CONTRA INCENDIO Y EMERGENCIA')
    pq = por['SEÑAL DE UBICACIÓN DE EXTINTOR PQS']; co = por['SEÑAL DE UBICACIÓN DE EXTINTOR CO2']
    M.t2('Extintores portátiles')
    M.par('Se instalan %d extintores de polvo químico seco (PQS) multipropósito tipo ABC de 6 kg y %d extintores de dióxido de carbono '
          '(CO2) de 10 lb, estos en la cocina del SUM (E-08) para fuegos de clase B y C de sus equipos. Cada extintor se cuelga en su '
          'soporte con la parte superior a no más de 1.50 m del piso, visible, de libre acceso, con su señal encima y su tarjeta de '
          'control, y se selecciona, inspecciona y recarga según la NTP 350.043-1.' % (pq['total'], co['total']))
    filas = [[c, n, pq['por'].get(c, 0) or '—', co['por'].get(c, 0) or '—'] for c, n in eds if pq['por'].get(c) or co['por'].get(c)]
    filas.append(['TOTAL', '', pq['total'], co['total']])
    tabla(M, 'Distribución de extintores (lámina SE-S-01)', ['CÓDIGO', 'EDIFICACIÓN', 'PQS 6 kg', 'CO2 10 lb'], filas,
          [2.0, W - 7.0, 2.5, 2.5], izq=(1,), colores={(len(filas) - 1, k): 'F2E6E8' for k in range(4)})
    M.t2('Detección y alarma')
    M.par('El sistema tiene %d detectores de humo fotoeléctricos de techo, %d estaciones manuales de alarma (pulsadores), %d avisadores '
          'sonoros y una central de alarma contra incendio en la administración (E-01). Los detectores cubren los dormitorios y los '
          'ambientes de los módulos, de modo que un incendio nocturno se detecte en su inicio. La alimentación, el cableado y las pruebas '
          'del sistema son de instalaciones eléctricas.' % (q['DETECTOR DE HUMO'], q['ALARMA CONTRA'], q['AVISADOR SONORO']))
    M.t2('Iluminación de emergencia')
    M.par('Se instalan %d unidades de luces de emergencia autónomas a 2.10 m del piso, en salidas, circulaciones y ambientes, con '
          'autonomía mínima de 90 minutos y encendido automático al cortarse la energía (Norma A.130).' % q['UNIDAD DE LUCES'])
    M.t2('Primeros auxilios y residuos')
    M.par('Se señalizan %d botiquines de primeros auxilios en todas las edificaciones y %d puntos ecológicos para el acopio selectivo '
          'de residuos sólidos.' % (q['BOTIQUIN'], q['PUNTO ECOL']))

    # ================================================================== 10 SEÑALIZACIÓN
    M.t1('SEÑALIZACIÓN DE SEGURIDAD')
    M.t2('Definición y clasificación')
    M.par('Señal de seguridad es la que, por la combinación de una forma geométrica y un color, proporciona una indicación general '
          'relativa a la seguridad y que, con un símbolo gráfico o un texto, proporciona una indicación particular. Según la NTP '
          '399.010-1 se clasifican en:')
    etiq(M, 'Señales de evacuación y emergencia', 'indican la vía segura hacia las salidas y las zonas seguras y la ubicación de los '
         'equipos de emergencia (primeros auxilios). Color verde, forma cuadrada o rectangular.')
    etiq(M, 'Señales de equipos contra incendio', 'ubican e identifican los equipos de protección contra incendio (extintores, alarmas, '
         'avisadores, central). Color rojo, forma cuadrada o rectangular.')
    etiq(M, 'Señales de advertencia', 'advierten un peligro (riesgo eléctrico, descarga eléctrica). Color amarillo, forma triangular con '
         'borde negro.')
    etiq(M, 'Señales de prohibición', 'prohíben una acción que puede provocar un accidente. Círculo con banda diagonal rojos sobre fondo blanco.')
    etiq(M, 'Señales informativas', 'informan sobre servicios e instalaciones (servicios higiénicos, punto ecológico, aforo). Color azul o verde.')
    tabla(M, 'Formas y colores de seguridad (NTP 399.010-1)', ['TIPO', 'FORMA', 'COLOR DE SEGURIDAD', 'CONTRASTE', 'PICTOGRAMA', 'EJEMPLOS DEL PROYECTO'], [
        ['Evacuación y emergencia', 'Cuadrado / rectángulo', 'Verde', 'Blanco', 'Blanco', 'Salida, zona segura, botiquín, punto ecológico'],
        ['Equipos contra incendio', 'Cuadrado / rectángulo', 'Rojo', 'Blanco', 'Blanco', 'Extintor PQS y CO2, alarma, avisador, central'],
        ['Advertencia', 'Triángulo equilátero', 'Amarillo', 'Negro', 'Negro', 'Riesgo eléctrico, riesgo de descarga'],
        ['Prohibición', 'Círculo con diagonal', 'Rojo', 'Blanco', 'Negro', 'Prohibido el ingreso'],
        ['Información', 'Cuadrado / rectángulo', 'Azul', 'Blanco', 'Blanco', 'SS.HH., aforo']],
        [3.0, 2.6, 2.2, 1.8, 2.0, W - 11.6], tam=8, izq=(0, 5),
        colores={(0, 2): '00874B', (1, 2): 'CC141E', (2, 2): 'FFCD00', (3, 2): 'CC141E', (4, 2): '004696'})
    M.t2('Criterios de instalación')
    vines(M, ['Las señales de evacuación y de equipos contra incendio son fotoluminiscentes, para que se vean sin energía eléctrica.',
              'Todas las señales llevan una placa de acrílico con su texto en braille (Norma A.120), que reproduce la leyenda de la señal.',
              'La altura de instalación se mide desde el piso terminado hasta el borde inferior de la señal; la señal de extintor va encima '
              'del equipo, a 1.80 m, visible por sobre el extintor.',
              'Las señales se instalan sobre superficies terminadas, firmes y niveladas, y no deben quedar tapadas por puertas abiertas, '
              'muebles ni equipos.'])
    M.t2('Descripción de la simbología utilizada en el proyecto')
    M.par('La simbología es la de la leyenda de la lámina SE-S-01. Cada señal se muestra tal como se fabrica (forma, color, pictograma, '
          'texto y placa en braille), con su cantidad, que coincide con la dibujada en la planta:')
    filas = []
    for p in pts:
        if not p['und']:
            continue
        filas.append([('img', img[p['item']], 1.9), p['desc'].replace(' CON BRAILLE', '').capitalize(), p['uso'], p['dim'], p['altura'], p['total']])
    tabla(M, 'Simbología del proyecto (leyenda de la lámina SE-S-01)', ['SEÑAL', 'DENOMINACIÓN', 'DESCRIPCIÓN', 'DIMENSIONES', 'ALTURA', 'CANT.'],
          filas, [2.3, 3.4, W - 10.9, 2.3, 1.7, 1.2], tam=8, izq=(1, 2))
    M.t2('Ficha de cada señal')
    M.par('Para la fabricación, la instalación y la supervisión, cada señal y equipo tiene su ficha con la función, las dimensiones, el '
          'material, la altura, la cantidad y las edificaciones donde se ubica (E-01 a E-10; EXT = exteriores):')
    for p in pts:
        if p['und'] is None:
            sub(M, '01.%s  %s' % (p['item'], p['desc'].capitalize()))
            continue
        ficha(M, p, img[p['item']])
    M.t2('Distribución por edificación')
    cols = [('SALIDA', 'Salida'), ('ZONA SEGURA EN', 'Zona segura'), ('LETRERO DE AFORO', 'Aforo'), ('ALARMA CONTRA', 'Alarma'),
            ('BOTIQUIN', 'Botiquín'), ('SEÑALES DE SERVICIOS', 'SS.HH.'), ('UNIDAD DE LUCES', 'Luces'), ('DETECTOR DE HUMO', 'Detector')]
    filas = []
    for cod, nombre in eds:
        fila = [cod]
        for clave, _ in cols:
            n = sum(por[k]['por'].get(cod, 0) for k in por if k.startswith(clave))
            fila.append(n or '—')
        filas.append(fila)
    filas.append(['TOTAL'] + [sum(f[k] for f in filas if f[k] != '—') for k in range(1, len(cols) + 1)])
    tabla(M, 'Señales y equipos principales por edificación (planta de SE-S-01)', ['EDIF.'] + [c[1] for c in cols], filas,
          [1.6] + [(W - 1.6) / len(cols)] * len(cols), tam=8.5, colores={(len(filas) - 1, k): 'F2E6E8' for k in range(len(cols) + 1)})
    M.par('El detalle de todas las partidas por edificación está en la hoja METRADO del metrado de evacuación y señalización.')
    figura(M, os.path.join(FIG, 'SE-S-01.png'), 'Plano de señalización (lámina SE-S-01)', 16.0,
           'Fuente: Lámina SE-S-01 del expediente de arquitectura (evacuación y señalización).')

    # ================================================================== 11 MANTENIMIENTO
    M.t1('MANTENIMIENTO, INSPECCIÓN Y SIMULACROS')
    tabla(M, 'Programa de inspección y mantenimiento', ['ELEMENTO', 'ACTIVIDAD', 'FRECUENCIA', 'RESPONSABLE'], [
        ['Extintores', 'Inspección visual (presión, precinto, acceso, tarjeta)', 'Mensual', 'Mantenimiento y seguridad'],
        ['Extintores', 'Mantenimiento y recarga por empresa certificada', 'Anual o después de cada uso', 'Dirección'],
        ['Luces de emergencia', 'Prueba de encendido y autonomía', 'Mensual / semestral (90 min)', 'Mantenimiento'],
        ['Detectores, pulsadores, avisadores y central', 'Prueba funcional y limpieza', 'Trimestral', 'Mantenimiento'],
        ['Señales de seguridad', 'Verificación de estado, fijación y fotoluminiscencia', 'Semestral', 'Comité de Seguridad'],
        ['Zonas de reunión pintadas', 'Repintado', 'Anual o cuando pierdan visibilidad', 'Mantenimiento'],
        ['Botiquines', 'Reposición de insumos y control de vencimientos', 'Mensual', 'Brigada de primeros auxilios'],
        ['Instalación de gas de la cocina', 'Revisión de mangueras, reguladores y válvulas', 'Mensual', 'Mantenimiento'],
        ['Simulacros de evacuación', 'Simulacro diurno y nocturno con registro de tiempos', 'Semestral', 'Comité de Seguridad']],
        [3.6, W - 10.6, 3.6, 3.4], tam=8.5, izq=(0, 1, 2, 3))

    # ================================================================== 12 CONCLUSIONES
    M.t1('CONCLUSIONES Y RECOMENDACIONES')
    vines(M, ['Todas las edificaciones del CAR Varones son de un nivel y evacúan en forma horizontal y directa al exterior; las trece rutas '
              'de evacuación tienen entre %.2f y %.2f m, por debajo del máximo de 45 m de la Norma A.130.' % (min(r['L'] for r in rutas), Lm),
              'Las %d zonas de reunión exteriores (S1 a S13) tienen capacidad para más del doble de la capacidad máxima del centro (%d personas).' % (len(zs), Pb['maxima']),
              'Los anchos de puertas y pasajes están gobernados por los mínimos normativos (0.90 m y 1.20 m), mayores que los requeridos por aforo.',
              'El proyecto cuenta con %d señales de seguridad con braille, %d extintores, %d detectores de humo, %d unidades de luces de '
              'emergencia y un sistema de alarma con central, pulsadores y avisadores, distribuidos según la lámina SE-S-01.' % (
                  sum(p['total'] for p in pts if p['und'] and p['item'][:2] in ('01', '02', '03', '04') and not p['desc'].startswith('ZONA DE REUNI')),
                  pq['total'] + co['total'], q['DETECTOR DE HUMO'], q['UNIDAD DE LUCES']),
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
    M.d.core_properties.author = ''; M.d.core_properties.title = 'Memoria descriptiva - Evacuación y señalización - CAR Varones'
    M.d.save(SALIDA)
    return SALIDA


if __name__ == '__main__':
    print(generar())
