# -*- coding: utf-8 -*-
"""Lectura del plano de equipamiento y mobiliario del CAR Varones (CUI 2705619), láminas MB-01 a MB-09.

Fuente: insumos/katiuska/mobiliario/EQUIPAMIENTO_Y_MOBILIARIO_CAR_VARONES.zip (DXF de la arquitecta, no se edita).

Lee del espacio modelo:
  - cada "CUADRO DE EQUIPAMIENTO Y MOBILIARIOS - <ambiente> / EDIFICACION n": el título va centrado sobre la tabla y las columnas
    están a distancia fija del centro (código -3.32, descripción -0.95, und +1.66, cantidad +2.23); cada fila se arma desde su
    código, con la descripción y la cantidad más cercanas en altura, y la sección (EQUIPO, MOBILIARIO, IMPLEMENTOS, SEGURIDAD)
    es el último encabezado por encima;
  - las etiquetas de código puestas sobre cada mueble o equipo dibujado en planta (capas "Letra Mobiliario" y "09.-ALE_TEXTO
    DE MOBILIARIO", textos dentro de bloques y directrices múltiples), asignadas a la edificación cuya planta las contiene
    (cada planta queda arriba y a la derecha de su título "PRIMER NIVEL (EDIFICACION n)");
  - las láminas (presentaciones MB-01 a MB-09) con su título.

Uso: python3 herramientas/varones/mobiliario/lee_plano_mb.py
Salida: entregables_varones/_calc/mobiliario_plano.json
"""
import json
import os
import re
import tempfile
import zipfile
from collections import Counter, defaultdict

import ezdxf

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(AQUI)))
ZIP = os.path.join(RAIZ, 'insumos/katiuska/mobiliario/EQUIPAMIENTO_Y_MOBILIARIO_CAR_VARONES.zip')
SALIDA = os.path.join(RAIZ, 'entregables_varones/_calc/mobiliario_plano.json')
CAPA_CUADROS = '13.-ALE_PRESENTACION'
CAPAS_ETIQ = ('Letra Mobiliario', '09.-ALE_TEXTO DE MOBILIARIO')
COD = re.compile(r'^\s*([MEKS])\s*-?\s*0*(\d{1,3})\s*$')
SECCIONES = ('EQUIPO', 'EQUIPOS', 'MOBILIARIO', 'IMPLEMENTOS', 'SEGURIDAD')


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


def etiquetas(msp, T):
    """Etiquetas de código sobre el dibujo: textos sueltos y directrices múltiples, también las que están dentro de bloques
    (hasta 6 niveles de anidamiento)."""
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


def cuadros(T):
    C = [t for t in T if t[2] == CAPA_CUADROS]
    tit = [t for t in C if t[3].startswith('CUADRO DE EQUIPAMIENTO')]
    res = []
    for cx, y0, _, s in tit:
        y1 = max([u[1] for u in tit if abs(u[0] - cx) < 0.5 and u[1] < y0 - 0.01], default=y0 - 40)
        cel = [t for t in C if cx - 3.7 <= t[0] <= cx + 3.7 and y1 + 0.05 < t[1] < y0 - 0.05]
        cods = [t for t in cel if abs(t[0] - (cx - 3.32)) < 0.3 and norm(t[3])]
        heads = [t for t in cel if abs(t[0] - (cx - 0.95)) < 1.4 and limpio(t[3]) in SECCIONES]
        items = []
        for x, y, _, c in sorted(cods, key=lambda t: -t[1]):
            des = [t for t in cel if abs(t[0] - (cx - 0.95)) < 1.4 and abs(t[1] - y) < 0.2 and limpio(t[3]) not in SECCIONES
                   and not norm(t[3]) and t[3].strip() not in ('COD.',)]
            can = [t for t in cel if abs(t[0] - (cx + 2.23)) < 0.25 and abs(t[1] - y) < 0.2 and re.fullmatch(r'\d+', t[3].strip())]
            sec = [h for h in heads if h[1] > y]
            items.append(dict(cod=norm(c), seccion=(limpio(min(sec, key=lambda h: h[1] - y)[3]) if sec else None),
                              des=(limpio(min(des, key=lambda t: abs(t[1] - y))[3]) if des else ''),
                              cant=(int(min(can, key=lambda t: abs(t[1] - y))[3]) if can else None)))
        titulo = limpio(s).replace('CUADRO DE EQUIPAMIENTO Y MOBILIARIOS - ', '')
        m = re.search(r'^(.*?)\s*EDIFICACION\s*0?(\d+)', titulo)
        res.append(dict(titulo=titulo, ambiente=limpio(m.group(1)) if m else titulo,
                        edificacion='E-%02d' % int(m.group(2)) if m else '?', x=round(cx, 3), y=round(y0, 3), items=items))
    return res


def plantas(T):
    out = []
    for x, y, l, s in T:
        m = re.search(r'\(EDIFICACION\s*0?(\d+)\)', s)
        if l == '0_TEXTOS 1' and m:
            out.append(dict(edificacion='E-%02d' % int(m.group(1)), nombre=limpio(s.split('\n')[0]), x=round(x, 3), y=round(y, 3)))
    return out


def edificacion_de(x, y, pl):
    c = [p for p in pl if -1 <= x - p['x'] <= 32 and -1 <= y - p['y'] <= 34]
    return min(c, key=lambda p: (y - p['y']) + 0.1 * (x - p['x']))['edificacion'] if c else '?'


def laminas(doc):
    out = []
    for lay in doc.layouts:
        if lay.name == 'Model':
            continue
        tx = [limpio(e.dxf.text if e.dxftype() == 'TEXT' else e.plain_text()) for e in lay.query('TEXT MTEXT')]
        cod = next((t for t in tx if re.fullmatch(r'MB-\d\d', t)), None)
        tit = next((t for t in tx if t.startswith('EQUIPAMIENTO Y MOBILIARIO')), '')
        if cod:
            out.append(dict(codigo=cod, titulo=tit, escala=next((t for t in tx if re.fullmatch(r'1/\d+', t)), ''),
                            fecha=next((t for t in tx if re.search(r'20\d\d$', t)), '')))
    return sorted(out, key=lambda l: l['codigo'])


def leer():
    doc = abrir(); msp = doc.modelspace(); T = textos(msp)
    pl = plantas(T)
    etq = defaultdict(Counter)
    for x, y, s in etiquetas(msp, T):
        for p in re.split(r'[,\s]+', s.strip()):
            k = norm(p)
            if k:
                etq[edificacion_de(x, y, pl)][k] += 1
    return dict(fuente=os.path.relpath(ZIP, RAIZ), laminas=laminas(doc), plantas=pl, cuadros=cuadros(T),
                etiquetas={k: dict(v) for k, v in sorted(etq.items())})


if __name__ == '__main__':
    D = leer()
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump(D, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(D['cuadros']), 'cuadros;', sum(len(c['items']) for c in D['cuadros']), 'filas;', [l['codigo'] for l in D['laminas']])
    for c in D['cuadros']:
        malos = [i for i in c['items'] if i['cant'] is None or not i['des']]
        if malos:
            print('  revisar', c['titulo'][:50], malos)
    print(SALIDA)
