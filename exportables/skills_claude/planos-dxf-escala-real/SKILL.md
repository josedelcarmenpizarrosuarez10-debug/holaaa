---
name: planos-dxf-escala-real
description: "Producir láminas DXF de drenaje pluvial (colector frontal, cunetas, cajas, registros, juntas, lloraderos, canaletas) a escala real (1 unidad = 1 m) con Python y ezdxf: plantas, perfiles longitudinales con guitarra (NCT, NCF, H), secciones, detalles, isométricos, cuadros, rótulo, presentaciones de AutoCAD, índice de planos en Word y vistas previas PNG. Reglas de legibilidad del usuario: sin textos encimados ni verticales, letra grande, concreto con relleno gris sólido, colores para fondo blanco, llamadas sin cruces. Usar siempre que se pida dibujar, corregir, reordenar, imprimir o indexar cualquier plano o lámina DXF de un expediente técnico."
---
# Planos DXF a escala real, ordenados y legibles

Proyectos de referencia (ejemplos, no mezclar datos): CAR Varones (CUI 2705619), Hogar de Refugio Temporal "Mujeres Violentadas"
(CUI 2675514), CAR Mujeres (CUI 2717013), I.E. N.° 0590 Barranquita (C.I. 468901). Detalle completo: `referencias/05_planos_dxf.md`.

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

## 1. Insumos que hay que pedir (no inventar)
- DXF del usuario (arquitectura, topografía, su versión de planos) y su metrado vigente (solo lectura: los cuadros de la lámina
  se leen de la planilla, nunca se recalculan).
- Resultado del diseño (ejes, progresivas, cotas de fondo NCF, NCT, NA, h, secciones, registros, cajas, juntas, descargas).
- Datos del rótulo: nombre completo del proyecto (2 líneas, la 2.ª termina en "CUI N. xxxxxxx"), entidad, ubicación,
  especialidad ("INSTALACIONES SANITARIAS - DRENAJE PLUVIAL"), fecha del rótulo. Proyectista y CIP: siempre en blanco.
- Si la lámina ya está impresa por el usuario: NO se regenera (se le avisa y los cambios van a los documentos).
- Lo que no está en el plano (dónde entrega una cuneta, distancia entre tapas) se propone rotulado "referencial / verificar en
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
  dimblk2=""; `doc.audit()` sin errores antes de guardar; "m2"/"m3" en vez de "²/³" (salían "m?"); diámetro con `%%c`.
- Todo cambio se hace en el script generador y se regenera; nunca a mano en el DXF final.

## 3. Formato, marco y rótulo
| Formato | mm | Uso típico |
|---|---|---|
| A0 | 1189 x 841 | plantas generales muy grandes |
| A1 | 841 x 594 | por defecto |
| A2 | 594 x 420 | perfiles generales cortos, empalmes, cuadros |
| A3 | 420 x 297 | índice de láminas, detalles pequeños |
Tamaño de papel según el dibujo, sin espacios vacíos excesivos. Marco interior x 25..W−10, y 10..H−10 (margen de anillado 25 mm),
polilínea 0.8 mm. Rótulo abajo a la derecha, 185 x 95 mm (x W−195..W−10, y 10..105): PROYECTO (2 líneas), ENTIDAD, UBICACIÓN,
ESPECIALIDAD, PLANO + título (2.4 mm; si pasa de 62 caracteres baja a max(1.5, 2.4·62/len)), subtítulo ≤ 110 caracteres,
`PROYECTISTA: ______  CIP: ____` en blanco, ESCALA ("1/50", "INDICADA", "S/E"), REVISADO en blanco, FECHA, FIRMA Y SELLO en
blanco, REVISIÓN, código de lámina 5.4 mm en la esquina. Nada dibujado encima del rótulo.
Zonas fijas: vistas arriba; leyenda, notas y cuadros en la franja inferior (~110 mm) a la izquierda y al centro.

## 4. Capas y colores (fondo blanco)
| Elemento | ACI / RGB | Grosor (1/100 mm) |
|---|---|---|
| Concreto cortado | contorno 250 + relleno SÓLIDO RGB (226,226,226) | 50 |
| Acero transversal (marcos) | 1 rojo, polilínea de ancho = diámetro real | 35 |
| Acero longitudinal cortado | 5 azul, círculo relleno a diámetro real (3/8" r = 0.00475 m; 1/2" r = 0.00635 m), bloque a escala 1.0 | 35 |
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
- No usar patrones (ANSI31, AR-CONC, EARTH, GRAVEL): en AutoCAD salen sin escala ("se ve horrible"). Grava = piedras de 20–40 mm
  dibujadas a tamaño real; tierra = grupos de 3 trazos inclinados; concreto con hueco = un HATCH con camino exterior e interior.
- Convención del usuario en cunetas: azul = borde NCT tramo abierto (en planta, rejilla celeste RGB 0,170,230 con platinas
  cada 0.10 m); verde = tramo tapado; magenta = losa de fondo NCF; rojo vertical = sección; flechas rojas de flujo.

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
- Las cotas miden el dibujo (texto "<>"). Nunca escribir un número que no corresponde ("pones 3.50 y mide 7.30"). Texto fijo
  solo para pulgadas, alias o vistas ampliadas con su escala declarada en el título (k = esc_lámina/esc_vista).
- Preferir una sola escala por lámina: el usuario se confundió con una vista a otra escala ("¿por qué mide 0.30 si es 0.60?").
- Cotas por fuera: abajo parciales (muro – interior – muro) y total más abajo; a la derecha verticales (fondo – altura – losa) y total.
- Nivel: triángulo + raya y texto "CF 259.100", "NA 259.452", "NPT +260.60". Decir "cota de fondo", nunca "invert".
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

## 8. Cómo se arma cada vista
- **Planta** (1/200 colector, 1/250 cunetas): arquitectura de fondo recortada y gris → límite de intervención (cerco; nada de obra
  fuera de él) → obra a escala real (contornos de cuneta unidos con shapely `buffer(cap_style=2, join_style=2)`, estado por tramo
  rejilla/tapada) → registros exactamente donde entrega cada cuneta → juntas → flechas (cada 5 m y en cada quiebre) → progresivas
  cada 10 m → rótulos → grilla UTM y norte → cuadro de coordenadas (punto, progresiva, E, N, cota de fondo, cota de tapa) → leyenda
  y notas. Quiebres a 45° en planta (chaflán de 0.60 m), que no se muestran en el perfil. Bloques de AutoCAD por tema
  (ARQUITECTURA_BASE, CURVAS_DE_NIVEL, LIMITE_DE_INTERVENCION, CUNETAS_SISTEMA_n, ROTULOS_RED).
- **Perfil longitudinal** (1/50 H = V; 1/25 si la losa mide < 3 mm en papel; ancho útil 800 mm en A1, ejes largos en piezas
  iguales apiladas): agua (relleno entre fondo y NA, termina en la caída), losa de fondo y solado cortados, losa superior con huecos
  de registro, NPT grueso, registros, ventanas de cunetas que llegan, juntas "J", cruces vehiculares, cajas, cotas "h=1.43",
  "S = 0.30 %", terreno existente discontinuo; líneas de cunetas: NCT azul/verde, NCF magenta, sección roja; recuadro por sección
  (25 mm: "SECCION nn", NCT, NCF, H, EL, EM y avisos "Llega EJE-xx", "Descarga D1"). **Guitarra** con columna propia de nombres
  separada por línea vertical: PROGRESIVA, TERRENO, NCT/CARA SUP. DE LOSA, COTA DE FONDO, NIVEL DE AGUA, ALTURA h, PROF. EXCAV.
  (cunetas: Progresiva, Etiqueta, Longitud, Pendiente). Estaciones en extremos, registros, cambios de zona y cada 5 m, omitiendo las
  que quedan a menos de 0.75 m (detalle) o 2.6 m (general). La longitud siempre de sección a sección completa aunque el tramo
  siga en otra pieza. Título: "PERFIL LONGITUDINAL EJE-04 - <descripción> - PROG. 0+000.00 A 0+035.59" (sin "bloque X" ni coordenadas).
- **Sección** (1/15 de a 2 x 2, o 1/20 de a 3; nunca 4 en fila a 1/25; si la vista ocupa < 1/3 de su espacio, subir la escala):
  mirando aguas abajo; concreto en una pieza con hueco y relleno gris; acero con recubrimiento real (nada "al aire", el acero no
  sale del concreto); agua con el Q de ESE tramo; NPT, terreno, excavación, cerco y junta si existen; cotas por fuera; niveles;
  llamadas en columna; título "SECCION S-03" y subtítulo "PROG. 0+020.00 - CF 259.040 - TRAMO NORMAL - ESC. 1/15".
  Cunetas: acero solo si h ≥ 0.40 m o si es tapada; si no, llamada "CONCRETO SIMPLE / SIN ACERO (h < 0.40)".
- **Detalle** (1/10, 1/5, 1/2): una escala por lámina o vistas ampliadas con escala en el título y cotas con texto real; despiece;
  cuadro de componentes por unidad (sirve al ACU: el ACU debe coincidir con el plano); procedimiento en notas; ser fiel al dibujo
  del usuario (no omitir piezas como el colgador).
- **Isométrico**: `u = (x − y)·cos30`, `v = z − (x + y)·sin30`; esa fórmula sale EN ESPEJO para plantas reales: intercambiar
  `(x, y, z) → (y, x, z)` y comprobar con una rosa N/E dibujada igual (mirando desde el sur, el este a la derecha). Teselar caras
  (0.05 m) y pintar por profundidad; sombreado por la normal; aristas en capa aparte; con bloques a 0° y 45° girar la vista 22.5°;
  solo las caras interiores que miran al observador. Color verdadero en cada cara.
- **Cuadros** (acero, metrados, coordenadas, empalmes): valores guardados de la planilla; si guarda fórmulas sin valores,
  recalcular una copia con LibreOffice (`soffice --headless --convert-to xlsx`) y leer con openpyxl `data_only=True`.

## 9. Códigos de lámina y juegos
- Colector: DP-00 índice (A3), DP-01 planta, DP-02 perfil general, DP-03 perfiles de detalle, DP-04 secciones con acero, DP-05
  isométricos de secciones, DP-06A secciones típicas, DP-06B registro y tapa, DP-06C empalme de cuneta, DP-07 cajas, DP-08 cuadros,
  DP-09/DP-10 isométricos; DA detalle de partidas; DD detalles constructivos; DJ juntas y rejilla; DL lloraderos; DS sumidero; DR red de techo.
- Cunetas sobre terreno: DC-00 índice, DC-01 planta, DC-02 secciones típicas, perfiles, secciones, cortes, descargas; numeración
  correlativa sin saltos (si cambia la cantidad de perfiles, se renumeran las siguientes).
- Juegos renombrados por el usuario (p. ej. DPL-01 a DPL-42, DPLV-01 a DPLV-44, incluso con erratas como "DPVL-09"): se respetan
  tal cual en índices y documentos.

## 10. Presentaciones, índice y PNG
- Modelo configurado en A1 con "DWG To PDF.pc3" (evita "Paper Size Not Found"); una presentación por lámina con su código:
  `layout.page_setup(size=(W, H), margins=(0,0,0,0), units="mm", name="ISO_full_bleed_A1_(841.00_x_594.00_MM)", device="DWG To PDF.pc3")`,
  ventana del tamaño del papel centrada en (W/2, H/2) mostrando `(ox + W/2·f, oy + H/2·f)` con `view_height = H·f`, bloqueada
  (`flags |= 16384`); borrar "Layout1". Índice DP-00 en A3: N.° / LÁMINA / DESCRIPCIÓN / FORMATO / ESCALA.
- Instrucción de impresión al usuario: pestaña de la lámina, Ctrl+P, Presentación, escala 1:1, centrar; su plotter con el mismo papel;
  todas juntas con PUBLISH.
- Índice de planos en Word (lo pide aparte): códigos y títulos TAL CUAL el rótulo del PDF del usuario, sin renumerar ni poner
  observaciones; orden que pida el usuario (por número de la primera a la última, o por formato A0 → A3 como su PDF); tabla N.°,
  LÁMINA, DESCRIPCIÓN (título + contenido en gris: secciones, progresivas, cortes), FORMATO, ESCALA; encabezado repetido, filas
  sin partir; total "N láminas (n en A0, n en A1...)". Lectura del PDF: `pdfinfo` (formato), `pdftotext -raw` (rótulo, código).
- Vista previa PNG: `ezdxf.addons.drawing` + matplotlib (Agg), fondo blanco, color real, una sola pasada de `draw_layout` del modelo
  y recorte por la caja de cada lámina; en paralelo con `xargs -P 4`. DXF enormes: recortar a la caja antes (sin hatch) o dibujar
  directo con matplotlib solo las entidades de la caja.

## 11. Verificación antes de entregar (obligatoria)
1. Escala: medir 3 o 4 cotas del dibujo contra el diseño/metrado (ancho total, espesores, h, longitudes); tolerancia 1 mm.
2. Todo dentro del marco interior; nada sobre el rótulo; ninguna entidad fuera de toda lámina.
3. Ningún texto encimado con otro texto, cota o llamada; ninguna línea de llamada cruzada.
4. Ningún TEXT con rotación ≠ 0 salvo progresivas/curvas en planta y cotas.
5. Alturas en papel 1.8–6 mm; losa o muro ≥ 3 mm en papel; barras a diámetro real.
6. Sin amarillo; HATCH sólidos con RGB, sin patrones; capas nuevas con color.
7. Acero dentro del concreto menos el recubrimiento. Nada de obra fuera del cerco.
8. Un mismo elemento igual en planta, perfil, sección, detalle e isométrico; cuadros = planilla; códigos sin saltos.
9. `doc.audit()` sin errores; láminas congeladas comparadas por huella (tipo, capa, punto, texto) antes/después: idénticas.
10. Mirar el PNG de cada lámina tocada; corregir y repetir. Entregar DXF + PNG (no PDF salvo pedido).
11. Un cambio de detalle (p. ej. tapa) obliga a revisar todas las láminas donde aparece y sus leyendas y notas.

## 12. Errores que el usuario ya corrigió (no repetirlos)
- Amarillo en fondo blanco; isométricos negros en el celular (faltaba RGB por entidad).
- Acero longitudinal y transversal del mismo color; barras como "cuadraditos" o sobredimensionadas ("si es 3/8 es 3/8").
- Perfil exagerado en vertical ("si la losa es 0.20 debe ser 20 cm en escala, dibujar con comando L"); agua "metida por debajo".
- Cotas con texto falso ("pones 3.50 y mide 7.30"; "dice que la losa es 0.80").
- Líneas de llamada mezcladas y cruzadas ("usa flechas, acomoda bien"); secciones "todo unido": separarlas, cotas por fuera.
- Acero rojo saliendo del muro en la caja de llegada; huecos/vacíos inexistentes en el isométrico general.
- Detalles de cerco en un proyecto sin cerco; tapas de registro corridas de donde entrega la cuneta; tomar la capa equivocada como cuneta.
- "Letras pequeñitas", textos verticales y encimados en perfiles; láminas en desorden y con espacio vacío ("A1, A2 o hasta A0").
- Láminas sin presentaciones ni índice; "Paper Size Not Found" al imprimir desde el modelo.
- Junta longitudinal dibujada donde hay terreno natural (solo va contra el cerco).
- Colgador omitido en el isométrico; demasiados soportes ("solo 2 soportes en 2 m"); faltaban cortes frontales.
- Obra dibujada fuera del cerco; isométrico 3D de todo el terreno (el usuario no lo quiere); quiebres a 90° (van a 45°, solo en planta).
- "Bloque X y número" en títulos de perfil; longitudes de tramo cortadas por la pieza ("¿por qué dice 31.45?" eran 35.59).
- Acero en cunetas de h 0.30 o 0.36 (solo desde 0.40 o tapada); sección imposible de 0.15 tapada (altura libre ≥ 0.25).
- Vista a otra escala dentro de la lámina sin decirlo; patrones de achurado que en AutoCAD "se ven horribles"; "m³" que sale "m?".
- Índice renumerado, ordenado distinto del PDF del usuario o con observaciones; regenerar planos ya impresos.
