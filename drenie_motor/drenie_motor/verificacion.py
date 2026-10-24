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
    tt = [(t["S"], c, t) for c, r in ram.items() for t in r["tramos"]]
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
            if c2 != c and fin in r2["nudos"][1:]:
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
    if sitio.modo == "nivelado":
        for c, r in ram.items():
            for p in r["perfil"]:
                if p[1] > sitio.borde + 0.005 and not any(abs(p[1] - z[1]) < 0.005 for z in sitio.zonas): altos += 1
    ok(7, "Borde de la cuneta al ras del piso" + (" (+%.2f)" % sitio.borde if sitio.borde else ""), "CUMPLE" if not altos else "NO CUMPLE",
       ("borde +%.2f en la red; zonas: %s" % (sitio.borde, ", ".join("%s +%.2f" % (z[2], z[1]) for z in sitio.zonas) or "ninguna"))
       if sitio.modo == "nivelado" else "rasante = terreno (modo terreno)")
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
    area, areaC = {}, {}
    for k, (c, j, a, b) in enumerate(segs):
        sel = asg == k; area[(c, j)] = float(sel.sum()); areaC[(c, j)] = float(Ccel[sel].sum())
    acum = {}
    def total(c, prof=0):
        if c in acum: return acum[c]
        r = ram[c]; out = []; A = AC = 0.0
        for j, t in enumerate(r["tramos"]):
            for c2, r2 in ram.items():
                if c2 != c and r2["nudos"][-1] == t["de"] and prof < 200:
                    A += total(c2, prof + 1)[-1][0]; AC += total(c2, prof + 1)[-1][1]
            A += area[(c, j)]; AC += areaC[(c, j)]; out.append((A, AC))
        acum[c] = out; return out
    filas = []; hq = dict(hq_prev or {}); b = P["b_int"]
    for c, r in ram.items():
        Ac = total(c)
        for j, t in enumerate(r["tramos"]):
            Q = I * Ac[j][1] / 3.6e6 * P["FS"]
            S = max(t["S"], P["S0"]); y = yn(Q, S, P["n_cap"], b) if Q > 0 else 0.0; yv = yn(Q, S, P["n_vel"], b) if Q > 0 else 1.0
            V = Q / (b * yv) if Q > 0 else 0.0
            hd = min(t["h_de"], t["h_a"]) - (P["e_tapa"] if t["L_tapado"] > 0 else 0.0)
            f = {"eje": c, "de": t["de"], "a": t["a"], "A_m2": round(Ac[j][0], 0), "C": round(Ac[j][1] / Ac[j][0], 3) if Ac[j][0] else 0,
                 "Q_ls": round(1000 * Q, 2), "S_pct": round(100 * S, 2), "y": round(y, 3), "h": round(hd, 3), "borde_libre": round(hd - y, 3),
                 "V": round(V, 2), "cap": "CUMPLE" if hd - y >= P["BL"] - 1e-3 else "NO CUMPLE", "vel": "CUMPLE" if V <= P["Vmax"] else "GRADAS"}
            filas.append(f)
            need = y + P["BL"] + 0.005; clave = "%s|%s|%s" % (c, t["de"], t["a"])
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
    # 10 muros (o cuerpo de las edificaciones)
    obst = red.obst
    if obst.is_empty:
        ok(10, "El eje no corta muros de las edificaciones (>= %.2f m)" % P["dist_muro"], "SIN DATO", "no se indico capa de muros ni techos")
    else:
        dmin, cerca = 9e9, 0
        for c, r in ram.items():
            for t in r["tramos"]:
                if t["origen"] == "usuario": continue      # las lineas del usuario mandan
                ls = LineString([Nn[t["de"]], Nn[t["a"]]]); d = ls.distance(obst); dmin = min(dmin, d)
                if d < P["dist_muro"]: cerca += 1
        ok(10, "Uniones nuevas lejos de las edificaciones (>= %.2f m)" % P["dist_muro"], "CUMPLE" if cerca == 0 else "REVISAR",
           ("distancia minima %.2f m" % dmin) if dmin < 9e8 else "sin uniones nuevas")
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
    out = {"comprobaciones": res, "descargas": desc, "hidraulica": filas, "empalmes": emp,
           "hidrologia": {"I": round(I, 2), "fuente_I": fuente_I, "C": round(Cp, 3), "A_total": Atot, "FS": P["FS"],
                          "superficies": {k: {"A": v, "C": P["C"][k]} for k, v in sup.items()}}}
    return out, hq
