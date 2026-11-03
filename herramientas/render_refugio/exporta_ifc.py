# -*- coding: utf-8 -*-
"""Exporta el modelo 3D del Hogar de Refugio Temporal (CUI 2675514) a IFC4 para abrirlo o vincularlo en Revit.

Toma refugio.blend (escena.py) tal como se renderiza: edificaciones E-01 a E-09, pórtico OE-01, cerco, losa deportiva,
patio cívico, juegos OC-04, bancas OC-01, tanque elevado, estacionamientos, pisos y áreas verdes, y toda la red de drenaje
(cunetas con rejilla, sumideros, tapas de inspección, canaletas, montantes, colector frontal con sus tapas).
Cada objeto sale como un elemento IFC con su categoría (IfcWall, IfcColumn, IfcBeam, IfcSlab, IfcRoof, IfcDoor, IfcWindow,
IfcPipeSegment, IfcFurnishingElement, ...), su color y el grupo de la escena (edificación u obra) en el Pset_HogarRefugio.
No se exportan la vegetación del entorno, el pasto en 3D ni el cielo; los árboles del lote salen como tronco y copa simples.
Coordenadas en metros, origen local = E 349 090, N 9 281 900 (UTM WGS 84 zona 18 S), con IfcMapConversion.

Esquema: IFC2X3 por defecto (sólidos IfcFacetedBrep; Revit lo abre con Abrir IFC y lo muestra sombreado y realista);
con --ifc4 sale en IFC4 con mallas IfcTriangulatedFaceSet. En la rejilla de las cunetas se exporta una platina de cada cuatro
(@ 0.10 m en vez de @ 0.025 m) para que el archivo sea manejable en Revit.

Uso: python3.11 exporta_ifc.py [refugio.blend] [salida.ifc] [--ifc4]
"""
import math, os, re, sys, time
import bpy
import bmesh  # noqa: E402  (después de bpy)
import ifcopenshell, ifcopenshell.guid
from mathutils import Matrix, Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
IFC4 = '--ifc4' in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
BLEND = ARGS[0] if len(ARGS) > 0 else os.path.join(AQUI, 'refugio.blend')
SALIDA = ARGS[1] if len(ARGS) > 1 else os.path.join(AQUI, 'HOGAR_REFUGIO_MODELO_3D.ifc')
E0, N0 = 349090.0, 9281900.0
LOTE = (-3.0, 5.0, 76.0, 135.0)                         # caja de exportación (lote, calle y vereda exterior)

# ------------------------------------------------------------------ clasificación por nombre de objeto
REGLAS = [  # (prefijos o textos, clase IFC, tipo predefinido, nombre de categoría)
    (('montante', 'oc01_bajada'), 'IfcPipeSegment', 'RIGIDSEGMENT', 'Montante PVC 4"'),
    (('_canaleta', 'oc01_canaleta'), 'IfcPipeSegment', 'GUTTER', 'Canaleta'),
    (('cunetas_muros', 'cunetas_fondo', 'cuneta_'), 'IfcPipeSegment', 'GUTTER', 'Cuneta de concreto b=0.40'),
    (('rejillas_cunetas',), 'IfcPipeFitting', 'NOTDEFINED', 'Rejilla metálica de cuneta y sumidero'),
    (('sumidero',), 'IfcWasteTerminal', 'GULLYTRAP', 'Sumidero con rejilla'),
    (('tapa_insp',), 'IfcDistributionChamberElement', 'INSPECTIONCHAMBER', 'Tapa de inspección'),
    (('tapa_ciega', 'tapa_junta', 'tapa_asa'), 'IfcDistributionChamberElement', 'INSPECTIONCHAMBER', 'Tapa ciega de registro del colector'),
    (('colector_losa', 'junta_colector', 'junta_losa'), 'IfcPipeSegment', 'CULVERT', 'Colector frontal b=0.80 (losa-vereda)'),
    (('falsa_columna', 'oc01_falsa'), 'IfcColumn', 'COLUMN', 'Falsa columna'),
    (('_hastial', 'oe01_lateral', 'oe01_muro', 'oe01_parapeto', '_muro', 'cerco_muro', 'cerco_zocalo', 'cerco_remate',
      '_zocalo', 'oe01_zocalo', 'oe01_caseta', 'jardinera'), 'IfcWall', 'NOTDEFINED', 'Muro'),
    (('_col', 'columna', 'oe01_col', 'oc01_columna', 'tanque_col', 'poste_', 'columna_losa'), 'IfcColumn', 'COLUMN', 'Columna'),
    (('_viga', 'viga', 'oc01_correa', 'travesano', 'diag', 'arco', 'tanque_viga', 'oe01_cielo'), 'IfcBeam', 'BEAM', 'Viga'),
    (('_techo', 'techo_', 'cubierta_losa', 'oc01_cobertura', 'oe01_techo', '_cumbrera', 'tobogan_techo'), 'IfcRoof', 'NOTDEFINED', 'Cobertura'),
    (('puerta', 'oe01_porton', 'oe01_puerta'), 'IfcDoor', 'DOOR', 'Puerta / portón'),
    (('ventana', 'oe01_ventana', 'oe01_celosia'), 'IfcWindow', 'WINDOW', 'Ventana / paño metálico'),
    (('_piso', 'losa', 'pavimento', 'vereda', 'plaza_piso', 'juegos_arena', 'juegos_sardinel', 'asta_base', 'oe01_piso',
      'sardinel', 'jardinera_tierra', 'tanque_losa'), 'IfcSlab', 'FLOOR', 'Piso / losa'),
    (('pasto_',), 'IfcGeographicElement', 'TERRAIN', 'Área verde'),
    (('banca', 'oc01_asiento', 'oc01_celosia', 'oc01_pata', 'columpio', 'tobogan', 'resbaladera', 'peldano', 'baranda',
      'balancin', 'cadena'), 'IfcFurnishingElement', 'NOTDEFINED', 'Mobiliario exterior / juegos'),
    (('linea', 'pista', 'cancha', 'area', 'tablero', 'poste_basquet', 'brazo', 'poste_arco'), 'IfcBuildingElementProxy', 'NOTDEFINED', 'Losa deportiva y vía'),
    (('letrero',), 'IfcBuildingElementProxy', 'NOTDEFINED', 'Letras "HOGAR DE REFUGIO TEMPORAL"'),
    (('bandera', 'asta'), 'IfcBuildingElementProxy', 'NOTDEFINED', 'Asta de banderas'),
    (('arbol',), 'IfcGeographicElement', 'NOTDEFINED', 'Árbol'),
]


def clasifica(nombre):
    n = nombre.lower().split('.')[0]
    if n.startswith('pasto_'):                                    # áreas verdes (también la de las jardineras OC-01)
        return 'IfcGeographicElement', 'TERRAIN', 'Área verde'
    if re.search(r'_(v|vt|vg)\d+_(vid|m|alf)$', n):                 # ventanas de las edificaciones: vidrio, marco y alféizar
        return 'IfcWindow', 'WINDOW', 'Ventana'
    if re.search(r'_(p\d+|pp)(_marco)?$', n):                       # puertas de las edificaciones
        return 'IfcDoor', 'DOOR', 'Puerta'
    for claves, clase, tipo, cat in REGLAS:
        for c in claves:
            if (c.startswith('_') and c in n) or n.startswith(c) or (len(c) > 5 and c in n):
                return clase, tipo, cat
    return 'IfcBuildingElementProxy', 'NOTDEFINED', 'Elemento'


def a_srgb(c):
    return max(0.0, min(1.0, 1.055 * c ** (1 / 2.4) - 0.055 if c > 0.0031308 else 12.92 * c))


COLOR_TABLA = {  # materiales con textura procedural: color representativo (RGB 0-255)
    'TP1': (123, 31, 45), 'TP2': (125, 133, 139), 'TP3': (241, 236, 225), 'pavimento': (186, 182, 174), 'vereda': (190, 186, 178),
    'concreto': (178, 176, 170), 'concreto_gris': (150, 150, 148), 'concreto_cuneta': (196, 194, 188), 'cuneta_fondo': (34, 34, 33),
    'tapa_concreto': (112, 110, 104), 'tapa_inspeccion': (150, 148, 142), 'arena': (198, 168, 120), 'asfalto': (52, 52, 54),
    'calamina_x': (196, 200, 204), 'calamina_y': (196, 200, 204), 'adoquin': (150, 92, 74), 'pasto': (88, 128, 58),
    'tierra_jardinera': (92, 70, 50), 'plancha_metalica': (58, 60, 63), 'hojas1': (60, 100, 40),
}


def color_material(m):
    if m is None:
        return (0.7, 0.7, 0.7)
    base = m.name.split('.')[0]
    if base in COLOR_TABLA:
        return tuple(v / 255 for v in COLOR_TABLA[base])
    try:
        p = m.node_tree.nodes['Principled BSDF']; bc = p.inputs['Base Color']
        if not bc.is_linked:
            return tuple(a_srgb(v) for v in bc.default_value[:3])
    except (AttributeError, KeyError):
        pass
    return (0.7, 0.7, 0.7)


# ------------------------------------------------------------------ IFC: proyecto, sitio, edificio, nivel
f = ifcopenshell.file(schema='IFC4' if IFC4 else 'IFC2X3')
G = lambda: ifcopenshell.guid.new()
CLASE_2X3 = {'IfcPipeSegment': 'IfcFlowSegment', 'IfcPipeFitting': 'IfcFlowFitting', 'IfcWasteTerminal': 'IfcFlowTerminal',
             'IfcGeographicElement': 'IfcBuildingElementProxy'}
if IFC4:
    OH = None
else:                                                            # IFC2X3: historial de propietario obligatorio (sin nombres)
    _per = f.createIfcPerson(None, '-', None, None, None, None, None, None)
    _org = f.createIfcOrganization(None, 'Hogar de Refugio Temporal - CUI 2675514', None, None, None)
    _po = f.createIfcPersonAndOrganization(_per, _org, None)
    _app = f.createIfcApplication(_org, '1.0', 'Modelo 3D Hogar de Refugio', 'HR3D')
    OH = f.createIfcOwnerHistory(_po, _app, None, 'ADDED', None, None, None, int(time.time()))
pt = lambda *c: f.createIfcCartesianPoint([float(x) for x in c])
dr = lambda *c: f.createIfcDirection([float(x) for x in c])
ejes = f.createIfcAxis2Placement3D(pt(0, 0, 0), dr(0, 0, 1), dr(1, 0, 0))
ctx = f.createIfcGeometricRepresentationContext(None, 'Model', 3, 1.0e-5, ejes, None)
cuerpo = f.createIfcGeometricRepresentationSubContext('Body', 'Model', None, None, None, None, ctx, None, 'MODEL_VIEW', None)
unidades = f.createIfcUnitAssignment([f.createIfcSIUnit(None, 'LENGTHUNIT', None, 'METRE'),
                                      f.createIfcSIUnit(None, 'AREAUNIT', None, 'SQUARE_METRE'),
                                      f.createIfcSIUnit(None, 'VOLUMEUNIT', None, 'CUBIC_METRE'),
                                      f.createIfcSIUnit(None, 'PLANEANGLEUNIT', None, 'RADIAN')])
proyecto = f.createIfcProject(G(), OH, 'Hogar de Refugio Temporal "Mujeres Violentadas" - CUI 2675514', None, None, None, None, [ctx], unidades)
if IFC4:
    crs = f.createIfcProjectedCRS('EPSG:32718', 'WGS 84 / UTM zona 18S', 'WGS84', None, None, '18S', None)
    f.createIfcMapConversion(ctx, crs, E0, N0, 0.0, 1.0, 0.0, 1.0)
lp0 = f.createIfcLocalPlacement(None, ejes)
sitio = f.createIfcSite(G(), OH, 'Predio Los Mangos - Morales, San Martín', None, None, lp0, None, None, 'ELEMENT', None, None, None, None, None)
lp1 = f.createIfcLocalPlacement(lp0, f.createIfcAxis2Placement3D(pt(0, 0, 0), None, None))
edif = f.createIfcBuilding(G(), OH, 'Hogar de Refugio Temporal', None, None, lp1, None, None, 'ELEMENT', None, None, None)
lp2 = f.createIfcLocalPlacement(lp1, f.createIfcAxis2Placement3D(pt(0, 0, 0), None, None))
nivel = f.createIfcBuildingStorey(G(), OH, 'NIVEL 1 (NPT +0.00)', None, None, lp2, None, None, 'ELEMENT', 0.0)
f.createIfcRelAggregates(G(), OH, None, None, proyecto, [sitio])
f.createIfcRelAggregates(G(), OH, None, None, sitio, [edif])
f.createIfcRelAggregates(G(), OH, None, None, edif, [nivel])
ESTILOS = {}


def estilo(m):
    clave = m.name if m else '_sin'
    if clave not in ESTILOS:
        r, g, b = color_material(m)
        rend = f.createIfcSurfaceStyleRendering(f.createIfcColourRgb(None, r, g, b), 0.0, None, None, None, None, None, None, 'FLAT')
        ESTILOS[clave] = f.createIfcSurfaceStyle(clave.split('.')[0], 'BOTH', [rend])
    return ESTILOS[clave]


ELEMENTOS, CUENTA, PORGRUPO = [], {}, {}


def agrega(nombre, grupo, verts, caras, mat):
    """caras: polígonos (índices de verts); en IFC4 se triangulan en abanico, en IFC2X3 van como caras de un IfcFacetedBrep."""
    if not caras:
        return
    clase, tipo, cat = clasifica(nombre)
    if IFC4:
        tris = [(c[0], c[k], c[k + 1]) for c in caras for k in range(1, len(c) - 1)]
        pl = f.createIfcCartesianPointList3D([tuple(round(c, 4) for c in v) for v in verts])
        geo = f.createIfcTriangulatedFaceSet(pl, None, None, [tuple(i + 1 for i in t) for t in tris], None)
        f.createIfcStyledItem(geo, [estilo(mat)], None)
        rep = f.createIfcShapeRepresentation(cuerpo, 'Body', 'Tessellation', [geo])
    else:
        clase = CLASE_2X3.get(clase, clase)
        P = [f.createIfcCartesianPoint([round(c, 4) for c in v]) for v in verts]
        caras_ifc = [f.createIfcFace([f.createIfcFaceOuterBound(f.createIfcPolyLoop([P[i] for i in c]), True)])
                     for c in caras if len(set(c)) >= 3]
        geo = f.createIfcFacetedBrep(f.createIfcClosedShell(caras_ifc))
        f.createIfcStyledItem(geo, [f.createIfcPresentationStyleAssignment([estilo(mat)])], None)
        rep = f.createIfcShapeRepresentation(cuerpo, 'Body', 'Brep', [geo])
    prod = f.createIfcProductDefinitionShape(None, None, [rep])
    lp = f.createIfcLocalPlacement(lp2, f.createIfcAxis2Placement3D(pt(0, 0, 0), None, None))
    kw = dict(GlobalId=G(), OwnerHistory=OH, Name=nombre.split('.')[0], ObjectType=cat, ObjectPlacement=lp, Representation=prod)
    if clase == 'IfcRoof' and not IFC4:
        kw['ShapeType'] = 'NOTDEFINED'
    e = f.create_entity(clase, **kw)
    try:
        e.PredefinedType = tipo
    except Exception:
        pass
    props = [f.createIfcPropertySingleValue('Grupo', None, f.createIfcLabel(grupo), None),
             f.createIfcPropertySingleValue('Categoria', None, f.createIfcLabel(cat), None),
             f.createIfcPropertySingleValue('Material', None, f.createIfcLabel((mat.name if mat else '-').split('.')[0]), None)]
    ps = f.createIfcPropertySet(G(), OH, 'Pset_HogarRefugio', None, props)
    f.createIfcRelDefinesByProperties(G(), OH, None, None, [e], ps)
    ELEMENTOS.append(e); CUENTA[clase] = CUENTA.get(clase, 0) + 1
    PORGRUPO.setdefault(grupo, []).append(e)


def dentro(verts):
    xs = [v[0] for v in verts]; ys = [v[1] for v in verts]
    return min(xs) > LOTE[0] - 1 and max(xs) < LOTE[2] + 1 and min(ys) > LOTE[1] - 1 and max(ys) < LOTE[3] + 1


def recorta(verts, tris):
    """Calle y veredas exteriores: se recortan a la caja del lote."""
    vs = [(min(max(x, LOTE[0]), LOTE[2]), y, z) for x, y, z in verts]
    return vs, tris


# ------------------------------------------------------------------ recorrido de la escena evaluada
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=BLEND)
dg = bpy.context.evaluated_depsgraph_get()
FUERA = ('Arboles', 'Prototipos (fuera del terreno)', 'Personas')         # del 'Pasto' solo salen las áreas (no las matas)
ARBOLES = []


def grupo_de(o):
    cols = [c.name for c in o.users_collection]
    return cols[0] if cols else 'Escena'


for inst in dg.object_instances:
    ob = inst.instance_object if inst.is_instance else inst.object
    orig = ob.original if hasattr(ob, 'original') else ob
    if inst.is_instance:
        par = inst.parent.original if inst.parent else None
        if par is not None and par.name.startswith('arbol'):
            if par.name not in [a[0] for a in ARBOLES]:
                ARBOLES.append((par.name, tuple(par.location), par.scale[0]))
        continue                                                  # pasto, hojas, personas: no se exportan
    if ob.type not in ('MESH', 'FONT', 'CURVE'):
        continue
    if any(c.name in FUERA for c in orig.users_collection) or orig.name in ('suelo', 'hoja', 'mata_pasto') or not orig.visible_get():
        continue
    if orig.hide_render:
        continue
    try:
        me = ob.to_mesh()
    except RuntimeError:
        continue
    if me is None or not len(me.polygons):
        ob.to_mesh_clear(); continue
    M = inst.matrix_world.copy()
    bm = bmesh.new(); bm.from_mesh(me)
    if any(ed.is_boundary for ed in bm.edges):                    # superficie abierta: se le da espesor (sólido cerrado para Revit)
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.02)
        bm.to_mesh(me); me.update()
    bm.free()
    verts = [tuple(M @ v.co) for v in me.vertices]
    polis = list(me.polygons)
    if orig.name.startswith('rejillas_cunetas'):                  # una platina de cada cuatro (cajas de 6 caras)
        largo = lambda q: max(max(verts[i][k] for i in q.vertices) - min(verts[i][k] for i in q.vertices) for k in (0, 1))
        polis = [q for q in polis if (q.index // 6) % 4 == 0 or largo(q) > 0.6]
    tris = [tuple(q.vertices) for q in polis]
    mats = list(me.materials)
    nombre = orig.name
    if nombre.startswith(('pista', 'vereda_ext', 'vereda_otra', 'sardinel', 'linea_carril')):
        verts, tris = recorta(verts, tris)
        if nombre.startswith('linea_carril') and not dentro(verts):
            ob.to_mesh_clear(); continue
    elif not dentro(verts):
        ob.to_mesh_clear(); continue
    if len(mats) > 1:                                             # un elemento por material
        por = {}
        for q in polis:
            por.setdefault(q.material_index, []).append(tuple(q.vertices))
        for k, tt in por.items():
            usados = sorted({i for t in tt for i in t}); ix = {v: i for i, v in enumerate(usados)}
            agrega(nombre, grupo_de(orig), [verts[i] for i in usados], [tuple(ix[i] for i in t) for t in tt], mats[k] if k < len(mats) else None)
    else:
        agrega(nombre, grupo_de(orig), verts, tris, mats[0] if mats else None)
    ob.to_mesh_clear()

# árboles del lote: tronco y copa simples (la vegetación del entorno no se exporta)
mt = bpy.data.materials.get('tronco'); mh = bpy.data.materials.get('hojas1')
for nom, (x, y, z), s in ARBOLES:
    if not (LOTE[0] < x < LOTE[2] and 17.5 < y < LOTE[3]):
        continue
    h = 2.4 * s; rt = 0.16 * s; n = 10
    vt = [(x + rt * math.cos(2 * math.pi * k / n), y + rt * math.sin(2 * math.pi * k / n), z + zz) for zz in (0, h) for k in range(n)]
    tt = [(k, (k + 1) % n, n + (k + 1) % n) for k in range(n)] + [(k, n + (k + 1) % n, n + k) for k in range(n)]
    agrega('arbol_tronco', 'Arboles', vt, tt, mt)
    rc = 2.3 * s; zc = z + h + rc * 0.75; vs, ts = [], []
    nl, nm = 8, 12
    for i in range(nl + 1):
        th = math.pi * i / nl
        for j in range(nm):
            ph = 2 * math.pi * j / nm
            vs.append((x + rc * math.sin(th) * math.cos(ph), y + rc * math.sin(th) * math.sin(ph), zc + rc * 0.85 * math.cos(th)))
    for i in range(nl):
        for j in range(nm):
            a, b, c, d = i * nm + j, i * nm + (j + 1) % nm, (i + 1) * nm + (j + 1) % nm, (i + 1) * nm + j
            ts += [(a, b, c), (a, c, d)]
    agrega('arbol_copa', 'Arboles', vs, ts, mh)

f.createIfcRelContainedInSpatialStructure(G(), OH, None, None, ELEMENTOS, nivel)
for g, els in PORGRUPO.items():                                    # grupos por edificación u obra
    gr = f.createIfcGroup(G(), OH, g, None, None)
    f.createIfcRelAssignsToGroup(G(), OH, None, None, els, None, gr)
f.write(SALIDA)
print('elementos', len(ELEMENTOS), CUENTA, 'grupos', len(PORGRUPO), 'tiempo', round(time.time() - t0), 's', '->', SALIDA,
      round(os.path.getsize(SALIDA) / 1e6, 1), 'MB')
