"""Descargas cuando el agua no sale por gravedad: pozos de infiltración o cámara de bombeo.

Infiltración (IS.020 y CE.040 + D.S. N.° 009-2026-VIVIENDA como estructura complementaria; método de CIRIA C753):
- tasa de diseño f = (1 cm / t) / FS, con t el tiempo del test de percolación para bajar 1 cm (IS.020, Anexo 1); con t > 12 min/cm el
  terreno no es apto (IS.020, art. 17) y se pasa a bombeo;
- pozo de absorción: diámetro interior ≥ 1.0 m (IS.020, 20 e), muro de mampostería con juntas abiertas y anillo de grava; área de
  infiltración = la lateral con el diámetro exterior (20 b), mojada hasta el nivel del agua; fondo ≥ 2 m sobre la napa (20 d);
  separación ≥ 6 m entre pozos (21 c);
- tránsito: el hidrograma de entrada (hietograma de bloques alternos × C·A del sector) llena el pozo y sale por las paredes:
  dV = (Qe − f · π · De · h) dt; el nivel máximo queda 0.30 m bajo la cota de fondo de la cuneta que llega; la mitad del volumen
  se vacía en ≤ 24 h (CIRIA).
Bombeo (CE.040 21.2.2; IS.010 6.4 y 7.1 f; OS.080):
- dos bombas sumergibles alternadas, cada una con el caudal pico que llega (máxima intensidad);
- volumen útil entre arranque y parada para ≤ 6 arranques por hora: V = Qb · 10 min / 4; nivel de alarma bajo la cota de fondo de la
  cuneta que llega (la cuneta no queda ahogada);
- impulsión de PVC con velocidad de 0.6 a 2.0 m/s; altura dinámica total = desnivel + fricción (Hazen-Williams, C = 150) +
  accesorios (válvula de retención, compuerta, codos: K = 5); potencia con eficiencia de 60 % y motor comercial con 15 % de reserva.
"""
import math

G = 9.81
DIAM_PVC = [(2, 0.0542), (3, 0.0800), (4, 0.1030), (6, 0.1522), (8, 0.1980), (10, 0.2476), (12, 0.2940)]   # pulgadas, D interior (m) clase 10
HP_COM = [0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100]


def hidrograma(AC_m2, hieto, FS=1.0):
    """Caudales de entrada (m³/s) por bloque del hietograma: Q = C·A·i/3.6e6 (método racional por bloque)."""
    return [FS * AC_m2 * i / 3.6e6 for i in hieto["intensidades"]]


def clase_terreno(t):
    return "rápido" if t <= 4 else "medio" if t <= 8 else "lento" if t <= 12 else "no apto"


# --------------------------------------------------------------------------------------------- infiltración
def _transitar_pozo(Qe, dt_s, n, Di, De, Hab, f_ms, extra=4.0):
    """Nivel máximo (m sobre el fondo) y tiempo para vaciar la mitad del volumen máximo (h). Paso de 30 s; tras la tormenta se
    sigue hasta vaciar (o 72 h)."""
    Ap = n * math.pi * Di ** 2 / 4.0
    h, hmax, paso = 0.0, 0.0, 30.0
    serie = [q for q in Qe for _ in range(int(dt_s / paso))]
    for q in serie:
        h = max(0.0, h + (q - n * f_ms * math.pi * De * h) * paso / Ap)
        hmax = max(hmax, h)
        if h > Hab: return h, None
    # vaciado de la mitad del volumen: dh/dt = −f·π·De·h·n/Ap → h = h0·exp(−k t), mitad en ln2/k
    k = n * f_ms * math.pi * De / Ap
    t50 = math.log(2) / k / 3600.0 if k > 0 else None
    return hmax, t50


def pozos(desc, Qe, dt_s, cfg_inf, P):
    """Diseño de los pozos de absorción de una descarga. desc: {"D", "cf", "ras"}; Qe: hidrograma (m³/s)."""
    t = float(cfg_inf.get("test_min_por_cm") or 0)
    if not t > 0:
        return {"factible": False, "motivo": "Falta el test de percolación (IS.020, Anexo 1): minutos para bajar 1 cm en el lugar del pozo."}
    clase = clase_terreno(t)
    if t > 12:
        return {"factible": False, "clase": clase, "motivo": "Test de percolación de %.1f min/cm: terreno no apto para infiltrar (IS.020, art. 17, más "
                "de 12 min/cm). Se plantea bombeo." % t}
    FS = float(cfg_inf.get("FS", 3.0))
    f_mh = 0.6 / t / FS; f_ms = f_mh / 3600.0
    napa = cfg_inf.get("napa_prof_m")                             # profundidad de la napa bajo el terreno (m); None = no se encontró
    e_muro, grava = float(cfg_inf.get("muro_m", 0.20)), float(cfg_inf.get("anillo_grava_m", 0.25))
    libre = 0.30                                                    # el agua queda 0.30 m bajo la cota de fondo que llega
    H_max = float(cfg_inf.get("H_max_m", 6.0))
    if napa is not None:
        z_napa = desc["ras"] - float(napa)
        H_max = min(H_max, desc["cf"] - libre - (z_napa + 2.0))
    if H_max < 2.0:
        return {"factible": False, "clase": clase, "motivo": "La napa freática está a %.2f m: el fondo del pozo no queda 2 m sobre ella con 2 m dentro "
                "de la capa filtrante (IS.020, 20 d). Se plantea bombeo o zanjas de infiltración superficiales." % float(napa)}
    mejor = None
    for Di in (1.0, 1.5, 2.0, 2.5, 3.0):
        De = Di + 2 * e_muro
        for n in range(1, 13):
            H = 2.0
            while H <= H_max + 1e-9:
                hmax, t50 = _transitar_pozo(Qe, dt_s, n, Di, De, H, f_ms)
                if t50 is not None and hmax <= H and t50 <= 24.0:
                    exc = n * math.pi * (De + 2 * grava) ** 2 / 4.0 * (H + libre + (desc["ras"] - desc["cf"]) + 0.15)
                    if mejor is None or exc < mejor["excavacion_m3"]:
                        mejor = {"n": n, "Di": Di, "De": round(De, 2), "H_absorcion": round(H, 2), "h_max": round(hmax, 3), "t50_h": round(t50, 1),
                                 "excavacion_m3": round(exc, 2)}
                    break
                H = round(H + 0.5, 2)
            if mejor and mejor["n"] <= n and mejor["Di"] <= Di: break
    if not mejor:
        return {"factible": False, "clase": clase, "f_mh": round(f_mh, 4), "motivo": "Con %.1f min/cm y %.0f m³ de tormenta harían falta más de 12 pozos de 3.0 m "
                "de diámetro: se plantea bombeo." % (t, sum(Qe) * dt_s)}
    prof_total = round((desc["ras"] - desc["cf"]) + libre + mejor["H_absorcion"], 2)
    V = sum(Qe) * dt_s
    return dict(mejor, factible=True, tipo="pozo de absorción", clase=clase, test_min_por_cm=t, FS=FS, f_mh=round(f_mh, 4),
                f_mmh=round(1000 * f_mh, 1), volumen_tormenta_m3=round(V, 2), cota_llegada=round(desc["cf"], 3),
                cota_nivel_max=round(desc["cf"] - libre, 3), cota_fondo=round(desc["cf"] - libre - mejor["H_absorcion"], 3),
                profundidad_total=prof_total, separacion_min=6.0, napa_prof_m=napa,
                area_infiltracion_m2=round(mejor["n"] * math.pi * mejor["De"] * mejor["H_absorcion"], 2))


# --------------------------------------------------------------------------------------------- bombeo
def _hazen(Q, D, L, C=150.0):
    return 10.67 * L * Q ** 1.852 / (C ** 1.852 * D ** 4.87)


def camara(desc, Qp, cfg_b, P):
    """Cámara de bombeo de una descarga. Qp: caudal pico que llega (m³/s)."""
    avisos = []
    z_ent = cfg_b.get("cota_entrega")
    if z_ent is None:
        z_ent = desc.get("terreno_ext", desc["ras"]) + 0.50
        avisos.append("Cota del punto de entrega supuesta (terreno exterior + 0.50 m = %.2f): confirmar con el buzón, cuneta o canal que recibe." % z_ent)
    L = cfg_b.get("L_impulsion_m")
    if L is None:
        L = 10.0; avisos.append("Longitud de impulsión supuesta de 10 m: confirmar el recorrido hasta el punto de entrega.")
    Qb = Qp                                                          # cada bomba con el caudal pico (IS.010 6.4 c y 7.1 f)
    Tmin = float(cfg_b.get("ciclo_min", 10.0)) * 60.0
    V_util = Qb * Tmin / 4.0
    lado = 1.50
    while V_util / lado ** 2 > 1.00 and lado < 4.0: lado = round(lado + 0.25, 2)    # altura útil ≤ 1.00 m
    h_util = max(0.30, V_util / lado ** 2)
    n_alarma = desc["cf"] - 0.10                                       # la cuneta que llega no queda ahogada
    n_arranque = n_alarma - 0.10
    n_parada = n_arranque - h_util
    sumergencia = float(cfg_b.get("sumergencia_m", 0.40))
    fondo = n_parada - sumergencia
    # impulsión: el menor diámetro comercial con V ≤ 2.0 m/s (y ≥ 0.6 si se puede)
    D_pulg, D = next(((p, d) for p, d in DIAM_PVC if Qb / (math.pi * d ** 2 / 4) <= 2.0), DIAM_PVC[-1])
    Vimp = Qb / (math.pi * D ** 2 / 4)
    hf = _hazen(Qb, D, L) ; hm = 5.0 * Vimp ** 2 / (2 * G)
    Hg = z_ent - n_parada
    TDH = Hg + hf + hm + 1.0                                          # 1.0 m de presión de llegada
    eta = float(cfg_b.get("eficiencia", 0.60))
    kW = G * Qb * TDH / eta                                         # ρ·g·Q·H/η en kW (Q en m³/s)
    HP = next((h for h in HP_COM if h >= 1.15 * kW / 0.746), HP_COM[-1])
    prof = desc["ras"] - fondo
    return {"tipo": "cámara de bombeo", "factible": True, "Qp_ls": round(1000 * Qp, 2), "Qb_ls": round(1000 * Qb, 2), "bombas": 2,
            "V_util_m3": round(V_util, 3), "lado_m": lado, "h_util_m": round(h_util, 3), "cota_llegada": round(desc["cf"], 3),
            "n_alarma": round(n_alarma, 3), "n_arranque": round(n_arranque, 3), "n_parada": round(n_parada, 3), "cota_fondo": round(fondo, 3),
            "profundidad_m": round(prof, 2), "cota_entrega": round(z_ent, 3), "L_impulsion_m": round(L, 1), "D_impulsion_pulg": D_pulg,
            "V_impulsion": round(Vimp, 2), "Hg_m": round(Hg, 2), "hf_m": round(hf, 2), "hm_m": round(hm, 2), "TDH_m": round(TDH, 2),
            "eficiencia": eta, "potencia_kW": round(kW, 2), "motor_HP": HP,
            "permanencia_min": round((V_util + lado ** 2 * 0.10) / max(Qp, 1e-6) / 60, 1),
            "texto": ("Dos bombas sumergibles para agua de lluvia (una en reserva, funcionamiento alternado), cada una de %.1f l/s a %.1f m de altura "
                      "dinámica total, motor de %s HP; impulsión PVC %d\" de %.0f m con válvula de retención y compuerta; cámara de %.2f × %.2f m, "
                      "fondo a %.2f m de profundidad, control por niveles con alarma, rejilla a la entrada y grupo electrógeno o rebose de "
                      "emergencia." % (1000 * Qb, TDH, ("%g" % HP), D_pulg, L, lado, lado, prof)),
            "avisos": avisos}


def disenar(descargas, cfg, P, hieto, AC_por_descarga, Q_por_descarga):
    """descargas: {D: {"cf", "ras", "terreno_ext"}}; cfg: bloque «descarga_alternativa» del proyecto ({"tipo": "infiltracion"|"bombeo",
    "infiltracion": {...}, "bombeo": {...}}). Devuelve {D: diseño} con la solución por descarga (infiltración si es factible, si no bombeo)."""
    tipo = cfg.get("tipo", "infiltracion")
    dt_s = hieto["dt_min"] * 60.0
    out = {}
    for D, d in descargas.items():
        r = None
        if tipo == "infiltracion":
            Qe = hidrograma(AC_por_descarga.get(D, 0.0), hieto, P.get("FS", 1.0))
            r = pozos(d, Qe, dt_s, cfg.get("infiltracion", {}), P)
            if not r.get("factible"):
                motivo = r.get("motivo")
                r = camara(d, Q_por_descarga.get(D, 0.0), cfg.get("bombeo", {}), P)
                r["avisos"] = [motivo] + r["avisos"]
        else:
            r = camara(d, Q_por_descarga.get(D, 0.0), cfg.get("bombeo", {}), P)
        r["D"] = D
        out[D] = r
    return out


# --------------------------------------------------------------------------------------------- metrado
KG_M2_MALLA = 2 * (1 / 0.20) * 0.56          # malla 3/8" @ 0.20 m en dos sentidos (0.56 kg/m) por cara


def metrado(DA):
    """Partidas de las descargas sin gravedad: [(descripcion, und, [(detalle, cantidad)])], con las mismas cantidades del diseño."""
    pz = [d for d in DA.values() if d.get("tipo") == "pozo de absorción"]
    cm = [d for d in DA.values() if d.get("tipo") == "cámara de bombeo"]
    out = []
    if pz:
        g = 0.25
        ex = [(d["D"], d["n"] * math.pi * (d["De"] + 2 * g) ** 2 / 4 * (d["profundidad_total"] + 0.15)) for d in pz]
        out += [("EXCAVACIÓN PARA POZOS DE ABSORCIÓN", "m³", ex),
                ("MURO DE MAMPOSTERÍA CON JUNTAS ABIERTAS EN POZOS DE ABSORCIÓN", "m²",
                 [(d["D"], d["n"] * math.pi * (d["Di"] + d["De"]) / 2 * (d["profundidad_total"] - 0.15)) for d in pz]),
                ("RELLENO CON GRAVA DE 1\" EN EL ANILLO DE LOS POZOS", "m³",
                 [(d["D"], d["n"] * math.pi * ((d["De"] + 2 * g) ** 2 - d["De"] ** 2) / 4 * (d["H_absorcion"] + 0.30)) for d in pz]),
                ("CONCRETO f'c=210 kg/cm2 EN LOSA DE TECHO DE POZOS (e = 0.15 m)", "m³",
                 [(d["D"], d["n"] * (math.pi * (d["De"] + 2 * g) ** 2 / 4 - 0.36) * 0.15) for d in pz]),
                ("ACERO f'y=4200 kg/cm2 EN LOSA DE TECHO DE POZOS (Ø 3/8\" @ 0.20 m)", "kg",
                 [(d["D"], d["n"] * math.pi * (d["De"] + 2 * g) ** 2 / 4 * KG_M2_MALLA) for d in pz]),
                ("TAPA DE CONCRETO ARMADO 0.60 x 0.60 m PARA POZO DE ABSORCIÓN", "und", [(d["D"], d["n"]) for d in pz]),
                ("ELIMINACIÓN DE MATERIAL EXCEDENTE (esponjamiento 25 %)", "m³", [(D, v * 1.25) for D, v in ex])]
    if cm:
        e, ef, el = 0.20, 0.25, 0.20
        ext = lambda d: d["lado_m"] + 2 * e
        out += [("EXCAVACIÓN PARA CÁMARA DE BOMBEO", "m³", [(d["D"], (ext(d) + 0.60) ** 2 * (d["profundidad_m"] + ef + 0.10)) for d in cm]),
                ("SOLADO DE CONCRETO e = 0.10 m EN CÁMARA DE BOMBEO", "m²", [(d["D"], (ext(d) + 0.20) ** 2) for d in cm]),
                ("CONCRETO f'c=210 kg/cm2 EN CÁMARA DE BOMBEO", "m³",
                 [(d["D"], ext(d) ** 2 * ef + 4 * (d["lado_m"] + e) * e * (d["profundidad_m"] - el) + (ext(d) ** 2 - 0.64) * el) for d in cm]),
                ("ENCOFRADO Y DESENCOFRADO EN CÁMARA DE BOMBEO", "m²",
                 [(d["D"], 4 * (d["lado_m"] + ext(d)) * (d["profundidad_m"] - el) + d["lado_m"] ** 2) for d in cm]),
                ("ACERO f'y=4200 kg/cm2 EN CÁMARA DE BOMBEO (Ø 3/8\" @ 0.20 m EN AMBAS CARAS)", "kg",
                 [(d["D"], (2 * 4 * (d["lado_m"] + e) * (d["profundidad_m"] - el) + 2 * ext(d) ** 2) * KG_M2_MALLA) for d in cm]),
                ("BOMBA SUMERGIBLE PARA AGUA DE LLUVIA (con su cable, cadena de izaje y conexiones)", "und",
                 [("%s: %.1f l/s a %.1f m, %s HP" % (d["D"], d["Qb_ls"], d["TDH_m"], "%g" % d["motor_HP"]), 2) for d in cm]),
                ("TABLERO ELÉCTRICO DE CONTROL AUTOMÁTICO (alternador, flotadores de nivel y alarma)", "und", [(d["D"], 1) for d in cm]),
                ("TUBERÍA DE IMPULSIÓN PVC CLASE 10", "m", [("%s: PVC %d\"" % (d["D"], d["D_impulsion_pulg"]), d["L_impulsion_m"] + 2 * d["profundidad_m"]) for d in cm]),
                ("VÁLVULA DE RETENCIÓN Y VÁLVULA DE COMPUERTA EN IMPULSIÓN", "und", [("%s: %d\" (una de cada por bomba)" % (d["D"], d["D_impulsion_pulg"]), 4) for d in cm]),
                ("REJILLA METÁLICA DE ENTRADA Y TAPA METÁLICA DE ACCESO 0.80 x 0.80 m", "und", [(d["D"], 1) for d in cm]),
                ("ELIMINACIÓN DE MATERIAL EXCEDENTE (esponjamiento 25 %)", "m³",
                 [(d["D"], 1.25 * (ext(d) + 0.60) ** 2 * (d["profundidad_m"] + ef + 0.10)) for d in cm])]
    return [(t, u, [(x, round(q, 3)) for x, q in f]) for t, u, f in out]
