"""Cotas de fondo de la red (muestreo cada 0.50 m).

- Borde de la cuneta = rasante del sitio (al ras del piso; zonas con su propio nivel; fuera del cerco, el terreno).
- Al inicio de cada eje h = 0.30 m (mas la losa si arranca tapado); la cota de fondo baja al menos 0.5 % y la altura libre no
  baja de 0.25 m (o de la que pida la capacidad del tramo, ciclo con la verificacion).
- En el pase por el cerco la cuneta llega con su mismo borde (no baja al terreno exterior).
- Empalmes: la cuneta que llega no queda bajo la que recibe; si el empalme obliga a bajar, el fondo baja parejo desde el nudo
  anterior (sin escalon).
- Cambios de nivel del piso (plataformas): hasta 0.15 m la cuneta sigue continua y el desnivel se absorbe en la pendiente de los
  3 m anteriores; con mas desnivel el fondo cae en el cambio y queda una estructura (caida corta, caja de caida o pase por el
  muro de contencion con poza; estructuras.py). Si el piso sube, la cuneta queda mas profunda (se avisa).
"""
import math

from matplotlib.path import Path
from shapely.geometry import Point


def _base(n): return n.split("~")[0]


def calcular(red, sitio, P, hq=None):
    hq = hq or {}
    N, nom, D = red.Nf, red.nombre, red.descargas
    geo = {}
    for r in red.ramales:
        cod, nudos = r["codigo"], r["nudos"]
        pts = []
        for i in range(len(nudos) - 1):
            a, b = N[nudos[i]], N[nudos[i + 1]]; L = math.dist(a, b); n = max(1, int(math.ceil(L / P["paso"])))
            for k in range(n + (1 if i == len(nudos) - 2 else 0)):
                t = k / n
                pts.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]), nudos[i] if k == 0 else (nudos[i + 1] if k == n else None)))
        s = [0.0]
        for i in range(1, len(pts)): s.append(s[-1] + math.dist(pts[i - 1][:2], pts[i][:2]))
        rr = [sitio.rasante(p[0], p[1]) for p in pts]
        idx = [i for i, p in enumerate(pts) if p[2]]
        # uniones nuevas: rasante recta entre sus extremos (relleno compactado)
        for i0, i1 in zip(idx[:-1], idx[1:]):
            o = red.origen_arista.get((_base(pts[i0][2]), _base(pts[i1][2])), "usuario")
            if o == "union" and s[i1] > s[i0]:
                for i in range(i0 + 1, i1): rr[i] = rr[i0] + (rr[i1] - rr[i0]) * (s[i] - s[i0]) / (s[i1] - s[i0])
        tap = [sitio.tapado(p[0], p[1]) for p in pts]
        # un pedazo tapado de menos de 0.40 m (la cuneta apenas toca una vereda) no se toma como tapado, igual que en los planos
        i = 0
        while i < len(pts):
            if tap[i]:
                j = i
                while j + 1 < len(pts) and tap[j + 1]: j += 1
                if s[j] - s[i] <= 0.4:
                    for k in range(i, j + 1): tap[k] = False
                i = j + 1
            else: i += 1
        if nudos[-1] in D:                                     # pase por el cerco: mismo borde y tapado
            idn = idx[-2]
            for i in range(idn + 1, len(pts)): rr[i] = rr[idn]; tap[i] = tap[i] or 1
            tap[idn] = tap[idn] or 1
        geo[cod] = (pts, s, rr, tap)
    req = {}
    for it in range(60):
        fondo, cambio = {}, False
        for r in red.ramales:
            cod, nudos = r["codigo"], r["nudos"]
            pts, s, rr, tap = geo[cod]; f = []
            hm = []; j = -1
            for i, p in enumerate(pts):
                if p[2] and i < len(pts) - 1: j += 1
                rq = hq.get("%s|%s|%s" % (cod, nom[nudos[j]], nom[nudos[j + 1]]), P["hmin"])
                if p[2] and 0 < i and j > 0: rq = max(rq, hq.get("%s|%s|%s" % (cod, nom[nudos[j - 1]], nom[nudos[j]]), P["hmin"]))
                hm.append(max(P["hmin"], rq) + (P.get("e_tapa_veh", P["e_tapa"]) if tap[i] == 2 else P["e_tapa"] if tap[i] else 0.0))
            for i, p in enumerate(pts):
                if i == 0: v = rr[0] - max(P["h0"] + (P.get("e_tapa_veh", P["e_tapa"]) if tap[0] == 2 else P["e_tapa"] if tap[0] else 0.0), hm[0])   # 0.30 al inicio
                else: v = min(f[-1] - P["S0"] * (s[i] - s[i - 1]), rr[i] - hm[i])
                if p[2] and 0 < i < len(pts) - 1 and p[2] in req: v = min(v, req[p[2]])   # solo el eje que recibe; el que llega cae libre
                f.append(v)
            # desnivel chico del piso (<= 0.15 m): el fondo no hace escalon, baja parejo antes del cambio con pendiente de 1.5 %
            # (entre 3 y 15 m), para no subir la velocidad
            # (tambien el engrosamiento de la losa al entrar a un estacionamiento: tapa vehicular)
            for i in range(1, len(pts)):
                d = rr[i - 1] - rr[i]; caida = f[i - 1] - f[i] - P["S0"] * (s[i] - s[i - 1])
                losa = tap[i] == 2 and tap[i - 1] != 2
                if (0.005 < d <= P["caida_continua_max"] + 1e-9 or (losa and d <= P["caida_continua_max"] + 1e-9)) and caida > 0.005:
                    La = min(max(P["caida_absorbe_L"], caida / P.get("caida_absorbe_S", 0.015)), 15.0)
                    k0 = i - 1
                    while k0 > 0 and s[i] - s[k0 - 1] <= La: k0 -= 1
                    if k0 >= i - 1: continue
                    pend = (f[k0] - f[i]) / (s[i] - s[k0])            # recta que empalma con el perfil al inicio de la zona
                    for k in range(k0 + 1, i): f[k] = min(f[k], f[i] + (s[i] - s[k]) * pend)
            nod = [i for i, p in enumerate(pts) if p[2]]
            for m in range(1, len(nod)):
                k1 = nod[m]
                # la bajada pareja empieza en el quiebre real anterior (no en un punto de chaflan)
                k0 = next((nod[q] for q in range(m - 1, -1, -1) if "~" not in pts[nod[q]][2] or q == 0), nod[m - 1])
                if pts[k1][2] in req and f[k1] < f[k1 - 1] - P["S0"] * (s[k1] - s[k1 - 1]) * 1.5:
                    for i in range(k0 + 1, k1):
                        f[i] = min(f[i], f[k0] + (f[k1] - f[k0]) * (s[i] - s[k0]) / (s[k1] - s[k0]))
            # ninguna bajada del fondo mas fuerte que S_max (fuera de las estructuras de caida): si hay que profundizar, se empieza
            # antes (sin escalones que suban la velocidad)
            smax = P.get("S_max_fondo", 0.02)
            for i in range(len(pts) - 1, 0, -1):
                if rr[i - 1] - rr[i] > P["caida_continua_max"]: continue
                f[i - 1] = min(f[i - 1], f[i] + smax * (s[i] - s[i - 1]) + max(0.0, rr[i - 1] - rr[i]))
            fondo[cod] = f
        for r in red.ramales:
            cod, fin = r["codigo"], r["nudos"][-1]; v = fondo[cod][-1]
            for r2 in red.ramales:
                if r2["codigo"] != cod and fin in r2["nudos"][1:-1]:
                    k = [i for i, p in enumerate(geo[r2["codigo"]][0]) if p[2] == fin][0]
                    if fondo[r2["codigo"]][k] > v + 1e-6:
                        req[fin] = min(req.get(fin, 9e9), v); cambio = True
        if not cambio: break
    res = {"nudos": {nom[k]: [round(v[0], 3), round(v[1], 3)] for k, v in N.items() if k in nom}, "ramales": []}
    for r in red.ramales:
        cod = r["codigo"]; pts, s, rr, tap = geo[cod]; f = fondo[cod]
        idx = [i for i, p in enumerate(pts) if p[2]]; tramos = []
        for i0, i1 in zip(idx[:-1], idx[1:]):
            L = s[i1] - s[i0]
            ltap = sum(s[i + 1] - s[i] for i in range(i0, i1) if tap[i] and tap[i + 1])
            lveh = sum(s[i + 1] - s[i] for i in range(i0, i1) if tap[i] == 2 and tap[i + 1] == 2)
            # caidas en los cambios de plataforma: no cuentan en la pendiente del canal (la estructura las toma)
            cai = sum(max(0.0, f[i - 1] - f[i] - P["S0"] * (s[i] - s[i - 1])) for i in range(i0 + 1, i1 + 1)
                      if rr[i - 1] - rr[i] > P["caida_continua_max"])
            S = (f[i0] - f[i1] - cai) / L if L > 0 else 0.0
            o = red.origen_arista.get((_base(pts[i0][2]), _base(pts[i1][2])), "usuario")
            if pts[i1][2] in D: o = "pase"
            tramos.append({"de": nom[pts[i0][2]], "a": nom[pts[i1][2]], "L": round(L, 2), "ras_de": round(rr[i0], 3), "ras_a": round(rr[i1], 3),
                           "cf_de": round(f[i0], 3), "cf_a": round(f[i1], 3), "h_de": round(rr[i0] - f[i0], 3), "h_a": round(rr[i1] - f[i1], 3),
                           "S": round(S, 5), "h_max": round(max(rr[i] - f[i] for i in range(i0, i1 + 1)), 3),
                           "L_tapado": round(ltap, 2), "L_rejilla": round(L - ltap, 2), "origen": o, "caidas": round(cai, 3), "L_vehicular": round(lveh, 2)})
        tiv = []; i = 0
        while i < len(pts):
            if tap[i]:
                j = i
                while j + 1 < len(pts) and tap[j + 1]: j += 1
                if s[j] - s[i] > 0.4: tiv.append([round(s[i], 2), round(s[j], 2)])
                i = j + 1
            else: i += 1
        viv = []; i = 0                                    # tramos con tapa vehicular (estacionamientos)
        while i < len(pts):
            if tap[i] == 2:
                j = i
                while j + 1 < len(pts) and tap[j + 1] == 2: j += 1
                if s[j] - s[i] > 0.4: viv.append([round(s[i], 2), round(s[j], 2)])
                i = j + 1
            else: i += 1
        cambios = []
        for i in range(1, len(pts)):
            d = rr[i - 1] - rr[i]
            # solo los cambios bruscos (borde de plataforma); una rampa cambia poco a poco y la cuneta la sigue
            if abs(d) <= 0.07 or (pts[i][2] in D): continue
            k = max(j for j, q in enumerate(idx) if q <= i - 1) if idx else 0
            cambios.append({"s": round(s[i], 2), "x": round(pts[i][0], 3), "y": round(pts[i][1], 3), "borde_arriba": round(rr[i - 1], 3),
                            "borde_abajo": round(rr[i], 3), "desnivel": round(d, 3), "cf_arriba": round(f[i - 1], 3), "cf_abajo": round(f[i], 3),
                            "caida_fondo": round(f[i - 1] - f[i], 3), "tramo": k, "sentido": "baja" if d > 0 else "sube",
                            "nivel_arriba": sitio.nivel_en(*pts[i - 1][:2]) if hasattr(sitio, "nivel_en") else "",
                            "nivel_abajo": sitio.nivel_en(*pts[i][:2]) if hasattr(sitio, "nivel_en") else ""})
        res["ramales"].append({"codigo": cod, "sistema": r["sistema"], "descarga": r["descarga"], "nudos": [nom[n] for n in r["nudos"]],
                               "L": round(s[-1], 2), "tramos": tramos, "tapados": tiv, "vehiculares": viv, "cambios_nivel": cambios,
                               "perfil": [[round(s[i], 2), round(rr[i], 3), round(f[i], 3)] for i in range(len(pts))]})
    return res
