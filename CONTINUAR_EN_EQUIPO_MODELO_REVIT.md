# Continuar en el equipo (local): modelo Revit del Hogar de Refugio

Hogar de Refugio Temporal "Mujeres Violentadas", CUI 2675514.

Este documento sirve para seguir el trabajo en tu computadora, sin la nube. Todo el trabajo hecho está en este repositorio,
en la rama `claude/colector-pluvial-hogar-refugio-ydbnaf`.

## 1. Preparar el equipo (una sola vez)

1. Instalar **Git for Windows**: https://git-scm.com/download/win
2. Instalar **Python 3.11** (https://www.python.org/downloads/). Al instalar, marca *Add Python to PATH*.
3. Instalar **Node.js LTS** (https://nodejs.org). Solo se necesita para los Word de especificaciones.
4. Instalar **Claude Code**. Tienes dos opciones:
   - la app de escritorio de Claude, pestaña **Code**, con la opción de trabajar en una carpeta local;
   - o en PowerShell: `irm https://claude.ai/install.ps1 | iex` y luego `claude` dentro de la carpeta.
5. Descargar el repositorio en PowerShell (por ejemplo, en `D:\PROYECTOS`):
   ```
   cd D:\PROYECTOS
   git clone https://github.com/josedelcarmenpizarrosuarez10-debug/holaaa.git
   cd holaaa
   git checkout claude/colector-pluvial-hogar-refugio-ydbnaf
   pip install ezdxf shapely openpyxl python-docx ifcopenshell matplotlib numpy
   ```
6. Abrir Claude Code en la carpeta `holaaa`. Lee solo el `CLAUDE.md` con todas las reglas del proyecto.

## 2. Dónde poner los planos

Copia los DXF de arquitectura en `holaaa\herramientas\render_refugio\dxf\`. Es la carpeta que leen `extrae.py` y los
demás lectores, y los nombres de archivo deben quedar como los de la arquitecta. Por ejemplo, la planta general debe
llamarse `PG 01-PG 02 PLANTA GENERAL.dxf`.

| Ya usados en la versión actual | Faltan para la versión precisa |
|---|---|
| A 01 a A 09 EDIFICACIONES | DT-01 a DT-15 (detalles de puertas y ventanas) |
| PG 01-PG 02 PLANTA GENERAL (PG-02 = planta de techos) | OE-01 a OE-07 |
| CG 01-EG 01 (cortes y elevaciones generales) | OC-02 a OC-05 |
| OC-06 | Cortes y elevaciones de cada edificación |
| Plano de drenaje: `PLANTA GENERAL - MUJERES VIOLENTADAS.dxf` | |

## 3. Qué está hecho

- **Renders** (`herramientas/render_refugio/`, salida en `entregables/renders_hogar_refugio/`):
  - el patio cívico va sin pérgola;
  - los portones y celosías del OE-01 son de plancha metálica llena;
  - el cerco del frente es de muro, sin rejas;
  - la red de drenaje está tal cual el plano del usuario.
- **Modelo para Revit** (`entregables/modelo_revit/`):
  - `DYNAMO_MODELO_NATIVO_HOGAR_REFUGIO.dyn/.py`: lo genera `herramientas/render_refugio/revit_nativo.py`. Usa el motor
    PythonNet3 y crea con familias nativas:
    - materiales TP-1 guinda RGB 123-31-45, TP-2 gris RGB 125-133-139 y TP-3 RAL 9010;
    - tipos HR- de muro, piso y cubierta;
    - muros, columnas, vigas collar, hastiales, cubiertas al 28 % con alero de 1.50;
    - arco de la losa deportiva, OE-01, cerco, pisos, puertas, ventanas y árboles RPC.
  - `HOGAR_REFUGIO_IFC2X3_COMPLEMENTO.ifc`: lo genera `exporta_ifc.py --complemento`. Lleva drenaje, juegos, bancas,
    portones, letras, tanque y cancha.
  - `LEEME_PASOS_REVIT.txt`: los pasos dentro de Revit.
  - Ya probado en Revit 2027 con éxito: muros, techos, el arco corregido, cerco, árboles RPC (se ven reales con
    *Accelerated Graphics* apagado) y el IFC vinculado.
- **Limitación actual:** las puertas y ventanas se colocan por regla, una cada ~3.6 m, y solo con la planta general.

## 4. Lo que sigue (versión precisa del script de Dynamo)

Hay que hacer una nueva versión de `herramientas/render_refugio/revit_nativo.py` que:

1. lea del DXF los **muros reales**, también los interiores, con su espesor;
2. coloque las **puertas y ventanas por bloque**, con su ancho y alto según los DT-01 a DT-15;
3. tome las **alturas** de los cortes de cada edificación (piso terminado, dintel, alféizar, viga, cumbrera);
4. arme los **techos** con la geometría de la PG-02 (planta de techos);
5. deje la salida en `entregables/modelo_revit/` con el mismo nombre y actualice `LEEME_PASOS_REVIT.txt`.

Antes de correr la versión nueva en Revit, **borra lo creado en la corrida anterior** (muros, pisos, cubiertas, puertas,
ventanas, columnas y árboles). Los tipos y materiales HR- se reutilizan, así que no hace falta borrarlos.

## 5. Mensaje para empezar en Claude Code local

Copia y pega esto al abrir Claude Code en la carpeta `holaaa`:

> Lee CLAUDE.md, el final de BITACORA_CONVERSACION.md y CONTINUAR_EN_EQUIPO_MODELO_REVIT.md. Continuamos el modelo Revit
> del Hogar de Refugio (CUI 2675514). Los DXF están en herramientas/render_refugio/dxf/. Revisa qué planos hay y haz la
> nueva versión de revit_nativo.py según el punto 4: muros reales también interiores, puertas y ventanas por bloque con
> su tamaño de los DT, alturas de los cortes y techos de la PG-02. Responde en español.

En local, Claude Code puede abrir directamente los DXF de tus carpetas y dejar el script listo en la carpeta que uses
con Revit. Para que los cambios queden guardados, al final de cada sesión pide: "haz commit y push".
