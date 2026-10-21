"""Memorias de drenaje pluvial (Word) de la I.E. N.° 0590 Barranquita (C.I. 468901):
- MEMORIA_HIDROLOGICA_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx
- MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx
Datos: hidrologia_b (lluvia transpuesta de Tarapoto), verificacion.json, diseno.json, cantidades_b (metrado) e indice de planos.
"""
import os, sys, json, re
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import hidrologia_b as H, diseno_b as DS, cantidades_b as Q, figuras_b as FG
from word_b import Doc
import hidrologica_doc_b as HD

ENT = os.path.join(RAIZ, "entregables_barranquita"); CALC = os.path.join(ENT, "_calc")
fig = lambda n: os.path.join(FG.DIR, n)
f2 = lambda v: ("%.2f" % v)
mil = lambda v, d=2: ("{:,.%df}" % d).format(v)


def limpio(t):
    """Quita las coordenadas de los textos de ubicacion (x = 820.1, etc.)."""
    t = re.sub(r",?\s*x\s*=\s*[\d.]+", "", t); t = re.sub(r"\(\s*\)", "", t); t = t.replace("( ", "(").replace(" )", ")")
    return re.sub(r"\s+", " ", t).strip()


def contexto():
    HID = H.resultados(); A = HID["analisis"]
    V = json.load(open(os.path.join(CALC, "verificacion.json"))); R = json.load(open(os.path.join(CALC, "diseno.json")))
    ind = json.load(open(os.path.join(CALC, "indice.json"))); q = Q.por_eje(); dsc = {d["D"]: d for d in V["descargas"]}
    hv = V["hidrologia"]; hid = V["hidraulica"]
    por_eje = {}
    for f in hid:
        e = por_eje.setdefault(f["ramal"], {"Q": 0, "A": 0, "y": 0, "V": 0, "bl": 9, "h": 0, "S": 0, "C": 0})
        if f["Q_ls"] >= e["Q"]: e.update(Q=f["Q_ls"], A=f["A_m2"], y=f["y"], h=f["h"], S=f["S"], C=f.get("C", hv["C"]))
        e["V"] = max(e["V"], f["V"]); e["bl"] = min(e["bl"], f["borde_libre"])
    sis = {}
    for r in R["ramales"]:
        s = sis.setdefault(r["sistema"], {"ejes": [], "L": 0.0, "D": DS.SISTEMAS[r["sistema"]][1], "nom": DS.SISTEMAS[r["sistema"]][0]})
        s["ejes"].append(r["codigo"]); s["L"] += r["L"]
    return dict(HID=HID, A=A, V=V, R=R, ind=ind, q=q, dsc=dsc, hv=hv, hid=hid, por_eje=por_eje, sis=sis,
                Qmax=max(f["Q_ls"] for f in hid), Vmax=max(f["V"] for f in hid), BLmin=min(f["borde_libre"] for f in hid),
                L=sum(r["L"] for r in R["ramales"]), Ltap=sum(x["L_tapado"] for x in q), tapas=sum(x["tapas"] for x in q),
                hmax=max(x["h_max"] for x in q), FIG=FG.DIR)


# ============================================================================== MEMORIA HIDROLOGICA
def hidrologica(D, c):
    HID, A, hv = c["HID"], c["A"], c["hv"]
    D.h(1, "Generalidades")
    D.h(2, "Introducción")
    D.p("La presente memoria hidrológica sustenta el dimensionamiento del sistema de drenaje pluvial (red de cunetas) del proyecto "
        "“Mejoramiento y ampliación del servicio de educación primaria en I.E. N° 0590 distrito de Barranquita de la provincia de Lamas "
        "del departamento de San Martín”, con código de idea C.I. N° 468901. Barranquita se ubica en la llanura amazónica del valle del "
        "Caynarachi, con clima tropical húmedo (Af de Köppen-Geiger), precipitaciones durante todo el año y tormentas intensas de corta "
        "duración, especialmente entre febrero y abril. Por ello la evacuación ordenada de las aguas de lluvia de techos, veredas, patios "
        "y áreas libres es indispensable para proteger las edificaciones, los pisos y las circulaciones del local educativo.")
    D.h(2, "Objetivos")
    D.vinetas(["Seleccionar la información pluviométrica representativa y trasladarla a las condiciones de Barranquita.",
               "Determinar la precipitación máxima en 24 horas para el periodo de retorno de diseño mediante el análisis de frecuencias.",
               "Obtener las lluvias de corta duración, las intensidades y las curvas intensidad - duración - frecuencia (IDF).",
               "Determinar los coeficientes de escorrentía, las áreas de aporte y los caudales de diseño de cada tramo de cuneta.",
               "Verificar la capacidad hidráulica, la velocidad y las descargas de la red de cunetas de 0.60 m de ancho total (0.40 m libres)."])
    D.h(2, "Ubicación del proyecto")
    D.tabla("Ubicación del proyecto", ["Descripción", "Dato"],
            [["Departamento", "San Martín"], ["Provincia", "Lamas"], ["Distrito", "Barranquita"], ["Localidad", "Barranquita"],
             ["Predio", "Mz Z Lote 23 (área educación), partida registral N° 11128704"],
             ["Colindancias", "Av. Vía de Evitamiento, Jr. Alfonso Ugarte C-3, Jr. Amazonas C-07 y C-08 y propiedad de terceros"],
             ["Altitud del local (NPT)", "+184.65 m s. n. m."],
             ["Acceso", "Tarapoto - Pongo de Caynarachi - Barranquita, carretera asfaltada de 95 km (2 h 25 min aprox.)"]],
            [5, 10.5], fuente="Memoria descriptiva de arquitectura del proyecto.")
    D.h(2, "Alcance")
    D.p("El estudio comprende el área de intervención delimitada por el cerco perimétrico del local (%s m²), donde se emplazan los "
        "pabellones, la losa deportiva, el patio de maniobra y las áreas libres. Las aguas de lluvia de las coberturas llegan a las cunetas "
        "mediante canaletas y montantes, y las de pisos y áreas libres por escurrimiento superficial; la red de cunetas conduce el agua por "
        "gravedad hasta cuatro descargas (D1 a D4) que atraviesan el cerco." % mil(hv["A_total"], 0))
    # ---------------------------------------------------------------- 2
    D.h(1, "Características del área de estudio")
    D.h(2, "Clima")
    D.p("Según la memoria descriptiva de arquitectura del proyecto, el clima de Barranquita es tropical húmedo, con temperatura media anual de "
        "26 °C a 28 °C (máximas de 33 °C a 35 °C y mínimas de 21 °C a 23 °C), humedad relativa de 75 % a 90 % y precipitación anual de "
        "1,800 mm a 2,400 mm. La temporada de lluvias va de octubre a abril, con chubascos de corta duración y alto volumen; los meses "
        "más secos (julio y agosto) también registran lluvias.")
    D.h(2, "Topografía y niveles del proyecto")
    D.p("El terreno tiene un relieve leve a moderado, con desniveles de hasta 2 m. Dentro del cerco el proyecto nivela las plataformas: "
        "pisos y pasadizos a NPT +184.65, áreas verdes a +184.60 y patio de maniobra a +184.50. El borde de las cunetas queda al ras del "
        "piso (+184.65; +184.50 en el patio de maniobra), con junta asfáltica al mismo nivel. Fuera del cerco el terreno natural desciende "
        "hacia las quebradas del oeste y del norte y hacia el Jr. Alfonso Ugarte, lo que permite descargar por gravedad.")
    D.figura(fig("fig_superficies.png"), "Área de intervención, tipos de superficie y ejes de cuneta.", 15.5,
             "Planta del proyecto (arquitectura) y planteamiento de cunetas, lámina DC-01.")
    # ---------------------------------------------------------------- 3
    D.h(1, "Información pluviométrica")
    D.h(2, "Estación de referencia")
    e = H.ESTACION
    D.p("No se cuenta con registros de precipitación máxima en 24 horas en Barranquita. Se adopta la estación convencional CO “Tarapoto” "
        "del SENAMHI, con la misma serie empleada en los estudios hidrológicos de los proyectos de Morales (Hogar de Refugio Temporal, "
        "CUI 2675514, y CAR Mujeres, CUI 2717013), y se traslada a Barranquita por la relación de precipitaciones medias anuales (ítem 4).")
    D.tabla("Características de la estación de referencia", ["Característica", "Información"],
            [["Estación", e["nombre"]], ["Tipo", e["tipo"]], ["Entidad", e["entidad"]], ["Ubicación", "Distrito de Tarapoto, provincia y departamento de San Martín"],
             ["Latitud / Longitud", "%s / %s" % (e["latitud"], e["longitud"])], ["Altitud", "%d m s. n. m." % e["altitud"]],
             ["Variable", "Precipitación máxima en 24 horas (mm)"], ["Periodo", "%s (26 años)" % e["periodo"]]], [5, 10.5])
    filas = []
    for a, m in H.SERIE.items():
        filas.append([a] + [("S/D" if v is None else "%.1f" % v) for v in m] + ["%.1f" % max(v for v in m if v is not None)])
    D.tabla("Precipitación máxima en 24 horas, estación CO Tarapoto (mm)", ["Año", "E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D", "Máx."],
            filas, [1.2] + [1.0] * 12 + [1.3], tam=7, fuente="SENAMHI. S/D: sin dato. 2020: sin datos de abril a julio; 2024: enero a julio.")
    D.p("La serie de máximos anuales tiene 26 valores, de 43.6 mm (2002) a 152.5 mm (2020). Se conservan los años 2020 y 2024 con su "
        "máximo registrado, igual que en los estudios de Morales.")
    # ---------------------------------------------------------------- 4
    D.h(1, "Transposición de la información a Barranquita")
    D.p("Barranquita (184 m s. n. m.) se encuentra en la llanura del Caynarachi - Huallaga, con un régimen de lluvias mayor que el de Tarapoto "
        "(356 m s. n. m.): las estaciones del SENAMHI de la llanura registran de 2,333 a 2,444 mm al año, más del doble que Tarapoto. Para no "
        "subestimar las lluvias de diseño, la serie de Tarapoto se "
        "transpone con la relación de precipitaciones medias anuales (Manual de Hidrología, Hidráulica y Drenaje del MTC, transposición de "
        "información pluviométrica):")
    D.formula("P (Barranquita) = P (Tarapoto) × Pa (Barranquita) / Pa (Tarapoto)")
    D.p("La precipitación media anual de Barranquita se obtiene de las estaciones del SENAMHI de la zona, presentadas en el estudio "
        "hidrológico del expediente de agua potable, alcantarillado sanitario y unidades básicas de saneamiento del distrito de Barranquita "
        "(Municipalidad Distrital de Barranquita). Se adopta el promedio de las estaciones de llanura (Navarro, Pelejo y Shanusi, de 100 a "
        "160 m s. n. m.), de altitud y relieve similares a los del local (184 m s. n. m.). La estación Pongo de Caynarachi se excluye porque "
        "está al pie de los cerros, a la salida del pongo, y registra lluvias orográficas mayores que las de la llanura; San Antonio (430 m "
        "s. n. m.) pertenece a la provincia de San Martín, fuera de la llanura.")
    D.tabla("Precipitación total anual de las estaciones de la zona (promedio 2013-2017)", ["Estación SENAMHI", "Código", "Provincia / distrito", "Altitud (m s. n. m.)", "P anual (mm)", "Uso"],
            [[e[0], e[1], e[2], e[3], mil(e[4]), "Se usa" if e[5] else "No se usa"] for e in H.ESTACIONES_ZONA] +
            [["Promedio adoptado (Navarro, Pelejo y Shanusi)", "", "", "", mil(H.P_ANUAL_BARRANQUITA), ""]],
            [4, 1.6, 3.8, 2, 2, 2], tam=8, total=True,
            fuente="Estudio hidrológico, Cuadro N° 05, expediente de agua potable y alcantarillado sanitario del distrito de Barranquita (SENAMHI, 2013-2017).")
    D.tabla("Factor de transposición", ["Concepto", "Valor", "Fuente"],
            [["Precipitación media anual en Tarapoto (Pa)", "%s mm" % mil(H.P_ANUAL_TARAPOTO, 1), "SENAMHI"],
             ["Precipitación media anual en la llanura de Barranquita (Pa)", "%s mm" % mil(H.P_ANUAL_BARRANQUITA, 1),
              "Promedio de las estaciones de llanura Navarro, Pelejo y Shanusi (SENAMHI, 2013-2017)"],
             ["Factor de transposición", "%.4f" % HID["factor"], "Pa Barranquita / Pa Tarapoto"]], [6.5, 2.5, 6.5],
            fuente=H.FUENTE_ANUAL + ".")
    D.figura(fig("fig_serie.png"), "Precipitación máxima anual en 24 h: Tarapoto y serie transpuesta a Barranquita.", 15.5)
    # ---------------------------------------------------------------- 5
    D.h(1, "Análisis de frecuencias")
    D.h(2, "Parámetros estadísticos")
    D.tabla("Parámetros de la serie transpuesta", ["Parámetro", "Valor"],
            [["Número de datos (n)", A["n"]], ["Media (mm)", f2(A["media"])], ["Desviación estándar (mm)", f2(A["desv"])],
             ["Coeficiente de asimetría", "%.3f" % A["cs"]], ["Media de log P", "%.4f" % A["media_log"]], ["Desviación estándar de log P", "%.4f" % A["desv_log"]],
             ["Asimetría de log P", "%.4f" % A["cs_log"]]], [8, 4])
    D.h(2, "Distribuciones de probabilidad")
    D.p("Se ajustaron las distribuciones Normal, Log-Normal de dos parámetros, Log-Pearson tipo III (factor de frecuencia de Wilson-Hilferty) "
        "y Extrema tipo I o Gumbel, con las expresiones:")
    D.vinetas(["Normal: P = media + z · s", "Log-Normal: log P = media(log P) + z · s(log P)",
               "Log-Pearson III: log P = media(log P) + KT · s(log P); KT = (2/Cs) [ (1 + Cs·z/6 − Cs²/36)³ − 1 ]",
               "Gumbel: P = media + KT · s; KT = −(√6/π) [0.5772 + ln(ln(T/(T−1)))]"])
    filas = [[T] + [f2(A["tabla"][T][k]) for k in ("normal", "lognormal", "lp3", "gumbel")] for T in H.PERIODOS]
    D.tabla("Precipitación máxima en 24 h por periodo de retorno, serie transpuesta (mm)", ["T (años)", "Normal", "Log-Normal", "Log-Pearson III", "Gumbel"],
            filas, [2.5, 3, 3, 3, 3])
    D.h(2, "Prueba de bondad de ajuste")
    ks = A["ks"]
    D.p("Se aplicó la prueba de Kolmogorov-Smirnov con la posición de graficación de Weibull, m/(n+1). Para n = 26 y nivel de significación "
        "de 0.05, el estadístico crítico es %.2f. Todas las distribuciones se aceptan y la Log-Normal presenta el menor estadístico, por lo "
        "que se adopta para el diseño (mismo resultado que en los estudios de Morales)." % A["ks_critico"])
    D.tabla("Prueba de Kolmogorov-Smirnov", ["Distribución", "D máx.", "D crítico", "Resultado"],
            [[n, "%.4f" % ks[k], "%.2f" % A["ks_critico"], "Se acepta" + (" (adoptada)" if k == A["elegida"] else "")]
             for k, n in (("normal", "Normal"), ("lognormal", "Log-Normal"), ("lp3", "Log-Pearson III"), ("gumbel", "Gumbel"))], [4, 3, 3, 4])
    D.figura(fig("fig_frecuencias.png"), "Ajuste de distribuciones a la serie transpuesta.", 14.5)
    # ---------------------------------------------------------------- 6
    D.h(1, "Periodo de retorno y tiempo de concentración")
    D.p("Para las cunetas del local educativo se adopta un periodo de retorno de %d años, el mismo de los proyectos de Morales, superior "
        "al mínimo recomendado por la Norma OS.060 para el drenaje pluvial menor. El tiempo de concentración de cada cuneta se toma igual a "
        "la duración mínima de %d minutos, porque las áreas de aporte son pequeñas, con recorridos cortos sobre techos y pavimentos." % (H.T_DISENO, H.TC))
    # ---------------------------------------------------------------- 7
    D.h(1, "Lluvias de corta duración e intensidades")
    D.p("Las lluvias de corta duración se obtienen con la expresión de Dick y Peschke, recomendada por el Manual de Hidrología del MTC, y "
        "la intensidad como la lluvia dividida entre la duración:")
    D.formula("P(D) = P24 · (D / 1440)^0.25          I = P(D) · 60 / D")
    filas = []
    for Dm in (5, 10, 15, 20, 30, 60, 120, 240, 720, 1440):
        filas.append([Dm] + ["%.1f" % HID["idf"][T][Dm] for T in (2, 5, 10, 25, 50, 100)])
    D.tabla("Intensidades máximas (mm/h)", ["D (min)", "T = 2", "T = 5", "T = 10", "T = 25", "T = 50", "T = 100"], filas, [2] + [2.2] * 6)
    D.p("La regresión múltiple de las intensidades (duraciones de 5 a 60 minutos) da la ecuación de las curvas IDF:")
    D.formula("I = %.2f · T^%.4f / t^%.4f     (I en mm/h, T en años, t en minutos)" % (HID["K"], HID["m"], HID["n"]))
    D.figura(fig("fig_idf.png"), "Curvas intensidad - duración - frecuencia (Barranquita).", 14.5)
    D.tabla("Intensidad de diseño", ["Parámetro", "Valor"],
            [["P máx. 24 h, T = 25 años (Log-Normal)", "%.2f mm" % HID["P24"]], ["Lluvia en tc = 10 min (Dick y Peschke)", "%.2f mm" % HID["P_tc"]],
             ["Intensidad de diseño", "%.2f mm/h" % HID["I"]]], [9, 4])
    # ---------------------------------------------------------------- 8
    D.h(1, "Coeficientes de escorrentía y áreas de aporte")
    D.p("El área dentro del cerco se dividió en celdas de 1 m², clasificadas según el tipo de superficie de la planta del proyecto. Cada "
        "celda se asignó a la cuneta más cercana; en los techos a dos aguas, cada mitad descarga a la cuneta de su lado. Los coeficientes "
        "para T = 25 años son los mismos de los estudios de Morales.")
    sup = hv["superficies"]; tot = sum(v["A"] for v in sup.values())
    filas = [[H.NOM_SUP[k], mil(sup[k]["A"], 0), f2(sup[k]["C"]), "%.1f %%" % (100 * sup[k]["A"] / tot)] for k in ("techo", "pavimento", "verde")]
    filas.append(["Total / C ponderado", mil(tot, 0), "%.3f" % hv["C"], "100.0 %"])
    D.tabla("Superficies y coeficiente de escorrentía", ["Superficie", "Área (m²)", "C", "%"], filas, [8.5, 2.5, 2, 2], total=True)
    # ---------------------------------------------------------------- 9
    D.h(1, "Caudales de diseño")
    D.p("Los caudales se calculan con el método racional, válido para áreas pequeñas:")
    D.formula("Q = C · I · A / 3 600 000     (Q en m³/s; I en mm/h; A en m²)")
    D.p("El caudal de cada tramo considera el área acumulada aguas arriba, incluidas las cuencas de los ejes que le entregan. La tabla siguiente "
        "muestra el tramo más cargado de cada eje; el detalle de los 91 tramos está en la hoja CAUDALES de la memoria de cálculo (Excel).")
    filas = []
    for r in c["R"]["ramales"]:
        e = c["por_eje"][r["codigo"]]
        filas.append([r["codigo"], "S%d - %s" % (r["sistema"], DS.SISTEMAS[r["sistema"]][1]), mil(e["A"], 0), "%.3f" % e["C"], "%.1f" % e["Q"]])
    D.tabla("Caudal máximo por eje (tramo final)", ["Eje", "Sistema - descarga", "Área acum. (m²)", "C", "Q (l/s)"], filas, [2.3, 3.5, 3, 2, 2.5], tam=8)
    # ---------------------------------------------------------------- 10
    D.h(1, "Verificación hidráulica de las cunetas")
    D.p("La cuneta es un canal rectangular de concreto de 0.60 m de ancho total (muros de 0.10 m y 0.40 m libres), con profundidad variable "
        "desde 0.30 m al inicio de cada eje y cota de fondo con pendiente mínima de 0.5 %. Con el caudal de diseño se verifica:")
    D.vinetas(["Capacidad: tirante normal de Manning con n = 0.015 (concreto con rejilla) y borde libre mínimo de 0.05 m respecto de la altura "
               "libre (bajo la losa en los tramos tapados).",
               "Velocidad: con n = 0.013 (concreto liso), máximo 3.0 m/s para no erosionar el concreto (OS.060).",
               "Pendiente mínima de 0.5 % en todos los tramos, para la autolimpieza."])
    D.formula("Q = (1/n) · A · R^(2/3) · S^(1/2)     A = b · y     R = b·y / (b + 2y)")
    filas = []
    for r in c["R"]["ramales"]:
        e = c["por_eje"][r["codigo"]]
        filas.append([r["codigo"], "%.1f" % e["Q"], "%.2f" % e["S"], "%.3f" % e["y"], "%.2f" % e["h"], "%.3f" % e["bl"], "%.2f" % e["V"], "Cumple"])
    D.tabla("Verificación hidráulica por eje (tramo más cargado)", ["Eje", "Q (l/s)", "S (%)", "y (m)", "h libre (m)", "Borde libre mín. (m)", "V máx. (m/s)", "Estado"],
            filas, [2, 1.8, 1.5, 1.7, 1.8, 2.3, 2, 1.8], tam=8)
    D.p("Todos los tramos cumplen: el caudal máximo es %.1f l/s, el menor borde libre es %.3f m y la velocidad máxima es %.2f m/s. Por lo "
        "tanto, la sección de 0.60 m de ancho total con 0.40 m libres se mantiene en toda la red; solo varía la profundidad (0.30 m a %.2f m) "
        "para seguir la pendiente de la cota de fondo con el borde al ras del piso." % (c["Qmax"], c["BLmin"], c["Vmax"], c["hmax"]))
    D.tabla("Comprobaciones del diseño", ["N°", "Comprobación", "Estado"],
            [[x["n"], x["comprobacion"], x["estado"]] for x in c["V"]["comprobaciones"]], [1, 12, 2.5], tam=8)
    # ---------------------------------------------------------------- 11
    D.h(1, "Descargas")
    D.p("La red se divide en cuatro sistemas, cada uno con su descarga por gravedad a través de un pase en el cimiento del cerco perimétrico. "
        "Fuera del cerco no se construyen obras; el agua sigue por el terreno natural.")
    filas = []
    for k in sorted(c["dsc"]):
        d = c["dsc"][k]; s = next(v for v in c["sis"].values() if v["D"] == k)
        filas.append([k, "S - " + s["nom"].title(), "%.3f" % d["cf"], "%.2f" % d["terreno"], limpio(d["receptor"])])
    D.tabla("Descargas de la red de cunetas", ["Descarga", "Sistema", "Cota de fondo", "Terreno al pie", "Receptor"], filas, [1.8, 3.2, 2, 2, 7], tam=8)
    D.vinetas([("D1 y D3: ", "perfilado del terreno en los primeros 0.50 m fuera del cerco para que el agua salga libre."),
               ("D2: ", "fuera del cerco el terreno baja unos 3.2 m en talud; se recomienda proteger la entrega al pie del cerco contra la "
                        "erosión (emboquillado de piedra), coordinándolo con el propietario del terreno exterior."),
               ("D4: ", "perfilado de unos 0.10 m en los primeros 0.50 m fuera del cerco.")])
    # ---------------------------------------------------------------- 12
    D.h(1, "Conclusiones y recomendaciones")
    D.vinetas([
        "La precipitación máxima en 24 horas de diseño es %.2f mm (T = 25 años, distribución Log-Normal), obtenida de la serie de la estación "
        "CO Tarapoto transpuesta a Barranquita con un factor de %.3f." % (HID["P24"], HID["factor"]),
        "La intensidad de diseño para tc = 10 minutos es %.2f mm/h (Dick y Peschke)." % HID["I"],
        "El coeficiente de escorrentía ponderado dentro del cerco es %.2f, sobre un área de aporte de %s m²." % (hv["C"], mil(hv["A_total"], 0)),
        "Las cunetas de 0.60 m de ancho total (0.40 m libres) cumplen en todos los tramos con el caudal de diseño (máximo %.1f l/s), con borde "
        "libre mínimo de %.3f m y velocidad máxima de %.2f m/s." % (c["Qmax"], c["BLmin"], c["Vmax"]),
        "Las cuatro descargas funcionan por gravedad. Se recomienda proteger contra la erosión la salida D2 y perfilar el terreno al pie del cerco en D1, D3 y D4.",
        "Las canaletas y montantes de las coberturas deben entregar a las cunetas en los tramos con rejilla, y las rejillas deben limpiarse antes y durante la temporada de lluvias.",
        "Si el SENAMHI pone a disposición la serie de precipitación máxima en 24 horas de las estaciones Navarro, Pelejo o Shanusi, conviene contrastarla con la serie transpuesta."])
    D.h(1, "Anexos")
    D.vinetas(["Memoria de cálculo hidrológico e hidráulico (Excel): MEMORIA_CALCULO_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.xlsx.",
               "Planos de drenaje pluvial DC-01 a DC-19 (PLANTEAMIENTO_CUNETAS_IE0590_BARRANQUITA.dxf)."])
    D.figura(fig("fig_planta.png"), "Planta general de cunetas (lámina DC-01).", 15.5)


# ============================================================================== MEMORIA DESCRIPTIVA
def descriptiva(D, c):
    hv, q = c["hv"], c["q"]
    tot = lambda k: sum(x[k] for x in q)
    D.h(1, "Generalidades")
    D.h(2, "Nombre del proyecto")
    D.p("“Mejoramiento y ampliación del servicio de educación primaria en I.E. N° 0590 distrito de Barranquita de la provincia de Lamas del "
        "departamento de San Martín”, código de idea C.I. N° 468901.")
    D.h(2, "Entidad y modalidad")
    D.p("Gobierno Regional San Martín - Gerencia Territorial Bajo Mayo - Tarapoto (GRSM / GTBM-T). Modalidad de ejecución: administración directa.")
    D.h(2, "Antecedentes")
    D.p("Mediante Oficio N° 530-2026-GRSM/GRPyP se emitió opinión sobre la validación de la idea de proyecto con código N° 468901. "
        "Con Nota Informativa N° 112-2026-GRSM-GTBM-T/OPP se asignó el presupuesto y con Resolución Directoral N° 298-2026-GRSM/GTBM-T/DI "
        "se aprobó el desagregado de gastos para la elaboración del estudio de preinversión (ficha técnica estándar). La presente memoria "
        "corresponde a la especialidad de drenaje pluvial del local educativo.")
    D.h(2, "Objetivo")
    D.p("Captar y conducir por gravedad las aguas de lluvia de techos, veredas, patios y áreas libres del local educativo hasta el terreno "
        "natural exterior, evitando empozamientos, el ingreso de agua a los ambientes y el deterioro de pisos y estructuras.")
    D.h(1, "Ubicación y accesos")
    D.tabla("Ubicación", ["Descripción", "Dato"],
            [["Departamento / provincia / distrito", "San Martín / Lamas / Barranquita"], ["Predio", "Mz Z Lote 23, partida registral N° 11128704"],
             ["Área del terreno", "61,413.00 m² - perímetro 1,023.62 ml"], ["Área de intervención del drenaje", "%s m² (dentro del cerco perimétrico)" % mil(hv["A_total"], 0)],
             ["Colindancias", "Av. Vía de Evitamiento, Jr. Alfonso Ugarte C-3, Jr. Amazonas C-07 y C-08, propiedad de terceros"],
             ["Acceso", "Tarapoto - Pongo de Caynarachi - Barranquita: 95 km de carretera asfaltada, 2 h 25 min aprox."]],
            [5.5, 10], fuente="Memoria descriptiva de arquitectura del proyecto.")
    D.h(1, "Características del terreno y del clima")
    D.p("El terreno tiene relieve leve a moderado, con desniveles de hasta 2 m. El clima es tropical húmedo, con precipitación anual de 1,800 a "
        "2,400 mm y lluvias intensas de corta duración de octubre a abril. La arquitectura plantea techos a dos aguas con pendientes de 46 % a "
        "57 %, canaletas y montantes, y cunetas de concreto con rejilla metálica por los bordes de las veredas, patios y losa deportiva.")
    D.p("Niveles del proyecto: pisos y pasadizos NPT +184.65; áreas verdes +184.60; patio de maniobra +184.50. El borde de las cunetas va al ras "
        "del piso, con junta asfáltica al mismo nivel.")
    D.h(1, "Descripción del sistema de drenaje pluvial")
    D.h(2, "Criterios de diseño")
    D.vinetas([("Lluvia de diseño: ", "estación CO Tarapoto transpuesta a Barranquita (factor %.3f), T = 25 años, P24 = %.2f mm, I = %.2f mm/h "
                                     "con tc = 10 min (ver memoria hidrológica)." % (c["HID"]["factor"], c["HID"]["P24"], c["HID"]["I"])),
               ("Caudales: ", "método racional con coeficiente de escorrentía ponderado %.2f y factor de seguridad de 1.15." % hv["C"]),
               ("Sección de cuneta: ", "rectangular de concreto armado o simple, 0.60 m de ancho total (muros de 0.10 m y 0.40 m libres), losa de "
                                      "fondo de 0.10 m sobre solado de 4\"; profundidad variable de 0.30 m al inicio a %.2f m como máximo." % c["hmax"]),
               ("Pendiente: ", "cota de fondo con pendiente mínima de 0.5 %; el borde sigue el nivel del piso."),
               ("Acero: ", "solo donde la profundidad (de la rejilla al fondo) es 0.40 m o más y en los tramos tapados; con h < 0.40 m la cuneta es de concreto simple."),
               ("Quiebres: ", "a 45° en planta en cada cambio de dirección (chaflanes de 0.60 m), para evitar el resalto hidráulico; los ejes que llegan entran en diagonal."),
               ("Cubierta: ", "rejilla metálica móvil de platinas 1\" x 3/16\" con marco de ángulo 1\" x 1\" x 3/16\" en los tramos abiertos; losa tapa de 0.10 m en cruces de vereda, ingresos, patio y pase por el cerco."),
               ("Tapas de inspección: ", "0.60 x 0.60 m en los tramos tapados: al inicio y al final, en cada empalme y a 10 m como máximo."),
               ("Juntas: ", "de dilatación de 1\" con sellador asfáltico en toda la sección en U cada 3.00 m, y junta asfáltica entre la cuneta y el piso adyacente.")])
    D.h(2, "Red de cunetas")
    D.p("La red tiene %d ejes (EJE-01 a EJE-19) con %s m de cuneta, de los cuales %s m son tapados y %s m llevan rejilla. Todo el sistema queda "
        "dentro del cerco perimétrico y se organiza en cuatro sistemas, cada uno con su descarga:" % (len(c["R"]["ramales"]), mil(c["L"]), mil(c["Ltap"]), mil(c["L"] - c["Ltap"])))
    filas = [["Sistema %d - %s" % (k, s["nom"].title()), ", ".join(s["ejes"]), mil(s["L"]), s["D"]] for k, s in sorted(c["sis"].items())]
    D.tabla("Sistemas de drenaje", ["Sistema", "Ejes", "Longitud (m)", "Descarga"], filas, [4, 7.5, 2.2, 2], tam=8)
    filas = [[x["eje"], x["descripcion"], mil(x["L"]), mil(x["L_tapado"]), "%.2f" % x["h_prom"], "%.2f" % x["h_max"]] for x in q]
    filas.append(["TOTAL", "", mil(c["L"]), mil(c["Ltap"]), "", ""])
    D.tabla("Ejes de cuneta", ["Eje", "Ubicación", "L (m)", "Tapado (m)", "h prom. (m)", "h máx. (m)"], filas, [1.7, 7.6, 1.5, 1.6, 1.5, 1.5], tam=7.5, total=True)
    D.figura(fig("fig_planta.png"), "Planta general de cunetas (lámina DC-01).", 15.5)
    D.figura(fig("fig_secciones.png"), "Secciones típicas: cuneta con rejilla y tramo tapado (lámina DC-02).", 14)
    D.h(2, "Descargas")
    D.p("Las cuatro descargas cruzan el cerco con un pase en su cimiento, en tramo tapado, y entregan el agua al terreno natural exterior por "
        "gravedad. Fuera del cerco no hay obras; solo se perfila el terreno al pie del cerco.")
    filas = [[k, "%.3f" % c["dsc"][k]["cf"], limpio(c["dsc"][k]["receptor"])] for k in sorted(c["dsc"])]
    D.tabla("Descargas", ["Descarga", "Cota de fondo", "Receptor"], filas, [2, 2.5, 11], tam=8)
    D.figura(fig("fig_descarga_d1.png"), "Detalle de la descarga D1: planta, perfil longitudinal e isométrico (lámina DC-16).", 15.5)
    D.h(1, "Metas físicas")
    filas = [["Limpieza y trazo", "m²", mil(tot("limpieza"))], ["Excavación manual de zanjas", "m³", mil(tot("excavacion"))],
             ["Solado de concreto f'c = 100 kg/cm², e = 4\"", "m²", mil(tot("solado"))], ["Concreto f'c = 175 kg/cm² en cunetas", "m³", mil(tot("concreto"))],
             ["Encofrado y desencofrado", "m²", mil(tot("encofrado"))], ["Acero f'y = 4200 kg/cm²", "kg", mil(tot("acero"))],
             ["Rejilla metálica", "m", mil(tot("rejilla"))], ["Tapas de inspección 0.60 x 0.60 m", "und", "%d" % tot("tapas")],
             ["Junta de dilatación de 1\" con sellador asfáltico", "m", mil(tot("junta"))], ["Junta asfáltica entre cuneta y piso", "m", mil(tot("junta_piso"))]]
    D.tabla("Principales metas físicas (ver metrado)", ["Descripción", "Und.", "Cantidad"], filas, [10, 1.5, 3], fuente="METRADO_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.xlsx.")
    D.h(1, "Normas técnicas")
    D.vinetas(["Reglamento Nacional de Edificaciones: Norma Técnica CE.040 Drenaje Pluvial (R.M. N° 126-2021-VIVIENDA); Norma E.060 Concreto Armado; Norma IS.010 Instalaciones Sanitarias para Edificaciones.",
               "Manual de Hidrología, Hidráulica y Drenaje del Ministerio de Transportes y Comunicaciones.",
               "Norma Técnica “Criterios de diseño para locales educativos de primaria y secundaria”, R.V.M. N° 208-2019-MINEDU.",
               "Especificaciones Técnicas Generales para Construcción EG-2013 (MTC), sección 510 (juntas).",
               "Norma G.050 Seguridad durante la construcción."])
    D.h(1, "Relación de planos")
    D.tabla("Planos de drenaje pluvial", ["Lámina", "Contenido", "Escala"], [[a, b, e] for a, b, _, e in c["ind"]], [2, 11, 2.5], tam=8)


def generar(nombre, titulo, sub, fn, corto):
    c = contexto()
    D0 = Doc(corto); fn(D0, c)                         # primera pasada: titulos para el contenido
    D = Doc(corto); D.caratula(titulo, sub); D.contenido([t for t in D0.indice]); fn(D, c)
    D.guardar(os.path.join(ENT, nombre))


if __name__ == "__main__":
    FG.todas(H.resultados())
    generar("MEMORIA_HIDROLOGICA_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx", "ESTUDIO HIDROLÓGICO Y DE DRENAJE PLUVIAL", "Memoria hidrológica - red de cunetas", HD.memoria, "MEMORIA HIDROLÓGICA")
    generar("MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx", "MEMORIA DESCRIPTIVA", "Drenaje pluvial - red de cunetas", descriptiva, "MEMORIA DESCRIPTIVA")
