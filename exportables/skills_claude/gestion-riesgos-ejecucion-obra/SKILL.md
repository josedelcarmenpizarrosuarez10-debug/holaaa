---
name: gestion-riesgos-ejecucion-obra
description: "Elaborar el estudio de gestión de riesgos en la planificación de la ejecución de obra (Ley N.° 32069 y su Reglamento, D.S. N.° 009-2025-EF, art. 156) para cualquier obra pública en el Perú: identificación, análisis cualitativo P x I, análisis cuantitativo (valor esperado y Monte Carlo), plan de respuesta, asignación, oportunidades y seguimiento, con efectos siempre en % del presupuesto de obra y nunca en soles. Entrega el Word con tablas y gráficos, la matriz de riesgos en Excel con fórmulas, el plano DXF de ubicación de riesgos, los anexos georreferenciados y, si hay observaciones del evaluador, el levantamiento de observaciones en Word aparte. Usar cuando el usuario pida una matriz de riesgos de obra, estudio o informe de gestión de riesgos, reserva de contingencia o absolver observaciones a ese estudio."
---

# Estudio de gestión de riesgos en la ejecución de obra

Método general para cualquier obra pública: **obras lineales** (vías, canales, redes de agua y alcantarillado, líneas
eléctricas), ubicadas por progresivas sobre un eje, y **obras puntuales** (edificaciones, colegios, establecimientos de salud,
PTAR, reservorios, puentes), ubicadas por frentes, sectores o ambientes del predio. Las categorías, la escala y la ubicación se
adaptan al tipo de obra; todos los datos salen de los documentos del proyecto. El caso que el usuario aprobó está al final como
"Ejemplo de referencia" y no se copia a otra obra.
Es un documento distinto del PSST (peligros a las personas) y de la evaluación de riesgo de desastres (EVAR).

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

**Reglas propias de este estudio:** ningún monto en soles en Word, Excel ni plano (todo efecto en **% del presupuesto de obra**
y en días); los componentes del presupuesto también en %; **sin sección ni hoja de "observaciones"** a los documentos de otros
(FTE, expediente, inventario) y sin textos que señalen diferencias entre ellos: si algo no cuadra, va como riesgo neutro
("subrasante de menor capacidad que la prevista") o en nota interna aparte.

## 1. Insumos y datos que hay que pedir
1. Ficha técnica (FTE) o expediente con su resumen ejecutivo: tipo de obra, nombre, CUI, código de idea, entidad, unidad
   ejecutora, ubicación, modalidad (contrata o administración directa), sistema de contratación, fuente de financiamiento,
   plazo en días, fecha prevista de convocatoria e inicio, metas físicas.
2. Presupuesto S10: costo directo, gastos generales, utilidad, IGV, presupuesto de obra, supervisión, gestión, control concurrente
   (solo para calcular porcentajes; no se publican los montos).
3. Estudios básicos: inventario vial o diagnóstico del local o del sistema existente, topografía, mecánica de suelos, hidrología, canteras y DME, impacto ambiental,
   arqueología, predios e interferencias (redes, postes, canales, local en funcionamiento); panel fotográfico con fecha y
   coordenadas UTM; plano clave con el eje (obra lineal) o planta general del predio (obra puntual) en DXF georreferenciado.
4. Clima: lluvia mensual de estaciones cercanas (SENAMHI o NOAA) para el calendario de programación.
5. Si es levantamiento: el estudio **tal como se presentó** (el archivo que sube el usuario, no una versión propia: puede diferir
   en encabezado, imágenes o filas) y el texto exacto de cada observación (cita textual, con el numeral que señala el evaluador).
6. Memoria descriptiva, cronograma de obra (ruta crítica), estudio de suelos y el **EVAR** del proyecto si existe (para no
   contradecir sus peligros); para edificaciones, el plan de frentes y si el local sigue funcionando durante la obra.
7. El formato o modelo que exija la entidad y, si hay, la carátula del expediente (para usar el mismo diseño).
Mínimo indispensable: presupuesto S10, plazo, modalidad y resumen ejecutivo; si algo falta, decir qué quedó supuesto.

Antes de empezar, comprobar si el estudio ya existe (de otro profesional) para revisarlo o completarlo, y no confundirlo con el
PSST ni con el EVAR. Si solo hay carátula o índice, decirlo y preguntar si se elabora desde cero.

## 2. Marco normativo
**Antes de citar, verificar que cada norma y artículo sigan vigentes** (reglamentos, directivas y comunicados del OECE cambian
seguido): si hay versión nueva, citarla y avisarlo al usuario.
Ley N.° 32069, Ley General de Contrataciones Públicas; su Reglamento (D.S. N.° 009-2025-EF), **art. 156** (matriz de riesgos en el
expediente de contratación: identificación, responsable, análisis cualitativo y cuantitativo; asignación a la parte que mejor
lo gestiona; comité de gestión de riesgos cuando la cuantía supera el monto del reglamento); Comunicado N.° 016-2025-OECE
(arts. 128 y 156 obligatorios sin esperar la directiva). La Directiva N.° 012-2017-OSCE/CD está **derogada** (Res. N.°
D000129-2025-OECE-PRE): citarla solo como referencia de método (escalas y formatos). Si la Dirección General de Abastecimiento
publica su directiva, adecuar los formatos. Normas sectoriales de la obra (EG-2013, DG-2018, Manual de Puentes, Manual de
Hidrología, Manual de Dispositivos de Control del Tránsito para vías; RNE para edificaciones; normas de saneamiento del MVCS
para agua y alcantarillado; Código Nacional de Electricidad para energía), Ley N.° 29664 (SINAGERD), Ley N.° 29783,
Ley N.° 27446 (SEIA), D.S. N.° 011-2022-MC (arqueología), Ley N.° 30025 (predios), Ley N.° 29338 (recursos hídricos).
Método: PMBOK y su estándar de gestión de riesgos; ISO 31000:2018.

## 3. Identificación
- Revisar todos los documentos y el recorrido del eje (obra lineal) o del predio (obra puntual) con relieve y lluvia; lista de verificación por categorías:
  diseño y expediente, geotecnia, clima y naturaleza, social y predios, permisos, interferencias, insumos y canteras, económico,
  ejecución, gestión del contrato, seguridad, ambiental.
- Registro por riesgo (código R-01...): evento (riesgo), causa (con datos concretos: volúmenes, alturas de talud, lluvias),
  efecto, ubicación (progresivas, sectores o ambientes), evidencia (documento y numeral, sin calificarlo), grupo de la ruta
  crítica (inicio, clima, terreno, gestión, otros), en ruta crítica sí/no.
- Oportunidades (O-01...): por ejemplo material de corte reutilizable, concentrar trabajos críticos en estiaje, compra anticipada.
- **Evidencia desde el primer día**: el evaluador pide foto con coordenadas de cada punto o riesgo identificado, y el usuario
  espera que "si se identificó, debe haber foto". Al armar la tabla de puntos críticos y el registro, anotar por cada punto su
  progresiva, coordenadas UTM de inicio y fin y la foto que lo respalda. Revisar todas las imágenes de todos los documentos
  (JPG y PNG del inventario, resumen ejecutivo, FTE): muchas fotos traen fecha, hora y coordenadas impresas por la cámara.
  Si un punto sale de un registro histórico sin fotos (por ejemplo, una tabla de zonas críticas antigua por progresivas),
  marcarlo así en el registro interno y pedir la foto de campo antes de presentar, no después.
- Ubicación de riesgos sin lugar físico (gestión, contrato, financiamiento, permisos): "No localizado". Cantera, fuente de agua,
  DME o arqueología sin coordenadas en el expediente: "ubicación por definir".
- Progresiva de cada foto y punto = proyección sobre el eje georreferenciado; si el inventario da otra progresiva, usar la del
  eje (la misma de los planos del estudio).

## 4. Análisis cualitativo (P x I)
Escalas y umbrales: criterio por defecto del usuario; confirmar en cada proyecto (o usar los de la entidad si los fija).

| Nivel | Probabilidad | Impacto | Costo (% del presupuesto de obra) | Plazo |
|---|---|---|---|---|
| Muy bajo/a | 0.10 | 0.05 | < 0.1 % | < 7 días |
| Bajo/a | 0.30 | 0.10 | 0.1 a 0.5 % | 7 a 21 días |
| Moderado/a | 0.50 | 0.20 | 0.5 a 1.5 % | 21 a 45 días |
| Alto/a | 0.70 | 0.40 | 1.5 a 4.0 % | 45 a 90 días |
| Muy alto/a | 0.90 | 0.80 | > 4.0 % | > 90 días |

- El impacto sale del **valor más probable** de costo y de plazo del análisis cuantitativo; se toma el mayor de los dos niveles
  (así el cualitativo y el cuantitativo quedan amarrados).
- Nivel: **ALTO si P x I ≥ 0.18; MODERADO de 0.05 a 0.18; BAJO < 0.05**. Tratamiento: ALTO = respuesta obligatoria antes del
  inicio o de la actividad y seguimiento mensual del comité; MODERADO = respuesta planificada; BAJO = se acepta y se vigila.
- Residual: probabilidad después de ejecutar la respuesta en su momento (el impacto se mantiene salvo que la respuesta lo reduzca).

## 5. Análisis cuantitativo
- Por riesgo: costo (mín., más probable, máx.) en % del presupuesto de obra y retraso (mín., más probable, máx.) en días,
  distribución triangular. Si se estima en soles, convertir a precio de obra (CD x factor = subtotal x (1 + IGV) / CD) y publicar solo el %.
- Valor esperado = P x media triangular, en % y en días (inherente y residual).
- Exposición de la Entidad: factor 1.0 Entidad, 0.5 compartido, 0 contratista; descontar lo que cubre la póliza CAR; sumar el
  costo por día de ampliación atribuible = (gastos generales x (1 + IGV) + supervisión) / plazo, expresado en % del presupuesto por día.
- Monte Carlo (20,000 iteraciones, semilla fija = CUI para que sea reproducible): cada riesgo ocurre según su P; costo y retraso
  triangulares. Retrasos: solo los de ruta crítica; dentro de cada grupo se suma el mayor y el 25 % de los demás (concurrencia);
  los grupos se suman. Resultados P50, P80, P90 y media, inherente y residual: costo para la Entidad, costo del contratista,
  retraso total y retraso atribuible a la Entidad.
- **Reserva de contingencia recomendada = P80 residual del costo para la Entidad (% del presupuesto)** (criterio por defecto del
  usuario; confirmar si la entidad fija otro percentil).

## 6. Respuesta, asignación y seguimiento
- Estrategia: evitar, mitigar, transferir (póliza CAR, garantías), aceptar; oportunidades: explotar, mejorar, compartir, aceptar.
- Por riesgo: acciones concretas, responsable, partida que la financia (o gastos generales / reserva de la Entidad), momento
  (antes de la convocatoria, antes del inicio, ejecución) y **alerta temprana medible** (lluvia > 30 mm/día, subida de quebrada
  > 0.50 m en 24 h, desplazamiento de hitos > 2 cm, autorización no emitida 30 días antes del inicio...).
- Capítulos aparte: acciones previas a la convocatoria (las de mayor efecto: canteras, DME, certificación ambiental, predios,
  interferencias, revisión del expediente, verificación en campo con foto georreferenciada de los puntos que solo tienen
  registro documental); programación según la lluvia (criterio por defecto: mes LLUVIOSO ≥ 110 mm, TRANSICIÓN ≥ 75 mm,
  ESTIAJE < 75 mm; confirmar con la lluvia del lugar): en estiaje lo sensible al agua (excavaciones, cimentaciones, terraplenes,
  carpetas, coberturas); en lluvias lo que tolera la lluvia o va bajo techo (obras de arte, acabados interiores, taller).
- Asignación a quien controla la causa: Entidad (decisiones, permisos, predios, interferencias, financiamiento, expediente),
  contratista (métodos, equipos, suministros, calidad, seguridad, lluvias previsibles), compartido (causas mixtas).
- Comité de gestión de riesgos, revisión mensual, formato de seguimiento y actualización de la matriz.

## 7. Excel de la matriz (amarillo = dato, verde = fórmula)
Hojas: INDICE, DATOS (incluye costo diario de ampliación en %), ESCALAS (probabilidad e impacto, umbrales, matriz P x I con
`=$B5*$B12`), IDENTIFICACION, ANALISIS CUALITATIVO (probabilidad con lista desplegable y `VLOOKUP`; nivel de impacto en costo
`=1+(E>umbral1)+(E>umbral2)+...`, ídem plazo; `=MAX(...)`; `INDEX` del valor; `=P*I`; nivel `=IF(PxI>=0.18,"ALTO",IF(PxI>=0.05,"MODERADO","BAJO"))`;
residual igual; conteos `COUNTIF`), ANALISIS CUANTITATIVO (media `=AVERAGE(mín:máx)`, valor esperado, exposición de la Entidad
`=P*media*factor*fr+IF(ruta="SI",P*días*factor*costo_día,0)`, totales), MONTE CARLO (resultados como valores, se indica que
salen de la simulación), MAPA DE CALOR, PLAN DE RESPUESTA, ASIGNACION (con conteos), OPORTUNIDADES, SEGUIMIENTO (formato
mensual con nivel recalculado por fórmula), CALENDARIO (lluvia mensual y temporada por fórmula). Formato condicional por nivel,
impresión apaisada. Recalcular con LibreOffice: cero errores.

## 8. Word del estudio
Carátula (entidad, título, nombre completo, CUI; sin especialista ni CIP) e índice. Capítulos: 1 Aspectos generales (objetivo,
alcance, diferencia con la EVAR, datos del proyecto); 2 Marco normativo; 3 Descripción del proyecto y su entorno (ubicación y
trazo, componentes en %, estado y puntos críticos con fotos, relieve, clima); 4 Metodología (con las tablas de escalas); 5
Identificación; 6 Análisis cualitativo (tabla ordenada por P x I y mapa de calor inherente y residual); 7 Análisis cuantitativo
(valor esperado de los mayores, p. ej. los 15 primeros; Monte Carlo y lectura de resultados); 8 Plan de respuesta; 9 Asignación; 10 Oportunidades;
11 Organización y seguimiento; 12 Conclusiones y recomendaciones; 13 Anexos.
Figuras: mapa de ubicación de sectores y puntos, perfil del terreno y pendiente, lluvia mensual con temporadas, mapa de calor,
curvas de probabilidad acumulada del costo y del retraso. Tablas con número ("Tabla N.° 08") y fuente.

**Carátula en Word** con el mismo diseño de las carátulas que ya tiene el expediente de ese proyecto (para que todo el expediente
se vea igual), de arriba abajo: escudo y nombre de la entidad (y la gerencia u oficina, si la usan), "EXPEDIENTE TÉCNICO DEL
PROYECTO DE INVERSIÓN:", nombre completo y CUI, vista de la obra (3D o foto), franja del color del proyecto con
**"GESTIÓN DE RIESGOS"** y debajo "EN LA PLANIFICACIÓN DE LA EJECUCIÓN DE LA OBRA", vista aérea del terreno, ubicación
(distrito, provincia, región) y fecha "MES - AÑO". Sin especialista ni CIP. Si el usuario pide solo la carátula, entregarla
sola, en la carpeta propia del estudio de ese proyecto, y ofrecer variantes (fecha, título largo, línea de la gerencia).

## 9. Plano DXF de riesgos (escala real, coordenadas UTM reales)
Obra lineal: las dos láminas siguientes. Obra puntual: planta del predio (o del entorno) con zonas de riesgo por frente, sector
o ambiente, accesos, colindantes, redes e interferencias, con la misma lógica de capas, llamadas, leyenda y rótulo.
Escalas, nombres de capa y códigos de lámina se adaptan a cada proyecto (ver el ejemplo al final).
- **Ubicación de riesgos** (escala según la extensión), UTM WGS 84 de la zona del proyecto: eje o predio georreferenciado,
  curvas de nivel de un DEM público si no hay topografía (Copernicus GLO-30, rotuladas como referenciales: incluye vegetación),
  localidades, accesos y estructuras, sectores como polilíneas gruesas y puntos como círculos llenos, una capa y color por tipo
  de riesgo (inundación, erosión, taludes, interferencias, predios...), llamadas con el código R-xx, leyenda, rótulo y norte.
- **Diagrama lineal por progresiva** (solo obra lineal): una fila por tipo de riesgo, barra de pendiente del entorno cada 100 m
  (criterio por defecto: ≥ 25° alto, 15-25° moderado, < 15° bajo), perfil de cotas, localidades y estructuras, cuadro por km.
  Vista previa PNG de cada lámina.

## 10. Anexos y levantamiento de observaciones
- Anexos: registro completo; matriz impresa (todas las hojas como apartados A.1 a A.12); ubicación georreferenciada (tabla de
  puntos y sectores críticos y tabla de riesgos con progresiva y coordenadas UTM de inicio y fin, fichas con foto); panel fotográfico
  georreferenciado.
- Fotos: usar las que imprimen fecha y coordenadas; progresiva = proyección sobre el eje; riesgos globales = "No localizado".
  Punto sin foto propia: la foto georreferenciada más cercana **del mismo tramo, a ≤ 500 m**, rotulada "F-06 (vista del sector, a 44 m)";
  las coordenadas que se publican son las del punto, no las de la foto. Nunca poner la foto de otro lugar como propia ni inventar
  coordenadas. Una imagen satelital solo como "imagen satelital", nunca como foto de campo.
- **Sin recuadros vacíos ni "fotografía por incorporar" / "fotos por completar"**: el punto sin foto a ≤ 500 m va como
  "Registro documental" con sus coordenadas exactas y una acción del plan de respuesta: la Entidad lo verifica en campo con foto
  georreferenciada antes de la convocatoria. Si luego llegan fotos de campo, se reemplaza sin tocar nada más.
- **No borrar puntos o riesgos porque les falte foto**: antes de quitar algo, buscar dónde se cita (tablas, anexos, conclusiones,
  recomendaciones, matriz, planos); quitarlo deja el estudio incoherente y "esconde" peligros. Explicarlo al usuario con esa tabla.
- **Fichas junto a la tabla** (el evaluador no debe buscar la foto en otro anexo): debajo de la tabla de coordenadas,
  - una ficha por punto crítico: título "FICHA 11 - km 37+520 a 37+780 - Inestabilidad de talud h = 30 m (LI)"; a la izquierda
    progresiva, descripción, coordenadas UTM de inicio y fin y código del riesgo relacionado; a la derecha la foto con su número,
    progresiva, coordenadas, fecha y hora (y la distancia si es del sector); sin foto: nota de registro documental, sin recuadro;
  - una ficha por riesgo localizado: categoría, riesgo, ubicación (la misma de la tabla de riesgos) y cada punto con progresiva y
    coordenadas; dos fotos representativas y "Ver también" con las demás; los riesgos sin lugar físico se listan al final con una
    nota (no hay lugar que fotografiar).
  - Formato: anchos de tabla fijos (que la foto no se recorte), título unido a su contenido (no partir la ficha entre páginas),
    dos fotos lado a lado, panel de 4 fotos por página; revisar cada página en imagen antes de entregar.
- **Levantamiento en dos pasos**: (1) primero un Word aparte solo con lo absuelto, para que el usuario lo revise: carátula;
  cuadro resumen (N.°, observación, absolución, ubicación en el estudio); por cada observación, cita textual, "Absolución:" y el
  contenido corregido (tablas completas como quedan); anexos; (2) cuando lo apruebe, se une al estudio presentado.
- **Unión al estudio presentado sin tocarlo** (no varía ni una letra; ya se envió): el archivo que subió el usuario es la base;
  se agregan al final anexos nuevos que continúan la numeración del capítulo de anexos (13.3, 13.4, 13.5...) y de las tablas
  (si la última es la Tabla N.° 14, siguen 15, 16, 17), con el mismo encabezado y pie de página del original, **sin las palabras
  "observación", "subsanación" ni "absolución"**. Contenido típico: matriz impresa completa (hojas
  apaisadas), ubicación georreferenciada (tablas que complementan las observadas + fichas) y panel fotográfico (A fotos;
  B puntos con foto de su sector y su distancia; C registro documental). Comprobar con un programa que todo lo anterior
  a los anexos quedó idéntico (elemento por elemento) e informar las páginas antes y después. El índice del inicio no se toca:
  preguntar si se agregan las líneas de los anexos nuevos. Si la observación buscaba algo en un anexo y ahora está en otro,
  decirlo en la respuesta ("la matriz se adjunta impresa en el Anexo 3 y en Excel").
- Al cerrar, revisar **observación por observación y tabla por tabla** que lo pedido se vea en el documento (no solo
  referenciado por número), decir cuál queda completa y cuál tiene un punto débil, y dar al usuario un **párrafo listo para
  enviar al ingeniero** (qué se agregó, dónde, criterio de fotos, qué queda como registro documental y por qué).

## 11. Verificación antes de entregar
- [ ] Ningún "S/" ni monto en soles en Word, Excel ni plano; todo en % y días. Buscar "S/" y cifras con millones.
- [ ] Sin sección u hoja de observaciones a documentos ajenos; textos neutros.
- [ ] Mismo número de riesgos, niveles, valores esperados y percentiles en Word, Excel y plano.
- [ ] Impacto coherente con el valor más probable; ALTO/MODERADO/BAJO con los umbrales; residuales con respuesta y momento.
- [ ] Coordenadas en el sistema y zona correctos; progresivas dentro del tramo; fotos con su distancia al eje.
- [ ] Nombre completo y CUI en carátula, pies y rótulos; sin nombres ni CIP; sin texto que revele IA.
- [ ] Cada punto crítico y cada riesgo localizado con foto propia, foto de sector (≤ 500 m, con distancia) o "Registro documental"
      con acción de verificación en el plan de respuesta; ningún recuadro vacío ni "por completar"; ninguna foto inventada.
- [ ] Levantamiento: cada observación citada textualmente y respondida donde el evaluador la buscará (fichas con foto junto a la
      tabla observada, no solo números de foto); cuadro resumen con ubicación en el estudio.
- [ ] Unión al presentado: base = archivo del usuario; cuerpo idéntico comprobado por programa; anexos con numeración
      continua de capítulo y tablas, mismo encabezado y pie; sin "observación" ni "subsanación"; índice sin tocar salvo pedido.
- [ ] Fichas revisadas en imagen: no se parten entre páginas, fotos sin recortar y lado a lado.

## 12. Errores que el usuario ya corrigió (no repetirlos)
- La primera versión traía montos en soles: se cambió todo (costos, valor esperado, Monte Carlo, reserva, componentes del
  presupuesto) a % del presupuesto de obra en Word, Excel y planos.
- Se había incluido una sección y una hoja de "observaciones" a los documentos del expediente: se eliminaron, y también las frases
  que comparaban documentos.
- El evaluador observó que la matriz citada en el anexo no estaba adjunta: adjuntarla siempre impresa dentro del estudio, además
  del Excel con fórmulas.
- Pidió fotografías con coordenadas para la tabla de riesgos y la de puntos críticos: cada riesgo localizado lleva progresiva,
  coordenadas UTM y foto georreferenciada.
- El estudio ya presentado se conserva sin cambios; lo nuevo va como anexos al final o en el levantamiento aparte.
- El estudio va en su propia carpeta y documento, separado del PSST y de los expedientes de drenaje; un proyecto nuevo, carpeta nueva.
- Carátulas con el diseño del proyecto (logo de la entidad, foto de la obra), sin nombre ni CIP del especialista.
- Se entregó un levantamiento con recuadros "FOTOGRAFÍA POR INCORPORAR": el usuario lo rechazó ("si lo identificaste, debe
  haber fotografía"). Primero agotar las fotos de todos los documentos (aparecen fotos en las imágenes del inventario), luego foto
  de sector a ≤ 500 m y el resto como registro documental con acción de verificación; nunca dejar vacíos visibles.
- Al pedir "otra solución" no hay que insistir en la misma (fotos de campo): ofrecer una alternativa distinta y aplicable con
  lo que hay (fotos por sector), explicando su punto débil.
- El usuario quiso borrar los puntos sin foto: se le mostró dónde estaba citado cada uno en lo presentado (tabla, conclusiones,
  recomendaciones, matriz, planos) y se mantuvieron; aun el que no tenía otras citas se dejó por coherencia con el inventario.
- La absolución de una tabla observada solo remitía a fotos por número en otro anexo: el usuario preguntó "¿adjuntaste
  fotografías?" y hubo que agregar fichas con sus fotos junto a esa tabla. Contestar cada tabla observada en su sitio.
- La versión presentada no era igual a la del repositorio (encabezado, una imagen más, una fila menos): la base es siempre el
  archivo que el usuario envió, guardado tal cual.
- Los anexos nuevos no dicen "subsanación" ni "observación": se agregan como anexos normales del estudio.
- Ante "dime texto para explicar al ingeniero", entregar un solo párrafo corrido, formal y concreto, listo para copiar.

## Ejemplo de referencia (solo ilustrativo; sus datos no se usan en otra obra)
"Mejoramiento del servicio de transitabilidad vial interurbana en la vía departamental SM-107, tramo Tingo de Ponasa –
Shamboyacu" (CUI 2673852), obra lineal de 25.35 km, 5 puentes, 720 días: 34 riesgos, 3 oportunidades, P x I, valor esperado,
Monte Carlo (semilla = CUI), planos PR-01 (1/25,000) y PR-02 (1/40,000, capas R-INUNDACION, R-EROSION, R-TALUDES, R-RIEGO,
R-INTERFERENCIAS, R-PLATAFORMA, R-PREDIOS) y levantamiento de 3 observaciones. En el levantamiento se completaron fichas con
foto para las Tablas N.° 04 (puntos críticos) y N.° 08 (riesgos) y se agregaron los Anexos 3 (matriz impresa), 4 (ubicación
georreferenciada) y 5 (panel fotográfico); de 31 puntos sin foto, 2 se cubrieron con fotos halladas en las PNG del inventario
y el resto con foto de sector a ≤ 500 m o como registro documental.
