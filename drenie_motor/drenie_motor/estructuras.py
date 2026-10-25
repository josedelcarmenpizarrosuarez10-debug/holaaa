"""Estructuras hidráulicas en los cambios de nivel del piso (plataformas, muros de contención).

Rangos del proyectista (desnivel del borde de la cuneta entre una plataforma y la siguiente):
- hasta 0.15 m: la cuneta sigue continua (el desnivel se absorbe en la pendiente; cotas.py);
- de 0.15 a 0.50 m: CAÍDA CORTA, escalón en el fondo de la cuneta con losa de fondo reforzada aguas abajo;
- de 0.50 a 1.00 m: CAJA DE CAÍDA de concreto armado con poza de disipación;
- más de 1.00 m (siempre hay muro de contención): la cuneta de arriba llega al ras hasta la cara del muro y lo atraviesa por un
  PASE CON MARCO DE CONCRETO ARMADO; el agua cae vertical a una POZA DE DISIPACIÓN al pie del muro y de ahí sigue la cuneta de abajo.
Si el piso sube, la cuneta queda más profunda: no hay estructura, se avisa (conviene que el agua vaya de la plataforma alta a la baja).

Dimensionamiento de la caída vertical con poza (Rand; USBR, Design of Small Canal Structures):
    q = Q/b, D = q² / (g·hd³) (número de caída), Ld = 4.30·hd·D^0.27 (alcance del chorro), yp = 1.00·hd·D^0.22 (colchón bajo
    el chorro), y1 = 0.54·hd·D^0.425, y2 = 1.66·hd·D^0.27 (tirantes conjugados del resalto), Lj = 6.9·(y2 − y1);
    largo de poza L = Ld + Lj. La poza se profundiza hasta que el tirante conjugado y2 quede cubierto por el tirante de la
    cuneta de abajo más la profundidad de la poza. Mínimos constructivos (criterio): poza de 0.60 m de largo y 0.10 m de colchón.
"""
import math

G = 9.81
TIPOS = {"continua": "Cuneta continua (desnivel absorbido en la pendiente)", "caida_corta": "Caída corta (escalón en el fondo)",
         "caja_caida": "Caja de caída con poza de disipación", "muro": "Pase por muro de contención con marco de concreto armado y poza",
         "subida": "Sube de plataforma (sin estructura)"}
PREF = {"caida_corta": "CC", "caja_caida": "CD", "muro": "PM"}


def tipo_de(desnivel, P):
    if desnivel < 0: return "subida"
    if desnivel <= P["caida_continua_max"] + 1e-9: return "continua"
    if desnivel <= P["caida_corta_max"] + 1e-9: return "caida_corta"
    if desnivel <= P["caja_caida_max"] + 1e-9: return "caja_caida"
    return "muro"


def caida_vertical(Q, b, caida, y_abajo, P):
    """Poza al pie de una caída vertical. Q en m³/s, b ancho (m), caida = diferencia de cotas de fondo (m), y_abajo = tirante de
    la cuneta de abajo (m). Devuelve las dimensiones redondeadas a 5 cm y los valores hidráulicos."""
    q = max(Q, 1e-5) / b
    yc = (q * q / G) ** (1 / 3)
    prof = P.get("poza_colchon_min", 0.10)
    for _ in range(20):
        hd = caida + prof
        D = q * q / (G * hd ** 3)
        Ld, yp = 4.30 * hd * D ** 0.27, 1.00 * hd * D ** 0.22
        y1, y2 = 0.54 * hd * D ** 0.425, 1.66 * hd * D ** 0.27
        falta = y2 - (y_abajo + prof)
        if falta <= 0.005: break
        prof += max(0.01, falta)
    Lj = 6.9 * (y2 - y1)
    sube = lambda v, m: max(m, math.ceil(v / 0.05 - 1e-9) * 0.05)
    L = sube(Ld + Lj, P.get("poza_largo_min", 0.60))
    return {"q_m2s": round(q, 4), "yc": round(yc, 3), "hd": round(hd, 3), "D": round(D, 6), "Ld": round(Ld, 3), "yp": round(yp, 3),
            "y1": round(y1, 3), "y2": round(y2, 3), "Lj": round(Lj, 3), "L_poza": round(L, 2), "prof_poza": round(sube(prof, P.get("poza_colchon_min", 0.10)), 2)}


def _malla(area_m2, P):
    """Acero de una malla Ø 3/8" @ separación en ambos sentidos (kg) sobre una superficie media (criterio del proyectista)."""
    barras_m = 2.0 / P.get("estr_malla_sep", 0.20)
    return area_m2 * barras_m * 0.560


def metrado(e, P):
    """Cantidades de una estructura (concreto m³, encofrado m², acero kg) con espesor de muros y fondo de estructuras."""
    t = P.get("estr_espesor", 0.15); b = e["b"]
    if e["tipo"] == "caida_corta":
        # losa de fondo reforzada aguas abajo del escalón (sobre el ancho total de la cuneta) y el escalón mismo
        L = e["L_poza"]; h = e["caida_fondo"]
        conc = (b + 2 * P["e_muro"]) * L * 0.05 + b * h * t
        enc = b * h * 2
        acero = _malla(b * L + b * h, P)
        return {"concreto_m3": round(conc, 3), "encofrado_m2": round(enc, 2), "acero_kg": round(acero, 1)}
    L, Hc = e["L_poza"], e["alto_caja"]
    ext = (b + 2 * t) * (L + 2 * t) * (Hc + t) - b * L * Hc
    enc = 2 * (b + L) * Hc + 2 * (b + 2 * t + L + 2 * t) * Hc
    acero = _malla(2 * (b + t + L + t) * Hc + (b + t) * (L + t), P)
    out = {"concreto_m3": round(ext, 3), "encofrado_m2": round(enc, 2), "acero_kg": round(acero, 1)}
    if e["tipo"] == "muro":
        lm = P.get("muro_espesor", 0.25); hm = e["marco_alto"]
        marco = ((b + 2 * t) * (hm + 2 * t) - b * hm) * lm
        out["marco_concreto_m3"] = round(marco, 3)
        out["marco_encofrado_m2"] = round(2 * (b + hm) * lm, 2)
        out["marco_acero_kg"] = round(_malla(2 * (b + t + hm + t) * lm, P), 1)
        for k in ("concreto_m3", "encofrado_m2", "acero_kg"): out[k] = round(out[k] + out["marco_" + k], 3 if k == "concreto_m3" else 1)
    return out


def calcular(C, V, P):
    """Estructuras de todos los cambios de nivel de la red (C = cotas, V = verificación con el caudal de cada tramo)."""
    fila = {(f["eje"], f["de"], f["a"]): f for f in V["hidraulica"]}
    out, avisos, cont = [], [], {}
    for r in C["ramales"]:
        for c in r.get("cambios_nivel", []):
            tipo = tipo_de(c["desnivel"], P)
            t = r["tramos"][min(c["tramo"], len(r["tramos"]) - 1)]
            f = fila.get((r["codigo"], t["de"], t["a"])) or {}
            Q, b, y = f.get("Q_ls", 0.0) / 1000.0, f.get("b", P["b_int"]), f.get("y", 0.05)
            e = {"eje": r["codigo"], "tramo": "%s-%s" % (t["de"], t["a"]), "progresiva": c["s"], "x": c["x"], "y": c["y"],
                 "tipo": tipo, "descripcion": TIPOS[tipo], "desnivel": c["desnivel"], "borde_arriba": c["borde_arriba"],
                 "borde_abajo": c["borde_abajo"], "cf_arriba": c["cf_arriba"], "cf_abajo": c["cf_abajo"], "caida_fondo": c["caida_fondo"],
                 "nivel_arriba": c.get("nivel_arriba", ""), "nivel_abajo": c.get("nivel_abajo", ""), "Q_ls": round(Q * 1000, 2), "b": b}
            if tipo == "subida":
                avisos.append("%s %s (prog. %.2f): la cuneta pasa de %s a %s, %.2f m más alta; queda más profunda. Conviene que el agua vaya "
                              "de la plataforma alta a la baja (otra descarga o cambiar el sentido)." % (
                                  r["codigo"], e["tramo"], c["s"], e["nivel_arriba"] or "un nivel", e["nivel_abajo"] or "otro", -c["desnivel"]))
                e["estado"] = "AVISO"; out.append(e); continue
            if tipo == "continua":
                e["estado"] = "CUMPLE"; out.append(e); continue
            hyd = caida_vertical(Q, b, max(c["caida_fondo"], 0.0), y, P)
            e.update(hyd)
            cont[tipo] = cont.get(tipo, 0) + 1
            e["codigo"] = "%s-%02d" % (PREF[tipo], cont[tipo])
            # caja: desde el fondo de la poza hasta el borde de arriba
            e["alto_caja"] = round(c["borde_arriba"] - (c["cf_abajo"] - hyd["prof_poza"]), 2)
            if tipo == "muro":
                e["marco_alto"] = round(max(P["hmin"], c["borde_arriba"] - c["cf_arriba"]), 2)
                e["marco_ancho"] = round(b, 2)
            e["metrado"] = metrado(e, P)
            e["estado"] = "CUMPLE"
            out.append(e)
    return {"estructuras": out, "avisos": avisos,
            "resumen": {k: sum(1 for e in out if e["tipo"] == k) for k in ("continua", "caida_corta", "caja_caida", "muro", "subida")}}
