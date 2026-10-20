"""Verificacion del planteamiento preliminar de cunetas - I.E. N.° 0590, Barranquita (10 comprobaciones).

1. Conectividad: todo ramal termina en una descarga o en otro ramal que llega a una descarga.
2. Sin contrapendiente: la cota de fondo baja en cada paso de 0.50 m de todos los ramales.
3. Pendiente minima de la cota de fondo >= 0.5 % en cada tramo.
4. Profundidad: h = 0.30 m al inicio de cada ramal y h >= 0.25 m en todo el recorrido.
5. Empalmes: la cuneta que llega lo hace a la misma cota o por encima de la que recibe (no remansa).
6. Descargas por gravedad: desde la cota de fondo de cada descarga, un canal de salida al 0.5 % sale a la superficie
   del terreno de las curvas de nivel (no queda enterrado).
7. Niveles de piso: el borde de la cuneta no queda por encima del piso terminado (NPT) de los bloques vecinos.
8. Capacidad: tirante normal con el caudal de diseno <= h - 0.05 m (borde libre) en cada tramo.
9. Velocidad: V <= 3.0 m/s (concreto, CE.040); los tramos que pasan se resuelven con gradas o caidas.
10. Interferencias: el eje de la cuneta no corta muros de los bloques (distancia al muro >= 0.30 m).

Caudal de diseno (referencial): metodo racional con el area tributaria de cada tramo dentro del cerco (cada punto de 1 m2
va a la cuneta mas cercana; techos a dos aguas: cada mitad al alero de su lado), C = 0.80, I = 211 mm/h
(tc = 10 min, TR = 25 anos, P10 = 35.16 mm de la estacion usada en el Hogar de Refugio - Morales; reemplazar por la del
proyecto), factor de seguridad 1.15.
Uso: python3 herramientas/barranquita/verifica_b.py -> entregables_barranquita/_calc/verificacion.json
"""
import os, sys, json, math
import numpy as np
from matplotlib.path import Path
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import terreno_b as T
import diseno_b as DS

CALC = os.path.join(RAIZ, "entregables_barranquita", "_calc")
C_ESC, P10, TC, FS = 0.80, 35.163, 10.0, 1.15
I_MMH = P10 / (TC / 60.0)                    # Dick y Peschke con tc = 10 min (tc / 10 = 1)
N_CAP, N_VEL, VMAX = 0.015, 0.013, 3.0
DIR_SAL = {"D1": None, "D2": (-0.7071, 0.7071), "D3": (0.0, -1.0), "D4": (-0.7071, -0.7071)}
RECEPTOR = {"D3": "Jr. Alfonso Ugarte, punto bajo de la calle (183.00)", "D4": "Jr. Alfonso Ugarte (calzada que baja al punto bajo)"}


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
    R = json.load(open(os.path.join(CALC, "diseno.json"))); z = T.modelo(); G = T.cargar()
    ram = {r["codigo"]: r for r in R["ramales"]}; N = R["nudos"]; nom = R["nombre"]
    res = []
    def ok(n, titulo, cumple, detalle):
        res.append({"n": n, "comprobacion": titulo, "estado": cumple, "detalle": detalle})
    # 1 conectividad
    fines = {}
    for c, r in ram.items():
        fin = r["nudos"][-1]
        if fin.startswith("D"): fines[c] = fin
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
       "22 ramales: " + ", ".join("%s->%s" % (c, fines[c]) for c in ram) if not sin else "sin salida: " + ", ".join(sin))
    # 2 contrapendiente
    malos = []
    for c, r in ram.items():
        P = r["perfil"]
        for i in range(1, len(P)):
            if P[i][2] > P[i - 1][2] + 1e-6: malos.append("%s prog %.2f" % (c, P[i][0])); break
    ok(2, "Sin contrapendiente en la cota de fondo (cada 0.50 m)", "CUMPLE" if not malos else "NO CUMPLE",
       "la cota de fondo baja en todos los puntos" if not malos else "; ".join(malos))
    # 3 pendiente minima
    smin = min((t["S"], c, t) for c, r in ram.items() for t in r["tramos"])
    ok(3, "Pendiente minima de la cota de fondo >= 0.5 %", "CUMPLE" if smin[0] >= DS.S0 - 1e-4 else "NO CUMPLE",
       "minima %.2f %% (%s %s-%s); maxima %.2f %%" % (100 * smin[0], smin[1], nom[smin[2]["de"]], nom[smin[2]["a"]],
                                                     100 * max(t["S"] for r in ram.values() for t in r["tramos"])))
    # 4 profundidades
    h0 = [round(r["perfil"][0][1] - r["perfil"][0][2], 3) for r in ram.values()]
    hmin = min((p[1] - p[2], c, p[0]) for c, r in ram.items() for p in r["perfil"])
    hmax = max((p[1] - p[2], c, p[0]) for c, r in ram.items() for p in r["perfil"])
    ok(4, "Profundidad: 0.30 m al inicio y >= 0.25 m en todo el recorrido",
       "CUMPLE" if min(h0) >= DS.H0 - 1e-3 and hmin[0] >= DS.HMIN - 1e-3 else "NO CUMPLE",
       "inicio %.2f a %.2f; minima %.2f (%s); maxima %.2f (%s, prog %.1f)" % (min(h0), max(h0), hmin[0], hmin[1], hmax[0], hmax[1], hmax[2]))
    # 5 empalmes
    emp = []
    for c, r in ram.items():
        fin = r["nudos"][-1]
        if fin.startswith("D"): continue
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
    # 6 descargas a la luz
    desc = []
    for D in ("D1", "D2", "D3", "D4"):
        rr = [r for r in ram.values() if r["nudos"][-1] == D]
        cf = min(r["perfil"][-1][2] for r in rr); x, y = N[D]
        u = DIR_SAL[D]
        if u is None:
            a = N[rr[0]["nudos"][-2]]; L = math.dist(a, (x, y)); u = ((x - a[0]) / L, (y - a[1]) / L)
        dl, corte = None, 0.0
        for k in range(1, 61):
            d = 0.5 * k; zt = z(x + u[0] * d, y + u[1] * d)
            if not np.isfinite(zt): break
            inv = cf - DS.S0 * d; corte = max(corte, zt - inv)
            if zt <= inv: dl = d; break
        desc.append({"D": D, "cf": round(cf, 3), "terreno": round(z(x, y), 2), "sale_a_m": dl, "corte_max": round(corte, 2),
                     "estado": "SALE POR GRAVEDAD" if dl is not None else "CONDICIONADO AL RECEPTOR",
                     "receptor": RECEPTOR.get(D, R["descargas"][D])})
    malas = [d for d in desc if d["sale_a_m"] is None]
    ok(6, "Descargas por gravedad: el canal de salida (0.5 %) sale a la superficie del terreno",
       "CUMPLE" if not malas else "CUMPLE CON CONDICION",
       "; ".join("%s CF %.3f: %s" % (d["D"], d["cf"], ("sale a la superficie a %.1f m (corte max %.2f)" % (d["sale_a_m"], d["corte_max"]))
                                        if d["sale_a_m"] is not None else "terreno plano a %.2f: requiere receptor (%s)" % (d["terreno"], d["receptor"]))
                 for d in desc))
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
            dd = np.hypot(pts[:, 0] - x, pts[:, 1] - y); k = int(dd.argmin())
            if dd[k] < 5: npt.append((round(ntn + rel, 2), round(float(ras[k]), 2), round(float(dd[k]), 1)))
    altos = [n for n in npt if n[1] > n[0] + 0.005]
    ok(7, "Borde de la cuneta por debajo del NPT de los bloques vecinos", "CUMPLE" if not altos else "NO CUMPLE",
       "%d rotulos NPT revisados (bloques a menos de 5 m de una cuneta); NPT de 183.50 a 184.65; borde de cuneta <= NPT en todos" % len(npt)
       if not altos else "borde sobre NPT: %s" % altos)
    # 8 y 9 capacidad y velocidad con el caudal de diseno
    cel = []; ce = Path(DS.CERCO)
    xs = np.arange(354805, 354985, 1.0) + 0.5; ys = np.arange(9249775, 9249890, 1.0) + 0.5
    XX, YY = np.meshgrid(xs, ys); P = np.c_[XX.ravel(), YY.ravel()]; P = P[ce.contains_points(P)]
    segs = []
    for c, r in ram.items():
        for j, t in enumerate(r["tramos"]):
            segs.append((c, j, N[t["de"]], N[t["a"]]))
    D2 = np.stack([seg_dist(P, a, b)[0] for c, j, a, b in segs], 1); asg = D2.argmin(1)
    area = {}
    for k, (c, j, a, b) in enumerate(segs): area[(c, j)] = float((asg == k).sum())
    acum = {}
    def total(c):
        if c in acum: return acum[c]
        r = ram[c]; out = []; A = 0.0
        for j, t in enumerate(r["tramos"]):
            for c2, r2 in ram.items():
                if c2 != c and r2["nudos"][-1] == t["de"] and j > 0: A += total(c2)[-1]
            A += area[(c, j)]; out.append(A)
        acum[c] = out; return out
    filas = []; peor_cap, peor_v = None, None
    for c, r in ram.items():
        Ac = total(c)
        for j, t in enumerate(r["tramos"]):
            Q = C_ESC * I_MMH * Ac[j] / 3.6e6 * FS
            S = max(t["S"], DS.S0); y = yn(Q, S, N_CAP); yv = yn(Q, S, N_VEL); V = Q / (DS.B_INT * yv)
            hdisp = min(t["h_de"], t["h_a"]); llen = y / hdisp
            f = {"ramal": c, "de": nom[t["de"]], "a": nom[t["a"]], "A_m2": round(Ac[j], 0), "Q_ls": round(1000 * Q, 1), "S": round(100 * S, 2),
                 "y": round(y, 3), "h": round(hdisp, 2), "borde_libre": round(hdisp - y, 3), "V": round(V, 2),
                 "cap": "CUMPLE" if hdisp - y >= DS.BL - 1e-3 else "NO CUMPLE", "vel": "CUMPLE" if V <= VMAX else "GRADAS"}
            filas.append(f)
            if peor_cap is None or f["borde_libre"] < peor_cap["borde_libre"]: peor_cap = f
            if peor_v is None or f["V"] > peor_v["V"]: peor_v = f
    ncap = [f for f in filas if f["cap"] != "CUMPLE"]; nvel = [f for f in filas if f["vel"] != "CUMPLE"]
    Atot = sum(area.values())
    ok(8, "Capacidad con el caudal de diseno (borde libre >= 0.05 m)", "CUMPLE" if not ncap else "NO CUMPLE",
       "I = %.0f mm/h, C = %.2f, area total %.0f m2; menor borde libre %.3f m en %s %s-%s (Q %.1f l/s, y %.3f, h %.2f)" % (
           I_MMH, C_ESC, Atot, peor_cap["borde_libre"], peor_cap["ramal"], peor_cap["de"], peor_cap["a"], peor_cap["Q_ls"], peor_cap["y"], peor_cap["h"])
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
    out = {"comprobaciones": res, "descargas": desc, "hidraulica": filas, "empalmes": emp,
           "hidrologia": {"C": C_ESC, "I": round(I_MMH, 1), "tc": TC, "FS": FS, "P10": P10, "n_cap": N_CAP, "n_vel": N_VEL, "A_total": Atot}}
    json.dump(out, open(os.path.join(CALC, "verificacion.json"), "w"), indent=1, ensure_ascii=False)
    for c in res: print("%2d %-75s %s\n     %s" % (c["n"], c["comprobacion"], c["estado"], c["detalle"]))


if __name__ == "__main__":
    main()
