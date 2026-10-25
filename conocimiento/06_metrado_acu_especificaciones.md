# 06 — Metrado, partidas Delphin, ACU, precios y especificaciones técnicas

Base de conocimiento permanente. Reúne todo lo aprendido desde el 03/10/2026 sobre cómo se metra, cómo se estructuran las
partidas en el formato Delphin, cómo se arman los análisis de costos unitarios (ACU), de dónde salen los precios y cómo se
redactan las especificaciones técnicas en los expedientes de drenaje pluvial del predio Los Mangos (Morales, San Martín) y de la
I.E. N.° 0590 Barranquita (Lamas).

Fuentes: mensajes del usuario (`conocimiento/_fuentes/mensajes_usuario.txt`), `BITACORA_CONVERSACION.md`, `CLAUDE.md`,
`insumos/solange/vigente/LEEME.txt`, `.claude/NOTAS_PROYECTO.md`, los skills `metrado-cunetas` y `diseno-colector-pluvial`, el
código de `herramientas/` y las planillas de `insumos/metrados_vigentes/` (leídas con openpyxl, solo lectura).

Convención de este documento: "dato" = celda amarilla editable de la planilla; "fórmula" = celda verde. Todas las cantidades
citadas son las de las planillas vigentes al 24/10/2026.

---

## 1. Reglas permanentes del usuario sobre metrados (no negociables)

| # | Regla | Desde | Por qué / cómo se aplica |
|---|---|---|---|
| 1 | No modificar los metrados del usuario salvo pedido expreso; cambiar solo lo pedido, sobre SU archivo, y comparar antes y después. | 03/10 (traspaso) y repetida siempre | El metrado ya está en el presupuesto Delphin y lo firman especialistas. Toda edición se verifica celda por celda tras recalcular. |
| 2 | No mezclar partidas sumando una en otra; no mezclar partidas ni láminas entre proyectos. | 03/10 05:31 | "sobre los metrados no vayas a mezclar las partidas sumando uno en otro". El colector va como partida aparte (01.04.04). |
| 3 | Nunca borrar lo que el usuario metró. | 03/10 20:41 | El usuario reclamó: "por qué borras todo mi metrado de la hoja concreto en cunetas y encofrado". Se agregan hojas nuevas (COLECTOR …) y no se tocan las existentes. |
| 4 | Integrar en la planilla del usuario, con su formato, colores y fórmulas, y justificar de dónde sale cada medida. | 03/10 20:09 | "agrega hojas donde salga el metrado del colector… preciso como sale cada medida exacto, utiliza mi formato colores… todo debe justificarse". Cada fila lleva columna SUSTENTO con lámina y criterio. |
| 5 | Las cunetas son del usuario: el colector no metra cunetas. | 03/10 17:24 | Se retiraron las partidas "prolongación de cunetas" que se habían puesto en el colector: "no se supone que ya he metrado yo mis cunetas y tú solo haces el colector?" |
| 6 | Rellenos menores (p. ej. base de un emboquillado) van DENTRO de la partida de relleno, no como partida aparte. | 03/10 (criterio del ingeniero de presupuesto) | Evita partidas sueltas pequeñas en Delphin. |
| 7 | Estructura y nombres de partidas = los de Delphin del CAR Mujeres (CUI 2717013); CANTIDADES siempre del metrado propio. | 06/10 23:52 | "están usando la misma base de datos de CAR Mujeres en Mujeres Violentadas, o sea la estructura y no las cantidades; ten en cuenta de ahora en adelante". |
| 8 | Metrado del CAR Mujeres CONGELADO. | 08/10 04:08 y siguientes | "En Mujeres Wilma ya no puedo mover porque ya está presupuestado". Solo se le agregan cosas pedidas (bancas 19/10) sin alterar lo demás. |
| 9 | Los planos se arreglan sin variar metrados. | 07/10 02:30, 08/10 00:40 | Al reordenar láminas se verifica que no cambia ni un número. |
| 10 | Mano de obra 2026 CAPECO-FTCCP: operario 28.95, oficial 22.68, peón 20.54 S/ hh. | 15/10 01:00 y 01:26 (PDF CAPECO) | "actualiza todo todo a 2026". Todas las ACU leen la hoja COSTO HORA HOMBRE 2026. |
| 11 | Precios reales comprobados, con su fuente. | 09/10 15:32-15:37 y 14/10 22:58 | "dame un precio real", "debe ser precio real comprobado; te doy acceso total a internet". Cada insumo lleva tienda / enlace / estado. |
| 12 | El ACU debe coincidir con los planos. | 14/10 23:57 | Las cantidades por unidad del ACU salen de la lámina de detalle (DD-03, DP-06B, DL-02…). |
| 13 | No preguntar lo que está en los planos. | 14/10 22:58 | "por qué me preguntas esto si tú sabes, tienes el plano, sabes por dónde entran vehículos…". |
| 14 | Sin nombre ni CIP del proyectista; nada que revele uso de IA; todo en español. | 08/10 04:35, 14/10 20:14 | Firmas y campos de proyectista en blanco. |
| 15 | Cambio de unidad pedido "solo en el Excel del ACU": el metrado original no cambia. | 15/10 15:01 | Partidas globales (glb) pasadas a metro/und solo en el libro de ACU. "Vale lo que es el Excel original". |
| 16 | Decir siempre "cota de fondo" (nunca "invert"). Citar proyectos por nombre y CUI. | 03/10 | También en metrados y especificaciones. |

---

## 2. Proyectos, planillas vigentes y generadores

| Proyecto | CUI | Alias del usuario | Planilla vigente (solo lectura) | Partida madre colector | Generadores de metrado/ACU |
|---|---|---|---|---|---|
| Hogar de Refugio Temporal "Mujeres Violentadas" | 2675514 | "de Solange" | `insumos/metrados_vigentes/METRADO_DRENAJE_MUJERES_VIOLENTADAS_CON_BANCAS_OC-01.xlsx` (la del usuario, con bancas; no trae las hojas de insumos/ACU). La versión con todas las hojas de análisis: `entregables/METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx` | 01.04.04 | `metrado_calc.py`, `metrado_xlsx.py`, `angulo_contramarco_refugio.py`, `acu_juntas_refugio.py`, `junta_*.py`, `mano_obra_2026_refugio.py`, `desagregado_lloraderos_refugio.py`, `acu_lloraderos_refugio.py`, `tapa_ciega.py`, `cotizacion_tapa_registro.py`, `acu_lija_thinner.py`, `bancas_oc01_en_planilla_refugio.py`, `renombrar_juntas_colector.py`, `render_tapa/add_acu_can.py` |
| CAR Varones | 2705619 | "de Katiuska" | `insumos/metrados_vigentes/METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx` (= metrado del 23-10-2026) | 01.04.04 | `metrado_varones.py` (cunetas desde el DXF), `varones/metrado_v.py` (colector), `varones/planilla_como_refugio.py` (parte A), `varones/portar_hojas_v.py` (parte B), `varones/codigos_laminas_metrado_v.py`, `varones/planilla_v.py` |
| CAR Mujeres | 2717013 | "de Wilma" | `insumos/metrados_vigentes/METRADO_DRENAJE_PLUVIAL_CAR_MUJERES.xlsx` — **congelado**; con bancas: `entregables_mujeres/METRADO_DRENAJE_PLUVIAL_CAR_MUJERES_09-10-2026_CON_BANCAS.xlsx` | 1.4.4.6 | `mujeres/bancas_en_planilla_m.py`, `techo/metrado_banca_m.py`, `mujeres/acu_globales_m.py`, `mujeres/acu_por_metro_m.py`, `mujeres/precios_globales_m.py` |
| I.E. N.° 0590 Barranquita | C.I. 468901 (confirmar CUI) | – | `entregables_barranquita/METRADO_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.xlsx` (generado) | 01 (solo cunetas) | `barranquita/cantidades_b.py`, `barranquita/metrado_b.py` |

Los alias de persona solo sirven para entender al usuario en la conversación: en los documentos se cita siempre por nombre del
proyecto y CUI.

---

## 3. Estructura de partidas Delphin

### 3.1 Origen y criterio (06-07/10/2026)
- El 06/10 el usuario entregó su metrado vigente del Hogar de Refugio ("grábatelo") y un archivo COMPARATIVO que le envió el
  ingeniero de presupuesto (Delphin), quien pidió corregir NOMBRES de partidas para que coincidan con Delphin.
- En la oficina el Delphin del Hogar de Refugio usa la estructura de partidas del CAR Mujeres (mismos nombres, códigos y
  agrupación). Criterio escrito en `insumos/solange/vigente/LEEME.txt`:
  - los nombres de Delphin son la referencia de redacción; las diferencias de cantidad son normales;
  - solo se cambian nombres cuando la obra es la misma; si la partida describe otra obra (dimensión, material, espesor, unidad)
    o no existe en el proyecto, se consulta antes.
- 07/10: 39 celdas de nombres adaptadas y unidad `ml` → `m` en rejilla y junta de cunetas; los 55 totales del RESUMEN iguales.
- 07/10: concreto del colector unificado en una sola partida (Delphin usa una): 01.04.04.04.01 = losa de fondo + muros + losa
  superior (en ese momento 58.31 m³ = 13.06 + 35.86 + 9.39). La PLANILLA mantiene el sustento completo bajo la partida única con
  subtítulos "Losa de fondo", "Muros:", "Losa superior"; COLECTOR INSUMOS conserva el desglose por elemento.
- 07/10: registros en una sola partida por und (pedido del ingeniero de presupuesto, como Delphin): las 7 partidas por
  componente (contramarco, marco, ángulos, tapa, concreto, acero, pintura) pasan a 01.04.04.05.01 TAPA DE REGISTRO … (und); el
  detalle va en la hoja DESAGREGADO TAPA REGISTRO y el costo en ACU TAPA REGISTRO.
- Pregunta del usuario (06/10 23:57) sobre el solado: en el CAR Mujeres el solado de cunetas es E = 4" (0.10 m); el del colector
  es E = 2" (0.05 m). Ambos nombres se conservan.
- 15/10 (tarde): el CAR Varones toma los mismos nombres y estructura del Refugio, manteniendo sus cantidades
  (`varones/planilla_como_refugio.py`, diccionario `NOMBRES`).

Renombres aplicados a Varones (código: nombre Delphin): 01.04.03.02.04 RELLENO COMPACTADO C/MATERIAL PROPIO SELECCIONADO;
01.04.03.02.05 ELIMINACIÓN DE MATERIAL EXCEDENTE D<1Km; 01.04.03.04.02.01 CONCRETO f'c=175 kg/cm2 PARA CUNETAS; 01.04.03.04.02.02
ENCOFRADO Y DESENCOFRADO DE CUNETAS; 01.04.03.04.03.01 REJILLA METALICA P/CUNETA C/PL 1''x 3/16'' Y ANGULO 1'' x 1'' x 3/16'',
S/DETALLE; 01.04.03.05.01.01 MONTANTE CON TUBERÍA PVC DE 4"; 01.04.03.05.02.01 TUBERIA DESAGÜE PVC-CP Ø4"; 01.04.03.05.02.03 CODO
DESAGÜE PVC Ø4" x 90°; 01.04.03.05.02.04 TEE SANITARIA DESAGÜE PVC Ø4"; 01.04.04.02.01 EXCAVACIÓN MANUAL DE ZANJAS P/COLECTOR;
01.04.04.03.01 CONCRETO f'c=100 kg/cm2 PARA SOLADO E=2''. Unidad `m` en 01.04.03.04.03.01 y .03.03.

### 3.2 Árbol de partidas del Hogar de Refugio (RESUMEN vigente, con bancas OC-01)

| Ítem | Descripción | Und | Total |
|---|---|---|---|
| 01.04.03 | SISTEMA DE DRENAJE PLUVIAL | | |
| 01.04.03.01 | TRABAJOS PRELIMINARES | | |
| 01.04.03.01.01 | LIMPIEZA MANUAL DE TERRENO | m² | 956.87 |
| 01.04.03.01.02 | TRAZO, NIVELES Y REPLANTEO PRELIMINAR | m² | 956.87 |
| 01.04.03.02 | MOVIMIENTO DE TIERRAS | | |
| 01.04.03.02.01 | EXCAVACIÓN MANUAL DE ZANJAS P/CUNETAS | m³ | 619.80 |
| 01.04.03.02.02 | EXCAVACIÓN MANUAL DE ZANJAS P/DADOS DE CONCRETO | m³ | 2.91 |
| 01.04.03.02.03 | REFINE, NIVELACIÓN Y COMPACTACIÓN EN TERRENO NORMAL | m² | 410.09 |
| 01.04.03.02.04 | RELLENO COMPACTADO C/MATERIAL PROPIO SELECCIONADO | m³ | 343.77 |
| 01.04.03.02.05 | ELIMINACIÓN DE MATERIAL EXCEDENTE D<1Km | m³ | 331.23 |
| 01.04.03.03 | OBRAS DE CONCRETO SIMPLE | | |
| 01.04.03.03.01 | CONCRETO f'c=100 kg/cm2 PARA SOLADO E=4'' | m² | 410.09 |
| 01.04.03.03.02 | CONCRETO f'c=140 Kg/cm2 PARA DADOS DE CONCRETO | m³ | 2.91 |
| 01.04.03.04 | OBRAS DE CONCRETO ARMADO | | |
| 01.04.03.04.02 | CUNETAS | | |
| 01.04.03.04.02.01 | CONCRETO f'c=175 kg/cm2 PARA CUNETAS | m³ | 122.65 |
| 01.04.03.04.02.02 | ENCOFRADO Y DESENCOFRADO DE CUNETAS | m² | 1,661.96 |
| 01.04.03.04.02.03 | ACERO f'y=4200 kg/cm2 PARA CUNETA | kg | 4,967.05 |
| 01.04.03.04.02.04 | CURADO DE CONCRETO EN CUNETA | m² | 1,084.21 |
| 01.04.03.04.03 | VARIOS | | |
| 01.04.03.04.03.01 | REJILLA METALICA P/CUNETA C/PL 1''x 3/16'' Y ANGULO 1'' x 1'' x 3/16'', S/DETALLE | m | 510.11 |
| 01.04.03.04.03.02 | TAPA DE INSPECCION 0.60m x 0.60m | und | 17 |
| 01.04.03.04.03.03 | JUNTA DE DILATACION E=1" CON SELLADOR ASFALTO | m | 335.16 |
| 01.04.03.04.03.04 | LLORADERO DE TUBERIA PVC Ø3" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m (CUNETA COLINDANTE CON AREA VERDE) | und | 157 |
| 01.04.03.05 | RED DE COLECCIÓN | | |
| 01.04.03.05.01 | RED DE RECOLECCION TECHO | | |
| 01.04.03.05.01.01 | MONTANTE CON TUBERÍA PVC DE 4" | m | 443.22 |
| 01.04.03.05.01.02 | FALSA COLUMNA P/MONTANTE DE 0.20m x 0.15m x 1.30m | und | 52 |
| 01.04.03.05.01.02.01 | CONCRETO F´C=175 KG/CM2 EN FALSA COLUMNA | m³ | 2.028 |
| 01.04.03.05.01.02.02 | ENCOFRADO Y DESENCOFRADO EN FALSA COLUMNA - MONTANTE PLUVIAL | m² | 33.80 |
| 01.04.03.05.01.02.03 | ACERO FY=4200 KG/CM2 EN FALSA COLUMNA (MONTANTE PLUVIAL) | kg | 291.78 |
| 01.04.03.05.01.03 | CANALETA DE PLANCHA DE ACERO GALVANIZADO e=0.9mm, SECCIÓN 0.25m x 0.20m | m | 513.98 |
| 01.04.03.05.01.04 | SOPORTE DE PLATINA F°G° 1" x 1/8" P/CANALETA | und | 884 |
| 01.04.03.05.01.05 | TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA | und | 40 |
| 01.04.03.05.01.06 | BOQUILLA DE PLANCHA GALVANIZADA P/CONEXIÓN DE CANALETA A MONTANTE Ø4" | und | 52 |
| 01.04.03.05.02 | RED DE RECOLECCION PISO | | |
| 01.04.03.05.02.01 | TUBERIA DESAGÜE PVC-CP Ø4" | m | 112.56 |
| 01.04.03.05.02.02 | SUMIDERO METALICO C/PLATINA 1" X 3/16" | und | 30 |
| 01.04.03.05.02.03 | CODO DESAGÜE PVC Ø4" x 90° | und | 24 |
| 01.04.03.05.02.04 | TEE SANITARIA DESAGÜE PVC Ø4" | und | 4 |
| 01.04.03.05.03 | ACCESORIOS | | |
| 01.04.03.05.03.02 | CODO DESAGÜE PVC Ø4" x 90° | und | 189 |
| 01.04.03.05.03.04 | COLGADOR F°G° P/TUBERIA PVC Ø4" | und | 99 |
| 01.04.03.05.03.05 | ABRAZADERA DE F°G° P/TUBERIA PVC Ø4" | und | 79 |
| 01.04.03.05.04 | RED DE RECOLECCION TECHO DE BANCAS CON PERGOLA (OC-01) | | |
| 01.04.03.05.04.01 | CANALETA DE PLANCHA DE ACERO GALVANIZADO e=0.50mm, SECCIÓN 0.18m x 0.21m | m | 35.37 |
| 01.04.03.05.04.02 | SOPORTE DE PLATINA F°G° 1" x 1/8" P/CANALETA | und | 18 |
| 01.04.03.05.04.03 | TAPA LATERAL DE PLANCHA GALVANIZADA P/CANALETA | und | 18 |
| 01.04.03.05.04.04 | BOQUILLA DE PLANCHA GALVANIZADA P/CONEXIÓN DE CANALETA A TUBERIA PVC Ø4" | und | 9 |
| 01.04.04 | COLECTOR PLUVIAL FRONTAL (TRAMO HOGAR DE REFUGIO - EMPALME CON CAR MUJERES) | | |
| 01.04.04.01.01 | LIMPIEZA MANUAL DE TERRENO | m² | 125.85 |
| 01.04.04.01.02 | TRAZO, NIVELES Y REPLANTEO PRELIMINAR | m² | 125.85 |
| 01.04.04.02.01 | EXCAVACIÓN MANUAL DE ZANJAS P/COLECTOR | m³ | 164.89 |
| 01.04.04.02.02 | REFINE, NIVELACIÓN Y COMPACTACIÓN EN TERRENO NORMAL | m² | 93.94 |
| 01.04.04.02.03 | RELLENO COMPACTADO C/MATERIAL PROPIO SELECCIONADO | m³ | 82.77 |
| 01.04.04.02.04 | ELIMINACIÓN DE MATERIAL EXCEDENTE D<1Km | m³ | 98.55 |
| 01.04.04.03.01 | CONCRETO f'c=100 kg/cm2 PARA SOLADO E=2'' | m² | 93.94 |
| 01.04.04.04 | OBRAS DE CONCRETO ARMADO - COLECTOR Y CAJAS | | |
| 01.04.04.04.01 | CONCRETO f'c=210 kg/cm2 PARA COLECTOR | m³ | 58.43 |
| 01.04.04.04.02 | ENCOFRADO Y DESENCOFRADO DE COLECTOR | m² | 585.23 |
| 01.04.04.04.03 | ACERO f'y=4200 kg/cm2 PARA COLECTOR | kg | 3,056.45 |
| 01.04.04.04.04 | ACABADO FROTACHADO DE LOSA SUPERIOR (VEREDA) | m² | 86.06 |
| 01.04.04.04.05 | CURADO DE CONCRETO EN COLECTOR | m² | 390.60 |
| 01.04.04.05.01 | TAPA DE REGISTRO CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08 | und | 10 |
| 01.04.04.06.01 | JUNTA DE DILATACION E=1" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR | m | 100.64 |
| 01.04.04.06.02 | JUNTA E=1" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO | m | 58.81 |

Notas: el subtítulo 01.04.03.04.01 no existe (la numeración salta a .04.02 porque así es la base Delphin); en ACCESORIOS
existen .03.02, .03.04 y .03.05 (los huecos son de la base). No renumerar.

### 3.3 CAR Varones: diferencias con el Refugio
Mismo árbol 01.04.03 (sin bancas OC-01) y colector 01.04.04 "COLECTOR PLUVIAL FRONTAL (TRAMO CAR VARONES - EMPALME CON LA CAJA CL
DEL HOGAR DE REFUGIO)". Subtítulo 01.04.04.04 "OBRAS DE CONCRETO ARMADO - COLECTOR" (sin cajas propias: la CL es del Refugio).

| Ítem | Descripción | Und | Total |
|---|---|---|---|
| 01.04.03.01.01 / .02 | Limpieza / trazo | m² | 753.54 |
| 01.04.03.02.01 | Excavación p/cunetas | m³ | 513.91 |
| 01.04.03.04.02.01 | Concreto f'c=175 cunetas | m³ | 94.14 |
| 01.04.03.04.02.02 | Encofrado cunetas | m² | 1,245.92 |
| 01.04.03.04.02.03 | Acero cunetas | kg | 3,354.73 |
| 01.04.03.04.03.01 | Rejilla | m | 373.85 |
| 01.04.03.04.03.02 | Tapa de inspección 0.60 x 0.60 | und | 18 |
| 01.04.03.04.03.03 | Junta de dilatación cunetas | m | 252.29 |
| 01.04.03.04.03.04 | Lloradero PVC Ø3" | und | 226 |
| 01.04.04.04.01 | Concreto f'c=210 colector | m³ | 55.75 |
| 01.04.04.04.02 | Encofrado colector | m² | 538.31 |
| 01.04.04.04.03 | Acero colector | kg | 2,523.84 |
| 01.04.04.04.04 | Acabado frotachado de losa superior (vereda) | m² | 94.76 |
| 01.04.04.04.05 | Curado colector | m² | 368.27 |
| 01.04.04.05.01 | TAPA DE REGISTRO CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08 | und | 11 |
| 01.04.04.06.01 | Junta de dilatación colector | m | 120.64 |
| 01.04.04.06.02 | JUNTA E=1" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CAJA CL | m | 4.64 |

- No existe 01.04.04.06.03 EMPALME DE CUNETA: el 08/10 la usuaria la quitó a propósito ("por qué hay empalme si ya he considerado
  su proyección hasta el colector de todas"). Cada cuneta se metra hasta el muro del colector (acortamientos de 0.04, 0.10, 0.26,
  3.39 y 2.77 m, hoja CUNETAS - LLEGADA AL COLECTOR). La DD-04 queda solo como detalle constructivo.
- No hay cerco en el frente del CAR Varones (corrección del 04/10 17:03): a ambos lados del colector hay terreno natural, por eso la
  junta 01.04.04.06.02 solo mide el contacto con la caja CL (perímetro de la sección 4.64 m).

### 3.4 CAR Mujeres (congelado): partidas del colector
| Ítem | Descripción | Und | Total |
|---|---|---|---|
| 1.4.4.6.1.1 / .2 | Limpieza / trazo | m² | 255.36 |
| 1.4.4.6.2.1 | Excavación p/colector | m³ | 180.66 |
| 1.4.4.6.2.2 | Refine | m² | 239.50 |
| 1.4.4.6.2.3 | Relleno compactado | m³ | 10.20 |
| 1.4.4.6.2.4 | Eliminación (factor 1.25) | m³ | 213.07 |
| 1.4.4.6.3.1 | Solado E=2'' | m² | 237.94 |
| 1.4.4.6.3.2 | CONCRETO CICLÓPEO f'c=140 kg/cm2 + 30% P.M. PARA UÑA | m³ | 0.52 |
| 1.4.4.6.4.1.1 | Concreto f'c=210 colector | m³ | 65.56 |
| 1.4.4.6.4.1.2 | Encofrado colector | m² | 490.72 |
| 1.4.4.6.4.1.3 | Acero colector | kg | 4,140.49 |
| 1.4.4.6.4.1.4 | Curado colector | m² | 919.70 |
| 1.4.4.6.4.1.5 | Acabado frotachado de losa superior (vereda) | m² | 128.90 |
| 1.4.4.6.4.2.1 a .4 | Estructura de salida con aleros: concreto 0.41 m³, encofrado 4.10 m², acero 18.23 kg, emboquillado de piedra e=0.20 1.56 m² | | |
| 1.4.4.6.5.1 | TAPA DE REGISTRO 0.68x0.68 C/MARCO Y CONTRAMARCO | und | 15 |
| 1.4.4.6.5.2 | JUNTA DE DILATACION E=1" CON SELLADOR ASFALTO | m | 162.69 |
| 1.4.4.6.5.3 | JUNTA E=1" CON TECNOPOR ENTRE COLECTOR Y PISO ADYACENTE | m | 78.42 |

El metrado del CAR Mujeres conserva la tapa con marco y contramarco (hojas PLANILLA TAPAS COLECTOR y METRADO ACERO COLECTOR); solo
su lámina DP-06B / D-RL dibuja la tapa ciega. Pendiente de decisión del usuario (no se tocó).

### 3.5 Código del metrado frente al código Delphin del ACU
Las ACU se rotulan con el código de la base Delphin (estructura del CAR Mujeres), que puede diferir del código del metrado propio:

| Partida | Código en el metrado del Refugio/Varones | Código Delphin del ACU |
|---|---|---|
| Tapa de registro | 01.04.04.05.01 | 01.04.04.06.05.01 (= 1.4.4.6.5.1 del CAR Mujeres) |
| Juntas del colector | 01.04.04.06.01 / .02 | 01.04.04.06.01 / .02 |
| Canaletas | 01.04.03.05.01.03 a .06 | mismos |
| Lloraderos | 01.04.03.04.03.04 | mismo |

Cada hoja ACU escribe ambos: "Partida" (Delphin) y "Partida del metrado".

### 3.6 Versión rechazada (03/10) para no repetir
El primer metrado del colector traía un subtítulo "01.04.04.06 JUNTAS, EMPALMES Y PROLONGACION DE CUNETAS" con: junta de
dilatación con sellador elastomérico (100.30 m), junta de tecnopor entre colector, cerco y piso (209.78 m), empalme de cuneta (6
und), concreto, encofrado, acero y tapa de prolongación de cunetas 0.40 x H. El usuario lo objetó: las prolongaciones son
cunetas (ya metradas por él). Hoy el subtítulo es solo "JUNTAS" con dos partidas.

### 3.7 I.E. 0590 Barranquita (solo red de cunetas; estructura y nombres del CAR Mujeres)
01 SISTEMA DE DRENAJE PLUVIAL - RED DE CUNETAS; 01.01.01 limpieza y 01.01.02 trazo (m²); 01.02.01 excavación, .02 refine, .03
relleno, .04 eliminación, .05 PERFILADO MANUAL DE TERRENO EN DESCARGAS (m², partida propia de las descargas por el cerco);
01.03.01 solado E=4''; 01.04.01.01 a .04 concreto f'c=175, encofrado, acero, curado de cunetas; 01.04.02.01 rejilla (m),
.02 tapa de inspección 0.60 x 0.60 (und), .03 junta de dilatación E=1" con sellador asfalto (m), .04 JUNTA E=1" CON SELLADOR
ASFALTICO ENTRE CUNETA Y PISO ADYACENTE (m). 16 partidas con fórmulas; valores de referencia (bitácora 21/10): concreto 150.74 m³,
acero 6,545 kg, rejilla 924.82 m, 10 tapas, juntas 547.80 m, junta con el piso 748.76 m. Fuera del alcance: canaletas y montantes
(especialidad de techos) y la protección de la entrega D2 fuera del cerco.

---

### 3.8 Programa DRENIE (24-10-2026)
`drenie_motor/drenie_motor/metrado.py`: metrado general con fórmulas para cualquier proyecto, estructura Delphin del Refugio
(01 SISTEMA DE DRENAJE PLUVIAL; .01 preliminares; .02 movimiento de tierras con dados y perfilado en descargas; .03 solado y dados;
.04.02 cunetas; .04.03 varios con rejilla, tapas, juntas, lloraderos y junta cuneta-piso; .05 red de colección: techo con montante,
falsa columna y sus 3 subpartidas, canaleta, soporte, tapa lateral y boquilla; piso con tubería, sumidero, codo y tee; accesorios
con codo, colgador y abrazadera). Cada eje con su ancho libre b (una medida por sector). Barranquita (red del programa): concreto
151.43 m³, acero 6,932 kg, rejilla 936.22 m, 30 tapas, juntas 544.25 m, 344 lloraderos, 124 montantes (635.18 m), canaleta
925.76 m, 2 sumideros (22.15 m de tubo). Junta cuneta-piso 1,416.50 m (ambos lados contra cualquier piso): pendiente de revisar.
DRENIE no hace ACU, precios ni presupuesto (regla del usuario, 24-10-2026): eso lo ve quien elabora el presupuesto.
Revisión general automática (24-10-2026): `drenie_motor/drenie_motor/revision.py` corre las validaciones de la sección 8.2 de
`01_reglas_y_metodo.md` al final de cada diseño y entrega REVISION_GENERAL.xlsx. Montantes: a lo más 4 de 4" por lado (si con
llenado 1/4 harían falta más, 4 con llenado hasta 7/24). Sumidero cuyo tubo no llega sobre la cota de fondo: se profundiza el
tramo de cuneta que lo recibe (también al inicio del eje) y se recalcula. Guitarra de perfiles: textos horizontales y la
pendiente de diseño del tramo (no la de cotas redondeadas al mm).
Juego completo de DRENIE (24-10-2026): planta, cuadros, perfiles, secciones, una lámina 1/25 por descarga (planta, perfil e
isométrico), 3 láminas de detalles a escala real (rejilla, tapa y juntas 1/5; lloradero, falsa columna, canaleta y sumidero 1/5;
montante en elevación y muro con lloraderos 1/10), PNG por lámina, memoria de cálculo Excel con fórmulas, carátulas e índice de
planos en Word; la revisión general comprueba que cada entregable exista.
El programa entrega metrado, memorias (hidrológica y descriptiva), especificaciones técnicas y planos.
Alcance de DRENIE en techos (usuario, 25-10-2026): ubica los montantes (esquinas) y metra canaletas, soportes de platina
1" × 1/8", tapas laterales, boquillas, falsa columna 0.20 × 0.15 × 1.30 (concreto, encofrado y acero), dados, y por cada montante
el codo de 90° de 4" del dado y la tubería PVC 4" embebida del dado a la cuneta (máximo 5 m, S 1 %, mínimo 0.5 %). La altura del
montante, el tubo que sube a la canaleta, codos del desvío, colgadores y abrazaderas los mete el proyectista (dependen de los cortes
de arquitectura); las rejillas, tramos tapados y áreas verdes los confirma el proyectista.
Llegada de tuberías a la cuneta (usuario, 25-10-2026): el fondo del tubo (montante o sumidero) llega sobre el nivel del agua de la
cuneta (cota de fondo + tirante) + 0.05 m; si llega a la cota de fondo, al llover el tubo queda ahogado, el agua se empoza y regresa.
Si no se da, se busca la salida (0.5 %, tubo más alto, otra cuneta, profundizar el tramo como último recurso).
DRENIE como programa que propone soluciones (usuario, 25-10-2026): no esconder lo que no pudo resolver; mostrarlo en una ventana
(qué pasó, dónde, por qué) con soluciones para elegir (aplicar automática, «lo hago a mano», confirmar, «lo analizo después»).
Ventana en el visor (JavaScript); motor en Python; se comunican por JSON (resultado.json → observaciones; ediciones.json →
soluciones elegidas). Terreno sin salida por gravedad: se calcula y se verifica cuánto subir el NPT. Batería de pruebas
(`drenie_motor/pruebas/`) antes de entregar cualquier versión: ninguna caída ni falla sin explicar.
Planteamiento de cunetas (usuario, 25-10-2026): la cuneta puede ir a lo largo del alero o transversal (por los lados cortos,
recibiendo los montantes de las esquinas, como en el CAR Varones); lo que importa es que el tubo de cada montante llegue. Se busca
el menor uso de cunetas largas (salen muy profundas o no llegan) y que empiecen lo menos profundas posible. Primero edificaciones
y losa deportiva; después entradas y obras exteriores. En el CAR Varones se deja el planteamiento de la usuaria.

## 4. Hojas de la planilla y su función

### 4.1 Orden de hojas (planilla completa del Refugio / Varones)
RESUMEN · PLANILLA GENERAL DE METRADOS · CONCRETO EN CUNETAS · ENCOFRADO Y DESENCOFRADO · METRADO MONTANTES · METRADO EN PISO
(SUMIDERO) · METRADO CANALETAS · [METRADO CANALETA BANCAS] · METRADO ACERO · METRADO DE CURADO · METRADO DE REJILLAS · METRADO JUNTA DE
DILATACION · METRADO LLORADEROS · PLANILLA TAPAS REGISTRO INTERNO · [CUNETAS - LLEGADA AL COLECTOR] (Varones) · PARAMETROS · Listas ·
COLECTOR PARAMETROS · COLECTOR MOV. TIERRAS · COLECTOR CONCRETO · COLECTOR ENCOFRADO · COLECTOR ACERO · COLECTOR REGISTROS Y TAPAS ·
COLECTOR JUNTAS Y EMPALMES · COLECTOR INSUMOS · ACU TAPA REGISTRO · ACU CANALETAS · DESAGREGADO TAPA REGISTRO · ACU JUNTA DILATACION ·
ACU JUNTA CERCO (Refugio) / ACU JUNTA CAJA CL (Varones) · DESAGREGADO LLORADEROS · COSTO HORA HOMBRE 2026 · ACU LLORADEROS.

El nombre "METRADO  EN PISO (SUMIDERO)" lleva DOS espacios (así está en la plantilla; respetar al referenciar).

CAR Mujeres: RESUMEN, PLANILLA GENERAL, METRADO MONTANTES, CONCRETO EN CUNETAS, ENCOFRADO, METRADO CANALETAS, [METRADO CANALETA
BANCAS], METRADO EN PISO, METRADO ACERO, METRADO JUNTA DE DILATACION, METRADO DE CURADO, METRADO DE REJILLAS, PLANILLA TAPAS
REGISTRO INTERNO, PLANILLA TAPAS COLECTOR, METRADO ACERO COLECTOR, PARAMETROS, Listas.

Barranquita: CARÁTULA, RESUMEN, PLANILLA GENERAL, CONCRETO EN CUNETAS, ENCOFRADO, METRADO ACERO, METRADO JUNTA DE DILATACION,
METRADO DE CURADO, METRADO DE REJILLAS, PLANILLA TAPAS INSPECCION, PARAMETROS, Listas.

### 4.2 Encabezado común
Todas las hojas de detalle repiten ENTIDAD, PROYECTO, UBICACIÓN y FECHA con fórmulas `=+RESUMEN!B4`, `B5`, `B6`, `B7`
(en algunas, columna C). RESUMEN: B4 = "GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO", B5 = nombre del proyecto "…, con CUI N.° …",
B6 = "SAN MARTIN - SAN MARTIN - MORALES", B7 = fecha 01/09/2026 (setiembre 2026). El nombre del proyecto se cambia en un solo
lugar (RESUMEN!B5).

### 4.3 RESUMEN
Columnas: Item · Descripción · Unid. · Total. Los totales son fórmulas a la columna K de la PLANILLA GENERAL. Títulos sin unidad.
Al agregar o quitar partidas se desplazan filas y se corrigen referencias (ver §16).

### 4.4 PLANILLA GENERAL DE METRADOS
Columnas (fila 8): A ITEM · B DESCRIPCION · C Nº DE VECES · D LARGO · E ANCHO · F ALTURA · G FACT. · H AREA · I VOLUMEN · J PARCIAL ·
K TOTAL · L UND. Formato pedido el 03/10 ("Nº veces, largo, ancho, alto, parcial, total"). Cada partida: fila del ítem con
`K = SUM(J…)` y filas de sustento por eje o tramo con `J = C*D*E(*F)` o `J = 'hoja'!celda`.

### 4.5 Hojas de cunetas
- CONCRETO EN CUNETAS: dos columnas de ejes (B-G y J-N). Por eje: MUROS (AREA = integral de H por el eje, ESPESOR 0.10, CANT. 2)
  → `F = E10*E11*E12`; LOSA (ESPESOR 0.10, LONGITUD total, ANCHO 0.60); TAPA (LONGITUD de tramos tapados, ESPESOR 0.10, ANCHO
  0.60); total por eje `G = SUM(F10:F18)`.
- ENCOFRADO Y DESENCOFRADO: por eje, ABIERTA (MURO EXTERNO área x 2, MURO INTERNO área x 2) y TAPADO (MURO EXTERNO x 2, MURO INTERNO
  x 2 + TAPA = L_tapado x 0.40); total `H = SUM(G…)`.
- METRADO ACERO: una fila por tramo (columnas A..AG, §5.3).
- METRADO DE CURADO: por tramo, `I = (G+H)/2`, `J = 2*E*I` (2 muros), `K = E*F` (fondo), `L = SI(TAPADA; E*F; 0)`, `M = SUMA`,
  `N = SI(TAPADA;4;3)` caras.
- METRADO DE REJILLAS: por tramo, `G = SI(ABIERTA; MAX(E−F;0); 0)` (F = descuento sin rejilla, a mano).
- METRADO JUNTA DE DILATACION: parámetros B8 espaciamiento 3.00, B9 muros con junta 2, B10 ancho interior del fondo 0.40; por eje
  D longitud, E área de muro (`='CONCRETO EN CUNETAS'!E10`), F = E/D (altura media), H = REDONDEAR.MAS(D/G;0), I = $B$9*F+$B$10,
  J = H*I; total J12. Notas al pie con el sustento EG-2013.
- METRADO LLORADEROS: N° · EJE · PROGRESIVA DEL TRAMO · LADO DEL MURO · LONGITUD JUNTO A ÁREA VERDE · ESPACIAMIENTO 1.50 ·
  `G = REDONDEAR.MAS(E/F;0)` · und; fila "TOTAL DE LLORADEROS".
- PLANILLA TAPAS REGISTRO INTERNO: tapa de inspección de cunetas tapadas (§5.8).
- CUNETAS - LLEGADA AL COLECTOR (Varones): longitud dibujada, acortamiento, longitud metrada `E = C − D`, "termina en", sustento.
- PARAMETROS: tapa de cuneta (B4 cantidad, B5 0.60, B6 0.60, B7 0.10, B8 recubrimiento 0.025, B9 separación 0.15, B10 peso 3/8"
  0.56, B11 barra 9 m); movimiento de tierras (B15 espesor de solado sumado a excavación y relleno 0.10; B16 esponjamiento 1.20).
- Listas: factores kg/m (6 mm 0.222; 8 mm 0.395; 3/8" 0.56; 12 mm 0.888; 1/2" 0.994; 5/8" 1.552; 3/4" 2.235; 1" 3.973), tipos de
  cuneta (ABIERTA, TAPADA) y criterio de conteo (TEÓRICO L/s+1 o ENTERO redondeo arriba, celda X1 de METRADO ACERO).

### 4.6 Hojas del colector (agregadas por `metrado_xlsx.py` / `varones/metrado_v.py`)
- COLECTOR PARAMETROS: N° · PARÁMETRO · VALOR · UND · SUSTENTO (lámina / norma / criterio). Varones (fila: valor): b 0.60; muro
  0.15; fondo 0.15; losa sup. 0.10; losa camión 0.25; solado 0.05; NPT 261.15; sobreancho 0.25 (zanja 1.40 = 0.90 + 2 x 0.25);
  franja de relleno 1.00; recubrimiento 0.04 (E.060 tabla 7.7.1); 3/8" 0.56; 1/2" 0.994; traslape 0.40 (E.060 12.15); barra 9.00;
  ganchos 0.30; esponjamiento `=PARAMETROS!B16`; marcos @0.20 normal y @0.15 camión; longitudinales @0.25 y @0.20; 11 registros;
  tapa 0.68; espesor 0.08; rebaje 0.70; luz 0.60; perímetro encofrado tapa 2.72; 2 asas; desarrollo 0.50; holgura 0.01; bisel
  0.01; borde engrosado `=2*b` (1.20); sección del borde 0.015 m²; cota de fondo 260.20 y 259.884; juntas cada 4; altura interior
  máxima 1.17; progresiva final 105.29; quiebre 100.90; ancho del muro de la CL 1.30. Refugio: b 0.80, zanja 1.60, L 69.89,
  NPT 260.60, cota de fondo 259.10 → 258.89, 10 registros, 17 juntas, hmax 1.61, más los datos de las cajas CL y CC.
- COLECTOR MOV. TIERRAS, CONCRETO, ENCOFRADO, ACERO: una fila por tramo homogéneo (zona NORMAL / MOTOS / CAMION / diagonal / final)
  con h y Hz medios ponderados; fórmulas en §6. Cada hoja empieza con una fila "Criterio:" (A7) que explica la regla.
- COLECTOR REGISTROS Y TAPAS: lista de registros (RS-xx / RV-xx, progresiva, ubicación, 1 und, sustento) y bloque "METRADO DE LAS
  PARTIDAS DE REGISTROS" (§7).
- COLECTOR JUNTAS Y EMPALMES: junta de dilatación, junta longitudinal (cerco / CL) y empalmes de cuneta (§8).
- COLECTOR INSUMOS: ratios por unidad de partida para las ACU (§13.4).

### 4.7 Hojas de análisis (ACU y desagregados)
- COSTO HORA HOMBRE 2026 (§13.2); ACU TAPA REGISTRO; ACU CANALETAS; ACU JUNTA DILATACION; ACU JUNTA CERCO / CAJA CL; ACU LLORADEROS;
  DESAGREGADO TAPA REGISTRO; DESAGREGADO LLORADEROS. Estructura común: encabezado (título en banda, filas 2-5 copiadas del RESUMEN,
  nota explicativa en A7), "1. CANTIDADES POR …" (tabla N° · CONCEPTO · UND · VALOR · SUSTENTO) y "2. ANALISIS DE COSTO UNITARIO
  (formato Delphin)".

### 4.8 Formato y colores (planilla del usuario)
Letra Arial Narrow; cabeceras azules con letra blanca; dato en amarillo claro (FFF2CC); fórmula en verde claro (F0F7E8 / estilo 306);
unidad en gris (F2F2F2); zona/tipo en lila (E4DFEC); total de fila naranja (F4B183); barra de totales azul oscuro (17365D);
subtítulos celeste (D9EAF7). En las hojas nuevas se clonan los estilos de la ACU TAPA REGISTRO (índices de estilo 277, 281-296,
306 y un amarillo de 4 decimales creado con `estilo_amarillo4`). Fórmulas en español con separador ";" (REDONDEAR, SUMA, SI) cuando
el usuario las ve en Excel en español (en el XML se guardan en inglés con ",").

---

## 5. Cómo se mide cada partida de cunetas (criterio confirmado por el usuario)

### 5.1 Lectura del perfil
- Altura H medida desde el NCT (nivel de piso terminado) hasta la cota de fondo NCF, en tramo abierto y tapado (04/10 05:35).
  H(x) se interpola linealmente entre secciones. Área de muro por eje = ∫H dx (una cara).
- Sección típica: 0.40 interior, muros 0.10, losa de fondo 0.10, tapa 0.10, ancho exterior 0.60. Pendiente 0.5 %.
- Convención de colores del DXF de perfiles (CAR Varones): azul = tramo abierto; verde = tramo tapado; magenta = losa de fondo y
  barras transversales; círculos azules = acero de 3/8" en tramo tapado. Rótulos "NCT:", "NCF:", "H:" junto a "SECCION nn";
  progresivas "0+xx.xx" en la guitarra; eje horizontal en metros reales. Si un plano no sigue la convención, el programa avisa
  qué no pudo leer en lugar de inventar (04/10 05:43).
- Errores de rótulo se avisan: Eje 04 de Varones decía NCF 259.66; el correcto es 260.42 (el usuario lo confirmó y corrigió).

### 5.2 Concreto, encofrado, curado
| Partida | Fórmula |
|---|---|
| Concreto muros | ∫H dx x 0.10 x 2 |
| Concreto losa de fondo | L_eje x 0.60 x 0.10 |
| Concreto tapa (tramo tapado) | L_tapado x 0.60 x 0.10 |
| Encofrado abierta | cara externa = (H + 0.10) x L; cara interna = H x L; cada una x 2 muros |
| Encofrado tapada | externo = (H + 0.20) x L; interno = H x L (x 2 muros) + fondo de tapa L_tapado x 0.40 |
| Curado | 2 x L x H_prom (caras interiores) + L x 0.40 (fondo) + L x 0.40 si TAPADA; 3 o 4 caras |

Aclaración del encofrado: en la hoja se escribe el ÁREA de una cara (externa o interna) y CANT. 2 (dos muros). La cara externa
suma la losa de fondo (+0.10) en abierta y fondo + tapa (+0.20) en tapada.

### 5.3 Acero de cunetas (regla del usuario 04/10 05:35, ratificada 16:43 y 21/10)
- Lleva acero solo donde H ≥ 0.40 m (desde el NCT o desde la rejilla hasta el fondo). Con H < 0.40 la cuneta abierta es de
  concreto simple. Excepción: todo tramo TAPADO lleva acero siempre (cuerpo en U y tapa), aunque H < 0.40 (ejemplo: Eje 01 de Varones,
  tapado de 13.20 a 19.20 m con H = 0.37 lleva acero). Un tramo abierto que pasa de 0.40 dentro de su longitud se metra desde la
  progresiva donde H = 0.40.
- Por tramo (hoja METRADO ACERO, columnas): A N° · B EJE · C TRAMO · D TIPO · E SEC. INI · F SEC. FIN · G LONGITUD · H Ø · I factor
  (`BUSCARV` en Listas) · J separación longitudinal · K barras long. inicio · L barras fin · M promedio · N = G*M · O = N*I ·
  P separación transversal 0.25 · Q desarrollo U inicio · R desarrollo fin · S promedio · T cantidad · U = S*T · V = U*I · W = O+V ·
  X Ø tapa · Y factor · Z separación tapa 0.25 · AA/AB barra de tapa 0.56 · AC promedio (si TAPADA) · AD cantidad · AE = AC*AD ·
  AF = AE*Y · AG = W + AF (total del tramo). Total en la fila 28 (`AG28` → PLANILLA).
- Separación longitudinal según H: 0.20 si H < 0.45; 0.22 si H < 0.60; 0.25 si mayor.
- Barras longitudinales = REDONDEAR.MAS((0.60 + 2H)/sep) al inicio y al final (ej. H 0.37 @0.20 → 7).
- Transversal en U @0.25, desarrollo = 0.60 + 2(H + 0.05) (ej. H 0.37 → 1.44 m). Cantidad = L/0.25 + 1 (teórico) o
  REDONDEAR.MAS(L/0.25) + 1 (entero), según X1.
- Tapa de cuneta tapada: transversal 3/8" @0.25 de 0.56 m SIEMPRE ("el acero transversal de las tapas mide 0.56 siempre y la
  separación es 0.25, eso está okey").
- 3/8" = 0.56 kg/m.

### 5.4 Movimiento de tierras y preliminares (PLANILLA GENERAL, por eje)
| Partida | Fórmula |
|---|---|
| Limpieza y trazo | L x 1.40 |
| Excavación | L x 1.40 x (H_prom + 0.10 + PARAMETROS!B15) — la columna ALTURA = H_prom + 0.10 de losa; B15 = 0.10 de solado |
| Refine y solado E=4" | L x 0.60 |
| Relleno | L x 0.80 x (H_prom + 0.10 + B15) |
| Eliminación | (excavación − relleno) x 1.20 (factor PARAMETROS!B16) |
| Excavación y concreto de dados | N° de dados x 0.40 x 0.35 x 0.40 = 0.056 m³ c/u (Varones 56 = falsas columnas) |

El "1.40" es el ancho de la franja de trabajo de cunetas. Pregunta de un ingeniero (16/10): "¿en CAR Varones el colector tiene
1.40 de ancho?" → No: b interior 0.60, exterior 0.90; 1.40 es el ANCHO DE ZANJA del colector (0.90 + 2 x 0.25 de sobreancho) que
se usa para limpieza, trazo y excavación.

### 5.5 Rejillas
Longitud con rejilla = longitud del tramo ABIERTO − descuentos (puertas, cruces), ingresados a mano. Los tapados no llevan
rejilla. Detalle constructivo (lámina DJ-03): módulo de 1.00 m (0.997 fabricado, 3 mm de holgura), 2 ángulos L 1" x 1" x 3/16",
39 platinas 1" x 3/16" x 0.446 m de canto @1" (abertura libre 0.021 m), ancho del módulo 0.497 m sobre rebaje de 0.05 x 1" del borde
interior de cada muro, 20.0 kg/m.

### 5.6 Juntas de cunetas (EG-2013 MTC, Sección 510)
- Cada 3.00 m y en los cambios de dirección, en TODA la sección en U (2 muros + losa de fondo) desde el 15/10 (Refugio y Varones):
  longitud por junta = 2 x H_media + 0.40, con H_media = área de muro / longitud del eje; N° = REDONDEAR.MAS(L/3.00).
  Refugio: 233 juntas, 241.96 → 335.16 m. Varones: 185 juntas, 252.29 m.
- Antes (y sigue así en el CAR Mujeres congelado): solo los 2 muros, altura x 2 x N°.
- Material: tecnopor 1" en todo el espesor + sellador asfáltico (RC-250 + arena) en la cara interior. El usuario aportó el
  procedimiento de juntas (14/10, PDF) y la norma MTC: "el tecnopor va en toda la sección y el asfalto actúa solo como sello
  superficial".
- Por qué: una junta solo en los muros deja la losa de fondo amarrada y se fisura.

### 5.7 Lloraderos (Refugio y Varones; el CAR Mujeres no lleva porque ya está presupuestado — 08/10 y 19/10)
- Ubicación: solo en muros de cuneta cuya franja exterior de 0.30 m cae sobre el achurado de área verde (medido en la planta
  general de drenaje). Tramos junto a veredas, pisos o edificaciones no llevan.
- N° por tramo = REDONDEAR.MAS(longitud junto a área verde / 1.50).
- Refugio: 157 und en 226.21 m de muro (12 tramos). Varones: 226 und en 320.53 m (34 tramos).
- Hoja METRADO LLORADEROS (unidades por tramo) + DESAGREGADO LLORADEROS (materiales) + ACU LLORADEROS (costo). El 23/10 la usuaria
  preguntó dónde estaba el metrado de piedra, tubo y geotextil: está en DESAGREGADO LLORADEROS, no en METRADO LLORADEROS.
- Desagregado por lloradero (láminas DL-01/DL-02 → DPL-38/37 en Refugio, DPLV-35/34 en Varones):

| Componente | Und | Por lloradero | Varones (226) |
|---|---|---|---|
| Tubo PVC-U Ø 3" (NTP 399.003), 0.10 en el muro + 0.20 perforado | m | 0.30 | 67.80 |
| Perforaciones Ø 3/8" (4 por fila @0.05, 2 filas a 120°) | und | 8 | 1,808 |
| Excavación local (0.30³) | m³ | 0.027 | 6.10 |
| Grava filtrante 20-40 mm: 0.30³ x 1.10 | m³ | 0.0297 | 6.71 |
| Geotextil no tejido clase 2: 6 x 0.30² x 1.10 | m² | 0.594 | 134.24 |
| Mortero 1:3 de sellado (anillo 0.02 m en las dos caras) | m³ | 0.0005 | 0.11 |

- Sección D del desagregado: control con el RESUMEN `=SI(ABS(E−F)<0.001;"CONFORME";"REVISAR")`.

### 5.8 Tapa de inspección de cunetas tapadas (0.60 x 0.60 x 0.10)
Hoja PLANILLA TAPAS REGISTRO INTERNO con PARAMETROS: concreto = N x 0.60 x 0.60 x 0.10 (0.036 m³/tapa); encofrado laterales
N x 2(0.60+0.60) x 0.10 + fondo de molde N x 0.36 (0.60 m²/tapa); acero 3/8" parrilla simple @0.15: barras de 0.60 − 2 x 0.025 =
0.55 m, cantidad REDONDEAR((0.60 − 0.05)/0.15) + 1 = 5 por sentido → 2 x 5 x 0.55 x 0.56 = 3.08 kg/tapa. Cantidades: Refugio 17,
Varones 18 (provisional: 1 por tramo tapado, "confirmar con el plano"), Mujeres 10. En Barranquita: tapas al inicio y fin de cada
tapado, en cada empalme y a 10 m como máximo (criterio propuesto; el usuario no fijó distancia).

### 5.9 Red de techo, piso y falsa columna
- METRADO MONTANTES: por edificación y lado: N° de montantes, veces, longitud → m de tubería; codos 90° (cantidad x veces);
  abrazaderas = MAX(1; REDONDEAR.MENOS(L/4;0)) por montante; colgadores; codos 45°.
- METRADO CANALETAS: por edificación y lado: N° de canaletas, longitud; soportes = REDONDEAR.MAS(L/0.60;0) + 1; 2 tapas laterales por
  canaleta; boquillas = montantes del lado (`='METRADO MONTANTES'!C…`). Parámetros: fondo 0.25, alto 0.20, pestaña 0.05, desarrollo
  0.75 m, e = 0.9 mm, soportes @0.60, plancha referencial = total x 0.75 (Refugio 385.49 m²).
- METRADO EN PISO (SUMIDERO): por sector: tubería 4" PVC-U CP (m), sumideros, codos 90°, codos 45°, tees.
- Falsa columna 0.20 x 0.15 x 1.30 (und = N° de montantes): concreto 0.039 m³/und; encofrado 2 x 1.30 x 0.15 + 1 x 1.30 x 0.20 =
  0.65 m²/und; acero longitudinal 4 barras de 1.20 m + 9 estribos de 0.58 m de 3/8" = 5.6112 kg/und. La partida en und no tiene pago
  propio: se paga por sus subpartidas de concreto, encofrado y acero.

### 5.10 Canaletas de bancas
- CAR Mujeres (19/10): 16 techos iguales, a una agua; un solo tramo de 2.00 m por techo, sin uniones; plancha de aluzinc e = 0.50 mm,
  0.18 x 0.20; 2 soportes de platina 1" x 1/8" (a 0.40 de cada extremo), 2 tapas, 1 boquilla (capucha, no sumidero) por techo.
  Planilla: subtítulo 1.4.4.5.4 RED DE RECOLECCION TECHO DE BANCAS DE JARDINERIA: 1.4.4.5.4.1 canaleta 32.00 m, tapas 32, soportes 32,
  boquillas 16. Codos, colgador y abrazadera NO se agregan (ya están en METRADO MONTANTES, BC-01 a BC-16). A pedido del usuario se
  agregó al RESUMEN el CODO DESAGÜE PVC Ø4" x 45° (1.4.4.5.3.2) que faltaba (19/10 19:08).
- Hogar de Refugio (22/10): 9 bancas = 3 juegos OC-01 de tres techos (3.79, 4.21, 3.79 m); canaleta galvanizada e = 0.50 mm,
  0.18 x 0.21; 2 sujetadores por canaleta (a 0.80/0.85 m de cada extremo), 2 tapas, 1 boquilla. Hoja METRADO CANALETA BANCAS: N° de
  juegos en F21 (editable) → 35.37 m, 18 soportes, 18 tapas, 9 boquillas. Solo esos 4 ítems (sin tubo, codos, colgador, abrazadera
  ni falsa columna, por indicación del usuario).

---

## 6. Metrado del colector (fórmulas de las hojas COLECTOR)

Cálculo de respaldo en Python: `herramientas/metrado_calc.py` (tramos de 2.00 m con secciones medias; `tramos()`, `segmentos()`,
`registros()`, `cajas()`, `juntas()`, `resumen()`, `cuadro_doblado()`). La planilla repite el cálculo con fórmulas por tramo
homogéneo; h y Hz son medias ponderadas.

| Concepto | Fórmula (por tramo de longitud L) |
|---|---|
| Ancho exterior | be = b + 2·e_muro |
| Ancho de zanja | be + 2 x 0.25 |
| Hz | terreno existente − fondo del solado (cota de fondo − e_fondo − e_solado) |
| Limpieza y trazo | ancho de zanja x L |
| Excavación | ancho de zanja x Hz x L |
| Refine | (be + 0.10) x L |
| Relleno lateral | 2 x 0.25 x Hz x L |
| Relleno franja de nivelación (lado vía) | 1.00 x (NPT − terreno) x L |
| Eliminación | (excavación − relleno) x esponjamiento (1.20 Refugio y Varones; 1.25 CAR Mujeres) |
| Solado f'c=100 e = 0.05 | (be + 0.10) x L |
| Losa de fondo | be x e_fondo x L |
| Muros | 2 x e_muro x h x L |
| Losa superior | be x e_losa x L (0.25 en cruce de camiones) |
| Acabado frotachado (vereda) | be x L |
| Curado | (2h + b + be) x L (2 caras interiores + fondo + losa superior) |
| Encofrado | 2h·L (caras interiores) + 2(e_fondo + h + e_losa)·L (caras exteriores) + b·L (fondo de la losa superior) |

Acero (hoja COLECTOR ACERO, E.060 14.3.4):
- Tramo normal y motos: un marco cerrado en el eje: perímetro = 2(be − e) + 2(e_fondo/2 + h + e_losa/2) + 0.30 de ganchos;
  3/8" @0.20 (normal) o @0.15 (motos).
- Cruce de camiones: marco exterior + interior de 1/2" @0.15 con recubrimiento 0.04: ext = 2(be − 0.08) + 2(e_fondo + h + e_losa −
  0.08) + 0.30; int = 2(b + 2(e − 0.04)) + 2(h + 2(e − 0.04)) + 0.30.
- N° de juegos = REDONDEAR.MAS(L/s). Longitud = N° x (per1 + per2). Peso = longitud x kg/m.
- Longitudinales 3/8": N° = REDONDEAR(per1/sl) + REDONDEAR(per2/sl) (sl 0.25 normal; 0.20 camión); longitud = N° x L x (1 + 0.40/9.00).
- Registros: refuerzo de borde 8 Ø 1/2" L = 1.40 por registro; parrilla de tapa 14 x 0.62 de 3/8"; asas 2 x 0.50 de fierro liso
  1/2" (0.994 kg/m).
- Cajas CL y CC (Refugio): malla 3/8" @0.20 en ambas caras: kg = ((L1/0.20 + 1)·L2 + (L2/0.20 + 1)·L1) x caras x 1.10 x 0.56.

Cajas del Refugio (hoja COLECTOR CONCRETO, sección "CAJAS CL Y CC POR ELEMENTO", lámina DP-07): solado (largo + 2e + 0.10)(ancho + 2e
+ 0.10); losa de fondo exterior x e; muros largos exterior x e x H (x2); muros cortos interior x e x H; descuentos de ventanas (salida
al colector 0.80 x 1.40; llegada del CAR Varones 0.60 x 1.166; cuneta Eje 01 de Varones 0.40 x 0.656; ventana de salida de la CC
1.50 x 0.43 = alto interior del R-01 del CAR Mujeres: losa 259.25 − 0.10 − cota de fondo 258.72); murete del escalón de la poza; umbral
0.25 x 0.40; losa superior con descuento de rebajes; acabado y curado. Corrección del 15/10: la ventana de la CC se tomaba de 0.842;
concreto del Refugio 58.31 → 58.41 m³ (hoy 58.43 en el RESUMEN).

Valores del Refugio por tramo: normal 0+000-0+026.32 (h 1.439), camión 0+026.32-0+031.33 (h 1.336, losa 0.25), normal hasta 0+039.04,
motos 0+039.04-0+041.04, normal hasta 0+058.81, diagonal (quiebres) hasta 0+066.89, tramo recto final hasta 0+069.89. Varones:
camión 0+000-0+006.08 (h 0.709, losa 0.25), normal 0+006.08-0+100.90 (h 1.01), empalme horizontal con la CL 0+100.90-0+105.29 (h 1.159).

---

## 7. Registros de limpieza: tapa ciega (vigente desde el 16/10)

### 7.1 Historia
| Fecha | Cambio |
|---|---|
| 03/10 | Registro tipo: tapa 0.68 x 0.68 x 0.08 f'c=210 con malla 3/8" @0.10; luz libre 0.60; contramarco L 2"x2"x3/16" (0.70/0.80) con 8 anclajes 3/8" L = 0.20; marco de tapa L 1½"x1½"x1/8"; borde engrosado 0.15 x 0.10; refuerzo de borde 8 barras 1/2" L = 1.40. Partidas por componente (7). |
| 03/10 20:46 | El que cotiza pidió detalle de cada componente: láminas aparte (DA/DD) con todo desagregado. |
| 07/10 | Una partida por und (Delphin) + hoja DESAGREGADO TAPA REGISTRO + ACU TAPA REGISTRO (S/ 383.29 por tapa). |
| 07/10 00:15 | Pregunta del usuario: ¿por qué tapas de concreto y no metálicas? Se explicó (peso, costo, robo); decidió mantener para no rehacer planos. |
| 14/10 | Refugio: contramarco L 2"x2"x3/16" → L 1 1/2"x1 1/2"x1/8" (carga peatonal: los 10 registros están fuera del ingreso OE-01 0+026.32-0+031.33 y del portón de motos 0+039.04-0+041.04; el ala apoya entera sobre el borde engrosado). Ángulos 151.42 → 101.02 kg; pintura 9.82 → 8.39 m²; lija y thinner por separado; ACU 383.29 → 297.45 S/ (partida 2,974.50). |
| 15/10 | Varones toma el mismo contramarco (ACU S/ 292.25). |
| 16/10 | Tapa CIEGA en los 3 CAR (sin marco ni contramarco): detalle DP-06B rev. 02; metrado actualizado SOLO en Refugio (10) y Varones (11); CAR Mujeres sin cambio en su metrado. ACU S/ 182.06 por tapa en ambos. |

### 7.2 Detalle vigente (DP-06B rev. 02)
Tapa 0.68 x 0.68 x 0.08 f'c=210 vaciada aparte en obra; parrilla 3/8" @0.10 (7 + 7 barras de 0.62); 2 asas de fierro liso 1/2"
(agarre 0.15 + 2 patas de 0.02 + 2 ganchos de 0.15 = 0.49, se toma 0.50) en cajuelas 0.19 x 0.06 x 0.03 a ±0.20; cantos biselados
1 x 1 cm; peso ≈ 89 kg (izaje entre dos operarios). Asiento en rebaje 0.70 x 0.70 x 0.08 de la losa (0.05 por lado), holgura 1 cm,
luz libre 0.60 x 0.60. Borde engrosado 0.15 x 0.10 bajo la losa (perímetro medio 4 x 0.75 = 3.00 m) con 8 Ø 1/2" L = 1.40.
CAR Varones (b 0.60 < abertura 0.70): en los lados largos el rebaje apoya en la cabeza de los muros; el borde engrosado va solo en los
2 lados transversales: 2 x 0.60 = 1.20 m por registro (antes se había copiado el de 3.00 m); barras transversales con ganchos de 0.29
dentro de los muros. Concreto de Varones 56.02 → 55.72 m³ por esa corrección.

### 7.3 Cantidades (hoja COLECTOR REGISTROS Y TAPAS, bloque de partidas)
| Componente | Und | Cálculo | Varones (11) |
|---|---|---|---|
| Tapa ciega (vaciada aparte) | und | 1 por registro | 11 |
| Encofrado lateral de la tapa | m² | N x 4 x 0.68 x 0.08 | 2.394 |
| Acero en tapas: parrilla 3/8" y asas 1/2" liso | kg | COLECTOR ACERO | 64.40 |
| Concreto f'c=210 en tapas | m³ | N x 0.68 x 0.68 x 0.08 | 0.407 |
| Asiento: rebaje 0.70 x 0.70 x 0.08 en la losa | und | concreto incluido en la losa | 11 |
| Colocación de la tapa (izaje con asas) | und | 1 por registro | 11 |

El concreto del rebaje y del borde engrosado se metra con la losa superior (COLECTOR CONCRETO): borde = perímetro x 0.15 x 0.10 x N;
descuento de la abertura = 0.70 x 0.70 x e_equivalente x N, con e_equivalente = 0.08 + (e_losa − 0.08) x (0.60/0.70)² (equivale a
0.49 x 0.08 + 0.36 x (e_losa − 0.08) por registro). Refugio: 10 registros = 7 en la losa + 1 en la CL + 2 en la CC (las aberturas
de las cajas se descuentan en su propia losa).

### 7.4 PLANILLA GENERAL
Fila de la partida con `K = SUMA` de los registros; filas de texto "Cada tapa: concreto armado f'c=210 de 0.68 x 0.68 x 0.08 vaciado
aparte en obra…" y una fórmula de texto: `="Totales para "&K…&" tapas: concreto "&TEXTO(…;"0.000")&" m3; acero de tapas y asas
"&TEXTO(…;"0.00")&" kg; encofrado …"` (celda con `t="str"`). "Desagregado por componente: ver hoja DESAGREGADO TAPA REGISTRO".

### 7.5 DESAGREGADO TAPA REGISTRO (estructura)
A. Ubicación (registro, progresiva, ubicación, cant., sustento; enlazado a COLECTOR REGISTROS Y TAPAS) y TOTAL. B. Componentes por
registro y total (CONCRETO 0.0370 m³; ENCOFRADO 0.2176 m²; ACERO: parrilla 4.8608 kg, asas 0.994 kg, borde 11.1328 kg). C. Control
con las hojas del colector (`CONFORME`/`REVISAR`, tolerancia 0.0005). Nota final: no hay ángulos, soldadura ni pintura.

---

## 8. Juntas del colector

| Partida | Refugio | Varones | Cálculo |
|---|---|---|---|
| 01.04.04.06.01 JUNTA DE DILATACION E=1" CON TECNOPOR Y SELLADOR ASFALTICO EN COLECTOR | 17 x 5.92 = 100.64 m | 26 x 4.64 = 120.64 m | N = ENTERO(L/4.00); perímetro = 2(b + 2e_muro) + 2(e_fondo + h_max + e_losa) |
| 01.04.04.06.02 JUNTA … ENTRE COLECTOR Y CERCO PERIMETRICO (Refugio) | 58.81 m | – | junta LONGITUDINAL entre el muro lado predio y el cimiento del cerco, 0+000.00 a 0+058.81 (primer quiebre), tecnopor de 0.90 m de alto + sellador |
| 01.04.04.06.02 JUNTA … ENTRE COLECTOR Y CAJA CL (Varones) | – | 4.64 m | perímetro de la sección en el contacto con el muro este de la CL |

Decisiones con fecha:
- 14/10 21:14: el usuario no entendía las dos juntas. Explicación: la de dilatación corta toda la sección transversal cada 4 m; la
  otra va a lo largo del colector, entre su muro y la estructura vecina.
- 14/10 21:45: renombrar ("una debe decir en colector y la otra cerco perimétrico, porque no hay vereda afuera en Mujeres
  Violentadas"); no sello elastomérico sino tecnopor + sellador asfáltico como la normativa (EG-2013 MTC Sección 510) →
  `renombrar_juntas_colector.py`.
- 14/10 22:46: también lleva sellador asfáltico la junta con el cerco ("en ambos casos creo debe ser sellado de una pulgada").
  Sellador vigente 1" x 2" (25 x 50 mm) de asfalto líquido RC-250 + arena gruesa.
- 15/10 00:59 / 01:26: "solo hay a un lado el cerco perimétrico"; al otro lado solo tierra: la partida queda solo con la junta
  longitudinal contra el cerco (210.98 → 58.81 m; `junta_cerco_solo_refugio.py`). Se pasó por un criterio intermedio "borde de losa
  a un solo lado" (`junta_cerco_un_lado_refugio.py`) que quedó reemplazado. La lámina DD-03 se corrigió (vista D nueva).
- CAR Varones conserva la estructura con su caso real: terreno natural a ambos lados (sin junta longitudinal) y contacto con la CL.
- CAR Mujeres (congelado): 1.4.4.6.5.3 "JUNTA E=1" CON TECNOPOR ENTRE COLECTOR Y PISO ADYACENTE" 78.42 m.
- Parámetros de sello por proyecto en código: `metrado_calc.SELLOS` ("poliuretano" 1" x 1" | "asfaltico" 1" x 2", en_tecnopor) y
  variable de entorno `SELLO_JUNTA`; `CONTRAMARCO` igual. `varones/compat.py` fija `CONTRAMARCO=1.5x1.5x1/8` y `SELLO_JUNTA=asfaltico`.

Empalmes de cuneta: se cuentan en COLECTOR JUNTAS Y EMPALMES como información (Refugio 6, Varones 4), sin partida propia. Ventana
0.40 x H en el muro lado predio, caída libre al fondo, junta de 1" en el contacto y registro encima. En el Refugio las cunetas de los
Ejes 11 y 12 terminan antes del cerco y se prolongan 1.88 y 5.39 m hasta el colector: esa prolongación se metra en cunetas.

---

## 9. Sustentos con código de lámina

- Cada fila de las hojas del colector y de los desagregados lleva el código de la lámina que justifica la medida.
- Códigos de trabajo (DP-01 … DP-10, DA-01 … DA-03, DD-01 … DD-04, DJ-01 … DJ-03, DL-01/02) se reemplazaron por los del juego final
  que imprime cada usuaria:

| Trabajo | CAR Varones (DPLV) | Hogar de Refugio (DPL) |
|---|---|---|
| DP-01 planta | DPLV-17 | – |
| DP-02 perfil | DPLV-18 | – |
| DP-04 secciones | DPLV-21 y DPLV-22 | – |
| DP-06B tapa ciega | DPLV-23 | DPL-24 |
| DP-06C empalme de cuneta | DPLV-24 | – |
| DP-06D isométricos de la tapa | DPLV-26 | DPL-29 |
| DP-07 empalme con la caja CL | DPLV-25 | – |
| DD-01 / DD-02 rebaje / tapa | DPLV-27 / DPLV-28 | (DPL-24 y DPL-29) |
| DD-03 juntas | DPLV-29 | DPL-28 |
| DD-04 empalme | DPLV-30 | DPL-25 |
| DJ-01 / DJ-02 / DJ-03 cunetas | DPLV-31 / 32 / 33 | sin lámina propia: se quita la cita |
| DL-01 isométrico lloradero / DL-02 detalle | DPLV-34 / DPLV-35 | DPL-37 / DPL-38 |
| Planta de ubicación de lloraderos (DL-00) | DPLV-43 | DPL-40 |
| Falsa columna | – | DPL-39 |
| Bancas OC-01 | – | DPL-41 / DPL-42 |

- Regla del 23/10 (19:45-19:47): láminas que la usuaria excluyó de su juego (DP-08 cuadro de doblado, DA-01 a DA-03 cuadros de
  metrado) → se BORRA la referencia del metrado, no se reemplaza ni se toca el metrado. Ej.: "Criterio (lamina DA-02): …" →
  "Criterio: …"; "Lamina DA-01: zanja …" → "Zanja …"; celdas cuyo único texto era la referencia quedan vacías. 140 celdas de texto
  en Varones (sharedStrings y texto en caché de fórmulas); ningún valor cambia. El generador parte del original de la usuaria
  (`insumos/katiuska/METRADO_DRENAJE_PLUVIAL_CAR_VARONES_23-10-2026_ORIGINAL.xlsx`).
- Los códigos se citan tal cual el rótulo de la usuaria (incluso DPVL-09, DPVL-10, DVPL-11 en Varones).
- Los cuadros de partidas de las láminas DA leen los valores guardados de la planilla (`varones/planilla_v.py` →
  `_calc/metrado_planilla.json`); nunca se recalculan aparte.

---

## 10. ACU: formato y reglas

### 10.1 Formato Delphin (función `acu_juntas_refugio.acu`)
Encabezado: Partida (código y nombre Delphin) · Partida del metrado · Unidad · Metrado (fórmula a la hoja de metrado) · Rendimiento.
Tabla: N° · RECURSO · UND · CUADRILLA · CANTIDAD POR (M / UND / TAPA) · PRECIO S/ · PARCIAL S/ · FUENTE DEL PRECIO. Grupos MANO DE OBRA,
MATERIALES, EQUIPOS, cada uno con subtotal; COSTO UNITARIO DIRECTO = MO + materiales + equipos; COSTO DIRECTO DE LA PARTIDA = CU x
metrado.

Relaciones (las mismas de Delphin/S10):
- Cantidad de MO (hh/und) = cuadrilla x 8 / rendimiento.
- Cuadrilla = cantidad x rendimiento / 8 (cuando la cantidad sale de un ratio, se despeja la cuadrilla).
- Rendimiento por defecto = 8 / cantidad del operario (`=8/E_operario`), o un dato.
- Herramientas manuales = % de la MO (3 % en concreto, juntas, tapa, lloraderos; 5 % en hojalatería de canaletas).
- Precios sin IGV: precio publicado con IGV / 1.18 (agua EMAPA ya sin IGV).

### 10.2 Mano de obra 2026 (hoja COSTO HORA HOMBRE 2026, `mano_obra_2026_refugio.py`)
Tabla oficial CAPECO - FTCCP "Remuneración y condiciones de trabajo en construcción civil 2026" (Exp. N.° 339-2025-MTPE/2.14-NC;
PDF en `insumos/normas/CAPECO_FTCCP_Remuneraciones_2026.pdf`), edificación, 01.01.2026 al 31.12.2026.

| Concepto | Operario | Oficial | Peón |
|---|---|---|---|
| Remuneración básica (R.M. 197-2025-TR) | 89.30 | 69.75 | 62.80 |
| Leyes y beneficios sociales sobre jornal (112.20 %) | 100.19 | 78.26 | 70.46 |
| BUC (32 % / 30 % / 30 %) | 28.58 | 20.93 | 18.84 |
| Leyes sociales sobre BUC (12.25 %) | 3.50 | 2.56 | 2.31 |
| Seguro de vida ESSALUD + Vida (S/ 5.00 al mes) | 0.16 | 0.16 | 0.16 |
| Fondo de capacitación | 0.40 | 0.31 | 0.28 |
| Movilidad (R.M. 139-2024-TR) | 8.60 | 8.60 | 8.60 |
| Overol (R.D. 777-87-DR-LIM): 2 x 132.80 / 300 | 0.89 | 0.89 | 0.89 |
| Total por día de 8 h | 231.62 | 181.46 | 164.34 |
| **Costo hora-hombre** | **28.95** | **22.68** | **20.54** |

Desglose del 112.20 %: CTS 12.00; participación de utilidades 3.00; SCTR asistencial 1.30 y económico 1.05; ESSALUD 9.00; seguro de vida
0.90; salario dominical 17.58; vacaciones 10.00; gratificaciones 22.22; feriados 4.33; asignación escolar 25.00; ESSALUD sobre dominical
1.58, vacaciones 0.90, feriados 0.39; SCTR sobre dominical 0.41, vacaciones 0.24, feriados 0.10; seguro de vida sobre dominical 0.16 y
feriados 0.04; bonificación Ley 30334 2.00. Sobre BUC (12.25 %): SCTR 1.30 + 1.05, ESSALUD 9.00, seguro de vida 0.90.
Resumen en G11:G13 (operario, oficial, peón): TODAS las ACU leen `'COSTO HORA HOMBRE 2026'!$G$11/12/13`. Si la hoja existe se
reemplaza su contenido conservando la ruta (las referencias no se rompen).
Antes del 15/10 se usaba 30.42 / 22.95 / 20.79 ("CAPECO 2024-2025 llevado al jornal básico 2025-2026"); el usuario preguntó el
09/10 17:51 si eran reales y el 15/10 pidió actualizar todo a 2026.

### 10.3 ACU vigentes (costo unitario directo, sin IGV)
| ACU | Unidad | Refugio | Varones |
|---|---|---|---|
| Tapa de registro ciega (01.04.04.06.05.01) | und | 182.06 | 182.06 |
| Canaleta 0.25 x 0.20 e=0.9 mm | m | 40.06 | 40.06 |
| Soporte de platina F°G° 1" x 1/8" | und | 16.45 | 16.45 |
| Tapa lateral | und | 15.59 | 15.59 |
| Boquilla a montante Ø4" | und | 27.08 | 27.08 |
| Junta de dilatación en colector | m | 11.66 | 11.60 |
| Junta colector-cerco (Refugio) / colector-caja CL (Varones) | m | 8.49 | 11.60 |
| Lloradero PVC Ø3" | und | 20.56 | 20.56 |

Historial: tapa 383.29 (07/10) → 297.45 (14/10) → 182.06 (16/10); juntas 12.01 y 6.12 S/m el 15/10 (antes de la junta solo-cerco);
canaletas 40.64 / 16.79 / 16.03 / 27.92 el 07/10 (MO anterior); partida de lloraderos Refugio 157 x 20.56 = 3,227.64; Varones
226 x 20.56 = 4,646.15.

### 10.4 COLECTOR INSUMOS: ratios por unidad de partida (dato amarillo editable)
| Partida | Insumo: cantidad por und |
|---|---|
| Concreto f'c=210 losa de fondo y losa superior (por m³) | cemento 9.73 bol; arena gruesa 0.52 m³; piedra chancada 1/2" 0.53 m³; agua 0.186 m³; mezcladora 9-11 p³ 0.8 hm; vibrador 0.8 hm; operario 0.8; oficial 0.8; peón 6.4 hh |
| Concreto f'c=210 muros (por m³) | mismos materiales; mezcladora 1.0; vibrador 1.0; operario 1.0; oficial 1.0; peón 8.0 |
| Encofrado (por m²) | madera tornillo 4.24 p²; clavos 3" 0.20 kg; alambre N° 8 0.20 kg; operario 0.8; oficial 0.8 hh |
| Acero (por kg) | acero corrugado 1.05 kg (5 % de desperdicio); alambre N° 16 0.06 kg; operario 0.032; oficial 0.032 hh |
| Solado f'c=100 e=0.05 (por m²) | cemento 0.30 bol; hormigón 0.064 m³; agua 0.01 m³; operario 0.1; peón 0.4 |
| Excavación manual (por m³) | peón 2.67 hh; herramientas 3 % MO |
| Relleno compactado (por m³) | agua 0.05 m³; compactador tipo plancha 0.4 hm; operario 0.4; peón 1.6 |
| Eliminación (por m³) | volquete 6 m³ 0.133 hm; cargador frontal 0.033 hm; peón 0.133 |
| Tapa: encofrado lateral (por m², 6 usos) | madera 4.24/6 = 0.7067 p²; clavos 0.20/6 = 0.0333 kg; operario 0.8; oficial 0.8 |
| Tapa: colocación y curado (por und) | operario 1.0; peón 1.0; agua 0.01 m³ |
| Junta de dilatación (por m) | tecnopor = ACU JUNTA (m²/m x 1.10); sellador = ACU JUNTA (m³/m); operario 0.2; peón 0.2 |
| Junta con el cerco (por m, Refugio) | tecnopor 0.90 m²/m x 1.05; sellador 0.0254 x 0.0508; peón 0.1; operario 0.05 |

La metadata del metrado (D) de cada bloque es fórmula a la PLANILLA (p. ej. losa de fondo = SUM de las filas de "Losa de fondo" de la
partida única de concreto).

### 10.5 ACU TAPA REGISTRO (tapa ciega, por tapa)
Datos: concreto 0.68² x 0.08 = 0.0370 m³; encofrado lateral 2.72 x 0.08 = 0.2176 m²; tablero de vaciado 0.80 x 0.80 x 1" = 6.89 p² en
6 usos = 1.15 p²; parrilla 4.8608 kg; borde 11.1328 kg; asas 0.994 kg; desperdicio de acero 5 %; ratios de COLECTOR INSUMOS.
| Recurso | Cantidad por tapa | Fórmula |
|---|---|---|
| Operario | 1.7473 hh | conc x 0.8 + (parr + borde + asas) x 0.032 + enc x 0.8 + 1 |
| Oficial | 0.7473 hh | conc x 0.8 + acero x 0.032 + enc x 0.8 |
| Peón | 1.2367 hh | conc x 6.4 + 1 |
| Cemento | 0.3599 bol | conc x 9.73 |
| Arena gruesa | 0.0192 m³ | conc x 0.52 |
| Piedra chancada 1/2" | 0.0196 m³ | conc x 0.53 |
| Agua | 0.0169 m³ | conc x 0.186 + 0.01 (curado) |
| Madera tornillo | 1.3038 p² | enc x 4.24/6 + 1.15 |
| Acero corrugado | 16.7933 kg | (parr + borde) x 1.05 |
| Fierro liso 1/2" (asas) | 1.0437 kg | asas x 1.05 (mismo precio del corrugado, referencial) |
| Alambre N° 16 | 1.0193 kg | acero x 0.06 |
| Herramientas | 3 % MO | |
Rendimiento = 8 / 1.7473 = 4.58 und/día (cuadrilla de 1 operario). MO 92.93 + materiales 86.34 + equipos 2.79 = 182.06 S/.
La ACU previa con marco y contramarco tenía 6 bloques (A ángulos y soldadura, B concreto, C tablero, D acero, E pintura, F colocación);
el ejemplo que pegó el usuario el 14/10 22:53 (ángulos 15.14 kg/tapa = 2.80 x 3.63 + 2.72 x 1.83; pintura 0.98 m²/tapa = 2.80 x 0.203
+ 2.72 x 0.152) corresponde a esa versión ya superada.

### 10.6 ACU CANALETAS (4 análisis; `render_tapa/add_acu_can.py`, datos de METRADO CANALETAS)
Datos: fondo 0.25, alto 0.20, pestaña 0.05, desarrollo 0.75 m²/m, e = 0.9 mm; peso de plancha = e x 7.85 + 0.30 (zinc) = 7.365
kg/m²; plancha comercial 1.22 x 2.44; traslape 0.05; desarrollo del soporte = 0.25 + 2 x 0.20 + 2 x 0.10 = 0.85 m; platina 1" x 1/8" =
0.633 kg/m (25.4 x 3.18 mm x 7.85); barra de 6 m.
| ACU | Rendimiento | Cuadrilla | Materiales por unidad |
|---|---|---|---|
| Canaleta (m) | 25 m/día | 1 operario hojalatero + 1 peón (0.32 hh c/u) | plancha 0.75 x (1 + 0.05/2.44) x 1.05 = 0.8036 m²; remache pop 1/8" 2 x 0.65/0.05/2.44 = 10.66; sellador PU (cartucho 300 ml = 8 m de cordón) 0.65/2.44/8 = 0.0333 |
| Soporte (und) | 40 und/día | 1 operario + 0.5 peón | platina 0.85 x 1.05 = 0.8925 m; 2 pernos de expansión 1/4" x 2 1/2" con tarugo; 2 tornillos autorroscantes 1/4" x 3/4" |
| Tapa lateral (und) | 30 und/día | 1 operario + 0.5 peón | plancha (0.25 x 0.20 + 2 x 0.45 x 0.03) x 1.10 = 0.0847 m²; 6 remaches; sellador 0.65/8 |
| Boquilla Ø4" (und) | 16 und/día | 1 operario + 0.5 peón | plancha (π x 0.1016 x 0.15 + 0.20 x 0.20) x 1.15 = 0.1011 m² (tubo de 4" x 0.15 + brida 0.20 x 0.20); 8 remaches; sellador (4 x 0.20 + π x 0.1016)/8 |
Herramientas 5 % MO. Hoja con "RESUMEN DE COSTOS DIRECTOS (referencial)" al final (Varones total 37,956.49 S/).
Detalle dibujado (09/10-10/10): canaleta, platina, pernos, abrazaderas y colgadores en isométrico "tal cual el ACU", con la sección
real 0.20 de ancho x 0.25 de alto (corrección del usuario 10/10 01:40).

### 10.7 ACU JUNTA DILATACION (por m de junta; Refugio)
Perímetro 5.92 m; 17 juntas; área de tecnopor por junta = 1.10 x (0.15 + 1.61 + 0.10) − 0.80 x 1.61 = 0.758 m²; tecnopor 0.758/5.92 =
0.128 m²/m; desperdicio 10 % (anillo); plancha 1.20 x 2.40 = 2.88 m² → planchas/m = 0.128 x 1.10 / 2.88; longitud sellada por junta =
2 x 1.61 + 0.80 (caras interiores) + 1.10 (cara superior) = 5.12 m; sellador 0.0254 x 0.0508 x 5.12 / 5.92 m³/m; RC-250 50 gal/m³ de
mezcla (mezcla ~2,000 kg/m³ con ~9 % de asfalto = 180 kg / 3.6 kg/gal); arena 1.05 m³/m³; operario 0.2 hh/m y peón 0.2 hh/m
(rendimiento 40 m/día). Varones: perímetro 4.64 (0.90 x 1.42 − 0.60 x 1.17 = 0.576 m²; longitud sellada 3.84 m).

### 10.8 ACU JUNTA CERCO (Refugio, por m)
58.805 m contra el cimiento del cerco con plancha de 0.90 m (lado opuesto 0 m, "no aplica"); tecnopor 0.90 m²/m x 1.05 / 2.88 =
0.3281 pln/m; sellador 0.0254 x 0.0508 m³/m en la cara superior; peón 0.1 hh/m (corte y colocación) y operario 0.05 hh/m (sellado),
rendimiento 160 m/día; MO 3.50 + materiales 4.89 + herramientas 0.11 = 8.49 S/m. Varones (caja CL): mismo cálculo de la junta de
dilatación con 1 junta de 4.64 m.

### 10.9 ACU LLORADEROS (por und)
Rendimiento 24 und/día, cuadrilla 0.5 operario + 1 peón → operario 0.1667 hh, peón 0.3333 hh. Tubo 0.30 x 1.05 = 0.315 m; grava
0.0297 m³; geotextil 0.594 x 1.05 = 0.6237 m²; mortero 1:3 0.0005 m³ (cemento 10.5 bol/m³, arena 1.05, agua 0.27). Herramientas 3 %
(pala, pico, barreta, sierra para PVC, taladro). MO 11.67 + materiales 8.54 + equipos 0.35 = 20.56 S/und. El usuario la pidió también
"sola" en Excel (08/10); el 15/10 quedó dentro de la planilla y se borró el Excel aparte.

### 10.10 Otros libros de ACU
- Libro aparte del 07/10 (pedido del usuario): RESUMEN DE METRADOS, DESAGREGADO TAPA REGISTRO, ACU CANALETAS, ACU TAPA REGISTRO,
  COLECTOR INSUMOS, COLECTOR REGISTROS Y TAPAS en un Excel separado.
- `entregables/DESAGREGADO_LIJA_THINNER_TAPA_REGISTRO_HOGAR_REFUGIO.xlsx` (14/10, `acu_lija_thinner.py`): el global "Lija y
  thinner" (glb, 0.05 glb/m², S/ 25.42) se desagregó en lija para fierro N° 80 = 0.25 und/m² (1 pliego cada 4 m²) y thinner acrílico =
  0.024 gal/m² (15 % del volumen de pintura, 0.08 + 0.08 gal/m²). Quedó superado por la tapa ciega (sin pintura).
- `entregables/COTIZACION_PRECIOS_ACU_TAPA_REGISTRO_HOGAR_REFUGIO.xlsx` (14/10, `cotizacion_tapa_registro.py`): hojas 1 COTIZACION
  (insumo, producto cotizado, presentación, precio publicado, contenido, IGV, precio sin IGV = publicado / contenido / 1.18, precio
  actual, variación, tienda, enlace, estado con color verde = comprobado, naranja = referencia de otra ciudad, rojo = sin precio
  publicado), 2 ANGULOS (ángulos comerciales y verificación del contramarco: tapa 0.68² x 0.08 x 2400 kg/m³, sobrecarga peatonal 500
  kg/m² E.020, Wu = 1.4D + 1.7L, área de apoyo 4 x 0.68 x (ala − holgura), aplastamiento ≤ 0.65 x 0.85 x f'c (E.060 10.17) → CUMPLE) y
  3 ACU COMPARATIVO (actual frente a propuesta). Nota del script: no volver a correrlo (la planilla ya tiene la ACU nueva).

### 10.11 ACU de partidas globales del CAR Mujeres (IISS, 15/10)
- Pedido: "dame el ACU solo de las partidas del metrado que está en global", con CAPECO 2026. `mujeres/acu_globales_m.py` sobre
  `insumos/wilma/METRADOS_IISS_CAR_MUJERES_DREA.xlsx` (hoja PLANILLA): 4.2.3.1.1 a 4.2.3.1.7 (líneas de cisterna y tanque elevado,
  prueba hidráulica) y 4.3.6.3.3 (tecle de palanca para caballete). Cantidades de materiales leídas de la planilla; filas irregulares
  avisadas en OBSERVACIONES; rendimientos por tipo de componente con tabla de cálculo (días-cuadrilla); MO 28.95/22.68/20.54;
  precios publicados con IGV / 1.18 (`mujeres/precios_globales_m.py`: insumo, und, producto, presentación, precio con IGV, contenido,
  tienda, enlace, estado EXACTO o EST.).
- 15/10 14:58-15:01: el usuario no quiere glb sino "por metro" para poder valorizar. Opción B aprobada (`mujeres/acu_por_metro_m.py`):
  tubería por m y cada accesorio por und (una subpartida por fila; filas repetidas del mismo insumo se suman); prueba hidráulica por
  m³ (32 + 15 m³ del programa arquitectónico); tecle por und. El cambio de unidad es solo en el libro de ACU. La partida 4.2.3.1.8 de
  prueba hidráulica de líneas tiene 67 m aunque el desagregado sume 77.64 m: vale el Excel original.
- Pregunta del 15/10 14:35: convertir las ACU a S10 o Delphin Express: no es posible directamente (formato propietario); el usuario
  cerró el tema.
- Salida: `entregables_mujeres/ACU_IISS_CISTERNA_TANQUE_Y_TECLE_POR_METRO_Y_UNIDAD_CAR_MUJERES.xlsx` (RESUMEN, MANO DE OBRA 2026,
  PRECIOS DE INSUMOS y una hoja por partida).

---

## 11. Precios de insumos (sin IGV) y sus fuentes

| Insumo | Und | Precio S/ sin IGV | Fuente (precio publicado) | Estado |
|---|---|---|---|---|
| Cemento Portland tipo I 42.5 kg | bol | 30.93 | Cemento Pacasmayo tipo I, S/ 36.50 con IGV (Ferretería Dinova; marca distribuida en San Martín) | comprobado |
| Arena gruesa | m³ | 40.68 | Agregados Tarapoto (Jr. Felipe Yap 220, Morales), S/ 48.00 el m³ | comprobado local (si no emite factura, usar 48.00 directo) |
| Piedra chancada 1/2" | m³ | 101.69 | sin precio publicado de 1/2" (la de 3/4" está a S/ 70.00 en el mismo proveedor) | por cotizar en Tarapoto |
| Agua | m³ | 8.33 | EMAPA San Martín, categoría comercial de 30 m³ a más: agua 6.80 + alcantarillado 1.53 (Res. 00077-2024-SUNASS-CD); tarifa sin IGV | comprobado |
| Madera tornillo | p² | 4.41 | Maderas del Norte, S/ 5.20 el p² con IGV | referencia (la página no indica ciudad) |
| Acero corrugado fy=4200 (ponderado tapa) | kg | 3.44 | Sodimac Perú, Aceros Arequipa: 1/2" x 9 m (8.946 kg) S/ 36.50 y 3/8" x 9 m (5.04 kg) S/ 20.35 con IGV | comprobado (precio nacional) |
| Alambre negro N° 16 | kg | 5.08 | Sodimac Perú, rollo de 10 kg S/ 59.90 con IGV (Prodac) | comprobado |
| Ángulo L 1 1/2" x 1 1/2" x 1/8" | kg | 3.08 | Sodimac Perú, barra de 6 m (10.98 kg) S/ 39.90 con IGV (Tupemesa) | comprobado; el L 2"x2"x3/16" no tiene precio publicado en el Perú |
| Soldadura cellocord E6011 1/8" | kg | 18.63 | Sodimac Perú, caja de 5 kg S/ 109.90 con IGV | comprobado |
| Pintura anticorrosiva | gal | 44.92 | Promart, anticorrosivo Vencedor 1 gl S/ 53.00 | comprobado |
| Esmalte sintético | gal | 48.31 | Promart, esmalte CPP 1 gl S/ 57.00 | comprobado |
| Lija para fierro N° 80 | und | 2.12 | Sodimac Perú, 3M grano 80 S/ 2.50 | comprobado |
| Thinner acrílico | gal | 35.65 | Sodimac Perú, TOPEX 3.5 L S/ 38.90 | comprobado |
| Mezcladora 9-11 p³ | hm | 12.71 | Konstrutecnia (Juliaca) S/ 15.00 la hora | referencia de otra ciudad |
| Vibrador de concreto | hm | 11.02 | Konstrutecnia (Juliaca) S/ 13.00 la hora | referencia de otra ciudad |
| Máquina de soldar 250 A | hm | 8.00 | sin tarifa publicada | por cotizar |
| Plancha de tecnopor 1" x 1.20 x 2.40 | pln | 11.78 | Sodimac Perú (Dipropor) S/ 13.90 con IGV | comprobado |
| Asfalto líquido RC-250 | gal | 15.00 | Conselva S/ 17.70 con IGV (Petroperú publica lista ex planta) | confirmar en Tarapoto |
| Tubo PVC desagüe 3" x 3 m (Pavco) | m | 11.27 | Sodimac Perú y Promart S/ 39.90 el tubo | comprobado |
| Grava filtrante 20-40 mm | m³ | 59.32 | Agregados Tarapoto: piedra chancada 3/4" S/ 70.00 puesto en obra (lo más cercano publicado) | por cotizar grava 20-40 |
| Geotextil no tejido 200 g/m² | m² | 4.87 | Ferrópolis Perú, rollo 4 x 100 m S/ 2,300.00 (5.75 el m² con IGV) | comprobado |
| Plancha galvanizada e = 0.9 mm | m² | 26.95 | "Mercado Tarapoto 2026, sin IGV (referencial)" | referencial |
| Platina F°G° 1" x 1/8" | m | 6.36 | "Mercado Tarapoto 2026, sin IGV (referencial)" | el usuario pidió sustento (09/10); sigue referencial |
| Remache pop 1/8" / sellador PU 300 ml / perno de expansión 1/4" / tornillo autorroscante | und | 0.10 / 21.19 / 1.02 / 0.25 | referenciales | referencial |

Criterios: se aceptan precios nacionales de Sodimac y Promart (tienen tienda en Tarapoto; el precio local puede variar); se prioriza
el proveedor local (Morales/Tarapoto) cuando publica; se marca "por cotizar" lo que no tiene precio publicado y se deja el precio
anterior; cada precio queda con tienda, enlace y fecha de búsqueda (14/10/2026). Nota en las ACU: "Precios sin IGV obtenidos de precios
publicados (octubre 2026), con su fuente en la columna H; los marcados por cotizar deben confirmarse en Tarapoto". Precios anteriores
(07/10, "mercado Tarapoto 2026 referencial"): ángulo 4.66, soldadura 13.56, cemento 30.51, arena 50.85, agua 5.00, madera 5.08, acero
3.81, anticorrosivo 59.32, esmalte 55.08, global lija y thinner 25.42.

Pendientes de cotizar en Tarapoto: piedra chancada 1/2", grava de 20 a 40 mm, alquiler de soldadora (y la platina y plancha
galvanizada de canaletas siguen como referencial).

---

## 12. Técnica de edición del Excel por XML y verificación con LibreOffice

### 12.1 Por qué
openpyxl, al guardar, pierde imágenes de encabezado (logos VML), estilos y fórmulas compartidas. Desde el 07/10 todas las ediciones de
planillas del usuario se hacen sobre el XML del .xlsx (zip) para conservar formato, logos y fórmulas. openpyxl solo se usa para LEER
(con `data_only=True` para valores) o para libros nuevos generados por completo.

### 12.2 Clase `Libro` (`herramientas/angulo_contramarco_refugio.py`)
- `Libro(f)`: lee todas las partes del zip; separa `sharedStrings` en `<si>`; mapea nombre de hoja → `xl/worksheets/sheetN.xml` vía
  `workbook.xml` y `workbook.xml.rels`.
- `hoja(nom)`: XML de la hoja (cacheado en `self.x`).
- `leer(nom, ref)`: valor de la celda (texto compartido o `<v>`).
- `texto(nom, ref, t)` (busca o agrega el string compartido, `t="s"`), `num(nom, ref, v)` (`t="n"`), `formula(nom, ref, f)`
  (`<f aca="false">…</f><v>0</v>`), `cambiar(nom, ref, viejo, nuevo)` (reemplazo con assert). Conservan el estilo `s` de la celda.
- `desplazar(nom, desde, hasta, d)`: baja d filas un bloque (debe haber filas libres debajo) y corrige referencias de la misma hoja en
  fórmulas, en el rango `ref="…"` de las fórmulas compartidas (`<f t="shared" ref=…>`, corrección del 19/10) y en `mergeCell`; las
  referencias a otras hojas no cambian.
- `insertar_copia(nom, origen, nueva)`: inserta una fila copiando otra (estilos incluidos).
- `guardar(f)`: reescribe sharedStrings (con `uniqueCount`) y las hojas modificadas; zip temporal y `move`.
- Auxiliares en `acu_juntas_refugio.py`: `Hoja` (compone una hoja nueva con los estilos de la ACU TAPA REGISTRO: `fila`, `banda`,
  `xml`), `encabezado` (copia las filas 2-5 de la plantilla), `tabla_datos`, `acu`, `agregar_hoja` (agrega sheetN.xml, entrada en
  workbook.xml, relación y Override en `[Content_Types].xml`), `estilo_amarillo4` (nuevo xf con 4 decimales).
- En `varones/planilla_como_refugio.py`: `vaciar`, `estilo`, `poner_estilo`, `estilo_fila`, `fila_de` (buscar fila por texto),
  `formula_txt` (fórmula de texto `t="str"`), `borrar_filas_resumen` (quita filas del RESUMEN y sube las de abajo).
- `varones/portar_hojas_v.py`: copia hojas de un libro a otro con sus estilos (fuentes, rellenos, bordes, formatos) y re-enlaza cada
  fórmula a las celdas equivalentes.
- `metrado_xlsx.reinyectar_vml`: si se usó openpyxl, reinyecta las imágenes de encabezado; comprobar el orden de elementos de cada
  hoja (`legacyDrawingHF` después de `rowBreaks`).

### 12.3 `recalcular(f, hojas)`
1. Copia el libro quitando los `<v>` de las celdas con fórmula (para que LibreOffice calcule todo).
2. `soffice --headless --convert-to xlsx` en una carpeta temporal.
3. Lee los valores con openpyxl `data_only=True`.
4. Escribe en el XML original el valor en caché de cada celda con fórmula (`t="n"` o `t="str"`), sin tocar la fórmula; ignora errores
   (`#…`). Devuelve el número de celdas actualizadas. Excel recalcula de todos modos al abrir.

### 12.4 Verificación obligatoria
- Antes/después: comparar todos los valores de todas las hojas (recalculadas); el informe tipo es `entregables/METRADO_COMPARACION_
  ANTES_DESPUES.txt` (celdas originales con contenido por hoja, modificadas 0; hojas nuevas; "SIN CAMBIOS en el contenido original").
- Buscar celdas con error (`#REF!`, `#VALUE!`) tras recalcular.
- Asserts de estado inicial en cada script ("la planilla ya fue modificada") para no aplicar dos veces un cambio.
- Controles CONFORME/REVISAR dentro de los desagregados.
- Al insertar bancas (19/10 y 22/10): 760 valores anteriores del Refugio comprobados iguales; en el CAR Mujeres todo el resto solo baja
  de fila (PLANILLA +6, RESUMEN +5).

---

## 13. Especificaciones técnicas

### 13.1 Motor
`herramientas/especificaciones/espec.py <proyecto>` → `especificaciones/_json/<proyecto>.json` → `node docx_espec.js <json> <docx>`.
- Lee las partidas (código, descripción, unidad) del RESUMEN del metrado vigente: no se agregan ni se quitan partidas; orden, códigos
  y unidades son los del metrado. Títulos = filas sin unidad (sin medición ni pago propio).
- Diccionario `PROYECTOS` (varones, refugio, mujeres) con archivo de metrado, CUI, nombre corto, `colector` (nombre, L, b, em, ef, es,
  es_cam, solado, zanja, NPT, cotas de fondo, S 0.30 %, registros, juntas y su número, tramos, acero, recubrimientos, receptor, cajas,
  salida, cerco, vereda, planos, contramarco, sello), `lam_llor`, `laminas` (mapa de códigos de trabajo → códigos del juego del usuario,
  aplicado al final sobre el JSON), `junta_cuneta_seccion`, `lamina_rejilla`. Datos comunes de cuneta en `CUNETA` (b 0.40, muros/losa/tapa
  0.10, solado E=4", junta 3.00, tapa 0.60 x 0.60 x 0.10 con parrilla 3/8" @0.15, dado 0.40 x 0.40 x 0.35, falsa columna 0.20 x 0.15 x
  1.30, S 0.50 %, canaletas S 1.00 % n 0.013, cunetas n 0.015, rejilla 1.00 m, rebaje 0.05, soportes @0.60).
- Detecta si una partida está dentro del capítulo del colector (subárbol del título que contiene "COLECTOR PLUVIAL").
- `espec(pt, P, ctx)` despacha por palabras clave de la descripción (LIMPIEZA, TRAZO, EXCAVA, REFINE, RELLENO, ELIMINACI, TAPA DE REGISTRO
  + CIEGA, TAPA DE REGISTRO, CONTRAMARCO, MARCO, PINTURA, ANGULOS, SOLADO, DADO, CICL, EMBOQUILLADO, CURADO, ACABADO/FROTACHADO, ENCOFRADO,
  ACERO, CONCRETO, LLORADERO, REJILLA, TAPA DE INSPECCION, JUNTA, bancas 01.04.03.05.04.*, SOPORTE, TAPA LATERAL, BOQUILLA, COLGADOR,
  ABRAZADERA, FALSA COLUMNA, MONTANTE, CANALETA, TUBER, SUMIDERO, CODO/TEE; genérico al final). El orden importa (p. ej. "TAPA DE REGISTRO"
  y "CIEGA" antes que la tapa con marco).
- `acentos()` pone tildes al texto redactado sin tildes (diccionario `_MAP` y futuros en "-ará"), y `laminas` reemplaza códigos.
- Barranquita: `barranquita/espec_b.py` usa el mismo motor (código "C.I. N.°" vía `J.codigo`; carátula con foto vía `J.caratula`).

### 13.2 Estructura de cada partida (función `bloque`)
DESCRIPCION · MATERIALES · EQUIPOS Y HERRAMIENTAS · PROCEDIMIENTO DE EJECUCION · CONTROL DE CALIDAD Y TOLERANCIAS · SEGURIDAD Y SALUD
EN EL TRABAJO · (extra) · UNIDAD DE MEDIDA · METODO DE MEDICION · FORMA DE PAGO. Forma de pago estándar: "El pago se efectuará al precio
unitario del presupuesto por <unidad>, de acuerdo con el avance valorizado y con la conformidad de la Supervisión. Dicho precio y pago
constituye compensación total por la mano de obra (incluidas las leyes sociales), los materiales, el equipo, las herramientas, el
transporte interno y todo imprevisto…". Bloques de seguridad reutilizables: EPP (DS 011-2019-TR y G.050), SEG_EXC, SEG_CONC, SEG_ACERO,
SEG_SOLD, SEG_ALTURA.

### 13.3 Capítulo I: generalidades
1.1 Generalidades (alcance, numeración y unidades del metrado; planos, memoria y metrado forman parte); 1.2 Ubicación (clima cálido y
lluvioso, ACI 305R); 1.3 Normas aplicables (RNE OS.060, CE.040, IS.010, E.020, E.050, E.060, E.090, G.050; DS 011-2019-TR; Norma Técnica
de Metrados RD 073-2010/VIVIENDA/VMCS-DNC; NTP 334.009, 400.037, 339.088, 341.031, 339.036, 339.035, 339.033, 339.034, 339.141, 339.143,
399.003; ASTM A615, A36, A653, A123, C920, D2564; AWS D1.1 y A5.1; ACI 318, 301, 304R, 305R, 308R, 347); orden de prelación planos →
especificaciones → memoria → metrado; 1.4 Materiales (tabla material / requisito / norma; juntas con sellador asfáltico RC-250 + arena
cuando `sello = asfaltico`); 1.5 Concreto (f'c 100 solado, 140 dados y ciclópeo, 175 cunetas y falsas columnas, 210 colector, cajas y
tapas; slump 3"-4" armado y 2"-3" simple; mezclado ≥ 1.5 min; colocación < 45 min, caída ≤ 1.50 m, capas ≤ 0.30 m; vibrado 0.40-0.50 m
por 5-15 s; clima cálido ≤ 32 °C; curado ≥ 7 días); 1.6 Encofrados (ACI 347; tolerancias 6 mm en 3 m, −6/+12 mm; desencofrado de
costados a 24 h y fondos de losa a 7 días o 70 % f'c); 1.7 Acero (E.060 cap. 7; ganchos de 0.15 por lado; traslapes 0.40 para 3/8" y
0.50 para 1/2", máx. 50 % en una sección; alambre N° 16); 1.8 Control de calidad y ensayos (tabla de frecuencias: probetas 1 al día,
cada 50 m³ y cada 300 m², aceptación E.060 5.6.3.3; Proctor modificado; densidad de campo ≥ 95 %; prueba hidráulica 15 min sin fugas;
diamantina E.060 5.6.5); 1.9 Seguridad, salud y medio ambiente; 1.10 Medición y pago (Norma Técnica de Metrados, hasta el metrado
del expediente).

### 13.4 Partidas especiales (resumen del texto)
- Tapa de registro ciega: rebaje 0.70 x 0.70 x 0.08 formado con un cajón de madera de dos niveles (0.70 x 0.70 x 0.08 y 0.60 x 0.60 x
  0.12) fijado al encofrado; tapa fabricada aparte sobre tablero, molde de 0.68 x 0.68 x 0.08 con chaflanes, parrilla con recubrimiento
  2.5 cm, asas con tacos para las cajuelas; desmolde a 24 h y curado 7 días; sin soldadura ni pintura; colocación con dos operarios, al
  ras, sin mortero (removible). Control: rebaje ±5 mm, tapa ±2 mm, ras ±3 mm. Varones: borde engrosado solo en 2 lados.
- Tapa con marco y contramarco (CAR Mujeres): texto con contramarco del proyecto (`CONTRAMARCOS`), anclajes, soldadura E6011, pintura
  2 manos anticorrosivo + 2 esmalte; Varones con ganchos de (1.40 − 2(b/2 + e − 0.04))/2 m dentro de los muros.
- Juntas: dilatación del colector (anillo de tecnopor, acero longitudinal interrumpido a 0.05 m, retirar 2" de tecnopor en caras
  interiores y superior, RC-250 caliente con arena compactado con tacos); junta contra el cerco (plancha de 0.90 m pegada al cimiento
  antes de vaciar el muro; lado vía terreno natural sin junta); junta con la caja CL (Varones; vista C de la DD-03); juntas de cunetas
  en toda la U (EG-2013 MTC Sección 510; medición 2 x H + 0.40 por junta).
- Rejilla móvil: módulos de 1.00 m de platinas 1" x 3/16" de canto @1" soldadas a 2 ángulos L 1" x 1" x 3/16"; 0.497 m de ancho en
  rebaje 0.05 x 1"; 20.0 kg/m; pintura 2 + 2 manos; junta con el piso de 1" con relleno asfáltico; medición solo en tramos abiertos.
- Lloraderos: tubo PVC-U 3" de 0.30 m a media altura con S 0.5 % hacia la cuneta, filtro 0.30³ de grava 20-40 mm forrado con geotextil
  clase 2 (traslape 0.10), tubos fijados al encofrado @1.50 m, a ≥ 0.30 m de las juntas, tapados al vaciar; prueba echando agua en el
  filtro; cuadro de materiales tomado de DESAGREGADO LLORADEROS (`desagregado_llor`). Láminas: Refugio DPL-40/38/37, Varones
  DPLV-43/35/34.
- Canaleta de bancas OC-01 (Refugio): plancha galvanizada 0.50 mm ASTM A653 G90, desarrollo 0.70 m (0.18 + 0.21 + 0.21 + 0.10 de ala),
  un tramo por techo, S 0.5 %, 2 soportes, 2 tapas, 1 boquilla (brida 0.16 x 0.16, cuello Ø 0.10 x 0.15, reemplaza al sumidero tipo
  cúpula); trabajo en altura 2.80 m (SEG_ALTURA).
- Falsa columna: 0.20 x 0.15 x 1.30, 4 barras de 3/8" de 1.20 m y estribos de 3/8" @0.15 (desarrollo 0.58), recubrimiento 0.04; partida
  en und sin pago propio. Leyenda en DXF: `espec_falsa_columna.py` (bloque ESPEC_FALSA_COLUMNA, valores leídos de la PLANILLA de cada
  proyecto).
- Acero: medición por peso nominal (3/8" = 0.56; 1/2" = 0.994 kg/m) con ganchos y traslapes, sin desperdicios ni alambre.
- Concreto de cunetas: losa y luego muros (o encofrado interior suspendido), rebaje de 0.05 para la rejilla con anclajes de fierro
  corrugado 1/4", pendiente 0.5 % sin contrapendientes, juntas cada 3.00 m.

### 13.5 Leyendas de especificaciones para los planos (DXF, 10/10)
- `leyenda_cunetas.py` (CAR Varones): bloque LEYENDA_ESPEC_CUNETAS a escala real, letra igual a la de las secciones del proyectista
  (0.031 / 0.038 m), con datos de las hojas de cunetas y lloraderos.
- `espec_lloraderos.py` (Refugio y Varones): leyenda y detalle; el sub-dren se retiró ("borró el subdrén, entonces solo lloraderos",
  10/10 04:14). 22/10: para el Refugio el detalle se dibuja sin patrones de achurado (rellenos sólidos, piedras de grava una por una,
  "m3" en lugar de "m³") porque en AutoCAD se veían mal.

### 13.6 Láminas citadas por proyecto (mapa `laminas` de espec.py)
- Varones: "DP-06B, DP-06D, DD-01 y DD-02" → "DPLV-23, DPLV-26, DPLV-27 y DPLV-28"; DD-03 → DPLV-29; DJ-01 y DJ-02 → DPLV-31 y DPLV-32;
  DJ-03 → DPLV-33; planos DPLV-01 a DPLV-44.
- Refugio: "DP-06B, DP-06D, DD-01 y DD-02" → "DPL-24 y DPL-29"; DP-06B → DPL-24; DD-03 → DPL-28; DD-04 → DPL-25; las citas DJ-01/02/03
  se quitan (son láminas del CAR Varones; corrección del 23/10); planos DPL-01 a DPL-42 (incluye las bancas OC-01).
- CAR Mujeres: planos DP-01 a DP-10 (sus códigos nuevos del juego ANDFY se aplicaron en la memoria hidrológica, no en el metrado).

### 13.7 Formato del Word (`docx_espec.js`)
A4, márgenes 3.0 cm izquierdo y 2.0 cm el resto, Arial; portada (entidad, "EXPEDIENTE TÉCNICO" o carátula con foto si el JSON trae
`caratula`, "ESPECIFICACIONES TÉCNICAS", especialidad "INSTALACIONES SANITARIAS - DRENAJE PLUVIAL", proyecto, CUI o C.I., ubicación,
fecha SETIEMBRE 2026); índice automático (TableOfContents, niveles 1-4); CAPÍTULO I GENERALIDADES (1.1 …); CAPÍTULO II ESPECIFICACIONES
TÉCNICAS POR PARTIDA (encabezados con código, descripción y unidad; nivel según la profundidad del código); apartados en azul 1F3864;
viñetas; tablas con cabecera D9E2F3; encabezado "ESPECIFICACIONES TÉCNICAS - DRENAJE PLUVIAL" + proyecto y código; pie "Página X de Y".
En Barranquita la carátula dice "SERVICIO DE DISEÑO - DRENAJE PLUVIAL" (corrección del 21/10), no "EXPEDIENTE TÉCNICO".

### 13.8 Historia de las especificaciones
- 08/10 03:35: el usuario pidió las especificaciones de los 3 proyectos "tal cual completito, normativas peruanas, al más mínimo
  detalle cómo se construirá"; 08/10 03:53: "revísalo antes de presentarlo; tú ya sabes qué dicen los planos" (los datos salen de los
  planos y del metrado, no se preguntan).
- 08/10: especificación de lloraderos agregada a Refugio y Varones; 08/10 04:42 las del CAR Mujeres.
- 15/10, 16/10: juntas asfálticas, tapa ciega, rejilla DJ-03, junta de cunetas en toda la U.
- 22/10 y 23/10: Refugio con el metrado con bancas (4 partidas 01.04.03.05.04 con texto propio) y láminas DPL; Varones con láminas DPLV y
  cuadro del desagregado de lloraderos (tubo 67.80 m, 1808 perforaciones, grava 6.71 m³, geotextil 134.24 m², mortero 0.11 m³). Refugio:
  50 páginas.
- 21/10: Barranquita, 20 páginas, mismo motor.

Comandos: `python3 herramientas/especificaciones/espec.py refugio && node herramientas/especificaciones/docx_espec.js
herramientas/especificaciones/_json/refugio.json entregables/ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL_HOGAR_REFUGIO.docx`
(análogo con `varones` → `entregables_varones/…`, `mujeres` → `entregables_mujeres/…`).

---

## 14. Cronología de pedidos, correcciones y decisiones (metrado, ACU, precios, especificaciones)

| Fecha | Pedido o corrección del usuario | Resultado |
|---|---|---|
| 03/10 | Traspaso: metrado en la plantilla del usuario, partida madre 1.4.4 (hoy 01.04.04), formato de la planilla general, hojas de acero y tapas, desglose de insumos para ACU; no modificar metrados; criterio de rellenos menores. | Hojas COLECTOR … (`metrado_xlsx.py`). |
| 03/10 16:36 | "¿Aumentaste secciones o espesores? ¿el metrado varió?" | Al corregir dibujos (escala real) se verifica que el metrado no cambia. |
| 03/10 17:24 | Objeción a las partidas de prolongación de cunetas en el colector. | Retiradas; la prolongación es cuneta. |
| 03/10 20:09 | Integrar en su planilla con su formato, sin mezclar, justificar cada medida. | Hojas nuevas con SUSTENTO. |
| 03/10 20:41 | "¿Por qué borras mis metrados de concreto y encofrado de cunetas?" | Regla: nunca borrar lo del usuario. |
| 03/10 20:46 | El que cotiza pide detalle de cada componente de registros y juntas. | Láminas DA/DD desagregadas. |
| 04/10 05:17 | Metrar cunetas de Varones con la plantilla, hoja por hoja, "tal cual". | `metrado_varones.py`. |
| 04/10 05:35 | Acero solo con H ≥ 0.40 desde el NCT; tapados siempre; tapa 0.56 @0.25. | Regla del skill `metrado-cunetas`. |
| 04/10 05:40-05:48 | Motor para un programa (MetraP) y guardar el análisis en un skill. | `MetraP/`, skill `metrado-cunetas`. |
| 04/10 06:12 | Restar el tramo de cuneta que cae dentro del colector. | Acortamientos (hoja CUNETAS - LLEGADA AL COLECTOR). |
| 04/10 16:43 | "¿Consideraste lo de 0.40 en Varones?" | Confirmado en la hoja METRADO ACERO. |
| 06/10 23:44-23:57 | Metrado vigente; COMPARATIVO de Delphin; estructura del CAR Mujeres, cantidades propias; solado 4". | Nombres Delphin (39 celdas). |
| 07/10 00:01 | Concreto del colector en una partida como Delphin. | 01.04.04.04.01 única. |
| 07/10 00:07 | Tapas por componentes quedan; ACU detallado en una hoja. | ACU TAPA REGISTRO. |
| 07/10 02:32 | ACU de 4 partidas de canaletas. | ACU CANALETAS. |
| 07/10 02:40 | Tapa por und + hoja de desagregado. | 01.04.04.05.01 (und) + DESAGREGADO TAPA REGISTRO. |
| 07/10 02:47 | Excel aparte con resumen, desagregado, ACU canaletas, ACU tapa, insumos, registros. | Libro aparte. |
| 08/10 01:28-02:37 | Verificar que los planos de Wilma y de Varones coinciden con el metrado; quitar empalme. | Coinciden; 01.04.04.06.03 eliminada. |
| 08/10 04:08 | Lloraderos PVC solo en Refugio y Varones, solo donde la cuneta está junto a área verde. | Partida 01.04.03.04.03.04 + METRADO LLORADEROS. |
| 08/10 04:35 | Sin nombre ni CIP; hoja ACU de lloraderos sola. | – |
| 09/10 15:32-15:37 | Sustento del precio de la platina; precio real; texto para el ingeniero de presupuesto. | Precio referencial explicado (sigue 6.36). |
| 09/10 17:51 | "¿Lo de peón y operario es real?" | Origen de la actualización a CAPECO 2026. |
| 14/10 20:02-20:05 | Desagregado de lija (und) y thinner (gal), en Excel aparte. | `acu_lija_thinner.py`. |
| 14/10 20:12-22:46 | ACU de la junta con el piso; explicar las dos juntas; renombrar a "en colector" y "entre colector y cerco perimétrico"; tecnopor + sellador asfáltico en ambas. | `renombrar_juntas_colector.py`, `acu_juntas_refugio.py`. |
| 14/10 22:58-23:12 | Tapa peatonal (se sabe por el plano); precios reales comprobados; procede el cambio de ángulo. | L 1 1/2"; cotización. |
| 14/10 23:55-23:57 | Ver en el Excel las hojas de ACU y metrado de cada junta; el ACU debe coincidir con los planos. | ACU con cantidades de DD-03. |
| 15/10 00:19-00:26 | Metrado de lloraderos con su hoja y el plano de áreas verdes. | DL-00 + DESAGREGADO. |
| 15/10 01:00 | Junta con cerco solo a un lado; juntas de cunetas según reglamento; MO 2026; ACU de lloraderos. | Junta 58.81 m; juntas en U; COSTO HORA HOMBRE 2026; ACU LLORADEROS. |
| 15/10 02:04 | Varones igual que el Refugio en nombres, manteniendo sus metrados. | `planilla_como_refugio.py` + `portar_hojas_v.py`. |
| 15/10 14:18-15:01 | ACU de partidas globales (IISS CAR Mujeres); luego por metro; vale el metrado original. | `acu_globales_m.py`, `acu_por_metro_m.py`. |
| 16/10 14:45-14:49 | "¿El colector de Varones es de 1.40?" | 1.40 = zanja. |
| 16/10 15:46 | Tapa ciega en los 3 CAR; actualizar solo metrado de Refugio y Varones. | `tapa_ciega.py`. |
| 19/10 00:37-00:43 | Cunetas construidas del CAR Mujeres en m y m². | Respuesta informativa (sin tocar el metrado). |
| 19/10 14:34 | ¿Wilma tiene lloraderos? | No (congelado). |
| 19/10 17:44-19:08 | Metrado de canaleta de bancas (16 techos), meterlo en la planilla general y hoja nueva; agregar codo de 45°. | `bancas_en_planilla_m.py`. |
| 21/10 15:39 | Barranquita en su formato de metrado, cálculo, análisis estadístico y especificaciones; no alterar planos impresos. | `metrado_b.py`, `espec_b.py`. |
| 22/10 13:39-14:03 | OC-01: canaleta 0.21 x 0.18 galvanizada 0.5 mm, 2 sujetadores; metrado solo de canaleta, tapas, sujetadores, boquilla; 9 bancas = 3 juegos; meterlo en el RESUMEN con su hoja. | `metrado_oc01_refugio.py`, `bancas_oc01_en_planilla_refugio.py`. |
| 23/10 17:20 | Especificaciones de Varones con el metrado del 23/10; dónde está el metrado de piedra, tubo, geotextil. | En DESAGREGADO LLORADEROS. |
| 23/10 19:38-19:47 | Cambiar en el metrado solo los códigos de lámina; borrar referencias a láminas excluidas. | `codigos_laminas_metrado_v.py`. |
| 23/10 22:24 | ¿Últimas especificaciones del Refugio? | Las del 23/10; se quitaron citas DJ-01/02/03. |

---

## 15. Pendientes conocidos
- CAR Mujeres: la partida 1.4.4.6.5.1 dice "C/MARCO Y CONTRAMARCO" y el IC-01 dibuja marco; la D-RL y la memoria indican tapa ciega.
  Decisión del usuario (no se tocó: metrado congelado).
- Precios por cotizar en Tarapoto: piedra chancada 1/2", grava 20-40 mm, alquiler de soldadora; plancha galvanizada y platina de
  canaletas siguen como "mercado Tarapoto referencial".
- CAR Varones: tapas de inspección de cunetas = 18 "provisional, 1 por tramo tapado, confirmar con el plano".
- Refugio: la nota de parámetros de METRADO CANALETA BANCAS aún dice "plano DO-02" (hoy DPL-42).
- La planilla vigente del Refugio que guardó el usuario (con bancas) no trae las hojas COLECTOR INSUMOS / ACU / DESAGREGADO; están en
  `entregables/METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx`. Si se piden ACU sobre el archivo con bancas, portarlas (técnica de §12) sin
  cambiar cantidades.

---

## 16. Para implementarlo en un programa

### 16.1 Modelo de datos
```
Proyecto { nombre, cui | ci, entidad, ubicacion, fecha, base_delphin: "CAR_MUJERES", congelado: bool,
           parametros: Parametros, ejes: [EjeCuneta], colector: Colector?, red_techo, red_piso, lloraderos: [TramoLloradero],
           laminas: {codigo_trabajo -> codigo_usuario}, precios: [Precio], mano_obra: ManoObra }
Partida { codigo_metrado, codigo_delphin, descripcion_delphin, unidad, nivel, es_titulo,
          filas_sustento: [FilaSustento], total (calculado), hoja_detalle, espec: EspecPartida }
FilaSustento { descripcion, n_veces, largo, ancho, alto, factor, area, volumen, parcial, formula, sustento_lamina, criterio }
EjeCuneta { nombre, longitud_dibujada, acortamiento, secciones: [Seccion{prog, NCT, NCF, H, tipo: ABIERTA|TAPADA}],
            tramos: [Tramo{sec_ini, sec_fin, tipo, L, H_ini, H_fin, descuento_rejilla}] }
Colector { b, e_muro, e_fondo, e_losa, e_losa_camion, solado, sobreancho, NPT, cf_ini, cf_fin, S, zonas: [Zona{p1,p2,tipo}],
           tramos: [TramoColector{p1,p2,zona,h_medio,Hz_medio,dNPT}], registros: [Registro{codigo, prog, tipo}],
           cajas: [Caja], juntas: {cada, h_max, junta_longitudinal: {tipo: cerco|CL|ninguna, L, h_plancha}}, empalmes }
ManoObra { año, fuente, categorias: {operario: {jornal, ...}, oficial, peon}, costo_hh (calculado) }
Precio { insumo, und, precio_publicado, contenido, igv, tienda, enlace, fecha, estado: COMPROBADO|REFERENCIA|POR_COTIZAR, sin_igv (calc) }
ACU { partida_delphin, partida_metrado, unidad, metrado (link), rendimiento, recursos: [Recurso{tipo: MO|MAT|EQ, nombre, und,
      cuadrilla, cantidad (formula), precio (link), fuente}], herramientas_pct }
EspecPartida { descripcion, materiales, equipos, procedimiento, control, seguridad, unidad, medicion, pago }
```

### 16.2 Cálculo
1. Cunetas: integrar H por eje (∫H dx) con interpolación lineal entre secciones; aplicar acortamientos de llegada al colector; por
   tramo calcular concreto, encofrado (externo +0.10 abierta / +0.20 tapada; fondo de tapa), curado (3 o 4 caras), rejilla (solo
   abierta − descuentos), acero (regla H ≥ 0.40 o tapado; separaciones 0.20/0.22/0.25; barras REDONDEAR.MAS((0.60+2H)/sep); U @0.25
   desarrollo 0.60 + 2(H+0.05); tapa 0.56 @0.25; conteo TEÓRICO o ENTERO), juntas (cada 3.00 m; 2H + 0.40 por junta o 2H en el modo
   antiguo), lloraderos (REDONDEAR.MAS(L/1.50) por tramo junto a área verde), planilla general por eje (1.40 / 0.60 / 0.80 / 1.20).
2. Colector: cortar en tramos homogéneos por zona (normal, motos, camión, quiebres, final), h y Hz ponderados; aplicar las fórmulas de
   §6; acero por marco único o doble (§6) con REDONDEAR.MAS(L/s); registros (tapa ciega §7, descuentos y bordes en la losa); cajas por
   elemento; juntas (ENTERO(L/4) x perímetro; longitudinal solo donde hay cerco o caja).
3. Redondeos: conservar decimales en las hojas de detalle; el total del RESUMEN es la suma de parciales (no redondear antes).
4. ACU: cantidades por unidad desde la lámina de detalle o desde los ratios de INSUMOS; MO = cuadrilla x 8 / rendimiento; precios
   sin IGV = publicado / contenido / 1.18; herramientas % MO; CU y costo de la partida.
5. Precios y MO como tablas versionadas (año, fuente, fecha); una sola fuente para todas las ACU.

### 16.3 Exportación
- Excel: escribir sobre la plantilla del usuario editando el XML (no reescribir con openpyxl), con estilos clonados, fórmulas visibles
  (no valores fijos) y columna SUSTENTO; recalcular con LibreOffice para dejar valores en caché; reinyectar logos si hiciera falta.
- Hojas: RESUMEN → PLANILLA GENERAL → hojas de detalle → PARAMETROS/Listas → COLECTOR … → INSUMOS → COSTO HH → ACU/DESAGREGADOS.
- Word de especificaciones: generar JSON por partida desde el RESUMEN y convertir con `docx_espec.js` (o equivalente), con índice,
  capítulos, encabezado/pie y tildes correctas.
- Planos: los cuadros de partidas de las láminas leen el metrado guardado (JSON de la planilla recalculada), nunca un recálculo propio.

### 16.4 Validaciones obligatorias
- Antes/después celda por celda en todas las hojas existentes: 0 diferencias fuera de lo pedido.
- Sin errores `#` tras recalcular; controles CONFORME en desagregados (desagregado = hoja fuente = RESUMEN).
- Coherencia metrado ↔ planos ↔ especificaciones ↔ memoria: mismo número de registros, juntas, longitudes; los códigos de lámina citados
  existen en el juego del usuario (si no, borrar la cita).
- Reglas de negocio: acero solo con H ≥ 0.40 o tapado; NCF que no cierra con la pendiente → aviso; partidas sin mezclar entre proyectos;
  nombres Delphin de la base CAR Mujeres; proyecto congelado → solo agregar lo pedido.
- No inventar datos que no estén en el plano (montantes, sumideros, dados, tapas de registro, descuentos de rejilla): pedirlos y listarlos
  como pendientes. No preguntar lo que el plano ya muestra.
- Unidades consistentes (m, m², m³, kg, und; "Kgr" → kg); el cambio de unidad para valorizar va solo en el libro de ACU.
- Documentos sin nombre ni CIP de proyectista y sin rastros de IA; todo en español.
