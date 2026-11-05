---
name: tesis-academica
description: "Apoyar como asesor técnico la parte técnica de una tesis de pregrado de ingeniería en una universidad peruana (modelo: guía de productos de investigación UCV): resultados por objetivo específico, informes técnicos de sustento con Excel y planos o mapas, discusión, conclusiones y recomendaciones, anexo fotográfico, guía de estudio y preguntas del jurado para la sustentación. Redacción de tesis en tercera persona impersonal, parafraseada, sin rastro de IA, con tablas y figuras numeradas listas para pegar en el Word de las tesistas, cifras idénticas en todos los documentos y control de comprobaciones antes de entregar. Usar cuando pidan redactar o corregir resultados, OE, discusión, anexos o preparar la sustentación de una tesis."
---

# Tesis académica: parte técnica, resultados y sustentación

Caso de referencia: tesis de ingeniería civil (UCV, 2026) sobre el colapso de un sistema de drenaje pluvial urbano analizado
con sensores remotos y fotogrametría con dron. El usuario es el asesor técnico (no el asesor formal) y su encargo cubría
solo algunos objetivos específicos (OE2, OE3 y OE4): capacidad hidráulica, estado estructural y vulnerabilidad hídrica.
El método sirve para cualquier tesis técnica con trabajo de campo, cálculo y planos.

## Reglas del usuario que aplican
- **Todo en español.** Avisos cortos y en lenguaje sencillo: el usuario suele leer en el celular. Si pregunta SÍ o NO,
  responder primero eso y luego la razón.
- **Nada que revele el uso de IA** en lo que se entrega: sin frases típicas de IA, sin mencionar verificaciones internas,
  versiones ni correcciones. Lo que imprime y ve el jurado no habla de "versión", "corregido" ni de "similitud".
- **Formatos del usuario y de la universidad**: se respeta la guía vigente de la escuela y los Word de las tesistas.
- **No inventar datos.** Si falta algo, decirlo. Separar lo que se vio, lo que dijeron y lo que se deduce.
- **Decidir una sola vez**: evaluar bien antes de dar un veredicto y no cambiarlo sin un dato real nuevo ("después no me
  hagas cambiar de decisión"). Si se entrega un texto para reenviar, darlo completo y definitivo.
- No alarmar: no decir "otro problema" sin necesidad; explicar cualquier palabra que suene a problema (p. ej. "limitación").
- **Honestidad**: nunca prometer "100 % sin errores" ni decir que se hicieron revisiones que no se hicieron; decir qué se
  comprobó. Sobre detectores de IA: la guía UCV pide declarar las herramientas de IA usadas y las autoras deben conocer y
  poder defender todo el contenido; decírselo al usuario en privado, no en los entregables.
- **No modificar el Word original de las tesistas** ni los archivos originales del usuario: las versiones nuevas van
  aparte; antes de reemplazar una entrega, mover lo anterior a una subcarpeta `ANTERIORES`.
- Carpeta propia para la tesis, sin mezclar con otros proyectos. No subir a git archivos pesados del dron ni datos de
  las tesistas sin preguntar. No borrar datos de forma permanente; no cerrar programas del usuario.
- No retomar tareas que el usuario detuvo (p. ej. una simulación 3D pesada) salvo que la pida otra vez; avisar del costo
  de procesos largos.
- Mensajes para WhatsApp: un párrafo, tono amable, sin códigos internos, sin sonar a IA.

## 1. Datos que hay que pedir
1. Título, objetivo general y objetivos específicos **con sus verbos** (evaluar, determinar, caracterizar, clasificar…),
   hipótesis, variables y matriz de consistencia; qué objetivos tocan al usuario.
2. Word vigente de la tesis (solo lectura) y la guía de la universidad (versión, p. ej. UCV V07) o del programa.
3. Datos de campo: ficha de campo (Excel), fotos con su ubicación, levantamiento topográfico (RTK), ortofoto y modelo
   de elevación del dron, informes de terceros (topografía, hidrología), datos de lluvia (SENAMHI u otra fuente).
4. Numeración de tablas y figuras que ya usa la tesis antes de los resultados (para continuar desde ahí).
5. Fechas de entrega por objetivo y qué debe ir en cada entrega.

## 2. Formato (guía UCV de referencia; confirmar con la guía vigente de la escuela)
- A4, Arial 12, interlineado 1,5, justificado, márgenes 2,54 cm; anexos sin número de página.
- Referencias en el estilo que pida la guía de la escuela (en el caso de referencia, ISO 690); citas autor-año.
- Tablas: "**Tabla N**" en negrita y debajo el título en cursiva; nota que explica abreviaturas; "Fuente: Producción de
  los autores 2026" sin punto final (o la fuente real si es de otro autor). Figuras con el mismo patrón.
- Numeración continua entre los Word que se pegan (p. ej. OE2: tablas 7 a 24 y figuras 1 a 14; OE3 y OE4 siguen desde
  la tabla 25 y la figura 15). Si cambia una tabla, renumerar todo y las referencias del texto.
- Pies de foto sin códigos internos ni coordenadas; descripción clara del lugar y de lo que se ve.

## 3. Redacción
- **III. Resultados**: ordenados por objetivo específico; cada resultado en tabla o figura con su descripción narrativa
  después; prosa formal, sin subtítulos, viñetas, guiones ni negritas dentro del texto; pretérito del indicativo;
  tercera persona impersonal ("se determinó", "se registró").
- **Discusión**: en presente; contrasta cada resultado con antecedentes y teoría citados.
- **Conclusiones**: una por objetivo, con las cifras finales. **Recomendaciones**: accionables y ligadas a los hallazgos.
- **Informes técnicos de sustento**: en presente, con método, cálculos, tablas y planos.
- Parafrasear todo lo citado "como si ellas lo expresaran", con su cita, para que la similitud quede baja; comprobar la
  similitud contra las fuentes antes de entregar (dato interno, no va en los documentos).
- **Propuestas de solución**: solo si algún objetivo las pide (si los verbos son evaluar, determinar, caracterizar o
  clasificar, no se agregan). La recomendación puede remitir a un expediente de mejoramiento; si las tesistas quieren
  algo más, solo como anexo referencial y fuera del encargo.
- Términos fijos en todos los documentos (p. ej. "sección completa" = sin descontar sedimento, "sección libre" = sobre
  el sedimento; "Q/Qc"). Las limitaciones se declaran una vez, con su efecto (tabla de sensibilidad) y la
  recomendación que las cierra.

## 4. Entregables (uno por objetivo y los de apoyo)
1. **"OE_ PARA LA TESIS"** (Word): texto, tablas y figuras listos para pegar sin cambiar nada; sin la parte de anexos
   si así se decidió.
2. **Informe técnico por objetivo** (Word) con su **Excel** de cálculo (fórmulas vivas, 0 errores) y su **plano o mapa**
   (PDF o DXF ordenado si lo piden en AutoCAD).
3. Estudio de apoyo (p. ej. hidrológico) en Excel, coherente con los resultados.
4. **Discusión, conclusiones y recomendaciones** (Word) generadas desde las cifras vigentes.
5. **Anexo fotográfico**: un solo PDF, con fotos señaladas o con gráficos que muestren la evidencia.
6. **Guía de estudio** para las tesistas: cada dato, de dónde sale y en qué página del Word está.
7. **Preguntas del jurado**: preguntas probables (incluidas las incómodas) con respuesta corta y técnica.
8. **Observaciones a las referencias** (Word aparte para las tesistas, no para el jurado).
9. **Control de comprobaciones** (Excel interno): cada cifra clave, dónde aparece y si coincide.
Ordenar en carpetas por fecha de entrega (lo de hoy, lo del sábado, lo del domingo).

## 5. Método de trabajo y comprobación
1. Fijar las cifras clave (conteos, longitudes, porcentajes) en un solo origen (Excel o JSON) y generar todos los
   Word, figuras y mapas desde ahí; nunca copiar cifras de un archivo viejo.
2. Al cambiar un dato: rehacer toda la cadena (cálculo → Excel → figuras → mapas → Word de tesis → informes →
   discusión → guía → preguntas → control) y comparar versión anterior vs nueva palabra por palabra y celda por celda.
3. Comprobaciones automáticas con las cifras clave en todos los documentos (incluidas imágenes incrustadas, guía y
   discusión) y búsqueda de cifras antiguas.
4. **Mirar cada página** convertida a imagen: el control automático pasa aunque haya imágenes viejas o textos cortados.
5. Revisión independiente cuando el entregable es grande; corregir y volver a mirar.
6. Coherencia con el campo: lo dibujado debe coincidir con la ficha y las fotos (p. ej. secciones con el sedimento
   medido, cunetas en V asimétricas tal como son). Decir qué no puede ser exacto (promedios, tramos sin dato).
7. Cuando una duda depende de las tesistas, mandar una pregunta corta con una imagen de control y cerrar con su respuesta.
8. Avisar cuándo los Word están listos para pegar; hasta entonces, que no peguen nada.

## 6. Lista de control final
- [ ] Mismas cifras en tesis, informes, Excel, mapas, discusión, guía, preguntas y anexos.
- [ ] Numeración de tablas y figuras continua y referencias del texto correctas.
- [ ] Formato de la guía (letra, interlineado, márgenes, tablas, fuentes, estilo de referencias).
- [ ] Tiempos verbales: resultados en pasado, discusión e informes en presente; tercera persona impersonal.
- [ ] Nada sobre IA, similitud, versiones, correcciones ni comprobaciones internas en lo que ve el jurado.
- [ ] Ningún valor absurdo o contradictorio en rótulos (p. ej. "libre 245,71" → "más de 20"; "0,00 m (0 %)" → "Sin
      sedimento"); ningún rótulo que parezca un pendiente.
- [ ] Cada página vista; archivos anteriores movidos a `ANTERIORES`; huellas de los copiados comprobadas.
- [ ] Mensaje al usuario: qué se entrega, qué se comprobó y qué no, y el texto para las tesistas si hace falta.

## 7. Errores que el usuario ya corrigió (no repetirlos)
- Enviar un Word "sin errores" que luego difería de la tesis ("me hiciste meter la pata"): no entregar hasta que todo
  esté cerrado y comparado.
- Contradecirse en una decisión (medir o no las alcantarillas): una sola respuesta, evaluada antes, y no reabrirla.
- Conclusiones de la discusión copiadas de un archivo viejo con cifras antiguas; imágenes viejas incrustadas en la guía y
  en un mapa: generar desde el origen vigente y buscar cifras antiguas en todo.
- Dibujar secciones "limpias" que contradecían las fotos: dibujarlas reales con el sedimento medido, o no presentarlas.
- Un rótulo que parecía contradictorio ("completa 0,13 · libre tapada"): explicarlo en el propio gráfico o rehacerlo;
  "no debe haber nada al pendiente".
- Poner en los entregables avisos sobre IA o similitud que podían desanimar a las tesistas: borrarlos.
- Usar "limitación" o "problema" sin explicar, alarmando al usuario.
- Contar por coincidencia de texto (una palabra dentro de otra fuente): usar criterios exactos y comprobar el conteo.
- Seguir con un proceso pesado que el usuario ya detuvo, o proponer agregar propuestas que ningún objetivo pide.
