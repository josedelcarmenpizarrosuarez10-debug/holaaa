"""Extrae del plano original del CAR Mujeres (insumos/wilma/PLANOS_COLECTOR_PLUVIAL_CAR_MUJERES.dxf) la geometria que
se conserva tal cual (eje, muros en planta, registros, cunetas, cruces, juntas, lindero, base de arquitectura, salida y
terreno del perfil) y del recalculo de la memoria de calculo el perfil de flujo. Salida: base_m.json (junto a este script).

Uso: python3 extraer_m.py <PLANOS_ORIGINAL.dxf> <MEMORIA_RECALCULADA.xlsx> <METRADO_COLECTOR.xlsx>
"""
import sys, os, json, math
import ezdxf, openpyxl

AQUI = os.path.dirname(os.path.abspath(__file__))
dxf, mem, met = sys.argv[1], sys.argv[2], sys.argv[3]
doc = ezdxf.readfile(dxf); msp = doc.modelspace()

def pts_de(e):
    if e.dxftype() == "LINE": return [tuple(e.dxf.start)[:2], tuple(e.dxf.end)[:2]]
    if e.dxftype() == "POLYLINE": return [tuple(v.dxf.location)[:2] for v in e.vertices]
    return None

def ancla(e):
    t = e.dxftype()
    if t in ("TEXT", "INSERT"): return e.dxf.insert
    if t in ("CIRCLE", "ARC"): return e.dxf.center
    if t in ("LINE", "POLYLINE"): return pts_de(e)[0]
    if t == "SOLID": return e.dxf.vtx0
    if t == "DIMENSION": return e.dxf.defpoint
    return None

def en(e, caja):
    p = ancla(e)
    return p is not None and caja[0] - 0.1 <= p[0] <= caja[2] + 0.1 and caja[1] - 0.1 <= p[1] <= caja[3] + 0.1

R = lambda v: round(float(v), 4)
DP01 = (-622.0, -52.0, -411.75, 96.5)
out = {}
# ---------------------------------------------------------------- planta
ents = [e for e in msp if en(e, DP01)]
def capa(nombre, tipos=("LINE", "POLYLINE")):
    return [[(R(x), R(y)) for x, y in pts_de(e)] for e in ents if e.dxf.layer == nombre and e.dxftype() in tipos]
# eje: la polilinea de 9 vertices (la linea suelta es la muestra de la leyenda)
eje = [p for p in capa("EJE-COLECTOR") if len(p) > 2][0]
out["eje"] = eje
caja_col = (-570, 5, -415, 40)       # zona del colector en planta (fuera de leyenda y cuadros)
def dentro(pl, c=caja_col): return all(c[0] <= x <= c[2] and c[1] <= y <= c[3] for x, y in pl)
for nombre in ("CONCRETO", "CONCRETO-OCULTO", "CUNETA", "CUNETA-OCULTA", "LINDERO", "EMBOQUILLADO", "CRUCE-VEHICULAR", "JUNTAS"):
    out[nombre] = [pl for pl in capa(nombre) if dentro(pl)]
out["piedras"] = [(R(e.dxf.center[0]), R(e.dxf.center[1]), R(e.dxf.radius)) for e in ents if e.dxf.layer == "EMBOQUILLADO-PIEDRA"]
out["registros"] = [(R(e.dxf.insert[0]), R(e.dxf.insert[1]), R(e.dxf.rotation)) for e in ents
                    if e.dxftype() == "INSERT" and e.dxf.name == "REGISTRO-PLANTA" and dentro([tuple(e.dxf.insert)[:2]])]
# base de arquitectura (lineas, arcos, circulos) y sus textos
arq = []
for e in ents:
    if e.dxf.layer != "ARQ-BASE": continue
    t = e.dxftype()
    if t in ("LINE", "POLYLINE"): arq.append(["L", [(R(x), R(y)) for x, y in pts_de(e)]])
    elif t == "CIRCLE": arq.append(["C", (R(e.dxf.center[0]), R(e.dxf.center[1])), R(e.dxf.radius)])
    elif t == "ARC": arq.append(["A", (R(e.dxf.center[0]), R(e.dxf.center[1])), R(e.dxf.radius), R(e.dxf.start_angle), R(e.dxf.end_angle)])
out["arq"] = arq
out["arq_textos"] = [(R(e.dxf.insert[0]), R(e.dxf.insert[1]), R(e.dxf.rotation), R(e.dxf.height), e.dxf.text)
                     for e in ents if e.dxf.layer == "ARQ-TEXTO" and e.dxftype() == "TEXT"]
# cuadro de coordenadas (UTM) del plano original
filas = {}
for e in ents:
    if e.dxftype() == "TEXT" and -613 < e.dxf.insert[0] < -583 and 66 < e.dxf.insert[1] < 84.5:
        filas.setdefault(round(e.dxf.insert[1], 1), []).append((e.dxf.insert[0], e.dxf.text))
out["cuadro_utm"] = [[s for _, s in sorted(v)] for k, v in sorted(filas.items(), reverse=True)]
out["norte_rot"] = [R(e.dxf.rotation) for e in ents if e.dxftype() == "INSERT" and e.dxf.name == "SIMB-NORTE"][0]

# ---------------------------------------------------------------- terreno natural (hoja TRAMOS del metrado: TIN en la progresiva media)
wbm = openpyxl.load_workbook(met, data_only=False)
ter = []
for r in wbm["TRAMOS"].iter_rows(min_row=5, values_only=True):
    if isinstance(r[0], (int, float)) and isinstance(r[1], (int, float)) and isinstance(r[9], (int, float)):
        ter.append((R((r[0] + r[1]) / 2), R(r[9])))
out["terreno"] = ter

# ---------------------------------------------------------------- salida (DP-07, 1/25): geometria original
# ---------------------------------------------------------------- perfil de flujo (memoria recalculada)
wb = openpyxl.load_workbook(mem, data_only=True); ws = wb["PERFIL_FLUJO"]
pf = []
for r in ws.iter_rows(min_row=5, values_only=True):
    if isinstance(r[0], (int, float)) and isinstance(r[4], (int, float)):
        pf.append([R(r[0]), R(r[1]), R(r[2]), R(r[4]), R(r[5]), R(r[6]), R(r[7]), R(r[10]), R(r[11])])
out["perfil_flujo"] = sorted(pf)       # prog, CF, Q m3/s, y, NA, V, Fr, llenado, BL
json.dump(out, open(os.path.join(AQUI, "base_m.json"), "w"))
print({k: (len(v) if isinstance(v, list) else v) for k, v in out.items()})
