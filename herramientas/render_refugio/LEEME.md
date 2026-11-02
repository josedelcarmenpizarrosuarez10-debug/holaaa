# Renders del Hogar de Refugio Temporal (CUI 2675514)

Modelo 3D en Blender (bpy 4.2, Python 3.11) armado con los planos de la arquitecta:
- `extrae.py`: polígonos de techos, veredas y bloques de la planta general `PG 01-PG 02 PLANTA GENERAL.dxf` -> `escena.json`
  (coordenadas locales: origen E 349090, N 9281600).
- `escena.py`: edificaciones E-01 a E-09 (techos a dos aguas, alero 1.50 m, muros TP-2, columnas y viga TP-1, hastiales TP-3),
  losa deportiva con techo en arco, pórtico de ingreso OE-01 según su detalle (frente 13.75 m, viga +4.18, parapeto con letras
  +5.09 a +5.95, techo S = 30 %), estacionamientos, tanque elevado, cerco perimétrico (frente con reja a ambos lados del pórtico),
  plaza con pérgola, juegos, calle, pasto 3D, árboles con follaje de hojas, personas y cielo físico -> `refugio.blend`.
- `render.py <vista|todas> <muestras> <ancho>`: 15 cámaras (`SALIDA_RENDERS` = carpeta de salida).
- Colores (cuadro de la arquitecta): TP-1 RGB 123-31-45, TP-2 RGB 125-133-139, TP-3 RAL 9010; vista "Standard" para que salgan tal cual.
- Assets libres: `sh descarga_assets.sh`. Los DXF de la arquitecta (650 MB) no se versionan.
