---
name: psst-iperc
description: Elaborar el Plan de Seguridad y Salud en el Trabajo (PSST) de cualquier obra en el Perú con su matriz IPERC (R.M. N.° 050-2013-TR), en Word ordenado con tablas y gráficos y Excel con fórmulas, usando el programa general de la carpeta PROGRAMA DE ELABORACION DE PSST/. Usar cuando el usuario pida un PSST, IPERC, matriz IPER, plan de seguridad de obra o actualizar uno existente.
---
# PSST con matriz IPERC (programa estándar)

1. Crear `"PROGRAMA DE ELABORACION DE PSST/proyectos/<NOMBRE>/insumos/"`, copiar `plantilla/DATOS_PROYECTO.xlsx` y cargar partidas:
   `python3 "PROGRAMA DE ELABORACION DE PSST/herramientas/importar_s10.py" <presupuesto.pdf> <.../insumos/DATOS_PROYECTO.xlsx>`
   (o pegarlas en la hoja PARTIDAS). Llenar PROYECTO, PERSONAL (histograma por mes) y EMERGENCIA.
   Condiciones del lugar en PROYECTO.condiciones: selva, altura (o altitud > 2500), cauces, zona_poblada, transito.
2. `python3 "PROGRAMA DE ELABORACION DE PSST/herramientas/generar.py" "PROGRAMA DE ELABORACION DE PSST/proyectos/<NOMBRE>"`.
   Solo generar el PSST de una obra cuando el usuario lo pida; la carpeta guarda el programa general.
3. Si avisa "partidas sin actividad reconocida": ampliar `biblioteca.py` (regex de la actividad o actividad nueva con
   `pel(...)`), nunca editar a mano el Word o el Excel.
4. Revisar el Word (soffice a PDF, pdftoppm) y el Excel recalculado con LibreOffice (sin errores #).

Reglas: todo en español; sin nombres ni CIP de profesionales (líneas en blanco); sin texto que revele IA; citar el proyecto
por nombre y CUI; el PSST va separado de `gestion_riesgos/` y de los colectores; los metrados del presupuesto no se modifican.
Método: probabilidad A+B+C+D (A por cuadrilla, B=C=2 inicial y 1 residual), severidad 1-3, nivel P x S
(4 trivial, 5-8 tolerable, 9-16 moderado, 17-24 importante, 25-36 intolerable); significativo = importante o intolerable;
el residual de todo peligro debe quedar en moderado o menos (si no, reforzar controles en la biblioteca).
