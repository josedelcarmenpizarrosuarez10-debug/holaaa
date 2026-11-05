---
name: memorias-especificaciones-tecnicas
description: "Redactar y armar en Word los documentos escritos de un expediente técnico de cualquier especialidad y tipo de edificación (drenaje pluvial, señalización, mobiliario, estructuras u otras): memoria descriptiva, memoria de cálculo (Excel con fórmulas y PDF si se pide), capítulo agregado a un estudio del usuario, especificaciones técnicas por partida Delphin (descripción, materiales, equipos, procedimiento, control, seguridad, unidad, medición y pago), carátulas, encabezados y pies, índice (TOC) actualizado, relación de planos y figuras tomadas de las láminas. Garantiza coherencia con el metrado y los planos. Usar cuando se pida una memoria, especificaciones, carátulas o encabezados, o revisar que los documentos cuadren con el metrado y las láminas."
---
# Memorias, especificaciones técnicas y documentos Word del expediente

Método general para colegios, establecimientos de salud, locales municipales, albergues u otras edificaciones, y para cualquier
especialidad que se documente con memoria, especificaciones y metrado. Nombre, CUI, entidad, colores, normas aplicables, números
de diseño y códigos de lámina salen del proyecto nuevo; los de proyectos anteriores están solo en el apartado final **"Ejemplo de
referencia"**. Detalle en `referencias/08_documentos_del_expediente.md` y `referencias/06_metrado_acu_especificaciones.md`
(describen proyectos ya trabajados; sus rutas no existen en este chat).

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
| Insumo | Uso | Regla |
|---|---|---|
| Datos del proyecto: nombre completo tal cual el rótulo, CUI, entidad (y gerencia u oficina), ubicación, fecha del rótulo | carátulas, encabezados, texto | copiar exacto; vigilar la fecha (SETIEMBRE / SEPTIEMBRE) |
| Especialidad y tipo de edificación (colegio, salud, municipal, albergue...) y su normativa sectorial | normas, criterios | confirmar las normas vigentes que aplican |
| Metrado vigente (Excel, RESUMEN y hojas de detalle) | partidas y cantidades de todos los documentos | solo lectura; recalcular una copia con LibreOffice antes de leer |
| PDF de las láminas que imprime el cliente | relación de planos, índice, figuras | códigos y títulos tal cual el rótulo |
| Resultado del diseño / memoria de cálculo | números técnicos | una sola fuente para Excel, Word y PDF |
| Word del usuario (estudio, plantilla, especificaciones propias) | base o estilo | se trabaja sobre copia; lo anterior no se altera |
| Documento modelo que el usuario considere bueno | estructura y extensión | seguir su estructura completa |
| Foto del proyecto y logo oficial de la entidad | carátulas | recortar en copia; logo completo |
| Color o estilo gráfico del proyecto (si el usuario lo fija) | carátulas, títulos, tablas | si no lo da, proponer uno y que no repita el de otro proyecto |
| Texto de servicio de la carátula ("SERVICIO DE DISEÑO - <ESPECIALIDAD>" u otro) | carátulas | el que indique el usuario |
Lo que está en los planos o el metrado no se pregunta ("tú ya sabes qué dicen los planos"); lo pendiente se resuelve con criterio
y se documenta como hipótesis cubierta (el usuario pidió no pedirle trabajo innecesario).

## 2. Reglas de redacción
- Español formal de expediente; sin frases ni metadatos que revelen IA (`core_properties.author = ''`, `last_modified_by = ''`).
- Firmas: `Profesional responsable: ______ · CIP ______ · Firma: ______` en blanco. Nunca nombres de personas: proyectos por nombre y
  CUI; un proyecto vecino aguas arriba es "aporte externo" y el de aguas abajo "receptor".
- Cantidades en el texto SIEMPRE leídas del RESUMEN vigente (función tipo `q(item)`: 2 decimales con unidad para m, m², m³, kg;
  entero para und). Nunca escribir cantidades a mano ni "corregir" el metrado desde un documento.
- Citar la norma en cada criterio (RNE y normas técnicas vigentes de la especialidad, normas sectoriales del tipo de edificación,
  Norma Técnica de Metrados, NTP y ASTM de cada material, seguridad en obra). El usuario pide un "documento irrefutable" ante la
  Contraloría: cuadro de cumplimiento (requisito, norma, criterio, valor, resultado) y, si se usaron datos de otros expedientes,
  sección que diga cuáles y cómo quedan cubiertos.
- Sin observaciones a documentos ajenos dentro del entregable (van al chat o a una nota de revisión interna aparte).
- Códigos de lámina citados = los del juego del cliente (mapear códigos de trabajo → códigos finales; si la lámina no existe en
  ese juego, borrar la cita). Fecha y nombre del proyecto iguales al rótulo.

## 3. Memoria descriptiva (Word)
Estructura por defecto (adaptar los capítulos técnicos a la especialidad):
1 Información del proyecto (tabla: unidad ejecutora, proyecto, CUI, ubicación, especialidad, componentes) · 2 Antecedentes
(introducción; normas aplicables) · 3 Ubicación (tabla política) · 4 Finalidad y objetivos · 5 Parámetros y criterios de diseño ·
6 Descripción del sistema o de los componentes (desde las hojas del metrado y las láminas) · 7 Obra principal (dimensiones,
funcionamiento, verificación) · 8 Relación con proyectos colindantes o redes existentes, si hay · 9 Metas físicas (todas las
partidas del RESUMEN) · 10 Operación y mantenimiento · 11 Conclusiones · 12 Recomendaciones · 13 Relación de planos (mismo orden y
códigos que el índice) · 14 Anexos si corresponde.
- Formato por defecto: A4; márgenes 3.0 / 2.0 / 2.5 / 2.0 cm (izq., der., sup., inf.); Arial Narrow 11, interlineado 1.15; H1 13 pt
  y H2 11.5 pt en el color del proyecto, numerados "1.  TÍTULO", "1.1  Subtítulo"; carátula en sección sin encabezado; cuerpo en
  sección nueva con numeración desde 1, encabezado "MEMORIA DESCRIPTIVA - <ESPECIALIDAD> | <PROYECTO CORTO> - CUI N.° ..." con borde.
- Tablas: "Tabla N.° 01: ..." arriba (10 pt negrita centrada); encabezado sombreado con texto blanco, total en negrita con fondo
  claro; tablas cortas que no se separan (`keep_with_next`); encabezado repetido (`w:tblHeader`), filas sin partir (`w:cantSplit`).
- Figuras: las LÁMINAS DEL PDF del cliente (no renders propios): `pdftoppm -f p -l p -singlefile -jpeg -scale-to 2200`, a 15.5 cm,
  "Figura N.° 01: ... (lámina COD)" y "Fuente: Lámina COD del expediente ..." (9 pt cursiva gris). Plantas alargadas en página
  horizontal sin reiniciar la numeración.
- Memoria descriptiva general de un expediente: solo información real de planos y documentos; cuadro resumen (ambiente – área – NPT)
  primero para validar; arquitectura antes que las demás especialidades; respetar el Word del usuario si lo adjunta. Una memoria
  "pobre" no se acepta: extensión acorde al modelo del usuario.

## 4. Capítulo agregado a un estudio del usuario y memoria de cálculo
- Capítulo nuevo AL FINAL del documento del usuario (p. ej. estudio hidrológico), en sección nueva con sus márgenes, estilos
  (Heading 1/2 con su numeración automática), fuente, interlineado y sangría; continuar la numeración de tablas e imágenes del
  documento. Verificar al final que los párrafos y tablas originales quedan idénticos.
- Explicar en el texto toda diferencia aparente de números (p. ej. lluvia en un intervalo vs. intensidad horaria; distintos tiempos
  de concentración) y que las memorias de proyectos encadenados coincidan (mismos datos de entrada; lo entregado = lo recibido).
- Memoria de cálculo en Excel con fórmulas (Excel en español: openpyxl guarda SUM/IF/ROUND y Excel muestra REDONDEAR/SUMA/SI con ";"):
  hojas MEMORIA, DATOS (parámetro, valor, und, fuente, símbolo), cálculos por etapa, verificaciones, CUMPLIMIENTO. Colores por defecto:
  dato azul `0000FF`, fórmula negro, vínculo verde `008000`; leyenda al pie; recalcular con LibreOffice y comprobar 0 errores `#` y
  0 "NO CUMPLE". PDF solo si el usuario lo pide, con el estilo que indique: los valores se copian sin cambiar, solo formato.

## 5. Especificaciones técnicas por partida (Word)
**Partidas = las del RESUMEN del metrado**: mismo código, descripción Delphin, unidad y orden; no se agregan ni se quitan.
Las filas sin unidad son títulos (agrupan; sin medición ni pago); nivel del título según la cantidad de segmentos del código; los de
primer nivel abren página. No renumerar huecos de la base Delphin.
Estructura: carátula → ÍNDICE (TOC niveles 1–4) → CAPÍTULO I GENERALIDADES → CAPÍTULO II ESPECIFICACIONES TÉCNICAS POR PARTIDA.
- Capítulo I: 1.1 Generalidades (alcance; numeración y unidades = metrado; planos, memoria y metrado forman parte); 1.2 Ubicación y
  clima (condiciones del sitio; en clima cálido, ACI 305R; en frío, ACI 306R); 1.3 Normas (RNE de la especialidad, normas sectoriales,
  Norma Técnica de Metrados, NTP, ASTM, ACI, AWS que correspondan a los materiales del metrado); orden de prelación por defecto planos
  → especificaciones → memoria → metrado (discrepancias al cuaderno de obra); 1.4 Materiales (tabla material / requisito / norma);
  1.5 Concreto (f'c de cada elemento según el proyecto, slump, mezclado, colocación, vibrado, curado); 1.6 Encofrados (ACI 347,
  tolerancias, desencofrado); 1.7 Acero (E.060: traslapes y empalmes); 1.8 Control de calidad y ensayos; 1.9 Seguridad y medio
  ambiente; 1.10 Medición y pago. Solo los capítulos que la especialidad necesita.
- Cada partida, encabezado "código  descripción  (und)" y apartados en negrita de color:
  **DESCRIPCIÓN · MATERIALES · EQUIPOS Y HERRAMIENTAS · PROCEDIMIENTO DE EJECUCIÓN · CONTROL DE CALIDAD Y TOLERANCIAS ·
  SEGURIDAD Y SALUD EN EL TRABAJO · (cuadro extra si aplica) · UNIDAD DE MEDIDA · MÉTODO DE MEDICIÓN · FORMA DE PAGO.**
  Datos constructivos del propio proyecto (dimensiones, cantidades, acero, recubrimientos, láminas). Seguridad con bloques tipo:
  EPP (casco, lentes, guantes, botas con puntera, chaleco; norma de seguridad vigente), excavación (material lejos del borde,
  entibado en zanjas profundas, redes enterradas), concreto, acero, soldadura, trabajo en altura (arnés, andamio).
  Medición según la Norma Técnica de Metrados (acero por peso nominal, con ganchos y traslapes, sin desperdicio). Pago tipo: "El pago
  se efectuará al precio unitario del presupuesto por <unidad>, de acuerdo con el avance valorizado y con la conformidad de la
  Supervisión. Dicho precio y pago constituye compensación total por la mano de obra (incluidas las leyes sociales), los materiales,
  el equipo, las herramientas, el transporte interno y todo imprevisto necesario."
- Partidas con desagregado: incluir el cuadro de materiales tomado de la hoja de desagregado del metrado.
- Formato por defecto: A4, márgenes 2.5 sup / 2.0 inf / 3.0 izq / 2.0 der; Arial 10, justificado, interlineado 1.15; H1 13 pt
  centrado; tablas con encabezado repetido sombreado y bordes grises; encabezado "ESPECIFICACIONES TÉCNICAS - <ESPECIALIDAD>" +
  "<corto> - CUI N.° ..." con borde inferior; pie "Página X de Y". Técnica: redactar a JSON por partida y convertir (python-docx o
  la librería `docx` de Node); revisar tildes al final.
- Si el usuario entrega SU Word de especificaciones: dejar solo las partidas del metrado (su numeración y nombre), conservar tal cual su
  texto e imágenes donde corresponden, borrar lo que no está en el metrado, completar con su mismo formato lo que falta ("Ídem" para
  repetidas) y poner proyecto, CUI y encabezado correctos en todas las páginas.

## 6. Carátulas, encabezados y pies
- Un solo Word con todas las carátulas, una por página (párrafo mínimo de 1 pt con salto antes; sin página en blanco al final);
  verificar convirtiendo a PDF que N carátulas = N páginas.
- Contenido de arriba abajo: escudo o logo oficial completo (sin cortarlo) + nombre de la entidad y su gerencia u oficina con línea
  del color; texto de servicio que indique el usuario (no "EXPEDIENTE TÉCNICO" si lo corrigió); proyecto entre comillas tal cual el
  rótulo; CUI; foto del proyecto a todo el ancho útil con leyenda; franja de color con el título del documento (20–26 pt blanco) y
  subtítulo; ubicación y fecha. **Un color por proyecto**, elegido para ese proyecto y distinto de los de otros proyectos del usuario.
- Carátula de planos: solo "PLANOS / LÁMINAS <primera> A <última>" con los códigos del cliente; no una de "índice de planos" si el
  usuario no la quiere.
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
(lista de láminas) → memorias → especificaciones → PDF si se pide → carátulas → controles.
Al cambiar un dato o el juego de láminas, actualizar en cadena todos los documentos y buscar en todos los textos los valores viejos
(áreas, coeficientes, cantidades, nombres de componentes retirados, códigos de lámina retirados).

## 9. Verificación final (checklist)
- [ ] Partidas de las especificaciones = RESUMEN (código, descripción, unidad, orden); cantidades de la memoria = RESUMEN.
- [ ] Todo código de lámina citado existe en el índice vigente; títulos y fecha iguales al rótulo.
- [ ] Mismo valor de cada dato técnico en Excel, PDF, memorias y especificaciones.
- [ ] Texto antes/después comparado: solo cambió lo pedido; Word original del usuario sin alterar; metrado con 0 celdas cambiadas.
- [ ] Nombre, CUI, entidad, color y normas del proyecto nuevo; nada heredado de otro proyecto.
- [ ] Sin nombres de personas, CIP, "observaciones" a terceros, textos en inglés ni rastros de IA; propiedades del archivo vacías.
- [ ] TOC lleno; tablas con encabezado repetido; cada carátula en una página; vista PNG de páginas críticas revisada.
- [ ] Decir con claridad lo que no se pudo comprobar.

## 10. Errores que el usuario ya corrigió (lecciones generales)
- Escribir en inglés ("¿por qué todo escribes en inglés?").
- Poner nombre o CIP del proyectista ("el nombre CIP no pongas nada").
- Números que parecen contradecirse sin explicarlo en el texto.
- Volver a metrar o describir como propio lo que otro documento del usuario ya cubre.
- Memoria "con pocas páginas" o "muy pobre": seguir la estructura completa del modelo del usuario y ampliar con datos reales.
- Carátula con un texto de servicio distinto del indicado; carátulas en Word separados (van en uno); escudo cortado; color repetido
  entre proyectos; fecha distinta del rótulo.
- Índice renumerado o con observaciones ("haces observaciones, pero no tienen sentido"); orden distinto del pedido.
- Citar láminas de otro proyecto o láminas excluidas por el usuario: se borran.
- Datos distintos entre memorias de proyectos encadenados (áreas, coeficientes): deben coincidir al decimal.
- Especificaciones del Word del usuario con partidas de otro proyecto y encabezados de otra entidad: dejar solo las del metrado propio.
- Excel de cálculo con funciones o textos en inglés visibles; documentos con valores tecleados en vez de leídos del metrado.

## Ejemplo de referencia (valores de proyectos anteriores; reemplazar por los del proyecto nuevo)
Proyectos de donde salió el método: Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514), CAR Varones (CUI 2705619),
CAR Mujeres (CUI 2717013) e I.E. N.° 0590 Barranquita (C.I. 468901), del Gobierno Regional San Martín.
- Memoria descriptiva de drenaje: 13–14 capítulos, 17–23 páginas; general del expediente 45–60 páginas. Capítulo agregado al
  estudio hidrológico del usuario en Arial Narrow 12, interlineado 1.5, sangría 1.75 cm.
- Diferencia explicada: 35.16 mm en 10 min = 210.98 mm/h (cunetas) frente a 155.66 mm/h con tc 15 min (colector).
- Normas citadas en drenaje: CE.040 (R.M. 126-2021-VIVIENDA), OS.060, IS.010, E.020, E.050, E.060, E.090, G.050, D.S. 011-2019-TR,
  Manual de Hidrología MTC, AASHTO LRFD, RD 073-2010-VIVIENDA; NTP 334.009, 400.037, 339.088, 341.031, 399.003; ASTM A615, A36,
  A653, A123, C920, D2564; AWS D1.1; ACI 318, 301, 304R, 305R, 308R, 347.
- Concreto: f'c 100 solado, 140 dados, 175 cunetas, 210 colector y tapas; slump 3"–4" armado; curado ≥ 7 días; traslapes 0.40
  (3/8") y 0.50 (1/2"); probetas 1 al día / 50 m³; densidad de relleno ≥ 95 % Proctor modificado; prueba hidráulica 15 min.
- Carátula: "GOBIERNO REGIONAL SAN MARTÍN" y gerencia; "SERVICIO DE DISEÑO - DRENAJE PLUVIAL"; colores usados granate 7B1E2B,
  verde 1E5E3B y azul 1F3A68 (uno por proyecto).
