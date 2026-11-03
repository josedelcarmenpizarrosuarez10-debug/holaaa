# -*- coding: utf-8 -*-
"""Genera el script de Dynamo que modela en Revit, con elementos nativos (familias de sistema y cargables), la arquitectura
del Hogar de Refugio Temporal (CUI 2675514) a partir de los mismos datos del modelo 3D (escena.json + medidas de escena.py):

  - materiales TP-1 (RGB 123-31-45), TP-2 (RGB 125-133-139), TP-3 (RAL 9010), concreto, calamina, área verde;
  - tipos de muro, piso y cubierta propios (prefijo "HR-");
  - E-01 a E-09: piso +0.15, muros TP-2 de 0.15 hasta +3.30, viga collar TP-1 +3.30 a +3.75, columnas TP-1 0.32 x 0.32 en las
    esquinas y cada ~3.6 m, hastiales TP-3 (muros de perfil), cubierta a dos aguas por huella (alero 1.50, pendiente 28 %),
    puertas y ventanas (familias del proyecto) en las mismas posiciones del render;
  - losa deportiva OC-06: losa, 14 columnas y cubierta en arco (cubierta por extrusión, flecha 4.20 sobre columnas de 6.00);
  - pórtico de ingreso OE-01: columnas C-1, viga VG-1, cielo CR-1, parapeto PL-2, muros laterales de perfil, muro M-1, caseta
    y losa inclinada (5.72 a 4.19);
  - cerco perimétrico de muro TP-3 de 2.40 con zócalo TP-2 y columnas cada 3 m (sin rejas);
  - veredas, pavimento de concreto con las áreas verdes como huecos, áreas verdes y patio cívico;
  - árboles del lote con la familia de vegetación (RPC) cargada en el proyecto.
Lo que no es arquitectura (red de drenaje, juegos, bancas OC-01, portones, letras, tanque, estacionamientos, cancha) va en el
IFC complementario (exporta_ifc.py --complemento) para vincularlo encima, en la misma posición (origen a origen).

Uso: python3.11 revit_nativo.py  ->  entregables/modelo_revit/DYNAMO_MODELO_NATIVO_HOGAR_REFUGIO.dyn y .py
"""
import json, math, os, uuid
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
D = json.load(open(os.path.join(AQUI, 'escena.json')))
SAL = os.path.join(RAIZ, 'entregables', 'modelo_revit'); os.makedirs(SAL, exist_ok=True)
VOL, H_MURO, Z_TECHO, PEND = 1.5, 3.3, 3.75, 0.28                  # mismas medidas de escena.py
r3 = lambda v: round(float(v), 3)

# ------------------------------------------------------------------ edificaciones (mismas reglas de escena.py)
edificios = []
for e in D['edificios']:
    x0, y0, x1, y1 = e['rect']; a0, b0, a1, b1 = x0 + VOL, y0 + VOL, x1 - VOL, y1 - VOL
    largo_x = e['cumbrera'] == 'y'
    lados, vanos, cols = [], [], []
    for k, (xa, ya, xb, yb, nrm) in enumerate(((a0, b0, a1, b0, (0, -1)), (a0, b1, a1, b1, (0, 1)),
                                               (a0, b0, a0, b1, (-1, 0)), (a1, b0, a1, b1, (1, 0)))):
        L = math.hypot(xb - xa, yb - ya); n = max(1, round(L / 3.6)); paso = L / n
        es_largo = (nrm[0] != 0) == largo_x
        lados.append([r3(xa), r3(ya), r3(xb), r3(yb), nrm[0], nrm[1]])
        for i in range(n + 1):
            t = i / n; cols.append([r3(xa + (xb - xa) * t), r3(ya + (yb - ya) * t)])
        for i in range(n):
            t = (i + 0.5) / n; cx, cy = xa + (xb - xa) * t, ya + (yb - ya) * t
            if es_largo:
                if i % 3 == 1 and L > 8:
                    vanos.append(dict(lado=k, x=r3(cx), y=r3(cy), tipo='puerta', ancho=1.0, alto=2.15, alf=0.15))
                else:
                    vanos.append(dict(lado=k, x=r3(cx), y=r3(cy), tipo='ventana', ancho=r3(paso * 0.58), alto=1.35, alf=1.05))
            else:
                if i == n // 2:
                    vid = e['cod'] in ('E-01', 'E-05')
                    vanos.append(dict(lado=k, x=r3(cx), y=r3(cy), tipo='puerta', ancho=1.8 if vid else 1.0, alto=2.35, alf=0.15,
                                      vidrio=vid))
                else:
                    vanos.append(dict(lado=k, x=r3(cx), y=r3(cy), tipo='ventana', ancho=r3(paso * 0.5), alto=1.35, alf=1.05))
    cols = [list(c) for c in {tuple(c) for c in cols}]
    if largo_x:
        semi = (a1 - a0) / 2; zr = Z_TECHO + PEND * semi
        hast = [[[r3(a0), r3(b), Z_TECHO], [r3((x0 + x1) / 2), r3(b), r3(zr)], [r3(a1), r3(b), Z_TECHO]] for b in (b0, b1)]
    else:
        semi = (b1 - b0) / 2; zr = Z_TECHO + PEND * semi
        hast = [[[r3(a), r3(b0), Z_TECHO], [r3(a), r3((y0 + y1) / 2), r3(zr)], [r3(a), r3(b1), Z_TECHO]] for a in (a0, a1)]
    edificios.append(dict(cod=e['cod'], nombre=e.get('nombre', ''), techo=[r3(x0), r3(y0), r3(x1), r3(y1)], cumbrera=e['cumbrera'],
                          muro=[r3(a0), r3(b0), r3(a1), r3(b1)], piso=[r3(a0 - 1.2), r3(b0 - 1.2), r3(a1 + 1.2), r3(b1 + 1.2)],
                          lados=lados, vanos=vanos, columnas=cols, hastiales=hast, alero=r3(Z_TECHO - PEND * VOL)))

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
DATOS = dict(edificios=edificios, losa=losa, oe01=oe01, cerco=cerco, pisos=pisos, arboles=arboles,
             medidas=dict(VOL=VOL, H_MURO=H_MURO, Z_TECHO=Z_TECHO, PEND=PEND))

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

doc = DocumentManager.Instance.CurrentDBDocument
D = json.loads(DATOS_JSON)
M = D['medidas']
FT = 1 / 0.3048
LOG = []
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
    ex = [t for t in FilteredElementCollector(doc).OfClass(clase).ToElements() if t.Name == nombre]
    if ex: return ex[0]
    bases = [t for t in FilteredElementCollector(doc).OfClass(clase).ToElements()
             if (clase != WallType or t.Kind == WallKind.Basic) and t.GetCompoundStructure() is not None]
    t = doc.GetElement(bases[0].Duplicate(nombre).Id)
    cs = CompoundStructure.CreateSingleLayerCompoundStructure(funcion, ft(ancho), mat)
    t.SetCompoundStructure(cs)
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
        a = P(*pts[i]); b = P(*pts[(i + 1) % len(pts)]); c.Add(Line.CreateBound(a, b))
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

cuenta = {}
def suma(k, n=1): cuenta[k] = cuenta.get(k, 0) + n

# ---------------- edificaciones E-01 a E-09
S_PUERTA = {}; S_VENT = {}
for e in D['edificios']:
    try:
        a0, b0, a1, b1 = e['muro']; t = 0.075
        piso([[[[x, y] for x, y in ((e['piso'][0], e['piso'][1]), (e['piso'][2], e['piso'][1]), (e['piso'][2], e['piso'][3]), (e['piso'][0], e['piso'][3]))]]], F_PISO, 0.15)
        muros = []
        for (xa, ya, xb, yb, nx, ny) in e['lados']:                    # eje del muro 0.075 hacia adentro de la cara exterior
            w = muro(xa - nx * t, ya - ny * t, xb - nx * t, yb - ny * t, W_TP2, 0.15, M['H_MURO'] - 0.15); muros.append(w); suma('muros')
            muro(xa - nx * 0.115, ya - ny * 0.115, xb - nx * 0.115, yb - ny * 0.115, W_VIGA, M['H_MURO'], M['Z_TECHO'] - M['H_MURO']); suma('vigas collar')
        for h in e['hastiales']:
            try: muro_perfil(h, W_HAST); suma('hastiales')
            except Exception as ex_: nota('%s hastial: %s' % (e['cod'], ex_))
        cols = []
        for (x, y) in e['columnas']:
            cols.append(columna(x, y, 0.32, 0.32, 0.15, M['H_MURO'], TP1, e['cod'] + ' columna TP-1')); suma('columnas')
        doc.Regenerate()
        for c in cols:                                                 # la columna queda en TP-1 (no toma el material del muro)
            for w in muros:
                try:
                    if JoinGeometryUtils.AreElementsJoined(doc, c, w): JoinGeometryUtils.UnjoinGeometry(doc, c, w)
                except Exception: pass
        for v in e['vanos']:
            try:
                w = muros[v['lado']]
                if v['tipo'] == 'puerta':
                    k = (v['ancho'], v['alto'], v.get('vidrio', False))
                    if k not in S_PUERTA:
                        S_PUERTA[k] = simbolo(BuiltInCategory.OST_Doors, ('double glass', 'doble', 'glass') if k[2] else ('single-flush', 'single', 'simple'),
                                              'HR-Puerta %.2fx%.2f%s' % (k[0], k[1], ' vidrio' if k[2] else ''),
                                              [(k[0], ['Width', 'Ancho'], [BuiltInParameter.DOOR_WIDTH, BuiltInParameter.FAMILY_WIDTH_PARAM]),
                                               (k[1], ['Height', 'Altura'], [BuiltInParameter.DOOR_HEIGHT, BuiltInParameter.FAMILY_HEIGHT_PARAM])])
                    s = S_PUERTA[k]
                else:
                    k = (v['ancho'], v['alto'])
                    if k not in S_VENT:
                        S_VENT[k] = simbolo(BuiltInCategory.OST_Windows, ('sliding', 'corrediza', 'fixed', 'fija'), 'HR-Ventana %.2fx%.2f' % k,
                                            [(k[0], ['Width', 'Ancho'], [BuiltInParameter.WINDOW_WIDTH, BuiltInParameter.FAMILY_WIDTH_PARAM]),
                                             (k[1], ['Height', 'Altura'], [BuiltInParameter.WINDOW_HEIGHT, BuiltInParameter.FAMILY_HEIGHT_PARAM])])
                    s = S_VENT[k]
                if s is None: nota('sin familia de %s cargada' % v['tipo']); continue
                nx, ny = e['lados'][v['lado']][4], e['lados'][v['lado']][5]
                fi = doc.Create.NewFamilyInstance(P(v['x'] - nx * 0.075, v['y'] - ny * 0.075, 0), s, w, NIV, StructuralType.NonStructural)
                pa = fi.get_Parameter(BuiltInParameter.INSTANCE_SILL_HEIGHT_PARAM)
                if pa is not None and not pa.IsReadOnly: pa.Set(ft(v['alf']))
                suma(v['tipo'] + 's')
            except Exception as ex_:
                nota('%s %s: %s' % (e['cod'], v['tipo'], ex_))
        techo_huella(e['techo'], e['alero'], M['PEND'], e['cumbrera'], R_CAL); suma('cubiertas a dos aguas')
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
    doc.Create.NewExtrusionRoof(ca, rp, NIV, R_CAL, 0.0, ft(y1 - y0)); suma('cubierta en arco')
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

TransactionManager.Instance.TransactionTaskDone()
OUT = ['%s: %d' % (k, v) for k, v in sorted(cuenta.items())] + ['--- avisos ---'] + LOG[:200]
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
print('edificios', len(edificios), 'vanos', sum(len(e['vanos']) for e in edificios), 'columnas', sum(len(e['columnas']) for e in edificios),
      'pisos', {k: len(v) for k, v in pisos.items()}, 'arboles', len(arboles), '->', SAL)
