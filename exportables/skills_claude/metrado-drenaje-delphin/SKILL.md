---
name: metrado-drenaje-delphin
description: "Metrar el drenaje pluvial de cualquier proyecto (cunetas, colector, canaletas, montantes, falsas columnas, sumideros, rejillas, juntas, tapas, lloraderos, techos de bancas u otros componentes) en la planilla Excel del usuario, con partidas de nombre y estructura Delphin: RESUMEN, PLANILLA GENERAL y hojas de detalle por componente, sustento por lámina con los códigos del juego del cliente, cotejo antes y después y edición del Excel sin romper el formato (XML y recálculo con LibreOffice). ACU y precios con fuente solo a pedido. Usar cuando se pida metrar, agregar o corregir una partida de drenaje, revisar un metrado, armar desagregados o actualizar la planilla tras un cambio de diseño, en colegios, establecimientos de salud, locales municipales, albergues u otras edificaciones."
---

# Metrado de drenaje pluvial en la planilla Delphin del usuario

Método general para cualquier edificación (colegio, posta o centro de salud, municipalidad, albergue, mercado, vivienda
multifamiliar). Todas las dimensiones, cantidades, códigos y precios salen del proyecto nuevo; los valores de proyectos
anteriores están solo en el apartado final **"Ejemplo de referencia"** y se reemplazan. Detalle en
`referencias/06_metrado_acu_especificaciones.md` y `referencias/07_componentes_complementarios.md`: describen proyectos ya
trabajados y sus rutas de archivo no existen en este chat; usarlos como ejemplos del método, nunca como datos.

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

## 1. Principios del metrado (criterios generales del usuario)
1. Trabajar sobre **su** archivo y su formato; nunca borrar ni rehacer hojas suyas. Lo nuevo va en hojas o filas nuevas con su estilo.
2. No mezclar partidas sumando una en otra. Cada obra principal (colector, canal, cámara) es partida aparte; lo que ya metró el
   usuario (p. ej. cunetas) no se vuelve a metrar en otra partida.
3. Estructura y nombres de partidas = estilo Delphin de la base que indique el usuario; **cantidades siempre del metrado propio**.
   Solo se reutiliza un nombre si la obra es la misma; si cambia dimensión, material, espesor o unidad, se consulta.
4. Proyecto congelado (ya presupuestado): solo se agrega lo pedido y todo lo demás queda idéntico.
5. Cada fila con su sustento: código de lámina **tal cual el rótulo del juego del cliente** y criterio. Si el usuario excluyó una
   lámina de su juego, se borra la cita y no se toca el valor.
6. Rellenos menores (base de un emboquillado) van dentro de la partida de relleno. Arreglar planos no cambia el metrado.
7. Un desagregado o ACU coincide con los planos (cantidades por unidad tomadas de la lámina de detalle). Cambiar la unidad para
   valorizar (glb → m o und) solo en el libro de ACU; vale el metrado original.
8. No inventar lo que no está en el plano (montantes, sumideros, dados, tapas, descuentos de rejilla): pedirlo y listarlo como
   pendiente. No preguntar lo que el plano ya muestra (accesos vehiculares, cerco, áreas verdes).
9. **Por defecto el trabajo llega hasta el metrado**: no proponer ACU, precios ni presupuesto si no los pide. El presupuesto lo hace
   el ingeniero en el programa que use (Delphin por defecto; no proponer exportar a otro programa sin pedido).
10. Antes de usar datos (horas-hombre, insumos, metrados, precios) confirmar de qué proyecto son; nunca meter datos de una obra en el
   archivo de otra.
11. Excel que se entrega: sin hojas protegidas, con los decimales completos a la vista y todo con fórmulas.

## 2. Insumos y datos que hay que pedir (lista completa)
| Grupo | Qué pedir | Para qué |
|---|---|---|
| Proyecto | Nombre completo tal cual el rótulo, CUI o código, entidad, ubicación, fecha; si el metrado está congelado | encabezados, RESUMEN |
| Planilla | Metrado vigente (.xlsx) o la plantilla a usar; confirmar cuál es la versión vigente | base de trabajo |
| Partidas | Árbol Delphin de referencia (presupuesto o COMPARATIVO del cliente) e ítem donde cuelga la especialidad | códigos y nombres |
| Planos | DXF de planta, perfiles, secciones y detalles; PDF del juego que imprime el cliente con sus códigos finales | medidas y sustento |
| Diseño | Ejes, longitudes, progresivas, NCT y cota de fondo por sección, ancho libre por eje, tramos abiertos y tapados | fórmulas |
| Criterios | Espesores (muro, losa, tapa), f'c por elemento, altura mínima con acero, separación de juntas, franja de trabajo, solado, esponjamiento, recubrimientos | confirmar o cambiar los valores por defecto |
| No dibujado | Tapas en tramos tapados, montantes por edificación y lado, red de piso, dados, descuentos de rejilla (puertas, cruces), lados de la junta cuneta-piso, cunetas junto a área verde (lloraderos), tarrajeo interior, cruces vehiculares | partidas que el plano no define |
| Alcance | ¿Solo metrado? (por defecto sí). Si pide ACU: tabla de mano de obra vigente y ciudad para los precios | evitar trabajo no pedido |
| Juego | Láminas excluidas por el usuario y equivalencia entre códigos de trabajo y códigos finales | citas correctas |

## 3. Estructura de partidas (formato general Delphin)
- Título de la especialidad → TRABAJOS PRELIMINARES (limpieza manual de terreno m², trazo, niveles y replanteo preliminar m²) →
  MOVIMIENTO DE TIERRAS (excavación manual de zanjas p/cunetas m³, p/dados m³, refine, nivelación y compactación m², relleno
  compactado c/material propio seleccionado m³, eliminación de material excedente m³) → CONCRETO SIMPLE (solado, dados) → CONCRETO
  ARMADO (por elemento: concreto m³, encofrado y desencofrado m², acero kg, curado m²) → VARIOS (rejilla metálica m, tapa de inspección
  und, junta de dilatación m, lloradero und) → RED DE COLECCIÓN (techo: montante, falsa columna, canaleta, soporte, tapa lateral,
  boquilla; piso: tubería, sumidero, codos, tees; accesorios) → componentes propios del proyecto (bancas, cajas, pozos).
- Obra principal aparte (p. ej. COLECTOR PLUVIAL): preliminares, movimiento de tierras, solado, concreto en **una sola partida**,
  encofrado, acero, acabado, curado, tapa de registro (und con desagregado), juntas.
- Nombres con el material y la medida al estilo Delphin ("CONCRETO f'c=<valor> kg/cm2 PARA CUNETAS", "TAPA DE INSPECCION <a>m x <b>m");
  códigos según el árbol del proyecto; no renumerar los huecos de la base. Unidades: m, m², m³, kg, und ("ml" → "m", "Kgr" → kg).

## 4. Hojas y formato de la planilla (formato por defecto del usuario; si trae su planilla, manda la suya)
- Orden: RESUMEN · PLANILLA GENERAL DE METRADOS · hojas de detalle (concreto, encofrado, montantes, piso/sumideros, canaletas,
  acero, curado, rejillas, juntas, lloraderos, tapas) · PARAMETROS · Listas · hojas de la obra principal (parámetros, movimiento de
  tierras, concreto, encofrado, acero, registros y tapas, juntas, insumos) · mano de obra · ACU · desagregados. Respetar los nombres
  de hoja exactos del usuario (incluidos espacios dobles).
- RESUMEN: Item · Descripción · Unid. · Total (fórmula a la columna TOTAL de la PLANILLA). Entidad, nombre del proyecto con CUI,
  ubicación y fecha en celdas propias que las demás hojas leen con `=+RESUMEN!B4`… (se cambian en un solo lugar).
- PLANILLA GENERAL: ITEM · DESCRIPCION · Nº DE VECES · LARGO · ANCHO · ALTURA · FACT. · AREA · VOLUMEN · PARCIAL · TOTAL · UND. Fila de
  partida con TOTAL = SUMA de sus parciales; filas de sustento por eje o tramo con PARCIAL = producto o enlace a la hoja de detalle.
- Formato por defecto: dato amarillo claro, fórmula verde claro, unidad gris, total naranja, cabeceras azules con letra blanca;
  Arial Narrow. Fórmulas visibles (nunca valores fijos); Excel en español (REDONDEAR, SUMA, SI, separador ";").
- PARAMETROS: todas las medidas del proyecto como datos editables (dimensiones de tapa, recubrimiento, separaciones, peso por metro,
  largo de barra, solado, esponjamiento). Listas: pesos nominales kg/m (6 mm 0.222; 8 mm 0.395; 3/8" 0.56; 12 mm 0.888; 1/2" 0.994;
  5/8" 1.552; 3/4" 2.235; 1" 3.973), tipos ABIERTA/TAPADA, conteo TEÓRICO (L/s + 1) o ENTERO (redondeo arriba + 1).

## 5. Cunetas: fórmulas en función de la sección del proyecto
Símbolos: b ancho libre del eje, e_m muro, e_l losa de fondo, e_t tapa, B = b + 2·e_m, e_s solado, F franja de trabajo, H altura
del NCT (borde) a la cota de fondo. Valores por defecto en el ejemplo final (criterio por defecto del usuario; confirmar en cada proyecto).
- H(x) interpolada entre secciones, en abierta y en tapada; área de muro = ∫H dx. Si un NCF no cierra con la pendiente, avisar.
- Concreto: muros ∫H dx × e_m × 2; losa L × B × e_l; tapa L_tapado × B × e_t.
- Encofrado (una cara, cant. 2): abierta externo (H + e_l)·L, interno H·L; tapada externo (H + e_l + e_t)·L, interno H·L + fondo de
  tapa L_tapado × b.
- Curado por tramo: 2·L·H_prom + L·b (+ L·b si TAPADA); 3 o 4 caras.
- Acero (regla por defecto: **solo donde H ≥ altura mínima con acero; todo tramo tapado lleva acero** aunque H sea menor); un tramo
  que pasa la altura mínima se metra desde la progresiva donde la alcanza. Longitudinal: barras = REDONDEAR.MAS((B + 2H)/sep) con la
  separación del plano según H; transversal U de desarrollo B + 2(H + gancho), cantidad L/sep + 1; barras de tapa de largo
  B − 2·recubrimiento. Hoja con una fila por tramo (Ø, factor BUSCARV, longitudinal, transversal, tapa, total del tramo).
- Planilla por eje: limpieza y trazo L × F; excavación L × F × (H_prom + e_l + e_s); refine y solado L × B; relleno
  L × (F − B) × (H_prom + e_l + e_s); eliminación (exc − rell) × esponjamiento; dados con su volumen unitario del plano.
- Rejilla: longitud = tramo ABIERTO − descuentos a mano (puertas, cruces); tapados sin rejilla. Peso por metro del despiece del detalle.
- Junta de cunetas (por defecto EG-2013 MTC, Sección 510): a la separación del proyecto y en cambios de dirección, **en toda la U**
  (2 muros + fondo): H_med = área de muro/L; N = REDONDEAR.MAS(L/sep); longitud = N × (2·H_med + b). Relleno y sellador según el detalle.
- Tapa de inspección (tramos tapados): concreto, encofrado y acero por unidad desde su detalle. Ubicación por defecto: inicio y fin de
  cada tapado, en cada empalme y a la distancia máxima que fije el proyecto.
- Lloraderos (solo en muros cuya franja exterior cae sobre área verde; cada lado aparte): N = REDONDEAR.MAS(L/sep). Hoja de
  lloraderos (N°, eje, progresivas, lado, longitud, separación, und, TOTAL) + DESAGREGADO por lloradero desde su detalle (tubo,
  perforaciones, excavación, grava, geotextil, mortero) y control `=SI(ABS(E−F)<0.001;"CONFORME";"REVISAR")` contra el RESUMEN.
- Cunetas que llegan a una obra principal: se metran hasta la cara del muro (acortar lo que invade; prolongar lo que no llega) y se
  documenta en una hoja de llegada (longitud dibujada, ajuste, longitud metrada, termina en, sustento).
- **Ancho variable por eje**: cada eje con su b (una medida por sector) en una columna de la planilla; las fórmulas usan b y B del eje.
- Con lloraderos no se metran drenes franceses ni subdrén salvo que el proyecto los tenga.
- Tarrajeo interior (si el proyecto lo lleva): hoja propia con muros y fondo de cunetas con rejilla y tapadas, en su partida.
- Junta cuneta-piso: confirmar a qué lados va (contra qué pisos) antes de metrarla; no asumir ambos lados.
- Partidas solo si el diseño las tiene: losa vehicular de cuneta tapada, caída corta, caja de caída, pase por muro, pozos de absorción,
  cámara de bombeo.

## 6. Red de techo, piso y bancas
- Canaletas (una por borde bajo de techo; dos aguas = dos): por edificación y lado, N° × L; soportes = SI(L>0; REDONDEAR.MAS(L/sep)+1;
  0) con la separación del detalle; 2 tapas laterales por canaleta; boquillas = montantes del lado.
- Montantes: m por edificación con el diámetro del plano; codos, colgadores y abrazaderas según el detalle (si el usuario ya tiene su
  regla de conteo en la planilla, se respeta aunque la especificación diga otra separación).
- Falsa columna y dado: concreto, encofrado y acero por unidad desde su detalle (und = montantes, sin pago propio si así está la base).
- Alcance por defecto cuando el metrado sale del diseño de la red: canaletas, soportes, tapas laterales, boquillas, falsa columna,
  dados y, por montante, el codo del dado y el tubo embebido hasta la cuneta. Altura del montante, desvíos, colgadores y abrazaderas
  los define el proyectista con los cortes de arquitectura; rejillas, tramos tapados y áreas verdes los confirma él.
- Conteos grandes (soportes, abrazaderas): mostrarlos por edificación y lado y pedir confirmación antes de entregar.
- Sumideros solo en áreas libres pavimentadas sin cobertura (patio, maniobra, estacionamiento), con su tubo a la cuneta.
- Red de piso por sector: tubería (m), sumideros, codos de 90° y 45° (distinguirlos de los del techo por el código), tees.
- Techos de bancas u otros elementos menores: solo los ítems que pida el usuario; lo ya metrado en otra hoja no se repite. Si falta en
  el RESUMEN una partida que el plano sí tiene, agregarla con aviso.

## 7. Obra principal y tapa de registro (fórmulas en el skill `colector-pluvial-frontal`)
Hojas con fila "Criterio:" al inicio y una fila por tramo homogéneo; concreto en una sola partida con subtítulos (losa de fondo,
muros, losa superior); tapa de registro por und con hoja DESAGREGADO (ubicación y componentes por registro desde su detalle; control
CONFORME con tolerancia); juntas de dilatación = ENTERO(L/sep) × perímetro; longitudinal solo contra cerco o estructura existente.

## 8. ACU (solo a pedido; formato Delphin)
- Encabezado: Partida (código y nombre Delphin) · Partida del metrado · Unidad · Metrado (fórmula a la planilla) · Rendimiento. Tabla:
  N° · RECURSO · UND · CUADRILLA · CANTIDAD · PRECIO S/ · PARCIAL S/ · FUENTE DEL PRECIO; grupos MANO DE OBRA, MATERIALES, EQUIPOS con
  subtotales; CU = MO + MAT + EQ; costo = CU × metrado. Cantidad MO (hh) = cuadrilla × 8 / rendimiento; herramientas como % de la MO
  según la base del usuario. Precio sin IGV = publicado / contenido / 1.18.
- Hoja de costo de hora-hombre con la tabla **vigente** que indique el usuario (CAPECO-FTCCP del año y régimen correspondiente):
  básico, leyes sociales, BUC, bonificaciones y total por día → S/ por hh de operario, oficial y peón. Todas las ACU enlazan a esa hoja.
- Ratios por unidad (aporte de materiales, rendimientos, horas-máquina) como dato editable, tomados de la base del usuario o de
  la norma de rendimientos que indique; nunca de memoria.

## 9. Precios con fuente (solo a pedido)
Cada insumo con producto, presentación, precio publicado con IGV, contenido, precio sin IGV, tienda, enlace, fecha de búsqueda y estado
(verde comprobado, naranja referencia de otra ciudad, rojo sin precio publicado / "por cotizar en <ciudad>"). Preferir proveedor de la
región del proyecto o cadenas con tienda en ella. Nota en las ACU: "Precios sin IGV obtenidos de precios publicados, con su fuente; los
marcados por cotizar deben confirmarse".

## 10. Editar la planilla sin romper el formato
openpyxl al guardar pierde logos del encabezado, estilos y fórmulas compartidas: **usarlo solo para leer** (`data_only=True`) o para
libros nuevos. Para editar el archivo del usuario:
1. Abrir el .xlsx como zip; mapear hoja → `xl/worksheets/sheetN.xml` con `workbook.xml` y sus `.rels`; textos en `sharedStrings.xml`.
2. Cambiar celdas en el XML conservando el atributo de estilo `s`: texto (`t="s"` al índice del string compartido, agregándolo y
   actualizando `uniqueCount`), número (`<v>`), fórmula (`<f>` en inglés con "," y `<v>` vacío). Assert del valor viejo antes de reemplazar.
3. Para insertar filas: desplazar el bloque y corregir referencias de la misma hoja en fórmulas, en el `ref` de las fórmulas
   compartidas (`<f t="shared" ref=…>`) y en `mergeCell`. Hoja nueva: agregar su XML, la entrada en `workbook.xml`, la relación y el
   Override en `[Content_Types].xml`, clonando estilos de una hoja existente.
4. Recalcular: copia sin los `<v>` de las fórmulas → `soffice --headless --convert-to xlsx` → leer valores → escribir esos valores en
   caché en el XML original sin tocar las fórmulas. Si el entorno no tiene LibreOffice, decirlo y entregar con aviso de recalcular.
5. Buscar errores `#REF!`, `#VALUE!`, `#DIV/0!` y revisar que los logos (`legacyDrawingHF`) sigan en su lugar.

## 11. Cotejo antes y después (obligatorio)
Leer todas las celdas con contenido de todas las hojas del original y de la versión nueva (ambas recalculadas) y listar las diferencias:
deben ser **solo** las pedidas (informe tipo "celdas originales N, modificadas 0, hojas nuevas …, SIN CAMBIOS en el contenido original";
con filas insertadas, comprobar que lo demás solo bajó de fila). Mostrar al usuario la tabla por eje y los totales del RESUMEN.

## 12. Especificaciones técnicas ligadas al metrado
Una por partida del RESUMEN (mismo código, nombre, unidad y orden; títulos sin unidad no llevan medición): DESCRIPCIÓN, MATERIALES,
EQUIPOS Y HERRAMIENTAS, PROCEDIMIENTO DE EJECUCIÓN, CONTROL DE CALIDAD Y TOLERANCIAS, SEGURIDAD Y SALUD EN EL TRABAJO, UNIDAD DE MEDIDA,
MÉTODO DE MEDICIÓN, FORMA DE PAGO. Detalle en el skill `memorias-especificaciones-tecnicas`. Láminas con los códigos del cliente.

## 13. Lista de verificación final
- [ ] Ningún valor del usuario cambió fuera de lo pedido (cotejo); sin errores `#`; logos y estilos intactos.
- [ ] Nombres Delphin y unidades correctas; partidas sin mezclar; obra principal aparte; nada de otro proyecto.
- [ ] Dimensiones, f'c, separaciones y reglas de acero = las del proyecto (no las del ejemplo); confirmadas las que se tomaron por defecto.
- [ ] Desagregados = hoja fuente = RESUMEN ("CONFORME"); si hay ACU, enlazadas a la hoja de mano de obra vigente y a precios con fuente.
- [ ] Mismas cantidades (registros, juntas, tapas, longitudes) en metrado, planos (cuadros leen la planilla), especificaciones y memoria.
- [ ] Citas de lámina existentes en el juego del cliente; pendientes y datos no disponibles listados aparte.
- [ ] Cada eje con su ancho libre; cantidades iguales a las del diseño (concreto, acero, rejilla, tapas, juntas, lloraderos, montantes).
- [ ] Nombre, CUI, ubicación y entidad del proyecto del archivo; datos (horas-hombre, insumos, precios) solo de ese proyecto.
- [ ] Sin hojas protegidas, decimales completos; sin errores de fórmula tras recalcular.
- [ ] Ni ACU, ni precios, ni presupuesto si el usuario no los pidió.

## 14. Errores que el usuario ya corrigió (lecciones generales)
- Borrar o rehacer hojas del usuario al integrar un componente nuevo.
- Volver a metrar dentro de otra partida lo que el usuario ya había metrado (prolongaciones, "empalmes").
- Abrir una partida por cada componente de un elemento que Delphin trata como una und con desagregado y ACU.
- Partir en varias partidas un concreto que la base tiene como una sola.
- Junta solo en los muros cuando debe ir en toda la sección (la losa amarrada se fisura).
- Juntas a lados donde no hay estructura (solo contra cerco o estructura existente) o con un material distinto del detalle.
- Precios "de mercado" sin fuente o mano de obra de una tabla no oficial o vencida.
- Elementos de carga vehicular donde solo hay paso peatonal ("tú tienes el plano, sabes por dónde entran vehículos").
- Agregar ítems que el usuario no pidió o que ya estaban metrados en otra hoja.
- Buscar un material en la hoja equivocada: explicar dónde está (desagregado) en vez de duplicarlo.
- Reemplazar citas de láminas excluidas por otras: se borra la cita y el valor no se toca.
- Confundir el ancho de zanja o franja de trabajo con el ancho de la obra.
- Usar sin avisar un rótulo de cota de fondo que no cierra con la pendiente.
- Proponer presupuesto con ACU cuando el alcance era solo metrado.
- Entregar el Excel protegido o con decimales redondeados.
- Poner horas-hombre o insumos de una obra en el archivo de otra.
- Entregar conteos muy grandes sin revisarlos antes con el usuario.

## Ejemplo de referencia (valores de proyectos anteriores; reemplazar por los del proyecto nuevo)
Proyectos de donde salió el método: CAR Varones (CUI 2705619), Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514),
CAR Mujeres (CUI 2717013; metrado congelado) e I.E. N.° 0590 Barranquita (C.I. 468901). Base Delphin usada: la del CAR Mujeres.
- Árbol: 01.04.03 SISTEMA DE DRENAJE PLUVIAL (.01 preliminares, .02 movimiento de tierras, .03 concreto simple, .04 concreto armado
  con .04.02 CUNETAS y .04.03 VARIOS, .05 red de colección: .05.01 techo, .05.02 piso, .05.03 accesorios) y 01.04.04 COLECTOR PLUVIAL
  FRONTAL. Nombres: "CONCRETO f'c=175 kg/cm2 PARA CUNETAS", "TAPA DE INSPECCION 0.60m x 0.60m", "REJILLA METALICA P/CUNETA C/PL 1''x
  3/16'' Y ANGULO 1'' x 1'' x 3/16'', S/DETALLE", "TAPA DE REGISTRO CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08".
- Cunetas: b 0.40 (variable 0.30–0.40 de 5 en 5 cm), e_m 0.10, e_l 0.10, e_t 0.10, B 0.60, S 0.5 %, solado 0.10, F 1.40,
  esponjamiento 1.20; acero solo con H ≥ 0.40 o tapada; longitudinal 3/8" @0.20 (H < 0.45), @0.22 (< 0.60), @0.25; U @0.25 con
  gancho 0.05; barra de tapa 0.56 @0.25; dados 0.40 × 0.35 × 0.40 = 0.056 m³.
- Rejilla: módulo 1.00 m, 2 ángulos L 1" × 1" × 3/16" + 39 platinas 1" × 3/16" @1" = 20.0 kg/m. Junta @3.00 m con tecnopor 1" y
  sellador asfáltico 1" × 2". Tapa de inspección 0.60 × 0.60 × 0.10: 0.036 m³, 0.60 m², 3.08 kg. Tapas a ≤ 10 m.
- Lloradero @1.50 m: tubo PVC 3" 0.30 m, 8 perforaciones 3/8", excavación 0.027 m³, grava 0.0297 m³, geotextil 0.594 m², mortero
  0.0005 m³. Falsa columna 0.20 × 0.15 × 1.30: 0.039 m³, 0.65 m², 5.6112 kg; dado 0.40 × 0.40 × 0.35. Soportes de canaleta @0.60;
  abrazaderas MAX(1; REDONDEAR.MENOS(L/4)); montantes PVC 4", 3 codos por montante, tubo del dado ≤ 5 m al 1 %.
- Tapa de registro del colector por und: 0.0370 m³, 0.2176 m², parrilla 4.8608 kg, asas 0.994 kg, borde 11.1328 kg; juntas
  ENTERO(L/4) × perímetro.
- Mano de obra CAPECO-FTCCP 2026 (edificación): operario 28.95, oficial 22.68, peón 20.54 S/ hh; herramientas 3 % (concreto) o 5 %
  (hojalatería). Precios oct. 2026 (S/ sin IGV): cemento 30.93/bol, acero 3.44/kg, tecnopor 1" 11.78/pln, tubo PVC 3" 11.27/m.
