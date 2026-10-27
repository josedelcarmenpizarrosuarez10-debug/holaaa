# -*- coding: utf-8 -*-
"""Biblioteca estándar de actividades de construcción, peligros, riesgos y controles para el IPERC y el Plan de Seguridad y
Salud en el Trabajo (PSST) de obras en el Perú (edificación, vías, saneamiento, drenaje, puentes, electrificación).

Cada ACTIVIDAD se reconoce en el presupuesto por las palabras clave de sus partidas (expresión regular sobre la descripción).
Cada PELIGRO trae su evaluación por defecto con el método de la R.M. N.° 050-2013-TR:
  D  = índice de exposición (1 esporádica / anual, 2 eventual / mensual, 3 permanente / diaria)
  S  = índice de severidad   (1 lesión sin incapacidad o disconfort, 2 incapacidad temporal o daño reversible,
                              3 incapacidad permanente, muerte o daño irreversible)
  Dr, Sr = exposición y severidad después de aplicar los controles (por defecto iguales a D y S).
El índice de personas expuestas (A) sale de la cuadrilla de la actividad; los índices de procedimientos (B) y capacitación (C)
son 2 antes de los controles y 1 después (PETS, ATS, capacitación y supervisión implementados).
Controles en el orden de la jerarquía (Ley N.° 29783, art. 21): eliminación, sustitución, ingeniería, administrativos, EPP.

Para ampliar la biblioteca basta agregar actividades o peligros con la misma estructura: el programa no cambia.
"""
import re

# ------------------------------------------------------------------ equipos de protección personal (EPP)
EPP = {
    "casco": "Casco de seguridad con barbiquejo (ANSI Z89.1)",
    "lentes": "Lentes de seguridad claros u oscuros (ANSI Z87.1)",
    "botas": "Calzado de seguridad con puntera (ASTM F2413)",
    "botas_jebe": "Botas de jebe con puntera de acero",
    "chaleco": "Chaleco o uniforme con cintas reflectivas (ANSI/ISEA 107)",
    "guantes_cuero": "Guantes de cuero o badana",
    "guantes_nitrilo": "Guantes de nitrilo o neopreno (químicos, cemento, asfalto)",
    "guantes_diel": "Guantes dieléctricos clase según tensión y guantes de cuero de protección",
    "auditivo": "Protector auditivo tipo tapón u orejera (ANSI S3.19)",
    "respirador": "Respirador de media cara con filtros para polvo P100 (NIOSH)",
    "respirador_gases": "Respirador de media cara con cartuchos para vapores orgánicos (NIOSH)",
    "arnes": "Arnés de cuerpo entero y línea de anclaje con absorbedor de impacto (ANSI Z359.11)",
    "careta_soldar": "Careta de soldar con filtro adecuado, mandil, escarpines y guantes de caña larga de cuero",
    "careta_facial": "Careta facial de policarbonato",
    "bloqueador": "Bloqueador solar FPS 50+ y cortasol para casco",
    "polainas": "Polainas de protección contra mordeduras y botas de caña alta",
    "salvavidas": "Chaleco salvavidas",
    "ropa_termica": "Ropa de manga larga de algodón y guantes de caña larga resistentes al calor",
    "repelente": "Repelente de insectos y ropa de manga larga",
    "impermeable": "Ropa impermeable (poncho o traje de agua)",
}
EPP_CORTO = {"casco": "Casco", "lentes": "Lentes", "botas": "Calzado de seguridad", "botas_jebe": "Botas de jebe", "chaleco": "Chaleco reflectivo",
             "guantes_cuero": "Guantes de cuero", "guantes_nitrilo": "Guantes de nitrilo", "guantes_diel": "Guantes dieléctricos", "auditivo": "Protector auditivo",
             "respirador": "Respirador para polvo", "respirador_gases": "Respirador para vapores", "arnes": "Arnés y línea de anclaje",
             "careta_soldar": "Careta y mandil de soldar", "careta_facial": "Careta facial", "bloqueador": "Bloqueador y cortasol", "polainas": "Polainas",
             "salvavidas": "Chaleco salvavidas", "ropa_termica": "Ropa resistente al calor", "repelente": "Repelente", "impermeable": "Ropa impermeable"}
EPP_BASICO = ["casco", "lentes", "botas", "chaleco", "guantes_cuero"]

PETAR = {
    "altura": "Trabajos en altura (a partir de 1.80 m)",
    "excavacion": "Excavaciones y zanjas (profundidad mayor de 1.50 m)",
    "caliente": "Trabajos en caliente (soldadura, oxicorte, esmerilado, asfalto caliente)",
    "confinado": "Trabajos en espacios confinados",
    "izaje": "Izaje de cargas con grúa o equipo de levante",
    "electrico": "Trabajos con energía eléctrica y cerca de líneas energizadas",
    "explosivos": "Uso de explosivos (voladura)",
    "cauces": "Trabajos en cauces, sobre agua o con riesgo de ahogamiento",
}


def pel(peligro, riesgo, consecuencia, tipo, D, S, ctrl, Dr=None, Sr=None, rutina="R"):
    """tipo: 'S' seguridad o 'SO' salud ocupacional. ctrl = (eliminación, sustitución, ingeniería, administrativos, epp)."""
    e, s, i, a, p = ctrl
    return dict(peligro=peligro, riesgo=riesgo, consecuencia=consecuencia, tipo=tipo, D=D, S=S,
                Dr=D if Dr is None else Dr, Sr=S if Sr is None else Sr, rutina=rutina,
                elim=e, sust=s, ing=i, adm=a, epp=p)


N = "No aplica"
# ------------------------------------------------------------------ peligros comunes (reutilizables)
P_SOL = pel("Radiación solar y temperatura ambiente elevada", "Exposición prolongada a radiación UV y a calor",
            "Golpe de calor, deshidratación, quemaduras de piel", "SO", 3, 2,
            (N, N, "Toldos o sombras en las zonas de descanso; puntos de hidratación con agua potable en cada frente",
             "Pausas de hidratación; rotación del personal en las horas de mayor radiación (11:00 a 15:00); charla de estrés térmico",
             EPP["bloqueador"]), Sr=1)
P_LLUVIA = pel("Lluvia intensa y tormenta eléctrica", "Resbalones y caídas; descarga eléctrica atmosférica",
               "Contusiones, fracturas, electrocución", "S", 2, 3,
               (N, N, "Refugios temporales y vehículos cerrados en el frente",
                "Suspensión de trabajos a campo abierto con tormenta eléctrica (regla 30-30); monitoreo del pronóstico del SENAMHI; orden y limpieza de accesos",
                EPP["impermeable"]), Dr=1, Sr=2)
P_SISMO = pel("Sismo", "Caída de objetos, colapso de estructuras provisionales o derrumbes",
              "Contusiones, aplastamiento, muerte", "S", 1, 3,
              (N, N, "Estructuras provisionales arriostradas; almacenamiento estable de materiales",
               "Plan de respuesta ante emergencias; zonas seguras señalizadas; simulacros", "EPP básico"), Sr=2)
P_OFIDIO = pel("Ofidios, arácnidos e insectos ponzoñosos", "Mordedura o picadura durante el trabajo en vegetación",
               "Envenenamiento, reacción alérgica, muerte", "S", 2, 3,
               (N, N, "Desbroce y limpieza previa de las áreas de trabajo y de tránsito",
                "Inspección visual antes de iniciar; coordinación con el establecimiento de salud sobre suero antiofídico; plan de evacuación inmediata",
                EPP["polainas"]), Sr=2)
P_VECTOR = pel("Mosquitos vectores (dengue, malaria, zika)", "Picadura de mosquitos infectados", "Enfermedad metaxénica", "SO", 3, 2,
               (N, N, "Mallas mosquiteras en campamento; eliminación de recipientes con agua estancada",
                "Campaña de prevención con el establecimiento de salud; vigilancia de casos febriles", EPP["repelente"]))
P_ALTITUD = pel("Altitud y bajas temperaturas", "Exposición a hipoxia y frío", "Mal de altura, hipotermia, enfermedades respiratorias", "SO", 3, 2,
                (N, N, "Ambientes de descanso abrigados", "Aclimatación progresiva; evaluación médica de aptitud para altura; pausas",
                 "Ropa térmica y casaca impermeable"), Sr=1)
P_CARGA = pel("Manipulación manual de cargas", "Sobreesfuerzo por levantar o trasladar cargas pesadas o en mala postura",
              "Lumbalgia, hernias, lesiones musculoesqueléticas", "SO", 3, 2,
              (N, "Uso de carretillas, montacargas o equipo para cargas mayores de 25 kg", "Puntos de acopio cerca del frente de trabajo",
               "Capacitación en levantamiento seguro (R.M. N.° 375-2008-TR); trabajo en pareja; pausas activas", "EPP básico; faja lumbar solo con indicación médica"), Sr=1)
P_HERR = pel("Herramientas manuales", "Golpes, cortes o atrapamiento al usar herramientas", "Contusiones, cortes, fracturas de dedos", "S", 3, 2,
             (N, N, "Herramientas con mangos y guardas en buen estado",
              "Inspección de herramientas con cinta de color del mes; retiro de las defectuosas; ATS diario", EPP["guantes_cuero"] + ", lentes de seguridad"), Sr=1)
P_SUELO = pel("Superficies irregulares, desniveles y desorden", "Caída al mismo nivel por tropiezo o resbalón", "Contusiones, esguinces, fracturas", "S", 3, 2,
              (N, N, "Accesos y pasarelas habilitados", "Orden y limpieza diaria; señalización de desniveles", EPP["botas"]), Sr=1)
P_POLVO = pel("Material particulado (polvo)", "Inhalación de polvo y contacto con los ojos", "Irritación ocular, enfermedades respiratorias", "SO", 3, 2,
              (N, N, "Riego de vías y frentes con cisterna", "Ubicación del personal a barlovento; monitoreo de polvo", EPP["respirador"] + ", lentes"))
P_RUIDO = pel("Ruido de maquinaria y equipos", "Exposición a ruido mayor de 85 dB(A)", "Hipoacusia inducida por ruido", "SO", 3, 2,
              (N, N, "Equipos con silenciadores y mantenimiento al día", "Monitoreo de ruido; rotación del personal; señalización de uso obligatorio de protección auditiva",
               EPP["auditivo"]))
P_ATROP_MAQ = pel("Maquinaria pesada en movimiento", "Atropello o golpe por maquinaria (retroceso, giro)", "Aplastamiento, fracturas, muerte", "S", 3, 3,
                  (N, N, "Alarma de retroceso y luces en los equipos; zona de trabajo delimitada",
                   "Vigía o señalero; distancia mínima al radio de giro; prohibido el ingreso de peatones al área de operación; operadores autorizados",
                   EPP["chaleco"]), Dr=1, Sr=3)
P_TRANSITO = pel("Tránsito vehicular de terceros", "Atropello o colisión con vehículos que circulan por la vía", "Politraumatismo, muerte", "S", 3, 3,
                 (N, N, "Dispositivos de control de tránsito (conos, barreras, tranqueras, señales) según el Manual de Dispositivos de Control del Tránsito del MTC",
                  "Plan de desvíos y control de tránsito; controladores con paletas PARE/SIGA y radio; trabajos nocturnos solo con iluminación",
                  EPP["chaleco"]), Dr=1, Sr=3)
P_ELEC_PORT = pel("Equipos eléctricos portátiles y extensiones", "Contacto eléctrico directo o indirecto", "Quemaduras, electrocución", "S", 2, 3,
                  (N, N, "Tablero provisional con interruptor diferencial y puesta a tierra; cables y enchufes industriales",
                   "Inspección de equipos y extensiones; bloqueo y etiquetado; solo personal autorizado manipula el tablero", EPP["guantes_cuero"]), Sr=2)
P_VIB_MB = pel("Vibración mano-brazo", "Exposición a vibración de equipos manuales (compactadoras, martillos, vibradores)",
               "Trastornos vasculares y osteomusculares", "SO", 3, 2,
               (N, "Equipos con mangos antivibratorios", "Mantenimiento de amortiguadores", "Rotación del personal y pausas", "Guantes antivibración"), Sr=1)
P_CEMENTO = pel("Cemento y concreto fresco", "Contacto dérmico y salpicaduras en los ojos", "Dermatitis, quemaduras químicas, lesión ocular", "SO", 3, 2,
                (N, N, "Lavaojos portátil en el frente", "Higiene personal al terminar la tarea; charla sobre dermatitis por cemento",
                 EPP["guantes_nitrilo"] + ", botas de jebe, lentes"), Sr=1)
P_CAIDA_ALT = pel("Trabajo en bordes, plataformas o estructuras a más de 1.80 m", "Caída a distinto nivel", "Fracturas, traumatismo encéfalo craneano, muerte", "S", 3, 3,
                  (N, N, "Barandas perimetrales de 1.00 m con rodapié; plataformas y andamios certificados; líneas de vida y puntos de anclaje",
                   "PETAR de trabajo en altura; inspección diaria de andamios (tarjeta verde/roja); personal capacitado y apto", EPP["arnes"]), Sr=2)
P_CAIDA_OBJ = pel("Objetos y materiales en altura", "Caída de herramientas o materiales sobre personas", "Contusiones, traumatismo encéfalo craneano", "S", 2, 3,
                  (N, N, "Rodapiés, mallas y portaherramientas; área inferior delimitada",
                   "Prohibido el tránsito bajo la zona de trabajo; amarre de herramientas", EPP["casco"]), Sr=2)
P_IZAJE = pel("Izaje de cargas con grúa o equipo de levante", "Caída de la carga, volteo de la grúa o contacto con la carga suspendida",
              "Aplastamiento, muerte", "S", 2, 3,
              (N, N, "Grúa con certificado de operatividad; aparejos certificados; estabilizadores sobre terreno firme; vientos de guía",
               "PETAR de izaje y plan de izaje; rigger y operador certificados; zona de exclusión bajo la carga", EPP["casco"] + ", " + EPP["guantes_cuero"]), Dr=1)
P_SOLDADURA = pel("Soldadura eléctrica y oxicorte", "Radiación UV, chispas, humos metálicos y contacto con piezas calientes",
                  "Quemaduras, conjuntivitis actínica, intoxicación por humos, incendio", "S", 3, 2,
                  (N, N, "Biombos o pantallas; ventilación o extracción localizada; extintor PQS a menos de 10 m",
                   "PETAR de trabajo en caliente; retiro de material combustible; vigía contra incendio", EPP["careta_soldar"]), Sr=1)
P_INCENDIO = pel("Combustibles y materiales inflamables", "Incendio o explosión", "Quemaduras, muerte, daño a instalaciones", "S", 2, 3,
                 (N, N, "Almacén ventilado con bandeja antiderrame, extintores PQS y señalización; distancia a fuentes de ignición",
                  "Prohibido fumar; hojas de datos de seguridad (SDS) en el almacén; inspección mensual de extintores", "EPP básico"), Dr=1)
P_ESTRES_PS = pel("Carga de trabajo, jornadas extensas y trabajo lejos del hogar", "Fatiga y estrés laboral", "Trastornos psicosociales, errores y accidentes", "SO", 3, 2,
                  (N, N, "Campamento con condiciones adecuadas de descanso y alimentación",
                   "Control de jornada y horas extras; programa de bienestar; canal de atención de quejas y hostigamiento", N), Sr=1)

# ------------------------------------------------------------------ actividades
# cod, proceso, nombre, regex sobre la descripción de partidas, cuadrilla, puestos, petar, pets, epp, peligros
ACT = []


def act(cod, proceso, nombre, regex, cuadrilla, puestos, peligros, petar=(), pets=None, epp=(), siempre=False, condicion=None, titulo=None):
    ACT.append(dict(cod=cod, proceso=proceso, nombre=nombre, rx=re.compile(regex, re.I) if regex else None, cuadrilla=cuadrilla,
                    puestos=list(puestos), peligros=peligros, petar=list(petar), pets=pets or "PETS - " + nombre.split(" (")[0],
                    epp=EPP_BASICO + [e for e in epp if e not in EPP_BASICO], siempre=siempre, condicion=condicion,
                    rx_tit=re.compile(titulo, re.I) if titulo else None))


act("GEN", "Actividades generales", "Trabajos generales a campo abierto", None, 30, ["Todo el personal"],
    [P_SOL, P_LLUVIA, P_SISMO, P_ESTRES_PS], pets="Reglamento interno de SST y charla diaria de 5 minutos", epp=["bloqueador", "impermeable"], siempre=True)
act("GEN-SEL", "Actividades generales", "Trabajos en zona de selva (fauna y vectores)", None, 30, ["Todo el personal"],
    [P_OFIDIO, P_VECTOR], pets="PETS - Prevención de mordeduras de ofidios y enfermedades metaxénicas", epp=["polainas", "repelente"],
    siempre=True, condicion="selva")
act("GEN-ALT", "Actividades generales", "Trabajos en zona de altura (más de 2,500 msnm)", None, 30, ["Todo el personal"],
    [P_ALTITUD], pets="Protocolo de aclimatación y aptitud médica para altura", siempre=True, condicion="altura")
act("TRAS", "Actividades generales", "Traslado de personal y materiales en vehículos", None, 15, ["Chofer", "Todo el personal"],
    [pel("Vehículos de transporte de personal en vías afirmadas y con pendiente", "Choque, despiste o volcadura", "Politraumatismo, muerte", "S", 3, 3,
         (N, N, "Vehículos con cinturones, barras antivuelco en camionetas, GPS con control de velocidad; mantenimiento preventivo",
          "Conductores con licencia y capacitación en manejo defensivo; límite de velocidad; prohibido trasladar personal en tolvas; check-list diario",
          "Cinturón de seguridad"), Sr=2),
     pel("Conducción prolongada", "Fatiga y somnolencia del conductor", "Accidente de tránsito", "S", 2, 3,
         (N, N, N, "Control de horas de manejo y descanso; prueba de alcoholemia aleatoria", N), Sr=2)],
    pets="PETS - Transporte de personal y manejo defensivo", siempre=True)
act("CAMP", "Obras provisionales", "Campamento, almacenes, comedor, servicios higiénicos y cartel de obra",
    r"CAMPAMENTO|ALMAC[EÉ]N(ES)?\b|PATIO DE M[AÁ]QUINAS|CARTEL|OBRAS PROVISIONALES|CERCO PROVISIONAL|CASETA|SERVICIOS HIGI[EÉ]NICOS PROVISIONALES",
    8, ["Operario", "Oficial", "Peón", "Almacenero"],
    [P_CARGA, P_HERR, P_INCENDIO, P_ELEC_PORT,
     pel("Agua y alimentos para consumo del personal", "Consumo de agua o alimentos contaminados", "Enfermedades diarreicas agudas, intoxicación", "SO", 3, 2,
         (N, N, "Agua potable o tratada en dispensadores; servicios higiénicos y lavamanos (1 por cada 15 trabajadores como mínimo)",
          "Control sanitario del comedor y del concesionario de alimentos; limpieza diaria de servicios", N), Sr=1)],
    pets="PETS - Instalación de campamento y almacenamiento de materiales")
act("MOVI", "Obras provisionales", "Movilización y desmovilización de equipos y fletes",
    r"MOVI?LIZACI[OÓ]N|DESMOVILIZACI[OÓ]N|FLETE", 4, ["Chofer", "Operador de equipo", "Rigger"],
    [pel("Carga y descarga de maquinaria en cama baja", "Volcadura del equipo o atrapamiento durante el embarque", "Aplastamiento, muerte", "S", 1, 3,
         (N, N, "Rampas firmes y calzas; cadenas y tensores certificados", "Procedimiento de embarque con vigía; zona de exclusión; escolta en la ruta",
          EPP["chaleco"]), Sr=2),
     P_CARGA],
    pets="PETS - Movilización de equipos en cama baja")
act("TOPO", "Obras preliminares", "Topografía, trazo, nivelación y replanteo",
    r"TOPOGRAF|TRAZO|REPLANTEO|GEORREFERENC|NIVELACI[OÓ]N TOPOGR", 3, ["Topógrafo", "Ayudante de topografía"],
    [P_TRANSITO, P_SUELO, P_HERR], pets="PETS - Trabajos de topografía en vía con tránsito")
act("TRAN", "Obras preliminares", "Mantenimiento del tránsito, desvíos y señalización temporal",
    r"MANTENIMIENTO DE TR[AÁ]NSITO|DESV[IÍ]O TEMPORAL|SE[NÑ]ALIZACI[OÓ]N TRANSITORIA|SEGURIDAD VIAL|DESV[IÍ]O DE TR[AÁ]NSITO|CONTROL DE TR[AÁ]NSITO|SE[NÑ]ALES TEMPORALES|POSTES PARA SE[NÑ]ALES",
    6, ["Controlador de tránsito (vigía)", "Peón", "Operador de equipo"],
    [P_TRANSITO,
     pel("Usuarios de la vía en espera o en desvío", "Agresión verbal o física por demoras del tránsito", "Estrés, lesiones", "SO", 2, 2,
         (N, N, "Desvíos habilitados para no detener el tránsito por más de 15 minutos",
          "Comunicación a la población de horarios de cierre; coordinación con la PNP", N), Sr=1),
     P_SOL],
    pets="Plan de desvíos y PETS - Control de tránsito en zona de trabajo", epp=["bloqueador"])
act("DESB", "Obras preliminares", "Desbroce, limpieza de terreno y tala de árboles",
    r"DESBROCE|LIMPIEZA (DEL|DE) TERRENO|LIMPIEZA Y DESBROCE|\bTALA\b|\bROCE\b|DESARRAIGO|DESBOSQUE", 6, ["Peón", "Motosierrista", "Operador de equipo"],
    [pel("Machetes, motosierras y desbrozadoras", "Cortes y proyección de partículas", "Heridas cortantes, amputaciones, lesión ocular", "S", 3, 3,
         (N, N, "Motosierra con freno de cadena y guardas", "Operador capacitado y autorizado; distancia entre trabajadores de 3 m como mínimo",
          "Careta de malla, pantalón anticorte, protector auditivo y guantes"), Sr=2),
     pel("Caída de árboles y ramas durante la tala", "Golpe o aplastamiento por el árbol", "Fracturas, muerte", "S", 2, 3,
         (N, N, "Corte direccional con cuñas y vía de escape", "Zona de exclusión de 2 veces la altura del árbol; vigía", EPP["casco"]), Dr=1),
     P_HERR, P_CARGA],
    pets="PETS - Desbroce y tala de árboles", epp=["auditivo", "careta_facial"])
act("DEMO", "Demoliciones", "Demolición de estructuras, escarificado y desmontaje",
    r"DEMOLICI[OÓ]N|ESCARIFICAD|DESMONTAJE|PICADO|ROTURA DE", 8, ["Operario", "Peón", "Operador de equipo"],
    [pel("Fragmentos de concreto, asfalto y acero", "Proyección de partículas y fragmentos", "Lesión ocular, cortes, contusiones", "S", 3, 2,
         (N, N, "Pantallas o mallas de contención", "Área delimitada; distancia segura a la zona de demolición", "Lentes y careta facial"), Sr=1),
     pel("Estructura existente debilitada", "Colapso no controlado de la estructura en demolición", "Aplastamiento, muerte", "S", 2, 3,
         (N, N, "Apuntalamiento previo; demolición mecánica a distancia", "Evaluación estructural previa y secuencia escrita de demolición; PETAR",
          EPP["casco"]), Dr=1),
     P_POLVO, P_RUIDO, P_VIB_MB],
    petar=["altura"], pets="PETS - Demolición de estructuras existentes", epp=["auditivo", "respirador", "careta_facial"])
act("MTMQ", "Movimiento de tierras", "Movimiento de tierras con maquinaria (corte, terraplén, eliminación, canteras y DME)",
    r"CORTE (EN|DE) |TERRAPL[EÉ]N|CONFORMACI[OÓ]N|MEJORAMIENTO DE SUELOS|ELIMINACI[OÓ]N|EXTRACCI[OÓ]N|APILAMIENTO|CARGU[IÍ]O|ACOMODO|"
    r"DEP[OÓ]SITO DE MATERIAL|HABILITACI[OÓ]N DE (ACCESO|CANTERA|DEP[OÓ]SITO)|SUB[- ]?BASE|BASE GRANULAR|AFIRMADO|PERFILADO|EXPLANACI|RIEGO PARA CONTROL",
    12, ["Operador de equipo", "Vigía de maquinaria", "Peón", "Chofer"],
    [P_ATROP_MAQ,
     pel("Equipos operando en taludes, bordes de terraplén y pendientes", "Volcadura de la maquinaria", "Aplastamiento del operador, muerte", "S", 2, 3,
         (N, N, "Equipos con estructura ROPS/FOPS y cinturón; bermas de seguridad en bordes", "Inspección del terreno antes de operar; operadores certificados",
          "Cinturón de seguridad"), Sr=2),
     pel("Taludes de corte inestables", "Desprendimiento de rocas o deslizamiento sobre personas y equipos", "Aplastamiento, muerte", "S", 2, 3,
         (N, N, "Desquinche de taludes; banquetas", "Inspección de taludes después de lluvias; vigía; prohibido trabajar al pie de taludes sin evaluar",
          EPP["casco"]), Dr=1),
     P_POLVO, P_RUIDO,
     pel("Vibración de cuerpo entero en la cabina", "Exposición del operador a vibración", "Lumbalgias, trastornos de columna", "SO", 3, 2,
         (N, N, "Asientos con suspensión en buen estado", "Pausas y rotación; mantenimiento de vías de circulación", N), Sr=1)],
    pets="PETS - Movimiento de tierras con maquinaria pesada", epp=["auditivo", "respirador"])
act("ROCA", "Movimiento de tierras", "Corte en roca (martillo hidráulico o voladura controlada)",
    r"ROCA FIJA|ROCA SUELTA|VOLADURA|PERFORACI[OÓ]N EN ROCA", 8, ["Operador de equipo", "Perforista", "Disparador autorizado", "Peón"],
    [pel("Explosivos y accesorios de voladura (si el procedimiento lo requiere)", "Detonación prematura o proyección de rocas", "Politraumatismo, muerte", "S", 1, 3,
         (N, "Uso de martillo hidráulico o métodos sin explosivos cuando sea factible", "Polvorín autorizado; mantas de voladura",
          "Licencias y autorizaciones de la SUCAMEC; disparador autorizado; PETAR; evacuación y cierre de vía en un radio de 500 m", EPP["auditivo"]), Sr=3),
     P_RUIDO, P_POLVO, P_ATROP_MAQ],
    petar=["explosivos"], pets="PETS - Corte en roca y voladura controlada", epp=["auditivo", "respirador"])
act("EXCA", "Movimiento de tierras", "Excavación de zanjas y para estructuras",
    r"EXCAVACI[OÓ]N|ZANJA", 8, ["Operario", "Peón", "Operador de equipo"],
    [pel("Paredes de excavación sin talud ni entibado", "Derrumbe y sepultamiento", "Asfixia, aplastamiento, muerte", "S", 3, 3,
         (N, N, "Talud estable o entibado en excavaciones mayores de 1.50 m; material excavado a 0.60 m del borde como mínimo",
          "PETAR de excavación; inspección diaria por persona competente; evaluación después de lluvias", EPP["casco"]), Dr=1),
     pel("Bordes de excavación abiertos", "Caída de personas o equipos a la excavación", "Fracturas, contusiones", "S", 3, 2,
         (N, N, "Barandas o cinta de señalización a 1.00 m del borde; escaleras de acceso cada 15 m", "Pasarelas para cruzar; iluminación nocturna",
          EPP["botas"]), Sr=1),
     pel("Redes enterradas de servicios (electricidad, agua, desagüe, telecomunicaciones)", "Contacto con cables energizados o rotura de tuberías",
         "Electrocución, inundación de la zanja", "S", 1, 3,
         (N, N, "Detección de redes y calicatas manuales antes de excavar", "Planos de interferencias; coordinación con las empresas de servicios",
          EPP["guantes_cuero"]), Sr=2),
     P_CARGA, P_HERR],
    petar=["excavacion"], pets="PETS - Excavación de zanjas y estructuras")
act("CAUC", "Movimiento de tierras", "Trabajos en cauces, excavación bajo agua y encauzamiento",
    r"BAJO AGUA|ENCAUZAMIENTO|ENCAUSAMIENTO|CURSO DE AGUA|CANTERA DE R[IÍ]O|FUENTE DE AGUA|QUEBRADA|DEFENSA RIBERE|BOMBEO|ATAGU[IÍ]A",
    8, ["Operario", "Peón", "Operador de equipo"],
    [pel("Cauces de ríos y quebradas", "Caída al agua y arrastre por la corriente", "Ahogamiento, muerte", "S", 2, 3,
         (N, N, "Atagüías y desvíos; cuerdas de vida y aros salvavidas en la orilla", "PETAR; trabajo en parejas; vigía en la orilla", EPP["salvavidas"]), Sr=2),
     pel("Crecida súbita del cauce", "Inundación del área de trabajo", "Ahogamiento, pérdida de equipos", "S", 2, 3,
         (N, N, "Ubicación de equipos y materiales fuera del nivel de crecida", "Alerta temprana con observador aguas arriba y pronóstico del SENAMHI; evacuación",
          N), Dr=1),
     pel("Motobombas de combustión", "Inhalación de monóxido de carbono en zanjas y pozas", "Intoxicación", "SO", 2, 3,
         (N, "Bombas eléctricas sumergibles con diferencial", "Motobombas fuera de la excavación y a sotavento", "Monitoreo de gases", N), Sr=2),
     P_SUELO],
    petar=["cauces"], pets="PETS - Trabajos en cauces y bajo agua", epp=["salvavidas", "botas_jebe"])
act("RELL", "Movimiento de tierras", "Rellenos, refine, nivelación y compactación",
    r"RELLENO|REFINE|COMPACTACI[OÓ]N|NIVELACI[OÓ]N|CAMA DE|FILTRO|SUBRASANTE|PERFILADO", 6, ["Operario", "Peón", "Operador de equipo"],
    [P_VIB_MB, P_RUIDO, P_CARGA,
     pel("Rodillo y plancha compactadora", "Atrapamiento de pies o golpe por el equipo", "Fracturas", "S", 2, 2,
         (N, N, "Equipos con guardas y parada de emergencia", "Operador capacitado; distancia al borde de taludes", EPP["botas"]), Sr=1)],
    pets="PETS - Relleno y compactación", epp=["auditivo"])
act("GEOS", "Movimiento de tierras", "Geosintéticos y subdrenaje",
    r"GEOMALLA|GEOTEXTIL|GEOBOLSA|PERMADRAIN|DRAINPIPE|GEOCOMPUESTO|GEOMEMBRANA|SUBDRENAJE|SUBDREN", 6, ["Operario", "Peón"],
    [P_CARGA, P_HERR, P_SUELO], pets="PETS - Instalación de geosintéticos")
act("TRSP", "Transporte", "Transporte de materiales con volquetes",
    r"TRANSPORTE DE|ACARREO|CARGU[IÍ]O Y TRANSPORTE", 10, ["Chofer", "Operador de cargador", "Vigía de maquinaria"],
    [pel("Volquetes en vías con tránsito y pendiente", "Choque, despiste o volcadura del volquete", "Politraumatismo, muerte", "S", 3, 3,
         (N, N, "Volquetes con mantenimiento, alarma de retroceso y tolva con cubierta", "Límite de velocidad; check-list diario; choferes con licencia A-IIIb o la que corresponda",
          "Cinturón de seguridad"), Sr=2),
     pel("Carguío con cargador frontal o excavadora", "Golpe por el cucharón o caída de material de la tolva", "Contusiones, fracturas", "S", 3, 2,
         (N, N, "Zona de carguío delimitada", "Chofer dentro de la cabina durante el carguío; vigía", EPP["casco"]), Sr=1),
     P_POLVO, P_ATROP_MAQ],
    pets="PETS - Transporte de materiales en volquetes")
act("ACER", "Obras de concreto", "Habilitación y colocación de acero de refuerzo",
    r"ACERO DE REFUERZO|ACERO CORRUGADO|ACERO FY|HABILITACI[OÓ]N DE ACERO|MALLA ELECTROSOLDADA|ALAMBRE N", 6, ["Operario fierrero", "Oficial", "Peón"],
    [pel("Varillas de acero y extremos expuestos", "Cortes, punzonamiento y golpes", "Heridas, empalamiento", "S", 3, 3,
         (N, N, "Capuchones o protectores en los extremos de varillas", "Orden en el área de habilitado; transporte en pareja", EPP["guantes_cuero"]), Sr=2),
     pel("Cizalla y dobladora de fierro", "Atrapamiento de manos", "Fracturas, amputación de dedos", "S", 3, 2,
         (N, N, "Banco de habilitado con guardas", "Solo personal capacitado; inspección de equipos", EPP["guantes_cuero"]), Sr=1),
     P_CARGA],
    pets="PETS - Habilitación y colocación de acero de refuerzo")
act("ENCF", "Obras de concreto", "Encofrado y desencofrado",
    r"ENCOFRADO|DESENCOFRADO|FALSO PUENTE|OBRA FALSA|CIMBRA", 6, ["Operario carpintero", "Oficial", "Peón"],
    [pel("Sierra circular de mesa y herramientas de corte", "Contacto con el disco y proyección de astillas", "Amputación, cortes, lesión ocular", "S", 3, 3,
         (N, N, "Sierra con guarda del disco, cuchillo divisor y empujador", "Solo operador autorizado; inspección diaria", "Lentes, careta facial y protector auditivo"), Sr=2),
     pel("Encofrados y puntales", "Colapso del encofrado durante el vaciado", "Aplastamiento, caída", "S", 2, 3,
         (N, "Encofrado metálico modular cuando sea posible", "Diseño del encofrado y apuntalamiento; puntales certificados", "Inspección y liberación antes del vaciado",
          EPP["casco"]), Dr=1),
     pel("Clavos expuestos en maderas desencofradas", "Punzonamiento de pies y manos", "Heridas, infección", "S", 3, 2,
         (N, N, N, "Retiro de clavos y apilamiento ordenado de maderas", EPP["botas"]), Sr=1),
     P_CAIDA_ALT, P_CARGA],
    petar=["altura"], pets="PETS - Encofrado y desencofrado", epp=["auditivo", "arnes"])
act("CONC", "Obras de concreto", "Preparación, vaciado y curado de concreto",
    r"CONCRETO(?! ASF)|SOLADO|WATER ?STOP|SARDINEL|ACABADO EN VEREDAS|CONTRAPISO|FALSO PISO|CIMIENTO", 10,
    ["Operario", "Oficial", "Peón", "Operador de mezcladora"],
    [P_CEMENTO,
     pel("Mezcladora y vibrador de concreto", "Atrapamiento con partes móviles o contacto eléctrico", "Fracturas, electrocución", "S", 3, 2,
         (N, N, "Guardas en transmisiones; vibrador con aislamiento y diferencial", "Operador capacitado; no limpiar el tambor en movimiento", EPP["guantes_nitrilo"]), Sr=1),
     P_CARGA, P_VIB_MB, P_SUELO],
    pets="PETS - Vaciado y curado de concreto", epp=["guantes_nitrilo", "botas_jebe"])
act("PIED", "Obras de concreto", "Gaviones y mampostería de piedra",
    r"GAVI[OÓ]N|MAMPOSTER[IÍ]A|EMBOQUILLAD|PIEDRA|ENROCADO|TEJIDO Y CIERRE", 10, ["Operario", "Peón"],
    [P_CARGA,
     pel("Piedras de gran tamaño", "Golpe o aplastamiento de manos y pies", "Contusiones, fracturas", "S", 3, 2,
         (N, N, N, "Selección y acarreo en pareja; uso de barretas", EPP["guantes_cuero"]), Sr=1),
     pel("Alambre galvanizado de las canastas", "Cortes y punzonamiento", "Heridas", "S", 3, 1, (N, N, N, "Uso de alicates y tenazas adecuadas", EPP["guantes_cuero"])),
     P_SOL],
    pets="PETS - Armado y llenado de gaviones")
act("TUBE", "Obras de arte y drenaje", "Instalación de alcantarillas, tuberías y elementos prefabricados",
    r"ALCANTARILLA|TMC|TUBER[IÍ]A|TUBOS DE DRENAJE|PREFABRICAD|BUZ[OÓ]N|CAJA DE REGISTRO|SUMIDERO|REJILLA", 6, ["Operario", "Peón", "Operador de equipo"],
    [P_IZAJE,
     pel("Planchas y tubos de acero corrugado", "Cortes y atrapamiento de manos durante el armado", "Heridas, fracturas", "S", 3, 2,
         (N, N, N, "Armado con herramientas adecuadas; coordinación con el operador", EPP["guantes_cuero"]), Sr=1),
     P_CARGA],
    petar=["izaje"], pets="PETS - Instalación de alcantarillas y tuberías")
act("ASFA", "Pavimentos", "Imprimación, riego de liga y pavimento asfáltico en caliente",
    r"IMPRIMACI[OÓ]N|ASF[AÁ]LT|MAC\b|CEMENTO ASF|MC-?30|RIEGO DE LIGA|FILLER|ADITIVO MEJORADOR|CARPETA|EMULSI[OÓ]N|SELLO|SLURRY", 12,
    ["Operador de pavimentadora", "Operador de rodillo", "Rastrillero", "Peón", "Chofer de imprimadora"],
    [pel("Mezcla asfáltica y cemento asfáltico a alta temperatura", "Contacto con material caliente", "Quemaduras de segundo y tercer grado", "S", 3, 3,
         (N, N, "Pavimentadora con plataforma y barandas", "Distancia a la tolva; procedimiento de descarga", EPP["ropa_termica"]), Sr=2),
     pel("Asfalto diluido MC-30 y vapores de asfalto", "Inhalación de vapores y contacto dérmico", "Irritación respiratoria, dermatitis", "SO", 3, 2,
         (N, "Emulsión asfáltica en lugar de asfalto diluido cuando las especificaciones lo permitan", N, "Trabajo a barlovento; SDS en el frente",
          EPP["respirador_gases"]), Sr=1),
     pel("Asfalto diluido (inflamable) y calentadores", "Incendio del producto o del equipo de riego", "Quemaduras, muerte", "S", 2, 3,
         (N, N, "Extintores PQS en imprimadora y frente", "Prohibido fumar y llamas abiertas; PETAR de trabajo en caliente", "EPP básico"), Dr=1),
     P_ATROP_MAQ, P_TRANSITO, P_SOL],
    petar=["caliente"], pets="PETS - Imprimación y colocación de carpeta asfáltica", epp=["ropa_termica", "respirador_gases", "bloqueador"])
act("ESTM", "Puentes y estructuras", "Fabricación, arenado, pintura y montaje de estructuras metálicas",
    r"VIGAS? MET[AÁ]LICA|ESTRUCTURA(S)? MET[AÁ]LICA|MONTAJE (DE )?ESTRUCTURA|ARENADO|BARANDA|JUNTA DE DILATACI[OÓ]N MET|TOPE S[IÍ]SMICO|CARPINTER[IÍ]A MET[AÁ]LICA|SOLDADURA",
    8, ["Operario soldador", "Montajista", "Rigger", "Operador de grúa", "Peón"],
    [P_SOLDADURA, P_IZAJE, P_CAIDA_ALT,
     pel("Arenado con abrasivo", "Inhalación de polvo de abrasivo y sílice", "Silicosis, enfermedades respiratorias", "SO", 2, 3,
         (N, "Abrasivo sin sílice libre (granalla de acero o escoria)", "Cabina o zona de arenado aislada", "Monitoreo de polvo respirable",
          "Casco de arenador con suministro de aire"), Sr=2),
     pel("Pintura anticorrosiva y solventes", "Inhalación de vapores orgánicos", "Intoxicación, dermatitis", "SO", 2, 2,
         (N, "Pinturas de bajo contenido de solventes", "Ventilación", "SDS; almacenamiento lejos de fuentes de ignición", EPP["respirador_gases"]), Sr=1),
     P_RUIDO],
    petar=["caliente", "izaje", "altura"], pets="PETS - Montaje de estructuras metálicas", epp=["careta_soldar", "arnes", "auditivo", "respirador_gases"])
act("PUEN", "Puentes y estructuras", "Trabajos en puentes sobre cauces (estribos, superestructura, prueba de carga)",
    r"SUPER ?ESTRUCTURA|ESTRIBO|PRUEBA DE CARGA|PUENTE|PONT[OÓ]N",
    12, ["Operario", "Oficial", "Peón", "Operador de grúa"],
    [P_CAIDA_ALT, P_CAIDA_OBJ,
     pel("Trabajo sobre el cauce", "Caída al río desde el tablero o la obra falsa", "Ahogamiento, muerte", "S", 2, 3,
         (N, N, "Redes o barandas perimetrales; aros salvavidas y cuerda en la orilla", "Bote o rescatista en la orilla durante trabajos sobre el agua", EPP["salvavidas"]), Sr=2),
     pel("Prueba de carga con camiones", "Falla de la estructura o movimiento de vehículos sobre el tablero", "Aplastamiento", "S", 1, 3,
         (N, N, "Instrumentación y control a distancia", "Procedimiento de prueba aprobado; personal fuera del tablero durante la carga", EPP["chaleco"]), Sr=2)],
    petar=["altura", "cauces"], pets="PETS - Trabajos en puentes sobre cauces", epp=["arnes", "salvavidas"], titulo=r"PUENTE|PONT[OÓ]N")
act("SENV", "Señalización y seguridad vial", "Señalización vial definitiva, pintura de tráfico y barreras",
    r"MARCAS|PINTURA DE TR[AÁ]FICO|SE[NÑ]AL (PREVENTIVA|REGLAMENTARIA|INFORMATIVA|IMFORMATIVA)|POSTES? (DE SOPORTE|KILOM)|TACHAS|BARRERA DE SEGURIDAD|GUARDAV[IÍ]A|PINTADO DE|DELINEADOR|MONTAJE DE SE[NÑ]AL|ESTRUCTURA DE SOPORTE",
    6, ["Operario", "Peón", "Controlador de tránsito (vigía)"],
    [P_TRANSITO,
     pel("Pintura de tráfico y solventes", "Inhalación de vapores y contacto dérmico", "Irritación, intoxicación leve", "SO", 2, 2,
         (N, "Pintura base agua cuando las especificaciones lo permitan", N, "SDS en el frente", EPP["respirador_gases"]), Sr=1),
     P_CARGA, P_HERR],
    pets="PETS - Señalización vial y pintura de tráfico", epp=["respirador_gases"])
act("POST", "Obras preliminares", "Reubicación de postes e interferencias con redes eléctricas",
    r"REUBICACI[OÓ]N DE POSTES|POSTES DE (CONCRETO|MADERA)|L[IÍ]NEA DE (MEDIA|BAJA) TENSI[OÓ]N|RED (EL[EÉ]CTRICA|PRIMARIA|SECUNDARIA)|SUBESTACI[OÓ]N|ALUMBRADO",
    6, ["Electricista", "Operario", "Peón", "Operador de grúa"],
    [pel("Líneas eléctricas aéreas energizadas", "Contacto directo o arco eléctrico con equipos o personas", "Electrocución, quemaduras, muerte", "S", 2, 3,
         (N, N, "Corte de energía y puesta a tierra temporal por la concesionaria; distancias mínimas de seguridad a líneas energizadas",
          "PETAR eléctrico; coordinación con la concesionaria; vigía para equipos con pluma", EPP["guantes_diel"]), Dr=1),
     P_IZAJE, P_CAIDA_ALT],
    petar=["electrico", "izaje", "altura"], pets="PETS - Reubicación de postes con la concesionaria eléctrica", epp=["guantes_diel", "arnes"])
act("MANT", "Obras provisionales", "Mantenimiento y abastecimiento de combustible de maquinaria", None, 4, ["Mecánico", "Abastecedor", "Operador de equipo"],
    [P_INCENDIO,
     pel("Partes móviles y sistemas presurizados de la maquinaria", "Atrapamiento o golpe durante el mantenimiento", "Fracturas, amputaciones", "S", 2, 3,
         (N, N, "Calzas y bloqueo de implementos", "Bloqueo y etiquetado (LOTO) antes de intervenir; motor apagado", EPP["guantes_cuero"]), Sr=2),
     pel("Hidrocarburos y lubricantes", "Derrame y contacto dérmico", "Dermatitis, contaminación de suelo y agua", "SO", 3, 1,
         (N, N, "Bandejas y kit antiderrame", "Manejo de residuos peligrosos con EO-RS", EPP["guantes_nitrilo"]))],
    pets="PETS - Mantenimiento y abastecimiento de combustible", condicion="maquinaria")
act("AMBI", "Gestión ambiental", "Manejo de residuos, servicios higiénicos portátiles y revegetación",
    r"RESIDUOS|LETRINA|LIMPIEZA FINAL DE OBRA|LIMPIEZA PERMANENTE|REVEG|SEMBR[IÍ]O|PLANTONES|CAPA SUPERFICIAL DE SUELO|READECU|PLAN DE MANEJO|BA[NÑ]OS? QU[IÍ]MICO|MONITOREO AMBIENTAL|CIERRE DE (CANTERA|DME|CAMPAMENTO)", 4, ["Peón", "Operario"],
    [pel("Residuos sólidos y peligrosos", "Contacto con residuos contaminados o punzocortantes", "Infecciones, dermatitis, cortes", "SO", 2, 2,
         (N, N, "Contenedores rotulados por tipo de residuo; almacén de residuos peligrosos con losa y techo",
          "Segregación en la fuente; disposición con EO-RS registrada", EPP["guantes_nitrilo"]), Sr=1),
     pel("Servicios higiénicos portátiles", "Exposición a agentes biológicos", "Enfermedades infecciosas", "SO", 2, 2,
         (N, N, N, "Mantenimiento y limpieza por empresa autorizada", EPP["guantes_nitrilo"]), Sr=1),
     P_CARGA],
    pets="PETS - Manejo de residuos sólidos y peligrosos")
# --- actividades frecuentes en edificación y saneamiento
act("ALBA", "Arquitectura", "Albañilería, tarrajeos, pisos y enchapes",
    r"MURO(S)? DE (LADRILLO|SOGA|CABEZA|BLOQUE)|ALBA[NÑ]IL|TARRAJEO|REVOQUE|ENLUCIDO|CIELO ?RASO|PISO|Z[OÓ]CALO|CONTRAZ[OÓ]CALO|CER[AÁ]MIC|PORCELANATO|ENCHAPE|DERRAME",
    8, ["Operario albañil", "Oficial", "Peón"],
    [P_CEMENTO, P_CARGA,
     pel("Andamios y escaleras", "Caída a distinto nivel", "Fracturas, traumatismo", "S", 3, 3,
         (N, N, "Andamios certificados con barandas, rodapiés y plataformas completas", "Inspección diaria con tarjeta; escaleras con 1 m sobre el apoyo", EPP["arnes"]), Sr=2),
     pel("Cortadora de cerámica y amoladora", "Cortes y proyección de partículas; polvo de sílice", "Heridas, lesión ocular, silicosis", "S", 3, 2,
         (N, "Corte en húmedo", "Guardas en los discos", "Personal capacitado", "Lentes, careta facial, respirador P100"), Sr=1)],
    petar=["altura"], pets="PETS - Albañilería, tarrajeo y enchapes", epp=["arnes", "respirador"])
act("TECH", "Arquitectura", "Coberturas, techos y trabajos en altura de edificación",
    r"COBERTURA|TECHO|CALAMINA|TEJA|ALIGERADO|CANALETA|MONTANTE|CERCH|TIJERAL|DRYWALL|FACHADA", 6, ["Operario", "Oficial", "Peón"],
    [P_CAIDA_ALT, P_CAIDA_OBJ, P_SOL, P_HERR],
    petar=["altura"], pets="PETS - Trabajos en techos y coberturas", epp=["arnes"])
act("IIEE", "Instalaciones", "Instalaciones eléctricas y de comunicaciones",
    r"INSTALACIONES EL[EÉ]CTRICAS|TABLERO|CABLE|CONDUCTOR|TOMACORRIENTE|INTERRUPTOR|LUMINARIA|SALIDA(S)? DE|POZO A TIERRA|DATA|CCTV|ACOMETIDA",
    4, ["Electricista", "Ayudante"],
    [pel("Circuitos energizados", "Contacto eléctrico directo o indirecto", "Electrocución, quemaduras", "S", 2, 3,
         (N, N, "Interruptores diferenciales; herramientas aisladas", "Bloqueo y etiquetado (LOTO); PETAR eléctrico; pruebas de ausencia de tensión",
          EPP["guantes_diel"]), Dr=1),
     P_CAIDA_ALT, P_HERR],
    petar=["electrico", "altura"], pets="PETS - Instalaciones eléctricas", epp=["guantes_diel"])
act("IISS", "Instalaciones", "Instalaciones sanitarias, redes de agua y alcantarillado",
    r"INSTALACIONES SANITARIAS|AGUA FR[IÍ]A|AGUA CALIENTE|DESAG[UÜ]E|APARATOS SANITARIOS|RED DE AGUA|RED DE ALCANTARILLADO|CONEXI[OÓ]N DOMICILIARIA|PRUEBA HIDR[AÁ]ULICA|V[AÁ]LVULA",
    6, ["Operario gasfitero", "Peón"],
    [pel("Pegamentos y solventes de PVC", "Inhalación de vapores", "Mareos, irritación", "SO", 3, 1, (N, N, "Ventilación", "SDS", EPP["guantes_nitrilo"])),
     pel("Aguas residuales en redes existentes", "Contacto con agentes biológicos", "Enfermedades infecciosas", "SO", 2, 2,
         (N, N, N, "Vacunación (tétanos, hepatitis); higiene personal", EPP["guantes_nitrilo"] + ", botas de jebe"), Sr=1),
     P_CARGA, P_HERR],
    pets="PETS - Instalaciones sanitarias y redes")
act("CONF", "Instalaciones", "Trabajos en espacios confinados (buzones, cámaras, cisternas, reservorios)",
    r"BUZ[OÓ]N|C[AÁ]MARA DE|CISTERNA|RESERVORIO|TANQUE (ELEVADO|CISTERNA|S[EÉ]PTICO)|POZO (S[EÉ]PTICO|PERCOLADOR|DE BOMBEO|TUBULAR)", 4, ["Operario", "Peón", "Vigía"],
    [pel("Atmósfera deficiente en oxígeno o con gases tóxicos", "Asfixia o intoxicación", "Muerte", "S", 2, 3,
         (N, N, "Ventilación forzada; detector multigás calibrado", "PETAR de espacio confinado; vigía permanente; plan de rescate", "Arnés con trípode de rescate"), Sr=2)],
    petar=["confinado"], pets="PETS - Trabajos en espacios confinados", epp=["arnes"])
act("PINT", "Arquitectura", "Pintura, empastes y acabados",
    r"^PINTURA (L[AÁ]TEX|ESMALTE|ANTICORROSIVA|EN|DE (MUROS|CIELO|PAREDES|CARPINTER))|EMPASTE|BARNIZ|\bLACA\b|IMPERMEABILIZA", 4, ["Operario pintor", "Oficial"],
    [pel("Pinturas, barnices y solventes", "Inhalación de vapores orgánicos", "Intoxicación, dermatitis", "SO", 3, 2,
         (N, "Pinturas al agua", "Ventilación de ambientes", "SDS; almacenamiento lejos de fuentes de ignición", EPP["respirador_gases"]), Sr=1),
     P_CAIDA_ALT],
    petar=["altura"], pets="PETS - Pintura", epp=["respirador_gases"])
act("CARP", "Arquitectura", "Carpintería de madera y vidrios",
    r"CARPINTER[IÍ]A DE MADERA|PUERTA|VENTANA|VIDRIO|CRISTAL|MAMPARA|MUEBLE", 4, ["Operario carpintero", "Oficial"],
    [pel("Vidrios y planchas", "Cortes durante la manipulación e instalación", "Heridas profundas", "S", 2, 2,
         (N, N, "Ventosas y caballetes", "Manipulación en pareja", "Guantes anticorte y mangas protectoras"), Sr=1),
     P_HERR, P_CARGA],
    pets="PETS - Carpintería e instalación de vidrios")

ACT_BY = {a["cod"]: a for a in ACT}

# ------------------------------------------------------------------ partidas que no son trabajo físico (no generan peligros)
NO_FISICAS = re.compile(r"EQUIPO(S)? DE PROTECCI[OÓ]N|CAPACITACI[OÓ]N|RECURSOS PARA RESPUESTA|SE[NÑ]ALIZACI[OÓ]N TEMPORAL DE SEGURIDAD|"
                        r"PLAN (DE )?(SEGURIDAD|MONITOREO ARQUEOL)|ELABORACI[OÓ]N|IMPLEMENTACI[OÓ]N Y ADMINISTRACI|GASTOS|"
                        r"ENSAYO|CONTROL DE CALIDAD|ESTUDIO|EXPEDIENTE|SUPERVISI[OÓ]N|DIFUSI[OÓ]N|CHARLA|TALLER|PROGRAMA DE|MONITOREO|SIMULACRO|MECANISMOS|ADQUISICI[OÓ]N|"
                        r"MOBILIARIO", re.I)
SST_PARTIDA = re.compile(r"PROTECCI[OÓ]N (PERSONAL|COLECTIVA)|SEGURIDAD Y SALUD|CAPACITACI[OÓ]N EN SEGURIDAD|RESPUESTA ANTE EMERGENCIA|"
                         r"SE[NÑ]ALIZACI[OÓ]N TRANSITORIA DE SEGURIDAD|SE[NÑ]ALIZACI[OÓ]N TEMPORAL DE SEGURIDAD|PLAN DE SEGURIDAD|"
                         r"MANTENIMIENTO DE TR[AÁ]NSITO", re.I)

# ------------------------------------------------------------------ temas de capacitación
CAPACITACION_BASE = [
    ("Inducción en SST para trabajadores nuevos (reglamento interno, IPERC del puesto, derechos y obligaciones)", "Todo el personal nuevo", 4, "al ingreso"),
    ("Identificación de peligros, evaluación de riesgos y uso del ATS", "Todo el personal", 2, "trimestral"),
    ("Uso, conservación y reposición de EPP", "Todo el personal", 1, "trimestral"),
    ("Orden y limpieza en obra", "Todo el personal", 1, "semestral"),
    ("Primeros auxilios y evacuación de heridos", "Brigadistas y capataces", 4, "semestral"),
    ("Prevención y uso de extintores", "Brigadistas y almaceneros", 2, "semestral"),
    ("Plan de respuesta ante emergencias y simulacros", "Todo el personal", 2, "semestral"),
    ("Manejo defensivo y reglamento de tránsito", "Choferes y operadores", 4, "semestral"),
    ("Ergonomía y levantamiento manual de cargas (R.M. N.° 375-2008-TR)", "Todo el personal", 1, "semestral"),
    ("Riesgos psicosociales, hostigamiento sexual y bienestar", "Todo el personal", 1, "anual"),
    ("Investigación de incidentes y accidentes", "Supervisores, capataces y comité", 2, "anual"),
]
CAPACITACION_PETAR = {
    "altura": ("Trabajos en altura y uso del sistema de protección contra caídas", "Personal que trabaja en altura", 4),
    "excavacion": ("Excavaciones y zanjas: taludes, entibados y PETAR", "Personal de excavaciones", 2),
    "caliente": ("Trabajos en caliente y prevención de incendios", "Soldadores, asfaltadores y vigías", 2),
    "confinado": ("Espacios confinados: monitoreo de gases y rescate", "Personal autorizado y vigías", 4),
    "izaje": ("Izaje de cargas, señales al operador y aparejos", "Riggers, operadores de grúa y montajistas", 4),
    "electrico": ("Riesgo eléctrico, bloqueo y etiquetado (LOTO)", "Electricistas y personal autorizado", 4),
    "explosivos": ("Manipulación de explosivos y voladura controlada", "Perforistas y disparadores autorizados", 4),
    "cauces": ("Trabajos en cauces y rescate acuático básico", "Personal que trabaja sobre o junto a cauces", 2),
}
