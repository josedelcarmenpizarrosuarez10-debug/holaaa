---
name: expediente-caratulas-lomos-indices
description: "Elaborar las piezas de presentación de un expediente técnico peruano: carátulas en Word (una por página, con la foto del proyecto), carátulas de tomos I a X y lomos de archivador oficio (6.3 y 4.0 cm, 3 por A4) en PowerPoint con tabla de contenido editable, separadores (uno por ítem del índice del cliente, con la foto como marca de agua), índice de planos en Word desde el Excel o los rótulos del PDF del cliente (códigos tal cual), índice general por tomos y encabezados y pies en Word. Usa la paleta guinda y dorado y evita los errores de esquema que impiden abrir los PowerPoint. Usar cuando el usuario pida carátulas, portadas, lomos, separadores, índices de planos o de expediente, encabezados o pies de página, o arreglar uno que no abre o se ve mal."
---

# Carátulas, lomos, separadores e índices del expediente técnico

Proyectos de referencia: CAR Varones (CUI 2705619), Hogar de Refugio Temporal (CUI 2675514) y CAR Mujeres (CUI 2717013), todos de la
Gerencia Territorial Bajo Mayo del Gobierno Regional San Martín, en Morales; también la I.E. N.° 0590 Barranquita (C.I. 468901).

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

## Datos que hay que pedir (si faltan)
- **Nombre completo del proyecto** entre comillas, tal cual el rótulo de las láminas, con su **CUI** (o C.I.); el nombre corto;
  la entidad ("GOBIERNO REGIONAL SAN MARTÍN"), la gerencia ("GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO"), la ubicación
  (distrito, provincia, departamento) y la **fecha tal como la escribe el cliente** ("SETIEMBRE - 2026" o "SEPTIEMBRE - 2026").
- El **servicio**, con su texto exacto. Por ejemplo: "SERVICIO DE DISEÑO DE DRENAJE PLUVIAL PARA ELABORACIÓN DEL EXPEDIENTE TÉCNICO
  DE PI:" o "SERVICIO DE DISEÑO - DRENAJE PLUVIAL". No poner "EXPEDIENTE TÉCNICO" si el cliente no lo dice.
- **Foto del proyecto** del cliente (vista aérea, 3D o render) y **logo oficial** de la entidad.
- La lista de documentos en el orden de su carpeta de entrega, el Excel del índice o el PDF de láminas que imprime.
- El **color o modelo**, si lo tiene. Si no, proponer 3 a 6 opciones en PNG antes de producir todo.

## Paleta y tipografía
- **Guinda `6B1F2E` y dorado `C5A15A`**, crema `FBF6F2`, rosado claro `F6ECEE`, gris de texto `595959`. Granate de los
  Word `7B1E2B` (claro `F2E6E8` en filas de grupo, `F2D7DB` en subtítulos de franja). Si se pide otro color, se cambia solo en
  ese proyecto: el Refugio usó verde `1E5E3B` / `D6EEDD` en sus carátulas de drenaje.
- **Color con medida:** franjas, placas, sellos y filetes en guinda y dorado, con el cuerpo de la hoja en blanco. Ni la hoja llena
  de color ni todo blanco.
- PowerPoint: Cambria (serif) para títulos y Calibri para el texto. Word: Arial; la entidad va en 15 a 17 pt y el título de la franja
  en 20 a 26 pt.
- **Un diseño distinto por proyecto.** No se repite el modelo de un proyecto en otro.

## A. Carátulas en Word (una por página, todas en un solo Word)
Página A4, márgenes 2.0 cm laterales, 2.3 superior y 1.2 inferior (ancho útil 17 cm). De arriba hacia abajo:
1. Tabla sin bordes de 2 columnas (3.2 cm y el resto): escudo de 2.8 cm de alto. Al lado, la entidad en 17 pt negrita con espaciado,
   y la gerencia en 10.5 pt gris con línea inferior de color.
2. El servicio en 11 pt negrita de color; el proyecto entre comillas en 10 pt negrita; "CUI N° ..." en 11.5 pt.
3. La foto a 17 cm de ancho, en una tabla de 1 celda sin márgenes para que mida igual que la franja, y su leyenda en 8 pt cursiva
   gris ("Vista del Hogar de Refugio Temporal").
4. Franja de 1 celda de color con el título del documento (26 pt blanco) y el subtítulo partido por " - " en líneas de 11 pt.
5. Ubicación y fecha en 2 celdas con borde izquierdo grueso de color.
- Documentos típicos: ESPECIFICACIONES TÉCNICAS; MEMORIA DE CÁLCULO (por componente); MEMORIA DESCRIPTIVA; MEMORIA HIDROLÓGICA;
  METRADOS; PLANOS ("LÁMINAS DPL-01 A DPL-42"). El subtítulo termina en "ESPECIALIDAD DE ...".
- **Escudo:** recortar el escudo completo del logo oficial, buscando por filas hasta la primera franja en blanco bajo el dibujo,
  porque debajo está el texto que ya va al lado.
- La foto se reduce a 1 600 px como máximo (calidad 90) y el original no se toca.
- **Salto entre carátulas:** un párrafo de 1 pt con `page_break_before`; al final, otro de 1 pt sin salto para no dejar una hoja en blanco.
- **Carátulas del cliente:** si el cliente da su Word de carátulas armado para otro proyecto, se conserva todo el formato. Solo se
  cambian el nombre, el CUI, la leyenda y la foto, del mismo tamaño en píxeles para que no cambie el encuadre.

## B. Carátulas de tomos I a X y lomos (PowerPoint)
- Diapositiva A4 vertical de 21 × 29.7 cm, con el diseño en blanco (layout 6). **Carátulas: una por tomo, sin contenido.**
  Llevan el escudo, la entidad, el nombre completo con CUI, la foto, "TOMO n" una sola vez, la ubicación y la fecha.
- **Lomos de archivador de palanca oficio:** ancho de 6.3 × 27.6 cm y delgado de 4.0 × 27.6 cm, **3 por hoja A4**, separados 0.35 cm
  y centrados. Llevan un contorno discontinuo gris "Línea de corte", marcas de corte en los bordes de la hoja y la nota "recortar
  por la línea discontinua". Se arman 4 hojas por tipo; la última trae el Tomo X y 2 lomos de reserva con un renglón para el número.
- Cada lomo lleva: escudo, número de tomo, **tabla editable "CONTENIDO"** (filas de 0.68 cm, encabezado guinda) y el **nombre completo
  del proyecto con su CUI en vertical** (cuadro de texto rotado 270°, se lee de abajo arriba), con franjas guinda arriba y al pie.
  Sigue el estilo de la carátula de su proyecto.
- Contenido editable = **tabla real** (`add_table`), no un cuadro de texto. Cada celda vacía lleva `endParaRPr` con la fuente,
  el tamaño y el color, para que lo que se escriba salga con el formato.

### Trampas del esquema de PowerPoint (si se cometen, el archivo no abre)
- **Nunca dos rellenos en una forma** (`solidFill` y `noFill` juntos, o dos `solidFill`). Fijar el relleno una sola vez: `fill.solid()`
  o `fill.background()`, y lo mismo para la línea.
- **Quitar `p:style`** de cada autoforma, porque trae la sombra y el contorno del tema: `el.remove(el.find(qn('p:style')))`.
- En las tablas, vaciar `tblPr` (sin estilo del tema, `firstRow=0`, `bandRow=0`) y escribir `tcPr` en el orden del esquema:
  `lnL, lnR, lnT, lnB` (cada uno con `solidFill` y `prstDash`) y **después** el `solidFill` de la celda.
- La transparencia va como `a:alpha` dentro de `a:srgbClr`; el espaciado de letras, como `spc` en `rPr`.
- Fotos con recorte (`crop_left` y demás) para llenar el recuadro sin deformar.
- **Validar** el XML de cada diapositiva contra el esquema `pml.xsd` (ECMA-376) con lxml antes de entregar, abrirlo con LibreOffice
  y exportar PNG de control. Propiedades: autor vacío y título descriptivo.

## C. Separadores (PowerPoint, uno por ítem del índice del cliente)
- Leer el Excel del índice desde la fila de encabezado ("ÍTEM"). Se toman solo las filas con **código y título**; se descartan las
  columnas de estado ("OK", "DEBEN PASAR") y las filas de planos sin título.
- **Códigos que Excel convirtió:** si la celda es fecha, se rearma como texto según su formato (dd.mm → "06.06", "08.01"); si es
  número, con dos decimales ("10.04"). Nunca se escribe "2026-06-06" ni "10.4".
- Nivel = número de puntos del código. Arriba va el capítulo de procedencia; al centro, el código grande en dorado (54 pt en el
  capítulo y 44 pt en el ítem), con filetes, y el título en guinda (32, 26 o 22 pt según su largo). Al pie: "EXPEDIENTE TÉCNICO",
  nombre completo y CUI.
- **Marca de agua:** foto del cliente recortada a la proporción A4 y aclarada con un 85 % de blanco (mezcla con blanco, no
  transparencia), puesta a hoja completa al fondo.

## D. Índice de planos en Word
- **Fuente:** el Excel de láminas del cliente (versión vigente) o el PDF que imprime. En el PDF, leer por página el rótulo: el
  título entre la línea del CUI y la del coordinador, el código, la escala, el formato según el tamaño ISO de la página y las escalas
  de los dibujos.
- **Códigos y títulos tal cual el rótulo**, incluso con erratas (DPVL-09, DVPL-11, "CONTRUCTIVO"): el cliente lo decidió así.
- Solo se arregla la forma: espacios sueltos ("PT - 01" → "PT-01"), tildes, numeración correlativa (sin saltos), grupos en orden
  (I, II, III...) y **códigos repetidos por copia**, tomando la hoja que dice su descripción ("EDIFICACIÓN 06 / 03 - 04" → A-06/03-04).
  Si el Excel y el rótulo se contradicen (SE-E-01 evacuación frente a SE-S-01 señalización), manda el rótulo.
- **Orden:** el que pide el cliente, por número de la primera a la última lámina, o el del juego por formato (A0, A1, A2, A3).
- Formato: A4 vertical, Arial 9. Encabezado "<PROYECTO CORTO> | CUI N.° ... | <ESPECIALIDAD>" en 7.5 pt granate con borde inferior;
  pie "Página X de Y". Cabecera: entidad, proyecto con CUI, "ÍNDICE DE PLANOS" en 15 pt y especialidad. Tabla N.° | LÁMINA |
  DESCRIPCIÓN | FORMATO | ESCALA (0.8 / 1.6 / resto / 1.8 / 1.9 cm), con encabezado granate repetido (`tblHeader`), filas `cantSplit`
  y filas de grupo combinadas en `F2E6E8`. Sin formato en el Excel: "—". Al final: "Total: N láminas (n en A0, n en A1...)".
- **Índice general del expediente:** resumen por tomo y detalle (Tomo I documentos D-01 a D-09; tomos II y siguientes, láminas).
- El índice alimenta la memoria descriptiva (relación de planos), las especificaciones y las carátulas: si cambia, se actualizan.

## E. Encabezados y pies en Word
- Encabezado en una tabla sin bordes de 3 columnas: escudo (1.75 cm), entidad, gerencia y nombre corto, y un bloque guinda con el
  título del documento y el CUI en dorado. Debajo, un filete doble guinda (sz 18) y dorado (sz 6) con párrafos `pBdr`, y el
  nombre completo en 6 pt cursiva gris. Margen superior de unos 4.4 cm.
- Pie: filete dorado, texto corto con el CUI y un recuadro guinda con "Página X de Y", usando los campos `PAGE` y `NUMPAGES`
  (`fldChar begin/separate/end`).
- La carátula va en una sección propia sin encabezado. El cuerpo va en una sección nueva con `pgNumType start=1` y el
  encabezado desvinculado.
- **Índice (TOC):** campo `TOC \o "1-3" \h \z \u`, títulos con nivel de esquema y `w:updateFields` en settings. Para que salga ya
  lleno al imprimir, abrir el docx con LibreOffice (UNO), actualizar los índices y guardar; o paginar en dos pasadas (PDF y pdftotext).
- `w:shd` va **antes** de `w:vAlign` en `tcPr`; si el orden no respeta el esquema, Word dice que el archivo está dañado.

## Verificación final
- [ ] Nombre completo, CUI, fecha y servicio idénticos al rótulo y a los demás documentos del proyecto; ningún dato de otro proyecto.
- [ ] Cada carátula ocupa una sola página: convertir a PDF y contar páginas (n carátulas = n páginas).
- [ ] Los PPTX validan contra el esquema y abren en LibreOffice. Ninguna forma con dos rellenos y ningún `p:style`. La tabla de los
      lomos es editable.
- [ ] Medidas de los lomos: 6.3 y 4.0 × 27.6 cm, 3 por A4, con líneas de corte.
- [ ] Separadores: tantos como ítems con título; ningún código con forma de fecha o número mal formado.
- [ ] Índice: cuenta de láminas igual al Excel o al PDF; códigos tal cual; numeración correlativa; total por formato.
- [ ] Vista previa en PNG revisada (textos que no se salen, foto sin deformar, escudo completo).
- [ ] Autor vacío en las propiedades; sin nombre ni CIP; nada que revele uso de IA.

## Errores que el usuario ya corrigió (no repetirlos)
- **PowerPoint no abría** los archivos porque un cuadro de texto tenía dos rellenos. Validar siempre contra el esquema.
- **Contenido no editable:** debe ser una tabla donde se hace clic y se escribe.
- **Lomos sin el nombre completo:** llevan el nombre completo del proyecto con su CUI, en vertical.
- **Contenido en las carátulas de tomo:** la usuaria no lo quiso; la carátula va sin contenido y el contenido va solo en los lomos.
- **Color:** con "no tan lleno de color" se pasó a todo blanco, y luego "no menos color, no tan lleno pero sí usa color". Punto medio:
  franjas, placas y sellos en guinda y dorado, cuerpo blanco.
- **Tomo repetido o desproporcionado:** el tomo salió dos veces con mucho espacio libre, y luego la placa quedó muy grande. Va una
  sola vez, en un tamaño moderado.
- **Diseños parecidos:** "muy simple, mejóralo sin que se parezca a los otros". Para el CAR Mujeres pidió **opciones antes de
  procesar** (A a F en PNG) y eligió la E (foto panorámica entre filetes y bloque guinda del tomo). Después pidió **sin foto en los lomos**.
- **Carátulas separadas:** "todo en un solo Word, no separado", una carátula por página.
- **Escudo cortado:** "el logo sale corto". Recortar del logo oficial completo.
- **Carátula de índice de planos:** "no pongas el que dice índice de planos, solo planos".
- **"EXPEDIENTE TÉCNICO" en lugar del servicio del cliente:** debía decir "SERVICIO DE DISEÑO - DRENAJE PLUVIAL".
- **Índice renumerado y con observaciones:** se rechazó ("haces observaciones, pero no tienen sentido"). Va sin observaciones, con
  los códigos tal cual y solo las láminas del juego.
- **Orden del índice:** "ordénalo de la lámina uno a la última sucesivamente", cuando lo pide así.
- **Carátula para el proyecto equivocado:** las opciones eran para el Hogar de Refugio y se hicieron para Varones. Confirmar el
  proyecto antes de producir.
- **Fecha:** se escribe como la usa cada cliente (SETIEMBRE en Varones y en el Refugio, SEPTIEMBRE en el CAR Mujeres).
