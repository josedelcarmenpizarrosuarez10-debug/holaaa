"""Lectura de datos diarios de precipitacion para la I.E. N.° 0590 Barranquita (C.I. 468901) y comparacion con la serie vigente.

Uso:
    python3 herramientas/barranquita/lluvia_datos_b.py [carpeta]
    (por defecto: insumos/barranquita/lluvia/)

Cada archivo de la carpeta (.csv, .txt, .xlsx) es una estacion o un punto. El nombre del archivo debe incluir el codigo o el nombre:
    000386 / navarro, 153322 / pelejo, 153315 / shanusi, 003317 / caynarachi, tarapoto,
    power_barranquita, power_tarapoto, chirps_barranquita, chirps_tarapoto.
Formatos aceptados (se detectan solos):
    - SENAMHI, descarga por estacion: "AÑO / MES / DÍA", ..., "PRECIPITACIÓN (mm/día) TOTAL" (o columnas Año, Mes, Dia, Precip.)
    - SENAMHI, archivo historico sin encabezado: anio mes dia precipitacion tmax tmin (-99.9 = sin dato)
    - NASA POWER (CSV diario): YEAR, MO, DY, PRECTOTCORR   (o YEAR, DOY, PRECTOTCORR)
    - CHIRPS / series por punto: fecha (AAAA-MM-DD) y precipitacion
"T" (traza) = 0.0; "S/D", vacio, -99.9 o negativos = sin dato.

No modifica hidrologia_b.py: imprime el resumen y lo guarda en entregables_barranquita/_calc/lluvia_comparacion.json.
"""
import csv, datetime as dt, json, math, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import hidrologia_b as H

CLAVES = [("000386", "Navarro", "llanura"), ("navarro", "Navarro", "llanura"),
          ("153322", "Pelejo", "llanura"), ("pelejo", "Pelejo", "llanura"),
          ("153315", "Shanusi", "llanura"), ("shanusi", "Shanusi", "llanura"),
          ("003317", "Pongo de Caynarachi", "cerro"), ("caynarachi", "Pongo de Caynarachi", "cerro"),
          ("power_barranquita", "NASA POWER Barranquita", "malla"), ("power_tarapoto", "NASA POWER Tarapoto", "malla"),
          ("chirps_barranquita", "CHIRPS Barranquita", "malla"), ("chirps_tarapoto", "CHIRPS Tarapoto", "malla"),
          ("tarapoto", "Tarapoto", "tarapoto")]
MIN_DIAS_MES = 25          # mes valido para totales
MIN_MESES_ANIO = 12        # anio valido para total anual
MIN_DIAS_ANIO_MAX = 300    # anio valido para la maxima en 24 h
MIN_ANIOS_SERIE = 25


def _num(v):
    v = (v or "").strip().replace(",", ".")
    if v.upper() in ("T", "TR", "TRAZA"): return 0.0
    try: x = float(v)
    except ValueError: return None
    return None if x < 0 or x > 900 else x


def _filas(ruta):
    if ruta.lower().endswith((".xlsx", ".xls")):
        import openpyxl
        ws = openpyxl.load_workbook(ruta, data_only=True, read_only=True).active
        return [["" if c is None else (c.strftime("%Y-%m-%d") if hasattr(c, "strftime") else str(c)) for c in r]
                for r in ws.iter_rows(values_only=True)]
    txt = open(ruta, encoding="utf-8", errors="replace").read()
    if "-END HEADER-" in txt: txt = txt.split("-END HEADER-", 1)[1]          # cabecera de NASA POWER
    lineas = [l for l in txt.splitlines() if l.strip()]
    muestra = "\n".join(lineas[:20])
    if muestra.count(",") >= muestra.count(";") and "," in muestra: sep = ","
    elif ";" in muestra: sep = ";"
    elif "\t" in muestra: sep = "\t"
    else: return [l.split() for l in lineas]
    return list(csv.reader(lineas, delimiter=sep))


def _norm(s):
    s = s.upper()
    for a, b in (("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"), ("Ñ", "N")): s = s.replace(a, b)
    return re.sub(r"[^A-Z0-9/]", "", s)


def leer(ruta):
    """Devuelve {fecha: mm} de un archivo diario."""
    filas = _filas(ruta); datos = {}
    i0, col = 0, None
    for i, f in enumerate(filas[:40]):                      # buscar encabezado
        h = [_norm(c) for c in f]
        if any(x in ("ANO", "YEAR", "FECHA", "DATE", "ANO/MES/DIA") or x.startswith("ANO") for x in h):
            col = h; i0 = i + 1; break
    def ip(nombres):
        for j, c in enumerate(col or []):
            if any(c.startswith(n) for n in nombres): return j
        return None
    if col:
        jp = ip(["PRECTOT", "PRECIP", "PP", "PREC", "LLUVIA", "RAIN", "CHIRPS"])
        jf = ip(["FECHA", "DATE", "ANO/MES/DIA"]); ja = ip(["ANO", "YEAR"]); jm = ip(["MES", "MO"]); jd = ip(["DIA", "DY"])
        jdoy = ip(["DOY"])
        if jp is None: jp = len(col) - 1
    else:
        jf, ja, jm, jd, jdoy, jp = None, 0, 1, 2, None, 3
    for f in filas[i0:]:
        try:
            if jf is not None and (ja is None or jf == ja):
                t = f[jf].strip().replace("/", "-")
                p = [int(x) for x in re.split(r"[-\s]", t)[:3]]
                d = dt.date(p[0], p[1], p[2]) if p[0] > 31 else dt.date(p[2], p[1], p[0])
            elif jdoy is not None and jm is None:
                d = dt.date(int(float(f[ja])), 1, 1) + dt.timedelta(days=int(float(f[jdoy])) - 1)
            else:
                d = dt.date(int(float(f[ja])), int(float(f[jm])), int(float(f[jd])))
        except (ValueError, IndexError):
            continue
        v = _num(f[jp]) if jp < len(f) else None
        if v is not None: datos[d] = v
    return datos


def resumen(datos):
    meses = {}
    for d, v in datos.items(): meses.setdefault((d.year, d.month), []).append(v)
    anios = sorted({a for a, _ in meses})
    tot, maxm, maxa = {}, {}, {}
    for a in anios:
        ms = [meses.get((a, m)) for m in range(1, 13)]
        maxm[a] = [round(max(x), 1) if x and len(x) >= 20 else None for x in ms]
        if sum(len(x) for x in ms if x) >= MIN_DIAS_ANIO_MAX: maxa[a] = max(max(x) for x in ms if x)
        if sum(1 for x in ms if x and len(x) >= MIN_DIAS_MES) >= MIN_MESES_ANIO: tot[a] = sum(sum(x) for x in ms if x)
    return {"desde": min(datos).isoformat() if datos else None, "hasta": max(datos).isoformat() if datos else None,
            "dias": len(datos), "totales": tot, "max_mensual": maxm, "max_anual": maxa,
            "p_anual": sum(tot.values()) / len(tot) if tot else None}


def frecuencias(serie_mensual, factor=1.0):
    """Analisis de hidrologia_b con otra serie (mismas distribuciones, K-S, Dick-Peschke, tc)."""
    viejo = H.SERIE
    try:
        H.SERIE = {a: m for a, m in serie_mensual.items() if any(v is not None for v in m)}
        A = H.analisis(factor=factor)
    finally:
        H.SERIE = viejo
    d = A["elegida"]; p24 = A["tabla"][H.T_DISENO][d]
    return {"n": A["n"], "elegida": d, "ks": A["ks"][d], "ks_critico": A["ks_critico"], "P24_T25": p24,
            "I_tc10": H.p_dur(p24, H.TC) * 60.0 / H.TC, "media": A["media"]}


def main(carpeta):
    est = {}
    for f in sorted(os.listdir(carpeta)):
        if not f.lower().endswith((".csv", ".txt", ".xlsx", ".xls")): continue
        b = f.lower()
        k = next(((n, t) for c, n, t in CLAVES if c in b), None)
        if not k: print("  (sin estacion reconocida, se omite)", f); continue
        r = resumen(leer(os.path.join(carpeta, f))); r["archivo"] = f; r["tipo"] = k[1]
        est[k[0]] = r
        pa = f"{r['p_anual']:,.1f}" if r["p_anual"] else "-"
        print(f"{k[0]:<24} {r['desde']} a {r['hasta']}  anios completos {len(r['totales']):>2}  P anual {pa} mm"
              f"  anios con Pmax24 {len(r['max_anual'])}")
    sal = {"estaciones": est, "vigente": {"P_anual_llanura": H.P_ANUAL_BARRANQUITA, "P_anual_tarapoto": H.P_ANUAL_TARAPOTO,
                                          "factor": H.FACTOR}}
    ll = [n for n in ("Navarro", "Pelejo", "Shanusi") if n in est and est[n]["p_anual"]]
    if ll:
        pa = sum(est[n]["p_anual"] for n in ll) / len(ll)
        sal["P_anual_llanura_nueva"] = pa; sal["estaciones_promedio"] = ll
        print(f"\nP anual llanura ({', '.join(ll)}): {pa:,.2f} mm (vigente {H.P_ANUAL_BARRANQUITA:,.2f})")
    pt = est.get("Tarapoto", {}).get("p_anual") or H.P_ANUAL_TARAPOTO
    fac = (sal.get("P_anual_llanura_nueva") or H.P_ANUAL_BARRANQUITA) / pt
    tr = frecuencias(H.SERIE, fac); sal["tarapoto_transpuesta"] = dict(tr, factor=fac)
    print(f"Tarapoto transpuesta x {fac:.4f}: n {tr['n']}, {tr['elegida']}, P24 T25 {tr['P24_T25']:.2f} mm, I {tr['I_tc10']:.2f} mm/h")
    for n in ("Navarro", "Pelejo", "Shanusi", "Pongo de Caynarachi"):
        if n in est and len(est[n]["max_anual"]) >= 10:
            fr = frecuencias({a: est[n]["max_mensual"][a] for a in est[n]["max_anual"]}); sal["serie_" + n] = fr
            ok = "suficiente" if fr["n"] >= MIN_ANIOS_SERIE else f"corta (< {MIN_ANIOS_SERIE} anios)"
            print(f"Serie propia {n}: n {fr['n']} ({ok}), {fr['elegida']} (K-S {fr['ks']:.3f} / {fr['ks_critico']:.2f}), "
                  f"P24 T25 {fr['P24_T25']:.2f} mm, I {fr['I_tc10']:.2f} mm/h")
    pb = [est[k]["p_anual"] for k in ("NASA POWER Barranquita", "CHIRPS Barranquita") if k in est and est[k]["p_anual"]]
    for fuente in ("NASA POWER", "CHIRPS"):
        a, b = est.get(fuente + " Barranquita"), est.get(fuente + " Tarapoto")
        if a and b and a["p_anual"] and b["p_anual"]:
            comunes = sorted(set(a["totales"]) & set(b["totales"]))
            if comunes:
                ra = sum(a["totales"][y] for y in comunes) / sum(b["totales"][y] for y in comunes)
                sal["relacion_" + fuente] = {"anios": [comunes[0], comunes[-1], len(comunes)], "relacion": ra}
                print(f"{fuente}: relacion anual Barranquita / Tarapoto {comunes[0]}-{comunes[-1]} ({len(comunes)} anios) = {ra:.3f}"
                      f" (vigente {H.FACTOR:.3f})")
    os.makedirs(os.path.join(RAIZ, "entregables_barranquita", "_calc"), exist_ok=True)
    with open(os.path.join(RAIZ, "entregables_barranquita", "_calc", "lluvia_comparacion.json"), "w", encoding="utf-8") as fh:
        json.dump(sal, fh, ensure_ascii=False, indent=1, default=str)
    return sal


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "insumos", "barranquita", "lluvia"))
