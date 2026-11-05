---
name: coordinador-expediente-tecnico
description: Coordinar y revisar el trabajo de un expediente técnico de obra pública en el Perú (drenaje pluvial, colector, cunetas, arquitectura, señalización, mobiliario, PSST, gestión de riesgos, renders y presentación del expediente). Decide qué skill especializado usar para cada pedido, ordena el trabajo cuando hay varios entregables, pide los insumos que faltan y hace la revisión final de coherencia (metrado ↔ planos ↔ memoria ↔ especificaciones) y de las reglas del usuario antes de entregar. Usar al inicio de cualquier pedido de expediente o cuando el pedido abarque varias especialidades, y siempre como último paso antes de entregar archivos.
---
# Coordinador del expediente técnico

Este skill no produce los documentos por sí mismo: elige el skill especializado, ordena el trabajo y revisa todo al final.

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

## 1. Qué skill usar
| Pedido del usuario | Skill |
|---|---|
| Red de cunetas, drenaje de un local nuevo, descargas, cotas de fondo | `planteamiento-drenaje-pluvial` |
| Colector frontal cubierto, registros, cajas de llegada y de caída, empalme entre proyectos | `colector-pluvial-frontal` |
| Lluvia de diseño, análisis estadístico, IDF, caudales, memoria hidrológica | `hidrologia-drenaje-pluvial` |
| Metrado, planilla, resumen, ACU, precios, partidas Delphin | `metrado-drenaje-delphin` |
| Láminas DXF, perfiles, secciones, detalles, índice de planos | `planos-dxf-escala-real` |
| Memoria descriptiva, memoria de cálculo, especificaciones técnicas | `memorias-especificaciones-tecnicas` |
| Evacuación y señalización, equipamiento y mobiliario (metrado desde el plano) | `senalizacion-mobiliario-metrado` |
| Memoria de arquitectura, incompatibilidades, sustento normativo | `revision-arquitectura-normativa` |
| Carátulas, lomos, separadores, índices, encabezados | `expediente-caratulas-lomos-indices` |
| Plan de Seguridad y Salud en el Trabajo, IPERC | `psst-iperc-obra` |
| Estudio de gestión de riesgos en la ejecución de obra | `gestion-riesgos-ejecucion-obra` |
| Renders, modelo 3D, IFC, Revit, Dynamo | `renders-revit-modelo-3d` |

Si el pedido toca varias filas, se usan los skills en el orden de la sección 2. Si ninguno encaja, se trabaja con las
reglas de arriba y se avisa que no hay skill para ese tema.

## 2. Orden de trabajo de un expediente de drenaje completo
1. **Insumos**: plano general (DXF con curvas), nombre completo, CUI, ubicación, entidad, foto, serie de lluvia, metrado
   o planilla del usuario si existe, láminas ya impresas (estas no se regeneran).
2. **Imagen de control** y preguntas: cerco, NPT, techos, descargas, receptor del agua.
3. `hidrologia-drenaje-pluvial` → intensidad de diseño.
4. `planteamiento-drenaje-pluvial` (cunetas) y, si hay frente a la vía, `colector-pluvial-frontal`.
5. `planos-dxf-escala-real` → láminas e índice de planos.
6. `metrado-drenaje-delphin` → metrado con las cantidades de los planos.
7. `memorias-especificaciones-tecnicas` → memorias y especificaciones con las mismas partidas del metrado.
8. `expediente-caratulas-lomos-indices` → carátulas, índices y encabezados.
9. **Revisión final** (sección 3) y entrega.
Para PSST y riesgos el orden es: presupuesto y cronograma → partidas → peligros o riesgos → matriz Excel → Word.

## 3. Revisión final antes de entregar (obligatoria)
**Coherencia entre documentos**
- [ ] Cada partida del metrado tiene su especificación con el mismo código, el mismo nombre y la misma unidad.
- [ ] Las cantidades de la memoria y de los cuadros coinciden con el metrado (sin diferencias).
- [ ] Las láminas citadas en la memoria y en el índice existen con ese código y ese título.
- [ ] Las dimensiones de los planos coinciden con la memoria de cálculo (sección, pendiente, cotas de fondo).
- [ ] El proyecto tiene el mismo nombre completo y el mismo CUI en todos los documentos; no hay datos de otro proyecto.

**Reglas del usuario**
- [ ] No hay nombre ni CIP del proyectista; esos campos están en blanco.
- [ ] Ningún texto menciona IA, asistente o generación automática (revisar también propiedades del archivo: autor vacío).
- [ ] Se dice "cota de fondo".
- [ ] Los planos están a escala real; los textos no se enciman ni van verticales.
- [ ] Lo que el usuario no pidió cambiar está idéntico (cotejo valor por valor si se tocó una planilla suya).
- [ ] Ningún plano ya impreso se regeneró.

**Archivos**
- [ ] Los archivos se abren sin error (Word, Excel con fórmulas recalculadas, DXF y PowerPoint).
- [ ] Hay vista previa PNG de lo gráfico.
- [ ] Solo se entregan los archivos que cambiaron, con nombres claros (proyecto y contenido en el nombre).

## 4. Cómo reportar al usuario
- Respuesta corta y en lenguaje sencillo: qué se hizo, qué archivos se entregan y qué falta confirmar.
- Las diferencias entre planos de otros profesionales se listan como "por confirmar con …", sin corregir su documento.
- Si algo no se pudo comprobar (por ejemplo, un programa que no se pudo abrir), decirlo con claridad.
