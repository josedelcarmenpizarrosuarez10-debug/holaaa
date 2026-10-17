# Plan de Seguridad y Salud en el Trabajo (PSST) – programa estándar

Carpeta independiente de los colectores y de `gestion_riesgos/`. Sirve para **cualquier tipo de obra en el Perú**
(vial, edificación, saneamiento, drenaje, puentes, electrificación): el programa reconoce las actividades a partir de
las partidas del presupuesto y arma el IPERC, los programas y el Word del plan.

## Estructura
```
seguridad_salud_trabajo/
├── herramientas/
│   ├── biblioteca.py     base de conocimiento: 36 actividades, 131 peligros, controles por jerarquía, EPP, PETS, PETAR, capacitaciones
│   ├── importar_s10.py   presupuesto S10 (PDF) -> insumos/DATOS_PROYECTO.xlsx (solo ítem, descripción, unidad y metrado)
│   ├── nucleo.py         reconoce actividades, calcula el IPERC (R.M. N.° 050-2013-TR) y los programas -> _calc/psst.json
│   ├── iperc_xlsx.py     Excel: IPERC con fórmulas, resumen, mapa de calor, EPP, PETS-PETAR, capacitación, inspecciones, monitoreo, indicadores
│   ├── figuras.py        gráficos del Word (histograma, mapa de calor, niveles, organigrama, jerarquía, emergencia, cronograma)
│   ├── psst_docx.py      Word del plan (estructura de la Norma G.050 y del D.S. N.° 011-2019-TR) con anexos
│   ├── docx_util.py      estilo común de los Word
│   └── generar.py        corre todo en orden
└── proyectos/
    └── <PROYECTO>/
        ├── insumos/DATOS_PROYECTO.xlsx      hojas PROYECTO, PARTIDAS, PERSONAL y EMERGENCIA (celdas amarillas)
        └── entregables/                     PLAN_SEGURIDAD_SALUD_TRABAJO_<codigo>.docx, MATRIZ_IPERC_PSST_<codigo>.xlsx, _calc/
```

## Proyecto nuevo (desde la raíz del repositorio)
```
mkdir -p seguridad_salud_trabajo/proyectos/<NOMBRE>/insumos
python3 seguridad_salud_trabajo/herramientas/importar_s10.py <presupuesto_S10.pdf> seguridad_salud_trabajo/proyectos/<NOMBRE>/insumos/DATOS_PROYECTO.xlsx
#   (sin PDF: importar_s10.py --plantilla <ruta>  y pegar las partidas en la hoja PARTIDAS)
#   llenar PROYECTO (código, nombre, CUI, condiciones: selva, altura, cauces, zona_poblada, transito), PERSONAL y EMERGENCIA
python3 seguridad_salud_trabajo/herramientas/generar.py seguridad_salud_trabajo/proyectos/<NOMBRE>
```
Si el programa avisa de "partidas sin actividad reconocida", se agregan las palabras clave en `biblioteca.py` (o una
actividad nueva con sus peligros) y se vuelve a generar. Nunca se edita a mano el Word ni el Excel final.

## Método
- IPERC de la R.M. N.° 050-2013-TR: probabilidad = A + B + C + D (personas, procedimientos, capacitación, exposición);
  nivel = probabilidad x severidad (trivial, tolerable, moderado, importante, intolerable). Significativo: importante o intolerable.
- Inicial con B = 2 y C = 2; residual con B = 1 y C = 1 y la exposición o severidad que reducen los controles de ingeniería.
- Controles en el orden de la jerarquía (Ley N.° 29783, art. 21): eliminación, sustitución, ingeniería, administrativos, EPP.
- Comité de SST con 20 o más trabajadores en el pico; supervisor de SST con menos.

## Proyectos
| Proyecto | CUI | Carpeta |
|---|---|---|
| Vía SM-107 Tingo de Ponasa – Shamboyacu | 2673852 | `proyectos/SM-107_TINGO_DE_PONASA_SHAMBOYACU/` |
