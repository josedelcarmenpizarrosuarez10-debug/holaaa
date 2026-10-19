# Bitácora de trabajo – colectores pluviales (Varones, Hogar de Refugio, CAR Mujeres)

Rama: `claude/colector-pluvial-hogar-refugio-ydbnaf`

## Ayer (6 y 7 de octubre de 2026)

**Hogar de Refugio Temporal – Mujeres Violentadas (Solange, CUI 2675514)**
- Se guardó tu metrado vigente (con canaletas y 52 montantes) como versión de referencia.
- Los nombres de las partidas se adaptaron a la estructura Delphin, sin cambiar las cantidades.
- El concreto del colector quedó en una sola partida y los registros en una partida por und.
- Se agregaron las hojas ACU de la tapa de registro y ACU CANALETAS, la hoja DESAGREGADO TAPA REGISTRO y un libro aparte con RESUMEN, desagregado, ACU e insumos del colector.
- Tapa de registro: lámina 3D, isométricos detallados, vistas del registro instalado y la DP-06B rev. 01 (tapa 0.68 x 0.68 asentada sobre el ala del contramarco).
- Planos del colector: todas las láminas se ordenaron con el estilo nuevo. La DP-06B y los perfiles quedaron congelados.
- Se creó el skill **planos-ordenados**, con las reglas de escala real, etiquetas sin cruces y estilo de láminas.

## Hoy (8 de octubre de 2026)

**1. CAR Mujeres (Wilma, CUI 2717013)**
- Se rehizo el juego de planos del colector a escala real, con láminas DP-01 a DP-10.
- Se verificó el metrado del colector contra los planos y coincide.
- En los planos el solado se dibuja al ancho exterior y se agregó el límite de excavación. El metrado no se tocó.
- Formatos: DP-02, DP-06C y DP-08 en A2, el resto en A1. El índice DP-00 va en A3.
- Cada lámina tiene una presentación de AutoCAD lista para imprimir. El espacio modelo quedó en A1, así que ya no sale "Paper Size Not Found".

**2. CAR Varones (Katiuska, CUI 2705619)**
- Se ordenaron las láminas con el skill. Son 18 láminas, con índice y presentaciones de AutoCAD.
- Perfil nuevo: DP-02 general a 1/100 en A2, y DP-03A y DP-03B de detalle a 1/25, con acero, registros, juntas y la llegada a la caja CL.
- Se corrigieron textos que venían del Hogar de Refugio:

  | Dato | Decía | Ahora |
  |---|---|---|
  | Caudal | 560.6 L/s | 221.7 L/s |
  | Piso | +260.60 | +261.15 |
  | Cerco | sí | no hay cerco |
  | Registros / tapas | 10 | 11 |
  | Juntas | 17 | 26 |

- Los cuadros de las láminas DA leen los valores de tu planilla.
- Se verificó tu metrado (versión con METRADO CANALETAS): las 23 partidas del colector coinciden con los planos.
- Se quitó la partida de empalme (01.04.04.06.03), como pediste: cada cuneta ya se metra hasta el muro del colector, con acortamientos de 0.04, 0.10, 0.26, 3.39 y 2.77 m. Por eso salió de la DA-03 y la DD-04 quedó solo como detalle constructivo.
- Tu planilla reemplazó a la anterior en el repositorio.

**3. Hogar de Refugio (Solange)**
- Se agregaron las presentaciones de AutoCAD de las 22 láminas y el índice DP-00. Las láminas no cambiaron: se comprobó entidad por entidad.

**4. Lloraderos en cunetas junto a área verde (CAR Varones y Hogar de Refugio; CAR Mujeres no se toca porque ya está presupuestado)**
- Partida nueva 01.04.03.04.03.04 LLORADERO DE TUBERIA PVC Ø3" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m (und), con su hoja METRADO LLORADEROS (eje, lado del muro, progresivas, longitud y N°).
- Tramos medidos en la planta general de drenaje: muro de cuneta cuya franja exterior de 0.30 m cae en el achurado de área verde.
- CAR Varones: 226 lloraderos (320.53 m de muro). Hogar de Refugio: 157 lloraderos (226.21 m).
- Ninguna otra partida cambió (comparadas todas, antes y después). Se mantuvieron los logos de los encabezados de la planilla del Hogar de Refugio.
- Planos de verificación: `entregables_varones/LLORADEROS_CUNETAS_AREA_VERDE_VARONES.png` y `entregables/LLORADEROS_CUNETAS_AREA_VERDE_HOGAR_REFUGIO.png`.
- Especificación técnica de la partida agregada a los Word de los dos proyectos.

## 14 de octubre de 2026: tapa de registro del Hogar de Refugio (CUI 2675514)
- Contramarco cambiado de L 2"x2"x3/16" a L 1 1/2"x1 1/2"x1/8" (carga peatonal; el asiento apoya sobre el borde engrosado). Verificación en `entregables/COTIZACION_PRECIOS_ACU_TAPA_REGISTRO_HOGAR_REFUGIO.xlsx`.
- Planilla: ángulos 151.42 → 101.02 kg; pintura 9.82 → 8.39 m²; lija y thinner por separado; ACU con precios publicados y su fuente: 383.29 → 297.45 S/ por tapa (partida 2,974.50).
- Planos DD-01, DD-02, DP-06B, DP-08, DP-09 y DA-03, isométricos 3D y especificaciones actualizados. CAR Varones conserva el L 2"x2"x3/16" (`CONTRAMARCO` en `varones/compat.py`).
- Pendiente por cotizar en Tarapoto: piedra chancada 1/2" y alquiler de soldadora (se dejó el precio anterior).

## 15 de octubre de 2026: juntas del colector del Hogar de Refugio (CUI 2675514)
- DD-03, DP-08, DA-03, especificaciones y memoria: tecnopor 1" + sellador asfáltico 1" x 2" (RC-250 + arena) en la junta de dilatación, contra el cerco y en el borde de la losa (EG-2013 MTC, 510). CAR Varones conserva el sello de poliuretano (`SELLO_JUNTA` en `varones/compat.py`).
- Planilla: hojas ACU JUNTA DILATACION (S/ 12.01/m) y ACU JUNTA CERCO (S/ 6.12/m) con cantidades del DD-03; COLECTOR INSUMOS lee de ellas el tecnopor y el sellador. Metrados sin cambio.
- Junta 01.04.04.06.02: solo la junta LONGITUDINAL entre el muro del colector y el cimiento del cerco (tecnopor 1" de 0.90 m + sellador), de 0+000.00 a 0+058.81. Al otro lado hay terreno natural (sin vereda ni piso): no lleva junta. Partida 210.98 → 58.81 m. Corregidos el metrado, la ACU, DD-03 (vista D nueva), DP-04A/B, DP-08, DP-09, DA-03, las especificaciones y la memoria; se borró el esquema antiguo de juntas.
- Junta de cunetas 01.04.03.04.03.03: en toda la sección en U (2 muros + losa de fondo), EG-2013 MTC Sección 510. Longitud por junta = 2 × H + 0.40; 233 juntas: 241.96 → 335.16 ml. Láminas en `entregables/PLANOS_DETALLE_CUNETAS_JUNTA_Y_REJILLA_HOGAR_REFUGIO.dxf` (vistas previas en `entregables/vistas_previas_cunetas/`): DJ-01 detalle y metrado de la junta; DJ-02 proceso constructivo en 4 isométricos 3D; DJ-03 rejilla móvil (módulo de 1.00 m, 39 platinas 1" x 3/16" @1", 2 ángulos L 1" x 1" x 3/16", rebaje 0.05 x 1", 20.0 kg/m) con isométricos, planta, sección, corte y despiece. Especificaciones actualizadas.
- Mano de obra 2026: hoja COSTO HORA HOMBRE 2026 con la tabla oficial CAPECO - FTCCP 2026 (Exp. N° 339-2025-MTPE/2.14-NC; PDF en `insumos/normas/`): operario 28.95, oficial 22.68, peón 20.54, con su desglose (leyes sociales 112.20 %, BUC, movilidad, overol). Todas las ACU leen de ella.
- Hoja ACU LLORADEROS dentro de la planilla: S/ 20.56 por und, partida S/ 3,227.64 (tubo PVC 3" Pavco S/ 39.90 el tubo de 3 m, geotextil 200 g/m² S/ 5.75/m², grava a S/ 70.00/m³ de Agregados Tarapoto). Se borró el Excel aparte.
- Siguen por cotizar en Tarapoto: piedra chancada 1/2", grava de 20 a 40 mm y alquiler de soldadora.

## 15 de octubre de 2026 (tarde): CAR Varones (CUI 2705619) igual que el Hogar de Refugio
Se mantuvieron los metrados del CAR Varones. Los nombres de las partidas y los criterios son los mismos del Hogar de Refugio.
- **Planilla:**
  - Concreto del colector en una sola partida: 56.02 m³ (55.72 m³ después de corregir el registro, ver abajo).
  - Tapa de registro por und: 11 und.
  - Acabado frotachado de losa superior (vereda).
  - Juntas 01.04.04.06.01 (120.64 m) y 01.04.04.06.02, solo el contacto con la caja CL (4.64 m).
  - Hojas COSTO HORA HOMBRE 2026 (CAPECO - FTCCP: 28.95 / 22.68 / 20.54), ACU TAPA REGISTRO (S/ 292.25), ACU CANALETAS, ACU JUNTA DILATACION, ACU JUNTA CAJA CL, DESAGREGADO TAPA REGISTRO (11 registros), DESAGREGADO LLORADEROS y ACU LLORADEROS (S/ 20.56/und, 226 und).
  - Junta de cunetas en toda la sección en U: 252.29 m (185 juntas).
- **Planos del colector:**
  - Contramarco L 1 1/2" x 1 1/2" x 1/8" (DD-01, DD-02, DP-06B, DP-08, DA-03).
  - Sellador asfáltico 1" x 2" (RC-250 + arena) en todas las juntas.
  - DD-03 nueva: vista C con la junta en la caja CL y vista D con terreno natural a ambos lados (sin junta longitudinal).
  - Leyendas: "losa superior = vereda +261.15".
- **Láminas de cunetas DJ-01 a DJ-03** (junta, proceso constructivo en isométricos y rejilla): `entregables_varones/PLANOS_DETALLE_CUNETAS_JUNTA_Y_REJILLA_CAR_VARONES.dxf`, con vistas previas en `entregables_varones/vistas_previas_cunetas/`.
- **Documentos actualizados:** especificaciones técnicas, memoria Word (tabla de metrados igual a la planilla), memoria de cálculo Excel, leyenda de cunetas y LEEME.
- **Ambos proyectos:**
  - DD-01 y DD-02 citan ahora la partida única 01.04.04.05.01 TAPA DE REGISTRO; ya no citan las antiguas .05.02 a .05.07.
  - DD-04 ya no cita la partida 01.04.04.06.03, que no existe en la planilla Delphin: la cuneta se metra hasta el muro del colector.
- **Registro de limpieza de Varones (corregido):** la abertura de 0.70 es más ancha que su colector de 0.60.
  - En los lados largos, el contramarco apoya en la cabeza de los muros y los anclajes bajan dentro del muro.
  - El borde engrosado va solo en los 2 lados transversales, entre muros: 2 × 0.60 = 1.20 m por registro; antes se había copiado el de 3.00 m del Refugio.
  - Las barras transversales de borde siguen midiendo 1.40 m, con ganchos de 0.29 dentro de los muros.
  - Concreto del colector: 56.02 → 55.72 m³ (COLECTOR PARAMETROS, fila 40).
  - Se corrigieron DP-06B, DD-01, DA-02, especificaciones y memoria, y se agregó la DP-06D de Varones (19 láminas).
- **Cadena de colectores verificada:**
  - Varones (0.60): cota de fondo 260.20 → 259.884, 221.7 + 37.0 = 258.7 L/s a la caja CL.
  - Refugio (0.80): cota de fondo 259.10 → 258.88, entrega 560.6 L/s en R-01 (cota de fondo 258.72, nivel de agua 259.062).
  - Mujeres (1.50): cota de fondo 258.72 → 258.30, nivel de agua inicial 259.063.
  - El ancho crece aguas abajo y las cotas y los niveles empalman.
- **Empalme Refugio → Mujeres (corregido):** la ventana de salida de la caja CC hacia el R-01 mide 1.50 × 0.43, el alto interior del colector del CAR Mujeres en su R-01 (losa 259.25 − 0.10 − fondo 258.72).
  - Antes el perfil la dibujaba de 0.43, la DP-07 de 0.60 (pasaba por encima del piso de Mujeres) y la planilla descontaba 0.842.
  - Concreto del Refugio: 58.31 → 58.41 m³.
  - Revisados también: llegada de Varones a la caja CL (ventana 0.60 × 1.17 en su muro este, techo 261.05 igual en ambos expedientes, caída libre de 0.28 sobre el nivel de agua 259.606), salida del Refugio de la CL (0.80 × 1.40) y ubicación UTM del R-01 (345666.974, 9282776.560), igual en el Refugio y en Mujeres.
- **Ambos proyectos:** DA-02 muestra el total de concreto del colector (Refugio 58.41 m³ = su partida 01.04.04.04.01) y el acabado con su nombre Delphin ("frotachado de losa superior (vereda)").

## 16 de octubre de 2026: tapa ciega en los 3 CAR y estudio de riesgos de la SM-107
- **Tapa ciega de concreto armado** (sin marco metálico) en lugar de tapa con marco y contramarco:
  tapa 0.68 × 0.68 × 0.08 vaciada en obra, parrilla 3/8" @0.10, 2 asas de fierro liso 1/2" en cajuelas, asiento en rebaje de
  concreto 0.70 × 0.70 × 0.08 de la losa (luz 0.60), borde engrosado y refuerzo de borde 8 Ø 1/2".
  - DP-06B nueva en los 3 CAR (sueltas: `entregables_solange/PLANO_DP-06B_DETALLE_TAPA_REGISTRO.dxf`,
    `entregables_varones/PLANO_DP-06B_DETALLE_TAPA_CIEGA_CAR_VARONES.dxf`, `entregables_mujeres/PLANO_DP-06B_DETALLE_TAPA_CIEGA_CAR_MUJERES.dxf`).
  - Metrado actualizado solo en Refugio (10 tapas, ACU S/ 182.06) y Varones (11 tapas); CAR Mujeres sin cambio en su metrado.
  - DD-01, DD-02, DP-06D, DP-08, DP-09, DA-03, isométricos y fotos 3D, especificaciones y memorias actualizados.
- **Estudio de gestión de riesgos en la ejecución de obra** de la vía SM-107 Tingo de Ponasa – Shamboyacu (CUI 2673852):
  Word, matriz Excel con fórmulas (34 riesgos, 3 oportunidades, P x I, valor esperado, Monte Carlo) y planos PR-01/PR-02
  en `gestion_riesgos/proyectos/SM-107_TINGO_DE_PONASA_SHAMBOYACU/` (carpeta propia `gestion_riesgos/`). Efectos en % del presupuesto; sin montos ni observaciones a los documentos.
- Se crearon `CLAUDE.md` (reglas y mapa del proyecto) y el skill `diseno-colector-pluvial` para continuar en otra conversación.

## Cómo imprimir (los tres proyectos)
1. Abrir la pestaña de la lámina (DP-00, DP-01, ...).
2. Ctrl+P: área = Presentación, escala 1:1, centrar.
3. Elegir tu plotter con el mismo papel. "DWG To PDF" solo sirve para que AutoCAD encuentre los papeles ISO.
4. Para imprimir todas las láminas de una vez: PUBLISH.

## Archivos
| Proyecto | Planos | Vistas previas | Notas |
|---|---|---|---|
| CAR Mujeres | `entregables_mujeres/PLANOS_COLECTOR_MEJORADOS/PLANOS_COLECTOR_PLUVIAL_CAR_MUJERES.dxf` | `entregables_mujeres/PLANOS_COLECTOR_MEJORADOS/vistas_previas/` | `LEEME.txt` |
| CAR Varones | `entregables_varones/PLANOS_COLECTOR_PLUVIAL_CAR_VARONES.dxf` y `PLANOS_DETALLE_CUNETAS_JUNTA_Y_REJILLA_CAR_VARONES.dxf` | `entregables_varones/vistas_previas/` y `vistas_previas_cunetas/` | `LEEME_PLANOS.txt` |
| Hogar de Refugio | `entregables/PLANOS_COLECTOR_PLUVIAL_HOGAR_REFUGIO.dxf` | `entregables/INDICE_DP-00_VISTA_PREVIA.png` | – |

## Reglas que se mantienen
- No modificar los metrados del usuario.
- Vistas previas en PNG; PDF solo si el usuario lo pide.
- Escala real ("si algo mide 0.56, así debe medir").
- No mezclar partidas ni láminas.
- Decir "cota de fondo".
- Citar los proyectos por nombre y CUI.

## 17 de octubre de 2026: carpetas separadas y programa general de PSST
- El estudio de gestión de riesgos de la SM-107 se movió a `gestion_riesgos/` (herramientas y proyectos/<proyecto>/insumos|entregables).
- Se creó la carpeta `PROGRAMA DE ELABORACION DE PSST/`: programa general del Plan de Seguridad y Salud en el Trabajo para cualquier obra
  en el Perú. Lee el presupuesto (S10 en PDF o partidas pegadas en Excel), reconoce las actividades con la biblioteca de peligros, calcula
  el IPERC (R.M. N.° 050-2013-TR, inicial y residual) y genera el Word del plan (estructura G.050 / D.S. N.° 011-2019-TR) y el Excel con fórmulas.
- El usuario pidió solo el programa general: no se deja ningún PSST de proyecto en la carpeta (se retiró el de la SM-107 que se había generado).
- No se encontró en el repositorio ningún PSST anterior de los CAR o del Refugio; si el usuario los sube, se guardan en `proyectos/<obra>/`.

## 19 de octubre de 2026: drenaje pluvial de la banca de jardinería – CAR Mujeres (CUI 2717013)
- Insumo: `insumos/wilma/detalle_banca/DETALLE_DE_BANCA_TIPO_01.dxf` (dibujado a escala real).
- Generador `herramientas/techo/planos_banca_m.py` → `entregables_mujeres/PLANOS_ISOMETRICO_BANCA_JARDINERIA_CAR_MUJERES.dxf`:
  DB-01 isométrico 1/15; DB-02 extremo de la canaleta 1/5 con corte de canaleta y sección C-C de la falsa columna;
  DB-03 corte A-A (lateral) y corte B-B (frontal) 1/10 con cotas y niveles. PNG en `vistas_previas_banca/`.
- Regla del usuario: ser fiel al dibujo. Todo sale del corte A-A y de la planta: canaleta 0.18 x 0.20 (indicación del usuario),
  S = 0.5 %, un solo tramo de 2.00 m por techo (a una agua, sin uniones), boquilla de aluzinc (brida 0.16 x 0.16, cuello Ø 0.10),
  niple, codo, tramo de 0.38 con colgador a la viga 2" x 2", codo, bajada,
  2 soportes de platina 1" x 1/8" a 0.40 de cada extremo (1.20 entre ellos), abrazadera a la columna (+1.77), falsa columna CL-01 0.20 x 0.15 de -0.15 a +1.05, cobertura hasta la cara posterior de la canaleta.
- Diferencias del plano de origen (informadas al usuario): falsa columna rotulada H = 1.50 pero dibujada 1.20; la elevación E2
  la dibuja de 0.15 de ancho y la planta de 0.20; no se indica a dónde descarga la bajada.
- Metrado para 16 techos iguales: `entregables_mujeres/METRADO_CANALETA_Y_ACCESORIOS_BANCAS_CAR_MUJERES.xlsx` (generador `herramientas/techo/metrado_banca_m.py`), sin tubo ni falsa columna.
- Espesor de la canaleta, tapas y boquilla de las bancas: plancha de aluzinc e = 0.50 mm (un tramo de 2.00 m con 2 soportes; los techos principales siguen con galvanizado e = 0.9 mm).

## 19-10-2026 – CAR Mujeres (Wilma, CUI 2717013): canaleta de bancas en la planilla general
- Pedido: meter en el Excel general de metrados (vigente 09-10-2026) solo los 4 ítems de la canaleta de los techos de las bancas
  (canaleta, tapa lateral, soporte, boquilla) y crear una hoja nueva de metrado de ese techo.
- Hecho con `herramientas/mujeres/bancas_en_planilla_m.py` (edición del XML, conserva formato):
  - Hoja nueva METRADO CANALETA BANCAS (formato de METRADO CANALETAS): 16 techos x 2.00 m, 2 tapas, 2 soportes y 1 boquilla por techo.
  - PLANILLA GENERAL y RESUMEN: subtítulo 1.4.4.5.4 RED DE RECOLECCION TECHO DE BANCAS DE JARDINERIA (después de ACCESORIOS),
    ítems 1.4.4.5.4.1 a 1.4.4.5.4.4 = 32.00 m, 32, 32 y 16 und. El resto solo baja de fila (PLANILLA +6, RESUMEN +5); se verificó
    que todos los valores anteriores quedan idénticos.
  - Codos, colgador y abrazadera de las bancas no se agregan: ya están en METRADO MONTANTES (BC-01 a BC-16).
- Corregido en `angulo_contramarco_refugio.py` (desplazar y recalcular): fórmulas compartidas de Excel (`<f t="shared" .../>`).
- Observación (no se cambió): el RESUMEN no tiene fila para el CODO DESAGÜE PVC Ø4" x 45° (PLANILLA 1.4.4.5.3.2).
- Salida: `entregables_mujeres/METRADO_DRENAJE_PLUVIAL_CAR_MUJERES_09-10-2026_CON_BANCAS.xlsx`.
