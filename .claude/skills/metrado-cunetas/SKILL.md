---
name: metrado-cunetas
description: Metrar cunetas de concreto (concreto, encofrado, acero, curado, rejillas, juntas, limpieza, trazo, movimiento de tierras) a partir de un DXF de perfiles longitudinales y secciones, llenando la plantilla Excel del proyecto hoja por hoja. Usar cuando el usuario pida metrar cunetas de un proyecto nuevo o revisar el metrado de Varones / Mujeres Violentadas.
---

# Metrado de cunetas sobre la plantilla del proyecto

Motor: `herramientas/metrado_varones.py` (lee el DXF, calcula y llena la plantilla). Caso resuelto: CAR Varones
(CUI 2705619), 9 ejes, 19 tramos, archivo `entregables/METRADO_DRENAJE_PLUVIAL_CAR_VARONES_CUNETAS.xlsx`.
Plantilla: `insumos/solange/METRADO_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS_v2.xlsx` (13 hojas; no se cambia su
estructura, solo los datos de entrada; los bloques de ejes sobrantes se dejan en blanco).

## 1. Lectura del DXF de perfiles (convencion del proyectista)
- Perfiles a la izquierda (x < 2216 en el dibujo de Varones), secciones transversales a la derecha.
- Cada eje es una banda horizontal con su rotulo `EJE nn` (capa A-AREA-IDEN). Origen de progresivas en
  x = 2087.48; la cuneta arranca en x = 0.87 del dibujo. El eje horizontal del perfil esta en metros reales
  (1 unidad = 1 m); el vertical es solo esquematico.
- Lineas horizontales: color 5 (azul) = tramo abierto; color 84 (verde) = tramo tapado; color 6 (magenta) =
  losa de fondo. Las lineas vienen duplicadas (dos paralelas por tramo): unir por intervalos.
- Junto a cada `SECCION nn` (capa TEXTO) hay rotulos `NCT:` (nivel de piso), `NCF:` (cota de fondo),
  `H:` (altura interior medida desde el NCT), `EL:` (espesor losa), `EM:` (espesor muro). Los rotulos de
  seccion a veces estan desplazados 0.4 m: la numeracion de secciones es consecutiva dentro de cada eje.
- Guitarra (capa GRID_TEXT): progresivas `0+xx.xx`; la ultima es la longitud del eje. Los limites de tramo
  se ajustan a la progresiva rotulada mas cercana (tolerancia 0.15 m).
- Secciones transversales: cuneta 0.40 interior, muros 0.10, losa 0.10, tapa 0.10, ancho exterior 0.60;
  transversal 3/8" @0.25, longitudinal 3/8" @0.17 a 0.25 segun altura; tapa 3/8" @0.25 de 0.56 m.
- Pendiente 0.5 % (NCF baja 0.005 por metro). Si un rotulo NCF no cierra con la pendiente, avisar al
  usuario (Eje 04: el DXF decia 259.66 y el correcto es 260.42).

## 2. Reglas de metrado (confirmadas por el usuario)
- Altura H se mide desde el NCT, en abierta y en tapada. H(x) se interpola linealmente entre secciones.
- Area de muro por eje = integral de H a lo largo del eje (una cara). CONCRETO EN CUNETAS: MUROS area,
  espesor 0.10, cant. 2; LOSA longitud total x 0.60 x 0.10; TAPA longitud de tramos tapados x 0.60 x 0.10.
- ENCOFRADO: abierta: muro externo = (H + 0.10) x L, interno = H x L; tapada: externo = (H + 0.20) x L,
  interno = H x L, fondo de tapa = L x 0.40. Cant. 2 en muros.
- ACERO: solo donde H > 0.40 m. Los tramos tapados llevan acero siempre (cuerpo en U + tapa), aunque
  H < 0.40 (ej. Eje 01 tapada 13.20-19.20 con H 0.37). Un tramo abierto que pasa de 0.40 dentro de su
  longitud se metra desde la progresiva donde H = 0.40 (en Varones, la seccion a 20 m). Por tramo:
  longitud, Ø 3/8", separacion longitudinal por altura (0.20 si H < 0.45; 0.22 si < 0.60; 0.25 si mayor),
  barras longitudinales = REDONDEAR.MAS((0.60 + 2H)/sep) al inicio y al fin, transversal @0.25 con
  desarrollo 0.60 + 2(H + 0.05) inicio y fin; tapa: 3/8" @0.25, barra 0.56 (siempre), solo en TAPADA.
- CURADO y REJILLAS: todos los tramos (abiertos y tapados); rejilla solo cuenta en abiertos; descuentos de
  rejilla (puertas, cruces) se ingresan a mano.
- JUNTAS: cada 3.00 m, 2 muros, altura = area de muro / longitud (formula de la plantilla).
- PLANILLA GENERAL por eje: limpieza y trazo = L x 1.40; excavacion = L x 1.40 x (Hprom + 0.10 + solado);
  refine y solado = L x 0.60; relleno = L x 0.80 x (Hprom + 0.10 + solado); eliminacion = (exc - rell) x 1.20.
- Datos que NO salen del perfil y se piden al usuario: nombre del proyecto (RESUMEN!B5), tapas de registro
  en cunetas tapadas (PARAMETROS!B4), montantes por edificacion, red de piso y sumideros, dados, descuentos
  de rejilla.

## 3. Verificacion antes de entregar
- Recalcular con LibreOffice y buscar celdas con error (`#`).
- Comprobar el orden de elementos de cada hoja (legacyDrawingHF despues de rowBreaks) y reinyectar las
  imagenes de encabezado con `metrado_xlsx.reinyectar_vml`.
- Mostrar al usuario la tabla por eje (L, tramos, H inicio/fin, NCF) y los totales del RESUMEN.

## Cunetas que llegan a un colector frontal (aprendido en CAR Varones)
- Las cunetas dibujadas hasta la franja exterior terminan en la cara del muro lado predio del colector (o en el muro de la caja receptora). El tramo que caía dentro del colector se descuenta del último tramo del eje (`DESCUENTOS` en `herramientas/metrado_varones.py`, leídos de `entregables_varones/_calc/diseno.json`) y se documenta en la hoja "CUNETAS - LLEGADA AL COLECTOR".
- La partida del colector se agrega aparte (`herramientas/varones/metrado_v.py`) con hojas COLECTOR *, sin mezclar con las partidas de cunetas.
