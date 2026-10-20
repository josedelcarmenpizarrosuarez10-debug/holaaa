"""Cortes del planteamiento de cunetas - I.E. N.° 0590, Barranquita.

Cortes por las descargas: A-A, B-B y C-C por las descargas D1, D2 y D3 (1/100, H = V): cuneta en su eje (losa de fondo, rasante,
gradas) hasta el cerco perimetrico (limite de intervencion), pase en el cimiento del cerco o poza de salida, y el agua
que sigue sobre el terreno natural exterior (fuera del cerco no se dibuja ninguna obra).
Cortes generales: E-E (norte-sur) y F-F (oeste-este) a 1/250 (H = V): terreno natural, plataforma +184.50,
bloques con techo a dos aguas y cada cuneta cortada con su cota de fondo.
Lo usa planos_b.py.
"""
import os, sys, math
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import dxf_base as B
from ezdxf.enums import TextEntityAlignment as TA
from matplotlib.path import Path
import terreno_b as T
import diseno_b as DS

COL_SIS = {1: 5, 2: 6, 3: 94}
NPT, H_ALERO, H_CUMB = 184.65, 3.00, 1.10          # bloques (solo en los cortes): alero 3.00 m sobre el NPT, cumbrera 1.10 m mas


def bloques(G):
    """Contornos de techo (0_PROYECCIONES 1) cerrados y de mas de 30 m2, uno por bloque (el mayor de cada par)."""
    out = []
    for pts, cl, b in G["geo"]["0_PROYECCIONES 1"]:
        q = [(p[0], p[1]) for p in pts]
        if len(q) > 2 and math.dist(q[0], q[-1]) < 0.05: q = q[:-1]; cl = True
        if not cl or len(q) < 4: continue
        A = abs(sum(q[i][0] * q[i + 1][1] - q[i + 1][0] * q[i][1] for i in range(-1, len(q) - 1))) / 2
        if A < 30: continue
        c = (sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q))
        dup = [o for o in out if math.dist(o[1], c) < 1.5]
        if dup:
            if A > dup[0][2]: out.remove(dup[0])
            else: continue
        out.append((q, c, A, b))
    return out


def capas(doc):
    for n, c, rgb in (("CORTE-SUELO", 7, (232, 222, 200)), ("CORTE-BLOQUE", 8, (240, 237, 230)), ("CORTE-TECHO", 1, (200, 110, 90)),
                      ("RELLENO", 32, (214, 190, 150))):
        ly = doc.layers.get(n) if n in doc.layers else doc.layers.add(n, color=c)
        ly.rgb = rgb; B.COLOR_RGB[n] = rgb


class Camino:
    """Polilinea en planta con progresiva."""
    def __init__(self, pts):
        self.p = [tuple(p) for p in pts]; self.s = [0.0]
        for i in range(1, len(self.p)): self.s.append(self.s[-1] + math.dist(self.p[i - 1], self.p[i]))
        self.L = self.s[-1]

    def punto(self, s):
        for i in range(len(self.p) - 1):
            if s <= self.s[i + 1] + 1e-9 or i == len(self.p) - 2:
                L = self.s[i + 1] - self.s[i]; t = 0 if L == 0 else (s - self.s[i]) / L
                a, b = self.p[i], self.p[i + 1]
                return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), ((b[0] - a[0]) / L, (b[1] - a[1]) / L)

    def cruces(self, a, b):
        """Progresivas donde el segmento a-b cruza el camino."""
        out = []
        for i in range(len(self.p) - 1):
            p, q = self.p[i], self.p[i + 1]
            d1 = (q[0] - p[0], q[1] - p[1]); d2 = (b[0] - a[0], b[1] - a[1]); den = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(den) < 1e-9: continue
            t = ((a[0] - p[0]) * d2[1] - (a[1] - p[1]) * d2[0]) / den; u = ((a[0] - p[0]) * d1[1] - (a[1] - p[1]) * d1[0]) / den
            if 0 <= t <= 1 and 0 <= u <= 1: out.append((self.s[i] + t * math.dist(p, q), u))
        return out


def perfil_cf(r, s):
    P = r["perfil"]; k = min(range(len(P)), key=lambda i: abs(P[i][0] - s)); return P[k][1], P[k][2]


def nombre_bloque(n):
    import re
    n = n.upper().replace("EDIFICACIÓN", "BLOQUE").replace("EDIFICACION", "BLOQUE").replace("_FINAL", "")
    n = re.sub(r"0(\d)\1{2,}", r"0\1", n); n = re.sub(r"\s+", " ", n).strip()
    return n[:24] or "BLOQUE"


def corte(lam, R, V, cam, xmm, ymm, titulo, zmin=None, zmax=None, ejes=(), desc=None, paso_z=0.5, txt_h=1.8, marcas=()):
    """Dibuja un corte por el camino cam con origen (xmm, ymm) = esquina inferior izquierda del dibujo (zref)."""
    f = lam.f; zt = T.modelo(); ras = DS.rasante_fn(); ce = Path(DS.CERCO)
    S = np.arange(0, cam.L + 0.01, 0.25)
    nat = []; fin = []
    for s in S:
        (x, y), u = cam.punto(s); nat.append(zt(x, y)); fin.append(ras(x, y))
    nat = np.array(nat); fin = np.array(fin)
    zlo = zmin if zmin is not None else math.floor((np.nanmin(fin) - 1.0) * 2) / 2
    zhi = zmax if zmax is not None else math.ceil((np.nanmax(fin) + 2.0))
    X = lambda s: lam.P(xmm + s / f, 0)[0]
    Yz = lambda z: lam.P(0, ymm + (z - zlo) / f)[1]
    # suelo terminado relleno
    ok = np.isfinite(fin)
    pts = [(X(s), Yz(z)) for s, z, k in zip(S, fin, ok) if k]
    if len(pts) > 1:
        lam.relleno(pts + [(pts[-1][0], Yz(zlo)), (pts[0][0], Yz(zlo))], "CORTE-SUELO")
        lam.poli(pts, "TERRENO")
    pn = [(X(s), Yz(z)) for s, z in zip(S, nat) if np.isfinite(z)]
    if len(pn) > 1: lam.poli(pn, "TERRENO-EXISTENTE")
    # bloques cortados (techo a dos aguas: cumbrera en el eje largo)
    G = T.cargar(); items = []; z_techo = float(np.nanmax(fin))
    for q, c, A, nombre in bloques(G):
        pth = Path(q); dentro = [pth.contains_point(cam.punto(s)[0]) for s in S]
        i = 0
        while i < len(S):
            if dentro[i]:
                j = i
                while j + 1 < len(S) and dentro[j + 1]: j += 1
                if S[j] - S[i] > 0.6:
                    z0, z1 = DS.NTN_PLAT, NPT + H_ALERO
                    if len(q) == 4:
                        l01, l12 = math.dist(q[0], q[1]), math.dist(q[1], q[2])
                        a0, a1, b0, b1 = (q[0], q[1], q[3], q[2]) if l01 >= l12 else (q[1], q[2], q[0], q[3])
                        m0 = ((a0[0] + b0[0]) / 2, (a0[1] + b0[1]) / 2); m1 = ((a1[0] + b1[0]) / 2, (a1[1] + b1[1]) / 2)
                        w = math.dist(a0, b0)
                        def zr(p):
                            dx, dy = m1[0] - m0[0], m1[1] - m0[1]; Lr = math.hypot(dx, dy)
                            d = abs((p[0] - m0[0]) * dy - (p[1] - m0[1]) * dx) / Lr
                            return z1 + H_CUMB * max(0.0, 1 - 2 * d / w)
                    else:
                        zr = lambda p: z1
                    techo = [(X(S[k]), Yz(zr(cam.punto(S[k])[0]))) for k in range(i, j + 1)]
                    cuerpo = [(X(S[i]), Yz(z0))] + [(X(S[i]), Yz(z1))] + [(X(S[j]), Yz(z1)), (X(S[j]), Yz(z0))]
                    lam.relleno(cuerpo, "CORTE-BLOQUE"); lam.poli(cuerpo, "ARQ-BASE", cerrada=True)
                    z_techo = max(z_techo, z1 + H_CUMB)
                    tt = techo + [(X(S[j]), Yz(z1)), (X(S[i]), Yz(z1))]
                    lam.relleno(tt, "CORTE-TECHO"); lam.poli(techo, "ARQ-BASE")
                    lam.linea((X(S[i]), Yz(NPT)), (X(S[j]), Yz(NPT)), "ARQ-BASE")
                    nom = nombre_bloque(nombre)
                    lam.texto(((X(S[i]) + X(S[j])) / 2, Yz(z0 + 1.4)), nom, txt_h * 0.8, "TEXTOS", TA.MIDDLE_CENTER)
                    lam.texto(((X(S[i]) + X(S[j])) / 2, Yz(z0 + 0.55)), "NPT +%.2f" % NPT, txt_h * 0.75, "TEXTOS", TA.MIDDLE_CENTER)
                i = j + 1
            else: i += 1
    # cerco perimetrico confirmado (limite de intervencion)
    vistos = []; ce_ = DS.CERCO
    for k in range(len(ce_)):
        for s, u in cam.cruces(ce_[k], ce_[(k + 1) % len(ce_)]):
            if any(abs(s - v) < 1.0 for v in vistos): continue
            vistos.append(s); z = ras(*cam.punto(s)[0])
            if np.isfinite(z):
                pase = desc is not None and abs(s - desc["s"]) < 0.5
                if pase:                                   # pase en el cimiento: la cuneta cruza bajo el muro
                    cf_ = desc_cf(V, desc)
                    lam.rect(X(s) - 0.075, Yz(z), X(s) + 0.075, Yz(z + 2.4), "CERCO")
                    lam.rect(X(s) - 0.075, Yz(min(z - 0.6, cf_ - 0.30)), X(s) + 0.075, Yz(cf_ - 0.10), "CERCO")
                else:
                    lam.rect(X(s) - 0.075, Yz(z - 0.6), X(s) + 0.075, Yz(z + 2.4), "CERCO")
                items.append((X(s), Yz(z + 2.4), ["CERCO PERIMETRICO", "(LIMITE DE INTERVENCION)"], 1))
    # cuneta a lo largo del eje (cortes por las descargas)
    for ramal_eje, sa, sb, s_cam in ejes:
        r = next(x for x in R["ramales"] if x["codigo"] == ramal_eje)
        grad = {(f_["ramal"], f_["de"], f_["a"]) for f_ in V["hidraulica"] if f_["vel"] != "CUMPLE"}
        seg = [p for p in r["perfil"] if sa - 1e-6 <= p[0] <= sb + 1e-6]
        off = s_cam - sa
        fondo = [(X(p[0] + off), Yz(p[2])) for p in seg]; losa = [(X(p[0] + off), Yz(p[2] - 0.10)) for p in seg]
        rasl = [(X(p[0] + off), Yz(p[1])) for p in seg]
        # gradas: fondo en escalones de 0.15 m en los tramos de fuerte pendiente
        acc = 0.0; nomb = R["nombre"]; esc = []
        for t in r["tramos"]:
            if (r["codigo"], nomb[t["de"]], nomb[t["a"]]) in grad: esc.append((acc, acc + t["L"]))
            acc += t["L"]
        # relleno compactado donde la cuneta va por encima del terreno (conexiones nuevas)
        rel = []
        for p in seg:
            (xx, yy), u_ = cam.punto(p[0] + off); zg = ras(xx, yy)
            rel.append((p[0] + off, p[2] - 0.10, zg))
        i = 0
        while i < len(rel):
            if np.isfinite(rel[i][2]) and rel[i][1] > rel[i][2] + 0.05:
                j = i
                while j + 1 < len(rel) and np.isfinite(rel[j + 1][2]) and rel[j + 1][1] > rel[j + 1][2] + 0.05: j += 1
                if j > i:
                    top = [(X(rel[k][0]), Yz(rel[k][1])) for k in range(i, j + 1)]; bot = [(X(rel[k][0]), Yz(rel[k][2])) for k in range(j, i - 1, -1)]
                    lam.relleno(top + bot, "RELLENO"); lam.poli(top + bot, "RELLENO", cerrada=True)
                    m = (i + j) // 2; items.append((X(rel[m][0]), Yz(rel[m][1]), ["RELLENO COMPACTADO"], 32))
                i = j + 1
            else: i += 1
        lam.relleno(fondo + losa[::-1], "CONCRETO-ACHURADO"); lam.poli(losa, "CONCRETO")
        if esc:
            esc_pts = []
            for p in seg:
                if any(a <= p[0] <= b for a, b in esc):
                    z = math.floor(p[2] / 0.15) * 0.15 + 0.15 * (1 if (p[2] % 0.15) > 0.075 else 0)
                    if esc_pts and abs(esc_pts[-1][1] - Yz(z)) > 1e-9: esc_pts.append((X(p[0] + off), esc_pts[-1][1]))
                    esc_pts.append((X(p[0] + off), Yz(z)))
                else:
                    if len(esc_pts) > 1: lam.poli(esc_pts, "CUNETA-GRADAS"); esc_pts = []
            if len(esc_pts) > 1: lam.poli(esc_pts, "CUNETA-GRADAS")
        lam.poli(fondo, "CONCRETO"); lam.poli(rasl, "CONCRETO")
        for s0_, s1_ in r["tapados"]:
            a, b = max(s0_, sa), min(s1_, sb)
            if b - a > 0.3:
                pp = [(X(p[0] + off), Yz(p[1])) for p in seg if a <= p[0] <= b]; ll = [(x, y - 0.10) for x, y in pp]
                lam.relleno(pp + ll[::-1], "CONCRETO-ACHURADO"); lam.poli(pp + ll[::-1], "CONCRETO", cerrada=True)
        # agua (tirante normal del ultimo tramo)
        hid = [f_ for f_ in V["hidraulica"] if f_["ramal"] == r["codigo"]]
        yagua = hid[-1]["y"] if hid else 0.1
        nomb = R["nombre"]
        lam.poli([(x, y + yagua) for x, y in fondo[-max(2, len(fondo) // 3):]], "AGUA")
        acc = 0.0
        nodos = [(0.0, r["tramos"][0]["de"])] + [(sum(t["L"] for t in r["tramos"][:i + 1]), t["a"]) for i, t in enumerate(r["tramos"])]
        for sN, n in nodos:
            if sa - 1e-6 <= sN <= sb + 1e-6 and not (desc and n == desc["D"]):
                rz, cf = perfil_cf(r, sN)
                items.append((X(sN + off), Yz(rz), ["%s  C.F. %.3f" % (nomb[n], cf), "rasante %.2f  h %.2f" % (rz, rz - cf)], 7))
        if esc:
            for a, b in esc:
                m = (max(a, sa) + min(b, sb)) / 2
                if sa <= m <= sb:
                    rz, cf = perfil_cf(r, m); items.append((X(m + off), Yz(rz), ["GRADAS (S fuerte)"], 1))
    # cunetas cortadas transversalmente
    for r in R["ramales"]:
        if r["codigo"] in [e[0] for e in ejes]: continue
        acc = 0.0
        for t in r["tramos"]:
            a, b = R["nudos"][t["de"]], R["nudos"][t["a"]]
            for s, u in cam.cruces(a, b):
                rz, cf = perfil_cf(r, acc + u * t["L"])
                e, bi = DS.E_MURO, DS.B_INT; W = 2 * e + bi; x0 = X(s) - W / 2
                cont = [(x0, Yz(cf - 0.10)), (x0 + W, Yz(cf - 0.10)), (x0 + W, Yz(rz)), (x0 + e + bi, Yz(rz)), (x0 + e + bi, Yz(cf)),
                        (x0 + e, Yz(cf)), (x0 + e, Yz(rz)), (x0, Yz(rz))]
                lam.relleno(cont, "CONCRETO-ACHURADO"); lam.poli(cont, "CONCRETO", cerrada=True)
                items.append((X(s), Yz(rz), ["%s  C.F. %.3f" % (r["codigo"], cf), "h %.2f" % (rz - cf)], COL_SIS[r["sistema"]]))
            acc += t["L"]
    # descarga: pase en el cimiento del cerco o poza de salida; fuera del cerco solo el agua sobre el terreno natural
    if desc:
        d = next(x for x in V["descargas"] if x["D"] == desc["D"]); sD = desc["s"]; cf = d["cf"]
        if d["tipo"] == "poza":
            Lp = DS.POZA_DIM[1]; zr = d["nivel_rebalse"]
            caja = [(X(sD - Lp - 0.10), Yz(cf - 0.10)), (X(sD + 0.10), Yz(cf - 0.10)), (X(sD + 0.10), Yz(zr)), (X(sD), Yz(zr)), (X(sD), Yz(cf)),
                    (X(sD - Lp), Yz(cf)), (X(sD - Lp), Yz(zr - 0.02)), (X(sD - Lp - 0.10), Yz(zr - 0.02))]
            lam.relleno(caja, "CONCRETO-ACHURADO"); lam.poli(caja, "CONCRETO", cerrada=True)
            lam.poli([(X(sD - Lp), Yz(zr - 0.03)), (X(sD), Yz(zr - 0.03))], "AGUA")
            items.append((X(sD - Lp / 2), Yz(zr), ["POZA DE SALIDA %.2f x %.2f" % DS.POZA_DIM, "rebalsa a %.2f" % zr], 1))
            z0 = zr
        else:
            z0 = cf
        # agua sobre el terreno exterior (perfilado del terreno natural donde queda sobre la C.F., sin obra)
        ext = [(s, zt(*cam.punto(s)[0])) for s in S if s >= sD]
        ext = [(s, z) for s, z in ext if np.isfinite(z)]
        ag = [(X(s), Yz(min(z, z0) + 0.06)) for s, z in ext[:60]]
        perf = [(X(s), Yz(z0)) for s, z in ext if z > z0 + 0.02 and s <= sD + (d["sale_a_m"] or 0) + 0.3]
        if len(perf) > 1 and d["tipo"] != "poza":
            lam.poli([(X(sD), Yz(cf))] + perf, "DESCARGA")
            items.append((perf[len(perf) // 2][0], perf[len(perf) // 2][1], ["PERFILADO DEL TERRENO NATURAL", "%.1f m (sin obra)" % d["sale_a_m"]], 8))
        if len(ag) > 1:
            lam.poli(ag, "DESCARGA", ancho=0.06 if f < 0.2 else 0.15); lam.flecha(ag[-2], ag[-1], "DESCARGA", tam_mm=4)
        items.append((X(sD), Yz(cf), ["%s %s  C.F. %.3f" % (desc["D"], "POZA" if d["tipo"] == "poza" else "PASE EN EL CERCO", cf), desc["txt"]], 1))
    # ejes: cotas cada paso_z y progresivas
    z = math.ceil(zlo / paso_z) * paso_z
    while z <= zhi + 1e-6:
        lam.linea((X(0) - 2 * f, Yz(z)), (X(0), Yz(z)), "GRILLA"); lam.texto((X(0) - 2.5 * f, Yz(z)), "%.2f" % z, 1.4, "TEXTOS", TA.MIDDLE_RIGHT); z += paso_z
    lam.linea((X(0), Yz(zlo)), (X(0), Yz(zhi)), "GRILLA"); lam.linea((X(0), Yz(zlo)), (X(cam.L), Yz(zlo)), "GRILLA")
    pp = 0.0; dp = 5.0 if f <= 0.1 else 10.0
    while pp <= cam.L + 1e-6:
        lam.linea((X(pp), Yz(zlo)), (X(pp), Yz(zlo) - 1.5 * f), "GRILLA"); lam.texto((X(pp), Yz(zlo) - 2.2 * f), "%.0f" % pp, 1.3, "TEXTOS", TA.TOP_CENTER); pp += dp

    for sm, t in marcas:                                   # referencias (calle, quebrada, talud)
        (xx, yy), u_ = cam.punto(sm); zg = ras(xx, yy)
        if np.isfinite(zg): items.append((X(sm), Yz(zg), [t], 8))
    y_lab = Yz(z_techo) + 3 * f
    if items: y_lab = rotulos(lam, items, Yz(z_techo) + 3 * f, None, txt_h)
    lam.texto((lam.P(xmm, 0)[0], y_lab + 5 * f), titulo, 3.0, "TITULOS", TA.LEFT)
    return Yz(zlo)


def rotulos(lam, items, y_min, y_max, hmm):
    """Rotulos sobre el corte, sin pisarse: cada uno sube hasta el primer hueco libre por encima de y_min
    (los de un mismo punto se juntan en un solo rotulo)."""
    f = lam.f; h = hmm * B.K_TXT["TEXTOS"] * f; lh = 1.5 * h; ch = 0.66 * h
    junt = []
    for x, y, ls, col in sorted(items, key=lambda e: e[0]):
        if junt and abs(junt[-1][0] - x) < 2.5 * f:
            junt[-1] = (junt[-1][0], max(junt[-1][1], y), junt[-1][2] + [t for t in ls if t not in junt[-1][2]], junt[-1][3])
        else: junt.append((x, y, list(ls), col))
    cajas = []
    for x, y, ls, col in junt:
        w = max(len(t) for t in ls) * ch + 1.5 * f; alto = len(ls) * lh + 1.0 * f
        yb = y_min
        while any(x < c[2] + 1.0 * f and x + w > c[0] - 1.0 * f and yb < c[3] and yb + alto > c[1] for c in cajas):
            yb = min(c[3] for c in cajas if x < c[2] + 1.0 * f and x + w > c[0] - 1.0 * f and yb < c[3] and yb + alto > c[1]) + 0.6 * f
        cajas.append((x, yb, x + w, yb + alto))
        lam.linea((x, y), (x, yb), "LLAMADAS"); lam.circulo((x, y), 0.5 * f, "LLAMADAS")
        for i, t in enumerate(ls):
            lam.texto((x + 0.8 * f, yb + 0.5 * f + (len(ls) - 1 - i) * lh), t, hmm, "TEXTOS", TA.BOTTOM_LEFT, color=col)
    return max([c[3] for c in cajas] + [y_min])


def desc_cf(V, desc):
    return next(x for x in V["descargas"] if x["D"] == desc["D"])["cf"]


def extender(p, u, d):
    return (p[0] + u[0] * d, p[1] + u[1] * d)


def cola(R, cod, largo, ext, u_ext=None):
    """Camino por los ultimos 'largo' m del ramal cod y 'ext' m fuera del cerco; devuelve (camino, s inicial en el ramal)."""
    N = R["nudos"]; r = next(x for x in R["ramales"] if x["codigo"] == cod); xy = [tuple(N[n]) for n in r["nudos"]]
    sa = max(0.0, r["L"] - largo); cam = []; acc = 0.0
    for i in range(len(xy) - 1):
        L = math.dist(xy[i], xy[i + 1])
        if acc + L > sa:
            t = max(0, (sa - acc) / L)
            if not cam: cam.append((xy[i][0] + t * (xy[i + 1][0] - xy[i][0]), xy[i][1] + t * (xy[i + 1][1] - xy[i][1])))
            cam.append(xy[i + 1])
        acc += L
    a, b = xy[-2], xy[-1]; u = u_ext or ((b[0] - a[0]) / math.dist(a, b), (b[1] - a[1]) / math.dist(a, b))
    cam.append(extender(b, u, ext))
    return cam, sa, r


def dc09(doc, R, V, ox, oy, codigo="DC-08"):
    lam = B.Lamina(doc, ox, oy, 100, codigo, "CORTES POR LAS DESCARGAS D1, D2 Y D3",
                   "CUNETA EN SU EJE HASTA EL CERCO, PASE O POZA EN EL CERCO Y AGUA SOBRE EL TERRENO NATURAL - ESC. H = V = 1/100")
    # A-A: R-01 (ultimos 35 m) + 8 m de terreno exterior
    cam, sa, r = cola(R, "R-01", 35.0, 8.0)
    corte(lam, R, V, Camino(cam), 40, 450, "CORTE A-A: PERIMETRAL R-01 Y DESCARGA D1 (CERCO SUR-OESTE, TALUD HACIA LA QUEBRADA DEL OESTE)",
          ejes=[("R-01", sa, r["L"], 0.0)], desc={"D": "D1", "s": r["L"] - sa, "txt": "el agua sigue por el talud natural a la quebrada"})
    # B-B: R-12 (ultimos 45 m, gradas) + 14 m por la hondonada exterior
    cam, sa, r = cola(R, "R-12", 45.0, 14.0, DS.DIR_SALIDA["D2"])
    corte(lam, R, V, Camino(cam), 40, 280, "CORTE B-B: PERIMETRAL ESTE R-12 (GRADAS) Y POZA DE SALIDA D2 (CERCO NORTE, HONDONADA NATURAL)",
          ejes=[("R-12", sa, r["L"], 0.0)], desc={"D": "D2", "s": r["L"] - sa, "txt": "rebalsa al fondo de la hondonada que baja a la quebrada del norte"})
    # C-C: R-07 (ultimos 35 m por el atrio) + 8 m de terreno exterior hacia el Jr. Alfonso Ugarte
    cam, sa, r = cola(R, "R-07", 35.0, 8.0)
    corte(lam, R, V, Camino(cam), 40, 115, "CORTE C-C: BAJADA R-07 POR EL ATRIO DE INGRESO Y DESCARGA D3 (CERCO SUR, JR. ALFONSO UGARTE)",
          ejes=[("R-07", sa, r["L"], 0.0)], desc={"D": "D3", "s": r["L"] - sa, "txt": "el agua sigue por el terreno exterior que baja a la calle (183.00)"})
    lam.notas(520, 440, "NOTAS", ["1. Cortes a escala real 1/100 sin exageracion vertical. Terreno natural en linea discontinua",
                                  "   (curvas C-TOPO); suelo terminado relleno (plataforma +184.50 dentro del cerco).",
                                  "2. Las cunetas terminan en el cerco perimetrico (limite de intervencion): fuera del cerco no se",
                                  "   construye; el agua sale por el pase en el cimiento (D1, D3) o rebalsa de la poza (D2).",
                                  "3. D1 y D3: donde el terreno exterior queda sobre la C.F. (1.0 m y 2.0 m) solo se perfila el terreno.",
                                  "4. Gradas (escalones de 0.15 m) donde la velocidad pasaria de 3.0 m/s."],
              hmm=1.6, ancho_mm=260)
    return lam


def dc10(doc, R, V, ox, oy, codigo="DC-09"):
    lam = B.Lamina(doc, ox, oy, 250, codigo, "CORTES GENERALES DEL TERRENO Y LA RED DE CUNETAS",
                   "CORTE E-E (SUR - NORTE) Y CORTE F-F (OESTE - ESTE) - ESC. H = V = 1/250")
    camE = Camino([(354925.0, 9249778.0), (354925.0, 9249890.0)])
    corte(lam, R, V, camE, 40, 400, "CORTE E-E (x = 354925): JR. ALFONSO UGARTE - FRENTE SUR - PATIO CENTRAL - BLOQUE NORTE - QUEBRADA",
          zmin=175.0, zmax=190.0, paso_z=1.0, txt_h=1.6, marcas=[(7.0, "JR. ALFONSO UGARTE (183.00)"), (100.0, "QUEBRADA (NORTE)"), (90.5, "TALUD")])
    camF = Camino([(354806.0, 9249846.0), (354988.0, 9249846.0)])
    corte(lam, R, V, camF, 40, 175, "CORTE F-F (y = 9249846): QUEBRADA OESTE - PABELLONES OESTE - PATIO CENTRAL - BLOQUE NOR-ESTE - CERCO ESTE",
          zmin=178.0, zmax=190.0, paso_z=1.0, txt_h=1.6, marcas=[(5.0, "QUEBRADA (OESTE)"), (168.0, "HONDONADA: CABECERA DE QUEBRADA")])
    lam.notas(30, 100, "NOTAS", ["1. Escala real 1/250 sin exageracion vertical. Terreno natural (curvas C-TOPO) en linea discontinua;",
                                 "   suelo terminado relleno: plataforma de los bloques +184.50 (NPT +184.65) y terreno natural fuera del cerco.",
                                 "2. Cada cuneta cortada se dibuja a escala con su cota de fondo (C.F.) y su profundidad h.",
                                 "3. Altura de bloques referencial: alero 3.00 m sobre el NPT, cumbrera 1.10 m mas arriba (techos a dos aguas).",
                                 "4. Cerco perimetrico = limite de intervencion: todas las cunetas quedan dentro del cerco."],
              hmm=1.6, ancho_mm=560)
    return lam
