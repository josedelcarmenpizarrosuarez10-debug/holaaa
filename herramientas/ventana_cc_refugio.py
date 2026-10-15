"""Hogar de Refugio (CUI 2675514): la ventana de salida de la caja de caida CC hacia el R-01 del CAR Mujeres (CUI 2717013)
mide 1.50 x 0.43, el alto interior del colector receptor en su R-01 (losa 259.25 - 0.10 - fondo 258.72). La planilla
descontaba 1.50 x 0.842 (NA + 0.50 - fondo), una ventana que habria pasado por encima del piso del CAR Mujeres.
Concreto del colector y cajas: 58.31 -> 58.41 m3. Uso: python3 herramientas/ventana_cc_refugio.py (una sola vez)
"""
import os, sys, shutil
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular

F = os.path.join(RAIZ, "insumos", "metrados_vigentes", "METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx")
COPIA = os.path.join(RAIZ, "entregables", "METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx")
CC, PG = "COLECTOR CONCRETO", "PLANILLA GENERAL DE METRADOS"
L = Libro(F)
assert "+0.5-" in L.celda(CC, "F38").group(0), "ya aplicado"
L.texto(CC, "B38", "Caja de caida CC: descuento ventana de salida (alto = interior del R-01 del CAR Mujeres: losa 259.25 - 0.10 - fondo)")
L.formula(CC, "F38", "259.25-0.1-'COLECTOR PARAMETROS'!$C$56")
L.guardar(F)
n = recalcular(F, [CC, PG, "RESUMEN", "COLECTOR INSUMOS"])
shutil.copyfile(F, COPIA)
print("celdas recalculadas:", n)
