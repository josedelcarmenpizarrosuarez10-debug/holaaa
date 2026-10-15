"""CAR Varones (CUI 2705619): registro de limpieza sobre un colector de b = 0.60, mas angosto que la abertura de 0.70.
En los lados largos la abertura cae sobre la cabeza de los muros (asiento del contramarco); el borde engrosado 0.15 x 0.10
solo existe en los 2 lados transversales, entre muros: perimetro 2 x 0.60 = 1.20 m (antes 3.00 m copiado del Hogar de
Refugio, cuyo colector de 0.80 si deja engrosado en los 4 lados). Concreto del colector 56.02 -> 55.72 m3.
El refuerzo de borde mantiene L = 1.40 (las barras transversales llevan ganchos de 0.29 dentro de los muros).
Uso: python3 herramientas/varones/registro_sobre_muros_v.py   (una sola vez; no repite cambios)
"""
import os, sys, shutil
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
sys.path.insert(0, HERR)
from angulo_contramarco_refugio import Libro, recalcular

F = os.path.join(RAIZ, "entregables_varones", "METRADO_DRENAJE_PLUVIAL_CAR_VARONES_CON_COLECTOR.xlsx")
COPIA = os.path.join(RAIZ, "insumos", "metrados_vigentes", "METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx")
PA, CC, RT, PG = "COLECTOR PARAMETROS", "COLECTOR CONCRETO", "COLECTOR REGISTROS Y TAPAS", "PLANILLA GENERAL DE METRADOS"

L = Libro(F)
assert L.leer(PA, "C40") in (3, 3.0, "3"), "ya aplicado"
L.texto(PA, "B40", "Borde engrosado de la abertura: perimetro (solo los 2 lados transversales, entre muros)")
L.formula(PA, "C40", "2*C10")
L.texto(PA, "E40", "Lamina DP-06B: 2 x b; b = 0.60 es menor que la abertura de 0.70, en los lados largos el asiento es la cabeza del muro")
L.texto(CC, "A15", "REGISTROS DE LIMPIEZA EN LA LOSA DEL COLECTOR - lamina DP-06B (borde engrosado 0.15 x 0.10 solo en los 2 lados transversales, entre muros: "
        "en los lados largos la abertura apoya en la cabeza de los muros; descuento de la abertura 0.70 x 0.70 en la losa superior)")
L.texto(CC, "B17", "Registros RV-01 a RV-11: borde engrosado de la abertura (2 lados, entre muros)")
L.texto(CC, "N17", "DP-06B, DD-01: 2 x 0.60 m por registro, en los 11 registros")
L.texto(RT, "A7", "Lamina DP-01 (ubicacion), DP-06B, DP-06D, DD-01 y DD-02 (detalle): contramarco L 1 1/2\"x1 1/2\"x1/8\" anclado a la losa y a la cabeza de los muros, "
        "marco L 1 1/2\"x1 1/2\"x1/8\" soldado a la tapa, tapa de concreto armado 0.68 x 0.68 x 0.08 con parrilla 3/8\" @0.10 y asas; abertura de 0.70 x 0.70 "
        "sobre el colector de 0.60: en los lados largos apoya en la cabeza de los muros y el borde engrosado 0.15 x 0.10 va solo en los 2 lados transversales. "
        "El registro de la caja CL pertenece al expediente del Hogar de Refugio.")
L.texto(PG, "B188", "Bordes engrosados de abertura de registros RV-01 a RV-11 (2 lados, entre muros)")
L.guardar(F)
n = recalcular(F, [PA, CC, PG, "RESUMEN", "COLECTOR INSUMOS", "DESAGREGADO TAPA REGISTRO", "ACU TAPA REGISTRO"])
shutil.copyfile(F, COPIA)
print("celdas recalculadas:", n)
