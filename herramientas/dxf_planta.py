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
    """Perfil longitudinal por el eje del colector entre p1 y p2 (corte): losas cortadas y achuradas, agua, cara interior del
    muro lejano con las ventanas de las cunetas, registros con tapa y borde engrosado, juntas, cruces, cajas CL y CC y el
    colector receptor como referencia. Origen de papel (xmm, ymm) = (p1, cota base)."""
    D = dz.D
    fx = 1.0                        # escala real: 1 unidad de dibujo = 1 m, horizontal = vertical (sin exageracion)
    fy = 1.0
    zb = 257.60                     # cota base del perfil
    detalle = True
    def X(p): return lam.ox + xmm * lam.f + (p - p1) * fx
    def Y(z): return lam.oy + ymm * lam.f + (z - zb) * fy
    def fz(p): return dz.fondo(min(p, dz.P_BRINK))
    ps = [e["p"] for e in R["perfil"] if p1 - 1e-6 <= e["p"] <= p2 + 1e-6]
    for z in R["zonas"]: ps += [z["p1"], z["p2"], z["p1"] - 1e-4, z["p2"] + 1e-4]
    ps = sorted(set([p1, p2] + [q for q in ps if p1 - 1e-6 <= q <= p2 + 1e-6]))
    NPT = D["NPT"]; ef = D["e_fondo"]; es = D["e_solado"]
    regs = [rg for rg in R["registros"] if p1 - 1e-6 <= rg["prog"] <= p2 + 1e-6 and rg["nombre"] not in ("CL", "CC")]
    # ---------- agua (relleno) y nivel de agua
    na = [(X(p), Y(perfil_en(R, p, "NA"))) for p in ps]
    lam.relleno([(X(p), Y(fz(p))) for p in ps] + list(reversed(na)), "AGUA-RELLENO")
    lam.poli(na, "AGUA")
    for p in np.arange(np.ceil(p1 / 10.0) * 10.0, p2 + 1e-6, 10.0):
        if p1 + 1.0 < p < min(p2, dz.P_BRINK) - 1.0: lam.bloque("SIMB-AGUA", (X(p), Y(perfil_en(R, p, "NA"))), lam.f)
    # ---------- losa de fondo (cortada) y solado
    fondo = [(X(p), Y(fz(p))) for p in ps]
    fondo_inf = [(X(p), Y(fz(p) - ef)) for p in ps]
    lam.achurado(fondo + list(reversed(fondo_inf)), escala_mm=0.5)
    lam.poli(fondo, "CONCRETO"); lam.poli(fondo_inf, "CONCRETO")
    lam.poli([(X(p), Y(fz(p) - ef - es)) for p in ps], "SOLADO")
    lam.poli([(X(p1), Y(fz(p1) - ef - es - 0.02)), (X(p2), Y(fz(p2) - ef - es - 0.02))], "EXCAVACION")
    # ---------- losa superior (cortada) con aberturas de registro
    cortes = sorted([(rg["prog"] - 0.35, rg["prog"] + 0.35) for rg in regs])
    a = p1
    tramos_losa = []
    for c1, c2 in cortes:
        if c1 > a: tramos_losa.append((a, c1))
        a = c2
    if a < p2: tramos_losa.append((a, p2))
    for a, b_ in tramos_losa:
        qs = sorted(set([a, b_] + [q for q in ps if a < q < b_]))
        techo = [(X(q), Y(dz.techo(q))) for q in qs]
        lam.achurado([(X(a), Y(NPT)), (X(b_), Y(NPT))] + list(reversed(techo)), escala_mm=0.5)
        lam.poli(techo, "CONCRETO")
        lam.linea((X(a), Y(NPT)), (X(a), Y(dz.techo(a))), "CONCRETO"); lam.linea((X(b_), Y(NPT)), (X(b_), Y(dz.techo(b_))), "CONCRETO")
    lam.poli([(X(p1), Y(NPT)), (X(p2), Y(NPT))], "TERRENO", ancho=0.35 * lam.f)
    # ---------- registros: borde engrosado, contramarco, tapa
    for rg in regs:
        p = rg["prog"]; zt = dz.techo(p)
        for sgn in (-1, 1):
            xa, xb = sorted([X(p + sgn * 0.35), X(p + sgn * 0.50)])
            lam.rect(xa, Y(zt - 0.10), xb, Y(zt), "CONCRETO"); lam.achurado([(xa, Y(zt - 0.10)), (xb, Y(zt - 0.10)), (xb, Y(zt)), (xa, Y(zt))], escala_mm=0.5)
        lam.rect(X(p - 0.34), Y(NPT - 0.08), X(p + 0.34), Y(NPT), "REGISTRO-TAPA")
        lam.linea((X(p - 0.35), Y(NPT - 0.10)), (X(p - 0.35), Y(NPT)), "MARCO-METALICO"); lam.linea((X(p + 0.35), Y(NPT - 0.10)), (X(p + 0.35), Y(NPT)), "MARCO-METALICO")
        lam.linea((X(p), Y(NPT)), (X(p), Y(NPT) + 5 * lam.f), "LLAMADAS")
        lam.texto((X(p) + 0.8 * lam.f, Y(NPT) + 6 * lam.f), "%s  %s" % (rg["nombre"], prog_txt(p)), 1.6, "REGISTRO", TA.LEFT, rot=90)
    # ---------- cunetas que llegan: ventana 0.40 x H en el muro lejano (lado predio) y caida al fondo
    for c in R["cunetas"]:
        p = c["prog"]
        if not (p1 - 1e-6 <= p <= p2 + 1e-6): continue
        zt = dz.techo(p); zv = c["NCF_fin"]
        lam.rect(X(p - 0.20), Y(zv), X(p + 0.20), Y(zt), "CUNETA")
        lam.relleno([(X(p - 0.20), Y(zv)), (X(p + 0.20), Y(zv)), (X(p + 0.20), Y(zt)), (X(p - 0.20), Y(zt))], "ISO-CUNETA")
        lam.linea((X(p - 0.20), Y(zv)), (X(p + 0.20), Y(zv)), "CUNETA")      # fondo de la cuneta en la ventana (NCF)
        lam.bloque("SIMB-FLECHA", (X(p), Y((zv + perfil_en(R, p, "NA")) / 2)), lam.f * 0.7, rot=-90, capa="FLUJO")
        lam.linea((X(p), Y(NPT)), (X(p), Y(NPT) + 5 * lam.f), "LLAMADAS")
        lam.texto((X(p) - 1.0 * lam.f, Y(NPT) + 6 * lam.f), "CUNETA %s - NCF %.2f" % (c["nombre"].split(" (")[0].upper(), zv), 1.6, "CUNETA", TA.LEFT, rot=90)
        lam.texto((X(p) - 3.6 * lam.f, Y(NPT) + 6 * lam.f), "ventana 0.40 x %.2f (perfil %s)" % (zt - zv, c["perfil"]), 1.4, "CUNETA", TA.LEFT, rot=90)
    # ---------- juntas de dilatacion cada 4.00 m
    for pj in np.arange(4.0, dz.P_BRINK - 0.5, 4.0):
        if p1 < pj < p2:
            lam.linea((X(pj), Y(NPT)), (X(pj), Y(dz.techo(pj))), "JUNTAS"); lam.linea((X(pj), Y(fz(pj))), (X(pj), Y(fz(pj) - ef)), "JUNTAS")
            if detalle: lam.texto((X(pj), Y(fz(pj) - ef) - 1.5 * lam.f), "J", 1.3, "JUNTAS", TA.TOP_CENTER)
    # ---------- cruces vehiculares
    for z in R["zonas"]:
        a, b_ = max(z["p1"], p1), min(z["p2"], p2)
        if a < b_:
            yb = Y(NPT) + 2.0 * lam.f
            lam.linea((X(a), yb), (X(b_), yb), "CRUCE-VEHICULAR"); lam.linea((X(a), yb - 1.0 * lam.f), (X(a), yb + 1.0 * lam.f), "CRUCE-VEHICULAR"); lam.linea((X(b_), yb - 1.0 * lam.f), (X(b_), yb + 1.0 * lam.f), "CRUCE-VEHICULAR")
            lam.texto((X((a + b_) / 2), yb + 1.5 * lam.f), "CRUCE DE CAMIONES: losa e=0.25, doble marco 1/2\"" if z["tipo"] == "CAMION" else "CRUCE DE MOTOS: marco 3/8\" @0.15", 1.5, "CRUCE-VEHICULAR", TA.BOTTOM_CENTER)
    # ---------- caja de llegada CL (0+000) y llegada del aporte externo
    if p1 <= 0.0:
        e = D["e_muro"]; zp = D["CF0"] - D["CL_poza"]
        xi = X(0) - D["CL_largo"] * fx; xo = xi - e * fx
        lam.rect(xo, Y(zp - ef), X(0), Y(NPT), "CONCRETO")
        lam.achurado([(xo, Y(zp - ef)), (X(0), Y(zp - ef)), (X(0), Y(zp)), (xo, Y(zp))], escala_mm=0.5)       # fondo de la caja
        lam.achurado([(xo, Y(zp)), (xi, Y(zp)), (xi, Y(D["CF_varones_sup"])), (xo, Y(D["CF_varones_sup"]))], escala_mm=0.5)   # muro de llegada bajo la ventana
        lam.achurado([(xo, Y(D["CF_varones_sup"] + 0.70)), (xi, Y(D["CF_varones_sup"] + 0.70)), (xi, Y(NPT)), (xo, Y(NPT))], escala_mm=0.5)
        lam.achurado([(xo, Y(NPT - D["e_losa"])), (X(0) - 0.35 * fx, Y(NPT - D["e_losa"])), (X(0) - 0.35 * fx, Y(NPT)), (xo, Y(NPT))], escala_mm=0.5)   # losa de la caja
        lam.rect(X(0) - 0.35 * fx - 0.34 * fx, Y(NPT - 0.08), X(0) - 0.35 * fx + 0.34 * fx, Y(NPT), "REGISTRO-TAPA")
        lam.linea((xi, Y(zp)), (xi, Y(D["CF_varones_sup"])), "CONCRETO"); lam.linea((xi, Y(D["CF_varones_sup"] + 0.70)), (xi, Y(NPT - D["e_losa"])), "CONCRETO")
        lam.linea((X(0), Y(zp)), (X(0), Y(fz(0))), "CONCRETO")
        lam.poli([(xi, Y(zp - ef - es)), (X(0), Y(zp - ef - es))], "SOLADO")
        # colector del CAR Varones (referencia): llega por la ventana del muro
        lam.rect(xo - 1.2 * fx, Y(D["CF_varones_sup"] - 0.15), xo, Y(D["CF_varones_sup"] + 0.70 + 0.10), "ARQ-BASE")
        lam.rect(xo - 1.2 * fx, Y(D["CF_varones_sup"]), xo, Y(D["CF_varones_sup"] + 0.70), "ARQ-BASE")
        lam.poli([(xo - 1.2 * fx, Y(D["CF_varones_sup"] + 0.35)), (xo, Y(D["CF_varones_sup"] + 0.35)), (xi + 0.3 * fx, Y(D["CF_varones_sup"] + 0.1)), (xi + 0.6 * fx, Y(zp + R["caja_llegada"]["tirante_poza"]))], "AGUA")
        lam.relleno([(xi, Y(zp)), (X(0), Y(zp)), (X(0), Y(perfil_en(R, 0.0, "NA"))), (xi, Y(perfil_en(R, 0.0, "NA")))], "AGUA-RELLENO")
        lam.llamada((xo - 0.6 * fx, Y(D["CF_varones_sup"] + 0.8)), (xo + 0.2 * fx, Y(NPT + 0.9)), ["COLECTOR CAR VARONES (CUI 2705619), referencia", "cota de fondo de llegada %.2f por confirmar" % D["CF_varones_sup"]], 1.6, al=TA.LEFT)
        lam.llamada((xi + 0.5 * fx, Y(zp)), (xo + 0.1 * fx, Y(zp - 0.75)), ["CAJA DE LLEGADA CL: interior %.2f x %.2f" % (D["CL_largo"], D["CL_ancho"]), "poza %.2f m, piso %.2f; colchon de agua %.2f m" % (D["CL_poza"], zp, R["caja_llegada"]["tirante_poza"])], 1.6, al=TA.LEFT)
        lam.nivel((xi + 0.3 * fx, Y(zp)), zp, lado=1)
        lam.cota((xi, Y(zp)), (xi, Y(D["CF_varones_sup"])), -8, horizontal=False, texto="%.2f" % (D["CF_varones_sup"] - zp))
    # ---------- caja de caida CC y colector receptor
    if p2 >= dz.P_BRINK - 1e-6:
        e = D["e_muro"]; zp = D["CF_R01"] - D["CC_poza_prof"]; pb, pf = dz.P_BRINK, dz.P_FIN
        xf = X(pf); xfe = xf + e * fx
        lam.rect(X(pb), Y(zp - ef), xfe, Y(NPT), "CONCRETO")
        lam.achurado([(X(pb), Y(zp - ef)), (xfe, Y(zp - ef)), (xfe, Y(zp)), (X(pb), Y(zp))], escala_mm=0.5)
        lam.achurado([(X(pb), Y(fz(pb) - ef)), (X(pb) + 0.0, Y(fz(pb) - ef)), (X(pb), Y(fz(pb))), (X(pb), Y(fz(pb)))], escala_mm=0.5)
        lam.achurado([(xf, Y(zp)), (xfe, Y(zp)), (xfe, Y(D["CF_R01"])), (xf, Y(D["CF_R01"]))], escala_mm=0.5)                      # muro bajo la ventana de salida
        lam.achurado([(xf, Y(D["NPT_wilma"] - 0.10)), (xfe, Y(D["NPT_wilma"] - 0.10)), (xfe, Y(NPT)), (xf, Y(NPT))], escala_mm=0.5)  # muro sobre la ventana de salida
        lam.achurado([(X(pb + 0.35), Y(NPT - D["e_losa"])), (xfe, Y(NPT - D["e_losa"])), (xfe, Y(NPT)), (X(pb + 0.35), Y(NPT))], escala_mm=0.5)
        lam.linea((X(pb), Y(fz(pb))), (X(pb), Y(zp)), "CONCRETO"); lam.linea((X(pb), Y(fz(pb) - ef)), (X(pb), Y(zp - ef)), "CONCRETO-OCULTO")
        lam.linea((xf, Y(zp)), (xf, Y(D["CF_R01"])), "CONCRETO"); lam.linea((xf, Y(D["NPT_wilma"] - 0.10)), (xf, Y(NPT - D["e_losa"])), "CONCRETO")
        # umbral de salida 0.25 x 0.40
        lam.rect(X(pf - 0.25), Y(zp), xf, Y(D["CF_R01"]), "POZA"); lam.achurado([(X(pf - 0.25), Y(zp)), (xf, Y(zp)), (xf, Y(D["CF_R01"])), (X(pf - 0.25), Y(D["CF_R01"]))], escala_mm=0.4)
        lam.poli([(X(pb), Y(zp - ef - es)), (xfe, Y(zp - ef - es))], "SOLADO")
        for pr in (pb + 0.6, pf - 1.0):
            lam.rect(X(pr - 0.34), Y(NPT - 0.08), X(pr + 0.34), Y(NPT), "REGISTRO-TAPA")
        # agua: caida libre, resalto ahogado y salida sobre el umbral
        y1 = R["poza"]["y1"]; nab = perfil_en(R, pb, "NA")
        agua = [(X(pb), Y(nab)), (X(pb + 0.45), Y(zp + y1 + 0.05)), (X(pb + 0.9), Y(zp + y1)), (X(pb + 1.6), Y(zp + R["poza"]["y2"] * 0.7)), (X(pb + 2.4), Y(D["NA_R01"])), (xf, Y(D["NA_R01"])), (xfe + 1.0 * fx, Y(D["NA_R01"]))]
        lam.relleno([(X(pb), Y(zp)), (X(pf - 0.25), Y(zp)), (X(pf - 0.25), Y(D["CF_R01"])), (xfe + 1.0 * fx, Y(D["CF_R01"]))] + list(reversed(agua)), "AGUA-RELLENO")
        lam.poli(agua, "AGUA")
        # colector receptor CAR Mujeres (referencia)
        xr2 = xfe + 1.0 * fx
        lam.rect(xfe, Y(D["CF_R01"] - 0.15), xr2, Y(D["NPT_wilma"]), "ARQ-BASE"); lam.rect(xfe, Y(D["CF_R01"]), xr2, Y(D["NPT_wilma"] - 0.10), "ARQ-BASE")
        lam.poli([(xfe, Y(NPT)), (xr2, Y(NPT))], "TERRENO-EXISTENTE")
        lam.llamada((xfe + 0.5 * fx, Y(D["NPT_wilma"])), (xfe + 0.5 * fx, Y(NPT + 0.9)), ["COLECTOR CAR MUJERES (CUI 2717013), referencia", "R-01: cota de fondo %.2f, losa %.2f, b=%.2f" % (D["CF_R01"], D["NPT_wilma"], D["b_wilma"])], 1.6, al=TA.RIGHT)
        lam.llamada((X(pb + 1.5), Y(zp)), (X(pb + 1.5), Y(zp - 0.75)), ["CAJA DE CAIDA CC: poza %.2f x %.2f, piso %.2f" % (D["CC_ancho"], D["CC_poza_largo"], zp), "umbral 0.25 x 0.40 a %.2f; resalto ahogado (y2 %.2f < %.2f)" % (D["CF_R01"], R["poza"]["y2"], R["poza"]["tirante_disp"])], 1.6, al=TA.LEFT)
        lam.nivel((xf + 0.5 * fx, Y(D["CF_R01"])), D["CF_R01"], texto="CF %.2f (R-01)" % D["CF_R01"], lado=1)
        lam.nivel((X(pb + 2.2), Y(zp)), zp, lado=1)
        lam.cota((X(pb), Y(zp)), (X(pb), Y(fz(pb))), -8, horizontal=False, texto="caida %.2f" % (fz(pb) - zp))
        lam.cota((X(pb), Y(zp - ef - es)), (X(pf), Y(zp - ef - es)), -6, texto="%.2f" % (pf - pb))
    # ---------- cotas de altura interior
    for pm in ([p1 + 0.3 * (p2 - p1), p1 + 0.7 * (p2 - p1)] if detalle else [p1 + 0.5 * (p2 - p1)]):
        pm = min(pm, dz.P_BRINK - 1.0)
        if any(abs(pm - rg["prog"]) < 1.0 for rg in regs) or any(abs(pm - c["prog"]) < 1.0 for c in R["cunetas"]): pm += 1.2
        lam.cota((X(pm), Y(fz(pm))), (X(pm), Y(dz.techo(pm))), 0, horizontal=False, texto="h=%.2f" % (dz.techo(pm) - fz(pm)))
    # ---------- niveles en extremos, NPT, terreno
    lam.poli([(X(t["p"]), Y(t["z"])) for t in T if p1 - 1e-6 <= t["p"] <= p2 + 1e-6], "TERRENO-EXISTENTE")
    for p in (p1, p2):
        pp = min(p, dz.P_BRINK)
        lam.nivel((X(p), Y(fz(pp))), fz(pp), texto="CF %.2f" % fz(pp), lado=1 if p == p1 else -1)
        lam.nivel((X(p), Y(perfil_en(R, p, "NA"))), perfil_en(R, p, "NA"), texto="NA %.3f" % perfil_en(R, p, "NA"), lado=1 if p == p1 else -1)
    lam.nivel((X(p1 + 2.5), Y(NPT)), NPT, texto="NPT +%.2f (losa superior = piso terminado)" % NPT)
    lam.texto((X(p1 + 1.0), Y(fz(p1 + 1.0)) - 4.5 * lam.f), "S = %.2f %%" % (D["S"] * 100), 1.8, "TEXTOS", TA.LEFT)
    # ---------- escala vertical de cotas
    for z in np.arange(258.0, 261.01, 0.5):
        lam.linea((X(p1) - 3 * lam.f, Y(z)), (X(p1) - 1 * lam.f, Y(z)), "GUITARRA")
        lam.texto((X(p1) - 4 * lam.f, Y(z)), "%.2f" % z, 1.4, "TEXTOS", TA.MIDDLE_RIGHT)
    lam.linea((X(p1) - 1 * lam.f, Y(257.6)), (X(p1) - 1 * lam.f, Y(261.0)), "GUITARRA")
    if titulo: lam.texto((X(p1), Y(261.0) + 44 * lam.f), titulo, 3.0, "TITULOS")
    # ---------- tabla (guitarra)
    if con_tabla:
        sing_r = [r["prog"] for r in R["registros"] if p1 <= r["prog"] <= p2]
        sing = sorted(set(sing_r + [c["prog"] for c in R["cunetas"] if p1 <= c["prog"] <= p2 and all(abs(c["prog"] - q) > (1.2 if detalle else 0.8) for q in sing_r)]))
        reg = [round(v, 2) for v in np.arange(p1, p2 + 1e-6, paso_tabla)] + [p2]
        reg = [v for v in reg if all(abs(v - q) > (1.2 if detalle else 0.8) for q in sing)]
        cols = sorted(set(reg + sing))
        filas = ["PROGRESIVA", "TERRENO", "LOSA SUP. / NPT", "FONDO", "NIVEL AGUA", "ALTURA h", "PROF. EXCAV."]
        yt = Y(257.6) - 6 * lam.f; dy = 6.0 * lam.f
        for i, fnm in enumerate(filas):
            lam.texto((X(p1) - 4 * lam.f, yt - (i + 0.5) * dy), fnm, 1.5, "TEXTOS", TA.MIDDLE_RIGHT)
            lam.linea((X(p1) - 30 * lam.f, yt - i * dy), (X(p2), yt - i * dy), "GUITARRA")
        lam.linea((X(p1) - 30 * lam.f, yt - len(filas) * dy), (X(p2), yt - len(filas) * dy), "GUITARRA")
        for p in cols:
            pp = min(p, dz.P_BRINK)
            vals = [prog_txt(p), "%.3f" % terreno_en(T, p), "%.3f" % NPT, "%.3f" % fz(pp), "%.3f" % perfil_en(R, p, "NA"),
                    "%.2f" % (dz.techo(p) - fz(pp)), "%.2f" % (terreno_en(T, p) - fz(pp) + ef + es)]
            lam.linea((X(p), yt), (X(p), yt - len(filas) * dy), "GUITARRA")
            lam.linea((X(p), Y(257.6)), (X(p), yt), "GUITARRA")
            for i, v in enumerate(vals):
                lam.texto((X(p), yt - (i + 0.5) * dy), v, 1.4, "PROGRESIVAS" if i == 0 else "TEXTOS", TA.MIDDLE_CENTER, rot=0)
    return X, Y


def dp02(doc, ox, oy, R, T):
    """Perfil general en dos franjas a escala real 1/50 (H = V, 1 unidad = 1 m)."""
    lam = B.Lamina(doc, ox, oy, 50, "DP-02", "PERFIL LONGITUDINAL GENERAL DEL COLECTOR",
                   "ESCALA REAL 1/50 (H = V) - CORTE POR EL EJE EN DOS FRANJAS: NIVELES DE DISENO, PERFIL HIDRAULICO, CAJAS, REGISTROS Y EMPALMES (0+000.00 - %s)" % prog_txt(dz.P_FIN))
    pm = 36.0
    perfil_tramo(lam, 72, 450, 0.0, pm, R, T, 50, 50, True, 5.0, "FRANJA 1: %s A %s - CORTE POR EL EJE DEL COLECTOR (ESC. 1/50, H = V)" % (prog_txt(0.0), prog_txt(pm)))
    perfil_tramo(lam, 45, 262, pm, dz.P_FIN, R, T, 50, 50, True, 5.0, "FRANJA 2: %s A %s - CORTE POR EL EJE DEL COLECTOR (ESC. 1/50, H = V)" % (prog_txt(pm), prog_txt(dz.P_FIN)))
    lam.leyenda(32, 150, [("linea2", "TERRENO", "piso terminado / losa superior (NPT +260.60)"), ("linea", "TERRENO-EXISTENTE", "terreno existente (superficie topografica)"),
                          ("achurado", "CONCRETO-ACHURADO", "concreto armado cortado (losas, cajas)"), ("linea", "SOLADO", "solado e=0.05 y limite de excavacion"),
                          ("relleno", "AGUA-RELLENO", "agua: nivel de diseno (Q = 560.6 L/s)"), ("rect", "REGISTRO-TAPA", "tapa de registro 0.68 x 0.68 x 0.08"),
                          ("relleno", "ISO-CUNETA", "ventana de llegada de cuneta 0.40 x H en el muro lado predio (cara interior)"), ("linea", "JUNTAS", "junta de dilatacion cada 4.00 m"),
                          ("rect", "POZA", "umbral de la poza de disipacion"), ("rect", "ARQ-BASE", "colectores vecinos (referencia)")], 1.8)
    lam.notas(330, 150, "NOTAS", [
        "1. Corte longitudinal por el eje a escala real 1/50, horizontal = vertical, sin exageracion. Cotas en m.s.n.m. Se ve la cara interior del muro lado predio con las ventanas de las cunetas.",
        "2. El nivel de agua de diseno resulta del calculo de flujo gradualmente variado (memoria de calculo, hoja PERFIL_FLUJO); control: tirante critico en la caida libre a la caja CC.",
        "3. Caudal de diseno 560.6 L/s: CAR Varones (258.7 L/s, dato de su memoria) + Hogar de Refugio (301.9 L/s), TR 25 anos. Velocidad 1.35 m/s (autolimpieza, CE.040).",
        "4. Registros con tapa de concreto 0.68 x 0.68 x 0.08, borde engrosado 0.15 x 0.10 y contramarco metalico (DP-06B). No hay registros dentro de los cruces vehiculares.",
        "5. Relleno nivelado del retiro hasta la cota de la losa (+260.60) donde el terreno existente queda por debajo.",
        "6. Perfil por tramos de 20 m en las laminas DP-03A y DP-03B (misma escala); cajas en DP-07; empalme de cunetas en DP-06C.",
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
        lam.leyenda(650, 330, [("achurado", "CONCRETO-ACHURADO", "concreto armado cortado"), ("linea", "SOLADO", "solado e=0.05"), ("rect", "REGISTRO-TAPA", "tapa de registro"),
                               ("relleno", "AGUA-RELLENO", "agua (nivel de diseno)"), ("linea2", "TERRENO", "piso terminado +260.60"), ("linea", "TERRENO-EXISTENTE", "terreno existente"),
                               ("relleno", "ISO-CUNETA", "ventana de llegada de cuneta"), ("linea", "JUNTAS", "junta de dilatacion cada 4.00 m")], 1.8)
        lam.notas(650, 240, "NOTAS", ["1. Escala real: horizontal = vertical.", "2. Cotas en m.s.n.m.; progresivas desde la caja CL.", "3. Prof. excav. medida desde el terreno existente al fondo del solado."], 1.7)
        lams.append(lam)
    return lams
