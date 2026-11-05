---
name: renders-revit-modelo-3d
description: "Armar el modelo 3D de un local (CAR, hogar, colegio, centro de salud) a partir de los DXF de la arquitecta y producir renders realistas en Blender Cycles (materiales y colores del cuadro de acabados, pisos y áreas verdes según los achurados de la planta, cerco perimétrico, obras exteriores según sus láminas, drenaje pluvial visible tal cual el plano) y llevarlo a Revit: IFC2X3 con sólidos cerrados para vincular origen a origen y script de Dynamo (nodo Python) con familias nativas (muros, pisos, cubiertas por huella con pendiente, cubierta en arco por extrusión, puertas y ventanas de familias cargadas, árboles RPC). Usar cuando el usuario pida renders, vistas realistas, fotomontajes, modelo 3D, IFC, Revit o Dynamo de un proyecto."
---

# Renders realistas y modelo para Revit desde los DXF de arquitectura

Referencia aprobada: Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514), 9 edificaciones, pórtico de ingreso OE-01,
losa deportiva con techo en arco, red de drenaje pluvial completa. Blender 4.2 LTS (bpy, Cycles) y Revit 2027 con Dynamo.
Desde un chat en la nube no se puede manejar Revit, Lumion ni la GPU del usuario: se entregan los scripts (Blender, IFC, Dynamo)
listos para correr en su equipo, con un LEEME de pasos, y se generan las imágenes donde haya Blender disponible.

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
1. Planta general en DXF con planta de techos (contornos de cobertura), achurados de pisos y áreas verdes, cerco y sus columnas.
2. Plantas, cortes y elevaciones de cada edificación (alturas: NPT, fondo y nivel superior de viga, cumbrera, sobretecho).
3. Cuadro de vanos de puertas y ventanas (láminas de detalle DT: ancho, alto, alféizar, sobreluz) y cuadro de acabados y colores.
4. Láminas de obras exteriores: pórtico de ingreso, cerco, estacionamientos, patio cívico, juegos, biohuerto, punto ecológico,
   tanque elevado, patio de descarga, PTAR, losa deportiva.
5. Plano de drenaje pluvial del proyecto (cunetas, rejillas, sumideros, tapas, canaletas, montantes, colector) si debe verse.
6. Vistas deseadas (cuántas aéreas, de fachada, peatonales), si quiere personas o autos, resolución, y su equipo (GPU, versión de
   Revit). Los DXF pesan cientos de MB: pedir que suba solo los necesarios o que corra el lector en su equipo.

## 2. Lectura de los DXF (un solo dato para render y Revit)
- Coordenadas locales en metros: restar un origen redondo UTM (ej. E 349 090, N 9 281 900) y usar el mismo en Blender, IFC y Dynamo.
- Muros: pares de líneas paralelas de la capa de muros con separación 0.07 a 0.42 m = un muro con su espesor (también los
  interiores), unidos a través de columnas y columnetas. Columnas con su sección de la planta.
- Vanos: bloques indicadores de puerta y ventana de las plantas, pasados a la planta general por coincidencia de muros; el
  tamaño sale del **cuadro de vanos de los DT, que manda** sobre el cuadro de las plantas. Diferencias (cantidades distintas,
  vano sin indicador, código que no está en el cuadro) → lista para confirmar con la arquitecta, nunca inventar en silencio.
- Alturas de los cortes (ejemplo aprobado): NPT +0.15; fondo de viga +3.44; nivel superior de viga +3.70 a +3.85; nave alta +5.05;
  cubierta a dos aguas al 30 % que arranca en el borde del alero al nivel de viga (alero 1.50 si el plano no da otro). Comparar
  cumbreras rotuladas con las que da la geometría y reportar las que no cuadran.
- Pisos: el pasto sale **solo** de los achurados de área verde de la planta (p. ej. capas 0_PASTO 01 / HIERVA); lo demás es concreto
  con juntas; arena solo donde está su achurado (AR-SAND); veredas de su capa. Pavimento = lote − áreas verdes − edificaciones − veredas.
- Hacer una planta de control PNG por edificación (muros, vanos, columnas, techo) y revisarla antes de modelar.

## 3. Escena en Blender (Cycles)
- Materiales con rugosidad y relieve leve: pintura de muros, concreto con bruñas (textura de ladrillo como juntas cada 1.5–2.0 m),
  calamina con ondas según su dirección, vidrio oscuro, aluminio, acero galvanizado, madera, pasto con imagen sin cuadrícula.
- Colores del cuadro de la arquitecta (ejemplo): **TP-1 guinda RGB 123-31-45** en columnas y vigas; **TP-2 gris RGB 125-133-139**
  en muros; **TP-3 RAL 9010 (RGB 241-236-225)** en hastiales, parapeto y cerco. Si las elevaciones y los detalles dan colores
  distintos para un mismo elemento, preguntar (en el ejemplo se usó el del detalle y se dejó anotado).
- Edificaciones: muros con sus vanos, puertas y ventanas del tamaño de los DT, vigas y columnas a la altura de los cortes, cubiertas
  con el contorno de la planta de techos, hastiales en los testeros, cuerpos de distinta altura si los hay, sobretecho y celosías.
- Exteriores **cada uno según su lámina**: pórtico con letras del nombre, cerco en todo el lote (muro y zócalo con columnas,
  juntas), portones de **plancha metálica llena**, estacionamientos con sus coberturas, biohuerto con su techo, patio cívico con
  bancas al ras y sardinel detrás, juegos sobre arena, tanque elevado, PTAR con piso de tierra o hierba (solo asoman las tapas).
- Drenaje **tal cual el plano del usuario** (explotar su bloque de red): cunetas de 0.40 libre con muros de 0.10 y rejilla de
  platinas 1" x 3/16" @ 0.025 con ángulo de marco, sumideros con rejilla, tapas de inspección, flechas de sentido solo en planta,
  canaletas galvanizadas en los aleros, montantes PVC 4" en las esquinas con falsa columna, colector frontal con losa-vereda,
  tapas ciegas y juntas de 1" (transversales cada 3.0 m).
- Árboles: ninguno atraviesa una cobertura ni el cerco (reducir copa o descartar); follaje con hojas; vegetación del entorno aparte.
- Personas y autos solo si el usuario los quiere (en el ejemplo se quitaron las personas).
- Luz y cámara: cielo físico (Nishita) con sol de baja intensidad (0.23) y luz de cielo mayor (1.15) solo en rayos de cámara, nubes;
  AgX "High Contrast", exposición −1.0; 10 rebotes; denoise; muestreo adaptativo; niebla leve de distancia. Cámaras peatonales a
  1.55–1.70 m con focal 18–24 mm; aéreas 30–42 mm; planta ortográfica en formato vertical como el plano. GPU OptiX/CUDA si hay.
- Ejecución en el equipo: `blender -b --factory-startup --python escena.py` (arma y guarda el .blend) y luego
  `blender -b -P render.py -- <vista|serie> 192 1920` (192 muestras, 1920 px, JPG). Primero una prueba a baja resolución.

## 4. Vistas
Serie que el usuario aprobó: 7 aéreas (frontales, posteriores, laterales), **solo 2 o 3 de fachada** (frontal, ingreso,
perspectiva), 2 peatonales entre edificaciones "como alguien parado mirando", patio cívico, administración, SUM y juegos, losa
deportiva, estacionamientos, biohuerto, tanque, patio de descarga y PTAR, y una planta general. Vistas de drenaje si se piden:
cunetas con rejilla, colector frontal, bancas, montante con cuneta, planta de la red sin coberturas ni árboles.
Nombre de archivo con código y lugar (A1_aerea_frontal_suroeste.jpg) y un zip con todas.

## 5. Camino a Revit
### 5.1 IFC (todo el modelo o complemento)
- **IFC2X3 con sólidos cerrados IfcFacetedBrep** (en Revit 2027 el IFC4 con mallas IfcTriangulatedFaceSet vinculado se veía
  solo en líneas). Cada objeto con su clase (IfcWall, IfcColumn, IfcBeam, IfcSlab, IfcRoof, IfcDoor, IfcWindow, IfcPipeSegment,
  IfcFurnishingElement...), color, grupo en un Pset propio e IfcMapConversion con el origen UTM.
- Limpieza de malla: caras coplanares unidas (sin cuadrícula de líneas), sin puntos repetidos en los lazos, superficies abiertas
  con espesor 0.02 para cerrarlas; rejilla aligerada (una platina de cada cuatro, @ 0.10); sin pasto 3D ni vegetación del entorno
  (los árboles van como RPC en Revit). Validar con ifcopenshell (0 errores de esquema, todos los elementos con geometría).
- En Revit: Insertar > Vincular IFC > Posicionamiento **Automático – origen a origen**.
### 5.2 Dynamo con familias nativas
- Un nodo Python Script (PythonNet3 o CPython3) con los datos embebidos en JSON; medidas en metros convertidas a pies. Correr
  **una sola vez** en un proyecto nuevo con plantilla de Arquitectura métrica; si se repite duplica: antes borrar lo creado.
- Cargar antes: puerta simple (Single-Flush), puerta doble de vidrio, ventana corrediza (Sliding) y fija (Fixed, sobreluces),
  columna rectangular y un árbol RPC. Si falta una familia, usar la primera de su categoría o una DirectShape con su material.
- Crea: materiales (TP-1, TP-2, TP-3, concreto, calamina, área verde), tipos propios de **una sola capa** con prefijo (HR-...)
  para muro, piso y cubierta; muros por eje y espesor hasta fondo de viga; vigas encima; columnas; puertas y ventanas alojadas
  en su muro, duplicando el tipo con el ancho y alto del cuadro (HR-Puerta 0.90x2.50); pisos con las áreas verdes como huecos;
  **cubiertas por huella** (NewFootPrintRoof) con pendiente 30 % en los bordes largos; cerco; pórtico; árboles RPC.
- **Cubierta en arco por extrusión** (NewExtrusionRoof sobre un plano de referencia vertical): la extrusión va según la normal
  del plano; si Normal.Y > 0 usar (0, L), si no (−L, 0); luego comprobar el cuadro delimitador y moverla sobre la losa si salió corrida.
- Salida del nodo: cantidades creadas y avisos completos (traceback) para corregir sin adivinar.
- Lo que no es arquitectura (drenaje, juegos, bancas, portones, letras, tanque, estacionamientos, cancha) va en el IFC
  complementario vinculado origen a origen.
- Visualización: Gráficos > estilo Realista o Sombreado y **quitar Show Edges** (las líneas blancas eran aristas); los árboles RPC
  se ven reales solo con **Accelerated Graphics apagado** (Opciones > Gráficos).

## 6. Verificación antes de entregar
- [ ] Plantas de control revisadas: cantidad de muros, columnas, puertas, ventanas y sobreluces igual a la de los planos.
- [ ] Colores según el cuadro; cerco completo incluido el frente; portones llenos; nada que el usuario retiró (pérgola, personas).
- [ ] Verde solo donde hay achurado; drenaje completo y en su sitio; bancas, arena y juegos visibles.
- [ ] Ningún árbol cruza techos ni cerco; nada flota ni se hunde; sombras y exposición sin zonas quemadas.
- [ ] IFC validado; mismo origen en IFC y Dynamo; script probado al menos con una API simulada y dicho si falta la prueba en Revit.
- [ ] Lista de diferencias entre planos enviada como nota aparte para confirmar con la arquitecta.

## 7. Errores que el usuario ya corrigió (no repetirlos)
- Faltaba el cerco frontal: el cerco va en todo el lote; el frente es de muro, **sin rejas** en el ingreso.
- Había demasiada área verde en el centro: el pasto sale solo de los achurados de la planta; lo demás, concreto con juntas.
- Se quitó la pérgola (techo de madera) del patio cívico: es área libre.
- Portones y celosías del pórtico de **plancha metálica llena**, no barrotes ni rejilla.
- No se veían cunetas ni bancas y el área de juegos parecía cemento: agregar cunetas con rejilla, bancas, juegos y piso de arena.
- "Quita a las personas… hazlo tal cual fielmente": sin personas; drenaje copiado del plano, no reinterpretado.
- Pidió solo 3 vistas de fachada (frontal, ingreso y perspectiva), no más.
- "Árboles que pasan el techo": regla de copas que no cruzan coberturas ni el cerco.
- "PTAR… es tierra o hierba nada más": sin losa de concreto; solo tapas visibles.
- "Las bancas están metidas hacia dentro": la banca da al patio, al ras, y el sardinel la rodea por detrás.
- "Revisa el área de estacionamiento… va cada detalle": cada obra exterior se modela con su lámina.
- IFC4 en Revit solo mostraba líneas → IFC2X3 con sólidos cerrados; aviso de puntos repetidos → lazos limpios.
- Árboles "bola" y caras cuadriculadas → árboles RPC, caras coplanares unidas, Show Edges apagado.
- Cubierta en arco fuera de la losa → dirección de extrusión según la normal del plano y comprobación final.
- "Can't keep elements joined": dos muros paralelos montados → recortar el más corto y desactivar la unión automática en los extremos.
- "Can't change plane of Opening Cut Sketch": no abrir huecos en la cubierta por huella bajo el sobretecho; dejar sobretecho y celosías.
- Tipos de muro, piso y cubierta de varias capas daban error de estructura en Revit 2027 → tipos de una capa.
