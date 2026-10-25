"""Lámina de detalle de las descargas sin gravedad: pozo de absorción (infiltración) y cámara de bombeo, a escala real
(1 unidad = 1 m), con planta, corte, niveles, cuadro de diseño y notas con las normas (IS.020, IS.010, OS.080, CE.040)."""
import math

from . import dxf_base as B
from .detalles import Vista, capas, titulo

ESC = 50


def sep_planta(d):
    """Distancia en mm del eje del corte al centro de la planta del pozo: sin cruzar dibujos ni títulos."""
    return max((d["De"] + 3.0) * 1000 / ESC, 135.0)


def _pozo(lam, xmm, ymm, d, P):
    """Corte y planta de un pozo de absorción (origen del corte: centro del fondo)."""
    V = Vista(lam, xmm, ymm)
    Di, De = d["Di"], d["De"]; e = (De - Di) / 2; g = 0.25
    H = d["H_absorcion"]; libre = 0.30; z0 = d["cota_fondo"]
    prof = d["profundidad_total"]; top = prof                     # el terreno está a «prof» sobre el fondo
    r_i, r_e = Di / 2, De / 2
    V.lleno([(-r_e - g, 0), (-r_e, 0), (-r_e, H + libre), (-r_e - g, H + libre)], "SEC-SOLADO", "CONCRETO")       # grava
    V.lleno([(r_e, 0), (r_e + g, 0), (r_e + g, H + libre), (r_e, H + libre)], "SEC-SOLADO", "CONCRETO")
    V.lleno([(-r_e, 0), (-r_i, 0), (-r_i, top - 0.15), (-r_e, top - 0.15)], "CONCRETO-ACHURADO", "CONCRETO")      # muro
    V.lleno([(r_i, 0), (r_e, 0), (r_e, top - 0.15), (r_i, top - 0.15)], "CONCRETO-ACHURADO", "CONCRETO")
    V.lleno([(-r_e - g, top - 0.15), (r_e + g, top - 0.15), (r_e + g, top), (-r_e - g, top)], "CONCRETO-ACHURADO", "CONCRETO")  # losa
    V.rect(-0.30, top - 0.15, 0.30, top, "DET-CORTE")                                                          # tapa 0.60
    V.linea((-r_e - g - 1.0, top), (r_e + g + 1.0, top), "TERRENO")
    hl = d["cota_llegada"] - z0
    V.poli([(-r_e - g - 1.0, hl), (-r_i, hl)], "DET-CORTE", cerrada=False)                                      # tubería de llegada
    V.linea((-r_i, d["h_max"]), (r_i, d["h_max"]), "AGUA")
    V.cota((-r_e - g, -0.10), (r_e + g, -0.10), -6, True, "%.2f" % (De + 2 * g))
    V.cota((r_e + g + 0.3, 0), (r_e + g + 0.3, H), 8, False, "%.2f" % H)
    V.cota((r_e + g + 0.3, H), (r_e + g + 0.3, top), 8, False, "%.2f" % (top - H))
    lam.nivel(V.p(-r_e - g - 0.6, hl), d["cota_llegada"], "LLEGADA +%.3f" % d["cota_llegada"], lado=-1, hmm=1.8)
    lam.nivel(V.p(-r_i + 0.2, d["h_max"]), z0 + d["h_max"], "N.A. MAX. +%.3f" % (z0 + d["h_max"]), hmm=1.8)
    lam.nivel(V.p(r_e + g + 0.2, 0), z0, "FONDO +%.3f" % z0, hmm=1.8)
    yt = ymm + max(top + 1.0, top / 2 + r_e + g + 1.0) * 1000 / ESC
    titulo(lam, xmm, yt, "POZO DE ABSORCION %s - CORTE" % d["D"], "%d POZO(S) DE D = %.2f m - ESC. 1/%d" % (d["n"], Di, ESC), 120)
    # planta
    dx = sep_planta(d)
    W = Vista(lam, xmm + dx, ymm + (top / 2) * 1000 / ESC)
    W.circ((0, 0), r_e + g, "SEC-SOLADO"); W.circ((0, 0), r_e, "CONCRETO"); W.circ((0, 0), r_i, "CONCRETO"); W.rect(-0.30, -0.30, 0.30, 0.30, "DET-CORTE")
    titulo(lam, xmm + dx, yt, "POZO %s - PLANTA" % d["D"], "ESC. 1/%d" % ESC, 80)
    return top


def _camara(lam, xmm, ymm, d, P):
    """Corte de la cámara de bombeo con sus niveles (origen: interior del fondo, cara izquierda)."""
    V = Vista(lam, xmm, ymm)
    L = d["lado_m"]; e, ef, el = 0.20, 0.25, 0.20
    z0 = d["cota_fondo"]; top = d["profundidad_m"]
    V.lleno([(-e, -ef), (L + e, -ef), (L + e, 0), (-e, 0)], "CONCRETO-ACHURADO", "CONCRETO")
    V.lleno([(-e, 0), (0, 0), (0, top - el), (-e, top - el)], "CONCRETO-ACHURADO", "CONCRETO")
    V.lleno([(L, 0), (L + e, 0), (L + e, top - el), (L, top - el)], "CONCRETO-ACHURADO", "CONCRETO")
    V.lleno([(-e, top - el), (L + e, top - el), (L + e, top), (-e, top)], "CONCRETO-ACHURADO", "CONCRETO")
    V.rect(L / 2 - 0.40, top - el, L / 2 + 0.40, top, "DET-CORTE")                                              # tapa de acceso
    V.linea((-e - 1.0, top), (L + e + 1.0, top), "TERRENO")
    for k, x in enumerate((L * 0.30, L * 0.70)):                                                                 # bombas sumergibles
        V.rect(x - 0.20, 0.05, x + 0.20, 0.55, "DET-CORTE")
        V.poli([(x, 0.55), (x, top + 0.30)], "DET-CORTE", cerrada=False)
    hl = d["cota_llegada"] - z0
    V.poli([(-e - 1.0, hl), (0, hl)], "DET-CORTE", cerrada=False)
    for cota, txt, lado in ((d["n_alarma"], "ALARMA", -1), (d["n_arranque"], "ARRANQUE", 1), (d["n_parada"], "PARADA", 1)):
        V.linea((0.05, cota - z0), (L - 0.05, cota - z0), "AGUA")
        lam.nivel(V.p(L + e + 0.2 if lado > 0 else -e - 1.6, cota - z0), cota, "%s +%.3f" % (txt, cota), lado=lado, hmm=1.6)
    lam.nivel(V.p(-e - 0.6, hl + 0.25), d["cota_llegada"], "LLEGADA +%.3f" % d["cota_llegada"], lado=-1, hmm=1.8)
    lam.nivel(V.p(L + e + 0.2, 0), z0, "FONDO +%.3f" % z0, hmm=1.8)
    V.cota((0, -ef - 0.05), (L, -ef - 0.05), -6, True, "%.2f" % L)
    V.cota((-e - 0.3, 0), (-e - 0.3, top), -8, False, "%.2f" % top)
    titulo(lam, xmm + L / 2 * 1000 / ESC, ymm + (top + 1.0) * 1000 / ESC, "CAMARA DE BOMBEO %s - CORTE" % d["D"], "%.2f x %.2f m - 2 BOMBAS SUMERGIBLES - ESC. 1/%d" % (L, L, ESC), 130)
    return top


def lamina(doc, codigo, ox, oy, P, DA):
    capas(doc)
    lam = B.Lamina(doc, ox, oy, ESC, codigo, "DETALLES: DESCARGA SIN GRAVEDAD (POZOS DE ABSORCION / CAMARA DE BOMBEO)",
                   "PLANTA, CORTE, NIVELES Y CUADRO DE DISEÑO - ESC. 1/%d" % ESC)
    # vistas en filas de arriba hacia abajo, sin pasar al cuadro ni al rótulo
    k = 1000.0 / ESC; vistas = []
    for D, d in sorted(DA.items()):
        if d.get("tipo") == "pozo de absorción":
            r = d["De"] / 2 + 0.25; top = d["profundidad_total"]
            izq = (r + 1.0) * k + 32; ancho = izq + sep_planta(d) + r * k + 12
            alto = max(top + 1.0, top / 2 + r + 1.0) * k + 12; vistas.append((_pozo, d, izq, ancho, alto))
        else:
            top = d["profundidad_m"]; izq = 2.0 * k + 34; ancho = izq + (d["lado_m"] + 0.6) * k + 40
            vistas.append((_camara, d, izq, ancho, (top + 1.0) * k + 12))
    y_tabla = 95 + 14 + 6.0 * (len(DA) + 1); y_min = y_tabla + 22        # el cuadro crece hacia arriba con las filas, sobre las notas
    x0, xmax, ytop, omitidas = 45, 790, 560, []
    filas_v = [[]]
    for v in vistas:                                                       # reparto en filas por ancho
        if filas_v[-1] and x0 + sum(w[3] + 15 for w in filas_v[-1]) + v[3] > xmax: filas_v.append([])
        filas_v[-1].append(v)
    for fila in filas_v:
        base = ytop - max(v[4] for v in fila); x = x0
        if base < y_min: omitidas += [v[1]["D"] for v in fila]; continue
        for f, d, izq, ancho, alto in fila: f(lam, x + izq, base, d, P); x += ancho + 15
        ytop = base - 22
    filas = []
    for D, d in sorted(DA.items()):
        if d.get("tipo") == "pozo de absorción":
            filas.append([D, "Pozo de absorción", "%d de D = %.2f m" % (d["n"], d["Di"]), "%.2f" % d["profundidad_total"], "%.3f" % d["cota_fondo"],
                          "%.1f min/cm (%s)" % (d["test_min_por_cm"], d["clase"]), "%.0f mm/h" % d["f_mmh"], "%.1f m³" % d["volumen_tormenta_m3"]])
        else:
            filas.append([D, "Cámara de bombeo", "%.2f × %.2f m" % (d["lado_m"], d["lado_m"]), "%.2f" % d["profundidad_m"], "%.3f" % d["cota_fondo"],
                          "2 × %.1f l/s" % d["Qb_ls"], "ADT %.1f m" % d["TDH_m"], "%s HP; PVC %d\"" % (("%g" % d["motor_HP"]), d["D_impulsion_pulg"])])
    lam.tabla(45, y_tabla, ["DESCARGA", "SOLUCION", "MEDIDAS", "PROF. (m)", "COTA DE FONDO", "DATO", "TASA / ALTURA", "VOLUMEN / EQUIPO"], filas,
              [20, 30, 30, 18, 24, 34, 24, 34], hmm=1.8, alto_mm=6.0, titulo="CUADRO DE DESCARGAS SIN GRAVEDAD")
    lam.notas(45, 95, "NOTAS", [
        "1. Medidas en metros. Se usa solo donde el agua no sale por gravedad (CE.040, art. 21).",
        "2. Pozo de absorción (IS.020, arts. 17, 20 y 21): muro de mampostería con juntas abiertas, anillo de grava de 1\", losa con tapa de",
        "   0.60 m; fondo a 2 m sobre la napa como mínimo; separación entre pozos de 6 m; diseño con el test de percolación del lugar.",
        "3. Cámara de bombeo (IS.010 6.4 y 7.1 f; OS.080): dos bombas sumergibles alternadas con el caudal pico, rejilla a la entrada,",
        "   válvulas de compuerta y de retención, control por niveles con alarma, grupo electrógeno o rebose de emergencia.",
        "4. Concreto f'c = 210 kg/cm2 en losas y cámara; acero fy = 4200 kg/cm2, malla 3/8\" @ 0.20 m en ambas caras.",
    ] + (["5. %s: mismo detalle con las medidas del cuadro." % ", ".join(omitidas)] if omitidas else []), hmm=1.8, ancho_mm=380)
    return lam
