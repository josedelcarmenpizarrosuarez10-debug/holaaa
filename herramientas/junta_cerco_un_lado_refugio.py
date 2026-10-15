"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): partida 01.04.04.06.02, junta de tecnopor y sellador en el
borde de la losa con el piso adyacente a UN SOLO LADO (lado via). Al lado predio esta el cerco perimetrico, que ya tiene su
junta de 0.90 m (fila 15); alli no hay piso que separar.

COLECTOR JUNTAS Y EMPALMES filas 16 a 18 (colector, caja CL y caja CC): veces 2 -> 1. La ACU JUNTA CERCO, COLECTOR INSUMOS,
PLANILLA GENERAL y RESUMEN leen estas filas por formula; se recalculan los valores en cache.
Edicion directa del XML (conserva formato e imagenes).
Uso: python3 herramientas/junta_cerco_un_lado_refugio.py <planilla.xlsx>
"""
import sys, os
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular

CJ = "COLECTOR JUNTAS Y EMPALMES"


def cambiar(f):
    L = Libro(f)
    assert L.leer(CJ, "D16") == "2", "la planilla ya fue modificada"
    L.texto(CJ, "B16", "Borde de la losa con el piso adyacente: colector (un lado, lado via; al lado predio esta el cerco)")
    L.formula(CJ, "C16", "\"1 x 0+\"&TEXT('COLECTOR PARAMETROS'!$C$64,\"000.00\")")
    L.num(CJ, "D16", 1)
    L.texto(CJ, "G16", "DP-04 y DD-03 D: junta de tecnopor en el borde de la losa superior, lado via")
    for r, caja in ((17, "CL"), (18, "CC")):
        L.texto(CJ, "B%d" % r, "Borde de la losa con el piso adyacente: caja %s (un lado, lado via)" % caja)
        L.texto(CJ, "C%d" % r, "1 x (largo exterior + 0.30)")
        L.num(CJ, "D%d" % r, 1)
    L.cambiar(CJ, "A7", "y entre el borde de la losa y el piso adyacente.", "y entre el borde de la losa y el piso adyacente (un solo lado, lado via).")
    L.cambiar("ACU JUNTA CERCO", "A7", "de 0.10 m en el borde de la losa con el piso adyacente,", "de 0.10 m en el borde de la losa con el piso adyacente (un solo lado, lado via),")
    L.texto("ACU JUNTA CERCO", "B13", "Junta en el borde de la losa con el piso adyacente, un lado (colector y cajas CL y CC)")
    L.guardar(f)
    return recalcular(f, list(L.ruta))


if __name__ == "__main__":
    print("celdas recalculadas:", cambiar(sys.argv[1]))
