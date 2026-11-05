# Cómo usar el planteamiento de drenaje pluvial en otro chat

Paquete: `PLANTEAMIENTO_DRENAJE_PLUVIAL_SKILL.zip`. Trae la carpeta `planteamiento-drenaje-pluvial/` con:
- `SKILL.md`: los criterios y el método general (sirve para cualquier local; Barranquita queda solo como ejemplo de referencia).
- `referencias/04_cunetas_sobre_terreno_BARRANQUITA.md`: el caso completo, con cada decisión y sus números.
- `referencias/02_hidrologia_e_hidraulica.md`: la lluvia, los coeficientes C, el método racional, Manning, canaletas y montantes.

## Opción A — Como skill en Claude (recomendada)
1. En claude.ai entra a **Configuración → Capacidades → Skills** y elige **Subir skill**.
2. Sube `PLANTEAMIENTO_DRENAJE_PLUVIAL_SKILL.zip` tal cual, sin descomprimirlo.
3. En cualquier chat nuevo, pide "haz el planteamiento de drenaje pluvial de …": el skill se activa solo. Pega además el
   mensaje de abajo.

## Opción B — Sin instalar nada
1. Abre un chat nuevo y adjunta `SKILL.md` y los dos archivos de `referencias/`.
2. Adjunta el plano (DXF o ZIP) y los demás insumos.
3. Pega el mensaje de abajo.

## Opción C — En Claude Code con el repositorio
El repositorio ya tiene el skill `planteamiento-cunetas-terreno` y la implementación completa de Barranquita en
`herramientas/barranquita/`. Abre una sesión en la rama de trabajo y pega el mensaje de abajo; el chat lee `CLAUDE.md` solo.

---

## Mensaje para pegar en el chat nuevo (completa lo que está entre [ ])

```
Hola. Necesito el planteamiento de drenaje pluvial con cunetas de este proyecto, con el mismo método y criterios del skill
"planteamiento-drenaje-pluvial". Lee primero SKILL.md y las referencias.

Proyecto: [nombre completo del proyecto]
CUI / código de inversión: [CUI]
Ubicación: [distrito, provincia, región]
Entidad: [p. ej. Gobierno Regional San Martín - Gerencia Territorial Bajo Mayo]
Tipo de local: [colegio / CAR / hogar / posta / otro]

Adjunto:
- Plano general en DXF (o ZIP en partes) con curvas de nivel, cerco, edificaciones, techos, veredas, áreas verdes y NPT.
- [Si tengo] mis líneas de ejes de cuneta en la capa [nombre/color].
- [Si tengo] serie Pmax 24 h de la estación [nombre, código SENAMHI].
- [Si tengo] foto o vista aérea para las carátulas.

Reglas: todo en español; entregables en Word, Excel y DXF a escala real (1 unidad = 1 m); vistas previas en PNG; decir
"cota de fondo"; nombre y CIP del proyectista en blanco; nada que revele uso de IA; todo dentro del cerco y el agua sale por
pases en el cimiento; cuneta bajo cada caída de techo (dos aguas a ambos lados); cuneta 0.60 total = muros 0.10 + 0.40 libre,
h inicial 0.30, S 0.5 %, borde al ras del piso; quiebres a 45°; FS 1.15; 11 comprobaciones hasta 11 de 11.

Primero muéstrame una imagen de control con el cerco, los niveles, los techos y las descargas que propones, y pregúntame lo
que no esté claro antes de diseñar. Luego: red de cunetas, cotas de fondo, verificación, láminas (planta, perfiles,
secciones, una lámina por descarga), memoria hidrológica, memoria descriptiva, especificaciones técnicas, memoria de cálculo,
análisis estadístico y metrado en formato Delphin.
```
