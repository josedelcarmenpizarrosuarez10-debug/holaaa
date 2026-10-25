"""Actualiza normas_biblioteca.json con la verificación hecha sobre los textos oficiales de insumos/normas/ (25-10-2026).

Cada dato verificado lleva el artículo, numeral o tabla exacta donde está y el archivo PDF. Lo que no se pudo verificar porque
falta el documento (EG-2013, Manual de Puentes, NTP 399.003, Chow, USBR, Wyly-Eaton, EPA SWMM) queda «por verificar».
Uso: python3 herramientas_normas/verificar_biblioteca.py   (idempotente)
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RUTA = os.path.join(AQUI, "..", "drenie_motor", "normas_biblioteca.json")

NORMAS = {
    "CE040": {"dispositivo": "R.M. N.° 126-2021-VIVIENDA (El Peruano, 24-04-2021), que reemplaza a la OS.060 Drenaje Pluvial Urbano",
              "archivo": "CE.040_DRENAJE_PLUVIAL_RM_126-2021-VIVIENDA.pdf"},
    "E060": {"dispositivo": "D.S. N.° 010-2009-VIVIENDA, edición SENCICO con NTP actualizadas", "archivo": "e.060-concreto-armado-sencico.pdf"},
    "E020": {"archivo": "Norma_E_020_CARGAS.pdf"},
    "IS010": {"nombre": "Norma Técnica IS.010 Instalaciones Sanitarias para Edificaciones del Reglamento Nacional de Edificaciones",
              "dispositivo": "D.S. N.° 011-2006-VIVIENDA, modificada por D.S. N.° 017-2012-VIVIENDA",
              "archivo": "IS.010_Instalaciones_Sanitarias_para_Edificaciones_DS_N__017-2012.pdf"},
    "MTC_HHD": {"dispositivo": "R.D. N.° 20-2011-MTC/14", "archivo": "MAN_11_HHD-2011.pdf"},
    "IS020": {"sigla": "IS.020", "nombre": "Norma Técnica IS.020 Tanques Sépticos del Reglamento Nacional de Edificaciones",
              "dispositivo": "D.S. N.° 011-2006-VIVIENDA", "archivo": "IS.020.pdf"},
    "OS080": {"sigla": "OS.080", "nombre": "Norma Técnica OS.080 Estaciones de Bombeo de Aguas Residuales del Reglamento Nacional de Edificaciones",
              "dispositivo": "D.S. N.° 011-2006-VIVIENDA", "archivo": "OS.080_Estaciones_de_bombeo_aguas_residuales.pdf"},
    "E050": {"sigla": "E.050", "nombre": "Norma Técnica E.050 Suelos y Cimentaciones del Reglamento Nacional de Edificaciones",
             "dispositivo": "", "archivo": "E.050_Suelos_y_Cimentaciones.pdf"},
    "REG_DRENAJE": {"sigla": "Reglamento de la Ley General de Drenaje Pluvial",
                    "nombre": "Reglamento del Decreto Legislativo N.° 1356, Ley General de Drenaje Pluvial",
                    "dispositivo": "D.S. N.° 009-2026-VIVIENDA (El Peruano, 29-05-2026), que deroga el D.S. N.° 016-2018-VIVIENDA",
                    "archivo": "REGLAMENTO_DRENAJE_PLUVIAL_2026.pdf"},
    "CIRIA": {"sigla": "CIRIA C753", "nombre": "CIRIA. The SuDS Manual, C753 (Londres, 2015): diseño de sistemas de drenaje sostenible "
              "(zanjas y pozos de infiltración, almacenamiento)", "dispositivo": ""},
}
# orden de las siglas nuevas antes de las referencias
ORDEN = ["CE040", "E060", "E020", "IS010", "IS020", "OS080", "E050", "REG_DRENAJE", "MTC_HHD", "MTC_PUENTES", "EG2013", "NTP341031",
         "NTP399003", "CHOW", "CHOW_HA", "EPA_SWMM", "APARICIO", "USBR", "WYLY", "CIRIA", "PROYECTISTA"]

V = "verificado"
DATOS = {
    "T": {"estado": V, "consideracion": "El período se escoge según el tipo de obra y el criterio de quien diseña (11.1); los caudales de "
          "precipitaciones de baja frecuencia son los de T ≥ 25 años (11.3), por el método racional en cuencas ≤ 3 km². Probabilidad anual 4 %."},
    "tc_min": {"estado": V, "ref": "Anexo I, numeral 1.2.3", "consideracion": "«El tiempo de concentración no debe ser menor que 10 minutos.»"},
    "registro_min": {"estado": V, "ref": "numeral 3.4", "consideracion": "Se recomienda un mínimo de 25 años de registro, incluyendo los años del "
                     "fenómeno El Niño."},
    "dick_peschke": {"estado": V, "ref": "numeral 3.8, ecuación 16", "consideracion": "Para duraciones menores de 1 hora o sin pluviógrafo: "
                     "Pd = P24h·(d/1440)^0.25; la intensidad es Pd entre la duración."},
    "riesgo": {"estado": V, "ref": "numeral 3.6, ecuación 1"},
    "ks_alfa": {"estado": V, "ref": "numeral 3.7 b), Tabla N.° 03", "consideracion": "D = máx |Fo(xm) − F(xm)| con Fo(xm) = 1 − m/(n+1) "
                "(datos de mayor a menor); se acepta si D < d crítico de la Tabla N.° 03 para el nivel de significancia adoptado (0.05)."},
    "Vmax": {"fuente": "MTC_HHD", "ref": "numeral 4.1, Tabla N.° 10 (concreto: 3.0 – 6.0 m/s)", "estado": V,
             "consideracion": "La CE.040 deja la velocidad máxima al proyectista según el material (17.8). Se adopta el límite inferior del rango "
             "del MTC para conductos revestidos de concreto, del lado seguro frente a la erosión."},
    "Vmin": {"ref": "numeral 17.7", "estado": V, "consideracion": "0.90 m/s en subcolectores y colectores con el caudal de diseño; si no se "
             "cumple, el profesional lo justifica. En las cunetas la autolimpieza se asegura con la pendiente mínima de 0.5 % (17.9)."},
    "n_cap": {"fuente": "CE040", "ref": "Anexo II, Tabla 1", "estado": V, "clase": "norma",
              "consideracion": "Cuneta de concreto paleteado n = 0.012, más 0.002 donde puede acumularse sedimento (0.014). Se adopta 0.015 para la "
              "capacidad por la rejilla y las juntas, del lado seguro."},
    "n_vel": {"fuente": "CE040", "ref": "Anexo II, Tabla 1", "estado": V, "clase": "criterio",
              "consideracion": "La Tabla 1 da 0.012 a 0.016 según el acabado; el proyectista adopta 0.013 (concreto liso) para la velocidad, con el "
              "límite de 3.0 m/s que ya es el inferior del rango admisible del MTC."},
    "S_canaleta": {"estado": V, "ref": "numeral 12.4", "consideracion": "Pendiente mínima de 1 % y diámetro mínimo de 0.10 m; la canaleta de "
                   "0.25 × 0.20 m lo cumple."},
    "D_montante_min": {"estado": V, "ref": "numeral 12.5", "consideracion": "Mínimo de norma 0.05 m; el proyectista usa siempre 4\" (0.10 m)."},
    "fy": {"fuente": "E060", "ref": "numeral 3.5.3.1 (NTP 341.031:2018, grado 60, fy = 420 MPa)", "estado": V},
    "rho_temp": {"estado": V, "ref": "numeral 9.7.2", "consideracion": "Barras corrugadas o malla con fy ≥ 420 MPa: 0.0018 del área bruta."},
    "s_max_temp": {"estado": V, "ref": "numeral 9.7.3"},
    "recub_suelo": {"valor": 7.5, "estado": V, "ref": "numeral 7.7.1 a)", "texto": "Recubrimiento mínimo, concreto colocado contra el suelo y "
                    "expuesto permanentemente a él", "consideracion": "75 mm. Las cunetas, cajas y pozas se vacían sobre solado: les "
                    "corresponde 7.7.1 b) (4 cm)."},
    "recub_expuesto": {"estado": V, "ref": "numeral 7.7.1 b)", "consideracion": "Concreto en contacto permanente con el suelo o la intemperie, "
                       "barras de 5/8\" y menores y mallas: 40 mm."},
    "hietograma": {"fuente": "MTC_HHD", "ref": "numeral 3.10.1, método del bloque alterno", "estado": V,
                   "consideracion": "Intensidades de la curva IDF para Δt, 2Δt, …; los incrementos se ordenan con el máximo al centro y los demás "
                   "alternando a la derecha y a la izquierda (Chow et al.). Se usa para la simulación dinámica (SWMM), la infiltración y el "
                   "bombeo, con bloques del tiempo de concentración (mínimo 10 min)."},
}
NUEVOS = [
    {"id": "tirante_max_conducto", "grupo": "Hidráulica", "texto": "Tirante máximo en conductos de sección no circular (tramos tapados)",
     "valor": 80, "unidad": "% de la altura libre", "clase": "norma", "fuente": "CE040", "ref": "numeral 17.6.2",
     "consideracion": "En los tramos tapados la cuneta trabaja como conducto cerrado: además del borde libre de 0.05 m, el tirante no pasa del "
     "80 % de la altura libre bajo la losa.", "estado": V},
    {"id": "evacuacion", "grupo": "Descargas", "texto": "Tipos de evacuación: gravedad, bombeo o mixta", "valor": "gravedad; bombeo; mixta",
     "unidad": "", "clase": "norma", "fuente": "CE040", "ref": "artículo 21 (21.2.1 a 21.2.3)",
     "consideracion": "Por gravedad siempre que se pueda; si no es posible, estación de bombeo (21.2.2) con otra fuente de energía prevista; "
     "mixta con válvula de retención cuando el receptor sube de nivel.", "estado": V},
    {"id": "detencion", "grupo": "Descargas", "texto": "Unidades de detención o retención", "valor": "volumen por tránsito en el reservorio",
     "unidad": "", "clase": "norma", "fuente": "CE040", "ref": "numerales 22.2 a 22.4",
     "consideracion": "Reducen el caudal pico que la infraestructura no puede evacuar; el volumen y el caudal atenuado se calculan por el "
     "tránsito de avenidas en el reservorio.", "estado": V},
    {"id": "infraestructura_verde", "grupo": "Descargas", "texto": "Infiltración y retención como estructuras complementarias",
     "valor": "permitida", "unidad": "", "clase": "norma", "fuente": "REG_DRENAJE", "ref": "artículos 6.1 y 8.2; Segunda Disposición "
     "Complementaria Final", "consideracion": "El sistema puede incluir retención, filtración e infiltración (infraestructura verde o azul). "
     "Mientras el MVCS no apruebe su norma, se tratan como estructuras complementarias de la CE.040 y su diseño se ampara en normativa "
     "internacional especializada (CIRIA C753).", "estado": V},
    {"id": "bombeo_pluvial", "grupo": "Bombeo", "texto": "Bombeo de aguas de lluvia en edificaciones", "valor": "automático, con la máxima intensidad",
     "unidad": "", "clase": "norma", "fuente": "IS010", "ref": "numerales 7.1 f) y 7.2",
     "consideracion": "La capacidad de las bombas se calcula con la máxima intensidad de lluvia; el volumen de almacenamiento, según la "
     "intensidad y frecuencia de lluvias; la elevación sigue lo de las cámaras de bombeo de la norma.", "estado": V},
    {"id": "bombas_numero", "grupo": "Bombeo", "texto": "Número y capacidad de las bombas", "valor": "2 alternadas, cada una con el gasto máximo",
     "unidad": "", "clase": "norma", "fuente": "IS010", "ref": "numeral 6.4 b) y c)",
     "consideracion": "Mínimo dos equipos de funcionamiento alternado, cada uno con el gasto máximo (capacidad total ≥ 150 %); tubería de "
     "descarga con válvula de interrupción y de retención; arranque por niveles, control manual y alarma de sobre nivel.", "estado": V},
    {"id": "camara_bombeo", "grupo": "Bombeo", "texto": "Cámara de bombeo", "valor": "permanencia ≤ 30 min; reserva; NPSH disponible − requerido ≥ 0.80 m",
     "unidad": "", "clase": "norma", "fuente": "OS080", "ref": "numerales 1 y 4",
     "consideracion": "La OS.080 alcanza a las estaciones de aguas pluviales: cámara de rejas a la entrada, fondo con pendiente a la succión, "
     "bomba de reserva, succión un diámetro mayor que la impulsión, válvulas de interrupción, retención y aire, control de niveles con "
     "alarma, rebose o grupo electrógeno.", "estado": V},
    {"id": "ciclo_bombas", "grupo": "Bombeo", "texto": "Volumen útil por arranques de la bomba", "valor": "V = Qb · Tmin / 4; Tmin = 10 min",
     "unidad": "m³", "clase": "referencia", "fuente": "PROYECTISTA", "ref": "", "consideracion": "Volumen entre los niveles de arranque y "
     "parada para no más de 6 arranques por hora (práctica de fabricantes de bombas sumergibles); se verifica además la permanencia ≤ 30 min "
     "de la OS.080.", "estado": "por_verificar"},
    {"id": "percolacion", "grupo": "Infiltración", "texto": "Test de percolación y clase de terreno", "valor": "rápido 0–4; medio 4–8; lento 8–12 min/cm",
     "unidad": "min por 1 cm", "clase": "norma", "fuente": "IS020", "ref": "artículo 17 a) y Anexo 1",
     "consideracion": "Seis o más agujeros de 0.30 × 0.30 m a la profundidad del sistema, saturación de 4 h (24 h salvo arenas). Con más de 12 "
     "min/cm el terreno no es apto: se plantea bombeo.", "estado": V},
    {"id": "pozo_absorcion", "grupo": "Infiltración", "texto": "Pozo de absorción (infiltración)", "valor": "D ≥ 1.0 m; 2 m en la capa filtrante; "
     "fondo ≥ 2 m sobre la napa; separación ≥ 6 m", "unidad": "", "clase": "norma", "fuente": "IS020", "ref": "artículos 20 y 21",
     "consideracion": "Área efectiva: la lateral del cilindro con el diámetro exterior (sin el fondo); muro de mampostería con juntas abiertas, "
     "relleno de grava de 1\" y tapa de inspección de 0.60 m.", "estado": V},
    {"id": "zanja_infiltracion", "grupo": "Infiltración", "texto": "Zanja de infiltración (percolación)", "valor": "ancho 0.45–0.90 m; profundidad "
     "≥ 0.60 m; ≥ 2 m sobre la napa; línea ≤ 30 m; ejes a ≥ 2 m", "unidad": "", "clase": "norma", "fuente": "IS020", "ref": "artículos 18 y 19",
     "consideracion": "Área útil: la mayor entre el fondo y las paredes laterales; grava de 1.5 a 5 cm y tubería PVC de 100 mm perforada con "
     "pendiente de 1.5 a 5 ‰; caja de inspección de 0.60 × 0.60 m al inicio.", "estado": V},
    {"id": "distancias_infiltracion", "grupo": "Infiltración", "texto": "Distancias mínimas del pozo o zanja de infiltración",
     "valor": "vivienda 6 m; pozo de agua 25 m; tubería de agua 10–15 m; curso de agua 10–15 m", "unidad": "m", "clase": "norma",
     "fuente": "IS020", "ref": "artículo 17 b), tabla de distancias mínimas", "consideracion": "La tabla es para efluentes de tanque séptico; "
     "para agua de lluvia se toma como mínimo prudente frente a cimentaciones, pozos y tuberías.", "estado": V},
    {"id": "tasa_infiltracion", "grupo": "Infiltración", "texto": "Tasa de infiltración de diseño", "valor": "f = (1 cm / t) / FS",
     "unidad": "m/h", "clase": "referencia", "fuente": "CIRIA", "ref": "capítulo 25, factores de seguridad para infiltración",
     "consideracion": "La tasa medida en el test de percolación (IS.020) se divide entre un factor de seguridad según el área drenada y las "
     "consecuencias de una falla (1.5 a 10; por defecto 3). La curva de la IS.020 (R en L/m²/día) es para efluente séptico que colmata el "
     "suelo y no se usa para lluvia.", "estado": "por_verificar"},
    {"id": "vaciado", "grupo": "Infiltración", "texto": "Tiempo de vaciado del almacenamiento de infiltración", "valor": "mitad del volumen en ≤ 24 h",
     "unidad": "h", "clase": "referencia", "fuente": "CIRIA", "ref": "capítulo 25", "consideracion": "Para que el sistema esté disponible para "
     "la siguiente tormenta.", "estado": "por_verificar"},
    {"id": "napa", "grupo": "Infiltración", "texto": "Nivel de la napa freática en el estudio de suelos", "valor": "obligatorio",
     "unidad": "", "clase": "norma", "fuente": "E050", "ref": "informe del EMS, «Nivel de la Napa Freática»",
     "consideracion": "El estudio de mecánica de suelos indica la napa con su fecha de medición; con napa alta la infraestructura debe ser "
     "compatible con el subdrenaje (CE.040, artículo 9).", "estado": V},
]
CUADROS_V = {"C_tabla1a": {"estado": V, "consideracion": "Valores para T = 25 años de la Tabla 1.a (Chow et al. 1994, tabla 15.1.1, estándares "
                                                         "de Austin): concreto/techo 0.88; asfáltico 0.86; zonas verdes planas 0–2 %: 0.29 "
                                                         "(buena), 0.34 (promedio), 0.40 (pobre)."}}
CUADROS_N = [
    {"id": "n_manning_ce040", "grupo": "Hidráulica", "titulo": "n de Manning para cunetas de calles y calzadas", "clase": "norma",
     "fuente": "CE040", "ref": "Anexo II, Tabla 1", "columnas": ["Tipo de cuneta o calzada", "n"],
     "filas": [["Cuneta de concreto con acabado paleteado", 0.012], ["Calzada de asfalto, textura suave", 0.013], ["Calzada de asfalto, textura rugosa", 0.016],
               ["Cuneta de concreto y calzada de asfalto, suave", 0.013], ["Cuneta de concreto y calzada de asfalto, rugoso", 0.015],
               ["Calzada de concreto, acabado", 0.014], ["Calzada de concreto, acabado escobillado", 0.016],
               ["Incremento en cunetas de pendiente pequeña con sedimento", 0.002]],
     "consideracion": "Referencia USDOT FHWA HEC-22 (2013).", "estado": V},
    {"id": "velocidades_mtc", "grupo": "Hidráulica", "titulo": "Velocidades máximas admisibles en conductos revestidos", "clase": "norma",
     "fuente": "MTC_HHD", "ref": "numeral 4.1, Tabla N.° 10", "columnas": ["Revestimiento", "V (m/s)"],
     "filas": [["Concreto", "3.0 – 6.0"], ["Ladrillo con concreto", "2.5 – 3.5"], ["Mampostería de piedra y concreto", "2.0"]],
     "consideracion": "Fuente citada por el MTC: HCANALES, Máximo Villón B.", "estado": V},
    {"id": "clases_terreno", "grupo": "Infiltración", "titulo": "Clasificación de los terrenos según el test de percolación", "clase": "norma",
     "fuente": "IS020", "ref": "artículo 17 a)", "columnas": ["Clase de terreno", "Tiempo para el descenso de 1 cm"],
     "filas": [["Rápido", "0 a 4 min"], ["Medio", "4 a 8 min"], ["Lento", "8 a 12 min"], ["No apto", "más de 12 min"]],
     "consideracion": "", "estado": V},
    {"id": "distancias_is020", "grupo": "Infiltración", "titulo": "Distancia mínima al sistema (m)", "clase": "norma", "fuente": "IS020",
     "ref": "artículo 17 b)", "columnas": ["Sistema", "Pozo de agua", "Tubería de agua", "Curso superficial", "Vivienda"],
     "filas": [["Campo de percolación", 25, 15, 10, 6], ["Pozo de absorción", 25, 10, 15, 6]],
     "consideracion": "Tabla para efluentes de tanque séptico; para agua de lluvia se toma como mínimo prudente.", "estado": V},
]


def main():
    b = json.load(open(RUTA, encoding="utf-8"))
    for k, v in NORMAS.items():
        b["normas"].setdefault(k, {"sigla": k, "nombre": "", "dispositivo": ""}).update(v)
    b["normas"] = {k: b["normas"][k] for k in ORDEN if k in b["normas"]} | {k: v for k, v in b["normas"].items() if k not in ORDEN}
    for d in b["datos"]:
        d.update(DATOS.get(d["id"], {}))
    ids = {d["id"] for d in b["datos"]}
    b["datos"] += [d for d in NUEVOS if d["id"] not in ids]
    for c in b["cuadros"]:
        c.update(CUADROS_V.get(c["id"], {}))
    idc = {c["id"] for c in b["cuadros"]}
    b["cuadros"] += [c for c in CUADROS_N if c["id"] not in idc]
    b["nota"] = ("Cada dato con su fuente. Verificado = cotejado con el texto oficial (PDF en insumos/normas/, 25-10-2026); por verificar = "
                 "falta el documento oficial o es una referencia técnica sin texto a la mano.")
    json.dump(b, open(RUTA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    t = b["datos"] + b["cuadros"]
    print("datos %d, cuadros %d, verificados %d, por verificar: %s" % (len(b["datos"]), len(b["cuadros"]), sum(1 for x in t if x["estado"] == V),
                                                                     ", ".join(x["id"] for x in t if x["estado"] != V)))


if __name__ == "__main__":
    main()
