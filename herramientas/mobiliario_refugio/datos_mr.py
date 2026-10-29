# -*- coding: utf-8 -*-
"""Datos de equipamiento y mobiliario del Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514): fuente única del
metrado, la memoria descriptiva y las especificaciones técnicas.

Cantidades adoptadas = las de cada ambiente según los cuadros de equipamiento de las láminas EM-01 a EM-07 (lee_plano_mr.py),
contrastadas con lo dibujado y rotulado en la planta de cada edificación. Donde el cuadro no coincide con la planta, rige la
planta (CORRECCIONES y AGREGADOS, cada uno con su motivo); en los implementos (K), que la planta rotula una sola vez por tipo,
rige el cuadro salvo que la planta rotule más piezas. Descripciones: una por código (DESCRIPCIONES), corregidas donde la fila del
cuadro trae la descripción de otro código. Los extintores (S) son partida de seguridad y señalización, no de mobiliario.
"""
import json
import os
import re
from collections import Counter, OrderedDict, defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
PLANO = os.path.join(RAIZ, 'entregables/_calc/mobiliario_plano.json')
SAL = os.path.join(RAIZ, 'entregables')

PROYECTO = ('CREACIÓN DEL SERVICIO DE PROTECCIÓN A MUJERES VÍCTIMAS DE VIOLENCIA EN SITUACIÓN DE RIESGO DE FEMINICIDIO O PELIGRE '
            'SU INTEGRIDAD Y/O SALUD FÍSICA Y/O MENTAL EN HOGAR DE REFUGIO TEMPORAL DISTRITO DE MORALES DE LA PROVINCIA DE SAN '
            'MARTÍN DEL DEPARTAMENTO DE SAN MARTÍN')
CUI = '2675514'
CORTO = 'HOGAR DE REFUGIO TEMPORAL'
ESPECIALIDAD = 'ARQUITECTURA - EQUIPAMIENTO Y MOBILIARIO'
UBICACION = 'Distrito de Morales, provincia y departamento de San Martín'
FECHA = 'SETIEMBRE 2026'

EDIFICACIONES = OrderedDict([
    ('E-01', 'Administración'), ('E-02', 'Almacén de donaciones y tópico'), ('E-03', 'Mantenimiento'),
    ('E-04', 'Talleres'), ('E-05', 'SUM-comedor, cocina, lavandería, módulo de enseñanza y módulo infantil'),
    ('E-06', 'Dormitorios (1)'), ('E-07', 'Dormitorios (2)'), ('E-08', 'Dormitorios (3)'),
    ('E-09', 'Vestidores y almacén de implementos deportivos')])
LAMINA = {'E-01': 'EM-01', 'E-02': 'EM-02', 'E-03': 'EM-02', 'E-04': 'EM-03', 'E-05': 'EM-04', 'E-06': 'EM-05', 'E-07': 'EM-06',
          'E-08': 'EM-07', 'E-09': 'EM-07'}

# cuadro (lámina, x del título) -> (edificación, ambiente); None = cuadro repetido que no se metra
CUADROS = {
    ('EM-01', 348109.148, 9281785.677): ('E-01', 'SALA DE ESPERA Y SALA DE VISITA'),
    ('EM-01', 348100.864, 9281785.648): ('E-01', 'ASISTENCIA SOCIAL'),
    ('EM-01', 348100.793, 9281780.111): ('E-01', 'PSICOLOGÍA, ÁREA LEGAL, OFICINA DE MONITOREO Y ADMINISTRACIÓN'),
    ('EM-01', 348109.151, 9281779.19): ('E-01', 'SALA DE REUNIONES'),
    ('EM-01', 348100.793, 9281774.869): ('E-01', 'SECRETARÍA Y ÁREA DE BIENVENIDA'),
    ('EM-01', 348109.151, 9281770.976): ('E-01', 'DIRECCIÓN GENERAL Y SS.HH.'),
    ('EM-01', 348100.864, 9281766.707): ('E-01', 'SS.HH. DE PERSONAL Y SS.HH. PARA PERSONAS CON DISCAPACIDAD'),
    ('EM-01', 348100.864, 9281764.962): ('E-01', 'PASADIZO'),
    ('EM-02', 348161.345): ('E-02', 'ALMACÉN DE DONACIONES, TÓPICO Y SS.HH.'),
    ('EM-02', 348170.536): None,
    ('EM-02', 348165.208): ('E-03', 'ALMACÉN GENERAL Y DE LIMPIEZA, Y ALMACENAMIENTO DE RESIDUOS SÓLIDOS'),
    ('EM-03', 348211.523, 9281789.118): ('E-04', 'TALLER DE COSTURA'),
    ('EM-03', 348211.523, 9281783.983): ('E-04', 'TALLER DE BISUTERÍA'),
    ('EM-03', 348211.528, 9281777.993): ('E-04', 'SS.HH. VARONES, SS.HH. MUJERES, SS.HH. PARA PERSONAS CON DISCAPACIDAD Y CUARTO DE LIMPIEZA'),
    ('EM-03', 348211.528, 9281775.804): ('E-04', 'PASADIZO'),
    ('EM-03', 348211.523, 9281772.421): ('E-04', 'TALLER DE REPOSTERÍA'),
    ('EM-03', 348211.523, 9281766.426): ('E-04', 'TERAPIA GRUPAL'),
    ('EM-03', 348211.523, 9281761.434): ('E-04', 'CUARTO DE CÁMARAS DE VIDEOVIGILANCIA, ARCHIVO Y DEPÓSITO'),
    ('EM-04', 348250.502, 9281785.378): ('E-05', 'MÓDULO DE ENSEÑANZA'),
    ('EM-04', 348250.507, 9281778.441): ('E-05', 'LAVANDERÍA'),
    ('EM-04', 348250.507, 9281775.114): ('E-05', 'SUM-COMEDOR'),
    ('EM-04', 348250.502, 9281771.71): ('E-05', 'COCINA, ALACENA Y DESPENSA'),
    ('EM-04', 348250.502, 9281765.88): ('E-05', 'MÓDULO INFANTIL'),
    ('EM-05', 348105.617): ('E-06', 'HABITACIONES ESPECIAL, DOBLES Y SIMPLES'),
    ('EM-05', 348105.691): ('E-06', 'SS.HH. DE LAS HABITACIONES'),
    ('EM-06', 348157.244): ('E-07', 'HABITACIONES ESPECIAL, DOBLES Y SIMPLES'),
    ('EM-06', 348157.317): ('E-07', 'SS.HH. DE LAS HABITACIONES'),
    ('EM-07', 348189.047): ('E-08', 'HABITACIONES ESPECIAL, DOBLES Y SIMPLES'),
    ('EM-07', 348189.12): ('E-08', 'SS.HH. DE LAS HABITACIONES'),
    ('EM-07', 348198.739): ('E-09', 'ALMACÉN DE IMPLEMENTOS DEPORTIVOS'),
    ('EM-07', 348208.175): ('E-09', 'VESTIDORES Y SS.HH.'),
}

# correcciones de cantidad: (edificación, ambiente contiene, código) -> (cantidad, motivo)
CORRECCIONES = [
    ('E-01', 'SALA DE ESPERA', 'M32', 3, 'En la planta hay 3 sillones M32 (1 en la sala de espera y 2 en la sala de visita); el cuadro dice 2.'),
    ('E-01', 'SALA DE ESPERA', 'M34', 2, 'En la planta hay 2 sofás de 2 cuerpos M34 (uno en cada sala); el cuadro dice 3.'),
    ('E-01', 'SALA DE ESPERA', 'M62', 2, 'En la planta hay 2 cestos M62 (uno en cada sala); el cuadro dice 1.'),
    ('E-01', 'ASISTENCIA SOCIAL', 'M39', 1, 'En la planta hay 1 archivador M39; el cuadro dice 2.'),
    ('E-01', 'PSICOLOGÍA', 'M62', 5, 'En la planta hay 5 cestos M62 (psicología, área legal, 2 en la oficina de monitoreo y administración); '
                                     'el cuadro dice 4.'),
    ('E-01', 'DIRECCIÓN', 'M32', 2, 'En la planta hay 2 sillones M32; el cuadro dice 1.'),
    ('E-01', 'DIRECCIÓN', 'M36', 5, 'En la planta hay 5 armarios M36 (3 en el muro norte y 2 en el muro oeste); el cuadro dice 2.'),
    ('E-02', 'ALMACÉN DE DONACIONES', 'M28', 1, 'En la planta hay 1 escritorio M28 (tópico); el cuadro dice 3.'),
    ('E-03', 'ALMACÉN GENERAL', 'M51', 6, 'En la planta hay 6 estantes M51 en el almacén general y de limpieza; el cuadro dice 15.'),
    ('E-03', 'ALMACÉN GENERAL', 'M75', 3, 'En la planta hay 3 contenedores M75 en el almacenamiento de residuos sólidos; el cuadro dice 5.'),
    ('E-05', 'MÓDULO DE ENSEÑANZA', 'M62', 2, 'En la planta hay 2 cestos M62; el cuadro dice 1.'),
    ('E-05', 'SUM-COMEDOR', 'M3', 192, 'En la planta hay 24 mesas M16 con 8 sillas M3 cada una: 192 sillas rotuladas; el cuadro dice 384.'),
    ('E-05', 'MÓDULO INFANTIL', 'K78', 8, 'En la planta hay 8 piezas de piso encastrable K78 rotuladas; el cuadro dice 1.'),
    ('E-09', 'ALMACÉN DE IMPLEMENTOS', 'M51', 3, 'En la planta hay 3 estantes metálicos M51; la fila del cuadro dice 1 y trae la descripción del '
                                                'atril M15 del módulo infantil.'),
    ('E-09', 'ALMACÉN DE IMPLEMENTOS', 'M52', 0, 'No está en la planta; la fila del cuadro trae la descripción del exhibidor M54 del módulo infantil.'),
]
# ítems dibujados y rotulados en la planta que no figuran en el cuadro: (edificación, ambiente, código, cantidad, motivo)
AGREGADOS = [
    ('E-01', 'PSICOLOGÍA', 'M39', 3, 'En la planta hay 3 archivadores M39 (psicología, área legal y administración); el cuadro no los incluye.'),
    ('E-01', 'PSICOLOGÍA', 'M32', 1, 'En la planta hay 1 sillón M32 en psicología; el cuadro no lo incluye.'),
    ('E-01', 'SECRETARÍA', 'M39', 1, 'En la planta hay 1 archivador M39 en secretaría; el cuadro no lo incluye.'),
    ('E-01', 'PASADIZO', 'M7', 8, 'En la planta hay 8 sillas M07 de espera en el pasadizo (junto a psicología, área legal y la oficina de '
                                  'monitoreo); no figuran en ningún cuadro.'),
    ('E-02', 'ALMACÉN DE DONACIONES', 'M76', 1, 'En la planta hay 1 portapapel higiénico M76 en el SS.HH. del tópico; el cuadro no lo incluye.'),
    ('E-09', 'ALMACÉN DE IMPLEMENTOS', 'K53', 1, 'Rotulado en la planta (colchoneta); no figura en el cuadro. Cantidad mínima rotulada.'),
    ('E-09', 'ALMACÉN DE IMPLEMENTOS', 'K73', 1, 'Rotulado en la planta (kit de vóley); no figura en el cuadro. Cantidad mínima rotulada.'),
    ('E-09', 'ALMACÉN DE IMPLEMENTOS', 'K74', 1, 'Rotulado en la planta (guantes de entrenamiento); no figura en el cuadro. Cantidad mínima rotulada.'),
    ('E-09', 'ALMACÉN DE IMPLEMENTOS', 'K79', 1, 'Rotulado en la planta (mica protectora); no figura en el cuadro. Cantidad mínima rotulada.'),
]
# mismo código para dos elementos distintos: (edificación, código) -> (clave del metrado, descripción)
DOBLES = {('E-04', 'M16'): ('M16-T', 'MESA DE CORTE TEXTIL 0.80 x 1.50 x 0.75 m'),
          ('E-09', 'M64'): ('M64-C', 'CANASTILLA MÓVIL CON RUEDAS PARA PELOTAS 1.00 x 0.80 x 1.00 m')}

DESCRIPCIONES = {
    'E1': 'PROYECTOR INTERACTIVO', 'E2': 'COMPUTADORA PORTÁTIL i5', 'E3': 'PRESENTADOR INALÁMBRICO CON PUNTERO LÁSER',
    'E4': 'RELOJ PARA ADOSAR A PARED', 'E5': 'LAVADORA DE 20 kg DE CARGA SUPERIOR', 'E6': 'COMPUTADORA i5 ESTACIONARIA',
    'E7': 'PROYECTOR MULTIMEDIA', 'E9': 'IMPRESORA MULTIFUNCIONAL', 'E10': 'MÁQUINA DE CORTE TEXTIL',
    'E13': 'COCINA INDUSTRIAL DE 2 HORNILLAS', 'E16': 'HORNO MICROONDAS DE 31 LITROS', 'E17': 'LICUADORA DE 1.5 LITROS', 'E18': 'ECRAN',
    'E19': 'REFRIGERADORA DE 315 LITROS',
    'M3': 'SILLA REGULABLE DE ESTUDIANTE DE MADERA Y METAL 0.30 x 0.27 x 0.32 m', 'M4': 'MESA REGULABLE DE MADERA Y METAL 0.56 x 0.50 x 0.60 m',
    'M7': 'SILLA DEL PROFESOR DE MADERA, MELAMINA Y METAL 0.45 x 0.40 x 0.36 m', 'M8': 'MESA PARA EL PROFESOR DE MADERA Y METAL 1.00 x 0.50 x 0.75 m',
    'M9': 'MANIQUÍ DE COSTURA PARA CONFECCIÓN TEXTIL', 'M13': 'RACK DE SOPORTE METÁLICO PARA PROYECTOR EN TECHO',
    'M15': 'ATRIL DE MESA PARA DIBUJO Y PINTURA', 'M16': 'MESA DE TRABAJO DE MADERA PARA ESTUDIANTES 0.90 x 1.80 x 0.56 m',
    'M19': 'MESA DE MADERA 1.00 x 1.80 x 0.75 m', 'M20': 'BIOMBO METÁLICO DE 3 CUERPOS',
    'M21': 'MESA DE REUNIONES DE MADERA Y MELAMINA 2.40 x 1.00 x 0.75 m', 'M22': 'MESA DE MADERA 1.00 x 1.80 x 0.75 m',
    'M23': 'MESA DE MADERA 1.00 x 2.00 x 0.75 m', 'M26': 'MESA DE ACERO INOXIDABLE 0.90 x 0.60 x 0.90 m', 'M27': 'SILLA DE RUEDAS',
    'M28': 'ESCRITORIO DE MELAMINA CON DOS CAJONERAS 1.00 x 0.50 x 0.75 m',
    'M31': 'ESCRITORIO DE MELAMINA CON CREDENZA MÓVIL 1.50 x 0.80 x 0.75 m', 'M32': 'SILLÓN PARA ACOPLAR 0.44 x 0.55 x 0.60 m',
    'M34': 'SOFÁ DE MADERA DE 2 CUERPOS 0.44 x 0.55 x 1.00 m',
    'M35': 'SILLA TIPO TABURETE REGULABLE DE MADERA Y METAL 0.15 x 0.30 x 0.60 x 0.75 m',
    'M36': 'ARMARIO DE MELAMINA CON 2 PUERTAS Y 4 NIVELES 0.90 x 0.45 x 1.80 m',
    'M37': 'ARMARIO PARA ALMACENAR MATERIAL DE MELAMINA CON 2 PUERTAS Y 5 DIVISIONES 0.90 x 0.60 x 1.80 m',
    'M39': 'ARCHIVADOR DE MELAMINA CON TRES GAVETAS 0.60 x 0.46 x 1.20 m',
    'M51': 'ESTANTE METÁLICO RANURADO CON CUATRO DIVISIONES 0.90 x 0.45 x 1.80 m',
    'M52': 'ESTANTE DE ACERO INOXIDABLE CON CUATRO DIVISIONES Y BANDEJA 0.60 x 0.60 x 1.80 m',
    'M54': 'EXHIBIDOR DE LIBROS DE MELAMINA CON DIVISIONES ESCALONADAS 1.20 x 0.40 x 0.85 m',
    'M56': 'MUEBLE BAJO DE MELAMINA PARA GUARDAR MOCHILAS CON DOS DIVISIONES 0.60 x 0.40 x 1.00 m',
    'M57': 'MUEBLE BAJO DE MELAMINA CON DOS PUERTAS Y DOS DIVISIONES HORIZONTALES 0.60 x 1.20 x 1.00 m',
    'M60': 'PAPELERA DE PLÁSTICO CON PEDAL', 'M61': 'VELADOR DE MADERA 0.45 x 0.50 m', 'M62': 'CESTO BOTA PAPELES DE ACERO CON PEDAL',
    'M63': 'SOFÁ DE 3 CUERPOS 0.55 x 1.50 x 0.44 m', 'M64': 'CAMAROTE DE UNA PLAZA Y MEDIA, INCLUYE COLCHÓN',
    'M65': 'CAMILLA METÁLICA RECLINABLE CON RESPALDO Y RUEDAS 1.80 x 0.60 x 0.70 m',
    'M67': 'ESCALERA METÁLICA DE DOS PELDAÑOS 0.40 x 0.40 x 0.36 m', 'M68': 'PARIHUELA DE MADERA 0.90 x 0.50 x 0.20 m',
    'M69': 'PIZARRA ACRÍLICA 4.20 x 1.20 m, INCLUYE ACCESORIOS DE FIJACIÓN',
    'M70': 'BOTIQUÍN DE MADERA DE PRIMEROS AUXILIOS CON DOS DIVISIONES Y UNA PUERTA 0.30 x 0.15 x 0.40 m, INCLUYE MEDICAMENTOS',
    'M71': 'COCHE MULTIUSOS MÓVIL DE ACERO INOXIDABLE 0.80 x 0.40 x 0.90 m',
    'M73': 'ESTACIÓN DE SERVIDO CON TRES BANDEJAS, UNA PUERTA Y UNA CUBIERTA 1.20 x 0.70 x 0.90 m',
    'M75': 'CONTENEDOR CON TAPA PARA RESIDUOS SÓLIDOS 0.80 x 1.00 x 1.00 m', 'M76': 'PORTAPAPEL HIGIÉNICO',
    'M77': 'DISPENSADOR DE PAPEL TOALLA', 'M78': 'CAMA DE DOS PLAZAS, INCLUYE COLCHÓN', 'M79': 'CAMA CUNA DE UNA PLAZA, INCLUYE COLCHÓN',
}
# implementos: descripción limpia del cuadro; los agregados de la planta con la del catálogo de códigos del mismo plano tipo
IMPLEMENTOS = {'K53': 'COLCHONETA SIMPLE FORRADA CON CUERO 1.50 x 0.50 m', 'K73': 'KIT DE VÓLEY: RED Y PARANTES TELESCÓPICOS',
               'K74': 'GUANTES DE ENTRENAMIENTO', 'K79': 'MICA PROTECTORA DE POLICARBONATO'}
GRUPOS = OrderedDict([('E', 'EQUIPOS'), ('M', 'MOBILIARIO'), ('K', 'IMPLEMENTOS')])


def cap(t):
    """Texto en mayúscula inicial, con siglas y códigos como se escriben (SS.HH., SUM, K78, ...)."""
    t = t[:1].upper() + t[1:].lower()
    for a, b in ((r'ss\.hh\.?', 'SS.HH.'), (r'\bsum\b', 'SUM'), (r'\b([mek])(\d+)\b', None), (r'\bi5\b', 'i5'), (r'\bpvc\b', 'PVC')):
        t = re.sub(a, (lambda m: m.group(1).upper() + m.group(2)) if b is None else b, t, flags=re.I)
    return t


def plano():
    return json.load(open(PLANO, encoding='utf-8'))


def _cuadro(c):
    v = [v for k, v in CUADROS.items()
         if k[0] == c['lamina'] and abs(k[1] - c['x']) < 0.01 and (len(k) == 2 or abs(k[2] - c['y']) < 0.01)]
    if len(v) != 1:
        raise KeyError('cuadro sin asignar o ambiguo: %s %s %s' % (c['lamina'], c['x'], c['titulo']))
    return v[0]


def _desc_k(d):
    d = re.sub(r'\s+', ' ', d).strip(' .').upper()
    for a, b in (('BASKET', 'BÁSQUET'), ('FUTBOL', 'FÚTBOL'), ('VOLEY', 'VÓLEY'), ('OBSTACULO', 'OBSTÁCULO'), ('METALICO', 'METÁLICO'),
                 ('BIDON', 'BIDÓN'), ('OXIGENO', 'OXÍGENO'), ('TENSIOMETRO', 'TENSIÓMETRO'), ('TERMOMETRO', 'TERMÓMETRO'),
                 ('ESTETOSCOPIO', 'ESTETOSCOPIO'), ('TOBOGAN', 'TOBOGÁN'), ('NIÑOS', 'NIÑOS'), ('ERGONOMETRICA', 'ERGONÓMICA'),
                 ('150X33CM', '1.50 m x 0.33 m'), ('1KG', '1 kg'), (' 1 KG', ' 1 kg'), ('600 GR', '600 g'), ('700 GR', '700 g'),
                 ('25 MM', '25 mm'), ('#', 'N.° ')):
        d = d.replace(a, b)
    return d


def ambientes(P=None):
    """[(edificación, ambiente, [dict(clave, cod, grupo, des, des_cuadro, cuadro, cant, nota)])] en orden de edificación."""
    P = P or plano()
    out = OrderedDict()
    for c in P['cuadros']:
        v = _cuadro(c)
        if v is None:
            continue
        ed, amb = v
        items = out.setdefault((ed, amb), [])
        for i in c['items']:
            cod = i['cod']; g = cod[0]
            if g == 'S':                                             # extintores: seguridad y señalización
                continue
            clave, des = DOBLES.get((ed, cod), (None, None))
            if g == 'K':
                des = _desc_k(i['des']); clave = 'K:%s:%s:%s' % (ed, amb, cod)
            else:
                clave = clave or cod; des = des or DESCRIPCIONES[cod]
            items.append(dict(clave=clave, cod=cod, grupo=g, des=des, des_cuadro=i['des'], cuadro=i['cant'], cant=i['cant'], nota=''))
    for (ed, amb), items in out.items():
        for e, a, cod, q, motivo in CORRECCIONES:
            if ed == e and a in amb:
                for it in items:
                    if it['cod'] == cod:
                        it['cant'] = q; it['nota'] = motivo
        for e, a, cod, q, motivo in AGREGADOS:
            if ed == e and a in amb and not any(it['cod'] == cod for it in items):
                g = cod[0]
                clave = 'K:%s:%s:%s' % (ed, amb, cod) if g == 'K' else cod
                items.append(dict(clave=clave, cod=cod, grupo=g, des=IMPLEMENTOS.get(cod) or DESCRIPCIONES[cod], des_cuadro='', cuadro=0,
                                  cant=q, nota=motivo))
    orden = list(EDIFICACIONES)
    res = [(ed, amb, [it for it in its if it['cant']]) for (ed, amb), its in out.items()]
    return [r for r in sorted(res, key=lambda a: orden.index(a[0])) if r[2]]


def catalogo(P=None):
    """Partidas en orden (equipos, mobiliario, implementos por ambiente) con descripción y total adoptado."""
    A = ambientes(P)
    tot = Counter(); des = {}; grupo = {}; cod = {}; amb_imp = {}
    for ed, amb, items in A:
        for it in items:
            tot[it['clave']] += it['cant']; des[it['clave']] = it['des']; grupo[it['clave']] = it['grupo']; cod[it['clave']] = it['cod']
            if it['grupo'] == 'K':
                amb_imp[it['clave']] = (ed, amb)
    num = lambda k: (int(re.sub(r'\D', '', cod[k])), k)            # noqa: E731
    filas = []
    for g, nombre in GRUPOS.items():
        ks = [k for k in tot if grupo[k] == g and tot[k] > 0]
        if g == 'K':
            ks.sort(key=lambda k: (list(EDIFICACIONES).index(amb_imp[k][0]), [a for e, a, _ in A].index(amb_imp[k][1]), num(k)))
        else:
            ks.sort(key=num)
        filas.append(dict(tipo='grupo', g=g, desc=nombre))
        sub = None
        for k in ks:
            if g == 'K' and amb_imp[k] != sub:
                sub = amb_imp[k]; filas.append(dict(tipo='sub', g=g, desc='%s - %s' % (sub[1], sub[0])))
            filas.append(dict(tipo='item', g=g, clave=k, cod=cod[k], desc=des[k], und='und', total=tot[k]))
    return filas


def numerar(cat=None):
    """Numeración de partidas (03 ARQUITECTURA, 03.01 MOBILIARIO Y EQUIPAMIENTO; .01 equipos, .02 mobiliario, .03 implementos por ambiente)."""
    cat = cat or catalogo()
    out = [dict(item='03', desc='ARQUITECTURA', nivel=0), dict(item='03.01', desc='MOBILIARIO Y EQUIPAMIENTO', nivel=1)]
    g_n = s_n = i_n = 0; base = ''; sub = None
    for f in cat:
        if f['tipo'] == 'grupo':
            g_n += 1; s_n = i_n = 0; base = '03.01.%02d' % g_n
            out.append(dict(f, item=base, nivel=2))
        elif f['tipo'] == 'sub':
            s_n += 1; i_n = 0; sub = f['desc']
            out.append(dict(f, item='%s.%02d' % (base, s_n), nivel=3))
        else:
            i_n += 1
            it = ('%s.%02d.%02d' % (base, s_n, i_n)) if f['g'] == 'K' else ('%s.%02d' % (base, i_n))
            out.append(dict(f, item=it, nivel=4 if f['g'] == 'K' else 3, ambiente=sub if f['g'] == 'K' else ''))
    return out


def edificacion_etiqueta(e, P=None):
    """Edificación de una etiqueta de la planta: por lámina; EM-02 (E-02 arriba del título de planta de E-02, E-03 abajo) y
    EM-07 (E-09 a la derecha del título de planta de E-09)."""
    P = P or plano()
    pl = {p['edificacion']: p for p in P['plantas']}
    if e['lamina'] == 'EM-02':
        return 'E-02' if e['y'] > pl['E-02']['y'] else 'E-03'
    if e['lamina'] == 'EM-07':
        return 'E-09' if e['x'] > pl['E-09']['x'] - 0.3 else 'E-08'
    return {'EM-01': 'E-01', 'EM-03': 'E-04', 'EM-04': 'E-05', 'EM-05': 'E-06', 'EM-06': 'E-07'}[e['lamina']]


def comprobacion(P=None):
    """Por edificación y código: suma de cuadros (sin corregir), etiquetas en planta y adoptado. En E y M el adoptado debe ser
    igual a la planta; en K, no menor que lo rotulado."""
    P = P or plano()
    cua = defaultdict(Counter); pla = defaultdict(Counter); ado = defaultdict(Counter)
    for c in P['cuadros']:
        v = _cuadro(c)
        if v:
            for i in c['items']:
                if i['cod'][0] != 'S':
                    k = DOBLES.get((v[0], i['cod']), (i['cod'],))[0]
                    cua[v[0]][k] += i['cant'] or 0
    for e in P['etiquetas']:
        ed = edificacion_etiqueta(e, P)
        k = DOBLES.get((ed, e['cod']), (e['cod'],))[0]
        pla[ed][k] += 1
    for ed, amb, its in ambientes(P):
        for it in its:
            k = it['clave'] if it['grupo'] != 'K' else it['cod']
            ado[ed][k] += it['cant']
    filas = []; errores = []
    for ed in EDIFICACIONES:
        ks = set(cua[ed]) | set(pla[ed]) | set(ado[ed])
        for k in sorted(ks, key=lambda k: (k[0], int(re.sub(r'\D', '', k)), k)):
            a, p, q = cua[ed][k], pla[ed][k], ado[ed][k]
            ok = (q == p) if k[0] in 'EM' else (q >= p)
            filas.append(dict(ed=ed, cod=k, cuadros=a, planta=p, adoptado=q, ok=ok))
            if not ok:
                errores.append((ed, k, a, p, q))
    return filas, errores


def observaciones_plano():
    """Correcciones que la arquitecta debe hacer en los cuadros de las láminas para que digan lo mismo que la planta y el metrado."""
    obs = [
        ('EM-01', 'Cuadro "Dirección general y SS.HH.": las descripciones están corridas una fila (M31 dice rack de proyector, M32 mesa de '
                  'reuniones, M36 credenza y M39 cesto); deben ser escritorio con credenza, sillón, armario y archivador.'),
        ('EM-01', 'Cuadro "Sala de reuniones": el código E9 está descrito como proyector multimedia; E9 es la impresora multifuncional '
                  '(dibujada sobre el archivador). El proyector es E7.'),
        ('EM-01', 'El cuadro "Pasadizo" solo trae el extintor; faltan las 8 sillas M07 de espera dibujadas en el pasadizo.'),
        ('EM-02', 'El cuadro de E-02 está titulado "Sala de espera y sala de visita - Edificación 2"; corresponde al almacén de donaciones, '
                  'el tópico y su SS.HH.'),
        ('EM-02', 'El cuadro "Tópico - Edificación 3" repite los ítems del tópico ya incluidos en el cuadro de E-02 y lo titula en E-03; '
                  'además describe el código M63 como camilla (la camilla es M65; M63 es el sofá de 3 cuerpos). Se debe retirar o '
                  'dejar un solo cuadro para el tópico.'),
        ('EM-03', 'Cuadro "Pasadizo - Edificación 2": está en la lámina de E-04 (talleres).'),
        ('EM-03', 'Cuadro "Taller de bisutería": el código M37 está descrito como archivador de tres gavetas; M37 es el armario para '
                  'almacenar material de 2 puertas y 5 divisiones (dibujado junto a los armarios M36).'),
        ('EM-03 / EM-04', 'El código M16 se usa para dos muebles distintos: mesa de corte textil 0.80 x 1.50 (taller de costura) y mesa '
                          'de trabajo 0.90 x 1.80 (SUM-comedor). Se metran como partidas separadas; conviene darle otro código a una.'),
        ('EM-03', 'Los códigos M19 (terapia grupal) y M22 (taller de repostería) describen la misma mesa de madera 1.00 x 1.80 x 0.75 m.'),
        ('EM-04', 'SUM-comedor: el cuadro pone 384 sillas M3; la planta tiene 24 mesas M16 con 8 sillas cada una (192).'),
        ('EM-04', 'Módulo infantil: el cuadro pone 1 piso encastrable K78; la planta rotula 8 piezas. Los códigos K32 y K33 se usan en el '
                  'módulo infantil (tobogán y juego de teatro) y en el tópico (bidón de oxígeno y tensiómetro).'),
        ('EM-05', 'Cuadro "SS.HH. personal - Edificación 1": está en la lámina de E-06 y corresponde a los SS.HH. de sus habitaciones.'),
        ('EM-07', 'Cuadro "Módulo infantil - Edificación 5": está en la lámina de E-08 y E-09 y corresponde al almacén de implementos '
                  'deportivos; sus filas M51, M52 y M64 traen las descripciones del atril, el exhibidor y el mueble bajo del módulo '
                  'infantil. En la planta hay 3 estantes M51, ningún M52 y 1 canastilla M64 (el código M64 es también el camarote).'),
        ('EM-07', 'Almacén de implementos deportivos: la planta rotula K53, K73, K74 y K79 (colchoneta, kit de vóley, guantes y mica '
                  'protectora) que no figuran en el cuadro; se metra 1 de cada uno, a confirmar.'),
        ('EM-07', 'Cuadro "Vestidores - Edificación 1": está en la lámina de E-08 y E-09 y corresponde a los vestidores de E-09.'),
        ('EM-01 y EM-03', 'Los cuadros "Pasadizo" incluyen extintores de 9 kg (S1); son partida de seguridad y señalización, no de '
                          'mobiliario, y no se metran aquí.'),
    ]
    for e, a, cod, q, motivo in CORRECCIONES + [(e, a, c, q, m) for e, a, c, q, m in AGREGADOS]:
        pass
    return obs


if __name__ == '__main__':
    P = plano(); A = ambientes(P)
    print(len(A), 'ambientes;', sum(len(i) for _, _, i in A), 'ítems')
    f, err = comprobacion(P)
    print('diferencias con la planta:', err or 'ninguna')
    cat = catalogo(P)
    for g in 'EMK':
        its = [x for x in cat if x['tipo'] == 'item' and x['g'] == g]
        print(g, len(its), 'partidas', sum(x['total'] for x in its), 'und')
