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
- Junta de cunetas 01.04.03.04.03.03: en toda la sección en U (2 muros + losa de fondo), EG-2013 MTC Sección 510. Longitud por junta = 2 × H + 0.40; 233 juntas: 241.96 → 335.16 ml. Lámina nueva DJ-01 (`entregables/PLANO_DJ-01_JUNTA_CUNETAS_HOGAR_REFUGIO.dxf`) y especificación actualizada.
- Mano de obra 2026: hoja COSTO HORA HOMBRE 2026 con la tabla oficial CAPECO - FTCCP 2026 (Exp. N° 339-2025-MTPE/2.14-NC; PDF en `insumos/normas/`): operario 28.95, oficial 22.68, peón 20.54, con su desglose (leyes sociales 112.20 %, BUC, movilidad, overol). Todas las ACU leen de ella.
- Hoja ACU LLORADEROS dentro de la planilla: S/ 20.56 por und, partida S/ 3,227.64 (tubo PVC 3" Pavco S/ 39.90 el tubo de 3 m, geotextil 200 g/m² S/ 5.75/m², grava a S/ 70.00/m³ de Agregados Tarapoto). Se borró el Excel aparte.
- Siguen por cotizar en Tarapoto: piedra chancada 1/2", grava de 20 a 40 mm y alquiler de soldadora.

## Cómo imprimir (los tres proyectos)
1. Abrir la pestaña de la lámina (DP-00, DP-01, ...).
2. Ctrl+P: área = Presentación, escala 1:1, centrar.
3. Elegir tu plotter con el mismo papel. "DWG To PDF" solo sirve para que AutoCAD encuentre los papeles ISO.
4. Para imprimir todas las láminas de una vez: PUBLISH.

## Archivos
| Proyecto | Planos | Vistas previas | Notas |
|---|---|---|---|
| CAR Mujeres | `entregables_mujeres/PLANOS_COLECTOR_MEJORADOS/PLANOS_COLECTOR_PLUVIAL_CAR_MUJERES.dxf` | `entregables_mujeres/PLANOS_COLECTOR_MEJORADOS/vistas_previas/` | `LEEME.txt` |
| CAR Varones | `entregables_varones/PLANOS_COLECTOR_PLUVIAL_CAR_VARONES.dxf` | `entregables_varones/vistas_previas/` | `LEEME_PLANOS.txt` |
| Hogar de Refugio | `entregables/PLANOS_COLECTOR_PLUVIAL_HOGAR_REFUGIO.dxf` | `entregables/INDICE_DP-00_VISTA_PREVIA.png` | – |

## Reglas que se mantienen
- No modificar los metrados del usuario.
- Vistas previas en PNG; nada de PDF.
- Escala real ("si algo mide 0.56, así debe medir").
- No mezclar partidas ni láminas.
- Decir "cota de fondo".
- Citar los proyectos por nombre y CUI.
