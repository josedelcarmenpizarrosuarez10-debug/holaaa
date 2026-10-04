"""Datos de diseno, geometria y calculo hidraulico del colector pluvial frontal.

Tramo CAR Varones (CUI 2705619): empalme con la caja de llegada CL del colector del Hogar de Refugio
Temporal (CUI 2675514). Mismo interfaz que herramientas/diseno.py (D, P_*, ZONAS, CUNETAS, REGISTROS,
fondo, techo, zona, eje_local, local_a_utm) para reutilizar los modulos de secciones, metrado y detalles.

Coordenadas: sistema local del plano de arquitectura de Solange (la planta de Varones se traslada con
insumos/katiuska/transform_varones_a_solange.json). Progresivas desde el poste derecho del porton de
camiones (0+000, extremo este) hacia la caja CL (extremo oeste).
"""
import json, math, os
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
SAL = os.path.join(RAIZ, "entregables_varones")
CALC = os.path.join(SAL, "_calc")
import sys; sys.path.insert(0, HERR)
import diseno as _sol      # transformacion local -> UTM y datos del tramo de Solange

D = dict(
    proyecto="CAR Varones", cui="2705619",
    receptor="Hogar de Refugio Temporal (CUI 2675514), caja de llegada CL",
    aporte_externo=None,
    TR=25, I=210.98, tc=10, FS=1.15, C_pond=0.7707,
    A_total=6752.03, Q_total=258.7,              # L/s, memoria de hidrologia de Varones (igual a lo citado en Solange)
    b=0.60, e_muro=0.15, e_fondo=0.15, e_losa=0.10, e_losa_camion=0.25, e_solado=0.05, n=0.015,
    NPT=261.15,                 # piso terminado de la franja exterior de Varones (losa superior al ras)
    NPT_empalme=261.15,         # la losa se mantiene en 261.15 hasta la CL; la CL de Solange (que queda del lado de Varones,
                                # entre el lindero x=349162.00 y x=349163.80) sube su tapa a 261.15 y recibe el colector por su muro este
    NPT_CL=261.15,              # cota de la tapa de la CL (piso terminado de Varones)
    L_empalme=0.0,              # largo del tramo final horizontal (se calcula)
    CF0=260.20, S=0.003,        # cota de fondo en 0+000 y pendiente
    junta_cerco=0.025,          # holgura entre el muro norte del colector y la linea de referencia del frente (no hay cerco)
    llenado_max=0.85, BL_min=0.05,
    # caja de llegada CL de Solange (receptor)
    CL_piso=_sol.D["CF0"] - _sol.D["CL_poza"], CL_CF0=_sol.D["CF0"], CL_NA=None, CL_largo=_sol.D["CL_largo"], CL_ancho=_sol.D["CL_ancho"],
    porton_camiones=5.78,
)
D["b_ext"] = D["b"] + 2 * D["e_muro"]                      # 0.90
D["eje_desde_cerco"] = D["junta_cerco"] + D["e_muro"] + D["b"] / 2   # 0.475

# ----------------------------------------------------------------------------- 1. geometria en planta
FR = json.load(open(os.path.join(RAIZ, "insumos", "katiuska", "frente_varones_marco_solange.json")))
CERCO = [tuple(p) for p in FR["cerco"]]                     # linea de referencia del frente (limite de las areas exteriores del plano de arquitectura); el CAR Varones NO tiene cerco perimetrico en este frente
BORDE = CERCO
X_NE, Y_CERCO = _sol.X_NE, _sol.Y_CERCO                     # lindero con Solange y cerco sur de Solange
Y_EJE_CL = _sol.Y_EJE                                       # eje del colector de Solange (= eje de la CL)
X_SO = X_NE                                                  # (compatibilidad)


def _offset(pts, d):
    """Polilinea paralela a d metros hacia la izquierda del sentido de avance (lado predio)."""
    P = np.array(pts); out = []
    for i in range(len(P)):
        if i == 0: dirs = [P[1] - P[0]]
        elif i == len(P) - 1: dirs = [P[-1] - P[-2]]
        else: dirs = [P[i] - P[i - 1], P[i + 1] - P[i]]
        ns = []
        for v in dirs:
            v = v / np.linalg.norm(v); ns.append(np.array([-v[1], v[0]]))
        n = np.mean(ns, axis=0); n = n / np.linalg.norm(n)
        # correccion de la bisectriz para mantener la distancia d
        cosang = np.dot(ns[0], n)
        out.append(P[i] + n * d / max(cosang, 0.3))
    return [tuple(p) for p in out]


_eje_cerco = _offset(CERCO, D["eje_desde_cerco"])
# ultimo tramo: desde el punto del eje que cruza y = Y_EJE_CL, horizontal hasta la cara este (exterior) de la CL de Solange.
# La CL ocupa x = X_NE .. X_NE + CL_largo + 2 e_muro (1.80 m) del lado de Varones (ver dxf_planta.dp01 y dxf_cajas_iso.dp07 de Solange).
X_CL_ESTE = X_NE + _sol.D["CL_largo"] + 2 * _sol.D["e_muro"]
_a, _b = np.array(_eje_cerco[-2]), np.array(_eje_cerco[-1])
_tt = (Y_EJE_CL - _a[1]) / (_b[1] - _a[1]); _pq = _a + _tt * (_b - _a)
EJE = _eje_cerco[:-1] + [tuple(_pq), (X_CL_ESTE, Y_EJE_CL)]
_P = np.array(EJE); _seg = np.hypot(np.diff(_P[:, 0]), np.diff(_P[:, 1])); _prog = np.concatenate([[0.0], np.cumsum(_seg)])
P_FIN = float(_prog[-1])                 # cara exterior del muro de la CL (fin del colector)
P_QUIEBRE = float(_prog[-2])             # inicio del tramo de empalme (horizontal)
D["L_empalme"] = round(P_FIN - P_QUIEBRE, 2)
P_EMPALME = P_QUIEBRE
P_BRINK = P_FIN                          # compatibilidad: el "brink" (caida libre a la CL) es el fin
P_B1 = P_QUIEBRE; P_B2 = P_QUIEBRE       # compatibilidad con metrado_calc.segmentos
L_FRENTE = P_FIN


def cruce_vertical(x, lateral=0.0):
    """Las cunetas del plano son rectas norte-sur (x = constante). Devuelve (progresiva, y) del punto donde la vertical x
    corta la polilinea del eje desplazada `lateral` m hacia el predio (norte); lateral = b/2 + e_muro es la cara del muro."""
    for i in range(len(_seg)):
        a, b = _P[i], _P[i + 1]; d = (b - a) / _seg[i]; n = np.array([-d[1], d[0]])
        if n[1] < 0: n = -n
        a2, b2 = a + n * lateral, b + n * lateral
        if min(a2[0], b2[0]) - 1e-6 <= x <= max(a2[0], b2[0]) + 1e-6 and abs(b2[0] - a2[0]) > 1e-9:
            t = (x - a2[0]) / (b2[0] - a2[0]); y = a2[1] + t * (b2[1] - a2[1])
            return float(_prog[i] + t * _seg[i]), float(y)
    return None


def eje_local(p):
    """(x, y, azimut local en grados desde +x) del eje en la progresiva p."""
    p = min(max(p, 0.0), P_FIN)
    i = int(np.searchsorted(_prog, p, side="right") - 1); i = min(i, len(_seg) - 1)
    a, b = _P[i], _P[i + 1]; d = (b - a) / _seg[i]
    q = a + (p - _prog[i]) * d
    return (float(q[0]), float(q[1]), math.degrees(math.atan2(d[1], d[0])))


def prog_de(x, y):
    """Progresiva del eje mas cercana al punto (x, y) y distancia perpendicular con signo (+ hacia el predio, lado norte)."""
    best = None
    for i in range(len(_seg)):
        a, b = _P[i], _P[i + 1]; d = b - a
        t = float(np.clip(np.dot([x - a[0], y - a[1]], d) / np.dot(d, d), 0, 1)); q = a + t * d
        dist = float(np.hypot(x - q[0], y - q[1])); pr = float(_prog[i] + t * _seg[i])
        n = np.array([-d[1], d[0]]) / _seg[i]
        if n[1] < 0: n = -n
        sgn = 1.0 if np.dot([x - q[0], y - q[1]], n) >= 0 else -1.0
        if best is None or dist < abs(best[0]): best = (sgn * dist, pr)
    return best[1], best[0]


local_a_utm = _sol.local_a_utm
utm_a_local = _sol.utm_a_local
R01_UTM = _sol.R01_UTM; AZ_FRENTE = _sol.AZ_FRENTE

# ----------------------------------------------------------------------------- 2. zonas de carga
ZONAS = [dict(tipo="CAMION", p1=0.0, p2=round(D["porton_camiones"] + 0.30, 2), nombre="Porton de camiones cisterna (5.78 m)")]


def zona(p):
    for z in ZONAS:
        if z["p1"] <= p < z["p2"]: return z["tipo"]
    return "NORMAL"


# ----------------------------------------------------------------------------- 3. cunetas que llegan
_LEC = json.load(open(os.path.join(RAIZ, "insumos", "katiuska", "CUNETAS_CAR_VARONES_LEIDAS.json")))["ejes"]
_ej = {e["eje"]: e for e in _LEC}
# extremo dibujado de cada cuneta (marco de Solange) y franja tributaria (ancho en m a lo largo del frente)
_FIN = {"09": (349255.4, 9281954.0), "08": (349242.6, 9281949.3), "06": (349218.6, 9281938.9), "04": (349190.0, 9281923.6), "01": (349162.6, 9281915.1)}
_LIND_E = 349262.0; _LIND_O = X_NE
_xs = {k: v[0] for k, v in _FIN.items()}
_orden = sorted(_xs, key=lambda k: -_xs[k])          # de este a oeste: 09, 08, 06, 04, 01
_lim = [_LIND_E] + [(_xs[a] + _xs[b]) / 2 for a, b in zip(_orden[:-1], _orden[1:])] + [_LIND_O]
_anchos = {k: _lim[i] - _lim[i + 1] for i, k in enumerate(_orden)}
_W = sum(_anchos.values())
CUNETAS = []
for k in _orden:
    e = _ej[k]; x, y = _FIN[k]
    cv = cruce_vertical(x); pr = cv[0] if cv else prog_de(x, y)[0]; dist = y - cv[1] if cv else prog_de(x, y)[1]
    frac = _anchos[k] / _W
    c = dict(perfil=k, nombre="Eje %s" % k, x=x, y=y, L=e["L"], NCF=e["NCF_fin"], NCT=e["NPT"][-1], ancho=0.40,
             H=round(e["NPT"][-1] - e["NCF_fin"], 2), prog=round(pr, 2), dist_eje=round(dist, 2),
             franja_m=round(_anchos[k], 2), frac=frac, Q=round(D["Q_total"] * frac, 1), tapada_fin=e["tramos"][-1][0] == "cerrado")
    # la cuneta termina en la cara del muro del colector (lado predio): distancia desde su extremo dibujado
    cara_muro = D["b"] / 2 + D["e_muro"]           # 0.45 desde el eje
    c["entra_en"] = "colector"
    cvm = cruce_vertical(x, cara_muro)
    if cvm: dist = (y - cvm[1]) + cara_muro          # distancia vertical del extremo dibujado a la cara del muro (+ cara_muro para que ajuste = dist - cara_muro)
    if x > X_NE and pr > P_FIN - 0.5:
        # la cuneta cae sobre la CL de Solange: entra por la ventana del muro norte de la CL (cara exterior a 0.65 del eje)
        cara_muro = D["CL_ancho"] / 2 + D["e_muro"]; c["entra_en"] = "CL"; dist = y - Y_EJE_CL   # la cuneta baja en direccion N-S hasta el muro norte de la CL
        c["dist_eje"] = round(dist, 2)
    c["ajuste_L"] = round(dist - cara_muro, 2)      # positivo = prolongar hasta el muro, negativo = acortar (entra en el colector)
    c["prolong"] = max(c["ajuste_L"], 0.0)
    c["NCF_fin"] = round(c["NCF"] - 0.005 * c["ajuste_L"], 3)
    CUNETAS.append(c)
# ajuste para que la suma de caudales sea exactamente Q_total
_dq = D["Q_total"] - sum(c["Q"] for c in CUNETAS); CUNETAS[1]["Q"] = round(CUNETAS[1]["Q"] + _dq, 1)
CUNETAS.sort(key=lambda c: c["prog"])


def caudal_en(p):
    """Caudal (m3/s) en la progresiva p: suma de las cunetas que entran aguas arriba de p."""
    return sum(c["Q"] for c in CUNETAS if c["prog"] <= p + 1e-6 and c["entra_en"] == "colector") / 1000.0


# ----------------------------------------------------------------------------- 4. registros
REGISTROS = []
_r = 1
for c in CUNETAS:
    if c["prog"] < P_QUIEBRE - 1.0:
        REGISTROS.append(dict(nombre="RV-%02d" % _r, prog=c["prog"], tipo="registro", nota="empalme cuneta Eje %s" % c["perfil"])); _r += 1
# registros intermedios para no superar 12 m
_tmp = sorted(REGISTROS, key=lambda r: r["prog"]); _ad = []
_prev = 0.0
for r in _tmp + [dict(prog=P_QUIEBRE)]:
    gap = r["prog"] - _prev
    if gap > 12.0:
        n = int(math.ceil(gap / 12.0))
        for k in range(1, n):
            _ad.append(dict(nombre="", prog=round(_prev + gap * k / n, 2), tipo="registro", nota="limpieza"))
    _prev = r["prog"]
REGISTROS += _ad
REGISTROS.append(dict(nombre="", prog=round(P_QUIEBRE, 2), tipo="registro", nota="quiebre; inicio del tramo de empalme con la CL"))
REGISTROS.sort(key=lambda r: r["prog"])
for i, r in enumerate(REGISTROS): r["nombre"] = "RV-%02d" % (i + 1)
REGISTROS.append(dict(nombre="CL", prog=round(P_FIN, 2), tipo="caja de llegada", nota="cara este de la caja de llegada CL del colector del Hogar de Refugio (CUI 2675514); recibe tambien la cuneta Eje 01"))

# ----------------------------------------------------------------------------- 5. hidraulica
G = 9.81


def yn(Q, b, S, n=D["n"]):
    lo, hi = 1e-4, 5.0
    for _ in range(200):
        y = (lo + hi) / 2; A = b * y; R = A / (b + 2 * y)
        if A * R ** (2 / 3) * math.sqrt(S) / n > Q: hi = y
        else: lo = y
    return (lo + hi) / 2


def yc(Q, b):
    return (Q * Q / (G * b * b)) ** (1 / 3)


def fondo(p):
    return D["CF0"] - D["S"] * min(max(p, 0.0), P_FIN)


def ancho(p):
    return D["b"]


def losa_superior(p):
    """Cota de la cara superior de la losa (piso terminado)."""
    return D["NPT_empalme"] if p >= P_QUIEBRE - 1e-6 else D["NPT"]


def techo(p):
    """Cota inferior de la losa superior."""
    return losa_superior(p) - (D["e_losa_camion"] if zona(p) == "CAMION" else D["e_losa"])


def paso_estandar(estaciones, y_control):
    """Perfil subcritico de aguas abajo hacia aguas arriba con caudal variable por tramo (caudal_en)."""
    n = D["n"]; out = []
    p2 = estaciones[0]; y2 = y_control; b = D["b"]; z2 = fondo(p2); Q2 = caudal_en(p2)
    V2 = Q2 / (b * y2); E2 = z2 + y2 + V2 ** 2 / (2 * G); Sf2 = (n * V2 / ((b * y2) / (b + 2 * y2)) ** (2 / 3)) ** 2
    out.append(dict(p=p2, z=z2, b=b, y=y2, V=V2, Sf=Sf2, Q=Q2))
    for p1 in estaciones[1:]:
        dx = p2 - p1; z1 = fondo(p1); Q1 = caudal_en(p1)
        if Q1 <= 0:
            out.append(dict(p=p1, z=z1, b=b, y=0.0, V=0.0, Sf=0.0, Q=0.0)); p2, z2 = p1, z1; continue
        lo, hi = yc(Q1, b) * 1.001, 3.0
        for _ in range(100):
            y1 = (lo + hi) / 2; V1 = Q1 / (b * y1)
            Sf1 = (n * V1 / ((b * y1) / (b + 2 * y1)) ** (2 / 3)) ** 2
            f = (z1 + y1 + V1 ** 2 / (2 * G)) - (E2 + dx * (Sf1 + Sf2) / 2)
            if f > 0: hi = y1
            else: lo = y1
        y1 = (lo + hi) / 2; V1 = Q1 / (b * y1); Sf1 = (n * V1 / ((b * y1) / (b + 2 * y1)) ** (2 / 3)) ** 2
        out.append(dict(p=p1, z=z1, b=b, y=y1, V=V1, Sf=Sf1, Q=Q1))
        p2, y2, z2, E2, Sf2 = p1, y1, z1, z1 + y1 + V1 ** 2 / (2 * G), Sf1
    return out


def disenar():
    # caudal del colector = suma de las cunetas que entran al colector; el total que recibe la CL (colector + cuneta Eje 01
    # directa) es exactamente Q_total = 258.7 L/s (memoria de hidrologia de Varones, igual a lo citado en el expediente del Hogar de Refugio)
    Q = caudal_en(P_FIN); b = D["b"]
    res = dict(I=D["I"], Q=round(Q * 1000, 1), Q_CL=D["Q_total"], Q_directo_CL=round(sum(c["Q"] for c in CUNETAS if c["entra_en"] == "CL"), 1),
               Q_varones_calc=D["Q_total"], Q_refugio_calc=_sol.D["Q_refugio"])
    assert abs(res["Q"] + res["Q_directo_CL"] - D["Q_total"]) < 0.051
    res["yn"] = yn(Q, b, D["S"]); res["yc"] = yc(Q, b); res["V_n"] = Q / (b * res["yn"]); res["F_n"] = res["V_n"] / math.sqrt(G * res["yn"])
    # control aguas abajo: caida libre a la CL -> tirante critico en el fin del colector
    zB = fondo(P_FIN); yc_b = yc(Q, b)
    res["brink"] = dict(p=P_FIN, z=zB, yc=yc_b, NA=zB + yc_b)
    est = sorted(set(round(x, 2) for x in list(np.arange(0, P_FIN, 1.0)) + [P_FIN, P_QUIEBRE] + [c["prog"] for c in CUNETAS]
                     + [r["prog"] for r in REGISTROS if r["prog"] < P_FIN] + [z["p2"] for z in ZONAS]), reverse=True)
    perfil = paso_estandar(est, yc_b)
    for e in perfil:
        e["NA"] = e["z"] + e["y"]; e["F"] = (e["V"] / math.sqrt(G * e["y"])) if e["y"] > 0 else 0.0
        e["techo"] = techo(e["p"]); e["h"] = e["techo"] - e["z"]; e["llenado"] = e["y"] / e["h"]; e["BL"] = e["techo"] - e["NA"]
        e["zona"] = zona(e["p"]); e["ok"] = e["llenado"] <= D["llenado_max"] and e["BL"] >= D["BL_min"] and (e["F"] < 1 or abs(e["p"] - P_FIN) < 1e-6)
    res["perfil"] = perfil[::-1]
    # capacidad a seccion llena al 85 % en el tramo mas desfavorable (fin, h minima)
    hmin = min(e["h"] for e in perfil); y85 = 0.85 * hmin; A = b * y85; Rh = A / (b + 2 * y85)
    res["capacidad_85"] = dict(h=hmin, y=y85, Q=A * Rh ** (2 / 3) * math.sqrt(D["S"]) / D["n"] * 1000)
    # llegada a la CL de Solange: caida desde el fondo del colector hasta el piso de la poza y nivel de agua de la CL
    sol = json.load(open(os.path.join(RAIZ, "entregables", "_calc", "diseno.json")))
    NA_CL = sol["perfil"][0]["NA"]; D["CL_NA"] = NA_CL
    res["caja_llegada"] = dict(z_piso=D["CL_piso"], caida=zB - D["CL_piso"], NA_CL=NA_CL, caida_libre=zB - NA_CL, ventana_alfeizar=zB, ventana_ancho=b, ventana_alto=techo(P_FIN) - zB,
                               techo_CL=D["NPT_CL"] - _sol.D["e_losa"], x_cara_este=X_CL_ESTE)
    for c in CUNETAS:
        if c["entra_en"] == "CL":
            c["NA_colector"] = NA_CL; c["caida_libre"] = round(c["NCF_fin"] - NA_CL, 3); c["h_colector"] = round(D["NPT_CL"] - _sol.D["e_losa"] - D["CL_piso"], 3)
            c["H_ventana"] = round(D["NPT_CL"] - _sol.D["e_losa"] - c["NCF_fin"], 2)
    for c in CUNETAS:
        if c["entra_en"] == "CL": continue
        e = min(perfil, key=lambda e: abs(e["p"] - c["prog"]))
        c["NA_colector"] = e["NA"]; c["caida_libre"] = round(c["NCF_fin"] - e["NA"], 3); c["h_colector"] = round(e["h"], 3); c["H_ventana"] = round(e["techo"] - c["NCF_fin"], 2)
    res["cunetas"] = CUNETAS; res["registros"] = REGISTROS; res["zonas"] = ZONAS
    res["geom"] = dict(EJE=EJE, BORDE=BORDE, P_FIN=P_FIN, P_QUIEBRE=P_QUIEBRE, X_CL_ESTE=X_CL_ESTE, P_BRINK=P_BRINK, P_B1=P_B1, P_B2=P_B2, X_NE=X_NE, Y_CERCO=Y_CERCO, Y_EJE_CL=Y_EJE_CL, L_FRENTE=L_FRENTE, R01_UTM=R01_UTM, AZ_FRENTE=AZ_FRENTE)
    res["datos"] = D
    return res


def guardar(res, fn=os.path.join(CALC, "diseno.json")):
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    json.dump(res, open(fn, "w", encoding="utf8"), indent=1, ensure_ascii=False, default=float); return fn


if __name__ == "__main__":
    r = disenar()
    print("Q = %.1f L/s  yn = %.3f  yc = %.3f  V = %.2f  F = %.2f" % (r["Q"], r["yn"], r["yc"], r["V_n"], r["F_n"]))
    print("L = %.2f  quiebre/empalme 0+%06.2f  fin 0+%06.2f  zonas %s" % (P_FIN, P_QUIEBRE, P_FIN, ZONAS))
    print("eje:", [(round(x, 2), round(y, 2)) for x, y in EJE])
    print("%8s %8s %6s %7s %5s %5s %5s %6s %7s %6s" % ("prog", "fondo", "y", "NA", "V", "F", "h", "y/h", "BL", "Q"))
    for e in r["perfil"]:
        if abs(e["p"] - round(e["p"] / 10) * 10) < 0.01 or e["p"] in (P_QUIEBRE, P_FIN) or any(abs(e["p"] - c["prog"]) < 0.01 for c in CUNETAS):
            print("%8.2f %8.3f %6.3f %7.3f %5.2f %5.2f %5.2f %6.2f %7.3f %6.1f %s %s" % (e["p"], e["z"], e["y"], e["NA"], e["V"], e["F"], e["h"], e["llenado"], e["BL"], e["Q"] * 1000, e["zona"], "OK" if e["ok"] else "NO"))
    print("capacidad 85 %%: %.0f L/s (h min %.2f)" % (r["capacidad_85"]["Q"], r["capacidad_85"]["h"]))
    print("Q colector %.1f + directo a la CL %.1f = %.1f L/s" % (r["Q"], r["Q_directo_CL"], r["Q_CL"]))
    print("CL:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r["caja_llegada"].items()})
    for c in CUNETAS:
        print("  cuneta Eje %s prog %6.2f Q %5.1f NCF %.2f ajuste L %+.2f NA %.3f caida libre %.3f Hv %.2f entra en %s" % (c["perfil"], c["prog"], c["Q"], c["NCF_fin"], c["ajuste_L"], c["NA_colector"], c["caida_libre"], c["H_ventana"], c["entra_en"]))
    print("registros:", [(r_["nombre"], r_["prog"], r_["nota"][:30]) for r_ in REGISTROS])
    print(guardar(r))
