"""Memoria de cálculo hidrológico e hidráulico del drenaje vial en Word (MEMORIA_DRENAJE_VIAL.docx).

Mismo formato de las memorias de DrenIE (word.Doc). Cada criterio con su recuadro de fuente de la biblioteca de normas
(Manual de Hidrología, Hidráulica y Drenaje del MTC, R.D. N.° 20-2011-MTC/14). Sin nombre ni CIP del proyectista.
"""
from . import normas, word
from .vial import progresiva


def _n(v, d=2):
    return "—" if v is None else ("{:,.%df}" % d).format(v).replace(",", " ")


def _sec(s):
    if s["tipo"] == "triangular": return "Triangular, d = %.2f m, a = %.2f m (talud interior 1:%.1f, exterior 1:%.2f)" % (s["d"], float(s["a"]), s["z1"], s["z2"])
    if s["tipo"] == "trapezoidal": return "Trapezoidal, b = %.2f m, d = %.2f m (taludes 1:%.1f y 1:%.2f)" % (s["b"], s["d"], s["z1"], s["z2"])
    return "Rectangular, b = %.2f m, d = %.2f m" % (s["b"], s["d"])


def contenido(D, R):
    pr = R["proyecto"]; via = R["via"]; Pp = R["periodo_plataforma"]
    nombre = pr.get("nombre", "el proyecto")
    D.h(1, "Generalidades")
    D.h(2, "Introducción")
    D.p("La presente memoria sustenta el diseño hidrológico e hidráulico del drenaje superficial de la vía del proyecto %s%s. "
        "El drenaje longitudinal (cunetas) capta el agua de la plataforma y de los taludes adyacentes y la entrega a las alcantarillas de "
        "alivio; el drenaje transversal (alcantarillas de paso y badenes) da paso a los cursos naturales que cruzan el eje."
        % (nombre, (", " + pr["codigo"]) if pr.get("codigo") else ""))
    D.h(2, "Objetivos")
    D.vinetas(["Determinar los períodos de retorno según el riesgo admisible y la vida útil de cada tipo de obra.",
               "Obtener la precipitación máxima en 24 horas y las intensidades de diseño.",
               "Calcular los caudales de las cuencas que cruzan la vía y los aportes a las cunetas.",
               "Verificar la capacidad de las cunetas, su longitud máxima y la ubicación de las alcantarillas de alivio.",
               "Dimensionar las alcantarillas y los badenes con su borde libre y verificar las velocidades."])
    D.h(2, "Ubicación y características de la vía")
    filas = [["Proyecto", nombre]]
    for k, t in (("ubicacion", "Ubicación"), ("entidad", "Entidad"), ("codigo", "Código")):
        if pr.get(k): filas.append([t, pr[k]])
    filas += [["Velocidad de diseño", "%s km/h" % _n(float(via.get("velocidad_kmh", 40)), 0)],
              ["IMDA", "%s veh/día" % _n(float(via.get("imda", 0)), 0)],
              ["Precipitación media anual", "%s mm (región %s)" % (_n(float(via.get("precipitacion_anual_mm", 2000)), 0), R["region"].lower())],
              ["Longitud de cunetas", "%s m" % _n(R["totales"]["cunetas_m"])]]
    D.tabla("Datos generales de la vía", ["Dato", "Valor"], filas, [5.5, 10.0])
    D.h(2, "Normas y referencias")
    D.vinetas(["Manual de Hidrología, Hidráulica y Drenaje del MTC, aprobado por R.D. N.° 20-2011-MTC/14.",
               "Manual de Diseño Geométrico DG-2001 (Tabla N.° 304.12, citada por el manual anterior).",
               "Norma Técnica CE.040 Drenaje Pluvial (tiempo de concentración mínimo)."])

    # -------------------------------------------------------------- hidrología
    D.h(1, "Hidrología")
    D.h(2, "Período de retorno")
    D.p("El período de retorno se obtiene del riesgo admisible R y de la vida útil n de cada obra (Tabla N.° 02 del manual), con la ecuación:")
    D.formula("R = 1 − (1 − 1/T)ⁿ   →   T = 1 / (1 − (1 − R)^(1/n))")
    obras = {Pp["obra"]: Pp}
    for a in R["alcantarillas"] + R["badenes"]: obras.setdefault(a["periodo"]["obra"], a["periodo"])
    D.tabla("Períodos de retorno de diseño", ["Tipo de obra", "R (%)", "n (años)", "T calculado (años)", "T adoptado (años)"],
            [[o["obra"], _n(100 * o["R"], 0), o["n"], _n(o["T_calculado"], 1), o["T"]] for o in obras.values()], [7.5, 1.6, 1.8, 2.4, 2.4])
    normas.recuadro_word(D, "vial_riesgo_tabla02")
    D.h(2, "Precipitación máxima en 24 horas")
    est = (R["lluvia"].get("estacion") or {})
    D.p("Serie de precipitación máxima en 24 horas: %s%s." % (R["lluvia"]["fuente"], (" (estación " + (est.get("name") or est.get("nombre")) + ")")
                                                                if (est.get("name") or est.get("nombre")) else ""))
    D.tabla("Precipitación máxima en 24 horas por período de retorno", ["T (años)", "P24 (mm)"],
            [[t, _n(p)] for t, p in sorted(((int(t), p) for t, p in R["lluvia"]["P24_por_T"].items()))], [3, 3])
    D.h(2, "Intensidad de diseño")
    D.p("La intensidad para una duración igual al tiempo de concentración se obtiene con la relación de Dick y Peschke:")
    D.formula("P_D = P24 · (D / 1440)^0.25        I = 60 · P_D / D")
    normas.recuadro_word(D, "dick_peschke", "tc_min")
    D.h(2, "Tiempo de concentración")
    D.p("Para las cuencas que cruzan la vía se calculan las fórmulas de la Tabla N.° 05 del manual con la longitud del cauce y su desnivel; "
        "se adopta el criterio indicado en cada obra, con un mínimo de %s min. En la plataforma se usa el mínimo." % _n(R["tc_min_norma"], 0))
    D.tabla("Fórmulas del tiempo de concentración", ["Método", "tc (min)"],
            [[f[0], f[1]] for f in normas.cuadro("vial_tc_tabla05")["filas"]], [6.5, 9.0])
    D.h(2, "Coeficiente de escorrentía")
    D.p("El coeficiente de escorrentía de cada cuenca se toma de la Tabla N.° 08 del manual según la cobertura vegetal, el tipo de suelo y la "
        "pendiente del terreno, ponderado por áreas cuando hay varias coberturas.")
    normas.recuadro_word(D, "vial_C_tabla08")
    cue = [x for x in R["alcantarillas"] + R["badenes"] if x.get("hidrologia")]
    if cue:
        D.h(2, "Caudales de las cuencas")
        D.p("Para cuencas de menos de 10 km² se aplica el método racional Q = 0.278 C I A; entre 10 y 770 km², el método racional modificado de "
            "Témez (numeral 3.12.2.1).")
        filas = []
        for x in cue:
            h, c = x["hidrologia"], x["cuenca"]
            filas.append([x["id"], progresiva(x["prog"]), _n(c["area_km2"], 3), _n(c["L_m"], 0), _n(c["H_m"], 0), _n(h["C"], 3),
                          " / ".join(_n(v, 1) for v in h["tc"].values()), _n(h["tc_min"], 1), x["periodo"]["T"], _n(h["I_mmh"], 1), _n(h["Q"], 3)])
        D.tabla("Caudales de diseño de las cuencas", ["Obra", "Prog.", "A (km²)", "L (m)", "H (m)", "C", "tc por método (min)", "tc adop. (min)",
                                                      "T", "I (mm/h)", "Q (m³/s)"], filas, [1.3, 1.6, 1.3, 1.2, 1.0, 1.2, 2.6, 1.3, 0.8, 1.3, 1.4], tam=7.5)
        D.p("Los tiempos de concentración por método corresponden, en ese orden, a: " + ", ".join(cue[0]["hidrologia"]["tc"].keys()) + ".", tam=8.5)
        normas.recuadro_word(D, "vial_racional", "vial_racional_mod")

    # -------------------------------------------------------------- cunetas
    if R["cunetas"]:
        D.h(1, "Drenaje longitudinal: cunetas")
        D.h(2, "Criterios de diseño")
        D.vinetas([("Capacidad: ", "el menor de dos límites, el caudal con la cuneta llena y el caudal que produce la velocidad máxima admisible "
                                   "(ecuación 117, Manning)."),
                   ("Caudal de aporte: ", "Q = C I A / 3.6 sobre el ancho de calzada, berma, talud y ladera que llega a la cuneta, para T = %d años "
                                          "y tc = %s min." % (Pp["T"], _n(R["tc_min_norma"], 0))),
                   ("Longitud máxima: ", "la cuneta descarga en una alcantarilla de alivio antes de llenarse y, como máximo, cada 250 m (200 m en "
                                         "región muy lluviosa)."),
                   ("Pendiente: ", "entre 0.5 % (autolimpieza) y 2 %; fuera de ese rango se verifica la velocidad."),
                   ("Dimensiones mínimas: ", "las de la Tabla N.° 34 para la región; talud interior según la Tabla N.° 304.12."),
                   ("Revestimiento: ", "concreto f'c = 175 kg/cm² de 0.075 m de espesor, con berma exterior de recepción de 0.60 m.")])
        normas.recuadro_word(D, "vial_cuneta_tabla34", "vial_cuneta_longitud", "vial_cuneta_pendiente", "vial_K_tabla32", "vial_vel_tabla33")
        D.formula("Q = A · R^(2/3) · S^(1/2) / n")
        D.h(2, "Sección y capacidad")
        filas = [[c["id"], c["lado"], "%s – %s" % (progresiva(c["prog_ini"]), progresiva(c["prog_fin"])), _n(100 * c["pendiente"], 2),
                  _sec(c["seccion"]), _n(c["n"], 3), _n(c["Q_lleno"], 3), _n(c["V_lleno"]), _n(c["Vmax"]), _n(c["Q_capacidad"], 3)] for c in R["cunetas"]]
        D.tabla("Capacidad de las cunetas", ["Cuneta", "Lado", "Tramo", "S (%)", "Sección", "n", "Q llena (m³/s)", "V llena (m/s)", "V adm. (m/s)",
                                             "Q cap. (m³/s)"], filas, [1.2, 1.4, 2.6, 1.0, 4.0, 1.1, 1.3, 1.2, 1.2, 1.3], tam=7.5)
        D.h(2, "Aportes, longitud máxima y descargas")
        filas = [[c["id"], "; ".join("%s %.2f m × C %.2f" % (a.get("descripcion", ""), float(a["ancho"]), float(a["C"])) for a in c["aportes"]),
                  _n(c["I_mmh"], 1), "%.6f" % c["q_m3s_m"], _n(c["L_capacidad"], 0), _n(c["L_norma"], 0), _n(c["L_max"], 0), len(c["tramos"]) - 1]
                 for c in R["cunetas"]]
        D.tabla("Aportes y longitud máxima de las cunetas", ["Cuneta", "Aportes (ancho × C)", "I (mm/h)", "q (m³/s/m)", "L cap. (m)", "L norma (m)",
                                                             "L máx. (m)", "Alivios"], filas, [1.2, 6.0, 1.3, 1.8, 1.3, 1.3, 1.3, 1.1], tam=7.5)
        filas = [[c["id"], progresiva(t["desde"]), progresiva(t["hasta"]), progresiva(t["descarga_en"]), _n(t["longitud"], 1), _n(t["Q"], 4),
                  _n(t["tirante"], 3), _n(t["V"]), _n(t["froude"])] for c in R["cunetas"] for t in c["tramos"]]
        D.tabla("Tramos de cuneta hasta cada descarga", ["Cuneta", "Desde", "Hasta", "Descarga en", "L (m)", "Q (m³/s)", "y (m)", "V (m/s)", "Froude"],
                filas, [1.3, 1.8, 1.8, 1.9, 1.3, 1.6, 1.3, 1.3, 1.3], tam=7.5)

    # -------------------------------------------------------------- alcantarillas
    if R["alcantarillas"]:
        D.h(1, "Drenaje transversal: alcantarillas")
        D.h(2, "Criterios de diseño")
        D.vinetas([("Hidráulica: ", "régimen uniforme por Manning (ecuación 47) con el n de la Tabla N.° 09: TMC 0.024; concreto 0.013."),
                   ("Borde libre: ", "las alcantarillas no trabajan a sección llena; el tirante no pasa del 75 % del diámetro o de la altura."),
                   ("Sección mínima: ", "circular de 0.90 m (36\") o su equivalente; en selva alta con cauces en V y suelos erosionables, TMC Ø 48\"."),
                   ("Velocidad: ", "mínima 0.25 m/s para que no se sedimente; a la salida se protege el cauce con enrocado de d50 = V² / (3.1 g)."),
                   ("Caudal: ", "el de la cuenca más el de las cunetas que descargan en la alcantarilla; las de alivio llevan solo el de las cunetas.")])
        normas.recuadro_word(D, "vial_alc_manning", "vial_alc_borde", "vial_alc_dmin", "vial_alc_selva", "vial_alc_vmin", "vial_laushey")
        filas = [[a["id"], progresiva(a["prog"]), "Alivio" if a["tipo"] == "alivio" else "Paso de quebrada", a["periodo"]["T"],
                  _n(a["Q_cuencas"], 3), _n(a["Q_cunetas"], 3), _n(a["Q"], 3), a["conducto"], _n(100 * a["pendiente"], 1), _n(a["tirante_rel"], 2),
                  _n(a["V"]), _n(a["d50_salida"], 2), a["estado"]] for a in R["alcantarillas"]]
        D.tabla("Diseño de las alcantarillas", ["Obra", "Prog.", "Tipo", "T", "Q cuenca", "Q cunetas", "Q diseño (m³/s)", "Sección", "S (%)", "y/D",
                                                "V (m/s)", "d50 (m)", "Estado"], filas,
                [1.1, 1.5, 1.4, 0.7, 1.1, 1.1, 1.2, 2.1, 0.8, 0.9, 1.0, 1.0, 1.7], tam=7)
    if R["badenes"]:
        D.h(1, "Badenes")
        D.p("El badén se idealiza como un canal trapezoidal en régimen uniforme (numeral 4.1.1.4.2), con pendiente transversal de 2 a 3 % y un "
            "borde libre de 0.30 a 0.50 m entre el nivel máximo del agua y la superficie de rodadura.")
        normas.recuadro_word(D, "vial_baden_bl", "vial_baden_pt")
        filas = [[b["id"], progresiva(b["prog"]), _n(b["Q"], 3), "b = %.2f m, z = %.0f, h = %.2f m" % (b["seccion"]["b"], b["seccion"]["z1"], b["profundidad"]),
                  _n(100 * b["pendiente_transversal"], 1), _n(b["tirante"], 3), _n(b["V"]), _n(b["borde_libre"], 2), b["estado"]] for b in R["badenes"]]
        D.tabla("Diseño de los badenes", ["Obra", "Prog.", "Q (m³/s)", "Sección", "S (%)", "y (m)", "V (m/s)", "Borde libre (m)", "Estado"], filas,
                [1.2, 1.6, 1.4, 3.9, 1.0, 1.2, 1.2, 1.6, 1.7], tam=7.5)

    # -------------------------------------------------------------- resumen
    D.h(1, "Conclusiones y recomendaciones")
    t = R["totales"]
    D.vinetas(["Cunetas: %s m, con %d alcantarillas de alivio." % (_n(t["cunetas_m"]), t["alivios"]),
               "Alcantarillas de paso de quebrada: %d; badenes: %d." % (t["cruces"], t["badenes"]),
               "Obras que no cumplen: %d; obras para revisar: %d." % (t["no_cumplen"], t["revisar"]),
               "Las cunetas deben mantenerse por lo menos dos veces al año, antes y después del período de lluvias (numeral 4.1.2.1).",
               "Las descargas de las alcantarillas de alivio se ubican sin afectar áreas agrícolas ni viviendas del talud inferior; donde la "
               "velocidad de salida supere la admisible del terreno, se protege el cauce con enrocado o emboquillado de piedra."])
    if R["avisos"]:
        D.h(2, "Observaciones del cálculo")
        D.vinetas(R["avisos"])
    D.h(1, "Anexo: normas y fuentes")
    for k in ("vial_cuneta_tabla34", "vial_talud_304_12", "vial_vel_tabla33", "vial_n_tabla09"):
        q = normas.cuadro(k)
        D.tabla(q["titulo"], q["columnas"], [[str(v) for v in f] for f in q["filas"]], fuente=normas.cita_larga(k), tam=8)


def escribir(ruta, R):
    pr = dict(R["proyecto"]); pr.setdefault("nombre_corto", pr.get("nombre", "")); pr.setdefault("especialidad_documentos", "DRENAJE VIAL")
    corto = "MEMORIA DE DRENAJE VIAL"
    D0 = word.Doc(pr, corto); contenido(D0, R)
    D = word.Doc(pr, corto); D.caratula("MEMORIA DE CÁLCULO HIDROLÓGICO E HIDRÁULICO", "Drenaje vial – cunetas, alcantarillas y badenes")
    D.contenido(D0.indice); contenido(D, R)
    return D.guardar(ruta)
