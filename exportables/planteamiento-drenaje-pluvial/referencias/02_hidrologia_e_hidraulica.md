# 02 — Hidrología e hidráulica de diseño

Base de conocimiento permanente. Reúne todo lo aprendido desde el 3 de octubre de 2026 sobre lluvia de diseño, caudales,
hidráulica de cunetas y del colector frontal compartido, con fórmulas, constantes, valores y el porqué de cada decisión.
Fuentes: mensajes del usuario, `BITACORA_CONVERSACION.md`, `CLAUDE.md`, skills `diseno-colector-pluvial` y
`planteamiento-cunetas-terreno`, y el código de `herramientas/` (se cita archivo y función en cada caso).

Reglas que rigen todo este tema:
- Decir siempre "cota de fondo" (nunca "invert").
- Citar los proyectos por nombre y CUI. Los alias de persona (Katiuska, Solange, Wilma) solo sirven para la conversación; en
  los documentos nunca aparecen.
- En los documentos no se pone el nombre ni el CIP del proyectista y nada debe delatar el uso de IA.
- Un dato que viene de otro expediente se cita como dato de ese expediente ("aporte externo", "receptor"), sin validarlo.
- Cuando se cambia la lluvia, el diseño o un texto, se actualiza todo lo relacionado: memoria hidrológica, memoria de cálculo,
  análisis estadístico, memoria descriptiva, especificaciones y planos. Excepción: si el usuario ya imprimió los planos, no se
  regeneran y se le avisa qué rótulos quedan con el valor anterior.

---

## 1. Proyectos y cadena hidráulica

| Proyecto | CUI | Alias (solo conversación) | Rol en el colector | Ancho interior colector | Q propio (L/s) |
|---|---|---|---|---|---|
| CAR Varones | 2705619 | Katiuska | tramo aguas arriba (aporte externo para el Refugio) | 0.60 m, muros 0.15 | 258.7 |
| Hogar de Refugio Temporal "Mujeres Violentadas" | 2675514 | Solange | tramo intermedio | 0.80 m, muros 0.15 | 301.9 |
| CAR Mujeres | 2717013 | Wilma | tramo final, receptor de los tres | 1.50 m, muros 0.10 | 262.3 |
| I.E. N.° 0590 Barranquita (Lamas) | C.I. 468901 (confirmar CUI) | – | red de cunetas propia, sin colector | cuneta 0.40 libre / 0.60 total | 229.2 máx. por tramo |

Cadena: Varones (0.60) → caja de llegada CL → Refugio (0.80) → caja de caída CC → R-01 del CAR Mujeres (1.50) → salida a la
berma de la Carretera Oasis. El ancho crece aguas abajo y las cotas de fondo y niveles de agua empalman (verificado el
15-10-2026):

| Punto | Cota de fondo | Nivel de agua | Caudal |
|---|---|---|---|
| Varones 0+000 (poste derecho del portón de camiones) | 260.20 | – | – |
| Varones en la cara este de la CL (0+105.29) | 259.884 (260.20 − 0.3 % × 105.29) | caída libre 0.278 m sobre el NA de la CL | 221.7 (colector) + 37.0 (cuneta Eje 01 directa a la CL) = 258.7 |
| Piso de la poza de la CL | 258.80 (259.10 − 0.30) | 259.606 | 258.7 |
| Refugio 0+000 (CL) | 259.10 | 259.606 | 560.6 |
| Refugio brink (fin del canal 0.80, 0+069.89) | 258.89 | 259.259 (tirante crítico) | 560.6 |
| Piso de la poza de la CC | 258.32 (258.72 − 0.40) | 259.062 | 560.6 |
| CAR Mujeres R-01 (0+000) | 258.72 | 259.063 | 626.2 (560.6 + 65.6 de su cuneta Eje 02) |
| CAR Mujeres salida (0+139.08) | 258.30 | 258.785 (control por vertido) | 822.9 |

Condiciones de entrega fijadas por el receptor (CAR Mujeres) para los dos proyectos de aguas arriba: entrega en su Eje 02
(0+000.00), cota de fondo de llegada ≥ 258.72 msnm y caudal conjunto ≤ 560.7 L/s.

---

## 2. Lluvia de diseño de los tres CAR de Morales (estación CO Tarapoto)

### 2.1 Estación y serie
- Estación meteorológica convencional CO "Tarapoto", SENAMHI. Latitud 06° 28' S, longitud 76° 22' O, altitud 356 m s. n. m.,
  distrito Tarapoto, provincia y departamento San Martín.
- Serie de precipitación máxima en 24 h por mes, 1999–2024 (26 años calendario). La memoria de los CAR integra 1999–2004 de un
  documento complementario y 2005–2024 del cuadro principal (una sola observación por mes y año).
- Máximos anuales usados (mm): 1999 79.3 · 2000 82.5 · 2001 75.9 · 2002 43.6 · 2003 84.5 · 2004 64.2 · 2005 71.0 · 2006 113.3 ·
  2007 63.5 · 2008 91.0 · 2009 49.0 · 2010 98.4 · 2011 65.2 · 2012 100.5 · 2013 71.7 · 2014 89.5 · 2015 64.2 · 2016 50.0 ·
  2017 73.6 · 2018 69.6 · 2019 86.9 · 2020 152.5 · 2021 73.5 · 2022 85.2 · 2023 92.4 · 2024 72.2.
  (Serie mensual completa en `herramientas/barranquita/hidrologia_b.py`, `SERIE_TARAPOTO`.)

### 2.2 Datos faltantes (criterio del usuario y de las memorias)
- No se rellenan vacíos con ceros, promedios ni valores de años vecinos. Los "S/D" y las celdas vacías se conservan como
  "dato no disponible".
- 2020: S/D de abril a julio; se conserva 152.5 mm (enero) como máximo de los meses disponibles. 2024: solo enero a julio,
  máximo disponible 72.2 mm (febrero). Ambos años entran en la serie de 26 valores con el máximo de los meses disponibles;
  la memoria lo declara expresamente ("año incompleto: el valor no se valida automáticamente como máximo anual").
- Prioridad declarada: recuperar los datos de la misma estación (SENAMHI); una estimación solo con estaciones de apoyo,
  correspondencia temporal y relación estadística comprobada, y siempre diferenciada de los datos observados.
- Referencia: numeral 3.4 del Manual de Hidrología, Hidráulica y Drenaje del MTC (mínimo 25 años de registro), citado como
  orientación metodológica, no como exigencia de la CE.040.
- Mismo criterio aplicado en Barranquita: enero 2005 y julio 2008 sin datos en Pongo de Caynarachi; se conserva el máximo de
  los otros 11 meses del año.

### 2.3 Resultados del análisis estadístico (hoja del usuario "ANALISIS ESTADISTICO – CAR VARONES")
Estadísticos (n = 26): media 79.354 mm, desviación 22.068 mm, asimetría 1.3587; log10: media 1.88474, desviación 0.114749,
asimetría 0.15635 (k = Cs/6 = 0.02606). Variación del coeficiente de asimetría 6/n = 0.2308; desviación estándar del
coeficiente √(6/n) = 0.4804.

Prueba K-S (α = 0.05, D crítico = 0.2599 ≈ 0.260):

| Distribución | D máx. |
|---|---|
| Normal | 0.0920 |
| Log-Normal | 0.0894 (adoptada, menor D) |
| Log Pearson III | 0.0964 |
| Gumbel | 0.1270 |

Precipitación máxima en 24 h de diseño (columna "Diseño" = Log-Normal):

| T (años) | 2 | 5 | 10 | 20 | 25 | 50 | 100 | 200 | 500 |
|---|---|---|---|---|---|---|---|---|---|
| P24 (mm) | 76.69 | 95.79 | 107.60 | 118.45 | **121.81** | 131.97 | 141.82 | 151.48 | 164.08 |

Para T = 25: Normal 118.00, Log-Normal 121.81, LP3 123.51, Gumbel 124.46 mm.

### 2.4 Lluvia de corta duración e intensidades (Dick y Peschke, hoja "C. P diseño")
P_D = P24 · (D / 1440)^0.25 ;  I_D = P_D · 60 / D   (D en minutos, P en mm, I en mm/h)

Con P24 = 121.81 mm (T = 25):

| D (min) | (D/1440)^0.25 | P_D (mm) | I_D (mm/h) |
|---|---|---|---|
| 10 | 0.2887 | 35.163 | **210.98** |
| 15 | 0.3195 | 38.915 | **155.66** |
| 20 | 0.3433 | 41.816 | 125.45 |
| 30 | 0.3799 | 46.28 | 92.56 |
| 60 | 0.4518 | 55.03 | 55.03 |

Forma equivalente usada en la memoria de cálculo Excel del colector (`herramientas/memoria_xlsx.py`, hoja DATOS):
b = ln(P20/P10) / ln 2 = ln(41.816/35.163)/ln 2 = 0.25 ;  I = P10 · (tc/10)^b / (tc/60). Con tc = 15 → 155.66 mm/h.

IDF de la hoja "A. Parametros / B. Int. maxima" (modelo de Bell, ver §4.6): K = 161.94, m = 0.1786, n = 0.5271,
I = K · T^m / t^n. Ojo: esas intensidades de Bell (T = 25: 10 min 91.6 mm/h) NO son las de diseño; el diseño usa siempre
Dick y Peschke ("C. P diseño").

### 2.5 Corrección del usuario sobre P10 (03-10-2026)
El usuario reclamó: "por qué pones 35.163 mm si el diseño es 210". Aclaración que quedó escrita en la hoja DATOS: 35.163 mm
es la lluvia de 10 minutos; expresada como intensidad es I10 = 35.163 × 60 / 10 = 210.98 mm/h. Son el mismo dato. En los
documentos se muestra siempre la intensidad junto a la lluvia para que no parezca una contradicción.

---

## 3. Tiempo de concentración: 210.98 mm/h en cunetas y 155.66 mm/h en el colector

### 3.1 Regla
- La CE.040 fija la intensidad de un punto para una duración igual al tiempo de concentración del área que drena hacia él,
  con mínimo de 10 minutos.
- Canaletas, montantes, sumideros y cunetas: áreas pequeñas (un techo o un tramo de piso), el agua llega en menos de
  10 min (Kirpich y SCS dan menos de 10) → tc = 10 min → I = 210.98 mm/h. Esta intensidad no se reemplaza nunca.
- Colector frontal: tc = 10 min de entrada (techo o piso hasta la cuneta) + ≈ 3 min por la cuneta hasta el colector +
  ≈ 2 min por el colector (139 m del tramo CAR Mujeres a 1.1–1.4 m/s) = 15 min → I = 155.66 mm/h.
- Se usa la misma intensidad (155.66) en los tres tramos del colector para que el caudal que entrega cada proyecto sea el
  mismo que recibe el siguiente.

### 3.2 Por qué no 210.98 en el colector (texto aprobado, 20-10-2026)
Usarla equivaldría a suponer que el agua de los tres predios llega toda a la vez en 10 minutos: el caudal sería 35.5 % mayor
(210.98 / 155.66 = 1.355) sin sustento en la norma. El cálculo del colector ya es conservador porque suma los picos de los
tres proyectos sin desfase y aplica FS = 1.15.

El usuario pidió (20-10-2026) "explicar bien, detallar por qué cambias de 210 a 155, todo justificado; las 3 memorias
hidrológicas sin errores deben coincidir". Se resolvió con `herramientas/revision_hidrologia.py`, que inserta el mismo bloque
"Intensidad de diseño: 210.98 mm/h en cunetas y 155.66 mm/h en el colector" en las tres memorias, después de la tabla de
caudales del colector, con: fórmula de Dick y Peschke, cálculo para D = 10 y D = 15, explicación por tipo de elemento,
porcentaje 35.5 % y caudales compartidos. Es idempotente (marca = título del bloque). La intensidad exacta que usan las
memorias es I15 = 121.81 · (15/1440)^0.25 · 60/15 = 155.659 mm/h.

### 3.3 Fórmulas de tc citadas en las memorias
- Kirpich: tc = 0.01947 · L^0.77 · S^(−0.385)  (tc en min, L en m, S en m/m).
- SCS (California Culverts Practice): tc = 0.0195 · (L³ / H)^0.385  (tc en min, L en m, H en m). La memoria del CAR Mujeres
  la presenta con L en km y H en pies (1 m = 3.28084 pies).
- Estimación física (Barranquita): 5 min de entrada sobre techos y pisos + L / V_media de las cunetas / 60.
- Si todo da < 10 min → tc = 10 min (mínimo CE.040).

---

## 4. Lluvia de diseño de la I.E. N.° 0590 Barranquita (historia completa y resultado vigente)

### 4.1 Cronología de decisiones (todas del 20 y 21-10-2026)
1. Planteamiento preliminar: verificación con la lluvia del Refugio (I ≈ 211 mm/h, tc 10 min, C 0.80), solo referencial.
2. El usuario preguntó "¿está bien que uses la misma estación Tarapoto?". Opción 2 aprobada: serie Pmax24 de CO Tarapoto
   transpuesta por la relación de lluvia anual Yurimaguas / Tarapoto = 2,039.6 / 1,073.1 = 1.90. Log-Normal T25:
   P24 = 231.49 mm; I = 400.96 mm/h; IDF K 1419.77, m 0.1315, n 0.750. C ponderado 0.57 y sin FS. El usuario: "mantén la cuneta
   0.40 interior, 0.60 total" → cumplían los 91 tramos (Q máx 227.3 L/s, borde libre mín 0.119 m, V máx 1.73 m/s).
3. Opción A aprobada: P anual de Barranquita = promedio de las estaciones de llanura Navarro (2,349.79), Pelejo (2,332.92) y
   Shanusi (2,444.00) = 2,375.57 mm (SENAMHI 2013–2017, Cuadro N.° 05 del estudio hidrológico del expediente de agua potable
   y alcantarillado del distrito de Barranquita). Factor 2,375.57 / 1,073.1 = 2.2137 → P24 T25 = 269.62 mm, I = 467.00 mm/h.
   En ese momento Pongo de Caynarachi (pie de cerros, lluvia orográfica, 3,853.16 mm/año) y San Antonio (1,834.84) no se usaron.
4. Se repuso FS = 1.15 (mismo criterio de los CAR): Q máx 304.4 L/s, borde libre mín 0.064 m (EJE-12 llegando a D2); seguía
   cumpliendo sin cambiar geometría. Se cambió la norma citada de OS.060 a CE.040.
5. El usuario pidió datos mínimo 2024–2025 y dio "acceso total a internet": desde el entorno, senamhi.gob.pe,
   power.larc.nasa.gov, data.chc.ucsb.edu y archive-api.open-meteo.com dieron 403. Se creó `lluvia_datos_b.py` para leer los
   archivos que el usuario entregue (no modifica el diseño).
6. El usuario entregó los datos diarios de Pongo de Caynarachi (SENAMHI 003317, nov-1963 a abr-2014, 125 días faltantes).
   Con 50 años (1964–2013): media 107.8, desv. 35.0, máx 226.3 mm (1968); K-S Gumbel 0.104, Log-Normal 0.111, LP3 0.119,
   Normal 0.159 (crítico 0.19); P24 T25 = 179.39 mm (Gumbel); I = 310.71 mm/h.
7. Decisión del usuario: "sí, usa estos datos, pero solo 25 años desde el año más reciente hacia abajo" → 1989–2013 (2014 solo
   tiene enero–abril). Sin transposición (factor 1.0). Gumbel adoptada (K-S 0.069; LP3 0.070; LN 0.095; Normal 0.130):
   P24 = 166.64 mm, P10 = 48.11 mm, I = 288.63 mm/h; IDF K 1009.51, m 0.1372, n 0.75. Q máx 188.1 L/s (C 0.57).
8. Superficies medidas en planta: C ponderado 0.761 (antes 0.570). Q máx 225.7 L/s.
9. El usuario envió su hoja "ANALISIS ESTADISTICO – CAR VARONES" ("así quiero el análisis estadístico"). Con los métodos
   exactos de esa hoja la prueba K-S elige **Log Pearson III**: P24 T25 = 169.27 mm, I = 293.18 mm/h (vigente).
10. El usuario preguntó si la memoria coincide con el nuevo análisis: `coteja_analisis_b.py` comparó 1696 valores (1002 del
    cuerpo y 694 del anexo N.° 01) con el Excel del análisis a la precisión impresa: 0 diferencias.

### 4.2 Por qué se descartó la transposición
- Pongo de Caynarachi llueve 3.3 a 3.8 veces lo que Tarapoto al año, pero su máxima en 24 h de 25 años es solo ≈ 1.4 veces la
  de Tarapoto (169.27 / 121.81 = 1.39). La transposición por lluvia anual sobreestima la máxima diaria.
- La serie medida está en la misma subcuenca del río Caynarachi que Barranquita (184 m s. n. m.); la estación (230 m s. n. m.,
  al pie de los cerros) es más lluviosa que la llanura, por lo que usarla sin transponer es conservador.
- Tarapoto transpuesta (×2.2137, Log-Normal) queda solo como contraste en la memoria: 269.65 mm, 467.05 mm/h;
  Tarapoto sin transponer 121.81 mm.
- Los totales anuales de Caynarachi 1981–1990 son anómalos (5,255 a 7,060 mm; el resto 1,680 a 4,333): no afectan las
  máximas, pero no sirven para la lluvia media anual sin depurar.

### 4.3 Serie vigente: Pongo de Caynarachi 1989–2013 (SENAMHI 003317)
Estación meteorológica convencional, Lamas / Caynarachi, 230 m s. n. m. Máximos anuales (mm):
1989 141.9 · 1990 115.1 · 1991 114.8 · 1992 123.0 · 1993 89.1 · 1994 179.9 · 1995 84.2 · 1996 96.4 · 1997 103.9 · 1998 171.8 ·
1999 146.0 · 2000 108.5 · 2001 78.0 · 2002 88.7 · 2003 138.5 · 2004 90.2 · 2005 97.3 · 2006 102.5 · 2007 77.3 · 2008 100.4 ·
2009 87.0 · 2010 128.0 · 2011 101.0 · 2012 110.2 · 2013 84.0. (Mensuales en `hidrologia_b.SERIE`.)

Archivo fuente: `insumos/barranquita/lluvia/qc00003317_pongo_de_caynarachi.txt` (año mes día pp tmax tmin; −99.9 = sin dato).

### 4.4 Resultados vigentes (`hidrologia_b.resultados()`)
- n = 25; media 110.31 mm; desviación 27.56 mm; asimetría 1.132.
- log10 P: media 2.03086; desviación 0.10076; asimetría 0.6858.
- ln P: media 4.67623; desviación 0.23201; asimetría 0.6858; β = 8.5045; α = 0.07956; δ = 3.99962.
- Gumbel (momentos): α = √6·s/π = 21.490; u = media − 0.5772·α = 97.904. Para K-S: yn = 0.5309, sn = 1.0914 (n = 25).
- K-S (α = 0.05, D crítico 0.2650): Normal 0.1304, Log-Normal 0.0947, **LP3 0.0683 (adoptada)**, Gumbel 0.0775.

| T (años) | Normal | Log-Normal | LP3 (diseño) | Gumbel |
|---|---|---|---|---|
| 2 | 110.31 | 107.36 | 104.59 | 105.78 |
| 5 | 133.50 | 130.51 | 128.94 | 130.14 |
| 10 | 145.64 | 144.55 | 146.18 | 146.26 |
| 20 | 155.65 | 157.27 | 163.56 | 161.73 |
| 25 | 158.57 | 161.18 | **169.27** | 166.64 |
| 50 | 166.93 | 172.92 | 187.45 | 181.76 |
| 100 | 174.44 | 184.21 | 206.50 | 196.76 |
| 200 | 181.32 | 195.19 | 226.62 | 211.71 |
| 500 | 189.65 | 209.37 | 255.07 | 231.44 |

Dick y Peschke con P24 = 169.27 (T = 25): P10 = 48.86 mm → I10 = 293.18 mm/h (diseño, tc = 10 min). I15 = 216.30,
I20 = 174.32, I30 = 128.61, I60 = 76.47 mm/h.

Bell: P60(10) = 0.4602 · 146.18^0.876 = 36.26 mm; IDF K = 211.66, m = 0.1786, n = 0.5269.

### 4.5 Métodos exactos del formato del usuario (hoja "ANALISIS ESTADISTICO", reproducidos en `hidrologia_b.analisis`)
Comprobación: con la serie de Tarapoto el código reproduce la hoja del CAR Varones (D 0.0920 / 0.0894 / 0.0964 / 0.1270;
K 161.94, m 0.1786, n 0.5271; P24 121.81; I 210.98).

1. Estadísticos: media, desviación con n − 1, asimetría Cs = n·Σ(x − x̄)³ / ((n − 1)(n − 2)·s³) (= SKEW de Excel).
2. Variable normal estándar para P = 1/T (Abramowitz y Stegun):
   w = √(ln(1/P²)) ;  z = w − (2.515517 + 0.802853 w + 0.010328 w²) / (1 + 1.432788 w + 0.189269 w² + 0.001308 w³).
3. Normal: x_T = x̄ + z·s.
4. Log-Normal (2 parámetros, log10): x_T = 10^(ȳ + z·s_y).
5. Log Pearson III (log10, Kite, k = Cs_log/6):
   K_T = z + (z² − 1)k + (z³ − 6z)k²/3 − (z² − 1)k³ + z·k⁴ + k⁵/3 ;  x_T = 10^(ȳ + K_T·s_y).
6. Gumbel (frecuencias): K_T = −(√6/π)·[0.5772 + ln(ln(T/(T − 1)))] ;  x_T = x̄ + K_T·s.
7. Kolmogorov-Smirnov ("C. Prueba Kolmorov-Smirnov", así se llama la hoja):
   - Serie ordenada de MAYOR a menor; probabilidad de excedencia observada de Weibull E_m = m/(n + 1).
   - Normal: P_teo = 1 − Φ((x − x̄)/s). Log-Normal: P_teo = 1 − Φ((log10 x − ȳ)/s_y).
   - LP3 por la distribución gamma de ln P: β = (2/Cs_ln)², α = s_ln/√β, δ = media_ln − α·β;
     P_teo = CHIDIST(2·(ln x − δ)/α ; 2β), con grados de libertad truncados a entero (como Excel).
   - Gumbel con yn y sn de Aparicio (pág. 264): P_teo = 1 − exp(−exp(−(((x − x̄)/s)·sn + yn))).
     Tabla (n, yn, sn): (10, 0.4952, 0.9496) (15, 0.5128, 1.0206) (20, 0.5236, 1.0628) (25, 0.5309, 1.0914)
     (30, 0.5362, 1.1124) (90, 0.5586, 1.2007) (95, 0.5593, 1.2037); interpolación lineal en n.
   - D = máx |P_teo − E_m|; D crítico = √(−ln(α/2)/(2n)) − 1/(6n) con α = 0.05 (n = 25: 0.2650; n = 26: 0.2599).
   - Se aceptan las que tienen D < D crítico; se adopta la de menor D. La columna "Diseño" del resumen debe tomar
     automáticamente la distribución que elige la K-S (corrección hecha en la plantilla de Barranquita).
8. Resumen "C.4 / D. Resumen": tabla T vs Normal, Log Normal, LP3, Gumbel, Diseño; más variación del coeficiente de
   asimetría 6/n y su desviación √(6/n).

### 4.6 Tormenta de diseño: modelo de Bell e IDF (hojas "A. Parametros" y "B. Int. maxima")
- P60(10) = 0.4602 · P24(10)^0.876 (lluvia de 60 min y 10 años a partir de la P24 de 10 años de la distribución de diseño).
- P(T, t) = (0.21·ln T + 0.52) · (0.54·t^0.25 − 0.50) · P60(10), con t en minutos (5 a 120). En la celda T = 10, t = 60 se
  pone directamente P60(10).
- Duraciones 5, 10, 15, 20, 30, 60 min; periodos 2, 5, 10, 20, 25, 50, 100, 200, 500 años (54 puntos).
- Intensidades I = 60·P/t, redondeadas a 0.1 mm/h (Cuadro N.° 05). Cuadro N.° 04 = lluvias; Cuadro N.° 06 = regresión.
- Regresión lineal múltiple de los logaritmos: Y = log I, X1 = log T, X2 = log t; m·X1 − n·X2 + log K = Y. Ecuaciones normales:
  m·ΣX1 + n·ΣX2 + (log K)·N = ΣY ; m·ΣX1² + n·ΣX1X2 + (log K)·ΣX1 = ΣX1Y ; m·ΣX1X2 + n·ΣX2² + (log K)·ΣX2 = ΣX2Y.
  K = 10^(log K) redondeado a 0.01; n = |coeficiente de X2|.
- "B. Int. maxima": tabla I = K·T^m/t^n para t = 10 a 120 min cada 10 y T = 2, 5, 10, 20, 25, 50, 100.
- Nota: cuando se ajustó una IDF directamente a las intensidades de Dick y Peschke (pasos 2 y 7 de §4.1) el exponente salió
  n = 0.75 exacto, porque Dick y Peschke da I ∝ t^(−0.75). Con Bell, n ≈ 0.53.

### 4.7 Lectura de datos diarios (`herramientas/barranquita/lluvia_datos_b.py`)
- Formatos: SENAMHI con encabezado, SENAMHI histórico sin encabezado (año mes día pp tmax tmin, −99.9 sin dato), NASA POWER
  (YEAR, MO, DY, PRECTOTCORR o YEAR, DOY), CHIRPS (fecha, precipitación). "T" (traza) = 0.0; S/D, vacío, −99.9, negativos o
  > 900 mm = sin dato.
- Máximo mensual válido con ≥ 20 días; máximo anual válido con ≥ 300 días con dato; total anual con 12 meses de ≥ 25 días.
- Serie mínima recomendada 25 años. Estaciones reconocidas por nombre o código: Navarro 000386, Pelejo 153322, Shanusi 153315,
  Pongo de Caynarachi 003317, Tarapoto; puntos NASA POWER / CHIRPS de Barranquita (−6.25, −76.03) y Tarapoto.
- Hace el mismo análisis de `hidrologia_b` y guarda `entregables_barranquita/_calc/lluvia_comparacion.json`. No cambia el diseño.

### 4.8 Estaciones de la zona (precipitación total anual, SENAMHI 2013–2017)
| Estación | Código | Provincia / distrito | Altitud | P anual (mm) |
|---|---|---|---|---|
| San Antonio | 153314 | San Martín / San Antonio | 430 | 1,834.84 |
| Pongo de Caynarachi | 003317 | Lamas / Caynarachi | 230 | 3,853.16 |
| Navarro | 000386 | San Martín / Chipurana | 130 | 2,349.79 |
| Pelejo | 153322 | San Martín / El Porvenir | 100 | 2,332.92 |
| Shanusi | 153315 | Alto Amazonas / Yurimaguas | 160 | 2,444.00 |

Tarapoto: 1,073.1 mm/año. Clima Af, 1,800–2,400 mm/año según la memoria de arquitectura del colegio.

---

## 5. Periodo de retorno, riesgo y factor de seguridad
- T = 25 años en todos los proyectos (probabilidad anual 4 %). Sustento: CE.040 numeral 11.1 (el periodo de retorno se elige
  según el tipo de proyecto y el criterio del profesional) y 11.3 (diseño para precipitaciones de baja frecuencia con T ≥ 25).
  Uso: CAR = alojamiento y protección de niñas, niños y adolescentes; colegio = estudiantes en dos turnos.
- Riesgo de excedencia en n años de vida útil: R = 1 − (1 − 1/T)^n (tabla para T 5–100 y n 10, 20, 25, 50 en la memoria).
- Factor de seguridad FS = 1.15 sobre todos los caudales (15 % de margen). En Barranquita se quitó un momento y el usuario
  lo volvió a poner: es criterio fijo.

---

## 6. Coeficientes de escorrentía

### 6.1 Tabla CE.040, Anexo I, Tabla 1.a (T = 25 años), tal como la citan las memorias
| Superficie | C |
|---|---|
| Concreto / techo | 0.88 |
| Asfalto | 0.86 |
| Zona verde, pendiente 0–2 %, pasto > 75 % | 0.29 |
| Zona verde, pendiente 0–2 %, pasto 50–75 % | 0.34 |
| Zona verde, pendiente 0–2 %, pasto < 50 % | 0.40 |

(La memoria de Barranquita rotula 0.29 / 0.34 / 0.40 como "pendiente 0–2 %, 2–7 %, > 7 %"; la del CAR Mujeres por cobertura
de pasto, que es la lectura de la tabla. Si se rehace el texto, preferir la del CAR Mujeres.)

### 6.2 Valores adoptados por proyecto
| Superficie | CAR (Morales) | Barranquita |
|---|---|---|
| Techos (proyección horizontal, con aleros) | 0.88 | 0.88 |
| Veredas / áreas libres de concreto frotachado | 0.88 | 0.88 |
| Estacionamiento | 0.86 (asfalto) | 0.88 (patio de maniobra de concreto) |
| Áreas verdes | 0.29 | 0.40 (valor mayor de la tabla: rellenos compactados, menos infiltración) |
| Patios o áreas libres (mencionado por el usuario) | 0.40 | – |

### 6.3 Dónde se usa cada uno
- Canaletas, montantes, sumideros y cunetas de los CAR: coeficiente uniforme C = 0.88 (simplificación conservadora, criterio
  del proyecto, no exigencia de la norma).
- Colector frontal: C ponderado por superficie de cada proyecto, C = Σ(C·A)/ΣA, porque recibe toda el área del predio
  incluidas las áreas verdes que infiltran.
- Barranquita: C por celda de 1 m² según la superficie que la cubre (ver §8.2); el C de cada tramo es el ponderado de su área
  acumulada.
- Comparación "C = 0.88 vs ponderado" de la plantilla de las memorias (decía 7.2 % en las tres; corregido el 20-10-2026):
  CAR Mujeres 25.0 % (C 0.704), Hogar de Refugio 9.0 % (C 0.807), CAR Varones 14.2 % (C 0.771). Fórmula: (0.88/C − 1)·100.

### 6.4 Superficies y C ponderado por proyecto
| Proyecto | Área (m²) | Σ C·A (m²) | C ponderado | Fuente |
|---|---|---|---|---|
| CAR Varones (2705619) | 6,752.03 | 5,203.32 | 0.771 (0.7707) | su memoria (área 6,752.029 m²; antes se citaba 6,752.06, corregido) |
| Hogar de Refugio (2675514) | 7,520.41 | 6,072.36 | 0.807 (0.8074; antes se escribía 0.808, corregido) | su memoria |
| CAR Mujeres (2717013) | 7,491.56 (fichas) | 5,274.45 | 0.704 | su memoria |
| Total 3 proyectos | 21,764.00 | 16,550.13 | – | – |

CAR Mujeres por tipo: techos TR4 3,654.58 m², concreto frotachado 816.87, estacionamiento asfaltado 812.65, áreas verdes
2,206.56 → 7,490.66 m² (diferencia de 0.90 m² con las fichas por redondeo; 0.1 L/s).

Barranquita (dentro del cerco, `hidrologia_b.superficies`): techos 5,476.7 m² (coberturas 4,129.6 + patio cívico techado
517.7 + losa multiusos techada 829.4), áreas libres de concreto 861.1 (patios 01 a 04: 118.8 / 194.2 / 257.9 / 87.7; veredas,
circulaciones, atrio y losa de tratamiento 202.5), patio de maniobra y estacionamiento 647.3, áreas verdes 2,379.7. En la malla
de 1 m²: 5,548 / 901 / 623 / 2,321 = 9,393 m², C ponderado 0.761. Contrastado con el cuadro de áreas de la memoria de
arquitectura (516 / 810 / 135 / 192 / 255 / 88 m²). La junta cuneta-piso del metrado usa otra clasificación
(`hidrologia_b.pisos_metrado`) que se conserva para no alterar el metrado.

---

## 7. Método racional y caudales

### 7.1 Fórmula
Q = C · I · A · FS / 3,600,000  [m³/s] con I en mm/h y A en m² (equivalente: Q[L/s] = C·I·A·FS/3600).
Con A en ha: Q = C·I·A/360. La memoria del CAR Mujeres expresa I = 210.98 mm/h = 0.00005861 m/s.

### 7.2 Caudales del colector compartido (I = 155.66 mm/h, FS = 1.15)
- CAR Varones: 5,203.32 · 155.66 · 1.15 / 3600 = 258.7 L/s (entregados en la caja CL).
- Hogar de Refugio: 6,072.36 · 155.66 · 1.15 / 3600 = 301.9 L/s.
- Entrega al R-01 del CAR Mujeres: 258.7 + 301.9 = 560.6 L/s (560.68 sin redondear, por eso el límite se escribe 560.7).
- CAR Mujeres: 5,274.45 · 155.66 · 1.15 / 3600 = 262.3 L/s.
- Total en la salida: 258.7 + 301.9 + 262.3 = 822.9 L/s.
- Si se usara 210.98 saldrían 350.7 / 409.3 / 355.5 L/s: error que tenía la memoria del CAR Varones (decía que sus 258.7 L/s
  salían con 210.98) y su celda de comprobación DATOS B13 daba 350.7; corregido: Q = ROUND(5203.32·155.66·FS/3600; 1) = 258.7.
- Hipótesis declarada: suma de picos sin desfase de hidrogramas y con FS 1.15 = conservadora.
- Cada proyecto es independiente: en el Refugio, el CAR Varones es "aporte externo, dato de su memoria, sin validarla" y el CAR
  Mujeres es el "receptor". Si un proyecto vecino no se ejecuta, el colector funciona con capacidad sobrante; si cambia su
  caudal o su punto de entrega, se verifica de nuevo.

### 7.3 Reparto del caudal entre cunetas y caudal a lo largo del colector
- CAR Mujeres: 262.3 L/s en partes iguales (1/4) a las cunetas de los Ejes 02, 07, 10 y 12 (65.6 L/s cada una). Caudal en el
  colector: 626.2 (0+000, Eje 02, con los 560.6 externos), 691.8 (0+037.95, Eje 07), 757.4 (0+049.38, Eje 10), 822.9 L/s
  (0+060.15, Eje 12, hasta la salida).
- Hogar de Refugio: reparto nominal 301.9/6 entre los Ejes 01, 02, 06, 07, 11 y 12 (hoja CAUDALES); el perfil se verifica con
  el caudal total 560.6 L/s en todo el tramo (conservador).
- CAR Varones: reparto de los 258.7 L/s por **franja de frente** que drena cada cuneta: el frente va del lindero este
  (x = 349262.0) al lindero con el Refugio (x = 349162.0); los límites de franja son los puntos medios entre cunetas vecinas;
  fracción = ancho de franja / ancho total; Q = ROUND(258.7 × fracción; 1) y la cuneta del Eje 08 absorbe el ajuste para que
  la suma sea exacta (`varones/diseno_v.py`, hoja CAUDALES de `varones/memoria_v.py`).

| Cuneta Varones | Franja (m) | Fracción | Q (L/s) | Progresiva | Entra en |
|---|---|---|---|---|---|
| Eje 09 | 13.34 | 0.1334 | 34.5 | 0+007.01 | colector (RV-01) |
| Eje 08 | 18.06 | 0.1806 | 46.8 (ajuste) | 0+020.02 | colector (RV-03) |
| Eje 06 | 26.30 | 0.2630 | 68.0 | 0+046.11 | colector (RV-06) |
| Eje 04 | 28.00 | 0.2800 | 72.4 | 0+077.20 | colector (RV-09) |
| Eje 01 | 14.30 | 0.1430 | 37.0 | 0+105.29 | directo a la CL por su muro norte |

  Colector Varones: 221.7 L/s (acumulado escalonado; `caudal_en(p)` = suma de las cunetas aguas arriba de p) + 37.0 directo = 258.7.
  Pregunta del usuario (04-10-2026): "todo debe coincidir, tú ya sabes cuánto caudal vota Varones" → el total siempre es 258.7.
- Barranquita: caudal acumulado por tramo con las áreas propias del eje y las de los ejes que le entregan, sin contar dos veces
  una superficie (§8.2).

---

## 8. Hidráulica de cunetas

### 8.1 Sección y criterios
- CAR (Morales): cunetas rectangulares en U 0.40 × H (interior), muros y losa 0.10, ancho exterior 0.60, pendiente 0.5 %
  (S = 0.005), Manning n = 0.015; canaletas n = 0.013 con S = 1.00 %. Secciones CAR Mujeres: cunetas 0.40 × 0.30
  (edificaciones y guardianía) y 0.40 × 0.25 (losa deportiva); canaletas 0.20 × 0.25 (edificaciones 01 a 10), 0.20 × 0.20
  (guardianía), 0.30 × 0.30 (losa deportiva). Caudales por punto de descarga de techo 1.277 a 6.145 L/s; en cunetas
  3.156 a 42.993 L/s.
- Predimensionamiento de las fichas CAR: sección de máxima eficiencia b0 = 2·y0, luego se redondea a medida constructiva y se
  recalcula el tirante normal por iteración; se verifica que quepan tirante + borde libre.
- Barranquita (criterios del usuario): ancho total 0.60 = muros 0.10 + 0.40 libre; profundidad 0.30 al inicio de cada eje,
  mínima 0.25; S = 0.5 % mínimo; rejilla en tramos abiertos; tapado (losa 0.10) en cruces de vereda e ingresos; con losa, la
  altura libre bajo la losa ≥ 0.25 (profundidad mínima = 0.25 + 0.10). Borde de cuneta al ras del NPT +184.65, área verde
  +184.60, patio de maniobra +184.50 con cuneta al ras (rejilla). "Mantén la cuneta 0.40 interior 0.60 total": si un tramo
  no tiene capacidad, se profundiza; nunca se cambia la sección acordada.
- Manning en Barranquita: n = 0.015 para la capacidad (concreto con rejilla) y n = 0.013 para la velocidad (concreto liso,
  más desfavorable para V máx.) (`verifica_b.N_CAP`, `N_VEL`).
- Borde libre ≥ 0.05 m; velocidad máxima 3.0 m/s (concreto, CE.040); si V > 3.0 → gradas (escalones) de concreto.
- Quiebres a 45° en planta (chaflán de 0.60 m por lado, máximo la mitad del tramo vecino, en esquinas con giro > 50°): el
  usuario lo exige porque una esquina de 90° provoca resalto hidráulico. Los ejes que llegan entran en diagonal (unión en Y).
  En los perfiles no se dibujan.
- Corrección del usuario (21-10-2026): una sección de 15 cm junto al cerco ("¿cómo vas a poner 15 centímetros? ahí se obstruye
  el flujo") → la cuneta llega al pase del cerco con su mismo borde, sin "achicarse" al terreno exterior.
- Empalmes sin escalón: si un empalme obliga a bajar, el fondo baja parejo desde el nudo anterior; un ramal puede entregar con
  caída a otro más profundo (EJE-01 a EJE-02 con 0.42 m).

### 8.2 Caudal por tramo en Barranquita (`verifica_b.py`, comprobaciones 8 y 9)
1. Malla de celdas de 1 m² dentro del cerco; cada celda se asigna al segmento de cuneta más cercano (techos a dos aguas: cada
   mitad cae a la cuneta de su lado, porque la cumbrera queda en el eje largo).
2. C de cada celda: verde 0.40 por defecto, sobrescrito por estacionamiento, pavimento y techo (en ese orden de prioridad).
3. Por tramo: A y Σ C·A propios + los totales de los ejes que entregan aguas arriba (recursivo, sin duplicar).
4. Q = I · ΣCA / 3.6e6 · FS con I = 293.18 mm/h y FS = 1.15.
5. S = máx(S del tramo, 0.005); y_cap con n 0.015, y_vel con n 0.013 (bisección entre 1e-4 y 3.0 m); V = Q/(0.40·y_vel).
6. Altura disponible = mín(h al inicio, h al final) − 0.10 si el tramo tiene parte tapada.
7. Cumple si h_disp − y ≥ 0.05 y V ≤ 3.0. Si no cumple, guarda en `hmin_req.json` la profundidad requerida y + 0.05 + 0.005;
   `calcula_b.py` repite diseño ↔ verificación (hasta 8 iteraciones) hasta que no cambie.
8. Resultado vigente (91 tramos, 11 de 11 comprobaciones): Q máx 229.2 L/s (EJE-02 P-03 → D1, A 3,539 m², C 0.692, y 0.453,
   h 0.79, V 1.42); borde libre mínimo 0.128 m (EJE-11 P-48 → P-33, Q 19.1 L/s, h 0.20 libre bajo losa); V máx 1.98 m/s
   (EJE-02 P-07 → P-08, S 2.92 %); pendiente mínima 0.50 %, máxima 2.92 %; sin gradas. `hmin_req.json` vacío: ninguna
   profundidad depende de la lluvia (por eso un cambio de lluvia se rehace con `verifica_b.py --solo-lluvia`,
   Q nuevo = Q anterior × I nueva / I anterior, sin la base del sitio).
9. Caudal por descarga: D1 229.2 (EJE-02), D2 228.9 (EJE-12), D3 166.2 (EJE-07), D4 45.5 L/s (EJE-17). Cotas de fondo de
   salida: D1 183.759, D2 183.758, D3 183.736, D4 184.145. Las láminas impresas DC-16 a DC-19 rotulan todavía "AGUA DE
   DISEÑO" 207.7 / 264.7 / 174.2 / 48.4 L/s (planos impresos: no se regeneran; avisado).

### 8.3 Capacidad de la cuneta de 0.40 m (referencia calculada con la fórmula de `diseno_b.q_manning`, S = 0.5 %, BL 0.05)
Q = (1/n)·A·R^(2/3)·S^(1/2), A = 0.40·y, R = 0.40·y/(0.40 + 2y), y = h − 0.05.

| h interior (m) | Q n = 0.015 (L/s) | Q n = 0.013 (L/s) |
|---|---|---|
| 0.25 | 81.2 | 93.7 |
| 0.30 | 109.0 | 125.7 |
| 0.35 | 137.6 | 158.8 |
| 0.40 | 167.0 | 192.7 |
| 0.50 | 227.1 | 262.0 |
| 0.60 | 288.4 | 332.8 |
| 0.80 | 413.1 | 476.7 |

En tramo tapado h es la altura libre bajo la losa.

### 8.4 Canaletas y montantes
- Canaleta (Manning, n = 0.013, S = 1 %): Barranquita 0.25 × 0.20 con 0.05 de borde libre conduce 48.1 L/s.
- Montantes por Wyly-Eaton con relación de llenado rs = 0.25: Q (gpm) = 27.8 · rs^(5/3) · D^(8/3) (D en pulgadas,
  1 L/s = 15.85 gpm), o Q (L/s) = 1.754 · rs^(5/3) · D^(8/3); D requerido = (Q·15.85 / (27.8·rs^(5/3)))^(3/8).
  4" = 7.0 L/s; 3" = 3.26 L/s. Se adopta 4" (supera el mínimo del artículo 12.5 de la CE.040). CAR Mujeres: D requerido 2.468
  a 3.821" → 4". Barranquita: cada m² de techo aporta 0.88 · 293.18 / 3.6e6 · 1.15 = 0.0824 L/s → un montante de 4" atiende
  hasta 85.1 m² en proyección horizontal; número mínimo de montantes por lado = ceil(área del lado / 85.1).
- Bancas OC-01 del Refugio (techos a una agua 3.79, 4.21 y 3.79 m × 2.40): C 0.88, I 210.98, FS 1.15, canaleta 0.18 × 0.21
  (galvanizada e = 0.50 mm, S 0.5 %, n 0.013): Q < 0.6 L/s por techo, tirante 0.012 m, D requerido 1.59" → bajada 4". La
  sección queda definida por la cobertura y la limpieza de hojas, no por la hidráulica.

### 8.5 Lloraderos
Los lloraderos (PVC Ø 3" @ 1.50 m con filtro de grava y geotextil, solo en muros de cuneta junto a área verde) no aportan un
caudal que cambie el dimensionamiento: el agua infiltrada ya está en el coeficiente de escorrentía del área verde.

---

## 9. Hidráulica del colector frontal

### 9.1 Datos de diseño por tramo
| Dato | CAR Varones | Hogar de Refugio | CAR Mujeres |
|---|---|---|---|
| b interior | 0.60 | 0.80 | 1.50 |
| Muros / fondo / losa superior | 0.15 / 0.15 / 0.10 | 0.15 / 0.15 / 0.10 | 0.10 / 0.10 / 0.10 |
| Losa en cruce de camiones | 0.25 (portón cisterna 5.78 m + 0.30: 0+000 a 0+006.08) | 0.25 (OE-01 4.415 m + 0.30 a cada lado: 0+026.32 a 0+031.33); motos 0+039.04 a 0+041.04 | 0.20, muros 0.15, fondo 0.20 (0+054 a 0+060); autos 0+002.74–0+018.45 y 0+035.04–0+051.86 |
| n (Manning) | 0.015 | 0.015 | 0.015 |
| S | 0.30 % | 0.30 % | 0.302 % (258.72 − 258.30)/139.08 |
| Cota de fondo inicio → fin | 260.20 → 259.884 | 259.10 → 258.89 (brink) | 258.72 → 258.30 |
| Longitud | 105.29 (quiebre 0+100.90) | 73.39 hasta R-01 (brink 0+069.89; quiebres 45° en 0+058.81 y 0+066.89) | 139.08 |
| Losa superior (= vereda / piso) | +261.15 | +260.60 | +259.25 hasta 0+078.42; luego h interior 0.60 constante |
| Q de diseño | 221.7 escalonado por cuneta | 560.6 constante | 626.2 → 822.9 escalonado |
| Control aguas abajo | caída libre a la CL (yc en el fin) | caída libre a la poza CC (yc en el brink) | vertido sobre la cresta de la Carretera Oasis |

Niveles fijados por el usuario: Refugio NPT 260.60 ("para que esté a nivel de estacionamientos e ingresos"; la cota 260.45 del
ingreso OE-01 estaba mal); Varones 261.15 en los Ejes 01, 04 y 06 y en todo el frente (colector al ras), entrada de camiones
cisterna solo junto al Eje 09.

Altura interior h = (losa superior − espesor de losa de la zona) − cota de fondo. Refugio: 1.34 m (cruce de camiones) a 1.61 m.
Varones: 0.70 m en 0+000 (bajo losa 0.25) a 1.17 m. Mujeres: 0.43 a 0.67 m en vereda, 0.60 en el tramo final.

### 9.2 Criterios de verificación (iguales en los tres)
- Llenado y/h ≤ 0.85 (el conducto cubierto siempre funciona como canal a superficie libre).
- Borde libre ≥ 0.05 m bajo la cara inferior de la losa.
- Régimen subcrítico, Froude < 1 en todo el tramo (salvo la sección de control).
- V mínima 0.90 m/s con el caudal de diseño (autolimpieza, CE.040); V máxima 3.0 m/s (concreto, valor conservador).
- Esfuerzo tractivo τ = γ·R·S ≥ 0.15 kg/m² (1.5 Pa) con caudales parciales hasta el 5 % del de diseño (criterio ASCE/WEF de
  autolimpieza de colectores: arrastre de arena fina). τ [kg/m²] = 1000 · R · S.
- Capacidad con llenado del 85 % en la altura mínima, como margen frente al caudal de diseño.
- Cunetas que llegan: su cota de fondo en el muro del colector por encima del nivel de agua del colector (caída libre, no
  remansa).
- Compatibilidad con los vecinos: cota de fondo y nivel de agua en cada empalme comprobados en ambos expedientes.
- Pedido del usuario (03-10-2026): "no sobredimensionar, ahorrar acero; el 0.3 % de pendiente, ¿la velocidad evita
  sedimento?" → se verificó la autolimpieza con τ y caudales parciales; la sección no se agrandó.

### 9.3 Tirante normal, crítico y Froude
- Manning: Q = (1/n)·A·R^(2/3)·S^(1/2), A = b·y, P = b + 2y, R = A/P.
- Tirante normal por bisección (`diseno.yn`): intervalo [1e-4, 5.0], 200 iteraciones; si Q(y) > Q baja el límite superior.
- Tirante normal por punto fijo (en Excel, 8 iteraciones):
  y0 = (Q·n / (b·√S))^(3/5) ;  y(k+1) = (Q·n·(b + 2·y(k))^(2/3) / (b^(5/3)·√S))^(3/5).
- Tirante crítico rectangular: yc = (Q² / (g·b²))^(1/3), g = 9.81.
- Froude: F = V / √(g·y). Si yn > yc → pendiente suave, régimen subcrítico.
- Resultados con Q de diseño: Refugio yn 0.518, yc 0.369, V 1.35 m/s, F 0.60. Varones (221.7 L/s) yn 0.343, yc 0.241,
  V 1.08 m/s, F 0.59.

### 9.4 Perfil de flujo gradualmente variado (paso estándar)
Ecuación de energía entre la estación 2 (aguas abajo, conocida) y la 1 (aguas arriba):
z1 + y1 + V1²/2g = z2 + y2 + V2²/2g + Δx · (Sf1 + Sf2)/2 ;  Sf = (n·V / R^(2/3))².

Algoritmo (`diseno.paso_estandar`, `varones/diseno_v.paso_estandar`):
1. Estaciones en orden decreciente de progresiva: cada 1 m (Refugio y Varones; cada 2 m en el CAR Mujeres) más los puntos
   singulares (quiebres, llegadas de cuneta, registros, límites de zonas de carga, brink).
2. En la primera estación (control) y = tirante de control (yc en el brink o el que da el vertedero).
3. Para cada estación aguas arriba: resolver y1 por bisección en [1.001·yc(Q1, b1), 3.0] con 100 iteraciones sobre
   f(y1) = (z1 + y1 + V1²/2g) − (E2 + Δx·(Sf1 + Sf2)/2); si f > 0 baja el límite superior. Así siempre se toma la rama
   subcrítica.
4. Con caudal creciente aguas abajo (Varones, Mujeres), Q1 = caudal del tramo de esa estación (escalón en cada cuneta); con
   Q1 = 0 (antes de la primera cuneta) la estación queda seca.
5. En cada estación: NA = z + y; techo = losa − espesor; h = techo − z; llenado = y/h; BL = techo − NA; F; zona;
   ok = llenado ≤ 0.85 y BL ≥ 0.05 y F < 1.
6. Perfil resultante en el Refugio: tipo M2 (el tirante crece hacia aguas arriba hacia el normal).

Excel (`memoria_xlsx.hoja_perfil`): la misma bisección con 30 iteraciones en columnas auxiliares P en adelante
(pares lo/hi), fórmula f(y) = y + V²/2g + z − E2 − Δx·(Sf + Sf2)/2. Resumen: llenado máximo, BL mínimo, Froude máximo sin el
brink, estaciones que no cumplen, NA en 0+000.

Resultados:
| Tramo | Estaciones | Llenado máx. | BL mín. | Froude | V (m/s) |
|---|---|---|---|---|---|
| Refugio | 85 | 0.372 | 0.834 m | ≤ 0.93 (sin brink) | 1.38 a 1.90 |
| Varones | 110 (memoria PDF) | 0.341 | 0.630 m | ≤ 0.92 (sin el fin) | hasta 1.54 |
| CAR Mujeres | 75 | 0.815 | 0.087 m (Eje 02); 0.091 en el cruce de camiones | 0.51 a 0.74 | 1.02 a 1.43 |

Capacidad con llenado 85 % en la altura mínima (fórmula de la hoja CUMPLIMIENTO: Q85 = (1/n)·b·0.85h·R^(2/3)·√S):
Varones 445 L/s (h 0.70, `capacidad_85` de `diseno_v`); Refugio ≈ 1,478 L/s (h 1.34), es decir, margen de unas 2.6 veces.

### 9.5 Velocidades y autolimpieza (flujo uniforme, Refugio b 0.80, S 0.3 %)
| Caso | Q (L/s) | yn (m) | V (m/s) | τ (kg/m²) | F |
|---|---|---|---|---|---|
| Caudal de diseño | 560.6 | 0.518 | 1.35 | 0.677 | 0.60 |
| Solo CAR Varones | 258.7 | 0.291 | 1.11 | 0.505 | 0.66 |
| Solo Refugio | 301.9 | 0.325 | 1.16 | 0.538 | 0.65 |
| 50 % | 280.3 | 0.308 | 1.14 | 0.522 | 0.65 |
| 25 % | 140.2 | 0.189 | 0.93 | 0.385 | 0.68 |
| 10 % | 56.1 | 0.102 | 0.69 | 0.244 | 0.68 |
| 5 % | 28.0 | 0.065 | 0.54 | 0.169 | 0.67 |

Con el 5 % del caudal τ sigue ≥ 0.15 kg/m²: la pendiente de 3 ‰ basta; más desnivel obligaría a profundizar la caja de caída.
En Varones los tramos de cabecera tienen V < 0.90 (0.60 es el ancho mínimo practicable para limpieza): la autolimpieza se
asegura por τ con el caudal propio de cada tramo y por registros cada ≤ 12 m (criterio escrito en la hoja PERFIL_FLUJO).

### 9.6 Caída libre y caja de llegada CL (Refugio 0+000)
- CL: 1.50 × 1.00 m interior, poza 0.30 m bajo la cota de fondo inicial (piso 258.80). Queda del lado del CAR Varones
  (x = 349162.00 a 349163.80); tapa al ras del piso de Varones +261.15 (escalón de 0.55 m con el piso del Refugio +260.60);
  techo interior 261.05.
- Llegada de Varones por ventana 0.60 × 1.17 en el muro este (alféizar = cota de fondo 259.884); cuneta Eje 01 de Varones por
  ventana 0.40 × 0.66 en el muro norte (NCF 260.394, caída libre 0.788 m).
- Caída del aporte: 259.884 − 258.80 = 1.084 m; colchón de agua = NA 259.606 − 258.80 = 0.806 m ≥ 0.50 m (cumple).
- Comprobación de compatibilidad: la cota de llegada debe quedar entre NA de la CL + 0.10 (caída libre) y el techo de la CL.

### 9.7 Caja de caída CC con poza de disipación (entrega Refugio → R-01 del CAR Mujeres)
Por qué: la vereda del Refugio está ≈ 1.35–1.50 m más alta que la del CAR Mujeres (259.25) y el NA del receptor (259.062) es
menor que el que tendría el canal de 0.80 con su tirante normal; una transición por ensanche estrangularía el flujo. El usuario
pidió (03-10-2026) no agrandar el colector y "hacer un disipador de energía para que no erosione" en la entrega.

Cálculo (`diseno.disenar`, hoja EMPALME):
1. Brink al final del canal 0.80: z = 258.890; yc = 0.369 m; NA = 259.259 (control del perfil).
2. Piso de la poza = cota de fondo del R-01 − 0.40 = 258.32. Caída = 258.890 − 258.32 = 0.570 m.
3. Energía al pie respecto al piso: E1 = caída + 1.5·yc = 1.123 m (sin pérdidas, conservador).
4. Tirante al pie: y1 + (Q/(b·y1))²/2g = E1 (bisección en [1e-3, yc], rama supercrítica) → y1 = 0.161 m; V1 = 4.344 m/s;
   F1 = 3.453. En Excel y1 se escribe como valor (cálculo circular) con fila de verificación y1 + V1²/19.62 = E1.
5. Resalto en el ancho del colector (conservador, sin contar la expansión a 1.50): y2 = y1/2 · (√(1 + 8·F1²) − 1) = 0.711 m.
6. Tirante disponible = NA del receptor − piso = 259.062 − 258.32 = 0.742 m ≥ y2 → resalto ahogado, cumple.
7. Longitud: L resalto ≈ 6·y2 = 4.27 m; poza adoptada 3.50 m ≥ 0.8 × 6·y2 = 3.41 m (criterio USBR para resalto ahogado).
8. Poza 3.50 × 1.50 m, 0.40 m de profundidad, umbral de salida de 0.40 m hasta el fondo del R-01; sale en régimen subcrítico
   (F ≈ 0.67 en el receptor).
9. Ventana de salida de la CC hacia el R-01: 1.50 × 0.43 = alto interior del colector receptor en su R-01
   (259.25 − 0.10 − 258.72). Antes se dibujaba de 0.60 (pasaba por encima del piso del CAR Mujeres): corregido el 15-10-2026.

### 9.8 Vertedero de cresta ancha en la salida del CAR Mujeres
- La salida rebalsa sobre la berma hasta la cresta de la Carretera Oasis (258.54 msnm): vertedero de cresta ancha,
  Q = Cw·Lw·H^1.5 con Cw = 1.70 m^0.5/s y Lw = 4.00 m (salida con dos aleros a 45°; la uña mide 2.91 m y el agua se abre sobre
  la berma).
- H = (Q/(Cw·Lw))^(2/3) = (0.823/(1.70 × 4.00))^(2/3) = 0.245 m → NA de vertido = 258.785 msnm.
- Nivel crítico en la salida: yc = 0.313 m → 258.30 + 0.313 = 258.613.
- Nivel de control = máx(NA vertido, NA crítico) = 258.785 (gobierna el remanso de la vía); desde allí el paso estándar hacia
  aguas arriba. Recomendación escrita: no elevar la berma ni la calzada frente a la salida sin reevaluar el colector; el
  cruce de la vía (badén o alcantarilla) queda fuera del alcance y se comunica a la entidad de la vía.

### 9.9 Llegada de las cunetas al colector
- Ventana 0.40 × H en el muro del lado del predio, caída libre al fondo del colector, junta de tecnopor 1" y registro encima.
- Si la cuneta termina antes del muro se prolonga con la misma sección y pendiente: NCF en el muro = NCF al cerco − 0.005 ×
  prolongación; si entra dentro del colector se acorta: NCF en el muro = NCF extremo + 0.005 × acortamiento.
- Refugio: caídas libres 0.131 (Eje 02, la más baja, NCF 259.70) a 0.627 m (Eje 11); prolongaciones de 1.88 (Eje 11) y 5.39 m
  (Eje 12). La cota de fondo inicial 259.10 la fija la cuneta del Eje 02.
- Varones: acortamientos 0.04, 0.10, 0.26, 3.39 y 2.77 m; caídas 0.27, 0.243, 0.089, 0.142 m y 0.788 (Eje 01 a la CL).
- CAR Mujeres: cunetas Ejes 02, 07, 10 y 12 en R-01, R-05, R-06 y R-07 con NCF 258.73, 258.74, 258.74 y 258.80.

---

## 10. Formato de los entregables de hidrología e hidráulica

### 10.1 Memoria hidrológica (Word), estructura de los estudios de Morales
1. Aspectos generales: introducción, objetivos (general y específicos), ubicación política y acceso, ubicación hidrográfica,
   clima, estación meteorológica de referencia.
2. Estudio hidrológico: introducción, metodología (a–i: recopilación, revisión de calidad y conformación de la serie,
   representatividad, caracterización estadística, ajuste y selección, precipitaciones e intensidades, áreas tributarias y tc,
   coeficientes y caudales, integración con la hidráulica), análisis estadístico de datos (cobertura, tabla mensual con S/D,
   máximos), representatividad (Barranquita: contraste con Tarapoto), análisis de intensidades (I = Pd/td), análisis de
   frecuencia (P(X ≥ xT) = 1/T; cuatro distribuciones con fórmulas y tablas), pruebas de bondad de ajuste, evaluación del ajuste
   (tabla K-S dato por dato y resumen), curvas IDF (Bell + regresión + Dick y Peschke), tiempo de concentración (Kirpich, SCS),
   periodo de retorno (riesgo), intensidad máxima de diseño.
3. Cálculo de caudales: coeficiente de escorrentía (tabla CE.040, adoptado), áreas de drenaje (techos, áreas libres, verdes,
   estacionamiento, con figuras), intensidad de lluvia, caudales de diseño.
4. Drenaje: instalación, parámetros, canaletas y montantes, cunetas, cunetas cubiertas, juntas, profundidades, verificación,
   descargas, presentación de los cálculos (fichas).
5. Conclusiones. 6. Recomendaciones. 7. Anexos (Barranquita: Anexo N.° 01 análisis estadístico y tormenta de diseño con los
   cuadros del CAR: registro, B.1–B.4, K-S, C.4, cuadros N.° 04–06, intensidades, diseño; Anexo N.° 02 planta y perfil típico).
- En los CAR el capítulo "Diseño del colector pluvial frontal" se agrega AL FINAL del Word del usuario sin alterar lo anterior
  (`memoria_docx.py` comprueba que párrafos y tablas originales quedan idénticos). Contenido: alcance y condiciones de
  compatibilidad, trazo, caudal de diseño, dimensionamiento, perfil de flujo, velocidades y autolimpieza, empalme (CC), caja
  CL, llegada de cunetas, verificación estructural, marco normativo, criterios constructivos, resumen de metrados (del RESUMEN
  vigente), cuadro de cumplimiento, datos de otros expedientes y cómo quedan cubiertos, conclusiones; luego el capítulo
  complementario (bancas OC-01 y lloraderos). CAR Mujeres: descripción general, aportes externos, caudal, criterios, perfil,
  secciones, registros, estructura de salida, verificación estructural, conclusiones.
- Barranquita: el usuario pidió más páginas ("¿por qué tan pocas páginas? ¿no tienes de los CAR el ejemplo?") → 29 páginas con
  la estructura de arriba (`hidrologica_doc_b.py`).
- Las tres memorias del colector compartido deben decir lo mismo (P24, I, C ponderados, caudales); cualquier cambio se aplica a
  las tres (`revision_hidrologia.py`).

### 10.2 Excel del análisis estadístico (formato del usuario)
Hojas: A. Estación (registro mensual y máximos, S/D resaltados), B. Modelo Distribución (B.1 Normal, B.2 Log Normal, B.3 LP3,
B.4 Gumbel), C. Prueba Kolmorov-Smirnov, D. Resumen (C.4), A. Parametros (Cuadros N.° 04–06, Bell y regresión),
B. Int. maxima (tabla IDF), C. P diseño (Dick y Peschke por T: D, D en horas, P, I). Encabezado: Proyecto (con CUI o C.I.),
Entidad, Ubicación, Fecha. Para un proyecto nuevo (`analisis_estadistico_b.py`): abrir la plantilla con LibreOffice (UNO),
cargar estación y serie, borrar filas sobrantes (LibreOffice ajusta fórmulas y gráficos), quitar hojas auxiliares (Hoja1, 210),
cambiar títulos de gráficos, corregir MAX(Z22:Z45) a todo el rango, y que "Diseño" siga a la K-S. Cotejar luego cada número de
la memoria contra este Excel (`coteja_analisis_b.py`).

### 10.3 Memoria de cálculo del colector (Excel con fórmulas)
- Hojas: MEMORIA (objeto, normativa, hidrología, hidráulica, estructuras, resultados con fórmulas de resumen), DATOS (parámetro,
  valor, unidad, fuente/criterio, símbolo), CAUDALES, CUNETAS, EMPALME (EMPALME_CL en Varones; SALIDA en el CAR Mujeres),
  PERFIL_FLUJO, ESTRUCTURAL, CUMPLIMIENTO (requisito, norma, criterio, valor, resultado; cada valor es una fórmula).
- Colores: azul = dato editable, negro = fórmula, verde = vínculo a otra hoja. Fórmulas guardadas en inglés (SUM, IF, ROUND,
  separador ","); Excel en español las muestra SUMA, SI, REDONDEAR con ";" (como exige el usuario).
- Recalcular con LibreOffice y leer los valores guardados para Word y PDF.
- PDF con el estilo HIDRO-CE040 solo cuando el usuario lo pide (`memoria_pdf_*`): datos y metodología, datos, caudales,
  cunetas / salida, empalme, perfil de flujo (gráfico y tabla), estructural, cumplimiento y diseño adoptado; firma en blanco.

### 10.4 Memoria de cálculo de Barranquita (Excel)
Hojas: CARÁTULA, RESUMEN, DATOS (filas 5 a 22: P anual Caynarachi, P anual llanura, factor B7, T B8, tc B9, n capacidad 0.015
B10, n velocidad 0.013 B11, b 0.40 B12, BL 0.05 B13, V máx 3.0 B14, P24 B15 = FRECUENCIAS, P en tc B16 =
B15·(B9/1440)^0.25, I B17 = B16·60/B9, C techo B18, C pavimento B19, C estacionamiento B20, C verde B21, FS B22), SERIE
(mensuales, MAX por año, × factor, LOG10), FRECUENCIAS (estadísticos con COUNT, AVERAGE, STDEV, SKEW; tabla T con z, Normal,
LN, KT LP3, LP3, KT Gumbel, Gumbel y Diseño), KS, IDF, SUPERFICIES (4 tipos y detalle por zona), CAUDALES (racional y Manning
por tramo con Q = I·C·A·FS/3,600,000, capacidad y velocidad), DESCARGAS. Aparte: CUADRO_TRAMOS (hojas SECCIONES y TAPAS
INSPECCION).

---

## 11. Marco normativo citado
- RNE CE.040 Drenaje Pluvial (R.M. N.° 126-2021-VIVIENDA, reemplaza a la OS.060): tc mínimo 10 min, periodo de retorno
  (11.1, 11.3), Tabla 1.a de coeficientes, velocidades, montantes (12.5), registros.
- Manual de Hidrología, Hidráulica y Drenaje del MTC: método racional, Dick y Peschke, distribuciones (3.7.1), longitud de
  registro (3.4).
- Chow, Hidráulica de canales abiertos (paso estándar, n del concreto); USBR (poza y resalto); Aparicio (yn, sn de Gumbel).
- EG-2013 MTC Sección 510 (juntas): colector cada 4.00 m; cunetas de Barranquita cada 3.00 m.
- E.020, E.060, E.050 y AASHTO LRFD / Manual de Puentes MTC (parte estructural, otro tema).

---

## 12. Para implementarlo en un programa

### 12.1 Entradas
1. Serie de precipitación máxima en 24 h por mes y año (o archivo diario SENAMHI / NASA POWER / CHIRPS) y datos de la estación
   (nombre, código, altitud, ubicación). Opcional: series de contraste y P anual de estaciones vecinas.
2. Parámetros: T = 25 años, α K-S = 0.05, tc cunetas = 10 min, tc colector (10 + recorrido; 15 en Morales), FS = 1.15,
   duraciones (5, 10, 15, 20, 30, 60, 90, 120, 240, 360, 720, 1440), periodos (2, 5, 10, 20, 25, 50, 100, 200, 500).
3. Coeficientes C por tipo de superficie (§6) y polígonos de cada superficie (techos, áreas libres, estacionamiento, verdes)
   dentro del límite de intervención.
4. Red: ejes de cuneta con nudos, sentido de flujo, rasante (borde) por punto, tramos tapados, descargas; sección (b = 0.40,
   muros 0.10), h inicial 0.30, h mínima 0.25, losa de tapado 0.10, S mínima 0.005, BL 0.05, n capacidad 0.015, n velocidad
   0.013, V máx 3.0.
5. Colector (si hay): b, espesores por zona, n, cota de fondo inicial, S, cota de losa por progresiva, zonas de carga, cunetas
   que llegan (progresiva, NCF, H, caudal o franja), registros, condición de control aguas abajo (caída libre, vertedero o NA
   del receptor) y datos del receptor (cota de fondo, NA, ancho, alto interior) y del aporte externo (Q, cota de llegada).

### 12.2 Algoritmo, en orden
1. Conformar la serie: máximo de cada mes válido; máximo anual = mayor de los meses disponibles; años incompletos se marcan,
   no se rellenan; tomar los 25 años completos más recientes (o los que indique el usuario) y documentar los excluidos.
2. Estadísticos de x, log10 x y ln x (media, s con n − 1, Cs de Excel).
3. Para cada T: z (Abramowitz-Stegun); Normal, Log-Normal, LP3 (Kite) y Gumbel (KT de momentos).
4. K-S: serie de mayor a menor, E = m/(n + 1); P teórica de cada modelo (§4.5); D = máx |P − E|; D crítico por fórmula;
   adoptar la de menor D entre las aceptadas.
5. P24 de diseño = distribución adoptada en T = 25.
6. Dick y Peschke: P_D = P24·(D/1440)^0.25, I_D = 60·P_D/D para todas las duraciones y periodos (tabla de diseño).
7. Bell: P60(10) = 0.4602·P24(10)^0.876; P(T, t) = (0.21 ln T + 0.52)(0.54 t^0.25 − 0.50)·P60(10); I redondeada a 0.1;
   regresión log I = log K + m log T − n log t (ecuaciones normales 3 × 3) → K, m, n. Solo para presentar la IDF.
8. tc: Kirpich, SCS y entrada + conducción por sistema; tc = máx(10, calculado) para cunetas; colector = 10 + recorrido en
   cuneta + recorrido en colector (redondeado; 15 min en Morales).
9. Intensidades de diseño: I(tc cunetas) e I(tc colector), ambas del mismo P24.
10. C: por elemento (uniforme 0.88 en canaletas, montantes, sumideros y cunetas de los CAR) o por celda (Barranquita); C
    ponderado = Σ C·A / Σ A.
11. Caudales: Q = C·I·A·FS/3.6e6. En redes: asignar cada celda de 1 m² al segmento más cercano, acumular aguas abajo con los
    ejes que entregan, sin duplicar. En colectores: Q acumulado por progresiva (escalón en cada cuneta); aportes externos como
    dato; repartir el caudal del predio entre cunetas por franja de frente (puntos medios) o en partes iguales, con ajuste de
    redondeo en una cuneta para que la suma sea exacta.
12. Canaletas y montantes: Manning (n 0.013, S 1 %) y Wyly-Eaton (rs 0.25), diámetro comercial ≥ requerido y ≥ mínimo de norma.
13. Cunetas por tramo: yn (bisección) con n 0.015 y Q; altura disponible (− losa si tapado); BL ≥ 0.05; yv con n 0.013, V ≤ 3.0
    (si no, gradas); S ≥ 0.5 %. Si falta capacidad, subir la profundidad mínima del tramo a y + 0.05 + 0.005 y rehacer la
    rasante de fondo; repetir diseño ↔ verificación hasta que no cambie (máx. 8 vueltas).
14. Colector: yn, yc, V, F con el Q de diseño; nivel de control aguas abajo (yc en caída libre; vertedero H = (Q/(Cw·Lw))^(2/3)
    + cresta; o NA del receptor), tomando el mayor; paso estándar hacia aguas arriba con bisección en la rama subcrítica;
    en cada estación llenado, BL, F, zona y cumplimiento.
15. Autolimpieza: flujo uniforme con Q de diseño, aportes parciales y 50, 25, 10, 5 % del Q; V ≥ 0.90 con Q de diseño o
    τ = 1000·R·S ≥ 0.15 kg/m²; V ≤ 3.0.
16. Empalmes: caída libre de cada cuneta (NCF en el muro − NA del colector > 0); caja de llegada (caída y colchón ≥ 0.50 m);
    caja de caída (E1 = caída + 1.5 yc, y1 por energía, F1, y2 conjugado, tirante disponible ≥ y2, poza ≥ 0.8·6·y2, ventana de
    salida con el alto interior del receptor); cota de fondo de entrega ≥ la del receptor y Q ≤ Q previsto por el receptor.
17. Descargas por el límite de intervención: el terreno exterior debe quedar bajo la cota de fondo de salida a pocos metros
    (≤ 2 m) sin obras fuera del cerco.

### 12.3 Salidas
- Tablas de la serie, estadísticos, frecuencias por T y distribución, K-S dato por dato y resumen, Bell (Cuadros 04–06), IDF,
  Dick y Peschke, tc, riesgo, C y superficies, caudales por elemento / tramo / eje / descarga, verificación hidráulica por
  tramo, perfil de flujo por estación, autolimpieza, empalmes, cuadro de cumplimiento.
- Archivos: Excel del análisis estadístico (formato del usuario), Excel de memoria de cálculo con fórmulas, Word de memoria
  hidrológica, JSON de diseño y verificación (`_calc/diseno.json`, `verificacion.json`, `hmin_req.json`).

### 12.4 Validaciones obligatorias
- Reproducir la hoja del usuario con la serie de Tarapoto: D K-S 0.0920 / 0.0894 / 0.0964 / 0.1270, P24 T25 121.81 mm,
  I10 210.98, I15 155.66, IDF K 161.94, m 0.1786, n 0.5271. Con Pongo de Caynarachi 1989–2013: LP3, D 0.0683, crítico 0.2650,
  169.27 mm, 293.18 mm/h, K 211.66, m 0.1786, n 0.5269.
- Caudales compartidos: 258.7 + 301.9 = 560.6 (≤ 560.7); 262.3; 822.9 L/s; los tres documentos con el mismo número.
- Cotejar cada valor impreso en la memoria con el Excel (0 diferencias) antes de entregar.
- Ningún tramo con llenado > 0.85, BL < 0.05, F ≥ 1 (colector), V > 3.0 sin gradas, S < 0.5 % (cunetas) o contrapendiente.
- La cuneta nunca reduce su sección al llegar a una descarga; los quiebres en planta son a 45°.
- Si un dato viene de otro expediente, mostrarlo como dato con su fuente; si dos expedientes discrepan (área 6,752.03 vs
  6,752.06, C 0.807 vs 0.808), usar el de la memoria del propio proyecto y corregir los demás textos.
- Si cambia la lluvia, comprobar si alguna profundidad dependía de ella (`hmin_req.json`); si no, la geometría, el metrado y
  los planos no cambian y solo se actualizan los documentos.
