"""Hogar de Refugio Temporal (Mujeres Violentadas, CUI 2675514): partida 01.04.03.04.03.03 JUNTA DE DILATACION E=1" CON
SELLADOR ASFALTO en cunetas, medida en TODA LA SECCION EN U (dos muros y losa de fondo), como pide la EG-2013 MTC,
Seccion 510 (cunetas revestidas de concreto): la junta separa la cuneta en tramos independientes, por lo que corta los muros
y tambien la losa de fondo; una junta solo en los muros deja la losa amarrada y se fisura.

Hoja METRADO JUNTA DE DILATACION:
- fila 10: el espesor referencial pasa al titulo; queda el ancho interior del fondo 0.40 m (CONCRETO EN CUNETAS: losa 0.60
  menos 2 muros de 0.10).
- columna I: longitud por junta = 2 x altura del muro + ancho del fondo; columna J = N de juntas x longitud por junta.
- notas al pie con el sustento.
PLANILLA GENERAL y RESUMEN leen J12 por formula; se recalculan los valores en cache. Edicion directa del XML.
Uso: python3 herramientas/junta_cunetas_seccion_refugio.py <planilla.xlsx>
"""
import sys, os, re
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from angulo_contramarco_refugio import Libro, recalcular

H = "METRADO JUNTA DE DILATACION"
NOTAS = [
    "NOTAS:",
    "1. EG-2013 MTC, Seccion 510 (cunetas revestidas de concreto): la junta corta toda la seccion en U, es decir los dos muros y la losa de fondo, "
    "para que cada paño de 3.00 m trabaje independiente.",
    "2. Longitud por junta = 2 x altura del muro (area del muro / longitud del eje, hoja CONCRETO EN CUNETAS) + ancho interior del fondo 0.40 m.",
    "3. Junta e = 1\" (0.0254 m): tecnopor de 1\" en todo el espesor y sellador asfaltico (RC-250 + arena) en la cara interior; se mide en metros "
    "lineales de junta sellada. Detalle en la lamina DJ-01.",
]


def cambiar(f):
    L = Libro(f)
    assert L.leer(H, "I13") == "2.0" or L.leer(H, "I13") == "2", "la planilla ya fue modificada"
    L.texto(H, "A1", "PLANILLA DE METRADOS - JUNTA DE DILATACIÓN E=1\" (0.0254 m) CON SELLADOR ASFÁLTICO EN CUNETAS: TODA LA SECCIÓN (2 MUROS + LOSA DE FONDO)")
    L.texto(H, "A10", "Ancho interior del fondo (m)")
    x = L.hoja(H)
    m = L.celda(H, "B10"); x = x[:m.start()] + '<c r="B10" s="236" t="n"><v>0.4</v></c>' + x[m.end():]; L.x[H] = x
    L.texto(H, "I11", "LONG. POR\nJUNTA (m)\n2 muros + fondo")
    L.texto(H, "J11", "PARCIAL\n(ml)")
    for r in range(13, 25):
        L.formula(H, "I%d" % r, "$B$9*F%d+$B$10" % r)
        L.formula(H, "J%d" % r, "H%d*I%d" % (r, r))
    # notas al pie (filas 26 a 29), con el estilo del texto de parametros
    x = L.hoja(H)
    assert not re.search(r'<row r="2[6-9]"[ >]', x)
    filas = "".join('<row r="%d" customHeight="true" ht="%s"><c r="A%d" s="237" t="s"><v>%d</v></c></row>' % (26 + i, "15" if i == 0 else "27", 26 + i, L.sid(t))
                    for i, t in enumerate(NOTAS))
    x = x.replace("</sheetData>", filas + "</sheetData>")
    x = x.replace("</mergeCells>", "".join('<mergeCell ref="A%d:J%d"/>' % (26 + i, 26 + i) for i in range(len(NOTAS))) + "</mergeCells>")
    x = re.sub(r'<mergeCells count="(\d+)"', lambda m: '<mergeCells count="%d"' % (int(m.group(1)) + len(NOTAS)), x)
    x = re.sub(r'<dimension ref="A1:([A-Z]+)\d+"/>', lambda m: '<dimension ref="A1:%s%d"/>' % (m.group(1), 25 + len(NOTAS)), x)
    L.x[H] = x
    L.guardar(f)
    return recalcular(f, list(L.ruta))


if __name__ == "__main__":
    print("celdas recalculadas:", cambiar(sys.argv[1]))
