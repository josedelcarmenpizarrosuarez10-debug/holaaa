# -*- coding: utf-8 -*-
"""Datos comunes de evacuación y señalización del CAR Varones (CUI 2705619): una sola fuente para el metrado, la memoria
descriptiva y las especificaciones técnicas.

Cantidades: del plano final de la arquitecta (lee_plano_se.py -> entregables_varones/_calc/senalizacion_plano.json):
  - señal con bloque en la planta de SE-S-01: la cantidad dibujada, por edificación (coincide con la leyenda en todas);
  - señal que en el DXF es imagen pegada (OLE, sin posición): la cantidad de la leyenda, en la columna "sin ubicar";
  - zona de reunión pintada en el piso: los 13 círculos S1 a S13 de SE-E-01 (radio 1.50 m, línea de 0.10 m).
Datos que el plano no define y se adoptan aquí (Cuadro 4 de las correcciones): extintor PQS 6 kg tipo ABC, extintor CO2
10 lb, aforo máximo 66 personas; la señal de extintor va sobre el equipo (borde inferior a 1.80 m).
"""
import json
import math
import os

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(AQUI)))
PLANO = os.path.join(RAIZ, 'entregables_varones/_calc/senalizacion_plano.json')
SAL = os.path.join(RAIZ, 'entregables_varones')

PROYECTO = ('CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE '
            'PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES DISTRITO DE MORALES DE LA PROVINCIA DE SAN MARTÍN DEL DEPARTAMENTO '
            'DE SAN MARTÍN')
CUI = '2705619'
CORTO = 'CAR VARONES'
ENTIDAD = 'GERENCIA TERRITORIAL BAJO MAYO - DIRECCIÓN DE INFRAESTRUCTURA'
UBICACION = 'Distrito de Morales, provincia y departamento de San Martín'
ESPECIALIDAD = 'ARQUITECTURA - EVACUACIÓN Y SEÑALIZACIÓN'
FECHA = 'SETIEMBRE 2026'                     # la de los rótulos de SE-S-01 y SE-E-01 (Setiembre-2026)
LAMINAS = [('SE-S-01', 'Plano de señalización', '1/150'), ('SE-E-01', 'Plano de evacuación', '1/150')]

# población (M-01): personal 5 + 11 + 6 = 22; residentes 40 (4 módulos de 10); temporales 4; capacidad máxima = aforo del SUM
POBLACION = dict(madres=5, administrativos=11, apoyo=6, residentes=40, temporales=4)
POBLACION['personal'] = POBLACION['madres'] + POBLACION['administrativos'] + POBLACION['apoyo']
POBLACION['permanentes'] = POBLACION['personal'] + POBLACION['residentes']
POBLACION['maxima'] = POBLACION['permanentes'] + POBLACION['temporales']
V_EVAC = 0.60                                # m/s: velocidad de desplazamiento adoptada (niños y personas con movilidad reducida)
D_MAX = 45.0                                 # m: recorrido máximo hasta un lugar seguro sin rociadores (RNE A.130)
ZONA_SEGURA = dict(radio=1.50, ancho=0.10, color='amarillo tráfico', pintura='pintura de tránsito')

# materiales de las señales (NTP 399.010-1; RNE A.120 para el braille)
FOTOLUM = 'Lámina de PVC celtex de 3 mm con vinil fotoluminiscente impreso y placa de acrílico con texto en braille'
VINIL = 'Lámina de PVC celtex de 3 mm con vinil adhesivo impreso y placa de acrílico con texto en braille'

# catálogo: clave = inicio de la descripción de la leyenda de SE-S-01
#   grupo, item, descripción de la partida, und, dimensiones de la señal, material, altura adoptada, función / ubicación
GRUPOS = [('01', 'SEÑALES DE EVACUACIÓN Y EMERGENCIA'), ('02', 'SEÑALES DE EQUIPOS CONTRA INCENDIO'),
          ('03', 'SEÑALES DE ADVERTENCIA Y PROHIBICIÓN'), ('04', 'SEÑALES INFORMATIVAS'),
          ('05', 'EQUIPOS DE PROTECCIÓN CONTRA INCENDIO Y EMERGENCIA')]
CATALOGO = [
    # ---- 01 evacuación y emergencia
    ('SALIDA', '01', 'SEÑAL DE SALIDA CON BRAILLE', 'und', '0.30 x 0.20 m', FOTOLUM, '2.10 m',
     'Indica la puerta de salida y la dirección de la ruta de evacuación; sobre el dintel de las puertas de salida y en la circulación peatonal interna.'),
    ('ZONA SEGURA EN', '01', 'SEÑAL DE ZONA SEGURA EN CASO DE SISMO CON BRAILLE', 'und', '0.20 x 0.30 m', FOTOLUM, '1.80 m',
     'Identifica los lugares de protección dentro de los ambientes (columnas y muros estructurales) durante un sismo.'),
    ('LETRERO DE AFORO', '01', 'LETRERO DE AFORO CON BRAILLE', 'und', '0.30 x 0.20 m', VINIL, '2.10 m',
     'Indica la capacidad máxima de personas del ambiente; junto al ingreso, en el lado de la cerradura.'),
    ('ZONA DE REUNI', '01', 'ZONA DE REUNIÓN (ZONA SEGURA EXTERNA) PINTADA EN PISO', 'und', 'círculo de 1.50 m de radio, línea de 0.10 m',
     'Pintura de tránsito color amarillo sobre piso de concreto', 'en piso',
     'Lugar exterior de concentración de los ocupantes al final de cada ruta de evacuación (S1 a S13 de la lámina SE-E-01).'),
    # ---- 02 equipos contra incendio
    ('SEÑAL DE UBICACIÓN DE EXTINTOR PQS', '02', 'SEÑAL DE UBICACIÓN DE EXTINTOR PQS CON BRAILLE', 'und', '0.20 x 0.30 m', FOTOLUM, '1.80 m',
     'Identifica la ubicación del extintor de polvo químico seco; sobre el equipo.'),
    ('SEÑAL DE UBICACIÓN DE EXTINTOR CO2', '02', 'SEÑAL DE UBICACIÓN DE EXTINTOR CO2 CON BRAILLE', 'und', '0.20 x 0.30 m', FOTOLUM, '1.80 m',
     'Identifica la ubicación del extintor de dióxido de carbono; sobre el equipo.'),
    ('ALARMA CONTRA', '02', 'SEÑAL DE ALARMA CONTRA INCENDIOS CON BRAILLE', 'und', '0.20 x 0.30 m', FOTOLUM, '1.80 m',
     'Identifica la estación manual (pulsador) de alarma contra incendios.'),
    ('AVISADOR SONORO', '02', 'SEÑAL DE AVISADOR SONORO CON BRAILLE', 'und', '0.20 x 0.30 m', FOTOLUM, '2.00 m',
     'Identifica la sirena o avisador sonoro del sistema de alarma.'),
    ('CENTRAL DE ALARMA', '02', 'SEÑAL DE CENTRAL DE ALARMA CONTRA INCENDIO CON BRAILLE', 'und', '0.20 x 0.30 m', FOTOLUM, '1.10 m',
     'Identifica el panel central del sistema de detección y alarma.'),
    # ---- 03 advertencia y prohibición
    ('ATENCIÓN RIESGO', '03', 'SEÑAL DE ATENCIÓN RIESGO ELÉCTRICO CON BRAILLE', 'und', '0.20 x 0.30 m', VINIL, '1.10 m',
     'Advierte la presencia de tableros y equipos eléctricos; en la puerta o frente del tablero.'),
    ('RIESGO DE DESCARGA', '03', 'SEÑAL DE RIESGO DE DESCARGA ELÉCTRICA CON BRAILLE', 'und', '0.20 x 0.30 m', VINIL, '1.10 m',
     'Advierte el riesgo de descarga eléctrica en tableros, subestación y grupo electrógeno.'),
    ('PROHIBIDO EL INGRESO', '03', 'SEÑAL DE PROHIBIDO EL INGRESO SOLO PERSONAL AUTORIZADO CON BRAILLE', 'und', '0.30 x 0.20 m', VINIL, '1.10 m',
     'Restringe el ingreso a los ambientes técnicos al personal autorizado.'),
    # ---- 04 informativas
    ('SEÑALES DE SERVICIOS HIGIENICOS PHD', '04', 'SEÑAL DE SERVICIOS HIGIÉNICOS PARA PERSONAS CON DISCAPACIDAD CON BRAILLE', 'und', '0.20 x 0.20 m', VINIL, '1.80 m',
     'Identifica el servicio higiénico accesible.'),
    ('SEÑALES DE SERVICIOS HIGIENICOS MIXTO', '04', 'SEÑAL DE SERVICIOS HIGIÉNICOS MIXTO CON BRAILLE', 'und', '0.20 x 0.20 m', VINIL, '1.80 m',
     'Identifica el servicio higiénico de uso mixto.'),
    ('SEÑALES DE SERVICIOS HIGIENICOS MUJER', '04', 'SEÑAL DE SERVICIOS HIGIÉNICOS MUJER CON BRAILLE', 'und', '0.20 x 0.20 m', VINIL, '1.80 m',
     'Identifica el servicio higiénico de mujeres.'),
    ('SEÑALES DE SERVICIOS HIGIENICOS VAR', '04', 'SEÑAL DE SERVICIOS HIGIÉNICOS VARÓN CON BRAILLE', 'und', '0.20 x 0.20 m', VINIL, '1.80 m',
     'Identifica el servicio higiénico de varones.'),
    ('BOTIQUIN', '04', 'SEÑAL DE BOTIQUÍN DE PRIMEROS AUXILIOS CON BRAILLE', 'und', '0.20 x 0.30 m', FOTOLUM, '1.80 m',
     'Identifica la ubicación del botiquín de primeros auxilios.'),
    ('PUNTO ECOL', '04', 'SEÑAL DE PUNTO ECOLÓGICO CON BRAILLE', 'und', '0.30 x 0.20 m', VINIL, '1.80 m',
     'Identifica el punto de acopio selectivo de residuos sólidos.'),
    # ---- 05 equipos
    ('UNIDAD DE LUCES', '05', 'UNIDAD DE LUCES DE EMERGENCIA', 'und', 'equipo de dos faros LED, autonomía mínima 90 min', 'Equipo autónomo con batería recargable, 220 V', '2.10 m',
     'Ilumina las rutas de evacuación y las salidas al cortarse la energía.'),
    ('DETECTOR DE HUMO', '05', 'DETECTOR DE HUMO', 'und', 'detector fotoeléctrico de techo', 'Equipo fotoeléctrico con base de montaje', 'techo',
     'Detecta el humo en los ambientes y activa la alarma.'),
]
# equipos que la leyenda solo señala: el extintor se cuenta con su señal (una por equipo)
EQUIPOS = [
    ('SEÑAL DE UBICACIÓN DE EXTINTOR PQS', 'EXTINTOR DE POLVO QUÍMICO SECO (PQS) TIPO ABC DE 6 kg', 'und', 'extintor portátil de 6 kg, agente PQS multipropósito ABC',
     'Cilindro de acero con manómetro, manguera, soporte de pared y tarjeta de control', '1.50 m (parte superior)',
     'Combate fuegos de clase A, B y C en las edificaciones.'),
    ('SEÑAL DE UBICACIÓN DE EXTINTOR CO2', 'EXTINTOR DE DIÓXIDO DE CARBONO (CO2) DE 10 lb', 'und', 'extintor portátil de 10 lb, agente CO2',
     'Cilindro de acero sin costura con válvula, manguera con difusor, soporte de pared y tarjeta de control', '1.50 m (parte superior)',
     'Combate fuegos de clase B y C (equipos eléctricos de la cocina).'),
]


def plano():
    return json.load(open(PLANO, encoding='utf-8'))


def edificaciones(P=None):
    P = P or plano()
    return [(e['codigo'], e['nombre']) for e in P['edificaciones']] + [(P['exterior']['codigo'], 'Exteriores')]


def _fila(P, clave):
    return next(f for f in P['leyenda'] if f['descripcion'].upper().startswith(clave.upper()))


def partidas(P=None):
    """Partidas en orden, con cantidad por edificación (o sin ubicar), cantidad de la leyenda y fuente."""
    P = P or plano()
    eds = [c for c, _ in edificaciones(P)]
    out = []
    for g, titulo in GRUPOS:
        out.append(dict(item=g, desc=titulo, und=None))
        filas = [c for c in CATALOGO if c[1] == g]
        if g == '05':
            filas = [(e[0], g) + e[1:] for e in EQUIPOS] + filas
        for k, (clave, _, desc, und, dim, mat, alt, uso) in enumerate(filas, 1):
            f = _fila(P, clave)
            reg = dict(item='%s.%02d' % (g, k), desc=desc, und=und, dim=dim, material=mat, altura=alt, uso=uso, clave=clave,
                       leyenda=f['cantidad'], altura_leyenda=f['altura'], desc_leyenda=f['descripcion'])
            if g == '05' and clave.startswith('SEÑAL DE UBICACIÓN'):
                reg['altura_leyenda'] = None                 # la altura de la leyenda es la de la señal, no la del equipo
            if clave.startswith('ZONA DE REUNI'):
                n = P['evacuacion']['circulos_zona_segura']
                reg.update(por=dict(EXT=n), sin_ubicar=0, total=n, fuente='Lámina SE-E-01: zonas seguras S1 a S%d dibujadas' % n)
            elif f['planta'] is None:
                reg.update(por={}, sin_ubicar=f['cantidad'], total=f['cantidad'],
                           fuente='Leyenda de SE-S-01 (el símbolo es una imagen pegada sin ubicación en el DXF)')
            else:
                reg.update(por={e: f['por_edificacion'].get(e, 0) for e in eds}, sin_ubicar=0, total=f['planta'],
                           fuente='Planta de SE-S-01: símbolos dibujados (leyenda: %d)' % f['cantidad'])
            out.append(reg)
    return out


def rutas(P=None):
    """Rutas de evacuación de SE-E-01: número, ambiente, longitud y tiempo de desplazamiento.
    La ruta 02 (servicios generales) tiene en la planta el rótulo "RUTA 03- 15.51ml": se identifica por su ubicación (E-10)."""
    P = P or plano(); ev = P['evacuacion']; eds = {e['codigo']: e for e in P['edificaciones']}
    L = {}
    for n, lista in ev['rutas'].items():
        for r in lista:
            c = eds['E-10']['caja']
            n2 = 2 if (int(n) == 3 and c[0] <= r['x'] <= c[2] and c[1] <= r['y'] <= c[3]) else int(n)
            L[n2] = r['L']
    out = []
    for n in sorted(L):
        amb = ev['rutas_leyenda'].get(str(n), ev['rutas_leyenda'].get(n, ''))
        for a, b in (('Administracion', 'Administración'), ('Modulo', 'Módulo'), ('Baños Públicos', 'SS.HH. público'), ('Servicios Generales', 'Servicios generales')):
            amb = amb.replace(a, b)
        out.append(dict(n=n, ambiente=amb, L=L[n],
                        t=L[n] / V_EVAC, cumple=L[n] <= D_MAX))
    return out


def aforos(P=None):
    P = P or plano(); nom = dict(edificaciones(P))
    out = {}
    for a in P['evacuacion']['aforos']:
        out.setdefault(a['edificacion'], []).append(a['personas'])
    filas = []
    for cod, nombre in edificaciones(P):
        if cod not in out:
            continue
        v = sorted(set(out[cod]), reverse=True)
        if cod == 'E-08':
            filas.append((cod, 'SUM', v[0])); filas.append((cod, 'Cocina', v[1]))
        elif cod == 'EXT':
            filas.append((cod, 'Caseta de control (O.E. 04)', v[0]))
        else:
            filas.append((cod, nombre, v[0]))
    return filas


def zona_segura():
    z = ZONA_SEGURA
    per = 2 * math.pi * z['radio']
    return dict(z, perimetro=per, area=per * z['ancho'])


if __name__ == '__main__':
    for p in partidas():
        print(p['item'], p['desc'], p.get('total', ''), p.get('fuente', ''))
    for r in rutas():
        print(r)
    print(aforos(), POBLACION, zona_segura())


def zonas(P=None):
    """Zonas seguras S1 a S13 de SE-E-01 con la edificación más cercana (distancia al contorno)."""
    P = P or plano()
    out = []
    for z in P['evacuacion']['zonas_seguras']:
        def dist(e):
            c = e['caja']; dx = max(c[0] - z['x'], 0, z['x'] - c[2]); dy = max(c[1] - z['y'], 0, z['y'] - c[3])
            return math.hypot(dx, dy)
        e = min(P['edificaciones'], key=dist)
        out.append(dict(nombre=z['nombre'], x=z['x'], y=z['y'], cerca='%s %s' % (e['codigo'], e['nombre']), d=round(dist(e), 1)))
    return out
