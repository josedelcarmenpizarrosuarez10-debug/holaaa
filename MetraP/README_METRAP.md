# MetraP 1.0 - Metrado de cunetas desde un plano DXF

MetraP lee un plano DXF con los **perfiles longitudinales de las cunetas** (y sus secciones) y llena,
hoja por hoja, la **plantilla Excel de metrados del proyecto** (misma estructura de la planilla de
drenaje pluvial: CONCRETO EN CUNETAS, ENCOFRADO Y DESENCOFRADO, METRADO ACERO, METRADO DE CURADO,
METRADO DE REJILLAS, METRADO JUNTA DE DILATACION, PLANILLA GENERAL DE METRADOS y PARAMETROS), con las
mismas fórmulas, formato y encabezados de la planilla original.

## 1. Contenido de la carpeta

| Archivo | Para qué sirve |
|---|---|
| `metrap.py` | Programa: interfaz gráfica (sin argumentos) o línea de comandos. |
| `metrap_engine.py` | Motor: lectura del DXF, cálculo de tramos, alturas, acero, y llenado de la plantilla. |
| `metrap_config.json` | Configuración del proyecto (capas, colores, umbral de acero, acortamientos, nombre del proyecto). |
| `plantilla/PLANTILLA_METRADO_CUNETAS.xlsx` | Plantilla Excel del proyecto (se copia; nunca se modifica). |
| `ejemplo/PERFIL_CAR_VARONES.dxf` | Plano de ejemplo (CAR Varones) para probar. |
| `requirements.txt` | Librerías de Python necesarias. |
| `build_exe.bat` | Genera `MetraP.exe` con PyInstaller (Windows). |

## 2. Cómo debe estar dibujado el DXF (convención que lee el programa)

- Un **perfil por eje**, apilados verticalmente. Cada perfil lleva su rótulo `EJE 01`, `EJE 02`, ... en la
  capa `capa_ejes` (por defecto `A-AREA-IDEN`). El rótulo define la banda vertical de ese eje.
- **Línea azul (color 5)** sobre el fondo = tramo **abierto**; **línea verde (color 84)** = tramo **tapado**.
  Los colores se cambian en `metrap_config.json` (`color_abierto`, `color_cerrado`; "por capa" también vale).
- Textos de las **progresivas** (`0+00`, `0+05`, ...) en la capa `capa_progresivas` (por defecto `GRID_TEXT`).
  La progresiva 0+000 es el **inicio de las líneas de perfil**; las secciones se ubican por su x.
- En cada sección rotulada del perfil, textos `SECCION nn`, `NCT: 261.15`, `NCF: 260.69`, `H: 0.56`
  (alturas medidas desde el NCT). Con esos textos se interpola H a lo largo del eje.
- Los perfiles van a la **izquierda** y las secciones transversales a la derecha; el programa detecta el
  límite automáticamente (o se fija con `x_max_perfiles`).

## 3. Reglas de metrado que aplica (iguales a las validadas en Varones)

- Longitudes y áreas de muro por tramo (integral de H entre secciones), abiertos y tapados por separado.
- **Acero**: solo donde H (desde el NCT) supera `h_minima_acero` (0.40 m); un tramo abierto que pasa de 0.40
  dentro de su longitud se metra desde el punto donde H = 0.40. Los **tramos tapados llevan acero siempre**, con
  acero transversal de tapa de `ancho_transversal_tapa` (0.56 m) cada `sep_transversal_tapa` (0.25 m).
- Separación del marco según H media: `separaciones_marco` ([límite, separación]: <0.45 → 0.20; <0.60 → 0.22; resto 0.25).
- Encofrado: abierta ext = (H + 0.10) × L, int = H × L; tapada ext = (H + 0.20) × L, int = H × L, fondo de tapa L × 0.40.
- Curado y rejillas: todos los tramos. Juntas: una fila por eje con su longitud. Movimiento de tierras: por eje con H promedio + losa.
- **Acortamientos** (`acortamientos`): metros que se descuentan del último tramo de un eje porque la cuneta
  termina en el muro de un colector o de una caja. Se documentan en una hoja nueva (`nombre_hoja_descuentos`).
- **Correcciones de NCF** (`correcciones_ncf`): fuerza el NCF de la última sección de un eje cuando el rótulo del plano está mal.
- Lo que no está en el DXF (montantes, sumideros, dados, tapas de registro) queda en 0 y se lista como PENDIENTE.

## 4. Uso

Interfaz gráfica: doble clic en `MetraP.exe` (o `python metrap.py`). Elegir DXF, plantilla, archivo de salida y configuración; pulsar METRAR.

Consola:
```
python metrap.py --dxf ejemplo\PERFIL_CAR_VARONES.dxf --plantilla plantilla\PLANTILLA_METRADO_CUNETAS.xlsx --salida METRADO_VARONES.xlsx --config metrap_config.json
```

Para otro proyecto: copiar `metrap_config.json`, cambiar `proyecto`, `acortamientos`, `correcciones_ncf` y, si el
dibujo usa otras capas o colores, `capa_ejes`, `capa_progresivas`, `color_abierto`, `color_cerrado`.

## 5. Generar el ejecutable MetraP.exe (Windows)

1. Instalar Python 3.10 o superior desde python.org (marcar "Add Python to PATH").
2. Abrir la carpeta `MetraP` y ejecutar `build_exe.bat` (doble clic). Hace:
   ```
   pip install -r requirements.txt
   pyinstaller --onefile --windowed --name MetraP --add-data "plantilla\PLANTILLA_METRADO_CUNETAS.xlsx;plantilla" --add-data "metrap_config.json;." --hidden-import ezdxf --hidden-import openpyxl --collect-all ezdxf metrap.py
   ```
3. El ejecutable queda en `dist\MetraP.exe`. Copiar junto a él `metrap_config.json` si se quiere editar la configuración sin recompilar.

## 6. Indicaciones para pedirle a ChatGPT (u otro asistente) que genere el .exe

Pegar este texto junto con la carpeta:

> Tengo un programa en Python llamado MetraP (archivos `metrap.py`, `metrap_engine.py`, `metrap_config.json`,
> carpeta `plantilla` con un .xlsx y `requirements.txt`). Usa `ezdxf`, `openpyxl` y `tkinter`. Necesito un
> ejecutable único para Windows (`MetraP.exe`) con interfaz gráfica, que incluya dentro la plantilla
> `plantilla/PLANTILLA_METRADO_CUNETAS.xlsx` y `metrap_config.json` como datos (`--add-data`), con
> `--onefile --windowed` y `--collect-all ezdxf`. El programa ya resuelve la ruta de recursos con `sys._MEIPASS`.
> Dame los pasos exactos con PyInstaller 6 y, si algo falla al abrir el .exe (por ejemplo falta de un
> submódulo de ezdxf), la corrección en el comando. No cambies la lógica de cálculo de `metrap_engine.py`.

## 7. Validación

Con `ejemplo/PERFIL_CAR_VARONES.dxf` y la configuración incluida, MetraP reproduce celda por celda la planilla
`METRADO_DRENAJE_PLUVIAL_CAR_VARONES_CUNETAS.xlsx` del expediente (0 diferencias), incluidos los acortamientos de
las cunetas que llegan al colector frontal.
