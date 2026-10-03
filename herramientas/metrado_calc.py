"""Metrado del colector (calculo en Python; la planilla Excel repite el calculo con formulas).

Tramos de hasta 2.00 m con secciones medias, mas registros, cajas, prolongaciones de
cunetas, juntas y empalmes. Criterio de rellenos menores: dentro de la partida de relleno.
"""
import os, sys, json, math
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import diseno as dz

D = dz.D
PESO = {"3/8": 0.56, "1/2": 0.994}
ANG = {"2x2x3/16": 3.63, "1.5x1.5x1/8": 1.83}   # kg/m
SOBREEXC = 0.25          # sobreancho de excavacion a cada lado
ESPONJ = 1.20   # esponjamiento, igual a PARAMETROS!B16 de la planilla del proyecto
RECUB = 0.04
TRASLAPE = 0.40
L_BARRA = 9.00
FRANJA_RELLENO = 1.00    # franja adyacente al muro lado via nivelada hasta NPT


def terreno():
    T = json.load(open(os.path.join(RAIZ, "entregables", "_calc", "terreno.json")))
    return [t["p"] for t in T], [t["z"] for t in T]


def cortes():
    c = {0.0, dz.P_BRINK, dz.P_B1, dz.P_B2}
    for z in dz.ZONAS: c.add(z["p1"]); c.add(z["p2"])
    p = 2.0
    while p < dz.P_BRINK: c.add(round(p, 2)); p += 2.0
    return sorted(c)


GANCHO = 0.30


def perimetros_marco(zona, be, em, ef, h, et):
    """Perimetros de las barras de un juego de marcos por espaciamiento.
    Tramo normal y motos: un solo marco cerrado en el eje de muros y losas (una capa; E.060 14.3.4).
    Cruce de camiones: marco exterior + marco interior (una capa en cada cara)."""
    if zona == "CAMION":
        per_ext = 2 * (be - 2 * RECUB) + 2 * (ef + h + et - 2 * RECUB) + GANCHO
        per_int = 2 * (be - 2 * em + 2 * (em - RECUB)) + 2 * (h + 2 * (em - RECUB)) + GANCHO
        return per_ext, per_int
    per_c = 2 * (be - em) + 2 * (ef / 2 + h + et / 2) + GANCHO
    return per_c, 0.0


def tramos():
    ps, zs = terreno(); out = []
    cs = cortes()
    for a, b in zip(cs[:-1], cs[1:]):
        if b - a < 1e-6: continue
        m = (a + b) / 2; zona = dz.zona(m); L = b - a
        em = D["e_muro"]; ef = D["e_fondo"]; et = D["e_losa_camion"] if zona == "CAMION" else D["e_losa"]
        cf = dz.fondo(m); techo = dz.techo(m); h = techo - cf
        terr = float(np.interp(m, ps, zs)); be = D["b"] + 2 * em
        fondo_sol = cf - ef - D["e_solado"]
        prof = max(0.0, terr - fondo_sol)
        anch = be + 2 * SOBREEXC
        exc = anch * prof * L
        rell_lat = 2 * SOBREEXC * prof * L
        rell_franja = FRANJA_RELLENO * max(0.0, D["NPT"] - terr) * L
        t = dict(p1=a, p2=b, L=L, pm=m, zona=zona, em=em, ef=ef, et=et, h=h, cf=cf, terreno=terr, be=be,
                 c_fondo=be * ef * L, c_muros=2 * em * h * L, c_losa=be * et * L,
                 excav=exc, relleno=rell_lat + rell_franja, relleno_lat=rell_lat, relleno_franja=rell_franja,
                 solado=(be + 0.10) * L, encof=L * (2 * h + 2 * (ef + h + et) + D["b"]),
                 acabado=be * L, trazo=(anch) * L)
        # acero: marcos cerrados exterior e interior (una barra cada uno por espaciamiento)
        s = 0.15 if zona in ("MOTOS", "CAMION") else 0.20
        dia = "1/2" if zona == "CAMION" else "3/8"
        per1, per2 = perimetros_marco(zona, be, em, ef, h, et)
        n = int(L / s) + (1 if a == 0 else 0)
        capas = 2 if zona == "CAMION" else 1
        t["marcos_n"] = n; t["marcos_L"] = (per1 + per2) * n; t["marcos_dia"] = dia; t["capas"] = capas
        t["marcos_kg"] = t["marcos_L"] * PESO[dia]
        sl = 0.20 if zona == "CAMION" else 0.25
        nb = int(round(per1 / sl)) + (int(round(per2 / sl)) if per2 > 0 else 0)
        t["long_n"] = nb; t["long_L"] = nb * L * (1 + TRASLAPE / L_BARRA); t["long_kg"] = t["long_L"] * PESO["3/8"]
        out.append(t)
    return out


def segmentos():
    """Segmentos por zona (los mismos de la hoja COLECTOR TRAMOS): valores medios de h y Hz y acero
    calculado con las mismas reglas de la planilla (marcos = REDONDEAR.MAS(L/s) x capas)."""
    T = tramos(); cortes = sorted(set([0.0] + [z["p1"] for z in dz.ZONAS] + [z["p2"] for z in dz.ZONAS] + [dz.P_B1, dz.P_B2, dz.P_BRINK]))
    segs = []
    for a, b in zip(cortes[:-1], cortes[1:]):
        ts = [t for t in T if t["p1"] >= a - 1e-6 and t["p2"] <= b + 1e-6]
        Ls = sum(t["L"] for t in ts)
        zona = ts[0]["zona"]
        nombre = {"NORMAL": "tramo normal", "MOTOS": "cruce de motos", "CAMION": "cruce de camiones"}[zona]
        if a >= dz.P_B1 - 1e-6 and b <= dz.P_B2 + 1e-6: nombre = "tramo diagonal (quiebres)"
        elif a >= dz.P_B2 - 1e-6: nombre = "tramo recto final"
        h = round(sum(t["h"] * t["L"] for t in ts) / Ls, 3)
        Hz = round(sum(max(0.0, t["terreno"] - (t["cf"] - t["ef"] - D["e_solado"])) * t["L"] for t in ts) / Ls, 3)
        dnpt = round(sum(max(0.0, D["NPT"] - t["terreno"]) * t["L"] for t in ts) / Ls, 3)
        et = ts[0]["et"]; dia = ts[0]["marcos_dia"]; em = D["e_muro"]; ef = D["e_fondo"]; be = D["b"] + 2 * em
        sp = 0.15 if zona in ("MOTOS", "CAMION") else 0.20; capas = 2 if zona == "CAMION" else 1; sl = 0.20 if zona == "CAMION" else 0.25
        L2 = round(b, 2) - round(a, 2)
        n = math.ceil(round(L2 / sp, 6))
        per1, per2 = perimetros_marco(zona, be, em, ef, h, et)
        nb = int(round(per1 / sl)) + (int(round(per2 / sl)) if per2 > 0 else 0)
        segs.append(dict(p1=a, p2=b, L=Ls, zona=zona, nombre=nombre, h=h, Hz=Hz, dnpt=dnpt, et=et, marcos_dia=dia, s=sp, capas=capas, sl=sl,
                         marcos_n=n, marcos_L=n * (per1 + per2), marcos_kg=n * (per1 + per2) * PESO[dia], per1=per1, per2=per2,
                         long_n=nb, long_L=nb * L2 * (1 + TRASLAPE / L_BARRA), long_kg=nb * L2 * (1 + TRASLAPE / L_BARRA) * PESO["3/8"]))
    return segs


def registros():
    n = len([r for r in dz.REGISTROS if r["tipo"] == "registro"]) + 3   # 7 + 1 en CL + 2 en CC
    return dict(n=n, contramarco_m=2.80 * n, contramarco_kg=2.80 * n * ANG["2x2x3/16"], marco_m=2.72 * n, marco_kg=2.72 * n * ANG["1.5x1.5x1/8"],
                tapa_conc=0.68 * 0.68 * 0.08 * n, borde_conc=3.00 * 0.15 * 0.10 * n,
                acero_borde_kg=8 * 1.40 * n * PESO["1/2"], acero_tapa_kg=14 * 0.62 * n * PESO["3/8"], asas_kg=2 * 0.40 * n * PESO["3/8"], anclajes_kg=8 * 0.20 * n * PESO["3/8"],
                pintura_m2=(2.80 * 0.203 + 2.72 * 0.152) * n, losa_descuento=0.70 * 0.70 * D["e_losa"] * n)


def cajas():
    ps, zs = terreno(); e = D["e_muro"]; ef = D["e_fondo"]
    out = {}
    # CL: interior 1.50 x 1.00, piso CF0-0.30, losa superior NPT-0.10
    Li, Bi = D["CL_largo"], D["CL_ancho"]; piso = D["CF0"] - D["CL_poza"]; H = D["NPT"] - D["e_losa"] - piso
    terr = float(np.interp(0.0, ps, zs))
    out["CL"] = dict(nombre="Caja de llegada CL", Li=Li, Bi=Bi, H=H, piso=piso,
                     c_fondo=(Li + 2 * e) * (Bi + 2 * e) * ef, c_muros=(2 * (Li + 2 * e) + 2 * Bi) * e * H - 0.80 * (D["NPT"] - D["e_losa"] - D["CF0"]) * e + e * Bi * (D["CF0"] - piso),
                     c_losa=(Li + 2 * e) * (Bi + 2 * e) * D["e_losa"] - 0.49 * D["e_losa"],
                     excav=(Li + 2 * e + 2 * SOBREEXC) * (Bi + 2 * e + 2 * SOBREEXC) * max(0.0, terr - (piso - ef - D["e_solado"])),
                     solado=(Li + 2 * e + 0.1) * (Bi + 2 * e + 0.1), encof=2 * (2 * (Li + Bi) * H) + Li * Bi, acabado=(Li + 2 * e) * (Bi + 2 * e),
                     acero_kg=((Li + 2 * e) * (Bi + 2 * e) * 2 / 0.20 * 2 + (2 * (Li + Bi)) * H / 0.20 * 2 * 1.1 + (2 * (Li + Bi) + 8 * e) / 0.20 * H * 2) * PESO["3/8"] * 0.6)
    # CC: poza 1.50 x 3.50, piso CF_R01-0.40, umbral 0.40 x 0.25, losa superior
    Li, Bi = D["CC_poza_largo"], D["CC_ancho"]; piso = D["CF_R01"] - D["CC_poza_prof"]; H = D["NPT"] - D["e_losa"] - piso
    terr = float(np.interp(dz.P_FIN - 1.0, ps, zs))
    out["CC"] = dict(nombre="Caja de caida CC", Li=Li, Bi=Bi, H=H, piso=piso,
                     c_fondo=(Li + 2 * e) * (Bi + 2 * e) * ef + 0.25 * D["CC_poza_prof"] * Bi,
                     c_muros=(2 * (Li + 2 * e) + Bi) * e * H - 1.50 * (D["NA_R01"] + 0.5 - D["CF_R01"]) * e + e * Bi * (dz.fondo(dz.P_BRINK) - piso),
                     c_losa=(Li + 2 * e) * (Bi + 2 * e) * D["e_losa"] - 2 * 0.49 * D["e_losa"],
                     excav=(Li + 2 * e + 2 * SOBREEXC) * (Bi + 2 * e + 2 * SOBREEXC) * max(0.0, terr - (piso - ef - D["e_solado"])),
                     solado=(Li + 2 * e + 0.1) * (Bi + 2 * e + 0.1), encof=2 * (2 * (Li + Bi) * H) + Li * Bi + 2 * Bi * D["CC_poza_prof"] + Bi * (dz.fondo(dz.P_BRINK) - piso), acabado=(Li + 2 * e) * (Bi + 2 * e),
                     acero_kg=((Li + 2 * e) * (Bi + 2 * e) * 2 / 0.20 * 2 + (2 * (Li + Bi)) * H / 0.20 * 2 * 1.1 + (2 * (Li + Bi) + 8 * e) / 0.20 * H * 2) * PESO["3/8"] * 0.6)
    for c in out.values():
        c["relleno"] = max(0.0, c["excav"] - (c["Li"] + 2 * e) * (c["Bi"] + 2 * e) * (c["H"] + ef + D["e_solado"]))
    return out


def prolongaciones():
    out = []
    for c in dz.CUNETAS:
        if c["prolong"] > 0.1:
            H = c["NCT"] - c["NCF"] + 0.10; L = c["prolong"]
            out.append(dict(cuneta=c["nombre"], L=L, H=H, c_conc=L * (0.60 * 0.10 + 2 * 0.10 * (H - 0.10)), encof=L * (2 * (H - 0.10) + 2 * H),
                            acero_kg=(L / 0.20 + 1) * (0.40 + 2 * H + 0.3) * PESO["3/8"] + (int((2 * H + 0.4) / 0.20) + 1) * L * PESO["3/8"],
                            excav=L * 0.90 * (H + 0.15), solado=L * 0.70, tapa_m2=L * 0.60))
    return out


def juntas():
    n = int(dz.P_BRINK // 4.0)
    per = 2 * (D["b"] + 2 * D["e_muro"]) + 2 * (D["e_fondo"] + 1.60 + D["e_losa"])
    return dict(n=n, L_dilat=n * per, L_tecnopor_cerco=dz.P_B1, L_tecnopor_piso=2 * dz.P_BRINK + 2 * (D["CL_largo"] + 0.3) + 2 * (D["CC_poza_largo"] + 0.3))


def resumen():
    T = tramos(); Rg = registros(); C = cajas(); Pr = prolongaciones(); J = juntas(); SG = segmentos()
    s = lambda k: sum(t[k] for t in T)
    sg = lambda k: sum(t[k] for t in SG)
    R = {}
    R["trazo_m2"] = s("trazo") + sum(c["solado"] for c in C.values()) + sum(p["solado"] for p in Pr)
    R["excav_m3"] = s("excav") + sum(c["excav"] for c in C.values()) + sum(p["excav"] for p in Pr)
    R["refine_m2"] = s("solado") + sum(c["solado"] for c in C.values())
    R["relleno_m3"] = s("relleno") + sum(c["relleno"] for c in C.values())
    R["elimin_m3"] = (R["excav_m3"] - R["relleno_m3"]) * ESPONJ
    R["solado_m2"] = s("solado") + sum(c["solado"] for c in C.values()) + sum(p["solado"] for p in Pr)
    R["conc_fondo_m3"] = s("c_fondo") + sum(c["c_fondo"] for c in C.values())
    R["conc_muros_m3"] = s("c_muros") + sum(c["c_muros"] for c in C.values())
    R["conc_losa_m3"] = s("c_losa") - Rg["losa_descuento"] + sum(c["c_losa"] for c in C.values()) + Rg["borde_conc"]
    R["encof_m2"] = s("encof") + sum(c["encof"] for c in C.values())
    R["acero_colector_kg"] = sg("marcos_kg") + sg("long_kg") + sum(c["acero_kg"] for c in C.values())
    R["acero_38_kg"] = sum(t["marcos_kg"] for t in SG if t["marcos_dia"] == "3/8") + sg("long_kg") + sum(c["acero_kg"] for c in C.values())
    R["acero_12_kg"] = sum(t["marcos_kg"] for t in SG if t["marcos_dia"] == "1/2")
    R["segmentos"] = SG
    R["acabado_m2"] = s("acabado") + sum(c["acabado"] for c in C.values())
    R["registros"] = Rg; R["cajas"] = C; R["prolong"] = Pr; R["juntas"] = J
    R["cuneta_conc_m3"] = sum(p["c_conc"] for p in Pr); R["cuneta_encof_m2"] = sum(p["encof"] for p in Pr); R["cuneta_acero_kg"] = sum(p["acero_kg"] for p in Pr)
    R["empalmes"] = len(dz.CUNETAS)
    R["L_colector"] = dz.P_BRINK; R["L_total"] = dz.P_FIN
    return T, R


def cuadro_doblado():
    """Filas del cuadro de doblado (elemento, forma, diametro, espaciamiento, longitud, total m, peso kg)."""
    T, R = resumen(); Rg = R["registros"]; SG = R["segmentos"]
    def f(k, zona=None, dia=None):
        return sum(t[k] for t in SG if (zona is None or t["zona"] == zona) and (dia is None or t["marcos_dia"] == dia))
    filas = [
        ("Colector: marcos tramo normal", "marco unico cerrado (eje de la seccion)", '3/8"', "0.20", "ver figura: 2 x (0.95 + h + 0.125) + 0.30", f("marcos_L", "NORMAL"), f("marcos_kg", "NORMAL")),
        ("Colector: marcos cruce de motos", "marco unico cerrado (eje de la seccion)", '3/8"', "0.15", "ver figura", f("marcos_L", "MOTOS"), f("marcos_kg", "MOTOS")),
        ("Colector: marcos cruce de camiones", "marco doble (exterior + interior)", '1/2"', "0.15", "ver figura", f("marcos_L", "CAMION"), f("marcos_kg", "CAMION")),
        ("Colector: barras longitudinales", "recta con traslape 0.40", '3/8"', "0.25 / 0.20", "continua", f("long_L"), f("long_kg")),
        ("Cajas CL y CC: muros y losas", "malla 3/8\" @0.20 ambas caras", '3/8"', "0.20", "ver DP-07", sum(c["acero_kg"] for c in R["cajas"].values()) / PESO["3/8"], sum(c["acero_kg"] for c in R["cajas"].values())),
        ("Registros: refuerzo de borde de abertura", "recta", '1/2"', "2 por lado", "1.40", 8 * 1.40 * Rg["n"], Rg["acero_borde_kg"]),
        ("Tapas de registro (incluye asas)", "recta / U", '3/8"', "0.10", "0.62 / 0.40", 14 * 0.62 * Rg["n"] + 2 * 0.40 * Rg["n"], Rg["acero_tapa_kg"] + Rg["asas_kg"]),
        ("Anclajes de contramarco", "L", '3/8"', "8 por registro", "0.20", 8 * 0.20 * Rg["n"], Rg["anclajes_kg"]),
        ("Prolongacion de cunetas Ejes 11 y 12", "U + rectas", '3/8"', "0.20", "ver DP-06C", R["cuneta_acero_kg"] / PESO["3/8"], R["cuneta_acero_kg"]),
    ]
    tot38 = sum(fl[6] for fl in filas if fl[2] == '3/8"'); tot12 = sum(fl[6] for fl in filas if fl[2] == '1/2"')
    return filas, tot38, tot12


if __name__ == "__main__":
    T, R = resumen()
    for k, v in R.items():
        if isinstance(v, float): print("%-22s %10.2f" % (k, v))
    print("registros", {k: round(v, 2) for k, v in R["registros"].items()})
    for k, c in R["cajas"].items(): print(k, {kk: round(vv, 3) for kk, vv in c.items() if isinstance(vv, float)})
    print("prolong", R["prolong"]); print("juntas", R["juntas"])
    filas, a, b = cuadro_doblado(); print("acero 3/8 %.1f kg, 1/2 %.1f kg" % (a, b))
    print("tramos", len(T), "ejemplo", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in T[0].items()})
