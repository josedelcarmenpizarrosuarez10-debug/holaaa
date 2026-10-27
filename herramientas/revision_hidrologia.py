"""Revision coordinada de las memorias hidrologicas de los tres proyectos del colector frontal compartido.

Agrega en las tres memorias (CAR Varones CUI 2705619, Hogar de Refugio Temporal CUI 2675514 y CAR Mujeres CUI 2717013) el mismo
texto que justifica las dos intensidades (210.98 mm/h para canaletas, montantes, sumideros y cunetas; 155.66 mm/h para el
colector), el coeficiente ponderado del colector y los caudales compartidos, y corrige en cada una el porcentaje de la
comparacion C = 0.88 / C ponderado (la plantilla decia 7,2 % en las tres).

No cambia ningun valor de diseno: solo textos. Es idempotente (si el texto ya esta, no lo repite).
Uso: python3 herramientas/revision_hidrologia.py      (revisa las tres; la de Wilma se guarda como copia en entregables_mujeres)
"""
import os, sys, re, copy
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARCA = "Intensidad de diseño: 210.98 mm/h en cunetas y 155.66 mm/h en el colector"

# datos de cada proyecto (memorias HIDRO-CE040 y memoria de calculo del colector de 3 proyectos)
P24, I10, I15, FS = 121.81, 210.98, 155.66, 1.15
I15_EXACTA = P24 * (15 / 1440) ** 0.25 * 60 / 15            # 155.659 mm/h: las memorias calculan con el valor sin redondear
PROY = {
    "varones": {"nombre": "CAR Varones", "cui": "2705619", "A": 6752.03, "CA": 5203.32},
    "refugio": {"nombre": "Hogar de Refugio Temporal", "cui": "2675514", "A": 7520.41, "CA": 6072.36},
    "mujeres": {"nombre": "CAR Mujeres", "cui": "2717013", "A": 7491.56, "CA": 5274.45},
}
for v in PROY.values():
    v["C"] = v["CA"] / v["A"]; v["Q"] = v["CA"] * I15_EXACTA * FS / 3600


def q(k): return PROY[k]["Q"]


def bloque():
    """El mismo texto para las tres memorias: (tipo, texto). tipo: t = subtitulo en negrita, p = parrafo, f = formula."""
    v, r, m = PROY["varones"], PROY["refugio"], PROY["mujeres"]
    k10, k15 = (10 / 1440) ** 0.25, (15 / 1440) ** 0.25
    Qvr = round(q("varones"), 1) + round(q("refugio"), 1); Qt = q("varones") + q("refugio") + q("mujeres")
    return [
        ("t", MARCA),
        ("p", "Las dos intensidades del estudio provienen del mismo análisis estadístico de precipitaciones máximas en 24 horas "
              "(estación CO Tarapoto, distribución Log-Normal, período de retorno de 25 años), común a los tres proyectos que "
              "descargan al colector frontal compartido: CAR Varones (CUI 2705619), Hogar de Refugio Temporal (CUI 2675514) y "
              "CAR Mujeres (CUI 2717013). De ese análisis resulta una sola lluvia de diseño, P24 = %.2f mm. Con el método de "
              "Dick y Peschke se obtiene la lluvia de cualquier duración D (en minutos) y su intensidad:" % P24),
        ("f", "P_D = P24 · (D / 1440)^0.25          I_D = P_D · 60 / D"),
        ("p", "Para las dos duraciones que se emplean en el proyecto:"),
        ("f", "D = 10 min:   P10 = %.2f · (10 / 1440)^0.25 = %.2f · %.4f = %.2f mm" % (P24, P24, k10, P24 * k10)),
        ("f", "I10 = %.2f · 60 / 10 = %.2f mm/h" % (P24 * k10, I10)),
        ("f", "D = 15 min:   P15 = %.2f · (15 / 1440)^0.25 = %.2f · %.4f = %.2f mm" % (P24, P24, k15, P24 * k15)),
        ("f", "I15 = %.2f · 60 / 15 = %.2f mm/h" % (P24 * k15, I15)),
        ("p", "Por lo tanto, la intensidad de 210.98 mm/h no se reemplaza: a cada elemento se le aplica la intensidad que "
              "corresponde a su duración de diseño. La Norma Técnica CE.040 establece que la intensidad de diseño de un punto "
              "corresponde a una duración igual al tiempo de concentración del área que drena hacia él, con un mínimo de 10 minutos:"),
        ("p", "•  Canaletas, montantes, sumideros y cunetas: drenan áreas pequeñas (un techo o un tramo de piso), en las que el "
              "agua llega en menos de 10 minutos. Se adopta el mínimo normativo, D = 10 min, con I = 210.98 mm/h. Con esta "
              "intensidad se dimensionan todos esos elementos, y su cálculo no cambia."),
        ("p", "•  Colector frontal: recibe el agua de los tres predios. El agua del punto más alejado recorre primero el techo o "
              "el piso hasta la cuneta (tiempo de entrada, 10 min), luego la cuneta hasta el colector (aproximadamente 3 min) y "
              "por último el colector hasta su salida (139 m en el tramo del CAR Mujeres, con velocidades de 1.1 a 1.4 m/s, "
              "aproximadamente 2 min). Su tiempo de concentración es tc = 10 + 3 + 2 = 15 min y su intensidad, I = 155.66 mm/h. "
              "Se emplea la misma intensidad en los tres tramos del colector, para que el caudal que entrega cada proyecto "
              "coincida con el que recibe el siguiente."),
        ("p", "Calcular el colector con 210.98 mm/h equivaldría a suponer que el agua de los tres predios llega toda a la vez en "
              "10 minutos, lo que no ocurre: el caudal resultaría un %.1f %% mayor (210.98 / 155.66 = %.3f) sin sustento en la "
              "norma. El cálculo del colector se mantiene del lado de la seguridad, porque suma los caudales máximos de los tres "
              "proyectos sin descontar el desfase entre ellos y aplica el factor de seguridad FS = 1.15." % ((I10 / I15 - 1) * 100, I10 / I15)),
        ("t", "Coeficiente de escorrentía y caudales del colector compartido"),
        ("p", "En canaletas, montantes, sumideros y cunetas se emplea el coeficiente uniforme C = 0.88 adoptado en el capítulo de "
              "coeficientes, como simplificación conservadora. En el colector, que recibe toda el área de cada predio, incluidas "
              "las áreas verdes que infiltran, se emplea el coeficiente ponderado por superficie de cada proyecto (Σ C·A / A, con "
              "los coeficientes de la Tabla 1.a del Anexo I de la CE.040): CAR Varones %.3f, Hogar de Refugio Temporal %.3f y "
              "CAR Mujeres %.3f. Con Q = Σ C·A · I · FS / 3600, I = 155.66 mm/h y FS = 1.15, los caudales del colector compartido "
              "son los mismos en las tres memorias:" % (v["C"], r["C"], m["C"])),
        ("f", "CAR Varones (CUI 2705619): %s m² · 155.66 · 1.15 / 3600 = %.1f L/s, entregados en la caja de llegada CL"
              % (fmt(v["CA"]), q("varones"))),
        ("f", "Hogar de Refugio Temporal (CUI 2675514): %s m² · 155.66 · 1.15 / 3600 = %.1f L/s" % (fmt(r["CA"]), q("refugio"))),
        ("f", "Entrega al registro R-01 del CAR Mujeres: %.1f + %.1f = %.1f L/s (%.2f L/s sin redondear, es decir, %.1f L/s)"
              % (q("varones"), q("refugio"), Qvr, q("varones") + q("refugio"), q("varones") + q("refugio"))),
        ("f", "CAR Mujeres (CUI 2717013): %s m² · 155.66 · 1.15 / 3600 = %.1f L/s" % (fmt(m["CA"]), q("mujeres"))),
        ("f", "Caudal total en la salida del colector: %.1f + %.1f + %.1f = %.1f L/s"
              % (q("varones"), q("refugio"), q("mujeres"), Qt)),
        ("p", "Para el CAR Mujeres, Σ C·A = %s m² corresponde a %s m² de las fichas de áreas tributarias; el cuadro de "
              "superficies de su estudio suma 7 490.66 m². La diferencia, de 0.90 m² (0.01 %%), se debe al redondeo de las fichas "
              "y modifica el caudal en 0.1 L/s." % (fmt(m["CA"]), fmt(m["A"]))),
    ]


def fmt(x):
    return "{:,.2f}".format(x).replace(",", " ")


def _texto(p, t, negrita=None):
    """Deja el parrafo con un solo run (el primero, con su formato) y el texto t."""
    runs = p.runs
    if not runs:
        p.add_run(t)
    else:
        guia = next((r for r in runs if r.text.strip()), runs[0])   # el primer run con texto conserva el formato
        guia.text = t
        for r in runs:
            if r is not guia: r._r.getparent().remove(r._r)
    if negrita is not None:
        for r in p.runs: r.bold = negrita


def _clon(modelo, despues_de, t, negrita=None):
    el = copy.deepcopy(modelo._p)
    despues_de._p.addnext(el)
    p = docx.text.paragraph.Paragraph(el, modelo._parent)
    _texto(p, t, negrita)
    return p


def _buscar(doc, patron, desde=0):
    for i, p in enumerate(doc.paragraphs):
        if i >= desde and re.search(patron, p.text): return i
    raise ValueError("no se encontro: " + patron)


def _formula_modelo(doc, desde):
    for p in doc.paragraphs[desde:]:
        if p.alignment == WD_ALIGN_PARAGRAPH.CENTER and "=" in p.text and len(p.text) < 160: return p
    raise ValueError("sin parrafo de formula")


def revisar(origen, destino, clave):
    d = docx.Document(origen)
    if any(MARCA in p.text for p in d.paragraphs):
        if origen != destino: d.save(destino)
        return "ya revisada"
    me = PROY[clave]; pct = (0.88 / me["C"] - 1) * 100; Cs = ("%.3f" % me["C"]).replace(".", ",")
    cambios = []
    # 1. coeficiente adoptado: C = 0.88 para canaletas, montantes, sumideros y cunetas; colector con C ponderado
    i = _buscar(d, r"^Para el dimensionamiento del sistema de drenaje pluvial .* se adopta un coeficiente uniforme")
    p = d.paragraphs[i]
    _texto(p, re.sub(r"^Para el dimensionamiento del sistema de drenaje pluvial", "Para el dimensionamiento de las canaletas, "
                     "montantes, sumideros y cunetas del sistema de drenaje pluvial", p.text)); cambios.append("coef. adoptado")
    i = _buscar(d, r"ponderación conservadora previamente calculada")
    _texto(d.paragraphs[i], "La comparación con el coeficiente ponderado por superficie del proyecto (C = %s, Σ C·A / A con los "
           "coeficientes de la Tabla 1.a del Anexo I de la CE.040) muestra que utilizar C = 0,88 incrementa el caudal "
           "aproximadamente %s %%, manteniendo iguales el área aportante y la intensidad de lluvia. De esta manera, se incorpora "
           "un margen explícito en la estimación de la escorrentía de canaletas, montantes, sumideros y cunetas. El colector "
           "frontal, que recibe toda el área del predio y los aportes de los proyectos colindantes, se calcula con el coeficiente "
           "ponderado (ver el capítulo del colector)." % (Cs, ("%.1f" % pct).replace(".", ","))); cambios.append("porcentaje %.1f %%" % pct)
    try:
        i = _buscar(d, r"^En consecuencia, para los cálculos de caudal del sistema se adopta C = 0,88")
        p = d.paragraphs[i]
        _texto(p, p.text.replace("para los cálculos de caudal del sistema se adopta", "para los cálculos de caudal de canaletas, "
                                 "montantes, sumideros y cunetas se adopta")); cambios.append("en consecuencia")
    except ValueError:
        pass
    # 2. intensidad adoptada (10 min): indicar donde se usa y remitir al colector
    i = _buscar(d, r"La adopción de la intensidad de diseño de 210[.,]98 mm/h")
    p = d.paragraphs[i]
    _texto(p, p.text.rstrip() + " Esta intensidad (duración de 10 minutos) corresponde a canaletas, montantes, sumideros y "
           "cunetas; el colector frontal, cuyo tiempo de concentración es de 15 minutos, se calcula con 155.66 mm/h, obtenida de "
           "la misma lluvia de diseño (ver el capítulo del colector)."); cambios.append("intensidad adoptada")
    # 3. bloque comun en el capitulo del colector, despues de la tabla de caudales (su parrafo "Fuente")
    ancla = {"mujeres": r"^Tabla N° ?\d+: Caudales de diseño que llegan al colector frontal",
             "refugio": r"Caudal de diseño del colector frontal, tramo Hogar de Refugio Temporal",
             "varones": r"^El caudal total del proyecto, [\d.]+ L/s, es el obtenido"}[clave]
    ia = _buscar(d, ancla)
    i_f = _buscar(d, r"^Fuente", ia)
    cuerpo = d.paragraphs[_buscar(d, r"^(Los caudales se calculan con el Método Racional|El caudal propio del Hogar|El caudal total del proyecto)")]
    formula = _formula_modelo(d, _buscar(d, r"(DISEÑO DEL COLECTOR|COLECTOR PLUVIAL FRONTAL)"))
    ult = d.paragraphs[i_f]
    for tipo, t in bloque():
        if tipo == "f": ult = _clon(formula, ult, t, negrita=False)
        elif tipo == "t": ult = _clon(cuerpo, ult, t, negrita=True); ult.alignment = WD_ALIGN_PARAGRAPH.LEFT
        else: ult = _clon(cuerpo, ult, t, negrita=False)
    cambios.append("bloque de intensidades y caudales")
    # 4. correcciones propias de cada memoria
    # area del CAR Varones: la de su propia memoria (6 752.03 m2); C del Refugio: 6072.36 / 7520.41 = 0.807
    reemplazos = {"6,752.06": "6,752.03", "6752.06": "6752.03", "21,764.03": "21,764.00"}
    for p in d.paragraphs:
        if "6752.06" in p.text or "6,752.06" in p.text:
            _texto(p, p.text.replace("6,752.06", "6,752.03").replace("6752.06", "6752.03")); cambios.append("area en texto")
    for t in d.tables:
        for row in t.rows:
            celdas = row.cells
            for x in celdas:
                if x.text.strip() in reemplazos:
                    _texto(x.paragraphs[0], reemplazos[x.text.strip()]); cambios.append("area %s" % x.text.strip())
            if celdas and celdas[0].text.startswith("Hogar de Refugio") and len(celdas) > 2 and celdas[2].text.strip() == "0.808":
                _texto(celdas[2].paragraphs[0], "%.3f" % PROY["refugio"]["C"]); cambios.append("C Refugio 0.807 en la tabla")
    if clave == "varones":
        i = _buscar(d, r"^El caudal total del proyecto, [\d.]+ L/s, es el obtenido")
        p = d.paragraphs[i]
        _texto(p, re.sub(r"\(TR = 25 años, I = 210\.98 mm/h, FS = 1\.15\)",
                         "(TR = 25 años, tc = 15 min, I = 155.66 mm/h, C ponderado = %.3f, FS = 1.15)" % me["C"], p.text))
        cambios.append("I = 155.66 en el caudal total")
    if clave == "mujeres": planos_mujeres(d, cambios)
    d.save(destino)
    return ", ".join(cambios)


# codigos de lamina del juego de planos del CAR Mujeres (PLANOS_ANDFY_MUJERES, set. 2026) que cita la memoria
PLANOS_M = {
    "Fuente: planos DP-04 y DP-06A del colector pluvial.":
        "Fuente: planos ST-CG-01 y ST-CG-02 (secciones transversales del colector) y STP-CG (secciones típicas del colector).",
    "Fuente: plano DP-06A, detalles típicos del colector.": "Fuente: plano STP-CG, secciones típicas del colector.",
    "Fuente: plano DP-07 del colector pluvial.": "Fuente: plano ESDAE-01, estructura de salida con dos aleros y emboquillado.",
    "Fuente: plano DP-09 del colector pluvial.": "Fuente: plano IC-01, isométricos constructivos (isométrico 4: estructura de salida).",
}
TAPA_M = ("Cada registro tiene una luz libre de 0.60 × 0.60 m y una tapa ciega de concreto armado de 0.68 × 0.68 × 0.08 m "
          "(f'c = 210 kg/cm², parrilla de 3/8\" @0.10 en ambos sentidos), sin marco ni contramarco metálico. La tapa se vacía aparte "
          "en obra y se asienta en un rebaje de 0.70 × 0.70 × 0.08 m formado en la losa (asiento de 0.05 m por lado y holgura de 1 cm), "
          "de modo que queda al ras de la vereda y es removible; se levanta con dos asas de fierro liso de 1/2\" alojadas en cajuelas, "
          "que no sobresalen (peso aproximado de 89 kg). El borde del registro lleva un engrosamiento de 0.15 × 0.10 m bajo la losa con "
          "2 barras de 1/2\" por lado. Detalle en el plano D-RL.")


def planos_mujeres(d, cambios):
    """Memoria de Wilma: codigos de lamina del juego de planos vigente y tapa ciega segun el plano D-RL."""
    for p in d.paragraphs:
        t = p.text.strip()
        if t in PLANOS_M:
            _texto(p, PLANOS_M[t]); cambios.append(t.split("plano")[-1].split(" del")[0].split(",")[0].strip() + " -> lamina nueva")
        elif t.startswith("Cada registro tiene una luz libre de 0.60") and "contramarco de ángulo" in t:
            _texto(p, TAPA_M); cambios.append("tapa ciega segun D-RL")
        elif t.endswith("Las tapas deberán permanecer colocadas y aseguradas en su contramarco."):
            _texto(p, t.replace("aseguradas en su contramarco.", "asentadas en su rebaje.")); cambios.append("tapa en su rebaje")
        for r in p.runs:
            for x, y in PERFIL_M.items():
                if x in r.text:
                    r.text = r.text.replace(x, y); cambios.append(y)


# rangos del perfil de flujo completo de la memoria de calculo (todas las estaciones, no solo los ejes)
PERFIL_M = {
    "números de Froude entre 0.52 y 0.74": "números de Froude entre 0.51 y 0.74",
    "velocidades se mantienen entre 1.13 y 1.43 m/s": "velocidades se mantienen entre 1.02 y 1.43 m/s",
    "manteniéndose un borde libre mínimo de 0.10 m": "manteniéndose un borde libre mínimo de 0.091 m",
}


ARCH = {
    "mujeres": (os.path.join(RAIZ, "insumos", "wilma", "MEMORIA_HIDROLOGICA_CAR_MUJERES.docx"),
                os.path.join(RAIZ, "entregables_mujeres", "MEMORIA_HIDROLOGICA_CAR_MUJERES_CON_COLECTOR.docx")),
    "refugio": (os.path.join(RAIZ, "entregables", "MEMORIA_HIDROLOGIA_MUJERES_VIOLENTADAS_2026_CON_COLECTOR.docx"),) * 2,
    "varones": (os.path.join(RAIZ, "entregables_varones", "MEMORIA_HIDROLOGICA_VARONES_CON_COLECTOR.docx"),) * 2,
}

if __name__ == "__main__":
    for k in (sys.argv[1:] or ARCH):
        a, b = ARCH[k]
        print(k, "->", os.path.relpath(b, RAIZ), ":", revisar(a, b, k))
