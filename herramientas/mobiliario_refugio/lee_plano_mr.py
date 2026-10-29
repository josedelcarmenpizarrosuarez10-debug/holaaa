# -*- coding: utf-8 -*-
"""Lectura del plano de equipamiento y mobiliario del Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514),
láminas EM-01 a EM-07.

Fuente: insumos/solange/mobiliario/EQUIPAMIENTO_Y_MOBILIARIO_HOGAR_REFUGIO.zip (DXF de la arquitecta, no se edita).

Lee del espacio modelo (coordenadas UTM, escala 1/50):
  - las láminas: marco de la capa "M ARCO" con su rótulo (código EM-nn, título, escala y fecha);
  - cada "CUADRO DE EQUIPAMIENTO; <ambiente> - EDIFICACION n": las columnas se toman de su fila de encabezado (COD., UND.,
    CANTID.); cada fila se arma desde su código con la descripción y la cantidad a la misma altura; la sección (EQUIPO,
    MOBILIARIO, IMPLEMENTOS) es el último encabezado por encima. Descripciones de las capas "13.-ALE_PRESENTACION" y "0";
  - las etiquetas de código puestas sobre cada mueble en planta (capas "Letra Mobiliario" y "09.-ALE_TEXTO DE MOBILIARIO",
    textos dentro de bloques y directrices múltiples);
  - los títulos de planta "PRIMER NIVEL (EDIFICACION nn)" (capa "0_TEXTOS 1") y los nombres de ambiente (capa "0_TEXTOS 2").

Uso: python3 herramientas/mobiliario_refugio/lee_plano_mr.py
Salida: entregables/_calc/mobiliario_plano.json
"""
import json
import os
import re
import tempfile
import zipfile
from collections import Counter, defaultdict

import ezdxf
from ezdxf import bbox

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
ZIP = os.path.join(RAIZ, 'insumos/solange/mobiliario/EQUIPAMIENTO_Y_MOBILIARIO_HOGAR_REFUGIO.zip')
SALIDA = os.path.join(RAIZ, 'entregables/_calc/mobiliario_plano.json')
CAPAS_CUADRO = ('13.-ALE_PRESENTACION', '0')
CAPAS_ETIQ = ('Letra Mobiliario', '09.-ALE_TEXTO DE MOBILIARIO')
COD = re.compile(r'^\s*([MEKS])\s*-?\s*0*(\d{1,3})\s*$')
SECCIONES = ('EQUIPO', 'EQUIPOS', 'MOBILIARIO', 'IMPLEMENTOS', 'IMPLEMENTO', 'SEGURIDAD')


def norm(c):
    m = COD.match(c or '')
    return '%s%d' % (m.group(1), int(m.group(2))) if m else None


def limpio(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def abrir():
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(ZIP) as zf:
        n = next(x for x in zf.namelist() if x.lower().endswith('.dxf'))
        zf.extract(n, tmp)
    return ezdxf.readfile(os.path.join(tmp, n))


def textos(msp):
    out = []
    for e in msp.query('TEXT MTEXT'):
        s = e.dxf.text if e.dxftype() == 'TEXT' else e.plain_text()
        p = e.dxf.insert
        out.append((p.x, p.y, e.dxf.layer, s))
    return out


def laminas(msp, T):
    """Marcos de la capa "M ARCO" con el código, el título, la escala y la fecha de su rótulo."""
    out = []
    for e in msp.query('LWPOLYLINE[layer=="M ARCO"]'):
        b = bbox.extents([e], fast=True)
        x0, y0, x1, y1 = b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y
        dentro = [t for t in T if x0 <= t[0] <= x1 and y0 <= t[1] <= y1 and t[2] == 'G-ANNO-TEXT']
        cod = next((limpio(t[3]) for t in dentro if re.fullmatch(r'EM-\d\d', limpio(t[3]))), None)
        if not cod:
            continue
        tit = next((limpio(t[3]) for t in dentro if t[3].startswith('EQUIPAMIENTO Y MOBILIARIO')), '')
        out.append(dict(codigo=cod, titulo=tit.replace(' :', ':'), caja=[round(v, 3) for v in (x0, y0, x1, y1)],
                        escala=next((limpio(t[3]) for t in dentro if re.fullmatch(r'1/\d+', limpio(t[3]))), ''),
                        fecha=next((limpio(t[3]) for t in dentro if re.search(r'20\d\d$', limpio(t[3]))), '')))
    return sorted(out, key=lambda l: l['codigo'])


def lamina_de(x, y, L):
    return next((l['codigo'] for l in L if l['caja'][0] <= x <= l['caja'][2] and l['caja'][1] <= y <= l['caja'][3]), None)


def cuadros(T, L):
    C = [t for t in T if t[2] in CAPAS_CUADRO]
    tit = [t for t in C if t[2] == CAPAS_CUADRO[0] and t[3].startswith('CUADRO DE EQUIPAMIENTO')]
    res = []
    for cx, y0, _, s in tit:
        cab = [t for t in C if y0 - 0.8 < t[1] < y0 and cx - 3.9 < t[0] < cx + 3.9]
        col = {}
        for k in ('COD.', 'UND.', 'CANTID.'):
            c = [t for t in cab if t[3].strip() == k]
            col[k] = min(c, key=lambda t: abs(t[0] - cx))[0]
        xc, xu, xq = col['COD.'], col['UND.'], col['CANTID.']
        y1 = max([u[1] for u in tit if abs(u[0] - cx) < 0.5 and u[1] < y0 - 0.01], default=y0 - 20)
        cel = [t for t in C if xc - 0.3 <= t[0] <= xq + 1.2 and y1 + 0.05 < t[1] < y0 - 0.05]
        cods = sorted([t for t in cel if abs(t[0] - xc) < 0.25 and norm(t[3])], key=lambda t: -t[1])
        heads = [t for t in cel if xc + 0.15 < t[0] < xu - 0.2 and limpio(t[3]) in SECCIONES]
        items = []; y_ant = y0
        for x, y, _, c in cods:
            if y_ant - y > 1.2:                                          # fin de la tabla (hueco grande)
                break
            y_ant = y
            des = [t for t in cel if xc + 0.15 < t[0] < xu - 0.2 and abs(t[1] - y) < 0.17 and limpio(t[3]) not in SECCIONES
                   and not norm(t[3]) and limpio(t[3]) not in ('COD.', 'UND.', 'CANTID.')]
            can = [t for t in cel if abs(t[0] - xq) < 0.3 and abs(t[1] - y) < 0.17 and re.fullmatch(r'\d+', t[3].strip())]
            und = [t for t in cel if abs(t[0] - xu) < 0.3 and abs(t[1] - y) < 0.17]
            sec = [h for h in heads if h[1] > y]
            d = min(des, key=lambda t: abs(t[1] - y)) if des else None
            items.append(dict(cod=norm(c), seccion=(limpio(min(sec, key=lambda h: h[1] - y)[3]) if sec else None),
                              des=limpio(d[3]) if d else '', capa_des=d[2] if d else '',
                              und=limpio(und[0][3]) if und else '',
                              cant=(int(min(can, key=lambda t: abs(t[1] - y))[3]) if can else None)))
        titulo = limpio(s.replace(';', ' ')).replace('CUADRO DE EQUIPAMIENTO ', '')
        m = re.search(r'^(.*?)[\s-]*EDIFICACION\s*0?(\d+)', titulo)
        res.append(dict(titulo=titulo, ambiente=limpio(m.group(1)).strip(' -') if m else titulo,
                        edificacion_titulo='E-%02d' % int(m.group(2)) if m else '?', lamina=lamina_de(cx, y0, L),
                        x=round(cx, 3), y=round(y0, 3), items=items))
    return sorted(res, key=lambda c: (c['lamina'] or '', -c['y'], c['x']))


def plantas(T, L):
    out = []
    for x, y, l, s in T:
        m = re.search(r'\(EDIFICACION\s*0?(\d+)\)', s)
        if l == '0_TEXTOS 1' and m:
            out.append(dict(edificacion='E-%02d' % int(m.group(1)), nombre=limpio(s.split('PRIMER')[0]).strip(' -'),
                            x=round(x, 3), y=round(y, 3), lamina=lamina_de(x, y, L)))
    return out


def ambientes_planta(T):
    return [dict(nombre=limpio(s), x=round(x, 3), y=round(y, 3)) for x, y, l, s in T if l == '0_TEXTOS 2']


def etiquetas(msp, T):
    """Etiquetas de código sobre el dibujo: textos sueltos y directrices múltiples, también dentro de bloques."""
    out = [(x, y, s) for x, y, l, s in T if l in CAPAS_ETIQ]

    def ver(e, prof):
        t = e.dxftype()
        if t in ('TEXT', 'MTEXT', 'ATTRIB'):
            s = e.dxf.text if t != 'MTEXT' else e.plain_text()
            if re.fullmatch(r'\s*[MEKS]\s*-?\d{1,3}\s*(,\s*[MEKS]\d{1,3}\s*)*', s):
                out.append((e.dxf.insert.x, e.dxf.insert.y, s))
        elif t == 'MULTILEADER':
            try:
                out.append((e.context.mtext.insert.x, e.context.mtext.insert.y,
                            re.sub(r'\\[A-Za-z][^;]*;|[{}]', '', e.context.mtext.default_content)))
            except Exception:
                pass
        elif t == 'INSERT' and prof < 6:
            try:
                for a in e.attribs:
                    ver(a, prof)
                for v in e.virtual_entities():
                    ver(v, prof + 1)
            except Exception:
                pass
    for e in msp.query('INSERT MULTILEADER'):
        ver(e, 0)
    return out


def leer():
    doc = abrir(); msp = doc.modelspace(); T = textos(msp)
    L = laminas(msp, T)
    etq = []
    for x, y, s in etiquetas(msp, T):
        lam = lamina_de(x, y, L)
        for p in re.split(r'[,\s]+', s.strip()):
            k = norm(p)
            if k and lam:
                etq.append(dict(cod=k, x=round(x, 3), y=round(y, 3), lamina=lam))
    return dict(fuente=os.path.relpath(ZIP, RAIZ), laminas=L, plantas=plantas(T, L), cuadros=cuadros(T, L),
                ambientes_planta=ambientes_planta(T), etiquetas=etq)


if __name__ == '__main__':
    D = leer()
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump(D, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(D['cuadros']), 'cuadros;', sum(len(c['items']) for c in D['cuadros']), 'filas;', [l['codigo'] for l in D['laminas']],
          len(D['etiquetas']), 'etiquetas')
    for c in D['cuadros']:
        malos = [i for i in c['items'] if i['cant'] is None or not i['des']]
        if malos:
            print('  revisar', c['lamina'], c['titulo'][:50], malos)
    print(SALIDA)
