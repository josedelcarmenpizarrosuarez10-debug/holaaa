---
name: colector-pluvial-frontal
description: "Diseñar y verificar un colector pluvial frontal cubierto (canal rectangular de concreto armado cuya losa superior es la vereda) que recoge las cunetas de piso de un predio de cualquier tipo de local y región, y empalma con colectores vecinos o con el receptor: trazo, cotas de fondo, caudal, tirante normal y crítico, perfil por paso estándar, autolimpieza, llegada de cunetas, caja de llegada y caja de caída con poza, registros con tapa ciega, juntas, estructura por zonas de carga, metrado y memoria. Usar cuando el usuario pida un colector frontal o canal cubierto nuevo, revisar uno existente, empalmar tramos de varios proyectos (cadena hidráulica) o cambiar registros, tapas, juntas o cajas."
---

# Colector pluvial frontal cubierto

Método general del usuario para cualquier predio (colegio, CAR, hogar, posta, municipalidad, mercado…) con frente a una vía.
Se aplicó y aprobó en una cadena de tres expedientes contiguos que aparece **solo como ejemplo** al final. Detalle (tablas por
tramo, fórmulas, cronología) en `referencias/03_colector_frontal.md`; sus rutas y números son del trabajo original y no se copian.
La lluvia y los caudales se calculan con `hidrologia-drenaje-pluvial`; el metrado en planilla, con `metrado-drenaje-delphin`.

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

## 1. Datos que hay que pedir (no inventar; no preguntar lo que ya muestra el plano)
1. Proyecto: nombre completo, CUI, entidad, tipo de local, ubicación. Proyecto aguas arriba ("aporte externo") y aguas abajo
   ("receptor": colector vecino, canal, cuneta vial, quebrada) con nombre y CUI si los tienen.
2. Planta general en DXF: línea del frente (cerco o línea de referencia), si hay cerco o no, lindero con la vía, vanos de acceso
   (camiones, autos, motos: coordenadas de postes), cunetas que llegan (eje, NCF, NCT, sección, abierta o tapada). Zona UTM.
3. Niveles: NPT del frente por tramo (la losa superior es la vereda), cota de fondo y nivel de agua (NA) del receptor, alto interior
   del receptor, cota de fondo y ancho del aporte externo en su llegada, terreno a lo largo del eje.
4. Hidrología del propio proyecto: P24 o P10/P20, Σ C·A del predio; caudal del aporte externo (dato de su memoria, sin validarlo).
5. Metrado vigente del usuario (planilla Delphin), estudio de mecánica de suelos (EMS) y tipo de tránsito en cada acceso.
6. Prefijo de numeración de registros y de láminas; criterios por defecto a confirmar (§2).
Si falta algo, plantear la hipótesis más conservadora, dejarla escrita como "hipótesis cubierta" y avisarla.

## 2. Concepción y criterios (por defecto del usuario; confirmar en cada proyecto)
- Marco cerrado monolítico de concreto armado f'c 210 kg/cm² (losa de fondo + 2 muros + losa superior), fy 4200, sobre solado
  e = 0.05 f'c 100 (al ancho exterior). Losa superior al ras del NPT con acabado frotachado: funciona como vereda.
- Cubierto en todo el recorrido (seguridad de los usuarios del local: niños, estudiantes, pacientes, público). Sin lloraderos.
- Todo dentro del lindero del predio; nada en la faja de la vía. Limpieza por registros con tapa removible.
- Régimen subcrítico; llenado y/h ≤ 0.85 (o 0.80 si se aplica CE.040 17.6.2, ver §16); borde libre BL ≥ 0.05 m bajo la losa;
  Froude F < 1 (F = 1 solo en el borde de caída).
- V 0.90 a 3.0 m/s con el caudal de diseño (CE.040, R.M. N.° 126-2021-VIVIENDA, que reemplaza a la OS.060); τ = γ·R·S ≥ 0.15 kg/m²
  con caudales parciales hasta el 5 %. Manning n = 0.015 (concreto vaciado in situ).
- Acero según la carga de cada zona, **sin sobredimensionar** (el usuario pide ahorrar acero).
- El ancho crece aguas abajo cuando varios colectores se encadenan; cada empalme con su caja de llegada o de caída.

## 3. Trazo en planta
- Eje paralelo al frente a d = junta 0.025 + e_muro + b/2 desde la cara del cerco (o desde la línea del frente si no hay cerco),
  hacia el predio. Contra el cimiento del cerco va junta de tecnopor 1".
- Progresivas 0+000.00 desde el extremo aguas arriba, crecientes aguas abajo.
- Llegada al receptor con quiebres a 45° (cada quiebre lleva registro) y un tramo final recto si hace falta.
- Zonas de carga en progresivas: p1 = inicio del vano − holgura, p2 = fin del vano + holgura (camiones 0.30; motos 0.115).
  Tipos NORMAL (peatonal), MOTOS, AUTOS, CAMION; cada zona define espesores y armado.
- UTM (WGS 84, zona del proyecto) por traslación y giro con un punto común del vecino (p. ej. un registro del receptor y el azimut
  de su lindero); rotular "ubicación referencial, verificar en campo" si no hay coordenadas del cerco.

## 4. Cotas y predimensionamiento (qué fija cada dimensión)
- Losa superior = NPT del frente (no se elige). Techo interior = NPT − e_losa(zona). h = techo − cota de fondo (h puede ser
  bastante mayor que el tirante).
- Cota de fondo inicial: la más alta que permita (a) caída libre de la cuneta más baja que llega y (b) llegada del aporte externo con
  caída ≥ 0.10 m sobre el NA.
- Cota de fondo final ≥ cota de fondo del receptor. S = la que cabe entre ambas con régimen subcrítico y autolimpieza.
- b: empezar en 0.60 (mínimo práctico para limpieza manual) y subir de 0.10 en 0.10 hasta cumplir llenado, BL y F en todas las estaciones.
- Espesores: 0.15 en muros de hasta ~1.65 m de alto; 0.10 si h ≤ 0.67 (verificar con §13).

## 5. Caudal del colector
- tc del colector = 10 min (entrada) + recorrido en cunetas + recorrido en el colector (L/V; en los ejemplos ≈ 15 min). La I sale
  de la lluvia del propio proyecto para ese tc (las cunetas, canaletas y montantes usan la I de 10 min: misma lluvia, otra duración).
- Q [L/s] = Σ(C·A) · I · FS / 3600 (A en m², I en mm/h), FS = 1.15, C ponderado del predio medido en su plano.
- Aporte externo = dato de la memoria del vecino. Suma de picos sin desfase + FS 1.15 = hipótesis conservadora declarada.
- Reparto entre cunetas: por franja de frente que drena cada una (límites en los puntos medios entre ejes; una cuneta absorbe el
  redondeo) o en partes iguales. Q acumulado por progresiva (escalón en cada cuneta; seco antes de la primera).

## 6. Hidráulica y perfil de flujo
- Manning: Q = (1/n)·A·R^(2/3)·S^(1/2); A = b·y; R = b·y/(b + 2y). Tirante normal por bisección en [1e-4, 5] o por punto fijo
  y(k+1) = (Q·n·(b + 2y(k))^(2/3) / (b^(5/3)·S^(1/2)))^(3/5) (8 iteraciones en Excel). yc = (Q²/(g·b²))^(1/3), g = 9.81. F = V/√(g·y).
- Control aguas abajo: caída libre a una caja con NA más bajo → yc en el borde; vertido sobre un control externo → NA = cresta + H con
  H = (Q/(Cw·Lw))^(2/3), Cw = 1.70 (cresta ancha); entrega ahogada → NA del receptor. Tomar el mayor.
- Paso estándar de aguas abajo (2) hacia aguas arriba (1): z1 + y1 + V1²/2g = z2 + y2 + V2²/2g + Δx·(Sf1 + Sf2)/2, Sf = (n·V/R^(2/3))².
  Resolver y1 por bisección en [1.001·yc, 3.0] (rama subcrítica), 100 iteraciones (30 en columnas de Excel, sin macros).
- Estaciones cada 1.00 m + quiebres, empalmes, registros, límites de zona y fin. En cada una: NA, h, llenado, BL, V, F, zona, CUMPLE.
- Capacidad con llenado 85 % en la h mínima: Q85 = (1/n)·b·0.85h·R^(2/3)·√S, como margen respecto del Q de diseño.

## 7. Autolimpieza
Tabla en flujo uniforme con el caudal de diseño, cada aporte por separado y 50, 25, 10 y 5 %: yn, V, τ = 1000·R·S (kg/m²), F.
Cumple si V ≥ 0.90 con el Q de diseño y τ ≥ 0.15 en los parciales. En cabeceras con poco caudal (b mínimo) se acepta V < 0.90 si
τ ≥ 0.15 con el caudal del tramo y hay registros cada ≤ 12 m (escribirlo en la memoria). Si no cumple: subir S, reducir b o caja de caída.

## 8. Llegada de las cunetas
- Ventana del ancho libre de la cuneta × Hv en el muro lado predio (Hv = techo − NCF en el muro), con cajón de madera, sin dintel.
  Refuerzo: 4 barras 3/8" verticales L = Hv + 0.60 y 2 horizontales de 1.00; los marcos se cortan con gancho de 0.10.
- Caída libre al fondo; fondo pulido 1:3 e = 1 cm en 1.00 m bajo la caída; junta de tecnopor 1" con sellador; registro encima.
- Verificar NCF en el muro − NA del colector > 0 ("CAIDA LIBRE"; si no, "AHOGADA" y la cuneta remansa).
- Tuberías que entregan directo (montante o sumidero): el fondo del tubo llega sobre el NA del colector + 0.05 m.
- Si el colector recibe una red de cunetas sobre terreno, en la verificación de cada descarga su cota de fondo y su NA reemplazan
  al terreno exterior: la cuneta no puede quedar "enterrada" respecto del colector.
- Si la cuneta no llega al muro se prolonga con su sección y pendiente (NCF muro = NCF − S·prolongación); si invade la franja se
  acorta hasta la cara del muro. **Prolongación y acortamiento se metran en las partidas de cunetas, no en el colector.**

## 9. Caja de llegada CL (recibe un colector vecino)
- Interior según lo que llega (ancho ≥ el del colector que llega + holgura para limpieza), muros 0.15; piso de poza = cota de fondo
  inicial − 0.30; tapa al piso del vecino si está más alto (escalón con murete). Ventanas con el ancho de lo que llega y alto hasta el techo.
- Verificar: caída libre del aporte ≥ 0.10 m sobre el NA de la caja; colchón NA − piso ≥ 0.50 m. Malla 3/8" @0.20 en ambas caras
  (+10 %). La junta entre estructuras de distinto expediente la metra el que llega.

## 10. Caja de caída CC con poza (entrega a un receptor más bajo)
1. Brink: yc en el ancho del colector; NA = CF + yc. 2. Piso de poza = CF del receptor − 0.40. 3. E1 = caída + 1.5·yc (sin pérdidas).
4. y1 por energía y1 + (Q/(b·y1))²/2g = E1 (rama supercrítica, bisección en [1e-3, yc]); V1; F1 = V1/√(g·y1).
5. y2 = y1/2·(√(1 + 8F1²) − 1) en el ancho del colector (conservador). 6. Exigir y2 ≤ NA del receptor − piso (resalto ahogado).
7. L poza ≥ 0.8 × 6·y2 (USBR). 8. Umbral con corona = CF del receptor. 9. Ventana de salida = ancho del receptor × su alto interior.

## 11. Registros y tapa ciega
- Uno sobre **cada** llegada de cuneta (exactamente encima), uno en cada quiebre; tramos > 12 m se dividen en n = ceil(L/12) partes
  iguales. **Nunca dentro de un cruce** (ni su rebaje): correrlo fuera del vano + holgura. Numerar con el prefijo del proyecto.
- Tapa ciega de concreto armado (diseño por defecto del usuario; verificar con la carga): 0.68 × 0.68 × 0.08 f'c 210 vaciada aparte;
  parrilla 3/8" @0.10 (7 + 7 barras de 0.62); 2 asas de fierro liso 1/2" (desarrollo 0.50) en cajuelas 0.19 × 0.06 × 0.03 a ±0.20;
  cantos biselados 1 × 1 cm; ≈ 89 kg (2 operarios). Asiento en rebaje 0.70 × 0.70 × 0.08, holgura 0.01, luz libre 0.60 × 0.60; borde
  engrosado 0.15 × 0.10 bajo la losa (perímetro medio 3.00 m) con 8 Ø 1/2" L = 1.40. **Sin marco, contramarco, soldadura ni pintura.**
- Si b ≤ 0.60 (menor que el rebaje): el rebaje apoya en la cabeza de los muros y el borde engrosado va solo en los 2 lados
  transversales (2 × b por registro), no en 4.
- Por registro: tapa 0.0370 m³; encofrado 0.2176 m²; parrilla 4.86 kg; asas 0.99 kg; borde 11.13 kg; descuento de losa
  0.49 × 0.08 + 0.36 × (e_losa − 0.08). La tapa se verifica con rueda de 1 t; si cae en paso de camiones, verificar HL-93.

## 12. Juntas
- Dilatación transversal cada 4.00 m en toda la sección: anillo de tecnopor 1" + sellador asfáltico 1" × 2" (RC-250 + arena gruesa)
  en caras interiores y superior (EG-2013 MTC, Sección 510). N = ENTERO(L/4); longitud = N × [2·b_ext + 2(e_fondo + h_máx + e_losa)].
  Acero longitudinal cortado a 0.05 de cada lado.
- Longitudinal (tecnopor 1" + sellador) **solo** donde el muro toca el cimiento del cerco u otra estructura; **nunca contra terreno
  natural**. Toda junta entre estructuras de distinto expediente lleva tecnopor + sellador.

## 13. Estructura (E.020, E.060, AASHTO LRFD / Manual de Puentes MTC, E.050)
Parámetros por defecto (reemplazar por los del EMS): γc 2.4, γs 1.8 t/m³, Ko 0.5, s/c peatonal 0.5 t/m², lateral liviano 1.0 y camión
2.7 t/m², rueda liviana/moto 1.0 t, rueda HL-93 7.26 t, IM 0.33, huella c 0.25, Lc = b + e_muro, franja E = 0.66 + 0.55·Lc;
U = 1.4D + 1.7L; φ 0.90 flexión, 0.85 cortante.
- A Losa normal: Mu = (1.4γc·e + 1.7·sp)·Lc²/8; d = e/2 (marco único). B Losa motos y C losa camiones: Mr = P(1+IM)(Lc/4 − c/8)/E;
  en C además Vu ≤ φVc = 0.85·0.53·√f'c·100·d/1000. D/E/F Muros: p = Ko·γs·H, q = Ko·s/c, M = pH²/20 + qH²/12, Mu = 1.7M.
  G Losa de fondo: Mu = 1.5·q·Lc²/8 y presión al suelo frente al EMS (sin EMS: comparar con 0.50 kg/cm² y escribir "VERIFICAR EMS").
  H Tapa: L 0.64, d = 5.5 − 0.48 cm, As 3/8" @0.10. Siempre Mu ≤ φMn, Vu ≤ φVc, As ≥ 0.0018·b·e.
- Armados de partida (verificar en cada proyecto): NORMAL un marco 3/8" @0.20 en el eje + longitudinales 3/8" @0.25 (una capa: E.060
  14.3.4 la permite en e ≤ 0.20), ganchos 0.30; MOTOS/AUTOS 3/8" @0.15; CAMION losa 0.25 y doble marco 1/2" @0.15, longitudinales
  @0.20. Traslapes 0.40 (3/8") y 0.50 (1/2"); barra 9.00 m.
- Si un elemento no cumple: pasar a @0.15, luego doble marco 1/2" o subir espesor. Curado 7 días; sin tránsito 14; camiones 28.

## 14. Metrado del colector (resumen; formato en `metrado-drenaje-delphin`)
Partida independiente "COLECTOR PLUVIAL FRONTAL (TRAMO …)" con subtítulo propio; no tocar ni mezclar las partidas de cunetas.
Por tramo homogéneo (≤ 2 m o por zona, h y Hz ponderados): zanja = b_ext + 2 × 0.25; excavación = zanja × Hz × L; refine y solado =
(b_ext + 0.10) × L; relleno = 2 × 0.25 × Hz × L + 1.00 × (NPT − terreno) × L; eliminación = (exc − rell) × 1.20; concreto = fondo +
muros + losa − descuentos + borde engrosado (**una sola partida**); encofrado = 2h·L + 2(e_f + h + e_l)·L + b·L; frotachado = b_ext × L;
curado = (2h + b + b_ext) × L; acero: marcos = REDONDEAR.MAS(L/s) × perímetro (marco único 2(b_ext − e) + 2(e_f/2 + h + e_l/2) + 0.30),
longitudinales = n × L × (1 + 0.40/9.00); tapa de registro por und; dos partidas de junta (dilatación y longitudinal/contacto).

## 15. Entregables
- Excel de memoria de cálculo con fórmulas visibles: MEMORIA, DATOS (parámetro, valor, und, fuente, símbolo), CAUDALES, CUNETAS,
  EMPALME (CC y CL), PERFIL_FLUJO, ESTRUCTURAL (A–H), CUMPLIMIENTO (requisito, norma, criterio, valor, resultado) y bloque "Datos de
  otros expedientes y cómo quedan cubiertos". Azul = dato, negro = fórmula, verde = vínculo.
- Capítulo del colector en Word **al final** de la memoria hidrológica del usuario, sin alterar lo anterior: alcance, trazo, caudal
  (I de cunetas frente a I del colector, explicado), sección, perfil, autolimpieza, cajas, cunetas, estructura, normativa, criterios
  constructivos, resumen de metrados, cumplimiento, datos de otros expedientes, conclusiones.
- Planos DXF a escala real con presentación (planta 1/200, perfil, secciones por zona con acero, registro y tapa, empalme, cajas,
  juntas, isométricos) + PNG; metrado en la planilla; especificaciones por partida. PDF solo si se pide.

## 16. Lista de verificación final
- [ ] Todos los datos (NPT, cotas, lluvia, C, vanos, receptor) del propio proyecto o de las memorias vecinas citadas.
- [ ] Llenado dentro del criterio, BL ≥ 0.05 y F < 1 en todas las estaciones (salvo el borde de caída); V 0.90–3.0; τ ≥ 0.15 con el 5 %.
- [ ] Cada cuneta con caída libre > 0; aporte externo ≥ 0.10 sobre el NA de la CL; colchón ≥ 0.50.
- [ ] CF de entrega ≥ CF del receptor; Q entregado ≤ Q previsto por el receptor; resalto ahogado; poza ≥ 0.8 × 6y2; ventana ≤ alto del receptor.
- [ ] Registros ≤ 12 m, sobre cada empalme y quiebre, ninguno en un cruce; borde engrosado en 2 lados si b ≤ 0.60.
- [ ] Juntas cada 4 m; junta longitudinal solo contra cerco o estructura.
- [ ] φMn ≥ Mu, φVc ≥ Vu, As ≥ As mín en A–H; una capa solo con e ≤ 0.20; presión al suelo ≤ EMS o "VERIFICAR EMS".
- [ ] Cotas, NA, caudales, ventanas y coordenadas iguales en los expedientes vecinos (cuadro de empalme).
- [ ] Metrado = cálculo (tolerancia 0.05) y ningún valor previo del usuario cambió; prolongaciones de cunetas fuera del colector.
- [ ] Llenado: los colectores ya aprobados usan y/h ≤ 0.85; la CE.040, 17.6.2 limita a 80 % el tirante en conductos cerrados. En uno
      nuevo cumplir el más exigente o consultarlo; en los aprobados no se cambia nada sin pedido: solo se avisa.
- [ ] Recubrimiento contra el suelo: E.060, 7.7.1 a) pide 75 mm para concreto vaciado contra el suelo; con solado se ha usado 0.04.
      Declarar qué caso aplica.
- [ ] Cada dato con su fuente; nombre, CUI, ubicación, tipo de local y entidad del propio expediente, sin textos de otro proyecto.

## 17. Errores que el usuario ya corrigió (lecciones generales)
- Losa vehicular en todo el frente: no; armado por zona según el tránsito real de cada vano.
- NPT tomado de un rótulo erróneo o de otro plano: confirmar el nivel del frente con el usuario.
- Suponer cerco donde no hay: sin cerco no hay junta longitudinal.
- Tapas corridas respecto de la entrega de cada cuneta: van exactamente encima del empalme.
- Partidas de empalme o prolongación de cunetas dentro del colector ("ya metré mis cunetas, tú solo haces el colector").
- Doble capa de acero sin necesidad: sobredimensionado; marco único donde cumple.
- Usar la I de 10 min en el colector: va con su propio tc.
- Junta longitudinal a ambos lados o contra el piso: solo contra el cerco o estructura; tecnopor + sellador asfáltico, no elastomérico.
- Ventana de salida de la CC más alta que el receptor: es el alto interior del receptor.
- Borde engrosado de 4 lados en un colector angosto: va en 2 lados.
- Dejar un detalle pendiente porque "el modelo supone otro ancho" ("tú diseñaste todo, todo debe cuadrar").
- Confundir el ancho de zanja con el ancho del colector.
- Memoria con textos de otro proyecto (nombre, CUI, tipo de local): revisar todo el documento.
- Proponer costos cuando se pide diseño o metrado: el usuario llega hasta los metrados; el presupuesto lo hace el ingeniero en Delphin.
- Planos: amarillo sobre fondo blanco, 3D negros, cotas que no miden lo que dicen, acero fuera de su losa, barras sin su diámetro
  real (3/8" = 9.5 mm), huecos en secciones, textos encimados o verticales.

## Ejemplo de referencia (solo ilustrativo; reemplazar por los datos del proyecto nuevo)
Cadena del predio Los Mangos, Morales (San Martín): CAR Varones (CUI 2705619) → caja de llegada CL → Hogar de Refugio Temporal
"Mujeres Violentadas" (CUI 2675514) → caja de caída CC con poza → R-01 del CAR Mujeres (CUI 2717013) → salida a la berma.
| Dato | CAR Varones | Hogar de Refugio | CAR Mujeres |
|---|---|---|---|
| b / muros / fondo / losa sup. | 0.60 / 0.15 / 0.15 / 0.10 | 0.80 / 0.15 / 0.15 / 0.10 | 1.50 / 0.10 / 0.10 / 0.10 |
| Longitud / S | 105.29 m / 0.30 % | 69.89 m / 0.30 % | 139.08 m / 0.302 % |
| Cota de fondo inicio → fin | 260.20 → 259.884 | 259.10 → 258.890 | 258.72 → 258.30 |
| Q de diseño (I15 155.66 mm/h) | 221.7 L/s + 37.0 directo a la CL | 560.6 L/s | 626.2 → 822.9 L/s |
| Control aguas abajo | caída libre a la CL | caída libre a la poza CC | vertedero sobre la cresta de la vía |
| Registros / juntas | 11 / 26 | 10 / 17 | 15 / 33 |
| Resultados | yn 0.343, llenado máx. 0.341 | yn 0.518, yc 0.369, F 0.60, llenado 0.372 | llenado máx. 0.815 (gobierna b) |
CC del Refugio: caída 0.570, E1 1.123, y1 0.161, F1 3.45, y2 0.711 ≤ 0.742, poza 3.50 ≥ 3.41, ventana 1.50 × 0.43.

## Referencias
- `referencias/03_colector_frontal.md`: capítulo completo del ejemplo (tramos, cunetas y registros, hidráulica, cajas, estructura,
  metrado, coordinación entre expedientes, cronología y validaciones). Leerlo antes de diseñar o revisar.
