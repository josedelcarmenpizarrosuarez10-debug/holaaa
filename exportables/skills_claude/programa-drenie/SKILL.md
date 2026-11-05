---
name: programa-drenie
description: Usar, mantener y ampliar DrenIE, el programa de escritorio de drenaje pluvial que el usuario vende con licencia (Windows, interfaz Tauri y motor de cálculo en Python), en especial la pestaña RED DE CUNETAS que lee el plano DXF del local, plantea la red con descargas por gravedad, calcula lluvia, caudales y secciones y entrega planos DXF y PNG, metrado, memorias, memoria de cálculo y especificaciones. Incluye las reglas del usuario para el programa (solo hasta metrados, todo en español, el programa propone y el proyectista elige), el flujo de pestañas, órdenes del motor, visor tipo CAD, lluvia PISCO-SENAMHI, mapas de ubicación, licencias, actualizaciones firmadas, reglas de seguridad de las claves y pendientes. Usar cuando el usuario hable de DrenIE, de su programa de drenaje, de licencias o versiones, o pida una mejora del programa.
---

# Programa DrenIE: red de cunetas desde el plano

DrenIE es el programa de escritorio de drenaje pluvial del usuario (Windows, instalador propio, vendido con licencia).
La versión 3.0.2 trae las pestañas de siempre; la 3.1.0 agrega la **RED DE CUNETAS**: lee el plano general en DXF, propone la
red y entrega el expediente de drenaje. Los criterios técnicos completos están en los skills `planteamiento-drenaje-pluvial`,
`hidrologia-drenaje-pluvial`, `metrado-drenaje-delphin` y `planos-dxf-escala-real`; aquí va cómo es y cómo se trabaja el programa.
El código del programa no está en este chat: pedirlo al usuario (zip de fuentes) si hay que cambiar algo.

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

## 1. Reglas del usuario para el programa
- **Solo hasta metrados**: "olvídate de costos de precios, en ningún momento estamos viendo eso, solo llegamos hasta metrados".
  DrenIE no hace ACU, precios ni presupuesto (eso lo hace el ingeniero en Delphin). No volver a proponerlo.
- **Todo en español**: interfaz, mensajes de error del motor (con tildes), documentos, commits y cada mensaje al usuario ("aquí veo
  inglés, ¿acaso yo hablo inglés?"). Explicar sencillo y paso a paso, diciendo dónde hacer clic ("no entiendo, explícame más
  sencillo"); el usuario no programa: darle comandos listos para copiar en PowerShell.
- **El programa propone y el proyectista elige**: lo que no se resuelve solo no se esconde; sale en la ventana de soluciones (§5).
- **El programa no se cae**: un error interno sale como mensaje en español y su detalle técnico queda en un registro de error.
- **Toda cuneta enterrada está prohibida**; secciones constructivas (máximo 0.40 libre, 0.60 total); sin drenes franceses.
- El dibujo a mano (áreas, flechas de caída, cunetas, descargas) se hace en la computadora; en el celular solo se revisa.
- La batería de pruebas corre antes de entregar cualquier versión: ninguna caída ni falla sin explicar.
- **Drenaje vial (MTC)**: está programado y probado, pero **oculto** a pedido del usuario ("aún no veo yo el tema de drenaje vial");
  se habilita cambiando `DV_ACTIVO = false` a `true` en su módulo y recompilando. No activarlo ni proponerlo sin pedido.

## 2. Seguridad y lo que no se toca (instrucciones del usuario, vigentes)
- No abrir, leer, copiar ni mostrar la carpeta de claves del propietario (`DrenIE_Propietario_PRIVADO`), ningún `clave-privada.xml`,
  la carpeta `DrenIE_Actualizaciones_PRIVADO` ni archivos `*.key`. No pegar la clave de desbloqueo en ningún archivo ni mensaje.
- No ejecutar `ROTAR_CLAVE_LICENCIAS.ps1` ni `GENERAR_CLAVE_ACTUALIZACIONES.ps1`: los corre el usuario en su PC.
- No modificar el código fuente del cliente (interfaz, núcleo Tauri, administrador de licencias, pruebas) salvo que un paso falle y
  el usuario lo apruebe. No tocar las bibliotecas (React, SheetJS, docx) ni la lógica de cálculo original de DrenIE (sus 26 pruebas
  de regresión deben dar igual). No debilitar el bloqueo de licencia ni desactivar pruebas.
- El armado de la interfaz debe terminar con "OK · … parches". Las integraciones nuevas van como archivos nuevos y parches.
- Si el repositorio de trabajo es público: no subir las fuentes del cliente (solo los archivos de integración) ni la base de lluvia.
- Datos de terceros: las series certificadas del SENAMHI nunca van dentro del programa (prohíben su reproducción; solo se guardan
  factores derivados); confirmar la licencia de PISCOp antes de vender el programa con esa base incluida.
- Entregar el programa como zip con la lista SHA256 de sus archivos; el usuario compila en Windows y prueba.

## 3. Pestañas y flujo de trabajo
ARCHIVO · PROYECTO · LLUVIA · **RED DE CUNETAS** · TECHOS Y ÁREAS · CUNETAS · MONTANTES · METRADO · RESULTADOS · CONFIGURACIÓN
(DRENAJE VIAL oculta). Tema claro: Poppins, azul marino #0B2545 y celeste #1EA7F2.
0. **LLUVIA**: curva IDF por análisis estadístico de la estación (o curva ingresada); botón «Lluvia PISCO-SENAMHI» en Análisis
   estadístico (§6). La red usa esa misma lluvia (intensidad para el tc de diseño, con su fuente; avisa si es la curva de ejemplo).
1. RED DE CUNETAS → «Nuevo desde plano DXF» → «Elegir plano DXF»: el programa propone las capas de cerco, techos, curvas de nivel,
   veredas, muros y líneas de cuneta del proyectista; se revisan. Sin curvas: terreno en LandXML.
2. Datos: nombre, CUI, entidad, ubicación, NPT (borde de cuneta), nivel del área verde.
3. Planteamiento: «Completar mis líneas de cuneta» (recomendado: solo agrega cuneta donde un montante no llega), «Proponer toda la
   red» o «Solo mis líneas de cuneta».
4. «Crear y abrir el proyecto» → visor (§4). Lo dibujado se guarda solo en la carpeta del proyecto.
5. «Calcular todo»: diseña y genera los entregables en la carpeta «salida». 6. «Soluciones». 7. «Entregables» (cada archivo se abre
   con su programa). 8. «Ubicación (mapas)» (§7). 9. **«Pasar a CUNETAS»**: cada eje queda como perfil de cuneta (misma cota de fondo,
   tramos tapados y vehiculares, caídas como escalón y conexión a la cuneta receptora; caudal propio como aportes por progresiva), cada
   techo como módulo en MONTANTES y las estructuras y montantes de la red como partidas adicionales en METRADO. Al volver a pasar solo
   se reemplaza lo que vino de la red; lo hecho a mano no se toca.

## 4. Visor tipo AutoCAD
Línea de comando abajo, OSNAP, ORTO, POLAR (45°), zoom ventana/previo, ayuda F1, sugerencias de comandos. Dibujo y edición: L, PL,
círculo, texto, M, CO, RO, escala, simetría, desfase, descomponer, estirar con pinzamientos, TR recortar, EX alargar, F empalme, CHA
chaflán (0.60 m por defecto), cotas alineada y lineal, DI distancia y área, propiedades, selección por clic y ventana. Drenaje: eje de
cuneta (al terminar pregunta el borde: al ras o rebajado 5 o 10 cm, y su NPT), MT montante, SU sumidero, descarga, caída de techo
(dos aguas con cumbrera o una agua con lado bajo), asignar superficie (varias a la vez; el tipo se ve al pasar el mouse). Niveles:
PLATAFORMA (NPT y rebaje), RAMPA (inicio y fin), ESCALERA (ninguna cuneta pasa). En el celular: cinta deslizable, Enter/Esc/Deshacer.

## 5. Ventana de soluciones
Cada observación dice qué pasó, dónde (E, N; «Ver en el plano» hace zoom y marca el punto), por qué y sus soluciones: **automática**
(p. ej. subir el NPT ya verificado, dejar que el programa elija las descargas), **manual** («lo resuelvo a mano»), **confirmar** (lo
que supuso el programa: caída de techos, tipo de superficie por defecto) o «Lo analizo después». La recomendada va marcada; lo
elegido se aplica con «Calcular con lo elegido». Si el NPT tendría que subir más de 3 m para salir por gravedad, se pide revisar el
dato (suele ser de otro plano o una cota relativa). La misma lista va en la hoja SOLUCIONES de la revisión general.

## 6. Lluvia PISCO-SENAMHI (serie referencial)
Máxima en 24 h de cada mes (1981-2025) de cualquier distrito o coordenada del Perú desde PISCOp v3.0 (va dentro del programa, sin
internet), corregida por el factor estación / PISCO interpolado entre 8 estaciones de San Martín (1.04 a 1.57; a más de 80 km, 1.00
con aviso). «Traer serie» y «Cargar en la tabla de lluvias» (misma tabla que «Importar Excel»); en la demo, los últimos 30 años.
Es **referencial**: para el expediente se usa la serie certificada de la estación más cercana. Factores y método: skill de hidrología.
La base se arma en la PC del usuario reduciendo el NetCDF diario de PISCOp a máximas mensuales por celda (el eje de tiempo puede
llamarse «Z1»).

## 7. Mapas de ubicación (lámina U-01 y memoria descriptiva)
Con el cerco del plano el programa ubica solo el proyecto (UTM WGS 84; prueba zonas 17S, 18S y 19S; si caben varias, decide por el
distrito escrito y pide confirmar la zona) en los límites del INEI (Censo 2025: 1 892 distritos con su forma real; provincias y
departamentos unidos desde sus distritos). Cuatro mapas: Perú, departamento, provincia y local (foto aérea del usuario con sus esquinas
en UTM, si no calles de OpenStreetMap con internet, si no el plano). En «Datos del proyecto» cada mapa tiene su lista (País = Perú por
defecto, Departamento, Provincia, Distrito); una imagen cargada por el usuario no se reemplaza sola y se ajusta a 960 × 1040 sin
deformarse. El distrito elegido en el editor manda sobre las coordenadas (con aviso si no coinciden).

## 8. Motor de cálculo (Python) y archivo de proyecto
- Órdenes: `lluvia`, `leer` (lectura, mapa de superficies e imagen de control), `disenar` (red, cotas, caudales, comprobaciones,
  entregables), `aplicar` (una solución sin visor); de escritorio, que responden un JSON en UTF-8 por la salida estándar (con `error`
  en español): `capas`, `crear`, `vista`, `ediciones`, `entregables`, `abrir`, `ubicacion`, `pisco`, `vial`, `normas`. Código de
  salida 0 bien, 2 error de datos, 3 error interno explicado. Lo que imprimen las bibliotecas va a la salida de errores.
- El motor compilado solo trabaja con la ficha de sesión firmada que le pasa DrenIE (HMAC-SHA256, 5 minutos); va protegido (Nuitka a
  módulo binario + PyInstaller, sin bytecode legible) e incluye EPA SWMM. Bibliotecas: ezdxf, shapely 2, numpy, scipy, matplotlib,
  openpyxl; LibreOffice opcional para recalcular el metrado (si no, calculador interno con los mismos totales).
- Proyecto (JSON): `proyecto` (nombre, código, entidad, ubicación, fecha, foto, datos de memoria: lo que no se da no se escribe), `dxf`,
  `capas` (curvas, cerco, ejes del usuario por capa y color, techos con contornos cerrados, área mínima y «separados»), `niveles`
  (NPT, borde, área verde, plataformas, rampas, escaleras, bordes por eje), `superficies` y `superficies_cfg` (leyenda, rótulos,
  asignaciones, por defecto), `techos_caida`, `secciones` o `dimensionamiento_adoptado`, `lluvia`, `descargas`, `planteamiento`
  («completar», «automatico», «no»), `descarga_alternativa`, `ubicacion`, `planos` (prefijo y número inicial) y `parametros` (b mínimo
  0.30, b máximo 0.40, paso 0.05, h inicial 0.30, S 0.5 %, espesores 0.10, una medida por sector, lloraderos @1.50, todo cambiable).
- Visor y motor se comunican por archivos JSON: escena y observaciones hacia el visor; ediciones y soluciones elegidas hacia el motor.

## 9. Entregables de «Calcular todo»
Planos en un solo DXF con una presentación por lámina (U-01, DC-01 planta, DC-02 cuadros, perfiles, secciones, una lámina 1/25 por
descarga, detalles, estructuras) y un PNG por lámina; METRADO_DRENAJE_PLUVIAL.xlsx (formato del CAR Mujeres, partidas Delphin, con
fórmulas); MEMORIA_CALCULO (Excel con fórmulas: datos, serie, frecuencias, K-S, IDF, superficies, Manning por tramo, canaletas y
montantes, sumideros, descargas, perfil de flujo, estructuras, tapa vehicular, normas y fuentes); memorias hidrológica y descriptiva,
especificaciones técnicas (una ficha por partida), carátulas e índice de planos (Word); DIMENSIONAMIENTO.xlsx (columna ADOPTADO para
el proyectista); REVISION_GENERAL.xlsx (CUMPLE / NO CUMPLE / AVISO de diseño, componentes, metrado, documentos, planos y entregables);
red en EPA SWMM 5 (.inp y su reporte). Documentos sin nombre ni CIP del proyectista y con metadatos vacíos.

## 10. Licencia, ventas y actualizaciones (como se le explicó al usuario)
- Licencia sin internet: código firmado ligado al identificador de la máquina; protección contra retroceso del reloj (24 h de
  tolerancia). Demo: leer el plano, crear el proyecto y dibujar; calcular la red, generar entregables y pasar a CUNETAS piden la
  licencia completa con el módulo de exportación. Renovar: en el administrador, «Renovar seleccionada» emite un código nuevo; el
  plazo corre desde el vencimiento anterior o desde hoy, lo que sea mayor. Diferidos por el usuario: aviso antes del vencimiento y
  licencia en línea.
- Actualizaciones firmadas: al abrir (una vez al día) y con «Buscar actualización»; solo se instala un instalador firmado con la clave
  del propietario; se publican en un repositorio público solo de instaladores. Sin certificado de firma de código, Windows SmartScreen
  puede advertir la primera vez.
- Claves privadas en el disco D: con `MOVER_CLAVES_A_D.ps1` (copia verificada por SHA256, permisos solo del usuario, enlace en C:);
  tras formatear, `-Restaurar` y «Restaurar respaldo…» en el administrador; copia extra en USB (D: está en el mismo disco físico).
- Scripts de PowerShell: correrlos desde una ventana de PowerShell abierta (con doble clic la ventana se cerraba al instante).
- Después de rotar claves, los zips nuevos deben llevar las claves públicas actuales (pedirle al usuario sus dos archivos públicos).

## 11. Pendientes propuestos (hacer solo si el usuario lo aprueba)
Capacidad de rejillas y sumideros (HEC-22), zanjas de infiltración, manual de usuario en Word y video largo, aviso de vencimiento de
licencia, exportar la red a Google Earth (KMZ), simulación de lluvia en 3D, más estaciones para el factor PISCO (serie diaria completa
de Picota, coordenadas exactas de Jepelacio, Sauce y San Antonio; Rioja, Moyobamba, Juanjuí, Tocache, Bellavista, Yurimaguas).

## 12. Antes de entregar una versión
- [ ] Batería de pruebas (ejemplos reales y terrenos inventados) sin caídas ni fallas sin explicar; regresiones de DrenIE iguales.
- [ ] Prueba de la interfaz en el navegador (pantallas de siempre y RED DE CUNETAS) y compilación de la parte nativa comprobada.
- [ ] Mensajes, rótulos y documentos en español; nada de costos; nada que revele herramientas en los archivos.
- [ ] Instructivo (LEEME) actualizado con lo nuevo; zip con lista SHA256; avisar qué debe hacer el usuario en su PC.

## 13. Errores que el usuario ya corrigió (no repetirlos)
- Responder o rotular en inglés.
- Proponer presupuesto con ACU como mejora del programa: "solo llegamos hasta metrados".
- Mapas de ubicación "muy rectos": límites con su forma real; y sin listas para elegir cada mapa.
- Mostrar la pestaña de drenaje vial que el usuario no pidió: quedó oculta, sin borrar el código.
- Cunetas de 0.50 libre y 0.70 total ("exagerado"), cunetas enterradas, tubos que llegan a la cota de fondo (quedan ahogados),
  montantes de 6", sumideros en áreas verdes, drenes franceses: ver los skills de planteamiento y metrado.
- "1616 soportes es demasiado": mostrar los conteos grandes por edificación para que el usuario los revise.
- Explicaciones técnicas largas: el usuario pide lo esencial y en simple.
