---
name: revision-arquitectura-normativa
description: Revisar y corregir los documentos de arquitectura de un expediente técnico peruano sin rehacer el trabajo de la arquitecta. Cubre la memoria descriptiva y la programación arquitectónica (copia corregida con el mismo formato e imágenes), el análisis de incompatibilidades de ubicación (cuadro de 18 dispositivos de la R.V.M. 010-2022 o 068-2025-MINEDU, más las condiciones propias del servicio) y el sustento normativo del programa (RNE A.030, A.040, A.080, A.090, R.V.M. 104-2019 y 208-2019-MINEDU, lineamientos ONU-Habitat/CONAVIM). Entrega un Word para el expediente, una matriz Excel con fórmulas y una nota de revisión interna aparte. Usar cuando el usuario mande una memoria o programación de arquitectura para revisar, corregir o sustentar, o pida un análisis de ubicación o de incompatibilidades de un CAR, hogar, refugio, colegio u otro servicio comunal.
---

# Revisión normativa de arquitectura (memoria, programación, ubicación y sustento)

Proyectos de referencia ya resueltos con este método:
- CAR Varones, CUI 2705619: memoria y programación de la arquitecta corregidas, y análisis de ubicación con la R.V.M. 068-2025-MINEDU.
- Hogar de Refugio Temporal para mujeres víctimas de violencia, CUI 2675514: sustento normativo del programa, análisis de ubicación hecho
  para el hogar y memoria "culminada" revisada a fondo.
- CAR Mujeres, CUI 2717013: colindante de los otros dos, en el predio Los Mangos de Morales (San Martín).

## Reglas permanentes del usuario (no negociables)
- Todo en español. Entregables en **Word, Excel y DXF**; vistas previas en **PNG**; PDF solo si el usuario lo pide.
- **Escala real: 1 unidad = 1 m** ("si algo mide 0.56, así debe medir en el plano").
- Decir siempre **"cota de fondo"**.
- Citar cada proyecto por su **nombre completo y su CUI**. No mezclar partidas, láminas ni datos entre proyectos.
- **Nada en los documentos que revele el uso de IA.** Nombre y CIP del proyectista: **campos en blanco**.
- **No modificar** los metrados ni los documentos del usuario salvo pedido expreso; cambiar solo lo pedido y verificar
  que lo demás quede idéntico (cotejo antes y después).
- Partidas con nombres y estructura **Delphin**; cantidades siempre del metrado propio. Precios reales con su fuente;
  mano de obra CAPECO-FTCCP 2026 (operario 28.95, oficial 22.68, peón 20.54 S/ por hora) salvo que el usuario dé otra.
- Actualizar todo lo relacionado de forma coherente: **metrado ↔ planos ↔ especificaciones ↔ memoria**.
- **Cuando el usuario ya imprimió un plano, no se regenera**: los cambios van a los documentos y se le avisan.
- Las observaciones sobre documentos de otros profesionales van en una **nota de revisión interna**, nunca dentro del documento.
- No reenviar archivos que no cambiaron. Preguntar lo dudoso antes de producir, con una imagen de control si hace falta.
- Revisar el trabajo propio varias veces antes de entregar; decir con claridad lo que no se pudo comprobar.

## Principio rector: proteger el trabajo de la arquitecta
El documento es para el expediente y lo revisará la entidad o la Contraloría. Por eso:
1. **El entregable solo sustenta.** Cada ambiente o dispositivo lleva la norma que le corresponde, su cálculo y el resultado
   (CUMPLE / CONFORME). No lleva un capítulo de "observaciones", ni frases como "error de la arquitecta" o "se recomienda revisar".
2. **Todo lo dudoso va a una nota de revisión interna** que no forma parte del expediente. Tiene dos partes: "1. Ya corregido" y
   "2. Para que la arquitecta revise". Si se cotejó una norma, se agrega una parte 3 con el cotejo fila por fila.
3. **No se cambian áreas, cantidades ni resultados de campo** (por ejemplo, los "CUMPLE" que ella midió en el sitio). Se corrigen
   las citas, el texto copiado de otro proyecto, las erratas, los totales que no suman y la numeración.
4. **El insumo no se edita.** Siempre se escribe una copia `..._CORREGIDA.docx` o `.xlsx`.

## Datos que hay que pedir (si faltan)
- Los Word y Excel de la arquitecta: memoria descriptiva, programación de áreas y borrador del cuadro de incompatibilidades.
- **El texto de cada norma citada** (PDF o escaneo). Si una norma no se entregó, sus índices quedan "por cotejar" y no se inventan.
  Ejemplo: la R.V.M. 208-2019-MINEDU llegó después; recién entonces se cotejaron los cuadros 12, 20, 21, 22, 23, 29, 31 y 40.
- El tipo de servicio y su marco sectorial. Un hogar de refugio se rige por la Ley 30364 y la R.M. 150-2016-MIMP; un CAR por el D.Leg. 1297.
  Si el servicio es otro, preguntar su marco.
- Los datos del terreno: poligonal y área, colindantes, usos dentro de 100 m, UTM referencial, vía de acceso y titular.
- El índice de láminas vigente, para el listado de planos de la memoria.
- La población: residentes, plazas, personal por turno.

## A. Corrección de la memoria descriptiva y de la programación (copia con el mismo formato)
Técnica con python-docx: abrir el original, editar el texto **solo en los runs que lo contienen** y guardar con otro nombre.
- Función de reemplazo que localiza el texto viejo en la concatenación de los runs del párrafo. Escribe el nuevo en el primer run
  afectado y vacía solo los siguientes que lo contenían. No hay que tocar los runs de hipervínculos: una versión anterior duplicaba
  su texto.
- Llevar una lista de cambios (viejo → nuevo) para la nota interna y comprobar que cada texto buscado exista. Si no está, detenerse.
- Conservar todas las imágenes: contarlas antes y después (32 en el Refugio y 30 en Varones, sin pérdidas).
- Las tablas nuevas, como los cuadros de ubicación, se insertan copiando una tabla modelo del mismo documento para heredar su estilo.

Qué se corrige (patrones reales encontrados):
- **Texto copiado de un colegio:** "Institución Educativa", "I.E.", "UP", "aulas", "aprendizaje", "infraestructura educativa", la NTIE
  001-2017 (derogada) y la R.V.M. 307-2019 (racionalización magisterial). Se pasan a "predio del hogar / del CAR", "ambientes", etc.
- **Datos del terreno:** titular (Gobierno Regional, no "Aldea Infantil"), "0.085562 ha" → 0.85562 ha, "8,556.24. m²", áreas sin
  unidad, pendiente "1. %", "TOLERANCIAS CATAS", leyendas repetidas, imágenes numeradas del 1 al n.
- **Normas mal citadas:** EM.110 (confort térmico, no A.030), "R.V.N", "SEMAMHI" → SENAMHI, D.L. 25884 → **Decreto Ley 25844**, "Ley Orgánica
  de Municipales" → Municipalidades. Agregar la A.090 cuando falta.
- **Drenaje:** "cunetas existentes" → drenaje pluvial del proyecto.
- **Programa:** el subtotal mal rotulado y el total que no suma. El cerco va en ml y no suma área; la fórmula omitía el estacionamiento
  (Varones: 4,205.30 → 4,281.52 m²). Se corrigen las citas normativas del programa para que coincidan con las del sustento,
  sin tocar las áreas.
- **Excel de programación:** fórmulas rotas, `#REF!` eliminado, unidades (m2), erratas. Recalcular y verificar que no quede ningún "#".
- **Listado de planos "(POR DEFINIR)"** → las láminas del índice vigente de la arquitecta (89 en Varones; 108, luego 155, en el Refugio).
- **Sustento pegado dentro de la memoria:** renumerar dentro del numeral que le toca (3.2.1 a 3.2.11) y renumerar las tablas.
- **Análisis de ubicación vacío** (solo el título): llenar el 2.3.1 con el método y el Cuadro de 18 incompatibilidades, y el 2.3.2 con
  el Cuadro de condiciones del servicio y la conclusión. La numeración de los cuadros sigue la del documento (si los N.° 1 a 3 son de
  topografía, el de incompatibilidades es el N.° 4).
- **Índice:** se pone en la página 2. Es un campo TOC `\o "1-3" \h \z \u` con nivel de esquema (`w:outlineLvl`) en cada título,
  entradas con tabulación derecha de puntos y `w:updateFields` en settings. Las páginas se calculan convirtiendo a PDF con LibreOffice
  y buscando cada título con pdftotext. Si falta Arial Narrow, usar una fuente métricamente igual para paginar como Word.

## B. Análisis de incompatibilidades de ubicación
Estructura del Word: generalidades (servicio y exigencias de ubicación), datos del predio (poligonal, área, colindantes, usos
dentro de 100 m), marco normativo, método, **Cuadro N.° 1**, **Cuadro N.° 2**, usos colindantes y conclusiones. El cuadro va en
una sección apaisada.

Método: área de influencia medida **desde el lindero** (50 / 100 / 150 / 200 m según el dispositivo). Cada fila lleva la
incompatibilidad, el dispositivo legal, la distancia mínima o el criterio, la condición encontrada y el resultado.

Cuadro N.° 1 (18 dispositivos del cuadro MINEDU, distancia o criterio):
1 velatorios y cementerios, D.S. 003-94-SA (150 m) · 2 establecimientos de salud, NTS 113 y 119-MINSA (100 m) · 3 plantas envasadoras
de GLP, D.S. 027-94-EM (100 m) · 4 grifos y gasocentros, D.S. 054-93-EM mod. 037-2007-EM (50 m) · 5 venta y consumo de bebidas
alcohólicas, Ley 28681 y D.S. 012-2009-SA (100 m) · 6 plantas de abastecimiento de combustibles, D.S. 045-2001-EM (100 m) · 7 fajas
marginales, D.S. 001-2010-AG · 8 ductos de hidrocarburos, D.S. 081-2007-EM (200 m) · 9 pozos de hidrocarburos, D.S. 032-2004-EM ·
10 aeródromos, D.S. 050-2001-MTC (superficies limitadoras; dar la distancia real al aeropuerto: Tarapoto ~3.5 km, pista 17/35) ·
11 servidumbre de líneas aéreas, CNE Suministro 2011 · 12 electroductos, **D.L. 25844** · 13 restricciones radioeléctricas,
R.M. 120-2005-MTC/03 · 14 PTAR de terceros, OS.090 · 15 derecho de vía, D.S. 034-2008-MTC (las obras, incluido el colector,
quedan dentro del lindero) · 16 vías férreas, D.S. 032-2005-MTC · 17 casinos y tragamonedas, Ley 27153 · 18 hostales, peñas,
discotecas, bingos y billar, Ley 27972 art. 79.

Cuadro N.° 2 (8 condiciones propias del servicio): zonificación compatible (A.090 art. 3); zona tranquila y no aislada (lineamientos
2.1); servicios de apoyo cercanos de salud, seguridad y justicia, con nombre y distancia; accesos sin estudio de impacto vial si hay
menos de 500 personas (A.090 art. 4); seguridad frente a agresiones (cerco, caseta, CCTV; lineamientos 2.4); reserva del uso y
privacidad (2.2 y 2.3); servicios básicos (2.8; A.040 art. 7 d); protección frente a lluvias (OS.060, drenaje del proyecto).

Marco: Ley y reglamento sectoriales del servicio; A.090 arts. 3 y 4; A.040 art. 7 b (solo para los ambientes educativos del servicio);
el cuadro MINEDU (R.V.M. 010-2022 o 068-2025) **como lista de verificación sectorial**; R.V.M. 208-2019 art. 8 c; lineamientos
ONU-Habitat / CONAVIM 2.1 a 2.8.

Matriz Excel: hoja CUADRO 1 (con fórmulas de estado y área de influencia), hoja CONDICIONES (del hogar o del CAR) y hoja RESUMEN con
COUNTIF de ambos cuadros. Se conservan los "CUMPLE" de campo de la arquitecta; solo se ordenan y se corrigen los textos.

## C. Sustento normativo del programa arquitectónico
1. Leer la programación (zona, ambiente, cantidad, capacidad, índice, área unitaria, total) **sin modificarla**.
2. A cada ambiente asignarle **la norma que le corresponde de verdad**, con artículo y cuadro. Por ejemplo: sala de reuniones con la
   A.090 art. 11 (1.0 m²/pers.) o la R.V.M. 208 cuadro 29 (1.50); oficinas con la A.080 art. 6; caseta con la 208 cuadro 40 (3.00);
   aula con la 208 cuadro 12 (2.00); SUM con la 208 cuadro 22 (1.00, máx. 300 m²); tópico con el cuadro 31 (9.00); lavandería con el
   12.2.1 i; almacén general con el 12.3.1 (mín. 10 m²); servicios higiénicos del personal con la A.090 art. 15; estacionamientos con
   la A.090 art. 17; nivel inicial con la R.V.M. 104-2019; hospedaje con la A.030 (anexos).
3. Cálculo: área mínima = capacidad × índice, o el área mínima fija de la norma. Resultado: **CUMPLE** si hay índice y el área lo
   alcanza; **CONFORME** si la norma no da índice y el sustento es cualitativo. Comparar además con la superficie sugerida de los
   lineamientos ONU-Habitat (EN RANGO / SUPERA), solo como referencia de buena práctica.
4. Verificaciones de la zona residencial: plazas, porcentaje de habitaciones con baño, baños compartidos por criterio de albergue
   (A.030) y de lineamientos, población frente a la capacidad sugerida.
5. Word para el expediente: marco normativo con el texto transcrito de cada artículo, población, sustento por zona y ambiente
   (tabla con área requerida, área del proyecto y superficie sugerida), criterios cualitativos y conclusiones. Sin capítulo
   de observaciones.
6. Matriz Excel con fórmulas: MATRIZ (columnas: zona, ambiente, cant., capacidad, I.O., norma, área mín. de la norma, área mín.
   calculada `=SI(Y(ESNUMERO(D);ESNUMERO(E));D*E;...)`, área del proyecto, resultado `CUMPLE/NO CUMPLE/CONFORME`, lineamientos mín. y
   máx., EN RANGO/SUPERA, total y sustento), RESIDENCIAL, ÍNDICES, NORMAS y RESUMEN (COUNTIFS y SUMIF). Fila de zona en granate claro.
7. Nota interna: citas corregidas; ambientes a revisar (garita contada dos veces, totales digitados, cocina o despensa bajo lo
   sugerido, baños compartidos, ambientes faltantes como el cuarto del personal nocturno o la sala de adolescentes); cotejo con la norma
   recién entregada y puntos para que ella decida.

## Formato de los entregables
- Word A4, Arial Narrow 11 pt, títulos en granate `7B1E2B`, encabezado con el nombre corto, CUI y especialidad, pie con "Página X de Y".
  Tablas con encabezado repetido, filas que no se parten y "Fuente:" debajo. Propiedades del documento: autor vacío.
- Carátula propia si el usuario la pide (escudo del Gobierno Regional, servicio, proyecto con CUI, foto y fecha).
- Nombres: `SUSTENTO_NORMATIVO_PROGRAMA_ARQUITECTONICO_<PROY>.docx`, `MATRIZ_..._<PROY>.xlsx`,
  `ANALISIS_INCOMPATIBILIDADES_UBICACION_<PROY>.docx`, `MEMORIA_DESCRIPTIVA_ARQUITECTURA_<PROY>_CORREGIDA.docx` y la nota
  `REVISION_..._<PROY>.docx` (marcada como uso interno).

## Verificación final (antes de entregar)
- [ ] Texto del original y de la copia comparados: solo cambió lo de la lista de cambios. Imágenes, tablas y áreas iguales.
- [ ] Ninguna área ni cantidad de la programación cambió; los totales nuevos se explican en la nota.
- [ ] Cada cita tiene número de norma, artículo, numeral o cuadro, y está en el texto entregado. Lo no entregado dice "por cotejar".
- [ ] Ningún texto de colegio queda en un documento de hogar o CAR (buscar: educativa, I.E., UP, aula, aprendizaje, NTIE).
- [ ] D.L. 25844, Ley Orgánica de Municipalidades, SENAMHI, EM.110: bien escritos.
- [ ] Excel recalculado sin "#" ni "NO CUMPLE" inesperados; el RESUMEN cuadra con el Word.
- [ ] Ninguna "observación" dentro del expediente; todo va en la nota interna.
- [ ] El listado de planos de la memoria es igual al índice de láminas vigente.
- [ ] El índice del Word tiene páginas reales y se actualiza al abrir.
- [ ] No hay datos de otro proyecto (CUI, colindantes, nombre corto).

## Errores que el usuario ya corrigió (no repetirlos)
- **Primer sustento con observaciones:** tenía un capítulo de observaciones y sugerencias. El usuario pidió que protegiera a la
  arquitecta: el sustento solo sustenta y las observaciones pasan a la nota interna.
- **Ubicación hecha como para un colegio:** se partió del borrador de la usuaria, que era el cuadro de un local educativo, para un hogar
  de refugio. Se rehízo con la mirada del hogar: marco sectorial, textos y el Cuadro 2 de condiciones propias.
- **Programación tocada:** no se cambian áreas ni la programación de la usuaria; los totales mal sumados se corrigen solo en la copia
  y se informan.
- **Norma no entregada:** sus índices no se dan por ciertos; quedan "por cotejar" hasta recibir el texto.
- **Vigencia de la norma:** el borrador del Refugio citaba la R.V.M. 010-2022 y el de Varones la 068-2025. No se cambia la que cita
  la arquitecta; la vigencia se plantea en la nota interna para que ella decida.
- **Proyecto equivocado:** se hicieron opciones de carátula para el CAR Varones cuando eran para el Hogar de Refugio. Confirmar siempre
  el proyecto (nombre y CUI) antes de producir.
- **Hipervínculos duplicados:** el reemplazo de texto duplicaba los hipervínculos. Editar solo los runs afectados y comparar el texto.
- **Pedirle trabajo al usuario:** "eso que me pides para yo hacer, hazlo tú o déjalo así". Los pendientes se resuelven con criterio
  y se documentan. Solo se pregunta lo que de verdad decide la arquitecta, como la garita repetida, los totales digitados o el nombre
  del lugar (Polvoraico o Polvorico).
- **Documento irrefutable:** el usuario quiere que "la Contraloría no intervenga". Cada criterio lleva su cita exacta y su cálculo;
  nada queda afirmado sin norma o sin dato del plano.
