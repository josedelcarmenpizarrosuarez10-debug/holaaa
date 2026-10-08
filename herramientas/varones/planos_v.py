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
import dxf_layouts as L
from dxf_planta import prog_txt, perfil_en, terreno_en, offset_poli, recortar

D = dz.D; DS_ = SOL.D
SALIDA = os.path.join(dz.SAL, "PLANOS_COLECTOR_PLUVIAL_CAR_VARONES.dxf")
from collections import OrderedDict
LAMINAS = OrderedDict()
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
                   "0+000.00 - %s: TRAZO, REGISTROS, CUNETAS Y EMPALME CON LA CAJA CL DEL HOGAR DE REFUGIO" % prog_txt(dz.P_FIN))
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
        izq = c["entra_en"] == "colector"
        dy = {"09": 3.0, "08": 6.0}.get(c["perfil"], 3.0)
        txt_p = (fin[0] - 1.0, fin[1] + dy) if izq else (fin[0] + 1.5, fin[1] + 3.0)
        lam.llamada(fin, txt_p, al=TA.RIGHT if izq else TA.LEFT, lineas=
                    ["CUNETA EJE %s: 0.40 x %.2f, NCF %.2f, Q %.1f L/s" % (c["perfil"], c["H"], c["NCF"], c["Q"]),
                     ("entra al colector en %s (%s); se acorta %.2f m" % (prog_txt(p), reg, -c["ajuste_L"])) if c["entra_en"] == "colector"
                     else "entra a la caja CL por su muro norte; se acorta %.2f m" % (-c["ajuste_L"])], hmm=1.6)
    # progresivas cada 10 m y puntos singulares
    for p in list(np.arange(0, dz.P_FIN, 10.0)) + [dz.ZONAS[0]["p2"], dz.P_QUIEBRE, dz.P_FIN]:
        a, b_ = _pe(p, -D["b_ext"] / 2 - 0.3), _pe(p, -D["b_ext"] / 2 - 1.2)
        lam.linea(a, b_, "PROGRESIVAS")
        lam.texto(_pe(p, -D["b_ext"] / 2 - 1.5), prog_txt(p), 1.5, "PROGRESIVAS", TA.TOP_CENTER, rot=dz.eje_local(p)[2] - 180)
    for p in (15, 35, 60, 85):
        lam.bloque("SIMB-FLECHA", _pe(p, 0), 0.12, rot=dz.eje_local(p)[2], capa="FLUJO")
    # quiebre, cruce del cerco y empalme
    lam.llamada(dz.eje_local(dz.P_QUIEBRE)[:2], (dz.eje_local(dz.P_QUIEBRE)[0] + 21.0, SOL.Y_CERCO - 5.5),
                ["QUIEBRE %s (registro RV-11): el colector deja la linea del frente y entra horizontal a la CL" % prog_txt(dz.P_QUIEBRE),
                 "tramo de empalme %s a %s bajo el piso exterior (+261.15), sin cerco" % (prog_txt(dz.P_QUIEBRE), prog_txt(dz.P_FIN))], 1.6)
    lam.llamada((dz.X_CL_ESTE, yS - 0.3), (dz.X_CL_ESTE + 2.5, SOL.Y_CERCO - 7.5),
                ["EMPALME %s: entrega a la caja de llegada CL del colector del Hogar de Refugio (CUI 2675514)" % prog_txt(dz.P_FIN),
                 "ventana 0.60 x 1.17 en el muro este de la CL, cota de fondo %.3f; la CL recibe %.1f + %.1f = %.1f L/s (ver DP-07)" % (dz.fondo(dz.P_FIN), R["Q"], R["Q_directo_CL"], R["Q_CL"])], 1.6)
    # textos de ubicacion
    xm = (dz.CERCO[0][0] + SOL.X_NE) / 2
    lam.texto((xm - 14.0, SOL.Y_CERCO + 40), "CENTRO DE ACOGIDA RESIDENCIAL - VARONES (CUI 2705619) - FRENTE A LA CARRETERA OASIS", 2.2, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto((xm, SOL.Y_CERCO - 2.0), "CARRETERA OASIS", 2.4, "TEXTOS", TA.MIDDLE_CENTER)
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
        filas.append([rg["nombre"], prog_txt(p), "%.3f" % Eu, "%.3f" % Nu, "%.3f" % dz.fondo(p), "%.3f" % D["NPT"],
                      "llegada a la caja CL del Hogar de Refugio (recibe la cuneta Eje 01)" if rg["nombre"] == "CL" else rg["nota"]])
    Eu, Nu = dz.local_a_utm(*dz.EJE[0]); filas.insert(0, ["0+000", prog_txt(0), "%.3f" % Eu, "%.3f" % Nu, "%.3f" % D["CF0"], "%.3f" % D["NPT"], "inicio: poste derecho del porton de camiones"])
    y_ = lam.tabla(32, 250, ["PUNTO", "PROGRESIVA", "ESTE", "NORTE", "COTA FONDO", "COTA TAPA", "OBSERVACION"], filas, [18, 20, 24, 26, 20, 20, 110], 1.6, 4.0, "CUADRO DE COORDENADAS DE REGISTROS Y EMPALME")
    lam.texto(lam.P(32, y_ - 4), "Coordenadas UTM WGS84 - Zona 18 Sur, en el mismo sistema del tramo del Hogar de Refugio (georreferenciado con el R-01 del CAR Mujeres y el azimut 49.54 del lindero). Verificar en campo.", 1.5, "TEXTOS-NOTAS")
    lam.leyenda2(330, 254, [("linea2", "CONCRETO", "muro exterior del colector"), ("linea", "CONCRETO-OCULTO", "cara interior (bajo losa superior)"),
                           ("linea", "EJE-COLECTOR", "eje del colector"), ("bloque:REGISTRO-PLANTA", "REGISTRO", "registro de limpieza con tapa removible"),
                           ("linea", "JUNTAS", "junta de dilatacion cada 4.00 m"), ("rect", "CRUCE-VEHICULAR", "cruce de camiones cisterna (porton)"),
                           ("linea", "CUNETA", "cuneta de arquitectura (tramo que se construye)"), ("linea", "CUNETA-OCULTA", "tramo de cuneta que se descuenta"),
                           ("linea2", "CERCO", "cerco existente del Hogar de Refugio"), ("linea", "LINDERO", "linderos y linea de referencia del frente (sin cerco)"),
                           ("linea", "ARQ-BASE", "arquitectura (referencia)"), ("bloque:SIMB-FLECHA", "FLUJO", "sentido del flujo")], hmm=1.7)
    lam.notas(478, 254, "NOTAS", [
        "1. Colector de concreto armado f'c=210 kg/cm2, cubierto, losa superior monolitica con los muros y al ras del piso terminado +261.15.",
        "2. El frente del CAR Varones no tiene cerco perimetrico: el colector va bajo el piso exterior, con su eje a 0.475 m de la linea de referencia del frente (limite de las areas exteriores del plano de arquitectura).",
        "3. Progresivas desde el poste derecho del porton de camiones (0+000, junto al Eje 09) crecientes hacia la caja CL del Hogar de Refugio.",
        "4. Registros con tapa removible al ras, en cada empalme de cuneta, en el quiebre y cada 12.00 m como maximo (11 und).",
        "5. Cotas en m.s.n.m. Fondo 260.20 (0+000) a %.3f (llegada a la CL), S = 0.30 %%; fondo de la CL 258.80 (caida %.2f m)." % (dz.fondo(dz.P_FIN), dz.fondo(dz.P_FIN) - D["CL_piso"]),
        "6. Las cunetas de los Ejes 09, 08, 06 y 04 entran por ventana en el muro lado predio; la del Eje 01 cae a la caja CL. El tramo",
        "   de cada cuneta que caia dentro del colector se descuenta en la partida de cunetas (%s m)." % C.DESC_TXT,
        "7. La caja CL es parte del expediente del Hogar de Refugio (CUI 2675514); su tapa queda en +261.15 (piso del CAR Varones).",
        "8. Perfiles en DP-02 (1/100) y DP-03A/B (1/25), secciones en DP-04, registro en DP-06B, empalme de cunetas en DP-06C, empalme con la CL en DP-07, acero en DP-08.",
    ], 1.7, ancho_mm=345)
    return lam


# =============================================================================== PERFILES: DP-02 (general 1/100) y DP-03A/B (detalle 1/25)
NARANJA = 30
TRAMOS_DP03 = [0.0, 17.9, 35.8, 53.7, 71.6, 89.5, None]      # el ultimo termina en la cara este de la CL (P_FIN)
TRAMOS_DP03[-1] = dz.P_FIN
L_CL = DS_["CL_largo"] + 2 * DS_["e_muro"]                    # largo exterior de la caja CL en el sentido del flujo (1.80)
L_REF = 0.90                                                 # tramo del colector del Hogar de Refugio dibujado como referencia


def _reg(R): return [r for r in R["registros"] if r["nombre"] != "CL"]


def _estaciones(R, p1, p2, paso, sep):
    """progresivas de la guitarra: extremos, registros, cambio de zona y cada `paso` m (se omite la que queda a menos de sep m)."""
    regs = [round(r["prog"], 2) for r in _reg(R)]
    fijos = [q for q in regs + [z["p2"] for z in R["zonas"]] + [p1, p2] if p1 - 1e-6 <= q <= p2 + 1e-6]
    out = []
    for q in sorted(set(round(v, 2) for v in fijos)):
        if all(abs(q - o) >= sep for o in out): out.append(q)
        elif q in regs: out = [o for o in out if abs(q - o) >= sep] + [q]
    if paso:
        k = math.ceil(p1 / paso) * paso
        while k <= p2 + 1e-6:
            if all(abs(k - o) >= sep for o in out): out.append(round(k, 2))
            k += paso
    return sorted(out)


def _zlim(R, T, p1, p2):
    pp = [p1 + (p2 - p1) * i / 40 for i in range(41)]
    zmin = min(dz.fondo(q) - D["e_fondo"] - D["e_solado"] for q in pp)
    if p2 >= dz.P_FIN - 1e-6: zmin = min(zmin, D["CL_piso"] - D["e_fondo"] - D["e_solado"])
    zmax = max(max(terreno_en(T, q) for q in pp), D["NPT"])
    return math.floor((zmin - 0.05) * 10) / 10, math.ceil((zmax + 0.05) * 10) / 10


def alto_perfil(R, T, p1, p2, f):
    a, b_ = _zlim(R, T, p1, p2); return (b_ - a) / f


def perfil(lam, xmm, ymm, p1, p2, R, T, detalle=True, titulo=None, paso=5.0, xmax_txt=None):
    """Corte longitudinal por el eje a escala real (H = V) entre p1 y p2. (xmm, ymm): papel en (p1, zmin del tramo);
    la guitarra va debajo y la franja de etiquetas (horizontales, sin cruces) encima. Devuelve el borde inferior (mm)."""
    f = lam.f; NPT = D["NPT"]; ef = D["e_fondo"]; es = D["e_solado"]
    zmin, zmax = _zlim(R, T, p1, p2)
    X = lambda p: lam.ox + xmm * f + (p - p1)
    Y = lambda z: lam.oy + ymm * f + (z - zmin)
    fz = dz.fondo
    zc = [z["p2"] for z in R["zonas"] if p1 < z["p2"] < p2]                     # cambio de espesor de la losa superior
    ps = sorted(set([p1, p2] + [e["p"] for e in R["perfil"] if p1 < e["p"] < p2] + zc))
    regs = [r for r in _reg(R) if p1 - 1e-6 <= r["prog"] <= p2 + 1e-6]
    ets = []
    # ---------- agua
    agua = [(X(q), Y(perfil_en(R, q, "NA"))) for q in ps]
    if any(perfil_en(R, q, "NA") - fz(q) > 0.005 for q in ps):
        lam.relleno(agua + [(X(q), Y(fz(q))) for q in reversed(ps)], "AGUA-RELLENO"); lam.poli(agua, "AGUA")
    # ---------- losa de fondo y solado
    pl = [(X(q), Y(fz(q))) for q in ps] + [(X(q), Y(fz(q) - ef)) for q in reversed(ps)]
    lam.relleno(pl, "CONCRETO-ACHURADO"); lam.poli(pl, "CONCRETO", cerrada=True)
    lam.poli([(X(q), Y(fz(q) - ef)) for q in ps] + [(X(q), Y(fz(q) - ef - es)) for q in reversed(ps)], "SOLADO", cerrada=True)
    # ---------- losa superior con el hueco de cada registro (0.70) y el escalon del cruce de camiones
    huecos = [(r["prog"] - 0.35, r["prog"] + 0.35) for r in regs]
    lim = [p1] + zc + [p2]
    for a, c in zip(lim[:-1], lim[1:]):
        segs = [(a, c)]
        for h1, h2 in huecos:
            nuevo = []
            for u, v in segs:
                if h2 <= u or h1 >= v: nuevo.append((u, v)); continue
                if u < h1: nuevo.append((u, h1))
                if h2 < v: nuevo.append((h2, v))
            segs = nuevo
        for u, v in segs:
            if v - u < 1e-3: continue
            m = (u + v) / 2; zt = dz.techo(m)
            pl = [(X(u), Y(NPT)), (X(v), Y(NPT)), (X(v), Y(zt)), (X(u), Y(zt))]
            lam.relleno(pl, "CONCRETO-ACHURADO"); lam.poli(pl, "CONCRETO", cerrada=True)
    # ---------- registros: borde engrosado 0.15 x 0.10 bajo la losa, contramarco y tapa 0.68 x 0.08
    for r in regs:
        q = r["prog"]; zt = dz.techo(q)
        for s_ in (-1, 1):
            xa, xb = sorted([q + s_ * 0.35, q + s_ * 0.50])
            pl = [(X(xa), Y(zt - 0.10)), (X(xb), Y(zt - 0.10)), (X(xb), Y(zt)), (X(xa), Y(zt))]
            lam.relleno(pl, "CONCRETO-ACHURADO"); lam.poli(pl, "CONCRETO", cerrada=True)
            if detalle: lam.linea((X(q + s_ * 0.35), Y(NPT - 0.10)), (X(q + s_ * 0.35), Y(NPT)), "MARCO-METALICO")
        tapa = [(X(q - 0.34), Y(NPT)), (X(q + 0.34), Y(NPT)), (X(q + 0.34), Y(NPT - 0.08)), (X(q - 0.34), Y(NPT - 0.08))]
        lam.relleno(tapa, "ISO-TAPA"); lam.poli(tapa, "REGISTRO", cerrada=True)
        ls = ["REGISTRO %s  %s" % (r["nombre"], prog_txt(q))] if detalle else ["%s  %s" % (r["nombre"], prog_txt(q))]
        c = [c for c in R["cunetas"] if c["entra_en"] == "colector" and abs(c["prog"] - q) < 0.5]
        if not detalle: ls.append("cuneta Eje %s" % c[0]["perfil"] if c else ("quiebre" if abs(q - dz.P_QUIEBRE) < 0.05 else "limpieza"))
        elif c: ls.append("cuneta Eje %s: NCF %.2f, ventana 0.40 x %.2f" % (c[0]["perfil"], c[0]["NCF_fin"], c[0]["H_ventana"]))
        elif abs(q - dz.P_QUIEBRE) < 0.05: ls.append("quiebre: sigue horizontal hasta la caja CL")
        else: ls.append("registro de limpieza, tapa +%.2f" % NPT)
        ets.append((X(q), Y(NPT), ls, 7))
    # ---------- ventanas de las cunetas en el muro lado predio (cara interior, se ve al fondo del corte)
    for c in R["cunetas"]:
        q = c["prog"]
        if c["entra_en"] != "colector" or not (p1 + 0.2 <= q <= p2 - 0.2): continue
        zt = dz.techo(q); zv = c["NCF_fin"]
        pl = [(X(q - 0.20), Y(zv)), (X(q + 0.20), Y(zv)), (X(q + 0.20), Y(zt)), (X(q - 0.20), Y(zt))]
        lam.relleno(pl, "ISO-CUNETA"); lam.poli(pl, "CUNETA", cerrada=True)
        lam.flecha((X(q + 0.05), Y(zv - 0.01)), (X(q + 0.05), Y(max(perfil_en(R, q, "NA"), fz(q)) + 0.04)), "FLUJO", 1.6 if detalle else 1.2)
    # ---------- juntas de dilatacion cada 4.00 m
    for pj in np.arange(4.0, dz.P_FIN - 0.5, 4.0):
        if p1 < pj < p2:
            lam.linea((X(pj), Y(NPT + 0.02)), (X(pj), Y(fz(pj) - ef - 0.02)), "JUNTAS")
    # ---------- acero (solo detalle): barras longitudinales y marcos cortados, a diametro real
    if detalle:
        for a, c in zip(lim[:-1], lim[1:]):
            m = (a + c) / 2; cam = dz.zona(m) == "CAMION"
            et = D["e_losa_camion"] if cam else D["e_losa"]
            if cam:
                ys = [lambda q: NPT - 0.04, lambda q, et=et: NPT - et + 0.04, lambda q: fz(q) - 0.04, lambda q: fz(q) - ef + 0.04]
                sep, blk = 0.15, "ACERO-12"
            else:
                ys = [lambda q, et=et: NPT - et / 2, lambda q: fz(q) - ef / 2]
                sep, blk = 0.20, "ACERO-38"
            pp = [q for q in ps if a <= q <= c]
            for fy in ys:
                for u, v in ([(a, c)] if fy(m) < NPT - et else [sg for sg in [(a, c)]]):
                    tr = [q for q in pp if u <= q <= v]
                    # la barra superior se interrumpe en los huecos de registro
                    if fy(m) > NPT - et - 1e-6:
                        cortes_ = [(u, v)]
                        for h1, h2 in huecos:
                            nu = []
                            for s1, s2 in cortes_:
                                if h2 <= s1 or h1 >= s2: nu.append((s1, s2)); continue
                                if s1 < h1 - 0.05: nu.append((s1, h1 - 0.05))
                                if h2 + 0.05 < s2: nu.append((h2 + 0.05, s2))
                            cortes_ = nu
                        for s1, s2 in cortes_: lam.linea((X(s1 + 0.03), Y(fy(s1))), (X(s2 - 0.03), Y(fy(s2))), "ACERO-LONG")
                    else:
                        lam.poli([(X(q), Y(fy(q))) for q in sorted(set([u + 0.03, v - 0.03] + [q for q in tr if u + 0.03 < q < v - 0.03]))], "ACERO-LONG")
            q = a + sep / 2
            while q < c - 0.02:
                if not any(h1 - 0.02 < q < h2 + 0.02 for h1, h2 in huecos):
                    for fy in ys: lam.bloque(blk, (X(q), Y(fy(q))), 1.0)
                else:
                    for fy in ys[len(ys) // 2:]: lam.bloque(blk, (X(q), Y(fy(q))), 1.0)
                q += sep
    # ---------- piso terminado (losa) y terreno existente
    lam.poli([(X(p1), Y(NPT)), (X(p2), Y(NPT))], "TERRENO", ancho=0.35 * f)
    lam.poli([(X(t["p"]), Y(t["z"])) for t in T if p1 - 1e-6 <= t["p"] <= p2 + 1e-6], "TERRENO-EXISTENTE")
    # ---------- cruce de camiones
    for z in R["zonas"]:
        a, c = max(z["p1"], p1), min(z["p2"], p2)
        if a < c:
            yb = Y(NPT + 0.10)
            lam.poli([(X(a), yb), (X(c), yb)], "CRUCE-VEHICULAR", ancho=0.8 * f)
            for q in (a, c): lam.linea((X(q), yb - 0.06), (X(q), yb + 0.06), "CRUCE-VEHICULAR")
            ets.append((X((a + c) / 2), yb, ["CRUCE DE CAMIONES CISTERNA %s - %s" % (prog_txt(z["p1"]), prog_txt(z["p2"])),
                                              "losa superior e = 0.25, doble marco 1/2\" @0.15"] if detalle else ["CRUCE DE CAMIONES", "%s - %s" % (prog_txt(z["p1"]), prog_txt(z["p2"]))], NARANJA))
    if p1 <= 0.0 and detalle:
        ets.append((X(0.0), Y(NPT), ["INICIO 0+000.00: poste derecho del porton", "de camiones (junto al Eje 09)"], 7))
    # ---------- llegada a la caja CL del Hogar de Refugio (CUI 2675514) al final del tramo
    if p2 >= dz.P_FIN - 1e-6:
        e = DS_["e_muro"]; zp = D["CL_piso"]; Li = DS_["CL_largo"]; tCL = D["NPT_CL"]; eL = DS_["e_losa"]
        cfF = fz(dz.P_FIN); ztF = dz.techo(dz.P_FIN)
        x0 = dz.P_FIN; xi, xo, xe = x0 + e, x0 + e + Li, x0 + L_CL       # muro este, interior, muro oeste (lindero), cara oeste
        conc = [[(x0, zp - ef), (xe, zp - ef), (xe, zp), (x0, zp)],                 # losa de fondo de la CL
                [(x0, zp), (xi, zp), (xi, cfF - ef), (x0, cfF - ef)],               # muro este bajo la ventana del colector
                [(xo, zp), (xe, zp), (xe, DS_["CF0"]), (xo, DS_["CF0"])],           # muro oeste bajo la salida al Refugio
                [(xo, DS_["NPT"] - eL), (xe, DS_["NPT"] - eL), (xe, tCL), (xo, tCL)],   # muro oeste sobre la salida
                [(xi, tCL - eL), (x0 + L_CL / 2 - 0.35, tCL - eL), (x0 + L_CL / 2 - 0.35, tCL), (xi, tCL)],   # losa de la CL con el hueco del registro
                [(x0 + L_CL / 2 + 0.35, tCL - eL), (xo, tCL - eL), (xo, tCL), (x0 + L_CL / 2 + 0.35, tCL)],
                [(x0, ztF), (xi, ztF), (xi, tCL), (x0, tCL)]]                         # muro este sobre la ventana (techo de la CL)
        for pl in conc:
            pp = [(X(u), Y(v)) for u, v in pl]
            if abs(pl[2][1] - pl[1][1]) > 1e-4: lam.relleno(pp, "CONCRETO-ACHURADO"); lam.poli(pp, "CONCRETO", cerrada=True)
        lam.poli([(X(x0), Y(zp - ef - es)), (X(xe), Y(zp - ef - es))], "SOLADO")
        tapa = [(X(x0 + L_CL / 2 - 0.34), Y(tCL)), (X(x0 + L_CL / 2 + 0.34), Y(tCL)), (X(x0 + L_CL / 2 + 0.34), Y(tCL - 0.08)), (X(x0 + L_CL / 2 - 0.34), Y(tCL - 0.08))]
        lam.relleno(tapa, "ISO-TAPA"); lam.poli(tapa, "REGISTRO", cerrada=True)
        # ventana de la cuneta Eje 01 en el muro norte de la CL (al fondo de la vista)
        c01 = [c for c in R["cunetas"] if c["entra_en"] == "CL"][0]; u01 = x0 + (dz.X_CL_ESTE - c01["x"])
        pl = [(X(u01 - 0.20), Y(c01["NCF_fin"])), (X(u01 + 0.20), Y(c01["NCF_fin"])), (X(u01 + 0.20), Y(tCL - eL)), (X(u01 - 0.20), Y(tCL - eL))]
        lam.relleno(pl, "ISO-CUNETA"); lam.poli(pl, "CUNETA", cerrada=True)
        # colector del Hogar de Refugio (referencia)
        lam.rect(X(xe), Y(DS_["CF0"] - ef), X(xe + L_REF), Y(DS_["NPT"]), "ARQ-BASE"); lam.rect(X(xe), Y(DS_["CF0"]), X(xe + L_REF), Y(DS_["NPT"] - eL), "ARQ-BASE")
        lam.poli([(X(xe), Y(DS_["NPT"])), (X(xe + L_REF), Y(DS_["NPT"]))], "TERRENO", ancho=0.35 * f)
        lam.poli([(X(x0), Y(tCL)), (X(xe), Y(tCL))], "TERRENO", ancho=0.35 * f)
        # agua: caida libre a la poza y salida al colector del Refugio
        naF = perfil_en(R, dz.P_FIN, "NA"); NA_CL = R["caja_llegada"]["NA_CL"]
        ag = [(x0, naF), (x0 + 0.35, NA_CL + 0.12), (x0 + 0.7, NA_CL), (xe + L_REF, NA_CL)]
        fondo_ag = [(x0, cfF), (xi, cfF), (xi, zp), (xo, zp), (xo, DS_["CF0"]), (xe + L_REF, DS_["CF0"])]
        lam.relleno([(X(u), Y(v)) for u, v in fondo_ag + list(reversed(ag))], "AGUA-RELLENO"); lam.poli([(X(u), Y(v)) for u, v in ag], "AGUA")
        lam.linea((X(xe), Y(zp - ef - es - 0.25)), (X(xe), Y(tCL + 0.15)), "LINDERO")
        if detalle:
            ets.append((X(x0 + L_CL / 2), Y(tCL), ["CAJA DE LLEGADA CL (Hogar de Refugio, CUI 2675514): interior %.2f x %.2f," % (Li, DS_["CL_ancho"]),
                                                   "piso %.2f, tapa +%.2f; NA %.3f; caida %.2f m desde el colector" % (zp, tCL, NA_CL, cfF - zp)], 7))
            ets.append((X(u01), Y(tCL - eL), ["CUNETA EJE 01: entra a la CL por el muro norte", "NCF %.2f, ventana 0.40 x %.2f" % (c01["NCF_fin"], c01["H_ventana"])], 94))
        else:
            ets.append((X(x0 + L_CL / 2), Y(tCL), ["CAJA CL %s (Hogar de Refugio): piso %.2f, tapa +%.2f" % (prog_txt(dz.P_FIN), zp, tCL),
                                                   "recibe la cuneta Eje 01 por su muro norte (ver DP-07)"], 7))
        lam.texto((X(xe), Y(zp - ef - es - 0.25) - 0.8 * f), "LINDERO", 1.4 if detalle else 1.2, "TEXTOS", TA.TOP_CENTER, color=6)
        lam.texto((X(xe + L_REF / 2), Y(DS_["NPT"]) + 1.0 * f), "REFUGIO", 1.4 if detalle else 1.1, "ARQ-TEXTO", TA.BOTTOM_CENTER)
        lam.nivel((X(xi + 0.25), Y(zp)), zp, texto="piso CL %.2f" % zp, lado=1, hmm=1.6)
        lam.cota((X(x0), Y(zp)), (X(x0), Y(cfF)), -6, horizontal=False, texto="caida %.2f" % (cfF - zp))
        if detalle:
            lam.cota((X(x0), Y(zp - ef - es)), (X(xi), Y(zp - ef - es)), -6); lam.cota((X(xi), Y(zp - ef - es)), (X(xo), Y(zp - ef - es)), -6)
            lam.cota((X(xo), Y(zp - ef - es)), (X(xe), Y(zp - ef - es)), -6)
    # ---------- cotas de altura interior y niveles en los extremos
    if detalle:
        for pm in (p1 + 0.3 * (p2 - p1), p1 + 0.7 * (p2 - p1)):
            pm = min(pm, dz.P_FIN - 1.0)
            while any(abs(pm - r["prog"]) < 1.0 for r in regs) or any(abs(pm - pj) < 0.3 for pj in np.arange(4.0, dz.P_FIN, 4.0)): pm += 0.6
            lam.cota((X(pm), Y(fz(pm))), (X(pm), Y(dz.techo(pm))), 0, horizontal=False, texto="h=%.2f" % (dz.techo(pm) - fz(pm)))
    lam.nivel((X(p1), Y(fz(p1))), fz(p1), texto="CF %.3f" % fz(p1), lado=1, hmm=1.6 if detalle else 1.4)
    if p2 < dz.P_FIN - 1e-6: lam.nivel((X(p2), Y(fz(p2))), fz(p2), texto="CF %.3f" % fz(p2), lado=-1, hmm=1.6 if detalle else 1.4)
    if detalle:
        lam.texto((X(p1 + 1.5), Y(fz(p1 + 1.5) - ef - es) - 3.2 * f), "S = %.2f %%" % (D["S"] * 100), 1.8, "TEXTOS", TA.LEFT)
    # ---------- escala de cotas a la izquierda
    xg = X(p1) - 4.0 * f
    dzs = 0.1 if detalle else 0.5
    for k in range(math.ceil(zmin / dzs - 1e-6), math.floor(zmax / dzs + 1e-6) + 1):
        z = k * dzs
        lam.linea((xg, Y(z)), (xg + 2 * f, Y(z)), "GRILLA")
        if detalle and k % 2: continue
        lam.texto((xg - 0.8 * f, Y(z)), "%.2f" % z, 1.5 if detalle else 1.3, "TEXTOS", TA.MIDDLE_RIGHT)
    lam.linea((xg + 2 * f, Y(zmin)), (xg + 2 * f, Y(zmax)), "GRILLA")
    # ---------- guitarra
    est = _estaciones(R, p1, p2, paso, 0.75 if detalle else 2.6)
    filas = [("PROGRESIVA", lambda q: prog_txt(q)), ("TERRENO EXISTENTE", lambda q: "%.3f" % terreno_en(T, q)),
             ("CARA SUP. DE LOSA", lambda q: "%.3f" % NPT), ("COTA DE FONDO", lambda q: "%.3f" % fz(q)),
             ("NIVEL DE AGUA", lambda q: "%.3f" % perfil_en(R, q, "NA") if perfil_en(R, q, "NA") - fz(q) > 0.005 else "-"),
             ("ALTURA INTERIOR h", lambda q: "%.2f" % (dz.techo(q + (1e-4 if q < p2 else -1e-4)) - fz(q)))]
    if detalle: filas.append(("PROF. EXCAVACION", lambda q: "%.2f" % (max(terreno_en(T, q), NPT) - (fz(q) - ef - es))))
    alto = 5.4 if detalle else 5.0
    yg0 = ymm - 4.0
    x0g = xmm - 44.0; x1g = xmm + (p2 - p1) / f
    for i in range(len(filas) + 1):
        lam.linea(lam.P(x0g, yg0 - i * alto), lam.P(x1g, yg0 - i * alto), "GUITARRA")
    for xv in (x0g, xmm - 6.0, x1g):
        lam.linea(lam.P(xv, yg0), lam.P(xv, yg0 - len(filas) * alto), "GUITARRA")
    for i, (nom, fn) in enumerate(filas):
        yc = yg0 - (i + 0.5) * alto
        lam.texto(lam.P(x0g + 1.5, yc), nom, 1.6 if detalle else 1.4, "TEXTOS", TA.MIDDLE_LEFT)
        for q in est:
            lam.texto((X(q), lam.oy + yc * f), fn(q), 1.45 if detalle else 1.25, "TEXTOS", TA.MIDDLE_CENTER)
    for q in est:
        lam.linea((X(q), lam.oy + yg0 * f), (X(q), Y(fz(q) - ef - es)), "GRILLA")
    # ---------- franja de etiquetas encima del perfil
    ytop = Y(max(zmax, D["NPT"] + 0.2))
    xmax = x1g + 2 + ((L_CL + L_REF) / f if p2 >= dz.P_FIN - 1e-6 else 0)
    yf = lam.franja(ets, ytop, abajo=False, hmm=1.6 if detalle else 1.4, xmin_mm=xmm - 40, xmax_mm=xmax_txt or min(xmax + 30, lam.W - 15)) if ets else ytop
    if titulo:
        lam.texto((lam.ox + (xmm - 44) * f, yf + 3.0 * f), titulo, 3.0, "TITULOS", TA.BOTTOM_LEFT)
    return yg0 - len(filas) * alto


LEY_PERFIL = [("concreto", "CONCRETO", "concreto armado f'c=210 cortado (losas, caja CL)"), ("rect", "SOLADO", "solado f'c=100 e = 0.05"),
              ("relleno", "AGUA-RELLENO", "agua con el caudal de diseno"), ("discontinua", "TERRENO-EXISTENTE", "terreno existente (topografia)"),
              ("linea2", "TERRENO", "piso terminado = losa superior +261.15"), ("relleno", "ISO-TAPA", "tapa de registro 0.68 x 0.08"),
              ("discontinua", "JUNTAS", "junta de dilatacion e = 1\" cada 4.00 m"), ("relleno", "ISO-CUNETA", "ventana de llegada de cuneta 0.40 x H"),
              ("linea2", "CRUCE-VEHICULAR", "cruce de camiones cisterna"), ("rect", "ARQ-BASE", "colector del Hogar de Refugio (referencia)")]


def cuadro_hidraulico(R):
    lims = [0.0] + [c["prog"] for c in R["cunetas"] if c["entra_en"] == "colector"] + [dz.P_FIN]
    noms = ["0+000 - RV-01 (Eje 09)"] + ["%s (Eje %s) - %s" % (_reg_en(R, a) or "", c["perfil"], (_reg_en(R, b_) or "CL") if b_ < dz.P_FIN - 0.5 else "CL")
                                      for c, a, b_ in zip([c for c in R["cunetas"] if c["entra_en"] == "colector"], lims[1:-1], lims[2:])]
    filas = []
    for k in range(len(lims) - 1):
        a, b_ = lims[k], lims[k + 1]
        rows = [e for e in R["perfil"] if a + 1e-6 < e["p"] < b_ - 1e-6] or [e for e in R["perfil"] if a - 1e-6 <= e["p"] <= b_ + 1e-6]
        q = max(e["Q"] for e in rows) * 1000
        if q < 0.05:
            filas.append([noms[k], "%s - %s" % (prog_txt(a), prog_txt(b_)), "0.0", "-", "-", "-", "-", "-"]); continue
        filas.append([noms[k], "%s - %s" % (prog_txt(a), prog_txt(b_)), "%.1f" % q, "%.2f - %.2f" % (min(e["y"] for e in rows), max(e["y"] for e in rows)),
                      "%.2f - %.2f" % (min(e["V"] for e in rows), max(e["V"] for e in rows)), "%.2f" % max(e["F"] for e in rows),
                      "%.0f %%" % (100 * max(e["llenado"] for e in rows)), "%.3f" % min(e["BL"] for e in rows)])
    return ["TRAMO", "PROGRESIVAS", "Q (L/s)", "TIRANTE (m)", "V (m/s)", "FROUDE", "LLENADO", "B. LIBRE (m)"], filas


def dp02(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 100, "DP-02", "PERFIL LONGITUDINAL GENERAL DEL COLECTOR",
                   "ESCALA REAL (H = V) - %s A %s - NIVEL DE AGUA DE DISENO, REGISTROS Y LLEGADA A LA CAJA CL" % (prog_txt(0.0), prog_txt(dz.P_FIN)), formato="A2")
    tr = [0.0, 35.1, 70.2, dz.P_FIN]
    ytop = 400
    for j in range(3):
        y = ytop - 30 - alto_perfil(R, T, tr[j], tr[j + 1], lam.f)
        yb = perfil(lam, 72, y, tr[j], tr[j + 1], R, T, detalle=False, titulo="PERFIL %d: %s A %s" % (j + 1, prog_txt(tr[j]), prog_txt(tr[j + 1])), paso=None,
                    xmax_txt=lam.W - 15 if j == 2 else 462)
        ytop = yb - 8
    yl = lam.leyenda2(470, 400, LEY_PERFIL, hmm=1.6)
    lam.notas(470, yl - 6, "NOTAS", [
        "1. Escala real H = V = 1/100; cotas en m.s.n.m. Perfil detallado con acero en DP-03A y DP-03B (1/25).",
        "2. Nivel de agua por flujo gradualmente variado con caudal creciente en cada cuneta; control: tirante critico en la caida a la caja CL.",
        "3. %s = %.1f L/s en el colector; la cuneta del Eje 01 (%.1f L/s) entra a la CL: total %.1f L/s (TR 25 anos)." % (
            " + ".join("Eje %s %.1f" % (c["perfil"], c["Q"]) for c in R["cunetas"] if c["entra_en"] == "colector"), R["Q"], R["Q_directo_CL"], R["Q_CL"]),
        "4. La caja CL y el colector del Hogar de Refugio (CUI 2675514) son referencia; la tapa de la CL queda en +261.15."], hmm=1.5, ancho_mm=112)
    cab, fh = cuadro_hidraulico(R)
    lam.tabla(30, min(ytop - 8, 150), cab, fh, [52, 46, 16, 26, 26, 16, 18, 22], hmm=1.4, alto_mm=4.6, titulo="CUADRO HIDRAULICO POR TRAMOS (TR = 25 ANOS)")
    return lam


def dp03(doc, ox, oy, R, T):
    out = []
    for k, cod in enumerate(("DP-03A", "DP-03B")):
        tr = TRAMOS_DP03[3 * k: 3 * k + 4]
        lam = B.Lamina(doc, ox + k * 25.0, oy, 25, cod, "PERFIL LONGITUDINAL DETALLADO DEL COLECTOR",
                       "TRAMOS %d A %d (%s - %s) - ESCALA REAL (H = V) - ACERO, REGISTROS, JUNTAS, EMPALMES%s" % (
                           3 * k + 1, 3 * k + 3, prog_txt(tr[0]), prog_txt(tr[-1]), " Y LLEGADA A LA CL" if k else ""))
        altos = [alto_perfil(R, T, tr[j], tr[j + 1], lam.f) for j in range(3)]
        gap = max(0.0, (578 - 112 - sum(altos) - 3 * (32 + 4 + 7 * 5.4)) / 2)
        ytop = 578
        for j in range(3):
            a, c = tr[j], tr[j + 1]
            y = ytop - 32 - altos[j]
            yb = perfil(lam, 72, y, a, c, R, T, detalle=True, titulo="TRAMO %d: %s A %s" % (3 * k + j + 1, prog_txt(a), prog_txt(c)), paso=2.5)
            ytop = yb - gap
        yl = lam.leyenda2(30, 100, LEY_PERFIL[:8] + [("bloque:ACERO-38", "ACERO-PUNTOS", "marco cortado (3/8\" o 1/2\")"),
                                                    ("linea", "ACERO-LONG", "barras longitudinales 3/8\"")], hmm=1.6, ancho_col=100, filas_col=5)
        lam.notas(255, 100, "NOTAS", [
            "1. Escala real H = V = 1/25; cotas en m.s.n.m.",
            "2. Tramo normal: marco 3/8\" @0.20 en el eje de losas y muros; cruce de camiones: doble marco 1/2\" @0.15, recubrimiento 0.04.",
            "3. Barras longitudinales 3/8\" @0.25 (@0.20 en el cruce de camiones), traslape 0.40 m; se interrumpen en las juntas.",
            "4. Juntas de dilatacion cada 4.00 m (%d und). Ventana de cuneta 0.40 x H en el muro lado predio, bajo el registro (DP-06C)." % int(dz.P_FIN // 4.0),
            "5. Registro: abertura 0.70, borde engrosado 0.15 x 0.10 y tapa 0.68 x 0.08 sobre el contramarco (DP-06B)."], hmm=1.6, ancho_mm=380)
        out.append(lam)
    return out


# =============================================================================== DP-07 EMPALME CON LA CL
def dp07(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 20, "DP-07", "EMPALME DEL COLECTOR CON LA CAJA DE LLEGADA CL DEL HOGAR DE REFUGIO",
                   "PLANTA Y CORTES: VENTANA ESTE 0.60 x 1.17, VENTANA NORTE DE LA CUNETA EJE 01, JUNTAS Y NIVELES - ESC. 1/20")
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
    lam.titulo_vista(170 + 60, 445 - 108, "A. EMPALME CON LA CAJA CL - PLANTA", "ESC. 1/20 - losas superiores retiradas; norte hacia arriba del dibujo (sistema local del plano de arquitectura)", 200)
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
    lam.llamada(Pc(u01 + 0.15, (c01["NCF_fin"] + tCL - eL) / 2 + 0.1), Pc(xt, tCL + 0.05), ["ventana norte 0.40 x %.2f (cuneta Eje 01)" % c01["H_ventana"], "NCF %.2f; caida libre %.2f m sobre el NA" % (c01["NCF_fin"], c01["caida_libre"])], 1.7)
    lam.llamada(Pc(uE, (zt + cf) / 2 + 0.15), Pc(xt, tCL - 0.45), ["ventana este 0.60 x %.2f (%.3f a %.2f)" % (zt - cf, cf, zt), "= seccion del colector; sin dintel (techo CL %.2f)" % (tCL - eL)], 1.7)
    lam.llamada(Pc(uV0 + jt / 2, cf + 0.15), Pc(xt, cf - 0.35), ["tecnopor 1\" en todo el contacto colector - CL"], 1.7)
    lam.llamada(Pc(uE - 0.45, NA_CL + 0.06), Pc(xt, cf - 0.85), ["caida libre %.2f m del fondo del colector al NA de la CL;" % (cf - NA_CL), "colchon de agua %.2f m sobre el piso de la CL" % (NA_CL - zp)], 1.7)
    lam.llamada(Pc(-0.05, (DS_["NPT"] + tCL) / 2), Pc(-1.5, tCL + 0.32), ["escalon de 0.55 m entre pisos (+261.15 Varones /", "+260.60 Refugio) en el lindero: cara oeste de la CL"], 1.7)
    lam.titulo_vista(170 + 60, 150 - 14, "B. CORTE A-A POR EL EJE (MIRANDO AL NORTE)", "ESC. 1/20 - colector CAR Varones (derecha) -> caja CL -> colector del Hogar de Refugio (izquierda, referencia)", 220)
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
    lam.titulo_vista(600 + 25, 150 - 14, "C. CORTE B-B POR LA CAJA CL (MIRANDO AL OESTE)", "ESC. 1/20", 200)
    # leyenda, cuadro y notas
    lam.leyenda2(600, 568, [("concreto", "CONCRETO", "concreto armado f'c=210 (CL: expediente del Hogar de Refugio)"), ("rect", "ARQ-BASE", "colector del Hogar de Refugio (referencia)"),
                            ("rect", "CUNETA", "cuneta de arquitectura (Eje 01)"), ("relleno", "ISO-CUNETA", "ventana de llegada de cuneta"), ("discontinua", "JUNTAS", "junta de tecnopor 1\""),
                            ("relleno", "AGUA-RELLENO", "agua (nivel de diseno)"), ("linea", "LINDERO", "lindero entre predios"), ("bloque:SIMB-FLECHA", "FLUJO", "sentido del flujo")], hmm=1.7)
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
    C.usar_planilla()                 # cuadros DA-01 a DA-03 con los valores de la planilla del presupuesto
    doc = B.nuevo_documento()
    LAMINAS.clear()
    lam = dp01(doc, OX1, OY1, R, T, BP); LAMINAS["DP-01"] = lam
    lam = dp02(doc, OX1 + 200, OY1, R, T); LAMINAS["DP-02"] = lam
    for lam in dp03(doc, OX1 + 265, OY1, R, T): LAMINAS[lam.codigo] = lam
    for lam in DS.dp04(doc, OX1, OY1 - 200, R, T): LAMINAS[lam.codigo] = lam
    lam = DS.dp06b(doc, OX1 + 70, OY1 - 200, R, T); LAMINAS[lam.codigo] = lam
    lam = DS.dp06c(doc, OX1 + 85, OY1 - 200, R, T); LAMINAS[lam.codigo] = lam
    lam = dp07(doc, OX1 + 100, OY1 - 200, R, T); LAMINAS[lam.codigo] = lam
    for lam in DQ.todas(doc, OX1, OY1 - 400, R, T): LAMINAS[lam.codigo] = lam
    for lam in DD.todas(doc, OX1, OY1 - 600, R, T): LAMINAS[lam.codigo] = lam
    indicadas = ("DP-06B", "DD-01", "DD-02", "DD-03", "DD-04")
    lista = [(c, l.titulo, l.formato, "INDICADA" if c in indicadas else l.escala_txt) for c, l in LAMINAS.items()]
    lam0 = L.indice(doc, OX1 - 20.0, OY1 - 200, [("DP-00", "INDICE DE LAMINAS", "A3", "S/E")] + lista)
    LAMINAS["DP-00"] = lam0; LAMINAS.move_to_end("DP-00", last=False)
    # rellenos al fondo: las lineas y textos quedan siempre visibles encima
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: "1" for e in msp.query("HATCH") if e.dxf.layer in ("CONCRETO-ACHURADO", "AGUA-RELLENO")})
    L.presentaciones(doc, LAMINAS)
    os.makedirs(dz.CALC, exist_ok=True)
    doc.saveas(SALIDA)
    cajas = {k: (l.ox, l.oy, l.ox + l.W * l.f, l.oy + l.H * l.f) for k, l in LAMINAS.items()}
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
