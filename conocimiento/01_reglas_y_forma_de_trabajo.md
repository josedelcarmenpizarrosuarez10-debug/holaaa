# 01 — Reglas del usuario, proyectos y forma de trabajo

Base de conocimiento permanente del repositorio de drenaje pluvial (Morales y Barranquita, San Martín, Perú).
Reúne todo lo aprendido desde el 3 de octubre de 2026 sobre **cómo quiere trabajar el usuario**: reglas fijas,
correcciones que hizo (con fecha y lo que se aprendió), registro de proyectos, cadena hidráulica compartida, códigos
de láminas vigentes y técnicas de trabajo comprobadas. Los criterios técnicos de diseño, planos y metrado tienen su
propio detalle en los demás temas de esta base y en los skills de `.claude/skills/`; aquí se citan solo cuando son
regla de trabajo.

Fuentes: `conocimiento/_fuentes/mensajes_usuario.txt` (todos los mensajes del usuario), `BITACORA_CONVERSACION.md`,
`CLAUDE.md`, `.claude/skills/*/SKILL.md`, `insumos/solange/vigente/LEEME.txt` y el código de `herramientas/`.

---

## 1. Reglas permanentes (resumen)

| N.° | Regla | Desde | Por qué / origen |
|---|---|---|---|
| R1 | Todo en español: respuestas, documentos, mensajes de commit, textos de planos, explicaciones | 03-10, reiterada 14-10 y 20-10 | "¿Por qué todo escribes en inglés?"; "dime todo en español, no entiendo inglés" |
| R2 | Explicar en idioma fácil, sin jerga ni anglicismos | 03-10 | "dime en idioma fácil"; "¿a qué te refieres aquí?" (20-10), "eso de decisiones antiguas, ¿cómo es? no entiendo" (15-10) |
| R3 | Nada en los documentos que revele uso de IA | traspaso 03-10 | Expediente técnico que firman especialistas; "sin frases que suenen a IA" (05-10) |
| R4 | Sin nombre ni CIP del proyectista; campos de firma en blanco | 08-10 | "el nombre CIP no pongas nada eso" |
| R5 | Citar los proyectos por nombre y CUI, nunca por persona | traspaso 03-10 | Cada proyecto es independiente y va a revisión |
| R6 | Decir siempre "cota de fondo" (nunca "invert") | traspaso 03-10 | Término del usuario |
| R7 | Escala real: 1 unidad de dibujo = 1 m | 03-10, reiterada 07-10 y 21-10 | "Si algo mide 0.56, así debe medir en el plano" |
| R8 | Entregables en Word, Excel y DXF; vistas previas en PNG; PDF solo cuando el usuario lo pida | 03-10 a 08-10 | Se retiraron las vistas previas en PDF (04-10, 14-10) |
| R9 | No modificar los metrados del usuario salvo pedido expreso; cambiar solo lo pedido, sobre SU archivo, y verificar que lo demás quede idéntico | traspaso 03-10 | "por qué borras todo mi metrado…" (03-10) |
| R10 | Partidas con nombres y estructura Delphin (base: CAR Mujeres); cantidades siempre del metrado propio | 06-10 | Así trabaja la oficina de presupuesto |
| R11 | No mezclar partidas ni láminas entre proyectos (ni sumar una partida dentro de otra) | 03-10 | "no vayas a mezclar las partidas sumando uno en otro" |
| R12 | Coherencia total: metrado ↔ planos ↔ especificaciones ↔ memorias ↔ ACU | 03-10 en adelante | "todo debe cuadrar… todo coherencia" (15-10) |
| R13 | Los insumos del usuario no se editan; todo cambio se hace en el generador y se regenera | 03-10 | Trazabilidad y no perder el original |
| R14 | Planos ya impresos por el usuario no se regeneran; láminas congeladas no se tocan | 07-10 y 21-10 | "ya no alteres planos, ya imprimí el último" |
| R15 | Precios reales con su fuente; mano de obra CAPECO-FTCCP 2026 (operario 28.95, oficial 22.68, peón 20.54) | 09-10 a 15-10 | "dame un precio real", "precio real comprobado" |
| R16 | Diseño según normativa peruana, sin sobredimensionar, ahorrando acero, documento "irrefutable" | 03-10 | "esto va a firmar especialistas… que después la Contraloría no intervenga" |
| R17 | Explicar el plan y confirmar antes de rehacer cosas grandes; si el usuario dice "espera", no hacer nada | traspaso 03-10, 14-10, 20-10 | "Antes que procedas a algo… yo te confirmo" |
| R18 | No preguntar lo que ya está en el repositorio ni pasarle al usuario tareas que uno puede hacer | 03-10, 05-10, 14-10 | "¿por qué me preguntas esto si tú sabes, tienes el plano?" |
| R19 | Informar siempre si un cambio afecta el metrado (o los planos / metrados de otro proyecto) | 03-10, 04-10, 07-10, 08-10 | "¿el metrado ha variado o no?", "¿no alteraste ni un número?" |
| R20 | Entregar todos los archivos afectados, completos, al terminar cada pedido | 03-10, 04-10, 15-10 | "¿y el archivo Excel? ¿nada?", "¿y los archivos?" |
| R21 | Estudios de gestión de riesgos de obra: sin montos en soles ni "observaciones" a documentos ajenos; efectos en % del presupuesto | 16-10 | "esto solo es un estudio de gestión de riesgos durante la ejecución" |
| R22 | PSST y gestión de riesgos siempre con su matriz (IPERC o matriz de riesgos) en Excel con fórmulas y un Word ordenado con tablas y gráficos; método estándar para cualquier obra en el Perú; cada tema en su carpeta | 17-10 | "debe ser algo estándar para cualquier tipo de proyecto en Perú" |
| R23 | Revisar a fondo antes de presentar ("revísalo unas 10 veces") y no dejar errores | 03-10, 08-10, 20-10 | "no quiero errores así nuevamente", "ya no quiero estar haciendo el mismo proceso" |
| R24 | Entidad: Gobierno Regional San Martín – **Gerencia Territorial Bajo Mayo (GTBM)** – Tarapoto. Nunca "Proyecto Especial Huallaga Central y Bajo Mayo" ni "PEHCBM": si aparece en un documento, se borra de todo | 28-10 | "no es el Proyecto Especial Huallaga… eso borra de todo, la entidad es la Gerencia Territorial Bajo Mayo, GTBM" |
| R25 | El presupuesto de obra lo hace el ingeniero en **Delphin** (no en S10) | 28-10 | "no usa S10, usa Delphin" |
| R26 | Antes de usar datos (horas-hombre, insumos, metrados, precios) confirmar de qué proyecto son; nunca meter datos de una obra en el archivo de otra | 28-10 | Horas-hombre del CAR Mujeres puestas por error en el PSST de Sauce |
| R27 | Quitar o cambiar solo lo pedido también en Word y PDF (un encabezado, un pie de página, una frase) y comprobar que el resto quedó idéntico | 28-10 | "no era para que borres todo, solo eso donde salía la fecha… veo que borraste el título" |
| R28 | Excel para el usuario: sin hojas protegidas, con los decimales completos a la vista, todo con fórmulas y con formato ordenado (amarillo = datos, gris = cálculo, verde = resultado) | 28-10 | "¿por qué el Excel está protegido todo? me redondea decimales"; "está feo el formato… necesito todo con un buen formato" |
| R29 | Al revisar o corregir un documento, comprobar que nombre, CUI, ubicación y entidad sean de ese proyecto y que no queden textos copiados de otro proyecto | 26-10 | "recuerda, esta memoria es de Refugio Mujeres Violentadas, CUI que termina en 14"; "varios dicen institución educativa… cambia todo" |
| R30 | Los archivos terminados se adjuntan en el chat para descargarlos; los archivos del usuario en `D:\GTBM\...` se editan en su sitio solo cuando él lo pide | 26-10 | "pásame aquí todos los archivos, no lo copies en carpetas, dame aquí, yo descargo" |

El detalle de cada regla, con sus casos, está en las secciones 2 a 6.

---

## 2. Detalle de las reglas

### 2.1 Idioma y comunicación
- Todo en español: el chat, los documentos (Word, Excel, DXF), los nombres de hojas, los comentarios de los generadores
  y los mensajes de commit. El 14-10 el usuario reclamó "¿por qué todo escribes en inglés?" y el 20-10 "por favor dime todo
  en español, no entiendo inglés" (había frases técnicas en inglés en un resumen). Los resúmenes automáticos de contexto
  salían en inglés: lo que se le muestra al usuario debe estar en español.
- Idioma fácil: el usuario pide explicaciones simples ("dime en idioma fácil", 03-10). Evitar palabras que él no usa:
  "invert", "nudos" (21-10: "no sé a qué te refieres cuando dices nudos, siempre es quiebres de 45"), "hondonada" sin
  explicarla, "perfilar el terreno", "decisiones antiguas". Si hay que usar un término técnico, explicarlo en una línea.
- Cuando el usuario pide un texto para un tercero (el ingeniero de presupuesto que trabaja en Delphin, la arquitecta),
  entregar **un párrafo corto, claro, en lenguaje sencillo**, listo para copiar ("dame el texto para escribirle al ingeniero
  así en un párrafo, idioma entendible fácil", 06-10; "dame un texto pequeño, párrafo, para mandarle a la arquitecta", 19-10;
  "dame texto para explicarle bien justificado un precio aproximado para el ing. de presupuesto", 09-10). El 28-10 lo precisó:
  "en un solo párrafo, tono amigable"; "no le preguntes, solo dile lo que necesitas" → el mensaje pide lo que hace falta, sin
  preguntas ni explicaciones que el destinatario ya conoce.
- Preguntas del usuario tipo "¿ya está todo ok sin errores?", "¿todo coincide al milímetro?": responder con la verificación
  hecha (qué se comparó y con qué resultado), no con una afirmación vacía.
- Responder lo que se pregunta: si pide "analízalo y dime si lo puedes hacer, sí o no; solo eso" (21-10), contestar eso y
  esperar la orden.
- El usuario usa mucho el celular para ver los archivos (03-10: "los 3D salen color negro, quizás sea porque veo los
  archivos desde mi celular"): los DXF deben verse bien también en visores simples (colores verdaderos, rellenos con color
  explícito, sin patrones de achurado que dependan de la escala).
- Avisar el avance en trabajos largos: el usuario escribe "¿aún nada?", "¿qué pasó? hasta ahora no veo nada", "no veo
  nada" (14-10, 19-10, 21-10). El 21-10 pidió "activa las notificaciones para estar atento".

### 2.2 Nada que revele IA y sin proyectista
- Ningún texto en Word, Excel, DXF o PDF que delate que se hizo con IA (frases genéricas, "como modelo…", "completar",
  "insertar", "[dato]"). En la memoria descriptiva general del CAR Mujeres (05-10) el usuario fijó: "Usa SOLO información
  real de los planos y documentos. No inventes ambientes, áreas, acabados ni metas. Si falta un dato, avísame aparte; no
  pongas 'completar' ni 'insertar'. Redacción formal de expediente técnico, sin frases que suenen a IA."
- Metadatos de los Word en blanco: `core_properties.author = ''`, `last_modified_by = ''`, `comments = ''`
  (ver `herramientas/mujeres/memoria_descriptiva_m.py`).
- Sin nombre ni CIP del proyectista (08-10: "el nombre CIP no pongas nada eso"). Firmas en blanco en la memoria de cálculo
  PDF; carátulas sin proyectista; en el rótulo DXF el campo `B.ELABORADO` se deja vacío cuando corresponde ("ELABORADO"
  vacío = no se escribe, `dxf_base`).
- Sin nombres de personas dentro de los documentos: el 20-10 se quitaron nombres de personas de la memoria de cálculo PDF
  del CAR Mujeres (`herramientas/mujeres/memoria_pdf_m.py`). En los documentos los proyectos se citan por nombre y CUI.
- Tampoco nombres de otros profesionales (ingeniero de presupuesto, arquitecta) en los entregables.

### 2.3 Citar los proyectos por nombre y CUI (trato entre proyectos)
- Regla del traspaso (03-10): "Cada proyecto es independiente. En los documentos de un proyecto, el vecino aguas arriba es un
  **APORTE EXTERNO** (dato de su memoria, sin validarla) y el de aguas abajo es el **RECEPTOR**. Citar siempre por nombre y
  CUI, nunca por persona."
- Formato de cita: "CAR Varones (CUI 2705619)", "Hogar de Refugio Temporal (CUI 2675514)", "CAR Mujeres (CUI 2717013)",
  "I.E. N.° 0590 Barranquita (C.I. N.° 468901)", "vía SM-107 Tingo de Ponasa – Shamboyacu (CUI 2673852)".
- Los nombres de las responsables (columna "Responsable" de CLAUDE.md) sirven solo para entender al usuario en el chat
  ("lo de Wilma", "Katiuska", "Solange"); nunca se escriben en un documento.
- Los datos de otro expediente se toman tal como están en su memoria (caudal, cota de fondo de entrega) y se rotulan como
  dato externo; si hay que comprobar que empalman, se comprueba en ambos expedientes (ver §4.3).

### 2.4 Terminología
- "Cota de fondo" (C.F.), nunca "invert". En perfiles: NCT (nivel de corona / piso terminado), NCF (cota de fondo), H
  (altura interior medida desde el NCT).
- "Quiebre a 45°", no "nudo".
- "Registro de limpieza" con "tapa ciega" (desde el 16-10), "caja de llegada CL", "caja de caída CC con poza de disipación".
- "Losa superior = vereda" en el colector; "junta de tecnopor y sellador asfáltico" (no elastomérico desde el 14-10).
- Unidad "m" (no "ml") en rejilla y junta de cunetas, como Delphin (07-10).
- En Barranquita: "pase en el cimiento del cerco" (no "poza") para las descargas D1 a D4; ejes "EJE-01 … EJE-19"
  (no "bloque X", 21-10: "no pongas eso de bloque X y tal número, eso se ve feo, solo pon nombre del eje y sus progresivas;
  y eso de pabellón conserva").

### 2.5 Escala real
- 1 unidad = 1 m en todos los DXF. Perfiles con escala horizontal = vertical (sin exageración).
- Origen: 03-10 ("si la losa es 0.20 m debe ser 20 cm en escala, dibujar 0.20 con comando L en AutoCAD"; "dice que mide el
  espesor de la losa 0.80 m, así no es la medida, yo te he pedido todo real, escala real, no sobredimensionado"; "pones 3.50
  y dice mide total, he medido y mide 7.30, todo está mal"); 07-10 ("no olvides todo es escala real, si algo mide 0.56 así
  debe medir"); 21-10 Barranquita ("¿por qué mide 0.30 si el ancho total de las cunetas es 0.60? ¿no dibujaste todo a escala
  real?" — la planta de cada descarga se había dibujado a 1/50 dentro de una lámina 1/25).
- Barras de acero dibujadas a su diámetro real (3/8" es 3/8", 1/2" es 1/2"; 03-10), barras longitudinales como círculos
  rellenos, no cuadrados.
- Las cotas miden el dibujo; nunca se escribe un texto fijo para "corregir" una medida mal dibujada.
- Las medidas de la fila Longitud de la guitarra son siempre de sección a sección completa (21-10: salía 31.45 en vez de
  35.59 cuando un tramo se partía entre dos piezas).
- Antes de entregar: comparar 3 o 4 cotas del dibujo con el diseño (memoria / metrado). Ver skill `planos-ordenados`.

### 2.6 Formatos de entregable
| Tipo | Formato | Notas |
|---|---|---|
| Planos | DXF (AutoCAD), escala real, con presentaciones (layouts) listas para imprimir e índice | A0/A1/A2/A3 según el tamaño del dibujo (08-10) |
| Vista previa de planos | PNG por lámina (`dxf_render.py`) | No PDF salvo pedido |
| Memorias, especificaciones, índices, carátulas | Word (.docx) | Verificado renderizando con LibreOffice |
| Metrado, memoria de cálculo, análisis estadístico, ACU, matrices | Excel con fórmulas | En la planilla del usuario, con su formato |
| PDF | Solo a pedido | Ej.: memorias de cálculo del colector en PDF con el estilo HIDRO-CE040 (15-10 y 23-10), pedidas expresamente |

- Reglas DXF del traspaso: cada elemento en su capa con nombre y color, cotas con entidad DIMENSION, bloques para lo que se
  repite, leyenda en cada lámina, listo para imprimir, sin textos que delaten IA. Para que AutoCAD lo abra: sin "/" en los
  nombres de bloque y con los grupos 3 a 7 del DIMSTYLE presentes.
- Impresión (08-10): cada lámina con su presentación de AutoCAD a escala 1:1; el espacio modelo en A1 para que no salga
  "Paper Size Not Found". Procedimiento que se le dejó al usuario: abrir la pestaña de la lámina, Ctrl+P, área =
  Presentación, escala 1:1, centrar; elegir el plotter con el mismo papel ("DWG To PDF" solo sirve para que AutoCAD
  encuentre los papeles ISO); para todas las láminas, PUBLISH.
- Excel del usuario en español: funciones REDONDEAR, SUMA, SI, con separador ";" (lo que él ve al abrir el libro).
  Fórmulas visibles que justifican cada medida ("todo debe justificarse de dónde sale cada uno", 03-10).
- Varias cosas "en un solo Word" cuando el usuario lo dice (carátulas: "todo en un solo Word, no separado", 23-10;
  "solo necesito el archivo en un solo Word, solo las carátulas nada más", 21-10; "índice de planos y carátula de planos en
  un solo Word", 21-10).
- Cuando pide "en un Excel aparte" algo (ACU de lloraderos, desagregado de lija y thinner), se entrega aparte; pero si
  luego pregunta por qué no está en la planilla, la versión definitiva va **dentro de la planilla** como hoja propia (14-10:
  "no veo en el Excel su hoja de ACU de cada una y su metrado"; 15-10 se metió ACU LLORADEROS en la planilla y se borró el
  Excel aparte).

### 2.7 Metrados del usuario: no tocar y verificar
- Regla del traspaso: "NO modificar los metrados del usuario: solo lo que se pida, sobre SU archivo, y comparar antes y
  después".
- Partidas nuevas siempre como partida independiente (ej. 01.04.04 COLECTOR PLUVIAL FRONTAL) con hojas propias
  (COLECTOR PARAMETROS, COLECTOR MOV. TIERRAS, COLECTOR CONCRETO, …), sin tocar las existentes, con el mismo formato y
  colores de la planilla (cabecera azul, Arial Narrow, dato en amarillo claro, fórmula en verde claro; `metrado_xlsx.py`).
- No metrar lo que el usuario ya metró: el 03-10 se agregaron partidas de "prolongación de cunetas" dentro del colector y el
  usuario reclamó "¿y esa partida? ¿por qué? ¿no se supone que ya he metrado yo mis cunetas y tú solo haces el colector?"
  → se retiraron. El 08-10 en CAR Varones: "¿por qué hay empalme si ya he considerado su proyección hasta el colector de
  todas?" → se quitó la partida 01.04.04.06.03 (empalme); la cuneta se metra hasta el muro del colector.
- Si el usuario borró algo de su planilla, fue a propósito ("sí lo quité a propósito, no va allí eso", 08-10): no volver a
  ponerlo.
- Metrado "vigente" = el último archivo que entregó el usuario; se guarda en `insumos/metrados_vigentes/` o en
  `insumos/<proyecto>/vigente/` ("este es, grábatelo", 06-10) y todo cambio posterior se hace sobre ese archivo.
- Después de cada edición: recalcular con LibreOffice y comparar celda por celda con el original; informar "sin cambios en
  las demás partidas" con el número de valores comparados (ej. "los 760 valores anteriores quedan iguales", 22-10; "los 55
  totales del RESUMEN verificados iguales", 07-10; "16 totales idénticos", 21-10).
- Excepción por pedido expreso: tapa ciega (16-10) "actualiza solo el metrado de Solange y Katiuska"; bancas del CAR
  Mujeres (19-10); códigos de lámina del metrado de Varones (23-10, solo textos).
- Al cambiar referencias de láminas en el metrado: solo el texto donde va el código; si la lámina fue excluida del juego,
  **se borra la referencia, no se reemplaza** y el metrado no cambia (23-10: "borra las referencias si hay en el metrado de
  las láminas que borré, solo las referencias del metrado, mas no el metrado").
- Cuando un diseño cambiaría el metrado, preguntar y decir cuánto cambia antes; el usuario quiere saberlo siempre ("dime si
  aumentaste secciones o muros, espesores; el metrado ¿ha variado o no?", 03-10; "con esto que hiciste no alteraste ni un
  número, ¿verdad?", 07-10; "verifica que no se haya cambiado ningún metrado", 08-10).
- Un dibujo puede mejorarse sin tocar el metrado (ej. CAR Mujeres 08-10: el solado se dibuja al ancho exterior y se agrega
  el límite de excavación; el metrado no se tocó).

### 2.8 Estructura Delphin y nombres de partidas
- 06-10: "En mi trabajo están usando la misma base de datos de CAR Mujeres en CAR Mujeres Violentadas, o sea la estructura y
  no las cantidades; eso tenlo en cuenta de ahora en adelante." Criterio escrito en `insumos/solange/vigente/LEEME.txt`:
  - el presupuesto en Delphin del Hogar de Refugio usa la ESTRUCTURA de partidas del CAR Mujeres: mismos nombres, códigos y
    agrupación;
  - las CANTIDADES son siempre las del metrado propio;
  - al comparar con Delphin, los nombres de Delphin son la referencia de redacción y las diferencias de cantidad son normales;
  - solo se cambian nombres cuando la obra es la misma; si la partida describe una obra distinta (dimensión, material,
    espesor, unidad) o no existe en el proyecto, **se consulta antes**.
- 06-10: el ingeniero de presupuesto envió un COMPARATIVO.xlsx; el usuario pidió "analízalo y dime qué se va a modificar
  antes que modifiques algo, solo es nombre nada más creo" y después "dime exactamente qué cambiaste y cómo lo hiciste".
  Resultado: 39 celdas de nombres y la unidad ml → m en rejilla y junta; cantidades, fórmulas y códigos sin cambio.
- Decisiones de estructura tomadas para parecerse a Delphin (07-10 en adelante):
  - concreto del colector en una sola partida 01.04.04.04.01 CONCRETO f'c=210 kg/cm2 PARA COLECTOR (losa de fondo + muros +
    losa superior; el sustento sigue completo en la PLANILLA con subtítulos);
  - registros en una partida por unidad 01.04.04.05.01 TAPA DE REGISTRO (und), con hoja DESAGREGADO TAPA REGISTRO y hoja ACU
    TAPA REGISTRO ("¿le podrías unir esto por und y luego agregar una hoja donde sale desagregado?", 07-10);
  - acabado frotachado de losa superior (vereda) como partida;
  - juntas 01.04.04.06.01 (dilatación en el colector) y 01.04.04.06.02 (entre colector y cerco perimétrico / caja CL);
  - unidad "m" en rejilla y junta de cunetas.
- Partidas globales pedidas "por metro" (15-10, CAR Mujeres, IISS): el cambio de unidad es **solo en el Excel de ACU**
  (tubería por m, accesorios por und, prueba por m3); el metrado original no cambia ("aquí vale lo que es en el Excel
  original, el metrado no tienes por qué cambiar eso").
- Criterio del ingeniero de presupuesto (traspaso): rellenos menores, como la base del emboquillado, van DENTRO de la
  partida de relleno, no como partida aparte.
- Las mismas estructuras y nombres se llevaron al CAR Varones el 15-10 ("así tal cual pero manteniendo los metrados de
  Varones; cambiaremos nombres de partidas, debe ser igual al de Mujeres", `herramientas/varones/planilla_como_refugio.py`).

### 2.9 No mezclar partidas ni láminas entre proyectos
- Nunca sumar una partida en otra ni mover cantidades entre partidas (03-10).
- Integrar lo nuevo en la planilla del usuario "sin mezclar lo que es del colector", en hojas aparte (03-10).
- Cada proyecto con su carpeta de entregables y su generador (ver §3.1). Al reutilizar módulos de otro proyecto, los textos
  fijos (caudales, niveles de piso, cantidades de registros y juntas, existencia de cerco) se convierten en parámetros del
  módulo y cada proyecto los fija en su `compat.py`; se comprueba con una huella que el otro proyecto queda idéntico.
  Caso real (04-10, CAR Varones): las láminas venían con textos del Hogar de Refugio: caudal 560.6 → 221.7 L/s, piso
  +260.60 → +261.15, cerco sí → no hay cerco, registros 10 → 11, juntas 17 → 26.
- Láminas de un proyecto no se citan en otro (23-10: en las especificaciones del Refugio se quitaron dos citas a DJ-01/DJ-02
  y DJ-03, que son láminas del CAR Varones y no existen en el juego DPL).
- "Borra lo antiguo solo de Mujeres Violentadas" (14-10): las limpiezas de versiones viejas se hacen solo en el proyecto
  indicado.
- Gestión de riesgos, PSST y colectores en carpetas separadas (§3.6 y §3.7).

### 2.10 Coherencia entre documentos
- Todo cambio se propaga: metrado ↔ ACU ↔ desagregados ↔ láminas (DP, DA, DD, DJ, DL, isométricos, leyendas, notas) ↔
  especificaciones ↔ memoria hidrológica ↔ memoria descriptiva ↔ memoria de cálculo ↔ índices ↔ carátulas. Buscar los textos
  viejos con grep en generadores y entregables.
- Ejemplo tapa ciega (16-10): DP-06B en los 3 CAR, DD-01, DD-02, DP-06D, DP-08, DP-09, DA-03, isométricos y fotos 3D,
  especificaciones, memorias y metrado (solo Refugio y Varones).
- Ejemplo códigos DPL del Refugio (23-10): memoria hidrológica, memoria descriptiva (relación de 42 láminas), especificaciones y
  carátulas cambiaron solo esas citas (comparado el texto antes y después).
- "El ACU también debe coincidir con los planos" (14-10): las cantidades de las ACU de juntas salen del detalle DD-03.
- Los cuadros de metrado dibujados en las láminas (DA-01 a DA-03) **leen los valores de la planilla** (valores guardados);
  nunca se recalculan aparte.
- Memorias hidrológicas de los 3 proyectos del colector compartido deben coincidir (20-10: "debes explicar bien, detallar
  por qué cambias de 210 a 155, todo justificado; las 3 memorias hidrológicas sin errores deben coincidir cada una").
  Se coordinó con `herramientas/revision_hidrologia.py` (mismo texto en las tres).
- No contradecir el estudio del usuario: el 03-10 el usuario preguntó "¿por qué pones 35.163 mm si el diseño es 210? hay
  contradicción". Lección: cuando una cifra del capítulo nuevo difiere a la vista de la memoria del usuario (P10 = 35.16 mm es
  precipitación; 210.98 mm/h es intensidad de cunetas; 155.66 mm/h es la del colector con tc 15 min), escribir
  explícitamente las intensidades de 10 y 20 min junto a la de diseño y explicar el porqué (bloque "Intensidad de diseño:
  210.98 mm/h en cunetas y 155.66 mm/h en el colector").
- Si dos documentos se contradicen y no se puede saber cuál vale, avisar al usuario con las opciones y recomendar la que
  coincide con su metrado; no cambiar el metrado sin que lo pida.
- Revisión de coherencia de un documento ajeno (memoria de cálculo PDF del CAR Mujeres, 20-10): revisado a mano, se
  corrigieron diferencias de redondeo (área CAR Varones 6 752.03 m² y no 6 752.06; C del Refugio 0.807 y no 0.808),
  progresiva del quiebre 0+078.42 (era 78.47), fecha setiembre 2026.

### 2.11 Insumos y generadores
- `insumos/` = archivos del usuario; no se editan. Las versiones vigentes en `insumos/metrados_vigentes/` y
  `insumos/solange/vigente/`. Cuando un generador debe partir del original, se guarda una copia "ORIGINAL"
  (ej. `insumos/katiuska/METRADO_DRENAJE_PLUVIAL_CAR_VARONES_23-10-2026_ORIGINAL.xlsx`).
- Revisiones de documentos del usuario se entregan como copia en `entregables_*` (ej. la memoria hidrológica de Wilma
  revisada en `entregables_mujeres/MEMORIA_HIDROLOGICA_CAR_MUJERES_CON_COLECTOR.docx`; "el insumo no se toca").
- Todo cambio se hace en el generador Python y se regenera; nunca a mano en el DXF, XLSX o DOCX final. Si un generador avisa
  algo que no reconoce (PSST: "partidas sin actividad reconocida"), se amplía la biblioteca; no se edita el resultado.
- Archivos muy grandes (DXF de 332–381 MB de Barranquita) no se versionan; se extrae una base reducida
  (`insumos/barranquita/base_sitio.pkl`; `.gitignore` excluye `*.pkl`). Sin esa base, se trabaja con cachés
  (`_calc/coberturas.json`, `_calc/junta_piso.json`) y `verifica_b.py --solo-lluvia`.

### 2.12 Planos impresos y láminas congeladas
- "Ya no toques la lámina DP-06B, tampoco las láminas de los perfiles longitudinales, solo las demás" (07-10, Refugio): se
  comprobaron entidad por entidad (huella) antes y después de regenerar.
- "Ya no alteres planos, ya imprimí el último que me pasaste" (21-10, Barranquita): desde entonces `planos_b.py` no se
  regenera; los cambios posteriores (lluvia, superficies, caudales) van a los documentos y se avisan como pendientes (ej. las
  láminas DC-16 a DC-19 rotulan "AGUA DE DISEÑO" con caudales anteriores 207.7 / 264.7 / 174.2 / 48.4 l/s; con la lluvia
  vigente serían 229.2 / 228.9 / 166.2 / 45.5 l/s).
- Juegos finales armados por el usuario en PDF (Refugio DPL, Varones DPLV, CAR Mujeres con códigos propios): sus códigos y
  títulos se usan tal cual el rótulo en índices, memorias, especificaciones y metrado; no se renumeran ni se "corrigen"
  (23-10: "son solo tildes y eso, además la fecha sí es setiembre, así que ya está bien").

### 2.13 Precios y mano de obra
- Cada precio de un ACU lleva su fuente (tienda, fecha, presentación, con o sin IGV). El 09-10 el usuario preguntó "en el ACU
  dime de dónde sacaste el precio de platina de fierro galvanizado 1" x 1/8", ¿tienes algún sustento?" y luego "dame un precio
  real"; el 14-10 "debe ser precio real comprobado, te doy acceso total a internet".
- Precios sin IGV, de fuentes publicadas (ejemplos de `herramientas/angulo_contramarco_refugio.py`): Sodimac Perú, Promart,
  Cemento Pacasmayo, Agregados Tarapoto (Morales), EMAPA San Martín (agua), Maderas del Norte, Konstrutecnia (alquiler de
  equipos); en lloraderos tubo PVC 3" Pavco S/ 39.90 el tubo de 3 m, geotextil 200 g/m² S/ 5.75/m², grava S/ 70.00/m³
  (Agregados Tarapoto). Lo que no tiene precio publicado se rotula "Por cotizar en Tarapoto" (piedra chancada 1/2", grava de
  20 a 40 mm, alquiler de soldadora) y se deja el precio anterior.
- Archivo de sustento de cotizaciones: `entregables/COTIZACION_PRECIOS_ACU_TAPA_REGISTRO_HOGAR_REFUGIO.xlsx` (14-10).
- Mano de obra: el 09-10 preguntó "eso de peón y operario, ¿es real sus precios?"; el 15-10 entregó la tabla oficial
  (`insumos/normas/CAPECO_FTCCP_Remuneraciones_2026.pdf`) y pidió "actualiza todo todo a 2026". Hoja COSTO HORA HOMBRE 2026 en
  cada planilla: CAPECO - FTCCP 2026 (Exp. N.° 339-2025-MTPE/2.14-NC), operario 28.95, oficial 22.68, peón 20.54 S/ por
  hora-hombre, con su desglose (leyes sociales 112.20 %, BUC, movilidad, overol). Todas las ACU leen de esa hoja.
- Formato ACU Delphin: mano de obra (cuadrilla y rendimiento), materiales, equipos (herramientas manuales 3 % de la MO).
- Exportar a S10 o Delphin Express no es posible desde el repositorio (15-10: "¿eres capaz de convertir todo este ACU al S10
  o al Delphin Express?" … "bueno, cerramos ese tema").

### 2.14 Calidad de expediente técnico
- 03-10: "Recuerda que es un expediente técnico. Esto va a firmar especialistas. Según normativas, leyes del Estado." / "al
  final de toda la memoria quiero un documento irrefutable, todo que esté bajo normas, que después la Contraloría no
  intervenga". Cada criterio con su norma (RNE CE.040, E.020, E.050, E.060, Manual de Hidrología, Hidráulica y Drenaje MTC,
  AASHTO LRFD / Manual de Puentes MTC, EG-2013 MTC). Se agregó una hoja CUMPLIMIENTO (requisito, norma, criterio, valor,
  resultado) en la memoria de cálculo, replicada en el Word.
- No sobredimensionar ni subdimensionar: "no puedes disminuir el arranque o altura del colector… no debe ser muy grande
  tampoco, solo lo suficiente para llevar las aguas" (03-10); "lo que yo quiero es ahorrar acero, mucho acero, veo que hay 5000
  kilos, y también no sobredimensionar" (03-10). Resultado: marco único en tramo normal y motos, doble solo en el cruce de
  camiones.
- "Por qué tanto soporte en 2 metros? ¿no sería solo 2 soportes?" (19-10) y "ponle solo dos sujetadores" (22-10): no poner más
  piezas de las necesarias.
- Ser fiel al dibujo del usuario: "debes ser fiel al dibujo, nada de errores" (19-10, banca); "borra esa cúpula" (22-10);
  "ese sumidero no le pondré, solo esa capucha… solo es 2 m lineales de canaleta por techo, es todo a una agua, no hay unión"
  (19-10). Si el plano de origen tiene diferencias (cota rotulada distinta de la dibujada), se informan al usuario.
- Planos "bien detallados, con isométricos, todo excelente" (03-10); detalles constructivos "al más mínimo detalle, todo lo
  que conforma cada uno, desagregándolo, para que lo puedan construir y analizar" (03-10, láminas DD-01 a DD-04).

### 2.15 Confirmar antes de rehacer; no preguntar lo que ya se sabe
- Traspaso: "Explicar primero el plan y confirmar antes de rehacer cosas grandes."
- Ejemplos: "antes que hagas algo más dime por qué necesitas de Katiuska algo, si primero estamos en Solange" (03-10);
  "dime antes que empieces" (15-10, cambio de unidad global → m); "espera, no hagas aún nada" (14-10); "Antes que procedas a
  algo, delimita el cerco perimétrico según lo que tú ves y yo te confirmo, mándame una imagen" (20-10; se hizo
  `revision/CERCO_PERIMETRICO_PARA_CONFIRMAR.png` y se esperó el "procede").
- Para cambios con impacto, mostrar primero un cuadro de control (ej. cuadro de ambientes por bloque y nivel antes de redactar
  la memoria descriptiva del CAR Mujeres, 05-10; cuadro de lectura de perfiles por eje antes de metrar, 04-10).
- El usuario cuida sus créditos: "eso sería cambiar todos los planos y con eso gastarás todos mis tokens" (07-10). Proponer el
  alcance mínimo que resuelve el pedido.
- No preguntar lo que está en el repositorio: "¿por qué me preguntas esto si tú sabes, tienes el plano, sabes por dónde entran
  vehículos como cisterna y por dónde entran motos o peatones?" (14-10); "cómo no va a haber, si aquí hemos trabajado todo"
  (05-10); "revísalo antes de presentarlo… tú ya sabes qué dicen los planos, tienes acceso a los 3 planos de cunetas y
  colectores de cada proyecto" (08-10); "trata de que eso que me pides para yo hacer hazlo tú, o déjalo así nomás" (03-10).
- Si un dato falta de verdad, decirlo aparte, con la hipótesis usada y su efecto (ej. ubicación UTM "referencial, verificar en
  campo"; C.I. 468901 "confirmar si es el CUI").
- No dejar pendiente lo que uno mismo diseñó con excusas: el 15-10 se dijo que la DP-06D de Varones quedaba pendiente porque el
  modelo 3D suponía un colector de 0.80 y el usuario respondió "¿qué me estás diciendo si tú diseñaste eso todo? … todo debe
  ser preciso… todo coherencia" → se resolvió el registro sobre colector de 0.60 (abertura 0.70 apoyada en los muros) y se hizo
  la DP-06D propia.
- Revisar varias veces: "revísalo unas 10 veces" / "comprueba primero 10 veces y dime si se mantiene tu planteamiento"
  (20-10) → ciclo de verificación automática (Barranquita: 11 comprobaciones hasta 11 de 11).

### 2.16 Gestión de riesgos de obra y PSST
- Gestión de riesgos (16-10, SM-107): "hazle en base a todo esto… igual que de los CAR pero orientado a infraestructura vial";
  corrección: "saca lo que es el presupuesto de S10, ponle todo en porcentaje así como en los CAR; las observaciones tampoco,
  no pongas observaciones, nada de eso que hallaste de que no cuadra eso con el otro; recuerda que esto solo es un estudio de
  gestión de riesgos durante la ejecución de la obra; no pongas nada de costos".
  → efectos en % del presupuesto, sin montos en soles, sin observaciones a documentos ajenos. Marco: Ley N.° 32069 y su
  Reglamento, D.S. N.° 009-2025-EF, art. 156.
- PSST (16-10 y 17-10): "¿un programa para el estudio de gestión de riesgos y también salud en el trabajo, que me envíe Word
  ordenadito, tablas, matriz IPER o matriz de riesgos, con gráficos?". Correcciones del 17-10: "esto debe ser algo estándar
  para cualquier tipo de proyecto en Perú… así debes trabajar siempre con su matriz… y debes separarlo, crea otra carpeta
  nueva"; "¿qué hiciste? no te pedí que hagas el PSST de esa carretera… muevas todo a una nueva carpeta llamada PROGRAMA DE
  ELABORACION DE PSST, una general para todo tipo de proyecto". → la carpeta guarda solo el programa general, sin proyectos de
  ejemplo; un PSST de obra se genera solo cuando el usuario lo pide.
- Detalle del método IPERC en el skill `psst-iperc` y en `PROGRAMA DE ELABORACION DE PSST/README.md`.
- Presupuesto del PSST de una obra (28-10, PSST del CAR Mujeres): el número de obreros sale de las horas-hombre del presupuesto
  de obra (Delphin) ÷ (8 h × días por mes × meses del cronograma) y manda sobre el número provisional del presupuesto ("61 es un
  número de trabajadores asumido provisional… ahora ya tenemos oficial, que es 78"). Solo obreros, EPP uno por obrero, solo
  insumos que ya están en el presupuesto de obra, cantidades en und / jgo / rll / par y cada cantidad y precio con su sustento.
  Criterios completos en el skill `psst-iperc` (sección "Presupuesto del PSST").

---

## 3. Registro de proyectos

### 3.1 Tabla general
| Proyecto (nombre corto) | Responsable | Código | Colector / obra | Carpeta de entregables | Generadores | Estado |
|---|---|---|---|---|---|---|
| CAR Varones | Katiuska | CUI 2705619 | colector b 0.60, muros 0.15, 11 registros (RV-01 a RV-11) | `entregables_varones/` | `herramientas/varones/` (`planos_v.py`, `compat.py`, `diseno_v.py`, …) | Juego final DPLV-01 a DPLV-44; metrado vigente del 23-10-2026 |
| Hogar de Refugio Temporal "Mujeres Violentadas" | Solange | CUI 2675514 | colector b 0.80, muros 0.15, 10 registros (7 en losa + 1 en CL + 2 en CC) | `entregables/` y `entregables_solange/` | `herramientas/diseno.py`, `planos_dxf.py`, `memoria_*.py`, `metrado_*.py` | Juego DPL-01 a DPL-42; metrado vigente con bancas OC-01 |
| CAR Mujeres | Wilma | CUI 2717013 | colector b 1.50, muros 0.10, 15 registros | `entregables_mujeres/` | `herramientas/mujeres/` | **Metrado congelado** (ya presupuestado); juego de 46 planos del usuario |
| I.E. N.° 0590 Barranquita (Lamas) – planteamiento preliminar de cunetas | – | C.I. N.° 468901 (confirmar si es el CUI) | cunetas 0.60 (muros 0.10, libre 0.40), h inicial 0.30, S 0.5 % | `entregables_barranquita/` | `herramientas/barranquita/` | Planos DC-01 a DC-19 impresos (no regenerar) |
| Vía SM-107 Tingo de Ponasa – Shamboyacu | – | CUI 2673852 | estudio de gestión de riesgos de obra | `gestion_riesgos/proyectos/SM-107_TINGO_DE_PONASA_SHAMBOYACU/` | `gestion_riesgos/herramientas/` | Entregado (Word, matriz Excel, PR-01/PR-02) |
| Programa de elaboración de PSST | – | (general) | PSST con matriz IPERC para cualquier obra | `PROGRAMA DE ELABORACION DE PSST/proyectos/<obra>/` | `PROGRAMA DE ELABORACION DE PSST/herramientas/` | Programa general, sin proyectos de ejemplo |

Otros proyectos del usuario cuyos archivos están fuera del repositorio (en `D:\GTBM\...`). Se trabajan sobre sus archivos y sin
mezclarlos con los de la tabla:

| Proyecto | Código | Archivos del usuario | Trabajo hecho |
|---|---|---|---|
| I.E. N.° 292 Ciudad Satélite, La Banda de Shilcayo | CUI 2684251 | `D:\GTBM\SATELITE\Drenaje Pluvial\` (metrado de drenaje); planos de arquitectura en `D:\PROGRAMAS\Conversor_DWG_DXF\DXF_convertidos` | 26-10: hoja METRADO DE TARRAJEO en su metrado (interior de cunetas con rejilla y tapadas, muros y fondo; partida 01.04.03.04.02.05); 28-10: revisión de 42 planos de arquitectura con las 14 indicaciones (skill `revision-planos-arquitectura`) |
| I.E. N.° 0603 Sauce | CUI 2647660 | `D:\GTBM\SAUCE\DRENAJE FINAL SAUCE\ESTUDIO DE SEGURIDAD Y SALUD EN EL TRABAJO\` | 28-10: explicación de su hoja de cálculo de personal (horas-hombre ÷ 8 h ÷ meses ÷ días por mes, 48 obreros) y Excel aparte "CALCULO DE PERSONAL EN OBRA - SAUCE"; su Excel de seguridad quedó igual al original (se le habían puesto por error las horas del CAR Mujeres y se devolvió) |
| PSST del CAR Mujeres | CUI 2717013 | `D:\GTBM\ALDEA INFANTIL\WILMA\PLAN DE SEGURIDAD Y SALUD EN EL TRABAJO - MUJERES\` | 28-10: 78 obreros, 10 meses, solo insumos del presupuesto de obra con precios nuevos; total S/ 45,167.72 (Excel, Word del plan y especificaciones iguales) |
| Evacuación y señalización del CAR Varones y del Hogar de Refugio | CUI 2705619 / 2675514 | `D:\GTBM\ALDEA INFANTIL\KATIUSKA\` y `...\SOLANGE\evacuacion\` | 26-10: metrado desde el DXF, especificaciones, informe de inconsistencias para la arquitecta y memoria del Refugio corregida |

### 3.2 Nombres oficiales completos (como van en carátulas)
- **CAR Varones (CUI 2705619)**: "CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS
  PARENTALES O EN RIESGO DE PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES DISTRITO DE MORALES DE LA PROVINCIA DE SAN
  MARTÍN DEL DEPARTAMENTO DE SAN MARTÍN" (`varones/caratulas_v.py`). Rótulo DXF: "UBICACION: PREDIO ALDEA INFANTIL VIRGEN DEL
  PILAR - MORALES - SAN MARTIN - SAN MARTIN" (`varones/compat.py`).
- **Hogar de Refugio Temporal (CUI 2675514)**: "CREACIÓN DEL SERVICIO DE PROTECCIÓN A MUJERES VÍCTIMAS DE VIOLENCIA EN
  SITUACIÓN DE RIESGO DE FEMINICIDIO O PELIGRE SU INTEGRIDAD Y/O SALUD FÍSICA Y/O MENTAL EN HOGAR DE REFUGIO TEMPORAL DISTRITO
  DE MORALES DE LA PROVINCIA DE SAN MARTÍN DEL DEPARTAMENTO DE SAN MARTÍN" (tal como el rótulo de las láminas DPL;
  `caratulas_refugio.py`, `indice_planos_refugio.py`). El rótulo de trabajo antiguo de `dxf_base.py` decía "CREACION DEL
  SERVICIO DE ATENCION INTEGRAL A MUJERES VICTIMAS DE VIOLENCIA EN EL HOGAR DE REFUGIO TEMPORAL MUJERES VIOLENTADAS…": para
  documentos nuevos usar el nombre del rótulo DPL. Ubicación: predio rural Los Mangos, distrito de Morales, provincia y
  departamento de San Martín (frente a la carretera Oasis).
- **CAR Mujeres (CUI 2717013)**: "CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS
  PARENTALES O EN RIESGO DE PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - MUJERES DISTRITO DE MORALES DE LA PROVINCIA DE SAN
  MARTÍN DEL DEPARTAMENTO DE SAN MARTÍN" (`mujeres/caratulas_m.py`). Predio rural Los Mangos (propiedad del Gobierno Regional
  de San Martín), Morales; área del terreno aprox. 7,000 m², NPT 259.75 (datos del pedido de memoria general, 05-10).
- **I.E. N.° 0590 Barranquita (C.I. N.° 468901)**: "MEJORAMIENTO Y AMPLIACIÓN DEL SERVICIO DE EDUCACIÓN PRIMARIA EN I.E. N°
  0590 DISTRITO DE BARRANQUITA DE LA PROVINCIA DE LAMAS DEL DEPARTAMENTO DE SAN MARTÍN" (`barranquita/caratula_b.py`).
  Datos de la memoria de arquitectura del usuario: GRSM / GTBM-T, Mz Z Lote 23 (partida 11128704), terreno 61,413 m², clima Af.
- **SM-107 (CUI 2673852)**: "MEJORAMIENTO DEL SERVICIO DE TRANSITABILIDAD VIAL INTERURBANA EN LA VÍA DEPARTAMENTAL SM-107,
  TRAMO TINGO DE PONASA - SHAMBOYACU, DISTRITO DE SHAMBOYACU, PROVINCIA DE PICOTA, DEPARTAMENTO DE SAN MARTÍN"; entidad Gobierno
  Regional San Martín – Dirección Regional de Transportes y Comunicaciones; progresivas 19+343.39 a 44+693.39
  (`gestion_riesgos/herramientas/riesgos_sm107.py`).

### 3.3 Entidad, servicio y fechas
- Entidad de los 3 CAR y de Barranquita: **GOBIERNO REGIONAL SAN MARTÍN – GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO**
  (rótulo DXF: "ENTIDAD: GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO"). Logo oficial completo entregado por el usuario:
  `insumos/katiuska/LOGO_GOBIERNO_REGIONAL_SAN_MARTIN.png` (el escudo recortado de un Word salía "corto"; 23-10: "este es el logo
  del gobierno, el otro sale corto, corrige"). `caratulas_v.escudo()` toma el escudo completo sin el texto, a 2.8 cm de alto.
- Especialidad: "ESPECIALIDAD DE DRENAJE PLUVIAL" (carátulas CAR) / "ESPECIALIDAD: INSTALACIONES SANITARIAS - DRENAJE PLUVIAL"
  (rótulos DXF y Barranquita).
- Línea de servicio en carátulas:
  - CAR (Mujeres, Varones, Refugio): "SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL EXPEDIENTE TÉCNICO DE PI:"
    (21-10: "esto sí debe ser servicio para elaboración de expediente técnico").
  - Barranquita: "SERVICIO DE DISEÑO - DRENAJE PLUVIAL" (21-10: "corrige, no debe decir EXPEDIENTE TÉCNICO, debería decir
    SERVICIO DE DISEÑO - DRENAJE PLUVIAL"; constante `caratula_b.EXPEDIENTE`).
- Fechas usadas (no cambiarlas sin pedido):

| Documento | Fecha |
|---|---|
| Rótulos DXF generados (`dxf_base.FECHA`) | OCT. 2026 |
| Carátulas CAR Varones y Hogar de Refugio | SETIEMBRE - 2026 (la de los rótulos DPLV / DPL; confirmada por el usuario el 23-10) |
| Carátulas CAR Mujeres | SEPTIEMBRE - 2026 (la de la plantilla de Wilma) |
| Memoria descriptiva y memoria de cálculo PDF de Varones | SETIEMBRE 2026 |
| Memoria de cálculo PDF del CAR Mujeres | setiembre 2026 (corregida el 20-10) |
| Memoria descriptiva del Hogar de Refugio | OCTUBRE 2026 (`memoria_descriptiva_refugio.FECHA`) |
| Barranquita (carátulas, metrado, memorias, análisis) | OCTUBRE 2026 |
| Metrado vigente CAR Varones | 23-10-2026 |
| Metrado vigente CAR Mujeres | 09-10-2026 (con bancas: `..._09-10-2026_CON_BANCAS.xlsx`) |
| Metrado vigente Hogar de Refugio | recibido 06-10-2026; vigente actual con bancas OC-01 (22-10) |

- Carátulas: diseño común (escudo, servicio, proyecto con CUI, foto, franja de color con el título, ubicación y fecha), sin
  proyectista, una por página A4 (verificado que cada una cabe en una página). Colores: CAR Varones y CAR Mujeres granate
  (7B1E2B); Hogar de Refugio verde (1E5E3B, subtítulo D6EEDD; 23-10: "usa otro color diferente, por ejemplo verde");
  Barranquita azul (1F3A68 / D9E2F3). Fotos: Varones `insumos/katiuska/FOTO_PROYECTO_CAR_VARONES.jpg`; Refugio
  `insumos/solange/FOTO_PROYECTO_HOGAR_REFUGIO.jpg` (es la misma imagen); Barranquita foto aérea de dron
  `insumos/barranquita/foto_aerea_ie0590.webp` recortada sin las esquinas oscuras del lente; CAR Mujeres sin foto del usuario
  (21-10: "no tengo foto, pero le puedes poner de la planta de CAR Mujeres").
- Documentos con carátula, en el orden de la carpeta de entrega:
  - Varones y Refugio (7): especificaciones técnicas; memoria de cálculo (canaletas, montantes y cunetas); memoria de cálculo
    (colector pluvial frontal); memoria descriptiva; memoria hidrológica; metrados; planos (DPLV-01 a DPLV-44 / DPL-01 a
    DPL-42). Refugio sin la carátula de "índice de planos" (23-10: "no pongas el que dice índice de planos, solo planos").
  - CAR Mujeres (6): metrados; memoria hidrológica; memoria descriptiva; memoria de cálculo colector; memoria de cálculo drenaje
    interno; especificaciones técnicas.
  - Barranquita (6 + planos): metrado; estudio hidrológico; memoria descriptiva; memoria de cálculo; especificaciones; análisis
    estadístico; planos (en el Word de carátula e índice).

### 3.4 Cadena hidráulica compartida (predio Los Mangos, Morales)
Varones (b 0.60) → caja de llegada CL → Hogar de Refugio (b 0.80) → caja de caída CC con poza → R-01 del CAR Mujeres (b 1.50)
→ salida. El ancho crece aguas abajo; las cotas de fondo y los niveles de agua empalman (verificado el 15-10 en ambos
expedientes).

| Tramo | Cota de fondo inicio → fin | Caudal | Entrega |
|---|---|---|---|
| CAR Varones (CUI 2705619) | 260.20 → 259.884 | 221.7 L/s por el colector + 37.0 L/s por la cuneta Eje 01 directo a la CL = 258.7 L/s | Caja CL: ventana 0.60 × 1.17 en su muro este, techo 261.05 igual en ambos expedientes, caída libre 0.28 m sobre el nivel de agua 259.606 |
| Hogar de Refugio (CUI 2675514) | 259.10 → 258.88 | 258.7 + 301.9 = 560.6 L/s (560.68; en memorias "560.7") | Salida de la CL 0.80 × 1.40; caja CC con poza; ventana de salida al R-01 de 1.50 × 0.43 (alto interior del colector del CAR Mujeres en su R-01: losa 259.25 − 0.10 − fondo 258.72) |
| CAR Mujeres (CUI 2717013) | 258.72 → 258.30 (L = 139.08 m, S = 0.302 %) | 560.6 + 262.3 = 822.9 L/s en la salida | Nivel de agua inicial 259.063 (Refugio entrega con 259.062) |

- Ubicación UTM del R-01: (345666.974, 9282776.560), igual en el Refugio y en el CAR Mujeres.
- Niveles de piso (losa superior = vereda): Varones +261.15 (sin cerco en el frente; la tapa de la CL también a 261.15);
  Refugio +260.60 (al nivel de estacionamientos e ingresos; el usuario corrigió el 03-10 que el ingreso "OE 01 260.45 está mal,
  es igual 260.60"); CAR Mujeres +259.25. Entre Refugio y Mujeres hay ~1.50 m de desnivel: por eso la caja de caída con poza.
- Parámetros hidrológicos comunes (traspaso): T = 25 años; P24 = 121.81 mm; Dick–Peschke (exponente 0.25); P10 = 35.16 mm;
  P20 = 41.82 mm; cunetas y canaletas tc = 10 min, I = 210.98 mm/h; colector tc = 15 min, I = 155.66 mm/h; FS = 1.15;
  C: techos y veredas 0.88, estacionamientos 0.86, áreas verdes 0.29, patios 0.40. Refugio A = 7,520.41 m², C 0.807 (no 0.808)
  → 301.9 L/s; Varones A = 6,752.03 m² (no 6,752.06), C 0.771 → 258.7 L/s (con I = 155.66, no 210.98).
- Trato documental: en cada expediente el vecino de aguas arriba es "aporte externo" (dato de su memoria) y el de aguas abajo
  "receptor" (condición de entrega: cota de fondo de llegada ≥ 258.72 y caudal conjunto ≤ 560.7 L/s en el R-01). El CAR Mujeres
  es el proyecto que recibe todos los caudales (06-10).
- Constructivamente (pregunta del usuario el 15-10: "¿el final del colector Varones empalma o se adapta al inicio de Mujeres
  Violentadas, y éste al inicio de Mujeres Wilma?"): sí; se revisaron ventanas, techos, cotas de fondo y niveles de agua en los
  dos lados de cada empalme.
- El cruce de la carretera Oasis (badén o alcantarilla) queda fuera del alcance; se recomienda comunicarlo a la entidad de la vía
  (memoria descriptiva del CAR Mujeres, 20-10). Todo el colector va dentro del lindero, sin invadir la carretera.

### 3.5 Particularidades por proyecto (lo que distingue a cada uno)
**CAR Varones (CUI 2705619)**
- No hay cerco perimétrico en el frente (04-10: "corrige algo urgente, no hay cerco perimétrico en Varones"): sin junta
  longitudinal; terreno natural a ambos lados; la única junta con otra estructura es el contacto con la caja CL (4.64 m).
- Ingreso de camiones cisterna por el Eje 09 (5.80 m); el colector arranca allí. No hay cruce de motos.
- Registros exactamente sobre el cruce de cada cuneta (las cunetas que llegan son las líneas rectas perpendiculares en negro,
  no las verdes; 04-10).
- Cunetas acortadas en el metrado de cunetas al llegar al muro del colector: 0.04, 0.10, 0.26, 3.39 y 2.77 m.
- Registro sobre colector de 0.60 con abertura de 0.70: el rebaje apoya en la cabeza de los muros en los lados largos; borde
  engrosado solo en los 2 lados transversales (2 × 0.60 = 1.20 m por registro); concreto del colector 56.02 → 55.72 m³.
- Lloraderos: 226 und en 34 tramos (320.53 m de muro). DL-00 de ubicación de lloraderos (23-10).
- Hasta la mañana del 15-10 conservaba el sello de poliuretano y el contramarco L 2"x2"x3/16"; desde la tarde del 15-10 usa,
  como el Refugio, sellador asfáltico 1" × 2" (RC-250 + arena) y contramarco L 1 1/2"x1 1/2"x1/8" (variables `SELLO_JUNTA` y
  `CONTRAMARCO` en `varones/compat.py`); desde el 16-10, tapa ciega sin marco ni contramarco en el metrado (11 tapas).

**Hogar de Refugio Temporal (CUI 2675514)**
- El colector va pegado al cerco perimétrico por un solo lado; al otro lado hay solo tierra (no hay vereda): junta longitudinal
  01.04.04.06.02 solo entre el muro del colector y el cimiento del cerco, de 0+000.00 a 0+058.81 (partida 210.98 → 58.81 m;
  15-10: "el colector solo tiene junta longitudinal a todo el largo pegado al cerco perimétrico de 1"; al otro lado no hay vereda,
  nada, solo es tierra").
- Frente con ingreso peatonal, ingreso de motos (pequeño) e ingreso vehicular de cisterna (4.41 m): no todo es losa vehicular
  (03-10).
- Losa superior del colector = vereda.
- Lloraderos: 157 und (226.21 m de muro). Bancas OC-01: 9 bancas = 3 juegos (techos de 3.79, 4.21 y 3.79 m).
- Láminas DP-06B y perfiles longitudinales congelados desde el 07-10.

**CAR Mujeres (CUI 2717013)**
- Metrado congelado: "sin variar sus metrados porque ya están en el presupuesto" (08-10); "en Mujeres Wilma ya no puedo mover
  porque ya está presupuestado" (08-10); "ya en el de Mujeres no se puede cambiar" (14-10). Por eso no lleva lloraderos (19-10:
  confirmado que no se metraron) y conserva en su metrado la partida "TAPA DE REGISTRO 0.68x0.68 C/MARCO Y CONTRAMARCO",
  aunque su lámina D-RL y la memoria indican tapa ciega (pendiente de decisión del usuario).
- Excepciones pedidas: canaleta de las 16 bancas de jardinería (19-10, subtítulo 1.4.4.5.4 y codo PVC 4" × 45° en el RESUMEN);
  ACU de partidas globales de IISS (15-10).
- Pendiente informado: la tapa del R-07 (0+060.15) entra 0.20 m en el cruce de camiones (0+054 a 0+060) y solo está verificada
  para rueda de auto; confirmar por dónde pasan los camiones.

**I.E. N.° 0590 Barranquita (C.I. N.° 468901)**
- Todo dentro del cerco perimétrico (área de intervención confirmada por el usuario con imagen); el agua sale por pase en el
  cimiento (D1 a D4), sin pozas. Ejes = líneas magenta del usuario. Niveles finales: NPT +184.65 = borde de cuneta; área verde
  +184.60; patio de maniobra +184.50 con cuneta al ras. Planos impresos: no regenerar.
- Proyecto de otra ubicación y otra estación de lluvia (Pongo de Caynarachi, SENAMHI 003317): no se mezclan sus datos con los de
  Morales.

**SM-107 y PSST**: ver §2.16.

### 3.6 Carpeta de gestión de riesgos
`gestion_riesgos/` con `herramientas/` (copia propia de `dxf_base.py`, `dxf_layouts.py`, `dxf_render.py`) y
`proyectos/<proyecto>/insumos|entregables`. Un proyecto nuevo va en su carpeta. SM-107: Word, matriz Excel con fórmulas
(34 riesgos, 3 oportunidades, P × I, valor esperado, Monte Carlo), planos PR-01 y PR-02.

### 3.7 Carpeta del PSST
`PROGRAMA DE ELABORACION DE PSST/` con `herramientas/` (`biblioteca.py`, `importar_s10.py`, `generar.py`, …),
`plantilla/DATOS_PROYECTO.xlsx`, `proyectos/<obra>/` y `GENERAR_PSST.bat`. El usuario no veía la carpeta en su panel ("no veo
la carpeta en el lado derecho", 17-10): debe quedar creada en la raíz del repositorio y subida (commit y push) para que aparezca.

---

## 4. Códigos de láminas vigentes

Regla: en índices, memorias, especificaciones, metrados y carátulas se usan los códigos y títulos **tal cual el rótulo** del
juego final del usuario, aunque tengan erratas (Varones: DPVL-09, DPVL-10, DVPL-11; "CONTRUCTIVO", "ALAMACEN"). Los códigos de
trabajo de los generadores (DP-, DA-, DD-, DJ-, DL-, DR-, DS-, DO-, DB-) se reemplazan por los del juego final cuando existe.

### 4.1 Hogar de Refugio — DPL-01 a DPL-42 (PDF `insumos/solange/PLANOS_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS_LAMINAS.pdf`)
| Grupo | Láminas |
|---|---|
| Red de cunetas | DPL-01 red general de drenaje pluvial; DPL-02 perfiles longitudinales; DPL-03 a DPL-05 secciones transversales 01 a 03 |
| Colector pluvial frontal | DPL-06 red general colector; DPL-07 perfil general; DPL-08 y DPL-09 perfil detallado; DPL-10 y DPL-11 secciones del colector; DPL-12 a DPL-14 isométricos de las secciones |
| Montantes por edificación | DPL-15 a DPL-23 detalle montante EDIF01 a EDIF09 |
| Detalles del colector | DPL-24 registro con tapa ciega 0.68×0.68×0.08; DPL-25 empalme de cunetas a colector; DPL-26 caja de llegada (0+000) y caja de caída con poza (entrega al CAR Mujeres); DPL-27 isométricos constructivos; DPL-28 juntas e=1" con tecnopor y sellador asfáltico (colector y cerco); DPL-29 registro con tapa ciega – componentes |
| Canaletas y montantes | DPL-30 canaleta de techo, soporte y accesorios; DPL-31 isométrico de canaleta, soportes, pernos, tapa y boquilla; DPL-32 detalles 3D del montante; DPL-33 elevación de canaleta y corte del montante; DPL-34 isométrico del montante típico |
| Sumidero, lloraderos, falsa columna | DPL-35 isométrico de caja sumidero; DPL-36 detalle de caja sumidero; DPL-37 isométrico de instalación de lloraderos (A1); DPL-38 detalle de lloradero (A2); DPL-39 falsa columna (A3); DPL-40 planta de ubicación de lloraderos (A0) |
| Obra complementaria OC-01 | DPL-41 isométrico del drenaje de la OC-01 (jardinera + banca + pérgola); DPL-42 salida de la canaleta de la OC-01 (A2) |
- Historia: el 22-10 el PDF tenía 40 láminas ordenadas por formato (A0, A1, A2, A3) y el isométrico de lloraderos tenía en el
  rótulo DPL-36 (repetido con la caja sumidero). El usuario corrigió: "el PDF de planos está ordenado por formato de hoja, primero
  A0 y así hasta abajo, y no ordenado por número" y rechazó las observaciones en el índice. El 23-10 entregó el PDF de 42 láminas
  que imprime, con numeración sin duplicados: el índice va de la DPL-01 a la DPL-42 con grupos temáticos.

### 4.2 CAR Varones — DPLV-01 a DPLV-44 (PDF `insumos/katiuska/PLANOS_DRENAJE_PLUVIAL_CAR_VARONES_LAMINAS.pdf`)
- DPLV-01 red general; DPLV-02 a 04 secciones transversales 01 a 03; DPLV-05 y 06 perfiles longitudinales; DPLV-07, 08, DPVL-09,
  DPVL-10, DVPL-11, DPLV-12 a 16 detalle montante edificación 01 a 10; DPLV-17 planta del colector; DPLV-18 perfil general;
  DPLV-19 y 20 perfil detallado; DPLV-21 y 22 secciones del colector; DPLV-23 registro con tapa ciega; DPLV-24 empalme de cuneta;
  DPLV-25 empalme con la caja CL del Hogar de Refugio; DPLV-26 registro – componentes; DPLV-27 rebaje de asiento y refuerzo de
  borde; DPLV-28 tapa ciega: fabricación y colocación; DPLV-29 juntas (colector y caja CL); DPLV-30 empalme de cuneta (ventana y
  caída); DPLV-31 junta de cunetas (toda la sección); DPLV-32 proceso constructivo de la junta en isométrico; DPLV-33 rejilla
  móvil; DPLV-34 isométrico de instalación de lloraderos; DPLV-35 detalle de lloradero; DPLV-36 a 38 canaleta, soportes y
  montante; DPLV-39 y 40 caja sumidero; DPLV-41 y 42 montante; DPLV-43 planta de ubicación de lloraderos; DPLV-44 falsa columna.
- Equivalencias aplicadas al metrado (23-10, `varones/codigos_laminas_metrado_v.py`, 140 celdas): DP-01→DPLV-17, DP-02→DPLV-18,
  DP-04→DPLV-21 y DPLV-22, DP-06B→DPLV-23, DP-06C→DPLV-24, DP-07→DPLV-25, DD-01..04→DPLV-27..30, DJ-01→DPLV-31, DL-01→DPLV-34,
  DL-02→DPLV-35. DP-08 (cuadro de doblado) y DA-01 a DA-03 (cuadros de metrado) fueron excluidos por el usuario: su referencia se
  borra (ej. "Criterio (lámina DA-02): …" → "Criterio: …"; celdas cuyo único texto era la referencia quedan vacías).
- Índice: ordenado de la DPLV-01 a la DPLV-44 sin grupos (23-10: "el índice debes arreglarlo, ordénale de la lámina uno a la
  última sucesivamente"; `I.ORDEN = 'numero'`).

### 4.3 CAR Mujeres — 46 láminas del juego del usuario (lista en `insumos/wilma/LISTA_PLANOS_ANDFY_MUJERES.txt`)
RGDPLV-01; ST-DPLV-01 a 04; PL-DPLV-01; IM-DPLV 01 a 10; IM-ING-DPLV 01 y 02; PCPLV-01; PLGC-01; PLDT-CG T01 03, T04 06, T07 09;
ST-CG-01 y 02; ISM-ST-01 y 02; STP-CG; D-RL; IC-01; DCTSA-01; D-ECC; ESDAE-01; ISM-MPLV; DS-01; DFC-MPLV-01; DT-RDTJ-01 a 07;
IDP-BJ; DI-CBCB (dos láminas con el mismo código: observación informada, láminas 45 y 46). Formatos: 3 A0, 15 A1, 21 A2, 7 A3.
- Equivalencias usadas en la memoria hidrológica (20-10): DP-04 → ST-CG-01 y ST-CG-02; DP-06A → STP-CG; DP-07 → ESDAE-01;
  DP-09 → IC-01 (isométrico 4: estructura de salida). Tapa del registro según D-RL: tapa ciega sin marco ni contramarco.
- Juego de trabajo del colector generado el 08-10 (`mujeres/planos_m.py`): DP-01 a DP-10 a escala real (DP-02, DP-06C y DP-08 en
  A2, el resto A1; índice DP-00 en A3).

### 4.4 Barranquita — DC-01 a DC-19 (impresos)
DC-01 planta general 1/250; DC-02 cuadro de tramos y secciones típicas 1/5; DC-03 a DC-11 perfiles longitudinales por eje 1/50;
DC-12 a DC-14 secciones transversales 1/20; DC-15 cortes generales 1/250; DC-16 a DC-19 detalle de las descargas D1 a D4 por el
cerco (1/25). Todas A1. Si cambia la cantidad de láminas, numeración correlativa sin saltos.

### 4.5 Juegos de trabajo del colector (generadores) y láminas sueltas
- Refugio (24 láminas): DP-00 índice (A3), DP-01 planta, DP-02 perfil general, DP-03A/B perfiles de detalle 1/25, DP-04A/B y
  DP-05A/B secciones, DP-06A secciones típicas, DP-06B registro con tapa ciega, DP-06C empalme de cuneta, DP-06D isométricos de la
  tapa, DP-07 cajas CL y CC, DP-08 cuadro de acero y especificaciones, DP-09/DP-10 isométricos, DA-01 a DA-03 cuadros de partidas,
  DD-01 a DD-04 detalles constructivos.
- Detalles de cunetas DJ-01 a DJ-03 (junta, proceso constructivo, rejilla); lloraderos DL-00 a DL-02; red de techo DR-01 a DR-06;
  sumidero DS-01 y DS-02; OC-01 DO-01 y DO-02 (luego DPL-41/42); banca del CAR Mujeres DB-01 a DB-03; riesgos PR-01 y PR-02.

---

## 5. Cronología de correcciones del usuario sobre la forma de trabajar y entregar

Formato: fecha — lo que dijo (resumido, en sus palabras cuando es útil) → lo que se aprendió.

### 03-10-2026 (traspaso y Hogar de Refugio)
- Traspaso con reglas (§2.6, §2.7, §2.8, §2.15) y trato entre proyectos (§2.3).
- "Antes que hagas algo más dime por qué necesitas de Katiuska algo, si primero estamos en Solange; más bien te pasaría el DXF
  de Wilma para que veas cómo empalmar" → trabajar el proyecto en curso; lo necesario es el receptor; no pedir de más.
- "En la entrada el nivel de piso o de colector terminado es 260.60, para que esté a nivel de estacionamientos e ingresos; el
  260.45 está mal" → la losa del colector va al nivel del piso del frente.
- "No todo eso es losa vehicular… hay una entrada peatonal, una de motos pequeña y otra de vehículos o cisterna" → zonas de
  carga por ingreso.
- "Sobre los metrados no vayas a mezclar las partidas sumando uno en otro; debes mantener eso así" (§2.9). "Dime en idioma
  fácil" (§2.1).
- "No olvides los planos bien detallados con isométricos y que sea todo excelente."
- "No debe ser muy grande tampoco… allí podrías hacer un disipador de energía"; "quiero ahorrar acero… no sobredimensionar;
  es un expediente técnico, lo firman especialistas" (§2.14).
- "No uses color amarillo, el fondo de mi AutoCAD es blanco; los 3D salen negros; el acero longitudinal y transversal con
  colores diferentes; el perfil no se aprecia" → paleta para fondo blanco; colores verdaderos.
- "La losa es 0.20 y debe medir 0.20; dice 0.80 m; dice 3.50 y mide 7.30; algo verde debajo de las cunetas" → escala real y
  revisión de cada cota (§2.5).
- "Las líneas que indican se mezclan, usa flechas, acomoda todo; el acero rojo se sale del muro; el longitudinal debe ser
  círculos, no cuadraditos" → llamadas ordenadas con flecha, acero dentro del concreto.
- "Otra vez ese hueco… ¿por qué hay un vacío allí?" → revisar huecos y vacíos de dibujo (caja de caída en su posición real).
- "Revisa todo el plano, no quiero errores así nuevamente; el diámetro de las barras tal cual es; que nada quede al aire, que el
  acero no salga de su losa; estos planos van a ser para que construyan y deben ser entendibles y legibles."
- "¿Aumentaste secciones o espesores? ¿El metrado ha variado?" / "¿Y el archivo Excel? ¿nada?" → informar impacto y entregar
  todo.
- "¿Por qué pones 35.163 mm si el diseño es 210? hay contradicción" → explicar las intensidades y no contradecir la memoria.
- "Quiero un documento irrefutable, todo bajo normas, que después la Contraloría no intervenga" / "lo que me pides para yo hacer,
  hazlo tú o déjalo así".
- "¿Y esa partida (prolongación de cunetas)? ¿No se supone que ya he metrado yo mis cunetas y tú solo haces el colector?" →
  no metrar lo del usuario.
- "Esta es mi planilla… tú debes integrar aquí sin mezclar lo que es del colector; agrega hojas donde salga el metrado del
  colector, preciso, cómo sale cada medida exacta; utiliza mi formato y colores; todo debe justificarse."
- "¿Por qué borras todo mi metrado de la hoja concreto en cunetas y encofrado?" → al guardar con openpyxl se perdían datos e
  imágenes; se corrigió reinyectando la imagen de encabezado (VML) y el orden de elementos de la hoja; luego se adoptó la edición
  directa del XML (§6.1).
- "El que va a cotizar o hacer su ACU me va a pedir detalles de cada uno (registros, tapas, juntas, empalme); hazle sus planos
  aparte bien detallados, al más mínimo detalle" → láminas DD-01 a DD-04 con despiece y cuadro de componentes por unidad.

### 04-10-2026 (CAR Varones: cunetas y colector; MetraP)
- Convención de colores del DXF de perfiles de Varones (azul tramo abierto, verde tramo cerrado, magenta losa de fondo y acero
  transversal en secciones, círculos azules acero 3/8" en tramos tapados) → leer colores y medidas antes de metrar y mostrar lo
  leído.
- "Usa el mismo formato tal cual la hoja, detalle a detalle, no hagas de otra forma"; "por ahora no vamos a hacer el colector
  hasta que te indique" → seguir la plantilla del usuario y el orden que él marca.
- "Las cunetas que superen 0.40 m llevarán acero… salvo excepción si aparece una cuneta tapada… la altura la mido desde el NCT;
  el acero transversal de las tapas mide 0.56 siempre y la separación es 0.25" → regla de acero (skill `metrado-cunetas`).
  El 04-10 por la tarde volvió a preguntar si se aplicó: comprobar y responder con el dato.
- "Excelente tu forma de metrar… ¿puedes crear un motor para un programa exe?" y "¿el programa puede ser general, o necesitas
  que te dé yo los colores?" → MetraP con configuración (`metrap_config.json`) y aviso de lo que no pudo leer en vez de inventar.
- "Guarda tu análisis del metrado en un prompt o skill para verlo después" → skill `metrado-cunetas`.
- "El colector todo debe estar a 261.15 al ras de lo de afuera; entrada de camiones solo por el Eje 09, longitud 5.80" ;
  "todo debe coincidir, tú ya sabes cuánto caudal bota Varones" → usar los datos ya fijados en el otro expediente.
- "Las cunetas de llegada no van a llegar hasta la franja; eso se tiene que restar" → acortamientos en el metrado de cunetas.
- "Antes dime: ¿va a variar planos o metrados de Solange?" → informar efecto en el proyecto vecino antes de seguir.
- "No hay cerco perimétrico en Varones… las tapas no van exactamente donde entrega la cuneta"; "las cunetas son las que van
  recto, perpendicular, la que está en negro" → no copiar supuestos de otro proyecto; registros en el cruce real.
- MetraP: "se ve muy rudimentario… dame 4 opciones de diseño visual"; "quiero moderno; lo de la web no me gusta" → MetraP 2.0
  PyQt6 (escritorio).

### 05-10-2026 (memoria descriptiva general del CAR Mujeres)
- Reglas del pedido: solo información real; mostrar cuadro resumen por bloque y nivel antes de redactar; no inventar; no
  "completar"/"insertar"; redacción formal sin frases de IA; revisar que las áreas sumen; entregar en Word.
- "Cómo no va a haber, si aquí hemos trabajado todo" → usar todo lo del repositorio.
- "Muy poco son 13 páginas, debe ser mucho más: 50, 60 o 45" → extensión acorde a un expediente (salió de 68 páginas).
- "Debes poner también la parte de arquitectura antes de drenaje; el drenaje hazlo mínimo, no quiero que se note mucho";
  "del estudio de suelos no metas todo, solo lo que debe ir en memoria descriptiva".

### 06-10 y 07-10-2026 (Delphin, ACU, tapa, orden de planos)
- "Este es [mi metrado], grábatelo" → metrado vigente guardado como referencia.
- COMPARATIVO del ingeniero de presupuesto: "analízalo y dime qué se va a modificar antes que modifiques algo"; "dame el texto
  para escribirle al ingeniero en un párrafo, fácil"; "usan la misma base de datos de CAR Mujeres… la estructura y no las
  cantidades"; "solo para cambiar nombre y adaptarle al Delphin"; "dime exactamente qué cambiaste y cómo lo hiciste".
- "Concreto del colector en tres partidas y Delphin usa una… ¿no lo puedes hacer como Delphin?" → una sola partida.
- "Tapas: esto queda así, solo que al último en una hoja hazme bien detallado su ACU" → ACU TAPA REGISTRO; luego "el ingeniero
  me pidió esto por und… ¿y agregar una hoja donde sale desagregado como mis demás plantillas?" → partida por und + hoja
  DESAGREGADO TAPA REGISTRO; "sepárame en un Excel solo el resumen, desagregado, ACU…".
- Tapa: "hazme un dibujo bien exacto en DXF… 4 vistas tipo 3D pero realista… separando cada composición"; "usa letra grande,
  tus letras son pequeñitas; colores que combinen con el fondo blanco; varios isométricos"; "¿cómo sería una foto realista,
  dos vistas, como queda instalado?"; "qué excelente estilo… así quisiera mis secciones transversales".
- "Hay láminas en desorden, letras en vertical, letras sobrepuestas… arregla, ordena y todo es escala real" → skill
  `planos-ordenados` ("dame el prompt o skill para que así haga los planos ordenados").
- "Ya no toques la lámina DP-06B, tampoco las láminas de los perfiles longitudinales; solo las demás, con leyendas y colores"
  → láminas congeladas con huella.
- "Con esto que hiciste no alteraste ni un número, ¿verdad?" → comparar el metrado tras cambios de planos.

### 08-10-2026 (orden de planos, layouts, especificaciones, lloraderos)
- CAR Mujeres: "arregla y ordena los planos sin variar sus metrados porque ya están en el presupuesto"; "¿cuadra todo?";
  "¿todo coincide al milímetro?" → verificar colector contra metrado partida por partida.
- "Las láminas ¿todas son A1? así me sale cuando doy Ctrl+P"; "tienen mucho espacio, reduce los espacios; hay planos grandes y
  pequeños, dimensiona en A1, A2 o A0"; "déjalo en layout de AutoCAD para que imprima y dame un índice de láminas" →
  presentaciones 1:1 e índice DP-00.
- CAR Varones: "arregla los planos con el skill y configura el layout"; "verifica que no se haya cambiado ningún metrado";
  "sí lo quité a propósito… ¿por qué hay empalme si ya he considerado su proyección?" (§2.7).
- "¿Y la conversación de hoy?"; "no veo la conversación"; "¿por qué cuando salgo y vuelvo ya no hay la conversación?" → se creó
  `BITACORA_CONVERSACION.md` con lo hecho por día (memoria escrita entre sesiones).
- "Me falta las especificaciones, tal cual, completito, según normativas peruanas, al más mínimo detalle de cómo se construirá"
  → especificaciones por partida de los tres proyectos; "revísalo antes de presentarlo; tú ya sabes qué dicen los planos".
- Lloraderos: "solo al proyecto de Mujeres Violentadas y Varones; en Mujeres Wilma ya no puedo mover porque ya está
  presupuestado; lloradero de PVC solo donde la cuneta esté expuesta a área verde".
- "El nombre CIP no pongas nada"; "pásame la hoja ACU sola de lloraderos".

### 09-10 y 10-10-2026 (precios, canaleta, sumidero)
- "¿De dónde sacaste el precio de la platina? ¿tienes sustento?"; "dame un precio real"; "dame texto para justificarle un precio
  aproximado al ingeniero de presupuesto"; "¿eso de peón y operario es real?" → precios con fuente (§2.13).
- "Dibújame en DXF el detalle de canaleta, platina…"; "debe ser su isométrico tal cual, detalles hasta de los pernos, según tu
  ACU" → los dibujos muestran lo que se metró y valorizó.
- "La sección de la canaleta es 0.20 de ancho y 0.25 de altura, recuerda" → no alterar medidas dadas por el usuario.
- "Borró el subdrén, entonces solo lloraderos" → se retiró el subdrén de leyendas y especificaciones.
- Sumidero de piso: "olvídate de ese sifón… solo va un codo de 90°" → no agregar piezas que el usuario no usa.

### 14-10 y 15-10-2026 (juntas, tapa, CAPECO, Varones igual al Refugio)
- "¿Esto es de CAR Mujeres Violentadas? Dámelo en Excel aparte"; "¿por qué todo escribes en inglés?".
- "Explícame estas dos partidas de junta… ¿dónde va cada una?" → esquema explicativo antes de cambiar.
- "Espera, no hagas aún nada; cambia el nombre de esas dos partidas: una debe decir en colector y la otra entre colector y cerco
  perimétrico, porque no hay vereda afuera; no le pongas sello elastomérico, ponle tecnopor y sellador asfáltico igual que la
  normativa que te pasé" → nombres corregidos, sellador asfáltico 1" × 2" (RC-250 + arena), EG-2013 MTC Sección 510.
- "¿La tapa es solo peatonal? ¿por qué me preguntas si tienes el plano?"; "precio real comprobado".
- "Borra lo antiguo solo de Mujeres Violentadas"; "no veo en el Excel su hoja de ACU de cada una y su metrado"; "el ACU también
  debe coincidir con los planos".
- "Junta colector-cerco: solo hay a un lado el cerco… Juntas de las cunetas: hazlo según reglamento, sin errores, ya no quiero
  estar haciendo el mismo proceso; mano de obra: actualiza todo a 2026" → junta de cunetas en toda la sección en U
  (2 × H + 0.40 por junta), CAPECO-FTCCP 2026.
- "La lámina DD-03 está mal: el colector solo tiene junta longitudinal… al otro lado no hay vereda, solo tierra"; "DJ-01 está bien;
  hazle 3D isométricos de todo el proceso constructivo y el detalle de la rejilla".
- "Así tal cual pero manteniendo los metrados de Varones; cambiaremos nombres de partidas igual al de Mujeres" (§2.8).
- "¿Qué me estás diciendo si tú diseñaste eso todo?… todo debe cuadrar, coherencia" (§2.15); "¿constructivamente todo cuadra?".
- "Dame los archivos finales de Varones y de Mujeres Violentadas"; "¿ya está todo, con detalles 3D, rejillas, todo lo nuevo y los
  metrados últimos?" → entregar el juego completo y actualizado.
- Memorias de cálculo en PDF con el estilo del ejemplo (pedido expreso, excepción a "PDF solo a pedido").
- "El ACU solo de las partidas en global… en un nuevo Excel"; "lo quiero por metro, dime antes que empieces porque después tendré
  que valorizar"; "vale lo que es en el Excel original, el metrado no tienes por qué cambiar" (§2.8).

### 16-10 y 17-10-2026 (tapa ciega, riesgos, PSST, continuidad)
- "Las tapas del colector deben ser tapa ciega… se construye aparte en obra y ya no tiene marco metálico; hazme el detalle de los
  3 CAR y actualiza solo el metrado de Solange y Katiuska" → propagación a todas las láminas y documentos; CAR Mujeres solo
  lámina.
- Estudio de riesgos SM-107: sin S10, en %, sin observaciones (§2.16).
- "¿Todo el diseño del colector se puede hacer en un programa sin depender de la IA?"; "quiero que el programa también tenga la
  capacidad de decisiones de criterio y de revisar que el plano se vea bien… interpretando el reglamento" (sección 8).
- "¿Cómo hacemos para pasar todo lo que sabes de los colectores a otra conversación?" → `CLAUDE.md` y skill
  `diseno-colector-pluvial`.
- PSST: programa general, carpeta propia, sin el PSST de la carretera, visible en su panel (§2.16, §3.7).

### 19-10-2026 (CAR Mujeres: bancas)
- "¿Cuánto de cunetas construidas hay en el CAR Mujeres, en m²… dame en metros lineales y metros cuadrados" → responder con los
  dos.
- "¿Al CAR Mujeres le hemos metrado lloraderos? creo que no" → confirmar contra el metrado (no lleva).
- "Es un detalle pequeño… dame un texto pequeño, párrafo, para mandarle a la arquitecta".
- Banca: "falta los cortes frontales; no sale el colgador en el isométrico; debes ser fiel al dibujo, nada de errores"; "¿por qué
  tanto soporte en 2 metros?"; "16 techos iguales: metrado de canaleta, codos, colgador, abrazadera en un Excel solo eso"; "ese
  sumidero no le pondré… solo 2 m de canaleta por techo, a una agua, no hay unión"; "¿de cuántos mm para este techito?"
  (aluzinc 0.50 mm).
- "Cómo meto solo eso a este Excel general… no olvides crear una hoja nueva del metrado de ese techo"; "sí agrega el codo de 45
  ya que eso está en el cuadro de montantes" → agregar solo lo pedido y verificar que todo lo demás quede idéntico.

### 20-10 y 21-10-2026 (Barranquita, memorias de Wilma, carátulas)
- "Revísalo unas 10 veces… ninguna cuneta queda enterrada, todas con descarga por gravedad"; "explícame qué color significa cada
  uno, tú ya sabes cómo son mis gráficos".
- "Me entendiste mal: el 3D solo de las cunetas con el terreno… no podemos salir del área de intervención (el cerco)… con esta
  instrucción cambian todas las cosas, necesito que me confirmes"; "antes que procedas delimita el cerco y mándame una imagen".
- "Por favor dime todo en español"; "¿cuál hondonada si todo el terreno está nivelado del cerco para adentro?"; "¿a qué te
  refieres aquí?".
- Niveles (en tres pasos): 184.65 pisos / 184.60 cuneta / 184.55 área verde; luego "donde es el patio de maniobras que quede así,
  la cuneta se adapta… no irá 5 cm abajo porque ya es hueco, al ras"; final: cunetas al ras del NPT 184.65, área verde 184.60.
- "Dame urgente la última memoria hidrológica final de Wilma"; "revisa si todo cuadra con los caudales que recibe de Solange y
  Katiuska"; "¿estás cambiando la intensidad 210?"; "explica por qué cambias de 210 a 155, las 3 memorias deben coincidir".
- "Cambié nombre a varios planos, corrige basándote en estos para actualizar solo la memoria hidrológica de Wilma" → solo ese
  documento.
- "Revisa si está bien [la memoria de cálculo PDF]" → "procede, corrige".
- Perfiles de Barranquita "así tal cual estilo de línea, colores, separación… divididos por ejes"; "hazlo ordenado, no alteres o
  mezcles líneas"; "la sección 4 de 15 cm es imposible, se obstruye el flujo"; "en cunetas de 30 estás considerando acero, el
  acero se considera a partir de 40"; quiebres a 45° en planta, no en perfil.
- "¿Por qué mide 0.30 si la cuneta es 0.60?"; "ya no quiero la vista 3D de todo el terreno"; "no pongas bloque X"; "¿por qué dice
  31.45? hay errores de medida".
- Hidrología: "¿está bien que uses la misma estación Tarapoto?"; "¿por qué tan pocas páginas? ¿no tienes de los CAR el ejemplo?";
  "datos de 2017 no, mínimo 2025 o 2024"; "te paso mi formato de cálculos, hazlo así tal cual; también formato de metrados,
  análisis estadístico, especificaciones"; "ya no alteres planos, ya imprimí el último"; "así quiero el análisis estadístico"
  (plantilla del CAR Varones); "¿los cálculos de la memoria coinciden con el nuevo análisis?" → comprobador
  `coteja_analisis_b.py` (1696 valores, 0 diferencias).
- Carátulas: "en base a esta imagen hazme la carátula para todos los documentos"; "solo el archivo en un solo Word, solo las
  carátulas"; "no debe decir EXPEDIENTE TÉCNICO"; "índice y carátula de planos en un solo Word"; CAR Mujeres: "índice según el
  PDF último"; "carátulas… servicio para elaboración de expediente técnico, en un solo Word"; "más vacán con su foto"; "no tengo
  foto, ponle la planta".
- Red: el 21-10 el internet del entorno bloqueaba senamhi.gob.pe, power.larc.nasa.gov y data.chc.ucsb.edu (403) aunque el usuario
  "habilitó acceso total"; el cambio de red se aplica en una sesión nueva. Mientras tanto, el usuario entregó los datos
  (`insumos/barranquita/lluvia/`) y se leyeron con `lluvia_datos_b.py` sin modificar el diseño hasta su decisión.

### 22-10 y 23-10-2026 (Refugio y Varones: juego final de documentos)
- "Cuando me pasas el detalle de lloraderos en DXF se ve horrible" → sin patrones de achurado (rellenos sólidos con color
  verdadero, piedras una por una, "m3" en vez de "m³"), legible en AutoCAD con fondo negro o blanco; presentaciones A3 1:10.
- OC-01: "hazle su isométrico solo donde sale la montante y accesorios; borra esa cúpula; canaleta 0.21 × 0.18; solo dos
  sujetadores; el metrado solo de canaleta, tapas, sujetadores y boquilla"; "son 9 bancas, la obra complementaria trae 3, o sea 3
  juegos de 3".
- "Actualiza o crea la memoria descriptiva… dame índice de planos en un Word aparte; crea nuevamente la memoria hidrológica,
  descriptiva y especificaciones" (Refugio) y lo mismo para Varones con "los planos finales".
- "En el índice haces observaciones pero no tienen sentido: el PDF está ordenado por formato de hoja, primero A0… y no por
  número" → índice sin observaciones, siguiendo el documento del usuario.
- "En la hoja de lloraderos no veo el metrado del lloradero (piedra, tubos perforados de 3", geotextil)… ¿no lo hiciste?" →
  existe en DESAGREGADO LLORADEROS y ACU LLORADEROS; explicar dónde está.
- "Corrige las siglas del metrado solo donde van códigos de láminas por las nuevas que puse"; "excluí esos planos, no los vi
  necesarios"; "borra las referencias… mas no el metrado".
- "El índice ordénalo de la lámina uno a la última sucesivamente" (Varones).
- "Dame una carátula de cada uno en un Word separado… la foto del proyecto en cada carátula… y carátula de planos"; luego "todo en
  un solo Word, no separado"; "este es el logo del gobierno, el otro sale corto"; "son solo tildes, la fecha sí es setiembre, ya
  está bien".
- Refugio: "no pongas el que dice índice de planos, solo planos"; "en un solo Word"; "usa otro color diferente, por ejemplo
  verde"; "¿tienes las últimas especificaciones?"; "revisa si este índice coincide con los planos"; "aquí te dejo las láminas que
  imprimo" → el PDF que imprime el usuario manda.

### 24-10-2026 (memoria permanente)
- "¿Tienes de memoria todo el proceso de cargar datos de terreno, leer cotas y curvas, no salir del límite del terreno, y que si un
  techo tiene dos caídas va cuneta a cada lado?" → skill `planteamiento-cunetas-terreno`.
- "Quiero que recuerdes todo, todo, al mínimo detalle… una memoria que dure siempre… para poder diseñar un programa o
  implementarlo en mi drenaje" → esta base de conocimiento (`conocimiento/`).
- Programa DRENIE (rama `claude/programa-drenie`, carpeta `drenie_motor/`), reglas dadas por el usuario para el programa:
  - Visor tipo AutoCAD dentro del programa para marcar a mano lo que no se detecta (áreas, flechas de caída, cunetas, descargas);
    "toda cuneta enterrada está prohibida"; la marcación manual se hace en la computadora (en el celular solo se revisa).
  - Orden: lluvia (estación SENAMHI, análisis estadístico, IDF, I) → superficies → caudal de cada cuneta (techos, pisos y áreas
    verdes que le llegan) → dimensiones → planos, metrado y documentos; después montantes, canaletas y accesorios de techo.
  - Lloraderos: solo en el muro de la cuneta que está en contacto con área verde (el muro que da a vereda o piso no lleva); con
    ellos se drena el agua que se carga en el área verde y no se usan drenes franceses. Filtro: caja de 0.30 × 0.30 de grava
    envuelta en geotextil (para que no pasen limos) detrás del tubo PVC Ø 3" @ 1.50 m.
  - Dimensiones de cuneta: muros de 0.10 y losa (tapa) de 0.10 siempre por defecto; ancho libre y profundidad variables según el
    caudal, propuestos por el programa, con opción de que el proyectista proponga su dimensionamiento y el programa lo verifique.
    Todo debe ser constructivo: nada de cunetas de 0.20 × 0.20 que no se pueden encofrar ni acabar.

### 26-10 a 28-10-2026 (evacuación y señalización, PSST del CAR Mujeres, revisión de planos de arquitectura)
- Evacuación y señalización del CAR Varones (26-10): "para las señales sin símbolo en planta, metra con las cantidades de la
  leyenda del plano". Después: "dame lista de inconsistencias" → "no te estoy diciendo de Satélite, estoy diciéndote de
  señalización y evacuación" → responder sobre el tema que el usuario está tratando, no sobre otro trabajo del mismo chat.
  "Pásame eso en un Word entendible para entregarle a la arquitecta" → informe en Word sencillo para un tercero.
- Archivos (26-10): "pásame aquí todos los archivos, no lo copies en carpetas, dame aquí, yo descargo" (R30). Cuando el archivo
  del usuario está abierto en Excel no se puede escribir: avisar, esperar a que lo cierre ("ya cerré el Excel, copia los cambios
  a mi archivo") y aplicar los cambios sobre su versión guardada, con respaldo previo.
- Memoria de evacuación del Hogar de Refugio (26-10): "recuerda, esta memoria es de Refugio Mujeres Violentadas, CUI que termina
  en 14"; "varios dicen institución educativa… cambia todo, ya me autorizó la arquitecta, ponle todo según el proyecto" (R29). Se
  corrigió con control de cambios para que la arquitecta vea cada cambio.
- PSST (28-10): "no usa S10, usa Delphin" (R25); "¿por qué el Excel está protegido todo? me redondea decimales" (R28); "solo deben
  salir 78 obreros según las horas… esto manda"; "solo haz para el personal de la imagen, no metas más" (sin personal técnico ni
  visitas); "¿por qué dos por obrero? ¿quién dice eso?" (EPP uno por obrero, sin reposiciones supuestas); "¿de dónde sacaste estos
  insumos?… el ing. de presupuesto me preguntará de dónde saqué eso" (cada insumo con sustento); "solo algunas podrías aumentar, no
  todo, porque el ing. otra vez actualizará su presupuesto"; "borra eso que dice por mes en cantidad, conserva lo que dice jgo o
  und"; "no compraré esos dos, es muy caro solo para usar de vez en cuando, bórralos"; "no solo es colector, también las
  edificaciones, todo el proyecto en general" (las cantidades de protección colectiva se sustentan por frente de trabajo de toda la
  obra); "quita todo insumo nuevo, conserva solo los que ya están en el presupuesto y sus nuevos precios".
- Entidad (28-10): "no es el Proyecto Especial Huallaga… eso borra de todo, la entidad es la Gerencia Territorial Bajo Mayo, GTBM";
  "sigue saliendo PEHCBM, borra de todo referencia al proyecto Huallaga" (R24). Revisar también resaltados que queden en el Word
  ("¿por qué sigue resaltado de amarillo en el Word?").
- PDF de la memoria de cálculo del CAR Mujeres (28-10): "borra ese encabezado y pie de página que dice Wilma" → "lo hiciste mal,
  no era para que borres todo, solo eso donde salía la fecha… borraste el título" (R27): se borran solo las líneas pedidas y se
  compara el texto de todas las páginas con el original.
- Mensajes para terceros (28-10): "en un solo párrafo, tono amigable"; "no le preguntes, solo dile lo que necesitas".
- ACU suelto en Excel (28-10, panel de policarbonato del CAR Varones): todo con fórmulas como el Delphin (cuadrilla × 8 h ÷
  rendimiento, herramientas 5 % de la mano de obra, parciales a 2 decimales) y, si pide "precios reales en Perú", hoja de
  cotización con tienda, enlace, fecha y precio con IGV y sin IGV (÷ 1.18).
- Revisión de planos de arquitectura (28-10, I.E. 292 Satélite): el usuario dio acceso a su carpeta de DXF y pegó 14 indicaciones
  de revisión → skill `revision-planos-arquitectura`.

---

## 6. Técnicas de trabajo verificadas

### 6.1 Editar una planilla .xlsx por XML sin romper el formato
Problema aprendido el 03-10: abrir y guardar la planilla del usuario con openpyxl borra imágenes de encabezado (VML), puede
dejar hojas vacías al abrir en Excel y reescribe estilos. Solución: editar el XML del libro.

- Clase `Libro` en `herramientas/angulo_contramarco_refugio.py` (reutilizada por `varones/planilla_como_refugio.py`,
  `mujeres/bancas_en_planilla_m.py`, `bancas_oc01_en_planilla_refugio.py`, `varones/codigos_laminas_metrado_v.py`, etc.):
  - `Libro(f)`: lee el ZIP completo, `xl/sharedStrings.xml`, `xl/workbook.xml` y sus relaciones (mapa nombre de hoja → archivo).
  - `hoja(nom)`, `celda(nom, ref)`, `leer(nom, ref)` (resuelve textos compartidos).
  - `texto(nom, ref, t)` (agrega el texto a sharedStrings si no existe), `num(nom, ref, v)`,
    `formula(nom, ref, f)` (escribe `<f aca="false">…</f><v>0</v>`), `cambiar(nom, ref, viejo, nuevo)` (exige que el texto viejo
    exista: si no, falla en vez de escribir a ciegas).
  - `desplazar(nom, desde, hasta, d)`: baja filas y corrige referencias de la hoja, rangos `ref=` de fórmulas compartidas
    (`<f t="shared" …/>`, corregido el 19-10) y celdas combinadas; no toca referencias a otras hojas.
  - `insertar_copia(nom, origen, nueva)`: inserta una fila nueva copiando el formato de otra.
  - `guardar(f)`: reescribe sharedStrings (con `uniqueCount`) y las hojas tocadas, conservando el resto del ZIP byte a byte.
  - Conserva el atributo de estilo `s="…"` de cada celda: el formato no cambia.
- Para vaciar una celda conservando su estilo: `<c r="X" s="…"/>` (`vaciar` en `planilla_como_refugio.py`).
- Cuando se usa openpyxl para hojas nuevas (`metrado_xlsx.py`), al final se reinyectan las imágenes de encabezado con
  `metrado_xlsx.reinyectar_vml` y se respeta el orden de elementos de cada hoja (legacyDrawingHF después de rowBreaks).

### 6.2 Recalcular con LibreOffice y escribir los valores en caché
- `recalcular(f, hojas)` (`angulo_contramarco_refugio.py`): copia el libro quitando los `<v>` de las celdas con fórmula (para que
  LibreOffice calcule todo), lo convierte con `soffice --headless --convert-to xlsx`, lo lee con
  `openpyxl.load_workbook(data_only=True)` y escribe en el XML original solo los valores nuevos de las celdas con fórmula
  (número `t="n"` o texto `t="str"`), sin tocar estilos. Ignora errores (`#…`). Excel recalcula al abrir igual.
- Si la planilla guarda fórmulas sin valores (o los cuadros DXF necesitan leer valores), recalcular una copia temporal y leer de
  ahí (`varones/planilla_v.py`, con caché por md5 del libro).
- Después de recalcular, buscar celdas con error (`#`) en todo el libro.

### 6.3 Comparar antes y después (metrados)
- `metrado_xlsx.comparar(orig, nuevo, informe)`: celda por celda en todas las hojas originales; cuenta celdas con contenido y
  modificadas por hoja, lista hasta 20 diferencias, informa hojas nuevas y da "SIN CAMBIOS en el contenido original" o "N celdas
  originales cambiaron (revisar)" (`entregables/METRADO_COMPARACION_ANTES_DESPUES.txt`). Una celda `''` y una vacía cuentan igual.
- Comparar sobre los dos libros recalculados (valores, no fórmulas) cuando se desplazaron filas: comparar los totales del RESUMEN
  por código de partida.
- Reportar al usuario el resultado con números (ej. "760 valores iguales", "140 celdas de texto cambiadas, ningún valor numérico
  cambia").

### 6.4 Word: generar, renderizar y comprobar
- Generar con python-docx (memorias, carátulas, índices) o con `node docx_espec.js <json> <docx>` (especificaciones, desde
  `especificaciones/espec.py` → `_json/`).
- Verificar renderizando: `soffice --headless --convert-to pdf --outdir <tmp> <docx>` y `pdftoppm` a PNG para mirar las páginas
  (que cada carátula quepa en una página A4, tablas sin cortes raros, figuras visibles).
- Índice con números de página en dos pasadas: generar, convertir a PDF, buscar en qué página cae cada título
  (`paginas_pdf`) y volver a generar con esas páginas (`mujeres/memoria_descriptiva_m.py`).
- Figuras de láminas tomadas del PDF que imprime el usuario: `pdftoppm -f N -l N -singlefile -jpeg -scale-to 2200`
  (`memoria_descriptiva_refugio.py`) y recorte sin rótulo.
- Capítulo nuevo al final de un Word del usuario sin alterar las páginas anteriores (capítulo del colector en el estudio
  hidrológico, 03-10).
- Metadatos vacíos (autor, último que modificó, comentarios).

### 6.5 Comparar texto antes y después (documentos)
- Antes de entregar una corrección de citas o de una línea (códigos de lámina, "SERVICIO DE DISEÑO", fecha), extraer el texto del
  Word anterior y del nuevo y comprobar que **solo** cambian los párrafos esperados (ej. 23-10 especificaciones del Refugio: "solo
  cambian esos 2 párrafos, el resto del Word es idéntico"; 21-10 carátulas de Barranquita: "solo cambia esa línea").
- Para Word con XML idéntico salvo un parámetro (color de carátulas del Refugio), verificar que el del otro proyecto queda con XML
  idéntico (23-10: Varones sin cambio).
- Comprobadores automáticos de cifras entre documentos: `barranquita/coteja_analisis_b.py` compara cada valor de la memoria
  hidrológica (cuerpo y anexo) con la hoja del análisis estadístico a la precisión impresa (1696 valores, 0 diferencias).

### 6.6 DXF: huella, auditoría y vista previa
- Huella de láminas congeladas: tipo, capa, punto y texto de cada entidad dentro de la caja de la lámina, antes y después de
  regenerar; deben quedar idénticas (DP-06B y perfiles del Refugio; Varones al tocar módulos comunes).
- `doc.audit()` sin errores.
- Vista previa PNG: `python3 herramientas/dxf_render.py <dxf> <png> x0 y0 x1 y1 110 color`; cajas de cada lámina en
  `entregables/_calc/laminas.json` (Varones en `entregables_varones/_calc/`, Mujeres en `PLANOS_COLECTOR_MEJORADOS/laminas.json`,
  Barranquita en `entregables_barranquita/_calc/laminas.json`); renderizar en paralelo con `xargs -P 4`. Láminas sueltas en mm de
  papel: caja 0 0 841 594.
- Mirar SIEMPRE la vista previa antes de entregar (textos encimados, verticales, fuera del marco, llamadas cruzadas, cotas que no
  coinciden).
- Parametrizar módulos compartidos por proyecto con `compat.py` (textos fijos → parámetros con el valor anterior por defecto).

### 6.7 Lecturas sin modificar
- Índices de planos que leen el PDF del usuario sin modificarlo (formato del papel, título y escala del rótulo, secciones y
  progresivas que distinguen láminas de igual título) y comprueban cada título contra el rótulo
  (`mujeres/indice_planos_m.py`, `indice_planos_refugio.py`, `varones/indice_planos_v.py`; Barranquita lee el DXF impreso).
- Plantillas del usuario abiertas con LibreOffice UNO cuando hay gráficos (análisis estadístico de Barranquita desde la plantilla
  del CAR Varones: carga la serie, borra filas sobrantes y LibreOffice ajusta fórmulas y gráficos).

### 6.8 Git y continuidad entre sesiones
- Rama de trabajo: `claude/colector-pluvial-hogar-refugio-ydbnaf`. Commit con mensaje claro en español (prefijo del proyecto:
  "Hogar de Refugio: …", "CAR Varones: …", "Barranquita: …") y `git push -u origin claude/colector-pluvial-hogar-refugio-ydbnaf`.
  No crear PR salvo pedido. Lo que no se sube no aparece en el panel del usuario (17-10: "no veo la carpeta").
- No versionar archivos enormes ni cachés (`*.pkl`, `entregables/_tmp/`, `herramientas/especificaciones/_json/`, renders de
  trabajo de `render_tapa`).
- Continuidad: `CLAUDE.md` (reglas y mapa del repositorio, se lee completo al empezar), `BITACORA_CONVERSACION.md` (decisiones
  fechadas por proyecto; agregar una sección por cada pedido), skills de `.claude/skills/` (criterios técnicos) y esta base
  `conocimiento/`. Si algo no cubre ninguna regla, no inventar: presentar opciones, recomendar una y, una vez decidida, escribirla
  como regla en el skill correspondiente.

---

## 7. Lista de comprobación antes de entregar
1. ¿Está todo en español, sin rastros de IA, sin nombres de personas ni CIP, con metadatos vacíos?
2. ¿El proyecto se cita por nombre y CUI (o C.I.)? ¿Ninguna cita a láminas o partidas de otro proyecto?
3. ¿Se dice "cota de fondo"? ¿Los términos son los del usuario?
4. ¿Escala real comprobada con 3 o 4 cotas? ¿Vista previa PNG revisada?
5. ¿Metrado del usuario intacto salvo lo pedido? ¿Comparación antes/después hecha y con resultado numérico?
6. ¿Nombres y estructura Delphin; cantidades propias?
7. ¿Coherencia propagada a metrado, ACU, desagregados, láminas, especificaciones, memorias, índice y carátulas?
8. ¿Láminas congeladas / planos impresos sin regenerar (huella idéntica)?
9. ¿Precios con fuente y MO CAPECO-FTCCP 2026?
10. ¿Se informó el impacto en el metrado y en los proyectos vecinos?
11. ¿Se entregaron todos los archivos afectados (Word, Excel, DXF, PNG) y se actualizó la bitácora?
12. ¿Commit y push en la rama de trabajo?
13. ¿Nombre, CUI, ubicación y entidad (GTBM, nunca PEHCBM) son los del proyecto, sin textos que queden de otro proyecto?
14. ¿Los datos usados (horas-hombre, insumos, precios) son del mismo proyecto del archivo que se entrega?

---

## 8. Para implementarlo en un programa

El usuario quiere un programa propio (su software de drenaje) que haga el trabajo sin depender de la IA, incluidas las
decisiones de criterio y la revisión de legibilidad de los planos (16-10). Estas son las reglas de esta sección que se pueden
volver datos, validaciones automáticas y salidas.

### 8.1 Datos de entrada por proyecto (ficha del proyecto)
| Campo | Ejemplo | Uso |
|---|---|---|
| nombre_oficial | "CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL…" | carátulas, rótulos, encabezados |
| nombre_corto | "CAR Varones" | textos del cuerpo |
| codigo_tipo / codigo | "CUI" / "2705619" (o "C.I." / "468901") | toda cita del proyecto |
| entidad / gerencia | "GOBIERNO REGIONAL SAN MARTÍN" / "GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO" | carátulas y rótulo |
| linea_servicio | "SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL EXPEDIENTE TÉCNICO DE PI:" o "SERVICIO DE DISEÑO - DRENAJE PLUVIAL" | carátulas |
| especialidad | "ESPECIALIDAD DE DRENAJE PLUVIAL" | carátulas y rótulo |
| ubicacion | "Predio rural Los Mangos, distrito de Morales…" | carátulas, memorias |
| fecha | "SETIEMBRE - 2026" | carátulas (igual a la de los rótulos del juego final) |
| color_caratula | 7B1E2B / 1E5E3B / 1F3A68 | carátulas |
| foto, logo | rutas en `insumos/` | carátulas |
| proyectista | vacío siempre | firma en blanco |
| metrado_vigente | ruta del Excel del usuario | única fuente de cantidades |
| congelado | sí / no (CAR Mujeres: sí) | bloquea escritura en metrado |
| juego_laminas | lista código → título → formato → escala, leída del PDF que imprime el usuario | índices y citas |
| orden_indice | "numero" o "pdf" (por formato) | índice |
| laminas_excluidas | ej. DP-08, DA-01 a DA-03 (Varones) | borrar referencias, no reemplazar |
| impresos | sí / no | bloquea regenerar planos |
| vecinos | aguas arriba (aporte externo: Q, cota de fondo, NA, ventana) y aguas abajo (receptor: cota de fondo mínima, Q máximo, alto interior) | empalmes y textos |
| tiene_cerco_frente, lados_con_junta | Varones: no; Refugio: un lado | juntas y textos |
| zonas_carga | peatonal / motos / camión con progresivas y holgura | estructura y registros |
| mano_obra | tabla CAPECO-FTCCP del año (28.95 / 22.68 / 20.54 en 2026) con su expediente | ACU |
| precios | insumo, unidad, precio sin IGV, fuente, fecha | ACU |
| estructura_partidas | catálogo Delphin base (CAR Mujeres): código, nombre, unidad | metrado |

### 8.2 Validaciones automáticas (bloqueantes)
1. **Idioma**: ningún texto de salida con palabras en inglés de una lista negra (p. ej. "invert", "check", "flow") ni frases
   típicas de asistente; marcar "completar", "insertar", "[", "TODO", "XXX".
2. **Sin personas**: ninguna salida contiene nombres de la lista de personas (responsables, profesionales) ni "CIP"; el campo
   proyectista vacío; metadatos de Word vacíos.
3. **Cita de proyectos**: cada mención de un proyecto vecino va con su nombre y código; prohibido citar por persona.
4. **Terminología**: reemplazar o rechazar "invert" → "cota de fondo"; "nudo" → "quiebre"; unidad "ml" → "m" donde Delphin usa m.
5. **Escala real**: para cada lámina, comparar medidas de entidades clave (espesor de losa, ancho de cuneta, diámetro de barras,
   longitudes de guitarra) con los valores de diseño; tolerancia 1 mm; error si una cota DIMENSION tiene texto fijo distinto de
   su medida.
6. **Metrado intacto**: tras cualquier escritura, recalcular y comparar celda por celda con el original; solo pueden cambiar las
   celdas de la lista de cambios autorizados; si el proyecto está congelado, no se escribe nada.
7. **Sin mezcla de partidas**: una partida nueva solo crea filas y hojas nuevas; no suma en partidas existentes; ningún código ni
   lámina de otro proyecto en el libro o documento.
8. **Coherencia**: cada cantidad citada en láminas (cuadros DA), especificaciones, memorias y ACU se lee del metrado vigente y se
   compara (tolerancia de redondeo impreso); cada código de lámina citado existe en el juego final del proyecto; cifras de memoria
   ↔ análisis estadístico (cotejo valor por valor).
9. **Empalmes entre proyectos**: cota de fondo de llegada ≥ cota de fondo del receptor; caudal entregado ≤ caudal de diseño del
   receptor; nivel de agua que llega ≈ nivel de agua inicial del receptor; ventana de salida con el ancho y el alto interior del
   receptor; caída libre sobre el nivel de agua en las llegadas.
10. **Láminas congeladas e impresas**: huella de entidades idéntica; si `impresos = sí`, el generador de planos no corre y el
    programa lista los textos de planos que quedaron desactualizados.
11. **Precios**: todo insumo de ACU con precio > 0, fuente no vacía y fecha; MO tomada de la tabla del año vigente.
12. **Legibilidad de planos**: sin textos rotados 90° salvo cotas verticales; sin cajas de texto superpuestas (holgura 2 mm en
    papel); todo dentro del marco y fuera del rótulo; sin color amarillo ni blanco puro en líneas; rellenos con color explícito
    (no negro por defecto) y al fondo; sin patrones de achurado que dependan de la escala del bloque.
13. **Gestión de riesgos**: ningún monto en soles (regex "S/" y cifras monetarias) y ninguna sección de observaciones; efectos en
    % del presupuesto.
14. **PSST**: matriz IPERC en Excel con fórmulas y Word con tablas y gráficos; residual de todo peligro en moderado o menos.

### 8.3 Validaciones que avisan (no bloquean) y piden decisión
- Dato faltante: listar qué no se pudo leer del DXF o de los documentos, con la hipótesis propuesta (nunca inventar en silencio).
- Diferencias en el plano de origen (cota rotulada distinta de la dibujada, códigos repetidos en rótulos): informar al usuario y
  no corregir su documento.
- Cambio que altera el metrado: mostrar el antes y el después por partida y pedir confirmación.
- Cambio que afecta al proyecto vecino: indicar qué documentos del vecino cambiarían.
- Elemento de diseño en una zona de carga distinta (ej. tapa de registro dentro del cruce de camiones): avisar.

### 8.4 Salidas por proyecto
| Salida | Formato | Origen |
|---|---|---|
| Juego de planos con presentaciones e índice | DXF (A0 a A3 según dibujo) + PNG por lámina | generadores de planos |
| Metrado | la planilla del usuario con hojas nuevas (formato y colores del usuario, fórmulas en español al abrir) | metrado vigente + cálculo |
| ACU, desagregados, costo hora-hombre | hojas dentro de la planilla (o Excel aparte si se pide) | precios + MO + cantidades |
| Memoria de cálculo | Excel con fórmulas (y PDF solo si se pide) | diseño |
| Memoria hidrológica, memoria descriptiva, especificaciones | Word | diseño + metrado + juego de láminas |
| Índice de planos y carátulas | Word (todo en uno cuando se pide) | ficha + juego de láminas |
| Informe de verificación | texto o Excel: comparaciones antes/después, cotejo de cifras, huellas, comprobaciones de diseño | validaciones |
| Bitácora | entrada fechada con qué se hizo, qué cambió y qué quedó pendiente | cada ejecución |

### 8.5 Reglas de orden de trabajo para el programa
1. Cargar la ficha y el metrado vigente; si el proyecto está congelado, modo solo lectura del metrado.
2. Mostrar lo leído (cuadro de control) y esperar confirmación antes de cambios grandes.
3. Calcular y dibujar; correr todas las validaciones; repetir hasta que las bloqueantes pasen.
4. Escribir el metrado por XML (sin perder formato), recalcular y comparar.
5. Propagar a documentos; cotejar cifras y citas.
6. Entregar todos los archivos afectados y el informe de verificación; registrar en la bitácora.
