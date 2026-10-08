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
