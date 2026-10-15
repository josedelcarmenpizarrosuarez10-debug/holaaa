"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): hoja ACU LLORADEROS dentro de la planilla vigente, con el
formato de la ACU TAPA REGISTRO (datos por lloradero + analisis en formato Delphin).

Cantidades por lloradero de la hoja DESAGREGADO LLORADEROS (laminas DL-01 y DL-02): tubo PVC-U 3" de 0.30 m, grava 0.0297 m3,
geotextil 0.594 m2 y mortero 1:3 de 0.0005 m3. Mano de obra de la hoja COSTO HORA HOMBRE 2026; cemento, arena y agua de la
ACU TAPA REGISTRO; tubo, grava y geotextil con precio publicado y su fuente. Precios sin IGV.
Edicion directa del XML (conserva formato e imagenes); no cambia ningun metrado.
Uso: python3 herramientas/acu_lloraderos_refugio.py <planilla.xlsx>
"""
import sys, os
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular
from acu_juntas_refugio import Hoja, encabezado, tabla_datos, acu, agregar_hoja
from desagregado_lloraderos_refugio import amarillo4

HOJA = "ACU LLORADEROS"
DL, AT, HH = "'DESAGREGADO LLORADEROS'!", "'ACU TAPA REGISTRO'!", "'COSTO HORA HOMBRE 2026'!"
TUBO, GRAVA, GEO = 39.90, 70.00, 2300.00          # con IGV: tubo de 3 m, m3 de piedra, rollo de 4 x 100 m
F_TUBO = "Sodimac Peru y Promart: tubo desague PVC 3\" x 3 m liviano Pavco S/ 39.90 con IGV (S/ 11.27 el m sin IGV)"
F_GRAVA = "Agregados Tarapoto (Morales): piedra chancada 3/4\" S/ 70.00 el m3 puesto en obra (precio publicado mas cercano a la grava 20 a 40 mm)"
F_GEO = "Ferropolis Peru: geotextil no tejido 200 g/m2, rollo de 4 x 100 m S/ 2,300.00 (S/ 5.75 el m2 con IGV)"
PARTIDA = "01.04.03.04.03.04 LLORADERO DE TUBERIA PVC Ø3\" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m (CUNETA COLINDANTE CON AREA VERDE)"


def construir(f):
    L = Libro(f)
    assert HOJA not in L.ruta and "DESAGREGADO LLORADEROS" in L.ruta and "COSTO HORA HOMBRE 2026" in L.ruta
    assert L.leer("DESAGREGADO LLORADEROS", "B37").startswith("Tubo PVC") and L.leer("DESAGREGADO LLORADEROS", "B42").startswith("Mortero")
    plantilla = L.hoja("ACU TAPA REGISTRO"); Y4 = amarillo4(L)
    H = Hoja(L, Y4)
    encabezado(H, "ANALISIS DE COSTO UNITARIO - LLORADERO DE TUBERIA PVC Ø3\" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m",
               "Partida de Delphin " + PARTIDA + " (metrado: hojas METRADO LLORADEROS y DESAGREGADO LLORADEROS). Cantidades por lloradero de las laminas DL-01 y DL-02: "
               "tubo PVC-U Ø 3\" de 0.30 m con 8 perforaciones Ø 3/8\", filtro de grava de 0.30 x 0.30 x 0.30 m forrado con geotextil no tejido y mortero 1:3 de sellado. "
               "Mano de obra de la hoja COSTO HORA HOMBRE 2026. Celda amarilla = dato; verde = formula. Precios sin IGV.", plantilla)
    D = tabla_datos(H, Y4, "1. CANTIDADES POR LLORADERO (hoja DESAGREGADO LLORADEROS)", [
        ("n", "Numero de lloraderos de la partida", "und", "=" + DL + "F23", "DESAGREGADO LLORADEROS fila 23"),
        ("tubo", "Tubo PVC-U Ø 3\" por lloradero", "m", "=" + DL + "D37", "DESAGREGADO LLORADEROS fila 37 (DL-02 B)"),
        ("dt", "Desperdicio del tubo (corte de 10 piezas por tubo de 3 m)", "-", 0.05, "criterio de obra"),
        ("gr", "Grava filtrante por lloradero (incluye 10 % de desperdicio)", "m3", "=" + DL + "D40", "DESAGREGADO LLORADEROS fila 40 (DL-02 A)"),
        ("geo", "Geotextil por lloradero (6 caras + 10 % de traslapes)", "m2", "=" + DL + "D41", "DESAGREGADO LLORADEROS fila 41 (DL-01 etapa 3)"),
        ("dg", "Desperdicio del geotextil (corte del rollo)", "-", 0.05, "criterio de obra"),
        ("mor", "Mortero 1:3 de sellado alrededor del tubo", "m3", "=" + DL + "D42", "DESAGREGADO LLORADEROS fila 42 (DL-02)"),
        ("cem", "Cemento por m3 de mortero 1:3", "bol/m3", 10.5, "dosificacion usual del mortero 1:3"),
        ("are", "Arena gruesa por m3 de mortero 1:3", "m3/m3", 1.05, "arena suelta con 5 % de desperdicio"),
        ("agu", "Agua por m3 de mortero 1:3", "m3/m3", 0.27, "dosificacion usual del mortero 1:3"),
        ("rend", "Rendimiento de la cuadrilla", "und/dia", 24, "excavacion local de 0.027 m3, forrado, grava y cierre; el tubo se deja al vaciar el muro"),
        ("cop", "Operarios en la cuadrilla", "-", 0.5, "colocacion del tubo, sellado y control"),
        ("cpe", "Peones en la cuadrilla", "-", 1.0, "excavacion, grava y relleno")])
    mo = [("Operario", "hh", "=%s*8/%s" % (D["cop"], D["rend"]), "=%s$G$11" % HH, "hoja COSTO HORA HOMBRE 2026 (CAPECO, jornal R.M. 197-2025-TR)"),
          ("Peon", "hh", "=%s*8/%s" % (D["cpe"], D["rend"]), "=%s$G$13" % HH, "hoja COSTO HORA HOMBRE 2026 (CAPECO, jornal R.M. 197-2025-TR)")]
    mat = [("Tubo PVC-U Ø 3\" desague (NTP 399.003)", "m", "=%s*(1+%s)" % (D["tubo"], D["dt"]), "=%s/1.18/3" % TUBO, F_TUBO),
           ("Grava filtrante 20 a 40 mm", "m3", "=" + D["gr"], "=%s/1.18" % GRAVA, F_GRAVA),
           ("Geotextil no tejido 200 g/m2", "m2", "=%s*(1+%s)" % (D["geo"], D["dg"]), "=%s/400/1.18" % GEO, F_GEO),
           ("Cemento Portland tipo I", "bol", "=%s*%s" % (D["mor"], D["cem"]), "=%sF76" % AT, "precio de la ACU TAPA REGISTRO (Cemento Pacasmayo tipo I S/ 36.50 con IGV)"),
           ("Arena gruesa", "m3", "=%s*%s" % (D["mor"], D["are"]), "=%sF77" % AT, "precio de la ACU TAPA REGISTRO (Agregados Tarapoto, Morales)"),
           ("Agua", "m3", "=%s*%s" % (D["mor"], D["agu"]), "=%sF79" % AT, "precio de la ACU TAPA REGISTRO (EMAPA San Martin)")]
    acu(H, PARTIDA, "01.04.03.04.03.04 (hojas METRADO LLORADEROS y DESAGREGADO LLORADEROS)", "und", "=" + DL + "F23", mo, mat,
        "und/dia, cuadrilla 0.5 operario + 1 peon", rend="=" + D["rend"], por="UND",
        herr="3 % del costo de mano de obra (pala, pico, barreta, sierra para PVC y taladro para las perforaciones)")
    agregar_hoja(L, HOJA, H.xml(plantilla))
    L.guardar(f)
    return recalcular(f, list(L.ruta))


if __name__ == "__main__":
    print("celdas recalculadas:", construir(sys.argv[1]))
