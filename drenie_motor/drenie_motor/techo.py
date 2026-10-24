"""Canaletas y montantes de techo (criterios de los CAR: conocimiento/07_componentes_complementarios.md y 02, seccion 8.4).

Por cada lado de techo (cada mitad a dos aguas, o cada parte que sigue una flecha de caida del usuario):
- Canaleta a lo largo del alero: plancha galvanizada, seccion b x h (0.25 x 0.20 por defecto), S = 1 %, Manning n = 0.013, borde
  libre 0.05 m. Caudal del lado Q = C I A FS (C = 0.88 del techo, A en proyeccion horizontal).
- Montantes PVC (Wyly-Eaton, llenado rs = 0.25): Q (l/s) = 1.754 rs^(5/3) D^(8/3); siempre 4" (CE.040, art. 12.5; el usuario no
  usa 6": en techos grandes se ponen mas montantes de 4" por lado, 3 o 4; 4 por lado sobre todo en losas deportivas). A lo mas
  4 por lado: si con 1/4 harian falta mas, se quedan 4 y se admite el llenado hasta 7/24; si aun no alcanza, se avisa.
  N.° de montantes del lado = el mayor de: area / area que atiende un montante de 4", y lo que pida la canaleta (cada montante
  recibe Q / n por la canaleta). Se reparten a lo largo del alero, en el centro de su parte.
- Cada montante baja por el muro y sale a la cuneta mas cercana (salida PVC horizontal); si no hay cuneta a menos de 3 m se avisa.
- Metrado (reglas de la planilla del usuario): canaleta = largo del alero; soportes = REDONDEAR.MAS(L / 0.60) + 1; 2 tapas
  laterales por canaleta; 1 boquilla por montante; montante = altura del alero + desvio bajo el alero + salida a la cuneta;
  3 codos de 90 por montante; 2 colgadores (desvio bajo el alero); abrazaderas = MAX(1, REDONDEAR.MENOS(L / 4)).
"""
import math

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, unary_union

DIAMETROS = [4, 6, 8]          # pulgadas (minimo 4" en techos)


def q_wyly(D, rs): return 1.754 * rs ** (5 / 3) * D ** (8 / 3)


def d_req(Q, rs): return (Q / (1.754 * rs ** (5 / 3))) ** (3 / 8) if Q > 0 else 0.0


def tirante(Q, S, n, b):
    lo, hi = 1e-5, 2.0
    for _ in range(80):
        y = (lo + hi) / 2; A = b * y; R = A / (b + 2 * y)
        if A * R ** (2 / 3) * math.sqrt(S) / n > Q: hi = y
        else: lo = y
    return (lo + hi) / 2


def _alero(ag):
    """Linea del alero de un lado de techo: la del dato (dos aguas / una agua) o, con flecha, los bordes del techo hacia los que
    apunta la flecha (normal exterior parecida a la flecha)."""
    if ag.get("alero") is not None: return ag["alero"]
    ux, uy = ag["flecha"]; pol = ag["poligono"]; borde_techo = ag["techo_poligono"].exterior
    ext = pol.exterior if hasattr(pol, "exterior") else max(pol.geoms, key=lambda g: g.area).exterior
    if not ext.is_ccw: ext = LineString(list(ext.coords)[::-1])
    cs = list(ext.coords); trozos = []
    for a, b in zip(cs[:-1], cs[1:]):
        L = math.dist(a, b)
        if L < 0.05: continue
        nx, ny = (b[1] - a[1]) / L, -(b[0] - a[0]) / L                 # normal exterior de un anillo antihorario
        m = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if nx * ux + ny * uy > 0.7 and borde_techo.distance(m) < 0.05: trozos.append(LineString([a, b]))
    if not trozos: return None
    lm = linemerge(unary_union(trozos))
    return max(lm.geoms, key=lambda g: g.length) if hasattr(lm, "geoms") else lm


def _altura(techo_pol, cfg_alt):
    """Altura del alero sobre el piso: {"defecto": 3.50, "techos": [{"punto": [x, y], "altura": 7.00}]} (punto dentro del techo)."""
    for d in cfg_alt.get("techos", []):
        if techo_pol.buffer(0.05).contains(Point(d["punto"])): return float(d["altura"])
    return float(cfg_alt.get("defecto", 3.50))


PARAM = {"canaleta_b": 0.25, "canaleta_h": 0.20, "BL": 0.05, "S": 0.01, "n": 0.013, "rs": 0.25, "rs_max": 7 / 24, "max_por_lado": 4,
         "desvio": 0.50, "entrada_cuneta": 0.30, "sep_soporte": 0.60, "abrazadera_cada": 4.0, "colgadores": 2, "codos90": 3,
         "salida_max": 3.0, "d_montante": 4, "fc_largo": 0.20, "fc_ancho": 0.15, "esquina_max": 3.0, "alero_vuelo": 0.60}


def _normal_alero(ag, al):
    """Direccion hacia donde cae el agua, perpendicular al alero (del techo hacia el alero)."""
    (x0, y0), (x1, y1) = al.coords[0], al.coords[-1]; L = math.dist((x0, y0), (x1, y1)) or 1.0
    ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    c = ag["poligono"].representative_point(); m = al.interpolate(0.5, normalized=True)
    if (m.x - c.x) * nx + (m.y - c.y) * ny < 0: nx, ny = -nx, -ny
    return (ux, uy), (nx, ny)


def _esquina(E, hacia, nrm, muros, tc):
    """Montante pegado a la esquina de la edificacion junto al extremo E del alero: vertice del muro mas cercano (a menos de 3 m);
    el tubo va en la cara que da al alero, al lado de la esquina, dentro de su falsa columna. Sin muros: bajo el alero, a
    'alero_vuelo' hacia adentro."""
    V = None
    if muros is not None and not muros.is_empty:
        cand = []
        for p in (muros.geoms if hasattr(muros, "geoms") else [muros]):
            if p.distance(Point(E)) > tc["esquina_max"]: continue
            for v in list(p.exterior.coords)[:-1]:
                d = math.dist(v, E)
                if d <= tc["esquina_max"]: cand.append((d, v))
        if cand: V = min(cand)[1]
    if V is None: V = (E[0] - nrm[0] * tc["alero_vuelo"] + hacia[0] * 0.30, E[1] - nrm[1] * tc["alero_vuelo"] + hacia[1] * 0.30)
    c = (V[0] + nrm[0] * tc["fc_ancho"] / 2 + hacia[0] * tc["fc_largo"] / 2, V[1] + nrm[1] * tc["fc_ancho"] / 2 + hacia[1] * tc["fc_largo"] / 2)
    return c, V


def ubicar(sitio, P, I, cfg):
    """Lados de techo con su canaleta y la ubicacion de sus montantes (sin la red de cunetas). Por defecto: uno en cada esquina
    de la edificacion junto a los extremos del alero (2 por lado: 4 por edificacion a dos aguas); si el area pide mas, se agregan
    intermedios repartidos. Si el proyecto trae montantes del visor ("montantes": [{"x", "y"}]), se usan esos (movidos, agregados
    o quitados por el proyectista): cada uno va al lado de techo con el alero mas cercano (a menos de 3 m)."""
    tc = dict(PARAM, C=P["C"]["techo"]); tc.update(cfg.get("techo_parametros", {}))
    q_m2 = tc["C"] * I / 3.6e6 * P["FS"] * 1000.0
    Q4 = q_wyly(4, tc["rs"]); A4 = Q4 / q_m2
    hu = tc["canaleta_h"] - tc["BL"]
    Qcan = tc["canaleta_b"] * hu * (tc["canaleta_b"] * hu / (tc["canaleta_b"] + 2 * hu)) ** (2 / 3) * math.sqrt(tc["S"]) / tc["n"] * 1000.0
    muros = getattr(sitio, "muros", None)
    lados, avisos, nt = [], [], {}
    for ag in getattr(sitio, "aguas", []):
        al = _alero(ag)
        if al is None or al.length < 0.5:
            avisos.append("Un lado del techo %d no tiene borde hacia donde cae el agua; revisar la flecha." % (ag["techo"] + 1)); continue
        u, nrm = _normal_alero(ag, al)
        A = ag["poligono"].area; Q = q_m2 * A; L = al.length
        n = max(1 if L < 3.0 else 2, math.ceil(A / A4 - 1e-9), math.ceil(Q / Qcan - 1e-9))
        if n > tc["max_por_lado"]:
            # usuario: a lo mas 4 montantes de 4" por lado; con 4 se admite el llenado de Wyly-Eaton hasta 7/24
            n = max(tc["max_por_lado"], math.ceil(Q / q_wyly(4, tc["rs_max"]) - 1e-9), math.ceil(Q / Qcan - 1e-9))
        E0, E1 = al.coords[0], al.coords[-1]
        c0, V0 = _esquina(E0, u, nrm, muros, tc)
        pos = [(c0, V0, u)]
        if n >= 2:
            c1, V1 = _esquina(E1, (-u[0], -u[1]), nrm, muros, tc)
            for k in range(1, n - 1):
                t = k / (n - 1); c = (c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t)
                pos.append((c, (c[0] - nrm[0] * tc["fc_ancho"] / 2 - u[0] * tc["fc_largo"] / 2, c[1] - nrm[1] * tc["fc_ancho"] / 2 - u[1] * tc["fc_largo"] / 2), u))
            pos.append((c1, V1, (-u[0], -u[1])))
        nt[ag["techo"]] = nt.get(ag["techo"], 0) + 1
        lados.append({"ag": ag, "alero": al, "u": u, "nrm": nrm, "A": A, "Q": Q, "L": L, "techo": "T-%02d" % (ag["techo"] + 1),
                      "lado": "Lado %02d" % nt[ag["techo"]], "pos": pos})
    manual = cfg.get("montantes")
    if manual:
        for l in lados: l["pos"] = []
        for m in manual:
            p = Point(m["x"], m["y"])
            cerca = [l for l in lados if l["alero"].distance(p) <= tc["esquina_max"] + 1.0]
            if not cerca:
                avisos.append("El montante del visor en (%.2f, %.2f) no esta junto a ningun alero: no se tomo." % (m["x"], m["y"])); continue
            l = min(cerca, key=lambda l: l["alero"].distance(p))
            V = (m["x"] - l["nrm"][0] * tc["fc_ancho"] / 2 - l["u"][0] * tc["fc_largo"] / 2, m["y"] - l["nrm"][1] * tc["fc_ancho"] / 2 - l["u"][1] * tc["fc_largo"] / 2)
            l["pos"].append(((m["x"], m["y"]), V, l["u"]))
        for l in lados:
            if not l["pos"]: avisos.append("%s %s no tiene montante (se quitaron en el visor): su agua (%.2f l/s) no tiene bajada." % (l["techo"], l["lado"], l["Q"]))
    return lados, avisos, {"q_m2": q_m2, "Q4": Q4, "A4": A4, "Qcan": Qcan, "hu": hu, "tc": tc}


def calcular(sitio, R, P, I, cfg):
    """R: red con cotas. Devuelve dict con lados, montantes, metrado y avisos."""
    lados0, avisos, K = ubicar(sitio, P, I, cfg)
    tc, hu = K["tc"], K["hu"]
    alturas = cfg.get("altura_alero", {"defecto": 3.50})
    Nn = R["nudos"]
    segs = [(r["codigo"], LineString([Nn[t["de"]], Nn[t["a"]]])) for r in R["ramales"] for t in r["tramos"] if t["origen"] != "pase"]
    red = unary_union([s for _, s in segs])
    techo_pol = {}
    for l in lados0: techo_pol[l["techo"]] = unary_union([techo_pol.get(l["techo"], l["ag"]["poligono"]), l["ag"]["poligono"]])
    lados, montantes = [], []
    for l in lados0:
        n = len(l["pos"]); A, Q, L = l["A"], l["Q"], l["L"]
        # siempre montantes de 4" (usuario 24-10-2026: no usar 6"; si el lado es grande se ponen mas montantes de 4" por lado)
        Qm = Q / n if n else 0.0; Dad = tc["d_montante"]
        rs = tc["rs"] if Qm <= q_wyly(Dad, tc["rs"]) + 1e-9 else tc["rs_max"]          # llenado 1/4; hasta 7/24 con 4 por lado
        D = d_req(Qm, rs)
        if n and D > Dad + 1e-6:
            falta = math.ceil(Q / q_wyly(Dad, tc["rs_max"]) - 1e-9)
            avisos.append("%s %s: con %d montantes de %d\" cada uno lleva %.2f l/s (pide %.2f\"); poner %d montantes de %d\" en ese lado." % (
                l["techo"], l["lado"], n, Dad, Qm, D, falta, Dad))
        y = tirante(Qm / 1000.0, tc["S"], tc["n"], tc["canaleta_b"]) if n else 0.0
        h = _altura(techo_pol[l["techo"]], alturas)
        ms = []
        for (c, V, hacia) in l["pos"]:
            p = Point(c)
            d = red.distance(p) if not red.is_empty else float("inf")
            seg = min(segs, key=lambda s: s[1].distance(p)) if segs else None
            q = seg[1].interpolate(seg[1].project(p)) if seg else None
            Lm = h + tc["desvio"] + (d if d <= tc["salida_max"] else 0.0) + tc["entrada_cuneta"]
            m = {"montante": "M-%02d" % (len(montantes) + 1), "techo": l["techo"], "lado": l["lado"], "x": round(c[0], 3), "y": round(c[1], 3),
                 "esquina": [round(V[0], 3), round(V[1], 3)], "a_lo_largo": [round(hacia[0], 4), round(hacia[1], 4)],
                 "hacia_alero": [round(l["nrm"][0], 4), round(l["nrm"][1], 4)],
                 "cuneta": seg[0] if seg and d <= tc["salida_max"] else "SIN CUNETA CERCANA", "salida_m": round(d, 2),
                 "hacia": [round(q.x, 3), round(q.y, 3)] if q is not None and d <= tc["salida_max"] else None,
                 "altura_alero": h, "L_m": round(Lm, 2), "Q_ls": round(Qm, 2), "D_req_pulg": round(D, 2), "D_pulg": Dad, "llenado": round(rs, 3),
                 "codos90": tc["codos90"], "colgadores": tc["colgadores"], "abrazaderas": max(1, math.floor(Lm / tc["abrazadera_cada"]))}
            if d > tc["salida_max"]:
                avisos.append("%s (%s %s) no tiene cuneta a menos de %.1f m (la mas cercana a %.1f m): revisar si falta cuneta o "
                              "si descarga a otro lugar." % (m["montante"], l["techo"], l["lado"], tc["salida_max"], d))
            montantes.append(m); ms.append(m["montante"])
        lados.append({"techo": l["techo"], "lado": l["lado"], "A_m2": round(A, 2), "L_canaleta_m": round(L, 2), "Q_ls": round(Q, 2),
                      "montantes": n, "Q_por_montante_ls": round(Qm, 2), "tirante_m": round(y, 3), "borde_libre_m": round(tc["canaleta_h"] - y, 3),
                      "canaleta": "CUMPLE" if y <= hu + 1e-6 else "NO CUMPLE", "soportes": math.ceil(L / tc["sep_soporte"] - 1e-9) + 1,
                      "tapas": 2, "boquillas": n, "ids": ms, "alero": [list(c) for c in l["alero"].coords], "caida": l["ag"]["tipo"]})
    met = {"canaleta_m": round(sum(l["L_canaleta_m"] for l in lados), 2), "soportes_und": sum(l["soportes"] for l in lados),
           "tapas_und": sum(l["tapas"] for l in lados), "boquillas_und": sum(l["boquillas"] for l in lados),
           "montante_m": round(sum(m["L_m"] for m in montantes), 2), "montantes_und": len(montantes), "falsas_columnas_und": len(montantes),
           "codo90_und": sum(m["codos90"] for m in montantes), "colgador_und": sum(m["colgadores"] for m in montantes),
           "abrazadera_und": sum(m["abrazaderas"] for m in montantes)}
    criterios = {"q_l_s_m2": round(K["q_m2"], 5), "Q_montante_4_ls": round(K["Q4"], 2), "A_por_montante_4_m2": round(K["A4"], 1),
                 "Q_canaleta_ls": round(K["Qcan"], 2), "parametros": tc, "altura_alero": alturas,
                 "ubicacion": "visor (proyectista)" if cfg.get("montantes") else "esquinas de la edificacion (2 por lado; mas si el area lo pide)"}
    if not alturas.get("techos"):
        avisos.append("Altura de alero de %.2f m para todos los techos (valor por defecto): poner la altura de cada edificacion "
                      "(altura_alero) para la longitud real de los montantes." % float(alturas.get("defecto", 3.5)))
    return {"lados": lados, "montantes": montantes, "metrado": met, "criterios": criterios, "avisos": avisos}


def excel(T, ruta, SM=None):
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    wb = openpyxl.Workbook(); neg = Font(bold=True); cab = PatternFill("solid", fgColor="D9E2F3")
    fino = Side(style="thin", color="999999"); borde = Border(left=fino, right=fino, top=fino, bottom=fino)

    def tabla(ws, f0, enc, filas, fmt):
        for j, h in enumerate(enc):
            c = ws.cell(f0, 1 + j, h); c.font = neg; c.fill = cab; c.border = borde; c.alignment = Alignment(horizontal="center", wrap_text=True)
            ws.column_dimensions[openpyxl.utils.get_column_letter(1 + j)].width = 13
        ws.row_dimensions[f0].height = 34
        for i, fl in enumerate(filas):
            for j, v in enumerate(fl):
                c = ws.cell(f0 + 1 + i, 1 + j, v); c.border = borde
                if fmt[j]: c.number_format = fmt[j]
        return f0 + len(filas) + 1
    ws = wb.active; ws.title = "CANALETAS"
    tc = T["criterios"]["parametros"]
    ws["A1"] = "CANALETAS DE PLANCHA GALVANIZADA %.2f x %.2f (S = %.0f %%) POR TECHO Y LADO" % (tc["canaleta_b"], tc["canaleta_h"], 100 * tc["S"]); ws["A1"].font = Font(bold=True, size=12)
    f = tabla(ws, 3, ["TECHO", "LADO", "N. CANALETAS", "LONGITUD (m)", "TOTAL (m)", "SOPORTES", "TAPAS", "BOQUILLAS", "AREA (m2)", "Q (l/s)",
                      "TIRANTE (m)", "BORDE LIBRE (m)", "CAPACIDAD"],
              [[l["techo"], l["lado"], 1, l["L_canaleta_m"], l["L_canaleta_m"], l["soportes"], l["tapas"], l["boquillas"], l["A_m2"], l["Q_ls"],
                l["tirante_m"], l["borde_libre_m"], l["canaleta"]] for l in T["lados"]],
              [None, None, "0", "0.00", "0.00", "0", "0", "0", "0.00", "0.00", "0.000", "0.000", None])
    m = T["metrado"]
    for j, v in ((4, m["canaleta_m"]), (5, m["soportes_und"]), (6, m["tapas_und"]), (7, m["boquillas_und"])):
        ws.cell(f, 1, "TOTAL").font = neg; c = ws.cell(f, 1 + j, v); c.font = neg; c.border = borde
    w = wb.create_sheet("MONTANTES")
    w["A1"] = "MONTANTES PVC (Wyly-Eaton, rs = %.2f; hasta 7/24 con 4 por lado) Y ACCESORIOS" % tc["rs"]; w["A1"].font = Font(bold=True, size=12)
    f = tabla(w, 3, ["MONTANTE", "TECHO", "LADO", "Q (l/s)", "D REQ. (pulg)", "D (pulg)", "ALTURA ALERO (m)", "SALIDA (m)", "LONGITUD (m)",
                     "CODO 90", "COLGADOR", "ABRAZADERA", "DESCARGA A"],
              [[x["montante"], x["techo"], x["lado"], x["Q_ls"], x["D_req_pulg"], x["D_pulg"], x["altura_alero"], x["salida_m"], x["L_m"],
                x["codos90"], x["colgadores"], x["abrazaderas"], x["cuneta"]] for x in T["montantes"]],
              [None, None, None, "0.00", "0.00", "0", "0.00", "0.00", "0.00", "0", "0", "0", None])
    for j, v in ((8, m["montante_m"]), (9, m["codo90_und"]), (10, m["colgador_und"]), (11, m["abrazadera_und"])):
        w.cell(f, 1, "TOTAL").font = neg; c = w.cell(f, 1 + j, v); c.font = neg; c.border = borde
    k = wb.create_sheet("CRITERIOS")
    cr = T["criterios"]
    filas = [("Caudal por m2 de techo (l/s/m2)", cr["q_l_s_m2"]), ("Capacidad de un montante de 4\" (l/s)", cr["Q_montante_4_ls"]),
             ("Area que atiende un montante de 4\" (m2)", cr["A_por_montante_4_m2"]), ("Capacidad de la canaleta con borde libre (l/s)", cr["Q_canaleta_ls"]),
             ("Seccion de canaleta (m)", "%.2f x %.2f" % (tc["canaleta_b"], tc["canaleta_h"])), ("Pendiente de canaleta", "%.1f %%" % (100 * tc["S"])),
             ("Manning n", tc["n"]), ("Soportes de platina F°G° 1\" x 1/8\"", "@ %.2f m (REDONDEAR.MAS(L/%.2f) + 1)" % (tc["sep_soporte"], tc["sep_soporte"])),
             ("Montante", "altura de alero + desvio %.2f + salida a la cuneta + %.2f" % (tc["desvio"], tc["entrada_cuneta"])),
             ("Accesorios por montante", "%d codos de 90, %d colgadores, abrazaderas MAX(1, REDONDEAR.MENOS(L/%.0f))" % (tc["codos90"], tc["colgadores"], tc["abrazadera_cada"]))]
    for i, (a, b) in enumerate(filas):
        k.cell(2 + i, 1, a).border = borde; k.cell(2 + i, 2, b).border = borde
    k.column_dimensions["A"].width = 52; k.column_dimensions["B"].width = 60
    if SM is not None:
        from . import sumideros as _s
        _s.hoja(wb, SM)
    wb.properties.creator = ""; wb.properties.lastModifiedBy = ""
    wb.save(ruta); return ruta
