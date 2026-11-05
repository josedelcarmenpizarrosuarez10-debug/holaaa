---
name: psst-iperc-obra
description: "Elaborar el Plan de Seguridad y Salud en el Trabajo (PSST) de cualquier tipo de obra en el Perú (edificación, vías, saneamiento, drenaje, puentes, electrificación) con su matriz IPERC según la R.M. N.° 050-2013-TR, la Norma G.050, la Ley N.° 29783 y su reglamento: reconocimiento de actividades desde el presupuesto, peligros y riesgos, probabilidad x severidad, nivel de riesgo, jerarquía de controles y riesgo residual, programas (EPP, PETS, PETAR, capacitación, inspecciones, monitoreo, emergencias, indicadores). Entrega un Word ordenado con tablas y gráficos y un Excel con fórmulas. Usar cuando el usuario pida un PSST, IPERC, matriz IPER, plan de seguridad de obra, actualizar uno existente o retirar o ajustar partes de un PSST suyo."
---

# PSST con matriz IPERC para cualquier obra en el Perú

Método estándar, no atado a un proyecto: con el presupuesto de la obra y unos datos generales se reconocen las actividades,
se arma la matriz IPERC (línea base, inicial y residual) y se derivan todos los programas del plan. El PSST va siempre
separado del estudio de gestión de riesgos de obra y de los expedientes de drenaje u otras especialidades.

## Reglas permanentes del usuario (valen para todo proyecto)
- Todo en español. Entregables en **Word, Excel y DXF**; vistas previas en **PNG**; PDF solo si el usuario lo pide.
- **Escala real: 1 unidad = 1 m** ("si algo mide 0.56, así debe medir en el plano").
- Decir siempre **"cota de fondo"**.
- Citar cada proyecto por su **nombre completo y su CUI** (o código de inversión). No mezclar partidas, láminas ni datos entre proyectos.
- **Nada en los documentos que revele el uso de IA.** Nombre y CIP del proyectista: **campos en blanco**.
- **No modificar** los metrados ni los documentos del usuario salvo pedido expreso; cambiar solo lo pedido y verificar
  que lo demás quede idéntico (cotejo antes y después).
- Partidas con nombres y estructura **Delphin**; cantidades siempre del metrado propio. Precios reales con su fuente y fecha;
  mano de obra según la tabla CAPECO vigente o la que indique el usuario.
- Actualizar todo lo relacionado de forma coherente: **metrado ↔ planos ↔ especificaciones ↔ memoria**.
- **Cuando el usuario ya imprimió un plano, no se regenera**: los cambios van a los documentos y se le avisan.
- Las observaciones sobre documentos de otros profesionales van en una **nota de revisión interna**, nunca dentro del documento.
- No reenviar archivos que no cambiaron. Preguntar lo dudoso antes de producir, con una imagen de control si hace falta.
- **Ningún dato de un proyecto anterior se usa en uno nuevo** (colores, dimensiones, niveles, lluvias, cantidades, nombres):
  todo sale de los planos y documentos del proyecto nuevo o se le pregunta al usuario. Los proyectos citados son solo ejemplos.
- Revisar el trabajo propio varias veces antes de entregar; decir con claridad lo que no se pudo comprobar.

## 1. Insumos y datos que hay que pedir
1. **Presupuesto**: PDF exportado de S10 o lista de partidas (ítem, descripción, unidad, metrado; los títulos sin unidad).
   Del S10 solo se usan ítem, descripción, unidad y metrado; los precios no intervienen y **los metrados no se tocan**.
   Si existe, la **lista de insumos** (horas-hombre de mano de obra) y el **costo directo** (para el % del presupuesto del plan).
2. **Proyecto**: tipo de obra (edificación, vía, saneamiento, riego, drenaje, puente, electrificación, otra), código corto, nombre
   completo, CUI, entidad, unidad ejecutora, ubicación (distrito, provincia, departamento), modalidad (contrata o administración
   directa), plazo en días, fecha prevista de inicio, altitud (msnm), clima y condiciones del lugar: `selva`, `altura`, `cauces`,
   `zona_poblada`, `transito`, `instalaciones_existentes` (local en funcionamiento, redes enterradas o aéreas).
3. **Cronograma** de obra y, si hay, el **histograma de trabajadores por mes** (o el calendario de adquisición de mano de obra).
4. **Frentes y procesos**: memoria descriptiva o resumen ejecutivo del expediente (componentes, metas, frentes simultáneos,
   subcontratistas previstos, obras colindantes o terceros en el sitio).
5. **Emergencia**: teléfonos y distancias locales (centro de salud más cercano, hospital de referencia, bomberos, PNP, defensa
   civil, aseguradora del SCTR).
6. Lo asignado al plan en la **preinversión** (si existe), para compararlo con el presupuesto del plan.
7. Si existe, el **PSST anterior o el modelo del usuario** (se respeta su formato y su numeración y solo se cambia lo que pida),
   y el formato que exija la entidad.
Si falta el histograma, calcular los obreros con las **horas-hombre de mano de obra de la lista de insumos del presupuesto**
entre las horas del plazo del cronograma (criterio por defecto del usuario; ver el ejemplo al final); si tampoco hay insumos,
suponer una cuadrilla razonable por mes y decirlo. Si falta un teléfono, dejar la celda amarilla para que el usuario lo confirme.

**Antes de producir nada:**
- Si el usuario solo pide confirmar el acceso o resumir el método, contestar en pocas líneas y **esperar sus instrucciones**.
- Si pregunta "¿sabes qué hacer?" sin indicar la obra, no arrancar: listar los datos que faltan (obra con nombre y CUI,
  presupuesto, personal por mes, condiciones del lugar, teléfonos), los pasos que se seguirán y **preguntar para qué obra es**.
- No tomar por iniciativa propia el presupuesto de otro estudio (por ejemplo, el de un estudio de gestión de riesgos) aunque
  sea el único disponible: ofrecerlo y esperar la confirmación; si se usa, el PSST va en su propia carpeta y sin mezclarse.
- Comprobar que estén las herramientas de gráficos, de lectura del PDF y la hoja de cálculo para recalcular; avisar si falta algo.

## 2. Marco normativo que se cita
**Antes de citar, verificar que cada norma siga vigente y con sus modificatorias** (las normas cambian: confirmar en El Peruano
o en el portal del MTPE/MVCS); si alguna fue derogada o reemplazada, citar la nueva y avisarlo al usuario.
Ley N.° 29783 y su reglamento D.S. N.° 005-2012-TR (art. 21: jerarquía de controles); D.S. N.° 011-2019-TR (Reglamento de SST
para el Sector Construcción); Norma G.050 Seguridad durante la construcción (contenido mínimo del plan); R.M. N.° 050-2013-TR
(formatos de registros e IPERC); R.M. N.° 375-2008-TR (ergonomía); R.M. N.° 312-2011-MINSA (vigilancia médica ocupacional);
SCTR (Ley N.° 26790 y D.S. N.° 003-98-SA); NTP 399.010-1 (señales de seguridad) y NTP de extintores; y las que correspondan a la
obra según su tipo: Manual de Dispositivos de Control del Tránsito del MTC (vías y obras en la vía pública), Código Nacional de
Electricidad (electrificación e instalaciones), normas de explosivos (SUCAMEC), normas de saneamiento y espacios confinados
(redes, buzones, PTAR), RNE (edificaciones).
Precisiones del modelo del usuario (criterio por defecto; confirmar en cada proyecto): el PSST **forma parte del expediente técnico** (D.S. N.° 011-2019-TR, art. 17) y sigue el
contenido mínimo del **art. 18**; numeral 17.1 = partida específica de SST en el presupuesto (y Norma Técnica de Metrados, R.D.
N.° 073-2010/VIVIENDA/VMCS-DNC); numeral 17.3 = el contratista y sus subcontratistas elaboran su propio PSST tomando este como
base, aprobado por el Subcomité o Comité de SST y presentado a la supervisión antes de iniciar. Indicar que la obra está en el
listado de actividades del sector construcción vigente. Registros obligatorios: art. 33 del D.S. N.° 005-2012-TR; IPERC: art. 77
(modificado por D.S. N.° 002-2020-TR). Requisitos contractuales: Ley N.° 32069 y su reglamento. Matriz de requisitos legales en
anexo (norma, requisito aplicable, cumplimiento en el plan).

## 3. Reconocimiento de actividades (desde las partidas)
- Cada actividad estándar se reconoce por palabras clave en la descripción de las partidas (y, si hace falta, por el título padre).
  Biblioteca base (36 actividades): generales a campo abierto; selva (fauna y vectores); altura > 2,500 msnm; traslado de personal;
  campamento y almacenes; movilización; topografía; mantenimiento de tránsito y desvíos; desbroce y tala; demoliciones; movimiento
  de tierras con maquinaria; corte en roca; excavación de zanjas; trabajos en cauces; rellenos y compactación; geosintéticos y
  subdrenaje; transporte con volquetes; acero; encofrado; concreto; gaviones y mampostería; tuberías y alcantarillas; pavimento
  asfáltico; estructuras metálicas; puentes; señalización vial; reubicación de postes; mantenimiento y combustible; gestión
  ambiental; albañilería y acabados; coberturas y techos; instalaciones eléctricas; sanitarias; espacios confinados; pintura; carpintería.
- **No generan peligros** (partidas no físicas): EPP, capacitación, señalización temporal de seguridad, planes, ensayos, control de
  calidad, estudios, expediente, supervisión, difusión, charlas, monitoreo, simulacros, adquisiciones, mobiliario.
- Las partidas de SST del presupuesto (protección personal y colectiva, capacitación, respuesta ante emergencias, señalización
  temporal, mantenimiento de tránsito) se listan aparte en el capítulo de partidas de SST.
- Siempre activas: actividades generales; selva si la condición lo indica; altura si altitud > 2,500 msnm; maquinaria si hay
  movimiento de tierras, asfalto, transporte o roca.
- Partidas que no encajan en ninguna actividad: **avisar la lista** y agregar la palabra clave o una actividad nueva con sus
  peligros; nunca dejar partidas físicas sin evaluar ni corregir a mano el resultado final.

## 4. Evaluación IPERC (R.M. N.° 050-2013-TR)
Por cada peligro: proceso, actividad, puestos, rutinaria (R) o no rutinaria (NR), peligro, riesgo, consecuencia, tipo
(S seguridad / SO salud ocupacional).

| Índice | 1 | 2 | 3 |
|---|---|---|---|
| A personas expuestas | 1 a 3 | 4 a 12 | más de 12 |
| B procedimientos | existen y son satisfactorios | parciales | no existen |
| C capacitación | entrenado, conoce el peligro | parcialmente | no entrenado |
| D exposición | esporádica (anual) | eventual (mensual) | permanente (diaria) |
| S severidad | lesión sin incapacidad / disconfort | incapacidad temporal / daño reversible | incapacidad permanente, muerte / irreversible |

- A = índice de min(cuadrilla de la actividad, pico de personal). **Inicial: B = 2 y C = 2**; **residual: B = 1 y C = 1**
  (PETS, ATS, capacitación y supervisión implementados) y D, S reducidos solo si un control de ingeniería lo justifica
  (criterio por defecto del usuario; confirmar en cada proyecto si la entidad o el modelo del usuario usan otro).
- Probabilidad = A + B + C + D (4 a 12). Nivel de riesgo = probabilidad x severidad (4 a 36):
  **4 Trivial; 5 a 8 Tolerable; 9 a 16 Moderado; 17 a 24 Importante; 25 a 36 Intolerable**.
- Significativo = Importante o Intolerable. Interpretación: Importante = no comenzar hasta reducirlo; Intolerable = no comenzar
  ni continuar; si no se puede reducir, prohibir el trabajo.
- **Todo peligro debe quedar en Moderado o menos en el residual**; si no, reforzar controles (no bajar índices sin control).
- Controles en el orden de la jerarquía (art. 21): eliminación, sustitución, ingeniería, administrativos, EPP. Escribir "No aplica"
  cuando no corresponda, nunca dejar vacío.
- Peligros comunes que casi toda obra tiene (agregar los propios del tipo de obra: tránsito y voladura en vías; zanjas,
  buzones y espacios confinados en saneamiento; trabajos en altura y acabados en edificaciones; energía en electrificación):
  radiación solar y calor (D3 S2), lluvia y tormenta eléctrica (regla 30-30, SENAMHI), sismo, ofidios y vectores (selva),
  altitud, manipulación de cargas (> 25 kg con ayuda mecánica), herramientas manuales (cinta de color del mes),
  superficies irregulares, polvo, ruido > 85 dB(A), maquinaria en movimiento (vigía, alarma de retroceso, D3 S3),
  tránsito de terceros (D3 S3), equipos eléctricos portátiles (diferencial y tierra), vibración, cemento, caída de altura > 1.80 m
  (barandas de 1.00 m con rodapié, línea de vida, arnés), caída de objetos, izaje, soldadura, combustibles, carga psicosocial.

## 5. Programas que salen del IPERC
- **EPP por puesto**: básico (casco con barbiquejo, lentes, calzado con puntera, chaleco reflectivo, guantes de cuero) más el
  específico de cada actividad (respirador P100 o para vapores, protector auditivo, arnés, careta de soldar, botas de jebe,
  guantes de nitrilo o dieléctricos, polainas, salvavidas, bloqueador, repelente, ropa impermeable), con su norma (ANSI, NIOSH, ASTM).
- **PETS**: uno por actividad. **PETAR** solo los que apliquen: altura (≥ 1.80 m), excavaciones (> 1.50 m), caliente, espacios
  confinados, izaje, eléctrico, explosivos (**solo si hay voladura explícita en el presupuesto**), cauces. ATS y charla de 5 minutos diarios.
- **Capacitación** (horas y frecuencia): inducción 4 h al ingreso; IPERC y ATS 2 h trimestral; EPP 1 h trimestral; orden y limpieza;
  primeros auxilios 4 h; extintores 2 h; emergencias y simulacros 2 h; manejo defensivo 4 h; ergonomía; psicosociales y hostigamiento;
  investigación de incidentes; más una por cada PETAR y las de selva, maquinaria y tránsito si aplican. Cronograma por mes con X.
- **Inspecciones**: pre-uso de maquinaria (diaria), frentes y ATS (diaria), herramientas, EPP, extintores y botiquines, campamento,
  instalaciones eléctricas (mensual), almacén de combustibles (semanal); andamios, excavaciones (diaria y después de lluvias),
  izaje y cauces según los PETAR.
- **Monitoreo de agentes** solo de los que aparecen en el IPERC: ruido (dosimetría, 85 dB(A) 8 h), polvo y sílice, vibración
  (ISO 5349 / 2631), estrés térmico (WBGT), vapores y humos, monóxido de carbono, radiación UV, ergonomía.
- **Organización** (D.S. N.° 011-2019-TR): con menos de 20 trabajadores, **supervisor de SST** elegido el primer día (art. 23);
  de 20 a 100, **Subcomité de SST** bipartito y paritario de **4 titulares** (2 del empleador, 2 de los trabajadores; numeral 27.1),
  que sesiona al menos una vez al mes y lleva libro de actas; si el contratista tiene una sola obra, **Comité de SST**. Al pasar de
  20 trabajadores se inicia la elección del subcomité. Perfil del especialista en SST: profesional colegiado y habilitado, con
  capacitación en SST de construcción, permanente en obra y sin funciones de producción (sin nombres).
- **Indicadores**: HHT = trabajadores x 8 h x 26 días; IF = accidentes x 1,000,000 / HHT; IG = días perdidos x 1,000,000 / HHT;
  IA = IF x IG / 1,000. Metas: cero accidentes mortales, 100 % de inducción, cumplimiento de programas ≥ 90 %.
- **Emergencias**: escenarios (accidente grave, incendio, sismo, lluvias e inundación, mordedura de ofidio, electrocución,
  derrame), brigadas (primeros auxilios, contra incendio, evacuación), flujograma de comunicación y directorio.

## 6. Word del PSST (Norma G.050 y D.S. N.° 011-2019-TR)
Carátula (nombre completo y CUI, entidad, fecha; sin nombres ni CIP), índice actualizable y capítulos:
1 Generalidades (objetivo, alcance, datos de la obra, componentes del presupuesto, histograma de personal); 2 Marco normativo;
3 Política, objetivos, metas e indicadores; 4 Organización (organigrama, funciones, comité o supervisor); 5 IPERC (metodología,
actividades evaluadas, resultados inicial y residual, mapa de calor, intolerables, jerarquía de controles); 6 Mapa de riesgos y
señalización; 7 Procedimientos (PETS, PETAR, ATS, charla diaria); 8 EPP y protección colectiva; 9 Capacitación con cronograma;
10 Inspecciones y auditorías; 11 Salud ocupacional (exámenes, SCTR, monitoreo, bienestar, primeros auxilios); 12 Subcontratistas
y proveedores; 13 Respuesta ante emergencias; 14 Notificación e investigación de accidentes; 15 Registros obligatorios,
indicadores y mejora continua; 16 Partidas de SST del presupuesto; 17 Anexos (IPERC completo, EPP por puesto, formato de ATS,
lista de verificación del PETAR).
**Estructura de ejemplo del usuario** (la de un PSST suyo de edificación, ver el ejemplo al final): **si el usuario trae su
propio plan o el formato de la entidad, se usa ese** y se respeta su numeración; si no trae nada, se propone esta o la anterior.
1 Generalidades (nombre, entidad y unidad ejecutora, ubicación, naturaleza y vigencia); 2 Objetivo
(general y específicos); 3 Alcance de la obra (descripción, **condiciones del sitio con incidencia en la SST**: condición | dato del
expediente | implicancia; plazo, **frentes** con procesos y peligros predominantes, personal estimado; alcance del plan); 4 Sistema
de gestión del empleador (documentos en obra, autorización de visitas, control de alcohol y drogas, **interrupción de actividades
por peligro inminente**, coordinación con subcontratistas y obras colindantes); 5 Política; 6 Presupuesto; 7 Organización
(organigrama, responsabilidades, perfil del especialista); 8 Elementos del plan (8.1 objetivos, metas e indicadores; 8.2
subcomité; 8.3 requisitos legales; 8.4 IPERC: metodología, resultados, ATS y PETAR; 8.5 mapa de riesgos; 8.6 vigilancia de la
salud; 8.7 PETS de alto riesgo; 8.8 capacitación; 8.9 registros; 8.10 inspecciones; 8.11 investigación; 8.12 auditorías; 8.13
mejora continua; 8.14 emergencias; 8.15 EPP por puesto; 8.16 señalización). Anexos: requisitos legales, matriz IPERC, mapa de
riesgos, PETS (cada uno con objetivo, alcance, responsables, EPP, equipos, procedimiento, restricciones, registros), capacitación
y programa de SST, inspecciones, vigilancia de la salud, emergencias (emergencias posibles, alerta, brigadas, antes/durante/después,
simulacros, autoridades y gestión del riesgo de desastres, directorio) y presupuesto del plan.
- **Presupuesto del plan**: cuadro resumen; % del costo directo de la obra; comparar con lo asignado en la preinversión y explicar
  la diferencia (número de obreros, capacitación mensual, agua para consumo); la señalética de la etapa de operación (Norma A.130)
  no entra; honorarios del especialista y exámenes médicos van en gastos generales. Anexo: cálculo del número de trabajadores
  (horas-hombre de insumos y plazo), detalle por subpartida y resumen. Las cantidades del presupuesto de obra no se tocan.
- Resultados del IPERC en el texto: número de combinaciones actividad-peligro y de procesos, cuadro inicial vs residual, número de
  significativos iniciales y las actividades que los concentran (caída de altura, derrumbe de zanja, espacio confinado...) con su PETAR.
- Cuadros y figuras numerados ("Cuadro N.° x") con su fuente; la fuente cita el anexo exacto (revisarla si se renumeran anexos).
- Tablas de ancho fijo con encabezado repetido; IPERC en sección horizontal A3 o A4 apaisada; títulos numerados; pie con el nombre
  corto del plan y página.
- Gráficos (PNG 200 ppp): histograma de personal; mapa de calor probabilidad x severidad inicial y residual; barras de niveles
  inicial vs residual; peligros por proceso; organigrama; pirámide de jerarquía de controles; flujograma de emergencias;
  cronograma de capacitación. Cada figura con número, título y fuente ("matriz IPERC del plan").

## 7. Excel con fórmulas
Celda amarilla = dato editable; celda verde = fórmula. Hojas: INDICE, DATOS, CRITERIOS, IPERC, RESUMEN, MAPA DE CALOR, EPP,
PETS-PETAR, CAPACITACION, INSPECCIONES, MONITOREO, INDICADORES, PARTIDAS (trazabilidad partida-actividad), EMERGENCIA.
- IPERC (34 columnas): identificación (N.°, proceso, actividad, puestos, R/NR, peligro, riesgo, consecuencia, S/SO); inicial
  A, B, C, D (amarillo), `=SUM(A..D)`, S, `=P*S`, nivel `=IF(x<=4,"Trivial",IF(x<=8,"Tolerable",IF(x<=16,"Moderado",IF(x<=24,"Importante","Intolerable"))))`,
  significativo `=IF(OR(nivel="Importante",nivel="Intolerable"),"Sí","No")`; controles en 5 columnas de la jerarquía; residual con
  las mismas fórmulas; PETS y PETAR. Formato condicional de colores por nivel (Trivial verde oscuro, Tolerable verde claro,
  Moderado amarillo, Importante naranja, Intolerable rojo), filtros, paneles inmovilizados, impresión A3 apaisada con títulos.
- RESUMEN y MAPA DE CALOR con `COUNTIF`/`COUNTIFS` sobre la hoja IPERC (se actualizan si se cambia un índice).
- CAPACITACION: veces `=COUNTIF(meses,"X")` y horas totales `=horas*veces`. INDICADORES: HHT, IF, IG, IA mensuales y acumulados
  con `IF(HHT=0,0,...)` para no dividir entre cero.
- Recalcular con LibreOffice y comprobar que ninguna celda dé error (#VALUE!, #REF!, #NAME?).

## 8. Verificación antes de entregar
- [ ] Todas las partidas físicas tienen actividad; lista de no reconocidas vacía o explicada al usuario.
- [ ] Ningún peligro residual en Importante o Intolerable; los significativos iniciales tienen controles de ingeniería o administrativos concretos.
- [ ] Conteos del Word = conteos del Excel (peligros, niveles inicial y residual, significativos, actividades, PETAR).
- [ ] PETAR solo los que aplican; explosivos solo con voladura en el presupuesto; selva y altura según el lugar.
- [ ] Supervisor, subcomité (4 titulares) o comité según el pico de personal; histograma igual al dato del usuario o calculado
      con las horas-hombre de insumos (y dicho).
- [ ] La obra, su presupuesto y el alcance los confirmó el usuario; nada tomado de otro estudio u obra sin su visto bueno.
- [ ] Presupuesto del plan: % del costo directo, comparación con la preinversión explicada, sin señalética de operación.
- [ ] Al retirar o renumerar una parte: cero referencias huérfanas (buscar "Anexo NN" y "numeral" en todo el texto, índice,
      lista de anexos, fuentes de cuadros, PETS y matriz de requisitos legales) y lo demás idéntico al original (cotejo).
- [ ] Nombre completo y CUI en carátula y pies; sin nombres ni CIP; sin texto que revele IA; nada de otro proyecto.
- [ ] Excel recalculado sin errores; Word revisado en vista previa (índice actualizado, tablas que no se cortan mal, figuras legibles).
- [ ] Informar al usuario lo que no se pudo comprobar y los datos supuestos (teléfonos, personal, condiciones del lugar).

## 9. Errores que el usuario ya corrigió (no repetirlos)
- El programa del PSST es **general**: no dejar planes de una obra de ejemplo dentro del programa ni generar el PSST de una obra
  si el usuario no lo pidió (se retiró uno de una vía que se había generado sin pedido).
- No mezclar el PSST con el estudio de gestión de riesgos de obra: son documentos y matrices distintos (IPERC de peligros a
  personas vs. matriz de riesgos del proyecto en costo y plazo).
- Al pedir "borra la parte que dice firma" (o retirar cualquier capítulo o anexo) se retira esa parte y se **renumera todo lo
  que dependía**: el anexo siguiente pasa a ocupar su número; se ajustan la lista de anexos, el índice (entradas y páginas,
  dejando el campo para que Word lo actualice al abrir), los numerales que lo citaban, el texto de los PETS, las fuentes de los
  cuadros y la matriz de requisitos legales. Donde un texto remitía a lo retirado, se reescribe sin la remisión (nunca un
  "ver Anexo NN" que ahora apunta a otra cosa). Lo retirado no se vuelve a poner en ese plan salvo pedido.
- Ante una pregunta general ("¿sabes qué hacer?") no se generó nada: se pidieron la obra y los datos. Mantener esa conducta;
  la conversación del programa general es solo para el programa (no se generan ni modifican PSST de obras sin instrucción).
- Al editar el Word del usuario, conservar su formato, estilos e imágenes; trabajar sobre una copia y cotejar que lo demás quede igual.
- No escribir nombres ni CIP de profesionales: dejar líneas en blanco para firmas y colegiaturas.
- No corregir a mano el Word o el Excel final para tapar una actividad faltante: ampliar la biblioteca y volver a generar.

## Ejemplo de referencia (solo ilustrativo; sus datos no se usan en otra obra)
- PSST del CAR Mujeres (CUI 2717013), edificación: estructura de capítulos de la sección 6 ("estructura de ejemplo del usuario").
  Sin histograma en el expediente, se calcularon 78 obreros en 10 meses con las horas-hombre de los insumos entre el plazo.
  El usuario pidió "borra la parte 9 que dice firma": se retiró el anexo de formatos con firma (ATS, PETAR, visitas, EPP,
  inspección y reporte), se quitaron sus 8 entradas del índice y se corrieron 3 páginas las siguientes, y se renumeró todo lo que
  dependía de él (anexos, numerales, PETS, fuente del cuadro de presupuesto, matriz de requisitos legales).
- Un PSST de una vía generado sin pedido dentro del programa general se retiró: el programa queda sin obras de ejemplo.
