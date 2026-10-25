"""Lámina de detalle de las estructuras en los cambios de nivel y de la tapa vehicular (escala real: 1 unidad = 1 m).

- Corte longitudinal tipo de cada clase presente (caída corta, caja de caída, pase por muro de contención con marco de concreto
  armado y poza de disipación) con las medidas de la mayor estructura de su clase.
- Cuadro de todas las estructuras: código, eje, progresiva, desnivel, caída de fondo, poza (largo y profundidad) y concreto.
- Corte de la tapa vehicular (losa de concreto armado sobre la cuneta en estacionamientos), si la red la tiene.
"""
from ezdxf.enums import TextEntityAlignment as TA

from . import dxf_base as B
from .detalles import Vista, capas, llamadas, titulo, u_seccion

ESC = 20


def _corte(lam, xmm, ymm, e, P, ancho_mm):
    """Corte longitudinal de una estructura: cuneta de arriba, caída, poza y cuneta de abajo (origen = fondo de la poza)."""
    V = Vista(lam, xmm, ymm)
    t = P.get("estr_espesor", 0.15); ef = P["e_fondo"]
    L, prof = e["L_poza"], e["prof_poza"]
    caida = max(e["caida_fondo"], 0.0)
    h_arr = e["borde_arriba"] - e["cf_arriba"]; h_ab = e["borde_abajo"] - e["cf_abajo"]
    z_cf_ab = prof; z_cf_arr = prof + caida
    z_b_arr = z_cf_arr + h_arr; z_b_ab = z_cf_ab + h_ab
    La = 1.2                                                     # tramo de cuneta dibujado a cada lado
    # cuneta de arriba (fondo y borde)
    V.lleno([(-La - t, z_cf_arr - ef), (0, z_cf_arr - ef), (0, z_cf_arr), (-La - t, z_cf_arr)], "CONCRETO-ACHURADO", "CONCRETO")
    V.linea((-La - t, z_b_arr), (-t if e["tipo"] != "caida_corta" else 0, z_b_arr), "TERRENO")
    if e["tipo"] == "muro":
        lm = P.get("muro_espesor", 0.25)
        V.lleno([(-lm, -ef), (0, -ef), (0, z_b_arr + 0.30), (-lm, z_b_arr + 0.30)], "CONCRETO-ACHURADO", "CONCRETO")    # muro de contención
        hm = e.get("marco_alto", h_arr)
        V.poli([(-lm - 0.02, z_cf_arr), (0.02, z_cf_arr), (0.02, z_cf_arr + hm), (-lm - 0.02, z_cf_arr + hm)], "DET-CORTE")    # vano del marco
        V.lleno([(-lm, z_cf_arr + hm), (0, z_cf_arr + hm), (0, z_cf_arr + hm + t), (-lm, z_cf_arr + hm + t)], "CONCRETO-ACHURADO", "CONCRETO")
    elif e["tipo"] == "caja_caida":
        V.lleno([(-t, -ef), (0, -ef), (0, z_b_arr), (-t, z_b_arr)], "CONCRETO-ACHURADO", "CONCRETO")                  # pared de la caja
    # poza / losa de fondo reforzada
    V.lleno([(-t, -ef), (L + t, -ef), (L + t, 0), (-t, 0)], "CONCRETO-ACHURADO", "CONCRETO")
    if e["tipo"] != "caida_corta":
        V.lleno([(L, 0), (L + t, 0), (L + t, z_cf_ab), (L, z_cf_ab)], "CONCRETO-ACHURADO", "CONCRETO")               # umbral de salida
    # cuneta de abajo
    V.lleno([(L + t, z_cf_ab - ef), (L + t + La, z_cf_ab - ef), (L + t + La, z_cf_ab), (L + t, z_cf_ab)], "CONCRETO-ACHURADO", "CONCRETO")
    V.linea((0 if e["tipo"] == "caida_corta" else -t, z_b_ab), (L + t + La, z_b_ab), "TERRENO")
    # chorro y agua
    yc = e.get("yc", 0.05)
    V.poli([(0, z_cf_arr + yc), (min(e.get("Ld", L / 2), L), e.get("yp", 0.1) * 0.5)], "AGUA", cerrada=False)
    V.linea((0.02, e.get("yp", 0.1)), (L, e.get("yp", 0.1)), "AGUA")
    # cotas
    V.cota((0, -ef), (L, -ef), -8, True, "%.2f" % L)
    V.cota((L + t, 0), (L + t, z_cf_ab), 8, False, "%.2f" % prof) if prof > 0.04 else None
    V.cota((-La - t, z_cf_ab), (-La - t, z_cf_arr), -10, False, "%.2f" % caida) if caida > 0.04 else None
    lam.nivel(V.p(-La * 0.75, z_b_arr), e["borde_arriba"], "BORDE +%.2f" % e["borde_arriba"], lado=-1, hmm=1.8)
    lam.nivel(V.p(L + t + La * 0.6, z_b_ab), e["borde_abajo"], "BORDE +%.2f" % e["borde_abajo"], hmm=1.8)
    lam.nivel(V.p(-La * 0.75, z_cf_arr), e["cf_arriba"], "C.F. +%.3f" % e["cf_arriba"], lado=-1, hmm=1.8)
    lam.nivel(V.p(L + t + La * 0.6, z_cf_ab), e["cf_abajo"], "C.F. +%.3f" % e["cf_abajo"], hmm=1.8)
    sub = {"caida_corta": "ESCALON EN EL FONDO Y LOSA DE FONDO REFORZADA", "caja_caida": "CAJA DE CONCRETO ARMADO CON POZA DE DISIPACION",
           "muro": "PASE POR EL MURO CON MARCO DE C.A. Y POZA DE DISIPACION"}[e["tipo"]]
    titulo(lam, xmm + 40, ymm + (z_b_arr + 0.6) * 1000 / ESC, "%s - CORTE LONGITUDINAL" % e["codigo"], "%s - ESC. 1/%d" % (sub, ESC), ancho_mm)
    return V


def lamina(doc, codigo, ox, oy, P, ES, TV=None, con_tapa=False):
    capas(doc)
    est = [e for e in ES.get("estructuras", []) if e.get("codigo")]
    lam = B.Lamina(doc, ox, oy, ESC, codigo, "DETALLES: ESTRUCTURAS EN LOS CAMBIOS DE NIVEL" + (" Y TAPA VEHICULAR" if con_tapa else ""),
                   "CAIDA CORTA, CAJA DE CAIDA Y PASE POR MURO DE CONTENCION CON POZA DE DISIPACION - ESC. 1/%d" % ESC)
    tipos = [t for t in ("muro", "caja_caida", "caida_corta") if any(e["tipo"] == t for e in est)]
    x = 95
    for t in tipos:
        e = max((q for q in est if q["tipo"] == t), key=lambda q: q["desnivel"])
        _corte(lam, x, 300, e, P, 160)
        x += 120 + (e["L_poza"] + 2.6) * 1000 / ESC
    if est:
        filas = [[e["codigo"], e["eje"], "%.2f" % e["progresiva"], "%.2f" % e["desnivel"], "%.2f" % max(e["caida_fondo"], 0), "%.1f" % e["Q_ls"],
                  "%.2f" % e["L_poza"], "%.2f" % e["prof_poza"], "%.3f" % e["metrado"]["concreto_m3"], "%.1f" % e["metrado"]["acero_kg"]] for e in est]
        lam.tabla(45, 215, ["CODIGO", "EJE", "PROG. (m)", "DESNIVEL (m)", "CAIDA (m)", "Q (l/s)", "POZA L (m)", "POZA PROF. (m)", "CONCRETO (m3)", "ACERO (kg)"], filas,
                  [20, 20, 22, 26, 22, 20, 24, 30, 30, 24], hmm=2.0, alto_mm=6.0, titulo="CUADRO DE ESTRUCTURAS")
    if con_tapa and TV:
        b = P["b_max"]; V = Vista(lam, 560, 160)
        W = u_seccion(V, b, 0.40, P["e_muro"], P["e_fondo"], tapa=True)
        V.lleno([(0, P["e_fondo"] + 0.40), (W, P["e_fondo"] + 0.40), (W, P["e_fondo"] + 0.40 + TV["h"]), (0, P["e_fondo"] + 0.40 + TV["h"])],
                "CONCRETO-ACHURADO", "CONCRETO")
        for k in range(max(2, int(W / TV["sep"]) + 1)): V.barra((0.04 + k * (W - 0.08) / max(1, int(W / TV["sep"])), P["e_fondo"] + 0.40 + 0.05))
        V.cota((0, P["e_fondo"] + 0.40), (0, P["e_fondo"] + 0.40 + TV["h"]), -6, False, "%.2f" % TV["h"])
        titulo(lam, 560 + 40, 160 + (P["e_fondo"] + 0.40 + TV["h"] + 0.3) * 1000 / ESC, "TAPA VEHICULAR - CORTE", "ESTACIONAMIENTOS - ESC. 1/%d" % ESC, 90)
        llamadas(lam, V, [((W / 2, P["e_fondo"] + 0.40 + TV["h"] / 2), ["LOSA DE CONCRETO ARMADO f'c = 280 kg/cm2, e = %.2f" % TV["h"], TV["acero"]])],
                 560 + W * 1000 / ESC + 20, 190, 150)
    lam.notas(45, 120, "NOTAS", [
        "1. Medidas en metros. Rangos del desnivel entre plataformas: hasta 0.15 m la cuneta sigue continua; 0.15 a 0.50 m caida corta;",
        "   0.50 a 1.00 m caja de caida con poza; mas de 1.00 m (muro de contencion) pase con marco de concreto armado y poza de disipacion.",
        "2. Pozas dimensionadas para la caida vertical (USBR): largo = alcance del chorro + 6.9 (y2 - y1); la profundidad cubre el tirante conjugado.",
        "3. Concreto f'c = 210 kg/cm2 en cajas, pozas y marcos; acero fy = 4200 kg/cm2, malla 3/8\" @ 0.20 m en ambos sentidos; espesor 0.15 m.",
        "4. El agua siempre va de la plataforma alta a la baja; la cuneta de arriba llega al ras del piso hasta la cara del muro.",
    ] + (["5. En estacionamientos la cuneta va siempre tapada (sin rejilla): losa vehicular para la rueda del camion HL-93 del MTC."] if con_tapa else []),
        hmm=1.8, ancho_mm=380)
    return lam
