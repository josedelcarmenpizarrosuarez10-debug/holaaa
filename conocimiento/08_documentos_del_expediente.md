# 08 — Documentos del expediente y sus formatos

Base de conocimiento permanente (vigente al 24-10-2026). Recoge cómo se arman, con qué formato y con qué datos, todos los
documentos escritos del expediente de drenaje pluvial: memoria hidrológica, memoria descriptiva, memoria de cálculo (Excel y
PDF), análisis estadístico, especificaciones técnicas, índice de planos y carátulas. Incluye cada corrección o decisión del
usuario con su fecha y el porqué de cada regla.

Fuentes: mensajes del usuario (03-10 a 24-10-2026), `BITACORA_CONVERSACION.md`, `CLAUDE.md`, skills de `.claude/skills/` y los
generadores de `herramientas/` (se citan por ruta). Los planos DXF (estilo, láminas, presentaciones) son de otro tema; aquí
solo se tocan en lo que alimentan a los documentos (imágenes de láminas, índice, rótulos).

Nota sobre nombres: en los documentos nunca se cita a personas; los proyectos se citan por nombre y CUI. Algunas carpetas de
`insumos/` tienen nombres internos; se mencionan solo como rutas.

---

## 1. Mapa de documentos por proyecto

### 1.1 Proyectos y códigos

| Proyecto | Código | Carpeta de entregables | Juego de láminas del usuario |
|---|---|---|---|
| Hogar de Refugio Temporal "Mujeres Violentadas" | CUI 2675514 | `entregables/` | DPL-01 a DPL-42 (PDF que imprime la usuaria) |
| CAR Varones | CUI 2705619 | `entregables_varones/` | DPLV-01 a DPLV-44 (PDF final) |
| CAR Mujeres | CUI 2717013 | `entregables_mujeres/` | 46 PDF "PLANOS_ANDFY_MUJERES" (códigos RGDPLV-01, ST-CG, D-RL, etc.) |
| I.E. N.° 0590 Barranquita | C.I. N.° 468901 (confirmar si es CUI) | `entregables_barranquita/` | DC-01 a DC-19 (DXF impreso, no se regenera) |

### 1.2 Documentos, generadores y archivos de salida

| Documento | Refugio (2675514) | Varones (2705619) | Mujeres (2717013) | Barranquita (C.I. 468901) |
|---|---|---|---|---|
| Memoria hidrológica (Word) | `memoria_docx.py` → `MEMORIA_HIDROLOGIA_MUJERES_VIOLENTADAS_2026_CON_COLECTOR.docx` | `varones/memoria_docx_v.py` → `MEMORIA_HIDROLOGICA_VARONES_CON_COLECTOR.docx` | `revision_hidrologia.py` → `MEMORIA_HIDROLOGICA_CAR_MUJERES_CON_COLECTOR.docx` (copia revisada) | `memorias_b.py` + `hidrologica_doc_b.py` + `anexo_estadistico_b.py` → `MEMORIA_HIDROLOGICA_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx` |
| Memoria descriptiva (Word) | `memoria_descriptiva_refugio.py` (19 pág.) | `varones/memoria_descriptiva_v.py` (17 pág.) | `mujeres/memoria_descriptiva_m.py` (23 pág., 14 capítulos) | `memorias_b.py` (función `descriptiva`) |
| Memoria de cálculo del colector (Excel) | `memoria_xlsx.py` → `MEMORIA_CALCULO_COLECTOR_HOGAR_REFUGIO.xlsx` | `varones/memoria_v.py` → `MEMORIA_CALCULO_COLECTOR_CAR_VARONES.xlsx` | libro del usuario `insumos/wilma/MEMORIA_CALCULO_COLECTOR_CAR_MUJERES_3_PROYECTOS.xlsx` | `memoria_calculo_b.py` → `MEMORIA_CALCULO_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.xlsx` (red de cunetas) |
| Memoria de cálculo del colector (PDF HIDRO-CE040) | `memoria_pdf_refugio.py` (18 pág.) | `varones/memoria_pdf_v.py` (17 pág.) | `mujeres/memoria_pdf_m.py` (12 pág.) | – |
| Análisis estadístico (Excel, plantilla del usuario) | – (dato del estudio del proyecto) | – | – | `analisis_estadistico_b.py` → `ANALISIS_ESTADISTICO_IE0590_BARRANQUITA.xlsx` |
| Especificaciones técnicas (Word) | `especificaciones/espec.py refugio` + `docx_espec.js` (50 pág.) | `espec.py varones` + `docx_espec.js` | `espec.py mujeres` + `docx_espec.js` | `espec_b.py` (mismo motor; 20 pág.) |
| Índice de planos (Word) | `indice_planos_refugio.py` → `INDICE_DE_PLANOS_DRENAJE_PLUVIAL_HOGAR_REFUGIO.docx` | `varones/indice_planos_v.py` → `INDICE_DE_PLANOS_DRENAJE_PLUVIAL_CAR_VARONES.docx` | `mujeres/indice_planos_m.py` → `INDICE_DE_PLANOS_DRENAJE_PLUVIAL_CAR_MUJERES.docx` | `indice_planos_b.py` → `CARATULA_E_INDICE_DE_PLANOS_IE0590_BARRANQUITA.docx` |
| Carátulas (un solo Word) | `caratulas_refugio.py` → `CARATULAS_DRENAJE_PLUVIAL_HOGAR_REFUGIO.docx` (7) | `varones/caratulas_v.py` → `CARATULAS_DRENAJE_PLUVIAL_CAR_VARONES.docx` (7) | `mujeres/caratulas_m.py` → `CARATULAS_DRENAJE_PLUVIAL_CAR_MUJERES.docx` (6) | `caratula_b.py` → `CARATULAS_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx` (6) |

Otros documentos que existen como archivo pero sin generador en el repositorio: `MEMORIA_DESCRIPTIVA_GENERAL_CAR_MUJERES.docx` y
`MEMORIA_DESCRIPTIVA_DESCRIPCION_DEL_PROYECTO_CAR_MUJERES.docx` (trabajo del 05-10-2026, ver §5.6).

---

## 2. Reglas generales de los documentos (permanentes)

1. **Todo en español.** El 14-10-2026 el usuario reclamó: "¿por qué todo escribes en inglés?". Textos, nombres de hojas,
   rótulos, comentarios visibles y mensajes: en español.
2. **Nada que revele uso de IA.** Redacción formal de expediente técnico; sin frases tipo "como modelo", sin marcas de
   herramientas. Propiedades del Word: `core_properties.author = ''` (y `last_modified_by = ''`, `comments = ''` donde aplica).
3. **Sin nombre ni CIP del proyectista** (08-10-2026: "el nombre cip no pongas nada"). Donde va firma: campos en blanco
   (`Profesional responsable: ______ · CIP ______ · Firma: ______`).
4. **Proyectos por nombre y CUI**, nunca por persona. En los textos de un proyecto, el aguas arriba es "aporte externo" (dato de
   su memoria, sin validarlo) y el aguas abajo es "receptor".
5. **No mezclar proyectos.** Cada documento solo con partidas, láminas y datos de su propio proyecto. Al reutilizar un motor
   entre proyectos, los textos fijos pasan a parámetros y se comprueba que el otro proyecto queda idéntico (por ejemplo, el XML de
   las carátulas de Varones quedó idéntico al parametrizar el color para el Refugio).
6. **Decir "cota de fondo"** (no "invert"). Cotas en msnm; progresivas `0+000.00`.
7. **Cantidades siempre del metrado vigente del usuario** (hoja RESUMEN y hojas de detalle, en solo lectura). Ningún documento
   recalcula ni "corrige" un metrado. Metrados vigentes: `insumos/metrados_vigentes/`.
8. **Códigos y títulos de lámina tal cual el rótulo del PDF del usuario** (aunque tengan erratas, por ejemplo DPVL-09, DVPL-11,
   "CONTRUCTIVO"); el usuario decidió dejarlos así el 23-10-2026.
9. **Sin observaciones a documentos ajenos** dentro de los entregables (las diferencias se informan al usuario en el chat, no se
   escriben en el índice o la memoria). Regla nacida el 22-10-2026 con el índice del Refugio (ver §10.6).
10. **Formatos de entrega:** Word y Excel; vistas previas en PNG; PDF solo cuando el usuario lo pide (lo pidió para las
    memorias de cálculo del colector, estilo HIDRO-CE040).
11. **Todo cambio se hace en el generador y se regenera**; nunca a mano en el Word/Excel final. Los insumos del usuario no se
    editan: se trabaja sobre copia (temporal o en `entregables*/`).
12. **Coherencia total:** un cambio de diseño se propaga a metrado ↔ planos ↔ especificaciones ↔ memorias ↔ carátulas e índice.
    Después de cada cambio se compara el texto antes y después y se confirma que solo cambió lo pedido.
13. **"Documento irrefutable"** (03-10-2026, 16:48): el usuario pidió que la memoria quede "bajo normas, que después la
    Contraloría no intervenga". De ahí salen el cuadro de cumplimiento normativo (requisito, norma, criterio, valor, resultado),
    la sección "Datos de otros expedientes y cómo quedan cubiertos" y la cita de la norma en cada criterio.
14. **No pedirle trabajo al usuario** (03-10-2026, 16:55: "eso que me pides para yo hacer hazlo tú o déjalo así"): los
    pendientes se resuelven con criterio y se dejan documentados como hipótesis cubierta.

---

## 3. Estilos Word comunes (técnica python-docx)

### 3.1 Paleta por proyecto

| Uso | Color (hex) | Dónde |
|---|---|---|
| Granate (CAR Varones, índices, memorias descriptivas Refugio/Varones/Mujeres) | `7B1E2B` | títulos, encabezado de tabla, franja de carátula, bordes |
| Granate claro (fila de grupo, fila total) | `F2E6E8` / `F3E6E8` | índices y memoria descriptiva |
| Subtítulo en franja granate | `F2D7DB` | carátulas Varones y Mujeres |
| Verde (carátulas del Hogar de Refugio) | `1E5E3B`, subtítulo `D6EEDD` | pedido del 23-10-2026 |
| Azul Barranquita | `1F3A68`, claro `D9E2F3` | carátula, Word de memorias, índice |
| Azul especificaciones | `1F3864`, encabezado de tabla `D9E2F3` | `docx_espec.js` |
| Azul del capítulo del colector (memoria hidrológica) | `1F4E79` con texto blanco | encabezado de tablas |
| Gris de texto secundario | `595959` | fuentes, leyendas, notas |
| Gris de tabla (memoria descriptiva del CAR Mujeres) | `D9D9D9` encabezado, `F2F2F2` total | plantilla IISS |

### 3.2 Fuentes y tamaños

| Documento | Fuente | Cuerpo | Títulos |
|---|---|---|---|
| Capítulo del colector en la memoria hidrológica (Refugio, Varones) | Arial Narrow (runs con `w:rFonts` ascii/hAnsi/cs) | 12 pt, interlineado 1.5, sangría izquierda 1.75 cm, justificado, 6 pt después | Heading 1 / Heading 2 del documento original con su numeración automática (lista `numId 1`, niveles 0 y 1) |
| Memoria descriptiva Refugio y Varones | Arial Narrow | 11 pt, interlineado 1.15 | H1 13 pt granate negrita (12 pt antes, 6 después); H2 11.5 pt granate |
| Memoria descriptiva CAR Mujeres | Swis721 Cn BT (de la plantilla IISS del proyecto) | estilo de la plantilla | estilos copiados de párrafos modelo de la plantilla |
| Memorias de Barranquita (`word_b.Doc`) | Arial | 10.5 pt, interlineado 1.15, 6 pt después | H1 13, H2 11.5, H3 10.5 pt, negrita, azul `1F3A68` |
| Especificaciones (`docx_espec.js`) | Arial | 10 pt (size 20) | H1 13 pt centrado azul; H2 11 pt azul; H3 10.5; H4 10; H5 10 cursiva |
| Índice de planos | Arial | 9 pt (Normal) | "ÍNDICE DE PLANOS" 15 pt granate |
| Carátulas | Arial | – | entidad 15-17 pt, título de la franja 20-26 pt |

### 3.3 Tablas

- Estilo `Table Grid`, centradas, `autofit = False`; anchos fijados en `w:gridCol` (1 cm = 567 twips) y en cada celda.
  `w:tblLayout type="fixed"` cuando se necesita que el ancho no cambie.
- **Encabezado repetido** en cada página: `w:tblHeader val="true"` en el `trPr` de la primera fila.
- **Filas que no se parten** entre páginas: `w:cantSplit` en cada fila (índices de planos).
- **Tablas cortas que no se separan**: `keep_with_next` en todos los párrafos de las filas excepto la última (opción `junta=True`
  en `memoria_docx.tabla`; en la memoria descriptiva, automático si la tabla tiene 12 filas o menos).
- Encabezado sombreado (`w:shd fill`) con texto blanco en negrita; fila TOTAL en negrita con fondo claro.
- Alineación: primera columna (o columnas de texto) a la izquierda; números centrados.
- Cuando se agrega `w:shd` a una celda que ya tiene `w:vAlign`, se inserta **antes** de `vAlign` (orden del esquema de Word);
  `caratulas_m._poner_en_orden()` respeta el orden de `tcPr` y `tblPr` para que Word no reporte el archivo como dañado.

### 3.4 Numeración de tablas y figuras, leyendas y fuentes

- Capítulo agregado a la memoria hidrológica: continúa la numeración del documento del usuario con `Numerador(tabla=22, imagen=5)`:
  "Tabla N° 22", "Imagen N° 05"... Leyenda **debajo** de la tabla, en negrita 11 pt centrada con `keep_with_next`; debajo
  "Fuente: Elaboración propia." en cursiva 10 pt (o la hoja de la memoria de cálculo que sustenta el dato). En las imágenes la
  leyenda va **arriba** de la imagen y la fuente debajo.
- Memoria descriptiva (Refugio, Varones): "Tabla N.° 01: ..." 10 pt negrita centrada **arriba** de la tabla; "Figura N.° 01: ...
  (lámina COD)" arriba de la imagen; fuente 9 pt cursiva gris (`Fuente: Lámina COD del expediente de drenaje pluvial.`).
- Memoria descriptiva del CAR Mujeres: "Tabla N.° xx" arriba; la figura va primero y la leyenda debajo.
- Barranquita (`word_b`): "Tabla N° 01. ..." 9 pt negrita arriba; "Figura N° 01. ..." 9 pt debajo de la imagen con la fuente en
  la misma línea (8 pt cursiva).

### 3.5 Encabezado, pie, índice (TOC) y secciones

- Encabezado con texto corto del proyecto + CUI + especialidad, con borde inferior (`w:pBdr/w:bottom`, sz 8, color del proyecto).
  Ejemplos: "MEMORIA DESCRIPTIVA - DRENAJE PLUVIAL | HOGAR DE REFUGIO TEMPORAL - CUI N.° 2675514" (8.5 pt granate);
  "HOGAR DE REFUGIO TEMPORAL - MORALES, SAN MARTÍN | CUI N.° 2675514 | DRENAJE PLUVIAL" (índice, 7.5 pt).
- Pie con número de página por campos `PAGE` y `NUMPAGES` construidos con `w:fldChar begin/separate/end` + `w:instrText`.
- La carátula queda en una sección propia sin encabezado; el cuerpo en una sección nueva (`WD_SECTION.NEW_PAGE`) con
  `w:pgNumType start="1"` y encabezado/pie no vinculados (`is_linked_to_previous = False`). En Barranquita:
  `different_first_page_header_footer = True`.
- Índice automático: campo `TOC \o "1-2" \h \z \u` con texto provisional "Actualice el índice (clic derecho > Actualizar campos)"
  y `w:updateFields val="true"` en `settings` para que Word lo actualice al abrir. En especificaciones: `TableOfContents` de la
  librería docx (niveles 1-4, con hipervínculos) y `features.updateFields`.
- **Índice con páginas en dos pasadas** (memoria descriptiva del CAR Mujeres): 1) se genera el Word; 2) se convierte a PDF con
  LibreOffice (`soffice --headless --convert-to pdf`); 3) se busca con `pdftotext -layout` la página de cada capítulo
  (`^N. TÍTULO$`); 4) se regenera el Word con el TOC rehecho (hipervínculo al marcador `_TocDPnn` y `PAGEREF`), ya con las páginas.
- **Contenido en dos pasadas** (Barranquita): una primera pasada del generador recolecta los títulos numerados y la segunda
  escribe la carátula, la lista "CONTENIDO" (sangría 0.6 cm por nivel) y el cuerpo.
- Salto de página: párrafo con `add_break(WD_BREAK.PAGE)` o `page_break_before = True`.

---

## 4. Memoria hidrológica

### 4.1 Principio rector (03-10-2026)

"Capítulo del colector agregado AL FINAL del estudio hidrológico, en Word, sin alterar las páginas anteriores." Se abre el Word
del usuario (`insumos/.../MEMORIA_HIDROLOGI*.docx`), se agrega una sección nueva vertical con los márgenes, tamaño de página y
distancias de encabezado/pie de la primera sección del documento, y se escribe el capítulo con los estilos ya existentes
(Heading 1, Heading 2, List Paragraph, Normal, Table Grid). El original nunca se modifica: la salida va a `entregables*/`.

### 4.2 Estructura del estudio original (igual en los proyectos de Morales)

1. Aspectos generales. 2. Estudio hidrológico. 3. Cálculo de caudales en el área del proyecto. 4. Drenaje. 5. Conclusiones.
6. Recomendaciones. 7. Anexos. Luego, agregados:
8. **COLECTOR PLUVIAL FRONTAL: TRAMO HOGAR DE REFUGIO TEMPORAL** (Varones: "TRAMO CAR VARONES Y EMPALME CON EL HOGAR DE REFUGIO").
9. **DRENAJE COMPLEMENTARIO**: Refugio "TECHOS DE LAS BANCAS CON PÉRGOLA (OC-01) Y LLORADEROS EN CUNETAS"; Varones "LLORADEROS EN
   CUNETAS COLINDANTES CON ÁREA VERDE".

Estado de los Word: Refugio 18 secciones, 49 tablas, 26 imágenes; Varones 18 secciones, 48 tablas, 22 imágenes.

### 4.3 Capítulo del colector: subtítulos en orden (`memoria_docx.construir`)

| N.° | Subtítulo (Heading 2) | Contenido | Dato de origen |
|---|---|---|---|
| 1 | Alcance del tramo | qué recibe (aporte externo), qué entrega (receptor), condiciones de compatibilidad en viñetas: cota de fondo de llegada ≥ cota de fondo del R-01, Q ≤ 560.7 L/s, entrega subcrítica | `diseno.json` |
| 2 | Trazo y emplazamiento | eje a 0.575 m del cerco, losa = vereda NPT, junta solo contra el cerco, quiebres 45°, cruces (OE-01 4.415 m de camiones, portón de motos 1.77 m), UTM referencial | `diseno.json`; tabla "Registros, cajas y puntos singulares"; figura DPL-06 |
| 3 | Caudal de diseño del tramo | Dick-Peschke, I = 155.66 mm/h (tc 15 min), explicación de 35.16 mm / 210.98 mm/h para cunetas; Q = Σ(C·A)·I·FS/3600; tabla de aportes | DATOS/CAUDALES |
| 4 | Dimensionamiento hidráulico de la sección | b, muros, losas, n, CF inicial, S ‰; Manning yn, V, F; yc; llenado y borde libre | perfil |
| 5 | Perfil de flujo | paso estándar desde el control aguas abajo (caída libre, tirante crítico), perfil M2; tabla cada 5 m más quiebre y brink | hoja PERFIL_FLUJO |
| 6 | Velocidades y autolimpieza | CE.040 0.90 a 3.0 m/s; esfuerzo tractivo ≥ 0.15 kg/m² con caudales parciales (hasta 5 %); tabla de casos; figura DPL-07 | PERFIL_FLUJO recalculada |
| 7 | Empalme con el colector receptor: caja de caída CC | resalto ahogado; tabla de verificación (11 filas: CF del brink, yc, piso de poza, caída, E1, y1/V1, F1, y2, tirante disponible, verificación, longitud de poza ≥ 0.8·6 y2) | hoja EMPALME |
| 8 | Caja de llegada CL del aporte externo | dimensiones, ventanas (este 0.60 × 1.17, norte 0.40 × 0.66), tapa al piso del proyecto vecino, poza y colchón; figura DPL-26 | DATOS |
| 9 | Llegada de las cunetas del proyecto | ventana 0.40 × H, caída libre, prolongaciones metradas en partidas de cunetas (no en el colector); tabla de empalmes | hoja CUNETAS |
| 10 | Verificación estructural | marco cerrado, E.020, HL-93 + 33 % impacto, E.060; tres armados; tabla Mu/φMn/Vu/φVc por elemento A a H; presión al suelo; figura DPL-14 | hoja ESTRUCTURAL recalculada |
| 11 | Marco normativo del diseño | viñetas: CE.040 (R.M. 126-2021-VIVIENDA, reemplaza a OS.060), E.020, E.060 (9.7.2, 14.3.4), Manual de Hidrología MTC, Manual de Puentes MTC / AASHTO LRFD, E.050 | – |
| 12 | Criterios constructivos | colector cubierto sin lloraderos, registros ≤ 12 m con tapa ciega, juntas, empalmes, concretos, excavación; remite a láminas DPL; figura DPL-27 | parámetros del metrado (`metrado_calc`) |
| 13 | Resumen de metrados del tramo | partidas `01.04.04.*` con unidad del RESUMEN vigente | RESUMEN del metrado vigente |
| 14 | Cuadro de cumplimiento normativo | requisito, norma, criterio, valor, resultado (todo "CUMPLE") | hoja CUMPLIMIENTO |
| 15 | Datos de otros expedientes y cómo quedan cubiertos | viñetas: llegada del aporte externo, caudal externo con margen de capacidad, capacidad portante, UTM, cotas de cunetas | hoja CUMPLIMIENTO (bloque final) |
| 16 | Conclusiones del tramo | 6 viñetas con números del diseño | – |

Varones (`memoria_docx_v.py`, mismo motor importando `memoria_docx`): "Caudal de diseño y su reparto entre las cunetas", "Perfil de
flujo con caudal creciente", "Llegada de las cunetas y acortamiento en el frente", "Empalme con la caja de llegada CL del Hogar de
Refugio"; tabla de metrados con 12 partidas leídas por código del RESUMEN vigente; figuras DPLV-17, DPLV-18, DPLV-21, DPLV-25 y
DPLV-35 (la bitácora registra además referencias a DPLV-23 y DPLV-25 a 30 en el texto).

### 4.4 Formato del capítulo

- `parrafo()`: Arial Narrow 12, justificado, interlineado 1.5, 6 pt después, sangría izquierda 1.75 cm.
- `titulo1/titulo2`: estilos Heading 1/Heading 2 del documento + numeración automática `numPr` (`ilvl` 0/1, `numId` 1) insertada
  después de `pStyle`, para que el capítulo siga la numeración del estudio (8, 8.1, 8.2...).
- `vineta()`: List Paragraph, sangría 2.5 cm con primera línea −0.5 cm, "•  ".
- `formula()`: centrada, cursiva, 6 pt después (por ejemplo `Q = (1/n) · A · R^(2/3) · S^(1/2) → yn = ...`).
- `tabla()`: encabezado `1F4E79` texto blanco negrita; cuerpo 9-10 pt; números con 2 decimales salvo formato propio.

### 4.5 Figuras de láminas tomadas del PDF del usuario

Decisión del 22-10-2026: las figuras de la memoria son **las láminas del PDF que imprime el usuario**, no renders propios. Así la
memoria muestra exactamente lo que se imprime y los códigos coinciden con el índice.

Algoritmo (`memoria_docx.lamina(cod)` y `memoria_descriptiva_refugio.figura_lamina(cod)`):
1. Leer `entregables/_calc/indice_planos.json` (lo escribe el generador del índice) y obtener la página del PDF de esa lámina.
2. Si existe: `pdftoppm -f pag -l pag -singlefile -jpeg -jpegopt quality=85 -scale-to 2200 <PDF> <FIG>/<COD>` (cache: si ya existe
   el JPG no se vuelve a extraer).
3. Si la lámina no está en el PDF: usar la vista previa PNG de su DXF (caso OC-01 antes de entrar al juego DPL).
4. Insertar a 15.5 cm de ancho con leyenda "Imagen N° xx: <texto> (lámina COD)." y fuente "Fuente: Lámina COD del expediente de
   drenaje pluvial."

CAR Mujeres (memoria descriptiva): figuras **recortadas sin rótulo** desde los PDF individuales: `pdftoppm -png -r <dpi>` y recorte
por fracciones de la hoja `(x0, y0, x1, y1)`, máximo 2400 px de ancho, JPG calidad 88. Tabla de recortes en
`memoria_descriptiva_m.FIGURAS` (RGDPLV-01 55 dpi; PCPLV-01 75; STP-CG 120; D-RL 90; D-ECC 120; ESDAE-01 95). Se ejecuta con
`python3 herramientas/mujeres/memoria_descriptiva_m.py figuras <carpeta_pdf>`.

### 4.6 Capítulo complementario

**Refugio — bancas con pérgola OC-01** (22-10-2026): 3 juegos × 3 techos a una agua (3.79, 4.21 y 3.79 m × 2.40 m) = 9 techos;
canaleta de plancha galvanizada e = 0.50 mm, 0.18 × 0.21 m, S = 0.5 %, boquilla en lugar del sumidero cúpula, bajada PVC Ø 4".
Método racional con C 0.88, I 210.98 mm/h, FS 1.15; Manning n 0.013; bajada por Wyly-Eaton `Q = 1.754 · rs^(5/3) · D^(8/3)` con
rs = 0.25. Tabla por techo (L, área, Q, y, V, Froude, borde libre, D req., D adoptado 4"), resultado Q < 0.6 L/s y tirante del
orden de 0.01 m, D req. 1.59" → 4". Tabla de metrado 01.04.03.05.04.* desde el RESUMEN. Figuras DPL-41 y DPL-42.

**Lloraderos** (Refugio 157 und; Varones 34 tramos, 226 und): por qué (empuje hidrostático del agua infiltrada en el jardín
contra el muro), tubo PVC Ø 3" cada 1.50 m con filtro de grava en geotextil; no cambian el dimensionamiento de las cunetas (el agua
infiltrada ya está en el C de áreas verdes). Tabla de tramos (eje, progresivas, lado, longitud, N.°) desde la hoja METRADO
LLORADEROS. Varones agrega la tabla de materiales de la hoja DESAGREGADO LLORADEROS (componente, und, por lloradero, N.°, total) y
remite a la ACU LLORADEROS (S/ 20.56 por und). Láminas: Refugio DPL-40 ubicación, DPL-38 detalle, DPL-37 isométrico; Varones
DPLV-43, DPLV-35, DPLV-34.

### 4.7 Revisión coordinada de las tres memorias (`revision_hidrologia.py`, 20-10-2026)

Pedido: "debes explicar bien, detallar por qué cambias de 210 a 155 ... las 3 memorias hidrológicas sin errores deben coincidir
cada una". Script idempotente (si encuentra la marca no repite), solo textos, ningún valor de diseño:

1. Bloque común "Intensidad de diseño: 210.98 mm/h en cunetas y 155.66 mm/h en el colector", insertado después de la tabla de
   caudales del colector (ancla distinta por proyecto). Contenido: misma lluvia P24 = 121.81 mm (estación CO Tarapoto, Log-Normal,
   TR 25); `P_D = P24 · (D/1440)^0.25`, `I_D = P_D · 60 / D`; D = 10 min → P10 35.16 mm, I10 210.98 mm/h; D = 15 min → I15 155.66
   mm/h; CE.040: la duración es el tiempo de concentración, mínimo 10 min; tc del colector = 10 (entrada) + 3 (cuneta) + 2
   (colector) = 15 min; usar 210.98 en el colector daría un caudal 35.5 % mayor sin sustento. Coeficiente ponderado por
   proyecto (Varones 0.771, Refugio 0.807, Mujeres 0.704) y caudales compartidos (258.7 + 301.9 = 560.7 L/s al R-01; total 822.9 L/s).
2. "Coeficiente adoptado": C = 0.88 solo para canaletas, montantes, sumideros y cunetas; el colector con C ponderado.
3. Porcentaje de la plantilla ("7,2 %" en las tres) corregido a 25,0 % (Mujeres), 9,0 % (Refugio), 14,2 % (Varones).
4. Varones: su caudal 258.7 L/s es con I = 155.66 (tc 15 min), no con 210.98.
5. Área del CAR Varones 6 752.03 m² (no 6 752.06); C del Refugio 0.807 (no 0.808) en la tabla del CAR Mujeres.
6. CAR Mujeres: códigos de lámina nuevos (DP-04 → ST-CG-01/02, DP-06A → STP-CG, DP-07 → ESDAE-01, DP-09 → IC-01), párrafo de la
   tapa ciega según D-RL (0.68 × 0.68 × 0.08 en rebaje 0.70 × 0.70 × 0.08, 2 asas 1/2", borde 0.15 × 0.10, unos 89 kg), "asentadas
   en su rebaje", y rangos del perfil completo (Froude 0.51-0.74, V 1.02-1.43 m/s, borde libre mínimo 0.091 m).

Técnica de edición: `_texto()` deja un solo run (el primero con texto conserva el formato); `_clon()` copia un párrafo modelo
(cuerpo o fórmula centrada) y lo inserta después del ancla. Así el texto nuevo hereda la fuente del documento del usuario.
La memoria del CAR Mujeres se guarda como copia en `entregables_mujeres/` (el insumo no se toca).

### 4.8 Verificación de no alteración

`memoria_docx.verificar()`: compara el texto de todos los párrafos y tablas del original con los primeros del documento nuevo
(`pa == pb[:len(pa)]`) e imprime "párrafos originales N (iguales: True)", tablas nuevas, secciones e imágenes antes y después.
Se corre siempre al final de la generación.

### 4.9 Memoria hidrológica de Barranquita

- 21-10-2026: el usuario reclamó "por qué tan pocas páginas ... ¿acaso no tienes de los CAR el ejemplo?" y pidió datos recientes
  (2024-2025). Se rehízo con la estructura de los estudios de Morales (`hidrologica_doc_b.memoria`, 29 páginas): 1 Aspectos generales
  (introducción, objetivos, ubicación política y acceso, ubicación hidrográfica, clima de 5 estaciones, estación de referencia);
  2 Estudio hidrológico (introducción, metodología, análisis estadístico, representatividad de la serie, intensidades, análisis de
  frecuencia, pruebas de bondad de ajuste, evaluación del ajuste, curvas IDF, tiempo de concentración, período de retorno,
  intensidad máxima de diseño); 3 Cálculo de caudales (coeficiente de escorrentía, áreas de drenaje, áreas de techo, intensidad,
  caudales); 4 Drenaje (edificaciones, parámetros, canaletas y montantes, cunetas, cunetas cubiertas, juntas, profundidad,
  verificación hidráulica, descargas, presentación de los cálculos); 5 Conclusiones; 6 Recomendaciones; 7 Anexos (N.° 01 análisis
  estadístico y tormenta de diseño; N.° 02 planta y perfil típico).
- Anexo N.° 01 (`anexo_estadistico_b.py`) con los cuadros del estudio del CAR Mujeres: cada hoja lleva Proyecto / Entidad /
  Ubicación / Fecha; Parte I: A registro de Pmax 24 h, B.1 Normal, B.2 Log Normal, B.3 Log Pearson III, B.4 Gumbel, C K-S y C.4
  resumen; Parte II: A parámetros (Cuadros N.° 04 a 06, modelo de Bell y regresión), B intensidades I = K·T^m/t^n, C intensidades de
  diseño T = 25. Clase `Hoja`: tabla tipo hoja de cálculo (celdas por fila/columna, combinaciones, fondo `D9E2F3`/`FFF2CC`/`F2F2F2`)
  que se vuelca a Word.
- `coteja_analisis_b.py` (21-10-2026, pregunta del usuario "¿te fijaste que los cálculos de la memoria coincidan con el nuevo
  análisis estadístico?"): compara 1 696 valores (1 002 del cuerpo y 694 del anexo) contra el Excel del análisis a la precisión
  impresa (tolerancia = media unidad del último decimal impreso). Resultado: 0 diferencias. Ignora la tabla de 1 × 1 de la franja de
  carátula.

---

## 5. Memoria descriptiva

### 5.1 Historia y pedidos

- 05-10-2026 (CAR Mujeres, memoria descriptiva **general** del expediente): ver §5.6.
- 20-10-2026: "ármame una memoria descriptiva" del CAR Mujeres (drenaje pluvial) → `mujeres/memoria_descriptiva_m.py`.
- 22-10-2026: "actualiza la memoria descriptiva o créala" (Hogar de Refugio) → `memoria_descriptiva_refugio.py`, documento nuevo
  porque el proyecto no tenía memoria descriptiva de la especialidad; misma estructura que la del CAR Mujeres.
- 23-10-2026: CAR Varones → `varones/memoria_descriptiva_v.py`, reutiliza la clase y los lectores del Refugio.

### 5.2 CAR Mujeres (plantilla del proyecto)

- Parte del Word de instalaciones sanitarias del mismo proyecto (`insumos/wilma/MEMORIA_IISS_CAR_MUJERES.docx`, solo lectura):
  conserva carátula, bloque de información, estilos, logos y encabezado. Reemplazos exactos: "INSTALACIONES SANITARIAS" → "DRENAJE
  PLUVIAL" (cuerpo), el encabezado con la errata "INSTALACIONES SANITARAS SANITARIAS" → "DRENAJE PLUVIAL"; párrafo de servicio →
  "SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL EXPEDIENTE TÉCNICO DE PI:"; título → "MEMORIA DESCRIPTIVA DE DRENAJE
  PLUVIAL".
- Clase `Escritor`: copia párrafos modelo de la plantilla (h1, subtítulo, cuerpo, viñeta, vacío), limpia sus runs y escribe el
  texto; `**x**` marca negritas; inserta antes del `sectPr` final; marcadores `_TocDPnn` en cada capítulo; `keepNext` en títulos y
  leyendas. Los capítulos 1 (Antecedentes, con Introducción y Normas) y 2 (Ubicación) vienen de la plantilla con su texto
  reescrito.
- Capítulos: 1 Antecedentes; 2 Ubicación; 3 Finalidad y objetivos; 4 Situación actual; 5 Parámetros y criterios de diseño (tablas
  de parámetros y de superficies/coeficientes); 6 Descripción del sistema (esquema general, canaletas, montantes y falsas columnas,
  drenaje de techos de jardineras y bancas, sumideros y red de piso, cunetas por eje); 7 Colector pluvial frontal (descripción,
  secciones, registros, empalmes, juntas, funcionamiento hidráulico con caudal acumulado y perfil de cotas, estructura de salida,
  verificación estructural); 8 Aportes de proyectos colindantes; 9 Metas físicas; 10 Operación y mantenimiento; 11 Conclusiones;
  12 Recomendaciones; 13 Relación de planos; 14 Anexos (01 estudio hidrológico con el capítulo del colector, 02 memoria de cálculo del
  colector, 03 especificaciones, 04 metrado, 05 planos). Resultado: 14 capítulos, 12 tablas, 6 figuras, 23 páginas.
- Datos: memoria hidrológica revisada, 46 planos (`insumos/wilma/LISTA_PLANOS_ANDFY_MUJERES.txt`), metrado vigente
  `entregables_mujeres/METRADO_DRENAJE_PLUVIAL_CAR_MUJERES_09-10-2026_CON_BANCAS.xlsx` (RESUMEN `1.4.4*` y hojas por eje).
- Índice con páginas reales en dos pasadas (§3.5). Tablas: 9 pt, encabezado `D9D9D9`, total `F2F2F2`, layout fijo.
- Correcciones posteriores (20-10-2026): el cruce de la Carretera Oasis (badén o alcantarilla) queda fuera del alcance, con
  recomendación de comunicarlo a la entidad de la vía; Froude 0.51-0.74, V 1.02-1.43 m/s, borde libre mínimo 0.091 m.

### 5.3 Hogar de Refugio y CAR Varones (`memoria_descriptiva_refugio.Memoria`)

- Documento creado desde cero con python-docx: A4, márgenes 3.0 / 2.0 / 2.5 / 2.0 cm (izquierdo, derecho, superior, inferior),
  Arial Narrow 11, H1 13 pt y H2 11.5 pt granate; títulos numerados por el propio generador ("1.  TÍTULO", "1.1  Subtítulo").
- Carátula propia del documento (`caratula()`): "GERENCIA TERRITORIAL BAJO MAYO" 16 pt granate; "DIRECCIÓN DE INFRAESTRUCTURA"
  11 pt gris con borde inferior granate; "PROYECTO:"; nombre del proyecto entre comillas tomado de la fila PROYECTO del RESUMEN del
  metrado (sin el sufijo "con CUI"); "CUI N.° ..." 12 pt granate; imagen de la lámina de red general (DPL-01 / DPLV-01) a 10.5 cm de
  alto con su leyenda; franja granate "MEMORIA DESCRIPTIVA" 22 pt blanco y "ESPECIALIDAD: INSTALACIONES SANITARIAS - DRENAJE
  PLUVIAL" 12 pt; ubicación; fecha (Refugio OCTUBRE 2026; Varones SETIEMBRE 2026, cambiado el 23-10-2026).
- Encabezado en la sección del cuerpo, numeración desde 1, índice TOC con actualización automática, y luego los capítulos.
- Capítulos (Refugio): 1 Información del proyecto (tabla de datos generales: unidad ejecutora, proyecto, CUI, ubicación,
  especialidad, componentes 01.04.03 y 01.04.04); 2 Antecedentes (Introducción; Normas aplicables: CE.040 R.M. 126-2021-VIVIENDA,
  IS.010, E.020, E.050, E.060, Manual de Hidrología MTC, AASHTO LRFD / Manual de Puentes, G.050 y D.S. 011-2019-TR); 3 Ubicación
  (tabla de ubicación política); 4 Finalidad y objetivos; 5 Parámetros y criterios de diseño (tabla de parámetros: TR, P10/P20, I10
  210.98, I15 155.66, FS 1.15, C por superficie, n, pendientes, Ø 4" Wyly-Eaton, llenado 85 % / borde libre 0.05 m; tabla de área y
  C ponderado); 6 Descripción del sistema (esquema general + DPL-01, canaletas, montantes y falsas columnas, techos OC-01 + DPL-41,
  sumideros y red de piso, cunetas con tabla por eje desde la hoja CONCRETO EN CUNETAS, lloraderos con tabla de tramos + DPL-40);
  7 Colector pluvial frontal (descripción + DPL-06, secciones + DPL-14, registros + tabla de puntos singulares + DPL-24, empalmes con
  tabla, caja de llegada y caja de caída + DPL-26, juntas, funcionamiento hidráulico, verificación estructural); 8 Aportes de
  proyectos colindantes (tabla de caudales); 9 Metas físicas (dos tablas: 01.04.03 y 01.04.04, todas las partidas del RESUMEN);
  10 Operación y mantenimiento; 11 Conclusiones; 12 Recomendaciones; 13 Relación de planos.
- Varones: mismos capítulos con "Empalme con la caja de llegada CL" y capítulo 8 "ENTREGA AL PROYECTO COLINDANTE"; figuras DPLV-01,
  DPLV-43, DPLV-17, DPLV-21, DPLV-23, DPLV-25.
- Cantidades en el texto con la función `q(item)`: 2 decimales y unidad para m, m², m³, kg; entero para und. Nunca se escriben a
  mano: todo sale del RESUMEN vigente.

### 5.4 Relación de planos (capítulo final de la memoria descriptiva)

Tabla "Relación de planos de drenaje pluvial" (N.°, lámina, descripción, formato) leída de `_calc/indice_planos.json`, es decir,
**en el mismo orden y con los mismos códigos que el índice de planos** (Refugio DPL-01 a DPL-42; Varones DPLV-01 a DPLV-44 en orden
de número desde el 23-10-2026). Fuente: "Índice de planos de drenaje pluvial (láminas DPL-01 a DPL-42)". CAR Mujeres: N.°, lámina,
descripción de los 46 planos.

### 5.5 Barranquita

`memorias_b.descriptiva`: 1 Generalidades (nombre del proyecto, entidad y modalidad, antecedentes, objetivo); 2 Ubicación y accesos;
3 Características del terreno y del clima; 4 Descripción del sistema (criterios de diseño, red de cunetas, descargas); 5 Metas
físicas; 6 Normas técnicas; 7 Relación de planos (lámina, contenido, escala desde `_calc/indice.json`). Los textos de ubicación se
limpian de coordenadas (`limpio()` quita "x = 820.1", etc.).

### 5.6 Memoria descriptiva general del CAR Mujeres (05-10-2026)

Pedido: completar la memoria descriptiva general del expediente (descripción del proyecto, componentes, metas físicas y ambientes)
a partir de los DXF y del resumen ejecutivo. Instrucciones del usuario que siguen valiendo para cualquier memoria general:
- Usar solo información real de planos y documentos; no inventar ambientes, áreas, acabados ni metas; si falta un dato, avisar
  aparte; nunca escribir "completar" o "insertar".
- Mostrar primero un cuadro resumen por bloque y nivel (ambiente – área – NPT) para validar la lectura.
- Organizar por componentes: infraestructura por bloque, obras exteriores, instalaciones (solo lo que aparece en planos), cuadro de
  áreas (techada por bloque, total, libre), metas físicas en formato de expediente.
- "Muy poco son 13 páginas, debe ser mucho más: 45, 50 o 60".
- Arquitectura **antes** del drenaje; el drenaje "mínimo, no quiero que se note mucho"; del estudio de suelos, cantera, diseño de
  mezcla y resistividad, solo lo que corresponde a una memoria general; también sanitarias y topografía.
- Respetar numeración, estructura y estilo del Word del usuario si lo adjunta.

---

## 6. Memoria de cálculo del colector en Excel

### 6.1 Origen y pedido

03-10-2026: "Memoria de cálculo en Excel con fórmulas: datos, caudales, perfil de flujo y verificación estructural", con las
mismas hojas y convenciones que la memoria del tramo CAR Mujeres. Regla del usuario: Excel en español (REDONDEAR, SUMA, SI con
separador ";"). Técnica: openpyxl guarda las fórmulas con nombres en inglés (SUM, IF, ROUND...) y separador ","; Excel en español
las muestra traducidas con ";".

### 6.2 Hojas (Refugio: `memoria_xlsx.py`)

| Hoja | Contenido |
|---|---|
| MEMORIA (primera) | 1 Objeto, 2 Normativa, 3 Hidrología, 4 Hidráulica, 5 Estructuras, 6 Resultados (texto en columna B, alto de fila 42); cuadro resumen con vínculos verdes (Q, I, b, S %, CF inicial/final, llenado, borde libre, Froude, estaciones que no cumplen, velocidades, cunetas con caída libre, resalto, elementos estructurales y requisitos que no cumplen); NOTAS |
| DATOS | parámetro, valor, und, fuente/criterio, símbolo; grupos HIDROLOGÍA, GEOMETRÍA, CRITERIOS DE VERIFICACIÓN, RECEPTOR, APORTE EXTERNO, CAJAS; incluye la fila aclaratoria "Intensidad para D = 10 min = P10 × 60/10 = 210.98 mm/h: es la misma lluvia de 35.163 mm en 10 min" y la nota de por qué el colector usa 155.66 |
| CAUDALES | proyecto, área, C×A, C ponderado, I, Q, punto de ingreso, fuente; total entregado al receptor; caudal adoptado; caudal acumulado por punto (CL + 6 cunetas, reparto nominal); nota "suma de picos sin desfase y FS 1.15: hipótesis conservadora" |
| CUNETAS | cuneta, perfil, progresiva, longitud, NCT, NCF al cerco, H, prolongación, NCF en el muro (`=F−0.005·H`), NA del colector (INDEX/MATCH sobre PERFIL_FLUJO), caída libre, verificación "CAIDA LIBRE"/"AHOGADA" |
| EMPALME | A. caja de caída CC (yc, piso de poza, caída, E1, y1, V1, F1, y2, tirante disponible, verificación del resalto, longitud de poza); B. caja de llegada CL (caída del aporte externo, colchón ≥ 0.50 m) |
| PERFIL_FLUJO | paso estándar desde el brink; columnas progresiva, cota de fondo, Q, b, yc, y, NA, V, Froude, cota bajo losa, h, y/h, borde libre, verificación, zona; resumen (llenado máx., borde libre mín., Froude máx., estaciones que no cumplen, NA en 0+000); verificación de velocidades y autolimpieza para 7 casos (diseño, solo aporte externo, solo propio, 50, 25, 10 y 5 %) |
| ESTRUCTURAL | parámetros (f'c, fy, pesos, Ko, sobrecargas, ruedas, IM, huella, luz de cálculo, H máx./mín.) y bloques A losa tramo normal, B losa cruce de motos, C losa cruce de camiones, D/E/F muros por zona, G losa de fondo y presión al suelo, H tapa de registro; cada uno con Mu, d, As, a, φMn y "CUMPLE"/"NO CUMPLE" |
| CUMPLIMIENTO | requisito, norma/referencia, criterio, valor (fórmula, verde), resultado; grupos hidrología e hidráulica, entrega al receptor, estructuras, constructivos; conteo de "NO CUMPLE*" + "VERIFICAR*"; bloque "DATOS DE OTROS EXPEDIENTES Y CÓMO QUEDAN CUBIERTOS" (5 párrafos) |

Varones (`varones/memoria_v.py`): MEMORIA, DATOS, CAUDALES (por cuneta y en el colector), CUNETAS (acortamiento y caída libre),
EMPALME_CL, PERFIL_FLUJO (caudal creciente), ESTRUCTURAL, CUMPLIMIENTO ("condiciones de compatibilidad entre los tres expedientes").
CAR Mujeres: libro del usuario con MEMORIA, DATOS, CAUDALES, SALIDA (vertido sobre la cresta y control), PERFIL_FLUJO, ESTRUCTURAL.

### 6.3 Convenciones de formato

| Elemento | Formato |
|---|---|
| Dato editable | Arial 9, azul `0000FF` |
| Fórmula | Arial 9, negro |
| Vínculo a otra hoja | Arial 9, verde `008000` |
| Encabezado de tabla y filas de grupo | negrita, relleno gris `EEEEEE`, borde fino `999999`, centrado con ajuste de texto |
| Título de hoja (A1) | Arial 12 negrita, numerado ("1. DATOS DE DISENO") |
| Subtítulo (A2) | Arial 9 cursiva gris `555555`: tramo, proyecto con CUI, ubicación, fecha |
| Leyenda de colores | al pie de DATOS: "Azul = dato editable; negro = fórmula; verde = vínculo." |
| Cuadrícula | oculta en todas las hojas; paneles inmovilizados (DATOS/CUMPLIMIENTO en A5, PERFIL_FLUJO en B6) |

Los textos del libro van sin tildes (compatibilidad); el PDF las agrega (§7.4).

### 6.4 Técnicas de fórmulas que conviene copiar

- **Referencias por símbolo:** cada fila de DATOS se registra con su símbolo (`ROW['b']`); las demás hojas se escriben con filas
  provisionales y al guardar se traducen con una expresión regular `DATOS!(\$?)B(\$?)(\d+)` → fila real. Así se puede agregar una
  fila en DATOS sin romper nada.
- **ESTRUCTURAL con claves:** las fórmulas se escriben con `{clave}` (por ejemplo `={wA}*{Lc}^2/8`) y se reemplazan por `B<fila>` al
  final; la tabla `KEY` también la usa CUMPLIMIENTO.
- **Paso estándar en Excel sin macros:** el tirante de cada estación se resuelve por bisección en 30 iteraciones en columnas
  auxiliares (P en adelante, pares lo/hi) con la función de energía `f(y) = y + V²/2g + z − E2 − Δx (Sf + Sf2)/2`.
- **Tirante normal por punto fijo** en 8 iteraciones: `y(k+1) = (Q n (b + 2 y(k))^(2/3) / (b^(5/3) S^(1/2)))^(3/5)`.
- **Valores que no se resuelven con fórmula simple** (y1 al pie de la caída): se calcula en Python, se escribe en azul como dato y se
  agrega una fila de verificación con fórmula (`y1 + V1²/2g` debe ser igual a E1).
- Celdas fijas de enlace (`PERFIL_FLUJO!G200` = NA en 0+000; `B200` = verificación global de velocidades) para que otras hojas
  apunten a una dirección estable.
- Recalcular con LibreOffice (`soffice --headless --convert-to xlsx`) antes de leer valores con openpyxl `data_only=True` (los
  generadores de Word y PDF trabajan sobre esa copia recalculada, nunca sobre el entregable).

### 6.5 Memoria de cálculo de Barranquita (red de cunetas)

`memoria_calculo_b.py`: hojas CARÁTULA, RESUMEN, DATOS, SERIE (Pmax 24 h Pongo de Caynarachi 1989-2013), FRECUENCIAS (Normal,
Log-Normal, Log-Pearson III, Gumbel), KS, IDF (modelo de Bell y regresión I = K·T^m/t^n; Dick-Peschke para el diseño), SUPERFICIES
(4 tipos y detalle por zona), CAUDALES (racional y Manning por tramo) y DESCARGAS. Formato: cabecera en filas 1 a 3 (título 11 pt
negrita; PROYECTO; ENTIDAD - UBICACIÓN - FECHA en 8 pt); encabezados de tabla con relleno `DDEBF7`; datos en negrita sobre amarillo
`FFF2CC`; valores de diseño sobre verde `E2EFDA`; fila gris `F2F2F2`; bordes finos `808080`. DATOS con 4 coeficientes de escorrentía
(techos, áreas libres de concreto, patio de maniobra y estacionamiento, áreas verdes) y FS en B22. El 21-10-2026 el usuario envió esta
misma memoria como "su formato" ("hazlo así tal cual mi formato") y pidió no alterar planos ya impresos.

---

## 7. Memoria de cálculo en PDF, estilo HIDRO-CE040

### 7.1 Pedidos

- 15-10-2026: "Te paso la memoria de cálculo de CAR Mujeres ... quiero que le des otro estilo visual en PDF"; adjuntó el ejemplo
  `MEMORIA_DE_CALCULO_-_CAR_MUJERES.pdf` (memoria HIDRO-CE040) y el Excel del colector → `mujeres/memoria_pdf_m.py`.
- 15-10-2026: "A este también dale en PDF así con el estilo que ya vimos" (Refugio) → `memoria_pdf_refugio.py`.
- 20-10-2026: "Revisa si está bien" la del CAR Mujeres → "Procede, corrige".
- 23-10-2026: "Hazle el Excel de colector igual que el PDF de cálculo de Varones" (adjuntó `MEMORIA_DE_CALCULO_VARONES.pdf`) →
  `varones/memoria_pdf_v.py`. El Excel que envió la usuaria era una versión anterior (mismos números, 5 textos distintos): se usó el
  vigente del repositorio.

### 7.2 Motor

1. Copiar el Excel a una carpeta temporal (el entregable o el insumo no se tocan); aplicar correcciones de coherencia sobre la copia
   (solo CAR Mujeres, §7.5).
2. Recalcular con LibreOffice y leer con openpyxl `data_only=True`.
3. Armar HTML: cada hoja se transforma en una sección con tablas; los valores se copian **sin cambiarlos**; solo se da formato.
4. Imprimir a PDF A4 con Chromium por Playwright de Node (`p.pdf({format:'A4', printBackground:true, preferCSSPageSize:true,
   displayHeaderFooter:true, headerTemplate, footerTemplate})`); el script `pdf.js` se escribe en temporal y se ejecuta con `node`.
5. Borrar temporales.

Los tres generadores comparten piezas: `memoria_pdf_m` (CSS, `tabla`, `formulas`, `fmt`, `tilde`, `PDF_JS`) ← `memoria_pdf_refugio`
(tildes adicionales, `perfil_svg` con marcas según el rango, `tabla_param`) ← `varones/memoria_pdf_v`.

### 7.3 Estilo visual (CSS)

| Elemento | Valor |
|---|---|
| Página | A4, márgenes 15 / 14 / 17 / 14 mm |
| Cuerpo | Liberation Sans / Arial 9.6 pt, color `#1d2329`, interlineado 1.42 |
| Título h1 | serif (DejaVu Serif / Georgia) 21 pt, negrita, `#11161b`: "Memoria de cálculo del colector pluvial frontal" |
| Línea del proyecto | 7.9 pt `#4b555e` (nombre completo, CUI, ubicación, mes y año) |
| Meta | 9.4 pt: "TRAMO ... · 0+000 a 0+xxx.xx · recibe / entrega ... · RNE CE.040" |
| h2 | 12.2 pt, número de sección en verde azulado `#2a6f73` |
| Recuadro de fórmulas | fondo `#eef3f6`, serif 9.6 pt, subíndices y superíndices, no se parte entre páginas |
| Tablas | 8.7 pt; encabezado celeste `#e9f1f5` con borde `#d3dee5`; celdas con borde `#dfe7ec`; encabezado repetido (`thead` como table-header-group); filas que no se parten |
| Fila de grupo | fondo `#f5f8fa`, texto `#2a6f73` negrita |
| Tabla de perfil | 7.1 pt, números a la derecha |
| Distintivo CUMPLE / NO CUMPLE | `#e3f3ea` / `#1e6b43` y `#fbe4e4` / `#9b1c1c`, pastilla redondeada |
| Bloque final | borde izquierdo de 4 px `#2a6f73` ("Resultados de la verificación", "Diseño adoptado", cuadro conjunto) |
| KPI | 4 tarjetas en grilla, valor serif 12.5 pt, fondo `#f5f8fa` |
| Gráfico del perfil (SVG) | fondo `#5b6670` 2 px; techo disponible `#9aa6ad` discontinuo; nivel de agua `#2b8cbf`; relleno de agua `#cfe8f3`; grilla `#e3eaee`; leyenda debajo |
| Firma | línea superior `#c9d3d9`: "Profesional responsable: ____ · CIP ____ · Firma: ____" en blanco |
| Encabezado y pie | 7 px `#7a858d`: izquierda "Memoria de cálculo · Colector pluvial frontal · <proyecto> (CUI ...)", derecha "Drenaje pluvial · RNE CE.040"; pie: tramo y progresivas / "N / total" |

### 7.4 Contenido y transformaciones

- Secciones (Refugio y Varones): Datos y metodología (KPIs: caudal, llenado máx., borde libre mín., Froude máx.; párrafos de la hoja
  MEMORIA; tabla de resultados; notas); 1 Datos de diseño; 2 Caudales (método racional); 3 Cunetas que llegan al colector (Varones:
  acortamiento y caída libre); 4 Cajas / empalme con la CL; 5 Perfil de flujo (gráfico SVG + tabla de todas las estaciones + resumen +
  velocidades y autolimpieza; Varones 110 estaciones); 6 Verificación estructural (un bloque por elemento + cuadro conjunto); 7 Cuadro
  de cumplimiento normativo; Diseño adoptado; referencia normativa; firma en blanco. CAR Mujeres: 3 Condición de control en la salida,
  4 Perfil, 5 Estructural, cuadro conjunto y diseño adoptado.
- **Tildes:** el libro no tiene tildes; el diccionario `TILDES` (palabras completas con `\b`) y `FRASES` las agregan (cálculo,
  diseño, sección, caída, régimen...). Unidades m2/m3 → m²/m³; `^2` → ²; `>=` → ≥; `fMn` → φMn; `tau = gamma R S` → τ = γ R S.
- **Referencias a celdas → referencias a secciones:** "(hoja PERFIL_FLUJO)" → "(sección 5)"; "B14 + B15^2/19.62 = B13" → texto sin
  celdas; "Ver cuadro resumen y la hoja CUMPLIMIENTO" → "Ver «Resultados de la verificación» y el cuadro de la sección 7".
- `fmt()`: enteros sin decimales; cotas entre 250 y 300 msnm con 3 decimales (al milímetro); ≥ 100 con 2; ≥ 1 con 3; < 0.01 con 4.

### 7.5 Correcciones de coherencia (CAR Mujeres, 20-10-2026, sobre copia temporal)

- Área del CAR Varones 6 752.03 m² (la de su memoria hidrológica; el caudal no cambia porque sale de C×A).
- Sin nombres de personas en la tabla de caudales (se quitan los paréntesis con nombres).
- Estación del quiebre vereda / tramo final en 0+078.42 (el libro la tenía en 78.47).
- Fecha setiembre 2026. Resultado: 12 páginas.
- Refugio (23-10-2026): al regenerar, solo cambió el área de Varones 6 752.03. Varones: fecha setiembre 2026 (rótulos).

---

## 8. Análisis estadístico en Excel con la plantilla del usuario

### 8.1 Pedido y plantilla

21-10-2026: el usuario envió `ANALISIS_ESTADISTICO - CAR VARONES.xlsx`: "así quiero el análisis estadístico". Copia en
`insumos/barranquita/plantillas/ANALISIS_ESTADISTICO_-_CAR_VARONES.xlsx`. Hojas de la plantilla (nombres tal cual, incluida la
errata): "A. Estación", "B.Modelo Distribución", "C. Prueba Kolmorov-Smirnov", "D.Resumen", "A. Parametros", "B. Int.maxima",
"C. P diseño" (más auxiliares "Hoja1" y "210").

### 8.2 Procedimiento (`analisis_estadistico_b.py`, LibreOffice UNO)

1. Levantar LibreOffice sin interfaz con socket (`--accept=socket,host=localhost,port=2083;urp;`, perfil temporal) y abrir la
   plantilla oculta.
2. Escribir proyecto, entidad, ubicación y fecha (C2:C5), título del registro (B9), datos de la estación (código, tipo, altura,
   departamento, provincia, distrito) y periodo (B15).
3. Cargar la serie (años y 12 meses desde la fila 18; "S/D" donde falta, con el mismo color de resaltado que usaba la plantilla).
4. Columna "Diseño" del resumen (L10:L18) = distribución que elige la prueba K-S de la misma hoja (`IF` anidado sobre la celda del
   resultado G55); resaltar esa columna en lugar de la Log-Normal fija.
5. Corregir `MAX(Z22:Z45)` a todo el rango (`Z22:Z47`: la plantilla dejaba fuera los dos últimos datos).
6. Cambiar títulos de gráficos ("CO TARAPOTO" → nombre de la estación).
7. **Borrar las filas sobrantes** (plantilla de 26 años; la serie tiene 25): al borrar filas con `Rows.removeByIndex`, LibreOffice
   ajusta solo las fórmulas y los rangos de los gráficos. Nunca se reescriben fórmulas a mano.
8. Quitar "Hoja1" y "210"; agregar la hoja CARÁTULA (UNO); `calculateAll()`; guardar como "Calc MS Excel 2007 XML".
9. `comprobar()`: la hoja y `hidrologia_b.py` deben dar lo mismo (distribución elegida, D de K-S, D crítico, P24 T25, K, m, n, I).

Resultado vigente: K-S elige Log Pearson III (D 0.0683; crítico 0.2650): P24 T25 169.27 mm, I = 293.18 mm/h (tc 10 min), IDF
K 211.66, m 0.1786, n 0.5269. Con los datos del CAR Varones, el método reproduce la hoja del usuario (D 0.0920 / 0.0894 / 0.0964 /
0.1270; K 161.94, m 0.1786, n 0.5271).

Métodos de la hoja replicados en Python: z de Abramowitz-Stegun, KT de LP3 de Kite, K-S con probabilidad de excedencia m/(n+1) y
serie de mayor a menor, LP3 por gamma de ln P, Gumbel con yn/sn de Aparicio, D crítico por fórmula, IDF por modelo de Bell
(P60(10) = 0.4602 · P24(10)^0.876; intensidades redondeadas a 0.1).

---

## 9. Especificaciones técnicas (Word)

### 9.1 Pedido (08-10-2026)

"Me faltan las especificaciones tal cual completito de todo ... de cada uno, sigue normativas peruanas, al más mínimo detalle cómo se
construirá" + "Revísalo antes de presentarlo; tú ya sabes qué dicen los planos". Se hicieron para los tres CAR desde la hoja RESUMEN
de cada metrado vigente; luego Barranquita con el mismo motor.

### 9.2 Motor

`especificaciones/espec.py <proyecto>` → `_json/<proyecto>.json` → `node docx_espec.js <json> <docx>`.
- Partidas: código, descripción y unidad de la hoja RESUMEN, en el mismo orden; **no se agregan ni se quitan partidas**. Los
  títulos (sin unidad) agrupan y no tienen medición ni pago.
- Nivel del título = número de segmentos del código menos el mínimo (H2 a H5); los títulos de primer nivel abren página.
- Datos constructivos de cada proyecto en el diccionario `PROYECTOS` (dimensiones del colector, n.° de registros y juntas, acero,
  recubrimientos, receptor, cajas, cerco sí/no, vereda, láminas, contramarco, tipo de sello) y de las hojas de parámetros del metrado.
- Pase de tildes al final (`acentos()`): el texto se redacta sin tildes y se acentúa por diccionario (`_MAP`), futuros
  ("sera" → "será") y terminaciones "-cion"/"-sion".
- Mapeo `laminas` por proyecto: reemplaza los códigos de trabajo (DP-06B, DD-03, DJ-03...) por los del juego del usuario (DPL-24,
  DPL-28; DPLV-23, DPLV-29, DPLV-33...). Con cadena vacía se quitan citas a láminas que no existen en ese juego.

### 9.3 Estructura

1. Portada (CAR): entidad, "EXPEDIENTE TÉCNICO", "ESPECIFICACIONES TÉCNICAS" 20 pt azul, especialidad, proyecto, CUI, ubicación,
   fecha SETIEMBRE 2026. Barranquita: si el JSON trae `caratula`, la portada es la carátula común con foto (§11.4) y el código es
   `J.codigo` ("C.I. N.° 468901").
2. ÍNDICE (TOC niveles 1-4).
3. CAPÍTULO I. GENERALIDADES: generalidades (alcance, numeración = metrado), ubicación y clima (ACI 305R), normas aplicables (RNE
   OS.060, CE.040, IS.010, E.020, E.050, E.060, E.090, G.050, D.S. 011-2019-TR, Norma Técnica de Metrados RD 073-2010-VIVIENDA, NTP
   334.009, 400.037, 339.088, 341.031, 339.036, 339.035, 339.033, 339.034, 339.141, 339.143, 399.003; ASTM A615, A36, A653, A123, C920,
   D2564; AWS D1.1 y A5.1; ACI 318, 301, 304R, 305R, 308R, 347), orden de prevalencia (planos, especificaciones, memoria de cálculo,
   metrado; discrepancias al cuaderno de obra), materiales (tabla material / requisito / norma) y demás capítulos generales.
4. CAPÍTULO II. ESPECIFICACIONES TÉCNICAS POR PARTIDA: "código  descripción  (und)" y, en cada partida, apartados en negrita azul
   9.5 pt: DESCRIPCIÓN, MATERIALES, EQUIPOS Y HERRAMIENTAS, PROCEDIMIENTO DE EJECUCIÓN, CONTROL DE CALIDAD Y TOLERANCIAS, SEGURIDAD Y
   SALUD EN EL TRABAJO (EPP, G.050, D.S. 011-2019-TR; bloques tipo para excavación, concreto, acero, soldadura, trabajo en altura),
   apartados extra (por ejemplo cuadro de materiales del lloradero), UNIDAD DE MEDIDA, MÉTODO DE MEDICIÓN, FORMA DE PAGO (texto tipo:
   precio unitario por la unidad, compensación total de mano de obra con leyes sociales, materiales, equipo, herramientas,
   transporte interno e imprevistos).

### 9.4 Formato (`docx_espec.js`)

- A4 (11906 × 16838 twips); márgenes superior 2.5 cm, inferior 2.0 cm, izquierdo 3.0 cm, derecho 2.0 cm; encabezado y pie a 1 cm.
- Arial 10; párrafos justificados, interlineado 276 (1.15), 100 twips después.
- Encabezado: "ESPECIFICACIONES TÉCNICAS - DRENAJE PLUVIAL" (7.5 pt negrita azul) y, con tabulación a la derecha, "<corto> - CUI N.°
  ..."; borde inferior azul. Pie: "Página X de Y" a la derecha, 8 pt.
- Tablas: ancho total 9071 twips; pesos de columnas 3 col [26, 50, 24] %, 5 col [44, 8, 17, 15, 16] %; encabezado repetido
  `D9E2F3`; bordes `808080`; 8.5 pt.
- Viñetas con numeración "vinetas" (sangría 567, colgante 284).

### 9.5 Contenidos clave y correcciones

- Juntas del colector del Refugio (14 y 15-10-2026): tecnopor 1" + sellador asfáltico 1" × 2" (RC-250 + arena), EG-2013 MTC 510;
  junta longitudinal solo contra el cimiento del cerco (al otro lado hay terreno natural). Junta de cunetas en toda la sección en U
  (2 × H + 0.40). Rejilla móvil (módulo 1.00 m, 39 platinas 1" × 3/16" @1"). CAR Varones conservó el sello de poliuretano en un
  momento y luego pasó al sellador asfáltico en todas las juntas (15-10-2026, tarde).
- Tapa ciega de concreto armado (16-10-2026) en los textos de registros.
- Lloraderos (08-10 y 23-10-2026): la partida lleva el cuadro de materiales del desagregado (Varones: tubo PVC 3" 67.80 m, 1 808
  perforaciones, grava 6.71 m³, geotextil 134.24 m², mortero 0.11 m³) y las láminas de ubicación, detalle e isométrico.
- Bancas OC-01 del Refugio: 4 partidas 01.04.03.05.04 con texto propio (`espec_bancas`).
- 23-10-2026: en el Refugio se quitaron dos citas a láminas DJ-01/DJ-02 y DJ-03 que no existen en su juego DPL (son del CAR
  Varones); solo cambiaron esos 2 párrafos. Vigentes: metrado con bancas, láminas DPL, 50 páginas.
- Barranquita (21-10-2026): mismo motor, código C.I., carátula con foto; 20 páginas; partidas del metrado propio (estructura Delphin
  del CAR Mujeres).

---

## 10. Índice de planos

### 10.1 Pedidos

- 08-10-2026: "déjalo en layout de AutoCAD ... y también me das un índice de láminas" → índice DP-00 dentro del DXF (A3) y
  presentaciones (tema de planos).
- 21-10-2026: Barranquita "índice de planos y carátula de planos en un solo Word"; CAR Mujeres "índice de planos en Word según el
  PDF de planos último".
- 22-10-2026: Refugio "en un Word aparte dame índice de planos". Corrección del mismo día (ver §10.6).
- 23-10-2026: CAR Varones índice; "el índice debes arreglarlo, ordénalo de la lámina uno a la última sucesivamente".
- 23-10-2026: Refugio "revisa si está bien este índice, si coincide con los planos" + PDF de las láminas que imprime (42).

### 10.2 Lectura del PDF del usuario (sin modificarlo)

Refugio y Varones (`indice_planos_refugio.leer_pdf`):
1. `pdfinfo -f 1 -l 999` → formato de cada página por el tamaño ISO entre paréntesis ("(A1)").
2. Por página, `pdftotext -raw`. En el rótulo: la línea que contiene el CUI, seguida del título y de una línea que empieza con
   "COORDINADOR"; el título son las líneas entre ambas. Después, la primera línea que termina en un año (20dd); la siguiente es la
   escala del rótulo ("INDICADA") y la siguiente el **código del rótulo**.
3. El código se toma tal cual del rótulo; el título se valida contra el diccionario `TITULOS` (con tildes) comparando en forma
   "llana" (mayúsculas sin tildes ni espacios, solo `A-Z0-9.,:()+`). Si no coincide, el programa se detiene con "Título distinto en
   <cód>": no se inventa ni se corrige.
4. Escalas de los dibujos: todas las coincidencias `ESC(ALA)?.?:? 1/n` de la página, sin repetir, ordenadas.
5. Contenido que distingue láminas de igual título, leído de los dibujos (`contenido()`): secciones "SECCION nn" (rango), progresivas
   `0+000.00` (desde/hasta), cortes "CORTE A-A", ejes, tramos. Refugio: DPL-02 "CUNETAS, CON LAS SECCIONES 01 A nn"; DPL-03 a 05
   "SECCIONES ..."; DPL-07 a 09 "PROGRESIVAS ..."; DPL-10 a 13 progresivas con su zona; DPL-14 texto fijo de secciones típicas;
   DPL-15 a 23 cortes; DPL-41/42 texto fijo de la OC-01.
6. Se guarda `_calc/indice_planos.json` (código, título, contenido, formato, escala, escalas de dibujo, página, rótulo). Ese JSON
   lo usan la memoria hidrológica (página de cada figura), la memoria descriptiva (relación de planos y figuras) y la
   especificación.

CAR Mujeres (`mujeres/indice_planos_m.py <carpeta>`): un PDF por lámina; el orden y los códigos salen de
`LISTA_PLANOS_ANDFY_MUJERES.txt` (archivo | código); el título del rótulo debe **terminar** con el título del diccionario; contador
para el código repetido DI-CBCB (láminas 45 y 46, informado al usuario fuera del documento). Sin argumento, arma el Word desde el JSON.

Barranquita (`indice_planos_b.py`): lee el DXF impreso (sin modificarlo) con ezdxf: lista de láminas de `_calc/indice.json` (mismo
cuadro de la DC-00), caja de cada lámina de `_calc/laminas.json`, subtítulo del rótulo (textos a la altura de "PLANO:"), ejes y
progresivas de cada perfil ("PERFIL LONGITUDINAL EJE-nn - ... - PROG. a A b"), número de secciones por eje, eje de salida de cada
descarga.

### 10.3 Formato del Word del índice (Refugio y Varones)

- A4 vertical, márgenes 2.0 / 1.6 / 2.0 / 1.6 cm (izquierdo, derecho, superior, inferior); Normal Arial 9.
- Encabezado: "<PROYECTO CORTO> | CUI N.° ... | DRENAJE PLUVIAL" 7.5 pt granate con borde inferior; pie "Página X de Y".
- Cabecera: "GERENCIA TERRITORIAL BAJO MAYO - DIRECCIÓN DE INFRAESTRUCTURA" 9 pt gris; "PROYECTO: ... CON CUI N.° ..." 7.5 pt;
  "ÍNDICE DE PLANOS" 15 pt granate con borde inferior; "ESPECIALIDAD: INSTALACIONES SANITARIAS - DRENAJE PLUVIAL" 9.5 pt; ubicación
  8 pt gris.
- Tabla de 5 columnas: N.° (0.8 cm), LÁMINA (1.6), DESCRIPCIÓN (resto), FORMATO (1.8), ESCALA (1.9). Encabezado granate con texto
  blanco 7.5 pt y `tblHeader`; cada fila con `cantSplit`. Código 8 pt negrita granate; título 8 pt negrita y debajo el contenido en
  6.5 pt gris; formato 8 pt; escala del rótulo 8 pt y debajo las escalas de los dibujos 6.5 pt gris.
- Filas de grupo (celdas combinadas, fondo `F2E6E8`, texto granate 7.5 pt negrita): en orden por número, "NOMBRE DEL GRUPO  (DPL-aa A
  DPL-bb)"; en orden de PDF, "LÁMINAS EN FORMATO A1  (n)".
- Pie del índice: "Total: N láminas (n en A0, n en A1, ...)." y notas: "Escala del rótulo: INDICADA; debajo, en gris, las escalas de los
  dibujos de cada lámina. Fecha de las láminas: setiembre 2026." y la nota de orden ("Láminas ordenadas por su número, de la primera a
  la última." o "El N.° es el orden de la lámina en el juego de planos, organizado por formato de hoja (A0, A1, A2 y A3).").
- Propiedades: autor vacío, título "Índice de planos - Drenaje pluvial - <proyecto>".

CAR Mujeres: usa la plantilla IISS del proyecto (vacía el cuerpo, conserva el `sectPr` del cuerpo con logo y proyecto en el
encabezado, sin `titlePg`); "ÍNDICE DE PLANOS" 13 pt subrayado, "ESPECIALIDAD: DRENAJE PLUVIAL", "CUI N° 2717013"; código 7.5 pt; 46
láminas en el orden del juego (3 A0, 15 A1, 21 A2, 7 A3); 2 páginas.

Barranquita: página 1 carátula común (clave "planos"); página 2 "ÍNDICE DE PLANOS" 15 pt azul, servicio, proyecto, C.I.; tabla de 5
columnas (0.8, 1.6, 9.2, 1.9, 2.0 cm) con encabezado azul y grupos numerados en `D9E2F3` ("1. PLANTA GENERAL", "2. CUADRO DE TRAMOS
Y SECCIONES TÍPICAS", "3. PERFILES LONGITUDINALES", "4. SECCIONES TRANSVERSALES", "5. CORTES GENERALES", "6. DETALLES DE DESCARGAS
POR EL CERCO"); pie "Total: 19 láminas, formato A1 (841 x 594 mm)" y nota de impresión a escala 1:1 y coordenadas UTM WGS84.

### 10.4 Orden: por número o por formato

Parámetro `ORDEN`:
- `'pdf'`: orden del juego en el PDF del usuario, que va **por formato de hoja** (A0, A1, A2, A3), con filas de grupo por formato.
- `'numero'`: de la primera a la última lámina, ordenadas por el número final del código (`(\d+)$`, de modo que DPLV-09, DPVL-09 y
  DVPL-11 cuentan igual), con o sin grupos temáticos.

| Proyecto | Orden vigente | Grupos |
|---|---|---|
| Hogar de Refugio | por número, DPL-01 a DPL-42 | 7 grupos temáticos: Red de cunetas (01-05); Colector pluvial frontal (06-14); Montantes pluviales por edificación (15-23); Detalles del colector: registros, empalmes, cajas y juntas (24-29); Canaletas y montantes pluviales (30-34); Caja sumidero de piso, lloraderos y falsa columna (35-40); Obra complementaria OC-01: bancas con pérgola (41-42) |
| CAR Varones | por número, DPLV-01 a DPLV-44 | sin grupos (lista corrida) |
| CAR Mujeres | orden del juego (archivo de lista) | sin grupos |
| Barranquita | orden de `_calc/indice.json` | 6 grupos por tipo de lámina |

### 10.5 Códigos tal cual el rótulo

- Varones: DPVL-09, DPVL-10 y DVPL-11 están así en los rótulos y así van en el índice; "DETALLE CONTRUCTIVO FALSA COLUMNA ..." (DPLV-44)
  también. La usuaria revisó el RAR y confirmó (23-10-2026): "son solo tildes y eso, además la fecha sí es setiembre, así que ya está
  bien".
- Refugio: con el PDF de 40 láminas el isométrico de lloraderos tenía en el rótulo DPL-36, repetido con la caja sumidero. Tras la
  corrección del usuario se citó como DPL-36 (su rótulo). Con el PDF de 42 láminas (23-10-2026) ya no hay duplicados: DPL-37
  isométrico de instalación de lloraderos (A1), DPL-38 detalle de lloradero (A2), DPL-39 falsa columna (A3), DPL-40 planta de ubicación
  de lloraderos (A0), DPL-41 y DPL-42 bancas OC-01 (A2); DPL-01 a DPL-36 sin cambio.

### 10.6 Corrección del usuario del 22-10-2026 (regla "sin observaciones")

La primera versión del índice del Refugio renumeró y "observó" la lámina (proponía cambiar del 39 al 40) y generó un PDF reordenado
DPL-01 a DPL-40 con marcadores. El usuario: "en el índice dices para cambiar del 39 al 40, haces observaciones, pero no tienen sentido
porque mira el PDF que te pasé de planos está ordenado por formato de hoja, primero A0 y así hasta abajo, y no ordenado por número".
Decisión: el índice sigue el orden del PDF, con los códigos tal como están en cada rótulo, **sin renumerar ni observaciones** y solo con
las láminas que trae el PDF; se retiró el PDF reordenado. Al día siguiente el usuario envió su propio índice (versión del 22-10) y el PDF
de 42 láminas; el índice quedó de la DPL-01 a la DPL-42 con grupos temáticos "como el índice que tenía la usuaria".

### 10.7 Coherencia del índice con los demás documentos

Al cambiar el juego de láminas (23-10-2026, Refugio 40 → 42) se actualizaron en cadena: memoria hidrológica (lloraderos
DPL-40/38/37), memoria descriptiva (falsa columna DPL-39, lloraderos, relación de 42 láminas, figuras de la OC-01 tomadas del PDF),
especificaciones (planos DPL-01 a DPL-42, lloraderos DPL-40/38/37) y carátulas ("LÁMINAS DPL-01 A DPL-42"). Se comparó el texto antes
y después: solo cambiaron esas citas. En el metrado de Varones (23-10-2026) las referencias a láminas se pasaron a los códigos DPLV
(140 celdas, solo textos); las láminas que la usuaria excluyó a propósito (DP-08, DA-01 a DA-03) no se reemplazan: sus referencias se
**borran** ("Criterio (lámina DA-02): ..." → "Criterio: ...").

---

## 11. Carátulas

### 11.1 Pedidos y correcciones (cronológico)

| Fecha | Pedido o corrección | Resultado |
|---|---|---|
| 21-10 17:15 | Barranquita: "en base a esta imagen hazme la carátula para todos los documentos" (foto aérea de dron) | carátula común en los 6 documentos (Word, Excel, UNO, especificaciones) |
| 21-10 17:24 | "Solo necesito el archivo en un solo Word, solo las carátulas" | `caratula_b.solo_caratulas()`: 6 carátulas, una por página |
| 21-10 17:31 | "No debe decir EXPEDIENTE TÉCNICO, debería decir SERVICIO DE DISEÑO - DRENAJE PLUVIAL" | `caratula_b.EXPEDIENTE`; se regeneraron los 6 documentos y se comprobó que solo cambió esa línea |
| 21-10 17:46 | "Índice de planos y carátula de planos en un solo Word" | `indice_planos_b.py` |
| 21-10 21:17 | CAR Mujeres: carátulas "servicio para elaboración de expediente técnico", todo en un Word | 6 carátulas copiando la de la plantilla IISS |
| 21-10 21:22 | "¿No le puedes hacer más vacán con su foto del CAR? ... más elegante" | diseño gráfico: escudo, franja granate, vista 3D, vista aérea |
| 21-10 21:30 | "No tengo foto, pero le puedes poner de la planta del CAR Mujeres, tú sabes cuál es la última" | la bitácora lo registra como pendiente de la foto; el generador vigente usa la vista 3D del resumen ejecutivo (confirmar con el usuario) |
| 23-10 20:42 | CAR Varones: "una carátula de cada uno en un Word separado y esa foto es la foto del proyecto en cada carátula ... dame carátula de planos también" | 7 carátulas (incluye planos) |
| 23-10 20:44 | "Todo en un solo Word, no separado" | un Word, una carátula por página; se borra la carpeta de la versión anterior |
| 23-10 20:46 | "Este es el logo del gobierno, el otro sale corto, corrige" | `escudo()` recorta el escudo completo del logo oficial |
| 23-10 21:49 | Fecha "sí es setiembre" | SETIEMBRE - 2026 en carátulas, memoria descriptiva y PDF de Varones |
| 23-10 22:05 | Refugio: carátulas con la foto que envía, más una de planos; "no pongas el que dice índice de planos, solo planos"; en un solo Word | `caratulas_refugio.py`, 7 carátulas |
| 23-10 22:07 | "Usa otro color diferente, por ejemplo verde" | Refugio en verde `1E5E3B` / `D6EEDD`; Varones sigue granate (XML idéntico) |

### 11.2 Diseño común (CAR Varones y Hogar de Refugio, `varones/caratulas_v.caratula`)

Página A4, márgenes 2.0 cm laterales, 2.3 superior, 1.2 inferior; ancho útil 17 cm. De arriba hacia abajo:
1. **Entidad con escudo**: tabla sin bordes de 2 columnas (3.2 cm y el resto). Escudo a 2.8 cm de alto. Al lado "GOBIERNO REGIONAL
   SAN MARTÍN" 17 pt negrita en el color del proyecto, espaciado de letras 10; debajo "GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO" 10.5 pt
   gris con línea inferior del color del proyecto.
2. **Servicio**: "SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL EXPEDIENTE TÉCNICO DE PI:" 11 pt negrita color (26 pt
   antes).
3. **Proyecto** entre comillas (nombre tal como el rótulo de las láminas) 10 pt negrita, interlineado 1.05; **CUI N° ...** 11.5 pt color.
4. **Foto del proyecto** a 17 cm de ancho (tabla de 1 celda sin bordes ni márgenes laterales, para que mida igual que la franja);
   leyenda 8 pt cursiva gris ("Vista del Centro de Acogida Residencial - Varones" / "Vista del Hogar de Refugio Temporal").
5. **Franja** (tabla de 1 celda con fondo del color): título del documento 26 pt blanco negrita (espaciado 8); el subtítulo se parte
   por " - " y cada parte va en su línea, 11 pt, color claro.
6. **Ubicación y fecha**: 2 celdas con borde izquierdo grueso (24) del color: "UBICACIÓN DEL PROYECTO" con Distrito: Morales /
   Provincia: San Martín / Departamento: San Martín (etiqueta gris, valor negrita); "FECHA" con "SETIEMBRE - 2026" 15 pt negrita.

Técnica: entre carátulas un párrafo mínimo de 1 pt (`w:sz val=2`) con `page_break_before` (no empuja el contenido); al final otro
párrafo mínimo sin salto, para no crear una página en blanco. Cada carátula cabe en una sola página A4 (verificado convirtiendo a
PDF). Foto reducida a 1 600 px máx. (calidad 90); el original del usuario no se toca.

Escudo (`escudo()`): del logo oficial entregado (`insumos/katiuska/LOGO_GOBIERNO_REGIONAL_SAN_MARTIN.png`), se recorre la imagen fila
por fila buscando píxeles no transparentes y oscuros; la primera franja en blanco después del dibujo marca el fin del escudo (debajo
está el texto "GOBIERNO REGIONAL SAN MARTÍN", que ya va al lado); se recorta a su caja. El escudo anterior (recorte de un Word del CAR
Mujeres) salía cortado.

Documentos y orden (carpeta de entrega del usuario): ESPECIFICACIONES TÉCNICAS; MEMORIA DE CÁLCULO (DRENAJE PLUVIAL: CANALETAS,
MONTANTES Y CUNETAS); MEMORIA DE CÁLCULO (COLECTOR PLUVIAL FRONTAL); MEMORIA DESCRIPTIVA; MEMORIA HIDROLÓGICA (HIDROLOGÍA Y DRENAJE
PLUVIAL CON COLECTOR FRONTAL); METRADOS; PLANOS (LÁMINAS DPLV-01 A DPLV-44 / DPL-01 A DPL-42). Cada subtítulo termina en
"ESPECIALIDAD DE DRENAJE PLUVIAL".

### 11.3 CAR Mujeres (`mujeres/caratulas_m.py`)

- Imágenes extraídas (sin modificar los originales) de los Word del proyecto: vista 3D del CAR (resumen ejecutivo,
  `word/media/image18.jpg`, recorte sin la sombra inferior), vista aérea del terreno (carátula de la memoria hidrológica,
  `word/media/image1.png`) y escudo (plantilla IISS). Se guardan en `entregables_mujeres/figuras_caratula/`.
- Escudo a 2.2 cm de ancho en columna de 2.6 cm; entidad 17 pt granate; gerencia 10.5 pt gris; servicio 11 pt granate; proyecto 10 pt;
  CUI 11 pt; vista 3D a 17 cm con leyenda "Vista 3D del Centro de Acogida Residencial - Mujeres"; franja granate con título 24 pt y
  subtítulo 11 pt `F2D7DB`; abajo, vista aérea (8.3 cm) con "Vista aérea del terreno del proyecto" y, a su derecha, ubicación con borde
  izquierdo granate y fecha "SEPTIEMBRE - 2026" 13 pt (escrita con P, distinta del "SETIEMBRE" de Varones y Refugio).
- 6 documentos en el orden de su carpeta: METRADOS; MEMORIA HIDROLÓGICA; MEMORIA DESCRIPTIVA; MEMORIA DE CÁLCULO (COLECTOR PLUVIAL
  FRONTAL); MEMORIA DE CÁLCULO (DRENAJE PLUVIAL INTERNO); ESPECIFICACIONES TÉCNICAS.

### 11.4 Barranquita (`barranquita/caratula_b.py`): una carátula para Word, Excel, UNO y especificaciones

- Contenido y orden: "GOBIERNO REGIONAL SAN MARTÍN" 15 pt azul; "GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO" 11 pt gris con línea azul;
  "SERVICIO DE DISEÑO - DRENAJE PLUVIAL" 12 pt azul; proyecto 11.5 pt; "C.I. N° 468901" 11 pt azul; foto aérea a 15.5 cm (recortada
  sin las esquinas oscuras del lente: caja 45, 30, 1555, 1150 de la foto de 1 600 × 1 198); leyenda 8 pt cursiva; franja azul con
  título (20 pt, o 17 pt si tiene 30 caracteres o más) y subtítulo 11 pt; "ESPECIALIDAD: INSTALACIONES SANITARIAS - DRENAJE PLUVIAL"
  10.5 pt; ubicación "Distrito de Barranquita - Provincia de Lamas - Departamento de San Martín"; "OCTUBRE 2026" 12 pt azul.
- Claves y títulos: metrado (METRADO / DRENAJE PLUVIAL - RED DE CUNETAS); hidrológica (ESTUDIO HIDROLÓGICO Y DE DRENAJE PLUVIAL /
  MEMORIA HIDROLÓGICA - RED DE CUNETAS); descriptiva; cálculo (MEMORIA DE CÁLCULO / HIDROLOGÍA E HIDRÁULICA DE LA RED DE CUNETAS);
  especificaciones; análisis (ANÁLISIS ESTADÍSTICO / PRECIPITACIÓN MÁXIMA EN 24 HORAS Y TORMENTA DE DISEÑO); planos.
- Word: `word_b.Doc.caratula(..., clave)` pone la carátula como primera página sin encabezado.
- Excel (openpyxl): hoja CARÁTULA al inicio, 8 columnas de 11.5, filas combinadas A:H, foto anclada con `TwoCellAnchor` de A8 a H8 y
  alto de la fila según la proporción de la foto; A4 vertical ajustada a 1 × 1 página, centrada, área de impresión A1:H17, sin
  cuadrícula.
- Calc por UNO (análisis estadístico, para no perder fórmulas ni gráficos): misma hoja con `GraphicObjectShape` anclado a A8, estilo de
  página "Caratula" A4 sin encabezado ni pie, escala 1 × 1, área de impresión A1:H17.
- Especificaciones: `datos(clave)` entrega textos, foto y proporción al JSON; `docx_espec.js` la dibuja (foto de 586 px de ancho).
- `solo_caratulas()`: Word con las 6 carátulas (sin la de planos, que va en el Word del índice).

### 11.5 Carátula de planos

Varones y Refugio: una carátula más en el mismo Word ("PLANOS" / "LÁMINAS DPLV-01 A DPLV-44 - ESPECIALIDAD DE DRENAJE PLUVIAL").
Barranquita: página 1 del Word "CARÁTULA E ÍNDICE DE PLANOS". El usuario pidió para el Refugio **no** incluir una carátula de "índice
de planos", solo la de planos.

### 11.6 Carátula propia de la memoria descriptiva

Además de las carátulas sueltas, las memorias descriptivas del Refugio y Varones llevan su carátula interna (§5.3) con la lámina de
red general como imagen. Fechas a vigilar: la del Refugio conserva OCTUBRE 2026 (no se pidió cambio), mientras sus carátulas sueltas
dicen SETIEMBRE - 2026; la memoria de cálculo PDF del Refugio dice octubre 2026.

---

## 12. Verificación visual y controles de calidad

| Control | Cómo | Cuándo |
|---|---|---|
| Word sin alterar el original | `memoria_docx.verificar()`: texto de párrafos y tablas originales igual | cada generación del capítulo |
| Solo cambia lo pedido | extraer texto (python-docx) antes y después y comparar; en Excel, valores tras recalcular con LibreOffice | toda corrección (por ejemplo "SERVICIO DE DISEÑO", citas DJ, códigos DPLV) |
| Metrados intactos | comparar todas las celdas numéricas de la planilla antes y después | cada vez que un documento toca el libro (códigos de lámina, carátula) |
| Títulos del índice = rótulo | comparación "llana"; si difiere, el programa se detiene | cada índice |
| Memoria = análisis estadístico | `coteja_analisis_b.py` (1 696 valores, 0 diferencias) y `analisis_estadistico_b.comprobar()` | cada cambio de lluvia |
| Página única por carátula | convertir a PDF y contar páginas (7 carátulas = 7 páginas) | cada versión de carátulas |
| Aspecto | `soffice --headless --convert-to pdf` y `pdftoppm` a PNG para revisar la vista (por ejemplo `figuras_memoria/vista_caratulas.png` de Barranquita) | antes de entregar |
| Excel sin errores | recalcular con LibreOffice y buscar `#` (errores) en las hojas; contadores "NO CUMPLE" = 0 | memorias de cálculo |
| Otro proyecto idéntico al parametrizar | huella (XML o texto) del proyecto que no se pidió cambiar | al reutilizar motores |

---

## 13. Cronología de decisiones del usuario sobre documentos

| Fecha | Mensaje / decisión | Efecto en los documentos |
|---|---|---|
| 03-10 | Entregables del CAR Mujeres repetidos para el Refugio: memoria Excel con fórmulas (datos, caudales, perfil, estructural); capítulo del colector al final del estudio hidrológico sin alterar lo anterior; Excel en español con ";" | `memoria_xlsx.py`, `memoria_docx.py` |
| 03-10 16:43 | "¿Por qué pones 35.163 mm si el diseño es 210? hay contradicción" | DATOS y memoria explican que 35.16 mm en 10 min = 210.98 mm/h y que el colector usa 155.66 por tc 15 min |
| 03-10 16:48 | Documento irrefutable, bajo normas, sin que intervenga la Contraloría | hoja CUMPLIMIENTO y sección "datos de otros expedientes" |
| 03-10 17:24 | Las prolongaciones de cunetas ya las metró el usuario | la memoria dice que se metran en partidas de cunetas; el colector solo incluye ventana y registro |
| 05-10 | Memoria descriptiva general CAR Mujeres: 45-60 páginas, arquitectura antes que drenaje, drenaje mínimo, solo datos reales | §5.6 |
| 08-10 | Especificaciones de los 3 proyectos, normativa peruana, al mínimo detalle; "revísalo antes de presentarlo" | `espec.py` + `docx_espec.js` |
| 08-10 04:35 | "El nombre CIP no pongas nada" | firmas en blanco |
| 14-10 | "¿Por qué todo escribes en inglés?" | todo en español |
| 15-10 | PDF de la memoria de cálculo con el estilo del ejemplo (CAR Mujeres y luego Refugio) | `memoria_pdf_m.py`, `memoria_pdf_refugio.py` |
| 20-10 17:29-17:37 | Revisar que la memoria del CAR Mujeres cuadre con los otros dos; justificar 210 → 155 en las 3 memorias, que coincidan | `revision_hidrologia.py` |
| 20-10 17:57 | Planos renombrados (RAR): actualizar solo la memoria hidrológica del CAR Mujeres | códigos ST-CG, STP-CG, ESDAE-01, IC-01 |
| 20-10 20:05 | Memoria descriptiva del CAR Mujeres | `memoria_descriptiva_m.py` |
| 20-10 20:28 | Revisar la memoria de cálculo PDF del CAR Mujeres → "procede, corrige" | área 6752.03, sin nombres, 0+078.42, setiembre |
| 21-10 13:06 | Barranquita: memoria, descriptiva, cálculo, especificaciones, metrado | expediente Barranquita |
| 21-10 14:40 | "¿Por qué tan pocas páginas? ... datos mínimo 2024 o 2025" | estructura de los CAR (29 pág.), lector de datos recientes |
| 21-10 15:39 | Usar sus formatos tal cual (cálculo, metrado, análisis, especificaciones); no alterar planos ya impresos | formatos CAR; planos sin regenerar |
| 21-10 16:44 | Análisis estadístico con la plantilla del CAR Varones | `analisis_estadistico_b.py` |
| 21-10 17:02 | ¿La memoria coincide con el nuevo análisis? | `coteja_analisis_b.py` |
| 21-10 17:15-17:46 | Carátula común con foto; solo carátulas en un Word; "SERVICIO DE DISEÑO - DRENAJE PLUVIAL"; índice + carátula de planos en un Word | §11.4, §10.3 |
| 21-10 21:00-21:30 | Índice y carátulas del CAR Mujeres; más elegante con foto; sin foto, usar la planta | §11.3 |
| 22-10 20:31 | Refugio: memoria hidrológica, descriptiva, especificaciones e índice con el PDF de láminas | figuras desde el PDF, `memoria_descriptiva_refugio.py` |
| 22-10 21:28 | El PDF va por formato, no por número; sin observaciones | §10.6 |
| 23-10 17:20 | Varones: índice, memorias y especificaciones con los planos finales; desagregado del lloradero | capítulo de lloraderos con desagregado |
| 23-10 19:38-19:47 | Códigos de lámina nuevos en el metrado; borrar referencias de láminas excluidas | solo textos del metrado |
| 23-10 20:12 | Índice de la lámina uno a la última | `ORDEN = 'numero'` en Varones |
| 23-10 20:22 | PDF del colector de Varones con el mismo estilo | `memoria_pdf_v.py` |
| 23-10 20:42-21:49 | Carátulas de Varones: separadas → un solo Word; logo oficial; fecha setiembre | §11.2 |
| 23-10 22:05-22:07 | Carátulas del Refugio en un Word, sin índice de planos, en verde | `caratulas_refugio.py` |
| 23-10 22:24 | ¿Tienes las últimas especificaciones del Refugio? | se quitaron citas DJ inexistentes |
| 23-10 22:30-22:32 | Revisar el índice del Refugio contra los planos; PDF de 42 láminas que imprime | índice DPL-01 a DPL-42 y cadena de citas |
| 24-10 | Guardar todo lo aprendido al mínimo detalle para implementarlo en su programa | esta base de conocimiento |

---

## 14. Para implementarlo en un programa

### 14.1 Plantillas e insumos que el programa debe recibir

| Insumo | Uso | Regla |
|---|---|---|
| Word del estudio hidrológico del proyecto | base de la memoria hidrológica | se agrega al final; se verifica que lo anterior quede igual |
| Plantilla Word del proyecto (por ejemplo memoria de IISS) | estilos, carátula y encabezado de la memoria descriptiva y del índice | se copia; nunca se edita el original |
| Metrado vigente (Excel) | cantidades de memorias y especificaciones; partidas de las especificaciones | solo lectura; hojas RESUMEN, CONCRETO EN CUNETAS, METRADO LLORADEROS, DESAGREGADO LLORADEROS, METRADO CANALETA BANCAS |
| PDF de láminas que imprime el usuario | índice (códigos, títulos, formatos, escalas, contenido) y figuras | leer con `pdfinfo`/`pdftotext`/`pdftoppm`; no modificar |
| Resultado del diseño (`_calc/diseno.json`) | números de hidráulica, perfil, registros, cunetas, cajas | una sola fuente para Excel, Word y PDF |
| Memoria de cálculo Excel recalculada | valores del capítulo y del PDF | recalcular con LibreOffice antes de leer |
| Plantilla de análisis estadístico del usuario | Excel del análisis | cargar datos y borrar filas sobrantes para que se ajusten fórmulas y gráficos |
| Foto del proyecto y logo oficial | carátulas | recortar en copia; escudo sin el texto |
| Ejemplo de estilo PDF (memoria HIDRO-CE040) | CSS del PDF | tokens de §7.3 |

### 14.2 Configuración por proyecto (un solo archivo de datos)

Campos mínimos: nombre completo del proyecto (tal cual el rótulo), código (CUI o C.I.), nombre corto para encabezados, entidad
(GOBIERNO REGIONAL SAN MARTÍN), gerencia (GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO), unidad ejecutora (Gerencia Territorial Bajo Mayo
- Dirección de Infraestructura), texto de servicio (según proyecto: "SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL
EXPEDIENTE TÉCNICO DE PI:" o "SERVICIO DE DISEÑO - DRENAJE PLUVIAL"), especialidad, ubicación (distrito, provincia, departamento,
sector), fecha de los rótulos, color principal y secundario, foto y leyenda, lista de documentos de la carpeta de entrega en su orden,
prefijo y rango de láminas, diccionario de títulos de lámina, grupos temáticos, orden del índice (`pdf` o `numero`), mapeo de códigos
de trabajo → códigos del juego del usuario, aporte externo y receptor (nombre, CUI, caudal, cotas), parámetros constructivos para las
especificaciones.

### 14.3 Orden de generación

1. Diseño → `_calc/diseno.json` (fuente única de números).
2. Memoria de cálculo Excel (fórmulas) → recalcular con LibreOffice → comprobar 0 "NO CUMPLE".
3. Análisis estadístico (si el proyecto lo requiere) → comprobar contra el cálculo propio.
4. Metrado vigente del usuario (no se genera: se lee).
5. Índice de planos desde el PDF del usuario → `_calc/indice_planos.json` (lo necesitan los pasos siguientes).
6. Memoria hidrológica: capítulo del colector + complementarios (figuras desde el PDF por la página del JSON) → verificación de no
   alteración → revisión coordinada de textos entre proyectos.
7. Memoria descriptiva (relación de planos desde el JSON; cantidades desde el RESUMEN) → índice con páginas (dos pasadas si aplica).
8. Especificaciones (partidas del RESUMEN, mapeo de láminas, pase de tildes) → JSON → Word.
9. Memoria de cálculo PDF (desde el Excel recalculado).
10. Carátulas (un solo Word) y, cuando corresponda, carátula de planos.
11. Controles de §12 y vista previa PNG de las páginas críticas.

### 14.4 Controles de coherencia que el programa debe ejecutar siempre

- El mismo valor (Q, I, C, áreas, cotas de fondo, número de registros, juntas, lloraderos) debe ser idéntico en Excel, PDF, memoria
  hidrológica, memoria descriptiva, especificaciones y metrado; buscar en todos los textos generados los valores antiguos después de un
  cambio (por ejemplo 6752.06, 0.808, "contramarco", "DJ-03").
- Entre proyectos encadenados: el caudal y la cota de fondo que entrega el aguas arriba = los que recibe el aguas abajo (258.7 L/s en la
  CL; 560.7 L/s en el R-01; misma lluvia, TR, FS e intensidad del colector en las tres memorias).
- Todo código de lámina citado en un documento debe existir en el índice vigente; las láminas excluidas no se citan.
- Las partidas de las especificaciones = partidas del RESUMEN (mismo código, descripción, unidad y orden).
- Ningún documento contiene nombres de personas, CIP, "observaciones" a documentos ajenos ni textos en inglés.
- Fecha y nombre del proyecto iguales a los rótulos de las láminas en carátulas, índice y memorias (vigilar SETIEMBRE / SEPTIEMBRE /
  OCTUBRE).
- Cada carátula en una página; tablas con encabezado repetido y filas que no se parten; el TOC se actualiza al abrir.

### 14.5 Librerías y herramientas usadas

python-docx (Word), openpyxl (Excel), LibreOffice en modo sin interfaz (recalcular, convertir a PDF, UNO para plantillas con
gráficos), Poppler (`pdfinfo`, `pdftotext -raw/-layout`, `pdftoppm`), Pillow (recortes de fotos, escudo y láminas), ezdxf (lectura de
DXF para el índice de Barranquita), Node con la librería `docx` (especificaciones) y Playwright/Chromium (PDF HTML → A4), NumPy (anexo
estadístico).
