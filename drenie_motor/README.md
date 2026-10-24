# Motor de DrenIE (Python) – Terreno, superficies y red de cunetas en planta

Programa auxiliar de DrenIE. DrenIE (interfaz) lo llama por línea de comandos con un archivo de proyecto JSON; el motor lee el
plano DXF, arma el mapa de superficies, traza la red de cunetas, calcula cotas de fondo y caudales, verifica y entrega
resultados en JSON, la planta en DXF (escala real, 1 unidad = 1 m) y vistas previas PNG.

Criterios: `conocimiento/04_cunetas_sobre_terreno.md` y `conocimiento/02_hidrologia_e_hidraulica.md` (valores por defecto en
`drenie_motor/parametros.py`, todos cambiables en el proyecto).

## Uso

```
python -m drenie_motor lluvia  proyecto.json   # lluvia de diseno: serie de la estacion, frecuencias, K-S, IDF, I de diseno
python -m drenie_motor leer    proyecto.json   # lectura, mapa de superficies, imagen de control (confirmar antes de disenar)
python -m drenie_motor disenar proyecto.json   # red, cotas, caudales, 12 comprobaciones, planta DXF y PNG
```

Salida en la carpeta `salida` del proyecto: `lectura.json`, `CONTROL_LECTURA.png`, `resultado.json`,
`PLANTA_RED_CUNETAS.dxf`, `PLANTA_RED_CUNETAS.png`; con `lluvia`: `hidrologia.json`, `HIDROLOGIA.xlsx` (datos, análisis,
Kolmogorov-Smirnov, IDF) y `CURVAS_IDF.png`. Código de salida 0 = bien; 2 = error de datos (mensaje en `error`).

Requisitos: Python 3.10+, `ezdxf`, `shapely` 2, `scipy`, `numpy`, `matplotlib`.

## Orden de trabajo en DrenIE

1. Proyecto → 2. Lectura del plano (`leer`) → 3. Mapa de superficies (confirmar; asignar lo que falte) → 4. Lluvia (estación
SENAMHI, análisis estadístico, Dick y Peschke → I) → 5. `disenar`: áreas de aporte y caudal de cada cuneta, diseño, verificación
→ 6. Planos, metrado y documentos (módulos siguientes).

## Archivo de proyecto (ejemplo completo: `ejemplos/barranquita/proyecto.json`)

| Clave | Contenido |
|---|---|
| `proyecto` | nombre, nombre_corto, codigo (CUI o C.I.) |
| `dxf` | plano del usuario (DXF, ZIP o carpeta con el ZIP en partes) |
| `capas.curvas`, `capas.curvas_texto`, `capas.equidistancia` | curvas de nivel (con elevación o rotuladas a cota 0) |
| `capas.cerco` | capa del cerco o `{"poligono": [...]}` confirmado |
| `capas.ejes` | líneas de cuneta del usuario: `{"capa": "0", "color": 6}` |
| `capas.techos`, `capas.veredas`, `capas.muros` | capas de arquitectura |
| `niveles` | `modo` (`nivelado` o `terreno`), `npt`, `borde_cuneta`, `area_verde`, `zonas` (polígono, nivel, superficie) |
| `superficies` | superficies con nombre (losas, patios techados...): `nombre`, `tipo`, `poligono` o `capa` |
| `superficies_cfg.leyenda` | colores o capas de sombreados → tipo: `[{"sel": {"capa": "AREAS", "color": 3}, "tipo": "verde"}]` |
| `superficies_cfg.rotulos` | textos → tipo (se suman a los de fábrica: AREA VERDE, VEREDA, ESTACIONAMIENTO...) |
| `superficies_cfg.asignaciones` | clics del visor: `{"x", "y", "tipo"}` (punto dentro del área) |
| `superficies_cfg.por_defecto` | tipo para lo no identificado; si falta, el diseño no corre hasta asignarlo |
| `techos_caida`, `caida_por_defecto` | caída por techo: `{"punto", "tipo": "dos_aguas", "cumbrera": [[x, y], [x, y]]}` o `{"punto", "tipo": "una_agua", "lado_bajo": [...]}` |
| `dimensionamiento_adoptado` | la hoja `DIMENSIONAMIENTO.xlsx` con la columna B ADOPTADO llena por el proyectista (el programa la verifica) |
| `secciones` | ancho libre adoptado por eje escrito en el proyecto: `{"EJE-01": 0.45}` |
| `parametros` | cambia cualquier valor de `parametros.py`: `b_int` 0.30 (ancho libre mínimo), `b_max` 1.00, `paso_seccion` 0.05, `hmin` 0.30, `h0` 0.30, `S0` 0.005, `e_muro`, `e_tapa`, `e_fondo` y `e_solado` 0.10, `uniforme` (`sector`, `eje` o `tramo`), `h_b_max` 2.0, `y_b_max` 1.0, `llor_sep` 1.50 |
| `lluvia` | Datos de la estación: `{"estacion": {...}, "archivo": "datos diarios SENAMHI / NASA POWER / CHIRPS", "desde", "hasta", "T": 25, "tc_min": 10, "factor": 1.0, "distribucion": opcional}` o `"serie": {anio: [12 máximas mensuales]}` o `"maximos": {anio: P24}`. Sin datos de estación: `{"I_mmh": ...}` o `{"P24": ..., "tc_min": 10}`. Barranquita: P24 = 169.27 mm, I = 293.18 mm/h (igual al expediente) |
| `descargas` | descargas fijadas por el usuario `[{"nombre": "D1", "x", "y"}]` (sin esto, el motor las propone) |
| `parametros` | cambios a los valores por defecto |

## Reglas que aplica

- **Mapa de superficies** sin montajes ni huecos (la suma de áreas = área del cerco); las cunetas ocupan su franja de 0.60 m y
  recortan las superficies de piso; cada ajuste se informa; lo no identificado queda "sin asignar".
- **Agua de los techos**: cada mitad cae por su alero a la cuneta que está debajo (dos aguas: ambos lados; una agua: lado
  bajo). Se avisan los aleros sin cuneta.
- **Las líneas del usuario mandan**: no se mueven; solo se agregan uniones (perpendiculares, en prolongación o por el camino
  perimetral a 0.60 m del cerco), sin cruzar edificaciones, losas ni otras cunetas, ni cruzarse entre sí.
- **Ninguna cuneta enterrada**: cada descarga (pase en el cimiento del cerco) debe tener el terreno exterior bajo la cota de
  fondo a ≤ 2 m; se eligen las menos descargas que cubren todas las líneas sin pasar la profundidad objetivo (1.00 m). Si una
  parte no tiene salida, no se entrega el diseño y se indican los metros sin salida.
- **12 comprobaciones**: conectividad, contrapendiente, pendiente mínima, profundidades, empalmes, descargas, niveles,
  capacidad, velocidad, distancia a edificaciones, dentro del cerco, todas las líneas del usuario con cuneta.

## Prueba

`python3 ejemplos/barranquita/armar_dxf_prueba.py` arma el plano de prueba de la I.E. N.° 0590 Barranquita (C.I. N.° 468901)
con los datos de entrada del usuario (curvas, techos, veredas, cerco y líneas magenta); luego `leer` y `disenar`.

## Sección de cada tramo y lloraderos

- Medidas: 0.30 × 0.30 es la sección libre; ancho total = libre + 2 muros (0.50); excavación = altura libre + losa de fondo +
  solado (0.50). Una sola medida por sector (todos los ejes que salen por la misma descarga llevan el mayor ancho que pida
  cualquiera de sus tramos); `uniforme: "eje"` da una medida por eje. El dimensionamiento final lo adopta el proyectista en la hoja
  `DIMENSIONAMIENTO.xlsx` (columna B ADOPTADO) y el programa lo verifica.
- Muros y losa de 0.10. Cada tramo pide el menor ancho libre (desde 0.30, de 5 en 5 cm) con el que el tirante más el borde libre
  cabe en la profundidad que da el perfil, con el tirante no mayor que el ancho y la profundidad no mayor que 2 veces el ancho
  (que se pueda encofrar y acabar). Aguas abajo no se angosta. Si con `b_max` no alcanza, se profundiza (redondeado a 5 cm).
- `resultado.json`: `verificacion.hidraulica` (por tramo: área y caudal de techos, pisos y áreas verdes, b, h, tirante, borde libre,
  velocidad), `secciones_por_eje`, `lloraderos` (tramos por lado junto a área verde, N.° = REDONDEAR.MAS(L / 1.50)).
- Lloraderos solo en el muro que da a área verde: PVC 3" @ 1.50 m con caja filtrante de 0.30 × 0.30 de grava y geotextil
  (capa `DRN-LLORADEROS` del DXF; el ancho de cada tramo en `DRN-SECCION-TXT`).
- Comprobación 13: secciones constructivas.
