"""Metrado de las cunetas de CAR Varones (CUI 2705619) sobre la plantilla de metrados del proyecto
(METRADO_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS, misma estructura hoja por hoja).

Datos: perfiles longitudinales y secciones del DXF PERFIL_CAR_VARONES.dxf (lectura en
insumos/katiuska/CUNETAS_CAR_VARONES_LEIDAS.json). Se llenan las mismas celdas que la plantilla llena
(longitudes, areas de muro, alturas, tramos abiertos/tapados, acero por tramo, curado, rejillas, juntas)
y se dejan en blanco los bloques de ejes que Varones no tiene. Los datos que no estan en el DXF
(montantes, sumideros, dados, tapas de registro) quedan en cero y se listan en PENDIENTES.
"""
import os, sys, json, math, re, copy
import openpyxl
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from metrado_xlsx import reinyectar_vml

PLANTILLA = os.path.join(RAIZ, "insumos", "solange", "METRADO_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS_v2.xlsx")
DXF = os.path.join(RAIZ, "insumos", "katiuska", "PERFIL_CAR_VARONES.dxf")
SALIDA = os.path.join(RAIZ, "entregables", "METRADO_DRENAJE_PLUVIAL_CAR_VARONES_CUNETAS.xlsx")
X0 = 2087.48            # origen de progresivas en el DXF
B_INT, E_MURO, E_LOSA, B_EXT = 0.40, 0.10, 0.10, 0.60
SEP_TRANSV = 0.25
PENDIENTES = []


# ----------------------------------------------------------------------------- lectura del DXF
def leer_dxf():
    import ezdxf
    doc = ezdxf.readfile(DXF); msp = doc.modelspace()
    ejes = sorted([(e.dxf.insert.y, (e.plain_text().strip() if e.dxftype() == "MTEXT" else e.dxf.text)) for e in msp if e.dxf.layer == "A-AREA-IDEN"], reverse=True)
    bandas = [(n, y + 1.0, (ejes[i + 1][0] if i + 1 < len(ejes) else 1360) + 1.0) for i, (y, n) in enumerate(ejes)]
    def banda(y):
        for n, a, b in bandas:
            if b < y <= a: return n
    def color(e):
        c = e.dxf.color
        return doc.layers.get(e.dxf.layer).color if c == 256 else c
    out = {}
    for n, _, _ in bandas: out[n] = dict(sec=[], abierto=[], cerrado=[], L=0.0)
    # anotaciones de las secciones en los perfiles
    cols = {}
    for e in msp:
        if e.dxftype() == "TEXT" and e.dxf.insert.x < 2216:
            t = e.dxf.text.strip(); x, y = e.dxf.insert.x, e.dxf.insert.y
            if t.startswith("%%USECCION") or re.match(r"(NCT|NCF|H):", t):
                key = (banda(y), round((x - X0) / 0.5) * 0.5)
                d = cols.setdefault(key, {})
                if ":" in t: d[t.split(":")[0]] = float(re.sub(r"[^\d.]", "", t.split(":")[1]))
                else: d["SEC"] = int(re.sub(r"\D", "", t))
    for (n, x), d in cols.items():
        if "H" in d: out[n]["sec"].append(dict(x=round(x, 2), sec=d.get("SEC"), NCT=d.get("NCT"), NCF=d.get("NCF"), H=d["H"]))
    for e in msp:
        if e.dxftype() == "TEXT" and e.dxf.layer == "GRID_TEXT" and e.dxf.insert.x < 2216 and e.dxf.text.strip().startswith("0+"):
            try: out[banda(e.dxf.insert.y)].setdefault("prog", []).append(float(e.dxf.text.strip()[2:]))
            except ValueError: pass
    for n in out:
        s = sorted(out[n]["sec"], key=lambda r: r["x"]); s[0]["x"] = 0.0      # la primera seccion es el 0+000
        for i, r in enumerate(s): r["sec"] = s[0]["sec"] + i                   # numeracion consecutiva por eje (rotulos desplazados)
        out[n]["sec"] = s
        if n == "EJE 04" and abs(s[-1]["NCF"] - 259.66) < 0.01: s[-1]["NCF"] = 260.42   # corregido por el proyectista (0.5 % desde 260.95)
    # tramos por color: 5 azul = abierto, 84 verde = cerrado; se toman las lineas horizontales del perfil
    for e in msp:
        c = color(e)
        if e.dxftype() == "LINE" and c in (5, 84) and e.dxf.start.x < 2216 and abs(e.dxf.start.y - e.dxf.end.y) < 0.05:
            n = banda(e.dxf.start.y); a, b = sorted([e.dxf.start.x - X0, e.dxf.end.x - X0])
            out[n]["abierto" if c == 5 else "cerrado"].append((a, b))
        elif e.dxftype() == "LWPOLYLINE" and c in (5, 84):
            pts = list(e.get_points("xy"))
            if pts[0][0] > 2216: continue
            xs = [p[0] - X0 for p in pts]; n = banda(pts[0][1])
            if max(xs) - min(xs) > 0.5: out[n]["abierto" if c == 5 else "cerrado"].append((min(xs), max(xs)))
    return out


def tramos_eje(d):
    """Une los segmentos de color en tramos consecutivos abierto / cerrado desde 0+000 (las lineas duplicadas
    del dibujo se funden por union de intervalos)."""
    def union(ivs):
        ivs = sorted((max(a, 0.87) - 0.87, b - 0.87) for a, b in ivs)
        out = []
        for a, b in ivs:
            if out and a <= out[-1][1] + 0.3: out[-1][1] = max(out[-1][1], b)
            else: out.append([a, b])
        return [(a, b) for a, b in out if b - a > 0.3]
    segs = [("ABIERTA", a, b) for a, b in union(d["abierto"])] + [("TAPADA", a, b) for a, b in union(d["cerrado"])]
    segs.sort(key=lambda s: s[1])
    out = []
    progs = d.get("prog", [])
    for i, (t, a, b) in enumerate(segs):
        a2 = 0.0 if i == 0 else out[-1][2]
        cerca = [p for p in progs if abs(p - b) < 0.15]
        out.append([t, a2, round(cerca[0] if cerca else b, 2)])        # el limite se ajusta a la progresiva rotulada
    return out


def H_en(d, x):
    """Altura interior en la progresiva x, interpolando entre las secciones rotuladas."""
    s = d["sec"]; xs = [r["x"] for r in s]; hs = [r["H"] for r in s]
    if x <= xs[0]: return hs[0]
    if x >= xs[-1]: return hs[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            f = (x - xs[i]) / (xs[i + 1] - xs[i]); return hs[i] + f * (hs[i + 1] - hs[i])


def area_muro(d, a, b, n=200):
    """Integral de H entre a y b (area de una cara del muro, en m2)."""
    tot = 0.0
    for i in range(n):
        x1 = a + (b - a) * i / n; x2 = a + (b - a) * (i + 1) / n
        tot += 0.5 * (H_en(d, x1) + H_en(d, x2)) * (x2 - x1)
    return tot


def sec_cercana(d, x):
    return min(d["sec"], key=lambda r: abs(r["x"] - x))


# ----------------------------------------------------------------------------- llenado de la plantilla
def limpiar(ws, celdas):
    for c in celdas: ws[c].value = None


def construir():
    D = leer_dxf()
    nombres = sorted(D.keys())                       # EJE 01 .. EJE 09
    E = []
    for n in nombres:
        d = D[n]; tr = tramos_eje(d); L = tr[-1][2]
        tramos = []
        for i, (t, a, b) in enumerate(tr):
            tramos.append(dict(tipo=t, a=a, b=b, L=round(b - a, 2), Hi=round(H_en(d, a), 2), Hf=round(H_en(d, b), 2), area=area_muro(d, a, b),
                               sec_i=sec_cercana(d, a)["sec"], sec_f=sec_cercana(d, b)["sec"]))
        E.append(dict(nombre=n, num=int(n.split()[1]), L=round(L, 2), tramos=tramos, area=area_muro(d, 0, L), L_tap=round(sum(t["L"] for t in tramos if t["tipo"] == "TAPADA"), 2),
                      L_ab=round(sum(t["L"] for t in tramos if t["tipo"] == "ABIERTA"), 2), Hprom=area_muro(d, 0, L) / L, NCF_ini=d["sec"][0]["NCF"], NCF_fin=d["sec"][-1]["NCF"]))
    wb = openpyxl.load_workbook(PLANTILLA)
    # ---------------- RESUMEN (datos del proyecto)
    wr = wb["RESUMEN"]
    wr["B5"] = "CENTRO DE ACOGIDA RESIDENCIAL (CAR) VARONES - DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN, con CUI N.° 2705619"
    PENDIENTES.append("RESUMEN!B5: nombre completo del proyecto CAR Varones (se puso un nombre provisional con el CUI 2705619).")
    # ---------------- CONCRETO EN CUNETAS: bloques de 12 filas; ejes 1-6 columna E, 7-12 columna M
    wc = wb["CONCRETO EN CUNETAS"]
    for k in range(12):
        r0 = 10 + 12 * (k % 6); col = "E" if k < 6 else "M"; lab = "B" if k < 6 else "J"
        if k < len(E):
            e = E[k]
            wc["%s%d" % (lab, r0)] = "CUNETA EJE %02d" % e["num"]
            wc["%s%d" % (col, r0)] = round(e["area"], 2); wc["%s%d" % (col, r0 + 4)] = e["L"]; wc["%s%d" % (col, r0 + 6)] = e["L_tap"]
        else:
            wc["%s%d" % (lab, r0)] = None; wc["%s%d" % (col, r0)] = 0; wc["%s%d" % (col, r0 + 4)] = 0; wc["%s%d" % (col, r0 + 6)] = 0
    # ---------------- ENCOFRADO: bloque k en fila [12,12,23,23,34,34,45,45,57,57,69,69], columna F (impar) / N (par)
    we = wb["ENCOFRADO Y DESENCOFRADO"]; filas_e = [12, 12, 23, 23, 34, 34, 45, 45, 57, 57, 69, 69]
    for k in range(12):
        r = filas_e[k]; col = "F" if k % 2 == 0 else "N"; lab = "B" if k % 2 == 0 else "J"; tipo = "C" if k % 2 == 0 else "K"
        if k < len(E):
            e = E[k]
            ab = [t for t in e["tramos"] if t["tipo"] == "ABIERTA"]; tp = [t for t in e["tramos"] if t["tipo"] == "TAPADA"]
            a_ab = sum(t["area"] for t in ab); L_ab = sum(t["L"] for t in ab); a_tp = sum(t["area"] for t in tp); L_tp = sum(t["L"] for t in tp)
            we["%s%d" % (lab, r)] = "EJE %d" % e["num"]; we["%s%d" % (tipo, r)] = "ABIERTA"
            we["%s%d" % (col, r)] = round(a_ab + E_LOSA * L_ab, 2)        # muro externo abierta: H + losa de fondo
            we["%s%d" % (col, r + 2)] = round(a_ab, 2)                     # muro interno abierta: H
            we["%s%d" % (col, r + 4)] = round(a_tp + 2 * E_LOSA * L_tp, 2)  # muro externo tapada: H + losa de fondo + tapa
            we["%s%d" % (col, r + 6)] = round(a_tp, 2)                     # muro interno tapada: H
            we["%s%d" % (col, r + 8)] = "=%s*%s" % (L_tp, B_INT) if L_tp > 0 else 0   # fondo de la tapa: L x 0.40
        else:
            we["%s%d" % (lab, r)] = None; we["%s%d" % (tipo, r)] = None
            for off in (0, 2, 4, 6, 8): we["%s%d" % (col, r + off)] = 0
    # ---------------- METRADO ACERO (filas 11-37), CURADO (7-36), REJILLAS (7-36): una fila por tramo
    wa = wb["METRADO ACERO"]; wk = wb["METRADO DE CURADO"]; wj = wb["METRADO DE REJILLAS"]
    # Acero solo donde la altura (medida desde el NCT) supera 0.40 m; los tramos tapados llevan acero siempre
    # (cuerpo y tapa). Un tramo abierto que pasa de 0.40 dentro de su longitud se metra desde el punto donde H = 0.40.
    H_MIN = 0.40
    filas = []
    for e in E:
        d = D[e["nombre"]]; k = 0
        for t in e["tramos"]:
            if t["tipo"] == "TAPADA":
                filas.append((e, k, t)); k += 1
            elif t["Hf"] >= H_MIN - 1e-9:
                if t["Hi"] >= H_MIN - 1e-9:
                    filas.append((e, k, t)); k += 1
                else:
                    x40 = t["a"]
                    while H_en(d, x40) < H_MIN - 1e-9 and x40 < t["b"]: x40 += 0.01
                    x40 = round(x40, 2)
                    cerca = [p for p in d.get("prog", []) if abs(p - x40) < 0.3]
                    if cerca: x40 = cerca[0]
                    t2 = dict(t); t2.update(a=x40, L=round(t["b"] - x40, 2), Hi=round(H_en(d, x40), 2), sec_i=sec_cercana(d, x40)["sec"])
                    filas.append((e, k, t2)); k += 1
    assert len(filas) <= 27, "mas tramos que filas en la plantilla"
    sep_long = {}
    for e in E:
        for s in D[e["nombre"]]["sec"]:
            sep_long[s["sec"]] = None
    for i in range(27):
        ra, rk, rj = 11 + i, 7 + i, 7 + i
        if i < len(filas):
            e, j, t = filas[i]
            Hm = (t["Hi"] + t["Hf"]) / 2
            sep = 0.20 if Hm < 0.45 else (0.22 if Hm < 0.60 else 0.25)
            wa["A%d" % ra] = i + 1; wa["B%d" % ra] = "EJE %02d" % e["num"]; wa["C%d" % ra] = "TRAMO %02d" % (j + 1); wa["D%d" % ra] = t["tipo"]
            wa["E%d" % ra] = "SEC %02d" % t["sec_i"]; wa["F%d" % ra] = "SEC %02d" % t["sec_f"]; wa["G%d" % ra] = t["L"]; wa["H%d" % ra] = '3/8"'
            wa["J%d" % ra] = sep
            wa["K%d" % ra] = math.ceil((B_EXT + 2 * t["Hi"]) / sep); wa["L%d" % ra] = math.ceil((B_EXT + 2 * t["Hf"]) / sep)
            wa["P%d" % ra] = SEP_TRANSV; wa["Q%d" % ra] = round(B_EXT + 2 * (t["Hi"] + 0.05), 2); wa["R%d" % ra] = round(B_EXT + 2 * (t["Hf"] + 0.05), 2)
            if t["tipo"] == "TAPADA":
                wa["X%d" % ra] = '3/8"'; wa["Y%d" % ra] = 0.56; wa["Z%d" % ra] = SEP_TRANSV; wa["AA%d" % ra] = 0.56; wa["AB%d" % ra] = 0.56
            else:
                wa["X%d" % ra] = None; wa["Y%d" % ra] = ""; wa["Z%d" % ra] = None; wa["AA%d" % ra] = None; wa["AB%d" % ra] = None
            for ws_, r in ((wk, rk), (wj, rj)):
                ws_["A%d" % r] = i + 1; ws_["B%d" % r] = "EJE %02d" % e["num"]; ws_["C%d" % r] = "TRAMO %02d" % (j + 1); ws_["D%d" % r] = t["tipo"]; ws_["E%d" % r] = t["L"]
            wk["F%d" % rk] = B_INT; wk["G%d" % rk] = t["Hi"]; wk["H%d" % rk] = t["Hf"]
            wj["F%d" % rj] = 0
        else:
            limpiar(wa, ["%s%d" % (c, ra) for c in ("A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "P", "Q", "R", "X", "Z", "AA", "AB")]); wa["Y%d" % ra] = ""
            limpiar(wk, ["%s%d" % (c, rk) for c in ("A", "B", "C", "D", "E", "F", "G", "H")])
            limpiar(wj, ["%s%d" % (c, rj) for c in ("A", "B", "C", "D", "E", "F")])
    # ---------------- JUNTA DE DILATACION: filas 13-24, un eje por fila (D longitud; E apunta al bloque de CONCRETO)
    wjd = wb["METRADO JUNTA DE DILATACION"]
    for k in range(12):
        r = 13 + k
        if k < len(E): wjd["B%d" % r] = "EJE %02d" % E[k]["num"]; wjd["D%d" % r] = E[k]["L"]
        else: limpiar(wjd, ["%s%d" % (c, r) for c in "ABDEFGHIJ"])
    # ---------------- PLANILLA GENERAL: filas por eje
    wp = wb["PLANILLA GENERAL DE METRADOS"]
    bloques = {"limpieza": (12, "D", None), "trazo": (25, "D", None), "excav": (39, "D", "F"), "refine": (55, "D", None), "relleno": (68, "D", "F"), "solado": (85, "D", None)}
    for nombre, (r0, cL, cH) in bloques.items():
        for k in range(12):
            r = r0 + k
            if k < len(E):
                wp["B%d" % r] = "EJE %d" % E[k]["num"]; wp["C%d" % r] = 1; wp["%s%d" % (cL, r)] = E[k]["L"]
                if cH: wp["%s%d" % (cH, r)] = round(E[k]["Hprom"] + E_LOSA, 2)     # altura promedio + losa de fondo (el solado lo suma PARAMETROS!B15)
            else:
                wp["B%d" % r] = None; wp["C%d" % r] = None; wp["%s%d" % (cL, r)] = None
                if cH: wp["%s%d" % (cH, r)] = None
    for r0 in (102, 115):
        for k in range(12):
            wp["B%d" % (r0 + k)] = ("EJE %d" % E[k]["num"]) if k < len(E) else None
    # dados, montantes, sumideros: sin datos de Varones
    for c in ("C51", "C97", "K139", "C140", "C142", "C145"): wp[c] = 0
    PENDIENTES.append("PLANILLA GENERAL: dados de concreto (C51, C97) y falsas columnas de montantes (K139, C140, C142, C145) en 0: falta la cantidad de montantes de Varones.")
    wm = wb["METRADO MONTANTES"]
    for r in range(11, 57):
        for c in "CDEGHJKMNPQ":
            cell = wm["%s%d" % (c, r)]
            if not (isinstance(cell.value, str) and cell.value.startswith("=")): cell.value = None
    PENDIENTES.append("METRADO MONTANTES: hoja vaciada; falta el calculo de montantes por edificacion de Varones (plano de techos).")
    wsu = wb["METRADO  EN PISO (SUMIDERO)"]
    for r in range(8, 12):
        for c in "BCDEF": wsu["%s%d" % (c, r)] = 0
        wsu["G%d" % r] = "Sin datos de Varones"
    PENDIENTES.append("METRADO EN PISO (SUMIDERO): sectores en 0; falta la red de piso y sumideros de Varones.")
    # tapas de registro en cunetas tapadas: 1 por tramo tapado (provisional)
    n_tap = sum(1 for e in E for t in e["tramos"] if t["tipo"] == "TAPADA")
    wb["PARAMETROS"]["B4"] = n_tap; wb["PARAMETROS"]["D4"] = "Provisional: 1 tapa por tramo tapado (%d tramos); confirmar con el plano" % n_tap
    PENDIENTES.append("PARAMETROS!B4: tapas de registro en cunetas tapadas = %d (1 por tramo tapado, provisional)." % n_tap)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True); wb.save(SALIDA)
    reinyectar_vml(PLANTILLA, SALIDA)
    return E, SALIDA


if __name__ == "__main__":
    E, fn = construir()
    print(fn)
    for e in E:
        print("%s L=%.2f Hprom=%.3f area muro=%.2f tapada=%.2f  NCF %.2f -> %.2f" % (e["nombre"], e["L"], e["Hprom"], e["area"], e["L_tap"], e["NCF_ini"], e["NCF_fin"]))
        for t in e["tramos"]: print("    %-8s %7.2f - %7.2f  L=%6.2f  H %.2f -> %.2f  sec %s-%s" % (t["tipo"], t["a"], t["b"], t["L"], t["Hi"], t["Hf"], t["sec_i"], t["sec_f"]))
    import openpyxl as _o
    wa = _o.load_workbook(fn)["METRADO ACERO"]
    print("FILAS DE ACERO:")
    for r in range(11, 38):
        if wa["B%d" % r].value: print("   ", wa["B%d" % r].value, wa["C%d" % r].value, wa["D%d" % r].value, wa["E%d" % r].value, wa["F%d" % r].value, "L=", wa["G%d" % r].value, "H", wa["Q%d" % r].value, wa["R%d" % r].value)
    print("PENDIENTES:"); [print(" -", p) for p in PENDIENTES]
