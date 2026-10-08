---
name: planos-ordenados
description: Dibujar o corregir planos DXF (plantas, perfiles longitudinales, secciones transversales, detalles, isometricos, laminas de partidas) ordenados y legibles, a escala real, sin textos encimados ni verticales, con el estilo del proyecto (letra grande, concreto con relleno gris, colores para fondo blanco). Usar siempre que se genere o mejore cualquier lamina DXF de drenaje, colector, cunetas, cajas o tapas.
---

# Planos ordenados, a escala real y sin cruces

Motor del estilo: `herramientas/dxf_base.py` (capas, colores, grosores, textos, cotas, llamadas, rotulo) y
`herramientas/dxf_planta.py` (`perfil_tramo`: franja de etiquetas y guitarra). Lamina de referencia del estilo:
`herramientas/render_tapa/dxf_tapa.py` (DP-06B). Todo cambio se hace en el generador, nunca a mano en el DXF.

## 1. Escala real (no negociable)
- 1 unidad de dibujo = 1 m. Cada lamina A1 (841 x 594 mm) tiene su escala 1:N y factor f = N/1000.
- Perfiles: horizontal = vertical (sin exageracion). Si algo mide 0.55 m, se dibuja de 0.55 m.
- Las cotas miden el dibujo (`<>`); solo se escribe texto fijo cuando la cota es una pulgada ("2\"") o una
  aclaracion; nunca para "corregir" una medida mal dibujada.
- Antes de entregar: comparar 3 o 4 cotas del dibujo con el diseno (memoria / metrado).

## 2. Escalas recomendadas (que el dibujo llene la lamina)
- Planta general 1/200; perfil longitudinal 1/50 (en franjas o tramos de 20 a 36 m).
- Secciones transversales 1/15 (2 x 2 por lamina) o 1/20 (3 por lamina); nunca 4 en fila a 1/25 si quedan chicas.
- Cajas 1/25; detalles 1/10, 1/5, 1/2; perfiles de angulos 1/1 (cotas en mm).
- Si una vista ocupa menos de un tercio de su espacio, subir la escala.

## 3. Textos
- Fuente Arial (`arial.ttf`), titulos en Arial negrita, color 160 (azul). Textos negros (7).
- Altura en papel: titulo de vista 4.0 a 6 mm, textos y llamadas 2.2 a 3.5 mm, cotas 3.0 mm, notas 2.2 a 3 mm.
  (en `dxf_base` el factor K_TXT por capa ya lo aplica).
- **Nunca texto vertical (rot=90) para rotulos de elementos.** Solo se permite vertical en cotas verticales.
- Llamadas largas: maximo ~62 caracteres por linea (se parten solas en `llamada`); maximo 2 a 3 lineas.

## 4. Etiquetas sin cruces (regla de la franja)
Para perfiles y cualquier vista con muchos rotulos (registros, cunetas, cajas, lindero, colectores vecinos):
1. Juntar todas las etiquetas en una lista `(x_punto, y_punto, [lineas], color)` en lugar de dibujarlas al vuelo.
2. Colocarlas en una franja horizontal encima del dibujo, por filas de 2 lineas.
3. Procesar de derecha a izquierda; cada etiqueta va a la fila mas baja donde:
   - no se superpone con otro texto de la misma fila (con 2 mm de holgura), y
   - su texto no tapa la linea de llamada de una etiqueta ya puesta en una fila mas alta.
4. Linea vertical fina desde el punto (con un circulito) hasta la fila; texto horizontal a su derecha.
   Si el texto se saldria del marco (x > 826 mm de papel), va a la izquierda de su linea.
5. Limitar a 8 filas (evita bucles) y dejar el titulo de la vista por encima de la ultima fila.
Ver la implementacion en `perfil_tramo` (bloque "etiquetas en la franja superior").

En vistas con pocas llamadas (secciones, detalles): columna de textos a un lado, ordenada de arriba hacia
abajo igual que los puntos que senalan, para que las lineas no se crucen.

## 5. Tablas y guitarras
- Columna propia para los nombres de fila, separada por una linea vertical; los valores empiezan despues.
- Valores centrados en su columna; no colocar dos columnas a menos de 12 mm de papel (omitir la menos importante).

## 6. Margenes y orden de la lamina
- Todo dentro del marco interior (x de 25 a 831 mm, y de 10 a 584 mm). Nada encima del rotulo (esquina inferior
  derecha 185 x 95 mm).
- Zonas fijas: vistas arriba; leyenda, notas y cuadros abajo a la izquierda y al centro; rotulo abajo a la derecha.
- Elementos de referencia (colectores vecinos, arquitectura) angostos y en gris; no deben empujar el dibujo fuera.

## 7. Estilo grafico (fondo blanco)
| Elemento | Capa / color | Grosor |
|---|---|---|
| Concreto cortado | contorno 250 + relleno solido RGB (226,226,226) al fondo | 0.50 |
| Angulos metalicos | 5 (azul) contramarco, 140 (celeste) marco | 0.40 |
| Acero corrugado | 1 (rojo); barras en seccion a diametro real, rellenas | 0.35 |
| Acero liso (asas) | 30 (naranja) | 0.35 |
| Cotas | 94 (verde oscuro), tic oblicuo | 0.18 |
| Llamadas | 30 (naranja), finas | 0.18 |
| Agua | 150 + relleno celeste | 0.25 |
| Ocultos | linea discontinua | 0.25 |
- Los rellenos solidos van al fondo (`set_redraw_order`) para que nunca tapen lineas ni textos.
- Evitar amarillo, cian claro y blanco puro como color de linea.

## 8. Verificacion antes de entregar (obligatoria)
1. Regenerar con el script del proyecto (p. ej. `python3 herramientas/planos_dxf.py`).
2. `doc.audit()` sin errores.
3. Renderizar cada lamina tocada a PNG (ezdxf drawing + matplotlib, una sola pasada de `draw_layout` y luego
   recortar por la caja de cada lamina) y mirar: textos encimados, textos fuera del marco, lineas cruzadas,
   vistas pequenas, cotas que no coinciden con el diseno.
4. Corregir y repetir hasta que la lamina se lea limpia. Enviar el DXF y la vista previa en PNG (no PDF).

## 9. Coherencia entre laminas
- Un mismo elemento se dibuja igual en todas las laminas (detalle, planta, perfil, isometrico, render).
- Si dos laminas se contradicen, avisar al usuario con las opciones y recomendar la que coincide con su metrado;
  no cambiar el metrado sin que lo pida.

## 10. Herramientas listas en dxf_base (usarlas siempre)
- `lam.franja(items, y0, abajo=True|False)`: etiquetas horizontales en filas, sin cruces, dentro del marco
  (planta, isometrico general). Si dos puntos caen casi en el mismo x, unir sus textos en una sola etiqueta.
- `lam.juntar_llamadas()` ... `lam.volcar_llamadas()`: las llamadas de una vista se agrupan por columna de texto
  y se reordenan para que ninguna linea cruce a otra (secciones, cajas, detalles).
- `lam.columna_llamadas(items, xt, ytop, ybot)`: lo mismo, explicito.
- `lam.leyenda2(...)`: leyenda con muestras grandes (concreto con relleno, lineas gruesas, barras), en 1 o 2 columnas.
- `lam.notas(..., ancho_mm=)`: ajusta las lineas al ancho disponible; `legado=True` solo para laminas congeladas.
- `lam.tabla(...)`: la letra se ajusta sola al ancho de cada celda.
- Laminas congeladas (no tocar): comprobar con una huella (tipo, capa, punto, texto de cada entidad dentro de su
  caja) antes y despues de regenerar; deben quedar identicas.

## 11. Lecciones del juego del CAR Mujeres (herramientas/mujeres/planos_m.py)
- Si la losa de un perfil mide menos de 3 mm en papel, subir la escala del perfil detallado (1/25) y partir en mas
  tramos; el perfil general puede quedar a 1/100.
- Los cuadros de metrados de las laminas se leen de la planilla del presupuesto (valores guardados), nunca se recalculan.
- Isometricos con elementos a 45 grados: girar la vista y ordenar las caras por profundidad (si no, quedan de canto).
- Etiquetas de un isometrico largo y en diagonal: junto a cada punto, del lado libre; la franja horizontal deja lineas largas.
- Antes de rehacer un plano ajeno, leer su metrado: el detalle debe dibujar lo que se metro (p. ej. rebaje de la tapa).

## 12. Lecciones del juego del CAR Varones (herramientas/varones/planos_v.py)
- Al reutilizar modulos de otro tramo, buscar textos fijos (caudales, cotas de piso, cantidades de registros y juntas, cerco)
  y convertirlos en parametros del modulo con el valor anterior por defecto; cada proyecto los fija en su compat.py.
  Comprobar con la huella que el otro tramo queda identico.
- Si la planilla guarda formulas sin valores, recalcular una copia con LibreOffice (planilla_v.py) y leer de ahi los cuadros.
- Franja de etiquetas: un rotulo cuyo punto queda bajo el texto de otro ya puesto no tiene fila libre y sube al borde de la
  lamina. En los extremos (cajas, referencias) usar pocas etiquetas, cortas, o texto suelto junto al objeto (LINDERO).
- Toda lamina con presentaciones de AutoCAD (dxf_layouts.presentaciones) y lamina indice DP-00 (dxf_layouts.indice).
