# Llevar el modelo de Blender a Lumion

Lo verificado viene de las páginas de soporte de Lumion, listadas al final. Lumion cambia de versión cada año: si un menú no coincide,
confiar en la página de soporte vigente. Lo que no se ha podido comprobar está dicho como tal.

## Lo que hay que saber antes de prometer nada
- **Lumion no da soporte oficial a Blender.** Su guía para Blender cubre las versiones 2.79 y 2.80 y advierte que no está probada hasta
  2.93. Con Blender 4.2 no hay guía oficial.
- **No hay LiveSync desde Blender.** Lumion lo ofrece para SketchUp, Revit, ArchiCAD, Vectorworks, AutoCAD, Rhinoceros, BricsCAD, FormIT
  y AllPlan. Cada corrección del modelo se exporta y se reimporta.
- **Formatos que acepta**: DAE, SKP, FBX, DWG, DXF, glTF, 3DS, OBJ y MAX (este último requiere 3ds Max). Desde Blender la guía indica FBX o DAE.
- **Requisitos** (página oficial de Lumion 2026): tarjeta dedicada NVIDIA, AMD o Intel (A580/B580 o superior), Windows 10 2004+ o
  Windows 11 24H2+, controladores recientes (NVIDIA 591.86, AMD 26.1.1, Intel 101.8509) y pantalla 1920×1080. Esa página no da una memoria
  de video numérica; sitios ajenos a Lumion hablan de 12 GB como mínimo y de 16 a 24 GB como recomendado. Pedir al usuario que compare con
  `lumion.com/product/system-requirements`. Con poca memoria, un proyecto con mucha vegetación puede no alcanzar.

## Cómo exportar (lo hace `scripts/exporta_lumion.py`)
```bash
blender -b modelo.blend --factory-startup -P exporta_lumion.py -- paquete_lumion MODELO vistas.json
```
| Requisito | Por qué | Cómo queda |
|---|---|---|
| Modelo cerca del origen | El punto de inserción en Lumion es el 0,0,0 de Blender | Coordenadas locales; el script avisa si el modelo está lejos |
| Texturas junto al modelo | Si no, Lumion no las encuentra | FBX con Path Mode Copy |
| Un material por superficie a tratar aparte | Lumion **siempre** une las superficies con el mismo material | Generador con materiales por elemento; `Malla` ya agrupa así |
| Nombres de material estables | Lumion reaplica sus materiales por nombre al reimportar | No renombrar entre versiones; prohibido `Material.001` |
| Mismo formato en cada reimportación | Cambiar de formato pierde lo asignado (dicho para SKP y DAE) | Elegir FBX o DAE y mantenerlo |
| Sin árboles ni pasto en 3D | Pesan y los de Lumion se ven mejor | Excluidos; quedan sus coordenadas |

Probado reimportando en Blender 4.2: tamaño, altura, nombres y colores se conservan en FBX y DAE. **Sin probar en Lumion**: si el modelo
entra acostado, a otra escala o con caras invertidas (la guía oficial no trata ejes, escala, UV ni normales), probar el otro formato y anotar qué
funcionó en esa versión. COLLADA viene en Blender 4.2; versiones posteriores pueden no traerlo y el script lo avisa y sigue con FBX.

## Qué se entrega al usuario (carpeta `paquete_lumion/`)
- `MODELO.fbx` (y `MODELO.dae`), con las texturas de imagen junto a él.
- `MODELO_marcas_arboles.fbx`: un poste por árbol, para plantar los de la biblioteca sobre ellos y luego borrarlo. Se inserta en el mismo punto.
- `materiales_lumion.csv`: material, RGB que llega, número de objetos, si usa textura de nodos y la columna del acabado.
- `arboles_lumion.csv`: posición y escala de cada árbol. `vistas_lumion.csv`: posición, mira, focal y sol de cada vista aprobada.
- Una imagen de Blender por vista, como referencia de encuadre y como comprobación de que nada falta.
- `LEEME_PASOS_LUMION.txt` con la plantilla de abajo, llenada con los datos del proyecto.

Antes de entregar, **llenar la columna del acabado** con el material y el RGB del cuadro de acabados (no inventar): pintura mate para muros,
concreto con juntas donde el plano lo diga, cobertura metálica o de teja, pasto solo en áreas verdes, arena donde hay achurado, vidrio y aluminio,
metal de portones.

## Plantilla del LEEME
```
<NOMBRE COMPLETO DEL PROYECTO> - CUI <CUI>
Modelo para Lumion. Unidades: metros. Origen local: E <...> / N <...> (zona <...>, datum <...>).

1. Copie la carpeta completa a su equipo; no separe el modelo de sus texturas.
2. En Lumion, cree un proyecto en un escenario plano e importe MODELO.fbx: Content Library > Imported Models,
   botón de importar. Colóquelo con Place, o arrastrando el archivo, en el punto 0,0,0.
3. Compruebe: ¿está de pie? ¿el muro de <elemento conocido> mide <medida>? ¿están todos los materiales de la tabla?
   Si algo sale mal, pruebe MODELO.dae y avise cuál funcionó. A partir de ahí use siempre ese formato.
4. Asigne a cada material el acabado de materiales_lumion.csv. Los colores RGB son los del cuadro de acabados.
5. Guarde el proyecto y una copia de los materiales (Save Material).
6. Inserte MODELO_marcas_arboles.fbx en el mismo punto, plante los árboles sobre los postes y borre las marcas.
   Ningún árbol debe tocar techos ni cerco.
7. Ponga el sol, el cielo y las cámaras guiándose por vistas_lumion.csv y por las imágenes de referencia.

Si el modelo cambia: reciba el archivo nuevo con el mismo nombre y use el botón de reimportar. Se conservan los
materiales mientras sus nombres no cambien. Si se pierden, use Load Material desde el proyecto guardado.
```

## Reimportar y recuperar materiales
- Botón ⟳ del modelo en Imported Models; con ALT permite elegir otro archivo.
- Si cambiaron los nombres de material, Lumion no puede reaplicar lo asignado. Arreglo: Save/Load Material desde un proyecto `.LS` intacto.
- Colocar un mismo modelo muchas veces usa referencias livianas.

## Límites honestos
- Claude no maneja Lumion por script: la imagen final la hace el usuario. Si no tiene Lumion o su tarjeta no alcanza, la salida es Cycles.
- Las texturas de nodos de Blender no viajan. Lo que se ve en Cycles no es lo que entra a Lumion hasta que se le asignen materiales.
- Las luces no se llevan: la iluminación se arma en Lumion.

## Fuentes
- Guía para Blender: https://support.lumion.com/hc/en-us/articles/360050219633-Model-import-guidelines-for-Blender
- Reimportar sin perder materiales: https://support.lumion.com/hc/en-us/articles/360008179854
- Importar modelos: https://support.lumion.com/hc/en-us/articles/12193299343260
- Formatos y LiveSync: https://support.lumion.com/hc/en-us/articles/360022038739
- Requisitos: https://support.lumion.com/hc/en-us/articles/12614080933660
