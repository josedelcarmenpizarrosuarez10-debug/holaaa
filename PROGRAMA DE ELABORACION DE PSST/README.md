# PROGRAMA DE ELABORACIÓN DE PSST

Programa general para elaborar el **Plan de Seguridad y Salud en el Trabajo (PSST)** de **cualquier tipo de obra en el Perú**:
vías, edificaciones, saneamiento, drenaje, puentes, electrificación y otras. No depende de un proyecto en particular.

Con el presupuesto de la obra y unos datos generales, el programa reconoce las actividades, arma la **matriz IPERC**
(R.M. N.° 050-2013-TR) y entrega el **Word del plan**, ordenado con tablas y gráficos, y el **Excel con fórmulas**.

## Contenido del PSST que genera
1. Generalidades: objetivo, alcance, datos de la obra, componentes del presupuesto, histograma de personal.
2. Marco normativo: Ley N.° 29783, D.S. N.° 005-2012-TR, D.S. N.° 011-2019-TR, Norma G.050, R.M. N.° 050-2013-TR, R.M. N.° 375-2008-TR,
   R.M. N.° 312-2011-MINSA, SCTR, NTP de señalización y extintores, y las normas que correspondan a la obra (tránsito, electricidad, explosivos).
3. Política de SST, objetivos, metas e indicadores.
4. Organización: organigrama, funciones y comité o supervisor de SST según el número de trabajadores.
5. IPERC: metodología, actividades evaluadas, resultados inicial y residual, mapa de calor, riesgos intolerables y jerarquía de controles.
6. Mapa de riesgos y señalización (NTP 399.010-1).
7. Procedimientos: PETS, PETAR (altura, excavaciones, caliente, espacios confinados, izaje, eléctrico, explosivos, cauces), ATS y charla diaria.
8. Equipos de protección personal y colectiva.
9. Programa de capacitación con cronograma.
10. Programa de inspecciones y auditorías.
11. Salud ocupacional: exámenes médicos, SCTR, monitoreo de agentes, bienestar y primeros auxilios.
12. Subcontratistas y proveedores.
13. Plan de respuesta ante emergencias: escenarios, brigadas, flujograma y directorio.
14. Notificación e investigación de accidentes.
15. Registros obligatorios, indicadores (IF, IG, IA) y mejora continua.
16. Partidas de SST del presupuesto.
17. Anexos: matriz IPERC completa, matriz de EPP por puesto, formato de ATS y lista de verificación del PETAR.

El Excel trae: datos, criterios, IPERC con fórmulas, resumen, mapa de calor, EPP, PETS-PETAR, capacitación, inspecciones,
monitoreo, indicadores mensuales, relación partida-actividad y directorio de emergencia.

## Estructura
```
PROGRAMA DE ELABORACION DE PSST/
├── GENERAR_PSST.bat          en Windows: arrastrar la carpeta del proyecto sobre este archivo
├── plantilla/DATOS_PROYECTO.xlsx    libro de datos en blanco (celdas amarillas)
├── herramientas/
│   ├── biblioteca.py         base de conocimiento: 36 actividades, 131 peligros, controles, EPP, PETS, PETAR, capacitaciones
│   ├── importar_s10.py       presupuesto S10 en PDF -> hoja PARTIDAS (solo ítem, descripción, unidad y metrado)
│   ├── nucleo.py             reconoce las actividades y calcula el IPERC y los programas
│   ├── iperc_xlsx.py         Excel del IPERC y programas
│   ├── figuras.py            gráficos
│   ├── psst_docx.py          Word del plan
│   ├── docx_util.py          estilo de los Word
│   └── generar.py            corre todo en orden
└── proyectos/                una carpeta por obra: <OBRA>/insumos/DATOS_PROYECTO.xlsx y <OBRA>/entregables/
```

## Cómo se usa
1. Crear `proyectos/<OBRA>/insumos/` y copiar ahí `plantilla/DATOS_PROYECTO.xlsx`.
2. Cargar las partidas:
   - con el PDF del S10: `python3 herramientas/importar_s10.py <presupuesto.pdf> proyectos/<OBRA>/insumos/DATOS_PROYECTO.xlsx`;
   - o pegarlas en la hoja PARTIDAS (ítem, descripción, unidad, metrado; los títulos sin unidad).
3. Llenar las hojas PROYECTO (código, nombre, CUI, entidad, ubicación, plazo, altitud, clima y condiciones del lugar:
   `selva, altura, cauces, zona_poblada, transito`), PERSONAL (trabajadores por mes) y EMERGENCIA (teléfonos locales).
4. Generar: `python3 herramientas/generar.py proyectos/<OBRA>` (o arrastrar la carpeta sobre `GENERAR_PSST.bat`).
5. Salen en `proyectos/<OBRA>/entregables/`: `PLAN_SEGURIDAD_SALUD_TRABAJO_<código>.docx` y `MATRIZ_IPERC_PSST_<código>.xlsx`.

Si el programa avisa de "partidas sin actividad reconocida", se agregan las palabras clave en `herramientas/biblioteca.py`
(o una actividad nueva con sus peligros) y se vuelve a generar. El Word y el Excel finales no se editan a mano.
Requisitos: Python 3 con `openpyxl`, `python-docx` y `matplotlib`; `pdftotext` (poppler) para leer el PDF del S10.

## Método del IPERC
- Probabilidad = A + B + C + D (personas expuestas, procedimientos, capacitación, exposición); nivel = probabilidad x severidad:
  4 trivial, 5 a 8 tolerable, 9 a 16 moderado, 17 a 24 importante, 25 a 36 intolerable. Significativo: importante o intolerable.
- Evaluación inicial con B = 2 y C = 2; residual con B = 1 y C = 1 y la reducción de exposición o severidad de los controles de ingeniería.
- Controles en el orden de la jerarquía (Ley N.° 29783, art. 21): eliminación, sustitución, ingeniería, administrativos y EPP.
- Comité de SST con 20 o más trabajadores en el mes de mayor personal; supervisor de SST con menos.
