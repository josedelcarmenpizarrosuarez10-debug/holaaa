"""Verificacion del planteamiento preliminar de cunetas - I.E. N.° 0590, Barranquita (10 comprobaciones).

1. Conectividad: todo ramal termina en una descarga o en otro ramal que llega a una descarga.
2. Sin contrapendiente: la cota de fondo baja en cada paso de 0.50 m de todos los ramales.
3. Pendiente minima de la cota de fondo >= 0.5 % en cada tramo.
4. Profundidad: h = 0.30 m al inicio de cada ramal y h >= 0.25 m en todo el recorrido.
5. Empalmes: la cuneta que llega lo hace a la misma cota o por encima de la que recibe (no remansa).
6. Descargas por el cerco: el terreno exterior no queda sobre la cota de fondo de la descarga (no se excava fuera del
   cerco) y baja por debajo de ella a pocos metros (el agua se aleja sola por la pendiente natural).
7. Niveles: borde de la cuneta al ras del piso (NPT +184.65) y 0.05 m sobre el area verde (+184.60); al ras del patio de maniobra (+184.50).
8. Capacidad: tirante normal con el caudal de diseno <= h - 0.05 m (borde libre) en cada tramo.
9. Velocidad: V <= 3.0 m/s (concreto, CE.040); los tramos que pasan se resuelven con gradas o caidas.
10. Interferencias: el eje de la cuneta no corta muros de los bloques (distancia al muro >= 0.30 m).
11. Limite de intervencion: toda la red queda dentro del cerco perimetrico; solo las descargas lo atraviesan.

Caudal de diseno: metodo racional con el area tributaria de cada tramo dentro del cerco (cada punto de 1 m2
va a la cuneta mas cercana; techos a dos aguas: cada mitad al alero de su lado), C por superficie (techos y pavimentos 0.88,
areas verdes 0.40) e I de hidrologia_b (estacion Pongo de Caynarachi 1989-2013, T = 25 anos, tc = 10 min), factor de seguridad 1.15.
Uso: python3 herramientas/barranquita/verifica_b.py -> entregables_barranquita/_calc/verificacion.json
     python3 herramientas/barranquita/verifica_b.py --solo-lluvia: cambio de lluvia sin base del sitio (base_sitio.pkl): rehace las
     comprobaciones 8 y 9 con la I vigente sobre la geometria y las areas de verificacion.json (Q proporcional a I, metodo racional);
     exige hmin_req.json vacio (ninguna profundidad fijada por capacidad), asi la geometria no depende de la lluvia.
"""
import os, sys, json, math
import numpy as np
from matplotlib.path import Path
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import diseno_b as DS

CALC = os.path.join(RAIZ, "entregables_barranquita", "_calc")
import hidrologia_b as H
HID = H.resultados()                         # lluvia de diseno: Pongo de Caynarachi 1989-2013 (T = 25 anos, Dick y Peschke)
TC, P10, I_MMH = HID["tc"], HID["P_tc"], HID["I"]
FS = 1.15                                    # factor de seguridad de los caudales (mismo criterio de los proyectos de Morales)
N_CAP, N_VEL, VMAX = 0.015, 0.013, 3.0
RECEPTOR = {}
DIR_EXT = DS.DIR_SALIDA


def yn(Q, S, n):
    lo, hi = 1e-4, 3.0
    for _ in range(100):
        y = (lo + hi) / 2; A = DS.B_INT * y; R = A / (DS.B_INT + 2 * y)
        if A * R ** (2 / 3) * math.sqrt(S) / n > Q: hi = y
        else: lo = y
    return (lo + hi) / 2


def seg_dist(P, a, b):
    """Distancia de los puntos P (n x 2) al segmento a-b y parametro t."""
    a = np.array(a); b = np.array(b); d = b - a; L2 = (d ** 2).sum()
    t = np.clip(((P - a) @ d) / L2, 0, 1); Q = a + t[:, None] * d
    return np.sqrt(((P - Q) ** 2).sum(1)), t


def main():
    import terreno_b as T
    R = json.load(open(os.path.join(CALC, "diseno.json"))); z = T.modelo(); G = T.cargar()
    ram = {r["codigo"]: r for r in R["ramales"]}; N = R["nudos"]; nom = R["nombre"]
    res = []
    def ok(n, titulo, cumple, detalle):
        res.append({"n": n, "comprobacion": titulo, "estado": cumple, "detalle": detalle})
    # 1 conectividad
    fines = {}
    for c, r in ram.items():
        fin = r["nudos"][-1]
        if fin in DS.DESCARGAS: fines[c] = fin
    cambio = True
    while cambio:
        cambio = False
        for c, r in ram.items():
            if c in fines: continue
            fin = r["nudos"][-1]
            for c2, r2 in ram.items():
                if c2 != c and fin in r2["nudos"][1:] and c2 in fines: fines[c] = fines[c2]; cambio = True; break
    sin = [c for c in ram if c not in fines]
    ok(1, "Conectividad: todos los ramales llegan a una descarga", "CUMPLE" if not sin else "NO CUMPLE",
       "%d ramales: " % len(ram) + "" + ", ".join("%s->%s" % (c, fines[c]) for c in ram) if not sin else "sin salida: " + ", ".join(sin))
    # 2 contrapendiente
    malos = []
    for c, r in ram.items():
        P = r["perfil"]
        for i in range(1, len(P)):
            if P[i][2] > P[i - 1][2] + 1e-6: malos.append("%s prog %.2f" % (c, P[i][0])); break
    ok(2, "Sin contrapendiente en la cota de fondo (cada 0.50 m)", "CUMPLE" if not malos else "NO CUMPLE",
       "la cota de fondo baja en todos los puntos" if not malos else "; ".join(malos))
    # 3 pendiente minima
    smin = min(((t["S"], c, t) for c, r in ram.items() for t in r["tramos"]), key=lambda e: (e[0], e[1]))
    ok(3, "Pendiente minima de la cota de fondo >= 0.5 %", "CUMPLE" if smin[0] >= DS.S0 - 1e-4 else "NO CUMPLE",
       "minima %.2f %% (%s %s-%s); maxima %.2f %%" % (100 * smin[0], smin[1], nom[smin[2]["de"]], nom[smin[2]["a"]],
                                                     100 * max(t["S"] for r in ram.values() for t in r["tramos"])))
    # 4 profundidades
    h0 = [round(r["perfil"][0][1] - r["perfil"][0][2], 3) for r in ram.values()]
    def libre(r, p):                                     # altura libre: en tramo tapado, bajo la losa de 0.10 m
        return p[1] - p[2] - (DS.E_TAPA if any(a - 1e-6 <= p[0] <= b + 1e-6 for a, b in r["tapados"]) else 0.0)
    hmin = min(((libre(r, p), c, p[0]) for c, r in ram.items() for p in r["perfil"]), key=lambda e: e[0])
    hmax = max(((p[1] - p[2], c, p[0]) for c, r in ram.items() for p in r["perfil"]), key=lambda e: e[0])
    ok(4, "Profundidad: 0.30 m al inicio y altura libre >= 0.25 m en todo el recorrido (bajo la losa en los tapados)",
       "CUMPLE" if min(h0) >= DS.H0 - 1e-3 and hmin[0] >= DS.HMIN - 1e-3 else "NO CUMPLE",
       "inicio %.2f a %.2f; altura libre minima %.2f (%s); profundidad maxima %.2f (%s, prog %.1f)" % (min(h0), max(h0), hmin[0], hmin[1], hmax[0], hmax[1], hmax[2]))
    # 5 empalmes
    emp = []
    for c, r in ram.items():
        fin = r["nudos"][-1]
        if fin in DS.DESCARGAS: continue
        cf_llega = r["perfil"][-1][2]
        for c2, r2 in ram.items():
            if c2 != c and fin in r2["nudos"][1:]:
                acc = 0.0; s_n = None
                for t in r2["tramos"]:
                    acc += t["L"]
                    if t["a"] == fin: s_n = acc
                cf_rec = min(r2["perfil"], key=lambda p: abs(p[0] - s_n))[2]
                emp.append((c, c2, nom[fin], cf_llega, cf_rec, cf_llega - cf_rec))
    mal = [e for e in emp if e[5] < -0.005]
    ok(5, "Empalmes: la cuneta que llega no queda por debajo de la que recibe", "CUMPLE" if not mal else "NO CUMPLE",
       "%d empalmes; caida maxima %.2f m (%s en %s)" % (len(emp), max(e[5] for e in emp), max(emp, key=lambda e: e[5])[0],
                                                       max(emp, key=lambda e: e[5])[2]) if not mal else str(mal))
    # 6 descargas por el cerco: el terreno exterior no queda sobre la cota de fondo (no hay que excavar fuera del cerco)
    #   y baja por debajo de ella a pocos metros (el agua se aleja sola por la pendiente natural)
    desc = []
    for D in sorted(DS.DESCARGAS):
        rr = [r for r in ram.values() if r["nudos"][-1] == D]
        cf = min(r["perfil"][-1][2] for r in rr); x, y = N[D]
        a = N[rr[0]["nudos"][-2]]; Lg = math.dist(a, (x, y)); u = ((x - a[0]) / Lg, (y - a[1]) / Lg)
        if D in DIR_EXT: u = DIR_EXT[D]
        perfil_ext = []
        for k in range(1, 61):
            d = 0.25 * k; zt = z(x + u[0] * d, y + u[1] * d)
            if np.isfinite(zt): perfil_ext.append((d, zt))
        if D in DS.POZA:
            # poza de salida: rebalsa a nivel del fondo interior junto al cerco; afuera el fondo natural no sube y baja aguas abajo
            nivel = DS.rasante_fn()(*N[D + "n"])
            sube = max([zt - nivel for d, zt in perfil_ext if d <= 2.0] + [-9])
            baja = next((d for d, zt in perfil_ext if zt <= nivel - 0.25), None)
            ok6 = sube <= 0.05 and baja is not None
            desc.append({"D": D, "cf": round(cf, 3), "nivel_rebalse": round(nivel, 2), "terreno": round(z(x, y), 2), "sale_a_m": baja,
                         "corte_max": round(max(sube, 0), 2), "tipo": "poza", "estado": "SALE POR GRAVEDAD" if ok6 else "NO SALE",
                         "receptor": R["descargas"][D], "exterior": [[d, round(zt, 2)] for d, zt in perfil_ext[:60:4]]})
            continue
        sobre = max([zt - cf for d, zt in perfil_ext if d <= 1.0] + [-9])
        baja = next((d for d, zt in perfil_ext if zt <= cf - 0.05), None)
        ok6 = baja is not None and baja <= 2.0
        desc.append({"D": D, "cf": round(cf, 3), "terreno": round(z(x, y), 2), "sale_a_m": baja, "corte_max": round(max(sobre, 0), 2), "tipo": "pase",
                     "estado": "SALE POR GRAVEDAD" if ok6 else "NO SALE", "receptor": R["descargas"][D],
                     "exterior": [[d, round(zt, 2)] for d, zt in perfil_ext[:12]]})
    malas = [d for d in desc if d["estado"] != "SALE POR GRAVEDAD"]
    ok(6, "Descargas por el cerco: el agua sale por gravedad al terreno exterior sin obras fuera del cerco",
       "CUMPLE" if not malas else "NO CUMPLE",
       "; ".join("%s C.F. %.3f: %s" % (d["D"], d["cf"], (("poza de salida: rebalsa a %.2f (fondo de la hondonada); afuera el fondo no sube y baja 0.25 m a %.1f m" % (d["nivel_rebalse"], d["sale_a_m"]))
                                        if d.get("tipo") == "poza" else ("pase en el cimiento del cerco; el terreno exterior queda bajo la C.F. a %.1f m del cerco" % d["sale_a_m"]))
                                        if d["estado"] == "SALE POR GRAVEDAD" else ("el terreno exterior (curvas cada 0.50 m) baja bajo la C.F. a %.1f m" % d["sale_a_m"]
                                        if d["sale_a_m"] else "el terreno exterior queda %.2f m sobre la C.F. en los 10 m revisados" % d["corte_max"])) for d in desc))
    # 7 NPT
    pts, ras = [], []
    for c, r in ram.items():
        xy = [tuple(N[n]) for n in r["nudos"]]
        for p in r["perfil"]:
            s = p[0]; acc = 0.0
            for i in range(len(xy) - 1):
                L = math.dist(xy[i], xy[i + 1])
                if acc + L >= s - 1e-9:
                    t = (s - acc) / L if L else 0; pts.append((xy[i][0] + t * (xy[i + 1][0] - xy[i][0]), xy[i][1] + t * (xy[i + 1][1] - xy[i][1]))); ras.append(p[1]); break
                acc += L
    pts = np.array(pts); ras = np.array(ras)
    npt = []
    for l, s, x, y, zz, b in G["txt"]:
        if "NTN" in s and "NPT" in s and 354800 < x < 355000 and 9249770 < y < 9249890:
            try:
                ntn = float(s.split("NTN=")[1].replace("+", "").strip()); rel = float(s.split("NPT=")[1].split("\n")[0].replace("+", "").strip())
            except ValueError: continue
            if not Path(DS.CERCO).contains_point((x, y)): continue          # rotulos de areas exteriores al cerco
            dd = np.hypot(pts[:, 0] - x, pts[:, 1] - y); k = int(dd.argmin())
            if dd[k] < 5: npt.append((round(ntn + rel, 2), round(float(ras[k]), 2), round(float(dd[k]), 1)))
    # niveles del usuario (21-10-2026): pisos y pasadizos +184.65, borde de cuneta +184.65 (al ras), areas verdes +184.60
    altos = [float(r) for r in ras if r > DS.NPT + 0.005 and r < 900]
    pat = Path(DS.PATIO)
    altos += [float(r) for p, r in zip(pts, ras) if pat.contains_point(p) and r > DS.NIVEL_PATIO + 0.005]
    n_pat = sum(1 for p in pts if pat.contains_point(p))
    difer = sorted({n[0] for n in npt if abs(n[0] - DS.NPT) > 0.005 and abs(n[0] - DS.NIVEL_PATIO) > 0.005})
    ok(7, "Borde de la cuneta al ras del NPT (+%.2f) y 0.05 m sobre el area verde (+%.2f)" % (DS.NPT, DS.NIVEL_AV),
       "CUMPLE" if not altos else "NO CUMPLE",
       ("borde de cuneta +%.2f en la red dentro del cerco (NPT +%.2f, area verde +%.2f); junto al patio de maniobra (NTN +%.2f) "
        "borde al ras +%.2f en %d puntos" % (DS.RASANTE, DS.NPT, DS.NIVEL_AV, DS.NIVEL_PATIO, DS.RAS_PATIO, n_pat)
        + ("; rotulos del plano de arquitectura con otro nivel junto a cunetas: %s (se toma +%.2f segun el usuario)"
           % (", ".join("%.2f" % v for v in difer), DS.NPT) if difer else "")) if not altos else "borde sobre el NPT: %d puntos" % len(altos))
    # 8 y 9 capacidad y velocidad con el caudal de diseno
    cel = []; ce = Path(DS.CERCO)
    xs = np.arange(354805, 354985, 1.0) + 0.5; ys = np.arange(9249775, 9249890, 1.0) + 0.5
    XX, YY = np.meshgrid(xs, ys); P = np.c_[XX.ravel(), YY.ravel()]; P = P[ce.contains_points(P)]
    segs = []
    for c, r in ram.items():
        for j, t in enumerate(r["tramos"]):
            segs.append((c, j, N[t["de"]], N[t["a"]]))
    D2 = np.stack([seg_dist(P, a, b)[0] for c, j, a, b in segs], 1); asg = D2.argmin(1)
    # coeficiente de escorrentia de cada celda de 1 m2 segun su superficie (techo, area libre de concreto, estacionamiento o area verde)
    import shapely
    SUP = H.superficies(G, DS.CERCO, DS.PATIO)
    Ccel = np.full(len(P), H.C_SUP["verde"]); tipo = np.array(["verde"] * len(P), dtype=object)
    for k in ("estacionamiento", "pavimento", "techo"):
        m = shapely.contains_xy(SUP[k], P[:, 0], P[:, 1]); Ccel[m] = H.C_SUP[k]; tipo[m] = k
    area, areaC, area_eje = {}, {}, {}
    for k, (c, j, a, b) in enumerate(segs):
        sel = asg == k; area[(c, j)] = float(sel.sum()); areaC[(c, j)] = float(Ccel[sel].sum())
        e = area_eje.setdefault(c, {t: 0.0 for t in H.C_SUP})
        for t in H.C_SUP: e[t] += float((tipo[sel] == t).sum())
    acum = {}
    def total(c):
        """Area y area x C acumuladas al final de cada tramo (con los ejes que entregan aguas arriba)."""
        if c in acum: return acum[c]
        r = ram[c]; out = []; A = 0.0; AC = 0.0
        for j, t in enumerate(r["tramos"]):
            for c2, r2 in ram.items():
                if c2 != c and r2["nudos"][-1] == t["de"] and j > 0:
                    A += total(c2)[-1][0]; AC += total(c2)[-1][1]
            A += area[(c, j)]; AC += areaC[(c, j)]; out.append((A, AC))
        acum[c] = out; return out
    filas = []; peor_cap, peor_v = None, None
    inv = {v: k for k, v in nom.items()}
    hreq = json.load(open(DS.HREQ)) if os.path.exists(DS.HREQ) else {}
    for c, r in ram.items():
        Ac = total(c)
        for j, t in enumerate(r["tramos"]):
            Q = I_MMH * Ac[j][1] / 3.6e6 * FS               # metodo racional: Q = C I A FS / 3.6e6 (C ponderado del area de aporte)
            S = max(t["S"], DS.S0); y = yn(Q, S, N_CAP); yv = yn(Q, S, N_VEL); V = Q / (DS.B_INT * yv)
            hdisp = min(t["h_de"], t["h_a"]) - (DS.E_TAPA if t["L_tapado"] > 0 else 0.0); llen = y / hdisp   # en tapado, altura libre bajo la losa
            f = {"ramal": c, "de": nom[t["de"]], "a": nom[t["a"]], "A_m2": round(Ac[j][0], 0), "C": round(Ac[j][1] / Ac[j][0], 3), "Q_ls": round(1000 * Q, 1), "S": round(100 * S, 2),
                 "y": round(y, 3), "h": round(hdisp, 2), "borde_libre": round(hdisp - y, 3), "V": round(V, 2),
                 "cap": "CUMPLE" if hdisp - y >= DS.BL - 1e-3 else "NO CUMPLE", "vel": "CUMPLE" if V <= VMAX or t["a"] in DS.POZA else "GRADAS"}     # en la poza el agua se remansa
            filas.append(f)
            need = y + DS.BL + 0.005                        # profundidad que necesita el tramo por capacidad
            clave = "%s|%s|%s" % (c, t["de"], t["a"])
            if need > DS.HMIN and hdisp - y < DS.BL: hreq[clave] = round(max(need, hreq.get(clave, 0)), 3)
            if peor_cap is None or f["borde_libre"] < peor_cap["borde_libre"]: peor_cap = f
            if peor_v is None or f["V"] > peor_v["V"]: peor_v = f
    ncap = [f for f in filas if f["cap"] != "CUMPLE"]; nvel = [f for f in filas if f["vel"] != "CUMPLE"]
    Atot = sum(area.values()); Cpond = sum(areaC.values()) / Atot
    sup_area = {k: float((tipo == k).sum()) for k in H.C_SUP}
    ok(8, "Capacidad con el caudal de diseno (borde libre >= 0.05 m)", "CUMPLE" if not ncap else "NO CUMPLE",
       "I = %.0f mm/h, C ponderado = %.2f, area total %.0f m2; menor borde libre %.3f m en %s %s-%s (Q %.1f l/s, y %.3f, h %.2f)" % (
           I_MMH, Cpond, Atot, peor_cap["borde_libre"], peor_cap["ramal"], peor_cap["de"], peor_cap["a"], peor_cap["Q_ls"], peor_cap["y"], peor_cap["h"])
       + ("" if not ncap else "; no cumplen: " + ", ".join("%s %s-%s" % (f["ramal"], f["de"], f["a"]) for f in ncap)))
    ok(9, "Velocidad maxima 3.0 m/s (concreto)", "CUMPLE" if not nvel else "CUMPLE CON GRADAS",
       ("V max %.2f m/s" % peor_v["V"]) if not nvel else "tramos de fuerte pendiente con V > 3.0 m/s: " +
       ", ".join("%s %s-%s (S %.1f %%, V %.2f)" % (f["ramal"], f["de"], f["a"], f["S"], f["V"]) for f in nvel) + " -> gradas (escalones) de concreto")
    # 10 muros
    muros = []
    for capa in ("0_MUROS 1",):
        for pp, cl, b in G["geo"].get(capa, []):
            q = [(p[0], p[1]) for p in pp]
            for i in range(len(q) - 1 + (1 if cl else 0)):
                muros.append((q[i], q[(i + 1) % len(q)]))
    dmin = np.full(len(pts), 1e9)
    for a, b in muros:
        if math.dist(a, b) < 1e-6: continue
        dmin = np.minimum(dmin, seg_dist(pts, a, b)[0])
    cerca = int((dmin < DS.B_TOT / 2).sum())
    ok(10, "El eje no corta muros de los bloques (>= 0.30 m)", "CUMPLE" if cerca == 0 else "REVISAR",
       "distancia minima eje-muro %.2f m en %d puntos revisados" % (float(dmin.min()), len(pts)) if cerca == 0 else
       "%d puntos a menos de 0.30 m de un muro (min %.2f m)" % (cerca, float(dmin.min())))
    # 11 dentro del cerco: los bordes de la cuneta (eje +- 0.30) quedan dentro del cerco, salvo el paso por el cerco (Dn -> D)
    ce = Path(DS.CERCO); fuera = []
    for c, r in ram.items():
        xy = [tuple(N[n]) for n in r["nudos"]]
        for i in range(len(xy) - 1):
            if r["nudos"][i + 1] in DS.DESCARGAS: continue
            a, b = xy[i], xy[i + 1]; L = math.dist(a, b); u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
            for k in range(int(L / 0.25) + 1):
                t = min(L, k * 0.25); p = (a[0] + u[0] * t, a[1] + u[1] * t)
                for sg in (-1, 1):
                    q = (p[0] - u[1] * 0.30 * sg, p[1] + u[0] * 0.30 * sg)
                    if not ce.contains_point(q): fuera.append((c, round(q[0], 2), round(q[1], 2))); break
    ok(11, "Toda la red dentro del cerco perimetrico (limite de intervencion)", "CUMPLE" if not fuera else "NO CUMPLE",
       "ningun borde de cuneta pasa el cerco; solo las %d salidas lo atraviesan" % len(DS.DESCARGAS) if not fuera else "%d puntos fuera: %s" % (len(fuera), fuera[:5]))
    json.dump(hreq, open(DS.HREQ, "w"), indent=1)
    out = {"comprobaciones": res, "descargas": desc, "hidraulica": filas, "empalmes": emp,
           "hidrologia": {"C": round(Cpond, 3), "I": round(I_MMH, 2), "tc": TC, "P10": round(P10, 2), "P24": round(HID["P24"], 2),
                          "T": HID["T"], "factor": round(HID["factor"], 4), "n_cap": N_CAP, "n_vel": N_VEL, "A_total": Atot,
                          "superficies": {k: {"A": v, "C": H.C_SUP[k]} for k, v in sup_area.items()}, "FS": FS,
                          "detalle_superficies": [{"tipo": t, "zona": z, "A": round(a, 1)} for t, z, a in SUP["detalle"]], "areas_eje": area_eje}}
    json.dump(out, open(os.path.join(CALC, "verificacion.json"), "w"), indent=1, ensure_ascii=False)
    for c in res: print("%2d %-75s %s\n     %s" % (c["n"], c["comprobacion"], c["estado"], c["detalle"]))




def solo_lluvia():
    """Cambio de lluvia: rehace capacidad (8) y velocidad (9) sobre la geometria vigente; Q nuevo = Q anterior x I nuevo / I anterior."""
    hreq = json.load(open(DS.HREQ)) if os.path.exists(DS.HREQ) else {}
    if hreq: raise SystemExit("hmin_req.json no esta vacio: hay profundidades fijadas por capacidad; correr calcula_b.py con la base del sitio")
    ruta = os.path.join(CALC, "verificacion.json"); out = json.load(open(ruta, encoding="utf-8"))
    hv = out["hidrologia"]; k = I_MMH / hv["I"]; filas = []; peor_cap = peor_v = None
    for f0 in out["hidraulica"]:
        Q = f0["Q_ls"] / 1000.0 * k; S = f0["S"] / 100.0; hdisp = f0["h"]
        y = yn(Q, S, N_CAP); yv = yn(Q, S, N_VEL); V = Q / (DS.B_INT * yv)
        f = dict(f0, Q_ls=round(1000 * Q, 1), y=round(y, 3), borde_libre=round(hdisp - y, 3), V=round(V, 2),
                 cap="CUMPLE" if hdisp - y >= DS.BL - 1e-3 else "NO CUMPLE", vel="CUMPLE" if V <= VMAX else "GRADAS")
        filas.append(f)
        if peor_cap is None or f["borde_libre"] < peor_cap["borde_libre"]: peor_cap = f
        if peor_v is None or f["V"] > peor_v["V"]: peor_v = f
    ncap = [f for f in filas if f["cap"] != "CUMPLE"]; nvel = [f for f in filas if f["vel"] != "CUMPLE"]
    for c in out["comprobaciones"]:
        if c["n"] == 8:
            c["estado"] = "CUMPLE" if not ncap else "NO CUMPLE"
            c["detalle"] = ("I = %.0f mm/h, C ponderado = %.2f, area total %.0f m2; menor borde libre %.3f m en %s %s-%s (Q %.1f l/s, y %.3f, h %.2f)" % (
                I_MMH, hv["C"], hv["A_total"], peor_cap["borde_libre"], peor_cap["ramal"], peor_cap["de"], peor_cap["a"], peor_cap["Q_ls"],
                peor_cap["y"], peor_cap["h"]) + ("" if not ncap else "; no cumplen: " + ", ".join("%s %s-%s" % (f["ramal"], f["de"], f["a"]) for f in ncap)))
        if c["n"] == 9:
            c["estado"] = "CUMPLE" if not nvel else "CUMPLE CON GRADAS"
            c["detalle"] = ("V max %.2f m/s" % peor_v["V"]) if not nvel else "tramos con V > 3.0 m/s: " + ", ".join(
                "%s %s-%s (S %.1f %%, V %.2f)" % (f["ramal"], f["de"], f["a"], f["S"], f["V"]) for f in nvel)
    out["hidraulica"] = filas
    hv.update({"I": round(I_MMH, 2), "P10": round(P10, 2), "P24": round(HID["P24"], 2), "T": HID["T"], "factor": round(HID["factor"], 4)})
    json.dump(out, open(ruta, "w"), indent=1, ensure_ascii=False)
    for c in out["comprobaciones"]: print("%2d %-75s %s\n     %s" % (c["n"], c["comprobacion"], c["estado"], c["detalle"]))


if __name__ == "__main__":
    solo_lluvia() if "--solo-lluvia" in sys.argv else main()
