---
name: colector-pluvial-frontal
description: Diseñar y verificar un colector pluvial frontal cubierto (canal rectangular de concreto armado cuya losa superior es la vereda) que recoge las cunetas de piso de un predio y empalma con los colectores vecinos (trazo, cotas de fondo, caudal, tirante normal y crítico, perfil por paso estándar, autolimpieza, llegada de cunetas, caja de llegada y caja de caída con poza, registros con tapa ciega, juntas, estructura por zonas de carga, metrado del colector y memoria). Usar cuando el usuario pida un colector frontal o canal cubierto nuevo, revisar uno existente, empalmar tramos de varios proyectos (cadena hidráulica) o cambiar registros, tapas, juntas o cajas de un colector.
---

# Colector pluvial frontal cubierto

Método aplicado y aprobado por el usuario en tres expedientes contiguos del predio Los Mangos, Morales (San Martín), que
sirven de ejemplo: CAR Varones (CUI 2705619), Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514) y CAR Mujeres
(CUI 2717013). Para el detalle completo (tablas de cada tramo, fórmulas, cronología de decisiones) leer
`referencias/03_colector_frontal.md`; las rutas de archivos que aparecen allí son del trabajo original y no existen en este chat.
La lluvia y los caudales se calculan con el skill `hidrologia-drenaje-pluvial`; el metrado en planilla, con `metrado-drenaje-delphin`.

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

## 1. Datos que hay que pedir (no inventar; no preguntar lo que ya muestra el plano)
1. Proyecto: nombre completo, CUI, entidad, ubicación. Proyecto aguas arriba ("aporte externo") y aguas abajo ("receptor") con nombre y CUI.
2. Planta general en DXF: línea del frente (cerco o línea de referencia), si hay cerco o no, lindero con la vía, vanos de acceso
   (camiones, autos, motos: coordenadas de postes), cunetas que llegan (eje, NCF, NCT, sección, abierta o tapada).
3. Niveles: NPT del frente por tramo (la losa superior es la vereda), cota de fondo y nivel de agua (NA) del receptor, alto interior
   del receptor en su registro, cota de fondo y ancho del aporte externo en su llegada, terreno a lo largo del eje.
4. Hidrología: P24 o P10/P20 del estudio, Σ C·A del predio, caudal del aporte externo (dato de su memoria, sin validarlo).
5. Metrado vigente del usuario (planilla Delphin) y estudio de mecánica de suelos (EMS) si existe.
Si falta algo, plantear la hipótesis más conservadora, dejarla escrita como "hipótesis cubierta" y avisarla.

## 2. Concepción y criterios fijos
- Marco cerrado monolítico de concreto armado f'c 210 kg/cm² (losa de fondo + 2 muros + losa superior), fy 4200, sobre solado
  e = 0.05 f'c 100 (dibujado al ancho exterior). Losa superior al ras del NPT con acabado frotachado: funciona como vereda.
- Cubierto en todo el recorrido (seguridad: centros con niños, adolescentes o mujeres). Sin lloraderos (solo las cunetas los llevan).
- Todo dentro del lindero del predio; nada en la faja de la vía. Limpieza por registros con tapa removible.
- Régimen subcrítico; llenado y/h ≤ 0.85; borde libre BL ≥ 0.05 m bajo la losa; Froude F < 1 (F = 1 solo en el borde de caída).
- V 0.90 a 3.0 m/s con el caudal de diseño (RNE CE.040, R.M. N.° 126-2021-VIVIENDA, que reemplaza a la OS.060); τ = γ·R·S ≥ 0.15 kg/m²
  con caudales parciales hasta el 5 %. Manning n = 0.015 (concreto vaciado in situ).
- Acero según la carga de cada zona, **sin sobredimensionar** (el usuario pidió ahorrar acero: el expediente lo firman especialistas).
- El ancho crece aguas abajo. Ejemplo de la cadena: Varones b 0.60 → caja de llegada CL → Refugio b 0.80 → caja de caída CC con poza →
  R-01 del CAR Mujeres b 1.50 → salida con aleros a la berma de la vía.

| Dato (ejemplos) | CAR Varones | Hogar de Refugio | CAR Mujeres |
|---|---|---|---|
| b / muros / fondo / losa sup. | 0.60 / 0.15 / 0.15 / 0.10 | 0.80 / 0.15 / 0.15 / 0.10 | 1.50 / 0.10 / 0.10 / 0.10 |
| Losa en cruce de camiones | 0.25 | 0.25 | 0.20 (muros 0.15, fondo 0.20) |
| Longitud / S | 105.29 m / 0.30 % | 69.89 m al brink / 0.30 % | 139.08 m / 0.302 % |
| Cota de fondo inicio → fin | 260.20 → 259.884 | 259.10 → 258.890 | 258.72 → 258.30 |
| Q de diseño | 221.7 L/s escalonado + 37.0 directo a la CL | 560.6 L/s constante | 626.2 → 822.9 L/s |
| Control aguas abajo | caída libre a la CL (yc) | caída libre a la poza CC (yc) | vertedero sobre la cresta de la vía |
| Registros / juntas | 11 / 26 | 10 / 17 | 15 / 33 |

## 3. Trazo en planta
- Eje paralelo al frente a d = junta 0.025 + e_muro + b/2 (Refugio, pegado por fuera del cerco: 0.575; Varones sin cerco: 0.475 desde
  la línea del frente hacia el predio). Contra el cimiento del cerco va junta de tecnopor 1".
- Progresivas 0+000.00 desde el extremo aguas arriba (caja de llegada o portón), crecientes aguas abajo.
- Llegada al receptor con quiebres a 45° (cada quiebre lleva registro) y un tramo final recto si hace falta.
- Zonas de carga en progresivas: p1 = inicio del vano − holgura, p2 = fin del vano + holgura (camiones 0.30; motos 0.115).
  Tipos NORMAL (peatonal), MOTOS, AUTOS, CAMION. Cada zona define espesores y armado.
- UTM (WGS 84, 18 S) por traslación y giro con un punto común del vecino (p. ej. el R-01 del receptor y el azimut de su lindero);
  rotular "ubicación referencial, verificar en campo" si no hay coordenadas del cerco.

## 4. Cotas y predimensionamiento (qué fija cada dimensión)
- Losa superior = NPT del frente (no se elige). Techo interior = NPT − e_losa(zona). h = techo − cota de fondo (por eso h puede ser
  1.40 a 1.61 aunque el tirante sea 0.50).
- Cota de fondo inicial: la más alta que permita (a) caída libre de la cuneta más baja que llega y (b) llegada del aporte externo con
  caída ≥ 0.10 m sobre el NA.
- Cota de fondo final ≥ cota de fondo del receptor. S = la que cabe entre ambas con régimen subcrítico y autolimpieza (se adoptó 0.30 %).
- b: empezar en 0.60 (mínimo práctico para limpieza manual) y subir de 0.10 en 0.10 hasta cumplir llenado, BL y F en todas las estaciones.
- Espesores: 0.15 en muros de hasta ~1.65 m de alto; 0.10 si h ≤ 0.67.

## 5. Caudal del colector
- tc del colector = 10 min (entrada) + ≈ 3 (recorrido en cunetas) + ≈ 2 (recorrido en el colector) = 15 min. Con la lluvia de Morales:
  I15 = 155.66 mm/h (las cunetas, canaletas y montantes usan I10 = 210.98 mm/h; es la misma lluvia: P10 = 35.163 mm en 10 min).
- Q [L/s] = Σ(C·A) · I · FS / 3600 (A en m², I en mm/h), FS = 1.15, C ponderado del predio (p. ej. 0.771 / 0.807 / 0.704).
- Aporte externo = dato de la memoria del vecino. Suma de picos sin desfase + FS 1.15 = hipótesis conservadora declarada.
- Reparto entre cunetas: por franja de frente que drena cada una (límites en los puntos medios entre ejes; una cuneta absorbe el
  redondeo para que la suma sea exacta) o en partes iguales. Q acumulado por progresiva (escalón en cada cuneta; seco antes de la primera).

## 6. Hidráulica y perfil de flujo
- Manning: Q = (1/n)·A·R^(2/3)·S^(1/2); A = b·y; R = b·y/(b + 2y). Tirante normal por bisección en [1e-4, 5] o por punto fijo
  y(k+1) = (Q·n·(b + 2y(k))^(2/3) / (b^(5/3)·S^(1/2)))^(3/5) (8 iteraciones en Excel). yc = (Q²/(g·b²))^(1/3), g = 9.81. F = V/√(g·y).
- Control aguas abajo: caída libre a una caja con NA más bajo → yc en el borde; vertido sobre un control externo → NA = cresta + H con
  H = (Q/(Cw·Lw))^(2/3), Cw = 1.70 (cresta ancha); entrega ahogada → NA del receptor. Tomar el mayor.
- Paso estándar de aguas abajo (2) hacia aguas arriba (1): z1 + y1 + V1²/2g = z2 + y2 + V2²/2g + Δx·(Sf1 + Sf2)/2, Sf = (n·V/R^(2/3))².
  Resolver y1 por bisección en [1.001·yc, 3.0] (rama subcrítica), 100 iteraciones (30 en columnas de Excel, sin macros).
- Estaciones cada 1.00 m + quiebres, empalmes, registros, límites de zona y fin. En cada una: NA, h, llenado, BL, V, F, zona, CUMPLE.
- Capacidad con llenado 85 % en la h mínima: Q85 = (1/n)·b·0.85h·R^(2/3)·√S, como margen (Varones 445 L/s = 2.0×; Refugio 2.6×).
- Resultados de control: Refugio yn 0.518, yc 0.369, V 1.35, F 0.60, llenado máx. 0.372, BL mín. 0.834; Varones yn 0.343, yc 0.241,
  llenado máx. 0.341, BL mín. 0.630; CAR Mujeres llenado máx. 0.815, BL mín. 0.087 (gobierna el llenado: por eso b = 1.50).

## 7. Autolimpieza
Tabla en flujo uniforme con el caudal de diseño, cada aporte por separado y 50, 25, 10 y 5 %: yn, V, τ = 1000·R·S (kg/m²), F.
Cumple si V ≥ 0.90 con el Q de diseño y τ ≥ 0.15 en los parciales. En cabeceras con poco caudal (b mínimo 0.60) se acepta V < 0.90 si
τ ≥ 0.15 con el caudal del tramo y hay registros cada ≤ 12 m (escribirlo en la memoria). Si no cumple: subir S, reducir b o caja de caída.

## 8. Llegada de las cunetas
- Ventana 0.40 × Hv en el muro lado predio (Hv = techo − NCF en el muro), dejada con cajón de madera, sin dintel, hasta la losa.
  Refuerzo: 4 barras 3/8" verticales L = Hv + 0.60 y 2 horizontales de 1.00; los marcos se cortan con gancho de 0.10.
- Caída libre al fondo; fondo pulido 1:3 e = 1 cm en 1.00 m bajo la caída; junta de tecnopor 1" con sellador en el contorno; registro encima.
- Verificar NCF en el muro − NA del colector > 0 ("CAIDA LIBRE"; si no, "AHOGADA" y la cuneta remansa).
- Tuberías que entregan directo (montante o sumidero): misma regla que en cunetas (usuario, 25-10-2026): el fondo del tubo llega
  sobre el NA del colector en ese punto + 0.05 m; si llega a la cota de fondo queda ahogado y el agua regresa.
- Cuando el colector recibe una red de cunetas sobre terreno, en la verificación de cada descarga su cota de fondo y su NA reemplazan
  al terreno exterior (prueba del CAR Varones, descargas D1 a D5): la cuneta no puede quedar "enterrada" respecto del colector.
- Si la cuneta no llega al muro se prolonga con su sección y pendiente (NCF muro = NCF − 0.005·prolongación); si invade la franja del
  colector se acorta hasta la cara del muro (NCF + 0.005·acortamiento). **Prolongación y acortamiento se metran en las partidas de
  cunetas; no hay partida de empalme ni de prolongación en el colector.**

## 9. Caja de llegada CL (recibe un colector vecino)
- Interior 1.50 × 1.00, muros 0.15; piso de poza = cota de fondo inicial − 0.30; tapa al piso del vecino si está más alto (escalón con
  murete de 0.15). Ventanas con el ancho de lo que llega y alto hasta el techo (sin dintel si techo CL = techo del colector que llega).
- Verificar: caída libre del aporte ≥ 0.10 m sobre el NA de la caja; colchón NA − piso ≥ 0.50 m. Ej.: 259.884 − 259.606 = 0.278;
  colchón 0.806. Malla 3/8" @0.20 en ambas caras (+10 %). La junta entre estructuras de distinto expediente la metra el que llega.

## 10. Caja de caída CC con poza (entrega a un receptor más bajo)
1. Brink: yc en el ancho del colector; NA = CF + yc. 2. Piso de poza = CF del receptor − 0.40. 3. E1 = caída + 1.5·yc (sin pérdidas).
4. y1 por energía y1 + (Q/(b·y1))²/2g = E1 (rama supercrítica, bisección en [1e-3, yc]); V1; F1 = V1/√(g·y1).
5. y2 = y1/2·(√(1 + 8F1²) − 1) en el ancho del colector (conservador). 6. Exigir y2 ≤ NA del receptor − piso (resalto ahogado).
7. L poza ≥ 0.8 × 6·y2 (USBR). 8. Umbral con corona = CF del receptor. 9. Ventana de salida = ancho del receptor × su alto interior.
Ejemplo Refugio: yc 0.369, caída 0.570, E1 1.123, y1 0.161, V1 4.34, F1 3.45, y2 0.711 ≤ 0.742, poza 3.50 ≥ 3.41, ventana 1.50 × 0.43.

## 11. Registros y tapa ciega
- Uno sobre **cada** llegada de cuneta (exactamente encima), uno en cada quiebre; tramos > 12 m se dividen en n = ceil(L/12) partes
  iguales. **Nunca dentro de un cruce** (ni su rebaje): correrlo fuera del vano + holgura. Numerar (RS-01, RV-01, R-01…) con progresiva y nota.
- Tapa ciega de concreto armado (vigente): 0.68 × 0.68 × 0.08 f'c 210 vaciada aparte; parrilla 3/8" @0.10 (7 + 7 barras de 0.62);
  2 asas de fierro liso 1/2" (desarrollo 0.50) en cajuelas 0.19 × 0.06 × 0.03 a ±0.20; cantos biselados 1 × 1 cm; ≈ 89 kg (2 operarios).
  Asiento en rebaje 0.70 × 0.70 × 0.08 de la losa, holgura 0.01, luz libre 0.60 × 0.60; borde engrosado 0.15 × 0.10 bajo la losa
  (perímetro medio 3.00 m) con 8 Ø 1/2" L = 1.40. **Sin marco, contramarco, soldadura ni pintura.**
- Si b ≤ 0.60 (menor que el rebaje): el rebaje apoya en la cabeza de los muros y el borde engrosado va solo en los 2 lados
  transversales (2 × b por registro), no en 4.
- Por registro: tapa 0.0370 m³; encofrado 0.2176 m²; parrilla 4.86 kg; asas 0.99 kg; borde 11.13 kg; descuento de losa
  0.49 × 0.08 + 0.36 × (e_losa − 0.08). La tapa se verifica con rueda de 1 t; si cae en paso de camiones, verificar HL-93.

## 12. Juntas
- Dilatación transversal cada 4.00 m en toda la sección: anillo de tecnopor 1" + sellador asfáltico 1" × 2" (RC-250 + arena gruesa)
  en caras interiores y superior (EG-2013 MTC, Sección 510). N = ENTERO(L/4); longitud = N × [2·b_ext + 2(e_fondo + h_máx + e_losa)].
  Acero longitudinal cortado a 0.05 de cada lado.
- Longitudinal (tecnopor 1" de 0.90 de alto + sellador) **solo** donde el muro toca el cimiento del cerco u otra estructura;
  **nunca contra terreno natural**. Toda junta entre estructuras de distinto expediente lleva tecnopor + sellador.

## 13. Estructura (E.020, E.060, AASHTO LRFD / Manual de Puentes MTC, E.050)
Parámetros: γc 2.4, γs 1.8 t/m³, Ko 0.5, s/c peatonal 0.5 t/m², lateral liviano 1.0 y camión 2.7 t/m², rueda liviana/moto 1.0 t, rueda
HL-93 7.26 t, IM 0.33, huella c 0.25, Lc = b + e_muro, franja E = 0.66 + 0.55·Lc; U = 1.4D + 1.7L; φ 0.90 flexión, 0.85 cortante.
- A Losa normal: Mu = (1.4γc·e + 1.7·sp)·Lc²/8; d = e/2 (marco único). B Losa motos y C losa camiones: Mr = P(1+IM)(Lc/4 − c/8)/E;
  en C además Vu ≤ φVc = 0.85·0.53·√f'c·100·d/1000. D/E/F Muros: p = Ko·γs·H, q = Ko·s/c, M = pH²/20 + qH²/12, Mu = 1.7M.
  G Losa de fondo: Mu = 1.5·q·Lc²/8 y presión al suelo frente al EMS (sin EMS: comparar con 0.50 kg/cm² y escribir "VERIFICAR EMS").
  H Tapa: L 0.64, d = 5.5 − 0.48 cm, As 3/8" @0.10. Siempre Mu ≤ φMn, Vu ≤ φVc, As ≥ 0.0018·b·e.
- Armados adoptados: NORMAL un marco cerrado 3/8" @0.20 en el eje + longitudinales 3/8" @0.25 (una capa: E.060 14.3.4 la permite en
  e ≤ 0.20), ganchos 0.30; MOTOS/AUTOS 3/8" @0.15; CAMION losa 0.25 y doble marco 1/2" @0.15, longitudinales @0.20, recubrimiento 0.04.
  Recubrimientos 0.04 contra el suelo, 0.025 losa superior normal y tapas. Traslapes 0.40 (3/8") y 0.50 (1/2"); barra 9.00 m.
- Si un elemento no cumple: pasar a @0.15, luego doble marco 1/2" o subir espesor. Curado 7 días; sin tránsito 14 días; camiones 28 días.

## 14. Metrado del colector (resumen; formato en el skill `metrado-drenaje-delphin`)
Partida independiente "COLECTOR PLUVIAL FRONTAL (TRAMO …)" con subtítulo propio; no tocar ni mezclar las partidas de cunetas.
Por tramo homogéneo (≤ 2 m o por zona, h y Hz ponderados): zanja = b_ext + 2 × 0.25; excavación = zanja × Hz × L; refine y solado =
(b_ext + 0.10) × L; relleno = 2 × 0.25 × Hz × L + 1.00 × (NPT − terreno) × L; eliminación = (exc − rell) × 1.20; concreto = fondo +
muros + losa − descuentos + borde engrosado (**una sola partida**); encofrado = 2h·L + 2(e_f + h + e_l)·L + b·L; frotachado = b_ext × L;
curado = (2h + b + b_ext) × L; acero: marcos = REDONDEAR.MAS(L/s) × perímetro (marco único 2(b_ext − e) + 2(e_f/2 + h + e_l/2) + 0.30),
longitudinales = n × L × (1 + 0.40/9.00); tapa de registro por und; dos partidas de junta (dilatación y longitudinal/contacto).

## 15. Entregables
- Excel de memoria de cálculo con fórmulas visibles: MEMORIA, DATOS (parámetro, valor, und, fuente, símbolo), CAUDALES, CUNETAS,
  EMPALME (CC y CL), PERFIL_FLUJO, ESTRUCTURAL (bloques A–H), CUMPLIMIENTO (requisito, norma, criterio, valor, resultado) y bloque
  "Datos de otros expedientes y cómo quedan cubiertos". Azul = dato, negro = fórmula, verde = vínculo.
- Capítulo del colector en Word **al final** de la memoria hidrológica del usuario, sin alterar lo anterior: alcance y condiciones de
  compatibilidad, trazo, caudal (210.98 vs 155.66 explicado), sección, perfil, autolimpieza, CC, CL, cunetas, estructura, normativa,
  criterios constructivos, resumen de metrados del RESUMEN vigente, cumplimiento, datos de otros expedientes, conclusiones.
- Planos DXF a escala real con presentación (planta 1/200, perfil, secciones por zona con acero, registro y tapa, empalme, cajas,
  juntas, isométricos) + PNG; metrado en la planilla; especificaciones por partida. PDF solo si se pide.

## 16. Lista de verificación final
- [ ] Llenado ≤ 0.85, BL ≥ 0.05 y F < 1 en todas las estaciones (salvo el borde de caída); V 0.90–3.0; τ ≥ 0.15 con el 5 %.
- [ ] Cada cuneta con caída libre > 0; aporte externo ≥ 0.10 sobre el NA de la CL; colchón ≥ 0.50.
- [ ] CF de entrega ≥ CF del receptor; Q entregado ≤ Q previsto por el receptor; resalto ahogado; poza ≥ 0.8 × 6y2; ventana ≤ alto del receptor.
- [ ] Registros ≤ 12 m, sobre cada empalme y quiebre, ninguno (ni su rebaje) en un cruce; borde engrosado en 2 lados si b ≤ 0.60.
- [ ] Juntas cada 4 m; junta longitudinal solo contra cerco o estructura.
- [ ] φMn ≥ Mu, φVc ≥ Vu, As ≥ As mín en A–H; una capa solo con e ≤ 0.20; presión al suelo ≤ EMS o "VERIFICAR EMS".
- [ ] Cotas, NA, caudales, ventanas y coordenadas iguales en los expedientes vecinos (cuadro de empalme).
- [ ] Metrado = cálculo (tolerancia 0.05) y ningún valor previo del usuario cambió; prolongaciones de cunetas fuera del colector.
- [ ] Misma información en memoria, Excel, planos, metrado y especificaciones; proyectos citados por nombre y CUI.
- [ ] Criterio de llenado declarado: los colectores aprobados usan y/h ≤ 0.85; la CE.040, 17.6.2 limita a 80 % el tirante en
      conductos cerrados (criterio que el usuario adoptó para los tramos tapados el 25-10-2026). En un colector nuevo cumplir el más
      exigente o consultarlo; en los aprobados (CAR Mujeres llega a 0.815) no se cambia nada sin pedido: solo se avisa.
- [ ] Recubrimiento contra el suelo: la biblioteca de normas cotejada con el texto oficial registra 75 mm para concreto vaciado
      contra el suelo (E.060, 7.7.1 a); los colectores aprobados usan 0.04 sobre solado. En uno nuevo, declarar qué caso aplica.
- [ ] Cada dato con su fuente (norma con artículo o tabla, referencia técnica o criterio del proyectista) en la hoja DATOS y en la memoria.
- [ ] Nombre, CUI, ubicación y entidad (GTBM; nunca "PEHCBM") del propio expediente, sin textos que queden de otro proyecto.

## 17. Errores que el usuario ya corrigió (no repetirlos)
- "Losa vehicular en todo el frente": no; hay vereda peatonal, portón de motos e ingreso de camiones; armado por zona.
- NPT tomado de un rótulo erróneo (260.45 del ingreso): el frente es uno solo (+260.60); en Varones todo a +261.15 "al ras de lo de afuera".
- Suponer cerco donde no hay (Varones): sin cerco no hay junta longitudinal; a ambos lados terreno natural.
- Tapas corridas respecto de la entrega de cada cuneta: deben ir exactamente encima del empalme.
- Partidas de empalme y de prolongación de cunetas dentro del colector: eliminadas ("ya metré mis cunetas, tú solo haces el colector").
- Doble capa de acero y ~5,000 kg: sobredimensionado; se pasó a marco único (≈ 3,056 kg en el Refugio).
- Usar 210.98 mm/h en el colector (caudal 35.5 % mayor sin sustento): el colector va con tc 15 min (155.66 mm/h).
- Junta "entre colector, cerco y piso" a ambos lados (210.98 m): solo existe contra el cerco (58.81 m). Sello elastomérico o de
  poliuretano: reemplazado por tecnopor + sellador asfáltico 1" × 2".
- Ventana de salida de la CC de 0.60 de alto (pasaba sobre el piso del receptor): es el alto interior del receptor (0.43).
- Borde engrosado de 4 lados copiado a un colector de b 0.60: va solo en 2 lados (concreto 56.02 → 55.72 m³).
- Dejar pendiente un detalle porque "el modelo supone otro ancho": rechazado ("tú diseñaste todo, todo debe cuadrar").
- Confundir el ancho de zanja (1.40) con el ancho del colector (0.60).
- Memoria con textos de otro proyecto ("recuerda, esta memoria es de Refugio Mujeres Violentadas, CUI que termina en 14"; "varios
  dicen institución educativa"): revisar nombre, CUI, entidad y tipo de local en todo el documento.
- Proponer costos o presupuesto cuando se pide diseño o metrado: el usuario llega solo hasta los metrados; el presupuesto lo hace el
  ingeniero en Delphin (no en S10).
- Planos: amarillo sobre fondo blanco, 3D negros, cotas que no miden lo que dicen, acero fuera de su losa, barras sin su diámetro real
  (3/8" = 9.5 mm), huecos en secciones, textos encimados o verticales.

## Referencias
- `referencias/03_colector_frontal.md`: capítulo completo (tramos, tablas de cunetas y registros, hidráulica, cajas, estructura,
  metrado, coordinación entre expedientes, cronología y validaciones para programarlo). Leerlo antes de diseñar o revisar.
