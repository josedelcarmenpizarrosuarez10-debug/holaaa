---
name: planteamiento-drenaje-pluvial
description: "Plantear el drenaje pluvial de cualquier local en el Perú (colegio, CAR, hogar, posta, municipalidad, mercado, etc.) a partir del plano general en DXF con topografía: red de cunetas con rejilla bajo cada caída de techo, cerco como límite, descargas por gravedad, cotas de fondo, hidrología (serie Pmax 24 h de la estación más representativa, Log Pearson III u otra por K-S, IDF), método racional por tramo, comprobaciones de diseño, láminas DXF a escala real y expediente (memorias, especificaciones, metrado). Usar cuando el usuario pida un planteamiento o expediente de drenaje pluvial o de cunetas para un proyecto nuevo o en otra región. Todo dato del proyecto sale de sus planos o se pregunta."
---
# Planteamiento de drenaje pluvial con cunetas sobre terreno

Método general del usuario para cualquier tipo de local y región del Perú. Las referencias traen un caso resuelto como
**ejemplo** (`referencias/04_cunetas_sobre_terreno_BARRANQUITA.md`: red, cotas, comprobaciones, láminas;
`referencias/02_hidrologia_e_hidraulica.md`: lluvia, C, caudales, Manning, canaletas y montantes): de ellas se toma el
método, **nunca sus números**. Las rutas de archivos de las referencias son del trabajo original. Leer el capítulo del tema
antes de diseñar, dibujar o redactar.

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

## 1. Insumos y datos a pedir (todo valor del proyecto sale de aquí; no preguntar lo que ya muestra el plano)
1. **Proyecto**: nombre completo, CUI o código, tipo de local (colegio, CAR, hogar, posta, municipalidad, mercado…), entidad,
   ubicación (distrito, provincia, región), fecha. Sirven para carátulas, encabezados y para sustentar T.
2. **Plano general en DXF** con topografía (curvas de nivel en UTM, con su zona 17 S, 18 S o 19 S), cerco, edificaciones, techos
   (proyecciones, caídas, cumbreras), veredas, pisos, áreas verdes, patio de maniobra, estacionamiento y textos de NPT. Puede pesar
   cientos de MB y llegar en un ZIP en partes (el orden de las partes puede no ser el del nombre: probar). Sin curvas: LandXML.
3. **Ejes de cuneta del usuario**, si los dibujó: preguntar en qué capa y color están. **Esas líneas mandan**: copiarlas tal cual a
   un JSON, sin moverlas ni juntarlas.
4. **Niveles**: NPT único o por **plataformas** (cada una con su NPT y el rebaje del borde), nivel del área verde, patio de maniobra,
   rampas (inicio y fin) y escaleras. Si el NPT parece de otro plano o es cota relativa (habría que subirlo más de 3 m para salir por
   gravedad), pedir que se revise el dato.
5. **Superficies**: qué es techo, concreto, asfalto, área verde (y su cobertura de pasto), estacionamiento y área de juegos.
6. **Techos**: tipo de caída (dos aguas o una agua), canaletas y montantes previstos por arquitectura, falsas columnas.
7. **Descargas**: qué hay afuera del cerco en cada lado bajo (calle, cuneta vial, quebrada, colector o canal existente) y su cota.
8. **Lluvia**: serie **Pmax 24 h certificada** (≥ 25 años completos más recientes) de la estación elegida por **cercanía y
   representatividad** (misma cuenca o subcuenca, altitud y régimen de lluvias parecidos, serie larga y completa). Si no la tiene,
   proponer las estaciones candidatas con distancia y diferencia de altitud y pedirle la serie (detalle en `hidrologia-drenaje-pluvial`).
9. **Criterios por defecto a confirmar** (§6): sección, profundidad inicial, pendiente, borde, T, FS. Si la entidad o el proyecto
   pide otros, mandan los del proyecto.
10. Accesos vehiculares (camiones, autos, motos) y zonas de carga; plantillas del usuario (metrado, memorias, carátulas).
11. Foto del proyecto o vista aérea (carátulas) y, si la hay, con las coordenadas UTM de sus esquinas (mapa de ubicación).
12. Solo si no hay salida por gravedad: test de percolación y profundidad de la napa (pozos) o cota y longitud de entrega (bombeo).
13. Si ya imprimió láminas de este proyecto: cuáles (no se regeneran).
Preguntar lo dudoso **antes** de diseñar y con una imagen de control (PNG): cerco, NPT, receptor de cada descarga, superficies.

## 2. Leer el DXF y modelar el terreno
- Explotar bloques a coordenadas reales. Si el dibujo trae varias copias del conjunto, la real es la que está **sobre las
  curvas de nivel, en UTM**. Bloques en espejo (escala X = −1): pasar sus entidades de OCS a WCS.
- Extraer una base reducida (pickle o JSON) con las capas útiles; el DXF grande no se versiona.
- Terreno: TIN lineal con los vértices de las curvas (`scipy.interpolate.LinearNDInterpolator`); descartar z en 0 y etiquetas mal leídas.
- Herramientas: `ezdxf`, `shapely`, `numpy`/`scipy`, `matplotlib` (vistas previas), `openpyxl` (Excel con fórmulas), `python-docx`
  o `docx` de Node (Word).

## 2b. Mapa de superficies (confirmarlo antes de diseñar)
- Todo el cerco queda repartido en superficies **sin montajes ni huecos** (suma de áreas = área del cerco). La franja de cada cuneta
  recorta las superficies de piso; cada ajuste se informa.
- Tipo de cada área, por prioridad: asignación manual > leyenda o capas de sombreados > superficie con nombre > capa > rótulo del
  plano (AREA VERDE, VEREDA, ESTACIONAMIENTO…) > tipo por defecto confirmado. Franjas sin tipo de menos de 0.35 m o 1 m² toman el tipo
  de la vecina con más borde común.
- Lo no identificado queda **"sin asignar"** y el diseño no corre hasta que se asigne. Imagen de control por tipo de superficie.

## 3. Límite de intervención (regla fija)
- El **cerco perimétrico es el límite**: ninguna cuneta ni obra fuera (bordes del eje ± medio ancho dentro del cerco). Solo el
  **agua** sale, por un **pase en el cimiento del cerco** (descargas D1, D2, …). Sin cerco: el lindero que indique el usuario.
- Cuneta perimetral con el eje a un ancho de cuneta del cerco (borde exterior a medio ancho).
- Afuera el terreno es el natural: en cada descarga el terreno exterior debe quedar **bajo la cota de fondo de salida**. No excavar
  afuera (a lo sumo perfilar unos decímetros, y decirlo). Sin pozas salvo que no haya otra salida. Salida a talud o quebrada:
  recomendar protección contra la erosión.

## 4. Dónde va cuneta
- **Una cuneta bajo cada caída de techo**: dos aguas → a **ambos lados** (una por alero); una agua → solo del lado bajo. Cada
  caída lleva canaleta y montante, y la cuneta va debajo, a lo largo de ese lado.
- Quitar las cunetas sin línea del usuario (si las dibujó); solo se agregan las uniones necesarias hasta las descargas.
- **Tramos tapados** (losa 0.10) donde cruza veredas, ingresos, pasadizos y el pase del cerco; el resto **abierto con rejilla**.
- **Quiebres a 45° en planta**: en cada esquina con giro mayor de 50°, chaflán de 0.60 m por lado (como máximo la mitad del tramo
  vecino); los ejes que llegan entran en diagonal (unión en Y). No se dibujan en perfiles. La esquina de 90° provoca resalto.
- Variante aceptada: la cuneta puede ir a lo largo del alero o **transversal** (lados cortos), recibiendo los montantes de las
  esquinas, siempre que el tubo de cada montante llegue (≤ 5 m). Buscar el menor uso de cunetas largas y que empiecen lo menos
  profundas posible; dos techos vecinos comparten la cuneta del espacio entre ellos. Orden: edificaciones y losas deportivas,
  luego entradas y obras exteriores. Si el usuario ya trazó su planteamiento, se respeta.
- Uniones: perpendiculares a la cuneta que recibe o en prolongación, o perimetrales; nunca cruzan edificaciones, losas, escaleras
  ni otras cunetas; a 0.30 m como mínimo de los edificios.

## 4b. Montantes, sumideros, lloraderos y llegada de tuberías (criterios por defecto del usuario)
- **Montantes** en la esquina de la edificación, en falsa columna adosada (0.20 × 0.15 × 1.30): por defecto 2 por lado. **Siempre
  de 4", nunca 6"**: si el área lo pide, más de 4" (hasta 4 por lado). Techos en L: alero de cada mitad solo donde hay techo;
  1 montante si el alero mide menos de 3 m. El proyectista puede moverlos y se diseña con los que deje.
- Salida: codo 90° de 4" en el dado y tubo PVC 4" embebido hasta la cara interior de la cuneta, **máximo 5 m**, al **1 % (mínimo
  0.5 %)**, fondo a 0.20 m bajo el piso (0.15 si hace falta).
- **Llegada de tuberías**: el fondo del tubo llega **sobre el nivel del agua** de la cuneta (cota de fondo + tirante) **+ 0.05 m**;
  si llega a la cota de fondo queda ahogado y el agua regresa. Si no se da: 0.5 %, tubo más alto, otra cuneta y, al final,
  profundizar el tramo que lo recibe (sin pasar la profundidad máxima).
- **Sumideros** solo en áreas pavimentadas sin cobertura (patio, patio de maniobra, estacionamiento); nunca en área verde, vereda ni
  bajo techo; área de juegos solo si el usuario lo decide. Solo donde la zona queda a más de 8 m de una cuneta; zonas < 20 m² o con
  < 10 m² lejos: sin sumidero. Tubo PVC 4" recto a la cuneta más cercana, 1 % (mínimo 0.5 %).
- **Lloraderos**: solo el muro de cuneta que toca área verde (los dos si ambos lados son verdes). PVC Ø 3" @ 1.50 m,
  N.° = REDONDEAR.MAS(L/1.50), con caja filtrante 0.30 × 0.30 de grava en geotextil. **Con lloraderos no se usan drenes franceses.**

## 5. Sentidos de flujo y descargas
- El agua va a los puntos bajos de las curvas. Agrupar la red en **sistemas**, cada uno con su descarga en el lado más bajo.
- No cruzar franjas altas: si la profundidad se dispara, mandar el ramal a otra descarga.
- Todo por **gravedad**, sin bombeo ni contrapendiente. **"Toda cuneta enterrada está prohibida"**: cada descarga necesita el
  terreno exterior bajo la cota de fondo a 2 m o menos del cerco; elegir las menos descargas que cubren todo sin pasar la
  profundidad objetivo (por defecto **1.00 m**). Si una parte no tiene salida, no se entrega: se dice cuántos metros quedan sin salida.
- El agua va de la plataforma alta a la baja; una zona que solo saldría subiendo de plataforma lleva su propia descarga.
- Sin salida por gravedad: diseñar lo que sale, calcular cuánto subir el NPT y **verificarlo rediseñando**. Solo si ningún nivel
  razonable sirve: colector o canal existente, o descarga sin gravedad (CE.040, art. 21) con pozos de absorción (IS.020: f = 0.6/t/FS;
  vaciado del 50 % en ≤ 24 h; fondo 2 m sobre la napa; D ≥ 1 m; 6 m entre pozos; t > 12 min/cm no apto) o bombeo (IS.010, OS.080:
  dos bombas alternadas, ciclos de 10 min, impulsión con V ≤ 2 m/s). Con descarga sin gravedad la cuneta puede bajar hasta 1.50 m.

## 6. Niveles y sección (criterio por defecto del usuario; confirmar en cada proyecto)
| Concepto | Criterio |
|---|---|
| Sección | Ancho total **0.60 = muros 0.10 + 0.40 libres**; losa de fondo 0.10; tapa 0.10 en tapados. Libre mínimo 0.30 × 0.30, de 5 en 5 cm, **máximo 0.40 libre** ("0.50 libre y 0.70 total es exagerado"): si el caudal pide más, se profundiza, nunca se ensancha. Excavación = libre + 0.10 de losa + 0.10 de solado. **Una medida por sector** (ejes de una misma descarga: la mayor que pida cualquier tramo), sin angostar aguas abajo. Nada que no se pueda encofrar ni acabar (0.20 × 0.20). El programa propone; el proyectista adopta y se verifica. |
| Profundidad | **0.30 m al inicio** de cada eje; mínima 0.25 (altura libre bajo la losa en tapados); máxima objetivo 1.00 m. |
| Pendiente | **0.5 % mínima**; con rasante horizontal la profundidad crece 0.5 cm por metro. Fuera de estructuras, fondo ≤ 2 %. |
| Borde | **Al ras del piso** (NPT), con junta asfáltica al mismo nivel. Área verde 0.05 bajo el NPT; patio de maniobra en su nivel. Rebaje de 5 o 10 cm solo si el proyectista lo indica; en rampas sigue la pendiente; por escaleras nunca pasa cuneta. |
| Estacionamiento | Nunca rejilla: tapada con losa de concreto armado para HL-93 (72.5 kN, IM 33 %, factor 1.75); calcular e y acero en cada caso (para 0.40 libre resultó e = 0.15, Ø 1/2" @ 0.175). |
| Llegada al cerco | Con su mismo borde y sección; no "achicarla" ("ahí se obstruye"). |
| Empalmes | Sin escalón: si obliga a bajar, el fondo baja parejo desde el nudo anterior. Un ramal puede caer a otro más profundo. V > 3.0 m/s: gradas. |
| Acero | Solo si h ≥ 0.40 m o tramo tapado; si no, concreto simple. |
| Tapas de inspección | 0.60 × 0.60 en tapados: inicio, final, cada empalme y cada 10 m como máximo. |

### 6b. Cambios de nivel entre plataformas
| Desnivel del borde | Estructura |
|---|---|
| ≤ 0.15 m | cuneta continua; se absorbe en la pendiente (1.5 %, entre 3 y 15 m antes del cambio) |
| 0.15 a 0.50 m | caída corta (escalón en el fondo, losa de fondo reforzada) |
| 0.50 a 1.00 m | caja de caída de concreto armado con poza de disipación |
| > 1.00 m (muro de contención) | llega al ras hasta el muro, lo atraviesa por un **marco de concreto armado**, cae a una **poza** y sigue |
Poza (USBR, caída vertical, Rand): D = q²/(g·hd³); Ld = 4.30·hd·D^0.27; yp = 1.00·hd·D^0.22; y1 = 0.54·hd·D^0.425;
y2 = 1.66·hd·D^0.27; L = Ld + 6.9·(y2 − y1); mínimos 0.60 m de largo y 0.10 de colchón; f'c 210, malla 3/8" @ 0.20, e = 0.15.

## 7. Hidrología e hidráulica (detalle en `hidrologia-drenaje-pluvial`)
- **Lluvia**: serie Pmax 24 h de la estación del proyecto; Weibull m/(n+1) y Kolmogorov-Smirnov sobre Normal, Log Normal, Gumbel y
  Log Pearson III; se adopta la de mejor ajuste (menor D). Corta duración por **Dick-Peschke**; **IDF por Bell** solo para presentar.
- Criterio por defecto: **T = 25 años** y **tc = 10 min** en cunetas; riesgo R = 1 − (1 − 1/T)^n.
- **C** (CE.040, Anexo I, Tabla 1.a, T = 25): techo y concreto 0.88; asfalto 0.86; zona verde 0.29 / 0.34 / 0.40 (pasto > 75 % /
  50–75 % / < 50 %); C ponderado con las superficies medidas en el plano del proyecto.
- **Racional por tramo**: Q = C·I·A/3.6e6 × **FS 1.15** (fijo). Áreas de aporte: malla de 1 m² dentro del cerco, cada celda al
  segmento de cuneta más cercano; cada mitad de un techo a dos aguas, a la cuneta de su lado.
- **Manning**: n 0.015 capacidad, n 0.013 velocidad; **borde libre ≥ 0.05 m**; **V ≤ 3.0 m/s**. Capacidad de la sección por
  defecto (0.40 libre, S 0.5 %, BL 0.05, n 0.015): h 0.25 → 81; 0.30 → 109; 0.40 → 167; 0.50 → 227; 0.60 → 288 L/s.
- **Canaletas** Manning n 0.013, S 1 %. **Montantes** Wyly-Eaton: Q (L/s) = 1.754·rs^(5/3)·D^(8/3), rs 0.25 → 4" = 7.0 L/s
  (mínimo 4"); por lado = ceil(área/área por montante), hasta 4 de 4" (si faltan, 4 con llenado 7/24).
- Caudal de cada tramo **separado en techos, pisos y áreas verdes** para la memoria.
- **Perfil de flujo** (paso estándar, Chow cap. 10, régimen mixto; controles en descargas y uniones): donde el remanso no deja borde
  libre se profundiza el camino a la descarga; en tapados el tirante ≤ 80 % de la altura libre (CE.040, 17.6.2). EPA SWMM 5 opcional.

## 8. Verificación: ciclo diseño ↔ verificación hasta cumplir todas
1 conectividad · 2 sin contrapendiente · 3 pendiente mínima · 4 profundidades (inicial y mínima) · 5 empalmes · 6 descargas por el
cerco con el terreno exterior bajo la cota de fondo · 7 NPT · 8 capacidad · 9 velocidad · 10 distancia a edificaciones (sin contar
conexiones) · 11 todo dentro del cerco · 12 todas las líneas del usuario con cuneta · 13 secciones constructivas · 14 perfil de flujo
con borde libre y tirante ≤ 80 % en tapados. Si la capacidad no cumple se profundiza y se repite hasta que no cambie. Revisar
varias veces ("revísalo unas 10 veces"). Lo no resuelto **no se esconde**: qué pasó, dónde (E, N), por qué y las soluciones
(recomendada, "lo hago a mano", confirmar lo supuesto o dejarlo pendiente) para que elija el proyectista.

## 9. Láminas DXF (estilo del usuario; detalle en `planos-dxf-escala-real`)
- **Escala real**, letra grande, sin textos encimados ni verticales, concreto con relleno gris, colores legibles en fondo blanco.
  Convención de dibujo por defecto (no de acabados): rejilla celeste con platinas @ 0.10, tapado verde, flechas rojas de flujo.
- Planta de cunetas (tapas, descargas D1… en el cerco, curvas en gris, NPT); perfiles 1/50 H = V con guitarra (progresiva, etiqueta,
  longitud, pendiente; NCT / NCF / H); secciones 1/20 con junta asfáltica 1" y rejilla de platinas 1" × 3/16" sobre ángulo; **una
  lámina 1/25 por descarga** (planta, perfil, isométrico); cortes, detalles, leyenda y cuadros. **No** el 3D de toda la red.
- Juego: U-01 ubicación (Perú, departamento, provincia y local con límites del INEI; cuadrícula UTM verdadera), planta, cuadros (ejes,
  descargas, lloraderos, montantes, sumideros), perfiles con línea de agua, secciones, descargas, caídas y detalles. Prefijo y
  numeración de láminas: los que indique el usuario para el proyecto.

## 10. Expediente
- **Word**: memoria hidrológica (anexo del análisis estadístico en cuadros), memoria descriptiva, especificaciones (partidas Delphin),
  carátulas con la foto del proyecto e índice de planos. **Excel**: memoria de cálculo por tramo con fórmulas, análisis estadístico,
  metrado por hojas (CONCRETO, ENCOFRADO, ACERO, JUNTA, CURADO, REJILLAS, TAPAS, PARAMETROS, Listas, RESUMEN, PLANILLA) y cuadro de tramos.
- Cotejar cada valor de la memoria con su hoja de cálculo (cero diferencias). Cada valor con su **fuente** (norma con artículo o
  tabla, referencia técnica o criterio del proyectista). Normas: CE.040 (R.M. N.° 126-2021-VIVIENDA, reemplaza a la OS.060), IS.010,
  IS.020, OS.080, E.020, E.050, E.060, Manual de Hidrología, Hidráulica y Drenaje del MTC; más las que pida la entidad o el tipo de local.
- Memoria descriptiva con ubicación (ubigeo, UTM, geográficas) y los 4 mapas; razonamiento por edificación; una sola cifra de
  profundidad máxima en todos los documentos.
- Revisión general (CUMPLE / NO CUMPLE / AVISO): diseño, componentes, metrado, documentos (español, sin personas ni CIP, metadatos
  vacíos, **sin textos ni datos de otros proyectos**, láminas citadas existentes), planos y pendientes.

## 10b. Lista de comprobación antes de entregar
- [ ] Todos los datos del proyecto (nombre, CUI, NPT, lluvia, superficies, descargas) salen de sus planos o del usuario.
- [ ] Mapa de superficies cuadrado con el área del cerco y sin "sin asignar".
- [ ] Ninguna cuneta enterrada ni fuera del cerco; descargas con el terreno exterior bajo la cota de fondo.
- [ ] Secciones constructivas, una medida por sector; todas las comprobaciones cumplen o están explicadas.
- [ ] Cada montante y sumidero llega con su tubo (≤ 5 m, 1 % o 0.5 %) sobre el nivel del agua + 0.05.
- [ ] Lloraderos solo del lado verde; estacionamiento tapado con losa vehicular; estructura en cada cambio de nivel.
- [ ] Cifras iguales en planos, metrado, memorias y especificaciones; fuente de cada valor; observaciones abiertas informadas.

## 11. Errores que el usuario ya corrigió (lecciones generales)
- Cunetas u obras fuera del cerco, o pozas afuera: todo adentro y solo el agua sale por el pase.
- Inventar ejes donde el usuario trazó los suyos: sus líneas mandan.
- Bajar el borde de la cuneta bajo el piso sin pedido: va al ras, tapada o con rejilla.
- Esquinas de 90°: chaflán a 45°. Achicar la sección al llegar al cerco o cambiar la acordada: se profundiza.
- Quitar el FS 1.15; regenerar planos ya impresos; secciones de 0.50 libre o imposibles de encofrar.
- Tubo de montante o sumidero a la cota de fondo (queda ahogado); drenes franceses con lloraderos; montantes de 6";
  sumideros en área verde, vereda o bajo techo; rejilla en estacionamientos.
- Copiar niveles, lluvias o dimensiones de un proyecto anterior: cada proyecto con sus propios datos.
- Dejar sin explicar lo no resuelto: se muestra con sus soluciones para que decida el proyectista.

## Ejemplo de referencia (solo ilustrativo; reemplazar por los datos del proyecto nuevo)
| Dato | I.E. N.° 0590 Barranquita (Lamas, San Martín) |
|---|---|
| NPT / área verde / patio de maniobra | +184.65 / +184.60 / +184.50 (borde de cuneta al ras de cada uno) |
| Lluvia | Estación Pongo de Caynarachi (SENAMHI 003317), 1989-2013, LP3: P24 (T 25) = 169.27 mm; I10 = 293.18 mm/h |
| Red | 19 ejes, 4 sistemas, descargas D1 a D4 por gravedad; sección 0.40 libre en D1 y D2, 0.30 en D3 |
| Ejes | líneas magenta del usuario en la capa 0 |
