"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): costo de la hora-hombre 2026 en todas las ACU de la planilla.

Hoja nueva COSTO HORA HOMBRE 2026:
- jornal basico 2026 del regimen de construccion civil (R.M. 197-2025-TR, El Peruano 19/12/2025; tabla salarial 2026 de la
  FTCCP): operario 89.30, oficial 69.75, peon 62.80 por dia;
- costo hora-hombre CAPECO del periodo 2024-2025 (jornales 86.80 / 68.10 / 61.30): 28.48 / 22.41 / 20.29, que incluye leyes y
  beneficios sociales, BUC (32 % operario, 30 % oficial y peon), movilidad y ropa de trabajo;
- costo 2026 = costo 2024-2025 x (jornal 2026 / jornal 2024-2025): se mantiene la misma estructura de beneficios sobre el
  jornal vigente. Cuando CAPECO publique su tabla 2026 basta cambiar las celdas amarillas.
Las ACU TAPA REGISTRO, CANALETAS, JUNTA DILATACION y JUNTA CERCO leen de esta hoja (la ACU LLORADEROS se agrega despues).
Edicion directa del XML (conserva formato e imagenes). Uso: python3 herramientas/mano_obra_2026_refugio.py <planilla.xlsx>
"""
import sys, os
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular
from acu_juntas_refugio import Hoja, encabezado, agregar_hoja

HOJA = "COSTO HORA HOMBRE 2026"
HH = "'%s'!" % HOJA
CAT = [("Operario", 86.80, 28.48, 89.30), ("Oficial", 68.10, 22.41, 69.75), ("Peon", 61.30, 20.29, 62.80)]
F_JB = "R.M. 197-2025-TR (El Peruano, 19/12/2025) y tabla salarial 2026 FTCCP: jornal basico desde el 01/01/2026"
F_HH = "CAPECO: tabla de costo hora-hombre pliego 2024-2025 (jornales 86.80 / 68.10 / 61.30)"
TXT = "hoja COSTO HORA HOMBRE 2026 (CAPECO, jornal R.M. 197-2025-TR)"


def construir(f):
    L = Libro(f)
    assert HOJA not in L.ruta, "la hoja ya existe"
    plantilla = L.hoja("ACU TAPA REGISTRO")
    H = Hoja(L, 284)
    encabezado(H, "COSTO DE LA HORA-HOMBRE 2026 - REGIMEN DE CONSTRUCCION CIVIL",
               "Costo de la hora-hombre que usan todas las ACU de la planilla. Jornal basico 2026: R.M. 197-2025-TR (convenio CAPECO - FTCCP). El costo hora-hombre de CAPECO "
               "(jornal + leyes y beneficios sociales + BUC + movilidad + ropa de trabajo) se lleva al jornal 2026 con la misma estructura: costo 2026 = costo 2024-2025 x "
               "jornal 2026 / jornal 2024-2025. Celda amarilla = dato; verde = formula. Cuando CAPECO publique la tabla 2026 se cambian solo las celdas amarillas.", plantilla)
    H.banda("1. COSTO HORA-HOMBRE POR CATEGORIA (S/ por hora)", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "CATEGORIA", "JORNAL 2024-2025 (S/ dia)", "COSTO HH CAPECO 2024-2025",
                                                      "FACTOR HH / JORNAL", "JORNAL BASICO 2026 (S/ dia)", "COSTO HH 2026 (S/ hh)", "FUENTE"))], 45)
    filas = {}
    for i, (cat, jb0, hh0, jb1) in enumerate(CAT, 1):
        r = H.r + 1
        H.fila([("A", 283, i), ("B", 149, cat), ("C", 289, jb0), ("D", 289, hh0), ("E", 306, "=D%d/C%d" % (r, r)), ("F", 289, jb1),
                ("G", 290, "=ROUND(E%d*F%d,2)" % (r, r)), ("H", 149, "Jornal 2026: R.M. 197-2025-TR (FTCCP). Costo HH: tabla CAPECO 2024-2025")], 45)
        filas[cat] = r
    H.banda("2. COMPONENTES QUE INCLUYE EL COSTO HORA-HOMBRE (estructura CAPECO)", salto=1)
    for i, t in enumerate(["Jornal basico por 8 horas de labor (operario, oficial y peon).",
                           "Leyes y beneficios sociales sobre el jornal basico (descanso dominical, feriados, vacaciones, gratificaciones, CTS, ESSALUD y otros), segun la tabla CAPECO.",
                           "Bonificacion unificada de construccion (BUC): 32 % del jornal del operario y 30 % del oficial y del peon.",
                           "Bonificacion por movilidad acumulada (S/ 8.60 por dia en la tabla FTCCP 2026) y ropa de trabajo.",
                           "No incluye horas extras, trabajo en altura ni bonificacion por alta especializacion (no se usan en estas partidas)."], 1):
        r = H.fila([("A", 283, i), ("B", 149, t)] + [(k, 149, None) for k in "CDEFGH"], 31.5); H.merges.append("B%d:H%d" % (r, r))
    agregar_hoja(L, HOJA, H.xml(plantilla))
    G = {c: "=%s$G$%d" % (HH, r) for c, r in filas.items()}
    # ---- ACU que leen la hora-hombre
    AT, AC = "ACU TAPA REGISTRO", "ACU CANALETAS"
    for ref, cat in (("69", "Operario"), ("70", "Oficial"), ("71", "Peon")):
        assert L.leer(AT, "B" + ref) == cat, (AT, ref)
        L.formula(AT, "F" + ref, G[cat][1:]); L.texto(AT, "H" + ref, TXT)
    for r0 in (31, 51, 71, 91):
        assert L.leer(AC, "B%d" % r0).startswith("Operario") and L.leer(AC, "B%d" % (r0 + 1)) == "Peon", (AC, r0)
        L.formula(AC, "F%d" % r0, G["Operario"][1:]); L.formula(AC, "F%d" % (r0 + 1), G["Peon"][1:])
        L.texto(AC, "H%d" % r0, TXT); L.texto(AC, "H%d" % (r0 + 1), TXT)
    for h in ("ACU JUNTA DILATACION", "ACU JUNTA CERCO"):
        assert L.leer(h, "B34") == "Operario" and L.leer(h, "B35") == "Peon", h
        L.formula(h, "F34", G["Operario"][1:]); L.formula(h, "F35", G["Peon"][1:]); L.texto(h, "H34", TXT); L.texto(h, "H35", TXT)
    L.guardar(f)
    return recalcular(f, list(L.ruta))


if __name__ == "__main__":
    print("celdas recalculadas:", construir(sys.argv[1]))
