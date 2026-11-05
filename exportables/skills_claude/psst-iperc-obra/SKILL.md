---
name: psst-iperc-obra
description: Elaborar el Plan de Seguridad y Salud en el Trabajo (PSST) de cualquier tipo de obra en el Perú (edificación, vías, saneamiento, drenaje, puentes, electrificación) con su matriz IPERC según la R.M. N.° 050-2013-TR, la Norma G.050, la Ley N.° 29783 y su reglamento: reconocimiento de actividades desde el presupuesto, peligros y riesgos, probabilidad x severidad, nivel de riesgo, jerarquía de controles y riesgo residual, programas (EPP, PETS, PETAR, capacitación, inspecciones, monitoreo, emergencias, indicadores). Entrega un Word ordenado con tablas y gráficos y un Excel con fórmulas. Usar cuando el usuario pida un PSST, IPERC, matriz IPER, plan de seguridad de obra, actualizar uno existente o retirar o ajustar partes de un PSST suyo.
---

# PSST con matriz IPERC para cualquier obra en el Perú

Método estándar, no atado a un proyecto: con el presupuesto de la obra y unos datos generales se reconocen las actividades,
se arma la matriz IPERC (línea base, inicial y residual) y se derivan todos los programas del plan. El PSST va siempre
separado del estudio de gestión de riesgos de obra y de los expedientes de drenaje u otras especialidades.

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

## 1. Datos que hay que pedir
1. **Presupuesto**: PDF exportado de S10 o lista de partidas (ítem, descripción, unidad, metrado; los títulos sin unidad).
   Del S10 solo se usan ítem, descripción, unidad y metrado; los precios no intervienen y **los metrados no se tocan**.
2. **Proyecto**: código corto, nombre completo, CUI, entidad, unidad ejecutora, ubicación (distrito, provincia, departamento),
   modalidad, plazo en días, altitud (msnm), clima y condiciones del lugar: `selva`, `altura`, `cauces`, `zona_poblada`, `transito`.
3. **Personal**: histograma de trabajadores por mes (del cronograma o del calendario de adquisición de mano de obra).
4. **Emergencia**: teléfonos locales (centro de salud más cercano, hospital de referencia, bomberos, PNP, defensa civil, SCTR).
5. Si existe, el PSST anterior del usuario (se respeta su formato y solo se cambia lo que pida).
Si falta el histograma, suponer una cuadrilla razonable por mes y decirlo; si falta un teléfono, dejar la celda amarilla.

## 2. Marco normativo que se cita
Ley N.° 29783 y su reglamento D.S. N.° 005-2012-TR (art. 21: jerarquía de controles); D.S. N.° 011-2019-TR (Reglamento de SST
para el Sector Construcción); Norma G.050 Seguridad durante la construcción (contenido mínimo del plan); R.M. N.° 050-2013-TR
(formatos de registros e IPERC); R.M. N.° 375-2008-TR (ergonomía); R.M. N.° 312-2011-MINSA (vigilancia médica ocupacional);
SCTR (Ley N.° 26790 y D.S. N.° 003-98-SA); NTP 399.010-1 (señales de seguridad) y NTP de extintores; y las que correspondan a la
obra: Manual de Dispositivos de Control del Tránsito del MTC, Código Nacional de Electricidad, normas de explosivos (SUCAMEC).

## 3. Reconocimiento de actividades (desde las partidas)
- Cada actividad estándar se reconoce por palabras clave en la descripción de las partidas (y, si hace falta, por el título padre).
  Biblioteca base (36 actividades): generales a campo abierto; selva (fauna y vectores); altura > 2,500 msnm; traslado de personal;
  campamento y almacenes; movilización; topografía; mantenimiento de tránsito y desvíos; desbroce y tala; demoliciones; movimiento
  de tierras con maquinaria; corte en roca; excavación de zanjas; trabajos en cauces; rellenos y compactación; geosintéticos y
  subdrenaje; transporte con volquetes; acero; encofrado; concreto; gaviones y mampostería; tuberías y alcantarillas; pavimento
  asfáltico; estructuras metálicas; puentes; señalización vial; reubicación de postes; mantenimiento y combustible; gestión
  ambiental; albañilería y acabados; coberturas y techos; instalaciones eléctricas; sanitarias; espacios confinados; pintura; carpintería.
- **No generan peligros** (partidas no físicas): EPP, capacitación, señalización temporal de seguridad, planes, ensayos, control de
  calidad, estudios, expediente, supervisión, difusión, charlas, monitoreo, simulacros, adquisiciones, mobiliario.
- Las partidas de SST del presupuesto (protección personal y colectiva, capacitación, respuesta ante emergencias, señalización
  temporal, mantenimiento de tránsito) se listan aparte en el capítulo de partidas de SST.
- Siempre activas: actividades generales; selva si la condición lo indica; altura si altitud > 2,500 msnm; maquinaria si hay
  movimiento de tierras, asfalto, transporte o roca.
- Partidas que no encajan en ninguna actividad: **avisar la lista** y agregar la palabra clave o una actividad nueva con sus
  peligros; nunca dejar partidas físicas sin evaluar ni corregir a mano el resultado final.

## 4. Evaluación IPERC (R.M. N.° 050-2013-TR)
Por cada peligro: proceso, actividad, puestos, rutinaria (R) o no rutinaria (NR), peligro, riesgo, consecuencia, tipo
(S seguridad / SO salud ocupacional).

| Índice | 1 | 2 | 3 |
|---|---|---|---|
| A personas expuestas | 1 a 3 | 4 a 12 | más de 12 |
| B procedimientos | existen y son satisfactorios | parciales | no existen |
| C capacitación | entrenado, conoce el peligro | parcialmente | no entrenado |
| D exposición | esporádica (anual) | eventual (mensual) | permanente (diaria) |
| S severidad | lesión sin incapacidad / disconfort | incapacidad temporal / daño reversible | incapacidad permanente, muerte / irreversible |

- A = índice de min(cuadrilla de la actividad, pico de personal). **Inicial: B = 2 y C = 2**; **residual: B = 1 y C = 1**
  (PETS, ATS, capacitación y supervisión implementados) y D, S reducidos solo si un control de ingeniería lo justifica.
- Probabilidad = A + B + C + D (4 a 12). Nivel de riesgo = probabilidad x severidad (4 a 36):
  **4 Trivial; 5 a 8 Tolerable; 9 a 16 Moderado; 17 a 24 Importante; 25 a 36 Intolerable**.
- Significativo = Importante o Intolerable. Interpretación: Importante = no comenzar hasta reducirlo; Intolerable = no comenzar
  ni continuar; si no se puede reducir, prohibir el trabajo.
- **Todo peligro debe quedar en Moderado o menos en el residual**; si no, reforzar controles (no bajar índices sin control).
- Controles en el orden de la jerarquía (art. 21): eliminación, sustitución, ingeniería, administrativos, EPP. Escribir "No aplica"
  cuando no corresponda, nunca dejar vacío.
- Peligros comunes que casi toda obra tiene: radiación solar y calor (D3 S2), lluvia y tormenta eléctrica (regla 30-30, SENAMHI),
  sismo, ofidios y vectores (selva), altitud, manipulación de cargas (> 25 kg con ayuda mecánica), herramientas manuales (cinta de
  color del mes), superficies irregulares, polvo, ruido > 85 dB(A), maquinaria en movimiento (vigía, alarma de retroceso, D3 S3),
  tránsito de terceros (D3 S3), equipos eléctricos portátiles (diferencial y tierra), vibración, cemento, caída de altura > 1.80 m
  (barandas de 1.00 m con rodapié, línea de vida, arnés), caída de objetos, izaje, soldadura, combustibles, carga psicosocial.

## 5. Programas que salen del IPERC
- **EPP por puesto**: básico (casco con barbiquejo, lentes, calzado con puntera, chaleco reflectivo, guantes de cuero) más el
  específico de cada actividad (respirador P100 o para vapores, protector auditivo, arnés, careta de soldar, botas de jebe,
  guantes de nitrilo o dieléctricos, polainas, salvavidas, bloqueador, repelente, ropa impermeable), con su norma (ANSI, NIOSH, ASTM).
- **PETS**: uno por actividad. **PETAR** solo los que apliquen: altura (≥ 1.80 m), excavaciones (> 1.50 m), caliente, espacios
  confinados, izaje, eléctrico, explosivos (**solo si hay voladura explícita en el presupuesto**), cauces. ATS y charla de 5 minutos diarios.
- **Capacitación** (horas y frecuencia): inducción 4 h al ingreso; IPERC y ATS 2 h trimestral; EPP 1 h trimestral; orden y limpieza;
  primeros auxilios 4 h; extintores 2 h; emergencias y simulacros 2 h; manejo defensivo 4 h; ergonomía; psicosociales y hostigamiento;
  investigación de incidentes; más una por cada PETAR y las de selva, maquinaria y tránsito si aplican. Cronograma por mes con X.
- **Inspecciones**: pre-uso de maquinaria (diaria), frentes y ATS (diaria), herramientas, EPP, extintores y botiquines, campamento,
  instalaciones eléctricas (mensual), almacén de combustibles (semanal); andamios, excavaciones (diaria y después de lluvias),
  izaje y cauces según los PETAR.
- **Monitoreo de agentes** solo de los que aparecen en el IPERC: ruido (dosimetría, 85 dB(A) 8 h), polvo y sílice, vibración
  (ISO 5349 / 2631), estrés térmico (WBGT), vapores y humos, monóxido de carbono, radiación UV, ergonomía.
- **Organización**: comité paritario de SST si el mes de mayor personal tiene **20 o más trabajadores**; supervisor de SST si menos.
- **Indicadores**: HHT = trabajadores x 8 h x 26 días; IF = accidentes x 1,000,000 / HHT; IG = días perdidos x 1,000,000 / HHT;
  IA = IF x IG / 1,000. Metas: cero accidentes mortales, 100 % de inducción, cumplimiento de programas ≥ 90 %.
- **Emergencias**: escenarios (accidente grave, incendio, sismo, lluvias e inundación, mordedura de ofidio, electrocución,
  derrame), brigadas (primeros auxilios, contra incendio, evacuación), flujograma de comunicación y directorio.

## 6. Word del PSST (Norma G.050 y D.S. N.° 011-2019-TR)
Carátula (nombre completo y CUI, entidad, fecha; sin nombres ni CIP), índice actualizable y capítulos:
1 Generalidades (objetivo, alcance, datos de la obra, componentes del presupuesto, histograma de personal); 2 Marco normativo;
3 Política, objetivos, metas e indicadores; 4 Organización (organigrama, funciones, comité o supervisor); 5 IPERC (metodología,
actividades evaluadas, resultados inicial y residual, mapa de calor, intolerables, jerarquía de controles); 6 Mapa de riesgos y
señalización; 7 Procedimientos (PETS, PETAR, ATS, charla diaria); 8 EPP y protección colectiva; 9 Capacitación con cronograma;
10 Inspecciones y auditorías; 11 Salud ocupacional (exámenes, SCTR, monitoreo, bienestar, primeros auxilios); 12 Subcontratistas
y proveedores; 13 Respuesta ante emergencias; 14 Notificación e investigación de accidentes; 15 Registros obligatorios,
indicadores y mejora continua; 16 Partidas de SST del presupuesto; 17 Anexos (IPERC completo, EPP por puesto, formato de ATS,
lista de verificación del PETAR).
- Tablas de ancho fijo con encabezado repetido; IPERC en sección horizontal A3 o A4 apaisada; títulos numerados; pie con el nombre
  corto del plan y página.
- Gráficos (PNG 200 ppp): histograma de personal; mapa de calor probabilidad x severidad inicial y residual; barras de niveles
  inicial vs residual; peligros por proceso; organigrama; pirámide de jerarquía de controles; flujograma de emergencias;
  cronograma de capacitación. Cada figura con número, título y fuente ("matriz IPERC del plan").

## 7. Excel con fórmulas
Celda amarilla = dato editable; celda verde = fórmula. Hojas: INDICE, DATOS, CRITERIOS, IPERC, RESUMEN, MAPA DE CALOR, EPP,
PETS-PETAR, CAPACITACION, INSPECCIONES, MONITOREO, INDICADORES, PARTIDAS (trazabilidad partida-actividad), EMERGENCIA.
- IPERC (34 columnas): identificación (N.°, proceso, actividad, puestos, R/NR, peligro, riesgo, consecuencia, S/SO); inicial
  A, B, C, D (amarillo), `=SUM(A..D)`, S, `=P*S`, nivel `=IF(x<=4,"Trivial",IF(x<=8,"Tolerable",IF(x<=16,"Moderado",IF(x<=24,"Importante","Intolerable"))))`,
  significativo `=IF(OR(nivel="Importante",nivel="Intolerable"),"Sí","No")`; controles en 5 columnas de la jerarquía; residual con
  las mismas fórmulas; PETS y PETAR. Formato condicional de colores por nivel (Trivial verde oscuro, Tolerable verde claro,
  Moderado amarillo, Importante naranja, Intolerable rojo), filtros, paneles inmovilizados, impresión A3 apaisada con títulos.
- RESUMEN y MAPA DE CALOR con `COUNTIF`/`COUNTIFS` sobre la hoja IPERC (se actualizan si se cambia un índice).
- CAPACITACION: veces `=COUNTIF(meses,"X")` y horas totales `=horas*veces`. INDICADORES: HHT, IF, IG, IA mensuales y acumulados
  con `IF(HHT=0,0,...)` para no dividir entre cero.
- Recalcular con LibreOffice y comprobar que ninguna celda dé error (#VALUE!, #REF!, #NAME?).

## 8. Verificación antes de entregar
- [ ] Todas las partidas físicas tienen actividad; lista de no reconocidas vacía o explicada al usuario.
- [ ] Ningún peligro residual en Importante o Intolerable; los significativos iniciales tienen controles de ingeniería o administrativos concretos.
- [ ] Conteos del Word = conteos del Excel (peligros, niveles inicial y residual, significativos, actividades, PETAR).
- [ ] PETAR solo los que aplican; explosivos solo con voladura en el presupuesto; selva y altura según el lugar.
- [ ] Comité o supervisor según el pico de personal; histograma igual al dato del usuario.
- [ ] Nombre completo y CUI en carátula y pies; sin nombres ni CIP; sin texto que revele IA; nada de otro proyecto.
- [ ] Excel recalculado sin errores; Word revisado en vista previa (índice actualizado, tablas que no se cortan mal, figuras legibles).

## 9. Errores que el usuario ya corrigió (no repetirlos)
- El programa del PSST es **general**: no dejar planes de una obra de ejemplo dentro del programa ni generar el PSST de una obra
  si el usuario no lo pidió (se retiró uno de una vía que se había generado sin pedido).
- No mezclar el PSST con el estudio de gestión de riesgos de obra: son documentos y matrices distintos (IPERC de peligros a
  personas vs. matriz de riesgos del proyecto en costo y plazo).
- PSST del usuario (CAR Mujeres, CUI 2717013): pidió "borra la parte 9 que dice firma" → se retiró el anexo de formatos con campos
  de firma (ATS, PETAR, visitas, EPP, inspección y reporte) y se **renumeró todo lo que dependía**: el anexo siguiente pasó a ocupar
  su número, se ajustaron la lista de anexos, el índice (entradas y páginas), los numerales que lo citaban, el texto de los PETS,
  la fuente del cuadro de presupuesto y la matriz de requisitos legales. Al quitar una parte, buscar y corregir todas sus referencias.
- Al editar el Word del usuario, conservar su formato, estilos e imágenes; trabajar sobre una copia y cotejar que lo demás quede igual.
- No escribir nombres ni CIP de profesionales: dejar líneas en blanco para firmas y colegiaturas.
- No corregir a mano el Word o el Excel final para tapar una actividad faltante: ampliar la biblioteca y volver a generar.
