"""Memorias de drenaje pluvial en Word: MEMORIA_HIDROLOGICA_DRENAJE_PLUVIAL.docx y MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL.docx.

Capitulos de los expedientes de la I.E. N.° 0590 Barranquita (C.I. 468901) y de los CAR de Morales (CUI 2705619, 2675514 y
2717013), llenados solo con lo que calcula DrenIE para este proyecto: lluvia de la estacion (analisis de frecuencias,
Kolmogorov-Smirnov, Dick y Peschke, IDF de Bell), superficies y coeficientes, caudales por tramo (techos, pisos y areas verdes),
secciones por sector, verificacion hidraulica, comprobaciones, descargas, lloraderos, canaletas y montantes, sumideros,
metas fisicas del metrado y relacion de planos. Lo que el programa no conoce (antecedentes, accesos, clima) solo aparece si el
proyecto lo trae en "memoria"; no se inventan datos.
"""
import os

from . import normas, word

f2 = lambda v: "%.2f" % v
mil = lambda v, d=2: ("{:,.%df}" % d).format(v)
NOM_SUP = {"techo": "Techos (coberturas)", "vereda": "Veredas", "patio": "Patios", "pavimento": "Pavimentos y áreas libres de concreto",
           "estacionamiento": "Patio de maniobra y estacionamiento", "juegos": "Área de juegos", "cuneta": "Cunetas", "verde": "Áreas verdes"}
NORMAS = ["Reglamento Nacional de Edificaciones: Norma Técnica CE.040 Drenaje Pluvial (R.M. N° 126-2021-VIVIENDA); Norma E.060 Concreto Armado; "
          "Norma IS.010 Instalaciones Sanitarias para Edificaciones.",
          "Manual de Hidrología, Hidráulica y Drenaje del Ministerio de Transportes y Comunicaciones.",
          "Especificaciones Técnicas Generales para Construcción EG-2013 (MTC), sección 510.",
          "Norma G.050 Seguridad durante la construcción."]


def _nombre(pr): return pr.get("nombre", "").strip("“”\"")


def _cita(pr):
    c = word.codigo_de(pr)
    return "“%s”%s" % (_nombre(pr), (", " + c) if c else "")


class Contexto:
    def __init__(self, cfg, P, Rh, LL, V, C, R, secciones, TT, SM, LLt, laminas, metas, rep_t, mapa, figuras):
        self.cfg, self.P, self.Rh, self.LL, self.V, self.C, self.R = cfg, P, Rh, LL, V, C, R
        self.pr = cfg.get("proyecto", {}); self.mem = cfg.get("memoria", {}) or {}
        self.sec, self.TT, self.SM, self.LLt, self.lam, self.metas, self.rep_t, self.mapa, self.fig = secciones, TT, SM, LLt, laminas, metas, rep_t, mapa, figuras
        self.hv = V["hidrologia"]; hid = V["hidraulica"]
        self.por_eje = {}
        for f in hid:
            e = self.por_eje.get(f["eje"])
            if e is None or f["Q_ls"] > e["Q_ls"]: self.por_eje[f["eje"]] = f
        self.bl_min = {}
        for f in hid: self.bl_min[f["eje"]] = min(self.bl_min.get(f["eje"], 9), f["borde_libre"])
        self.Qmax = max(f["Q_ls"] for f in hid); self.Vmax = max(f["V"] for f in hid); self.BLmin = min(f["borde_libre"] for f in hid)
        self.L = sum(r["L"] for r in C["ramales"]); self.Ltap = sum(t["L_tapado"] for r in C["ramales"] for t in r["tramos"])
        self.hmax = max(t["h_max"] for r in C["ramales"] for t in r["tramos"])
        self.sectores = {}
        for s in secciones:
            g = self.sectores.setdefault(s["sector"], {"ejes": [], "L": 0.0, "b": 0.0, "Q": 0.0})
            g["ejes"].append(s["eje"]); g["L"] += s["L_m"]; g["b"] = max(g["b"], s["b_adoptado"]); g["Q"] = max(g["Q"], s["Q_max_ls"])
        self.bs = sorted({s["b_adoptado"] for s in secciones})
        niv = cfg.get("niveles", {}) or {}
        self.npt = niv.get("borde_cuneta") or niv.get("npt"); self.verde = niv.get("area_verde")
        self.zonas = [(z.get("nombre", "zona"), z["nivel"]) for z in niv.get("zonas", []) if z.get("nivel") is not None]
        cod = [x["codigo"] for x in laminas]
        self.planos = ("%s a %s" % (cod[0], cod[-1])) if cod else ""
        self.planta = cod[0] if cod else ""

    def anchos(self):
        em = self.P["e_muro"]
        return " y ".join("%.2f m libres (%.2f m de ancho total)" % (b, b + 2 * em) for b in self.bs)

    def niveles(self):
        if self.npt is None: return []
        s = ["borde de cuneta y pisos al NPT +%.2f" % self.npt]
        if self.verde is not None: s.append("áreas verdes a +%.2f" % self.verde)
        s += ["%s a +%.2f" % (n.lower(), z) for n, z in self.zonas]
        return s

    def descargas(self):
        D = [d["D"] for d in self.V["descargas"]]
        if not D: return "las descargas"
        return ("una descarga (%s)" % D[0]) if len(D) == 1 else "%d descargas (%s)" % (len(D), ", ".join(D))


def _ubicacion(Dc, c):
    pr, mem = c.pr, c.mem
    filas = [[k, mem[k2]] for k, k2 in (("Departamento", "departamento"), ("Provincia", "provincia"), ("Distrito", "distrito"), ("Localidad", "localidad"),
                                         ("Predio", "predio"), ("Colindancias", "colindancias"), ("Acceso", "acceso")) if mem.get(k2)]
    if pr.get("ubicacion") and not filas: filas.append(["Ubicación", pr["ubicacion"]])
    filas.append(["Área de intervención (dentro del cerco)", "%s m²" % mil(c.mapa.get("area_total_m2") or c.hv["A_total"], 0)])
    if c.npt is not None: filas.append(["Nivel de piso terminado (NPT)", "+%.2f m s. n. m." % c.npt])
    if c.rep_t.get("z_min") is not None:
        filas.append(["Terreno (curvas de nivel leídas)", "de %.2f a %.2f m s. n. m." % (c.rep_t["z_min"], c.rep_t["z_max"])])
    Dc.tabla("Ubicación del proyecto", ["Descripción", "Dato"], filas, [5.5, 10])


# ============================================================================== MEMORIA HIDROLOGICA
def hidrologica(D, c):
    Rh, hv, P = c.Rh, c.hv, c.P
    D.h(1, "Generalidades")
    D.h(2, "Introducción")
    D.p("La presente memoria hidrológica sustenta el dimensionamiento del sistema de drenaje pluvial (red de cunetas) del proyecto %s. "
        "La evacuación ordenada de las aguas de lluvia de techos, pisos y áreas libres protege las edificaciones, los pisos y las circulaciones "
        "del local." % _cita(c.pr))
    if c.mem.get("clima"): D.p(c.mem["clima"])
    D.h(2, "Objetivos")
    D.vinetas(["Determinar la precipitación máxima en 24 horas para el periodo de retorno de diseño mediante el análisis de frecuencias.",
               "Obtener las lluvias de corta duración, las intensidades y las curvas intensidad - duración - frecuencia (IDF).",
               "Determinar los coeficientes de escorrentía, las áreas de aporte y los caudales de diseño de cada tramo de cuneta.",
               "Dimensionar las cunetas con medidas constructivas, una sola sección por sector de descarga, y verificar su capacidad, velocidad y descargas.",
               "Dimensionar las canaletas, montantes y sumideros de piso."])
    D.h(2, "Ubicación del proyecto")
    _ubicacion(D, c)
    D.h(2, "Alcance")
    D.p("El estudio comprende el área de intervención delimitada por el cerco perimétrico (%s m²). Las aguas de lluvia de las coberturas llegan a "
        "las cunetas mediante canaletas y montantes, y las de pisos y áreas libres por escurrimiento superficial o por sumideros; la red de cunetas "
        "conduce el agua por gravedad hasta %s que atraviesan el cerco." % (mil(c.mapa.get("area_total_m2") or hv["A_total"], 0), c.descargas()))
    # ---------------------------------------------------------------- lluvia
    if Rh:
        A = Rh["analisis"]; e = Rh["estacion"] or {}
        D.h(1, "Información pluviométrica")
        D.h(2, "Estación de referencia")
        filas = [[k, str(e[k2])] for k, k2 in (("Estación", "nombre"), ("Código", "codigo"), ("Entidad", "entidad"), ("Departamento", "departamento"),
                                                ("Provincia", "provincia"), ("Distrito", "distrito"), ("Latitud", "latitud"), ("Longitud", "longitud")) if e.get(k2)]
        if e.get("altitud"): filas.append(["Altitud", "%s m s. n. m." % e["altitud"]])
        filas += [["Variable", "Precipitación máxima en 24 horas (mm)"], ["Periodo", "%d - %d (%d años)" % (Rh["maximos"][0][0], Rh["maximos"][-1][0], A["n"])],
                  ["Origen de los datos", Rh["fuente_serie"]]]
        D.tabla("Características de la estación", ["Característica", "Información"], filas, [5, 10.5])
        filas = [[a] + [("S/D" if v is None else "%.1f" % v) for v in m] + ["%.1f" % max(v for v in m if v is not None)]
                 for a, m in sorted(Rh["serie_mensual"].items()) if any(v is not None for v in m)]
        D.tabla("Precipitación máxima en 24 horas por mes (mm)", ["Año", "E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D", "Máx."],
                filas, [1.05] + [1.08] * 12 + [1.2], tam=6.5, fuente="%s. S/D: sin dato." % (e.get("entidad") or "Registro de la estación"))
        mx = [v for _, v in Rh["maximos"]]
        D.p("La serie de máximos anuales tiene %d valores, de %.1f mm a %.1f mm, con media de %.2f mm y desviación estándar de %.2f mm." % (
            A["n"], min(mx), max(mx), A["media"], A["desv"]))
        if abs(Rh["factor"] - 1.0) > 1e-6:
            D.p("La serie se traslada al lugar del proyecto con un factor de transposición de %.4f (relación de precipitaciones medias anuales, "
                "Manual de Hidrología, Hidráulica y Drenaje del MTC)." % Rh["factor"])
        D.h(1, "Análisis de frecuencias")
        D.h(2, "Parámetros estadísticos")
        D.tabla("Parámetros de la serie", ["Parámetro", "Valor"],
                [["Número de datos (n)", A["n"]], ["Media (mm)", f2(A["media"])], ["Desviación estándar (mm)", f2(A["desv"])],
                 ["Coeficiente de asimetría", "%.3f" % A["cs"]], ["Media de log P", "%.4f" % A["media_log"]], ["Desviación estándar de log P", "%.4f" % A["desv_log"]],
                 ["Asimetría de log P", "%.4f" % A["cs_log"]], ["Gumbel: yn y sn (Aparicio)", "%.4f y %.4f" % (A["gumbel_yn"], A["gumbel_sn"])]], [8, 4])
        D.h(2, "Distribuciones de probabilidad")
        D.p("Se ajustaron las distribuciones Normal, Log Normal de dos parámetros, Log Pearson tipo III (factor de frecuencia de Kite) y Extrema "
            "tipo I o Gumbel (con los valores yn y sn de Aparicio para la muestra):")
        D.vinetas(["Normal: P = media + z · s", "Log Normal: log P = media(log P) + z · s(log P)",
                   "Log Pearson III: log P = media(log P) + KT · s(log P), con KT de Kite (k = Cs/6)",
                   "Gumbel: P = u + y / α, con α = sn / s, u = media − yn / α e y = −ln(−ln(1 − 1/T))"])
        filas = [[T] + [f2(A["tabla"][T][k]) for k in ("normal", "lognormal", "lp3", "gumbel")] for T in sorted(A["tabla"])]
        D.tabla("Precipitación máxima en 24 h por periodo de retorno (mm)", ["T (años)", "Normal", "Log Normal", "Log Pearson III", "Gumbel"],
                filas, [2.5, 3, 3, 3, 3])
        D.h(2, "Prueba de bondad de ajuste")
        ks = A["ks"]
        D.p("Se aplicó la prueba de Kolmogorov-Smirnov con la probabilidad empírica de Weibull, m/(n+1). Para n = %d y nivel de significación de 0.05 el "
            "estadístico crítico es %.4f. Se adopta la distribución %s%s." % (A["n"], A["ks_critico"], Rh["distribucion_nombre"],
                                                                       ", que presenta el menor estadístico" if Rh["distribucion"] == A["elegida"] else ""))
        D.tabla("Prueba de Kolmogorov-Smirnov", ["Distribución", "D máx.", "D crítico", "Resultado"],
                [[n, "%.4f" % ks[k], "%.4f" % A["ks_critico"], ("Se acepta" if ks[k] <= A["ks_critico"] else "No se acepta") + (" (adoptada)" if k == Rh["distribucion"] else "")]
                 for k, n in (("normal", "Normal"), ("lognormal", "Log Normal"), ("lp3", "Log Pearson III"), ("gumbel", "Gumbel"))], [4, 3, 3, 4])
        D.h(1, "Periodo de retorno y tiempo de concentración")
        D.p("Se adopta un periodo de retorno de %d años para las cunetas, canaletas y montantes. El tiempo de concentración de cada cuneta se toma igual a "
            "la duración mínima de %.0f minutos, porque las áreas de aporte son pequeñas, con recorridos cortos sobre techos y pavimentos." % (Rh["T"], Rh["tc_min"]))
        normas.recuadro_word(D, "T", "tc_min")
        D.h(1, "Lluvias de corta duración e intensidades")
        D.p("Las lluvias de corta duración se obtienen con la expresión de Dick y Peschke, recomendada por el Manual de Hidrología del MTC, y la "
            "intensidad como la lluvia dividida entre la duración:")
        D.formula("P(D) = P24 · (D / 1440)^0.25          I = P(D) · 60 / D")
        Ts = [T for T in (2, 5, 10, 25, 50, 100) if T in Rh["idf"]]
        filas = [[Dm] + ["%.1f" % Rh["idf"][T][Dm] for T in Ts] for Dm in (5, 10, 15, 20, 30, 60, 120, 240, 720, 1440) if Dm in Rh["idf"][Ts[0]]]
        D.tabla("Intensidades máximas (mm/h)", ["D (min)"] + ["T = %d" % T for T in Ts], filas, [2] + [2.2] * len(Ts))
        D.p("Con el modelo de Bell (duraciones de 5 a 60 minutos) y la regresión de las intensidades se obtiene la ecuación de las curvas IDF:")
        D.formula("I = %.2f · T^%.4f / t^%.4f     (I en mm/h, T en años, t en minutos)" % (Rh["K"], Rh["m"], Rh["n"]))
        D.figura(c.fig.get("idf"), "Curvas intensidad - duración - frecuencia y serie de precipitación máxima en 24 h.", 15.5)
        D.tabla("Intensidad de diseño", ["Parámetro", "Valor"],
                [["P máx. 24 h, T = %d años (%s)" % (Rh["T"], Rh["distribucion_nombre"]), "%.2f mm" % Rh["P24"]],
                 ["Lluvia en tc = %.0f min (Dick y Peschke)" % Rh["tc_min"], "%.2f mm" % Rh["P_tc"]], ["Intensidad de diseño", "%.2f mm/h" % Rh["I"]]], [9, 4])
    else:
        D.h(1, "Intensidad de diseño")
        D.p("El proyecto no trae registros de una estación; se usa la intensidad de diseño indicada: I = %.2f mm/h (%s)." % (
            hv["I"], c.LL.get("fuente") or "dato del proyecto"))
        normas.recuadro_word(D, "tc_min")
    # ---------------------------------------------------------------- superficies
    D.h(1, "Coeficientes de escorrentía y áreas de aporte")
    D.p("El área dentro del cerco se dividió en superficies según la planta del proyecto (techos, pisos de concreto y áreas verdes) y cada celda de "
        "1 m² se asignó a la cuneta que la recibe; en los techos, cada agua descarga a la cuneta de su lado por medio de canaletas y montantes.")
    sup = hv["superficies"]; tot = sum(v["A"] for v in sup.values()) or 1.0
    filas = [[NOM_SUP.get(k, k.capitalize()), mil(v["A"], 0), f2(v["C"]), "%.1f %%" % (100 * v["A"] / tot)] for k, v in sup.items() if v["A"] > 0]
    filas.append(["Total / C ponderado", mil(tot, 0), "%.3f" % hv["C"], "100.0 %"])
    D.tabla("Superficies y coeficiente de escorrentía", ["Superficie", "Área (m²)", "C", "%"], filas, [8.5, 2.5, 2, 2], total=True)
    normas.recuadro_word(D, "C_tabla1a")
    D.figura(c.fig.get("planta"), "Planta de la red de cunetas, descargas y superficies de aporte.", 15.5)
    # ---------------------------------------------------------------- caudales
    D.h(1, "Caudales de diseño")
    D.p("Los caudales se calculan con el método racional, válido para áreas pequeñas, separando el aporte de techos, pisos y áreas verdes:")
    D.formula("Q = C · I · A · FS / 3 600 000     (Q en m³/s; I en mm/h; A en m²; FS = %.2f)" % hv["FS"])
    normas.recuadro_word(D, "FS")
    D.p("El caudal de cada tramo considera el área acumulada aguas arriba, incluidas las cuencas de los ejes que le entregan. La tabla muestra el tramo "
        "más cargado de cada eje; el detalle por tramo está en la hoja POR TRAMO del libro DIMENSIONAMIENTO.xlsx.")
    filas = [[e, f["sector"], mil(f["A_m2"], 0), "%.1f" % f["Q_techo_ls"], "%.1f" % f["Q_pisos_ls"], "%.1f" % f["Q_verde_ls"], "%.1f" % f["Q_ls"]]
             for e, f in sorted(c.por_eje.items())]
    D.tabla("Caudal máximo por eje (tramo más cargado)", ["Eje", "Descarga", "Área acum. (m²)", "Q techos (l/s)", "Q pisos (l/s)", "Q áreas verdes (l/s)", "Q total (l/s)"],
            filas, [2, 1.8, 2.4, 2.3, 2.2, 2.6, 2.2], tam=8)
    # ---------------------------------------------------------------- secciones
    D.h(1, "Dimensionamiento de las cunetas")
    D.p("La cuneta es un canal rectangular de concreto con muros de %.2f m y losa de fondo de %.2f m sobre solado de %.2f m. Para cada tramo se busca el "
        "menor ancho libre, entre %.2f m y %.2f m, con el que el tirante deja el borde libre mínimo; las medidas van de 5 en 5 cm para que sean "
        "constructivas. Todos los ejes que salen por una misma descarga llevan una sola sección, la mayor que pide el sector; si hace falta más "
        "capacidad que la del ancho máximo, se profundiza la cuneta. El dimensionamiento adoptado es el de la tabla siguiente." % (
            P["e_muro"], P["e_fondo"], P["e_solado"], P["b_int"], P["b_max"]))
    filas = [[k, ", ".join(g["ejes"]), mil(g["L"]), "%.1f" % g["Q"], f2(g["b"]), f2(g["b"] + 2 * P["e_muro"])] for k, g in sorted(c.sectores.items())]
    D.tabla("Sección adoptada por sector de descarga", ["Sector", "Ejes", "L (m)", "Q máx. (l/s)", "Ancho libre (m)", "Ancho total (m)"], filas,
            [1.6, 7, 1.8, 1.8, 1.8, 1.8], tam=7.5)
    D.h(1, "Verificación hidráulica de las cunetas")
    D.p("La profundidad es variable desde %.2f m al inicio de cada eje, con la cota de fondo en pendiente mínima de %.1f %% y el borde al ras del piso. "
        "Con el caudal de diseño se verifica:" % (P["h0"], 100 * P["S0"]))
    D.vinetas(["Capacidad: tirante normal de Manning con n = %.3f (concreto con rejilla) y borde libre mínimo de %.2f m respecto de la altura libre (bajo la losa en los tramos tapados)." % (P["n_cap"], P["BL"]),
               "Velocidad: con n = %.3f (concreto liso), máximo %.1f m/s para no erosionar el concreto." % (P["n_vel"], P["Vmax"]),
               "Pendiente mínima de %.1f %% en todos los tramos, para la autolimpieza." % (100 * P["S0"])])
    D.formula("Q = (1/n) · A · R^(2/3) · S^(1/2)     A = b · y     R = b·y / (b + 2y)")
    normas.recuadro_word(D, "n_cap", "n_vel", "Vmax", "BL", "S0")
    filas = [[e, "%.1f" % f["Q_ls"], f2(f["S_pct"]), f2(f["b"]), "%.3f" % f["y"], f2(f["h"]), "%.3f" % c.bl_min[e], f2(f["V"]),
              "Cumple" if f["cap"] == "CUMPLE" and f["vel"] == "CUMPLE" else "Revisar"] for e, f in sorted(c.por_eje.items())]
    D.tabla("Verificación hidráulica por eje (tramo más cargado)", ["Eje", "Q (l/s)", "S (%)", "b (m)", "y (m)", "h libre (m)", "BL mín. (m)", "V (m/s)", "Estado"],
            filas, [1.8, 1.6, 1.4, 1.4, 1.5, 1.7, 1.8, 1.5, 1.6], tam=8)
    D.p("El caudal máximo es %.1f l/s, el menor borde libre es %.3f m y la velocidad máxima es %.2f m/s; la profundidad varía de %.2f m a %.2f m para "
        "seguir la pendiente de la cota de fondo con el borde al ras del piso." % (c.Qmax, c.BLmin, c.Vmax, P["h0"], c.hmax))
    D.tabla("Comprobaciones del diseño", ["N°", "Comprobación", "Estado"],
            [[x["n"], x["comprobacion"].replace("diseno", "diseño").replace("minima", "mínima").replace("maxima", "máxima"), x["estado"]]
             for x in c.V["comprobaciones"]], [1, 12, 2.5], tam=8)
    # ---------------------------------------------------------------- techo y piso
    if c.TT["montantes"]:
        T = c.TT
        D.h(1, "Canaletas y montantes")
        D.p("Las canaletas de plancha galvanizada de 0.25 x 0.20 m van en los aleros con pendiente de 1 %% hacia las montantes. Las montantes son todas de "
            "tubería PVC de 4\" y van en las esquinas de las edificaciones, en una falsa columna adosada al muro; cuando el área de techo de un lado lo pide "
            "se colocan 3 o 4 montantes de 4\" en ese lado en lugar de un diámetro mayor. La capacidad de cada montante se verifica con la fórmula de "
            "Wyly-Eaton (relación de llenado 1/4; hasta 7/24 cuando el lado lleva 4 montantes, como máximo por lado) y la de la canaleta con "
            "Manning (n = 0.013, borde libre 0.05 m).")
        filas = [[x["techo"], x["lado"], mil(x["A_m2"]), mil(x["L_canaleta_m"]), "%.1f" % x["Q_ls"], x["montantes"], "%.2f" % x["Q_por_montante_ls"],
                  "%.3f" % x["tirante_m"], x["canaleta"]] for x in T["lados"]]
        D.tabla("Canaletas y montantes por lado de techo", ["Techo", "Lado", "Área (m²)", "Canaleta (m)", "Q (l/s)", "Montantes 4\"", "Q / montante (l/s)", "Tirante (m)", "Estado"],
                filas, [1.4, 1.6, 1.7, 1.8, 1.5, 1.7, 2, 1.6, 1.8], tam=7.5)
        normas.recuadro_word(D, "D_montante_min", "wyly", "S_canaleta", "llegada")
        m = T["metrado"]
        D.p("En total: %s m de canaleta, %d montantes de 4\" en las esquinas, cada uno en una falsa columna de 0.20 x 0.15 x 1.30 m sobre su dado. "
            "En el dado, un codo de 90° de 4\" y la tubería PVC de 4\" enterrada hasta la cuneta (%s m en total, hasta 5 m por montante), con pendiente "
            "de 1 %% (mínimo 0.5 %%), llegando sobre el nivel del agua de la cuneta más 0.05 m para que no quede ahogada. La cuneta puede ir a lo largo "
            "del alero o transversal a él: lo que se verifica es que el tubo de cada montante llegue." % (
                mil(m["canaleta_m"]), m["montantes_und"], mil(m["tuberia_enterrada_m"])))
        mt = [x for x in T["montantes"] if x.get("tubo_enterrado_m")]
        if mt:
            D.tabla("Salida enterrada de cada montante (del dado a la cuneta)", ["Montante", "Techo", "Cuneta", "Tubo (m)", "S (%)", "Llegada", "Cota de fondo",
                                                                                  "Nivel mínimo", "Estado"],
                    [[x["montante"], x["techo"], x["cuneta"], f2(x["tubo_enterrado_m"]), f2(x["S_tubo_pct"]), "%.3f" % x["z_llegada"], "%.3f" % x["cf_cuneta"],
                      "%.3f" % x["nivel_min"], x["llega"].lower()] for x in mt], [1.6, 1.3, 1.6, 1.4, 1.2, 1.7, 1.9, 1.9, 2.4], tam=7.5)
    if c.SM["sumideros"]:
        D.h(1, "Sumideros de piso")
        D.p("Los sumideros se colocan solo en las áreas libres sin cobertura (patios, estacionamientos y pavimentos; no en áreas verdes ni en veredas) que "
            "quedan lejos de una cuneta. Cada uno descarga con tubería PVC de 4\" a la cuneta más cercana, con pendiente de 1 % (mínimo 0.5 %), llegando "
            "sobre el nivel del agua de la cuneta (cota de fondo + tirante) más 0.05 m, para que no quede ahogada (Norma CE.040).")
        filas = [[s["sumidero"], mil(s["A_m2"], 0), "%.2f" % s["Q_ls"], s["cuneta"], mil(s["L_tubo_m"]), f2(s["S_tubo_pct"]), "%.3f" % s["z_llegada"], "%.3f" % s["cf_cuneta"], s["llega"].lower()]
                 for s in c.SM["sumideros"]]
        D.tabla("Sumideros y tubería a la cuneta", ["Sumidero", "Área (m²)", "Q (l/s)", "Cuneta", "Tubo 4\" (m)", "S (%)", "Llegada", "C.F. cuneta", "Estado"],
                filas, [1.7, 1.6, 1.4, 1.8, 1.7, 1.2, 1.7, 1.8, 2.6], tam=7.5)
    # ---------------------------------------------------------------- plataformas, estructuras de caida y tapa vehicular
    ES = getattr(c, "ES", None) or {}; TV = getattr(c, "TV", None); est = [e for e in ES.get("estructuras", []) if e.get("codigo")]
    niv = c.cfg.get("niveles", {}) or {}
    if niv.get("plataformas") or niv.get("rampas") or est:
        D.h(1, "Niveles por plataforma y estructuras de caída")
        filas = [[q.get("nombre", ""), "%.2f" % float(q["npt"]), "%.2f" % (float(q["npt"]) - float(q.get("rebaje", 0) or 0))] for q in niv.get("plataformas", [])]
        if filas:
            D.p("El terreno se resuelve en plataformas; en cada una el borde de la cuneta va al nivel de su piso terminado (o con el rebaje indicado). "
                "El agua va siempre de la plataforma alta a la baja, y en cada cambio de nivel se dispone una estructura según el desnivel:")
            D.tabla("Plataformas del proyecto", ["Plataforma", "NPT", "Borde de cuneta"], filas, [7, 3, 3.5])
        D.vinetas(["Hasta 0.15 m: la cuneta sigue continua y el desnivel se absorbe en la pendiente de los 3 m anteriores.",
                   "De 0.15 a 0.50 m: caída corta, escalón en el fondo con losa de fondo reforzada aguas abajo.",
                   "De 0.50 a 1.00 m: caja de caída de concreto armado con poza de disipación.",
                   "Más de 1.00 m (con muro de contención): la cuneta de arriba llega al ras hasta la cara del muro, lo atraviesa por un marco de "
                   "concreto armado y el agua cae vertical a una poza de disipación al pie del muro, de donde sigue la cuneta de abajo."])
        if est:
            D.p("Cada poza se dimensiona para la caída vertical: con q = Q/b y el número de caída D = q²/(g·hd³) se obtienen el alcance del chorro "
                "Ld = 4.30·hd·D^0.27, el colchón yp = 1.00·hd·D^0.22 y los tirantes conjugados del resalto y1 = 0.54·hd·D^0.425 e "
                "y2 = 1.66·hd·D^0.27; el largo de la poza es Ld + 6.9·(y2 − y1) y su profundidad cubre el tirante conjugado.")
            D.tabla("Estructuras en los cambios de nivel", ["Código", "Eje", "Prog.", "De → a", "Desnivel", "Caída de fondo", "Q (l/s)", "Poza L × prof.", "y2"],
                    [[e["codigo"], e["eje"], "%.2f" % e["progresiva"], "%s → %s" % (e["nivel_arriba"], e["nivel_abajo"]), "%.2f" % e["desnivel"],
                      "%.2f" % e["caida_fondo"], "%.1f" % e["Q_ls"], "%.2f × %.2f" % (e["L_poza"], e["prof_poza"]), "%.3f" % e["y2"]] for e in est],
                    [1.5, 1.5, 1.3, 4, 1.5, 1.7, 1.4, 2.2, 1.2], tam=7.5)
            normas.recuadro_word(D, "caida_vertical", "rangos_desnivel")
        if ES.get("avisos"): D.vinetas(ES["avisos"])
    if TV and any(t.get("L_vehicular", 0) > 0 for r in c.C["ramales"] for t in r["tramos"]):
        D.h(1, "Cunetas en estacionamientos: tapa vehicular")
        D.p("En los estacionamientos y accesos vehiculares la cuneta no lleva rejilla: va siempre tapada con una losa de concreto armado diseñada "
            "para el paso de camiones. " + TV["texto"])
        normas.recuadro_word(D, "carga_vehicular")
    # ---------------------------------------------------------------- perfil de flujo (paso estandar) y simulacion dinamica (SWMM)
    PF = getattr(c, "PF", None); SW = getattr(c, "SW", None)
    if PF and PF.get("ejes"):
        rs = PF["resumen"]
        D.h(1, "Perfil de flujo y comprobación dinámica")
        D.p("La verificación anterior usa el tirante normal de cada tramo. Para comprobar el nivel del agua real a lo largo de cada eje, con los "
            "remansos en las uniones, las caídas y los cambios de pendiente, se calcula el perfil de flujo gradualmente variado por el método del "
            "paso estándar, con el caudal de diseño de cada tramo y n = %.3f:" % PF["n"])
        D.formula("z₁ + y₁ + V₁²/2g = z₂ + y₂ + V₂²/2g + hf     hf = Δx · (Sf₁ + Sf₂)/2     Sf = (n · V / R^(2/3))²")
        D.vinetas(["Control aguas abajo: en una descarga libre por el cerco, el tirante crítico; en la unión con otra cuneta, el nivel del agua de "
                   "la cuneta que recibe (por eso se calculan primero los ejes que reciben).",
                   "Régimen subcrítico: de aguas abajo hacia aguas arriba; supercrítico: de aguas arriba hacia aguas abajo desde el tirante crítico. "
                   "En cada estación (cada 0.5 m) queda el de mayor fuerza específica; el paso de supercrítico a subcrítico es un resalto hidráulico.",
                   "En el borde de cada caída el tirante es el crítico (o el nivel de aguas abajo si la ahoga); la poza disipa la energía de la caída."])
        filas = [[e["eje"], mil(e["L"]), "%.3f" % e["y_max"], "%.3f" % e["BL_min"], "%.2f" % e["s_BL_min"], "%.2f" % e["V_max"],
                  "%.1f" % e["supercritico_m"], len(e["saltos"]), e["estado"].capitalize()] for e in PF["ejes"]]
        D.tabla("Perfil de flujo por eje (paso estándar)", ["Eje", "L (m)", "y máx. (m)", "BL mín. (m)", "en prog. (m)", "V máx. (m/s)",
                                                            "Supercrítico (m)", "Resaltos", "Estado"], filas, [1.6, 1.5, 1.6, 1.7, 1.8, 1.7, 2.0, 1.5, 2.2], tam=7.5)
        D.p("En toda la red el menor borde libre del perfil de flujo es %.3f m y la velocidad máxima es %.2f m/s; %d de %d ejes cumplen el borde "
            "libre mínimo de %.2f m con el nivel del agua real%s. El detalle de cada estación (tirante, velocidad, energía, número de Froude y "
            "balance de energía con fórmulas) está en la hoja «PERFIL DE FLUJO» de la memoria de cálculo." % (
                rs["BL_min"], rs["V_max"], rs["cumplen"], rs["ejes"], P["BL"],
                "" if not rs["observados"] else " (" + "; ".join("%s: %s, %.3f m en la progresiva %.2f" % (o["eje"], o["estado"].lower(), o["BL_min"], o["s"])
                                                                for o in rs["observados"]) + ")"))
        normas.recuadro_word(D, "paso_estandar")
        if SW:
            H = SW["hietograma"]
            D.p("Además, la red se entrega en un archivo de EPA SWMM 5 (RED_CUNETAS_SWMM.inp: %d puntos de la red, %d tramos de cuneta, %d áreas de "
                "aporte y %d descargas) "
                "para la comprobación con tránsito por onda dinámica y lluvia variable en el tiempo: %s (lámina total %.2f mm, intensidad pico "
                "%.2f mm/h). Las áreas verdes infiltran por el método de Horton; techos y pisos son impermeables." % (
                    SW["nudos"], SW["conductos"], SW["subcuencas"], SW["descargas"], H["metodo"], H["lamina_mm"], H["pico_mmh"]))
            Sm = SW.get("simulacion")
            if Sm:
                D.p("Resultado de la simulación con el motor de %s: error de continuidad de %.2f %% en la escorrentía y %.2f %% en el tránsito; "
                    "caudal pico en %s." % (Sm["motor"], Sm["continuidad_escorrentia_pct"] or 0, Sm["continuidad_transito_pct"] or 0,
                                            ", ".join("%s %.1f l/s" % (d["D"], d["Q_max_ls"]) for d in Sm["descargas"])))
                if Sm["rebalses"]:
                    D.p("Con el bloque más intenso del hietograma (%d min) rebalsan por un momento %d puntos de la red (%s), con un volumen total "
                        "de %.1f m³: la lluvia de %d min es más intensa que la del tiempo de concentración con la que se dimensionan los tramos "
                        "por el método racional. El proyectista evalúa si acepta ese rebalse breve o si aumenta la sección de esos tramos." % (
                            H["dt_min"], len(Sm["rebalses"]), ", ".join("%s (%.2f h)" % (r["nudo"], r["horas"]) for r in Sm["rebalses"][:8]),
                            Sm["volumen_rebalse_m3"], H["dt_min"]))
                else:
                    D.p("Ningún punto de la red rebalsa durante la tormenta de diseño.")
            normas.recuadro_word(D, "hietograma", "swmm")
    # ---------------------------------------------------------------- descargas y conclusiones
    D.h(1, "Descargas")
    D.p("Cada sector entrega por gravedad a través de un pase en el cimiento del cerco perimétrico; fuera del cerco no se construyen obras y el agua "
        "sigue por el terreno natural.")
    filas = [[d["D"], "%.3f" % d["cf"], "%.2f" % d["terreno"], d["estado"].capitalize(), ("%.2f m" % d["perfilado_max"]) if d.get("perfilado_max") else "-"]
             for d in c.V["descargas"]]
    D.tabla("Descargas de la red de cunetas", ["Descarga", "Cota de fondo", "Terreno exterior", "Estado", "Perfilado"], filas, [2, 2.5, 2.8, 5, 2.5], tam=8)
    D.h(1, "Conclusiones")
    con = []
    if c.Rh:
        con.append("La precipitación máxima en 24 horas de diseño es %.2f mm (T = %d años, distribución %s) y la intensidad de diseño para tc = %.0f minutos "
                   "es %.2f mm/h (Dick y Peschke)." % (c.Rh["P24"], c.Rh["T"], c.Rh["distribucion_nombre"], c.Rh["tc_min"], c.Rh["I"]))
    con += ["El coeficiente de escorrentía ponderado dentro del cerco es %.3f, sobre un área de aporte de %s m² (celdas de 1 m²)." % (hv["C"], mil(hv["A_total"], 0)),
            "Las cunetas de %s cumplen en todos los tramos con el caudal de diseño (máximo %.1f l/s), con borde libre mínimo de %.3f m y velocidad "
            "máxima de %.2f m/s." % (c.anchos(), c.Qmax, c.BLmin, c.Vmax),
            "Las %s funcionan por gravedad, sin obras fuera del cerco." % c.descargas()]
    if c.TT["montantes"]: con.append("Las montantes son todas de 4\" (%d unidades), en las esquinas de las edificaciones." % c.TT["metrado"]["montantes_und"])
    con.append("Las rejillas, canaletas y sumideros deben limpiarse antes y durante la temporada de lluvias.")
    D.vinetas(con)
    D.h(1, "Anexos")
    D.vinetas(["Lluvia de diseño (Excel): HIDROLOGIA.xlsx." if c.Rh else "Intensidad de diseño del proyecto.",
               "Dimensionamiento de las cunetas por sector y por tramo (Excel): DIMENSIONAMIENTO.xlsx.",
               "Canaletas, montantes y sumideros (Excel): CANALETAS_MONTANTES_Y_SUMIDEROS.xlsx.",
               "Planos de drenaje pluvial %s (PLANOS_CUNETAS.dxf)." % c.planos,
               "Normas, referencias y criterios del diseño (anexo siguiente y hoja NORMAS Y FUENTES de la memoria de cálculo)."], izq=True)
    normas.anexo_word(D)


# ============================================================================== MEMORIA DESCRIPTIVA
def descriptiva(D, c):
    P, hv, mem = c.P, c.hv, c.mem
    D.h(1, "Generalidades")
    D.h(2, "Nombre del proyecto")
    D.p(_cita(c.pr) + ".")
    if c.pr.get("entidad"):
        D.h(2, "Entidad")
        D.p(c.pr["entidad"] + ((" - " + c.pr["gerencia"]) if c.pr.get("gerencia") else "") + (". Modalidad de ejecución: %s." % mem["modalidad"] if mem.get("modalidad") else "."))
    if mem.get("antecedentes"):
        D.h(2, "Antecedentes"); D.p(mem["antecedentes"])
    D.h(2, "Objetivo")
    D.p("Captar y conducir por gravedad las aguas de lluvia de techos, veredas, patios y áreas libres hasta el terreno natural exterior, evitando "
        "empozamientos, el ingreso de agua a los ambientes y el deterioro de pisos y estructuras.")
    D.h(1, "Ubicación")
    _ubicacion(D, c)
    D.h(1, "Características del terreno")
    t = []
    if c.rep_t.get("z_min") is not None:
        t.append("El terreno, según las curvas de nivel del plano, va de %.2f a %.2f m s. n. m." % (c.rep_t["z_min"], c.rep_t["z_max"]))
    if c.niveles(): t.append("Niveles del proyecto: %s. El borde de las cunetas va al ras del piso, con junta asfáltica al mismo nivel." % "; ".join(c.niveles()))
    if mem.get("clima"): t.append(mem["clima"])
    D.p(" ".join(t) if t else "Ver planos de arquitectura y topografía del proyecto.")
    D.h(1, "Descripción del sistema de drenaje pluvial")
    D.h(2, "Criterios de diseño")
    if c.Rh:
        e = c.Rh["estacion"] or {}
        ll = ("estación %s%s, serie de precipitación máxima en 24 horas %d - %d (%d años), T = %d años, P24 = %.2f mm, I = %.2f mm/h con tc = %.0f min "
              "(ver memoria hidrológica)." % (e.get("nombre", ""), (" (%s, código %s)" % (e.get("entidad", ""), e["codigo"])) if e.get("codigo") else "",
                                              c.Rh["maximos"][0][0], c.Rh["maximos"][-1][0], c.Rh["analisis"]["n"], c.Rh["T"], c.Rh["P24"], c.Rh["I"], c.Rh["tc_min"]))
    else:
        ll = "I = %.2f mm/h (%s)." % (hv["I"], c.LL.get("fuente") or "dato del proyecto")
    crit = [("Lluvia de diseño: ", ll),
            ("Caudales: ", "método racional con coeficiente de escorrentía ponderado %.3f y factor de seguridad de %.2f." % (hv["C"], hv["FS"])),
            ("Sección de cuneta: ", "rectangular de concreto, %s, muros de %.2f m, losa de fondo de %.2f m sobre solado de %.2f m; una sola medida por sector de "
                                    "descarga; profundidad variable de %.2f m al inicio a %.2f m como máximo." % (c.anchos(), P["e_muro"], P["e_fondo"], P["e_solado"], P["h0"], c.hmax)),
            ("Pendiente: ", "cota de fondo con pendiente mínima de %.1f %%; el borde sigue el nivel del piso." % (100 * P["S0"])),
            ("Acero: ", "solo donde la profundidad (de la rejilla al fondo) es %.2f m o más y en los tramos tapados; con menor profundidad la cuneta abierta es de concreto simple." % P["h_acero"]),
            ("Quiebres: ", "a 45° en planta en cada cambio de dirección (chaflanes de %.2f m); los ejes que llegan entran en diagonal." % P["chaflan"]),
            ("Cubierta: ", "rejilla metálica móvil de platinas 1\" x 3/16\" con marco de ángulo 1\" x 1\" x 3/16\" en los tramos abiertos; losa tapa de %.2f m en cruces, "
                           "ingresos y pases por el cerco." % P["e_tapa"]),
            ("Tapas de inspección: ", "%.2f x %.2f m en los tramos tapados: al inicio y al final, en cada empalme y a %.0f m como máximo." % (P["tapa_lado"], P["tapa_lado"], P["tapa_sep_max"])),
            ("Juntas: ", "de dilatación de 1\" con sellador asfáltico en toda la sección en U cada 3.00 m, y junta asfáltica entre la cuneta y el piso adyacente.")]
    if c.LLt: crit.append(("Lloraderos: ", "PVC de 3\" @%.2f m con caja filtrante de 0.30 x 0.30 m de grava envuelta en geotextil, solo en el muro en contacto con área verde "
                                           "(reemplazan a los drenes franceses)." % P["llor_sep"]))
    if c.TT["montantes"]: crit.append(("Techos: ", "canaletas galvanizadas de 0.25 x 0.20 m al 1 % y montantes de PVC de 4\" en las esquinas de las edificaciones, en falsa columna."))
    if c.SM["sumideros"]: crit.append(("Sumideros: ", "solo en áreas libres sin cobertura, con tubería PVC de 4\" al 1 % (mínimo 0.5 %) hasta la cuneta más cercana."))
    D.vinetas(crit)
    D.h(2, "Red de cunetas")
    D.p("La red tiene %d ejes con %s m de cuneta, de los cuales %s m son tapados y %s m llevan rejilla. Todo el sistema queda dentro del cerco perimétrico "
        "y se organiza en %d sectores, cada uno con su descarga:" % (len(c.C["ramales"]), mil(c.L), mil(c.Ltap), mil(c.L - c.Ltap), len(c.sectores)))
    filas = [[k, ", ".join(g["ejes"]), mil(g["L"]), f2(g["b"]), f2(g["b"] + 2 * P["e_muro"])] for k, g in sorted(c.sectores.items())]
    D.tabla("Sectores de drenaje", ["Descarga", "Ejes", "Longitud (m)", "Ancho libre (m)", "Ancho total (m)"], filas, [2, 8, 2, 1.8, 1.8], tam=8)
    filas = [[s["eje"], s["sector"], mil(s["L_m"]), f2(s["b_adoptado"]), f2(s["h_min"]), f2(s["h_max"]), f2(s["excavacion_max"])] for s in c.sec]
    filas.append(["TOTAL", "", mil(sum(s["L_m"] for s in c.sec)), "", "", "", ""])
    D.tabla("Ejes de cuneta", ["Eje", "Descarga", "L (m)", "b libre (m)", "h mín. (m)", "h máx. (m)", "Excavación máx. (m)"], filas,
            [1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 2.6], tam=7.5, total=True)
    D.figura(c.fig.get("planta"), "Planta general de la red de cunetas.", 15.5)
    pl = [t for t in (getattr(c, "plan", None) or []) if t.get("decision") not in (None, "ya cubierto")]
    if pl:
        D.h(2, "Planteamiento de las cunetas de las edificaciones")
        D.p("Cada edificación y la losa deportiva descargan su techo por canaletas a montantes en las esquinas; de cada dado sale un tubo de 4\" que "
            "debe llegar a una cuneta a 5 m o menos. Por eso la cuneta puede ir a lo largo del alero o por los lados cortos del techo (transversal): "
            "para cada techo se probaron sus lados y sus combinaciones y se eligió la que deja todos sus montantes al alcance con menos cuneta nueva, "
            "aprovechando las cunetas vecinas; luego cada cuneta se prolongó en línea recta hacia las descargas hasta otra cuneta o el cerco. Menos "
            "cuneta larga significa menos profundidad y descargas que sí llegan por gravedad.")
        trad = {"a lo largo del alero": "a lo largo del alero", "transversal": "transversal (lados cortos)", "mixta": "mixta", "prolongaciones": "prolongaciones"}
        filas = [[t["techo"], str(t.get("montantes", "")), trad.get(t["decision"], t["decision"]), mil(t["nueva_m"]) if t.get("nueva_m") is not None else "",
                  "; ".join("%s: %s m" % (k, mil(v)) for k, v in sorted((t.get("opciones") or {}).items()))] for t in pl]
        D.tabla("Planteamiento por techo", ["Techo", "Montantes", "Opción elegida", "Cuneta nueva (m)", "Opciones comparadas (cuneta nueva)"], filas,
                [1.4, 1.7, 3.2, 2.2, 7.5], tam=7.5)
    D.h(2, "Descargas")
    D.p("Las descargas cruzan el cerco con un pase en su cimiento, en tramo tapado, y entregan el agua al terreno natural exterior por gravedad. Fuera del "
        "cerco no hay obras; solo se perfila el terreno al pie del cerco donde hace falta.")
    D.tabla("Descargas", ["Descarga", "Cota de fondo", "Terreno exterior", "Estado"],
            [[d["D"], "%.3f" % d["cf"], "%.2f" % d["terreno"], d["estado"].capitalize()] for d in c.V["descargas"]], [2.5, 3, 3, 7], tam=8)
    if c.LLt:
        D.h(2, "Lloraderos")
        n = sum(x["n"] for x in c.LLt)
        D.p("Se colocan %d lloraderos en %d tramos de muro en contacto con área verde (%s m de muro), a %.2f m entre sí. En el muro que da a vereda, patio "
            "o piso no se colocan." % (n, len(c.LLt), mil(sum(x["L_m"] for x in c.LLt)), P["llor_sep"]))
    if c.TT["montantes"]:
        m = c.TT["metrado"]
        D.h(2, "Canaletas y montantes")
        D.p("Las coberturas descargan por %s m de canaleta galvanizada de 0.25 x 0.20 m a %d montantes de PVC de 4\", ubicados en las esquinas de las "
            "edificaciones dentro de falsas columnas de 0.20 x 0.15 x 1.30 m; desde el dado de cada montante, un codo de 90° y tubería PVC de 4\" enterrada "
            "(%s m) entregan a la cuneta sobre su nivel de agua." % (mil(m["canaleta_m"]), m["montantes_und"], mil(m["tuberia_enterrada_m"])))
    if c.SM["sumideros"]:
        m = c.SM["metrado"]
        D.h(2, "Sumideros de piso")
        D.p("Se colocan %d sumideros en las áreas libres sin cobertura alejadas de las cunetas, con %s m de tubería PVC de 4\" hasta la cuneta más cercana." % (
            m["sumideros_und"], mil(m["tuberia_4_m"])))
    D.h(1, "Metas físicas")
    filas = []
    for x in c.metas:
        if x["und"] and x.get("total") is not None: filas.append([x["codigo"], x["desc"], x["und"], mil(x["total"])])
    if filas:
        D.tabla("Metas físicas (resumen del metrado)", ["Ítem", "Descripción", "Und.", "Cantidad"], filas, [2.2, 9.8, 1.3, 2.2], tam=7.5,
                fuente="METRADO_DRENAJE_PLUVIAL.xlsx.")
    else:
        D.p("Las cantidades de cada partida están en el metrado de la especialidad (METRADO_DRENAJE_PLUVIAL.xlsx, hoja RESUMEN).")
    D.h(1, "Normas técnicas")
    D.vinetas(NORMAS + list(mem.get("normas", [])))
    D.h(1, "Relación de planos")
    D.tabla("Planos de drenaje pluvial", ["Lámina", "Contenido"], [[x["codigo"], x["titulo"]] for x in c.lam], [2.5, 13], tam=8)


def generar(ruta, titulo, sub, fn, corto, c):
    D0 = word.Doc(c.pr, corto); fn(D0, c)                         # primera pasada: titulos para el contenido
    D = word.Doc(c.pr, corto); D.caratula(titulo, sub); D.contenido(D0.indice); fn(D, c)
    return D.guardar(ruta)


def escribir(salida, c):
    h = generar(os.path.join(salida, "MEMORIA_HIDROLOGICA_DRENAJE_PLUVIAL.docx"), "ESTUDIO HIDROLÓGICO Y DE DRENAJE PLUVIAL",
                "Memoria hidrológica - red de cunetas", hidrologica, "MEMORIA HIDROLÓGICA", c)
    d = generar(os.path.join(salida, "MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL.docx"), "MEMORIA DESCRIPTIVA", "Drenaje pluvial - red de cunetas",
                descriptiva, "MEMORIA DESCRIPTIVA", c)
    return h, d
