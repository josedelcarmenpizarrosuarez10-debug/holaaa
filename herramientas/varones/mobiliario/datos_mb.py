# -*- coding: utf-8 -*-
"""Datos de equipamiento y mobiliario del CAR Varones (CUI 2705619): fuente única del metrado, la memoria y las especificaciones.

Cantidades adoptadas = los cuadros de equipamiento de cada ambiente del plano (láminas MB-01 a MB-09, lee_plano_mb.py),
contrastados con lo dibujado y etiquetado en la planta de cada edificación. Donde el cuadro y el dibujo no coinciden por un
error evidente de copia del cuadro, se corrige con lo dibujado (CORRECCIONES, cada una con su motivo). Descripciones: las del
plano; donde el cuadro trae la descripción de otro código, la del código (DESCRIPCIONES).

El metrado original del usuario (insumos/katiuska/mobiliario/..._ORIGINAL.xlsx, hoja HR) solo se lee para compararlo.
"""
import json
import os
import re
from collections import Counter, OrderedDict, defaultdict

import openpyxl

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(AQUI)))
PLANO = os.path.join(RAIZ, 'entregables_varones/_calc/mobiliario_plano.json')
ORIGINAL = os.path.join(RAIZ, 'insumos/katiuska/mobiliario/METRADO_MOBILIARIOS_EQUIPAMIENTO_CAR_VARONES_ORIGINAL.xlsx')
SAL = os.path.join(RAIZ, 'entregables_varones')

PROYECTO = ('CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE '
            'PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES DISTRITO DE MORALES DE LA PROVINCIA DE SAN MARTÍN DEL DEPARTAMENTO '
            'DE SAN MARTÍN')
CUI = '2705619'
CORTO = 'CAR VARONES'
ESPECIALIDAD = 'ARQUITECTURA - EQUIPAMIENTO Y MOBILIARIO'
UBICACION = 'Distrito de Morales, provincia y departamento de San Martín'
FECHA = 'SETIEMBRE 2026'

EDIFICACIONES = OrderedDict([('E-01', 'Administración'), ('E-02', 'Vestidores y almacén de implementos deportivos'),
                             ('E-03', 'Módulo de madres sustitutas'), ('E-04', 'Vivienda de niños de 12 a 17 años (1)'),
                             ('E-05', 'Vivienda de niños de 12 a 17 años (2)'), ('E-06', 'Vivienda de niños de 3 a 5 años'),
                             ('E-07', 'Vivienda de niños de 6 a 11 años'), ('E-08', 'Sala de usos múltiples, comedor y cocina'),
                             ('E-09', 'Servicios higiénicos públicos'), ('E-10', 'Servicios generales')])

# títulos de cuadro mal rotulados en el plano: (edificación del título, ambiente del título, x del cuadro) -> (edificación, ambiente)
RETITULOS = {('E-06', 'OFICINA DE ENTREVISTA Y ESTAR', 2756.693): ('E-08', 'ALMACÉN DE COCINA Y CUARTO DE GAS'),
             ('E-02', 'TOPICO', 2601.457): ('E-02', 'ALMACÉN DE IMPLEMENTOS DEPORTIVOS')}

# correcciones de cantidad: (edificación, ambiente contiene, código) -> (cantidad, motivo)
CORRECCIONES = [
    ('E-01', 'TOPICO', 'E7', 0, 'El cuadro del tópico repite el de la sala de reuniones (proyector y 10 sillas); en la planta de E-01 hay 2 '
                               'proyectores (nutrición y sala de reuniones) y 38 sillas M07, no 41.'),
    ('E-01', 'TOPICO', 'M7', 7, 'Ídem: se ajusta el tópico para que E-01 sume las 38 sillas M07 dibujadas.'),
    ('E-04', 'DORMITORIO MADRE', 'E6', 1, 'El cuadro repite las 5 computadoras del salón de estudios; en la planta hay 1 (escritorio de la madre).'),
    ('E-05', 'DORMITORIO MADRE', 'E6', 1, 'Ídem E-04.'),
    ('E-06', 'DORMITORIO MADRE', 'E6', 1, 'Ídem E-04.'),
    ('E-07', 'DORMITORIO MADRE', 'E6', 1, 'Ídem E-04.'),
    ('E-04', 'OFICINA DE ENTREVISTA', 'M34', 2, 'En la planta hay 2 sofás de 2 cuerpos (M34) en la oficina de entrevista y estar; el cuadro dice 1.'),
    ('E-05', 'OFICINA DE ENTREVISTA', 'M34', 2, 'Ídem E-04.'),
    ('E-06', 'OFICINA DE ENTREVISTA', 'M34', 2, 'Ídem E-04.'),
    ('E-07', 'OFICINA DE ENTREVISTA', 'M34', 2, 'Ídem E-04.'),
    ('E-07', 'TALLER DE ARTE', 'M56', 5, 'En la planta hay 5 muebles para mochilas (M56); el cuadro dice 1.'),
    ('E-08', 'LAVANDER', 'M42', 4, 'En la planta hay 4 casilleros (M42); el cuadro dice 7.'),
    ('E-08', 'LAVANDER', 'S1', 0, 'Los extintores son partida de evacuación y señalización (lámina SE-S-01), no de mobiliario.'),
    ('E-08', 'SUM', 'S1', 0, 'Ídem.'),
    ('E-10', 'MAESTRANZA', 'M75', 2, 'En la planta hay 2 contenedores (M75); el cuadro dice 4.'),
    ('E-07', 'DORMITORIO', 'M37', 0, 'En la planta del dormitorio de E-07 los muebles junto a cada cama están rotulados M44 (credenza), '
                                    '10 en total; el cuadro dice 10 armarios M37. Se cuenta lo rotulado en planta.'),
]
AGREGADOS = [('E-08', 'SUM/COMEDOR - DEPÓSITO', 'M73', 1, 'MOBILIARIO', 'La estación de servido (M73) está dibujada en el comedor y no figura en su cuadro.'),
             ('E-07', 'DORMITORIO', 'M44', 10, 'MOBILIARIO', 'Credenzas M44 rotuladas en la planta del dormitorio de E-07 (una junto a cada cama); '
                                                            'no figuran en el cuadro, que pone armarios M37.'),
             ('E-01', 'SECRETARIA/SALA DE ESPERA', 'M62', 1, 'MOBILIARIO', 'La planta de E-01 tiene 11 cestos M62 rotulados y los cuadros suman 10; '
                                                                          'el cuadro de secretaría y sala de espera no trae cesto.')]

# descripción correcta del código cuando el cuadro trae la de otro mueble
DESCRIPCIONES = {
    'M28': 'ESCRITORIO DE MELAMINA CON DOS CAJONERAS 1.00 x 0.50 x 0.75 m',
    'M51': 'ESTANTE METÁLICO RANURADO CON CUATRO DIVISIONES 0.90 x 0.45 x 1.80 m',
    'M55': 'CAMA CON CABECERA DE 0.90 x 1.90 m',
    'M63': 'SOFÁ DE 3 CUERPOS 0.55 x 1.80 x 0.44 m',
    'M73': 'ESTACIÓN DE SERVIDO CON TRES BANDEJAS, UNA PUERTA Y UNA CUBIERTA 1.20 x 0.70 x 0.90 m',
    'M16': 'MESA DE TRABAJO DE MADERA PARA ESTUDIANTES 0.90 x 1.80 x 0.56 m',
    'E13': 'COCINA INDUSTRIAL DE 2 HORNILLAS',
    'M44': 'CREDENZA DE MELAMINA CON DOS PUERTAS, DOS DIVISIONES Y TRES GAVETAS 0.75 x 0.40 x 1.20 m',
}
DESC_MAL = {'M28': 'ESCRITORIO DE MELAMINA CON CREDENZA', 'M51': 'EXHIBIDOR DE LIBROS', 'M55': 'MUEBLE ALTO'}
GRUPOS = OrderedDict([('E', 'EQUIPOS'), ('M', 'MOBILIARIO'), ('K', 'IMPLEMENTOS')])


def plano():
    return json.load(open(PLANO, encoding='utf-8'))


def _titulo(s):
    s = s.replace('SS.HH', 'SS.HH.').replace('SSHH', 'SS.HH.').replace('..', '.')
    return s


def ambientes(P=None):
    """Lista de ambientes con sus ítems adoptados: [(edificación, ambiente, [dict(clave, cod, grupo, des, cant, cuadro, nota)])]."""
    P = P or plano()
    out = []
    for c in P['cuadros']:
        ed, amb = c['edificacion'], c['ambiente']
        for (e0, a0, x0), (e1, a1) in RETITULOS.items():
            if ed == e0 and amb.startswith(a0) and abs(c['x'] - x0) < 0.05:
                ed, amb = e1, a1
        items = []
        for i in c['items']:
            cod = i['cod']; g = cod[0]
            if g == 'S':
                g = 'S'
            des = DESCRIPCIONES.get(cod, i['des']) if g in 'EM' else i['des']
            clave = cod if g in 'EM' else 'K:' + amb + ':' + i['des']
            items.append(dict(clave=clave, cod=cod, grupo=g, des=des, des_cuadro=i['des'], cuadro=i['cant'], cant=i['cant'], nota=''))
        for e, a, cod, q, motivo in CORRECCIONES:
            if ed == e and a in amb:
                for it in items:
                    if it['cod'] == cod:
                        it['cant'] = q; it['nota'] = motivo
        for e, a, cod, q, sec, motivo in AGREGADOS:
            if ed == e and amb == a and not any(it['cod'] == cod for it in items):
                items.append(dict(clave=cod, cod=cod, grupo=cod[0], des=DESCRIPCIONES.get(cod, cod), des_cuadro='', cuadro=0, cant=q, nota=motivo))
        out.append((ed, _titulo(amb), [it for it in items if it['grupo'] != 'S' or it['cant']]))
    orden = list(EDIFICACIONES)
    return sorted(out, key=lambda a: (orden.index(a[0]) if a[0] in orden else 99, a[1]))


def catalogo(P=None):
    """Partidas en orden (equipos, mobiliario, implementos por ambiente) con descripción, total adoptado y cuadros sin corregir."""
    A = ambientes(P)
    tot = Counter(); cua = Counter(); des = {}; grupo = {}; amb_imp = {}
    for ed, amb, items in A:
        for it in items:
            if it['grupo'] == 'S':
                continue
            tot[it['clave']] += it['cant']; cua[it['clave']] += it['cuadro'] or 0
            d = it['des']
            mal = it['cod'] in DESC_MAL and d.startswith(DESC_MAL[it['cod']])
            if it['cod'] in DESCRIPCIONES:
                des[it['clave']] = DESCRIPCIONES[it['cod']]
            elif not mal and len(d) > len(des.get(it['clave'], '')):
                des[it['clave']] = d
            grupo[it['clave']] = it['grupo']
            if it['grupo'] == 'K':
                amb_imp[it['clave']] = (ed, amb)
    num = lambda k: (int(re.sub(r'\D', '', k)) if k[0] in 'EM' else 0)
    filas = []
    for g, nombre in GRUPOS.items():
        ks = [k for k in tot if grupo[k] == g and tot[k] > 0]
        if g == 'K':
            ks.sort(key=lambda k: (list(EDIFICACIONES).index(amb_imp[k][0]), amb_imp[k][1], k))
        else:
            ks.sort(key=num)
        filas.append(dict(tipo='grupo', g=g, desc=nombre))
        sub = None
        for k in ks:
            if g == 'K' and amb_imp[k] != sub:
                sub = amb_imp[k]; filas.append(dict(tipo='sub', g=g, desc='%s - %s' % (sub[1], sub[0])))
            filas.append(dict(tipo='item', g=g, clave=k, cod=(k if g in 'EM' else ''), desc=re.sub(r'\s*\((PRIMARIA|INICIAL)\)', '', des[k]).strip(' .(').upper(), und='und',
                              total=tot[k], cuadros=cua[k]))
    return filas


def original():
    """Metrado original del usuario (hoja HR): código -> (descripción, cantidad); implementos por nombre."""
    wb = openpyxl.load_workbook(ORIGINAL, data_only=True); ws = wb['HR']
    cod, imp = {}, []
    for r in range(17, ws.max_row + 1):
        c, d, q = ws.cell(r, 3).value, ws.cell(r, 4).value, ws.cell(r, 6).value
        m = re.fullmatch(r'\s*([EM])\s*0*(\d+)\s*', str(c or ''))
        if m:
            cod['%s%d' % (m.group(1), int(m.group(2)))] = (re.sub(r'\s+', ' ', str(d)).strip(), q)
        elif d and isinstance(q, (int, float)):
            imp.append((re.sub(r'\s+', ' ', str(d)).strip(), q, str(ws.cell(r, 2).value)))
    return cod, imp, wb.sheetnames


def _sin_tildes(s):
    import unicodedata
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()


def etiquetas(P=None):
    P = P or plano(); t = Counter()
    for ed, c in P['etiquetas'].items():
        for k, v in c.items():
            t[k] += v
    return t


def verificacion(P=None):
    """Por código: metrado original, suma de cuadros, etiquetas en planta, adoptado y observación."""
    P = P or plano(); cat = [f for f in catalogo(P) if f['tipo'] == 'item' and f['g'] in 'EM']
    org, imp, hojas = original(); et = etiquetas(P)
    notas = defaultdict(list)
    for ed, amb, items in ambientes(P):
        for it in items:
            if it['nota'] and it['nota'] not in notas[it['cod']]:
                notas[it['cod']].append(it['nota'])
    out = []
    for f in cat:
        k = f['clave']; o = org.get(k)
        obs = list(notas.get(k, []))
        if o and o[1] != f['total']:
            obs.insert(0, 'El metrado original dice %s; el plano da %s.' % (o[1], f['total']))
        if not o:
            obs.insert(0, 'No figura en el metrado original.')
        if o and k in DESCRIPCIONES and not _sin_tildes(o[0]).upper().startswith(_sin_tildes(DESCRIPCIONES[k])[:12]):
            obs.append('Descripción del original: "%s".' % o[0])
        out.append(dict(clave=k, desc=f['desc'], original=o[1] if o else None, cuadros=f['cuadros'], planta=et.get(k, 0),
                        adoptado=f['total'], obs=' '.join(obs)))
    for k, (d, q) in org.items():
        if not any(f['clave'] == k for f in cat):
            out.append(dict(clave=k, desc=d.upper(), original=q, cuadros=0, planta=et.get(k, 0), adoptado=0,
                            obs='No figura en ningún cuadro ni en la planta del plano%s.' % (
                                '')))
    return out, imp, hojas


OBS_PLANO = [
    ('MB-02', 'El cuadro del almacén de implementos deportivos de E-02 está titulado "TÓPICO - EDIFICACIÓN 2".'),
    ('MB-08', 'El cuadro del almacén de cocina y cuarto de gas (balones de gas y parihuelas) está titulado "OFICINA DE ENTREVISTA Y ESTAR - EDIFICACIÓN 6".'),
    ('MB-01', 'El cuadro del tópico repite el de la sala de reuniones: proyector multimedia y 10 sillas.'),
    ('MB-04 a MB-07', 'El cuadro del dormitorio de la madre repite las 5 computadoras del salón de estudios (en planta hay 1).'),
    ('MB-04 a MB-07', 'El cuadro de la oficina de entrevista y estar pone 1 sofá de 2 cuerpos (M34); en planta hay 2.'),
    ('MB-04 a MB-07', 'Los cuadros de dormitorio describen el código M55 como "mueble alto de melamina"; M55 es la cama con cabecera (dibujada).'),
    ('MB-04, MB-05', 'El salón de estudios describe el código M28 como "escritorio con credenza móvil 1.50 x 0.80"; M28 es el escritorio con dos cajoneras 1.00 x 0.50 (dibujado).'),
    ('MB-07', 'En el dormitorio de E-07 la planta rotula 10 credenzas M44 (una junto a cada cama) y el cuadro pone 10 armarios M37; se cuenta lo rotulado. Corregir el cuadro.'),
    ('MB-04, MB-05, MB-01', 'Sin etiqueta en planta pero sí en su cuadro: las 5 computadoras E6 del salón de estudios (E-04 y E-05) y el rack M13 y la pizarra M69 de la sala de reuniones (E-01); se mantienen.'),
    ('MB-07', 'El cuadro del taller de arte pone 1 mueble para mochilas (M56); en planta hay 5.'),
    ('MB-02', 'El cuadro del almacén deportivo describe M51 como "exhibidor de libros"; M51 es el estante metálico ranurado.'),
    ('MB-01, MB-06', 'Los códigos de implementos K32 y K33 se usan para dos cosas distintas (tópico: bidón de oxígeno y tensiómetro; '
                     'psicomotricidad: piscina de pelotas y juego de teatro) y K78 para cojines cuadrados y piso encastrable.'),
    ('MB-08', 'El SUM y la cocina tienen 6 extintores de 9 kg en sus cuadros; la lámina de señalización SE-S-01 tiene 4 en E-08 '
              '(2 PQS y 2 CO2). Los extintores se metran en evacuación y señalización.'),
    ('MB-08', 'Cocina: el cuadro pone 7 casilleros (M42) y en planta hay 4. Comedor: la estación de servido (M73) está dibujada y no figura en el cuadro.'),
    ('MB-02', 'Maestranza (E-10): el cuadro pone 4 contenedores (M75) y en planta hay 2.'),
]


def verificacion_implementos(P=None):
    """Implementos del metrado original frente a los cuadros del plano (por nombre)."""
    org = original()[1]
    plan = {}
    for f in catalogo(P):
        if f['tipo'] == 'item' and f['g'] == 'K':
            plan[_sin_tildes(f['desc']).upper()] = f
    key = lambda s: re.sub(r'[^A-Z0-9]', '', re.sub(r'\b(DE|INCL|INC)\b', '', _sin_tildes(s).upper()))
    pk = {key(k): v for k, v in plan.items()}
    out = []; usados = set()
    for d, q, it in org:
        f = pk.get(key(d))
        if f:
            usados.add(f['clave'])
        out.append(dict(desc=d.upper(), original=q, plano=f['total'] if f else 0,
                        obs='' if f and f['total'] == q else ('No figura en los cuadros del plano.' if not f else
                                                              'El metrado original dice %s; el cuadro del plano, %s.' % (q, f['total']))))
    for f in plan.values():
        if f['clave'] not in usados:
            out.append(dict(desc=f['desc'], original=None, plano=f['total'], obs='No figura en el metrado original.'))
    return out


def numerar(cat=None):
    """Numeración de partidas del RESUMEN (03.01.01 equipos, 03.01.02 mobiliario, 03.01.03 implementos por ambiente)."""
    cat = cat or catalogo()
    out = [dict(item='03', desc='ARQUITECTURA', nivel=0), dict(item='03.01', desc='MOBILIARIO Y EQUIPAMIENTO', nivel=1)]
    g_n = s_n = i_n = 0; base = ''; sub = None
    for f in cat:
        if f['tipo'] == 'grupo':
            g_n += 1; s_n = i_n = 0; base = '03.01.%02d' % g_n
            out.append(dict(f, item=base, nivel=2))
        elif f['tipo'] == 'sub':
            s_n += 1; i_n = 0; sub = f['desc']
            out.append(dict(f, item='%s.%02d' % (base, s_n), desc=f['desc'].upper(), nivel=3))
        else:
            i_n += 1
            it = ('%s.%02d.%02d' % (base, s_n, i_n)) if f['g'] == 'K' else ('%s.%02d' % (base, i_n))
            out.append(dict(f, item=it, nivel=4 if f['g'] == 'K' else 3, ambiente=sub if f['g'] == 'K' else ''))
    return out
