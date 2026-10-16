---
name: diseno-colector-pluvial
description: Diseñar un colector pluvial frontal cubierto (canal rectangular de concreto armado con losa-vereda) y la llegada de cunetas de piso, con hidrología, hidráulica, estructura, registros con tapa ciega, juntas, cajas de llegada y de caída, metrado Delphin, ACU, memoria, especificaciones y juego de planos. Usar en proyectos nuevos de colector/cunetas o al revisar los de CAR Varones, Hogar de Refugio y CAR Mujeres.
---

# Diseño de colector pluvial frontal y cunetas (criterio de los 3 CAR del predio Los Mangos)

Implementación de referencia: `herramientas/diseno.py` (Hogar de Refugio, CUI 2675514), `herramientas/varones/diseno_v.py`
(CAR Varones, CUI 2705619), `herramientas/mujeres/datos_m.py` (CAR Mujeres, CUI 2717013). Planos con el skill
`planos-ordenados`; metrado de cunetas con `metrado-cunetas`.

## 0. Flujo de trabajo
1. Leer insumos: planta general de arquitectura (DXF), perfiles de cunetas, estudio hidrológico del proyecto (P10, P20, TR),
   metrado vigente del usuario (planilla Delphin) y expedientes de los colectores vecinos (aguas arriba / abajo).
2. Fijar datos en un diccionario `D` (ver §1) y la geometría en planta (§2). Todo valor debe tener su fuente.
3. Calcular hidrología (§3) e hidráulica con perfil de flujo (§4); verificar velocidades y autolimpieza (§5).
4. Ubicar registros, cruces, empalmes y juntas con las reglas (§6 a §9).
5. Verificar estructura por zonas (§10).
6. Metrar en la planilla del usuario como partida independiente (§12), ACU (§13).
7. Planos (§14), memoria y especificaciones (§15). Revisar coherencia (§16) y entregar DXF + PNG + Excel + Word.

## 1. Datos tipo (Hogar de Refugio como ejemplo)
| Dato | Valor | Nota |
|---|---|---|
| Sección | rectangular, b interior 0.80 (Varones 0.60, Mujeres 1.50) | ancho crece aguas abajo |
| Espesores | muro 0.15 (Mujeres 0.10), fondo 0.15, losa superior 0.10; 0.25 en cruce de camiones | |
| Solado | 0.05 m, f'c = 100 kg/cm² | dibujado al ancho exterior |
| Concreto / acero | f'c = 210 kg/cm²; fy = 4200 kg/cm²; recubrimiento 4 cm; traslapes 0.40 (3/8") y 0.50 (1/2") | |
| Rugosidad | n = 0.015 (concreto) | |
| Pendiente | S = 0.3 % (3 ‰) | controlada por cota de fondo de entrega |
| Losa superior | = piso terminado del frente (NPT): funciona como vereda | sin lloraderos en el colector |
| Junta con cerco | tecnopor 1" (0.025) entre muro y cimiento del cerco | eje a 0.575 del cerco |
| Criterios | llenado ≤ 0.85; borde libre ≥ 0.05 m; Froude < 1 | |

## 2. Trazo en planta (decisiones)
- El colector va paralelo al lindero o cerco frontal, del lado interior, pegado al cerco con la junta de 1".
- Quiebres a 45° para llegar al registro o caja del receptor; cada quiebre lleva registro.
- Progresivas desde la caja de llegada (0+000) creciendo aguas abajo. Coordenadas: las del plano de arquitectura y,
  si se pide UTM (WGS 84, 18 S), por traslación y giro con un punto común del colector vecino (p. ej. R-01 del CAR Mujeres).
- Zonas de carga a lo largo del eje: NORMAL (peatonal), MOTOS (portón de motos), CAMION (ingreso vehicular), con una
  holgura a cada lado del vano (Refugio: 0.115 m).

## 3. Hidrología
- Método racional: Q = C·I·A/360 (A en ha) o con CA ponderado por áreas de techo, pavimento y área verde.
- Intensidad con la ecuación de Dick y Peschke a partir de P10 y P20 del estudio hidrológico; TR = 25 años;
  tc del colector = 15 min (mayor que el de una cuneta). Factor de seguridad 1.15.
- Sumar los aportes externos (colector vecino aguas arriba) con su caudal de su propio expediente.
  Ej.: Refugio 301.9 L/s + Varones 258.7 L/s (221.7 por colector + 37.0 por cuneta Eje 01) = 560.6 L/s.

## 4. Hidráulica y perfil de flujo
- Tirante normal (Manning) y crítico; perfil por el método del paso estándar desde el control aguas abajo
  (tirante crítico en el borde de la caída a la poza, o nivel del receptor si está ahogado) hacia aguas arriba.
- Verificar en cada estación: llenado ≤ 0.85, borde libre ≥ 0.05 m, Froude < 1 (subcrítico).
- Caja de caída CC (entrega al receptor): poza de 3.50 m de largo y 0.40 de profundidad, ancho 1.50; resalto en el ancho del
  colector (conservador); exigir que el tirante disponible aguas abajo supere y₂ (resalto ahogado); L resalto ≈ 6·y₂.
  La ventana de salida tiene el alto interior del colector receptor en su registro (ej. 1.50 × 0.43).
- Caja de llegada CL (aporte externo): 1.50 × 1.00 interior con poza de 0.30 bajo la cota de fondo; las ventanas de llegada
  con el ancho del colector que llega; verificar caída libre sobre el nivel de agua.
- Las cotas de fondo y niveles de agua deben empalmar con los colectores vecinos (comprobar ambos expedientes).

## 5. Velocidades y autolimpieza (RNE CE.040 Drenaje Pluvial, R.M. N.° 126-2021-VIVIENDA, que reemplaza a la OS.060)
- V mínima 0.90 m/s con el caudal de diseño; V máxima 3.0 m/s (concreto).
- Esfuerzo tractivo τ = γ·R·S ≥ 0.15 kg/m² (1.5 Pa) con caudales parciales (hasta 5 % del de diseño).
- Si no cumple: subir S dentro de lo que permite la cota de entrega, reducir b, o proponer escalones / caja de caída.

## 6. Registros de limpieza (reglas)
- Separación máxima 12 m; uno en cada llegada de cuneta, en cada quiebre y donde haga falta para no pasar de 12 m.
- Nunca dentro de un cruce vehicular o de motos: si cae dentro, correrlo fuera del vano más la holgura.
- Numeración RS-01, RS-02… (Varones RV-xx). Lista con progresiva, tipo y nota (empalme, limpieza, quiebre).
- **Tapa ciega de concreto armado (vigente desde oct. 2026)**:
  - Tapa 0.68 × 0.68 × 0.08, f'c 210, vaciada aparte en obra; parrilla 3/8" @0.10 (7 + 7 barras de 0.62);
    2 asas de fierro liso 1/2" (agarre 0.15, patas 0.02, ganchos 0.15; desarrollo 0.50) en cajuelas 0.19 × 0.06 × 0.03,
    eje de asas a ±0.20; cantos biselados 1 × 1 cm; peso ≈ 89 kg.
  - Asiento: rebaje 0.70 × 0.70 × 0.08 en la losa (0.05 por lado), holgura 1 cm, luz libre 0.60 × 0.60.
  - Borde engrosado 0.15 × 0.10 bajo la losa (anillo de 0.60 a 0.90) y refuerzo de borde 8 Ø 1/2" L = 1.40.
  - Si b ≤ luz libre (CAR Varones, b 0.60): en los lados largos el rebaje apoya en la cabeza de los muros y el borde
    engrosado va solo en los 2 lados transversales (entre muros); barras transversales con ganchos dentro de los muros.
  - Sin marco, contramarco, anclajes, soldadura ni pintura. Descuento de la losa por registro:
    0.49 × 0.08 + 0.36 × (e_losa − 0.08).
  - CAR Mujeres conserva su metrado con marco y contramarco (congelado); solo su lámina DP-06B usa la tapa ciega.

## 7. Empalme de cunetas
- Ventana de 0.40 × H en el muro del lado del predio, caída libre al fondo del colector, junta de tecnopor 1" en el contacto
  y registro sobre el empalme.
- Verificar que la cota de fondo de la cuneta al llegar quede por encima del nivel de agua del colector (no remansa).
- Si la cuneta termina antes del cerco, se prolonga con la misma sección y pendiente hasta el muro del colector; esa
  prolongación se metra en las partidas de cunetas (la cuneta se metra hasta el muro; no hay partida de empalme aparte).

## 8. Cunetas de piso (criterio del proyecto)
- Sección 0.40 × H, muros y losa de 0.10, pendiente 0.5 %; tramos abiertos y tapados (tapa 0.10). Acero 3/8" solo donde
  H > 0.40 o en tramos tapados (ver `metrado-cunetas`).
- Junta de cunetas en toda la sección en U (2 muros + losa): longitud por junta = 2·H + 0.40 (EG-2013 MTC, Sección 510).
- Lloraderos PVC Ø 3" con filtro de grava y geotextil @1.50 m solo en muros de cuneta junto a área verde (franja exterior de
  0.30 m sobre el achurado de área verde). CAR Mujeres no lleva (ya presupuestado).
- Rejilla móvil: módulo de 1.00 m, platinas 1" × 3/16" @1", ángulos L 1" × 1" × 3/16", rebaje 0.05 × 1".

## 9. Juntas del colector
- Dilatación cada 4.00 m en toda la sección: tecnopor 1" + sellador asfáltico 1" × 2" (asfalto líquido RC-250 + arena gruesa).
- Junta longitudinal muro–cimiento del cerco solo donde hay cerco; del lado de terreno natural no lleva junta.
- Contacto con la caja CL: junta de tecnopor 1" con sellador.

## 10. Estructura (marco cerrado monolítico)
- Cargas: E.020 (peso propio, sobrecarga peatonal), empuje en reposo del relleno, rueda HL-93 (AASHTO LRFD / Manual de
  Puentes MTC) con impacto 33 % en ingreso vehicular; rueda de 1 t en portón de motos. Diseño por resistencia E.060.
- Armados por zona (Refugio): NORMAL un marco 3/8" @0.20 en el eje + longitudinales 3/8" @0.25 (una capa, E.060 14.3.4
  para espesores ≤ 0.20); MOTOS 3/8" @0.15; CAMION doble marco 1/2" @0.15 con losa 0.25. ≈ 38 kg/m en tramo normal.
- Verificar Mu ≤ φMn y Vu ≤ φVc por elemento, tapas incluidas, y la presión al suelo frente a la capacidad portante (E.050).

## 11. Movimiento de tierras
- Excavación con sobreancho de 0.25 por lado; relleno lateral compactado con material propio seleccionado;
  eliminación del excedente con esponjamiento 20 %.

## 12. Metrado (planilla Delphin del usuario)
- Partida independiente 01.04.04 COLECTOR PLUVIAL FRONTAL; no tocar las partidas existentes.
- Hojas con fórmulas visibles: COLECTOR PARAMETROS, MOV. TIERRAS, CONCRETO, ENCOFRADO, ACERO, REGISTROS Y TAPAS, JUNTAS Y
  EMPALMES, INSUMOS; DESAGREGADO TAPA REGISTRO. Concreto del colector en una sola partida; tapa de registro por und
  (01.04.04.05.01); acabado frotachado de losa superior (vereda); juntas 01.04.04.06.01 y .06.02.
- Editar planillas con `angulo_contramarco_refugio.Libro` (XML) para no perder formato y recalcular con LibreOffice.
- Los cuadros de las láminas DA leen la planilla (valores guardados); nunca se recalculan aparte.

## 13. ACU
- Formato Delphin: mano de obra (cuadrilla y rendimiento), materiales, equipos (% MO de herramientas).
- MO: hoja COSTO HORA HOMBRE 2026 (CAPECO-FTCCP): 28.95 / 22.68 / 20.54. Precios de materiales reales con su fuente.
- Partidas globales pedidas "por metro": tubería por m y accesorios por und; el metrado original no cambia.

## 14. Juego de planos (Refugio, 24 láminas)
DP-00 índice (A3) · DP-01 planta 1/200 · DP-02 perfil general · DP-03A/B perfiles de detalle 1/25 · DP-04A/B y DP-05A/B secciones ·
DP-06A secciones típicas armadas · DP-06B registro con tapa ciega · DP-06C empalme de cuneta · DP-06D isométricos de la tapa ·
DP-07 cajas CL y CC · DP-08 cuadro de acero y especificaciones · DP-09/DP-10 isométricos · DA-01 a DA-03 cuadros de partidas ·
DD-01 rebaje de asiento y refuerzo de borde · DD-02 tapa ciega: fabricación y colocación · DD-03 juntas · DD-04 empalme de cuneta.
Todas con presentación de AutoCAD (escala 1:1) y vista previa PNG. Ver `planos-ordenados`.

## 15. Memoria y especificaciones
- Memoria de cálculo Excel: DATOS, CAUDALES, EMPALME, PERFIL_FLUJO, ESTRUCTURAL (`memoria_xlsx.py`).
- Capítulo del colector al final del Word de hidrología del usuario, sin tocar lo anterior (`memoria_docx.py`).
- Especificaciones técnicas por partida (`especificaciones/espec.py` + `docx_espec.js`).
- Marco normativo: CE.040, E.020, E.060, E.050, Manual de Hidrología, Hidráulica y Drenaje (MTC), Manual de Puentes (MTC) /
  AASHTO LRFD, EG-2013 (MTC).

## 16. Coherencia y verificación (obligatoria)
- Un cambio de diseño (p. ej. tapa ciega) se propaga a: metrado, ACU, desagregado, láminas (DP, DA, DD, isométricos),
  especificaciones y memoria. Buscar textos viejos con grep en generadores y entregables.
- Al reutilizar módulos entre proyectos, convertir textos fijos en parámetros (`compat.py`) y comprobar con una huella que el
  otro proyecto queda idéntico.
- Si algo no cubre ninguna regla (empalme raro, interferencia, pedido nuevo), no inventar: presentar opciones al usuario,
  recomendar una y, una vez decidida, agregarla como regla en este skill.
