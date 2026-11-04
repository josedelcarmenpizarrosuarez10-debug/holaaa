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

## 2. Leer el DXF y modelar el terreno
- Explotar bloques a coordenadas reales. Si el dibujo trae varias copias del conjunto, la real es la que está **sobre las
  curvas de nivel, en UTM**.
- Extraer una base reducida (pickle o JSON) con las capas útiles. El DXF grande no se versiona.
- Terreno: TIN lineal con los vértices de las curvas (`scipy.interpolate.LinearNDInterpolator`). Descartar las z en 0 y las
  etiquetas mal leídas.
- Herramientas: `ezdxf` (lectura y escritura DXF), `shapely` (polígonos, offsets, áreas), `numpy`/`scipy`, `matplotlib`
  (vistas previas), `openpyxl` (Excel con fórmulas), `python-docx` o `docx` de Node (Word).

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

## 5. Sentidos de flujo y descargas
- El agua va hacia los puntos bajos que muestran las curvas. Agrupar la red en **sistemas**, cada uno con su descarga en el
  cerco, del lado más bajo (calle, quebrada o talud).
- No cruzar franjas altas para llegar a una descarga: si la profundidad se dispara, mandar el ramal a otra descarga.
- Todo por **gravedad**, sin bombeo ni contrapendiente.

## 6. Niveles y sección (criterios de Barranquita; confirmar en cada proyecto)
| Concepto | Criterio |
|---|---|
| Sección | Ancho exterior 0.60 = muros 0.10 + 0.40 libres; losa de fondo 0.10; losa tapa 0.10 en tramos tapados. "Mantén la cuneta 0.40 interior y 0.60 total": si no da la capacidad se profundiza, nunca se cambia la sección. |
| Profundidad | 0.30 m al inicio de cada eje; mínima 0.25 (altura libre bajo la losa en tramos tapados). |
| Pendiente de fondo | 0.5 % mínima. Con rasante horizontal, la profundidad crece 0.5 cm por metro. |
| Borde | **Al ras del piso** (NPT), con junta asfáltica al mismo nivel, sin hueco. Áreas verdes 0.05 m bajo el NPT. Patio de maniobra en su nivel, con la cuneta al ras del patio. |
| Llegada al cerco | La cuneta llega al pase con su mismo borde; no "achicarla" ("¿cómo vas a poner 15 cm? ahí se obstruye"). |
| Empalmes | Sin escalón: si un empalme obliga a bajar, el fondo baja parejo desde el nudo anterior. Un ramal puede entregar con caída a otro más profundo. Si V > 3.0 m/s, gradas. |
| Acero | Solo si h ≥ 0.40 m (de la rejilla al fondo) o en tramo tapado; si no, concreto simple. |
| Tapas de inspección | 0.60 × 0.60 en tramos tapados: al inicio, al final, en cada empalme y cada 10 m como máximo. |
| Lloraderos | PVC Ø 3" @ 1.50 m con filtro, solo en los muros de cuneta junto a área verde (si el proyecto los lleva). |

## 7. Hidrología e hidráulica
- **Lluvia**: serie Pmax 24 h medida (25 años). Se procesa con el análisis estadístico en el formato del usuario:
  - Weibull m/(n+1) y prueba de Kolmogorov-Smirnov.
  - Distribuciones Normal, Log Normal, Gumbel (yn/sn de Aparicio) y **Log Pearson III**.
  - Se adopta la de mejor ajuste; en Barranquita fue la LP3.
- **Lluvia de corta duración** por Dick-Peschke e **IDF con el modelo de Bell**.
- **Periodo de retorno y tiempo de concentración**: T = 25 años y tc = 10 min en cunetas.
  - Referencia Barranquita: P24 = 169.27 mm e I = 293.18 mm/h.
  - Riesgo R = 1 − (1 − 1/T)^n.
- **Coeficientes C** (CE.040, Anexo I, Tabla 1.a, T = 25):
  - techo y concreto 0.88; asfalto 0.86;
  - zona verde 0.29 / 0.34 / 0.40 (pasto > 75 % / 50–75 % / < 50 %);
  - C ponderado por superficie medida en el plano.
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
  - Número de montantes por lado = ceil(área del lado / área por montante).

## 8. Verificación: ciclo diseño ↔ verificación hasta 11 de 11
1. Conectividad.
2. Sin contrapendiente.
3. Pendiente mínima.
4. Profundidades (0.30 al inicio, 0.25 mínima).
5. Empalmes.
6. Descargas por el cerco, con el terreno exterior bajo la cota de fondo.
7. NPT.
8. Capacidad.
9. Velocidad ≤ 3.0 m/s.
10. Muros.
11. Todo dentro del cerco.

Si la capacidad no cumple, se profundiza el tramo (se sube la profundidad mínima requerida) y se repite el ciclo hasta que
no cambie. Antes de entregar, revisar varias veces ("revísalo unas 10 veces").

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

## 11. Errores que el usuario ya corrigió (no repetirlos)
- Cunetas fuera del cerco o pozas afuera: no; todo adentro y solo el agua sale por el pase.
- Inventar ejes donde el usuario no trazó: no; sus líneas mandan.
- Bajar el borde de la cuneta 5 cm bajo el piso: no; va al ras, sea tapada o con rejilla.
- Esquinas de 90°: no; chaflán a 45°.
- Achicar la sección al llegar al cerco o cambiar la sección acordada: no; se profundiza.
- Quitar el factor de seguridad 1.15: no.
- Regenerar planos que el usuario ya imprimió: no.
