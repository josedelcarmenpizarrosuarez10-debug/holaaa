"""Especificaciones tecnicas para el detalle de falsa columna y dado del montante pluvial (3 proyectos).

Reemplaza los cuadros "Consideraciones" y "Detalle de Falsa Columna" del plano del proyectista. Se dibuja a escala
real (1 unidad = 1 m) como BLOQUE "ESPEC_FALSA_COLUMNA", igual que la leyenda de cunetas (leyenda_cunetas.py).
Los valores salen de la PLANILLA GENERAL DE METRADOS de cada proyecto (partidas de falsa columna y dado).
"""
import os, sys
import ezdxf
from ezdxf.enums import TextEntityAlignment as TA
import openpyxl
from leyenda_cunetas import Hoja, HT, HS, HB, INTER, C_TIT, C_TXT, RAIZ

MET = os.path.join(RAIZ, "insumos", "metrados_vigentes")
PROY = {
    "varones": ("METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx", "CAR VARONES - CUI N.° 2705619", "entregables_varones", "CAR_VARONES"),
    "refugio": ("METRADO_DRENAJE_MUJERES_VIOLENTADAS.xlsx", "HOGAR DE REFUGIO TEMPORAL - CUI N.° 2675514", "entregables", "HOGAR_REFUGIO"),
    "mujeres": ("METRADO_DRENAJE_PLUVIAL_CAR_MUJERES.xlsx", "CAR MUJERES - CUI N.° 2717013", "entregables_mujeres", "CAR_MUJERES"),
}


def datos(archivo):
    """Lee de la planilla: cantidad de falsas columnas y dados, totales y el desglose por unidad."""
    ws = openpyxl.load_workbook(os.path.join(MET, archivo), data_only=True)["PLANILLA GENERAL DE METRADOS"]
    filas = [[c.value for c in r] for r in ws.iter_rows()]
    D = {}
    for i, r in enumerate(filas):
        txt = next((v.strip() for v in r if isinstance(v, str) and not v.strip()[:1].isdigit() and len(v.strip()) > 8), "")
        num = [v for v in r if isinstance(v, (int, float))]
        u = txt.upper()
        if u.startswith("FALSA COLUMNA P/MONTANTE"):
            D["n"] = num[0]
        elif u.startswith("CONCRETO F´C=175 KG/CM2 EN FALSA"):
            D["conc"] = num[-1]
        elif u.startswith("ENCOFRADO Y DESENCOFRADO EN FALSA"):
            D["enc"] = num[-1]
        elif u.startswith("ACERO FY=4200 KG/CM2 EN FALSA"):
            D["acero"] = num[-1]
        elif u == "ACERO LONGITUDINAL":
            D["long"] = num[:2]                       # longitud por barra, numero de barras
        elif u == "ACERO TRANSVERSAL":
            D["tra"] = num[:2]                        # longitud por estribo, numero de estribos
        elif u.startswith("CONCRETO F'C=140 KG/CM2 PARA DADOS"):
            D["dado"] = (num[0], num[-1])
    return D


def construir(clave):
    archivo, nombre, carpeta, suf = PROY[clave]
    D = datos(archivo)
    n = D["n"]; ndado, vdado = D["dado"]
    Ll, nl = D["long"]; Lt, nt = D["tra"]
    kg_u = (Ll * nl + Lt * nt) * 0.56

    doc = ezdxf.new("R2013", setup=True); doc.header["$INSUNITS"] = 6
    doc.styles.add("ARIAL", font="arial.ttf"); doc.styles.add("ARIAL-N", font="arialbd.ttf")
    for nm, c in (("LEY-TEXTO", 7), ("LEY-TITULO", 160), ("LEY-SIMBOLO", 7), ("LEY-RELLENO", 8), ("LEY-MARCO", 250), ("LEY-COTA", 94)):
        doc.layers.add(nm, color=c)
    blk = doc.blocks.new("ESPEC_FALSA_COLUMNA")
    S = Hoja(blk)

    W, X1, X2, AC = 2.72, 0.06, 1.42, 1.19
    YT = 1.95
    S.t(W / 2, YT - 0.085, "ESPECIFICACIONES TECNICAS - FALSA COLUMNA Y DADO DEL MONTANTE PLUVIAL", HT * 0.9, C_TIT, "LEY-TITULO", "ARIAL-N", TA.MIDDLE_CENTER)
    S.t(W / 2, YT - 0.150, nombre + " - falsa columna de 0.20 x 0.15 x 1.30 m sobre dado de 0.40 x 0.40 x 0.35 m", HB, al=TA.MIDDLE_CENTER)
    YC = YT - 0.20
    S.ln((0, YC), (W, YC), 250, "LEY-MARCO")
    sep = S.b.add_line((X2 - 0.06, YC), (X2 - 0.06, 0), dxfattribs={"layer": "LEY-MARCO", "color": 250})

    def bloque(x, y, items):
        for tit, ps in items:
            S.t(x, y, tit, HB, C_TIT, estilo="ARIAL-N"); y -= HB * INTER
            for p in ps:
                y = S.parrafo(x, y, "- " + p, AC, sangria="  ")
            y -= 0.015
        return y

    C1 = [
        ("1. FUNCION", [
            "Elemento de concreto armado no estructural, adosado al muro, que aloja y protege contra golpes el tramo inferior del montante "
            "PVC Ø 4\" hasta 1.30 m sobre el piso terminado. No recibe cargas de la edificacion."]),
        ("2. CONCRETO", [
            "f'c = 175 kg/cm² a los 28 dias; cemento Portland tipo I (NTP 334.009); agua potable (NTP 339.088).",
            "Piedra chancada de 1/2\" (tamano maximo menor que 1/5 de la dimension menor y que 3/4 del espacio libre entre barras y tubo); asentamiento de 3\" a 4\".",
            "Vaciado en una sola etapa, despues de instalar y probar el montante, compactando con varilla y golpes suaves en el encofrado (no vibrar contra el tubo)."]),
        ("3. ACERO DE REFUERZO", [
            "Barras corrugadas fy = 4200 kg/cm², grado 60 (ASTM A615 / NTP 341.031), con certificado de calidad del fabricante por cada lote; sin oxido suelto, grasa ni barro.",
            "Longitudinal: %d Ø 3/8\" en las cuatro esquinas, en toda la altura de la falsa columna y ancladas en el dado." % nl,
            "Transversal: estribos cerrados Ø 3/8\" @0.15 m (%d por falsa columna), con ganchos a 135° de 0.075 m; el primero a 0.05 m del dado." % nt,
            "Doblado en frio; ganchos y diametros de doblado segun la Norma E.060, capitulo 7."]),
        ("4. RECUBRIMIENTO", [
            "Recubrimiento libre de 2 cm medido a la cara exterior del estribo, asegurado con separadores de concreto o plastico (no usar piedras ni madera)."]),
        ("5. MONTANTE DENTRO DE LA FALSA COLUMNA", [
            "Tubo PVC-U Ø 4\" (NTP 399.003) aplomado y centrado, sin tocar el acero; se prueba con agua antes del vaciado y se tapa su extremo superior durante el vaciado.",
            "En el dado, el montante se une al codo PVC Ø 4\" x 90° de salida con cemento solvente."]),
    ]
    C2 = [
        ("6. DADO DE CONCRETO", [
            "Concreto simple f'c = 140 kg/cm² (partida de dados del metrado), de 0.40 x 0.40 x 0.35 m, vaciado sobre el fondo de la excavacion compactado; envuelve el codo de salida y el arranque de las barras."]),
        ("7. ENCOFRADO Y DESENCOFRADO", [
            "Madera o triplay en tres caras (la cuarta es el muro), aplomado y arriostrado, con juntas selladas.",
            "Desencofrado a las 24 horas como minimo, sin golpear el concreto."]),
        ("8. CURADO Y PROTECCION", [
            "Curado con agua o curador quimico durante 7 dias como minimo; proteger las aristas contra golpes hasta la entrega."]),
        ("9. CONTROL DE CALIDAD", [
            "Verificar antes del vaciado: plomo del tubo, numero y diametro de barras, separacion de estribos y recubrimiento (tolerancia ±5 mm en el plomo)."]),
        ("10. NORMAS", [
            "RNE: E.060 Concreto Armado e IS.010 Instalaciones Sanitarias; NTP 341.031, NTP 399.003, NTP 334.009 y NTP 339.088."]),
    ]
    y1 = bloque(X1, YC - 0.07, C1)
    y2 = bloque(X2, YC - 0.07, C2)

    # cuadro de cantidades (valores de la planilla)
    y2 = S.titulo(X2, y2 - 0.02, "CANTIDADES SEGUN EL METRADO", ancho=0.72)
    cab = ["ELEMENTO", "POR UNIDAD", "TOTAL (%d und)" % n]
    filas = [["Concreto f'c = 175", "%.3f m³" % (D["conc"] / n), "%.3f m³" % D["conc"]],
             ["Encofrado", "%.2f m²" % (D["enc"] / n), "%.2f m²" % D["enc"]],
             ["Acero longitudinal", "%d Ø3/8\" x %.2f m" % (nl, Ll), "-"],
             ["Estribos", "%d Ø3/8\" x %.2f m" % (nt, Lt), "-"],
             ["Acero fy = 4200", "%.2f kg" % kg_u, "%.2f kg" % D["acero"]],
             ["Dado f'c = 140", "%.3f m³" % (vdado / ndado), "%.3f m³ (%d und)" % (vdado, ndado)]]
    anchos = [0.42, 0.40, 0.40]; fh = HB * 1.75
    yy = y2 + HB * 0.6; ytab = yy
    for i, fl in enumerate([cab] + filas):
        x = X2
        for j, v in enumerate(fl):
            if i == 0:
                S.t(x + anchos[j] / 2, yy - fh / 2, v, HB * 0.85, C_TIT, estilo="ARIAL-N", al=TA.MIDDLE_CENTER)
            else:
                S.t(x + (0.02 if j == 0 else anchos[j] / 2), yy - fh / 2, v, HB * 0.82, al=TA.MIDDLE_LEFT if j == 0 else TA.MIDDLE_CENTER)
            x += anchos[j]
        S.ln((X2, yy), (X2 + sum(anchos), yy), 8, "LEY-MARCO"); yy -= fh
    S.ln((X2, yy), (X2 + sum(anchos), yy), 8, "LEY-MARCO")
    x = X2
    for a in [0] + anchos:
        x += a; S.ln((x, ytab), (x, yy), 8, "LEY-MARCO")
    y2 = S.parrafo(X2, yy - HB * 1.3, "Fuente: PLANILLA GENERAL DE METRADOS (partidas de falsa columna y de dados de concreto).", AC, HB * 0.8)

    yb = min(y1, y2) - 0.04
    sep.dxf.end = (X2 - 0.06, yb)
    blk.add_lwpolyline([(0, yb), (W, yb), (W, YT), (0, YT)], close=True, dxfattribs={"layer": "LEY-MARCO", "color": 250, "lineweight": 50})
    doc.modelspace().add_blockref("ESPEC_FALSA_COLUMNA", (0, 0), dxfattribs={"layer": "0"})
    err = len(doc.audit().errors)
    sal = os.path.join(RAIZ, carpeta, "ESPECIFICACIONES_FALSA_COLUMNA_MONTANTE_%s.dxf" % suf)
    doc.saveas(sal)
    return sal, (0, yb, W, YT), err, D


if __name__ == "__main__":
    for k in (sys.argv[1:] or PROY):
        sal, caja, err, D = construir(k)
        print(k, os.path.relpath(sal, RAIZ), [round(v, 3) for v in caja], "errores", err, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in D.items()})
