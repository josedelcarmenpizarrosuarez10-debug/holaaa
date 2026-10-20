"""Planteamiento preliminar de cunetas - I.E. N.° 0590, Barranquita (Lamas - San Martin).

Red de cunetas sobre los ejes del planteamiento preliminar del usuario (capa 0_ CUNETAS / 0_REJILLA del plano
PLANTA_GENERAL_590_2), con los sentidos de flujo, empalmes y descargas elegidos segun las curvas de nivel.

Criterios del usuario:
- Seccion: ancho total 0.60 m = muros de 0.10 m + 0.40 m libres.
- Profundidad al inicio de cada ramal 0.30 m (minima 0.25 m donde el terreno baja mas rapido que la cuneta).
- Pendiente de la cota de fondo 0.5 %; si el terreno cae mas, la cuneta lo acompana (h >= 0.25 m).
- Rejilla en los tramos abiertos; tramo tapado (losa) donde la cuneta cruza veredas o ingresos.
- Techos a dos aguas (cumbrera en el eje largo de cada bloque): cada alero descarga a la cuneta o al terreno de su lado.

Rasante (borde superior de la cuneta): dentro de la plataforma de los bloques NTN = +184.50 (rotulos NTN del plano);
dentro del cerco, el terreno de las curvas C-TOPO recortado a +184.50 (el monticulo de 185.5 se corta); fuera del cerco, el
terreno natural. En las conexiones nuevas (tramos cortos de relleno) la rasante va en linea recta entre sus extremos.
Uso: python3 herramientas/barranquita/diseno_b.py   -> entregables_barranquita/_calc/diseno.json
"""
import os, sys, json, math
import numpy as np
from matplotlib.path import Path
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import terreno_b as T

B_INT, E_MURO, B_TOT = 0.40, 0.10, 0.60
H0, HMIN, S0 = 0.30, 0.25, 0.005
NTN_PLAT = 184.50
N_MAN, BL = 0.013, 0.05                  # Manning (concreto) y borde libre para la capacidad
SAL = os.path.join(RAIZ, "entregables_barranquita", "_calc", "diseno.json")

# plataforma de los bloques (NTN +184.50)
PLAT = [(354827, 9249852), (354844, 9249875), (354878, 9249843.5), (354884, 9249853), (354917, 9249855.5), (354917, 9249867),
        (354950, 9249867), (354950, 9249854.5), (354973, 9249854.5), (354978.2, 9249840), (354978.2, 9249795), (354955, 9249795),
        (354950, 9249803), (354885, 9249803), (354872, 9249807), (354866, 9249811)]


# cerco perimetrico = limite de intervencion (capa 0 del plano PLANTA_GENERAL_590_2; confirmado por el usuario, C1..C22).
# Entre C11-C12 y C18-C19 el limite es la fachada del ingreso secundario y del ingreso principal.
CERCO_L = [(813.64, 855.63), (841.92, 883.91), (871.13, 854.70), (916.13, 854.70), (916.13, 869.58), (977.74, 869.58), (977.74, 785.21),
           (976.37, 784.10), (969.93, 785.38), (969.93, 791.81), (955.81, 791.81), (948.88, 794.19), (936.64, 794.19), (936.64, 792.02),
           (926.97, 793.95), (926.97, 800.53), (919.17, 800.53), (919.17, 802.42), (907.61, 802.61), (883.57, 802.61), (879.56, 803.41),
           (859.72, 811.52)]
CERCO = [(354000.0 + x, 9249000.0 + y) for x, y in CERCO_L]
D_CERCO = 0.60                            # eje de la cuneta perimetral a 0.60 m del cerco (borde exterior a 0.30 m)


def pie(p, a, b):
    """Pie de la perpendicular de p sobre el segmento a-b."""
    ax, ay = a; bx, by = b; t = ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)
    return (ax + t * (bx - ax), ay + t * (by - ay))


def en_recta(a, b, x):
    return (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))


def offset_cerco(d=D_CERCO):
    """Vertices del cerco desplazados d hacia adentro (interseccion de los lados desplazados)."""
    n = len(CERCO); A = abs(sum(CERCO[i][0] * CERCO[(i + 1) % n][1] - CERCO[(i + 1) % n][0] * CERCO[i][1] for i in range(n))) / 2
    sg = 1 if sum(CERCO[i][0] * CERCO[(i + 1) % n][1] - CERCO[(i + 1) % n][0] * CERCO[i][1] for i in range(n)) > 0 else -1
    lin = []
    for i in range(n):
        a, b = CERCO[i], CERCO[(i + 1) % n]; L = math.dist(a, b); u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
        nn = (-u[1] * sg, u[0] * sg)                        # normal hacia adentro
        lin.append(((a[0] + nn[0] * d, a[1] + nn[1] * d), u))
    out = []
    for i in range(n):
        (p1, u1), (p2, u2) = lin[i - 1], lin[i]
        den = u1[0] * u2[1] - u1[1] * u2[0]
        if abs(den) < 1e-9: out.append(p2); continue
        t = ((p2[0] - p1[0]) * u2[1] - (p2[1] - p1[1]) * u2[0]) / den
        out.append((p1[0] + t * u1[0], p1[1] + t * u1[1]))
    return out                                               # out[i] = vertice interior junto a C(i+1)


Y = 9249000.0
P = lambda x, y: (354000.0 + x, Y + y)
O = offset_cerco()
OC = lambda k: O[k - 1]                                      # vertice interior junto a Ck
# --- nudos (coordenadas UTM del eje de la cuneta)
N = {
    "W1a": P(853.10, 865.70), "W12": P(844.95, 857.55), "W13": P(838.81, 851.41), "W1b": P(830.70, 843.30),
    "W2a": P(867.80, 834.70), "W4a": P(876.10, 842.67), "W34": P(862.00, 828.20),
    "W3c": P(866.80, 823.40), "W3d": P(881.60, 817.40), "N885": P(885.10, 815.97),
    "X885a": P(884.91, 851.50), "X885b": P(884.91, 825.40),
    "X896a": P(896.84, 851.45), "X896b": P(896.84, 839.94), "X896c": P(896.84, 822.09), "X896d": P(896.84, 815.97),
    "X919a": P(919.61, 815.97), "X919b": P(919.61, 800.53 + D_CERCO), "K1": P(926.97 + D_CERCO, 800.53 + D_CERCO),
    "X932a": P(932.64, 839.94), "X932b": P(932.64, 822.09), "X932c": P(932.64, 815.97),
    "X936a": P(936.52, 853.47), "X936b": P(936.52, 839.94), "Y853a": P(918.70, 853.47),
    "X937a": P(937.26, 815.97), "X937b": P(937.26, 804.40), "K2": P(937.26, 795.10),
    "Y815e": P(935.26, 815.97), "X952a": P(952.32, 815.97), "X952b": P(952.32, 838.82), "X952c": P(952.32, 839.94),
    "X971a": P(971.71, 839.94), "X971b": P(971.71, 851.87),
    "X948a": P(948.13, 838.82), "X948b": P(948.13, 851.87), "X948c": P(948.13, 853.47), "Y853b": P(941.39, 853.47), "Y853c": P(950.03, 853.47),
    "L1": P(955.92, 796.00), "L2": P(976.90, 796.00), "L3": P(976.90, 831.28), "L4": P(952.52, 831.28),
    "E0": P(976.90, 786.30), "Q1": P(976.90, 851.87), "Q2": P(976.90, 860.50), "Q3": P(968.00, 869.58 - D_CERCO),
    "D2n": P(965.50, 869.58 - D_CERCO), "D2": P(965.50, 869.58),
    "S19": OC(19), "S20": OC(20), "S21": OC(21), "S22": OC(22),
}
# perimetral sur-oeste: sale por el cerco donde el talud exterior cae mas rapido (lado C22-C1, a 54 m de C22)
_a, _b = OC(22), OC(1); _L = math.dist(_a, _b); _u = ((_b[0] - _a[0]) / _L, (_b[1] - _a[1]) / _L)
N["D1n"] = (_a[0] + _u[0] * 54.0, _a[1] + _u[1] * 54.0)
N["D1"] = pie(N["D1n"], CERCO[21], CERCO[0])
N["C1"] = pie(N["W1b"], OC(22), N["D1n"])
# frente sur: sale por el cerco entre C14 y C15 junto a C14 (x = 935.5), donde el terreno exterior cae hacia la calle
N["D3"] = en_recta(CERCO[13], CERCO[14], 354935.50)
_u = (CERCO[14][0] - CERCO[13][0], CERCO[14][1] - CERCO[13][1]); _L = math.hypot(*_u)
N["D3n"] = (N["D3"][0] + _u[1] / _L * D_CERCO, N["D3"][1] - _u[0] / _L * D_CERCO)
N["F1"] = (N["K1"][0], en_recta(OC(15), OC(14), N["K1"][0])[1])
N["K3"] = (N["D3n"][0], N["K2"][1])                           # quiebre para no cortar la esquina C13 del cerco

# --- ramales: (codigo, sistema, nudos en el sentido del flujo, descripcion). Todos empiezan con h = 0.30 m.
# Todo dentro del cerco; el ultimo tramo de cada descarga (Dn -> D) es el paso por el cerco.
RAMALES = [
    # Sistema 1 - Oeste: descarga D1 (cerco junto a la esquina oeste C1, terreno exterior hacia la quebrada)
    ("R-01", 1, ["S19", "S20", "S21", "S22", "C1", "D1n", "D1"], "Perimetral sur-oeste por dentro del cerco (C19 a C1)"),
    ("R-02", 1, ["W1a", "W12", "W13", "W1b", "C1"], "Pabellones oeste: extremo nor-oeste del patio, empalma a R-01"),
    ("R-03", 1, ["W2a", "W12"], "Pabellones oeste: alero sur-oeste del pabellon norte"),
    ("R-04", 1, ["W4a", "W2a", "W34", "W13"], "Pabellones oeste: extremo sur-este del patio y alero nor-este del pabellon sur"),
    ("R-05", 1, ["X885a", "X885b", "N885", "W3d", "W3c", "W34"], "Bloque x=884.9 (lado oeste) y union al patio de pabellones oeste"),
    ("R-06", 1, ["X896d", "N885"], "Tramo y=815.97 entre x=896.8 y x=885.1"),
    # Sistema 2 - Frente sur: descarga D3 (cerco sur entre C15 y C14, hacia el Jr. Alfonso Ugarte)
    ("R-07", 2, ["X896a", "X896b", "X896c", "X896d", "X919a", "X919b", "K1", "F1", "D3n", "D3"], "Patio central (x=896.8, y=815.97), bajada x=919.6 y atrio de ingreso a D3"),
    ("R-08", 2, ["X932a", "X896b"], "Patio central: alero sur del pabellon norte (y=839.94)"),
    ("R-09", 2, ["X932b", "X896c"], "Patio central: y=822.09"),
    ("R-10", 2, ["Y853a", "X936a", "X936b", "X932a", "X932b", "X932c", "X919a"], "Bloque norte (alero sur), x=936.5, x=932.6 (muro de contencion) e y=815.97"),
    ("R-11", 2, ["X937a", "X937b", "K2", "K3", "D3n"], "Bajada x=937.3 por el atrio de ingreso a D3"),
    # Sistema 3 - Nor-este: descarga D2 (cerco norte, x = 965.5, hondonada que baja a la quebrada)
    ("R-12", 3, ["E0", "L2", "L3", "Q1", "Q2", "Q3", "D2n", "D2"], "Perimetral este por dentro del cerco (x=976.9) y salida al cerco norte"),
    ("R-13", 3, ["L1", "L2"], "Losa deportiva: lado sur"),
    ("R-14", 3, ["L4", "L3"], "Losa deportiva: lado norte"),
    ("R-15", 3, ["Y815e", "X952a", "X952b", "X952c", "X971a", "X971b", "Q1"], "Bloque nor-este: y=815.97, x=952.3, y=839.94, x=971.7"),
    ("R-16", 3, ["X948a", "X952b"], "Bloque nor-este: tramo y=838.8"),
    ("R-17", 3, ["X948a", "X948b", "X971b"], "Bloque nor-este: x=948.1 e y=851.87"),
    ("R-18", 3, ["Y853b", "X948c", "X948b"], "Bloque norte (alero sur, lado este) y x=948.1"),
    ("R-19", 3, ["Y853c", "X948c"], "Remate y=853.47 al este de x=948.1"),
]
POZA = {"D2"}                                                 # descargas con poza de salida (rebalse a nivel del terreno)
POZA_DIM = (0.80, 0.80)                                       # poza: ancho y largo interior (m), fondo a la cota de fondo de llegada
DIR_SALIDA = {"D2": (-0.6, 0.8)}                              # D2: el fondo de la hondonada exterior baja hacia el nor-oeste
DESCARGAS = {"D1": "Cerco sur-oeste (lado C22-C1, x = 820.7): al talud natural que baja a la quebrada del oeste",
             "D2": "Cerco norte (x = 965.5): poza de salida que rebalsa a nivel del fondo de la hondonada natural (baja a la quebrada del norte)",
             "D3": "Cerco sur junto a C14 (x = 935.5): al terreno exterior que baja al Jr. Alfonso Ugarte (183.00)"}

# tramos tapados que no salen de las veredas del plano: ingresos y conexiones nuevas (codigo, nudo a, nudo b, motivo)
TAPADOS_FIJOS = [("R-02", "W1b", "C1", "Conexion nueva a la perimetral (cruza la vereda)"),
                 ("R-07", "X919b", "D3", "Atrio del ingreso principal y paso por el cerco"),
                 ("R-11", "X937b", "D3n", "Atrio del ingreso principal"),
                 ("R-12", "Q2", "D2", "Patio pavimentado del nor-este y paso por el cerco"),
                 ("R-15", "X971b", "Q1", "Conexion nueva a la perimetral este"), ("R-05", "X885b", "N885", "Conexion nueva x=884.9"),
                 ("R-01", "D1n", "D1", "Paso por el cerco")]


def plataforma():
    return Path(PLAT)


def rasante_fn():
    z = T.modelo(); pl = plataforma(); ce = Path(CERCO)
    def ras(x, y):
        if pl.contains_point((x, y)): return NTN_PLAT
        if ce.contains_point((x, y)): return min(z(x, y), NTN_PLAT)
        return z(x, y)
    return ras


def veredas():
    G = T.cargar(); out = []
    for capa in ("0_VEREDAS",):
        for pts, cl, b in G["geo"].get(capa, []):
            if cl and len(pts) > 3 and 354800 < pts[0][0] < 355000 and 9249770 < pts[0][1] < 9249890:
                out.append(Path([(p[0], p[1]) for p in pts]))
    return out


def q_manning(h, s):
    y = max(h - BL, 0.01); A = B_INT * y; Pm = B_INT + 2 * y; R = A / Pm
    return A * R ** (2 / 3) * math.sqrt(s) / N_MAN


HREQ = os.path.join(os.path.dirname(SAL), "hmin_req.json")


def hmin_tramos():
    """Profundidad minima por tramo exigida por la capacidad (tirante normal + borde libre), de verifica_b.py."""
    return json.load(open(HREQ)) if os.path.exists(HREQ) else {}


def calcular():
    ras = rasante_fn(); ver = veredas(); hq = hmin_tramos()
    # puntos cada 0.5 m de cada ramal
    geo = {}
    for cod, sis, nudos, desc in RAMALES:
        pts = []
        for i in range(len(nudos) - 1):
            a, b = N[nudos[i]], N[nudos[i + 1]]; L = math.dist(a, b); n = max(1, int(math.ceil(L / 0.5)))
            for k in range(n + (1 if i == len(nudos) - 2 else 0)):
                t = k / n; pts.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]), nudos[i] if k == 0 else (nudos[i + 1] if k == n else None)))
        s = [0.0]
        for i in range(1, len(pts)): s.append(s[-1] + math.dist(pts[i - 1][:2], pts[i][:2]))
        r = [ras(p[0], p[1]) for p in pts]
        for c, a, b, mot in TAPADOS_FIJOS:              # conexiones nuevas: rasante recta entre extremos (relleno)
            if c == cod and mot.startswith("Conexion"):
                ia = [i for i, p in enumerate(pts) if p[2] == a][0]; ib = [i for i, p in enumerate(pts) if p[2] == b][-1]
                for i in range(ia + 1, ib): r[i] = r[ia] + (r[ib] - r[ia]) * (s[i] - s[ia]) / (s[ib] - s[ia])
        geo[cod] = (pts, s, r)
    # cota de fondo: iteracion hasta que los empalmes queden por debajo de los ramales que llegan
    req = {}                                          # cota maxima admisible en cada nudo (por los ramales que llegan)
    for it in range(50):
        fondo, cambio = {}, False
        for cod, sis, nudos, desc in RAMALES:
            pts, s, r = geo[cod]; f = []
            hm = []; j = -1                                # profundidad minima de cada punto (0.25 o la del tramo)
            for i, p in enumerate(pts):
                if p[2] and i < len(pts) - 1: j += 1
                req_j = hq.get("%s|%s|%s" % (cod, nudos[j], nudos[j + 1]), HMIN)
                if p[2] and i > 0: req_j = max(req_j, hq.get("%s|%s|%s" % (cod, nudos[j - 1], nudos[j]), HMIN) if j > 0 else HMIN)
                hm.append(max(HMIN, req_j))
            for i, p in enumerate(pts):
                if i == 0: v = r[0] - H0
                else: v = min(f[-1] - S0 * (s[i] - s[i - 1]), r[i] - hm[i])
                if p[2] and i > 0 and p[2] in req: v = min(v, req[p[2]])
                f.append(v)
            fondo[cod] = f
        for cod, sis, nudos, desc in RAMALES:          # el ramal llega a su nudo final por encima de la cota del que lo recibe
            fin = nudos[-1]; v = fondo[cod][-1]
            for c2, s2, n2, d2 in RAMALES:
                if c2 != cod and fin in n2[1:]:
                    k = [i for i, p in enumerate(geo[c2][0]) if p[2] == fin][0]
                    if fondo[c2][k] > v + 1e-6:
                        req[fin] = min(req.get(fin, 9e9), v); cambio = True
        if not cambio: break
    nombre = {}                                      # P-01, P-02, ... en el orden de los ramales; descargas D1..D4
    for cod, sis, nudos, desc in RAMALES:
        for n in nudos:
            if n not in nombre: nombre[n] = n if n in DESCARGAS else "P-%02d" % (1 + sum(1 for v in nombre.values() if v.startswith("P")))
    res = {"criterios": {"b_int": B_INT, "muro": E_MURO, "b_tot": B_TOT, "h0": H0, "hmin": HMIN, "S": S0, "ntn_plataforma": NTN_PLAT,
                         "n_manning": N_MAN, "borde_libre": BL},
           "nudos": {k: [round(v[0], 3), round(v[1], 3)] for k, v in N.items() if k in nombre}, "nombre": nombre, "descargas": DESCARGAS, "ramales": []}
    for cod, sis, nudos, desc in RAMALES:
        pts, s, r = geo[cod]; f = fondo[cod]
        # tapados: puntos dentro de veredas o en los tramos fijos
        tap = [any(v.contains_point(p[:2]) for v in ver) for p in pts]
        for c, a, b, mot in TAPADOS_FIJOS:
            if c == cod:
                ia = [i for i, p in enumerate(pts) if p[2] == a][0]; ib = [i for i, p in enumerate(pts) if p[2] == b][-1]
                for i in range(ia, ib + 1): tap[i] = True
        tramos = []
        idx = [i for i, p in enumerate(pts) if p[2]]
        for j in range(len(idx) - 1):
            i0, i1 = idx[j], idx[j + 1]; L = s[i1] - s[i0]
            ltap = sum(s[i + 1] - s[i] for i in range(i0, i1) if tap[i] and tap[i + 1])
            S = (f[i0] - f[i1]) / L if L > 0 else 0
            hmax = max(r[i] - f[i] for i in range(i0, i1 + 1))
            tramos.append({"de": pts[i0][2], "a": pts[i1][2], "L": round(L, 2), "ras_de": round(r[i0], 3), "ras_a": round(r[i1], 3),
                           "cf_de": round(f[i0], 3), "cf_a": round(f[i1], 3), "h_de": round(r[i0] - f[i0], 3), "h_a": round(r[i1] - f[i1], 3),
                           "S": round(S, 5), "h_max": round(hmax, 3), "L_tapado": round(ltap, 2), "L_rejilla": round(L - ltap, 2),
                           "Q_cap": round(q_manning(min(r[i0] - f[i0], r[i1] - f[i1]), max(S, S0)), 4)})
        # perfil (cada 0.5 m) para los planos
        tap_iv = []; i = 0
        while i < len(pts):
            if tap[i]:
                j = i
                while j + 1 < len(pts) and tap[j + 1]: j += 1
                if s[j] - s[i] > 0.4: tap_iv.append([round(s[i], 2), round(s[j], 2)])
                i = j + 1
            else: i += 1
        res["ramales"].append({"codigo": cod, "sistema": sis, "nudos": nudos, "descripcion": desc, "L": round(s[-1], 2),
                               "tramos": tramos, "tapados": tap_iv,
                               "perfil": [[round(s[i], 2), round(r[i], 3), round(f[i], 3)] for i in range(len(pts))]})
    return res


def main():
    res = calcular()
    os.makedirs(os.path.dirname(SAL), exist_ok=True)
    json.dump(res, open(SAL, "w"), indent=1, ensure_ascii=False)
    Lt = sum(r["L"] for r in res["ramales"]); Ltap = sum(t["L_tapado"] for r in res["ramales"] for t in r["tramos"])
    for r in res["ramales"]:
        t0, t1 = r["tramos"][0], r["tramos"][-1]
        print("%s S%d L=%6.2f  CF %.3f (h %.2f) -> %.3f (h %.2f)  hmax %.2f  tapado %.1f" % (
            r["codigo"], r["sistema"], r["L"], t0["cf_de"], t0["h_de"], t1["cf_a"], t1["h_a"], max(t["h_max"] for t in r["tramos"]),
            sum(t["L_tapado"] for t in r["tramos"])))
    print("longitud total %.1f m, tapado %.1f m, con rejilla %.1f m" % (Lt, Ltap, Lt - Ltap)); print(SAL)


if __name__ == "__main__":
    main()
