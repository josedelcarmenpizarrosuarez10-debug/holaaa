"""Especificaciones tecnicas de la especialidad de drenaje pluvial (tres expedientes).

Lee las partidas (codigo, descripcion, unidad) de la hoja RESUMEN del metrado vigente de cada proyecto y redacta
la especificacion de cada una con los datos constructivos del proyecto (planos y hojas de parametros del metrado).
No se agregan ni se quitan partidas: el orden, los codigos y las unidades son los del metrado.
Salida: un JSON por proyecto que docx_espec.js convierte en Word.
"""
import os, sys, json, re
import openpyxl, warnings

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
MET = os.path.join(RAIZ, "insumos", "metrados_vigentes")

# ============================================================================== datos de cada proyecto
CUNETA = dict(b=0.40, em=0.10, ef=0.10, et=0.10, be=0.60, solado="E = 4\" (0.10 m)", acero_long="3/8\" @0.20 a 0.25 m (segun tramo)",
              acero_tr="3/8\" en U @0.25 m", junta=3.00, tapa=(0.60, 0.60, 0.10), tapa_acero="parrilla simple de 3/8\" @0.15 m en ambos sentidos",
              dado=(0.40, 0.40, 0.35), fcol=(0.20, 0.15, 1.30),
              S=0.50, S_can=1.00, n_cun=0.015, n_can=0.013, rej_mod=1.00, rej_reb=0.05, sep_sop=0.60)
# Fuentes: tablas de pendiente de las cunetas en la planta general de drenaje (S = 0.5 %); memoria hidrologica de cada proyecto
# (canaletas S = 1.00 % con n = 0.013, cunetas S = 0.50 % con n = 0.015); detalles de rejilla, detalle 1, caja sumidero, abrazadera
# y falsa columna de los planos de drenaje pluvial; hoja METRADO CANALETAS (soportes @0.60 m) y METRADO MONTANTES (cantidades).

PROYECTOS = {
    "varones": dict(
        clave="varones", archivo="METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx", corto="CAR VARONES", cui="2705619",
        salida=os.path.join(RAIZ, "entregables_varones", "ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL_CAR_VARONES"),
        colector=dict(
            nombre="colector pluvial frontal del CAR Varones", L=105.29, b=0.60, em=0.15, ef=0.15, es=0.10, es_cam=0.25, solado=0.05,
            zanja=1.40, NPT=261.15, cf0=260.20, cf1=259.884, S=0.30, n_reg=11, juntas=4.00, n_juntas=26,
            tramos="cruce de camiones cisterna (0+000.00 a 0+006.08), tramo normal (0+006.08 a 0+100.90) y tramo de empalme horizontal con la caja CL (0+100.90 a 0+105.29)",
            acero="tramo normal: un marco cerrado de 3/8\" @0.20 m en el eje de muros y losas; cruce de camiones: doble marco de 1/2\" @0.15 m (marco exterior e interior); barras longitudinales de 3/8\" @0.25 m (@0.20 m en el cruce de camiones)",
            recub="0.04 m en muros y losa de fondo; 0.025 m en la losa superior del tramo normal; 0.04 m en el cruce de camiones; 0.025 m en tapas",
            receptor="la caja de llegada CL del colector del Hogar de Refugio Temporal (CUI 2675514), por la ventana de 0.60 x 1.17 m de su muro este",
            cajas=None, salida=None, cerco=False, planos="DP-01 a DP-08, DA-01 a DA-03 y DD-01 a DD-04"),
    ),
    "refugio": dict(
        clave="refugio", archivo="METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx", corto="HOGAR DE REFUGIO TEMPORAL", cui="2675514",
        salida=os.path.join(RAIZ, "entregables", "ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL_HOGAR_REFUGIO"),
        colector=dict(
            nombre="colector pluvial frontal del Hogar de Refugio Temporal", L=69.89, b=0.80, em=0.15, ef=0.15, es=0.10, es_cam=0.25, solado=0.05,
            zanja=1.60, NPT=260.60, cf0=259.10, cf1=258.89, S=0.30, n_reg=10, juntas=4.00, n_juntas=17,
            tramos="tramo normal, cruce de motos, cruce de camiones y tramo diagonal hasta la caja de caida CC",
            acero="tramo normal: un marco cerrado de 3/8\" @0.20 m; cruce de motos: marco de 3/8\" @0.15 m; cruce de camiones: doble marco de 1/2\" @0.15 m; barras longitudinales de 3/8\" @0.25 m (@0.20 m en el cruce de camiones); cajas CL y CC: malla de 3/8\" @0.20 m en ambas caras",
            recub="0.04 m en muros y losa de fondo; 0.025 m en la losa superior del tramo normal; 0.04 m en el cruce de camiones; 0.025 m en tapas",
            receptor="el registro R-01 del colector del CAR Mujeres (CUI 2717013), a traves de la caja de caida CC con poza de disipacion",
            cajas="caja de llegada CL (interior 1.50 x 1.00 m, poza de 0.30 m, recibe el colector del CAR Varones y su cuneta del Eje 01) y caja de caida CC (poza 3.50 x 1.50 m, profundidad 0.40 m bajo el fondo del receptor, umbral de 0.25 x 0.40 m)",
            salida=None, cerco=True, planos="DP-01 a DP-10, DA-01 a DA-03 y DD-01 a DD-04"),
    ),
    "mujeres": dict(
        clave="mujeres", archivo="METRADO_DRENAJE_PLUVIAL_CAR_MUJERES.xlsx", corto="CAR MUJERES", cui="2717013",
        salida=os.path.join(RAIZ, "entregables_mujeres", "ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL_CAR_MUJERES"),
        colector=dict(
            nombre="colector pluvial frontal del CAR Mujeres", L=139.08, b=1.50, em=0.10, ef=0.10, es=0.10, es_cam=0.20, solado=0.05,
            zanja=1.80, NPT=259.25, cf0=258.72, cf1=258.30, S=0.30, n_reg=15, juntas=4.00, n_juntas=33,
            tramos="tramo en vereda (0+000.00 a 0+078.42, losa superior al nivel de la vereda +259.25), cruces vehiculares de autos y de camiones, y tramo final de altura interior 0.60 m hasta la estructura de salida (0+139.08)",
            acero="tramo en vereda y tramo final: marco de 3/8\" @0.20 m; cruces de autos: marco de 3/8\" @0.15 m; cruce de camiones (muros 0.15 m, losas 0.20 m): marcos dobles de 1/2\" @0.15 m; barras longitudinales de 3/8\" @0.25 m (@0.20 m en el cruce de camiones), barras de 9.00 m con traslape de 0.40 m",
            recub="malla centrada en los elementos de 0.10 m; 0.045 m al eje en el cruce de camiones; 0.025 m en tapas",
            receptor="la estructura de salida con dos aleros a 45 grados, uña de concreto ciclopeo y emboquillado de piedra (0+139.08)",
            cajas=None, salida=True, cerco=False, planos="DP-01 a DP-10"),
    ),
}
ENTIDAD = "GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO"
UBICACION = "Distrito de Morales, provincia y departamento de San Martin"
ESPECIALIDAD = "INSTALACIONES SANITARIAS - DRENAJE PLUVIAL"


# ============================================================================== lectura del metrado
def partidas(P):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(os.path.join(MET, P["archivo"]), data_only=True)
    ws = wb["RESUMEN"]
    out = []; proyecto = None
    for r in ws.iter_rows(values_only=True):
        if r[0] == "PROYECTO": proyecto = str(r[1]).strip().strip("“”\"")
        c = str(r[0]).strip() if r[0] is not None else ""
        if re.match(r"^\d+(\.\d+)+$", c):
            und = (str(r[2]).strip() if r[2] else "")
            if und.lower() in ("kgr", "kg."): und = "kg"
            out.append(dict(codigo=c, desc=str(r[1]).strip(), und=und, cant=r[3]))
    P["proyecto"] = proyecto
    return out


# ============================================================================== texto comun
def p(t): return ["p", t]
def l(*items): return ["l", list(items)]
def t(cab, filas): return ["t", cab, filas]

UND_TXT = {"m²": "metro cuadrado (m²)", "m³": "metro cubico (m³)", "m": "metro lineal (m)", "ml": "metro lineal (ml)", "kg": "kilogramo (kg)", "und": "unidad (und)"}


def pago(und):
    u = UND_TXT.get(und, und)
    return [p("El pago se efectuara al precio unitario del presupuesto por %s, de acuerdo con el avance valorizado y con la conformidad de la "
              "Supervision. Dicho precio y pago constituye compensacion total por la mano de obra (incluidas las leyes sociales), los materiales, "
              "el equipo, las herramientas, el transporte interno y todo imprevisto necesario para ejecutar la partida segun esta especificacion y los planos." % u)]


def bloque(desc, mat=None, equ=None, proc=None, ctrl=None, seg=None, und=None, medicion=None, extra=None):
    """Especificacion de una partida en apartados ordenados."""
    norm = lambda x: [x] if (x and isinstance(x[0], str)) else x      # un solo bloque ["p"/"l"/"t", ...] -> lista de bloques
    desc, mat, equ, proc, ctrl, seg, medicion = map(lambda x: norm(x) if x else x, (desc, mat, equ, proc, ctrl, seg, medicion))
    s = [["DESCRIPCION", desc]]
    if mat: s.append(["MATERIALES", mat])
    if equ: s.append(["EQUIPOS Y HERRAMIENTAS", equ])
    if proc: s.append(["PROCEDIMIENTO DE EJECUCION", proc])
    if ctrl: s.append(["CONTROL DE CALIDAD Y TOLERANCIAS", ctrl])
    if seg: s.append(["SEGURIDAD Y SALUD EN EL TRABAJO", seg])
    if extra: s += extra
    s.append(["UNIDAD DE MEDIDA", [p("La unidad de medida es: %s." % UND_TXT.get(und, und))]])
    s.append(["METODO DE MEDICION", medicion])
    s.append(["FORMA DE PAGO", pago(und)])
    return s


EPP = "Uso obligatorio de equipo de proteccion personal: casco, lentes de seguridad, guantes, botas con puntera de acero y chaleco reflectivo (DS N.° 011-2019-TR y Norma G.050)."
SEG_EXC = l(EPP, "Delimitar y senalizar la zona de trabajo con cinta y conos; colocar pasarelas sobre las zanjas en los accesos peatonales.",
            "Dejar el material excavado a no menos de 0.60 m del borde de la zanja. Entibar las paredes cuando la profundidad supere 1.50 m o el suelo lo requiera (Norma G.050).",
            "Antes de excavar, verificar la existencia de redes enterradas (agua, desague, electricidad) y protegerlas.")
SEG_CONC = l(EPP, "Proteccion de manos y piel contra el cemento (guantes de jebe y ropa de manga larga); lavado inmediato en caso de contacto.",
             "La mezcladora y el vibrador seran operados solo por personal capacitado; conexiones electricas con tablero, interruptor diferencial y puesta a tierra.")
SEG_ACERO = l(EPP, "Guantes de cuero para el manipuleo de varillas; proteger los extremos de las barras en espera con capuchones o dobleces.",
              "El corte y doblado se hara en una zona habilitada, fuera de la circulacion del personal.")
SEG_SOLD = l(EPP, "Careta de soldar con filtro adecuado, guantes y mandil de cuero; pantallas que protejan al personal vecino.",
             "Equipo de soldar con puesta a tierra; extintor de PQS a la mano; prohibido soldar cerca de materiales inflamables.")


# ============================================================================== capitulo de generalidades
def generalidades(P, partidas_):
    C = P["colector"]
    cap = []
    cap.append(["GENERALIDADES", [
        p("Las presentes especificaciones tecnicas definen la calidad de los materiales, los procedimientos de ejecucion, los controles, la "
          "seguridad, la unidad de medida, el metodo de medicion y la forma de pago de cada partida de la especialidad de drenaje pluvial del "
          "proyecto %s, con CUI N.° %s." % (P["proyecto"], P["cui"])),
        p("Comprenden el sistema de drenaje pluvial del predio (cunetas de concreto armado con rejillas y tapas, montantes y canaletas de techo, "
          "red de recoleccion de piso con sumideros) y el %s, que recorre el frente del predio y entrega a %s." % (C["nombre"], C["receptor"])),
        p("Su numeracion, la descripcion y la unidad de cada partida son las del metrado de la especialidad (hoja RESUMEN). Los planos de la especialidad, la "
          "memoria de calculo y el metrado forman parte de este documento."),
    ]])
    cap.append(["UBICACION", [p("Entidad: %s. Ubicacion: %s, region San Martin." % (ENTIDAD.title(), UBICACION)),
                              p("Clima calido y lluvioso: el vaciado de concreto y el curado se programaran considerando la temperatura ambiente y las lluvias (ACI 305R).")]])
    cap.append(["NORMAS APLICABLES", [
        p("En todo lo no previsto en estas especificaciones rigen, en su version vigente:"),
        l("Reglamento Nacional de Edificaciones (RNE): Norma OS.060 Drenaje Pluvial Urbano; Norma CE.040 Drenaje Pluvial; Norma IS.010 Instalaciones Sanitarias para Edificaciones.",
          "RNE: Norma E.020 Cargas; Norma E.050 Suelos y Cimentaciones; Norma E.060 Concreto Armado; Norma E.090 Estructuras Metalicas.",
          "RNE: Norma G.050 Seguridad durante la Construccion y DS N.° 011-2019-TR, Reglamento de Seguridad y Salud en el Trabajo para el Sector Construccion.",
          "Norma Tecnica de Metrados para Obras de Edificacion y Habilitaciones Urbanas (RD N.° 073-2010/VIVIENDA/VMCS-DNC).",
          "Normas Tecnicas Peruanas: NTP 334.009 (cemento Portland), NTP 400.037 (agregados para concreto), NTP 339.088 (agua de mezcla), NTP 341.031 (barras de acero corrugado), NTP 339.036 (muestreo del concreto fresco), NTP 339.035 (asentamiento con el cono de Abrams), NTP 339.033 (elaboracion y curado de probetas en obra), NTP 339.034 (resistencia a la compresion), NTP 339.141 (Proctor modificado), NTP 339.143 (densidad de campo por el cono de arena), NTP 399.003 (tubos de PVC-U para desague).",
          "Normas ASTM de referencia: A615 grado 60 (acero corrugado), A36 (perfiles y platinas), A653 y A123 (galvanizado), C920 (selladores elastomericos), D2564 (cemento solvente para PVC); AWS D1.1 y A5.1 (soldadura).",
          "American Concrete Institute: ACI 318, ACI 301, ACI 304R (dosificacion, mezclado y colocacion), ACI 305R (concreto en clima calido), ACI 308R (curado), ACI 347 (encofrados)."),
        p("Si hubiera discrepancia entre documentos, prevalecen en este orden: planos, especificaciones tecnicas, memoria de calculo y metrado; las "
          "discrepancias se anotaran en el cuaderno de obra y las resolvera la Supervision."),
    ]])
    cap.append(["MATERIALES", [
        p("Todos los materiales seran nuevos, de primera calidad y con certificado de calidad del fabricante o del laboratorio. La Supervision "
          "aprobara las muestras antes de su uso y podra rechazar el material que no cumpla."),
        t(["MATERIAL", "REQUISITO", "NORMA"], [
            ["Cemento", "Portland tipo I (tipo MS o V si el estudio de suelos indica sulfatos); almacenado sobre tarimas, en pilas de no mas de 10 bolsas, bajo techo, usado en orden de llegada; no se usara cemento endurecido", "NTP 334.009"],
            ["Agregado fino", "Arena gruesa limpia, de granulometria continua, libre de arcilla, limo, sales y materia organica", "NTP 400.037"],
            ["Agregado grueso", "Piedra chancada de 1/2\" a 3/4\", dura y limpia; tamano maximo no mayor de 1/5 de la menor dimension del elemento ni de 3/4 del espacio libre entre barras", "NTP 400.037"],
            ["Agua", "Potable o que cumpla la norma; prohibida el agua de acequia sin analisis", "NTP 339.088"],
            ["Acero de refuerzo", "Barras corrugadas grado 60, fy = 4200 kg/cm²; limpias, sin oxido suelto, aceite ni pintura; almacenadas sobre durmientes y bajo techo", "NTP 341.031 / ASTM A615"],
            ["Perfiles y platinas", "Acero estructural A36; galvanizado en caliente cuando se indique F°G°", "ASTM A36 / A123"],
            ["Tuberia y accesorios", "PVC-U para desague, clase pesada (CP), con union espiga-campana y cemento solvente", "NTP 399.003 / ASTM D2564"],
            ["Plancha galvanizada", "Acero galvanizado de 0.9 mm de espesor, recubrimiento de zinc continuo, sin oxidacion", "ASTM A653"],
            ["Juntas", "Poliestireno expandido (tecnopor) de 1\"; sellador asfaltico para juntas de cunetas; sellador de poliuretano en el colector", "ASTM C920"],
        ]),
    ]])
    cap.append(["CONCRETO", [
        p("Calidades: f'c = 100 kg/cm² (solado), 140 kg/cm² (dados y concreto ciclopeo), 175 kg/cm² (cunetas y falsas columnas) y 210 kg/cm² (colector, "
          "estructuras de llegada o salida y tapas). La resistencia corresponde a 28 dias."),
        l("Dosificacion: el Contratista presentara el diseno de mezcla de un laboratorio con los agregados de obra (ACI 211.1); la resistencia promedio requerida sera la de la Norma E.060, 5.3. La dosificacion se hara en peso o en volumen con cajones calibrados aprobados.",
          "Asentamiento (slump): 3\" a 4\" para elementos armados; 2\" a 3\" para solado y concreto simple (NTP 339.035).",
          "Mezclado: con mezcladora mecanica, no menos de 1.5 minutos desde que todos los materiales estan en el tambor; no se permite el mezclado a mano ni el reamasado de concreto que inicio su fragua.",
          "Transporte y colocacion: el concreto se colocara antes de 45 minutos de su mezclado, desde una altura de caida no mayor de 1.50 m, en capas de 0.30 m como maximo, sin segregacion (ACI 304R).",
          "Compactacion: con vibrador de inmersion, introducido verticalmente a distancias de 0.40 a 0.50 m y por 5 a 15 segundos, sin tocar el acero ni el encofrado.",
          "Juntas de construccion: solo donde indiquen los planos o apruebe la Supervision; la superficie se picara, limpiara y humedecera antes del siguiente vaciado.",
          "Clima calido: temperatura del concreto no mayor de 32 °C al colocarlo; humedecer encofrados y bases, proteger del sol y del viento, vaciar en horas de menor temperatura (ACI 305R). Lluvia: suspender el vaciado o cubrir el concreto fresco.",
          "Curado: iniciarlo apenas el concreto endurezca lo suficiente, manteniendolo humedo por 7 dias como minimo (ACI 308R); ver las partidas de curado."),
    ]])
    cap.append(["ENCOFRADOS", [
        l("Seran de madera tornillo o de paneles metalicos o fenolicos, con resistencia y rigidez para soportar el concreto fresco y la vibracion sin deformarse (ACI 347).",
          "Se armaran a las dimensiones de los planos, alineados, aplomados y estancos; las caras en contacto con el concreto se limpiaran y cubriran con desmoldante que no manche.",
          "Tolerancias: desplome de 6 mm en 3.00 m; variacion de dimensiones de la seccion de -6 mm a +12 mm.",
          "Desencofrado sin golpes que danen el concreto: costados de muros, cunetas y falsas columnas a las 24 horas como minimo; fondos de losas (losa superior del colector y tapas) a los 7 dias, o antes con ensayos que demuestren el 70 % de f'c."),
    ]])
    cap.append(["ACERO DE REFUERZO", [
        l("El corte y doblado se hara en frio, a las dimensiones del cuadro de doblado de los planos; no se enderezaran ni volveran a doblar barras.",
          "Ganchos estandar y diametros de doblado segun la Norma E.060, capitulo 7; ganchos de cierre de los marcos de 0.15 m a cada lado (0.30 m por marco).",
          "Traslapes alternados: 0.40 m para 3/8\" y 0.50 m para 1/2\" (E.060, 12.15); no se traslapara mas del 50 % de las barras en una misma seccion.",
          "Recubrimientos libres (E.060, 7.7): los indicados en los planos; se asegurarán con dados de concreto o separadores, nunca con piedras o madera.",
          "Las barras se amarraran con alambre negro N.° 16 en todos los cruces de los bordes y en forma alternada en el interior; antes del vaciado la Supervision verificara diametro, numero, espaciamiento, traslapes y recubrimientos."),
    ]])
    cap.append(["CONTROL DE CALIDAD Y ENSAYOS", [
        p("El Contratista contratara un laboratorio acreditado y entregara los resultados a la Supervision. Frecuencias minimas:"),
        t(["ENSAYO", "FRECUENCIA", "CRITERIO DE ACEPTACION"], [
            ["Asentamiento del concreto (NTP 339.035)", "Cada tanda que se muestree y cuando la Supervision lo pida", "Dentro del rango de la especificacion"],
            ["Probetas de concreto (NTP 339.033 y 339.034)", "Por cada clase de concreto: no menos de una muestra al dia, una por cada 50 m³ y una por cada 300 m² de losas o muros; cada ensayo es el promedio de 2 probetas a 28 dias (E.060, 5.6.2)", "Promedio de 3 ensayos consecutivos >= f'c y ningun ensayo < f'c - 35 kg/cm² (E.060, 5.6.3.3)"],
            ["Proctor modificado (NTP 339.141)", "Una vez por cada tipo de material de relleno", "Curva de compactacion de referencia"],
            ["Densidad de campo (NTP 339.143)", "Una por cada capa y cada 50 m de zanja, como minimo", ">= 95 % de la maxima densidad seca del Proctor modificado"],
            ["Acero de refuerzo", "Certificado de calidad por lote; ensayo de traccion si la Supervision lo pide", "NTP 341.031"],
            ["Prueba hidraulica de tuberias", "Cada tramo de la red de piso antes del relleno", "Sin fugas durante 15 minutos"],
        ]),
        p("Si el concreto no cumple, la Supervision podra ordenar ensayos de diamantina (E.060, 5.6.5); la demolicion y reposicion del elemento seran a cuenta del Contratista."),
    ]])
    cap.append(["SEGURIDAD, SALUD Y MEDIO AMBIENTE", [
        l("El Contratista aplicara el Plan de Seguridad y Salud en el Trabajo de la obra (DS N.° 011-2019-TR, Norma G.050): induccion, charla diaria de 5 minutos, analisis de trabajo seguro (ATS) y permisos de trabajo de riesgo (excavaciones, trabajos en altura, en caliente).",
          "Equipo de proteccion personal obligatorio para todo el personal. Botiquin, extintores y senalizacion en los frentes de trabajo.",
          "Las excavaciones abiertas se senalizaran y cercaran; los trabajos en altura (canaletas y montantes) se haran con andamios certificados y arnes de cuerpo entero con linea de vida.",
          "El material excedente se eliminara a botaderos autorizados; prohibido arrojar residuos o lechadas de cemento a cunetas, quebradas o al terreno. Riego para controlar el polvo."),
    ]])
    cap.append(["MEDICION Y PAGO", [
        p("Los trabajos se mediran segun la Norma Tecnica de Metrados, en la unidad de cada partida, sobre lo realmente ejecutado y aprobado, y hasta el metrado del "
          "expediente salvo modificacion aprobada. No se pagaran trabajos rechazados, sobreexcavaciones ni excesos no autorizados."),
        p("El cuaderno de obra registrara las aprobaciones de trazo, fondos de excavacion, acero y encofrado antes de cada vaciado, y los resultados de los ensayos."),
    ]])
    return cap


# ============================================================================== especificaciones por tipo de partida
def es_titulo(pt):
    return not pt["und"]


def espec(pt, P, ctx):
    d = pt["desc"].upper(); und = pt["und"]; C = P["colector"]; K = CUNETA
    col = ctx["colector"]          # True dentro del capitulo del colector
    zona = C["nombre"] if col else "las cunetas, dados y obras de la red de drenaje pluvial del predio"
    # ------------------------------------------------------------ trabajos preliminares
    if "LIMPIEZA" in d:
        return bloque([p("Comprende la eliminacion de la vegetacion, raices, basura, desmonte y todo material suelto de la franja donde se construiran %s, hasta una profundidad de 0.10 m, para dejar el terreno listo para el trazo." % zona)],
                      equ=l("Herramientas manuales: pico, lampa, rastrillo, machete, carretilla."),
                      proc=l("Delimitar la franja de trabajo segun los planos.", "Cortar y retirar la vegetacion con sus raices; retirar piedras, basura y desmonte.",
                             "Acumular el material en un punto autorizado para su eliminacion, sin obstruir el transito ni las cunetas existentes."),
                      ctrl=l("La Supervision verificara que la franja quede libre de material organico y de desechos antes de aprobar el trazo."),
                      seg=l(EPP, "Senalizar la zona; cuidado con insectos y animales al retirar la vegetacion."), und=und,
                      medicion=[p("Se medira el area efectivamente limpiada en proyeccion horizontal, igual a la del trazo de la partida (largo por ancho de la franja de cada eje).")])
    if "TRAZO" in d:
        return bloque([p("Comprende el replanteo en el terreno de los ejes, alineamientos, anchos, progresivas y niveles de %s segun los planos de planta y perfil, y su control durante la obra. "
                         "Las cotas de fondo se referiran a los BM del proyecto." % zona)],
                      mat=l("Yeso o cal para el marcado, estacas de madera, clavos, pintura esmalte, hilo de nylon."),
                      equ=l("Estacion total o teodolito y nivel de ingeniero con su mira, wincha metalica de 50 m, jalones y plomadas."),
                      proc=l("Ubicar y monumentar los BM y puntos de control fuera de la zona de excavacion.",
                             "Marcar los ejes y bordes de la excavacion con estacas cada 5.00 m en recta y cada 2.00 m en curvas y quiebres, y en cada registro, cuneta que llega, cambio de seccion y extremo.",
                             ("Colocar niveletas de madera con la cota de fondo y la pendiente de diseno (%.2f %% en el colector); verificar las cotas de fondo de cada tramo." % C["S"]) if col else
                             ("Colocar niveletas de madera con la cota de fondo y la pendiente longitudinal de las cunetas (%.2f %%, segun las tablas de pendiente de la planta de drenaje); verificar las cotas de fondo de cada tramo." % K["S"]),
                             "El trazo sera aprobado por la Supervision y anotado en el cuaderno de obra antes de iniciar la excavacion."),
                      ctrl=l("Tolerancias: 0.02 m en alineamiento y 0.01 m en las cotas de fondo; la pendiente no cambiara de sentido en ningun tramo." +
                             ("" if col else " Se verificara por control topografico que las cunetas mantengan la pendiente minima de %.2f %% y las canaletas de techo la de %.2f %% (memoria hidrologica), sin contrapendientes ni depresiones." % (K["S"], K["S_can"]))),
                      seg=l(EPP, "Trabajar con chaleco reflectivo y senalizacion cuando el trazo este junto a la via."), und=und,
                      medicion=[p("Se medira el area replanteada en proyeccion horizontal: largo de cada eje por el ancho de la franja de trabajo indicada en el metrado.")])
    # ------------------------------------------------------------ movimiento de tierras
    if "EXCAVA" in d:
        if "DADO" in d:
            dsc = "Comprende la excavacion manual de los hoyos para los dados de concreto de %.2f x %.2f x %.2f m de la base de los montantes, en la ubicacion de los planos." % K["dado"]
        elif col:
            dsc = ("Comprende la excavacion manual de la zanja del %s, de %.2f m de ancho (%.2f m del colector mas 0.25 m a cada lado para el encofrado y el trabajo), desde el terreno existente "
                   "hasta el fondo del solado, segun el perfil longitudinal (cota de fondo %.3f en el inicio y %.3f al final, pendiente %.2f %%)." % (C["nombre"], C["zanja"], C["b"] + 2 * C["em"], C["cf0"], C["cf1"], C["S"]))
        else:
            dsc = ("Comprende la excavacion manual de las zanjas para las cunetas de concreto armado (ancho interior %.2f m, muros y losa de %.2f m, ancho exterior %.2f m) hasta el fondo del solado, "
                   "con la profundidad que resulta del perfil de cada eje." % (K["b"], K["em"], K["be"]))
        if "DADO" in d:
            return bloque([p(dsc)], equ=l("Pico, lampa, barreta, posteadora, wincha."),
                          proc=l("Ubicar cada dado al pie de su montante segun los planos de arquitectura y de la especialidad.",
                                 "Excavar el hoyo a las dimensiones del dado, con paredes verticales y fondo plano y compactado.",
                                 "Retirar el material suelto; el fondo sera aprobado por la Supervision antes del vaciado."),
                          ctrl=l("Dimensiones -0.00 / +0.03 m; fondo firme."), seg=l(EPP, "Tapar o senalizar los hoyos abiertos."), und=und,
                          medicion=[p("Se medira el volumen excavado: largo por ancho por profundidad de cada dado (%.2f x %.2f x %.2f m) por el numero de dados." % K["dado"])])
        return bloque([p(dsc), p("Incluye el perfilado de las paredes y el acarreo del material excavado a la zona de acopio dentro de la obra.")],
                      equ=l("Pico, lampa, barreta, carretilla, nivel y wincha; bomba de achique si aparece agua."),
                      proc=l("Excavar por tramos, de aguas abajo hacia aguas arriba, siguiendo las niveletas del trazo; no excavar mas tramo del que se pueda vaciar en la semana.",
                             "Las paredes quedaran verticales y el fondo plano y con la pendiente de diseno; los ultimos 0.10 m se excavaran justo antes del refine para no alterar el suelo.",
                             "Si el fondo presenta suelo blando, organico o con agua, se comunicara a la Supervision, que ordenara el reemplazo con material seleccionado o solado adicional.",
                             "La sobreexcavacion no autorizada se rellenara con concreto f'c=100 kg/cm² a cuenta del Contratista.",
                             "Mantener la zanja seca con bombeo y proteger de la lluvia; no dejar zanjas abiertas en dias de lluvia sin proteccion."),
                      ctrl=l("La Supervision aprobara el fondo de la excavacion (dimensiones, cota y tipo de suelo) antes del solado; tolerancia de la cota de fondo +0.00 / -0.03 m."),
                      seg=SEG_EXC, und=und,
                      medicion=[p("Se medira el volumen excavado en su posicion original (sin esponjamiento): area de la seccion de excavacion de los planos por la longitud de cada tramo, con la profundidad promedio del perfil.")])
    if "REFINE" in d:
        return bloque([p("Comprende el refine de las paredes y el fondo de la excavacion, su nivelacion a la cota del proyecto y la compactacion del fondo, para recibir el solado de %s." % zona)],
                      mat=l("Agua para el humedecimiento."), equ=l("Plancha compactadora o pison manual, nivel, regla, lampa."),
                      proc=l("Retirar el material suelto del fondo y de las paredes; perfilar a las dimensiones de los planos.",
                             "Humedecer el fondo hasta el contenido optimo y compactar con plancha vibratoria o pison hasta lograr una superficie firme y uniforme.",
                             "Verificar las cotas de fondo y la pendiente con nivel cada 5.00 m."),
                      ctrl=l("Fondo firme, sin material suelto ni charcos; tolerancia de nivel ±0.01 m."), seg=l(EPP, "Cuidado con la plancha compactadora (proteccion auditiva)."), und=und,
                      medicion=[p("Se medira el area del fondo refinado y compactado: ancho del solado por la longitud de cada tramo.")])
    if "RELLENO" in d:
        extra = (" Incluye el relleno lateral entre los muros del colector y las paredes de la zanja y la nivelacion de la franja adyacente hasta el nivel del piso (+%.2f)." % C["NPT"]) if col else " Comprende el relleno lateral de las cunetas entre sus muros y las paredes de la zanja."
        return bloque([p("Comprende el relleno compactado con material propio seleccionado, proveniente de la excavacion, libre de piedras mayores de 3\", raices, materia organica y basura." + extra)],
                      mat=l("Material propio seleccionado (zarandeado si fuese necesario); agua."), equ=l("Plancha compactadora o pison manual, carretilla, lampa, zaranda."),
                      proc=l("Iniciar el relleno solo cuando el concreto tenga al menos 7 dias y la Supervision lo autorice; en el colector, despues de la prueba de la losa superior.",
                             "Colocar el material en capas de 0.15 m de espesor suelto, humedecidas al contenido optimo de humedad.",
                             "Compactar cada capa a ambos lados del elemento a la vez, para no empujar los muros, hasta el 95 % de la maxima densidad seca del Proctor modificado.",
                             "La ultima capa quedara al nivel del piso terminado o del terreno, con bombeo hacia la cuneta o el colector."),
                      ctrl=l("Densidad de campo en cada capa (NTP 339.143); no se colocara la siguiente capa hasta que la anterior este aprobada."), seg=SEG_EXC, und=und,
                      medicion=[p("Se medira el volumen compactado en su posicion final: volumen de la excavacion menos el volumen ocupado por el elemento y el solado, segun el metrado.")])
    if "ELIMINACI" in d:
        return bloque([p("Comprende el carguio, transporte y descarga en un botadero autorizado del material excedente de las excavaciones, despues de descontar el material usado en el relleno, "
                         "y del desmonte de la limpieza.%s" % (" Distancia de transporte menor de 1 km." if "1KM" in d.replace(" ", "") or "D<1" in d.replace(" ", "") else ""))],
                      equ=l("Carretillas, lampas; volquete y cargador o carguio manual segun el volumen."),
                      proc=l("Acumular el excedente en puntos que no obstruyan el transito.", "Cargar y transportar al botadero autorizado por la Municipalidad; cubrir la tolva con lona.",
                             "Dejar la zona limpia al terminar cada tramo."),
                      ctrl=l("La Supervision verificara los viajes con vales firmados y que no queden acopios en la obra."), seg=l(EPP, "Senalizacion y vigia durante las maniobras del volquete."), und=und,
                      medicion=[p("Se medira el volumen excedente esponjado: (volumen excavado - volumen de relleno) por el factor de esponjamiento del metrado (1.20 para el sistema de cunetas; el del metrado del colector).")])
    # ------------------------------------------------------------ registros del colector
    if "TAPA DE REGISTRO" in d or ("TAPA DE CONCRETO" in d and und == "und"):
        comp = "TAPA DE REGISTRO" in d
        desc_ = ("Comprende el registro de limpieza completo del %s: contramarco de angulo L 2\" x 2\" x 3/16\" de 0.70 x 0.70 m con 8 anclajes de 3/8\" embutido en la abertura de la losa, "
                 "borde engrosado de 0.15 x 0.10 m bajo la losa con refuerzo de 2 barras de 1/2\" por lado, y tapa de concreto armado f'c = 210 kg/cm² de 0.68 x 0.68 x 0.08 m con marco de angulo "
                 "L 1 1/2\" x 1 1/2\" x 1/8\", parrilla de 7 + 7 barras de 3/8\" @0.10 m y dos asas de 3/8\" liso, todo segun la lamina DP-06B." % C["nombre"]) if comp else \
                ("Comprende la tapa de concreto armado f'c = 210 kg/cm² de 0.68 x 0.68 x 0.08 m de cada registro de limpieza del %s, vaciada dentro de su marco metalico, con parrilla de 7 + 7 barras de 3/8\" @0.10 m y dos asas de 3/8\" liso embutidas en cajuelas." % C["nombre"])
        return bloque([p(desc_), p("Numero de registros: %d, en la losa superior del colector%s." % (C["n_reg"], " y en las cajas" if C["cajas"] else ""))],
                      mat=l("Angulos A36; concreto f'c = 210 kg/cm²; acero corrugado grado 60 de 3/8\" y 1/2\"; acero liso de 3/8\"; soldadura E6011; pintura anticorrosiva y esmalte."),
                      equ=l("Maquina de soldar, amoladora, mezcladora o mezclado en batea, vibrador, herramientas de carpinteria."),
                      proc=l("Fabricar el contramarco y colocarlo con el encofrado de la losa, nivelado, con su ala a 0.08 m bajo el piso terminado, amarrado al refuerzo de borde." if comp else "Verificar el contramarco ya colocado en la losa.",
                             "Fabricar el marco de la tapa y soldar a el la parrilla; colocar las asas en sus cajuelas (molde de 0.18 x 0.06 x 0.03 m) para que no sobresalgan.",
                             "Vaciar la tapa sobre un tablero plano, vibrar y frotachar; curar 7 dias.", "Pintar los angulos con dos manos de anticorrosivo y dos de esmalte.",
                             "Colocar la tapa sobre el contramarco con holgura de 1 cm por lado; debe asentar en todo su perimetro, al ras del piso, y retirarse con dos operarios usando las asas."),
                      ctrl=l("Medidas ±2 mm; tapa sin cojeo ni fisuras; ras con el piso ±3 mm."), seg=SEG_SOLD, und=und,
                      medicion=[p("Se contara el numero de registros (tapas con su marco y contramarco) terminados y aprobados." if comp else "Se contara el numero de tapas fabricadas y colocadas.")])
    if "CONTRAMARCO" in d and und == "und":
        return bloque([p("Comprende la fabricacion y colocacion del contramarco de angulo de acero L 2\" x 2\" x 3/16\" de cada registro de limpieza, de 0.70 x 0.70 m de medida exterior, con 8 anclajes de 3/8\" de 0.20 m soldados (2 por lado), embutido en el borde de la abertura de la losa superior; su ala horizontal queda 0.08 m bajo el piso terminado y sirve de asiento a la tapa.")],
                      mat=l("Angulo A36 L 2\" x 2\" x 3/16\" (4 piezas de 0.71 m con extremos a 45 grados); varillas de 3/8\" para anclajes; soldadura E6011 de 1/8\"; pintura anticorrosiva y esmalte."),
                      equ=l("Maquina de soldar de 250 A, amoladora, escuadra, nivel."),
                      proc=l("Cortar las piezas a inglete de 45 grados y soldar las esquinas; verificar escuadra (diagonales iguales).", "Soldar los anclajes al ala vertical con cordon de 3/16\" x 25 mm.",
                             "Limpiar y aplicar anticorrosivo (excepto en la zona que quedara embutida).", "Fijar el contramarco al encofrado de la losa, nivelado y aplomado, amarrado al refuerzo del borde; vaciar la losa."),
                      ctrl=l("Medida exterior 0.70 x 0.70 m ±2 mm; diagonales iguales ±3 mm; ala de asiento a 0.08 m bajo el piso terminado."), seg=SEG_SOLD, und=und,
                      medicion=[p("Se contara el numero de contramarcos colocados (uno por registro). El peso de los angulos y la pintura se miden en sus partidas.")])
    if "MARCO" in d and und == "und":
        return bloque([p("Comprende la fabricacion del marco de angulo L 1 1/2\" x 1 1/2\" x 1/8\" de cada tapa, de 0.68 x 0.68 m, que sirve de encofrado perdido y canto de proteccion de la tapa de concreto.")],
                      mat=l("Angulo A36 L 1 1/2\" x 1 1/2\" x 1/8\"; soldadura E6011; pintura anticorrosiva y esmalte."), equ=l("Maquina de soldar, amoladora, escuadra."),
                      proc=l("Cortar 4 piezas de 0.68 m a inglete y soldar las esquinas.", "Soldar por puntos los extremos de la parrilla de la tapa al ala vertical.", "Proteger con anticorrosivo y esmalte las caras vistas."),
                      ctrl=l("Medida 0.68 x 0.68 m ±2 mm; holgura de 1 cm por lado con la abertura de 0.70 m."), seg=SEG_SOLD, und=und,
                      medicion=[p("Se contara el numero de marcos fabricados (uno por tapa).")])
    if "PINTURA" in d:
        return bloque([p("Comprende la proteccion de los angulos metalicos de marcos y contramarcos con dos manos de pintura anticorrosiva y dos manos de esmalte sintetico en sus caras expuestas.")],
                      mat=l("Pintura anticorrosiva (base epoxica o alquidica con cromato de zinc); esmalte sintetico; disolvente; lija."), equ=l("Escobilla de acero, lija, brochas, amoladora con grata."),
                      proc=l("Limpiar el oxido, la escoria y la grasa con escobilla y disolvente hasta metal blanco comercial.", "Aplicar la primera mano de anticorrosivo; la segunda a las 24 horas.",
                             "Aplicar dos manos de esmalte en las caras que quedan a la vista; retocar despues del montaje."),
                      ctrl=l("Pelicula uniforme, sin poros ni escurrimientos."), seg=l(EPP, "Ventilacion y mascarilla con filtro para vapores organicos."), und=und,
                      medicion=[p("Se medira el area pintada segun el desarrollo de las caras de los angulos (0.203 m²/m para L 2\" y 0.152 m²/m para L 1 1/2\").")])
    if "ANGULOS" in d:
        return bloque([p("Comprende el suministro de los angulos de acero de los contramarcos (L 2\" x 2\" x 3/16\", 3.63 kg/m, 2.80 m por registro) y de los marcos de tapa (L 1 1/2\" x 1 1/2\" x 1/8\", 1.83 kg/m, 2.72 m por tapa), incluida la soldadura.")],
                      mat=l("Angulos de acero A36; electrodos E6011 de 1/8\" (AWS A5.1)."), equ=l("Maquina de soldar de 250 A, amoladora."),
                      proc=l("Habilitar y soldar segun las partidas de contramarco y marco.", "Las soldaduras seran continuas, sin escoria ni porosidades (AWS D1.1)."),
                      ctrl=l("Certificado de calidad de los angulos; inspeccion visual de soldaduras."), seg=SEG_SOLD, und=und,
                      medicion=[p("Se medira el peso de los angulos colocados: longitud de cada pieza por su peso nominal, segun el metrado.")])
    # ------------------------------------------------------------ concreto simple
    if "SOLADO" in d:
        e = "0.05 m (2\")" if ("2''" in pt["desc"] or '2"' in pt["desc"]) else "0.10 m (4\")"
        return bloque([p("Comprende el vaciado de una capa de concreto simple f'c = 100 kg/cm² de %s de espesor sobre el fondo refinado y compactado, que sirve de base nivelada y limpia para el armado del acero y el vaciado de %s." % (e, "la losa de fondo del colector" if col else "la losa de las cunetas"))],
                      mat=l("Cemento Portland tipo I, arena gruesa, piedra chancada de 1/2\" y agua (dosificacion en volumen referencial 1:4:6 o segun diseno de mezcla)."),
                      equ=l("Mezcladora de 9 a 11 p³, carretillas, regla de madera, frotacho, nivel."),
                      proc=l("Humedecer el fondo compactado sin encharcarlo.", "Colocar reglas de nivel para controlar el espesor.",
                             "Vaciar, extender y reglear el concreto; acabado frotachado plano y con la pendiente del proyecto.", "Curar con agua durante 3 dias como minimo."),
                      ctrl=l("Espesor no menor que el indicado; nivel ±0.01 m; superficie sin oquedades."), seg=SEG_CONC, und=und,
                      medicion=[p("Se medira el area de solado ejecutado: ancho del solado de los planos por la longitud de cada tramo.")])
    if "DADO" in d:
        return bloque([p("Comprende el vaciado de los dados de concreto simple f'c = 140 kg/cm² de %.2f x %.2f x %.2f m que anclan la base de cada montante pluvial y protegen el codo de llegada a la red de piso o a la cuneta." % K["dado"])],
                      mat=l("Cemento Portland tipo I, arena gruesa, piedra chancada de 1/2\", agua."), equ=l("Mezcladora o mezclado en batea aprobada para pequenos volumenes, carretilla, pison."),
                      proc=l("Colocar y fijar el codo y el tubo del montante en su posicion antes del vaciado.", "Vaciar el concreto en el hoyo, compactando con varilla sin desplazar la tuberia.",
                             "Acabado plano en la cara superior; curar 7 dias."),
                      ctrl=l("Dimensiones y ubicacion segun planos; tuberia aplomada y sin danos."), seg=SEG_CONC, und=und,
                      medicion=[p("Se medira el volumen de concreto colocado: largo por ancho por alto de cada dado por el numero de dados.")])
    if "CICL" in d:
        return bloque([p("Comprende la uña de concreto ciclopeo f'c = 140 kg/cm² con 30 % de piedra mediana al pie del emboquillado de la estructura de salida (seccion trapezoidal de 0.35 / 0.15 x 0.65 m segun planos), que protege contra la socavacion.")],
                      mat=l("Concreto f'c = 140 kg/cm²; piedra mediana de 6\" a 8\", limpia, dura, sin aristas debiles (30 % del volumen)."), equ=l("Mezcladora, carretillas, pison."),
                      proc=l("Excavar a la seccion de los planos sobre terreno firme.", "Vaciar una capa de concreto de 0.10 m; colocar las piedras humedecidas, separadas al menos 0.05 m entre si y de las caras, sin tocarse, y cubrirlas con concreto.",
                             "Compactar con varilla; curar 7 dias."),
                      ctrl=l("Ninguna piedra quedara a la vista ni en contacto con otra."), seg=SEG_CONC, und=und,
                      medicion=[p("Se medira el volumen ejecutado de concreto ciclopeo segun la seccion de los planos por su longitud.")])
    if "EMBOQUILLADO" in d:
        return bloque([p("Comprende el revestimiento de piedra mediana de 6\" a 8\" asentada con concreto f'c = 140 kg/cm², de 0.20 m de espesor, sobre una capa de relleno compactado de 0.10 m, en el fondo de la estructura de salida entre los aleros, segun los planos.")],
                      mat=l("Piedra mediana de 6\" a 8\" (canto rodado o de cantera), limpia y dura; concreto f'c = 140 kg/cm²; material de relleno compactado."),
                      equ=l("Mezcladora, carretillas, comba, nivel, pison."),
                      proc=l("Compactar la base con una capa de 0.10 m de relleno al 95 % del Proctor modificado.", "Asentar las piedras humedecidas sobre una cama de concreto, con su cara plana hacia arriba y trabadas entre si.",
                             "Llenar las juntas con concreto y compactar con varilla; la superficie quedara con la pendiente de salida y sin piedras sueltas.", "Curar 7 dias."),
                      ctrl=l("Espesor de 0.20 m; piedras bien asentadas y juntas llenas."), seg=SEG_CONC, und=und,
                      medicion=[p("Se medira el area de emboquillado ejecutado en proyeccion horizontal.")])
    # ------------------------------------------------------------ concreto armado
    if "CURADO" in d:
        return bloque([p("Comprende el curado del concreto %s para mantenerlo humedo y a temperatura adecuada durante su endurecimiento, en todas sus caras expuestas: muros por ambas caras, fondo y tapa o losa superior." % ("del colector y sus estructuras" if col else "de las cunetas"))],
                      mat=l("Agua limpia; arpilleras o mantas de yute; opcionalmente compuesto quimico de curado que forme membrana (ASTM C309) aprobado por la Supervision."),
                      equ=l("Mangueras, baldes, mochila fumigadora para el curador quimico."),
                      proc=l("Iniciar el curado apenas el concreto haya fraguado y no se marque con el dedo (en clima calido, dentro de las 2 horas del acabado).",
                             "Mantener las superficies permanentemente humedas por 7 dias como minimo con riego, arpilleras humedas o arroceras; las caras encofradas se curan al desencofrar.",
                             "Si se usa curador quimico, aplicarlo uniformemente con mochila sobre la superficie aun humeda, en la dosis del fabricante.",
                             "Proteger el concreto del sol directo, el viento y la lluvia fuerte durante las primeras 24 horas; no transitar ni cargar la losa antes de 14 dias."),
                      ctrl=l("La Supervision verificara diariamente el curado y lo anotara en el cuaderno de obra."), seg=l(EPP), und=und,
                      medicion=[p("Se medira el area de concreto curada: suma de las superficies expuestas de muros (dos caras), fondo y tapa o losa, segun el metrado.")])
    if "ACABADO" in d or "FROTACHADO" in d:
        bru = "BRU" in d
        return bloque([p("Comprende el acabado frotachado%s de la cara superior de la losa del %s, que en el tramo de vereda sirve de piso peatonal, al nivel del piso terminado (+%.2f)." % (" y brunado" if bru else "", C["nombre"], C["NPT"]))],
                      mat=l("El mismo concreto de la losa; mortero cemento-arena 1:2 solo para resanes."), equ=l("Regla de aluminio, frotacho de madera, plancha de acero, brunadora."),
                      proc=l("Despues de reglear el concreto fresco de la losa, cuando pierda el brillo del agua superficial, pasar el frotacho de madera hasta lograr una superficie uniforme y antideslizante.",
                             "No espolvorear cemento seco ni agregar agua para facilitar el acabado.",
                             ("Marcar bruñas de 1 cm de profundidad en los bordes y en coincidencia con las juntas cada %.2f m." % C["juntas"]) if bru else "Los bordes se redondearan con bruñadora y la losa quedara con el bombeo de 1 % hacia el lado de la via.",
                             "Curar segun la partida de curado."),
                      ctrl=l("Planitud: separaciones no mayores de 5 mm bajo una regla de 3.00 m; nivel del piso terminado ±0.005 m respecto al piso adyacente."), seg=l(EPP), und=und,
                      medicion=[p("Se medira el area acabada de la cara superior de la losa: ancho exterior del colector por la longitud del tramo con acabado.")])
    if "ENCOFRADO" in d:
        if "FALSA COLUMNA" in d:
            el = "las falsas columnas de %.2f x %.2f x %.2f m que protegen los montantes" % K["fcol"]
        elif "ALERO" in d:
            el = "los aleros de la estructura de salida (muros de 0.15 m a 45 grados, con su zapata)"
        elif col:
            el = "el %s: caras interiores y exteriores de los muros (el muro del lado de la via puede vaciarse contra el terreno si la Supervision lo aprueba) y el fondo de la losa superior%s" % (C["nombre"], ", y las cajas" if C["cajas"] else "")
        else:
            el = "las cunetas: caras interior y exterior de los muros y el fondo de la losa de las cunetas tapadas"
        return bloque([p("Comprende el suministro, habilitacion, colocacion, apuntalamiento y retiro de los encofrados para %s, de modo que el concreto quede con la forma, dimensiones y acabado de los planos." % el)],
                      mat=l("Madera tornillo en tablas de 1\" y barrotes de 2\" x 3\", o paneles fenolicos o metalicos; alambre negro N.° 8, clavos de 2\" a 4\", desmoldante, separadores."),
                      equ=l("Herramientas de carpinteria: serrucho, martillo, sierra circular, nivel, plomada, wincha, escuadra."),
                      proc=l("Habilitar los paneles a las dimensiones de los planos; limpiar y aplicar desmoldante.",
                             "Colocar y alinear los paneles con su escuadra y plomo; asegurarlos con barrotes, tirantes y puntales para que no se deformen con el vaciado.",
                             "Dejar las ventanas y pases indicados en los planos (ventanas de llegada de cunetas, pases de tuberia, bordes de registros)." if col or "FALSA" not in d else "Dejar el espacio del tubo del montante centrado en la falsa columna.",
                             "Sellar las juntas para evitar la fuga de lechada.", "Desencofrar segun los plazos del capitulo de generalidades, sin golpear el concreto; limpiar la madera para su reuso."),
                      ctrl=l("Revision de dimensiones, plomo, alineamiento y rigidez antes del vaciado; tolerancias de la seccion -6 / +12 mm."), seg=l(EPP, "Retirar o doblar los clavos de la madera desencofrada; apilarla ordenadamente."), und=und,
                      medicion=[p("Se medira el area de contacto del encofrado con el concreto, en cada cara encofrada, segun el metrado.")])
    if "ACERO" in d and ("FY" in d.replace(" ", "").replace("'", "") or "F'Y" in d or "REFUERZO" in d):
        if "FALSA COLUMNA" in d:
            el, arm = "las falsas columnas de los montantes", "4 barras longitudinales de 3/8\" de 1.20 m y estribos de 3/8\" @0.15 m (desarrollo 0.58 m), segun el detalle de falsa columna para montante de los planos"
        elif "ALERO" in d:
            el, arm = "los aleros de la estructura de salida", "barras en L (vertical y zapata) y barras horizontales en el muro y longitudinales en la zapata, de 3/8\", segun el cuadro de doblado"
        elif "TAPA" in d:
            el, arm = "las tapas de concreto, el borde engrosado de la abertura de los registros y los anclajes del contramarco", "parrilla de 7 + 7 barras de 3/8\" @0.10 m (L = 0.62 m) por tapa, 2 asas de 3/8\" liso, 8 anclajes de 3/8\" de 0.20 m soldados al contramarco y refuerzo de borde de 2 barras de 1/2\" por lado (L = 1.40 m)"
        elif col:
            el, arm = "%s" % C["nombre"], C["acero"]
        else:
            el, arm = "las cunetas", "barras longitudinales de %s y acero transversal de %s en el cuerpo U; en los tramos tapados, la losa superior lleva su propio refuerzo segun los planos" % (K["acero_long"], K["acero_tr"])
        return bloque([p("Comprende el suministro, corte, doblado, colocacion y amarre del acero de refuerzo corrugado grado 60 (fy = 4200 kg/cm²) %s %s: %s." % ("del" if el.startswith("colector") else "de", el, arm)),
                       p("Recubrimientos libres: %s." % ("0.04 m minimo sobre las armaduras (notas del detalle de falsa columna)" if "FALSA COLUMNA" in d
                                                          else "0.04 m en las caras en contacto con el terreno y 0.025 m en las caras expuestas" if "ALERO" in d
                                                          else "0.025 m en las tapas; el borde y los anclajes segun la lamina DP-06B" if "TAPA" in d
                                                          else C["recub"] if col else "0.025 m en cunetas, 0.04 m en las caras en contacto con el suelo"))],
                      mat=l("Barras de acero corrugado NTP 341.031 / ASTM A615 grado 60; acero liso de 3/8\" para asas; alambre negro N.° 16; dados de concreto o separadores."),
                      equ=l("Cizalla o cortadora, dobladora manual (grifas y tubo), wincha, tiza."),
                      proc=l("Cortar y doblar en frio segun el cuadro de doblado de los planos, con los ganchos y diametros de doblado de la Norma E.060.",
                             "Colocar las barras en su posicion, con los espaciamientos de los planos, sobre separadores que garanticen el recubrimiento.",
                             "Amarrar con alambre N.° 16 en todos los cruces del perimetro y alternadamente en el interior; los traslapes se ubicaran alternados y fuera de las zonas de mayor esfuerzo.",
                             "En las juntas de dilatacion las barras longitudinales se interrumpen a 0.05 m de la junta; no la atraviesan." if col else "En las juntas de dilatacion las barras longitudinales se interrumpen a ambos lados de la junta.",
                             "Antes del vaciado el acero estara limpio; la Supervision lo aprobara y se anotara en el cuaderno de obra."),
                      ctrl=l("Tolerancias: espaciamiento ±10 mm; recubrimiento -5 / +10 mm; longitud de traslape no menor que la especificada."), seg=SEG_ACERO, und=und,
                      medicion=[p("Se medira el peso del acero colocado segun las longitudes de los planos (incluidos ganchos y traslapes) por el peso nominal de cada diametro (3/8\" = 0.56 kg/m; 1/2\" = 0.994 kg/m), sin considerar desperdicios ni alambre.")])
    if "CONCRETO" in d:
        if "FALSA COLUMNA" in d:
            el = "las falsas columnas de %.2f x %.2f x %.2f m que alojan y protegen el tramo inferior de cada montante pluvial" % K["fcol"]; fc = 175
        elif "CUNETA" in d:
            el = "las cunetas en U (ancho interior %.2f m, muros y losa de fondo de %.2f m; en los tramos tapados, losa superior de %.2f m), con la altura variable de cada eje segun su perfil" % (K["b"], K["em"], K["et"]); fc = 175
        elif "ALERO" in d:
            el = "los dos aleros de la estructura de salida (muros de 0.15 m, L = 1.00 m a 45 grados, altura de 0.70 a 0.45 m) con su zapata de 0.45 x 0.20 m"; fc = 210
        elif "TAPA" in d:
            el = "las tapas de los registros de limpieza (0.68 x 0.68 x 0.08 m), vaciadas dentro de su marco metalico"; fc = 210
        else:
            parte = "la losa de fondo" if "FONDO" in d else "los muros" if "MURO" in d else "la losa superior, incluidos los bordes engrosados de 0.15 x 0.10 m de las aberturas de registro" if "SUPERIOR" in d else "losa de fondo, muros y losa superior" + (" y las cajas" if C["cajas"] else "")
            el = "%s del %s (ancho interior %.2f m; muros de %.2f m; losa de fondo de %.2f m; losa superior de %.2f m y de %.2f m en el cruce de camiones)" % (parte, C["nombre"], C["b"], C["em"], C["ef"], C["es"], C["es_cam"]); fc = 210
        m = re.search(r"F[´'`]?C\s*=\s*(\d+)", d.replace(" ", ""))
        if m: fc = int(m.group(1))
        extra_proc = []
        if col and "TAPA" not in d and "ALERO" not in d:
            extra_proc = ["La losa superior se vaciara monoliticamente con los muros, sin junta horizontal, salvo junta de construccion aprobada.",
                          "El vaciado se hara por paños entre juntas de dilatacion (cada %.2f m)." % C["juntas"]]
            if C["cajas"]: extra_proc.append("Cajas: %s; muros y losa de fondo de 0.15 m vaciados con la losa del colector adyacente." % C["cajas"])
        if "CUNETA" in d:
            extra_proc = ["Vaciar primero la losa de fondo y luego los muros, o en una sola operacion con encofrado interior suspendido, cuidando que el concreto no se desplace.",
                          "En los tramos tapados la losa superior se vacia sobre encofrado; en los tramos abiertos se deja en el borde superior de los muros el rebaje de %.2f m para asentar la rejilla y se embeben los anclajes de fierro corrugado de 1/4\" soldados a su marco (detalle 1 de los planos)." % K["rej_reb"],
                          "Dar al fondo la pendiente longitudinal de %.2f %% hacia la descarga; no se aceptaran contrapendientes." % K["S"],
                          "Respetar las juntas de dilatacion cada %.2f m (partida de juntas)." % K["junta"]]
        return bloque([p("Comprende la preparacion, transporte, colocacion, compactacion y acabado del concreto f'c = %d kg/cm² de %s." % (fc, el))],
                      mat=l("Cemento Portland tipo I, arena gruesa, piedra chancada de 1/2\" a 3/4\" y agua, segun el diseno de mezcla aprobado; aditivos solo con aprobacion de la Supervision."),
                      equ=l("Mezcladora de 9 a 11 p³, vibrador de concreto de 1.5\" a 2\", carretillas, buggies, regla, frotacho, cono de Abrams y moldes de probetas."),
                      proc=l("Verificar y aprobar el encofrado, el acero, las cotas y la limpieza; humedecer el encofrado y el solado.",
                             "Preparar el concreto con mezcladora y la dosificacion aprobada; controlar el asentamiento de cada tanda.",
                             "Colocar el concreto en capas de no mas de 0.30 m y vibrarlo sin segregarlo; altura de caida no mayor de 1.50 m.",
                             *extra_proc,
                             "Dar el acabado a las superficies expuestas y empezar el curado segun la partida correspondiente.",
                             "Tomar las muestras para probetas segun el capitulo de control de calidad."),
                      ctrl=l("Resistencia a la compresion segun E.060, 5.6.3; dimensiones -6 / +12 mm; superficies sin cangrejeras (las que aparezcan se resanaran con mortero o se demoleran segun su extension, a cuenta del Contratista)."),
                      seg=SEG_CONC, und=und,
                      medicion=[p("Se medira el volumen de concreto colocado segun las dimensiones de los planos (seccion por longitud), descontando los vacios y aberturas indicados.")])
    # ------------------------------------------------------------ varios de cunetas
    if "LLORADERO" in d:
        return bloque([p("Comprende el suministro e instalacion de los lloraderos de tuberia PVC de 3\" en los muros de las cunetas colindantes con areas verdes o terreno natural sin cobertura, "
                         "segun el detalle de instalacion de lloraderos en cunetas de evacuacion pluvial y la especificacion tecnica del plano de drenaje: lloraderos de tuberia PVC Ø 3\", "
                         "espaciamiento tipico L = 1.50 m, que alivian la presion del agua infiltrada en el terreno por las lluvias y la descargan dentro de la cuneta."),
                       p("Cada unidad comprende: pase de tuberia PVC-U de 3\" (76 mm) de 0.30 m de longitud a traves del muro, a media altura entre el fondo y el borde, con pendiente S = 0.5 % hacia el interior de la cuneta; "
                         "filtro localizado de 0.30 x 0.30 x 0.30 m de grava filtrante (ripio de 20 a 40 mm) en el lado del terreno, envuelto integramente en geotextil no tejido, que retiene los finos del suelo y deja pasar el agua; "
                         "y la excavacion local y el relleno compactado alrededor del filtro."),
                       p("Ubicacion: solo en los tramos de muro de cuneta colindantes con area verde de la hoja METRADO LLORADEROS (eje, lado del muro y progresivas); los tramos junto a veredas, pisos o edificaciones no llevan lloraderos.")],
                      mat=l("Tuberia PVC-U para desague de 3\" (NTP 399.003), cortada en tramos de 0.30 m.", "Grava filtrante (ripio) de 20 a 40 mm, limpia, lavada, sin finos ni materia organica: 0.027 m³ por lloradero.",
                            "Geotextil no tejido (NTP / ASTM D4491 y D4751, clase 2 para filtro): 0.60 m² por lloradero, con traslapes de 0.10 m.", "Mortero 1:3 cemento-arena para sellar el contorno del tubo en el muro."),
                      equ=l("Herramientas manuales, sierra de arco, nivel, wincha, pison de mano."),
                      proc=l("Antes del vaciado de los muros, fijar al encofrado los tubos de 3\" @1.50 m en los tramos indicados, a media altura del muro y con pendiente de 0.5 % hacia la cuneta, tapados en sus extremos para que no entre concreto; el primero y el ultimo a no menos de 0.30 m de las juntas de dilatacion.",
                             "Despues del desencofrado, destapar los tubos y verificar que queden libres; sellar con mortero cualquier vacio alrededor del tubo.",
                             "En el lado del terreno, excavar un hueco de 0.30 x 0.30 x 0.30 m centrado en cada tubo, forrarlo con el geotextil, llenarlo con la grava y cerrar el geotextil por encima con traslape de 0.10 m.",
                             "Rellenar y compactar el resto de la zanja con la partida de relleno, sin danar el filtro."),
                      ctrl=l("Ubicacion y espaciamiento segun la hoja de metrado (tolerancia ±0.10 m); tubo libre y con pendiente hacia la cuneta; filtro completo, con el geotextil cerrado y sin contaminacion de tierra.",
                             "Prueba: al echar agua en el filtro, debe salir por el lloradero dentro de la cuneta."),
                      seg=l(EPP), und=und,
                      medicion=[p("Se contara el numero de lloraderos instalados y aprobados, con su filtro, en los tramos de la hoja METRADO LLORADEROS.")])
    if "REJILLA" in d:
        return bloque([p("Comprende la fabricacion y colocacion de la rejilla metalica movil de los tramos abiertos de las cunetas, segun el detalle de rejilla y el detalle 1 de los planos de drenaje pluvial: "
                         "modulos removibles de %.2f m de longitud (nota de los planos: rejilla metalica removible en paños de 1.00 m), formados por platinas de 1\" x 3/16\" colocadas de canto, transversales al eje de la cuneta, "
                         "soldadas por sus extremos a dos angulos L 1\" x 1\" x 3/16\" longitudinales que forman el marco (cortes B-B y C-C del detalle)." % K["rej_mod"]),
                       p("Separacion de las platinas: 1\" (0.025 m) entre ejes, con abertura libre de 0.02 m, segun la proporcion del detalle de rejilla (dibujado sin escala: la separacion entre platinas es igual al ala de 1\" del angulo del marco). "
                         "El ancho del modulo sera el ancho interior de la cuneta (%.2f m) mas el apoyo en el rebaje de %.2f m de cada borde." % (K["b"], K["rej_reb"])),
                       p("En la junta de la rejilla con el piso adyacente se deja la junta de dilatacion de 1\" con relleno asfaltico del detalle 1.")],
                      mat=l("Platina de acero A36 de 1\" x 3/16\"; angulo A36 de 1\" x 1\" x 3/16\"; soldadura E6011 de 1/8\"; pintura anticorrosiva (dos manos) y esmalte (dos manos)."),
                      equ=l("Maquina de soldar de 250 A, amoladora con disco de corte y desbaste, escuadra, wincha, brochas."),
                      proc=l("Cortar los angulos y platinas a la medida del modulo (%.2f m de largo); presentar las platinas sobre una plantilla con la separacion de 1\" entre ejes." % K["rej_mod"],
                             "Soldar cada platina por ambos extremos a los angulos del marco, verificando escuadra y planitud; las platinas quedan de canto (1\" de altura).",
                             "Esmerilar las soldaduras, limpiar con escobilla y aplicar dos manos de pintura anticorrosiva y dos de esmalte.",
                             "Colocar los modulos en el rebaje de la cuneta, apoyados en todo su perimetro, al ras del piso terminado y sin cojear."),
                      ctrl=l("Modulos a escuadra, planos, intercambiables; soldaduras continuas sin porosidades; pintura uniforme sin escurrimientos."), seg=SEG_SOLD, und=und,
                      medicion=[p("Se medira la longitud de rejilla colocada a lo largo del eje de la cuneta, solo en los tramos abiertos (sin rejilla en los tramos tapados).")])
    if "TAPA DE INSPECCION" in d:
        return bloque([p("Comprende la fabricacion y colocacion de las tapas de inspeccion de concreto armado de %.2f x %.2f x %.2f m sobre los tramos tapados de las cunetas, con %s, segun el detalle de los planos." % (K["tapa"] + (K["tapa_acero"],)))],
                      mat=l("Concreto f'c = 210 kg/cm²; acero corrugado de 3/8\" fy = 4200 kg/cm²; acero liso de 3/8\" para asas; madera para el molde."),
                      equ=l("Mezcladora o mezclado en batea, vibrador, herramientas de carpinteria."),
                      proc=l("Habilitar el molde de 0.60 x 0.60 x 0.10 m sobre una base plana.", "Colocar la parrilla con recubrimiento de 0.025 m y las dos asas embutidas en un bolsillo para que no sobresalgan.",
                             "Vaciar, vibrar y frotachar; curar 7 dias y desmoldar.", "Colocar las tapas en su abertura con holgura de 5 mm, al ras del piso."),
                      ctrl=l("Dimensiones ±3 mm; tapa plana, sin fisuras ni cangrejeras, removible con las asas."), seg=SEG_CONC, und=und,
                      medicion=[p("Se medira por unidad de tapa fabricada y colocada.")])
    if "JUNTA" in d:
        if col and "DILAT" in d:
            sell = "sellador asfaltico" if "ASFALT" in d else "sellador elastomerico de poliuretano de 25 x 25 mm (ASTM C920)"
            return bloque([p("Comprende la junta de dilatacion de 1\" (25 mm) en toda la seccion del %s, cada %.2f m (%d juntas) y en los cambios de seccion, rellena con plancha de poliestireno expandido (tecnopor) y sellada con %s en las caras interiores y en la cara superior." % (C["nombre"], C["juntas"], C["n_juntas"], sell))],
                          mat=l("Plancha de tecnopor de 1\" (densidad 15 kg/m³); " + sell + "; imprimante del sellador; cinta de respaldo."),
                          equ=l("Cuchilla, pistola de calafateo, espatula, escobilla, compresora o soplador."),
                          proc=l("Cortar la plancha de tecnopor a la forma de la seccion (anillo con el hueco interior del colector) y fijarla al concreto ya vaciado.",
                                 "Vaciar el paño siguiente contra la plancha; el acero longitudinal se interrumpe a 0.05 m a cada lado.",
                                 "Retirar 25 mm de tecnopor en las caras interiores y en la cara superior; limpiar y secar, aplicar el imprimante y el sellador con pistola, y alisar.",
                                 "La junta sera continua, recta y vertical."),
                          ctrl=l("Sellador adherido en ambas caras, sin burbujas ni discontinuidades."), seg=l(EPP, "Ventilar al aplicar imprimantes y selladores; mantenerlos lejos del fuego."), und=und,
                          medicion=[p("Se medira la longitud de junta segun el perimetro de la seccion en cada junta por el numero de juntas, como en el metrado.")])
        if col:
            return bloque([p("Comprende la junta de 1\" con plancha de poliestireno expandido (tecnopor) entre el %s y las estructuras vecinas: borde de la losa superior con el piso adyacente a ambos lados%s, de modo que cada estructura trabaje en forma independiente." % (C["nombre"], ", el cerco existente" if C["cerco"] else "" ) + (" Incluye el contacto con la caja de llegada CL." if "CL" in pt["desc"] else ""))],
                          mat=l("Plancha de tecnopor de 1\" (densidad 15 kg/m³) en tiras de 0.10 m de altura para el borde de la losa; pegamento compatible."),
                          equ=l("Cuchilla, regla, wincha."),
                          proc=l("Fijar la tira de tecnopor contra el borde de la losa del colector antes de vaciar el piso adyacente.", "Mantenerla vertical y continua; retirar los excesos al ras del piso."),
                          ctrl=l("Junta continua en toda la longitud, sin contacto directo entre el concreto del colector y el del piso."), seg=l(EPP), und=und,
                          medicion=[p("Se medira la longitud de junta colocada, a ambos lados del colector y en los contactos indicados en el metrado.")])
        return bloque([p("Comprende las juntas de dilatacion de 1\" en los muros de las cunetas, cada %.2f m y en los cambios de direccion, selladas con sellador asfaltico, para absorber los cambios de temperatura y evitar fisuras." % K["junta"])],
                      mat=l("Plancha de tecnopor de 1\" o tabla de madera aceitada que se retira; sellador asfaltico para juntas aplicado en caliente o en frio, segun el fabricante; imprimante asfaltico."),
                      equ=l("Cuchilla, espatula, pistola o tetera para el sellador, escobilla."),
                      proc=l("Dejar la separacion de 1\" al vaciar, con la plancha colocada en todo el alto del muro.", "Limpiar y secar la junta; aplicar el imprimante y llenar con el sellador hasta el ras.",
                             "Retirar los excesos y dejar la junta pareja."),
                      ctrl=l("Juntas verticales, continuas y bien selladas, sin filtraciones."), seg=l(EPP, "Cuidado con quemaduras si el sellador se aplica en caliente."), und=und,
                      medicion=[p("Se medira la longitud de junta sellada: altura del muro por el numero de muros con junta por el numero de juntas de cada eje, como en el metrado.")])
    # ------------------------------------------------------------ red de techo
    if "SOPORTE" in d:
        return bloque([p("Comprende la fabricacion y colocacion de los soportes de platina de fierro galvanizado de 1\" x 1/8\", que abrazan la canaleta (fondo y lados) y se fijan al alero o viga con dos orejas, colocados a cada %.2f m (separacion de soportes de la hoja METRADO CANALETAS: soportes por canaleta = L / %.2f + 1)." % (K["sep_sop"], K["sep_sop"]))],
                      mat=l("Platina de F°G° de 1\" x 1/8\" (desarrollo 0.85 m por soporte); pernos o tornillos autorroscantes galvanizados con arandela; tarugos."),
                      equ=l("Dobladora, taladro, amoladora, nivel."),
                      proc=l("Cortar y doblar la platina con la forma de la canaleta y las orejas de fijacion.", "Perforar y fijar a la estructura a la separacion de 0.60 m, con la pendiente de la canaleta.",
                             "Repintar con pintura rica en zinc los cortes y perforaciones."),
                      ctrl=l("Soportes alineados, firmes, a la separacion indicada."), seg=l(EPP, "Trabajo en altura con arnes."), und=und,
                      medicion=[p("Se contara el numero de soportes instalados.")])
    if "TAPA LATERAL" in d:
        return bloque([p("Comprende la fabricacion y colocacion de las tapas laterales de plancha galvanizada de 0.9 mm que cierran los extremos de cada canaleta.")],
                      mat=l("Plancha galvanizada de 0.9 mm; remaches pop de 1/8\"; sellador de poliuretano."), equ=l("Tijera de hojalatero, remachadora."),
                      proc=l("Cortar la tapa con la seccion de la canaleta mas pestanas de 0.02 m.", "Remacharla al extremo y sellar el contorno."),
                      ctrl=l("Cierre estanco, sin filtraciones."), seg=l(EPP, "Trabajo en altura con arnes."), und=und, medicion=[p("Se contara el numero de tapas colocadas.")])
    if "BOQUILLA" in d:
        return bloque([p("Comprende la fabricacion y colocacion de la boquilla de plancha galvanizada que conecta el fondo de la canaleta con la montante de PVC de 4\".")],
                      mat=l("Plancha galvanizada de 0.9 mm; remaches pop; sellador de poliuretano."), equ=l("Tijera de hojalatero, remachadora, taladro, sacabocado."),
                      proc=l("Abrir el agujero en el fondo de la canaleta en el punto bajo.", "Fabricar la boquilla con un cuello de 0.10 m que entre en la montante.",
                             "Remachar y sellar a la canaleta; insertar en la montante."),
                      ctrl=l("Sin filtraciones; la canaleta descarga totalmente por la boquilla."), seg=l(EPP, "Trabajo en altura con arnes."), und=und, medicion=[p("Se contara el numero de boquillas instaladas.")])
    if "COLGADOR" in d:
        return bloque([p("Comprende el suministro e instalacion de colgadores de fierro galvanizado que sostienen el tramo no vertical de cada montante de PVC de 4\" (desvio bajo el alero entre la boquilla de la canaleta y la bajada, con los tres codos de 90 grados de cada montante), "
                         "en la cantidad por montante de la hoja METRADO MONTANTES (hasta dos por montante, uno junto a cada codo del desvio).")],
                      mat=l("Colgadores de F°G° para tubo de 4\" con varilla roscada de 3/8\", tuercas y arandelas galvanizadas y anclajes de expansion; diametro interior del colgador 1/4\" mayor que el del tubo, como en el detalle de abrazadera."), equ=l("Taladro, llaves."),
                      proc=l("Fijar un colgador junto a cada codo del desvio, a no mas de 0.30 m del codo, de modo que el peso del tubo y del agua no cargue sobre las uniones.", "Dar al tramo la pendiente hacia la bajada y ajustar sin deformar el tubo."),
                      ctrl=l("Tuberia sin flechas ni contrapendientes."), seg=l(EPP, "Trabajo en altura con arnes."), und=und, medicion=[p("Se contara el numero de colgadores instalados.")])
    if "ABRAZADERA" in d:
        return bloque([p("Comprende el suministro e instalacion de abrazaderas de fierro galvanizado para fijar las montantes de PVC de 4\" a los muros y columnas, segun el detalle de abrazadera de F°G° para tuberia de los planos: "
                         "abrazadera tipica de platina de F°G° de e = 1/8\" con dos orejas, fijada con tirafon de 2\" x 1/4\" (55 x 6 mm) en tarugo plastico con estrias de 2\" x 1/2\" en cada oreja, colocadas @1.50 m."),
                       p("Nota del detalle: el diametro interior de cada abrazadera sera 1/4\" mayor que la medida exterior de la tuberia.")],
                      mat=l("Abrazaderas de platina de F°G° e = 1/8\" para tubo de 4\"; tirafones galvanizados de 2\" x 1/4\"; tarugos plasticos con estrias de 2\" x 1/2\"."), equ=l("Taladro con broca de 1/2\", llaves, nivel, plomada."),
                      proc=l("Marcar en el muro o columna el eje de la montante con plomada y las abrazaderas @1.50 m, la primera sobre la falsa columna y la ultima bajo el desvio superior.",
                             "Perforar con broca de 1/2\", colocar los tarugos y fijar cada abrazadera con sus dos tirafones.", "Ajustar sin deformar el tubo."),
                      ctrl=l("Montante firme y aplomada."), seg=l(EPP, "Trabajo en altura con arnes."), und=und, medicion=[p("Se contara el numero de abrazaderas instaladas.")])
    if "FALSA COLUMNA" in d and und == "und":
        return bloque([p("Comprende la falsa columna de concreto armado de %.2f x %.2f x %.2f m que aloja el tramo inferior de cada montante pluvial y lo protege contra golpes, apoyada en su dado de concreto. "
                         "Sus componentes se ejecutan y pagan en las subpartidas de concreto, encofrado y acero que siguen." % K["fcol"])],
                      proc=l("Ubicar cada falsa columna junto al muro o columna de la edificacion, con el montante centrado y aplomado.",
                             "Ejecutar el acero, el encofrado y el concreto segun sus subpartidas, sin danar la tuberia."),
                      ctrl=l("Dimensiones y plomo segun planos; montante sin deformaciones ni fisuras."), und=und,
                      medicion=[p("Se contara el numero de falsas columnas terminadas. El pago se efectua a traves de las subpartidas de concreto, encofrado y acero; esta partida no tiene pago independiente.")])
    if "MONTANTE" in d:
        return bloque([p("Comprende el suministro e instalacion de las montantes de tuberia PVC para desague de 4\", que conducen el agua de las canaletas de techo hasta la cuneta o la red de piso, con sus codos, abrazaderas y uniones, en la ubicacion y longitud de los planos.")],
                      mat=l("Tuberia PVC-U para desague de 4\" (NTP 399.003); cemento solvente para PVC (ASTM D2564) y limpiador; abrazaderas de F°G°."),
                      equ=l("Sierra de arco, lima, escalera o andamio, nivel, plomada."),
                      proc=l("Cortar los tubos a escuadra, eliminar rebabas y biselar la espiga.", "Limpiar espiga y campana, aplicar el cemento solvente en ambas y unir con un cuarto de giro; mantener 30 segundos.",
                             "Fijar la montante a la estructura con abrazaderas, aplomada, con la boquilla de la canaleta arriba y el codo de descarga abajo, embebido en su dado y falsa columna.",
                             "Probar el escurrimiento con agua antes de cerrar la falsa columna."),
                      ctrl=l("Plomo: desviacion maxima 5 mm por metro; uniones sin fugas; tuberia sin abolladuras."), seg=l(EPP, "Trabajo en altura con andamio certificado y arnes con linea de vida (Norma G.050)."), und=und,
                      medicion=[p("Se medira la longitud de montante instalada, desde la boquilla de la canaleta hasta la descarga, segun el metrado.")])
    if "CANALETA" in d:
        return bloque([p("Comprende la fabricacion y colocacion de las canaletas de techo de plancha de acero galvanizado de 0.9 mm, de seccion interior 0.25 m (fondo) x 0.20 m (alto) con pestanas de 0.05 m, una por cada lado de los techos a dos aguas, con pendiente hacia sus boquillas.")],
                      mat=l("Plancha de acero galvanizado de 0.9 mm (ASTM A653), desarrollo de 0.75 m por metro de canaleta; remaches pop de 1/8\"; sellador de poliuretano."),
                      equ=l("Dobladora de plancha, tijera de hojalatero, remachadora, taladro, andamio."),
                      proc=l("Cortar y doblar la plancha en tramos de 2.44 m con la seccion del detalle.",
                             "Unir los tramos con traslape de 0.05 m, dos filas de remaches pop de 1/8\" @0.05 m y cordon de sellador.",
                             "Colocar la canaleta sobre sus soportes con la pendiente longitudinal de %.2f %% hacia las boquillas (pendiente de diseno de la memoria hidrologica, con n = %.3f), cuidando que el borde exterior quede mas bajo que el borde de la cubierta." % (K["S_can"], K["n_can"]),
                             "Probar con agua que no haya filtraciones ni empozamientos."),
                      ctrl=l("Pendiente minima de %.2f %% verificada con nivel en cada canaleta, sin contrapendientes; alineamiento uniforme; uniones estancas; galvanizado sin rayaduras (las que se produzcan se repintaran con pintura rica en zinc)." % K["S_can"]), seg=l(EPP, "Trabajo en altura con andamio certificado y arnes con linea de vida."), und=und,
                      medicion=[p("Se medira la longitud de canaleta colocada a lo largo de cada lado del techo.")])
    # ------------------------------------------------------------ red de piso y accesorios
    if "TUBER" in d:
        return bloque([p("Comprende el suministro e instalacion de la tuberia PVC-U para desague clase pesada de 4\" de la red de recoleccion de piso, que une los sumideros con las cunetas (nota de los planos: tuberia PVC-U clase pesada de 4\" que llega a la cuneta), con pendiente minima de 1 %% para 4\" (Norma IS.010) hacia la cuneta.")],
                      mat=l("Tuberia PVC-U para desague clase pesada de 4\" (NTP 399.003) en tubos de 3 m; cemento solvente y limpiador; arena fina para la cama."),
                      equ=l("Sierra, lima, nivel, wincha, pison."),
                      proc=l("Excavar la zanja de 0.40 m de ancho y la profundidad necesaria; compactar el fondo y colocar una cama de arena de 0.10 m.",
                             "Instalar los tubos de aguas abajo hacia aguas arriba, con las campanas hacia aguas arriba, unidos con cemento solvente.",
                             "Verificar la pendiente con nivel entre buzones o sumideros.",
                             "Antes de rellenar, hacer la prueba hidraulica llenando el tramo con agua (sin fugas en 15 minutos).",
                             "Rellenar con material seleccionado en capas de 0.15 m compactadas, protegiendo los primeros 0.30 m sobre la tuberia con material fino."),
                      ctrl=l("Pendiente uniforme; sin contrapendientes ni fugas."), seg=SEG_EXC, und=und,
                      medicion=[p("Se medira la longitud de tuberia instalada entre los ejes de los accesorios, sin descontar estos.")])
    if "SUMIDERO" in d:
        return bloque([p("Comprende el suministro e instalacion de la caja sumidero de 4\" en las areas de piso del primer piso, segun el detalle de caja sumidero de los planos: rejilla metalica de platinas de 1\" x 3/16\" de 0.25 m de lado "
                         "sobre marco de angulo L 1\" x 1\" x 3/16\" fijado al concreto con anclajes de fierro de 3\" x 3/8\", caja de 0.10 m de profundidad bajo la rejilla con fondo inclinado hacia la salida, "
                         "trampa y salida de PVC de 4\" conectada a la red de piso.")],
                      mat=l("Platina de 1\" x 3/16\" y angulo L 1\" x 1\" x 3/16\" de acero A36; anclajes de fierro de 3\" x 3/8\"; accesorios de PVC de 4\"; pintura anticorrosiva y esmalte; mortero 1:4 para el asentado."),
                      equ=l("Maquina de soldar, amoladora, herramientas de albanileria."),
                      proc=l("Fabricar la rejilla y el marco segun el detalle, soldar los anclajes al marco y proteger todo con anticorrosivo y esmalte.", "Formar la caja de 0.10 m con fondo inclinado hacia la salida y conectarla a la tuberia de 4\" con su trampa y accesorios.",
                             "Asentarlo al ras del piso terminado, en el punto bajo, con pendiente del piso hacia el sumidero."),
                      ctrl=l("Ras con el piso; el agua de la superficie escurre sin empozarse."), seg=SEG_SOLD, und=und, medicion=[p("Se contara el numero de sumideros instalados.")])
    if "CODO" in d or "TEE" in d:
        nom = "tee sanitaria" if "TEE" in d else "codo de 90 grados"
        return bloque([p("Comprende el suministro e instalacion de los accesorios de PVC para desague de 4\" (%s) de la red de recoleccion de piso y de las montantes, en los cambios de direccion y derivaciones de los planos." % nom)],
                      mat=l("Accesorios de PVC-U para desague de 4\" del mismo fabricante y clase de la tuberia (NTP 399.003); cemento solvente y limpiador."),
                      equ=l("Herramientas manuales."),
                      proc=l("Limpiar las superficies de union, aplicar el cemento solvente y unir con la tuberia, manteniendo la posicion 30 segundos.", "Verificar la orientacion para que el flujo siga la direccion del diseno."),
                      ctrl=l("Uniones estancas probadas con la red."), seg=l(EPP), und=und, medicion=[p("Se contara el numero de accesorios instalados.")])
    # ------------------------------------------------------------ sin plantilla especifica
    return bloque([p("Comprende la ejecucion de la partida \"%s\" segun los planos, el metrado y las indicaciones de la Supervision." % pt["desc"])],
                  proc=l("Ejecutar segun los planos y las normas del capitulo de generalidades."), seg=l(EPP), und=und,
                  medicion=[p("Se medira en la unidad de la partida segun lo ejecutado y aprobado.")])


# ============================================================================== documento
def construir(clave):
    P = PROYECTOS[clave]; pts = partidas(P)
    # nombres de grupos para saber si estamos dentro del colector
    raiz_col = None
    for pt in pts:
        if es_titulo(pt) and "COLECTOR PLUVIAL" in pt["desc"].upper(): raiz_col = pt["codigo"]
    doc = dict(proyecto=P["proyecto"], cui=P["cui"], corto=P["corto"], entidad=ENTIDAD, especialidad=ESPECIALIDAD,
               ubicacion="SAN MARTIN - SAN MARTIN - MORALES", fecha="SETIEMBRE 2026",
               generalidades=generalidades(P, pts), partidas=[])
    base = min(len(pt["codigo"].split(".")) for pt in pts)
    for pt in pts:
        nivel = len(pt["codigo"].split(".")) - base
        col = raiz_col is not None and (pt["codigo"] == raiz_col or pt["codigo"].startswith(raiz_col + "."))
        item = dict(codigo=pt["codigo"], desc=pt["desc"], und=pt["und"], nivel=nivel)
        if not es_titulo(pt):
            item["secciones"] = espec(pt, P, dict(colector=col))
        doc["partidas"].append(item)
    os.makedirs(os.path.dirname(P["salida"]), exist_ok=True)
    fn = os.path.join(AQUI, "_json", clave + ".json"); os.makedirs(os.path.dirname(fn), exist_ok=True)
    json.dump(doc, open(fn, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    return fn, P["salida"] + ".docx", pts


# ============================================================================== ortografia (tildes) del texto redactado
_FUT = ("amarraran anotara anotaran aplicara aprobara armaran cambiara cercaran colocara comunicara construiran contara contratara cubriran demoleran "
        "efectuara eliminara enderezaran entregara estara excavaran hara haran humedecera limpiara limpiaran medira mediran ordenara pagaran picara "
        "presentara programaran quedara quedaran redondearan referiran registrara rellenara repintaran resanaran resolvera senalizaran sera seran "
        "traslapara ubicaran usara vaciara verificara volveran podra tendra").split()
_MAP = {"albanileria": "albañilería", "analisis": "análisis", "angulo": "ángulo", "angulos": "ángulos", "area": "área", "areas": "áreas", "arnes": "arnés",
        "asfaltico": "asfáltico", "brunado": "bruñado", "brunadora": "bruñadora", "caida": "caída", "calculo": "cálculo", "calido": "cálido", "capitulo": "capítulo",
        "carguio": "carguío", "carpinteria": "carpintería", "ciclopeo": "ciclópeo", "codigo": "código", "cordon": "cordón", "cubico": "cúbico", "danar": "dañar",
        "danen": "dañen", "danos": "daños", "debiles": "débiles", "despues": "después", "diametro": "diámetro", "diametros": "diámetros", "dias": "días",
        "diseno": "diseño", "elastomerico": "elastomérico", "elastomericos": "elastoméricos", "electricas": "eléctricas", "espatula": "espátula",
        "estandar": "estándar", "estan": "están", "fenolicos": "fenólicos", "frio": "frío", "granulometria": "granulometría", "hidraulica": "hidráulica",
        "humeda": "húmeda", "humedas": "húmedas", "humedo": "húmedo", "humedos": "húmedos", "linea": "línea", "manteniendolo": "manteniéndolo",
        "maxima": "máxima", "maximo": "máximo", "mecanica": "mecánica", "metalica": "metálica", "metalico": "metálico", "metalicos": "metálicos",
        "metodo": "método", "minimas": "mínimas", "minimo": "mínimo", "modulo": "módulo", "modulos": "módulos", "monoliticamente": "monolíticamente",
        "ningun": "ningún", "numero": "número", "optimo": "óptimo", "organica": "orgánica", "organico": "orgánico", "oxido": "óxido", "pequenos": "pequeños",
        "perimetro": "perímetro", "pestanas": "pestañas", "pison": "pisón", "quimico": "químico", "raices": "raíces", "region": "región", "segun": "según",
        "senalizar": "señalizar", "tamano": "tamaño", "tecnicas": "técnicas", "tecnica": "técnica", "transito": "tránsito", "traves": "través",
        "tuberia": "tubería", "tuberias": "tuberías", "ultima": "última", "ultimos": "últimos", "union": "unión", "vacios": "vacíos", "vigia": "vigía",
        "volumenes": "volúmenes", "aun": "aún", "sintetico": "sintético", "alquidica": "alquídica", "epoxica": "epóxica", "via": "vía", "lamina": "lámina",
        "laminas": "láminas", "electrodos": "electrodos", "hidraulico": "hidráulico", "geometrico": "geométrico", "periodo": "período", "acido": "ácido",
        "solida": "sólida", "plastico": "plástico", "dimension": "dimensión", "exposicion": "exposición", "mas": "más", "cubicos": "cúbicos",
        "metrico": "métrico", "titulo": "título", "maximos": "máximos", "minima": "mínima", "minimos": "mínimos", "rapido": "rápido", "facil": "fácil",
        "tecnico": "técnico", "desague": "desagüe", "metalicas": "metálicas", "dia": "día", "vacia": "vacía", "martin": "Martín", "integramente": "íntegramente", "ultimo": "último", "vacio": "vacío", "tecnicos": "técnicos", "telefono": "teléfono", "ademas": "además", "asi": "así", "esta_": "está", "tirafon": "tirafón", "desvio": "desvío", "hidrologica": "hidrológica", "topografico": "topográfico", "estrias": "estrías", "plasticos": "plásticos", "movil": "móvil", "tipica": "típica", "tipico": "típico", "maquina": "máquina"}
for f in _FUT:
    i = f.rfind("a"); _MAP[f] = f[:i] + "á" + f[i + 1:]


def _caso(orig, nuevo):
    if orig.isupper(): return nuevo.upper()
    if orig[0].isupper(): return nuevo[0].upper() + nuevo[1:]
    return nuevo


def acentos(s):
    def palabra(m):
        w = m.group(0); lw = w.lower()
        if lw in _MAP: return _caso(w, _MAP[lw])
        if lw.endswith("cion") and len(lw) > 5: return _caso(w, lw[:-4] + "ción")
        if lw.endswith("sion") and len(lw) > 5: return _caso(w, lw[:-4] + "sión")
        if lw.startswith("senaliza"): return _caso(w, "señaliza" + lw[8:])
        return w
    return re.sub(r"[A-Za-z]+", palabra, s)


def _acentuar(x):
    if isinstance(x, str): return acentos(x)
    if isinstance(x, list): return [_acentuar(v) for v in x]
    return x


_construir0 = construir


def construir(clave):
    fn, out, pts = _construir0(clave)
    doc = json.load(open(fn, encoding="utf8"))
    doc["generalidades"] = _acentuar(doc["generalidades"])
    for it in doc["partidas"]:
        if "secciones" in it: it["secciones"] = _acentuar(it["secciones"])
    json.dump(doc, open(fn, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    return fn, out, pts


if __name__ == "__main__":
    for k in (sys.argv[1:] or PROYECTOS):
        construir(k)
