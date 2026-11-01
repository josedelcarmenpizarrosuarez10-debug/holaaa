# Tesis de Lizeth Mori – revisión inicial de la información

Todo en español. Esta sesión corre en mi laptop. Lee completa la carpeta con la información de Lizeth (te la indico abajo o te la paso en el siguiente mensaje).

## Contexto
- **Quién pide:** Lizeth Mori, tesista. Yo soy ingeniero y conozco la hidráulica de drenaje (uso mi programa DRENIE). La voy a ayudar con tres objetivos de su tesis.
- **Título:** "Análisis geoespacial mediante sensores remotos y fotogrametría con drones del colapso en el sistema de drenaje pluvial en Morales-2026".
- **Objetivos a desarrollar:**
  - OE02: Determinar la capacidad hidráulica del sistema de drenaje pluvial mediante el análisis de sus características geométricas, parámetros hidráulicos y capacidad de conducción.
  - OE03: Caracterizar el estado estructural y funcional de los componentes del sistema de drenaje pluvial, identificando sus condiciones de conservación, deterioro y obstrucción.
  - OE04: Clasificar el nivel de vulnerabilidad hídrica mediante la integración de información geoespacial, hidráulica y estructural, identificando los sectores críticos del área de estudio.
  - El OE01 no se mencionó. Probablemente es el procesamiento fotogramétrico, que hace ella; confirmarlo.
- **Plazo:** Lizeth tiene 10 a 12 días desde el 01-11-2026, porque adelantaron la presentación de toda la tesis.
- **Mi situación:** estoy cerrando proyectos con el Gobierno Regional (transferencia). Solo puedo trabajar en las noches, una o dos horas: subo la información, reviso lo que prepares, leo la guía y se la envío. El trabajo pesado lo haces tú.
- **Lo acordado con Lizeth:** le pedí toda la información y hasta esta noche para revisarla. Esta noche le confirmo si asumo los tres objetivos completos o solo una parte, y qué datos faltan.

## Qué hacer ahora (revisión de factibilidad, sin calcular todavía)
1. **Inventario de lo recibido:** tipo, formato, tamaño y contenido de cada archivo. Se esperaba:
   - Del dron: ortomosaico, modelo de elevación y/o nube de puntos.
   - Área de estudio: .kmz o .shp.
   - Inventario de cunetas, canales, alcantarillas y buzones: medidas, material, pendiente o cotas de fondo.
   - Fotos de campo originales con GPS.
   - Fichas o anotaciones del estado de cada tramo: fisuras, colapsos, sedimentos, basura, % de obstrucción.
   - Esquema de tesis de la universidad.
   - Si hay borradores de la tesis, leer sus objetivos, metodología, variables, indicadores y matriz de consistencia: los resultados deben responder a eso.
2. **Por objetivo:** ¿alcanza la información? ¿Qué falta exactamente? ¿Qué puede completar ella rápido?
3. **Veredicto honesto:** ¿se hacen los tres en 10 días o conviene asumir solo una parte?
4. **Mensaje para Lizeth**, listo para WhatsApp, con el veredicto y lo que falta. Que suene natural: frases simples, sin paréntesis, sin listas largas y sin que parezca escrito por IA.

## Plan si se asume
Entregas por partes:

| Día | Entrega |
|---|---|
| 1 | Revisión y lista de lo que falta |
| 4 | OE02 |
| 7 | OE03 |
| 10 | OE04 con mapa |
| 11 y 12 | Correcciones |

- **OE02:**
  - Caudal de diseño con el método racional.
  - Lluvia de Morales: estación CO Tarapoto (SENAMHI), ya trabajada en mi repositorio holaaa para los CAR de Morales. Ver `conocimiento/02_hidrologia_e_hidraulica.md`, sección 2, y `SERIE_TARAPOTO` en `herramientas/barranquita/hidrologia_b.py`. Citar la fuente.
  - Capacidad de cada tramo con Manning y relación entre caudal de diseño y capacidad.
  - Excel con fórmulas.
- **OE03:** ficha por tramo, escala de condición (bueno, regular, malo, colapsado), % de obstrucción, cuadros y gráficos.
- **OE04:**
  - Del modelo de elevación: pendiente, depresiones y acumulación de flujo.
  - Matriz multicriterio en Excel con pesos y fórmulas, que integra el modelo de elevación, el OE02 y el OE03.
  - Mapa de vulnerabilidad (baja, media, alta, muy alta) en PNG, con los sectores críticos.
  - Usar Python (rasterio, geopandas, pysheds o whitebox) y, si está instalado, QGIS.
- **Redacción:** Word con la metodología y los resultados de cada objetivo.
- **Guía por entrega:** cada entrega lleva una guía paso a paso para Lizeth y para mí. Explica qué se hizo, por qué, de dónde sale cada número y cómo leer tablas y mapas, e incluye las preguntas típicas del jurado con su respuesta. No tengo tiempo de enseñarle, así que la guía tiene que bastar. Explicar con lenguaje de ingeniero de drenaje práctico, como el del DRENIE.
- **Lo que hace Lizeth:** vuelo, procesamiento fotogramétrico, trabajo de campo, marco teórico, discusión, conclusiones y sustentación.

## Reglas
- Trabajar en una carpeta propia, sin mezclar con los proyectos CAR ni la I.E. Barranquita.
- No versionar en git los archivos pesados del dron ni los datos de Lizeth sin preguntarme.
- No inventar datos. Si falta algo, decirlo.
- Recordarme que muchas universidades piden declarar el uso de IA en la tesis, y que Lizeth debe revisar lo que exige la suya.

## Carpeta con la información de Lizeth
RUTA: (pega aquí la ruta de tu laptop)
