"""Hidraulica y las 11 comprobaciones del planteamiento de cunetas.

1 conectividad · 2 sin contrapendiente · 3 pendiente minima · 4 profundidades (0.30 / 0.25) · 5 empalmes · 6 descargas por el
cerco (terreno exterior bajo la cota de fondo) · 7 niveles (borde al ras del piso) · 8 capacidad (borde libre) · 9 velocidad
(<= 3.0 m/s; si pasa, gradas) · 10 distancia a muros · 11 todo dentro del cerco.

Caudal: metodo racional Q = C I A FS / 3.6e6 con el area de aporte de cada tramo (cada celda de 1 m2 dentro del cerco va al
tramo de cuneta mas cercano), C segun la superficie de la celda (techo, pavimento, estacionamiento, area verde) e I de la
lluvia de diseno (dato de DrenIE o Dick y Peschke con P24 y tc).
"""
import math

import numpy as np
from shapely.geometry import LineString, Point

from . import geom


def intensidad(lluvia):
    """I (mm/h). Directa, o por Dick y Peschke: P_D = P24 (D/1440)^0.25, I = 60 P_D / D (D = tc, minimo 10 min)."""
    if lluvia.get("I_mmh"): return float(lluvia["I_mmh"]), "dato"
    P24, tc = float(lluvia["P24"]), max(10.0, float(lluvia.get("tc_min", 10.0)))
    return 60.0 * P24 * (tc / 1440.0) ** 0.25 / tc, "Dick y Peschke (P24 = %.2f mm, tc = %.0f min)" % (P24, tc)


def yn(Q, S, n, b):
    lo, hi = 1e-4, 3.0
    for _ in range(100):
        y = (lo + hi) / 2; A = b * y; R = A / (b + 2 * y)
        if A * R ** (2 / 3) * math.sqrt(S) / n > Q: hi = y
        else: lo = y
    return (lo + hi) / 2


def _seg_dist(P, a, b):
    a = np.array(a); b = np.array(b); d = b - a; L2 = (d ** 2).sum()
    if L2 < 1e-12: return np.full(len(P), np.inf)          # tramo de largo cero: no recibe area
    t = np.clip(((P - a) @ d) / L2, 0, 1); Q = a + t[:, None] * d
    return np.sqrt(((P - Q) ** 2).sum(1))


def verificar(R, red, sitio, terreno, P, lluvia, hq_prev=None):
    """R = resultado de cotas.calcular. Devuelve (verificacion, hq) con hq = profundidad minima por capacidad de cada tramo."""
    ram = {r["codigo"]: r for r in R["ramales"]}; Nn = R["nudos"]
    D = set(red.descargas)
    res = []
    def ok(n, titulo, estado, detalle): res.append({"n": n, "comprobacion": titulo, "estado": estado, "detalle": detalle})
    # 1 conectividad
    fines = {c: r["nudos"][-1] for c, r in ram.items() if r["nudos"][-1] in D}
    cambio = True
    while cambio:
        cambio = False
        for c, r in ram.items():
            if c in fines: continue
            for c2, r2 in ram.items():
                if c2 != c and r["nudos"][-1] in r2["nudos"][1:] and c2 in fines: fines[c] = fines[c2]; cambio = True; break
    sin = [c for c in ram if c not in fines]
    if red.sin_salida: sin.append("%d nudos sin salida" % len(red.sin_salida))
    ok(1, "Conectividad: todos los ejes llegan a una descarga", "CUMPLE" if not sin else "NO CUMPLE",
       "%d ejes, %d descargas" % (len(ram), len(D)) if not sin else "sin salida: " + ", ".join(sin))
    # 2 contrapendiente
    malos = []
    for c, r in ram.items():
        Pf = r["perfil"]
        for i in range(1, len(Pf)):
            if Pf[i][2] > Pf[i - 1][2] + 1e-6: malos.append("%s prog %.2f" % (c, Pf[i][0])); break
    ok(2, "Sin contrapendiente en la cota de fondo (cada 0.50 m)", "CUMPLE" if not malos else "NO CUMPLE",
       "la cota de fondo baja en todos los puntos" if not malos else "; ".join(malos))
    # 3 pendiente minima
    tt = [(t["S"], c, t) for c, r in ram.items() for t in r["tramos"]] or [(P["S0"], "-", {"de": "-", "a": "-"})]
    smin = min(tt, key=lambda e: e[0])
    ok(3, "Pendiente minima de la cota de fondo >= %.1f %%" % (100 * P["S0"]), "CUMPLE" if smin[0] >= P["S0"] - 1e-4 else "NO CUMPLE",
       "minima %.2f %% (%s %s-%s); maxima %.2f %%" % (100 * smin[0], smin[1], smin[2]["de"], smin[2]["a"], 100 * max(e[0] for e in tt)))
    # 4 profundidades
    def libre(r, p):
        return p[1] - p[2] - (P["e_tapa"] if any(a - 1e-6 <= p[0] <= b + 1e-6 for a, b in r["tapados"]) else 0.0)
    h0 = [round(libre(r, r["perfil"][0]), 3) for r in ram.values()]
    hmn = min(((libre(r, p), c, p[0]) for c, r in ram.items() for p in r["perfil"]), key=lambda e: e[0])
    hmx = max(((p[1] - p[2], c, p[0]) for c, r in ram.items() for p in r["perfil"]), key=lambda e: e[0])
    ok(4, "Profundidad: %.2f m al inicio y altura libre >= %.2f m (bajo la losa en los tapados)" % (P["h0"], P["hmin"]),
       "CUMPLE" if min(h0) >= P["h0"] - 1e-3 and hmn[0] >= P["hmin"] - 1e-3 else "NO CUMPLE",
       "inicio %.2f a %.2f; altura libre minima %.2f (%s); profundidad maxima %.2f (%s, prog %.1f)" % (min(h0), max(h0), hmn[0], hmn[1], hmx[0], hmx[1], hmx[2]))
    # 5 empalmes
    emp = []
    for c, r in ram.items():
        fin = r["nudos"][-1]
        if fin in D: continue
        for c2, r2 in ram.items():
            # recibe la cuneta que pasa por el nudo (no otra que tambien termina en el)
            if c2 != c and fin in r2["nudos"][1:-1]:
                acc, s_n = 0.0, None
                for t in r2["tramos"]:
                    acc += t["L"]
                    if t["a"] == fin: s_n = acc
                cf_rec = min(r2["perfil"], key=lambda p: abs(p[0] - s_n))[2]
                emp.append({"llega": c, "recibe": c2, "nudo": fin, "cf_llega": r["perfil"][-1][2], "cf_recibe": cf_rec,
                            "caida": round(r["perfil"][-1][2] - cf_rec, 3)})
    mal = [e for e in emp if e["caida"] < -0.005]
    ok(5, "Empalmes: la cuneta que llega no queda por debajo de la que recibe", "CUMPLE" if not mal else "NO CUMPLE",
       ("%d empalmes; caida maxima %.2f m" % (len(emp), max([e["caida"] for e in emp] + [0]))) if not mal else
       "; ".join("%s en %s (%.3f)" % (e["llega"], e["nudo"], e["caida"]) for e in mal))
    # 6 descargas
    desc = []
    for d, info in sorted(red.descargas.items(), key=lambda e: e[1]["s"]):
        rr = [r for r in ram.values() if r["nudos"][-1] == d]
        if not rr: continue
        cf = min(r["perfil"][-1][2] for r in rr); x, y = info["q"]; nin = info["nin"]
        ext = []
        for k in range(1, 41):
            dd = 0.25 * k; zt = terreno.z(x - nin[0] * dd, y - nin[1] * dd)
            if np.isfinite(zt): ext.append((dd, zt))
        sobre = max([zt - cf for dd, zt in ext if dd <= 1.0] + [-9])
        baja = next((dd for dd, zt in ext if zt <= cf - P["desc_margen"]), None)
        okd = baja is not None and baja <= P["desc_dist_ext"]
        desc.append({"D": d, "x": round(x, 3), "y": round(y, 3), "cf": round(cf, 3), "terreno": round(terreno.z(x, y), 2),
                     "sale_a_m": baja, "perfilado_max": round(max(sobre, 0), 2), "estado": "SALE POR GRAVEDAD" if okd else "NO SALE",
                     "exterior": [[dd, round(zt, 2)] for dd, zt in ext[:16]]})
    malas = [d for d in desc if d["estado"] != "SALE POR GRAVEDAD"]
    ok(6, "Descargas por el cerco: el agua sale por gravedad sin obras fuera del cerco", "CUMPLE" if not malas else "NO CUMPLE",
       "; ".join("%s C.F. %.3f: %s" % (d["D"], d["cf"], ("terreno exterior bajo la C.F. a %.2f m del cerco" % d["sale_a_m"]) if d["sale_a_m"]
                                                       else "el terreno exterior no baja de la C.F.") for d in desc))
    # 7 niveles: borde de cuneta al ras del piso (interior nivelado) y de cada zona
    altos = 0
    sector = getattr(sitio, "por_sector", False)
    if sector:
        # niveles por plataforma, rampa o eje: el borde queda entre el nivel mas bajo y el mas alto definidos
        nv = [sitio.borde] + [q["borde"] for q in sitio.plataformas] + [z[1] for z in sitio.zonas] + \
             [v for r in sitio.rampas for v in (r["za"], r["zb"])] + [float(b["npt"]) - b["rebaje"] for b in sitio.bordes_eje if b["npt"] is not None]
        tope = max(v for v in nv if v is not None)
    if sitio.modo == "nivelado":
        for c, r in ram.items():
            for p in r["perfil"]:
                if sector:
                    if p[1] > tope + 0.005: altos += 1
                elif p[1] > sitio.borde + 0.005 and not any(abs(p[1] - z[1]) < 0.005 for z in sitio.zonas): altos += 1
    if sector:
        det = "bordes por sector: " + ", ".join(["%s +%.2f" % (q["nombre"], q["borde"]) for q in sitio.plataformas] +
                                                 ["%s +%.2f a +%.2f" % (r["nombre"], r["za"], r["zb"]) for r in sitio.rampas] +
                                                 (["%d ejes con su propio borde" % len(sitio.bordes_eje)] if sitio.bordes_eje else []) +
                                                 ["resto +%.2f" % sitio.borde])
    else:
        det = ("borde +%.2f en la red; zonas: %s" % (sitio.borde, ", ".join("%s +%.2f" % (z[2], z[1]) for z in sitio.zonas) or "ninguna")) \
            if sitio.modo == "nivelado" else "rasante = terreno (modo terreno)"
    ok(7, "Borde de la cuneta al ras del piso" + (" (+%.2f)" % sitio.borde if sitio.borde and not sector else " (por plataformas)" if sector else ""),
       "CUMPLE" if not altos else "NO CUMPLE", det)
    # 8 y 9 capacidad y velocidad
    I, fuente_I = intensidad(lluvia)
    ce = sitio.cerco; x0, y0, x1, y1 = ce.bounds
    xs = np.arange(math.floor(x0), math.ceil(x1), 1.0) + 0.5; ys = np.arange(math.floor(y0), math.ceil(y1), 1.0) + 0.5
    XX, YY = np.meshgrid(xs, ys); Pc = np.c_[XX.ravel(), YY.ravel()]
    import shapely
    Pc = Pc[shapely.contains_xy(ce, Pc[:, 0], Pc[:, 1])]
    segs = [(c, j, Nn[t["de"]], Nn[t["a"]]) for c, r in ram.items() for j, t in enumerate(r["tramos"])]
    Dm = np.stack([_seg_dist(Pc, a, b) for c, j, a, b in segs], 1); asg = Dm.argmin(1)
    Ccel, tipo = sitio.c_celdas(Pc[:, 0], Pc[:, 1])
    # techos: cada mitad descarga por su alero (canaleta y montante) a la cuneta que esta debajo, no a la mas cercana
    techos_ok = 0; sin_cuneta = []
    from shapely.geometry import Point as _Pt
    for ag in getattr(sitio, "aguas", []):
        m = shapely.contains_xy(ag["poligono"], Pc[:, 0], Pc[:, 1]) & (tipo == "techo")
        if not m.any(): continue
        if ag["tipo"] == "flecha":
            # cada m2 sigue la flecha hasta el borde del techo; de ahi a la cuneta que esta debajo (<= 1.5 m del punto de salida)
            ux, uy = ag["flecha"]; borde = ag["techo_poligono"].exterior
            idx = np.nonzero(m)[0]; sale = []
            for x, y in Pc[idx]:
                rayo = LineString([(x, y), (x + ux * 300, y + uy * 300)]).intersection(borde)
                pts = [q for q in (rayo.geoms if hasattr(rayo, "geoms") else [rayo]) if not q.is_empty]
                q = min(pts, key=lambda q: q.distance(_Pt(x, y))) if pts else _Pt(x, y)
                sale.append((q.x, q.y))
            sale = np.array(sale)
            Dc = np.stack([_seg_dist(sale, a, b) for c, j, a, b in segs], 1)
            k_min = Dc.argmin(1); d_min = Dc.min(1)
            bien = d_min <= 1.5
            asg[idx[bien]] = k_min[bien]; techos_ok += int(bien.sum())
            if (~bien).sum() > 0:
                c0 = ag["poligono"].representative_point()
                sin_cuneta.append({"techo": ag["techo"], "area_m2": int((~bien).sum()), "punto": [round(c0.x, 2), round(c0.y, 2)]})
            continue
        al = ag["alero"]
        def bajo_alero(a, b):
            """Cuneta paralela al alero (< 20 grados), a <= 1.5 m y que corre a lo largo de el (se solapan al proyectar)."""
            sg = LineString([a, b])
            if sg.length < 0.05 or sg.distance(al) > 1.5: return False
            (ux, uy), _ = geom.unit(a, b); (vx, vy), _ = geom.unit(*al.coords)
            if abs(ux * vx + uy * vy) < math.cos(math.radians(20)): return False
            s1, s2 = sorted((al.project(_Pt(*a)), al.project(_Pt(*b))))
            return s2 - s1 > 0.3 and s1 < al.length - 0.3 and s2 > 0.3
        cand = [k for k, (c, j, a, b) in enumerate(segs) if bajo_alero(a, b)]
        if not cand:
            c0 = ag["poligono"].representative_point()
            sin_cuneta.append({"techo": ag["techo"], "area_m2": int(m.sum()), "punto": [round(c0.x, 2), round(c0.y, 2)]}); continue
        idx = np.nonzero(m)[0]
        proy = np.array([[al.interpolate(al.project(_Pt(x, y))).x, al.interpolate(al.project(_Pt(x, y))).y] for x, y in Pc[idx]])
        Dc = np.stack([_seg_dist(proy, segs[k][2], segs[k][3]) for k in cand], 1)
        asg[idx] = np.array(cand)[Dc.argmin(1)]; techos_ok += len(idx)
    # area de aporte de cada tramo por grupo de superficie: techos, pisos (veredas, patios, estacionamiento, juegos, la propia
    # cuneta) y areas verdes; con su C, para mostrar cuanto caudal llega de cada uno
    GR = {"techo": "techo", "verde": "verde"}
    area, areaC, grupo = {}, {}, {}
    for k, (c, j, a, b) in enumerate(segs):
        sel = asg == k; area[(c, j)] = float(sel.sum()); areaC[(c, j)] = float(Ccel[sel].sum())
        g = {"techo": [0.0, 0.0], "pisos": [0.0, 0.0], "verde": [0.0, 0.0]}
        for tp in P["C"]:
            m = sel & (tipo == tp); n = float(m.sum())
            if n: gg = g[GR.get(tp, "pisos")]; gg[0] += n; gg[1] += float(Ccel[m].sum())
        grupo[(c, j)] = g
    acum = {}
    def total(c, prof=0):
        if c in acum: return acum[c]
        r = ram[c]; out = []; v = np.zeros(8)          # A, AC, A techo, AC techo, A pisos, AC pisos, A verde, AC verde
        for j, t in enumerate(r["tramos"]):
            for c2, r2 in ram.items():
                if c2 != c and r2["nudos"][-1] == t["de"] and prof < 200: v = v + total(c2, prof + 1)[-1]
            g = grupo[(c, j)]
            v = v + np.array([area[(c, j)], areaC[(c, j)], *g["techo"], *g["pisos"], *g["verde"]]); out.append(v.copy())
        acum[c] = out; return out
    # seccion de cada tramo: el menor ancho libre (de b_int a b_max, de 5 en 5 cm) con el que el tirante mas el borde libre cabe
    # en la profundidad que da el perfil; sin angostarse aguas abajo. Si ni con b_max cabe, se pide profundizar (redondeado a 5 cm).
    # El proyectista puede fijar el ancho de un eje (secciones: {"EJE-01": 0.45}) y el programa lo verifica.
    paso = P.get("paso_seccion", 0.05); bmin = P["b_int"]; bmax = max(P.get("b_max", bmin), bmin)
    anchos = [round(bmin + paso * i, 3) for i in range(int(round((bmax - bmin) / paso)) + 1)]
    fijas = P.get("secciones") or {}
    sube = lambda v: math.ceil(v / paso - 1e-6) * paso
    filas = []; hq = dict(hq_prev or {})
    # 1) ancho que pide cada tramo; 2) una sola medida por sector (o eje): la mayor que pida cualquiera de sus tramos
    def pide(t, muestras, S):
        """muestras: [(Q, h libre)] a lo largo del tramo (el caudal crece con el largo; bajo la losa solo donde esta tapado)."""
        hmax_t = max(t["h_de"], t["h_a"])
        def basta(bb):
            if P.get("h_b_max") and hmax_t > P["h_b_max"] * bb + 1e-9: return False   # limite opcional de profundidad / ancho
            for Q, hd in muestras:
                if Q <= 0: continue
                y_ = yn(Q, S, P["n_cap"], bb)
                if not (y_ + P["BL"] <= hd + 1e-9 and y_ <= P.get("y_b_max", 1.0) * bb + 1e-9): return False
            return True
        return next((bb for bb in anchos if basta(bb)), anchos[-1])

    def muestras_de(c, r, j, t, Q, Ac):
        """Caudal y altura libre en cada punto del perfil del tramo (cada 0.50 m): el caudal va del que entra al tramo al de su
        final en proporcion al largo; la altura libre es la del perfil, menos la losa tapa solo donde el tramo esta tapado."""
        s0 = sum(x["L"] for x in r["tramos"][:j]); s1 = s0 + t["L"]
        Qin = I * (Ac[j - 1][1] if j > 0 else Ac[0][1] - areaC[(c, 0)]) / 3.6e6 * P["FS"]
        tap = lambda s_: any(a - 1e-6 <= s_ <= b + 1e-6 for a, b in r.get("tapados", []))
        out = []
        for s_, nct, ncf in r.get("perfil", []):
            if s0 - 1e-6 <= s_ <= s1 + 1e-6:
                fr = (s_ - s0) / t["L"] if t["L"] > 0 else 1.0
                out.append((Qin + (Q - Qin) * fr, nct - ncf - (P["e_tapa"] if tap(s_) else 0.0)))
        if not out: out = [(Q, min(t["h_de"], t["h_a"]) - (P["e_tapa"] if t["L_tapado"] > 0 else 0.0))]
        return out
    uni = P.get("uniforme", "sector")
    grupo_de = lambda c: (fines.get(c, c) if uni == "sector" else c)
    datos, pedido = [], {}
    for c, r in ram.items():
        Ac = total(c)
        for j, t in enumerate(r["tramos"]):
            v = Ac[j]; Q = I * v[1] / 3.6e6 * P["FS"]; S = max(t["S"], P["S0"])
            mu = muestras_de(c, r, j, t, Q, Ac)
            bp = pide(t, mu, S); datos.append((c, t, v, Q, S, mu, bp))
            k = grupo_de(c) if uni != "tramo" else (c, t["de"])
            pedido[k] = max(pedido.get(k, 0.0), bp)
    for c, t, v, Q, S, mu, bp in datos:
        if c in fijas: b = float(fijas[c]); origen_b = "adoptado por el proyectista"
        else:
            b = pedido[grupo_de(c) if uni != "tramo" else (c, t["de"])]
            origen_b = "caudal del tramo" if abs(b - bp) < 1e-9 else ("mayor del sector (%s)" % grupo_de(c) if uni == "sector" else "mayor del eje")
        # punto critico del tramo: el de menor borde libre con su caudal
        crit = min(((hh - (yn(qq, S, P["n_cap"], b) if qq > 0 else 0.0), qq, hh) for qq, hh in mu), key=lambda e: e[0])
        hd = crit[2]; y = yn(crit[1], S, P["n_cap"], b) if crit[1] > 0 else 0.0
        yv = yn(Q, S, P["n_vel"], b) if Q > 0 else 1.0
        V = Q / (b * yv) if Q > 0 else 0.0
        q = lambda AC: round(1000 * I * AC / 3.6e6 * P["FS"], 2)
        hmax_t = max(t["h_de"], t["h_a"])
        f = {"eje": c, "sector": fines.get(c, "-"), "de": t["de"], "a": t["a"], "L": round(t["L"], 2), "A_m2": round(v[0], 0),
             "C": round(v[1] / v[0], 3) if v[0] else 0,
             "A_techo_m2": round(v[2], 0), "A_pisos_m2": round(v[4], 0), "A_verde_m2": round(v[6], 0),
             "Q_techo_ls": q(v[3]), "Q_pisos_ls": q(v[5]), "Q_verde_ls": q(v[7]),
             "Q_ls": round(1000 * Q, 2), "S_pct": round(100 * S, 2), "b_pide": round(bp, 3), "b": round(b, 3), "ancho_por": origen_b,
             "ancho_total": round(b + 2 * P["e_muro"], 3), "excavacion_max": round(hmax_t + P["e_fondo"] + P["e_solado"], 3),
             "h_de": round(t["h_de"], 3), "h_a": round(t["h_a"], 3), "y": round(y, 3), "h": round(hd, 3), "Q_critico_ls": round(1000 * crit[1], 2), "Q_in_ls": round(1000 * min(q_ for q_, h_ in mu), 2), "borde_libre": round(hd - y, 3),
             "V": round(V, 2), "cap": "CUMPLE" if hd - y >= P["BL"] - 1e-3 else "NO CUMPLE", "vel": "CUMPLE" if V <= P["Vmax"] else "GRADAS"}
        filas.append(f)
        need = sube(y + P["BL"]); clave = "%s|%s|%s" % (c, t["de"], t["a"])
        if need > P["hmin"] and hd - y < P["BL"]: hq[clave] = round(max(need, hq.get(clave, 0)), 3)
    ncap = [f for f in filas if f["cap"] != "CUMPLE"]; nvel = [f for f in filas if f["vel"] != "CUMPLE"]
    pc = min(filas, key=lambda f: f["borde_libre"]); pv = max(filas, key=lambda f: f["V"])
    Atot = sum(area.values()); Cp = sum(areaC.values()) / Atot if Atot else 0
    ok(8, "Capacidad con el caudal de diseno (borde libre >= %.2f m)" % P["BL"], "CUMPLE" if not ncap else "NO CUMPLE",
       "I = %.2f mm/h, C ponderado = %.3f, area %.0f m2; menor borde libre %.3f m en %s %s-%s (Q %.1f l/s)" % (
           I, Cp, Atot, pc["borde_libre"], pc["eje"], pc["de"], pc["a"], pc["Q_ls"]) +
       ("" if not ncap else "; no cumplen: " + ", ".join("%s %s-%s" % (f["eje"], f["de"], f["a"]) for f in ncap)))
    ok(9, "Velocidad maxima %.1f m/s (concreto)" % P["Vmax"], "CUMPLE" if not nvel else "CUMPLE CON GRADAS",
       ("V max %.2f m/s" % pv["V"]) if not nvel else "con gradas: " + ", ".join("%s %s-%s (V %.2f)" % (f["eje"], f["de"], f["a"], f["V"]) for f in nvel))
    # 13 secciones constructivas (minimo 0.30 x 0.30, medidas de 5 en 5 cm)
    raras = [f for f in filas if f["b"] < bmin - 1e-6 or abs(f["b"] / paso - round(f["b"] / paso)) > 1e-6]
    anchas = [f for f in filas if f["b"] > bmax + 1e-6]
    hondas = [f for f in filas if P.get("h_b_max") and max(f["h_de"], f["h_a"]) > P["h_b_max"] * f["b"] + 1e-6]
    bs = sorted({f["b"] for f in filas})
    estado = "NO CUMPLE" if raras or hmn[0] < P["hmin"] - 1e-3 else ("REVISAR" if anchas or hondas else "CUMPLE")
    det = "anchos libres usados: %s (total %s)" % (", ".join("%.2f" % x for x in bs), ", ".join("%.2f" % (x + 2 * P["e_muro"]) for x in bs))
    if raras: det += "; fuera de medida: " + ", ".join("%s %s-%s b %.3f" % (f["eje"], f["de"], f["a"], f["b"]) for f in raras)
    if anchas: det += "; mas anchas que %.2f libre (adoptadas): %s" % (bmax, ", ".join(sorted({f["eje"] for f in anchas})))
    if hondas: det += "; profundidad mayor que %.1f veces el ancho (revisar encofrado): %s" % (P.get("h_b_max") or 0, ", ".join(sorted({f["eje"] for f in hondas})))
    ok(13, "Secciones constructivas: ancho libre de %.2f a %.2f m (total %.2f a %.2f), altura libre >= %.2f m, medidas de %.0f en %.0f cm" % (
        bmin, bmax, bmin + 2 * P["e_muro"], bmax + 2 * P["e_muro"], P["hmin"], 100 * paso, 100 * paso), estado, det)
    # 10 uniones nuevas lejos de muros, edificaciones y losas (sin contar los 0.60 m donde se conectan a una cuneta)
    obst = red.obst
    if obst.is_empty:
        ok(10, "Uniones nuevas lejos de las edificaciones (>= %.2f m)" % P["dist_muro"], "SIN DATO", "no se indico capa de muros ni techos")
    else:
        from shapely.ops import substring
        dmin, cerca = 9e9, []
        for c, r in ram.items():
            for t in r["tramos"]:
                if t["origen"] == "usuario": continue      # las lineas del usuario mandan
                ls = LineString([Nn[t["de"]], Nn[t["a"]]])
                cuerpo = substring(ls, 0.6, ls.length - 0.6) if ls.length > 1.3 else None
                if cuerpo is None: continue
                d = cuerpo.distance(obst); dmin = min(dmin, d)
                if d < P["dist_muro"]: cerca.append("%s %s-%s a %.2f m" % (c, t["de"], t["a"], d))
        base_o = "muros" if not sitio.muros.is_empty else "techos reducidos 1.00 m (no hay capa de muros)"
        ok(10, "Uniones nuevas lejos de las edificaciones y losas (>= %.2f m)" % P["dist_muro"], "CUMPLE" if not cerca else "REVISAR",
           (("distancia minima %.2f m" % dmin) if dmin < 9e8 else "sin uniones nuevas") + " (referencia: %s)" % base_o
           if not cerca else "; ".join(cerca) + " (referencia: %s)" % base_o)
    # 12 todas las lineas del usuario con cuneta (las lineas del usuario mandan)
    from shapely.ops import unary_union
    red_buf = unary_union([LineString([Nn[t["de"]], Nn[t["a"]]]) for r in ram.values() for t in r["tramos"]]).buffer(P["b_int"] / 2 + P["e_muro"] + 0.2)
    faltan = []
    for k, e in enumerate(red.E):
        ls = LineString([red.N[e["u"]], red.N[e["v"]]]); f = ls.difference(red_buf).length
        if f > 0.5: faltan.append(f)
    ok(12, "Todas las lineas de cuneta del usuario quedan con cuneta", "CUMPLE" if not faltan else "NO CUMPLE",
       "%d tramos del usuario revisados" % len(red.E) if not faltan else "%d tramos sin cuneta (%.1f m)" % (len(faltan), sum(faltan)))
    # 11 dentro del cerco
    fuera = []
    for c, r in ram.items():
        for t in r["tramos"]:
            if t["a"] in D: continue
            ls = LineString([Nn[t["de"]], Nn[t["a"]]])
            for lado in (-0.30, 0.30):
                o = ls.offset_curve(lado) if ls.length > 0.01 else ls
                if not ce.buffer(1e-3).covers(o): fuera.append("%s %s-%s" % (c, t["de"], t["a"])); break
    ok(11, "Toda la red dentro del cerco (limite de intervencion)", "CUMPLE" if not fuera else "NO CUMPLE",
       "solo las %d descargas atraviesan el cerco" % len(D) if not fuera else "%d tramos con borde fuera: %s" % (len(fuera), ", ".join(fuera[:6])))
    sup = {k: float((tipo == k).sum()) for k in P["C"]}
    res.sort(key=lambda c: c["n"])
    out = {"comprobaciones": res, "descargas": desc, "hidraulica": filas, "empalmes": emp,
           "hidrologia": {"I": round(I, 2), "fuente_I": fuente_I, "C": round(Cp, 3), "A_total": Atot, "FS": P["FS"],
                          "superficies": {k: {"A": v, "C": P["C"][k]} for k, v in sup.items()},
                          "techo_por_caida_m2": techos_ok,
                          "aleros_sin_cuneta": sin_cuneta,
                          "aporte_por_tramo": [{"eje": c, "tramo": j, "de": ram[c]["tramos"][j]["de"], "a": ram[c]["tramos"][j]["a"],
                                                **{t: float((tipo[asg == k] == t).sum()) for t in P["C"]}}
                                               for k, (c, j, a, b) in enumerate(segs)]}}
    return out, hq
