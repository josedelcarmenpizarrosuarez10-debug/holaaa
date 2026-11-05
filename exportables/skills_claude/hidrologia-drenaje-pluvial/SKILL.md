---
name: hidrologia-drenaje-pluvial
description: Calcular la lluvia y los caudales de diseño de un drenaje pluvial en el Perú y redactar la memoria hidrológica (Word) y el análisis estadístico (Excel con fórmulas) en el formato del usuario (serie de precipitación máxima en 24 h, Weibull, Kolmogorov-Smirnov, Normal, Log-Normal, Gumbel y Log Pearson III, Dick-Peschke, IDF por el modelo de Bell, T = 25 años, tiempo de concentración, coeficientes C de la CE.040, método racional con FS 1.15, Manning de cunetas y canaletas, montantes por Wyly-Eaton). Usar cuando el usuario entregue datos de lluvia (SENAMHI u otros), pida la lluvia de diseño, una IDF, los caudales, la memoria hidrológica o el análisis estadístico, o cuando cambie la lluvia y haya que actualizar documentos.
---

# Hidrología del drenaje pluvial y memoria hidrológica

Método del usuario, comprobado en los expedientes de CAR Varones (CUI 2705619), Hogar de Refugio Temporal "Mujeres
Violentadas" (CUI 2675514), CAR Mujeres (CUI 2717013) y la I.E. N.° 0590 Barranquita (C.I. 468901, CUI por confirmar). Detalle
completo en `referencias/02_hidrologia_e_hidraulica.md` (fórmulas, series, resultados, cronología) y
`referencias/08_documentos_del_expediente.md` (§3 estilos Word, §4 memoria hidrológica, §6 memoria de cálculo, §8 Excel del análisis).
Las rutas de archivos de esas referencias son del trabajo original y no existen en este chat.

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

## 1. Datos que hay que pedir
1. Proyecto (nombre, CUI o código, entidad, ubicación, fecha) y uso del local (sustenta T).
2. Serie de lluvia: archivo diario o mensual de la estación más representativa (SENAMHI con o sin encabezado; −99.9, S/D o vacío =
   sin dato; "T" traza = 0.0). Nombre, código, tipo, altitud, coordenadas, distrito/provincia/departamento de la estación.
3. Plantilla de análisis estadístico del usuario (Excel) y su memoria hidrológica modelo (Word), si las tiene: se usan tal cual.
4. Superficies dentro del límite de intervención (techos en proyección horizontal con aleros, áreas libres de concreto,
   estacionamiento/patio de maniobra, áreas verdes) y la red (canaletas, montantes, cunetas, colector).
Si no hay acceso a internet para bajar datos, decirlo y pedir los archivos; nunca rellenar con valores supuestos.
5. Formatos de lluvia diaria que se leen: SENAMHI (txt: año, mes, día, precipitación, tmax, tmin; −99.9 = sin dato), NASA POWER y
   CHIRPS; o las máximas mensuales/anuales ya armadas. El usuario: "las lluvias se compran, no hay así gratis": la serie del
   expediente es la **certificada** de la estación; las fuentes libres (§2b) son solo referenciales o de contraste.
6. Las tablas certificadas del SENAMHI dicen "solo será empleada para el propósito de la solicitud, quedando prohibida su
   reproducción total o parcial": usarlas solo en el proyecto para el que se pidieron; no copiarlas a otros archivos ni programas
   (de ellas solo se guardan factores derivados).

## 2. Conformar la serie (sin inventar datos)
- Máximo de cada mes válido (≥ 20 días con dato) y máximo anual = mayor de los meses disponibles. Año incompleto: se conserva el
  máximo de los meses disponibles y se declara en la memoria; **no se rellenan vacíos** con ceros, promedios ni años vecinos.
- Mínimo 25 años (orientación del Manual de Hidrología, Hidráulica y Drenaje del MTC, 3.4). Si el usuario lo pide: "25 años desde el
  año más reciente hacia abajo" (excluir el último año si solo tiene unos meses).
- Preferir la estación de la misma subcuenca sin transponer. La transposición por lluvia anual sobreestima la máxima diaria (se
  descartó en Barranquita: la estación llovía 3.6 veces más al año pero solo 1.4 veces más en 24 h); dejarla solo como contraste.

## 2b. Serie referencial PISCO-SENAMHI (cuando no hay estación cercana; definida con el usuario, 27-10-2026)
- PISCOp v3.0 del SENAMHI: lluvia diaria grillada de 0.1° (1981-2025), de descarga libre (figshare, DOI 10.6084/m9.figshare.32411886).
  Se reduce a la **máxima en 24 h de cada mes** por celda (mismo formato año × 12 meses de las tablas del SENAMHI) y se toma la celda
  con datos más cercana al distrito o a las coordenadas.
- La grilla promedia ~10 × 10 km y **subestima las máximas puntuales** ("le veo pocos mm para Tarapoto"): se multiplica por el factor
  estación / PISCO = media de las máximas anuales de la estación ÷ media de las de PISCO en su celda exacta (años comunes),
  interpolado por inverso de la distancia al cuadrado. San Martín: CO Tarapoto 1.35, Pongo de Caynarachi 1.28, Chazuta 1.37,
  Lamas 1.57, San Pablo 1.26 (coordenadas exactas de su ficha); Jepelacio 1.33, Sauce 1.33, San Antonio 1.04 (ubicación aproximada).
  A más de 80 km de toda estación el factor es 1.00 y se avisa. Control: Tarapoto 75.0 mm de media de máximas con PISCO corregido
  frente a 76.6 mm de la estación; estimando el factor de cada estación solo con las demás, el error es de 0 a 6 % en 5 de las 8.
- Fichas SENAMHI (para ubicar estaciones): Chazuta 153319 (6°34'16.3" S, 76°7'53.4" W, 203 msnm); Pongo de Caynarachi 003317
  (6°19'49.7", 76°16'54.3", 187); Lamas 000383 (6°25'7.46", 76°31'40.6", 840); Picota 153313 (6°55'11.61", 76°19'48.77", 220);
  San Pablo 153307 (6°48'34.4", 76°34'34.5", 270).
- Es una serie **REFERENCIAL**: escribirlo así; para el expediente vale la serie certificada de la estación más cercana.

## 3. Estadísticos y distribuciones (métodos exactos de la hoja del usuario)
- x̄, s con n − 1, Cs = n·Σ(x − x̄)³/((n − 1)(n − 2)·s³) (= SKEW de Excel), para x, log10 x y ln x.
- z para P = 1/T (Abramowitz-Stegun): w = √(ln(1/P²)); z = w − (2.515517 + 0.802853w + 0.010328w²)/(1 + 1.432788w + 0.189269w² + 0.001308w³).
- Normal: x_T = x̄ + z·s. Log-Normal (log10): x_T = 10^(ȳ + z·s_y).
- Log Pearson III (Kite, k = Cs_log/6): K_T = z + (z² − 1)k + (z³ − 6z)k²/3 − (z² − 1)k³ + z·k⁴ + k⁵/3; x_T = 10^(ȳ + K_T·s_y).
- Gumbel: K_T = −(√6/π)·[0.5772 + ln(ln(T/(T − 1)))]; x_T = x̄ + K_T·s.
- Periodos 2, 5, 10, 20, 25, 50, 100, 200, 500 años; además 6/n y √(6/n) (variación y desviación del coeficiente de asimetría).

## 4. Prueba de Kolmogorov-Smirnov (hoja "C. Prueba Kolmorov-Smirnov", con su errata)
- Serie de MAYOR a menor; excedencia observada de Weibull E_m = m/(n + 1).
- P teórica: Normal 1 − Φ((x − x̄)/s); Log-Normal 1 − Φ((log10 x − ȳ)/s_y); LP3 por gamma de ln P: β = (2/Cs_ln)², α = s_ln/√β,
  δ = x̄_ln − α·β, P = CHIDIST(2(ln x − δ)/α; 2β) con grados de libertad truncados a entero; Gumbel con yn, sn de Aparicio:
  P = 1 − exp(−exp(−(((x − x̄)/s)·sn + yn))). (n, yn, sn): (10, 0.4952, 0.9496) (15, 0.5128, 1.0206) (20, 0.5236, 1.0628)
  (25, 0.5309, 1.0914) (30, 0.5362, 1.1124); interpolar en n.
- D = máx |P − E|; D crítico = √(−ln(α/2)/(2n)) − 1/(6n), α = 0.05 (n 25: 0.2650; n 26: 0.2599).
- Se adopta la de **menor D** entre las aceptadas, y la columna "Diseño" del resumen debe seguir **automáticamente** a la K-S.

## 5. Lluvia de corta duración e intensidad de diseño (Dick y Peschke)
P_D = P24·(D/1440)^0.25 ; I_D = 60·P_D/D (D en min, P en mm, I en mm/h). Forma equivalente: b = ln(P20/P10)/ln 2 (= 0.25);
I = P10·(tc/10)^b/(tc/60). Mostrar siempre la lluvia junto a la intensidad (35.163 mm en 10 min = 210.98 mm/h: mismo dato).

## 6. IDF por el modelo de Bell (solo para presentar; el diseño usa Dick y Peschke)
P60(10) = 0.4602·P24(10)^0.876; P(T, t) = (0.21 ln T + 0.52)(0.54 t^0.25 − 0.50)·P60(10) para t = 5, 10, 15, 20, 30, 60 min y los 9
periodos (en T = 10, t = 60 va P60(10)); I = 60P/t redondeada a 0.1 (Cuadros N.° 04 lluvias, N.° 05 intensidades). Regresión
log I = log K + m log T − n log t con las 3 ecuaciones normales (Cuadro N.° 06); K a 0.01, n = |coef. de log t|. Tabla
I = K·T^m/t^n para t = 10 a 120 min y T = 2 a 100.

## 7. Tiempo de concentración, periodo de retorno y factor de seguridad
- Kirpich tc = 0.01947·L^0.77·S^(−0.385) (min, m, m/m); SCS tc = 0.0195·(L³/H)^0.385 (min, m, m); estimación física = entrada 5 min
  + L/V de las cunetas. Si todo da < 10 min → **tc = 10 min** (mínimo CE.040) para canaletas, montantes, sumideros y cunetas.
- Colector frontal: tc = 10 + ≈ 3 (cuneta) + ≈ 2 (colector) = 15 min. Usar la intensidad de 10 min en el colector supone que todo
  llega a la vez: caudal 35.5 % mayor sin sustento (texto aprobado). Misma intensidad en todos los tramos de un colector compartido.
- T = 25 años (CE.040 11.1 y 11.3; locales con niños, estudiantes o personas protegidas). Riesgo R = 1 − (1 − 1/T)^n (tabla T 5–100,
  n 10, 20, 25, 50). **FS = 1.15 en todos los caudales** (criterio fijo; el usuario lo repuso cuando se quitó).
- Una sola lluvia para todo el proyecto: la intensidad de la IDF del proyecto para el tc de diseño, citando su fuente (análisis
  estadístico de la estación o curva ingresada); avisar si se está usando una curva de ejemplo.

## 8. Coeficientes de escorrentía (RNE CE.040, Anexo I, Tabla 1.a, T = 25)
| Superficie | C |
|---|---|
| Concreto / techo | 0.88 |
| Asfalto | 0.86 |
| Zona verde 0–2 %, pasto > 75 % / 50–75 % / < 50 % | 0.29 / 0.34 / 0.40 |
- Canaletas, montantes, sumideros y cunetas de los CAR: C = 0.88 uniforme (simplificación conservadora, criterio del proyecto).
- Colector o red completa: C ponderado = Σ(C·A)/ΣA. Áreas verdes 0.29 en los CAR; 0.40 en rellenos compactados (Barranquita).
- En redes sobre terreno: malla de celdas de 1 m², cada una asignada al segmento de cuneta más cercano (techo a dos aguas: cada mitad a
  su lado); prioridad techo > pavimento > estacionamiento > verde; acumular aguas abajo sin contar dos veces una superficie.
- Comparación "C 0.88 vs ponderado": (0.88/C − 1)·100 (no copiar el % de otra memoria).

## 9. Caudales y verificación hidráulica
- Q [L/s] = C·I·A·FS/3600 (A en m², I en mm/h) = C·I·A·FS/3.6e6 m³/s; con A en ha, Q = C·I·A/360.
- Cuneta (sección del usuario: 0.40 libre, muros 0.10, total 0.60; S ≥ 0.5 %): Manning con n 0.015 para capacidad y n 0.013 para
  velocidad; y por bisección; cumple si h_disp − y ≥ 0.05 y V ≤ 3.0 m/s (si no, gradas). En tapado h_disp = altura libre bajo la losa
  (≥ 0.25). Si falta capacidad se **profundiza**; nunca se cambia la sección acordada. Capacidad (S 0.5 %, BL 0.05, n 0.015):
  h 0.25 → 81.2; 0.30 → 109.0; 0.40 → 167.0; 0.50 → 227.1; 0.60 → 288.4 L/s.
- Canaleta: Manning rectangular n 0.013, S 1 % (bancas 0.5 %), borde libre 0.05 (0.25 × 0.20 conduce 48.1 L/s).
- Montante (Wyly-Eaton, rs = 0.25): Q (L/s) = 1.754·rs^(5/3)·D^(8/3) (D en pulgadas; o 27.8·rs^(5/3)·D^(8/3) en gpm, 1 L/s = 15.85 gpm);
  D req = (Q/(1.754·rs^(5/3)))^(3/8). 4" = 7.0 L/s, 3" = 3.26 L/s → se adopta 4" (≥ mínimo de la CE.040 12.5). Área máxima por
  montante de 4" = 7.0 / (C·I·FS/3600) m² (ej. 0.88 · 293.18 · 1.15/3600 = 0.0824 L/s por m² → 85.1 m²; montantes por lado = ceil(A/85.1)).
- Montantes por lado: a lo más 4 de 4" (llenado rs 1/4); si hicieran falta más, 4 con llenado hasta 7/24. Nunca 6".
- Caudal de cada tramo de cuneta **separado en techos, pisos y áreas verdes** (área y caudal de cada tipo) en la memoria.
- Perfil de flujo de la red (paso estándar de Chow, régimen mixto, controles en descargas, uniones y caídas, caudal creciente en el
  tramo): donde el remanso no deja el borde libre se profundiza el camino a la descarga. Tramos tapados: tirante ≤ 80 % de la altura
  libre bajo la losa (CE.040, 17.6.2). Comprobación dinámica opcional en EPA SWMM 5: hietograma de bloques alternos de la IDF (bloques
  del tc; Chow, Maidment y Mays), Horton en áreas verdes; resumir continuidad, caudal pico por descarga, rebalses y tramos llenos.
- Descarga sin gravedad (solo si no hay otra): pozos de absorción con tránsito del hidrograma de la tormenta (IS.020: f = 0.6/t/FS en
  m/h, vaciado del 50 % en ≤ 24 h) o cámara de bombeo (IS.010, OS.080). Detalle en el skill `planteamiento-drenaje-pluvial`.
- Lloraderos: no cambian el dimensionamiento (el agua infiltrada ya está en el C de las áreas verdes).
- Colector frontal: perfil, cajas y autolimpieza con el skill `colector-pluvial-frontal`.

## 10. Valores de control (reproducirlos antes de usar el método con datos nuevos)
- Estación CO Tarapoto, 1999–2024 (n 26): x̄ 79.354, s 22.068; K-S Normal 0.0920, Log-Normal 0.0894 (adoptada), LP3 0.0964, Gumbel
  0.1270, crítico 0.2599; P24 T25 = 121.81 mm; P10 35.163 → I10 210.98; I15 155.66 mm/h; Bell K 161.94, m 0.1786, n 0.5271.
- Pongo de Caynarachi (SENAMHI 003317), 1989–2013 (n 25): x̄ 110.31, s 27.56; K-S Normal 0.1304, LN 0.0947, **LP3 0.0683 (adoptada)**,
  Gumbel 0.0775, crítico 0.2650; P24 T25 = 169.27 mm; P10 48.86 → I10 293.18 mm/h; Bell K 211.66, m 0.1786, n 0.5269.
- Caudales compartidos de Morales (I 155.66, FS 1.15): Σ C·A 5,203.32 → 258.7; 6,072.36 → 301.9; 5,274.45 → 262.3 L/s; total 822.9.

## 10b. Drenaje vial (MTC) – solo si el usuario lo pide
El usuario dijo (29-10-2026) que por ahora no trabaja drenaje de carreteras ("no lo veía tan necesario"): no proponerlo. Si lo pide:
Manual de Hidrología, Hidráulica y Drenaje del MTC (R.D. N.° 20-2011-MTC/14); T por riesgo admisible y vida útil (Tabla 02):
plataforma R 40 %, n 15 → 30 años; alcantarillas menores y alivios R 35 %, n 15 → 36; quebradas importantes y badenes R 30 %,
n 25 → 71; C de la Tabla 08; tc de la Tabla 05; racional si A < 10 km², Témez de 10 a 770 km²; Manning con borde libre del 25 %.

## 11. Excel del análisis estadístico (formato del usuario, con fórmulas)
Hojas (nombres tal cual): "A. Estación" (registro mensual, máximos, S/D resaltados), "B.Modelo Distribución" (B.1 Normal, B.2 Log
Normal, B.3 Log Pearson III, B.4 Gumbel), "C. Prueba Kolmorov-Smirnov", "D.Resumen" (C.4), "A. Parametros" (Cuadros 04–06, Bell,
regresión), "B. Int.maxima" (tabla IDF), "C. P diseño" (Dick-Peschke por T), más CARÁTULA. Encabezado Proyecto (con CUI), Entidad,
Ubicación, Fecha. Procedimiento sobre la plantilla del usuario (LibreOffice sin interfaz si hay que automatizar):
1. Escribir encabezado, datos de la estación y periodo; cargar años y 12 meses ("S/D" con el resaltado de la plantilla).
2. **Borrar filas sobrantes** con la herramienta de filas (LibreOffice/Excel ajustan fórmulas y rangos de gráficos); nunca reescribir
   fórmulas a mano. Si sobra un año, eliminar su fila; si falta, insertar dentro del rango.
3. Revisar rangos que dejan datos fuera (en la plantilla de referencia `MAX(Z22:Z45)` debía cubrir todo el rango).
4. "Diseño" = IF anidado sobre el resultado de la K-S; resaltar esa columna. Títulos de gráficos con el nombre de la estación.
5. Quitar hojas auxiliares; recalcular; guardar .xlsx; comparar con el cálculo independiente (distribución, D, P24, K, m, n, I).

## 12. Memoria hidrológica (Word)
- Estructura (como los estudios de Morales): 1 Aspectos generales (introducción, objetivos, ubicación política y acceso, ubicación
  hidrográfica, clima, estación de referencia); 2 Estudio hidrológico (metodología a–i, análisis estadístico de datos con tabla mensual
  y S/D, representatividad, intensidades, análisis de frecuencia con fórmulas y tablas, pruebas de bondad, evaluación del ajuste dato
  por dato, curvas IDF, tc, periodo de retorno y riesgo, intensidad de diseño); 3 Cálculo de caudales (C, áreas con figuras, I,
  caudales); 4 Drenaje (canaletas y montantes, cunetas, cunetas cubiertas, juntas, profundidades, verificación, descargas, fichas);
  5 Conclusiones; 6 Recomendaciones; 7 Anexos (N.° 01 análisis estadístico y tormenta de diseño con los cuadros: registro, B.1–B.4,
  K-S, C.4, Cuadros 04–06, intensidades, diseño; N.° 02 planta y perfil típico). Extensión de referencia ≈ 29 páginas.
- Si el usuario ya tiene su memoria: el capítulo nuevo va **al final**, en sección nueva con los márgenes y estilos del documento
  (Heading 1/2 con su numeración automática, Normal, Table Grid); comprobar que párrafos y tablas originales quedan idénticos.
- Formato: Arial Narrow 12, justificado, interlineado 1.5 (o Arial 10.5 / 1.15 en documentos nuevos); tablas con encabezado sombreado y
  texto blanco, encabezado repetido, filas que no se parten; "Tabla N° xx" y "Fuente: …" debajo, numeración continua con la del
  documento; índice automático con actualización al abrir; encabezado con proyecto y CUI; pie "Página X de Y"; carátula en sección
  propia; propiedades del archivo sin autor. Figuras de planos = las láminas del PDF que imprime el usuario, con su código.
- Recuadro de **fuente** junto a cada cálculo (norma con artículo o tabla, referencia técnica o criterio del proyectista, y si se cotejó
  con el texto oficial) y anexo de normas, referencias y criterios. Capítulo "Perfil de flujo y comprobación dinámica" si se hizo.
- Editar la memoria del usuario: quitar o cambiar **solo** lo pedido ("borra el encabezado que dice la fecha" no incluye el título) y
  comparar el texto de todas las páginas con el original. Revisar que no queden resaltados.
- Textos obligatorios: por qué T = 25; por qué tc = 10 en cunetas y 15 en el colector (bloque "Intensidad de diseño: … en cunetas y …
  en el colector"); hipótesis de suma de picos con FS 1.15; datos de otros expedientes citados como dato de su memoria.
- Memoria de cálculo en Excel con fórmulas (visibles en español: REDONDEAR, SUMA, SI con ";"): DATOS (P anual, T, tc, n capacidad,
  n velocidad, b, BL, V máx, P24 enlazada a FRECUENCIAS, P en tc = P24·(tc/1440)^0.25, I = P·60/tc, C por superficie, FS), SERIE,
  FRECUENCIAS (COUNT, AVERAGE, STDEV, SKEW), KS, IDF, SUPERFICIES, CAUDALES por tramo, DESCARGAS. Amarillo = dato; verde = diseño.
- **Cotejo obligatorio**: cada número impreso en la memoria (cuerpo y anexo) contra el Excel del análisis, a la precisión impresa
  (tolerancia media unidad del último decimal); entregar con 0 diferencias.

## 13. Cuando cambia la lluvia
Recalcular caudales (Q nuevo = Q anterior × I nueva / I anterior si la geometría no cambia); revisar si alguna profundidad dependía de la
lluvia; actualizar memoria hidrológica, memoria de cálculo, análisis estadístico, memoria descriptiva y especificaciones. Si los planos
ya están impresos, no se regeneran: avisar qué rótulos quedan con el valor anterior.

## 14. Lista de verificación final
- [ ] Serie sin datos inventados; años incompletos declarados; n ≥ 25 o justificado; fuente y estación completas.
- [ ] El método reproduce los valores de control del §10 antes de aplicarlo a datos nuevos.
- [ ] K-S: D crítico por fórmula; adoptada la de menor D; "Diseño" sigue a la K-S en Excel y en Word.
- [ ] I de diseño con Dick y Peschke (no con Bell); tc 10 min en cunetas; tc del colector justificado; T 25; FS 1.15 en todo.
- [ ] C de la CE.040 citado con su lectura correcta; C ponderado con superficies medidas en planta y tabla de áreas.
- [ ] Cunetas: BL ≥ 0.05, V ≤ 3.0, S ≥ 0.5 %, sin reducir sección; montantes ≤ 7.0 L/s por 4"; canaletas con BL 0.05.
- [ ] Memoria = Excel (cotejo con 0 diferencias); las memorias de proyectos vecinos dicen los mismos P24, I, C y caudales.
- [ ] Norma citada: CE.040 (R.M. N.° 126-2021-VIVIENDA), no la OS.060; Manual de Hidrología MTC; Chow; Aparicio.
- [ ] Sin nombre ni CIP; sin rastros de IA; todo en español; proyecto con nombre y CUI.
- [ ] Nombre, CUI, ubicación y entidad del propio proyecto (Gobierno Regional San Martín – Gerencia Territorial Bajo Mayo, GTBM; nunca
      "Proyecto Especial Huallaga" ni "PEHCBM"); ningún texto que quede de otro proyecto.
- [ ] Serie certificada en el expediente; PISCO u otras fuentes libres declaradas como referenciales y con su factor de corrección.
- [ ] Cada valor con su fuente; montantes ≤ 4 de 4" por lado; tirante ≤ 80 % en tramos tapados si se hizo el perfil de flujo.
- [ ] Excel sin hojas protegidas, con los decimales completos a la vista y todo con fórmulas (amarillo dato, gris cálculo, verde resultado).

## 15. Errores que el usuario ya corrigió (no repetirlos)
- "¿Por qué pones 35.163 mm si el diseño es 210?": mostrar lluvia e intensidad juntas; son el mismo dato.
- Un proyecto vecino declaraba su caudal "con 210.98" y una celda de control daba 350.7 L/s: el colector usa 155.66 (258.7 L/s).
- Porcentaje "7,2 %" copiado igual en tres memorias: se calcula para cada C (25.0 %, 9.0 %, 14.2 %).
- Áreas y C redondeados distinto entre expedientes (6,752.06 vs 6,752.03; 0.808 vs 0.807): usar el de la memoria del propio proyecto.
- Quitar el FS 1.15: el usuario lo repuso; es criterio fijo.
- Citar la OS.060: la norma vigente es la CE.040.
- Transponer una estación lejana por la lluvia anual cuando hay una serie medida en la misma subcuenca.
- Usar las intensidades de Bell como diseño (dan 91.6 mm/h donde Dick y Peschke da 210.98).
- Columna "Diseño" fija en Log-Normal aunque la K-S elija otra; fórmula MAX que dejaba fuera los dos últimos años.
- Memoria hidrológica de pocas páginas: el usuario pidió la estructura completa de los estudios de los CAR.
- Reducir la cuneta a 0.15 m junto al cerco ("ahí se obstruye el flujo"): la sección nunca se achica al llegar a la descarga.
- Escribir textos en inglés (hojas, rótulos, mensajes): todo en español ("¿acaso yo hablo inglés?"), también cada mensaje al usuario.
- Usar la lluvia grillada (PISCO) tal cual: subestima las máximas; va con el factor estación / PISCO y como serie referencial.
- Copiar la serie certificada del SENAMHI a otro proyecto o archivo: prohibido por la propia tabla.
- Excel protegido que "redondea decimales": entregarlo sin protección y con los decimales completos.
- Borrar de más en Word o PDF (se pidió quitar la fecha del encabezado y se borró el título): solo lo pedido.

## Referencias
- `referencias/02_hidrologia_e_hidraulica.md`: series completas, estadísticos, tablas por T, K-S, Bell, C, caudales por proyecto,
  hidráulica de cunetas, canaletas, montantes y colector, formato de entregables y validaciones.
- `referencias/08_documentos_del_expediente.md`: reglas y estilos de todos los documentos (Word, Excel, PDF), memoria hidrológica,
  memoria de cálculo, Excel del análisis estadístico, carátulas e índices.
