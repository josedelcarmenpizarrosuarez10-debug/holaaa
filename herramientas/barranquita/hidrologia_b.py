"""Hidrologia de la I.E. N.° 0590 Barranquita (C.I. 468901): lluvia de diseno con la estacion Pongo de Caynarachi (SENAMHI).

1. Serie de precipitacion maxima en 24 h de la estacion Pongo de Caynarachi (codigo 003317, SENAMHI, datos diarios historicos con
   control de calidad, insumos/barranquita/lluvia/qc00003317_pongo_de_caynarachi.txt): los 25 anios completos mas recientes,
   1989-2013 (indicacion del usuario: "solo 25 anios desde el anio mas reciente hacia abajo"; 2014 solo tiene enero a abril).
   Misma subcuenca del rio Caynarachi que Barranquita; se usa la serie medida, sin transposicion (factor 1.0).
   Antes (hasta el 21-10-2026): serie CO Tarapoto 1999-2024 transpuesta x 2.2137 (SERIE_TARAPOTO), que se conserva solo como contraste:
   la transposicion por lluvia anual sobreestima la maxima en 24 h (Caynarachi llueve 3.3 a 3.8 veces Tarapoto al anio, pero su
   maxima T 25 es solo 1.4 a 1.5 veces).
2. Analisis de frecuencias (Normal, Log-Normal, Log-Pearson III, Gumbel), prueba de Kolmogorov-Smirnov y periodo de retorno
   T = 25 anos (mismo criterio de los proyectos de Morales).
3. Lluvias de corta duracion por Dick y Peschke, intensidades, curvas IDF (I = K T^m / t^n) e intensidad de diseno con tc = 10 min.
4. Coeficientes de escorrentia por tipo de superficie (techos, pavimentos, areas verdes) medidos en la planta del proyecto.
"""
import math, json, os, sys
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)

ESTACION = {"nombre": "Pongo de Caynarachi", "codigo": "003317", "tipo": "Meteorologica convencional", "entidad": "SENAMHI",
            "departamento": "San Martin", "provincia": "Lamas", "distrito": "Caynarachi", "altitud": 230, "periodo": "1989–2013",
            "anios": 25}
# precipitacion maxima en 24 h por mes (mm) del archivo diario del SENAMHI; None = mes sin datos (enero 2005, julio 2008)
SERIE = {
    1989: [74.4, 82.7, 80.1, 61.9, 78.4, 77.5, 76.1, 58.1, 64.4, 141.9, 69.4, 46.9],
    1990: [81.5, 97.9, 62.6, 78.8, 61.2, 56.2, 41.6, 49.5, 65.4, 57.4, 115.1, 74.0],
    1991: [46.5, 53.7, 106.7, 56.6, 60.3, 83.4, 33.4, 32.5, 95.3, 55.3, 114.8, 88.4],
    1992: [63.3, 37.3, 103.8, 123.0, 98.7, 30.5, 45.3, 70.7, 60.2, 77.5, 50.0, 120.4],
    1993: [64.2, 89.1, 73.7, 62.5, 72.7, 76.1, 37.3, 32.1, 75.2, 64.9, 46.6, 74.0],
    1994: [63.2, 64.0, 143.2, 84.5, 82.1, 53.4, 76.0, 81.5, 65.5, 110.1, 60.0, 179.9],
    1995: [37.0, 74.3, 77.6, 50.9, 84.2, 29.2, 30.0, 81.2, 44.2, 57.1, 46.1, 73.5],
    1996: [96.4, 50.7, 73.2, 35.1, 60.2, 39.5, 14.8, 73.0, 29.1, 80.9, 55.9, 76.8],
    1997: [87.3, 70.1, 53.1, 71.2, 51.5, 41.9, 17.0, 40.0, 65.5, 97.3, 86.9, 103.9],
    1998: [72.5, 78.2, 95.4, 78.9, 67.1, 72.2, 56.6, 22.0, 31.9, 76.3, 171.8, 79.7],
    1999: [146.0, 122.0, 75.0, 40.7, 64.0, 70.2, 35.5, 27.8, 61.5, 40.1, 62.1, 56.9],
    2000: [56.8, 101.7, 59.5, 97.0, 65.4, 75.9, 43.1, 31.1, 108.5, 71.3, 87.4, 70.4],
    2001: [47.7, 76.8, 75.8, 74.9, 77.3, 52.4, 40.8, 26.1, 35.0, 74.7, 78.0, 76.8],
    2002: [27.8, 77.2, 63.4, 78.0, 46.7, 35.5, 52.3, 32.2, 45.4, 88.7, 67.1, 75.3],
    2003: [59.0, 45.1, 61.2, 75.5, 138.5, 75.2, 57.1, 21.0, 69.7, 81.5, 100.8, 82.8],
    2004: [47.4, 81.6, 76.3, 75.3, 87.0, 32.5, 44.4, 55.5, 44.3, 75.5, 90.2, 66.1],
    2005: [None, 80.8, 76.7, 97.3, 45.0, 65.6, 17.0, 75.6, 23.0, 70.5, 77.3, 66.2],
    2006: [80.7, 39.5, 81.5, 66.9, 48.7, 68.0, 35.8, 51.0, 52.7, 71.6, 72.2, 102.5],
    2007: [56.2, 33.3, 74.6, 76.5, 39.2, 46.8, 58.7, 33.0, 47.5, 76.0, 77.3, 76.5],
    2008: [57.8, 86.9, 74.0, 70.5, 67.0, 51.0, None, 25.9, 48.0, 55.2, 43.0, 100.4],
    2009: [87.0, 69.7, 58.0, 52.2, 70.0, 75.5, 77.2, 25.3, 70.4, 76.2, 59.0, 78.8],
    2010: [40.0, 79.0, 69.2, 128.0, 103.0, 56.5, 56.5, 15.2, 36.5, 75.8, 80.8, 73.8],
    2011: [73.8, 76.3, 80.8, 60.7, 77.8, 67.3, 58.8, 57.3, 57.0, 70.0, 101.0, 77.6],
    2012: [110.2, 56.5, 58.0, 87.2, 77.6, 25.5, 51.2, 12.1, 48.0, 48.2, 72.0, 54.8],
    2013: [78.7, 76.4, 64.5, 62.5, 53.6, 74.5, 81.2, 64.9, 54.8, 76.8, 84.0, 30.7],
}
# serie anterior (contraste en la memoria): CO Tarapoto 1999-2024, transpuesta por la relacion de lluvia anual
ESTACION_TARAPOTO = {"nombre": 'CO "Tarapoto"', "tipo": "Meteorologica convencional", "entidad": "SENAMHI", "departamento": "San Martin",
            "provincia": "San Martin", "distrito": "Tarapoto", "latitud": "06° 28' S", "longitud": "76° 22' O", "altitud": 356,
            "periodo": "1999-2024"}
# precipitacion maxima en 24 h por mes (mm); None = sin dato
SERIE_TARAPOTO = {
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
# estaciones SENAMHI de la zona: precipitacion total anual promedio 2013-2017 (Cuadro N° 05 del estudio hidrologico del expediente
# "Creacion del sistema de agua potable, alcantarillado sanitario y UBS en ... Barranquita ... distrito de Barranquita", Municipalidad
# Distrital de Barranquita)
ESTACIONES_ZONA = [("San Antonio", "153314", "San Martin / San Antonio", 430, 1834.84, False),
                   ("Pongo de Caynarachi", "003317", "Lamas / Caynarachi", 230, 3853.16, False),
                   ("Navarro", "000386", "San Martin / Chipurana", 130, 2349.79, True),
                   ("Pelejo", "153322", "San Martin / El Porvenir", 100, 2332.92, True),
                   ("Shanusi", "153315", "Alto Amazonas / Yurimaguas", 160, 2444.00, True)]
P_ANUAL_BARRANQUITA = round(sum(e[4] for e in ESTACIONES_ZONA if e[5]) / sum(1 for e in ESTACIONES_ZONA if e[5]), 2)   # 2,375.57 mm
FUENTE_ANUAL = ("Tarapoto: precipitacion media anual de 1,073.1 mm (SENAMHI). Barranquita: promedio de las estaciones de llanura Navarro, "
                "Pelejo y Shanusi (SENAMHI, 2013-2017), Cuadro N° 05 del estudio hidrologico del expediente de agua potable y alcantarillado "
                "sanitario del distrito de Barranquita (Municipalidad Distrital de Barranquita)")
FACTOR_TARAPOTO = P_ANUAL_BARRANQUITA / P_ANUAL_TARAPOTO   # transposicion anterior (solo contraste)
FACTOR = 1.0                      # serie medida de Pongo de Caynarachi: sin transposicion
T_DISENO = 25                     # anos
TC = 10.0                         # min (cunetas: tiempo de concentracion minimo)
PERIODOS = [2, 5, 10, 20, 25, 50, 100, 200, 500]
DURACIONES = [5, 10, 15, 20, 30, 60, 90, 120, 240, 360, 720, 1440]
# coeficientes de escorrentia (T = 25 anos; mismos valores de los estudios de Morales)
# (CE.040 Anexo I, Tabla 1.a: concreto / techo T 25 = 0.88; areas verdes en condicion promedio, pendiente promedio = 0.40)
C_SUP = {"techo": 0.88, "pavimento": 0.88, "estacionamiento": 0.88, "verde": 0.40}
NOM_SUP = {"techo": "Techos: edificaciones, corredores, patio civico techado y losa multiusos techada",
           "pavimento": "Areas libres de concreto: veredas, patios, atrio y circulaciones",
           "estacionamiento": "Patio de maniobra y estacionamiento (pavimento de concreto)",
           "verde": "Areas verdes y terreno natural (relleno nivelado)"}
ORDEN_SUP = ("techo", "pavimento", "estacionamiento", "verde")


def maximos(serie=None):
    return [(a, max(v for v in m if v is not None)) for a, m in (serie or SERIE).items()]


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


# tabla de la media y desviacion de la variable reducida de Gumbel segun n (Aparicio, pag. 264), como en el analisis de los CAR
GUMBEL_YN_SN = [(10, 0.4952, 0.9496), (15, 0.5128, 1.0206), (20, 0.5236, 1.0628), (25, 0.5309, 1.0914), (30, 0.5362, 1.1124),
                (90, 0.5586, 1.2007), (95, 0.5593, 1.2037)]
ALFA_KS = 0.05


def z_aprox(T):
    """Variable normal estandar para P = 1/T (aproximacion de Abramowitz y Stegun, la misma de la hoja de calculo)."""
    p = 1.0 / T; w = math.sqrt(math.log(1.0 / p ** 2))
    return w - (2.515517 + 0.802853 * w + 0.010328 * w * w) / (1 + 1.432788 * w + 0.189269 * w * w + 0.001308 * w ** 3)


def kt_lp3(z, k):
    """Factor de frecuencia de Log Pearson III (Kite) con k = Cs/6 de los logaritmos."""
    return z + (z * z - 1) * k + (z ** 3 - 6 * z) * k * k / 3 - (z * z - 1) * k ** 3 + z * k ** 4 + k ** 5 / 3


def kt_gumbel(T): return -(math.sqrt(6) / math.pi) * (0.5772 + math.log(math.log(T / (T - 1))))


def _chi2_sf(x, gl):
    """P(chi2 >= x) con gl grados de libertad, como CHIDIST de la hoja de calculo (gl truncado a entero)."""
    from scipy.special import gammaincc
    gl = int(gl)
    return float(gammaincc(gl / 2.0, x / 2.0)) if x > 0 else 1.0


def analisis(factor=FACTOR):
    """Analisis de frecuencias de la serie de diseno (factor 1.0: serie medida de Pongo de Caynarachi), con los mismos metodos de
    la hoja ANALISIS ESTADISTICO de los CAR: Normal, Log Normal, Log Pearson III (Kite) y Gumbel; Kolmogorov-Smirnov con la
    probabilidad de excedencia de Weibull m/(n+1) sobre la serie ordenada de mayor a menor."""
    serie = [(a, round(p * factor, 2)) for a, p in maximos()]
    x = [p for _, p in serie]; n, m, s, cs = estad(x)
    lx = [math.log10(p) for p in x]; _, ml, sl, csl = estad(lx)
    a_g = math.sqrt(6) * s / math.pi; u_g = m - 0.5772 * a_g
    tab = {}
    for T in PERIODOS:
        z = z_aprox(T); kp = kt_lp3(z, csl / 6)
        tab[T] = {"normal": m + z * s, "lognormal": 10 ** (ml + z * sl), "lp3": 10 ** (ml + kp * sl),
                  "gumbel": m + kt_gumbel(T) * s, "z": z, "kt_gumbel": kt_gumbel(T), "kt_lp3": kp}
    # Kolmogorov-Smirnov (hoja C de los CAR)
    xd = sorted(x, reverse=True); E = [(i + 1) / (n + 1) for i in range(n)]
    lnx = [math.log(v) for v in x]; _, mL, sL, csL = estad(lnx)
    b1 = (2 / csL) ** 2 if csL > 0 else None; a1 = sL / math.sqrt(b1) if b1 else None; d1 = mL - a1 * b1 if b1 else None
    yn = float(np.interp(n, [t[0] for t in GUMBEL_YN_SN], [t[1] for t in GUMBEL_YN_SN]))
    sn = float(np.interp(n, [t[0] for t in GUMBEL_YN_SN], [t[2] for t in GUMBEL_YN_SN]))
    tabla_ks = []
    for i, v in enumerate(xd):
        fn = 1 - _phi((v - m) / s); fl = 1 - _phi((math.log10(v) - ml) / sl)
        fp = _chi2_sf(2 * (math.log(v) - d1) / a1, 2 * b1) if b1 else None
        fg = 1 - math.exp(-math.exp(-(((v - m) / s) * sn + yn)))
        tabla_ks.append({"m": i + 1, "P": v, "E": E[i], "normal": fn, "lognormal": fl, "lp3": fp, "gumbel": fg})
    ks = {d: max(abs(t[d] - t["E"]) for t in tabla_ks) if all(t[d] is not None for t in tabla_ks) else float("inf")
          for d in ("normal", "lognormal", "lp3", "gumbel")}
    crit = math.sqrt(-math.log(ALFA_KS / 2) / (2 * n)) - 1 / (6 * n)
    mejor = min(ks, key=ks.get)
    xs = sorted(x); fe = [(i + 1) / (n + 1) for i in range(n)]
    return {"serie": serie, "n": n, "media": m, "desv": s, "cs": cs, "media_log": ml, "desv_log": sl, "cs_log": csl,
            "gumbel_alfa": a_g, "gumbel_u": u_g, "gumbel_yn": yn, "gumbel_sn": sn,
            "ln": {"media": mL, "desv": sL, "cs": csL, "beta": b1, "alfa": a1, "delta": d1},
            "tabla": tab, "ks": ks, "ks_critico": crit, "elegida": mejor, "tabla_ks": tabla_ks,
            "orden": [(xs[i], fe[i]) for i in range(n)]}


def contraste_tarapoto():
    """Resultado con la serie anterior (CO Tarapoto transpuesta x FACTOR_TARAPOTO), solo para comparar en la memoria."""
    global SERIE
    viejo = SERIE; SERIE = SERIE_TARAPOTO
    try:
        A = analisis(FACTOR_TARAPOTO); d = A["elegida"]; P24 = A["tabla"][T_DISENO][d]
        A0 = analisis(1.0); P0 = A0["tabla"][T_DISENO][A0["elegida"]]
    finally:
        SERIE = viejo
    return {"factor": FACTOR_TARAPOTO, "elegida": d, "P24": P24, "I": p_dur(P24, TC) * 60.0 / TC, "P24_sin": P0, "n": A["n"]}


def p_dur(P24, D):
    """Dick y Peschke: P_D = P24 (D / 1440)^0.25."""
    return P24 * (D / 1440.0) ** 0.25


DUR_BELL = [5, 10, 15, 20, 30, 60]


def bell(P60_10, T, t):
    """Modelo de Bell: P(T, t) = (0.21 ln T + 0.52)(0.54 t^0.25 - 0.50) P60^10 (t en minutos, de 5 a 120)."""
    return (0.21 * math.log(T) + 0.52) * (0.54 * t ** 0.25 - 0.50) * P60_10


def resultados():
    A = analisis(); d = A["elegida"]
    p24 = {T: A["tabla"][T][d] for T in PERIODOS}
    idf = {T: {D: p_dur(p24[T], D) * 60.0 / D for D in DURACIONES} for T in PERIODOS}       # Dick y Peschke (intensidades de diseno)
    # parametros de intensidades maximas (hoja A. Parametros de los CAR): lluvias de 5 a 60 min con el modelo de Bell, con
    # P60 de 10 anos = 0.4602 P24(10)^0.876, intensidades redondeadas a 0.1 mm/h y regresion I = K T^m / t^n
    P60_10 = 0.4602 * p24[10] ** 0.876
    bell_p = {T: {t: bell(P60_10, T, t) for t in DUR_BELL} for T in PERIODOS}
    bell_p[10][60] = P60_10                         # en la hoja, la celda T = 10, t = 60 min es la propia P60 de 10 anos
    bell_i = {T: {t: round(60.0 * bell_p[T][t] / t, 1) for t in DUR_BELL} for T in PERIODOS}
    X, Y = [], []
    for t in DUR_BELL:
        for T in sorted(PERIODOS, reverse=True):
            X.append([math.log10(T), math.log10(t), 1.0]); Y.append(math.log10(bell_i[T][t]))
    X, Y = np.array(X), np.array(Y)
    M = np.array([[X[:, 0].sum(), X[:, 1].sum(), len(Y)], [(X[:, 0] ** 2).sum(), (X[:, 0] * X[:, 1]).sum(), X[:, 0].sum()],
                  [(X[:, 0] * X[:, 1]).sum(), (X[:, 1] ** 2).sum(), X[:, 1].sum()]])
    V = np.array([Y.sum(), (X[:, 0] * Y).sum(), (X[:, 1] * Y).sum()])
    mm, mn, lk = np.linalg.solve(M, V)
    K, nn = round(10 ** lk, 2), abs(mn)
    P24d = p24[T_DISENO]; Pd = p_dur(P24d, TC); I = Pd * 60.0 / TC
    return {"analisis": A, "p24": p24, "idf": idf, "K": K, "m": mm, "n": nn, "P24": P24d, "P_tc": Pd, "I": I,
            "T": T_DISENO, "tc": TC, "factor": FACTOR, "P60_10": P60_10, "bell_p": bell_p, "bell_i": bell_i,
            "regresion": {"M": M.tolist(), "V": V.tolist(), "inv": np.linalg.inv(M).tolist(), "sol": [mm, mn, lk]}}


def _caras(G, nombres):
    """Caras (poligonos) formadas por todas las lineas de las capas, sin unir."""
    from shapely.geometry import LineString
    from shapely.ops import polygonize, unary_union
    ls = []
    for k in nombres:
        for e in G["geo"].get(k, []):
            q = [(x, y) for x, y, *_ in e[0]]
            if len(q) >= 2: ls.append(LineString(q + [q[0]] if e[1] else q))
    return [f for f in polygonize(unary_union(ls)) if f.area > 2]


def _poligonos(G, nombres, cerradas=True):
    """Poligonos shapely de las capas: polilineas cerradas o, con cerradas=False, caras formadas por todas sus lineas."""
    from shapely.geometry import Polygon, LineString
    from shapely.ops import polygonize, unary_union
    ps, ls = [], []
    for k in nombres:
        for e in G["geo"].get(k, []):
            q = [(x, y) for x, y, *_ in e[0]]
            if cerradas:
                if e[1] and len(q) >= 3:
                    try:
                        p = Polygon(q).buffer(0)
                        if p.area > 1: ps.append(p)
                    except Exception: pass
            elif len(q) >= 2:
                ls.append(LineString(q + [q[0]] if e[1] else q))
    if not cerradas:
        ps = [f for f in polygonize(unary_union(ls)) if f.area > 2]
    return unary_union(ps) if ps else Polygon()


# zonas del plano de arquitectura (cuadro de areas de la memoria de arquitectura) leidas en la base del sitio (UTM)
PATIO_CIVICO = (354902.2, 9249822.4, 354932.3, 9249839.6)    # patio civico techado (516 m2)
PATIO_04 = (354897.1, 9249822.4, 354902.2, 9249839.6)        # patio 04 + asta de bandera (88.15 m2)
LOSA = (354952.9, 9249796.2, 354976.7, 9249831.05)           # losa multiusos tipo I techada (810 m2), dentro del anillo de cunetas


def pisos_metrado(G, CERCO, PATIO):
    """Pisos (techos y pavimentos) del metrado de la junta cuneta-piso; se conserva tal cual para no alterar el metrado."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    ce = Polygon(CERCO)
    techo = _poligonos(G, ["0_PROYECCIONES 1"]).intersection(ce)
    pav = unary_union([_poligonos(G, ["0_VEREDAS", "0.000. CIRCULACION - PLANTA", "0_PISO NIVEL 01"]).intersection(ce),
                       Polygon(PATIO).intersection(ce)]).difference(techo)
    return {"techo": techo, "pavimento": pav}


def superficies(G, CERCO, PATIO):
    """Superficies dentro del cerco (shapely) para el coeficiente de escorrentia por celda: techos, areas libres de concreto,
    patio de maniobra y estacionamiento, y areas verdes (el resto)."""
    from shapely.geometry import Polygon, Point, box
    from shapely.ops import unary_union
    ce = Polygon(CERCO)
    # techos: caras de la proyeccion de coberturas (incluye las aulas en diagonal y los corredores) + patio civico y losa techados
    cob = _poligonos(G, ["0_PROYECCIONES 1"], cerradas=False).buffer(0.05, join_style=2).buffer(-0.05, join_style=2)
    cob = unary_union([Polygon(p.exterior) for p in getattr(cob, "geoms", [cob]) if not p.is_empty])
    techo = unary_union([cob, _poligonos(G, ["0_PROYECCIONES 1"]), box(*PATIO_CIVICO), box(*LOSA)]).intersection(ce)
    # areas libres de concreto: veredas, circulaciones, pisos exteriores, patios 01 a 04 y area de tratamiento
    patios = [f for f in _caras(G, ["0_ CUNETAS"]) if 150 < f.area < 300 and (f.contains(Point(354850.1, 9249846.3))       # patio 03 (255 m2)
              or f.contains(Point(354916.9, 9249819.0)))]                                                                  # patio 02 (192 m2)
    pav = unary_union([_poligonos(G, ["0_VEREDAS", "0.000. CIRCULACION - PLANTA", "0_PISO NIVEL 01"]), box(*PATIO_04)] + patios)
    pat = Polygon(PATIO).intersection(ce).difference(techo)
    trat = _poligonos(G, ["0_VEREDAS"]).intersection(pat)                  # losa del area de tratamiento dentro del patio
    est = pat.difference(trat)
    pav = pav.intersection(ce).difference(techo).difference(est)
    verde = ce.difference(techo).difference(pav).difference(est)
    # detalle por zona (nombres del cuadro de areas de la memoria de arquitectura)
    civ, los = box(*PATIO_CIVICO).intersection(techo), box(*LOSA).intersection(techo)
    p01 = [f for f in _caras(G, ["0_VEREDAS"]) if f.contains(Point(354912.4, 9249810.3))]
    zonas = {"Patio 01: ingreso principal": unary_union(p01).intersection(pav) if p01 else Polygon(),
             "Patio 02: circulacion principal": unary_union([f for f in patios if f.contains(Point(354916.9, 9249819.0))]).intersection(pav),
             "Patio 03: area privada de estudiantes": unary_union([f for f in patios if f.contains(Point(354850.1, 9249846.3))]).intersection(pav),
             "Patio 04: asta de bandera": box(*PATIO_04).intersection(pav)}
    resto = pav.difference(unary_union(list(zonas.values())))
    detalle = [("techo", "Coberturas de las edificaciones y corredores techados", techo.difference(civ).difference(los).area),
               ("techo", "Patio civico techado", civ.area), ("techo", "Losa multiusos tipo I techada", los.area)]
    detalle += [("pavimento", k, v.area) for k, v in zonas.items()]
    detalle += [("pavimento", "Veredas, circulaciones, atrio y losa del area de tratamiento", resto.area),
                ("estacionamiento", "Patio de maniobra y estacionamiento", est.area),
                ("verde", "Areas verdes, jardines y terreno natural nivelado", verde.area)]
    return {"techo": techo, "pavimento": pav, "estacionamiento": est, "verde": verde, "detalle": detalle}


if __name__ == "__main__":
    r = resultados(); A = r["analisis"]
    print("factor %.4f  n %d  media %.2f  s %.2f  elegida %s  KS %s (critico %.2f)" % (
        r["factor"], A["n"], A["media"], A["desv"], A["elegida"], {k: round(v, 4) for k, v in A["ks"].items()}, A["ks_critico"]))
    for T in PERIODOS: print(T, {k: round(v, 2) for k, v in A["tabla"][T].items() if k in ("normal", "lognormal", "lp3", "gumbel")})
    print("P24 T25 %.2f  P10 %.2f  I %.2f mm/h  K %.2f m %.3f n %.3f" % (r["P24"], r["P_tc"], r["I"], r["K"], r["m"], r["n"]))
