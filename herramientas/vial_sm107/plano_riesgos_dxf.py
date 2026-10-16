# -*- coding: utf-8 -*-
"""Planos de la gestion de riesgos en la ejecucion de obra - SM-107 Tingo de Ponasa - Shamboyacu (CUI 2673852).
PR-01: plano de ubicacion de riesgos, 1/25,000, en coordenadas UTM WGS 84 zona 18 S reales (el eje sale del plano clave
       PC-01; curvas de nivel cada 10 m del modelo Copernicus GLO-30, referenciales).
PR-02: diagrama lineal de riesgos por progresiva (escala horizontal 1/40,000).
Uso: python3 plano_riesgos_dxf.py"""
import os, sys, json, math
import numpy as np
from ezdxf.enums import TextEntityAlignment as TA
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
for p in (HERR, AQUI):
    if p not in sys.path: sys.path.insert(0, p)
import dxf_base as B
import dxf_layouts as L
import riesgos_sm107 as RS
RS.calcular()

B.PROYECTO = ("MEJORAMIENTO DEL SERVICIO DE TRANSITABILIDAD VIAL INTERURBANA EN LA VIA DEPARTAMENTAL SM-107, TRAMO TINGO DE PONASA -",
              "SHAMBOYACU, DISTRITO DE SHAMBOYACU, PROVINCIA DE PICOTA, DEPARTAMENTO DE SAN MARTIN - CUI N. 2673852")
B.ENTIDAD = "ENTIDAD: GOBIERNO REGIONAL SAN MARTIN - DIRECCION REGIONAL DE TRANSPORTES Y COMUNICACIONES"
B.UBICACION = "UBICACION: TINGO DE PONASA (KM 19+343.39) - SHAMBOYACU (KM 44+693.39) - PICOTA - SAN MARTIN"
B.ESPECIALIDAD = "ESPECIALIDAD: GESTION DE RIESGOS EN LA EJECUCION DE OBRA"
B.ELABORADO = ""
SAL = os.path.join(RAIZ, "entregables_vial_sm107", "PLANOS_GESTION_RIESGOS_SM107.dxf")
CALC = RS.CALC

CAPAS_EXTRA = [("EJE-VIA", 5, "CONTINUOUS"), ("EJE-REFERENCIAL", 5, "DASHED"), ("CURVAS", 9, "CONTINUOUS"), ("CURVAS-MAESTRAS", 8, "CONTINUOUS"),
               ("CUADRICULA", 9, "CONTINUOUS"), ("LOCALIDADES", 7, "CONTINUOUS"), ("PUENTES", 7, "CONTINUOUS"),
               ("R-EROSION", 6, "CONTINUOUS"), ("R-INUNDACION", 150, "CONTINUOUS"), ("R-TALUDES", 1, "CONTINUOUS"),
               ("R-INTERFERENCIAS", 3, "CONTINUOUS"), ("R-RIEGO", 140, "CONTINUOUS"), ("R-PREDIOS", 30, "CONTINUOUS"),
               ("R-PLATAFORMA", 8, "CONTINUOUS"), ("R-PUENTES", 1, "CONTINUOUS"), ("R-EXPEDIENTE", 210, "DASHED"),
               ("NIVEL-ALTO", 1, "CONTINUOUS"), ("NIVEL-MODERADO", 30, "CONTINUOUS"), ("NIVEL-BAJO", 3, "CONTINUOUS")]
RGB = {"R-RIEGO": (0, 140, 140), "R-INUNDACION": (40, 110, 220), "R-PREDIOS": (230, 130, 0), "R-PLATAFORMA": (120, 120, 120),
       "NIVEL-ALTO": (230, 60, 60), "NIVEL-MODERADO": (245, 190, 40), "NIVEL-BAJO": (110, 180, 90),
       "R-EROSION": (220, 0, 220), "R-TALUDES": (230, 0, 0), "R-INTERFERENCIAS": (0, 200, 0), "R-PUENTES": (230, 0, 0)}
B.COLOR_RGB.update({k: v for k, v in RGB.items() if k.startswith(("R-", "NIVEL-"))})

EJE = json.load(open(os.path.join(CALC, "eje_terreno.json")))
XYP = np.array(EJE["eje"])                    # E, N, progresiva


def pk(prog):
    """punto del eje y direccion en una progresiva (m)"""
    i = int(np.clip(np.searchsorted(XYP[:, 2], prog), 1, len(XYP) - 1))
    a, b = XYP[i - 1], XYP[i]; t = (prog - a[2]) / max(b[2] - a[2], 1e-6)
    p = a[:2] + t * (b[:2] - a[:2]); d = (b[:2] - a[:2]) / max(np.hypot(*(b[:2] - a[:2])), 1e-6)
    return p, d


def tramo(p0, p1):
    m = (XYP[:, 2] > p0) & (XYP[:, 2] < p1)
    return [tuple(pk(p0)[0])] + [tuple(x) for x in XYP[m, :2]] + [tuple(pk(p1)[0])]


def km(t):
    k, m = t.split("+"); return int(k) * 1000 + float(m)


def txt_prog(p):
    return "%d+%03d" % (int(p // 1000), int(round(p % 1000)) % 1000)


LOCALIDADES = [("TINGO DE PONASA", 19560), ("AYPENA", 21940), ("NUEVO AMERICA", 26270), ("LEONCIO PRADO", 28080), ("SAN ANTONIO", 31420),
               ("HUANIPO", 33780), ("PAUCAR", 38020), ("ALFONSO UGARTE", 38730), ("SHAMBOYACU", 44500)]
PUENTES = [("PTE. TINGO DE PONASA L=40 m", 20300), ("PTE. BARCO L=40 m", 29300), ("PTE. PAUCARILLO L=20 m", 37870),
           ("PTE. APANGURAYCO L=15 m", 38800), ("PTE. CHANCHAMAYCO L=12 m", 44040)]
# sectores (capa, prog_ini, prog_fin, etiqueta, codigos)
SECTORES = [("R-INUNDACION", 20360, 21170, "INUNDACION ARROZALES", "R-06"), ("R-INUNDACION", 22800, 22960, "EMPOZAMIENTO", "R-06"),
            ("R-EROSION", 34766, 34786, "EROSION h=3 m", "R-05"), ("R-EROSION", 36380, 36460, "EROSION h=2 m", "R-05"),
            ("R-EROSION", 39380, 39840, "EROSION h=3-5 m", "R-05"), ("R-EROSION", 43620, 43632, "EROSION h=1 m", "R-05"),
            ("R-EROSION", 20337, 20340, "EROSION h=2 m", "R-05"),
            ("R-TALUDES", 36060, 36100, "TALUD h=20 m", "R-04"), ("R-TALUDES", 37520, 37780, "TALUD h=30 m", "R-04"),
            ("R-RIEGO", 31100, 31920, "CANAL DE RIEGO", "R-12"),
            ("R-PLATAFORMA", 34400, 34900, "PLATAFORMA ANGOSTA", "R-27"), ("R-PLATAFORMA", 35200, 39000, "PLATAFORMA ANGOSTA", "R-27"),
            ("R-PLATAFORMA", 40000, 40300, "PLATAFORMA ANGOSTA", "R-27"), ("R-PLATAFORMA", 40600, 42000, "PLATAFORMA ANGOSTA", "R-27"),
            ("R-PLATAFORMA", 42300, 44600, "PLATAFORMA ANGOSTA", "R-27")]
PUNTOS = [("R-INUNDACION", 22270, "EMPOZAMIENTO", "R-06"), ("R-INUNDACION", 26924, "EMPOZAMIENTO SIN DESCARGA", "R-06"),
          ("R-INUNDACION", 34954, "EMPOZAMIENTO SIN DESCARGA", "R-06"), ("R-INUNDACION", 40380, "EMPOZAMIENTO SIN DESCARGA", "R-06"),
          ("R-INUNDACION", 42280, "QUEBRADA SIN DESCARGA", "R-06"), ("R-INUNDACION", 43660, "EMPOZAMIENTO SIN DESCARGA", "R-06"),
          ("R-INTERFERENCIAS", 22425, "PASE DE AGUA POTABLE", "R-11"), ("R-INTERFERENCIAS", 25715, "PASE PVC 21 pulg.", "R-11"),
          ("R-INTERFERENCIAS", 34688, "PASE PVC 6 pulg.", "R-11"),
          ("R-RIEGO", 32578, "CRUCE DE CANAL", "R-12"), ("R-RIEGO", 35950, "CRUCE DE CANAL", "R-12"), ("R-RIEGO", 36120, "CRUCE DE CANAL", "R-12"),
          ("R-RIEGO", 37400, "CRUCE DE CANAL", "R-12"), ("R-RIEGO", 37794, "CRUCE DE CANAL", "R-12"), ("R-RIEGO", 38370, "CRUCE DE CANAL", "R-12")]


def preparar(doc):
    for n, c, lt in CAPAS_EXTRA:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt)
            if n in RGB: ly.rgb = RGB[n]
    doc.layers.get("EJE-VIA").dxf.lineweight = 60; doc.layers.get("CURVAS").dxf.lineweight = 9; doc.layers.get("CURVAS-MAESTRAS").dxf.lineweight = 18
    for n in ("R-EROSION", "R-INUNDACION", "R-TALUDES", "R-RIEGO", "R-PLATAFORMA", "R-PREDIOS"): doc.layers.get(n).dxf.lineweight = 100


def curvas(lam, bbox, buffer_m=2200.0):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    d = np.load(os.path.join(CALC, "dem_corredor.npz")); Z = d["Z"].astype(float); c, f, a, e = d["tr"]
    from scipy.ndimage import gaussian_filter
    Zs = gaussian_filter(np.nan_to_num(Z, nan=np.nanmean(Z)), 2.0)          # suaviza el ruido del dosel (DSM)
    xs = c + a * (np.arange(Z.shape[1]) + 0.5); ys = f + e * (np.arange(Z.shape[0]) + 0.5)
    # mascara: distancia al eje
    from scipy.spatial import cKDTree
    tree = cKDTree(XYP[::3, :2])
    niveles = np.arange(230, 340, 10)
    cs = plt.contour(xs, ys, Zs, levels=niveles); plt.close()
    x0, y0, x1, y1 = bbox
    for lev, segs in zip(cs.levels, cs.allsegs):
        capa = "CURVAS-MAESTRAS" if lev % 50 == 0 else "CURVAS"
        for sg in segs:
            if len(sg) < 4: continue
            dist, _ = tree.query(sg)
            dentro = (dist < buffer_m) & (sg[:, 0] > x0) & (sg[:, 0] < x1) & (sg[:, 1] > y0) & (sg[:, 1] < y1)
            # cortar en tramos continuos dentro de la franja
            idx = np.where(dentro)[0]
            if len(idx) < 4: continue
            cortes = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
            for ct in cortes:
                if len(ct) < 4: continue
                pts = sg[ct][::2] if len(ct) > 8 else sg[ct]
                lam.poli([tuple(p) for p in pts], capa)
                if capa == "CURVAS-MAESTRAS" and len(ct) > 40:
                    pm = sg[ct[len(ct) // 2]]
                    lam.texto(tuple(pm), "%d" % lev, 1.6, "CURVAS-MAESTRAS", TA.MIDDLE_CENTER)


def nivel_capa(cod):
    r = next(x for x in RS.R if x["cod"] == cod)
    return {"ALTO": "NIVEL-ALTO", "MODERADO": "NIVEL-MODERADO", "BAJO": "NIVEL-BAJO"}[r["nivel"]]


def pr01(doc):
    esc = 25000
    ox, oy = 360050.0, 9219100.0                  # lamina: x 30 mm = E 360 800, y 168 mm = N 9 223 300
    lam = B.Lamina(doc, ox, oy, esc, "PR-01", "PLANO DE UBICACION DE RIESGOS EN LA EJECUCION DE OBRA",
                   "EJE, PROGRESIVAS, LOCALIDADES, PUENTES Y SECTORES CON RIESGO IDENTIFICADO - ESC. 1/25,000 - UTM WGS 84 ZONA 18 S", escala_txt="1/25,000")
    mx0, my0, mx1, my1 = 30, 168, 602, 578
    X0, Y0 = lam.P(mx0, my0); X1, Y1 = lam.P(mx1, my1)
    lam.rect(X0, Y0, X1, Y1, "MARCO")
    curvas(lam, (X0, Y0, X1, Y1))
    # cuadricula UTM cada 2 km
    for E in range(362000, 376000, 2000):
        if X0 < E < X1:
            lam.linea((E, Y0), (E, Y1), "CUADRICULA")
            lam.texto((E, Y1 + lam.mm(1.5)), "%d E" % E, 1.8, "TEXTOS", TA.BOTTOM_CENTER)
            lam.texto((E, Y0 - lam.mm(1.5)), "%d E" % E, 1.8, "TEXTOS", TA.TOP_CENTER)
    for N in range(9224000, 9234000, 2000):
        if Y0 < N < Y1:
            lam.linea((X0, N), (X1, N), "CUADRICULA")
            lam.texto((X0 - lam.mm(1.5), N), "%d N" % N, 1.8, "TEXTOS", TA.MIDDLE_RIGHT, rot=90)
            lam.texto((X1 + lam.mm(1.5), N), "%d N" % N, 1.8, "TEXTOS", TA.MIDDLE_LEFT, rot=90)
    # eje
    prog_pc = EJE["prog0"] + EJE["longitud_pc01_m"]
    m = XYP[:, 2] <= prog_pc + 1
    lam.poli([tuple(p) for p in XYP[m, :2]], "EJE-VIA")
    lam.poli([tuple(XYP[m, :2][-1])] + [tuple(p) for p in XYP[~m, :2]], "EJE-REFERENCIAL")
    # progresivas cada km
    for k in range(20, 45):
        p, d = pk(k * 1000.0); n = np.array([-d[1], d[0]])
        a = p + n * lam.mm(1.6); b = p - n * lam.mm(1.6)
        lam.linea(tuple(a), tuple(b), "PROGRESIVAS")
        ang = math.degrees(math.atan2(n[1], n[0]))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        q = p - n * lam.mm(3.2) if n[1] < 0 or (abs(n[1]) < 0.2 and n[0] < 0) else p + n * lam.mm(3.2)
        lam.texto(tuple(q), "KM %d" % k, 1.8, "PROGRESIVAS", TA.MIDDLE_CENTER, rot=0)
    for t, pr in (("INICIO KM 19+343.39", 19343.39), ("FIN KM 44+693.39", 44693.39), ("FIN DEL EJE EN PC-01 KM 44+090", prog_pc)):
        p, d = pk(pr); lam.circulo(tuple(p), lam.mm(1.2), "EJE-VIA")
    p, _ = pk(19343.39); lam.texto((p[0] + lam.mm(4), p[1] + lam.mm(2)), "INICIO KM 19+343.39", 2.2, "TITULOS")
    p, _ = pk(44693.39); lam.linea(tuple(p), (X1 + lam.mm(1.5), p[1]), "LLAMADAS"); lam.texto((X1 + lam.mm(2.5), p[1]), "FIN KM 44+693.39", 2.2, "TITULOS", TA.MIDDLE_LEFT)
    # sectores y puntos
    for capa, a, b, et, cod in sorted(SECTORES, key=lambda x: x[0] != "R-PLATAFORMA"):
        lam.poli(tramo(a, b), capa, ancho=lam.mm(0.9 if capa == "R-PLATAFORMA" else 1.8))
    for capa, pr, et, cod in PUNTOS:
        p, _ = pk(pr); lam.circulo(tuple(p), lam.mm(1.3), capa)
        h = lam.msp.add_hatch(color=256, dxfattribs={"layer": capa}); h.paths.add_edge_path().add_arc(tuple(p), lam.mm(1.3), 0, 360)
    # localidades (zona urbana: riesgo de predios R-10)
    for nom, pr in LOCALIDADES:
        p, d = pk(pr); n = np.array([-d[1], d[0]])
        lam.poli(tramo(max(pr - 250, 19343.4), min(pr + 250, 44693)), "R-PREDIOS", ancho=lam.mm(0.6))
        q = p + n * lam.mm(9) if n[1] > 0 else p - n * lam.mm(9)
        lam.texto(tuple(q), nom, 2.4, "LOCALIDADES", TA.MIDDLE_CENTER)
    # puentes
    for nom, pr in PUENTES:
        p, d = pk(pr); n = np.array([-d[1], d[0]])
        for s_ in (-1, 1):
            a = p + d * lam.mm(1.6) * s_
            lam.poli([tuple(a + n * lam.mm(3.0) + d * lam.mm(0.8) * s_), tuple(a + n * lam.mm(2.4)), tuple(a - n * lam.mm(2.4)),
                      tuple(a - n * lam.mm(3.0) + d * lam.mm(0.8) * s_)], "R-PUENTES", ancho=lam.mm(0.45))
    # etiquetas de riesgos (columna de llamadas a la derecha de cada grupo)
    etiquetas = [(20300, "R-03 R-27 R-33 R-34  PUENTE TINGO DE PONASA (20+300)"), (20765, "R-06  INUNDACION POR ARROZALES 20+360-21+170"),
                 (22600, "R-06 R-11  EMPOZAMIENTOS 22+270, 22+800-22+960; PASE AGUA 22+425"), (25715, "R-11  PASE PVC 21 pulg. 25+715"),
                 (26924, "R-06  EMPOZAMIENTO SIN DESCARGA 26+924"), (29300, "R-03 R-27 R-33 R-34  PUENTE BARCO (29+300)"),
                 (31510, "R-12  CANAL DE RIEGO 31+100-31+920"), (32578, "R-12  CRUCE DE CANAL 32+578"),
                 (34800, "R-05 R-06 R-11  EROSION 34+766, EMPOZAMIENTO 34+954, PVC 34+688"), (36080, "R-04  TALUD h=20 m 36+060-36+100"),
                 (36420, "R-05  EROSION h=2 m 36+380-36+460"), (37650, "R-04  TALUD h=30 m 37+520-37+780"),
                 (37870, "R-03 R-27 R-33  PUENTE PAUCARILLO (37+870)"), (38800, "R-03 R-27 R-33  PUENTE APANGURAYCO (38+800)"),
                 (39610, "R-05  EROSION h=3-5 m 39+380-39+840"), (40380, "R-06  EMPOZAMIENTO 40+380"), (42280, "R-06  QUEBRADA SIN DESCARGA 42+280"),
                 (43640, "R-05 R-06  EROSION 43+620, EMPOZAMIENTO 43+660"), (44040, "R-03 R-27 R-33  PUENTE CHANCHAMAYCO (44+040)")]
    return lam, etiquetas, (mx0, my0, mx1, my1)


def llamadas(lam, etiquetas, caja):
    """Marcas numeradas junto a cada punto o sector (al lado del eje con más espacio) y su cuadro de descripción."""
    from scipy.spatial import cKDTree
    tree = cKDTree(XYP[:, :2]); r = lam.mm(2.6); off = lam.mm(8.0)
    puestos = []
    for k, (pr, t) in enumerate(etiquetas, 1):
        p, d = pk(pr); n = np.array([-d[1], d[0]])
        mejor = None
        for s_ in (1, -1):
            for f in (1.0, 1.5, 2.0, 2.6, 3.2):
                q = p + s_ * n * off * f
                lejos = tree.query(q, k=60)[0].min()
                choque = min([np.hypot(*(q - x)) for x in puestos] or [9e9])
                pts = q if lejos > off * 0.8 and choque > 3.4 * r else None
                if pts is not None:
                    sc = lejos + min(choque, 3 * r)
                    if mejor is None or sc > mejor[0]: mejor = (sc, q)
            if mejor is not None and mejor[0] > 2 * off: break
        q = mejor[1] if mejor else p + n * off
        puestos.append(q)
        u = (q - p) / max(np.hypot(*(q - p)), 1e-6)
        lam.linea(tuple(p), tuple(q - u * r), "LLAMADAS")
        lam.circulo(tuple(q), r, "TITULOS"); lam.texto(tuple(q), "%d" % k, 2.1, "TITULOS", TA.MIDDLE_CENTER)


def leyenda_y_cuadro(lam, etiquetas):
    y = lam.leyenda2(612, 572, [("linea2", "EJE-VIA", "Eje de via (plano clave PC-01, georreferenciado)"),
                                ("discontinua", "EJE-REFERENCIAL", "Tramo final 44+090 a 44+693 (referencial)"),
                                ("linea2", "R-INUNDACION", "Inundacion / empozamiento (R-06)"), ("linea2", "R-EROSION", "Erosion de plataforma (R-05)"),
                                ("linea2", "R-TALUDES", "Inestabilidad de taludes (R-04)"), ("linea2", "R-RIEGO", "Canal y cruces de riego (R-12)"),
                                ("linea2", "R-PLATAFORMA", "Plataforma angosta: transito en obra (R-20, R-27)"),
                                ("linea2", "R-PREDIOS", "Zona poblada: libre disponibilidad (R-10, R-13)"),
                                ("punto", "R-INTERFERENCIAS", "Interferencia de servicios (R-11)", 3),
                                ("linea2", "R-PUENTES", "Puente a reemplazar (R-03, R-27, R-33, R-34)"),
                                ("linea", "CURVAS", "Curvas de nivel cada 10 m (Copernicus GLO-30, referencial)")], 1.8)
    filas = [[str(k), t.split("  ", 1)[1] if "  " in t else t, t.split("  ", 1)[0]] for k, (pr, t) in enumerate(etiquetas, 1)]
    yt = lam.tabla(612, y - 9, ["N.", "PUNTO O SECTOR", "RIESGOS"], filas, [8, 140, 61], hmm=1.55, alto_mm=4.3, titulo="PUNTOS Y SECTORES DE RIESGO")
    lam.notas(612, yt - 8, "NOTAS", [
        "1. Coordenadas UTM WGS 84 zona 18 S. El eje se tomo del plano clave PC-01 (DRTC San Martin, nov. 2024) y se georreferencio con su "
        "cuadricula: los puntos geodesicos y BM del inventario vial quedan a 4-12 m del eje (PC-4 a 52 m).",
        "2. Progresivas = 19+343.39 + distancia sobre el eje; coinciden con el inventario (Huanipo 33+803, Aypena 21+993).",
        "3. Sectores y puntos segun el estudio de inventario vial (zonas criticas, drenaje, cruces de canal e interferencias).",
        "4. Curvas de un modelo digital de superficie de 30 m que incluye la vegetacion: solo ubican el relieve.",
        "5. Codigos R-xx de la matriz de gestion de riesgos (Excel) y del estudio (Word)."], 1.6, ancho_mm=215)
    top = sorted(RS.R, key=lambda r: (-r["PxI"], r["cod"]))[:14]
    sin = lambda t: t.upper().translate(str.maketrans("ÁÉÍÓÚÑÜ", "AEIOUNU"))
    filas = [[r["cod"], sin(r["riesgo"]), sin(r["asig"]), "%.2f" % r["PxI"], r["nivel"], "%.3f" % r["PxIr"], r["nivel_r"]] for r in top]
    lam.tabla(30, 150, ["COD.", "RIESGO", "ASIGNADO A", "P x I", "INHERENTE", "P x I RES.", "RESIDUAL"], filas, [13, 400, 28, 15, 24, 18, 24],
              hmm=1.7, alto_mm=4.6, titulo="RIESGOS DE MAYOR NIVEL (ANALISIS CUALITATIVO P x I)")


def pr02(doc):
    esc = 40000
    ox, oy = 360050.0, 9180000.0
    lam = B.Lamina(doc, ox, oy, esc, "PR-02", "DIAGRAMA LINEAL DE RIESGOS POR PROGRESIVA",
                   "SECTORES, OBRAS Y RIESGOS UBICADOS A LO LARGO DEL TRAMO 19+343.39 - 44+693.39 - ESC. HORIZONTAL 1/40,000", escala_txt="H 1/40,000")
    x0mm = 100.0
    X = lambda prog: x0mm + (prog - 19343.39) / esc * 1000.0
    filas = [("LOCALIDADES", 540), ("PUENTES Y OBRAS DE ARTE", 515), ("INUNDACION Y EMPOZAMIENTO (R-06)", 490), ("EROSION (R-05)", 465),
             ("TALUDES (R-04)", 440), ("RIEGO E INTERFERENCIAS (R-11, R-12)", 415), ("PLATAFORMA ANGOSTA (R-20, R-27)", 390),
             ("PENDIENTE DEL ENTORNO (DSM)", 365), ("COTA DEL TERRENO (DSM)", 330), ("NIVEL DE RIESGO DEL SECTOR", 285)]
    xf = X(44693.39)
    for nom, y in filas:
        lam.texto(lam.P(28, y), nom, 1.7, "TEXTOS", TA.MIDDLE_LEFT)
        lam.linea(lam.P(x0mm, y - 10), lam.P(xf, y - 10), "GRILLA")
    # escala de progresivas
    for k in range(20, 45):
        x = X(k * 1000.0)
        lam.linea(lam.P(x, 552), lam.P(x, 262), "GRILLA")
        lam.texto(lam.P(x, 556), "%d+000" % k, 1.8, "PROGRESIVAS", TA.BOTTOM_CENTER)
    lam.linea(lam.P(x0mm, 552), lam.P(xf, 552), "EJE-VIA")
    lam.texto(lam.P(x0mm, 562), "19+343.39", 1.8, "PROGRESIVAS", TA.BOTTOM_LEFT); lam.texto(lam.P(xf, 562), "44+693.39", 1.8, "PROGRESIVAS", TA.BOTTOM_RIGHT)
    def barra(y, a, b, capa, h=5.0):
        x1, x2 = X(a), max(X(b), X(a) + 0.8)
        pts = [lam.P(x1, y - h / 2), lam.P(x2, y - h / 2), lam.P(x2, y + h / 2), lam.P(x1, y + h / 2)]
        lam.relleno(pts, capa); lam.poli(pts, capa, cerrada=True)
    def marca(y, a, capa, txt=None):
        lam.circulo(lam.P(X(a), y), lam.mm(1.4), capa)
        h = lam.msp.add_hatch(color=256, dxfattribs={"layer": capa}); h.paths.add_edge_path().add_arc(lam.P(X(a), y), lam.mm(1.4), 0, 360)
    for k, (nom, pr) in enumerate(LOCALIDADES):
        barra(540, pr - 250, pr + 250, "R-PREDIOS", 3.0)
        lam.texto(lam.P(X(pr), 545 if k % 2 == 0 else 533.5), nom, 1.5, "LOCALIDADES", TA.MIDDLE_CENTER)
    for k, (nom, pr) in enumerate(PUENTES):
        for dx in (-1.5, 1.5): lam.poli([lam.P(X(pr) + dx, 512), lam.P(X(pr) + dx, 520)], "R-PUENTES", ancho=lam.mm(0.6))
        lam.texto(lam.P(X(pr), 509 if k % 2 == 0 else 522), nom.replace("PTE. ", ""), 1.4, "TEXTOS", TA.MIDDLE_CENTER)
    fila = {"R-INUNDACION": 490, "R-EROSION": 465, "R-TALUDES": 440, "R-RIEGO": 415, "R-INTERFERENCIAS": 415, "R-PLATAFORMA": 390}
    for capa, a, b, et, cod in SECTORES: barra(fila[capa], a, b, capa)
    for capa, pr, et, cod in PUNTOS: marca(fila[capa], pr, capa)
    # pendiente y cota del DSM cada 100 m
    T = EJE.get("tramos_100m", [])
    if T:
        for t in T:
            pmax = t["pend_max_grados"]
            capa = "NIVEL-ALTO" if pmax >= 25 else ("NIVEL-MODERADO" if pmax >= 15 else "NIVEL-BAJO")
            barra(365, t["pi"], t["pf"], capa, 6.0)
        zmin, zmax = 230.0, 330.0
        yb, yt = 312.0, 348.0
        pts = [lam.P(X((t["pi"] + t["pf"]) / 2), yb + (t["z"] - zmin) / (zmax - zmin) * (yt - yb)) for t in T]
        lam.poli(pts, "TERRENO")
        for z in (250, 275, 300, 325):
            y = yb + (z - zmin) / (zmax - zmin) * (yt - yb)
            lam.linea(lam.P(x0mm - 2, y), lam.P(x0mm, y), "TEXTOS"); lam.texto(lam.P(x0mm - 3, y), "%d" % z, 1.4, "TEXTOS", TA.MIDDLE_RIGHT)
        lam.texto(lam.P(28, 358), "verde < 15 grados, ambar 15-25, rojo > 25", 1.4, "TEXTOS", TA.MIDDLE_LEFT)
    # nivel de riesgo por sector (km): el mayor nivel inherente de los riesgos ubicados en cada km
    rk = {}
    for capa, a, b, et, cod in SECTORES:
        for k in range(int(a // 1000), int(b // 1000) + 1): rk.setdefault(k, set()).add(cod)
    for capa, pr, et, cod in PUNTOS: rk.setdefault(int(pr // 1000), set()).add(cod)
    for nom, pr in PUENTES: rk.setdefault(int(pr // 1000), set()).update({"R-03", "R-27", "R-33"} | ({"R-34"} if "40" in nom else set()))
    for nom, pr in LOCALIDADES: rk.setdefault(int(pr // 1000), set()).add("R-10")
    ordn = {"ALTO": 2, "MODERADO": 1, "BAJO": 0}
    for k in range(19, 45):
        cods = sorted(rk.get(k, set()))
        a = max(k * 1000.0, 19343.39); b = min((k + 1) * 1000.0, 44693.39)
        if not cods:
            barra(285, a, b, "NIVEL-BAJO", 8.0); continue
        niv = max((next(x for x in RS.R if x["cod"] == c)["nivel"] for c in cods), key=lambda v: ordn[v])
        barra(285, a, b, {"ALTO": "NIVEL-ALTO", "MODERADO": "NIVEL-MODERADO", "BAJO": "NIVEL-BAJO"}[niv], 8.0)
        for j, c in enumerate(cods[:6]): lam.texto(lam.P((X(a) + X(b)) / 2, 278 - j * 3.2), c, 1.4, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto(lam.P(28, 276), "(mayor nivel inherente de los", 1.4, "TEXTOS", TA.MIDDLE_LEFT); lam.texto(lam.P(28, 272.5), "riesgos ubicados en el km)", 1.4, "TEXTOS", TA.MIDDLE_LEFT)
    # riesgos de todo el tramo y nota
    lam.notas(30, 245, "RIESGOS QUE AFECTAN TODO EL TRAMO (NO UBICABLES EN UNA PROGRESIVA)", [
        "R-01 Lluvias estacionales (ALTO). R-02 Lluvias extraordinarias / El Nino. R-07 Subrasante de menor capacidad. R-08 Canteras y transporte (ALTO). "
        "R-09 Permisos de agua y cauce. R-13 Conflictos sociales. R-14 Arqueologia. R-15 Certificacion ambiental (ALTO). R-16 Expediente tecnico. "
        "R-17 Precios de insumos. R-18 Suministros. R-19 Equipos. R-21 Accidentes de trabajo. R-22 Sismo. R-23 Financiamiento. R-24 Decisiones de la Entidad. "
        "R-25 DME insuficientes (ALTO). R-26 Contaminacion. R-28 Calidad. R-29 Dengue. R-30 Gremios. R-31 Robos. R-32 Quemas agricolas.",
        "Fuentes: estudio de inventario vial (zonas criticas, obras de drenaje, cruces y senales), plano clave PC-01, presupuesto S10 y modelo Copernicus GLO-30."],
        1.8, ancho_mm=600)
    lam.leyenda2(30, 175, [("relleno", "R-INUNDACION", "Inundacion / empozamiento"), ("relleno", "R-EROSION", "Erosion"), ("relleno", "R-TALUDES", "Taludes"),
                           ("relleno", "R-RIEGO", "Riego"), ("punto", "R-INTERFERENCIAS", "Interferencia", 3), ("relleno", "R-PLATAFORMA", "Plataforma angosta"),
                           ("relleno", "R-PREDIOS", "Zona poblada"), ("relleno", "NIVEL-ALTO", "Nivel ALTO"), ("relleno", "NIVEL-MODERADO", "Nivel MODERADO"),
                           ("relleno", "NIVEL-BAJO", "Nivel BAJO")], 1.8, ancho_col=110, filas_col=4)
    return lam


def main():
    doc = B.nuevo_documento(); preparar(doc)
    lam, et, caja = pr01(doc); llamadas(lam, et, caja); leyenda_y_cuadro(lam, et)
    lam2 = pr02(doc)
    cajas = {l.codigo: (l.ox, l.oy, l.ox + l.W * l.f, l.oy + l.H * l.f) for l in (lam, lam2)}
    L.presentaciones(doc, {lam.codigo: lam, lam2.codigo: lam2})
    doc.saveas(SAL); json.dump(cajas, open(os.path.join(CALC, "laminas_pr.json"), "w"), indent=1)
    print(SAL, cajas)


if __name__ == "__main__":
    main()
