---
name: planos-dxf-escala-real
description: "Producir láminas DXF de cualquier proyecto y especialidad (drenaje pluvial, cunetas, colectores, cajas, detalles constructivos, señalización, ubicación) a escala real (1 unidad = 1 m) con Python y ezdxf: plantas, perfiles longitudinales con guitarra, secciones, detalles, isométricos, cuadros, rótulo, presentaciones de AutoCAD, índice de planos en Word y vistas previas PNG. Aplica las reglas de legibilidad del usuario: sin textos encimados ni verticales, letra grande, concreto con relleno gris sólido, colores para fondo blanco y llamadas sin cruces. Respeta los códigos de lámina que use el cliente. Usar siempre que se pida dibujar, corregir, reordenar, imprimir o indexar cualquier plano o lámina DXF de un expediente técnico."
---
# Planos DXF a escala real, ordenados y legibles

Método general para cualquier edificación (colegio, establecimiento de salud, municipalidad, albergue, mercado) y cualquier
especialidad que se dibuje en DXF. Los datos del rótulo, los códigos de lámina, las escalas y los colores propios de un proyecto
salen del proyecto nuevo o del juego del cliente; los de proyectos anteriores están solo en el apartado final **"Ejemplo de
referencia"**. Detalle en `referencias/05_planos_dxf.md` (describe proyectos ya trabajados; sus rutas no existen en este chat).

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

## 1. Insumos y datos que hay que pedir (no inventar)
| Grupo | Qué pedir | Regla |
|---|---|---|
| Base | DXF del usuario (arquitectura, topografía, su versión de planos); sistema de coordenadas y zona UTM | solo lectura; confirmar la zona si cabe en más de una |
| Metrado | Planilla vigente (Excel) | los cuadros de la lámina se leen de ella, nunca se recalculan |
| Diseño | Ejes, progresivas, cotas de fondo, NCT, NA, alturas, secciones, registros, cajas, juntas, descargas (o lo que corresponda a la especialidad) | una sola fuente para todas las vistas |
| Rótulo | Nombre completo del proyecto (2 líneas, la 2.ª termina en "CUI N.° xxxxxxx"), entidad, ubicación, especialidad, fecha, logo si lo usa | proyectista y CIP siempre en blanco |
| Juego | Códigos y prefijos de lámina del cliente (o su índice), formato de papel preferido, láminas ya impresas | códigos tal cual; lo impreso no se regenera |
| Estilo | Plantilla de rótulo o capas del cliente, si tiene | si no hay, el estilo por defecto de este skill |
| Ubicación | Foto aérea o imagen del local (con sus esquinas en UTM si las tiene), ubigeo | si no hay, calles de OpenStreetMap o plano del sitio |
Lo que no está en el plano (dónde entrega una cuneta, distancia entre tapas) se propone rotulado "referencial / verificar en
campo" o se pregunta; lo que el plano ya muestra no se pregunta.

## 2. Documento y unidades (ezdxf)
```python
import ezdxf
doc = ezdxf.new("R2010", setup=["linetypes"])
doc.header["$INSUNITS"] = 6; doc.header["$LUPREC"] = 2; doc.header["$LTSCALE"] = 0.25
doc.styles.add("STANDARD_AR", font="arial.ttf"); doc.styles.add("TITULOS", font="arialbd.ttf")
f = esc / 1000            # m de modelo por mm de papel; todo tamaño "de papel" se multiplica por f
```
- Geometría SIEMPRE en metros reales. Perfiles con H = V (sin exageración). Si algo mide 0.56 m, se dibuja de 0.56 m.
- Cada lámina en su zona del modelo con origen (ox, oy) = esquina inferior izquierda del papel; plantas en coordenadas reales
  (UTM o locales) para que queden "en su sitio"; las demás láminas apiladas en filas/columnas. Guardar la caja de cada lámina
  `{codigo: [ox, oy, ox+W·f, oy+H·f]}` para vista previa, auditoría y presentaciones.
- Compatibilidad AutoCAD: sin "/" en nombres de bloque; cada DIMSTYLE con dimpost="<>", dimapost="", dimblk="", dimblk1="",
  dimblk2=""; `doc.audit()` sin errores antes de guardar; "m2"/"m3" en vez de "²/³" (salen "m?"); diámetro con `%%c`.
- Todo cambio se hace en el script generador y se regenera; nunca a mano en el DXF final.

## 3. Formato, marco y rótulo (formato por defecto del usuario; si el cliente tiene el suyo, manda el suyo)
| Formato | mm | Uso típico |
|---|---|---|
| A0 | 1189 x 841 | plantas generales muy grandes |
| A1 | 841 x 594 | por defecto |
| A2 | 594 x 420 | perfiles cortos, empalmes, cuadros |
| A3 | 420 x 297 | índice de láminas, detalles pequeños |
Tamaño de papel según el dibujo, sin espacios vacíos excesivos. Marco interior x 25..W−10, y 10..H−10 (margen de anillado 25 mm),
polilínea 0.8 mm. Rótulo abajo a la derecha, 185 x 95 mm: PROYECTO (2 líneas), ENTIDAD, UBICACIÓN, ESPECIALIDAD, PLANO + título
(2.4 mm; si pasa de 62 caracteres baja a max(1.5, 2.4·62/len)), subtítulo ≤ 110 caracteres, `PROYECTISTA: ______  CIP: ____` en
blanco, ESCALA ("1/50", "INDICADA", "S/E"), REVISADO en blanco, FECHA, FIRMA Y SELLO en blanco, REVISIÓN, código de lámina 5.4 mm.
Nada dibujado encima del rótulo. Zonas fijas: vistas arriba; leyenda, notas y cuadros en la franja inferior (~110 mm).

## 4. Capas y colores (estilo por defecto para fondo blanco)
| Elemento | ACI / RGB | Grosor (1/100 mm) |
|---|---|---|
| Concreto cortado | contorno 250 + relleno SÓLIDO RGB (226,226,226) | 50 |
| Acero transversal (marcos) | 1 rojo, polilínea de ancho = diámetro real | 35 |
| Acero longitudinal cortado | 5 azul, círculo relleno a diámetro real, bloque a escala 1.0 | 35 |
| Acero liso (asas) | 30 naranja | 35 |
| Cotas | 94 verde oscuro, tic oblicuo | 18 |
| Llamadas y flechas | 30 naranja | 18 |
| Títulos | 160 azul, Arial negrita | 35 |
| Agua | 150 discontinua + relleno RGB (205,228,246) | 25 |
| Ocultos | 8 HIDDEN | 25 |
| Cortes | 6 magenta | 50 |
| Arquitectura de fondo | 8 gris, fino | 13 |
| Isométricos | caras RGB 232 / 206 / 178 (superior / frontal / lateral), aristas 8 | – |
- Prohibido amarillo (2), cian claro como texto, blanco puro (solo 7, que se ve negro en fondo blanco).
- Rellenos: HATCH sólido con color verdadero en la capa Y en cada entidad (si no, en el celular salen negros); capas nuevas con
  RGB definido o color 256. Rellenos al fondo con `msp.set_redraw_order({h.dxf.handle: "1"})`.
- No usar patrones (ANSI31, AR-CONC, EARTH, GRAVEL): en AutoCAD salen sin escala. Grava = piedras dibujadas a tamaño real; tierra =
  grupos de 3 trazos inclinados; concreto con hueco = un HATCH con camino exterior e interior.
- Colores de una especialidad o de un cliente (convención de cunetas, colores de acabado de arquitectura, colores de seguridad de
  señales) se toman del plano o la memoria de ese proyecto; si no hay, se usa la convención por defecto y se dice en la leyenda.

## 5. Textos
- Altura en papel = base × K por capa (≈1.3–1.35); en modelo `h = hmm·K·f`. Título de vista 4.0–6 mm (+ raya), subtítulo 3 mm,
  textos y llamadas 2.2–3.5 mm, notas 2.2–3 mm, cotas 3.0 mm, guitarra 1.8–2.0 mm, código de lámina 5.4 mm.
- NUNCA texto vertical (rot = 90) para rótulos; solo cotas verticales. Texto girado solo si sigue un elemento lineal en planta
  (progresivas, cota de curvas), con ángulo llevado a −90..90 para que no quede de cabeza.
- Llamadas ≤ ~62 caracteres por línea y 2–3 líneas; celdas de tabla: bajar la letra de 0.1 en 0.1 mm hasta que entre
  (ancho ≈ 0.72·h por carácter); no partir palabras en celdas angostas.

## 6. Cotas, niveles y llamadas
- DIMSTYLE por escala (`COT-50`...): dimscale = esc/1000, dimtxt 3.0, dimtsz 1.4 (tic), dimexe 1.6, dimexo 1.2, dimgap 1.0, dimtad 1,
  dimdec 2, dimlfac 1.0, texto negro. Crear el estilo de cada escala usada ANTES de dibujar.
- Las cotas miden el dibujo (texto "<>"). Nunca escribir un número que no corresponde. Texto fijo solo para pulgadas, alias o vistas
  ampliadas con su escala declarada en el título (k = esc_lámina/esc_vista).
- Preferir una sola escala por lámina; una vista a otra escala sin decirlo confunde al lector.
- Cotas por fuera: abajo parciales (muro – interior – muro) y total más abajo; a la derecha verticales (fondo – altura – losa) y total.
- Nivel: triángulo + raya y texto "CF <cota>", "NA <cota>", "NPT +<nivel>". Decir "cota de fondo", nunca "invert".
- Llamada: texto con apoyo horizontal de 4 mm y línea con flecha sólida hasta el objeto.

## 7. Que nada se cruce (algoritmos obligatorios)
- **Franja de etiquetas** (perfiles, plantas largas): juntar todas las etiquetas `(x, y, [líneas])`; ordenar de derecha a
  izquierda; cada una va a la fila más baja donde no choca con otro texto de la fila (holgura 1.5–2 mm), su texto no tapa la línea
  vertical de una etiqueta de fila más alta y su línea no cruza un texto de fila más baja; máximo 8 filas; puntos casi en el mismo
  x se unen en una etiqueta; si se sale del marco, el texto va a la izquierda de su línea. Título de la vista encima de la última fila.
- **Columna de llamadas** (secciones, cajas, detalles): textos en una columna a un lado, repartidos en el mismo orden vertical que
  sus puntos; permutar vecinos mientras dos líneas se crucen (prueba de segmentos, hasta 4n pasadas).
- **Plantas con muchos rótulos**: probar 8 posiciones alrededor del punto a 1, 2 y 3 veces la distancia; si se aleja, línea de llamada.
- **Mapas muy cargados**: globo numerado junto a cada punto y cuadro con el significado de cada número.
- **Cortes**: cada rótulo sube desde el corte hasta el primer hueco libre (cajas de alto variable), nunca filas fijas.

## 8. Cómo se arma cada vista (escalas por defecto; ajustarlas al tamaño del proyecto)
- **Planta**: arquitectura de fondo recortada y gris → límite de intervención (cerco o el que fije el proyecto; nada de obra fuera)
  → obra a escala real (contornos unidos con shapely `buffer(cap_style=2, join_style=2)`, estado por tramo) → elementos puntuales
  exactamente donde corresponden (registros donde entrega cada cuneta) → juntas → flechas de flujo (a intervalo fijo y en cada
  quiebre) → progresivas → rótulos → grilla UTM y norte → cuadro de coordenadas → leyenda y notas. Escala elegida para que el
  límite de intervención entre en el formato. Bloques de AutoCAD por tema (base, curvas, límite, sistemas, rótulos). Los elementos
  se dibujan como los dibuja el usuario en su plano (montantes, falsas columnas, sumideros, cajas filtrantes).
- **Lámina de ubicación** (primera del juego): mapas país → departamento → provincia → distrito y local, con los **límites reales**
  del INEI/IGN, área siguiente resaltada con su recuadro, norte, escala y fuente corta; mapa del local sobre la foto aérea del
  usuario o calles de OpenStreetMap; localización con cuadrícula UTM verdadera, ubigeo y coordenadas de los vértices del límite.
  Imágenes del usuario ajustadas al tamaño de los demás mapas sin deformarlas.
- **Perfil longitudinal** (1/50 H = V por defecto; 1/25 si un espesor mide < 3 mm en papel; ejes largos en piezas iguales apiladas):
  agua (relleno entre fondo y NA), losas cortadas, NPT, registros, llegadas, juntas, cruces, cajas, cotas, pendientes, terreno
  existente discontinuo; recuadro por sección con sus niveles y avisos de llegada o descarga. **Guitarra** con columna propia de
  nombres separada por línea vertical (progresiva, terreno, NCT, cota de fondo, nivel de agua, altura, excavación; o las filas que
  use el cliente). Estaciones en extremos, elementos y cambios de zona, omitiendo las demasiado juntas. La longitud siempre de
  sección a sección completa aunque el tramo siga en otra pieza. Título "PERFIL LONGITUDINAL <eje> - <descripción> - PROG. A a B"
  (sin nombres internos ni coordenadas). En la guitarra va la **pendiente de diseño** (no la de cotas redondeadas), en texto horizontal.
- **Sección** (1/15 o 1/20 por defecto; si la vista ocupa < 1/3 de su espacio, subir la escala): mirando aguas abajo; concreto en una
  pieza con hueco y relleno gris; acero con recubrimiento real (nunca fuera del concreto); agua con el caudal de ESE tramo; NPT,
  terreno, excavación y elementos vecinos solo si existen; cotas por fuera; niveles; llamadas en columna; título y subtítulo con
  progresiva, cota de fondo, tipo de tramo y escala. Si un tramo no lleva acero según el criterio del proyecto, llamada que lo diga.
- **Detalle** (1/10, 1/5, 1/2): una escala por lámina o vistas ampliadas con escala en el título; despiece; cuadro de componentes por
  unidad (el desagregado y el ACU deben coincidir con el plano); procedimiento en notas; fiel al dibujo del usuario (sin omitir piezas).
- **Isométrico**: `u = (x − y)·cos30`, `v = z − (x + y)·sin30`; esa fórmula sale EN ESPEJO para plantas reales: intercambiar
  `(x, y, z) → (y, x, z)` y comprobar con una rosa N/E (mirando desde el sur, el este a la derecha). Teselar caras (0.05 m) y pintar
  por profundidad; sombreado por la normal; aristas en capa aparte; solo caras que miran al observador; color verdadero en cada cara.
  No hacer el 3D de toda la red o de todo el terreno si el usuario no lo pide.
- **Cuadros** (acero, metrados, coordenadas): valores guardados de la planilla; si guarda fórmulas sin valores, recalcular una copia
  con LibreOffice (`soffice --headless --convert-to xlsx`) y leer con openpyxl `data_only=True`.
- **Otras especialidades** (señalización, mobiliario, arquitectura): planta base del cliente intacta, símbolos y rótulos con el mismo
  control de choques, cuadro y leyenda que cuadren con el metrado.

## 9. Códigos de lámina y juegos
- Manda la codificación del cliente (prefijos, numeración, erratas incluidas): se respeta tal cual en láminas, índices y documentos.
- Si el cliente no tiene codificación, proponer una por defecto y confirmarla: prefijo por especialidad o tema (U ubicación, planta,
  perfiles, secciones, detalles, cuadros), 00 = índice, numeración correlativa sin saltos (si cambia la cantidad de láminas de un
  grupo, se renumeran las siguientes); prefijo y número inicial a elección del usuario.

## 10. Presentaciones, índice y PNG
- Modelo configurado en el formato con "DWG To PDF.pc3" (evita "Paper Size Not Found"); una presentación por lámina con su código:
  `layout.page_setup(size=(W, H), margins=(0,0,0,0), units="mm", name="ISO_full_bleed_A1_(841.00_x_594.00_MM)", device="DWG To PDF.pc3")`,
  ventana del tamaño del papel centrada en (W/2, H/2) mostrando `(ox + W/2·f, oy + H/2·f)` con `view_height = H·f`, bloqueada
  (`flags |= 16384`); borrar "Layout1". Índice en A3: N.° / LÁMINA / DESCRIPCIÓN / FORMATO / ESCALA.
- Instrucción de impresión al usuario: pestaña de la lámina, Ctrl+P, Presentación, escala 1:1, centrar; todas juntas con PUBLISH.
- Índice de planos en Word: códigos y títulos TAL CUAL el rótulo del PDF del usuario, sin renumerar ni poner observaciones; orden
  que pida el usuario; tabla N.°, LÁMINA, DESCRIPCIÓN (título + contenido en gris), FORMATO, ESCALA; encabezado repetido, filas sin
  partir; total "N láminas (n en A0, n en A1...)". Lectura del PDF: `pdfinfo` (formato), `pdftotext -raw` (rótulo, código).
- Vista previa PNG: `ezdxf.addons.drawing` + matplotlib (Agg), fondo blanco, color real, una sola pasada del modelo y recorte por la
  caja de cada lámina; en paralelo con `xargs -P 4`. DXF enormes: recortar a la caja antes o dibujar solo las entidades de la caja.

## 11. Verificación antes de entregar (obligatoria)
1. Escala: medir 3 o 4 cotas del dibujo contra el diseño/metrado (ancho total, espesores, alturas, longitudes); tolerancia 1 mm.
2. Todo dentro del marco interior; nada sobre el rótulo; ninguna entidad fuera de toda lámina.
3. Ningún texto encimado con otro texto, cota o llamada; ninguna línea de llamada cruzada.
4. Ningún TEXT con rotación ≠ 0 salvo progresivas/curvas en planta y cotas.
5. Alturas en papel 1.8–6 mm; espesores ≥ 3 mm en papel; barras a diámetro real.
6. Sin amarillo; HATCH sólidos con RGB, sin patrones; capas nuevas con color.
7. Acero dentro del concreto menos el recubrimiento. Nada de obra fuera del límite de intervención.
8. Un mismo elemento igual en planta, perfil, sección, detalle e isométrico; cuadros = planilla; códigos sin saltos.
9. `doc.audit()` sin errores; láminas congeladas comparadas por huella (tipo, capa, punto, texto) antes/después: idénticas.
10. Mirar el PNG de cada lámina tocada; corregir y repetir. Entregar DXF + PNG (no PDF salvo pedido).
11. Un cambio de detalle obliga a revisar todas las láminas donde aparece y sus leyendas y notas.
12. Propiedades y metadatos del DXF vacíos (sin marcas de la herramienta); unidades en metros; un mismo valor con la misma cifra
    en planos, memorias y metrado.
13. Láminas citadas en memorias y especificaciones existen en el juego con ese código; rótulo con nombre y CUI del proyecto nuevo.

## 12. Errores que el usuario ya corrigió (lecciones generales)
- Amarillo en fondo blanco; rellenos negros en el celular (faltaba RGB por entidad).
- Acero longitudinal y transversal del mismo color; barras como "cuadraditos" o sobredimensionadas ("si es 3/8 es 3/8").
- Perfil exagerado en vertical ("dibujar con comando L", a su medida real); agua dibujada por debajo del fondo.
- Cotas con texto que no corresponde a la medida dibujada.
- Líneas de llamada mezcladas y cruzadas; vistas "todo unido": separarlas, cotas por fuera.
- Acero saliendo del concreto; huecos inexistentes en los isométricos.
- Detalles de elementos que el proyecto no tiene (p. ej. cerco); elementos corridos de su posición real; capa equivocada tomada como obra.
- "Letras pequeñitas", textos verticales y encimados; láminas en desorden y con espacio vacío (elegir A0, A1 o A2 según el dibujo).
- Láminas sin presentaciones ni índice; "Paper Size Not Found" al imprimir desde el modelo.
- Juntas dibujadas donde no hay estructura contra la cual ir.
- Piezas omitidas en un detalle o isométrico; cantidades de piezas distintas del detalle del usuario; faltaban cortes.
- Obra dibujada fuera del límite de intervención; 3D de todo el terreno no pedido; quiebres en planta distintos del criterio del proyecto.
- Nombres internos en los títulos de perfil; longitudes de tramo cortadas por la pieza.
- Acero en tramos que según el criterio del proyecto van sin acero; secciones imposibles (altura libre insuficiente).
- Vista a otra escala sin decirlo; patrones de achurado sin escala; "m³" que sale "m?".
- Índice renumerado, ordenado distinto del PDF del usuario o con observaciones; regenerar planos ya impresos.
- Mapas de ubicación con límites simplificados ("lo haces muy recto"): límites reales del INEI/IGN; cada mapa con su lista para
  elegir y la imagen cargada por el usuario redimensionada al tamaño de los demás.
- Pendiente de la guitarra calculada con cotas redondeadas; rótulos de curvas verticales.

## Ejemplo de referencia (valores de proyectos anteriores; reemplazar por los del proyecto nuevo)
Proyectos de donde salió el método: CAR Varones (CUI 2705619), Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514),
CAR Mujeres (CUI 2717013) e I.E. N.° 0590 Barranquita (C.I. 468901). Especialidad del rótulo: "INSTALACIONES SANITARIAS - DRENAJE PLUVIAL".
- Escalas usadas: planta del colector 1/200, de cunetas 1/250 (o la que haga entrar el cerco en A1); perfiles 1/50; secciones 1/15 de
  a 2 x 2 o 1/20 de a 3; detalles 1/5 y 1/10. Acero 3/8" r = 0.00475 m; 1/2" r = 0.00635 m.
- Convención de cunetas: azul = borde NCT de tramo abierto (rejilla celeste RGB 0,170,230 con platinas cada 0.10 m); verde = tramo
  tapado; magenta = losa de fondo; rojo vertical = sección; flechas rojas cada 5 m; progresivas cada 10 m; quiebres a 45° con chaflán
  de 0.60 m (no se muestran en perfil); acero solo si h ≥ 0.40 m o tapada; altura libre mínima de tapada 0.25.
- Códigos de trabajo: DP-00 a DP-10 (colector), DA, DD, DJ, DL, DS, DR (detalles); DC-00 a DC-nn y U-01 (cunetas sobre terreno).
  Juegos renombrados por los clientes: DPL-01 a DPL-42 y DPLV-01 a DPLV-44, con erratas como "DPVL-09" respetadas tal cual.
