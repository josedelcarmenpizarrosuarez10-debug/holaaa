# Proyecto: drenaje pluvial y colectores frontales – predio Los Mangos, Morales (San Martín)

Leer completo antes de trabajar. Detalle técnico en los skills de `.claude/skills/` y en `BITACORA_CONVERSACION.md`.
**Base de conocimiento completa (todo lo aprendido con el usuario, al mínimo detalle): `conocimiento/01_*.md` a `08_*.md`,
índice en el skill `conocimiento-drenaje-pluvial`. Leer el capítulo del tema antes de diseñar, dibujar, metrar o redactar.** Manual Word: `conocimiento/MANUAL_TECNICO_DRENAJE_PLUVIAL.docx` (`python3 herramientas/conocimiento_docx.py`).

## Reglas permanentes del usuario (no negociables)
- No modificar los metrados del usuario salvo pedido expreso; cambiar solo lo que se pida y verificar que lo demás quede idéntico.
- Entregables en Word, Excel y DXF; vistas previas en PNG. PDF solo cuando el usuario lo pida.
- Escala real: 1 unidad = 1 m. "Si algo mide 0.56, así debe medir en el plano."
- Decir siempre "cota de fondo". Citar los proyectos por nombre y CUI.
- Nada en los documentos que revele uso de IA. No poner nombre ni CIP del proyectista (campos en blanco).
- Partidas con nombres y estructura Delphin (base: CAR Mujeres); cantidades siempre del metrado propio.
- Precios reales con su fuente; mano de obra CAPECO-FTCCP 2026 (operario 28.95, oficial 22.68, peón 20.54).
- Todo en español. Actualizar todo lo relacionado de forma coherente (metrado ↔ planos ↔ especificaciones ↔ memoria).
- No mezclar partidas ni láminas entre proyectos.
- Estudios de gestión de riesgos de obra: sin montos en soles ni "observaciones" a documentos ajenos; efectos en % del presupuesto.
- PSST y gestión de riesgos: siempre con su matriz (IPERC o matriz de riesgos) en Excel con fórmulas y un Word ordenado con tablas y gráficos.
  El método es estándar para cualquier tipo de obra en el Perú (no solo vial o CAR). Cada tema en su carpeta: `PROGRAMA DE ELABORACION DE PSST/` (programa general, sin proyectos de ejemplo) y `gestion_riesgos/`.

## Proyectos
| Proyecto | Responsable | CUI | Colector | Carpeta de entregables | Generador |
|---|---|---|---|---|---|
| CAR Varones | Katiuska | 2705619 | b 0.60, muros 0.15, 11 registros | `entregables_varones/` | `herramientas/varones/` (`planos_v.py`, `compat.py`, `diseno_v.py`) |
| Hogar de Refugio Temporal "Mujeres Violentadas" | Solange | 2675514 | b 0.80, muros 0.15, 10 registros | `entregables/` y `entregables_solange/` | `herramientas/diseno.py`, `planos_dxf.py`, `memoria_*.py`, `metrado_*.py` |
| CAR Mujeres | Wilma | 2717013 | b 1.50, muros 0.10, 15 registros | `entregables_mujeres/` | `herramientas/mujeres/` (`datos_m.py`, `planos_m.py`, `memoria_descriptiva_m.py`, `indice_planos_m.py` = indice de los 46 planos PDF en Word, `caratulas_m.py` = las 6 caratulas en un Word) – **metrado congelado** |
| I.E. N.° 0590 Barranquita (Lamas) – planteamiento preliminar de cunetas | – | C.I. 468901 (confirmar CUI) | cunetas 0.60 (muros 0.10, libre 0.40), h inicial 0.30, S 0.5 %; borde de cuneta +184.65 al ras del NPT (área verde +184.60; al ras del patio de maniobra +184.50); acero solo con h ≥ 0.40 o tapada | `entregables_barranquita/` | `herramientas/barranquita/` (`diseno_b.py`, `verifica_b.py`, `calcula_b.py`, `planos_b.py`, `planta_cunetas_b.py`, `perfiles_b.py`, `descargas_b.py`, `excel_b.py`, `hidrologia_b.py`, `lluvia_datos_b.py`, `cantidades_b.py`, `metrado_b.py`, `memoria_calculo_b.py`, `memorias_b.py`, `espec_b.py`) – todo dentro del cerco, ejes = lineas magenta del usuario |
| Vía SM-107 Tingo de Ponasa – Shamboyacu | – | 2673852 | (estudio de gestión de riesgos de obra) | `gestion_riesgos/proyectos/SM-107_TINGO_DE_PONASA_SHAMBOYACU/` | `gestion_riesgos/herramientas/` |

Cadena hidráulica: Varones (0.60) → caja de llegada CL → Refugio (0.80) → caja de caída CC → R-01 del CAR Mujeres (1.50) → salida.

## Mapa del repositorio
- `insumos/`: archivos del usuario (no se editan; las versiones vigentes en `insumos/metrados_vigentes/` y `insumos/solange/vigente/`).
- `herramientas/`: todos los generadores (Python). Todo cambio se hace en el generador y se regenera; nunca a mano en el DXF/XLSX final.
  - Diseño y cálculo: `diseno.py` (Refugio), `metrado_calc.py`, `memoria_xlsx.py` (memoria de cálculo Excel), `memoria_docx.py` (capítulo en el Word de hidrología).
  - Planos: `dxf_base.py` (estilo, capas, rótulo, llamadas, tablas), `dxf_planta.py`, `dxf_secciones.py`, `dxf_cajas_iso.py`, `dxf_cuadros.py`, `dxf_detalles.py`, `dxf_layouts.py` (presentaciones AutoCAD e índice), `dxf_render.py` (vista previa PNG).
  - Tapa de registro: `render_tapa/` (`dxf_tapa_ciega.py` DP-06B, `dxf_tapa_3d.py` DP-06D, `modelo.py`, `iso.py`, `foto.py`), `tapa_ciega.py` (parche de planillas).
  - Especificaciones: `especificaciones/espec.py` → `_json/` → `node docx_espec.js <json> <docx>`.
  - Edición de planillas sin romper formato: `angulo_contramarco_refugio.Libro` (XML) + `recalcular()` con LibreOffice.
- `.claude/skills/`: `diseno-colector-pluvial` (criterios y decisiones de diseño), `planos-ordenados` (dibujo sin cruces), `metrado-cunetas`, `planteamiento-cunetas-terreno` (cargar DXF y curvas, cerco = límite, cuneta bajo cada caída de techo, descargas por gravedad, verificación), `psst-iperc` (plan de seguridad y salud en el trabajo).
- `MetraP/`: programa de metrados (ejecutable Windows con `build_exe.bat`).
- `herramientas/barranquita/`: I.E. 0590 Barranquita. Base del sitio en `insumos/barranquita/base_sitio.pkl` (extraída del DXF
  PLANTA_GENERAL_590_2 de 332 MB, que no se versiona; la copia real del sitio es la que está sobre las curvas C-TOPO, en UTM).
  `python3 herramientas/barranquita/calcula_b.py && python3 herramientas/barranquita/planos_b.py && python3 herramientas/barranquita/excel_b.py`
  (calcula_b: ciclo diseno <-> verificacion de 11 comprobaciones; planta_cunetas_b: cunetas en planta a escala real (rejilla celeste,
  tapada verde, flechas rojas, tapas de inspeccion; requiere shapely); cortes_b: cortes generales; descargas_b: una lamina 1/25 por
  descarga con planta, perfil e isometrico; iso_b ya no se usa: el usuario no quiere el 3D de toda la red). Quiebres a 45 grados en planta
  (chaflanes de 0.60 m en cada esquina, `diseno_b.chaflanes`), no se muestran en perfiles. Area de intervencion = dentro del cerco perimetrico (`diseno_b.CERCO`, confirmado por
  el usuario): ninguna cuneta sale del cerco; el agua sale por pase en el cimiento (D1 a D4; sin pozas).
  Expediente de drenaje (Word/Excel): `hidrologia_b.py` (serie Pmax 24 h de la estacion Pongo de Caynarachi SENAMHI 003317, 25 anios 1989-2013, sin
  transposicion; metodos de la hoja ANALISIS ESTADISTICO del usuario (CAR Varones): K-S con Weibull m/(n+1), LP3 por gamma de ln P y Kite, Gumbel con yn/sn
  de Aparicio, IDF con el modelo de Bell; adoptada Log Pearson III, T = 25: P24 169.27 mm, Dick-Peschke, I = 293.18 mm/h; Excel del analisis:
  `analisis_estadistico_b.py` (abre la plantilla `insumos/barranquita/plantillas/` con LibreOffice UNO, carga la serie y borra filas sobrantes); `coteja_analisis_b.py` compara
  cada valor de la memoria hidrologica (cuerpo y anexo) con esa hoja (1696 valores, 0 diferencias); Tarapoto transpuesta x 2.21 solo como contraste; `lluvia_datos_b.py` lee datos diarios SENAMHI / NASA POWER / CHIRPS de
  `insumos/barranquita/lluvia/` y compara sin modificar el diseno), `metrado_b.py`, `memoria_calculo_b.py`, `memorias_b.py` (memoria hidrologica y
  descriptiva; anexo de analisis estadistico en cuadros como el CAR Mujeres: `anexo_estadistico_b.py`), `espec_b.py` (motor y formato de
  `herramientas/especificaciones/espec.py` + `docx_espec.js`, codigo C.I.). Metrado en el formato del CAR Mujeres (hojas CONCRETO, ENCOFRADO, ACERO, JUNTA,
  CURADO, REJILLAS, TAPAS, PARAMETROS, Listas) con las mismas cantidades. Superficies (`hidrologia_b.superficies`): techos (caras de 0_PROYECCIONES 1 +
  patio civico y losa multiusos techados), areas libres de concreto, patio de maniobra y estacionamiento, areas verdes; C ponderado 0.761. La junta
  cuneta-piso del metrado usa `hidrologia_b.pisos_metrado` (clasificacion anterior, metrado sin cambios). Planos impresos por el usuario: NO regenerar. Sin `base_sitio.pkl`: `verifica_b.py --solo-lluvia` (cambio de lluvia sobre la geometria vigente) y caches
  `_calc/coberturas.json` (areas de techo) y `_calc/junta_piso.json` (junta con el piso por eje); los planos (`planos_b.py`) si necesitan la base.
  Regenerar con `python3 herramientas/barranquita/metrado_b.py && ... memoria_calculo_b.py && memorias_b.py && espec_b.py`.
  Caratula comun de los 6 documentos (`caratula_b.py`): foto aerea del usuario `insumos/barranquita/foto_aerea_ie0590.webp` (recortada en
  `figuras_memoria/foto_caratula.jpg`); Word por `word_b.Doc.caratula(..., clave)`, especificaciones por `J.caratula` en `docx_espec.js`, Excel por
  hoja CARÁTULA (openpyxl en metrado y calculo; UNO en el analisis estadistico). Solo las 6 caratulas en un Word:
  `python3 herramientas/barranquita/caratula_b.py` -> `CARATULAS_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx`.
  Caratula e indice de planos en un Word: `python3 herramientas/barranquita/indice_planos_b.py` (lee sin modificar el DXF impreso:
  rotulos, ejes y progresivas de perfiles, secciones por lamina) -> `CARATULA_E_INDICE_DE_PLANOS_IE0590_BARRANQUITA.docx`.
  Ejes de cuneta (v3): lineas magenta del plano "PLANTA_GENERAL_590 ULTIMA VERSION" (lados de cada bloque, techos a dos aguas),
  copiadas en `insumos/barranquita/cunetas_magenta_usuario.json`; la base del sitio (`base_sitio.pkl`) es de esa version.
- `gestion_riesgos/`: estudios de gestión de riesgos durante la ejecución de obra, separados de los colectores. `herramientas/` (generadores, con copia propia de `dxf_base.py`, `dxf_layouts.py`, `dxf_render.py`) y `proyectos/<proyecto>/insumos` y `proyectos/<proyecto>/entregables`. Ver `gestion_riesgos/README.md`.
- `PROGRAMA DE ELABORACION DE PSST/`: programa general del Plan de Seguridad y Salud en el Trabajo para todo tipo de obra (IPERC R.M. 050-2013-TR,
  Word y Excel). `herramientas/` (`biblioteca.py`, `importar_s10.py`, `generar.py`), `plantilla/DATOS_PROYECTO.xlsx`, `proyectos/<obra>/`,
  `GENERAR_PSST.bat`. Ver su `README.md` y el skill `psst-iperc`.

## Cómo regenerar (Hogar de Refugio)
```
python3 herramientas/diseno.py            # diseño hidráulico -> entregables/_calc/diseno.json
python3 herramientas/memoria_xlsx.py      # memoria de cálculo
python3 herramientas/planos_dxf.py        # juego de planos DP/DA/DD
python3 herramientas/dxf_render.py <dxf> <png> x0 y0 x1 y1 110 color   # vista previa (caja de entregables/_calc/laminas.json)
```
Refugio, sustento normativo del programa arquitectónico (RNE A.030/A.040/A.080/A.090, R.V.M. 104-2019 y 208-2019-MINEDU (cotejada con su texto, cuadro 40) y lineamientos ONU-Habitat/CONAVIM): `python3 herramientas/sustento_normativo_refugio.py` (Word + matriz Excel con fórmulas; insumos en `insumos/solange/sustento_normativo/`). Análisis de incompatibilidades de ubicación (cuadro de 18 de la arquitecta, R.V.M. 010-2022-MINEDU): `python3 herramientas/incompatibilidades_refugio.py` (Word con cuadro apaisado + matriz Excel; nota interna en `entregables/revision_interna/`).
Refugio, memoria descriptiva de arquitectura de Solange corregida (copia, mismo formato e imágenes; análisis 2.3.1/2.3.2, normativa, programa con las citas del sustento, listado de 108 láminas, índice con páginas): `python3 herramientas/corrige_memoria_arquitectura_refugio.py` -> `entregables/arquitectura/*_CORREGIDA.docx` + nota `entregables/revision_interna/REVISION_MEMORIA_ARQUITECTURA_HOGAR_REFUGIO.docx` (insumo en `insumos/solange/arquitectura/`; usa las piezas de `varones/corrige_memoria_arquitectura_v.py`).
Refugio, juego de láminas DPL que imprime la usuaria (`insumos/solange/PLANOS_DRENAJE_PLUVIAL_MUJERES_VIOLENTADAS_LAMINAS.pdf`, 42 láminas
DPL-01 a DPL-42, sin códigos repetidos; DPL-37 isométrico de lloraderos, DPL-38 detalle de lloradero, DPL-39 falsa columna, DPL-40 planta
de lloraderos, DPL-41/42 bancas OC-01): `python3 herramientas/indice_planos_refugio.py` -> índice Word de la DPL-01 a la DPL-42 con grupos
temáticos (códigos y títulos tal cual el rótulo). Metrado vigente: `insumos/metrados_vigentes/METRADO_DRENAJE_MUJERES_VIOLENTADAS_CON_BANCAS_OC-01.xlsx` (del usuario;
`bancas_oc01_en_planilla_refugio.py` ya no lo pisa). Documentos: `memoria_docx.py` (hidrológica, láminas DPL, OC-01 y lloraderos),
`especificaciones/espec.py refugio` + `node docx_espec.js`, `memoria_descriptiva_refugio.py` (nueva). Carátulas (7 en un Word, foto `insumos/solange/FOTO_PROYECTO_HOGAR_REFUGIO.jpg`): `caratulas_refugio.py` (motor de `varones/caratulas_v.py`).
CAR Varones, evacuación y señalización (plano final SE-S-01/SE-E-01 de la arquitecta en `insumos/katiuska/senalizacion/`): `herramientas/varones/senalizacion/` (`lee_plano_se.py` -> `datos_se.py` -> `metrado_se.py`, `memoria_se.py`, `espec_se.py`, `vistas_se.py`), salidas `entregables_varones/*EVACUACION_Y_SENALIZACION*`.
CAR Varones, equipamiento y mobiliario (láminas MB-01 a MB-09, `insumos/katiuska/mobiliario/`): `herramientas/varones/mobiliario/` (`lee_plano_mb.py` -> `datos_mb.py` -> `metrado_mb.py`, `memoria_mb.py`, `espec_mb.py`, `vistas_mb.py`); el metrado original del usuario solo se compara (hoja VERIFICACIÓN).
CAR Varones: `python3 herramientas/varones/planos_v.py`; plano DL-00 de ubicación de lloraderos (34 tramos, 226 und):
`python3 herramientas/planos_ubicacion_lloraderos.py varones` (ejes en `insumos/katiuska/EJES_CUNETAS_VARONES.json`; sin `varones` = Refugio).
Varones, juego de 44 láminas DPLV de la usuaria (`insumos/katiuska/PLANOS_DRENAJE_PLUVIAL_CAR_VARONES_LAMINAS.pdf`): índice
`varones/indice_planos_v.py` (mismo motor que el del Refugio; ordenado de la DPLV-01 a la DPLV-44; códigos tal cual el rótulo, incluso DPVL-09, DPVL-10, DVPL-11), memoria
hidrológica `varones/memoria_docx_v.py` (láminas DPLV, capítulo de lloraderos con su desagregado), especificaciones `espec.py varones`,
memoria descriptiva `varones/memoria_descriptiva_v.py` (reusa `memoria_descriptiva_refugio.py`). Memoria de cálculo del colector en PDF (estilo HIDRO-CE040): `varones/memoria_pdf_v.py` (lee el Excel de `varones/memoria_v.py`). Carátulas (7, todas en un Word, una por página, con la foto `insumos/katiuska/FOTO_PROYECTO_CAR_VARONES.jpg`): `varones/caratulas_v.py` -> `entregables_varones/CARATULAS_DRENAJE_PLUVIAL_CAR_VARONES.docx`. Opciones de carátula guinda (4 diseños: banda lateral, franjas, marco clásico, bloques; página 1 = vista previa): `varones/caratulas_opciones_v.py` -> `entregables_varones/OPCIONES_CARATULA_GUINDA_CAR_VARONES.docx` (pendiente que el usuario elija). Metrado vigente = el del 23-10-2026. Índices de arquitectura (Excel de la usuaria `insumos/katiuska/INDICE_DE_LAMINAS_ARQUITECTURA_CAR_VARONES.xlsx`): `varones/indice_arquitectura_v.py` -> índice general del expediente (Tomo I documentos D-01 a D-09 + Tomos II-V, 89 láminas) e índice de planos (solo las 89 láminas). Análisis de incompatibilidades de ubicación (cuadro de Katiuska en su memoria de arquitectura, R.V.M. 068-2025-MINEDU; insumos en `insumos/katiuska/arquitectura/`): `varones/incompatibilidades_v.py` (motor de `incompatibilidades_refugio.py`; Cuadro 1 de 18 + Cuadro 2 de 8 condiciones RNE/R.V.M. 208; revisión interna en `entregables_varones/revision_interna/`). Memoria descriptiva y programación de arquitectura de Katiuska corregidas (copias, mismo formato e imágenes): `varones/corrige_memoria_arquitectura_v.py` -> `entregables_varones/arquitectura/*_CORREGIDA.*` (total del programa 4,281.52 m²; cerco en ml no suma área). CAR Mujeres: `python3 herramientas/mujeres/planos_m.py`.
DP-06B suelta: `python3 herramientas/render_tapa/dxf_tapa_ciega.py <salida.dxf> <refugio|varones|mujeres>` (render: 0 0 841 594).

## Git
Rama de trabajo: `claude/colector-pluvial-hogar-refugio-ydbnaf`. Commit con mensaje claro y push con
`git push -u origin claude/colector-pluvial-hogar-refugio-ydbnaf`. No crear PR salvo pedido.
