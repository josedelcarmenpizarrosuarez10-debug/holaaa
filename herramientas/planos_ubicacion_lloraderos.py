"""Lamina DL-00: PLANTA DE UBICACION DE LLORADEROS en cunetas colindantes con area verde.
  refugio: Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514)
  varones: CAR Varones (CUI 2705619)

Fondo: planta general de arquitectura del proyecto en gris, con la red de cunetas en azul y las areas verdes en verde.
Encima: los tramos de muro de cuneta colindantes con area verde (los de la hoja METRADO LLORADEROS de la planilla), numerados
igual que en la hoja, y cada lloradero en su posicion (@1.50 m, repartidos en el tramo), con el cuadro de tramos, la leyenda y
las notas. Escala real (1 unidad = 1 m), lamina A1 a 1/250.
Datos: ejes de las cunetas con su progresiva 0+000 (insumos/solange/EJES_CUNETAS_REFUGIO.json, insumos/katiuska/EJES_CUNETAS_VARONES.json)
y tramos de la hoja METRADO LLORADEROS (valores guardados en la planilla vigente). Lado del muro: tabla LADO (refugio) o, si no
hay tabla, el rumbo de la hoja (ESTE/OESTE/NORTE/SUR) comparado con la normal al eje (varones; la planta esta con el norte arriba).
Uso: python3 herramientas/planos_ubicacion_lloraderos.py [refugio|varones]
"""
import os, sys, json, math, zipfile, tempfile, warnings
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI); sys.path.insert(0, AQUI)
import numpy as np
import ezdxf, openpyxl
from ezdxf.addons import Importer
from ezdxf.enums import TextEntityAlignment as TA
import dxf_base as B, dxf_layouts as L, diseno as dz
from ezdxf import bbox

ESC = 250
I = lambda *a: os.path.join(RAIZ, "insumos", *a)
PROY = {
    "refugio": dict(
        zip=I("solange", "PLANTA_GENERAL_REFUGIO_FINAL_03-10-2026_dxf.zip"), ejes=I("solange", "EJES_CUNETAS_REFUGIO.json"),
        plan=I("metrados_vigentes", "METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx"),
        sal=os.path.join(RAIZ, "entregables", "PLANO_DL-00_UBICACION_LLORADEROS_HOGAR_REFUGIO.dxf"),
        ext=(349085.0, 9281912.0, 349168.0, 9282036.0),      # planta del predio (coordenadas locales del plano de arquitectura)
        # lado de cada tramo respecto al sentido de la progresiva del eje (+1 izquierda, -1 derecha), del levantamiento de la planta
        lado={("01", "ESTE"): 1, ("01", "OESTE"): -1, ("02", "SUR"): 1, ("07", "SUR"): 1, ("07", "ESTE"): 1, ("07", "OESTE"): -1,
              ("09", "SUR"): 1, ("11", "ESTE"): 1, ("11", "OESTE"): -1, ("12", "ESTE"): 1, ("12", "OESTE"): -1},
        verdes={"HIERVA"}, verdes_bloques=False, red_bloques={"red drenaje"}, red_capas=set(), ejes_txt="01 a 12",
        nombre="Hogar de Refugio Temporal - CUI 2675514", proyecto=None, ubicacion=None, panel=400, fila=5.2, cad=False),
    "varones": dict(
        zip=I("katiuska", "PLANTA_GENERAL_CAR_VARONES.zip"), ejes=I("katiuska", "EJES_CUNETAS_VARONES.json"),
        plan=I("metrados_vigentes", "METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx"),
        sal=os.path.join(RAIZ, "entregables_varones", "PLANO_DL-00_UBICACION_LLORADEROS_CAR_VARONES.dxf"),
        ext=(349713.0, 9282556.0, 349815.0, 9282681.0), lado=None,
        verdes={"HIERVA", "Area Verde", "Hatch Jardin"}, verdes_bloques=True,
        red_bloques={"RED DE DRENAJE 01", "drenaje 01", "drenaje"}, red_capas={"CUNETAS"}, ejes_txt="01 a 09",
        nombre="CAR Varones - CUI 2705619",
        proyecto=("CREACION DEL SERVICIO DE PROTECCION INTEGRAL A NINAS, NINOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE PERDERLOS",
                  "EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2705619"),
        ubicacion="UBICACION: PREDIO ALDEA INFANTIL VIRGEN DEL PILAR - MORALES - SAN MARTIN - SAN MARTIN", panel=None, fila=4.6, cad=True),
}
CFG = PROY["refugio"]
RUMBO = {"ESTE": (1, 0), "OESTE": (-1, 0), "NORTE": (0, 1), "SUR": (0, -1)}
OFS = 0.55                                                   # distancia del eje a la cara exterior del muro (cuneta tipica)
CAPAS = [("ARQ-FONDO", 253, "CONTINUOUS", 9), ("CUNETAS-RED", 5, "CONTINUOUS", 18), ("AREA-VERDE", 3, "CONTINUOUS", 9),
         ("LLORAD-TRAMO", 1, "CONTINUOUS", 70), ("LLORAD-SIMB", 1, "CONTINUOUS", 25), ("LLORAD-TEXTO", 1, "CONTINUOUS", 25),
         ("EJE-TEXTO", 5, "CONTINUOUS", 25)]
EXCL_LAYERS = {"cotas", "Lineas", "LCOTAS", "Z-DIM", "GRID_TEXT", "ANNOTATION", "ANNOTATION_TABLE", "TEX", "TEXTO", "TEXTO AMBIENTES",
               "Areas", "A-TEXTO-04", "13.-ALE_PRESENTACION", "0_COTAS 1", "PISO Cemento pulido", "Lpiso det_PD", "0_COLUMNA ACHURADO"}
EXCL_TIPOS = {"DIMENSION", "LEADER", "TEXT", "MTEXT"}
EXCL_BLOQUES = ("topooooo", "Cotas de elev", "TEXTO 2", "A$C", "CAMA", "LINEA SUSPEN", "VEHICULO", "punto.ecologico")


def tramos():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ws = openpyxl.load_workbook(CFG["plan"], data_only=True)["METRADO LLORADEROS"]
    out = []
    r = 6
    while isinstance(ws["A%d" % (r + 1)].value, (int, float)):
        r += 1
        eje = str(ws["B%d" % r].value).split()[-1].zfill(2); p0, p1 = [float(v) for v in str(ws["C%d" % r].value).replace("0+", "").split(" a ")]
        out.append(dict(n=int(ws["A%d" % r].value), eje=eje, prog=ws["C%d" % r].value, lado=str(ws["D%d" % r].value).replace("LADO ", ""),
                        p0=p0, p1=p1, L=float(ws["E%d" % r].value), sep=float(ws["F%d" % r].value), nll=int(float(ws["G%d" % r].value))))
    return out


def lado_de(t, poly):
    """+1 si el muro del tramo queda a la izquierda del eje (sentido de la progresiva), -1 a la derecha."""
    if CFG["lado"]:
        return CFG["lado"][(t["eje"], t["lado"])]
    _, u = a_lo_largo(poly, (t["p0"] + t["p1"]) / 2, 0)
    return 1 if np.dot([-u[1], u[0]], RUMBO[t["lado"]]) > 0 else -1


def a_lo_largo(poly, s, lado):
    poly = np.asarray(poly, float); acc = 0.0
    for a, b in zip(poly[:-1], poly[1:]):
        Ls = float(np.hypot(*(b - a)))
        if s <= acc + Ls + 1e-6 or (b == poly[-1]).all():
            u = (b - a) / Ls; nrm = np.array([-u[1], u[0]])
            return a + u * min(s - acc, Ls) + lado * OFS * nrm, u
        acc += Ls


def fondo(doc, lam):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(CFG["zip"]) as z:
        nom = z.namelist()[0]; z.extract(nom, tmp)
    src = ezdxf.readfile(os.path.join(tmp, nom)); msp = src.modelspace()
    sel = []
    for e in msp:
        t, ly = e.dxftype(), e.dxf.layer
        if t in EXCL_TIPOS or ly in EXCL_LAYERS: continue
        if t == "INSERT" and e.dxf.name.startswith(EXCL_BLOQUES): continue
        if t == "HATCH" and ly not in CFG["verdes"]: continue
        try: bb = bbox.extents([e], fast=True)
        except Exception: continue
        EXT = CFG["ext"]
        if not bb.has_data or bb.extmin.x < EXT[0] - 2 or bb.extmin.y < EXT[1] - 2 or bb.extmax.x > EXT[2] + 2 or bb.extmax.y > EXT[3] + 2: continue
        sel.append(e)                                        # solo lo que esta dentro del predio (sin linderos ni topografia lejana)
    imp = Importer(src, doc); imp.import_entities(sel, doc.modelspace()); imp.finalize()
    # todo en gris (capa ARQ-FONDO), salvo la red de cunetas (azul) y las areas verdes (verde)
    def gris(ents, capa):
        for x in ents:
            try:
                x.dxf.layer = capa; x.dxf.color = 256
                if x.dxf.hasattr("true_color"): x.dxf.discard("true_color")
            except Exception: pass
    for blk in doc.blocks:
        if blk.name.startswith("*") or blk.name.startswith(("SIMB-", "ACERO", "_")) or blk.name in B_PROPIOS: continue
        verdes = []
        for h in [x for x in blk if x.dxftype() in ("HATCH", "MPOLYGON", "WIPEOUT", "IMAGE", "OLE2FRAME")]:
            if CFG["verdes_bloques"] and h.dxftype() == "HATCH" and h.dxf.layer in CFG["verdes"]: verdes.append(h); continue
            blk.delete_entity(h)                             # fondo limpio: sin rellenos de pisos
        gris([x for x in blk if x not in verdes], "CUNETAS-RED" if blk.name in CFG["red_bloques"] else "ARQ-FONDO")
        for h in verdes:
            h.dxf.layer = "AREA-VERDE"; h.set_solid_fill(color=3); h.rgb = (196, 228, 178)
    nuevos = [e for e in doc.modelspace() if e.dxf.layer not in [c[0] for c in CAPAS] and e.dxf.handle not in PREVIOS]
    for e in nuevos:
        if e.dxftype() == "HATCH":
            e.dxf.layer = "AREA-VERDE"; e.set_solid_fill(color=3); e.rgb = (196, 228, 178)
        elif (e.dxftype() == "INSERT" and e.dxf.name in CFG["red_bloques"]) or e.dxf.layer in CFG["red_capas"]:
            e.dxf.layer = "CUNETAS-RED"; e.dxf.color = 256
            if e.dxf.hasattr("true_color"): e.dxf.discard("true_color")
        else:
            gris([e], "ARQ-FONDO")
    return src


B_PROPIOS, PREVIOS = set(), set()


def lamina(doc, ox, oy):
    global B_PROPIOS, PREVIOS
    for nm, c, lt, lw in CAPAS:
        if nm not in doc.layers:
            ly = doc.layers.add(nm, color=c, linetype=lt); ly.dxf.lineweight = lw
    lam = B.Lamina(doc, ox, oy, ESC, "DL-00", "PLANTA DE UBICACION DE LLORADEROS EN CUNETAS COLINDANTES CON AREA VERDE",
                   "PARTIDA 01.04.03.04.03.04 - LLORADEROS PVC Ø3\" @1.50 m CON FILTRO DE GRAVA Y GEOTEXTIL - ESC. 1/250")
    B_PROPIOS = {b.name for b in doc.blocks}; PREVIOS = {e.dxf.handle for e in doc.modelspace()}
    fondo(doc, lam)
    E = json.load(open(CFG["ejes"])); T = tramos(); f = lam.f
    xp = CFG["panel"] or (CFG["ext"][2] - CFG["ext"][0]) / f + 40 + 14         # columna del cuadro, leyenda y notas (mm)
    # ---------------- etiquetas de ejes
    for k, poly in E.items():
        p = np.asarray(poly[0], float)
        lam.texto((p[0] + 0.8, p[1] + 0.8), "EJE " + k, 3.0, "EJE-TEXTO")
    # ---------------- tramos y lloraderos
    tot = 0
    for t in T:
        poly = E[t["eje"]]; sg = lado_de(t, poly)
        ss = np.linspace(t["p0"], t["p1"], max(2, int(math.ceil((t["p1"] - t["p0"]) / 0.25)) + 1))
        pts = [tuple(a_lo_largo(poly, s, sg)[0]) for s in ss]
        lam.poli(pts, "LLORAD-TRAMO", ancho=0.30)
        n = t["nll"]; d = (t["p1"] - t["p0"]) / n
        for i in range(n):                                   # un lloradero por cada 1.50 m, centrado en su paño
            q, u = a_lo_largo(poly, t["p0"] + d * (i + 0.5), sg); nrm = np.array([-u[1], u[0]]) * sg
            lam.circulo(tuple(q + nrm * 0.45), 0.22, "LLORAD-SIMB")
            lam.linea(tuple(q), tuple(q + nrm * 0.23), "LLORAD-SIMB")
        tot += n
        qm, u = a_lo_largo(poly, (t["p0"] + t["p1"]) / 2, sg); nrm = np.array([-u[1], u[0]]) * sg
        c = qm + nrm * 3.2
        lam.linea(tuple(qm + nrm * 0.7), tuple(c - nrm * 1.25), "LLORAD-TEXTO")
        lam.circulo(tuple(c), 1.25, "LLORAD-TEXTO")
        lam.texto(tuple(c), "T%d" % t["n"], 2.6, "LLORAD-TEXTO", TA.MIDDLE_CENTER)
    assert tot == sum(t["nll"] for t in T)
    # ---------------- norte
    lam.bloque("SIMB-NORTE", lam.P(385, 562), f, rot=dz.AZ_FRENTE - 90)
    # ---------------- cuadro de tramos
    filas = [("T%d" % t["n"], "EJE " + t["eje"], t["prog"], "LADO " + t["lado"], "%.2f" % t["L"], "%.2f" % t["sep"], "%d" % t["nll"]) for t in T]
    filas.append(("", "", "", "TOTAL", "%.2f" % sum(t["L"] for t in T), "", "%d" % tot))
    yb = lam.tabla(xp, 548, ["TRAMO", "EJE", "PROGRESIVA DEL TRAMO", "LADO DEL MURO", "LONGITUD (m)", "ESPAC. (m)", "N° LLORAD."], filas,
                   [16, 18, 50, 34, 30, 24, 26], 1.9, CFG["fila"], "CUADRO DE TRAMOS CON LLORADEROS (= hoja METRADO LLORADEROS de la planilla)")
    # ---------------- leyenda
    ly0 = yb - 14
    lam.texto(lam.P(xp, ly0), "LEYENDA", 3.0, "TITULOS")
    items = [("rect", "AREA-VERDE", (196, 228, 178), "Area verde (jardin, tendal, cerco vivo)"), ("linea", "CUNETAS-RED", None, "Red de cunetas del proyecto (ejes %s) y sentido del flujo" % CFG["ejes_txt"]),
             ("grueso", "LLORAD-TRAMO", None, "Muro de cuneta colindante con area verde: lleva lloraderos"), ("simb", "LLORAD-SIMB", None, "Lloradero PVC Ø 3\" con filtro de grava y geotextil (@1.50 m)"),
             ("tramo", "LLORAD-TEXTO", None, "N° de tramo (cuadro de tramos y hoja METRADO LLORADEROS)"), ("linea", "ARQ-FONDO", None, "Arquitectura (planta general del proyecto)")]
    for i, (tp, capa, rgb, txt) in enumerate(items):
        y = ly0 - 9 - i * 7
        if tp == "rect":
            pts = [lam.P(xp, y - 2), lam.P(xp + 14, y - 2), lam.P(xp + 14, y + 2), lam.P(xp, y + 2)]
            h = lam.msp.add_hatch(color=3, dxfattribs={"layer": capa}); h.paths.add_polyline_path(pts, is_closed=True); h.rgb = rgb
        elif tp == "linea": lam.linea(lam.P(xp, y), lam.P(xp + 14, y), capa)
        elif tp == "grueso": lam.poli([lam.P(xp, y), lam.P(xp + 14, y)], capa, ancho=0.30)
        elif tp == "simb":
            lam.poli([lam.P(xp, y - 1.2), lam.P(xp + 14, y - 1.2)], "LLORAD-TRAMO", ancho=0.30)
            for xx in (3.5, 10.5): lam.circulo(lam.P(xp + xx, y + 0.8), 0.22, capa)
        else:
            lam.circulo(lam.P(xp + 7, y), 2.6 * f, capa); lam.texto(lam.P(xp + 7, y), "T1", 2.2, capa, TA.MIDDLE_CENTER)
        lam.texto(lam.P(xp + 18, y), txt, 2.0, "TEXTOS", TA.MIDDLE_LEFT)
    # ---------------- detalle tipico (bloque de las especificaciones de lloraderos, dibujado a 1/10)
    import espec_lloraderos as EL
    if "ARIAL-N" not in doc.styles: doc.styles.add("ARIAL-N", font="arialbd.ttf")
    if "ARIAL" not in doc.styles: doc.styles.add("ARIAL", font="arial.ttf")
    for nm, c in (("LEY-TEXTO", 7), ("LEY-TITULO", 160), ("LEY-SIMBOLO", 7), ("LEY-RELLENO", 8), ("LEY-MARCO", 250), ("LEY-COTA", 94)):
        if nm not in doc.layers: doc.layers.add(nm, color=c)
    blk = (EL.detalle_cad if CFG["cad"] else EL.detalle)(doc, CFG["nombre"])   # cad: sin patrones de achurado (AutoCAD)
    if CFG["cad"]:
        for t in blk.query("TEXT"): t.dxf.text = t.dxf.text.replace("³", "3")
    for x in [x for x in blk if x.dxftype() == "TEXT" and x.dxf.text.startswith(("ESC. REAL", "DETALLE DE INSTALACION", "Seccion cuneta"))]: blk.delete_entity(x)
    bb = bbox.extents(blk); k = ESC / 10                         # 1/10 en una lamina a 1/250
    cx, cy = (bb.extmin.x + bb.extmax.x) / 2, (bb.extmin.y + bb.extmax.y) / 2
    alto = (bb.extmax.y - cy) * k / f                          # media altura del detalle en mm de papel
    xd, yd = (560, 238) if CFG["panel"] else (xp + 160, ly0 - 112 - 12 - alto)   # varones: debajo de las notas, sobre el rotulo
    lam.msp.add_blockref(blk.name, (lam.P(xd, yd)[0] - cx * k, lam.P(xd, yd)[1] - cy * k), dxfattribs={"layer": "0", "xscale": k, "yscale": k})
    lam.titulo_vista(xd, yd + (bb.extmax.y - cy) * k / f + 12, "DETALLE TIPICO DEL LLORADERO", "ESC. 1/10 - seccion de cuneta junto a area verde (H variable; se dibuja H = 0.50 m). Detalle completo en DL-01 y DL-02", 150)
    # ---------------- notas
    lam.notas(xp, ly0 - 58, "NOTAS", [
        "1. Llevan lloraderos solo los muros de cuneta cuya cara exterior colinda con area verde, donde el agua del terreno empuja al muro. Los muros junto a veredas, pisos o edificaciones no llevan.",
        "2. Un lloradero cada 1.50 m: N° por tramo = REDONDEAR.MAS(longitud / 1.50), repartidos en el tramo. Se ubican a no menos de 0.30 m de las juntas de dilatacion de la cuneta.",
        "3. Lloradero: tubo PVC-U Ø 3\" de 0.30 m (0.20 m perforado) a media altura del muro, con S = 0.5 % hacia la cuneta, y filtro de grava de 0.30 x 0.30 x 0.30 m forrado con geotextil no tejido. Detalle en las laminas DL-01 y DL-02.",
        "4. Metrado: partida 01.04.03.04.03.04 = %d und (hojas METRADO LLORADEROS y DESAGREGADO LLORADEROS de la planilla)." % tot,
        "5. Progresivas medidas a lo largo del eje de cada cuneta desde su inicio (0+000.00), en el sentido de la planta de drenaje.",
    ], hmm=1.9, ancho_mm=245)
    return lam, tot


if __name__ == "__main__":
    CFG = PROY[sys.argv[1] if len(sys.argv) > 1 else "refugio"]
    if CFG["proyecto"]: B.PROYECTO, B.UBICACION = CFG["proyecto"], CFG["ubicacion"]
    SAL = CFG["sal"]
    doc = B.nuevo_documento()
    x0, y0, x1, y1 = CFG["ext"]
    lam, tot = lamina(doc, x0 - 40 * ESC / 1000, y0 - 40 * ESC / 1000)
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: -1 for e in msp.query("HATCH")})
    L.presentaciones(doc, {"DL-00": lam})
    print("errores de auditoria:", len(doc.audit().errors), "| lloraderos:", tot)
    doc.saveas(SAL)
    print(SAL, os.path.getsize(SAL) // 1024, "KB")
