"""CAR Varones (CUI 2705619): laminas DJ-01 a DJ-03 de las cunetas de piso, iguales a las del Hogar de Refugio
(junta de dilatacion en toda la seccion en U, proceso constructivo en isometricos y rejilla movil), con el metrado de
la hoja METRADO JUNTA DE DILATACION de la planilla del CAR Varones (9 ejes) y el rotulo del CAR Varones.
Uso: python3 herramientas/varones/planos_junta_cunetas_v.py
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
for p in (HERR, AQUI):
    if p not in sys.path: sys.path.insert(0, p)
import compat  # noqa: F401  (rotulo del CAR Varones en dxf_base)
import planos_junta_cunetas as PJ

PJ.PLANILLA = os.path.join(RAIZ, "entregables_varones", "METRADO_DRENAJE_PLUVIAL_CAR_VARONES_CON_COLECTOR.xlsx")
PJ.SALIDA = os.path.join(RAIZ, "entregables_varones", "PLANOS_DETALLE_CUNETAS_JUNTA_Y_REJILLA_CAR_VARONES.dxf")

if __name__ == "__main__":
    PJ.construir()
