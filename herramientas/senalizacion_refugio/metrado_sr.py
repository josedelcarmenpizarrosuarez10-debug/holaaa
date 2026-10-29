# -*- coding: utf-8 -*-
"""Metrado de señalización y seguridad - Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514), en Excel con fórmulas.

Cantidades del plano de señalización de la arquitecta (datos_sr.py / lee_plano_sr.py): cada señal y equipo contado en la
planta de la lámina SE-S-02 y repartido por edificación (E-01 a E-09 y exteriores), cotejado con la columna CANTIDAD de su
leyenda; la señal de atención riesgo eléctrico, que en el DXF es una imagen pegada sin ubicación, en la columna SIN UBICAR.

Hojas: RESUMEN (partidas y metrado, enlazado), METRADO (por edificación, total = suma, cotejo con la leyenda),
LEYENDA (cada fila de la leyenda del plano con lo dibujado en la planta), POBLACIÓN (ocupantes del hogar),
SEÑALES (dimensiones, material y altura de cada partida). Formato del metrado de señalización del CAR Varones.

Uso: python3 herramientas/senalizacion_refugio/metrado_sr.py
Salida: entregables/METRADO_SENALIZACION_Y_SEGURIDAD_HOGAR_REFUGIO.xlsx
"""
import os
import sys

import openpyxl
from openpyxl.utils import get_column_letter as L

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI)
for d in (AQUI, os.path.join(HER, 'varones', 'senalizacion')):
    sys.path.insert(0, d)
import datos_sr as D  # noqa: E402
import metrado_se as MS  # noqa: E402  (celdas, encabezado, impresión y hoja SEÑALES del metrado del CAR Varones)

MS.D = D                                                          # encabezado con el proyecto, el CUI y las láminas del hogar
celda, cabecera, impresion = MS.celda, MS.cabecera, MS.impresion
GRANATE, ROSA, GRIS, IZQ = MS.GRANATE, MS.ROSA, MS.GRIS, MS.IZQ
SALIDA = os.path.join(D.SAL, 'METRADO_SENALIZACION_Y_SEGURIDAD_HOGAR_REFUGIO.xlsx')


def hoja_metrado(wb, P, pts):
    ws = wb.create_sheet('METRADO')
    eds = D.edificaciones(P)
    n_e = len(eds)
    c_sin = 4 + n_e; c_tot = c_sin + 1; c_ley = c_tot + 1; c_dif = c_ley + 1; c_fue = c_dif + 1
    r = cabecera(ws, 'METRADO DE SEÑALIZACIÓN Y SEGURIDAD POR EDIFICACIÓN', c_fue)
    cab = ['ITEM', 'DESCRIPCIÓN', 'UND'] + [c for c, _ in eds] + ['SIN UBICAR', 'TOTAL', 'LEYENDA %s' % D.LS, 'DIFERENCIA',
                                                                 'FUENTE DE LA CANTIDAD']
    for k, v in enumerate(cab, 1):
        celda(ws, r, k, v, True, GRANATE, 'FFFFFF')
    for k, (_, nombre) in enumerate(eds, 4):
        celda(ws, r + 1, k, nombre, False, ROSA, size=7)
    for k in list(range(1, 4)) + list(range(c_sin, c_fue + 1)):
        ws.merge_cells(start_row=r, start_column=k, end_row=r + 1, end_column=k)
    ws.row_dimensions[r + 1].height = 60
    r += 2; filas = {}; r0 = r
    for p in pts:
        if p['und'] is None:
            celda(ws, r, 1, p['item'], True, GRIS); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=c_fue)
            celda(ws, r, 2, p['desc'], True, GRIS, al=IZQ)
            for c in range(3, c_fue + 1): ws.cell(r, c).border = MS.BORDE
            r += 1; continue
        celda(ws, r, 1, p['item']); celda(ws, r, 2, p['desc'], al=IZQ); celda(ws, r, 3, p['und'])
        for k, (cod, _) in enumerate(eds, 4):
            v = p['por'].get(cod, 0)
            celda(ws, r, k, v if v else None, fmt='0')
        celda(ws, r, c_sin, p['sin_ubicar'] or None, fmt='0')
        celda(ws, r, c_tot, '=SUM(%s%d:%s%d)' % (L(4), r, L(c_sin), r), True, ROSA, fmt='0')
        celda(ws, r, c_ley, p['leyenda'], fmt='0')
        celda(ws, r, c_dif, '=%s%d-%s%d' % (L(c_tot), r, L(c_ley), r), fmt='+0;-0;"conforme"')
        celda(ws, r, c_fue, p['fuente'], al=IZQ, size=8)
        filas[p['item']] = r; r += 1
    celda(ws, r, 2, 'TOTAL DE SEÑALES Y EQUIPOS', True, ROSA, al=IZQ)
    for c in range(4, c_tot + 1):
        celda(ws, r, c, '=SUM(%s%d:%s%d)' % (L(c), r0, L(c), r - 1), True, ROSA, fmt='0')
    for c in (1, 3, c_ley, c_dif, c_fue): celda(ws, r, c, None, fondo=ROSA)
    r += 2
    notas = ['Notas:',
             '1. Cantidad por edificación: cada símbolo de la planta de la lámina %s se asigna a la edificación donde está (contorno del '
             'bloque de la planta general, con 0.60 m de margen para las señales de fachada); EXT = exteriores (patios, '
             'estacionamientos, puntos ecológicos y circulaciones). No se metran las copias de símbolos que están fuera del terreno.' % D.LS,
             '2. SIN UBICAR: la señal de atención riesgo eléctrico es en el DXF una imagen pegada (OLE) que no exporta su ubicación; '
             'se metran las 39 imágenes de igual tamaño del espacio modelo (la leyenda indica 38). Se instalan en los tableros y '
             'ambientes eléctricos que indica la lámina, en coordinación con el plano de instalaciones eléctricas.',
             '3. Unidad de luces de emergencia: los bloques "LE" (77) y "A$C7A2016C2" (38) son el mismo símbolo de la leyenda '
             '(el primero contiene al segundo); se suman los dos: 115 und. La leyenda indica 77.',
             '4. Extintores: uno por cada señal de ubicación de extintor de la planta (33), PQS tipo ABC de 9 kg.',
             '5. DIFERENCIA = metrado - leyenda: las filas distintas de "conforme" son correcciones a la leyenda del plano '
             '(nota de observaciones de señalización).',
             '6. Unidades de luces de emergencia y detectores de humo: su conexión y circuitos son de instalaciones eléctricas.']
    for t in notas:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=c_fue)
        celda(ws, r, 1, t, t == 'Notas:', al=IZQ, borde=False, size=8); ws.row_dimensions[r].height = 12 if t == 'Notas:' else 26; r += 1
    for c, w in zip(range(1, c_fue + 1), [7, 46, 5] + [7] * n_e + [7.5, 7.5, 8.5, 9, 44]):
        ws.column_dimensions[L(c)].width = w
    ws.freeze_panes = ws.cell(10, 4)
    impresion(ws, c_fue, r)
    return filas, c_tot, c_ley


def hoja_leyenda(wb, P):
    """Cada fila de la leyenda del plano, con la cantidad dibujada en la planta y la que se metra."""
    ws = wb.create_sheet('LEYENDA')
    r = cabecera(ws, 'COTEJO DE LA LEYENDA DE LA LÁMINA %s CON LA PLANTA' % D.LS, 7)
    for k, v in enumerate(['N.°', 'FILA DE LA LEYENDA (TEXTO DEL PLANO)', 'ALTURA EN LA LEYENDA', 'CANTIDAD EN LA LEYENDA',
                           'DIBUJADO EN LA PLANTA', 'DIFERENCIA', 'OBSERVACIÓN'], 1):
        celda(ws, r, k, v, True, GRANATE, 'FFFFFF')
    r += 1; r0 = r
    pts = {p['clave']: p for p in D.partidas(P) if p['und'] and not p['desc'].startswith('EXTINTOR DE')}
    for n, f in enumerate(P['leyenda'], 1):
        p = next((x for k, x in pts.items() if f['descripcion'].upper().startswith(k.upper())), None)
        dib = p['total'] if p else 0
        if p is None:
            obs = 'Sin símbolos en la planta; no se metra.' if not f['cantidad'] else 'Revisar.'
        elif p['bloques'] is None:
            obs = 'Imagen pegada (OLE): %d imágenes en el espacio modelo, sin ubicación.' % dib
        elif dib == (f['cantidad'] or 0):
            obs = 'Conforme.'
        else:
            obs = 'Corregir la leyenda a %d (lo dibujado).' % dib
        celda(ws, r, 1, n); celda(ws, r, 2, f['descripcion'], al=IZQ); celda(ws, r, 3, f['altura'] or '—')
        celda(ws, r, 4, f['cantidad'] or 0, fmt='0'); celda(ws, r, 5, dib, fmt='0')
        celda(ws, r, 6, '=E%d-D%d' % (r, r), fmt='+0;-0;"conforme"'); celda(ws, r, 7, obs, al=IZQ, size=8)
        r += 1
    celda(ws, r, 2, 'TOTAL', True, ROSA, al=IZQ)
    for c in (4, 5, 6):
        celda(ws, r, c, '=SUM(%s%d:%s%d)' % (L(c), r0, L(c), r - 1), True, ROSA, fmt='0')
    for c in (1, 3, 7): celda(ws, r, c, None, fondo=ROSA)
    for c, w in zip(range(1, 8), [5, 50, 10, 11, 11, 11, 48]):
        ws.column_dimensions[L(c)].width = w
    impresion(ws, 7, r, horizontal=False)


def hoja_poblacion(wb):
    ws = wb.create_sheet('POBLACIÓN')
    r = cabecera(ws, 'POBLACIÓN DEL HOGAR (OCUPANTES PARA LA EVACUACIÓN)', 5)
    for k, v in enumerate(['HABITACIÓN', 'CANTIDAD', 'CAMAS / PLAZAS POR HABITACIÓN', 'PLAZAS'], 1):
        celda(ws, r, k, v, True, GRANATE, 'FFFFFF')
    r += 1; r0 = r
    for a, n, c in D.PLAZAS:
        celda(ws, r, 1, a, al=IZQ); celda(ws, r, 2, n, fmt='0'); celda(ws, r, 3, c, fmt='0'); celda(ws, r, 4, '=B%d*C%d' % (r, r), fmt='0'); r += 1
    celda(ws, r, 1, 'RESIDENTES (mujeres con sus hijas e hijos)', True, ROSA, al=IZQ)
    celda(ws, r, 2, '=SUM(B%d:B%d)' % (r0, r - 1), True, ROSA, fmt='0'); celda(ws, r, 3, None, fondo=ROSA)
    celda(ws, r, 4, '=SUM(D%d:D%d)' % (r0, r - 1), True, ROSA, fmt='0'); rr = r; r += 2
    for k, v in enumerate(['POBLACIÓN', 'DETALLE', '', 'PERSONAS'], 1):
        if v: celda(ws, r, k, v, True, GRANATE, 'FFFFFF')
    r += 1
    celda(ws, r, 1, 'Residentes', al=IZQ); celda(ws, r, 2, 'Plazas de las habitaciones (A.030 art. 5)', al=IZQ)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3); celda(ws, r, 4, '=D%d' % rr, fmt='0'); a = r; r += 1
    celda(ws, r, 1, 'Personal', al=IZQ); celda(ws, r, 2, 'Administrativo, atención especializada, mantenimiento y vigilancia', al=IZQ)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3); celda(ws, r, 4, D.POBLACION['personal'], fmt='0'); b = r; r += 1
    celda(ws, r, 1, 'Permanentes', True, ROSA, al=IZQ); celda(ws, r, 2, 'Residentes + personal', True, ROSA, al=IZQ)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3); celda(ws, r, 4, '=D%d+D%d' % (a, b), True, ROSA, fmt='0'); c = r; r += 1
    celda(ws, r, 1, 'Temporales', al=IZQ); celda(ws, r, 2, 'Visitas, talleres, sala de reuniones y personal eventual', al=IZQ)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3); celda(ws, r, 4, D.POBLACION['temporales'], fmt='0'); t = r; r += 1
    celda(ws, r, 1, 'CAPACIDAD MÁXIMA', True, ROSA, al=IZQ); celda(ws, r, 2, 'Permanentes + temporales', True, ROSA, al=IZQ)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3); celda(ws, r, 4, '=D%d+D%d' % (c, t), True, ROSA, fmt='0'); r += 2
    for txt in ['Fuente: residentes = tabla de plazas de la memoria descriptiva de arquitectura (23 habitaciones); personal y '
                'temporales = memoria de evacuación de arquitectura del hogar.']:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        celda(ws, r, 1, txt, al=IZQ, borde=False, size=8); ws.row_dimensions[r].height = 26; r += 1
    for k, w in zip(range(1, 5), [40, 30, 18, 12]):
        ws.column_dimensions[L(k)].width = w
    impresion(ws, 4, r, horizontal=False)


def generar():
    P = D.plano(); pts = D.partidas(P)
    err = D.comprobacion(P)
    if err:
        raise ValueError('; '.join(err))
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'RESUMEN'
    filas, c_tot, c_ley = hoja_metrado(wb, P, pts)
    hoja_leyenda(wb, P); hoja_poblacion(wb); MS.hoja_senales(wb, pts)
    r = cabecera(ws, 'RESUMEN DE METRADOS - SEÑALIZACIÓN Y SEGURIDAD', 4)
    for k, v in enumerate(['ITEM', 'DESCRIPCIÓN', 'UND', 'METRADO'], 1):
        celda(ws, r, k, v, True, GRANATE, 'FFFFFF')
    r += 1
    celda(ws, r, 1, '01', True, GRIS); celda(ws, r, 2, 'SEÑALIZACIÓN Y SEGURIDAD', True, GRIS, al=IZQ)
    celda(ws, r, 3, None, fondo=GRIS); celda(ws, r, 4, None, fondo=GRIS); r += 1
    for p in pts:
        it = '01.' + p['item']
        if p['und'] is None:
            celda(ws, r, 1, it, True); celda(ws, r, 2, p['desc'], True, al=IZQ); celda(ws, r, 3, None); celda(ws, r, 4, None)
        else:
            celda(ws, r, 1, it); celda(ws, r, 2, p['desc'], al=IZQ); celda(ws, r, 3, p['und'])
            celda(ws, r, 4, "='METRADO'!%s%d" % (L(c_tot), filas[p['item']]), True, fmt='0.00')
        r += 1
    for c, w in zip(range(1, 5), [11, 70, 7, 12]):
        ws.column_dimensions[L(c)].width = w
    impresion(ws, 4, r - 1, horizontal=False)
    for w in wb.worksheets:
        w.sheet_view.showGridLines = False
    wb.properties.creator = ''; wb.properties.title = 'Metrado de señalización y seguridad - Hogar de Refugio Temporal'
    wb.save(SALIDA)
    return SALIDA, pts


if __name__ == '__main__':
    s, pts = generar()
    print(s)
