# 07 — Componentes complementarios del drenaje pluvial

Base de conocimiento permanente (desde el 03-10-2026). Cubre todo lo que no es el colector frontal en sí: red de techo
(canaletas, soportes, tapas, boquillas, montantes PVC Ø 4", colgadores, abrazaderas, falsa columna y dado), red de piso
(sumidero y tubería), cunetas de concreto (sección, rejilla móvil, tapas de inspección), juntas de dilatación de cunetas,
lloraderos, tapa ciega del registro del colector y drenaje de bancas con techo (OC-01 del Hogar de Refugio y banca tipo 01
del CAR Mujeres). Para cada componente se da: dimensiones, materiales, regla de ubicación, fórmula de metrado, cantidades por
proyecto, ACU, láminas, generador y la historia de decisiones del usuario con fecha.

Convenciones del documento:
- Proyectos por nombre y CUI: CAR Varones (CUI 2705619), Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514),
  CAR Mujeres (CUI 2717013, metrado congelado), I.E. N.° 0590 Barranquita (C.I. 468901, CUI por confirmar).
- Medidas en metros salvo indicación; escala real en planos (1 unidad = 1 m). "Cota de fondo" (nunca otro término).
- Valores de metrado tomados de las planillas vigentes (`insumos/metrados_vigentes/`, entregables) con valores guardados.
- Mano de obra 2026 CAPECO-FTCCP: operario 28.95, oficial 22.68, peón 20.54 S/ por hh (hoja COSTO HORA HOMBRE 2026).

---

## 1. Línea de tiempo de decisiones del usuario (componentes complementarios)

| Fecha | Componente | Decisión / corrección del usuario | Consecuencia |
|---|---|---|---|
| 03-10-2026 | Tapa de registro | Registro tipo heredado del CAR Mujeres: tapa 0.68 x 0.68 x 0.08 f'c 210 malla 3/8" @0.10, luz 0.60, contramarco L 2"x2"x3/16" con 8 anclajes 3/8" L 0.20, marco L 1 1/2"x1 1/2"x1/8", borde engrosado 0.15 x 0.10, refuerzo de borde 8 Ø 1/2" L 1.40 | Base de la DP-06B rev. 00/01 |
| 03-10-2026 | Empalme y prolongación de cunetas | "¿por qué esa partida? ya metré mis cunetas, tú solo haces el colector" | Se eliminan las partidas de prolongación de cunetas del colector: la cuneta se metra hasta el muro del colector en las partidas de cunetas |
| 03-10-2026 | Registros / tapas | El cotizador pedirá detalle de cada componente (contramarco, marco, ángulos, tapa, concreto, acero, pintura, juntas, empalme) | Láminas de detalle aparte (DD-01 a DD-04) |
| 04-10-2026 | Cunetas (acero) | Cunetas con H > 0.40 llevan acero; las que no, concreto simple; excepción: tramo tapado lleva acero aunque H < 0.40 (ej. Eje 01 tapado 13.20-19.20 con H 0.37). H se mide desde el NCT (abierta o tapada). Acero transversal de las tapas siempre 0.56 m @0.25 | Regla fija del metrado de cunetas |
| 04-10-2026 | Cunetas que llegan al colector (CAR Varones) | Las cunetas son las perpendiculares; las tapas del colector deben ir exactamente sobre la caja de llegada de cada cuneta | Registro en cada empalme |
| 07-10-2026 | Tapa | Pregunta: por qué de concreto y no metálica, cuánto pesa | Se explica: ~89 kg (0.68² x 0.08 x 2400), se levanta entre 2 con ganchos en las asas; se mantiene concreto (cambiar todo costaría los créditos) |
| 07-10-2026 | Tapa | Dibujo 3D realista en 4 vistas, letra grande, colores para fondo blanco, varios isométricos, "foto realista" instalada, luego en DXF | DP-06D, isométricos y fotos (`render_tapa/`) |
| 07-10-2026 | Tapa (Delphin) | Unir los 7 componentes en una partida por und con su hoja de desagregado y ACU | Partida única 01.04.04.05.01 TAPA DE REGISTRO + hojas DESAGREGADO TAPA REGISTRO y ACU TAPA REGISTRO |
| 07-10-2026 | Canaletas | ACU de 01.04.03.05.01.03 a .06 (canaleta 513.98 m, soporte 884 und, tapa lateral 40 und, boquilla 52 und) del Hogar de Refugio | Hoja ACU CANALETAS |
| 08-10-2026 | Lloraderos | Agregar lloraderos solo al Hogar de Refugio y al CAR Varones (CAR Mujeres ya presupuestado), de PVC, solo donde la cuneta está expuesta a área verde | Partida nueva 01.04.03.04.03.04 y hoja METRADO LLORADEROS |
| 08-10-2026 | Firma | "El nombre CIP no pongas nada" | Campos de proyectista y CIP en blanco en todo |
| 09-10-2026 | Soporte de canaleta | ¿Sustento del precio de la platina F°G° 1" x 1/8"? Pedir precio real y texto justificado | Precio referencial en la ACU (ver §2.6) |
| 09-10-2026 | Canaleta | Dibujar en DXF el detalle de canaleta y platina; "debe ser su isométrico tal cual, detalles hasta de los pernos, todo según tu ACU" | Láminas DR-01 a DR-06 |
| 10-10-2026 | Canaleta | "La sección de la canaleta es 0.20 ancho y 0.25 altura, recuerda"; dibujar tubo, dado, abrazaderas y colgadores en 3D | `planos_techo.py` usa 0.20 x 0.25 (ver discrepancia §2.1) |
| 10-10-2026 | Leyendas | Leyenda/especificaciones para las láminas de secciones transversales de cunetas, de falsa columna y de lloraderos, en DXF | Bloques LEYENDA_ESPEC_CUNETAS, ESPEC_FALSA_COLUMNA, ESPEC_LLORADEROS |
| 10-10-2026 | Subdrén | "Borró el subdrén, entonces solo lloraderos" | El sub-dren se retira de la leyenda de lloraderos |
| 10-10-2026 | Sumidero de piso | Detalle isométrico del sumidero 0.25 x 0.25; abajo tubo de 4" con un solo codo de 90° que evacúa a la cuneta; "olvídate del sifón" | Láminas DS-01/DS-02 sin trampa ni sifón |
| 10-10-2026 | Lloraderos | Detalle isométrico de instalación: geotextil, grava, tubería perforada de 3" | Láminas DL-01 y DL-02 |
| 14-10-2026 | Lija y thinner | Desagregar el global "lija y thinner" en lija (und) y thinner (gal) | Excel aparte y luego en la ACU |
| 14-10-2026 | Juntas | "¿Qué es y dónde va cada una de las dos juntas?"; el tecnopor va en toda la sección (U) y el asfalto solo como sello superficial (MTC/RNE); envía PDF de procedimiento de juntas | Junta de cunetas en toda la sección en U |
| 14-10-2026 | Juntas del colector | Renombrar: una "en colector" y otra "entre colector y cerco perimétrico" (no hay vereda afuera en el Hogar de Refugio); no sellador elastomérico sino tecnopor + sellador asfáltico; en ambas sellado de 1" | Nombres Delphin nuevos (ver §7.6) |
| 14-10-2026 | Contramarco | Pregunta sobre carga peatonal o vehicular: "tú tienes el plano, sabes por dónde entran vehículos"; precios "reales comprobados", acceso a internet | Contramarco L 1 1/2"x1 1/2"x1/8" en el Hogar de Refugio; cotización con fuentes |
| 15-10-2026 | Lloraderos | Pide el metrado y una hoja de cómo se sacó, con geotextil; luego que se señalen en un plano "profesionalmente" | Hoja DESAGREGADO LLORADEROS y plano DL-00 |
| 15-10-2026 | Junta colector-cerco | Solo hay cerco a un lado; al otro lado solo tierra; la DD-03 estaba mal | Junta longitudinal solo contra el cerco (58.81 m) |
| 15-10-2026 | Junta de cunetas | "Hazlo según reglamento, sin errores"; DJ-01 perfecta; pedir 3D del proceso constructivo y detalle de la rejilla | DJ-01, DJ-02 (4 isométricos), DJ-03 (rejilla) |
| 15-10-2026 | Mano de obra | "Actualiza todo a 2026" (envía PDF CAPECO-FTCCP 2026) | Hoja COSTO HORA HOMBRE 2026 |
| 15-10-2026 | CAR Varones | Igual que el Hogar de Refugio pero manteniendo sus metrados; mismos nombres de partidas | Juntas, ACU, DJ-01 a DJ-03 en Varones |
| 16-10-2026 | Tapa | "Las tapas del colector deben ser tapa ciega, se construye aparte en obra, ya no tiene marco metálico; detalle de los 3 CAR; actualiza solo el metrado del Hogar de Refugio y del CAR Varones" | Tapa ciega (§9) |
| 19-10-2026 | Banca CAR Mujeres | Isométrico de la banca tipo 01 solo para CAR Mujeres, detalles pluviales, canaleta 0.20 alto x 0.18 ancho; faltan cortes frontales; el colgador debe salir en el isométrico; "fiel al dibujo, sin errores" | DB-01 a DB-03 |
| 19-10-2026 | Banca CAR Mujeres | "¿Por qué tanto soporte en 2 m? Solo 2 soportes de 1"x1/8""; 16 techos iguales; "ese sumidero no, solo la boquilla"; solo 2 m lineales por techo, a una agua, sin uniones; espesor para el techito: 0.50 mm (aceptado) | 2 soportes, 1 boquilla, 2 tapas, 2.00 m por techo |
| 19-10-2026 | Banca CAR Mujeres | Meter solo esos ítems al Excel general, con hoja nueva; agregar el codo de 45° que está en el cuadro de montantes | Subtítulo 1.4.4.5.4 y CODO 45° en el RESUMEN |
| 21-10-2026 | Cunetas Barranquita | Cuneta 0.60 total (muros 0.10, libre 0.40); acero solo desde h ≥ 0.40 (de la rejilla al fondo) o tapada; sección de 0.15 "imposible"; rejilla y tapada en planta a escala real; tapas de inspección en tapados | Reglas de cunetas sobre terreno (§6) |
| 22-10-2026 | Lloraderos DXF | "Se ve bien en imagen pero en DXF se ve horrible" (Hogar de Refugio) | Detalle sin patrones de achurado (§8.8) |
| 22-10-2026 | OC-01 Hogar de Refugio | Isométrico solo donde sale la montante y accesorios; borrar la cúpula; canaleta galvanizada 0.5 mm, 0.21 alto x 0.18 ancho; solo dos sujetadores; metrado solo de canaleta, tapas, sujetadores y boquilla; 9 bancas = 3 juegos de 3 techos (3.79, 4.21, 3.79) | §10.2 |
| 23-10-2026 | Lloraderos CAR Varones | Falta el plano de áreas verdes en contacto con lloraderos en DXF; ¿dónde está el metrado de piedra, tubo perforado, geotextil? | DL-00 Varones; se aclara que está en DESAGREGADO LLORADEROS |

---

## 2. Canaletas de techo (red de recolección de techo)

### 2.1 Sección y material
- Techos a dos aguas: **una canaleta por cada lado** (hoja METRADO CANALETAS: "Lado 01" y "Lado 02" por edificación).
- Plancha de acero galvanizado e = 0.9 mm (ASTM A653), pestañas superiores de 0.05 m por lado.
- Sección del metrado y de la partida Delphin: **0.25 m (fondo) x 0.20 m (alto)**; desarrollo de plancha
  = fondo + 2 alturas + 2 pestañas = 0.25 + 2 x 0.20 + 2 x 0.05 = **0.75 m²/m**.
- Discrepancia registrada: el 10-10-2026 el usuario dijo "la sección de la canaleta es 0.20 ancho y 0.25 altura"; las láminas
  DR-01 a DR-06 (`herramientas/techo/planos_techo.py`, `CB, CH = 0.20, 0.25`) dibujan 0.20 x 0.25 y su nota de fijaciones dice
  "remaches de unión con la sección 0.20 x 0.25: 28 por unión cada 2.44 m (el ACU tiene 26, de la sección 0.25 x 0.20)".
  El nombre de la partida y la hoja METRADO CANALETAS siguen con 0.25 x 0.20 (no se cambian sin pedido expreso).
- Fabricación en tramos de 2.44 m (largo de la plancha comercial 1.22 x 2.44). Unión cada 2.44 m: traslape 0.05 m, el tramo de
  aguas arriba va por dentro del de aguas abajo, 2 filas de remaches pop 1/8" @0.05 en todo el perímetro y cordón de sellador
  de poliuretano.
- Pendiente de diseño de la canaleta: **S = 1.00 %** hacia las boquillas (memoria hidrológica de los CAR, n = 0.013).
  Bancas: S = 0.5 %.
- Apoyo: alero o viga de borde de concreto (dimensiones referenciales, según arquitectura y estructuras). Cobertura de aluzinc
  TR4 e = 0.40 mm que vuela 0.13 m sobre la canaleta (referencial). Borde exterior de la canaleta más bajo que el borde de la cubierta.
- Cortes y perforaciones del galvanizado: dos manos de pintura rica en zinc.

### 2.2 Soporte de platina F°G° 1" x 1/8"
- Platina 25.4 x 3.18 mm; peso 0.633 kg/m (25.4 x 3.18 x 7.85).
- Forma: abraza fondo y dos lados de la canaleta + 2 orejas de fijación de 0.10 m. Desarrollo:
  - ACU y especificación: 0.25 + 2 x 0.20 + 2 x 0.10 = **0.85 m** (sección 0.25 x 0.20).
  - Lámina DR-01 (sección 0.20 x 0.25): 2 x 0.10 + 0.20 + 2 x 0.25 = 0.90 m.
- Separación **@0.60 m**. Metrado por canaleta: `soportes = REDONDEAR.MAS(L / 0.60; 0) + 1` (si L > 0).
- Fijación: 2 pernos de expansión 1/4" x 2 1/2" con tarugo (una oreja a cada lado) y 2 tornillos autorroscantes 1/4" x 3/4"
  (oreja exterior y fondo). Dobleces a 90°; perforaciones 5/16" (pernos) y 1/4" (tornillos).

### 2.3 Tapa lateral
- Plancha galvanizada e = 0.9 mm con la sección de la canaleta y pestaña perimetral de 0.03 m que entra en la canaleta
  (especificación: pestañas de 0.02 m).
- 6 remaches pop 1/8" por tapa (2 por lado) + cordón de sellador. **2 tapas por canaleta** (una en cada extremo).

### 2.4 Boquilla a montante Ø 4"
- Abertura Ø 0.10 en el punto bajo del fondo de la canaleta.
- Brida 0.20 x 0.20 remachada (8 remaches pop 1/8") y sellada; cuello de plancha galvanizada Ø 0.10 x 0.15 que entra en la
  campana del montante PVC 4" (Ø ext. 0.114).
- Cantidad: la boquilla de cada lado = número de montantes de ese lado (`'METRADO MONTANTES'!C`), es decir, 1 boquilla por montante.

### 2.5 Fijaciones por unidad (lámina DR-05 y ACU)
| Fijación | Por | Cantidad por unidad |
|---|---|---|
| Perno de expansión 1/4" x 2 1/2" con tarugo | soporte | 2 |
| Tornillo autorroscante 1/4" x 3/4" | soporte | 2 |
| Remache pop 1/8" en uniones | m de canaleta | 2 x (fondo + 2 x alto) / 0.05 / 2.44 (26 por unión con 0.25 x 0.20; 28 con 0.20 x 0.25) |
| Remache pop 1/8" | tapa lateral | 6 |
| Remache pop 1/8" | boquilla | 8 |
| Sellador de poliuretano, cartucho 300 ml (= 8 m de cordón de 6 mm) | uniones, tapas, boquillas | junta 0.65 m cada 2.44 m; tapa 0.65 m; boquilla 1.12 m |
| Tirafón 2" x 1/4" + tarugo 2" x 1/2" | abrazadera | 2 |
| Varilla roscada 3/8" + anclaje 3/8" + 2 tuercas + arandela | colgador | 1 juego |

Medidas reales dibujadas: cabeza hexagonal de perno 7/16" (11 mm), tornillo 5/16" (8 mm), remache 1/8" (cuerpo 3.2 x 10 mm,
cabeza 6.4 mm).

### 2.6 ACU CANALETAS (formato Delphin; mismos valores en Hogar de Refugio y CAR Varones)
Datos: fondo 0.25, alto 0.20, pestaña 0.05, desarrollo 0.75 m²/m, plancha 0.9 mm, peso plancha = e x 7.85 + 0.3 (zinc) = 7.365 kg/m²,
plancha comercial 2.44 m, traslape 0.05, soporte 0.85 m, platina 0.633 kg/m en barras de 6 m. Precios sin IGV, referenciales
("al pasar a Delphin rigen los de la base de precios del presupuesto").

| Partida | Rend. | Cuadrilla | Materiales (cantidad por unidad, precio S/ sin IGV) | C.U. S/ |
|---|---|---|---|---|
| Canaleta (m) | 25 m/día | 1 op (hojalatero) + 1 peón | plancha 0.75 x (1 + 0.05/2.44) x 1.05 = 0.8036 m² a 26.95; remache 10.66 und a 0.10; sellador 0.0333 cartucho a 21.19; herramientas 5 % MO | 40.06 |
| Soporte (und) | 40 und/día | 1 op + 0.5 peón | platina 0.85 x 1.05 = 0.8925 m a 6.36; perno expansión 2 a 1.02; tornillo 2 a 0.25; herram. 5 % MO | 16.45 |
| Tapa lateral (und) | 30 und/día | 1 op + 0.5 peón | plancha (0.25 x 0.20 + 2 x 0.45 x 0.03) x 1.1 = 0.0847 m²; 6 remaches; sellador 0.65/8 = 0.0813; herram. 5 % | 15.59 |
| Boquilla (und) | 16 und/día | 1 op + 0.5 peón | plancha (π x 0.1016 x 0.15 + 0.2 x 0.2) x 1.15 = 0.1011 m²; 8 remaches; sellador (4 x 0.2 + π x 0.1016)/8 = 0.1399 | 27.08 |

Precio de la platina F°G° 1" x 1/8" en la ACU: S/ 6.36 por m sin IGV, rotulado "Mercado Tarapoto 2026, sin IGV (referencial)"
(el usuario pidió sustento el 09-10-2026; mantener la fuente a la vista y actualizarla con cotización comprobada).

### 2.7 Hidráulica de canaletas y montantes (memorias de los CAR)
- Método racional Q = C·I·A·FS con C = 0.88 (techos), I = 210.98 mm/h (tc = 10 min), FS = 1.15.
- Canaleta: Manning rectangular, n = 0.013, S = 1 % (bancas 0.5 %); borde libre de 0.05 m al verificar capacidad.
- Montante: Wyly-Eaton con relación de llenado rs = 0.25: Q (gpm) = 27.8 · rs^(5/3) · D^(8/3), o
  Q (L/s) = 1.754 · rs^(5/3) · D^(8/3) con D en pulgadas; D requerido = (Q / (1.754 · rs^(5/3)))^(3/8).
  Capacidad de 4" = 7.0 L/s. CAR Mujeres: diámetros requeridos 2.468" a 3.821" → se adopta PVC Ø 4" en todos.
- Barranquita (hidrología): canaleta 0.25 x 0.20, S 1 %, n 0.013 y montante 4" verificados, pero canaletas y montantes quedan fuera
  del alcance del metrado (especialidad de techos).

### 2.8 Metrado (hoja METRADO CANALETAS de la planilla del usuario)
Estructura: por edificación, Lado 01 y Lado 02; columnas N° de canaletas (C), longitud (D), total m (E = C·D), soportes
(F = SI(D>0; REDONDEAR.MAS(D/$F$50;0)+1; 0), G = C·F), tapas (H = $F$51 = 2, I = C·H), boquillas (J = 'METRADO MONTANTES'!C de la
misma fila, K = C·J). Parámetros (filas 45-52): fondo 0.25, alto 0.20, pestaña 0.05, desarrollo = F45 + 2·F46 + 2·F47 = 0.75,
espesor 0.9 mm (editable; "cambiar también la descripción de la partida"), separación 0.60, tapas 2, área de plancha referencial
= E41 x F48.

| Proyecto | Canaleta (m) | Soportes (und) | Tapas laterales | Boquillas |
|---|---|---|---|---|
| Hogar de Refugio (CUI 2675514) | 513.98 | 884 | 40 | 52 |
| CAR Varones (CUI 2705619) | 523.16 | 906 | 44 | 52 |
| CAR Mujeres (CUI 2717013), `insumos/metrados_vigentes/` | 515.48 | 894 | 44 | 52 |
| CAR Mujeres, versión 09-10-2026 (`insumos/wilma/vigente_09-10-2026/`) | 446.22 | 776 | 40 | 44 |

Hogar de Refugio por edificación (largo por lado): Ed. 01 25.33, Ed. 02 14.33, Ed. 03 17.33, Ed. 04 38.13, Ed. 05 32.31,
Ed. 06 20.73, Ed. 07 38.13, Ed. 08 20.73, Ed. 09 14.77, losa deportiva 35.20 (20 canaletas).

Partidas Delphin (Hogar de Refugio y CAR Varones): 01.04.03.05.01.03 CANALETA DE PLANCHA DE ACERO GALVANIZADO e=0.9mm, SECCIÓN
0.25m x 0.20m (m); .04 SOPORTE DE PLATINA F°G° 1" x 1/8" P/CANALETA (und); .05 TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA
(und); .06 BOQUILLA DE PLANCHA GALVANIZADA P/CONEXIÓN DE CANALETA A MONTANTE Ø4" (und). CAR Mujeres: 1.4.4.5.1.3 a .6.

---

## 3. Montantes PVC Ø 4" y accesorios

### 3.0 Reglas para el programa DRENIE (24-10-2026)
- El montante va pegado a la esquina de la edificación, en su falsa columna adosada al muro (dibujo del usuario: falsa columna,
  tubo Ø 4" y el concreto que lo envuelve, junto a la columna de la esquina): por defecto 2 por lado (4 por edificación a dos aguas).
- Siempre 4"; no usar 6". Si el área lo pide, se ponen más montantes de 4" por lado (3, o 4 por lado sobre todo en losas deportivas).
- El proyectista puede mover, quitar o agregar montantes en el visor (comando MT); el programa diseña con los que deje.
- "1616 soportes es demasiado; después revisaré" (pendiente: separación de soportes @0.60 m de la planilla).

### 3.1 Recorrido típico (corte I de DR-02, isométrico DR-04)
Boquilla en el fondo de la canaleta → niple → codo PVC 4" x 90° → desvío horizontal bajo el alero (con colgadores) → codo 90° →
bajada vertical adosada al muro con abrazaderas → tramo inferior dentro de la falsa columna → codo de salida 90° dentro del dado →
salida PVC 4" hasta la cuneta (longitud según metrado). **3 codos de 90° por montante** (hoja METRADO MONTANTES).
- Tubería PVC-U para desagüe 4" (NTP 399.003), uniones con cemento solvente (ASTM D2564); campanas: el tubo entra 0.05.
- Plomo: desviación máxima 5 mm por metro; prueba de escurrimiento con agua antes de cerrar la falsa columna.
- Longitud de cada montante: la de la hoja METRADO MONTANTES (nota de DR-02: 6.16 a 11.00 m según edificación; en el Hogar de
  Refugio la hoja tiene de 5.90 a 11.00 m en edificaciones y losa, y de 5.43 a 7.96 m en las bancas).

### 3.2 Colgador F°G° (desvío bajo el alero)
- Banda F°G° alrededor del tubo 4" + varilla roscada F°G° 3/8" con tuerca y contratuerca + anclaje de expansión 3/8" en el fondo
  del alero. Diámetro interior 1/4" mayor que el tubo.
- **Uno junto a cada codo del desvío**, a no más de 0.30 m del codo (2 por montante en edificaciones; 0 en la losa deportiva;
  1 en bancas y obras exteriores).

### 3.3 Abrazadera F°G°
- Platina F°G° e = 1/8" (anillo Ø int. 1/4" mayor que el tubo) con 2 orejas; cada oreja con tirafón 2" x 1/4" (55 x 6 mm) en tarugo
  plástico con estrías 2" x 1/2"; broca de 1/2".
- Especificación y plano: **@1.50 m como máximo**, la primera sobre la falsa columna y la última bajo el desvío superior.
- Metrado del usuario (hoja METRADO MONTANTES): `abrazaderas por montante = MAX(1; REDONDEAR.MENOS(L/4; 0))` (una cada 4 m);
  en la losa deportiva 3 por montante. Diferencia con el @1.50 de la especificación: no se tocó (metrado del usuario).

### 3.4 Hoja METRADO MONTANTES (estructura)
Columnas: N° montantes (C), veces (D = C), longitud (E), total m (F = E·D), codo 90° (G = 3, H = C, I = G·H), abrazadera (J, K, L),
colgador (M, N, O), codo 45° (P, Q, R). Totales en la fila 53.

| Proyecto | Montante PVC 4" (m) | Codo 90° accesorios | Colgador | Abrazadera | Codo 45° |
|---|---|---|---|---|---|
| Hogar de Refugio | 443.22 (63 montantes, incluye 9 bancas B-01 a B-09 y 2 obras exteriores) | 189 | 99 | 79 | 0 |
| CAR Varones | 408.02 | 168 | 100 | 80 | – |
| CAR Mujeres (`metrados_vigentes`) | 386.48 | 150 | 90 | 74 | – |
| CAR Mujeres 09-10-2026 con bancas | 522.96 | 207 | 106 | 90 | 2 (1.4.4.5.3.2, agregado al RESUMEN el 19-10) |

CAR Mujeres: las bancas BC-01 a BC-16 ya están en METRADO MONTANTES (bajadas de 5.17 a 13.36 m, 3 o 4 codos de 90°, 1 colgador,
1 abrazadera; BC-12 y BC-13 con 1 codo de 45°). Por eso los codos, colgador y abrazadera de las bancas no se repiten en la partida de
bancas.

### 3.5 Especificación (resumen)
Montante: cortar a escuadra, biselar espiga, limpiar, cemento solvente, cuarto de giro y 30 s; aplomar con abrazaderas; codo de
descarga embebido en dado y falsa columna; trabajo en altura con andamio certificado y arnés con línea de vida (G.050).
Medición por metro desde la boquilla hasta la descarga. Colgador y abrazadera por und.

---

## 4. Falsa columna de concreto y dado del montante

### 4.1 Geometría y materiales
| Elemento | Medidas | Material | Función |
|---|---|---|---|
| Falsa columna | 0.20 x 0.15 x 1.30 m (adosada al muro: 3 caras encofradas, la cuarta es el muro) | Concreto f'c = 175 kg/cm², piedra chancada 1/2", slump 3" a 4" | Aloja y protege contra golpes el tramo inferior del montante hasta 1.30 m sobre el NPT; no recibe cargas |
| Acero longitudinal | 4 Ø 3/8" en las esquinas, L = 1.20 por barra (metrado), anclados en el dado | fy 4200, grado 60 (ASTM A615 / NTP 341.031) | |
| Estribos | Ø 3/8" @0.15, 9 por falsa columna, L = 0.58 por estribo, ganchos a 135° de 0.075 m; el primero a 0.05 del dado | | |
| Dado | 0.40 x 0.40 x 0.35 m | Concreto simple f'c = 140 kg/cm² | Envuelve el codo de salida 90° y el arranque de las barras |

- Recubrimiento: el bloque ESPEC_FALSA_COLUMNA dice 2 cm libres a la cara exterior del estribo (separadores, no piedras ni madera);
  la especificación técnica de la partida de acero (`espec.py`) dice 0.04 m mínimo "según notas del detalle de falsa columna".
  Diferencia a resolver con el detalle del plano antes de imprimir de nuevo.
- Vaciado en una etapa después de instalar y probar el montante; compactar con varilla y golpes suaves (no vibrar contra el tubo);
  tubo aplomado, centrado, sin tocar el acero, tapado arriba durante el vaciado. Desencofrado ≥ 24 h; curado ≥ 7 días.
  Tolerancia de plomo ±5 mm. Normas: E.060, IS.010, NTP 341.031, 399.003, 334.009, 339.088.

### 4.2 Metrado (PLANILLA GENERAL, Hogar de Refugio, filas 140-148)
- Partida madre 01.04.03.05.01.02 FALSA COLUMNA P/MONTANTE DE 0.20m x 0.15m x 1.30m (und) = número de montantes de edificación
  (52); sin pago independiente (se paga por sus subpartidas).
- .02.01 Concreto f'c 175: 1.30 x 0.15 x 0.20 = 0.039 m³/und → 52 x 0.039 = **2.028 m³**.
- .02.02 Encofrado: 2 x 1.30 x 0.15 + 1 x 1.30 x 0.20 = 0.65 m²/und → **33.80 m²**.
- .02.03 Acero: (1.20 x 4 + 0.58 x 9) x 0.56 = 5.6112 kg/und → **291.78 kg**.
- Dados: excavación 01.04.03.02.02 y concreto 01.04.03.03.02 = 52 x 0.40 x 0.40 x 0.35 = **2.912 m³**.

| Proyecto | Falsas columnas | Concreto (m³) | Encofrado (m²) | Acero (kg) | Dados (m³) |
|---|---|---|---|---|---|
| Hogar de Refugio | 52 | 2.028 | 33.80 | 291.78 | 2.912 |
| CAR Varones | 56 | 2.184 | 36.40 | 314.23 | 3.136 |
| CAR Mujeres (`metrados_vigentes`) | 54 | 2.106 | 35.10 | 303.00 | 3.024 |
| CAR Mujeres 09-10-2026 | 70 | 2.73 | 45.50 | 392.78 | – |

Falsa columna de las bancas (CL-01 de drenaje pluvial): 0.20 x 0.15 dibujada de −0.15 a +1.05 (1.20 m); el plano de la banca del
CAR Mujeres la rotula H = 1.50 (diferencia informada al usuario). No se metra en la partida de bancas.

Generador: `herramientas/espec_falsa_columna.py` (bloque ESPEC_FALSA_COLUMNA a escala real, lee la PLANILLA GENERAL) →
`entregables*/ESPECIFICACIONES_FALSA_COLUMNA_MONTANTE_*.dxf`. Hogar de Refugio: lámina DPL-39 (A3).

---

## 5. Red de piso: caja sumidero, tubería y accesorios

### 5.1 Caja sumidero (láminas DS-01 isométrico y DS-02 corte, planta, explosionado y desagregado)
| Pieza | Medida |
|---|---|
| Rejilla | 0.25 x 0.25 m de platinas 1" x 3/16" de canto, 9 platinas interiores @0.025 entre ejes (abertura libre ~0.020), removible, apoyada en el ala del marco sin soldar |
| Marco | Ángulo L 1" x 1" x 3/16" al ras del piso terminado, interior 0.254 (holgura 2 mm por lado) |
| Anclajes | 8 de fierro 3/8" x 3" (2 por lado) soldados al marco, a 45° hacia el concreto |
| Caja | Concreto f'c = 140 kg/cm², exterior 0.45 x 0.45, 0.10 m de profundidad bajo el piso en la pared, fondo inclinado hacia la salida (0.13 en la salida) |
| Salida | PVC-U 4" en el centro del fondo + **un solo codo PVC 4" x 90°** (sin trampa ni sifón: decisión del 10-10-2026) |
| Tubería | PVC-U 4" clase pesada a la cuneta, S ≥ 1.0 % (IS.010), descarga en el muro de la cuneta sobre su fondo |

Desagregado por sumidero (`planos_sumidero.desagregado()`):
| Material | Cantidad | kg |
|---|---|---|
| Platina 1" x 3/16" (marco de rejilla + 9 platinas): 4 x 0.25 + 9 x (0.25 − 2 x 0.0048) | 3.164 m | 3.00 (0.949 kg/m) |
| Ángulo L 1" x 1" x 3/16": 4 x (0.254 + 0.0048) | 1.035 m | 1.79 (1.73 kg/m) |
| Anclajes 3/8" x 3" | 8 x 0.075 = 0.60 m | 0.34 (0.56 kg/m) |
| Pintura anticorrosiva + 2 manos de esmalte | 0.296 m² | – |
| Concreto f'c 140 de la caja | 0.035 m³ | – |
| Mortero 1:4 (fondo inclinado y asentado) | 0.004 m³ | – |
Acero total ≈ 5.13 kg por sumidero. Soldadura E6011 1/8" en todos los encuentros; acero A36 con anticorrosivo y esmalte.
La tubería de 4" y los codos se pagan en sus propias partidas, no dentro del sumidero.

Ubicación: en el punto bajo del piso; el piso tiene pendiente hacia el sumidero.

### 5.2 Hoja METRADO EN PISO (SUMIDERO) y cantidades
Por sector: tubería 4" PVC-U clase pesada (m), sumidero 4" (und), codo 90° x 4", codo 45° x 4", tee x 4".

| Proyecto | Tubería PVC-CP 4" (m) | Sumideros | Codo 90° | Tee |
|---|---|---|---|---|
| Hogar de Refugio (4 sectores) | 112.56 | 30 | 24 | 4 |
| CAR Varones | 92.08 | 16 | 13 | 3 |
| CAR Mujeres | 73.20 | 39 | 37 | 2 |

Partidas (Hogar de Refugio): 01.04.03.05.02.01 TUBERIA DESAGÜE PVC-CP Ø4" (m); .02 SUMIDERO METALICO C/PLATINA 1" X 3/16" (und);
.03 CODO DESAGÜE PVC Ø4" x 90° (und); .04 TEE SANITARIA DESAGÜE PVC Ø4" (und). Ojo: el codo de 90° aparece en la red de piso y en
accesorios del techo (01.04.03.05.03.02); los generadores distinguen por el código ("05.02." = piso).

Especificación de la tubería: zanja 0.40 de ancho, cama de arena 0.10, campanas aguas arriba, prueba hidráulica 15 min sin fugas,
relleno en capas de 0.15 con los primeros 0.30 de material fino. Medición entre ejes de accesorios sin descontarlos.

Generador: `herramientas/techo/planos_sumidero.py [varones refugio mujeres]` →
`entregables*/PLANOS_DETALLE_SUMIDERO_PISO_*.dxf` (1/5).

---

## 6. Cunetas de concreto armado (componentes de la sección)

### 6.1 Sección tipo
- Ancho interior 0.40, muros 0.10, losa de fondo 0.10, ancho exterior **0.60**; tramos tapados con losa superior (tapa) de 0.10.
- Solado f'c 100 kg/cm² e = 4" (0.10) bajo la losa de fondo (CAR); concreto f'c 175 kg/cm² en muros, losa de fondo y losa superior,
  piedra chancada 1/2", slump 3" a 4".
- Pendiente S = 0.5 %; n = 0.015.
- Rebaje para la rejilla: 0.05 x 1" en el borde interior de cada muro (formado con listones al vaciar).
- H (altura) se mide desde el NCT (nivel de corona / borde superior) al fondo interior, en abierta y en tapada.
- Recubrimientos (leyenda de cunetas): 0.025 m en caras interiores y losa superior; 0.04 m en caras contra el terreno.
  Traslape Ø 3/8" 0.60 m mínimo alternado (E.060, 12.15). Peso Ø 3/8" = 0.56 kg/m.

### 6.2 Acero (regla del usuario, 04-10 y 21-10-2026)
- Lleva acero solo si **H > 0.40 m** (CAR, medido desde el NCT) / **h ≥ 0.40 m de la rejilla al fondo** (Barranquita). Menor:
  concreto simple.
- **Tramo tapado: lleva acero siempre** (cuerpo en U + tapa), aunque H < 0.40.
- Tramo abierto que pasa de 0.40 dentro de su longitud: se metra desde la progresiva donde H = 0.40.
- Transversal Ø 3/8" en U @0.25 (desarrollo 0.60 + 2(H + 0.05)); longitudinales Ø 3/8" @0.20 si H < 0.45, @0.22 si H < 0.60,
  @0.25 si mayor; barras longitudinales = REDONDEAR.MAS((0.60 + 2H)/sep).
- Tapa de tramo tapado: Ø 3/8" @0.25, barra transversal **0.56 m siempre**.
- Barranquita: U 3/8" @0.25 con ganchos de 0.10; longitudinales 3/8" @0.20 en muros y fondo; losa tapa 3/8" @0.20 transversal y
  3 barras longitudinales.
- El acero longitudinal se interrumpe a 0.05 m a cada lado de cada junta (no la atraviesa).

### 6.3 Tramos tapados (cruces de vereda, ingresos, pasadizos)
- Losa superior de 0.10 vaciada con los muros (monolítica).
- Barranquita: altura libre bajo la losa ≥ 0.25 m (profundidad mínima = 0.25 + 0.10); la capacidad se verifica con la altura libre.
  El usuario rechazó secciones de 0.15 m ("se obstruye el flujo").

### 6.4 Tapas de inspección 0.60 x 0.60 en cunetas tapadas
- Concreto armado f'c 210 de 0.60 x 0.60 x 0.10 (tapa de registro interno), parrilla simple 3/8" @0.15 en ambos sentidos,
  recubrimiento 0.025, 2 asas embutidas en bolsillo (no sobresalen), holgura 5 mm, al ras del piso; molde sobre base plana,
  curado 7 días.
- Hoja PLANILLA TAPAS REGISTRO INTERNO + PARAMETROS (B4 cantidad, B5/B6 lado 0.60, B7 espesor 0.10, B8 recubrimiento 0.025,
  B9 separación 0.15, B10 peso 0.56 kg/m):
  - Concreto = N x 0.60 x 0.60 x 0.10.
  - Encofrado = N x [2(0.60 + 0.60) x 0.10 + 0.60 x 0.60] (laterales + fondo).
  - Acero por sentido = N x (0.60 − 2 x 0.025) x (REDONDEAR((0.60 − 2 x 0.025)/0.15; 0) + 1) x 0.56 (0.55 x 5 barras).
- Cantidades: Hogar de Refugio 17 und (0.612 m³, 10.20 m², 52.36 kg; la nota de PARAMETROS D4 dice "según resumen: 10 tapas",
  pero el valor vigente es 17), CAR Varones 18 und ("provisional: 1 tapa por tramo tapado; confirmar con el plano"),
  CAR Mujeres 10 und, Barranquita 10 und.
- Regla de ubicación propuesta (Barranquita, `planta_cunetas_b._tapas`; el usuario no fijó distancia): al inicio y al final de cada
  tramo tapado, en cada empalme dentro del tramo tapado (si no hay otra a menos de 2.0 m) y a **10 m como máximo**; la última se
  separa del cerco o de la cuneta receptora (0.075 + 0.15 + 0.30 en descarga; 0.30 + 0.30 en otra cuneta); en tramos cortos
  (≥ 0.70 m) una al centro. Lista en `_calc/tapas.json` y hoja "TAPAS INSPECCION".
- Partida: 01.04.03.04.03.02 TAPA DE INSPECCION 0.60m x 0.60m (und).

### 6.5 Rejilla metálica móvil (lámina DJ-03, partida 01.04.03.04.03.01)
- Nombre Delphin: REJILLA METALICA P/CUNETA C/PL 1''x 3/16'' Y ANGULO 1'' x 1'' x 3/16'', S/DETALLE (m).
- Módulos removibles de **1.00 m** (0.997 m fabricado, 3 mm entre módulos), ancho **0.497 m** (0.40 + 2 x 0.05 − 2 x 0.0015),
  holgura 1.5 mm por lado.
- Marco: 2 ángulos L 1" x 1" x 3/16" longitudinales (1.73 kg/m), ala horizontal apoyada en el rebaje y ala vertical hacia la cuneta.
- **39 platinas 1" x 3/16" de canto @1" entre ejes** (abertura libre 0.021 m), longitud 0.446 m (0.497 − 2 x 1"), transversales al
  eje, soldadas a tope al ala vertical (2 cordones E6011 1/8" de 1" por platina = 78 por módulo). Platina 0.95 kg/m.
- Peso: 39 x 0.446 x 0.95 + 2 x 0.997 x 1.73 = **20.0 kg por metro de rejilla**.
- Pintura: 2 manos de anticorrosivo + 2 de esmalte (superficie de platinas y ángulos); acero A36; esmerilar soldaduras.
- A ras del borde superior de la cuneta; no se fija al concreto. En la junta de la rejilla con el piso adyacente va la junta de 1" con
  relleno asfáltico (detalle 1).
- Metrado (hoja METRADO DE REJILLAS): por tramo, `LONGITUD CON REJILLA = SI(TIPO="ABIERTA"; MAX(LONGITUD − DESCUENTO; 0); 0)`;
  los tapados no llevan rejilla; los descuentos (puertas, cruces) se ingresan a mano.

| Proyecto | Rejilla (m) |
|---|---|
| Hogar de Refugio (30 tramos, 12 ejes) | 510.11 |
| CAR Varones | 373.85 |
| CAR Mujeres | 627.93 |
| Barranquita | 924.82 |

Planta de cunetas (estilo del usuario, Barranquita): rejilla con bordes exterior 0.60 e interior 0.40 en celeste y platinas
dibujadas cada 0.10 m (símbolo); tapada con bordes en verde; tapas de inspección en azul; flechas rojas de flujo cada 5 m y en
cada quiebre a 45°. Recomendación pendiente: rejilla de tránsito vehicular en las cunetas del patio de maniobra.

---

## 7. Juntas de dilatación de cunetas (partida 01.04.03.04.03.03)

### 7.1 Criterio normativo (decidido el 14/15-10-2026)
- EG-2013 MTC, **Sección 510** (cunetas revestidas de concreto): la junta corta **toda la sección en U** (los dos muros y la losa de
  fondo) para que cada paño de 3.00 m trabaje independiente; una junta solo en los muros deja la losa amarrada y se fisura.
- Texto del usuario (14-10): "el tecnopor va en toda la sección (U o triángulo) de la cuneta y el asfalto actúa solo como sello
  superficial".
- Junta e = 1" (0.0254 m): plancha de tecnopor de 1" en todo el espesor + sellador asfáltico 1" x 2" (25 x 50 mm) de asfalto líquido
  RC-250 (NTP 321.028) + arena gruesa en la cara interior. Cada **3.00 m** y en los cambios de dirección. El solado se vacía corrido.
- Nombre Delphin: JUNTA DE DILATACION E=1" CON SELLADOR ASFALTO (m).

### 7.2 Metrado (hoja METRADO JUNTA DE DILATACION)
Parámetros: B8 espaciamiento 3.00; B9 muros con junta 2; B10 ancho interior del fondo 0.40.
Por eje: longitud D; área de muro E (de CONCRETO EN CUNETAS); altura media F = E/D; G = 3.00;
`N° de juntas H = REDONDEAR.MAS(D/G; 0)`; `longitud por junta I = $B$9·F + $B$10 = 2·H + 0.40`; `parcial J = H·I`.

| Proyecto | Juntas | Total (ml) | Método |
|---|---|---|---|
| Hogar de Refugio (12 ejes) | 233 | 241.96 → **335.16** | sección en U (desde 15-10-2026) |
| CAR Varones (9 ejes) | 185 | **252.29** | sección en U |
| CAR Mujeres | – | 230.46 | método antiguo (congelado): N° juntas x 2 muros x H |
| Barranquita | – | 547.80 | sección en U: `N = ENTERO(L/3.00)`, desarrollo = 2(h + ef) + be |

Ejemplo (Hogar de Refugio, Eje 02): L 130.85, área 78.32 → H 0.5985; 44 juntas x (2 x 0.5985 + 0.40 = 1.5971) = 70.27 ml.
Diferencia a notar: Barranquita mide con ENTERO y desarrollo exterior 2(h + 0.10) + 0.60; los CAR con REDONDEAR.MAS e interior
2H + 0.40. Unificar el criterio antes de llevarlo a un programa (ver §13).

### 7.3 Proceso constructivo (lámina DJ-02, 4 isométricos 3D)
1. Vaciar el paño 1 (losa de fondo y muros) hasta la junta con tapa de encofrado en U; el acero longitudinal termina a 0.05 de la cara.
2. Desencofrar la tapa y pegar la plancha de tecnopor 1" cortada con la forma de la U: cubre los 2 muros y la losa de fondo, a ras del
   borde y del rebaje.
3. Armar el acero del paño 2 (U transversal 3/8" @0.25 y longitudinales 3/8") sin cruzar la junta y vaciar contra la plancha
   (encofrado perdido).
4. Retirar 2" (50 mm) de tecnopor en la cara interior de muros y fondo; limpiar y secar; calentar el RC-250, mezclarlo con arena gruesa
   y compactarlo con tacos de madera hasta el ras.
5. Colocar la rejilla en el rebaje (DJ-03). Junta continua y alineada: muro – fondo – muro.
6. Control: sellador compacto, al ras, sin filtraciones. Seguridad: calentar el asfalto lejos de inflamables, extintor a la mano.

### 7.4 Lámina DJ-01 (detalle y metrado)
A sección en la junta 1/5 (longitud por junta = 2 x H + 0.40, cara interior sellada); B detalle 1/2 (tecnopor 1", sellador 2",
acero a 0.05); C planta de un tramo 1/25 (juntas cada 3.00); D corte longitudinal 1/25 (acero interrumpido); E cuadro de metrado por
eje leído de la planilla (el generador comprueba que la suma coincide con J12).

### 7.5 Junta cuneta – piso adyacente
- Junta asfáltica e = 1" en todo el contacto de la cuneta con el piso, vereda o losa adyacente.
- Barranquita: partida propia 01.04.02.04 JUNTA E=1" CON SELLADOR ASFALTICO ENTRE CUNETA Y PISO ADYACENTE = 748.76 m (borde de cuneta
  al ras del NPT +184.65, junta al mismo nivel del piso). En los CAR va dentro del detalle 1 de la rejilla.

### 7.6 Juntas del colector relacionadas (resumen; detalle en el documento del colector)
- 01.04.04.06.01 JUNTA DE DILATACION E=1" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR: cada 4.00 m en toda la sección; tecnopor
  1" + sellador asfáltico 1" x 2" (RC-250 + arena) en caras interiores y cara superior (Refugio 100.64 m; Varones 26 juntas, 120.64 m;
  perímetro por junta Varones 2 x 0.90 + 2 x (0.15 + 1.17 + 0.10) = 4.64 m).
- 01.04.04.06.02 Hogar de Refugio: JUNTA E=1" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO, solo la junta
  longitudinal muro–cimiento del cerco (plancha de 0.90 m de altura), 0+000.00 a 0+058.81 = 58.81 m (antes 209.78/210.98). El otro lado
  es terreno natural: sin junta. CAR Varones (sin cerco): ENTRE COLECTOR Y CAJA CL, 4.64 m.
- Antes: "sellador elastomérico" (desechado el 14-10 por pedido del usuario). CAR Varones conservaba poliuretano en sus planos hasta el
  15-10 (`SELLO_JUNTA` en `varones/compat.py`), luego pasa también a asfáltico.
- ACU (Hogar de Refugio, valores vigentes): junta de dilatación 11.66 S/ por m; junta con el cerco 8.49 S/ por m (la bitácora del 15-10
  registró 12.01 y 6.12, antes de la junta de 0.90 m). ACU de Varones: 11.60 S/ por m. Datos: tecnopor Sodimac 1" x 1.20 x 2.40
  S/ 13.90 con IGV; RC-250 Conselva S/ 17.70 el galón con IGV; 50 gal de RC-250 por m³ de mezcla; arena 1.05 m³/m³.

Generadores: `herramientas/junta_cunetas_seccion_refugio.py` (cambia la hoja: B10 = 0.40, I = $B$9·F + $B$10, notas),
`herramientas/planos_junta_cunetas.py` (DJ-01), `herramientas/planos_junta_cunetas_iso.py` (DJ-02, DJ-03),
`herramientas/varones/planos_junta_cunetas_v.py`, `herramientas/acu_juntas_refugio.py`. Salidas
`entregables/PLANOS_DETALLE_CUNETAS_JUNTA_Y_REJILLA_HOGAR_REFUGIO.dxf` y `entregables_varones/PLANOS_DETALLE_CUNETAS_JUNTA_Y_REJILLA_CAR_VARONES.dxf`.

---

## 8. Lloraderos en cunetas colindantes con área verde (partida 01.04.03.04.03.04)

### 8.1 Alcance y decisión
- 08-10-2026: solo en el Hogar de Refugio y en el CAR Varones; el CAR Mujeres no lleva (presupuesto congelado; confirmado el 19-10).
- Nombre Delphin: LLORADERO DE TUBERIA PVC Ø3" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m (CUNETA COLINDANTE CON AREA VERDE) (und).
- Función: aliviar la presión del agua infiltrada en el terreno por las lluvias y descargarla dentro de la cuneta.
- 10-10-2026: el subdrén se retiró; solo lloraderos.
- Partida nueva: no modifica ninguna otra partida (comparadas todas antes y después).

### 8.2 Regla de ubicación
- Solo los muros de cuneta colindantes con área verde (o terreno natural sin cobertura): tramo de muro cuya **franja exterior de
  0.30 m** cae dentro del achurado de área verde de la planta general de drenaje. No en tramos junto a veredas, pisos o edificaciones.
- No se cuentan tramos menores de 1.50 m. Si ambos muros dan al área verde, va en los dos (se registra cada lado por separado).
- Progresivas desde el inicio de cada eje (igual que los perfiles), recortadas a la longitud del eje del metrado.
- Lado del muro: ESTE / OESTE / NORTE / SUR (rumbo, con el norte arriba).
- Espaciamiento típico L = 1.50 m, a **media altura del muro**; el primero y el último a no menos de 0.30 m de las juntas de dilatación.
- Número por tramo: `N = REDONDEAR.MAS(longitud / 1.50; 0)`, repartidos en el tramo (centrados en su paño en el plano DL-00).
- Capas de área verde reconocidas en las plantas: Hogar de Refugio HIERVA; CAR Varones HIERVA, Area Verde, Hatch Jardin.

### 8.3 Componentes de un lloradero (láminas DL-01/DL-02; Varones DPLV-34/35; Refugio DPL-37/38)
| Componente | Medida | Detalle |
|---|---|---|
| Tubo PVC-U Ø 3" (76 mm) desagüe NTP 399.003 | L = 0.30 m | 0.10 en el muro + 0.20 perforado dentro del filtro; S = 0.5 % hacia la cuneta (extremo exterior más alto); extremo interior al ras de la cara del muro |
| Perforaciones Ø 3/8" | 8 por tubo | 2 filas a 120° (simétricas respecto al fondo), 4 por fila @0.05 |
| Filtro localizado | 0.30 x 0.30 x 0.30 m = 0.027 m³ | grava filtrante (ripio) 20 a 40 mm, limpia, lavada, sin finos ni materia orgánica; pegado a la cara exterior del muro |
| Geotextil no tejido clase 2 (ASTM D4491, D4751) | 6 caras + 10 % = 0.594 m² | traslape 0.10; envuelve todo el filtro; tapa el extremo del tubo |
| Mortero 1:3 de sellado | 0.0005 m³ | anillo de 0.02 en las dos caras del muro |
| Excavación local del hueco | 0.027 m³ | incluida en la mano de obra |

### 8.4 Procedimiento (DL-02)
1. Antes del vaciado del muro, fijar al encofrado el tubo de 0.30 m ya perforado, a media altura, con S = 0.5 % y extremos tapados.
2. Vaciar; al desencofrar, destapar y sellar el contorno con mortero 1:3 si quedó holgura.
3. Excavar en el lado del terreno el hueco 0.30 x 0.30 x 0.30 centrado en el tubo y forrarlo con geotextil dejando las solapas afuera.
4. Llenar con grava 20-40 mm sin romper el geotextil.
5. Cerrar el geotextil por encima con traslape de 0.10 y rellenar y compactar en capas de 0.15.
6. Prueba: al verter agua sobre el filtro debe salir por el lloradero; se repara el que no drene. Nunca a contrapendiente.

DL-01 (1/10): isométrico de un tramo de 4.50 m con 3 lloraderos @1.50 (x = 0.75, 2.25, 3.75) mostrados en las 3 etapas y junta a 3.00;
elevación del muro desde el área verde.

### 8.5 Metrado (hoja METRADO LLORADEROS)
Columnas: N°, EJE, PROGRESIVA (desde – hasta), LADO DEL MURO, LONGITUD JUNTO A ÁREA VERDE, ESPACIAMIENTO 1.50,
`N° = SI(B="";"";REDONDEAR.MAS(E/F;0))`. Notas de criterio 1 a 4 al pie.

Hogar de Refugio (12 tramos, 226.21 m, **157 und**):
| N° | Eje | Progresiva | Lado | L (m) | N° |
|---|---|---|---|---|---|
| 1 | 01 | 0+000.00 a 0+037.00 | ESTE | 37.00 | 25 |
| 2 | 01 | 0+032.25 a 0+037.00 | OESTE | 4.75 | 4 |
| 3 | 02 | 0+040.62 a 0+045.37 | SUR | 4.75 | 4 |
| 4 | 07 | 0+040.62 a 0+042.87 | SUR | 2.25 | 2 |
| 5 | 07 | 0+123.97 a 0+125.70 | ESTE | 1.73 | 2 |
| 6 | 07 | 0+123.97 a 0+125.70 | OESTE | 1.73 | 2 |
| 7 | 09 | 0+000.50 a 0+005.00 | SUR | 4.50 | 3 |
| 8 | 11 | 0+069.05 a 0+071.30 | ESTE | 2.25 | 2 |
| 9 | 11 | 0+039.50 a 0+062.75 | OESTE | 23.25 | 16 |
| 10 | 11 | 0+066.80 a 0+071.30 | OESTE | 4.50 | 3 |
| 11 | 12 | 0+078.50 a 0+109.00 | ESTE | 30.50 | 21 |
| 12 | 12 | 0+000.00 a 0+109.00 | OESTE | 109.00 | 73 |

CAR Varones: **34 tramos, 320.53 m, 226 und** (ejes 01 a 09; p. ej. Eje 01 ESTE 0+013.50 a 0+019.00, 0+054.75 a 0+077.25 y
0+080.75 a 0+111.53 → 4 + 15 + 21; Eje 06 ESTE 0+000.00 a 0+034.25 → 23; Eje 09 OESTE 0+000.25 a 0+021.75 → 15).

### 8.6 Hoja DESAGREGADO LLORADEROS (materiales de la partida)
A. Ubicación y número enlazados a METRADO LLORADEROS; B. datos del detalle (lado 0.30, tubo 0.30, 4 perforaciones por fila, 2 filas,
desperdicio de grava 10 %, traslapes de geotextil 10 %, mortero 0.0005); C. componentes; D. control con el RESUMEN
(`SI(ABS(E−F)<0.001;"CONFORME";"REVISAR")`).

| Componente | Por lloradero | CAR Varones (226) | Hogar de Refugio (157) |
|---|---|---|---|
| Tubo PVC-U Ø 3" (m) | 0.30 | 67.80 | 47.10 |
| Perforaciones Ø 3/8" (und) | 8 | 1808 | 1256 |
| Excavación local (m³) | 0.027 | 6.102 | 4.239 |
| Grava 20-40 mm (m³) = 0.30³ x 1.10 | 0.0297 | 6.71 | 4.66 |
| Geotextil (m²) = 6 x 0.30² x 1.10 | 0.594 | 134.24 | 93.26 |
| Mortero 1:3 (m³) | 0.0005 | 0.113 | 0.079 |

Respuesta al usuario (23-10): el desagregado (piedra, tubo perforado, geotextil) está en DESAGREGADO LLORADEROS, no en
METRADO LLORADEROS (que solo cuenta unidades por tramo), y está valorizado en ACU LLORADEROS.

### 8.7 ACU LLORADEROS (S/ 20.56 por und; Varones S/ 4,646.15; Refugio S/ 3,227.64)
- Rendimiento 24 und/día; cuadrilla 0.5 operario + 1 peón → operario 0.1667 hh x 28.95; peón 0.3333 hh x 20.54 (MO 11.67).
- Tubo 0.30 x 1.05 = 0.315 m a 11.27 (Pavco 3" x 3 m liviano S/ 39.90 con IGV en Sodimac/Promart; 10 lloraderos por tubo);
  grava 0.0297 m³ a 59.32 (Agregados Tarapoto, Morales: piedra chancada 3/4" S/ 70.00 el m³, el más cercano a 20-40 mm);
  geotextil 0.594 x 1.05 = 0.6237 m² a 4.87 (Ferropolis: rollo 4 x 100 m S/ 2,300); cemento 10.5 bol/m³, arena 1.05, agua 0.27 por m³
  de mortero (precios de la ACU TAPA REGISTRO); herramientas 3 % MO.
- Pendiente de cotizar en Tarapoto: grava 20 a 40 mm.

### 8.8 Planos y legibilidad
- DL-00 planta de ubicación (A1 a 1/250; Refugio DPL-40 A0): planta de arquitectura en gris, cunetas en azul, áreas verdes en verde
  sólido, tramos con línea gruesa (ancho 0.30) numerados como la hoja, cada lloradero en su posición, cuadro de tramos (TRAMO, EJE,
  PROGRESIVA, LADO, LONGITUD, ESPAC., N°), leyenda, notas y detalle típico. Ejes en `insumos/solange/EJES_CUNETAS_REFUGIO.json` e
  `insumos/katiuska/EJES_CUNETAS_VARONES.json`. Refugio: lado por tabla LADO (+1 izquierda / −1 derecha respecto al sentido de la
  progresiva); Varones: por el rumbo de la hoja comparado con la normal al eje.
- 22-10-2026: en AutoCAD los patrones EARTH, AR-CONC, AR-SAND y GRAVEL salían sin la escala del bloque y "m³" como "m?". Para el
  Hogar de Refugio el detalle y la leyenda se dibujan **sin patrones**: rellenos sólidos con color verdadero, piedras de grava una por
  una (20 a 40 mm a escala real), punteado de concreto y solado, trazos de tierra, cotas en gris oscuro fijo (legibles con fondo negro
  y blanco), "m3"; dos presentaciones A3 a 1:10 (ESPECIFICACIONES y DETALLE LLORADERO). Regla general: **no usar patrones de achurado
  en bloques que se escalan**.
- Bloque ESPEC_LLORADEROS (leyenda y especificaciones) a escala real; detalle con H dibujada 0.50 (variable según perfil).

Generadores: `herramientas/techo/planos_lloraderos.py [varones refugio]` (DL-01, DL-02), `herramientas/planos_ubicacion_lloraderos.py
[refugio|varones]` (DL-00), `herramientas/espec_lloraderos.py`, `herramientas/desagregado_lloraderos_refugio.py`,
`herramientas/acu_lloraderos_refugio.py`. Especificación de la partida en `especificaciones/espec.py` (lee el cuadro de
DESAGREGADO LLORADEROS si existe).

---

## 9. Tapa ciega de concreto armado del registro del colector (0.68 x 0.68 x 0.08)

### 9.1 Historia de decisiones
| Fecha | Versión | Contenido |
|---|---|---|
| 03-10-2026 | DP-06B rev. 00 | Tapa 0.68 x 0.68 x 0.08 f'c 210 malla 3/8" @0.10 con marco L 1 1/2"x1 1/2"x1/8" y contramarco L 2"x2"x3/16" (0.70/0.80) con 8 anclajes 3/8" L 0.20; luz 0.60; borde engrosado 0.15 x 0.10; refuerzo de borde 8 Ø 1/2" L 1.40 |
| 07-10-2026 | DP-06B rev. 01 | Tapa asentada sobre el ala del contramarco; 7 componentes del metrado unidos en una partida por und; hojas DESAGREGADO y ACU (383.29 S/ por tapa antes del cambio del 14-10); 3D, isométricos y fotos |
| 14-10-2026 | Refugio | Contramarco L 1 1/2"x1 1/2"x1/8" (carga peatonal; el asiento apoya en el borde engrosado; el L 2"x2"x3/16" no tiene precio publicado en tiendas). Ángulos 151.42 → 101.02 kg (15.14 → 10.10 kg por tapa: 2.80 x 1.83 + 2.72 x 1.83); pintura 9.82 → 8.39 m² (0.84 m² por tapa); lija y thinner separados; ACU 383.29 → 297.45 S/ por tapa (partida 2,974.50). CAR Varones conserva L 2"x2"x3/16" |
| 16-10-2026 | DP-06B rev. 02 (vigente) | **Tapa ciega**: vaciada aparte en obra, sin marco, contramarco, anclajes, soldadura ni pintura; asiento en rebaje de concreto. DP-06B nueva en los 3 CAR; metrado actualizado solo en Hogar de Refugio (10 tapas, ACU 182.06) y CAR Varones (11 tapas, ACU 182.06) |
| 20-10-2026 | CAR Mujeres | El plano D-RL de su juego final muestra tapa ciega, pero su metrado (congelado) sigue con 1.4.4.6.5.1 TAPA DE REGISTRO 0.68x0.68 C/MARCO Y CONTRAMARCO (15 und) y el isométrico 2 de IC-01 dibuja marco y contramarco: pendiente de decisión del usuario |

### 9.2 Geometría vigente (rev. 02; `render_tapa/modelo.py`, `dxf_tapa_ciega.py`)
| Elemento | Medida |
|---|---|
| Tapa | 0.68 x 0.68 x 0.08, f'c 210, cantos superiores biselados 1 x 1 cm; peso ≈ 0.68² x 0.08 x 2400 = **89 kg** (2 operarios con ganchos) |
| Parrilla | 3/8" @0.10 en ambos sentidos: 7 + 7 barras L = 0.62 (14 x 0.62 x 0.56 = 4.86 kg); recubrimiento 2.5 cm; barras en X abajo (z −0.055), en Y arriba (z −0.0455) |
| Asas | 2 de fierro liso 1/2" (A36): agarre 0.15, patas 0.02, ganchos 0.15 → desarrollo 0.49 (se toma 0.50); eje a ±0.20 del centro; en cajuelas 0.19 x 0.06 x 0.03 (no sobresalen); ganchos amarrados a la parrilla con alambre N° 16; 2 x 0.50 x 0.994 = 0.99 kg |
| Rebaje (asiento) | 0.70 x 0.70 x 0.08 en la losa superior (0.05 por lado), plano y nivelado, chaflán 1 x 1 cm; holgura 1 cm por lado; la tapa queda al ras del NPT (vereda), removible, sin sello de mortero |
| Luz libre | 0.60 x 0.60 bajo el rebaje (en los 0.02 restantes de la losa de 0.10) |
| Borde engrosado | 0.15 x 0.10 bajo la losa, anillo de la luz 0.60 a 0.90 (perímetro de cálculo 4 x 0.75 = 3.00 m) |
| Refuerzo de borde | 8 Ø 1/2" L = 1.40 (2 barras por lado a ±0.40 del eje; CAR Mujeres ±0.39), en dos niveles (z −0.045 y −0.155): 8 x 1.40 x 0.994 = 11.13 kg |
| Descuento de la losa por registro | 0.49 x 0.08 + 0.36 x (e_losa − 0.08) (= 0.0464 m³ con losa 0.10) |

Caso CAR Varones (colector b = 0.60 ≤ luz 0.60, `MURO_APOYO`): en los lados largos el rebaje apoya en la cabeza de los muros y los
anclajes (versión anterior) bajaban dentro del muro; el borde engrosado va solo en los 2 lados transversales entre muros
(2 x 0.60 = 1.20 m por registro; antes se había copiado el de 3.00 m del Refugio); las barras transversales de borde siguen de
1.40 m con ganchos de 0.29 dentro de los muros (`GANCHO = (1.40 − 2(BI + BW − 0.04))/2`). Concreto del colector 56.02 → 55.72 m³.

Proceso (notas DP-06B): vaciar sobre tablero nivelado con molde lateral de madera 0.68 x 0.68 x 0.08; desmoldar a las 24 h; curado
húmedo ≥ 7 días; colocar con 70 % de f'c; el rebaje se forma con un cajón de madera fijado antes del vaciado de la losa; registros
fuera de los cruces vehiculares.

### 9.3 Metrado y ACU (CAR Varones y Hogar de Refugio)
- Partida 01.04.04.05.01 TAPA DE REGISTRO CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08 (und): Refugio 10 (CL, RS-01 a RS-07, CC con 2),
  Varones 11 (RV-01 a RV-11). Partida Delphin del ACU: 01.04.04.06.05.01.
- Hoja COLECTOR REGISTROS Y TAPAS: tapa (und), encofrado lateral = N x 4 x 0.68 x 0.08 (0.2176 m²/und), acero de tapas (parrilla +
  asas), concreto = N x 0.68² x 0.08 (0.037 m³/und), asiento en rebaje (concreto incluido en la losa), colocación.
- DESAGREGADO TAPA REGISTRO por registro: concreto 0.037 m³; encofrado 0.2176 m²; parrilla 4.8608 kg; asas 0.994 kg; borde 11.1328 kg
  (subtotal acero 16.99 kg). Control "CONFORME" contra las hojas del colector. "No hay ángulos, soldadura ni pintura".
- ACU (S/ 182.06 por und; Varones partida 2,002.65): operario 1.7473 hh, oficial 0.7473, peón 1.2367 (concreto 0.8/0.8/6.4 hh/m³; acero
  0.032 hh/kg; encofrado 0.8 hh/m²; colocación 1 hh); cemento 9.73 bol/m³ (Pacasmayo tipo I S/ 36.50 con IGV → 30.93), arena 0.52 m³/m³
  a 40.68, piedra 1/2" 0.53 a 101.69 (por cotizar en Tarapoto), agua 0.186 + 0.01 de curado a 8.33 (EMAPA San Martín), madera tornillo
  4 x 0.68 x 0.08 x 4.24/6 + 1.15 p² de tablero (0.80 x 0.80 x 1" en 6 usos) a 4.41, acero corrugado y fierro liso 3.44 S/ por kg
  (Aceros Arequipa en Sodimac), alambre N° 16 al 6 % a 5.08, herramientas 3 % MO.
- Lija y thinner (versión con contramarco, 14-10): el global "lija y thinner" 0.05 glb/m² se reemplazó por lija para fierro N° 80
  0.25 und/m² (1 pliego ≈ 4 m², S/ 2.12 sin IGV) y thinner = 15 % del volumen de pintura (10 % dilución + 5 % limpieza) = 0.0240
  gal/m² (S/ 35.65 el galón sin IGV). Dejó de aplicar con la tapa ciega (sin pintura).
- Generadores: `herramientas/tapa_ciega.py <planilla>` (edita el XML: COLECTOR PARAMETROS, REGISTROS Y TAPAS, ACERO, CONCRETO, INSUMOS,
  PLANILLA, RESUMEN; rehace ACU y DESAGREGADO), `render_tapa/dxf_tapa_ciega.py <salida.dxf> <refugio|varones|mujeres>` (DP-06B, A1 en mm,
  render 0 0 841 594), `render_tapa/dxf_tapa_3d.py` (DP-06D: 4 isométricos, despiece, corte y armado), `render_tapa/foto.py` (vistas
  fotorrealistas), `render_tapa/iso.py`; históricos: `render_tapa/dxf_tapa.py` (rev. 01 con marco), `cotizacion_tapa_registro.py`,
  `angulo_contramarco_refugio.py` (también da la clase `Libro` para editar planillas sin perder formato), `acu_lija_thinner.py`.
- Láminas que se revisan en cada cambio de tapa: DP-06B, DP-06D, DD-01 (rebaje y refuerzo de borde), DD-02 (fabricación y colocación),
  DP-08, DP-09, DA-03, isométricos, especificaciones y memoria. CAR Varones: DPLV-23 (DP-06B).

---

## 10. Bancas con techo: canaleta, boquilla y bajada

### 10.1 CAR Mujeres (CUI 2717013): banca de jardinería tipo 01 (19-10-2026)
- Insumo: `insumos/wilma/detalle_banca/DETALLE_DE_BANCA_TIPO_01.dxf` (escala real). Regla: **fiel al dibujo**.
- Techo a una agua de 2.00 x 2.40 (cobertura 0.30 de caída en 2.40, pendiente 12.5 %); columnas de tubo rectangular 4" x 10" x 3 mm.
- Canaleta de plancha de **aluzinc e = 0.50 mm**, interior **0.18 (ancho) x 0.20 (alto)**, ala posterior 0.10 sobre la viga bajo la
  cobertura, S = 0.5 %, **un solo tramo de 2.00 m por techo** (sin uniones), fondo en la boquilla +2.385; cobertura hasta la cara
  posterior de la canaleta (vuelo 0.013).
- **2 soportes de platina F°G° 1" x 1/8"** a 0.40 de cada extremo (1.20 entre ellos) (el usuario: "¿por qué tanto soporte en 2 m?").
- 2 tapas laterales; 1 boquilla de aluzinc (brida 0.16 x 0.16 con 8 remaches y sellador, cuello Ø 0.10 x 0.15) a 0.30 del extremo,
  en el eje de la columna derecha (x = 1.70); "solo la boquilla", sin capucha ni sumidero.
- Bajada: boquilla → niple → codo 4" x 90° → tramo horizontal de 0.38 con colgador a la viga 2" x 2" (eje +2.129) → codo → bajada
  adosada a la columna con abrazadera (+1.77) → falsa columna CL-01 0.20 x 0.15 de −0.15 a +1.05 (jardín −0.15).
- Diferencias del plano de origen informadas: falsa columna rotulada H = 1.50 pero dibujada 1.20; elevación E2 de 0.15 de ancho y
  planta de 0.20; no se indica a dónde descarga la bajada.
- Láminas (`herramientas/techo/planos_banca_m.py` → `entregables_mujeres/PLANOS_ISOMETRICO_BANCA_JARDINERIA_CAR_MUJERES.dxf`): DB-01
  isométrico 1/15; DB-02 extremo de la canaleta 1/5 con corte de canaleta y sección C-C de la falsa columna; DB-03 corte A-A (lateral)
  y corte B-B (frontal) 1/10 con cotas y niveles. El usuario pidió también cortes frontales y que el colgador aparezca en el isométrico.
- Metrado (16 techos iguales): `herramientas/techo/metrado_banca_m.py` → `METRADO_CANALETA_Y_ACCESORIOS_BANCAS_CAR_MUJERES.xlsx`
  (canaleta 2.00 m, tapa 2, soporte 2, boquilla 1, codo 90° 2, colgador 1, abrazadera 1 por techo; sin tubo ni falsa columna).
- En la planilla general (`herramientas/mujeres/bancas_en_planilla_m.py`, entrada 09-10-2026): hoja nueva METRADO CANALETA BANCAS y
  subtítulo **1.4.4.5.4 RED DE RECOLECCION TECHO DE BANCAS DE JARDINERIA** después de ACCESORIOS: 1.4.4.5.4.1 CANALETA DE PLANCHA DE
  ALUZINC e=0.50mm, SECCION INTERIOR 0.18 m (ANCHO) x 0.20 m (ALTO) = **32.00 m**; .2 TAPA LATERAL = **32**; .3 SOPORTE = **32**;
  .4 BOQUILLA = **16**. PLANILLA +6 filas, RESUMEN +5 filas; los valores anteriores idénticos. Codos, colgador y abrazadera no se
  agregan (ya están en METRADO MONTANTES BC-01 a BC-16). Se agregó al RESUMEN el CODO DESAGÜE PVC Ø4" x 45° (1.4.4.5.3.2, 2 und) que
  faltaba; COLGADOR y ABRAZADERA pasan a 1.4.4.5.3.3 y .3.4. Salida
  `entregables_mujeres/METRADO_DRENAJE_PLUVIAL_CAR_MUJERES_09-10-2026_CON_BANCAS.xlsx`. Corregido de paso: fórmulas compartidas de Excel
  (`<f t="shared" .../>`) al desplazar filas en `Libro`.

### 10.2 Hogar de Refugio (CUI 2675514): OC-01 jardinera + banca + pérgola (22-10-2026)
- Insumo: `insumos/solange/oc01/OC-01_BANCA_CON_PERGOLA.dxf` (planta de techos, corte A-A, elevación E1).
- **9 bancas = 3 juegos OC-01**; cada juego tiene 3 techos a una agua de 2.40 de fondo: **T-1 3.79** (canaleta al norte, salida en el
  extremo izquierdo, x 0.147), **T-2 4.21** (central, canaleta al sur, salida a la izquierda, x 3.939), **T-3 3.79** (canaleta al norte,
  salida a la derecha, x 11.649).
- El "sumidero 4" tipo cúpula" del plano se reemplaza por **boquilla** de plancha (pedido del usuario; "borra esa cúpula").
- Canaleta de plancha **galvanizada e = 0.50 mm**, interior **0.18 x 0.21** (indicación del usuario), ala posterior 0.10, S = 0.5 %,
  fondo en la boquilla +2.55 (borde +2.76 bajo la cobertura; cobertura +2.855 en el borde bajo, 12.5 %); desarrollo 0.70 m/m
  (0.18 + 0.21 + 0.21 + 0.10).
- **2 sujetadores** (soportes de platina F°G° 1" x 1/8", desarrollo 0.70) por canaleta: a 0.80 de cada extremo en T-1 y T-3 y 0.85 en
  T-2 (`round(0.207·L/0.05)·0.05`); tapas en los dos extremos.
- Bajada (corte A-A): boquilla (brida 0.16 x 0.16, cuello Ø 0.10 x 0.15) → niple → codo 4" x 90° → tramo bajo la canaleta con colgador
  (eje +2.294) → codo → bajada a 0.0655 de la cara de la columna (0.10 x 0.25) con abrazadera (+1.80) → falsa columna CL-01 (+1.05 a −0.15).
- Hidráulica (memoria, cap. 9): Q < 0.6 L/s por techo, tirante y ≈ 0.012 m, D requerido 1.59" → se adopta Ø 4"; la sección la define la
  cobertura y la limpieza de hojas de la pérgola, no la capacidad.
- Láminas (`herramientas/techo/planos_oc01_refugio.py` → `entregables/PLANOS_DRENAJE_OC-01_BANCA_PERGOLA_HOGAR_REFUGIO.dxf`): DO-01 →
  **DPL-41** isométrico general 1/30 + planta de techos 1/50; DO-02 → **DPL-42** isométrico de la salida y corte de la canaleta 1/5.
- Metrado suelto: `herramientas/techo/metrado_oc01_refugio.py` → `METRADO_CANALETA_OC-01_BANCA_PERGOLA_HOGAR_REFUGIO.xlsx` (por juego:
  canaleta 11.79 m, 6 tapas, 6 sujetadores, 3 boquillas; N.° de juegos = 3 editable). Solo los 4 ítems pedidos (sin tubo, codos,
  colgador, abrazadera ni falsa columna).
- En la planilla (`herramientas/bancas_oc01_en_planilla_refugio.py`): hoja METRADO CANALETA BANCAS (N.° de juegos en F21), subtítulo
  **01.04.03.05.04 RED DE RECOLECCION TECHO DE BANCAS CON PERGOLA (OC-01)** (PLANILLA filas 165-169, RESUMEN filas 53-57):
  .01 CANALETA DE PLANCHA DE ACERO GALVANIZADO e=0.50mm, SECCIÓN 0.18m x 0.21m = **35.37 m** (3 x (3.79 + 4.21 + 3.79));
  .02 SOPORTE = **18**; .03 TAPA LATERAL = **18**; .04 BOQUILLA DE PLANCHA GALVANIZADA P/CONEXIÓN DE CANALETA A TUBERIA PVC Ø4" = **9**.
  Los 760 valores anteriores quedan iguales. El metrado vigente de la usuaria es
  `insumos/metrados_vigentes/METRADO_DRENAJE_MUJERES_VIOLENTADAS_CON_BANCAS_OC-01.xlsx` (sin la fila 8 de la hoja de bancas);
  `bancas_oc01_en_planilla_refugio.py` ya no lo pisa.
- Especificación propia (`espec.espec_bancas`): plancha ASTM A653 G90, remaches pop 1/8", sellador de poliuretano; trabajo a 2.80 m con
  escalera de tijera o andamio y arnés (G.050); prueba con agua; medición por metro (largo de cada techo x juegos).

---

## 11. Leyendas y especificaciones en DXF (bloques a escala real)
| Bloque | Generador | Contenido |
|---|---|---|
| LEYENDA_ESPEC_CUNETAS | `herramientas/leyenda_cunetas.py` (CAR Varones) | Simbología (abierta azul, tapada verde, longitudinal, transversal, junta, piso, lloradero, rótulo de acero, cotas), abreviaturas NCT/NCF, especificaciones de concreto, solado, acero, recubrimiento, traslape, encofrado, curado, juntas, rejilla, tapada, lloraderos, pendiente, relleno 95 % Proctor modificado, normas |
| ESPEC_FALSA_COLUMNA | `herramientas/espec_falsa_columna.py` (3 proyectos) | Reemplaza "Consideraciones" y "Detalle de falsa columna" del plano del proyectista |
| ESPEC_LLORADEROS / DETALLE_LLORADERO | `herramientas/espec_lloraderos.py` (Varones y Refugio) | Leyenda, detalle de sección cuneta–área verde (H = 0.50 dibujada), especificaciones y cantidades |
Alturas de letra a escala real: título 0.050, subtítulo 0.036, texto 0.028 m (llamadas de secciones del proyectista 0.031, títulos 0.038).
Se insertan en (0, 0); se copian junto a las secciones o se escalan con INSERT si la lámina tiene otra escala.

---

## 12. Láminas, archivos y regeneración

| Componente | Láminas | Generador | Salida |
|---|---|---|---|
| Red de techo (canaleta, soporte, tapa, boquilla, unión, abrazadera, colgador, montante, falsa columna, dado) | DR-01 (1/5), DR-02 (1/10), DR-03 isométrico tramo 1/5, DR-04 isométrico montante 1/15, DR-05 fijaciones 1/1, DR-06 detalles 3D 1/5 | `herramientas/techo/planos_techo.py [varones refugio mujeres]` | `entregables*/PLANOS_DETALLE_RED_TECHO_*.dxf` |
| Sumidero | DS-01, DS-02 | `herramientas/techo/planos_sumidero.py` | `PLANOS_DETALLE_SUMIDERO_PISO_*.dxf` |
| Lloraderos | DL-00, DL-01, DL-02 (Varones DPLV-43/34/35; Refugio DPL-40/37/38) | `planos_ubicacion_lloraderos.py`, `techo/planos_lloraderos.py` | `PLANO_DL-00_*`, `PLANOS_DETALLE_LLORADEROS_*` |
| Junta y rejilla de cunetas | DJ-01, DJ-02, DJ-03 (Varones DJ-01 → DPLV-31) | `planos_junta_cunetas.py`, `planos_junta_cunetas_iso.py`, `varones/planos_junta_cunetas_v.py` | `PLANOS_DETALLE_CUNETAS_JUNTA_Y_REJILLA_*` |
| Tapa ciega | DP-06B rev. 02, DP-06D, DD-01, DD-02 | `render_tapa/dxf_tapa_ciega.py`, `render_tapa/dxf_tapa_3d.py` | `PLANO_DP-06B_*`, `PLANO_DP-06D_*` |
| Banca CAR Mujeres | DB-01 a DB-03 | `techo/planos_banca_m.py` | `PLANOS_ISOMETRICO_BANCA_JARDINERIA_CAR_MUJERES.dxf` |
| OC-01 Refugio | DPL-41, DPL-42 | `techo/planos_oc01_refugio.py` | `PLANOS_DRENAJE_OC-01_BANCA_PERGOLA_HOGAR_REFUGIO.dxf` |
| Falsa columna (espec.) | DPL-39 (Refugio) | `espec_falsa_columna.py` | `ESPECIFICACIONES_FALSA_COLUMNA_MONTANTE_*.dxf` |

Motor 3D común: `herramientas/techo/iso3d.py` (caras planas, orden por profundidad x + y + z, sombreado por la normal, aristas solo en
bordes reales; observador desde +x, +y, +z). Los cuadros de metrado de las láminas leen los valores guardados de la planilla vigente
(nunca se recalculan aparte). Todo cambio se hace en el generador y se regenera.

Edición de planillas sin perder formato: `angulo_contramarco_refugio.Libro` (XML: `leer`, `poner`, `texto`, `num`, `formula`,
`cambiar`, `sid`) + `recalcular()` con LibreOffice; hojas nuevas con los estilos de las existentes (`acu_juntas_refugio.Hoja`,
`bancas_en_planilla_m.agregar_hoja_despues`); comprobar antes y después que ningún otro valor cambió.

---

## 13. Diferencias detectadas que conviene resolver (no se cambiaron sin pedido)
1. Sección de canaleta principal: metrado/partida 0.25 x 0.20 vs láminas DR (indicación del 10-10) 0.20 x 0.25; remaches 26 vs 28 por
   unión; desarrollo del soporte 0.85 vs 0.90.
2. Abrazaderas: especificación @1.50 m vs metrado del usuario MAX(1; REDONDEAR.MENOS(L/4)).
3. Recubrimiento de la falsa columna: 2 cm (bloque de especificación) vs 0.04 m (especificación de la partida).
4. Junta de cunetas: CAR (REDONDEAR.MAS(L/3), 2H + 0.40) vs Barranquita (ENTERO(L/3), 2(h + 0.10) + 0.60); CAR Mujeres aún con
   N x 2 x H (congelado).
5. Tapas de inspección del Hogar de Refugio: 17 en el valor vs nota "10 tapas" en PARAMETROS D4; Varones 18 "provisional".
6. CAR Mujeres: partida de tapa con marco y contramarco vs plano D-RL con tapa ciega.
7. Leyenda de cunetas cita OS.060; las memorias usan CE.040 (R.M. 126-2021-VIVIENDA), que la reemplaza.
8. Precios pendientes de cotizar en Tarapoto: piedra chancada 1/2", grava 20-40 mm, alquiler de soldadora; platina F°G° 1" x 1/8"
   referencial.

---

## 14. Para implementarlo en un programa

### 14.1 Parámetros por componente (valores por defecto; todos editables)
```
CANALETA_TECHO   = {b: 0.25, h: 0.20, pestana: 0.05, e_mm: 0.9, material: "acero galvanizado ASTM A653",
                    S: 0.010, n: 0.013, tramo_plancha: 2.44, traslape: 0.05, sep_soporte: 0.60,
                    tapas_por_canaleta: 2, remache_paso: 0.05, filas_remache: 2}
SOPORTE          = {platina: "F°G° 1 x 1/8 pulg", kg_m: 0.633, oreja: 0.10, pernos: 2 (1/4 x 2 1/2), tornillos: 2 (1/4 x 3/4)}
BOQUILLA         = {abertura: 0.10, brida: 0.20 (bancas 0.16), cuello: (0.10, 0.15), remaches: 8}
TAPA_LATERAL     = {pestana: 0.03, remaches: 6}
MONTANTE         = {D_pulg: 4, D_ext: 0.114, rs: 0.25, codos_90: 3, colgadores: 2 (uno por codo del desvio),
                    abrazadera_sep_max: 1.50, abrazaderas_metrado: "max(1, floor(L/4))"}
FALSA_COLUMNA    = {a: 0.20, b: 0.15, h: 1.30, fc: 175, long: (4, 3/8, 1.20), estribos: (9, 3/8, 0.58, @0.15)}
DADO             = {a: 0.40, b: 0.40, h: 0.35, fc: 140}
SUMIDERO         = {rejilla: 0.25, platina: "1 x 3/16", n_platinas_int: 9, paso: 0.025, marco: "L 1x1x3/16",
                    anclajes: (8, 3/8, 0.075), caja_ext: 0.45, prof: 0.10, salida: "PVC 4 + 1 codo 90 (sin trampa)", S_tubo: 0.01}
CUNETA           = {b_int: 0.40, e_muro: 0.10, e_fondo: 0.10, e_tapa: 0.10, b_ext: 0.60, solado: 0.10, fc: 175, S: 0.005,
                    n: 0.015, H_acero: 0.40, regla_acero: "H > 0.40 (CAR) / h >= 0.40 (terreno) o tapada",
                    altura_libre_min_tapada: 0.25, rebaje_rejilla: (0.05, 0.0254)}
REJILLA          = {modulo: 1.00, holgura_modulos: 0.003, holgura_lado: 0.0015, ancho: b_int + 2*0.05 - 2*0.0015,
                    platina: "1 x 3/16 de canto", paso: 0.0254, n_platinas: round(1.00/0.0254)=39, kg_platina_m: 0.95,
                    angulo: "L 1x1x3/16", kg_angulo_m: 1.73, kg_m: 20.0}
TAPA_INSPECCION  = {lado: 0.60, e: 0.10, fc: 210, parrilla: (3/8, 0.15), rec: 0.025, sep_max: 10.0}
JUNTA_CUNETA     = {sep: 3.00, e: 0.0254, sello: (0.0254, 0.0508), relleno: "tecnopor 1", sellador: "RC-250 + arena",
                    seccion: "U completa (2 muros + fondo)"}
LLORADERO        = {D_pulg: 3, L_tubo: 0.30, L_perforado: 0.20, perf: (2 filas, 4 por fila, @0.05, 3/8), S: 0.005,
                    filtro: 0.30, grava: "20-40 mm", desp_grava: 0.10, geotextil: "no tejido clase 2", traslape_geo: 0.10,
                    mortero: 0.0005, sep: 1.50, franja_area_verde: 0.30, L_min_tramo: 1.50, dist_min_junta: 0.30}
TAPA_CIEGA       = {lado: 0.68, e: 0.08, fc: 210, parrilla: (3/8, 0.10, 7+7, L 0.62), asas: (2, 1/2 liso, 0.50),
                    cajuela: (0.19, 0.06, 0.03), bisel: 0.01, rebaje: 0.70, holgura: 0.01, luz: 0.60,
                    borde_engrosado: (0.15, 0.10, anillo 0.60-0.90), refuerzo_borde: (8, 1/2, 1.40), peso: 89 kg}
BANCA            = {canaleta: (0.18, 0.20 o 0.21), e_mm: 0.50, material: "aluzinc (CAR Mujeres) / galvanizado (OC-01)",
                    S: 0.005, tramos: 1 por techo, soportes: 2, tapas: 2, boquillas: 1}
```

### 14.2 Reglas de ubicación
1. Canaleta: una por cada borde bajo de techo (dos aguas → dos canaletas; una agua → una). Longitud = largo del borde del techo.
2. Boquilla y montante: en el punto bajo de la canaleta; número de montantes por lado según el plano (la hoja vincula boquillas =
   montantes). Bajada adosada a muro o columna; desvío bajo el alero con colgador junto a cada codo.
3. Falsa columna + dado: al pie de cada montante de edificación; el codo de salida queda dentro del dado; salida PVC 4" a la cuneta.
4. Sumidero: punto bajo de cada paño de piso; tubería 4" con S ≥ 1 % hasta el muro de la cuneta, descarga sobre su fondo; un codo 90°.
5. Cuneta tapada: donde cruza veredas, ingresos o pasadizos; abierta con rejilla en lo demás.
6. Tapas de inspección: inicio y fin de cada tramo tapado, en cada empalme dentro del tapado, separación ≤ 10 m.
7. Juntas de cuneta: cada 3.00 m y en cada cambio de dirección, en toda la U.
8. Lloraderos: solo en el muro cuya franja exterior de 0.30 m interseca el polígono de área verde; tramos ≥ 1.50 m; cada lado por
   separado; a media altura; ≥ 0.30 m de las juntas; repartidos @1.50.
9. Registros del colector con tapa ciega: fuera de cruces vehiculares; sobre cada llegada de cuneta.

### 14.3 Cálculo de cantidades (fórmulas)
```
# canaletas (por canaleta de largo L)
soportes   = ceil(L / 0.60) + 1                     # bancas: 2 fijos
tapas      = 2
boquillas  = n_montantes_del_lado
plancha_m2 = L * (b + 2h + 2*pestana) * (1 + traslape/2.44) * 1.05
remaches   = L * 2*(b + 2h)/0.05/2.44 + 6*tapas + 8*boquillas
# montantes
L_tubo = suma(longitud_montante); codos90 = 3*n; colgadores = 2*n (edif.); abrazaderas = max(1, floor(L_mont/4))
# falsa columna (n und)
conc = n*0.20*0.15*1.30; enc = n*(2*1.30*0.15 + 1.30*0.20); acero = n*(4*1.20 + 9*0.58)*0.56; dado = n*0.40*0.40*0.35
# rejilla
L_rejilla = suma(L_tramo - descuento) solo tramos abiertos; kg = 20.0 * L_rejilla
# tapas de inspeccion (N)
conc = N*0.6*0.6*0.10; enc = N*(2*(0.6+0.6)*0.10 + 0.36); acero = 2*N*0.55*(round(0.55/0.15)+1)*0.56
# juntas de cuneta (por eje)
H_med = area_muro / L_eje; N_j = ceil(L_eje/3.00); L_junta = N_j*(2*H_med + 0.40)
# lloraderos (por tramo)
N = ceil(L_tramo/1.50); tubo = 0.30*N; perf = 8*N; grava = 0.0297*N; geo = 0.594*N; mortero = 0.0005*N; excav = 0.027*N
# tapa ciega (por registro)
conc = 0.68^2*0.08; enc = 4*0.68*0.08; parrilla = 14*0.62*0.56; asas = 2*0.50*0.994; borde = 8*1.40*0.994
descuento_losa = 0.49*0.08 + 0.36*(e_losa - 0.08)
borde_engrosado_m = 4*0.75  (si b > 0.60)  o  2*b  (si b <= 0.60)
# sumidero (por und)
platina = 4*0.25 + 9*(0.25 - 2*0.0048); angulo = 4*(0.254 + 0.0048); anclajes = 8*0.075
# hidraulica
Q = C*I*A*FS  (C 0.88, I 210.98 mm/h, FS 1.15); canaleta: Manning rectangular; montante: D = (Q/(1.754*rs^(5/3)))^(3/8)
```

### 14.4 Validaciones obligatorias
- Canaleta: tirante + 0.05 ≤ alto; S ≥ 0.5 % y sin contrapendiente; soportes ≥ 2; boquillas ≥ 1 por canaleta.
- Montante: D requerido ≤ 4" (Q ≤ 7.0 L/s por montante con rs 0.25); si no, más montantes.
- Sumidero: S tubo ≥ 1 %; salida por encima del fondo de la cuneta; sin trampa.
- Cuneta: sección mínima (tapada: altura libre ≥ 0.25); acero según la regla H/h y tapado; tapa 0.56 @0.25.
- Juntas: separación ≤ 3.00; criterio de sección en U declarado (no mezclar métodos dentro de un proyecto).
- Lloraderos: solo tramos con área verde; N entero; distancia a juntas ≥ 0.30; total de la hoja = RESUMEN ("CONFORME").
- Tapa ciega: b del colector vs luz 0.60 decide el apoyo (cabeza de muro o borde engrosado en 4 lados); tapa fuera de cruces de
  camiones (si no, verificar HL-93); peso ≤ ~90 kg (2 operarios).
- Coherencia: cada cambio se propaga a metrado ↔ ACU ↔ desagregado ↔ láminas ↔ especificaciones ↔ memoria; comparar la planilla antes y
  después (ningún valor ajeno debe cambiar); los cuadros de las láminas leen la planilla vigente.
- Precios con fuente visible; mano de obra de la tabla CAPECO-FTCCP del año; sin nombres ni CIP de proyectistas; nada que delate IA.
- Planos: escala real, sin patrones de achurado en bloques escalables, colores visibles en fondo blanco (no amarillo), letra grande,
  llamadas sin cruces (skill `planos-ordenados`).
