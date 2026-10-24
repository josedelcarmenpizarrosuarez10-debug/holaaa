"""Lloraderos: solo en el muro de la cuneta que esta en contacto con area verde (el que da a vereda, patio o piso no lleva).

Drenan el agua que se carga en el area verde cuando llueve, sin drenes franceses. Cada lloradero: tubo PVC 3" que atraviesa el
muro a media altura, con caja filtrante de 0.30 x 0.30 de grava envuelta en geotextil (para que no pasen limos), @ 1.50 m.

Por cada tramo de cuneta y cada lado (izquierdo / derecho segun el sentido del agua) se recorre el eje cada 0.25 m; el punto de
la franja exterior del muro (0.30 m) se marca si cae en area verde; las marcas seguidas forman un tramo junto a area verde.
N.° de lloraderos del tramo = REDONDEAR.MAS(L / 1.50), repartidos en el tramo y centrados en su paño.
"""
import math

import numpy as np
import shapely

PASO = 0.25


def calcular(R, verde, P, anchos):
    """R: red con cotas (cotas.calcular). verde: poligono de areas verdes. anchos: {(eje, de, a): b}.
    Devuelve (tramos, puntos): tramos junto a area verde con su N.° y la posicion de cada lloradero."""
    if verde is None or verde.is_empty: return [], []
    Nn = R["nudos"]; tramos, puntos = [], []
    for r in R["ramales"]:
        s_eje = 0.0
        for t in r["tramos"]:
            a, b = Nn[t["de"]], Nn[t["a"]]; L = math.dist(a, b)
            if L < P["llor_min"] or t["origen"] == "pase":
                s_eje += L; continue
            ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            bb = anchos.get((r["codigo"], t["de"], t["a"]), P["b_int"])
            cara = bb / 2 + P["e_muro"]                       # cara exterior del muro
            s = np.arange(PASO / 2, L, PASO)
            for lado, sg in (("izquierdo", 1.0), ("derecho", -1.0)):
                d = cara + P["llor_franja"] / 2
                xs = a[0] + ux * s - uy * sg * d; ys = a[1] + uy * s + ux * sg * d
                m = shapely.contains_xy(verde, xs, ys)
                i = 0
                while i < len(s):
                    if not m[i]: i += 1; continue
                    j = i
                    while j + 1 < len(s) and m[j + 1]: j += 1
                    p0, p1 = s[i] - PASO / 2, s[j] + PASO / 2; Lv = p1 - p0
                    if Lv >= P["llor_min"]:
                        n = math.ceil(Lv / P["llor_sep"] - 1e-9); dd = Lv / n
                        tramos.append({"eje": r["codigo"], "de": t["de"], "a": t["a"], "lado": lado,
                                       "prog_desde": round(s_eje + p0, 2), "prog_hasta": round(s_eje + p1, 2), "L_m": round(Lv, 2),
                                       "sep_m": P["llor_sep"], "n": n})
                        for k in range(n):
                            sk = p0 + dd * (k + 0.5)
                            puntos.append({"eje": r["codigo"], "x": a[0] + ux * sk - uy * sg * cara, "y": a[1] + uy * sk + ux * sg * cara,
                                           "nx": -uy * sg, "ny": ux * sg, "ux": ux, "uy": uy})
                    i = j + 1
            s_eje += L
    return tramos, puntos


def resumen(tramos):
    return {"tramos": len(tramos), "lloraderos": sum(t["n"] for t in tramos), "longitud_muro_m": round(sum(t["L_m"] for t in tramos), 2),
            "detalle": "PVC 3\" @ %.2f m a media altura del muro, con caja filtrante de 0.30 x 0.30 de grava y geotextil" % (tramos[0]["sep_m"] if tramos else 1.5)}
