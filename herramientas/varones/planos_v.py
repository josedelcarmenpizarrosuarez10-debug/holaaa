"""Planos DXF del colector pluvial frontal del CAR Varones (CUI 2705619) y su empalme con la caja CL del
Hogar de Refugio Temporal (CUI 2675514).

Laminas propias: DP-01 (planta 1/200), DP-02 (perfil 1/50 en tres franjas), DP-07 (empalme con la CL 1/20).
Laminas reutilizadas de los modulos comunes con los parametros de Varones (compat.py): DP-04A/B (secciones),
DP-06B (registro), DP-06C (empalme de cunetas), DP-08 (acero y especificaciones), DA-01 a DA-03 (partidas),
DD-01 a DD-04 (detalles de registro, tapa, juntas y empalmes).
Escala real 1 unidad = 1 m; cada lamina en una zona del modelo.
"""
import os, sys, json, math
import numpy as np
from ezdxf.enums import TextEntityAlignment as TA
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
for p in (HERR, AQUI):
    if p not in sys.path: sys.path.insert(0, p)
import compat as C
import diseno_v as dz
import diseno as SOL
import dxf_base as B
import dxf_planta as DP
import dxf_secciones as DS
import dxf_cuadros as DQ
import dxf_detalles as DD
from dxf_planta import prog_txt, perfil_en, terreno_en, offset_poli, recortar

D = dz.D; DS_ = SOL.D
SALIDA = os.path.join(dz.SAL, "PLANOS_COLECTOR_PLUVIAL_CAR_VARONES.dxf")
LAMINAS = {}
# origen de la planta (la planta queda en coordenadas locales reales del plano de arquitectura de Solange)
F200 = 0.2
OX1 = 349150.0 - 40 * F200
OY1 = SOL.Y_CERCO - 330 * F200


def _pe(p, lateral):
    """Punto a `lateral` m del eje (positivo hacia el predio = norte) en la progresiva p."""
    x, y, az = dz.eje_local(p); a = math.radians(az)
    nx, ny = -math.sin(a), math.cos(a)
    if ny < 0: nx, ny = -nx, -ny
    return (x + lateral * nx, y + lateral * ny)


def _reg_en(R, p, tol=1.5):
    rs = [r["nombre"] for r in R["registros"] if abs(r["prog"] - p) < tol]
    return rs[0] if rs else None


# =============================================================================== DP-01 PLANTA
def dp01(doc, ox, oy, R, T, BP):
    lam = B.Lamina(doc, ox, oy, 200, "DP-01", "PLANTA DEL COLECTOR PLUVIAL",
                   "TRAMO CAR VARONES (0+000.00 - %s) - TRAZO, REGISTROS, LLEGADA DE CUNETAS Y EMPALME CON LA CAJA CL DEL HOGAR DE REFUGIO" % prog_txt(dz.P_FIN))
    f = lam.f
    xw0, xw1 = 349150.0, 349276.0
    win = (xw0, SOL.Y_CERCO - 16, xw1, SOL.Y_CERCO + 45)
    # --- base de arquitectura de Varones (trasladada al marco de Solange) y de Solange (oeste del lindero)
    for sg in BP["segmentos"]:
        for seg in recortar([(sg[0], sg[1]), (sg[2], sg[3])], win):
            lam.poli(seg, "ARQ-BASE")
    for t in BP["textos"]:
        if win[0] < t[0] < win[2] and win[1] < t[1] < win[3] and "OASIS" not in t[2]:
            lam.texto((t[0], t[1]), t[2], 1.6, "ARQ-TEXTO")
    BS = json.load(open(os.path.join(RAIZ, "entregables", "_calc", "base_planta.json"), encoding="utf8"))
    wins = (xw0, win[1], SOL.X_NE, win[3])
    for s in BS["arq"]:
        for seg in recortar(s["pts"], wins): lam.poli(seg, s["layer"])
    for seg in recortar(BS["lote_sur"], win): lam.poli(seg, "LINDERO")
    # cerco de Solange (existente) y linea de referencia del frente de Varones (no hay cerco perimetrico en Varones)
    lam.poli([(xw0, SOL.Y_CERCO), (SOL.X_NE, SOL.Y_CERCO)], "CERCO", ancho=0.08)
    lam.poli(dz.BORDE, "LINDERO")
    lam.linea((SOL.X_NE, SOL.Y_CERCO), (SOL.X_NE, SOL.Y_CERCO - 7.0), "LINDERO")
    # --- colector de Solange (referencia) y caja CL
    yS = SOL.Y_EJE; bS = DS_["b"]; beS = DS_["b_ext"]
    lam.poli([(SOL.X_NE, yS), (SOL.X_NE - 12, yS)], "EJE-COLECTOR")
    for d_ in (beS / 2, -beS / 2): lam.poli([(SOL.X_NE, yS + d_), (SOL.X_NE - 12, yS + d_)], "ARQ-BASE")
    xcl0, xcl1 = SOL.X_NE, dz.X_CL_ESTE; e = DS_["e_muro"]
    lam.rect(xcl0, yS - DS_["CL_ancho"] / 2 - e, xcl1, yS + DS_["CL_ancho"] / 2 + e, "CONCRETO", const_width=0.04)
    lam.rect(xcl0 + e, yS - DS_["CL_ancho"] / 2, xcl1 - e, yS + DS_["CL_ancho"] / 2, "CONCRETO-OCULTO")
    lam.bloque("REGISTRO-PLANTA", ((xcl0 + xcl1) / 2, yS), 1.0)
    lam.texto(((xcl0 + xcl1) / 2, yS - 1.1), "CL", 1.8, "REGISTRO", TA.MIDDLE_CENTER)
    # --- colector de Varones: eje, muros, losa
    E = [tuple(p) for p in dz.EJE]
    lam.poli(E, "EJE-COLECTOR")
    for d_, capa in ((D["b_ext"] / 2, "CONCRETO"), (-D["b_ext"] / 2, "CONCRETO")):
        lam.poli(offset_poli(E, d_), capa, ancho=0.04)
    for d_ in (D["b"] / 2, -D["b"] / 2): lam.poli(offset_poli(E, d_), "CONCRETO-OCULTO")
    # registros
    for rg in R["registros"]:
        if rg["nombre"] == "CL": continue
        p = rg["prog"]; c = dz.eje_local(p)
        lam.bloque("REGISTRO-PLANTA", c[:2], 1.0, rot=c[2])
        lam.texto(_pe(p, -1.3), rg["nombre"], 1.6, "REGISTRO", TA.MIDDLE_CENTER)
    # juntas cada 4 m
    p = 4.0
    while p < dz.P_FIN - 0.5:
        lam.linea(_pe(p, D["b_ext"] / 2 + 0.15), _pe(p, -D["b_ext"] / 2 - 0.15), "JUNTAS"); p += 4.0
    # cruce de camiones (porton)
    for z in R["zonas"]:
        pts = [_pe(z["p1"], D["b_ext"] / 2 + 0.1), _pe(z["p2"], D["b_ext"] / 2 + 0.1), _pe(z["p2"], -D["b_ext"] / 2 - 0.1), _pe(z["p1"], -D["b_ext"] / 2 - 0.1)]
        lam.poli(pts, "CRUCE-VEHICULAR", cerrada=True, ancho=0.03)
        lam.llamada(_pe((z["p1"] + z["p2"]) / 2, -D["b_ext"] / 2 - 0.1), (dz.CERCO[0][0] - 2.0, SOL.Y_CERCO + 24.0),
                    ["CRUCE DE CAMIONES CISTERNA %s - %s (porton de 5.78 m, unico ingreso vehicular):" % (prog_txt(z["p1"]), prog_txt(z["p2"])),
                     "losa e=0.25, muros e=0.15, doble marco 1/2\" @0.15; el colector arranca en el poste derecho del porton"], 1.6)
    # cunetas que llegan: se acortan hasta la cara del muro (lado predio); la del Eje 01 entra a la CL
    for k, c in enumerate(R["cunetas"]):
        p = c["prog"]; x, y = c["x"], c["y"]
        if c["entra_en"] == "colector":
            # la cuneta es una recta norte-sur (x = cte): termina en la cara del muro lado predio, sobre esa misma vertical
            cv = dz.cruce_vertical(x, D["b_ext"] / 2); corte = (x, cv[1]); ux, uy = 0.0, 1.0
            fin = (corte[0], corte[1] + 3.0)
            # tramo que se descuenta (desde el extremo dibujado hasta la cara del muro), en linea oculta
            lam.poli([(x, y), corte], "CUNETA-OCULTA")
            fl = (corte[0] + ux * 1.0, corte[1] + uy * 1.0); rot = math.degrees(math.atan2(-uy, -ux))
        else:
            corte = (x, SOL.Y_EJE + DS_["CL_ancho"] / 2 + e); ux, uy = 0.0, 1.0
            fin = (x, corte[1] + 3.0); lam.poli([(x, y), corte], "CUNETA-OCULTA")
            fl = (x, corte[1] + 1.0); rot = -90
        for d_ in (-0.30, 0.30): lam.poli([(corte[0] - uy * d_, corte[1] + ux * d_), (fin[0] - uy * d_, fin[1] + ux * d_)], "CUNETA")
        for d_ in (-0.20, 0.20): lam.poli([(corte[0] - uy * d_, corte[1] + ux * d_), (fin[0] - uy * d_, fin[1] + ux * d_)], "CUNETA-OCULTA")
        lam.bloque("SIMB-FLECHA", fl, 0.08, rot=rot, capa="FLUJO")
        reg = _reg_en(R, p) if c["entra_en"] == "colector" else "CL"
        txt_p = (fin[0] + 1.5, fin[1] + 3.2 + 2.6 * (k % 2))
        lam.llamada(fin, txt_p,
                    ["CUNETA EJE %s: 0.40 x %.2f, NCF %.2f, Q %.1f L/s" % (c["perfil"], c["H"], c["NCF"], c["Q"]),
                     ("entra al colector en %s (%s); se acorta %.2f m" % (prog_txt(p), reg, -c["ajuste_L"])) if c["entra_en"] == "colector"
                     else "entra a la caja CL por su muro norte; se acorta %.2f m" % (-c["ajuste_L"])], 1.6)
    # progresivas cada 10 m y puntos singulares
    for p in list(np.arange(0, dz.P_FIN, 10.0)) + [dz.ZONAS[0]["p2"], dz.P_QUIEBRE, dz.P_FIN]:
        a, b_ = _pe(p, -D["b_ext"] / 2 - 0.3), _pe(p, -D["b_ext"] / 2 - 1.2)
        lam.linea(a, b_, "PROGRESIVAS")
        lam.texto(_pe(p, -D["b_ext"] / 2 - 1.5), prog_txt(p), 1.5, "PROGRESIVAS", TA.TOP_CENTER, rot=dz.eje_local(p)[2] - 180)
    for p in (15, 35, 60, 85):
        lam.bloque("SIMB-FLECHA", _pe(p, 0), 0.12, rot=dz.eje_local(p)[2], capa="FLUJO")
    # quiebre, cruce del cerco y empalme
    lam.llamada(dz.eje_local(dz.P_QUIEBRE)[:2], (dz.eje_local(dz.P_QUIEBRE)[0] + 14.0, SOL.Y_CERCO - 9.0),
                ["QUIEBRE %s (registro RV-11): el colector deja la linea del frente y entra horizontal a la CL" % prog_txt(dz.P_QUIEBRE),
                 "tramo de empalme %s a %s bajo el piso exterior (+261.15), sin cerco" % (prog_txt(dz.P_QUIEBRE), prog_txt(dz.P_FIN))], 1.6)
    lam.llamada((dz.X_CL_ESTE, yS - 0.3), (dz.X_CL_ESTE + 8.0, SOL.Y_CERCO - 13.0),
                ["EMPALME %s: entrega a la caja de llegada CL del colector del Hogar de Refugio (CUI 2675514)" % prog_txt(dz.P_FIN),
                 "ventana 0.60 x 1.17 en el muro este de la CL, cota de fondo %.3f; la CL recibe %.1f + %.1f = %.1f L/s (ver DP-07)" % (dz.fondo(dz.P_FIN), R["Q"], R["Q_directo_CL"], R["Q_CL"])], 1.6)
    # textos de ubicacion
    xm = (dz.CERCO[0][0] + SOL.X_NE) / 2
    lam.texto((xm, SOL.Y_CERCO + 40), "CENTRO DE ACOGIDA RESIDENCIAL - VARONES (CUI 2705619) - FRENTE A LA CARRETERA OASIS", 2.2, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto((xm, SOL.Y_CERCO - 2.0), "CARRETERA OASIS", 2.4, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto((xm, SOL.Y_CERCO - 5.5), "COLECTOR CUBIERTO DE CONCRETO ARMADO b = 0.60 m, h = 0.70 a 1.17 m, S = 0.30 % - LOSA SUPERIOR A NIVEL DEL PISO TERMINADO +261.15", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto((SOL.X_NE - 8, SOL.Y_CERCO + 6), "HOGAR DE REFUGIO TEMPORAL (CUI 2675514)", 1.8, "ARQ-TEXTO", TA.MIDDLE_CENTER)
    lam.texto((SOL.X_NE - 8, SOL.Y_CERCO + 3.5), "piso terminado +260.60", 1.5, "ARQ-TEXTO", TA.MIDDLE_CENTER)
    # grilla UTM (cruces cada 25 m)
    E0, N0 = dz.local_a_utm(xm, SOL.Y_CERCO)
    for Eg in np.arange(math.floor((E0 - 90) / 25) * 25, E0 + 95, 25):
        for Ng in np.arange(math.floor((N0 - 60) / 25) * 25, N0 + 70, 25):
            x, y = dz.utm_a_local(Eg, Ng)
            if lam.ox + 30 * f < x < lam.ox + 820 * f and lam.oy + 245 * f < y < lam.oy + 575 * f:
                lam.linea((x - 1.5, y), (x + 1.5, y), "GRILLA"); lam.linea((x, y - 1.5), (x, y + 1.5), "GRILLA")
                lam.texto((x + 0.3, y + 0.3), "E %d" % Eg, 1.2, "GRILLA"); lam.texto((x + 0.3, y - 1.5), "N %d" % Ng, 1.2, "GRILLA")
    lam.bloque("SIMB-NORTE", lam.P(700, 540), f, rot=dz.AZ_FRENTE - 90)
    # cuadro de coordenadas
    filas = []
    for rg in R["registros"]:
        p = rg["prog"]; x, y, _ = dz.eje_local(p); Eu, Nu = dz.local_a_utm(x, y)
        filas.append([rg["nombre"], prog_txt(p), "%.3f" % Eu, "%.3f" % Nu, "%.3f" % dz.fondo(p), "%.3f" % D["NPT"], rg["nota"]])
    Eu, Nu = dz.local_a_utm(*dz.EJE[0]); filas.insert(0, ["0+000", prog_txt(0), "%.3f" % Eu, "%.3f" % Nu, "%.3f" % D["CF0"], "%.3f" % D["NPT"], "inicio: poste derecho del porton de camiones"])
    y_ = lam.tabla(32, 250, ["PUNTO", "PROGRESIVA", "ESTE", "NORTE", "COTA FONDO", "COTA TAPA", "OBSERVACION"], filas, [18, 20, 24, 26, 20, 20, 110], 1.6, 4.0, "CUADRO DE COORDENADAS DE REGISTROS Y EMPALME")
    lam.texto(lam.P(32, y_ - 4), "Coordenadas UTM WGS84 - Zona 18 Sur, en el mismo sistema del tramo del Hogar de Refugio (georreferenciado con el R-01 del CAR Mujeres y el azimut 49.54 del lindero). Verificar en campo.", 1.5, "TEXTOS-NOTAS")
    lam.leyenda(330, 250, [("linea2", "CONCRETO", "muro exterior del colector"), ("linea", "CONCRETO-OCULTO", "cara interior (bajo losa superior)"),
                           ("linea", "EJE-COLECTOR", "eje del colector"), ("bloque:REGISTRO-PLANTA", "REGISTRO", "registro de limpieza con tapa removible"),
                           ("linea", "JUNTAS", "junta de dilatacion cada 4.00 m"), ("rect", "CRUCE-VEHICULAR", "cruce de camiones cisterna (porton)"),
                           ("linea", "CUNETA", "cuneta de arquitectura (tramo que se construye)"), ("linea", "CUNETA-OCULTA", "tramo de cuneta que se descuenta"),
                           ("linea2", "CERCO", "cerco existente del Hogar de Refugio"), ("linea", "LINDERO", "linderos y linea de referencia del frente (sin cerco)"),
                           ("linea", "ARQ-BASE", "arquitectura (referencia)"), ("bloque:SIMB-FLECHA", "FLUJO", "sentido del flujo")], 1.7)
    lam.notas(500, 250, "NOTAS", [
        "1. Colector de concreto armado f'c=210 kg/cm2, cubierto, losa superior monolitica con los muros y al ras del piso terminado +261.15.",
        "2. El frente del CAR Varones no tiene cerco perimetrico: el colector va bajo el piso exterior, con su eje a 0.475 m de la linea de referencia del frente (limite de las areas exteriores del plano de arquitectura).",
        "3. Progresivas desde el poste derecho del porton de camiones (0+000, junto al Eje 09) crecientes hacia la caja CL del Hogar de Refugio.",
        "4. Registros con tapa removible al ras, en cada empalme de cuneta, en el quiebre y cada 12.00 m como maximo (11 und).",
        "5. Cotas en m.s.n.m. Fondo 260.20 (0+000) a %.3f (llegada a la CL), S = 0.30 %%; fondo de la CL 258.80 (caida %.2f m)." % (dz.fondo(dz.P_FIN), dz.fondo(dz.P_FIN) - D["CL_piso"]),
        "6. Las cunetas de los Ejes 09, 08, 06 y 04 entran por ventana en el muro lado predio; la del Eje 01 cae a la caja CL. El tramo",
        "   de cada cuneta que caia dentro del colector se descuenta en la partida de cunetas (%s m)." % C.DESC_TXT,
        "7. La caja CL es parte del expediente del Hogar de Refugio (CUI 2675514); su tapa queda en +261.15 (piso del CAR Varones).",
        "8. Perfil en DP-02, secciones en DP-04, registro en DP-06B, empalme de cunetas en DP-06C, empalme con la CL en DP-07, acero y especificaciones en DP-08.",
    ], 1.6)
    return lam


# =============================================================================== DP-02 PERFIL
ZB = 258.40    # cota base del dibujo del perfil


def perfil(lam, xmm, ymm, p1, p2, R, T, titulo=None, paso_tabla=5.0):
    """Corte longitudinal por el eje entre p1 y p2 a escala real (1 unidad = 1 m). Origen de papel (xmm, ymm) = (p1, ZB)."""
    f = lam.f; NPT = D["NPT"]; ef = D["e_fondo"]; es = D["e_solado"]; em = D["e_muro"]
    def X(p): return lam.ox + xmm * f + (p - p1)
    def Y(z): return lam.oy + ymm * f + (z - ZB)
    fz = dz.fondo
    ps = [e["p"] for e in R["perfil"] if p1 - 1e-6 <= e["p"] <= p2 + 1e-6]
    for z in R["zonas"]: ps += [z["p1"], z["p2"], z["p2"] - 1e-4, z["p2"] + 1e-4]
    ps = sorted(set([p1, p2] + [q for q in ps if p1 - 1e-6 <= q <= p2 + 1e-6]))
    regs = [rg for rg in R["registros"] if p1 - 1e-6 <= rg["prog"] <= p2 + 1e-6 and rg["nombre"] != "CL"]
    # agua
    na = [(X(p), Y(perfil_en(R, p, "NA"))) for p in ps]
    lam.relleno([(X(p), Y(fz(p))) for p in ps] + list(reversed(na)), "AGUA-RELLENO"); lam.poli(na, "AGUA")
    for p in np.arange(np.ceil(p1 / 10.0) * 10.0, p2 + 1e-6, 10.0):
        if p1 + 1.0 < p < p2 - 1.0: lam.bloque("SIMB-AGUA", (X(p), Y(perfil_en(R, p, "NA"))), f)
    # losa de fondo y solado
    fondo = [(X(p), Y(fz(p))) for p in ps]; fondo_inf = [(X(p), Y(fz(p) - ef)) for p in ps]
    lam.achurado(fondo + list(reversed(fondo_inf)), escala_mm=0.5); lam.poli(fondo, "CONCRETO"); lam.poli(fondo_inf, "CONCRETO")
    lam.poli([(X(p), Y(fz(p) - ef - es)) for p in ps], "SOLADO")
    lam.poli([(X(p1), Y(fz(p1) - ef - es - 0.02)), (X(p2), Y(fz(p2) - ef - es - 0.02))], "EXCAVACION")
    # losa superior con aberturas de registro (el techo cambia en el cruce de camiones)
    cortes = sorted([(rg["prog"] - 0.35, rg["prog"] + 0.35) for rg in regs]); a = p1; tramos = []
    for c1, c2 in cortes:
        if c1 > a: tramos.append((a, c1))
        a = c2
    if a < p2: tramos.append((a, p2))
    for a, b_ in tramos:
        qs = sorted(set([a, b_] + [q for q in ps if a < q < b_]))
        techo = [(X(q), Y(dz.techo(q))) for q in qs]
        lam.achurado([(X(a), Y(NPT)), (X(b_), Y(NPT))] + list(reversed(techo)), escala_mm=0.5)
        lam.poli(techo, "CONCRETO"); lam.linea((X(a), Y(NPT)), (X(a), Y(dz.techo(a))), "CONCRETO"); lam.linea((X(b_), Y(NPT)), (X(b_), Y(dz.techo(b_))), "CONCRETO")
    lam.poli([(X(p1), Y(NPT)), (X(p2), Y(NPT))], "TERRENO", ancho=0.35 * f)
    # registros
    for rg in regs:
        p = rg["prog"]; zt = dz.techo(p)
        for sgn in (-1, 1):
            xa, xb = sorted([X(p + sgn * 0.35), X(p + sgn * 0.50)])
            lam.rect(xa, Y(zt - 0.10), xb, Y(zt), "CONCRETO"); lam.achurado([(xa, Y(zt - 0.10)), (xb, Y(zt - 0.10)), (xb, Y(zt)), (xa, Y(zt))], escala_mm=0.5)
        lam.rect(X(p - 0.34), Y(NPT - 0.08), X(p + 0.34), Y(NPT), "REGISTRO-TAPA")
        lam.linea((X(p - 0.35), Y(NPT - 0.10)), (X(p - 0.35), Y(NPT)), "MARCO-METALICO"); lam.linea((X(p + 0.35), Y(NPT - 0.10)), (X(p + 0.35), Y(NPT)), "MARCO-METALICO")
        lam.linea((X(p), Y(NPT)), (X(p), Y(NPT) + 5 * f), "LLAMADAS")
        lam.texto((X(p) + 0.8 * f, Y(NPT) + 6 * f), "%s  %s" % (rg["nombre"], prog_txt(p)), 1.6, "REGISTRO", TA.LEFT, rot=90)
    # ventanas de cunetas (cara interior del muro lado predio)
    for c in R["cunetas"]:
        p = c["prog"]
        if c["entra_en"] != "colector" or not (p1 - 1e-6 <= p <= p2 + 1e-6): continue
        zt = dz.techo(p); zv = c["NCF_fin"]
        lam.rect(X(p - 0.20), Y(zv), X(p + 0.20), Y(zt), "CUNETA")
        lam.relleno([(X(p - 0.20), Y(zv)), (X(p + 0.20), Y(zv)), (X(p + 0.20), Y(zt)), (X(p - 0.20), Y(zt))], "ISO-CUNETA")
        lam.bloque("SIMB-FLECHA", (X(p), Y((zv + perfil_en(R, p, "NA")) / 2)), f * 0.7, rot=-90, capa="FLUJO")
        lam.texto((X(p) - 1.0 * f, Y(NPT) + 6 * f), "CUNETA EJE %s - NCF %.2f" % (c["perfil"], zv), 1.6, "CUNETA", TA.LEFT, rot=90)
        lam.texto((X(p) - 3.6 * f, Y(NPT) + 6 * f), "ventana 0.40 x %.2f (Q %.1f L/s)" % (zt - zv, c["Q"]), 1.4, "CUNETA", TA.LEFT, rot=90)
    # juntas
    for pj in np.arange(4.0, dz.P_FIN - 0.5, 4.0):
        if p1 < pj < p2:
            lam.linea((X(pj), Y(NPT)), (X(pj), Y(dz.techo(pj))), "JUNTAS"); lam.linea((X(pj), Y(fz(pj))), (X(pj), Y(fz(pj) - ef)), "JUNTAS")
            lam.texto((X(pj), Y(fz(pj) - ef) - 1.5 * f), "J", 1.3, "JUNTAS", TA.TOP_CENTER)
    # cruce de camiones
    for z in R["zonas"]:
        a, b_ = max(z["p1"], p1), min(z["p2"], p2)
        if a < b_:
            yb = Y(NPT) + 2.0 * f
            lam.linea((X(a), yb), (X(b_), yb), "CRUCE-VEHICULAR"); lam.linea((X(a), yb - 1.0 * f), (X(a), yb + 1.0 * f), "CRUCE-VEHICULAR"); lam.linea((X(b_), yb - 1.0 * f), (X(b_), yb + 1.0 * f), "CRUCE-VEHICULAR")
            lam.texto((X((a + b_) / 2), yb + 1.5 * f), "CRUCE DE CAMIONES: losa e=0.25, doble marco 1/2\"", 1.5, "CRUCE-VEHICULAR", TA.BOTTOM_CENTER)
    # quiebre y cruce del cerco
    if p1 < dz.P_QUIEBRE < p2:
        lam.linea((X(dz.P_QUIEBRE), Y(NPT) + 11 * f), (X(dz.P_QUIEBRE), Y(NPT) + 16 * f), "LLAMADAS")
        lam.texto((X(dz.P_QUIEBRE) + 0.8 * f, Y(NPT) + 17 * f), "QUIEBRE %s" % prog_txt(dz.P_QUIEBRE), 1.5, "TEXTOS", TA.LEFT, rot=90)
    # ---------- llegada a la caja CL de Solange (receptor) al final del tramo
    if p2 >= dz.P_FIN - 1e-6:
        e = DS_["e_muro"]; zp = D["CL_piso"]; Li = DS_["CL_largo"]; tCL = D["NPT_CL"]; eL = DS_["e_losa"]
        xf = X(dz.P_FIN); xi = xf + e; xo = xi + Li; xe = xo + e      # muro este (con ventana), interior, muro oeste (lindero), cara exterior oeste
        # fondo de la caja y muro bajo la ventana este
        lam.achurado([(xf, Y(zp - ef)), (xe, Y(zp - ef)), (xe, Y(zp)), (xf, Y(zp))], escala_mm=0.5)
        lam.achurado([(xf, Y(zp)), (xi, Y(zp)), (xi, Y(fz(dz.P_FIN) - ef)), (xf, Y(fz(dz.P_FIN) - ef))], escala_mm=0.5)
        lam.poli([(xf, Y(fz(dz.P_FIN) - ef)), (xi, Y(fz(dz.P_FIN) - ef)), (xi, Y(zp)), (xo, Y(zp)), (xo, Y(DS_["CF0"])), (xe, Y(DS_["CF0"]))], "CONCRETO")
        lam.poli([(xf, Y(zp - ef)), (xe, Y(zp - ef))], "CONCRETO"); lam.poli([(xf, Y(zp - ef - es)), (xe, Y(zp - ef - es))], "SOLADO")
        # muro oeste (lindero): bajo la ventana de salida a Solange y sobre ella (hasta la tapa 261.15); losa de la CL
        lam.achurado([(xo, Y(zp)), (xe, Y(zp)), (xe, Y(DS_["CF0"])), (xo, Y(DS_["CF0"]))], escala_mm=0.5)
        lam.achurado([(xo, Y(DS_["NPT"] - eL)), (xe, Y(DS_["NPT"] - eL)), (xe, Y(tCL)), (xo, Y(tCL))], escala_mm=0.5)
        lam.rect(xo, Y(DS_["NPT"] - eL), xe, Y(tCL), "CONCRETO")
        lam.achurado([(xf + 0.35, Y(tCL - eL)), (xo, Y(tCL - eL)), (xo, Y(tCL)), (xf + 0.35, Y(tCL))], escala_mm=0.5)
        lam.poli([(xf, Y(NPT)), (xf, Y(tCL)), (xo, Y(tCL)), (xo, Y(tCL - eL)), (xf + 0.35, Y(tCL - eL))], "CONCRETO")
        # ventana del muro este (cara de corte: el colector entra con su seccion 0.60 x h): muro de la CL sobre la ventana no hay (techo a 261.05)
        lam.linea((xf, Y(fz(dz.P_FIN))), (xf, Y(dz.techo(dz.P_FIN))), "CONCRETO-OCULTO")
        # registro de la CL
        lam.rect(xf + 0.35, Y(tCL - 0.08), xf + 0.35 + 0.68, Y(tCL), "REGISTRO-TAPA")
        # ventana de la cuneta Eje 01 en el muro norte (fondo de la vista)
        c01 = [c for c in R["cunetas"] if c["entra_en"] == "CL"]
        if c01:
            c = c01[0]; u = dz.X_CL_ESTE - c["x"]    # distancia desde la cara este
            lam.rect(xf + u - 0.20, Y(c["NCF_fin"]), xf + u + 0.20, Y(tCL - eL), "CUNETA")
            lam.relleno([(xf + u - 0.20, Y(c["NCF_fin"])), (xf + u + 0.20, Y(c["NCF_fin"])), (xf + u + 0.20, Y(tCL - eL)), (xf + u - 0.20, Y(tCL - eL))], "ISO-CUNETA")
            lam.texto((xf + u - 1.0 * f, Y(tCL) + 6 * f), "CUNETA EJE %s - NCF %.2f (entra a la CL)" % (c["perfil"], c["NCF_fin"]), 1.6, "CUNETA", TA.LEFT, rot=90)
        # colector de Solange (referencia) y su piso
        lam.rect(xe, Y(DS_["CF0"] - ef), xe + 0.9, Y(DS_["NPT"]), "ARQ-BASE"); lam.rect(xe, Y(DS_["CF0"]), xe + 0.9, Y(DS_["NPT"] - eL), "ARQ-BASE")
        lam.poli([(xe, Y(DS_["NPT"])), (xe + 0.9, Y(DS_["NPT"]))], "TERRENO", ancho=0.35 * f)
        # agua: caida libre a la poza y salida por Solange
        naf = perfil_en(R, dz.P_FIN, "NA"); NA_CL = R["caja_llegada"]["NA_CL"]
        agua = [(xf, Y(naf)), (xf + 0.35, Y(NA_CL + 0.12)), (xf + 0.7, Y(NA_CL)), (xe + 0.9, Y(NA_CL))]
        lam.relleno([(xf, Y(fz(dz.P_FIN)))] + [(xi, Y(fz(dz.P_FIN) - ef)), (xi, Y(zp)), (xo, Y(zp)), (xo, Y(DS_["CF0"])), (xe + 0.9, Y(DS_["CF0"]))] + list(reversed(agua)), "AGUA-RELLENO")
        lam.poli(agua, "AGUA")
        # llamadas y niveles
        lam.llamada((xi + 0.4, Y(zp)), (xf - 0.3, Y(zp - 0.55)), ["CAJA DE LLEGADA CL (Hogar de Refugio, CUI 2675514): interior %.2f x %.2f, piso %.2f" % (Li, DS_["CL_ancho"], zp),
                                                                 "tapa en +%.2f (piso del CAR Varones); colchon de agua NA %.3f" % (tCL, NA_CL)], 1.6, al=TA.RIGHT)
        lam.llamada((xe + 0.6, Y(DS_["NPT"] - eL / 2)), (xf - 0.6, Y(tCL + 1.15)), ["COLECTOR DEL HOGAR DE REFUGIO (referencia): b=0.80, fondo %.2f, losa +%.2f" % (DS_["CF0"], DS_["NPT"])], 1.6, al=TA.RIGHT)
        lam.llamada((xf + 0.05, Y((fz(dz.P_FIN) + dz.techo(dz.P_FIN)) / 2)), (xf - 0.6, Y(tCL + 0.8)), ["ventana 0.60 x %.2f en el muro este de la CL: el colector entra con su seccion completa" % (dz.techo(dz.P_FIN) - fz(dz.P_FIN))], 1.6, al=TA.RIGHT)
        lam.nivel((xo - 0.3, Y(zp)), zp, lado=-1); lam.nivel((xe + 0.4, Y(DS_["CF0"])), DS_["CF0"], texto="CF %.2f" % DS_["CF0"], lado=1)
        lam.nivel((xo - 0.1, Y(tCL)), tCL, texto="tapa CL +%.2f" % tCL, lado=-1); lam.nivel((xe + 0.4, Y(DS_["NPT"])), DS_["NPT"], texto="+%.2f" % DS_["NPT"], lado=1)
        lam.cota((xf, Y(zp)), (xf, Y(fz(dz.P_FIN))), -8, horizontal=False, texto="caida %.2f" % (fz(dz.P_FIN) - zp))
        lam.cota((xf, Y(zp - ef - es)), (xi, Y(zp - ef - es)), -6); lam.cota((xi, Y(zp - ef - es)), (xo, Y(zp - ef - es)), -6); lam.cota((xo, Y(zp - ef - es)), (xe, Y(zp - ef - es)), -6)
        lam.texto((xe, Y(tCL) + 1.5 * f), "LINDERO", 1.4, "LINDERO", TA.BOTTOM_CENTER, rot=90); lam.linea((xe, Y(zp - ef - es - 0.3)), (xe, Y(tCL + 0.5)), "LINDERO")
    # cotas de altura interior
    for pm in (p1 + 0.3 * (p2 - p1), p1 + 0.7 * (p2 - p1)):
        pm = min(pm, dz.P_FIN - 1.0)
        if any(abs(pm - rg["prog"]) < 1.0 for rg in regs) or any(abs(pm - c["prog"]) < 1.0 for c in R["cunetas"]): pm += 1.2
        lam.cota((X(pm), Y(fz(pm))), (X(pm), Y(dz.techo(pm))), 0, horizontal=False, texto="h=%.2f" % (dz.techo(pm) - fz(pm)))
    # terreno existente, niveles en extremos
    lam.poli([(X(t["p"]), Y(t["z"])) for t in T if p1 - 1e-6 <= t["p"] <= p2 + 1e-6], "TERRENO-EXISTENTE")
    for p in (p1, p2):
        lam.nivel((X(p), Y(fz(p))), fz(p), texto="CF %.3f" % fz(p), lado=1 if p == p1 else -1)
        if perfil_en(R, p, "NA") - fz(p) > 0.02:
            lam.nivel((X(p), Y(perfil_en(R, p, "NA"))), perfil_en(R, p, "NA"), texto="NA %.3f" % perfil_en(R, p, "NA"), lado=1 if p == p1 else -1)
    lam.nivel((X(p1 + (8.5 if p1 < 1 else 2.5)), Y(NPT)), NPT, texto="NPT +%.2f (losa superior = piso terminado)" % NPT)
    lam.texto((X(p1 + 1.0), Y(fz(p1 + 1.0)) - 4.5 * f), "S = %.2f %%" % (D["S"] * 100), 1.8, "TEXTOS", TA.LEFT)
    # escala vertical
    xs = X(p1)
    for z in np.arange(258.5, 261.51, 0.5):
        lam.linea((xs - 3 * f, Y(z)), (xs - 1 * f, Y(z)), "GUITARRA"); lam.texto((xs - 4 * f, Y(z)), "%.2f" % z, 1.4, "TEXTOS", TA.MIDDLE_RIGHT)
    lam.linea((xs - 1 * f, Y(ZB)), (xs - 1 * f, Y(261.6)), "GUITARRA")
    if titulo: lam.texto((X(p1), Y(261.6) + 30 * f), titulo, 3.0, "TITULOS")
    # guitarra
    sing_r = [r["prog"] for r in R["registros"] if p1 <= r["prog"] <= p2]
    sing = sorted(set(sing_r + [c["prog"] for c in R["cunetas"] if p1 <= c["prog"] <= p2 and all(abs(c["prog"] - q) > 1.2 for q in sing_r)]))
    reg = [round(v, 2) for v in np.arange(p1, p2 + 1e-6, paso_tabla)] + [p2]
    reg = [v for v in reg if all(abs(v - q) > 1.2 for q in sing)]
    cols = sorted(set(reg + sing))
    filas = ["PROGRESIVA", "TERRENO", "LOSA SUP. / NPT", "FONDO", "NIVEL AGUA", "ALTURA h", "PROF. EXCAV."]
    yt = Y(ZB) - 6 * f; dy = 6.0 * f
    for i, fnm in enumerate(filas):
        lam.texto((X(p1) - 4 * f, yt - (i + 0.5) * dy), fnm, 1.5, "TEXTOS", TA.MIDDLE_RIGHT)
        lam.linea((X(p1) - 30 * f, yt - i * dy), (X(p2), yt - i * dy), "GUITARRA")
    lam.linea((X(p1) - 30 * f, yt - len(filas) * dy), (X(p2), yt - len(filas) * dy), "GUITARRA")
    for p in cols:
        vals = [prog_txt(p), "%.3f" % terreno_en(T, p), "%.3f" % NPT, "%.3f" % fz(p), "%.3f" % perfil_en(R, p, "NA"),
                "%.2f" % (dz.techo(p) - fz(p)), "%.2f" % (terreno_en(T, p) - fz(p) + ef + es)]
        lam.linea((X(p), yt), (X(p), yt - len(filas) * dy), "GUITARRA"); lam.linea((X(p), Y(ZB)), (X(p), yt), "GUITARRA")
        for i, v in enumerate(vals):
            lam.texto((X(p), yt - (i + 0.5) * dy), v, 1.4, "PROGRESIVAS" if i == 0 else "TEXTOS", TA.MIDDLE_CENTER)
    return X, Y


def dp02(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 50, "DP-02", "PERFIL LONGITUDINAL DEL COLECTOR",
                   "ESCALA REAL 1/50 (H = V) - CORTE POR EL EJE EN TRES FRANJAS: NIVELES DE DISENO, PERFIL HIDRAULICO, REGISTROS, EMPALMES Y LLEGADA A LA CL (0+000.00 - %s)" % prog_txt(dz.P_FIN))
    L1, L2 = 36.0, 72.0
    perfil(lam, 72, 470, 0.0, L1, R, T, "FRANJA 1: %s A %s - CORTE POR EL EJE (ESC. 1/50, H = V)" % (prog_txt(0.0), prog_txt(L1)))
    perfil(lam, 72, 325, L1, L2, R, T, "FRANJA 2: %s A %s" % (prog_txt(L1), prog_txt(L2)))
    perfil(lam, 60, 180, L2, dz.P_FIN, R, T, "FRANJA 3: %s A %s - LLEGADA A LA CAJA CL DEL HOGAR DE REFUGIO" % (prog_txt(L2), prog_txt(dz.P_FIN)))
    lam.leyenda(32, 98, [("linea2", "TERRENO", "piso terminado / losa superior (NPT +261.15)"), ("linea", "TERRENO-EXISTENTE", "terreno existente (superficie topografica)"),
                         ("achurado", "CONCRETO-ACHURADO", "concreto armado cortado (losas, caja CL)"), ("linea", "SOLADO", "solado e=0.05 y limite de excavacion"),
                         ("relleno", "AGUA-RELLENO", "agua: nivel de diseno (Q = %.1f L/s al final)" % R["Q"]), ("rect", "REGISTRO-TAPA", "tapa de registro 0.68 x 0.68 x 0.08"),
                         ("relleno", "ISO-CUNETA", "ventana de llegada de cuneta 0.40 x H (cara interior del muro lado predio)"), ("linea", "JUNTAS", "junta de dilatacion cada 4.00 m"),
                         ("rect", "ARQ-BASE", "colector del Hogar de Refugio (referencia)")], 1.7)
    lam.notas(330, 98, "NOTAS", [
        "1. Corte longitudinal por el eje a escala real 1/50, horizontal = vertical. Cotas en m.s.n.m. Se ve la cara interior del muro lado predio con las ventanas de las cunetas.",
        "2. Nivel de agua por flujo gradualmente variado con caudal creciente en cada empalme (memoria, hoja PERFIL_FLUJO); control: tirante critico en la caida libre a la caja CL.",
        "3. Caudales: %s = %.1f L/s en el colector; la cuneta del Eje 01 (%.1f L/s) entra directamente a la CL: total %.1f L/s (TR 25 anos)." % (" + ".join("Eje %s %.1f" % (c["perfil"], c["Q"]) for c in R["cunetas"] if c["entra_en"] == "colector"), R["Q"], R["Q_directo_CL"], R["Q_CL"]),
        "4. Registros con tapa de concreto 0.68 x 0.68 x 0.08, borde engrosado y contramarco metalico (DP-06B, DD-01, DD-02). No hay registros dentro del cruce de camiones.",
        "5. La caja CL y el colector del Hogar de Refugio (CUI 2675514) se muestran como referencia; la tapa de la CL queda en +261.15 (piso del CAR Varones).",
        "6. Prof. excav. medida desde el terreno existente al fondo del solado. Relleno de nivelacion del retiro hasta +261.15 donde el terreno queda por debajo.",
    ], 1.6)
    return lam


# =============================================================================== DP-07 EMPALME CON LA CL
def dp07(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 20, "DP-07", "EMPALME DEL COLECTOR CON LA CAJA DE LLEGADA CL DEL HOGAR DE REFUGIO",
                   "PLANTA Y CORTES DEL EMPALME: VENTANA ESTE 0.60 x 1.17, VENTANA NORTE PARA LA CUNETA EJE 01, JUNTAS Y NIVELES - ESC. 1/20")
    f = lam.f; e = DS_["e_muro"]; Li, Bi = DS_["CL_largo"], DS_["CL_ancho"]; zp = D["CL_piso"]; tCL = D["NPT_CL"]; eL = DS_["e_losa"]
    ef = D["e_fondo"]; es = D["e_solado"]; em = D["e_muro"]; b = D["b"]; be = D["b_ext"]
    cf = dz.fondo(dz.P_FIN); zt = dz.techo(dz.P_FIN); NA_CL = R["caja_llegada"]["NA_CL"]; naf = perfil_en(R, dz.P_FIN, "NA")
    c01 = [c for c in R["cunetas"] if c["entra_en"] == "CL"][0]; u01 = c01["x"] - SOL.X_NE   # posicion de la cuneta Eje 01 desde el lindero
    # ---------------- A. PLANTA (losa superior retirada). u = este (+), v = norte (+); origen = esquina (lindero, eje)
    o = lam.P(170, 445)
    def Pp(u, v): return (o[0] + u, o[1] + v)
    uE = Li + 2 * e        # cara este de la CL (1.80)
    # CL
    lam.rect(*Pp(0, -Bi / 2 - e), *Pp(uE, Bi / 2 + e), "CONCRETO", const_width=0.006); lam.rect(*Pp(e, -Bi / 2), *Pp(uE - e, Bi / 2), "CONCRETO")
    for pts in ([Pp(0, -Bi / 2 - e), Pp(uE, -Bi / 2 - e), Pp(uE, -Bi / 2), Pp(0, -Bi / 2)], [Pp(0, Bi / 2), Pp(uE, Bi / 2), Pp(uE, Bi / 2 + e), Pp(0, Bi / 2 + e)]):
        lam.achurado(pts, escala_mm=0.5)
    # muro este con ventana del colector (0.60) ; muro oeste con ventana de Solange (0.80) ; muro norte con ventana Eje 01 (0.40)
    for (v1, v2) in ((-Bi / 2, -b / 2), (b / 2, Bi / 2)): lam.achurado([Pp(uE - e, v1), Pp(uE, v1), Pp(uE, v2), Pp(uE - e, v2)], escala_mm=0.5)
    for (v1, v2) in ((-Bi / 2, -DS_["b"] / 2), (DS_["b"] / 2, Bi / 2)): lam.achurado([Pp(0, v1), Pp(e, v1), Pp(e, v2), Pp(0, v2)], escala_mm=0.5)
    lam.rect(*Pp(uE - e, -b / 2), *Pp(uE, b / 2), "CONCRETO-OCULTO"); lam.rect(*Pp(0, -DS_["b"] / 2), *Pp(e, DS_["b"] / 2), "CONCRETO-OCULTO")
    lam.rect(*Pp(u01 - 0.20, Bi / 2), *Pp(u01 + 0.20, Bi / 2 + e), "CONCRETO-OCULTO")
    # colector de Varones llegando (3.0 m) con junta de tecnopor contra la CL
    jt = D["junta_cerco"]
    lam.rect(*Pp(uE + jt, -be / 2), *Pp(uE + 3.0, be / 2), "CONCRETO", const_width=0.006); lam.rect(*Pp(uE + jt, -b / 2), *Pp(uE + 3.0, b / 2), "CONCRETO")
    for (v1, v2) in ((-be / 2, -b / 2), (b / 2, be / 2)): lam.achurado([Pp(uE + jt, v1), Pp(uE + 3.0, v1), Pp(uE + 3.0, v2), Pp(uE + jt, v2)], escala_mm=0.5)
    DD.tecnopor(lam, [Pp(uE, -be / 2), Pp(uE + jt, -be / 2), Pp(uE + jt, be / 2), Pp(uE, be / 2)])
    lam.linea(Pp(uE + 3.0, 0), Pp(uE, 0), "EJE-COLECTOR"); lam.bloque("SIMB-FLECHA", Pp(uE + 2.2, 0), f, rot=180, capa="FLUJO")
    # colector de Solange saliendo (referencia, 2.0 m)
    lam.rect(*Pp(-2.0, -DS_["b_ext"] / 2), *Pp(0, DS_["b_ext"] / 2), "ARQ-BASE"); lam.rect(*Pp(-2.0, -DS_["b"] / 2), *Pp(0, DS_["b"] / 2), "ARQ-BASE")
    lam.bloque("SIMB-FLECHA", Pp(-1.3, 0), f, rot=180, capa="FLUJO")
    # cuneta Eje 01 llegando desde el norte (2.0 m) con tecnopor
    lam.rect(*Pp(u01 - 0.30, Bi / 2 + e + jt), *Pp(u01 + 0.30, Bi / 2 + e + 1.4), "CUNETA", const_width=0.006); lam.rect(*Pp(u01 - 0.20, Bi / 2 + e + jt), *Pp(u01 + 0.20, Bi / 2 + e + 1.4), "CUNETA")
    DD.tecnopor(lam, [Pp(u01 - 0.30, Bi / 2 + e), Pp(u01 + 0.30, Bi / 2 + e), Pp(u01 + 0.30, Bi / 2 + e + jt), Pp(u01 - 0.30, Bi / 2 + e + jt)])
    lam.bloque("SIMB-FLECHA", Pp(u01, Bi / 2 + e + 0.9), f, rot=-90, capa="FLUJO")
    # registro de la CL (tapa 0.68) y lindero
    lam.bloque("REGISTRO-PLANTA", Pp(uE / 2, 0), 1.0)
    lam.linea(Pp(0, -Bi / 2 - e - 1.2), Pp(0, Bi / 2 + e + 1.9), "LINDERO"); lam.texto(Pp(-0.05, Bi / 2 + e + 1.75), "LINDERO (x = 349162.00)", 1.5, "LINDERO", TA.RIGHT)
    # cortes
    for (u, v1, v2, nm) in ((uE + 2.3, -Bi / 2 - e - 0.5, Bi / 2 + e + 0.5, "B"),):
        lam.linea(Pp(u, v1), Pp(u, v2), "CORTES"); lam.texto(Pp(u + 0.05, v2 + 0.05), nm, 2.5, "CORTES"); lam.texto(Pp(u + 0.05, v1 - 0.25), nm, 2.5, "CORTES")
    lam.linea(Pp(-2.2, 0), Pp(-2.0, 0), "CORTES"); lam.linea(Pp(uE + 3.55, 0), Pp(uE + 3.75, 0), "CORTES")
    lam.texto(Pp(-2.5, 0.1), "A", 2.5, "CORTES"); lam.texto(Pp(uE + 3.8, 0.1), "A", 2.5, "CORTES")
    # cotas
    yc_ = -Bi / 2 - e - 0.45
    lam.cota(Pp(0, yc_), Pp(e, yc_), -6); lam.cota(Pp(e, yc_), Pp(uE - e, yc_), -6); lam.cota(Pp(uE - e, yc_), Pp(uE, yc_), -6); lam.cota(Pp(uE, yc_), Pp(uE + 3.0, yc_), -6, texto="llegada del colector")
    lam.cota(Pp(0, yc_), Pp(uE, yc_), -13, texto="%.2f" % uE)
    xc_ = -0.9
    lam.cota(Pp(xc_, -Bi / 2 - e), Pp(xc_, -Bi / 2), -6, horizontal=False); lam.cota(Pp(xc_, -Bi / 2), Pp(xc_, Bi / 2), -6, horizontal=False); lam.cota(Pp(xc_, Bi / 2), Pp(xc_, Bi / 2 + e), -6, horizontal=False)
    lam.cota(Pp(uE + 3.0, -b / 2), Pp(uE + 3.0, b / 2), 8, horizontal=False); lam.cota(Pp(uE + 3.0, -be / 2), Pp(uE + 3.0, be / 2), 14, horizontal=False)
    lam.cota(Pp(u01 - 0.20, Bi / 2 + e + 1.4), Pp(u01 + 0.20, Bi / 2 + e + 1.4), 5, texto="0.40"); lam.cota(Pp(0, Bi / 2 + e + 1.4), Pp(u01, Bi / 2 + e + 1.4), 11, texto="%.2f" % u01)
    lam.cota(Pp(uE - e, b / 2), Pp(uE - e, -b / 2), 0, horizontal=False, texto="0.60")
    # llamadas (a la derecha, ordenadas de arriba a abajo)
    xt = uE + 3.4
    # derecha: anclajes ordenados de arriba a abajo (las lineas no se cruzan)
    lam.llamada(Pp(u01 + 0.3, Bi / 2 + e + 1.1), Pp(xt, 2.05), ["cuneta Eje 01 (0.40 x 0.77, NCF 260.38): se acorta 2.77 m y entra a la CL", "por ventana 0.40 x %.2f en el muro norte (corte B-B)" % c01["H_ventana"]], 1.7)
    lam.llamada(Pp(u01 + 0.3, Bi / 2 + e + jt / 2), Pp(xt, 1.45), ["tecnopor 1\" entre la cuneta y la CL (junta)"], 1.7)
    lam.llamada(Pp(uE + jt / 2, be / 2), Pp(xt, 1.05), ["tecnopor 1\" entre el colector de Varones y la CL (muro este, todo el perimetro)"], 1.7)
    lam.llamada(Pp(uE - e / 2, b / 2 + 0.05), Pp(xt, 0.7), ["ventana 0.60 x %.2f en el muro este de la CL (de %.3f a %.2f):" % (zt - cf, cf, zt), "el colector entra con su seccion completa"], 1.7)
    lam.llamada(Pp(uE + 2.6, -be / 2), Pp(xt, -0.75), ["colector CAR Varones b=0.60, muros 0.15; tramo de empalme", "%s a %s (horizontal en planta)" % (prog_txt(dz.P_QUIEBRE), prog_txt(dz.P_FIN))], 1.7)
    # izquierda (lado Hogar de Refugio) y abajo
    lam.llamada(Pp(e / 2, -DS_["b"] / 2 - 0.08), Pp(-0.3, -1.75), ["salida al colector del Hogar de Refugio: ventana 0.80 x 1.40", "en el muro oeste (lindero), fondo %.2f" % DS_["CF0"]], 1.7, al=TA.RIGHT)
    lam.llamada(Pp(uE / 2, -0.3), Pp(uE / 2 + 0.4, -1.75), ["registro de la CL con tapa 0.68 x 0.68 al ras de +%.2f (piso del CAR Varones)" % tCL], 1.7)
    lam.titulo_vista(170 + 60, 445 - 115, "A. EMPALME CON LA CAJA CL - PLANTA", "ESC. 1/20 - losas superiores retiradas; norte hacia arriba del dibujo (sistema local del plano de arquitectura)", 200)
    # ---------------- B. CORTE A-A (por el eje, mirando al norte): Varones -> CL -> Solange
    o = lam.P(170, 150)
    def Pc(u, z): return (o[0] + u, o[1] + (z - 258.3))
    # colector de Varones (2.2 m)
    uV0 = uE + jt; uV1 = uE + 2.4
    lam.achurado([Pc(uV0, cf - ef), Pc(uV1, cf - ef), Pc(uV1, cf), Pc(uV0, cf)], escala_mm=0.5); lam.achurado([Pc(uV0, zt), Pc(uV1, zt), Pc(uV1, D["NPT"]), Pc(uV0, D["NPT"])], escala_mm=0.5)
    lam.poli([Pc(uV1, cf - ef), Pc(uV0, cf - ef), Pc(uV0, D["NPT"]), Pc(uV1, D["NPT"])], "CONCRETO", ancho=0.006); lam.linea(Pc(uV0, cf), Pc(uV1, cf), "CONCRETO"); lam.linea(Pc(uV0, zt), Pc(uV1, zt), "CONCRETO")
    lam.poli([Pc(uV0, cf - ef - es), Pc(uV1, cf - ef - es)], "SOLADO")
    # CL: fondo, muro este (bajo la ventana), muro oeste (bajo y sobre la ventana de Solange), losa con registro
    lam.achurado([Pc(0, zp - ef), Pc(uE, zp - ef), Pc(uE, zp), Pc(0, zp)], escala_mm=0.5)
    lam.achurado([Pc(uE - e, zp), Pc(uE, zp), Pc(uE, cf - ef), Pc(uE - e, cf - ef)], escala_mm=0.5)
    lam.achurado([Pc(0, zp), Pc(e, zp), Pc(e, DS_["CF0"]), Pc(0, DS_["CF0"])], escala_mm=0.5)
    lam.achurado([Pc(0, DS_["NPT"] - eL), Pc(e, DS_["NPT"] - eL), Pc(e, tCL), Pc(0, tCL)], escala_mm=0.5)
    lam.achurado([Pc(e, tCL - eL), Pc(uE / 2 - 0.35, tCL - eL), Pc(uE / 2 - 0.35, tCL), Pc(e, tCL)], escala_mm=0.5)
    lam.achurado([Pc(uE / 2 + 0.35, tCL - eL), Pc(uE, tCL - eL), Pc(uE, tCL), Pc(uE / 2 + 0.35, tCL)], escala_mm=0.5)
    lam.poli([Pc(0, zp - ef), Pc(uE, zp - ef), Pc(uE, cf - ef), Pc(uE - e, cf - ef), Pc(uE - e, zp), Pc(e, zp), Pc(e, DS_["CF0"]), Pc(0, DS_["CF0"])], "CONCRETO", ancho=0.006)
    lam.poli([Pc(0, DS_["NPT"] - eL), Pc(e, DS_["NPT"] - eL), Pc(e, tCL - eL), Pc(uE / 2 - 0.35, tCL - eL), Pc(uE / 2 - 0.35, tCL), Pc(0, tCL), Pc(0, DS_["NPT"] - eL)], "CONCRETO", ancho=0.006)
    lam.poli([Pc(uE / 2 + 0.35, tCL - eL), Pc(uE, tCL - eL), Pc(uE, zt), Pc(uE, tCL), Pc(uE / 2 + 0.35, tCL)], "CONCRETO", ancho=0.006)
    lam.linea(Pc(uE, zt), Pc(uE, tCL - eL), "CONCRETO")           # muro este sobre la ventana: 261.05 -> 261.05 (coincide con el techo; no hay dintel)
    lam.rect(*Pc(uE / 2 - 0.34, tCL - 0.08), *Pc(uE / 2 + 0.34, tCL), "REGISTRO-TAPA")
    lam.poli([Pc(0, zp - ef - es), Pc(uE, zp - ef - es)], "SOLADO")
    DD.tecnopor(lam, [Pc(uE, cf - ef), Pc(uV0, cf - ef), Pc(uV0, D["NPT"]), Pc(uE, D["NPT"])])
    # ventana Eje 01 en el muro norte (fondo)
    lam.rect(*Pc(u01 - 0.20, c01["NCF_fin"]), *Pc(u01 + 0.20, tCL - eL), "CUNETA")
    lam.relleno([Pc(u01 - 0.20, c01["NCF_fin"]), Pc(u01 + 0.20, c01["NCF_fin"]), Pc(u01 + 0.20, tCL - eL), Pc(u01 - 0.20, tCL - eL)], "ISO-CUNETA")
    # Solange (referencia)
    lam.rect(*Pc(-1.6, DS_["CF0"] - ef), *Pc(0, DS_["NPT"]), "ARQ-BASE"); lam.rect(*Pc(-1.6, DS_["CF0"]), *Pc(0, DS_["NPT"] - eL), "ARQ-BASE")
    lam.poli([Pc(-1.6, DS_["NPT"]), Pc(0, DS_["NPT"])], "TERRENO", ancho=0.3 * f); lam.poli([Pc(uE, D["NPT"]), Pc(uV1 + 0.6, D["NPT"])], "TERRENO", ancho=0.3 * f)
    lam.poli([Pc(uV1, D["NPT"]), Pc(uV1 + 0.6, D["NPT"])], "TERRENO", ancho=0.3 * f)
    # agua
    agua = [Pc(uV1, naf), Pc(uE, naf), Pc(uE - 0.3, NA_CL + 0.12), Pc(uE - 0.6, NA_CL), Pc(-1.6, NA_CL)]
    lam.relleno([Pc(uV1, cf), Pc(uE - e, cf), Pc(uE - e, zp), Pc(e, zp), Pc(e, DS_["CF0"]), Pc(-1.6, DS_["CF0"])] + list(reversed(agua)), "AGUA-RELLENO"); lam.poli(agua, "AGUA")
    lam.bloque("SIMB-AGUA", Pc(uV1 - 0.6, naf), f); lam.bloque("SIMB-AGUA", Pc(uE / 2, NA_CL), f)
    # niveles y cotas
    lam.nivel(Pc(uV1 + 0.3, D["NPT"]), D["NPT"], texto="NPT +%.2f (Varones)" % D["NPT"]); lam.nivel(Pc(-1.2, DS_["NPT"]), DS_["NPT"], texto="NPT +%.2f (Refugio)" % DS_["NPT"], lado=-1)
    lam.nivel(Pc(uV1 + 0.3, cf), cf, texto="CF %.3f" % cf); lam.nivel(Pc(-1.2, DS_["CF0"]), DS_["CF0"], texto="CF %.2f" % DS_["CF0"], lado=-1)
    lam.nivel(Pc(uE / 2, zp), zp, texto="piso CL %.2f" % zp); lam.nivel(Pc(uE / 2 + 0.5, NA_CL), NA_CL, texto="NA CL %.3f" % NA_CL)
    lam.nivel(Pc(uV1 + 0.3, naf), naf, texto="NA %.3f" % naf)
    lam.cota(Pc(0, zp - ef - es), Pc(e, zp - ef - es), -6); lam.cota(Pc(e, zp - ef - es), Pc(uE - e, zp - ef - es), -6); lam.cota(Pc(uE - e, zp - ef - es), Pc(uE, zp - ef - es), -6)
    lam.cota(Pc(uE + 1.2, cf), Pc(uE + 1.2, zt), 0, horizontal=False, texto="h=%.2f" % (zt - cf))
    lam.cota(Pc(uE, zp), Pc(uE, cf), 10, horizontal=False, texto="caida %.2f" % (cf - zp))
    lam.cota(Pc(0, DS_["CF0"]), Pc(0, DS_["NPT"] - eL), -8, horizontal=False, texto="1.40")
    lam.cota(Pc(-0.4, DS_["NPT"]), Pc(-0.4, tCL), -8, horizontal=False, texto="0.55")
    lam.cota(Pc(uE - e, zp), Pc(uE - e, tCL - eL), 0, horizontal=False, texto="%.2f" % (tCL - eL - zp))
    xt = uV1 + 1.4
    lam.llamada(Pc(uE / 2 + 0.2, tCL - eL / 2), Pc(xt, tCL + 0.55), ["losa de la CL e=0.10 con registro 0.68 x 0.68,", "tapa al ras de +%.2f (Hogar de Refugio, CUI 2675514)" % tCL], 1.7)
    lam.llamada(Pc(u01 + 0.15, (c01["NCF_fin"] + tCL - eL) / 2 + 0.1), Pc(xt, tCL + 0.05), ["ventana norte 0.40 x %.2f para la cuneta Eje 01" % c01["H_ventana"], "(NCF %.2f, caida libre %.2f m sobre el NA)" % (c01["NCF_fin"], c01["caida_libre"])], 1.7)
    lam.llamada(Pc(uE, (zt + cf) / 2 + 0.15), Pc(xt, tCL - 0.45), ["ventana este 0.60 x %.2f (%.3f a %.2f): coincide con la seccion" % (zt - cf, cf, zt), "del colector; sin dintel (techo de la CL en %.2f)" % (tCL - eL)], 1.7)
    lam.llamada(Pc(uV0 + jt / 2, cf + 0.15), Pc(xt, cf - 0.35), ["tecnopor 1\" en todo el contacto colector - CL"], 1.7)
    lam.llamada(Pc(uE - 0.45, NA_CL + 0.06), Pc(xt, cf - 0.85), ["caida libre %.2f m del fondo del colector al NA de la CL;" % (cf - NA_CL), "colchon de agua %.2f m sobre el piso" % (NA_CL - zp)], 1.7)
    lam.llamada(Pc(-0.05, (DS_["NPT"] + tCL) / 2), Pc(-1.5, tCL + 0.32), ["escalon de 0.55 m entre pisos (+261.15 Varones /", "+260.60 Refugio) en el lindero: cara oeste de la CL"], 1.7)
    lam.titulo_vista(170 + 60, 150 - 42, "B. CORTE A-A POR EL EJE (MIRANDO AL NORTE)", "ESC. 1/20 - colector CAR Varones (derecha) -> caja CL -> colector del Hogar de Refugio (izquierda, referencia)", 220)
    # ---------------- C. CORTE B-B (transversal por la CL, mirando al oeste): cuneta Eje 01 por el muro norte
    o = lam.P(600, 150)
    def Pt(v, z): return (o[0] + v, o[1] + (z - 258.3))     # v = norte (+) hacia la derecha
    vS, vN = -Bi / 2 - e, Bi / 2 + e
    lam.achurado([Pt(vS, zp - ef), Pt(vN, zp - ef), Pt(vN, zp), Pt(vS, zp)], escala_mm=0.5)
    lam.achurado([Pt(vS, zp), Pt(-Bi / 2, zp), Pt(-Bi / 2, tCL), Pt(vS, tCL)], escala_mm=0.5)
    lam.achurado([Pt(Bi / 2, zp), Pt(vN, zp), Pt(vN, c01["NCF_fin"] - 0.10), Pt(Bi / 2, c01["NCF_fin"] - 0.10)], escala_mm=0.5)
    lam.achurado([Pt(-Bi / 2, tCL - eL), Pt(Bi / 2, tCL - eL), Pt(Bi / 2, tCL), Pt(-Bi / 2, tCL)], escala_mm=0.5)
    lam.poli([Pt(vS, zp - ef), Pt(vN, zp - ef), Pt(vN, c01["NCF_fin"] - 0.10), Pt(Bi / 2, c01["NCF_fin"] - 0.10), Pt(Bi / 2, zp), Pt(-Bi / 2, zp), Pt(-Bi / 2, tCL - eL), Pt(Bi / 2, tCL - eL), Pt(Bi / 2, tCL), Pt(vS, tCL)], "CONCRETO", cerrada=True, ancho=0.006)
    lam.poli([Pt(vS, zp - ef - es), Pt(vN + 0.9, zp - ef - es)], "SOLADO")
    # ventana de salida a Solange en el muro oeste (fondo de la vista)
    lam.rect(*Pt(-DS_["b"] / 2, DS_["CF0"]), *Pt(DS_["b"] / 2, DS_["NPT"] - eL), "ARQ-BASE"); lam.texto(Pt(0, (DS_["CF0"] + DS_["NPT"] - eL) / 2), "salida al colector del Refugio 0.80 x 1.40", 1.4, "ARQ-TEXTO", TA.MIDDLE_CENTER)
    # cuneta Eje 01: fondo a NCF, muros 0.10, hasta NCT 261.15, con tecnopor contra la CL
    xq = vN + jt
    lam.poli([Pt(xq, c01["NCF_fin"] - 0.10), Pt(xq + 0.9, c01["NCF_fin"] - 0.10), Pt(xq + 0.9, D["NPT"]), Pt(xq + 0.8, D["NPT"]), Pt(xq + 0.8, c01["NCF_fin"]), Pt(xq, c01["NCF_fin"])], "CUNETA", ancho=0.006)
    lam.achurado([Pt(xq, c01["NCF_fin"] - 0.10), Pt(xq + 0.9, c01["NCF_fin"] - 0.10), Pt(xq + 0.9, c01["NCF_fin"]), Pt(xq, c01["NCF_fin"])], "TERRENO-ACHURADO", escala_mm=0.4)
    lam.achurado([Pt(xq + 0.8, c01["NCF_fin"]), Pt(xq + 0.9, c01["NCF_fin"]), Pt(xq + 0.9, D["NPT"]), Pt(xq + 0.8, D["NPT"])], "TERRENO-ACHURADO", escala_mm=0.4)
    DD.tecnopor(lam, [Pt(vN, c01["NCF_fin"] - 0.10), Pt(xq, c01["NCF_fin"] - 0.10), Pt(xq, D["NPT"]), Pt(vN, D["NPT"])])
    lam.linea(Pt(xq, c01["NCF_fin"] + 0.05), Pt(xq + 0.8, c01["NCF_fin"] + 0.05), "AGUA"); lam.bloque("SIMB-FLECHA", Pt(Bi / 2 - 0.2, c01["NCF_fin"] + 0.12), f * 0.8, rot=-135, capa="FLUJO")
    lam.relleno([Pt(-Bi / 2, zp), Pt(Bi / 2, zp), Pt(Bi / 2, NA_CL), Pt(-Bi / 2, NA_CL)], "AGUA-RELLENO"); lam.linea(Pt(-Bi / 2, NA_CL), Pt(Bi / 2, NA_CL), "AGUA"); lam.bloque("SIMB-AGUA", Pt(0, NA_CL), f)
    lam.poli([Pt(vS - 0.8, tCL), Pt(vS, tCL)], "TERRENO", ancho=0.3 * f); lam.poli([Pt(xq + 0.9, D["NPT"]), Pt(xq + 1.6, D["NPT"])], "TERRENO", ancho=0.3 * f)
    lam.nivel(Pt(vS - 0.5, tCL), tCL, texto="+%.2f" % tCL, lado=-1); lam.nivel(Pt(xq + 1.2, D["NPT"]), D["NPT"], texto="NCT +%.2f" % D["NPT"])
    lam.nivel(Pt(xq + 0.4, c01["NCF_fin"]), c01["NCF_fin"], texto="NCF %.2f" % c01["NCF_fin"]); lam.nivel(Pt(0.1, zp), zp, texto="piso %.2f" % zp); lam.nivel(Pt(0.1, NA_CL), NA_CL, texto="NA %.3f" % NA_CL)
    lam.cota(Pt(vS, zp - ef - es), Pt(-Bi / 2, zp - ef - es), -6); lam.cota(Pt(-Bi / 2, zp - ef - es), Pt(Bi / 2, zp - ef - es), -6); lam.cota(Pt(Bi / 2, zp - ef - es), Pt(vN, zp - ef - es), -6)
    lam.cota(Pt(xq, c01["NCF_fin"] - 0.10), Pt(xq + 0.8, c01["NCF_fin"] - 0.10), -6, texto="0.40")
    lam.cota(Pt(vN, c01["NCF_fin"]), Pt(vN, tCL - eL), 14, horizontal=False, texto="ventana %.2f" % c01["H_ventana"])
    lam.cota(Pt(vS - 0.3, zp), Pt(vS - 0.3, tCL - eL), -6, horizontal=False)
    xt = xq + 1.75
    lam.llamada(Pt(xq + 0.85, D["NPT"] - 0.1), Pt(xt, tCL + 0.75), ["cuneta Eje 01 (0.40 x 0.77) acortada 2.77 m:", "termina en la cara exterior del muro norte de la CL"], 1.7)
    lam.llamada(Pt(vN + jt / 2, (c01["NCF_fin"] + D["NPT"]) / 2 + 0.2), Pt(xt, tCL + 0.2), ["tecnopor 1\" entre la cuneta y la CL"], 1.7)
    lam.llamada(Pt(vN - e / 2, (c01["NCF_fin"] + tCL - eL) / 2 - 0.1), Pt(xt, tCL - 0.35), ["ventana 0.40 x %.2f en el muro norte (del NCF %.2f" % (c01["H_ventana"], c01["NCF_fin"]), "al techo %.2f); sin dintel adicional" % (tCL - eL)], 1.7)
    lam.llamada(Pt(Bi / 2 - 0.1, NA_CL), Pt(xt, NA_CL - 0.1), ["NA de la CL %.3f = NA en 0+000 del colector del Refugio;" % NA_CL, "caida libre de la cuneta %.2f m" % c01["caida_libre"]], 1.7)
    lam.titulo_vista(600 + 25, 150 - 42, "C. CORTE B-B POR LA CAJA CL (MIRANDO AL OESTE)", "ESC. 1/20", 200)
    # leyenda, cuadro y notas
    lam.leyenda(600, 565, [("achurado", "CONCRETO-ACHURADO", "concreto armado f'c=210 (CL: expediente del Hogar de Refugio)"), ("rect", "ARQ-BASE", "colector del Hogar de Refugio (referencia)"),
                           ("achurado", "TERRENO-ACHURADO", "cuneta de arquitectura (Eje 01)"), ("relleno", "ISO-CUNETA", "ventana de llegada de cuneta"), ("linea", "JUNTAS", "junta de tecnopor 1\""),
                           ("relleno", "AGUA-RELLENO", "agua (nivel de diseno)"), ("linea", "LINDERO", "lindero entre predios"), ("bloque:SIMB-FLECHA", "FLUJO", "sentido del flujo")], 1.7)
    filas = [["Colector CAR Varones", prog_txt(dz.P_FIN), "%.1f" % R["Q"], "%.3f" % cf, "ventana este 0.60 x %.2f" % (zt - cf), "%.2f" % (cf - NA_CL)],
             ["Cuneta Eje 01", "muro norte", "%.1f" % c01["Q"], "%.2f" % c01["NCF_fin"], "ventana norte 0.40 x %.2f" % c01["H_ventana"], "%.2f" % c01["caida_libre"]],
             ["TOTAL a la CL", "", "%.1f" % R["Q_CL"], "", "poza: piso %.2f, NA %.3f" % (zp, NA_CL), ""]]
    lam.tabla(600, 487, ["APORTE", "UBICACION", "Q (L/s)", "COTA FONDO", "VENTANA", "CAIDA LIBRE (m)"], filas, [38, 22, 16, 22, 48, 26], 1.6, 4.5, "CUADRO DE LLEGADAS A LA CAJA CL")
    lam.notas(600, 452, "NOTAS", [
        "1. La caja CL pertenece al expediente del Hogar de Refugio Temporal (CUI 2675514, lamina DP-07 de ese tramo); aqui se dibuja",
        "   para definir el empalme. Queda del lado del CAR Varones (x = 349162.00 a 349163.80), por eso su tapa esta en +261.15.",
        "2. Coordinacion entre expedientes: en la CL se dejan la ventana este 0.60 x %.2f (cota de fondo %.3f) y la ventana norte" % (zt - cf, cf),
        "   0.40 x %.2f (NCF %.2f). El CAR Varones entrega %.1f L/s (colector) + %.1f L/s (cuneta Eje 01) = %.1f L/s." % (c01["H_ventana"], c01["NCF_fin"], R["Q"], R["Q_directo_CL"], R["Q_CL"]),
        "3. Si la CL se construye antes que el colector de Varones, las ventanas se dejan tapadas con muro de ladrillo pandereta (sin",
        "   mortero de union a la CL) para retirarlo al empalmar; si se construye despues, el colector de Varones termina en tapon provisional.",
        "4. Juntas de tecnopor 1\" en todo el contacto entre estructuras de distinto expediente (colector - CL, cuneta - CL). No hay cerco perimetrico en el frente de Varones.",
        "5. El tramo de empalme %s a %s es horizontal en planta y mantiene la pendiente 0.30 %%; registro RV-11 en el quiebre." % (prog_txt(dz.P_QUIEBRE), prog_txt(dz.P_FIN)),
    ], 1.6)
    return lam


# =============================================================================== CONSTRUIR
def construir():
    R, T, BP = C.cargar()
    doc = B.nuevo_documento()
    lam = dp01(doc, OX1, OY1, R, T, BP); LAMINAS["DP-01"] = lam
    lam = dp02(doc, OX1 + 200, OY1, R, T); LAMINAS["DP-02"] = lam
    for lam in DS.dp04(doc, OX1, OY1 - 200, R, T): LAMINAS[lam.codigo] = lam
    lam = DS.dp06b(doc, OX1 + 70, OY1 - 200, R, T); LAMINAS[lam.codigo] = lam
    lam = DS.dp06c(doc, OX1 + 85, OY1 - 200, R, T); LAMINAS[lam.codigo] = lam
    lam = dp07(doc, OX1 + 100, OY1 - 200, R, T); LAMINAS[lam.codigo] = lam
    for lam in DQ.todas(doc, OX1, OY1 - 400, R, T): LAMINAS[lam.codigo] = lam
    for lam in DD.todas(doc, OX1, OY1 - 600, R, T): LAMINAS[lam.codigo] = lam
    os.makedirs(dz.CALC, exist_ok=True)
    doc.saveas(SALIDA)
    cajas = {k: (l.ox, l.oy, l.ox + 841 * l.f, l.oy + 594 * l.f) for k, l in LAMINAS.items()}
    json.dump(cajas, open(os.path.join(dz.CALC, "laminas.json"), "w"), indent=1)
    return SALIDA, cajas


def auditar(fn, cajas):
    """Entidades fuera de toda lamina (texto o vertices)."""
    import ezdxf
    doc = ezdxf.readfile(fn); fuera = {}
    def dentro(x, y):
        return any(x0 - 1e-6 <= x <= x1 + 1e-6 and y0 - 1e-6 <= y <= y1 + 1e-6 for (x0, y0, x1, y1) in cajas.values())
    for e in doc.modelspace():
        pts = []
        t = e.dxftype()
        if t == "LINE": pts = [e.dxf.start, e.dxf.end]
        elif t == "LWPOLYLINE": pts = list(e.get_points("xy"))
        elif t in ("TEXT", "INSERT"): pts = [e.dxf.insert]
        elif t == "CIRCLE": pts = [e.dxf.center]
        for p in pts:
            if not dentro(p[0], p[1]):
                fuera[t] = fuera.get(t, 0) + 1; break
    return fuera


if __name__ == "__main__":
    fn, cajas = construir()
    print(fn); [print(' ', k, [round(v, 2) for v in c]) for k, c in cajas.items()]
    print("fuera de lamina:", auditar(fn, cajas))
