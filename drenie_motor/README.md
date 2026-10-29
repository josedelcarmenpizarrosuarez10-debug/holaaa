# Motor de DrenIE (Python) – Terreno, superficies y red de cunetas en planta

Programa auxiliar de DrenIE. DrenIE (interfaz) lo llama por línea de comandos con un archivo de proyecto JSON; el motor lee el
plano DXF, arma el mapa de superficies, traza la red de cunetas, calcula cotas de fondo y caudales, verifica y entrega
resultados en JSON, la planta en DXF (escala real, 1 unidad = 1 m) y vistas previas PNG.

Criterios: `conocimiento/04_cunetas_sobre_terreno.md` y `conocimiento/02_hidrologia_e_hidraulica.md` (valores por defecto en
`drenie_motor/parametros.py`, todos cambiables en el proyecto).

## Uso

```
python -m drenie_motor lluvia  proyecto.json   # lluvia de diseno: serie de la estacion, frecuencias, K-S, IDF, I de diseno
python -m drenie_motor leer    proyecto.json   # lectura, mapa de superficies, imagen de control (confirmar antes de disenar)
python -m drenie_motor disenar proyecto.json   # red, cotas, caudales, 12 comprobaciones, planta DXF y PNG
```

Salida en la carpeta `salida` del proyecto: `lectura.json`, `CONTROL_LECTURA.png`, `resultado.json`,
`PLANTA_RED_CUNETAS.dxf`, `PLANTA_RED_CUNETAS.png`; con `lluvia`: `hidrologia.json`, `HIDROLOGIA.xlsx` (datos, análisis,
Kolmogorov-Smirnov, IDF) y `CURVAS_IDF.png`. Código de salida 0 = bien; 2 = error de datos (mensaje en `error`).

Requisitos: Python 3.10+, `ezdxf`, `shapely` 2, `scipy`, `numpy`, `matplotlib`.

## Orden de trabajo en DrenIE

1. Proyecto → 2. Lectura del plano (`leer`) → 3. Mapa de superficies (confirmar; asignar lo que falte) → 4. Lluvia (estación
SENAMHI, análisis estadístico, Dick y Peschke → I) → 5. `disenar`: áreas de aporte y caudal de cada cuneta, diseño, verificación
→ 6. Planos, metrado y documentos (módulos siguientes).

## Archivo de proyecto (ejemplo completo: `ejemplos/barranquita/proyecto.json`)

| Clave | Contenido |
|---|---|
| `proyecto` | nombre, nombre_corto, codigo (CUI o C.I.) |
| `dxf` | plano del usuario (DXF, ZIP o carpeta con el ZIP en partes) |
| `capas.curvas`, `capas.curvas_texto`, `capas.equidistancia` | curvas de nivel (con elevación o rotuladas a cota 0) |
| `capas.cerco` | capa del cerco o `{"poligono": [...]}` confirmado |
| `capas.ejes` | líneas de cuneta del usuario: `{"capa": "0", "color": 6}` |
| `capas.techos`, `capas.veredas`, `capas.muros` | capas de arquitectura; en una selección con llaves también `"cerrada": true` (solo polilíneas cerradas), `"area_min"` (m²) y, en techos, `"separados": true` (cada contorno cerrado es un techo aunque toque al vecino). CAR Varones: `{"capa": "0", "color": 1, "cerrada": true, "area_min": 40, "separados": true}` (techos dentro de los bloques de cada edificación) |
| `niveles` | `modo` (`nivelado` o `terreno`), `npt`, `borde_cuneta`, `area_verde`, `zonas` (polígono, nivel, superficie) |
| `superficies` | superficies con nombre (losas, patios techados...): `nombre`, `tipo`, `poligono` o `capa` |
| `superficies_cfg.leyenda` | colores o capas de sombreados → tipo: `[{"sel": {"capa": "AREAS", "color": 3}, "tipo": "verde"}]` |
| `superficies_cfg.rotulos` | textos → tipo (se suman a los de fábrica: AREA VERDE, VEREDA, ESTACIONAMIENTO...) |
| `superficies_cfg.asignaciones` | clics del visor: `{"x", "y", "tipo"}` (punto dentro del área) |
| `superficies_cfg.por_defecto` | tipo para lo no identificado; si falta, el diseño no corre hasta asignarlo |
| `techos_caida`, `caida_por_defecto` | caída por techo: `{"punto", "tipo": "dos_aguas", "cumbrera": [[x, y], [x, y]]}` o `{"punto", "tipo": "una_agua", "lado_bajo": [...]}` |
| `dimensionamiento_adoptado` | la hoja `DIMENSIONAMIENTO.xlsx` con la columna B ADOPTADO llena por el proyectista (el programa la verifica) |
| `secciones` | ancho libre adoptado por eje escrito en el proyecto: `{"EJE-01": 0.45}` |
| `parametros` | cambia cualquier valor de `parametros.py`: `b_int` 0.30 (ancho libre mínimo), `b_max` 0.40 (ancho libre máximo recomendado: 0.60 total), `paso_seccion` 0.05, `hmin` 0.30, `h0` 0.30, `S0` 0.005, `e_muro`, `e_tapa`, `e_fondo` y `e_solado` 0.10, `uniforme` (`sector`, `eje` o `tramo`), `y_b_max` 1.0, `llor_sep` 1.50 |
| `lluvia` | Datos de la estación: `{"estacion": {...}, "archivo": "datos diarios SENAMHI / NASA POWER / CHIRPS", "desde", "hasta", "T": 25, "tc_min": 10, "factor": 1.0, "distribucion": opcional}` o `"serie": {anio: [12 máximas mensuales]}` o `"maximos": {anio: P24}`. Sin datos de estación: `{"I_mmh": ...}` o `{"P24": ..., "tc_min": 10}`. Barranquita: P24 = 169.27 mm, I = 293.18 mm/h (igual al expediente) |
| `descargas` | descargas fijadas por el usuario `[{"nombre": "D1", "x", "y"}]` (sin esto, el motor las propone) |
| `parametros` | cambios a los valores por defecto |

## Reglas que aplica

- **Mapa de superficies** sin montajes ni huecos (la suma de áreas = área del cerco); las cunetas ocupan su franja de 0.60 m y
  recortan las superficies de piso; cada ajuste se informa; lo no identificado queda "sin asignar".
- **Agua de los techos**: cada mitad cae por su alero a la cuneta que está debajo (dos aguas: ambos lados; una agua: lado
  bajo). Se avisan los aleros sin cuneta.
- **Las líneas del usuario mandan**: no se mueven; solo se agregan uniones (perpendiculares, en prolongación o por el camino
  perimetral a 0.60 m del cerco), sin cruzar edificaciones, losas ni otras cunetas, ni cruzarse entre sí.
- **Ninguna cuneta enterrada**: cada descarga (pase en el cimiento del cerco) debe tener el terreno exterior bajo la cota de
  fondo a ≤ 2 m; se eligen las menos descargas que cubren todas las líneas sin pasar la profundidad objetivo (1.00 m). Si una
  parte no tiene salida, no se entrega el diseño y se indican los metros sin salida.
- **12 comprobaciones**: conectividad, contrapendiente, pendiente mínima, profundidades, empalmes, descargas, niveles,
  capacidad, velocidad, distancia a edificaciones, dentro del cerco, todas las líneas del usuario con cuneta.

## Prueba

`python3 ejemplos/barranquita/armar_dxf_prueba.py` arma el plano de prueba de la I.E. N.° 0590 Barranquita (C.I. N.° 468901)
con los datos de entrada del usuario (curvas, techos, veredas, cerco y líneas magenta); luego `leer` y `disenar`.

`ejemplos/car_varones/proyecto.json`: CAR Varones (CUI 2705619) con el plano general real de la usuaria
(`insumos/katiuska/planta/`), la topografía LandXML transformada al plano y el colector frontal como receptor (su cota de
fondo reemplaza al terreno exterior en las descargas D1 a D5). Comparado con el metrado de la usuaria del 23-10-2026:
canaletas 523.90 m (523.16), soportes 906 (906), tapas laterales 44 (44); cunetas 538.22 m en 9 ejes (545.2 m).

## Sección de cada tramo y lloraderos

- Medidas: 0.30 × 0.30 es la sección libre; ancho total = libre + 2 muros (0.50); excavación = altura libre + losa de fondo +
  solado (0.50). Una sola medida por sector (todos los ejes que salen por la misma descarga llevan el mayor ancho que pida
  cualquiera de sus tramos); `uniforme: "eje"` da una medida por eje. El dimensionamiento final lo adopta el proyectista en la hoja
  `DIMENSIONAMIENTO.xlsx` (columna B ADOPTADO) y el programa lo verifica.
- Muros y losa de 0.10. Cada tramo pide el menor ancho libre (desde 0.30, de 5 en 5 cm) con el que el tirante más el borde libre
  cabe en la profundidad que da el perfil, con el tirante no mayor que el ancho y la profundidad no mayor que 2 veces el ancho
  (que se pueda encofrar y acabar). Aguas abajo no se angosta. Ancho libre máximo recomendado 0.40 (0.60 total): si no alcanza, se profundiza (redondeado a 5 cm). La profundidad no tiene límite respecto al ancho: la regla es que ninguna cuneta quede enterrada (todas las descargas salen por gravedad).
- `resultado.json`: `verificacion.hidraulica` (por tramo: área y caudal de techos, pisos y áreas verdes, b, h, tirante, borde libre,
  velocidad), `secciones_por_eje`, `lloraderos` (tramos por lado junto a área verde, N.° = REDONDEAR.MAS(L / 1.50)).
- Lloraderos solo en el muro que da a área verde: PVC 3" @ 1.50 m con caja filtrante de 0.30 × 0.30 de grava y geotextil
  (capa `DRN-LLORADEROS` del DXF; el ancho de cada tramo en `DRN-SECCION-TXT`).
- Comprobación 13: secciones constructivas.

## Juego de planos de cunetas (`PLANOS_CUNETAS.dxf`)

Mismo estilo de las láminas de Barranquita, una presentación (layout) por lámina y rótulo con los datos del proyecto (sin
nombre ni CIP del proyectista):
- DC-01 planta general (escala elegida para que el cerco entre en A1; coordenadas UTM): arquitectura de fondo, curvas, límite de
  intervención, cunetas a escala real con el ancho de cada eje (rejilla con platinas, tapados con tapas 0.60 × 0.60), flechas de
  flujo, lloraderos con su caja filtrante, nudos, códigos de eje con su ancho libre, descargas, leyenda, cuadro de descargas y
  criterios; todo en bloques de AutoCAD por tema.
- DC-02 cuadros: ejes (sector, L, Q máx, b libre, total, h mín/máx, excavación), descargas (ejes, L, Q, C.F.) y tramos de lloraderos.
- DC-03 en adelante: perfiles longitudinales por eje (1/50) y el corte de cada sección (1/20).
Canaletas y montantes (`techo.py`, hoja `CANALETAS_Y_MONTANTES.xlsx`): por cada lado de techo, canaleta galvanizada
0.25 × 0.20 a lo largo del alero (S 1 %, n 0.013, borde libre 0.05; soportes de platina 1" × 1/8" @0.60 + 1, 2 tapas laterales,
1 boquilla por montante) y montantes PVC 4" por Wyly-Eaton (rs 0.25) en las esquinas de la edificación (2 por lado; hasta 4),
editables en el visor (MT). DrenIE solo ubica el montante y mide su salida: falsa columna 0.20 × 0.15 × 1.30 y dado por montante;
en el dado un codo de 90° de 4" y la tubería PVC 4" embebida hasta la cara interior de la cuneta (máximo 5 m, `tubo_max`), al 1 %
(mínimo 0.5 %), con su fondo a 0.20 m bajo el piso (0.15 si hace falta). La altura del montante, el tubo que sube a la canaleta,
los codos del desvío, colgadores y abrazaderas los mete el proyectista con los cortes de arquitectura (usuario, 25-10-2026).
La cuneta puede ir a lo largo del alero o transversal a él: se verifica que el tubo de cada montante llegue a una cuneta.
Llegada de tuberías (`llegada.py`, montantes y sumideros): el fondo del tubo llega sobre el nivel del agua de la cuneta en ese punto
(cota de fondo + tirante con el caudal del punto) + 0.05 m, para que no quede ahogado. Si no: 0.5 %, tubo más alto, otra cuneta y
por último se profundiza el tramo que lo recibe (sin pasar de la profundidad máxima objetivo, 1.00 m); si aun así no llega, se avisa.
Se dibujan en la DC-01 (bloque CANALETAS_Y_MONTANTES) y su cuadro va en la DC-02.
Planteamiento de cunetas de edificaciones y losa deportiva (`planteamiento.py`, proyecto `"planteamiento"`): para cada techo se
prueban los lados de su contorno (a 0.30 m fuera de la proyección del techo; a lo largo del alero o transversales) y todas sus
combinaciones, y se elige la que deja todos sus montantes a 5 m o menos con menos cuneta nueva, aprovechando las cunetas vecinas
(dos techos vecinos comparten la cuneta del espacio entre ellos). Luego cada cuneta planteada se prolonga en línea recta hacia las
descargas hasta otra cuneta o el cerco junto a una descarga, sin entrar en techos; el resto de uniones las hace la red. Modos:
`"completar"` (por defecto: solo donde un montante no llega a las líneas del proyectista), `"automatico"` (todo desde cero, sin
las líneas del proyectista; ejemplo `ejemplos/car_varones_auto/`) y `"no"`. El razonamiento por techo va en
`resultado.json` (`planteamiento.techos`) y en la memoria descriptiva.
Sumideros (`sumideros.py`): solo en áreas libres sin cobertura (`sumidero_tipos`, por defecto patio y estacionamiento), donde la
zona queda a más de 8 m de una cuneta; tubo PVC 4" recto a la cuneta (S 1 %, llega sobre el nivel del agua + 0.05); editables en el
visor (SU); hoja SUMIDEROS en `CANALETAS_MONTANTES_Y_SUMIDEROS.xlsx`, dibujo en la DC-01 y cuadro en la DC-02.
Prefijo y número inicial en `planos` (`{"prefijo": "DC", "inicio": 1}`). `PLANTA_RED_CUNETAS.dxf` queda como dibujo de trabajo.
Librería de dibujo propia en `dxf_base.py` y `dxf_layouts.py` (copias de las de `herramientas/`).

## Metrado general (`metrado.py` → `METRADO_DRENAJE_PLUVIAL.xlsx`)

Formato del metrado del CAR Mujeres y de Barranquita, con fórmulas: RESUMEN, PLANILLA GENERAL DE METRADOS, CONCRETO EN CUNETAS,
ENCOFRADO Y DESENCOFRADO, METRADO ACERO, METRADO JUNTA DE DILATACION, METRADO DE CURADO, METRADO DE REJILLAS, PLANILLA TAPAS
INSPECCION, METRADO LLORADEROS, METRADO MONTANTES, METRADO CANALETAS, METRADO  EN PISO (SUMIDERO), PARAMETROS y Listas. Partidas con
los nombres y la estructura Delphin del Hogar de Refugio (prefijo en `metrado.prefijo`, por defecto `01`); cantidades del diseño
(cada eje con su ancho libre). Datos del rótulo: `proyecto.entidad`, `proyecto.ubicacion`, `proyecto.fecha`.

## Memorias y especificaciones técnicas (Word)
`disenar` entrega también, en la carpeta de salida:
- `MEMORIA_HIDROLOGICA_DRENAJE_PLUVIAL.docx` (`memorias.py`): estación y serie de máximos en 24 h, análisis de frecuencias
  (Normal, Log Normal, Log Pearson III, Gumbel), Kolmogorov-Smirnov, Dick y Peschke, IDF de Bell, superficies y C ponderado,
  caudales por eje (techos, pisos y áreas verdes), sección adoptada por sector, verificación hidráulica, comprobaciones,
  canaletas y montantes, sumideros, descargas y conclusiones. Sin estación (solo `I_mmh`) se cita la intensidad dada.
- `MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL.docx`: ubicación, terreno y niveles, criterios de diseño, sectores y ejes, descargas,
  lloraderos, techos, sumideros, metas físicas (totales del metrado recalculado con LibreOffice si está instalado), normas y
  relación de planos.
- `ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL.docx` (`especificaciones.py` + `espec_textos.py`): capítulo de generalidades y una
  ficha por partida del metrado (mismos códigos, nombres y unidades), con los datos de este diseño.
Formato común (`word.py`): A4, Arial, títulos azules numerados, tablas y figuras numeradas, carátula con el proyecto y su código.
Sin nombre ni CIP del proyectista. Datos opcionales del proyecto para los textos: `proyecto.entidad`, `gerencia`, `ubicacion`,
`fecha`, `foto` (carátula) y `memoria` (`departamento`, `provincia`, `distrito`, `localidad`, `predio`, `colindancias`, `acceso`,
`clima`, `antecedentes`, `modalidad`, `normas`): lo que no se da no se escribe.

## Revisión general (`revision.py` → `REVISION_GENERAL.xlsx`)
Al terminar `disenar` el programa revisa solo todo lo que entregó (validaciones de `conocimiento/01`, sección 8.2) y lo deja en
`REVISION_GENERAL.xlsx` y en `resultado.json` (`revision`): CUMPLE, NO CUMPLE (regla incumplida) o AVISO (dato a confirmar o
entregable pendiente).
- Diseño: ancho libre 0.30 a 0.40, de 5 en 5 cm, una medida por sector; espesores de 0.10; pendiente; profundidad inicial;
  borde libre; velocidad; descargas por gravedad; las 13 comprobaciones del ciclo.
- Componentes: montantes de 4", a lo más 4 por lado (hasta 7/24 de llenado), canaletas, sumideros solo en áreas libres sin
  cobertura y con su tubo sobre la cota de fondo (si no llega, el programa profundiza el tramo que lo recibe), lloraderos @1.50 m.
- Metrado: sin errores de fórmula (recalculado con LibreOffice) y cantidades iguales a las del diseño.
- Documentos: español y términos del usuario, sin personas ni CIP, metadatos vacíos (sin marcas de la herramienta en Word,
  Excel ni DXF), sin citas a otros proyectos, láminas citadas existentes, cifras de memorias y especificaciones = diseño.
- Planos: cotas con texto igual a su medida, unidades en metros, textos dentro del marco, sin encimarse, sin textos verticales,
  sin amarillo ni blanco puro.
- Entregables pendientes y datos tomados por defecto, como avisos.

## Juego completo de entregables (24-10-2026)
`disenar` entrega, además de lo anterior:
- Láminas de **descargas** (`descargas.py`, 1/25, una por descarga): planta, perfil longitudinal con el agua de diseño e
  isométrico; portado del generador de Barranquita con los datos del proyecto.
- Láminas de **detalles** (`detalles.py`, a escala real): DC rejilla, tapa de inspección y juntas (1/5); lloradero, falsa
  columna con el montante en la esquina, canaleta con soporte y sumidero (1/5); montante en elevación y muro con lloraderos (1/10).
  Las especificaciones citan la lámina de detalle de cada partida.
- `MEMORIA_CALCULO_DRENAJE_PLUVIAL.xlsx` (`memoria_calculo.py`): DATOS editables, serie, frecuencias, Kolmogorov-Smirnov, IDF,
  superficies, caudales y Manning por tramo, canaletas y montantes (Wyly-Eaton), sumideros y descargas, todo con fórmulas; la
  revisión la recalcula y compara con el diseño.
- `CARATULA_E_INDICE_DE_PLANOS.docx` y `CARATULAS_DRENAJE_PLUVIAL.docx` (`caratulas.py`).
- `LAMINA_<código>.png` de cada lámina (`render.py`; se apaga con `"png_laminas": false`).

## Batería de pruebas (antes de entregar cualquier versión)

`python3 pruebas/sitios.py 12 100` arma terrenos de prueba inventados (`pruebas/sitios/`, no se versionan): cercos rectos, con
esquina cortada o lado inclinado; edificios, techos en L y losa deportiva, pegados entre sí o cerca del cerco; sitio girado;
terreno de 0.5 % a 7 % de pendiente. `python3 pruebas/correr.py` corre los proyectos de `ejemplos/` y esos terrenos y clasifica
cada uno: BIEN (revisión sin fallas), PROYECTISTA (diseño completo; lo que no se resuelve sin cambiar un dato queda como
«decisión del proyectista» con la solución calculada), DATOS (mensaje en español de lo que falta) o CAIDA / FALLA (no se entrega
la versión). Resultado en `pruebas/RESULTADO_PRUEBAS.json`.

El programa no se cae: un error interno sale como mensaje en español (código 3) y su detalle técnico queda en
`REGISTRO_DE_ERROR.txt` de la carpeta de salida. Si el agua no tiene salida por gravedad con el NPT dado, el motor diseña lo que
sí sale, calcula cuánto hay que subir el piso y lo verifica rediseñando con ese nivel («subir el nivel de piso 0.55 m
(NPT 170.64): verificado, con ese nivel toda la red sale por gravedad»); si con ningún nivel razonable sale, pide una descarga
a un colector o canal existente. Si quedan cunetas sin unir, la red se rehace admitiendo uniones más largas (×2, ×3).

## Ventana de soluciones

Lo que el programa no resuelve solo, o que conviene confirmar, no se esconde: `resultado.json` trae `observaciones`, cada una con
qué pasó, dónde (E, N), por qué y las soluciones posibles: **automática** (el programa la aplica en el siguiente cálculo, p. ej.
subir el NPT ya verificado o dejar que elija las descargas), **manual** («lo resuelvo a mano»: dibujar la cuneta, mover el montante,
indicar una descarga) o **confirmar** (aceptar lo que supuso el programa: caída de techos, tipo de superficie por defecto). La
recomendada va marcada. El motor arma `VISOR_DRENIE.html` (escena + observaciones) en la carpeta de salida; al abrirlo aparece la
ventana «El programa necesita su decisión» (también el botón Soluciones y la pestaña Soluciones), con «Ver en el plano» (zoom y
marca en el punto) y un botón por solución; «Lo analizo después» la deja pendiente. Lo elegido viaja en `ediciones.json`
(`"soluciones"`) y el motor lo aplica al volver a calcular. Sin visor: `python -m drenie_motor aplicar proyecto.json nivel A`.
La hoja SOLUCIONES de `REVISION_GENERAL.xlsx` lleva la misma lista. Arquitectura: ventana en JavaScript (visor), motor en
Python, y se comunican por archivos JSON.

## Dentro de DrenIE 3.1.0 (pestaña RED DE CUNETAS)

El motor va dentro del instalador de DrenIE como programa auxiliar (`empaquetar/`: `arranque.py`, `drenie-motor.spec`,
`construir.py` compila con PyInstaller y prueba el ejecutable; bibliotecas en `requisitos_motor.txt`). DrenIE lo llama con la
orden nativa `motor_red` (licencia de DrenIE en cada llamada) y el visor va en un marco de la página 15 (`visor-red.html`, el
mismo `visor/visor.html` con el tema claro de DrenIE: Poppins, azul marino #0B2545 y celeste #1EA7F2). La cinta RED DE CUNETAS
manda los comandos al visor por mensajes (`postMessage`) y el visor pide a la página lo que necesita del motor.

Órdenes de escritorio (`escritorio.py`; responden un JSON por la salida estándar, con `error` en español si algo falla):

```
python -m drenie_motor capas plano.dxf                 # capas del plano y las que el programa propone (cerco, techos, curvas...)
python -m drenie_motor crear < datos.json              # carpeta y proyecto.json (nombre, dxf, capas, npt, I_mmh, planteamiento)
python -m drenie_motor vista proyecto.json             # escena, ediciones y observaciones para el visor
python -m drenie_motor ediciones proyecto.json < ed.json   # guarda lo dibujado en el visor (ediciones.json)
python -m drenie_motor entregables proyecto.json       # archivos del último cálculo
python -m drenie_motor abrir proyecto.json [ARCHIVO]   # abre la carpeta de salida o un entregable
```

El ejecutable compilado solo trabaja con la ficha de sesión que firma DrenIE (`DRENIE_SESION`, HMAC-SHA256 con la clave que
comparten `__main__.py` y `motor_red.rs`, válida 5 minutos); desde el código fuente no la pide. Todo lo que imprimen las
bibliotecas durante el cálculo va a la salida de errores: la salida estándar lleva solo el JSON de respuesta, en UTF-8.
Integración en DrenIE (archivos nuevos y cambios sobre 3.0.2): `integracion_drenie_3_1_0/`.

Protección del código: `construir.py` compila primero el paquete `drenie_motor` con Nuitka (módulo binario de C compilado:
`.pyd` en Windows, con Visual Studio o con el MinGW64 que Nuitka descarga solo la primera vez) y PyInstaller empaqueta ese módulo
en lugar del bytecode; el análisis de PyInstaller sigue usando el código fuente solo para encontrar las bibliotecas. Al final se
comprueba que ningún módulo de `drenie_motor` quede como bytecode. Los resultados son los mismos que con el código fuente
(probado con un diseño completo). `--sin-compilar` arma una versión sin proteger, solo para pruebas internas.

## Plataformas, estructuras de caída y estacionamientos

`niveles.plataformas` (polígono, NPT, rebaje), `niveles.rampas` (polígono, inicio, fin, NPT de inicio y de fin), `niveles.escaleras` y
`niveles.bordes_eje` (línea, NPT, rebaje), también dibujados en el visor (comandos PLATAFORMA, RAMPA, ESCALERA y la pregunta del borde
al terminar un eje de cuneta; viajan en `ediciones.json` → `niveles`). `sitio.rasante` da el borde en cada punto; `red.py` no deja
que el agua suba de plataforma (penalidad al elegir recorridos y descargas, y división del flujo en el borde de la plataforma);
`cotas.py` registra los cambios de nivel (`cambios_nivel`) y absorbe los de hasta 0.15 m; `estructuras.py` define y dimensiona caída
corta, caja de caída y pase por muro con marco de C.A. y poza (USBR); `estructuras_dxf.py` dibuja su lámina de detalle. En
estacionamientos la cuneta va siempre tapada con la losa de `tapa_vehicular.py` (rueda HL-93). Todo pasa al metrado, la memoria
(capítulo propio y recuadros de fuente), la memoria de cálculo (hojas ESTRUCTURAS y TAPA VEHICULAR, con fórmulas) y las
especificaciones. Terrenos de prueba: `python3 pruebas/plataformas.py` (PL1 muro de contención, rampa y escalera; PL2 caída corta,
caja de caída y estacionamiento).

## Perfil de flujo (paso estándar) y comprobación dinámica (SWMM)

`perfil_flujo.py` calcula el nivel del agua real de cada eje por el método del paso estándar (Chow, cap. 10), en régimen mixto:
subcrítico de aguas abajo hacia arriba desde el control (descarga libre: tirante crítico; unión: nivel del agua de la cuneta que
recibe, por eso se calculan primero los ejes que reciben), supercrítico de aguas arriba hacia abajo, y en cada estación (0.5 m) el de
mayor fuerza específica; resaltos y caídas incluidos. El caudal crece a lo largo del tramo como en la verificación. Dentro del ciclo de
diseño (`motor._remansos`), donde el remanso no deja el borde libre mínimo se profundiza en lo que falta el camino hasta la descarga
(lo único que baja el nivel del agua), sin pasar del terreno exterior de la descarga; si una descarga dejara de salir se prueba con
el 75 % y el 50 %, y si no, queda como observación (comprobación 14). Se apaga con `"corregir_remansos": false`.
Salidas: línea de agua en los perfiles longitudinales (capa PERF-AGUA), hojas PERFIL DE FLUJO (con fórmulas y balance de energía) y
PERFIL DE FLUJO RESUMEN en la memoria de cálculo, capítulo «Perfil de flujo y comprobación dinámica» en la memoria hidrológica y
`perfil_flujo` en `resultado.json`.

`swmm.py` exporta la red a EPA SWMM 5 (`RED_CUNETAS_SWMM.inp`: conductos partidos en las caídas, secciones abiertas o cerradas,
áreas de aporte por tramo con Horton en las áreas verdes, hietograma de bloques alternos de `hietograma.py` con bloques del tiempo de
concentración) y, si `swmm-toolkit` está instalado (va en el motor compilado), lo corre con el motor de EPA y resume continuidad,
caudales pico por descarga, rebalses y tramos llenos (`RED_CUNETAS_SWMM.rpt`). Fuentes en la biblioteca de normas: `paso_estandar`,
`hietograma`, `swmm`.
En los tramos tapados el tirante del perfil de flujo no pasa del 80 % de la altura libre bajo la losa (`tirante_max_conducto`, CE.040,
17.6.2; con 1 se desactiva). Esta regla va solo en el perfil de flujo (comprobación 14), no en la verificación por tramo.

## Descargas sin gravedad: pozos de absorción y cámara de bombeo (`descarga_alternativa.py`)

Cuando con los niveles dados el agua no sale por gravedad por ningún lado del cerco, el motor ya no se detiene: rediseña la red con
descarga sin gravedad (CE.040, art. 21) y deja la observación con las opciones (subir el nivel de piso lo que hace falta, bombeo o
pozos). También se puede pedir desde el proyecto:

```json
"descarga_alternativa": {"tipo": "infiltracion",
                         "infiltracion": {"test_min_por_cm": 4.0, "napa_prof_m": 6.0, "FS": 3.0},
                         "bombeo": {"cota_entrega": 159.20, "L_impulsion_m": 25}}
```

- `tipo`: `infiltracion` (pozos; si el terreno no es apto pasa a bombeo) o `bombeo`. Sin `tipo`, el rediseño automático usa pozos
  si hay test de percolación y bombeo si no (`"descarga_alternativa_auto": false` lo apaga).
- Pozos de absorción (IS.020, arts. 17, 20 y 21): tasa f = 0.6/t/FS (m/h); tránsito del hidrograma de la tormenta de diseño en el pozo
  (entra Qe, sale f por la pared mojada); vaciado del 50 % en 24 h como máximo; fondo 2 m sobre la napa; D interior ≥ 1 m; 6 m entre
  pozos; t > 12 min/cm: no apto.
- Cámara de bombeo (IS.010, 6.4 y 7.1 f; OS.080): dos bombas alternadas, cada una con el caudal pico; volumen útil para ciclos de
  10 min; niveles de alarma, arranque, parada y fondo; impulsión PVC con V ≤ 2 m/s, Hazen-Williams C = 150; potencia con 60 % de
  eficiencia y 15 % de reserva.
- Con descarga sin gravedad la cuneta puede bajar hasta `prof_max_sin_gravedad` (1.50 m) para reducir el número de descargas.

Salidas: lámina de detalle (corte y planta de cada pozo, corte de cada cámara, cuadro y notas), partidas en el metrado y en las
especificaciones, hoja DESCARGA SIN GRAVEDAD (con fórmulas) en la memoria de cálculo, capítulo en la memoria hidrológica y
`descargas_sin_gravedad` en `resultado.json`. En SWMM el pozo o la cámara se representan como descarga libre (el diseño de los pozos y de
la cámara se hace aparte con el hidrograma de la tormenta). La batería de pruebas corre además una copia de S02 con pozos de absorción.

## Mapas de ubicación y lámina U-01 (`ubicacion.py`, `ubicacion_dxf.py`)

Con el cerco del plano el motor ubica el proyecto solo: pasa el centro del cerco de UTM WGS 84 a latitud y longitud (prueba las zonas
17S, 18S y 19S y se queda con la que cae dentro de un distrito; si caben varias, decide por el nombre del distrito escrito en el proyecto
y deja la observación «Confirmar la zona UTM del plano») y busca el distrito, la provincia y el departamento en los límites del INEI
(`limites_peru.json`: 1 892 distritos del Censo Nacional 2025 del INEI con su forma real —vía GEO GPS Perú—; las 196 provincias y los 25 departamentos se arman uniendo sus distritos, así los bordes coinciden; países vecinos de Natural Earth. Se rehace con `herramientas_mapas/limites_censo.py LIMITE_DISTRITAL.shp`; las geometrías van en texto compacto, enteros en 1e-5 grados con diferencias entre puntos, que leen `ubicacion.decodificar` y el visor). Si el plano no está en UTM
se usa el distrito escrito en el proyecto o el elegido en el editor.

Salidas en «Calcular todo»:
- `mapas_ubicacion/MAPA_01_PERU.png` a `MAPA_04_LOCAL.png`: Perú con el departamento, departamento con la provincia, provincia con el
  distrito y el local. El mapa 4 lleva de fondo la foto aérea del proyecto (si se dio, con sus esquinas en UTM), si no las calles de
  OpenStreetMap (con internet; quedan en caché en `_mapas_osm`), si no el plano del sitio.
- Lámina U-01 (primera del juego `PLANOS_CUNETAS.dxf`): los tres mapas, la localización a escala (la escala se elige para que el cerco
  entre en su marco) con la cuadrícula UTM verdadera, datos de ubicación, coordenadas de los vértices del cerco y notas.
- Memoria descriptiva: cuadro de ubicación con ubigeo, coordenadas UTM y geográficas, y los 4 mapas en un cuadro de 2 × 2.
- `ubicacion` en `resultado.json`.

Lo que se puede cambiar (editor de Ubicación del visor, orden `ubicacion`, o a mano en el proyecto):

```json
"ubicacion": {"zona_utm": 18, "ubigeo": "220910", "nombres": {"220910": "Morales"},
              "titulos": ["", "", "", "Mapa N° 04: Localización del local"],
              "colores": {"resaltado": "#E4572E", "recuadro": "#D90429", "cerco": "#FFD60A"},
              "foto": {"ruta": "C:/obra/foto.jpg", "fuente": "Google Earth, 2026", "xmin": 353900, "ymin": 9279892, "xmax": 354218, "ymax": 9280210},
              "osm": true, "codigo_lamina": "U-01"}
```

El distrito elegido en el editor (`ubigeo`) manda sobre las coordenadas (queda un aviso si no coinciden). Orden de escritorio:
`python -m drenie_motor ubicacion proyecto.json` con JSON por la entrada: `{"buscar": "Morales"}` lista distritos; `{"guardar": {...}}`
guarda lo editado y rehace los 4 mapas (vista previa en JPEG dentro de la respuesta). Para rearmar los límites con un límite distrital más reciente del INEI: `python herramientas_mapas/limites_censo.py distritos.shp`.

## Lluvia PISCO-SENAMHI (`lluvia_pisco.py`, orden `pisco`)

Serie de precipitación máxima en 24 h de cada mes (1981-2025) de cualquier punto del Perú, desde PISCOp v3.0 del SENAMHI
(lluvia diaria grillada de 0.1°). La base `lluvia_pisco_mensual.npz` se arma en la PC con `herramientas_lluvia/reducir_pisco.py
PISCOp_d.nc` (de https://doi.org/10.6084/m9.figshare.32411886) y va con el motor; no se sube a este repositorio.

La lluvia grillada promedia ~10 × 10 km y subestima las máximas puntuales, por eso se multiplica por el factor estación / PISCO,
interpolado (inverso de la distancia al cuadrado) entre 8 estaciones del SENAMHI de San Martín, cada factor medido en la celda
PISCO de la estación: CO Tarapoto 1.35, Pongo de Caynarachi 1.28, Chazuta 1.37, Lamas 1.57 y San Pablo 1.26 (coordenadas exactas
de la ficha del SENAMHI); Jepelacio 1.33, Sauce 1.33 y San Antonio 1.04 (ubicación aproximada en el centro de su distrito). A más
de 80 km de toda estación el factor es 1.00 y se avisa. Solo se guardan los factores; las series de las estaciones no se
reproducen. Comprobación: Tarapoto 75.0 mm de promedio de máximas anuales con PISCO corregido frente a 76.6 mm de la estación;
estimando el factor de cada estación solo con las demás, el error es de 0 a 6 % en 5 de las 8 y de 13 a 32 % en Tarapoto, Lamas
y San Antonio (variación local de la lluvia).

En DrenIE: pestaña LLUVIA → Análisis estadístico → «Lluvia PISCO-SENAMHI»: distrito o coordenadas, factor (automático o a mano),
«Traer serie» y «Cargar en la tabla de lluvias». Orden: `echo '{"ubigeo":"220910"}' | python -m drenie_motor pisco`.

## Drenaje vial MTC (`vial.py`, orden `vial`)

Drenaje de carreteras según el Manual de Hidrología, Hidráulica y Drenaje del MTC (R.D. N.° 20-2011-MTC/14). Los valores
normativos están en la biblioteca (`herramientas_normas/agregar_mtc_vial.py`, cotejados con `insumos/normas/MAN_11_HHD-2011.pdf`):

- **Período de retorno** por riesgo admisible y vida útil (Tabla N.° 02, ecuación 1): plataforma R 40 %, n 15 → T 30 años; alcantarillas
  de quebradas menores y alivios R 35 %, n 15 → T 36; quebradas importantes y badenes R 30 %, n 25 → T 71 (editables).
- **Lluvia**: la serie de la pestaña LLUVIA (análisis de frecuencias del motor) o P24 por T; intensidad de Dick y Peschke.
- **Cuencas**: C de la Tabla N.° 08 (cobertura, suelo y pendiente, ponderado), tc de la Tabla N.° 05 (Kirpich, California, Témez, SCS,
  FAA; promedio, mínimo o un método), racional (A < 10 km²) o racional modificado de Témez (10 a 770 km²).
- **Cunetas**: Manning (ecuación 117) con n de la Tabla N.° 32; capacidad = cuneta llena limitada por la velocidad de la Tabla N.° 33;
  dimensiones mínimas de la Tabla N.° 34; talud interior de la Tabla N.° 304.12; longitud máxima 250 m (200 m en región muy
  lluviosa); pendiente 0.5–2 %. Divide cada cuneta en tramos iguales y pone una **alcantarilla de alivio automática** en cada
  descarga que no tenga obra (una alcantarilla o un badén que nombra la cuneta recibe su descarga más cercana, hasta 50 m).
- **Alcantarillas**: TMC (Ø comerciales desde 36", o 48" en selva alta; hasta 3 líneas) o marco de concreto; tirante ≤ 75 % (borde
  libre 25 %); V ≥ 0.25 m/s; marco ≤ 6 m/s; enrocado de salida d50 = V²/(3.1 g) (Laushey).
- **Badenes**: canal trapezoidal en régimen uniforme, borde libre ≥ 0.30 m, pendiente transversal 2–3 %.

Entregables con `echo '{...}' | python -m drenie_motor vial CARPETA` (o `{"plantilla": "DATOS_DRENAJE_VIAL.xlsx"}`;
`{"crear_plantilla": true}` escribe la plantilla vacía): `MEMORIA_CALCULO_DRENAJE_VIAL.xlsx` (fórmulas), `MEMORIA_DRENAJE_VIAL.docx`,
`METRADO_DRENAJE_VIAL.xlsx` (planilla veces × largo × ancho × alto con fórmulas), `PLANOS_DRENAJE_VIAL.dxf` (VD-01 diagrama por
progresivas, VD-02 secciones típicas de cuneta, VD-03 alcantarillas típicas con cabezales y protección, VD-04 badenes, VD-05 cuadro
de obras de arte) con su PNG por lámina. Las medidas que el MTC no fija (cabezal, cama, relleno mínimo, protección, juntas) son
típicas editables, marcadas como criterio del proyectista. Ejemplo: `ejemplos/vial/vial_ejemplo.json`; pruebas:
`python3 pruebas/vial_pruebas.py`.
