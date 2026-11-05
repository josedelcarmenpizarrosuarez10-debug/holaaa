---
name: planteamiento-drenaje-pluvial
description: Plantear el drenaje pluvial de un local (colegio, CAR, hogar, posta, municipio) a partir del plano general en DXF con topografía - red de cunetas con rejilla bajo cada caída de techo, cerco como límite, descargas por gravedad, cotas de fondo, hidrología (serie Pmax 24 h, Log Pearson III, IDF), método racional por tramo, 11 comprobaciones, láminas DXF a escala real y expediente (memorias, especificaciones, metrado). Usar cuando el usuario pida un planteamiento o expediente de drenaje pluvial o de cunetas para un proyecto nuevo. Referencia completa - I.E. N.° 0590 Barranquita (Lamas, San Martín).
---
# Planteamiento de drenaje pluvial con cunetas sobre terreno

Método probado en la I.E. N.° 0590 Barranquita (Lamas, San Martín) y en los CAR de Morales. El detalle completo de cada
decisión, con sus números, está en `referencias/04_cunetas_sobre_terreno_BARRANQUITA.md` (red, cotas, comprobaciones,
láminas) y `referencias/02_hidrologia_e_hidraulica.md` (lluvia, C, caudales, Manning, canaletas y montantes). Leer el
capítulo del tema antes de diseñar, dibujar o redactar.

## 0. Reglas permanentes del usuario (no negociables)
- Todo en español. Entregables en **Word, Excel y DXF**; vistas previas en **PNG**; PDF solo si lo pide.
- **Escala real: 1 unidad = 1 m.** "Si algo mide 0.56, así debe medir en el plano."
- Decir siempre **"cota de fondo"** (nunca "cota de solera" ni "invert").
- Nada en los documentos que revele el uso de IA. Nombre y CIP del proyectista: **campos en blanco**.
- Citar el proyecto por su nombre completo y su CUI (o código de inversión).
- No modificar los metrados ni documentos del usuario salvo pedido expreso; cambiar solo lo pedido y verificar que lo demás
  quede idéntico.
- Partidas con nombres y estructura **Delphin**; cantidades siempre del metrado propio. Precios reales con su fuente.
- **Cuando el usuario imprime los planos, ya no se regeneran**: los cambios posteriores van a los documentos y se le avisan.
- Actualizar todo lo relacionado de forma coherente: metrado ↔ planos ↔ especificaciones ↔ memorias.

## 1. Pedir al inicio (insumos)
1. **Plano general en DXF** con topografía (curvas de nivel en UTM), cerco, edificaciones, techos (proyecciones, caídas,
   cumbreras), veredas, pisos, áreas verdes, patio de maniobra y textos de NPT. Suele pesar 300 MB o más y llegar en un ZIP
   en partes: el orden de las partes puede no ser el del nombre (probar).
2. Nombre completo del proyecto, CUI, ubicación (distrito, provincia, región) y entidad (para carátulas y encabezados).
3. Si el usuario dibuja los **ejes de cuneta** (en Barranquita: líneas magenta en la capa 0, a los lados de cada bloque),
   **esas líneas mandan**: copiarlas tal cual a un JSON y no moverlas ni juntarlas.
4. Lluvia: estación SENAMHI más cercana y representativa con **serie Pmax 24 h** (25 años completos más recientes). Si no hay,
   proponer estaciones y pedir la serie; la transposición desde otra estación solo como contraste.
5. Foto del proyecto o vista aérea, para las carátulas.
6. Preguntar lo dudoso **antes** de diseñar y con una imagen de control (PNG): cerco, NPT, receptor de cada descarga, qué
   superficies son verdes o de concreto.
7. Niveles: NPT único o por **plataformas** (terrenos muy desnivelados: 1 a 4, cada una con su NPT y el rebaje del borde),
   nivel del área verde, rampas (nivel de inicio y de fin) y escaleras. Si el NPT parece de otro plano o es cota relativa
   (habría que subirlo más de 3 m para salir por gravedad), pedir que se revise el dato.
8. Solo si no hay salida por gravedad: test de percolación y profundidad de la napa (pozos de absorción) o cota y longitud de
   entrega (bombeo). Para el mapa de ubicación: foto aérea con las coordenadas UTM de sus esquinas, si la hay.

## 2. Leer el DXF y modelar el terreno
- Explotar bloques a coordenadas reales. Si el dibujo trae varias copias del conjunto, la real es la que está **sobre las
  curvas de nivel, en UTM**.
- Extraer una base reducida (pickle o JSON) con las capas útiles. El DXF grande no se versiona.
- Terreno: TIN lineal con los vértices de las curvas (`scipy.interpolate.LinearNDInterpolator`). Descartar las z en 0 y las
  etiquetas mal leídas.
- Herramientas: `ezdxf` (lectura y escritura DXF), `shapely` (polígonos, offsets, áreas), `numpy`/`scipy`, `matplotlib`
  (vistas previas), `openpyxl` (Excel con fórmulas), `python-docx` o `docx` de Node (Word).
- Bloques insertados en espejo (escala X = −1): convertir sus entidades de OCS a WCS; si no, los techos caen fuera del plano.
- Sin curvas en el DXF: terreno en LandXML transformado al plano.

## 2b. Mapa de superficies (confirmarlo antes de diseñar)
- Todo el cerco queda repartido en superficies **sin montajes ni huecos**: la suma de áreas = área del cerco. La franja de cada
  cuneta (0.60 m) recorta las superficies de piso; cada ajuste se informa.
- Tipo de cada área, por prioridad: asignación manual > leyenda de colores o capas de sombreados > superficie con nombre (losa
  techada, patio cívico) > capa > rótulo del plano (AREA VERDE, VEREDA, ESTACIONAMIENTO…) > tipo por defecto confirmado. Franjas
  sin tipo de menos de 0.35 m de ancho o 1 m² (sardineles, juntas) toman el tipo de la vecina con más borde común.
- Lo que no se identifica queda **"sin asignar"** y el diseño no corre hasta que el proyectista lo asigne. Entregar una imagen de
  control por tipo de superficie.

## 3. Límite de intervención (regla fija)
- El **cerco perimétrico es el límite**: ninguna cuneta ni obra fuera del cerco (comprobación 11: bordes del eje ± 0.30
  dentro del cerco). Solo el **agua** sale, por un **pase en el cimiento del cerco** (descargas D1, D2, …).
- Cuneta perimetral con el eje a 0.60 m del cerco (borde exterior a 0.30 m).
- Afuera del cerco el terreno es el natural de las curvas: en cada descarga el terreno exterior debe quedar **bajo la cota de
  fondo de salida**. No excavar afuera; a lo sumo perfilar unos decímetros, y decirlo. Sin pozas, salvo que no haya otra
  salida. Si la salida da a un talud o una quebrada, recomendar protección contra la erosión.

## 4. Dónde va cuneta
- **Una cuneta bajo cada caída de techo.**
  - **Techo a dos aguas**: la cumbrera va en el eje largo y hay cuneta a **ambos lados** del bloque, una por alero.
  - **Techo a una agua**: cuneta solo del lado bajo.
  - Cada caída lleva su canaleta y su montante, y la cuneta va debajo, a lo largo de ese lado.
- Quitar las cunetas que no tengan línea del usuario. Solo se agregan las uniones necesarias hasta las descargas.
- **Tramos tapados** (losa de 0.10) donde la cuneta cruza veredas, ingresos, pasadizos y el pase del cerco. El resto va
  **abierto con rejilla** de platinas.
- **Quiebres a 45° en planta**: en cada esquina con giro mayor de 50°, un chaflán de 0.60 m por lado (como máximo la mitad
  del tramo vecino). Los ejes que llegan entran en diagonal (unión en Y). En los perfiles no se dibujan. La esquina de 90°
  provoca resalto hidráulico.
- **Variante aceptada (25-10-2026)**: la cuneta puede ir a lo largo del alero o **transversal**, por los lados cortos, recibiendo
  los montantes de las esquinas (como en el CAR Varones). Lo que importa es que el tubo de cada montante llegue (≤ 5 m). Buscar
  el menor uso de cunetas largas (salen muy profundas o no llegan) y que empiecen lo menos profundas posible; dos techos vecinos
  comparten la cuneta del espacio entre ellos. Orden: primero edificaciones y losa deportiva; después entradas y obras exteriores.
  Si el usuario ya trazó su planteamiento, se respeta.
- Uniones que agrega la red: perpendiculares a la cuneta que recibe o en prolongación, o por un camino perimetral a 0.60 m del
  cerco; nunca cruzan edificaciones, losas, escaleras ni otras cunetas; a 0.30 m como mínimo de los edificios.

## 4b. Montantes, sumideros, lloraderos y llegada de tuberías (usuario, 24 y 25-10-2026)
- **Montantes** pegados a la esquina de la edificación, en su falsa columna adosada al muro (0.20 × 0.15 × 1.30): por defecto 2
  por lado (4 por edificación a dos aguas). **Siempre de 4", nunca 6"**: si el área lo pide se ponen más de 4" (hasta 4 por lado,
  sobre todo en losas deportivas). Techos en L o con entrantes: el alero de cada mitad solo donde hay techo; 1 montante si el
  alero mide menos de 3 m. El proyectista puede moverlos, quitarlos o agregarlos y se diseña con los que deje.
- Salida del montante: codo de 90° de 4" en el dado y tubo PVC 4" embebido hasta la cara interior de la cuneta, **máximo 5 m**,
  al **1 % (mínimo 0.5 %)**, con su fondo a 0.20 m bajo el piso (0.15 si hace falta).
- **Llegada de tuberías** (montante o sumidero): el fondo del tubo llega **sobre el nivel del agua** de la cuneta en ese punto
  (cota de fondo + tirante) **+ 0.05 m**. Si llega a la cota de fondo, al llover queda ahogado, el agua se empoza y regresa. Si no
  se da: 0.5 %, tubo más alto, otra cuneta y, como último recurso, profundizar el tramo que lo recibe (sin pasar de 1.00 m).
- **Sumideros de piso** solo en áreas libres pavimentadas sin cobertura (patio, patio de maniobra, estacionamiento); nunca en
  área verde, vereda ni bajo techo; el área de juegos queda fuera hasta que el usuario lo decida. Solo donde la zona queda a más de
  8 m de una cuneta (lo cercano escurre a la cuneta); zonas < 20 m² o con < 10 m² lejos: sin sumidero. Tubo PVC 4" recto a la
  cuneta más cercana (no al tramo de la descarga), 1 % (mínimo 0.5 %); si se mueve el sumidero, el tubo se vuelve a trazar.
- **Lloraderos por lado**: cada lado de cada tramo se revisa con el mapa de superficies; solo el muro que toca área verde lleva
  lloraderos (los dos si ambos lados dan a verde); el que da a vereda, patio o pavimento no. PVC Ø 3" @ 1.50 m,
  N.° = REDONDEAR.MAS(L/1.50), con caja filtrante de 0.30 × 0.30 de grava envuelta en geotextil detrás de cada tubo (para que no
  pasen limos). **Con lloraderos no se usan drenes franceses.**

## 5. Sentidos de flujo y descargas
- El agua va hacia los puntos bajos que muestran las curvas. Agrupar la red en **sistemas**, cada uno con su descarga en el
  cerco, del lado más bajo (calle, quebrada o talud).
- No cruzar franjas altas para llegar a una descarga: si la profundidad se dispara, mandar el ramal a otra descarga.
- Todo por **gravedad**, sin bombeo ni contrapendiente. **"Toda cuneta enterrada está prohibida"**: cada descarga necesita el
  terreno exterior bajo la cota de fondo a 2 m o menos del cerco; se eligen las menos descargas que cubren todas las líneas sin
  pasar la profundidad objetivo de **1.00 m**. Si una parte no tiene salida, no se entrega el diseño: se dice cuántos metros quedan
  sin salida.
- El agua va siempre de la plataforma alta a la baja: una zona que solo saldría subiendo de plataforma lleva su propia descarga.
- Sin salida por gravedad: diseñar lo que sí sale, calcular cuánto subir el NPT y **verificarlo rediseñando** con ese nivel
  ("subir el nivel de piso 0.55 m: verificado"). Solo si ningún nivel razonable sirve: descarga a un colector o canal existente, o
  descarga sin gravedad (CE.040, art. 21) con pozos de absorción (IS.020: f = 0.6/t/FS; vaciado del 50 % en ≤ 24 h; fondo 2 m sobre
  la napa; D ≥ 1 m; 6 m entre pozos; t > 12 min/cm no apto) o cámara de bombeo (IS.010, OS.080: dos bombas alternadas, ciclos de
  10 min, impulsión PVC con V ≤ 2 m/s). Con descarga sin gravedad la cuneta puede bajar hasta 1.50 m.

## 6. Niveles y sección (criterios de Barranquita; confirmar en cada proyecto)
| Concepto | Criterio |
|---|---|
| Sección | Ancho exterior 0.60 = muros 0.10 + 0.40 libres; losa de fondo 0.10; losa tapa 0.10 en tramos tapados. "Mantén la cuneta 0.40 interior y 0.60 total": si no da la capacidad se profundiza, nunca se cambia la sección. |
| Sección (criterio general, 24-10-2026) | Muros 0.10 y losas 0.10 fijos. Libre mínimo 0.30 × 0.30, de 5 en 5 cm, **máximo 0.40 libre (0.60 total)**: "0.50 libre y 0.70 total es exagerado"; si el caudal pide más, se profundiza. Total = libre + 0.20; excavación = altura libre + 0.10 de losa + 0.10 de solado. **Una sola medida por sector** (ejes que salen por la misma descarga: la mayor que pida cualquiera de sus tramos), sin mezclar 0.30 y 0.40 en tramos seguidos ni angostar aguas abajo. Tirante ≤ ancho; sin límite de profundidad respecto al ancho ("la regla es que no quede enterrada la cuneta"). Nada que no se pueda encofrar ni acabar (0.20 × 0.20). El programa propone; el dimensionamiento final lo adopta el proyectista (hoja DIMENSIONAMIENTO, columna ADOPTADO) y se verifica. Barranquita: D1 y D2 0.40 libre, D3 0.30. |
| Profundidad | 0.30 m al inicio de cada eje; mínima 0.25 (altura libre bajo la losa en tramos tapados). |
| Pendiente de fondo | 0.5 % mínima. Con rasante horizontal, la profundidad crece 0.5 cm por metro. Fuera de las estructuras el fondo no baja más de 2 % (se profundiza empezando antes). La profundidad inicial puede ser mayor que la mínima. Profundidad máxima objetivo 1.00 m. |
| Borde | **Al ras del piso** (NPT), con junta asfáltica al mismo nivel, sin hueco. Áreas verdes 0.05 m bajo el NPT. Patio de maniobra en su nivel, con la cuneta al ras del patio. Rebaje de 5 o 10 cm solo si el proyectista lo indica para ese eje o plataforma; en rampas el borde sigue la pendiente; por escaleras nunca pasa una cuneta. |
| Estacionamiento | Nunca rejilla: siempre cuneta tapada con losa de concreto armado f'c 280 para la rueda del camión HL-93 (72.5 kN, IM 33 %, factor 1.75); para 0.40 libre: e = 0.15 con Ø 1/2" @ 0.175 en ambos sentidos. |
| Llegada al cerco | La cuneta llega al pase con su mismo borde; no "achicarla" ("¿cómo vas a poner 15 cm? ahí se obstruye"). |
| Empalmes | Sin escalón: si un empalme obliga a bajar, el fondo baja parejo desde el nudo anterior. Un ramal puede entregar con caída a otro más profundo. Si V > 3.0 m/s, gradas. |
| Acero | Solo si h ≥ 0.40 m (de la rejilla al fondo) o en tramo tapado; si no, concreto simple. |
| Tapas de inspección | 0.60 × 0.60 en tramos tapados: al inicio, al final, en cada empalme y cada 10 m como máximo. |
| Lloraderos | PVC Ø 3" @ 1.50 m con caja filtrante 0.30 × 0.30 de grava y geotextil, solo en los muros de cuneta junto a área verde (§4b). |

### 6b. Cambios de nivel entre plataformas (usuario, 25-10-2026)
| Desnivel del borde | Estructura |
|---|---|
| ≤ 0.15 m | cuneta continua; el desnivel se absorbe en la pendiente (1.5 %, entre 3 y 15 m antes del cambio) |
| 0.15 a 0.50 m | caída corta (escalón en el fondo, losa de fondo reforzada) |
| 0.50 a 1.00 m | caja de caída de concreto armado con poza de disipación |
| > 1.00 m (con muro de contención) | la cuneta de arriba llega al ras hasta la cara del muro, lo atraviesa por un **marco de concreto armado** (no tubería), cae a una **poza de disipación** al pie y sigue la cuneta de abajo |
Poza (USBR, caída vertical, Rand): D = q²/(g·hd³); Ld = 4.30·hd·D^0.27; yp = 1.00·hd·D^0.22; y1 = 0.54·hd·D^0.425;
y2 = 1.66·hd·D^0.27; L = Ld + 6.9·(y2 − y1); profundidad hasta cubrir y2; mínimos 0.60 m de largo y 0.10 m de colchón; f'c 210,
malla 3/8" @ 0.20 en ambos sentidos, e = 0.15. La pendiente del tramo no cuenta la caída (la toma la estructura).

## 7. Hidrología e hidráulica
- **Lluvia**: serie Pmax 24 h medida (25 años), con el análisis estadístico del usuario: Weibull m/(n+1) y Kolmogorov-Smirnov;
  Normal, Log Normal, Gumbel (yn/sn de Aparicio) y **Log Pearson III**; se adopta la de mejor ajuste (Barranquita: LP3).
- **Lluvia de corta duración** por Dick-Peschke e **IDF con el modelo de Bell**.
- **Periodo de retorno y tiempo de concentración**: T = 25 años y tc = 10 min en cunetas.
  - Referencia Barranquita: P24 = 169.27 mm e I = 293.18 mm/h.
  - Riesgo R = 1 − (1 − 1/T)^n.
- **Coeficientes C** (CE.040, Anexo I, Tabla 1.a, T = 25): techo y concreto 0.88; asfalto 0.86; zona verde 0.29 / 0.34 / 0.40
  (pasto > 75 % / 50–75 % / < 50 %); C ponderado por superficie medida en el plano.
- **Método racional por tramo**: Q = C·I·A/3.6e6 × **FS 1.15**, un factor de seguridad fijo que el usuario lo exige.
  - Áreas de aporte: malla de 1 m² dentro del cerco; cada celda va al segmento de cuneta más cercano y cada mitad del techo
    a dos aguas, a la cuneta de su lado.
- **Manning**: n = 0.015 para la capacidad y n = 0.013 para la velocidad. Borde libre ≥ 0.05 m y V ≤ 3.0 m/s.
- **Capacidad de la cuneta de 0.40** (S 0.5 %, BL 0.05, n 0.015):

  | h (m) | 0.25 | 0.30 | 0.35 | 0.40 | 0.50 | 0.60 | 0.80 |
  |---|---|---|---|---|---|---|---|
  | Q (L/s) | 81 | 109 | 138 | 167 | 227 | 288 | 413 |

- **Canaletas y montantes**:
  - Canaleta con Manning, n 0.013 y S 1 %.
  - Montantes por Wyly-Eaton: Q (L/s) = 1.754·rs^(5/3)·D^(8/3), con rs 0.25. Un montante de 4" conduce 7.0 L/s; se adopta
    4" como mínimo.
  - Número de montantes por lado = ceil(área del lado / área por montante); a lo más 4 de 4" por lado (con llenado 1/4; si hacen
    falta más, 4 con llenado hasta 7/24).
- **Caudal de cada tramo separado** en techos, pisos y áreas verdes (área y caudal de cada tipo), para la memoria y la revisión.
- **Perfil de flujo** (paso estándar, Chow cap. 10, régimen mixto: subcrítico desde el control de aguas abajo —descarga libre con
  tirante crítico; en una unión, el nivel del agua de la cuneta que recibe—, supercrítico desde aguas arriba). Donde el remanso no
  deja el borde libre, se profundiza el camino hasta la descarga sin pasar del terreno exterior. En tramos tapados el tirante del
  perfil no pasa del 80 % de la altura libre bajo la losa (CE.040, 17.6.2). Comprobación dinámica opcional en EPA SWMM 5 con
  hietograma de bloques alternos de la IDF (caudal pico por descarga y puntos que rebalsan).

## 8. Verificación: ciclo diseño ↔ verificación hasta 11 de 11
1 conectividad · 2 sin contrapendiente · 3 pendiente mínima · 4 profundidades (0.30 al inicio, 0.25 mínima) · 5 empalmes ·
6 descargas por el cerco, con el terreno exterior bajo la cota de fondo · 7 NPT · 8 capacidad · 9 velocidad ≤ 3.0 m/s ·
10 muros (distancia a edificaciones) · 11 todo dentro del cerco.

Si la capacidad no cumple, se profundiza el tramo (se sube la profundidad mínima requerida) y se repite el ciclo hasta que
no cambie. Antes de entregar, revisar varias veces ("revísalo unas 10 veces").
Comprobaciones agregadas después: 12. todas las líneas del usuario quedan con cuneta; 13. secciones constructivas (§6);
14. perfil de flujo con borde libre y tirante ≤ 80 % en tapados. La 10 revisa la distancia a las edificaciones sin contar las
conexiones. Lo que no se resuelve solo **no se esconde**: se informa qué pasó, dónde (E, N), por qué y las soluciones posibles
(aplicar la recomendada, "lo hago a mano", confirmar lo supuesto o dejarlo pendiente) para que el proyectista elija.

## 9. Láminas DXF (estilo del usuario)
- **Escala real**, letra grande y legible, sin textos encimados ni verticales, y concreto con relleno gris. Colores para
  fondo blanco.
- **Planta de cunetas**:
  - rejilla en celeste con las platinas dibujadas (cada 0.10 m), tapada en verde, flechas rojas de flujo;
  - tapas de inspección, descargas D1… en el cerco;
  - curvas de nivel en gris y los NPT.
- **Perfiles longitudinales** 1/50, H = V:
  - guitarra con progresiva, etiqueta, longitud y pendiente;
  - recuadros NCT / NCF / H en cada punto.
- **Secciones** 1/20: piso adyacente con junta asfáltica de 1" al nivel del borde y rejilla de platinas 1" × 3/16" sobre
  ángulo; acero cuando corresponda.
- **Una lámina 1/25 por descarga**: planta, perfil e isométrico con el terreno.
- Cortes generales, detalles (junta, rejilla, tapa de inspección, pase en el cerco, canaleta y montante), leyenda y cuadros.
- **No** hacer el 3D de toda la red (el usuario no lo quiere).
- Juego de cunetas: **U-01 ubicación** (mapas de Perú, departamento, provincia y local con límites reales del INEI, localización
  a escala con cuadrícula UTM verdadera y coordenadas del cerco), DC-01 planta (escala para que el cerco entre en A1; cada eje con su
  ancho libre; lloraderos con su caja filtrante; montantes con su falsa columna; sumideros con su tubo), DC-02 cuadros (ejes: sector,
  L, Q máx, b libre, total, h mín./máx., excavación; descargas; lloraderos; montantes y sumideros), perfiles con la línea de agua,
  secciones, descargas, estructuras de caída y detalles (rejilla, tapa y juntas 1/5; lloradero, falsa columna, canaleta y sumidero
  1/5; montante en elevación y muro con lloraderos 1/10).

## 10. Expediente
- **Word**:
  - memoria hidrológica (con el anexo del análisis estadístico en cuadros);
  - memoria descriptiva;
  - especificaciones técnicas (partidas Delphin);
  - carátulas con la foto del proyecto e índice de planos.
- **Excel**:
  - memoria de cálculo por tramo, con fórmulas;
  - análisis estadístico;
  - metrado por hojas: CONCRETO, ENCOFRADO, ACERO, JUNTA, CURADO, REJILLAS, TAPAS, PARAMETROS, Listas, más RESUMEN y
    PLANILLA;
  - cuadro de tramos.
- Cotejar cada valor de la memoria con su hoja de cálculo (cero diferencias) antes de entregar.
- Cada valor de diseño con su **fuente**: norma (artículo o tabla), referencia técnica o criterio del proyectista, y si ya se
  cotejó con el texto oficial vigente; en la memoria, recuadros de fuente junto a cada cálculo y un anexo de normas. Normas:
  CE.040 (R.M. N.° 126-2021-VIVIENDA, reemplaza a la OS.060), IS.010, IS.020, OS.080, E.020, E.050, E.060, Manual de Hidrología,
  Hidráulica y Drenaje del MTC.
- Memoria descriptiva con cuadro de ubicación (ubigeo, UTM y geográficas) y los 4 mapas en un cuadro de 2 × 2; razonamiento del
  planteamiento por edificación. Una sola cifra de profundidad máxima en todos los documentos.
- Revisión general al final (CUMPLE / NO CUMPLE / AVISO): diseño, componentes, metrado sin errores de fórmula e igual al diseño,
  documentos (español, sin personas ni CIP, metadatos vacíos, sin citas a otros proyectos, láminas citadas existentes), planos y
  entregables pendientes.

## 10b. Lista de comprobación antes de entregar
- [ ] Mapa de superficies cuadrado con el área del cerco y sin áreas "sin asignar".
- [ ] Ninguna cuneta enterrada ni fuera del cerco; descargas con el terreno exterior bajo la cota de fondo.
- [ ] Secciones constructivas, una medida por sector, ≤ 0.40 libre; las 14 comprobaciones cumplen o están explicadas.
- [ ] Cada montante y sumidero llega con su tubo (≤ 5 m, 1 % o 0.5 %) sobre el nivel del agua + 0.05.
- [ ] Lloraderos solo del lado de área verde; estacionamiento tapado con losa vehicular; estructura en cada cambio de nivel.
- [ ] Cifras iguales en planos, metrado, memorias y especificaciones; fuente de cada valor; observaciones abiertas informadas.

## 11. Errores que el usuario ya corrigió (no repetirlos)
- Cunetas fuera del cerco o pozas afuera: no; todo adentro y solo el agua sale por el pase.
- Inventar ejes donde el usuario no trazó: no; sus líneas mandan.
- Bajar el borde de la cuneta 5 cm bajo el piso: no; va al ras, sea tapada o con rejilla.
- Esquinas de 90°: no; chaflán a 45°.
- Achicar la sección al llegar al cerco o cambiar la sección acordada: no; se profundiza.
- Quitar el factor de seguridad 1.15: no.
- Regenerar planos que el usuario ya imprimió: no.
- Proponer 0.50 libre / 0.70 total: "exagerado"; máximo 0.40 libre y se profundiza.
- Secciones de 0.20 × 0.20 o que no se pueden encofrar ni acabar: no.
- Llevar el tubo del montante o del sumidero a la cota de fondo: queda ahogado; llega sobre el nivel del agua + 0.05.
- Drenes franceses junto a cunetas con lloraderos: no; el agua del área verde sale por los lloraderos con su caja filtrante.
- Montantes de 6": no; siempre 4", con más montantes por lado si hace falta.
- Sumideros en área verde, vereda o bajo techo: no.
- Rejilla en estacionamientos: no; cuneta tapada con losa vehicular.
- Dejar sin explicar lo que no se pudo resolver: se muestra con sus soluciones para que decida el proyectista.
