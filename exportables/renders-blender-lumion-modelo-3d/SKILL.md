---
name: renders-blender-lumion-modelo-3d
description: "Armar en Blender el modelo 3D de cualquier proyecto con planos de arquitectura en DXF (colegios, centros de salud, albergues, oficinas, viviendas, mercados, locales comunales y sus obras exteriores) y producir renders realistas fieles al plano: en Blender Cycles o llevando el modelo a Lumion por FBX o DAE. Colores del cuadro de acabados, pisos y áreas verdes según los achurados, cerco, obras exteriores según sus láminas, instalaciones visibles tal cual su plano. Trae scripts probados de materiales, árboles que no cruzan techos, piso recortado, cielo, encuadre de aéreas, serie de vistas y exportación a Lumion con tablas de materiales, árboles y cámaras. Usar cuando el usuario pida renders, vistas realistas, imágenes, maqueta o modelo 3D de un proyecto, o mencione Blender, Lumion o Cycles, aunque no pida este método por su nombre."
---

# Renders realistas y modelo 3D con Blender y Lumion desde los DXF de arquitectura

Método general para cualquier proyecto con planos de arquitectura en DXF. **Todos los datos del modelo (colores, alturas,
pendientes, número y forma de las edificaciones, obras exteriores, instalaciones) salen de las láminas del proyecto o se le
preguntan al usuario.** Los valores del "Ejemplo de referencia" del final son solo ilustrativos y no se copian a otro proyecto.

**Quién hace qué.** El modelo se construye en **Blender**, por script y con la geometría de los DXF. **Lumion no modela**: recibe
un modelo ya hecho, le pone materiales, vegetación y luz, y da imágenes y videos. Por eso hay dos salidas del mismo modelo:

| Salida | Cuándo conviene | Quién la corre |
|---|---|---|
| **Blender Cycles** | Hay que entregar imágenes ya, repetir la serie con cada corrección o trabajar sin tener Lumion a mano | Claude si hay Blender en el equipo, o el usuario con los scripts |
| **Lumion** | El usuario tiene Lumion, una tarjeta suficiente y quiere ajustar a mano vegetación, materiales, ambiente o video | El usuario, en su equipo |

Hay que decirle al usuario desde el inicio: **Lumion no da soporte oficial a Blender y no tiene LiveSync con Blender**; se exporta a
FBX o DAE y cada cambio se reimporta. Lumion tampoco se maneja por script desde aquí: se entrega el paquete y los pasos en
`references/lumion.md`, que hay que leer antes de preparar esa salida.

Herramientas con las que se probó el método: Blender 4.2 LTS (bpy, Cycles, OptiX) con shapely. La importación en Lumion **no** se
probó: el FBX y el DAE se comprobaron reimportándolos en Blender (escala, ejes, nombres de material y colores se conservan).

## Reglas permanentes del usuario (valen para todo proyecto)
- Todo en español. Entregables en **Word, Excel y DXF**; vistas previas en **PNG**; PDF solo si el usuario lo pide.
- **Escala real: 1 unidad = 1 m** ("si algo mide 0.56, así debe medir en el plano").
- Decir siempre **"cota de fondo"**.
- Citar cada proyecto por su **nombre completo y su CUI** (o código de inversión). No mezclar partidas, láminas ni datos entre proyectos.
- **Nada en los documentos que revele el uso de IA.** Nombre y CIP del proyectista: **campos en blanco**.
- **No modificar** los metrados ni los documentos del usuario salvo pedido expreso; cambiar solo lo pedido y verificar
  que lo demás quede idéntico (cotejo antes y después).
- Actualizar todo lo relacionado de forma coherente: **metrado ↔ planos ↔ especificaciones ↔ memoria**.
- **Cuando el usuario ya imprimió un plano, no se regenera**: los cambios van a los documentos y se le avisan.
- Las observaciones sobre documentos de otros profesionales van en una **nota de revisión interna**, nunca dentro del documento.
- No reenviar archivos que no cambiaron. Preguntar lo dudoso antes de producir, con una imagen de control si hace falta.
- **Ningún dato de un proyecto anterior se usa en uno nuevo** (colores, dimensiones, niveles, cantidades, nombres):
  todo sale de los planos y documentos del proyecto nuevo o se le pregunta al usuario. Los proyectos citados son solo ejemplos.
- **Pedir permiso antes de descargar** (programas, texturas, modelos), diciendo nombre, fuente, tamaño y licencia.
- Si el usuario pide solo una cosa o dice que pare, se hace eso y se para: no seguir produciendo vistas por iniciativa propia.
- Revisar el trabajo propio varias veces antes de entregar; decir con claridad lo que no se pudo comprobar.

## 1. Insumos y datos que hay que pedir
1. **Datos del proyecto**: nombre completo, CUI, ubicación, zona UTM y datum del plano.
2. **Planta general en DXF**: contorno de cada edificación, planta de techos (coberturas, cumbreras, caídas, aleros), achurados
   de pisos y de áreas verdes, veredas, cerco con sus columnas, ingresos. Si las capas no son evidentes, pedir cuáles son.
3. **Plantas, cortes y elevaciones de cada edificación**: NPT, fondo y nivel superior de viga, cumbrera, naves altas, sobretecho,
   pendiente de cada techo, alero y punto de arranque de la cubierta.
4. **Cuadro de vanos** (código, ancho, alto, alféizar, sobreluz, tipo de hoja) de las láminas de detalle y **cuadro de acabados y
   colores** de la arquitecta (código, nombre, RGB o RAL, elemento donde va según las elevaciones).
5. **Láminas de obras exteriores** que tenga el proyecto: ingreso o pórtico, cerco, estacionamientos, patios, losas deportivas,
   juegos, tanque elevado, cisterna, PTAR, biohuerto, caseta, rampas, mobiliario exterior.
6. **Planos de instalaciones que deban verse** (drenaje pluvial, iluminación exterior, otras) y sus detalles.
7. **Qué quiere ver**: preguntar **cuántas vistas y cuáles** (aéreas, fachada, peatonales, interiores, planta), si quiere personas
   o autos (por defecto no), resolución, formato y si la salida es Blender, Lumion o ambas.
8. **Su equipo**: tarjeta de video y memoria, versión de Blender, si tiene Lumion y cuál. Los DXF pueden pesar cientos de MB: pedir
   solo los necesarios, y guardar lo extraído en una caché para no releerlos en cada corrida.
Lo que falte se pregunta; nunca se completa con datos de otro proyecto.

## 2. Lectura de los DXF (un solo dato para Blender y Lumion)
- **Coordenadas locales en metros**: restar un origen redondo de la UTM del proyecto y usar **el mismo** en todo. Con la UTM completa
  fallan la precisión en Blender y el punto de inserción en Lumion, que es el 0,0,0 de Blender. El origen se anota en el LEEME.
- Muros: pares de líneas paralelas de la capa de muros separadas dentro del rango de espesores del proyecto (criterio por defecto
  del usuario 0.07 a 0.42 m; confirmar en cada proyecto) = un muro con su espesor, también los interiores, unidos a través de
  columnas y columnetas. Columnas con su sección de la planta.
- Vanos: bloques indicadores de puerta y ventana de las plantas, pasados a la planta general por coincidencia de muros; el
  tamaño sale del **cuadro de vanos de los detalles, que manda** sobre el de las plantas (criterio por defecto del usuario;
  confirmar en cada proyecto). Diferencias (cantidades distintas, vano sin indicador, código que no está en el cuadro) →
  lista para confirmar con la arquitecta, nunca inventar en silencio.
- **Alturas y pendientes: las de los cortes del proyecto**, edificación por edificación. Si un dato falta (alero, arranque de la
  cubierta), preguntar. Comparar las cumbreras rotuladas con las que da la geometría y reportar las que no cuadran.
- Pisos: el área verde sale **solo** de los achurados de área verde de la planta (identificar sus capas en cada proyecto); arena,
  grava u otros solo donde está su achurado; lo demás según el cuadro de acabados de pisos (concreto con juntas si el plano no
  indica otro). Pavimento = lote − áreas verdes − edificaciones − veredas.
- Hacer una **planta de control PNG** por edificación (muros, vanos, columnas, techo) y revisarla, y si hay dudas mostrarla al
  usuario, antes de modelar.

## 3. Escena en Blender
Copiar `scripts/` a una carpeta del proyecto y escribir ahí un generador propio de la obra (por ejemplo `escena.py`) que importa
`base_escena.py`. **`scripts/ejemplo_escena.py` es la plantilla mínima**, con datos inventados: comprueba la instalación y muestra el
uso de cada función. Todo cambio se hace en el generador y se vuelve a correr; nunca a mano en el .blend.

| Script | Qué da |
|---|---|
| `base_escena.py` | `rgb`, `mat_pintura`, `mat_concreto` (juntas), `mat_calamina`, `mat_pasto`, `mat_vidrio`, `mat_simple`; `caja`, `prisma`, `obj_mesh`, `Malla` (miles de cajas en un objeto por material); `piso_exacto`; `prototipos_arbol`, `plantar_arboles`; `suavizar_cilindros`; `mundo`, `ajustes_render` |
| `render_serie.py` | Serie de vistas desde un JSON, con GPU, sol por vista y planta ortográfica |
| `encuadre.py` | Mira y focal para que todo el predio entre en una aérea sin cortarse (no requiere Blender) |
| `exporta_lumion.py` | FBX y DAE, tablas de materiales, árboles y cámaras, y marcas para plantar los árboles (ver §5) |

```bash
# una sola vez: shapely en el Python de Blender
"<carpeta de blender>/4.2/python/bin/python.exe" -m ensurepip
"<carpeta de blender>/4.2/python/bin/python.exe" -m pip install shapely
```
```bash
blender -b --factory-startup --python escena.py -- modelo.blend
```
```bash
blender -b modelo.blend --factory-startup -P render_serie.py -- vistas.json renders 48 1280
```
Rutas con espacios entre comillas. Primero la prueba baja (48 muestras, 1280 de ancho) y se **mira cada imagen**; la serie final
se hace al final (192 muestras, 1920) y solo con las vistas aprobadas.

**Geometría**
- Edificaciones: muros con sus vanos, puertas y ventanas del tamaño del cuadro, vigas y columnas a la altura de los cortes,
  cubiertas con el contorno de la planta de techos y la pendiente de los cortes, hastiales, cuerpos de distinta altura,
  sobretechos y celosías si el plano los tiene.
- Exteriores **cada uno según su lámina**: el cerco en todo el perímetro que dibuja el plano (frente incluido) con su detalle;
  portones, rejas y celosías del material que dice el plano (si es plancha llena, llena); cada obra exterior con sus medidas.
  **No agregar** elementos que no estén en el plano (pérgolas, rejas, techos, mobiliario) **ni quitar** los que están.
- Instalaciones visibles **tal cual su plano** (explotar el bloque de la red, no reinterpretarla): en drenaje, cunetas con su
  sección y rejilla, sumideros, tapas, canaletas, montantes, colector y juntas con las medidas de las láminas del proyecto;
  flechas de sentido solo en planta.
- Pisos con `piso_exacto`: recorta al contorno real. Excluir celdas por su centro deja bordes en escalones donde el plano tiene una
  diagonal, y desde el aire se nota.
- Personas y autos **solo si el usuario los pide**. Hechos con cajas y cilindros se ven de juguete: si los pide, proponerle descargar
  modelos reales, con permiso.

**Colores y materiales**
- **Colores: los del cuadro de acabados de la arquitecta**, con su código y su RGB o RAL, en el elemento que indican las
  elevaciones. Antes de modelar, armar la tabla código → elemento → RGB y revisarla. Si elevaciones y detalles dan colores
  distintos para un mismo elemento, preguntar y anotar la decisión.
- **Nombre de material estable y claro** desde el principio (`TP-1_guinda_columnas`, `concreto_patio`): Lumion agrupa por ese nombre
  y con él reconoce lo ya asignado. Un material distinto por cada superficie que se quiera tratar aparte.
- Pasto: `mat_pasto` con imagen mezcla dos capas de la textura para que desde el aire no se vea cuadriculado, y baja la saturación.
- Vidrio: `mat_vidrio` oscuro y opaco con reflejo. Sin interiores modelados, uno transparente deja ver un vacío.

**Árboles**
- `plantar_arboles` recibe un polígono con todo lo que no se puede tocar: **cada cobertura y también el cerco**. Reduce la copa
  según su radio real, hojas sueltas incluidas, y la descarta si tendría que quedar muy pequeña. Devuelve los descartados: decirlos.
- Follaje de hojas sueltas también en los árboles del entorno. Se plantan como instancias, así que no gastan memoria; los de pocas
  caras se ven de caricatura.

**Luz y tono** (`mundo` y `ajustes_render`; punto de partida probado, ajustar mirando las imágenes)

| Ajuste | Valor | Por qué |
|---|---|---|
| Intensidad del disco solar | 0.23 | Con más sol el pasto sale neón y los colores se alejan del cuadro (un guinda se vuelve rojo) |
| Cielo que ilumina | 0.22; 0.50 con sol a menos de 15° | Luz de relleno; la luz blanca de las nubes suma a las sombras |
| Cielo que ve la cámara | 1.15, con nubes a 3.2 | Rama aparte: el fondo se ajusta sin alterar la luz de la escena |
| Tono | AgX, `AgX - High Contrast`, exposición −1.0 | Sin zonas quemadas |
| Rebotes | 10 (difusos 5, brillo 3, transparencia 12) | Rellena sombras; las hojas necesitan transparencia |
| Muestreo | Adaptativo 0.03 con eliminación de ruido | |

Las nubes deben ir en las dos ramas del cielo: puestas solo en la rama de luz iluminan pero la cámara nunca las ve. Dan un velo suave,
no cúmulos definidos; para un cielo con formas claras, usar una imagen HDRI de uso libre, con permiso para descargarla.
Después de la primera prueba, **medir un píxel de cada color en una cara soleada** y compararlo con el RGB del cuadro: el ojo engaña. Si se
aleja mucho, ajustar el sol o la exposición antes de tocar el color, que debe seguir siendo el del cuadro.
Si hace falta profundidad en las aéreas, añadir niebla de distancia con el pase Mist y comprobar que no lave el cielo.

## 4. Vistas
**Preguntar cuántas vistas quiere y cuáles** antes de la serie final. Propuesta base para que elija: aéreas desde cada lado,
2 o 3 de fachada (frontal, ingreso, perspectiva), peatonales entre edificaciones "como alguien parado mirando", una por cada
zona exterior importante del proyecto y una planta general; de instalaciones (drenaje u otras) solo si se piden.

`vistas.json` define cada una con `pos`, `mira`, `focal`, `sol_elev` y `sol_rot` (ver el encabezado de `render_serie.py`):
- **Aéreas**: calcular mira y focal con `encuadre.py`; que no se corte el predio ni el tanque. Focal 30–42 mm; menos de 28 mm deforma.
```bash
python encuadre.py --predio 0 0 40 30 --alto 3 --punto 20 13 5 --camara A1 -22 -30 28 --camara A2 70 -25 30
```
- **Peatonales**: cámara a 1.55–1.70 m con focal 18–24 mm, parada dentro del lote. Comprobar que no quede dentro de un muro, detrás de
  una malla o de un cerco, porque tapan la vista.
- **Sol**: `sol_rot` es el rumbo desde donde viene (205 = suroeste, 25 = noreste, 100 = este). Elegirlo para que la cara principal quede
  iluminada; si la sombra de una copa cae rara sobre un tanque o una columna, cambiar el rumbo.
- **Planta**: `focal` 0 con `escala` en metros y `vertical` si el lote es alargado, con la orientación del plano.
- Nombre de archivo con código y lugar (`A1_AEREA_FRONTAL_SUROESTE_<PROYECTO>.jpg`). Al cambiar nombres, no dejar imágenes viejas con
  otro nombre en la carpeta de entrega. Pruebas en otra carpeta.

## 5. Salida a Lumion
Leer `references/lumion.md` antes de preparar esta salida.
```bash
blender -b modelo.blend --factory-startup -P exporta_lumion.py -- paquete_lumion MODELO vistas.json
```
Genera `MODELO.fbx` y `MODELO.dae`, las marcas de árboles y los tres CSV. Se entrega con un **LEEME de pasos** en español (plantilla en la
referencia), que incluye lo que el usuario debe revisar.
- Los materiales con nodos de Blender **no pasan a Lumion**: llega el color base, el nombre y las texturas de imagen. Lumion se ve
  bien porque el usuario le asigna sus materiales; la tabla le indica cuáles y con qué RGB.
- Sin vegetación: los árboles salen del FBX y se plantan los de la biblioteca de Lumion sobre las marcas.
- No prometer que el resultado se ve igual en todos los equipos: depende de la tarjeta de video y de los materiales que elija el
  usuario; el modelo y los colores sí deben ser exactos.

## 6. Fidelidad al plano, lámina por lámina ("cada detalle")
Antes de dar por terminado el modelo, recorrer cada lámina y marcar en una tabla (elemento, lámina, estado):
- **Planta general**: posición y contorno de cada edificación y su techo (cumbreras, caídas, aleros), veredas, pisos, áreas
  verdes (solo achurados), cerco completo, ingresos y obras exteriores.
- **Edificaciones**: muros exteriores e interiores con su espesor, columnas con su sección, puertas y ventanas con ancho, alto y
  alféizar del cuadro de vanos, sobreluces, alturas de los cortes, pendiente de techo.
- **Obras exteriores**: cada una con su lámina de detalle (portones, casetas, estacionamientos, tanques, patios, juegos, bancas,
  PTAR, losas, cerco).
- **Instalaciones visibles**: copiadas de su plano, sin reinterpretar.
- **Acabados**: cada color del cuadro en el elemento que indica la elevación.
Toda diferencia entre láminas (vanos, alturas, cumbreras, colores) va en una nota aparte "por confirmar con la arquitecta";
no se corrige el plano ajeno.

## 7. Verificación antes de entregar
- [ ] Ningún dato tomado de otro proyecto: colores, alturas, pendientes y medidas trazables a una lámina de este proyecto o a
      una respuesta del usuario.
- [ ] Plantas de control revisadas: cantidad de muros, columnas, puertas, ventanas y sobreluces igual a la de los planos.
- [ ] Colores según el cuadro de acabados; cerco completo incluido el frente; portones del material del plano; nada agregado
      que no esté en el plano ni nada que el usuario haya retirado; sin personas salvo pedido.
- [ ] Verde solo donde hay achurado; bordes de piso sin escalones; instalaciones completas y en su sitio; obras exteriores con su detalle.
- [ ] Ningún árbol cruza techos ni cerco (lista de plantados y descartados); nada flota ni se hunde; sombras y exposición sin zonas quemadas.
- [ ] **Cada imagen mirada una por una**, en especial los bordes y lo que hay detrás de los árboles; predio completo en las aéreas;
      colores medidos en la imagen contra el cuadro de acabados.
- [ ] Número y tipo de vistas = lo que pidió el usuario; sin imágenes viejas en la carpeta de entrega.
- [ ] Tabla de fidelidad lámina por lámina (§6) sin pendientes; diferencias entre planos enviadas como nota aparte.
- [ ] Si va a Lumion: FBX reimportado en Blender para medir escala, nombres y colores; LEEME con origen, unidades, tablas y vistas;
      dicho con claridad que la importación en Lumion la comprueba el usuario.

## 8. Errores que el usuario ya corrigió (lecciones generales)
**De fidelidad al plano**
- Cerco incompleto: el cerco va en todo el perímetro que dibuja el plano, frente incluido, con el tipo de cierre de su lámina
  (no poner rejas donde el plano dice muro).
- Demasiada área verde: el verde sale solo de los achurados de la planta; lo demás, el piso del cuadro de acabados.
- Elementos inventados (una pérgola, un techo que no estaba): se quitan; se modela solo lo que está en el plano.
- Portones y celosías dibujados como barrotes cuando el plano decía plancha llena: el material es el del plano.
- Instalaciones, bancas y juegos que no se veían, y un patio de juegos que parecía cemento: modelar todo lo que el plano tiene,
  con su piso propio (arena u otro según el achurado).
- "Quita a las personas… hazlo tal cual fielmente": sin personas salvo pedido; instalaciones copiadas del plano, no reinterpretadas.
- "Árboles que pasan el techo": regla de copas que no cruzan coberturas ni el cerco, medida con el radio real del follaje.
- Una PTAR modelada con losa cuando era terreno natural: cada obra con su acabado real del plano (solo asoman las tapas).
- Bancas mal orientadas: el mobiliario se orienta y se apoya como en su detalle, también si va metido en un entrante del patio.
- "Revisa el área de estacionamiento… va cada detalle": cada obra exterior se modela con su lámina.

**De cantidad y entrega**
- Demasiadas vistas de fachada: preguntar cuántas y cuáles; no producir más de las pedidas.
- "Solo dame la vista en planta nada más": entregar lo pedido y parar, aunque quede otra serie en marcha.

**De imagen**
- Pasto cuadriculado desde el aire → dos capas de textura mezcladas por manchas.
- Pasto neón y guinda que sale rojo → menos sol, más relleno de cielo y colores fieles al cuadro.
- Árboles de fondo de caricatura → follaje de hojas también en el entorno, como instancias. Hojas pálidas desde el aire → más
  rugosidad y menos brillo.
- Aéreas que cortan el predio → focal calculada con `encuadre.py`, no a ojo.
- Bordes de piso en escalones → recorte exacto al contorno.
- Tacho o rueda como huevo → costado suave y tapas planas (`suavizar_cilindros`). Si además le cae la sombra de una copa, cambiar el rumbo del sol.
- Cámara detrás de la malla del cerco → pararla dentro. Cámara dentro de un edificio → comprobar la posición antes de la serie.
- Franja de cierre atravesando el techo → altura calculada con la pendiente del tramo. Cara inferior de cobertura con ondas rara desde abajo
  → cara inferior lisa propia.
- Entrantes y corredores sin luz salen negros: no hay interior que refleje. Probar otro rumbo de sol o más relleno, y decirlo si queda.

## Ejemplo de referencia (solo ilustrativo; sus valores no se usan en otro proyecto)
Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514): 9 edificaciones (E-01 a E-09), pórtico de ingreso OE-01, losa
deportiva con techo en arco, red de drenaje pluvial completa.
- Colores del cuadro de la arquitecta de ese proyecto: TP-1 guinda RGB 123-31-45 en columnas y vigas; TP-2 gris RGB 125-133-139
  en muros; TP-3 RAL 9010 (RGB 241-236-225) en hastiales, parapeto y cerco (se usó el color del detalle donde la elevación difería).
- Alturas de sus cortes: NPT +0.15; fondo de viga +3.44; nivel superior de viga +3.70 (E-01) y +3.85 (demás); nave alta del SUM
  +5.05; cubiertas a dos aguas al 30 % desde el borde del alero (alero 1.50) al nivel de viga.
- Origen local E 349 090 / N 9 281 900; capas de área verde 0_PASTO 01 / HIERVA y de arena AR-SAND.
- Drenaje de ese plano: cunetas de 0.40 libre con muros de 0.10, rejilla de platinas 1" x 3/16" @ 0.025 con ángulo de marco,
  montantes PVC 4" con falsa columna, colector frontal con losa-vereda, juntas de 1" cada 3.0 m.
- Decisiones de ese proyecto: cerco frontal de muro sin rejas; se retiró la pérgola del patio cívico; portones del OE-01 de plancha
  llena; PTAR sobre tierra o hierba; bancas del patio al ras con sardinel detrás; sin personas.
- Serie en ese caso: 7 aéreas, 2 de fachada, 2 peatonales, una por zona exterior y una planta general (22 vistas).
