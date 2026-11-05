---
name: hidrologia-drenaje-pluvial
description: "Calcular la lluvia y los caudales de diseño del drenaje pluvial de cualquier local en cualquier región del Perú y redactar la memoria hidrológica (Word) y el análisis estadístico (Excel con fórmulas) en el formato del usuario: elección de la estación por cercanía y representatividad, serie de precipitación máxima en 24 h, Weibull, Kolmogorov-Smirnov, Normal, Log-Normal, Gumbel y Log Pearson III, Dick-Peschke, IDF por Bell, T, tiempo de concentración, coeficientes C de la CE.040, método racional con FS, Manning de cunetas y canaletas, montantes por Wyly-Eaton. Usar cuando el usuario entregue datos de lluvia (SENAMHI u otros), pida la lluvia de diseño, una IDF, los caudales, la memoria hidrológica o el análisis estadístico, o cuando cambie la lluvia y haya que actualizar documentos."
---

# Hidrología del drenaje pluvial y memoria hidrológica

Método general del usuario, válido para cualquier tipo de local (colegio, CAR, hogar, posta, municipalidad, mercado…) y región
del Perú (costa, sierra o selva). Se comprobó en varios expedientes de San Martín, que aparecen aquí **solo como ejemplo** (§10).
Detalle en `referencias/02_hidrologia_e_hidraulica.md` (fórmulas, series de ejemplo, cronología) y
`referencias/08_documentos_del_expediente.md` (§3 estilos Word, §4 memoria hidrológica, §6 memoria de cálculo, §8 Excel del análisis).
Las rutas de archivos de esas referencias son del trabajo original; sus números no se copian a un proyecto nuevo.

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

## 1. Datos que hay que pedir (nunca rellenar con valores supuestos)
1. Proyecto: nombre, CUI o código, entidad, tipo de local (sustenta T), ubicación (distrito, provincia, región, coordenadas y
   altitud del predio), fecha.
2. **Estación**: la que el usuario elija o compre; si no la tiene, proponer candidatas (§1b). Ficha completa: nombre, código,
   tipo, altitud, coordenadas, distrito/provincia/departamento.
3. **Serie certificada** diaria o de máximas mensuales (SENAMHI con o sin encabezado; −99.9, S/D o vacío = sin dato; "T" traza = 0.0).
   Formatos que se leen: SENAMHI txt (año, mes, día, precipitación, tmax, tmin), NASA POWER, CHIRPS o máximas ya armadas. El usuario:
   "las lluvias se compran, no hay así gratis": en el expediente va la **certificada**; las fuentes libres (§2b) solo son referenciales.
4. Plantilla de análisis estadístico (Excel) y memoria hidrológica modelo (Word) del usuario, si las tiene: se usan tal cual.
5. Superficies dentro del límite de intervención (techos en proyección horizontal con aleros, concreto, asfalto, estacionamiento,
   áreas verdes con su cobertura de pasto) y la red (canaletas, montantes, cunetas, colector), medidas en los planos del proyecto.
6. Criterios a confirmar: T (por defecto 25 años), tc (10 min en cunetas), FS (1.15), y si la entidad exige otros.
7. Estudios hidrológicos de proyectos vecinos que comparten red o receptor (para que las cifras sean coherentes), con nombre y CUI.
8. Las tablas certificadas del SENAMHI prohíben su reproducción: usarlas solo en el proyecto para el que se pidieron; no copiarlas
   a otros archivos ni programas (solo se guardan factores derivados).
Sin internet para bajar datos: decirlo y pedir los archivos.

## 1b. Elección de la estación (cualquier región)
- Ordenar las candidatas por **representatividad**: misma cuenca o subcuenca y vertiente, altitud parecida (la lluvia cambia mucho con
  la altitud en sierra y ceja de selva), mismo régimen (costa árida, sierra con lluvias estacionales, selva), luego **cercanía**.
- Preferir serie larga, completa y reciente (≥ 25 años, Manual de Hidrología, Hidráulica y Drenaje del MTC, 3.4); estación
  pluviométrica o climatológica con registro diario.
- Presentar al usuario un cuadro: estación, código, distancia, Δ altitud, años con dato, % de vacíos; él decide y compra la serie.
- **Sin transposición** si hay una serie medida representativa; la transposición por lluvia anual sobreestima la máxima diaria
  (dejarla solo como contraste y declararla).

## 2. Conformar la serie (sin inventar datos)
- Máximo de cada mes válido (≥ 20 días con dato) y máximo anual = mayor de los meses disponibles. Año incompleto: se conserva el
  máximo disponible y se declara; **no se rellenan vacíos** con ceros, promedios ni años vecinos.
- Mínimo 25 años; si el usuario lo pide: "25 años desde el año más reciente hacia abajo" (excluir el último si solo tiene unos meses).

## 2b. Serie referencial PISCO-SENAMHI (cuando no hay estación representativa)
- PISCOp v3.0 del SENAMHI: lluvia diaria grillada de 0.1° (1981-2025), descarga libre (figshare, DOI 10.6084/m9.figshare.32411886).
  Se reduce a la **máxima en 24 h de cada mes** por celda y se toma la celda con datos más cercana al predio.
- La grilla promedia ~10 × 10 km y **subestima las máximas puntuales**: multiplicar por el factor estación / PISCO = media de las
  máximas anuales de la estación ÷ media de PISCO en su celda (años comunes), **calibrado con estaciones de la misma región** e
  interpolado por inverso de la distancia al cuadrado. A más de 80 km de toda estación calibrada: factor 1.00 y aviso.
- Validar el factor dejando fuera cada estación (error esperado de pocos %). Es una serie **REFERENCIAL**: escribirlo así.

## 3. Estadísticos y distribuciones (métodos exactos de la hoja del usuario)
- x̄, s con n − 1, Cs = n·Σ(x − x̄)³/((n − 1)(n − 2)·s³) (= SKEW de Excel), para x, log10 x y ln x.
- z para P = 1/T (Abramowitz-Stegun): w = √(ln(1/P²)); z = w − (2.515517 + 0.802853w + 0.010328w²)/(1 + 1.432788w + 0.189269w² + 0.001308w³).
- Normal: x_T = x̄ + z·s. Log-Normal (log10): x_T = 10^(ȳ + z·s_y).
- Log Pearson III (Kite, k = Cs_log/6): K_T = z + (z² − 1)k + (z³ − 6z)k²/3 − (z² − 1)k³ + z·k⁴ + k⁵/3; x_T = 10^(ȳ + K_T·s_y).
- Gumbel: K_T = −(√6/π)·[0.5772 + ln(ln(T/(T − 1)))]; x_T = x̄ + K_T·s.
- Periodos 2, 5, 10, 20, 25, 50, 100, 200, 500 años; además 6/n y √(6/n).

## 4. Prueba de Kolmogorov-Smirnov (hoja "C. Prueba Kolmorov-Smirnov", con su errata)
- Serie de MAYOR a menor; excedencia observada de Weibull E_m = m/(n + 1).
- P teórica: Normal 1 − Φ((x − x̄)/s); Log-Normal 1 − Φ((log10 x − ȳ)/s_y); LP3 por gamma de ln P: β = (2/Cs_ln)², α = s_ln/√β,
  δ = x̄_ln − α·β, P = CHIDIST(2(ln x − δ)/α; 2β) con grados de libertad truncados a entero; Gumbel con yn, sn de Aparicio:
  P = 1 − exp(−exp(−(((x − x̄)/s)·sn + yn))). (n, yn, sn): (10, 0.4952, 0.9496) (15, 0.5128, 1.0206) (20, 0.5236, 1.0628)
  (25, 0.5309, 1.0914) (30, 0.5362, 1.1124); interpolar en n.
- D = máx |P − E|; D crítico = √(−ln(α/2)/(2n)) − 1/(6n), α = 0.05 (n 25: 0.2650; n 26: 0.2599).
- Se adopta la de **menor D** entre las aceptadas; la columna "Diseño" del resumen sigue **automáticamente** a la K-S.

## 5. Lluvia de corta duración e intensidad de diseño (Dick y Peschke)
P_D = P24·(D/1440)^0.25 ; I_D = 60·P_D/D (D en min, P en mm, I en mm/h). Forma equivalente: b = ln(P20/P10)/ln 2 (= 0.25);
I = P10·(tc/10)^b/(tc/60). Mostrar siempre la lluvia junto a la intensidad (P10 en mm y su I10 en mm/h son el mismo dato).

## 6. IDF por el modelo de Bell (solo para presentar; el diseño usa Dick y Peschke)
P60(10) = 0.4602·P24(10)^0.876; P(T, t) = (0.21 ln T + 0.52)(0.54 t^0.25 − 0.50)·P60(10) para t = 5, 10, 15, 20, 30, 60 min y los 9
periodos (en T = 10, t = 60 va P60(10)); I = 60P/t redondeada a 0.1 (Cuadros N.° 04 lluvias, N.° 05 intensidades). Regresión
log I = log K + m log T − n log t con las 3 ecuaciones normales (Cuadro N.° 06); K a 0.01, n = |coef. de log t|. Tabla
I = K·T^m/t^n para t = 10 a 120 min y T = 2 a 100.

## 7. Tiempo de concentración, periodo de retorno y factor de seguridad (criterios por defecto; confirmar)
- Kirpich tc = 0.01947·L^0.77·S^(−0.385) (min, m, m/m); SCS tc = 0.0195·(L³/H)^0.385; estimación física = entrada 5 min + L/V.
  Si todo da < 10 min → **tc = 10 min** (mínimo CE.040) para canaletas, montantes, sumideros y cunetas.
- Colector frontal: tc = 10 + recorrido en cunetas + recorrido en el colector (en los ejemplos ≈ 15 min). Con Dick-Peschke,
  I10/I15 = 1.5^0.75 = 1.355: usar I10 en el colector da un caudal 35.5 % mayor sin sustento. Misma I en todo un colector compartido.
- **T = 25 años** (CE.040 11.1 y 11.3; locales con niños, estudiantes, pacientes, público o personas protegidas); si la entidad o la
  importancia del local pide más, se usa el mayor. Riesgo R = 1 − (1 − 1/T)^n (tabla T 5–100, n 10, 20, 25, 50).
- **FS = 1.15 en todos los caudales** (criterio fijo del usuario; lo repuso cuando se quitó).
- Una sola lluvia para todo el proyecto, citando su fuente; avisar si se usa una curva de ejemplo.

## 8. Coeficientes de escorrentía (RNE CE.040, Anexo I, Tabla 1.a, T = 25)
| Superficie | C |
|---|---|
| Concreto / techo | 0.88 |
| Asfalto | 0.86 |
| Zona verde 0–2 %, pasto > 75 % / 50–75 % / < 50 % | 0.29 / 0.34 / 0.40 |
- Para otra T o pendiente, leer la fila y columna que corresponden en la tabla; citar la lectura.
- Canaletas, montantes y sumideros pueden ir con C = 0.88 uniforme (simplificación conservadora) si el proyectista lo acepta.
- Red o colector: C ponderado = Σ(C·A)/ΣA con las áreas medidas; el C del área verde según su cobertura real (rellenos compactados
  con poco pasto: 0.40).
- En redes sobre terreno: malla de 1 m², cada celda al segmento de cuneta más cercano (techo a dos aguas: cada mitad a su lado);
  prioridad techo > pavimento > estacionamiento > verde; acumular aguas abajo sin contar dos veces una superficie.
- Comparación "C 0.88 vs ponderado": (0.88/C − 1)·100, calculada para cada proyecto (no copiar el % de otra memoria).

## 9. Caudales y verificación hidráulica
- Q [L/s] = C·I·A·FS/3600 (A en m², I en mm/h) = C·I·A·FS/3.6e6 m³/s; con A en ha, Q = C·I·A/360.
- Cuneta (sección por defecto del usuario: 0.40 libre, muros 0.10, total 0.60; S ≥ 0.5 %): Manning n 0.015 capacidad y n 0.013
  velocidad; y por bisección; cumple si h_disp − y ≥ 0.05 y V ≤ 3.0 m/s (si no, gradas). En tapado h_disp = altura libre bajo la
  losa (≥ 0.25). Si falta capacidad se **profundiza**; nunca se cambia la sección acordada. Capacidad (S 0.5 %, BL 0.05, n 0.015):
  h 0.25 → 81.2; 0.30 → 109.0; 0.40 → 167.0; 0.50 → 227.1; 0.60 → 288.4 L/s.
- Canaleta: Manning rectangular n 0.013, S 1 % (bancas 0.5 %), borde libre 0.05 (0.25 × 0.20 conduce 48.1 L/s).
- Montante (Wyly-Eaton, rs = 0.25): Q (L/s) = 1.754·rs^(5/3)·D^(8/3) (D en pulgadas); D req = (Q/(1.754·rs^(5/3)))^(3/8).
  4" = 7.0 L/s, 3" = 3.26 L/s → se adopta 4" (≥ mínimo CE.040 12.5). Área máxima por montante de 4" = 7.0/(C·I·FS/3600) m²,
  con la I de diseño **del proyecto**; montantes por lado = ceil(A/área máx.), a lo más 4 de 4" (si faltan, llenado 7/24). Nunca 6".
- Caudal de cada tramo de cuneta **separado en techos, pisos y áreas verdes** (área y caudal de cada tipo) en la memoria.
- Perfil de flujo (paso estándar de Chow, régimen mixto, controles en descargas, uniones y caídas): donde el remanso no deja borde
  libre se profundiza el camino a la descarga. Tapados: tirante ≤ 80 % de la altura libre (CE.040, 17.6.2). EPA SWMM 5 opcional
  (bloques alternos de la IDF; Horton en áreas verdes; continuidad, picos por descarga, rebalses).
- Descarga sin gravedad (solo si no hay otra): pozos de absorción (IS.020) o bombeo (IS.010, OS.080); ver `planteamiento-drenaje-pluvial`.
- Lloraderos: no cambian el dimensionamiento. Colector frontal: skill `colector-pluvial-frontal`.

## 10. Ejemplo de referencia: valores de control del método (no son datos de diseño)
Reproducirlos con la implementación antes de usarla con datos nuevos; en el proyecto nuevo van su estación y su serie.
- CO Tarapoto, 1999–2024 (n 26): x̄ 79.354, s 22.068; K-S Normal 0.0920, Log-Normal 0.0894 (adoptada), LP3 0.0964, Gumbel 0.1270,
  crítico 0.2599; P24 T25 = 121.81 mm; P10 35.163 → I10 210.98; I15 155.66 mm/h; Bell K 161.94, m 0.1786, n 0.5271.
- Pongo de Caynarachi (SENAMHI 003317), 1989–2013 (n 25): x̄ 110.31, s 27.56; K-S Normal 0.1304, LN 0.0947, LP3 0.0683 (adoptada),
  Gumbel 0.0775, crítico 0.2650; P24 T25 = 169.27 mm; P10 48.86 → I10 293.18 mm/h; Bell K 211.66, m 0.1786, n 0.5269.
- Montantes con I10 293.18 y C 0.88: 0.0824 L/s por m² → 85.1 m² por montante de 4".
- Factores estación / PISCO calibrados en San Martín: CO Tarapoto 1.35, Pongo de Caynarachi 1.28, Chazuta 1.37, Lamas 1.57, San Pablo
  1.26; Jepelacio 1.33, Sauce 1.33, San Antonio 1.04 (ubicación aproximada). No sirven fuera de esa región.
- Fichas: Chazuta 153319 (6°34'16.3" S, 76°7'53.4" W, 203 msnm); Pongo de Caynarachi 003317 (6°19'49.7", 76°16'54.3", 187); Lamas
  000383 (6°25'7.46", 76°31'40.6", 840); Picota 153313 (6°55'11.61", 76°19'48.77", 220); San Pablo 153307 (6°48'34.4", 76°34'34.5", 270).

## 10b. Drenaje vial (MTC) – solo si el usuario lo pide
Por ahora el usuario no trabaja drenaje de carreteras: no proponerlo. Si lo pide: Manual de Hidrología, Hidráulica y Drenaje del
MTC (R.D. N.° 20-2011-MTC/14); T por riesgo admisible y vida útil (Tabla 02): plataforma R 40 %, n 15 → 30 años; alcantarillas
menores y alivios R 35 %, n 15 → 36; quebradas importantes y badenes R 30 %, n 25 → 71; C de la Tabla 08; tc de la Tabla 05;
racional si A < 10 km², Témez de 10 a 770 km²; Manning con borde libre del 25 %.

## 11. Excel del análisis estadístico (formato del usuario, con fórmulas)
Hojas (nombres tal cual): "A. Estación", "B.Modelo Distribución" (B.1 Normal, B.2 Log Normal, B.3 Log Pearson III, B.4 Gumbel),
"C. Prueba Kolmorov-Smirnov", "D.Resumen" (C.4), "A. Parametros" (Cuadros 04–06, Bell, regresión), "B. Int.maxima" (IDF),
"C. P diseño" (Dick-Peschke por T), más CARÁTULA. Encabezado Proyecto (con CUI), Entidad, Ubicación, Fecha del proyecto nuevo.
1. Escribir encabezado, datos de la estación y periodo; cargar años y 12 meses ("S/D" con el resaltado de la plantilla).
2. **Borrar o insertar filas** con la herramienta de filas (se ajustan fórmulas y gráficos); nunca reescribir fórmulas a mano.
3. Revisar rangos que dejan datos fuera (p. ej. un `MAX` que no cubre todos los años).
4. "Diseño" = IF anidado sobre la K-S; resaltar esa columna. Títulos de gráficos con el nombre de la estación del proyecto.
5. Quitar hojas auxiliares; recalcular; guardar .xlsx; comparar con el cálculo independiente (distribución, D, P24, K, m, n, I).

## 12. Memoria hidrológica (Word)
- Estructura completa del usuario: 1 Aspectos generales (introducción, objetivos, ubicación política y acceso, ubicación hidrográfica,
  clima, estación de referencia y su representatividad); 2 Estudio hidrológico (metodología, análisis de datos con tabla mensual y S/D,
  intensidades, frecuencias, bondad de ajuste, IDF, tc, T y riesgo, intensidad de diseño); 3 Caudales (C, áreas con figuras, I,
  caudales); 4 Drenaje (canaletas y montantes, cunetas, tapadas, juntas, profundidades, verificación, descargas); 5 Conclusiones;
  6 Recomendaciones; 7 Anexos (análisis estadístico en cuadros; planta y perfil típico). Extensión de referencia ≈ 29 páginas.
- Si el usuario ya tiene su memoria: el capítulo nuevo va **al final**, en sección nueva con sus márgenes y estilos; comprobar que
  párrafos y tablas originales quedan idénticos.
- Formato: Arial Narrow 12, justificado, 1.5 (o Arial 10.5 / 1.15 en documentos nuevos); tablas con encabezado sombreado y texto
  blanco, encabezado repetido; "Tabla N° xx" y "Fuente: …"; índice automático; encabezado con proyecto y CUI; pie "Página X de Y";
  carátula en sección propia; propiedades sin autor. Figuras de planos = las láminas que imprime el usuario, con su código.
- Recuadro de **fuente** junto a cada cálculo y anexo de normas, referencias y criterios.
- Editar la memoria del usuario: quitar o cambiar **solo** lo pedido y comparar el texto de todas las páginas con el original.
- Textos obligatorios: por qué T; por qué tc 10 en cunetas y el del colector; hipótesis de suma de picos con FS 1.15; datos de otros
  expedientes citados como dato de su memoria.
- Memoria de cálculo en Excel con fórmulas (REDONDEAR, SUMA, SI con ";"): DATOS, SERIE, FRECUENCIAS, KS, IDF, SUPERFICIES, CAUDALES
  por tramo, DESCARGAS. Amarillo = dato; verde = diseño.
- **Cotejo obligatorio**: cada número de la memoria (cuerpo y anexo) contra el Excel, a la precisión impresa; 0 diferencias.

## 13. Cuando cambia la lluvia
Recalcular caudales (Q nuevo = Q anterior × I nueva / I anterior si la geometría no cambia); revisar si alguna profundidad dependía de
la lluvia; actualizar memorias, análisis estadístico y especificaciones. Planos ya impresos: no se regeneran; avisar qué rótulos quedan.

## 14. Lista de verificación final
- [ ] Estación elegida por representatividad y cercanía, con su ficha; serie sin datos inventados; n ≥ 25 o justificado.
- [ ] El método reproduce los valores de control del §10 antes de aplicarlo; ningún valor del ejemplo quedó en el proyecto nuevo.
- [ ] K-S con D crítico por fórmula; adoptada la de menor D; "Diseño" sigue a la K-S en Excel y en Word.
- [ ] I de diseño con Dick y Peschke (no Bell); tc 10 min en cunetas; tc del colector justificado; T y FS 1.15 en todo.
- [ ] C de la CE.040 con su lectura; C ponderado con superficies medidas en planta.
- [ ] Cunetas: BL ≥ 0.05, V ≤ 3.0, S ≥ 0.5 %, sin reducir sección; montantes ≤ 7.0 L/s por 4"; canaletas con BL 0.05.
- [ ] Memoria = Excel (0 diferencias); proyectos vecinos que comparten red dicen los mismos P24, I, C y caudales.
- [ ] Norma: CE.040 (R.M. N.° 126-2021-VIVIENDA), no la OS.060; Manual de Hidrología MTC; Chow; Aparicio.
- [ ] Nombre, CUI, ubicación, tipo de local y **entidad correcta del propio proyecto**; ningún texto que quede de otro proyecto.
- [ ] Serie certificada en el expediente; PISCO u otras fuentes libres declaradas referenciales y con su factor regional.
- [ ] Excel sin protección, con los decimales completos y todo con fórmulas (amarillo dato, gris cálculo, verde resultado).

## 15. Errores que el usuario ya corrigió (lecciones generales)
- Mostrar la lluvia en mm sin su intensidad (o al revés) confunde: van juntas, son el mismo dato.
- Usar en el colector la I de 10 min de las cunetas: caudal sobrestimado sin sustento; el colector va con su propio tc.
- Copiar un porcentaje, un área o un C de otra memoria: se calcula para cada proyecto con sus superficies.
- Quitar el FS 1.15; citar la OS.060 en lugar de la CE.040; usar las intensidades de Bell como diseño (dan mucho menos).
- Transponer una estación lejana por lluvia anual habiendo una serie medida representativa.
- Columna "Diseño" fija en una distribución aunque la K-S elija otra; fórmulas que dejan años fuera del rango.
- Memoria hidrológica de pocas páginas: el usuario quiere la estructura completa.
- Achicar la cuneta junto al cerco ("ahí se obstruye el flujo"): la sección no se achica en la descarga.
- Textos en inglés (hojas, rótulos, mensajes): todo en español ("¿acaso yo hablo inglés?").
- Usar la lluvia grillada (PISCO) tal cual o con factores de otra región: subestima; va con su factor regional y como referencial.
- Copiar la serie certificada del SENAMHI a otro proyecto o archivo: prohibido por la propia tabla.
- Excel protegido que "redondea decimales"; borrar de más al editar un Word (se pidió quitar la fecha y se borró el título).
- Dejar en un documento la entidad, el nombre o el tipo de local de un proyecto anterior.

## Referencias
- `referencias/02_hidrologia_e_hidraulica.md`: series de ejemplo, estadísticos, tablas por T, K-S, Bell, C, caudales, hidráulica de
  cunetas, canaletas, montantes y colector, formato de entregables y validaciones.
- `referencias/08_documentos_del_expediente.md`: reglas y estilos de los documentos (Word, Excel, PDF), memoria hidrológica,
  memoria de cálculo, Excel del análisis estadístico, carátulas e índices.
