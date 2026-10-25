# 04 — Planteamiento de cunetas sobre terreno (algoritmo completo)

Base de conocimiento del repositorio. Tema: cómo se plantea una red de cunetas pluviales de un local (colegio, CAR, hogar)
a partir del plano general en DXF con topografía, hasta las cotas de fondo, la verificación y los datos para planos y metrado.
Implementación de referencia: **I.E. N.° 0590 Barranquita (Lamas), C.I. N.° 468901 (confirmar si es el CUI)**, carpeta
`herramientas/barranquita/`. Al final se agrega lo aplicable a las cunetas de los CAR de Morales (CAR Varones, CUI 2705619;
Hogar de Refugio Temporal "Mujeres Violentadas", CUI 2675514).

Fuentes: mensajes del usuario (20 y 21 de octubre de 2026 para Barranquita; 4, 8 y 15 de octubre para Varones/Refugio),
`BITACORA_CONVERSACION.md`, skill `planteamiento-cunetas-terreno`, código de `herramientas/barranquita/` y los JSON de
`entregables_barranquita/_calc/`. Todo lo que aquí se cita existe en esas fuentes; donde algo no quedó en el repositorio se dice.

---

## 1. Resumen en una página

| Concepto | Valor / regla (Barranquita, versión vigente) |
|---|---|
| Sección | ancho total 0.60 m = muros 0.10 + 0.40 libres; losa de fondo 0.10; losa tapa 0.10 (tramos tapados) |
| Profundidad | h inicial 0.30 m en todo ramal; mínima 0.25 m (altura libre, bajo la losa si es tapada) |
| Pendiente de fondo | 0.5 % mínima (S0 = 0.005); con rasante horizontal la profundidad crece 0.5 cm por metro |
| Niveles interiores | NPT pisos y pasadizos +184.65 = borde de cuneta +184.65 (al ras, junta asfáltica al mismo nivel); áreas verdes +184.60; patio de maniobra +184.50 con cuneta al ras +184.50 |
| Límite | cerco perimétrico: ninguna cuneta ni obra fuera; solo el agua sale por un pase en el cimiento del cerco |
| Dónde va cuneta | bajo cada caída de techo; dos aguas = a ambos lados; una agua = lado bajo; las líneas magenta del usuario mandan |
| Quiebres en planta | toda esquina con giro > 50° se ochava con chaflán de 0.60 m por lado (quiebres de 45°) |
| Tapados | donde cruza veredas, ingresos y el pase del cerco; tapas de inspección 0.60 x 0.60 al inicio, final, empalmes y cada 10 m máx. |
| Acero | solo si h ≥ 0.40 m (rejilla a fondo) o tramo tapado; si no, concreto simple |
| Hidráulica | método racional por tramo; Manning n = 0.015 (capacidad) y 0.013 (velocidad); borde libre ≥ 0.05 m; V ≤ 3.0 m/s |
| Verificación | 11 comprobaciones; ciclo diseño ↔ verificación (`calcula_b.py`) hasta 11 de 11 |
| Resultado | 19 ejes (EJE-01 a EJE-19), 968.78 m (43.96 m tapados), 4 sistemas, descargas D1 a D4 por gravedad |

Orden de ejecución:
```
python3 herramientas/barranquita/calcula_b.py     # diseno_b.main() + verifica_b.main() en ciclo (hasta 8 vueltas)
python3 herramientas/barranquita/planos_b.py      # DXF DC-00 a DC-19 (usa perfiles_b, planta_cunetas_b, cortes_b, descargas_b)
python3 herramientas/barranquita/excel_b.py       # CUADRO_TRAMOS_CUNETAS_IE0590_BARRANQUITA.xlsx
```
Sin la base del sitio (`base_sitio.pkl`) solo se puede: `verifica_b.py --solo-lluvia` (cambio de lluvia sobre la geometría
vigente) y el metrado/memorias con las cachés `_calc/coberturas.json` y `_calc/junta_piso.json`.

**Regla de oro posterior:** el 21-10-2026 (15:39) el usuario imprimió los planos: "ya no alteres planos, ya imprimí el último que
me pasaste". Desde entonces los planos de Barranquita NO se regeneran; los cambios van a los documentos y se le avisan.

---

## 2. Lectura del DXF grande

### 2.1 Cómo llegó el archivo
- 20-10-2026 02:05: el usuario pide "otro colector... no es colector": un planteamiento preliminar de cunetas de un colegio, con
  curvas topográficas, edificaciones, muros, cerco perimétrico y un planteamiento preliminar de cunetas suyo.
- 02:10: intentó subir `PLANTA_GENERAL_590_2.7z`; 02:15: el límite de subida es 30 MB y su archivo pesaba 60 MB comprimido;
  02:30: lo subió partido en `PARTE_01.zip` y `PARTE_02.zip`. El DXF descomprimido pesa **332 MB**.
- 20-10-2026 16:31-16:34: nueva versión "PLANTA_GENERAL_590 ULTIMA VERSION.dxf" (**381 MB**, ZIP en 3 partes). **El orden real de
  las partes no era el del nombre**: PARTE_02, PARTE_03, PARTE_01. Regla: si el ZIP partido no abre, probar los órdenes posibles.
- El DXF grande **no se versiona** (pesa demasiado). Se extrae una base reducida: `insumos/barranquita/base_sitio.pkl` (7.6 MB).

### 2.2 Las tres copias del conjunto
- El DXF traía **3 copias del conjunto** (planta repetida en distintas posiciones del espacio modelo).
- La copia real es la que está **sobre las curvas de nivel C-TOPO, en coordenadas UTM** (WGS84, zona del proyecto):
  ventana `X0, X1, Y0, Y1 = 354700, 355000, 9249700, 9250140` (constante en `terreno_b.py`).
- Regla general: buscar la capa de curvas; la copia cuyos bloques/edificaciones caen sobre las curvas (y con coordenadas de
  magnitud UTM: E ~ 3.5e5, N ~ 9.25e6) es la que se usa. Las otras copias se ignoran.

### 2.3 Explotar bloques a coordenadas reales
- Las edificaciones vienen como bloques (INSERT) anidados. Se explotan con `virtual_entities()` de ezdxf hasta 6 niveles de
  profundidad, de modo que cada línea quede en coordenadas reales del modelo.
- Herramienta genérica del repositorio: `herramientas/explode.py <dxf> <pkl>`: recorre el espacio modelo; por cada INSERT
  (profundidad < 6) recorre sus entidades virtuales; guarda tuplas `(capa, tipo, puntos, texto, bloque)` para LWPOLYLINE,
  POLYLINE, LINE, TEXT, MTEXT, INSERT (con sus atributos `tag=texto`), CIRCLE, ARC y POINT.
- El script exacto que generó `base_sitio.pkl` **no quedó versionado**; su resultado sí. Estructura del pickle:

```
base_sitio.pkl = {
  "geo": { capa: [ (pts, cerrada, bloque), ... ] },   # pts = [(x, y, z), ...] en UTM; cerrada = bool; bloque = nombre o ''
  "txt": [ (capa, texto, x, y, z, bloque), ... ]      # 313 textos (NPT/NTN, nombres de ambientes, etc.)
}
```

### 2.4 Capas que se usan (base vigente, versión "ULTIMA VERSION") y para qué

| Capa en la base | N.° entidades | Uso |
|---|---|---|
| `C-TOPO` | 91 | curvas de nivel (175.0 a 188.5 cada 0.50 m); modelo de terreno |
| `2` | 70 | cerco perimétrico (se dibuja en la capa CERCO de la planta) |
| `0_PROYECCIONES 1` | 861 | proyección de coberturas (techos): áreas de techo y bloques de los cortes |
| `0_MUROS 1` | 195 | muros de los bloques: comprobación 10 (eje a ≥ 0.30 m del muro) |
| `MUROS-02`, `MURO DE CONTENCION` | 44 / 2 | base de la planta |
| `0_VEREDAS` | 909 | polilíneas cerradas de veredas: definen los tramos **tapados**; también pavimentos |
| `0.000. CIRCULACION - PLANTA`, `0_PISO NIVEL 01` | 348 / 29 | pavimentos (áreas libres de concreto) |
| `0_ CUNETAS`, `0_REJILLA#H` | 41 / 35 | planteamiento preliminar del usuario (ejes de la v1); caras de los patios 02 y 03 |
| `Area Verde` | 1734 | achurado de áreas verdes (referencia) |
| `MAGENTA_CUNETAS` | 30 | líneas magenta (capa 0, color magenta) trazadas por el usuario: lados con cuneta (v3) |
| otras (`0_TARRAJEO`, `0_COLUMNAS`, `0_BARANDA METALICA`, `SARDINEL`, `0_SARDINEL`, `tuberia des. fluvial ftt`, `VEREDA`) | — | se guardaron pero no intervienen en el cálculo |

Textos: los rótulos de nivel del plano tienen la forma `"NTN=+184.50 ... NPT=+0.15"`; la comprobación 7 los lee
(texto que contiene "NTN" y "NPT"; nivel = NTN + NPT relativo).

### 2.5 Las líneas magenta del usuario
- 20-10-2026 16:41: "ahora ya he trazado con unas líneas color magenta a los costados de cada edificación y por donde debería ir las
  cunetas, ya que todos los techos son a dos aguas y eso no habías considerado tú anteriormente... donde hay líneas magenta allí
  debería haber cunetas porque los techos son a dos aguas, así que reciben por ambos lados su canaleta".
- Se identificaron por **capa 0 y color magenta** (ACI 6) en la nueva versión del plano: 30 líneas rectas de 2 vértices,
  792.6 m en total. Se copiaron a `insumos/barranquita/cunetas_magenta_usuario.json`:
```
{"fuente": "PLANTA_GENERAL_590 ULTIMA VERSION.dxf - lineas magenta (capa 0) trazadas por el usuario: lados de edificaciones con cuneta",
 "lineas": [ [[x0, y0], [x1, y1]], ... 30 lineas ... ]}
```
- Los extremos de esas líneas son los nudos de la red (p. ej. `A0 = (354844.67, 9249873.87)` es el inicio de la línea 0).
  **No se mueve ni se junta ninguna**; solo se agregan las uniones necesarias hasta las descargas.

---

## 3. Modelo de terreno (TIN)

Archivo: `herramientas/barranquita/terreno_b.py`.

```
def curvas(G):
    para cada (pts, cerrada, bloque) en G["geo"]["C-TOPO"]:
        z = pts[0].z                                   # la curva es plana: su z es la del primer vértice
        si z > 100 y X0 < pts[0].x < X1 y Y0 < pts[0].y < Y1:   # descarta z = 0 (curvas sin elevación) y otras copias
            guardar (z, [(x, y) de cada vértice])

def modelo(G):
    P = todos los vértices de todas las curvas; Z = su cota
    f = scipy.interpolate.LinearNDInterpolator(P, Z)   # triangulación de Delaunay + interpolación lineal (TIN)
    devolver z(x, y) = float(f(x, y))                  # NaN fuera del casco convexo
```
- Curvas válidas: 175.0 a 188.5 m cada 0.50 m (28 cotas). En la base aparece también z = 0.0 (entidades sin elevación): se
  descartan con `z > 100`. Revisar siempre las cotas de las curvas (descartar z = 0 o etiquetas).
- Puntos fuera del TIN devuelven NaN; la comprobación 6 filtra con `np.isfinite`.
- Limitación conocida: en la hondonada de D2 (exterior norte) las curvas cada 0.50 m dejan el modelo plano en ~180.5; se
  pidió levantamiento de detalle (v2) y luego el usuario aclaró que el interior está nivelado (ver 12.5).
- Para los proyectos de Morales (colectores) el terreno venía en LandXML (`TOPO FINAL.xml`): `herramientas/parse_topo.py`
  (lee puntos `P`, caras `F`, `CgPoint` y alineamientos) y `herramientas/terreno.py` (`cargar_tin()` → `entregables/_calc/topo.pkl`,
  `interpolador(P, E0, E1, N0, N1)` con `LinearNDInterpolator` recortado a una ventana ±60 m del eje). Varones lo reusa en
  `herramientas/varones/terreno_v.py` (cota del terreno cada 0.50 m a lo largo del eje del colector).

---

## 4. Cerco perimétrico = límite de intervención

### 4.1 La regla (fija para todo proyecto)
- 20-10-2026 04:03, el usuario: "no podemos salir del área de intervención... las cunetas no pueden salir dibujadas, no se puede
  proyectar más allá de los cercos perimétricos... hasta ahí nomás se puede construir. No puede salir, pero sí pueden mandar el
  agua por esos lugares alrededor del cerco perimétrico".
- 04:05: "Antes que procedas a algo, delimita el cerco perimétrico según lo que tú ves y yo te confirmo, mándame una imagen".
  Se envió `entregables_barranquita/revision/CERCO_PERIMETRICO_PARA_CONFIRMAR.png`. 04:09: "Si todo está bien procede"
  (confirmación del usuario).
- Consecuencia: ninguna cuneta se dibuja ni se proyecta fuera del cerco; solo el **agua** sale, por un **pase en el cimiento del
  cerco**. Fuera del cerco, terreno natural de las curvas, sin obra (a lo sumo perfilar unos decímetros de tierra, y decirlo).

### 4.2 El polígono (22 vértices C1 a C22)
`diseno_b.CERCO_L` en coordenadas locales (sumar 354000 a x y 9249000 a y para UTM). Entre C11-C12 y C18-C19 el límite es la
fachada del ingreso secundario y del ingreso principal.

| Vértice | x local | y local | Vértice | x local | y local |
|---|---|---|---|---|---|
| C1 | 813.64 | 855.63 | C12 | 948.88 | 794.19 |
| C2 | 841.92 | 883.91 | C13 | 936.64 | 794.19 |
| C3 | 871.13 | 854.70 | C14 | 936.64 | 792.02 |
| C4 | 916.13 | 854.70 | C15 | 926.97 | 793.95 |
| C5 | 916.13 | 869.58 | C16 | 926.97 | 800.53 |
| C6 | 977.74 | 869.58 | C17 | 919.17 | 800.53 |
| C7 | 977.74 | 785.21 | C18 | 919.17 | 802.42 |
| C8 | 976.37 | 784.10 | C19 | 907.61 | 802.61 |
| C9 | 969.93 | 785.38 | C20 | 883.57 | 802.61 |
| C10 | 969.93 | 791.81 | C21 | 879.56 | 803.41 |
| C11 | 955.81 | 791.81 | C22 | 859.72 | 811.52 |

Perímetro 488.82 m; área del polígono 9,365 m² (la malla de 1 m² de la hidráulica cuenta 9,393 celdas).
En la v1 se usaba un cerco aproximado de 12 vértices leído a ojo; desde la v2 se usa este, confirmado.

### 4.3 Offset interior (cuneta perimetral)
- Eje de la cuneta perimetral a `D_CERCO = 0.60 m` del cerco (borde exterior a 0.30 m del cerco).
- `offset_cerco(d)`: desplaza cada lado del polígono `d` hacia adentro (normal interior según el signo del área) e
  intersecta lados consecutivos; `OC(k)` = vértice interior junto a Ck.

```
sg = signo(área con signo del polígono)               # +1 antihorario
para cada lado i (a = C[i], b = C[i+1]):
    u = (b - a)/|b - a|;  n = (-u.y*sg, u.x*sg)        # normal hacia adentro
    recta_i = (a + n*d, u)
para cada i: vértice_i = intersección(recta_{i-1}, recta_i)  (si son paralelas, el punto de la recta i)
```

### 4.4 Comprobación del límite (comprobación 11)
```
para cada ramal, para cada segmento a-b que NO termina en una descarga (el último, Dn -> D, es el pase y cruza el cerco):
    recorrer cada 0.25 m; en cada punto p tomar q = p ± 0.30 * normal (bordes exteriores de la cuneta)
    si algún q no está dentro del polígono CERCO -> punto fuera (NO CUMPLE)
```
Resultado vigente: "ningún borde de cuneta pasa el cerco; solo las 4 salidas lo atraviesan".

---

## 5. Niveles interiores

### 5.1 Valores vigentes (`diseno_b.py`)
```
NPT      = 184.65   # pisos y pasadizos
RASANTE  = 184.65   # borde superior de la cuneta, al ras del piso (junta asfáltica al mismo nivel, sin hueco)
NIVEL_AV = 184.60   # áreas verdes: 0.05 m bajo el borde
NIVEL_PATIO = RAS_PATIO = 184.50   # patio de maniobra y estacionamiento (NTN del plano) y cunetas al ras del patio
PATIO = rectángulo x 951.5..977.5, y 830.8..869.6 (locales) — entre la losa (y = 831.3), el cerco este, el cerco norte y x = 951.5
```
`rasante(x, y)`: si el punto está en PATIO → 184.50; si está dentro del CERCO → 184.65; si no → terreno natural z(x, y).

### 5.2 Cómo se llegó (cada indicación del usuario)
| Fecha y hora | Indicación | Efecto |
|---|---|---|
| 20-10 (v1) | sin niveles; rótulos NTN +184.50 en la plataforma | rasante = NTN 184.50 en la plataforma de bloques (`PLAT`, polígono de 16 vértices); dentro del cerco terreno de las curvas recortado a 184.50 (montículo de 185.5 cortado); fuera, terreno natural; la cuneta podía bajar con el terreno |
| 20-10 17:15 | "¿cuál hondonada? si todo el terreno está nivelado del cerco para adentro no debe haber ningún hueco" | se abandona la idea de hondonada interior |
| 20-10 17:22 | "todos los pisos y pasadizo... están en 184.65; ¿nivel de área verde debe estar al mismo nivel de cuneta terminada?" | se le pide criterio |
| 20-10 23:24 | "nivel de plantas todo es 184.65, las cunetas ponle en 184.60 y todo el área verde está a 184.55" | interior nivelado: NPT 184.65, borde 184.60, AV 184.55 |
| 20-10 23:31 | "donde es el patio de maniobras que quede así nomás con ese nivel, allí la cuneta se adapta" | patio en su NTN 184.50 |
| 20-10 23:33 | "no irá 5 cm abajo porque ya es hueco... eso debe ir al ras, ya sea tapada o con rejilla" | cunetas al ras del patio 184.50; D2 deja de ser poza (pase) |
| 21-10 00:59 | "la planta es 184.65, las cunetas van ahí también a 184.65, y el área verde iría a 184.60", para que encaje la junta asfáltica al mismo nivel del piso | **vigente**: borde 184.65, AV 184.60 |

### 5.3 Comprobación 7 (niveles)
- Toma la rasante de cada punto del perfil (cada 0.5 m) y su posición en planta.
- NO CUMPLE si algún borde queda sobre el NPT (> 184.655) o, dentro del PATIO, sobre 184.505.
- Lee los rótulos NTN/NPT del plano dentro del cerco y a < 5 m de una cuneta; los que difieren de 184.65 y de 184.50 se informan
  ("se toma +184.65 según el usuario"). Resultado: borde +184.65 en toda la red; al ras +184.50 en 292 puntos junto al patio.

---

## 6. Dónde va cuneta: regla de techos

- **Una cuneta bajo cada caída de techo.** Cada caída recibe su canaleta y montante, y la cuneta va debajo, a lo largo de ese lado.
- **Techo a dos aguas** (cumbrera en el eje largo del bloque): cuneta a **ambos lados** del bloque, una por cada alero.
- **Techo a una agua**: cuneta solo del **lado bajo**.
- 24-10-2026 00:32 el usuario lo resume: "depende de cuántas caídas tenga: si es dos caídas, un techo siempre va a tener una cuneta
  a su costado y otro lado hacia la caída".
- **Las líneas del usuario mandan**: si traza líneas (en Barranquita, magenta en capa 0), se copian a un JSON en `insumos/`, no se
  mueven ni se juntan, y se **quitan las cunetas que no tengan línea del usuario**. Solo se agregan uniones hasta las descargas.
- Error que motivó la v3: en la v1/v2 se había asumido que los aleros del lado norte de los pabellones oeste, del bloque norte y
  de la fila central descargaban al terreno (sin cuneta); el usuario señaló que todos los techos son a dos aguas y cada lado lleva
  cuneta.
- Memoria de arquitectura del colegio: techos a dos aguas con pendiente 46 a 57 %.

---

## 7. Construcción de la red

### 7.1 Estructuras (`diseno_b.py`)
```
N = { nombre_nudo: (x, y) UTM }           # extremos de líneas magenta + uniones + descargas
RAMALES = [ (codigo, sistema, [nudos en el sentido del flujo], descripcion), ... ]
SISTEMAS = {1: ("OESTE","D1"), 2: ("CENTRO Y FRENTE SUR","D3"), 3: ("NOR-ESTE Y LOSA","D2"), 4: ("NORTE","D4")}
DESCARGAS = {"D1": receptor, "D2": ..., "D3": ..., "D4": ...}
TAPADOS_FIJOS = [ (codigo, nudo_a, nudo_b, motivo), ... ]   # tapados que no salen de las veredas del plano
CONEXIONES   = [ (codigo, nudo_a, nudo_b), ... ]            # uniones nuevas: rasante en línea recta (relleno)
POZA = set()                                                # vigente: ninguna poza
DIR_SALIDA = {"D2": (-0.6, 0.8)}                             # dirección del agua afuera de D2 (fondo de la hondonada al nor-oeste)
```
- Un **ramal / eje** es una polilínea de nudos en el sentido del flujo. Empieza siempre con h = 0.30 m en su primer nudo
  (cabezal) y termina en una descarga o en un nudo intermedio de otro ramal (empalme).
- Un **nudo** puede ser: extremo de línea magenta, esquina, empalme (un ramal termina en un nudo interior de otro), unión nueva,
  `Dn` (punto a 0.60 m del cerco, por dentro, frente a la descarga) o `D` (la descarga en el cerco).
- Un **sistema** es el conjunto de ramales que llegan a la misma descarga (para colores y bloques en planta).
- Nombres de nudos en los planos: `P-01, P-02, ...` en el orden de aparición en los ramales; las descargas conservan D1..D4
  (`nombre` en diseno.json). Los nudos de chaflán (`X~a`, `X~b`) se numeran pero no se rotulan en planta salvo que sean empalmes.

### 7.2 Ramales vigentes (v3, 19 ejes)
Desde el 21-10-2026 00:26 los ramales se llaman EJE-01 a EJE-19 (antes R-xx), con la misma geometría y los mismos nudos.

| Eje | Sist. | Nudos (P-xx, tras chaflanes) | Descripción |
|---|---|---|---|
| EJE-01 | 1 | P-01 → P-02 → P-03 | Pabellón oeste A, lado nor-oeste; entrega al EJE-02 junto al cerco |
| EJE-02 | 1 | P-04 → ... → P-11 → P-03 → D1 | Pabellón oeste B lado nor-este; pabellón A lado sur-este; salida D1 |
| EJE-03 | 1 | P-12 → P-07 | Pabellón oeste B: lado sur-oeste (patio) |
| EJE-04 | 1 | P-13 → ... → P-19 → P-08 | Bloque D (lado norte) y pabellón C (lado nor-este) |
| EJE-05 | 1 | P-20 → ... → P-24 → P-10 | Bloque del ingreso (lado sur), bloque D (lado sur) y pabellón C (lado sur-oeste) |
| EJE-06 | 1 | P-25 → P-16 | Bloque del ingreso: lado norte, tramo oeste |
| EJE-07 | 2 | P-26 → ... → P-41 → D3 | Patio central, bajada al atrio de ingreso y salida D3 |
| EJE-08 | 2 | P-42 → P-43 → P-27 | Bloque del centro: lado sur |
| EJE-09 | 2 | P-44 → P-28 | Patio central |
| EJE-10 | 2 | P-43 → ... → P-47 → P-32 | Bloque del frente: lado norte |
| EJE-11 | 2 | P-48 → P-33 | Bloque del frente: lado sur |
| EJE-12 | 3 | P-49 → ... → P-60 → D2 | Losa: lados oeste, sur y este; unión por dentro del cerco a D2 |
| EJE-13 | 3 | P-61 → P-54 | Losa: lado norte |
| EJE-14 | 3 | P-62 → ... → P-68 → P-55 | Bloque nor-este: lado sur |
| EJE-15 | 3 | P-69 → ... → P-72 → P-56 | Bloque nor-este: lados oeste y norte |
| EJE-16 | 3 | P-73 → ... → P-78 → P-60 | Bloque norte: lado norte y unión a D2 por el norte de la planta de tratamiento |
| EJE-17 | 4 | P-79 → P-80 → P-81 → P-82 → D4 | Bloque norte: lado sur y salida D4 |
| EJE-18 | 4 | P-42 → P-83 → ... → P-86 → P-81 | Bloque del centro: lados este y norte, tramo este |
| EJE-19 | 4 | P-87 → P-88 → P-86 | Bloque del centro: lado norte, tramo oeste |

Observaciones de la topología: EJE-08 y EJE-18 nacen en el mismo nudo (P-42, divisoria: el agua se reparte a dos sistemas);
EJE-10 nace en P-43, que es un nudo intermedio del EJE-08.

Uniones nuevas (no son lados de edificación): `CONEXIONES` = EJE-04 X885b→N885, EJE-05 T29w→T7e y T7w→T4s, EJE-02 W1b→D1n,
EJE-14 X971a→Q0, EJE-15 X971b→Q1 (en la v1 la rasante de estas uniones iba en línea recta entre extremos = relleno compactado;
con el interior nivelado la recta queda horizontal).

### 7.3 Descargas y cómo se eligen con las curvas
Criterios (skill y bitácora):
- El agua va a los **puntos bajos que muestran las curvas**; agrupar la red en sistemas, cada uno con su descarga en el cerco, del
  lado más bajo (calle, quebrada, talud).
- **No cruzar franjas altas** para llegar a una descarga: si la profundidad se dispara, mandar el ramal a otra descarga.
- Todo por **gravedad**, sin bombeo ni contrapendiente; ninguna cuneta "enterrada" sin salida.
- En cada descarga el **terreno exterior debe quedar bajo la cota de fondo de salida** a pocos metros (no excavar afuera).
- Sin pozas salvo que no haya otra salida. Si la salida da a un talud o quebrada, recomendar protección contra erosión
  (recomendación, no obra metrada fuera del cerco).

Ubicación geométrica (vigente):
```
D1  = pie de la perpendicular desde A1 (fin de la línea magenta 0) sobre el lado C22-C1 del cerco (x local ≈ 820.1)
D1n = D1 + 0.60 * unitario(A1 - D1)                    # punto interior a 0.60 m del cerco
D3  = punto del lado C14-C15 con x = 354935.50 (junto a C14)
D3n = D3 + 0.60 * normal interior del lado C14-C15
D4  = punto del lado C3-C4 (y = 854.70) con x = 354911.00 (entre el bloque norte y el bloque del centro)
D4n = D4 - (0, 0.60)
D2  = (965.50, 869.58) en el cerco norte; D2n = (965.50, 869.58 - 0.60)
```

| Descarga | Lado del cerco | Receptor | Por qué ahí |
|---|---|---|---|
| D1 | sur-oeste, C22-C1, x = 820.1 | talud natural que baja a la quebrada del oeste | frente al extremo de la línea 0; el talud exterior cae rápido |
| D2 | norte, x = 965.5 | terreno exterior que baja a la quebrada del norte (hondonada natural) | esquina nor-este, la más baja del lado este/norte; afuera el terreno baja ~3.2 m en talud |
| D3 | sur, junto a C14, x = 935.5 | terreno exterior que baja al Jr. Alfonso Ugarte (183.00) | frente sur, hacia la calle |
| D4 | norte, C3-C4, x = 911.0 | talud natural de la quebrada del norte | entre el bloque norte y el del centro, sobre el talud |

Decisiones de ruta con las curvas (v3, 20-10-2026): el lado oeste y sur de la losa iba primero a D3, pero cruzaba una franja
natural a 183.5 delante del frente (h = 1.33 m y D3 sin salida): se mandó por el lado este de la losa a D2. En la v1, D3 quedaba
7 cm bajo la calle y el último tramo del frente no tenía capacidad: D3 se movió al punto bajo del frente (x = 925.0, rasante 183.25,
C.F. 182.99 = calle 183.00) y el frente se partió en dos ramales.

### 7.4 Tramos tapados
```
tapado(p) = p dentro de alguna polilínea CERRADA de 0_VEREDAS (con > 3 vértices y dentro de la ventana del sitio)
            o p dentro de un intervalo de TAPADOS_FIJOS
TAPADOS_FIJOS (vigente):
  EJE-07  X919b -> D3   "Atrio del ingreso principal y paso por el cerco"
  EJE-12  Q2    -> D2   "Patio pavimentado del nor-este y paso por el cerco"
  EJE-02  D1n   -> D1   "Paso por el cerco"
  EJE-17  D4n   -> D4   "Paso por el cerco"
```
- Regla: tapado (losa) donde la cuneta **cruza veredas, ingresos o pasadizos** y en el pase del cerco; el resto **abierto con rejilla**.
- Intervalos tapados del perfil: tramos consecutivos de puntos tapados de más de 0.40 m (`tapados` en diseno.json).
- Vigente: EJE-02 [75.28, 76.04]; EJE-07 [71.79, 94.69]; EJE-11 [19.41, 19.91]; EJE-12 [103.16, 118.38]; EJE-17 [8.95, 12.93] y
  [39.38, 39.98]. Total 43.96 m tapados.

---

## 8. Chaflanes a 45° en planta

### 8.1 Indicación del usuario (21-10-2026)
- 01:15: "Recuerda usar quiebres de 45 siempre, no sé a qué te refieres cuando dices nudos, siempre es quiebres de 45".
- 01:19: "en el perfil longitudinal no vas a mostrar los quiebres... En la vista en planta sí va a haber quiebres. Donde ves que hay
  de 90, tú al quiebre de 45, trata por favor de hacerlo así, porque si no va a haber resalto hidráulico".
- Por qué: en una esquina de 90° el agua choca de frente contra el muro (resalto); con dos quiebres de 45° el cambio de dirección
  se reparte.

### 8.2 Algoritmo (`diseno_b.chaflanes()`, se ejecuta al importar el módulo)
```
CHAFLAN = 0.60; ANG_CHAFLAN = 50.0
giro(a, b, c) = ángulo entre (b - a) y (c - b), en grados (0 = sigue recto, 90 = esquina en L)
para cada ramal, para cada nudo interior X (con anterior a y siguiente c):
    g = giro(a, X, c); si g < 50: seguir
    u = unit(a -> X), Lin = |X - a|;  v = unit(X -> c), Lout = |c - X|
    ch = min(0.60, 0.5*Lin, 0.5*Lout)              # nunca más de la mitad del tramo vecino
    X~a = X - u*ch;  X~b = X + v*ch                # se reemplaza X por [X~a, X~b] (tramo en diagonal)
    para cada otro ramal que TERMINA en X (empalme en la esquina):
        si giro(su penúltimo, X, c) >= 50:
            chq = min(0.60, 0.5*|su último tramo|, ch); X~<eje> = X - w*chq
            su final pasa a [X~<eje>, X~b]         # entra en diagonal al inicio del tramo de salida (unión en Y)
        si no: su final pasa a [X~b]
    TAPADOS_FIJOS y CONEXIONES se renombran: inicio -> X~a, fin -> X~b
```
- Resultado vigente: 22 esquinas ochavadas (la mayoría de 90°, algunas de 78-113°); chaflán 0.60 salvo donde el tramo es corto
  (0.30 en D1n, D3n y D2n; 0.56 en X952c; 0.25 en J4).
- En los **perfiles** y en la **numeración de secciones** los nudos con "~" no aparecen (de 96 secciones se pasó a 69).

---

## 9. Cálculo de cotas de fondo

### 9.1 Constantes
```
B_INT, E_MURO, B_TOT = 0.40, 0.10, 0.60
H0, HMIN, S0 = 0.30, 0.25, 0.005
E_TAPA = 0.10            # losa de los tramos tapados: la altura libre bajo la losa no baja de HMIN
H_ACERO = 0.40
N_MAN, BL = 0.013, 0.05  # Manning para Q_cap informativo y borde libre
```

### 9.2 Muestreo
```
para cada ramal:
    pts = []
    para cada segmento i (a = N[nudo_i], b = N[nudo_i+1]):
        n = max(1, ceil(L/0.5))
        k = 0..n-1 (y n en el último segmento): t = k/n; punto = a + t(b - a)
        etiqueta = nudo_i si k == 0; nudo_i+1 si k == n; None si no
    s = progresiva acumulada (distancia en planta)
    r[i] = rasante(x_i, y_i)                          # 184.65 / 184.50 / terreno
    CONEXIONES del ramal: r lineal entre r(nudo_a) y r(nudo_b)
    si el ramal termina en una descarga: r[i] = r[idx(Dn)] para todo i después de Dn   # pase: la cuneta llega al cerco con su mismo borde
    tap[i] = tapado(pts[i])
```

### 9.3 Fondo con empalmes (iteración hasta 50 vueltas)
```
req = {}                                    # cota de fondo máxima admisible en un nudo, impuesta por los ramales que llegan
repetir:
    para cada ramal:
        hm[i] = max(HMIN, hreq(tramo del punto)) + (0.10 si tap[i])   # profundidad mínima total en el punto
        f[0] = r[0] - H0 - (0.10 si tap[0])                            # arranque: altura 0.30 (libre) bajo el borde
        f[i] = min( f[i-1] - S0*(s[i]-s[i-1]),  r[i] - hm[i] )         # baja al 0.5 % o más si la rasante lo exige
        si pts[i] es nudo y está en req: f[i] = min(f[i], req[nudo])
        # sin escalón: si en un nudo k1 con req el fondo cae más de 1.5 veces lo que daría S0 respecto al punto anterior,
        # el fondo baja parejo (línea recta) desde el nudo anterior k0:
        para nudos consecutivos k0, k1 con nudo(k1) en req y f[k1] < f[k1-1] - 1.5*S0*ds:
            f[i] = min(f[i], f[k0] + (f[k1]-f[k0])*(s[i]-s[k0])/(s[k1]-s[k0]))   para k0 < i < k1
    para cada ramal que termina en un nudo `fin` interior de otro ramal c2:
        v = fondo(ramal)[último];  si fondo(c2)[en fin] > v + 1e-6:
            req[fin] = min(req.get(fin, inf), v); cambio = True    # el que recibe debe quedar a la misma cota o más abajo
hasta que no haya cambio
```
Por qué: "la cuneta que llega lo hace a la misma cota o por encima de la que recibe (no remansa)". Si la que recibe está más alta,
se la obliga a bajar en ese nudo, y para que no quede un escalón se baja parejo desde su nudo anterior. Un ramal puede **entregar
con caída** a otro más profundo (ejemplo: EJE-01 entrega al EJE-02 con caída de 0.42 m en P-03).

### 9.4 Reglas que salieron de correcciones
- **Pase sin "achicar"** (21-10 00:59): antes la cuneta tomaba el terreno exterior al llegar al cerco y se reducía (una sección de
  0.15 m, tapada: "¿cómo vas a poner 15 centímetros ahí? Eso es imposible... ahí se obstruye el flujo"). Ahora la rasante se
  mantiene desde Dn hasta el cerco.
- **Tapados con altura libre**: la profundidad mínima suma la losa de 0.10 m (altura libre ≥ 0.25 m bajo la losa); la capacidad se
  calcula con la altura libre bajo la losa.
- **Quiebre raro del EJE-01** ("en el eje 1 del pabellón oeste, en los 34.64 m, hay un quiebre medio raro... la cuneta así bien
  chiquitita"): el EJE-01 bajaba 20 % en 2 m para entrar al EJE-02. Ahora el EJE-02 sigue hasta D1 por el pase y el EJE-01 le
  entrega con caída de 0.42 m.
- **Velocidad > 3.0 m/s → gradas** (escalones de concreto cada 0.50 m en planta). En la v1 hubo 6 tramos con gradas, en la v2/v3
  tres (R-01 al pase D1, R-12 al norte de la losa, R-15 x = 971.7). Con el interior nivelado (pendiente máx. 2.92 %) no queda
  ninguna grada (V máx. 1.98 m/s).

### 9.5 Ciclo diseño ↔ verificación (`calcula_b.py`)
```
borrar hmin_req.json
para it en 1..8:
    diseno_b.main()      # cotas con las profundidades mínimas de hmin_req.json
    verifica_b.main()    # en la comprobación 8, cada tramo sin borde libre escribe hreq["EJE|nudo_de|nudo_a"] = y + 0.05 + 0.005
    si hmin_req.json no cambió: terminar
```
Regla del usuario: si no cumple, **primero profundizar el tramo**; no cambiar la sección acordada (21-10 13:11: "mantén la cuneta
0.40 interior 0.60 total"). Vigente: `hmin_req.json = {}` (ningún tramo necesitó más profundidad; la geometría no depende de la lluvia).

### 9.6 Salida por tramo (diseno.json)
```
L = s[i1]-s[i0]; L_tapado = suma de sub-tramos con ambos extremos tapados; L_rejilla = L - L_tapado
S = (cf_de - cf_a)/L; h_de = ras_de - cf_de; h_a = ras_a - cf_a; h_max = max(r - f) en el tramo
Q_cap = Manning(n 0.013) con y = min(h_de, h_a) - (0.10 si hay tapado) - 0.05 y S = max(S, 0.005)
```

---

## 10. Tapas de inspección

- 21-10-2026 12:23 el usuario pide dibujar "si es posible, no sé cada cuántos metros, tapas de inspección en las cunetas tapadas".
  Criterio propuesto (el usuario no fijó distancia): **al inicio y al final de cada tramo tapado, en cada empalme y a 10 m como máximo**.
- Tapa 0.60 x 0.60 (concreto removible, con dos asas), ancho total de la cuneta. Archivo `planta_cunetas_b.py`, función `_tapas`.

```
TAPA = 0.60; MAX_TAPAS = 10.0; EM = 0.10; BT = 0.30
para cada eje, para cada intervalo tapado [a, b] (progresivas sobre el eje dibujado):
    a2 = a (o 0.10 si el tapado empieza en el cabezal)
    si b llega al final del eje:
        b2 = L - (0.075 + 0.15 + 0.30)  si el eje termina en descarga (lejos del cerco)
        b2 = L - (0.30 + 0.30)          si entrega a otra cuneta (lejos de la que recibe)
    si no: b2 = b
    i0 = a2 + 0.30 + 0.10;  i1 = b2 - 0.30 - 0.10
    si i1 < i0: una tapa al centro si b2 - a2 >= 0.70; si no, ninguna
    si no: n = max(1, ceil((i1 - i0)/10)); tapas en i0 + (i1 - i0)*k/n, k = 0..n   (o una al centro si i1 - i0 <= 0.5)
para cada empalme dentro de un tramo tapado: tapa en el empalme si no hay otra a menos de 2.0 m
```
- El eje que termina en una descarga se prolonga 0.075 m hasta la cara exterior del cerco (`eje_pts`).
- Vigente: 10 tapas (`_calc/tapas.json`): EJE-02 0+075.74; EJE-07 0+072.19, 0+079.41, 0+086.62, 0+093.84; EJE-12 0+103.56,
  0+110.54, 0+117.53; EJE-17 0+009.35, 0+012.53. Hoja "TAPAS INSPECCION" del Excel. El metrado descuenta 0.60 x 0.60 x 0.10
  de losa por tapa.

---

## 11. Acero según h

- 21-10-2026 00:59, el usuario: "en varias cunetas de 30 estás considerando acero. El acero se considera a partir de 40, cuando el
  fondo es 40 o más... desde arriba, desde la rejilla hasta abajo, 40. Si es más de 40 o a partir de 40 ya lleva acero. Antes no; si
  hay cunetas de 30, de 36, no llevan acero, salvo... si hay tapadas, sí".
- Regla: `con_acero = tapado or h >= 0.40` (h = del borde/rejilla al fondo interior). Menor: concreto simple
  (llamada "CONCRETO SIMPLE / SIN ACERO (h < 0.40)" en la sección).
- Vigente: de las 69 secciones, 29 sin acero; 12 tapadas.
- Armado dibujado (1/20): U de 3/8" @0.25 (transversal), longitudinales 3/8" @0.20 en abiertas y @0.22 en tapadas; en tapada el
  estribo cierra por la losa y lleva una barra central arriba; recubrimiento de dibujo 0.045.
- Metrado (`cantidades_b.py`): acero solo en la longitud con h ≥ 0.40 o tapada; U de desarrollo `2(h + 0.10 - 2·0.04) + (0.60 - 2·0.04) + 2·0.10`
  @0.25; longitudinales `2(ceil(h/0.20) + 1) + (ceil(0.52/0.20) + 1)` barras; losa tapa con transversales @0.20 de
  (0.60 - 0.08 + 0.20) y 3 barras longitudinales; 0.56 kg/m (3/8").
- Mismo criterio que en los CAR (4-10-2026, ver sección 16), donde la altura se mide desde el NCT en abierta y en tapada.

---

## 12. Hidráulica por tramo (comprobaciones 8 y 9)

### 12.1 Áreas de aporte (malla de 1 m²)
```
celdas = centros (x + 0.5, y + 0.5) de una malla de 1 m entre x 354805..354985 e y 9249775..9249890, solo dentro del CERCO
segmentos = cada tramo (recta de nudo a nudo) de cada ramal
cada celda se asigna al segmento más cercano  (techos a dos aguas: cada mitad cae naturalmente al alero de su lado)
C de la celda según la superficie en que cae (hidrologia_b.superficies):
    techo 0.88 | pavimento (áreas libres de concreto) 0.88 | estacionamiento / patio de maniobra 0.88 | verde (el resto) 0.40
area[tramo] = n.° de celdas; areaC[tramo] = suma de C
acumulado(ramal): recorre sus tramos; en el tramo j > 0 suma el acumulado final de cada ramal que termina en el nudo inicial del tramo
```
Superficies (`hidrologia_b.superficies`, shapely): techos = caras de `0_PROYECCIONES 1` + patio cívico techado + losa multiusos
techada; pavimentos = `0_VEREDAS`, `0.000. CIRCULACION - PLANTA`, `0_PISO NIVEL 01`, patio 04 y las caras de `0_ CUNETAS` de los
patios 02 y 03; estacionamiento = PATIO menos la losa del área de tratamiento; verde = el resto dentro del cerco.
Vigente (celdas): techo 5,548, pavimento 901, estacionamiento 623, verde 2,321; total 9,393 m²; **C ponderado 0.761**.

### 12.2 Caudal, tirante y velocidad
```
Q = I * sum(C·A) / 3.6e6 * FS            # I en mm/h, A en m2, FS = 1.15  (Q en m3/s)
S = max(S_tramo, 0.005)
y  = tirante normal Manning, n = 0.015 (bisección 1e-4..3.0 m, 100 iteraciones), canal rectangular b = 0.40
yv = tirante normal con n = 0.013;  V = Q / (0.40 * yv)              # velocidad máxima probable (n bajo = más rápido)
h_disp = min(h_de, h_a) - (0.10 si el tramo tiene parte tapada)     # altura libre disponible
cap CUMPLE si h_disp - y >= 0.05 - 0.001
vel CUMPLE si V <= 3.0 (si no: "GRADAS")
si no cumple capacidad: hreq[tramo] = max(y + 0.05 + 0.005, anterior)   -> ciclo de calcula_b
```
- Por qué dos n: capacidad con n = 0.015 (conservador, más tirante) y velocidad con n = 0.013 (conservador, más velocidad).
- Lluvia vigente (`hidrologia_b.resultados()`): estación Pongo de Caynarachi (SENAMHI 003317), serie 1989-2013, Log Pearson III,
  T = 25 años: P24 = 169.27 mm, P10 = 48.86 mm, tc = 10 min, I = 293.18 mm/h (Dick-Peschke). El detalle de la hidrología es otro
  tema de la base de conocimiento.
- `verifica_b.py --solo-lluvia`: sin la base del sitio, rehace 8 y 9 con Q nuevo = Q anterior x I nuevo / I anterior; exige
  `hmin_req.json` vacío.

### 12.3 Evolución del caudal de verificación
| Momento | I y C | Nota |
|---|---|---|
| v1 (20-10) | C 0.80, I 211 mm/h (tc 10 min, estación del Refugio, referencial) | 9 de 10 |
| 21-10 (Tarapoto transpuesta x 1.90) | I 400.96 mm/h, C 0.57, sin FS | 91 tramos cumplen sin cambiar profundidades (Q máx. 227.3 l/s) |
| 21-10 (superficies medidas, FS 1.15) | C 0.761 | Q máx. 225.7 l/s, borde libre mín. 0.129, V máx. 1.97 |
| vigente | I 293.18 mm/h (LP3), C 0.761, FS 1.15 | Q máx. 229.2 l/s, borde libre mín. 0.128 m, V máx. 1.98 m/s |

---

## 13. Las 11 comprobaciones (`verifica_b.py`) con su criterio exacto

| N.° | Comprobación | Criterio exacto en el código | Resultado vigente |
|---|---|---|---|
| 1 | Conectividad | todo ramal termina en una descarga o en un nudo interior de otro ramal que llega a una descarga (cierre iterativo) | 19 ramales: EJE-01..06 → D1; 07..11 → D3; 12..16 → D2; 17..19 → D4 |
| 2 | Sin contrapendiente | en el perfil cada 0.50 m, `f[i] <= f[i-1] + 1e-6` | la cota de fondo baja en todos los puntos |
| 3 | Pendiente mínima | min S de tramos `>= 0.005 - 1e-4` | mín. 0.50 % (EJE-01 P-01-P-02); máx. 2.92 % |
| 4 | Profundidades | h al inicio de cada ramal `>= 0.30 - 1e-3` y altura libre (h - 0.10 en tapados) `>= 0.25 - 1e-3` en todo punto | inicio 0.30; libre mín. 0.25 (EJE-17); h máx. 0.91 (EJE-07, prog. 94.7) |
| 5 | Empalmes | `cf_llega - cf_recibe >= -0.005` en el nudo de entrega | 15 empalmes; caída máx. 0.42 m (EJE-01 en P-03) |
| 6 | Descargas por el cerco | dirección = prolongación del último tramo (o DIR_SALIDA); terreno exterior muestreado cada 0.25 m hasta 15 m; pase: `sobre = max(z - cf)` en el primer metro (perfilado) y `sale_a` = primera distancia con `z <= cf - 0.05`; cumple si `sale_a <= 2.0 m`. Poza (ya no se usa): rebalse al nivel interior junto al cerco, el terreno no sube más de 0.05 en 2 m y baja 0.25 m | D1 C.F. 183.759 a 0.5 m; D2 183.758 a 0.2 m; D3 183.736 a 0.5 m; D4 184.145 a 0.5 m |
| 7 | Niveles | ningún borde sobre el NPT +184.65 (ni sobre +184.50 en el patio); rótulos del plano informados | borde +184.65; al ras +184.50 en 292 puntos |
| 8 | Capacidad | `h_disp - y >= 0.05` con n 0.015 | I 293, C 0.76, A 9,393 m²; borde libre mín. 0.128 m (EJE-11 P-48-P-33, Q 19.1 l/s, y 0.072, h 0.20) |
| 9 | Velocidad | `V <= 3.0 m/s` con n 0.013 (CE.040, concreto); si no, gradas | V máx. 1.98 m/s |
| 10 | Muros | distancia eje-muro (`0_MUROS 1`) `>= 0.30` en cada punto del perfil | mín. 1.22 m en 1,986 puntos |
| 11 | Dentro del cerco | bordes eje ± 0.30 cada 0.25 m dentro del polígono, salvo el tramo Dn → D | ningún borde pasa el cerco |

Nota sobre la 8: en EJE-11 el tramo tiene 0.50 m tapados, así que el código toma `h_disp = 0.30 - 0.10 = 0.20` (conservador,
porque en el punto tapado la profundidad real es ≥ 0.35).

Historia de la lista: el 20-10 03:27 el usuario pidió "revísalo unas 10 veces... dime si ninguna queda tapada bajo la tierra, que
todas tengan descarga por gravedad". Se hicieron 10 comprobaciones (v1: 9 de 10); en la v2 se agregó la 11 (límite del cerco) y
se corrigió un fallo: R-11 terminaba en el nudo previo a D3 y se tomaba como descarga (su empalme no se revisaba); desde
entonces solo cuentan como descargas las de `DESCARGAS`.

---

## 14. Evolución v1 → v2 → v3 → vigente (cada corrección del usuario)

### v1 — 20-10-2026 (03:01)
- Red sobre los ejes del planteamiento del usuario (capas `0_ CUNETAS` y `0_REJILLA`): 22 ramales R-01..R-22, 894.6 m
  (836.1 con rejilla, 58.6 tapados), 4 sistemas, descargas D1 (esquina oeste), D2 (perimetral este, y = 860.5, cabecera de la
  quebrada), D3 (frente sur, ingreso), D4 (ingreso sur-este, exterior). Profundidad máx. 0.83 m.
- Rasante: NTN +184.50 en la plataforma; terreno de las curvas dentro del cerco recortado a 184.50; terreno natural fuera;
  cerco aproximado de 12 vértices; perimetrales sobre el cerco.
- Pendientes: receptores de D3 y D4, CUI, caudales; aleros sin cuneta al terreno.

### v1.1 — 20-10-2026 (04:02): "revísalo unas 10 veces"
- `verifica_b.py` con 10 comprobaciones. D3 7 cm bajo la calle y sin capacidad al final del frente → D3 al punto bajo (x = 925.0,
  C.F. 182.99 = Jr. Alfonso Ugarte 183.00); frente partido en R-07 (oeste) y R-23 (este); bajada R-08 directa a D3; 6 tramos con
  gradas. 9 de 10. Planta en bloques de AutoCAD por sector; isométricos y cortes. Se halló que `dxf_base.iso` proyectaba en espejo
  (corregido solo en `iso_b.py`).

### v2 — 20-10-2026 (05:09): todo dentro del cerco
- Usuario 04:03: no salir del cerco; 3D "solo de todas las cunetas, con todo el terreno, todas las veredas". 04:05-04:09: cerco
  delimitado en imagen y confirmado.
- Perimetrales a 0.60 m por dentro; eliminado el sistema 4 (R-21 fuera del cerco): 19 ramales, 825.6 m (756.1 rejilla, 69.6
  tapados), 3 sistemas (1 oeste → D1, 2 frente sur → D3, 3 nor-este → D2).
- D1 (C22-C1, x = 820.7) y D3 (junto a C14, x = 935.5) con pase en el cimiento (terreno exterior bajo la C.F. a 1.0 y 2.0 m);
  D2 (cerco norte, x = 965.5) con **poza 0.80 x 0.80** que rebalsa a 180.62 hacia la hondonada.
- Nace `calcula_b.py` y la comprobación 11. Gradas en R-01, R-12 y R-15.

### v3 — 20-10-2026 (17:13): líneas magenta
- Nuevo DXF (3 partes) y 30 líneas magenta. 19 ramales, 973.3 m (44.5 tapados), 4 sistemas: 1 oeste → D1 (339.7 m), 2 centro y
  frente sur → D3 (239.4 m), 3 nor-este y losa → D2 (301.1 m), 4 norte → D4 (93.1 m, nueva).
- Se quitaron las cunetas sin línea magenta: perimetral sur-oeste, bajada x = 937.3, y = 838.8, x = 971.7 y el inicio de la
  perimetral este.
- D1 se movió frente al extremo de la línea 0 (x = 820.1); D4 nueva (cerco norte C3-C4, x = 911.0). Pase en D1, D3 y D4 (terreno
  exterior bajo la C.F. a 0.8, 1.8 y 0.8 m); poza en D2. Losa oeste/sur → D2 (no D3). 11 de 11; h máx. 0.85 m (R-07).
- 17:15 el usuario no entendió "hondonada" ni "perfilar 0.8/1.8 m" y pidió todo en español: el interior está nivelado.

### Niveles — 21-10-2026 (00:02)
- NPT 184.65, borde 184.60, AV 184.55; patio 184.50 al ras; D2 pase (sin poza). 11 de 11; h máx. 0.92 (R-07); C.F. de salida
  D1 183.660, D2 183.704, D3 183.576, D4 184.099. Recomendación pendiente: rejilla de tránsito vehicular en el patio.

### Perfiles por eje — 21-10-2026 (00:26)
- Usuario 00:10: perfiles "tal cual" su estilo, cunetas divididas por ejes y dónde se interconectan; "dónde está tapado, solamente
  quiero que se vean los cortes"; 00:11: "hazlo ordenado, no alteres o mezcles líneas".
- R-xx → EJE-01..EJE-19; 96 secciones con su corte 1/20 (ver sección 15).

### Al ras, pases y acero — 21-10-2026 (01:10)
- Borde = NPT 184.65, AV 184.60; pase sin achicar; tapados con altura libre; EJE-01 entrega con caída; fondo parejo en empalmes;
  pendiente máx. 2.93 %, V máx. 1.84, sin gradas; acero solo h ≥ 0.40 o tapada (36 de 96 secciones sin acero).

### Quiebres a 45° y detalle por descarga — 21-10-2026 (01:41)
- Chaflanes (22 esquinas, 69 secciones). Las cuatro descargas por pase en el cimiento: D1 183.759, D2 183.758 (afuera el terreno baja
  ~3.2 m en talud: proteger la entrega contra erosión), D3 183.736, D4 184.145 (perfilar ~0.10 m en los primeros 0.5 m afuera).
- `descargas_b.py`: una lámina por descarga (planta, perfil longitudinal e isométrico de esa esquina).

### Escala real y estilo de planta — 21-10-2026 (mañana)
- 12:12: "¿por qué mide 0.30 si el ancho total es 0.60?": la planta e isométrico de las descargas estaban a la mitad (1/50 en una
  lámina 1/25). Ahora toda la lámina de descarga es 1/25 real: planta últimos 4.0 m, isométrico últimos 3.0 m + 1.75 m de terreno
  exterior; perfil 6.0 m de cuneta + 2.5 m de terreno exterior.
- 12:23: "ya no quiero la vista 3D o isométrico de todo el terreno, bórralo"; planta con rejilla o tapada como en sus capturas
  (tapada todo en líneas verdes); tapas de inspección.
- 12:25: "no pongas eso de bloque X y tal número, se ve feo; solo pon nombre del eje y sus progresivas; lo de pabellón conserva".
- 12:28: "¿por qué dice 31.45?": la fila Longitud mostraba la parte del tramo dentro de una pieza de perfil; ahora siempre la
  medida completa de sección a sección (35.59 de S-07 a S-08 del EJE-04).
- Láminas finales: DC-00 índice, DC-01 planta 1/250, DC-02 cuadro y secciones típicas 1/5, DC-03 a DC-11 perfiles 1/50, DC-12 a
  DC-14 secciones 1/20, DC-15 cortes generales 1/250, DC-16 a DC-19 detalle de descargas D1 a D4 (INDICADA, 1/25).

### Expediente — 21-10-2026 (tarde)
- Sección intocable ("mantén la cuneta 0.40 interior 0.60 total"); planos impresos (no se regeneran). Los DC-16 a DC-19 rotulan
  "AGUA DE DISEÑO" con caudales anteriores (207.7 / 264.7 / 174.2 / 48.4 l/s); con la lluvia y superficies vigentes son los de la
  tabla 17.3 (pendiente de decisión del usuario).

---

## 15. Secciones y perfiles (datos que salen del diseño)

### 15.1 Dónde se pone sección (`perfiles_b.secciones`)
```
candidatas por eje:
  - inicio del eje ("Inicio del eje") y fin ("Descarga Dn" o "Entrega a EJE-yy; caída x.xx m" si caída > 0.02)
  - cada nudo donde llega otro eje ("Llega EJE-xx")
  - quiebre en planta SOLO si cambia la pendiente del fondo (|Sa - Sb| >= 0.0005) y no es nudo "~"
  - inicio y fin de cada tramo tapado (si están a > 0.20 m de los extremos)
  - cambio de borde (salto de rasante > 0.02 entre puntos: patio de maniobra)
ordenar por progresiva; juntar las que distan < 0.25 m (gana la de mayor prioridad: nudo 3 > tapado 2 > borde 1; se unen notas)
numerar correlativo en el orden de los ejes: SECCION 01, 02, ...
```
Vigente: 69 secciones (`_calc/secciones.json`: `n, s, nct, ncf, h, tap, nota, eje`).

### 15.2 Estilo de perfiles (lo pidió el usuario, con sus láminas del CAR Mujeres como modelo)
- Un perfil por eje, H = V = 1/50; NCT azul en abierto, verde en tapado (cara superior e inferior de la losa); NCF magenta (cara
  superior e inferior de la losa de fondo 0.10); línea roja vertical en cada sección.
- Líneas de referencia "Altura relativa al NPT (m)" cada 0.15 m (0.00 = NPT +184.65).
- Recuadro sobre cada sección: SECCION nn, NCT, NCF, H, EL (0.10), EM (0.10) y conexión ("Llega EJE-xx", "Entrega a EJE-yy",
  "Descarga Dn"); filas de recuadros sin traslape (hasta 4 filas).
- Guitarra: Progresiva (m), Etiqueta, Longitud (m), Pendiente (%); progresivas cada 5 m (`0+xxx.xx`).
- Ejes largos partidos en piezas iguales que entran en franjas de 800 mm de papel.
- Sección 1/20: piso adyacente con junta asfáltica de 1" al mismo nivel del borde; rejilla móvil de platinas 1" x 3/16" sobre
  ángulos en abiertas; losa 0.10 en tapadas; cotas 0.10 / 0.40 / 0.10 / 0.60, EL y H.

### 15.3 Planta (`planta_cunetas_b.py`, estilo de las capturas del usuario)
- Rejilla: bordes exterior 0.60 e interior 0.40 en celeste (capa CUN-REJ-BORDE, RGB 0,170,230) y platinas cada 0.10 m
  (CUN-REJ-PLATINA); tapada: bordes en verde (CUN-TAP-BORDE, RGB 0,150,0); flechas rojas cada 5 m y en cada quiebre (CUN-FLUJO);
  tapas en azul (CUN-TAPA-INSP). Contornos unidos por sistema con shapely (buffer con esquinas en inglete) para empalmes limpios;
  el cabezal arranca con muro de 0.10; la que llega no repite platinas dentro de la que recibe.
- Gradas (si las hubiera): trazos transversales cada 0.50 m.
- DC-01 en bloques de AutoCAD: ARQUITECTURA_BASE, CURVAS_DE_NIVEL (cota rotulada en las de metro entero), LIMITE_DE_INTERVENCION,
  CUNETAS_SISTEMA_n_..., ROTULOS_RED.

### 15.4 Detalle de cada descarga (`descargas_b.py`) y cortes (`cortes_b.py`)
- Lámina por descarga a 1/25: planta (eje que sale con quiebres, ejes que llegan, rejilla, tapado, pase bajo el cerco, curvas
  exteriores, flecha), perfil longitudinal (losa de fondo, NCT, losa tapa, agua de diseño, muro del cerco cortado 0.15 sobre el pase,
  cimiento corrido "dimensiones según estructuras", terreno natural exterior y perfilado "sin obra"), isométrico de esa esquina con
  caras ocultas eliminadas. Capas DET-* e ISOD-*.
- Cortes generales E-E (norte-sur) y F-F (oeste-este) 1/250 H = V: terreno natural, interior nivelado, bloques con alero a 3.00 m
  sobre el NPT y cumbrera 1.10 m más, cada cuneta cortada con su cota de fondo.
- El usuario NO quiere el 3D de toda la red (`iso_b.py` ya no se usa).

---

## 16. Datos finales (vigentes)

### 16.1 Por eje (`diseno.json`)
| Eje | Sist. | L (m) | Tapado (m) | C.F. inicio | C.F. final | h final | h máx. |
|---|---|---|---|---|---|---|---|
| EJE-01 | 1 | 34.34 | 0.00 | 184.350 | 184.178 | 0.472 | 0.472 |
| EJE-02 | 1 | 76.04 | 0.76 | 184.350 | 183.759 | 0.891 | 0.891 |
| EJE-03 | 1 | 32.31 | 0.00 | 184.350 | 184.188 | 0.462 | 0.462 |
| EJE-04 | 1 | 94.34 | 0.00 | 184.350 | 183.878 | 0.772 | 0.772 |
| EJE-05 | 1 | 90.56 | 0.00 | 184.350 | 183.897 | 0.753 | 0.753 |
| EJE-06 | 1 | 12.30 | 0.00 | 184.350 | 184.289 | 0.361 | 0.361 |
| EJE-07 | 2 | 94.69 | 22.91 | 184.350 | 183.736 | 0.914 | 0.914 |
| EJE-08 | 2 | 39.68 | 0.00 | 184.350 | 184.152 | 0.498 | 0.498 |
| EJE-09 | 2 | 35.80 | 0.00 | 184.350 | 184.171 | 0.479 | 0.479 |
| EJE-10 | 2 | 36.90 | 0.00 | 184.350 | 184.166 | 0.484 | 0.484 |
| EJE-11 | 2 | 30.36 | 0.50 | 184.350 | 184.198 | 0.452 | 0.452 |
| EJE-12 | 3 | 118.38 | 15.21 | 184.350 | 183.758 | 0.742 | 0.742 |
| EJE-13 | 3 | 24.38 | 0.00 | 184.200 | 184.078 | 0.422 | 0.422 |
| EJE-14 | 3 | 64.93 | 0.00 | 184.350 | 184.025 | 0.475 | 0.475 |
| EJE-15 | 3 | 41.47 | 0.00 | 184.350 | 184.124 | 0.376 | 0.379 |
| EJE-16 | 3 | 49.55 | 0.00 | 184.350 | 184.102 | 0.398 | 0.476 |
| EJE-17 | 4 | 39.98 | 4.58 | 184.350 | 184.145 | 0.505 | 0.505 |
| EJE-18 | 4 | 38.68 | 0.00 | 184.350 | 184.157 | 0.493 | 0.493 |
| EJE-19 | 4 | 14.09 | 0.00 | 184.350 | 184.280 | 0.370 | 0.370 |
| **Total** | | **968.78** | **43.96** | | | | |

EJE-13 arranca en 184.20 porque nace en el patio de maniobra (rasante 184.50 - 0.30). Longitud por sistema: 1 = 339.89 m,
2 = 237.43 m, 3 = 298.71 m, 4 = 92.75 m. 91 tramos hidráulicos.

### 16.2 Empalmes (caída = C.F. que llega - C.F. que recibe)
EJE-01→EJE-02 en P-03 0.417; EJE-03→02 P-07 0.056; EJE-04→02 P-08 0.000; EJE-05→02 P-10 0.078; EJE-06→04 P-16 0.117;
EJE-08→07 P-27 0.000; EJE-09→07 P-28 0.109; EJE-10→07 P-32 0.248; EJE-11→07 P-33 0.335; EJE-13→12 P-54 0.098;
EJE-14→12 P-55 0.088; EJE-15→12 P-56 0.247; EJE-16→12 P-60 0.342; EJE-18→17 P-81 0.008; EJE-19→18 P-86 0.116.

### 16.3 Descargas
| Descarga | C.F. de salida | Terreno en el cerco | Terreno bajo la C.F. a | Perfilado máx. | Último tramo (A, C, Q) | y / h / BL / V |
|---|---|---|---|---|---|---|
| D1 (EJE-02) | 183.759 | 183.91 | 0.5 m | 0.01 m | 3,539 m², 0.692, 229.2 l/s | 0.453 / 0.79 / 0.336 / 1.42 m/s |
| D2 (EJE-12) | 183.758 | 180.55 | 0.25 m | 0 | 3,028 m², 0.807, 228.9 l/s | 0.453 / 0.64 / 0.187 / 1.42 m/s |
| D3 (EJE-07) | 183.736 | 183.83 | 0.5 m | 0.00 | 2,193 m², 0.809, 166.2 l/s | 0.349 / 0.81 / 0.464 / 1.34 m/s |
| D4 (EJE-17) | 184.145 | 184.46 | 0.5 m | 0.10 m | 633 m², 0.767, 45.5 l/s | 0.131 / 0.40 / 0.271 / 0.96 m/s |

Perfil exterior guardado (distancia, cota) en `verificacion.json → descargas[].exterior`, p. ej. D1: 0.25 → 183.77, 0.5 → 183.58,
1.0 → 183.21, 2.0 → 182.49, 3.0 → 181.93. D2 sale a terreno ~3.2 m más bajo: proteger la entrega contra erosión (recomendación
fuera del alcance metrado). El metrado considera un perfilado de terreno de 0.60 x distancia de salida por descarga.

---

## 17. JSON intermedios (`entregables_barranquita/_calc/`)

### 17.1 diseno.json (de `diseno_b.py`)
```
{
 "criterios": {"b_int":0.4, "muro":0.1, "b_tot":0.6, "h0":0.3, "hmin":0.25, "S":0.005, "ntn_plataforma":184.65,
               "n_manning":0.013, "borde_libre":0.05, "npt":184.65, "rasante":184.65, "nivel_area_verde":184.6,
               "nivel_patio":184.5, "rasante_patio":184.5},
 "nudos":   {"A0": [354844.67, 9249873.87], ...},          # 92 nudos usados (UTM, 3 decimales)
 "nombre":  {"A0": "P-01", "D1n~b": "P-03", ..., "D1": "D1"},
 "descargas": {"D1": "Cerco sur-oeste (lado C22-C1, x = 820.1): al talud natural ...", ...},
 "ramales": [
   {"codigo":"EJE-01", "sistema":1, "nudos":["A0","A1","D1n~b"], "descripcion":"...", "L":34.34,
    "tramos":[{"de":"A0","a":"A1","L":31.9,"ras_de":184.65,"ras_a":184.65,"cf_de":184.35,"cf_a":184.191,
               "h_de":0.3,"h_a":0.459,"S":0.005,"h_max":0.459,"L_tapado":0,"L_rejilla":31.9,"Q_cap":0.1257}, ...],
    "tapados":[[s_ini, s_fin], ...],
    "perfil":[[s, rasante, cota_de_fondo], ...]}            # cada ~0.5 m
 ]
}
```

### 17.2 verificacion.json (de `verifica_b.py`)
```
{
 "comprobaciones": [{"n":1, "comprobacion":"Conectividad: ...", "estado":"CUMPLE", "detalle":"..."}, ... 11],
 "descargas": [{"D":"D1","cf":183.759,"terreno":183.91,"sale_a_m":0.5,"corte_max":0.01,"tipo":"pase",
                "estado":"SALE POR GRAVEDAD","receptor":"...","exterior":[[0.25,183.77], ...]}, ...],
 "hidraulica": [{"ramal":"EJE-01","de":"P-01","a":"P-02","A_m2":533.0,"C":0.575,"Q_ls":28.7,"S":0.5,"y":0.095,
                 "h":0.3,"borde_libre":0.205,"V":0.83,"cap":"CUMPLE","vel":"CUMPLE"}, ... 91],
 "empalmes": [["EJE-01","EJE-02","P-03",184.178,183.761,0.417], ...],      # (llega, recibe, nudo, cf_llega, cf_recibe, caída)
 "hidrologia": {"C":0.761,"I":293.18,"tc":10.0,"P10":48.86,"P24":169.27,"T":25,"factor":1.0,"n_cap":0.015,"n_vel":0.013,
                "A_total":9393.0,"superficies":{"techo":{"A":5548,"C":0.88}, ...},"FS":1.15,
                "detalle_superficies":[{"tipo":"techo","zona":"Patio civico techado","A":517.7}, ...],
                "areas_eje":{"EJE-02":{"techo":451,"pavimento":21,"estacionamiento":0,"verde":271}, ...}}
}
```
Detalle de superficies (m², shapely): coberturas 4,129.6; patio cívico techado 517.7; losa multiusos techada 829.4; patio 01 118.8;
patio 02 194.2; patio 03 257.9; patio 04 87.7; veredas/circulaciones/atrio/losa de tratamiento 202.5; patio de maniobra y
estacionamiento 647.3; áreas verdes 2,379.7.

### 17.3 Otros
| Archivo | Estructura | Lo escribe / lo lee |
|---|---|---|
| `hmin_req.json` | `{"EJE-xx|nudo_de|nudo_a": h_min}`; vigente `{}` | verifica_b / diseno_b |
| `tapas.json` | `[{"eje":"EJE-02","progresiva":75.74,"x":354820.328,"y":9249849.643}, ...]` (10) | planos_b / cantidades_b, excel_b |
| `secciones.json` | `{"EJE-01":[{"n":2,"s":0.0,"nct":184.65,"ncf":184.35,"h":0.3,"tap":false,"nota":"Inicio del eje","eje":"EJE-01"}, ...]}` | planos_b / excel_b |
| `indice.json` | `[["DC-01","PLANTA GENERAL DE CUNETAS - PLANTEAMIENTO PRELIMINAR","A1","1/250"], ...]` (DC-01 a DC-19) | planos_b / excel_b, memorias_b, indice_planos_b |
| `laminas.json` | `{"DC-00":[x0,y0,x1,y1], ...}` caja de cada lámina en el espacio modelo (para `dxf_render.py`) | planos_b / render, indice_planos_b |
| `coberturas.json` | `{"fuente":..., "coberturas":[{"A":379.99,"ejes":["EJE-16","EJE-17"]}, ...]}` (16 techos y los dos ejes que reciben sus aguas) | hidrologica_doc_b (caché sin base) |
| `junta_piso.json` | `{"fuente":..., "junta_piso":{"EJE-04":24.0, ...}}` junta asfáltica cuneta-piso por eje (m) | cantidades_b (caché sin base) |
| `lluvia_comparacion.json` | comparación de fuentes de lluvia (otro tema) | lluvia_datos_b |

Excel de control `CUADRO_TRAMOS_CUNETAS_IE0590_BARRANQUITA.xlsx`: hojas RESUMEN, VERIFICACION, CRITERIOS, HIDRAULICA, TRAMOS,
NUDOS, SECCIONES y TAPAS INSPECCION.

---

## 18. Aplicable a las cunetas de los CAR (Morales)

### 18.1 Cunetas del CAR Varones (CUI 2705619)
- 4-10-2026 04:57: el usuario pasó el DXF de perfiles y secciones de Varones con su convención de colores: **azul** = cuneta
  tramo abierto; **verde** = tramo tapado (cerrado); **magenta** = losa de fondo (y, en secciones, barras de acero transversal);
  **círculos azules** = acero longitudinal de 3/8" en las cunetas tapadas. Rótulos `NCT:`, `NCF:`, `H:` junto a cada `SECCION nn`,
  progresivas `0+xx.xx` en la guitarra, eje horizontal en metros reales (detalle en el skill `metrado-cunetas`).
- 4-10-2026 05:35, acero: "las cunetas que superen los 0.40 m llevarán acero, las que no superen eso no llevarán acero, salvo
  excepción si aparece una cuneta tapada (p. ej. a los 13.20 m con 0.37 m de profundidad): allí sí entra el acero aunque no llegue
  a 0.40. La altura la mido desde el NCT, ya sea cuneta abierta o cerrada". Eje 01 tapado de 13.20 a 19.20 lleva acero también en
  la tapa; acero transversal de las tapas 0.56 m siempre, @0.25. (En Barranquita el usuario lo dijo "a partir de 40": h ≥ 0.40.)
- 4-10-2026 06:09: ejes 06, 04 y 01 a nivel terminado 261.15; el colector al ras 261.15; por el eje 09 (lado derecho) es la única
  entrada de camiones cisterna, de 5.80 m.
- 4-10-2026 06:12: donde el colector ocupa la franja exterior, las cunetas de llegada se acortan ("eso se tiene que restar"): cada
  cuneta se metra hasta la cara del muro lado predio del colector (acortamientos 0.04, 0.10, 0.26, 3.39 y 2.77 m; `DESCUENTOS` en
  `herramientas/metrado_varones.py`). El 8-10 el usuario quitó la partida de empalme: "por qué hay empalme si ya he considerado su
  proyección hasta el colector de todas".
- 4-10-2026 17:03: "no hay cerco perimétrico en Varones... todo lo que está en su lindero cerca a la carretera no tiene cerco"
  (se corrigieron los detalles de cerco); y "cuando las cunetas llegan al colector tú pones las tapas en otro lugar y no exactamente
  donde deben ir las cajas": el registro va exactamente donde entrega la cuneta. 17:18: "las cunetas son las que van recto,
  perpendicular [al colector]... la de color verde fuerte, no la que está en color negro".
- Ejes de cunetas de Varones: `insumos/katiuska/EJES_CUNETAS_VARONES.json` = `{"01": [[x, y], [x, y], ...], ..., "09": [...]}`
  (polilínea de cada eje desde su progresiva 0+000; coordenadas del plano de arquitectura). Refugio: `insumos/solange/EJES_CUNETAS_REFUGIO.json`
  (ejes 01 a 12).

### 18.2 Lloraderos junto a áreas verdes (CAR Varones y Hogar de Refugio; CAR Mujeres no, ya presupuestado)
- 8-10-2026 04:08, el usuario: "agrégale como lloradero de PVC... pero solo irán en las partes donde la cuneta esté expuesta a área
  verde". CAR Mujeres (CUI 2717013) no se toca.
- **Detección de tramos** (medidos en la planta general de drenaje): un tramo de muro de cuneta lleva lloraderos cuando la **franja
  exterior de 0.30 m del muro cae en el achurado de área verde**. Capas de área verde: Refugio `HIERVA`; Varones `HIERVA`,
  `Area Verde`, `Hatch Jardin` (también dentro de bloques). Las progresivas de los tramos salen en múltiplos de 0.25 m (p. ej.
  0+013.50 a 0+019.00).

```
para cada eje de cuneta (polilínea desde 0+000), para cada lado del muro (izquierdo / derecho):
    recorrer el eje (paso 0.25 m); en cada progresiva tomar el punto de la franja exterior del muro (0.30 m hacia afuera)
    marcar si cae dentro de un achurado de área verde
    agrupar progresivas consecutivas marcadas -> tramo (eje, lado ESTE/OESTE/NORTE/SUR, p0, p1, L = p1 - p0)
N.° de lloraderos del tramo = REDONDEAR.MAS(L / 1.50)       # hoja METRADO LLORADEROS: =IF(B7="","",ROUNDUP(E7/F7,0))
```
- Resultado: CAR Varones 226 lloraderos en 34 tramos (320.53 m de muro); Hogar de Refugio 157 lloraderos (226.21 m).
- Partida 01.04.03.04.03.04 "LLORADERO DE TUBERIA PVC Ø3" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m" (und), hoja METRADO LLORADEROS
  (N.°, eje, progresiva desde-hasta, lado del muro, longitud junto a área verde, espaciamiento 1.50, N.° de lloraderos). Ninguna
  otra partida cambió.
- Detalle: tubo PVC-U Ø 3" (76 mm), L = 0.30 m, que atraviesa el muro a media altura, S = 0.5 % hacia la cuneta, con filtro de grava
  (20 a 40 mm) y geotextil; el primero y el último a no menos de 0.30 m de las juntas de dilatación; si ambos muros dan al área
  verde, en los dos (`espec_lloraderos.py`, `techo/planos_lloraderos.py`). Se colocan repartidos en el tramo (`d = (p1 - p0)/n`,
  centrados en su paño).
- Plano DL-00 de ubicación (`herramientas/planos_ubicacion_lloraderos.py [refugio|varones]`): planta de arquitectura en gris,
  cunetas en azul, áreas verdes en verde sólido, tramos numerados igual que la hoja (capa LLORAD-TRAMO), lloraderos @1.50
  (LLORAD-SIMB), cuadro de tramos, leyenda, notas y detalle típico sin patrones de achurado (en AutoCAD los patrones salían sin
  escala). Lado del muro: tabla `LADO` en el Refugio; en Varones se deduce del rumbo de la hoja comparado con la normal al eje
  (norte arriba): `lado = +1 si dot((-u.y, u.x), RUMBO[lado]) > 0` (izquierda del sentido de la progresiva). Distancia del eje a la
  cara exterior del muro en el dibujo: `OFS = 0.55`. Escala 1/250, A1.

### 18.3 Reglas para el programa DRENIE (24-10-2026)
- **Lloraderos por lado**: el programa revisa cada lado de cada tramo de cuneta con el mapa de superficies; el lado cuyo muro
  toca área verde lleva lloraderos (PVC Ø 3" @ 1.50 m, N.° = REDONDEAR.MAS(L / 1.50)); el lado que toca vereda, patio o
  pavimento no lleva. Si los dos lados dan a área verde, en los dos. Cada lloradero lleva detrás una caja filtrante de
  0.30 × 0.30 de grava envuelta en geotextil. Con lloraderos no se usan drenes franceses (subdrén).
- **Dimensiones**: muros 0.10 y losa 0.10 fijos por defecto; ancho libre b y profundidad h salen del caudal de cada cuneta,
  redondeados a medidas constructivas; el proyectista puede proponer su dimensionamiento y el programa lo verifica. No se
  aceptan secciones que no se pueden encofrar ni acabar (p. ej. 0.20 × 0.20).
- **Caudal por cuneta**: el programa muestra, por tramo, el área de techo, de pisos y de área verde que le llega y su caudal.
- **Medidas y uniformidad** (usuario, 24-10-2026): mínimo 0.30 × 0.30 libre, medidas de 5 en 5 cm, pendiente inicial 0.5 %.
  0.30 × 0.30 es lo libre: ancho total 0.30 + 2 × 0.10 = 0.50; excavación 0.30 + 0.10 losa de fondo + 0.10 solado = 0.50. Un eje
  o un sector (ejes que se unen y salen por la misma descarga) lleva una sola medida: la mayor que pida cualquiera de sus tramos;
  no se mezclan 0.30 y 0.40 en tramos seguidos. El dimensionamiento final adoptado es manual (hoja DIMENSIONAMIENTO, columna B
  ADOPTADO) y el programa lo verifica. Tirante <= ancho. Sin límite de profundidad respecto al ancho (usuario: "no hay
  problema; la regla es que no quede enterrada la cuneta, que todo salga bien siempre").
- **Ancho máximo** (usuario, 24-10-2026): "0.50 libre y 0.70 total es exagerado"; proponer medidas reales constructivas: máximo
  0.40 libre interior (0.60 total). Si el caudal pide más, se profundiza en vez de ensanchar. Barranquita: sectores D1 y D2 0.40
  libre (0.60 total), D3 0.30 libre (0.50 total).

---

## 19. Para implementarlo en un programa

### 19.1 Módulos
| Módulo | Responsabilidad | Equivalente en el repositorio |
|---|---|---|
| `lector_dxf` | abrir DXF (o ZIP en partes, probando el orden), explotar bloques (profundidad ≤ 6), detectar la copia sobre las curvas, filtrar por ventana UTM, guardar base reducida `{geo, txt}` | `explode.py` + extracción a `base_sitio.pkl` |
| `terreno` | curvas válidas (z > 100 o rango del sitio), TIN lineal `z(x, y)` | `terreno_b.py` |
| `sitio` | cerco (polígono confirmado), offset interior, patio y otras zonas de nivel, veredas cerradas, muros, superficies por tipo | `diseno_b.py` (CERCO, PATIO), `hidrologia_b.superficies` |
| `red` | nudos, ramales, sistemas, descargas, tapados fijos, conexiones, chaflanes | `diseno_b.py` (N, RAMALES, chaflanes) |
| `cotas` | muestreo cada 0.5 m, rasante, tapado, cota de fondo con empalmes | `diseno_b.calcular()` |
| `hidraulica` | áreas de aporte por malla de 1 m², C por superficie, Q racional acumulado, Manning, borde libre, V | `verifica_b.py` (8 y 9) |
| `verificacion` | las 11 comprobaciones; escribe profundidades mínimas por capacidad | `verifica_b.py` |
| `ciclo` | diseño ↔ verificación hasta que no cambien las profundidades mínimas | `calcula_b.py` |
| `secciones` | dónde va sección, numeración, acero sí/no | `perfiles_b.secciones` |
| `tapas` | tapas de inspección en tapados | `planta_cunetas_b._tapas` |
| `cantidades` | concreto, encofrado, acero, juntas, rejilla, tapas, movimiento de tierras por eje | `cantidades_b.py` |
| `planos` | planta, perfiles, secciones, cortes, detalle de descargas a escala real | `planos_b.py` y vecinos |

### 19.2 Estructuras de datos mínimas
```
Parametros  { b_int=0.40, e_muro=0.10, b_tot=0.60, e_losa_fondo=0.10, e_tapa=0.10, h0=0.30, hmin=0.25, S0=0.005,
              h_acero=0.40, n_cap=0.015, n_vel=0.013, BL=0.05, Vmax=3.0, chaflan=0.60, ang_chaflan=50,
              d_cerco=0.60, paso_muestreo=0.5, tapa=0.60, max_tapas=10.0, FS=1.15 }
Niveles     { npt=184.65, borde=184.65, area_verde=184.60, zonas=[(poligono_patio, 184.50)] }
Sitio       { cerco: Poligono, veredas: [Poligono], muros: [Segmento], superficies: {tipo: MultiPoligono}, z(x, y) }
Nudo        { id, x, y, nombre_plano ("P-xx" / "Dn") }
Ramal       { codigo, sistema, nudos: [id], descripcion }
Descarga    { id, nudo_D, nudo_Dn, receptor, direccion_exterior opcional }
TramoTapado { codigo, nudo_a, nudo_b, motivo }
Punto       { s, x, y, nudo|None, rasante, tapado, cota_fondo }
Tramo       { de, a, L, ras_de, ras_a, cf_de, cf_a, h_de, h_a, S, h_max, L_tapado, L_rejilla, A, C, Q, y, BL, V }
Seccion     { n, eje, s, nct, ncf, h, tapada, nota, con_acero }
Tapa        { eje, s, x, y }
```

### 19.3 Orden del algoritmo
```
1. Leer el DXF (o sus partes), explotar bloques, elegir la copia sobre las curvas (UTM), guardar base reducida.
2. Construir el TIN con las curvas válidas. Generar imagen de control.
3. Delimitar el cerco y CONFIRMARLO con el usuario (imagen). Leer NPT del plano; preguntar los niveles que falten
   (pisos, borde de cuneta, áreas verdes, patios) y el receptor de cada descarga.
4. Definir dónde va cuneta: bajo cada caída de techo (dos aguas: ambos lados; una agua: lado bajo); si el usuario trazó
   líneas, usar exactamente esas (no mover ni juntar; quitar las que no tengan línea).
5. Elegir descargas en el cerco, en los lados bajos según las curvas, donde el terreno exterior quede bajo la cota de fondo
   probable a ≤ 2 m; agrupar en sistemas; trazar uniones dentro del cerco (perimetral a 0.60 m del cerco) sin cruzar franjas altas.
6. Ochavar esquinas (> 50°) con chaflanes de 0.60 m; ejes que llegan a una esquina entran en diagonal.
7. Marcar tapados (veredas cerradas, ingresos, pase del cerco).
8. Muestrear cada 0.5 m, rasante por zona, pase sin bajar, y calcular cotas de fondo con la iteración de empalmes.
9. Hidráulica y 11 comprobaciones; si falla capacidad, subir la profundidad mínima del tramo y volver a 8 (ciclo).
   Si una descarga no sale o la profundidad se dispara, cambiar la ruta o la descarga (volver a 5).
10. Secciones, acero sí/no, tapas de inspección, cantidades.
11. Planos a escala real (1 unidad = 1 m) con el estilo del usuario; cuando el usuario imprime, congelar planos.
```

### 19.4 Validaciones que el programa debe hacer (y avisar en vez de inventar)
- Curvas con z = 0 o fuera de rango: descartar y reportar cuántas.
- Más de una copia del conjunto: reportar cuáles y cuál se usa (la que está sobre las curvas).
- Polígono del cerco: cerrado, sin autointersecciones, confirmado por el usuario antes de diseñar.
- Cada ramal: ≥ 2 nudos; su último nudo es una descarga o un nudo interior de otro ramal (conectividad, sin ciclos).
- Ningún borde (eje ± 0.30) fuera del cerco salvo el tramo Dn → D.
- Fondo monótono (sin contrapendiente), S ≥ 0.5 %, h inicial 0.30, altura libre ≥ 0.25 (bajo la losa en tapados).
- Empalmes: la que llega no queda bajo la que recibe (tolerancia 0.005); preferir caída a escalón.
- Descarga: terreno exterior bajo la C.F. - 0.05 a ≤ 2.0 m; perfilado en el primer metro informado (sin obra fuera).
- Borde de cuneta ≤ NPT (al ras) y al ras de cada zona de nivel especial; rótulos del plano distintos se informan.
- Capacidad con borde libre ≥ 0.05 m (n 0.015) y V ≤ 3.0 m/s (n 0.013); si no, profundizar (no cambiar la sección acordada) o gradas.
- Eje a ≥ 0.30 m de los muros de los bloques.
- Sección mínima real: nunca una sección menor que la acordada en un pase o empalme (lección de la "sección de 15 cm").
- Acero: h ≥ 0.40 o tapado; si no, concreto simple.
- Longitudes en guitarras: siempre de sección a sección (no la parte de una pieza).
- Si el dibujo del usuario no sigue la convención (colores, rótulos), avisar qué no se pudo leer.

## 20. Plataformas, cambios de nivel y estacionamientos (usuario, 25-10-2026)
- **Nivel de piso**: un solo NPT para todo o por plataformas (terrenos muy desnivelados: 1 a 4 plataformas). El usuario delimita
  cada plataforma (en DrenIE: comando PLATAFORMA del visor) con su NPT y el rebaje del borde de cuneta (al ras, 5 o 10 cm).
  Rampas: el borde de la cuneta sigue la pendiente de la rampa (nivel de inicio y de fin). Escaleras: nunca pasa una cuneta.
- **Borde por eje**: al dibujar cada eje de cuneta el programa pregunta si va al ras del NPT o rebajado 5 o 10 cm (u otro), y el NPT
  del eje si no es el de su plataforma.
- **El agua va siempre de la plataforma alta a la baja**: una zona que solo saldría subiendo de plataforma tiene su propia descarga.
- **Estructura según el desnivel** del borde entre plataformas:
  - hasta 0.15 m: cuneta continua, el desnivel se absorbe en la pendiente (1.5 %, entre 3 y 15 m antes del cambio);
  - 0.15 a 0.50 m: caída corta (escalón en el fondo, losa de fondo reforzada);
  - 0.50 a 1.00 m: caja de caída de concreto armado con poza de disipación;
  - más de 1.00 m (siempre hay muro de contención): la cuneta de arriba llega al ras hasta la cara del muro, lo atraviesa por un
    **marco de concreto armado** (no tubería), cae vertical a una **poza de disipación** al pie del muro y de ahí sigue la cuneta de abajo.
- Poza (USBR, caída vertical, Rand): D = q²/(g·hd³), Ld = 4.30·hd·D^0.27, yp = 1.00·hd·D^0.22, y1 = 0.54·hd·D^0.425,
  y2 = 1.66·hd·D^0.27, L = Ld + 6.9·(y2 − y1); profundidad hasta cubrir y2; mínimos 0.60 m de largo y 0.10 m de colchón.
  Concreto f'c 210, malla 3/8" @ 0.20 en ambos sentidos, espesor 0.15. La pendiente del tramo no cuenta la caída (la toma la estructura).
- **Estacionamiento (regla fija)**: nunca rejilla, siempre cuneta tapada, con losa de concreto armado f'c 280 diseñada para la rueda del
  camión HL-93 del MTC (72.5 kN, IM 33 %, factor 1.75): para 0.40 libre sale e = 0.15 con Ø 1/2" @ 0.175 en ambos sentidos.
- Cada valor con su fuente en la biblioteca de normas (`drenie_motor/normas_biblioteca.json`): norma, referencia técnica o criterio
  del proyectista, y su estado (verificado o por verificar con el texto oficial vigente). La OS.060 fue reemplazada por la CE.040
  (R.M. N.° 126-2021-VIVIENDA).
