# Renders del Hogar de Refugio Temporal (CUI 2675514)

Modelo 3D en Blender (bpy 4.2, Python 3.11) armado con los planos de la arquitecta:
- `extrae.py`: polígonos de techos, veredas y bloques de la planta general `PG 01-PG 02 PLANTA GENERAL.dxf` -> `escena.json`
  (coordenadas locales: origen E 349090, N 9281600).
- `escena.py`: edificaciones E-01 a E-09 (techos a dos aguas, alero 1.50 m, muros TP-2, columnas y viga TP-1, hastiales TP-3),
  losa deportiva con techo en arco, pórtico de ingreso OE-01 según su detalle (frente 13.75 m, viga +4.18, parapeto con letras
  +5.09 a +5.95, techo S = 30 %), estacionamientos, tanque elevado, cerco perimétrico (frente con reja a ambos lados del pórtico),
  plaza con pérgola, calle, pasto 3D, árboles con follaje de hojas y cielo físico -> `refugio.blend` (sin personas, pedido del usuario).
- Drenaje pluvial tal cual el plano del usuario (`PLANTA GENERAL - MUJERES VIOLENTADAS.dxf` del 02-11-2026, bloque "red drenaje"):
  `extrae_red_usuario.py` -> `red_drenaje_usuario.json`; `extrae_drenaje.py` -> agrega a `escena.json` los ejes de cuneta 01 a 12
  (`insumos/solange/EJES_CUNETAS_REFUGIO.json` ajustados a lo dibujado), 17 tapas de inspección, 30 sumideros con rejilla, las
  cunetas del frente, los 3 juegos OC-01 (jardinera + banca + pérgola), los equipos del OC-04 sobre arena (achurado AR-SAND) y los
  registros del colector frontal (`entregables/_calc/diseno.json`). En la escena: cuneta 0.40 con muros de 0.10 y rejilla de
  platinas 1" x 3/16" @ 0.025, canaletas galvanizadas en los aleros, montantes PVC 4" con falsa columna en las esquinas de cada
  edificación, losa del colector b = 0.80 con tapas ciegas y juntas de 1".
- `render.py <vista|todas> <muestras> <ancho>`: 21 cámaras (`SALIDA_RENDERS` = carpeta de salida); la 19 es la planta de la red
  de drenaje sin coberturas ni árboles, en formato vertical como el plano.
- Colores (cuadro de la arquitecta): TP-1 RGB 123-31-45, TP-2 RGB 125-133-139, TP-3 RAL 9010; vista "Standard" para que salgan tal cual.
- Assets libres: `sh descarga_assets.sh`. Los DXF de la arquitecta (650 MB) no se versionan.
