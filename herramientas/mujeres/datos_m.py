"""Datos de diseno del colector pluvial frontal del CAR Mujeres (CUI 2717013).

Parametros: hoja DATOS del metrado METRADO_COLECTOR_PLUVIAL_CAR_MUJERES.xlsx (los mismos de la planilla del
presupuesto, partidas 1.4.4.6). Geometria en planta (eje, registros, cunetas, cruces, juntas, base de arquitectura) y
perfil de flujo: base_m.json (extraer_m.py, desde el plano original y la memoria de calculo).
Cotas en m.s.n.m.; progresivas desde el registro R-01 (Eje 02, llegada de CAR Varones y Hogar de Refugio) hacia la salida.
"""
import os, json, math

AQUI = os.path.dirname(os.path.abspath(__file__))
HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
SAL = os.path.join(RAIZ, "entregables_mujeres", "PLANOS_COLECTOR_MEJORADOS")
BASE = json.load(open(os.path.join(AQUI, "base_m.json")))

# ------------------------------------------------------------------ parametros (hoja DATOS del metrado)
b = 1.50
CF0, CFS, L = 258.72, 258.30, 139.08
S = (CF0 - CFS) / L
NPT = 259.25
P_VER = 78.42            # fin del tramo en vereda
H_FIN = 0.60             # altura interior del tramo final
CAMION = (54.0, 60.0)
AUTOS = ((2.74, 18.45), (35.04, 51.86))
E_SOLADO = 0.05
PESO = {"3/8": 0.56, "1/2": 0.994}
# salida
AL_L, AL_E, AL_H0, AL_H1, ZAP_B, ZAP_H = 1.00, 0.15, 0.70, 0.45, 0.45, 0.20
AL_AV = 0.707; ANCHO_FIN = 2.914
UNA_B1, UNA_B2, UNA_H = 0.35, 0.15, 0.65
EMB_E, AFIRM_E = 0.20, 0.10
# registros
REB, LUZ, TAPA, E_TAPA, ENG_B, ENG_H = 0.70, 0.60, 0.68, 0.08, 0.15, 0.10
CUNETAS = [("EJE 02", "R-01", 258.73), ("EJE 07", "R-05", 258.74), ("EJE 10", "R-06", 258.74), ("EJE 12", "R-07", 258.80)]
Q_LLEGADA = 560.6        # L/s: CAR Varones 258.7 + Hogar de Refugio 301.9


def CF(p):
    return CF0 - S * p


def zona(p):
    if CAMION[0] <= p < CAMION[1]: return "CAMION"
    if any(a <= p <= c for a, c in AUTOS): return "AUTOS"
    return "NORMAL"


def esp(p):
    """(e muro, e losa de fondo, e losa superior)"""
    return (0.15, 0.20, 0.20) if zona(p) == "CAMION" else (0.10, 0.10, 0.10)


def h(p):
    return NPT - esp(p)[2] - CF(p) if p <= P_VER else H_FIN


def techo(p):
    """cara superior de la losa superior"""
    return NPT if p <= P_VER else CF(p) + H_FIN + esp(p)[2]


def b_ext(p):
    return b + 2 * esp(p)[0]


def tramo_txt(p):
    z = zona(p)
    if z == "CAMION": return "CRUCE DE CAMIONES"
    if z == "AUTOS": return "CRUCE VEHICULAR (AUTOS)"
    return "TRAMO EN VEREDA" if p <= P_VER else "TRAMO FINAL"


def acero(p):
    """Armadura de la seccion segun el metrado (hoja TRAMOS): marcos y barras longitudinales."""
    z = zona(p); hh = h(p); em, ef, es = esp(p)
    if z == "CAMION":
        return dict(marco='1/2"', sep=0.15, doble=True, long_sep=0.20, recub=0.045)
    return dict(marco='3/8"', sep=0.15 if z == "AUTOS" else 0.20, doble=False, long_sep=0.25, recub=None,
                n_muro=max(math.ceil(round((hh + 0.10) / 0.25, 6)) - 1, 0))


def prog_txt(p):
    return "%d+%06.2f" % (int(p // 1000), p % 1000)


# ------------------------------------------------------------------ eje en planta (coordenadas locales del plano)
EJE = [tuple(q) for q in BASE["eje"]]
_ac = [0.0]
for a, c in zip(EJE[:-1], EJE[1:]): _ac.append(_ac[-1] + math.dist(a, c))
L_EJE = _ac[-1]


def eje_local(p):
    """(x, y, azimut_grados de la direccion de avance) en la progresiva p."""
    p = max(0.0, min(p, L_EJE))
    for i in range(len(EJE) - 1):
        if p <= _ac[i + 1] + 1e-9:
            a, c = EJE[i], EJE[i + 1]; t = (p - _ac[i]) / max(_ac[i + 1] - _ac[i], 1e-9)
            return (a[0] + t * (c[0] - a[0]), a[1] + t * (c[1] - a[1]), math.degrees(math.atan2(c[1] - a[1], c[0] - a[0])))


def lateral(p, d):
    """Punto a d m del eje, positivo hacia el predio (norte del plano)."""
    x, y, az = eje_local(p); a = math.radians(az)
    nx, ny = -math.sin(a), math.cos(a)
    if ny < 0: nx, ny = -nx, -ny
    return (x + d * nx, y + d * ny)


def prog_de(pt):
    """progresiva del punto proyectado sobre el eje"""
    best = (1e9, 0)
    for i in range(len(EJE) - 1):
        a, c = EJE[i], EJE[i + 1]; dx, dy = c[0] - a[0], c[1] - a[1]; l2 = dx * dx + dy * dy
        t = max(0, min(1, ((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / l2))
        q = (a[0] + t * dx, a[1] + t * dy); d = math.dist(q, pt)
        if d < best[0]: best = (d, _ac[i] + t * math.sqrt(l2))
    return best[1]


# ------------------------------------------------------------------ registros (cuadro UTM del plano original)
REGISTROS = []
for f in BASE["cuadro_utm"]:
    if f[0].startswith("R-"):
        REGISTROS.append(dict(nombre=f[0], prog=float(f[1].replace("0+", "")), E=f[2], N=f[3], cf=float(f[4]), ct=float(f[5])))
SALIDA_UTM = [f for f in BASE["cuadro_utm"] if f[0] == "SALIDA"][0]
JUNTAS = sorted(round(prog_de(((pl[0][0] + pl[-1][0]) / 2, (pl[0][1] + pl[-1][1]) / 2)), 2) for pl in BASE["JUNTAS"])
SECCIONES = [(i + 1, p) for i, p in enumerate([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 136.58])]

# ------------------------------------------------------------------ terreno (TIN, hoja TRAMOS) y perfil de flujo (memoria)
TERRENO = [tuple(q) for q in BASE["terreno"]]
FLUJO = [tuple(q) for q in BASE["perfil_flujo"]]     # prog, CF, Q, y, NA, V, Fr, llenado, BL


def _interp(tab, p, k):
    if p <= tab[0][0]: return tab[0][k]
    for a, c in zip(tab[:-1], tab[1:]):
        if p <= c[0]:
            t = (p - a[0]) / max(c[0] - a[0], 1e-9); return a[k] + t * (c[k] - a[k])
    return tab[-1][k]


def terreno(p): return _interp(TERRENO, p, 1)
def NA(p): return _interp(FLUJO, p, 4)
def tirante(p): return _interp(FLUJO, p, 3)


def Q(p):
    """caudal de diseno (L/s) del tramo que contiene p (escalon en cada cuneta)"""
    for r in sorted(FLUJO, key=lambda r: r[0]):
        if r[0] >= p - 1e-6: return r[2] * 1000
    return FLUJO[-1][2] * 1000
