"""Laminas DP-01 (planta), DP-02 (perfil general) y DP-03 (perfiles por tramos)."""
import os, sys, json, math
import numpy as np
from ezdxf.enums import TextEntityAlignment as TA
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import diseno as dz
import dxf_base as B

CALC = os.path.join(RAIZ, "entregables", "_calc")


def cargar():
    R = json.load(open(os.path.join(CALC, "diseno.json"), encoding="utf8"))
    T = json.load(open(os.path.join(CALC, "terreno.json")))
    BP = json.load(open(os.path.join(CALC, "base_planta.json"), encoding="utf8"))
    return R, T, BP


def prog_txt(p):
    return "0+%06.2f" % p


def terreno_en(T, p):
    ps = [t["p"] for t in T]; zs = [t["z"] for t in T]
    return float(np.interp(p, ps, zs))


def perfil_en(R, p, clave):
    P = R["perfil"]; ps = [e["p"] for e in P]; vs = [e[clave] for e in P]
    return float(np.interp(p, ps, vs))


# ----------------------------------------------------------------------------
# geometria del eje y de los muros en planta (coordenadas locales)
def eje_puntos():
    """Vertices del eje: inicio (0+000), quiebre 1, quiebre 2, brink, fin (cara de R-01)."""
    return [dz.eje_local(p)[:2] for p in (0.0, dz.P_B1, dz.P_B2, dz.P_BRINK, dz.P_FIN)]


def offset_poli(pts, d):
    """Desplaza una polilinea abierta una distancia d (positivo a la izquierda del sentido de avance)."""
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        elif i == n - 1:
            dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
        else:
            d1 = np.array([pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]]); d1 /= np.linalg.norm(d1)
            d2 = np.array([pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]]); d2 /= np.linalg.norm(d2)
            n1 = np.array([-d1[1], d1[0]]); n2 = np.array([-d2[1], d2[0]])
            bis = n1 + n2; bis /= np.linalg.norm(bis)
            k = d / np.dot(bis, n1)
            out.append((pts[i][0] + bis[0] * k, pts[i][1] + bis[1] * k)); continue
        L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
        out.append((pts[i][0] + nx * d, pts[i][1] + ny * d))
    return out


def _pe(p, lateral):
    x, y, az = dz.eje_local(p)
    a = math.radians(az)
    # avance = (cos a, sin a); izquierda = (-sin a, cos a)
    return (x + lateral * (-math.sin(a)), y + lateral * math.cos(a))


def _clip_seg(p1, p2, w):
    """Liang-Barsky: recorta el segmento p1-p2 a la ventana w=(x0,y0,x1,y1)."""
    x0, y0, x1, y1 = w; dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, p1[0] - x0), (dx, x1 - p1[0]), (-dy, p1[1] - y0), (dy, y1 - p1[1])):
        if p == 0:
            if q < 0: return None
        else:
            t = q / p
            if p < 0: t0 = max(t0, t)
            else: t1 = min(t1, t)
    if t0 > t1: return None
    return ((p1[0] + t0 * dx, p1[1] + t0 * dy), (p1[0] + t1 * dx, p1[1] + t1 * dy))


def recortar(pts, w):
    """Devuelve las polilineas resultantes de recortar pts a la ventana w."""
    out = []; cur = []
    for a, b_ in zip(pts[:-1], pts[1:]):
        c = _clip_seg(a, b_, w)
        if c is None:
            if len(cur) > 1: out.append(cur)
            cur = []; continue
        if not cur or (abs(cur[-1][0] - c[0][0]) > 1e-6 or abs(cur[-1][1] - c[0][1]) > 1e-6):
            if len(cur) > 1: out.append(cur)
            cur = [c[0]]
        cur.append(c[1])
    if len(cur) > 1: out.append(cur)
    return out


# ----------------------------------------------------------------------------
def dp01(doc, ox, oy, R, T, BP):
    esc = 200
    lam = B.Lamina(doc, ox, oy, esc, "DP-01", "PLANTA DEL COLECTOR PLUVIAL",
                   "TRAMO HOGAR DE REFUGIO (0+000.00 - %s) - TRAZO, REGISTROS, CAJAS Y EMPALME CON CAR MUJERES" % prog_txt(dz.P_FIN))
    D = dz.D; msp = lam.msp
    # --- base de arquitectura (coordenadas locales reales), recortada a la ventana de dibujo
    win = (dz.X_SO - 36, dz.Y_CERCO - 22, dz.X_NE + 22, dz.Y_CERCO + 38)
    winw = (dz.X_SO - 36, dz.Y_CERCO - 22, dz.X_SO + 2, dz.Y_CERCO + 14)
    for s in BP["arq"]:
        for seg in recortar(s["pts"], win):
            lam.poli(seg, s["layer"])
    for s in BP["wilma"]:
        for seg in recortar(s["pts"], winw):
            lam.poli(seg, s["layer"])
    claves = ("ESTACIONAMIENTO", "INGRESO", "VIGILANCIA", "SS.HH", "OE-", "OC-", "VEREDA", "PTAR", "PATIO")
    for t in BP["textos"]:
        if win[0] < t["x"] < win[2] and win[1] < t["y"] < win[3] and (t["y"] > dz.Y_CERCO + 12 or any(k in t["t"] for k in claves)):
            lam.texto((t["x"], t["y"]), t["t"], 1.6, "ARQ-TEXTO")
    for seg in recortar(BP["lote_sur"], win):
        lam.poli(seg, "LINDERO")
    # cerco sur (resaltado)
    lam.poli([(dz.X_SO, dz.Y_CERCO), (dz.X_NE, dz.Y_CERCO)], "CERCO", ancho=0.08)
    # --- colector: eje, muros, losa
    E = eje_puntos()
    ext_pred = offset_poli(E[:4], D["b_ext"] / 2)          # lado predio (izquierda del avance)
    ext_via = offset_poli(E[:4], -D["b_ext"] / 2)
    int_pred = offset_poli(E[:4], D["b"] / 2); int_via = offset_poli(E[:4], -D["b"] / 2)
    lam.poli(E[:4], "EJE-COLECTOR")
    for pl in (ext_pred, ext_via): lam.poli(pl, "CONCRETO", ancho=0.04)
    for pl in (int_pred, int_via): lam.poli(pl, "CONCRETO-OCULTO")
    # caja de llegada CL en 0+000 (interior 1.50 x 1.00): hacia aguas arriba del 0+000
    x0, y0 = E[0]
    cl = [(x0, y0 - 0.5 - D["e_muro"]), (x0 + D["CL_largo"] + D["e_muro"], y0 - 0.5 - D["e_muro"]),
          (x0 + D["CL_largo"] + D["e_muro"], y0 + 0.5 + D["e_muro"]), (x0, y0 + 0.5 + D["e_muro"])]
    lam.poli(cl, "CONCRETO", cerrada=True, ancho=0.04)
    lam.rect(x0, y0 - 0.5, x0 + D["CL_largo"], y0 + 0.5, "CONCRETO-OCULTO")
    lam.poli([(x0, y0 - 0.5), (x0, y0 + 0.5)], "CONCRETO-OCULTO")
    # caja de caida CC: poza 1.50 x 3.50 entre brink y fin
    xb, yb = E[3]; xf, yf = E[4]
    lam.rect(xf - D["e_muro"], yb - 0.75 - D["e_muro"], xb, yb + 0.75 + D["e_muro"], "CONCRETO", const_width=0.04)
    lam.rect(xf, yb - 0.75, xb, yb + 0.75, "POZA")
    lam.poli([(xb, yb - D["b"] / 2), (xb, yb + D["b"] / 2)], "CONCRETO-OCULTO")   # brink
    lam.poli([(xf + 0.20, yb - 0.75), (xf + 0.20, yb + 0.75)], "POZA")             # umbral
    # registros
    for rg in R["registros"]:
        p = rg["prog"]; nm = rg["nombre"]
        if nm in ("CL", "CC"): continue
        c = dz.eje_local(p)[:2]
        lam.bloque("REGISTRO-PLANTA", c, 1.0, rot=dz.eje_local(p)[2])
        lam.texto(_pe(p, -1.3), nm, 1.8, "REGISTRO", TA.MIDDLE_CENTER)
    lam.texto(_pe(0.75, -1.6), "CL", 1.8, "REGISTRO", TA.MIDDLE_CENTER)
    lam.texto(((xb + xf) / 2, yb - 1.5), "CC", 1.8, "REGISTRO", TA.MIDDLE_CENTER)
    # tapas de registro de las cajas (0.68) en planta
    lam.bloque("REGISTRO-PLANTA", (x0 + 0.75, y0), 1.0); lam.bloque("REGISTRO-PLANTA", (xf + 1.0, yb), 1.0); lam.bloque("REGISTRO-PLANTA", (xb - 0.6, yb), 1.0)
    # juntas cada 4 m
    p = 4.0
    while p < dz.P_BRINK - 0.5:
        a, b_ = _pe(p, D["b_ext"] / 2 + 0.15), _pe(p, -D["b_ext"] / 2 - 0.15)
        lam.linea(a, b_, "JUNTAS"); p += 4.0
    # cruces vehiculares
    for z in R["zonas"]:
        pts = [_pe(z["p1"], D["b_ext"] / 2 + 0.1), _pe(z["p2"], D["b_ext"] / 2 + 0.1), _pe(z["p2"], -D["b_ext"] / 2 - 0.1), _pe(z["p1"], -D["b_ext"] / 2 - 0.1)]
        lam.poli(pts, "CRUCE-VEHICULAR", cerrada=True, ancho=0.03)
        txt = "CRUCE DE CAMIONES %s - %s: losa e=0.25, muros e=0.15, doble marco 1/2\" @0.15" % (prog_txt(z["p1"]), prog_txt(z["p2"])) if z["tipo"] == "CAMION" else "CRUCE DE MOTOS %s - %s: marco 3/8\" @0.15" % (prog_txt(z["p1"]), prog_txt(z["p2"]))
        lam.llamada(_pe((z["p1"] + z["p2"]) / 2, -D["b_ext"] / 2 - 0.1), _pe((z["p1"] + z["p2"]) / 2 + (8 if z["tipo"] == "CAMION" else -8), -D["b_ext"] / 2 - (4.0 if z["tipo"] == "CAMION" else 6.5)), [txt], 1.6)
    # cunetas que llegan: prolongacion + ventana
    for c in R["cunetas"]:
        p = c["prog"]; x = c["x"]
        if c["prolong"] <= 0.1:
            a = (x, dz.Y_CERCO); b_ = _pe(p, D["b_ext"] / 2)
        elif p < dz.P_B2 + 0.5 and p > dz.P_B1:
            # prolongacion perpendicular al cerco hasta el muro del tramo diagonal
            a = (x, dz.Y_CERCO); b_ = (x, dz.Y_CERCO - c["prolong"])
        else:
            a = (x, dz.Y_CERCO); b_ = (x, dz.Y_CERCO - c["prolong"])
        if c["prolong"] > 0.1:
            lam.poli([(a[0] - 0.3, a[1]), (b_[0] - 0.3, b_[1])], "CUNETA"); lam.poli([(a[0] + 0.3, a[1]), (b_[0] + 0.3, b_[1])], "CUNETA")
            lam.poli([(a[0] - 0.2, a[1]), (b_[0] - 0.2, b_[1])], "CUNETA-OCULTA"); lam.poli([(a[0] + 0.2, a[1]), (b_[0] + 0.2, b_[1])], "CUNETA-OCULTA")
        lam.bloque("SIMB-FLECHA", (x, dz.Y_CERCO + 1.2), 0.08, rot=-90, capa="FLUJO")
        k = [cc["perfil"] for cc in R["cunetas"]].index(c["perfil"])
        lam.llamada((x, dz.Y_CERCO + 1.9), (x + 2.0, dz.Y_CERCO + 3.6 + 2.6 * (k % 3)),
                    ["CUNETA %s - perfil %s: 0.40 x %.2f, NCF %.2f" % (c["nombre"].split(" (")[0], c["perfil"], c["H"], c["NCF"]),
                     "empalme en %s (%s)%s" % (prog_txt(p), [r["nombre"] for r in R["registros"] if abs(r["prog"] - p) < 1.5][0] if any(abs(r["prog"] - p) < 1.5 for r in R["registros"]) else "registro",
                                              "; prolongacion %.2f m" % c["prolong"] if c["prolong"] > 0.1 else "")], 1.6)
    # progresivas cada 10 m y puntos singulares
    for p in list(np.arange(0, dz.P_BRINK, 10.0)) + [dz.P_B1, dz.P_B2, dz.P_BRINK, dz.P_FIN]:
        a, b_ = _pe(p, -D["b_ext"] / 2 - 0.3), _pe(p, -D["b_ext"] / 2 - 1.2)
        lam.linea(a, b_, "PROGRESIVAS")
        lam.texto(_pe(p, -D["b_ext"] / 2 - 1.5), prog_txt(p), 1.5, "PROGRESIVAS", TA.TOP_CENTER, rot=dz.eje_local(p)[2] - 180)
    # flechas de flujo
    for p in (15, 35, 55, 63.5):
        lam.bloque("SIMB-FLECHA", _pe(p, 0), 0.12, rot=dz.eje_local(p)[2], capa="FLUJO")
    # llegada de CAR Varones
    lam.llamada((x0 + D["CL_largo"] + D["e_muro"], y0), (x0 + 9, y0 - 6.5),
                ["LLEGADA DEL COLECTOR DE CAR VARONES (CUI 2705619): 258.7 L/s", "entra por la cara NE de la caja de llegada CL (cota referencial 260.18, por confirmar)"], 1.6)
    # entrega a CAR Mujeres
    lam.llamada((xf, yb), (xf - 2, yb - 10.0), ["ENTREGA AL REGISTRO R-01 DEL COLECTOR DE CAR MUJERES (CUI 2717013)", "CF 258.72 = fondo del umbral de la poza; Q entregado 560.6 L/s"], 1.6, al=TA.LEFT)
    lam.texto((xf - 1.0, yb + 1.3), "R-01 (CAR Mujeres)", 1.6, "ARQ-TEXTO", TA.RIGHT)
    # textos de ubicacion
    lam.texto((dz.X_NE - 35, dz.Y_CERCO - 7.5), "HOGAR DE REFUGIO TEMPORAL MUJERES VIOLENTADAS - FRENTE SUR (cerco perimetrico)", 2.2, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto((dz.X_NE - 35, dz.Y_CERCO - 13.5), "CARRETERA OASIS", 2.4, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto((dz.X_SO - 14, dz.Y_CERCO + 10), "CAR MUJERES (CUI 2717013)", 2.0, "ARQ-TEXTO", TA.MIDDLE_CENTER)
    lam.texto((dz.X_NE + 12, dz.Y_CERCO + 10), "CAR VARONES (CUI 2705619)", 2.0, "ARQ-TEXTO", TA.MIDDLE_CENTER)
    lam.texto((dz.X_NE - 35, dz.Y_CERCO - 10.5), "COLECTOR CUBIERTO DE CONCRETO ARMADO b = 0.80 m, h = 1.40 a 1.61 m, S = 0.30 % - LOSA SUPERIOR A NIVEL DEL PISO TERMINADO +260.60", 1.8, "TEXTOS", TA.MIDDLE_CENTER)
    # grilla UTM (cruces cada 25 m) y rotulos
    E0, N0 = dz.local_a_utm(dz.X_NE - 35, dz.Y_CERCO)
    for Eg in np.arange(math.floor((E0 - 70) / 25) * 25, E0 + 75, 25):
        for Ng in np.arange(math.floor((N0 - 50) / 25) * 25, N0 + 55, 25):
            x, y = dz.utm_a_local(Eg, Ng)
            if lam.ox + 30 * lam.f < x < lam.ox + 600 * lam.f and lam.oy + 280 * lam.f < y < lam.oy + 575 * lam.f:
                lam.linea((x - 1.5, y), (x + 1.5, y), "GRILLA"); lam.linea((x, y - 1.5), (x, y + 1.5), "GRILLA")
                lam.texto((x + 0.3, y + 0.3), "E %d" % Eg, 1.2, "GRILLA", rot=90 - dz.AZ_FRENTE - 90 + 90 if False else 0)
                lam.texto((x + 0.3, y - 1.5), "N %d" % Ng, 1.2, "GRILLA")
    # norte (UTM) girado
    lam.bloque("SIMB-NORTE", lam.P(690, 500), lam.f, rot=dz.AZ_FRENTE - 90)   # norte UTM en coordenadas locales
    # cuadro de coordenadas
    filas = []
    for rg in R["registros"]:
        p = rg["prog"]; x, y, _ = dz.eje_local(p); Eu, Nu = dz.local_a_utm(x, y)
        cf = dz.fondo(min(p, dz.P_BRINK)) if rg["nombre"] != "CC" else D["CF_R01"] - D["CC_poza_prof"]
        filas.append([rg["nombre"], prog_txt(p), "%.3f" % Eu, "%.3f" % Nu, "%.3f" % cf, "%.3f" % D["NPT"], rg["nota"]])
    x, y, _ = dz.eje_local(dz.P_FIN); Eu, Nu = dz.local_a_utm(x, y)
    filas.append(["R-01 (receptor)", prog_txt(dz.P_FIN), "%.3f" % Eu, "%.3f" % Nu, "%.3f" % D["CF_R01"], "%.3f" % D["NPT_wilma"], "0+000 del tramo CAR Mujeres"])
    lam.tabla(32, 560, ["PUNTO", "PROGRESIVA", "ESTE", "NORTE", "COTA FONDO", "COTA TAPA", "OBSERVACION"], filas, [22, 20, 24, 26, 20, 20, 92], 1.7, 4.2, "CUADRO DE COORDENADAS DE REGISTROS Y CAJAS")
    lam.texto(lam.P(32, 560 - 4.2 * (len(filas) + 1) - 6), "Coordenadas UTM WGS84 - Zona 18 Sur. Ubicacion referencial: el plano de arquitectura se georreferencio con el R-01 del CAR Mujeres y el rumbo de su lindero (azimut 49.54); verificar en campo.", 1.5, "TEXTOS-NOTAS")
    # leyenda y notas
    lam.leyenda(32, 150, [("linea2", "CONCRETO", "muro exterior del colector"), ("linea", "CONCRETO-OCULTO", "cara interior (bajo losa superior)"),
                          ("linea", "EJE-COLECTOR", "eje del colector"), ("bloque:REGISTRO-PLANTA", "REGISTRO", "registro de limpieza con tapa removible"),
                          ("linea", "JUNTAS", "junta de dilatacion cada 4.00 m"), ("rect", "CRUCE-VEHICULAR", "cruce vehicular (motos / camiones)"),
                          ("rect", "POZA", "poza de disipacion (caja de caida)"), ("linea", "CUNETA", "cuneta de arquitectura que llega al colector"),
                          ("linea2", "CERCO", "cerco perimetrico del predio"), ("linea", "LINDERO", "lindero con la Crta. Oasis"),
                          ("linea", "ARQ-BASE", "arquitectura (referencia)"), ("bloque:SIMB-FLECHA", "FLUJO", "sentido del flujo")], 1.8)
    lam.notas(300, 150, "NOTAS", [
        "1. Colector de concreto armado f'c=210 kg/cm2, cubierto en todo su recorrido, losa superior vaciada monoliticamente con los muros.",
        "2. El colector va por fuera del cerco, dentro del predio: muro lado predio a 0.025 m del cerco (junta de tecnopor de 1\"). Eje a 0.575 m del cerco.",
        "3. Progresivas a lo largo del eje desde la caja de llegada CL (limite con CAR Varones), crecientes hacia la entrega al CAR Mujeres.",
        "4. Registros de limpieza con tapa removible a ras del piso terminado, en cada empalme de cuneta, en los quiebres y cada 12.00 m como maximo.",
        "5. Cotas en m.s.n.m. Cara superior de la losa = piso terminado del frente +260.60. Fondo 259.10 (0+000) a 258.89 (brink), S = 0.30 %.",
        "6. Cajas: CL de llegada (0+000) con poza de 0.30 m; CC de caida con poza de 0.40 m bajo el fondo del receptor y umbral de salida.",
        "7. Las cunetas de arquitectura (perfiles 01 a 12) entran por ventana en el muro lado predio; las de los Ejes 11 y 12 se prolongan fuera del cerco.",
        "8. Ver perfil en DP-02 y DP-03, secciones en DP-04 a DP-06, cajas en DP-07, acero y especificaciones en DP-08, isometricos en DP-09 y DP-10.",
    ], 1.7)
    return lam


# ----------------------------------------------------------------------------
def perfil_tramo(lam, xmm, ymm, p1, p2, R, T, escH, escV, con_tabla=True, paso_tabla=5.0, titulo=None):
    """Dibuja el perfil entre p1 y p2 con origen de papel (xmm, ymm) = (p1, cota_base).
    escH, escV: m de papel por m real -> usamos factores: fx = 1000/escH mm por m."""
    D = dz.D
    fx = 1000.0 / escH * lam.f      # unidades modelo por m horizontal
    fy = 1000.0 / escV * lam.f
    zb = 257.60                     # cota base del perfil (eje de referencia)
    def X(p): return lam.ox + xmm * lam.f + (p - p1) * fx
    def Y(z): return lam.oy + ymm * lam.f + (z - zb) * fy
    ps = [e["p"] for e in R["perfil"] if p1 - 1e-6 <= e["p"] <= p2 + 1e-6]
    ps = sorted(set([p1, p2] + ps))
    fondo = [(X(p), Y(dz.fondo(min(p, dz.P_BRINK)))) for p in ps]
    techo = [(X(p), Y(dz.techo(p))) for p in ps]
    npt = [(X(p1), Y(D["NPT"])), (X(p2), Y(D["NPT"]))]
    na = [(X(p), Y(perfil_en(R, p, "NA"))) for p in ps]
    terr = [(X(t["p"]), Y(t["z"])) for t in T if p1 - 1e-6 <= t["p"] <= p2 + 1e-6]
    # losa superior y fondo (espesores)
    lam.poli(npt, "TERRENO", ancho=0.3 * lam.f)
    lam.poli(techo, "CONCRETO"); lam.poli(fondo, "CONCRETO")
    lam.poli([(X(p), Y(dz.fondo(min(p, dz.P_BRINK)) - D["e_fondo"])) for p in ps], "CONCRETO")
    lam.poli([(X(p), Y(dz.fondo(min(p, dz.P_BRINK)) - D["e_fondo"] - D["e_solado"])) for p in ps], "SOLADO")
    lam.poli(terr, "TERRENO-EXISTENTE")
    lam.poli(na, "AGUA")
    # achurado de losas
    for i in range(len(ps) - 1):
        a, b_ = ps[i], ps[i + 1]
        lam.achurado([(X(a), Y(D["NPT"])), (X(b_), Y(D["NPT"])), (X(b_), Y(dz.techo(b_))), (X(a), Y(dz.techo(a)))], escala_mm=0.6)
        lam.achurado([(X(a), Y(dz.fondo(min(a, dz.P_BRINK)))), (X(b_), Y(dz.fondo(min(b_, dz.P_BRINK)))), (X(b_), Y(dz.fondo(min(b_, dz.P_BRINK)) - D["e_fondo"])), (X(a), Y(dz.fondo(min(a, dz.P_BRINK)) - D["e_fondo"]))], escala_mm=0.6)
    # registros y cunetas
    for rg in R["registros"]:
        p = rg["prog"]
        if not (p1 - 1e-6 <= p <= p2 + 1e-6) or rg["nombre"] in ("CL", "CC"): continue
        lam.rect(X(p - 0.35), Y(D["NPT"] - 0.10), X(p + 0.35), Y(D["NPT"]), "REGISTRO-TAPA")
        lam.linea((X(p), Y(D["NPT"])), (X(p), Y(D["NPT"]) + 6 * lam.f), "LLAMADAS")
        lam.texto((X(p) + 0.8 * lam.f, Y(D["NPT"]) + 7 * lam.f), "%s  %s" % (rg["nombre"], prog_txt(p)), 1.6, "TEXTOS", TA.LEFT, rot=90)
    for c in R["cunetas"]:
        p = c["prog"]
        if not (p1 - 1e-6 <= p <= p2 + 1e-6): continue
        lam.rect(X(p - 0.3), Y(c["NCF_fin"]), X(p + 0.3), Y(D["NPT"]), "CUNETA")
        lam.linea((X(p), Y(D["NPT"])), (X(p), Y(D["NPT"]) + 6 * lam.f), "LLAMADAS")
        lam.texto((X(p) - 0.8 * lam.f, Y(D["NPT"]) + 7 * lam.f), "Cuneta %s (perfil %s) NCF %.2f" % (c["nombre"].split(" (")[0], c["perfil"], c["NCF_fin"]), 1.6, "CUNETA", TA.RIGHT, rot=90) if False else lam.texto((X(p) - 2.5 * lam.f, Y(D["NPT"]) + 7 * lam.f), "Cuneta %s (perfil %s) NCF %.2f" % (c["nombre"].split(" (")[0], c["perfil"], c["NCF_fin"]), 1.6, "TEXTOS", TA.LEFT, rot=90)
    # cruces
    for z in R["zonas"]:
        a, b_ = max(z["p1"], p1), min(z["p2"], p2)
        if a < b_:
            lam.texto((X((a + b_) / 2), Y(D["NPT"]) + 2.5 * lam.f), "CRUCE DE CAMIONES: losa e=0.25, muros e=0.15" if z["tipo"] == "CAMION" else "CRUCE DE MOTOS", 1.6, "CRUCE-VEHICULAR", TA.BOTTOM_CENTER)
    # cajas en los extremos
    if p1 <= 0.0:
        xcl0 = X(0) - (D["CL_largo"] + D["e_muro"]) * fx
        lam.rect(xcl0, Y(D["CF0"] - D["CL_poza"] - D["e_fondo"]), X(0), Y(D["NPT"]), "CONCRETO")
        lam.rect(xcl0 + D["e_muro"] * fx, Y(D["CF0"] - D["CL_poza"]), X(0), Y(D["NPT"] - D["e_losa"]), "CONCRETO-OCULTO")
        lam.linea((xcl0, Y(D["CF_varones_sup"])), (xcl0 + D["e_muro"] * fx, Y(D["CF_varones_sup"])), "CONCRETO")
        lam.llamada((xcl0, Y(D["CF_varones_sup"])), (xcl0 - 10 * lam.f, Y(D["CF_varones_sup"] + 0.5)), ["CAJA DE LLEGADA CL: poza 0.30 m", "llegada de CAR Varones (cota ref. 260.18)"], 1.6, al=TA.RIGHT)
        lam.nivel((xcl0 + 0.8 * fx, Y(D["CF0"] - D["CL_poza"])), D["CF0"] - D["CL_poza"])
    if p2 >= dz.P_BRINK - 1e-6:
        zp = D["CF_R01"] - D["CC_poza_prof"]
        lam.rect(X(dz.P_BRINK), Y(zp - D["e_fondo"]), X(dz.P_FIN) + D["e_muro"] * fx, Y(D["NPT"]), "CONCRETO")
        lam.rect(X(dz.P_BRINK), Y(zp), X(dz.P_FIN), Y(D["NPT"] - D["e_losa"]), "CONCRETO-OCULTO")
        lam.poli([(X(dz.P_FIN - 0.25), Y(zp)), (X(dz.P_FIN - 0.25), Y(D["CF_R01"])), (X(dz.P_FIN), Y(D["CF_R01"]))], "POZA")
        lam.linea((X(dz.P_BRINK), Y(dz.fondo(dz.P_BRINK))), (X(dz.P_BRINK), Y(zp)), "CONCRETO")
        lam.poli([(X(dz.P_BRINK), Y(perfil_en(R, dz.P_BRINK, "NA"))), (X(dz.P_BRINK + 0.5), Y(zp + R["poza"]["y1"])), (X(dz.P_FIN - 0.3), Y(D["NA_R01"])), (X(dz.P_FIN), Y(D["NA_R01"]))], "AGUA")
        lam.llamada((X(dz.P_BRINK + 1.5), Y(zp)), (X(dz.P_BRINK + 1.5) - 12 * lam.f, Y(zp - 0.9)), ["CAJA DE CAIDA CC: poza 1.50 x 3.50, piso %.2f" % zp, "umbral 0.40 a 258.72; entrega al R-01 de CAR Mujeres"], 1.6, al=TA.RIGHT)
        lam.nivel((X(dz.P_FIN), Y(D["CF_R01"])), D["CF_R01"], texto="CF 258.72 (R-01)")
    # niveles en extremos
    for p in (p1, p2):
        pp = min(p, dz.P_BRINK)
        lam.nivel((X(p), Y(dz.fondo(pp))), dz.fondo(pp), lado=1 if p == p1 else -1)
        lam.nivel((X(p), Y(perfil_en(R, p, "NA"))), perfil_en(R, p, "NA"), texto="NA %.3f" % perfil_en(R, p, "NA"), lado=1 if p == p1 else -1)
    lam.nivel((X(p1 + 2), Y(D["NPT"])), D["NPT"], texto="NPT +%.2f" % D["NPT"])
    # grilla vertical de cotas a la izquierda
    for z in np.arange(258.0, 261.01, 0.5):
        lam.linea((X(p1) - 3 * lam.f, Y(z)), (X(p1) - 1 * lam.f, Y(z)), "GUITARRA")
        lam.texto((X(p1) - 4 * lam.f, Y(z)), "%.2f" % z, 1.4, "TEXTOS", TA.MIDDLE_RIGHT)
    lam.linea((X(p1) - 1 * lam.f, Y(257.6)), (X(p1) - 1 * lam.f, Y(261.0)), "GUITARRA")
    if titulo: lam.texto((X(p1), Y(261.0) + (26 if escH >= 200 else 20) * lam.f), titulo, 3.0, "TITULOS")
    # tabla (guitarra)
    if con_tabla:
        sing = [] if escH >= 200 else sorted(set([r["prog"] for r in R["registros"] if p1 <= r["prog"] <= p2] + [c["prog"] for c in R["cunetas"] if p1 <= c["prog"] <= p2]))
        reg = [round(v, 2) for v in np.arange(p1, p2 + 1e-6, paso_tabla)] + [p2]
        reg = [v for v in reg if all(abs(v - q) > 0.8 for q in sing)]
        cols = sorted(set(reg + sing))
        filas = ["PROGRESIVA", "TERRENO", "LOSA SUP. / NPT", "FONDO", "NIVEL AGUA", "ALTURA h", "PROF. EXCAV."]
        yt = Y(257.6) - 6 * lam.f; dy = (7.0 if escH >= 200 else 4.5) * lam.f
        for i, fnm in enumerate(filas):
            lam.texto((X(p1) - 4 * lam.f, yt - (i + 0.5) * dy), fnm, 1.5, "TEXTOS", TA.MIDDLE_RIGHT)
            lam.linea((X(p1) - 30 * lam.f, yt - i * dy), (X(p2), yt - i * dy), "GUITARRA")
        lam.linea((X(p1) - 30 * lam.f, yt - len(filas) * dy), (X(p2), yt - len(filas) * dy), "GUITARRA")
        for p in cols:
            pp = min(p, dz.P_BRINK)
            vals = [prog_txt(p), "%.3f" % terreno_en(T, p), "%.3f" % D["NPT"], "%.3f" % dz.fondo(pp), "%.3f" % perfil_en(R, p, "NA"),
                    "%.2f" % (dz.techo(p) - dz.fondo(pp)), "%.2f" % (terreno_en(T, p) - dz.fondo(pp) + D["e_fondo"] + D["e_solado"])]
            lam.linea((X(p), yt), (X(p), yt - len(filas) * dy), "GUITARRA")
            lam.linea((X(p), Y(257.6)), (X(p), yt), "GUITARRA")
            for i, v in enumerate(vals):
                lam.texto((X(p), yt - (i + 0.5) * dy), v, 1.5 if escH >= 200 else 1.3, "TEXTOS", TA.MIDDLE_CENTER, rot=0)
    return X, Y


def dp02(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 200, "DP-02", "PERFIL LONGITUDINAL GENERAL DEL COLECTOR",
                   "ESCALA H 1/200 - V 1/50 - NIVELES DE DISENO Y PERFIL HIDRAULICO (0+000.00 - %s)" % prog_txt(dz.P_FIN))
    X, Y = perfil_tramo(lam, 95, 330, 0.0, dz.P_FIN, R, T, 200, 50, True, 10.0, "PERFIL LONGITUDINAL - EJE DEL COLECTOR (H 1/200, V 1/50)")
    lam.leyenda(32, 150, [("linea2", "TERRENO", "piso terminado / losa superior (NPT +260.60)"), ("linea", "TERRENO-EXISTENTE", "terreno existente (superficie topografica)"),
                          ("linea", "CONCRETO", "colector de concreto armado"), ("linea", "SOLADO", "solado e=0.05"), ("linea", "AGUA", "nivel de agua de diseno (Q = 560.6 L/s)"),
                          ("rect", "REGISTRO-TAPA", "registro de limpieza"), ("rect", "CUNETA", "llegada de cuneta"), ("linea", "POZA", "poza de disipacion y umbral")], 1.8)
    lam.notas(300, 150, "NOTAS", [
        "1. Perfil con exageracion vertical x4 (H 1/200, V 1/50). Cotas en m.s.n.m.",
        "2. El nivel de agua de diseno resulta del calculo de flujo gradualmente variado (memoria de calculo, hoja PERFIL_FLUJO); control: tirante critico en el brink de la caida.",
        "3. Caudal de diseno 560.6 L/s: CAR Varones (258.7 L/s, dato de su memoria) + Hogar de Refugio (301.9 L/s), TR 25 anos.",
        "4. Relleno nivelado del retiro hasta la cota de la losa (+260.60) donde el terreno existente queda por debajo.",
        "5. Ver perfil detallado por tramos en las laminas DP-03A y DP-03B.",
    ], 1.7)
    return lam


def dp03(doc, ox, oy, R, T):
    lams = []
    tramos = [(0.0, 20.0), (20.0, 40.0), (40.0, 60.0), (60.0, dz.P_FIN)]
    for k, (cod, pares) in enumerate((("DP-03A", tramos[:2]), ("DP-03B", tramos[2:]))):
        lam = B.Lamina(doc, ox + k * 60, oy, 50, cod, "PERFIL LONGITUDINAL DETALLADO DEL COLECTOR",
                       "TRAMOS %s - ESCALA REAL 1/50 (H = V)" % ("1 Y 2 (0+000.00 - 0+040.00)" if k == 0 else "3 Y 4 (0+040.00 - %s)" % prog_txt(dz.P_FIN)))
        for j, (p1, p2) in enumerate(pares):
            perfil_tramo(lam, 90, 420 - j * 230, p1, p2, R, T, 50, 50, True, 5.0, "TRAMO %d: %s A %s" % (tramos.index((p1, p2)) + 1, prog_txt(p1), prog_txt(p2)))
        lam.leyenda(650, 330, [("linea", "CONCRETO", "concreto armado del colector"), ("linea", "SOLADO", "solado e=0.05"), ("rect", "REGISTRO-TAPA", "tapa de registro"),
                               ("linea", "AGUA", "nivel de agua de diseno"), ("linea2", "TERRENO", "piso terminado +260.60"), ("linea", "TERRENO-EXISTENTE", "terreno existente"),
                               ("rect", "CUNETA", "llegada de cuneta")], 1.8)
        lam.notas(650, 240, "NOTAS", ["1. Escala real: horizontal = vertical.", "2. Cotas en m.s.n.m.; progresivas desde la caja CL.", "3. Prof. excav. medida desde el terreno existente al fondo del solado."], 1.7)
        lams.append(lam)
    return lams
