# -*- coding: utf-8 -*-
"""Genera el script de Dynamo que modela en Revit, con elementos nativos (familias de sistema y cargables), la arquitectura
del Hogar de Refugio Temporal (CUI 2675514). Las edificaciones salen de los planos de la arquitecta (edificaciones_revit.json, que
escribe lee_edificaciones.py desde la PG 01-PG 02, las A 01-A 09 y los DT-01 a DT-15); el resto, de escena.json:

  - materiales TP-1 (RGB 123-31-45), TP-2 (RGB 125-133-139), TP-3 (RAL 9010), concreto, calamina, área verde;
  - tipos de muro, piso y cubierta propios (prefijo "HR-");
  - E-01 a E-09: piso +0.15; muros reales exteriores e interiores con su espesor (TP-2) hasta el fondo de viga +3.44; vigas TP-1
    sobre cada muro hasta el nivel superior de viga de los cortes (+3.70 en E-01, +3.85 en las demás; nave del SUM +5.05);
    columnas TP-1 con su sección de la planta; puertas y ventanas en su vano, con el ancho, alto y alféizar del cuadro de vanos
    de los DT (sobreluz fija sobre las puertas que la llevan); cubiertas a dos aguas con el contorno de la PG-02 (pendiente 30 %,
    arranque en el borde del alero al nivel de viga), hastiales TP-3 en los testeros; E-05 en tres cuerpos (nave central más
    alta); E-01 con sobretecho sobre el lucernario, abertura en la cubierta y celosías;
  - losa deportiva OC-06: losa, 14 columnas y cubierta en arco (cubierta por extrusión, flecha 4.20 sobre columnas de 6.00);
  - pórtico de ingreso OE-01: columnas C-1, viga VG-1, cielo CR-1, parapeto PL-2, muros laterales de perfil, muro M-1, caseta
    y losa inclinada (5.72 a 4.19);
  - cerco perimétrico de muro TP-3 de 2.40 con zócalo TP-2 y columnas cada 3 m (sin rejas);
  - veredas, pavimento de concreto con las áreas verdes como huecos, áreas verdes y patio cívico;
  - árboles del lote con la familia de vegetación (RPC) cargada en el proyecto.
Lo que no es arquitectura (red de drenaje, juegos, bancas OC-01, portones, letras, tanque, estacionamientos, cancha) va en el
IFC complementario (exporta_ifc.py --complemento) para vincularlo encima, en la misma posición (origen a origen).

Uso: python lee_edificaciones.py (solo si cambian los DXF) y python revit_nativo.py  ->  entregables/modelo_revit/DYNAMO_MODELO_NATIVO_HOGAR_REFUGIO.dyn y .py
"""
import json, math, os, uuid
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
D = json.load(open(os.path.join(AQUI, 'escena.json')))
SAL = os.path.join(RAIZ, 'entregables', 'modelo_revit'); os.makedirs(SAL, exist_ok=True)
r3 = lambda v: round(float(v), 3)

# ------------------------------------------------------------------ edificaciones (leídas de los planos por lee_edificaciones.py)
ED = json.load(open(os.path.join(AQUI, 'edificaciones_revit.json'), encoding='utf-8'))
PEND, FONDO_VIGA = ED['pendiente'], ED['fondo_viga']


def anfitrion(muros, v):
    """Índice del muro cuyo eje contiene el vano completo (mismo sentido, eje a menos de 6 cm)."""
    mejor = None
    for i, w in enumerate(muros):
        h = abs(w[1] - w[3]) < 1e-6
        if (v['o'] == 'H') != h: continue
        d, c, a, b = (abs(w[1] - v['y']), v['x'], min(w[0], w[2]), max(w[0], w[2])) if h else (abs(w[0] - v['x']), v['y'], min(w[1], w[3]), max(w[1], w[3]))
        if d < 0.06 and a - 0.01 <= c - v['ancho'] / 2 and c + v['ancho'] / 2 <= b + 0.01 and (mejor is None or d < mejor[0]): mejor = (d, i)
    if mejor is None: raise SystemExit('%s sin muro anfitrión en %.2f, %.2f' % (v['cod'], v['x'], v['y']))
    return mejor[1]


def sin_solapes(muros, vigas, vanos):
    """Recorta el más corto de dos muros paralelos que se montan (Revit no puede mantenerlos unidos); quita los que quedan dentro.
    Los muros que llevan puertas o ventanas se recortan al final, para que conserven su vano."""
    W = [list(w) for w in muros]; V = [list(v) for v in vigas]
    con_vano = {anfitrion(muros, v) for v in vanos}
    for i in sorted(range(len(W)), key=lambda k: (k in con_vano, abs(W[k][2] - W[k][0]) + abs(W[k][3] - W[k][1]))):
        a = W[i]; h = abs(a[1] - a[3]) < 1e-6; k0, k1 = (0, 2) if h else (1, 3); c = 1 if h else 0
        for j, b in enumerate(W):
            if j == i or b is None or a is None or (abs(b[1] - b[3]) < 1e-6) != h or abs(a[c] - b[c]) >= (a[4] + b[4]) / 2: continue
            a0, a1 = sorted((a[k0], a[k1])); b0, b1 = sorted((b[k0], b[k1]))
            if min(a1, b1) - max(a0, b0) <= 0.02: continue
            if b0 <= a0 + 0.02 and a1 <= b1 + 0.02: W[i] = a = None; break   # queda dentro del otro
            a0, a1 = (b1, a1) if a0 >= b0 else (a0, b0)                     # se deja la parte que sobresale
            a[k0], a[k1] = round(a0, 3), round(a1, 3); V[i][k0], V[i][k1] = a[k0], a[k1]
    return [w for w in W if w is not None], [v for w, v in zip(W, V) if w is not None]


edificios = []
for e in ED['edificios']:
    e['muros'], e['vigas'] = sin_solapes(e['muros'], e['vigas'], e['puertas'] + e['ventanas'])
    for v in e['puertas'] + e['ventanas']: v['muro'] = anfitrion(e['muros'], v)
    edificios.append({k: e[k] for k in ('cod', 'nombre', 'npt', 'piso', 'muros', 'vigas', 'columnas', 'puertas', 'ventanas', 'techos',
                                         'hastiales', 'aberturas_techo', 'celosias')})

# ------------------------------------------------------------------ losa deportiva, pórtico OE-01, cerco
lx0, ly0, lx1, ly1 = D['losa']
losa = dict(rect=[lx0, ly0, lx1, ly1], h_col=6.0, flecha=4.2,
            columnas=[[r3(xx), r3(ly0 + (ly1 - ly0) * i / 6)] for i in range(7) for xx in (lx0, lx1)])
gx0, gy0, gx1, gy1 = D['garita']; FX = [0.0, 2.08, 6.97, 8.93, 13.75]
X = lambda d: gx0 + d * (gx1 - gx0) / 13.75
yf, yb = gy0, gy1
oe01 = dict(gx0=gx0, gx1=gx1, yf=yf, yb=yb,
            columnas=[[r3(X(min(max(d, 0.14), 13.61))), r3(yy)] for d in FX for yy in (yf + 0.2, yb - 0.2)],
            m1=[r3(X(2.21)), r3(yf + 0.15), r3(X(6.84)), r3(yb - 0.15)], caseta=[r3(X(7.0)), r3(yf + 0.3), r3(X(8.9)), r3(yb - 0.15)])
XO, XE, YF, YN = 1.05, 71.76, 18.0, 131.21
cerco = [[XO, YF, gx0, YF], [gx1, YF, XE, YF], [XE, YF, XE, YN], [XE, YN, XO, YN], [XO, YN, XO, YF]]

# ------------------------------------------------------------------ pisos: veredas, pavimento (con huecos) y áreas verdes
def anillos(g):
    out = []
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty or p.area < 0.5:
            continue
        p = p.simplify(0.02)
        out.append([[[r3(x), r3(y)] for x, y in list(p.exterior.coords)[:-1]]] +
                   [[[r3(x), r3(y)] for x, y in list(i.coords)[:-1]] for i in p.interiors if Polygon(i).area > 0.3])
    return out


VERDES = unary_union([Polygon(e_, i_).buffer(0) for e_, i_ in D['verdes']])
LOTE = box(1.05, 18.0, 71.76, 131.21)
EDIF = unary_union([box(*e['piso']) for e in edificios] + [box(lx0, ly0, lx1, ly1), box(gx0 - 0.5, yf - 0.6, gx1 + 0.5, yb + 0.6)])
veredas = [Polygon(p).buffer(0) for p in D['veredas'] if len(p) >= 3]
pav = LOTE.difference(VERDES).difference(EDIF).difference(unary_union(veredas)).buffer(-0.01).buffer(0.01)
pisos = dict(veredas=anillos(unary_union(veredas).difference(EDIF)), pavimento=anillos(pav),
             verdes=anillos(VERDES.intersection(LOTE).difference(EDIF)), plaza=[[[[D['plaza'][0], D['plaza'][1]], [D['plaza'][2], D['plaza'][1]],
                                                                                [D['plaza'][2], D['plaza'][3]], [D['plaza'][0], D['plaza'][3]]]]])
arboles = [list(p) for p in D['arboles']] + [[6.0, 52], [6.0, 60], [6.0, 68], [2.5, 46], [66, 33], [66, 45], [66, 56], [66, 70], [66, 82],
                                             [28, 60], [29, 90], [52, 90], [48.5, 114], [60, 112], [28.8, 18.8], [58, 19.3]]
DATOS = dict(edificios=edificios, losa=losa, oe01=oe01, cerco=cerco, pisos=pisos, arboles=arboles, medidas=dict(PEND=PEND, FONDO_VIGA=FONDO_VIGA))

# ------------------------------------------------------------------ script de Dynamo (Python Script, CPython3 / PythonNet3)
CODIGO = r'''# Modelo nativo del Hogar de Refugio Temporal (CUI 2675514) - Revit + Dynamo (nodo Python Script, CPython3 o PythonNet3)
# Correr UNA vez en un proyecto nuevo (plantilla de arquitectura), con las familias de puerta, ventana, columna y vegetación
# cargadas. Medidas en metros (se pasan a pies). Origen local = E 349 090, N 9 281 900 (mismo origen del IFC complementario).
import clr, json, math
clr.AddReference('RevitAPI'); clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.DB.Visual import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from System.Collections.Generic import List

import traceback
doc = DocumentManager.Instance.CurrentDBDocument
D = json.loads(DATOS_JSON)
LOG = []
cuenta = {}
def _principal():
    M = D['medidas']
    FT = 1 / 0.3048
    def ft(v): return v * FT
    def P(x, y, z=0.0): return XYZ(ft(x), ft(y), ft(z))
    def nota(t): LOG.append(t)

    TransactionManager.Instance.EnsureInTransaction(doc)

    # ---------------- nivel
    niveles = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(), key=lambda l: abs(l.Elevation))
    NIV = niveles[0] if niveles else Level.Create(doc, 0.0)

    # ---------------- materiales con color (sombreado) y apariencia (realista)
    PLANTILLA_APAR = None
    for a in FilteredElementCollector(doc).OfClass(AppearanceAssetElement).ToElements():
        try:
            if a.GetRenderingAsset().FindByName('generic_diffuse') is not None:
                PLANTILLA_APAR = a; break
        except Exception:
            pass
    MATS = {}
    def material(nombre, rgb):
        if nombre in MATS: return MATS[nombre]
        ex = [m for m in FilteredElementCollector(doc).OfClass(Material).ToElements() if m.Name == nombre]
        mat = ex[0] if ex else doc.GetElement(Material.Create(doc, nombre))
        mat.Color = Color(rgb[0], rgb[1], rgb[2]); mat.UseRenderAppearanceForShading = False
        if PLANTILLA_APAR is not None and not ex:
            try:
                ap = PLANTILLA_APAR.Duplicate('Apar ' + nombre)
                esc = AppearanceAssetEditScope(doc)
                asset = esc.Start(ap.Id)
                asset.FindByName('generic_diffuse').SetValueAsColor(Color(rgb[0], rgb[1], rgb[2]))
                esc.Commit(True); esc.Dispose()
                mat.AppearanceAssetId = ap.Id
            except Exception as ex_:
                nota('apariencia %s: %s' % (nombre, ex_))
        MATS[nombre] = mat.Id
        return mat.Id

    TP1 = material('HR TP-1 Guinda', (123, 31, 45)); TP2 = material('HR TP-2 Gris', (125, 133, 139))
    TP3 = material('HR TP-3 Blanco RAL 9010', (241, 236, 225)); CONC = material('HR Concreto', (186, 182, 174))
    VER = material('HR Vereda', (190, 186, 178)); CAL = material('HR Calamina', (196, 200, 204))
    PASTO = material('HR Area verde', (88, 128, 58)); ACERO = material('HR Acero', (110, 115, 120))
    ADOQ = material('HR Adoquin', (150, 92, 74)); CANCHA = material('HR Losa deportiva', (150, 62, 52))

    # ---------------- tipos de muro, piso y cubierta de una capa
    def tipo(clase, base_nombre, nombre, ancho, mat, funcion=MaterialFunctionAssignment.Structure):
        """Tipo de una sola capa (espesor y material); si ya existe (corrida anterior) se le vuelve a fijar la capa."""
        ex = [t for t in FilteredElementCollector(doc).OfClass(clase).ToElements() if t.Name == nombre]
        if ex:
            t = ex[0]
        else:
            bases = [t for t in FilteredElementCollector(doc).OfClass(clase).ToElements()
                     if (clase != WallType or t.Kind == WallKind.Basic) and t.GetCompoundStructure() is not None]
            t = doc.GetElement(bases[0].Duplicate(nombre).Id)
        errores = []
        # 1) la estructura del tipo base con una sola capa (núcleo) del espesor y material pedidos
        try:
            cs = t.GetCompoundStructure()
            capas = List[CompoundStructureLayer]()
            capas.Add(CompoundStructureLayer(ft(ancho), funcion, mat))
            cs.SetLayers(capas)
            cs.SetNumberOfShellLayers(ShellLayerType.Exterior, 0)
            cs.SetNumberOfShellLayers(ShellLayerType.Interior, 0)
            try: cs.StructuralMaterialIndex = 0
            except Exception: pass
            t.SetCompoundStructure(cs)
            return t
        except Exception as ex_:
            errores.append(str(ex_).split('\n')[0])
        # 2) estructura nueva de una capa
        try:
            t.SetCompoundStructure(CompoundStructure.CreateSingleLayerCompoundStructure(funcion, ft(ancho), mat))
            return t
        except Exception as ex_:
            errores.append(str(ex_).split('\n')[0])
        # 3) solo el material en todas las capas del tipo base (espesor del tipo base)
        try:
            cs = t.GetCompoundStructure()
            for i in range(cs.LayerCount): cs.SetMaterialId(i, mat)
            t.SetCompoundStructure(cs)
        except Exception as ex_:
            errores.append(str(ex_).split('\n')[0])
        nota('%s: %s' % (nombre, ' | '.join(errores)))
        return t

    W_TP2 = tipo(WallType, '', 'HR-Muro TP-2 e=0.15', 0.15, TP2)
    W_VIGA = tipo(WallType, '', 'HR-Viga collar TP-1 0.23', 0.23, TP1)
    W_HAST = tipo(WallType, '', 'HR-Hastial TP-3 e=0.20', 0.20, TP3)
    W_CERCO = tipo(WallType, '', 'HR-Cerco TP-3 e=0.15', 0.15, TP3)
    W_ZOC = tipo(WallType, '', 'HR-Zocalo cerco TP-2 e=0.17', 0.17, TP2)
    W_PARA = tipo(WallType, '', 'HR-Parapeto PL-2 TP-3 e=0.35', 0.35, TP3)
    W_LAT = tipo(WallType, '', 'HR-Muro lateral OE-01 TP-2 e=0.20', 0.20, TP2)
    F_PISO = tipo(FloorType, '', 'HR-Piso concreto e=0.15', 0.15, CONC)
    F_VER = tipo(FloorType, '', 'HR-Vereda e=0.10', 0.10, VER)
    F_PAV = tipo(FloorType, '', 'HR-Pavimento concreto e=0.10', 0.10, CONC)
    F_VERDE = tipo(FloorType, '', 'HR-Area verde e=0.05', 0.05, PASTO)
    F_ADOQ = tipo(FloorType, '', 'HR-Patio civico adoquin e=0.12', 0.12, ADOQ)
    F_LOSA = tipo(FloorType, '', 'HR-Losa deportiva e=0.12', 0.12, CANCHA)
    R_CAL = tipo(RoofType, '', 'HR-Cobertura calamina e=0.05', 0.05, CAL)
    R_LOSA = tipo(RoofType, '', 'HR-Cobertura losa OE-01 e=0.20', 0.20, CONC)

    # ---------------- utilidades
    def lazo(pts):
        cl = CurveLoop()
        for i in range(len(pts)):
            a = pts[i]; b = pts[(i + 1) % len(pts)]
            if a.DistanceTo(b) > 0.003: cl.Append(Line.CreateBound(a, b))
        return cl

    def piso(anillos, ftipo, z_sup):
        n = 0
        for poli in anillos:
            try:
                loops = List[CurveLoop]()
                for r in poli: loops.Add(lazo([P(x, y) for x, y in r]))
                fl = Floor.Create(doc, loops, ftipo.Id, NIV.Id)
                fl.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(ft(z_sup))
                n += 1
            except Exception as ex_:
                nota('piso %s: %s' % (ftipo.Name, ex_))
        return n

    def muro(x0, y0, x1, y1, wtipo, z0, h):
        w = Wall.Create(doc, Line.CreateBound(P(x0, y0), P(x1, y1)), wtipo.Id, NIV.Id, ft(h), ft(z0), False, False)
        return w

    def muro_perfil(pts, wtipo):
        c = List[Curve]()
        for i in range(len(pts)):
            a = P(*pts[i]); b = P(*pts[(i + 1) % len(pts)])
            if a.DistanceTo(b) > 0.003: c.Add(Line.CreateBound(a, b))
        return Wall.Create(doc, c, wtipo.Id, NIV.Id, False)

    def solido(x0, y0, z0, x1, y1, z1, mat, cat, nombre):
        """Caja como DirectShape (categoría nativa con material), para piezas que no tienen familia en el proyecto."""
        loops = List[CurveLoop](); loops.Add(lazo([P(x0, y0, z0), P(x1, y0, z0), P(x1, y1, z0), P(x0, y1, z0)]))
        so = SolidOptions(mat, ElementId.InvalidElementId)
        s = GeometryCreationUtilities.CreateExtrusionGeometry(loops, XYZ.BasisZ, ft(z1 - z0), so)
        ds = DirectShape.CreateElement(doc, ElementId(cat))
        g = List[GeometryObject](); g.Add(s); ds.SetShape(g); ds.Name = nombre
        return ds

    def simbolo(cat, claves, nombre_tipo, dims=(), mat=None):
        """Tipo de familia cargada: el primero cuyo nombre tenga una de las claves; se duplica con las medidas pedidas.
        dims = [(valor_m, [nombres de parámetro], [BuiltInParameter])]."""
        sims = [s for s in FilteredElementCollector(doc).OfCategory(cat).OfClass(FamilySymbol).ToElements()]
        if not sims: return None
        elegido = None
        for k in claves:
            for s in sims:
                if k.lower() in (s.FamilyName + ' ' + s.Name).lower(): elegido = s; break
            if elegido: break
        elegido = elegido or sims[0]
        ex = [s for s in sims if s.Name == nombre_tipo and s.FamilyName == elegido.FamilyName]
        if ex: s = ex[0]
        else:
            s = doc.GetElement(elegido.Duplicate(nombre_tipo).Id)
            for val, nombres, bips in dims:
                p = None
                for b in bips:
                    q = s.get_Parameter(b)
                    if q is not None and not q.IsReadOnly: p = q; break
                if p is None:
                    for n in nombres:
                        q = s.LookupParameter(n)
                        if q is not None and not q.IsReadOnly: p = q; break
                if p is not None: p.Set(ft(val))
                else: nota('%s: sin parámetro %s' % (nombre_tipo, nombres[0]))
            if mat is not None:
                q = s.LookupParameter('Material')
                if q is not None and not q.IsReadOnly: q.Set(mat)
        if not s.IsActive: s.Activate()
        return s

    S_COL = {}
    def columna(x, y, b, h, z0, z1, mat, nombre):
        k = (b, h, mat.IntegerValue if hasattr(mat, 'IntegerValue') else str(mat))
        if k not in S_COL:
            S_COL[k] = simbolo(BuiltInCategory.OST_Columns, ('rectangular', 'rectangle'), 'HR-Columna %.2fx%.2f %s' % (b, h, doc.GetElement(mat).Name),
                               [(b, ['Width', 'Ancho', 'b'], []), (h, ['Depth', 'Profundidad', 'h'], [])], mat)
        s = S_COL[k]
        if s is not None:
            try:
                c = doc.Create.NewFamilyInstance(P(x, y, 0), s, NIV, StructuralType.NonStructural)
                for bip, val in ((BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM, ft(z0)), (BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM, ft(z1))):
                    q = c.get_Parameter(bip)
                    if q is not None and not q.IsReadOnly: q.Set(val)
                q = c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM)
                if q is not None and not q.IsReadOnly: q.Set(NIV.Id)
                return c
            except Exception as ex_:
                nota('columna familia: %s' % ex_)
        return solido(x - b / 2, y - h / 2, z0, x + b / 2, y + h / 2, z1, mat, BuiltInCategory.OST_Columns, nombre)

    def techo_huella(rect, base, pend, eje, rtipo):
        x0, y0, x1, y1 = rect
        ca = CurveArray()
        for a, b in ((P(x0, y0), P(x1, y0)), (P(x1, y0), P(x1, y1)), (P(x1, y1), P(x0, y1)), (P(x0, y1), P(x0, y0))):
            ca.Append(Line.CreateBound(a, b))
        try:
            res = doc.Create.NewFootPrintRoof(ca, NIV, rtipo, ModelCurveArray())
        except Exception:
            res = doc.Create.NewFootPrintRoof(ca, NIV, rtipo)
        roof = res[0] if isinstance(res, tuple) else res
        roof.get_Parameter(BuiltInParameter.ROOF_LEVEL_OFFSET_PARAM).Set(ft(base))
        for arr in roof.GetProfiles():
            for mc in arr:
                ln = mc.GeometryCurve; d = ln.GetEndPoint(1) - ln.GetEndPoint(0)
                paralelo_y = abs(d.Y) > abs(d.X)
                define = (eje == 'y' and paralelo_y) or (eje == 'x' and not paralelo_y)
                if eje == 'una':
                    define = abs(ln.GetEndPoint(0).Y - ft(y1)) < 0.01 and abs(ln.GetEndPoint(1).Y - ft(y1)) < 0.01
                try:
                    roof.set_DefinesSlope(mc, define)
                    if define: roof.set_SlopeAngle(mc, pend)
                except Exception:
                    roof.DefinesSlope[mc] = define
                    if define: roof.SlopeAngle[mc] = pend
        return roof

    def suma(k, n=1): cuenta[k] = cuenta.get(k, 0) + n

    # ---------------- edificaciones E-01 a E-09 (muros, vanos, alturas y coberturas leídos de los planos)
    W_MURO = {}
    def tipo_muro(e_):
        k = round(e_, 2)
        if k not in W_MURO: W_MURO[k] = tipo(WallType, '', 'HR-Muro TP-2 e=%.2f' % k, k, TP2)
        return W_MURO[k]
    W_CEL = tipo(WallType, '', 'HR-Celosia sobretecho TP-1 e=0.05', 0.05, TP1)

    S_PUERTA = {}; S_VENT = {}
    def familia_puerta(ancho, alto, vidrio):
        k = (ancho, alto, vidrio)
        if k not in S_PUERTA:
            S_PUERTA[k] = simbolo(BuiltInCategory.OST_Doors, ('double glass', 'doble', 'glass', 'vidrio') if vidrio else ('single-flush', 'single', 'simple'),
                                  'HR-Puerta %.2fx%.2f%s' % (ancho, alto, ' vidrio' if vidrio else ''),
                                  [(ancho, ['Width', 'Ancho'], [BuiltInParameter.DOOR_WIDTH, BuiltInParameter.FAMILY_WIDTH_PARAM]),
                                   (alto, ['Height', 'Altura'], [BuiltInParameter.DOOR_HEIGHT, BuiltInParameter.FAMILY_HEIGHT_PARAM])])
        return S_PUERTA[k]

    def familia_ventana(ancho, alto, fija=False):
        k = (ancho, alto, fija)
        if k not in S_VENT:
            S_VENT[k] = simbolo(BuiltInCategory.OST_Windows, ('fixed', 'fija', 'sliding', 'corrediza') if fija else ('sliding', 'corrediza', 'fixed', 'fija'),
                                'HR-%s %.2fx%.2f' % ('Sobreluz' if fija else 'Ventana', ancho, alto),
                                [(ancho, ['Width', 'Ancho'], [BuiltInParameter.WINDOW_WIDTH, BuiltInParameter.FAMILY_WIDTH_PARAM]),
                                 (alto, ['Height', 'Altura'], [BuiltInParameter.WINDOW_HEIGHT, BuiltInParameter.FAMILY_HEIGHT_PARAM])])
        return S_VENT[k]

    def vano(s, host, v, sill):
        fi = doc.Create.NewFamilyInstance(P(v['x'], v['y'], sill), s, host, NIV, StructuralType.NonStructural)
        pa = fi.get_Parameter(BuiltInParameter.INSTANCE_SILL_HEIGHT_PARAM)
        if pa is not None and not pa.IsReadOnly: pa.Set(ft(sill))
        return fi

    for e in D['edificios']:
        try:
            p_ = e['piso']
            piso([[[[p_[0], p_[1]], [p_[2], p_[1]], [p_[2], p_[3]], [p_[0], p_[3]]]]], F_PISO, e['npt'])
            muros = []
            for (x0, y0, x1, y1, esp, z0, z1, ext), vg in zip(e['muros'], e['vigas']):
                fondo = vg[5]                                              # el muro llega al fondo de la viga; encima, la viga TP-1
                w = muro(x0, y0, x1, y1, tipo_muro(esp), z0, fondo - z0); muros.append(w); suma('muros')
                for extremo in (0, 1):                                     # los muros llegan a tope a columnas y a otros muros:
                    try: WallUtils.DisallowWallJoinAtEnd(w, extremo)       # sin uniones automáticas ("Can't keep elements joined")
                    except Exception: pass
                a = vg[4] / 2
                if abs(y0 - y1) < 1e-6:
                    solido(min(x0, x1), y0 - a, fondo, max(x0, x1), y0 + a, vg[6], TP1, BuiltInCategory.OST_StructuralFraming, e['cod'] + ' viga TP-1')
                else:
                    solido(x0 - a, min(y0, y1), fondo, x0 + a, max(y0, y1), vg[6], TP1, BuiltInCategory.OST_StructuralFraming, e['cod'] + ' viga TP-1')
                suma('vigas')
            cols = []
            for (x, y, b, h, z0, z1) in e['columnas']:
                cols.append(columna(x, y, round(b, 2), round(h, 2), z0, z1, TP1, e['cod'] + ' columna TP-1')); suma('columnas')
            doc.Regenerate()
            for c in cols:                                                 # la columna queda en TP-1 (no toma el material del muro)
                for w in muros:
                    try:
                        if JoinGeometryUtils.AreElementsJoined(doc, c, w): JoinGeometryUtils.UnjoinGeometry(doc, c, w)
                    except Exception: pass
            for v in e['puertas']:
                try:
                    s = familia_puerta(v['ancho'], v['alto'], v['vidrio'])
                    if s is None: nota('sin familia de puerta cargada'); continue
                    vano(s, muros[v['muro']], v, v['sill']); suma('puertas')
                    hs = round(M['FONDO_VIGA'] - (v['sill'] + v['alto']), 3)
                    if v['sobreluz'] and hs > 0.2:                         # sobreluz fija sobre la puerta, hasta el fondo de la viga
                        s2 = familia_ventana(v['ancho'], hs, True)
                        if s2 is not None: vano(s2, muros[v['muro']], v, v['sill'] + v['alto']); suma('sobreluces')
                except Exception as ex_:
                    nota('%s puerta %s: %s' % (e['cod'], v['cod'], ex_))
            for v in e['ventanas']:
                try:
                    s = familia_ventana(v['ancho'], v['alto'])
                    if s is None: nota('sin familia de ventana cargada'); continue
                    vano(s, muros[v['muro']], v, v['sill']); suma('ventanas')
                except Exception as ex_:
                    nota('%s ventana %s: %s' % (e['cod'], v['cod'], ex_))
            for h in e['hastiales']:
                try: muro_perfil(h, W_HAST); suma('hastiales')
                except Exception as ex_: nota('%s hastial: %s' % (e['cod'], ex_))
            techo_ppal = None
            for t in e['techos']:
                try:
                    r_ = techo_huella(t['rect'], t['base'], t['pend'], t['eje'], R_CAL); suma('cubiertas a dos aguas')
                    if not t.get('sobretecho') and techo_ppal is None: techo_ppal = r_
                except Exception as ex_:
                    nota('%s cubierta: %s' % (e['cod'], ex_))
            for (x0, y0, x1, y1) in e['aberturas_techo']:                 # lucernario bajo el sobretecho (E-01)
                try:
                    doc.Regenerate()
                    ca = CurveArray()
                    for a, b in ((P(x0, y0), P(x1, y0)), (P(x1, y0), P(x1, y1)), (P(x1, y1), P(x0, y1)), (P(x0, y1), P(x0, y0))):
                        ca.Append(Line.CreateBound(a, b))
                    doc.Create.NewOpening(techo_ppal, ca, True); suma('aberturas de cobertura')
                except Exception as ex_:
                    nota('%s abertura de cobertura: %s' % (e['cod'], ex_))
            for c in e['celosias']:
                try: muro_perfil(c, W_CEL); suma('celosias')
                except Exception as ex_: nota('%s celosia: %s' % (e['cod'], ex_))
        except Exception as ex_:
            nota('%s: %s' % (e['cod'], ex_))

    # ---------------- losa deportiva OC-06: losa, columnas y cubierta en arco
    L = D['losa']; x0, y0, x1, y1 = L['rect']
    try:
        piso([[[[x0, y0], [x1, y0], [x1, y1], [x0, y1]]]], F_LOSA, 0.12)
        for (x, y) in L['columnas']:
            columna(x, y, 0.36, 0.36, 0.12, L['h_col'], ACERO, 'OC-06 columna'); suma('columnas')
        rp = doc.Create.NewReferencePlane(P(x1, y0, 0), P(x0, y0, 0), XYZ.BasisZ, doc.ActiveView)
        ca = CurveArray()
        ca.Append(Arc.Create(P(x0, y0, L['h_col']), P(x1, y0, L['h_col']), P((x0 + x1) / 2, y0, L['h_col'] + L['flecha'])))
        doc.Regenerate()
        Lx = ft(y1 - y0)                                               # la extrusión va según la normal del plano: hacia +Y
        e0, e1 = (0.0, Lx) if rp.Normal.Y > 0 else (-Lx, 0.0)
        techo_arco = doc.Create.NewExtrusionRoof(ca, rp, NIV, R_CAL, e0, e1); suma('cubierta en arco')
        doc.Regenerate()
        bb = techo_arco.get_BoundingBox(None)                           # comprobación: debe quedar sobre la losa deportiva
        if bb is not None and (bb.Min.Y < ft(y0) - 1.0 or bb.Max.Y > ft(y1) + 1.0):
            ElementTransformUtils.MoveElement(doc, techo_arco.Id, XYZ(0, ft(y0) - bb.Min.Y, 0))
            nota('cubierta en arco reubicada sobre la losa deportiva')
    except Exception as ex_:
        nota('losa deportiva: %s' % ex_)

    # ---------------- pórtico de ingreso OE-01
    O = D['oe01']; gx0, gx1, yf, yb = O['gx0'], O['gx1'], O['yf'], O['yb']
    try:
        piso([[[[gx0 - 0.5, yf - 0.6], [gx1 + 0.5, yf - 0.6], [gx1 + 0.5, yb + 0.6], [gx0 - 0.5, yb + 0.6]]]], F_VER, 0.05)
        for (x, y) in O['columnas']:
            columna(x, y, 0.26, 0.40, 0.05, 4.18, TP1, 'OE-01 columna C-1'); suma('columnas')
        solido(gx0, yf, 4.18, gx1, yf + 0.4, 4.71, TP1, BuiltInCategory.OST_StructuralFraming, 'OE-01 viga VG-1')
        solido(gx0, yf + 0.05, 4.71, gx1, yf + 0.4, 5.09, TP2, BuiltInCategory.OST_GenericModel, 'OE-01 cielo CR-1')
        solido(gx0, yb - 0.4, 3.55, gx1, yb, 4.19, TP1, BuiltInCategory.OST_StructuralFraming, 'OE-01 viga posterior')
        muro(gx0 - 0.05, yf + 0.125, gx1 + 0.05, yf + 0.125, W_PARA, 5.09, 0.86)
        muro(gx0 - 0.05, yb - 0.10, gx1 + 0.05, yb - 0.10, W_PARA, 4.19, 0.60)
        for xx, s in ((gx0 + 0.1, 1), (gx1 - 0.1, -1)):
            muro_perfil([[xx, yf, 0.05], [xx, yb, 0.05], [xx, yb, 4.19], [xx, yf, 5.72]], W_LAT); suma('muros')
        m = O['m1']; solido(m[0], m[1], 0.05, m[2], m[3], 4.18, TP2, BuiltInCategory.OST_GenericModel, 'OE-01 muro M-1 (SS.HH.)')
        c = O['caseta']; solido(c[0], c[1], 0.05, c[2], c[3], 3.5, TP2, BuiltInCategory.OST_GenericModel, 'OE-01 caseta de vigilancia')
        techo_huella([gx0, yf + 0.3, gx1, yb - 0.2], 4.19, (5.72 - 4.19) / (yb - yf - 0.5), 'una', R_LOSA); suma('cubierta OE-01')
    except Exception as ex_:
        nota('OE-01: %s' % ex_)

    # ---------------- cerco perimétrico (muro TP-3, zócalo TP-2, columnas cada 3 m)
    for (xa, ya, xb, yb_) in D['cerco']:
        try:
            Lc = math.hypot(xb - xa, yb_ - ya)
            if Lc < 0.5: continue
            muro(xa, ya, xb, yb_, W_CERCO, 0.0, 2.43); muro(xa, ya, xb, yb_, W_ZOC, 0.0, 0.60); suma('tramos de cerco')
            nc = max(1, int(round(Lc / 3.0)))
            for k in range(nc + 1):
                t = float(k) / nc
                solido(xa + (xb - xa) * t - 0.14, ya + (yb_ - ya) * t - 0.14, 0.0, xa + (xb - xa) * t + 0.14, ya + (yb_ - ya) * t + 0.14, 2.5,
                       TP2, BuiltInCategory.OST_Columns, 'Columna de cerco')
        except Exception as ex_:
            nota('cerco: %s' % ex_)

    # ---------------- pisos exteriores
    Pz = D['pisos']
    suma('veredas', piso(Pz['veredas'], F_VER, 0.10)); suma('pavimento', piso(Pz['pavimento'], F_PAV, 0.08))
    suma('areas verdes', piso(Pz['verdes'], F_VERDE, 0.02)); suma('patio civico', piso(Pz['plaza'], F_ADOQ, 0.12))

    # ---------------- árboles (familia de vegetación RPC del proyecto)
    sims = [s for s in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Planting).OfClass(FamilySymbol).ToElements()]
    if sims:
        s = next((x for x in sims if 'tree' in (x.FamilyName + x.Name).lower() or 'arbol' in (x.FamilyName + x.Name).lower()), sims[0])
        if not s.IsActive: s.Activate()
        for (x, y) in D['arboles']:
            try: doc.Create.NewFamilyInstance(P(x, y, 0), s, NIV, StructuralType.NonStructural); suma('arboles')
            except Exception as ex_: nota('arbol: %s' % ex_)
    else:
        nota('No hay familia de vegetación cargada: Insertar > Cargar familia de Autodesk > Vegetación (RPC Tree) y volver a correr solo esta parte.')


TransactionManager.Instance.EnsureInTransaction(doc)
ERROR = None
try:
    _principal()
except Exception:
    ERROR = traceback.format_exc()
TransactionManager.Instance.TransactionTaskDone()
OUT = (['ERROR (copiar este texto):', ERROR] if ERROR else []) + ['%s: %d' % (k, v) for k, v in sorted(cuenta.items())] + ['--- avisos ---'] + LOG[:200]
'''


def guid():
    return uuid.uuid4().hex


codigo = 'DATOS_JSON = r\'\'\'' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + '\'\'\'\n' + CODIGO
open(os.path.join(SAL, 'DYNAMO_MODELO_NATIVO_HOGAR_REFUGIO.py'), 'w', encoding='utf-8').write(codigo)
id_py, id_in, id_out, id_b, id_bo = guid(), guid(), guid(), guid(), guid()
dyn = {
    "Uuid": str(uuid.uuid4()), "IsCustomNode": False, "Description": "Modelo nativo del Hogar de Refugio Temporal (CUI 2675514)",
    "Name": "DYNAMO_MODELO_NATIVO_HOGAR_REFUGIO", "ElementResolver": {"ResolutionMap": {}}, "Inputs": [], "Outputs": [],
    "Nodes": [
        {"ConcreteType": "CoreNodeModels.Input.BoolSelector, CoreNodeModels", "NodeType": "BooleanInputNode", "InputValue": True,
         "Id": id_b, "Inputs": [], "Outputs": [{"Id": id_bo, "Name": "", "Description": "Boolean", "UsingDefaultValue": False,
                                                 "Level": 2, "UseLevels": False, "KeepListStructure": False}],
         "Replication": "Disabled", "Description": "Selección entre verdadero y falso."},
        {"ConcreteType": "PythonNodeModels.PythonNode, PythonNodeModels", "Code": codigo, "Engine": "CPython3", "EngineName": "CPython3",
         "VariableInputPorts": True, "Id": id_py, "NodeType": "PythonScriptNode",
         "Inputs": [{"Id": id_in, "Name": "IN[0]", "Description": "Input #0", "UsingDefaultValue": False, "Level": 2,
                     "UseLevels": False, "KeepListStructure": False}],
         "Outputs": [{"Id": id_out, "Name": "OUT", "Description": "Result of the python script", "UsingDefaultValue": False,
                      "Level": 2, "UseLevels": False, "KeepListStructure": False}],
         "Replication": "Disabled", "Description": "Ejecuta un script de Python incrustado."}],
    "Connectors": [{"Start": id_bo, "End": id_in, "Id": guid(), "IsHidden": "False"}],
    "Dependencies": [], "NodeLibraryDependencies": [], "Bindings": [],
    "View": {"Dynamo": {"ScaleFactor": 1.0, "HasRunWithoutCrash": True, "IsVisibleInDynamoLibrary": True, "Version": "3.0.0.0",
                        "RunType": "Manual", "RunPeriod": "1000"},
             "Camera": {"Name": "Background Preview", "EyeX": -17.0, "EyeY": 24.0, "EyeZ": 50.0, "LookX": 12.0, "LookY": -13.0,
                        "LookZ": -58.0, "UpX": 0.0, "UpY": 1.0, "UpZ": 0.0},
             "NodeViews": [{"Id": id_b, "Name": "Boolean", "IsSetAsInput": False, "IsSetAsOutput": False, "Excluded": False,
                            "ShowGeometry": True, "X": 0.0, "Y": 0.0},
                           {"Id": id_py, "Name": "MODELO NATIVO HOGAR DE REFUGIO", "IsSetAsInput": False, "IsSetAsOutput": False,
                            "Excluded": False, "ShowGeometry": True, "X": 300.0, "Y": 0.0}],
             "Annotations": [], "X": 0.0, "Y": 0.0, "Zoom": 1.0}}
json.dump(dyn, open(os.path.join(SAL, 'DYNAMO_MODELO_NATIVO_HOGAR_REFUGIO.dyn'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('edificios', len(edificios), 'muros', sum(len(e['muros']) for e in edificios), 'puertas', sum(len(e['puertas']) for e in edificios),
      'ventanas', sum(len(e['ventanas']) for e in edificios), 'columnas', sum(len(e['columnas']) for e in edificios),
      'pisos', {k: len(v) for k, v in pisos.items()}, 'arboles', len(arboles), '->', SAL)
