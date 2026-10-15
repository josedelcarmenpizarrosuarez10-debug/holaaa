"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): hoja DESAGREGADO LLORADEROS dentro de la planilla vigente.

A. Ubicacion y numero de lloraderos: enlazada a la hoja METRADO LLORADEROS (tramos de muro de cuneta colindantes con area
   verde medidos en la planta general de drenaje, @1.50 m).
B. Componentes de un lloradero y total de la partida 01.04.03.04.03.04, con las medidas de las laminas DL-01 y DL-02:
   tubo PVC-U 3" de 0.30 m con 8 perforaciones de 3/8", filtro de grava de 0.30 x 0.30 x 0.30 m forrado con geotextil,
   excavacion local y mortero de sellado.
C. Control con el RESUMEN.
Edicion directa del XML (conserva formato e imagenes); no cambia ninguna cantidad de metrado.
Uso: python3 herramientas/desagregado_lloraderos_refugio.py <planilla.xlsx>
"""
import sys, os, re
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular
from acu_juntas_refugio import Hoja, encabezado, agregar_hoja

ML = "'METRADO LLORADEROS'!"
HOJA = "DESAGREGADO LLORADEROS"


def amarillo4(L):
    """Formato amarillo con 4 decimales (el que agrega acu_juntas_refugio); lo crea si no existe."""
    s = L.F["xl/styles.xml"].decode(); i, j = s.index("<cellXfs"), s.index("</cellXfs>")
    xfs = re.findall(r"<xf [^>]*?(?:/>|>.*?</xf>)", s[i:j], re.S)
    nuevo = xfs[284].replace('numFmtId="173"', 'numFmtId="170"')
    if nuevo in xfs: return xfs.index(nuevo)
    s = s[:j] + nuevo + s[j:]; s = re.sub(r'<cellXfs count="\d+"', '<cellXfs count="%d"' % (len(xfs) + 1), s, count=1)
    L.F["xl/styles.xml"] = s.encode(); return len(xfs)


def construir(f):
    L = Libro(f)
    assert HOJA not in L.ruta, "la hoja ya existe"
    assert "LLORADERO" in L.leer("RESUMEN", "B32"), "la partida de lloraderos no esta en RESUMEN!B32"
    plantilla = L.hoja("ACU TAPA REGISTRO"); Y4 = amarillo4(L)
    H = Hoja(L, Y4)
    encabezado(H, "DESAGREGADO DE LA PARTIDA 01.04.03.04.03.04 - LLORADERO DE TUBERIA PVC Ø3\" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m",
               "La partida se mide por unidad de lloradero. A: ubicacion y numero, de la hoja METRADO LLORADEROS (muros de cuneta colindantes con area verde, medidos en la planta "
               "general de drenaje; un lloradero cada 1.50 m). B: componentes de un lloradero segun las laminas DL-01 y DL-02 (tubo PVC-U Ø 3\" de 0.30 m con 8 perforaciones "
               "Ø 3/8\", filtro de grava de 0.30 x 0.30 x 0.30 m forrado con geotextil no tejido) por el numero de lloraderos. Celda amarilla = dato; verde = formula.", plantilla)
    # ------------------------------------------------------------ A. ubicacion
    H.banda("A. UBICACION Y NUMERO DE LLORADEROS (hoja METRADO LLORADEROS)", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "EJE Y TRAMO (progresivas de la cuneta)", "LADO DEL MURO", "LONGITUD JUNTO A AREA VERDE (m)",
                                                      "ESPACIAM. (m)", "N° DE LLORADEROS", None, "SUSTENTO"))], 31.5)
    r0 = H.r + 1
    for i, rr in enumerate(range(7, 19), 1):
        H.fila([("A", 283, i), ("B", 149, "=%sB%d&\": \"&%sC%d" % (ML, rr, ML, rr)), ("C", 285, "=%sD%d" % (ML, rr)), ("D", 290, "=%sE%d" % (ML, rr)),
                ("E", 290, "=%sF%d" % (ML, rr)), ("F", 290, "=%sG%d" % (ML, rr)), ("G", 295, None), ("H", 149, "planta general de drenaje; N° = REDONDEAR.MAS(L / 1.50)")])
    r1 = H.r
    rt = H.fila([("A", 21, None), ("B", 294, "TOTAL (und de la partida)"), ("C", 295, None), ("D", 296, "=SUM(D%d:D%d)" % (r0, r1)), ("E", 295, None),
                 ("F", 296, "=SUM(F%d:F%d)" % (r0, r1)), ("G", 295, None), ("H", 295, None)])
    N = "$F$%d" % rt
    # ------------------------------------------------------------ B. datos del detalle
    H.banda("B. DATOS DEL DETALLE (laminas DL-01 y DL-02)", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "DATO", "UND", "VALOR", None, None, None, "SUSTENTO"))], 31.5)
    dat = {}
    for i, (k, t, u, v, s) in enumerate([
            ("lf", "Lado del filtro localizado (cubo de grava forrado con geotextil)", "m", 0.30, "DL-02 A: filtro 0.30 x 0.30 x 0.30 m"),
            ("lt", "Longitud del tubo PVC-U Ø 3\" por lloradero", "m", 0.30, "DL-02 B: 0.10 en el muro + 0.20 perforado dentro del filtro"),
            ("np", "Perforaciones Ø 3/8\" por fila", "und", 4, "DL-02 B: 4 perforaciones @0.05 por fila"),
            ("nf", "Filas de perforaciones", "und", 2, "DL-02 B: 2 filas a 120 grados, simetricas respecto al fondo"),
            ("dg", "Desperdicio de grava (acomodo y perdidas)", "-", 0.10, "criterio de obra"),
            ("tg", "Traslapes del geotextil", "-", 0.10, "DL-01 etapa 3: traslape de 0.10 m al cerrar el filtro"),
            ("mo", "Mortero 1:3 de sellado alrededor del tubo", "m3", 0.0005, "anillo de 0.02 m en las dos caras del muro (DL-02)")], 1):
        r = H.fila([("A", 283, i), ("B", 149, t), ("C", 285, u), ("D", Y4, v), ("E", 295, None), ("F", 295, None), ("G", 295, None), ("H", 149, s)], 31.5)
        dat[k] = "$D$%d" % r
    # ------------------------------------------------------------ C. componentes
    H.banda("C. COMPONENTES DE UN LLORADERO Y TOTAL DE LA PARTIDA", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", ("N°", "COMPONENTE", "UND", "POR LLORADERO", "N° LLORADEROS", "TOTAL", None, "SUSTENTO"))], 31.5)
    comps = [("Tubo PVC-U Ø 3\" para desague (NTP 399.003)", "m", "=" + dat["lt"], "DL-02 B; sale de tubos de 3 m (10 lloraderos por tubo)"),
             ("Perforaciones Ø 3/8\" en el tramo dentro del filtro", "und", "=%s*%s" % (dat["np"], dat["nf"]), "DL-02 B"),
             ("Excavacion local del hueco del filtro (lado^3)", "m3", "=%s^3" % dat["lf"], "DL-01 etapa 1; incluida en la mano de obra del ACU"),
             ("Grava filtrante (ripio) 20 a 40 mm: lado^3 + desperdicio", "m3", "=%s^3*(1+%s)" % (dat["lf"], dat["dg"]), "DL-01 etapa 2; DL-02 A"),
             ("Geotextil no tejido clase 2: 6 caras del cubo + traslapes", "m2", "=6*%s^2*(1+%s)" % (dat["lf"], dat["tg"]), "DL-01 etapa 3; DL-02 A"),
             ("Mortero 1:3 de sellado alrededor del tubo", "m3", "=" + dat["mo"], "DL-02")]
    for i, (t, u, q, s) in enumerate(comps, 1):
        r = H.r + 1
        H.fila([("A", 283, i), ("B", 149, t), ("C", 285, u), ("D", 306, q), ("E", 290, "=+" + N), ("F", 306, "=D%d*E%d" % (r, r)), ("G", 295, None), ("H", 149, s)], 31.5)
    # ------------------------------------------------------------ D. control
    H.banda("D. CONTROL CON EL RESUMEN", salto=1)
    H.fila([(k, 282, t) for k, t in zip("ABCDEFGH", (None, "PARTIDA", "UND", None, "ESTA HOJA", "RESUMEN", "CONTROL", None))])
    r = H.r + 1
    H.fila([("A", 21, None), ("B", 149, "01.04.03.04.03.04 LLORADERO DE TUBERIA PVC Ø3\" C/FILTRO DE GRAVA Y GEOTEXTIL @1.50 m"), ("C", 285, "und"), ("D", 295, None),
            ("E", 306, "=+" + N), ("F", 306, "=+RESUMEN!D32"), ("G", 283, '=IF(ABS(E%d-F%d)<0.001,"CONFORME","REVISAR")' % (r, r)), ("H", 295, None)], 31.5)
    agregar_hoja(L, HOJA, H.xml(plantilla))
    L.guardar(f)
    return recalcular(f, [HOJA])


if __name__ == "__main__":
    print("celdas recalculadas:", construir(sys.argv[1]))
