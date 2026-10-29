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

## Presupuesto del PSST (criterios del usuario, 28-10-2026, PSST del CAR Mujeres CUI 2717013)
- El presupuesto de obra lo hace el ingeniero en **Delphin**, no en S10 (`importar_s10.py` solo sirve si hay un PDF del S10).
- **Personal en obra** = horas-hombre de obreros del presupuesto de obra (operario, oficial y peón, incluidos operador de equipo y
  operario electromecánico; reporte de recursos del Delphin) ÷ (8 h × días de trabajo por mes × meses del cronograma de obra),
  redondeado hacia arriba. No se divide entre las horas de un año natural. CAR Mujeres: 149,541.8166 hh ÷ (8 × 24 × 10) = 77.89
  → **78 obreros**. El plazo lo confirma el ingeniero con su cronograma (10 meses). El número de trabajadores del presupuesto de
  obra (61) era provisional; manda el calculado.
- Solo los obreros calculados: no sumar personal técnico ni juegos para visitas. EPP **uno por obrero**, sin reposiciones
  supuestas (× 2, × 4); arnés, línea de vida y EPP de tareas especiales con la cantidad del presupuesto de obra.
- **Insumos**: solo los que ya están en el presupuesto de obra, con sus precios actualizados. No agregar insumos nuevos (el
  ingeniero tendría que crearlos en el Delphin) ni equipos caros de uso ocasional. Cambiar lo mínimo para que el ingeniero no
  rehaga su presupuesto.
- Cantidades en **und, jgo, rll o par**; nada "por mes" en los insumos (la capacitación sigue en meses, como en el presupuesto de
  obra).
- **Sustento** de cada cantidad ("uno por obrero", o por frente de trabajo de toda la obra: edificaciones, exteriores,
  instalaciones y drenaje, no solo el colector) y **fuente** de cada precio (lista de insumos del presupuesto de obra, o cotización
  con tienda y fecha; precio sin IGV = precio de tienda ÷ 1.18). El ingeniero pregunta de dónde sale cada número.
- Entregar: el Excel del PSST (hojas RESUMEN, PERSONAL EN OBRA, SUSTENTO CANTIDADES, una por partida, IPERC; sin hojas
  protegidas, decimales completos, amarillo = datos, gris = cálculo, verde = resultado); el Word del plan y las especificaciones
  con las mismas cantidades, precios y total; y una hoja "PARA DELPHIN" con lo que el ingeniero debe cambiar (cantidad, precio o
  sin cambio).
- Entidad: Gerencia Territorial Bajo Mayo (GTBM). Nunca "Proyecto Especial Huallaga Central y Bajo Mayo" ni "PEHCBM".
- Confirmar que las horas-hombre e insumos son de la misma obra del PSST antes de usarlos.
