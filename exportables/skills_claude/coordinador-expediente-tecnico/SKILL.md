---
name: coordinador-expediente-tecnico
description: "Coordinar y revisar el trabajo de un expediente técnico de obra pública en el Perú de cualquier tipo (edificaciones, vías, saneamiento, drenaje pluvial, electrificación, obras exteriores) y de cualquier especialidad (drenaje, arquitectura, señalización, mobiliario, PSST, gestión de riesgos, renders, informes y presentación del expediente). Decide qué skill especializado usar para cada pedido, ordena el trabajo cuando hay varios entregables, pide los insumos que faltan y hace la revisión final de coherencia (metrado, planos, memoria y especificaciones) y de las reglas del usuario antes de entregar. Usar al inicio de cualquier pedido de expediente, cuando el pedido abarque varias especialidades y siempre como último paso antes de entregar archivos."
---
# Coordinador del expediente técnico

Este skill no produce los documentos por sí mismo: elige el skill especializado, ordena el trabajo, pide los insumos y revisa
todo al final. Sirve para cualquier proyecto y tipo de obra; los proyectos que citan los demás skills son solo ejemplos.

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

## 1. Qué skill usar
| Pedido del usuario | Skill |
|---|---|
| Pedido que abarca varias especialidades, orden de trabajo, revisión final antes de entregar | `coordinador-expediente-tecnico` (este) |
| Red de cunetas, drenaje pluvial de un local nuevo, descargas, cotas de fondo | `planteamiento-drenaje-pluvial` |
| Colector frontal cubierto, registros, cajas de llegada y de caída, empalme entre proyectos | `colector-pluvial-frontal` |
| Lluvia de diseño, análisis estadístico, IDF, caudales, memoria hidrológica | `hidrologia-drenaje-pluvial` |
| Metrado, planilla, resumen, ACU, precios, partidas Delphin | `metrado-drenaje-delphin` |
| Láminas DXF, plantas, perfiles, secciones, detalles, índice de planos | `planos-dxf-escala-real` |
| Memoria descriptiva, memoria de cálculo, especificaciones técnicas | `memorias-especificaciones-tecnicas` |
| Evacuación y señalización, equipamiento y mobiliario (metrado desde el plano) | `senalizacion-mobiliario-metrado` |
| Memoria de arquitectura, programación, incompatibilidades, sustento normativo | `revision-arquitectura-normativa` |
| Carátulas, lomos, separadores, índices, encabezados | `expediente-caratulas-lomos-indices` |
| Plan de Seguridad y Salud en el Trabajo, IPERC | `psst-iperc-obra` |
| Estudio de gestión de riesgos en la ejecución de obra, matriz de riesgos, reserva de contingencia | `gestion-riesgos-ejecucion-obra` |
| Renders, modelo 3D, maqueta, Blender, Cycles, Lumion | `renders-blender-lumion-modelo-3d` |
| Observaciones del evaluador, subsanar, corregir o anexar a un documento ya presentado | `levantamiento-observaciones-expediente` |
| Informe técnico de culminación o consistencia (Invierte.pe, Formato 08-A) de un expediente | `informe-tecnico-obra` |
| Asesoría de tesis (objetivos, resultados, discusión, formato de la universidad) | `tesis-academica` |
| El programa DrenIE: uso, licencias, versiones o mejoras | `programa-drenie` |

Si el pedido toca varias filas, se usan los skills en el orden de la sección 3. Si ninguno encaja (otra especialidad:
estructuras, sanitarias, eléctricas, vías...), se trabaja con las reglas de arriba y el orden genérico de la sección 3.1, y se
avisa que no hay skill específico para ese tema.

## 2. Insumos y datos que hay que pedir al inicio (cualquier proyecto)
1. **Identificación**: nombre completo, CUI (o código de inversión), entidad, unidad ejecutora, ubicación (distrito, provincia,
   departamento), tipo de obra, modalidad y plazo.
2. **Alcance del pedido**: qué especialidades y qué documentos (memoria, cálculo, metrado, presupuesto, especificaciones, planos,
   PSST, riesgos, renders, carátulas), en qué formato y para cuándo.
3. **Planos base** en DXF (planta general, topografía, arquitectura) con su sistema de coordenadas; láminas ya impresas (no se
   regeneran).
4. **Documentos del usuario** que mandan: metrado o planilla propia, presupuesto S10, cronograma, estudios básicos, modelo o
   formato de la entidad, documentos ya presentados y observaciones recibidas.
5. **Datos de presentación**: foto o vista del proyecto, logo y nombre de la entidad, diseño de carátula ya usado en el expediente.
6. **Criterios por confirmar** que dependen del proyecto (dimensiones mínimas, niveles, colores, normas de la entidad).
Si falta algo, preguntar antes de producir; si se supone algo, decirlo en el reporte.

## 3. Orden de trabajo
### 3.1 Orden genérico para cualquier especialidad
1. **Insumos** (sección 2) y lectura de lo que ya existe; separar lo del usuario (no se toca) de lo que se produce.
2. **Imagen de control** del planteamiento y preguntas de lo dudoso, antes de calcular o dibujar.
3. **Criterios y cálculo** de la especialidad (normas vigentes, datos del proyecto) → memoria de cálculo.
4. **Planos** con las dimensiones del cálculo → láminas e índice de planos.
5. **Metrado** con las cantidades de los planos → presupuesto, ACU y precios con fuente si se piden.
6. **Memoria descriptiva y especificaciones** con las mismas partidas, códigos y unidades del metrado.
7. **Documentos transversales** si se piden: PSST, gestión de riesgos, renders.
8. **Presentación**: carátulas, índices, separadores, lomos y encabezados.
9. **Revisión final** (sección 4) y entrega solo de lo que cambió.
### 3.2 Expediente de drenaje pluvial
1. Insumos: plano general (DXF con curvas), datos del proyecto, foto, serie de lluvia, metrado del usuario si existe,
   láminas ya impresas.
2. Imagen de control y preguntas: límite de intervención, NPT, techos, descargas, receptor del agua.
3. `hidrologia-drenaje-pluvial` → intensidad de diseño.
4. `planteamiento-drenaje-pluvial` (cunetas) y, si hay frente a la vía, `colector-pluvial-frontal`.
5. `planos-dxf-escala-real` → láminas e índice.
6. `metrado-drenaje-delphin` → metrado con las cantidades de los planos.
7. `memorias-especificaciones-tecnicas` → con las mismas partidas.
8. `expediente-caratulas-lomos-indices`.
9. Revisión final (sección 4).
### 3.3 Arquitectura, señalización y mobiliario
Lectura de los planos de la arquitecta → `revision-arquitectura-normativa` (nota interna, sin corregir el plano ajeno) →
`senalizacion-mobiliario-metrado` (metrado = lo dibujado) → memorias y especificaciones → `renders-blender-lumion-modelo-3d` si se piden.
### 3.4 PSST y gestión de riesgos
Presupuesto y cronograma → partidas → peligros (PSST) o riesgos (estudio) → matriz Excel con fórmulas → Word con tablas y
gráficos → plano de riesgos si corresponde. Cada uno en su carpeta y documento, sin mezclarse.
### 3.5 Observaciones e informes
Documento presentado + observaciones → `levantamiento-observaciones-expediente`; informe de consistencia →
`informe-tecnico-obra` con los documentos ya cerrados.

## 4. Revisión final antes de entregar (obligatoria)
**Coherencia entre documentos**
- [ ] Cada partida del metrado tiene su especificación con el mismo código, el mismo nombre y la misma unidad.
- [ ] Las cantidades de la memoria, del presupuesto y de los cuadros coinciden con el metrado (sin diferencias).
- [ ] Las láminas citadas en la memoria y en el índice existen con ese código y ese título.
- [ ] Las dimensiones de los planos coinciden con la memoria de cálculo (secciones, pendientes, niveles, cotas de fondo).
- [ ] El proyecto tiene el mismo nombre completo y el mismo CUI en todos los documentos; no hay datos de otro proyecto.
- [ ] Las normas citadas están vigentes y son las mismas en memoria, especificaciones y estudios.

**Reglas del usuario**
- [ ] No hay nombre ni CIP del proyectista; esos campos están en blanco.
- [ ] Ningún texto menciona IA, asistente o generación automática (revisar también propiedades del archivo: autor vacío).
- [ ] Se dice "cota de fondo".
- [ ] Los planos están a escala real; los textos no se enciman ni van verticales.
- [ ] Lo que el usuario no pidió cambiar está idéntico (cotejo valor por valor si se tocó un archivo suyo).
- [ ] Ningún plano ya impreso se regeneró.
- [ ] Cada valor de diseño sale de este proyecto o de una respuesta del usuario (ninguno copiado de un ejemplo).

**Archivos**
- [ ] Los archivos se abren sin error (Word, Excel con fórmulas recalculadas, DXF y PowerPoint).
- [ ] Hay vista previa PNG de lo gráfico.
- [ ] Solo se entregan los archivos que cambiaron, con nombres claros (proyecto y contenido en el nombre).

## 5. Cómo reportar al usuario
- Respuesta corta y en lenguaje sencillo: qué se hizo, qué archivos se entregan y qué falta confirmar.
- Las diferencias entre planos de otros profesionales se listan como "por confirmar con …", sin corregir su documento.
- Si algo no se pudo comprobar (por ejemplo, un programa que no se pudo abrir), decirlo con claridad.
- Los datos supuestos se listan aparte para que el usuario los confirme.
