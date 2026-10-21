"""Perfiles longitudinales por eje y cortes de cada seccion - I.E. N.° 0590, Barranquita.

Estilo pedido por el usuario (laminas del CAR Mujeres):
- Un perfil por eje de cuneta (EJE-01 ... EJE-19), escala H = V = 1/50.
- Borde superior (NCT) en azul en los tramos abiertos y en verde en los tramos tapados (cara superior e inferior de la losa);
  cota de fondo (NCF) en magenta (cara superior e inferior de la losa de fondo); cada seccion con una linea roja vertical.
- Lineas de referencia "Altura relativa al NPT (m)" cada 0.15 m (0.00 = NPT +184.65).
- Arriba de cada seccion su recuadro: SECCION nn, NCT, NCF, H, EL, EM y con que eje se conecta.
- Guitarra: Progresiva (m), Etiqueta, Longitud (m) y Pendiente (%); progresivas cada 5 m.
- Secciones (numeradas en orden, todos los ejes): inicio y fin de cada eje, cada nudo (quiebre, empalme, descarga), cada inicio y
  fin de tramo tapado y cada cambio de borde (patio de maniobra). Cada seccion tiene su corte transversal a 1/20.
Solo dibuja con los datos de diseno.json (no cambia ninguna cota ni ningun eje). Lo usa planos_b.py.
"""
import math
import dxf_base as B
from ezdxf.enums import TextEntityAlignment as TA
import diseno_b as DS

ESC_P, ESC_S = 50, 20                  # escala de perfiles y de cortes
ANCHO_LAM = 800.0                      # mm utiles por franja (x de 27 a 827)
CAB = 34.0                             # columna de encabezados de la guitarra (mm)
FILAS = ["Progresiva (m)", "Etiqueta", "Longitud (m)", "Pendiente (%)"]
ALTO_FILA = 6.5
EL, EM = 0.10, DS.E_MURO               # espesor de losa de fondo y de muro
NPT = DS.NPT
PASO_REF = 0.15
CAJA_W, CAJA_PASO = 25.0, 34.0         # ancho del recuadro de seccion y paso entre filas de recuadros (mm)
CAPAS = [("PERF-NCT", 5, "CONTINUOUS"), ("PERF-TAPA", 3, "CONTINUOUS"), ("PERF-FONDO", 6, "CONTINUOUS"), ("PERF-SECCION", 1, "CONTINUOUS"),
         ("PERF-REF", 9, "CONTINUOUS"), ("PERF-CAJA", 7, "CONTINUOUS"), ("SEC-ABIERTA", 5, "CONTINUOUS"), ("SEC-TAPADA", 3, "CONTINUOUS"),
         ("SEC-ACERO", 6, "CONTINUOUS"), ("SEC-ACERO-LONG", 5, "CONTINUOUS"), ("SEC-REJILLA", 1, "CONTINUOUS"), ("SEC-PISO", 8, "CONTINUOUS"),
         ("SEC-JUNTA", 8, "CONTINUOUS")]
GROSOR = {"PERF-NCT": 35, "PERF-TAPA": 35, "PERF-FONDO": 35, "PERF-SECCION": 25, "PERF-REF": 9, "SEC-ABIERTA": 35, "SEC-TAPADA": 35,
          "SEC-ACERO": 50, "SEC-REJILLA": 35, "SEC-PISO": 25}


def capas(doc):
    for n, c, lt in CAPAS:
        if n not in doc.layers:
            doc.layers.add(n, color=c, linetype=lt)
        if n in GROSOR: doc.layers.get(n).dxf.lineweight = GROSOR[n]
    B.COLOR_RGB["SEC-JUNTA"] = (70, 70, 70)


def prog(s):
    return "0+%06.2f" % s


# ----------------------------------------------------------------------------- secciones de cada eje
def _valor(P, s):
    """(rasante, fondo) en la progresiva s (interpolado entre los puntos del perfil cada 0.5 m)."""
    for i in range(1, len(P)):
        if P[i][0] >= s - 1e-9:
            a, b = P[i - 1], P[i]; t = 0 if b[0] == a[0] else (s - a[0]) / (b[0] - a[0])
            return a[1] + t * (b[1] - a[1]), a[2] + t * (b[2] - a[2])
    return P[-1][1], P[-1][2]


def _tapado(r, s):
    return any(a - 1e-6 <= s <= b + 1e-6 for a, b in r["tapados"])


def secciones(R):
    """Lista de secciones por eje: {eje: [dict(n, s, nct, ncf, h, tap, nota)]}; numeracion correlativa en el orden de los ejes."""
    llegan = {}                                            # nudo -> ejes que terminan en el
    for r in R["ramales"]: llegan.setdefault(r["nudos"][-1], []).append(r["codigo"])
    recibe = {}                                            # eje -> eje que lo recibe en su nudo final
    for r in R["ramales"]:
        fin = r["nudos"][-1]
        for r2 in R["ramales"]:
            if r2 is not r and fin in r2["nudos"][1:]: recibe[r["codigo"]] = r2["codigo"]
    out, k = {}, 0
    for r in R["ramales"]:
        P = r["perfil"]; L = r["L"]; cand = []
        acc = 0.0; nodos = [(0.0, r["nudos"][0])]
        for t in r["tramos"]: acc += t["L"]; nodos.append((min(acc, L), t["a"]))
        nodos[-1] = (L, nodos[-1][1])                      # la suma de tramos redondeados puede pasar L en 0.01
        for s, n in nodos:
            nota = ""
            if n in llegan and n != r["nudos"][-1]:
                nota = "Llega " + ", ".join(c for c in llegan[n] if c != r["codigo"])
            if s == 0.0: nota = nota or "Inicio del eje"
            if not nota and 0.0 < s < L:                   # quiebre en planta: solo lleva seccion si cambia la pendiente del fondo
                k = [i for i, (s_, n_) in enumerate(nodos) if n_ == n][0]
                sa = (_valor(P, nodos[k - 1][0])[1] - _valor(P, s)[1]) / max(s - nodos[k - 1][0], 1e-6)
                sb = (_valor(P, s)[1] - _valor(P, nodos[k + 1][0])[1]) / max(nodos[k + 1][0] - s, 1e-6)
                if abs(sa - sb) < 0.0005 or "~" in n: continue
            if n == r["nudos"][-1]:
                if n in DS.DESCARGAS: nota = "Descarga " + n
                else:
                    r2 = next(x for x in R["ramales"] if x["codigo"] == recibe.get(r["codigo"]))
                    acc2 = 0.0; s2 = 0.0
                    for t in r2["tramos"]:
                        acc2 += t["L"]
                        if t["a"] == n: s2 = acc2
                    caida = r["perfil"][-1][2] - _valor(r2["perfil"], min(s2, r2["L"]))[1]
                    nota = "Entrega a %s" % r2["codigo"] + ("; caida %.2f m" % caida if caida > 0.02 else "")
            cand.append([s, nota, 3])
        for a, b in r["tapados"]:
            for s in (a, b):
                if 0.2 < s < L - 0.2: cand.append([s, "Inicio de tapado" if s == a else "Fin de tapado", 2])
        for i in range(1, len(P)):                         # cambio de borde (patio de maniobra +184.50)
            if abs(P[i][1] - P[i - 1][1]) > 0.02 and P[i][1] > 184.0 and P[i - 1][1] > 184.0:
                cand.append([P[i - 1][0], "Cambio de borde", 1]); cand.append([P[i][0], "Cambio de borde", 1])
        cand.sort(key=lambda c: (c[0], -c[2]))
        sel = []
        for c in cand:                                     # se juntan las secciones a menos de 0.25 m (queda la del nudo)
            if sel and c[0] - sel[-1][0] < 0.25:
                notas = [t for t in (sel[-1][1], c[1]) if t]
                if c[2] > sel[-1][2]: sel[-1] = list(c)
                sel[-1][1] = "; ".join(dict.fromkeys(t for n_ in notas for t in n_.split("; ")))
                continue
            sel.append(list(c))
        lst = []
        for s, nota, _ in sel:
            nct, ncf = _valor(P, s); k += 1
            tap = _tapado(r, s + 0.01) if s < L - 0.01 else _tapado(r, s - 0.01)
            lst.append({"n": k, "s": s, "nct": nct, "ncf": ncf, "h": nct - ncf, "tap": tap, "nota": nota, "eje": r["codigo"]})
        out[r["codigo"]] = lst
    return out


# ----------------------------------------------------------------------------- perfil de un tramo de eje
def _franjas(R):
    """Cada eje largo se parte en tramos iguales que entran en una franja; los tramos se juntan en franjas sin pasar el ancho."""
    f = ESC_P / 1000.0; largo = (ANCHO_LAM - CAB - 14) * f
    franjas, cur, usado = [], [], 0.0
    for r in R["ramales"]:
        n = max(1, math.ceil(r["L"] / largo - 1e-9)); paso = r["L"] / n
        for k in range(n):
            w = CAB + paso / f + 14
            if cur and usado + w > ANCHO_LAM:
                franjas.append(cur); cur, usado = [], 0.0
            cur.append((r, k * paso, (k + 1) * paso, n)); usado += w
    if cur: franjas.append(cur)
    return franjas


def _filas_cajas(secs, xs, x_min, x_max, ancho):
    """Reparte los recuadros en filas sin traslape. Devuelve [(fila, xc)] en el orden de secs."""
    paso = ancho + 2.0
    filas = 1
    while len(secs) * paso > (x_max - x_min) * filas and filas < 4: filas += 1
    res = [None] * len(secs)
    for f in range(filas):
        idx = [i for i in range(len(secs)) if i % filas == f]
        pos = []
        for j, i in enumerate(idx):
            c = max(xs[i], x_min + ancho / 2) if not pos else max(xs[i], pos[-1] + paso)
            pos.append(c)
        for j in range(len(pos) - 1, -1, -1):          # si se pasan del borde derecho se corren a la izquierda
            lim = x_max - ancho / 2 if j == len(pos) - 1 else pos[j + 1] - paso
            pos[j] = min(pos[j], lim)
        for i, c in zip(idx, pos): res[i] = (f, c)
    return res, filas


def alto_pieza(R, SEC, pz):
    r, s0, s1, n = pz
    P = [p for p in r["perfil"] if s0 - 1e-6 <= p[0] <= s1 + 1e-6]
    zmin = min(p[2] for p in P) - EL
    nref = math.ceil((NPT - zmin) / PASO_REF + 1e-9)
    secs = [x for x in SEC[r["codigo"]] if s0 - 1e-6 <= x["s"] <= s1 + 1e-6]
    f = ESC_P / 1000.0
    xs = [(x["s"] - s0) / f for x in secs]
    _, filas = _filas_cajas(secs, xs, -6, (s1 - s0) / f + 6, CAJA_W)
    return ALTO_FILA * len(FILAS) + 10 + nref * PASO_REF / f + 14 + filas * CAJA_PASO + 9, filas


def perfil(lam, R, SEC, pz, xmm, ymm):
    """Dibuja la pieza pz con la guitarra apoyada en (xmm, ymm) (mm de papel, esquina inferior izquierda)."""
    r, s0, s1, n = pz
    f = lam.f
    P = [p for p in r["perfil"] if s0 - 1e-6 <= p[0] <= s1 + 1e-6]
    secs = [x for x in SEC[r["codigo"]] if s0 - 1e-6 <= x["s"] <= s1 + 1e-6]
    zmin = min(p[2] for p in P) - EL
    nref = math.ceil((NPT - zmin) / PASO_REF + 1e-9)
    xg0, xd0 = xmm, xmm + CAB                          # guitarra y comienzo del dibujo
    X = lambda s: lam.P(xd0 + (s - s0) / f, 0)[0]
    yg = ymm; yg1 = yg + ALTO_FILA * len(FILAS)
    yb = yg1 + 10                                       # linea de referencia mas baja
    y0 = yb + nref * PASO_REF / f                       # 0.00 = NPT
    Yz = lambda z: lam.P(0, y0 + (z - NPT) / f)[1]
    xfin = X(s1)
    # guitarra
    for i, t in enumerate(FILAS + [None]):
        yy = yg1 - i * ALTO_FILA
        lam.linea(lam.P(xg0, yy), (xfin, lam.P(0, yy)[1]), "GUITARRA")
        if t: lam.texto(lam.P(xd0 - 2, yy - ALTO_FILA / 2), t, 1.55, "TEXTOS", TA.MIDDLE_RIGHT)
    lam.linea(lam.P(xd0, yg), lam.P(xd0, yg1), "GUITARRA")
    # lineas de referencia (altura relativa al NPT) y su rotulo
    for i in range(nref + 1):
        z = NPT - i * PASO_REF
        lam.linea((X(s0) - 3 * f, Yz(z)), (xfin, Yz(z)), "PERF-REF")
        lam.texto((X(s0) - 3.5 * f, Yz(z)), "%.2f" % (-i * PASO_REF), 1.15, "TEXTOS", TA.MIDDLE_RIGHT)
    lam.textos(lam.P(xg0, y0 - 3), ["Altura relativa", "al NPT (m)"], 1.6, "TEXTOS", TA.LEFT)
    # cuadricula cada 5 m y progresivas
    k = math.ceil(s0 / 5.0 - 1e-9) * 5
    marcas = []
    while k <= s1 + 1e-6:
        marcas.append(k); k += 5
    for k in marcas:
        lam.linea((X(k), lam.P(0, yb)[1]), (X(k), lam.P(0, yg)[1]), "GRILLA")
        if (s1 - k) / f > 18 or abs(s1 - k) < 1e-6:
            lam.texto((X(k), lam.P(0, yg1 + 3)[1]), "0+%02d" % k, 1.6, "TEXTOS", TA.BOTTOM_CENTER)
    if abs(s1 - marcas[-1]) > 1e-6 if marcas else True:
        lam.texto((xfin, lam.P(0, yg1 + 3)[1]), "0+%.2f" % s1, 1.6, "TEXTOS", TA.BOTTOM_CENTER)
    # borde (NCT): azul abierto, verde tapado (cara superior e inferior de la losa)
    grupos, cur, est = [], [P[0]], None              # tramos consecutivos con el mismo estado (abierto / tapado)
    for a, b in zip(P[:-1], P[1:]):
        e = _tapado(r, (a[0] + b[0]) / 2)
        if est is None or e == est: cur.append(b)
        else:
            grupos.append((est, cur)); cur = [a, b]
        est = e
    grupos.append((est, cur))
    for tap, g in grupos:
        if len(g) < 2: continue
        lam.poli([(X(p[0]), Yz(p[1])) for p in g], "PERF-TAPA" if tap else "PERF-NCT")
        if tap: lam.poli([(X(p[0]), Yz(p[1] - 0.10)) for p in g], "PERF-TAPA")
    # fondo (NCF) en magenta: cara superior e inferior de la losa de fondo
    lam.poli([(X(p[0]), Yz(p[2])) for p in P], "PERF-FONDO")
    lam.poli([(X(p[0]), Yz(p[2] - EL)) for p in P], "PERF-FONDO")
    # secciones: linea roja, recuadro y guitarra
    xs_mm = [(x["s"] - s0) / f for x in secs]
    pos, filas = _filas_cajas(secs, xs_mm, -6, (s1 - s0) / f + 6, CAJA_W)
    ytop = Yz(max(p[1] for p in P))
    for x, (fila, xc) in zip(secs, pos):
        xs = X(x["s"])
        lam.linea((xs, Yz(x["nct"])), (xs, Yz(x["ncf"] - EL)), "PERF-SECCION")
        lam.linea((xs, lam.P(0, yg)[1]), (xs, lam.P(0, yg1)[1]), "GUITARRA")
        # recuadro
        lineas = ["NCT: %.2f" % x["nct"], "NCF: %.2f" % x["ncf"], " H: %.2f m" % x["h"], " EL: %.2f m" % EL, " EM: %.2f m" % EM]
        if x["nota"]: lineas += x["nota"].split("; ")              # cada aviso en su linea (no se sale del recuadro)
        alto = 2.4 + 3.7 * len(lineas)
        cx = lam.P(xd0 + xc, 0)[0]; yc0 = ytop + (12 + fila * CAJA_PASO) * f    # borde inferior del recuadro
        w = CAJA_W * f
        lam.rect(cx - w / 2, yc0, cx + w / 2, yc0 + alto * f, "PERF-CAJA")
        for i, t in enumerate(lineas):
            lam.texto((cx - w / 2 + 1.3 * f, yc0 + (alto - 2.8 - 3.7 * i) * f), t, 1.45 if i < 5 else 1.15, "TEXTOS", TA.MIDDLE_LEFT)
        lam.texto((cx, yc0 + (alto + 2.4) * f), "SECCION %02d" % x["n"], 1.8, "TITULOS", TA.BOTTOM_CENTER)
        lam.linea((cx - 11 * f, yc0 + (alto + 1.8) * f), (cx + 11 * f, yc0 + (alto + 1.8) * f), "TITULOS")
        lam.flecha((cx, yc0), (xs, Yz(x["nct"])), "PERF-CAJA", tam_mm=2.0)
        # guitarra: progresiva y etiqueta (verticales, para que no se encimen)
        lam.texto((xs + 0.6 * f, lam.P(0, yg1 - ALTO_FILA / 2)[1]), "%.2f" % x["s"], 1.0, "TEXTOS", TA.MIDDLE_CENTER, rot=90)
        lam.texto((xs + 0.6 * f, lam.P(0, yg1 - 1.5 * ALTO_FILA)[1]), "S-%02d" % x["n"], 1.0, "TEXTOS", TA.MIDDLE_CENTER, rot=90)
    # longitud y pendiente entre secciones: siempre la medida completa de seccion a seccion, aunque el tramo
    # siga en la pieza anterior o en la siguiente (en ese caso se indica entre que secciones es)
    todas = sorted(SEC[r["codigo"]], key=lambda x: x["s"])
    for A, Bs in zip(todas[:-1], todas[1:]):
        a, b = A["s"], Bs["s"]
        va, vb = max(a, s0), min(b, s1)
        if vb - va < 1e-6 or (vb - va) / f < 7: continue
        za, zb = _valor(r["perfil"], a)[1], _valor(r["perfil"], b)[1]
        xm = (X(va) + X(vb)) / 2
        cortado = a < s0 - 1e-6 or b > s1 + 1e-6
        lon = "%.2f" % (b - a)
        if cortado and (vb - va) / f > 40: lon += "  (S-%02d a S-%02d)" % (A["n"], Bs["n"])
        lam.texto((xm, lam.P(0, yg1 - 2.5 * ALTO_FILA)[1]), lon, 1.2, "TEXTOS", TA.MIDDLE_CENTER)
        lam.texto((xm, lam.P(0, yg1 - 3.5 * ALTO_FILA)[1]), "%.2f" % (100 * (za - zb) / (b - a)), 1.2, "TEXTOS", TA.MIDDLE_CENTER)
    # titulo del eje
    yt = lam.P(0, (ytop - lam.oy) / f + 12 + filas * CAJA_PASO + 4)[1]
    tit = "PERFIL LONGITUDINAL %s - %s - PROG. %s A %s" % (r["codigo"], r["descripcion"].upper(), prog(s0), prog(s1))
    lam.texto((lam.P(xg0, 0)[0], yt), tit, 2.0, "TITULOS", TA.LEFT)
    return CAB + (s1 - s0) / f


def leyenda_perfil(lam, xmm, ymm):
    lam.leyenda2(xmm, ymm, [("linea", "PERF-NCT", "Borde superior de cuneta (NCT) - tramo abierto con rejilla"),
                            ("linea", "PERF-TAPA", "Tramo tapado: cara superior e inferior de la losa"),
                            ("linea", "PERF-FONDO", "Cota de fondo (NCF) y cara inferior de la losa de fondo"),
                            ("linea", "PERF-SECCION", "Seccion (corte transversal en las laminas de secciones)"),
                            ("linea", "PERF-REF", "Altura relativa al NPT cada 0.15 m (0.00 = NPT +%.2f)" % NPT)],
                 hmm=1.6, ancho_col=150, filas_col=3)


def perfiles(doc, R, SEC, ox0, oy0, sep, num0):
    """Laminas A1 de perfiles: franjas de arriba hacia abajo; varias piezas cortas por franja."""
    franjas = _franjas(R); f = ESC_P / 1000.0
    lams, i, num = [], 0, num0
    while i < len(franjas):
        lam = B.Lamina(doc, ox0 + (num - num0) * sep, oy0, ESC_P, "DC-%02d" % num, "PERFILES LONGITUDINALES DE CUNETAS POR EJE",
                       "NCT, NCF, PROFUNDIDAD, LONGITUD Y PENDIENTE POR SECCION - ESC. H = V = 1/%d" % ESC_P)
        ytop = 580.0
        while i < len(franjas):
            a = max(alto_pieza(R, SEC, p)[0] for p in franjas[i])
            ancho_fr = sum(CAB + (p[2] - p[1]) / f + 14 for p in franjas[i])
            if ytop - a < 112.0 and ytop < 579: break       # abajo: leyenda (izquierda) y rotulo (derecha)
            x = 30.0
            for p in franjas[i]:
                x += perfil(lam, R, SEC, p, x, ytop - a) + 14
            ytop -= a + 4; i += 1
        leyenda_perfil(lam, 30, 100)
        lams.append(lam); num += 1
    return lams


# ----------------------------------------------------------------------------- cortes transversales (1/20)
def corte(lam, x, x0, y0):
    """Corte de la seccion x con su esquina exterior inferior izquierda en (x0, y0) (m de modelo)."""
    W, e, b = 2 * EM + DS.B_INT, EM, DS.B_INT
    H = x["h"]; tap = x["tap"]; ytop = y0 + EL + H
    capa = "SEC-TAPADA" if tap else "SEC-ABIERTA"
    if tap:
        ext = [(x0, y0), (x0 + W, y0), (x0 + W, ytop), (x0, ytop)]
        hueco = [(x0 + e, y0 + EL), (x0 + e + b, y0 + EL), (x0 + e + b, ytop - 0.10), (x0 + e, ytop - 0.10)]
        lam.relleno(ext, "CONCRETO-ACHURADO"); lam.relleno(hueco, "SEC-HUECO")
        lam.poli(ext, capa, cerrada=True); lam.poli(hueco, capa, cerrada=True)
    else:
        u = [(x0, y0), (x0 + W, y0), (x0 + W, ytop), (x0 + e + b, ytop), (x0 + e + b, y0 + EL), (x0 + e, y0 + EL), (x0 + e, ytop), (x0, ytop)]
        lam.relleno(u, "CONCRETO-ACHURADO"); lam.poli(u, capa, cerrada=True)
        a, t = 0.0254, 0.0048                            # rejilla movil de platinas 1" x 3/16" sobre angulos
        for xa, sg in ((x0 + e, 1), (x0 + e + b, -1)):
            lam.poli([(xa, ytop - a), (xa, ytop), (xa + sg * a, ytop)], "SEC-REJILLA")
        lam.rect(x0 + e - 0.012, ytop, x0 + e + b + 0.012, ytop + t, "SEC-REJILLA")
    # piso adyacente con junta asfaltica de 1", al mismo nivel que el borde de la cuneta
    yp = ytop; j = 0.0254
    piso = [(x0 - j, yp), (x0 - j - 0.34, yp), (x0 - j - 0.34, yp - 0.10), (x0 - j - 0.14, yp - 0.10), (x0 - j - 0.08, yp - 0.24), (x0 - j, yp - 0.24)]
    lam.relleno(piso, "CONCRETO-ACHURADO"); lam.poli(piso, "SEC-PISO", cerrada=True)
    jun = [(x0 - j, yp), (x0, yp), (x0, yp - 0.24), (x0 - j, yp - 0.24)]
    lam.relleno(jun, "SEC-JUNTA"); lam.poli(jun, "SEC-PISO", cerrada=True)
    # acero solo con h >= 0.40 m (de la rejilla al fondo) o en tramo tapado; si no, concreto simple
    r = 0.045
    con_acero = tap or H >= DS.H_ACERO - 1e-6
    sep = 0.22 if tap else 0.20
    barras = []
    if con_acero and tap:
        lam.poli([(x0 + r, y0 + r), (x0 + W - r, y0 + r), (x0 + W - r, ytop - r), (x0 + r, ytop - r)], "SEC-ACERO", cerrada=True)
    elif con_acero:
        lam.poli([(x0 + r + 0.03, ytop - 0.03), (x0 + r, ytop - 0.03), (x0 + r, y0 + r), (x0 + W - r, y0 + r), (x0 + W - r, ytop - 0.03),
                  (x0 + W - r - 0.03, ytop - 0.03)], "SEC-ACERO")
    if con_acero:
        barras = [(x0 + r, y0 + r), (x0 + W / 2, y0 + r), (x0 + W - r, y0 + r)]
        ny = max(1, round((ytop - 0.03 - (y0 + r)) / sep))
        for i in range(1, ny + 1):
            yy = y0 + r + i * (ytop - (0.05 if tap else 0.03) - (y0 + r)) / ny
            barras += [(x0 + r, yy), (x0 + W - r, yy)]
        if tap: barras.append((x0 + W / 2, ytop - r))
    for p in barras:
        hh = lam.msp.add_hatch(dxfattribs={"layer": "SEC-ACERO-LONG", "color": 5}); hh.set_solid_fill(color=5)
        hh.paths.add_edge_path().add_arc(p, 0.0085, 0, 360)
    # cotas
    lam.cota((x0, y0), (x0 + e, y0), -7, True); lam.cota((x0 + e, y0), (x0 + e + b, y0), -7, True)
    lam.cota((x0 + e + b, y0), (x0 + W, y0), -7, True); lam.cota((x0, y0), (x0 + W, y0), -14, True)
    lam.cota((x0 + W, y0), (x0 + W, y0 + EL), 6, False)
    lam.cota((x0 + W, y0 + EL), (x0 + W, ytop - (0.10 if tap else 0.0)), 13, False)
    if tap: lam.cota((x0 + W, ytop - 0.10), (x0 + W, ytop), 6, False)
    # llamadas
    if con_acero:
        lam.llamada((x0 + r, y0 + r + (ytop - y0) * 0.45), (x0 - 0.62, y0 + (ytop - y0) * 0.30), ['%%%%c3/8"@%.2f' % sep, "Longitudinal"], hmm=1.4)
        lam.llamada((x0 + W - r, ytop - 0.12), (x0 + W + 0.42, ytop - 0.02), ['%%c3/8"@0.25', "Transversal"], hmm=1.4)
    else:
        lam.llamada((x0 + e / 2, y0 + (ytop - y0) * 0.5), (x0 - 0.62, y0 + (ytop - y0) * 0.30), ["CONCRETO SIMPLE", "SIN ACERO (h < %.2f)" % DS.H_ACERO], hmm=1.4)
    lam.llamada((x0 - j / 2, yp - 0.05), (x0 - 0.62, yp + 0.20), ["JUNTA", 'ASFALTICA E=1"'], hmm=1.4)
    if not tap:
        lam.llamada((x0 + e + b, ytop + 0.004), (x0 + W + 0.04, ytop + 0.24), ["REJILLA METALICA MOVIL", 'PLATINAS DE 1" X 3/16"'], hmm=1.4)
    lam.texto((x0 + W / 2, ytop + 0.50), "SECCION %02d" % x["n"], 3.0, "TITULOS", TA.BOTTOM_CENTER)
    lam.linea((x0 + W / 2 - 0.32, ytop + 0.48), (x0 + W / 2 + 0.32, ytop + 0.48), "TITULOS")
    lam.texto((x0 + W / 2, ytop + 0.40), "%s - PROG. %s - %s" % (x["eje"], prog(x["s"]), "TAPADA" if tap else "CON REJILLA"),
              1.5, "TEXTOS", TA.MIDDLE_CENTER)
    lam.texto((x0 + W / 2, ytop + 0.33), "NCT %.2f - NCF %.2f - H %.2f m - ESC. 1/%d" % (x["nct"], x["ncf"], H, ESC_S), 1.4, "TEXTOS", TA.MIDDLE_CENTER)


def cortes(doc, SEC, ox0, oy0, sep, num0):
    """Laminas A1 con el corte de cada seccion, en orden, en una grilla de celdas."""
    todas = [x for lst in SEC.values() for x in lst]
    B.COLOR_RGB["SEC-HUECO"] = (255, 255, 255)
    if "SEC-HUECO" not in doc.layers: doc.layers.add("SEC-HUECO", color=7)
    f = ESC_S / 1000.0
    cw = 116.0                                            # ancho de celda (mm)
    ncol = int((ANCHO_LAM - 6) // cw)
    lams, i, num = [], 0, num0
    while i < len(todas):
        lam = B.Lamina(doc, ox0 + (num - num0) * sep, oy0, ESC_S, "DC-%02d" % num, "SECCIONES TRANSVERSALES DE CUNETAS",
                       "CORTE DE CADA SECCION DE LOS PERFILES: DIMENSIONES, ACERO, REJILLA, LOSA Y JUNTA - ESC. 1/%d" % ESC_S)
        ytop = 578.0
        while i < len(todas):
            fila = todas[i:i + ncol]
            hmax = max(EL + x["h"] for x in fila)
            alto = (hmax + 0.62) / f + 22
            if ytop - alto < 112.0: break                   # abajo: notas (izquierda) y rotulo (derecha)
            for c, x in enumerate(fila):
                x0, y0 = lam.P(30 + c * cw + 40, ytop - alto + 20)
                corte(lam, x, x0, y0)
            i += len(fila); ytop -= alto + 2
        lam.notas(30, 100, "NOTAS", [
            "1. Concreto f'c = 175 kg/cm2 en muros, losa de fondo y losa tapa; solado f'c = 100 kg/cm2 e = 0.05 m; recubrimiento 0.04 m.",
            "2. Acero fy = 4200 kg/cm2 solo con h >= 0.40 m y en tramos tapados: marco 3/8\" @ 0.25 m; longitudinales 3/8\" @ 0.20 m (rejilla) y @ 0.22 m (tapada). h < 0.40 m: concreto simple.",
            "3. Rejilla metalica movil de platinas 1\" x 3/16\" sobre angulos 1\" x 1\" x 3/16\" anclados a los muros (tramos abiertos).",
            "4. Junta asfaltica e = 1\" entre la cuneta y el piso, al mismo nivel. H = NCT - NCF; en la tapada incluye la losa de 0.10 m (libre >= 0.25 m).",
            "5. Niveles: NPT y borde de cuneta +184.65 (al ras); area verde +184.60; patio de maniobra +184.50 (cuneta al ras)."],
            hmm=1.6, ancho_mm=590)
        lams.append(lam); num += 1
    return lams
