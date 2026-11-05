# 03 — Colector pluvial frontal cubierto (diseño completo)

Base de conocimiento del colector pluvial frontal compartido por tres expedientes del predio Los Mangos, Morales (San Martín).
Reúne lo aprendido desde el 3 de octubre de 2026: concepción, datos, cálculo, estructura, registros, empalmes, cajas, juntas,
metrado, coordinación entre expedientes y cada corrección o decisión del usuario, con su fecha y su porqué.

Fuentes de este documento (todas en el repositorio):
- Mensajes del usuario: `conocimiento/_fuentes/mensajes_usuario.txt` (traspaso del 03-10-2026 y correcciones siguientes).
- `BITACORA_CONVERSACION.md`, `CLAUDE.md`, `.claude/skills/diseno-colector-pluvial/SKILL.md`.
- Código: `herramientas/diseno.py` (Refugio), `herramientas/varones/diseno_v.py` y `compat.py` (Varones), `herramientas/mujeres/datos_m.py`
  y `base_m.json` (Mujeres), `memoria_xlsx.py`, `varones/memoria_v.py`, `metrado_calc.py`, `tapa_ciega.py`, `ventana_cc_refugio.py`,
  `varones/registro_sobre_muros_v.py`, `junta_*.py`, `renombrar_juntas_colector.py`, `dxf_*.py`, `render_tapa/dxf_tapa_ciega.py`.
- Resultados guardados: `entregables/_calc/diseno.json` (Refugio), `entregables_varones/_calc/diseno.json` (Varones).
- Planillas vigentes: `insumos/metrados_vigentes/*.xlsx`, `insumos/wilma/METRADO_DRENAJE_PLUVIAL_CAR_MUJERES.xlsx` (congelada).

Convenciones del documento:
- Cotas en m s. n. m.; longitudes en m; progresivas "0+xxx.xx". Siempre "cota de fondo" (CF), nunca "invert".
- Los proyectos se citan por nombre y CUI. En la conversación el usuario los nombra por la responsable de cada expediente
  (Katiuska = CAR Varones, Solange = Hogar de Refugio, Wilma = CAR Mujeres); en los documentos nunca se usa el nombre de una persona.
- NCT = nivel de cuneta terminada (borde superior); NCF = nivel de cota de fondo de cuneta; NPT = nivel de piso terminado; NA = nivel de agua;
  BL = borde libre; h = altura interior libre del colector (cara inferior de la losa superior menos cota de fondo).

---

## 1. Qué es el colector frontal y por qué es así

### 1.1 Concepción
- Canal rectangular de concreto armado f'c = 210 kg/cm², vaciado monolíticamente (losa de fondo + 2 muros + losa superior) formando un
  marco cerrado. La losa superior queda al ras del piso terminado del frente y funciona como vereda (acabado frotachado).
- Cubierto en todo su recorrido: por seguridad, porque los tres predios son centros con niños, niñas, adolescentes o mujeres víctimas
  de violencia; no se deja canal abierto en el frente. Por ser cubierto no lleva lloraderos (los lloraderos son solo de cunetas).
- Limpieza por registros con tapa removible (cada 12 m como máximo y en cada llegada de cuneta).
- Todo dentro del lindero del predio, sin invadir la faja de la Carretera Oasis (vía frente a los tres predios).
- Recoge las cunetas de piso de cada predio que llegan al frente y entrega aguas abajo al tramo vecino. El ancho crece aguas abajo:
  0.60 (Varones) → 0.80 (Refugio) → 1.50 (Mujeres).
- Régimen subcrítico en todo el colector; perfil de flujo por el método del paso estándar desde el control aguas abajo.
- Llenado y/h ≤ 85 %; borde libre ≥ 0.05 m bajo la losa superior.
- Acero según la carga de cada zona (peatonal, motos/autos, camiones), sin sobredimensionar (pedido expreso del usuario, 03-10-2026).

### 1.2 Cadena hidráulica (de aguas arriba hacia aguas abajo)
CAR Varones (b 0.60) → caja de llegada CL (expediente del Refugio) → Hogar de Refugio (b 0.80) → caja de caída CC con poza
(expediente del Refugio) → registro R-01 del CAR Mujeres (b 1.50) → estructura de salida con aleros → berma de la Carretera Oasis.

### 1.3 Resumen de los tres tramos

| Dato | CAR Varones (CUI 2705619) | Hogar de Refugio (CUI 2675514) | CAR Mujeres (CUI 2717013) |
|---|---|---|---|
| Papel en la cadena | aguas arriba | intermedio | receptor final |
| Ancho interior b | 0.60 | 0.80 | 1.50 |
| Muros | 0.15 | 0.15 | 0.10 (0.15 en cruce de camiones) |
| Losa de fondo | 0.15 | 0.15 | 0.10 (0.20 en cruce de camiones) |
| Losa superior | 0.10 (0.25 en camiones) | 0.10 (0.25 en camiones) | 0.10 (0.20 en camiones) |
| Ancho exterior | 0.90 | 1.10 | 1.70 (1.80 en camiones) |
| Solado | 0.05, f'c 100 | 0.05, f'c 100 | 0.05, f'c 100 |
| Longitud | 105.29 (0+000 a cara este de la CL) | 69.89 hasta el brink; 73.39 hasta la cara del R-01 | 139.08 (R-01 a la salida) |
| Cota de fondo inicial | 260.20 | 259.10 | 258.72 |
| Cota de fondo final | 259.884 | 258.890 (brink) | 258.30 (salida) |
| Pendiente | 0.30 % | 0.30 % | 0.302 % (0.42 / 139.08) |
| Losa superior (NPT) | +261.15 en todo el frente | +260.60 | +259.25 hasta 0+078.42; después h = 0.60 constante |
| Altura interior h | 0.70 (camiones) a 1.17 (CL) | 1.33 (camiones) / 1.40 (0+000) a 1.61 (brink) | 0.43 a 0.67 en vereda; 0.60 tramo final |
| Caudal de diseño | 221.7 L/s por el colector + 37.0 L/s directo a la CL = 258.7 | 258.7 + 301.9 = 560.6 L/s | 560.6 + 262.3 = 822.9 L/s |
| Registros | 11 (RV-01 a RV-11) | 10 (RS-01 a RS-07 + 1 en CL + 2 en CC) | 15 (R-01 a R-15) |
| Juntas de dilatación | 26 (cada 4.00 m) | 17 (cada 4.00 m) | 33 (cada 4.00 m + 2 en camiones) |
| Cerco en el frente | no hay cerco | sí: colector pegado por fuera del cerco | lindero con la vía |
| Cruces | camiones cisterna 0+000.00 a 0+006.08 | camiones 0+026.32 a 0+031.33; motos 0+039.04 a 0+041.04 | autos 2.74-18.45 y 35.04-51.86; camiones 54.00-60.00 |
| Entrega | caída libre a la CL (ventana 0.60 × 1.17) | caída a poza de la CC, ventana 1.50 × 0.43 al R-01 | salida con 2 aleros a 45°, emboquillado |
| Estado del metrado | vigente 23-10-2026 | vigente con bancas OC-01 | congelado (ya presupuestado) |

---

## 2. Hidrología común a los tres expedientes

### 2.1 Lluvia de diseño
- Periodo de retorno TR = 25 años; P24 = 121.81 mm (análisis estadístico de los CAR, estación CO Tarapoto).
- Distribución temporal de Dick y Peschke (exponente 0.25): P(t) = P24 · (t / 1440)^0.25, con t en minutos.
  - P10 = 35.163 mm → I10 = P10 · 60 / 10 = 210.98 mm/h.
  - P15 = 38.91 mm → I15 = 155.66 mm/h.
  - P20 = 41.816 mm → I20 = 125.45 mm/h.
- Implementación (`diseno.intensidad`): b = ln(P20 / P10) / ln 2 (= 0.25), I = P10 · (tc / 10)^b / (tc / 60). Con tc = 15: 155.66 mm/h.

### 2.2 Por qué el colector usa 155.66 mm/h y las cunetas 210.98 mm/h
- Cunetas, canaletas, montantes y sumideros: tc = 10 min (mínimo CE.040) → I = 210.98 mm/h.
- Colector: recoge todo el predio y el aporte de aguas arriba; su tiempo de concentración es tc = 10 (entrada) + 3 (recorrido en cunetas)
  + 2 (recorrido en el colector) = 15 min → I = 155.66 mm/h, sobre la misma curva precipitación-duración.
- El usuario preguntó el 03-10-2026 (16:43) "por qué pones 35.163 mm si el diseño es 210": son la misma lluvia; 35.163 mm en 10 min
  equivalen a 210.98 mm/h. El 20-10-2026 pidió justificarlo en las tres memorias hidrológicas: se agregó con `revision_hidrologia.py`
  un bloque idéntico en las tres ("Intensidad de diseño: 210.98 mm/h en cunetas y 155.66 mm/h en el colector").
- En `varones/diseno_v.D` quedaron los campos I = 210.98 y tc = 10 heredados; no intervienen en el cálculo (el caudal se toma de
  Q_total = 258.7 L/s). La memoria de Varones dice correctamente que sus 258.7 L/s salen con I = 155.66 (tc 15 min).

### 2.3 Método racional y caudales
- Q = Σ(C·A) · I · FS / 3600 (Q en L/s, A en m², I en mm/h); FS = 1.15 (factor de seguridad de las memorias HIDRO-CE040).
- Coeficientes del traspaso: techos y veredas 0.88; estacionamientos 0.86; áreas verdes 0.29; patios 0.40.

| Proyecto | Área (m²) | Σ C·A (m²) | C ponderado | Q con I = 155.66 y FS 1.15 |
|---|---|---|---|---|
| CAR Varones | 6,752.03 (antes 6,752.06) | 5,203.3213 | 0.771 | 258.7 L/s |
| Hogar de Refugio | 7,520.41 | 6,072.3596 | 0.807 (antes se escribió 0.808) | 301.9 L/s |
| CAR Mujeres | 7,491.56 | 5,274.4494 | 0.704 | 262.3 L/s |
| Total en la salida | 21,764.00 | | | 822.9 L/s |

- Suma de picos sin desfase de tiempos, con FS 1.15: hipótesis conservadora declarada en las memorias.
- Cada expediente toma el aporte externo como dato de la memoria del otro, sin validarlo ("aporte externo"); el proyecto aguas abajo es
  el "receptor".
- Condiciones del receptor (CAR Mujeres) para el aporte conjunto: Q ≤ 560.7 L/s y cota de fondo de llegada ≥ 258.72.
- Correcciones de coherencia del 20-10-2026 (solo textos): área de Varones 6,752.03; C del Refugio 0.807; el "7,2 %" de la plantilla
  pasa a 25.0 % (Mujeres, C 0.704), 9.0 % (Refugio, C 0.807) y 14.2 % (Varones, C 0.771); la celda DATOS B13 de Varones daba 350.7
  (con 210.98) y ahora 258.7.

### 2.4 Reparto del caudal a lo largo de cada tramo
- CAR Varones: los 258.7 L/s se reparten entre las 5 cunetas que llegan al frente en proporción al ancho de frente que drena cada una
  (franjas limitadas por los puntos medios entre ejes, del lindero este x = 349262.0 al lindero con el Refugio x = 349162.0; suman
  100.0 m). El redondeo se ajusta en la segunda cuneta para que la suma sea exactamente 258.7.

| Cuneta Varones | Franja (m) | Q (L/s) | Entra a |
|---|---|---|---|
| Eje 09 | 13.34 | 34.5 | colector (0+007.01) |
| Eje 08 | 18.06 | 46.8 | colector (0+020.02) |
| Eje 06 | 26.30 | 68.0 | colector (0+046.11) |
| Eje 04 | 28.00 | 72.4 | colector (0+077.20) |
| Eje 01 | 14.30 | 37.0 | directo a la CL (muro norte) |
| Total | 100.00 | 258.7 | 221.7 por el colector + 37.0 directo |

- Hogar de Refugio: 258.7 entran en la CL (0+000); el aporte propio (301.9) se reparte nominalmente entre sus 6 cunetas (301.9 / 6) en la
  hoja CAUDALES, pero el perfil se verifica con el caudal total de 560.6 L/s en todo el tramo (conservador).
- CAR Mujeres: 560.6 en el R-01 más 262.3 propios repartidos en 4 cunetas (≈ 65.6 cada una): 626.2 (Eje 02, 0+000) → 691.8 (Eje 07, R-05)
  → 757.3 (Eje 10, R-06) → 822.9 L/s (Eje 12, R-07). El receptor declara Q = 626.1 L/s y NA 259.062 en su 0+000.

---

## 3. Tramo CAR Varones (CUI 2705619)

### 3.1 Geometría en planta
- Coordenadas en el sistema local del plano de arquitectura del Refugio; la planta de Varones se traslada con
  `insumos/katiuska/transform_varones_a_solange.json`. Frente leído en `insumos/katiuska/frente_varones_marco_solange.json`.
- No hay cerco perimetral en el frente de Varones (corrección del usuario, 04-10-2026 17:03): la polilínea "CERCO" del código es solo la
  línea de referencia del frente (límite de las áreas exteriores del plano). A ambos lados del colector hay terreno natural.
- Eje del colector = paralela a la línea del frente a 0.475 m hacia el predio (0.025 de holgura + 0.15 muro + 0.30 medio ancho),
  calculada con `_offset` (bisectriz corregida para mantener la distancia).
- Progresivas desde el poste derecho del portón de camiones (0+000, extremo este) hacia la caja CL (extremo oeste).
- Último tramo: desde el punto donde el eje corta y = eje de la CL, recta horizontal (perpendicular al lindero) hasta la cara este
  exterior de la CL (x = 349163.80): tramo de empalme de 4.39 m, del quiebre 0+100.90 a 0+105.29.
- La CL (del expediente del Refugio) ocupa x = 349162.00 a 349163.80 del lado de Varones (1.50 interior + 2 × 0.15).

### 3.2 Niveles (decisión del usuario, 04-10-2026 06:09)
- "El colector todo debe estar a 261.15, al ras justo de lo de afuera": los ejes 06, 04 y 01 y la franja exterior están a +261.15.
- La losa superior se mantiene en +261.15 hasta la CL; la tapa de la CL se sube a +261.15 (piso de Varones).
- CF0 = 260.20 en 0+000; S = 0.30 %; CF final = 260.20 − 0.003 × 105.29 = 259.884.
- h = 261.15 − 0.25 − 260.20 = 0.70 en el cruce de camiones; 0.85 en 0+006.08; 1.17 (1.166) en la llegada a la CL.

### 3.3 Cruce de camiones
- Única entrada de camiones (cisternas) por el Eje 09, lado derecho, de 5.78 m ("5.80" según el usuario); "el colector arranca allí".
- Zona CAMION = 0+000.00 a 0+006.08 (5.78 + 0.30 de holgura). No hay cruce de motos en Varones.
- Ningún registro dentro del cruce (el primero, RV-01, está en 0+007.01).

### 3.4 Cunetas que llegan y acortamiento
- Las cunetas son las rectas perpendiculares al frente (norte-sur, x constante), no la línea negra del plano (corrección 04-10-2026 17:18).
- Están dibujadas hasta la franja exterior del frente; el colector ocupa esa franja, por eso cada cuneta termina en la cara del muro lado
  predio (a b/2 + e = 0.45 del eje) y el tramo que caía dentro del colector se descuenta en todas las hojas de cunetas (pedido del usuario
  04-10-2026 06:12: "eso se tiene que restar").
- `cruce_vertical(x, lateral)` da la progresiva donde la vertical x de la cuneta corta el eje desplazado 0.45 (cara del muro).
- ajuste_L = distancia del extremo dibujado a la cara del muro: positivo = prolongar, negativo = acortar. NCF en el muro = NCF dibujado −
  0.005 × ajuste_L (misma pendiente 0.5 %).

| Cuneta | Prog. empalme | Longitud dibujada | Acortamiento | Longitud metrada | NCF en el muro | H ventana | Caída libre sobre NA |
|---|---|---|---|---|---|---|---|
| Eje 09 | 0+007.01 | 42.70 | 0.04 | 42.66 | 260.69 | 0.36 | 0.270 |
| Eje 08 | 0+020.02 | 60.70 | 0.10 | 60.60 | 260.65 | 0.40 | 0.243 |
| Eje 06 | 0+046.11 | 98.95 | 0.26 | 98.69 | 260.461 | 0.59 | 0.089 |
| Eje 04 | 0+077.20 | 105.70 | 3.39 | 102.31 | 260.437 | 0.61 | 0.142 |
| Eje 01 | CL (muro norte) | 114.30 | 2.77 | 111.53 | 260.394 | 0.66 | 0.788 (sobre NA de la CL) |

- Las cunetas de los Ejes 02, 03, 05 y 07 no llegan al frente y no cambian. Hoja de la planilla: "CUNETAS - LLEGADA AL COLECTOR".

### 3.5 Registros de Varones (algoritmo de `diseno_v.py`)
1. Un registro en cada empalme de cuneta que entra al colector (aguas arriba del quiebre).
2. Si entre dos registros (o entre 0+000 y el primero) hay más de 12 m, se dividen en n = ceil(gap / 12) partes iguales.
3. Un registro en el quiebre (inicio del tramo de empalme con la CL).
4. Se numeran RV-01 a RV-11 en orden de progresiva. La CL no se numera (su registro es del Refugio).

| Registro | Progresiva | Nota |
|---|---|---|
| RV-01 | 0+007.01 | empalme cuneta Eje 09 |
| RV-02 | 0+013.52 | limpieza |
| RV-03 | 0+020.02 | empalme cuneta Eje 08 |
| RV-04 | 0+028.72 | limpieza |
| RV-05 | 0+037.41 | limpieza |
| RV-06 | 0+046.11 | empalme cuneta Eje 06 |
| RV-07 | 0+056.47 | limpieza |
| RV-08 | 0+066.84 | limpieza |
| RV-09 | 0+077.20 | empalme cuneta Eje 04 |
| RV-10 | 0+089.05 | limpieza |
| RV-11 | 0+100.90 | quiebre, inicio del tramo de empalme con la CL |

- Corrección del 04-10-2026 17:03: las tapas deben ir exactamente donde entrega cada cuneta (antes se dibujaban corridas).

### 3.6 Hidráulica de Varones (resultados de `entregables_varones/_calc/diseno.json`)
- Caudal variable por tramo: `caudal_en(p)` = suma de las cunetas que entran aguas arriba de p (0 antes del Eje 09).
- Control aguas abajo: caída libre a la CL → tirante crítico en el fin del colector: yc = (Q² / (g b²))^(1/3) = 0.241 m con Q = 221.7 L/s;
  NA de control = 259.884 + 0.241 = 260.125.
- Tirante normal con 221.7 L/s: yn = 0.343 m, V = 1.08 m/s, F = 0.59 (subcrítico, pendiente suave).
- Perfil (119 estaciones): llenado máximo 0.341, borde libre mínimo 0.630 m, F < 1 en todo el colector (F = 1 solo en el borde de caída),
  V de 0.21 a 1.54 m/s (las velocidades bajas están en la cabecera remansada por el control aguas abajo).
- Capacidad con llenado del 85 % en la sección más desfavorable (h mínima 0.70, cruce de camiones): 445 L/s, 2.0 veces el caudal de diseño.
- Llegada a la CL: caída libre del fondo 259.884 sobre el NA de la CL 259.606 = 0.278 m (≥ 0.10, cumple); caída total al piso de la poza
  (258.80) = 1.084 m; colchón en la CL = 259.606 − 258.80 = 0.806 m (≥ 0.50).
- Ventana en el muro este de la CL: 0.60 × 1.17 (alféizar 259.884, techo 261.05 = 261.15 − 0.10); sin dintel: techo de la CL = techo del
  colector = 261.05.
- Autolimpieza: V ≥ 0.90 m/s con el caudal de diseño en la entrega y, en cada tramo entre empalmes, V ≥ 0.90 m/s o τ = γ R S ≥ 0.15 kg/m²
  con su propio caudal. En la cabecera la velocidad es menor de 0.90 m/s porque 0.60 es el ancho mínimo practicable para limpieza; allí
  la autolimpieza se asegura por esfuerzo tractivo y por los registros cada 12 m como máximo. Ejemplo con tirante normal: Eje 09 solo
  (34.5 L/s): yn 0.092, V 0.62, τ 0.21 kg/m² (cumple por τ); 81.3 L/s: V 0.82, τ 0.32; 149.3 L/s: V 0.97.

### 3.7 Por qué el ancho de 0.60 (y la pregunta del "1.40")
- 0.60 es el ancho mínimo práctico para la limpieza manual; con él el llenado es solo 34 % y la capacidad al 85 % es el doble del caudal.
- El 16-10-2026 el usuario preguntó "en CAR Varones el ancho del colector es 1.40?": 1.40 m es el ancho de la zanja de excavación
  (ancho exterior 0.90 + 2 × 0.25 de sobreancho), no del colector; profundidades de excavación de 1.10 a 1.75 m.

---

## 4. Tramo Hogar de Refugio Temporal (CUI 2675514)

### 4.1 Emplazamiento (decisión del 03-10-2026)
- Discusión inicial (05:16): el colector del CAR Mujeres llega al límite del terreno con la Carretera Oasis, pero el cerco del Refugio está
  más adentro. Opciones: proyectar las cunetas hasta el lindero, o pegar el colector a lo proyectado. Se adoptó: colector pegado por fuera
  del cerco perimetral frontal, dentro del lindero, con junta de 1" contra el cimiento del cerco.
- Eje del colector a 0.575 m del paramento exterior del cerco (0.025 junta + 0.15 muro + 0.40 medio ancho).
- Sistema local del plano PLANTA GENERAL REFUGIO: lindero con Varones x = 349162.00 (X_NE), extremo suroeste x = 349090.98 (X_SO),
  cerco sur y = 9281917.79; eje y = 9281917.215; frente de 71.02 m (el traspaso decía ≈ 71.10).
- R-01 del CAR Mujeres (hipótesis de ubicación local): (349090.98, 9281911.50), sobre la prolongación del lado oeste del cerco, 0.75 m
  dentro del lindero frontal (lindero local y = 9281910.8).
- Trazo: recta pegada al cerco de 0+000.00 a 0+058.81 (quiebre 1), diagonal a 45° de 5.715 m de desnivel en planta (8.08 m de eje)
  hasta 0+066.89 (quiebre 2), recta final de 6.50 m (3.00 de colector + 3.50 de poza) hasta la cara del R-01: brink en 0+069.89, fin de la
  estructura en 0+073.39. Cada quiebre lleva registro.
- UTM WGS 84 zona 18 S por traslación y giro haciendo coincidir el R-01 (E 345666.974, N 9282776.560, igual en ambos expedientes) y el
  rumbo del lindero del CAR Mujeres (azimut 49.54°); ubicación referencial, verificar en campo. El usuario preguntó "¿qué UTM quieres?"
  (03-10-2026 05:31); al no haber coordenadas del cerco se usó esa hipótesis y se rotuló "ubicación referencial".

### 4.2 Niveles
- NPT del frente = +260.60 (decisión del usuario, 03-10-2026 05:26): "a nivel de estacionamientos e ingresos; si ves 260.45 en el ingreso
  OE-01 está mal, es igual 260.60". El traspaso decía NT 260.60 + 0.15 = 260.75 y se había propuesto 260.65: se descartaron.
- CF0 = 259.10 en 0+000: fijada por las cunetas del proyecto (la más baja llega con NCF 259.70, Eje 02) y por la llegada de Varones.
- S = 0.30 %: CF en el brink = 259.10 − 0.003 × 69.887 = 258.890 ≥ 258.72 (R-01). El usuario preguntó si 0.3 % basta para no sedimentar
  (03-10-2026 13:42): se verificó con velocidades y esfuerzo tractivo (ver 4.6).
- h = 260.50 − CF: 1.40 en 0+000 a 1.61 en el brink; en el cruce de camiones (losa 0.25) h = 1.33.
- La CL lleva la tapa en +261.15 (piso de Varones): escalón de 0.55 m respecto del frente del Refugio (+260.60), con murete de 0.15 en el escalón.

### 4.3 Accesos y zonas de carga (corrección del 03-10-2026 05:26 a 05:33)
- No es "losa vehicular en los 71 m": hay una entrada peatonal, un portón de motos pequeño (lado izquierdo) y un ingreso de autos y
  vehículos pesados (cisterna al PTAR / pozo séptico) de 4.41 m.

| Zona | Vano | Holgura por lado | Progresivas | Armado |
|---|---|---|---|---|
| CAMION (ingreso vehicular OE-01) | 4.415 m (x 349130.965 a 349135.38) | 0.30 | 0+026.32 a 0+031.33 | losa 0.25, doble marco 1/2" @0.15 |
| MOTOS (portón) | 1.77 m (x 349121.07 a 349122.84) | 0.115 | 0+039.04 a 0+041.04 | marco 3/8" @0.15 |
| NORMAL (vereda peatonal) | resto | - | - | marco 3/8" @0.20 |

- Progresivas de zona: p1 = X_NE − x2 − holgura; p2 = X_NE − x1 + holgura.

### 4.4 Cunetas del Refugio que llegan (perfiles 01 a 12 del plano de arquitectura del 03-10-2026)

| Cuneta | Prog. | NCF al llegar | NCT | H | Prolongación | NCF en el muro | NA colector | Caída libre |
|---|---|---|---|---|---|---|---|---|
| Eje 01 (perimetral este) | 0+001.07 | 260.12 | 260.60 | 0.48 | (junta) | 260.12 | 259.603 | 0.517 |
| Eje 02 (estacionamiento) | 0+011.27 | 259.70 | 260.60 | 0.90 | (junta) | 259.70 | 259.569 | 0.131 |
| Eje 06 (ingreso vehicular) | 0+032.50 | 259.75 | 260.60 | 0.85 | (junta) | 259.75 | 259.493 | 0.257 |
| Eje 07 | 0+042.68 | 259.72 | 260.60 | 0.88 | (junta) | 259.72 | 259.453 | 0.267 |
| Eje 11 (tramo diagonal) | 0+060.89 | 260.00 | 260.60 | 0.60 | 1.88 | 259.991 | 259.364 | 0.627 |
| Eje 12 (perimetral oeste) | 0+069.56 (entra a la CC) | 259.80 | 260.60 | 0.80 | 5.39 | 259.773 | 259.278 | 0.495 |

- Prolongación hasta el muro: si la cuneta llega al tramo pegado al cerco basta la junta (0.025); en el tramo diagonal
  prolong = Y_CERCO − (y_eje + b_ext/2 / cos 45°); en el tramo final / CC prolong = Y_CERCO − (y_R01 + 1.50/2 + 0.15).
- Las prolongaciones de los Ejes 11 y 12 (1.88 y 5.39 m) se metran en las partidas de cunetas, no en el colector (ver 9.4).
- La cuneta Eje 01 del propio Refugio entra por el muro lado predio del colector en 0+001.07 (no confundir con la Eje 01 de Varones,
  que entra a la CL por su muro norte).

### 4.5 Registros del Refugio

| Elemento | Progresiva | Nota |
|---|---|---|
| CL | 0+000.00 | caja de llegada: CAR Varones y cuneta Eje 01 de Varones (1 tapa) |
| RS-01 | 0+011.27 | empalme cuneta Eje 02 |
| RS-02 | 0+022.00 | limpieza |
| RS-03 | 0+032.50 | empalme cuneta Eje 06 |
| RS-04 | 0+042.68 | empalme cuneta Eje 07 |
| RS-05 | 0+052.00 | limpieza |
| RS-06 | 0+058.81 | quiebre 1 (45°) y empalme cuneta Eje 11 |
| RS-07 | 0+066.89 | quiebre 2 (45°) |
| CC | 0+069.89 | poza de disipación y empalme cuneta Eje 12 (2 tapas sobre la poza) |

- Total con tapa: 7 + 1 (CL) + 2 (CC) = 10. Separación máxima 11.27 m. Ninguno dentro de los cruces (RS-02 en 22.00 queda antes del cruce
  de camiones 26.32-31.33; RS-03 en 32.50 después).

### 4.6 Hidráulica del Refugio (resultados de `entregables/_calc/diseno.json`)
- Q = 560.6 L/s en todo el tramo (258.7 + 301.9, valores de las memorias de cada proyecto).
- Tirante normal yn = 0.518 m, V = 1.35 m/s, F = 0.60; tirante crítico yc = 0.369 m (yn > yc: pendiente suave, subcrítico).
- Control: brink de la caída a la poza de la CC (0+069.89, CF 258.890): yc = 0.369, NA = 259.259.
- Perfil por paso estándar (85 estaciones: cada 1 m + quiebres, cunetas, registros y límites de zona), de aguas abajo hacia aguas arriba:
  NA en 0+000 = 259.606 (y = 0.506), llenado máximo 0.372, borde libre mínimo 0.834 m, F de 0.62 a 0.81 dentro del colector
  (1.0 solo en el brink), V de 1.38 a 1.90 m/s. Todas las estaciones cumplen.
- Capacidad con llenado del 85 % y h mínima (1.33, cruce de camiones): 1,464 L/s = 2.6 veces el caudal de diseño.
- Velocidades y autolimpieza (tirante normal, S 0.3 %, n 0.015):

| Caso | Q (L/s) | yn | V (m/s) | τ (kg/m²) | Resultado |
|---|---|---|---|---|---|
| Diseño (Varones + Refugio) | 560.6 | 0.518 | 1.35 | 0.68 | V ≥ 0.90 cumple |
| Solo Varones | 258.7 | 0.291 | 1.11 | 0.51 | cumple |
| Solo Refugio | 301.9 | 0.325 | 1.16 | 0.54 | cumple |
| 50 % | 280.3 | 0.308 | 1.14 | 0.52 | cumple |
| 25 % | 140.2 | 0.189 | 0.93 | 0.39 | cumple |
| 10 % | 56.1 | 0.102 | 0.69 | 0.24 | cumple por τ |
| 5 % | 28.0 | 0.065 | 0.54 | 0.17 | cumple por τ (≥ 0.15) |

- Conclusión de la memoria: con 3 ‰ se cumplen 0.90 ≤ V ≤ 3.0 m/s con el caudal de diseño y el colector se autolimpia hasta con el 5 %.

### 4.7 Decisión del usuario sobre el tamaño (03-10-2026 13:38 y 13:42)
- "No puedes disminuir el arranque o altura del colector de Solange; no debe ser muy grande, solo suficiente para llevar las aguas de
  Katiuska y Solange; al entregar a Wilma haz un disipador de energía para que no erosione" → caja de caída CC con poza de disipación.
- "Quiero ahorrar acero, veo 5000 kilos; no sobredimensionar; es un expediente técnico que firman especialistas" → se pasó de doble capa a
  un solo marco cerrado en el eje de muros y losas (E.060 14.3.4 permite una capa en espesores ≤ 0.20) en el tramo normal y de motos; el
  acero del colector quedó en ≈ 3,056 kg (≈ 38 kg/m en tramo normal según la memoria), dejando doble marco solo en el cruce de camiones.
- 03-10-2026 16:36: el usuario preguntó si al corregir los dibujos se aumentaron secciones o espesores; no, los cambios de esa fecha fueron de
  dibujo y el metrado no varió por ellos.

---

## 5. Tramo CAR Mujeres (CUI 2717013) – receptor, ya diseñado y congelado

### 5.1 Datos (hoja DATOS de `insumos/wilma/METRADO_COLECTOR_PLUVIAL_CAR_MUJERES.xlsx` y `mujeres/datos_m.py`)
- b = 1.50; muros y losas 0.10; cruce de camiones: muros 0.15, losa de fondo 0.20, losa superior 0.20.
- CF 258.72 en el R-01 (0+000, Eje 02; la cuneta Eje 02 llega con NCF 258.73) → 258.30 en la salida (0+139.08); S = 0.302 %.
- NPT de vereda +259.25 hasta 0+078.42 (fin del tramo en vereda, quiebre C-1); después altura interior constante h = 0.60 con losa
  monolítica (cara superior = CF + 0.60 + 0.10).
- Eje a 0.85 m del lindero; los últimos 4 m se desvían 0.85 m hacia el predio para la salida con aleros.
- Cruces: autos 2.74-18.45 (rampa estacionamiento 01) y 35.04-51.86 (rampa estacionamiento 02); camiones 54.00-60.00 (ingreso secundario).
- Armado: marcos 3/8" @0.20 en vereda y tramo final; 3/8" @0.15 en cruces de autos; 2 marcos 1/2" @0.15 en el cruce de camiones
  (recubrimiento 0.045); longitudinales @0.25 (@0.20 en camiones).
- 15 registros R-01 a R-15 (separaciones de 9.13 a 11.43 m); 33 juntas; esponjamiento 1.25; pesos 3/8" 0.56 y 1/2" 0.994 kg/m.
- Cunetas que llegan: Eje 02 en R-01 (NCF 258.73), Eje 07 en R-05 (258.74), Eje 10 en R-06 (258.74), Eje 12 en R-07 (258.80).

### 5.2 Hidráulica del receptor
- Control en la salida: la calzada de la Carretera Oasis (cresta 258.54) obliga a calcular el vertido: Q = Cw · Lw · H^1.5 con Cw = 1.7
  (cresta ancha) y Lw = 4.00 m (el agua sale por la uña de 2.91 m y se abre sobre la berma) → H = 0.245 m, NA de control 258.785.
- Perfil por paso estándar desde la salida hasta el Eje 02 con el caudal que entra en cada eje: NA inicial 259.063 en el R-01
  (y = 0.343), llenado máximo 0.815, borde libre mínimo 0.087 m (0.091 m en el cruce de camiones), F de 0.51 a 0.74, V de 1.02 a 1.43 m/s.

### 5.3 Estructura de salida con dos aleros (DP-07, luego ESDAE-01)
- Aleros de concreto armado e = 0.15, L = 1.00 inclinados a 45° (avance 0.707 en planta), altura 0.70 sobre el piso en el cabezal y 0.45
  en el extremo; zapata 0.45 × 0.20; ancho interior al final de los aleros 2.914 m; horizontales 3/8" @0.20 (5 por alero).
- Uña de concreto ciclópeo f'c 140 + 30 % P.M.: base 0.35, corona 0.15, alto 0.65.
- Emboquillado de piedra e = 0.20 con concreto f'c 140 sobre relleno compactado e = 0.10 (base del emboquillado dentro de la partida de
  relleno: criterio del ingeniero de presupuesto, "rellenos menores van dentro de la partida de relleno").
- Toda la estructura queda dentro del lindero; el agua vierte sobre la berma (cresta 258.54). El cruce de la vía (badén o alcantarilla) queda
  fuera del alcance; se recomienda comunicarlo a la entidad de la vía.
- Metrado (partidas 1.4.4.6.3.2 y 1.4.4.6.4.2): uña 0.522 m³; aleros concreto 0.4125 m³, encofrado 4.095 m², acero 18.23 kg; emboquillado 1.56 m².

### 5.4 Estado
- Metrado congelado (ya presupuestado): no se modifica. Partida 1.4.4.6.5.1 sigue "TAPA DE REGISTRO 0.68x0.68 C/MARCO Y CONTRAMARCO"
  (15 und) aunque la lámina DP-06B / D-RL y la memoria indican tapa ciega: pendiente de decisión del usuario.
- Pendiente: la tapa del R-07 (0+060.15, rebaje 0+059.80 a 0+060.50) entra 0.20 m en el cruce de camiones (54-60) y solo está verificada
  para rueda de auto (con HL-93: Mu 3.1 > φMn 1.12). Confirmar por dónde pasan los camiones.
- Códigos de lámina renombrados por el usuario (20-10-2026): DP-04 → ST-CG-01 y ST-CG-02; DP-06A → STP-CG; DP-07 → ESDAE-01;
  DP-09 → IC-01; registro D-RL; empalme D-ECC.

---

## 6. Predimensionamiento y elección de la sección

### 6.1 Qué fija cada dimensión
- Cota de la losa superior: fija = NPT del frente (la losa es la vereda). No se elige.
- Cota de fondo inicial: la más alta posible que (a) quede por debajo de la cuneta más baja que llega menos su caída libre sobre el NA y
  (b) permita la llegada del tramo de aguas arriba con caída libre (Refugio: Varones llega en 259.884 ≥ NA 259.606 + 0.10).
- Cota de fondo final: ≥ cota de fondo del receptor (Refugio: 258.890 ≥ 258.72).
- Pendiente: la que cabe entre ambas cotas con régimen subcrítico y autolimpieza; se adoptó 0.30 % (prediseño 0.5 % en el traspaso).
- Altura interior h: resulta (NPT − e_losa − CF); por eso h es grande (1.40 a 1.61 en el Refugio) aunque el tirante sea 0.50.
- Ancho b: el menor que cumple llenado ≤ 85 %, BL ≥ 0.05, F < 1 y permite limpieza; crece aguas abajo con el caudal.
- Espesores: 0.15 en muros y fondo de Varones y Refugio (muros de hasta 1.65 m de altura); 0.10 en Mujeres (h ≤ 0.67).

### 6.2 Tabla de verificación del ancho

| Tramo | Q (L/s) | b | yn | Llenado máx. del perfil | Q al 85 % con h mín. | Margen |
|---|---|---|---|---|---|---|
| Varones | 221.7 | 0.60 | 0.343 | 0.34 | 445 L/s | 2.0 |
| Refugio | 560.6 | 0.80 | 0.518 | 0.37 | 1,464 L/s | 2.6 |
| Mujeres | 822.9 | 1.50 | tirante del perfil 0.34-0.49 | 0.815 | - | (gobierna el llenado) |

- En Varones y Refugio el ancho no lo gobierna la capacidad sino la altura (fijada por cotas) y la limpieza; por eso una variación razonable
  del caudal del vecino "no compromete el tramo" (texto de la memoria: "la sección tiene capacidad para más del doble del caudal").
- En Mujeres gobierna el llenado (h pequeña de 0.43 a 0.67): por eso b = 1.50.

---

## 7. Perfil hidráulico: método y verificaciones

### 7.1 Fórmulas
- Manning: Q = (1/n) · A · R^(2/3) · S^(1/2); A = b·y; R = b·y / (b + 2y); n = 0.015 (concreto vaciado in situ, Chow).
- Tirante normal: bisección en [1e-4, 5] (200 iteraciones) o punto fijo y(k+1) = (Q n (b + 2 y(k))^(2/3) / (b^(5/3) S^(1/2)))^(3/5) (Excel, 8 iteraciones).
- Tirante crítico (rectangular): yc = (Q² / (g b²))^(1/3), g = 9.81.
- Paso estándar (de aguas abajo, estación 2, hacia aguas arriba, estación 1):
  z1 + y1 + V1²/2g = z2 + y2 + V2²/2g + Δx · (Sf1 + Sf2)/2, con Sf = (n V / R^(2/3))².
  Se resuelve y1 por bisección en [1.001·yc, 3.0] (rama subcrítica), 100 iteraciones; en Excel, 30 iteraciones de bisección en columnas.
- Caudal variable (Varones): Q en cada estación = suma de las cunetas aguas arriba; si Q = 0 la estación queda seca.
- En cada estación: NA = z + y; F = V / sqrt(g y); techo = NPT − e_losa(zona); h = techo − z; llenado = y/h; BL = techo − NA.
- Cumple si llenado ≤ 0.85, BL ≥ 0.05 y F < 1 (en el borde de caída se acepta F = 1).

### 7.2 Controles aguas abajo usados
- Caída libre a una caja con NA más bajo que el fondo (Varones → CL; Refugio → poza de la CC): tirante crítico en el borde.
- Vertido sobre un control externo (Mujeres → cresta de la vía): NA = cresta + H del vertedero.
- Si la entrega estuviera ahogada se tomaría el NA del receptor.

### 7.3 Estaciones
- Cada 1.00 m más todos los puntos singulares: quiebres, empalmes de cuneta, registros, límites de zona y fin del colector.

### 7.4 Normativa hidráulica
- RNE CE.040 Drenaje Pluvial (R.M. N.° 126-2021-VIVIENDA, reemplaza a la OS.060): V mínima 0.90 m/s con el caudal de diseño; V máxima
  3.0 m/s (concreto, valor conservador); accesibilidad para mantenimiento.
- Esfuerzo tractivo τ = γ R S ≥ 0.15 kg/m² (1.5 Pa) para caudales parciales (criterio ASCE/WEF).
- Manual de Hidrología, Hidráulica y Drenaje (MTC); Chow, Hidráulica de canales abiertos (flujo gradualmente variado).

---

## 8. Estructura

### 8.1 Modelo y normas
- Marco cerrado monolítico (losa de fondo, muros y losa superior vaciados juntos).
- Cargas RNE E.020 (peso propio, sobrecarga peatonal), empuje del relleno en reposo, rueda de camión HL-93 de AASHTO LRFD / Manual de
  Puentes MTC con impacto 33 % en el ingreso vehicular, rueda de 1 t en el portón de motos (y en las tapas). Diseño por resistencia E.060
  (U = 1.4 D + 1.7 L; φ = 0.90 flexión, 0.85 cortante). Suelos E.050 (sin EMS al diseñar: capacidad a confirmar).

### 8.2 Parámetros

| Símbolo | Valor | Fuente |
|---|---|---|
| f'c | 210 kg/cm² | E.060 |
| fy | 4200 kg/cm² | grado 60 |
| γ concreto armado | 2.4 t/m³ | E.020 |
| γ suelo / relleno | 1.8 t/m³ | verificar con EMS |
| Ko (reposo) | 0.5 | relleno compactado contra muro rígido |
| s/c peatonal | 0.5 t/m² | E.020 |
| s/c lateral vehículo liviano | 1.0 t/m² | - |
| s/c lateral camión (h eq 1.50 m) | 2.7 t/m² | AASHTO 3.11.6.4 |
| Rueda liviana / moto | 1.0 t | - |
| Rueda HL-93 | 7.26 t | AASHTO |
| Impacto IM | 0.33 | AASHTO 3.6.2 |
| Huella de rueda c | 0.25 m | AASHTO 3.6.1.2.5 |
| Luz de cálculo Lc | b + e_muro (centro a centro) | Refugio 0.95; Varones 0.75 |
| Ancho de franja E | 0.66 + 0.55 · Lc | AASHTO 4.6.2.1.3 |

### 8.3 Fórmulas por elemento (hoja ESTRUCTURAL de `memoria_xlsx.py` y `varones/memoria_v.py`)
- A. Losa superior tramo normal (e 0.10, 3/8" @0.20): wu = 1.4 γc e + 1.7 sp; Mu = wu Lc²/8; d = e/2 (marco único en el eje);
  As = 0.71/0.20 = 3.55 cm²/m; a = As fy / (0.85 f'c 100); φMn = 0.9 As fy (d − a/2) / 10⁵ (t·m/m); As mín = 0.0018 · 100 · e(cm).
- B. Losa superior cruce de motos (3/8" @0.15): Mr = P (1 + IM)(Lc/4 − c/8) / E; Mu = 1.4 γc e Lc²/8 + 1.7 Mr; As = 0.71/0.15.
- C. Losa superior cruce de camiones (e 0.25, doble marco 1/2" @0.15): Mr con P = 7.26 t; d = (e − 0.04)·100 − 0.635 cm; As = 1.27/0.15;
  Vu = 1.7 P (1 + IM)(Lc − d − c/2)/Lc/E + 1.4 γc e Lc/2; φVc = 0.85 · 0.53 · sqrt(f'c) · 100 · d / 1000 (t/m).
- D. Muro tramo normal (e 0.15, 3/8" @0.20): p = Ko γs H; q = Ko sp; M = p H²/20 + q H²/12 (miembro de marco cerrado con extremos
  empotrados: triangular + uniforme); Mu = 1.7 M; d = e/2; Vu = 1.7 (p H/2 · 0.6 + q H/2).
- E. Muro cruce de motos: q = Ko · 1.0; As 3/8" @0.15.
- F. Muro cruce de camiones: q = Ko · 2.7; d = (e − 0.04)·100 − 0.635; As 1/2" @0.15 (una capa por cara). Varones usa H del cruce
  (HF = 0.70 + S · 6.08 = 0.72).
- G. Losa de fondo (e 0.15, 3/8" @0.20): W = γc (b + 2e)(et + ef) + 2 γc e H; Ww = 1.0 · b · H + sp (b + 2e); q = (W + Ww)/(b + 2e);
  Mu = 1.5 q Lc²/8; presión sobre el suelo σ = q/10 (kg/cm²); se compara con 0.50 kg/cm² (mínimo usual en suelos blandos).
  Varones agrega el cruce de camiones con la rueda HL-93 repartida en 2.50 m (σ ≈ 0.63 kg/cm², carga transitoria, cumple si el EMS lo confirma).
- H. Tapa de registro 0.68 × 0.68 × 0.08, 3/8" @0.10: L = 0.64 (luz 0.60 + 0.02 de apoyo por lado); E = mín(0.66 + 0.55 L, 0.68);
  Mr con rueda de 1 t e IM; d = (0.08 − 0.025)·100 − 0.48 cm; As = 0.71/0.10.

### 8.4 Resultados (Refugio, H = 1.61; Varones, H = 1.17)

| Elemento | Refugio Mu | Refugio φMn | Varones Mu | Varones φMn | Resultado |
|---|---|---|---|---|---|
| A. Losa superior normal | 0.134 | 0.615 | 0.083 | 0.615 | cumple (As 3.55 ≥ 1.80) |
| B. Losa superior motos | 0.432 | 0.795 | - | - | cumple |
| C. Losa superior camiones | 2.958 | 6.199 | 2.451 | 6.199 | cumple; Vu 9.48 / 8.91 < φVc 13.30 t/m |
| D. Muro normal | 0.411 | 0.950 | 0.169 | 0.950 | cumple; Vu 1.53 < φVc 4.90; As 3.55 ≥ 2.70 |
| E. Muro motos | 0.503 | 1.242 | - | - | cumple |
| F. Muro camiones | 0.815 | 2.998 | (con HF 0.72) | 2.998 | cumple |
| G. Losa de fondo | 0.563 | 0.950 | 0.296 | 0.950 | cumple; σ 0.33 / 0.28 kg/cm² < 0.50 |
| H. Tapa 0.68 × 0.08 | 0.442 | 1.123 | 0.442 | 1.123 | cumple (rueda liviana) |

(Mu y φMn en t·m/m.)

### 8.5 Armados adoptados
- Tramo normal (Refugio y Varones): un solo marco cerrado 3/8" @0.20 en el eje de muros y losas + longitudinales 3/8" @0.25 (una capa;
  E.060 art. 14.3.4 exige dos capas solo en muros de más de 0.20 m). Ganchos de cierre del marco 0.30 (2 × 0.15).
- Cruce de motos (Refugio): marco único 3/8" @0.15, longitudinales @0.25.
- Cruce de camiones (Refugio y Varones): losa superior 0.25 y doble marco 1/2" @0.15 (exterior e interior, una capa en cada cara),
  longitudinales 3/8" @0.20, recubrimiento 0.04.
- CAR Mujeres: ver 5.1. El traspaso del 03-10-2026 fijaba como criterio: vereda e 0.10 con marco 3/8" @0.20 y longitudinal 3/8" @0.25;
  cruce de autos marco 3/8" @0.15; cruce de camiones muros 0.15, losas 0.20 y doble marco 1/2" @0.15.
- Recubrimientos (E.060 7.7): 0.04 en muros y losa de fondo (contacto con el suelo, sobre solado); 0.025 en la losa superior del tramo normal
  (no expuesta); 0.04 en el cruce de camiones; 0.025 en tapas; 0.045 en el cruce de camiones de Mujeres.
- Traslapes (E.060 cap. 12, clase B): 0.40 (3/8") y 0.50 (1/2"), alternados; barras comerciales de 9.00 m.
- Curado húmedo mínimo 7 días; no transitar sobre la losa antes de 14 días; no cargar con camiones antes de 28 días.

### 8.6 Perímetros de marco (metrado y cuadro de doblado, `metrado_calc.perimetros_marco`)
- Marco único (normal y motos): per = 2 (be − em) + 2 (ef/2 + h + et/2) + 0.30, con be = b + 2 em.
  Ej. Refugio normal: 2 × (1.10 − 0.15) + 2 × (0.075 + h + 0.05) + 0.30 = "2 × (0.95 + h + 0.125) + 0.30".
- Cruce de camiones: per_ext = 2 (be − 2·0.04) + 2 (ef + h + et − 2·0.04) + 0.30; per_int = 2 (b + 2 (em − 0.04)) + 2 (h + 2 (em − 0.04)) + 0.30.
- N.° de marcos por segmento = REDONDEAR.MAS(L / s); N.° de longitudinales = redondeo(per / s_long) por cada marco; longitud de
  longitudinales = n · L · (1 + 0.40 / 9.00).

---

## 9. Empalme de cunetas al colector

### 9.1 Detalle constructivo (DP-06C, DD-04)
- Ventana de 0.40 × Hv en el muro del lado del predio, dejada en el vaciado con un cajón de madera 0.40 × Hv × 0.15 (se retira a los 2 días);
  su fondo en la NCF de la cuneta; llega hasta la losa superior, sin dintel.
- Hv = techo del colector − NCF en el muro.
- Refuerzo de borde de la ventana: 2 barras 3/8" verticales a cada lado (4), L = Hv + 0.60 (anclaje 0.30 abajo y gancho en la losa), y 2
  horizontales de 1.00; los marcos 3/8" se interrumpen en la ventana con gancho de 0.10 bajo el alféizar.
- Caída libre al fondo del colector; fondo pulido (mortero 1:3, e = 1 cm) en 1.00 m bajo la caída.
- Junta de tecnopor 1" en todo el contorno del contacto cuneta–colector, sellada con sellador asfáltico 1" × 2" (RC-250 + arena).
- Registro de limpieza encima del empalme.
- Verificación hidráulica: la NCF de la cuneta en el muro debe quedar por encima del NA del colector (caída libre > 0, "CAIDA LIBRE";
  si no, "AHOGADA" y la cuneta se remansa). Todas las cunetas de los tres tramos cumplen.

### 9.2 Prolongación y acortamiento de la cuneta
- Si la cuneta termina antes del muro (Refugio, Ejes 11 y 12: 1.88 y 5.39 m) se prolonga con la misma sección (0.40 × H, muros 0.10) y
  pendiente (0.5 %) hasta el muro.
- Si la cuneta dibujada entra en la franja que ocupa el colector (Varones) se acorta hasta la cara del muro.
- En ambos casos la longitud se metra en las partidas de cunetas del proyecto (la cuneta "se metra hasta el muro del colector").

### 9.3 Partidas de empalme: historia
- 03-10-2026 17:24: en el metrado del Refugio aparecían 01.04.04.06.03 EMPALME DE CUNETA AL COLECTOR (6 und) y 01.04.04.06.04 a .06.07 de
  prolongación de cunetas (concreto 1.52 m³, encofrado 23.21 m², acero 98.20 kg, tapa 4.36 m²). El usuario: "¿no se supone que ya he metrado
  yo mis cunetas y tú solo haces el colector?" → se retiraron las prolongaciones del colector; `metrado_calc.prolongaciones()` queda
  solo informativo.
- 08-10-2026 02:37 (Varones): "¿por qué hay empalme si ya he considerado su proyección hasta el colector de todas?" → se quitó la partida
  01.04.04.06.03; la DD-04 queda solo como detalle constructivo (`DD.PARTIDA_EMPALME = None` en `compat.py`). El Refugio tampoco la tiene en
  su planilla vigente (solo 01.04.04.06.01 y .06.02).
- Regla: no hay partida de empalme aparte; la ventana es parte del muro (concreto y encofrado del colector) y la cuneta llega hasta el muro.

---

## 10. Caja de llegada CL (expediente del Hogar de Refugio, en 0+000)

| Dato | Valor |
|---|---|
| Dimensiones interiores | 1.50 (largo) × 1.00 (ancho); muros 0.15; exterior 1.80 × 1.30 |
| Ubicación | del lado de Varones: x = 349162.00 a 349163.80; eje = eje del colector del Refugio |
| Piso de la poza | CF0 − 0.30 = 258.80 (colchón bajo la cota de fondo del colector) |
| Tapa | +261.15 (piso del CAR Varones); techo interior 261.05; altura interior 2.25 |
| Escalón con el Refugio | 0.55 m (261.15 − 260.60), murete de 0.15 |
| Ventana este (llegada de Varones) | 0.60 × 1.17, alféizar 259.884, sin dintel |
| Ventana norte (cuneta Eje 01 de Varones) | 0.40 × 0.66, NCF 260.394, 37.0 L/s |
| Ventana oeste (salida al colector del Refugio) | 0.80 × 1.40 (259.10 a 260.50) |
| NA en la caja (= NA en 0+000 del Refugio) | 259.606 |
| Colchón de agua | 259.606 − 258.80 = 0.806 m (≥ 0.50, cumple) |
| Caída libre de Varones sobre el NA | 259.884 − 259.606 = 0.278 m (≥ 0.10) |
| Caída total de Varones al piso | 1.084 m |
| Caída libre de la cuneta Eje 01 | 260.394 − 259.606 = 0.788 m |
| Acero | malla 3/8" @0.20 en ambas caras de muros y losas (+10 % por traslapes y ganchos) |
| Registro | 1 tapa (del Refugio) |
| Juntas | tecnopor 1" + sellador en el contacto con el colector de Varones (4.64 m, metrado en Varones) |

- Cuenta en el metrado del Refugio: concreto de fondo, muros (menos las 3 ventanas, más el escalón), losa (menos 0.49 × e de la abertura),
  excavación, solado, encofrado y malla (`metrado_calc.cajas()`).
- Rango de compatibilidad de la llegada de Varones: entre NA + 0.10 = 259.71 y el techo de la CL 261.05 − e_losa: 259.884 cumple.

---

## 11. Caja de caída CC y entrega al R-01 del CAR Mujeres (expediente del Refugio)

### 11.1 Geometría
- Poza de disipación 3.50 (largo) × 1.50 (ancho = ancho del receptor) interiores, muros 0.15; piso = CF del R-01 − 0.40 = 258.32.
- Brink (fin del colector b 0.80) en 0+069.89, CF 258.890; sin transición de ancho (CC_transicion = 0): de 0.80 se pasa a 1.50 en el brink.
- Umbral de salida de concreto 0.25 × 0.40 con corona en 258.72 (= CF del R-01).
- Ventana de salida 1.50 × 0.43 en el muro aguas abajo, sobre el umbral: alto = interior del colector del CAR Mujeres en su R-01
  (259.25 − 0.10 − 258.72 = 0.43); junta de 1" con el muro del R-01.
- Altura interior de la caja: 260.50 − 258.32 = 2.18; 2 registros con tapa sobre la poza.
- La cuneta Eje 12 del Refugio entra a la CC por ventana 0.40 × 0.80.
- Malla 3/8" @0.20 en ambas caras (muro de salida en una cara).

### 11.2 Cálculo de la poza (hoja EMPALME)

| Paso | Fórmula | Valor |
|---|---|---|
| Tirante crítico en el brink | yc = (Q²/(g b²))^(1/3), b 0.80 | 0.369 m |
| NA en el brink | CF + yc | 259.259 |
| Caída total | CF brink − piso poza | 0.570 m |
| Energía al pie | E1 = caída + 1.5 yc (sin pérdidas, conservador) | 1.123 m |
| Tirante al pie | y1 + (Q/(b y1))²/2g = E1, bisección | 0.161 m |
| Velocidad al pie | V1 = Q/(b y1) | 4.34 m/s |
| Froude al pie | F1 = V1/sqrt(g y1) | 3.45 |
| Conjugado | y2 = y1/2 (sqrt(1 + 8 F1²) − 1), en el ancho 0.80 (conservador, sin la expansión a 1.50) | 0.711 m |
| Tirante disponible | NA R-01 − piso poza = 259.062 − 258.32 | 0.742 m |
| Resalto | y2 ≤ disponible | ahogado, cumple |
| Longitud de resalto | 6 y2 | 4.27 m |
| Longitud de poza | 3.50 ≥ 0.8 × 6 y2 = 3.41 (resalto ahogado, USBR) | cumple |

- Aguas abajo del umbral el régimen es subcrítico (F = 0.67 en el receptor).

### 11.3 Corrección de la ventana de salida (15-10-2026)
- Antes el perfil la dibujaba de 0.43, la DP-07 de 0.60 (pasaba por encima del piso del CAR Mujeres) y la planilla descontaba 1.50 × 0.842
  (NA + 0.50 − fondo). Se unificó en 1.50 × 0.43 (`ventana_cc_refugio.py`); concreto del colector y cajas 58.31 → 58.41 m³.

### 11.4 Condiciones de compatibilidad con el receptor (todas cumplen)
- Cota de fondo de llegada 258.89 ≥ 258.72.
- Caudal entregado 560.6 ≤ 560.7 L/s.
- Entrega en régimen subcrítico (resalto ahogado en la poza).

---

## 12. Registros de limpieza y tapa

### 12.1 Reglas de ubicación
- Separación máxima 12 m (accesibilidad para mantenimiento, CE.040); uno en cada llegada de cuneta, en cada quiebre y donde haga falta.
- Nunca dentro de un cruce vehicular o de motos: si cae dentro, se corre fuera del vano más la holgura.
- La tapa va exactamente sobre el empalme de cada cuneta (corrección del 04-10-2026).
- Numeración: RS-xx (Refugio), RV-xx (Varones), R-xx (Mujeres). Cuadro con progresiva, tipo y nota (empalme, limpieza, quiebre) y, en
  Mujeres, coordenadas UTM, CF y cota de tapa.

### 12.2 Tapa vigente: tapa ciega de concreto armado (desde el 16-10-2026)
- Tapa 0.68 × 0.68 × 0.08, f'c 210, vaciada aparte en obra (molde lateral de madera 0.68 × 0.68 × 0.08 sobre tablero 0.80 × 0.80, reutilizable).
- Parrilla 3/8" @0.10 en ambos sentidos: 7 + 7 barras de 0.62 m, sobre dados de 2.5 cm (recubrimiento 0.025); en el modelo DXF las barras en X van a −0.055 y
  las de Y a −0.0455 respecto de la cara superior.
- 2 asas de fierro liso 1/2" en cajuelas 0.19 × 0.06 × 0.03, eje de asas a ±0.20 del centro; agarre 0.15, patas 0.02, ganchos 0.15
  (desarrollo 0.49, se toma 0.50 m).
- Cantos superiores biselados 1 × 1 cm. Peso ≈ 0.68 × 0.68 × 0.08 × 2400 = 89 kg: se coloca con 2 operarios y ganchos en las asas.
- Asiento: rebaje de concreto 0.70 × 0.70 × 0.08 en la losa superior (0.05 de asiento por lado), holgura 0.01 por lado, tapa al ras del NPT;
  luz libre del registro 0.60 × 0.60 en el resto del espesor.
- Borde engrosado 0.15 × 0.10 bajo la losa alrededor de la abertura (anillo de 0.30 a 0.45 del eje de la abertura; perímetro medio
  4 × 0.75 = 3.00 m) con refuerzo de borde 8 Ø 1/2" L = 1.40 (2 barras por lado).
- Sin marco, contramarco, anclajes, soldadura ni pintura.
- Encofrado del rebaje: cajón de madera de dos niveles, inferior 0.60 × 0.60 × 0.12 (luz y borde) y superior 0.70 × 0.70 × 0.08 (rebaje), con
  chaflán 1 × 1 cm; se retira a las 24 h; tolerancia del rebaje ± 5 mm; curado 7 días.

### 12.3 Caso b ≤ luz libre (CAR Varones, b 0.60 < 0.70) – `registro_sobre_muros_v.py` (15-10-2026)
- La abertura de 0.70 es más ancha que el colector: en los lados largos el rebaje apoya en la cabeza de los muros (y los anclajes del
  contramarco, cuando lo había, bajaban dentro del muro).
- El borde engrosado va solo en los 2 lados transversales, entre muros: 2 × 0.60 = 1.20 m por registro (antes se copió el de 3.00 m del Refugio).
- Las barras transversales del refuerzo de borde siguen midiendo 1.40 con ganchos de 0.29 dentro de los muros.
- Concreto del colector de Varones 56.02 → 55.72 m³ (COLECTOR PARAMETROS, fila 40). Se agregó la DP-06D propia de Varones (19 láminas).
- En código: `MC.BORDE_PERIM = 2 * b if b < 0.70 else 3.00`; en el DXF `MURO = b/2 <= 0.30` y `ENG_PER = 2 * (2 * b/2)`.

### 12.4 Cantidades por registro (tapa ciega)

| Concepto | Fórmula | Por registro |
|---|---|---|
| Concreto de la tapa | 0.68 × 0.68 × 0.08 | 0.0370 m³ |
| Encofrado lateral de la tapa | 4 × 0.68 × 0.08 | 0.2176 m² |
| Parrilla 3/8" | 14 × 0.62 × 0.56 | 4.86 kg |
| Asas 1/2" liso | 2 × 0.50 × 0.994 | 0.99 kg |
| Refuerzo de borde 1/2" | 8 × 1.40 × 0.994 | 11.13 kg |
| Borde engrosado (concreto, va en la losa) | 3.00 × 0.15 × 0.10 (Varones 1.20 × 0.015) | 0.045 m³ (0.018) |
| Descuento de la losa | 0.70² × 0.08 + 0.60² × (e_losa − 0.08) | 0.0464 m³ (e 0.10) |

- Totales Refugio (10): tapa 0.37 m³, parrilla 48.61 kg, asas 9.94 kg, borde 111.33 kg. Varones (11): tapa 0.407 m³, encofrado 2.394 m²,
  parrilla + asas 64.40 kg.
- En el Refugio el descuento se aplica a los 7 registros de la losa; las aberturas de las cajas se descuentan en `cajas()` (0.49 × e_losa).

### 12.5 Historia de la tapa (decisiones con fecha)
1. 03-10-2026 (traspaso): tapa 0.68 × 0.68 × 0.08 f'c 210 con malla 3/8" @0.10; luz libre 0.60; contramarco L 2" × 2" × 3/16" (0.70/0.80) con
   8 anclajes 3/8" L = 0.20; marco de tapa L 1½" × 1½" × 1/8"; borde engrosado 0.15 × 0.10; refuerzo de borde 8 Ø 1/2" L = 1.40. Metrado por
   componentes (contramarco 10 und, marco 10 und, ángulos 151.42 kg, tapa 10 und, concreto 0.37 m³, acero 173.38 kg, pintura 9.82 m²).
2. 03-10-2026 20:46: el que cotiza pidió detalle de cada componente → láminas DD-01 (rebaje/contramarco y refuerzo) y DD-02 (tapa: fabricación y
   colocación) con desagregado.
3. 07-10-2026: Delphin usa una sola tapa con marco y contramarco → partida única por und (01.04.04.05.01) con hoja DESAGREGADO TAPA REGISTRO
   y ACU TAPA REGISTRO (formato Delphin, partida de Delphin 01.04.04.06.05.01). El usuario preguntó por qué tapas de concreto y no metálicas
   y cuánto pesan para levantarlas: se mantuvo concreto (≈ 89 kg, 2 personas) por costo y porque cambiarlas implicaba rehacer todos los planos.
   Se hicieron isométricos 3D, vistas "fotográficas" del registro instalado y la DP-06B rev. 01 (tapa asentada sobre el ala del contramarco).
4. 14-10-2026: "¿la tapa es peatonal?" → el usuario: "tú sabes por dónde entran los vehículos"; los registros están fuera de los cruces, así que
   la carga es peatonal: contramarco L 1½" × 1½" × 1/8" en el Refugio (ángulos 151.42 → 101.02 kg; pintura 9.82 → 8.39 m²; lija y thinner por
   separado; ACU 383.29 → 297.45 S/ por tapa, partida 2,974.50) con precios publicados y su fuente (`cotizacion_tapa_registro.py`,
   `angulo_contramarco_refugio.py`). Varones conservó L 2" ese día.
5. 15-10-2026: Varones igual que el Refugio: contramarco L 1½" × 1½" × 1/8" (ACU 292.25 S/).
6. 16-10-2026 15:46: "las tapas del colector deben ser tapa ciega, se construye aparte en obra, sin marco metálico; detalle de los 3 CAR y
   actualiza solo el metrado de Solange y Katiuska" → DP-06B rev. 02 en los 3 CAR (`render_tapa/dxf_tapa_ciega.py`), metrado con
   `tapa_ciega.py` en Refugio (10 tapas) y Varones (11 tapas), ACU S/ 182.06 por tapa (Varones: partida S/ 2,002.65); CAR Mujeres sin cambio
   de metrado. Se actualizaron DD-01, DD-02, DP-06D, DP-08, DP-09, DA-03, isométricos, fotos 3D, especificaciones y memorias.
7. 20-10-2026: memoria hidrológica de Mujeres corregida para decir tapa ciega (según D-RL); su partida sigue "C/MARCO Y CONTRAMARCO" (pendiente).

---

## 13. Juntas del colector

### 13.1 Junta de dilatación transversal (partida 01.04.04.06.01)
- Cada 4.00 m en todo el perímetro de la sección: plancha de tecnopor (poliestireno expandido) de 1" cortada en anillo (be × (ef + h + et)
  con hueco b × h) + sellador asfáltico 1" × 2" (asfalto líquido RC-250 + arena gruesa) en las caras interiores y en la cara superior
  (EG-2013 MTC, Sección 510).
- Procedimiento: fijar la plancha al concreto vaciado; vaciar el tramo siguiente contra ella; el acero longitudinal termina a 0.05 de cada lado
  y los marcos se colocan a cada lado; retirar 2" (50 mm) de tecnopor en las caras expuestas, limpiar, calentar el RC-250, mezclar con arena y
  compactar con tacos hasta el ras.
- N.° de juntas = ENTERO(L / 4.00); perímetro = 2 × ancho exterior + 2 × (e fondo + h máx + e losa).

| Tramo | N.° | Perímetro | Total |
|---|---|---|---|
| Varones | ENTERO(105.29/4) = 26 | 2 × 0.90 + 2 × (0.15 + 1.17 + 0.10) = 4.64 | 120.64 m |
| Refugio | ENTERO(69.887/4) = 17 | 2 × 1.10 + 2 × (0.15 + 1.61 + 0.10) = 5.92 | 100.64 m |
| Mujeres | 33 (cada 4 m + 2 en camiones) | - | 162.69 m ("CON SELLADOR ASFALTO") |

- Sellador: 0.0254 × 0.0508 = 0.0013 m³ de mezcla por m de junta; mezcla con 50 gal de RC-250 y 1.05 m³ de arena por m³.
- ACU: Refugio S/ 12.01/m; Varones S/ 11.60/m (rendimiento 40 m/día).

### 13.2 Junta longitudinal con el cerco (Refugio, partida 01.04.04.06.02)
- Solo entre el muro lado predio del colector y el cimiento del cerco, en todo el tramo pegado al cerco: 0+000.00 a 0+058.81 (= P_B1) →
  58.81 m. Plancha de tecnopor de 1" de 0.90 m de alto pegada al cimiento antes de vaciar el muro + sellador asfáltico 1" × 2" en la cara superior.
- Al otro lado del colector hay terreno natural (sin vereda ni piso): no lleva junta. El colector solo tiene junta longitudinal de un lado.
- ACU JUNTA CERCO S/ 6.12/m.

### 13.3 Contacto con la caja CL (Varones, partida 01.04.04.06.02)
- Varones no tiene cerco y a ambos lados hay terreno natural: no lleva junta longitudinal. Su única junta con otra estructura es el contacto con
  el muro este de la CL: tecnopor 1" con sellador en todo el perímetro de la sección = 4.64 m (muro este de la CL 1.30 × 1.52).

### 13.4 Juntas entre expedientes y con cunetas
- Toda junta entre estructuras de distinto expediente lleva tecnopor 1" + sellador: Varones–CL (metrada en Varones), CC–muro del R-01 (Refugio).
- Contacto cuneta–colector en cada empalme: tecnopor 1" en el contorno con sellador asfáltico.
- Junta de las cunetas (partida de cunetas, no del colector): en toda la sección en U (2 muros + losa de fondo), longitud por junta = 2 H + 0.40
  (EG-2013, Sección 510); Refugio 233 juntas, 241.96 → 335.16 m; Varones 185 juntas, 252.29 m (15-10-2026).

### 13.5 Historia de las juntas (decisiones con fecha)
1. 03-10-2026 (traspaso): juntas cada 4 m (tecnopor 1" + sello asfáltico 1" × 1") y junta de tecnopor 1" entre el colector y el piso adyacente.
2. Primera planilla del Refugio: 01.04.04.06.01 "JUNTA DE DILATACION E=1" CON TECNOPOR Y SELLADOR ELASTOMERICO" (100.30 m) y 01.04.04.06.02
   "JUNTA DE TECNOPOR E=1" ENTRE COLECTOR, CERCO Y PISO ADYACENTE" (209.78 m).
3. 14-10-2026 21:14: el usuario no entendía dónde va cada una. Explicación: la 01 corta toda la sección transversal cada 4 m; la 02 es
   longitudinal entre el colector y lo que tiene al costado. Envió el procedimiento de juntas de dilatación (PDF) y la norma MTC: tecnopor en
   toda la sección y asfalto como sello superficial.
4. 14-10-2026 21:45: "en Mujeres Violentadas no hay vereda afuera, hay cerco perimétrico; no le pongas sello elastomérico, pon tecnopor y sellador
   asfáltico como la normativa" → renombradas (`renombrar_juntas_colector.py`): "JUNTA DE DILATACION E=1" CON TECNOPOR Y SELLADOR ASFALTICO EN
   COLECTOR" y "JUNTA E=1" CON TECNOPOR ENTRE COLECTOR Y CERCO PERIMETRICO".
5. 14-10-2026 22:46: "aquí también debería ir sellador asfáltico; en ambos casos sellado de una pulgada" → la 02 pasa a "JUNTA E=1" CON TECNOPOR Y
   SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO"; sellador 1" × 2" en ambas.
6. 14-10-2026 (intermedio, `junta_cerco_un_lado_refugio.py`): borde de losa con piso adyacente solo en un lado (veces 2 → 1).
7. 15-10-2026 00:59 y 01:26: "solo hay a un lado el cerco"; "la lámina DD-03 está mal: el colector solo tiene junta longitudinal a todo el largo
   pegado al cerco; al otro lado no hay vereda, solo tierra" → `junta_cerco_solo_refugio.py`: partida 210.98 → 58.81 m; DD-03 con vista D nueva;
   DP-04A/B, DP-08, DP-09, DA-03, especificaciones y memoria corregidas; se borró el esquema antiguo.
8. 15-10-2026: hojas ACU JUNTA DILATACION y ACU JUNTA CERCO en la planilla del Refugio; COLECTOR INSUMOS lee de ellas tecnopor y sellador.
9. 15-10-2026 (tarde): Varones igual (sellador asfáltico; antes conservaba poliuretano, `SELLO_JUNTA` en `compat.py`); su 02 es el contacto con la CL.
- CAR Mujeres (congelado) conserva 1.4.4.6.5.3 "JUNTA E=1" CON TECNOPOR ENTRE COLECTOR Y PISO ADYACENTE" = 78.42 m (tramo en vereda).

---

## 14. Movimiento de tierras, concreto y metrado del colector

### 14.1 Fórmulas por tramo (`metrado_calc.tramos`, segmentos de hasta 2.00 m con sección media)
- Fondo del solado = CF − ef − 0.05; profundidad = máx(0, terreno − fondo del solado) (terreno de `_calc/terreno.json`).
- Ancho de zanja = be + 2 × 0.25 (Refugio 1.60; Varones 1.40). Excavación = ancho × prof × L.
- Relleno = lateral 2 × 0.25 × prof × L + franja de 1.00 m del lado vía nivelada hasta el NPT: 1.00 × máx(0, NPT − terreno) × L
  (incluye la nivelación del retiro; rellenos menores dentro de la partida de relleno).
- Eliminación = (excavación − relleno) × 1.20 (esponjamiento; Mujeres 1.25).
- Solado = refine = (be + 0.10) × L. Trazo y limpieza = (be + 0.50) × L.
- Concreto: fondo be × ef × L; muros 2 × em × h × L; losa be × et × L − descuentos de registros + borde engrosado.
- Encofrado = L × (2 h + 2 (ef + h + et) + b) (2 caras interiores, 2 exteriores y fondo de la losa superior).
- Acabado frotachado = be × L. Curado = (2 h + b + be) × L + cajas.
- Relleno: material propio seleccionado en capas de 0.15 m al 95 % del Proctor modificado.

### 14.2 Partidas (estructura Delphin; Refugio y Varones 01.04.04; Mujeres 1.4.4.6)

| Partida | Und | Refugio | Varones |
|---|---|---|---|
| 01.04.04.01.01 Limpieza manual de terreno | m² | 125.85 | 147.41 |
| 01.04.04.01.02 Trazo, niveles y replanteo preliminar | m² | 125.85 | 147.41 |
| 01.04.04.02.01 Excavación manual de zanjas p/colector | m³ | 164.89 | 130.62 |
| 01.04.04.02.02 Refine, nivelación y compactación | m² | 93.94 | 105.29 |
| 01.04.04.02.03 Relleno compactado c/material propio seleccionado | m³ | 82.77 | 91.51 |
| 01.04.04.02.04 Eliminación de material excedente D < 1 km | m³ | 98.55 | 46.93 |
| 01.04.04.03.01 Concreto f'c = 100 para solado e = 2" | m² | 93.94 | 105.29 |
| 01.04.04.04.01 Concreto f'c = 210 para colector (una sola partida) | m³ | 58.43 | 55.75 |
| 01.04.04.04.02 Encofrado y desencofrado de colector | m² | 585.23 | 538.31 |
| 01.04.04.04.03 Acero fy = 4200 para colector | kg | 3,056.45 | 2,523.84 |
| 01.04.04.04.04 Acabado frotachado de losa superior (vereda) | m² | 86.06 | 94.76 |
| 01.04.04.04.05 Curado de concreto en colector | m² | 390.60 | 368.27 |
| 01.04.04.05.01 Tapa de registro ciega de concreto armado 0.68x0.68x0.08 | und | 10 | 11 |
| 01.04.04.06.01 Junta de dilatación e = 1" con tecnopor y sellador asfáltico en colector | m | 100.64 | 120.64 |
| 01.04.04.06.02 Junta e = 1" con tecnopor y sellador asfáltico entre colector y cerco perimétrico (Refugio) / caja CL (Varones) | m | 58.81 | 4.64 |

- Refugio incluye las cajas CL y CC (subtítulo "OBRAS DE CONCRETO ARMADO - COLECTOR Y CAJAS"); Varones no tiene cajas propias (la CL es del Refugio).
- Acero del Refugio: 3/8" 2,681.18 kg y 1/2" 375.27 kg (incluye mallas de las cajas, ≈ 684.5 kg).
- CAR Mujeres (congelado): limpieza y trazo 255.36 m²; excavación 180.66 m³; refine 239.50 m²; relleno 10.20 m³; eliminación 213.07 m³;
  solado 237.94 m²; uña 0.52 m³; concreto colector 65.56 m³; encofrado 490.72 m²; acero 4,140.49 kg; curado 919.70 m²; acabado 128.90 m²;
  aleros 0.41 m³ / 4.10 m² / 18.23 kg; emboquillado 1.56 m²; tapas 15 und; junta de dilatación 162.69 m; junta con piso 78.42 m.

### 14.3 Reglas de metrado del colector
- Partida independiente (subtítulo propio en PLANILLA GENERAL y RESUMEN); no tocar ni mezclar las partidas existentes de cunetas.
- Hojas con fórmulas visibles y sustento por lámina: COLECTOR PARAMETROS, COLECTOR MOV. TIERRAS, COLECTOR CONCRETO, COLECTOR ENCOFRADO,
  COLECTOR ACERO, COLECTOR REGISTROS Y TAPAS, COLECTOR JUNTAS Y EMPALMES, COLECTOR INSUMOS, DESAGREGADO TAPA REGISTRO y las ACU.
- Formato de la planilla del usuario: N.° de veces, largo, ancho, alto, parcial, total; celda amarilla = dato, verde = fórmula; Excel en español
  (REDONDEAR, SUMA, SI, separador ";").
- Nombres y estructura Delphin con base CAR Mujeres; cantidades siempre del metrado propio (regla del 06-10-2026).
- Concreto del colector en una sola partida (Delphin, 07-10-2026); tapa de registro por und con su desagregado.
- Editar las planillas sin romper formato con `angulo_contramarco_refugio.Libro` (XML) y `recalcular()` con LibreOffice; comparar antes y después.
- Los cuadros de las láminas DA leen los valores guardados de la planilla; nunca se recalculan aparte.
- 03-10-2026 20:41: el usuario reclamó que se borraron sus metrados de concreto y encofrado de cunetas al integrar el colector: nunca borrar ni
  rehacer hojas del usuario; agregar hojas nuevas para el colector.

### 14.4 ACU (formato Delphin)
- Mano de obra CAPECO-FTCCP 2026 (hoja COSTO HORA HOMBRE 2026): operario 28.95, oficial 22.68, peón 20.54 S/ por hh (antes 30.42 / 22.95 / 20.79).
- Tapa ciega: S/ 182.06 por und (Varones: rendimiento 4.58 und/día, MO 92.93, materiales 86.34, equipos 2.79).
- Junta de dilatación del colector: S/ 12.01/m (Refugio) y 11.60/m (Varones); junta con el cerco S/ 6.12/m; junta con la CL 11.60/m.
- Precios de materiales reales con su fuente (Sodimac, Promart, Agregados Tarapoto, EMAPA San Martín, etc.); lo no publicado queda "por cotizar en
  Tarapoto" (piedra chancada 1/2", alquiler de soldadora).

---

## 15. Coordinación entre los tres expedientes

### 15.1 Qué es de quién

| Elemento | Expediente que lo metra y dibuja |
|---|---|
| Colector b 0.60 de 0+000 a la cara este de la CL | CAR Varones |
| Cunetas Ejes 09, 08, 06, 04 (acortadas hasta el muro) y Eje 01 (hasta el muro norte de la CL) | CAR Varones |
| Junta de tecnopor y sellador Varones–CL (4.64 m) | CAR Varones |
| Caja de llegada CL con sus ventanas este y norte, su losa y su tapa (+261.15) | Hogar de Refugio |
| Colector b 0.80, cajas CL y CC, poza, umbral, ventana 1.50 × 0.43, 2 tapas sobre la poza | Hogar de Refugio |
| Junta CC–muro del R-01 | Hogar de Refugio |
| Registro R-01 en adelante, colector b 1.50, estructura de salida | CAR Mujeres |

- En los documentos de cada proyecto el vecino aguas arriba es "aporte externo" (dato de su memoria, sin validarlo) y el de aguas abajo es "receptor".
- No mezclar partidas ni láminas entre proyectos.

### 15.2 Cotas y niveles que deben empalmar (verificado el 15-10-2026)

| Punto | Expediente A | Expediente B | Estado |
|---|---|---|---|
| Fondo de Varones en la CL | 259.884 (Varones) | alféizar de la ventana este 259.884 (Refugio) | igual |
| Techo de la CL / del colector de Varones | 261.05 | 261.05 | igual, sin dintel |
| Caudal que recibe la CL | 221.7 + 37.0 = 258.7 | 258.7 | igual |
| NA en la CL | 259.606 (perfil del Refugio) | caída libre de Varones 0.278 | cumple |
| CF de entrega del Refugio | 258.890 | ≥ 258.72 (R-01) | cumple |
| Caudal al R-01 | 560.6 | ≤ 560.7 | cumple |
| NA en el R-01 | 259.062 (Refugio usa) | 259.063 (perfil de Mujeres) | igual |
| Ventana de salida de la CC | 1.50 × 0.43 | alto interior del R-01 0.43 | igual |
| UTM del R-01 | 345666.974, 9282776.560 | igual en el Refugio y en Mujeres | igual |

- Pregunta del usuario (15-10-2026 03:40): "¿constructivamente todo cuadra, el final de Varones empalma con el inicio de Mujeres Violentadas y este con
  el de Wilma?": sí; el ancho crece aguas abajo y las cotas y los niveles empalman.
- 15-10-2026 03:11: se había dejado pendiente la DP-06D de Varones "porque el modelo 3D de la tapa supone 0.80"; el usuario lo rechazó ("tú diseñaste
  todo, todo debe cuadrar"): se hizo el modelo propio de Varones (registro sobre muros, sección 12.3).
- 04-10-2026 06:17: antes de diseñar Varones el usuario preguntó si variaban los planos o metrados del Refugio: la CL se ajustó (tapa +261.15, ventanas
  este y norte) y se revisó su metrado.

### 15.3 Datos de otros expedientes y cómo quedan cubiertos (texto de las memorias)
- La llegada de Varones queda definida por su expediente; el Refugio deja la CL con su tapa en +261.15 y ventanas 0.60 × 1.17 y 0.40 × 0.66.
- El caudal de Varones es dato de su memoria; la sección del Refugio tiene más del doble de capacidad, así que una variación de ese dato no la compromete.
- Capacidad portante: presión transmitida 0.33 kg/cm² < 0.50 kg/cm²; el EMS (exigido por E.050) debe confirmarla. No había EMS al diseñar.
- UTM referencial; el trazo queda definido por su posición física (eje a 0.575 del cerco en el Refugio; a 0.475 de la línea del frente en Varones)
  y se replantea desde el cerco, el portón de camiones, la CL y las cunetas.

---

## 16. Planos del colector (lo propio del colector; el estilo general está en el skill `planos-ordenados`)

### 16.1 Juegos de láminas
- Hogar de Refugio (24 láminas del generador): DP-00 índice (A3), DP-01 planta 1/200 con UTM y leyenda, DP-02 perfil general, DP-03A/B perfiles de
  detalle 1/25, DP-04A/B y DP-05A/B secciones con acero e isométricos, DP-06A secciones típicas, DP-06B registro con tapa ciega, DP-06C empalme de
  cuneta, DP-06D isométricos de la tapa, DP-07 cajas CL y CC, DP-08 cuadro de acero y especificaciones, DP-09/DP-10 isométricos constructivos y
  general, DA-01 a DA-03 cuadros de partidas, DD-01 rebaje y refuerzo de borde, DD-02 tapa ciega: fabricación y colocación, DD-03 juntas, DD-04 empalme.
  En el juego que imprime la usuaria: DPL-06 red general, DPL-07 perfil general, DPL-14 secciones típicas, DPL-26 cajas CL y CC, DPL-27 isométricos.
- CAR Varones (19 láminas del generador; juego final DPLV): DPLV-17 planta, DPLV-18 perfil, DPLV-21/22 secciones, DPLV-23 tapa (DP-06B), DPLV-24
  empalme (DP-06C), DPLV-25 empalme con la CL (DP-07), DPLV-27 a DPLV-30 = DD-01 a DD-04. La usuaria excluyó DP-08 y DA-01 a DA-03 del juego final.
- CAR Mujeres (DP-01 a DP-10 rehechas el 08-10-2026 sin variar el metrado; luego renombradas ST-CG, STP-CG, ESDAE-01, IC-01, D-RL, D-ECC).
- Secciones de cálculo: Refugio S-01 0+000.50 … S-08 0+068.50; Varones S-01 0+003 (camiones) … S-08 0+103.50; Mujeres S-01 a S-15 cada 10 m.

### 16.2 Correcciones de dibujo del usuario sobre el colector (03-10-2026)
- 13:57: no usar amarillo (fondo blanco); los 3D salían negros; acero longitudinal y transversal en colores distintos; mejor acabado; el perfil
  longitudinal debía mostrar todos los elementos del colector.
- 14:36: escala real ("si la losa es 0.20, debe medir 0.20 con el comando L"); se dibujó una losa de 0.80; algo verde bajo las cunetas; una cota
  "3.50" que medía 7.30; el agua parecía meterse por debajo de algo.
- 14:49: líneas de llamada que se mezclan (usar flechas); en la caja de llegada el acero rojo salía del muro; acero longitudinal en círculos, no cuadrados.
- 15:15 y 15:17: huecos y vacíos en las secciones.
- 15:27: los círculos del acero deben tener el diámetro real (3/8" = 9.5 mm, 1/2" = 12.7 mm); nada al aire; el acero nunca fuera de su losa.
- 07-10-2026 y 08-10-2026: planos ordenados sin textos verticales ni encimados; layouts de AutoCAD (A1, algunos A2/A3) e índice; la DP-06B y
  los perfiles quedaron congelados en el Refugio.

---

## 17. Cronología de decisiones y correcciones (colector)

| Fecha | Proyecto | Decisión o corrección |
|---|---|---|
| 03-10-2026 03:13 | Refugio | Traspaso: mismo método que el CAR Mujeres; prediseño b 0.80 S 0.5 %; Q 560.6; caja de caída con poza hacia Wilma; criterios de acero, juntas, registro y empalme |
| 03-10-2026 03:38 | Refugio | Empezar por el Refugio con el DXF del CAR Mujeres como referencia de empalme (no esperar datos de Varones) |
| 03-10-2026 05:16 | Refugio | Colector pegado al cerco del Refugio (por fuera, dentro del lindero), no hasta la vía |
| 03-10-2026 05:26 | Refugio | NPT 260.60 en todo el frente (260.45 del ingreso OE-01 es error); losa vehicular solo en los ingresos |
| 03-10-2026 05:31-05:33 | Refugio | Portón de motos; ingreso de 4.41 m para autos y camión cisterna; UTM por el R-01 del CAR Mujeres, referencial |
| 03-10-2026 13:38-13:42 | Refugio | No reducir la altura; disipador en la entrega; ahorrar acero sin sobredimensionar (de ≈ 5,000 kg a ≈ 3,056 kg); 0.3 % verificado por autolimpieza |
| 03-10-2026 16:43 | los 3 | 35.163 mm en 10 min = 210.98 mm/h; colector con 155.66 mm/h (tc 15) |
| 03-10-2026 17:24 | Refugio | Fuera del colector las prolongaciones de cunetas (las metra el usuario en cunetas) |
| 03-10-2026 20:09-20:41 | Refugio | Integrar el colector en la planilla del usuario con hojas nuevas, su formato y sustento; no borrar sus hojas |
| 03-10-2026 20:46 | Refugio | Láminas de detalle de cada componente de registros, tapas, juntas y empalme (DD-01 a DD-04) |
| 04-10-2026 06:09 | Varones | Colector al ras de +261.15; cruce de camiones solo en el Eje 09 (5.80 m); arranca allí; caudal coherente 258.7 |
| 04-10-2026 06:12 | Varones | Quiebre al llegar a la CL; acortar las cunetas que entran a la franja del colector |
| 04-10-2026 17:03 | Varones | No hay cerco en Varones; tapas exactamente sobre cada entrega de cuneta |
| 04-10-2026 17:18 | Varones | Las cunetas son las rectas perpendiculares al frente |
| 07-10-2026 00:01-00:07 | Refugio | Concreto del colector en una partida; tapa por und con ACU detallado |
| 07-10-2026 00:15 | los 3 | Tapas de concreto (≈ 89 kg) y no metálicas |
| 08-10-2026 | Mujeres | Planos rehechos y ordenados sin cambiar el metrado; solado al ancho exterior; límite de excavación |
| 08-10-2026 02:37 | Varones | Se quita la partida de empalme |
| 14-10-2026 | Refugio | Contramarco L 1½" × 1½" × 1/8" (peatonal); juntas renombradas con sellador asfáltico |
| 15-10-2026 01:26 | Refugio | Junta longitudinal solo contra el cerco (58.81 m); DD-03 corregida; CAPECO 2026 |
| 15-10-2026 | Varones | Igual que el Refugio; registro sobre muros (borde 1.20 m; 55.72 m³); ventana CC 1.50 × 0.43 (58.41 m³); cadena verificada |
| 16-10-2026 15:46 | los 3 | Tapa ciega de concreto armado; metrado solo en Refugio y Varones |
| 20-10-2026 | los 3 | Revisión coordinada de memorias (áreas, C, 155.66 vs 210.98); Mujeres: Froude 0.51-0.74, V 1.02-1.43, BL 0.091 en camiones |
| 23-10-2026 | Varones | Códigos de lámina DPLV en el metrado; se borran referencias a DP-08 y DA-01 a DA-03 |

---

## 18. Pendientes y observaciones abiertas
- CAR Mujeres: partida de tapa con marco y contramarco frente a la tapa ciega de D-RL; tapa del R-07 dentro del cruce de camiones.
- EMS de los tres proyectos (capacidad portante ≥ presión transmitida; Varones en el cruce ≈ 0.63 kg/cm²).
- Replanteo UTM en campo (georreferenciación referencial por el R-01 y el azimut 49.54°).
- Cruce de la Carretera Oasis (badén o alcantarilla) fuera del alcance: comunicar a la entidad de la vía.
- Precios por cotizar en Tarapoto: piedra chancada 1/2", grava de 20 a 40 mm y alquiler de soldadora.
- Memorias de cálculo en PDF del Refugio y de Mujeres: diferencias de redondeo (6752.06 y 0.808) señaladas el 20-10-2026.

---

## 19. Archivos y funciones

| Archivo | Qué hace |
|---|---|
| `herramientas/diseno.py` | Datos D del Refugio, geometría (eje_local, local_a_utm, utm_a_local), cunetas, zonas, registros, intensidad, caudal, yn, yc, paso_estandar, resalto, disenar() → `entregables/_calc/diseno.json` |
| `herramientas/varones/diseno_v.py` | Igual interfaz para Varones: _offset, cruce_vertical, prog_de, caudal_en (Q variable), registros automáticos, losa_superior, techo, capacidad al 85 % |
| `herramientas/varones/compat.py` | Reasigna los módulos compartidos a Varones (dz = diseno_v), textos y parámetros propios (sin cerco, juntas, borde 2 × b, CONTRAMARCO, SELLO_JUNTA); usar_planilla() lee la planilla y comprueba concreto, acero, juntas y registros |
| `herramientas/mujeres/datos_m.py` + `base_m.json` | Parámetros y geometría del CAR Mujeres (CF, zona, esp, h, techo, acero, eje, registros UTM, juntas, terreno, perfil de flujo) |
| `herramientas/memoria_xlsx.py` | Memoria de cálculo Excel del Refugio con fórmulas: MEMORIA, DATOS, CAUDALES, CUNETAS, EMPALME, PERFIL_FLUJO (bisección en celdas), ESTRUCTURAL, CUMPLIMIENTO |
| `herramientas/varones/memoria_v.py` | Ídem Varones (EMPALME_CL, autolimpieza por tramo); `memoria_pdf_v.py` lo pasa a PDF |
| `herramientas/memoria_docx.py` | Capítulo del colector al final de la memoria hidrológica del Refugio |
| `herramientas/metrado_calc.py` | Metrado en Python (tramos, segmentos, registros, cajas, juntas, cuadro de doblado, CONTRAMARCOS, SELLOS) |
| `herramientas/tapa_ciega.py` | Cambia las planillas a tapa ciega (Refugio y Varones) |
| `herramientas/varones/registro_sobre_muros_v.py` | Borde engrosado 2 × 0.60 en Varones |
| `herramientas/ventana_cc_refugio.py` | Ventana de salida de la CC 1.50 × 0.43 |
| `herramientas/renombrar_juntas_colector.py`, `junta_cerco_un_lado_refugio.py`, `junta_cerco_solo_refugio.py` | Historia de la partida de juntas del Refugio |
| `herramientas/junta_cunetas_seccion_refugio.py` | Junta de cunetas en toda la sección en U |
| `herramientas/angulo_contramarco_refugio.py` | Clase Libro (edición XML de xlsx) y recalcular(); cambio de contramarco del 14-10 |
| `herramientas/render_tapa/dxf_tapa_ciega.py` | DP-06B rev. 02 por proyecto (`refugio`, `varones`, `mujeres`) |
| `herramientas/dxf_planta.py`, `dxf_secciones.py`, `dxf_cajas_iso.py`, `dxf_detalles.py`, `dxf_cuadros.py`, `dxf_layouts.py`, `planos_dxf.py` | Juego de planos del Refugio (Varones con `varones/planos_v.py`; Mujeres con `mujeres/planos_m.py`) |

Orden de regeneración del Refugio: `diseno.py` → `memoria_xlsx.py` → `planos_dxf.py` → `dxf_render.py` (vistas previas PNG).

---

## 20. Para implementarlo en un programa

### 20.1 Entradas
1. Proyecto: nombre, CUI, entidad, ubicación; proyecto aguas arriba (aporte externo) y aguas abajo (receptor) con su nombre y CUI.
2. Hidrología: P24 y TR (o P10 y P20), exponente de Dick-Peschke (0.25), tc del colector (10 + recorridos; 15 min), FS (1.15), Σ C·A del
   predio (o tabla de superficies con C), caudal del aporte externo (dato de su memoria) y su punto de entrada.
3. Planta: polilínea del frente (cerco o línea de referencia), lado del predio, si hay cerco o no, lindero con la vía, ubicación del receptor
   (registro R-01 o caja), sistema de coordenadas y punto común para UTM (coordenadas y azimut).
4. Niveles: NPT del frente (cara superior de la losa) por tramo; cota de fondo y NA del receptor; alto interior del receptor en su registro;
   cota de fondo y ancho del aporte externo en su llegada.
5. Cunetas que llegan: eje (x, y del extremo dibujado), NCF, NCT, longitud, ancho (0.40), si llegan tapadas o abiertas.
6. Accesos: vanos de camiones, autos y motos (coordenadas de los postes) y holguras (camiones 0.30; motos 0.115 o la que dé un tramo de 2.00 m).
7. Criterios: n = 0.015; llenado ≤ 0.85; BL ≥ 0.05; F < 1; V 0.90 a 3.0 m/s; τ ≥ 0.15 kg/m²; separación de registros ≤ 12 m; juntas cada 4.00 m.
8. Materiales y espesores candidatos: f'c 210, fy 4200, muros 0.10/0.15, losas 0.10/0.15, losa de camiones 0.20/0.25, solado 0.05; recubrimientos
   0.04/0.025; traslapes 0.40/0.50; barra 9.00 m; pesos 0.56 y 0.994 kg/m.
9. Terreno a lo largo del eje (para excavación y relleno) y capacidad portante del EMS si existe.
10. Planilla del usuario (para agregar hojas sin tocar las existentes) y precios con fuente para las ACU.

### 20.2 Pasos
1. Trazar el eje: paralela al frente a d = junta (0.025) + e_muro + b/2 hacia el lado definido (Refugio: por fuera del cerco; Varones: hacia el predio
   desde la línea del frente). Calcular progresivas acumuladas desde el extremo aguas arriba (caja de llegada o portón).
2. Resolver la llegada al receptor con quiebres a 45° (cada quiebre con registro) y, si hace falta, un tramo final recto (Refugio 6.50 = 3.00 de
   colector + 3.50 de poza; Varones tramo horizontal hasta la cara de la CL).
3. Convertir los vanos de acceso a zonas de carga en progresivas (p1 = inicio − holgura, p2 = fin + holgura) y asignar a cada zona espesores y armado.
4. Proyectar cada cuneta sobre el eje: progresiva de empalme, distancia a la cara del muro, ajuste (prolongar o acortar), NCF en el muro, Hv.
   Decidir si entra al colector, a la caja de llegada o a la caja de caída.
5. Caudales: I = P10 (tc/10)^b/(tc/60); Q propio = Σ C·A · I · FS / 3600; Q externo como dato; reparto por cuneta (por franjas de frente o nominal);
   caudal acumulado por progresiva.
6. Fijar cotas: CF0 tal que todas las cunetas caigan libremente y el aporte externo llegue con caída ≥ 0.10 sobre el NA; S tal que la CF final ≥ CF del
   receptor; techo = NPT − e_losa(zona); h = techo − CF.
7. Elegir b (empezar por 0.60 y subir en 0.10): calcular yn y yc; control aguas abajo (yc en caída libre, NA del receptor si está ahogado, o vertedero);
   perfil por paso estándar cada 1 m + puntos singulares; verificar llenado, BL y F en todas las estaciones; si falla, aumentar b o ajustar S/CF.
8. Autolimpieza: V con el caudal de diseño y τ = 1000 R S con 50, 25, 10 y 5 % (o con el caudal de cada tramo); si V < 0.90, exigir τ ≥ 0.15.
9. Capacidad al 85 % con la h mínima (margen frente al caudal).
10. Cajas: caja de llegada (poza 0.30, colchón ≥ 0.50, caída libre ≥ 0.10, ventanas con el ancho de lo que llega y alto hasta el techo); caja de caída
    (piso = CF receptor − 0.40; yc en el brink; E1 = caída + 1.5 yc; y1 por energía; F1; y2 conjugado en el ancho del colector; exigir y2 ≤ NA receptor
    − piso; L poza ≥ 0.8 × 6 y2; umbral con corona = CF del receptor; ventana de salida con el alto interior del receptor).
11. Estructura por zona: elementos A a H de la sección 8.3; si alguno no cumple, pasar a 3/8" @0.15, luego a doble marco 1/2" @0.15 o subir espesor.
    Presión sobre el suelo frente a la capacidad del EMS.
12. Registros: uno por empalme; dividir los vanos > 12 m en partes iguales; uno por quiebre; mover fuera de las zonas de carga; numerar.
13. Tapa: tapa ciega 0.68 × 0.68 × 0.08 en rebaje 0.70; si b ≤ 0.60 (b menor que el rebaje), borde engrosado solo en 2 lados (2 × b).
14. Juntas: n = ENTERO(L/4); perímetro de la sección con h máx; junta longitudinal solo donde hay cerco o estructura vecina (nunca contra terreno
    natural); junta en cada contacto entre expedientes.
15. Metrado por segmentos de ≤ 2 m (fórmulas de 14.1), cajas, registros, juntas; acero con marcos = REDONDEAR.MAS(L/s), longitudinales por perímetro;
    cuadro de doblado.
16. Escribir hojas nuevas en la planilla del usuario (sin tocar las existentes) con estructura Delphin y sustento por lámina; recalcular y comparar.
17. ACU con MO CAPECO 2026 y precios con fuente.
18. Generar planos a escala real (planta, perfil general y de detalle, secciones, isométricos, registro, empalme, cajas, juntas, cuadros) y vista previa PNG.
19. Generar memoria de cálculo Excel con fórmulas y el capítulo de la memoria hidrológica; especificaciones técnicas por partida.
20. Verificar coherencia (metrado ↔ planos ↔ especificaciones ↔ memoria ↔ expedientes vecinos) y emitir el cuadro de cumplimiento.

### 20.3 Salidas
- `diseno.json`: datos, geometría, zonas, cunetas (prog, NCF en el muro, caída libre, Hv), registros, perfil (p, z, b, y, V, F, NA, techo, h, llenado,
  BL, zona, ok), poza, caja de llegada, capacidad.
- Memoria de cálculo Excel (DATOS, CAUDALES, CUNETAS, EMPALME, PERFIL_FLUJO, ESTRUCTURAL, CUMPLIMIENTO, MEMORIA) y, si se pide, PDF.
- Planilla con las hojas del colector, RESUMEN y PLANILLA GENERAL actualizados; ACU y desagregados.
- DXF con presentaciones de AutoCAD e índice; PNG de cada lámina.
- Capítulo del colector en Word, especificaciones técnicas y memoria descriptiva.

### 20.4 Validaciones obligatorias (el programa debe avisar, no inventar)
- Llenado ≤ 0.85, BL ≥ 0.05 y F < 1 en todas las estaciones (salvo el borde de caída).
- 0.90 ≤ V ≤ 3.0 m/s con el caudal de diseño; τ ≥ 0.15 kg/m² en caudales parciales.
- Caída libre > 0 en cada cuneta (NCF en el muro > NA del colector) y ≥ 0.10 m en la llegada del aporte externo.
- CF de entrega ≥ CF del receptor; Q entregado ≤ Q previsto por el receptor; resalto ahogado y longitud de poza suficiente.
- Ventana de salida de la caja de caída ≤ alto interior del receptor (no pasar por encima de su piso).
- Techo de la caja de llegada = techo del colector que llega (sin dintel) o dintel explícito.
- Separación entre registros ≤ 12 m; ningún registro (ni su rebaje) dentro de una zona de carga.
- Si b ≤ luz libre de la tapa, el borde engrosado no puede tener 4 lados.
- φMn ≥ Mu, φVc ≥ Vu y As ≥ As mín en cada elemento; una capa solo si e ≤ 0.20.
- Presión sobre el suelo ≤ capacidad admisible del EMS (si no hay EMS, marcar "VERIFICAR EMS").
- Junta longitudinal solo donde hay cerco o estructura; ninguna contra terreno natural.
- Metrado: totales de la planilla = cálculo del programa (tolerancia 0.05) y ningún valor previo del usuario cambia.
- Coherencia entre expedientes: mismos caudales, cotas, NA, dimensiones de ventanas y coordenadas del punto común.
- Si un caso no cubre ninguna regla (empalme raro, interferencia, acceso nuevo), presentar opciones al usuario y recomendar una; una vez decidida,
  agregarla como regla.
