# -*- coding: utf-8 -*-
"""Hogar de Refugio Temporal (CUI 2675514): ACU aparte, en un Excel nuevo, de las partidas que el usuario marcó en amarillo en la
hoja RESUMEN de su metrado (nombre sombreado):

  01.04.03.04.03.04  LLORADERO DE TUBERIA PVC Ø3" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m (CUNETA COLINDANTE CON AREA VERDE)
  01.04.03.05.01.05  TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA SECCIÓN 0.25m x 0.20m
  01.04.03.05.04.01  CANALETA DE PLANCHA DE ACERO GALVANIZADO e=0.50mm, SECCIÓN 0.18m x 0.21m  (bancas OC-01)
  01.04.03.05.04.03  TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA SECCIÓN 0.18m x 0.21m      (bancas OC-01)
  01.04.04.05.01     TAPA DE REGISTRO CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08
  01.04.04.06.01     JUNTA DE DILATACION E=1" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR
  01.04.04.06.02     JUNTA E=1" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO

Base: las hojas ACU de la planilla del Refugio (entregables/METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx: ACU LLORADEROS,
ACU CANALETAS (ACU 3), ACU TAPA REGISTRO, ACU JUNTA DILATACION, ACU JUNTA CERCO y COSTO HORA HOMBRE 2026), copiadas con su
formato. Las fórmulas internas de cada ACU se conservan; las que leían otras hojas de la planilla (parámetros, desagregados,
insumos) pasan a valor (recalculado con LibreOffice). El metrado de cada partida se toma del archivo del usuario (hoja RESUMEN)
y la mano de obra de la hoja COSTO HORA HOMBRE 2026 (CAPECO-FTCCP 2026). Las dos partidas de las bancas OC-01 no tenían ACU:
se arman con el mismo criterio de las canaletas de techo (plancha de 0.50 mm, una pieza por techo, sin uniones).

Uso: python3 herramientas/acu_partidas_amarillas_refugio.py <metrado del usuario.xlsx>
Salida: entregables/ACU_PARTIDAS_RESALTADAS_HOGAR_REFUGIO.xlsx
"""
import copy
import os
import re
import shutil
import subprocess
import sys
import tempfile

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANILLA = os.path.join(RAIZ, 'entregables', 'METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx')
SALIDA = os.path.join(RAIZ, 'entregables', 'ACU_PARTIDAS_RESALTADAS_HOGAR_REFUGIO.xlsx')
RES = 'RESUMEN ACU'
CHH = 'COSTO HORA HOMBRE 2026'
# (ítem del metrado, hoja de la ACU, celda del metrado en la ACU, celda del costo unitario, celda del parcial)
PARTIDAS = [
    ('01.04.03.04.03.04', 'ACU LLORADEROS', 'C29', 'G47'),
    ('01.04.03.05.01.05', 'ACU TAPA LATERAL CANALETA', 'C27', 'G42'),
    ('01.04.03.05.04.01', 'ACU CANALETA BANCAS OC-01', 'C25', 'G38'),
    ('01.04.03.05.04.03', 'ACU CANALETA BANCAS OC-01', 'C43', 'G58'),
    ('01.04.04.05.01', 'ACU TAPA REGISTRO', 'C33', 'G54'),
    ('01.04.04.06.01', 'ACU JUNTA DILATACION', 'C30', 'G45'),
    ('01.04.04.06.02', 'ACU JUNTA CERCO', 'C30', 'G45'),
]
# nombres tal como el usuario los resaltó en su RESUMEN (las tapas laterales llevan la sección)
NOMBRES = {'01.04.03.05.01.05': 'TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA SECCIÓN 0.25m x 0.20m',
           '01.04.03.05.04.03': 'TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA SECCIÓN 0.18m x 0.21m'}
COPIAR = ['ACU LLORADEROS', 'ACU TAPA REGISTRO', 'ACU JUNTA DILATACION', 'ACU JUNTA CERCO', CHH]
REF = re.compile(r"(?:'([^']+)'|([A-Za-z][A-Za-z0-9_]*))!(\$?[A-Z]{1,3}\$?\d+)")


def recalculado(ruta):
    tmp = tempfile.mkdtemp(); shutil.copy(ruta, os.path.join(tmp, 'p.xlsx'))
    subprocess.run(['soffice', '--headless', '--convert-to', 'xlsx', '--outdir', os.path.join(tmp, 'c'), os.path.join(tmp, 'p.xlsx')],
                   check=True, capture_output=True)
    wb = openpyxl.load_workbook(os.path.join(tmp, 'c', 'p.xlsx'), data_only=True)
    shutil.rmtree(tmp)
    return wb


def estilo(dst, src):
    if src.has_style:
        dst.font = copy.copy(src.font); dst.fill = copy.copy(src.fill); dst.border = copy.copy(src.border)
        dst.alignment = copy.copy(src.alignment); dst.number_format = src.number_format


def copiar_hoja(F, V, nombre, destino, filas=None, desplazar=None, metrado=None, cabecera=None):
    """Copia la hoja con formato. Referencias a hojas que no viajan -> valor recalculado; a RESUMEN -> hoja RESUMEN ACU.
    desplazar = (fila_desde, salto): las filas >= fila_desde suben 'salto' filas (y sus referencias internas)."""
    fs, vs, ws = F[nombre], V[nombre], destino
    for k, dim in fs.column_dimensions.items():
        ws.column_dimensions[k].width = dim.width
    nuevo = lambda r: r - desplazar[1] if desplazar and r >= desplazar[0] else r

    for fila in fs.iter_rows():
        for c in fila:
            r = c.row
            if filas and r not in filas:
                continue
            d = ws.cell(nuevo(r), c.column)
            v = c.value
            if isinstance(v, str) and v.startswith('='):
                def externa(m):
                    hoja = m.group(1) or m.group(2); celda = m.group(3).replace('$', '')
                    if hoja == 'RESUMEN':
                        return "'%s'!%s" % (RES, cabecera[celda])
                    if hoja in COPIAR or hoja == nombre:
                        return m.group(0)
                    x = V[hoja][celda].value
                    return repr(round(x, 10)) if isinstance(x, float) else str(x)
                v = REF.sub(externa, v)
                if desplazar:                                          # referencias de la misma hoja
                    partes = re.split(r"('[^']*'![$A-Z0-9]+)", v)
                    v = ''.join(p if p.startswith("'") else re.sub(r'(\$?[A-Z]{1,3}\$?)(\d+)\b',
                                lambda m: m.group(1) + str(nuevo(int(m.group(2)))), p) for p in partes)
            d.value = v
            estilo(d, c)
    for rng in fs.merged_cells.ranges:
        if not filas or rng.min_row in filas:
            ws.merge_cells(start_row=nuevo(rng.min_row), start_column=rng.min_col, end_row=nuevo(rng.max_row), end_column=rng.max_col)
    if metrado:
        celda, ref = metrado
        ws[celda] = "='%s'!%s" % (RES, ref)


def bancas(ws, F, cabecera, ref_metrado):
    """ACU de la canaleta y de la tapa lateral de las bancas OC-01, con el formato de la hoja ACU CANALETAS."""
    t = F['ACU CANALETAS']
    for k, dim in t.column_dimensions.items():
        ws.column_dimensions[k].width = dim.width
    def fila(r, valores, plantilla):
        for col in range(1, 9):
            estilo(ws.cell(r, col), t.cell(plantilla, col))
        for col, v in valores.items():
            ws.cell(r, col).value = v
    fila(1, {1: 'ANALISIS DE COSTOS UNITARIOS - CANALETA DE TECHO DE BANCAS CON PERGOLA (OC-01)'}, 1)
    ws.merge_cells('A1:H1')
    for i, (et, c) in enumerate((('ENTIDAD', 'C2'), ('PROYECTO', 'C3'), ('UBICACIÓN', 'C4'), ('FECHA', 'C5')), 2):
        fila(i, {1: et, 3: "='%s'!%s" % (RES, cabecera[c])}, i)
    fila(7, {1: 'Analisis de las partidas 01.04.03.05.04.01 y 01.04.03.05.04.03 (3 juegos OC-01 de tres techos de 3.79, 4.21 y 3.79 m; '
                'laminas DPL-41 y DPL-42). Mismo criterio de las canaletas de techo (hoja ACU CANALETAS de la planilla).'}, 7)
    fila(9, {1: 'DATOS DE CALCULO (hoja METRADO CANALETA BANCAS y especificaciones tecnicas)'}, 9)
    fila(10, {1: 'N°', 2: 'DATO', 3: 'UND', 4: 'VALOR', 8: 'SUSTENTO'}, 10)
    datos = [('Ancho interior de la canaleta', 'm', 0.18, 'METRADO CANALETA BANCAS F18; laminas DPL-41 y DPL-42'),
             ('Altura interior de la canaleta', 'm', 0.21, 'METRADO CANALETA BANCAS F19'),
             ('Ala posterior apoyada sobre la viga de la pergola', 'm', 0.10, 'especificacion 01.04.03.05.04.01'),
             ('Desarrollo de plancha por metro de canaleta', 'm2/m', '=D11+2*D12+D13', 'fondo + 2 lados + ala = 0.70 m'),
             ('Espesor de plancha galvanizada', 'mm', 0.5, 'METRADO CANALETA BANCAS F20'),
             ('Peso de la plancha galvanizada', 'kg/m2', '=D15*7.85+0.3', 'espesor x 7.85 kg/m2 por mm + zinc (0.3 kg/m2)'),
             ('Pestana de la tapa lateral (contorno)', 'm', 0.02, 'especificacion 01.04.03.05.04.03'),
             ('Piezas por techo', 'und', 1, 'una sola pieza por techo, sin uniones ni traslapes (especificacion)')]
    for i, (a, u, v, s) in enumerate(datos, 11):
        fila(i, {1: i - 10, 2: a, 3: u, 4: v, 8: s}, 11 + min(i - 11, 11))
    # ACU 1: canaleta
    def acu(r0, titulo, und, ref, rend, nota, mo, mat, cu_txt):
        fila(r0, {1: titulo}, 25); ws.merge_cells(start_row=r0, start_column=1, end_row=r0, end_column=8)
        fila(r0 + 1, {1: 'Unidad', 3: und}, 26)
        fila(r0 + 2, {1: 'Metrado', 3: "='%s'!%s" % (RES, ref)}, 27)
        fila(r0 + 3, {1: 'Rendimiento (%s/dia)' % und, 3: rend, 5: nota}, 28)
        for c1, c2 in ((1, 2), (5, 8)):
            ws.merge_cells(start_row=r0 + 3, start_column=c1, end_row=r0 + 3, end_column=c2)
        for k in (1, 2):
            ws.merge_cells(start_row=r0 + k, start_column=1, end_row=r0 + k, end_column=2)
        ws.row_dimensions[r0 + 3].height = 30; ws.row_dimensions[r0 + 4].height = 31.5
        fila(r0 + 4, {1: 'N°', 2: 'RECURSO', 3: 'UND', 4: 'CUADRILLA', 5: 'CANTIDAD', 6: 'PRECIO S/', 7: 'PARCIAL S/', 8: 'SUSTENTO / FUENTE'}, 29)
        r = r0 + 5; n = 0
        fila(r, {2: 'MANO DE OBRA'}, 30); r += 1; ini = r
        for nom, cuad, g in mo:
            n += 1
            fila(r, {1: n, 2: nom, 3: 'hh', 4: cuad, 5: '=D%d*8/$C$%d' % (r, r0 + 3), 6: "='%s'!$G$%d" % (CHH, g), 7: '=E%d*F%d' % (r, r),
                     8: 'hoja COSTO HORA HOMBRE 2026 (tabla oficial CAPECO-FTCCP 2026)'}, 31)
            r += 1
        fila(r, {2: 'Subtotal mano de obra', 7: '=SUM(G%d:G%d)' % (ini, r - 1)}, 33); smo = r; r += 1
        fila(r, {2: 'MATERIALES'}, 34); r += 1; ini = r
        for nom, u, cant, pre, s in mat:
            n += 1
            fila(r, {1: n, 2: nom, 3: u, 5: cant, 6: pre, 7: '=E%d*F%d' % (r, r), 8: s}, 35)
            r += 1
        fila(r, {2: 'Subtotal materiales', 7: '=SUM(G%d:G%d)' % (ini, r - 1)}, 38); smat = r; r += 1
        fila(r, {2: 'EQUIPOS'}, 39); r += 1
        n += 1
        fila(r, {1: n, 2: 'Herramientas manuales', 3: '%mo', 5: 0.05, 6: '=+G%d' % smo, 7: '=E%d*F%d' % (r, r),
                 8: '5 % del costo de mano de obra (hojalateria)'}, 40); r += 1
        fila(r, {2: 'Subtotal equipos', 7: '=SUM(G%d:G%d)' % (r - 1, r - 1)}, 41); seq = r; r += 1
        fila(r, {1: cu_txt, 7: '=+G%d+G%d+G%d' % (smo, smat, seq)}, 42); cu = r; r += 1
        fila(r, {1: 'COSTO DIRECTO DE LA PARTIDA (metrado x costo unitario)', 7: '=G%d*C%d' % (cu, r0 + 2)}, 43)
        return cu
    for rng in ('A2:B2', 'A3:B3', 'A4:B4', 'A5:B5', 'C2:H2', 'C3:H3', 'C4:H4', 'C5:H5', 'A7:H7', 'A9:H9'):
        ws.merge_cells(rng)
    for r, h in ((1, 27), (2, 24.75), (3, 58.5), (4, 24.75), (5, 24.75), (7, 40), (9, 19.5), (10, 21.75)):
        ws.row_dimensions[r].height = h
    pl = "='PRECIOS DE INSUMOS'!$D$5"
    cu1 = acu(23, 'ACU 1: 01.04.03.05.04.01 CANALETA DE PLANCHA DE ACERO GALVANIZADO e=0.50mm, SECCIÓN 0.18m x 0.21m', 'm', ref_metrado[0], 25,
              'fabricacion en una pieza por techo (corte y doblado en obra) y colocacion sobre sus dos soportes; cuadrilla 1 op + 1 peon',
              [('Operario (hojalatero)', 1, 11), ('Peon', 1, 13)],
              [('Plancha de acero galvanizado e=0.50 mm', 'm2', '=$D$14*1.05', pl, 'desarrollo 0.70 m2/m x 1.05 desperdicio (sin traslapes: una pieza por techo)')],
              'COSTO UNITARIO DIRECTO (S/ por m)')
    cu2 = acu(41, 'ACU 2: 01.04.03.05.04.03 TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA SECCIÓN 0.18m x 0.21m', 'und', ref_metrado[1], 30,
              'trazo, corte, doblez de pestanas, remachado y sellado en el extremo de la canaleta; cuadrilla 1 op + 0.5 peon',
              [('Operario (hojalatero)', 1, 11), ('Peon', 0.5, 13)],
              [('Plancha de acero galvanizado e=0.50 mm', 'm2', '=($D$11*$D$12+2*($D$11+$D$12)*$D$17)*1.1', pl,
                'tapa 0.18 x 0.21 + pestana de 0.02 en el contorno, 10 % desperdicio'),
               ('Remache pop 1/8"', 'und', 6, "='PRECIOS DE INSUMOS'!$D$6", '6 por tapa'),
               ('Sellador de poliuretano (cartucho 300 ml)', 'und', '=($D$11+2*$D$12)/8', "='PRECIOS DE INSUMOS'!$D$7",
                'contorno de la tapa (0.60 m) / 8 m por cartucho')],
              'COSTO UNITARIO DIRECTO (S/ por und)')
    return cu1, cu2


def generar(metrado_usuario):
    F = openpyxl.load_workbook(PLANILLA)
    V = recalculado(PLANILLA)
    U = openpyxl.load_workbook(metrado_usuario, data_only=True)['RESUMEN']
    filas_u = {str(U.cell(r, 1).value).strip(): r for r in range(1, U.max_row + 1) if U.cell(r, 1).value}
    wb = openpyxl.Workbook(); R = wb.active; R.title = RES
    cab = {'C2': 'C4', 'C3': 'C5', 'C4': 'C6', 'C5': 'C7', 'B4': 'C4', 'B5': 'C5', 'B6': 'C6', 'B7': 'C7'}
    # ---- hoja resumen (formato de la hoja RESUMEN del usuario)
    fino = Side(style='thin', color='808080'); borde = Border(left=fino, right=fino, top=fino, bottom=fino)
    azul = PatternFill('solid', fgColor='1F4E79'); celeste = PatternFill('solid', fgColor='EAF4FB'); amarillo = PatternFill('solid', fgColor='FFFF00')
    R['A1'] = 'ANALISIS DE COSTOS UNITARIOS - PARTIDAS RESALTADAS DEL METRADO DE DRENAJE PLUVIAL'
    R['A1'].font = Font(name='Arial Narrow', size=14, bold=True, color='1F4E79'); R.merge_cells('A1:G1')
    for i, (et, r) in enumerate((('ENTIDAD', 4), ('PROYECTO', 5), ('UBICACIÓN', 6), ('FECHA', 7)), 4):
        R.cell(i, 1, et).font = Font(name='Arial Narrow', bold=True)
        v = U.cell(r, 2).value
        R.cell(i, 3, v.strftime('%d/%m/%Y') if hasattr(v, 'strftime') else v).font = Font(name='Arial Narrow')
        R.cell(i, 3).alignment = Alignment(wrap_text=True, vertical='center'); R.merge_cells(start_row=i, start_column=3, end_row=i, end_column=7)
    R.row_dimensions[5].height = 62
    cab_r = 9
    for col, t in enumerate(('Item', 'Descripción', 'Und', 'Metrado', 'C.U. S/', 'Parcial S/', 'Hoja ACU'), 1):
        c = R.cell(cab_r, col, t); c.font = Font(name='Arial Narrow', bold=True, color='FFFFFF'); c.fill = azul; c.border = borde
        c.alignment = Alignment(horizontal='center', vertical='center')
    ref_metrado, filas_res = {}, []
    for k, (item, hoja, cm, ccu) in enumerate(PARTIDAS):
        r = cab_r + 1 + k; ru = filas_u[item]
        vals = [item, NOMBRES.get(item, U.cell(ru, 2).value), U.cell(ru, 3).value, U.cell(ru, 4).value, "='%s'!%s" % (hoja, ccu), '=D%d*E%d' % (r, r), hoja]
        for col, v in enumerate(vals, 1):
            c = R.cell(r, col, v); c.font = Font(name='Arial Narrow'); c.border = borde
            c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='left' if col in (2, 7) else 'center')
        R.cell(r, 2).fill = amarillo
        for col in (4, 5, 6):
            R.cell(r, col).number_format = '#,##0.00'
        ref_metrado[item] = 'D%d' % r; filas_res.append(r)
    rt = cab_r + 1 + len(PARTIDAS)
    R.cell(rt, 2, 'COSTO DIRECTO TOTAL DE LAS PARTIDAS RESALTADAS').font = Font(name='Arial Narrow', bold=True)
    R.cell(rt, 6, '=SUM(F%d:F%d)' % (filas_res[0], filas_res[-1])).font = Font(name='Arial Narrow', bold=True)
    R.cell(rt, 6).number_format = '#,##0.00'
    for col in range(1, 8):
        R.cell(rt, col).fill = celeste; R.cell(rt, col).border = borde
    nota = rt + 2
    for i, t in enumerate(('Notas:',
                           'Metrados tomados de la hoja RESUMEN del metrado de drenaje pluvial (partidas con el nombre resaltado en amarillo).',
                           'Mano de obra: tabla oficial CAPECO-FTCCP 2026 (operario 28.95, oficial 22.68, peon 20.54 S/ hh). Precios sin IGV, con su fuente en cada ACU.',
                           'Costo directo; no incluye gastos generales, utilidad ni IGV.')):
        R.cell(nota + i, 1, t).font = Font(name='Arial Narrow', size=9, italic=i > 0, bold=i == 0)
    for col, w in zip('ABCDEFG', (17, 62, 6, 11, 11, 13, 28)):
        R.column_dimensions[col].width = w
    R.row_dimensions[cab_r].height = 18
    for r in filas_res:
        R.row_dimensions[r].height = 30
    # ---- precios de insumos de las bancas (los demás van con su fuente en cada ACU)
    P = wb.create_sheet('PRECIOS DE INSUMOS')
    P['A1'] = 'PRECIOS DE INSUMOS PARA LAS ACU DE LAS BANCAS OC-01 (sin IGV)'; P['A1'].font = Font(name='Arial Narrow', size=12, bold=True, color='1F4E79')
    for col, t in enumerate(('N°', 'INSUMO', 'UND', 'PRECIO S/', 'FUENTE'), 1):
        c = P.cell(4, col, t); c.font = Font(name='Arial Narrow', bold=True, color='FFFFFF'); c.fill = azul; c.border = borde
    pv = V['ACU CANALETAS']
    filas_p = [('Plancha de acero galvanizado e=0.50 mm', 'm2', '=%s*(0.5*7.85+0.3)/(0.9*7.85+0.3)' % pv['F75'].value,
                'Referencial: precio por kg de la plancha de 0.9 mm de la ACU CANALETAS (S/ %.2f por m2, Mercado Tarapoto 2026) aplicado al peso de la de 0.50 mm '
                '(4.225 frente a 7.365 kg/m2). Por cotizar en Tarapoto.' % pv['F75'].value),
               ('Remache pop 1/8"', 'und', pv['F76'].value, 'mismo precio de la ACU CANALETAS de la planilla (Mercado Tarapoto 2026, sin IGV)'),
               ('Sellador de poliuretano (cartucho 300 ml)', 'und', pv['F77'].value, 'mismo precio de la ACU CANALETAS de la planilla (sin IGV)')]
    for i, (a, u, p, s) in enumerate(filas_p, 5):
        for col, v in enumerate((i - 4, a, u, p, s), 1):
            c = P.cell(i, col, v); c.font = Font(name='Arial Narrow'); c.border = borde; c.alignment = Alignment(wrap_text=True, vertical='center')
        P.cell(i, 4).number_format = '#,##0.00'; P.row_dimensions[i].height = 42 if i == 5 else 18
    for col, w in zip('ABCDE', (5, 40, 6, 11, 90)):
        P.column_dimensions[col].width = w
    # ---- ACU copiadas de la planilla
    hojas = {}
    for hoja, celda in (('ACU LLORADEROS', 'C29'), ('ACU TAPA REGISTRO', 'C33'), ('ACU JUNTA DILATACION', 'C30'), ('ACU JUNTA CERCO', 'C30')):
        item = next(p[0] for p in PARTIDAS if p[1] == hoja)
        hojas[hoja] = wb.create_sheet(hoja)
        copiar_hoja(F, V, hoja, hojas[hoja], metrado=(celda, ref_metrado[item]), cabecera=cab)
    # tapa lateral de la canaleta de techo: datos (filas 1-22) y ACU 3 (filas 65-83 -> 25-43) de ACU CANALETAS
    ws = wb.create_sheet('ACU TAPA LATERAL CANALETA')
    copiar_hoja(F, V, 'ACU CANALETAS', ws, filas=set(range(1, 23)) | set(range(65, 84)), desplazar=(65, 40),
                metrado=('C27', ref_metrado['01.04.03.05.01.05']), cabecera=cab)
    ws['A1'] = 'ANALISIS DE COSTO UNITARIO - TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA SECCIÓN 0.25m x 0.20m'
    ws['A7'] = 'Partida 01.04.03.05.01.05 (ACU 3 de la hoja ACU CANALETAS de la planilla; datos de la hoja METRADO CANALETAS)'
    ws['A25'] = 'ACU: 01.04.03.05.01.05 TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA SECCIÓN 0.25m x 0.20m'
    # bancas OC-01
    bancas(wb.create_sheet('ACU CANALETA BANCAS OC-01'), F, cab, (ref_metrado['01.04.03.05.04.01'], ref_metrado['01.04.03.05.04.03']))
    copiar_hoja(F, V, CHH, wb.create_sheet(CHH), cabecera=cab)
    wb.properties.creator = ''; wb.properties.title = 'ACU - partidas resaltadas - Hogar de Refugio Temporal'
    for s in wb.worksheets:
        s.sheet_view.showGridLines = False
        s.page_setup.orientation = 'portrait'; s.page_setup.paperSize = s.PAPERSIZE_A4
        s.sheet_properties.pageSetUpPr.fitToPage = True; s.page_setup.fitToWidth = 1; s.page_setup.fitToHeight = 0
        s.print_area = 'A1:%s%d' % (get_column_letter(min(s.max_column, 8)), s.max_row)
    wb.save(SALIDA)
    return SALIDA


if __name__ == '__main__':
    print(generar(sys.argv[1]))
