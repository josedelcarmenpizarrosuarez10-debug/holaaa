"""Analisis estadistico de la precipitacion maxima en 24 h de la I.E. N.° 0590 Barranquita (C.I. 468901), en el formato del usuario.

Plantilla: insumos/barranquita/plantillas/ANALISIS_ESTADISTICO_-_CAR_VARONES.xlsx (hojas A. Estacion, B. Modelo Distribucion,
C. Prueba Kolmogorov-Smirnov, D. Resumen, A. Parametros, B. Int. maxima y C. P diseno, con sus formulas y graficos).
Se abre con LibreOffice (UNO), se cargan los datos de la estacion Pongo de Caynarachi (SENAMHI 003317, 25 anios 1989-2013)
y se eliminan las filas sobrantes del registro de 26 anios: LibreOffice ajusta solo las formulas y los rangos de los graficos.
La columna "Diseno" del resumen toma la distribucion que selecciona la prueba de Kolmogorov-Smirnov de la misma hoja.
Las hojas auxiliares de la plantilla (Hoja1, 210) no forman parte del analisis y se quitan.
Salida: entregables_barranquita/ANALISIS_ESTADISTICO_IE0590_BARRANQUITA.xlsx (con los valores calculados).
"""
import os, sys, time, shutil, subprocess, tempfile
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import hidrologia_b as H

PLANTILLA = os.path.join(RAIZ, "insumos", "barranquita", "plantillas", "ANALISIS_ESTADISTICO_-_CAR_VARONES.xlsx")
SAL = os.path.join(RAIZ, "entregables_barranquita", "ANALISIS_ESTADISTICO_IE0590_BARRANQUITA.xlsx")
PROYECTO = ("“MEJORAMIENTO Y AMPLIACIÓN DEL SERVICIO DE EDUCACIÓN PRIMARIA EN I.E. N° 0590 DISTRITO DE BARRANQUITA DE LA PROVINCIA DE "
            "LAMAS DEL DEPARTAMENTO DE SAN MARTÍN”, con C.I. N.° 468901")
ENTIDAD = "GOBIERNO REGIONAL SAN MARTIN - GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO"
UBIC = "SAN MARTIN - LAMAS - BARRANQUITA"
FECHA = "OCTUBRE 2026"
KS = "C. Prueba Kolmorov-Smirnov"
FILA0 = 18                    # primera fila del registro en la hoja A. Estacion (26 filas en la plantilla: 18 a 43)


def _conectar():
    import uno
    tmp = tempfile.mkdtemp(); puerto = 2083
    proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--norestore", "-env:UserInstallation=file://%s/perfil" % tmp,
                             "--accept=socket,host=localhost,port=%d;urp;" % puerto], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    local = uno.getComponentContext()
    res = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(60):
        try:
            ctx = res.resolve("uno:socket,host=localhost,port=%d;urp;StarOffice.ComponentContext" % puerto); break
        except Exception:
            time.sleep(0.5)
    else:
        proc.kill(); raise SystemExit("No se pudo iniciar LibreOffice")
    desk = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    return proc, desk


def _prop(n, v):
    from com.sun.star.beans import PropertyValue
    p = PropertyValue(); p.Name = n; p.Value = v; return p


def construir():
    import uno
    serie = list(H.SERIE.items()); n = len(serie)
    e = H.ESTACION
    proc, desk = _conectar()
    try:
        url = uno.systemPathToFileUrl(os.path.abspath(PLANTILLA))
        doc = desk.loadComponentFromURL(url, "_blank", 0, (_prop("Hidden", True),))
        sh = doc.Sheets
        A = sh.getByName("A. Estación"); B = sh.getByName("B.Modelo Distribución"); C = sh.getByName(KS); D = sh.getByName("D.Resumen")
        txt = lambda hoja, ref, v: hoja.getCellRangeByName(ref).setString(v)
        num = lambda hoja, ref, v: hoja.getCellRangeByName(ref).setValue(v)
        fml = lambda hoja, ref, v: hoja.getCellRangeByName(ref).setFormula(v)
        # ---------------------------------------------------------------- datos del proyecto y de la estacion
        txt(A, "C2", PROYECTO); txt(A, "C3", ENTIDAD); txt(A, "C4", UBIC); txt(A, "C5", FECHA)
        txt(A, "B9", "REGISTRO DE PRECIPITACIONES MÁXIMAS EN 24 HORAS  (mm) - %s" % e["nombre"].upper())
        for ref, v in (("B11", "Código"), ("C11", e["codigo"]), ("B12", "Tipo"), ("C12", "Convencional"),
                       ("B13", "Altura"), ("C13", "%d msnm." % e["altitud"]), ("G11", ": SAN MARTIN"), ("G12", ": LAMAS"), ("G13", ": CAYNARACHI")):
            txt(A, ref, v)
        from com.sun.star.table.CellHoriJustify import LEFT
        A.getCellRangeByName("C11:C13").HoriJustify = LEFT
        txt(A, "B15", "Precipitación Máxima en 24 Horas (mm) - periodo %s" % e["periodo"])
        # resaltado de los meses sin dato (la plantilla resaltaba los de su anio 2020, fila 39)
        resal = A.getCellRangeByName("F39").CellBackColor; normal = A.getCellRangeByName("C38").CellBackColor
        A.getCellRangeByName("C39:N39").CellBackColor = normal
        for i, (anio, meses) in enumerate(serie):
            r = FILA0 + i
            num(A, "B%d" % r, anio)
            for j, v in enumerate(meses):
                col = "CDEFGHIJKLMN"[j]
                if v is None:
                    txt(A, "%s%d" % (col, r), "S/D"); A.getCellRangeByName("%s%d" % (col, r)).CellBackColor = resal
                else: num(A, "%s%d" % (col, r), v)
        for i, (anio, _) in enumerate(serie): num(B, "B%d" % (11 + i), anio)
        # ---------------------------------------------------------------- distribucion de diseno = la que selecciona la prueba K-S
        for r in range(10, 19):
            fml(D, "L%d" % r, "=IF($'%s'.$G$55=\"Normal\";H{r};IF($'%s'.$G$55=\"Log - Normal\";I{r};IF($'%s'.$G$55=\"Gumbel\";K{r};J{r})))".format(r=r) % (KS, KS, KS))
        fml(C, "Z48", "=MAX(Z22:Z47)")
        # columna resaltada del resumen = distribucion de diseno (la plantilla resaltaba Log Normal, columna I)
        sel0 = {"normal": "H", "lognormal": "I", "lp3": "J", "gumbel": "K"}[H.analisis()["elegida"]]
        res_c = D.getCellRangeByName("I10").CellBackColor; nor_c = D.getCellRangeByName("H10").CellBackColor
        D.getCellRangeByName("I10:I18").CellBackColor = nor_c; D.getCellRangeByName("%s10:%s18" % (sel0, sel0)).CellBackColor = res_c
        # titulos de los graficos con el nombre de la estacion
        for i in range(sh.Count):
            ch = sh.getByIndex(i).getCharts()
            for j in range(ch.Count):
                cd = ch.getByIndex(j).getEmbeddedObject()
                for prop in ("Title", "SubTitle"):
                    try:
                        t = getattr(cd, prop)
                        if t is not None and "TARAPOTO" in t.String.upper():
                            t.String = t.String.replace("CO-TARAPOTO", "PONGO DE CAYNARACHI").replace("CO TARAPOTO", "PONGO DE CAYNARACHI").replace("CO:TARAPOTO", "PONGO DE CAYNARACHI")
                    except Exception:
                        pass                      # la plantilla tomaba Z22:Z45 (sin los dos ultimos datos)
        # ---------------------------------------------------------------- filas sobrantes (registro de 26 anios en la plantilla)
        sobran = 26 - n
        if sobran > 0:
            C.Rows.removeByIndex(22 + n - 1, sobran)        # filas N = n+1 .. 26 de la prueba K-S (fila 22 = N 1)
            B.Rows.removeByIndex(11 + n - 1, sobran)        # anios sobrantes de la serie (fila 11 = primer anio)
            A.Rows.removeByIndex(FILA0 + n - 1, sobran)     # anios sobrantes del registro
        for nombre in ("Hoja1", "210"):
            if sh.hasByName(nombre): sh.removeByName(nombre)
        doc.calculateAll()
        sel = C.getCellRangeByName("G%d" % (55 - sobran)).getString()
        res = {"seleccion": sel}
        for T, r in ((2, 10), (25, 14), (500, 18)):
            res["P24_T%d" % T] = D.getCellRangeByName("L%d" % r).getValue()
        res["K"] = sh.getByName("B. Int.maxima").getCellRangeByName("D12").getValue()
        res["m"] = sh.getByName("B. Int.maxima").getCellRangeByName("D13").getValue()
        res["n"] = sh.getByName("B. Int.maxima").getCellRangeByName("D14").getValue()
        res["D"] = {k: C.getCellRangeByName(ref).getValue() for k, ref in (("normal", "D%d" % (53 - sobran)), ("lognormal", "E%d" % (53 - sobran)),
                                                                           ("lp3", "G%d" % (53 - sobran)), ("gumbel", "I%d" % (53 - sobran)))}
        res["D_crit"] = C.getCellRangeByName("P%d" % (53 - sobran)).getValue()
        P = sh.getByName("C. P diseño")
        res["I_T25_10"] = P.getCellRangeByName("E116").getValue()
        os.makedirs(os.path.dirname(SAL), exist_ok=True)
        doc.storeToURL(uno.systemPathToFileUrl(os.path.abspath(SAL)), (_prop("FilterName", "Calc MS Excel 2007 XML"),))
        doc.close(True)
    finally:
        try: desk.terminate()
        except Exception: pass
        time.sleep(1); proc.kill()
    print(SAL); print(res)
    return res


def comprobar(res):
    """La hoja del usuario y hidrologia_b.py deben dar lo mismo (distribucion, P24, K-S, IDF e intensidad de diseno)."""
    R = H.resultados(); A = R["analisis"]
    nom = {"normal": "Normal", "lognormal": "Log - Normal", "lp3": "Log Pearson Tipo III", "gumbel": "Gumbel"}
    dif = []
    if res["seleccion"] != nom[A["elegida"]]: dif.append("distribucion: hoja %s / hidrologia_b %s" % (res["seleccion"], A["elegida"]))
    for k, v in res["D"].items():
        if abs(v - A["ks"][k]) > 5e-4: dif.append("D %s: hoja %.4f / hidrologia_b %.4f" % (k, v, A["ks"][k]))
    for a, b, t in ((res["P24_T25"], R["P24"], "P24 T25"), (res["K"], R["K"], "K"), (res["m"], R["m"], "m"), (res["n"], R["n"], "n"),
                    (res["I_T25_10"], R["I"], "I"), (res["D_crit"], A["ks_critico"], "D critico")):
        if abs(a - b) > 5e-3 * max(1, abs(b)) * (0.1 if t in ("m", "n") else 1): dif.append("%s: hoja %.4f / hidrologia_b %.4f" % (t, a, b))
    print("Comprobacion hoja de calculo vs hidrologia_b:", "IGUALES" if not dif else dif)
    return dif


if __name__ == "__main__":
    comprobar(construir())
