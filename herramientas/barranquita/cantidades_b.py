"""Cantidades de obra por eje de la red de cunetas (I.E. N.° 0590 Barranquita) a partir de diseno.json, verificacion.json y
tapas.json: longitudes, profundidades del perfil (cada 0.50 m), concreto, encofrado, curado, acero, excavacion, rellenos,
rejillas, juntas y tapas de inspeccion. Las mismas cantidades alimentan el metrado (metrado_b.py) y las memorias.
"""
import os, sys, json, math
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import diseno_b as DS

CALC = os.path.join(RAIZ, "entregables_barranquita", "_calc")
B, E, EF, ET = DS.B_INT, DS.E_MURO, 0.10, 0.10      # luz 0.40, muros 0.10, losa de fondo 0.10, losa tapa 0.10
BT = B + 2 * E                                      # 0.60
SOBREANCHO = 0.15                                   # sobreancho de excavacion a cada lado (trabajo y encofrado)
B_EXC = BT + 2 * SOBREANCHO                         # 0.90
SOLADO = 0.10                                       # solado e = 4"
ESPONJ = 1.25                                       # esponjamiento para la eliminacion
JUNTA_CADA = 3.00                                   # junta de dilatacion en toda la seccion en U cada 3.00 m
REC = 0.04                                          # recubrimiento
KG38 = 0.56                                         # kg/m de la barra de 3/8"
SEP_T, SEP_L = 0.25, 0.20                           # U de 3/8" @0.25; longitudinales de 3/8" @0.20
H_ACERO = DS.H_ACERO                                # acero solo con h >= 0.40 m (rejilla al fondo) o en tramo tapado
TAPA = (0.60, 0.60, 0.10)


def u_long(h):
    """Longitud de la U de 3/8" (con ganchos de 0.10 m) y numero de barras longitudinales para una profundidad h."""
    u = 2 * (h + EF - 2 * REC) + (BT - 2 * REC) + 2 * 0.10
    n = 2 * (math.ceil(round(h / SEP_L, 6)) + 1) + (math.ceil(round((BT - 2 * REC) / SEP_L, 6)) + 1)
    return u, n


def kg_acero(L_ac, h_ac, L_tap):
    """Acero de 3/8" de un eje: U @0.25 y longitudinales @0.20 en el largo con acero; losa tapa: transversales @0.20 y 3 barras."""
    if L_ac <= 0: return 0.0
    u, n = u_long(h_ac)
    return (L_ac / SEP_T) * u * KG38 + n * L_ac * KG38 + (L_tap / SEP_L) * (BT - 2 * REC + 0.20) * KG38 + 3 * L_tap * KG38


def _tap(r, s): return any(a - 1e-6 <= s <= b + 1e-6 for a, b in r["tapados"])


def por_eje():
    R = json.load(open(os.path.join(CALC, "diseno.json")))
    tapas = json.load(open(os.path.join(CALC, "tapas.json"))) if os.path.exists(os.path.join(CALC, "tapas.json")) else []
    out = []
    try:
        import shapely, terreno_b as T, hidrologia_b as H
        SUP = H.pisos_metrado(T.cargar(), DS.CERCO, DS.PATIO)
        from shapely.ops import unary_union
        PISO = unary_union([SUP["pavimento"], SUP["techo"]])
    except Exception:
        PISO = None
    CJP = os.path.join(CALC, "junta_piso.json")
    cache_jp = json.load(open(CJP))["junta_piso"] if PISO is None else {}
    if PISO is None and not os.path.exists(CJP):
        raise SystemExit("Sin base del sitio (base_sitio.pkl) ni _calc/junta_piso.json: no se puede metrar la junta con el piso")
    for r in R["ramales"]:
        P = r["perfil"]; L = r["L"]
        L_tap = sum(b - a for a, b in r["tapados"]); L_rej = L - L_tap
        int_h = int_hw = int_ho = 0.0; int_hac = 0.0; L_acero = 0.0; hmax = 0.0
        for (s0, n0, f0), (s1, n1, f1) in zip(P[:-1], P[1:]):
            ds = s1 - s0
            if ds <= 0: continue
            h = ((n0 - f0) + (n1 - f1)) / 2; tap = _tap(r, (s0 + s1) / 2); hmax = max(hmax, n0 - f0, n1 - f1)
            hw = h - (ET if tap else 0.0)                       # altura del muro sobre la losa de fondo (bajo la losa tapa en tapados)
            int_h += h * ds; int_hw += hw * ds; int_ho += (h + EF) * ds
            if tap or h >= H_ACERO - 1e-6:
                L_acero += ds; int_hac += h * ds
        h_prom = int_h / L
        h_ac = int_hac / L_acero if L_acero > 0 else 0.0
        acero = kg_acero(L_acero, h_ac, L_tap)
        n_tapas = sum(1 for t in tapas if t["eje"] == r["codigo"])
        c_muros = 2 * E * int_hw; c_fondo = BT * EF * L; c_tapa = BT * ET * L_tap - n_tapas * TAPA[0] * TAPA[1] * TAPA[2]
        enc = 2 * int_hw + 2 * (int_hw + EF * L) + (B + 2 * ET) * L_tap      # caras interior y exterior de muros + fondo y cantos de la losa tapa
        cur = 2 * int_hw + B * L + 2 * E * (L - L_tap) + BT * L_tap          # caras interiores, fondo, coronas de muro y losa tapa
        exc = B_EXC * (int_ho + SOLADO * L)
        rell = (B_EXC - BT) * (int_ho + SOLADO * L)
        n_j = int(L // JUNTA_CADA); l_junta = 2 * (h_prom + EF) + BT
        j_piso = 0.0                                           # junta asfaltica longitudinal entre el borde de la cuneta y el piso
        if PISO is not None:
            import shapely
            from shapely.geometry import LineString
            ln = LineString([tuple(R["nudos"][n]) for n in r["nudos"]]); k = 0.25
            while k < ln.length:
                p = ln.interpolate(k); q = ln.interpolate(min(ln.length, k + 0.01)); o = ln.interpolate(max(0.0, k - 0.01))
                dx, dy = q.x - o.x, q.y - o.y; d = math.hypot(dx, dy) or 1.0; nx, ny = -dy / d, dx / d
                for sg in (1, -1):
                    if shapely.contains_xy(PISO, p.x + sg * nx * (BT / 2 + 0.15), p.y + sg * ny * (BT / 2 + 0.15)): j_piso += 0.5
                k += 0.5
        out.append({"eje": r["codigo"], "sistema": r["sistema"], "descripcion": r["descripcion"], "L": round(L, 2),
                    "L_tapado": round(L_tap, 2), "L_rejilla": round(L_rej, 2), "h_prom": round(h_prom, 3), "h_max": round(hmax, 2),
                    "area_muro": round(int_hw, 2), "L_acero": round(L_acero, 2), "h_acero": round(h_ac, 3),
                    "concreto": round(c_muros + c_fondo + c_tapa, 3), "c_muros": round(c_muros, 3), "c_fondo": round(c_fondo, 3), "c_tapa": round(c_tapa, 3),
                    "encofrado": round(enc, 2), "curado": round(cur, 2), "acero": round(acero, 2),
                    "solado": round(BT * L, 2), "limpieza": round(B_EXC * L, 2), "excavacion": round(exc, 3), "refine": round(BT * L, 2),
                    "relleno": round(rell, 3), "eliminacion": round((exc - rell) * ESPONJ, 3),
                    "rejilla": round(L_rej, 2), "tapas": n_tapas, "n_juntas": n_j, "l_junta": round(l_junta, 3), "junta": round(n_j * l_junta, 2),
                    "junta_piso": round(min(j_piso, 2 * L), 2) if PISO is not None else cache_jp.get(r["codigo"], 0.0)})
    if PISO is not None:                                    # cache para corridas sin la base del sitio
        json.dump({"fuente": "cantidades_b / base_sitio.pkl", "junta_piso": {x["eje"]: x["junta_piso"] for x in out if x["junta_piso"]}},
                  open(CJP, "w"), indent=1)
    return out


def descargas():
    V = json.load(open(os.path.join(CALC, "verificacion.json")))
    return [{"D": d["D"], "cf": d["cf"], "sale_a_m": d.get("sale_a_m") or 0.5, "perfilado": round(BT * (d.get("sale_a_m") or 0.5), 2),
             "receptor": d.get("receptor", "")} for d in V["descargas"]]


if __name__ == "__main__":
    q = por_eje()
    for k in ("L", "L_tapado", "concreto", "encofrado", "curado", "acero", "excavacion", "relleno", "eliminacion", "rejilla", "tapas", "junta", "junta_piso"):
        print(k, round(sum(x[k] for x in q), 2))
    for x in q: print(x["eje"], x["L"], x["h_prom"], x["acero"], x["L_acero"])
