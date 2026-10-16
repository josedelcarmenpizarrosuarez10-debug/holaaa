# -*- coding: utf-8 -*-
"""Registro de riesgos de la ejecución de la obra: MEJORAMIENTO DEL SERVICIO DE TRANSITABILIDAD VIAL INTERURBANA EN LA
VÍA DEPARTAMENTAL SM-107, TRAMO TINGO DE PONASA - SHAMBOYACU (CUI N.° 2673852).

Fuente única de datos para el Excel (matriz), el plano de ubicación y el Word del estudio.
Escalas de probabilidad e impacto y umbrales P x I del PMBOK (las mismas que usaban los formatos de la ex Directiva
N.° 012-2017-OSCE/CD); el nivel de impacto se obtiene del impacto más probable en costo y en plazo con los umbrales
de IMPACTO_COSTO e IMPACTO_PLAZO, de modo que el análisis cualitativo y el cuantitativo quedan amarrados.
Montos en soles a precio de obra (costo directo x 1.3865: gastos generales 10.5 %, utilidad 7 % e IGV 18 %).
"""
import json, os
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)          # carpeta gestion_riesgos
PROY = os.path.join(RAIZ, "proyectos", "SM-107_TINGO_DE_PONASA_SHAMBOYACU")
ENT = os.path.join(PROY, "entregables"); INS = os.path.join(PROY, "insumos"); CALC = os.path.join(ENT, "_calc")

# ------------------------------------------------------------------ datos del proyecto (FTE, resumen ejecutivo y S10)
P = {
    "nombre": "MEJORAMIENTO DEL SERVICIO DE TRANSITABILIDAD VIAL INTERURBANA EN LA VÍA DEPARTAMENTAL SM-107, TRAMO TINGO DE "
              "PONASA - SHAMBOYACU, DISTRITO DE SHAMBOYACU, PROVINCIA DE PICOTA, DEPARTAMENTO DE SAN MARTÍN",
    "cui": "2673852", "idea": "313790", "entidad": "Gobierno Regional San Martín - Dirección Regional de Transportes y Comunicaciones",
    "ue": "925 - Región San Martín - Transportes", "ubicacion": "Distrito de Shamboyacu, provincia de Picota, departamento de San Martín",
    "prog_ini": "19+343.39", "prog_fin": "44+693.39", "L_inv": 25.350, "L_fte": 24.70, "L_topo": 24.09,
    "CD": 88262797.61, "GG": 9267593.75, "UT": 6178395.83, "ST": 103708787.19, "IGV": 18667581.69, "PO": 122376368.88,
    "SUP": 4833866.57, "GEST": 2338964.14, "CCC": 647746.00, "ET": 2500000.00, "TOTAL": 132696945.59,
    "plazo": 720, "modalidad": "Administración indirecta - por contrata", "fuente_fin": "Recursos determinados",
    "imda_actual": 254, "imda_proy": 298, "poblacion": 11960, "fecha_ppto": "02/12/2024",
}
P["K"] = P["ST"] * 1.18 / P["CD"]                      # factor costo directo -> precio de obra
P["costo_dia"] = (P["GG"] * 1.18 + P["SUP"]) / P["plazo"]   # gastos generales + supervisión por día de ampliación
P["costo_dia_pct"] = P["costo_dia"] / P["PO"] * 100

PROB = [("Muy baja", 0.10), ("Baja", 0.30), ("Moderada", 0.50), ("Alta", 0.70), ("Muy alta", 0.90)]
IMP = [("Muy bajo", 0.05), ("Bajo", 0.10), ("Moderado", 0.20), ("Alto", 0.40), ("Muy alto", 0.80)]
# umbrales (límite superior de cada nivel) del impacto más probable
IMPACTO_COSTO = [0.001, 0.005, 0.015, 0.04]            # fracción del presupuesto de obra
IMPACTO_PLAZO = [7, 21, 45, 90]                        # días calendario
UMBRAL_ALTO, UMBRAL_MOD = 0.18, 0.05


def nivel_impacto(costo, dias):
    ic = sum(costo > u * P["PO"] for u in IMPACTO_COSTO); ip = sum(dias > u for u in IMPACTO_PLAZO)
    return max(ic, ip), ic, ip


def nivel_riesgo(pxi):
    return "ALTO" if pxi >= UMBRAL_ALTO - 1e-9 else ("MODERADO" if pxi >= UMBRAL_MOD - 1e-9 else "BAJO")


K = 1000.0
# campos: cod, categoria, riesgo (evento), causa, efecto, ubicacion, evidencia, p (indice 0-4),
#         costo (min, mp, max) S/, plazo (min, mp, max) días, ruta_critica, asignado, tipo de respuesta, acciones,
#         responsable, partida, alerta, momento
R = [
 dict(cod="R-01", pr=3, grupo="clima", cat="Clima y naturaleza", riesgo="Lluvias estacionales intensas (octubre a abril) que paralizan el movimiento de tierras, la pavimentación y los vaciados",
      causa="Clima cálido y húmedo con lluvias todo el año: 1,020 mm anuales en Tarapoto y 1,471 mm en Juanjuí (NOAA GHCN-Daily), con máximos en marzo y en octubre-noviembre; el plazo de 720 días abarca dos temporadas de lluvias.",
      efecto="Días no trabajables, capas granulares saturadas que se deben reprocesar, retraso de la ruta crítica.",
      ubic="Todo el tramo, 19+343 a 44+693", evid="FTE: lluvias intensas SI, nivel medio. Inventario: empozamientos y pérdida de material por escorrentía.",
      p=4, costo=(150*K, 400*K, 900*K), plazo=(10, 25, 60), rc=True, asig="Contratista", resp="Mitigar",
      acc="Cronograma valorizado con calendario climático: terraplenes, bases y carpeta en mayo-setiembre; drenaje provisional y bombeo; "
          "protección de capas terminadas; frentes alternos (alcantarillas, cunetas) en temporada de lluvias.",
      quien="Residente de obra / Supervisor", partida="Gastos generales del contratista; 1.04.02 Mantenimiento de tránsito temporal",
      alerta="Pronóstico y avisos meteorológicos del SENAMHI; lluvia > 30 mm/día; dos días seguidos sin trabajo en un frente.", momento="Ejecución (oct-abr)"),
 dict(cod="R-02", pr=1, grupo="clima", fr=0.4, cat="Clima y naturaleza", riesgo="Lluvias extraordinarias o anomalías climáticas (El Niño / La Niña) con desborde de quebradas y daños a la obra ejecutada",
      causa="Eventos de lluvia superiores a los de diseño, declarados por el ENFEN o con declaratoria de emergencia.",
      efecto="Daños en terraplenes, alcantarillas y accesos de puentes; ampliación de plazo con gastos generales.",
      ubic="Quebradas de los 5 puentes y sectores bajos 19+343 a 23+000", evid="FTE 18.3: el área ha sido afectada por desastres. Inventario: inundación 20+360 a 21+170.",
      p=1, costo=(300*K, 1200*K, 3500*K), plazo=(15, 30, 60), rc=True, asig="Entidad", resp="Transferir / Mitigar",
      acc="Exigir póliza Todo Riesgo Construcción (CAR) con cobertura de eventos de la naturaleza; plan de contingencias por lluvias; "
          "registro en el cuaderno de obra y comunicación inmediata para la ampliación de plazo.",
      quien="Entidad (DRTC) / Supervisor", partida="Póliza CAR del contratista; reserva de contingencia de la Entidad",
      alerta="Comunicado oficial del ENFEN; nivel de agua en las quebradas sobre la marca de alerta.", momento="Ejecución"),
 dict(cod="R-03", pr=1, grupo="clima", cat="Clima y naturaleza", riesgo="Crecidas de quebradas durante la construcción de estribos de los 5 puentes",
      causa="Demolición de estribos existentes y excavación bajo agua (806.94 m³ en cada puente de 40 m) en época de lluvias.",
      efecto="Inundación de excavaciones, arrastre de encofrados y ataguías, reprogramación de la subestructura.",
      ubic="Puentes Tingo de Ponasa 20+300, Barco 29+300, Paucarillo 37+870, Apangurayco 38+800, Chanchamayco 44+040",
      evid="S10 1.10: excavación bajo agua, encauzamiento de quebrada y desvío temporal en cada puente.",
      p=2, costo=(100*K, 350*K, 900*K), plazo=(7, 20, 45), rc=True, asig="Contratista", resp="Mitigar",
      acc="Programar cimentaciones y estribos en estiaje (junio-setiembre); ataguías y bombeo; desvío del cauce antes de excavar; "
          "monitoreo diario del nivel de agua.",
      quien="Residente / Especialista en puentes", partida="1.04.10 Desvío provisional de curso de agua; 1.10.0x.01.05 Encauzamiento de quebrada",
      alerta="Subida del nivel de la quebrada > 0.50 m en 24 h; lluvias en la cuenca alta.", momento="Ejecución de puentes"),
 dict(cod="R-04", pr=1, grupo="terreno", cat="Geotecnia", riesgo="Inestabilidad de taludes y deslizamientos durante los cortes en ladera",
      causa="Taludes altos (h = 20 a 30 m) en suelos limosos y arcillosos saturables; pendientes del entorno de hasta 40° (modelo digital).",
      efecto="Derrumbes sobre la plataforma, cortes adicionales, banquetas o muros no previstos, riesgo para el personal.",
      ubic="36+060 a 36+100 (h = 20 m, LI) y 37+520 a 37+780 (h = 30 m, LI); laderas 34+000 a 37+000 y 43+000 a 44+000",
      evid="Inventario: zonas críticas por inestabilidad de talud.",
      p=2, costo=(200*K, 700*K, 2000*K), plazo=(7, 20, 45), rc=True, asig="Compartido", resp="Mitigar",
      acc="Antes del inicio: verificar la estabilidad de cortes (factor de seguridad estático y seudoestático) y el diseño de muros en esos "
          "sectores; durante la obra: cortes por banquetas de arriba hacia abajo, drenaje de coronación, hitos de control de desplazamiento.",
      quien="Entidad (diseño) / Contratista (método de corte)", partida="1.05.02 a 1.05.04 Cortes; 1.08.03 Muros de contención",
      alerta="Grietas de tracción en la corona, surgencias de agua, desplazamiento de hitos > 2 cm.", momento="Antes del inicio y ejecución"),
 dict(cod="R-05", pr=2, grupo="otros", cat="Geotecnia", riesgo="Erosión y socavación de la plataforma y de los terraplenes en construcción",
      causa="Escorrentía sin control y bordes con desnivel de 2 a 5 m; drenaje transversal colmatado.",
      efecto="Pérdida de terraplén, reducción del ancho útil, reconstrucción de capas y protección adicional.",
      ubic="20+337 a 20+340; 34+766 a 34+786; 36+380 a 36+460; 39+380 a 39+840 (h = 3 a 5 m); 43+620 a 43+632",
      evid="Inventario: zonas críticas por erosión y alcantarillas colmatadas o semicolmatadas.",
      p=3, costo=(150*K, 500*K, 1200*K), plazo=(5, 15, 40), rc=False, asig="Contratista", resp="Mitigar",
      acc="Ejecutar primero los gaviones y la protección de pie en esos sectores; limpieza de alcantarillas y salidas antes del "
          "movimiento de tierras; protección temporal con geobolsas.",
      quien="Residente / Especialista en geotecnia", partida="1.08.04 Muros de gavión; 1.05.08 Geobolsas",
      alerta="Pérdida de material en el borde después de cada lluvia; socavación > 0.30 m al pie.", momento="Ejecución"),
 dict(cod="R-06", pr=2, grupo="terreno", cat="Clima y naturaleza", riesgo="Saturación de terraplenes por inundación de arrozales, canales de riego y empozamientos",
      causa="La vía cruza zonas de cultivo de arroz con riego por inundación y sectores sin elemento de descarga.",
      efecto="Subrasante saturada, mayor mejoramiento de suelos, retraso de la compactación.",
      ubic="20+360 a 21+170; 22+270; 22+800 a 22+960; 26+924; 34+954; 40+380; 43+660",
      evid="Inventario: inundación por cultivos de arroz y empozamientos sin descarga; cuadro 8 propone alcantarillas en 26+924, 34+954, 40+380 y 43+660.",
      p=3, costo=(200*K, 600*K, 1500*K), plazo=(10, 20, 45), rc=False, asig="Compartido", resp="Mitigar",
      acc="Acordar con la junta y comisiones de usuarios de riego los turnos y cortes de agua en los frentes; subdrenaje y geotextil; "
          "construir primero las alcantarillas de alivio proyectadas.",
      quien="Entidad (coordinación) / Contratista (ejecución)", partida="1.05.06 Mejoramiento de suelos; 1.05.09 Geotextil; 1.05.11 a 1.05.13 Subdrenaje",
      alerta="Lámina de agua en los arrozales colindantes; humedad de la subrasante sobre la óptima + 2 %.", momento="Ejecución"),
 dict(cod="R-07", pr=1, grupo="terreno", cat="Geotecnia", riesgo="Subrasante de menor capacidad de soporte que la prevista en el expediente",
      causa="Suelos limosos y arcillosos variables; exploración con espaciamiento insuficiente.",
      efecto="Mayor volumen de mejoramiento de suelos y geomalla (mayores metrados).",
      ubic="Sectores de terreno natural y material de préstamo expuesto", evid="Inventario 10.2: terreno natural limoso y arcilloso. S10: mejoramiento 59,801 m³.",
      p=2, costo=(490*K, 1220*K, 2450*K), plazo=(10, 20, 40), rc=False, asig="Entidad", resp="Mitigar",
      acc="Completar calicatas y ensayos CBR cada 500 m antes de la convocatoria; definir criterios de reemplazo en el expediente.",
      quien="Entidad (expediente) / Supervisor", partida="1.05.06 Mejoramiento de suelos; 1.05.07 Geomalla",
      alerta="CBR de campo menor al de diseño en dos sectores consecutivos.", momento="Antes de la convocatoria"),
 dict(cod="R-08", pr=0, grupo="terreno", cat="Insumos y canteras", riesgo="Cantera insuficiente, sin calidad o sin autorización, con mayor distancia de transporte",
      causa="Unos 423,600 m³ de material granular (terraplén, mejoramiento, subbase y base) dependen de canteras de río; la distancia media es ~31 km.",
      efecto="Cada kilómetro adicional de transporte equivale a cerca de 0.75 % del presupuesto de obra; retraso en la producción de agregados.",
      ubic="Cantera de río (4.50 ha) y accesos (2.50 km)", evid="S10 1.07.02 Transporte de material granular > 1 km; 1.04.07 y 1.04.08 Cantera.",
      p=2, costo=(920*K, 2770*K, 7380*K), plazo=(15, 30, 60), rc=True, asig="Entidad", resp="Evitar",
      acc="Antes de convocar: ensayos de calidad y cálculo de potencia, autorización de la municipalidad y de la ANA para extracción en cauce, "
          "y una cantera alternativa con su distancia.",
      quien="Entidad (DRTC)", partida="1.04.07, 1.04.08 Cantera; 1.07 Transporte",
      alerta="Potencia útil menor al 120 % del volumen requerido; observación de la autoridad.", momento="Antes de la convocatoria"),
 dict(cod="R-09", pr=0, grupo="inicio", cat="Permisos", riesgo="Demora en autorizaciones de uso de agua y de extracción de material de cauce",
      causa="Trámites ante la Autoridad Local del Agua y la municipalidad no iniciados en la fase de formulación.",
      efecto="Paralización de la producción de agregados, del riego y de los vaciados.",
      ubic="Fuente de agua (acceso 1.70 km) y cantera de río", evid="S10 1.04.09 Acceso a fuente de agua; 1.04.08 Cantera de río.",
      p=2, costo=(20*K, 60*K, 150*K), plazo=(15, 30, 60), rc=True, asig="Entidad", resp="Evitar",
      acc="Tramitar las autorizaciones antes del inicio de obra y entregarlas al contratista con el expediente.",
      quien="Entidad (DRTC)", partida="—", alerta="Autorización no emitida 30 días antes del inicio.", momento="Antes del inicio"),
 dict(cod="R-10", pr=1, grupo="inicio", cat="Social y predios", riesgo="Falta de libre disponibilidad del terreno para el ensanche de la plataforma",
      causa="El ancho pasa de 4.50-6.00 m a 7.00 m más cunetas; derecho de vía de 20 m inexistente; viviendas, cercos y cultivos en el borde.",
      efecto="Frentes detenidos, compensaciones, rediseño de cunetas y del eje en zonas urbanas.",
      ubic="Tingo de Ponasa 19+343 a 19+800; Aypena 21+940; Nuevo América 26+270; Leoncio Prado 28+080; San Antonio 31+420; Huañipo 33+780; "
           "Paucar 38+020; Alfonso Ugarte 38+730; Shamboyacu 44+300 a 44+693",
      evid="FTE 11: acta de libre disponibilidad del terreno. Resumen ejecutivo: derecho de vía de 20 m como mínimo con proyecto.",
      p=3, costo=(100*K, 400*K, 1200*K), plazo=(15, 30, 90), rc=True, asig="Entidad", resp="Evitar",
      acc="Catastro de afectaciones por progresiva; actas de libre disponibilidad firmadas; evaluar el PACRI y el saneamiento físico-legal "
          "(Ley N.° 30025) antes de la convocatoria.",
      quien="Entidad (DRTC) / Municipalidades", partida="Fuera del presupuesto de obra (gestión de la Entidad)",
      alerta="Predio sin acta a 60 días de su frente de trabajo.", momento="Antes de la convocatoria"),
 dict(cod="R-11", pr=1, grupo="inicio", cat="Interferencias", riesgo="Interferencias con redes eléctricas, de agua potable y de telecomunicaciones",
      causa="73 postes a reubicar; pases de agua potable y tuberías de PVC bajo la vía.",
      efecto="Cortes de servicio, reclamos, espera de la concesionaria, frentes detenidos.",
      ubic="Pase de agua potable 22+425; PVC 21\" 25+715; PVC 6\" 34+688; postes en las 9 localidades",
      evid="S10 1.04.12 Reubicación de postes (73 und); inventario 11.3.",
      p=3, costo=(50*K, 200*K, 500*K), plazo=(10, 20, 45), rc=True, asig="Entidad", resp="Mitigar",
      acc="Factibilidad y presupuesto aprobados por la concesionaria eléctrica y las JASS o EPS antes del inicio; cronograma de cortes programados.",
      quien="Entidad / Contratista", partida="1.04.12 Reubicación de postes", alerta="Concesionaria sin respuesta a 30 días.", momento="Antes del inicio"),
 dict(cod="R-12", pr=1, grupo="gestion", cat="Social y predios", riesgo="Afectación de canales y cruces de riego con reclamos de los agricultores",
      causa="6 cruces de canal, un canal paralelo (31+100 a 31+920) y alcantarillas compartidas con el riego.",
      efecto="Corte del riego de arrozales, reclamos, paralización de frentes, indemnizaciones.",
      ubic="Cruces 32+578, 35+950, 36+120, 37+400, 37+794, 38+370; canal 31+100 a 31+920",
      evid="Inventario 11.1 y 11.3: cruces de canal de regadío TMC 72\" y de concreto.",
      p=2, costo=(50*K, 150*K, 400*K), plazo=(5, 15, 30), rc=False, asig="Compartido", resp="Mitigar",
      acc="Plan de trabajo con la comisión de regantes; ejecutar cada cruce fuera de la campaña de riego o con derivación temporal.",
      quien="Entidad (relacionamiento) / Contratista", partida="1.08.01 Alcantarillas TMC; 1.11.08 Plan de gestión social",
      alerta="Queja formal de la comisión de regantes; caudal cortado > 24 h.", momento="Ejecución"),
 dict(cod="R-13", pr=1, grupo="gestion", cat="Social y predios", riesgo="Conflictos sociales y paralizaciones de la población",
      causa="Expectativas de empleo local, polvo, ruido, accesos a viviendas y afectaciones de predios.",
      efecto="Paralización de frentes, reprogramación, compromisos adicionales.",
      ubic="Localidades del tramo", evid="S10 1.11.08 Plan de gestión social.",
      p=2, costo=(50*K, 200*K, 600*K), plazo=(5, 15, 45), rc=True, asig="Compartido", resp="Mitigar",
      acc="Relacionamiento comunitario durante todo el plazo, oficina de atención de quejas, contratación de mano de obra local, riego para polvo en zonas pobladas.",
      quien="Entidad / Contratista (especialista social)", partida="1.11.08 Plan de gestión social; 1.11.04 Riego para polvo",
      alerta="Actas de reclamo sin respuesta; convocatoria a paro.", momento="Antes del inicio y ejecución"),
 dict(cod="R-14", pr=0, grupo="inicio", cat="Permisos", riesgo="Hallazgos arqueológicos o falta del instrumento de intervención arqueológica aprobado",
      causa="Cortes, canteras, DME y ensanches en zonas que pueden tener restos arqueológicos; el proyecto contempla un plan de monitoreo arqueológico.",
      efecto="Paralización de frentes por el Ministerio de Cultura hasta el rescate o la liberación.",
      ubic="Cortes, canteras, DME y ensanches", evid="S10 1.12.01 Plan y monitoreo arqueológico.",
      p=1, costo=(20*K, 80*K, 300*K), plazo=(10, 30, 90), rc=True, asig="Entidad", resp="Evitar",
      acc="Tramitar ante el Ministerio de Cultura el instrumento que corresponda (Reglamento de Intervenciones Arqueológicas, D.S. N.° 011-2022-MC) "
          "antes del inicio, incluidas las áreas auxiliares.",
      quien="Entidad (DRTC)", partida="1.12.01 Plan y monitoreo arqueológico", alerta="Hallazgo fortuito registrado por el arqueólogo.", momento="Antes del inicio"),
 dict(cod="R-15", pr=0, grupo="inicio", cat="Permisos", riesgo="Demora o condicionamiento de la certificación ambiental",
      causa="La FTE señala que se requiere estudio de impacto ambiental; sin certificación no se puede iniciar la obra.",
      efecto="Inicio postergado o cambios del Plan de Manejo Ambiental.",
      ubic="Todo el proyecto y áreas auxiliares", evid="FTE 11 y 21; S10 1.11 Plan de manejo ambiental.",
      p=2, costo=(30*K, 100*K, 300*K), plazo=(30, 60, 120), rc=True, asig="Entidad", resp="Evitar",
      acc="Obtener la certificación ambiental de la autoridad competente del SEIA (Ley N.° 27446) antes de convocar; compatibilizar el PMA con el presupuesto.",
      quien="Entidad (DRTC)", partida="1.11 Plan de manejo ambiental", alerta="Observaciones de la autoridad sin levantar.", momento="Antes de la convocatoria"),
 dict(cod="R-16", pr=1, grupo="inicio", cat="Expediente técnico", riesgo="Deficiencias del expediente técnico (metrados, diseños, estudios básicos)",
      causa="Información de campo o de diseño incompleta o desactualizada (topografía, estudios básicos, metrados) que obliga a ajustar el expediente durante la obra.",
      efecto="Adicionales, deductivos, consultas y controversias; mayor plazo.",
      ubic="Todo el expediente", evid="Expediente técnico del proyecto.",
      p=3, costo=(500*K, 1500*K, 4000*K), plazo=(10, 25, 60), rc=True, asig="Entidad", resp="Evitar",
      acc="Revisión integral y compatibilización del expediente antes de convocar; "
          "en solo construcción, el contratista revisa el expediente e informa los riesgos al supervisor.",
      quien="Entidad (DRTC) / Proyectista", partida="Expediente técnico", alerta="Consulta de obra que revela incompatibilidad.", momento="Antes de la convocatoria"),
 dict(cod="R-17", pr=3, grupo="otros", cat="Económico", riesgo="Variación de precios de insumos críticos (asfalto, combustible, acero, TMC)",
      causa="El cemento asfáltico (6.5 % de la obra), el transporte (29.0 %) y las vigas metálicas dependen de precios internacionales.",
      efecto="Mayor costo vía reajuste de precios; presión sobre el financiamiento.",
      ubic="Todo el proyecto", evid="S10: 1.06.02.03 Cemento asfáltico; 1.07 Transporte; 1.10 Vigas metálicas 84.49 t por puente.",
      p=3, costo=(400*K, 1200*K, 3000*K), plazo=(0, 0, 0), rc=False, asig="Entidad", resp="Aceptar / Mitigar",
      acc="Reajuste por fórmulas polinómicas según el reglamento; previsión presupuestal multianual; abastecimiento anticipado de asfalto.",
      quien="Entidad (DRTC) / Oficina de Presupuesto", partida="Reajustes de precios", alerta="Índices unificados INEI con alza > 5 % en el trimestre.", momento="Ejecución"),
 dict(cod="R-18", pr=1, grupo="gestion", cat="Insumos y canteras", riesgo="Retraso en el suministro de materiales de importación o fabricación especial",
      causa="Cemento asfáltico, TMC MP-68, vigas metálicas (84.49 t en cada puente de 40 m), neoprenos y geosintéticos con plazos largos.",
      efecto="Frentes detenidos, puentes fuera de secuencia.",
      ubic="Puentes y pavimento", evid="S10 1.08.01.12 a 14 (TMC); 1.10.01.04 y 1.10.02.04 (vigas metálicas).",
      p=2, costo=(50*K, 150*K, 400*K), plazo=(7, 20, 45), rc=True, asig="Contratista", resp="Mitigar",
      acc="Plan de compras en el primer mes; fabricación de vigas con inspección en taller; stock mínimo de asfalto y TMC.",
      quien="Contratista (logística)", partida="Costos del contratista", alerta="Orden de compra no colocada en la fecha del plan.", momento="Inicio y ejecución"),
 dict(cod="R-19", pr=1, grupo="gestion", cat="Ejecución", riesgo="Falla o insuficiencia de equipos (planta de asfalto, chancadora, compactación)",
      causa="Zona alejada de talleres; transporte de equipo por la PE-5N.",
      efecto="Baja producción y retraso del pavimento.",
      ubic="Planta y frentes", evid="S10 1.01.03 Movilización de equipo y maquinaria pesada.",
      p=2, costo=(50*K, 200*K, 500*K), plazo=(5, 15, 30), rc=True, asig="Contratista", resp="Mitigar",
      acc="Equipo de respaldo, mantenimiento preventivo y repuestos críticos en obra.", quien="Contratista", partida="Costos del contratista",
      alerta="Disponibilidad mecánica < 85 %.", momento="Ejecución"),
 dict(cod="R-20", pr=1, grupo="otros", cat="Seguridad", riesgo="Accidentes de tránsito y atropellos en la vía en servicio durante la obra",
      causa="IMD de 254 veh/día, un carril, desvíos, maquinaria y peatones en 9 localidades.",
      efecto="Víctimas, responsabilidad civil y penal, paralización del frente.",
      ubic="Todo el tramo, en especial las localidades", evid="FTE: IMDA 254 veh/día. S10 1.04.02 Mantenimiento de tránsito temporal y seguridad vial.",
      p=2, costo=(20*K, 100*K, 500*K), plazo=(1, 5, 20), rc=False, asig="Contratista", resp="Mitigar / Transferir",
      acc="Plan de manejo de tránsito aprobado, controladores, señalización transitoria, horarios; seguro de responsabilidad civil y SCTR.",
      quien="Contratista (prevencionista)", partida="1.04.02 Mantenimiento de tránsito; 1.02.03 Señalización transitoria",
      alerta="Incidente o casi accidente registrado.", momento="Ejecución"),
 dict(cod="R-21", pr=0, grupo="otros", cat="Seguridad", riesgo="Accidentes de trabajo graves (izaje de vigas, trabajo en agua, excavaciones, maquinaria)",
      causa="Montaje de vigas metálicas, excavación bajo agua y cortes altos.",
      efecto="Lesiones o fatalidades, paralización por la autoridad de trabajo.",
      ubic="Puentes y cortes en ladera", evid="S10 1.02 Seguridad y salud ocupacional; 1.10 Montaje de estructuras metálicas.",
      p=1, costo=(30*K, 150*K, 600*K), plazo=(3, 10, 30), rc=False, asig="Contratista", resp="Mitigar / Transferir",
      acc="Plan de seguridad y salud en el trabajo (Ley N.° 29783 y D.S. N.° 011-2019-TR), procedimientos de izaje, permisos de trabajo de alto riesgo, SCTR.",
      quien="Contratista (prevencionista)", partida="1.02 Seguridad y salud ocupacional", alerta="Acto o condición subestándar repetida.", momento="Ejecución"),
 dict(cod="R-22", pr=0, grupo="clima", fr=0.4, cat="Clima y naturaleza", riesgo="Sismo de intensidad moderada a alta durante la obra",
      causa="Actividad sísmica de la región nororiental.",
      efecto="Daños a estructuras en construcción y a taludes; paralización.",
      ubic="Todo el tramo", evid="FTE 18.3: sismos SI, nivel bajo.",
      p=0, costo=(50*K, 300*K, 1500*K), plazo=(5, 15, 45), rc=True, asig="Entidad", resp="Aceptar / Transferir",
      acc="Póliza CAR; puentes diseñados con el Manual de Puentes del MTC; plan de respuesta ante emergencias.",
      quien="Entidad / Contratista", partida="Póliza CAR; 1.02.05 Recursos para emergencias", alerta="Reporte del IGP de sismo sentido en la zona.", momento="Ejecución"),
 dict(cod="R-23", pr=1, grupo="inicio", cat="Económico", riesgo="Retraso en el financiamiento o en los pagos de valorizaciones",
      causa="Fuente de recursos determinados (canon, FONCOR) sujeta a variaciones; inversión alta concentrada en 24 meses.",
      efecto="Ritmo de obra menor, paralización y reconocimiento de gastos generales.",
      ubic="Todo el proyecto", evid="FTE 20: recursos determinados. Resumen ejecutivo: canon, FONCOR, RDR.",
      p=2, costo=(100*K, 400*K, 1500*K), plazo=(10, 30, 90), rc=True, asig="Entidad", resp="Mitigar",
      acc="Certificación y previsión presupuestal multianual antes de convocar; cronograma de desembolsos alineado al calendario de avance.",
      quien="Entidad (Gerencia de Presupuesto)", partida="—", alerta="Valorización impaga a 30 días.", momento="Antes de la convocatoria y ejecución"),
 dict(cod="R-24", pr=1, grupo="gestion", cat="Gestión del contrato", riesgo="Demoras en la absolución de consultas, aprobación de prestaciones adicionales y decisiones de la Entidad",
      causa="Volumen de consultas técnicas durante la obra; designación tardía de la supervisión.",
      efecto="Frentes detenidos, ampliaciones de plazo y controversias.",
      ubic="Todo el proyecto", evid="—",
      p=2, costo=(50*K, 150*K, 500*K), plazo=(7, 20, 45), rc=True, asig="Entidad", resp="Mitigar",
      acc="Comité de gestión de riesgos; plazos internos de respuesta; supervisión contratada antes del inicio; "
          "junta de prevención y resolución de disputas cuando corresponda.",
      quien="Entidad (DRTC)", partida="—", alerta="Consulta sin respuesta en el plazo del reglamento.", momento="Ejecución"),
 dict(cod="R-25", pr=1, grupo="inicio", cat="Ambiental", riesgo="Áreas de depósito de material excedente (DME) insuficientes",
      causa="La obra genera cerca de 298,000 m³ de material excedente que deben disponerse en DME autorizados y cercanos a la vía.",
      efecto="DME adicionales, mayor transporte, observaciones ambientales.",
      ubic="DME del proyecto", evid="S10 1.04.04 Habilitación de DME; 1.11.01.01 Acomodo de material excedente.",
      p=4, costo=(300*K, 900*K, 2000*K), plazo=(10, 20, 45), rc=True, asig="Entidad", resp="Evitar",
      acc="Identificar DME con capacidad suficiente (unas 6 a 7.5 ha con 4 a 5 m de altura), con autorización del propietario y ubicación aprobada en el estudio ambiental.",
      quien="Entidad (expediente) / Especialista ambiental", partida="1.04.03, 1.04.04, 1.11.01 DME",
      alerta="DME al 70 % de su capacidad.", momento="Antes de la convocatoria"),
 dict(cod="R-26", pr=0, grupo="otros", cat="Ambiental", riesgo="Contaminación de quebradas y suelos (sedimentos, derrames de asfalto y combustible)",
      causa="Trabajos en cauce en 5 puentes, planta de asfalto y patio de máquinas.",
      efecto="Sanción ambiental, paralización, remediación.",
      ubic="Puentes, planta y patio de máquinas", evid="S10 1.11.02 Residuos; 1.11.10 Monitoreo de calidad de agua (2 und).",
      p=1, costo=(30*K, 100*K, 400*K), plazo=(3, 10, 30), rc=False, asig="Contratista", resp="Mitigar",
      acc="Barreras de sedimentos, kits antiderrame, impermeabilización de la zona de combustibles, monitoreo de agua por puente.",
      quien="Contratista (especialista ambiental)", partida="1.11 Plan de manejo ambiental", alerta="Turbidez aguas abajo mayor que aguas arriba.", momento="Ejecución"),
 dict(cod="R-27", pr=1, grupo="gestion", cat="Ejecución", riesgo="Interrupción prolongada del tránsito y del acceso a las localidades",
      causa="No existe vía alterna; demolición y reconstrucción de 5 puentes en el mismo eje.",
      efecto="Aislamiento de centros poblados, reclamos, exigencia de puentes provisionales.",
      ubic="Puentes 20+300, 29+300, 37+870, 38+800, 44+040", evid="S10: desvíos temporales en cada puente; 1.04.11 Desvío temporal durante la ejecución.",
      p=2, costo=(30*K, 120*K, 300*K), plazo=(3, 10, 25), rc=False, asig="Contratista", resp="Mitigar",
      acc="Desvíos con badén o puente modular provisional en los puentes de 40 m; demoler el puente existente solo con el desvío habilitado.",
      quien="Contratista / Supervisor", partida="1.04.11 Desvío temporal; desvíos de cada puente", alerta="Desvío intransitable después de una lluvia.", momento="Ejecución de puentes"),
 dict(cod="R-28", pr=0, grupo="otros", cat="Ejecución", riesgo="Calidad deficiente de la carpeta asfáltica o del concreto",
      causa="Colocación con lluvia, temperatura de la mezcla por distancia de transporte, curado insuficiente.",
      efecto="Rechazo y reconstrucción, mayor plazo.",
      ubic="Pavimento y estructuras", evid="S10 1.06.02 MAC 10,469 m³; 1.07.05 y 1.07.06 Transporte de mezcla.",
      p=1, costo=(100*K, 400*K, 1200*K), plazo=(5, 15, 40), rc=False, asig="Contratista", resp="Mitigar",
      acc="Plan de calidad, tramo de prueba, laboratorio en obra, no colocar mezcla con lluvia ni sobre base húmeda.",
      quien="Contratista / Supervisor", partida="Costos del contratista", alerta="Ensayo fuera de especificación.", momento="Ejecución"),
 dict(cod="R-29", pr=1, grupo="otros", cat="Seguridad", riesgo="Enfermedades transmitidas por vectores (dengue) y emergencias sanitarias en el personal",
      causa="Zona endémica de selva; campamento con agua estancada.",
      efecto="Ausentismo y menor rendimiento.",
      ubic="Campamento y frentes", evid="S10 1.02.05 Recursos para respuesta ante emergencias.",
      p=2, costo=(20*K, 60*K, 200*K), plazo=(3, 10, 30), rc=False, asig="Contratista", resp="Mitigar",
      acc="Plan de salud, control de vectores en campamento, repelentes y coordinación con el establecimiento de salud de Tingo de Ponasa.",
      quien="Contratista", partida="1.02 Seguridad y salud", alerta="Casos febriles en el personal.", momento="Ejecución"),
 dict(cod="R-30", pr=1, grupo="otros", cat="Social y predios", riesgo="Conflictos laborales y presión de gremios de construcción civil",
      causa="Obra de gran monto en zona con oferta limitada de mano de obra calificada.",
      efecto="Paralizaciones y amenazas al personal.",
      ubic="Frentes de obra", evid="—",
      p=1, costo=(20*K, 100*K, 300*K), plazo=(3, 10, 30), rc=False, asig="Contratista", resp="Mitigar",
      acc="Registro de trabajadores, contratación local transparente, coordinación con la Policía Nacional y la autoridad de trabajo.",
      quien="Contratista", partida="1.11.08.03 Contratación de mano de obra", alerta="Presencia de grupos ajenos en el frente.", momento="Ejecución"),
 dict(cod="R-31", pr=1, grupo="otros", cat="Ejecución", riesgo="Robo y vandalismo de materiales, señales y equipos",
      causa="Frentes dispersos en 25 km.", efecto="Reposición y retrasos menores.",
      ubic="Almacenes y frentes", evid="—",
      p=2, costo=(20*K, 60*K, 150*K), plazo=(1, 3, 10), rc=False, asig="Contratista", resp="Mitigar / Transferir",
      acc="Vigilancia, inventario semanal, seguro de equipos.", quien="Contratista", partida="1.01.01 Campamento y almacenes",
      alerta="Faltante en inventario.", momento="Ejecución"),
 dict(cod="R-32", pr=1, grupo="otros", cat="Clima y naturaleza", riesgo="Incendios y quemas agrícolas en época seca",
      causa="Quema de rastrojos en la campaña agrícola (julio a setiembre).", efecto="Humo, baja visibilidad y daño a señales o geosintéticos.",
      ubic="Sectores agrícolas", evid="—",
      p=1, costo=(5*K, 20*K, 80*K), plazo=(1, 2, 5), rc=False, asig="Contratista", resp="Aceptar",
      acc="Coordinación con las municipalidades y los agricultores; extintores en frentes.", quien="Contratista", partida="—",
      alerta="Focos de quema cerca de la vía.", momento="Estiaje"),
 dict(cod="R-33", pr=0, grupo="gestion", cat="Ejecución", riesgo="Falla de los puentes existentes por el paso de equipo pesado antes de su reemplazo",
      causa="Puentes antiguos de viga y losa, con señal de carga máxima de 30 t en el puente Barco.",
      efecto="Colapso o daño, corte de la vía, accidentes.",
      ubic="Puentes existentes 20+300, 29+329, 37+960, 38+919, 44+149", evid="Inventario: señales 'Puente Barco carga máx. 30.0 TN' (29+318 y 29+380).",
      p=1, costo=(50*K, 250*K, 800*K), plazo=(5, 20, 45), rc=True, asig="Contratista", resp="Evitar",
      acc="Evaluación de la capacidad de carga antes del inicio; prohibir el paso de equipo con cargas superiores; transportar el equipo pesado por desvío o vado.",
      quien="Contratista / Supervisor", partida="1.04.02 Mantenimiento de tránsito", alerta="Fisuras o deflexión visible en el tablero.", momento="Inicio y ejecución"),
 dict(cod="R-34", pr=0, grupo="terreno", cat="Expediente técnico", riesgo="Cambio de diseño de puentes por condiciones de cauce, socavación o cimentación distintas",
      causa="Puentes de 12 a 40 m en cauces con socavación y suelos de fundación variables.",
      efecto="Mayores profundidades de cimentación o luces, adicionales y plazo.",
      ubic="Puentes Tingo de Ponasa 20+300 y Barco 29+300", evid="S10 1.10 Puentes; inventario vial 11.2 (puentes existentes).",
      p=1, costo=(200*K, 800*K, 2500*K), plazo=(15, 30, 90), rc=True, asig="Entidad", resp="Evitar",
      acc="Verificar por puente el estudio hidrológico, hidráulico, de socavación y geotécnico (Manual de Puentes del MTC) antes de convocar.",
      quien="Entidad / Proyectista", partida="1.10 Puentes", alerta="Perforación con estrato de apoyo más profundo que el de diseño.", momento="Antes de la convocatoria"),
]

OPORT = [
 dict(cod="O-01", oport="Aprovechar el material de corte como relleno de terraplén", causa="47,772 m³ de corte en material suelto y 3,337 m³ en roca.",
      p=2, beneficio=(100*K, 300*K, 700*K), plazo=(0, 0, 0), resp="Explotar", acc="Clasificar el material de corte y usar el apto en terraplenes; reduce préstamo y transporte.",
      quien="Contratista / Supervisor"),
 dict(cod="O-02", oport="Concentrar puentes, terraplenes y carpeta en el estiaje", causa="Las lluvias bajan en junio-agosto.",
      p=3, beneficio=(0, 0, 0), plazo=(5, 15, 30), resp="Mejorar", acc="Cronograma con hitos de estiaje y frentes paralelos; reduce la exposición a R-01 y R-03.",
      quien="Contratista / Entidad"),
 dict(cod="O-03", oport="Compra anticipada de cemento asfáltico y alcantarillas TMC", causa="Precios volátiles y plazos de entrega largos.",
      p=1, beneficio=(50*K, 150*K, 400*K), plazo=(0, 5, 15), resp="Mejorar", acc="Contratos de suministro al inicio de obra con entregas programadas.",
      quien="Contratista"),
]


CONCURRENCIA = 0.25    # dentro de un grupo, los retrasos se superponen: suma el mayor y el 25 % de los demás
GRUPOS = {"inicio": "Antes del inicio (permisos, predios, interferencias, expediente, financiamiento, DME)",
          "clima": "Lluvias, crecidas y sismo", "terreno": "Terreno, canteras y diseño de puentes",
          "gestion": "Gestión, suministros y relación con la población", "otros": "Otros"}
FACTOR = {"Entidad": 1.0, "Compartido": 0.5, "Contratista": 0.0}


def calcular():
    for r in R:
        r.setdefault("fr", 1.0)
        r["P"] = PROB[r["p"]][1]; r["P_txt"] = PROB[r["p"]][0]
        ni, ic, ip = nivel_impacto(r["costo"][1], r["plazo"][1])
        r["i"], r["ic"], r["ip"] = ni, ic, ip
        r["I"] = IMP[ni][1]; r["I_txt"] = IMP[ni][0]
        r["PxI"] = round(r["P"] * r["I"], 4); r["nivel"] = nivel_riesgo(r["PxI"])
        r["Pr"] = PROB[r["pr"]][1]; r["Pr_txt"] = PROB[r["pr"]][0]
        r["PxIr"] = round(r["Pr"] * r["I"], 4); r["nivel_r"] = nivel_riesgo(r["PxIr"])
        r["costo_pct"] = tuple(v / P["PO"] * 100 for v in r["costo"])
        r["c_media"] = sum(r["costo"]) / 3.0; r["t_media"] = sum(r["plazo"]) / 3.0
        r["EMV_costo"] = r["P"] * r["c_media"]; r["EMV_plazo"] = r["P"] * r["t_media"]
        r["EMV_costo_r"] = r["Pr"] * r["c_media"]; r["EMV_plazo_r"] = r["Pr"] * r["t_media"]
    for o in OPORT:
        o["beneficio_pct"] = tuple(v / P["PO"] * 100 for v in o["beneficio"])
        o["P"] = PROB[o["p"]][1]; o["EMV_pct"] = o["P"] * sum(o["beneficio"]) / 3.0 / P["PO"] * 100; o["EMV"] = o["P"] * sum(o["beneficio"]) / 3.0; o["EMV_plazo"] = o["P"] * sum(o["plazo"]) / 3.0


def montecarlo(n=20000, semilla=2673852, residual=False):
    """Simulación de Monte Carlo. Cada riesgo ocurre con su probabilidad (inherente o residual) y su costo y su retraso
    siguen una distribución triangular (mínimo, más probable, máximo).
    Costo para la Entidad = riesgos asignados a la Entidad + 50 % de los compartidos (afectados por el factor de
    transferencia de la póliza CAR) + gastos generales y supervisión por los días de ampliación que le corresponden.
    Plazo: los riesgos en la ruta crítica se agrupan por etapa; dentro de cada grupo se suma el mayor retraso y el 25 %
    de los demás (concurrencia), y los grupos se suman entre sí."""
    rng = np.random.default_rng(semilla)
    cE = np.zeros(n); cC = np.zeros(n)
    G = {}; GE = {}
    for r in R:
        occ = rng.random(n) < (r["Pr"] if residual else r["P"])
        a, m, b = r["costo"]; c = rng.triangular(a, m, b, n) if b > a else np.full(n, float(m))
        a, m, b = r["plazo"]; t = rng.triangular(a, m, b, n) if b > a else np.full(n, float(m))
        f = FACTOR[r["asig"]]
        cE += occ * c * f * r["fr"]; cC += occ * c * (1 - f)
        if r["rc"]:
            G.setdefault(r["grupo"], []).append(occ * t); GE.setdefault(r["grupo"], []).append(occ * t * f)
    def combinar(lst):
        M = np.vstack(lst); mx = M.max(0); return mx + CONCURRENCIA * (M.sum(0) - mx)
    dias = sum(combinar(v) for v in G.values())
    diasE = sum(combinar(v) for v in GE.values())
    cE_tot = cE + diasE * P["costo_dia"]
    pct = lambda x, q: float(np.percentile(x, q))
    res = {"n": n, "residual": residual, "costo_dia": P["costo_dia"],
           "entidad": {q: pct(cE_tot, q) for q in (10, 50, 80, 90)}, "entidad_media": float(cE_tot.mean()),
           "entidad_directo_media": float(cE.mean()), "entidad_dias_media": float(diasE.mean()),
           "contratista": {q: pct(cC, q) for q in (10, 50, 80, 90)}, "contratista_media": float(cC.mean()),
           "dias": {q: pct(dias, q) for q in (10, 50, 80, 90)}, "dias_media": float(dias.mean()),
           "diasE": {q: pct(diasE, q) for q in (10, 50, 80, 90)}}
    hist, bordes = np.histogram(cE_tot / 1e6, bins=40); res["hist_entidad"] = [hist.tolist(), bordes.tolist()]
    hd, bd = np.histogram(dias, bins=40); res["hist_dias"] = [hd.tolist(), bd.tolist()]
    res["muestras_entidad"] = np.sort(cE_tot)[:: max(1, n // 500)].tolist(); res["muestras_dias"] = np.sort(dias)[:: max(1, n // 500)].tolist()
    return res


def todo():
    calcular(); mc = {"inherente": montecarlo(), "residual": montecarlo(residual=True)}
    os.makedirs(CALC, exist_ok=True)
    json.dump({"proyecto": P, "riesgos": R, "oportunidades": OPORT, "montecarlo": mc, "grupos": GRUPOS, "concurrencia": CONCURRENCIA}, open(os.path.join(CALC, "riesgos.json"), "w"), ensure_ascii=False, indent=1)
    return mc


if __name__ == "__main__":
    mc = todo()
    import collections
    print("K", round(P["K"], 4), "costo/dia", round(P["costo_dia"]))
    print(collections.Counter(r["nivel"] for r in R))
    for r in sorted(R, key=lambda r: -r["PxI"]): print(r["cod"], r["P_txt"], r["I_txt"], r["PxI"], r["nivel"], r["asig"], round(r["EMV_costo"]))
    for k, m in mc.items():
        print(k, "entidad", {q: round(v / 1e6, 2) for q, v in m["entidad"].items()}, "dias", {q: round(v) for q, v in m["dias"].items()},
              "diasE", {q: round(v) for q, v in m["diasE"].items()}, "contratista", {q: round(v / 1e6, 2) for q, v in m["contratista"].items()})
    print(collections.Counter(r["nivel_r"] for r in R))
