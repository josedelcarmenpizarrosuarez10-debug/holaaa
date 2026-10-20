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


# cerco perimetrico (aprox., del plano)
CERCO = [(354812.3, 9249854.6), (354843, 9249884), (354867, 9249855.6), (354917, 9249855.6), (354917, 9249868.5), (354980.3, 9249868.5),
         (354980.3, 9249785), (354975, 9249781.5), (354938, 9249789.4), (354910, 9249795), (354879, 9249801.3), (354858.6, 9249809.7)]


def pie(p, a, b):
    """Pie de la perpendicular de p sobre el segmento a-b."""
    ax, ay = a; bx, by = b; t = ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)
    return (ax + t * (bx - ax), ay + t * (by - ay))


def en_recta(a, b, x):
    return (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))


Y = 9249000.0
P = lambda x, y: (354000.0 + x, Y + y)
# --- nudos (coordenadas UTM del eje de la cuneta)
N = {
    "D1": P(812.50, 854.29), "A1": P(858.75, 810.03), "A2": P(879.05, 801.72), "A3": P(910.09, 795.53), "A4": P(918.70, 793.80),
    "E7": P(938.00, 789.90), "E0": P(979.50, 786.24), "E1": P(979.50, 833.66), "E2": P(979.50, 837.76), "D2": P(979.50, 860.50), "E3": P(979.50, 869.53),
    "G1": P(974.70, 782.60), "D4": P(969.77, 783.60),
    "W1a": P(853.10, 865.70), "W12": P(844.95, 857.55), "W13": P(838.81, 851.41), "W1b": P(830.70, 843.30),
    "W2a": P(867.80, 834.70), "W4a": P(876.10, 842.67), "W34": P(862.00, 828.20),
    "W3c": P(866.80, 823.40), "W3d": P(881.60, 817.40), "N885": P(885.10, 815.97),
    "X885a": P(884.91, 851.50), "X885b": P(884.91, 825.40),
    "X896a": P(896.84, 851.45), "X896b": P(896.84, 839.94), "X896c": P(896.84, 822.09), "X896d": P(896.84, 815.97),
    "X919a": P(919.61, 815.97), "X919b": P(919.61, 800.53),
    "X932a": P(932.64, 839.94), "X932b": P(932.64, 822.09), "X932c": P(932.64, 815.97),
    "X936a": P(936.52, 853.47), "X936b": P(936.52, 839.94), "Y853a": P(918.70, 853.47),
    "X937a": P(937.26, 815.97), "X937b": P(937.26, 804.40),
    "Y815e": P(935.26, 815.97), "X952a": P(952.32, 815.97), "X952b": P(952.32, 838.82), "X952c": P(952.32, 839.94),
    "X971a": P(971.71, 839.94), "X971b": P(971.71, 851.87), "C971": P(979.50, 851.87),
    "X948a": P(948.13, 838.82), "X948b": P(948.13, 851.87), "X948c": P(948.13, 853.47), "Y853b": P(941.39, 853.47), "Y853c": P(950.03, 853.47),
    "L1": P(955.92, 796.00), "L2": P(976.90, 796.00), "L3": P(976.90, 831.28), "L4": P(952.52, 831.28), "CL": P(979.50, 831.28),
}
N["C1"] = pie(N["W1b"], N["D1"], N["A1"])
N["J919"] = en_recta(N["A4"], N["E7"], N["X919a"][0])
N["D3"] = en_recta(N["A4"], N["E7"], 354924.97)               # punto bajo de la rasante del frente sur (183.25)
N["J937"] = en_recta(N["A4"], N["E7"], N["X937a"][0])

# --- ramales: (codigo, sistema, nudos en el sentido del flujo, descripcion). Todos empiezan con h = 0.30 m.
RAMALES = [
    # Sistema 1 - Oeste: descarga D1 (esquina oeste, terreno natural hacia la quebrada)
    ("R-01", 1, ["A2", "A1", "C1", "D1"], "Perimetral sur-oeste, junto al cerco"),
    ("R-02", 1, ["W1a", "W12", "W13", "W1b", "C1"], "Pabellones oeste: extremo nor-oeste del patio, empalma a R-01"),
    ("R-03", 1, ["W2a", "W12"], "Pabellones oeste: alero sur-oeste del pabellon norte"),
    ("R-04", 1, ["W4a", "W2a", "W34", "W13"], "Pabellones oeste: extremo sur-este del patio y alero nor-este del pabellon sur"),
    ("R-05", 1, ["X885a", "X885b", "N885", "W3d", "W3c", "W34"], "Bloque x=884.9 (lado oeste) y union al patio de pabellones oeste"),
    ("R-06", 1, ["X896d", "N885"], "Tramo y=815.97 entre x=896.8 y x=885.1"),
    # Sistema 2 - Sur: descarga D3 (frente sur, ingreso principal)
    ("R-07", 2, ["A2", "A3", "A4", "D3"], "Perimetral del frente sur, tramo oeste (baja a D3)"),
    ("R-23", 2, ["E7", "J937", "D3"], "Perimetral del frente sur, tramo este (baja a D3)"),
    ("R-08", 2, ["X896a", "X896b", "X896c", "X896d", "X919a", "X919b", "D3"], "Patio central: lado oeste, y=815.97 y bajada x=919.6 directa a D3"),
    ("R-09", 2, ["X932a", "X896b"], "Patio central: alero sur del pabellon norte (y=839.94)"),
    ("R-10", 2, ["X932b", "X896c"], "Patio central: y=822.09"),
    ("R-11", 2, ["Y853a", "X936a", "X936b", "X932a", "X932b", "X932c", "X919a"], "Bloque norte (alero sur), x=936.5, x=932.6 (muro de contencion) e y=815.97"),
    ("R-12", 2, ["X937a", "X937b", "J937"], "Bajada x=937.3 al frente sur"),
    # Sistema 3 - Nor-este: descarga D2 (esquina nor-este, quebrada)
    ("R-13", 3, ["E0", "CL", "E1", "E2", "C971", "D2"], "Perimetral este, junto al cerco"),
    ("R-22", 3, ["E3", "D2"], "Remate norte de la perimetral este (baja hacia la descarga)"),
    ("R-14", 3, ["L1", "L2", "L3", "CL"], "Losa deportiva: lados sur y este"),
    ("R-15", 3, ["L4", "L3"], "Losa deportiva: lado norte"),
    ("R-16", 3, ["Y815e", "X952a", "X952b", "X952c", "X971a", "X971b", "C971"], "Bloque nor-este: y=815.97, x=952.3, y=839.94, x=971.7"),
    ("R-17", 3, ["X948a", "X952b"], "Bloque nor-este: tramo y=838.8"),
    ("R-18", 3, ["X948a", "X948b", "X971b"], "Bloque nor-este: x=948.1 e y=851.87"),
    ("R-19", 3, ["Y853b", "X948c", "X948b"], "Bloque norte (alero sur, lado este) y x=948.1"),
    ("R-20", 3, ["Y853c", "X948c"], "Remate y=853.47 al este de x=948.1"),
    # Sistema 4 - Ingreso sur-este: descarga D4 (exterior)
    ("R-21", 4, ["G1", "D4"], "Cuneta transversal del ingreso sur-este"),
]
DESCARGAS = {"D1": "Esquina oeste: al terreno natural (quebrada al oeste / nor-oeste)",
             "D2": "Perimetral este, punto bajo (y = 860.5): a la cabecera de la quebrada del norte",
             "D3": "Frente sur, punto bajo (x = 925.0): al Jr. Alfonso Ugarte en su punto bajo (183.00) - confirmar evacuacion de la calle",
             "D4": "Ingreso sur-este: a la calzada del Jr. Alfonso Ugarte, que baja hacia su punto bajo"}

# tramos tapados que no salen de las veredas del plano: ingresos y conexiones nuevas (codigo, nudo a, nudo b, motivo)
TAPADOS_FIJOS = [("R-07", "A3", "A4", "Ingreso peatonal del frente sur"), ("R-13", "E1", "E2", "Ingreso vehicular este"),
                 ("R-02", "W1b", "C1", "Conexion nueva a la perimetral (cruza la vereda)"), ("R-08", "X919b", "D3", "Conexion nueva directa a D3 (cruza la vereda)"),
                 ("R-12", "X937b", "J937", "Conexion nueva al frente sur"), ("R-14", "L3", "CL", "Conexion nueva a la perimetral este"),
                 ("R-16", "X971b", "C971", "Conexion nueva a la perimetral este"), ("R-05", "X885b", "N885", "Conexion nueva x=884.9")]


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


def calcular():
    ras = rasante_fn(); ver = veredas()
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
            for i, p in enumerate(pts):
                if i == 0: v = r[0] - H0
                else: v = min(f[-1] - S0 * (s[i] - s[i - 1]), r[i] - HMIN)
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
            if n not in nombre: nombre[n] = n if n.startswith("D") else "P-%02d" % (1 + sum(1 for v in nombre.values() if v.startswith("P")))
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
