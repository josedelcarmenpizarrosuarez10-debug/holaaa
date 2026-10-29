"""Drenaje vial de carreteras según el Manual de Hidrología, Hidráulica y Drenaje del MTC (R.D. N.° 20-2011-MTC/14).

Cunetas laterales (drenaje longitudinal, 4.1.2), alcantarillas de alivio y de paso de quebradas (drenaje transversal, 4.1.1.3)
y badenes (4.1.1.4). Cada valor normativo sale de la biblioteca de normas (normas_biblioteca.json, cotejada con el texto oficial).

Datos (JSON): proyecto, lluvia (la misma de la pestaña LLUVIA: serie de máximas o P24 por período de retorno), via (velocidad de
diseño, IMDA, precipitación anual, selva alta), cunetas [...], alcantarillas [...], badenes [...]. Ver ejemplos/vial_sm.json.
Resultado: períodos de retorno, intensidades, tiempos de concentración, caudales, secciones y verificaciones, con avisos.
"""
import math

from . import hidrologia, normas

G = 9.81
# Tabla N.° 02 (numeral 3.6): riesgo admisible R y vida útil n por tipo de obra
OBRAS = {
    "plataforma": (0.40, 15, "Drenaje de la plataforma (a nivel longitudinal)"),
    "quebrada_menor": (0.35, 15, "Alcantarillas de paso de quebradas menores y descarga de agua de cunetas"),
    "quebrada_importante": (0.30, 25, "Alcantarillas de paso de quebradas importantes y badenes"),
}
# Tabla N.° 08 (numeral 3.12.2): C por cobertura, suelo y pendiente (> 50, > 20, > 5, > 1, < 1 %)
COBERTURAS = {"sin_vegetacion": "Sin vegetación", "cultivos": "Cultivos", "pastos": "Pastos, vegetación ligera",
              "hierba": "Hierba, grama", "bosques": "Bosques, densa vegetación"}
SUELOS = {"impermeable": "Impermeable", "semipermeable": "Semipermeable", "permeable": "Permeable"}
# Tabla N.° 32: n = 1/K en cunetas; Tabla N.° 33: velocidad límite (se adopta el inferior del rango)
CUNETA_N = {"concreto": 0.015, "tierra": 0.030, "roca": 0.040}
TMC_PULG = [24, 36, 48, 60, 72, 84, 96, 108, 120]
N_TMC = 0.024                       # Tabla N.° 09: metal corrugado, dren para aguas lluvias (normal)
N_CONCRETO = 0.013                  # Tabla N.° 09: canal revestido de concreto afinado con plana (normal)


# ------------------------------------------------------------------------------------------------ hidrología
def T_de(R, n):
    """Período de retorno para el riesgo admisible R en n años de vida útil (ecuación 1: R = 1 − (1 − 1/T)^n)."""
    return 1.0 / (1.0 - (1.0 - R) ** (1.0 / n))


def periodo(obra, via):
    R, n, texto = OBRAS[obra]
    R = float(via.get("riesgo", {}).get(obra, R)); n = int(via.get("vida_util", {}).get(obra, n))
    T = via.get("T", {}).get(obra)
    exacto = T_de(R, n)
    return {"obra": texto, "R": R, "n": n, "T_calculado": round(exacto, 1), "T": int(T) if T else int(math.ceil(exacto - 1e-9))}


class Lluvia:
    """P24 de diseño para cualquier T: desde la serie de máximas (análisis de frecuencias del motor) o desde P24 por T dados."""

    def __init__(self, lluvia, base="."):
        self.fuente, self._A, self._d, self._tabla = "", None, None, None
        sm, fuente = hidrologia.serie_de(lluvia, base)
        if sm:
            f = float(lluvia.get("factor", 1.0))
            self.maximos = [(a, round(max(v for v in m if v is not None) * f, 2)) for a, m in sorted(sm.items())
                            if any(v is not None for v in m)]
            A = hidrologia.analisis(self.maximos, hidrologia.PERIODOS)
            self._d = lluvia.get("distribucion") or A["elegida"]
            self.fuente = "%s, %s (%d años, factor %.2f)" % (fuente, hidrologia.NOMBRE_DIST[self._d], A["n"], f)
        elif lluvia.get("P24_por_T"):
            self._tabla = sorted((float(t), float(p)) for t, p in lluvia["P24_por_T"].items())
            self.fuente = "P24 por período de retorno del proyecto"
        else:
            raise ValueError("Falta la lluvia: cargue la serie de máximas en 24 h (pestaña LLUVIA) o la P24 por período de retorno.")
        self.estacion = lluvia.get("estacion", {})

    def P24(self, T):
        if self._tabla is None:
            return float(hidrologia.analisis(self.maximos, [T])["tabla"][T][self._d])
        t = self._tabla
        if len(t) == 1: return t[0][1]
        x = math.log(T)                                   # P24 lineal con ln T (interpolación y extrapolación en los extremos)
        for (t1, p1), (t2, p2) in zip(t, t[1:]):
            if T <= t2 or (t2, p2) == t[-1]:
                return p1 + (p2 - p1) * (x - math.log(t1)) / (math.log(t2) - math.log(t1))

    def I(self, T, tc_min):
        """Intensidad (mm/h) para la duración tc por Dick y Peschke (numeral 3.8, ecuación 16)."""
        return 60.0 * hidrologia.p_dur(self.P24(T), tc_min) / tc_min


def C_tabla(cobertura, suelo, pendiente_pct):
    """C de la Tabla N.° 08."""
    nombre = COBERTURAS[cobertura]; s = SUELOS[suelo]
    fila = next(f for f in normas.cuadro("vial_C_tabla08")["filas"] if f[0] == nombre and f[1] == s)
    p = float(pendiente_pct)
    col = 2 if p > 50 else 3 if p > 20 else 4 if p > 5 else 5 if p > 1 else 6
    return fila[col]


def C_cuenca(x):
    """C dado, o ponderado por áreas con la Tabla N.° 08: coberturas = [{fraccion, cobertura, suelo}] y pendiente del terreno."""
    if x.get("C") not in (None, ""): return float(x["C"]), "dato"
    cob = x.get("coberturas") or [{"fraccion": 1.0, "cobertura": x.get("cobertura", "bosques"), "suelo": x.get("suelo", "semipermeable")}]
    p = x.get("pendiente_terreno_pct", 100 * float(x.get("H_m", 0)) / max(1.0, float(x.get("L_m", 1))))
    tot = sum(float(k["fraccion"]) for k in cob)
    C = sum(float(k["fraccion"]) * C_tabla(k["cobertura"], k["suelo"], p) for k in cob) / tot
    det = "; ".join("%s %s %.0f %%" % (COBERTURAS[k["cobertura"]], SUELOS[k["suelo"]].lower(), 100 * float(k["fraccion"]) / tot) for k in cob)
    return round(C, 3), "Tabla N.° 08 (%s; pendiente %.1f %%)" % (det, p)


def tiempos(x, C=None):
    """Tiempos de concentración de la Tabla N.° 05 que se pueden calcular con los datos de la cuenca (min)."""
    L = float(x["L_m"]); H = float(x["H_m"]); S = H / L
    t = {"Kirpich": 0.01947 * L ** 0.77 * S ** -0.385,
         "California Culverts Practice": 0.0195 * (L ** 3 / H) ** 0.385,
         "Témez": 60 * 0.3 * ((L / 1000.0) / S ** 0.25) ** 0.76}
    if x.get("CN"): t["Retardo SCS"] = 0.0136 * L ** 0.8 * (1000.0 / float(x["CN"]) - 9) ** 0.7 / S ** 0.5
    if x.get("L_superficial_m") and C is not None:
        t["Federal Aviation Administration"] = 0.7035 * (1.1 - C) * float(x["L_superficial_m"]) ** 0.5 / S ** 0.333
    return {k: round(v, 2) for k, v in t.items()}


def caudal_cuenca(x, lluvia, T, tc_min_norma):
    """Caudal de una quebrada: racional (A < 10 km²) o racional modificado de Témez (10 a 770 km²)."""
    A = float(x["area_km2"]); avisos = []
    if A >= 770: raise ValueError("%s: cuenca de %.1f km²; el método racional modificado vale hasta 770 km² (use un hidrograma)." % (x["id"], A))
    C, fuente_C = C_cuenca(x)
    tcs = tiempos(x, C)
    metodo = x.get("tc_metodo", "promedio")
    if metodo == "promedio": tc = sum(tcs.values()) / len(tcs)
    elif metodo == "minimo": tc = min(tcs.values())
    else: tc = tcs[metodo]
    tc_adop = max(tc_min_norma, tc)
    if A < 10:
        I = lluvia.I(T, tc_adop); Q = 0.278 * C * I * A
        return {"metodo": "Racional (Q = 0.278 C I A)", "cita": normas.cita("vial_racional"), "C": C, "fuente_C": fuente_C,
                "tc": tcs, "tc_metodo": metodo, "tc_min": round(tc_adop, 2), "I_mmh": round(I, 2), "K": 1.0, "Q": round(Q, 3)}, avisos
    tch = (0.3 * ((float(x["L_m"]) / 1000.0) / (float(x["H_m"]) / float(x["L_m"])) ** 0.25) ** 0.76)     # Témez, horas
    K = 1 + tch ** 1.25 / (tch ** 1.25 + 14); kA = 1 - math.log10(A) / 15
    Pd = lluvia.P24(T); P = kA * Pd
    I = (P / 24.0) * 11 ** ((28 ** 0.1 - tch ** 0.1) / (28 ** 0.1 - 1))
    if x.get("CN"):
        Po = 5000.0 / float(x["CN"]) - 50; C = (Pd - Po) * (Pd + 23 * Po) / (Pd + 11 * Po) ** 2 if Pd > Po else 0.0
        fuente_C = "Témez con CN %.0f (Po = %.1f mm)" % (float(x["CN"]), Po)
    else:
        avisos.append("%s: sin número de curva CN se usa el C de la Tabla N.° 08 en el racional modificado." % x["id"])
    Q = 0.278 * C * I * A * K
    return {"metodo": "Racional modificado de Témez (Q = 0.278 C I A K)", "cita": normas.cita("vial_racional_mod"), "C": round(C, 3),
            "fuente_C": fuente_C, "tc": tcs, "tc_metodo": "Témez", "tc_min": round(60 * tch, 2), "I_mmh": round(I, 2), "K": round(K, 3),
            "kA": round(kA, 3), "P_mm": round(P, 2), "Q": round(Q, 3)}, avisos


# ------------------------------------------------------------------------------------------------ hidráulica
def geometria(sec, y):
    """(área, perímetro mojado, ancho superficial) para el tirante y."""
    t = sec["tipo"]
    if t == "triangular":
        z1, z2 = sec["z1"], sec["z2"]
        return y * y * (z1 + z2) / 2, y * (math.hypot(1, z1) + math.hypot(1, z2)), y * (z1 + z2)
    if t == "trapezoidal":
        b, z1, z2 = sec["b"], sec["z1"], sec["z2"]
        return y * (b + y * (z1 + z2) / 2), b + y * (math.hypot(1, z1) + math.hypot(1, z2)), b + y * (z1 + z2)
    if t in ("rectangular", "marco"):
        b = sec["b"] * sec.get("celdas", 1)
        return b * y, b + 2 * y * sec.get("celdas", 1), b
    if t == "circular":
        D = sec["D"]; y = min(y, D * 0.9999); th = 2 * math.acos(1 - 2 * y / D)
        k = sec.get("celdas", 1)
        return k * D * D / 8 * (th - math.sin(th)), k * D * th / 2, k * D * math.sin(th / 2)
    raise ValueError("Sección desconocida: %s" % t)


def manning(sec, y, S, n):
    A, P, _ = geometria(sec, y)
    V = (A / P) ** (2 / 3) * math.sqrt(S) / n if A > 0 else 0.0
    return A * V, V


def tirante(sec, Q, S, n, ymax):
    """Tirante normal para Q (bisección hasta ymax); None si no cabe."""
    if manning(sec, ymax, S, n)[0] < Q: return None
    lo, hi = 1e-5, ymax
    for _ in range(80):
        y = (lo + hi) / 2
        if manning(sec, y, S, n)[0] > Q: hi = y
        else: lo = y
    return (lo + hi) / 2


def froude(sec, y, V):
    A, _, Tsup = geometria(sec, y)
    return V / math.sqrt(G * A / Tsup) if Tsup > 0 else 0.0


# ------------------------------------------------------------------------------------------------ cunetas
def region(pp_anual):
    p = float(pp_anual)
    return ("Seca", 0) if p < 400 else ("Lluviosa", 1) if p < 1600 else ("Muy lluviosa", 2) if p < 3000 else ("Muy lluviosa (> 3000 mm)", 3)


def talud_interior_min(via):
    """Z1 mínimo (H por 1 V) de la Tabla N.° 304.12 (DG-2001) según la velocidad de diseño y el IMDA. Con V < 70 km/h e
    IMDA < 750 la tabla da 1:2 – 1:3 «sólo en casos muy especiales»: se acepta 1:2 con aviso."""
    v, imda = float(via.get("velocidad_kmh", 40)), float(via.get("imda", 0))
    if v < 70: return 2.0 if imda <= 750 else 3.0
    return 3.0 if imda <= 750 else 4.0


def seccion_cuneta(c, via):
    """Sección de la cuneta. Triangular: profundidad d y ancho a (borde de la rasante a la vertical del vértice: z1 = a/d)."""
    s = dict(c.get("seccion") or {})
    reg, k = region(via.get("precipitacion_anual_mm", 2000))
    minimo = normas.cuadro("vial_cuneta_tabla34")["filas"][k]
    if not s:                                              # la mínima de la Tabla N.° 34 para la región
        s = {"tipo": "trapezoidal", "b": 0.30, "d": 0.30, "a": 1.20} if k == 3 else {"tipo": "triangular", "d": minimo[2], "a": minimo[3]}
    s.setdefault("tipo", "triangular")
    if s["tipo"] in ("triangular", "trapezoidal"):
        s["z1"] = float(s.get("z1") or (float(s["a"]) / float(s["d"])))
        s["z2"] = float(s.get("z2", via.get("talud_corte_z", 0.5)))
    s["d"] = float(s["d"])
    return s, reg, minimo


def cuneta(c, via, lluvia, T, avisos):
    """Capacidad (cuneta llena y velocidad límite), longitud máxima y alcantarillas de alivio de un tramo de cuneta."""
    sec, reg, minimo = seccion_cuneta(c, via)
    rev = c.get("revestimiento", "concreto")
    n = float(c.get("n", CUNETA_N[rev]))
    vel = {f[0]: f[1] for f in normas.cuadro("vial_vel_tabla33")["filas"]}
    Vmax = float(c.get("Vmax", vel["Concreto"] if rev == "concreto" else vel["Mampostería, rocas duras"] if rev == "roca" else
                       vel[c.get("superficie", "Terreno parcialmente cubierto de vegetación")]))
    S = float(c["pendiente"]); L = float(c["prog_fin"]) - float(c["prog_ini"])
    if L <= 0: raise ValueError("%s: la progresiva final debe ser mayor que la inicial." % c["id"])
    tc = max(float(via.get("tc_min", normas.dato("tc_min")["valor"])), float(c.get("tc_min", 0)))
    I = lluvia.I(T, tc)
    aportes = c.get("aportes") or [{"descripcion": "Calzada y berma", "ancho": 3.6, "C": 0.86}]
    CA = sum(float(a["C"]) * float(a["ancho"]) for a in aportes)
    q = CA * I / 3.6e6                                      # m³/s por metro de cuneta (Q = C I A / 3.6, A en km²)
    Q0 = float(c.get("Q_inicial", 0))
    Qll, Vll = manning(sec, sec["d"], S, n)
    Qcap, ycap = Qll, sec["d"]
    if Vll > Vmax:                                         # el límite es la velocidad: tirante con V = Vmax
        lo, hi = 1e-5, sec["d"]
        for _ in range(80):
            y = (lo + hi) / 2
            if manning(sec, y, S, n)[1] > Vmax: hi = y
            else: lo = y
        ycap = lo; Qcap = manning(sec, ycap, S, n)[0]
    Lnorma = 200.0 if float(via.get("precipitacion_anual_mm", 2000)) >= 1600 else 250.0
    Lcap = (Qcap - Q0) / q if q > 0 else float("inf")
    Lmax = min(Lcap, Lnorma, float(c.get("Lmax", 1e9)))
    tramos = max(1, math.ceil(L / Lmax - 1e-9)) if Lmax > 0 else None
    av = []
    if Lmax <= 0 or tramos is None:
        av.append("%s: la cuneta no puede recibir el caudal inicial; aumente la sección." % c["id"]); tramos = 1
    Lseg = L / tramos
    p0 = float(c["prog_ini"]); sentido = c.get("sentido", "creciente")
    segs = []
    for i in range(tramos):
        a, b = (p0 + i * Lseg, p0 + (i + 1) * Lseg)
        Qs = (Q0 if i == 0 else 0) + q * Lseg
        y = tirante(sec, Qs, S, n, sec["d"])
        Qy, V = manning(sec, y, S, n) if y else (None, None)
        desc = b if sentido == "creciente" else a
        segs.append({"desde": round(a, 2), "hasta": round(b, 2), "longitud": round(Lseg, 2), "Q": round(Qs, 4),
                     "tirante": round(y, 5) if y else None, "V": round(V, 2) if V else None,
                     "froude": round(froude(sec, y, V), 2) if y else None, "descarga_en": round(desc, 2)})
    estado = "CUMPLE"
    if sec["tipo"] == "triangular":
        if isinstance(minimo[2], (int, float)) and (sec["d"] + 1e-9 < minimo[2] or float(sec["a"]) + 1e-9 < minimo[3]):
            av.append("%s: la sección %.2f × %.2f m es menor que la mínima de la Tabla N.° 34 para región %s (%.2f × %.2f m)."
                      % (c["id"], sec["d"], float(sec["a"]), reg.lower(), minimo[2], minimo[3])); estado = "REVISAR"
        if sec["d"] > 0.60 + 1e-9: av.append("%s: profundidad mayor que 0.60 m (numeral 4.1.2.1)." % c["id"])
        zmin = talud_interior_min(via)
        if sec["z1"] + 1e-9 < zmin:
            av.append("%s: talud interior 1:%.1f más empinado que el 1:%.0f de la Tabla N.° 304.12." % (c["id"], sec["z1"], zmin)); estado = "REVISAR"
        elif zmin == 2.0 and sec["z1"] < 3.0 - 1e-9:
            av.append("%s: talud interior 1:%.1f; con V < 70 km/h e IMDA < 750 la Tabla N.° 304.12 da 1:2 – 1:3 «sólo en casos muy "
                      "especiales»: justifíquelo o use 1:3." % (c["id"], sec["z1"]))
    if S < 0.005: av.append("%s: pendiente %.2f %% menor que 0.5 %% (autolimpieza); prevea limpieza o depósitos de sedimentos." % (c["id"], 100 * S))
    if S > 0.02: av.append("%s: pendiente %.2f %% mayor que 2 %%; velocidad verificada con la Tabla N.° 33." % (c["id"], 100 * S))
    if any(s["V"] and s["V"] > Vmax + 1e-9 for s in segs): estado = "NO CUMPLE"
    if Lcap < Lnorma and Lcap < L: av.append("%s: la capacidad obliga a descargar cada %.0f m (menos que los %.0f m del numeral 4.1.2.1)." % (c["id"], Lcap, Lnorma))
    avisos.extend(av)
    return {"id": c["id"], "lado": c.get("lado", ""), "prog_ini": float(c["prog_ini"]), "prog_fin": float(c["prog_fin"]), "longitud": round(L, 2),
            "pendiente": S, "seccion": sec, "region": reg, "minimo_tabla34": minimo[2:], "revestimiento": rev, "n": n, "Vmax": Vmax,
            "tc_min": tc, "I_mmh": round(I, 2), "aportes": aportes, "CA": round(CA, 3), "q_m3s_m": q, "Q_inicial": Q0,
            "Q_lleno": round(Qll, 4), "V_lleno": round(Vll, 2), "Q_capacidad": round(Qcap, 4), "tirante_capacidad": round(ycap, 3),
            "L_capacidad": round(Lcap, 1) if Lcap != float("inf") else None, "L_norma": Lnorma, "L_max": round(Lmax, 1),
            "tramos": segs, "alivios": [s["descarga_en"] for s in segs], "estado": estado, "avisos": av}


# ------------------------------------------------------------------------------------------------ alcantarillas
def _diseno_conducto(Q, S, x, via, avisos):
    """Sección de la alcantarilla con tirante ≤ 75 % de la altura (borde libre del 25 %)."""
    tipo = x.get("tipo_conducto", "TMC")
    fr = 1 - normas.dato("vial_alc_borde")["valor"] / 100.0
    if tipo == "MCA":
        n = float(x.get("n", N_CONCRETO))
        if x.get("b") and x.get("h"): opciones = [(float(x["b"]), float(x["h"]))]
        else: opciones = [(b / 100, h / 100) for h in range(100, 401, 25) for b in range(100, 601, 25) if 0.5 <= b / h <= 2.0]
        opciones.sort(key=lambda bh: (bh[0] * bh[1], bh[1]))
        for b, h in opciones:
            sec = {"tipo": "marco", "b": b, "h": h}
            y = tirante(sec, Q, S, n, fr * h)
            if y: return sec, n, y, "Marco de concreto armado %.2f × %.2f m" % (b, h)
        raise ValueError("%s: Q = %.2f m³/s no cabe en un marco de hasta 6.00 × 4.00 m; plantee un puente o celdas múltiples." % (x["id"], Q))
    n = float(x.get("n", N_TMC))
    dmin = float(x.get("diametro_min_pulg") or via.get("diametro_min_pulg") or (48 if via.get("selva_alta") else 36))
    lista = [float(x["diametro_pulg"])] if x.get("diametro_pulg") else [d for d in TMC_PULG if d >= dmin]
    for celdas in (1, 2, 3):
        for dp in lista:
            sec = {"tipo": "circular", "D": dp * 0.0254, "pulg": dp, "celdas": celdas}
            y = tirante(sec, Q, S, n, fr * sec["D"])
            if y:
                if celdas > 1: avisos.append("%s: %d líneas de TMC Ø %.0f\"; separación entre tubos D/2 (0.40 a 1.00 m) y cuide la palizada." % (x["id"], celdas, dp))
                return sec, n, y, "%sTMC Ø %.0f\"" % ("%d × " % celdas if celdas > 1 else "", dp)
    raise ValueError("%s: Q = %.2f m³/s supera 3 TMC de Ø %.0f\"; use un marco de concreto (tipo_conducto MCA)." % (x["id"], Q, lista[-1]))


def _cuenca(x):
    return {k: float(x[k]) for k in ("area_km2", "L_m", "H_m") if x.get(k) not in (None, "")} if float(x.get("area_km2", 0)) > 0 else None


def progresiva(p):
    """0+480.00"""
    return "%d+%06.2f" % (int(p // 1000), p - 1000 * int(p // 1000))


def asignar_descargas(cun, obras, tolerancia=50.0):
    """Cada obra (alcantarilla o badén) que nombra cunetas recibe la descarga de cada una más cercana a su progresiva (hasta
    `tolerancia_m`, 50 m por defecto). Devuelve las descargas ya recibidas {(cuneta, índice del tramo)}."""
    usadas = set()
    for x in obras:
        x["_recibe"] = []
        for cid in x.get("cunetas", []):
            c = next((c for c in cun if c["id"] == cid), None)
            if c is None: raise ValueError("%s: la cuneta %s no existe." % (x["id"], cid))
            k, s = min(enumerate(c["tramos"]), key=lambda t: abs(t[1]["descarga_en"] - float(x["prog"])))
            if abs(s["descarga_en"] - float(x["prog"])) <= float(x.get("tolerancia_m", tolerancia)) and (cid, k) not in usadas:
                usadas.add((cid, k)); x["_recibe"].append((cid, s["Q"], s["descarga_en"]))
    return usadas


def alcantarilla(x, via, lluvia, tc_norma, avisos):
    obra = x.get("obra") or ("quebrada_menor" if x.get("tipo", "cruce") == "alivio" or float(x.get("area_km2", 0)) < 1 else "quebrada_importante")
    P = periodo(obra, via); av = []
    hid = None; Qc = 0.0; desde = []
    if float(x.get("area_km2", 0)) > 0:
        hid, a2 = caudal_cuenca(x, lluvia, P["T"], tc_norma); av += a2
    for cid, Qs, p in x.get("_recibe", []):                 # cunetas que descargan en esta alcantarilla
        Qc += Qs; desde.append("%s en %s (%.3f m³/s)" % (cid, progresiva(p), Qs))
    Q = (hid["Q"] if hid else 0.0) + Qc + float(x.get("Q_adicional", 0))
    if Q <= 0: raise ValueError("%s: sin caudal (no tiene cuenca ni cunetas que descarguen en la progresiva %.2f)." % (x["id"], float(x["prog"])))
    S = float(x.get("pendiente", 0.02))
    sec, n, y, nombre = _diseno_conducto(Q, S, x, via, av)
    _, V = manning(sec, y, S, n)
    altura = sec.get("D") or sec.get("h")
    vmin = normas.dato("vial_alc_vmin")["valor"]
    if V < vmin: av.append("%s: velocidad %.2f m/s menor que %.2f m/s; puede sedimentarse (aumente la pendiente)." % (x["id"], V, vmin))
    vmax_c = 6.0                                            # Tabla N.° 10: concreto 3.0 – 6.0 m/s
    if sec["tipo"] == "marco" and V > vmax_c:
        av.append("%s: velocidad %.2f m/s mayor que %.1f m/s, límite del concreto en la Tabla N.° 10; reduzca la pendiente, agrande la "
                  "sección o disipe la energía a la salida." % (x["id"], V, vmax_c))
    if via.get("selva_alta") and sec["tipo"] == "circular" and sec["pulg"] < 48:
        av.append("%s: en selva alta con cauces en V y suelos erosionables el MTC recomienda TMC Ø 48\" como mínimo." % x["id"])
    vel11 = {f[0]: f[1] for f in normas.cuadro("vial_vel_tabla11")["filas"]}
    vs = vel11.get(x.get("terreno_salida", ""), None)
    d50 = V * V / (3.1 * G)
    if vs and V > vs: av.append("%s: la velocidad de salida %.2f m/s supera %.2f m/s del terreno (Tabla N.° 11): enrocado d50 ≥ %.2f m." % (x["id"], V, vs, d50))
    avisos.extend(av)
    return {"id": x["id"], "prog": float(x["prog"]), "tipo": x.get("tipo", "cruce"), "periodo": P, "hidrologia": hid, "cuenca": _cuenca(x),
            "Q_cuencas": hid["Q"] if hid else 0.0, "Q_cunetas": round(Qc, 4), "desde_cunetas": desde, "Q": round(Q, 3),
            "pendiente": S, "longitud": float(x.get("longitud_m", 0)) or None, "seccion": sec, "conducto": nombre, "n": n,
            "tirante": round(y, 5), "tirante_rel": round(y / altura, 3), "V": round(V, 2), "froude": round(froude(sec, y, V), 2),
            "d50_salida": round(d50, 3),
            "estado": "CUMPLE" if V >= vmin and not (sec["tipo"] == "marco" and V > vmax_c) else "REVISAR", "avisos": av}


# ------------------------------------------------------------------------------------------------ badenes
def baden(x, via, lluvia, tc_norma, avisos):
    """Badén idealizado como canal trapezoidal en régimen uniforme (4.1.1.4.2) con borde libre de 0.30 a 0.50 m."""
    P = periodo("quebrada_importante", via); av = []
    hid, a2 = caudal_cuenca(x, lluvia, P["T"], tc_norma) if float(x.get("area_km2", 0)) > 0 else (None, [])
    av += a2
    Qc = sum(q for _, q, _ in x.get("_recibe", []))
    Q = (hid["Q"] if hid else 0.0) + Qc + float(x.get("Q_adicional", 0))
    S = float(x.get("pendiente_transversal", 0.025))
    sec = {"tipo": "trapezoidal", "b": float(x.get("b", 4.0)), "z1": float(x.get("z", 10.0)), "z2": float(x.get("z", 10.0))}
    H = float(x.get("profundidad", 0.60)); n = float(x.get("n", 0.017))
    y = tirante(sec, Q, S, n, H)
    bl = H - y if y else None
    if not (0.02 - 1e-9 <= S <= 0.03 + 1e-9): av.append("%s: pendiente transversal %.1f %% fuera del 2 a 3 %% recomendado." % (x["id"], 100 * S))
    estado = "CUMPLE"
    if y is None or bl < 0.30 - 1e-9:
        estado = "NO CUMPLE"; av.append("%s: el borde libre no llega a 0.30 m; ensanche el badén o aumente su profundidad." % x["id"])
    _, V = manning(sec, y, S, n) if y else (None, None)
    avisos.extend(av)
    return {"id": x["id"], "prog": float(x["prog"]), "periodo": P, "hidrologia": hid, "cuenca": _cuenca(x), "Q_cunetas": round(Qc, 4),
            "desde_cunetas": ["%s en %s (%.3f m³/s)" % (c, progresiva(p), q) for c, q, p in x.get("_recibe", [])],
            "Q": round(Q, 3), "seccion": sec, "profundidad": H,
            "n": n, "pendiente_transversal": S, "tirante": round(y, 5) if y else None, "borde_libre": round(bl, 3) if bl is not None else None,
            "V": round(V, 2) if V else None, "estado": estado, "avisos": av}


# ------------------------------------------------------------------------------------------------ cálculo completo
CAMPOS = {"cunetas": ("cuneta", ("id", "prog_ini", "prog_fin", "pendiente")), "alcantarillas": ("alcantarilla", ("id", "prog")),
          "badenes": ("badén", ("id", "prog"))}
NOMBRES = {"id": "código", "prog_ini": "progresiva inicial", "prog_fin": "progresiva final", "pendiente": "pendiente (m/m)",
           "prog": "progresiva", "L_m": "longitud del cauce L (m)", "H_m": "desnivel de la cuenca H (m)"}


def _num(v):
    try: return float(v)
    except (TypeError, ValueError): return None


def revisar_datos(d):
    """Mensajes en español por cada dato que falte o no sea número."""
    falta = []
    for grupo, (nombre, campos) in CAMPOS.items():
        for i, x in enumerate(d.get(grupo, [])):
            cod = x.get("id") or i + 1
            area = _num(x.get("area_km2") or 0)
            if area is None: falta.append("%s %s: el área de la cuenca no es un número (%r)" % (nombre, cod, x.get("area_km2"))); area = 0
            req = list(campos) + (["L_m", "H_m"] if grupo != "cunetas" and area > 0 else [])
            for k in req:
                v = x.get(k)
                if v in (None, ""): falta.append("%s %s: falta %s" % (nombre, cod, NOMBRES[k]))
                elif k != "id" and _num(v) is None: falta.append("%s %s: %s no es un número (%r)" % (nombre, cod, NOMBRES[k], v))
                elif k in ("L_m", "H_m") and _num(v) <= 0: falta.append("%s %s: %s debe ser mayor que cero" % (nombre, cod, NOMBRES[k]))
        ids = [x.get("id") for x in d.get(grupo, [])]
        for k in sorted({str(k) for k in ids if ids.count(k) > 1}): falta.append("%s %s repetida" % (nombre, k))
    if falta: raise ValueError("Revise los datos del drenaje vial: " + "; ".join(falta) + ".")


def calcular(d, base="."):
    revisar_datos(d)
    via = d.get("via", {}); avisos = []
    lluvia = Lluvia(d.get("lluvia", {}), base)
    tc_norma = float(via.get("tc_min", normas.dato("tc_min")["valor"]))
    Pp = periodo("plataforma", via)
    cun = [cuneta(c, via, lluvia, Pp["T"], avisos) for c in d.get("cunetas", [])]
    alcs = list(d.get("alcantarillas", []))
    bads = [dict(b) for b in d.get("badenes", [])]
    usadas = asignar_descargas(cun, alcs + bads)
    if via.get("alivios_automaticos", True):              # una alcantarilla de alivio en cada descarga de cuneta que no tenga obra
        k = 0
        for c in cun:
            for i, s in enumerate(c["tramos"]):
                if (c["id"], i) in usadas: continue
                k += 1
                alcs.append({"id": "AL-%02d" % k, "prog": s["descarga_en"], "tipo": "alivio", "automatica": True,
                             "_recibe": [(c["id"], s["Q"], s["descarga_en"])],
                             "pendiente": via.get("pendiente_alivio", 0.02), "longitud_m": via.get("longitud_alivio_m", 0)})
    alc = sorted((alcantarilla(x, via, lluvia, tc_norma, avisos) for x in alcs), key=lambda a: a["prog"])
    bad = [baden(x, via, lluvia, tc_norma, avisos) for x in bads]
    reg, _ = region(via.get("precipitacion_anual_mm", 2000))
    tot = {"cunetas_m": round(sum(c["longitud"] for c in cun), 2), "alcantarillas": len(alc),
           "alivios": sum(1 for a in alc if a["tipo"] == "alivio"), "cruces": sum(1 for a in alc if a["tipo"] != "alivio"),
           "badenes": len(bad),
           "no_cumplen": sum(1 for x in cun + alc + bad if x["estado"] == "NO CUMPLE"),
           "revisar": sum(1 for x in cun + alc + bad if x["estado"] == "REVISAR")}
    return {"accion": "vial", "norma": normas.cita_larga("vial_racional").split(",")[0], "proyecto": d.get("proyecto", {}),
            "lluvia": {"fuente": lluvia.fuente, "estacion": lluvia.estacion,
                       "P24_por_T": {str(t): round(lluvia.P24(t), 2) for t in sorted({Pp["T"]} | {a["periodo"]["T"] for a in alc} |
                                                                                    {b["periodo"]["T"] for b in bad})}},
            "via": via, "region": reg, "tc_min_norma": tc_norma, "periodo_plataforma": Pp, "cunetas": cun, "alcantarillas": alc,
            "badenes": bad, "totales": tot, "avisos": avisos}
