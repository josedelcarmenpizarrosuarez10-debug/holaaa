"""Agrega a normas_biblioteca.json los valores del Manual de Hidrología, Hidráulica y Drenaje del MTC (R.D. N.° 20-2011-MTC/14)
que usa el drenaje vial (vial.py), cotejados con el texto oficial insumos/normas/MAN_11_HHD-2011.pdf (29-10-2026).
Se puede ejecutar varias veces: reemplaza los datos y cuadros con el mismo id.

    python3 herramientas_normas/agregar_mtc_vial.py
"""
import json
import os

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drenie_motor", "normas_biblioteca.json")
M = "MTC_HHD"


def d(id_, grupo, texto, valor, unidad, ref, consideracion, clase="norma", fuente=M):
    return {"id": id_, "grupo": grupo, "texto": texto, "valor": valor, "unidad": unidad, "clase": clase, "fuente": fuente,
            "ref": ref, "consideracion": consideracion, "estado": "verificado"}


def c(id_, grupo, titulo, ref, columnas, filas, consideracion="", clase="norma", fuente=M):
    return {"id": id_, "grupo": grupo, "titulo": titulo, "clase": clase, "fuente": fuente, "ref": ref, "columnas": columnas,
            "filas": filas, "consideracion": consideracion, "estado": "verificado"}


DATOS = [
    d("vial_racional", "Drenaje vial", "Caudal por el método racional", "Q = 0.278 C I A", "m³/s", "numeral 3.12.2, ecuación 28",
      "Muy usado para cuencas de A < 10 km²; la duración de la lluvia es igual al tiempo de concentración. I en mm/h y A en km²."),
    d("vial_racional_mod", "Drenaje vial", "Método racional modificado (Témez)", "Q = 0.278 C I A K", "m³/s",
      "numeral 3.12.2.1, ecuaciones 29 a 35",
      "Cuencas naturales de menos de 770 km² y Tc de 0.25 a 24 h: Tc = 0.3 (L/S^0.25)^0.76; K = 1 + Tc^1.25/(Tc^1.25 + 14); "
      "kA = 1 − log10(A)/15; P = kA·Pd; I = (P/24)·11^((28^0.1 − Tc^0.1)/(28^0.1 − 1)); C = (Pd − Po)(Pd + 23 Po)/(Pd + 11 Po)²; "
      "Po = 5000/CN − 50."),
    d("vial_cuneta_pendiente", "Drenaje vial", "Pendiente longitudinal de la cuneta", "0.5 % < i < 2 %", "",
      "numeral 4.1.2, literal c)",
      "Entre la condición de autolimpieza y la que produciría velocidades erosivas; fuera de ese rango se verifica la velocidad "
      "con la Tabla N.° 33."),
    d("vial_cuneta_longitud", "Drenaje vial", "Longitud máxima de cuneta hasta su alcantarilla de alivio", "250 / 200", "m",
      "numeral 4.1.2.1, literal d)",
      "Región seca o poco lluviosa: 250 m como máximo (recorridos mayores se justifican técnicamente); región muy lluviosa: se "
      "recomienda reducirla a 200 m. Se adopta 200 m desde 1600 mm/año (región muy lluviosa de la Tabla N.° 34)."),
    d("vial_cuneta_revestimiento", "Drenaje vial", "Revestimiento de la cuneta", "f'c = 175 kg/cm², e = 0.075 m", "",
      "numeral 4.1.2.1, literal e)",
      "Se reviste cuando la velocidad supera los límites de la Tabla N.° 33 o el terreno es muy permeable."),
    d("vial_cuneta_berma", "Drenaje vial", "Berma exterior de recepción entre la cuneta y el pie del talud", 0.60, "m",
      "numeral 4.1.2.1, literal c)", "Ancho mínimo; recibe la caída de materiales del talud superior."),
    d("vial_cuneta_h", "Drenaje vial", "Altura de la cuneta triangular en el procedimiento de cálculo", "< 0.60", "m",
      "numeral 4.1.2.1, literal a)", "En el procedimiento de cálculo: «elijo una altura H, que sea menor a 0.60 m»."),
    d("vial_alc_dmin", "Drenaje vial", "Sección mínima de alcantarilla", 0.90, "m",
      "numeral 4.1.1.3.4, literal a)",
      "En carreteras de alto volumen de tránsito, por limpieza y mantenimiento: circular de 0.90 m (36\") o su equivalente; salvo "
      "cruces de canales de riego."),
    d("vial_alc_selva", "Drenaje vial", "Diámetro mínimo de TMC en selva alta", "48", "pulg",
      "numeral 4.1.1.3.7, literal a)",
      "Cauces encajonados en V, pendientes de 5 % a 60 %, taludes y lecho granulares erosionables y vegetación arbustiva: flujos de "
      "barro con caudal sólido de al menos 2 veces el líquido; diámetro mínimo TMC Ø 48\"."),
    d("vial_alc_borde", "Drenaje vial", "Borde libre de la alcantarilla", 25, "% de la altura",
      "numeral 4.1.1.3.7, literal b)",
      "No se diseña a sección llena; como mínimo el 25 % de la altura, diámetro o flecha (tirante ≤ 75 %)."),
    d("vial_alc_vmin", "Drenaje vial", "Velocidad mínima en la alcantarilla", 0.25, "m/s", "numeral 4.1.1.3.6",
      "Para que no haya sedimentación que reduzca su capacidad hidráulica."),
    d("vial_alc_manning", "Drenaje vial", "Diseño hidráulico de la alcantarilla", "V = R^(2/3) S^(1/2) / n", "m/s",
      "numeral 4.1.1.3.6, ecuación 47", "Régimen uniforme (Manning) con el n de la Tabla N.° 09."),
    d("vial_laushey", "Drenaje vial", "Protección a la salida de la alcantarilla (Laushey)", "d50 = V² / (3.1 g)", "m",
      "numeral 4.1.1.3.7, literal c), ecuación 49", "Diámetro medio del enrocado de protección según la velocidad a la salida."),
    d("vial_alc_separacion", "Drenaje vial", "Separación entre tubos de alcantarillas múltiples", "D/2 (0.40 a 1.00)", "m",
      "numeral 4.1.1.3.4, literal a)", "Medida entre superficies externas: la mitad del diámetro, con 1.0 m como máximo y 0.4 m como mínimo."),
    d("vial_baden_bl", "Drenaje vial", "Borde libre del badén", "0.30 a 0.50", "m", "numeral 4.1.1.4.1, literal e)",
      "Entre el nivel del flujo máximo esperado y la superficie de rodadura."),
    d("vial_baden_pt", "Drenaje vial", "Pendiente transversal del badén", "2 a 3", "%", "numeral 4.1.1.4.1, literal d)",
      "Para evacuar el material de arrastre; el badén se idealiza como canal trapezoidal en régimen uniforme (4.1.1.4.2)."),
    d("vial_bordillo", "Drenaje vial", "Bordillo en terraplenes", "base 0.20, corona 0.15, altura 0.40", "m",
      "numeral 4.1.2.5",
      "En terraplenes de más de 1.5 m; sobresale 0.15 m de la rodadura; aliviaderos cada 50 a 100 m en tangente."),
]

CUADROS = [
    c("vial_riesgo_tabla02", "Drenaje vial", "Valores máximos recomendados de riesgo admisible de obras de drenaje", "numeral 3.6, Tabla N.° 02",
      ["Tipo de obra", "Riesgo admisible (%)", "Vida útil n (años)"],
      [["Puentes", 25, 40], ["Alcantarillas de paso de quebradas importantes y badenes", 30, 25],
       ["Alcantarillas de paso de quebradas menores y descarga de agua de cunetas", 35, 15],
       ["Drenaje de la plataforma (a nivel longitudinal)", 40, 15], ["Subdrenes", 40, 15], ["Defensas ribereñas", 25, 40]],
      "T = 1 / (1 − (1 − R)^(1/n)) (ecuación 1). El propietario de la obra define el riesgo admisible y la vida útil."),
    c("vial_tc_tabla05", "Drenaje vial", "Fórmulas para el tiempo de concentración", "numeral 3.9, Tabla N.° 05",
      ["Método", "tc (min)", "Datos"],
      [["Kirpich (1940)", "0.01947 L^0.77 S^−0.385", "L longitud del canal (m); S pendiente media (m/m)"],
       ["California Culverts Practice (1942)", "0.0195 (L³/H)^0.385", "L curso más largo (m); H desnivel divisoria-salida (m)"],
       ["Federal Aviation Administration (1970)", "0.7035 (1.1 − C) L^0.50 / S^0.333", "C racional; L flujo superficial (m); S (m/m)"],
       ["Retardo SCS (1973)", "0.0136 L^0.8 (1000/CN − 9)^0.7 / S^0.5", "L longitud hidráulica (m); CN; S (m/m)"],
       ["Témez (numeral 3.12.2.1)", "60 · 0.3 (L/S^0.25)^0.76", "L cauce mayor (km); S (m/m)"]],
      "Kirpich: para flujo superficial en concreto o asfalto se multiplica tc por 0.4 y para canales de concreto por 0.2; sin ajuste "
      "para suelo descubierto o cunetas. California es esencialmente la ecuación de Kirpich."),
    c("vial_C_tabla08", "Drenaje vial", "Coeficientes de escorrentía, método racional", "numeral 3.12.2, Tabla N.° 08",
      ["Cobertura vegetal", "Tipo de suelo", "> 50 %", "> 20 %", "> 5 %", "> 1 %", "< 1 %"],
      [["Sin vegetación", "Impermeable", 0.80, 0.75, 0.70, 0.65, 0.60], ["Sin vegetación", "Semipermeable", 0.70, 0.65, 0.60, 0.55, 0.50],
       ["Sin vegetación", "Permeable", 0.50, 0.45, 0.40, 0.35, 0.30], ["Cultivos", "Impermeable", 0.70, 0.65, 0.60, 0.55, 0.50],
       ["Cultivos", "Semipermeable", 0.60, 0.55, 0.50, 0.45, 0.40], ["Cultivos", "Permeable", 0.40, 0.35, 0.30, 0.25, 0.20],
       ["Pastos, vegetación ligera", "Impermeable", 0.65, 0.60, 0.55, 0.50, 0.45],
       ["Pastos, vegetación ligera", "Semipermeable", 0.55, 0.50, 0.45, 0.40, 0.35],
       ["Pastos, vegetación ligera", "Permeable", 0.35, 0.30, 0.25, 0.20, 0.15], ["Hierba, grama", "Impermeable", 0.60, 0.55, 0.50, 0.45, 0.40],
       ["Hierba, grama", "Semipermeable", 0.50, 0.45, 0.40, 0.35, 0.30], ["Hierba, grama", "Permeable", 0.30, 0.25, 0.20, 0.15, 0.10],
       ["Bosques, densa vegetación", "Impermeable", 0.55, 0.50, 0.45, 0.40, 0.35],
       ["Bosques, densa vegetación", "Semipermeable", 0.45, 0.40, 0.35, 0.30, 0.25],
       ["Bosques, densa vegetación", "Permeable", 0.25, 0.20, 0.15, 0.10, 0.05]],
      "Columnas por pendiente del terreno: pronunciada (> 50 %), alta (> 20 %), media (> 5 %), suave (> 1 %) y despreciable (< 1 %)."),
    c("vial_n_tabla09", "Drenaje vial", "Coeficiente de rugosidad de Manning (valores normales usados)", "numeral 4.1.1.3.6, Tabla N.° 09",
      ["Superficie", "n mínimo", "n normal", "n máximo"],
      [["Metal corrugado, dren para aguas lluvias (TMC)", 0.021, 0.024, 0.030], ["Concreto, tubo recto y libre de basuras", 0.010, 0.011, 0.013],
       ["Canal revestido de concreto afinado con plana", 0.011, 0.013, 0.015], ["Albañilería de piedra con mortero", 0.017, 0.025, 0.030],
       ["Tierra, recto y uniforme, nuevo", 0.016, 0.018, 0.020]],
      "Fuente citada por el MTC: Hidráulica de Canales Abiertos, Ven Te Chow, 1983."),
    c("vial_K_tabla32", "Drenaje vial", "Coeficiente de Strickler K (= 1/n) más usado en cunetas", "numeral 4.1.2.1, Tabla N.° 32",
      ["Cuneta", "K", "n = 1/K"],
      [["Excavada en el terreno", 33, 0.030], ["En roca", 25, 0.040], ["De concreto", 67, 0.015]],
      "Fuente citada por el MTC: Ingeniería Vial I, Hugo Morales Sosa."),
    c("vial_vel_tabla33", "Drenaje vial", "Velocidades límites admisibles en cunetas", "numeral 4.1.2.1, Tabla N.° 33",
      ["Tipo de superficie", "V mínima del rango (m/s)", "V máxima del rango (m/s)"],
      [["Arena fina o limo (poca o ninguna arcilla)", 0.20, 0.60], ["Arena arcillosa dura, margas duras", 0.60, 0.90],
       ["Terreno parcialmente cubierto de vegetación", 0.60, 1.20], ["Arcilla, grava, pizarras blandas con cubierta vegetal", 1.20, 1.50],
       ["Hierba", 1.20, 1.80], ["Conglomerado, pizarras duras, rocas blandas", 1.40, 2.40], ["Mampostería, rocas duras", 3.00, 4.50],
       ["Concreto", 4.50, 6.00]],
      "Mampostería y concreto: para flujos de muy corta duración. Se adopta el límite inferior de cada rango, del lado seguro."),
    c("vial_cuneta_tabla34", "Drenaje vial", "Dimensiones mínimas de la cuneta triangular", "numeral 4.1.2.1, literal c), Tabla N.° 34",
      ["Región", "Precipitación anual (mm)", "Profundidad d (m)", "Ancho a (m)"],
      [["Seca", "< 400", 0.20, 0.50], ["Lluviosa", "400 a < 1600", 0.30, 0.75], ["Muy lluviosa", "1600 a < 3000", 0.40, 1.20],
       ["Muy lluviosa", "> 3000", "0.30 (trapezoidal, fondo ≥ 0.30)", 1.20]],
      "El ancho se mide desde el borde de la rasante hasta la vertical del vértice inferior y la profundidad desde el borde de la "
      "rasante al fondo (Figura N.° 27)."),
    c("vial_talud_304_12", "Drenaje vial", "Inclinación máxima del talud interior de la cuneta (V:H)",
      "numeral 4.1.2.1 (Tabla N.° 304.12 del Manual de Diseño Geométrico DG-2001)",
      ["Velocidad de diseño", "IMDA < 750 veh/día", "IMDA > 750 veh/día"],
      [["< 70 km/h", "1:2 – 1:3 (*)", "1:3"], ["> 70 km/h", "1:3", "1:4"]],
      "(*) Sólo en casos muy especiales (en la tabla la nota está junto a 1:2 y 1:3). El talud exterior sigue la inclinación del "
      "talud de corte."),
    c("vial_vel_tabla11", "Drenaje vial", "Velocidades máximas admisibles en canales no revestidos", "numeral 4.1.1.3.6, Tabla N.° 11",
      ["Tipo de terreno", "Flujo intermitente (m/s)", "Flujo permanente (m/s)"],
      [["Arena fina (no coloidal)", 0.75, 0.75], ["Arcilla arenosa (no coloidal)", 0.75, 0.75], ["Arcilla limosa (no coloidal)", 0.90, 0.90],
       ["Arcilla fina", 1.00, 1.00], ["Ceniza volcánica", 1.20, 1.00], ["Grava fina", 1.50, 1.20], ["Arcilla dura (coloidal)", 1.80, 1.40],
       ["Material graduado desde arcilla a grava", 2.00, 1.50], ["Material graduado desde limo a grava", 2.10, 1.70], ["Grava", 2.30, 1.80],
       ["Grava gruesa", 2.40, 2.00], ["Desde grava a piedras (< 15 cm)", 2.70, 2.10], ["Desde grava a piedras (> 20 cm)", 3.00, 2.40]],
      "Para la velocidad a la salida de la alcantarilla sobre el cauce natural. Fuente citada por el MTC: Manual de Carreteras de California."),
]


def main():
    b = json.load(open(RUTA, encoding="utf-8"))
    for lista, nuevos in ((b["datos"], DATOS), (b["cuadros"], CUADROS)):
        ids = {x["id"] for x in nuevos}
        lista[:] = [x for x in lista if x["id"] not in ids] + nuevos
    b["version"] = "2026-10-29"
    with open(RUTA, "w", encoding="utf-8") as f:
        json.dump(b, f, ensure_ascii=False, indent=1); f.write("\n")
    print("OK · %d datos y %d cuadros del drenaje vial (MTC)" % (len(DATOS), len(CUADROS)))


if __name__ == "__main__":
    main()
