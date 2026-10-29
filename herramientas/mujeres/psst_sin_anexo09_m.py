# -*- coding: utf-8 -*-
"""Plan de Seguridad y Salud en el Trabajo del CAR Mujeres (CUI 2717013), documento del usuario: se retira el ANEXO 09 (formatos
de registros con campos de firma: ATS, PETAR, visitas, entrega de EPP, inspección y reporte), por pedido del usuario.

El resto del Word queda igual. Se ajusta lo que lo nombraba: el ANEXO 10 (presupuesto) pasa a ser el ANEXO 09; la lista de anexos;
el índice (sin las entradas del anexo retirado y con las páginas siguientes corridas lo que este ocupaba; Word lo actualiza al abrir); el numeral 4.4 (registro de
visitas), el 8.9 (formatos de los registros), los PETS (PETAR), la fuente del cuadro de presupuesto y la matriz de requisitos legales.

Uso: python3 herramientas/mujeres/psst_sin_anexo09_m.py
Entrada: insumos/wilma/psst/PLAN_DE_SST_CAR_MUJERES_2026.docx (no se modifica)
Salida: entregables_mujeres/PLAN_DE_SST_CAR_MUJERES_2026.docx
"""
import os
import re

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENT = os.path.join(RAIZ, 'insumos/wilma/psst/PLAN_DE_SST_CAR_MUJERES_2026.docx')
SALIDA = os.path.join(RAIZ, 'entregables_mujeres/PLAN_DE_SST_CAR_MUJERES_2026.docx')
W = qn('w:t')
CAMBIOS = [   # (texto viejo, texto nuevo); cada uno debe aparecer al menos una vez
    (' en el registro de visitas (Anexo 09).', ' en el registro de visitas.'),
    ('Fuente: Anexo 10 y archivo', 'Fuente: Anexo 09 y archivo'),
    ('El Anexo 09 presenta los registros obligatorios del artículo 33 del D.S. N.° 005-2012-TR con los formatos referenciales de la '
     'R.M. N.° 050-2013-TR y los formatos operativos de la obra',
     'Los registros obligatorios del artículo 33 del D.S. N.° 005-2012-TR se llevan en los formatos referenciales de la R.M. N.° '
     '050-2013-TR; en la obra se usan además los formatos operativos'),
    ('Anexo 10. Presupuesto del plan', 'Anexo 09. Presupuesto del plan'),
    ('Numeral 8.4; Anexo 09', 'Numerales 8.4 y 8.9'),
    ('Capítulo 6; Anexo 10', 'Capítulo 6; Anexo 09'),
    ('el PETAR (Anexo 09).', 'el PETAR.'),
    ('ANEXO 10. PRESUPUESTO DEL PLAN', 'ANEXO 09. PRESUPUESTO DEL PLAN'),
]


def texto(p):
    return ''.join(t.text or '' for t in p.iter(W))


def reemplazar(p, viejo, nuevo):
    """Reemplaza en los w:t del párrafo aunque el texto esté repartido; solo toca los textos del tramo cambiado."""
    ts = list(p.iter(W)); s = ''.join(t.text or '' for t in ts); i = s.find(viejo)
    if i < 0:
        return False
    pos = 0
    for a, t in enumerate(ts):
        if pos + len(t.text or '') > i:
            break
        pos += len(t.text or '')
    fin = i + len(viejo); pos2 = pos
    for b in range(a, len(ts)):
        pos2 += len(ts[b].text or '')
        if pos2 >= fin:
            break
    ts[a].text = s[pos:i] + nuevo + s[fin:pos2]
    ts[a].set(qn('xml:space'), 'preserve')
    for t in ts[a + 1:b + 1]:
        t.text = ''
    return True


def quitar_anexo(body):
    els = list(body.iterchildren())
    ini = next(k for k, e in enumerate(els) if texto(e).startswith('ANEXO 09. FORMATOS DE LOS REGISTROS'))
    fin = next(k for k, e in enumerate(els) if texto(e).startswith('ANEXO 10. PRESUPUESTO'))
    while fin > ini and 'w:type="page"' in els[fin - 1].xml and not texto(els[fin - 1]).strip():
        fin -= 1                                                 # se deja el salto de página que ya precede al anexo 09
    for e in els[ini:fin]:
        body.remove(e)
    return fin - ini


def indice(body):
    sdt = next(e for e in body.iterchildren() if e.tag == qn('w:sdt'))
    ps = list(sdt.iter(qn('w:p'))); quitar = False; n = 0
    for p in ps:
        t = texto(p)
        if t.startswith('ANEXO 09. FORMATOS'):
            quitar = True
        elif t.startswith('ANEXO 10.'):
            quitar = False
        if quitar:
            p.getparent().remove(p); n += 1
        elif t.startswith('ANEXO 10.'):
            reemplazar(p, 'ANEXO 10.', 'ANEXO 09.')
    return sdt, n


def _num(p):
    m = re.search(r'(\d+)\s*$', texto(p))
    return int(m.group(1)) if m else None


def generar():
    d = docx.Document(ENT); body = d.element.body
    n_el = quitar_anexo(body)
    ps0 = list(next(e for e in body.iterchildren() if e.tag == qn('w:sdt')).iter(qn('w:p')))
    p09 = _num(next(p for p in ps0 if texto(p).startswith('ANEXO 09. FORMATOS')))
    p10 = _num(next(p for p in ps0 if texto(p).startswith('ANEXO 10.')))
    menos = p10 - p09                                            # páginas que ocupaba el anexo retirado (empieza y termina en salto)
    sdt, n_toc = indice(body)
    for p in list(body.iter(qn('w:p'))):                        # lista de anexos: se quita la línea del anexo 09
        if texto(p).strip() == 'Anexo 09. Formatos de los registros del sistema de gestión':
            p.getparent().remove(p)
    usados = {v: 0 for v, _ in CAMBIOS}
    for p in body.iter(qn('w:p')):
        for v, nv in CAMBIOS:
            while reemplazar(p, v, nv):
                usados[v] += 1
    falta = [v for v, n in usados.items() if not n]
    if falta:
        raise ValueError('no se encontró: %s' % falta)
    resto = [texto(p) for p in body.iter(qn('w:p')) if re.search(r'Anexo 10|ANEXO 10|FORMATOS DE LOS REGISTROS DEL SISTEMA', texto(p))]
    if resto:
        raise ValueError('quedan referencias: %s' % resto)
    upd = d.settings.element.find(qn('w:updateFields'))
    if upd is None:
        upd = OxmlElement('w:updateFields'); d.settings.element.append(upd)
    upd.set(qn('w:val'), 'true')
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    d.save(SALIDA)
    pag = {}
    for p in list(sdt.iter(qn('w:p'))):                          # entradas posteriores: menos páginas en el índice
        n = _num(p); t = texto(p)
        if n is not None and n >= p10:
            ts = [x for x in p.iter(W) if (x.text or '').strip()]
            if re.fullmatch(r'\d+', ts[-1].text.strip()):
                ts[-1].text = str(n - menos); pag[t[:45]] = (n, n - menos)
    d.save(SALIDA)
    return SALIDA, n_el, n_toc, usados, pag


if __name__ == '__main__':
    s, n_el, n_toc, usados, pag = generar()
    print(s); print('elementos retirados:', n_el, '| entradas del índice retiradas:', n_toc)
    for v, n in usados.items():
        print('  %d x %s' % (n, v[:60]))
    print(pag)
