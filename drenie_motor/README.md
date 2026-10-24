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
0.25 × 0.20 a lo largo del alero (S 1 %, n 0.013, borde libre 0.05), montantes PVC 4" por Wyly-Eaton (rs 0.25) repartidos en el
alero con su salida a la cuneta más cercana (aviso si no hay a menos de 3 m) y metrado con las reglas de la planilla del usuario
(soportes @0.60 + 1, 2 tapas, 1 boquilla por montante, 3 codos de 90, 2 colgadores, abrazaderas cada 4 m). Altura del alero por
techo en `altura_alero` (`{"defecto": 3.50, "techos": [{"punto": [x, y], "altura": 7.00}]}`); parámetros en `techo_parametros`.
Se dibujan en la DC-01 (bloque CANALETAS_Y_MONTANTES) y su cuadro va en la DC-02. Montantes: en las esquinas de la
edificación (2 por lado), siempre 4", editables en el visor (MT).
Sumideros (`sumideros.py`): solo en áreas libres sin cobertura (`sumidero_tipos`, por defecto patio y estacionamiento), donde la
zona queda a más de 8 m de una cuneta; tubo PVC 4" recto a la cuneta (S 1 %, llega sobre la cota de fondo); editables en el
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
