"""Laminas DP-08 (cuadro de doblado, especificaciones) y DA-01 a DA-03 (detalles de partidas para el metrado)."""
import os, sys, math
from ezdxf.enums import TextEntityAlignment as TA
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import diseno as dz
import dxf_base as B
from dxf_planta import prog_txt
from dxf_secciones import geometria, seccion
import metrado_calc as MC

D = dz.D


def dp08(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 25, "DP-08", "CUADROS DE ACERO, ESPECIFICACIONES TECNICAS Y NOTAS", "CUADRO DE DOBLADO Y RESUMEN DE ACERO, ESPECIFICACIONES DE MATERIALES Y GROSORES DE IMPRESION")
    filas, t38, t12 = MC.cuadro_doblado()
    tab = [[a, b, c, d, e_, "%.1f" % f_, "%.1f" % g] for a, b, c, d, e_, f_, g in filas] + [["TOTAL", "", "", "", "", "", "%.1f" % (t38 + t12)]]
    y = lam.tabla(32, 560, ["ELEMENTO", "FORMA", "DIAMETRO", "ESPACIAM.", "LONGITUD (m)", "LONG. TOTAL (m)", "PESO (kg)"], tab, [72, 58, 18, 22, 32, 26, 22], 1.7, 4.5, "CUADRO DE DOBLADO DE ACERO")
    lam.texto(lam.P(32, y - 5), "Resumen: acero 3/8\" = %.1f kg ; acero 1/2\" = %.1f kg ; total = %.1f kg (incluye traslapes y ganchos). Angulos metalicos: %.1f kg." % (t38, t12, t38 + t12, MC.registros()["contramarco_kg"] + MC.registros()["marco_kg"]), 1.7, "TEXTOS-NOTAS")
    # figuras de marcos
    f = lam.f; be = D["b_ext"]; g = geometria(10.0); h = g["h"]; ef = D["e_fondo"]; et = D["e_losa"]
    ox_, oy_ = lam.P(60, 300); k = 1.0
    em = D["e_muro"]; w1 = be - em; h1 = ef / 2 + h + et / 2
    lam.rect(ox_, oy_, ox_ + w1 * k, oy_ + h1 * k, "ACERO")
    lam.poli([(ox_, oy_ + h1 * k), (ox_ + 0.30 * k, oy_ + h1 * k)], "ACERO", ancho=0.01)
    lam.cota((ox_, oy_), (ox_ + w1 * k, oy_), -6, texto="%.2f" % w1); lam.cota((ox_ + w1 * k, oy_), (ox_ + w1 * k, oy_ + h1 * k), 6, horizontal=False, texto="h + %.3f" % (ef / 2 + et / 2))
    lam.texto((ox_ + 0.05, oy_ + h1 * k + 0.08), "gancho 0.30", 1.6, "TEXTOS")
    lam.titulo_vista(85, 275, "MARCO UNICO 3/8\" (tramo normal @0.20, motos @0.15)", "un marco cerrado en el eje de muros y losas: %.2f x (h + %.3f); gancho de 0.30 m; una capa (E.060 14.3.4)" % (w1, ef / 2 + et / 2), 150)
    ox_, oy_ = lam.P(300, 300)
    efc = D["e_losa_camion"]
    lam.rect(ox_, oy_, ox_ + (be - 0.08) * k, oy_ + (ef + h + efc - 0.08) * k, "ACERO")
    lam.rect(ox_ + 0.11 * k, oy_ + (ef - 0.04) * k, ox_ + (be - 0.08 - 0.22) * k, oy_ + (ef + h + 0.04 - 0.08) * k, "ACERO")
    lam.poli([(ox_, oy_ + (ef + h + efc - 0.08) * k), (ox_ + 0.30 * k, oy_ + (ef + h + efc - 0.08) * k)], "ACERO", ancho=0.01)
    lam.cota((ox_, oy_), (ox_ + (be - 0.08) * k, oy_), -6, texto="1.02"); lam.cota((ox_ + (be - 0.08) * k, oy_), (ox_ + (be - 0.08) * k, oy_ + (ef + h + efc - 0.08) * k), 6, horizontal=False, texto="h + 0.32")
    lam.titulo_vista(325, 275, "MARCO DOBLE 1/2\" @0.15 (cruce de camiones)", "marco exterior 1.02 x (h + 0.32) y marco interior 0.80 + 0.22 x (h + 0.08); una capa en cada cara; losa superior e=0.25", 150)
    # especificaciones
    esp = ["CONCRETO ARMADO: f'c = 210 kg/cm2 (colector, cajas y tapas). Cemento tipo I; agregados limpios; slump 3\" a 4\".",
           "CONCRETO SIMPLE: solado f'c = 100 kg/cm2, e = 0.05 m; umbral de la poza f'c = 210 kg/cm2 vaciado con la losa de fondo.",
           "ACERO DE REFUERZO: fy = 4200 kg/cm2 (grado 60), corrugado. Ganchos de 0.30 m en marcos y 0.40 m en esquinas de cajas.",
           "RECUBRIMIENTOS: 0.04 m en muros y losa de fondo; 0.025 m en losa superior del tramo normal; 0.04 m en el cruce de camiones; 0.025 m en tapas.",
           "TRASLAPES: 3/8\" = 0.40 m ; 1/2\" = 0.50 m, alternados. Barras longitudinales de 9.00 m.",
           "LOSA SUPERIOR: vaciada monoliticamente con los muros en todo el colector; acabado frotachado y brunado (a nivel del piso terminado +260.60).",
           "REGISTROS: marco y contramarco de angulo 2\"x2\"x3/16\" y 1 1/2\"x1 1/2\"x1/8\" con anclajes, pintura anticorrosiva y esmalte; tapas de concreto 0.68 x 0.68 x 0.08 con asas.",
           "JUNTAS: cada 4.00 m, e = 1\", relleno de poliestireno expandido y sello elastomerico de poliuretano. Tecnopor de 1\" entre el colector y el cerco, las cunetas y el piso adyacente.",
           "CAJAS: muros e = 0.15 y losa de fondo e = 0.15 con malla 3/8\" @0.20 en ambas caras; umbral 0.25 x 0.40 en la caja de caida.",
           "CURADO: humedo minimo 7 dias; no transitar sobre la losa antes de 14 dias; no cargar con camiones antes de 28 dias.",
           "RELLENO: material propio seleccionado, capas de 0.15 m, 95 % del Proctor modificado; incluye la nivelacion del retiro hasta la cota de la losa.",
           "EXCAVACION: zanja de 1.60 m de ancho (0.25 m a cada lado del muro); entibar si la profundidad supera 1.50 m o el suelo lo requiere.",
           "VERIFICAR la cota de llegada del colector de CAR Varones (CUI 2705619) antes de vaciar la caja de llegada; verificar en campo la ubicacion del R-01 del CAR Mujeres (CUI 2717013)."]
    lam.notas(440, 560, "ESPECIFICACIONES TECNICAS", esp, 1.7)
    ctb = ["color  94   concreto (cortes y contornos)      0.40 mm", "color   1   acero transversal (marcos)         0.30 mm", "color   5   acero longitudinal y progresivas   0.30 mm",
           "color  32   registros y marcos metalicos       0.30 mm", "color   6   cotas, cortes y lindero            0.18 mm", "color  14   cerco perimetrico                  0.30 mm",
           "color   7   textos, titulos, piso terminado    0.25 mm", "color   3   cunetas                            0.25 mm", "color  30   tapas y cruces vehiculares         0.18 mm",
           "color  34   poza y umbral                      0.18 mm", "color 150   agua y flujo                       0.13 mm", "color   8   achurados, auxiliares y arq. base  0.09 mm",
           "color   9   grillas                            0.05 mm", "caras de isometricos y agua: color verdadero (RGB), plumilla 0.05 mm"]
    lam.notas(440, 470 - 4.2 * len(esp) + 8, "GROSOR DE PLUMILLA POR COLOR (CTB)", ctb, 1.7)
    notas = ["1. Dimensiones en metros y cotas en m.s.n.m., salvo indicacion.", "2. El colector esta dimensionado para 560.6 L/s (CAR Varones 258.7 + Hogar de Refugio 301.9; TR 25 anos).",
             "3. Verificaciones hidraulica y estructural segun memoria de calculo del proyecto (RNE CE.040, E.020, E.060; AASHTO LRFD HL-93).",
             "4. Las cunetas de arquitectura (perfiles 01 a 12) y sus cotas de fondo son datos del plano PLANTA GENERAL REFUGIO (03-10-2026).",
             "5. Confirmar la capacidad portante con el estudio de mecanica de suelos antes del vaciado (presion de contacto 0.33 kg/cm2)."]
    lam.notas(32, 215, "NOTAS GENERALES", notas, 1.7)
    return lam


def da(doc, ox, oy, R, T):
    """DA-01: partidas de movimiento de tierras; DA-02: concreto y encofrado; DA-03: acero, registros y juntas."""
    lams = []
    Tr, Rs = MC.resumen()
    # ---------------- DA-01
    lam = B.Lamina(doc, ox, oy, 25, "DA-01", "DETALLE DE PARTIDAS: TRAZO, EXCAVACION, RELLENO Y ELIMINACION", "SECCION TIPICA DE ZANJA POR ZONA Y RESUMEN DE METRADO - ESC. 1/25")
    f = lam.f
    for j, (p, nm) in enumerate(((10.0, "ZANJA TIPICA - TRAMO NORMAL"), (28.8, "ZANJA - CRUCE DE CAMIONES"), (65.0, "ZANJA - TRAMO DIAGONAL"))):
        xmm = 120 + j * 230; ymm = 330
        s = seccion(lam, xmm, ymm, p, R, T, llamadas=False, con_cerco=True)
        g = s["g"]; cy = s["cy"]; xl, xr, zs = s["xl"], s["xr"], s["zs"]
        zt = zs - (D["NPT"] - float(__import__("numpy").interp(p, [t["p"] for t in T], [t["z"] for t in T])))
        # zanja: ancho be + 0.50, desde el terreno hasta el fondo del solado
        lam.poli([(xl - 0.25, zt), (xl - 0.25, cy - 0.05), (xr + 0.25, cy - 0.05), (xr + 0.25, zt)], "EXCAVACION", ancho=0.006)
        lam.achurado([(xl - 0.25, zt), (xl - 0.25, cy - 0.05), (xl, cy - 0.05), (xl, zt)], "RELLENO", escala_mm=0.4)
        lam.achurado([(xr, zt), (xr, cy - 0.05), (xr + 0.25, cy - 0.05), (xr + 0.25, zt)], "RELLENO", escala_mm=0.4)
        lam.achurado([(xl - 1.25, zt), (xl - 0.25, zt), (xl - 0.25, zs), (xl - 1.25, zs)], "RELLENO", escala_mm=0.4)
        lam.cota((xl - 0.25, cy - 0.05), (xr + 0.25, cy - 0.05), -14, texto="1.60"); lam.cota((xl - 0.25, cy - 0.05), (xl - 0.25, zt), -14, horizontal=False, texto="Hz")
        lam.cota((xl - 1.25, zs), (xl - 0.25, zs), 6, texto="1.00")
        xt = xr + 0.95
        lam.llamada((xl - 0.12, (zt + cy) / 2), (xt, zs + 0.2), ["relleno lateral de zanja: 2 x 0.25 x Hz (material propio compactado)"], 1.8)
        lam.llamada((xl - 0.75, (zt + zs) / 2), (xt, zs - 0.2), ["relleno de nivelacion del retiro: franja de 1.00 m hasta +260.60 (dentro de la partida de relleno)"], 1.8)
        lam.llamada((xr + 0.25, cy + 0.3), (xt, zs - 0.6), ["excavacion de zanja 1.60 x Hz (Hz = terreno - fondo del solado)"], 1.8)
        lam.llamada((xl - 0.25, zs - 0.05), (xt, zs - 1.0), ["trazo y replanteo: franja de 1.60 m"], 1.8)
        lam.llamada((s["cx"], cy + 0.03), (xt, zs - 1.4), ["refine y nivelacion del fondo: ancho 1.20 (solado)"], 1.8)
        lam.titulo_vista(xmm + 15, ymm - 55, nm, "PROG. %s - ESC. 1/25" % prog_txt(p), 150)
    filas = [["Trazo, niveles y replanteo", "m2", "%.2f" % Rs["trazo_m2"], "franja de 1.60 m x L + cajas"],
             ["Excavacion de zanja", "m3", "%.2f" % Rs["excav_m3"], "1.60 x Hz x L por tramo (Hz desde el terreno existente) + cajas"],
             ["Refine y nivelacion de fondo", "m2", "%.2f" % Rs["refine_m2"], "1.20 x L + cajas"],
             ["Relleno compactado con material propio", "m3", "%.2f" % Rs["relleno_m3"], "relleno lateral de zanja + franja de nivelacion del retiro (1.00 m) + cajas"],
             ["Eliminacion de material excedente", "m3", "%.2f" % Rs["elimin_m3"], "(excavacion - relleno) x 1.25"]]
    lam.tabla(32, 200, ["PARTIDA", "UND", "METRADO", "CRITERIO"], filas, [70, 12, 22, 170], 1.7, 4.8, "RESUMEN DE MOVIMIENTO DE TIERRAS")
    lam.notas(32, 150, "NOTAS", ["1. Hz varia con el terreno existente (superficie topografica) y la cota de fondo del colector; ver tabla de tramos en la planilla de metrados.",
                                  "2. Criterio: los rellenos menores (nivelacion de la franja adyacente, base de las cajas) van dentro de la partida de relleno, no como partida aparte.",
                                  "3. Donde el terreno existente queda por debajo de la losa, el muro lado via se vacia con encofrado exterior y luego se rellena."], 1.7)
    lams.append(lam)
    # ---------------- DA-02
    lam = B.Lamina(doc, ox + 30, oy, 25, "DA-02", "DETALLE DE PARTIDAS: SOLADO, CONCRETO ARMADO Y ENCOFRADO", "AREAS Y VOLUMENES POR METRO LINEAL EN CADA ZONA - ESC. 1/25")
    for j, (p, nm) in enumerate(((10.0, "TRAMO NORMAL"), (40.0, "CRUCE DE MOTOS"), (28.8, "CRUCE DE CAMIONES"))):
        xmm = 120 + j * 230; ymm = 330
        s = seccion(lam, xmm, ymm, p, R, T, llamadas=False, con_cerco=False)
        g = s["g"]; be = D["b_ext"]; h = g["h"]; et = g["et"]; ef = D["e_fondo"]
        xt = s["xr"] + 0.5
        lam.llamada((s["cx"] + 0.3, s["zs"] - et / 2), (xt, s["zs"] + 0.3), ["losa superior: %.2f x %.2f = %.3f m3/m" % (be, et, be * et)], 1.8)
        lam.llamada((s["xr"] - D["e_muro"] / 2, s["zf"] + h / 2), (xt, s["zs"] - 0.1), ["muros: 2 x 0.15 x %.2f = %.3f m3/m" % (h, 2 * 0.15 * h)], 1.8)
        lam.llamada((s["cx"] + 0.3, s["zf"] - ef / 2), (xt, s["zs"] - 0.5), ["losa de fondo: %.2f x %.2f = %.3f m3/m" % (be, ef, be * ef)], 1.8)
        lam.llamada((s["cx"] + 0.4, s["cy"] + 0.025), (xt, s["zs"] - 0.9), ["solado: 1.20 m2/m"], 1.8)
        lam.llamada((s["xl"] + D["e_muro"] + 0.02, s["zf"] + h * 0.7), (xt, s["zs"] - 1.3), ["encofrado: caras interiores 2 x %.2f + exteriores 2 x %.2f + fondo de losa 0.80 = %.2f m2/m" % (h, ef + h + et, 2 * h + 2 * (ef + h + et) + 0.80)], 1.8)
        lam.llamada((s["cx"], s["zs"]), (xt, s["zs"] - 1.7), ["acabado frotachado y brunado: 1.10 m2/m"], 1.8)
        lam.titulo_vista(xmm + 15, ymm - 55, nm, "PROG. %s - h = %.2f m - ESC. 1/25" % (prog_txt(p), h), 150)
    filas = [["Solado f'c=100 e=0.05", "m2", "%.2f" % Rs["solado_m2"]], ["Concreto f'c=210 - losa de fondo", "m3", "%.2f" % Rs["conc_fondo_m3"]],
             ["Concreto f'c=210 - muros", "m3", "%.2f" % Rs["conc_muros_m3"]], ["Concreto f'c=210 - losa superior (incluye bordes de registro)", "m3", "%.2f" % Rs["conc_losa_m3"]],
             ["Encofrado y desencofrado", "m2", "%.2f" % Rs["encof_m2"]], ["Acabado frotachado y brunado de losa superior", "m2", "%.2f" % Rs["acabado_m2"]]]
    lam.tabla(32, 200, ["PARTIDA", "UND", "METRADO"], filas, [110, 16, 26], 1.7, 4.8, "RESUMEN DE CONCRETO Y ENCOFRADO (colector + cajas)")
    lams.append(lam)
    # ---------------- DA-03
    lam = B.Lamina(doc, ox + 60, oy, 25, "DA-03", "DETALLE DE PARTIDAS: ACERO, REGISTROS, JUNTAS Y EMPALMES", "DESPIECE POR METRO, INSUMOS POR REGISTRO Y LONGITUDES DE JUNTA - ESC. 1/25")
    Rg = Rs["registros"]; J = Rs["juntas"]
    for j, (p, nm) in enumerate(((10.0, "TRAMO NORMAL @0.20"), (40.0, "CRUCE DE MOTOS @0.15"), (28.8, "CRUCE DE CAMIONES 1/2\" @0.15 DOBLE"))):
        xmm = 120 + j * 230; ymm = 330
        s = seccion(lam, xmm, ymm, p, R, T, llamadas=False, con_cerco=False)
        g = s["g"]; be = D["b_ext"]; h = g["h"]; et = g["et"]; ef = D["e_fondo"]
        tr = [t for t in Tr if t["p1"] <= p < t["p2"]][0]
        xt = s["xr"] + 0.5
        lam.llamada((s["xr"] - 0.04, s["zf"] + h / 2), (xt, s["zs"] + 0.3), ["marcos %s: %d capa(s), %.2f m por juego" % (tr["marcos_dia"] + '"', 2 if tr["zona"] == "CAMION" else 1, tr["marcos_L"] / tr["marcos_n"])], 1.8)
        lam.llamada((s["xl"] + 0.04, s["zf"] + h / 2), (xt, s["zs"] - 0.1), ["= %.1f kg/m" % (tr["marcos_kg"] / tr["L"])], 1.8)
        lam.llamada((s["cx"], s["zs"] - 0.04), (xt, s["zs"] - 0.5), ["longitudinales 3/8\": %d barras = %.1f kg/m (con traslape 0.40 cada 9.00 m)" % (tr["long_n"], tr["long_kg"] / tr["L"])], 1.8)
        lam.llamada((s["cx"], s["zf"] + 0.04), (xt, s["zs"] - 0.9), ["total acero: %.1f kg/m" % ((tr["marcos_kg"] + tr["long_kg"]) / tr["L"])], 1.8)
        lam.titulo_vista(xmm + 15, ymm - 55, nm, "PROG. %s - ESC. 1/25" % prog_txt(p), 150)
    filas = [["Acero fy=4200 colector y cajas - 3/8\"", "kg", "%.1f" % Rs["acero_38_kg"]], ["Acero fy=4200 colector - 1/2\" (cruce de camiones)", "kg", "%.1f" % Rs["acero_12_kg"]],
             ["Registros: contramarco L 2\"x2\"x3/16\" (%d und)" % Rg["n"], "kg", "%.1f" % Rg["contramarco_kg"]], ["Registros: marco de tapa L 1 1/2\"x1 1/2\"x1/8\"", "kg", "%.1f" % Rg["marco_kg"]],
             ["Tapas de concreto 0.68 x 0.68 x 0.08", "und / m3", "%d / %.2f" % (Rg["n"], Rg["tapa_conc"])], ["Acero en tapas, bordes, asas y anclajes", "kg", "%.1f" % (Rg["acero_borde_kg"] + Rg["acero_tapa_kg"] + Rg["asas_kg"] + Rg["anclajes_kg"])],
             ["Pintura anticorrosiva y esmalte en angulos", "m2", "%.2f" % Rg["pintura_m2"]],
             ["Junta de dilatacion e=1\" con sello (%d und x %.2f m)" % (J["n"], J["L_dilat"] / J["n"]), "m", "%.2f" % J["L_dilat"]],
             ["Junta de tecnopor e=1\" con el cerco (muro)", "m", "%.2f" % J["L_tecnopor_cerco"]], ["Junta de tecnopor e=1\" con el piso adyacente", "m", "%.2f" % J["L_tecnopor_piso"]],
             ["Empalme de cuneta al colector (ventana + caida)", "und", "%d" % Rs["empalmes"]]]
    lam.tabla(32, 200, ["PARTIDA", "UND", "METRADO"], filas, [120, 18, 26], 1.7, 4.6, "RESUMEN DE ACERO, REGISTROS, JUNTAS Y EMPALMES")
    lams.append(lam)
    return lams


def todas(doc, ox, oy, R, T):
    return [dp08(doc, ox, oy, R, T)] + da(doc, ox + 30, oy, R, T)
