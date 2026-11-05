# 05 — Planos DXF: estilo, láminas, plantas, perfiles, secciones, detalles e isométricos

Base de conocimiento permanente del dibujo de planos de drenaje pluvial (colectores frontales y cunetas) del repositorio.
Recoge todo lo aprendido desde el 3 de octubre de 2026: reglas del usuario, constantes del código, cómo se arma cada
vista, cada corrección que hizo el usuario (qué estaba mal y cómo quedó) y una guía para implementarlo en un programa propio.

Fuentes leídas: `conocimiento/_fuentes/mensajes_usuario.txt`, `BITACORA_CONVERSACION.md`, `CLAUDE.md`, skills
`planos-ordenados`, `diseno-colector-pluvial`, `planteamiento-cunetas-terreno`, `metrado-cunetas`, el historial de git
y el código de `herramientas/` (archivos citados en cada sección).

---

## 1. Reglas no negociables del usuario (resumen)

| Regla | Origen (fecha) | Cómo se cumple en el código |
|---|---|---|
| Escala real: 1 unidad de dibujo = 1 m. "Si algo mide 0.56, así debe medir en el plano." | 03-10 (losa 0.20 "con comando L"), 07-10, 21-10 | Toda la geometría en metros; cada lámina tiene un factor `f = escala/1000` (m de modelo por mm de papel). Perfiles H = V. |
| Las cotas deben medir el dibujo; nunca escribir un número que no corresponde ("pones 3.50 y mide 7.30") | 03-10 | DIMENSION con texto `<>` (medida automática). Texto fijo solo para pulgadas, alias ("h", "ventana") o vistas ampliadas con su escala indicada. |
| Fondo de AutoCAD blanco: no usar amarillo ni cian claro ni blanco como color de línea | 03-10 | Paleta de capas sin amarillo (ver §4). |
| Los 3D/isométricos no deben salir negros (en el celular salían negros) | 03-10 | Color verdadero (RGB) en cada entidad SOLID/HATCH, no solo en la capa. |
| Acero longitudinal y transversal en colores distintos; longitudinales como círculos (no cuadraditos) y a diámetro real (3/8" = 9.5 mm, 1/2" = 12.7 mm) | 03-10 | Transversal rojo (capa ACERO, ACI 1); longitudinal azul (ACERO-PUNTOS / ACERO-LONG, ACI 5), bloques `ACERO-38` y `ACERO-12` con radio real insertados a escala 1.0. |
| Nada "al aire": el acero no sale del concreto | 03-10 | Marcos con recubrimiento real (0.04 / 0.025 m); acero interrumpido en ventanas de cajas. |
| Textos sin encimarse, sin textos verticales, líneas de llamada que no se crucen, usar flechas | 03-10, 07-10 | `franja`, `columna_llamadas`, `juntar_llamadas/volcar_llamadas`, `llamada` con flecha (§8). |
| Letra grande (las letras eran "pequeñitas") | 07-10 | Factor `K_TXT` por capa (≈1.3–1.35) sobre alturas de 1.6–4.0 mm. |
| Concreto con relleno gris SÓLIDO, no patrones; los patrones (EARTH, AR-CONC, AR-SAND, GRAVEL) en AutoCAD salen sin escala ("se ve horrible") | 07-10 (estilo), 22-10 (lloraderos) | `achurado()` del concreto llama a `relleno()` sólido RGB (226,226,226). Lloraderos del Refugio: rellenos sólidos + piedras y punteado dibujados uno a uno. |
| Láminas ordenadas, llenas con leyendas, colores y qué significa cada uno | 07-10 | Leyenda con muestras grandes (`leyenda2`), notas, cuadros. |
| Tamaño de papel según el dibujo (A0, A1, A2, A3), sin espacio vacío excesivo | 08-10 | `Lamina(..., formato=)`; presentaciones con papel ISO full bleed. |
| Presentaciones (layouts) de AutoCAD listas para imprimir e índice de láminas | 08-10 | `dxf_layouts.presentaciones()` e `indice()` (lámina DP-00 / DC-00 en A3). |
| Ser fiel al dibujo del usuario (no inventar, no omitir piezas como el colgador) | 19-10 | Se leen medidas del DXF del usuario; diferencias se informan, no se corrigen solas. |
| Nada de obra dibujado fuera del límite de intervención (cerco) | 20-10 | Bloque `LIMITE_DE_INTERVENCION`; fuera del cerco solo el agua sobre el terreno. |
| Quiebres de 45° en planta (no de 90°); en el perfil no se muestran | 21-10 | `diseno_b.chaflanes()` (chaflán de 0.60 m); nudos "~" omitidos en perfiles. |
| No poner "bloque X y número" en los títulos; solo nombre del eje, progresivas y "pabellón" | 21-10 | Título del perfil = eje + descripción sin coordenadas + progresivas. |
| Planos ya impresos por el usuario: no regenerar | 21-10 | Cambios posteriores van a los documentos y se avisa. |
| Nada que revele IA; sin nombre ni CIP del proyectista | permanente | Rótulo con `PROYECTISTA: ____ CIP: ____` en blanco. |
| Decir siempre "cota de fondo" (no "invert"); citar proyectos por nombre y CUI | permanente | Textos "CF", "C.F.", "NCF", "cota de fondo". |
| Entregar DXF + vista previa PNG; PDF solo si se pide | permanente | `dxf_render.py`. |
| Todo cambio en el generador, nunca a mano en el DXF final | permanente | Generadores Python en `herramientas/`. |

---

## 2. Unidades, documento DXF y compatibilidad con AutoCAD

Archivo: `herramientas/dxf_base.py` (`nuevo_documento()`).

- Versión DXF R2010 (`ezdxf.new("R2010", setup=["linetypes"])`).
- Cabecera: `$INSUNITS = 6` (metros), `$LUPREC = 2`, `$LTSCALE = 0.25` (para que DASHED/HIDDEN se vean en planos en metros).
- Tipo de línea `HIDDEN` definido si falta: patrón `[0.375, 0.25, -0.125]`.
- Estilos de texto: `STANDARD` con `arial.ttf`; `TITULOS` con `arialbd.ttf` (Arial negrita).
- Reglas para que AutoCAD abra el archivo sin errores (pedido del traspaso, 03-10):
  - Sin "/" en nombres de bloque.
  - En cada DIMSTYLE deben existir los grupos 3–7: `dimpost="<>"`, `dimapost=""`, `dimblk=""`, `dimblk1=""`, `dimblk2=""`.
  - Cada elemento en su capa con nombre y color; cotas como entidades DIMENSION; bloques para lo que se repite.
  - Ejecutar `doc.audit()` antes de guardar (0 errores).
- Símbolos fuera del ASCII: el "³" no sale en AutoCAD (aparecía "m?"): escribir "m3", "m2" (corrección del 22-10).
  Diámetro: secuencia de AutoCAD `%%c` (p. ej. `%%c3/8"@0.20`).
- Textos de bases ajenas con caracteres rotos se pasan a ASCII (`mujeres/planos_m.ascii_`: normaliza NFKD y quita tildes).
- Láminas en milímetros de papel (DP-06B de la tapa ciega): `ezdxf.new('R2010', setup=True, units=4)` (mm), `$LTSCALE = 8`,
  estilos `ARIAL`/`ARIALB`; DIMSTYLE con `dimlfac = escala/1000` para que la cota muestre metros reales (ver §11.9).

### 2.1 Organización del espacio modelo
- Cada lámina se dibuja en su propia zona del modelo con origen `(ox, oy)` (esquina inferior izquierda del papel) y su escala.
- La planta se dibuja en coordenadas reales (locales del plano de arquitectura o UTM) para que quede "en su sitio"; el origen
  de la lámina se calcula a partir de esas coordenadas (p. ej. Refugio `OX1 = X_SO - 50`, `OY1 = Y_CERCO - 78`;
  Barranquita `ox = caja[0] - 30 f`, `oy = caja[3] - 578 f`).
- Las demás láminas se apilan en filas/columnas separadas (p. ej. `OX1 + 200`, `OY1 - 200`, `OY1 - 400`...).
- Al terminar se guarda la caja de cada lámina en `_calc/laminas.json`: `{codigo: [ox, oy, ox + W f, oy + H f]}`
  (Refugio `entregables/_calc/`, Varones `entregables_varones/_calc/`, Mujeres `entregables_mujeres/PLANOS_COLECTOR_MEJORADOS/`,
  Barranquita `entregables_barranquita/_calc/`). Esa caja la usan la vista previa, la auditoría y las presentaciones.

---

## 3. Formatos de lámina, marco y rótulo

### 3.1 Formatos (horizontal, mm)
| Formato | Ancho x alto (mm) | Papel AutoCAD (presentación) |
|---|---|---|
| A0 | 1189 x 841 | `ISO_full_bleed_A0_(1189.00_x_841.00_MM)` |
| A1 | 841 x 594 (por defecto) | `ISO_full_bleed_A1_(841.00_x_594.00_MM)` |
| A2 | 594 x 420 | `ISO_full_bleed_A2_(594.00_x_420.00_MM)` |
| A3 | 420 x 297 | `ISO_full_bleed_A3_(420.00_x_297.00_MM)` |

Criterio (usuario, 08-10): "hay planos grandes y otros pequeños; dimensionar algunos en A1, otros en A2 o hasta A0" y reducir
espacios vacíos. Ejemplos aplicados: CAR Mujeres DP-02, DP-06C y DP-08 en A2, el resto A1, índice DP-00 en A3; CAR Varones
DP-02 en A2; detalle de lloraderos del Refugio con presentaciones A3 a 1:10.

### 3.2 Marco (`Lamina.marco`)
- Borde exterior del papel: rectángulo 0..W x 0..H (capa MARCO).
- Marco interior: x de 25 a W−10 mm, y de 10 a H−10 mm, polilínea con ancho constante 0.8 mm de papel
  (margen izquierdo de 25 mm para el anillado). En A1: x 25–831, y 10–584.
- Todo el dibujo debe quedar dentro del marco interior; el texto de la franja de etiquetas no pasa de x = 826 mm (A1).

### 3.3 Rótulo (`Lamina.rotulo`), esquina inferior derecha, 185 x 95 mm
Caja: x0 = W−195, y0 = 10, x1 = W−10, y1 = 105 (polilínea de 0.5 mm). Líneas horizontales en y1−22, y1−40, y1−52, y1−62,
y1−74, y1−85. Líneas verticales en x0+125 (desde y1−62 hacia abajo) y x0+165 (desde y1−74 hacia abajo).

| Campo | Posición (mm desde x0, y1) | Altura base (mm) | Contenido |
|---|---|---|---|
| PROYECTO: | (2, −3.5) | 2.0 | etiqueta |
| Nombre del proyecto (2 líneas) | (2, −8) y (2, −11.5) | 1.6 | `B.PROYECTO` (tupla de 2 líneas; la 2.ª termina en "CUI N. xxxxxxx" o "C.I. N.° ...") |
| ENTIDAD | (2, −17.5) | 1.6 | `B.ENTIDAD` (p. ej. "ENTIDAD: GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO") |
| UBICACIÓN | (2, −27) | 1.8 | `B.UBICACION` |
| ESPECIALIDAD | (2, −33) | 1.8 | `B.ESPECIALIDAD` ("INSTALACIONES SANITARIAS - DRENAJE PLUVIAL") |
| PLANO: + título | (2, −44.5) / (14, −44.5) | 2.0 / 2.4 | título de la lámina; si pasa de 62 caracteres la altura baja a `max(1.5, 2.4·62/len)` |
| Subtítulo | (14, −49) | 1.8 | `subtitulo` (no más de ~110 caracteres) |
| PROYECTISTA / CIP | (2, −57.5) | 1.8 | `PROYECTISTA: ______________________        CIP: ________` (siempre en blanco) |
| ELABORADO | (2, −68) | 1.8 | `B.ELABORADO`; vacío = no se escribe (Barranquita lo deja vacío) |
| ESCALA | (127, −68) / (143, −68) | 1.8 / 2.4 | `escala_txt` ("1/50", "INDICADA", "S/E") |
| REVISADO | (2, −79.5) | 1.8 | `REVISADO: ________________` |
| FECHA | (127, −79.5) / (143, −79.5) | 1.8 / 2.0 | `B.FECHA` ("OCT. 2026") |
| LÁMINA | (167, −79.5) | 1.8 | etiqueta |
| FIRMA Y SELLO | (2, −91) | 1.8 | en blanco |
| REVISIÓN | (127, −91) | 1.8 | "REVISION: 00" |
| Código de lámina | esquina (x1−1.5, y0+1.5), alineado abajo-derecha | 4.0 (capa TITULOS → 5.4 mm) | "DP-01", "DC-12"... |

Capa del texto del rótulo: ROTULO-TEXTO (factor de altura 1.0, sin ampliación). Los datos `B.PROYECTO`, `B.UBICACION`,
`B.ESPECIALIDAD`, `B.ENTIDAD`, `B.ELABORADO`, `B.FECHA` se fijan por proyecto ANTES de crear las láminas
(Varones en `varones/compat.py`, Mujeres en `mujeres/planos_m.py`, Barranquita en `barranquita/planos_b.py`).

Rótulo de la DP-06B (lámina en mm, `render_tapa/dxf_tapa_ciega.py`): membrete propio de (590, 12) a (W−12, 90) con líneas en
by+58, +42, +24, +12, separación vertical en bx+150; PROYECTO en MTEXT 2.4 mm ancho 232; ENTIDAD/UBICACIÓN/ESPECIALIDAD 2.5 mm;
PLANO en 2 líneas ARIALB 3.4 mm; PROYECTISTA/CIP en blanco 2.6 mm; "ESCALA: INDICADA FECHA: OCT. 2026"; "REVISION: 02";
código "DP-06B" 9 mm en ARIALB.

### 3.4 Códigos de lámina usados
- Colector: DP-00 índice, DP-01 planta, DP-02 perfil general, DP-03A/B/C perfiles de detalle, DP-04A/B secciones con acero,
  DP-05A/B isométricos de secciones, DP-06A secciones típicas, DP-06B registro y tapa, DP-06C empalme de cuneta,
  DP-06D isométricos de la tapa, DP-07 cajas / estructura de salida / empalme, DP-08 cuadros de acero y especificaciones,
  DP-09 isométricos constructivos, DP-10 isométrico general; DA-01 a DA-03 detalle de partidas; DD-01 a DD-04 detalles constructivos.
- Cunetas: DJ-01 a DJ-03 (junta, proceso constructivo, rejilla); DL-00 planta de lloraderos, DL-01/DL-02 detalle de lloraderos;
  DS-01/DS-02 caja sumidero; DR-01 a DR-06 red de techo; DB-01 a DB-03 banca (CAR Mujeres); DO-01/DO-02 → DPL-41/DPL-42 OC-01 (Refugio).
- Barranquita: DC-00 índice, DC-01 planta, DC-02 cuadro y secciones típicas, DC-03 a DC-11 perfiles, DC-12 a DC-14 secciones,
  DC-15 cortes generales, DC-16 a DC-19 detalle de descargas D1 a D4 (numeración correlativa: si cambia la cantidad de perfiles,
  las siguientes se renumeran sin saltos).
- Juegos finales renombrados por los usuarios (se respetan tal cual en índices y documentos, incluso con errores de tipeo):
  Refugio DPL-01 a DPL-42; CAR Varones DPLV-01 a DPLV-44 (con "DPVL-09", "DPVL-10", "DVPL-11" tal como están en el rótulo);
  CAR Mujeres 46 láminas con códigos propios (ST-CG-01, STP-CG, D-RL, ESDAE-01, IC-01, RGDPLV-01, PCPLV-01, D-ECC...).

---

## 4. Capas, colores y grosores

### 4.1 Capas base (`dxf_base.CAPAS`: nombre, color ACI, tipo de línea) y grosor (`GROSOR`, centésimas de mm)
| Capa | ACI | Tipo | Grosor | Uso |
|---|---|---|---|---|
| MARCO | 7 | CONTINUOUS | 50 | marco de lámina, ventanas de presentación |
| ROTULO | 7 | CONTINUOUS | 35 | líneas del rótulo |
| ROTULO-TEXTO | 7 | CONTINUOUS | – | textos del rótulo |
| TITULOS | 160 (azul) | CONTINUOUS | 35 | títulos de vista, de leyenda y de tablas (Arial negrita) |
| TEXTOS | 7 | CONTINUOUS | – | textos y llamadas |
| TEXTOS-NOTAS | 7 | CONTINUOUS | – | notas |
| LEYENDA | 7 | CONTINUOUS | – | textos de leyenda |
| COTAS | 94 (verde oscuro) | CONTINUOUS | 18 | DIMENSION |
| NIVELES | 7 | CONTINUOUS | – | símbolo y texto de nivel |
| LLAMADAS | 30 (naranja) | CONTINUOUS | 18 | líneas de llamada y flechas |
| EJE-COLECTOR | 1 | CENTER | 18 | eje del colector |
| CONCRETO | 250 (gris muy oscuro) | CONTINUOUS | 50 | contorno de concreto cortado |
| CONCRETO-OCULTO | 8 | HIDDEN | 25 | caras ocultas (interior bajo losa) |
| CONCRETO-ACHURADO | 8 | CONTINUOUS | – | relleno sólido RGB (226,226,226) |
| SOLADO | 8 | CONTINUOUS | – | solado f'c=100, e=0.05 |
| ACERO | 1 (rojo) | CONTINUOUS | 35 | acero transversal (marcos), barras vistas de largo |
| ACERO-LONG | 5 (azul) | CONTINUOUS | 35 | acero longitudinal visto de largo en perfiles |
| ACERO-PUNTOS | 5 (azul) | CONTINUOUS | – | barras cortadas (círculos rellenos a diámetro real) |
| REGISTRO | 32 | CONTINUOUS | 35 | luz libre del registro |
| REGISTRO-TAPA | 30 | CONTINUOUS | 18 | tapa |
| MARCO-METALICO | 32 | CONTINUOUS | 40 | ángulos metálicos (marco y contramarco; histórico) |
| JUNTAS | 8 | DASHED | – | juntas / tecnopor |
| CRUCE-VEHICULAR | 30 | CONTINUOUS | – | zonas de cruce |
| CUNETA | 3 (verde) | CONTINUOUS | 35 | cunetas que llegan |
| CUNETA-OCULTA | 3 | HIDDEN | – | interior de cuneta |
| POZA | 34 | CONTINUOUS | 35 | poza / umbral / emboquillado |
| TERRENO | 7 | CONTINUOUS | 30 | piso terminado / NPT (línea gruesa) |
| TERRENO-EXISTENTE | 8 | DASHED | – | terreno natural |
| TERRENO-ACHURADO | 8 | CONTINUOUS | – | cerco / cuneta existente (patrón) |
| EXCAVACION | 8 | HIDDEN | – | límite de excavación |
| RELLENO | 32 | CONTINUOUS | – | relleno / sello |
| AGUA | 150 | DASHED | 25 | nivel de agua |
| AGUA-SIMBOLO | 150 | CONTINUOUS | – | triángulo de nivel de agua |
| AGUA-RELLENO | 150 | CONTINUOUS | – | relleno sólido RGB (205,228,246) |
| FLUJO | 150 | CONTINUOUS | – | flechas de flujo |
| CORTES | 6 (magenta) | CONTINUOUS | 50 | líneas y rótulos de corte |
| PROGRESIVAS | 5 | CONTINUOUS | – | marcas y textos de progresiva |
| GRILLA | 9 | CONTINUOUS | 13 | grilla UTM, líneas interiores de tablas |
| GUITARRA | 8 | CONTINUOUS | – | guitarra de perfiles |
| LINDERO | 6 | PHANTOM | – | lindero |
| CERCO | 14 | CONTINUOUS | 40 | cerco perimétrico |
| ARQ-BASE / ARQ-TEXTO / VIA | 8 | CONTINUOUS | 13 | arquitectura y vecinos de referencia (gris, finos) |
| ISO-CONCRETO-SUP / -LAT1 / -LAT2 | 254 / 253 / 252 | CONTINUOUS | – | caras de isométricos: RGB (232,232,232) / (206,206,206) / (178,178,178) |
| ISO-TAPA | 255 | CONTINUOUS | – | RGB (248,244,230) |
| ISO-ARISTAS | 8 | CONTINUOUS | – | aristas de isométricos |
| ISO-AGUA | 150 | CONTINUOUS | – | RGB (130,190,240) |
| ISO-TERRENO | 94 | CONTINUOUS | – | RGB (214,226,196) |
| ISO-PIEDRA | 34 | CONTINUOUS | – | RGB (196,176,146) |
| ISO-CUNETA | 94 | CONTINUOUS | – | RGB (168,214,168) |
| ISO-CERCO | 14 | CONTINUOUS | – | RGB (226,200,200) |

Las capas con color verdadero (`COLOR_RGB`) lo guardan en la capa y además en cada entidad (`solido()` pone `e.rgb`;
`relleno()` pone `h.rgb` y `set_solid_fill(rgb=...)`): así se ve igual en AutoCAD, en el celular y en la vista previa.

### 4.2 Capas propias de otros generadores
- Perfiles de cunetas (`barranquita/perfiles_b.py`): PERF-NCT 5 (azul, 35), PERF-TAPA 3 (verde, 35), PERF-FONDO 6 (magenta, 35),
  PERF-SECCION 1 (rojo, 25), PERF-REF 9 (13→9), PERF-CAJA 7; SEC-ABIERTA 5, SEC-TAPADA 3, SEC-ACERO 6 (magenta, 50),
  SEC-ACERO-LONG 5, SEC-REJILLA 1, SEC-PISO 8, SEC-JUNTA 8 (RGB 70,70,70), SEC-HUECO 7 (RGB blanco, interior de la tapada).
- Planta de cunetas (`barranquita/planta_cunetas_b.py`), color verdadero: CUN-REJ-BORDE celeste (0,170,230), CUN-REJ-PLATINA
  (120,205,240), CUN-TAP-BORDE verde (0,150,0), CUN-FLUJO rojo (230,0,0), CUN-TAPA-INSP azul (0,0,230).
- Planta general Barranquita (`planos_b.CAPAS_EXTRA`): CURVAS 33 RGB (176,136,96) grosor 13, CURVAS-TXT, ARQ-TECHO 8, ARQ-VEREDA 9,
  CUNETA-S1 5 / S2 6 / S3 94 / S4 30 (color por sistema), LIMITE-INTERV 1 DASHED grosor 70, DESCARGA 1, CUNETA-GRADAS 1,
  NUDOS 7, POZA 8, MURO-CONT 6.
- Detalle de descargas (`descargas_b.py`): DET-MURO 250 (215,215,215), DET-LOSA 8, DET-REJILLA 1, DET-CERCO 1 (225,120,120),
  DET-CURVAS 33 DASHED, DET-AGUA 150, DET-NCT 5, DET-TAPA 3, DET-FONDO 6, DET-TERRENO 32 DASHED, DET-PERFILADO 1 DASHED,
  DET-CIMIENTO 8, DET-SECCION 1; isométrico ISOD-PISO (243,240,232), ISOD-TERRENO (214,226,196), ISOD-SUP (236,236,236),
  ISOD-INT (196,196,196), ISOD-FONDO (176,176,176), ISOD-LOSA (150,150,150), ISOD-REJILLA 1, ISOD-CERCO (232,190,190),
  ISOD-AGUA (130,190,240), ISOD-HUECO (60,60,60), ISOD-ARISTA 8.
- DP-06B en mm (`dxf_tapa_ciega.py`): LAMINA 7/50, MEMBRETE 7/25, CONCRETO 8/50, CONCRETO_ACHURADO 253, TAPA 8/50, ACERO 1/40,
  ACERO_LISO 30/40 (asas de fierro liso, naranja), OCULTO 8 DASHED, ACERO_OCULTO 1 DASHED, EJES 1 CENTER, COTAS 94/18,
  TEXTO 7/25, TITULOS 160/50, NOTAS_LLAMADA 30/25, CORTE 1/35. Rellenos: concreto de losa color 254, tapa 253.
- Ubicación de lloraderos (`planos_ubicacion_lloraderos.py`): ARQ-FONDO 253 (9), CUNETAS-RED 5 (18), AREA-VERDE 3 (9, sólido),
  LLORAD-TRAMO 1 (70), LLORAD-SIMB 1, LLORAD-TEXTO 1, EJE-TEXTO 5.
- DP-06D (`dxf_tapa_3d.py`): ISO-3D, ISO-3D-ARISTAS 250, PANEL 5, PANEL-FONDO 5, LLAMADAS-NUM 30; colores: concreto
  (196,194,188), tapa (176,174,168), acero (138,88,58), liso (128,124,118).

### 4.3 Convención de colores del usuario (sus propios planos de cunetas, CAR Varones)
Leída del DXF de perfiles del usuario (04-10) y reproducida en los perfiles de Barranquita:
- Azul (ACI 5) = cuneta tramo abierto (borde NCT); verde (ACI 84 en su DXF; 3 en los nuestros) = tramo cerrado/tapado (caras de la losa);
  magenta (6) = losa de fondo (NCF) y también barras de acero transversal en sus secciones; círculos azules = acero de 3/8"
  en cuneta tapada; línea roja vertical = sección.
- En planta (capturas del 21-10): cuneta con rejilla = bordes en celeste con las platinas dibujadas; cuneta tapada = bordes verdes;
  flechas rojas de flujo; tapas de inspección.

### 4.4 Reglas de color
- Sin amarillo (2), sin cian claro (4 como línea fina de texto), sin blanco puro como línea (7 se ve negro en fondo blanco y blanco en
  fondo negro: es el único "blanco" permitido).
- Los textos y puntos sobre rellenos claros van en gris oscuro fijo (RGB 35,35,35 en lloraderos) para leerse con fondo blanco y negro.
- Rellenos de capas nuevas: dar RGB en `B.COLOR_RGB` o usar color 256 (por capa); si no, los HATCH salen negros.
- Referencias (arquitectura, colectores vecinos) en gris y finos; no deben empujar el dibujo fuera de la lámina.

---

## 5. Textos

### 5.1 Altura en papel = altura base × `K_TXT[capa]`
`K_TXT = {TEXTOS 1.35, TEXTOS-NOTAS 1.3, LLAMADAS 1.35, NIVELES 1.3, LEYENDA 1.3, TITULOS 1.35, ROTULO-TEXTO 1.0, PROGRESIVAS 1.25, CORTES 1.3}`.
La altura en el modelo es `hmm × K × f` (m). Ejemplos a 1/50 (f = 0.05): texto de 2.0 mm en TEXTOS → 2.7 mm de papel → 0.135 m de modelo.

| Elemento | Altura base (mm) | En papel (mm) |
|---|---|---|
| Título de vista (`titulo_vista`) | 4.0 (TITULOS) + raya a 3.5 mm debajo | 5.4 |
| Subtítulo de vista | 2.2 (TEXTOS), 7.5 mm debajo | 3.0 |
| Título de leyenda / notas / tabla | 3.0 (TITULOS) | 4.05 |
| Llamadas | 1.8–2.0 (TEXTOS) | 2.4–2.7 |
| Textos de leyenda | 1.7–2.0 (LEYENDA) | 2.2–2.6 |
| Notas | 1.5–2.0 (TEXTOS-NOTAS) | 2.0–2.6 |
| Etiquetas de franja (perfiles) | 1.6–1.7 | 2.2–2.3 |
| Guitarra (valores) | 1.35–1.5 | 1.8–2.0 |
| Cotas (DIMSTYLE) | `dimtxt` 3.0 | 3.0 |
| Código de lámina | 4.0 (TITULOS) | 5.4 |
| DP-06B (mm): títulos | 6 ARIALB + raya lw 70; escala 4 | 6 / 4 |
| DP-06B: textos / llamadas | 2.75–3.5 / 3.0–3.3 (MTEXT) | igual |

Regla del skill: título de vista 4.0–6 mm, textos y llamadas 2.2–3.5 mm, cotas 3.0 mm, notas 2.2–3 mm.
Bloques de leyenda a escala real para pegar en planos del proyectista (`leyenda_cunetas.py`): llamadas 0.031 m y títulos 0.038 m
(las mismas alturas de letra del plano del proyectista), bloque `LEYENDA_ESPEC_CUNETAS` insertado en (0, 0).

### 5.2 Orientación
- Nunca texto vertical (rot = 90) para rótulos de elementos. Solo se acepta vertical en cotas verticales.
- Texto girado solo cuando sigue a un elemento lineal en planta: progresivas a lo largo del eje (DP-01), cota de las curvas de nivel
  en su dirección (con el ángulo llevado a −90..90 para que no quede de cabeza), rótulos S-nn de cortes según el azimut del eje.
- Excepciones que existen en el código (ver §16): guitarra de los perfiles de cunetas de Barranquita (progresiva y etiqueta S-nn
  verticales de 1.0 mm), texto "LINDERO" vertical en el corte de la caja CL (DP-07 del Refugio).

### 5.3 Longitud de líneas
- Llamadas: si una línea pasa de 70 caracteres se parte a 62 (`textwrap.wrap`); máximo 2 o 3 líneas por llamada.
- Notas: el ancho se ajusta solo (`nch = max(30, ancho_mm / (0.80 × hmm × 1.3))`).
- Celdas de tabla: la letra baja de 0.1 en 0.1 mm hasta entrar (`len × 0.78 × h × 1.35 ≤ ancho − 1.5`, mínimo 1.2 mm).
- Ancho estimado de un carácter para cálculos de choque: 0.62–0.72 × altura (Arial).
- Subtítulo del rótulo ≤ ~110 caracteres; "MODERADO" u otras palabras no deben partirse en celdas angostas.

---

## 6. Cotas, niveles, llamadas, flechas y símbolos

### 6.1 DIMSTYLE por escala (`COT-<escala>`, `nuevo_documento`)
Escalas disponibles: `ESCALAS = [10, 15, 20, 25, 50, 100, 175, 200, 250]` (Barranquita agrega 5 antes de crear el documento).
Si la escala de la lámina no está en la lista se usa `COT-25` (texto de cota con tamaño equivocado): agregar la escala antes.

| Variable | Valor | Significado |
|---|---|---|
| dimscale | escala/1000 | todo en mm de papel |
| dimtxt | 3.0 | altura del texto (mm papel) |
| dimasz | 2.2 | tamaño de flecha (no se usa: tic) |
| dimtsz | 1.4 | tic oblicuo (sin bloque de flecha) |
| dimexe / dimexo | 1.6 / 1.2 | extensión más allá de la línea / separación del objeto |
| dimgap | 1.0 | separación texto–línea |
| dimtad / dimtih / dimtoh | 1 / 0 / 0 | texto encima de la línea, alineado |
| dimdec | 2 | dos decimales (metros) |
| dimlfac | 1.0 | mide el dibujo real |
| dimclrd / dimclre / dimclrt | 256 / 256 / 7 | líneas por capa (COTAS, verde 94), texto negro |
| dimtxsty | STANDARD (Arial) | |
| dimpost / dimapost / dimblk(1,2) | "<>" / "" / "" | grupos 3–7 presentes para AutoCAD |
| dimzin / dimdsep | 0 / "." | ceros y punto decimal |

DP-06B en mm: `M_1_10` (dimlfac 0.01), `M_1_5` (0.005), `M_1_2` (0.002, 3 decimales); dimtxt 2.8, dimtsz 1.6, dimtmove 1, colores 94.

### 6.2 Uso de cotas
- `lam.cota(p1, p2, dist_mm, horizontal=True|False, texto=None, angulo=None)`: lineal horizontal o vertical a `dist_mm` de papel del
  lado positivo (negativo = abajo/izquierda); con `angulo` se hace alineada. Siempre `dim.render()`.
- Cotas por fuera del dibujo: abajo las parciales (muro – interior – muro) y la total más abajo (−dist y −2.2·dist); a la derecha las
  verticales (solado/fondo – interior – losa) y la total; líneas de referencia GUITARRA del objeto hasta la línea de cotas.
- Antes de entregar: comparar 3 o 4 cotas del dibujo con la memoria/metrado.
- Vistas ampliadas dentro de una lámina (k = escala_lámina / escala_vista, p. ej. 1/5 en lámina 1/10 → k = 2): la cota mediría k veces;
  ahí se escribe el texto real y la escala de la vista en su título. El usuario se confundió cuando una vista estaba a otra escala
  sin decirlo ("¿por qué mide 0.30 si la cuneta es 0.60?", 21-10): preferir una sola escala por lámina o una presentación propia.

### 6.3 Niveles
`lam.nivel(p, cota, texto=None, lado=1, hmm=2.0)`: bloque `SIMB-NIVEL` (triángulo de 3 x 2.2 mm con raya de 6 mm, escala f) y texto a
3.5 mm al lado y 2.6 mm arriba ("CF 259.100", "NA 259.452", "NPT +260.60 (losa superior = piso terminado)", "tapa CL +261.15").

### 6.4 Llamadas (`lam.llamada`)
Texto en `p_txt`; tramo horizontal de apoyo de 4 mm; línea con punta de flecha (triángulo sólido de 2.2 mm de largo y 0.35·t de
media base, capa LLAMADAS naranja) hasta el objeto; texto a 1 mm del apoyo, elevado 0.3·hmm. Alineación izquierda o derecha
según el lado de la columna. En la DP-06B (mm): círculo de 0.7 mm relleno naranja en el objeto, polilínea al texto con
quiebre de 4 mm y MTEXT (ancho 50–70 mm).

### 6.5 Flechas y símbolos (bloques en `crear_bloques`, en mm de papel, se insertan con escala f)
| Bloque | Geometría | Uso |
|---|---|---|
| SIMB-FLECHA | línea −4..4 mm + triángulo (4,0),(1,±1.2) | sentido del flujo (capa FLUJO); rotación = azimut |
| SIMB-NIVEL | triángulo y raya | nivel |
| SIMB-AGUA | triángulo invertido 2.4 x 1.8 mm + 2 rayas | nivel de agua |
| SIMB-CORTE | triángulo + línea | marca de corte |
| SIMB-NORTE | círculo r 8 mm, flecha, "N" 4 mm | norte (girado al azimut del frente en el Refugio) |
| ACERO-38 | círculo r = 0.00475 m + hatch sólido color 5 | barra 3/8" cortada (insertar con escala 1.0) |
| ACERO-12 | círculo r = 0.00635 m + hatch sólido | barra 1/2" cortada (escala 1.0) |
| REGISTRO-PLANTA | contramarco 0.70, luz 0.60, rayado diagonal de tapa, 2 asas | registro en planta (escala 1.0, girado con el eje) |
| SIMB-CUNETA-LLEGA | ventana 0.40 y cuneta 0.60 | empalme en planta |

Flechas de la planta de cunetas (geometría a escala real, no bloque): planta 1/250 largo 0.70 m, punta 0.30, media punta 0.13,
grosor 0.07; detalle 1/25: 0.40 / 0.14 / 0.06 / 0.025; una flecha cada 5 m y en cada quiebre (tramos ≥ 2 m), una en tramos de 0.4–2 m.
Marca de corte en la DP-06B: polilínea de 0.6 mm de ancho, triángulo rojo, letra ARIALB 5 mm, eje entre los extremos.

---

## 7. Rellenos (hatch) y orden de dibujo

- Concreto cortado: `lam.achurado(pts)` con capa CONCRETO-ACHURADO llama a `relleno()` → HATCH sólido RGB (226,226,226) + contorno
  CONCRETO 250. No se usan patrones para el concreto (desde el 07-10 en adelante).
- Concreto con hueco (sección U cerrada del CAR Mujeres): un solo HATCH con dos caminos: exterior (flags 1) e interior (flags 16).
- Agua: sólido AGUA-RELLENO (205,228,246) + línea AGUA discontinua + símbolo SIMB-AGUA.
- Rellenos al fondo: después de dibujar todo, `msp.set_redraw_order({handle: "1"})` para los HATCH de CONCRETO-ACHURADO y
  AGUA-RELLENO: las líneas y textos quedan siempre encima.
- Patrones (`achurado(..., patron="ANSI31")`, ANSI37 en tecnopor, TERRENO-ACHURADO en cercos): AutoCAD los redibuja a escala 1 sin la
  escala del bloque/lámina (rayas gigantes o rellenos vacíos). Lección del 22-10 (lloraderos del Refugio): dibujar SIN patrones —
  sólidos con color verdadero, grava como piedras de 20–40 mm a tamaño real, punteado de concreto con trazos de 3 mm y triángulos de
  agregado, tierra como grupos de 3 trazos inclinados en tresbolillo (`espec_lloraderos.py`, versión "CAD").
- Barras: círculo + hatch con camino de arco (`add_edge_path().add_arc(c, r, 0, 360)`).
- Isométricos: caras como SOLID (4 vértices en orden 0,1,3,2) o HATCH con color verdadero; aristas en capa aparte.

---

## 8. Reglas para que nada se cruce

### 8.1 Franja de etiquetas (perfiles, plantas largas, isométricos generales)
Algoritmo de `Lamina.franja(items, y0, abajo=True, hmm=1.6, xmin_mm=27, xmax_mm=W-15, max_filas=30)` (y la variante interna de
`perfil_tramo` con límite de 8 filas):
```
items = [(x_punto, y_punto, [lineas], color)]   # se juntan antes, no se dibujan al vuelo
h = hmm*1.35 ; ch = 0.72*h*f (ancho de caracter) ; lh = 1.55*h*f ; fila_h = n_lineas_max*lh + 2.2*f
para cada item ordenado de derecha a izquierda (x descendente):
    w = max(len(linea))*ch + 2*f ; g = 1.5*f
    lado: a la derecha de su linea; a la izquierda solo si se saldria por x_max
    fila = la mas baja (0, 1, 2...) donde:
        - no choca con otro texto de la misma fila (con holgura g)
        - su texto no tapa la linea vertical de una etiqueta puesta en una fila mas alta
        - su propia linea no cruza un texto de una fila mas baja
    si no hay fila libre: la ultima permitida (limite = borde de la lamina - 12 mm)
    dibujar: linea vertical fina LLAMADAS desde el punto (circulito r 0.5-0.6 mm) hasta la fila; texto horizontal al lado
devuelve el borde de la ultima fila (para poner el titulo de la vista encima)
```
- Si dos puntos caen casi en el mismo x, unir sus textos en una sola etiqueta.
- En extremos (cajas, referencias) pocas etiquetas y cortas, o texto suelto junto al objeto (p. ej. LINDERO): un rótulo cuyo punto
  queda bajo el texto de otro no tiene fila libre y sube al borde.

### 8.2 Columna de llamadas (secciones, cajas, detalles)
`columna_llamadas(items, xt, ytop, ybot, hmm, al)`: textos en una columna x = xt, repartidos de ytop a ybot en el mismo orden de
altura que los puntos que señalan; luego se permutan vecinos mientras dos líneas se crucen (prueba de orientación de segmentos,
hasta 4n pasadas). `juntar_llamadas()` ... `volcar_llamadas()`: todas las `llamada()` de una vista se guardan, se agrupan por columna
(x del texto y alineación), se separan al menos `n_lineas × 1.6 × hmm × 1.35 × f + 2.5 f` y se colocan con `columna_llamadas`.
Columna típica: a la derecha de la vista (x = borde + 0.20 m + 30 mm) o a la izquierda (lado vía) con alineación derecha.

### 8.3 Etiquetas junto al punto (plantas con muchos rótulos)
`planos_b.Etiquetas.poner(p, txt, hmm, capa, color, d_mm)`: prueba 8 posiciones alrededor del punto (diagonales, lados, arriba/abajo)
a 1, 2 y 3 veces `d_mm`; toma la primera cuya caja no toca otra ya puesta; si se alejó (k > 1) traza una línea de llamada.

### 8.4 Rótulos sobre un corte (`cortes_b.rotulos`)
Rótulos del mismo punto (a menos de 2.5 mm) se unen; cada rótulo sube desde `y_min` hasta el primer hueco libre (cajas de alto variable);
nunca filas fijas que se llenan y se pisan. No usar `lam.franja` en cortes (manda al borde de la lámina lo que no entra).

### 8.5 Mapas con muchas etiquetas
En lugar de líneas largas a una columna lejana: marcas numeradas (círculo con N.°) junto a cada punto, del lado del eje con más espacio,
y un cuadro con el significado de cada número (planos de riesgos y planta de lloraderos).

### 8.6 Recuadros de sección en perfiles (`perfiles_b._filas_cajas`)
Recuadros de ancho fijo (25 mm) repartidos en 1 a 4 filas (las que hagan falta para que entren), corridos a la derecha si chocan y a la
izquierda si se salen del borde; cada recuadro con flecha hasta su punto NCT.

---

## 9. Tablas, leyendas y notas

- `lam.tabla(xmm, ymm, cabeceras, filas, anchos_mm, hmm=1.8, alto_mm=4.5, titulo=None)`: líneas exteriores y de cabecera en TEXTOS,
  interiores en GRILLA; texto centrado; la letra se ajusta a cada celda; devuelve el y inferior (mm). Columna propia para los nombres
  de fila; no poner dos columnas a menos de 12 mm de papel.
- `lam.leyenda2(xmm, ymm, items, hmm=2.0, titulo="LEYENDA", ancho_col=0, filas_col=99)`: muestras de 14 x 4 mm; tipos `linea`,
  `linea2` (gruesa 0.7 mm), `discontinua`, `rect`, `relleno`, `concreto` (relleno gris + contorno), `punto`, `bloque:NOMBRE`
  (barras a diámetro real con escala 1.0, símbolos con escala f); texto a 17 mm; paso vertical `6.0 × 1.3 × hmm / 2`; varias columnas.
  Devuelve el y final.
- `lam.leyenda(...)`: versión antigua (muestras de 12 mm, paso 5.5 mm), usada en perfiles congelados.
- `lam.notas(xmm, ymm, titulo, lineas, hmm=2.0, ancho_mm=None, legado=False)`: título TITULOS 3.0 con raya de 25 mm; ajuste de línea
  al ancho; si no se da ancho usa hasta el borde derecho (o hasta el rótulo si la nota baja de y = 110 mm); interlineado
  `4.2 × hmm / 1.8` mm. `legado=True` = formato anterior para láminas congeladas (perfiles del Refugio).
- Zonas fijas de la lámina: vistas arriba; leyenda, notas y cuadros abajo a la izquierda y al centro (franja inferior de ~110 mm);
  rótulo abajo a la derecha. Nada encima del rótulo.
- Los cuadros de metrado de las láminas se leen de la planilla del presupuesto (valores guardados), nunca se recalculan; si la
  planilla guarda fórmulas sin valores, recalcular una copia con LibreOffice y leer de ahí.

---

## 10. API de `dxf_base.Lamina`

```python
lam = B.Lamina(doc, ox, oy, esc, codigo, titulo, subtitulo, formato="A1", escala_txt=None)
# atributos: formato, A1 (=(W,H) del papel), W, H, escala_txt ("1/esc" por defecto), ox, oy, esc,
#            f = esc/1000, codigo, titulo, subtitulo, dimstyle ("COT-esc"), doc, msp
# al crearse dibuja marco() y rotulo()
```
| Método | Firma | Qué hace |
|---|---|---|
| P | `P(xmm, ymm) -> (x, y)` | papel (mm desde la esquina de la lámina) → modelo (m) |
| mm | `mm(v)` | mm de papel → m de modelo (`v·f`) |
| linea | `linea(p1, p2, capa, **kw)` | LINE |
| poli | `poli(pts, capa, cerrada=False, ancho=0.0, **kw)` | LWPOLYLINE (ancho constante opcional, en m) |
| rect | `rect(x1, y1, x2, y2, capa, **kw)` | polilínea cerrada |
| circulo | `circulo(c, r, capa)` | CIRCLE |
| solido | `solido(pts4, capa)` | SOLID con RGB de la capa |
| texto | `texto(p, t, hmm=2.5, capa="TEXTOS", al=TA.LEFT, rot=0, estilo="STANDARD", color=None)` | TEXT con altura `hmm·K_TXT·f`; capa TITULOS usa Arial negrita |
| textos | `textos(p, lineas, hmm, capa, al, inter=1.6)` | varias líneas hacia abajo |
| bloque | `bloque(nombre, p, escala=None, rot=0, capa=None)` | INSERT; escala por defecto f (símbolos en mm) |
| cota | `cota(p1, p2, dist_mm, horizontal=True, texto=None, estilo=None, angulo=None)` | DIMENSION lineal/alineada |
| achurado | `achurado(pts, capa="CONCRETO-ACHURADO", patron="ANSI31", escala_mm=1.0)` | concreto → relleno sólido; otras capas → patrón |
| relleno | `relleno(pts, capa)` | HATCH sólido con RGB de la capa |
| flecha | `flecha(p_from, p_to, capa="LLAMADAS", tam_mm=2.2)` | línea con punta |
| llamada | `llamada(p_obj, p_txt, lineas, hmm=2.0, capa="LLAMADAS", al=TA.LEFT)` | llamada con flecha (se guarda si hay `juntar_llamadas`) |
| nivel | `nivel(p, cota, texto=None, lado=1, hmm=2.0)` | símbolo de nivel y texto |
| titulo_vista | `titulo_vista(xmm, ymm, titulo, sub=None, ancho_mm=90)` | título centrado 4.0, raya, subtítulo 2.2 |
| marco / rotulo | – | se llaman en el constructor |
| leyenda / leyenda2 | ver §9 | |
| franja | ver §8.1 | |
| juntar_llamadas / volcar_llamadas / columna_llamadas | ver §8.2 | |
| notas | ver §9 | |
| tabla | ver §9 | |

Funciones del módulo:
- `iso(x, y, z, ex=1.0) -> (u, v)`: `u = x·cos30 − y·cos30`, `v = −x·sin30 − y·sin30 + z·ex` (ver §11.15, espejo).
- `caja_iso(lam, x0, y0, z0, dx, dy, dz, capas=(SUP, LAT1, LAT2), ex, origen, esc, aristas=True, solido=True)`: prisma con sus
  3 caras visibles (superior, frontal en y0+dy, lateral derecha en x0+dx), pintadas lateral → frontal → superior; devuelve la función T.
- Otras utilidades: `dxf_planta.offset_poli(pts, d)` (paralela con bisectriz en los vértices), `recortar(pts, ventana)`
  (Liang–Barsky, recorta la arquitectura de fondo a la ventana de dibujo), `prog_txt(p)` → "0+012.34".
- `planos_b.EnBloque(lam, nombre, capa)`: context manager que redirige `lam.msp` a un bloque nuevo (geometría en coordenadas reales)
  y lo inserta en (0, 0) al salir.

---

## 11. Cómo se arma cada tipo de vista

### 11.1 Planta del colector (DP-01; `dxf_planta.dp01`, `varones/planos_v.dp01`, `mujeres/planos_m.dp01`) — 1/200, A1
1. Arquitectura de fondo recortada a una ventana alrededor del frente (capas ARQ-BASE, textos filtrados por palabras clave:
   ESTACIONAMIENTO, INGRESO, VIGILANCIA, SS.HH, OE-, OC-, VEREDA, PTAR, PATIO), lindero (PHANTOM) y cerco resaltado (0.08 m de ancho).
2. Colector: eje (CENTER) por los vértices reales (recta, quiebres a 45°, brink, fin); muros exteriores (`offset_poli(±b_ext/2)`,
   ancho 0.04) y caras interiores ocultas; en el CAR Mujeres además relleno gris de la losa.
3. Cajas CL (llegada) y CC (caída con poza): contornos y poza.
4. Registros con el bloque REGISTRO-PLANTA girado con el eje; los registros van exactamente donde entrega cada cuneta (corrección del
   04-10 en Varones: las tapas estaban corridas de las cajas de llegada) y fuera de los cruces vehiculares.
5. Juntas cada 4.00 m (línea transversal JUNTAS que sobresale 0.15 m), cruces vehiculares (polígono CRUCE-VEHICULAR).
6. Cunetas que llegan: dos líneas de 0.60 (CUNETA) y dos ocultas de 0.40, perpendiculares al cerco hasta el muro del colector; flecha.
   Las cunetas son las que llegan perpendiculares (no la línea verde fuerte de otra capa: corrección del 04-10).
7. Progresivas cada 10 m y en puntos singulares (marca de 0.9 m y texto girado con el eje); flechas de flujo.
8. Etiquetas en franja inferior (`franja(..., abajo=True)`): registros no asociados a cuneta, cruces, cunetas (eje, perfil, 0.40 x H,
   NCF, registro, prolongación), cajas, cerco, carretera, colector.
9. Grilla UTM (cruces de 3 m cada 25 m con "E ..." y "N ..."), norte girado, cuadro de coordenadas de registros y cajas (PUNTO,
   PROGRESIVA, ESTE, NORTE, COTA FONDO, COTA TAPA, OBSERVACIÓN) con nota de georreferencia.
10. Leyenda (2 columnas) y notas (materiales, ubicación respecto al cerco, progresivas, registros, cotas, cajas, láminas relacionadas).
- CAR Varones: sin cerco en el frente (corrección del 04-10: "no hay cerco perimétrico en Varones"); textos de caudal, piso (+261.15),
  número de registros (11) y juntas (26) parametrizados en `compat.py`.

### 11.2 Planta de cunetas (Barranquita DC-01; `planos_b.dc01`, `planta_cunetas_b.py`) — 1/250, A1, coordenadas UTM reales
- Bloques de AutoCAD por tema: `ARQUITECTURA_BASE` (veredas, proyección de techos, muros, cerco, muro de contención),
  `CURVAS_DE_NIVEL` (cada 0.50 m; cota en las de metro entero, dos veces por curva, girada con la curva),
  `LIMITE_DE_INTERVENCION` (cerco confirmado, polilínea DASHED de 0.35 m), `CUNETAS_SISTEMA_n` (uno por sector/sistema),
  `ROTULOS_RED` (nudos, códigos de eje, descargas, gradas).
- Cuneta a escala real: contorno exterior (media anchura 0.30) e interior (0.20) de todos los ejes de un sistema unidos con shapely
  (`buffer` con extremos planos `cap_style=2`, esquinas en inglete `join_style=2`, `mitre_limit=5`) para que los empalmes queden limpios;
  el interior arranca 0.10 m (muro de cabecera) en los ejes que nacen en un cabezal.
- Cada tramo del contorno toma el estado del eje más cercano: rejilla → celeste (CUN-REJ-BORDE); tapado → verde (CUN-TAP-BORDE);
  el estado puede cambiar dentro de un lado largo (se evalúa cada 0.25 m).
- Platinas de la rejilla: líneas transversales de 0.40 m cada 0.10 m solo en tramos abiertos; el eje que llega no las repite dentro de la
  cuneta que lo recibe.
- Tapas de inspección 0.60 x 0.60 (azul, polilínea 0.03 m con 2 asas a ±0.17 m) en tramos tapados: al inicio y al final, en cada empalme
  dentro del tramo tapado y a 10 m como máximo (criterio propuesto; el usuario no fijó distancia). Lista en `_calc/tapas.json`.
- Eje que termina en descarga se prolonga 0.075 m hasta la cara exterior del cerco. Descarga: polilínea de 4 m (0.25 de ancho) con
  flecha y rótulo "D1"... (TITULOS, rojo).
- Gradas (tramos con V > 3 m/s): rayas transversales de 0.56 m y 0.12 de ancho cada 0.50 m.
- Rótulos: código del eje junto a su tramo más largo, color del sistema; nombre de nudos (los quiebres a 45° "~" no se rotulan, salvo
  que sean empalme); todo con `Etiquetas` (8 posiciones).
- Leyenda (6 filas por columna), cuadro de DESCARGAS (C.F., ubicación, salida por gravedad) y notas de criterios (sección, niveles
  NPT +184.65 / área verde +184.60 / patio +184.50, techos a dos aguas, tapas, todo dentro del cerco, bloques).
- Quiebres a 45°: en cada esquina con giro > 50° se corta un chaflán de 0.60 m por lado (máximo la mitad del tramo vecino); los ejes
  que llegan a una esquina entran en diagonal (unión en Y). Solo en planta.

### 11.3 Planta de ubicación de lloraderos (DL-00; `planos_ubicacion_lloraderos.py`) — 1/250, A1
Arquitectura en gris (ARQ-FONDO 253, sin cotas, textos ni bloques de mobiliario), red de cunetas en azul, áreas verdes en verde sólido,
tramos de muro colindantes con área verde (rojo, grosor 0.70) numerados igual que la hoja METRADO LLORADEROS, cada lloradero en su
posición (@1.50 m repartidos en el tramo), cuadro de tramos, leyenda, notas y detalle típico 1/10 (bloque escalado k = 250/10).
Lado del muro por tabla LADO (Refugio) o por el rumbo de la hoja comparado con la normal al eje (Varones, norte arriba).

### 11.4 Perfil longitudinal del colector (`dxf_planta.perfil_tramo`, `varones/planos_v.perfil`, `mujeres/planos_m.perfil`)
Escala real H = V (1/50 Refugio; 1/100 general y 1/25 detalle en Varones y CAR Mujeres). Corte por el eje mirando el muro lejano.
Elementos, de abajo hacia arriba:
1. Agua: relleno AGUA-RELLENO entre fondo y NA del perfil hidráulico + línea AGUA + SIMB-AGUA cada 10 m. El canal (fondo, solado
   y agua) termina en el brink (caída libre a la caja CC): el agua no se mete "por debajo" de nada (corrección del 03-10).
2. Losa de fondo cortada (concreto gris, espesor real e_fondo) y solado (e = 0.05) con línea de excavación 0.02 debajo.
3. Losa superior cortada con los huecos de los registros (abertura 0.70 = prog ± 0.35); en el cruce de camiones el escalón de
   espesor (0.25).
4. NPT / piso terminado como línea gruesa (TERRENO, 0.35 mm) en la cara superior de la losa.
5. Registros: borde engrosado 0.15 x 0.10 a cada lado (0.35–0.50 del eje), tapa 0.68 x 0.08 (REGISTRO-TAPA).
6. Cunetas que llegan: ventana 0.40 x H en el muro lejano (relleno claro ISO-CUNETA), raya de NCF, flecha de caída.
7. Juntas cada 4.00 m (en losa superior y de fondo) con letra "J" de 1.3 mm.
8. Cruces vehiculares: línea naranja 2 mm sobre el NPT con topes y texto ("CRUCE DE CAMIONES: losa e=0.25, doble marco 1/2\"").
9. Cajas CL y CC con su poza, murete del escalón (e = 0.15, corrección del 03-10), umbral, ventanas, tapas, agua (caída libre, resalto
   ahogado), niveles y cotas ("caida 0.28", "0.55"); colectores vecinos como referencia gris (ARQ-BASE).
10. Cotas de altura interior "h=1.43" en 2 puntos del tramo (evitando registros y cunetas), niveles CF/NA en los extremos, NPT,
    texto "S = 0.30 %", terreno existente (DASHED).
11. Acero en el perfil de detalle (CAR Mujeres): barras longitudinales como líneas ACERO-LONG y marcos vistos en el corte como puntos a
    diámetro real cada `sep` (doble capa en cruce de camiones).
12. Escala vertical de cotas a la izquierda (cada 0.5 m en general; cada 0.1 m en detalle con texto cada 0.2 m).
13. Etiquetas en franja superior (registros "R-03 0+024.00", cunetas "CUNETA EJE 02 - NCF 259.85 / ventana 0.40 x 0.75", cajas,
    colectores vecinos, LINDERO), título de la franja encima.
14. Guitarra debajo: columna propia de nombres (36 mm a la izquierda, separada por línea vertical) y valores centrados.
    - Refugio: PROGRESIVA, TERRENO, LOSA SUP. / NPT, FONDO, NIVEL AGUA, ALTURA h, PROF. EXCAV.; filas de 6 mm; texto 1.4.
    - CAR Mujeres: PROGRESIVA, TERRENO NATURAL, CARA SUP. DE LOSA, COTA DE FONDO, NIVEL DE AGUA, ALTURA INTERIOR h y, en detalle,
      PROF. EXCAVACIÓN; filas de 6.0 (detalle) o 5.2 mm; nombres en 44 mm.
    - Estaciones: extremos, registros, cambios de zona y cada 5 m; se omite la que cae a menos de `sep` (0.75 m detalle, 2.6 m general;
      el registro manda sobre la estación regular).
- Si la losa mide menos de 3 mm en papel, subir la escala (1/25) y partir en más tramos (lección del CAR Mujeres: el general a 1/250 no
  se leía y el detalle a 1/50 tenía la losa de 2 mm → 1/100 y 1/25).
- Perfiles del Refugio (DP-02 en 2 franjas 0–36 m y 36 m–fin; DP-03A/B por tramos de 20 m, ambos 1/50): congelados por pedido del
  usuario (07-10); sus notas usan `legado=True`.

### 11.5 Perfil longitudinal de cunetas con el estilo del usuario (`barranquita/perfiles_b.py`) — 1/50 H = V, A1
Pedido del 21-10: "así quiero los perfiles tal cual, estilo de línea, colores, separación, arriba sección; dividir por ejes".
- Un perfil por eje (EJE-01 ... EJE-19). Ejes largos se parten en piezas iguales que entren en una franja de 800 mm útiles
  (`ANCHO_LAM`); piezas cortas se juntan en la misma franja; las franjas se apilan de arriba abajo y la lámina se corta cuando la
  siguiente no entra sobre los 112 mm inferiores (leyenda a la izquierda, rótulo a la derecha).
- Líneas: NCT azul (tramo abierto) y verde (tramo tapado: cara superior y cara inferior de la losa, 0.10 m); NCF magenta (cara superior
  e inferior de la losa de fondo, EL = 0.10); línea roja vertical en cada sección del NCT a la cara inferior de la losa de fondo.
- Referencias "Altura relativa al NPT (m)" cada 0.15 m (0.00 = NPT +184.65), con su valor (1.15 mm) a la izquierda.
- Grilla cada 5 m con progresiva "0+05" arriba de la guitarra; la final con su valor "0+35.59".
- Recuadro sobre cada sección (25 mm de ancho, paso de filas 34 mm): título "SECCION nn" (1.8 TITULOS, raya de 22 mm) y líneas
  `NCT: 184.65`, `NCF: 184.35`, ` H: 0.30 m`, ` EL: 0.10 m`, ` EM: 0.10 m` (1.45 mm) más los avisos de conexión, cada uno en su
  línea (1.15 mm): "Inicio del eje", "Llega EJE-xx", "Entrega a EJE-yy; caida 0.42 m", "Descarga D1", "Inicio de tapado",
  "Fin de tapado", "Cambio de borde". Flecha del recuadro al punto NCT.
- Guitarra (filas de 6.5 mm, encabezados en columna de 34 mm): `Progresiva (m)`, `Etiqueta`, `Longitud (m)`, `Pendiente (%)`.
  Progresiva y etiqueta S-nn en cada sección; longitud y pendiente entre secciones consecutivas, siempre la medida completa de sección a
  sección aunque el tramo siga en otra pieza (corrección del 21-10: salía 31.45 en vez de 35.59 de S-07 a S-08 del EJE-04); si el tramo
  está cortado y hay más de 40 mm se agrega "(S-07 a S-08)"; si hay menos de 7 mm no se escribe.
- Secciones (numeración correlativa en el orden de los ejes): inicio y fin de cada eje, nudos con llegada, quiebres solo si cambia la
  pendiente del fondo, inicio y fin de tapado, cambio de borde (patio de maniobra); se juntan las que distan menos de 0.25 m. Los quiebres
  a 45° ("~") no generan sección ni se dibujan en el perfil.
- Título: "PERFIL LONGITUDINAL EJE-04 - <descripción sin coordenadas> - PROG. 0+000.00 A 0+035.59" (sin "bloque X", conservando
  "pabellón"; corrección del 21-10).
- Leyenda del perfil: 5 ítems (borde abierto, tapado, cota de fondo, sección, altura relativa al NPT).

### 11.6 Secciones transversales del colector (`dxf_secciones.seccion`, `mujeres/planos_m.seccion`)
Mirando aguas abajo: izquierda = lado vía (lindero), derecha = lado predio (cerco). Origen en el fondo del solado en el eje.
1. Solado (0.05 más ancho a cada lado; en CAR Mujeres al ancho exterior, como el metrado) y concreto en una pieza (U + losa
   superior monolítica) con relleno gris; interior hueco.
2. Acero transversal (rojo): tramo normal y cruce de motos un solo marco cerrado en el eje de muros y losas; cruce de camiones doble
   marco (exterior e interior, recubrimiento 0.04); ganchos a 135° en la esquina superior del lado vía (CAR Mujeres, `g = 6d + 0.03`);
   marcos dibujados con polilínea de ancho = diámetro real.
3. Acero longitudinal: círculos rellenos azules a diámetro real (bloques ACERO-38 / ACERO-12, escala 1.0) repartidos sobre el marco
   a la separación del diseño (0.25 normal, 0.20 camiones), por dentro del marco.
4. Agua: línea y relleno al NA de diseño con el caudal de ESE tramo ("NA 259.452 (Q=560.6 L/s)"; corrección del CAR Mujeres: antes
   todas decían 823 L/s).
5. Nivel terminado a ambos lados (vereda o terreno natural), terreno existente lado vía, límite de excavación (0.05 a cada lado en
   CAR Mujeres, 0.25 en Refugio), cerco con su cimiento y junta de tecnopor (si el proyecto tiene cerco; Varones no), suelo contra el
   muro con trazos inclinados.
6. Cotas por fuera: abajo muro/interior/muro y total; a la derecha losa de fondo/altura/losa superior y total.
7. Niveles: CF en el fondo, NPT en la losa. Textos "LADO VIA (LINDERO)" y "LADO PREDIO".
8. Llamadas en columna, ordenadas como los puntos (losa superior, terreno, acero transversal, acero longitudinal, muro, NA, losa de fondo,
   solado).
- Láminas: DP-04A/B 1/15, 2 x 2 secciones por lámina (Refugio: centros x 215 / 615 mm, y 405 / 178 mm) con `titulo_vista`
  "SECCION S-03" y subtítulo "PROG. 0+020.00 - CF 259.040 - TRAMO NORMAL - ESC. 1/15"; CAR Mujeres 9 + 6 secciones y cuadro.
  DP-06A secciones típicas 1/10 (tramo normal, motos, camiones; Mujeres además tramo final), sin contexto (`contexto=False`).
- Regla de escala: secciones 1/15 (2 x 2) o 1/20 (3 por lámina); nunca 4 en fila a 1/25 si quedan chicas. Si una vista ocupa menos de un
  tercio de su espacio, subir la escala.

### 11.7 Secciones de cunetas (`perfiles_b.corte` 1/20; `planos_b.seccion` 1/5 en DC-02)
- Corte de cada sección de los perfiles en una grilla de celdas de 116 mm (6 por fila en A1), filas de alto `(h_max + 0.62)/f + 22` mm.
- Abierta: U de concreto (muros 0.10, losa de fondo 0.10, interior 0.40) + ángulos 1" del marco y rejilla de platinas 1" x 3/16"
  (0.0254 x 0.0048) a ras del borde. Tapada: rectángulo con hueco y losa tapa de 0.10 (altura libre ≥ 0.25 m bajo la losa).
- Piso adyacente con junta asfáltica de 1" al mismo nivel que el borde de la cuneta (perfil de piso 0.34 x 0.10 con talón a 0.24).
- Acero solo si h ≥ 0.40 m (de la rejilla al fondo) o si es tapada: marco 3/8" @0.25 (abierta: marco en U con ganchos arriba; tapada:
  marco cerrado), longitudinales 3/8" @0.20 (rejilla) o @0.22 (tapada); si h < 0.40: llamada "CONCRETO SIMPLE / SIN ACERO (h < 0.40)".
  Regla del usuario (04-10 y 21-10): "el acero se considera a partir de 40... si hay cunetas de 30, de 36, no llevan acero, salvo si son
  tapadas".
- Cotas por fuera (abajo 0.10 / 0.40 / 0.10 y total 0.60; derecha EL y H, y losa en la tapada), llamadas a ambos lados (longitudinal
  izquierda, transversal derecha, junta asfáltica, rejilla), título "SECCION nn" 3.0 con raya, subtítulos "EJE-04 - PROG. 0+012.30 -
  CON REJILLA" y "NCT 184.65 - NCF 184.29 - H 0.36 m - ESC. 1/20".
- Notas de la lámina: concreto f'c 175, acero solo con h ≥ 0.40 y tapados, rejilla, junta, niveles (NPT y borde +184.65, área verde
  +184.60, patio +184.50).

### 11.8 Cajas de llegada y de caída (DP-07; `dxf_cajas_iso.dp07`) — 1/25
- CL-1 planta (losa superior retirada): caja interior 1.50 x 1.00 + murete de 0.15 en el escalón, ventana de llegada del colector vecino
  (0.60) en el muro este, ventana norte 0.40 de la cuneta que entra a la caja, cuneta propia que entra al colector, registro, eje,
  lindero con su x, cotas parciales, llamadas en columna (`juntar_llamadas`).
- CL-2 corte longitudinal por el eje: contorno exterior e interior escalonados, solado escalonado, rellenos, tapa, ventana del muro norte,
  colector vecino como referencia, agua (caída libre y colchón), acero 3/8" @0.20 en ambas caras interrumpido en las ventanas (el acero
  no debe salir del muro: corrección del 03-10), puntos de acero perpendicular, niveles y cotas ("caida 0.29", "ventana 1.17", "0.55").
- CC-1 / CC-2 caja de caída: poza 1.50 x 3.50, brink, umbral 0.25 x 0.40, ventana de salida 1.50 x 0.43 (alto interior del receptor),
  registros, receptor como referencia, agua (chorro, resalto ahogado, NA receptor).
- Cuadro de materiales de las cajas y leyenda; notas.
- CAR Varones DP-07 (1/20): empalme con la caja CL vista en planta, corte y corte transversal.
- CAR Mujeres DP-07 (1/15): estructura de salida con dos aleros y emboquillado (piedras dibujadas como círculos ISO-PIEDRA).

### 11.9 Registro de limpieza y tapa ciega (DP-06B rev. 02; `render_tapa/dxf_tapa_ciega.py`)
Lámina A1 en mm de papel; cada vista con la clase `Vista(ox, oy, esc)` (k = 1000/esc mm por m) y su DIMSTYLE con `dimlfac`.
`python3 herramientas/render_tapa/dxf_tapa_ciega.py <salida.dxf> <refugio|varones|mujeres>` (b = 0.80 / 0.60 / 1.50; muros 0.15 / 0.15 / 0.10;
10 / 11 / 15 registros).
- A. Planta del registro 1/10 (colector b, muros e). B. Corte A-A transversal 1/10 (con muros y "INTERIOR DEL COLECTOR").
  D. Detalle 1: asiento de la tapa 1/2 (corte B-B). E. Tapa: planta de armado 1/5. G. Detalle del asa 1/2 (fierro liso 1/2" A36).
  H. Isométrico tapa y asiento (sin escala, tapa elevada 0.42 para mostrar el montaje, llamadas a la derecha).
  I. Materiales por registro (tabla). J. Notas y proceso constructivo. Leyenda de 4 muestras (concreto de losa 254, tapa 253, acero
  corrugado 1, fierro liso 30).
- Geometría: tapa 0.68 x 0.68 x 0.08 con bisel 1 x 1 cm, parrilla 3/8" @0.10 (7 + 7 barras de 0.62), 2 asas de fierro liso 1/2"
  (agarre 0.15, patas 0.02, ganchos 0.15; desarrollo 0.49 → 0.50) en cajuelas 0.19 x 0.06 x 0.03 a ±0.20 del centro; rebaje de concreto
  0.70 x 0.70 x 0.08 en la losa (asiento 0.05 por lado, holgura 1 cm), luz libre 0.60 x 0.60, borde engrosado 0.15 x 0.10 (de 0.30 a 0.45
  del eje), refuerzo de borde 8 Ø 1/2" L = 1.40 (2 por lado). Peso de la tapa ≈ 89 kg (0.68² x 0.08 x 2400).
- Colector más angosto que la luz (Varones b = 0.60): en los lados largos el rebaje queda sobre la cabeza de los muros; borde engrosado
  solo en los 2 lados transversales (2 x 0.60 = 1.20 m por registro); barras de borde con ganchos dentro de los muros.
- Barras en sección: círculo con radio `max(d/2·k, 0.55 mm)` relleno.
- Inserción en el juego en metros (`dxf_secciones.dp06b`): se genera la lámina suelta, se explotan las DIMENSION, se excluye marco y
  membrete (capas LAMINA/MEMBRETE y entidades con inserción x ≥ 588 e y ≤ 92), se importa con `ezdxf.addons.Importer` y se transforma
  con `translate(−15, −12) · scale(0.984) · translate(27, 12) · scale(f) · translate(ox, oy)` dentro de una lámina `B.Lamina` de 1/10.
- DP-06D (`render_tapa/dxf_tapa_3d.py`, 1/10, vistas 3 y 4 al doble 1/5): 4 isométricos en color del registro (armado, despiece, corte
  por el registro, armado interior de la tapa) con globos numerados, panel de fondo, cuadro de componentes y datos clave; misma
  geometría que `modelo.py` (variables de entorno COLECTOR_B, MURO_E, N_REG, PROY_DP06D).
- DD-01 (rebaje de asiento y refuerzo de borde) y DD-02 (tapa ciega: fabricación y colocación) en `dxf_detalles.py` a 1/10 con vistas
  1/5, 1/2 y 1/1 (k = 2, 5, 10), despiece, procedimiento y cuadro de componentes por unidad para el ACU.
- Renders fotográficos (PNG) del registro instalado: `render_tapa/render.py`, `iso.py`, `foto.py` (pyvista con texturas, luces y
  SSAO; pedido del 07-10 "una foto realista tipo fotografía").
- Un cambio de detalle (tapa) obliga a revisar todas las láminas donde aparece: DP-06B, DP-06D, DD-01, DD-02, DP-08, DP-09 (isométrico del
  registro), DA-03, DP-01 (nota) y las leyendas.

### 11.10 Juntas (DD-03; DJ-01 a DJ-03)
- DD-03 (`dxf_detalles.dd03`, 1/10): A. sección del colector en la junta (tecnopor en toda la sección, sellador en caras interiores y
  superior; perímetro calculado); B. detalle de la junta 1/2 (1" = 25 mm, sellador asfáltico 1" x 2" RC-250 + arena, barras cortadas a
  5 cm de la junta); C/D junta longitudinal contra el cerco o con la caja CL según el proyecto (`MODO_DD03 = "cerco"` Refugio,
  `"caja_cl"` Varones). Corrección del 15-10: el colector del Refugio solo tiene junta longitudinal del lado del cerco (al otro lado hay
  terreno natural): se agregó la vista D y se borró el esquema antiguo.
- DJ-01 (`planos_junta_cunetas.py`, 1/10): junta de cunetas en toda la sección en U (2 muros + losa de fondo), EG-2013 MTC Sección 510;
  longitud por junta = 2 x H + 0.40.
- DJ-02 (`planos_junta_cunetas_iso.py`, 1/10): proceso constructivo en 4 isométricos 3D (vaciado paño 1; plancha de tecnopor en U;
  acero y vaciado paño 2; sellador y rejilla, con corte parcial del muro cercano).
- DJ-03: rejilla móvil (módulo de 1.00 m, platinas 1" x 3/16" de canto @1", 2 ángulos L 1" x 1" x 3/16", rebaje 0.05 x 1") con
  isométricos, planta, sección, corte y despiece.

### 11.11 Empalme de cuneta al colector (DP-06C; DD-04)
- E1 planta 1/10 (losa retirada): colector, ventana 0.40 x H en el muro lado predio, cuneta 0.40 / 0.60, junta de 1", cerco con su
  abertura 0.60 (si hay cerco), registro encima, flechas, cotas (0.40, 0.60, 0.70), llamadas a la derecha.
- E2 corte transversal mirando aguas abajo: muro con ventana, cuneta que llega con su NCF y vierte en caída libre, NA del colector
  bajo el fondo de la cuneta, junta, niveles.
- Cuadro de empalmes (cuneta, progresiva, NCF que llega, H de ventana, registro) y notas de prolongación/acortamiento.
- DD-04: empalme como detalle constructivo (sin partida propia: la cuneta se metra hasta el muro del colector).

### 11.12 Lloraderos (DL-01, DL-02; `techo/planos_lloraderos.py`; leyenda `espec_lloraderos.py`)
- DL-01 (1/10): isométrico de un tramo de cuneta con tres lloraderos @1.50 m en las tres etapas de instalación y elevación del muro desde
  el área verde. DL-02 (1/5): corte transversal, tubo PVC Ø 3" perforado (Ø 3/8"), isométrico explosionado, procedimiento y desagregado
  de materiales (tubo 0.30 m, filtro de grava 0.30 x 0.30 x 0.30 = 0.027 m3, geotextil 6 caras + 10 %, mortero 0.0005 m3), S = 0.5 %.
- Versión CAD sin patrones (Refugio, 22-10) y dos presentaciones A3 a 1:10 (ESPECIFICACIONES y DETALLE LLORADERO).

### 11.13 Red de techo, sumidero y bancas
- DR-01 a DR-06 (`techo/planos_techo.py`): canaleta (sección 0.25 x 0.20 de los techos principales), soporte de platina, tapa lateral,
  boquilla, montante con codos, colgadores, abrazaderas, falsa columna (0.20 x 0.15 x 1.30) y dado (0.40 x 0.40 x 0.35); isométricos con
  todas las fijaciones del ACU (pedido del 09-10: "detalles hasta de los pernos según tu ACU").
- DS-01/DS-02 (`techo/planos_sumidero.py`, 1/5): caja sumidero de piso con rejilla 0.25 x 0.25 de platinas, marco de ángulo, anclajes,
  salida PVC 4" con un solo codo de 90° hacia la cuneta, sin trampa ni sifón (pedido del 10-10); isométricos opacos.
- DB-01 a DB-03 banca del CAR Mujeres (`techo/planos_banca_m.py`): isométrico 1/15, extremo de la canaleta 1/5, cortes A-A y B-B 1/10.
  Lecciones del 19-10: ser fiel al dibujo (el colgador no salía en el isométrico), faltaban los cortes frontales, solo 2 soportes por canaleta
  de 2.00 m (no muchos), un solo tramo sin uniones, canaleta 0.18 x 0.20 de aluzinc e = 0.50 mm; diferencias del plano de origen se informan.
- DPL-41/DPL-42 OC-01 del Refugio (`techo/planos_oc01_refugio.py`): isométrico general 1/30 + planta de techos 1/50; salida 1/5 y corte de
  canaleta 0.18 x 0.21 (cúpula reemplazada por boquilla a pedido).

### 11.14 Cuadros y partidas (DP-08, DA-01 a DA-03; `dxf_cuadros.py`)
- DP-08 (1/25; CAR Mujeres 1/20 A2): cuadro de doblado de acero (elemento, forma, diámetro, espaciamiento, longitud, longitud total, peso),
  resumen, figuras de marcos (ESC. 1/15 dentro de la lámina 1/25, k = 25/15, cotas con texto real), especificaciones técnicas en notas,
  grosores de impresión, cuadro hidráulico.
- DA-01 (zanja típica por zona y resumen), DA-02 (solado, concreto y encofrado por metro lineal), DA-03 (acero, registros, juntas) a 1/20,
  con secciones reutilizadas de `dxf_secciones.seccion`. En CAR Varones DP-08 y DA-01..03 se excluyeron del juego final.

### 11.15 Isométricos
- Proyección: `dxf_base.iso(x, y, z)` → `u = (x − y)·cos30`, `v = z − (x + y)·sin30`; `iso3d.proy` es la misma. El observador "mira desde
  (+x, +y, +z)" (la esquina más baja en el papel es la más cercana) y la profundidad de pintado es x + y + z.
- Error de espejo (hallado el 20-10 en Barranquita): con esa fórmula +x va a la derecha, pero un observador real en (+x, +y, +z) vería +x a
  la izquierda: la planta sale invertida. Corrección para isométricos de planta con orientación real: intercambiar ejes al entrar
  `(x, y, z) → (v, u, z)` (`iso_b.Vista.L`). Comprobar SIEMPRE con una rosa N/E dibujada con la misma transformación (mirando desde el sur,
  el este va a la derecha). Las láminas de otros proyectos no se tocaron.
- Vistas giradas: `Vista(giro)` rota la planta (u = dx·cos − dy·sin, v = dx·sin + dy·cos) antes de proyectar; con bloques a 0° y 45° girar
  22.5° (si no, unos quedan de canto); CAR Mujeres DP-09 iso 4 girado −28° con caras ordenadas por profundidad.
- `caja_iso`: tres caras visibles con 3 tonos de gris (superior claro 232, frontal 206, lateral 178) y aristas.
- `iso3d.Escena` (`techo/iso3d.py`): caras planas 3D teseladas cada `paso` (0.05 m) para que el algoritmo del pintor no falle;
  orden por (grupo, suma de coordenadas + sesgo); sombreado por la normal `k = 0.58 + 0.42·max(0, n·LUZ)` con LUZ (0.35, 0.55, 0.76);
  aristas solo en bordes reales; primitivas `caja`, `quad`, `cilindro` (con anillos de rosca), `codo` de 90° con campanas, `prisma_hex`
  (pernos), `disco`. `iso_b.dibujar` = mismo pintor pero cada cara en su capa (4.º elemento del color).
- Isométrico de sección (DP-05, 1/20): tramo de 1.00 m cortado; cara interior del muro lejano visible, agua, tapa 0.68 sobre la losa, marco y
  puntos de acero en la cara de corte; llamadas en columna; título "ISOMETRICO S-03".
- DP-09 isométricos constructivos (colector junto al cerco con junta y terreno; registro explotado con rebaje y tapa elevada; empalme de
  cuneta con la ventana; caja de caída con poza y losa cortada); llamadas con `juntar/volcar`.
- DP-10 isométrico general a escala real H = V (Refugio 1/175, CAR Mujeres 1/200; el original del CAR Mujeres tenía exageración vertical
  x3 y se corrigió): trazo real con quiebres a 45°, cajas, tapas, cunetas que llegan, receptor; etiquetas en `franja(abajo=False)`.
  Corrección del 03-10: la caja de caída se dibujaba separada ("hueco/vacío"): ahora en la posición real del final del canal.
- Isométrico de una descarga (Barranquita, 1/25): ejes locales con x en el sentido de salida; piso interior, malla de terreno exterior
  (0.25 x 0.30 m) con perfilado frente a la salida, agua sobre el terreno, fondo, agua, solo las caras interiores que miran al observador
  (las otras taparían el fondo), coronas, losa tapa, cara de salida con el hueco, muro del cerco cortado a 0.40 m; rejilla con líneas cada
  0.10 m; llamadas ("MURO DEL CERCO (CORTADO)", "SALIDA D1: C.F. 183.759", "AGUA SOBRE EL TERRENO NATURAL", "LOSA TAPA e = 0.10 m").
- Isométrico de toda la red con el terreno: se hizo (DC-06/DC-07, 20-10) y el usuario lo descartó el 21-10 ("ya no quiero la vista 3D de todo
  el terreno"); antes había pedido "3D solo de las cunetas, con el terreno y las veredas, sin edificaciones".

### 11.16 Cortes generales y detalle de descargas (Barranquita)
- Cortes generales (`cortes_b.py`, 1/250 H = V): terreno natural, interior nivelado, bloques con techo a dos aguas (alero 3.00 m sobre NPT,
  cumbrera 1.10 m más), cada cuneta cortada con su cota de fondo; relleno donde la cuneta pasa sobre una hondonada; rótulos con `rotulos()`.
- Detalle de cada descarga (`descargas_b.py`, una lámina A1 a 1/25 toda a escala real): planta de los últimos 4.0 m (ejes que llegan, cerco,
  curvas exteriores, rótulos en dos columnas sin cruces), perfil longitudinal H = V por el eje que sale (muro del cerco cortado, cimiento,
  losa del pase, agua de diseño, terreno y perfilado, recuadros NCT/NCF/H, guitarra) e isométrico de los últimos 3.0 m con 1.75 m de terreno
  exterior; nota propia según el terreno exterior (talud → proteger contra erosión; terreno alto → perfilar).

---

## 12. Juegos de láminas por proyecto (generados por el repositorio)

### 12.1 Hogar de Refugio "Mujeres Violentadas" (CUI 2675514) — `herramientas/planos_dxf.py`
24 láminas (DP-00 A3, el resto A1): DP-01 1/200; DP-02 1/50 (2 franjas); DP-03A/B 1/50; DP-04A/B 1/15; DP-05A/B 1/20; DP-06A 1/10;
DP-06B INDICADA; DP-06C 1/10; DP-06D INDICADA; DP-07 1/25; DP-08 1/25; DP-09 1/25; DP-10 1/175; DA-01 a DA-03 1/20; DD-01 a DD-04
INDICADA. Además: DJ-01 a DJ-03 (`PLANOS_DETALLE_CUNETAS_JUNTA_Y_REJILLA_HOGAR_REFUGIO.dxf`), DL-00, DL-01/02, DS, DR, DPL-41/42.
Juego final que imprime la usuaria: DPL-01 a DPL-42 (PDF en `insumos/solange/`).

### 12.2 CAR Varones (CUI 2705619) — `herramientas/varones/planos_v.py` (+ `compat.py`)
19 láminas: DP-00 A3; DP-01 1/200; DP-02 1/100 A2; DP-03A/B 1/25; DP-04A/B 1/15; DP-06B; DP-06C 1/10; DP-06D; DP-07 1/20; DP-08;
DA-01 a DA-03; DD-01 a DD-04. Módulos comunes reutilizados con parámetros (textos fijos convertidos en variables del módulo con el valor
anterior por defecto: caudales, cotas de piso, cantidades de registros y juntas, cerco). `auditar()` cuenta entidades fuera de toda lámina.
Juego final de la usuaria: DPLV-01 a DPLV-44.

### 12.3 CAR Mujeres (CUI 2717013) — `herramientas/mujeres/planos_m.py` (metrado congelado)
17 láminas: DP-00 A3 S/E; DP-01 A1 1/200; DP-02 A2 1/100 (3 franjas); DP-03A/B/C A1 1/25; DP-04A/B 1/15; DP-05A/B 1/20; DP-06A 1/10;
DP-06B INDICADA; DP-06C A2 1/10; DP-07 1/15; DP-08 A2 1/20; DP-09 1/20; DP-10 1/200. Geometría de la hoja DATOS del metrado; cuadros
con los valores guardados de la planilla. Juego final con 46 PDF (3 A0, 15 A1, 21 A2, 7 A3).

### 12.4 I.E. N.° 0590 Barranquita (C.I. 468901) — `herramientas/barranquita/planos_b.py`
DC-00 A3; DC-01 1/250; DC-02 1/5 (INDICADA); DC-03 a DC-11 perfiles 1/50; DC-12 a DC-14 secciones 1/20; DC-15 cortes generales 1/250;
DC-16 a DC-19 descargas D1 a D4 1/25. Planos impresos por el usuario: no regenerar (necesita `insumos/barranquita/base_sitio.pkl`).

---

## 13. Presentaciones de AutoCAD, índice e impresión

`dxf_layouts.presentaciones(doc, laminas)` (CAR Mujeres tiene su copia en `planos_m.presentaciones`):
- Espacio modelo configurado en A1 (`plot_configuration_file = "DWG To PDF.pc3"`, `paper_size` A1, 841 x 594, márgenes 0, unidades mm):
  así Ctrl+P en el modelo ya no muestra "Paper Size Not Found" (problema del 08-10).
- Una presentación por lámina, con el nombre del código: `page_setup(size=(W, H), margins=0, units="mm", scale=16, name="ISO_full_bleed_A1",
  device="DWG To PDF.pc3")`; una ventana del tamaño del papel centrada en (W/2, H/2) mostrando el centro de la lámina
  `(ox + W/2·f, oy + H/2·f)` con `view_height = H·f` (escala 1:esc exacta); ventana bloqueada (`flags |= 16384`) en capa MARCO.
- Se borra "Layout1" si hay más presentaciones.
- Índice (`dxf_layouts.indice`): lámina DP-00 en A3 S/E con tabla N.º / LÁMINA / DESCRIPCIÓN / FORMATO / ESCALA (anchos 10, 20, 268, 40,
  32 mm; filas de 6.0 mm hasta 17 láminas, 5.2 mm si son más) y notas de impresión. Escala "INDICADA" para láminas con varias escalas.
- Cómo imprimir (instrucción al usuario): abrir la pestaña de la lámina; Ctrl+P; área = Presentación, escala 1:1, centrar; elegir el
  plotter propio con el mismo papel ("DWG To PDF" solo sirve para que AutoCAD encuentre los papeles ISO); todas juntas con PUBLISH.
- Al agregar presentaciones a un juego existente (Refugio, 08-10) se comprobó entidad por entidad que las láminas no cambiaron.
- Índices en Word (otros documentos): códigos y títulos tal cual el rótulo, sin renumerar ni poner observaciones; orden según pida el usuario
  (Refugio: DPL-01 a DPL-42 con grupos temáticos; Varones: DPLV-01 a DPLV-44 sin grupos; antes el Refugio seguía el orden del PDF por formato
  A0 → A3, corrección del 22-10).

---

## 14. Vista previa PNG, auditoría y control de láminas congeladas

- `python3 herramientas/dxf_render.py <dxf> <png> x0 y0 x1 y1 [dpi=110] [color]`: ezdxf drawing + matplotlib (backend Agg), fondo blanco
  (`BackgroundPolicy.WHITE`), color real con el 9.º argumento (si no, todo negro), grosores absolutos con mínimo 0.08, figura de 23.4 pulgadas
  de ancho, una sola pasada de `draw_layout` del modelo y recorte por la caja de la lámina (`laminas.json`).
- Láminas sueltas en mm de papel: caja `0 0 841 594`; DP-06D (en m): `0 0 8.41 5.94`.
- En paralelo: generar la lista de comandos desde `laminas.json` y `xargs -P 4` (o `ThreadPoolExecutor(5)`). Planos enormes (DL-00 con la
  arquitectura completa): `dxf_recorte.py` recorta el DXF a una caja sin hatch para renderizar con poca memoria.
- Resumen de todas: `vistas_previas/00_RESUMEN_TODAS.png`.
- Mirar SIEMPRE la vista previa antes de entregar: textos encimados, textos fuera del marco, llamadas cruzadas, cotas que pisan textos,
  vistas pequeñas, rótulo con textos largos, cotas que no coinciden con el diseño.
- Auditoría: `doc.audit()` sin errores; `varones/planos_v.auditar()` cuenta entidades cuyos vértices o inserción caen fuera de toda lámina.
- Láminas congeladas (DP-06B y perfiles del Refugio desde el 07-10; planos impresos de Barranquita): huella = (tipo, capa, punto, texto) de
  cada entidad dentro de su caja, antes y después de regenerar; deben quedar idénticas.

---

## 15. Lecciones de cada corrección del usuario (cronología)

| Fecha | Qué estaba mal (palabras del usuario) | Cómo quedó |
|---|---|---|
| 03-10 | "No uses color amarillo, el fondo de mi AutoCAD es blanco"; "los 3D salen color negro" (visto en el celular) | Paleta para fondo blanco; caras de isométricos con color verdadero en cada entidad. |
| 03-10 | "El acero longitudinal y transversal debe verse con colores diferentes" | Transversal rojo; longitudinal primero verde, luego círculos azules. |
| 03-10 | "No me convence el perfil longitudinal, no se aprecia el diseño" | Perfil con cajas, registros, ventanas y receptor; luego a escala real. |
| 03-10 | "Si la losa es 0.20 m debe ser 20 cm en escala... dibujar 0.20 con comando L"; "todo real, escala real, no sobredimensionado" | Perfil 1/50 H = V en dos franjas, sin exageración vertical. |
| 03-10 | "El agua se mete por debajo de algo" | La losa de fondo y el agua terminan en la caída a la caja CC (sin franja ni hueco en la poza). |
| 03-10 | "Dice que el espesor de la losa superior es 0.80... así no es la medida"; "pones 3.50 dice mide total, he medido y mide 7.30" | Cotas DIMENSION que miden el dibujo; textos de espesor con el valor real. |
| 03-10 | "Veo algo verde debajo de las cunetas" | Ventanas de cuneta simplificadas en el perfil. |
| 03-10 | "Tus líneas que indican se mezclan, usa flechas, acomoda bien todo" | Llamadas con flecha ordenadas sin cruces (columna). |
| 03-10 | "En la caja de llegada el acero rojo se sale del muro" | Acero dentro del concreto e interrumpido en las ventanas; murete del escalón en ambas cajas. |
| 03-10 | "El acero longitudinal deben ser círculos, no cuadrados pequeñitos que ni se ven" | Barras como círculos rellenos. |
| 03-10 | "En las secciones transversales todo lo mezclas, todo está unido" (envió imagen de referencia) | Secciones separadas, cotas por fuera, llamadas a un lado. |
| 03-10 | "¿Por qué hay un hueco así?" / "¿por qué hay un vacío allí?" | Isométrico general con la caja de caída en la posición real del final del canal. |
| 03-10 | "Esos círculos azules están sobredimensionados; si es 3/8 es 3/8, si es 1/2 es 1/2"; "que nada quede al aire, que el acero no salga de su losa... debe ser entendible y legible" | Bloques ACERO-38/ACERO-12 a diámetro real, escala 1.0; recubrimientos reales. |
| 04-10 | "No hay cerco perimétrico en Varones" (detalles de cerco en DP-04A); "las tapas no van exactamente donde entrega la cuneta" | `CON_CERCO = False`; registro exactamente en el cruce de cada cuneta. |
| 04-10 | "Las cunetas son las que van rectas perpendiculares, la de color negro, no la verde fuerte" | Cunetas de la capa correcta, perpendiculares. |
| 07-10 | Tapa de registro: "un dibujo bien exacto... 4 vistas tipo 3D realista, separando cada composición"; "usa letra grande, tus letras son pequeñitas; colores que combinen con fondo blanco; varios isométricos"; "una foto realista" | Lámina 3D, isométricos con letra grande, renders fotográficos y DP-06B rev. 01 en DXF. Usuario: "¡Qué excelente estilo!" → mismo estilo para las demás láminas. |
| 07-10 | "Hay láminas en desorden, letras en vertical, letras sobrepuestas, más que todo en los perfiles... todo a escala real, si algo mide 0.56 así debe medir" | Perfiles con etiquetas horizontales en franja, guitarra con columna de nombres, dibujo dentro del marco. Skill `planos-ordenados`. |
| 07-10 | Envió su DXF corregido: "así quiero los planos ordenados... ya no toques la DP-06B ni los perfiles; solo las demás, llenas con leyendas, colores" | Todas las láminas reordenadas salvo DP-06B y perfiles (congelados). |
| 08-10 | CAR Mujeres: "arregla y ordena todo el plano sin variar sus metrados" | 16–17 láminas a escala real; metrado verificado; solado al ancho exterior y límite de excavación. |
| 08-10 | "¿Las láminas todas son A1?"; "así me sale con Ctrl+P"; "tienen mucho espacio, reduce los espacios; hay planos grandes y pequeños: A1, A2 o hasta A0"; "déjalo en layout de AutoCAD e índice" | Formatos A1/A2/A3, presentaciones por lámina, modelo en A1 (sin "Paper Size Not Found"), índice DP-00. Igual en Varones y Refugio. |
| 09/10-10 | Canaleta: "isométrico tal cual, detalles hasta de los pernos según tu ACU"; "la sección es 0.20 x 0.25; dibújale vacán, colores, ordenado: el tubo, el dado, las abrazaderas, los colgadores" | DR-01 a DR-06 con todas las fijaciones del ACU. |
| 10-10 | Leyenda/especificaciones para las láminas de secciones de cunetas (DXF); sumidero 0.25 x 0.25 con tubo 4" y codo de 90° (sin sifón); lloraderos con geotextil, grava y tubo perforado 3" | Bloques de leyenda a escala real; DS-01/02; DL-01/02. |
| 15-10 | "La lámina DD-03 está mal: el colector solo tiene junta longitudinal al lado del cerco; al otro lado es tierra"; "DJ-01 está bien; hazle 3D isométricos del proceso constructivo y detalle de la rejilla" | DD-03 con vista D; DJ-02 y DJ-03. |
| 16-10 | Tapas del colector pasan a tapa ciega sin marco metálico | DP-06B rev. 02 en los 3 CAR y revisión de todas las láminas donde aparece. |
| 19-10 | Banca: "faltan los cortes frontales"; "el colgador no sale en el isométrico; debes ser fiel al dibujo, nada de errores"; "¿por qué tanto soporte en 2 metros? solo 2 soportes" | DB-03 con cortes A-A y B-B; colgador dibujado; 2 soportes. |
| 20-10 | Barranquita: agrupar en bloques por sector, explicar colores, isométrico y cortes | Bloques por tema y sistema; leyenda de colores. |
| 20-10 | "No te pido 3D así, solo de todas las cunetas, con el terreno y las veredas"; "las cunetas no pueden salir dibujadas fuera del cerco" | Isométrico solo de cunetas; nada fuera del límite de intervención. |
| 21-10 | "Así quiero los perfiles tal cual (estilo, colores, separación, sección arriba); divide por ejes"; "hazlo ordenado, no alteres ni mezcles líneas" | Perfiles por eje con el estilo del usuario (§11.5). |
| 21-10 | "En el eje 1, a los 34.64 m hay un quiebre raro"; "la sección 4 de 15 cm es imposible, peor tapada"; "en cunetas de 30 consideras acero: el acero es desde 40" | EJE-01 entrega con caída de 0.42 m; pase por el cerco sin bajar el borde; tapados con altura libre ≥ 0.25; acero solo desde h = 0.40 o tapado. |
| 21-10 | "Hazme detalle en corte longitudinal e isométrico solo de las descargas, no mezcles líneas ni capas"; "usa quiebres de 45"; "en el perfil no muestres los quiebres, en planta sí" | Una lámina por descarga; chaflanes de 0.60 m en planta; nudos "~" fuera de perfiles. |
| 21-10 | "¿Por qué mide 0.30 si el ancho total es 0.60? ¿No dibujaste a escala real?" | Toda la lámina de descarga a 1/25 real (antes planta e isométrico a 1/50 dentro de una lámina 1/25). |
| 21-10 | "Ya no quiero el 3D de todo el terreno; dibuja bien la planta: con rejilla o tapada como mi ejemplo; tapas de inspección cada tantos metros; tapada con líneas verdes" | Planta con rejilla celeste y platinas, tapada verde, flechas rojas, tapas 0.60 x 0.60; sin isométricos de la red. |
| 21-10 | "No pongas 'bloque X y número', se ve feo; solo nombre del eje y progresivas; conserva 'pabellón'" | Títulos de perfil sin coordenadas ni bloques. |
| 21-10 | "¿Por qué dice 31.45? En varios veo errores de medida" | Longitud siempre de sección a sección (35.59). |
| 21-10 | "Ya no alteres planos, ya imprimí el último" | Planos de Barranquita congelados. |
| 22-10 | Lloraderos: "en la imagen se ve bien, pero en DXF se ve horrible" (patrones sin escala, "m³" → "m?") | Dibujo sin patrones, "m3", presentaciones A3 1:10. |
| 22-10 | Índice: "el PDF está ordenado por formato de hoja, primero A0..., no por número"; sin observaciones | Índice con los códigos del rótulo, sin renumerar. |
| 23-10 | Varones: "el índice ordénalo de la lámina uno a la última sucesivamente" | Índice DPLV-01 a DPLV-44. |

---

## 16. Discrepancias conocidas y pendientes (no corregidas porque las láminas están impresas o congeladas)
- `perfiles_b.corte` dibuja las barras longitudinales de 3/8" con radio 0.0085 m (Ø 17 mm) en vez de 0.00475 m (Ø 9.5 mm); contradice la regla
  de diámetro real. Al rehacer: usar el bloque ACERO-38.
- Guitarra de los perfiles de cunetas: progresiva y etiqueta verticales (1.0 mm) para que no se encimen; un programa nuevo debería
  ponerlas horizontales con selección de estaciones (como `_estaciones`) o filas alternadas.
- DP-07 del Refugio: texto "LINDERO" vertical en el corte CL.
- `dxf_detalles` (tecnopor ANSI37) y `achurado()` en capas no-concreto (TERRENO-ACHURADO) usan patrones: riesgo de verse mal en AutoCAD (lección
  del 22-10). Preferir sólidos con color verdadero.
- Vistas ampliadas dentro de láminas (DD-01..04 a 1/5, 1/2, 1/1 en lámina 1/10; DP-08 figuras 1/15 en 1/25; DP-06D vistas 3 y 4 al doble):
  la geometría del modelo no mide 1:1; llevan escala indicada y cotas con texto real.
- Barranquita DC-16 a DC-19: el texto "AGUA DE DISEÑO" conserva los caudales anteriores (207.7 / 264.7 / 174.2 / 48.4 l/s; vigentes 229.2 /
  228.9 / 166.2 / 45.5 l/s) hasta regenerar con `base_sitio.pkl`; decisión del usuario.
- CAR Mujeres: la partida del metrado dice "C/MARCO Y CONTRAMARCO" y el isométrico 2 de IC-01 dibuja marco y contramarco, mientras D-RL y la
  memoria indican tapa ciega; no se tocó (presupuesto congelado).

---

## 17. Para implementarlo en un programa

### 17.1 Motor de dibujo
- Biblioteca: `ezdxf` (Python) para escribir DXF R2010; `ezdxf.addons.drawing` + matplotlib para la vista previa; `shapely` para unir
  contornos en planta; `numpy` para interpolar perfiles. En otro lenguaje: cualquier escritor DXF que soporte LWPOLYLINE con ancho, HATCH
  sólido con color verdadero (grupo 420), DIMENSION con DIMSTYLE completo, bloques, layouts con VIEWPORT.
- Unidad del modelo: metros. Unidad de "papel" para decidir tamaños: mm. Conversión única `modelo = origen + mm × f`, `f = escala/1000`.
- Capas, colores, grosores, alturas de texto y DIMSTYLE en un archivo de estilo (tablas de §4–§6), no repartidos en el código.

### 17.2 Estructuras de datos sugeridas
```
Estilo        : capas{nombre: (aci, rgb, tipo_linea, grosor)}, k_txt{capa: factor}, dimstyles{escala}, fuentes
Proyecto      : nombre (2 lineas), cui, entidad, ubicacion, especialidad, elaborado (vacio), fecha
Lamina        : codigo, titulo, subtitulo, formato (A0..A3), escala, escala_txt, origen (ox, oy), caja, vistas[]
Vista         : tipo (planta|perfil|seccion|detalle|iso|tabla|leyenda|notas), caja_papel (mm), escala_propia,
                origen_modelo, entidades[], etiquetas[], llamadas[]
Etiqueta      : punto (m), lineas[], color, prioridad          -> colocada por la franja
Llamada       : punto_objeto (m), lineas[], lado (izq|der)     -> colocada por la columna
Cota          : p1, p2, distancia_mm, orientacion, texto ("<>" por defecto)
Diseno        : eje (polilinea), perfil[(prog, NCT, NCF, NA, h, zona)], secciones[], registros[], cunetas[], juntas[],
                cruces[], cajas[], descargas[]    (todo leido del calculo; el dibujo no inventa cotas)
```

### 17.3 Flujo general
```
leer diseno (json) y metrado vigente (solo lectura)
doc = nuevo_documento(estilo)          # capas, estilos, dimstyles, bloques
para cada lamina del juego:
    elegir formato y escala (la vista debe llenar >= 1/3 de su espacio; losa >= 3 mm en papel)
    crear Lamina (marco + rotulo con datos del proyecto; proyectista y CIP en blanco)
    dibujar vistas en sus cajas de papel (arriba), leyenda/notas/cuadros (franja inferior), nada sobre el rotulo
    colocar etiquetas (franja) y llamadas (columna) al final de cada vista
rellenos al fondo (redraw order); indice A3; presentaciones por lamina; audit; guardar
guardar cajas (laminas.json) e indice (indice.json); renderizar PNG por lamina; controles de calidad (17.5)
```

### 17.4 Pasos por tipo de lámina
- Planta: fondo de arquitectura recortado y gris → límite de intervención → obra (contornos unidos, estado por tramo: rejilla/tapada) →
  registros/tapas en las llegadas → juntas → flechas → progresivas → rótulos (Etiquetas 8 posiciones o franja) → grilla UTM y norte →
  cuadro de coordenadas → leyenda y notas. Bloques por tema. Quiebres a 45° con chaflán 0.60.
- Perfil: decidir franjas/piezas (ancho útil 800 mm en A1) → por pieza: agua, losa de fondo y solado, losa superior con huecos, NPT,
  registros, ventanas, juntas, cruces, cajas → niveles y cotas h → escala de cotas o referencias relativas al NPT → secciones (línea roja)
  y recuadros NCT/NCF/H en filas → guitarra con columna de nombres y estaciones filtradas → etiquetas en franja superior → título.
- Sección: concreto en una pieza con hueco → acero (marco con recubrimiento real, barras a diámetro real) → agua con Q del tramo → terreno,
  NPT, excavación, cerco/junta → cotas por fuera (parciales y totales) → niveles → llamadas en columna → título con progresiva, CF y zona.
- Detalle: una escala por lámina o vistas ampliadas con su escala en el título y cotas con texto real; despiece; cuadro de componentes por
  unidad (para el ACU); procedimiento constructivo en notas.
- Isométrico: transformación con corrección de espejo (y rosa N/E de control) → teselar caras → pintor con sombreado → solo caras visibles →
  aristas en capa aparte → llamadas en columna o junto al punto del lado libre.
- Cuadros: leer valores guardados de la planilla; nunca recalcular.
- Índice y presentaciones: lista (código, título, formato, escala) en el orden del juego; una presentación por lámina con su papel ISO.

### 17.5 Controles de calidad automáticos (antes de entregar)
1. Escala: para cada vista, comparar cotas/medidas del dibujo con el diseño (ancho total, espesores, h, longitudes de tramo); tolerancia 1 mm.
   Ninguna cota con texto fijo distinto de su medida (salvo pulgadas, alias o vista ampliada declarada).
2. Dentro del marco: todos los vértices e inserciones dentro de x 25..W−10, y 10..H−10; nada dentro del rectángulo del rótulo
   (W−195..W−10, 10..105) salvo el rótulo; nada fuera de toda lámina (como `auditar`).
3. Cruces de texto: caja de cada texto (ancho ≈ 0.62–0.72 × h × n.º de caracteres, alto h) sin intersección con otras cajas de texto, con
   cotas ni con líneas de llamada; líneas de llamada que no se cruzan entre sí (prueba de segmentos).
4. Orientación: ningún TEXT con rotación ≠ 0 salvo progresivas/curvas en planta y cotas.
5. Tamaños: altura de texto en papel entre 1.8 y 6 mm (rótulo 1.6–2.4); losa o muro ≥ 3 mm en papel; barras con el radio real.
6. Colores: ninguna capa ni entidad en amarillo; rellenos HATCH sólidos con RGB (sin patrones); capas nuevas con color definido.
7. Acero dentro del concreto: cada barra/marco dentro del polígono de concreto menos el recubrimiento.
8. Límite de intervención: ninguna entidad de obra fuera del cerco.
9. Coherencia: un mismo elemento igual en planta, perfil, sección, detalle e isométrico; códigos de lámina correlativos sin saltos; cuadros
   iguales a la planilla.
10. `doc.audit()` sin errores; abrir en AutoCAD sin avisos (DIMSTYLE con grupos 3–7, sin "/" en bloques, sin caracteres fuera de ASCII).
11. Vista previa PNG de cada lámina y revisión visual; láminas congeladas comparadas por huella.

### 17.6 Pseudocódigo de la columna de llamadas sin cruces
```
def columna(items, xt, ytop, ybot):
    n = len(items); ys = [ytop - i*(ytop-ybot)/(n-1) for i in range(n)]
    orden = sorted(range(n), key=lambda i: -items[i].punto.y)       # mismo orden vertical que los puntos
    repetir hasta 4n veces:
        cambio = False
        para k en 0..n-2:
            si segmento(items[orden[k]].punto, (xt, ys[k])) cruza segmento(items[orden[k+1]].punto, (xt, ys[k+1])):
                intercambiar orden[k], orden[k+1]; cambio = True
        si no cambio: salir
    para k, i en enumerate(orden): llamada(items[i].punto, (xt, ys[k]), items[i].lineas)
```

### 17.7 Lo que el programa no debe decidir solo (avisar al usuario)
- Contradicciones entre láminas y metrado: ofrecer opciones y recomendar la que coincide con el metrado; no cambiar el metrado.
- Datos que no están en el plano (dónde llegan cunetas, receptores de descargas, distancia entre tapas de inspección): proponer y rotular
  como "referencial / verificar en campo" o preguntar.
- Láminas impresas o congeladas: no regenerar.
