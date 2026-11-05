---
name: gestion-riesgos-ejecucion-obra
description: Elaborar el estudio de gestión de riesgos en la planificación de la ejecución de obra (Ley N.° 32069 y su Reglamento, D.S. N.° 009-2025-EF, art. 156) para cualquier obra pública en el Perú: identificación, análisis cualitativo P x I, análisis cuantitativo (valor esperado y Monte Carlo), plan de respuesta, asignación, oportunidades y seguimiento, con efectos siempre en % del presupuesto de obra y nunca en soles. Entrega el Word con tablas y gráficos, la matriz de riesgos en Excel con fórmulas, el plano DXF de ubicación de riesgos, los anexos georreferenciados y, si hay observaciones del evaluador, el levantamiento de observaciones en Word aparte. Usar cuando el usuario pida una matriz de riesgos de obra, estudio o informe de gestión de riesgos, reserva de contingencia o absolver observaciones a ese estudio.
---

# Estudio de gestión de riesgos en la ejecución de obra

Ejemplo de referencia aprobado por el usuario: "Mejoramiento del servicio de transitabilidad vial interurbana en la vía
departamental SM-107, tramo Tingo de Ponasa – Shamboyacu" (CUI 2673852), 25.35 km, 5 puentes, 720 días: 34 riesgos,
3 oportunidades, P x I, valor esperado, Monte Carlo, planos PR-01 y PR-02 y levantamiento de 3 observaciones.
El método sirve igual para edificaciones (CAR, colegios, hogares) cambiando las categorías y la ubicación por ambientes o frentes.
Es un documento distinto del PSST (peligros a las personas) y de la evaluación de riesgo de desastres (EVAR).

## Reglas permanentes del usuario (no negociables)
- Todo en español. Entregables en **Word, Excel y DXF**; vistas previas en **PNG**; PDF solo si el usuario lo pide.
- **Escala real: 1 unidad = 1 m** ("si algo mide 0.56, así debe medir en el plano").
- Decir siempre **"cota de fondo"**.
- Citar cada proyecto por su **nombre completo y su CUI**. No mezclar partidas, láminas ni datos entre proyectos.
- **Nada en los documentos que revele el uso de IA.** Nombre y CIP del proyectista: **campos en blanco**.
- **No modificar** los metrados ni los documentos del usuario salvo pedido expreso; cambiar solo lo pedido y verificar
  que lo demás quede idéntico (cotejo antes y después).
- Partidas con nombres y estructura **Delphin**; cantidades siempre del metrado propio. Precios reales con su fuente;
  mano de obra CAPECO-FTCCP 2026 (operario 28.95, oficial 22.68, peón 20.54 S/ por hora) salvo que el usuario dé otra.
- Actualizar todo lo relacionado de forma coherente: **metrado ↔ planos ↔ especificaciones ↔ memoria**.
- **Cuando el usuario ya imprimió un plano, no se regenera**: los cambios van a los documentos y se le avisan.
- Las observaciones sobre documentos de otros profesionales van en una **nota de revisión interna**, nunca dentro del documento.
- No reenviar archivos que no cambiaron. Preguntar lo dudoso antes de producir, con una imagen de control si hace falta.
- Revisar el trabajo propio varias veces antes de entregar; decir con claridad lo que no se pudo comprobar.

**Reglas propias de este estudio:** ningún monto en soles en Word, Excel ni plano (todo efecto en **% del presupuesto de obra**
y en días); los componentes del presupuesto también en %; **sin sección ni hoja de "observaciones"** a los documentos de otros
(FTE, expediente, inventario) y sin textos que señalen diferencias entre ellos: si algo no cuadra, va como riesgo neutro
("subrasante de menor capacidad que la prevista") o en nota interna aparte.

## 1. Datos que hay que pedir
1. Ficha técnica (FTE) o expediente con su resumen ejecutivo: nombre, CUI, código de idea, entidad, unidad ejecutora, ubicación,
   modalidad (contrata o administración directa), fuente de financiamiento, plazo en días, metas físicas.
2. Presupuesto S10: costo directo, gastos generales, utilidad, IGV, presupuesto de obra, supervisión, gestión, control concurrente
   (solo para calcular porcentajes; no se publican los montos).
3. Estudios básicos: inventario vial o diagnóstico, topografía, mecánica de suelos, hidrología, canteras y DME, impacto ambiental,
   arqueología, predios e interferencias; panel fotográfico con fecha y coordenadas UTM; plano clave o planta con el eje.
4. Clima: lluvia mensual de estaciones cercanas (SENAMHI o NOAA) para el calendario de programación.
5. Si es levantamiento: el estudio tal como se presentó y el texto exacto de cada observación.

## 2. Marco normativo
Ley N.° 32069, Ley General de Contrataciones Públicas; su Reglamento (D.S. N.° 009-2025-EF), **art. 156** (matriz de riesgos en el
expediente de contratación: identificación, responsable, análisis cualitativo y cuantitativo; asignación a la parte que mejor
lo gestiona; comité de gestión de riesgos cuando la cuantía supera el monto del reglamento); Comunicado N.° 016-2025-OECE
(arts. 128 y 156 obligatorios sin esperar la directiva). La Directiva N.° 012-2017-OSCE/CD está **derogada** (Res. N.°
D000129-2025-OECE-PRE): citarla solo como referencia de método (escalas y formatos). Si la Dirección General de Abastecimiento
publica su directiva, adecuar los formatos. Normas sectoriales de la obra (EG-2013, DG-2018, Manual de Puentes, Manual de
Hidrología, Manual de Dispositivos de Control del Tránsito; RNE para edificaciones), Ley N.° 29664 (SINAGERD), Ley N.° 29783,
Ley N.° 27446 (SEIA), D.S. N.° 011-2022-MC (arqueología), Ley N.° 30025 (predios), Ley N.° 29338 (recursos hídricos).
Método: PMBOK y su estándar de gestión de riesgos; ISO 31000:2018.

## 3. Identificación
- Revisar todos los documentos y el recorrido del eje o del predio con relieve y lluvia; lista de verificación por categorías:
  diseño y expediente, geotecnia, clima y naturaleza, social y predios, permisos, interferencias, insumos y canteras, económico,
  ejecución, gestión del contrato, seguridad, ambiental.
- Registro por riesgo (código R-01...): evento (riesgo), causa (con datos concretos: volúmenes, alturas de talud, lluvias),
  efecto, ubicación (progresivas, sectores o ambientes), evidencia (documento y numeral, sin calificarlo), grupo de la ruta
  crítica (inicio, clima, terreno, gestión, otros), en ruta crítica sí/no.
- Oportunidades (O-01...): por ejemplo material de corte reutilizable, concentrar trabajos críticos en estiaje, compra anticipada.

## 4. Análisis cualitativo (P x I)
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
  distribución triangular. Si se estima en soles, convertir a precio de obra (costo directo x factor = subtotal x 1.18 / CD) y
  publicar solo el %.
- Valor esperado = P x media triangular, en % y en días (inherente y residual).
- Exposición de la Entidad: factor 1.0 Entidad, 0.5 compartido, 0 contratista; descontar lo que cubre la póliza CAR; sumar el
  costo por día de ampliación atribuible = (gastos generales x 1.18 + supervisión) / plazo, expresado en % del presupuesto por día.
- Monte Carlo (20,000 iteraciones, semilla fija = CUI para que sea reproducible): cada riesgo ocurre según su P; costo y retraso
  triangulares. Retrasos: solo los de ruta crítica; dentro de cada grupo se suma el mayor y el 25 % de los demás (concurrencia);
  los grupos se suman. Resultados P50, P80, P90 y media, inherente y residual: costo para la Entidad, costo del contratista,
  retraso total y retraso atribuible a la Entidad.
- **Reserva de contingencia recomendada = P80 residual del costo para la Entidad (% del presupuesto).**

## 6. Respuesta, asignación y seguimiento
- Estrategia: evitar, mitigar, transferir (póliza CAR, garantías), aceptar; oportunidades: explotar, mejorar, compartir, aceptar.
- Por riesgo: acciones concretas, responsable, partida que la financia (o gastos generales / reserva de la Entidad), momento
  (antes de la convocatoria, antes del inicio, ejecución) y **alerta temprana medible** (lluvia > 30 mm/día, subida de quebrada
  > 0.50 m en 24 h, desplazamiento de hitos > 2 cm, autorización no emitida 30 días antes del inicio...).
- Capítulos aparte: acciones previas a la convocatoria (las de mayor efecto: canteras, DME, certificación ambiental, predios,
  interferencias, revisión del expediente); programación según la lluvia (mes LLUVIOSO ≥ 110 mm, TRANSICIÓN ≥ 75 mm, ESTIAJE
  < 75 mm; en estiaje cimentaciones, terraplenes y carpeta; en lluvias obras de arte, cunetas y taller).
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
(valor esperado de los 15 mayores; Monte Carlo y lectura de resultados); 8 Plan de respuesta; 9 Asignación; 10 Oportunidades;
11 Organización y seguimiento; 12 Conclusiones y recomendaciones; 13 Anexos.
Figuras: mapa de ubicación de sectores y puntos, perfil del terreno y pendiente, lluvia mensual con temporadas, mapa de calor,
curvas de probabilidad acumulada del costo y del retraso. Tablas con número ("Tabla N.° 08") y fuente.

## 9. Plano DXF de riesgos (escala real, coordenadas UTM reales)
- **PR-01 Ubicación de riesgos**, 1/25,000, UTM WGS 84 (zona del proyecto): eje georreferenciado (del plano clave), curvas de
  nivel cada 10 m de un DEM público (Copernicus GLO-30, rotuladas como referenciales: incluye vegetación), localidades, puentes,
  sectores como polilíneas gruesas y puntos como círculos llenos, una capa y color por tipo (R-INUNDACION, R-EROSION, R-TALUDES,
  R-RIEGO, R-INTERFERENCIAS, R-PLATAFORMA, R-PREDIOS), llamadas con el código R-xx, leyenda, rótulo y norte.
- **PR-02 Diagrama lineal por progresiva** (horizontal 1/40,000): una fila por tipo de riesgo, barra de pendiente del entorno cada
  100 m (≥ 25° alto, 15-25° moderado, < 15° bajo), perfil de cotas, localidades y puentes, cuadro de riesgos por kilómetro.
- Para edificaciones: planta del predio con zonas de riesgo por ambiente o frente. Vista previa PNG de cada lámina.

## 10. Anexos y levantamiento de observaciones
- Anexos: registro completo; matriz impresa (todas las hojas como apartados A.1 a A.12); ubicación georreferenciada (tabla de
  puntos y sectores críticos y tabla de riesgos con progresiva y coordenadas UTM de inicio y fin, fichas con foto); panel fotográfico
  georreferenciado.
- Fotos: usar las que imprimen fecha y coordenadas; progresiva = proyección sobre el eje; un punto sin foto propia se registra
  con la foto de su sector a ≤ 500 m (indicar la distancia; las coordenadas del punto son las de la tabla); sin foto cercana =
  registro documental y su verificación de campo pasa a ser acción del plan de respuesta; riesgos globales = "No localizado".
- **Levantamiento de observaciones en Word aparte**: carátula; cuadro resumen (N.°, observación, absolución, ubicación en el
  estudio); por cada observación, cita textual, "Absolución:" y el contenido corregido (tablas completas como quedan); anexos.
- Si el usuario pide agregar al estudio presentado, **no tocar lo presentado**: anexar al final y comprobar que el cuerpo
  original quede idéntico (comparar elemento por elemento).

## 11. Verificación antes de entregar
- [ ] Ningún "S/" ni monto en soles en Word, Excel ni plano; todo en % y días. Buscar "S/" y cifras con millones.
- [ ] Sin sección u hoja de observaciones a documentos ajenos; textos neutros.
- [ ] Mismo número de riesgos, niveles, valores esperados y percentiles en Word, Excel y plano.
- [ ] Impacto coherente con el valor más probable; ALTO/MODERADO/BAJO con los umbrales; residuales con respuesta y momento.
- [ ] Coordenadas en el sistema y zona correctos; progresivas dentro del tramo; fotos con su distancia al eje.
- [ ] Nombre completo y CUI en carátula, pies y rótulos; sin nombres ni CIP; sin texto que revele IA.

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
