# -*- coding: utf-8 -*-
"""Separadores del expediente técnico del CAR Mujeres (Wilma, CUI 2717013) en PowerPoint, uno por cada ítem con título del índice
final de la usuaria (insumos/wilma/indice_final/1._INDICE_FINAL_CAR_NINAS.xlsx), con la vista aérea del CAR de fondo como marca de
agua (foto de la usuaria aclarada, insumos/wilma/indice_final/FOTO_CAR_MUJERES_VISTA_AEREA.jpg).

Estilo de la carátula del CAR Mujeres (opción E): guinda y dorado, encabezado con escudo, número del ítem en dorado, título en
guinda, capítulo de procedencia arriba y pie con el proyecto y su CUI. No se usan las columnas de estado de la usuaria ("OK",
"DEBEN PASAR", etc.) ni las filas de planos sin título (12.01.01 ...). Los códigos que Excel convirtió en fecha (formato dd.mm:
06.06 y 08.01) o en número (10.04) se leen como texto.

Uso: python3 herramientas/mujeres/separadores_m.py
Salida: entregables_mujeres/SEPARADORES_EXPEDIENTE_TECNICO_CAR_MUJERES.pptx
"""
import datetime
import os
import sys

import openpyxl
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI); RAIZ = os.path.dirname(HER)
sys.path.insert(0, HER)
import caratulas_tomos_pptx as C  # noqa: E402  (piezas de dibujo y colores de las carátulas)
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402

INDICE = os.path.join(RAIZ, 'insumos/wilma/indice_final/1._INDICE_FINAL_CAR_NINAS.xlsx')
FOTO = os.path.join(RAIZ, 'insumos/wilma/indice_final/FOTO_CAR_MUJERES_VISTA_AEREA.jpg')
MARCA = os.path.join(RAIZ, 'entregables_mujeres/figuras_caratula/marca_agua_separadores.jpg')
SALIDA = os.path.join(RAIZ, 'entregables_mujeres/SEPARADORES_EXPEDIENTE_TECNICO_CAR_MUJERES.pptx')
P = next(p for p in C.PROYECTOS if p['clave'] == 'CAR_MUJERES')
ACLARADO = 0.85          # fracción de blanco sobre la foto (marca de agua)


def codigo(v, fmt):
    if isinstance(v, datetime.datetime):                       # Excel convirtió "06.06" / "08.01" en fecha (formato dd.mm)
        return '%02d.%02d' % (v.day, v.month) if fmt.startswith('dd') else '%02d.%02d' % (v.month, v.day)
    if isinstance(v, float):
        return '%05.2f' % v
    return str(v).strip() if v is not None else ''


def items():
    ws = openpyxl.load_workbook(INDICE).worksheets[0]
    out, padres = [], {}
    empezar = False
    for r in range(1, ws.max_row + 1):
        a, b = ws.cell(r, 1), ws.cell(r, 2)
        if a.value == 'ÍTEM':
            empezar = True; continue
        if not empezar:
            continue
        cod, tit = codigo(a.value, a.number_format), (b.value or '').strip()
        if not cod or not tit:
            continue
        nivel = cod.count('.')
        padres[nivel] = (cod, tit)
        ruta = [padres[k] for k in range(nivel) if k in padres]
        out.append(dict(cod=cod, tit=tit, nivel=nivel, ruta=ruta))
    return out


def marca_agua():
    """Foto recortada a hoja A4 vertical (centro de la imagen: portada con el letrero del CAR) y aclarada."""
    im = Image.open(FOTO).convert('RGB')
    W, H = im.size; r = 21 / 29.7
    w = int(H * r); x0 = (W - w) // 2
    im = im.crop((x0, 0, x0 + w, H))
    im = Image.blend(im, Image.new('RGB', im.size, 'white'), ACLARADO)
    os.makedirs(os.path.dirname(MARCA), exist_ok=True)
    im.save(MARCA, quality=88)
    return MARCA


def separador(sl, it, marca):
    c1, c2 = P['c1'], P['c2']
    sl.shapes.add_picture(marca, 0, 0, C.Cm(21), C.Cm(29.7)).name = 'Marca de agua'
    C.rect(sl, 0, 0, 21, 0.15, fill=c1)
    C.escudo(sl, 2.6, 0.9, 2.1)
    C.texto(sl, 4.2, 1.2, 15.5, 0.85, C.ENTIDAD, size=15, color=c1, font=C.SERIF, bold=True, esp=2)
    C.texto(sl, 4.2, 2.0, 15.5, 0.7, C.GERENCIA, size=10.5, color='404040', esp=1)
    C.rect(sl, 1.5, 3.3, 18, 0.05, fill=c2)
    if it['ruta']:                                              # capítulo de procedencia
        C.texto(sl, 1.5, 9.2, 18, 1.4, [[('%s   %s' % (cod, t.upper()), {})] for cod, t in it['ruta']], size=11, color='595959',
                bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM, esp=1)
    C.texto(sl, 1, 10.9, 19, 2.0, it['cod'], size=54 if it['nivel'] == 0 else 44, color=c2, font=C.SERIF, bold=True,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, esp=2)
    C.rect(sl, 10.5 - 3.5, 13.15, 7.0, 0.08, fill=c1); C.rect(sl, 10.5 - 2.4, 13.33, 4.8, 0.03, fill=c2)
    tam = 32 if it['nivel'] == 0 else 26 if len(it['tit']) < 60 else 22
    C.texto(sl, 1.8, 13.75, 17.4, 5.2, it['tit'].upper(), size=tam, color=c1, font=C.SERIF, bold=True, align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.TOP)
    yb = 25.0                                                   # pie: proyecto y CUI
    C.rect(sl, 1.5, yb, 18, 0.05, fill=c2)
    C.texto(sl, 1.5, yb + 0.25, 18, 2.2, [[('EXPEDIENTE TÉCNICO', dict(color=c2, size=10, esp=3))],
                                          [(P['nombre'], dict(color=c1, size=9.5, font=C.SERIF))],
                                          [('CUI N° ' + P['cui'], dict(color=c1, size=10.5, esp=1))]],
            bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP)
    C.rect(sl, 0, 29.05, 21, 0.06, fill=c2); C.rect(sl, 0, 29.11, 21, 0.59, fill=c1)


def generar():
    marca = marca_agua()
    prs = C.presentacion()
    lista = items()
    for it in lista:
        separador(C.nueva(prs), it, marca)
    prs.core_properties.title = 'Separadores del expediente técnico - CAR Mujeres'; prs.core_properties.author = ''
    prs.save(SALIDA)
    return SALIDA, lista


if __name__ == '__main__':
    s, lista = generar()
    for it in lista:
        print('%-10s %s' % (it['cod'], it['tit']))
    print(len(lista), 'separadores ->', s)
