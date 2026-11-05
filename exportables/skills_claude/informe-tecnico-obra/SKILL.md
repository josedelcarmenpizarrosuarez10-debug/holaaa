---
name: informe-tecnico-obra
description: "Mejorar o elaborar el informe técnico de culminación y consistencia del expediente técnico de un proyecto de inversión registrado en Invierte.pe (formato vigente de la fase de ejecución), para cualquier servicio y entidad: costo de inversión por activo calculado desde el presupuesto y los metrados, presupuesto por edificación o componente, metas físicas estudio viable vs expediente, causa de la variación, consistencia del presupuesto y del cronograma, conclusiones y recomendaciones, sin mover los montos finales. Entrega el informe final con lo nuevo resaltado, un Word con solo lo nuevo, el Excel de sustento con fórmulas, un Word de consultas y propuestas, un Word de pendientes que ubica cada error (página, cuadro, fila o celda) y un mensaje de un párrafo para el ingeniero. Usar cuando pidan revisar, corregir, sustentar o blindar ante la Contraloría un informe de consistencia."
---

# Informe técnico de culminación y consistencia del expediente técnico

Método general para cualquier proyecto de inversión pública registrado en Invierte.pe (instituciones educativas,
establecimientos de salud, locales municipales, CAR, vías, saneamiento, etc.) y para cualquier entidad. Cambian los activos,
las normas sectoriales y la estructura del modelo de la entidad; el método de reparto, los cotejos y los entregables se mantienen.
El caso de la sección "Ejemplo de referencia" solo ilustra: ninguna cifra suya se usa en otro informe.

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

**Reglas propias de este informe (criterio por defecto del usuario; confirmar en cada proyecto):**
- **"Mantenga los montos finales"**: subtotal, gestión del proyecto, expediente técnico, supervisión, costo de inversión,
  control concurrente, JRD (o los rubros que tenga el informe) y total quedan iguales al informe. Solo se reparten; nunca se
  suben ni se bajan. La **supervisión no se toca**. Si una corrección cambiaría un monto final, se plantea como opción en el
  Word de consultas.
- **No cambiar la estructura** del informe (títulos, numeración, orden de ítems). Se mejora solo lo pedido.
- Lo que el usuario pidió corregir **se corrige** en el informe (no se deja solo como sugerencia). Lo ambiguo, o lo que
  depende del ingeniero (metas, unidades, partidas del presupuesto), va al Word de consultas con opciones.
- **Todo lo nuevo o cambiado, resaltado en amarillo** en el informe final, y además en un Word aparte con solo lo nuevo.
- Los archivos del usuario son de solo lectura: se copian a una carpeta de insumos y se trabaja sobre la copia.
- El nombre, CIP o RUC del coordinador o firmante que figura en el informe original **no se reproduce** en los documentos
  nuevos. Usar siempre el nombre exacto de la **entidad del proyecto**; nunca el de otra entidad.
- Excel con fórmulas, sin protección; colores: **amarillo = datos, gris = cálculo, verde = resultado**.
- Mensajes para terceros (el ingeniero): **un párrafo, amable, entendible, sin preguntas**.
- Citar las tablas por **su número y página reales** en el informe (nunca un número inventado).

## 1. Insumos que hay que pedir
1. **Datos del proyecto:** nombre completo, CUI, entidad, unidad ejecutora, sector y tipo de servicio, ubicación.
2. Informe original en Word (y su PDF para ubicar páginas). Qué ítems mejorar y qué celdas están resaltadas para calcular.
3. **Modelo de informe de la entidad** y **formato de Invierte.pe que corresponde** (confirmar el formato y la directiva vigentes
   en el portal del MEF: se han renumerado y modificado varias veces).
4. Montos finales que no deben variar (los del informe).
5. Presupuesto del expediente técnico exportado a Excel (Delphin, S10 u otro): ítem, descripción, unidad, cantidad, precio,
   parcial; gastos generales, utilidad, IGV; hojas de mobiliario y equipamiento por ambiente (si existen).
6. **Todos** los metrados por especialidad: estructuras, arquitectura, demolición, instalaciones sanitarias, eléctricas (planilla y
   sustento por tablero), mecánicas, drenaje pluvial, comunicaciones, redes exteriores, mobiliario y equipamiento, y las propias
   del tipo de obra (equipamiento médico, pavimentos, obras de arte, etc.). Si el usuario dice que una especialidad "tiene que
   entrar", buscar en todos los archivos antes de decir que no hay metrado.
7. Cuadro de áreas o de metas "viable vs expediente" por ambiente, edificación o componente; ficha técnica o estudio viable;
   cronograma; PMA.
8. Datos del estudio viable: población objetivo, VAN, TIR, CAE, costo por beneficiario, monto viable.
9. **Normas sectoriales** que deben citarse y su versión vigente (criterios de diseño del ministerio del sector).

## 2. Estructura del informe (la del modelo de la entidad; conservarla)
Estructura típica (puede variar según la entidad y el formato vigente):
I y II. Datos generales y antecedentes del proyecto.
III. Población objetivo (beneficiarios por nivel o grupo, viable y modificado).
IV. Variación en el monto de inversión (cuadro viable vs modificado, % de variación; variación sustancial o no).
V. Evaluación social (monto a precios sociales, VAN, TIR, CAE, costo por beneficiario).
VI. Análisis: descripción; **evaluación de las metas físicas** ficha técnica / estudio vs expediente técnico, activo por activo;
**Cuadro de metas y costo de inversión por activo** (en el ejemplo, "Cuadro 01"); **análisis de la causa de la variación** del costo
de inversión; **evaluación de consistencia** en Invierte.pe: del presupuesto de obra (tabla de costo total del proyecto) y del
cronograma de ejecución.
VII. Conclusiones (con la estructura de costos). VIII. Recomendaciones.

## 3. Método: costo de inversión por activo y por edificación o componente
1. **Lugares**: edificaciones, obras complementarias, obras exteriores, redes exteriores (o tramos, componentes y frentes en obras
   lineales). Cada ambiente o elemento pertenece a un lugar y a un **activo** del cuadro de metas (los activos dependen del
   servicio: aulas por nivel y SUM en educación; consultorios, tópico y farmacia en salud; oficinas y atención al público en un
   local municipal; además cerco, espacios exteriores, instalaciones exteriores, mobiliario y equipamiento).
2. **Partidas con metrado por lugar**: se imputan al lugar según la cantidad del metrado. Emparejar metrado y presupuesto
   por código + cantidad, o descripción + cantidad, con tolerancia máx(0.05; 0.5 %). Si la numeración del metrado difiere
   del presupuesto, exigir que la cantidad coincida. Dentro de una edificación, el costo pasa a los ambientes por
   criterio (marca × peso, normalmente el área).
3. **Lugar único**: partidas que solo pueden estar en un sitio (cocina, losa deportiva, red exterior) van completas a él.
4. **Criterio general**: partidas sin metrado por lugar (obras provisionales, PMA, demoliciones, pruebas) se reparten en proporción
   al costo directo; las de SS.HH. sin batería, por los ambientes de SS.HH.
5. **Especialidades difíciles**: tableros eléctricos sin edificación → inferir por cargas y niveles y pedir confirmación en un
   cuadro; mecánicas por ambiente y por capacidad; comunicaciones por ambiente; sanitarias por las etiquetas de grupo de la
   planilla. Las filas sin lugar no se fuerzan a una edificación: siguen la proporción de las que sí lo tienen. Al emparejar
   artefactos, restringir al capítulo (que una luminaria de emergencia no se confunda con un tablero de emergencia).
6. **Mobiliario y equipamiento**: conteo por ambiente de su hoja del presupuesto; repartir en enteros por mayor resto.
7. Aplicar el factor del presupuesto (GG, utilidad, IGV) y la contingencia; la última fila de cada componente es la de
   cuadre para que la suma dé **exactamente** el subtotal del informe.
8. Informar la **cobertura**: % del costo directo repartido con metrado, por lugar único y por criterio general. Si queda una parte
   por criterio, explicar qué falta y qué metrado la completaría.

## 4. Cotejos que haría la Contraloría (hacerlos todos y ubicar cada hallazgo)
- Suma de componentes = costo de inversión; la supervisión del cuadro de metas igual a la de la tabla de costo total
  y a la de las conclusiones. Si no cuadra, mostrar las dos sumas y las opciones (A: valor que cuadra; B: valor del
  cuadro con el nuevo costo de inversión, control y total).
- Metas del cuadro vs la evaluación de metas físicas, activo por activo (cantidad y m²); comprobar cantidad × área unitaria con el
  cuadro viable vs expediente; detectar filas cruzadas entre tablas.
- Aritmética de los textos ("se incrementa en…", "variación de… unidades"): restar y comparar.
- Unidades de mobiliario y equipamiento del informe vs la hoja del presupuesto.
- Evaluación social: CAE en 0.00, VAC igual al monto a precios de mercado, costo por beneficiario = monto ÷ población.
- Porcentajes de variación (un 100 % sumado de más es un error frecuente).
- Encabezado del presupuesto: distrito y ubicación correctos.
- Cantidades del metrado vs presupuesto: efecto en costo directo y en el valor referencial con el factor; es decisión del
  ingeniero en el programa de presupuestos.
- Descripciones de partidas que difieren entre metrado, resumen y presupuesto (potencias, medidas).

## 5. Entregables
1. **Informe final** (Word): copia del original con el mismo formato; cuadro de metas con los costos por activo, causa de la
   variación, consistencia, conclusiones y recomendaciones mejorados y correcciones puntuales; todo lo nuevo en amarillo
   (`w:highlight` en el orden del esquema de `w:rPr`).
2. **Contenido nuevo** (Word): cuadro de metas original vs corregido; cuadro de presupuesto por edificación o componente
   (incluidos mobiliario, equipamiento y contingencia); textos nuevos; correcciones puntuales; puntos para revisión.
3. **Excel de sustento**: LEEME (fuentes y método), AMBIENTES, CRITERIOS, PARTIDAS (columnas por lugar), CRIT_LUGAR,
   DISTRIBUCION (INDEX/MATCH), MOBILIARIO_EQUIPAMIENTO, CUADRO_METAS (subtotal = SUMA; montos finales como datos amarillos).
   Recalcular con Excel o LibreOffice: 0 errores, sin "#####" (ancho de columna suficiente).
4. **Consultas y propuestas** (Word): cada tema con opciones y su efecto en los montos; información que falta; tabla de
   decisiones con la columna "Decisión" en blanco.
5. **Pendientes para cerrar el informe** (Word, A4 horizontal): un cuadro resumen (N.°, punto, dónde, prioridad) y,
   por cada punto: **Dónde está** (documento, página, cuadro o ítem, fila; o archivo, hoja, fila, celda), **Qué dice**
   (valores), **Por qué está mal** (con la cuenta), **Cómo se corrige** (opciones), **Qué enviar**, **Decisión**
   (casillas). Al final, lo que ya quedó resuelto y "cómo usar este documento".
6. **Mensaje para el ingeniero**: un párrafo que explique qué documento leer y qué devolver.

## 6. Redacción
- Formal, impersonal, sin adjetivos de venta; cada cifra con su fuente (presupuesto, metrado, cuadro, página).
- En la causa de la variación dejar claro que los montos por edificación **son parte del mismo costo de inversión**, no un
  monto adicional.
- Normas: la directiva general de Invierte.pe y el formato que correspondan, **en su versión vigente**, y las normas técnicas del
  sector del servicio (criterios de diseño, programas arquitectónicos). Verificar número y vigencia antes de citarlas; ver ejemplos
  al final.
- Si el usuario pregunta si el informe "ya cumple" ante un control futuro: responder con honestidad qué quedó sustentado
  y qué sigue abierto (los pendientes), sin prometer que no habrá observaciones.

## 7. Lista de control final
- [ ] Montos finales idénticos al informe; la suma de todos los valores repartidos = subtotal exacto; supervisión sin cambios.
- [ ] Cotejo informe original vs final: solo cambian los bloques previstos, y todos están en amarillo.
- [ ] Excel = cálculo (diferencia < 1e-6), 0 errores, fórmulas vivas, sin protección, colores de datos/cálculo/resultado.
- [ ] Cobertura de reparto informada; todos los metrados de la carpeta usados (o dicho por qué uno no se pudo usar).
- [ ] Cada tabla citada con su número y página reales; cada hallazgo con su ubicación exacta.
- [ ] Normas y formato de Invierte.pe citados en su versión vigente.
- [ ] Ningún nombre, CIP ni RUC del firmante original en los documentos nuevos; entidad correcta; nada que revele IA.
- [ ] Ningún dato, activo ni cifra de otro proyecto.
- [ ] Documentos vistos página por página (vista previa interna) antes de enviarlos; no se reenvía lo que no cambió.

## 8. Errores que el usuario ya corrigió (lecciones generales)
- Redactar la causa de la variación de modo que parezca que el presupuesto aumentó ("¿aumentaste el presupuesto? eso no
  debe variar"): el reparto nunca cambia el total.
- Dejar como sugerencia lo que el usuario había pedido corregir ("¿yo te dije que no corrijas?").
- Omitir especialidades habiendo metrados en la carpeta: revisar todos los archivos.
- Entregar el Word de pendientes como un resumen, sin decir en qué página, cuadro, fila o celda está cada error.
- Nombrar tablas con números que no existen en el informe: usar el nombre real y la página.
- Mandar cantidades exteriores a las edificaciones por filas sin lugar; confundir artefactos con tableros por nombre.
- Guardar una copia "_ACTUALIZADO" porque el archivo estaba abierto: pedir que lo cierre y mantener un solo archivo vigente.

## Ejemplo de referencia (solo para ilustrar; no copiar datos a otro informe)
- **Caso:** Informe N.° 044-2026 "Culminación y consistencia del expediente técnico" del proyecto "Mejoramiento y ampliación del
  servicio de educación primaria y secundaria en la I.E. N.° 0103, distrito de Chazuta, provincia y departamento de San Martín"
  (CUI 2688865), Gobierno Regional San Martín – GTBM. Informe de 26 páginas; 12 edificaciones (E-I a E-XII), obras complementarias
  (OC-xx) y exteriores (OE-xx), redes exteriores (REDEXT), mobiliario, equipamiento y contingencia.
- **Formato y normas citadas en ese caso** (verificar vigencia antes de reutilizarlas): Formato 08-A de Invierte.pe; Directiva
  General de Invierte.pe, R.D. N.° 001-2019-EF/63.01; MINEDU: R.S.G. N.° 239-2018-MINEDU, R.V.M. N.° 208-2019-MINEDU y
  R.V.M. N.° 164-2020-MINEDU.
- **Estructura del modelo:** 6.1 (6.1.1) descripción; 6.2 metas físicas; Cuadro 01 "Presupuesto de la Institución Educativa"
  (24 valores); 6.3 causa de la variación; 6.4.1 consistencia del presupuesto y 6.4.2 del cronograma; Cuadro 01-A por edificación.
- **Activos del Cuadro 01:** aula de primaria, aula de secundaria, AIP, biblioteca, SUM, circulación interior, administración,
  preparación de alimentos, servicios generales, almacén, SS.HH., cerco, espacio deportivo, espacio exterior, instalaciones
  exteriores; mobiliario y equipamiento por nivel (componente II, hoja HD del presupuesto; metrado HR).
- **Cifras del caso:** cobertura 96.55 % con metrado, 0.51 % por lugar único y 2.94 % por criterio general; variación escrita
  189.85 % que en realidad era 89.85 %; distrito equivocado en la celda D5 del presupuesto; 88 und en el metrado y 28 en el
  presupuesto; tableros eléctricos inferidos por tableros gemelos, estabilizados y de aire acondicionado; mecánicas por kBTU.
