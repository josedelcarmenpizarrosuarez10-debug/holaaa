---
name: renders-revit-modelo-3d
description: "Armar el modelo 3D de cualquier proyecto con planos de arquitectura en DXF (colegios, centros de salud, albergues, oficinas, viviendas, mercados, locales comunales y sus obras exteriores) y producir renders realistas en Blender Cycles fieles al plano: colores del cuadro de acabados del proyecto, pisos y áreas verdes según los achurados, cerco, obras exteriores según sus láminas e instalaciones visibles tal cual su plano. Llevarlo a BIM: Revit (IFC2X3 con sólidos cerrados vinculado origen a origen y script de Dynamo con familias nativas) y a Lumion, Twinmotion o Enscape (LiveSync o FBX con materiales por nombre). Usar cuando el usuario pida renders, vistas realistas, modelo 3D o BIM, IFC, Revit, Dynamo o Lumion de un proyecto."
---

# Renders realistas y modelo para Revit desde los DXF de arquitectura

Método general para cualquier proyecto con planos de arquitectura en DXF. **Todos los datos del modelo (colores, alturas,
pendientes, número y forma de las edificaciones, obras exteriores, instalaciones) salen de las láminas del proyecto o se le
preguntan al usuario.** Los valores del "Ejemplo de referencia" del final son solo ilustrativos y no se copian a otro proyecto.
Desde un chat en la nube no se maneja Revit, Lumion ni la GPU del usuario: se entregan los scripts (Blender, IFC, Dynamo)
listos para correr en su equipo, con un LEEME de pasos, y se generan las imágenes donde haya Blender disponible.
Herramientas con las que se probó el método: Blender 4.2 LTS (bpy, Cycles), ifcopenshell, Revit 2027 con Dynamo
(confirmar las versiones del usuario: cambian algunos nombres de la API).

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
   o autos (por defecto no), resolución, formato y si el modelo va a Revit, Lumion, Twinmotion o Enscape.
8. **Su equipo**: GPU, versiones de Blender, Revit y del programa de render. Los DXF pueden pesar cientos de MB: pedir solo los
   necesarios o entregar el lector para que lo corra en su equipo.
Lo que falte se pregunta; nunca se completa con datos de otro proyecto.

## 2. Lectura de los DXF (un solo dato para render y Revit)
- Coordenadas locales en metros: restar un origen redondo de la UTM del proyecto y usar **el mismo** en Blender, IFC, Dynamo y Lumion.
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

## 3. Escena en Blender (Cycles)
- Materiales con rugosidad y relieve leve: pintura de muros, concreto con bruñas o juntas, cobertura (calamina, teja, losa) con su
  textura y dirección, vidrio, aluminio, acero, madera, pasto con imagen sin cuadrícula.
- **Colores: los del cuadro de acabados de la arquitecta**, con su código y su RGB o RAL, en el elemento que indican las
  elevaciones. Antes de modelar, armar la tabla código → elemento → RGB y revisarla. Si elevaciones y detalles dan colores
  distintos para un mismo elemento, preguntar y anotar la decisión.
- Edificaciones: muros con sus vanos, puertas y ventanas del tamaño del cuadro, vigas y columnas a la altura de los cortes,
  cubiertas con el contorno de la planta de techos y la pendiente de los cortes, hastiales, cuerpos de distinta altura,
  sobretechos y celosías si el plano los tiene.
- Exteriores **cada uno según su lámina**: el cerco en todo el perímetro que dibuja el plano (frente incluido) con su detalle;
  portones, rejas y celosías del material que dice el plano (si es plancha llena, llena); cada obra exterior con sus medidas.
  **No agregar** elementos que no estén en el plano (pérgolas, rejas, techos, mobiliario) **ni quitar** los que están.
- Instalaciones visibles **tal cual su plano** (explotar el bloque de la red, no reinterpretarla): en drenaje, cunetas con su
  sección y rejilla, sumideros, tapas, canaletas, montantes, colector y juntas con las medidas de las láminas del proyecto;
  flechas de sentido solo en planta.
- Árboles: ninguno atraviesa una cobertura ni el cerco (reducir copa o descartar); follaje con hojas; vegetación del entorno aparte.
- Personas y autos **solo si el usuario los pide**.
- Luz y cámara (ajustes de partida que dieron buen resultado; ajustar a la vista): cielo físico (Nishita) con sol de baja
  intensidad y luz de cielo mayor solo en rayos de cámara, nubes; AgX "High Contrast", exposición cercana a −1.0; 10 rebotes;
  denoise; muestreo adaptativo; niebla leve de distancia. Cámaras peatonales a 1.55–1.70 m con focal 18–24 mm; aéreas 30–42 mm;
  planta ortográfica con la orientación del plano. GPU OptiX/CUDA si hay.
- Ejecución en el equipo: `blender -b --factory-startup --python escena.py` (arma y guarda el .blend) y luego
  `blender -b -P render.py -- <vista|serie> <muestras> <ancho>`. Primero una prueba a baja resolución.

## 4. Vistas
**Preguntar cuántas vistas quiere y cuáles** antes de la serie final. Propuesta base para que elija: aéreas desde cada lado,
2 o 3 de fachada (frontal, ingreso, perspectiva), peatonales entre edificaciones "como alguien parado mirando", una por cada
zona exterior importante del proyecto y una planta general; de instalaciones (drenaje u otras) solo si se piden.
Nombre de archivo con código y lugar (A1_aerea_frontal_suroeste.jpg) y un zip con todas.

## 5. Camino a Revit
### 5.1 IFC (todo el modelo o complemento)
- **IFC2X3 con sólidos cerrados IfcFacetedBrep** (el IFC4 con mallas IfcTriangulatedFaceSet vinculado en Revit se vio solo en
  líneas). Cada objeto con su clase (IfcWall, IfcColumn, IfcBeam, IfcSlab, IfcRoof, IfcDoor, IfcWindow, IfcPipeSegment,
  IfcFurnishingElement...), color, grupo en un Pset propio con las siglas del proyecto e IfcMapConversion con el origen UTM.
- Limpieza de malla: caras coplanares unidas (sin cuadrícula de líneas), sin puntos repetidos en los lazos, superficies abiertas
  con un espesor mínimo para cerrarlas; rejillas aligeradas; sin pasto 3D ni vegetación del entorno (árboles como RPC en Revit).
  Validar con ifcopenshell (0 errores de esquema, todos los elementos con geometría).
- En Revit: Insertar > Vincular IFC > Posicionamiento **Automático – origen a origen**.
### 5.2 Dynamo con familias nativas
- Un nodo Python Script (PythonNet3 o CPython3) con los datos embebidos en JSON; medidas en metros convertidas a pies. Correr
  **una sola vez** en un proyecto nuevo con plantilla de Arquitectura métrica; si se repite duplica: antes borrar lo creado.
- Cargar antes las familias que pida el cuadro de vanos (puertas simples y dobles, ventanas corredizas, fijas para sobreluces),
  columna rectangular y un árbol RPC. Si falta una familia, usar la primera de su categoría o una DirectShape con su material.
- Crea: materiales con los **códigos del cuadro de acabados** (más concreto, cobertura y área verde); tipos propios de **una sola
  capa** con **prefijo de las siglas del proyecto** para muro, piso y cubierta; muros por eje y espesor hasta fondo de viga; vigas;
  columnas; puertas y ventanas alojadas en su muro, duplicando el tipo con el ancho y alto del cuadro ("<siglas>-Puerta
  <ancho>x<alto>"); pisos con las áreas verdes como huecos; **cubiertas por huella** (NewFootPrintRoof) con la pendiente de los
  cortes en los bordes que indique la planta de techos; cerco; obras exteriores; árboles RPC.
- **Cubierta curva por extrusión** (NewExtrusionRoof sobre un plano de referencia vertical), si el proyecto la tiene: la extrusión
  va según la normal del plano; si Normal.Y > 0 usar (0, L), si no (−L, 0); luego comprobar el cuadro delimitador y moverla
  sobre su apoyo si salió corrida.
- Salida del nodo: cantidades creadas y avisos completos (traceback) para corregir sin adivinar.
- Lo que no es arquitectura (instalaciones, juegos, bancas, portones, letras, tanques, canchas) va en el IFC complementario
  vinculado origen a origen.
- Visualización: estilo Realista o Sombreado y **quitar Show Edges** (las líneas blancas eran aristas); los árboles RPC se ven
  reales solo con **Accelerated Graphics apagado** (Opciones > Gráficos).
### 5.3 Lumion, Twinmotion o Enscape (render en el equipo del usuario)
- **Desde Revit (lo más limpio)**: con el modelo nativo y el IFC complementario vinculado, usar **LiveSync** de Lumion (o el
  botón Twinmotion / Enscape de Revit). Los materiales llegan con su nombre (siglas del proyecto + código del cuadro de
  acabados) y se reemplazan por materiales realistas del mismo color exacto: pintura mate, concreto con juntas, cobertura
  metálica o de teja, pasto 3D solo en las áreas verdes, arena donde hay achurado, vidrio y aluminio, metal de portones.
- **Desde Blender**: exportar en **FBX** (o COLLADA .dae) con un material por superficie y nombres claros, escala en metros, sin
  vegetación del entorno ni pasto de partículas. Los árboles del lote se reemplazan por los de la biblioteca en las mismas
  posiciones (entregar la lista de coordenadas).
- Entregar un **LEEME** con: qué archivo importar, origen y unidades, tabla material → acabado sugerido con el RGB de cada color,
  lista de vistas aprobadas (posición de cámara y objetivo) y lo que se debe revisar.
- No prometer que el resultado se ve igual en todos los equipos: depende de la tarjeta de video y de los materiales que elija el
  usuario; el modelo y los colores sí deben ser exactos.
### 5.4 Fidelidad al plano, lámina por lámina ("cada detalle")
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

## 6. Verificación antes de entregar
- [ ] Ningún dato tomado de otro proyecto: colores, alturas, pendientes y medidas trazables a una lámina de este proyecto o a
      una respuesta del usuario.
- [ ] Plantas de control revisadas: cantidad de muros, columnas, puertas, ventanas y sobreluces igual a la de los planos.
- [ ] Colores según el cuadro de acabados; cerco completo incluido el frente; portones del material del plano; nada agregado
      que no esté en el plano ni nada que el usuario haya retirado; sin personas salvo pedido.
- [ ] Verde solo donde hay achurado; instalaciones completas y en su sitio; obras exteriores visibles y con su detalle.
- [ ] Ningún árbol cruza techos ni cerco; nada flota ni se hunde; sombras y exposición sin zonas quemadas.
- [ ] Número y tipo de vistas = lo que pidió el usuario.
- [ ] IFC validado; mismo origen en IFC y Dynamo; script probado al menos con una API simulada y dicho si falta la prueba en Revit.
- [ ] Lista de diferencias entre planos enviada como nota aparte; tabla de fidelidad lámina por lámina (§5.4) sin pendientes.
- [ ] Si va a Lumion / Twinmotion / Enscape: archivo, LEEME con origen, unidades, tabla de materiales con RGB y vistas aprobadas.

## 7. Errores que el usuario ya corrigió (lecciones generales)
- Cerco incompleto: el cerco va en todo el perímetro que dibuja el plano, frente incluido, con el tipo de cierre de su lámina
  (no poner rejas donde el plano dice muro).
- Demasiada área verde: el verde sale solo de los achurados de la planta; lo demás, el piso del cuadro de acabados.
- Elementos inventados (una pérgola, un techo que no estaba): se quitan; se modela solo lo que está en el plano.
- Portones y celosías dibujados como barrotes cuando el plano decía plancha llena: el material es el del plano.
- Instalaciones, bancas y juegos que no se veían, y un patio de juegos que parecía cemento: modelar todo lo que el plano tiene,
  con su piso propio (arena u otro según el achurado).
- "Quita a las personas… hazlo tal cual fielmente": sin personas salvo pedido; instalaciones copiadas del plano, no reinterpretadas.
- Demasiadas vistas de fachada: preguntar cuántas y cuáles; no producir más de las pedidas.
- "Árboles que pasan el techo": regla de copas que no cruzan coberturas ni el cerco.
- Una PTAR modelada con losa cuando era terreno natural: cada obra con su acabado real del plano (solo asoman las tapas).
- Bancas mal orientadas: el mobiliario se orienta y se apoya como en su detalle.
- "Revisa el área de estacionamiento… va cada detalle": cada obra exterior se modela con su lámina.
- IFC4 en Revit solo mostraba líneas → IFC2X3 con sólidos cerrados; aviso de puntos repetidos → lazos limpios.
- Árboles "bola" y caras cuadriculadas → árboles RPC, caras coplanares unidas, Show Edges apagado.
- Cubierta curva fuera de su apoyo → dirección de extrusión según la normal del plano y comprobación final.
- "Can't keep elements joined": dos muros paralelos montados → recortar el más corto y desactivar la unión automática en los extremos.
- "Can't change plane of Opening Cut Sketch": no abrir huecos en una cubierta por huella bajo un sobretecho; modelar sobretecho
  y celosías aparte.
- Tipos de muro, piso y cubierta de varias capas daban error de estructura en Revit → tipos de una capa.

## Ejemplo de referencia (solo ilustrativo; sus valores no se usan en otro proyecto)
Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514): 9 edificaciones (E-01 a E-09), pórtico de ingreso OE-01, losa
deportiva con techo en arco, red de drenaje pluvial completa.
- Colores del cuadro de la arquitecta de ese proyecto: TP-1 guinda RGB 123-31-45 en columnas y vigas; TP-2 gris RGB 125-133-139
  en muros; TP-3 RAL 9010 (RGB 241-236-225) en hastiales, parapeto y cerco (se usó el color del detalle donde la elevación difería).
- Alturas de sus cortes: NPT +0.15; fondo de viga +3.44; nivel superior de viga +3.70 (E-01) y +3.85 (demás); nave alta del SUM
  +5.05; cubiertas a dos aguas al 30 % desde el borde del alero (alero 1.50) al nivel de viga.
- Origen local E 349 090 / N 9 281 900; capas de área verde 0_PASTO 01 / HIERVA y de arena AR-SAND.
- Tipos y materiales con prefijo HR- (HR-Puerta 0.90x2.50; HR TP-1 Guinda, HR Concreto, HR Calamina, HR Área verde).
- Drenaje de ese plano: cunetas de 0.40 libre con muros de 0.10, rejilla de platinas 1" x 3/16" @ 0.025 con ángulo de marco,
  montantes PVC 4" con falsa columna, colector frontal con losa-vereda, juntas de 1" cada 3.0 m.
- Decisiones de ese proyecto: cerco frontal de muro sin rejas; se retiró la pérgola del patio cívico; portones del OE-01 de plancha
  llena; PTAR sobre tierra o hierba; bancas del patio al ras con sardinel detrás; sin personas.
- Serie aprobada en ese caso: 7 aéreas, 3 de fachada, 2 peatonales, una por zona exterior y una planta general.
