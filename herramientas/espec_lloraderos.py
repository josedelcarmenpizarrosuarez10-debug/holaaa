"""Leyenda y especificaciones tecnicas para el detalle de lloraderos en cunetas (el sub-dren se retiro de los planos).

Solo CAR Varones (CUI 2705619) y Hogar de Refugio Temporal (CUI 2675514), los dos proyectos con la partida de lloraderos.
Bloque "ESPEC_LLORADEROS" a escala real (1 unidad = 1 m), igual que leyenda_cunetas.py y espec_falsa_columna.py.
Cantidades de la hoja METRADO LLORADEROS; materiales por unidad del criterio de esa hoja y del ACU de lloraderos.
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
}
TUBO_U, GRAVA_U, GEO_U = 0.30, 0.027, 0.60          # m de tubo, m3 de grava y m2 de geotextil por lloradero


def datos(archivo):
    ws = openpyxl.load_workbook(os.path.join(MET, archivo), data_only=True)["METRADO LLORADEROS"]
    for r in ws.iter_rows(values_only=True):
        v = [c for c in r if c not in (None, "")]
        if v and isinstance(v[0], str) and v[0].upper().startswith("TOTAL DE LLORADEROS"):
            return dict(L=v[1], n=v[2])
    raise ValueError("sin total en METRADO LLORADEROS")


def detalle(doc, nombre):
    """Bloque DETALLE_LLORADERO: seccion de cuneta abierta junto a area verde, a escala real (H = 0.50 m tipico)."""
    blk = doc.blocks.new("DETALLE_LLORADERO")
    S = Hoja(blk)
    H, e, b = 0.50, 0.10, 0.40                       # altura interior dibujada, espesor de muros y losa, ancho interior
    B = b + 2 * e; ytop = e + H; yc = e + H / 2      # ancho exterior, corona, eje del lloradero (media altura)
    F, LT, DT = 0.30, 0.30, 0.076                    # filtro, largo del tubo, diametro del tubo
    XT0, XT1 = -0.55, B + 0.55                       # extension del terreno dibujado
    # ---- terreno con huecos en los filtros y en la cuneta
    ter = blk.add_hatch(color=33, dxfattribs={"layer": "LEY-RELLENO"}); ter.set_pattern_fill("EARTH", scale=0.03, color=33)
    ter.paths.add_polyline_path([(XT0, -0.25), (XT1, -0.25), (XT1, ytop), (XT0, ytop)], is_closed=True, flags=1)
    ter.paths.add_polyline_path([(-0.002, -0.102), (B + 0.002, -0.102), (B + 0.002, ytop), (-0.002, ytop)], is_closed=True, flags=16)
    for x0 in (-F, B):
        ter.paths.add_polyline_path([(x0, yc - F / 2), (x0 + F, yc - F / 2), (x0 + F, yc + F / 2), (x0, yc + F / 2)], is_closed=True, flags=16)
    S.ln((XT0, ytop), (0, ytop), 33); S.ln((B, ytop), (XT1, ytop), 33)
    import random; rnd = random.Random(7)
    x = XT0 + 0.02
    while x < XT1 - 0.02:                            # pasto (area verde)
        if not (-0.01 < x < B + 0.01):
            for dx, h in ((0, 0.035), (0.008, 0.05), (0.016, 0.03)):
                S.ln((x + dx, ytop), (x + dx + rnd.uniform(-0.01, 0.01), ytop + h * rnd.uniform(0.7, 1.1)), 94)
        x += 0.07
    # ---- solado y cuneta de concreto
    sol = [(-0.0, -0.10), (B, -0.10), (B, 0), (0, 0)]
    S.relleno(sol, None, "AR-SAND", 0.012, 8); S.poli(sol, 8, cerrada=True)
    cun = [(0, 0), (B, 0), (B, ytop), (B - e + 0.05 - 0.05, ytop), (B - e, ytop), (B - e, ytop - 0.03), (B - e - 0.0, ytop - 0.03),
           (B - e, e), (e, e), (e, ytop - 0.03), (e, ytop), (0, ytop)]
    cun = [(0, 0), (B, 0), (B, ytop), (B - e + 0.05, ytop), (B - e + 0.05, ytop - 0.03), (B - e, ytop - 0.03), (B - e, e),
           (e, e), (e, ytop - 0.03), (e - 0.05, ytop - 0.03), (e - 0.05, ytop), (0, ytop)]
    h = S.relleno(cun, None, "AR-CONC", 0.012, 8)
    for x0 in (0, B - e):                            # pase de los tubos sin achurado
        pass
    S.poli(cun, 5, cerrada=True, lw=50)
    # ---- rejilla movil sobre el rebaje
    rj = [(e - 0.05, ytop - 0.03), (B - e + 0.05, ytop - 0.03), (B - e + 0.05, ytop), (e - 0.05, ytop)]
    S.relleno(rj, (214, 70, 70), color=1); S.poli(rj, 1, cerrada=True, lw=35)
    for x0, sg in ((e - 0.05, 1), (B - e + 0.05, -1)):
        S.poli([(x0, ytop - 0.03), (x0, ytop - 0.03 - 0.025), (x0 + sg * 0.004, ytop - 0.03 - 0.025)], 5, lw=25)
    # ---- filtros, geotextil, tubos
    for lado in (-1, 1):
        x0 = -F if lado < 0 else B                   # filtro pegado a la cara exterior del muro
        fil = [(x0, yc - F / 2), (x0 + F, yc - F / 2), (x0 + F, yc + F / 2), (x0, yc + F / 2)]
        S.relleno(fil, None, "GRAVEL", 0.05, 250)
        S.poli([(x0 - 0.006, yc - F / 2 - 0.006), (x0 + F + 0.006, yc - F / 2 - 0.006), (x0 + F + 0.006, yc + F / 2 + 0.006), (x0 - 0.006, yc + F / 2 + 0.006)], 150, cerrada=True, lw=70)
        xi = e if lado < 0 else B - e                # cara interior del muro (extremo bajo)
        xe = xi + lado * LT                          # extremo dentro del filtro (hacia el terreno)
        dz = LT * 0.005
        p = [(xe, yc + dz + DT / 2), (xi, yc + DT / 2), (xi, yc - DT / 2), (xe, yc + dz - DT / 2)]
        S.relleno(p, (180, 214, 246), color=151); S.poli(p, 5, cerrada=True, lw=35)
        xm = xi + lado * e                           # cara exterior del muro: desde aqui el tubo va perforado
        for k in range(4):
            xx = xm + lado * (0.03 + k * 0.05)
            S.punto((xx, yc + 0.012), 0.004, 250); S.punto((xx, yc - 0.012), 0.004, 250)
        # flecha de flujo hacia la cuneta
        xa = xi - lado * 0.03; xb = xi - lado * 0.15
        S.ln((xa, yc - 0.09), (xb, yc - 0.09), 1)
        S.poli([(xb, yc - 0.09), (xb + lado * 0.035, yc - 0.078), (xb + lado * 0.035, yc - 0.102)], 1, cerrada=True)
        S.t((xa + xb) / 2, yc - 0.075, "S = 0.5 %", HB * 0.8, 160, al=TA.BOTTOM_CENTER)

    # ---- cotas (lineas verdes con tic oblicuo)
    def cota_h(xa, xb, y, txt=None, arriba=True):
        S.ln((xa, y), (xb, y), 94, "LEY-COTA")
        for x in (xa, xb):
            S.ln((x - 0.01, y - 0.01), (x + 0.01, y + 0.01), 94, "LEY-COTA"); S.ln((x, y - 0.02), (x, y + 0.02), 94, "LEY-COTA")
        S.t((xa + xb) / 2, y + (0.012 if arriba else -0.012), txt or "%.2f" % (xb - xa), HB * 0.85, 7,
            al=TA.BOTTOM_CENTER if arriba else TA.TOP_CENTER)

    def cota_v(x, ya, yb, txt=None, izq=True):
        S.ln((x, ya), (x, yb), 94, "LEY-COTA")
        for y in (ya, yb):
            S.ln((x - 0.01, y - 0.01), (x + 0.01, y + 0.01), 94, "LEY-COTA"); S.ln((x - 0.02, y), (x + 0.02, y), 94, "LEY-COTA")
        S.t(x + (-0.015 if izq else 0.015), (ya + yb) / 2, txt or "%.2f" % (yb - ya), HB * 0.85, 7,
            al=TA.MIDDLE_RIGHT if izq else TA.MIDDLE_LEFT)

    cota_h(0, e, -0.17, arriba=False); cota_h(e, B - e, -0.17, arriba=False); cota_h(B - e, B, -0.17, arriba=False)
    cota_h(0, B, -0.24, arriba=False)
    cota_h(-F, 0, yc + F / 2 + 0.07, "0.30")                         # filtro
    cota_h(-LT + e, e, yc - F / 2 - 0.05, "L = 0.30", arriba=False)  # tubo
    cota_v(-F - 0.06, yc - F / 2, yc + F / 2, "0.30")
    cota_v(B + F + 0.06, e, ytop, "H variable", izq=False)
    cota_v(B / 2, e, yc - DT / 2, "H/2", izq=False)
    cota_v(-F - 0.06, -0.10, 0, "0.10")

    # ---- llamadas en columna a la derecha, de arriba hacia abajo
    xt = B + F + 0.42
    items = [((B / 2, ytop - 0.015), "Rejilla metalica movil: platinas 1\" x 3/16\" sobre angulo 1\" x 1\" x 3/16\""),
             ((B + 0.15, ytop + 0.03), "Area verde (terreno natural con cobertura vegetal)"),
             ((B + F - 0.02, yc + F / 2 - 0.02), "Grava filtrante (ripio) de 20 a 40 mm"),
             ((B + F + 0.006, yc + 0.06), "Filtro localizado 0.30 x 0.30 x 0.30 m (0.027 m³)"),
             ((B - e + 0.05, yc + 0.02), "Lloradero: tubo PVC-U Ø 3\" (76 mm), L = 0.30 m @1.50 m, S = 0.5 %"),
             ((B + 0.13, yc - 0.012), "Tramo perforado Ø 3/8\" dentro del filtro"),
             ((B + F + 0.006, yc - 0.10), "Geotextil no tejido clase 2 envolviendo la grava"),
             ((B - 0.05, 0.15), "Muro y losa de cuneta f'c = 175 kg/cm², e = 0.10 m"),
             ((B + 0.25, 0.02), "Relleno compactado con material propio"),
             ((B - 0.10, -0.05), "Solado f'c = 100 kg/cm², e = 4\"")]
    ys = ytop + 0.10; dy = 0.085
    for k, (pt, txt) in enumerate(items):
        y = ys - k * dy
        S.ln(pt, (xt - 0.03, y), 30, "LEY-COTA"); S.ln((xt - 0.03, y), (xt - 0.005, y), 30, "LEY-COTA")
        S.punto(pt, 0.006, 30)
        S.t(xt, y, txt, HB * 0.9, al=TA.MIDDLE_LEFT)
    # ---- titulo
    S.t(B / 2 + 0.55, ytop + 0.36, "DETALLE DE INSTALACION DE LLORADEROS EN CUNETAS", HT * 0.85, C_TIT, "LEY-TITULO", "ARIAL-N", TA.MIDDLE_CENTER)
    S.t(B / 2 + 0.55, ytop + 0.29, "Seccion cuneta - area verde (H variable segun perfil; se dibuja H = 0.50 m) - " + nombre, HB * 0.9, al=TA.MIDDLE_CENTER)
    S.t(B / 2 + 0.55, -0.36, "ESC. REAL (1 unidad = 1 m) - lloraderos solo en los muros colindantes con area verde", HB * 0.85, al=TA.MIDDLE_CENTER)
    return blk


def construir(clave):
    archivo, nombre, carpeta, suf = PROY[clave]
    D = datos(archivo); n, L = D["n"], D["L"]

    doc = ezdxf.new("R2013", setup=True); doc.header["$INSUNITS"] = 6
    doc.styles.add("ARIAL", font="arial.ttf"); doc.styles.add("ARIAL-N", font="arialbd.ttf")
    for nm, c in (("LEY-TEXTO", 7), ("LEY-TITULO", 160), ("LEY-SIMBOLO", 7), ("LEY-RELLENO", 8), ("LEY-MARCO", 250), ("LEY-COTA", 94)):
        doc.layers.add(nm, color=c)
    blk = doc.blocks.new("ESPEC_LLORADEROS")
    S = Hoja(blk)

    W, X1, X2, AC = 2.72, 0.06, 1.42, 1.19
    YT = 2.30
    S.t(W / 2, YT - 0.085, "LEYENDA Y ESPECIFICACIONES TECNICAS - LLORADEROS EN CUNETAS", HT * 0.9, C_TIT, "LEY-TITULO", "ARIAL-N", TA.MIDDLE_CENTER)
    S.t(W / 2, YT - 0.150, nombre + " - cunetas de evacuacion pluvial colindantes con area verde", HB, al=TA.MIDDLE_CENTER)
    YC = YT - 0.20
    S.ln((0, YC), (W, YC), 250, "LEY-MARCO")
    sep = S.b.add_line((X2 - 0.06, YC), (X2 - 0.06, 0), dxfattribs={"layer": "LEY-MARCO", "color": 250})

    # ------------------------------------------------------------ leyenda de los achurados del detalle
    y = S.titulo(X1, YC - 0.07, "LEYENDA", ancho=0.30)
    xs, xt = X1, X1 + 0.30

    def fila(dib, txt):
        nonlocal y
        yc = y - 0.035 + HB * 0.4
        dib(yc)
        y = min(S.parrafo(xt, y, txt, AC - 0.30), y - 0.075) - 0.025

    def caja(yc, **k):
        return [(xs, yc - 0.03), (xs + 0.26, yc - 0.03), (xs + 0.26, yc + 0.03), (xs, yc + 0.03)]

    def terreno(yc):
        p = caja(yc); S.relleno(p, None, "EARTH", 0.03, 33); S.poli(p, 7, cerrada=True)
    fila(terreno, "Terreno natural / area verde (relleno compactado)")

    def concreto(yc):
        p = caja(yc); S.relleno(p, None, "AR-CONC", 0.012, 8); S.poli(p, 5, cerrada=True)
    fila(concreto, "Muro y losa de la cuneta, concreto f'c = 175 kg/cm²")

    def grava(yc):
        p = caja(yc); S.relleno(p, None, "GRAVEL", 0.05, 250); S.poli(p, 7, cerrada=True)
    fila(grava, "Grava filtrante (ripio) de 20 a 40 mm, limpia y lavada")

    def geo(yc):
        S.poli(caja(yc), 150, cerrada=True, lw=70)
    fila(geo, "Geotextil no tejido clase 2 envolviendo la grava (linea celeste)")

    def tubo(yc):
        p = [(xs + 0.02, yc - 0.019), (xs + 0.24, yc - 0.019), (xs + 0.24, yc + 0.019), (xs + 0.02, yc + 0.019)]
        S.relleno(p, (180, 214, 246), color=151); S.poli(p, 5, cerrada=True)
        for k in range(5): S.punto((xs + 0.14 + k * 0.022, yc), 0.004, 250)
    fila(tubo, "Tubo PVC-U; tramo perforado (puntos) dentro del filtro")

    def flecha(yc):
        S.ln((xs + 0.24, yc), (xs + 0.03, yc), 1)
        S.poli([(xs + 0.03, yc), (xs + 0.07, yc + 0.015), (xs + 0.07, yc - 0.015)], 1, cerrada=True)
        S.t(xs + 0.13, yc + 0.012, "S = 0.5 %", HB * 0.75, 6, al=TA.BOTTOM_CENTER)
    fila(flecha, "Sentido del flujo y pendiente del tubo")
    y -= 0.02

    C1 = [
        ("1. LLORADERO - ELEMENTO", [
            "Tubo PVC-U Ø 3\" (76 mm) para desague, NTP 399.003, de 0.30 m de longitud por lloradero: atraviesa el muro de 0.10 m y entra 0.20 m en el filtro.",
            "El tramo dentro del filtro lleva perforaciones Ø 3/8\" en dos filas a 120°, @0.05 m; el extremo dentro del filtro se tapa con el geotextil."]),
        ("2. UBICACION Y DISTRIBUCION", [
            "Solo en los muros de cuneta colindantes con area verde o terreno natural sin cobertura (hoja METRADO LLORADEROS); no en los tramos junto a veredas, pisos o edificaciones.",
            "Espaciamiento tipico L = 1.50 m, a media altura del muro; el primero y el ultimo a no menos de 0.30 m de las juntas de dilatacion."]),
    ]
    for tit, ps in C1:
        S.t(X1, y, tit, HB, C_TIT, estilo="ARIAL-N"); y -= HB * INTER
        for p in ps:
            y = S.parrafo(X1, y, "- " + p, AC, sangria="  ")
        y -= 0.015
    y1 = y

    C2 = [
        ("3. PENDIENTE E INSTALACION", [
            "Pendiente S = 0.5 % hacia el interior de la cuneta (el extremo exterior, dentro del filtro, queda mas alto); el extremo interior queda al ras de la cara del muro, sin sobresalir. Verificar con nivel: nunca a contrapendiente.",
            "El tubo se fija al encofrado antes del vaciado del muro, con sus extremos tapados para que no entre concreto; el contorno se sella con mortero 1:3 si se coloca despues."]),
        ("4. FILTRO LOCALIZADO (PROTECCION)", [
            "En el lado del terreno, cada lloradero lleva un filtro de 0.30 x 0.30 x 0.30 m (0.027 m³) de grava de 20 a 40 mm, sin finos ni materia organica, envuelto integramente en geotextil.",
            "Geotextil no tejido clase 2 para filtro (ASTM D4491 y D4751), 0.60 m² por lloradero con traslapes de 0.10 m; retiene los finos del suelo y deja pasar el agua hacia la cuneta."]),
        ("5. EJECUCION Y PRUEBA", [
            "Excavar el hueco del filtro despues del desencofrado, forrarlo con el geotextil, llenar con la grava sin dañar la tela y cerrar por encima antes del relleno compactado.",
            "Prueba: al verter agua en el filtro debe salir por el lloradero dentro de la cuneta; se repara el que no drene."]),
    ]
    y = YC - 0.07
    for tit, ps in C2:
        S.t(X2, y, tit, HB, C_TIT, estilo="ARIAL-N"); y -= HB * INTER
        for p in ps:
            y = S.parrafo(X2, y, "- " + p, AC, sangria="  ")
        y -= 0.015

    y = S.titulo(X2, y - 0.02, "CANTIDADES SEGUN EL METRADO", ancho=0.72)
    cab = ["ELEMENTO", "POR UNIDAD", "TOTAL (%d und)" % n]
    filas = [["Lloraderos", "@1.50 m", "%d und en %.2f m de muro" % (n, L)],
             ["Tubo PVC Ø 3\"", "%.2f m" % TUBO_U, "%.2f m" % (n * TUBO_U)],
             ["Grava 20-40 mm", "%.3f m³" % GRAVA_U, "%.2f m³" % (n * GRAVA_U)],
             ["Geotextil clase 2", "%.2f m²" % GEO_U, "%.2f m²" % (n * GEO_U)]]
    anchos = [0.38, 0.30, 0.52]; fh = HB * 1.75
    yy = y + HB * 0.6; ytab = yy
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
    y2 = S.parrafo(X2, yy - HB * 1.3, "Fuente: hoja METRADO LLORADEROS (partida 01.04.03.04.03.04) y ACU de lloraderos.", AC, HB * 0.8)

    yb = min(y1, y2) - 0.04
    sep.dxf.end = (X2 - 0.06, yb)
    blk.add_lwpolyline([(0, yb), (W, yb), (W, YT), (0, YT)], close=True, dxfattribs={"layer": "LEY-MARCO", "color": 250, "lineweight": 50})
    doc.modelspace().add_blockref("ESPEC_LLORADEROS", (0, 0), dxfattribs={"layer": "0"})
    detalle(doc, nombre.split(" - ")[0])
    doc.modelspace().add_blockref("DETALLE_LLORADERO", (W + 0.85, 0.85), dxfattribs={"layer": "0"})
    err = len(doc.audit().errors)
    sal = os.path.join(RAIZ, carpeta, "ESPECIFICACIONES_LLORADEROS_%s.dxf" % suf)
    doc.saveas(sal)
    return sal, (0, yb, W, YT), err, D


if __name__ == "__main__":
    for k in (sys.argv[1:] or PROY):
        sal, caja, err, D = construir(k)
        print(k, os.path.relpath(sal, RAIZ), [round(v, 3) for v in caja], "errores", err, D)
