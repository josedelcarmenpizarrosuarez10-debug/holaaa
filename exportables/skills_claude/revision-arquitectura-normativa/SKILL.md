---
name: revision-arquitectura-normativa
description: "Revisar y corregir los documentos de arquitectura de un expediente técnico peruano sin rehacer el trabajo del autor: memoria descriptiva y programación arquitectónica (copia corregida con el mismo formato e imágenes), análisis de incompatibilidades de ubicación (lista de verificación vigente del sector más las condiciones propias del servicio) y sustento normativo del programa (RNE y normas sectoriales vigentes, cotejadas con su texto). Sirve para colegios, establecimientos de salud, CAR, hogares, locales municipales y otros servicios de cualquier entidad. Entrega un Word para el expediente, una matriz Excel con fórmulas y una nota de revisión interna aparte. Usar cuando el usuario mande una memoria o programación de arquitectura para revisar, corregir o sustentar, o pida un análisis de ubicación o de incompatibilidades."
---

# Revisión normativa de arquitectura (memoria, programación, ubicación y sustento)

Método general para cualquier edificación pública o privada (colegio, posta o centro de salud, CAR, hogar o refugio, local
municipal, comisaría, centro comunal, etc.) y para cualquier entidad. Los proyectos que aparecen en las secciones
"Ejemplo de referencia" solo ilustran el método: ningún dato suyo (normas, áreas, nombres, colores) se usa en otro proyecto.

## Reglas permanentes del usuario (valen para todo proyecto)
- Todo en español. Entregables en **Word, Excel y DXF**; vistas previas en **PNG**; PDF solo si el usuario lo pide.
- **Escala real: 1 unidad = 1 m** ("si algo mide 0.56, así debe medir en el plano").
- Decir siempre **"cota de fondo"**.
- Citar cada proyecto por su **nombre completo y su CUI** (o código de inversión). No mezclar partidas, láminas ni datos entre proyectos.
- **Nada en los documentos que revele el uso de IA.** Nombre y CIP del proyectista: **campos en blanco**.
- **No modificar** los metrados ni los documentos del usuario salvo pedido expreso; cambiar solo lo pedido y verificar
  que lo demás quede idéntico (cotejo antes y después).
- Partidas con nombres y estructura **Delphin**; cantidades siempre del metrado propio. Precios reales con su fuente y fecha;
  mano de obra según la tabla CAPECO vigente o la que indique el usuario.
- Actualizar todo lo relacionado de forma coherente: **metrado ↔ planos ↔ especificaciones ↔ memoria**.
- **Cuando el usuario ya imprimió un plano, no se regenera**: los cambios van a los documentos y se le avisan.
- Las observaciones sobre documentos de otros profesionales van en una **nota de revisión interna**, nunca dentro del documento.
- No reenviar archivos que no cambiaron. Preguntar lo dudoso antes de producir, con una imagen de control si hace falta.
- **Ningún dato de un proyecto anterior se usa en uno nuevo** (colores, dimensiones, niveles, lluvias, cantidades, nombres):
  todo sale de los planos y documentos del proyecto nuevo o se le pregunta al usuario. Los proyectos citados son solo ejemplos.
- Revisar el trabajo propio varias veces antes de entregar; decir con claridad lo que no se pudo comprobar.

## Principio rector: proteger el trabajo del autor del documento
El documento es para el expediente y lo revisará la entidad o la Contraloría. Por eso:
1. **El entregable solo sustenta.** Cada ambiente o dispositivo lleva la norma que le corresponde, su cálculo y el resultado
   (CUMPLE / CONFORME). No lleva un capítulo de "observaciones", ni frases como "error del arquitecto" o "se recomienda revisar".
2. **Todo lo dudoso va a una nota de revisión interna** que no forma parte del expediente. Tiene dos partes: "1. Ya corregido" y
   "2. Para que el autor revise". Si se cotejó una norma, se agrega una parte 3 con el cotejo fila por fila.
3. **No se cambian áreas, cantidades ni resultados de campo** (por ejemplo, los "CUMPLE" que el autor verificó en el sitio). Se
   corrigen las citas, el texto copiado de otro proyecto, las erratas, los totales que no suman y la numeración.
4. **El insumo no se edita.** Siempre se escribe una copia `..._CORREGIDA.docx` o `.xlsx`.

## Datos que hay que pedir (si faltan)
- **Proyecto:** nombre completo tal cual el rótulo, CUI (o código de inversión), entidad, unidad ejecutora, ubicación y fecha.
- **Tipo de servicio y sector:** educación, salud, protección de niños o de víctimas, municipal, etc. De eso depende el marco
  normativo; si no se conoce, preguntarlo antes de redactar.
- Los Word y Excel del autor: memoria descriptiva, programación de áreas y borrador del cuadro de incompatibilidades.
- **La lista de normas que aplican y su versión vigente**, con **el texto de cada una** (PDF o escaneo). Las normas cambian:
  verificar en la fuente oficial (El Peruano, portal del ministerio) que no esté derogada ni modificada. Si una norma no se
  entregó, sus índices quedan "por cotejar" y no se inventan.
- **La lista de verificación de ubicación del sector** (cuadro de incompatibilidades o de criterios de localización) en su versión
  vigente. Si el sector no tiene una propia, usar la del sector más parecido como referencia y decirlo.
- **Guías de buena práctica del servicio**, si existen (superficies sugeridas, criterios de diseño), para la comparación referencial.
- Los datos del terreno: poligonal y área, colindantes, usos dentro del área de influencia, UTM referencial, vía de acceso y titular
  según la partida registral o el documento de saneamiento.
- El índice de láminas vigente, para el listado de planos de la memoria.
- La población usuaria: alumnos por nivel, atenciones o camas, residentes o plazas, personal por turno, según el servicio.
- **Formato de presentación:** paleta institucional del proyecto (o la que el usuario elija), logo o escudo oficial de la entidad,
  tipo de letra y encabezado; si quiere carátula propia, la foto del proyecto.

## A. Corrección de la memoria descriptiva y de la programación (copia con el mismo formato)
Técnica con python-docx: abrir el original, editar el texto **solo en los runs que lo contienen** y guardar con otro nombre.
- Función de reemplazo que localiza el texto viejo en la concatenación de los runs del párrafo. Escribe el nuevo en el primer run
  afectado y vacía solo los siguientes que lo contenían. No hay que tocar los runs de hipervínculos (se duplica su texto).
- Llevar una lista de cambios (viejo → nuevo) para la nota interna y comprobar que cada texto buscado exista. Si no está, detenerse.
- Conservar todas las imágenes: contarlas antes y después; la cantidad debe ser igual.
- Las tablas nuevas, como los cuadros de ubicación, se insertan copiando una tabla modelo del mismo documento para heredar su estilo.

Qué se corrige (patrones frecuentes, válidos para cualquier servicio):
- **Texto copiado de otro proyecto o de otro tipo de servicio:** términos, nombres, normas y datos que no corresponden (por ejemplo,
  "aulas" o "infraestructura educativa" en un hogar, "residentes" en un colegio, "pacientes" en un local municipal) y normas
  derogadas o de otro sector. Se pasan a los términos propios del servicio del proyecto.
- **Datos del terreno:** titular equivocado, decimales mal puestos en hectáreas, áreas sin unidad, puntos sobrantes ("8,556.24. m²"),
  porcentajes incompletos, erratas en títulos, leyendas repetidas, imágenes con numeración que no sigue.
- **Normas mal citadas:** número, tipo o nombre del dispositivo mal escritos (Decreto Ley frente a Decreto Legislativo, "R.V.N",
  "SEMAMHI" → SENAMHI, "Ley Orgánica de Municipales" → Municipalidades), norma citada para un tema que no regula, o norma que falta.
- **Drenaje u otras especialidades** descritos como existentes cuando son parte del proyecto, o al revés.
- **Programa:** subtotales mal rotulados y totales que no suman. El cerco va en ml y no suma área; revisar que la fórmula del total
  incluya todos los ambientes (estacionamientos, patios, áreas techadas). Las citas normativas del programa deben coincidir con las
  del sustento, sin tocar las áreas.
- **Excel de programación:** fórmulas rotas, `#REF!`, unidades (m2 → m²), erratas. Recalcular y verificar que no quede ningún "#".
- **Listado de planos "(POR DEFINIR)"** → las láminas del índice vigente del autor.
- **Sustento pegado dentro de la memoria:** renumerar dentro del numeral que le toca y renumerar las tablas.
- **Análisis de ubicación vacío** (solo el título): llenarlo con el método, el Cuadro de incompatibilidades y el Cuadro de condiciones
  del servicio con su conclusión. La numeración de los cuadros sigue la del documento (si los N.° 1 a 3 ya existen, el siguiente es el 4).
- **Índice:** se pone en la página 2. Es un campo TOC `\o "1-3" \h \z \u` con nivel de esquema (`w:outlineLvl`) en cada título,
  entradas con tabulación derecha de puntos y `w:updateFields` en settings. Las páginas se calculan convirtiendo a PDF con LibreOffice
  y buscando cada título con pdftotext. Si falta la fuente del documento, usar una métricamente igual para paginar como Word.

## B. Análisis de incompatibilidades de ubicación
Estructura del Word: generalidades (servicio y exigencias de ubicación), datos del predio (poligonal, área, colindantes, usos
dentro del área de influencia), marco normativo, método, **Cuadro N.° 1**, **Cuadro N.° 2**, usos colindantes y conclusiones.
Los cuadros van en una sección apaisada.

Método: área de influencia medida **desde el lindero**, con la distancia que fija cada dispositivo. Cada fila lleva la
incompatibilidad, el dispositivo legal (con su versión vigente), la distancia mínima o el criterio, la condición encontrada
(con nombre y distancia real del elemento más cercano) y el resultado.
- **Cuadro N.° 1:** la lista de verificación de incompatibilidades del sector, completa y en su orden (actividades peligrosas,
  combustibles, líneas eléctricas, aeródromos, fajas marginales, derechos de vía, locales nocturnos, etc.). Si el sector no tiene
  lista propia, se usa una lista sectorial reconocida como referencia, indicándolo en el método.
- **Cuadro N.° 2:** condiciones propias del servicio, que cambian con el tipo de edificación. Ejemplos de temas: zonificación
  compatible; accesos y transporte; servicios de apoyo cercanos (salud, seguridad, justicia, educación) con nombre y distancia;
  seguridad y privacidad del usuario; servicios básicos; protección frente a lluvias e inundaciones; accesibilidad de ambulancias
  (salud); recorridos seguros para alumnos (colegios); reserva de la ubicación (hogares de víctimas).
- **Marco:** ley y reglamento del servicio; RNE (A.010 y la norma A.0xx del uso); la lista sectorial como verificación; guías del
  sector. Confirmar cada número de norma con la versión vigente.
- **Matriz Excel:** hoja CUADRO 1 (fórmulas de estado y área de influencia), hoja CONDICIONES y hoja RESUMEN con COUNTIF de ambos
  cuadros. Se conservan los "CUMPLE" de campo del autor; solo se ordenan y se corrigen los textos.

## C. Sustento normativo del programa arquitectónico
1. Leer la programación (zona, ambiente, cantidad, capacidad, índice, área unitaria, total) **sin modificarla**.
2. A cada ambiente asignarle **la norma que le corresponde de verdad**, con artículo y cuadro: primero la norma sectorial del servicio
   (criterios de diseño del ministerio que corresponda) y, donde no la haya, el RNE (A.080 oficinas, A.090 servicios comunales,
   A.030 hospedaje, A.040 educación, A.050 salud, A.120 accesibilidad, según el uso).
3. Cálculo: área mínima = capacidad × índice de ocupación, o el área mínima fija de la norma. Resultado: **CUMPLE** si hay índice y
   el área lo alcanza; **CONFORME** si la norma no da índice y el sustento es cualitativo. Si existe una guía de buena práctica con
   superficies sugeridas, comparar además (EN RANGO / SUPERA), solo como referencia.
4. Verificaciones propias del servicio: por ejemplo, plazas y baños por persona en servicios residenciales, aforo y aparatos
   sanitarios en educación, ambientes mínimos obligatorios en salud; población frente a la capacidad del programa.
5. Word para el expediente: marco normativo con el texto transcrito de cada artículo, población, sustento por zona y ambiente
   (tabla con área requerida, área del proyecto y, si aplica, superficie sugerida), criterios cualitativos y conclusiones.
   Sin capítulo de observaciones.
6. Matriz Excel con fórmulas: MATRIZ (zona, ambiente, cant., capacidad, I.O., norma, área mín. de la norma, área mín. calculada
   `=SI(Y(ESNUMERO(D);ESNUMERO(E));D*E;...)`, área del proyecto, resultado `CUMPLE/NO CUMPLE/CONFORME`, referencia mín. y máx.,
   EN RANGO/SUPERA, total y sustento), hojas de verificaciones propias, ÍNDICES, NORMAS y RESUMEN (COUNTIFS y SUMIF).
   Fila de zona en el tono claro de la paleta del proyecto.
7. Nota interna: citas corregidas; ambientes a revisar (ambientes contados dos veces, totales digitados, áreas bajo lo exigido o
   sugerido, ambientes que la norma exige y faltan); cotejo con la norma recién entregada y puntos para que el autor decida.

## Formato de los entregables (criterio por defecto del usuario; confirmar en cada proyecto)
- Word A4, letra del documento del autor (si no hay, Arial Narrow 11 pt), títulos en el color principal de la **paleta
  institucional del proyecto o la que el usuario elija**; encabezado con nombre corto, CUI y especialidad; pie con "Página X de Y".
  Tablas con encabezado repetido, filas que no se parten y "Fuente:" debajo. Propiedades del documento: autor vacío.
- Carátula propia solo si el usuario la pide: logo o escudo oficial de la **entidad del proyecto**, servicio, proyecto con CUI,
  foto y fecha.
- Nombres: `SUSTENTO_NORMATIVO_PROGRAMA_ARQUITECTONICO_<PROY>.docx`, `MATRIZ_..._<PROY>.xlsx`,
  `ANALISIS_INCOMPATIBILIDADES_UBICACION_<PROY>.docx`, `MEMORIA_DESCRIPTIVA_ARQUITECTURA_<PROY>_CORREGIDA.docx` y la nota
  `REVISION_..._<PROY>.docx` (marcada como uso interno).

## Verificación final (antes de entregar)
- [ ] Texto del original y de la copia comparados: solo cambió lo de la lista de cambios. Imágenes, tablas y áreas iguales.
- [ ] Ninguna área ni cantidad de la programación cambió; los totales nuevos se explican en la nota.
- [ ] Cada cita tiene número de norma, artículo, numeral o cuadro, está en el texto entregado y es la versión vigente.
      Lo no entregado dice "por cotejar".
- [ ] Ningún término, norma ni dato de otro tipo de servicio o de otro proyecto (buscar las palabras típicas del servicio ajeno).
- [ ] Nombres de dispositivos legales, instituciones y especialidades bien escritos.
- [ ] Excel recalculado sin "#" ni "NO CUMPLE" inesperados; el RESUMEN cuadra con el Word.
- [ ] Ninguna "observación" dentro del expediente; todo va en la nota interna.
- [ ] El listado de planos de la memoria es igual al índice de láminas vigente.
- [ ] El índice del Word tiene páginas reales y se actualiza al abrir.
- [ ] Nombre, CUI, entidad, colindantes y colores son los del proyecto en curso.

## Errores que el usuario ya corrigió (lecciones generales)
- **Sustento con observaciones:** un sustento con capítulo de observaciones deja expuesto al autor. El sustento solo sustenta;
  las observaciones van a la nota interna.
- **Análisis hecho con la mirada de otro servicio:** partir del borrador de otro tipo de edificación (por ejemplo, el cuadro de un
  colegio para un hogar) da un análisis equivocado. Se rehace con el marco sectorial, los textos y las condiciones propias del servicio.
- **Programación tocada:** no se cambian áreas ni la programación del autor; los totales mal sumados se corrigen solo en la copia
  y se informan.
- **Norma no entregada:** sus índices no se dan por ciertos; quedan "por cotejar" hasta recibir el texto.
- **Vigencia de la norma:** si el autor cita una versión anterior de una norma, no se cambia en su documento; la vigencia se plantea
  en la nota interna para que él decida.
- **Proyecto equivocado:** confirmar siempre el proyecto (nombre y CUI) antes de producir, sobre todo cuando hay proyectos vecinos.
- **Hipervínculos duplicados:** editar solo los runs afectados y comparar el texto antes y después.
- **Pedirle trabajo al usuario:** "eso que me pides para yo hacer, hazlo tú o déjalo así". Los pendientes se resuelven con criterio
  y se documentan. Solo se pregunta lo que de verdad decide el autor (ambientes repetidos, totales digitados, toponimia dudosa).
- **Documento irrefutable:** el usuario quiere que "la Contraloría no intervenga". Cada criterio lleva su cita exacta y su cálculo;
  nada queda afirmado sin norma o sin dato del plano.

## Ejemplo de referencia (solo para ilustrar; no copiar datos a otro proyecto)
Tres servicios de protección colindantes en el predio Los Mangos, Morales (San Martín), del Gobierno Regional San Martín:
CAR Varones (CUI 2705619; arquitecta Katiuska), Hogar de Refugio Temporal para mujeres víctimas de violencia (CUI 2675514;
arquitecta Solange) y CAR Mujeres (CUI 2717013; Wilma).
- **Marco sectorial usado:** hogar de refugio, Ley 30364 y R.M. 150-2016-MIMP; CAR, D.Leg. 1297; guía de buena práctica,
  lineamientos ONU-Habitat / CONAVIM 2.1 a 2.8; lista de ubicación, cuadro de 18 dispositivos de MINEDU (R.V.M. 010-2022 en el
  borrador del Refugio y R.V.M. 068-2025 en el de Varones; no se cambió la que citaba cada arquitecta); R.V.M. 104-2019 y
  208-2019-MINEDU para ambientes educativos (la 208 llegó tarde y recién entonces se cotejaron sus cuadros 12, 20 a 23, 29, 31 y 40).
- **Cuadro N.° 1 usado (MINEDU, verificar la versión vigente antes de reutilizarlo):** 1 velatorios y cementerios, D.S. 003-94-SA
  (150 m) · 2 establecimientos de salud, NTS 113 y 119-MINSA (100 m) · 3 plantas envasadoras de GLP, D.S. 027-94-EM (100 m) ·
  4 grifos y gasocentros, D.S. 054-93-EM mod. 037-2007-EM (50 m) · 5 venta de bebidas alcohólicas, Ley 28681 y D.S. 012-2009-SA
  (100 m) · 6 plantas de abastecimiento de combustibles, D.S. 045-2001-EM (100 m) · 7 fajas marginales, D.S. 001-2010-AG ·
  8 ductos de hidrocarburos, D.S. 081-2007-EM (200 m) · 9 pozos de hidrocarburos, D.S. 032-2004-EM · 10 aeródromos, D.S.
  050-2001-MTC (aeropuerto de Tarapoto a ~3.5 km) · 11 servidumbre de líneas aéreas, CNE Suministro 2011 · 12 electroductos,
  D.L. 25844 · 13 restricciones radioeléctricas, R.M. 120-2005-MTC/03 · 14 PTAR de terceros, OS.090 · 15 derecho de vía,
  D.S. 034-2008-MTC · 16 vías férreas, D.S. 032-2005-MTC · 17 casinos y tragamonedas, Ley 27153 · 18 hostales, peñas,
  discotecas, bingos y billar, Ley 27972 art. 79.
- **Cuadro N.° 2 usado (8 condiciones del hogar o CAR):** zonificación (A.090 art. 3); zona tranquila y no aislada; servicios de
  apoyo con nombre y distancia; accesos sin estudio de impacto vial con menos de 500 personas (A.090 art. 4); seguridad (cerco,
  caseta, CCTV); reserva y privacidad; servicios básicos (A.040 art. 7 d); protección frente a lluvias (OS.060).
- **Asignaciones del sustento:** sala de reuniones A.090 art. 11 (1.0 m²/pers.) o R.V.M. 208 cuadro 29 (1.50); oficinas A.080
  art. 6; caseta cuadro 40 (3.00); aula cuadro 12 (2.00); SUM cuadro 22 (1.00, máx. 300 m²); tópico cuadro 31 (9.00); almacén
  12.3.1 (mín. 10 m²); SS.HH. del personal A.090 art. 15; estacionamientos A.090 art. 17; hospedaje A.030.
- **Hallazgos:** memorias con texto de colegio (NTIE 001-2017 derogada, R.V.M. 307-2019); titular "Aldea Infantil" en lugar del
  Gobierno Regional; "0.085562 ha" por 0.85562 ha; D.L. 25884 por 25844; EM.110 citada como A.030; total del programa de Varones
  4,205.30 → 4,281.52 m² (omitía el estacionamiento); 32 imágenes en la memoria del Refugio y 30 en la de Varones, sin pérdidas;
  listados de planos con 89 láminas (Varones) y 155 (Refugio); duda de toponimia Polvoraico / Polvorico.
- **Formato usado:** títulos en granate `7B1E2B`, filas de zona en granate claro; carátula con el escudo del Gobierno Regional.
