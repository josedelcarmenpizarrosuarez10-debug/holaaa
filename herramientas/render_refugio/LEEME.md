# Renders del Hogar de Refugio Temporal (CUI 2675514)

Modelo 3D en Blender (bpy 4.2, Python 3.11) armado con los planos de la arquitecta:
- `extrae.py`: polígonos de techos, veredas y bloques de la planta general `PG 01-PG 02 PLANTA GENERAL.dxf` -> `escena.json`
  (coordenadas locales: origen E 349090, N 9281600).
- `escena.py`: edificaciones E-01 a E-09 (techos a dos aguas, alero 1.50 m, muros TP-2, columnas y viga TP-1, hastiales TP-3),
  losa deportiva con techo en arco, pórtico de ingreso OE-01 según su detalle (frente 13.75 m, viga +4.18, parapeto con letras
  +5.09 a +5.95, techo S = 30 %), estacionamientos, tanque elevado, cerco perimétrico de muro en todo el lote (sin rejas en el ingreso; portones y paños
  del OE-01 de plancha metálica llena),
  patio cívico OC-03 libre (sin pérgola, indicación de la usuaria), calle, pasto 3D, árboles con follaje de hojas y cielo físico -> `refugio.blend` (sin personas, pedido del usuario).
- Drenaje pluvial tal cual el plano del usuario (`PLANTA GENERAL - MUJERES VIOLENTADAS.dxf` del 02-11-2026, bloque "red drenaje"):
  `extrae_red_usuario.py` -> `red_drenaje_usuario.json`; `extrae_drenaje.py` -> agrega a `escena.json` los ejes de cuneta 01 a 12
  (`insumos/solange/EJES_CUNETAS_REFUGIO.json` ajustados a lo dibujado), 17 tapas de inspección, 30 sumideros con rejilla, las
  cunetas del frente, los 3 juegos OC-01 (jardinera + banca + pérgola), los equipos del OC-04 sobre arena (achurado AR-SAND) y los
  registros del colector frontal (`entregables/_calc/diseno.json`). En la escena: cuneta 0.40 con muros de 0.10 y rejilla de
  platinas 1" x 3/16" @ 0.025, canaletas galvanizadas en los aleros, montantes PVC 4" con falsa columna en las esquinas de cada
  edificación, losa del colector b = 0.80 con tapas ciegas y juntas de 1".
- `render.py <vista|todas> <muestras> <ancho>`: 22 cámaras (22 = fachada en perspectiva) (`SALIDA_RENDERS` = carpeta de salida); la 19 es la planta de la red
  de drenaje sin coberturas ni árboles, en formato vertical como el plano.
- Colores (cuadro de la arquitecta): TP-1 RGB 123-31-45, TP-2 RGB 125-133-139, TP-3 RAL 9010; la serie con las edificaciones usa la vista AgX.
- Serie con las edificaciones de los planos (03-11-2026): `escena.py` toma de `edificaciones_revit.json` (de
  `lee_edificaciones.py`, el mismo dato del modelo Revit) los muros reales con sus vanos, puertas y ventanas con el tamaño de
  los DT, vigas y columnas a la altura de los cortes, cubiertas de la PG-02 al 30 %, la nave alta del SUM y el sobretecho con
  celosías de la administración. 22 vistas: 7 aéreas (A1-A7), 2 de fachada (F1-F2), 2 peatonales entre edificaciones (P1-P2),
  4 más (O1-O4), estacionamientos (E1-E2), biohuerto (B1-B2), tanque (T1), patio de descarga y PTAR (D1), planta general (PL1):
  `blender -b -P render.py -- serie_planos 192 1920` con `SALIDA_RENDERS=../../entregables/renders_hogar_refugio/modelo_planos`
  y `FORMATO_RENDERS=JPG`.
- En Windows: Blender 4.2 LTS portable (`D:/PROYECTOS/blender`, con shapely instalado en su Python):
  `blender.exe -b --factory-startup --python escena.py` y luego el `render.py` de arriba (usa la GPU OptiX o CUDA si la hay).
- Exteriores de la serie, cada uno con su lámina: OE-02/03 estacionamientos (coberturas TR-4 en arco, autos y motos armados con
  primitivas), biohuerto, OC-02, OC-03 patio cívico (contornos de la capa 1-TEXTURA PISOS: el sardinel rodea cada banca por detrás
  y la banca da al patio, al ras), OE-04 patio de descarga, OE-05 cerco, OE-06 tanque elevado, OE-07 PTAR (piso de tierra o hierba,
  sin concreto: del tanque y los pozos enterrados solo asoman las tapas).
- `cerco_columnas.json`: ejes de las columnas del cerco, leídos de la capa `1-COLUMNA CERCO PERIMETRICO` del DXF; es un dato
  versionado, no lo genera ningún script de esta carpeta.
- Árboles: se descartan los que no caben; la copa se reduce donde hay poco espacio y ninguno atraviesa una cobertura ni el cerco.
- Tono: vista AgX (`AgX - High Contrast`, exposición -1.0), 10 rebotes. Cielo en dos ramas: lo que ve la cámara (intensidad 1.15, con nubes) y lo que ilumina
  la escena (intensidad 0.22, o 0.5 con sol bajo, sol 0.23 y luz blanca de las nubes, que rellena las sombras).
- Assets libres: `sh descarga_assets.sh`. Los DXF de la arquitecta (650 MB) no se versionan.
