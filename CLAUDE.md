# Proyecto: drenaje pluvial y colectores frontales – predio Los Mangos, Morales (San Martín)

Leer completo antes de trabajar. Detalle técnico en los skills de `.claude/skills/` y en `BITACORA_CONVERSACION.md`.

## Reglas permanentes del usuario (no negociables)
- No modificar los metrados del usuario salvo pedido expreso; cambiar solo lo que se pida y verificar que lo demás quede idéntico.
- Entregables en Word, Excel y DXF; vistas previas en PNG. PDF solo cuando el usuario lo pida.
- Escala real: 1 unidad = 1 m. "Si algo mide 0.56, así debe medir en el plano."
- Decir siempre "cota de fondo". Citar los proyectos por nombre y CUI.
- Nada en los documentos que revele uso de IA. No poner nombre ni CIP del proyectista (campos en blanco).
- Partidas con nombres y estructura Delphin (base: CAR Mujeres); cantidades siempre del metrado propio.
- Precios reales con su fuente; mano de obra CAPECO-FTCCP 2026 (operario 28.95, oficial 22.68, peón 20.54).
- Todo en español. Actualizar todo lo relacionado de forma coherente (metrado ↔ planos ↔ especificaciones ↔ memoria).
- No mezclar partidas ni láminas entre proyectos.
- Estudios de gestión de riesgos de obra: sin montos en soles ni "observaciones" a documentos ajenos; efectos en % del presupuesto.
- PSST y gestión de riesgos: siempre con su matriz (IPERC o matriz de riesgos) en Excel con fórmulas y un Word ordenado con tablas y gráficos.
  El método es estándar para cualquier tipo de obra en el Perú (no solo vial o CAR). Cada tema en su carpeta: `seguridad_salud_trabajo/` y `gestion_riesgos/`.

## Proyectos
| Proyecto | Responsable | CUI | Colector | Carpeta de entregables | Generador |
|---|---|---|---|---|---|
| CAR Varones | Katiuska | 2705619 | b 0.60, muros 0.15, 11 registros | `entregables_varones/` | `herramientas/varones/` (`planos_v.py`, `compat.py`, `diseno_v.py`) |
| Hogar de Refugio Temporal "Mujeres Violentadas" | Solange | 2675514 | b 0.80, muros 0.15, 10 registros | `entregables/` y `entregables_solange/` | `herramientas/diseno.py`, `planos_dxf.py`, `memoria_*.py`, `metrado_*.py` |
| CAR Mujeres | Wilma | 2717013 | b 1.50, muros 0.10, 15 registros | `entregables_mujeres/` | `herramientas/mujeres/` (`datos_m.py`, `planos_m.py`) – **metrado congelado** |
| Vía SM-107 Tingo de Ponasa – Shamboyacu (PSST) | – | 2673852 | (plan de seguridad y salud en el trabajo) | `seguridad_salud_trabajo/proyectos/SM-107_TINGO_DE_PONASA_SHAMBOYACU/` | `seguridad_salud_trabajo/herramientas/` (`generar.py`) |
| Vía SM-107 Tingo de Ponasa – Shamboyacu | – | 2673852 | (estudio de gestión de riesgos de obra) | `gestion_riesgos/proyectos/SM-107_TINGO_DE_PONASA_SHAMBOYACU/` | `gestion_riesgos/herramientas/` |

Cadena hidráulica: Varones (0.60) → caja de llegada CL → Refugio (0.80) → caja de caída CC → R-01 del CAR Mujeres (1.50) → salida.

## Mapa del repositorio
- `insumos/`: archivos del usuario (no se editan; las versiones vigentes en `insumos/metrados_vigentes/` y `insumos/solange/vigente/`).
- `herramientas/`: todos los generadores (Python). Todo cambio se hace en el generador y se regenera; nunca a mano en el DXF/XLSX final.
  - Diseño y cálculo: `diseno.py` (Refugio), `metrado_calc.py`, `memoria_xlsx.py` (memoria de cálculo Excel), `memoria_docx.py` (capítulo en el Word de hidrología).
  - Planos: `dxf_base.py` (estilo, capas, rótulo, llamadas, tablas), `dxf_planta.py`, `dxf_secciones.py`, `dxf_cajas_iso.py`, `dxf_cuadros.py`, `dxf_detalles.py`, `dxf_layouts.py` (presentaciones AutoCAD e índice), `dxf_render.py` (vista previa PNG).
  - Tapa de registro: `render_tapa/` (`dxf_tapa_ciega.py` DP-06B, `dxf_tapa_3d.py` DP-06D, `modelo.py`, `iso.py`, `foto.py`), `tapa_ciega.py` (parche de planillas).
  - Especificaciones: `especificaciones/espec.py` → `_json/` → `node docx_espec.js <json> <docx>`.
  - Edición de planillas sin romper formato: `angulo_contramarco_refugio.Libro` (XML) + `recalcular()` con LibreOffice.
- `.claude/skills/`: `diseno-colector-pluvial` (criterios y decisiones de diseño), `planos-ordenados` (dibujo sin cruces), `metrado-cunetas`, `psst-iperc` (plan de seguridad y salud en el trabajo).
- `MetraP/`: programa de metrados (ejecutable Windows con `build_exe.bat`).
- `gestion_riesgos/`: estudios de gestión de riesgos durante la ejecución de obra, separados de los colectores. `herramientas/` (generadores, con copia propia de `dxf_base.py`, `dxf_layouts.py`, `dxf_render.py`) y `proyectos/<proyecto>/insumos` y `proyectos/<proyecto>/entregables`. Ver `gestion_riesgos/README.md`.
- `seguridad_salud_trabajo/`: programa estándar del Plan de Seguridad y Salud en el Trabajo (IPERC R.M. 050-2013-TR, Word y Excel) para cualquier obra.
  `herramientas/biblioteca.py` (actividades, peligros y controles), `importar_s10.py`, `generar.py`; `proyectos/<proyecto>/insumos/DATOS_PROYECTO.xlsx`.
  Ver `seguridad_salud_trabajo/README.md` y el skill `psst-iperc`.

## Cómo regenerar (Hogar de Refugio)
```
python3 herramientas/diseno.py            # diseño hidráulico -> entregables/_calc/diseno.json
python3 herramientas/memoria_xlsx.py      # memoria de cálculo
python3 herramientas/planos_dxf.py        # juego de planos DP/DA/DD
python3 herramientas/dxf_render.py <dxf> <png> x0 y0 x1 y1 110 color   # vista previa (caja de entregables/_calc/laminas.json)
```
CAR Varones: `python3 herramientas/varones/planos_v.py`. CAR Mujeres: `python3 herramientas/mujeres/planos_m.py`.
DP-06B suelta: `python3 herramientas/render_tapa/dxf_tapa_ciega.py <salida.dxf> <refugio|varones|mujeres>` (render: 0 0 841 594).

## Git
Rama de trabajo: `claude/colector-pluvial-hogar-refugio-ydbnaf`. Commit con mensaje claro y push con
`git push -u origin claude/colector-pluvial-hogar-refugio-ydbnaf`. No crear PR salvo pedido.
