# Gestión de riesgos durante la ejecución de obra

Carpeta independiente de los proyectos de drenaje pluvial (colectores). Aquí van solo los estudios de
gestión de riesgos en la planificación de la ejecución de obra (Ley N. 32069 y su Reglamento,
D.S. N. 009-2025-EF, art. 156).

## Estructura
```
gestion_riesgos/
├── herramientas/                 generadores (Python)
│   ├── riesgos_sm107.py          registro de riesgos, análisis P x I, VME y Monte Carlo -> _calc/riesgos.json
│   ├── terreno_sm107.py          eje (plano clave PC-01) y terreno (DEM Copernicus GLO-30)
│   ├── matriz_xlsx.py            matriz de riesgos (Excel con fórmulas)
│   ├── plano_riesgos_dxf.py      láminas PR-01 y PR-02 (DXF)
│   ├── figuras_sm107.py          figuras del estudio
│   ├── estudio_docx.py           estudio (Word)
│   ├── fotos_sm107.py            fotos georreferenciadas del inventario vial -> _calc/fotos/ (catálogo con coordenadas)
│   ├── levantamiento_obs_docx.py levantamiento de observaciones (Word aparte)
│   ├── anexos_estudio_docx.py    estudio presentado (insumos/estudio_presentado, sin cambios) + Anexos 3, 4 y 5 al final
│   └── dxf_base.py, dxf_layouts.py, dxf_render.py   estilo de láminas, presentaciones y vista previa PNG
└── proyectos/
    └── SM-107_TINGO_DE_PONASA_SHAMBOYACU/      Vía SM-107 Tingo de Ponasa – Shamboyacu (CUI 2673852)
        ├── insumos/              archivos del usuario (no se editan)
        └── entregables/          Word, Excel, DXF, vistas_previas/ y _calc/ (datos intermedios)
```

## Regenerar (desde la raíz del repositorio)
```
python3 gestion_riesgos/herramientas/terreno_sm107.py <carpeta tif>   # solo si cambia el eje o el DEM
python3 gestion_riesgos/herramientas/riesgos_sm107.py
python3 gestion_riesgos/herramientas/matriz_xlsx.py
python3 gestion_riesgos/herramientas/plano_riesgos_dxf.py
python3 gestion_riesgos/herramientas/figuras_sm107.py
python3 gestion_riesgos/herramientas/estudio_docx.py
python3 gestion_riesgos/herramientas/fotos_sm107.py              # solo si cambian las fotos (requiere LibreOffice)
python3 gestion_riesgos/herramientas/levantamiento_obs_docx.py
python3 gestion_riesgos/herramientas/anexos_estudio_docx.py
```
Vistas previas: `python3 gestion_riesgos/herramientas/dxf_render.py <dxf> <png> x0 y0 x1 y1 110 color`
(cajas en `entregables/_calc/laminas_pr.json`).

## Reglas
- Sin montos en soles: efectos en % del presupuesto de obra.
- Sin "observaciones" a documentos ajenos.
- Un proyecto nuevo va en su propia carpeta `proyectos/<NOMBRE>/` con `insumos/` y `entregables/`.
