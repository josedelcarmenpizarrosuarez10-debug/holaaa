"""Perfil de flujo de cada eje por el método del paso estándar (flujo gradualmente variado, Chow, cap. 10).

La verificación por tramo usa el tirante normal; aquí se calcula el nivel del agua real a lo largo de cada eje, con los
remansos de las uniones y las caídas:
- régimen subcrítico: se avanza aguas arriba desde el control de aguas abajo; régimen supercrítico: aguas abajo desde el
  control de aguas arriba (tirante crítico). En cada estación queda el de mayor fuerza específica (régimen mixto); el paso
  de supercrítico a subcrítico es un resalto hidráulico.
- controles: en una descarga libre por el cerco, el tirante crítico; en la unión con otra cuneta, el nivel del agua de la
  cuneta que recibe (si queda bajo el fondo, el crítico); en el borde de una caída, el crítico (o el nivel de aguas abajo
  si la ahoga).
- energía: z + y + V²/2g; pérdida por fricción hf = Δx·(Sf1 + Sf2)/2 con Sf = (n·V / R^(2/3))², n de capacidad.
- el caudal crece a lo largo de cada tramo, igual que en la verificación: del que entra al tramo (el del tramo anterior más
  el de los ejes que llegan a su nudo inicial) al de diseño de su final.
"""
import math

G = 9.81


def _geo(Q, b, y, n):
    A = b * y; Pm = b + 2 * y; R = A / Pm; V = Q / A
    return A, V, (n * V / R ** (2.0 / 3.0)) ** 2


def critico(Q, b):
    return (Q * Q / (G * b * b)) ** (1.0 / 3.0) if Q > 0 else 0.0


def fuerza(Q, b, y):
    return Q * Q / (G * b * y) + b * y * y / 2.0


def _biseccion(f, lo, hi, it=60):
    for _ in range(it):
        m = (lo + hi) / 2
        if f(m) > 0: hi = m
        else: lo = m
    return (lo + hi) / 2


def _estaciones(r, fila, P, entra):
    """Estaciones del perfil del eje: s, cota de fondo, rasante, altura libre disponible, caudal y ancho del tramo.
    El caudal crece a lo largo de cada tramo, como en la verificación: del que entra (el del tramo anterior más el de los ejes
    que llegan a su nudo inicial, entra[nudo] en m³/s) al de diseño de su final."""
    lim = []; s0 = 0.0; q_ant = 0.0
    for t in r["tramos"]:
        f = fila.get((r["codigo"], t["de"], t["a"])) or {}
        q1 = f.get("Q_ls", 0.0) / 1000.0; q0 = min(q1, q_ant + entra.get(t["de"], 0.0))
        lim.append((s0, s0 + t["L"], q0, q1, f.get("b", P["b_int"]))); s0 += t["L"]; q_ant = q1
    tap = r.get("tapados", []); veh = r.get("vehiculares", [])
    est = []
    for s, ras, cf in r["perfil"]:
        x = next((x for x in lim if x[0] - 1e-6 <= s <= x[1] + 1e-6), lim[-1])
        k = min(1.0, max(0.0, (s - x[0]) / (x[1] - x[0]))) if x[1] > x[0] else 1.0
        q, b = x[2] + (x[3] - x[2]) * k, x[4]
        losa = (P.get("e_tapa_veh", P["e_tapa"]) if any(a <= s <= c for a, c in veh) else P["e_tapa"] if any(a <= s <= c for a, c in tap) else 0.0)
        est.append({"s": s, "z": cf, "ras": ras, "h": ras - cf - losa, "tapado": losa > 0, "Q": max(q, 1e-5), "b": b})
    return est


def _es_caida(a, b):
    dz = a["z"] - b["z"]; ds = max(b["s"] - a["s"], 1e-6)
    return dz > 0.05 and dz / ds > 0.10


def perfil_eje(est, y_fin, n):
    """Tirantes por el paso estándar en régimen mixto. y_fin: tirante en el extremo de aguas abajo (ya con su control)."""
    N = len(est)
    yc = [critico(e["Q"], e["b"]) for e in est]
    H = lambda i, y: est[i]["z"] + y + _geo(est[i]["Q"], est[i]["b"], y, n)[1] ** 2 / (2 * G)
    Sf = lambda i, y: _geo(est[i]["Q"], est[i]["b"], y, n)[2]
    # subcrítico: de aguas abajo hacia aguas arriba
    ysub = [0.0] * N; ysub[-1] = max(y_fin, yc[-1])
    for i in range(N - 2, -1, -1):
        if _es_caida(est[i], est[i + 1]):
            ysub[i] = max(yc[i], est[i + 1]["z"] + ysub[i + 1] - est[i]["z"]); continue
        dx = est[i + 1]["s"] - est[i]["s"]; Hd = H(i + 1, ysub[i + 1]); sd = Sf(i + 1, ysub[i + 1])
        f = lambda y: H(i, y) - Hd - dx * (Sf(i, y) + sd) / 2
        if f(yc[i]) >= 0: ysub[i] = yc[i]; continue                     # no hay solución subcrítica: control crítico
        hi = max(Hd - est[i]["z"], yc[i]) + 1.0
        while f(hi) < 0: hi += 1.0
        ysub[i] = _biseccion(f, yc[i], hi)
    # supercrítico: de aguas arriba hacia aguas abajo, desde el crítico
    ysup = [0.0] * N; ysup[0] = yc[0]
    for i in range(N - 1):
        if _es_caida(est[i], est[i + 1]): ysup[i + 1] = yc[i + 1]; continue  # la poza disipa; sale por el umbral en crítico
        dx = est[i + 1]["s"] - est[i]["s"]; Hu = H(i, ysup[i]); su = Sf(i, ysup[i])
        g = lambda y: H(i + 1, y) + dx * (Sf(i + 1, y) + su) / 2 - Hu
        if g(yc[i + 1]) >= 0: ysup[i + 1] = yc[i + 1]; continue           # no alcanza la energía: crítico
        ysup[i + 1] = _biseccion(lambda y: -g(y), 1e-4, yc[i + 1])
    out = []
    for i, e in enumerate(est):
        sup = ysup[i] < yc[i] * 0.98 and fuerza(e["Q"], e["b"], ysup[i]) > fuerza(e["Q"], e["b"], ysub[i])
        y = ysup[i] if sup else ysub[i]
        A, V, sf = _geo(e["Q"], e["b"], y, n)
        out.append(dict(e, y=y, yc=yc[i], ws=e["z"] + y, V=V, Fr=V / math.sqrt(G * y), E=y + V * V / (2 * G), Sf=sf,
                        regimen="supercrítico" if sup else ("crítico" if abs(y - yc[i]) < 0.002 else "subcrítico"), BL=e["h"] - y))
    return out


def _recibe(ram):
    """{eje: (eje que lo recibe, progresiva de la unión en ese eje)}."""
    recibe = {}
    for c, r in ram.items():
        fin = r["nudos"][-1]
        q = next((x for x in ram.values() if x["codigo"] != c and fin in x["nudos"][1:-1]), None)
        if q:
            s = 0.0; prog = {q["nudos"][0]: 0.0}
            for t in q["tramos"]: s += t["L"]; prog[t["a"]] = s
            recibe[c] = (q["codigo"], prog.get(fin, 0.0))
    return recibe


def calcular(C, V, P, descargas=None):
    """Perfil de flujo de toda la red: los ejes que reciben se calculan antes que los que llegan a ellos."""
    n = P["n_cap"]; fila = {(f["eje"], f["de"], f["a"]): f for f in V["hidraulica"]}
    ram = {r["codigo"]: r for r in C["ramales"] if r.get("tramos") and len(r.get("perfil", [])) >= 2}
    recibe = _recibe(ram)
    entra = {}
    for c, (q, _) in recibe.items():
        t = ram[c]["tramos"][-1]; nd = ram[c]["nudos"][-1]
        entra.setdefault(q, {})[nd] = entra.get(q, {}).get(nd, 0.0) + (fila.get((c, t["de"], t["a"])) or {}).get("Q_ls", 0.0) / 1000.0
    res = {}

    def nivel_en(cod, s):
        pts = res[cod]["estaciones"]
        for a, b in zip(pts[:-1], pts[1:]):
            if a["s"] <= s <= b["s"]:
                k = (s - a["s"]) / (b["s"] - a["s"]) if b["s"] > a["s"] else 0
                return a["ws"] + k * (b["ws"] - a["ws"])
        return pts[-1]["ws"]

    def hacer(c, pila=()):
        if c in res or c in pila: return
        est = _estaciones(ram[c], fila, P, entra.get(c, {}))
        control = "descarga libre (tirante crítico)"; yfin = 0.0
        if c in recibe and recibe[c][0] in ram:
            hacer(recibe[c][0], pila + (c,))
            if recibe[c][0] in res:
                ws = nivel_en(recibe[c][0], recibe[c][1]); yfin = max(0.0, ws - est[-1]["z"])
                control = "nivel del agua de %s en la progresiva %.2f (+%.3f)" % (recibe[c][0], recibe[c][1], ws)
        pts = perfil_eje(est, yfin, n)
        for p in pts:                    # margen: borde libre minimo y, en tramos tapados, tirante <= 80 % de la altura libre (CE.040, 17.6.2)
            p["margen"] = p["h"] - (max(p["y"] + P["BL"], p["y"] / P.get("tirante_max_conducto", 0.80)) if p["tapado"] else p["y"] + P["BL"])
        saltos = [{"s": round(b["s"], 2), "y1": round(a["y"], 3), "y2": round(b["y"], 3)} for a, b in zip(pts[:-1], pts[1:])
                  if a["regimen"] == "supercrítico" and b["regimen"] != "supercrítico" and not _es_caida(a, b)]
        bl = min(pts, key=lambda p: p["BL"]); vm = max(pts, key=lambda p: p["V"])
        presion = [p for p in pts if p["tapado"] and p["y"] > p["h"] + 1e-3]
        mg = min(pts, key=lambda p: p["margen"])
        estado = "DESBORDA" if bl["BL"] < -1e-3 else ("CUMPLE" if mg["margen"] >= -1e-3 else
                                                      ("TIRANTE MAYOR AL 80 %" if mg["tapado"] and mg["BL"] >= P["BL"] - 1e-3 else "BORDE LIBRE MENOR"))
        res[c] = {"eje": c, "control": control, "estaciones": pts, "saltos": saltos, "estado": estado,
                  "BL_min": round(bl["BL"], 3), "s_BL_min": round(bl["s"], 2) if estado != "TIRANTE MAYOR AL 80 %" else round(mg["s"], 2),
                  "margen_min": round(mg["margen"], 3), "V_max": round(vm["V"], 2), "s_V_max": round(vm["s"], 2),
                  "y_max": round(max(p["y"] for p in pts), 3), "tramos_a_presion_m": round(sum(1 for _ in presion) * 0.5, 1),
                  "supercritico_m": round(sum(b["s"] - a["s"] for a, b in zip(pts[:-1], pts[1:]) if a["regimen"] == "supercrítico"), 1),
                  "L": round(pts[-1]["s"], 2)}

    for c in ram: hacer(c)
    ejes = [res[c] for c in ram if c in res]
    malos = [e for e in ejes if e["estado"] != "CUMPLE"]
    return {"ejes": ejes, "metodo": "paso estándar (Chow), régimen mixto por fuerza específica", "n": n,
            "resumen": {"ejes": len(ejes), "cumplen": len(ejes) - len(malos), "BL_min": min((e["BL_min"] for e in ejes), default=None),
                        "V_max": max((e["V_max"] for e in ejes), default=None), "saltos": sum(len(e["saltos"]) for e in ejes),
                        "observados": [{"eje": e["eje"], "estado": e["estado"], "BL_min": e["BL_min"], "margen_min": e["margen_min"],
                                        "s": e["s_BL_min"]} for e in malos]}}


def profundizar(C, V, P, hq, descargas):
    """Remansos: donde el nivel del agua real deja menos borde libre que el mínimo, el nivel lo fija lo que hay aguas abajo; se
    profundiza en lo que falta el camino desde ese punto hasta la descarga (el tramo, los que le siguen en el eje y los de los ejes
    que lo reciben), sin pasar de lo que permite el terreno exterior en la descarga. Devuelve {descarga: {tramo: altura libre minima}}
    con lo que cambia (vacio si no hay nada que corregir)."""
    PF = calcular(C, V, P)
    ram = {r["codigo"]: r for r in C["ramales"] if r.get("tramos") and len(r.get("perfil", [])) >= 2}
    recibe = _recibe(ram)
    # lo que puede bajar cada descarga con el mismo criterio de la verificacion: terreno exterior bajo la C.F. - margen a <= 2 m
    holgura = {d["D"]: d["cf"] - P["desc_margen"] - min([zt for dd, zt in d.get("exterior", []) if dd <= P["desc_dist_ext"]] or [d["cf"]])
               for d in V["descargas"] if d["estado"] == "SALE POR GRAVEDAD"}
    holgura.update({d["D"]: d["holgura_alt"] for d in V["descargas"] if d.get("alternativa") and d.get("holgura_alt") is not None})
    nuevo = {}

    def tramos_desde(c, s):
        r = ram[c]; s0 = 0.0; out = []
        for t in r["tramos"]:
            if s0 + t["L"] > s + 1e-6: out.append((c, t, s0))
            s0 += t["L"]
        return out
    for e in PF["ejes"]:
        malos = [p for p in e["estaciones"] if p["margen"] < -1e-3]
        if not malos: continue
        p = min(malos, key=lambda q: q["margen"]); falta = math.ceil(-p["margen"] * 100 - 1e-6) / 100.0
        camino = tramos_desde(e["eje"], p["s"]); c = e["eje"]; vistos = {c}
        while c in recibe and recibe[c][0] in ram and recibe[c][0] not in vistos:
            c, s = recibe[c]; vistos.add(c); camino += tramos_desde(c, s)
        D = ram[c].get("descarga")
        d = min(falta, max(0.0, holgura.get(D, 0.0)))
        if d < 0.01: continue
        for cod, t, s0 in camino:
            # la altura libre minima del tramo exige su punto mas bajo de hoy mas lo que falta: el fondo baja «d», no mas, aunque
            # el piso cambie de nivel a lo largo del tramo
            rr = ram[cod]
            losa = lambda s_: P.get("e_tapa_veh", P["e_tapa"]) if any(a <= s_ <= b for a, b in rr.get("vehiculares", [])) else (
                P["e_tapa"] if any(a <= s_ <= b for a, b in rr.get("tapados", [])) else 0.0)
            libres = [ras - cf - losa(s_) for s_, ras, cf in rr["perfil"] if s0 - 1e-6 <= s_ <= s0 + t["L"] + 1e-6]
            hlib = min(libres) if libres else min(t["h_de"], t["h_a"])
            k = "%s|%s|%s" % (cod, t["de"], t["a"]); g = nuevo.setdefault(D, {})
            v = round(max(g.get(k, 0.0), hq.get(k, P["hmin"]), hlib + d), 3)
            if v > hq.get(k, P["hmin"]) + 1e-6: g[k] = v
    return {D: g for D, g in nuevo.items() if g}


def limitado(PF, C, V, P):
    """Si los ejes con remanso ya no se pueden corregir porque su descarga no puede bajar más (terreno exterior), devuelve el texto
    de la decisión del proyectista con las soluciones; si alguno aún se podría corregir (o no hay remansos), None."""
    obs = PF["resumen"]["observados"]
    if not obs: return None
    ram = {r["codigo"]: r for r in C["ramales"] if r.get("tramos")}
    recibe = _recibe({c: r for c, r in ram.items() if len(r.get("perfil", [])) >= 2})
    holgura = {d["D"]: d["cf"] - P["desc_margen"] - min([zt for dd, zt in d.get("exterior", []) if dd <= P["desc_dist_ext"]] or [d["cf"]])
               for d in V["descargas"]}
    holgura.update({d["D"]: d["holgura_alt"] for d in V["descargas"] if d.get("alternativa") and d.get("holgura_alt") is not None})
    cf = {d["D"]: d["cf"] for d in V["descargas"]}
    por_d = {}
    for o in obs:
        c = o["eje"]; vistos = {c}
        while c in recibe and recibe[c][0] not in vistos: c = recibe[c][0]; vistos.add(c)
        D = ram[c].get("descarga")
        if D not in V.get("remanso_sin_salida", []) and holgura.get(D, 0.0) >= max(0.01, -o.get("margen_min", o["BL_min"] - P["BL"]) - 0.005):
            return None
        por_d.setdefault(D, []).append(o["eje"])
    return ("el nivel del agua lo fija la descarga %s, que ya no puede bajar más por el terreno exterior; soluciones: ancho libre mayor "
            "en los tramos de mayor caudal que llegan a esa descarga, otra descarga para %s, o subir el nivel de piso" % (
                ", ".join("%s (C.F. +%.3f)" % (D, cf.get(D, 0)) for D in por_d), ", ".join(e for v in por_d.values() for e in v)))


def redondear(PF, cada=1):
    """Copia ligera para resultado.json: estaciones redondeadas (una de cada «cada»)."""
    ejes = []
    for e in PF["ejes"]:
        pts = e["estaciones"]; sel = pts[::cada] + ([pts[-1]] if (len(pts) - 1) % cada else [])
        ejes.append(dict({k: v for k, v in e.items() if k != "estaciones"}, estaciones=[
            {"s": round(p["s"], 2), "z": round(p["z"], 3), "y": round(p["y"], 3), "ws": round(p["ws"], 3), "V": round(p["V"], 2),
             "Fr": round(p["Fr"], 2), "BL": round(p["BL"], 3), "regimen": p["regimen"]} for p in sel]))
    return dict(PF, ejes=ejes)
