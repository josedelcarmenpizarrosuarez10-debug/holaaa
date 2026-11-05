---
name: senalizacion-mobiliario-metrado
description: "A partir de los planos DXF de la arquitecta de evacuación y señalización (SE-S, SE-E) y de equipamiento y mobiliario (EM, MB), leer lo dibujado y rotulado (bloques, etiquetas de código, cuadros, leyenda, rutas, zonas), armar una fuente única de datos y producir el metrado en Excel con fórmulas, la memoria descriptiva y las especificaciones técnicas en Word, vistas PNG de las plantas, el cotejo con el metrado de la usuaria, la nota de observaciones (revisión interna) y el documento de subsanación (subsanadas en documentos / pendientes en láminas). Regla: cantidad = lo dibujado o rotulado en planta; ajustes solo con su motivo. Usar cuando se pida metrar, revisar o documentar señalización, evacuación, seguridad, equipamiento o mobiliario de un expediente."
---
# Evacuación y señalización / equipamiento y mobiliario: del plano al metrado y los documentos

Proyectos de referencia (ejemplos, no mezclar datos): CAR Varones (CUI 2705619: láminas SE-S-01, SE-E-01 y MB-01 a MB-09) y Hogar de
Refugio Temporal "Mujeres Violentadas" (CUI 2675514: láminas SE-S-02, SE-E-01 y EM-01 a EM-07).

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

## 1. Principio rector
- **Manda el plano: cantidad = lo dibujado o rotulado en la planta.** La leyenda y los cuadros del plano son referencia; si
  contradicen la planta, rige la planta y la diferencia se anota con su motivo. Nada se ajusta sin un motivo escrito.
- Se cuenta por la **etiqueta escrita en la planta** (código sobre cada mueble), no por lo que diga el cuadro (p. ej. 10 credenzas
  M44 rotuladas junto a las camas aunque el cuadro decía armarios M37).
- **Evacuación y señalización es una sola especialidad** (un metrado, una memoria, unas especificaciones). Los extintores son partida
  de seguridad y señalización, no de mobiliario.
- Los documentos del expediente quedan **limpios** (sin columnas LEYENDA/DIFERENCIA, sin "observaciones"); todo cotejo y crítica al
  plano va en documentos de revisión interna aparte (nota de observaciones, comparación y subsanación), nunca en el expediente.
- El DXF y el metrado de la usuaria se leen sin modificarlos (trabajar sobre copia).

## 2. Insumos que hay que pedir
- DXF de la arquitecta (pueden pesar 77–300 MB: pedir comprimido) y, si hay imágenes pegadas, el **PDF de la lámina** (A1).
- Metrado de la arquitecta/usuaria (Excel) para cotejo, y su Word de especificaciones o memoria si quiere que se respete su formato.
- Índice de láminas de arquitectura (códigos vigentes: p. ej. señalización = SE-S-02 aunque el rótulo diga otra cosa).
- Población del local (residentes por plazas del programa, personal, temporales/visitantes), ambientes por edificación.
- Ejemplo de memoria que el usuario considere buena (la del Hogar de Refugio sirvió de modelo para la del CAR Varones).

## 3. Lectura del DXF (Python + ezdxf, espacio modelo, coordenadas reales)
**Señalización (SE-S):**
1. Leyenda (bloque de leyenda) fila por fila: símbolo (nombre de bloque), descripción, altura de instalación, cantidad.
2. Cada inserción de bloque de señal en la planta: posición = **centro del dibujo sin textos** (los bloques tienen la geometría
   desplazada del punto de inserción; el MTEXT del letrero de aforo desplaza el centro). Recorrer bloques anidados dentro de los
   bloques de cada edificación, líneas, sombreados y textos sueltos: no dejar símbolos sin contar.
3. Edificación de cada señal: contorno del bloque de la planta general de cada edificación (E-01...E-nn) con 0.60 m de margen para
   señales de fachada; en aleros que se traslapan, la edificación que la contiene con más holgura; fuera de todo = EXT.
4. Copias sueltas fuera del terreno: no se metran (se informan). Símbolos superpuestos: detectar duplicados.
5. Bloques distintos que son el mismo símbolo (p. ej. "LE" contiene al símbolo de la leyenda de luces): se suman.
6. **Imágenes pegadas (OLE2FRAME)**: el DXF solo guarda su tamaño, no posición ni contenido. Contar las de igual tamaño; ubicarlas en
   el PDF de la lámina (calibrar la hoja con rótulos de posición conocida, p. ej. "EDIF. 01" a "EDIF. 09", por mínimos cuadrados, y
   pasar el centro de cada imagen a coordenadas). Sin PDF: cantidad de la leyenda o reparto del metrado de la usuaria si suma igual,
   con la fuente escrita. Comprobación independiente: contar en el PDF las palabras de las señales que trae como texto.
**Evacuación (SE-E):** rutas (rótulo "RUTA n / DISTANCIA: L m": número, longitud, edificación de origen; verificar que no falten ni se
repitan y que L ≤ 45 m sin rociadores, RNE A.130); zonas de reunión pintadas (círculos: radio exterior e interior → área del anillo
π(R² − r²) con fórmula; número y aforo); números repetidos se renumeran al siguiente libre y se informa.
**Mobiliario (EM/MB):**
1. Cuadros "CUADRO DE EQUIPAMIENTO ... - <ambiente> - EDIFICACIÓN n": columnas por su fila de encabezado (COD., DESCRIPCIÓN, UND.,
   CANTID.) o a distancia fija del centro del título; cada fila desde su código con la descripción y cantidad a la misma altura;
   la sección (EQUIPO, MOBILIARIO, IMPLEMENTOS, SEGURIDAD) = último encabezado por encima.
2. Etiquetas de código sobre cada mueble (capas de texto de mobiliario, textos dentro de bloques y **directrices múltiples anidadas
   hasta 6 niveles**), asignadas a la edificación por la planta que las contiene (títulos "PRIMER NIVEL (EDIFICACIÓN n)").
3. Láminas por su marco/presentación (código, título, escala, fecha). Guardar todo en un JSON de lectura.

## 4. Fuente única de datos
Un solo módulo/archivo de datos alimenta metrado, memoria, especificaciones, nota y subsanación (así todos dicen lo mismo):
- Datos del proyecto (nombre completo, CUI, corto, especialidad "ARQUITECTURA - EVACUACIÓN Y SEÑALIZACIÓN" o "... - EQUIPAMIENTO Y
  MOBILIARIO", ubicación, fecha del rótulo), edificaciones y su lámina.
- **Catálogo de partidas** con grupo, descripción, und, dimensiones, material, altura de instalación, función y bloques que la
  representan. Señalización (grupos): 01 evacuación y emergencia (salida con braille 0.30 x 0.20 a 2.10 m; dirección de evacuación
  0.20 x 0.30; zona segura en caso de sismo 0.20 x 0.30 a 1.80 m; letrero de aforo; pintura de zona de reunión en m²), 02 equipos
  contra incendio (ubicación de extintor sobre el equipo, borde inferior a 1.80 m), 03 advertencia (riesgo eléctrico a 1.10 m),
  04 informativas (SS.HH. mujeres/varones/discapacidad, punto ecológico), 05 equipos (extintor PQS tipo ABC uno por señal de extintor,
  luces de emergencia LED ≥ 90 min, detector de humo). Materiales NTP 399.010-1: PVC celtex 3 mm con vinil fotoluminiscente o adhesivo
  y placa de acrílico con braille grado 1 (RNE A.120).
- Mobiliario: códigos E (equipos), M (mobiliario), K (implementos); numeración 03 ARQUITECTURA → 03.01 MOBILIARIO Y EQUIPAMIENTO →
  .01 equipos, .02 mobiliario, .03 implementos por ambiente (.03.nn.mm). Una descripción por código (corregir filas que traen la de
  otro código). Mismo código para dos muebles distintos → dos partidas con clave propia (p. ej. M16 mesa de corte textil / mesa de trabajo).
- **CORRECCIONES** (edificación, ambiente, código, cantidad adoptada, motivo: "En la planta hay 3 sillones M32...; el cuadro dice 2")
  y **AGREGADOS** (rotulados en planta y ausentes del cuadro). Implementos K: el plano rotula uno por tipo → rige el cuadro, salvo que
  la planta rotule más piezas. Cuadros repetidos o mal titulados: se asignan al ambiente real o no se metran (anotado).
- Datos que el plano no define y se adoptan (peso del extintor 6 o 9 kg según la memoria de arquitectura, alturas): con su fuente.
- `comprobacion()`: suma por edificación = total; sin duplicados; en E y M adoptado = planta; en K adoptado ≥ planta. Debe dar 0 errores.

## 5. Metrado (Excel con fórmulas, formato del expediente)
- Señalización: RESUMEN (partidas y metrado enlazado) · METRADO por edificación (columnas E-01...E-nn, EXT; total `=SUM`) · ZONAS DE
  EVACUACIÓN (n.°, radios, área del anillo con fórmula) · RUTAS DE EVACUACIÓN (n.°, origen, L, tiempo a 0.60 y 1.00 m/s, verificación
  A.130) · POBLACIÓN · SEÑALES (dimensiones, material, altura por partida).
- Mobiliario: RESUMEN (03.01..., metrado por `SUMIF` sobre el detalle) · METRADO POR AMBIENTE (cada ítem de cada ambiente) · POR
  EDIFICACIÓN (`SUMIFS`, totales que cruzan con el RESUMEN).
- Estilo: Arial 9, encabezados con fondo del color del proyecto (p. ej. granate 7B1E2B) y texto blanco, totales con fondo claro
  (F2E6E8), bordes finos 808080, título en la fila 1, proyecto con CUI y fuente "Lámina SE-S-02" como referencia neutra. Recalcular con
  LibreOffice y comprobar sin errores `#`.

## 6. Memoria descriptiva (Word, 26–40 páginas; "muy pobre" no se acepta)
- **Señalización/evacuación**: generalidades (ubicación con UTM referencial, accesos, objetivos, normas: RNE A.120, A.130,
  NTP 399.010-1, G.050); descripción del local con los ambientes de cada edificación leídos del plano;
  peligros por edificación; población y aforo (índices de ocupación); medios de evacuación (ancho de puertas y pasajes 0.005 m/persona,
  rutas, distancias, tiempos, zonas de reunión con capacidad); organización (comité, brigadas, personal); protocolos (sismo, incendio,
  lluvias intensas, fuga de gas, corte de energía, ingreso no autorizado si aplica); procedimiento con directorio de emergencias;
  protección contra incendio (extintores por edificación); señalización con clasificación NTP 399.010-1, tabla de simbología con la
  imagen de cada señal y una ficha por señal; distribución por edificación con su planta; mantenimiento; conclusiones; láminas.
- **Mobiliario**: generalidades; criterios de diseño por tipo de usuario; equipamiento de cada edificación y ambiente con su planta y
  **un párrafo por ambiente que nombre cada código con su cantidad** ("10 credenzas de melamina... (M44)"); características por familia
  (fichas compartidas con las especificaciones); sustento de cantidades y capítulo "Compatibilización del plano con el metrado"
  (método, tabla de ajustes con motivo); resumen; suministro, instalación y mantenimiento.
- Imágenes de señales dibujadas a escala con forma, color de seguridad y contraste NTP (verde evacuación, rojo incendio/prohibición,
  amarillo advertencia, azul información), pictograma, texto y placa braille real. Formato y carátula de las memorias del proyecto;
  índice lleno (actualizado con LibreOffice) antes de entregar.

## 7. Especificaciones técnicas
Partidas, numeración, unidades y cantidades = metrado, en el mismo orden. Generalidades + una ficha por partida: DESCRIPCIÓN (con
imagen de la señal), ubicación/ambientes donde va (de las láminas), MATERIALES/CARACTERÍSTICAS, EQUIPOS Y HERRAMIENTAS, PROCEDIMIENTO
(instalación, altura, fijación), CONTROL DE CALIDAD, SEGURIDAD, UNIDAD, MÉTODO DE MEDICIÓN (und colocada y verificada; m² de pintura),
FORMA DE PAGO. Si la usuaria entrega su Word: solo las partidas del metrado, su texto e imágenes tal cual, borrar lo ajeno (otro
proyecto, otra medida), completar lo faltante con su formato ("Ídem" para repetidas), proyecto/CUI/encabezado propios en todas las páginas.

## 8. Vistas PNG
DXF pesados agotan memoria con el render completo: dibujar solo las entidades que tocan la caja de cada planta (muros rellenos,
aparatos, mobiliario, directrices y etiquetas) o directo con matplotlib (bloques explotados, rellenos solo en símbolos < 3 m);
fondo blanco: pasar lo blanco a negro sin tocar el negro (las etiquetas blancas desaparecían). Salidas: planta general, planta por
edificación (margen 2.5 m) y **figura de conteo** (círculo de color sobre cada símbolo contado) para la nota. Revisar que se vean.

## 9. Documentos de revisión interna (no van al expediente)
1. **Nota de observaciones**: lectura del plano, cotejo leyenda / cuadros / planta / metrado por edificación, criterio de cada
   cantidad adoptada, observaciones numeradas que debe corregir la arquitecta (cuadros mal titulados, descripciones corridas, códigos
   repetidos, leyenda con otra cantidad, rótulo de otro proyecto, alturas distintas, erratas) y puntos a confirmar.
2. **Comparación con el metrado de la usuaria** (Excel): por partida (usuaria, plano, propio, diferencia con fórmula), por
   edificación y ERRORES DEL ARCHIVO (celdas que enlazan mal, p. ej. HR!E26 → HD!K107 en vez de K112; hojas de otro proyecto; títulos
   repetidos; fechas; `#REF!`).
3. **Subsanación**: (1) observaciones ya subsanadas en metrado, memoria y especificaciones; (2) correcciones pendientes en cada lámina
   para que cuadre con los documentos; (3) correcciones del metrado de la usuaria; (4) decisiones que quedan a la arquitecta.

## 10. Verificación final
- [ ] `comprobacion()` con 0 errores; total por partida = suma por edificación; sin símbolos sin edificación salvo los justificados.
- [ ] Metrado = memoria = especificaciones (mismas partidas, cantidades y descripciones; cotejo automático).
- [ ] Cada ajuste con su motivo; nada inventado (lo no definido, adoptado con fuente y anotado para confirmar).
- [ ] Documentos del expediente sin columnas de cotejo ni observaciones; nombre y CUI correctos; sin rastros de IA; firmas en blanco.
- [ ] Códigos de lámina = índice de arquitectura vigente; plantas PNG visibles; índice de los Word lleno.

## 11. Errores que el usuario ya corrigió (no repetirlos)
- Contar por el cuadro en vez de la etiqueta escrita en planta (credenzas M44 en el dormitorio de E-07 del CAR Varones).
- Tratar "atención riesgo eléctrico" como bloque: es imagen pegada sin posición (ubicarla con el PDF de la lámina).
- Metrar SS.HH. "mixto" en un hogar solo para mujeres: son SS.HH. de mujeres (sin partida de mixto).
- Memoria "muy pobre": ampliar con la estructura completa del ejemplo (34 páginas en Varones); no mencionar un código (M44) en la memoria;
  imágenes de plantas que no se veían (etiquetas blancas).
- Dejar en el metrado del expediente columnas LEYENDA/DIFERENCIA/SIN UBICAR o la hoja de leyenda: el cotejo va solo a revisión interna.
- Separar evacuación y señalización en dos especialidades (es una sola); meter extintores en mobiliario.
- Copiar a ciegas el metrado o el Word de la usuaria: traían hojas y partidas de otro proyecto (colegio de 55 aulas, CAR Mujeres,
  I.E. Ofelia Velásquez), códigos repetidos, `#REF!` y enlaces a la celda equivocada.
- No leer directrices múltiples anidadas en bloques (faltaban computadoras, rack, pizarra y un proyector).
- Pintura de zonas con espesor de línea distinto del plano (decía E = 10 cm y el plano dibuja 0.15 m).
