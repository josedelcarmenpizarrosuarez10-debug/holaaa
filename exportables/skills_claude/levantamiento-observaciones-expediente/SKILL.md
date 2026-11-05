---
name: levantamiento-observaciones-expediente
description: "Levantar las observaciones del evaluador o del coordinador sobre un documento del expediente técnico ya presentado (estudio, memoria, especificaciones, metrado, PSST, gestión de riesgos, planos), y editar un Word, Excel o DXF del usuario sin romperlo. Parte siempre del archivo tal como fue presentado, responde observación por observación, agrega anexos o correcciones sin tocar lo demás, conserva la numeración, el encabezado y el pie, verifica por programa que el resto quedó idéntico y entrega un cuadro de levantamiento y un párrafo listo para el ingeniero. Usar cuando el usuario reciba observaciones, pida subsanar, corregir un documento presentado, quitar o renumerar capítulos o anexos, o agregar fotos y anexos a un Word ya enviado."
---
# Levantamiento de observaciones y edición de documentos ya presentados

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

## 1. Insumos
1. **El archivo tal como fue presentado** (el que envió el usuario, no una copia anterior: puede diferir).
2. El documento de **observaciones** del evaluador: texto, capturas o acta. Si llegan como imagen, transcribirlas y
   confirmar el texto con el usuario.
3. Los archivos de apoyo que hagan falta: metrado, planos, fotos, cronograma, presupuesto.
4. Si es un proyecto con varios documentos, preguntar cuáles más deben cambiar por coherencia.

## 2. Método
1. **Copia de trabajo**: nunca se edita el original; se trabaja sobre una copia con el mismo nombre más un sufijo de versión.
2. **Cuadro de observaciones**: una fila por observación, con N.°, texto literal, dónde está (capítulo, página, cuadro),
   qué se hizo, dónde quedó la respuesta (página, anexo, lámina) y estado (subsanada / por confirmar / no procede, con motivo).
3. **Responder en el lugar**: la corrección va donde está el problema (el cuadro, la ficha, la lámina), no en un párrafo suelto.
   "Otra solución" significa una opción distinta, no repetir la misma.
4. **Agregar sin tocar lo demás**:
   - Los anexos nuevos continúan la numeración existente (capítulos, tablas, figuras, cuadros, anexos).
   - El mismo encabezado, pie, estilos, fuente y márgenes del documento.
   - Los anexos nuevos **no** se titulan "subsanación" ni "levantamiento de observaciones": llevan su título técnico.
   - Si se quita un capítulo o anexo, se renumera lo que sigue, se corrigen todas las referencias cruzadas y las fuentes
     de los cuadros ("Anexo N.°…"), se actualiza el índice y no se deja ninguna referencia huérfana.
   - Antes de tocar el índice o la carátula, preguntar.
5. **Fotos y evidencia**: cada punto con su foto real y sus coordenadas. No inventar fotos ni coordenadas; las imágenes
   satelitales van rotuladas como tales. Una foto del sector (a menos de 500 m, en el mismo tramo) se rotula con su distancia.
   No dejar cuadros vacíos ni "foto por incorporar": si no hay foto, se indica "registro documental" y la acción pendiente.
   No borrar puntos sin foto sin antes mostrar al usuario dónde están citados.
6. **Dos pasos cuando es largo**: primero un Word aparte con lo nuevo para revisión; con la aprobación, recién se une al documento.
7. **Coherencia**: si la respuesta cambia una cantidad, se actualizan el metrado, la memoria, las especificaciones y los
   planos que la citan (salvo planos ya impresos: se avisa).

## 3. Edición técnica sin romper archivos
- **Word**: editar el XML del .docx (párrafos y runs) para no perder formato; unir runs antes de buscar texto. Mantener
  imágenes, secciones y encabezados con sus relaciones. Actualizar el índice abriendo con LibreOffice o dejando
  updateFields para que Word lo actualice al abrir.
- **Excel**: editar celdas sin reescribir el libro entero (respetar estilos, celdas combinadas y fórmulas) y recalcular
  con LibreOffice; comprobar que las fórmulas siguen siendo fórmulas.
- **DXF**: copia del archivo; cambiar solo las entidades observadas; no regenerar láminas ya impresas.
- Renderizar el resultado (PDF temporal a imágenes) y mirarlo página por página antes de entregar.

## 4. Verificación por programa (obligatoria)
- Comparar original y corregido: todo lo que no estaba observado debe quedar **idéntico** (texto párrafo por párrafo,
  tablas celda por celda, valores del Excel, entidades del DXF). Reportar el número de diferencias y que todas son las pedidas.
- Revisar que no queden referencias a capítulos, anexos, tablas o láminas que ya no existen.
- Revisar encabezados, pies y numeración de páginas en las partes nuevas.
- Revisar que no aparezcan el nombre ni el CIP del proyectista ni rastros de IA (también en las propiedades del archivo).

## 5. Entregables
1. El documento corregido (Word/Excel/DXF), con el nombre del original y la versión.
2. El **cuadro de levantamiento de observaciones** en Word (una fila por observación, con dónde quedó cada respuesta).
3. Si el usuario lo pide, la lista de **pendientes** (qué falta, quién lo debe dar y qué enviar).
4. Un **párrafo único**, sencillo y que no parezca escrito por una máquina, para mandar al ingeniero o al evaluador.

## 6. Lista de revisión final
- [ ] Se partió del archivo presentado, no de una copia anterior.
- [ ] Cada observación tiene su respuesta en el lugar y su fila en el cuadro.
- [ ] Lo no observado quedó idéntico (cotejo por programa).
- [ ] Numeración, índice, referencias cruzadas, encabezado y pie correctos.
- [ ] Sin cuadros vacíos, sin fotos inventadas, sin la palabra "subsanación" en los anexos.
- [ ] Coherencia con metrado, memoria, especificaciones y planos.
- [ ] Sin nombre ni CIP del proyectista; sin rastros de IA.
- [ ] Párrafo para el ingeniero listo.

## 7. Errores que el usuario ya corrigió (no repetirlos)
- Dejar cuadros con "fotografía por incorporar": se rechazó; o va foto real o va "registro documental".
- Responder "otra solución" con la misma solución.
- Tomar como base una copia distinta de la que se presentó.
- Titular los anexos nuevos como "subsanación".
- Citar números de foto en una tabla sin adjuntar las fotos.
- Explicaciones largas o con viñetas para el ingeniero: va un solo párrafo sencillo.
- Quitar un anexo y dejar referencias a él en el texto o en el índice.
- Modificar partes del documento del usuario que no se pidieron.
