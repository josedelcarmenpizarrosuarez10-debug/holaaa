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
- A pedido del usuario se agregó al RESUMEN el CODO DESAGÜE PVC Ø4" x 45° (1.4.4.5.3.2 = PLANILLA K161, de METRADO MONTANTES),
  que faltaba; COLGADOR y ABRAZADERA pasan a 1.4.4.5.3.3 y 1.4.4.5.3.4, igual que en la PLANILLA.
- Salida: `entregables_mujeres/METRADO_DRENAJE_PLUVIAL_CAR_MUJERES_09-10-2026_CON_BANCAS.xlsx`.

## 20-10-2026 – I.E. N.° 0590 Barranquita (Lamas): planteamiento preliminar de cunetas
- Insumo: PLANTA_GENERAL_590_2.dxf (332 MB, en dos partes .zip). Proyecto del rótulo: "MEJORAMIENTO Y AMPLIACIÓN DEL SERVICIO DE
  EDUCACIÓN PRIMARIA EN I.E 0590, DISTRITO DE BARRANQUITA, PROVINCIA DE LAMAS", C.I 468901 (confirmar si es el CUI).
- El DXF tiene 3 copias del conjunto; la real es la que está sobre las curvas C-TOPO (175.0 a 188.5 cada 0.50 m, UTM).
  Base reducida en insumos/barranquita/base_sitio.pkl.
- Criterios del usuario: cuneta 0.60 m (muros 0.10 + 0.40 libre), h inicial 0.30 (mínima 0.25), S = 0.5 %, rejillas, tramos tapados
  en cruces de vereda, techos a dos aguas, que toda el agua salga por gravedad.
- Red sobre los ejes del planteamiento del usuario (capas 0_ CUNETAS y 0_REJILLA): 22 ramales, 894.6 m (836.1 con rejilla, 58.6 tapados),
  4 sistemas y descargas D1 (esquina oeste), D2 (perimetral este en y = 860.5, cabecera de la quebrada), D3 (frente sur, ingreso) y
  D4 (ingreso sur-este). Profundidad máxima 0.83 m. Rasante: NTN +184.50 en la plataforma; terreno de las curvas fuera (montículo de
  185.5 recortado a +184.50); conexiones nuevas con rasante recta.
- Entregables: entregables_barranquita/PLANTEAMIENTO_CUNETAS_IE0590_BARRANQUITA.dxf (DC-00 a DC-06), CUADRO_TRAMOS_CUNETAS_IE0590_BARRANQUITA.xlsx,
  vistas_previas/*.png.
- Pendiente de confirmar: receptores de D3 y D4, CUI, caudales con la hidrología; aleros sin cuneta (lado norte de los pabellones oeste,
  lado norte del bloque norte y de la fila central) descargan al terreno hacia la quebrada.

## 20-10-2026 (cont.) – Barranquita: verificacion de 10 puntos, bloques, isometricos y cortes
- verifica_b.py: conectividad, sin contrapendiente, S >= 0.5 %, h 0.30/0.25, empalmes, descargas a la luz, NPT, capacidad con Q de diseno
  (C 0.80, I 211 mm/h tc 10 min de la estacion del Refugio - referencial), V <= 3.0 m/s y muros.
- Hallazgos y correcciones: D3 quedaba 7 cm bajo la calle y el ultimo tramo del frente no tenia capacidad -> D3 se movio al punto bajo
  del frente (x = 925.0, rasante 183.25, C.F. 182.99 = nivel de la calle 183.00); el frente se partio en R-07 (oeste) y R-23 (este) y la
  bajada R-08 llega directo a D3. Seis tramos con V > 3 m/s llevan gradas.
- Resultado: 9 de 10 cumplen; D1, D2 y D4 salen a la superficie a 1.5, 5.5 y 7.0 m; D3 entrega al punto bajo del Jr. Alfonso Ugarte
  (la calle debe evacuar ese punto bajo: confirmar).
- Planta en bloques de AutoCAD; isometricos DC-07 (sur) y DC-08 (norte); cortes DC-09 (A-A a D-D por las descargas) y DC-10 (E-E, F-F).
- Hallazgo: iso3d / dxf_base.iso proyectan en espejo (corregido solo en iso_b.py; las laminas de otros proyectos no se tocaron).

## 20-10-2026 (v2) – Barranquita: todo dentro del cerco perimetrico y 3D solo de cunetas
- Pedido del usuario: el 3D solo de las cunetas, con todo el terreno y todas las veredas (sin edificaciones); el area de intervencion es
  el interior del cerco perimetrico: las cunetas no pueden dibujarse ni proyectarse fuera del cerco, pero el agua si puede salir por el.
  El usuario confirmo el cerco delimitado (revision/CERCO_PERIMETRICO_PARA_CONFIRMAR.png).
- Rediseno: las perimetrales del planteamiento que quedaban fuera del cerco (sur-oeste, frente y este) pasan a 0.60 m por dentro de su eje;
  se elimina el sistema 4 (R-21 fuera del cerco). Quedan 19 ramales, 825.6 m (756.1 con rejilla, 69.6 tapados), 3 sistemas:
  1 oeste -> D1, 2 frente sur -> D3, 3 nor-este -> D2.
- Descargas por el cerco: D1 (lado C22-C1, x = 820.7) y D3 (junto a C14, x = 935.5) con pase en el cimiento del cerco; el terreno
  exterior queda bajo la cota de fondo a 1.0 m y 2.0 m (solo perfilado del terreno, sin obra). D2 (cerco norte, x = 965.5) con poza de
  salida 0.80 x 0.80 que rebalsa a 180.62 (nivel del terreno) hacia el fondo de la hondonada natural (baja 0.25 m a 10.8 m).
- calcula_b.py: la profundidad minima de cada tramo sube hasta que el tirante de diseno deja 0.05 m de borde libre (hmin_req.json).
  verifica_b.py: 11 comprobaciones, todas cumplen (gradas en R-01 P-06-D1, R-12 P-41-P-43 y R-15 P-52-P-41). Corregido: R-11 termina en
  el nudo previo a D3 y se tomaba como descarga (su empalme no se revisaba); ahora 16 empalmes revisados.
- Planos: DC-01 con el bloque LIMITE_DE_INTERVENCION y la poza; DC-06 y DC-07 isometricos solo de cunetas sobre el terreno y las veredas
  (bloques ISO_TERRENO_VEREDAS e ISO_CUNETAS); DC-08 cortes A-A (D1), B-B (D2, poza) y C-C (D3); DC-09 cortes generales; DC-10 detalle
  isometrico de las tres descargas a 1/75 (rejillas, tapados, gradas, poza, cerco y agua). Laminas numeradas correlativas.
- Pendiente: levantamiento de detalle en la hondonada de D2 (curvas cada 0.50 m; el modelo es plano en 180.5), confirmar el CUI, y que
  se acepte el perfilado de 1.0 / 2.0 m de terreno fuera del cerco en D1 y D3.

## 20-10-2026 (v3) – Barranquita: cunetas en las lineas magenta del usuario (techos a dos aguas)
- Insumo: PLANTA_GENERAL_590 ULTIMA VERSION.dxf (381 MB, ZIP en 3 partes: el orden real es PARTE_02, PARTE_03, PARTE_01).
  Curvas C-TOPO, cerco (capa 2), cunetas preliminares y textos NPT iguales a la version anterior; cambian veredas, techos, muros y pisos.
- El usuario trazo 30 lineas magenta (capa 0, 792.6 m) a los lados de cada edificacion: todos los techos son a dos aguas y cada lado
  recibe su canaleta, por eso alli va cuneta. Copia en insumos/barranquita/cunetas_magenta_usuario.json; base_sitio.pkl rehecha.
- Red v3: 19 ramales, 973.3 m (44.5 m tapados), 4 sistemas: 1 oeste -> D1 (339.7 m), 2 centro y frente sur -> D3 (239.4 m),
  3 nor-este y losa -> D2 (301.1 m), 4 norte -> D4 (93.1 m, nueva). Se quitaron las cunetas sin linea magenta (perimetral sur-oeste,
  bajada x=937.3, y=838.8, x=971.7 y el inicio de la perimetral este); quedan solo las uniones necesarias hasta las descargas.
- Descargas: D1 se movio frente al extremo de la linea 0 (cerco C22-C1, x = 820.1); D4 nueva en el cerco norte C3-C4 (x = 911.0) entre el
  bloque norte y el bloque del centro (talud de la quebrada). Pase en el cimiento en D1, D3 y D4 (terreno exterior bajo la C.F. a 0.8,
  1.8 y 0.8 m); poza en D2. El lado oeste y sur de la losa iba primero a D3, pero cruzaba una franja natural a 183.5 delante del frente
  (h = 1.33 y D3 sin salida): se mando por el lado este de la losa a D2. PLAT ampliada en la esquina sur-oeste de la losa (NTN 184.50).
- Verificacion: 11 de 11 (gradas en R-01 al pase D1, R-12 al norte de la losa y R-15 x=971.7 -> perimetral). Profundidad maxima 0.85 m (R-07).
- Planos: 12 laminas (DC-00 a DC-11): cortes A-A a D-D por D1, D2, D3 y D4 (DC-08) y detalle 3D de las 4 descargas (DC-11).

## 20-10-2026 – Revision coordinada de las memorias hidrologicas de los 3 proyectos del colector compartido
- Pedido: revisar que la memoria de Wilma (CAR Mujeres, CUI 2717013) cuadre con Solange (Hogar de Refugio, CUI 2675514) y Katiuska
  (CAR Varones, CUI 2705619), y explicar en detalle por que el colector usa 155.66 mm/h y las cunetas 210.98 mm/h.
- Cuadran: 258.7 + 301.9 = 560.7 L/s (560.68) al R-01; 262.3 L/s Mujeres; 822.9 L/s en la salida; misma lluvia P24 = 121.81 mm,
  TR 25, FS 1.15; cota de fondo de entrega 258.89 >= 258.72; NA 259.062.
- Corregido (solo textos, ningun caudal ni diseno cambia), con herramientas/revision_hidrologia.py (mismo texto en las tres):
  * bloque "Intensidad de diseno: 210.98 mm/h en cunetas y 155.66 mm/h en el colector" (Dick-Peschke con P24, tc = 10 + 3 + 2 = 15 min,
    por que no 210.98 en el colector, C ponderado del colector y caudales compartidos), despues de la tabla de caudales del colector;
  * "Coeficiente adoptado": C = 0.88 para canaletas, montantes, sumideros y cunetas; el colector con C ponderado;
  * el "7,2 %" de la plantilla: 25,0 % (Mujeres, C 0.704), 9,0 % (Refugio, C 0.807), 14,2 % (Varones, C 0.771);
  * Katiuska decia que sus 258.7 L/s salian con I = 210.98: es con I = 155.66 (tc 15 min); su celda de comprobacion (DATOS B13) daba
    350.7 y ahora da 258.7;
  * area del CAR Varones 6 752.03 m2 (la de su memoria) en vez de 6 752.06; C del Refugio 0.807 (no 0.808) en la tabla de Wilma.
- Wilma: copia revisada en entregables_mujeres/MEMORIA_HIDROLOGICA_CAR_MUJERES_CON_COLECTOR.docx (el insumo no se toca).
- Pendiente de decidir: las memorias de calculo en PDF (Refugio y CAR Mujeres) aun dicen 6752.06 y 0.808 (diferencias de redondeo).

## 20-10-2026 – Memoria hidrologica de Wilma con los codigos de lamina nuevos (PLANOS_ANDFY_MUJERES.rar)
- El usuario renombro las laminas del CAR Mujeres (46 PDF; lista en insumos/wilma/LISTA_PLANOS_ANDFY_MUJERES.txt).
- En la memoria de Wilma (entregables_mujeres/MEMORIA_HIDROLOGICA_CAR_MUJERES_CON_COLECTOR.docx): DP-04 -> ST-CG-01 y ST-CG-02,
  DP-06A -> STP-CG, DP-07 -> ESDAE-01, DP-09 -> IC-01 (isometrico 4: estructura de salida).
- Tapa del registro segun el plano D-RL: tapa ciega 0.68 x 0.68 x 0.08 sin marco ni contramarco metalico, en rebaje 0.70 x 0.70 x 0.08,
  2 asas de fierro liso 1/2" en cajuelas, borde engrosado 0.15 x 0.10 (la memoria decia marco L 1 1/2" y contramarco L 2").
- Tabla 25 (secciones tipicas) y estructura de salida coinciden con STP-CG, ESDAE-01 e IC-01. Hecho en herramientas/revision_hidrologia.py.

## 20-10-2026 – Memoria descriptiva de drenaje pluvial del CAR Mujeres (Wilma, CUI 2717013)
- Generador: herramientas/mujeres/memoria_descriptiva_m.py (carátula, encabezado, logos y estilos de insumos/wilma/MEMORIA_IISS_CAR_MUJERES.docx).
  `python3 herramientas/mujeres/memoria_descriptiva_m.py figuras <carpeta PDF de PLANOS_ANDFY_MUJERES>` recorta 6 figuras sin rótulo
  (RGDPLV-01, PCPLV-01, STP-CG, D-RL, D-ECC, ESDAE-01) en entregables_mujeres/figuras_memoria_descriptiva/;
  `python3 herramientas/mujeres/memoria_descriptiva_m.py` arma el Word en dos pasadas (la segunda pone las páginas del índice).
- Salida: entregables_mujeres/MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL_CAR_MUJERES.docx (14 capítulos, 12 tablas, 6 figuras, 23 páginas).
- Datos: memoria hidrológica revisada, 46 planos, metrado vigente (RESUMEN y hojas por eje, solo lectura).
- Pendiente de decisión del usuario: la partida 1.4.4.6.5.1 del metrado dice "TAPA DE REGISTRO 0.68x0.68 C/MARCO Y CONTRAMARCO" y el
  isométrico 2 de IC-01 dibuja marco L 1 1/2" y contramarco L 2"; D-RL y la memoria indican tapa ciega en rebaje sin marco. No se tocó.

## 20-10-2026 – Revision de la memoria de calculo del colector del CAR Mujeres (PDF) y correcciones de coherencia
- Revisado a mano: intensidad 155.66, caudales (822.93 L/s), vertido sobre la cresta (H 0.245, NA 258.785), perfil (91 estaciones,
  llenado 0.815, BL 0.087) y los 11 elementos estructurales: todo cumple.
- Corregido en herramientas/mujeres/memoria_pdf_m.py (sobre copia temporal del libro; el insumo no se toca): area CAR Varones
  6752.03 (total 21764.00), sin nombres de personas, estacion del quiebre en 0+078.42 (era 78.47), fecha setiembre 2026.
- Memoria hidrologica de Wilma (revision_hidrologia.py, PERFIL_M) y memoria descriptiva: Froude 0.51-0.74 y V 1.02-1.43 m/s
  (perfil completo, no solo los ejes); borde libre minimo en el cruce de camiones 0.091 m (decia 0.10).
- Memoria descriptiva: el cruce de la Carretera Oasis (baden o alcantarilla) queda fuera del alcance; recomendacion de comunicarlo a
  la entidad de la via.
- Pendiente (usuario): la tapa del R-07 (0+060.15, rebaje 0+059.80 a 0+060.50) entra 0.20 m en el cruce de camiones (0+054 a 0+060)
  y solo esta verificada para rueda de auto (con HL-93: Mu 3.1 > phiMn 1.12). Confirmar por donde pasan los camiones.

## 20-10-2026 – Barranquita: niveles del interior del cerco (indicacion del usuario)
- Interior del cerco nivelado (sin hondonadas): pisos y pasadizos NPT +184.65; borde superior de las cunetas +184.60; areas verdes
  +184.55. Fuera del cerco, terreno natural.
- Patio de maniobra y estacionamiento (nor-este, 470 m2, NTN +184.50 del plano): se queda en su nivel; las cunetas que lo bordean
  (R-12, R-13, R-14, R-15 y R-16 en ese tramo) van AL RAS del patio (+184.50), con rejilla en los tramos abiertos (no 5 cm abajo:
  el usuario no quiere hueco). Poligono diseno_b.PATIO.
- D2 ya no es poza: pase en el cimiento como D1, D3 y D4 (POZA = set()).
- Resultado: 11 de 11 comprobaciones; profundidad maxima 0.92 m (R-07); C.F. de salida D1 183.660, D2 183.704, D3 183.576, D4 184.099.
- Recomendacion pendiente: rejilla de transito vehicular en las cunetas del patio de maniobra.

## 21-10-2026 – Barranquita: perfiles longitudinales por eje y secciones (estilo de las laminas del usuario)
- Los 19 ramales pasan a llamarse EJE-01 ... EJE-19 (misma geometria, mismos nudos: no se mueve ni se junta ninguna linea).
- herramientas/barranquita/perfiles_b.py: perfiles a 1/50 (H = V) con el estilo del usuario: NCT azul (abierto) / verde (tapado,
  cara superior e inferior de la losa), NCF magenta (cara superior e inferior de la losa de fondo), linea roja en cada seccion,
  referencias "Altura relativa al NPT" cada 0.15 m (0.00 = NPT +184.65), recuadro SECCION nn (NCT, NCF, H, EL, EM y conexion:
  "Llega EJE-xx", "Entrega a EJE-yy", "Descarga Dn") y guitarra Progresiva / Etiqueta / Longitud / Pendiente con progresivas cada 5 m.
- 96 secciones numeradas en orden (inicio y fin de eje, nudos, empalmes, inicio y fin de tapado, cambio de borde junto al patio);
  cada una con su corte a 1/20 (rejilla movil de platinas o losa tapa, marco 3/8"@0.25, longitudinales 3/8"@0.20 / @0.22, junta
  asfaltica 1" con el piso). Laminas: DC-03 a DC-11 perfiles, DC-12 a DC-15 secciones; isometricos y cortes pasan a DC-16 a DC-20.
- Excel: hoja SECCIONES (mismas 96 secciones) y nota de laminas leida de _calc/indice.json.

## 21-10-2026 – Barranquita: cunetas al ras del piso, pases sin bajar, tapados con altura libre y acero solo desde h = 0.40
- Niveles (usuario): NPT +184.65 = borde de cuneta +184.65 (junta asfaltica al mismo nivel del piso); area verde +184.60; patio de
  maniobra +184.50 con cuneta al ras.
- Pase por el cerco: la cuneta llega al cerco con su mismo borde (antes tomaba el terreno exterior y "se achicaba": seccion de 0.15 m).
- Tramos tapados: la profundidad minima suma la losa de 0.10 m (altura libre >= 0.25 m); capacidad con la altura libre bajo la losa.
- EJE-02 sigue hasta D1 por el pase y el EJE-01 le entrega con caida de 0.42 m (antes el EJE-01 bajaba 20 % en 2 m).
- Donde un empalme obliga a bajar, el fondo baja parejo desde el nudo anterior (sin escalon). Pendiente maxima 2.93 %, V max 1.84 m/s,
  sin gradas. 11 de 11 comprobaciones.
- Acero solo con h >= 0.40 m (rejilla - fondo) o en tramo tapado; menor: concreto simple (36 de 96 secciones).

## 21-10-2026 – Barranquita: quiebres a 45 grados en planta y detalle de cada descarga
- Usuario: "en la vista en planta si va a haber quiebres; donde hay de 90, quiebre de 45 (si no, resalto hidraulico); en el perfil
  longitudinal no se muestran". diseno_b.chaflanes(): en cada esquina con giro > 50 grados se corta un chaflan de 0.60 m por lado
  (maximo la mitad del tramo vecino); nudos X~a / X~b. Los ejes que llegan a una esquina entran en diagonal (union en Y).
  22 esquinas. En los perfiles y en la numeracion de secciones los nudos "~" no aparecen (69 secciones).
- Descargas (D1 a D4): las cuatro salen por gravedad por pase en el cimiento del cerco (ninguna poza).
  D1 C.F. 183.759, D2 183.758 (afuera el terreno baja ~3.2 m en talud: proteger la entrega contra erosion),
  D3 183.736, D4 184.145 (perfilar ~0.10 m en los primeros 0.5 m afuera).
- herramientas/barranquita/descargas_b.py: una lamina A1 por descarga (DC-18 a DC-21): planta 1/50 (ultimos 6 m, ejes que llegan,
  cerco, curvas exteriores, rotulos en columnas sin cruces), perfil longitudinal 1/25 por el eje que sale (muro del cerco cortado,
  cimiento, losa del pase, agua de diseno, terreno y perfilado, recuadros NCT/NCF/H y guitarra) e isometrico 1/50 con el terreno.
  Reemplazan a la lamina de cortes por las descargas y al detalle isometrico anterior. Capas DET-* e ISOD-*.
- Laminas: DC-03 a DC-11 perfiles, DC-12 a DC-14 secciones, DC-15/DC-16 isometricos de la red, DC-17 cortes generales,
  DC-18 a DC-21 detalle de descargas.

## 21-10-2026 – Barranquita: todo a escala real, planta con el estilo del usuario y tapas de inspeccion
- Usuario: "por que mide 0.30 si la cuneta es 0.60": la planta y el isometrico de las descargas se dibujaban a la mitad
  (1/50 dentro de una lamina 1/25). Ahora toda la lamina de cada descarga es 1/25 a escala real (1 unidad = 1 m); la planta
  muestra los ultimos 4.0 m (o menos si no entra) y el isometrico los ultimos 3.0 m con 1.75 m de terreno exterior.
- Revisadas las demas laminas: DC-01 1/250 en coordenadas reales, DC-02 1/5, perfiles 1/50 H = V, secciones 1/20, cortes
  generales 1/250 H = V: todas a escala real, sin exageracion vertical.
- Se quitan los isometricos de toda la red con el terreno (antes DC-15 y DC-16). Laminas: DC-03 a DC-11 perfiles, DC-12 a
  DC-14 secciones, DC-15 cortes generales, DC-16 a DC-19 detalle de las descargas D1 a D4.
- Planta (herramientas/barranquita/planta_cunetas_b.py, usado en DC-01 y en la planta de cada descarga), como las capturas del
  usuario: cuneta con rejilla = bordes exterior 0.60 e interior 0.40 en celeste y platinas cada 0.10 m; cuneta tapada = bordes en
  verde; flechas rojas de flujo (cada 5 m y en cada quiebre a 45 grados); contornos unidos por sistema (shapely) para empalmes limpios.
- Tapas de inspeccion 0.60 x 0.60 (concreto removible) en los tramos tapados: al inicio y al final, en cada empalme y a 10 m como
  maximo (criterio propuesto; el usuario no fijo distancia). Lista en _calc/tapas.json y hoja "TAPAS INSPECCION" del Excel.
- Perfiles: titulo = eje + nombre sin coordenadas (se quitaron "x=884.9", "y=815.97", etc. de las descripciones) + progresivas de la
  pieza. Fila Longitud / Pendiente: siempre la medida completa de seccion a seccion (antes, si el tramo se partia entre dos piezas,
  salia la parte, p. ej. 31.45 en vez de 35.59 de S-07 a S-08 del EJE-04).

## 21-10-2026 – Barranquita: expediente de drenaje pluvial (memorias, calculo, especificaciones y metrado)
- Insumo del usuario: memoria descriptiva de arquitectura (RAR con .doc de 38 MB, no versionado): CI 468901, GRSM / GTBM-T,
  Mz Z Lote 23 (partida 11128704), terreno 61,413 m2, clima Af, 1,800 - 2,400 mm/ano, techos a dos aguas 46 - 57 %.
- Lluvia: el usuario aprobo la opcion 2: serie Pmax24 de CO Tarapoto (la misma de Morales) transpuesta por la relacion de
  precipitacion anual Yurimaguas / Tarapoto = 2,039.6 / 1,073.1 = 1.90 (llanura Caynarachi - Huallaga, 184 m s. n. m.).
  Log-Normal (menor K-S) T = 25 anos: P24 = 231.49 mm; Dick y Peschke tc = 10 min: I = 400.96 mm/h; IDF K 1419.77, m 0.1315, n 0.750.
- C por superficie medido en la planta (techos 0.88, pavimentos 0.88, areas verdes 0.40): C ponderado 0.57; se quito el FS 1.15.
- Usuario: "manten la cuneta 0.40 interior 0.60 total": con la nueva lluvia cumplen los 91 tramos sin cambiar profundidades
  (Q max 227.3 l/s, borde libre min 0.119 m, V max 1.73 m/s); las cotas de fondo y descargas no cambian.
- Entregables nuevos en entregables_barranquita/: MEMORIA_HIDROLOGICA_..., MEMORIA_DESCRIPTIVA_..., ESPECIFICACIONES_TECNICAS_...
  (Word), MEMORIA_CALCULO_... (Excel con formulas: DATOS, SERIE, FRECUENCIAS, KS, IDF, SUPERFICIES, CAUDALES, DESCARGAS) y
  METRADO_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.xlsx (estructura Delphin del CAR Mujeres, 16 partidas con formulas; concreto
  f'c 175 150.74 m3, acero 6,545 kg, rejilla 924.82 m, 10 tapas, juntas 547.80 m y junta con el piso 748.76 m). Figuras en figuras_memoria/.
- Fuera del alcance (no metrado): canaletas y montantes de las coberturas (especialidad de techos) y la proteccion de la entrega D2
  fuera del cerco (recomendacion).

## 21-10-2026 – Barranquita: lluvia anual con las estaciones de la llanura (opcion A del usuario)
- Insumos del usuario: estudio hidrologico del expediente de agua potable y alcantarillado del distrito de Barranquita (Cuadro N° 05,
  SENAMHI 2013-2017: San Antonio 1,834.84; Pongo de Caynarachi 3,853.16; Navarro 2,349.79; Pelejo 2,332.92; Shanusi 2,444.00 mm/ano)
  y memoria descriptiva del drenaje de Santiago de Borja (estacion CO Juan Guerra, sin datos). Ninguno trae serie de Pmax 24 h.
- Opcion A aprobada: Pa Barranquita = promedio de Navarro, Pelejo y Shanusi (llanura, 100-160 m) = 2,375.57 mm; Pongo de Caynarachi
  (pie de cerros, lluvia orografica) y San Antonio no se usan. Factor 2.2137; P24 T25 = 269.62 mm; I (tc 10 min) = 467.00 mm/h.
- Cunetas 0.40 / 0.60 siguen cumpliendo en los 91 tramos (Q max 264.7 l/s, borde libre min 0.110 m, V max 1.82 m/s); diseno.json,
  planos, metrado y especificaciones sin cambios de cantidades. Actualizadas las memorias hidrologica, descriptiva y de calculo.

## 21-10-2026 – Barranquita: memoria hidrologica completa con la estructura de los CAR
- Usuario: "por que tan pocas paginas ... no tienes de los CAR el ejemplo?" -> hidrologica_doc_b.py con la estructura de los estudios
  hidrologicos de Morales (aspectos generales, estudio hidrologico, caudales, drenaje, conclusiones, recomendaciones, anexos): 29 paginas,
  clima de 5 estaciones (Cuadros 05 y 06 del estudio de Barranquita), las 4 distribuciones con sus formulas y tablas, K-S dato por dato,
  IDF, tiempo de concentracion (Kirpich, SCS y recorrido; todos < 10 min -> tc = 10 min por CE.040), riesgo de excedencia, coeficientes
  CE.040 Tabla 1.a, coberturas de techo, montantes por Wyly-Eaton (4" = 7.0 l/s), canaleta 0.25 x 0.20, verificacion de los 91 tramos.
- Se agrega el factor de seguridad 1.15 a los caudales (mismo criterio de los CAR): Q max 304.4 l/s, borde libre min 0.064 m (EJE-12
  llegando a D2): sigue cumpliendo sin cambiar la geometria. Normativa: CE.040 (R.M. 126-2021-VIVIENDA) en lugar de OS.060.
- Usuario pidio datos de 2024-2025: la serie Pmax24 de Tarapoto ya llega a 2024; los totales anuales de la llanura son 2013-2017. El
  internet del entorno sigue bloqueado para senamhi.gob.pe, power.larc.nasa.gov y data.chc.ucsb.edu (403): pendiente descargar series
  recientes de Navarro / Shanusi / Pelejo cuando el usuario habilite la red o envie los datos.

## 21-10-2026 – Barranquita: intento de actualizar la lluvia con datos SENAMHI 2024-2025
- Pedido del usuario: descargar datos diarios de Navarro (000386), Pelejo (153322), Shanusi (153315), Pongo de Caynarachi (003317)
  y Tarapoto; si no, NASA POWER o CHIRPS para Barranquita (-6.25, -76.03) y Tarapoto.
- Comprobacion de red: desde el entorno, senamhi.gob.pe, power.larc.nasa.gov, data.chc.ucsb.edu (y archive-api.open-meteo.com)
  siguen rechazados por el proxy (403); por la herramienta web, SENAMHI y NASA POWER no permiten lectura automatica. No se
  descargo ningun dato: hidrologia_b.py, diseno, planos, metrado, memorias y especificaciones quedan sin cambios (no se regenero).
- Nuevo herramientas/barranquita/lluvia_datos_b.py: lee los archivos diarios que entregue el usuario (formato SENAMHI con o sin
  encabezado, NASA POWER, CHIRPS), calcula totales anuales (meses con >= 25 dias), P anual de la llanura, serie de Pmax 24 h por
  estacion con el mismo analisis de hidrologia_b (4 distribuciones, K-S, T 25, Dick-Peschke tc 10 min) y la relacion anual
  Barranquita / Tarapoto; no modifica el diseno (salida en entregables_barranquita/_calc/lluvia_comparacion.json). Probado con
  archivos de ensayo en los cuatro formatos.
- Pendiente: datos reales (archivos del usuario o dominios habilitados en la configuracion de red).


## 21-10-2026 – Barranquita: datos diarios de Pongo de Caynarachi (003317) entregados por el usuario
- Insumo: insumos/barranquita/lluvia/qc00003317_pongo_de_caynarachi.txt (SENAMHI, datos historicos con control de calidad:
  anio mes dia pp tmax tmin, -99.9 sin dato), nov-1963 a abr-2014 (may-jun 2014 sin lluvia), 125 dias faltantes.
- lluvia_datos_b.py: Pmax 24 h anual 1964-2013 (50 anios): media 107.8 mm, desv. 35.0, max 226.3 (1968). K-S: Gumbel 0.104,
  Log-Normal 0.111, LP3 0.119, Normal 0.159 (critico 0.19). P24 T25 = 179.39 mm (Gumbel); I (tc 10 min) = 310.71 mm/h.
- Comparacion: Tarapoto transpuesta x 2.2137 (vigente) P24 T25 = 269.62 mm, I = 467.00 mm/h; Tarapoto sin transponer 121.8 mm.
  Caynarachi llueve 3.3 a 3.8 veces Tarapoto al anio pero su maxima T25 es solo 1.47 veces: la transposicion por lluvia anual
  sobreestima la maxima en 24 h.
- Totales anuales de Caynarachi 1981-1990 anomalos (5,255 a 7,060 mm; el resto 1,680 a 4,333): no afectan las maximas, pero no
  sirven para la lluvia media anual sin depurar.
- Pendiente decision del usuario: serie propia de Caynarachi o mantener Tarapoto transpuesta. hidrologia_b.py sin cambios.

## 21-10-2026 – Barranquita: lluvia de diseno con la serie medida de Pongo de Caynarachi (decision del usuario)
- Usuario: "si usa estos datos pero solo 25 anos desde el ano mas reciente hasta abajo". Serie Pmax 24 h de Pongo de Caynarachi
  (SENAMHI 003317) 1989-2013 (25 anios completos mas recientes; 2014 solo enero-abril). Faltan enero 2005 y julio 2008 (se
  conservan los maximos de los otros 11 meses). Sin transposicion (factor 1.0).
- K-S (critico 0.27): Gumbel 0.069 (adoptada), LP3 0.070, Log-Normal 0.095, Normal 0.130. T 25: P24 166.64 mm; tc 10 min
  P 48.11 mm, I = 288.63 mm/h; IDF K 1009.51, m 0.1372, n 0.75 (antes Tarapoto transpuesta: 269.62 mm, 467.00 mm/h).
- Cunetas 0.40 / 0.60: cumplen los 91 tramos (11 de 11 comprobaciones). Q max 188.1 l/s (EJE-12 a D2; antes 304.4), borde libre
  min 0.129 m (EJE-11 P-48 a P-33; antes 0.064), V max 1.62 m/s. hmin_req.json vacio: ninguna profundidad depende de la lluvia,
  cotas de fondo, descargas y metrado sin cambios (METRADO identico celda por celda; texto de especificaciones igual).
- base_sitio.pkl no esta en el repositorio (.gitignore *.pkl; se extrajo en una sesion anterior del DXF de 381 MB y no hay script):
  verifica_b.py --solo-lluvia rehace las comprobaciones 8 y 9 sobre la geometria vigente; caches _calc/coberturas.json (de la memoria
  hidrologica anterior) y _calc/junta_piso.json (del metrado vigente, 748.76 m); figuras de superficies y recortes se conservan.
- Regenerados: verificacion.json, CUADRO_TRAMOS, MEMORIA_CALCULO (Excel recalculado con LibreOffice: P24 166.64, I 288.63, Q max
  188.2, 0 tramos que no cumplen), MEMORIA_HIDROLOGICA (estacion, cobertura, serie, representatividad con contraste frente a
  Tarapoto, distribucion adoptada y conclusiones automaticas), MEMORIA_DESCRIPTIVA, METRADO y ESPECIFICACIONES (sin cambios).
- Pendiente: laminas DC-16 a DC-19 (texto "AGUA DE DISENO: Q = ... l/s, tirante" y nivel de agua en perfil e isometrico) y la figura
  fig_descarga_d1.png siguen con el caudal anterior hasta regenerar planos_b.py con base_sitio.pkl.

## 21-10-2026 – Barranquita: formatos de los CAR (calculo, metrado, analisis estadistico, especificaciones) y superficies
- Usuario: "procede ya con esto" (envio la memoria de calculo generada con la serie de Pongo de Caynarachi como su formato), metrado,
  analisis estadistico y especificaciones en los formatos que ya existen (CAR), mejorar areas verdes, techos, libres y estacionamiento,
  "ya no alteres planos, ya imprimi el ultimo". Se trajeron los commits de la otra sesion (Pongo de Caynarachi 1989-2013, Gumbel, I 288.63).
- Superficies: techos 5,477 m2 (proyeccion de coberturas por caras de lineas, incluye las aulas en diagonal, patio civico techado 518 m2 y
  losa multiusos techada 829 m2), areas libres de concreto 861 m2 (patios 01 a 04, veredas, atrio), patio de maniobra y estacionamiento
  647 m2, areas verdes 2,380 m2; contrastado con el cuadro de areas de la memoria de arquitectura (516 / 810 / 135 / 192 / 255 / 88 m2).
  C ponderado 0.761 (antes 0.570). Verificacion: 11 de 11 cumplen; Q max 225.7 l/s (EJE-02 a D1), borde libre min 0.129 m, V max 1.97 m/s.
- Memoria de calculo: mismo formato del usuario; DATOS con 4 coeficientes (FS pasa a B22) y SUPERFICIES con tabla de 4 tipos y detalle por zona.
- Metrado: formato del CAR Mujeres con hojas de detalle por eje; los 16 totales del RESUMEN identicos a la version anterior (LibreOffice).
- Memoria hidrologica: anexo N.° 01 con los cuadros del CAR (registro, B.1-B.4, K-S, C.4, cuadros N.° 04-06, intensidades, diseno).
- Especificaciones: motor espec.py + docx_espec.js (docx_espec.js acepta J.codigo para "C.I. N.°"); 20 paginas.
- Planos (DXF y PNG) sin cambios. Pendiente de decision del usuario: DC-16 a DC-19 rotulan "AGUA DE DISENO" con los caudales anteriores
  (207.7 / 264.7 / 174.2 / 48.4 l/s); con la lluvia y superficies vigentes son 225.7 / 225.3 / 163.6 / 44.8 l/s.

## 21-10-2026 – Barranquita: analisis estadistico en el formato del usuario (Excel del CAR Varones)
- Usuario envio ANALISIS_ESTADISTICO - CAR VARONES.xlsx: "asi quiero el analisis estadistico". Copia en insumos/barranquita/plantillas/.
- analisis_estadistico_b.py: abre la plantilla con LibreOffice (UNO), pone proyecto, estacion Pongo de Caynarachi (003317) y la serie
  1989-2013 (25 anios, S/D resaltados), borra las filas sobrantes del registro de 26 anios (LibreOffice ajusta formulas y graficos), quita
  las hojas auxiliares Hoja1 y 210, cambia los titulos de graficos (CO TARAPOTO -> PONGO DE CAYNARACHI), corrige MAX(Z22:Z45) a todo el
  rango y hace que la columna "Diseno" del resumen tome la distribucion que selecciona la prueba K-S. Salida
  entregables_barranquita/ANALISIS_ESTADISTICO_IE0590_BARRANQUITA.xlsx; se compara con hidrologia_b (iguales).
- hidrologia_b.analisis/resultados con los metodos de la hoja: z de Abramowitz-Stegun, KT de LP3 de Kite, K-S con P de excedencia
  m/(n+1) y serie de mayor a menor, LP3 por gamma de ln P (CHIDIST con gl entero), Gumbel con yn/sn (Aparicio), D critico por formula;
  IDF por el modelo de Bell (P60(10) = 0.4602 P24(10)^0.876, intensidades redondeadas a 0.1). Con los datos del CAR Varones reproduce la
  hoja del usuario (D 0.0920 / 0.0894 / 0.0964 / 0.1270; K 161.94, m 0.1786, n 0.5271).
- Barranquita: la prueba K-S del formato del usuario elige Log Pearson III (D 0.0683; Gumbel 0.0775; critico 0.2650): P24 T25 169.27 mm,
  I = 293.18 mm/h (antes Gumbel 166.64 / 288.63); IDF K 211.66, m 0.1786, n 0.5269. Verificacion 11 de 11; Q max 229.2 l/s (EJE-02 a D1),
  borde libre min 0.128 m, V max 1.98 m/s. Metrado identico. Memoria de calculo (FRECUENCIAS, KS, IDF), memoria hidrologica y anexo,
  descriptiva y cuadro de tramos regenerados. Planos sin cambios; DC-16 a DC-19 siguen rotulando 207.7 / 264.7 / 174.2 / 48.4 l/s
  (ahora 229.2 / 228.9 / 166.2 / 45.5 l/s).
- Usuario pregunto si la memoria hidrologica coincide con el nuevo analisis estadistico. coteja_analisis_b.py: 1696 valores de la
  memoria (1002 del cuerpo y 694 del anexo N.° 01) comparados con ANALISIS_ESTADISTICO_IE0590_BARRANQUITA.xlsx a la precision impresa:
  0 diferencias. La memoria de calculo (FRECUENCIAS, KS, IDF) tambien coincide (P24 169.27, D K-S, K 211.66, I 293.18).

## 21-10-2026 – Barranquita: caratula con la foto aerea en todos los documentos
- Usuario envio la foto aerea del local (dron) y pidio la caratula para los 6 documentos (metrado, memoria hidrologica, memoria
  descriptiva, memoria de calculo, especificaciones tecnicas, analisis estadistico).
- caratula_b.py: mismo contenido en todos (Gobierno Regional San Martin / Gerencia Territorial Bajo Mayo - Tarapoto, expediente tecnico,
  proyecto, C.I. N° 468901, foto recortada sin las esquinas oscuras del lente, franja azul con el titulo del documento, especialidad,
  ubicacion y fecha); sin nombre ni CIP del proyectista. Word: primera pagina sin encabezado; Excel: hoja CARÁTULA al inicio, A4 vertical.
- docx_espec.js: portada con foto solo si el JSON trae "caratula" (las especificaciones de los CAR siguen igual).
- coteja_analisis_b.py ignora la franja de la caratula (1696 valores, 0 diferencias). Metrado identico; planos sin cambios.
- Pedido "solo necesito el archivo en un solo Word, solo las caratulas": caratula_b.solo_caratulas() (python3 herramientas/barranquita/caratula_b.py)
  genera entregables_barranquita/CARATULAS_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx con las 6 caratulas, una por pagina (A4, 6 paginas).
- Correccion del usuario: la caratula no debe decir "EXPEDIENTE TÉCNICO" sino "SERVICIO DE DISEÑO - DRENAJE PLUVIAL" (caratula_b.EXPEDIENTE).
  Regenerados el Word de caratulas y los 6 documentos; comparados con la version anterior: solo cambia esa linea (coteja 1696 / 0; planos sin cambios).
- Pedido "pasame un indice de planos y caratula de planos en un solo Word": indice_planos_b.py -> CARATULA_E_INDICE_DE_PLANOS_IE0590_BARRANQUITA.docx
  (pag. 1 caratula comun con titulo PLANOS; pag. 2 indice de las 19 laminas DC-01 a DC-19 por grupos, con formato A1 y escala de _calc/indice.json
  y el contenido leido del DXF impreso: ejes y progresivas de cada perfil, secciones por lamina, eje de salida de cada descarga). Planos sin cambios.

## 21-10-2026 – Indice de planos del CAR Mujeres (Wilma, CUI 2717013) en Word
- Pedido: "armame un indice de planos en Word del CAR Mujeres segun el PDF de planos ultimo" (PLANOS_ANDFY_MUJERES, 46 laminas, set. 2026).
- herramientas/mujeres/indice_planos_m.py <carpeta PDF>: lee cada PDF sin modificarlo (formato del papel, titulo y escala del rotulo,
  escalas de los dibujos, secciones / tramos / progresivas / BC / cortes que distinguen laminas de igual titulo), comprueba cada titulo
  contra el rotulo y guarda entregables_mujeres/_calc/indice_planos.json; sin argumento arma el Word desde el JSON.
- Salida: entregables_mujeres/INDICE_DE_PLANOS_DRENAJE_PLUVIAL_CAR_MUJERES.docx (encabezado con logo y proyecto de la plantilla IISS de
  Wilma, especialidad DRENAJE PLUVIAL; 46 laminas en el orden del juego: 3 A0, 15 A1, 21 A2, 7 A3; 2 paginas).
- Observacion para el usuario: las laminas 45 y 46 tienen el mismo codigo DI-CBCB en el rotulo.

## 21-10-2026 – Caratulas de los documentos del CAR Mujeres (Wilma, CUI 2717013) en un solo Word
- Pedido: caratulas de los 6 documentos de la carpeta de entrega (metrados, memoria hidrologica, memoria descriptiva, memoria de calculo del
  colector, memoria de calculo del drenaje interno, especificaciones tecnicas), con "servicio para elaboracion de expediente tecnico".
- herramientas/mujeres/caratulas_m.py: copia 6 veces la caratula de la plantilla de Wilma (insumos/wilma/MEMORIA_IISS_CAR_MUJERES.docx, solo
  lectura; la misma de la memoria descriptiva): recuadro con el titulo de cada documento, "SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA
  ELABORACIÓN DEL EXPEDIENTE TÉCNICO DE PI:", nombre del proyecto con CUI 2717013 y fecha SEPTIEMBRE- 2026; encabezado DRENAJE PLUVIAL.
- Salida: entregables_mujeres/CARATULAS_DRENAJE_PLUVIAL_CAR_MUJERES.docx (6 paginas).
- Pedido siguiente: caratulas "mas elegantes, con foto del CAR". caratulas_m.py ya arma el diseno grafico (escudo del GORE San Martin,
  servicio y proyecto, imagen principal, franja granate con el titulo, vista aerea del terreno con la ubicacion y la fecha); imagenes del
  proyecto en entregables_mujeres/figuras_caratula/ (vista 3D del resumen ejecutivo, vista aerea de la caratula de la memoria hidrologica,
  escudo de la plantilla IISS). El usuario va a enviar la foto que quiere como imagen principal: el Word entregado queda como estaba hasta
  regenerarlo con esa foto.

## 22-10-2026 – Detalle de lloraderos del Hogar de Refugio (CUI 2675514) legible en AutoCAD
- El usuario mostro una captura de AutoCAD: los patrones EARTH, AR-CONC, AR-SAND y GRAVEL salian sin la escala del bloque (rayas
  gigantes, concreto y grava casi vacios) y "m³" salia "m?".
- espec_lloraderos.py: para "refugio" el detalle (detalle_cad) y la leyenda se dibujan sin patrones: rellenos solidos con color verdadero,
  piedras de grava una por una (20 a 40 mm, escala real), punteado de concreto y solado, trazos de tierra; cotas y puntos en gris oscuro fijo
  (se leen con fondo negro y blanco); "m3". Dos presentaciones A3 a escala 1:10 (ESPECIFICACIONES y DETALLE LLORADERO).
  CAR Varones sin cambios (no se regenero).

## 22-10-2026 – Hogar de Refugio (CUI 2675514): drenaje pluvial de la OC-01 (jardinera + banca + pergola)
- Insumo: `insumos/solange/oc01/OC-01_BANCA_CON_PERGOLA.dxf` (planta de techos, corte A-A, elevacion E1; proyecto confirmado por el usuario).
- Tres techos a una agua de 2.40 de fondo: T-1 3.79 (canaleta al norte, salida en el extremo izquierdo), T-2 4.21 (central, canaleta
  al sur, salida a la izquierda), T-3 3.79 (canaleta al norte, salida a la derecha). El "sumidero 4" tipo cupula" se reemplaza por
  boquilla de plancha (pedido del usuario). Canaleta de plancha galvanizada e = 0.50 mm, 0.18 x 0.21 (indicacion del usuario), S = 0.5 %,
  2 sujetadores por canaleta (0.80 / 0.85 m de cada extremo), tapas en los dos extremos.
- `herramientas/techo/planos_oc01_refugio.py` -> `entregables/PLANOS_DRENAJE_OC-01_BANCA_PERGOLA_HOGAR_REFUGIO.dxf`: DO-01 isometrico
  general 1/30 + planta de techos 1/50; DO-02 isometrico de la salida (boquilla, niple, codos, colgador, abrazadera, bajada) y corte de
  la canaleta 1/5. PNG en `entregables/vistas_previas_oc01/`.
- `herramientas/techo/metrado_oc01_refugio.py` -> `entregables/METRADO_CANALETA_OC-01_BANCA_PERGOLA_HOGAR_REFUGIO.xlsx`: solo canaleta
  11.79 m, 6 tapas, 6 sujetadores, 3 boquillas (N.° de OC-01 = 1, dato editable).
- Bancas OC-01 en la planilla del Hogar de Refugio: son 9 bancas = 3 juegos OC-01 (cada juego: techos de 3.79, 4.21 y 3.79 m).
  El usuario envio su metrado actualizado (copiado a `insumos/metrados_vigentes/METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx`).
  `herramientas/bancas_oc01_en_planilla_refugio.py` -> `entregables/METRADO_DRENAJE_MUJERES_VIOLENTADAS_CON_BANCAS_OC-01.xlsx`:
  hoja nueva METRADO CANALETA BANCAS (estilos de METRADO CANALETAS; N.° de juegos en F22 editable), subtitulo
  01.04.03.05.04 RED DE RECOLECCION TECHO DE BANCAS CON PERGOLA (OC-01) en PLANILLA (filas 165-169) y RESUMEN (filas 53-57):
  canaleta 35.37 m, soportes 18, tapas 18, boquillas 9. Los 760 valores anteriores quedan iguales (comprobado).
  El metrado suelto de la OC-01 y la nota 5 de DO-01 pasan a 3 juegos.


## 22/10/2026 - Hogar de Refugio: índice de planos, memorias y especificaciones con el juego DPL
- El usuario entregó el PDF de 40 láminas DPL (ordenado por tamaño) y su metrado con bancas editado (hoja METRADO CANALETA BANCAS
  sin la fila 8). Ese metrado pasa a vigente (`insumos/metrados_vigentes/..._CON_BANCAS_OC-01.xlsx`) sin cambios.
- `indice_planos_refugio.py`: índice en Word (42 láminas en 8 grupos) y PDF reordenado DPL-01 a DPL-40 con marcadores.
  El isométrico de lloraderos tenía en el rótulo DPL-36 (repetido con la caja sumidero): en el índice es DPL-40 (corregir rótulo en CAD).
  Las láminas OC-01 (DO-01/DO-02) pasan a DPL-41/DPL-42 en el DXF; la nota de parámetros del metrado del usuario aún dice "plano DO-02".
- Memoria hidrológica: figuras = láminas del PDF del usuario, referencias DPL, metrado del colector desde el RESUMEN vigente y
  capítulo 9 nuevo (canaletas de bancas OC-01: Q < 0.6 L/s por techo, y 0.012 m, D req. 1.59" -> 4"; lloraderos 157 und).
- Especificaciones: lee el metrado vigente con bancas (4 partidas 01.04.03.05.04 con texto propio) y láminas DPL.
- Memoria descriptiva nueva (`memoria_descriptiva_refugio.py`), estructura del CAR Mujeres, 19 páginas.
- Corrección pedida por el usuario: el PDF de láminas está organizado por formato de hoja (A0, A1, A2, A3), no por número.
  El índice sigue ahora ese orden, con los códigos tal como están en cada rótulo, sin renumerar ni observaciones y solo con las
  40 láminas del PDF. Se retiró el PDF reordenado. El isométrico de lloraderos se cita como DPL-36 (su rótulo) en las memorias;
  la OC-01 queda como DPL-41/42 en DXF aparte.

## 23/10/2026 - CAR Varones (CUI 2705619): plano DL-00 de ubicación de lloraderos en DXF
- `planos_ubicacion_lloraderos.py` ahora sirve a los dos proyectos (`refugio` por defecto, `varones`). Varones: planta general de
  Katiuska en gris, cunetas (capa CUNETAS y bloques de drenaje) en azul, áreas verdes (HIERVA, Area Verde, Hatch Jardin) en verde
  sólido, 34 tramos de la hoja METRADO LLORADEROS con sus 226 lloraderos @1.50 m, cuadro de tramos, leyenda, notas y detalle típico
  sin patrones de achurado (se ve igual en AutoCAD). Lado del muro por el rumbo de la hoja (ESTE/OESTE/NORTE/SUR).
- Salida: `entregables_varones/PLANO_DL-00_UBICACION_LLORADEROS_CAR_VARONES.dxf` + vista previa PNG. Metrado sin cambios.

## 23/10/2026 - CAR Varones (CUI 2705619): índice, memorias y especificaciones con el juego final DPLV
- La usuaria entregó el PDF final de 44 láminas DPLV (orden por formato A0-A3) y el metrado del 23-10-2026 (igual al vigente salvo
  la celda de fecha C5 de las hojas ACU/DESAGREGADO); pasa a vigente.
- Índice de planos en Word en el orden del PDF, códigos tal cual el rótulo (DPVL-09, DPVL-10 y DVPL-11 están así en los rótulos).
- Memoria hidrológica: figuras y referencias DPLV (DPLV-17, 18, 21, 23, 25-30), metrado del RESUMEN vigente y capítulo nuevo de
  lloraderos (34 tramos, 226 und) con el cuadro de materiales de la hoja DESAGREGADO LLORADEROS.
- Especificaciones: láminas DPLV; la partida de lloraderos lleva el cuadro de materiales del desagregado (tubo PVC 3" 67.80 m,
  1808 perforaciones, grava 6.71 m3, geotextil 134.24 m2, mortero 0.11 m3) y las láminas DPLV-43/35/34 (Refugio: DPL-39/37/36).
- Memoria descriptiva nueva de Varones (17 páginas), con la misma estructura que la del Refugio.
- Pregunta de la usuaria: el desagregado de materiales del lloradero sí existe, en la hoja DESAGREGADO LLORADEROS (no en METRADO
  LLORADEROS, que solo cuenta las unidades por tramo) y valorizado en ACU LLORADEROS (S/ 20.56 por und).

## 23/10/2026 - CAR Varones: códigos de lámina del metrado = juego final DPLV
- Pedido de la usuaria: en el metrado, solo donde va código de lámina, poner los códigos nuevos de sus planos.
- `herramientas/varones/codigos_laminas_metrado_v.py` edita el XML del libro (sharedStrings y texto en caché de fórmulas):
  140 celdas de sustento/criterio/notas. DP-01->DPLV-17, DP-02->DPLV-18, DP-04->DPLV-21 y DPLV-22, DP-06B (rev. 02)->DPLV-23,
  DP-06C->DPLV-24, DP-07->DPLV-25, DD-01..04->DPLV-27..30, DJ-01->DPLV-31, DL-01->DPLV-34, DL-02->DPLV-35. DP-08 (cuadro de
  doblado) y DA-01..03 (cuadros de metrado) no existen en el juego final: se citan las secciones del colector DPLV-21 y DPLV-22.
- Control: ningún valor numérico cambia (comparado tras recalcular con LibreOffice). Salida
  `entregables_varones/METRADO_DRENAJE_PLUVIAL_CAR_VARONES_23-10-2026.xlsx`, copiada como vigente.
- Corrección de la usuaria: DP-08 y DA-01 a DA-03 los excluyó a propósito del juego final; en el metrado se BORRAN esas referencias
  (no se reemplazan por DPLV-21/22). Ej.: "Criterio (lamina DA-02): ..." -> "Criterio: ...", "Lamina DA-01: zanja ..." -> "Zanja ...",
  celdas cuyo único texto era la referencia (E18, E24 de COLECTOR PARAMETROS) quedan vacías. El generador parte ahora del original
  de la usuaria (`insumos/katiuska/METRADO_DRENAJE_PLUVIAL_CAR_VARONES_23-10-2026_ORIGINAL.xlsx`). Valores sin cambio (recalculado).
- Índice de planos de Varones: a pedido de la usuaria, ordenado por número de lámina (DPLV-01 a DPLV-44, sin grupos por formato;
  `I.ORDEN = 'numero'` en varones/indice_planos_v.py). El del Refugio sigue en el orden de su PDF. La relación de planos de la
  memoria descriptiva de Varones sigue el mismo orden.

## 23/10/2026 - CAR Varones: memoria de cálculo del colector en PDF
- Pedido de la usuaria: el Excel de cálculo del colector de Varones en PDF con el mismo estilo de la memoria de cálculo
  HIDRO-CE040 de Varones (título serif, recuadro de fórmulas, tablas con encabezado celeste, bloques finales).
- `herramientas/varones/memoria_pdf_v.py` (mismo motor que `memoria_pdf_refugio.py` / `mujeres/memoria_pdf_m.py`): lee
  `entregables_varones/MEMORIA_CALCULO_COLECTOR_CAR_VARONES.xlsx` recalculado con LibreOffice en copia temporal (sin las
  correcciones propias del CAR Mujeres) y copia sus valores sin cambiarlos -> `MEMORIA_CALCULO_COLECTOR_CAR_VARONES.pdf` (17 pág.):
  datos y metodología, 1 datos, 2 caudales por cuneta, 3 cunetas (acortamiento y caída libre), 4 empalme con la CL, 5 perfil de
  flujo (gráfico, 110 estaciones, velocidades y autolimpieza), 6 estructural, 7 cumplimiento y diseño adoptado; firma en blanco.
- `varones/memoria_v.py`: referencias de lámina del Excel pasadas al juego final (DPLV-17, DPLV-24, DPLV-25, DPLV-30; láminas
  DPLV-17 a DPLV-30). Solo 3 celdas de texto cambian; valores iguales.
- El Excel que envió la usuaria era una versión anterior (mismos números, 5 textos distintos); se usó el vigente del repositorio.
- `memoria_pdf_refugio.perfil_svg`: marcas del eje de progresivas según el rango de datos (Refugio sin cambio). El PDF del Refugio
  se regeneró: solo cambia el área de Varones 6752.03 m² (la de su memoria hidrológica, ya en el Excel vigente).

## 23/10/2026 - CAR Varones: carátulas de cada documento (Word por separado)
- Pedido de la usuaria: una carátula por documento de su carpeta de entrega (luego pidió todas en un solo Word, una por página), con la foto del proyecto
  que envió (guardada en `insumos/katiuska/FOTO_PROYECTO_CAR_VARONES.jpg`), y además la carátula de planos.
- `herramientas/varones/caratulas_v.py` (mismo diseño que las carátulas del CAR Mujeres, `mujeres/caratulas_m.py`): Gobierno Regional
  San Martín - Gerencia Territorial Bajo Mayo, servicio, proyecto con CUI 2705619, foto, franja granate con el título, ubicación y
  fecha OCTUBRE - 2026; sin proyectista. 7 carátulas en `entregables_varones/CARATULAS_DRENAJE_PLUVIAL_CAR_VARONES.docx`: especificaciones técnicas, memoria de cálculo
  (canaletas, montantes y cunetas), memoria de cálculo (colector pluvial frontal), memoria descriptiva, memoria hidrológica,
  metrados y planos (láminas DPLV-01 a DPLV-44). Cada una cabe en una sola página A4 (verificado).
- Logo: la usuaria entregó el logo oficial del Gobierno Regional San Martín (`insumos/katiuska/LOGO_GOBIERNO_REGIONAL_SAN_MARTIN.png`);
  el escudo anterior (recorte de un Word del CAR Mujeres) salía cortado. `caratulas_v.escudo()` toma el escudo completo del logo
  (sin el texto, que ya va al lado) y lo coloca a 2.8 cm de alto en las 7 carátulas.
- Revisión del RAR "PLANTA GENERAL- CAR VARONES PRUENA_LAMINAS": es el mismo PDF de 44 láminas DPLV ya usado (idéntico byte a byte).
  Observaciones de texto (tildes, DPVL-09/10, DVPL-11, CONTRUCTIVO, ALAMACEN): la usuaria las deja como están.
- Fecha: la usuaria confirma SETIEMBRE 2026 (la de los rótulos). Carátulas, memoria descriptiva y memoria de cálculo del colector
  (PDF) de Varones pasan de octubre a setiembre 2026 (`memoria_descriptiva_refugio.FECHA`, por defecto OCTUBRE 2026 para el Refugio,
  sin cambio en su Word).

## 23/10/2026 - Hogar de Refugio: carátulas de los documentos en un solo Word
- Pedido de la usuaria: carátulas de los documentos de su carpeta de entrega del Hogar de Refugio Temporal (CUI 2675514), sin el
  índice de planos, más una de planos; todo en un Word. Foto entregada: `insumos/solange/FOTO_PROYECTO_HOGAR_REFUGIO.jpg` (es la
  misma imagen que la del CAR Varones).
- `herramientas/caratulas_refugio.py` reutiliza `varones/caratulas_v.py` (parametrizado con LEYENDA y TITULO; Varones sin cambio):
  nombre del proyecto tal como el rótulo de las láminas DPL, fecha SETIEMBRE - 2026 (rótulos), 7 carátulas: especificaciones,
  memoria de cálculo (canaletas, montantes y cunetas), memoria de cálculo (colector), memoria descriptiva, memoria hidrológica,
  metrados y planos (láminas DPL-01 a DPL-40) -> `entregables/CARATULAS_DRENAJE_PLUVIAL_HOGAR_REFUGIO.docx` (7 páginas, verificado).
- Color: a pedido de la usuaria, las carátulas del Hogar de Refugio van en verde (1E5E3B; subtítulo D6EEDD) para distinguirlas del
  granate del CAR Varones (`caratulas_v.COLOR`/`COLOR_SUB`; Varones sin cambio, XML idéntico).

## 23/10/2026 - Hogar de Refugio: especificaciones técnicas vigentes
- La usuaria pregunta por las últimas especificaciones del Hogar de Refugio (CUI 2675514): son las del 23/10 (metrado vigente con
  bancas OC-01, láminas DPL, 50 páginas). Se quitaron dos citas a láminas que no existen en el juego DPL de la usuaria (DJ-01/DJ-02
  en la junta de cunetas y DJ-03 en la rejilla; son láminas del CAR Varones), con el mapeo `laminas` de `espec.py` (refugio).
  Solo cambian esos 2 párrafos; el resto del Word es idéntico.

## 23/10/2026 - Hogar de Refugio: índice con las láminas que imprime la usuaria (42 láminas)
- La usuaria envió su índice en PDF (versión del 22/10) para comprobarlo y luego el PDF de las láminas que imprime
  (PLANTA_GENERAL_-_MUJERES_VIOLENTADAS_LAMINAS.pdf, 42 láminas), que reemplaza al juego de 40 en
  `insumos/solange/PLANOS_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS_LAMINAS.pdf`. Numeración nueva sin duplicados: DPL-37 isométrico de
  instalación de lloraderos (A1), DPL-38 detalle de lloradero (A2), DPL-39 falsa columna (A3), DPL-40 planta de ubicación de lloraderos
  (A0), DPL-41 y DPL-42 bancas OC-01 (A2). DPL-01 a DPL-36 sin cambio.
- Índice: de la DPL-01 a la DPL-42 con los grupos temáticos (como el índice que tenía la usuaria); el de Varones sigue sin grupos.
- Coherencia: memoria hidrológica (lloraderos DPL-40/38/37), memoria descriptiva (falsa columna DPL-39, lloraderos DPL-40/38/37, relación
  de planos de 42 láminas, figuras de la OC-01 tomadas del PDF), especificaciones (planos DPL-01 a DPL-42, lloraderos DPL-40/38/37) y
  carátulas (LÁMINAS DPL-01 A DPL-42). Solo cambian esas citas (comparado el texto antes y después).

## 24/10/2026 - Criterios del planteamiento de cunetas sobre terreno guardados como skill
- Pregunta del usuario: si los criterios (cargar terreno, leer cotas y curvas, no salir del límite del terreno, cuneta a cada lado
  en techos a dos aguas, etc.) quedaron guardados. Se reunieron en `.claude/skills/planteamiento-cunetas-terreno/SKILL.md`
  (antes estaban repartidos en la bitácora, el código de herramientas/barranquita y CLAUDE.md) y se citan en CLAUDE.md.

## 24/10/2026 - Base de conocimiento completa (memoria permanente) y manual técnico
- Pedido del usuario: que todo lo aprendido desde el inicio (colector, cunetas, hidrología, planos ordenados, secciones, perfiles,
  metrado, documentos) quede guardado al mínimo detalle, para recordarlo siempre e implementarlo en su programa (DRENIE).
- `conocimiento/`: 8 capítulos (01 reglas y forma de trabajo, 02 hidrología e hidráulica, 03 colector frontal, 04 cunetas sobre
  terreno, 05 planos DXF, 06 metrado/ACU/especificaciones, 07 componentes complementarios, 08 documentos del expediente; ~7 460
  líneas), redactados a partir de los 328 mensajes del usuario (`_fuentes/mensajes_usuario.txt`), esta bitácora, los skills y el
  código. Cada uno termina con "Para implementarlo en un programa".
- Skill índice `.claude/skills/conocimiento-drenaje-pluvial/` y aviso al inicio de CLAUDE.md. Manual Word:
  `herramientas/conocimiento_docx.py` -> `conocimiento/MANUAL_TECNICO_DRENAJE_PLUVIAL.docx` (≈159 páginas, índice automático).
- Chat nuevo "PROGRAMA DRENIE" (rama `claude/programa-drenie`, parte de esta rama) para cargar el código del programa del usuario
  e integrar la base de conocimiento.

## 26/10/2026 - Hogar de Refugio: índice de planos de ARQUITECTURA en Word
- El usuario envió el índice de láminas de arquitectura en Excel (copia en `insumos/solange/INDICE_DE_LAMINAS_ARQUITECTURA_HOGAR_REFUGIO.xlsx`)
  y pidió el Word con el estilo de los índices de drenaje. `herramientas/indice_arquitectura_refugio.py` (piezas de `indice_planos_refugio.py`)
  -> `entregables/INDICE_DE_PLANOS_ARQUITECTURA_HOGAR_REFUGIO.docx`: 107 láminas en 6 grupos (I arquitectura 7, II desarrollo de módulos 34,
  III obras complementarias 15, IV obras exteriores 12, V detalles de arquitectura 37, VI evacuación y señalización 2), 3 páginas.
- Arreglos de forma: grupos I a VI en orden (el Excel tenía I, II, IV, IV, IV, III), numeración correlativa (el Excel salta el 51:
  terminaba en 108), códigos sin espacios, tildes (EDIFICACIÓN, CIELORRASO, ...), y 6 códigos repetidos por copia tomados de su
  descripción (A-06/03-04, A-06/04-04, A-08/02-04, A-08/03-04, A-08/04-04, OC-03/03-03). 44 láminas sin formato en el Excel: "—".

## 26/10/2026 - Hogar de Refugio: ACU aparte de las partidas resaltadas en amarillo
- El usuario envió su metrado (copia en `insumos/metrados_vigentes/METRADO_DRENAJE_MUJERES_VIOLENTADAS_26-10-2026.xlsx`; respecto
  del vigente con bancas cambian falsas columnas y boquillas 52 -> 63 y los dados) y pidió las ACU de las partidas con el NOMBRE
  resaltado en amarillo en su RESUMEN (capturas): lloradero, tapa lateral 0.25x0.20, canaleta y tapa lateral de bancas OC-01
  0.18x0.21, tapa de registro ciega, junta de dilatación del colector y junta con el cerco (no las que solo tienen la cantidad en amarillo).
- `herramientas/acu_partidas_amarillas_refugio.py <metrado>` -> `entregables/ACU_PARTIDAS_RESALTADAS_HOGAR_REFUGIO.xlsx`: hoja
  RESUMEN ACU (ítem, nombre, und, metrado del usuario, C.U. vinculado, parcial; total S/ 8,587.70 de costo directo), las ACU de la
  planilla copiadas con su formato y fórmulas (referencias a otras hojas pasan a valor), COSTO HORA HOMBRE 2026, y ACU nuevas de
  las bancas OC-01 (plancha de 0.50 mm, una pieza por techo; precio referencial por peso a partir de la plancha de 0.9 mm, por cotizar).

## 27/10/2026 - CAR Varones: evacuación y señalización (memoria descriptiva, metrado y especificaciones)
- El usuario envió el plano final de la arquitecta (EVACUACION Y SEGURIDAD OK, láminas SE-S-01 y SE-E-01; copia comprimida en
  `insumos/katiuska/senalizacion/`, con el documento de correcciones pendientes) y pidió la memoria descriptiva, el metrado final y
  las especificaciones "todo corregido". Módulo nuevo `herramientas/varones/senalizacion/`:
  `lee_plano_se.py` (DXF -> `entregables_varones/_calc/senalizacion_plano.json`: leyenda fila por fila, cada símbolo por la posición
  del centro de su contorno y su edificación E-01..E-10/EXT, rutas, zonas seguras S1-S13, aforos, rótulos), `datos_se.py` (catálogo
  de partidas, población, rutas, aforos: fuente única), `metrado_se.py` (Excel con fórmulas: RESUMEN, METRADO por edificación con
  cotejo contra la leyenda, ZONAS DE REUNIÓN, RUTAS Y AFOROS, SEÑALES), `memoria_se.py` (Word, carátula granate del CAR Varones),
  `espec_se.py` (motor `docx_espec.js`, ahora con `cabecera`, `titulo_doc` y anchos de tabla propios opcionales) y `vistas_se.py`
  (PNG de las plantas con dibujo propio: el render de ezdxf supera 10 GB con este plano).
- Revisión del plano final: las 16 señales con bloque coinciden planta = leyenda (salida 80, zona segura 62, ...); avisador sonoro,
  riesgo eléctrico, riesgo de descarga y prohibido el ingreso son imágenes OLE sin posición en el DXF (vale la leyenda). Corregido
  por la arquitecta: P-01..P-04, P-07 (radio 1.50 m), P-11 (rótulos). Quedan en el plano: "INCEDIOS" en la leyenda, señal de extintor
  a 1.20 m (los documentos usan 1.80 m sobre el equipo), SS.HH. PHD con otro bloque en la planta, zona de reunión 11 en la leyenda
  frente a 13 zonas S1-S13 dibujadas (el metrado usa 13), rótulo "RUTA 03 - 15.51ml" que es la ruta 02 (servicios generales),
  extintores CO2 en la cocina y E-09/E-10 sin extintor (P-09). Memoria con M-01..M-06: personal 22, 62 permanentes + 4 temporales = 66.
- 27/10/2026 (2): el usuario dijo que la memoria era "muy pobre" y envió de ejemplo la memoria de evacuación y señalización del
  Hogar de Refugio (copia en `insumos/katiuska/senalizacion/EJEMPLO_...docx`; mapas de ubicación en `.../mapas/`). `memoria_se.py`
  rehecha con la estructura del ejemplo y ampliada (34 páginas): ubicación (UTM referencial E 345 749, N 9 282 885), accesos,
  objetivos, normas, zonificación y ambientes de cada edificación leídos del plano (`lee_plano_se.ambientes`), peligros por
  edificación, población y aforo con índices, ancho de puertas y pasajes (A.130, 0.005 m/persona), rutas y tiempos, zonas de
  reunión con su capacidad, comité, director, mantenimiento, brigadas, personal, protocolos (sismo, incendio, lluvias, gas, corte
  de energía), procedimiento de evacuación con directorio, extintores por edificación, clasificación NTP 399.010-1, tabla de
  simbología con la imagen de cada señal y una ficha por señal, programa de mantenimiento y conclusiones. `senales_img.py` dibuja
  cada señal a escala con su color, pictograma y placa en braille grado 1 real; las especificaciones muestran la imagen en cada
  ficha (`docx_espec.js` acepta el bloque ["i", ruta, ancho, alto]).

## 27/10/2026 - CAR Varones: equipamiento y mobiliario (revisión del metrado, memoria, especificaciones)
- El usuario envió el plano EQUIPAMIENTO Y MOBILIARIO (láminas MB-01 a MB-09) y su metrado (copias en `insumos/katiuska/mobiliario/`)
  y pidió memoria, especificaciones y metrado, comprobando si está bien. Módulo `herramientas/varones/mobiliario/`:
  `lee_plano_mb.py` (48 cuadros de equipamiento por ambiente: título centrado, columnas a distancia fija del centro; etiquetas de
  código sobre el dibujo, también dentro de bloques y en directrices, por edificación), `datos_mb.py` (cantidades adoptadas =
  cuadros corregidos con lo dibujado, correcciones con su motivo, comparación con el original), `metrado_mb.py` (RESUMEN con SUMIF,
  METRADO POR AMBIENTE, VERIFICACIÓN, VERIF. IMPLEMENTOS, OBSERVACIONES), `fichas_mb.py` (características por familia),
  `memoria_mb.py` (26 p., tablas y planta por edificación), `espec_mb.py` (77 p.), `vistas_mb.py` (PNG por edificación).
- Resultado: el metrado original está mal. Hoja1 es de otro proyecto (colegio de 55 aulas); en HR: computadoras 18 (son 27),
  sillas M07 52 (80), escritorios M28 4 (32), armarios M37 25 (35), credenzas M44 20 (10, solo en el dormitorio de E-07),
  M63 como camilla 6 (es sofá de 3 cuerpos, 4; camillas M65 = 2), faltan M03 88, M04 16, M32 7, M14 2; implementos deportivos de
  otro proyecto; numeración con códigos repetidos y #REF!. Errores del plano: cuadros mal titulados (tópico de E-02 = almacén
  deportivo; "oficina de entrevista E-06" en MB-08 = almacén de cocina y gas), tópico de E-01 copiado de la sala de reuniones,
  dormitorio de la madre con 5 computadoras copiadas, descripciones cruzadas (M28, M51, M55), códigos K repetidos, extintores
  de 9 kg distintos de la lámina SE-S-01.
- 27/10/2026 (2): el usuario aclaró (captura del dormitorio de E-07) que se cuenta por la etiqueta escrita en la planta: en E-07 hay
  10 credenzas M44 junto a las camas (el cuadro decía armarios M37). Adoptado: M44 10, M37 35, M62 22 (cesto rotulado en
  secretaría).
- 27/10/2026 (3): nueva verificación por texto. `lee_plano_mb.etiquetas` ahora lee también las directrices múltiples que están dentro
  de bloques (hasta 6 niveles): aparecen las etiquetas de las 5 computadoras E6 por salón de estudios (E-04, E-05), del rack M13,
  la pizarra M69 y un tercer proyector E7 de E-01 (el del tópico). Se quitó la corrección "E7 del tópico = 0": E7 = 4, igual al
  original. Resultado: en equipos y mobiliario (E y M) lo adoptado coincide con lo rotulado en todas las edificaciones (642 und,
  0 diferencias). Implementos K: el plano rotula un solo ejemplar por tipo, así que mandan los cuadros; los cojines K78 de
  psicomotricidad son 10 dibujados y 7 rotulados (se metran 10).
- 27/10/2026 (4): el usuario observó que la memoria no mencionaba el M44 y que las imágenes de las plantas no se veían. Memoria
  (`memoria_mb.py`, 40 p.): cada ambiente con su párrafo de código y cantidad (p. ej. "10 credenza de melamina... (M44)"),
  cantidades ajustadas a la planta por edificación con su motivo completo, tabla de familias con columna UBICACIÓN y capítulo
  nuevo "Compatibilización del plano con el metrado" (método, tabla de correcciones y observaciones al plano); las plantas
  alargadas van en hoja horizontal sin reiniciar la numeración. Vistas (`vistas_mb.py`): caja por los muros de cada edificación
  (capas MURO/A-WALL/COLUMNAS y bloques de módulo), dibujo con el motor de ezdxf solo con las entidades de la caja (muros
  rellenos, aparatos, directrices); lo blanco se pasa a negro (las etiquetas de la capa 09 son blancas) sin tocar el negro.

## 27/10/2026 - Hogar de Refugio: índice de planos de arquitectura con el plano topográfico
- La usuaria envió el índice de láminas de arquitectura actualizado (copia en `insumos/solange/INDICE_DE_LAMINAS_ARQUITECTURA_HOGAR_REFUGIO_v2.xlsx`):
  respecto del anterior solo agrega PT-01 Plano topográfico (A1) en el grupo I. `indice_arquitectura_refugio.py` lee la v2 ->
  `entregables/INDICE_DE_PLANOS_ARQUITECTURA_HOGAR_REFUGIO.docx`: 108 láminas (I arquitectura 8, II módulos 34, III obras
  complementarias 15, IV obras exteriores 12, V detalles 37, VI evacuación y señalización 2), 2 páginas. Mismos arreglos de forma
  (grupos en orden, numeración correlativa, 6 códigos repetidos por copia), más espacios sueltos en descripciones
  ("DEPORTIVA /01-05", "(PATIO DE DESCARGA )").

## 28/10/2026 - Hogar de Refugio: sustento normativo del programa arquitectónico (pedido de Solange)
- Insumos: programación de áreas del 27-10-2026 y lista de normas (copias en `insumos/solange/sustento_normativo/`), textos de
  las normas A.030 (R.M. 005-2019-VIVIENDA), A.040 (R.M. 068-2020-VIVIENDA), A.080 y A.090 (D.S. 011-2006-VIVIENDA), R.V.M.
  104-2019-MINEDU (escaneada, leída como imagen) y los Lineamientos arquitectónicos para refugios de ONU-Habitat / CONAVIM (2016).
  La R.V.M. 208-2019-MINEDU no fue entregada: sus índices quedan "por cotejar".
- `herramientas/sustento_normativo_refugio.py` -> `entregables/SUSTENTO_NORMATIVO_PROGRAMA_ARQUITECTONICO_HOGAR_REFUGIO.docx`
  (17 p.: marco normativo, índices transcritos de cada artículo, población, sustento por zona y ambiente con área requerida /
  proyecto / superficie sugerida, criterios cualitativos, ambientes faltantes, observaciones y conclusiones) y
  `entregables/MATRIZ_SUSTENTO_NORMATIVO_PROGRAMA_ARQUITECTONICO_HOGAR_REFUGIO.xlsx` (MATRIZ con fórmulas, RESIDENCIAL, INDICES,
  NORMAS, AMBIENTES FALTANTES, RESUMEN con COUNTIFS/SUMIF). La programación de la usuaria no se modifica.
- Resultado: 71 ambientes, ninguno bajo el área de su norma; 10 a observar. Correcciones de cita: sala de reuniones (1.0 m² es
  A.090 art. 11), cuarto de limpieza, área de descanso, almacén general (8.80 m² es el dormitorio docente de la R.V.M. 104),
  triple tipo II. Garita contada dos veces; totales digitados en estacionamientos y patio de descarga. Habitación especial
  12 m² (lineamientos 28 m² + baño 6), despensa 6 m² (9/12), cocina 36 m² (0.40 x 113 = 45.2), baños compartidos 7 frente a
  13 juegos con el criterio de albergue (A.030 Anexo 4). 113 plazas en 23 habitaciones frente a ~35 residentes de los
  lineamientos: organizar en pabellones. Faltan cuarto del personal nocturno, sala del personal, sala para adolescentes,
  taller de cómputo y sala multiuso.
- 28/10/2026 (2): el usuario pidió que el sustento proteja el trabajo de la arquitecta (es para el expediente). Se separó: el
  sustento (Word 15 p. y matriz) solo sustenta, cada ambiente con la norma que le corresponde y su cálculo (dict EXP: sala de
  reuniones con A.090 art. 11, almacén general con R.V.M. 104 num. 13.3.1, despensa con la alacena, etc.), resultados CUMPLE /
  CONFORME, sin capítulo de observaciones; las observaciones y sugerencias pasan a una nota interna para la arquitecta
  (`entregables/revision_interna/PROGRAMACION_CORREGIDO_Y_POR_REVISAR_HOGAR_REFUGIO.docx`: 1) lo ya corregido en el sustento, 2) lo que ella debe revisar; no forma parte del expediente).


### 28-10-2026 – CAR Varones (CUI 2705619): índices de arquitectura en Word
- Fuente: índice en Excel de la usuaria (`insumos/katiuska/INDICE_DE_LAMINAS_ARQUITECTURA_CAR_VARONES.xlsx`). Generador
  `herramientas/varones/indice_arquitectura_v.py` (mismo estilo que los índices del Refugio).
- `INDICE_GENERAL_EXPEDIENTE_ARQUITECTURA_CAR_VARONES.docx`: resumen por tomo + detalle (Tomo I: 9 documentos D-01 a D-09; Tomos II a V: 89 láminas).
- `INDICE_DE_PLANOS_ARQUITECTURA_CAR_VARONES.docx`: solo las 89 láminas en 7 grupos, numeradas 01 a 89, 2 copias cada una.
- Arreglos de forma: numeración correlativa (el Excel no numeraba UL-02, PT-01 ni DT-09/00-03), códigos sin espacios, tildes y erratas,
  ED-02.2/2 "02 / 02 - 04" -> "02 / 02 - 02", DT-01/07-8 y 08-8 -> 07-08 y 08-08, SE-E-01 = evacuación y SE-S-01 = señalización (como los
  rótulos; el Excel las tenía cruzadas), MB-01 a MB-09 con el título de su rótulo. Formato no indicado en el Excel: "—".

### 28-10-2026 – Hogar de Refugio (CUI 2675514): análisis de incompatibilidades de ubicación
- Base: borrador de la arquitecta (`insumos/solange/sustento_normativo/ANALISIS_INCOMPATIBILIDADES_UBICACION_BORRADOR.docx`), 18 incompatibilidades
  del cuadro de la R.V.M. 010-2022-MINEDU, todas CUMPLE (se conservan). Generador `herramientas/incompatibilidades_refugio.py`.
- Expediente: `entregables/ANALISIS_INCOMPATIBILIDADES_UBICACION_HOGAR_REFUGIO.docx` (generalidades, colindantes CAR Varones/CAR Mujeres,
  marco normativo A.090 art. 3 y A.040 art. 7 b, metodología del área de influencia 50/100/150/200 m, cuadro apaisado, conclusiones) y
  `MATRIZ_INCOMPATIBILIDADES_UBICACION_HOGAR_REFUGIO.xlsx` (fórmulas: estado, área de influencia, resumen).
- Ajustes: "I.E."/"UP" -> predio del hogar; D.L. 25884 -> 25844; "Municipales" -> Municipalidades; aeródromo con la distancia al aeropuerto de
  Tarapoto (~3.5 km desde la UTM referencial, al costado de la pista 17/35); derecho de vía con el colector dentro del lindero.
- Nota interna (`entregables/revision_interna/INCOMPATIBILIDADES_CORREGIDO_Y_POR_REVISAR_HOGAR_REFUGIO.docx`): vigencia R.V.M. 010-2022 frente a
  R.V.M. 068-2025-MINEDU, líneas de MT en la carretera Oasis, PTAR propia (152 m²), nombre y distancia del establecimiento de salud, sustento gráfico.

### 28-10-2026 – Hogar de Refugio: cotejo con la R.V.M. N.° 208-2019-MINEDU (texto entregado)
- La usuaria envió la R.V.M. 208-2019 (primaria y secundaria; PDF escaneado de 115 p. en zip dividido; no se versiona, ver LEEME).
  Leída por imágenes: cuadros 12 (aula 2.00), 20 (taller de arte 3.00), 21 (EpT 3.50), 22 (SUM 1.00, máx. 300 m²), 23 (losa tipo II 800 m²),
  29 (archivo 6.00, depósito 4.00, sala de reuniones 1.50), 31 (tópico 9.00), 40 (caseta 3.00, maestranza 40.00, cuarto de limpieza 1.50,
  almacén general 1.50/sección mín. 10, depósito deportivo 16/30/60), num. 12.2.1 i (lavandería 3.00 m² x 1/2 usuarios), 12.2.1 k (almacén de
  ropa de cama 1.00 m² x dormitorio), anexo 4 (cocina escolar según normativa vigente).
- Sustento (`sustento_normativo_refugio.py`): citas 208 con numeral y cuadro; módulo de enseñanza vuelve a la cita de la arquitecta (cuadro 12);
  cocina por lineamientos (32 m²), despensa/alacena/maestranza CONFORME; resultado igual: 71 ambientes, 44 CUMPLE, 27 CONFORME.
- Nota interna: nueva sección 3 con el cotejo fila por fila y 4 puntos a decidir (maestranza 40 m², talleres EpT 3.50, almacén de ropa de cama
  23 m², lavandería). Incompatibilidades: se añade la R.V.M. 208 art. 8 c (selección del terreno según la N.T. Criterios Generales).

### 28-10-2026 – Hogar de Refugio: análisis de ubicación rehecho para el hogar (ya no de colegio)
- El borrador de la usuaria era el cuadro de un local educativo. `incompatibilidades_refugio.py` ahora: servicio y exigencias de ubicación
  (Ley 30364), marco normativo del proyecto (Ley 30364 y D.S. 009-2016-MIMP, R.M. 150-2016-MIMP, A.090 arts. 3 y 4, A.040 art. 7 b,
  R.V.M. 010-2022 como relación sectorial, R.V.M. 208 art. 8 c, lineamientos 2.1 a 2.8), Cuadro N.° 1 (18 incompatibilidades por cercanía,
  textos con la mirada del hogar) y Cuadro N.° 2 nuevo (8 condiciones propias del hogar: zonificación, zona tranquila no aislada, servicios
  de apoyo, accesos sin estudio de impacto vial (< 500 personas), seguridad, reserva del uso, servicios básicos, drenaje). Excel con hoja
  CONDICIONES HOGAR y RESUMEN de ambos cuadros. Nota interna: certificado de zonificación, servicios de apoyo con nombre y distancia, altura de colindantes.

### 28-10-2026 – CAR Varones (CUI 2705619): revisión y análisis de incompatibilidades de ubicación
- Insumos de Katiuska en `insumos/katiuska/arquitectura/` (memoria descriptiva de arquitectura y programación). Su cuadro (18 dispositivos,
  R.V.M. 068-2025-MINEDU, todos CUMPLE) está completo y con la norma vigente; tiene los mismos errores de copia del colegio: D.L. 25884 (es 25844),
  "Ley Orgánica de Municipales", fila 13 "Institución Educativa", "área definida para la UP", aeródromo sin mencionar el aeropuerto (~3.5 km).
- `herramientas/varones/incompatibilidades_v.py` (usa el motor del Refugio; `incompatibilidades_refugio.py` ahora parametriza SERV/HOJA2 en la
  matriz): Word con poligonal P1-P4 (6,999.98 m²), colindantes, usos dentro de 100 m, marco (D.Leg. 1297, A.090, A.040 art. 7, R.V.M. 068-2025,
  R.V.M. 208 art. 8), Cuadro 1 y Cuadro 2 (8 condiciones), Excel y revisión interna (fajas marginales vs "aguas de drenaje" de la memoria,
  comercio vecinal vs bebidas alcohólicas, acceso F.B.T. vs carretera Oasis, R.M. 377-2024-MIMP sin verificar, zonificación, pozo séptico).
- Corrección pedida de la memoria descriptiva de arquitectura y la programación de Katiuska (`varones/corrige_memoria_arquitectura_v.py`, copias
  en `entregables_varones/arquitectura/`): cuadro de incompatibilidades (Cuadro N.° 4; filas 4, 5, 7, 10, 12, 13, 14, 15, 17, 18), acceso F.B.T. +
  carretera Oasis, titular GORE (antes Aldea Infantil), "1. %", TOLERANCIAS CATASTRALES, imágenes 1 a 9, SENAMHI, R.V.M., EM.110 (no A.030),
  drenaje del proyecto (no "cunetas existentes"), A.090 en la normativa, subtotal mal rotulado (1,103.81 sin cerco en ml) y total 4,281.52
  (antes 4,205.30: valor viejo sin el estacionamiento), listado de planos "(POR DEFINIR)" -> 89 láminas del índice. Excel: fórmulas I103/I125,
  #REF! fuera, Nutrición m2, erratas. 30 imágenes conservadas.
- Memoria de arquitectura del CAR Varones (pedido de la arquitecta): análisis de ubicación dentro del numeral 2.3 (2.3.1 método + Cuadro N.° 4;
  2.3.2 Cuadro N.° 5 con las 8 condiciones de `incompatibilidades_v.CONDICIONES` + conclusión), "INCOMPATILIDAD" corregido, e índice nuevo en la
  página 2 (campo TOC de Word con `updateFields`, 39 títulos con nivel de esquema, páginas calculadas con LibreOffice usando una fuente de
  paginación tipo Arial Narrow: `varones/fuente_paginacion.py`, solo para paginar). 43 páginas.
- Revisión a fondo de la memoria descriptiva de arquitectura "culminada" del Hogar de Refugio (Solange, CUI 2675514), copia en
  `insumos/solange/arquitectura/`. `herramientas/corrige_memoria_arquitectura_refugio.py` -> copia corregida en `entregables/arquitectura/`
  (60 págs., 32 imágenes conservadas, áreas del programa sin cambio) y nota interna `entregables/revision_interna/REVISION_MEMORIA_...`.
  Corregido: texto de colegio (Institución Educativa, aulas, aprendizaje, NTIE 001-2017, R.V.M. 307-2019), titular GORE (no Aldea Infantil),
  0.085562 -> 0.85562 ha, unidades, imágenes 1 a 9, Cuadro N°3, usos a 100 m (no el propio hogar), análisis 2.3 vacío -> 2.3.1 Cuadro N° 4 (18)
  y 2.3.2 Cuadro N° 5 (8), fuente del terreno tipo II = R.V.M. 208 cuadro 2, normativa (Ley 30364, R.M. 150-2016-MIMP, R.V.M. 104/208, Ley
  30102), drenaje del proyecto, EM.110, Cuadro N°06 en demanda, sustento pegado renumerado 3.2.1-3.2.11 y Tablas 02-12, citas del programa =
  sustento, listado de 108 láminas, índice con páginas. Para confirmar con ella: garita repetida, totales de estacionamientos/patio de descarga,
  circulación + 15 % muros (2,803.64 vs 2,607.97), rótulo "área construida (interior)", 7 SS.HH. para 10 habitaciones dobles, R.V.M. 010-2022
  vs 068-2025, Polvoraico/Polvorico, zonificación, servicios de apoyo, fecha de imágenes.
  `CV.reemplazar` ahora solo toca los runs del texto cambiado (antes duplicaba el texto de hipervínculos); Varones regenerado, texto idéntico.
- Pedido: carátula en guinda con otra forma, 4 opciones en un Word con vista previa. `herramientas/varones/caratulas_opciones_v.py` (contenido de
  `caratulas_v.py`, ejemplo "MEMORIA DESCRIPTIVA"): 1 banda lateral guinda, 2 franjas superior e inferior, 3 marco clásico (borde de página doble),
  4 bloques; página 1 con el mosaico (render LibreOffice) y PNG por opción en `entregables_varones/figuras_caratula/`. Falta que elija una.
- Corrección del usuario: las opciones de carátula no eran para Varones sino para el Hogar de Refugio (Solange). Script movido a
  `herramientas/caratulas_opciones_refugio.py` (datos de `caratulas_refugio.py`, servicio y especialidad de arquitectura, para su memoria
  descriptiva de arquitectura); salida en `entregables/arquitectura/OPCIONES_CARATULA_GUINDA_MEMORIA_ARQUITECTURA_HOGAR_REFUGIO.docx`.
  Se retiró la versión de Varones.
- Hogar de Refugio, equipamiento y mobiliario (pedido: metrado, memoria descriptiva y especificaciones). DXF de Solange (77 MB, en
  `insumos/solange/mobiliario/` comprimido): 7 láminas EM-01 a EM-07 en el modelo (marcos capa "M ARCO"), 31 cuadros (230 filas), 1069
  etiquetas de código en planta. `herramientas/mobiliario_refugio/`: E y M del metrado = lo rotulado en planta en las 9 edificaciones
  (comprobado por código); K = cuadro salvo que la planta rotule más. Ajustes: E-01 (M32, M34, M36, M39, M62, 8 sillas M07 en pasadizo),
  E-02 (cuadro del tópico repetido y mal titulado, M28 3->1, M76), E-03 (M51 15->6, M75 5->3), E-05 (SUM 384->192 sillas M3, K78 1->8,
  M62), E-09 (cuadro "módulo infantil" = almacén deportivo, M51 3, M52 0, M64 = canastilla, K53/K73/K74/K79 agregados). Códigos dobles
  M16 (mesa de corte textil / mesa de trabajo) y M64 (camarote / canastilla) como partidas separadas. Extintores S1 fuera (señalización).
  99 partidas, 1251 und. Para confirmar con Solange: SUM 192 asientos vs 80 del programa, sillas de estudiante en el comedor, E10.
