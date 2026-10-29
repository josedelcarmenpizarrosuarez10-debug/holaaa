# -*- coding: utf-8 -*-
"""Especificaciones técnicas de equipamiento y mobiliario - Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514).

Motor y formato de las especificaciones del expediente (JSON -> herramientas/especificaciones/docx_espec.js). Partidas,
numeración, descripción y cantidades = las del metrado (datos_mr.numerar); características por familia = fichas_mr (las mismas
de la memoria descriptiva). Cada ficha indica los ambientes donde va la partida, según las láminas EM-01 a EM-07.

Uso: python3 herramientas/mobiliario_refugio/espec_mr.py
Salida: entregables/ESPECIFICACIONES_TECNICAS_EQUIPAMIENTO_Y_MOBILIARIO_HOGAR_REFUGIO.docx
"""
import json
import os
import subprocess
import sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI)
for d in (AQUI, HER):
    sys.path.insert(0, d)
import datos_mr as D  # noqa: E402
import fichas_mr as F  # noqa: E402
import caratulas_refugio as CR  # noqa: E402  (foto y leyenda del Hogar de Refugio)

V = CR.V
ESP = os.path.join(HER, 'especificaciones')
JSON = os.path.join(ESP, '_json', 'refugio_mobiliario.json')
SALIDA = os.path.join(D.SAL, 'ESPECIFICACIONES_TECNICAS_EQUIPAMIENTO_Y_MOBILIARIO_HOGAR_REFUGIO.docx')
NORMAS = ['Ley N.° 30364, Ley para prevenir, sancionar y erradicar la violencia contra las mujeres y los integrantes del grupo familiar, '
          'y su Reglamento (D.S. N.° 009-2016-MIMP).',
          'R.M. N.° 150-2016-MIMP, Lineamientos para la atención y funcionamiento de los Hogares de Refugio Temporal.',
          'Reglamento Nacional de Edificaciones: Normas A.010, A.090, A.120, A.130, EM.010 y G.050.',
          'NTP 900.058 (código de colores para el almacenamiento de residuos sólidos); registro sanitario DIGEMID para los implementos '
          'médicos del tópico.']


def p(t): return ['p', t]
def l(*it): return ['l', list(it)]
def t(cab, filas, pesos=None): return ['t', cab, filas] + ([pesos] if pesos else [])


EPP = 'Uso de equipo de protección personal durante el armado y la instalación: casco, guantes y calzado de seguridad (Norma G.050).'


def ubicaciones():
    u = defaultdict(list)
    for ed, amb, its in D.ambientes():
        for it in its:
            u[it['clave']].append('%s %s (%d)' % (ed, D.cap(amb), it['cant']))
    return u


def ficha(f, fam, donde):
    x = F.FAMILIAS[fam]
    desc = [p('Comprende el suministro%s de %s, con las características de esta especificación, en los ambientes indicados en las '
              'láminas EM-01 a EM-07. Cantidad del metrado: %d und.' % (
                  '' if fam == 'implemento' else ', el transporte, el armado y la instalación', f['desc'].lower(), f['total'])),
            p('Ubicación: ' + '; '.join(donde) + '.')]
    ctrl = x['ctrl'] + ['El contratista presentará la ficha técnica o una muestra para la aprobación de la Supervisión antes de la '
                        'compra o la fabricación.']
    return [['DESCRIPCIÓN', desc], ['MATERIALES Y CARACTERÍSTICAS', [l(*x['mat'])]],
            ['PROCEDIMIENTO DE SUMINISTRO E INSTALACIÓN', [l(*x['proc'])]], ['CONTROL DE CALIDAD', [l(*ctrl)]],
            ['SEGURIDAD Y SALUD EN EL TRABAJO', [l(EPP)]],
            ['UNIDAD DE MEDIDA', [p('La unidad de medida es la unidad (und).')]],
            ['MÉTODO DE MEDICIÓN', [p('Se contará el número de unidades suministradas, instaladas y recibidas a satisfacción de la '
                                      'Supervisión, según el equipamiento de cada ambiente de las láminas EM-01 a EM-07.')]],
            ['FORMA DE PAGO', [p('El pago se efectuará al precio unitario del presupuesto por unidad (und), de acuerdo con el avance '
                                 'valorizado y con la conformidad de la Supervisión. Dicho precio constituye compensación total por el '
                                 'suministro, el transporte, el armado, la instalación, las pruebas y todo imprevisto necesario para '
                                 'entregar la partida en funcionamiento.')]]]


def generalidades(N):
    filas = [[f['item'], ('%s  ' % f['cod'] if f.get('cod') else '') + f['desc'], 'und', str(f['total'])] for f in N if f.get('tipo') == 'item']
    return [
        ['GENERALIDADES', [p('Las presentes especificaciones técnicas definen las características, el suministro, la instalación, el '
                             'control, la medición y el pago de los equipos, el mobiliario y los implementos del proyecto “%s”, con CUI '
                             'N.° %s.' % (D.PROYECTO, D.CUI)),
                           p('Las partidas, su numeración y sus cantidades son las del metrado de equipamiento y mobiliario; su ubicación, '
                             'la de las láminas EM-01 a EM-07. La memoria descriptiva, las láminas y el metrado forman parte de este '
                             'documento.')]],
        ['CONDICIONES GENERALES', [l('Todos los equipos y muebles serán nuevos, de primera calidad y con garantía del fabricante.',
                                     'Antes de la compra o la fabricación, el contratista presentará fichas técnicas, catálogos o muestras '
                                     'para la aprobación de la Supervisión; las características indicadas son mínimas y pueden ser superadas.',
                                     'Los muebles de más de 1.20 m de altura (armarios, estantes, archivadores) y los camarotes se fijarán a '
                                     'la pared para evitar su volteo en un sismo.',
                                     'Cantos redondeados, sin aristas ni elementos cortantes; materiales no tóxicos y lavables, resistentes a '
                                     'la humedad del clima cálido y húmedo de Morales.',
                                     'La entrega se hará por ambiente, con acta (código, cantidad, estado y número de serie de los equipos), '
                                     'manuales y garantías.')]],
        ['NORMAS APLICABLES', [l(*NORMAS)]],
        ['PARTIDAS Y CANTIDADES', [p('Partidas del metrado de equipamiento y mobiliario:'),
                                   t(['ITEM', 'DESCRIPCIÓN', 'UND', 'CANT.'], filas, [16, 66, 8, 10])]],
    ]


def construir():
    N = D.numerar(); u = ubicaciones()
    partidas = []
    for f in N:
        it = dict(codigo=f['item'], desc=(('%s  ' % f['cod']) if f.get('cod') else '') + f['desc'],
                  und='und' if f.get('tipo') == 'item' else '', nivel=min(f['nivel'], 4))
        if f.get('tipo') == 'item':
            it['secciones'] = ficha(f, F.familia(f['clave']), u[f['clave']])
        partidas.append(it)
    from PIL import Image
    img = V.foto(); w, h = Image.open(img).size
    doc = dict(proyecto=D.PROYECTO, cui=D.CUI, corto=D.CORTO, entidad='GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO',
               especialidad=D.ESPECIALIDAD, ubicacion='SAN MARTÍN - SAN MARTÍN - MORALES', fecha=D.FECHA,
               cabecera='ESPECIFICACIONES TÉCNICAS - EQUIPAMIENTO Y MOBILIARIO',
               titulo_doc='Especificaciones técnicas - Equipamiento y mobiliario',
               caratula=dict(entidad='GOBIERNO REGIONAL SAN MARTÍN', gerencia='GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO',
                             expediente='EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:', proyecto='“%s”' % D.PROYECTO,
                             ci='CUI N.° %s' % D.CUI, foto=img, proporcion=h / w, leyenda=V.LEYENDA, titulo='ESPECIFICACIONES TÉCNICAS',
                             subtitulo='EQUIPAMIENTO Y MOBILIARIO', especialidad='ESPECIALIDAD: ' + D.ESPECIALIDAD,
                             ubicacion=D.UBICACION, fecha=D.FECHA),
               generalidades=generalidades(N), partidas=partidas)
    os.makedirs(os.path.dirname(JSON), exist_ok=True)
    json.dump(doc, open(JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    subprocess.run(['node', os.path.join(ESP, 'docx_espec.js'), JSON, SALIDA], check=True, cwd=ESP)
    import indice_word
    indice_word.llenar([SALIDA])                                # índice lleno para imprimir
    return SALIDA


if __name__ == '__main__':
    print(construir())
