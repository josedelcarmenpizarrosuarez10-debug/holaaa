"""Canaletas y montantes de techo (criterios de los CAR: conocimiento/07_componentes_complementarios.md y 02, seccion 8.4).

Por cada lado de techo (cada mitad a dos aguas, o cada parte que sigue una flecha de caida del usuario):
- Canaleta a lo largo del alero: plancha galvanizada, seccion b x h (0.25 x 0.20 por defecto), S = 1 %, Manning n = 0.013, borde
  libre 0.05 m. Caudal del lado Q = C I A FS (C = 0.88 del techo, A en proyeccion horizontal).
- Montantes PVC (Wyly-Eaton, llenado rs = 0.25): Q (l/s) = 1.754 rs^(5/3) D^(8/3); siempre 4" (CE.040, art. 12.5; el usuario no
  usa 6": en techos grandes se ponen mas montantes de 4" por lado, 3 o 4; 4 por lado sobre todo en losas deportivas). A lo mas
  4 por lado: si con 1/4 harian falta mas, se quedan 4 y se admite el llenado hasta 7/24; si aun no alcanza, se avisa.
  N.° de montantes del lado = el mayor de: area / area que atiende un montante de 4", y lo que pida la canaleta (cada montante
  recibe Q / n por la canaleta). Se reparten a lo largo del alero, en el centro de su parte.
- Cada montante va en una esquina, dentro de una falsa columna de 0.20 x 0.15 x 1.30 sobre un dado; en el dado un codo de 90
  de 4" y de ahi la tuberia PVC 4" enterrada hasta la cuneta (hasta 5 m), al 1 % (minimo 0.5 %), llegando sobre el nivel del agua
  de la cuneta + 5 cm. La cuneta puede ir a lo largo del alero o transversal: basta que el tubo de cada montante llegue.
- Metrado de DrenIE: canaleta = largo del alero; soportes = REDONDEAR.MAS(L / 0.60) + 1; 2 tapas laterales por canaleta;
  1 boquilla por montante; falsa columna y dado por montante; codo del dado y tuberia enterrada. La altura del montante, el tubo
  que sube a la canaleta, los codos del desvio, colgadores y abrazaderas los mete el proyectista (cortes de arquitectura).
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
         "tubo_max": 5.0, "S_tubo": 0.01, "S_tubo_min": 0.005, "prof_tubo": 0.20, "prof_tubo_min": 0.15, "d_montante": 4, "fc_largo": 0.20, "fc_ancho": 0.15, "esquina_max": 3.0, "alero_vuelo": 0.60}


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


def _adentro(sitio, p, d=0.30):
    """Punto del lado de adentro del cerco mas cercano a p (a d del cerco)."""
    b = sitio.cerco.buffer(-d).exterior
    return b.interpolate(b.project(p))


def calcular(sitio, R, P, I, cfg, descargas=(), V=None):
    """R: red con cotas; V: verificacion (tirantes y anchos de cada tramo). Devuelve dict con lados, montantes, metrado y avisos.
    DrenIE ubica los montantes (esquinas) y mide su salida: en el dado un codo de 90 de 4" y de ahi la tuberia PVC 4" enterrada hasta
    la cara interior de la cuneta (hasta tubo_max, 5 m; usuario 25-10-2026), al 1 % (minimo 0.5 %), llegando sobre el nivel del agua
    de la cuneta + 5 cm (llegada.py). La altura del montante, el tubo que sube a la canaleta, abrazaderas y colgadores los mete el
    proyectista con los cortes de arquitectura. No hace falta que la cuneta vaya a lo largo del alero: basta que cada montante llegue."""
    from .sumideros import _cf_en
    from . import llegada
    lados0, avisos, K = ubicar(sitio, P, I, cfg)
    tc, hu = K["tc"], K["hu"]
    tir = llegada.tirantes(V, P, R) if V else {}
    anc = llegada.anchos(V) if V else {}
    Nn = R["nudos"]
    segs_e = [(r["codigo"], LineString([Nn[t["de"]], Nn[t["a"]]]), "%s|%s|%s" % (r["codigo"], t["de"], t["a"])) for r in R["ramales"]
              for t in r["tramos"] if t["origen"] != "pase" and math.dist(Nn[t["de"]], Nn[t["a"]]) > 1.0]
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
        ms = []
        for (c, Vx, hacia) in l["pos"]:
            p = Point(c)
            m = {"montante": "M-%02d" % (len(montantes) + 1), "techo": l["techo"], "lado": l["lado"], "x": round(c[0], 3), "y": round(c[1], 3),
                 "esquina": [round(Vx[0], 3), round(Vx[1], 3)], "a_lo_largo": [round(hacia[0], 4), round(hacia[1], 4)],
                 "hacia_alero": [round(l["nrm"][0], 4), round(l["nrm"][1], 4)], "Q_ls": round(Qm, 2), "D_req_pulg": round(D, 2), "D_pulg": Dad,
                 "llenado": round(rs, 3), "codo_dado": 1, "cuneta": "SIN CUNETA A MENOS DE %.0f m" % tc["tubo_max"], "hacia": None,
                 "salida_m": None, "llega": None, "tramo": None}
            # la tuberia va dentro del cerco: si la esquina del techo cae fuera, se toma el piso del lado de adentro
            pin = p if sitio.dentro(p.x, p.y) else _adentro(sitio, p)
            z_piso = sitio.rasante(pin.x, pin.y)

            def opcion(e):
                # el tubo va embebido bajo el piso: sale del codo del dado con su fondo a prof_tubo (0.20) bajo el piso; si asi no llega sobre
                # el agua, se sube hasta prof_tubo_min (0.15, la clave queda bajo el angulo de la rejilla); recien despues se profundiza la cuneta
                q_ = e[1].interpolate(e[1].project(p))
                L_ = max(p.distance(q_) - anc.get(e[2], P.get("b_int", 0.30)) / 2.0, 0.10)       # hasta la cara interior de la cuneta
                cf_ = _cf_en(R, e[0], (q_.x, q_.y))[1]; y_ = tir[e[2]]((q_.x, q_.y)) if e[2] in tir else 0.10
                for pr in (tc["prof_tubo"], tc["prof_tubo_min"]):
                    z0 = z_piso - pr
                    S_, zl_, nv_, ok_ = llegada.resolver(z0, L_, cf_, y_, (tc["S_tubo"], tc["S_tubo_min"]))
                    if ok_: break
                hr_ = llegada.h_req(sitio.rasante(q_.x, q_.y), z_piso - tc["prof_tubo_min"], L_, y_, tc["S_tubo_min"])
                return (not ok_, L_), e, q_, L_, cf_, y_, S_, zl_, nv_, ok_, hr_, z0
            ops = sorted((opcion(e) for e in segs_e if e[1].distance(p) - anc.get(e[2], 0.30) / 2.0 <= tc["tubo_max"]), key=lambda o: o[0])
            if ops:
                _, (eje, ln, clave), qe, Le, cf, yv, St, z_ll, nivel, ok, hreq, z_ini = ops[0]
                m.update({"cuneta": eje, "hacia": [round(qe.x, 3), round(qe.y, 3)], "salida_m": round(Le, 2), "tubo_enterrado_m": round(Le, 2),
                          "S_tubo_pct": round(100 * St, 2), "z_salida": round(z_ini, 3), "z_llegada": round(z_ll, 3), "cf_cuneta": round(cf, 3),
                          "tirante_cuneta": round(yv, 3), "nivel_min": round(nivel, 3), "llega": llegada.estado(ok), "tramo": clave,
                          "h_req_cuneta": round(hreq, 3)})
                if not ok and hreq > tc.get("h_cuneta_max", P["prof_max_objetivo"]):
                    # no se entierra la cuneta para recibirla
                    m.update({"llega": "BAJO EL AGUA (TERRENO BAJO)", "tramo": None})
                    avisos.append("%s (%s %s): la tuberia del dado llega a %.3f, bajo el nivel del agua de %s (%.3f); para recibirla la cuneta "
                                  "tendria que tener %.2f m: llevar ese montante a otra esquina u otra cuneta, o poner una cuneta mas cerca." % (
                                      m["montante"], l["techo"], l["lado"], z_ll, eje, nivel, hreq))
            else:
                avisos.append("%s (%s %s) no tiene cuneta a menos de %.1f m: su tubo no llega; poner una cuneta cerca de esa esquina "
                              "(a lo largo del alero o transversal) o llevar el montante a otra esquina." % (m["montante"], l["techo"], l["lado"], tc["tubo_max"]))
            montantes.append(m); ms.append(m["montante"])
        lados.append({"techo": l["techo"], "lado": l["lado"], "A_m2": round(A, 2), "L_canaleta_m": round(L, 2), "Q_ls": round(Q, 2),
                      "montantes": n, "Q_por_montante_ls": round(Qm, 2), "tirante_m": round(y, 3), "borde_libre_m": round(tc["canaleta_h"] - y, 3),
                      "canaleta": "CUMPLE" if y <= hu + 1e-6 else "NO CUMPLE", "soportes": math.ceil(L / tc["sep_soporte"] - 1e-9) + 1,
                      "tapas": 2, "boquillas": n, "ids": ms, "alero": [list(c) for c in l["alero"].coords], "caida": l["ag"]["tipo"]})
    ent = [m for m in montantes if m.get("tubo_enterrado_m")]
    met = {"canaleta_m": round(sum(l["L_canaleta_m"] for l in lados), 2), "soportes_und": sum(l["soportes"] for l in lados),
           "tapas_und": sum(l["tapas"] for l in lados), "boquillas_und": sum(l["boquillas"] for l in lados),
           "montantes_und": len(montantes), "falsas_columnas_und": len(montantes), "dados_und": len(montantes),
           "codo_dado_und": len(ent), "tuberia_enterrada_m": round(sum(m["tubo_enterrado_m"] for m in ent), 2),
           "montantes_con_tuberia_und": len(ent), "montantes_sin_cuneta_und": len(montantes) - len(ent)}
    criterios = {"q_l_s_m2": round(K["q_m2"], 5), "Q_montante_4_ls": round(K["Q4"], 2), "A_por_montante_4_m2": round(K["A4"], 1),
                 "Q_canaleta_ls": round(K["Qcan"], 2), "parametros": tc,
                 "ubicacion": "visor (proyectista)" if cfg.get("montantes") else "esquinas de la edificacion (2 por lado; mas si el area lo pide)"}
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
    w["A1"] = "MONTANTES PVC 4\" (Wyly-Eaton, rs = %.2f; hasta 7/24 con 4 por lado): UBICACION Y SALIDA ENTERRADA DEL DADO A LA CUNETA" % tc["rs"]
    w["A1"].font = Font(bold=True, size=12)
    f = tabla(w, 3, ["MONTANTE", "TECHO", "LADO", "ESTE (m)", "NORTE (m)", "Q (l/s)", "D REQ. (pulg)", "D (pulg)", "CODO 90 EN DADO", "CUNETA",
                     "TUBERIA ENTERRADA (m)", "S (%)", "COTA SALIDA", "COTA LLEGADA", "COTA DE FONDO", "TIRANTE (m)", "NIVEL MINIMO (+5 cm)", "LLEGA"],
              [[x["montante"], x["techo"], x["lado"], x["x"], x["y"], x["Q_ls"], x["D_req_pulg"], x["D_pulg"], 1 if x.get("tubo_enterrado_m") else 0,
                x["cuneta"], x.get("tubo_enterrado_m"), x.get("S_tubo_pct"), x.get("z_salida"), x.get("z_llegada"), x.get("cf_cuneta"),
                x.get("tirante_cuneta"), x.get("nivel_min"), x.get("llega") or "NO LLEGA"] for x in T["montantes"]],
              [None, None, None, "0.000", "0.000", "0.00", "0.00", "0", "0", None, "0.00", "0.00", "0.000", "0.000", "0.000", "0.000", "0.000", None])
    for j, v in ((8, m["codo_dado_und"]), (10, m["tuberia_enterrada_m"])):
        w.cell(f, 1, "TOTAL").font = neg; c = w.cell(f, 1 + j, v); c.font = neg; c.border = borde
    k = wb.create_sheet("CRITERIOS")
    cr = T["criterios"]
    filas = [("Caudal por m2 de techo (l/s/m2)", cr["q_l_s_m2"]), ("Capacidad de un montante de 4\" (l/s)", cr["Q_montante_4_ls"]),
             ("Area que atiende un montante de 4\" (m2)", cr["A_por_montante_4_m2"]), ("Capacidad de la canaleta con borde libre (l/s)", cr["Q_canaleta_ls"]),
             ("Seccion de canaleta (m)", "%.2f x %.2f" % (tc["canaleta_b"], tc["canaleta_h"])), ("Pendiente de canaleta", "%.1f %%" % (100 * tc["S"])),
             ("Manning n", tc["n"]), ("Soportes de platina F°G° 1\" x 1/8\"", "@ %.2f m (REDONDEAR.MAS(L/%.2f) + 1)" % (tc["sep_soporte"], tc["sep_soporte"])),
             ("Salida del montante", "codo de 90 de 4\" en el dado y tuberia PVC 4\" enterrada hasta la cuneta (maximo %.1f m), S = %.1f %% (minimo %.1f %%)" % (
                 tc["tubo_max"], 100 * tc["S_tubo"], 100 * tc["S_tubo_min"])),
             ("Llegada a la cuneta", "fondo del tubo sobre el nivel del agua de la cuneta (cota de fondo + tirante) + 0.05 m"),
             ("A cargo del proyectista", "altura del montante, tubo que sube a la canaleta, codos del desvio, colgadores y abrazaderas")]
    for i, (a, b) in enumerate(filas):
        k.cell(2 + i, 1, a).border = borde; k.cell(2 + i, 2, b).border = borde
    k.column_dimensions["A"].width = 52; k.column_dimensions["B"].width = 60
    if SM is not None:
        from . import sumideros as _s
        _s.hoja(wb, SM)
    wb.properties.creator = ""; wb.properties.lastModifiedBy = ""
    wb.save(ruta); return ruta
