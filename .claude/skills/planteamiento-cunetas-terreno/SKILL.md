---
name: planteamiento-cunetas-terreno
description: Plantear la red de cunetas pluviales de un local (colegio, CAR, hogar, etc.) a partir del plano general en DXF con topografía: leer curvas de nivel y cotas, modelar el terreno, respetar el cerco como límite de intervención, poner cuneta bajo cada caída de techo, definir sentidos de flujo y descargas por gravedad, cotas de fondo, verificación hidráulica y láminas. Usar en todo proyecto nuevo de cunetas sobre terreno (referencia completa: I.E. N.° 0590 Barranquita).
---
# Planteamiento de cunetas sobre terreno (criterios del usuario)

Implementación de referencia: `herramientas/barranquita/` (I.E. N.° 0590 Barranquita). Detalle de cada decisión en
`BITACORA_CONVERSACION.md` (secciones "Barranquita"). Para metrar usar el skill `metrado-cunetas`; para dibujar, `planos-ordenados`.

## 1. Cargar el plano y la topografía
- El DXF del usuario suele ser enorme (300+ MB, ZIP en partes; el orden de las partes puede no ser el del nombre: probar).
  No versionarlo; extraer una base reducida (`insumos/<proyecto>/base_sitio.pkl`) con las capas útiles: curvas (C-TOPO),
  cerco, edificaciones/techos, veredas, pisos, textos NPT y las líneas que trace el usuario.
- Si el dibujo tiene varias copias del conjunto, la real es la que está **sobre las curvas de nivel, en coordenadas UTM**.
- Bloques explotados a coordenadas reales. Modelo de terreno: TIN lineal de los vértices de las curvas
  (`terreno_b.modelo()`, `LinearNDInterpolator`); revisar cotas de curvas (descartar z de 0 o etiquetas).
- Leer los NPT del plano y preguntar los niveles que falten. Generar una imagen de control (PNG) y confirmar con el usuario
  lo dudoso (cerco, niveles, receptor de cada descarga) antes de diseñar.

## 2. Límite de intervención (regla fija)
- El **cerco perimétrico es el límite**: ninguna cuneta ni obra se dibuja ni se proyecta fuera del cerco (comprobación 11:
  bordes eje ± 0.30 dentro del cerco). Solo el **agua** sale, por un **pase en el cimiento del cerco**.
- Cuneta perimetral con el eje a 0.60 m del cerco (borde exterior a 0.30 m).
- Fuera del cerco, terreno natural de las curvas: en cada descarga el terreno exterior debe quedar **bajo la cota de fondo de
  salida** (no excavar afuera; a lo sumo perfilar unos decímetros, y decirlo). Sin pozas salvo que no haya otra salida.
- Si la salida da a un talud o quebrada, recomendar protección contra erosión (no es obra metrada fuera del cerco).

## 3. Dónde va cuneta (techos y caídas)
- **Una cuneta bajo cada caída de techo.** Techo a **dos aguas** (cumbrera en el eje largo): cuneta a **ambos lados** del bloque,
  una por cada alero. Techo a **una agua**: cuneta solo del lado bajo. Cada caída recibe su canaleta y montante, y la cuneta va
  debajo, a lo largo de ese lado.
- Si el usuario traza líneas (en Barranquita, magenta en capa 0, a los lados de cada edificación), **esas líneas mandan**:
  copiarlas a un JSON en `insumos/` y no mover ni juntar ninguna. Solo se agregan las uniones necesarias hasta las descargas.
  Quitar cunetas que no tengan línea del usuario.
- Tramos **tapados** (losa) donde la cuneta cruza veredas, ingresos o pasadizos; el resto **abierto con rejilla**.

## 4. Sentidos de flujo y descargas
- El agua va hacia los puntos bajos que muestran las curvas; agrupar la red en sistemas, cada uno con su descarga (D1, D2, ...)
  en el cerco, del lado más bajo (calle, quebrada, talud).
- No cruzar franjas altas para llegar a una descarga (si la profundidad se dispara, mandar el ramal a otra descarga).
- Todo por **gravedad**, sin bombeo ni contrapendiente.

## 5. Niveles y sección (criterios del usuario en Barranquita; confirmar en cada proyecto)
- Interior del cerco nivelado: NPT de pisos y pasadizos; **borde de cuneta al ras del piso** (junta asfáltica al mismo nivel,
  sin hueco); áreas verdes 0.05 m abajo; patio de maniobra en su nivel con la cuneta al ras del patio.
- Sección: 0.60 m exterior = muros 0.10 + 0.40 libres. Altura al inicio 0.30 m (mínima 0.25). Pendiente de fondo 0.5 %.
  Con rasante horizontal la profundidad crece 0.5 cm por metro. Tapados: losa 0.10 + altura libre ≥ 0.25.
- La cuneta llega al cerco con su mismo borde (no "achicarla" al pasar).
- Empalmes sin escalón: si un empalme obliga a bajar, el fondo baja parejo desde el nudo anterior; un ramal puede entregar
  con caída a otro más profundo. V > 3.0 m/s: gradas.
- **Quiebres a 45° en planta**: en cada esquina con giro > 50° un chaflán de 0.60 m por lado (máximo la mitad del tramo vecino);
  los ejes que llegan a una esquina entran en diagonal. En perfiles y en la numeración de secciones no se muestran.
- Acero solo con h ≥ 0.40 m (rejilla a fondo) o en tramo tapado; menor, concreto simple.
- Tapas de inspección 0.60 x 0.60 en tramos tapados: al inicio, al final, en cada empalme y cada 10 m como máximo.

## 6. Hidrología e hidráulica
- Lluvia: serie Pmax 24 h medida de la estación más cercana y representativa (25 años completos más recientes); análisis en
  el formato del usuario (hoja ANALISIS ESTADISTICO del CAR Varones: K-S, LP3, Gumbel, IDF de Bell); la transposición de otra
  estación solo como contraste. T = 25 años, tc = 10 min.
- C ponderado por tipo de superficie medida en el plano: techos, áreas libres de concreto, patio/estacionamiento, áreas verdes.
- Método racional por tramo; Manning n = 0.013; capacidad con borde libre ≥ 0.05 m. Si no cumple, primero profundizar el tramo
  (`calcula_b.py` sube la profundidad mínima), no cambiar la sección acordada.

## 7. Verificación (ciclo diseño ↔ verificación hasta 11 de 11)
1 conectividad · 2 sin contrapendiente · 3 pendiente mínima · 4 profundidades (0.30 / 0.25) · 5 empalmes · 6 descargas por el cerco
(terreno exterior bajo la cota de fondo) · 7 NPT · 8 capacidad · 9 velocidad (≤ 3.0 m/s) · 10 muros · 11 todo dentro del cerco.

## 8. Láminas y entregables
- Todo a **escala real** (1 unidad = 1 m). Planta con el estilo del usuario: rejilla celeste con platinas, tapada verde,
  flechas rojas de flujo, tapas de inspección. Perfiles 1/50 H = V con guitarra (progresiva, etiqueta, longitud, pendiente) y
  recuadros NCT/NCF/H; secciones 1/20; una lámina 1/25 por descarga (planta, perfil e isométrico con terreno).
- No hacer el 3D de toda la red (el usuario no lo quiere). Decir siempre "cota de fondo".
- Expediente: memoria hidrológica, memoria descriptiva, especificaciones (Word); memoria de cálculo, análisis estadístico y
  metrado en formato CAR (Excel); carátulas con la foto del proyecto.
- **Cuando el usuario imprime los planos, ya no se regeneran**; cambios posteriores van a los documentos y se le avisan.
