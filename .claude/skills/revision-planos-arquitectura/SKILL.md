---
name: revision-planos-arquitectura
description: Revisar un juego de planos de arquitectura en DXF (planta general, desarrollo de edificaciones, obras exteriores y complementarias, detalles) con la lista de 14 indicaciones de revisión que dio el usuario, y entregar un informe en Word y una matriz de observaciones en Excel. Usar cuando el usuario pida revisar, verificar o compatibilizar planos de arquitectura de cualquier proyecto.
---
# Revisión de planos de arquitectura (14 indicaciones)

Lista dada por el usuario el 28-10-2026 (indicaciones que recibió para revisar planos; primer caso: I.E. N.° 292 Ciudad Satélite,
CUI 2684251, 42 DXF y 106 láminas, 118 observaciones).

## Antes de empezar
- Los planos son del usuario: **solo se leen, nunca se modifican**. Su carpeta habitual es `D:\PROGRAMAS\Conversor_DWG_DXF\DXF_convertidos`;
  si no está en la sesión, pedir acceso a esa ruta en vez de pedir que suba archivos.
- Identificar el proyecto por el rótulo (nombre y CUI) y citarlo así. Un proyecto nuevo se trabaja aparte de los del repositorio.
- Los DXF grandes (60 a 100 MB) se leen por partes con ezdxf; ubicar cada planta y cada presentación (layout) con su ventana.

## Las 14 indicaciones y cómo verificarlas en el DXF
| N.° | Indicación | Cómo se verifica |
|---|---|---|
| 1 | El emplazamiento de la planta general coincide con el desarrollo de cada módulo | Comparar ejes (cantidad y separación), dimensiones y forma de cada edificación en la planta general con su plano de desarrollo |
| 2 | Láminas completas; en el layout las escalas corresponden con la descripción y el nombre del proyecto | Escala real de cada ventana (altura de la vista en papel ÷ altura en modelo) contra la escala del título y del rótulo; nombre y CUI del rótulo en todas las láminas; códigos y números de lámina sin repetir |
| 3 | Cotas correctas en planta y en corte | Cotas con texto forzado: el valor escrito frente a la medida real de la cota |
| 4 | Nomenclaturas de valorizaciones correctas | Códigos de edificaciones, obras exteriores (OE) y complementarias (OC) iguales en rótulos, títulos y planta general (confirmar con el usuario qué entiende por "valorizaciones") |
| 5 | Los desniveles están conectados con escaleras o rampas | NPT de cada plataforma y la escalera o rampa que la une con la vecina |
| 6 | El detalle de pisos corresponde a cada corte o detalle | Códigos de piso de la planta frente a los cortes y al cuadro de acabados |
| 7 | Las dimensiones del techo van de acuerdo con la línea proyectada y los cortes, verificado en la planta general | Proyección del techo en planta, cortes y planta de techos |
| 8 | El primer nivel tiene NPT y cota (nivel de la plataforma) | Textos NPT y cota absoluta en la planta del primer nivel |
| 9 | Hay elevaciones lateral, frontal y posterior | Que cada edificación tenga las tres y bien tituladas |
| 10 | Leyenda de colores y acabados, cuadro de vanos y detalle de vanos de acuerdo con planta y corte | Códigos de vanos de la planta frente al cuadro de vanos; leyenda de colores con color y descripción |
| 11 | Los pisos tienen código de acabado | Código en cada ambiente |
| 12 | Cada nomenclatura que se coloca está en su leyenda | Todo código usado en planta aparece en una leyenda o cuadro |
| 13 | Bajo los servicios higiénicos del segundo piso hay falso cielo raso | Cortes que pasan por los SS.HH. de pisos superiores, con el falso cielo dibujado y rotulado |
| 14 | El plano clave pequeño de los planos de desarrollo corresponde al número de la edificación | Que el plano clave resalte la edificación del rótulo; láminas sin plano clave |

Errores frecuentes que aparecieron en el primer caso: rótulos que quedaron de otro proyecto; rótulos copiados sin actualizar (varias
láminas con el mismo título y código); escala del título distinta a la de la ventana; cotas forzadas; "módulo", "bloque" y
"edificación" mezclados; un mismo prefijo para dos cosas (P- para pisos y puertas); vanos con un código en planta y otro en el
cuadro; códigos escritos con cero en vez de O ("0C-06", "0E-05"); dos versiones casi iguales del mismo plano.

## Entregables
- **Excel** (matriz de observaciones con fórmulas): N.°, indicación, plano y lámina, observación, prioridad (alta, media, baja),
  estado (Pendiente / Corregido) y un resumen por indicación que se actualiza solo.
- **Word** (informe): resultado por indicación (Cumple / Parcial / No cumple / Por verificar), lo más importante primero y lo que
  no se pudo cerrar desde el plano y por qué.
- Ambos en español, sin nombres ni CIP, adjuntos en el chat. Lo que no se puede comprobar con el DXF se dice como "por verificar",
  nunca se da por cumplido.
