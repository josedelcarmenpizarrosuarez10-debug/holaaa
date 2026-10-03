"""Datos de diseno, geometria y calculo hidraulico del colector pluvial frontal.

Tramo Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514).
Todas las cotas en m.s.n.m.; progresivas en m desde la caja de llegada (0+000,
limite con CAR Varones) creciendo hacia aguas abajo (limite con CAR Mujeres).

Coordenadas:
  * "locales": las del plano de arquitectura PLANTA GENERAL REFUGIO (DXF).
  * "UTM": WGS84 zona 18 Sur, obtenidas haciendo coincidir el registro R-01 del
    colector del CAR Mujeres (CUI 2717013) con la esquina sur-oeste del frente
    y el rumbo del lindero frontal (azimut 49.54 grados).  Ubicacion referencial.
"""
import json, math, os
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

# ----------------------------------------------------------------------------
# 1. DATOS
# ----------------------------------------------------------------------------
D = dict(
    proyecto="Hogar de Refugio Temporal Mujeres Violentadas",
    cui="2675514",
    receptor="CAR Mujeres (CUI 2717013)",
    aporte_externo="CAR Varones (CUI 2705619)",
    # hidrologia
    TR=25, P10=35.163, P20=41.816, tc=15, FS=1.15,
    A_refugio=7520.41, CA_refugio=6072.3596,     # C ponderado 0.8074
    A_varones=6752.06, CA_varones=5203.3213,     # C ponderado 0.7707
    Q_refugio=301.9, Q_varones=258.7,            # L/s (memorias HIDRO-CE040)
    # geometria del colector
    b=0.80, e_muro=0.15, e_fondo=0.15, e_losa=0.10, e_losa_camion=0.20,
    e_solado=0.05, n=0.015,
    NPT=260.60,                 # cara superior de la losa = piso terminado del frente
    CF0=259.10,                 # cota de fondo en 0+000 (caja de llegada)
    S=0.003,                    # pendiente del fondo
    junta_cerco=0.025,          # tecnopor 1" entre el muro y el cerco
    # criterios
    llenado_max=0.85, BL_min=0.05,
    # receptor (CAR Mujeres)
    CF_R01=258.72, NA_R01=259.062, b_wilma=1.50, NPT_wilma=259.25,
    # aporte externo (CAR Varones): cota de llegada supuesta
    CF_varones_sup=260.18,
    # caja de llegada CL (0+000) y caja de caida CC (empalme)
    CL_largo=1.50, CL_ancho=1.00, CL_poza=0.30,
    CC_transicion=0.0, CC_poza_largo=3.50, CC_poza_prof=0.40, CC_ancho=1.50,
)
D["b_ext"] = D["b"] + 2 * D["e_muro"]                     # 1.10
D["eje_desde_cerco"] = D["junta_cerco"] + D["e_muro"] + D["b"] / 2   # 0.575

# ----------------------------------------------------------------------------
# 2. GEOMETRIA EN PLANTA (coordenadas locales del plano de arquitectura)
# ----------------------------------------------------------------------------
X_NE, X_SO, Y_CERCO = 349162.00, 349090.98, 9281917.79   # cerco sur
Y_EJE = Y_CERCO - D["eje_desde_cerco"]                     # eje del colector
L_FRENTE = X_NE - X_SO                                     # 71.02
# R-01 de CAR Mujeres (hipotesis de ubicacion): sobre la prolongacion del lado
# oeste del cerco, 0.75 m dentro del lindero frontal (lindero local y=9281910.8)
R01_LOCAL = (X_SO, 9281911.50)
RECTA_FINAL = 6.50                      # tramo recto paralelo al frente antes de R-01 (3.0 colector + 3.5 poza)
DY_DIAG = Y_EJE - R01_LOCAL[1]          # 5.715
X_B2 = X_SO + RECTA_FINAL               # quiebre 2
X_B1 = X_B2 + DY_DIAG                   # quiebre 1 (diagonal a 45 grados)
P_B1 = X_NE - X_B1
L_DIAG = DY_DIAG * math.sqrt(2)
P_B2 = P_B1 + L_DIAG
P_FIN = P_B2 + RECTA_FINAL              # cara aguas arriba de R-01 (0+000 de CAR Mujeres)
P_BRINK = P_FIN - D["CC_poza_largo"]    # fin de la transicion / inicio de la poza
P_TRANS = P_BRINK - D["CC_transicion"]  # inicio de la transicion 0.80 -> 1.50


def eje_local(p):
    """(x, y, azimut local en grados desde +x antihorario) del eje en la progresiva p."""
    if p <= P_B1:
        return (X_NE - p, Y_EJE, 180.0)
    if p <= P_B2:
        d = (p - P_B1) / math.sqrt(2)
        return (X_B1 - d, Y_EJE - d, 225.0)
    return (X_B2 - (p - P_B2), R01_LOCAL[1], 180.0)


# transformacion local -> UTM (WGS84 18S): rotacion + traslacion
R01_UTM = (345666.974, 9282776.560)
AZ_FRENTE = 49.54                      # azimut del lindero/colector de CAR Mujeres en R-01
ANG = math.radians(90.0 - AZ_FRENTE)   # giro antihorario de +x local al rumbo NE
_c, _s = math.cos(ANG), math.sin(ANG)


def local_a_utm(x, y):
    dx, dy = x - R01_LOCAL[0], y - R01_LOCAL[1]
    return (R01_UTM[0] + _c * dx - _s * dy, R01_UTM[1] + _s * dx + _c * dy)


def utm_a_local(E, N):
    dE, dN = E - R01_UTM[0], N - R01_UTM[1]
    return (R01_LOCAL[0] + _c * dE + _s * dN, R01_LOCAL[1] - _s * dE + _c * dN)


# ----------------------------------------------------------------------------
# 3. CUNETAS QUE LLEGAN (del plano de arquitectura, perfiles 01..12)
# ----------------------------------------------------------------------------
CUNETAS = [  # perfil, x local del eje, NCF al llegar, NCT, L cuneta
    dict(perfil="01", x=349160.93, NCF=260.12, NCT=260.60, L=37.14, nombre="Eje 01 (perimetral este)"),
    dict(perfil="02", x=349150.73, NCF=259.70, NCT=260.60, L=130.85, nombre="Eje 02 (estacionamiento)"),
    dict(perfil="06", x=349129.50, NCF=259.75, NCT=260.60, L=120.36, nombre="Eje 06 (ingreso vehicular)"),
    dict(perfil="07", x=349119.32, NCF=259.72, NCT=260.60, L=125.70, nombre="Eje 07"),
    dict(perfil="11", x=349101.11, NCF=260.00, NCT=260.60, L=71.46, nombre="Eje 11"),
    dict(perfil="12", x=349092.44, NCF=259.80, NCT=260.60, L=109.12, nombre="Eje 12 (perimetral oeste)"),
]
for c in CUNETAS:
    c["prog"] = round(X_NE - c["x"], 2)
    c["ancho"] = 0.40
    c["H"] = round(c["NCT"] - c["NCF"], 2)
    # prolongacion necesaria fuera del cerco hasta el muro del colector
    x = c["x"]
    if x >= X_B1:                      # llega al tramo pegado al cerco
        c["prolong"] = round(D["junta_cerco"], 2)
    elif x >= X_B2:                    # tramo diagonal
        y_eje = Y_EJE - (X_B1 - x)
        c["prolong"] = round(Y_CERCO - (y_eje + D["b_ext"] / 2 / math.cos(math.pi / 4)), 2)
    else:                              # tramo final / caja de caida
        c["prolong"] = round(Y_CERCO - (R01_LOCAL[1] + D["CC_ancho"] / 2 + D["e_muro"]), 2)
    c["NCF_fin"] = round(c["NCF"] - 0.005 * c["prolong"], 3)

# ----------------------------------------------------------------------------
# 4. ZONAS DE CARGA (losa) y accesos
# ----------------------------------------------------------------------------
ACCESOS = [
    dict(nombre="Porton de motos (1.77 m)", x1=349121.07, x2=349122.84, tipo="MOTOS", holgura=0.115),
    dict(nombre="Ingreso vehicular OE-01 (4.415 m)", x1=349130.965, x2=349135.38, tipo="CAMION", holgura=0.30),
]
ZONAS = []
for a in ACCESOS:
    p1 = round(X_NE - a["x2"] - a["holgura"], 2)
    p2 = round(X_NE - a["x1"] + a["holgura"], 2)
    ZONAS.append(dict(tipo=a["tipo"], p1=p1, p2=p2, nombre=a["nombre"]))
ZONAS.sort(key=lambda z: z["p1"])


def zona(p):
    for z in ZONAS:
        if z["p1"] <= p < z["p2"]:
            return z["tipo"]
    return "NORMAL"


# ----------------------------------------------------------------------------
# 5. REGISTROS
# ----------------------------------------------------------------------------
REGISTROS = [
    dict(nombre="CL", prog=0.0, tipo="caja de llegada", nota="llegada de CAR Varones y cuneta Eje 01"),
    dict(nombre="RS-01", prog=11.27, tipo="registro", nota="empalme cuneta Eje 02"),
    dict(nombre="RS-02", prog=22.00, tipo="registro", nota="limpieza"),
    dict(nombre="RS-03", prog=32.50, tipo="registro", nota="empalme cuneta Eje 06"),
    dict(nombre="RS-04", prog=42.68, tipo="registro", nota="empalme cuneta Eje 07"),
    dict(nombre="RS-05", prog=52.00, tipo="registro", nota="limpieza"),
    dict(nombre="RS-06", prog=round(P_B1, 2), tipo="registro", nota="quiebre 1 (45 grados) y empalme cuneta Eje 11"),
    dict(nombre="RS-07", prog=round(P_B2, 2), tipo="registro", nota="quiebre 2 (45 grados)"),
    dict(nombre="CC", prog=round(P_BRINK, 2), tipo="caja de caida", nota="poza de disipacion y empalme cuneta Eje 12; entrega al R-01 de CAR Mujeres"),
]

# ----------------------------------------------------------------------------
# 6. HIDROLOGIA E HIDRAULICA
# ----------------------------------------------------------------------------
G = 9.81


def intensidad(tc, P10=D["P10"], P20=D["P20"]):
    bx = math.log(P20 / P10) / math.log(2)
    return P10 * (tc / 10) ** bx / (tc / 60)


def caudal(CA, I, FS=D["FS"]):
    return CA * I / 3.6e6 * FS * 1000.0   # L/s


def yn(Q, b, S, n=D["n"]):
    lo, hi = 1e-4, 5.0
    for _ in range(200):
        y = (lo + hi) / 2
        A = b * y; R = A / (b + 2 * y)
        if A * R ** (2 / 3) * math.sqrt(S) / n > Q: hi = y
        else: lo = y
    return (lo + hi) / 2


def yc(Q, b):
    return (Q * Q / (G * b * b)) ** (1 / 3)


def fondo(p):
    """Cota de fondo del colector (tramo b=0.80 y transicion)."""
    return D["CF0"] - D["S"] * p


def ancho(p):
    """Ancho interior en la progresiva p (transicion lineal 0.80 -> 1.50)."""
    return D["b"] if p <= P_BRINK else D["CC_ancho"]


def techo(p):
    """Cota inferior de la losa superior."""
    return D["NPT"] - (D["e_losa_camion"] if zona(p) == "CAMION" else D["e_losa"])


def paso_estandar(Q, estaciones, y_control):
    """Perfil de flujo subcritico, de aguas abajo hacia aguas arriba.

    estaciones: progresivas decrecientes; y_control: tirante en la primera.
    Devuelve lista de dict por estacion.
    """
    n = D["n"]; out = []
    p2 = estaciones[0]; y2 = y_control; b2 = ancho(p2); z2 = fondo(p2)
    V2 = Q / (b2 * y2); E2 = z2 + y2 + V2 ** 2 / (2 * G)
    Sf2 = (n * V2 / ((b2 * y2) / (b2 + 2 * y2)) ** (2 / 3)) ** 2
    out.append(dict(p=p2, z=z2, b=b2, y=y2, V=V2, Sf=Sf2))
    for p1 in estaciones[1:]:
        dx = p2 - p1; b1 = ancho(p1); z1 = fondo(p1)
        # resolver y1 subcritico: E1 = E2 + dx*(Sf1+Sf2)/2
        lo, hi = yc(Q, b1) * 1.001, 3.0
        for _ in range(100):
            y1 = (lo + hi) / 2
            V1 = Q / (b1 * y1)
            Sf1 = (n * V1 / ((b1 * y1) / (b1 + 2 * y1)) ** (2 / 3)) ** 2
            E1 = z1 + y1 + V1 ** 2 / (2 * G)
            f = E1 - (E2 + dx * (Sf1 + Sf2) / 2)
            if f > 0: hi = y1
            else: lo = y1
        y1 = (lo + hi) / 2; V1 = Q / (b1 * y1)
        Sf1 = (n * V1 / ((b1 * y1) / (b1 + 2 * y1)) ** (2 / 3)) ** 2
        out.append(dict(p=p1, z=z1, b=b1, y=y1, V=V1, Sf=Sf1))
        p2, y2, b2, z2, E2, Sf2 = p1, y1, b1, z1, z1 + y1 + V1 ** 2 / (2 * G), Sf1
    return out


def resalto(y1, V1):
    F1 = V1 / math.sqrt(G * y1)
    y2 = y1 / 2 * (math.sqrt(1 + 8 * F1 * F1) - 1)
    return F1, y2


def disenar():
    I = intensidad(D["tc"])
    Qv = caudal(D["CA_varones"], I); Qr = caudal(D["CA_refugio"], I)
    Q = (D["Q_varones"] + D["Q_refugio"]) / 1000.0      # 0.5606 m3/s, valores de las memorias
    res = dict(I=I, Q_varones_calc=Qv, Q_refugio_calc=Qr, Q=Q * 1000)
    res["yn"] = yn(Q, D["b"], D["S"]); res["yc"] = yc(Q, D["b"])
    res["V_n"] = Q / (D["b"] * res["yn"]); res["F_n"] = res["V_n"] / math.sqrt(G * res["yn"])
    # control aguas abajo: brink de la caida libre -> tirante critico en la seccion de 0.80
    # (la poza esta deprimida 0.30 bajo el fondo del receptor; el resalto queda ahogado por el tirante del receptor)
    bB = D["b"]; yc_b = yc(Q, bB); zB = fondo(P_BRINK)
    res["brink"] = dict(p=P_BRINK, z=zB, yc=yc_b, NA=zB + yc_b)
    # estaciones cada 1 m + puntos singulares
    est = sorted(set([round(x, 2) for x in np.arange(0, P_BRINK, 1.0)] + [P_BRINK, P_TRANS, P_B1, P_B2]
                     + [c["prog"] for c in CUNETAS] + [r["prog"] for r in REGISTROS if r["prog"] < P_BRINK]
                     + [z["p1"] for z in ZONAS] + [z["p2"] for z in ZONAS]), reverse=True)
    perfil = paso_estandar(Q, est, yc_b)
    for e in perfil:
        e["NA"] = e["z"] + e["y"]; e["F"] = e["V"] / math.sqrt(G * e["y"])
        e["techo"] = techo(e["p"]); e["h"] = e["techo"] - e["z"]
        e["llenado"] = e["y"] / e["h"]; e["BL"] = e["techo"] - e["NA"]
        e["zona"] = zona(e["p"]); e["ok"] = e["llenado"] <= D["llenado_max"] and e["BL"] >= D["BL_min"] and e["F"] < 1
    res["perfil"] = perfil[::-1]
    # poza de disipacion: caida desde el brink hasta el piso de la poza
    zp = D["CF_R01"] - D["CC_poza_prof"]
    dz = zB - zp
    E1 = dz + 1.5 * yc_b                     # energia en el brink respecto al piso de la poza
    # tirante al pie (energia conservada): y1 + V1^2/2g = E1
    lo, hi = 1e-3, yc_b
    for _ in range(100):
        y1 = (lo + hi) / 2
        f = y1 + (Q / (bB * y1)) ** 2 / (2 * G) - E1
        if f > 0: lo = y1
        else: hi = y1
    V1 = Q / (bB * y1); F1, y2 = resalto(y1, V1)   # resalto en el ancho del colector (conservador: sin expansion)
    NA_aguas_abajo = D["NA_R01"]
    res["poza"] = dict(z_piso=zp, caida=dz, y1=y1, V1=V1, F1=F1, y2=y2, tirante_disp=NA_aguas_abajo - zp,
                       ok=NA_aguas_abajo - zp >= y2, L_resalto=6 * y2, L_poza=D["CC_poza_largo"],
                       Q_wilma_0=626.1)
    # caja de llegada: caida de CAR Varones
    zCL = D["CF0"] - D["CL_poza"]
    hcl = D["CF_varones_sup"] - zCL
    res["caja_llegada"] = dict(z_piso=zCL, caida=hcl, NA_salida=res["perfil"][0]["NA"],
                               tirante_poza=res["perfil"][0]["NA"] - zCL)
    # cunetas: holgura entre su fondo y el nivel de agua del colector
    for c in CUNETAS:
        e = min(perfil, key=lambda e: abs(e["p"] - c["prog"]))
        c["NA_colector"] = e["NA"]; c["caida_libre"] = round(c["NCF_fin"] - e["NA"], 3)
    res["cunetas"] = CUNETAS
    res["registros"] = REGISTROS; res["zonas"] = ZONAS
    res["geom"] = dict(X_NE=X_NE, X_SO=X_SO, Y_CERCO=Y_CERCO, Y_EJE=Y_EJE, L_FRENTE=L_FRENTE,
                       R01_LOCAL=R01_LOCAL, X_B1=X_B1, X_B2=X_B2, P_B1=P_B1, P_B2=P_B2, L_DIAG=L_DIAG,
                       P_TRANS=P_TRANS, P_BRINK=P_BRINK, P_FIN=P_FIN, RECTA_FINAL=RECTA_FINAL,
                       AZ_FRENTE=AZ_FRENTE, R01_UTM=R01_UTM)
    res["datos"] = D
    return res


def guardar(res, fn=os.path.join(RAIZ, "entregables", "_calc", "diseno.json")):
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, "w", encoding="utf8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=float)
    return fn


if __name__ == "__main__":
    r = disenar()
    print("I = %.2f mm/h  Q = %.1f L/s (Varones %.1f + Refugio %.1f calc.)" % (r["I"], r["Q"], r["Q_varones_calc"], r["Q_refugio_calc"]))
    print("yn = %.3f  yc = %.3f  V = %.2f  F = %.2f" % (r["yn"], r["yc"], r["V_n"], r["F_n"]))
    print("Quiebres: B1 0+%06.2f  B2 0+%06.2f  transicion 0+%06.2f  brink 0+%06.2f  R-01 0+%06.2f" % (P_B1, P_B2, P_TRANS, P_BRINK, P_FIN))
    print("Zonas:", ZONAS)
    print("%8s %8s %6s %6s %7s %5s %5s %5s %6s %7s" % ("prog", "fondo", "b", "y", "NA", "V", "F", "h", "y/h", "BL"))
    for e in r["perfil"]:
        if abs(e["p"] - round(e["p"] / 5) * 5) < 0.01 or e["p"] in (P_TRANS, P_BRINK, P_B1, P_B2):
            print("%8.2f %8.3f %6.2f %6.3f %7.3f %5.2f %5.2f %5.2f %6.2f %7.3f %s %s" % (e["p"], e["z"], e["b"], e["y"], e["NA"], e["V"], e["F"], e["h"], e["llenado"], e["BL"], e["zona"], "OK" if e["ok"] else "NO"))
    print("Poza:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r["poza"].items()})
    print("Caja llegada:", {k: round(v, 3) for k, v in r["caja_llegada"].items()})
    for c in CUNETAS:
        print("  cuneta %s prog %6.2f NCF %.2f prolong %.2f NA colector %.3f caida libre %.3f" % (c["perfil"], c["prog"], c["NCF"], c["prolong"], c["NA_colector"], c["caida_libre"]))
    print(guardar(r))
