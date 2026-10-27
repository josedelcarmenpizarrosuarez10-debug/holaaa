# -*- coding: utf-8 -*-
"""Panel fotográfico georreferenciado del estudio de gestión de riesgos SM-107 (CUI 2673852).
Fotografías del estudio de inventario vial (panel fotográfico, setiembre 2026) con fecha y coordenadas UTM impresas por la cámara
(WGS 84, zona 18 S). La progresiva se obtiene proyectando el punto sobre el eje georreferenciado (_calc/eje_terreno.json).
Uso: python3 fotos_sm107.py   (extrae las fotos del .doc del inventario con LibreOffice y las guarda en _calc/fotos/)"""
import os, sys, json, math, glob, shutil, subprocess, tempfile, zipfile

AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import riesgos_sm107 as RS
FOTO = os.path.join(RS.CALC, "fotos")
INV = os.path.join(os.path.dirname(RS.ENT), "insumos", "INFORME_INVENTARIO_VIAL_SM107.doc")
EJE = json.load(open(os.path.join(RS.CALC, "eje_terreno.json")))["eje"]

# imagen del inventario (word/media/imageN.jpeg o .png), Este, Norte, fecha y hora del sello, descripción, riesgos relacionados
CATALOGO = [
    (6, 361552, 9233392, "25/09/2026 13:59", "Inicio del tramo en estudio (km 19+343.39) en la localidad de Tingo de Ponasa; vía afirmada con viviendas a ambos lados.", ["R-10", "R-13", "R-20", "R-27"]),
    (7, 361559, 9233353, "25/09/2026 14:39", "Medición del ancho de la plataforma en Tingo de Ponasa; vegetación y viviendas junto al borde de la vía.", ["R-10"]),
    (12, 361569, 9233352, "25/09/2026 14:05", "Alcantarilla de dos tubos TMC con la entrada obstruida por vegetación y residuos.", ["R-02", "R-06"]),
    (41, 361587, 9233255, "25/09/2026 15:08", "Calzada con baches y viviendas al borde de la vía en Tingo de Ponasa.", ["R-10", "R-20", "R-27"]),
    (14, 361595, 9233027, "25/09/2026 15:58", "Calzada con parchado y bordes sin berma, cerca del desvío hacia la vía SM-803.", ["R-20", "R-27"]),
    (42, 361410.19, 9232492.02, "25/09/2026 16:26", "Puente existente Tingo de Ponasa, de un solo carril (ancho útil 3.20 m), con vegetación en los accesos.", ["R-02", "R-03", "R-21", "R-26", "R-27", "R-33", "R-34"]),
    (15, 361010.23, 9231044.65, "26/09/2026 10:51", "Señal de ingreso a la localidad de Aypena.", ["R-10", "R-13"]),
    (16, 360944, 9230789, "26/09/2026 11:28", "Intersección con vía vecinal en el sector de Aypena; calzada con fisuras y bermas de tierra.", ["R-20", "R-27"]),
    (17, 361620, 9227828, "26/09/2026 15:44", "Señal de ingreso al caserío Nuevo América.", ["R-10", "R-13"]),
    (18, 363161, 9227178, "26/09/2026 16:52", "Señal de ingreso al centro poblado Leoncio Prado.", ["R-10", "R-13"]),
    (19, 365824, 9226267, "27/09/2026 09:22", "Señal de ingreso al centro poblado San Antonio.", ["R-10", "R-13"]),
    (40, 365835, 9226263, "27/09/2026 09:25", "Medición en el borde de la calzada en el sector de San Antonio; plataforma sin berma y con material suelto.", ["R-10", "R-20"]),
    (20, 367783, 9225324, "27/09/2026 11:54", "Localidad de Huañipo frente a la plaza de armas: viviendas y postes junto a la vía.", ["R-10", "R-11", "R-13", "R-20"]),
    (47, 368289, 9225322, "27/09/2026 12:39", "Plataforma angosta en afirmado, en ladera, con vegetación en ambos bordes.", ["R-04", "R-05", "R-07", "R-11"]),
    (48, 368293, 9225342, "27/09/2026 12:43", "Empozamiento y huellas de rodadura sobre la calzada afirmada.", ["R-01", "R-05", "R-06"]),
    (49, 369714, 9226878, "27/09/2026 16:02", "Cantos rodados y agua acumulada sobre la calzada.", ["R-05", "R-06", "R-07"]),
    (50, 369850, 9226904, "27/09/2026 16:08", "Erosión del borde de la plataforma (lado derecho) con pérdida de suelo junto a la calzada; talud de corte al lado izquierdo.", ["R-04", "R-05", "R-21"]),
    (51, 370355, 9226812, "27/09/2026 16:18", "Calzada húmeda con lodo y baches con agua, al final del sector de talud inestable 37+520 a 37+780.", ["R-01", "R-04", "R-06"]),
    (22, 370478, 9226785, "28/09/2026 08:18", "Señal de ingreso a la localidad de Paucar; ladera al lado izquierdo de la vía.", ["R-10", "R-13"]),
    (52, 370541, 9226763, "28/09/2026 08:20", "Medición de un bache con agua turbia y agregado expuesto.", ["R-01", "R-06"]),
    (23, 370855, 9226643, "28/09/2026 08:50", "Acceso a la localidad de Alfonso Ugarte.", ["R-10", "R-13"]),
    (53, 371498, 9226001, "28/09/2026 09:46", "Deterioro de la calzada con agua junto al drenaje lateral, al pie de la ladera.", ["R-05", "R-06"]),
    (54, 371809, 9224794, "28/09/2026 11:09", "Deterioro transversal de la calzada con piedras y humedad en el encuentro con el drenaje lateral.", ["R-06"]),
    (55, 372754, 9223862, "28/09/2026 14:32", "Baches con agua y agregado suelto en plataforma angosta, cerca de la quebrada sin descarga del km 42+280.", ["R-02", "R-06"]),
    (57, 373093, 9223667, "28/09/2026 14:19", "Empozamiento que ocupa todo el ancho de la calzada, con tránsito de vehículos.", ["R-01", "R-06", "R-27"]),
    (56, 373481, 9223706, "28/09/2026 13:59", "Franja húmeda transversal con lodo y agua sobre la calzada.", ["R-06"]),
    (43, 374500, 9223591, "28/09/2026 12:59", "Ingreso a Shamboyacu: calzada con baches y pérdida del revestimiento.", ["R-10", "R-27"]),
    (46, 374744, 9223493, "28/09/2026 12:45", "Calle de concreto en Shamboyacu, al final del tramo, con viviendas y postes a ambos lados.", ["R-10", "R-11", "R-13", "R-20"]),
]


def progresiva(e, n):
    """Progresiva (m) y distancia al eje (m) del punto más cercano del eje georreferenciado."""
    b = min(EJE, key=lambda p: (p[0] - e) ** 2 + (p[1] - n) ** 2)
    return b[2], math.hypot(b[0] - e, b[1] - n)


def punto(prog):
    """Coordenadas UTM del eje en una progresiva (m), interpoladas."""
    for a, b in zip(EJE, EJE[1:]):
        if a[2] <= prog <= b[2]:
            t = (prog - a[2]) / (b[2] - a[2]); return a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
    q = EJE[0] if prog < EJE[0][2] else EJE[-1]; return q[0], q[1]


km = lambda m: "%d+%03d" % divmod(int(round(m)), 1000)


def fotos():
    """Lista de fotos ordenada por progresiva, con su número F-01, F-02..."""
    L = []
    for img, e, n, f, d, rr in CATALOGO:
        pg, dist = progresiva(e, n)
        L.append(dict(img=img, e=e, n=n, fecha=f, desc=d, riesgos=rr, prog=pg, dist=dist))
    L.sort(key=lambda x: x["prog"])
    for i, x in enumerate(L, 1):
        x["id"] = "F-%02d" % i; x["ruta"] = os.path.join(FOTO, "inv_%02d.jpg" % x["img"])
    return L


def extraer():
    from PIL import Image
    os.makedirs(FOTO, exist_ok=True)
    tmp = tempfile.mkdtemp()
    subprocess.run(["soffice", "--headless", "--convert-to", "docx", "--outdir", tmp, INV], check=True, capture_output=True)
    docx = glob.glob(os.path.join(tmp, "*.docx"))[0]
    with zipfile.ZipFile(docx) as z:
        for img, *_ in CATALOGO:
            nom = [n for n in z.namelist() if n.startswith("word/media/image%d." % img)][0]
            with z.open(nom) as f:
                im = Image.open(f).convert("RGB"); im.thumbnail((1280, 1280))
                im.save(os.path.join(FOTO, "inv_%02d.jpg" % img), quality=82)
    shutil.rmtree(tmp)
    for x in fotos(): print(x["id"], km(x["prog"]), "%.0f m del eje" % x["dist"], x["ruta"])


if __name__ == "__main__":
    extraer()
