---
name: metrado-drenaje-delphin
description: Metrar el drenaje pluvial (cunetas, colector frontal, canaletas, montantes, falsas columnas, sumideros, rejillas, juntas, tapas de inspección y de registro, lloraderos, bancas con techo) en la planilla Excel del usuario con partidas de nombre y estructura Delphin (hojas RESUMEN, PLANILLA GENERAL, CONCRETO, ENCOFRADO, ACERO, CURADO, REJILLAS, JUNTA, TAPAS, PARAMETROS, Listas y hojas del colector), con su sustento por lámina, ACU con mano de obra CAPECO 2026 y precios con fuente, sin alterar ningún valor del usuario, cotejo antes y después y edición del Excel sin romper formato (XML + recálculo con LibreOffice). Usar cuando el usuario pida metrar, agregar o corregir una partida de drenaje, armar ACU o desagregados, revisar un metrado o actualizar la planilla tras un cambio de diseño.
---

# Metrado de drenaje pluvial en la planilla Delphin del usuario

Criterio aplicado en CAR Varones (CUI 2705619), Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514), CAR Mujeres
(CUI 2717013, metrado congelado: ya presupuestado) e I.E. N.° 0590 Barranquita (C.I. 468901). Detalle completo en
`referencias/06_metrado_acu_especificaciones.md` (partidas, hojas, fórmulas, ACU, precios, edición XML, especificaciones) y
`referencias/07_componentes_complementarios.md` (canaletas, montantes, falsa columna, sumidero, rejilla, juntas, lloraderos, tapa
ciega, bancas). Las rutas de archivos de las referencias son del trabajo original y no existen en este chat.

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

## 1. Principios del metrado (reglas del usuario)
1. Trabajar sobre **su** archivo y su formato; nunca borrar ni rehacer hojas suyas ("¿por qué borras mi metrado de concreto y
   encofrado?"). Lo nuevo va en hojas nuevas o filas nuevas con su mismo estilo.
2. No mezclar partidas sumando una en otra; el colector es partida aparte; las cunetas son del usuario (el colector no metra cunetas).
3. Estructura y nombres de partidas = base Delphin del CAR Mujeres; **cantidades siempre del metrado propio**. Solo se cambia un nombre
   si la obra es la misma; si cambia dimensión, material, espesor o unidad, se consulta.
4. Proyecto congelado (ya presupuestado): solo se agrega lo pedido y todo lo demás queda idéntico.
5. Cada fila con su sustento (código de lámina tal cual el rótulo del usuario y criterio). Cita a una lámina que el usuario excluyó de su
   juego: se borra la cita, no se toca el valor.
6. Rellenos menores (base de un emboquillado) van dentro de la partida de relleno. Arreglar planos no cambia el metrado.
7. El ACU coincide con los planos (cantidades por unidad tomadas de la lámina de detalle). Cambiar la unidad para valorizar (glb → m o
   und) solo en el libro de ACU; vale el metrado original.
8. No inventar lo que no está en el plano (montantes, sumideros, dados, tapas, descuentos de rejilla): pedirlo y listarlo como
   pendiente. No preguntar lo que el plano ya muestra (por dónde entran vehículos, dónde hay cerco).
9. **El trabajo llega hasta el metrado** (usuario, 24-10 y 29-10-2026: "olvídate de costos de precios, en ningún momento estamos
   viendo eso, solo llegamos hasta metrados"): no proponer ACU, precios ni presupuesto si no los pide; las ACU de §8 solo a pedido.
   El presupuesto lo hace el ingeniero en **Delphin, no en S10** (no proponer exportar a S10).
10. Antes de usar datos (horas-hombre, insumos, metrados, precios) confirmar de qué proyecto son; nunca meter datos de una obra en el
   archivo de otra (pasó con horas-hombre del CAR Mujeres puestas en el archivo de otra obra).
11. Excel que se entrega: sin hojas protegidas, con los decimales completos a la vista y todo con fórmulas.

## 2. Insumos que hay que pedir
Planilla vigente (.xlsx), planta general y perfiles/secciones (DXF), juego de láminas que imprime el usuario (PDF con códigos), lista de
partidas Delphin de referencia (o su COMPARATIVO), nombre del proyecto y CUI, y datos que no salen del plano: tapas de registro en
tramos tapados, montantes por edificación y lado, red de piso, dados, descuentos de rejilla.

## 3. Estructura de partidas (ejemplo Delphin del Hogar de Refugio; no renumerar los huecos de la base)
01.04.03 SISTEMA DE DRENAJE PLUVIAL · .01 TRABAJOS PRELIMINARES (.01 LIMPIEZA MANUAL DE TERRENO m², .02 TRAZO, NIVELES Y REPLANTEO
PRELIMINAR m²) · .02 MOVIMIENTO DE TIERRAS (.01 EXCAVACIÓN MANUAL DE ZANJAS P/CUNETAS m³, .02 … P/DADOS DE CONCRETO, .03 REFINE,
NIVELACIÓN Y COMPACTACIÓN EN TERRENO NORMAL m², .04 RELLENO COMPACTADO C/MATERIAL PROPIO SELECCIONADO m³, .05 ELIMINACIÓN DE MATERIAL
EXCEDENTE D<1Km m³) · .03 CONCRETO SIMPLE (.01 CONCRETO f'c=100 kg/cm2 PARA SOLADO E=4'' m², .02 f'c=140 PARA DADOS m³) · .04 CONCRETO
ARMADO · .04.02 CUNETAS (.01 CONCRETO f'c=175 kg/cm2 PARA CUNETAS m³, .02 ENCOFRADO Y DESENCOFRADO DE CUNETAS m², .03 ACERO f'y=4200
kg/cm2 PARA CUNETA kg, .04 CURADO DE CONCRETO EN CUNETA m²) · .04.03 VARIOS (.01 REJILLA METALICA P/CUNETA C/PL 1''x 3/16'' Y ANGULO 1''
x 1'' x 3/16'', S/DETALLE m, .02 TAPA DE INSPECCION 0.60m x 0.60m und, .03 JUNTA DE DILATACION E=1" CON SELLADOR ASFALTO m, .04 LLORADERO
DE TUBERIA PVC Ø3" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m (CUNETA COLINDANTE CON AREA VERDE) und) · .05 RED DE COLECCIÓN: .05.01 TECHO
(MONTANTE CON TUBERÍA PVC DE 4" m; FALSA COLUMNA P/MONTANTE DE 0.20m x 0.15m x 1.30m und con subpartidas de concreto f'c 175, encofrado y
acero; CANALETA DE PLANCHA DE ACERO GALVANIZADO e=0.9mm, SECCIÓN 0.25m x 0.20m m; SOPORTE DE PLATINA F°G° 1" x 1/8" P/CANALETA und; TAPA
LATERAL …; BOQUILLA … A MONTANTE Ø4" und) · .05.02 PISO (TUBERIA DESAGÜE PVC-CP Ø4" m; SUMIDERO METALICO C/PLATINA 1" X 3/16"; CODO
DESAGÜE PVC Ø4" x 90°; TEE SANITARIA) · .05.03 ACCESORIOS (CODO 90°, COLGADOR F°G°, ABRAZADERA F°G°) · .05.04 bancas (si hay).
01.04.04 COLECTOR PLUVIAL FRONTAL (TRAMO …): limpieza, trazo, excavación P/COLECTOR, refine, relleno, eliminación, solado E=2'',
CONCRETO f'c=210 PARA COLECTOR (una sola partida), ENCOFRADO, ACERO, ACABADO FROTACHADO DE LOSA SUPERIOR (VEREDA), CURADO, TAPA DE
REGISTRO CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08 (und), JUNTA DE DILATACION E=1" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR (m),
JUNTA E=1" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO (m). Unidades: m, m², m³, kg, und ("ml" → "m", "Kgr" → kg).

## 4. Hojas y formato de la planilla
- Orden: RESUMEN · PLANILLA GENERAL DE METRADOS · CONCRETO EN CUNETAS · ENCOFRADO Y DESENCOFRADO · METRADO MONTANTES · METRADO  EN PISO
  (SUMIDERO) (con **dos** espacios, respetarlo) · METRADO CANALETAS · METRADO ACERO · METRADO DE CURADO · METRADO DE REJILLAS · METRADO JUNTA
  DE DILATACION · METRADO LLORADEROS · PLANILLA TAPAS REGISTRO INTERNO · PARAMETROS · Listas · hojas COLECTOR (PARAMETROS, MOV. TIERRAS,
  CONCRETO, ENCOFRADO, ACERO, REGISTROS Y TAPAS, JUNTAS Y EMPALMES, INSUMOS) · COSTO HORA HOMBRE 2026 · ACU … · DESAGREGADO ….
- RESUMEN: Item · Descripción · Unid. · Total (fórmula a la columna K de la PLANILLA). B4 entidad, B5 nombre del proyecto con CUI (se
  cambia en un solo lugar), B6 ubicación, B7 fecha; las demás hojas los leen con `=+RESUMEN!B4`…`B7`.
- PLANILLA GENERAL: ITEM · DESCRIPCION · Nº DE VECES · LARGO · ANCHO · ALTURA · FACT. · AREA · VOLUMEN · PARCIAL · TOTAL · UND. Fila de
  partida con TOTAL = SUMA de sus parciales; filas de sustento por eje o tramo con PARCIAL = producto o enlace a la hoja de detalle.
- Colores: dato amarillo FFF2CC, fórmula verde claro, unidad gris F2F2F2, tipo lila E4DFEC, total naranja F4B183, cabeceras azules con
  letra blanca, barra de totales azul oscuro; Arial Narrow. Fórmulas visibles (nunca valores fijos); Excel en español (REDONDEAR, SUMA,
  SI, separador ";"). PARAMETROS: tapa (cantidad, 0.60, 0.60, 0.10, rec. 0.025, @0.15, 0.56 kg/m, barra 9 m), solado sumado a
  excavación 0.10, esponjamiento 1.20. Listas: kg/m (6 mm 0.222; 8 mm 0.395; 3/8" 0.56; 12 mm 0.888; 1/2" 0.994; 5/8" 1.552; 3/4" 2.235;
  1" 3.973), tipos ABIERTA/TAPADA, conteo TEÓRICO (L/s + 1) o ENTERO (redondeo arriba + 1).

## 5. Cunetas (sección 0.40 interior, muros 0.10, losa 0.10, tapa 0.10, exterior 0.60, S 0.5 %)
- H se mide desde el NCT (borde) hasta la cota de fondo, en abierta y en tapada; H(x) interpolada entre secciones; área de muro = ∫H dx.
  Si un NCF no cierra con la pendiente, avisar (no corregir en silencio).
- Concreto: muros ∫H dx × 0.10 × 2; losa L × 0.60 × 0.10; tapa L_tapado × 0.60 × 0.10.
- Encofrado (área de una cara, cant. 2): abierta externo (H + 0.10)·L, interno H·L; tapada externo (H + 0.20)·L, interno H·L + fondo
  de tapa L_tapado × 0.40.
- Curado por tramo: 2·L·H_prom + L·0.40 + (L·0.40 si TAPADA); 3 o 4 caras.
- Acero: **solo donde H ≥ 0.40** (desde el NCT o la rejilla); H < 0.40 abierta = concreto simple; **todo tramo tapado lleva acero**
  (U + tapa) aunque H < 0.40; un tramo que pasa de 0.40 se metra desde la progresiva donde H = 0.40. Longitudinal 3/8" @0.20 si
  H < 0.45, @0.22 si < 0.60, @0.25 si mayor; barras = REDONDEAR.MAS((0.60 + 2H)/sep) al inicio y al fin; transversal U @0.25,
  desarrollo 0.60 + 2(H + 0.05), cantidad L/0.25 + 1; tapa 3/8" @0.25 de **0.56 m siempre**. Hoja con una fila por tramo (Ø, factor
  BUSCARV, longitudinal, transversal, tapa, total del tramo).
- Planilla por eje: limpieza y trazo L × 1.40 (franja de trabajo); excavación L × 1.40 × (H_prom + 0.10 + 0.10 solado); refine y
  solado E=4" L × 0.60; relleno L × 0.80 × (H_prom + 0.20); eliminación (exc − rell) × 1.20; dados 0.40 × 0.35 × 0.40 = 0.056 m³ c/u.
- Rejilla: longitud = tramo ABIERTO − descuentos a mano (puertas, cruces); tapados sin rejilla. Módulo 1.00 m (0.997), ancho 0.497 en
  rebaje 0.05 × 1", 2 ángulos L 1" × 1" × 3/16" + 39 platinas 1" × 3/16" × 0.446 de canto @1" = 20.0 kg/m; anticorrosivo + esmalte.
- Junta de cunetas (EG-2013 MTC, Sección 510): cada 3.00 m y en cambios de dirección, **en toda la U** (2 muros + fondo): por eje
  H_med = área de muro/L; N = REDONDEAR.MAS(L/3.00); longitud = N × (2·H_med + 0.40). Tecnopor 1" en todo el espesor + sellador
  asfáltico 1" × 2" (RC-250 + arena) en la cara interior; acero longitudinal cortado a 0.05.
- Tapa de inspección (tramos tapados) 0.60 × 0.60 × 0.10 f'c 210: concreto 0.036 m³, encofrado 0.60 m², acero parrilla 3/8" @0.15
  2 × 5 × 0.55 × 0.56 = 3.08 kg por tapa. Ubicación: inicio y fin de cada tapado, en cada empalme y a ≤ 10 m.
- Lloraderos (solo muros cuya franja exterior de 0.30 m cae sobre área verde; tramos ≥ 1.50 m; cada lado aparte):
  N = REDONDEAR.MAS(L/1.50). Hoja METRADO LLORADEROS (N°, eje, progresivas, lado, longitud, @1.50, und, TOTAL) + DESAGREGADO por
  lloradero: tubo PVC 3" 0.30 m, 8 perforaciones 3/8", excavación 0.027 m³, grava 20–40 mm 0.0297 m³, geotextil no tejido 0.594 m²,
  mortero 1:3 0.0005 m³; control con el RESUMEN `=SI(ABS(E−F)<0.001;"CONFORME";"REVISAR")`.
- Cunetas que llegan a un colector: se metran hasta la cara del muro (acortar lo que invade la franja; prolongar lo que no llega) y se
  documenta en una hoja "CUNETAS - LLEGADA AL COLECTOR" (longitud dibujada, ajuste, longitud metrada, termina en, sustento).
- **Ancho variable por eje** (criterio general, 24-10-2026): cada eje con su ancho libre b (0.30 a 0.40, de 5 en 5 cm, una medida por
  sector). En las fórmulas de arriba 0.40 pasa a b y 0.60 a b + 0.20 (losa, tapa, fondo de tapa, curado, refine y solado); excavación =
  altura libre + 0.10 de losa + 0.10 de solado. La columna del ancho va en la planilla por eje.
- Con lloraderos no se metran drenes franceses ni subdrén (el usuario no los usa). Lloradero = tubo + caja filtrante 0.30 × 0.30 de grava
  y geotextil (su DESAGREGADO).
- **Tarrajeo interior de cunetas** (cuando el proyecto lo lleva; I.E. N.° 292 Ciudad Satélite, CUI 2684251, 26-10-2026): hoja METRADO DE
  TARRAJEO con el interior de las cunetas con rejilla y de las tapadas (muros y fondo), en su propia partida del árbol del proyecto.
- Junta cuneta-piso: confirmar con el usuario a qué lados va (contra qué pisos) antes de metrarla; no asumir "ambos lados contra
  cualquier piso" (quedó pendiente de revisar).
- Partidas que aparecen solo si el diseño las tiene: losa vehicular de cuneta tapada en estacionamiento (f'c 280, rueda HL-93), caída
  corta, caja de caída y pase por muro con marco de concreto armado y poza; pozos de absorción o cámara de bombeo.

## 6. Red de techo, piso y bancas
- Canaletas (una por borde bajo de techo; dos aguas = dos): por edificación y lado, N° × L; soportes = SI(L>0; REDONDEAR.MAS(L/0.60)+1;
  0); 2 tapas por canaleta; boquillas = montantes del lado. Plancha referencial = m × 0.75 (0.25 + 2 × 0.20 + 2 × 0.05).
- Montantes PVC 4": m por edificación; 3 codos 90° por montante; colgadores 2 por montante de edificación; abrazaderas
  MAX(1; REDONDEAR.MENOS(L/4)) (no cambiar aunque la especificación diga @1.50: es el metrado del usuario).
- Falsa columna 0.20 × 0.15 × 1.30 (und = montantes, sin pago propio): concreto 0.039 m³, encofrado 0.65 m², acero (4 × 1.20 + 9 × 0.58)
  × 0.56 = 5.6112 kg por und; dado 0.40 × 0.40 × 0.35 en excavación y concreto f'c 140.
- Alcance acordado (25-10-2026) cuando el metrado sale del diseño de la red: se metran canaletas, soportes de platina 1" × 1/8", tapas
  laterales, boquillas, falsa columna (concreto, encofrado, acero), dados y, por cada montante, el codo de 90° de 4" del dado y el tubo
  PVC 4" embebido del dado a la cuneta (máximo 5 m, 1 %, mínimo 0.5 %). La altura del montante, el tubo que sube a la canaleta, los
  codos del desvío, colgadores y abrazaderas los mete el proyectista con los cortes de arquitectura; rejillas, tramos tapados y áreas
  verdes los confirma él. Montantes siempre de 4" (2 por lado en las esquinas; hasta 4 por lado).
- Soportes: el usuario observó "1616 soportes es demasiado; después revisaré": antes de entregar un conteo grande de soportes @0.60,
  mostrarlo por edificación y lado y pedir su confirmación.
- Sumideros solo en áreas libres pavimentadas sin cobertura (patio, maniobra, estacionamiento), con su tubo PVC 4" recto a la cuneta.
- Red de piso por sector: tubería PVC-CP 4" (m), sumideros, codos 90° (distinguir del codo del techo por el código), codos 45°, tees.
- Bancas con techo: solo los ítems que pida el usuario (ej. canaleta, tapas, 2 soportes por techo, 1 boquilla por techo); los codos,
  colgadores y abrazaderas que ya estén en METRADO MONTANTES no se repiten. Si falta una partida en el RESUMEN que el plano sí tiene
  (codo de 45°), agregarla con aviso.

## 7. Colector y tapa de registro (fórmulas completas en el skill `colector-pluvial-frontal`)
Hojas COLECTOR con fila "Criterio:" al inicio y una fila por tramo homogéneo; concreto en una sola partida con subtítulos Losa de
fondo / Muros / Losa superior; tapa de registro por und con hoja DESAGREGADO TAPA REGISTRO (ubicación, componentes por registro:
concreto 0.0370 m³, encofrado 0.2176 m², parrilla 4.8608 kg, asas 0.994 kg, borde 11.1328 kg; control CONFORME, tolerancia 0.0005;
sin ángulos, soldadura ni pintura). Juntas: dilatación ENTERO(L/4) × perímetro; longitudinal solo contra cerco o estructura.

## 8. ACU (formato Delphin)
- Encabezado: Partida (código y nombre Delphin) · Partida del metrado · Unidad · Metrado (fórmula a la planilla) · Rendimiento. Tabla:
  N° · RECURSO · UND · CUADRILLA · CANTIDAD · PRECIO S/ · PARCIAL S/ · FUENTE DEL PRECIO; grupos MANO DE OBRA, MATERIALES, EQUIPOS con
  subtotales; CU = MO + MAT + EQ; costo de la partida = CU × metrado. Cantidad MO (hh) = cuadrilla × 8 / rendimiento; herramientas
  3 % MO (concreto, juntas, tapa, lloraderos) o 5 % (hojalatería). Precio sin IGV = publicado / contenido / 1.18.
- Hoja COSTO HORA HOMBRE 2026 (CAPECO-FTCCP, edificación, 01.01–31.12.2026): básico 89.30 / 69.75 / 62.80; leyes sociales 112.20 %;
  BUC 32/30/30 %; leyes sobre BUC 12.25 %; seguro de vida 0.16; capacitación 0.40/0.31/0.28; movilidad 8.60; overol 0.89; total día
  231.62 / 181.46 / 164.34 → **28.95 / 22.68 / 20.54 S/ hh**. Todas las ACU enlazan a esa hoja.
- Ratios (dato editable) por unidad: concreto f'c 210 por m³ cemento 9.73 bol, arena 0.52, piedra 1/2" 0.53, agua 0.186, mezcladora y
  vibrador 0.8 hm (muros 1.0), operario 0.8, oficial 0.8, peón 6.4 hh (muros 1.0/1.0/8.0); encofrado por m² madera 4.24 p², clavos 0.20
  kg, alambre N° 8 0.20 kg, operario y oficial 0.8; acero por kg 1.05 kg, alambre N° 16 0.06, operario y oficial 0.032; excavación
  manual peón 2.67 hh/m³; relleno compactador 0.4 hm, operario 0.4, peón 1.6; eliminación volquete 0.133 hm, cargador 0.033, peón 0.133.
- Valores vigentes de referencia (S/ sin IGV): tapa ciega 182.06/und (rend. 4.58 und/día; MO 92.93, mat. 86.34, eq. 2.79); canaleta
  40.06/m; soporte 16.45; tapa lateral 15.59; boquilla 27.08; junta de dilatación del colector 11.60–11.66/m; junta con el cerco 8.49/m;
  lloradero 20.56/und (24 und/día, 0.5 operario + 1 peón).

## 9. Precios con fuente
Cada insumo con producto, presentación, precio publicado con IGV, contenido, precio sin IGV, tienda, enlace, fecha de búsqueda y estado
(verde comprobado, naranja referencia de otra ciudad, rojo sin precio publicado / "por cotizar en <ciudad>"). Preferir proveedor local;
aceptar Sodimac y Promart (tienen tienda en la región). Ejemplos (oct. 2026): cemento tipo I 30.93/bol; arena gruesa 40.68/m³; agua
8.33/m³ (tarifa EMAPA sin IGV); acero corrugado 3.44/kg; alambre N° 16 5.08/kg; tecnopor 1" × 1.20 × 2.40 11.78/pln; RC-250 15.00/gal;
tubo PVC 3" 11.27/m; geotextil 4.87/m². Nota en las ACU: "Precios sin IGV obtenidos de precios publicados, con su fuente; los marcados
por cotizar deben confirmarse".

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
MÉTODO DE MEDICIÓN, FORMA DE PAGO ("al precio unitario del presupuesto por <unidad>… compensación total…"). Capítulo I de generalidades
(normas RNE, NTP, ASTM, ACI; prelación planos → especificaciones → memoria → metrado). Láminas citadas con los códigos del usuario.

## 13. Lista de verificación final
- [ ] Ningún valor del usuario cambió fuera de lo pedido (cotejo); sin errores `#`; logos y estilos intactos.
- [ ] Nombres Delphin y unidades correctas; partidas sin mezclar; colector aparte; nada de otro proyecto.
- [ ] Acero de cunetas según H ≥ 0.40 o tapado; tapa 0.56 @0.25; juntas en toda la U; lloraderos solo junto a área verde.
- [ ] Desagregados = hoja fuente = RESUMEN ("CONFORME"); ACU enlazadas a la hoja de mano de obra y a precios con fuente.
- [ ] Mismas cantidades (registros, juntas, tapas, longitudes) en metrado, planos (cuadros leen la planilla), especificaciones y memoria.
- [ ] Citas de lámina existentes en el juego del usuario; pendientes y datos no disponibles listados aparte.
- [ ] Cada eje con su ancho libre; cantidades iguales a las del diseño (concreto, acero, rejilla, tapas, juntas, lloraderos, montantes).
- [ ] Datos solo del proyecto del archivo (horas-hombre, insumos, precios); nombre, CUI, ubicación y entidad (GTBM) del proyecto.
- [ ] Sin hojas protegidas, decimales completos; sin errores de fórmula tras recalcular (LibreOffice o un calculador equivalente).
- [ ] Ni ACU, ni precios, ni presupuesto si el usuario no los pidió.

## 14. Errores que el usuario ya corrigió (no repetirlos)
- Borrar o rehacer las hojas de cunetas del usuario al integrar el colector.
- Meter prolongaciones de cunetas y una partida de "empalme de cuneta" en el colector (las cunetas se metran hasta el muro).
- Siete partidas por componente para la tapa de registro: Delphin usa una por und con desagregado y ACU.
- Concreto del colector en tres partidas: es una sola.
- Junta de cunetas solo en los 2 muros: va en toda la sección en U (la losa amarrada se fisura).
- Junta "entre colector, cerco y piso" a los dos lados y con sello elastomérico: solo contra el cerco, con tecnopor + sellador asfáltico.
- Precios "de mercado" sin fuente y mano de obra no oficial (30.42/22.95/20.79): precios publicados con fuente y CAPECO 2026.
- Tapa con contramarco de carga vehicular donde solo hay paso peatonal ("tú tienes el plano, sabes por dónde entran vehículos").
- Agregar a las bancas codos, colgadores, abrazaderas o falsa columna que el usuario no pidió o que ya estaban metrados.
- Buscar el metrado de grava, tubo y geotextil en la hoja de unidades: está en el DESAGREGADO LLORADEROS (explicarlo, no duplicarlo).
- Reemplazar citas de láminas excluidas por otras: se borra la cita y el valor no se toca.
- Leer el "1.40" (ancho de zanja o franja de trabajo) como ancho del colector.
- Rótulo NCF que no cierra con la pendiente usado sin avisar (Eje 04: 259.66 era 260.42).
- Proponer presupuesto con ACU como "lo que más falta": rechazado; solo metrados.
- "¿Por qué el Excel está protegido? me redondea decimales": sin protección y con todos los decimales.
- Horas-hombre de una obra puestas en el archivo de otra: se devolvió el archivo a su original.
- Conteos de soportes muy grandes entregados sin revisar con el usuario ("1616 soportes es demasiado").

## Referencias
- `referencias/06_metrado_acu_especificaciones.md`: reglas, árboles de partidas por proyecto, hojas, fórmulas, tapa ciega, juntas,
  sustentos con código de lámina, ACU completas, precios con fuente, edición XML, especificaciones, cronología y validaciones.
- `referencias/07_componentes_complementarios.md`: dimensiones, materiales, ubicación, metrado y ACU de cada componente complementario.
