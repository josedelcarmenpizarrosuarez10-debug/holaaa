"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): costo de la hora-hombre 2026 en todas las ACU de la planilla.

Hoja COSTO HORA HOMBRE 2026 con la tabla oficial CAPECO - FTCCP "Remuneracion y condiciones de trabajo en construccion civil
2026" (Acta final de negociacion colectiva, Exp. N 339-2025-MTPE/2.14-NC), costo hora-hombre en edificacion del 01.01.2026
al 31.12.2026:
  1 remuneracion basica 89.30 / 69.75 / 62.80;  2 leyes y beneficios sociales sobre el jornal basico 112.20 %;
  3 BUC 32 % / 30 % / 30 %;  4 leyes sociales sobre el BUC 12.25 %;  5 seguro de vida ESSALUD + Vida S/ 0.16;
  6 fondo de capacitacion 0.40 / 0.31 / 0.28;  7 movilidad S/ 8.60;  8 overol (2 x S/ 132.80) / 300 = S/ 0.89.
  Total por dia de 8 horas 231.62 / 181.46 / 164.34; costo HH 28.95 / 22.68 / 20.54.
El resumen (filas 11 a 13, columna G) es lo que leen las ACU TAPA REGISTRO, CANALETAS, JUNTA DILATACION, JUNTA CERCO y
LLORADEROS. Si la hoja ya existe se reemplaza su contenido (las referencias de las ACU se mantienen).
Edicion directa del XML (conserva formato e imagenes). Uso: python3 herramientas/mano_obra_2026_refugio.py <planilla.xlsx>
"""
import sys, os
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular
from acu_juntas_refugio import Hoja, encabezado, agregar_hoja

HOJA = "COSTO HORA HOMBRE 2026"
HH = "'%s'!" % HOJA
FUENTE = "Tabla oficial CAPECO - FTCCP 2026 (Exp. N° 339-2025-MTPE/2.14-NC)"
TXT = "hoja COSTO HORA HOMBRE 2026 (tabla oficial CAPECO - FTCCP 2026)"
JB = (89.30, 69.75, 62.80)
PCT = [  # concepto, % sobre jornal basico, % sobre BUC
    ("1.01 Indemnizacion por tiempo de servicios", 12.00, None), ("1.01 Indemnizacion por participacion de utilidades", 3.00, None),
    ("1.02 SCTR: prestaciones asistenciales (Ley 26790)", 1.30, 1.30), ("1.02 SCTR: prestaciones economicas", 1.05, 1.05),
    ("1.04 Regimen de prestaciones de salud (ESSALUD)", 9.00, 9.00), ("1.05 Seguro de vida ley", 0.90, 0.90),
    ("2.01 Salario dominical", 17.58, None), ("2.02 Vacaciones record (30 dias)", 10.00, None),
    ("2.03 Gratificacion por Fiestas Patrias y Navidad", 22.22, None), ("2.04 Jornales por dias feriados no laborables", 4.33, None),
    ("2.05 Asignacion escolar (promedio 3 hijos)", 25.00, None),
    ("3.01 ESSALUD sobre salario dominical (9 % de 17.58 %)", 1.58, None), ("3.02 ESSALUD sobre vacaciones (9 % de 10.00 %)", 0.90, None),
    ("3.03 ESSALUD sobre feriados (9 % de 4.33 %)", 0.39, None),
    ("4.01 SCTR sobre salario dominical (2.35 % de 17.58 %)", 0.41, None), ("4.02 SCTR sobre vacaciones (2.35 % de 10.00 %)", 0.24, None),
    ("4.03 SCTR sobre feriados (2.35 % de 4.33 %)", 0.10, None),
    ("5.01 Seguro de vida ley sobre salario dominical (0.90 % de 17.58 %)", 0.16, None), ("5.02 Seguro de vida ley sobre feriados (0.90 % de 4.33 %)", 0.04, None),
    ("6.01 Bonificacion extraordinaria Ley 30334 (9 % de 22.22 %)", 2.00, None)]


def hoja_xml(L, plantilla):
    H = Hoja(L, 284)
    encabezado(H, "COSTO DE LA HORA-HOMBRE 2026 - REGIMEN DE CONSTRUCCION CIVIL (TABLA OFICIAL CAPECO - FTCCP)",
               "Costo de la hora-hombre en edificacion del 01.01.2026 al 31.12.2026, segun la tabla oficial elaborada entre CAPECO y la FTCCP (Remuneracion y condiciones de "
               "trabajo en construccion civil 2026, Acta final de negociacion colectiva, Exp. N° 339-2025-MTPE/2.14-NC). El resumen de la parte 1 es el que usan todas las ACU "
               "de la planilla. Celda amarilla = dato de la tabla oficial; verde = formula.", plantilla)
    H.banda("1. COSTO HORA-HOMBRE 2026 POR CATEGORIA (lo usan todas las ACU)", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "CATEGORIA", "JORNAL BASICO (S/ dia)", "TOTAL POR DIA DE 8 h (S/)", None, None, "COSTO HH 2026 (S/ hh)", "FUENTE"))], 33)
    r_res = H.r + 1
    assert r_res == 11, r_res
    r_d = r_res + 5                                    # cabecera de la parte 2
    for i, (cat, col) in enumerate((("Operario", "D"), ("Oficial", "E"), ("Peon", "F")), 1):
        H.fila([("A", 283, i), ("B", 149, cat), ("C", 290, "=%s%d" % (col, r_d + 1)), ("D", 290, "=%s%d" % (col, r_d + 9)), ("E", 295, None), ("F", 295, None),
                ("G", 296, "=%s%d" % (col, r_d + 10)), ("H", 149, FUENTE)], 21)
    H.banda("2. COSTO HORA-HOMBRE EN EDIFICACION DEL 01.01.2026 AL 31.12.2026", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "CONCEPTO", "BASE", "OPERARIO", "OFICIAL", "PEON", None, "SUSTENTO"))], 21)
    r0 = H.r + 1; assert r0 == r_d + 1, (r0, r_d)
    rp = r0 + 13 + len(PCT)                            # fila del total de porcentajes (parte 3)
    filas = [
        ("Remuneracion basica del 01/01/2026 al 31/12/2026", "jornal", [(289, v) for v in JB], "R.M. 197-2025-TR; tabla oficial CAPECO - FTCCP 2026"),
        ("Beneficios y leyes sociales sobre el jornal basico (%)", "=$D$%d" % rp, [(290, "=ROUND(%s%d*$C$%d/100,2)" % (c, r0, r0 + 1)) for c in "DEF"], "parte 3: 112.20 % sobre el jornal basico"),
        ("Bonificacion unificada de construccion (BUC)", "32/30/30 %", [(290, "=ROUND(D%d*0.32,2)" % r0), (290, "=ROUND(E%d*0.30,2)" % r0), (290, "=ROUND(F%d*0.30,2)" % r0)],
         "32 % operario; 30 % oficial y peon"),
        ("Beneficios y leyes sociales sobre el BUC (%)", "=$E$%d" % rp, [(290, "=ROUND(%s%d*$C$%d/100,2)" % (c, r0 + 2, r0 + 3)) for c in "DEF"], "parte 3: 12.25 % sobre el BUC"),
        ("Seguro de vida ESSALUD + Vida (S/ 5.00 por mes)", "dia", [(289, 0.16)] * 3, "tabla oficial"),
        ("Fondo de capacitacion (Exp. N° 339-2025-MTPE/2.14-NC)", "dia", [(289, 0.40), (289, 0.31), (289, 0.28)], "tabla oficial"),
        ("Bonificacion por movilidad (R.M. N° 139-2024-TR)", "dia", [(289, 8.60)] * 3, "S/ 8.60 por dia laborado en todo el pais"),
        ("Overol (R.D. N° 777-87-DR-LIM): (2 x S/ 132.80) / 300", "dia", [(290, "=ROUND(2*132.8/300,2)")] * 3, "tabla oficial")]
    for i, (t, base, vals, s) in enumerate(filas, 1):
        H.fila([("A", 283, i), ("B", 149, t), ("C", 290 if str(base).startswith("=") else 285, base)] + [(c, st, v) for c, (st, v) in zip("DEF", vals)] +
               [("G", 295, None), ("H", 149, s)], 21)
    H.fila([("A", 21, None), ("B", 294, "Total por dia de 8 horas (S/)"), ("C", 295, None)] + [(c, 296, "=SUM(%s%d:%s%d)" % (c, r0, c, r0 + 7)) for c in "DEF"] + [("G", 295, None), ("H", 295, None)], 21)
    H.fila([("A", 21, None), ("B", 294, "Costo de la hora-hombre (S/ hh)"), ("C", 295, None)] + [(c, 296, "=ROUND(%s%d/8,2)" % (c, r0 + 8)) for c in "DEF"] + [("G", 295, None), ("H", 149, "total por dia / 8 horas")], 21)
    H.banda("3. PORCENTAJES DE BENEFICIOS Y LEYES SOCIALES EN EDIFICACION (tabla oficial CAPECO - FTCCP 2026)", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "CONCEPTO", None, "SOBRE JORNAL BASICO (%)", "SOBRE BUC (%)", None, None, "SUSTENTO"))], 33)
    p0 = H.r + 1
    for i, (t, a, b) in enumerate(PCT, 1):
        H.fila([("A", 283, i), ("B", 149, t), ("C", 295, None), ("D", 289, a), ("E", 289 if b is not None else 295, b), ("F", 295, None), ("G", 295, None), ("H", 149, "tabla oficial")], 19.5)
    r = H.fila([("A", 21, None), ("B", 294, "PORCENTAJE TOTAL DE LEYES Y BENEFICIOS SOCIALES"), ("C", 295, None), ("D", 296, "=SUM(D%d:D%d)" % (p0, H.r)), ("E", 296, "=SUM(E%d:E%d)" % (p0, H.r)),
                ("F", 295, None), ("G", 295, None), ("H", 149, "112.20 % y 12.25 %")], 21)
    assert r == rp, (r, rp)
    return H.xml(plantilla)


def construir(f):
    L = Libro(f)
    plantilla = L.hoja("ACU TAPA REGISTRO")
    xml = hoja_xml(L, plantilla)
    if HOJA in L.ruta:
        L.x.pop(HOJA, None); L.F[L.ruta[HOJA]] = xml.encode()
    else:
        agregar_hoja(L, HOJA, xml)
    G = {c: "%s$G$%d" % (HH, r) for c, r in (("Operario", 11), ("Oficial", 12), ("Peon", 13))}
    AT, AC = "ACU TAPA REGISTRO", "ACU CANALETAS"
    for ref, cat in (("69", "Operario"), ("70", "Oficial"), ("71", "Peon")):
        assert L.leer(AT, "B" + ref) == cat, (AT, ref)
        L.formula(AT, "F" + ref, G[cat]); L.texto(AT, "H" + ref, TXT)
    for r0 in (31, 51, 71, 91):
        assert L.leer(AC, "B%d" % r0).startswith("Operario") and L.leer(AC, "B%d" % (r0 + 1)) == "Peon", (AC, r0)
        L.formula(AC, "F%d" % r0, G["Operario"]); L.formula(AC, "F%d" % (r0 + 1), G["Peon"])
        L.texto(AC, "H%d" % r0, TXT); L.texto(AC, "H%d" % (r0 + 1), TXT)
    for h in ("ACU JUNTA DILATACION", "ACU JUNTA CERCO"):
        assert L.leer(h, "B34") == "Operario" and L.leer(h, "B35") == "Peon", h
        L.formula(h, "F34", G["Operario"]); L.formula(h, "F35", G["Peon"]); L.texto(h, "H34", TXT); L.texto(h, "H35", TXT)
    if "ACU LLORADEROS" in L.ruta:
        assert L.leer("ACU LLORADEROS", "B33") == "Operario" and L.leer("ACU LLORADEROS", "B34") == "Peon"
        L.texto("ACU LLORADEROS", "H33", TXT); L.texto("ACU LLORADEROS", "H34", TXT)
    L.guardar(f)
    return recalcular(f, list(L.ruta))


if __name__ == "__main__":
    print("celdas recalculadas:", construir(sys.argv[1]))
