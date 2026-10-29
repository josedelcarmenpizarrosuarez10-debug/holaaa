---
name: conocimiento-drenaje-pluvial
description: Base de conocimiento completa del usuario en drenaje pluvial (desde el 03-10-2026) — reglas, hidrología, colector frontal, cunetas sobre terreno, planos DXF, metrado/ACU/especificaciones, componentes (canaletas, montantes, rejillas, juntas, lloraderos, tapa ciega, bancas) y documentos del expediente. Usar SIEMPRE antes de diseñar, dibujar, metrar o redactar cualquier cosa de drenaje, en este repositorio o en el programa DRENIE.
---
# Base de conocimiento de drenaje pluvial

Todo lo aprendido con el usuario está escrito al mínimo detalle en `conocimiento/` (8 capítulos, unas 7 500 líneas, con
valores exactos, fórmulas, archivos y funciones, cada corrección del usuario con su fecha y una sección final
"Para implementarlo en un programa"). La fuente original son los mensajes del usuario en `conocimiento/_fuentes/mensajes_usuario.txt`.

**Antes de trabajar, leer el capítulo del tema** (y siempre el 01). No repetir errores que el usuario ya corrigió: cada
capítulo tiene su tabla de correcciones.

| Capítulo | Tema | Leer cuando |
|---|---|---|
| `conocimiento/01_reglas_y_forma_de_trabajo.md` | Reglas permanentes, proyectos y CUI, nombres oficiales, cadena hidráulica, códigos de lámina vigentes, técnicas de trabajo verificadas | Siempre, al empezar |
| `conocimiento/02_hidrologia_e_hidraulica.md` | Estaciones y series, análisis estadístico (formato del usuario), IDF, tc, C, FS, método racional, Manning, perfil de flujo, cajas y pozas | Lluvia, caudales, capacidad |
| `conocimiento/03_colector_frontal.md` | Colector cubierto de los 3 CAR: geometría, perfil, estructura E.060/HL-93, registros y tapa ciega, empalmes, cajas CL/CC, juntas, coordinación entre expedientes | Colector o cajas |
| `conocimiento/04_cunetas_sobre_terreno.md` | DXF y curvas, TIN, cerco = límite, cuneta bajo cada caída de techo, red, chaflanes 45°, cotas de fondo, 11 comprobaciones, Barranquita | Cunetas de un local nuevo |
| `conocimiento/05_planos_dxf.md` | Escala real, láminas y rótulo, capas y colores, textos sin cruces, plantas, perfiles con guitarra, secciones con acero, detalles, isométricos, layouts, vista previa | Cualquier plano |
| `conocimiento/06_metrado_acu_especificaciones.md` | Partidas Delphin, hojas de la planilla, fórmulas de metrado, ACU y precios CAPECO 2026, edición del xlsx por XML, especificaciones técnicas | Metrado, presupuesto, especificaciones |
| `conocimiento/07_componentes_complementarios.md` | Canaletas, montantes, falsa columna, sumideros, rejilla, juntas de cunetas, lloraderos, tapa ciega, bancas OC-01 | Esos componentes |
| `conocimiento/08_documentos_del_expediente.md` | Memorias hidrológica, descriptiva y de cálculo (Excel y PDF), análisis estadístico, índice de planos, carátulas, estilos Word | Documentos |

Skills específicos que complementan: `diseno-colector-pluvial`, `planteamiento-cunetas-terreno`, `planos-ordenados`,
`metrado-cunetas`, `psst-iperc`, `revision-planos-arquitectura`. Los criterios del motor de DRENIE agregados después del 24-10
están en `drenie_motor/README.md`. La bitácora (`BITACORA_CONVERSACION.md`) sigue siendo el registro fechado; cuando se aprenda
algo nuevo, anotarlo en la bitácora **y** en el capítulo que corresponda, y regenerar el manual Word:
`python3 herramientas/conocimiento_docx.py` -> `conocimiento/MANUAL_TECNICO_DRENAJE_PLUVIAL.docx`.

Pendientes abiertos que los capítulos dejan anotados (no resolver sin el usuario): caudales rotulados en DC-16 a DC-19 de
Barranquita (planos impresos), tapa del CAR Mujeres (partida con marco vs. plano de tapa ciega), registro R-07 del CAR Mujeres
en el cruce de camiones, fechas de octubre/setiembre en documentos del Refugio, "SEPTIEMBRE" en carátulas del CAR Mujeres,
diferencias canaleta 0.25 x 0.20 vs 0.20 x 0.25, abrazaderas @1.50 vs cada 4 m, recubrimiento de falsa columna 2 vs 4 cm,
leyenda de cunetas que cita OS.060.
