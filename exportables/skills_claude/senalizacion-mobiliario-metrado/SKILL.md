---
name: senalizacion-mobiliario-metrado
description: "Para cualquier edificación (colegio, establecimiento de salud, municipalidad, albergue, mercado, oficinas): leer de los planos DXF de evacuación y señalización y de equipamiento y mobiliario lo dibujado y rotulado (bloques, etiquetas de código, cuadros, leyenda, rutas, zonas, imágenes pegadas), armar una fuente única de datos y producir el metrado en Excel con fórmulas, la memoria descriptiva y las especificaciones técnicas en Word, vistas PNG de las plantas, el cotejo con el metrado del cliente, la nota de observaciones (revisión interna) y el documento de subsanación. Regla: cantidad = lo dibujado o rotulado en planta; ajustes solo con su motivo. Usar cuando se pida metrar, revisar o documentar señalización, evacuación, seguridad, equipamiento o mobiliario de un expediente."
---
# Evacuación y señalización / equipamiento y mobiliario: del plano al metrado y los documentos

Método general para cualquier tipo de edificación y cualquier codificación de láminas del cliente. Códigos de lámina, de
muebles y de edificaciones, cantidades, población, colores y alturas salen de los planos y documentos del proyecto nuevo; los de
proyectos anteriores están solo en el apartado final **"Ejemplo de referencia"**.

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

## 1. Principio rector (criterios generales del usuario)
- **Manda el plano: cantidad = lo dibujado o rotulado en la planta.** La leyenda y los cuadros del plano son referencia; si
  contradicen la planta, rige la planta y la diferencia se anota con su motivo. Nada se ajusta sin un motivo escrito.
- Se cuenta por la **etiqueta escrita en la planta** (código sobre cada mueble o equipo), no por lo que diga el cuadro.
- **Evacuación y señalización es una sola especialidad** (un metrado, una memoria, unas especificaciones). Extintores, luces de
  emergencia y detectores son partidas de seguridad y señalización, no de mobiliario (criterio por defecto; confirmar si el cliente
  los agrupa distinto).
- Los documentos del expediente quedan **limpios** (sin columnas LEYENDA/DIFERENCIA, sin "observaciones"); todo cotejo y crítica al
  plano va en documentos de revisión interna aparte (nota de observaciones, comparación y subsanación), nunca en el expediente.
- El DXF y el metrado del cliente se leen sin modificarlos (trabajar sobre copia).
- Rótulos ambiguos se interpretan con el programa del local y se confirman (p. ej. SS.HH. "mixto" en un local de un solo sexo).

## 2. Insumos y datos que hay que pedir
| Grupo | Qué pedir | Para qué |
|---|---|---|
| Proyecto | Nombre completo tal cual el rótulo, CUI, entidad, ubicación, fecha del rótulo, tipo de edificación y uso | encabezados, normas, aforo |
| Planos | DXF de señalización, evacuación y mobiliario (si pesan cientos de MB, comprimidos) y **PDF de cada lámina** si hay imágenes pegadas | lectura y ubicación |
| Índice | Índice de láminas de arquitectura vigente (códigos finales aunque el rótulo diga otra cosa) | citas correctas |
| Edificaciones | Lista de edificaciones o bloques con su código y sus ambientes por nivel | asignar cada símbolo |
| Población | Ocupantes por tipo según el uso: alumnos y docentes, pacientes y personal, residentes y cuidadores, trabajadores y público, visitantes | aforo, medios de evacuación |
| Metrado del cliente | Excel de la arquitecta o del cliente | solo cotejo |
| Formato | Word de memoria o especificaciones del cliente, si quiere que se respete; memoria modelo que considere buena | estructura y extensión |
| Datos no dibujados | Peso y tipo de extintor, altura de instalación, tipo de luminaria, material de señales, color del proyecto | se adoptan con fuente si no los da |
| Alcance | Si se pide solo metrado, o también memoria, especificaciones, nota y subsanación | evitar trabajo no pedido |

## 3. Lectura del DXF (Python + ezdxf, espacio modelo, coordenadas reales)
**Señalización:**
1. Leyenda (bloque de leyenda) fila por fila: símbolo (nombre de bloque), descripción, altura de instalación, cantidad.
2. Cada inserción de bloque de señal en la planta: posición = **centro del dibujo sin textos** (los bloques pueden tener la geometría
   desplazada del punto de inserción; los textos internos desplazan el centro). Recorrer bloques anidados dentro de los bloques de
   cada edificación, líneas, sombreados y textos sueltos: no dejar símbolos sin contar.
3. Edificación de cada señal: contorno del bloque de la planta de cada edificación con un margen (p. ej. 0.60 m) para señales de
   fachada; en aleros que se traslapan, la edificación que la contiene con más holgura; fuera de todo = EXT.
4. Copias sueltas fuera del terreno: no se metran (se informan). Símbolos superpuestos: detectar duplicados.
5. Bloques distintos que son el mismo símbolo (uno contiene al otro): se suman en una partida.
6. **Imágenes pegadas (OLE2FRAME)**: el DXF solo guarda su tamaño, no posición ni contenido. Contar las de igual tamaño; ubicarlas en
   el PDF de la lámina (calibrar la hoja con rótulos de posición conocida, p. ej. los de cada edificación, por mínimos cuadrados, y
   pasar el centro de cada imagen a coordenadas). Sin PDF: cantidad de la leyenda o reparto del metrado del cliente si suma igual,
   con la fuente escrita. Comprobación independiente: contar en el PDF las palabras de las señales que trae como texto.
**Evacuación:** rutas (rótulo con número y distancia: número, longitud, edificación de origen; verificar que no falten ni se repitan
y que la distancia cumpla la RNE A.130 vigente para el uso y si hay rociadores); zonas de reunión pintadas (círculos: radio exterior e
interior → área del anillo π(R² − r²) con fórmula; número y aforo); números repetidos se renumeran al siguiente libre y se informa.
**Mobiliario y equipamiento:**
1. Cuadros de equipamiento por ambiente y edificación: columnas por su fila de encabezado (código, descripción, und, cantidad) o a
   distancia fija del centro del título; cada fila desde su código con la descripción y cantidad a la misma altura; la sección
   (equipo, mobiliario, implementos, seguridad) = último encabezado por encima.
2. Etiquetas de código sobre cada mueble (capas de texto de mobiliario, textos dentro de bloques y **directrices múltiples anidadas
   hasta 6 niveles**), asignadas a la edificación por la planta que las contiene (títulos de planta con nivel y edificación).
3. Láminas por su marco/presentación (código, título, escala, fecha). Guardar todo en un JSON de lectura.

## 4. Fuente única de datos
Un solo módulo/archivo de datos alimenta metrado, memoria, especificaciones, nota y subsanación (así todos dicen lo mismo):
- Datos del proyecto (nombre completo, CUI, corto, especialidad "ARQUITECTURA - EVACUACIÓN Y SEÑALIZACIÓN" o "... - EQUIPAMIENTO Y
  MOBILIARIO" o la que use el cliente, ubicación, fecha del rótulo), edificaciones y su lámina.
- **Catálogo de partidas** con grupo, descripción, und, dimensiones, material, altura de instalación, función y bloques que la
  representan. Grupos de señalización por defecto: 01 evacuación y emergencia (salida, dirección de evacuación, zona segura en caso
  de sismo, aforo, pintura de zona de reunión en m²), 02 equipos contra incendio, 03 advertencia, 04 obligación y prohibición (si
  las hay), 05 informativas, 06 equipos (extintores uno por señal de extintor, luces de emergencia, detectores). Dimensiones, alturas
  y materiales del plano o de la memoria de arquitectura; si no los dan, los de la NTP 399.010-1 y la RNE A.120 (braille donde
  aplique), anotados como adoptados.
- Mobiliario: familias de código del cliente (p. ej. E equipos, M mobiliario, K implementos); numeración según el árbol del
  proyecto (título de arquitectura → mobiliario y equipamiento → equipos / mobiliario / implementos por ambiente). Una descripción
  por código (corregir filas que traen la de otro código). Mismo código para dos muebles distintos → dos partidas con clave propia.
- **CORRECCIONES** (edificación, ambiente, código, cantidad adoptada, motivo: "En la planta hay 3 ...; el cuadro dice 2") y
  **AGREGADOS** (rotulados en planta y ausentes del cuadro). Implementos que el plano rotula uno por tipo → rige el cuadro, salvo que
  la planta rotule más piezas. Cuadros repetidos o mal titulados: se asignan al ambiente real o no se metran (anotado).
- Datos que el plano no define y se adoptan (peso del extintor, alturas): con su fuente.
- `comprobacion()`: suma por edificación = total; sin duplicados; en equipos y mobiliario adoptado = planta; en implementos
  adoptado ≥ planta. Debe dar 0 errores.

## 5. Metrado (Excel con fórmulas, formato del expediente)
- Señalización: RESUMEN (partidas y metrado enlazado) · METRADO por edificación (una columna por edificación y EXT; total `=SUM`) ·
  ZONAS DE EVACUACIÓN (n.°, radios, área del anillo con fórmula) · RUTAS DE EVACUACIÓN (n.°, origen, L, tiempo a velocidades de
  marcha de referencia, verificación A.130) · POBLACIÓN · SEÑALES (dimensiones, material, altura por partida).
- Mobiliario: RESUMEN (metrado por `SUMIF` sobre el detalle) · METRADO POR AMBIENTE (cada ítem de cada ambiente) · POR EDIFICACIÓN
  (`SUMIFS`, totales que cruzan con el RESUMEN).
- Estilo por defecto: Arial 9, encabezados con fondo del color del proyecto y texto blanco, totales con fondo claro, bordes finos
  grises, título en la fila 1, proyecto con CUI y la lámina fuente como referencia neutra. Recalcular con LibreOffice y comprobar sin
  errores `#`. Si el cliente da su formato de planilla, manda el suyo.

## 6. Memoria descriptiva (Word; extensión acorde al modelo del usuario, "muy pobre" no se acepta)
- **Señalización/evacuación**: generalidades (ubicación con UTM referencial, accesos, objetivos, normas: RNE A.120, A.130, la norma
  del uso — A.040 educación, A.050 salud, A.080 oficinas u otra —, NTP 399.010-1, G.050); descripción del local con los ambientes de
  cada edificación leídos del plano; peligros por edificación; población y aforo (índices de ocupación del uso); medios de evacuación
  (ancho de puertas y pasajes por persona, rutas, distancias, tiempos, zonas de reunión con capacidad); organización (comité,
  brigadas, personal); protocolos (sismo, incendio, lluvias intensas, fuga de gas, corte de energía y los propios del uso);
  directorio de emergencias; protección contra incendio (extintores por edificación); señalización con clasificación NTP 399.010-1,
  tabla de simbología con la imagen de cada señal y una ficha por señal; distribución por edificación con su planta; mantenimiento;
  conclusiones; láminas.
- **Mobiliario**: generalidades; criterios de diseño por tipo de usuario (niños, adultos mayores, personas con discapacidad,
  pacientes, público); equipamiento de cada edificación y ambiente con su planta y **un párrafo por ambiente que nombre cada código con
  su cantidad**; características por familia (fichas compartidas con las especificaciones); sustento de cantidades y capítulo
  "Compatibilización del plano con el metrado" (método, tabla de ajustes con motivo); resumen; suministro, instalación y mantenimiento.
- Imágenes de señales dibujadas a escala con forma, color de seguridad y contraste NTP (verde evacuación, rojo incendio/prohibición,
  amarillo advertencia, azul obligación/información), pictograma, texto y placa braille real. Formato y carátula de las memorias del
  proyecto; índice lleno (actualizado con LibreOffice) antes de entregar.

## 7. Especificaciones técnicas
Partidas, numeración, unidades y cantidades = metrado, en el mismo orden. Generalidades + una ficha por partida: DESCRIPCIÓN (con
imagen de la señal o del mueble), ubicación/ambientes donde va (de las láminas), MATERIALES/CARACTERÍSTICAS, EQUIPOS Y HERRAMIENTAS,
PROCEDIMIENTO (instalación, altura, fijación), CONTROL DE CALIDAD, SEGURIDAD, UNIDAD, MÉTODO DE MEDICIÓN (und colocada y verificada;
m² de pintura), FORMA DE PAGO. Si el cliente entrega su Word: solo las partidas del metrado, su texto e imágenes tal cual, borrar lo
ajeno (otro proyecto, otra medida), completar lo faltante con su formato ("Ídem" para repetidas), proyecto/CUI/encabezado propios
en todas las páginas.

## 8. Vistas PNG
DXF pesados agotan memoria con el render completo: dibujar solo las entidades que tocan la caja de cada planta (muros rellenos,
aparatos, mobiliario, directrices y etiquetas) o directo con matplotlib (bloques explotados, rellenos solo en símbolos pequeños);
fondo blanco: pasar lo blanco a negro sin tocar el negro (las etiquetas blancas desaparecen). Salidas: planta general, planta por
edificación (con margen) y **figura de conteo** (círculo de color sobre cada símbolo contado) para la nota. Revisar que se vean.

## 9. Documentos de revisión interna (no van al expediente)
1. **Nota de observaciones**: lectura del plano, cotejo leyenda / cuadros / planta / metrado por edificación, criterio de cada
   cantidad adoptada, observaciones numeradas que debe corregir el autor del plano (cuadros mal titulados, descripciones corridas,
   códigos repetidos, leyenda con otra cantidad, rótulo de otro proyecto, alturas distintas, erratas) y puntos a confirmar.
2. **Comparación con el metrado del cliente** (Excel): por partida (cliente, plano, propio, diferencia con fórmula), por
   edificación y ERRORES DEL ARCHIVO (celdas que enlazan a la celda equivocada, hojas de otro proyecto, títulos repetidos, fechas,
   `#REF!`).
3. **Subsanación**: (1) observaciones ya subsanadas en metrado, memoria y especificaciones; (2) correcciones pendientes en cada lámina
   para que cuadre con los documentos; (3) correcciones del metrado del cliente; (4) decisiones que quedan al autor del plano.

## 10. Verificación final
- [ ] `comprobacion()` con 0 errores; total por partida = suma por edificación; sin símbolos sin edificación salvo los justificados.
- [ ] Metrado = memoria = especificaciones (mismas partidas, cantidades y descripciones; cotejo automático).
- [ ] Cada ajuste con su motivo; nada inventado (lo no definido, adoptado con fuente y anotado para confirmar).
- [ ] Documentos del expediente sin columnas de cotejo ni observaciones; nombre y CUI correctos; sin rastros de IA; firmas en blanco.
- [ ] Códigos de lámina = índice de arquitectura vigente; normas del uso correcto; plantas PNG visibles; índice de los Word lleno.
- [ ] Nada heredado de otro proyecto (códigos, cantidades, población, color, texto de la memoria modelo).

## 11. Errores que el usuario ya corrigió (lecciones generales)
- Contar por el cuadro en vez de la etiqueta escrita en la planta.
- Tratar una imagen pegada como bloque: no tiene posición en el DXF; ubicarla con el PDF de la lámina.
- Metrar un rótulo ambiguo al pie de la letra sin mirar el programa del local (SS.HH. "mixto" en un local de un solo sexo).
- Memoria "muy pobre": ampliar con la estructura completa del modelo; nombrar cada código en la memoria; imágenes de plantas que no
  se veían (etiquetas blancas).
- Dejar en el metrado del expediente columnas LEYENDA/DIFERENCIA/SIN UBICAR o la hoja de leyenda: el cotejo va solo a revisión interna.
- Separar evacuación y señalización en dos especialidades (es una sola); meter extintores en mobiliario.
- Copiar a ciegas el metrado o el Word del cliente: pueden traer hojas y partidas de otros proyectos, códigos repetidos, `#REF!` y
  enlaces a la celda equivocada.
- No leer directrices múltiples anidadas en bloques (faltaban equipos rotulados así).
- Medidas distintas de las del plano (espesor de línea de las zonas pintadas): manda lo dibujado.

## Ejemplo de referencia (valores de proyectos anteriores; reemplazar por los del proyecto nuevo)
- CAR Varones (CUI 2705619): láminas SE-S-01, SE-E-01 y MB-01 a MB-09; memoria de 34 páginas; 10 credenzas M44 rotuladas en el
  dormitorio de E-07 aunque el cuadro decía armarios M37.
- Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514): láminas SE-S-02 (según índice), SE-E-01 y EM-01 a EM-07; edificaciones
  "EDIF. 01" a "EDIF. 09" usadas para calibrar el PDF; 39 imágenes de riesgo eléctrico ubicadas con el PDF; SS.HH. "mixto" = mujeres;
  error del archivo del cliente HR!E26 → HD!K107 en vez de K112; numeración 03 ARQUITECTURA → 03.01 MOBILIARIO Y EQUIPAMIENTO.
- Valores adoptados allí: salida con braille 0.30 x 0.20 a 2.10 m; dirección de evacuación 0.20 x 0.30; zona segura 0.20 x 0.30 a
  1.80 m; extintor con borde inferior a 1.80 m (PQS ABC de 6 o 9 kg según la memoria de arquitectura); riesgo eléctrico a 1.10 m;
  luces LED ≥ 90 min; PVC celtex 3 mm con vinil fotoluminiscente; margen de fachada 0.60 m; ancho 0.005 m/persona; distancia
  ≤ 45 m sin rociadores; tiempos a 0.60 y 1.00 m/s; zonas pintadas de 0.15 m; color de encabezado granate 7B1E2B con total F2E6E8.
