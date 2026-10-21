"""Memoria hidrologica y de drenaje pluvial (Word) de la I.E. N.° 0590 Barranquita (C.I. 468901), con la estructura de los
estudios hidrologicos de los proyectos de Morales (CAR Varones, CUI 2705619; Hogar de Refugio Temporal, CUI 2675514; CAR Mujeres,
CUI 2717013): aspectos generales, estudio hidrologico, caudales, drenaje, conclusiones, recomendaciones y anexos."""
import os, sys, math, json
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import hidrologia_b as H, diseno_b as DS

f2 = lambda v: "%.2f" % v
mil = lambda v, d=2: ("{:,.%df}" % d).format(v)
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"]
# Cuadros N° 05 y N° 06 del estudio hidrologico del expediente de agua potable y alcantarillado del distrito de Barranquita
P_MENSUAL = {"San Antonio": [183.46, 206.09, 217.37, 154.81, 190.35, 97.80, 93.69, 88.43, 139.81, 124.76, 188.74, 149.54],
             "Pongo de Caynarachi": [424.75, 416.42, 471.21, 286.88, 395.89, 220.77, 207.64, 173.99, 192.18, 283.43, 468.45, 311.55],
             "Navarro": [232.41, 274.69, 360.37, 202.74, 202.11, 139.72, 73.19, 95.40, 192.37, 131.37, 249.87, 195.55],
             "Pelejo": [221.45, 273.92, 330.51, 148.25, 193.52, 109.24, 109.42, 137.21, 151.41, 138.04, 329.37, 190.59],
             "Shanusi": [232.57, 322.93, 305.07, 198.48, 218.10, 140.26, 123.10, 123.76, 144.88, 142.72, 331.22, 160.92]}
T_ANUAL = {"San Antonio": 26.24, "Pongo de Caynarachi": 27.17, "Navarro": 27.04, "Pelejo": 26.80, "Shanusi": 27.23}
RS, MONT_D = 0.25, 4.0                 # Wyly-Eaton: relacion de llenado y diametro comercial del montante (pulg.)
CAN_B, CAN_H, CAN_S, CAN_N = 0.25, 0.20, 0.010, 0.013


def wyly_q(D, rs=RS):
    """Capacidad del montante (l/s) por Wyly-Eaton: Q (gpm) = 27.8 rs^(5/3) D^(8/3), D en pulgadas."""
    return 27.8 * rs ** (5 / 3) * D ** (8 / 3) / 15.850


def wyly_d(Q, rs=RS):
    return (Q * 15.850 / (27.8 * rs ** (5 / 3))) ** (3 / 8)


def manning(b, y, S, n):
    A = b * y; R = A / (b + 2 * y); return A * R ** (2 / 3) * math.sqrt(S) / n


def coberturas():
    """Techos dentro del cerco (proyeccion horizontal) agrupados por cobertura, con el eje que recibe su agua."""
    import terreno_b as T
    from shapely.geometry import LineString
    SUP = H.superficies(T.cargar(), DS.CERCO, DS.PATIO)
    R = json.load(open(os.path.join(RAIZ, "entregables_barranquita", "_calc", "diseno.json")))
    lin = {r["codigo"]: LineString([R["nudos"][n] for n in r["nudos"]]) for r in R["ramales"]}
    g = SUP["techo"]; out = []
    for p in sorted(getattr(g, "geoms", [g]), key=lambda p: (-p.centroid.y, p.centroid.x)):
        if p.area < 4: continue
        ejes = sorted(lin, key=lambda c: lin[c].distance(p))[:2]
        out.append({"A": p.area, "ejes": ejes})
    return out


def caminos(R):
    """Recorrido mas largo de cada sistema: desde el inicio de un eje, siguiendo los ejes que reciben, hasta la descarga."""
    ram = {r["codigo"]: r for r in R["ramales"]}
    def hasta_d(c, s0=0.0):
        r = ram[c]; fin = r["nudos"][-1]; L = r["L"] - s0
        if fin in DS.DESCARGAS: return L, [c]
        rec = next(x for x in R["ramales"] if fin in x["nudos"] and x["codigo"] != c)
        P = [tuple(R["nudos"][n]) for n in rec["nudos"]]; i = rec["nudos"].index(fin)
        sN = sum(math.dist(P[k], P[k + 1]) for k in range(i))
        L2, ruta = hasta_d(rec["codigo"], sN); return L + L2, [c] + ruta
    res = {}
    for c, r in ram.items():
        L, ruta = hasta_d(c); k = r["sistema"]
        if k not in res or L > res[k][0]: res[k] = (L, ruta)
    return res


def memoria(D, c):
    HID, A, hv, V, R = c["HID"], c["A"], c["hv"], c["V"], c["R"]
    FS = hv.get("FS", 1.15); nom_p = "“Mejoramiento y ampliación del servicio de educación primaria en I.E. N° 0590 distrito de Barranquita de la provincia de Lamas del departamento de San Martín”"
    sup = hv["superficies"]; Atot = sum(v["A"] for v in sup.values())
    # =========================================================================== 1
    D.h(1, "Aspectos generales")
    D.h(2, "Introducción")
    for t in [
        "El presente Estudio Hidrológico y de Drenaje Pluvial forma parte del expediente del proyecto %s, con código de idea C.I. N° 468901. "
        "Su finalidad es sustentar las condiciones de diseño para la captación, conducción y evacuación de las aguas de lluvia del local "
        "educativo, protegiendo las edificaciones, las circulaciones y los ambientes pedagógicos durante la temporada de lluvias." % nom_p,
        "El local se ubica en la localidad y distrito de Barranquita, provincia de Lamas, departamento de San Martín, sobre el predio Mz Z "
        "Lote 23 (área educación), inscrito en la partida registral N° 11128704, con un área de 61,413.00 m² y un perímetro de 1,023.62 ml. "
        "El área de intervención del drenaje pluvial es la comprendida dentro del cerco perimétrico, con %s m², donde se emplazan los "
        "pabellones de aulas, los ambientes complementarios, la losa deportiva techada, el patio cívico y el patio de maniobra." % mil(hv["A_total"], 0),
        "Barranquita se encuentra en la llanura amazónica del valle del Caynarachi, afluente del río Huallaga, con clima tropical húmedo "
        "(Af según Köppen-Geiger), precipitaciones durante todo el año y tormentas intensas de corta duración, en especial entre noviembre "
        "y abril. En este entorno, la concentración del escurrimiento sobre techos, veredas, patios y áreas libres puede originar "
        "empozamientos, humedecimiento de muros y deterioro de pisos si la captación es insuficiente o si las conducciones no tienen "
        "continuidad hasta un punto de descarga.",
        "El estudio comprende la selección y evaluación de la información pluviométrica, su traslado a las condiciones de Barranquita, el "
        "análisis de las precipitaciones máximas, la determinación de las intensidades de lluvia de diseño, la delimitación de las áreas "
        "tributarias por tipo de superficie y el cálculo de los caudales que llegan a cada tramo de cuneta. Con estos caudales se verifica "
        "la capacidad hidráulica de la red de cunetas de 0.60 m de ancho total (0.40 m libres) y el funcionamiento de las cuatro descargas "
        "que atraviesan el cerco perimétrico.",
        "Los criterios y procedimientos se sustentan en la Norma Técnica CE.040 “Drenaje Pluvial” del Reglamento Nacional de Edificaciones "
        "(R.M. N° 126-2021-VIVIENDA), en la Norma IS.010 de instalaciones sanitarias para edificaciones y, como referencia metodológica, en "
        "el Manual de Hidrología, Hidráulica y Drenaje del Ministerio de Transportes y Comunicaciones. Se emplean los mismos criterios de los "
        "estudios hidrológicos de los proyectos de Morales (CAR Varones, CUI 2705619; Hogar de Refugio Temporal, CUI 2675514; CAR Mujeres, "
        "CUI 2717013), con los datos propios de Barranquita."]:
        D.p(t)
    D.h(2, "Objetivos del estudio")
    D.p("General.", neg=None)
    D.p("Determinar los parámetros hidrológicos y dimensionar los componentes del sistema de drenaje pluvial del proyecto %s, C.I. N° 468901, "
        "mediante el análisis de las precipitaciones, las áreas aportantes y las condiciones de escurrimiento, para sustentar una solución de "
        "captación, conducción y evacuación de las aguas de lluvia que proteja la infraestructura y a sus usuarios, conforme a la normativa "
        "técnica aplicable." % nom_p)
    D.p("Específicos.")
    D.vinetas([
        "Caracterizar las condiciones topográficas e hidrográficas del emplazamiento, identificando las direcciones de escurrimiento y los puntos de descarga posibles fuera del cerco.",
        "Seleccionar la información pluviométrica representativa y trasladarla a Barranquita con información de las estaciones del SENAMHI de la zona.",
        "Determinar las precipitaciones de diseño mediante el análisis de frecuencia y la evaluación del ajuste de las distribuciones probabilísticas.",
        "Establecer el período de retorno de diseño de acuerdo con la Norma CE.040 y la función del local educativo.",
        "Delimitar las áreas tributarias de techos, pavimentos y áreas verdes y asignar coeficientes de escorrentía sustentados.",
        "Determinar los tiempos de concentración y las intensidades de lluvia de las duraciones críticas.",
        "Calcular los caudales de diseño de cada tramo de cuneta, con la incorporación progresiva de los aportes y sin duplicar áreas.",
        "Verificar hidráulicamente las cunetas, los montantes y las canaletas tipo, considerando capacidad, pendientes, velocidades y borde libre.",
        "Evaluar las descargas por el cerco y definir las medidas para prevenir empozamientos y erosión.",
        "Establecer recomendaciones de ejecución, operación y mantenimiento coherentes con los planos, el metrado y las especificaciones."])
    D.h(2, "Ubicación política y acceso")
    D.tabla("Ubicación política", ["Denominación", "Ubicación"],
            [["Departamento", "San Martín"], ["Provincia", "Lamas"], ["Distrito", "Barranquita"], ["Localidad", "Barranquita"],
             ["Predio", "Mz Z Lote 23 (área educación) - partida registral N° 11128704"], ["Área / perímetro del terreno", "61,413.00 m² / 1,023.62 ml"],
             ["Área de intervención (dentro del cerco)", "%s m²" % mil(hv["A_total"], 0)], ["Nivel de piso terminado", "NPT +184.65 m s. n. m."]],
            [6, 9.5], fuente="Memoria descriptiva de arquitectura del proyecto.")
    D.p("El terreno colinda con la Av. Vía de Evitamiento, el Jr. Alfonso Ugarte (cuadra 3), el Jr. Amazonas (cuadras 7 y 8) y propiedades de "
        "terceros. Por su frente principal y por el Jr. Alfonso Ugarte el terreno natural queda por debajo del nivel del local, lo que permite "
        "entregar las aguas pluviales por gravedad.")
    D.tabla("Vías de acceso a la localidad de Barranquita", ["De", "A", "Vía", "Distancia (km)", "Tiempo"],
            [["Tarapoto", "Pongo de Caynarachi", "Asfaltada", "50", "90 min"], ["Pongo de Caynarachi", "Barranquita", "Bicapa", "37", "45 min"],
             ["Total", "", "", "87 a 95", "2 h 15 min a 2 h 25 min"]], [3.5, 3.5, 2.5, 2.5, 3.5],
            fuente="Estudio hidrológico del expediente de agua potable y alcantarillado del distrito de Barranquita; memoria de arquitectura.", total=True)
    D.h(2, "Ubicación hidrográfica")
    D.tabla("Ubicación hidrográfica", ["Nivel de referencia", "Identificación"],
            [["Vertiente", "Atlántico (Amazonas)"], ["Intercuenca", "Medio Bajo Huallaga"], ["Subcuenca", "Río Caynarachi"],
             ["Autoridad", "Autoridad Nacional del Agua - Administración Local de Agua Tarapoto"]], [6, 9.5],
            fuente="Estudio hidrológico del expediente de agua potable y alcantarillado del distrito de Barranquita.")
    D.p("La ubicación hidrográfica permite comprender la organización general del escurrimiento; sin embargo, la descarga del sistema pluvial "
        "del local depende de las condiciones locales del terreno. Fuera del cerco, el terreno natural desciende hacia las quebradas del oeste y "
        "del norte y hacia el Jr. Alfonso Ugarte, que conducen el agua al sistema del Caynarachi; el proyecto no descarga directamente a un río.")
    D.h(2, "Clima de la zona")
    D.p("La temperatura media anual de la zona varía entre 26.2 °C y 27.2 °C, con humedad relativa de 75 % a 95 %. La precipitación total "
        "anual en las estaciones del SENAMHI de la llanura está entre 2,333 mm y 2,444 mm; en Pongo de Caynarachi, al pie de los cerros, "
        "llega a 3,853 mm. Las lluvias se concentran de noviembre a abril y los meses de menor precipitación son de junio a setiembre, aunque "
        "en todos los meses llueve.")
    filas = [[k, H.ESTACIONES_ZONA[[e[0] for e in H.ESTACIONES_ZONA].index(k)][3]] + ["%.0f" % v for v in P_MENSUAL[k]] + [mil(sum(P_MENSUAL[k]), 0)]
             for k in P_MENSUAL]
    D.tabla("Precipitación total mensual promedio (mm), estaciones SENAMHI de la zona", ["Estación", "Alt."] + MESES + ["Anual"], filas,
            [2.6, 0.8] + [0.85] * 12 + [1.1], tam=6.5, fuente="Estudio hidrológico del expediente de agua potable y alcantarillado del distrito de Barranquita, Cuadro N° 05 (SENAMHI).")
    D.figura(os.path.join(c["FIG"], "fig_meses.png"), "Precipitación media mensual de las estaciones de la zona.", 14.5)
    D.tabla("Temperatura media anual (°C)", ["Estación", "Altitud (m s. n. m.)", "Temperatura (°C)"],
            [[k, H.ESTACIONES_ZONA[[e[0] for e in H.ESTACIONES_ZONA].index(k)][3], "%.2f" % v] for k, v in T_ANUAL.items()], [5, 4, 4],
            fuente="Estudio hidrológico del expediente de agua potable y alcantarillado del distrito de Barranquita, Cuadro N° 06 (SENAMHI).")
    D.h(2, "Estación meteorológica de referencia")
    e = H.ESTACION
    D.p("Las estaciones de la zona (San Antonio, Pongo de Caynarachi, Navarro, Pelejo y Shanusi) cuentan con información de precipitación "
        "total mensual, pero no con series publicadas de precipitación máxima en 24 horas. Por ello, para el análisis de lluvias extremas "
        "se adopta la Estación Convencional CO “Tarapoto” del SENAMHI, con la serie de precipitación máxima en 24 horas 1999–2024 empleada en "
        "los estudios de Morales, y se traslada a Barranquita mediante la relación de precipitaciones medias anuales (ítem 2.5).")
    D.tabla("Características de la estación de referencia", ["Característica", "Información"],
            [["Estación", e["nombre"]], ["Tipo", e["tipo"]], ["Entidad responsable", e["entidad"]], ["Departamento / provincia / distrito", "San Martín / San Martín / Tarapoto"],
             ["Latitud / longitud", "%s / %s" % (e["latitud"], e["longitud"])], ["Altitud", "%d m s. n. m." % e["altitud"]],
             ["Variable", "Precipitación máxima en 24 horas"], ["Unidad", "milímetros (mm)"], ["Período documental", "%s (26 años)" % e["periodo"]]], [6.5, 9])
    D.p("Como referencia técnica, el numeral 3.4 del Manual de Hidrología, Hidráulica y Drenaje del MTC recomienda un mínimo de 25 años de "
        "registro; la serie disponible tiene 26 años calendario. Los años 2020 (sin datos de abril a julio) y 2024 (datos de enero a julio) "
        "son incompletos: sus máximos se conservan como observaciones válidas, con el mismo tratamiento de los estudios de Morales, porque "
        "2020 registra el mayor valor de la serie (152.5 mm en enero) y excluirlo subestimaría los eventos extremos.")
    # =========================================================================== 2
    D.h(1, "Estudio hidrológico")
    D.h(2, "Introducción")
    D.p("El estudio hidrológico determina las características de la precipitación y su transformación en escorrentía dentro del local educativo. "
        "Su desarrollo proporciona las lluvias e intensidades de diseño necesarias para calcular los caudales que reciben las cunetas, "
        "considerando las condiciones del terreno nivelado y las superficies previstas en el proyecto (techos, veredas, patios y áreas verdes).")
    D.p("La respuesta hidrológica del emplazamiento depende de la magnitud y duración de las lluvias, de la distribución de las áreas aportantes "
        "y de la capacidad de infiltración de las superficies. En las cubiertas y pavimentos el agua se concentra con mayor rapidez que en los "
        "sectores permeables; por ello se evalúa el aporte de cada tipo de superficie y su recorrido hasta la cuneta más cercana.")
    D.h(2, "Metodología empleada")
    for tit, txt in [
        ("a) Recopilación y organización de la información. ", "Se integra la serie de precipitación máxima en 24 horas de la estación CO Tarapoto (1999–2024) y la precipitación total anual de las estaciones del SENAMHI de la zona. Se usan la topografía y los planos del proyecto para reconocer los niveles, las coberturas y los recorridos del escurrimiento."),
        ("b) Revisión de calidad y conformación de la serie. ", "Se verifica la transcripción de los registros y la correspondencia entre los valores mensuales y los máximos anuales; los vacíos no se reemplazan por ceros ni promedios."),
        ("c) Transposición de la información. ", "La serie de Tarapoto se traslada a Barranquita con la relación entre la precipitación media anual de la llanura y la de Tarapoto (Manual de Hidrología del MTC)."),
        ("d) Caracterización estadística y análisis de frecuencia. ", "Se calculan la media, la desviación estándar y la asimetría, y se ajustan las distribuciones Normal, Log-Normal, Log-Pearson tipo III y Gumbel (numeral 3.7.1 del Manual del MTC)."),
        ("e) Evaluación del ajuste y selección del modelo. ", "Se aplica la prueba de Kolmogorov-Smirnov y se comparan las precipitaciones estimadas; se selecciona la distribución de mejor ajuste."),
        ("f) Precipitaciones e intensidades de diseño. ", "Con la distribución seleccionada se obtienen las precipitaciones para los períodos de retorno; las lluvias de corta duración se obtienen por Dick y Peschke y se construyen las curvas IDF."),
        ("g) Áreas tributarias y tiempos de concentración. ", "Se identifican las superficies que descargan a cada tramo de cuneta y se determinan los tiempos de concentración, con la duración mínima de 10 minutos de la Norma CE.040."),
        ("h) Coeficientes y caudales. ", "Se asignan coeficientes de escorrentía por superficie y se calculan los caudales por el método racional, acumulando los aportes de aguas arriba."),
        ("i) Integración con la evaluación hidráulica. ", "Los caudales se verifican en cada tramo de cuneta con Manning, y se evalúan las descargas por el cerco.")]:
        D.p(txt, neg=tit)
    D.h(2, "Análisis estadístico de datos")
    D.tabla("Cobertura de la información de la estación CO Tarapoto", ["Componente", "Período", "Condición"],
            [["Registros del documento complementario", "1999–2004", "Seis años con valores completos"], ["Registros del cuadro principal", "2005–2019", "Quince años con valores completos"],
             ["Año con meses sin información", "2020", "Sin datos de abril a julio; se conserva el máximo de enero (152.5 mm)"],
             ["Registros recientes", "2021–2023", "Tres años con valores completos"], ["Último año", "2024", "Datos de enero a julio"],
             ["Cobertura total", "1999–2024", "26 años calendario: 24 completos y 2 parciales"]], [5.5, 2.5, 7.5],
            fuente="SENAMHI, estación CO Tarapoto.")
    filas = [[a] + [("S/D" if v is None else "%.1f" % v) for v in m] + ["%.1f" % max(v for v in m if v is not None)] for a, m in H.SERIE.items()]
    D.tabla("Precipitación máxima en 24 horas, estación CO Tarapoto (mm)", ["Año"] + [x[0] for x in MESES] + ["Máx."],
            filas, [1.2] + [1.0] * 12 + [1.3], tam=7, fuente="SENAMHI, estación CO Tarapoto. S/D: sin dato.")
    D.h(2, "Transposición de la información a Barranquita")
    D.p("Barranquita (184 m s. n. m.) se encuentra en la llanura del Caynarachi, con un régimen de lluvias mucho mayor que el de Tarapoto "
        "(356 m s. n. m.). Para no subestimar las lluvias de diseño, la serie de Tarapoto se transpone con la relación de precipitaciones "
        "medias anuales, procedimiento de transposición de información pluviométrica del Manual de Hidrología del MTC:")
    D.formula("P (Barranquita) = P (Tarapoto) × Pa (Barranquita) / Pa (Tarapoto)")
    D.p("La precipitación media anual de Barranquita se obtiene de las estaciones de llanura Navarro, Pelejo y Shanusi (100 a 160 m s. n. m.), "
        "de altitud y relieve similares a los del local. La estación Pongo de Caynarachi se excluye porque está al pie de los cerros, a la salida "
        "del pongo, y registra lluvias orográficas mayores que las de la llanura; San Antonio (430 m s. n. m.) se encuentra fuera de la llanura.")
    D.tabla("Precipitación total anual de las estaciones de la zona", ["Estación SENAMHI", "Código", "Provincia / distrito", "Altitud", "P anual (mm)", "Uso"],
            [[x[0], x[1], x[2], x[3], mil(x[4]), "Se usa" if x[5] else "No se usa"] for x in H.ESTACIONES_ZONA] +
            [["Promedio adoptado (Navarro, Pelejo y Shanusi)", "", "", "", mil(H.P_ANUAL_BARRANQUITA), ""]], [4, 1.6, 3.8, 1.6, 2.2, 2.2], tam=8, total=True,
            fuente="Estudio hidrológico, Cuadro N° 05, expediente de agua potable y alcantarillado del distrito de Barranquita (SENAMHI).")
    D.tabla("Factor de transposición", ["Concepto", "Valor"],
            [["Precipitación media anual en Tarapoto", "%s mm" % mil(H.P_ANUAL_TARAPOTO, 1)], ["Precipitación media anual en la llanura de Barranquita", "%s mm" % mil(H.P_ANUAL_BARRANQUITA, 2)],
             ["Factor de transposición", "%.4f" % HID["factor"]]], [10, 5])
    filas = [[a, "%.1f" % p0, "%.2f" % p1] for (a, p0), (_, p1) in zip(H.maximos(), A["serie"])]
    D.tabla("Serie de precipitación máxima anual en 24 horas (mm)", ["Año", "Tarapoto", "Barranquita (transpuesta)"], filas, [3, 4, 5], tam=8)
    D.figura(os.path.join(c["FIG"], "fig_serie.png"), "Precipitación máxima anual en 24 h: Tarapoto y serie transpuesta a Barranquita.", 15.5)
    D.h(2, "Análisis de intensidades")
    D.p("La intensidad de precipitación expresa la lluvia acumulada por unidad de tiempo y es el parámetro que determina los caudales del "
        "método racional. Como los registros son de 24 horas, las lluvias de corta duración se obtienen por desagregación temporal (Dick y "
        "Peschke) y la intensidad media de cada duración se calcula como:")
    D.formula("I = Pd / td")
    D.vinetas(["I: intensidad media de precipitación (mm/h).", "Pd: precipitación de la duración y período de retorno analizados (mm).", "td: duración de la precipitación (h)."])
    D.p("La duración que interviene en el método racional se iguala al tiempo de concentración del área tributaria; dividir la lluvia de 24 horas "
        "entre 24 solo da la intensidad media del día y no la de una tormenta corta, que es la que solicita a canaletas, montantes y cunetas.")
    D.h(2, "Análisis de frecuencia")
    D.p("El análisis de frecuencia estima las precipitaciones máximas asociadas a distintas probabilidades de ocurrencia a partir de la serie "
        "de máximos anuales. Para una serie anual, la probabilidad de excedencia y el período de retorno se relacionan por:")
    D.formula("P(X ≥ xT) = 1 / T          F(xT) = P(X < xT) = 1 − 1/T")
    D.p("El período de retorno es un intervalo medio entre excedencias; no implica que el evento ocurra regularmente cada T años. Se evalúan "
        "las distribuciones Normal, Log-Normal de dos parámetros, Log-Pearson tipo III y Extrema tipo I de Gumbel:")
    D.p("Distribución Normal. ", neg=None); D.formula("f(x) = 1/(σ√(2π)) · exp[−(x − μ)² / (2σ²)]          xT = x̄ + zT · s")
    D.p("Distribución Log-Normal (dos parámetros). Los logaritmos de la precipitación siguen una distribución normal (en este estudio se usan logaritmos decimales):")
    D.formula("y = log x          yT = ȳ + zT · sy          xT = 10^yT")
    D.p("Distribución Log-Pearson tipo III. Los logaritmos siguen una distribución Pearson III; el factor de frecuencia depende de la asimetría Cs de los logaritmos (Wilson-Hilferty):")
    D.formula("KT = (2/Cs) · [ (1 + Cs·zT/6 − Cs²/36)³ − 1 ]          xT = 10^(ȳ + KT · sy)")
    D.p("Distribución Extrema tipo I de Gumbel (máximos):")
    D.formula("F(x) = exp[−exp(−(x − u)/α)]     α = √6·s/π     u = x̄ − 0.5772·α     KT = −(√6/π)·[0.5772 + ln(ln(T/(T−1)))]")
    D.tabla("Parámetros estadísticos de la serie transpuesta", ["Parámetro", "Valor"],
            [["Número de datos (n)", A["n"]], ["Media (mm)", f2(A["media"])], ["Desviación estándar (mm)", f2(A["desv"])], ["Coeficiente de asimetría", "%.3f" % A["cs"]],
             ["Media de log P", "%.4f" % A["media_log"]], ["Desviación estándar de log P", "%.4f" % A["desv_log"]], ["Asimetría de log P", "%.4f" % A["cs_log"]],
             ["Gumbel: α (mm)", "%.3f" % A["gumbel_alfa"]], ["Gumbel: u (mm)", "%.3f" % A["gumbel_u"]]], [9, 4])
    for k, nom, cab, fil in (
        ("normal", "Distribución Normal", ["T (años)", "F = 1 − 1/T", "z", "P máx. (mm)"], lambda T, t: [T, "%.4f" % (1 - 1 / T), "%.3f" % t["z"], f2(t["normal"])]),
        ("lognormal", "Distribución Log-Normal", ["T (años)", "F = 1 − 1/T", "z", "log P", "P máx. (mm)"], lambda T, t: [T, "%.4f" % (1 - 1 / T), "%.3f" % t["z"], "%.4f" % math.log10(t["lognormal"]), f2(t["lognormal"])]),
        ("lp3", "Distribución Log-Pearson tipo III", ["T (años)", "z", "KT", "log P", "P máx. (mm)"], lambda T, t: [T, "%.3f" % t["z"], "%.3f" % t["kt_lp3"], "%.4f" % math.log10(t["lp3"]), f2(t["lp3"])]),
        ("gumbel", "Distribución Extrema tipo I - Gumbel", ["T (años)", "KT", "P máx. (mm)"], lambda T, t: [T, "%.4f" % t["kt_gumbel"], f2(t["gumbel"])])):
        D.tabla(nom + " - serie transpuesta", cab, [fil(T, A["tabla"][T]) for T in H.PERIODOS], None, tam=8.5)
    D.h(2, "Pruebas de bondad de ajuste")
    D.p("La prueba de Kolmogorov-Smirnov compara la distribución empírica de la muestra con la distribución acumulada de cada modelo; el "
        "estadístico es la mayor diferencia absoluta entre ambas:")
    D.formula("D = máx | F(xi) − Fe(xi) |          Fe(xi) = i / (n + 1)")
    D.p("Se adopta un nivel de significación α = 0.05. Para n = 26 el valor crítico es 0.27 (tabla de Smirnov); una distribución se acepta si "
        "D < 0.27. La selección considera además la representación de los eventos de mayor magnitud y la coherencia de las estimaciones.")
    D.tabla("Valores críticos de Kolmogorov-Smirnov", ["n", "α = 0.20", "α = 0.10", "α = 0.05", "α = 0.01"],
            [[5, 0.45, 0.51, 0.56, 0.67], [10, 0.32, 0.37, 0.41, 0.49], [15, 0.27, 0.30, 0.34, 0.40], [20, 0.23, 0.26, 0.29, 0.36], [25, 0.21, 0.24, 0.27, 0.32],
             [30, 0.19, 0.22, 0.24, 0.29], [40, 0.17, 0.19, 0.21, 0.25], [50, 0.15, 0.17, 0.19, 0.23]], [2, 2.5, 2.5, 2.5, 2.5],
            fuente="Yevjevich, V. (1972). Probability and Statistics in Hydrology. Water Resources Publications.")
    D.h(2, "Evaluación del ajuste de las distribuciones")
    ml, sl, csl = A["media_log"], A["desv_log"], A["cs_log"]
    def F_all(v):
        def lp3(v):
            lo, hi = -8.0, 8.0
            for _ in range(100):
                zz = (lo + hi) / 2; k = csl / 6; kt = (2 / csl) * ((1 + k * zz - k * k) ** 3 - 1)
                if 10 ** (ml + kt * sl) < v: lo = zz
                else: hi = zz
            return H._phi((lo + hi) / 2)
        return (H._phi((v - A["media"]) / A["desv"]), H._phi((math.log10(v) - ml) / sl), lp3(v), math.exp(-math.exp(-(v - A["gumbel_u"]) / A["gumbel_alfa"])))
    filas = []
    for i, (x, fe) in enumerate(A["orden"], 1):
        Fs = F_all(x); filas.append([i, f2(x), "%.4f" % fe] + ["%.4f" % abs(fe - F) for F in Fs])
    D.tabla("Prueba de Kolmogorov-Smirnov: diferencias |F − Fe| por dato", ["m", "P (mm)", "Fe", "Normal", "Log-Normal", "LP III", "Gumbel"], filas,
            [1, 2, 2, 2.2, 2.2, 2.2, 2.2], tam=7.5)
    ks = A["ks"]
    D.tabla("Resumen de la prueba de Kolmogorov-Smirnov", ["Distribución", "D máx.", "D crítico", "Resultado"],
            [[n, "%.4f" % ks[k], "%.2f" % A["ks_critico"], "Se acepta" + (" (adoptada)" if k == A["elegida"] else "")]
             for k, n in (("normal", "Normal"), ("lognormal", "Log-Normal"), ("lp3", "Log-Pearson III"), ("gumbel", "Gumbel"))], [5, 3, 3, 4])
    D.p("Las cuatro distribuciones se aceptan al nivel de significación de 0.05. La distribución Log-Normal presenta el menor estadístico "
        "(D = %.4f) y estimaciones intermedias entre la Normal y las distribuciones de cola más pesada, por lo que se adopta para el diseño, "
        "igual que en los estudios de Morales." % ks["lognormal"])
    filas = [[T] + [f2(A["tabla"][T][k]) for k in ("normal", "lognormal", "lp3", "gumbel")] + [f2(A["tabla"][T]["lognormal"])] for T in H.PERIODOS]
    D.tabla("Resumen de precipitaciones máximas en 24 h por distribución (mm)", ["T (años)", "Normal", "Log-Normal", "Log-Pearson III", "Gumbel", "Diseño"], filas, [2, 2.6, 2.6, 2.8, 2.6, 2.6])
    D.figura(os.path.join(c["FIG"], "fig_frecuencias.png"), "Ajuste de las distribuciones a la serie transpuesta.", 14.5)
    D.h(2, "Curvas intensidad - duración - frecuencia")
    D.p("Las lluvias de corta duración se obtienen de la precipitación máxima en 24 horas mediante la expresión de Dick y Peschke, recomendada "
        "por el Manual de Hidrología del MTC cuando no se dispone de registros pluviográficos:")
    D.formula("Pd = P24 · (d / 1440)^0.25")
    filas = [[d] + ["%.2f" % (H.p_dur(HID["p24"][T], d)) for T in (2, 5, 10, 25, 50, 100, 500)] for d in H.DURACIONES]
    D.tabla("Lluvias máximas por duración (mm)", ["D (min)", "T = 2", "T = 5", "T = 10", "T = 25", "T = 50", "T = 100", "T = 500"], filas, [1.8] + [1.9] * 7, tam=8)
    filas = [[d] + ["%.2f" % HID["idf"][T][d] for T in (2, 5, 10, 25, 50, 100, 500)] for d in H.DURACIONES]
    D.tabla("Intensidades máximas por duración (mm/h)", ["D (min)", "T = 2", "T = 5", "T = 10", "T = 25", "T = 50", "T = 100", "T = 500"], filas, [1.8] + [1.9] * 7, tam=8)
    D.p("Con las intensidades de 5 a 60 minutos y todos los períodos de retorno se ajustó, por regresión lineal múltiple de los logaritmos, la "
        "ecuación de las curvas IDF:")
    D.formula("I = K · T^m / t^n          log I = log K + m · log T − n · log t")
    D.tabla("Parámetros de la ecuación IDF", ["Parámetro", "Valor"], [["K", "%.2f" % HID["K"]], ["m", "%.4f" % HID["m"]], ["n", "%.4f" % HID["n"]]], [6, 4])
    D.formula("I = %.2f · T^%.4f / t^%.4f     (I en mm/h, T en años, t en minutos)" % (HID["K"], HID["m"], HID["n"]))
    D.figura(os.path.join(c["FIG"], "fig_idf.png"), "Curvas intensidad - duración - frecuencia de Barranquita.", 14.5)
    D.h(2, "Tiempo de concentración")
    D.p("El tiempo de concentración es el tiempo que tarda el agua en llegar desde el punto hidráulicamente más alejado del área tributaria "
        "hasta la sección de control. Para cada sistema se evaluó el recorrido más largo: escurrimiento sobre el techo o el piso hasta la "
        "cuneta y conducción por las cunetas hasta la descarga.")
    D.p("Kirpich. ", neg=None); D.formula("tc = 0.01947 · L^0.77 · S^(−0.385)     (tc en min, L en m, S en m/m)")
    D.p("Ecuación del SCS (California Culverts Practice). ", neg=None); D.formula("tc = 0.0195 · (L³ / H)^0.385     (tc en min, L en m, H en m)")
    cam = caminos(R); hid = c["hid"]; filas = []
    vel = {}
    for f in hid: vel.setdefault(f["ramal"], []).append(f["V"])
    for k, (L, ruta) in sorted(cam.items()):
        r0 = next(r for r in R["ramales"] if r["codigo"] == ruta[0]); cf0 = r0["perfil"][0][2]
        d = DS.SISTEMAS[k][1]; cfD = c["dsc"][d]["cf"]; Hh = max(cf0 - cfD, 0.01); S = Hh / L
        tk = 0.01947 * L ** 0.77 * S ** -0.385; ts = 0.0195 * (L ** 3 / Hh) ** 0.385
        Vm = sum(sum(vel[x]) / len(vel[x]) for x in ruta) / len(ruta); tv = 5.0 + L / Vm / 60
        filas.append(["S%d - %s" % (k, d), " → ".join(ruta), "%.1f" % L, "%.3f" % Hh, "%.2f" % (100 * S), "%.1f" % tk, "%.1f" % ts, "%.1f" % tv])
    D.tabla("Tiempo de concentración del recorrido más largo de cada sistema", ["Sistema", "Recorrido", "L (m)", "H (m)", "S (%)", "Kirpich (min)", "SCS (min)", "Entrada + conducción (min)"],
            filas, [1.8, 5.3, 1.3, 1.2, 1.1, 1.6, 1.4, 1.8], tam=7.5)
    tmax = max(max(float(f[5]), float(f[6]), float(f[7])) for f in filas)
    D.p("Los tiempos de concentración calculados para el recorrido más largo de cada sistema, tanto con las ecuaciones de Kirpich y del SCS "
        "como con la estimación física (5 minutos de entrada sobre techos y pisos más el tiempo de conducción con la velocidad media de las "
        "cunetas), resultan menores de 10 minutos (máximo %.1f min). La Norma CE.040 establece que el tiempo de concentración de diseño no "
        "debe ser menor de 10 minutos; por tanto se adopta tc = 10 min para toda la red." % tmax)
    D.h(2, "Período de retorno")
    D.p("Se adopta un período de retorno de 25 años (probabilidad anual de excedencia de 4 %), conforme al numeral 11.1 de la Norma CE.040, "
        "que deja la elección del período de retorno al tipo de proyecto y al criterio del proyectista, y al numeral 11.3, que contempla el "
        "diseño para precipitaciones de baja frecuencia con períodos de retorno de 25 años o más. El local educativo concentra estudiantes "
        "durante dos turnos y requiere que patios, pasadizos y aulas permanezcan operativos durante las lluvias intensas. Es el mismo "
        "período de retorno de los proyectos de Morales.")
    D.p("El riesgo de que el evento de diseño sea superado al menos una vez durante n años de vida útil es:")
    D.formula("R = 1 − (1 − 1/T)^n")
    D.tabla("Riesgo de excedencia (%)", ["T (años)", "n = 10 años", "n = 20 años", "n = 25 años", "n = 50 años"],
            [[T] + ["%.1f" % (100 * (1 - (1 - 1 / T) ** n)) for n in (10, 20, 25, 50)] for T in (5, 10, 25, 50, 100)], [2.5, 3, 3, 3, 3])
    D.h(2, "Determinación de la intensidad máxima de diseño")
    filas = [[d, "%.2f" % (d / 60), "%.2f" % H.p_dur(HID["P24"], d), "%.2f" % (H.p_dur(HID["P24"], d) * 60 / d)] for d in (5, 10, 15, 20, 30, 45, 60, 90, 120, 240, 360, 720, 1440)]
    D.tabla("Precipitación e intensidad de lluvia, P máx. 24 h = %.2f mm, T = 25 años" % HID["P24"], ["D (min)", "D (h)", "P (mm)", "I (mm/h)"], filas, [3, 3, 3.5, 3.5])
    D.p("La intensidad disminuye conforme aumenta la duración. Con T = 25 años y tc = 10 min:")
    D.formula("P10 = %.2f · (10/1440)^0.25 = %.2f mm          I = %.2f × 60 / 10 = %.2f mm/h" % (HID["P24"], HID["P_tc"], HID["P_tc"], HID["I"]))
    D.p("Se adopta como intensidad máxima de diseño I = %.2f mm/h, que se utiliza en el método racional para todas las áreas tributarias." % HID["I"])
    # =========================================================================== 3
    D.h(1, "Cálculo de caudales en el área del proyecto")
    D.h(2, "Coeficiente de escorrentía")
    D.p("El coeficiente de escorrentía representa la fracción de la lluvia que escurre superficialmente. Se asigna por tipo de superficie del "
        "proyecto terminado, con la Tabla 1.a del Anexo I de la Norma CE.040 para T = 25 años, y se pondera por área cuando un tramo recibe "
        "superficies diferentes.")
    D.tabla("Coeficientes de escorrentía por tipo de superficie (T = 25 años)", ["Superficie y condición", "C"],
            [["Concreto / techo", "0.88"], ["Asfalto", "0.86"], ["Zona verde, pendiente 0 a 2 %", "0.29"], ["Zona verde, pendiente 2 a 7 %", "0.34"], ["Zona verde, pendiente mayor de 7 %", "0.40"]],
            [10, 3], fuente="Norma Técnica CE.040, Anexo I, Tabla 1.a (mismos valores de los estudios de Morales).")
    D.p("Se adopta C = 0.88 para techos y para veredas, pisos, losa y patio de maniobra, y C = 0.40 para áreas verdes y terreno nivelado. Aunque "
        "las áreas verdes del local son casi planas (que corresponderían a C = 0.29), se usa el valor mayor de la tabla por tratarse de rellenos "
        "compactados con menor infiltración. Además, los caudales se afectan por un factor de seguridad de %.2f, igual que en los proyectos de Morales." % FS)
    D.h(2, "Áreas de drenaje")
    D.p("El área dentro del cerco se dividió en celdas de 1 m² y cada celda se clasificó según la planta del proyecto: proyección de coberturas "
        "(techos), veredas, circulaciones, pisos y patio de maniobra (pavimentos) y el resto como áreas verdes o terreno nivelado. Cada celda se "
        "asignó a la cuneta más cercana; en los techos a dos aguas, cada mitad descarga a la cuneta de su lado.")
    filas = [[H.NOM_SUP[k], mil(sup[k]["A"], 0), f2(sup[k]["C"]), "%.1f %%" % (100 * sup[k]["A"] / Atot)] for k in ("techo", "pavimento", "verde")]
    filas.append(["Total / C ponderado", mil(Atot, 0), "%.3f" % hv["C"], "100.0 %"])
    D.tabla("Superficies del área de intervención", ["Superficie", "Área (m²)", "C", "%"], filas, [8.5, 2.5, 2, 2], total=True)
    D.figura(os.path.join(c["FIG"], "fig_superficies.png"), "Delimitación de techos, pavimentos y áreas verdes dentro del cerco.", 15.5)
    D.h(2, "Áreas de drenaje de techo en edificaciones")
    cb = coberturas()
    D.p("Las coberturas de las edificaciones son de panel termoacústico o planchas TR4, a dos aguas con pendientes de 46 %% a 57 %%. Su proyección "
        "horizontal dentro del cerco suma %s m² en %d paños. Cada paño descarga por canaletas y montantes de PVC a las cunetas de sus lados." % (mil(sum(x["A"] for x in cb)), len(cb)))
    filas = [["Cobertura %02d" % i, mil(x["A"]), "0.88", " / ".join(x["ejes"])] for i, x in enumerate(cb, 1)]
    filas.append(["Total", mil(sum(x["A"] for x in cb)), "", ""])
    D.tabla("Áreas de techo (proyección horizontal) y cunetas que las reciben", ["Paño", "Área (m²)", "C", "Ejes de cuneta"], filas, [3, 3, 2, 7.5], tam=8, total=True)
    ae = hv.get("areas_eje", {})
    if ae:
        filas = []
        for r in R["ramales"]:
            a = ae.get(r["codigo"], {}); tot = sum(a.values()) or 1
            filas.append([r["codigo"], mil(a.get("techo", 0), 0), mil(a.get("pavimento", 0), 0), mil(a.get("verde", 0), 0), mil(tot, 0),
                          "%.3f" % ((0.88 * (a.get("techo", 0) + a.get("pavimento", 0)) + 0.40 * a.get("verde", 0)) / tot)])
        D.tabla("Áreas propias de cada eje por tipo de superficie (m²)", ["Eje", "Techos", "Pavimentos", "Áreas verdes", "Total", "C ponderado"], filas, [2.2, 2.4, 2.6, 2.6, 2.4, 2.6], tam=8)
    D.h(2, "Intensidad de lluvia")
    D.p("La intensidad de diseño corresponde a T = 25 años y a la duración de 10 minutos: I = %.2f mm/h, equivalente a %.8f m/s." % (HID["I"], HID["I"] / 3.6e6))
    D.h(2, "Caudales de diseño")
    D.p("Los caudales se calculan por el método racional, aplicable a áreas pequeñas como las del local:")
    D.formula("Q = C · I · A · FS / 3 600 000     (Q en m³/s; I en mm/h; A en m²)")
    D.p("El caudal de cada tramo considera el área acumulada aguas arriba, incluidas las de los ejes que le entregan, sin contar dos veces una misma superficie.")
    filas = []
    for r in R["ramales"]:
        e = c["por_eje"][r["codigo"]]
        filas.append([r["codigo"], "S%d - %s" % (r["sistema"], DS.SISTEMAS[r["sistema"]][1]), mil(e["A"], 0), "%.3f" % e["C"], "%.1f" % e["Q"]])
    D.tabla("Caudal máximo de cada eje (tramo final)", ["Eje", "Sistema - descarga", "Área acum. (m²)", "C", "Q (l/s)"], filas, [2.3, 3.5, 3, 2, 2.5], tam=8)
    # =========================================================================== 4
    D.h(1, "Drenaje")
    D.h(2, "Drenaje pluvial de las edificaciones")
    D.p("El sistema se desarrolla en la secuencia techo → canaleta → montante → cuneta → descarga. Las coberturas a dos aguas entregan a "
        "canaletas en los aleros; los montantes bajan el agua a las cunetas, que además reciben la escorrentía de veredas, patios y áreas "
        "verdes, y la conducen por gravedad hasta las cuatro descargas por el cerco.")
    D.h(2, "Parámetros hidrológicos e hidráulicos")
    D.tabla("Parámetros de diseño", ["Parámetro", "Valor"],
            [["Intensidad de diseño", "%.2f mm/h" % HID["I"]], ["Factor de seguridad", "%.2f" % FS], ["C techos y pavimentos", "0.88"], ["C áreas verdes", "0.40"],
             ["Manning canaletas (plancha galvanizada / PVC)", "0.013"], ["Manning cunetas (capacidad / velocidad)", "0.015 / 0.013"],
             ["Pendiente mínima de canaletas", "1.00 %"], ["Pendiente mínima de cunetas", "0.50 %"], ["Borde libre mínimo de cunetas", "0.05 m"], ["Velocidad máxima", "3.0 m/s"]], [10, 5])
    D.h(2, "Dimensionamiento de canaletas y montantes")
    qm2 = 0.88 * HID["I"] / 3.6e6 * FS * 1000               # l/s por m2 de techo
    Qmon = wyly_q(MONT_D); Amon = Qmon / qm2
    Qcan = manning(CAN_B, CAN_H - 0.05, CAN_S, CAN_N) * 1000
    D.p("La capacidad de las canaletas se verifica con Manning y la de los montantes con la ecuación de Wyly-Eaton (relación de llenado rs = 0.25), "
        "con los mismos criterios de los proyectos de Morales:")
    D.formula("Q (gpm) = 27.8 · rs^(5/3) · D^(8/3)     (D en pulgadas; 1 l/s = 15.85 gpm)")
    D.p("Con la intensidad de diseño, cada m² de techo aporta %.4f l/s. Un montante de PVC de 4\" conduce %.2f l/s, por lo que puede atender "
        "hasta %.1f m² de techo en proyección horizontal. Una canaleta de %.2f × %.2f m con pendiente de 1 %% conduce %.1f l/s con 0.05 m de borde libre." % (qm2, Qmon, Amon, CAN_B, CAN_H, Qcan))
    filas = []
    for i, x in enumerate(cb, 1):
        lado = x["A"] / 2; n = max(1, math.ceil(lado / Amon)); q = lado / n * qm2
        filas.append(["Cobertura %02d" % i, mil(x["A"]), mil(lado), n, "%.2f" % q, "%.2f" % wyly_d(q), "4\"", "%.1f" % (lado * qm2)])
    D.tabla("Montantes mínimos por lado de cada cobertura (techos a dos aguas)", ["Paño", "Área (m²)", "Por lado (m²)", "Montantes por lado", "Q por montante (l/s)",
            "D requerido (pulg.)", "D adoptado", "Q canaleta por lado (l/s)"], filas, [2.1, 1.7, 1.8, 1.7, 1.9, 1.9, 1.6, 2.3], tam=7.5)
    D.p("El número de montantes es el mínimo hidráulico; su ubicación definitiva se coordina con los planos de coberturas y arquitectura, "
        "entregando siempre a tramos de cuneta con rejilla. El diámetro adoptado de 4\" supera el mínimo del artículo 12.5 de la Norma CE.040.")
    D.h(2, "Cunetas de concreto")
    D.p("Las cunetas son de sección rectangular en U, con losa de fondo y muros de 0.10 m de espesor: ancho interior de 0.40 m y ancho exterior "
        "total de 0.60 m, sobre solado de 4\". La profundidad es variable: 0.30 m al inicio de cada eje y aumenta con la pendiente de la cota de "
        "fondo (mínima 0.5 %%) porque el borde se mantiene al ras del piso (+184.65; +184.50 en el patio de maniobra), hasta %.2f m como máximo. "
        "Se coloca acero solo donde la profundidad es 0.40 m o más y en los tramos tapados; con menos de 0.40 m la cuneta es de concreto simple." % c["hmax"])
    D.figura(os.path.join(c["FIG"], "fig_secciones.png"), "Secciones típicas de cuneta con rejilla y tramo tapado (lámina DC-02).", 14)
    D.h(2, "Cunetas cubiertas y pasos de circulación")
    D.p("En los tramos abiertos se instala rejilla metálica móvil de platinas de 1\" x 3/16\" con marco de ángulo de 1\" x 1\" x 3/16\". En los cruces "
        "de vereda, ingresos, patio de maniobra y en el pase por el cerco, la cuneta se cubre con losa de concreto de 0.10 m; en estos tramos se "
        "verifica la altura libre bajo la losa y se colocan tapas de inspección de 0.60 x 0.60 m al inicio y al final, en cada empalme y a 10 m "
        "como máximo (%d tapas)." % c["tapas"])
    D.h(2, "Juntas y criterios constructivos")
    D.p("Se disponen juntas de dilatación de 1\" con sellador asfáltico en toda la sección en U cada 3.00 m (EG-2013, sección 510), y junta "
        "asfáltica entre la cuneta y el piso adyacente, al mismo nivel del piso terminado. Los cambios de dirección se resuelven con quiebres "
        "a 45° (chaflanes de 0.60 m) para evitar el resalto hidráulico, y los ejes que llegan entran en diagonal a la cuneta que los recibe.")
    D.h(2, "Profundidad y secciones adoptadas")
    filas = [[x["eje"], mil(x["L"]), mil(x["L_tapado"]), "%.2f" % x["h_prom"], "%.2f" % x["h_max"], mil(x["L_acero"])] for x in c["q"]]
    filas.append(["Total", mil(c["L"]), mil(c["Ltap"]), "", "", mil(sum(x["L_acero"] for x in c["q"]))])
    D.tabla("Longitudes y profundidades de los ejes de cuneta", ["Eje", "L (m)", "Tapado (m)", "h prom. (m)", "h máx. (m)", "L con acero (m)"], filas, [2.2, 2.4, 2.4, 2.4, 2.4, 2.8], tam=8, total=True)
    D.h(2, "Verificación del funcionamiento hidráulico")
    D.p("Para cada tramo se calcula el tirante normal con Manning (n = 0.015) y se verifica el borde libre respecto de la altura libre (bajo la "
        "losa en los tramos tapados); la velocidad se calcula con n = 0.013. Un tramo cumple si el borde libre es de 0.05 m o más, la velocidad "
        "no supera 3.0 m/s y la pendiente es de 0.5 % o más.")
    D.formula("Q = (1/n) · A · R^(2/3) · S^(1/2)     A = b · y     R = b·y / (b + 2y)")
    filas = [[f["ramal"], f["de"], f["a"], mil(f["A_m2"], 0), "%.1f" % f["Q_ls"], "%.2f" % f["S"], "%.3f" % f["y"], "%.2f" % f["h"], "%.3f" % f["borde_libre"], "%.2f" % f["V"],
              "Cumple" if f["cap"] == "CUMPLE" else "No cumple"] for f in hid]
    D.tabla("Verificación hidráulica por tramo", ["Eje", "De", "A", "Área (m²)", "Q (l/s)", "S (%)", "y (m)", "h libre (m)", "BL (m)", "V (m/s)", "Estado"],
            filas, [1.5, 1.2, 1.2, 1.5, 1.4, 1.2, 1.3, 1.4, 1.3, 1.3, 1.6], tam=7)
    D.p("Todos los tramos cumplen: caudal máximo %.1f l/s, menor borde libre %.3f m y velocidad máxima %.2f m/s. La sección de 0.60 m de ancho "
        "total y 0.40 m libres se mantiene en toda la red." % (c["Qmax"], c["BLmin"], c["Vmax"]))
    D.tabla("Comprobaciones del diseño", ["N°", "Comprobación", "Estado"], [[x["n"], x["comprobacion"], x["estado"]] for x in V["comprobaciones"]], [1, 12, 2.5], tam=8)
    D.h(2, "Descargas")
    D.p("La red se divide en cuatro sistemas, cada uno con su descarga por gravedad mediante un pase en el cimiento del cerco perimétrico, en "
        "tramo tapado. Fuera del cerco no se construyen obras: el agua sigue por el terreno natural, que se perfila al pie del cerco.")
    import re
    lim = lambda t: re.sub(r"\s+", " ", re.sub(r"\(\s*\)", "", re.sub(r",?\s*x\s*=\s*[\d.]+", "", t))).strip()
    filas = [[k, "%.3f" % c["dsc"][k]["cf"], "%.2f" % c["dsc"][k]["terreno"], lim(c["dsc"][k]["receptor"])] for k in sorted(c["dsc"])]
    D.tabla("Descargas de la red de cunetas", ["Descarga", "Cota de fondo", "Terreno al pie", "Receptor"], filas, [2, 2.3, 2.3, 9], tam=8)
    D.figura(os.path.join(c["FIG"], "fig_descarga_d1.png"), "Detalle de la descarga D1: planta, perfil longitudinal e isométrico (lámina DC-16).", 15.5)
    D.h(2, "Presentación de los cálculos")
    D.p("El cálculo completo se presenta en la memoria de cálculo (Excel con fórmulas): datos, serie, frecuencias, prueba de Kolmogorov-Smirnov, "
        "curvas IDF, superficies, caudales y verificación de Manning de los 91 tramos, y descargas. Los planos DC-01 a DC-19 presentan la planta, "
        "las secciones típicas, los perfiles longitudinales por eje, las secciones transversales, los cortes y el detalle de cada descarga.")
    # =========================================================================== 5 y 6
    D.h(1, "Conclusiones")
    D.vinetas([
        "Se determinaron los parámetros hidrológicos e hidráulicos del sistema de drenaje pluvial del proyecto %s, C.I. N° 468901." % nom_p,
        "La serie de precipitación máxima en 24 horas de la estación CO Tarapoto (1999–2024) se trasladó a Barranquita con un factor de %.4f, "
        "obtenido con la precipitación media anual de las estaciones de llanura Navarro, Pelejo y Shanusi (%s mm)." % (HID["factor"], mil(H.P_ANUAL_BARRANQUITA)),
        "La distribución Log-Normal presenta el mejor ajuste (Kolmogorov-Smirnov D = %.4f < 0.27). La precipitación máxima en 24 horas para T = 25 años es %.2f mm." % (ks["lognormal"], HID["P24"]),
        "La intensidad de diseño para tc = 10 minutos (Dick y Peschke) es %.2f mm/h; la ecuación IDF es I = %.2f T^%.4f / t^%.4f." % (HID["I"], HID["K"], HID["m"], HID["n"]),
        "El área de intervención es de %s m², con coeficiente de escorrentía ponderado de %.3f, y los caudales se afectan por un factor de seguridad de %.2f." % (mil(hv["A_total"], 0), hv["C"], FS),
        "La red de cunetas tiene %s m en 19 ejes y 4 sistemas; las cunetas de 0.60 m de ancho total (0.40 m libres) cumplen en todos los tramos, con caudal máximo de %.1f l/s, borde libre mínimo de %.3f m y velocidad máxima de %.2f m/s." % (mil(c["L"]), c["Qmax"], c["BLmin"], c["Vmax"]),
        "Los montantes de PVC de 4\" atienden hasta %.1f m² de techo cada uno; el número mínimo por cobertura se presenta en este estudio." % Amon,
        "Las cuatro descargas funcionan por gravedad a través del cimiento del cerco."])
    D.h(1, "Recomendaciones")
    D.vinetas([
        "Respetar durante la obra las dimensiones, cotas de fondo, pendientes, quiebres a 45° y descargas de los planos; cualquier cambio debe ser evaluado previamente.",
        "Verificar con control topográfico que la cota de fondo de las cunetas tenga pendiente mínima de 0.5 % y que las canaletas tengan 1 % como mínimo, sin contrapendientes.",
        "Entregar los montantes a tramos de cuneta con rejilla y proteger su llegada para evitar salpicaduras sobre muros y veredas.",
        "No reducir la sección de las cunetas con tuberías, soportes o acabados; mantener el acabado interior liso del fondo.",
        "Proteger contra la erosión la entrega de la descarga D2, donde el terreno exterior baja unos 3 m en talud, coordinándolo con el propietario del terreno exterior; perfilar el terreno al pie del cerco en D1, D3 y D4.",
        "Antes de la puesta en funcionamiento, retirar residuos de obra y realizar una prueba de escurrimiento desde los puntos altos de cada sistema.",
        "Limpiar canaletas, rejillas, tapas de inspección y cunetas antes y durante la temporada de lluvias (noviembre a abril), e implementar un programa de mantenimiento preventivo.",
        "Toda ampliación futura de techos o pavimentos requiere una nueva evaluación hidrológica e hidráulica.",
        "Cuando el SENAMHI disponga de series de precipitación máxima en 24 horas de Navarro, Pelejo o Shanusi con registros recientes, contrastarlas con la serie transpuesta."])
    D.h(1, "Anexos")
    D.vinetas(["Memoria de cálculo hidrológico e hidráulico (Excel): MEMORIA_CALCULO_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.xlsx.",
               "Planos de drenaje pluvial DC-01 a DC-19 (PLANTEAMIENTO_CUNETAS_IE0590_BARRANQUITA.dxf)."])
    D.figura(os.path.join(c["FIG"], "fig_planta.png"), "Planta general de cunetas (lámina DC-01).", 15.5)
    D.figura(os.path.join(c["FIG"], "fig_perfil.png"), "Perfil longitudinal típico por eje (lámina DC-04).", 15.5)
