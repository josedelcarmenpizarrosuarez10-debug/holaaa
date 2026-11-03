# -*- coding: utf-8 -*-
"""Lee de los DXF de la arquitecta los datos de las edificaciones E-01 a E-09 del Hogar de Refugio Temporal (CUI 2675514)
para el modelo nativo de Revit (revit_nativo.py):

  - PG 01-PG 02 PLANTA GENERAL: muros (capa 1-MURO, las dos caras de cada muro, también los interiores), columnas
    (1-COLUMNAS), columnetas (1-COLUMNETAS), arcos de giro de las puertas y contorno de cada techo (PG-02);
  - A 01-A 09 EDIFICACIONES: indicadores de puerta y ventana (bloques INDICADOR PUERTAS / INDICADOR VENTANA) de la planta
    de cada edificación, pasados a la planta general por coincidencia de los muros;
  - DT-01 DT-15 DETALLES DE PUERTAS Y VENTANAS: cuadro de vanos de cada edificación (ancho, alto, alféizar); se coteja con
    el cuadro de los planos A;
  - alturas de los cortes de cada edificación (NPT, nivel superior de viga, techo terminado, sobretecho) y pendiente de
    las coberturas medida en los cortes (30 %).

Coordenadas locales (m) = las de escena.json: E - 349 090, N - 9 281 900 (copia PG-02 de la planta general).
Salida: edificaciones_revit.json (lo lee revit_nativo.py) y vistas de control en entregables/modelo_revit/control_edificaciones/.
Uso: python lee_edificaciones.py   (los DXF van en herramientas/render_refugio/dxf/; la lectura se guarda en dxf/_cache).
"""
import collections, json, math, os, pickle, re, sys
import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
DXF = os.path.join(AQUI, 'dxf'); CACHE = os.path.join(DXF, '_cache'); os.makedirs(CACHE, exist_ok=True)
F_PG = os.path.join(DXF, 'PG 01-PG 02 PLANTA GENERAL.dxf')
F_A = os.path.join(DXF, 'A 01-A 09 EDIFICACIONES.dxf')
F_DT = os.path.join(DXF, 'DT-01 DT-15 PLANO DE DETALLES DE PUERTAS Y VENTANAS.dxf')
CONTROL = os.path.join(RAIZ, 'entregables', 'modelo_revit', 'control_edificaciones'); os.makedirs(CONTROL, exist_ok=True)
OX, OY = 349090.0, 9281900.0
ESC = json.load(open(os.path.join(AQUI, 'escena.json'), encoding='utf-8'))
r3 = lambda v: round(float(v), 3)

# ------------------------------------------------------------------ alturas de los cortes (A 01-A 09) y pendiente
# Niveles rotulados en los cortes y elevaciones de cada edificación (m sobre el nivel 0.00 del terreno):
#   npt = piso terminado; viga = nivel superior de viga (arranque de la cobertura en el borde del alero);
#   techo = techo terminado rotulado (cumbrera); fondo_viga = 0.15 + alféizar 1.30 + alto 1.99 = 0.15 + 2.50 + sobreluz 0.785.
# La pendiente de las coberturas medida en los cortes es 30 % en todas las edificaciones (tijerales de los cortes).
PEND = 0.30
NIVELES = {
    'E-01': dict(npt=0.15, viga=3.70, techo=7.08, sobretecho=8.77, fuente='CORTE A-A / B-B y elevaciones E-1, E-2 (EDIF. 01)'),
    'E-02': dict(npt=0.15, viga=3.85, techo=5.37, fuente='CORTE B-B (EDIF. 02); el corte A-A rotula +5.95'),
    'E-03': dict(npt=0.15, viga=3.85, techo=5.37, fuente='CORTE B-B y elevaciones E-1, E-2 (EDIF. 03); el corte A-A rotula +5.00'),
    'E-04': dict(npt=0.15, viga=3.85, techo=5.98, fuente='CORTES A-A, B-B y elevaciones E-1, E-2 (EDIF. 04)'),
    'E-05': dict(npt=0.15, viga=3.85, techo=6.68, viga_nave=5.05, techo_nave=7.88,
                 fuente='CORTES A-A, B-B y elevaciones E-1, E-3 (EDIF. 05): extremos +3.85 / +6.68, nave central +5.05 / +7.88'),
    'E-06': dict(npt=0.15, viga=3.85, techo=5.98, fuente='CORTES A-A, B-B y elevaciones E-1, E-2 (EDIF. 06)'),
    'E-07': dict(npt=0.15, viga=3.85, techo=5.98, fuente='CORTES A-A, B-B y elevaciones E-1, E-2 (EDIF. 07)'),
    'E-08': dict(npt=0.15, viga=3.85, techo=5.98, fuente='CORTES A-A, B-B y elevaciones E-1, E-2 (EDIF. 08)'),
    'E-09': dict(npt=0.15, viga=3.85, techo=5.98, fuente='CORTES A-A, B-B y elevaciones E-1 a E-3 (EDIF. 09)'),
}
FONDO_VIGA = 3.44                                                   # 0.15 + 1.30 + 1.99 (ventanas) = 0.15 + 2.50 + 0.785 (puertas)

CAP_MURO = {'1-MURO', '1-MUROS OTRO MATERIAL', '1-MUROS OTRO MATERIAL 2'}
CAP_MURO_BAJO = {'1-MUROS BAJOS'}
CAP_COL = {'1-COLUMNAS', 'COLUMNAS'}
CAP_COLTA = {'1-COLUMNETAS'}
CAP_VANO = {'0_VANOS', '1-VANOS', '1-VIDRIO'}


# ================================================================== lectura de los DXF (con caché)
def _leer(fichero, filtro_y=None, prof_max=5):
    import ezdxf
    doc = ezdxf.readfile(fichero); msp = doc.modelspace()
    lineas, arcos, textos, inds, tablas = [], [], [], [], []

    def rec(ents, blk, prof):
        for e in ents:
            t = e.dxftype()
            try:
                if t == 'INSERT':
                    if prof == 0 and filtro_y is not None and not filtro_y(e.dxf.insert[1]):
                        continue
                    n = e.dxf.name
                    if n.startswith('INDICADOR'):
                        at = {a.dxf.tag: a.dxf.text.strip() for a in e.attribs}
                        inds.append((n, e.dxf.insert[0], e.dxf.insert[1], at, blk)); continue
                    if prof < prof_max:
                        rec(e.virtual_entities(), blk or n, prof + 1)
                elif t == 'LINE':
                    lineas.append((e.dxf.layer, blk, [(e.dxf.start[0], e.dxf.start[1]), (e.dxf.end[0], e.dxf.end[1])]))
                elif t == 'LWPOLYLINE':
                    p = [(q[0], q[1]) for q in e.get_points('xy')]
                    if e.closed and p: p.append(p[0])
                    lineas.append((e.dxf.layer, blk, p))
                elif t == 'POLYLINE':
                    p = [(v.dxf.location[0], v.dxf.location[1]) for v in e.vertices]
                    if e.is_closed and p: p.append(p[0])
                    lineas.append((e.dxf.layer, blk, p))
                elif t == 'ARC':
                    c = e.dxf.center; arcos.append((e.dxf.layer, blk, c[0], c[1], e.dxf.radius, e.dxf.start_angle, e.dxf.end_angle))
                elif t in ('TEXT', 'MTEXT'):
                    s = e.plain_text() if t == 'MTEXT' else e.dxf.text
                    textos.append((e.dxf.layer, blk, e.dxf.insert[0], e.dxf.insert[1], s.strip().replace('\n', ' ')))
                elif t == 'ACAD_TABLE' and prof == 0:
                    celdas = []
                    for v in e.virtual_entities():
                        if v.dxftype() in ('TEXT', 'MTEXT'):
                            s = v.plain_text() if v.dxftype() == 'MTEXT' else v.dxf.text
                            celdas.append((v.dxf.insert[0], v.dxf.insert[1], s.strip().replace('\n', ' ')))
                    tablas.append((e.dxf.insert[0], e.dxf.insert[1], celdas))
            except Exception:
                pass
    rec(msp, None, 0)
    return dict(lineas=lineas, arcos=arcos, textos=textos, inds=inds, tablas=tablas)


def leer(fichero, **kw):
    c = os.path.join(CACHE, os.path.basename(fichero) + '.pkl')
    if os.path.exists(c) and os.path.getmtime(c) > os.path.getmtime(fichero):
        return pickle.load(open(c, 'rb'))
    print('leyendo', os.path.basename(fichero), '...', flush=True)
    d = _leer(fichero, **kw); pickle.dump(d, open(c, 'wb'))
    return d


# ================================================================== cuadros de vanos (DT y A)
def cuadros(tablas):
    """{'E-01': {'P-12': dict(cant, ancho, alto, alf, obs), ...}} de las tablas 'EDIFICACIÓN 0n'."""
    out = {}
    for _, _, celdas in tablas:
        filas = collections.defaultdict(list)
        for x, y, s in celdas: filas[round(y, 2)].append((x, s))
        filas = [[s for x, s in sorted(v)] for k, v in sorted(filas.items(), reverse=True)]
        tit = next((f[0] for f in filas if f and re.match(r'EDIFICACI', f[0])), '')
        m = re.search(r'(\d+)', tit)
        if not m: continue
        cod = 'E-%02d' % int(m.group(1)); d = out.setdefault(cod, {})
        for f in filas:
            if len(f) >= 5 and re.match(r'^[PVM]-?\d+$', f[0]):
                k = norm(f[0])
                num = lambda s: float(s) if re.match(r'^\d+(\.\d+)?$', s) else None
                d[k] = dict(cant=int(f[1]), ancho=num(f[2]), alto=num(f[3]), alf=num(f[4]), obs=f[-1])
    return out


def norm(c):
    m = re.match(r'^([PVM])-?0*(\d+)$', c.strip().upper())
    return '%s-%d' % (m.group(1), int(m.group(2))) if m else c


# ================================================================== geometría básica
def aristas(pts):
    for a, b in zip(pts, pts[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 0.01: yield a, b


def eje(a, b, tol=0.01):
    """'H' (horizontal), 'V' (vertical) o None."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    if abs(dy) <= tol * max(1, abs(dx)) and abs(dy) < 0.02: return 'H'
    if abs(dx) <= tol * max(1, abs(dy)) and abs(dx) < 0.02: return 'V'
    return None


def union_intervalos(iv, tol=0.003):
    iv = sorted(iv); out = []
    for a, b in iv:
        if out and a <= out[-1][1] + tol: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out


def muros_de_caras(segs, e_min=0.07, e_max=0.42):
    """Empareja las caras paralelas de los muros (líneas H con H y V con V a 0.07-0.42 m) -> rectángulos de muro
    (orient, c = coordenada del eje, t0, t1 = tramo a lo largo, e = espesor)."""
    out = []
    for o in ('H', 'V'):
        niveles = collections.defaultdict(list)
        for a, b in segs:
            if eje(a, b) != o: continue
            if o == 'H': niveles[round((a[1] + b[1]) / 2, 3)].append((min(a[0], b[0]), max(a[0], b[0])))
            else: niveles[round((a[0] + b[0]) / 2, 3)].append((min(a[1], b[1]), max(a[1], b[1])))
        ks = sorted(niveles); libre = {k: union_intervalos(niveles[k]) for k in ks}
        for i, k in enumerate(ks):
            for (a, b) in list(libre[k]):
                resto = [(a, b)]
                for k2 in ks[i + 1:]:
                    d = k2 - k
                    if d < e_min: continue
                    if d > e_max: break
                    nuevo = []
                    for (ra, rb) in resto:
                        for (c, dd) in libre[k2]:
                            s, t = max(ra, c), min(rb, dd)
                            if t - s >= 0.05:
                                out.append(dict(o=o, c=round((k + k2) / 2, 3), t0=round(s, 3), t1=round(t, 3), e=round(d, 2)))
                        # lo no emparejado sigue buscando más arriba
                        cort = [(max(ra, c), min(rb, dd)) for (c, dd) in libre[k2] if min(rb, dd) - max(ra, c) >= 0.05]
                        pos = ra
                        for s, t in sorted(cort):
                            if s - pos > 0.05: nuevo.append((pos, s))
                            pos = max(pos, t)
                        if rb - pos > 0.05: nuevo.append((pos, rb))
                    resto = nuevo
                    if not resto: break
    return out


def rect_muro(m):
    h = m['e'] / 2
    return box(m['t0'], m['c'] - h, m['t1'], m['c'] + h) if m['o'] == 'H' else box(m['c'] - h, m['t0'], m['c'] + h, m['t1'])


def piezas_cerradas(segs, a_min, a_max):
    """Columnas y columnetas: componentes conexas de las líneas de la capa -> rectángulo envolvente."""
    if not segs: return []
    g = unary_union([LineString([a, b]).buffer(0.004) for a, b in segs])
    out = []
    for p in getattr(g, 'geoms', [g]):
        x0, y0, x1, y1 = p.bounds
        if a_min <= (x1 - x0) * (y1 - y0) <= a_max and max(x1 - x0, y1 - y0) < 1.2:
            out.append([r3(x0 + 0.004), r3(y0 + 0.004), r3(x1 - 0.004), r3(y1 - 0.004)])
    return out


def fusionar(muros, solidos, tol_hueco=0.02, hueco_max=0.6):
    """Une los tramos colineales del mismo espesor cuando el hueco entre ellos está ocupado por una columna o columneta
    (o es menor de 2 cm). Devuelve la lista de corridas (mismo formato)."""
    grupos = collections.defaultdict(list)
    for m in muros: grupos[(m['o'], round(m['c'] / 0.02) * 0.02, m['e'])].append(m)
    out = []
    for (o, c, e), ms in grupos.items():
        ms = sorted(ms, key=lambda m: m['t0']); cur = dict(ms[0])
        for m in ms[1:]:
            hueco = m['t0'] - cur['t1']
            une = hueco <= tol_hueco
            if not une and hueco <= hueco_max:
                g = box(cur['t1'], c - e / 2, m['t0'], c + e / 2) if o == 'H' else box(c - e / 2, cur['t1'], c + e / 2, m['t0'])
                une = solidos.intersection(g).area >= 0.8 * g.area
            if une: cur['t1'] = max(cur['t1'], m['t1'])
            else: out.append(cur); cur = dict(m)
        out.append(cur)
    return out


def extender_a_columnetas(muros, ctas):
    """Alarga los extremos de cada corrida hasta cubrir la columneta contigua (las caras de muro paran en ella)."""
    for m in muros:
        for _ in range(3):
            cambio = False
            for c in ctas:
                if m['o'] == 'H':
                    a0, a1, b0, b1 = c[0], c[2], c[1], c[3]
                else:
                    a0, a1, b0, b1 = c[1], c[3], c[0], c[2]
                if not (b0 - 0.02 <= m['c'] <= b1 + 0.02): continue
                if abs(a1 - m['t0']) < 0.03 and a0 < m['t0']: m['t0'] = r3(a0); cambio = True
                if abs(a0 - m['t1']) < 0.03 and a1 > m['t1']: m['t1'] = r3(a1); cambio = True
            if not cambio: break
    return muros


def huecos(muros, cols, l_min=0.5, l_max=3.4):
    """Vanos sin muro en la línea de cada corrida: desde un extremo hasta el siguiente sólido (otro muro o columna)
    a menos de 3.4 m. -> [dict(o, c, t0, t1, e)]"""
    solidos = [rect_muro(m) for m in muros] + [box(*c) for c in cols]
    out = {}
    for i, m in enumerate(muros):
        h = m['e'] / 2 - 0.01
        for lado in (1, -1):
            t = m['t1'] if lado == 1 else m['t0']
            a, b = (t, t + lado * l_max)
            g = (box(min(a, b), m['c'] - h, max(a, b), m['c'] + h) if m['o'] == 'H' else box(m['c'] - h, min(a, b), m['c'] + h, max(a, b)))
            mejor = None
            for j, s in enumerate(solidos):
                if j == i or not s.intersects(g): continue
                x0, y0, x1, y1 = s.intersection(g).bounds
                d = ((x0 if lado == 1 else x1) if m['o'] == 'H' else (y0 if lado == 1 else y1)) - t
                d = d * lado
                if d > 0.02 and (mejor is None or d < mejor): mejor = d
            if mejor is not None and l_min <= mejor <= l_max:
                t0, t1 = sorted((t, t + lado * mejor))
                out[(m['o'], round(m['c'], 2), round(t0, 2), round(t1, 2))] = dict(o=m['o'], c=m['c'], t0=r3(t0), t1=r3(t1), e=m['e'])
    return list(out.values())


def restar(iv, cortes):
    out = []
    for s, t in iv:
        pos = s
        for a, b in sorted(cortes):
            if b <= pos or a >= t: continue
            if a > pos: out.append((pos, a))
            pos = max(pos, b)
        if t > pos: out.append((pos, t))
    return out


def ventanas_en_muros(muros, segs, piezas, l_min=0.35):
    """Líneas de vano (vidrio o marco) paralelas dentro de la franja de cada corrida -> tramos de ventana, cortados en
    las columnas y columnetas."""
    out = []
    for i, m in enumerate(muros):
        iv = []
        for a, b in segs:
            if eje(a, b) != m['o']: continue
            k = (a[1] + b[1]) / 2 if m['o'] == 'H' else (a[0] + b[0]) / 2
            if abs(k - m['c']) > m['e'] / 2 + 0.03: continue
            s, t = sorted((a[0], b[0]) if m['o'] == 'H' else (a[1], b[1]))
            s, t = max(s, m['t0']), min(t, m['t1'])
            if t - s > 0.05: iv.append((s, t))
        cortes = []
        for c in piezas:
            a0, a1, b0, b1 = (c[0], c[2], c[1], c[3]) if m['o'] == 'H' else (c[1], c[3], c[0], c[2])
            if b0 - 0.02 <= m['c'] <= b1 + 0.02: cortes.append((a0, a1))
        for s, t in restar(union_intervalos(iv, tol=0.08), cortes):
            if t - s >= l_min: out.append(dict(muro=i, o=m['o'], c=m['c'], t0=r3(s), t1=r3(t), e=m['e']))
    return out


def proyectar(muros, x, y, d_max, holgura=0.3):
    """Corrida más cercana a (x, y) cuya extensión contiene la proyección -> (i, t, distancia) o None."""
    mejor = None
    for i, m in enumerate(muros):
        t, d = (x, abs(y - m['c'])) if m['o'] == 'H' else (y, abs(x - m['c']))
        if m['t0'] - holgura <= t <= m['t1'] + holgura and d <= d_max and (mejor is None or d < mejor[2]):
            mejor = (i, min(max(t, m['t0']), m['t1']), d)
    return mejor


def en_linea(muros, cols, x, y, w, d_max=1.6, l_max=7.0):
    """Para un indicador sin vano ni muro: línea de muro (orientación, eje, espesor) más cercana y tramo libre entre
    sólidos que contiene la proyección. -> (o, c, e, t0, t1) del muro que se agrega como anfitrión, o None."""
    lineas = {}
    for m in muros:
        k = (m['o'], round(m['c'], 2))
        if k not in lineas or m['e'] > lineas[k]: lineas[k] = m['e']
    mejor = None
    for (o, c), e in lineas.items():
        t, d = (x, abs(y - c)) if o == 'H' else (y, abs(x - c))
        if d > d_max: continue
        sol = []
        for m in muros:
            if m['o'] == o and abs(m['c'] - c) < 0.05: sol.append((m['t0'], m['t1']))
            elif m['o'] != o and m['t0'] - 0.35 <= c <= m['t1'] + 0.35: sol.append((m['c'] - m['e'] / 2, m['c'] + m['e'] / 2))
        for q in cols:
            a0, a1, b0, b1 = (q[0], q[2], q[1], q[3]) if o == 'H' else (q[1], q[3], q[0], q[2])
            if b0 - 0.05 <= c <= b1 + 0.05: sol.append((a0, a1))
        if any(a - 0.01 <= t <= b + 0.01 for a, b in sol): continue
        izq = max([b for a, b in sol if b <= t], default=None); der = min([a for a, b in sol if a >= t], default=None)
        if izq is None and der is not None and der - t <= w + 0.6: izq = der - w - 0.2      # vano al final de la línea
        if der is None and izq is not None and t - izq <= w + 0.6: der = izq + w + 0.2
        if izq is None or der is None or der - izq > l_max or der - izq < w: continue
        if der - izq > w + 1.2:                                       # tramo abierto: solo un muro corto para la puerta
            t = min(max(t, izq + w / 2 + 0.1), der - w / 2 - 0.1); izq, der = t - w / 2 - 0.1, t + w / 2 + 0.1
        if mejor is None or d < mejor[0]: mejor = (d, (o, c, e, r3(izq), r3(der)))
    return mejor and mejor[1]


def anfitrion(muros, o, x, y):
    """Índice de la corrida (misma orientación) que contiene el punto (x, y) en su franja."""
    for i, m in enumerate(muros):
        if m['o'] != o: continue
        t, k = (x, y) if o == 'H' else (y, x)
        if abs(k - m['c']) <= m['e'] / 2 + 0.02 and m['t0'] - 0.01 <= t <= m['t1'] + 0.01: return i
    return None


def centro(v):
    t = (v['t0'] + v['t1']) / 2
    return (t, v['c']) if v['o'] == 'H' else (v['c'], t)


def asignar(vanos, inds, cuadro, d_max, dw_max):
    """Empareja cada vano con el indicador más cercano de ancho compatible (costo = distancia + 2 x diferencia de ancho)."""
    pares = []
    for i, v in enumerate(vanos):
        L = v['t1'] - v['t0']; cx, cy = centro(v)
        for j, (cod, x, y) in enumerate(inds):
            w = cuadro.get(cod, {}).get('ancho')
            dw = abs(w - L) if w else 0.3
            d = math.hypot(x - cx, y - cy)
            if d <= d_max and dw <= dw_max: pares.append((d + 2 * dw, i, j))
    usados_v, usados_i, asig = set(), set(), {}
    for c, i, j in sorted(pares):
        if i in usados_v or j in usados_i: continue
        usados_v.add(i); usados_i.add(j); asig[i] = j
    return asig, [j for j in range(len(inds)) if j not in usados_i]


# ================================================================== transformación planta A -> planta general
def traslacion(pa, pb, paso=0.02):
    """Votación de las diferencias pb - pa (extremos de las líneas de muro) -> (dx, dy, votos)."""
    pa = np.array(pa); pb = np.array(pb)
    d = (pb[None, :, :] - pa[:, None, :]).reshape(-1, 2)
    k = np.round(d / paso).astype(np.int64)
    u, n = np.unique(k, axis=0, return_counts=True)
    i = int(np.argmax(n)); c = u[i] * paso
    sel = np.all(np.abs(d - c) <= paso, axis=1)
    return float(d[sel, 0].mean()), float(d[sel, 1].mean()), int(n[i])


# ================================================================== principal
def principal():
    PG = leer(F_PG, filtro_y=lambda y: y > 9281850)
    A = leer(F_A); DT = leer(F_DT)
    cu_dt, cu_a = cuadros(DT['tablas']), cuadros(A['tablas'])
    dif_cuadros = []
    for cod in sorted(set(cu_dt) | set(cu_a)):
        for k in sorted(set(cu_dt.get(cod, {})) | set(cu_a.get(cod, {}))):
            a, b = cu_a.get(cod, {}).get(k), cu_dt.get(cod, {}).get(k)
            if a is None or b is None or any(a[c] != b[c] for c in ('cant', 'ancho', 'alto', 'alf')):
                dif_cuadros.append('%s %s: DT %s / plano A %s' % (cod, k, b and (b['cant'], b['ancho'], b['alto'], b['alf']),
                                                                 a and (a['cant'], a['ancho'], a['alto'], a['alf'])))

    loc = lambda p: (p[0] - OX, p[1] - OY)
    pg_lin = [(L, b, [loc(q) for q in p]) for L, b, p in PG['lineas'] if p]
    pg_arc = [(L, b, cx - OX, cy - OY, r, a0, a1) for L, b, cx, cy, r, a0, a1 in PG['arcos']]

    # títulos de las plantas en los planos A
    tit = {}
    for L, b, x, y, s in A['textos']:
        m = re.match(r'^PLANTA\s.*EDIFICACI.N\s*0?(\d)', s)
        if m and b is None: tit['E-0' + m.group(1)] = (x, y)
    a_lin = [(L, b, p) for L, b, p in A['lineas'] if p and L in ('MURO', 'MURO CORTE', '0_MUROS 1', '00muros gr')]

    res, informe = [], []
    for e in ESC['edificios']:
        cod = e['cod']; x0, y0, x1, y1 = e['rect']
        zona = box(x0 - 0.4, y0 - 0.4, x1 + 0.4, y1 + 0.4)
        dentro = lambda p: zona.contains(Point(p[0], p[1]))
        capas = collections.defaultdict(list)
        for L, b, p in pg_lin:
            if all(dentro(q) for q in p): capas[L].extend(aristas(p))
        # --- techo (PG-02): contorno = envolvente de las proyecciones de techo en la zona
        pr = [q for L in ('1-PROYECCIONES',) for ab in capas[L] for q in ab]
        if pr:
            xs, ys = [q[0] for q in pr], [q[1] for q in pr]
            techo = [r3(min(xs)), r3(min(ys)), r3(max(xs)), r3(max(ys))]
        else:
            techo = list(e['rect'])
        # --- muros, columnas, columnetas
        cols = piezas_cerradas(capas['1-COLUMNAS'] + capas['COLUMNAS'], 0.03, 0.5)
        ctas = piezas_cerradas(capas['1-COLUMNETAS'], 0.008, 0.2)
        solidos = unary_union([box(*c) for c in cols + ctas]) if cols + ctas else Polygon()
        caras = capas['1-MURO'] + capas['1-MUROS OTRO MATERIAL'] + capas['1-MUROS OTRO MATERIAL 2']
        muros = fusionar(muros_de_caras(caras), solidos)
        muros = extender_a_columnetas([m for m in muros if m['t1'] - m['t0'] >= 0.12], ctas)
        muros = fusionar(muros, solidos)
        bajos = [m for m in muros_de_caras(capas['1-MUROS BAJOS']) if m['t1'] - m['t0'] >= 0.12]
        vanos_h = huecos(muros, cols, l_max=3.6)
        vent = ventanas_en_muros(muros, capas['0_VANOS'] + capas['1-VANOS'] + capas['1-VIDRIO'], cols + ctas)
        diag = [(a, b) for L in capas for a, b in capas[L] if eje(a, b) is None and math.hypot(b[0] - a[0], b[1] - a[1]) > 5]
        # --- arcos de puerta (giro ~90°, radio 0.55-1.30)
        arcos = []
        for L, b, cx, cy, r, a0, a1 in pg_arc:
            span = (a1 - a0) % 360
            if 0.55 <= r <= 1.30 and 80 <= span <= 95 and L not in ('1-MOBILIARIO', 'LMOBILIARIO') and dentro((cx, cy)):
                arcos.append((cx, cy, r, a0, a1))
        # --- transformación de la planta A
        ta = tit.get(cod)
        tr = None
        if ta:
            pa = [q for L, b, p in a_lin for q in p if abs(q[0] - ta[0]) < 32 and -3 < q[1] - ta[1] < 48]
            pb = [q for ab in caras for q in ab]
            pa = sorted(set((round(x, 3), round(y, 3)) for x, y in pa)); pb = sorted(set((round(x, 3), round(y, 3)) for x, y in pb))
            if len(pa) > 6000: pa = pa[::len(pa) // 6000 + 1]
            dx, dy, votos = traslacion(pa, pb)
            tr = dict(dx=dx, dy=dy, votos=votos, n_pg=len(pb))
        # --- indicadores de la planta A en coordenadas locales
        ip, iv_ = [], []
        if tr:
            for n, x, y, at, b in A['inds']:
                X, Y = x + tr['dx'], y + tr['dy']
                if not box(x0 - 2.5, y0 - 2.5, x1 + 2.5, y1 + 2.5).contains(Point(X, Y)): continue
                v = list(at.values())
                if 'PUERT' in n:
                    num = at.get('D-01', ''); let = at.get('P-3', 'P')
                    ip.append((norm('%s-%s' % (let, num)), X, Y))
                else:
                    num = at.get('A-074', ''); iv_.append((norm('V-%s' % num), X, Y))
        cuadro = cu_dt.get(cod, {})
        obs = []

        def tipo_de(c, ancho_med, clase):
            """Datos del cuadro; si el código no está en el cuadro de la edificación, el del mismo tipo con ancho más parecido."""
            if c in cuadro: return c, dict(cuadro[c], ref=c), False
            cand = [(abs((v['ancho'] or 0) - ancho_med), k, v) for k, v in cuadro.items() if k[0] in clase]
            if not cand: return c, dict(cant=0, ancho=ancho_med, alto=2.50 if 'P' in clase else 1.99, alf=None, obs=''), True
            _, k, v = min(cand); return c, dict(v, ancho=r3(ancho_med), ref=k), True

        # --- puertas: vano detectado con indicador compatible; si no, proyección del indicador sobre el muro más cercano
        puertas, nuevos = [], []
        a_p, sin_p = asignar(vanos_h, ip, cuadro, 2.6, 0.45)
        for i, j in a_p.items():
            v = vanos_h[i]; cx, cy = centro(v); L = v['t1'] - v['t0']
            c, d, raro = tipo_de(ip[j][0], L, 'PM')
            w = min(d['ancho'] or L, L - 0.02)
            puertas.append(dict(cod=c, x=r3(cx), y=r3(cy), o=v['o'], ancho=r3(w), alto=d['alto'] or 2.50, obs=d['obs'], via='vano'))
            nuevos.append(dict(o=v['o'], c=v['c'], t0=v['t0'], t1=v['t1'], e=v['e']))
            if raro: obs.append('%s: indicador %s no figura en el cuadro de vanos; se usó el ancho del vano (%.2f)' % (cod, c, L))
        for j in sin_p:
            c0, x, y = ip[j]
            c, d, raro = tipo_de(c0, 0.9, 'PM'); w = d['ancho'] or 0.9
            ln = en_linea(muros + nuevos, cols, x, y, w)
            if ln:                                                    # vano sin muro dibujado: muro anfitrión en la línea
                o, cc, e_, t0, t1 = ln; t = (t0 + t1) / 2; w = min(w, t1 - t0 - 0.02)
                nuevos.append(dict(o=o, c=cc, t0=t0, t1=t1, e=e_))
                px, py = (t, cc) if o == 'H' else (cc, t)
                puertas.append(dict(cod=c, x=r3(px), y=r3(py), o=o, ancho=r3(w), alto=d['alto'] or 2.50, obs=d['obs'], via='linea'))
                continue
            pr = proyectar(muros, x, y, 1.6)
            if pr is None: obs.append('%s: indicador %s en (%.2f, %.2f) sin muro cercano; no se coloca' % (cod, c0, x, y)); continue
            i, t, _ = pr; m = muros[i]
            t = min(max(t, m['t0'] + w / 2 + 0.02), m['t1'] - w / 2 - 0.02)
            px, py = (t, m['c']) if m['o'] == 'H' else (m['c'], t)
            puertas.append(dict(cod=c, x=r3(px), y=r3(py), o=m['o'], ancho=r3(w), alto=d['alto'] or 2.50, obs=d['obs'], via='proyeccion'))
        muros = fusionar(muros + nuevos, solidos)

        # --- ventanas: tramo de vano en el muro con indicador compatible; si no, proyección del indicador
        ventanas = []
        a_v, sin_v = asignar(vent, iv_, cuadro, 3.2, 0.7)
        for i, j in a_v.items():
            v = vent[i]; cx, cy = centro(v); L = v['t1'] - v['t0']
            c, d, raro = tipo_de(iv_[j][0], L, 'V')
            w = min(d['ancho'] or L, L + 0.05)
            ventanas.append(dict(cod=c, x=r3(cx), y=r3(cy), o=v['o'], ancho=r3(w), alto=d['alto'] or 1.99, alf=d['alf'] if d['alf'] is not None else 1.30, via='vano'))
            if raro: obs.append('%s: indicador %s no figura en el cuadro de vanos; ancho del vano %.2f y alto/alféizar de %s' % (cod, c, L, d.get('ref')))
        for j in sin_v:
            c0, x, y = iv_[j]; pr = proyectar(muros, x, y, 3.2)
            if pr is None: obs.append('%s: indicador %s en (%.2f, %.2f) sin muro cercano; no se coloca' % (cod, c0, x, y)); continue
            i, t, _ = pr; m = muros[i]
            c, d, raro = tipo_de(c0, 1.5, 'V')
            w = d['ancho'] or 1.5; t = min(max(t, m['t0'] + w / 2 + 0.02), m['t1'] - w / 2 - 0.02)
            px, py = (t, m['c']) if m['o'] == 'H' else (m['c'], t)
            ventanas.append(dict(cod=c, x=r3(px), y=r3(py), o=m['o'], ancho=r3(w), alto=d['alto'] or 1.99,
                                 alf=d['alf'] if d['alf'] is not None else 1.30, via='proyeccion'))
        # tramos de ventana sin indicador (p. ej. V-51 y V-52 del SUM): se completan con el cuadro de vanos por ancho
        usados = set(a_v)
        falta = collections.Counter({k: d['cant'] for k, d in cuadro.items() if k[0] == 'V'})
        for v in ventanas: falta[v['cod']] -= 1
        for i, v in enumerate(vent):
            if i in usados: continue
            L = v['t1'] - v['t0']
            cand = [(abs(cuadro[k]['ancho'] - L), k) for k, n in falta.items() if n > 0 and cuadro[k]['ancho'] and abs(cuadro[k]['ancho'] - L) <= 0.25]
            if not cand: continue
            _, k = min(cand); falta[k] -= 1; d = cuadro[k]; cx, cy = centro(v)
            ventanas.append(dict(cod=k, x=r3(cx), y=r3(cy), o=v['o'], ancho=r3(min(d['ancho'], L + 0.05)), alto=d['alto'], alf=d['alf'], via='cuadro'))
            obs.append('%s: %s colocada en un vano de ventana sin indicador (ancho %.2f), según el cuadro de vanos' % (cod, k, L))
        # sobreluz de las puertas que la tienen (h = 0.785 sobre la hoja de 2.50)
        for p in puertas:
            p['sobreluz'] = 0.785 if re.search(r'sobre\s*luz', p['obs'], re.I) else 0.0
            p['vidrio'] = bool(re.search(r'vidrio templado con bisagra|Mampara|vidrio', p['obs'], re.I)) and not re.search(r'visor|sobre luz', p['obs'], re.I)
        # vanos que se pisan en el mismo muro (en planta y en altura): se deja el primero
        def tramo(v): t = v['x'] if v['o'] == 'H' else v['y']; return (t - v['ancho'] / 2, t + v['ancho'] / 2)
        def altura(v): return (0.0, v['alto'] + v.get('sobreluz', 0)) if 'alf' not in v else (v['alf'], v['alf'] + v['alto'])
        aceptados = []
        for lista, nom in ((puertas, 'puerta'), (ventanas, 'ventana')):
            limpio = []
            for v in sorted(lista, key=lambda v: v['via'] != 'vano'):
                h = anfitrion(muros, v['o'], v['x'], v['y']); v['muro'] = h
                if h is None: obs.append('%s: %s %s sin muro anfitrión; no se coloca' % (cod, nom, v['cod'])); continue
                choca = [u for u in aceptados if u['muro'] == h and min(tramo(u)[1], tramo(v)[1]) - max(tramo(u)[0], tramo(v)[0]) > 0.05]
                for u in list(choca):                                 # ventana alta sobre puerta: sin sobreluz y sin choque
                    if 'alf' in v and 'alf' not in u and v['alf'] >= u['alto'] - 0.01:
                        if u['sobreluz']: obs.append('%s: %s sin sobreluz por la ventana alta %s' % (cod, u['cod'], v['cod']))
                        u['sobreluz'] = 0.0; choca.remove(u)
                    elif min(altura(u)[1], altura(v)[1]) - max(altura(u)[0], altura(v)[0]) <= 0.01:
                        choca.remove(u)
                if choca: obs.append('%s: %s %s se superpone con %s; no se coloca' % (cod, nom, v['cod'], choca[0]['cod'])); continue
                limpio.append(v); aceptados.append(v)
            lista[:] = limpio
        # cotejo con el cuadro de vanos (DT)
        cnt = collections.Counter(v['cod'] for v in puertas + ventanas)
        for k, d in sorted(cuadro.items()):
            if cnt.get(k, 0) != d['cant']: obs.append('%s: %s colocadas %d, cuadro de vanos (DT) %d' % (cod, k, cnt.get(k, 0), d['cant']))

        res.append(dict(cod=cod, nombre=e.get('nombre', ''), techo=techo, cumbrera=e['cumbrera'], muros=muros, columnas=cols,
                        columnetas=ctas, tr=tr, huecos=vanos_h, tramos_ventana=vent, ind_p=ip, ind_v=iv_, puertas=puertas,
                        ventanas=ventanas, diag=diag, obs=obs))
        informe.append('%s: muros %d, columnas %d | puertas %d (ind. %d, en vano %d) | ventanas %d (ind. %d, en vano %d) | transf. %s/%s'
                       % (cod, len(muros), len(cols), len(puertas), len(ip), sum(p['via'] == 'vano' for p in puertas), len(ventanas),
                          len(iv_), sum(v['via'] == 'vano' for v in ventanas), tr and tr['votos'], tr and tr['n_pg']))
    print('\n'.join(informe)); print('\n'.join(dif_cuadros))
    for r in res: print('\n'.join(r['obs']))
    return res, A, cu_dt, dif_cuadros


# ================================================================== elementos para Revit
def modelo(r):
    """Muros (eje, espesor, base, tope), vigas, columnas, puertas, ventanas, coberturas, hastiales y piso de una edificación."""
    cod = r['cod']; N = NIVELES[cod]; npt, zv = N['npt'], N['viga']
    rects = [rect_muro(m) for m in r['muros']] + [box(*c) for c in r['columnas']]
    wx0, wy0, wx1, wy1 = unary_union(rects).bounds
    tx0, ty0, tx1, ty1 = r['techo']; eje_c = r['cumbrera']
    # nave central del SUM (E-05): entre los dos muros transversales interiores de todo el ancho
    nave = None
    if 'viga_nave' in N:
        lineas_h = collections.defaultdict(float)                   # muros transversales (partidos por las puertas) por eje
        for m in r['muros']:
            if m['o'] == 'H' and wy0 + 0.5 < m['c'] < wy1 - 0.5: lineas_h[round(m['c'], 2)] += m['t1'] - m['t0']
        tr_ = sorted(c for c, L in lineas_h.items() if L >= 0.6 * (wx1 - wx0))
        if len(tr_) >= 2: nave = (tr_[0], tr_[-1])
    def en_nave(y0_, y1_): return nave is not None and y0_ >= nave[0] - 0.3 and y1_ <= nave[1] + 0.3
    muros, vigas = [], []
    for m in r['muros']:
        piezas = [(m['t0'], m['t1'])]
        if nave and m['o'] == 'V':                                  # los muros largos se parten en los muros de la nave
            for yc in nave:
                piezas = [q for a, b in piezas for q in (((a, yc), (yc, b)) if a < yc < b else ((a, b),))]
        for a, b in piezas:
            if m['o'] == 'H': p0, p1, yy = (a, m['c']), (b, m['c']), (m['c'], m['c'])
            else: p0, p1, yy = (m['c'], a), (m['c'], b), (a, b)
            z1 = N['viga_nave'] if en_nave(*yy) else zv
            ext = (m['o'] == 'H' and min(abs(m['c'] - wy0), abs(m['c'] - wy1)) < 0.35) or \
                  (m['o'] == 'V' and min(abs(m['c'] - wx0), abs(m['c'] - wx1)) < 0.35)
            muros.append([r3(p0[0]), r3(p0[1]), r3(p1[0]), r3(p1[1]), m['e'], npt, r3(z1), bool(ext)])
            fondo = z1 - 0.41 if z1 > zv else min(FONDO_VIGA, z1 - 0.25)
            vigas.append([r3(p0[0]), r3(p0[1]), r3(p1[0]), r3(p1[1]), r3(m['e'] + 0.02), r3(fondo), r3(z1)])
    cols = []
    for c in r['columnas']:
        cx, cy = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
        z1 = N['viga_nave'] if nave and nave[0] - 0.4 <= cy <= nave[1] + 0.4 else zv
        cols.append([r3(cx), r3(cy), r3(c[2] - c[0]), r3(c[3] - c[1]), npt, r3(z1)])
    puertas = [dict(cod=p['cod'], x=p['x'], y=p['y'], o=p['o'], ancho=p['ancho'], alto=p['alto'], sill=npt, sobreluz=p['sobreluz'],
                    vidrio=p['vidrio'], via=p['via']) for p in r['puertas']]
    ventanas = [dict(cod=v['cod'], x=v['x'], y=v['y'], o=v['o'], ancho=v['ancho'], alto=v['alto'], sill=r3(npt + v['alf']), via=v['via'])
                for v in r['ventanas']]

    # coberturas a dos aguas (contorno de la PG-02, arranque en el borde del alero al nivel de viga, pendiente 30 %)
    techos, hastiales, aberturas, celosias = [], [], [], []
    across = (tx0, tx1) if eje_c == 'y' else (ty0, ty1)             # dirección de la pendiente
    def z_techo(base, a0, a1, a):                                   # altura de la cara inferior de la cobertura en 'a'
        return base + PEND * min(a - a0, a1 - a)
    def hastial(base, a0, a1, pos, zw):
        """Pentágono en el plano del muro de testero (eje 'pos'): de zw hasta la cobertura."""
        wa0, wa1 = (wx0, wx1) if eje_c == 'y' else (wy0, wy1)
        ar = (a0 + a1) / 2; pts2 = [(wa0, zw), (wa0, z_techo(base, a0, a1, wa0) - 0.02), (ar, z_techo(base, a0, a1, ar) - 0.02),
                                    (wa1, z_techo(base, a0, a1, wa1) - 0.02), (wa1, zw)]
        return [[r3(a), r3(pos), r3(z)] if eje_c == 'y' else [r3(pos), r3(a), r3(z)] for a, z in pts2]
    ends = (wy0 + 0.075, wy1 - 0.075) if eje_c == 'y' else (wx0 + 0.075, wx1 - 0.075)
    if nave:
        ya, yb = nave
        for rect, base, zw, testeros in (([tx0, ty0, tx1, ya], zv, zv, [ends[0]]), ([tx0, ya - 0.3, tx1, yb + 0.3], N['viga_nave'], N['viga_nave'], [ya, yb]),
                                         ([tx0, yb, tx1, ty1], zv, zv, [ends[1]])):
            techos.append(dict(rect=[r3(v) for v in rect], base=r3(base), pend=PEND, eje=eje_c))
            for pos in testeros: hastiales.append(hastial(base, across[0], across[1], pos, zw))
    else:
        techos.append(dict(rect=[r3(v) for v in r['techo']], base=r3(zv), pend=PEND, eje=eje_c))
        for pos in ends: hastiales.append(hastial(zv, across[0], across[1], pos, zv))
    if 'sobretecho' in N and r['diag']:                            # E-01: sobretecho sobre el lucernario (aspa de la PG-02)
        xs = [q[0] for ab in r['diag'] for q in ab]; ys = [q[1] for ab in r['diag'] for q in ab]
        lx0, ly0, lx1, ly1 = min(xs), min(ys), max(xs), max(ys)
        aberturas.append([r3(lx0), r3(ly0), r3(lx1), r3(ly1)])
        if eje_c == 'y': sr = [lx0 - 0.7, ly0 - 0.3, lx1 + 0.7, ly1 + 0.3]; s0, s1 = sr[0], sr[2]
        else: sr = [lx0 - 0.3, ly0 - 0.7, lx1 + 0.3, ly1 + 0.7]; s0, s1 = sr[1], sr[3]
        sbase = N['sobretecho'] - PEND * (s1 - s0) / 2
        techos.append(dict(rect=[r3(v) for v in sr], base=r3(sbase), pend=PEND, eje=eje_c, sobretecho=True))
        # celosías entre la cobertura y el sobretecho: lados largos y testeros
        la0, la1 = (lx0, lx1) if eje_c == 'y' else (ly0, ly1); lb0, lb1 = (ly0, ly1) if eje_c == 'y' else (lx0, lx1)
        P3 = lambda a, b, z: [r3(a), r3(b), r3(z)] if eje_c == 'y' else [r3(b), r3(a), r3(z)]
        for a in (la0, la1):
            zb, zt = z_techo(zv, across[0], across[1], a), z_techo(sbase, s0, s1, a)
            celosias.append([P3(a, lb0, zb), P3(a, lb1, zb), P3(a, lb1, zt), P3(a, lb0, zt)])
        ar = (la0 + la1) / 2
        for b in (lb0, lb1):
            celosias.append([P3(la0, b, z_techo(zv, across[0], across[1], la0)), P3(ar, b, z_techo(zv, across[0], across[1], ar)),
                             P3(la1, b, z_techo(zv, across[0], across[1], la1)), P3(la1, b, z_techo(sbase, s0, s1, la1)),
                             P3(ar, b, z_techo(sbase, s0, s1, ar)), P3(la0, b, z_techo(sbase, s0, s1, la0))])
    cumbreras = [r3(t['base'] + PEND * ((t['rect'][2] - t['rect'][0]) if eje_c == 'y' else (t['rect'][3] - t['rect'][1])) / 2) for t in techos]
    return dict(cod=cod, nombre=r['nombre'], npt=npt, piso=[r3(wx0 - 1.2), r3(wy0 - 1.2), r3(wx1 + 1.2), r3(wy1 + 1.2)],
                contorno_muros=[r3(wx0), r3(wy0), r3(wx1), r3(wy1)], techo=r['techo'], cumbrera=eje_c, muros=muros, vigas=vigas,
                columnas=cols, puertas=puertas, ventanas=ventanas, techos=techos, hastiales=hastiales, aberturas_techo=aberturas,
                celosias=celosias, nave=nave and [r3(nave[0]), r3(nave[1])], cumbreras_calculadas=cumbreras, niveles=N, obs=r['obs'])


def vista(r, m, ruta):
    """Planta de control: muros, columnas, puertas (verde) y ventanas (rojo) con su código, sobre la planta general."""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    x0, y0, x1, y1 = r['techo']
    fig, ax = plt.subplots(figsize=(14, 14 * (y1 - y0) / (x1 - x0) + 1.2))
    ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ls='--', lw=0.8, ec='0.5'))
    for w in m['muros']:
        a = LineString([(w[0], w[1]), (w[2], w[3])]).buffer(w[4] / 2, cap_style=2)
        ax.fill(*a.exterior.xy, color='0.25' if w[7] else '0.55', lw=0)
    for c in m['columnas']: ax.add_patch(plt.Rectangle((c[0] - c[2] / 2, c[1] - c[3] / 2), c[2], c[3], color='#7b1f2d'))
    for lst, col in ((m['puertas'], '#1f7a3a'), (m['ventanas'], '#c0392b')):
        for v in lst:
            o = 'H' if any(abs(v['y'] - w[1]) < 0.02 and abs(w[1] - w[3]) < 1e-6 and min(w[0], w[2]) - 0.01 <= v['x'] <= max(w[0], w[2]) + 0.01
                           for w in m['muros']) else 'V'
            h = v['ancho'] / 2
            ax.add_patch(plt.Rectangle((v['x'] - h, v['y'] - 0.14) if o == 'H' else (v['x'] - 0.14, v['y'] - h),
                                       2 * h if o == 'H' else 0.28, 0.28 if o == 'H' else 2 * h, color=col, alpha=0.8))
            ax.text(v['x'], v['y'] + (0.22 if o == 'H' else 0), v['cod'], fontsize=6.5, ha='center', va='bottom' if o == 'H' else 'center',
                    rotation=0 if o == 'H' else 90, color=col)
    for t in m['techos']:
        a, b, c, d = t['rect']
        if t['eje'] == 'y': ax.plot([(a + c) / 2] * 2, [b, d], color='#e67e22', lw=1, ls='-.')
        else: ax.plot([a, c], [(b + d) / 2] * 2, color='#e67e22', lw=1, ls='-.')
    ax.set_aspect('equal'); ax.set_xlim(x0 - 0.5, x1 + 0.5); ax.set_ylim(y0 - 0.5, y1 + 0.5)
    ax.set_title('%s %s - muros, columnas, puertas (verde) y ventanas (rojo); cumbrera en naranja' % (m['cod'], m['nombre']), fontsize=10)
    ax.tick_params(labelsize=7); fig.savefig(ruta, dpi=110, bbox_inches='tight'); plt.close(fig)


if __name__ == '__main__':
    res, A, cu_dt, dif = principal()
    edif = []
    for r in res:
        m = modelo(r); edif.append(m)
        vista(r, m, os.path.join(CONTROL, 'PLANTA_CONTROL_%s.png' % r['cod']))
    salida = dict(origen='E 349 090, N 9 281 900 (copia PG-02 de la planta general); metros', pendiente=PEND, fondo_viga=FONDO_VIGA,
                  diferencias_cuadros_dt_vs_a=dif, cuadros_dt=cu_dt, edificios=edif)
    json.dump(salida, open(os.path.join(AQUI, 'edificaciones_revit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for m in edif:
        print('%s: muros %d, columnas %d, puertas %d, ventanas %d, techos %d, hastiales %d, cumbreras %s (rotulado %s)'
              % (m['cod'], len(m['muros']), len(m['columnas']), len(m['puertas']), len(m['ventanas']), len(m['techos']),
                 len(m['hastiales']), m['cumbreras_calculadas'], m['niveles'].get('techo')))
