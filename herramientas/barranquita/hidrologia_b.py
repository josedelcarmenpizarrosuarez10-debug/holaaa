"""Hidrologia de la I.E. N.° 0590 Barranquita (C.I. 468901): lluvia de diseno transpuesta desde la estacion CO Tarapoto.

1. Serie de precipitacion maxima en 24 h de la estacion CO "Tarapoto" (SENAMHI, 1999-2024, 26 anos): la misma serie de los
   estudios hidrologicos de los proyectos de Morales (Hogar de Refugio, CUI 2675514; CAR Mujeres, CUI 2717013).
2. Transposicion a Barranquita por la relacion de precipitacion media anual (Manual de Hidrologia, Hidraulica y Drenaje MTC,
   transposicion de informacion pluviometrica): factor = P anual Barranquita / P anual Tarapoto. La llanura del Caynarachi -
   Huallaga (184 m s. n. m.) se representa con la precipitacion media anual de Yurimaguas (2,039.6 mm, misma altitud y misma
   fuente que Tarapoto, 1,073.1 mm); queda dentro del rango 1,800 - 2,400 mm/ano de la memoria de arquitectura del proyecto.
3. Analisis de frecuencias (Normal, Log-Normal, Log-Pearson III, Gumbel), prueba de Kolmogorov-Smirnov y periodo de retorno
   T = 25 anos (mismo criterio de los proyectos de Morales).
4. Lluvias de corta duracion por Dick y Peschke, intensidades, curvas IDF (I = K T^m / t^n) e intensidad de diseno con tc = 10 min.
5. Coeficientes de escorrentia por tipo de superficie (techos, pavimentos, areas verdes) medidos en la planta del proyecto.
"""
import math, json, os, sys
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)

ESTACION = {"nombre": 'CO "Tarapoto"', "tipo": "Meteorologica convencional", "entidad": "SENAMHI", "departamento": "San Martin",
            "provincia": "San Martin", "distrito": "Tarapoto", "latitud": "06° 28' S", "longitud": "76° 22' O", "altitud": 356,
            "periodo": "1999-2024"}
# precipitacion maxima en 24 h por mes (mm); None = sin dato
SERIE = {
    1999: [79.3, 42.5, 39.3, 16.9, 54.5, 17.5, 27.9, 23.0, 11.3, 17.3, 48.8, 46.5],
    2000: [27.5, 34.2, 15.6, 34.7, 30.2, 12.6, 17.5, 52.6, 82.5, 19.4, 24.2, 30.3],
    2001: [16.2, 32.0, 35.0, 75.9, 40.3, 13.8, 40.6, 21.3, 24.3, 61.0, 30.0, 42.2],
    2002: [9.3, 30.0, 14.8, 39.8, 12.5, 43.6, 35.3, 7.1, 5.8, 32.3, 27.5, 20.7],
    2003: [74.0, 37.0, 54.6, 33.1, 37.6, 27.5, 17.8, 18.0, 18.0, 84.5, 40.2, 52.2],
    2004: [15.8, 64.2, 24.0, 26.2, 48.1, 30.7, 25.7, 25.6, 28.2, 33.2, 46.2, 59.9],
    2005: [15.9, 33.7, 48.8, 44.0, 22.4, 26.8, 16.3, 15.5, 26.0, 45.0, 71.0, 9.3],
    2006: [38.5, 44.5, 41.5, 52.0, 39.0, 17.3, 113.3, 7.0, 18.5, 39.2, 74.0, 28.0],
    2007: [37.0, 7.5, 48.0, 21.0, 45.4, 16.5, 60.0, 46.2, 45.2, 37.8, 63.5, 18.5],
    2008: [25.6, 91.0, 27.5, 51.0, 25.6, 24.0, 9.3, 10.4, 38.0, 17.4, 18.0, 15.3],
    2009: [29.4, 49.0, 28.0, 35.5, 36.5, 47.0, 9.1, 25.0, 31.5, 18.4, 25.5, 42.0],
    2010: [32.2, 62.4, 17.6, 72.8, 31.6, 40.6, 6.1, 44.5, 23.9, 27.7, 98.4, 47.8],
    2011: [42.4, 11.8, 63.2, 51.9, 31.5, 65.2, 49.2, 14.5, 21.6, 24.6, 49.2, 61.8],
    2012: [71.7, 35.6, 53.1, 100.5, 40.8, 28.8, 20.0, 8.3, 31.2, 40.2, 15.6, 82.4],
    2013: [71.7, 32.7, 45.3, 27.4, 32.1, 20.1, 15.0, 49.0, 41.8, 27.0, 64.5, 28.4],
    2014: [33.4, 29.5, 60.3, 37.6, 32.1, 13.2, 32.5, 22.4, 28.2, 89.5, 46.1, 26.0],
    2015: [28.4, 40.9, 16.4, 43.7, 34.4, 40.2, 12.8, 34.6, 13.7, 32.9, 64.2, 60.3],
    2016: [36.0, 40.1, 35.9, 18.6, 32.2, 47.5, 19.4, 10.3, 19.0, 50.0, 27.0, 33.5],
    2017: [51.2, 73.6, 62.9, 51.8, 36.0, 39.6, 19.5, 30.8, 47.7, 15.7, 72.5, 63.7],
    2018: [25.6, 42.5, 55.4, 47.4, 27.5, 35.0, 34.2, 18.4, 34.7, 27.5, 26.5, 69.6],
    2019: [42.9, 42.3, 20.8, 23.5, 32.0, 9.7, 39.8, 23.7, 25.3, 86.9, 36.4, 44.0],
    2020: [152.5, 33.0, 50.6, None, None, None, None, 32.2, 32.9, 50.6, 38.4, 14.2],
    2021: [42.4, 46.8, 73.5, 28.5, 12.9, 32.4, 59.9, 24.3, 54.3, 28.8, 30.8, 69.7],
    2022: [15.0, 48.8, 54.4, 39.0, 48.1, 17.0, 15.8, 40.9, 32.8, 31.6, 85.2, 43.0],
    2023: [58.0, 22.8, 92.4, 43.3, 25.8, 9.2, 14.5, 26.0, 14.0, 14.2, 77.5, 56.5],
    2024: [57.8, 72.2, 30.8, 34.5, 16.4, 10.4, 6.0, None, None, None, None, None],
}
P_ANUAL_TARAPOTO = 1073.1         # mm/ano, estacion Tarapoto (SENAMHI)
P_ANUAL_BARRANQUITA = 2039.6      # mm/ano, llanura Caynarachi - Huallaga (Yurimaguas, 184 m s. n. m.; SENAMHI)
FUENTE_ANUAL = ("Precipitacion media anual de las estaciones Tarapoto (1,073.1 mm) y Yurimaguas (2,039.6 mm), datos SENAMHI "
                "reportados en la Disertacion de Maestria USP (teses.usp.br, tde-20191218-125548); rango 1,800 - 2,400 mm/ano "
                "de la memoria descriptiva de arquitectura del proyecto")
FACTOR = P_ANUAL_BARRANQUITA / P_ANUAL_TARAPOTO
T_DISENO = 25                     # anos
TC = 10.0                         # min (cunetas: tiempo de concentracion minimo)
PERIODOS = [2, 5, 10, 20, 25, 50, 100, 200, 500]
DURACIONES = [5, 10, 15, 20, 30, 60, 90, 120, 240, 360, 720, 1440]
# coeficientes de escorrentia (T = 25 anos; mismos valores de los estudios de Morales)
C_SUP = {"techo": 0.88, "pavimento": 0.88, "verde": 0.40}
NOM_SUP = {"techo": "Techos y coberturas (TR4 / panel termoacustico)", "pavimento": "Veredas, pisos, losa y patio de maniobra (concreto)",
           "verde": "Areas verdes y terreno natural (relleno nivelado)"}
KS_CRIT = {5: 0.56, 10: 0.41, 15: 0.34, 20: 0.29, 25: 0.27, 30: 0.24, 34: 0.23, 40: 0.21, 45: 0.20, 50: 0.19}   # alfa = 0.05


def maximos():
    return [(a, max(v for v in m if v is not None)) for a, m in SERIE.items()]


def _phi(z): return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def _z(p):
    """Inversa de la normal estandar (p = probabilidad de no excedencia)."""
    lo, hi = -10.0, 10.0
    for _ in range(200):
        m = (lo + hi) / 2
        if _phi(m) < p: lo = m
        else: hi = m
    return (lo + hi) / 2


def estad(x):
    x = np.array(x, float); n = len(x); m = x.mean(); s = x.std(ddof=1)
    cs = n * ((x - m) ** 3).sum() / ((n - 1) * (n - 2) * s ** 3)
    return n, m, s, cs


def analisis(factor=FACTOR):
    """Analisis de frecuencias de la serie transpuesta (P anual Barranquita / P anual Tarapoto)."""
    serie = [(a, round(p * factor, 2)) for a, p in maximos()]
    x = [p for _, p in serie]; n, m, s, cs = estad(x)
    lx = [math.log10(p) for p in x]; _, ml, sl, csl = estad(lx)
    a_g = math.sqrt(6) * s / math.pi; u_g = m - 0.5772 * a_g
    def kt_lp3(z, c):
        if abs(c) < 1e-6: return z
        k = c / 6; return (2 / c) * ((1 + k * z - k * k) ** 3 - 1)
    def kt_gum(T): return -(math.sqrt(6) / math.pi) * (0.5772 + math.log(math.log(T / (T - 1))))
    tab = {}
    for T in PERIODOS:
        z = _z(1 - 1 / T)
        tab[T] = {"normal": m + z * s, "lognormal": 10 ** (ml + z * sl), "lp3": 10 ** (ml + kt_lp3(z, csl) * sl),
                  "gumbel": m + kt_gum(T) * s, "z": z, "kt_gumbel": kt_gum(T), "kt_lp3": kt_lp3(z, csl)}
    # Kolmogorov-Smirnov (posicion de Weibull m / (n + 1))
    xs = sorted(x); fe = [(i + 1) / (n + 1) for i in range(n)]
    def F(d, v):
        if d == "normal": return _phi((v - m) / s)
        if d == "lognormal": return _phi((math.log10(v) - ml) / sl)
        if d == "lp3":                                  # Wilson-Hilferty inverso aproximado por biseccion en z
            lo, hi = -8.0, 8.0
            for _ in range(100):
                zz = (lo + hi) / 2
                if 10 ** (ml + kt_lp3(zz, csl) * sl) < v: lo = zz
                else: hi = zz
            return _phi((lo + hi) / 2)
        return math.exp(-math.exp(-(v - u_g) / a_g))
    ks = {d: max(abs(fe[i] - F(d, xs[i])) for i in range(n)) for d in ("normal", "lognormal", "lp3", "gumbel")}
    crit = min(KS_CRIT.items(), key=lambda kv: abs(kv[0] - n))[1]
    mejor = min(ks, key=ks.get)
    return {"serie": serie, "n": n, "media": m, "desv": s, "cs": cs, "media_log": ml, "desv_log": sl, "cs_log": csl,
            "gumbel_alfa": a_g, "gumbel_u": u_g, "tabla": tab, "ks": ks, "ks_critico": crit, "elegida": mejor,
            "orden": [(xs[i], fe[i]) for i in range(n)]}


def p_dur(P24, D):
    """Dick y Peschke: P_D = P24 (D / 1440)^0.25."""
    return P24 * (D / 1440.0) ** 0.25


def resultados():
    A = analisis(); d = A["elegida"]
    p24 = {T: A["tabla"][T][d] for T in PERIODOS}
    idf = {T: {D: p_dur(p24[T], D) * 60.0 / D for D in DURACIONES} for T in PERIODOS}
    # regresion I = K T^m / t^n (duraciones de 5 a 60 min, todos los periodos)
    X, Y = [], []
    for T in PERIODOS:
        for D in (5, 10, 15, 20, 30, 60):
            X.append([1.0, math.log10(T), math.log10(D)]); Y.append(math.log10(idf[T][D]))
    b = np.linalg.lstsq(np.array(X), np.array(Y), rcond=None)[0]
    K, mm, nn = 10 ** b[0], b[1], -b[2]
    P24d = p24[T_DISENO]; Pd = p_dur(P24d, TC); I = Pd * 60.0 / TC
    return {"analisis": A, "p24": p24, "idf": idf, "K": K, "m": mm, "n": nn, "P24": P24d, "P_tc": Pd, "I": I,
            "T": T_DISENO, "tc": TC, "factor": FACTOR}


def superficies(G, CERCO, PATIO):
    """Poligonos de techos y pavimentos dentro del cerco (shapely) para el coeficiente de escorrentia por celda."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    ce = Polygon(CERCO)
    def capa(nombres):
        ps = []
        for k in nombres:
            for e in G["geo"].get(k, []):
                if e[1] and len(e[0]) >= 3:
                    try:
                        p = Polygon([(x, y) for x, y, *_ in e[0]]).buffer(0)
                        if p.area > 1: ps.append(p)
                    except Exception: pass
        return unary_union(ps).intersection(ce) if ps else Polygon()
    techo = capa(["0_PROYECCIONES 1"])
    pav = unary_union([capa(["0_VEREDAS", "0.000. CIRCULACION - PLANTA", "0_PISO NIVEL 01"]), Polygon(PATIO).intersection(ce)]).difference(techo)
    verde = ce.difference(techo).difference(pav)
    return {"techo": techo, "pavimento": pav, "verde": verde}


if __name__ == "__main__":
    r = resultados(); A = r["analisis"]
    print("factor %.4f  n %d  media %.2f  s %.2f  elegida %s  KS %s (critico %.2f)" % (
        r["factor"], A["n"], A["media"], A["desv"], A["elegida"], {k: round(v, 4) for k, v in A["ks"].items()}, A["ks_critico"]))
    for T in PERIODOS: print(T, {k: round(v, 2) for k, v in A["tabla"][T].items() if k in ("normal", "lognormal", "lp3", "gumbel")})
    print("P24 T25 %.2f  P10 %.2f  I %.2f mm/h  K %.2f m %.3f n %.3f" % (r["P24"], r["P_tc"], r["I"], r["K"], r["m"], r["n"]))
