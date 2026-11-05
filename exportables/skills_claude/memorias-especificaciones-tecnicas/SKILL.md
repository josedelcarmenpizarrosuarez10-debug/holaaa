---
name: memorias-especificaciones-tecnicas
description: Redactar y armar en Word los documentos escritos del expediente técnico de drenaje pluvial (y de otras especialidades con el mismo método): memoria descriptiva, memoria de cálculo (Excel con fórmulas y su versión PDF si se pide), capítulo agregado a la memoria hidrológica, especificaciones técnicas por partida Delphin (descripción, materiales, equipos, procedimiento, control, seguridad, unidad, medición y pago), carátulas, encabezados y pies, índice (TOC) actualizado, relación de planos y figuras tomadas de las láminas. Garantiza coherencia con el metrado y los planos. Usar cuando se pida una memoria, especificaciones, carátulas, encabezados o revisar que los documentos cuadren con el metrado y las láminas.
---
# Memorias, especificaciones técnicas y documentos Word del expediente

Proyectos de referencia (ejemplos, no mezclar datos): Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514), CAR Varones
(CUI 2705619), CAR Mujeres (CUI 2717013), I.E. N.° 0590 Barranquita (C.I. 468901). Detalle completo en `referencias/08_documentos_del_expediente.md`
(formatos, estructura, cronología) y `referencias/06_metrado_acu_especificaciones.md` (§13 especificaciones, árbol de partidas).

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

## 1. Insumos que hay que pedir
| Insumo | Uso | Regla |
|---|---|---|
| Metrado vigente (Excel, hoja RESUMEN y hojas de detalle) | partidas y cantidades de todos los documentos | solo lectura; recalcular una copia con LibreOffice antes de leer valores |
| PDF de las láminas que imprime el usuario | relación de planos, índice, figuras | códigos y títulos tal cual el rótulo |
| Resultado del diseño / memoria de cálculo | números de hidráulica, cotas de fondo, registros, juntas | una sola fuente para Excel, Word y PDF |
| Word del usuario (estudio hidrológico, plantilla de la especialidad) | base o estilo | se trabaja sobre copia; lo anterior no se altera |
| Foto del proyecto y logo oficial | carátulas | recortar en copia |
| Datos del proyecto | nombre completo tal cual el rótulo, CUI, entidad, ubicación, fecha del rótulo, color | ver §8 |
Lo que está en los planos o el metrado no se pregunta ("tú ya sabes qué dicen los planos"); lo pendiente se resuelve con criterio
y se documenta como hipótesis cubierta (el usuario pidió no pedirle trabajo).

## 2. Reglas de redacción
- Español formal de expediente; sin frases ni metadatos que revelen IA (`core_properties.author = ''`, `last_modified_by = ''`).
- Firmas: `Profesional responsable: ______ · CIP ______ · Firma: ______` en blanco. Nunca nombres de personas: proyectos por nombre y CUI;
  el proyecto aguas arriba es "aporte externo" y el aguas abajo "receptor".
- Cantidades en el texto SIEMPRE leídas del RESUMEN vigente (función tipo `q(item)`: 2 decimales con unidad para m, m², m³, kg;
  entero para und). Nunca escribir cantidades a mano ni "corregir" el metrado desde un documento.
- Citar la norma en cada criterio (CE.040 R.M. 126-2021-VIVIENDA, E.020, E.050, E.060, IS.010, G.050, D.S. 011-2019-TR, Manual de
  Hidrología MTC, AASHTO LRFD, Norma Técnica de Metrados RD 073-2010-VIVIENDA, NTP y ASTM de cada material). El usuario pide un
  "documento irrefutable" ante la Contraloría: cuadro de cumplimiento (requisito, norma, criterio, valor, resultado) y sección
  "Datos de otros expedientes y cómo quedan cubiertos".
- Sin observaciones a documentos ajenos dentro del entregable (van al chat o a una nota de revisión interna aparte).
- Códigos de lámina citados = los del juego del usuario (mapear códigos de trabajo → códigos finales; si la lámina no existe en
  ese juego, borrar la cita). Fecha y nombre del proyecto iguales al rótulo (vigilar SETIEMBRE / SEPTIEMBRE / OCTUBRE).

## 3. Memoria descriptiva (Word)
Estructura (13–14 capítulos, 17–23 páginas en drenaje):
1 Información del proyecto (tabla: unidad ejecutora, proyecto, CUI, ubicación, especialidad, componentes) · 2 Antecedentes
(introducción; normas aplicables) · 3 Ubicación (tabla política) · 4 Finalidad y objetivos · 5 Parámetros y criterios de diseño
(TR, P24, intensidades, FS, C por superficie y ponderado, n, pendientes, llenado, borde libre) · 6 Descripción del sistema
(esquema general, canaletas, montantes y falsas columnas, sumideros y red de piso, cunetas por eje desde la hoja de concreto,
lloraderos por tramo) · 7 Colector u obra principal (secciones, registros, empalmes, cajas, juntas, funcionamiento hidráulico,
verificación estructural) · 8 Aportes de proyectos colindantes / entrega al receptor · 9 Metas físicas (todas las partidas del
RESUMEN) · 10 Operación y mantenimiento · 11 Conclusiones · 12 Recomendaciones · 13 Relación de planos (mismo orden y códigos que el
índice) · 14 Anexos si corresponde.
- Formato: A4; márgenes 3.0 / 2.0 / 2.5 / 2.0 cm (izq., der., sup., inf.); Arial Narrow 11, interlineado 1.15; H1 13 pt y H2 11.5 pt
  en el color del proyecto, numerados "1.  TÍTULO", "1.1  Subtítulo"; carátula propia en sección sin encabezado; cuerpo en sección
  nueva con numeración desde 1, encabezado "MEMORIA DESCRIPTIVA - DRENAJE PLUVIAL | <PROYECTO CORTO> - CUI N.° ..." con borde inferior.
- Tablas: "Tabla N.° 01: ..." arriba (10 pt negrita centrada); encabezado sombreado con texto blanco, total en negrita con fondo
  claro; tablas cortas que no se separan (`keep_with_next`); encabezado repetido (`w:tblHeader`), filas sin partir (`w:cantSplit`).
- Figuras: las LÁMINAS DEL PDF del usuario (no renders propios): `pdftoppm -f p -l p -singlefile -jpeg -scale-to 2200`, a 15.5 cm,
  "Figura N.° 01: ... (lámina COD)" y "Fuente: Lámina COD del expediente ..." (9 pt cursiva gris). Plantas alargadas en página horizontal
  sin reiniciar la numeración.
- Memoria descriptiva general de un expediente: solo información real de planos y documentos; cuadro resumen (ambiente – área – NPT)
  primero para validar; arquitectura antes que drenaje; extensión 45–60 páginas si es general; respetar el Word del usuario si lo adjunta.

## 4. Memoria hidrológica y memoria de cálculo
- Capítulo nuevo AL FINAL del estudio hidrológico del usuario, en sección nueva con sus márgenes, estilos (Heading 1/2 con su
  numeración automática), Arial Narrow 12, interlineado 1.5, sangría 1.75 cm; continuar la numeración de tablas/imágenes del
  documento ("Tabla N° 22"). Verificar al final que los párrafos y tablas originales quedan idénticos.
- Explicar toda diferencia aparente de números (p. ej. 35.16 mm en 10 min = 210.98 mm/h para cunetas; colector con tc 15 min →
  155.66 mm/h) y que las memorias de proyectos encadenados coincidan (misma lluvia, TR, FS; caudal y cota de fondo entregados = recibidos).
- Memoria de cálculo en Excel con fórmulas (Excel en español: openpyxl guarda SUM/IF/ROUND y Excel los muestra REDONDEAR/SUMA/SI con ";"):
  hojas MEMORIA, DATOS (parámetro, valor, und, fuente, símbolo), CAUDALES, perfil/tramos, verificaciones, CUMPLIMIENTO. Colores: dato
  azul `0000FF`, fórmula negro, vínculo verde `008000`; leyenda de colores al pie; recalcular con LibreOffice y comprobar 0 errores
  `#` y 0 "NO CUMPLE". PDF (estilo de la memoria HIDRO-CE040) solo si el usuario lo pide: los valores se copian sin cambiar, solo formato.

## 5. Especificaciones técnicas por partida (Word)
**Partidas = las del RESUMEN del metrado**: mismo código, descripción Delphin, unidad y orden; no se agregan ni se quitan.
Las filas sin unidad son títulos (agrupan; sin medición ni pago); nivel del título según la cantidad de segmentos del código; los de
primer nivel abren página. No renumerar huecos de la base Delphin (p. ej. falta .04.01: se deja así).
Estructura del documento: portada/carátula → ÍNDICE (TOC niveles 1–4) → CAPÍTULO I GENERALIDADES → CAPÍTULO II ESPECIFICACIONES
TÉCNICAS POR PARTIDA.
- Capítulo I: 1.1 Generalidades (alcance; numeración y unidades = metrado; planos, memoria y metrado forman parte); 1.2 Ubicación y
  clima (cálido y lluvioso, ACI 305R); 1.3 Normas (RNE CE.040, OS.060, IS.010, E.020, E.050, E.060, E.090, G.050; D.S. 011-2019-TR;
  Norma Técnica de Metrados; NTP 334.009, 400.037, 339.088, 341.031, 339.033/034/035/036, 339.141/143, 399.003; ASTM A615, A36, A653,
  A123, C920, D2564; AWS D1.1, A5.1; ACI 318, 301, 304R, 305R, 308R, 347); orden de prelación planos → especificaciones → memoria →
  metrado (discrepancias al cuaderno de obra); 1.4 Materiales (tabla material / requisito / norma); 1.5 Concreto (f'c 100 solado,
  140 dados, 175 cunetas, 210 colector y tapas; slump 3"–4" armado, 2"–3" simple; mezclado ≥ 1.5 min; colocación < 45 min; caída
  ≤ 1.50 m; capas ≤ 0.30 m; vibrado; ≤ 32 °C; curado ≥ 7 días); 1.6 Encofrados (ACI 347; tolerancias; desencofrado 24 h costados,
  7 días o 70 % f'c fondos); 1.7 Acero (E.060 cap. 7; traslapes 0.40 para 3/8" y 0.50 para 1/2"; máx. 50 % por sección); 1.8 Control
  de calidad y ensayos (probetas 1 al día / 50 m³ / 300 m²; Proctor modificado; densidad ≥ 95 %; prueba hidráulica 15 min); 1.9
  Seguridad y medio ambiente; 1.10 Medición y pago.
- Cada partida, encabezado "código  descripción  (und)" y apartados en negrita de color:
  **DESCRIPCIÓN · MATERIALES · EQUIPOS Y HERRAMIENTAS · PROCEDIMIENTO DE EJECUCIÓN · CONTROL DE CALIDAD Y TOLERANCIAS ·
  SEGURIDAD Y SALUD EN EL TRABAJO · (cuadro extra si aplica) · UNIDAD DE MEDIDA · MÉTODO DE MEDICIÓN · FORMA DE PAGO.**
  Datos constructivos del propio proyecto (dimensiones, n.° de registros y juntas, acero, recubrimientos, láminas). Seguridad con
  bloques tipo: EPP (casco, lentes, guantes, botas con puntera, chaleco; D.S. 011-2019-TR y G.050), excavación (material a ≥ 0.60 m
  del borde, entibado > 1.50 m, redes enterradas), concreto, acero, soldadura, trabajo en altura (arnés, andamio).
  Medición según la Norma Técnica de Metrados (acero por peso nominal 3/8" = 0.56 kg/m, 1/2" = 0.994 kg/m, con ganchos y traslapes,
  sin desperdicio). Pago tipo: "El pago se efectuará al precio unitario del presupuesto por <unidad>, de acuerdo con el avance
  valorizado y con la conformidad de la Supervisión. Dicho precio y pago constituye compensación total por la mano de obra (incluidas
  las leyes sociales), los materiales, el equipo, las herramientas, el transporte interno y todo imprevisto necesario."
- Partidas con desagregado (lloraderos, tapas): incluir el cuadro de materiales tomado de la hoja de desagregado del metrado.
- Formato: A4, márgenes 2.5 sup / 2.0 inf / 3.0 izq / 2.0 der; Arial 10, justificado, interlineado 1.15; H1 13 pt centrado; tablas con
  encabezado repetido sombreado y bordes grises 8.5 pt; encabezado "ESPECIFICACIONES TÉCNICAS - <ESPECIALIDAD>" + "<corto> - CUI N.° ..."
  con borde inferior; pie "Página X de Y". Técnica: redactar a JSON por partida y convertir (python-docx o la librería `docx` de Node);
  revisar tildes al final.
- Si el usuario entrega SU Word de especificaciones: dejar solo las partidas del metrado (su numeración y nombre), conservar tal cual su
  texto e imágenes donde corresponden, borrar lo que no está en el metrado, completar con su mismo formato lo que falta ("Ídem" para
  repetidas) y poner proyecto, CUI y encabezado correctos en todas las páginas.

## 6. Carátulas, encabezados y pies
- Un solo Word con todas las carátulas, una por página (párrafo mínimo de 1 pt con salto antes; sin página en blanco al final);
  verificar convirtiendo a PDF que N carátulas = N páginas.
- Contenido de arriba abajo: escudo (recortado completo del logo oficial, sin el texto) + "GOBIERNO REGIONAL SAN MARTÍN" y gerencia
  con línea del color; texto de servicio ("SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL EXPEDIENTE TÉCNICO DE PI:" o
  "SERVICIO DE DISEÑO - DRENAJE PLUVIAL", nunca "EXPEDIENTE TÉCNICO" si el usuario lo corrigió); proyecto entre comillas tal cual el
  rótulo; CUI; foto del proyecto a todo el ancho útil con leyenda; franja de color con el título del documento (20–26 pt blanco) y
  subtítulo; ubicación y fecha. Un color por proyecto (p. ej. granate 7B1E2B, verde 1E5E3B, azul 1F3A68).
- Carátula de planos: solo "PLANOS / LÁMINAS XX-01 A XX-nn"; no una de "índice de planos" si el usuario no la quiere.
- Encabezado del cuerpo: texto corto del proyecto + CUI + especialidad con borde inferior; pie con campos PAGE y NUMPAGES
  (`w:fldChar` begin/separate/end + `w:instrText`). Carátula en sección propia sin encabezado; cuerpo con `pgNumType start=1`
  y encabezado no vinculado.
- XML de Word en orden del esquema (p. ej. `w:shd` antes de `w:vAlign` en `tcPr`), o Word dice que el archivo está dañado.

## 7. Índice (TOC) actualizado
- Insertar campo `TOC \o "1-3" \h \z \u` y `w:updateFields val="true"` en settings; para imprimir, llenarlo de verdad: abrir con
  LibreOffice (UNO), actualizar índices y guardar el mismo .docx (queda con títulos y páginas y Word recalcula al abrir).
- Alternativa en dos pasadas: generar, convertir a PDF (`soffice --headless --convert-to pdf`), buscar la página de cada título con
  `pdftotext -layout`, regenerar el TOC con marcadores y PAGEREF. Nunca dejar "Actualice el índice" en un documento para imprimir.

## 8. Coherencia (cadena metrado ↔ planos ↔ especificaciones ↔ memoria)
Orden de generación: diseño → memoria de cálculo (recalcular, 0 NO CUMPLE) → metrado vigente (se lee) → índice de planos desde el PDF
(lista de láminas) → memoria hidrológica → memoria descriptiva → especificaciones → PDF si se pide → carátulas → controles.
Al cambiar un dato o el juego de láminas, actualizar en cadena todos los documentos y buscar en todos los textos los valores viejos
(área, C, número de registros, "contramarco", códigos de lámina retirados).

## 9. Verificación final (checklist)
- [ ] Partidas de las especificaciones = RESUMEN (código, descripción, unidad, orden); cantidades de la memoria = RESUMEN.
- [ ] Todo código de lámina citado existe en el índice vigente; títulos y fecha iguales al rótulo.
- [ ] Mismo valor (Q, I, C, áreas, cotas de fondo, registros, juntas, lloraderos) en Excel, PDF, memorias y especificaciones.
- [ ] Texto antes/después comparado: solo cambió lo pedido; Word original del usuario sin alterar; metrado con 0 celdas cambiadas.
- [ ] Sin nombres de personas, CIP, "observaciones" a terceros, textos en inglés ni rastros de IA; propiedades del archivo vacías.
- [ ] TOC lleno; tablas con encabezado repetido; cada carátula en una página; vista PNG de páginas críticas revisada.
- [ ] Decir con claridad lo que no se pudo comprobar.

## 10. Errores que el usuario ya corrigió (no repetirlos)
- Escribir en inglés ("¿por qué todo escribes en inglés?").
- Poner nombre o CIP del proyectista ("el nombre CIP no pongas nada").
- Contradicción de números sin explicar ("¿por qué pones 35.163 mm si el diseño es 210?"): explicar la relación en el texto.
- Metrar en el colector las prolongaciones de cunetas que el usuario ya había metrado.
- Memoria "con pocas páginas" o "muy pobre": seguir la estructura completa de los ejemplos del usuario y ampliar con datos reales.
- Carátula con "EXPEDIENTE TÉCNICO" cuando debía decir "SERVICIO DE DISEÑO - DRENAJE PLUVIAL"; carátulas en Word separados (van en uno);
  escudo cortado (usar el logo oficial completo); color repetido entre proyectos (pidió otro color, p. ej. verde); fecha distinta del rótulo.
- Índice renumerado o con observaciones ("haces observaciones, pero no tienen sentido"); orden distinto del pedido (de la uno a la última).
- Citar láminas de otro proyecto (DJ-01/DJ-03 del CAR Varones en el Refugio) o láminas excluidas por el usuario: se borran.
- Mezclar datos entre las memorias de proyectos encadenados (áreas 6 752.06 vs 6 752.03, C 0.808 vs 0.807): deben coincidir.
- Especificaciones del Word del usuario con partidas de otro proyecto y encabezados de otra entidad: dejar solo las del metrado propio.
- Excel de cálculo con funciones o textos en inglés visibles; documentos con valores tecleados en vez de leídos del metrado.
