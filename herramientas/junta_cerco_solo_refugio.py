"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): partida 01.04.04.06.02 JUNTA E=1" CON TECNOPOR Y SELLADOR
ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO = solo la junta LONGITUDINAL entre el muro del colector y el cimiento del cerco,
en todo el tramo pegado al cerco (0+000.00 a 0+058.81). Al otro lado del colector hay terreno natural (sin vereda ni piso):
no lleva junta. Reemplaza el criterio anterior (borde de la losa con piso adyacente).

COLECTOR JUNTAS Y EMPALMES: fila 16 = nota del lado opuesto (0 m); filas 17 y 18 (cajas CL y CC) quedan vacias.
ACU JUNTA CERCO: el borde de losa queda en 0 (la plancha de 0.90 m es el unico tecnopor de la partida).
Edicion directa del XML; PLANILLA GENERAL, RESUMEN, COLECTOR INSUMOS y la ACU se recalculan.
Uso: python3 herramientas/junta_cerco_solo_refugio.py <planilla.xlsx>
"""
import sys, os, re
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular

CJ, AJ = "COLECTOR JUNTAS Y EMPALMES", "ACU JUNTA CERCO"


def vaciar(L, nom, ref):
    x = L.hoja(nom); m = L.celda(nom, ref); assert m, ref
    s = re.search(r' s="(\d+)"', m.group(0)); s = ' s="%s"' % s.group(1) if s else ""
    L.x[nom] = x[:m.start()] + '<c r="%s"%s/>' % (ref, s) + x[m.end():]


def cambiar(f):
    L = Libro(f)
    assert L.leer(CJ, "B17").startswith("Borde de la losa"), "la planilla ya fue modificada"
    L.texto(CJ, "A7", "Lamina DP-01 (nota 5), DP-03, DP-06C y DD-03. Junta de dilatacion de 1\" cada 4.00 m en todo el perimetro de la seccion (tecnopor de 1\" en todo el perimetro "
                      "+ sellador asfaltico RC-250 con arena de 1\" x 2\" en la cara expuesta, EG-2013 MTC). Junta longitudinal de tecnopor de 1\" con sellador asfaltico entre el muro del "
                      "colector y el cimiento del cerco, en todo el tramo pegado al cerco; al otro lado hay terreno natural (sin vereda ni piso) y no lleva junta. Empalme de cada cuneta "
                      "por ventana en el muro lado predio con caida libre al fondo (sin dintel adicional).")
    L.texto(CJ, "B15", "Junta longitudinal contra el cimiento del cerco (tramo pegado al cerco, 0+000 al primer quiebre)")
    L.texto(CJ, "G15", "DP-01, DP-04 y DD-03 C: junta entre el muro lado predio y el cimiento del cerco (h = 0.90)")
    L.texto(CJ, "B16", "Lado opuesto al cerco (colector y cajas CL y CC): terreno natural, sin vereda ni piso: no lleva junta")
    L.texto(CJ, "C16", "-"); L.num(CJ, "D16", 0); L.texto(CJ, "G16", "DP-04 y DD-03 D")
    for r in (17, 18):
        for c in "ABCDEFG": vaciar(L, CJ, "%s%d" % (c, r))
    L.texto(CJ, "A19", "TOTAL JUNTA LONGITUDINAL CON EL CERCO (m)")
    L.texto(AJ, "A7", "Partida de Delphin 01.04.04.06.02 JUNTA E=1\" CON TECNOPOR Y SELLADOR ASFALTICO ENTRE COLECTOR Y CERCO PERIMETRICO (metrado 01.04.04.06.02, hoja COLECTOR "
                      "JUNTAS Y EMPALMES). Cantidades de la lamina DD-03: junta longitudinal con plancha de tecnopor de 1\" de 0.90 m de altura contra el cimiento del cerco, en todo el "
                      "tramo pegado al cerco, con sellador asfaltico 1\" x 2\" (RC-250 + arena) en la cara superior. Al otro lado hay terreno natural: no lleva junta. "
                      "Celda amarilla = dato; verde = formula. Precios sin IGV.")
    L.texto(AJ, "B13", "Lado opuesto al cerco: terreno natural, sin junta")
    L.formula(AJ, "D13", "'%s'!F16" % CJ)
    L.texto(AJ, "B14", "Altura de plancha en el lado opuesto (no aplica)"); L.num(AJ, "D14", 0)
    L.texto(AJ, "H13", "COLECTOR JUNTAS Y EMPALMES fila 16 (0 m)")
    L.guardar(f)
    return recalcular(f, list(L.ruta))


if __name__ == "__main__":
    print("celdas recalculadas:", cambiar(sys.argv[1]))
