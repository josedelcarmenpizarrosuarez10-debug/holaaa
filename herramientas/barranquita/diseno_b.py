"""Planteamiento preliminar de cunetas - I.E. N.° 0590, Barranquita (Lamas - San Martin).

Red de cunetas sobre las lineas magenta que el usuario trazo en el plano "PLANTA_GENERAL_590 ULTIMA VERSION" a los lados de
cada edificacion (techos a dos aguas: canaleta y cuneta a ambos lados), unidas hasta descargas por gravedad en el cerco
perimetrico (limite de intervencion: ninguna obra fuera del cerco). Sentidos de flujo y descargas segun las curvas de nivel.

Criterios del usuario:
- Seccion: ancho total 0.60 m = muros de 0.10 m + 0.40 m libres.
- Profundidad al inicio de cada ramal 0.30 m (minima 0.25 m donde el terreno baja mas rapido que la cuneta).
- Pendiente de la cota de fondo 0.5 %; si el terreno cae mas, la cuneta lo acompana (h >= 0.25 m).
- Rejilla en los tramos abiertos; tramo tapado (losa) donde la cuneta cruza veredas o ingresos.
- Techos a dos aguas (cumbrera en el eje largo de cada bloque): cada alero descarga a la cuneta o al terreno de su lado.

Niveles (indicacion del usuario, 20-10-2026): todo el interior del cerco queda nivelado, sin hondonadas. Pisos y pasadizos
NPT +184.65; borde superior de las cunetas (rasante) +184.65, al ras del piso (junta asfaltica al mismo nivel); areas verdes
+184.60. Fuera del cerco, el terreno natural de
las curvas C-TOPO. Con la rasante horizontal, la profundidad crece con la pendiente de fondo de 0.5 %.
Excepcion: el PATIO DE MANIOBRA Y ESTACIONAMIENTO (nor-este, 470 m2) queda en su nivel del plano NTN +184.50; las cunetas que lo
bordean van al ras del patio (+184.50), con rejilla en los tramos abiertos para que el agua del patio entre por ella.
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
E_TAPA = 0.10                          # losa de los tramos tapados: la altura libre bajo la losa no baja de HMIN
H_ACERO = 0.40                         # con h >= 0.40 m (rejilla - fondo) la cuneta lleva acero; menor, concreto simple (salvo tapadas)
NPT, RASANTE, NIVEL_AV = 184.65, 184.65, 184.60   # pisos y pasadizos, borde de cuneta (al ras del piso), areas verdes
NTN_PLAT = RASANTE                         # nivel del terreno terminado junto a la cuneta (dentro del cerco)
NIVEL_PATIO, RAS_PATIO = 184.50, 184.50    # patio de maniobra (NTN del plano); cunetas al ras del patio
# patio de maniobra y estacionamiento: entre la losa (y = 831.3), el cerco este, el cerco norte y x = 951.5; incluye los ejes de
# las cunetas que lo bordean (lado norte de la losa, lados sur y norte del bloque nor-este, cerco este y cerco norte hasta D2)
PATIO = [(354000.0 + x, 9249000.0 + y) for x, y in ((951.5, 830.8), (977.5, 830.8), (977.5, 869.6), (951.5, 869.6))]
N_MAN, BL = 0.013, 0.05                  # Manning (concreto) y borde libre para la capacidad
SAL = os.path.join(RAIZ, "entregables_barranquita", "_calc", "diseno.json")

# plataforma de los bloques (NTN +184.50)
PLAT = [(354827, 9249852), (354844, 9249875), (354878, 9249843.5), (354884, 9249853), (354917, 9249855.5), (354917, 9249867),
        (354950, 9249867), (354950, 9249854.5), (354973, 9249854.5), (354978.2, 9249840), (354978.2, 9249795), (354952.5, 9249795),
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
# --- nudos (coordenadas UTM del eje de la cuneta). Los ejes son las lineas magenta del plano "ULTIMA VERSION" (lados de cada
# edificacion: techos a dos aguas, canaleta a ambos lados); los demas nudos son las uniones hasta las descargas.
N = {
    # pabellones oeste A (lineas 0, 1), B (2, 5), C (3, 4) y bloque D (6, 7)
    "A0": P(844.67, 873.87), "A1": P(822.02, 851.41), "B5a": P(876.15, 842.90),
    "W1a": P(853.10, 865.70), "W12": P(844.95, 857.55), "W13": P(838.81, 851.41), "W1b": P(830.70, 843.30),
    "W2a": P(867.80, 834.70), "W34": P(862.00, 828.20),
    "W3c": P(866.80, 823.40), "W3d": P(881.60, 817.40), "N885": P(885.10, 815.97),
    "T29e": P(906.62, 804.22), "T29w": P(885.30, 804.18), "T7e": P(879.56, 805.51), "T7w": P(863.11, 812.40), "T4s": P(858.19, 815.42),
    # bloques del centro (lineas 8 a 11, 16, 17, 20, 21, 26, 28, 29)
    "X885a": P(884.91, 851.50), "X885b": P(884.91, 825.40),
    "X896a": P(896.84, 851.45), "X896b": P(896.84, 839.94), "X896c": P(896.84, 822.09), "X896d": P(896.84, 815.97),
    "X919a": P(919.61, 815.97), "X919c": P(919.61, 804.20), "X919b": P(919.61, 800.53 + D_CERCO), "K1": P(926.97 + D_CERCO, 800.53 + D_CERCO),
    "X932a": P(932.64, 839.94), "X932b": P(932.64, 822.09), "X932c": P(932.64, 815.97),
    "X936b": P(936.52, 839.94), "T17n": P(936.47, 851.69), "T11w": P(897.16, 851.69), "J11": P(911.00, 851.69),
    "T28e": P(949.97, 804.09),
    # bloque norte (lineas 12, 13)
    "Y853c": P(950.03, 853.47), "J4": P(911.00, 853.60),
    "T12w": P(918.93, 865.08), "T12e": P(950.13, 865.08), "T12k": P(950.60, 869.58 - D_CERCO),
    # bloque nor-este y losa (lineas 14, 15, 18, 19, 22 a 25, 27)
    "Y815e": P(935.26, 815.97), "X952a": P(952.32, 815.97), "X952b": P(952.32, 838.82), "X952c": P(952.32, 839.94),
    "X971a": P(971.71, 839.94), "X971b": P(971.71, 851.87), "X948a": P(948.13, 838.82), "X948b": P(948.13, 851.87),
    "T22w": P(953.20, 796.03), "T25n": P(953.10, 811.69),
    "L2": P(976.90, 796.00), "L3": P(976.90, 831.28), "L4": P(952.52, 831.28),
    "Q0": P(976.90, 839.94), "Q1": P(976.90, 851.87), "Q2": P(976.90, 860.50), "Q3": P(968.00, 869.58 - D_CERCO),
    "D2n": P(965.50, 869.58 - D_CERCO), "D2": P(965.50, 869.58),
}
# D1: pase por el cerco sur-oeste (lado C22-C1) frente al extremo de la linea 0, donde el talud exterior cae rapido
N["D1"] = pie(N["A1"], CERCO[21], CERCO[0])
_u = np.subtract(N["A1"], N["D1"]); _u = _u / np.linalg.norm(_u)
N["D1n"] = (N["D1"][0] + _u[0] * D_CERCO, N["D1"][1] + _u[1] * D_CERCO)
# D3: frente sur, cerco entre C14 y C15 junto a C14 (x = 935.5), donde el terreno exterior cae hacia la calle
N["D3"] = en_recta(CERCO[13], CERCO[14], 354935.50)
_u = (CERCO[14][0] - CERCO[13][0], CERCO[14][1] - CERCO[13][1]); _L = math.hypot(*_u)
N["D3n"] = (N["D3"][0] + _u[1] / _L * D_CERCO, N["D3"][1] - _u[0] / _L * D_CERCO)
N["F1"] = (N["K1"][0], en_recta(OC(15), OC(14), N["K1"][0])[1])
# D4: cerco norte (lado C3-C4, y = 854.70) entre el bloque norte y el bloque del centro, sobre el talud de la quebrada
N["D4"] = en_recta(CERCO[2], CERCO[3], 354911.00)
N["D4n"] = (N["D4"][0], N["D4"][1] - D_CERCO)

# --- ramales: (codigo, sistema, nudos en el sentido del flujo, descripcion). Todos empiezan con h = 0.30 m.
# Todo dentro del cerco; el ultimo tramo de cada descarga (Dn -> D) es el paso por el cerco.
RAMALES = [
    # Sistema 1 - Oeste: descarga D1 (cerco sur-oeste, talud hacia la quebrada del oeste)
    ("EJE-01", 1, ["A0", "A1", "D1n"], "Pabellon oeste A: lado nor-oeste; entrega al EJE-02 junto al cerco (caida)"),
    ("EJE-02", 1, ["B5a", "W1a", "W12", "W13", "W1b", "D1n", "D1"], "Pabellon oeste B: lado nor-este; pabellon A: lado sur-este; salida D1"),
    ("EJE-03", 1, ["W2a", "W12"], "Pabellon oeste B: lado sur-oeste (patio)"),
    ("EJE-04", 1, ["X885a", "X885b", "N885", "W3d", "W3c", "W34", "W13"], "Bloque x=884.9 (lado oeste), bloque D (lado norte) y pabellon C (lado nor-este)"),
    ("EJE-05", 1, ["T29e", "T29w", "T7e", "T7w", "T4s", "W1b"], "Bloque del ingreso (lado sur), bloque D (lado sur) y pabellon C (lado sur-oeste)"),
    ("EJE-06", 1, ["X896d", "N885"], "Bloque del ingreso: lado norte (y=815.97) al oeste de x=896.8"),
    # Sistema 2 - Centro y frente sur: descarga D3 (cerco sur junto a C14, hacia el Jr. Alfonso Ugarte)
    ("EJE-07", 2, ["X896a", "X896b", "X896c", "X896d", "X919a", "X919c", "X919b", "K1", "F1", "D3n", "D3"], "Patio central (x=896.8), y=815.97, bajada x=919.6 y atrio de ingreso a D3"),
    ("EJE-08", 2, ["X936b", "X932a", "X896b"], "Bloque del centro: lado sur (y=839.94)"),
    ("EJE-09", 2, ["X932b", "X896c"], "Patio central: y=822.09"),
    ("EJE-10", 2, ["X932a", "X932b", "X932c", "X919a"], "x=932.6 y bloque del frente: lado norte (y=815.97)"),
    ("EJE-11", 2, ["T28e", "X919c"], "Bloque del frente: lado sur (y=804.1)"),
    # Sistema 3 - Nor-este: descarga D2 (pase en el cerco norte, x = 965.5, hacia la hondonada natural exterior)
    ("EJE-12", 3, ["T25n", "T22w", "L2", "L3", "Q0", "Q1", "Q2", "Q3", "D2n", "D2"], "Losa: lados oeste, sur y este; union por dentro del cerco a D2"),
    ("EJE-13", 3, ["L4", "L3"], "Losa: lado norte (y=831.3)"),
    ("EJE-14", 3, ["Y815e", "X952a", "X952b", "X952c", "X971a", "Q0"], "y=815.97, x=952.3 y bloque nor-este: lado sur (y=839.9)"),
    ("EJE-15", 3, ["X948a", "X948b", "X971b", "Q1"], "Bloque nor-este: lado oeste (x=948.1) y lado norte (y=851.9)"),
    ("EJE-16", 3, ["T12w", "T12e", "T12k", "D2n"], "Bloque norte: lado norte (y=865.1) y union a D2 por el norte de la planta de tratamiento"),
    # Sistema 4 - Norte: descarga D4 (cerco norte, x = 911.0, talud de la quebrada del norte)
    ("EJE-17", 4, ["Y853c", "J4", "D4n", "D4"], "Bloque norte: lado sur (y=853.5) y salida D4"),
    ("EJE-18", 4, ["X936b", "T17n", "J11", "J4"], "Bloque del centro: lado este (x=936.5) y lado norte (y=851.7), tramo este"),
    ("EJE-19", 4, ["T11w", "J11"], "Bloque del centro: lado norte (y=851.7), tramo oeste"),
]
# sistemas: nombre y descarga (los colores de cada sistema estan en planos_b.py e iso_b.py)
SISTEMAS = {1: ("OESTE", "D1"), 2: ("CENTRO Y FRENTE SUR", "D3"), 3: ("NOR-ESTE Y LOSA", "D2"), 4: ("NORTE", "D4")}
POZA = set()                                                  # interior nivelado: D2 tambien es pase en el cimiento (sin poza)
POZA_DIM = (0.80, 0.80)                                       # poza: ancho y largo interior (m), fondo a la cota de fondo de llegada
DIR_SALIDA = {"D2": (-0.6, 0.8)}                              # D2: el fondo de la hondonada exterior baja hacia el nor-oeste
DESCARGAS = {"D1": "Cerco sur-oeste (lado C22-C1, x = %.1f): al talud natural que baja a la quebrada del oeste" % (N["D1"][0] - 354000),
             "D2": "Cerco norte (x = 965.5): pase en el cimiento del cerco al terreno exterior que baja a la quebrada del norte",
             "D3": "Cerco sur junto a C14 (x = 935.5): al terreno exterior que baja al Jr. Alfonso Ugarte (183.00)",
             "D4": "Cerco norte (lado C3-C4, x = 911.0): al talud natural que baja a la quebrada del norte"}

# tramos tapados que no salen de las veredas del plano: ingresos y pases por el cerco (codigo, nudo a, nudo b, motivo)
TAPADOS_FIJOS = [("EJE-07", "X919b", "D3", "Atrio del ingreso principal y paso por el cerco"),
                 ("EJE-12", "Q2", "D2", "Patio pavimentado del nor-este y paso por el cerco"),
                 ("EJE-02", "D1n", "D1", "Paso por el cerco"), ("EJE-17", "D4n", "D4", "Paso por el cerco")]
# uniones nuevas (no son lados de edificacion): rasante en linea recta entre sus extremos (relleno compactado)
CONEXIONES = [("EJE-04", "X885b", "N885"), ("EJE-05", "T29w", "T7e"), ("EJE-05", "T7w", "T4s"), ("EJE-02", "W1b", "D1n"),
              ("EJE-14", "X971a", "Q0"), ("EJE-15", "X971b", "Q1")]

# --- quiebres a 45 grados (indicacion del usuario): cada esquina de mas de 50 grados se ochava con un tramo en diagonal, de modo que
# el cambio de direccion se hace en dos quiebres (dos de 45 grados en una esquina de 90) y el agua no choca de frente contra el muro.
CHAFLAN = 0.60                       # corte en cada lado de la esquina (m), sin pasar de la mitad del tramo mas corto
ANG_CHAFLAN = 50.0                   # esquinas con un giro mayor se ochavan


def _giro(a, b, c):
    u = (b[0] - a[0], b[1] - a[1]); v = (c[0] - b[0], c[1] - b[1])
    cs = (u[0] * v[0] + u[1] * v[1]) / (math.hypot(*u) * math.hypot(*v))
    return math.degrees(math.acos(max(-1.0, min(1.0, cs))))


def _unit(a, b):
    L = math.dist(a, b); return ((b[0] - a[0]) / L, (b[1] - a[1]) / L), L


def chaflanes():
    """Ochava las esquinas de los ejes. Los ejes que llegan a una esquina entran en diagonal al inicio del tramo de salida
    (union en Y). Devuelve la lista de esquinas ochavadas."""
    global RAMALES, TAPADOS_FIJOS, CONEXIONES
    nuevos = {cod: list(nudos) for cod, sis, nudos, desc in RAMALES}
    hechas, inicio_de, fin_de = [], {}, {}
    for cod, sis, nudos, desc in RAMALES:
        for i in range(1, len(nudos) - 1):
            X = nudos[i]; a, x, c = N[nudos[i - 1]], N[X], N[nudos[i + 1]]
            g = _giro(a, x, c)
            if g < ANG_CHAFLAN: continue
            (u, Lin), (v, Lout) = _unit(a, x), _unit(x, c)
            ch = min(CHAFLAN, 0.5 * Lin, 0.5 * Lout)
            xa, xb = X + "~a", X + "~b"
            N[xa] = (x[0] - u[0] * ch, x[1] - u[1] * ch); N[xb] = (x[0] + v[0] * ch, x[1] + v[1] * ch)
            k = nuevos[cod].index(X); nuevos[cod][k:k + 1] = [xa, xb]
            inicio_de[X], fin_de[X] = xa, xb
            hechas.append((cod, X, round(g), round(ch, 2)))
            for c2, s2, n2, d2 in RAMALES:                 # ejes que terminan en la esquina: entran en diagonal al tramo de salida
                if c2 != cod and n2[-1] == X:
                    w, Lw = _unit(N[n2[-2]], x)
                    if _giro(N[n2[-2]], x, c) >= ANG_CHAFLAN:
                        chq = min(CHAFLAN, 0.5 * Lw, ch)
                        xq = X + "~" + c2
                        N[xq] = (x[0] - w[0] * chq, x[1] - w[1] * chq)
                        nuevos[c2][-1:] = [xq, xb]
                    else:
                        nuevos[c2][-1:] = [xb]
    RAMALES = [(cod, sis, nuevos[cod], desc) for cod, sis, nudos, desc in RAMALES]
    TAPADOS_FIJOS = [(c, inicio_de.get(a, a), fin_de.get(b, b), m) for c, a, b, m in TAPADOS_FIJOS]
    CONEXIONES = [(c, fin_de.get(a, a), inicio_de.get(b, b)) for c, a, b in CONEXIONES]
    return hechas


CHAFLANES = chaflanes()


def plataforma():
    return Path(PLAT)


def rasante_fn():
    z = T.modelo(); ce = Path(CERCO); pa = Path(PATIO)
    def ras(x, y):
        if pa.contains_point((x, y)): return RAS_PATIO    # cunetas al ras del patio de maniobra (+184.50)
        if ce.contains_point((x, y)): return RASANTE      # interior nivelado
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
        for c, a, b in CONEXIONES:                       # conexiones nuevas: rasante recta entre extremos (relleno)
            if c == cod:
                ia = [i for i, p in enumerate(pts) if p[2] == a][0]; ib = [i for i, p in enumerate(pts) if p[2] == b][-1]
                for i in range(ia + 1, ib): r[i] = r[ia] + (r[ib] - r[ia]) * (s[i] - s[ia]) / (s[ib] - s[ia])
        if nudos[-1] in DESCARGAS:                       # pase por el cerco: la cuneta llega al cerco con su mismo borde (no baja al terreno exterior)
            idn = [i for i, p in enumerate(pts) if p[2] == nudos[-2]][-1]
            for i in range(idn + 1, len(pts)): r[i] = r[idn]
        tap = [any(v.contains_point(p[:2]) for v in ver) for p in pts]    # tramos tapados: veredas del plano y tramos fijos
        for c, a, b, mot in TAPADOS_FIJOS:
            if c == cod:
                ia = [i for i, p in enumerate(pts) if p[2] == a][0]; ib = [i for i, p in enumerate(pts) if p[2] == b][-1]
                for i in range(ia, ib + 1): tap[i] = True
        geo[cod] = (pts, s, r, tap)
    # cota de fondo: iteracion hasta que los empalmes queden por debajo de los ramales que llegan
    req = {}                                          # cota maxima admisible en cada nudo (por los ramales que llegan)
    for it in range(50):
        fondo, cambio = {}, False
        for cod, sis, nudos, desc in RAMALES:
            pts, s, r, tap = geo[cod]; f = []
            hm = []; j = -1                                # profundidad minima de cada punto (0.25 o la del tramo)
            for i, p in enumerate(pts):
                if p[2] and i < len(pts) - 1: j += 1
                req_j = hq.get("%s|%s|%s" % (cod, nudos[j], nudos[j + 1]), HMIN)
                if p[2] and i > 0: req_j = max(req_j, hq.get("%s|%s|%s" % (cod, nudos[j - 1], nudos[j]), HMIN) if j > 0 else HMIN)
                hm.append(max(HMIN, req_j) + (E_TAPA if tap[i] else 0.0))     # en tapado se suma la losa
            for i, p in enumerate(pts):
                if i == 0: v = r[0] - H0 - (E_TAPA if tap[0] else 0.0)
                else: v = min(f[-1] - S0 * (s[i] - s[i - 1]), r[i] - hm[i])
                if p[2] and i > 0 and p[2] in req: v = min(v, req[p[2]])
                f.append(v)
            # donde un empalme obliga a bajar (llega un eje mas hondo), el fondo baja parejo desde el nudo anterior (sin escalon)
            nod = [i for i, p in enumerate(pts) if p[2]]
            for k0, k1 in zip(nod[:-1], nod[1:]):
                if pts[k1][2] in req and f[k1] < f[k1 - 1] - S0 * (s[k1] - s[k1 - 1]) * 1.5:
                    for i in range(k0 + 1, k1):
                        f[i] = min(f[i], f[k0] + (f[k1] - f[k0]) * (s[i] - s[k0]) / (s[k1] - s[k0]))
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
                         "n_manning": N_MAN, "borde_libre": BL, "npt": NPT, "rasante": RASANTE, "nivel_area_verde": NIVEL_AV,
                         "nivel_patio": NIVEL_PATIO, "rasante_patio": RAS_PATIO},
           "nudos": {k: [round(v[0], 3), round(v[1], 3)] for k, v in N.items() if k in nombre}, "nombre": nombre, "descargas": DESCARGAS, "ramales": []}
    for cod, sis, nudos, desc in RAMALES:
        pts, s, r, tap = geo[cod]; f = fondo[cod]
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
                           "Q_cap": round(q_manning(min(r[i0] - f[i0], r[i1] - f[i1]) - (E_TAPA if ltap > 0 else 0.0), max(S, S0)), 4)})
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
