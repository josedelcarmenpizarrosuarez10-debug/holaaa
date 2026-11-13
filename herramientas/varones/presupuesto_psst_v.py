# -*- coding: utf-8 -*-
"""CAR Varones (CUI 2705619): presupuesto del PSST final (Excel del usuario, 13-11-2026) y su paso al Word del PSST y a las
especificaciones técnicas del PSST.

1. Excel (LibreOffice UNO, sin rehacer el libro): nombre del proyecto y CUI de Varones (el archivo venía con los del CAR Mujeres),
   frentes de trabajo de la hoja SUSTENTO CANTIDADES con los del cuadro N.° 5 del PSST de Varones, texto del paso 1 sin el costo
   directo (el usuario lo retiró del libro) y sin la columna «Fuente del precio unitario» en las hojas 01.02.01 a 01.02.07
   (pedido del usuario). Se recalcula; las cantidades, precios y fórmulas del usuario no se tocan.
2. Word del PSST (entregables_varones/psst/PSST - VARONES.docx, que ya tiene el terreno actualizado): lo resaltado en amarillo
   (numeral 3.3, capítulo 6, numeral 8.2 y Anexo 10) se rehace con los valores del Excel, sin costo directo de la obra, y se
   quita el resaltado. El resto del Word queda igual.
3. Especificaciones técnicas del PSST: la lista «Comprende» de cada partida igual a los insumos del Excel y las líneas del método
   que nombraban insumos que ya no están en el presupuesto.

Uso: python3 herramientas/varones/presupuesto_psst_v.py
"""
import copy
import os
import subprocess
import sys
import tempfile
import time

import docx
import openpyxl
from docx.oxml.ns import qn

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas', 'mujeres'))
from terreno_actualizado_m import reemplazar  # noqa: E402

INS = os.path.join(RAIZ, 'insumos/katiuska/psst')
SAL = os.path.join(RAIZ, 'entregables_varones/psst')
XLS_IN = os.path.join(INS, 'PRESUPUESTO PSST 2026 - VAROINES CAR.xlsx')
XLS_OUT = os.path.join(SAL, 'PRESUPUESTO PSST 2026 - CAR VARONES.xlsx')
DOC = os.path.join(SAL, 'PSST - VARONES.docx')                       # ya con el terreno (terreno_psst_v.py)
ET_IN = os.path.join(INS, 'ESPECIFICACIONES TECNICAS PSST - VARONES.docx')
ET_OUT = os.path.join(SAL, 'ESPECIFICACIONES TECNICAS PSST - VARONES.docx')
PARTIDAS = ['01.02.01', '01.02.02', '01.02.03', '01.02.04', '01.02.05', '01.02.06', '01.02.07']
FRENTES = {9: 'Zanjas de cimientos y zapatas de las diez edificaciones, acero, encofrado y concreto, tanque elevado.',
           10: 'Muros, estructura metálica de techo, soldadura e izaje, cobertura de termotecho de las edificaciones.',
           11: 'Columnas, tribuna y estructura con cobertura autosoportada de la losa deportiva.',
           12: 'Red de desagüe, cisterna, buzones, tanque séptico, subestación y grupo electrógeno.',
           13: 'Cunetas, colector frontal, portada de ingreso, cerco frontal y conexión de agua junto a la Carretera Oasis.',
           14: 'Tarrajeo, pisos, pintura, carpintería, pavimentos, veredas y cerco perimétrico.'}


# ------------------------------------------------------------------ 1. Excel
def _conectar():
    import uno
    tmp = tempfile.mkdtemp(); puerto = 2091
    proc = subprocess.Popen(['soffice', '--headless', '--invisible', '--norestore', '-env:UserInstallation=file://%s/perfil' % tmp,
                             '--accept=socket,host=localhost,port=%d;urp;' % puerto], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    local = uno.getComponentContext()
    res = local.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', local)
    for _ in range(60):
        try:
            ctx = res.resolve('uno:socket,host=localhost,port=%d;urp;StarOffice.ComponentContext' % puerto); break
        except Exception:
            time.sleep(0.5)
    else:
        proc.kill(); raise SystemExit('No se pudo iniciar LibreOffice')
    return proc, ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)


def _prop(n, v):
    from com.sun.star.beans import PropertyValue
    p = PropertyValue(); p.Name = n; p.Value = v; return p


def excel():
    import uno
    proc, desk = _conectar()
    try:
        doc = desk.loadComponentFromURL(uno.systemPathToFileUrl(XLS_IN), '_blank', 0, (_prop('Hidden', True),))
        hojas = doc.Sheets
        for i in range(hojas.Count):
            h = hojas.getByIndex(i)
            for viejo, nuevo in (('RESIDENCIAL - MUJERES', 'RESIDENCIAL - VARONES'), ('2717013', '2705619')):
                r = h.createReplaceDescriptor(); r.SearchString = viejo; r.ReplaceString = nuevo; h.replaceAll(r)
        p = hojas.getByName('PERSONAL EN OBRA')
        p.getCellRangeByName('D16').setValue(2705619)
        p.getCellRangeByName('B8').setString('2.  Paso 1: plazo de la obra, horas por día y días de trabajo por mes.')
        s = hojas.getByName('SUSTENTO CANTIDADES')
        for fila, texto in FRENTES.items():
            s.getCellRangeByName('G%d' % fila).setString(texto)
        for n in PARTIDAS:                                     # columna I = «Fuente del precio unitario»
            hojas.getByName(n).Columns.removeByIndex(8, 1)
        doc.calculateAll()
        os.makedirs(SAL, exist_ok=True)
        doc.storeToURL(uno.systemPathToFileUrl(XLS_OUT), (_prop('FilterName', 'Calc MS Excel 2007 XML'),))
        doc.close(True)
    finally:
        try: desk.terminate()
        except Exception: pass
        time.sleep(1); proc.kill()


def valores():
    """Valores calculados del Excel final (recalculado por LibreOffice al guardar)."""
    wb = openpyxl.load_workbook(XLS_OUT, data_only=True)
    p = wb['PERSONAL EN OBRA']
    cat = {p.cell(r, 2).value: p.cell(r, 4).value for r in range(40, 44)}
    V = dict(plazo=p['D17'].value, horas=p['D18'].value, dias=p['D19'].value, hh=p['K35'].value, hh_obrero=p['D47'].value,
             promedio=p['D49'].value, obreros=p['D50'].value, hh_cat=cat, partidas=[], total=wb['RESUMEN']['G14'].value)
    r = wb['RESUMEN']
    for fila in range(7, 14):
        V['partidas'].append(dict(item=r.cell(fila, 2).value, desc=r.cell(fila, 3).value, und=r.cell(fila, 4).value,
                                  metrado=r.cell(fila, 5).value, pu=r.cell(fila, 6).value, parcial=r.cell(fila, 7).value))
    V['detalle'] = {}
    for n in PARTIDAS:
        h = wb[n]; items = []; extra = {}
        for fila in range(9, h.max_row + 1):
            a, b = h.cell(fila, 2).value, h.cell(fila, 3).value
            if isinstance(a, (int, float)) and b:
                items.append(dict(desc=b, und=h.cell(fila, 4).value, cant=h.cell(fila, 5).value, pu=h.cell(fila, 6).value,
                                  parcial=h.cell(fila, 7).value))
            elif isinstance(a, str) and a.startswith('COSTO'):
                extra[a] = h.cell(fila, 7).value
        V['detalle'][n] = dict(items=items, totales=extra)
    return V


# ------------------------------------------------------------------ utilidades Word
def f2(x):
    return '{:,.2f}'.format(x)


def fcant(x):
    return '{:,.0f}'.format(x) if abs(x - round(x)) < 1e-9 else '{:,.2f}'.format(x)


def texto(p):
    return ''.join(t.text or '' for t in p.iter(qn('w:t')))


def poner(p, nuevo):
    """Deja el párrafo con el texto nuevo en su primer run (conserva su formato) y vacía los demás."""
    ts = list(p.iter(qn('w:t')))
    if not ts:
        return
    ts[0].text = nuevo
    ts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    for t in ts[1:]:
        t.text = ''


def celda(c, nuevo):
    ps = c._tc.findall(qn('w:p'))
    poner(ps[0], nuevo)
    for p in ps[1:]:
        c._tc.remove(p)


def sin_resaltado(raiz):
    n = 0
    for h in list(raiz.iter(qn('w:highlight'))):
        h.getparent().remove(h); n += 1
    for s in list(raiz.iter(qn('w:shd'))):
        if s.getparent().tag == qn('w:rPr') and (s.get(qn('w:fill')) or '').upper() in ('FFFF00', 'FFFF99', 'FFF2CC', 'FFFFCC'):
            s.getparent().remove(s); n += 1
    return n


def filas_items(tabla, k):
    """Tabla de detalle: encabezado, título de la partida, k filas de insumos y la fila del total."""
    filas = tabla.rows
    items = list(filas)[2:-1]
    while len(items) > k:
        tr = items.pop()._tr; tr.getparent().remove(tr)
    while len(items) < k:
        nuevo = copy.deepcopy(items[-1]._tr); items[-1]._tr.addnext(nuevo)
        items = list(tabla.rows)[2:-1]
    return list(tabla.rows)[2:-1]


def tabla_resumen(t, V):
    for fila, pa in zip(list(t.rows)[1:8], V['partidas']):
        vals = [pa['item'], pa['desc'], pa['und'], fcant(pa['metrado']), f2(pa['pu']), f2(pa['parcial'])]
        for c, v in zip(fila.cells, vals):
            celda(c, v)
    ult = list(t.rows)[-1].cells
    celda(ult[1], 'Costo total de la partida 01.02 Seguridad y salud ocupacional')
    celda(ult[-1], f2(V['total']))


# ------------------------------------------------------------------ 2. Word del PSST
def word(V):
    d = docx.Document(DOC)
    cuerpo = d.element.body
    hh = V['hh_cat']
    nuevos = {
        'Los documentos recibidos del expediente no indican el plazo':
            'El plazo de ejecución de la obra es de diez (%d) meses, según el cronograma de ejecución de obra del expediente técnico.'
            % V['plazo'],
        'Los documentos recibidos tampoco indican el costo directo':
            'El número de obreros se obtiene de las horas-hombre de mano de obra de la lista de insumos del presupuesto de obra: '
            '%s hh (%s de operarios, %s de oficiales y %s de peones). Con jornadas de %d horas, %d días de trabajo por mes y %d meses de '
            'plazo, cada obrero trabaja %s horas en la obra, lo que da un promedio de %s obreros por día; se consideran %d obreros. '
            'El cálculo se detalla en la hoja «PERSONAL EN OBRA» del archivo de presupuesto del plan y en el Anexo 10.'
            % (f2(V['hh']), f2(hh['Operario']), f2(hh['Oficial']), f2(hh['Peón']), V['horas'], V['dias'], V['plazo'],
               fcant(V['hh_obrero']), f2(V['promedio']), V['obreros']),
        'Conforme al numeral 17.1 del D.S. N.° 011-2019-TR y a la Norma Técnica de Metrados':
            'Conforme al numeral 17.1 del D.S. N.° 011-2019-TR y a la Norma Técnica de Metrados para Obras de Edificación y '
            'Habilitaciones Urbanas (R.D. N.° 073-2010/VIVIENDA/VMCS-DNC), el presupuesto de obra incluye la partida específica de '
            'seguridad y salud, que estima el costo de los mecanismos técnicos y administrativos del plan para %d obreros y un plazo '
            'de %d meses.' % (V['obreros'], V['plazo']),
        'El monto equivale al':
            'Los honorarios del especialista en SST y los exámenes médico ocupacionales se consideran en los gastos generales del '
            'presupuesto de obra.',
        'Con un máximo estimado de 33 obreros':
            None,                                              # solo cambia el número (reemplazo abajo)
        'Jornales básicos de la convención colectiva':
            'Horas-hombre de la lista de insumos del presupuesto de obra. El número de obreros es el promedio redondeado hacia '
            'arriba y se usa en los equipos de protección individual y en el agua para consumo humano; el plazo, en la capacitación.',
    }
    hechos = []
    for p in list(cuerpo.iter(qn('w:p'))):
        t = texto(p)
        for ini, nuevo in nuevos.items():
            if t.startswith(ini):
                if nuevo is None:
                    reemplazar(p, 'Con un máximo estimado de 33 obreros', 'Con %d obreros' % V['obreros'])
                else:
                    poner(p, nuevo)
                hechos.append(ini)
        if t.startswith('Los precios unitarios marcados en el archivo de presupuesto'):
            p.getparent().remove(p); hechos.append('precios marcados')
    tablas = d.tables
    resumenes = [t for t in tablas if t.rows[0].cells[0].text == 'Ítem' and '01.02.01' in t.rows[1].cells[0].text]
    for t in resumenes:
        tabla_resumen(t, V)
    calc = next(t for t in tablas if t.rows[0].cells[0].text == 'Concepto' and 'Costo directo de infraestructura' in t.rows[1].cells[0].text)
    filas_calc = [('Plazo de ejecución de la obra', '%d meses' % V['plazo']),
                  ('Horas de trabajo por día / días de trabajo por mes', '%d horas / %d días' % (V['horas'], V['dias'])),
                  ('Horas-hombre de mano de obra (lista de insumos del presupuesto de obra)', '%s hh' % f2(V['hh'])),
                  ('Horas-hombre de operarios / oficiales / peones', '%s / %s / %s hh' % (f2(hh['Operario']), f2(hh['Oficial']), f2(hh['Peón']))),
                  ('Horas que trabaja un obrero en toda la obra (%d × %d × %d)' % (V['horas'], V['dias'], V['plazo']), '%s h' % fcant(V['hh_obrero'])),
                  ('Promedio de obreros por día (horas-hombre ÷ horas de un obrero)', f2(V['promedio'])),
                  ('Número de obreros considerado (promedio redondeado hacia arriba)', '%d' % V['obreros'])]
    filas = list(calc.rows)[1:]
    for f in filas[len(filas_calc):]:
        f._tr.getparent().remove(f._tr)
    for f, (a, b) in zip(list(calc.rows)[1:], filas_calc):
        celda(f.cells[0], a); celda(f.cells[1], b)
    for n in PARTIDAS:
        t = next(t for t in tablas if t.rows[0].cells[0].text == 'Descripción' and t.rows[1].cells[0].text.startswith(n))
        det = V['detalle'][n]
        for f, it in zip(filas_items(t, len(det['items'])), det['items']):
            for c, v in zip(f.cells, [it['desc'], it['und'], fcant(it['cant']), f2(it['pu']), f2(it['parcial'])]):
                celda(c, v)
        total = det['totales'].get('COSTO POR MES', det['totales'].get('COSTO TOTAL DE LA PARTIDA'))
        celda(list(t.rows)[-1].cells[-1], f2(total))
    n_res = sin_resaltado(cuerpo)
    for p in cuerpo.iter(qn('w:p')):                         # índice: el Anexo 10 queda una página más corto (55 en vez de 56)
        ts = list(p.iter(qn('w:t')))
        if texto(p) == '3. Resumen56' and ts[-1].text == '56':
            ts[-1].text = '55'
    d.save(DOC)
    return hechos, n_res


# ------------------------------------------------------------------ 3. Especificaciones técnicas del PSST
ET_TEXTOS = [
    ('que requieren los trabajadores, el personal técnico y las visitas, según los peligros identificados en la IPERC y el cuadro de EPP '
     'por puesto del PSST. Incluye los juegos de EPP para visitas que exige el numeral 9.3 del D.S. N.° 011-2019-TR.',
     'que requieren los obreros de la obra, según los peligros identificados en la IPERC y el cuadro de EPP por puesto del PSST.'),
    ('delimitación de excavaciones y zonas de trabajo, protección de huecos y puntas de acero, sistemas de línea de vida horizontal para '
     'trabajos en coberturas, equipos para espacios confinados, escaleras, zonas de sombra e hidratación y estaciones lavaojos.',
     'delimitación de excavaciones y zonas de trabajo con malla, postes, señalizadores tubulares, conos y cinta de señalización, y '
     'escaleras para el acceso a las excavaciones.'),
    (', con luces intermitentes en horario nocturno.', '.'),
    ('primeros auxilios, inmovilización y traslado de accidentados, lucha contra incendios, alerta y control de derrames.',
     'primeros auxilios, inmovilización y traslado de accidentados, lucha contra incendios y control de derrames.'),
    ('(numeral 50.3); sus insumos se reponen mensualmente.', '(numeral 50.3).'),
    ('Los dispensadores se ubican en las zonas de sombra e hidratación', 'Los bidones se ubican en las zonas de sombra e hidratación'),
    ('Se controla el abastecimiento diario y la limpieza de los dispensadores.', 'Se controla el abastecimiento diario.'),
]
ET_BORRAR = ('La línea de vida horizontal se instala en la estructura metálica', 'El detector multigás se usa calibrado')


def especificaciones(V):
    d = docx.Document(ET_IN)
    P = d.paragraphs
    for n in PARTIDAS[1:]:                                     # 01.02.01: el Excel la lleva en un solo insumo global; su lista de
        i = next(k for k, p in enumerate(P) if p.text.startswith(n + ' '))   # lo que comprende el plan queda como estaba
        j = next(k for k in range(i, len(P)) if P[k].text.strip() == 'Comprende')
        fin = next(k for k in range(j, len(P)) if P[k].text.strip() == 'Método de ejecución')
        bul = P[j + 1:fin]
        items = [it['desc'] for it in V['detalle'][n]['items']]
        while len(bul) > len(items):
            e = bul.pop()._p; e.getparent().remove(e)
        while len(bul) < len(items):
            nuevo = copy.deepcopy(bul[-1]._p); bul[-1]._p.addnext(nuevo)
            P = d.paragraphs; j = next(k for k in range(i, len(P)) if P[k].text.strip() == 'Comprende')
            fin = next(k for k in range(j, len(P)) if P[k].text.strip() == 'Método de ejecución'); bul = P[j + 1:fin]
        for b, it in zip(bul, items):
            poner(b._p, it)
        P = d.paragraphs
    n = 0
    for p in list(d.element.body.iter(qn('w:p'))):
        for viejo, nuevo in ET_TEXTOS:
            n += reemplazar(p, viejo, nuevo)
        if texto(p).startswith(ET_BORRAR):
            p.getparent().remove(p); n += 1
    d.save(ET_OUT)
    return n


if __name__ == '__main__':
    excel()
    V = valores()
    print('Excel:', XLS_OUT, '| obreros', V['obreros'], '| plazo', V['plazo'], '| total S/', f2(V['total']))
    print('Word:', word(V))
    print('ET:', especificaciones(V), 'cambios de texto')
