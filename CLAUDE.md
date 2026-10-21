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
  El método es estándar para cualquier tipo de obra en el Perú (no solo vial o CAR). Cada tema en su carpeta: `PROGRAMA DE ELABORACION DE PSST/` (programa general, sin proyectos de ejemplo) y `gestion_riesgos/`.

## Proyectos
| Proyecto | Responsable | CUI | Colector | Carpeta de entregables | Generador |
|---|---|---|---|---|---|
| CAR Varones | Katiuska | 2705619 | b 0.60, muros 0.15, 11 registros | `entregables_varones/` | `herramientas/varones/` (`planos_v.py`, `compat.py`, `diseno_v.py`) |
| Hogar de Refugio Temporal "Mujeres Violentadas" | Solange | 2675514 | b 0.80, muros 0.15, 10 registros | `entregables/` y `entregables_solange/` | `herramientas/diseno.py`, `planos_dxf.py`, `memoria_*.py`, `metrado_*.py` |
| CAR Mujeres | Wilma | 2717013 | b 1.50, muros 0.10, 15 registros | `entregables_mujeres/` | `herramientas/mujeres/` (`datos_m.py`, `planos_m.py`, `memoria_descriptiva_m.py`) – **metrado congelado** |
| I.E. N.° 0590 Barranquita (Lamas) – planteamiento preliminar de cunetas | – | C.I. 468901 (confirmar CUI) | cunetas 0.60 (muros 0.10, libre 0.40), h inicial 0.30, S 0.5 %; borde de cuneta +184.65 al ras del NPT (área verde +184.60; al ras del patio de maniobra +184.50); acero solo con h ≥ 0.40 o tapada | `entregables_barranquita/` | `herramientas/barranquita/` (`diseno_b.py`, `verifica_b.py`, `calcula_b.py`, `planos_b.py`, `planta_cunetas_b.py`, `perfiles_b.py`, `descargas_b.py`, `excel_b.py`, `hidrologia_b.py`, `lluvia_datos_b.py`, `cantidades_b.py`, `metrado_b.py`, `memoria_calculo_b.py`, `memorias_b.py`, `espec_b.py`) – todo dentro del cerco, ejes = lineas magenta del usuario |
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
- `herramientas/barranquita/`: I.E. 0590 Barranquita. Base del sitio en `insumos/barranquita/base_sitio.pkl` (extraída del DXF
  PLANTA_GENERAL_590_2 de 332 MB, que no se versiona; la copia real del sitio es la que está sobre las curvas C-TOPO, en UTM).
  `python3 herramientas/barranquita/calcula_b.py && python3 herramientas/barranquita/planos_b.py && python3 herramientas/barranquita/excel_b.py`
  (calcula_b: ciclo diseno <-> verificacion de 11 comprobaciones; planta_cunetas_b: cunetas en planta a escala real (rejilla celeste,
  tapada verde, flechas rojas, tapas de inspeccion; requiere shapely); cortes_b: cortes generales; descargas_b: una lamina 1/25 por
  descarga con planta, perfil e isometrico; iso_b ya no se usa: el usuario no quiere el 3D de toda la red). Quiebres a 45 grados en planta
  (chaflanes de 0.60 m en cada esquina, `diseno_b.chaflanes`), no se muestran en perfiles. Area de intervencion = dentro del cerco perimetrico (`diseno_b.CERCO`, confirmado por
  el usuario): ninguna cuneta sale del cerco; el agua sale por pase en el cimiento (D1 a D4; sin pozas).
  Expediente de drenaje (Word/Excel): `hidrologia_b.py` (serie Pmax 24 h de la estacion Pongo de Caynarachi SENAMHI 003317, 25 anios 1989-2013, sin
  transposicion; Gumbel T = 25: P24 166.64 mm, Dick-Peschke, I = 288.63 mm/h; Tarapoto transpuesta x 2.21 solo como contraste; `lluvia_datos_b.py` lee datos diarios SENAMHI / NASA POWER / CHIRPS de
  `insumos/barranquita/lluvia/` y compara sin modificar el diseno), `metrado_b.py`, `memoria_calculo_b.py`, `memorias_b.py` (memoria hidrologica y
  descriptiva), `espec_b.py`. Sin `base_sitio.pkl`: `verifica_b.py --solo-lluvia` (cambio de lluvia sobre la geometria vigente) y caches
  `_calc/coberturas.json` (areas de techo) y `_calc/junta_piso.json` (junta con el piso por eje); los planos (`planos_b.py`) si necesitan la base.
  Regenerar con `python3 herramientas/barranquita/metrado_b.py && ... memoria_calculo_b.py && memorias_b.py && espec_b.py`.
  Ejes de cuneta (v3): lineas magenta del plano "PLANTA_GENERAL_590 ULTIMA VERSION" (lados de cada bloque, techos a dos aguas),
  copiadas en `insumos/barranquita/cunetas_magenta_usuario.json`; la base del sitio (`base_sitio.pkl`) es de esa version.
- `gestion_riesgos/`: estudios de gestión de riesgos durante la ejecución de obra, separados de los colectores. `herramientas/` (generadores, con copia propia de `dxf_base.py`, `dxf_layouts.py`, `dxf_render.py`) y `proyectos/<proyecto>/insumos` y `proyectos/<proyecto>/entregables`. Ver `gestion_riesgos/README.md`.
- `PROGRAMA DE ELABORACION DE PSST/`: programa general del Plan de Seguridad y Salud en el Trabajo para todo tipo de obra (IPERC R.M. 050-2013-TR,
  Word y Excel). `herramientas/` (`biblioteca.py`, `importar_s10.py`, `generar.py`), `plantilla/DATOS_PROYECTO.xlsx`, `proyectos/<obra>/`,
  `GENERAR_PSST.bat`. Ver su `README.md` y el skill `psst-iperc`.

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
