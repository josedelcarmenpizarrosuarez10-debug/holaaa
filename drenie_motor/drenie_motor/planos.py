"""Juego de planos de cunetas (PLANOS_CUNETAS.dxf): planta general y cuadros (planta_lamina.py), perfiles y secciones.

Mismo estilo de las laminas aprobadas por el usuario (I.E. N.° 0590 Barranquita, perfiles_b.py), para cualquier proyecto:
- Un perfil por eje, escala H = V = 1/50: borde superior (NCT) azul en tramos con rejilla y verde en tramos tapados (cara
  superior e inferior de la losa); cota de fondo (NCF) magenta (cara superior e inferior de la losa de fondo); linea roja en cada
  seccion; lineas de referencia cada 0.15 m respecto al NPT; recuadro de cada seccion (NCT, NCF, H, b, EL, EM y con que eje se
  une); guitarra con progresiva, etiqueta, longitud y pendiente.
- Secciones: inicio y fin de cada eje, cada nudo donde cambia la pendiente, empalme o descarga, inicio y fin de tapado y cambio
  de borde. Cada seccion con su corte a 1/20 (ancho libre del tramo, muros, losa de fondo, solado, rejilla o losa tapa, acero
  si h >= h_acero o tapada, junta con el piso, cotas y llamadas).
Escala real: 1 unidad = 1 m. Solo dibuja con el resultado del diseno (no cambia cotas ni ejes).
"""
import math

from ezdxf.enums import TextEntityAlignment as TA

from . import dxf_base as B
from . import dxf_layouts as LY

ESC_P, ESC_S = 50, 20
ANCHO_LAM = 800.0
CAB = 34.0
FILAS = ["Progresiva (m)", "Etiqueta", "Longitud (m)", "Pendiente (%)"]
ALTO_FILA = 6.5
PASO_REF = 0.15
CAJA_W, CAJA_PASO = 25.0, 34.0
CAPAS = [("PERF-NCT", 5, "CONTINUOUS"), ("PERF-TAPA", 3, "CONTINUOUS"), ("PERF-FONDO", 6, "CONTINUOUS"), ("PERF-SECCION", 1, "CONTINUOUS"),
         ("PERF-REF", 9, "CONTINUOUS"), ("PERF-CAJA", 7, "CONTINUOUS"), ("SEC-ABIERTA", 5, "CONTINUOUS"), ("SEC-TAPADA", 3, "CONTINUOUS"),
         ("SEC-ACERO", 6, "CONTINUOUS"), ("SEC-ACERO-LONG", 5, "CONTINUOUS"), ("SEC-REJILLA", 1, "CONTINUOUS"), ("SEC-PISO", 8, "CONTINUOUS"),
         ("SEC-JUNTA", 8, "CONTINUOUS"), ("SEC-SOLADO", 8, "CONTINUOUS"), ("SEC-HUECO", 7, "CONTINUOUS")]
GROSOR = {"PERF-NCT": 35, "PERF-TAPA": 35, "PERF-FONDO": 35, "PERF-SECCION": 25, "PERF-REF": 9, "SEC-ABIERTA": 35, "SEC-TAPADA": 35,
          "SEC-ACERO": 50, "SEC-REJILLA": 35, "SEC-PISO": 25}


def rotulo_de(proyecto):
    """Rotulo de las laminas con los datos del proyecto (sin nombre ni CIP del proyectista)."""
    nom = proyecto.get("nombre", "")
    cod = proyecto.get("codigo", "")
    l1 = proyecto.get("rotulo", [None, None])
    if l1 and l1[0]: B.PROYECTO = (l1[0], l1[1] if len(l1) > 1 else "")
    else:
        corte = nom[:110].rfind(" ") if len(nom) > 110 else len(nom)
        B.PROYECTO = (nom[:corte].upper(), (nom[corte:].strip() + (" - " + cod if cod else "")).upper())
    B.UBICACION = "UBICACION: " + proyecto.get("ubicacion", "").upper()
    B.ENTIDAD = "ENTIDAD: " + proyecto.get("entidad", "").upper()
    B.ESPECIALIDAD = "ESPECIALIDAD: " + proyecto.get("especialidad", "DRENAJE PLUVIAL - CUNETAS").upper()
    B.FECHA = proyecto.get("fecha", ""); B.ELABORADO = ""


def capas(doc):
    for n, c, lt in CAPAS:
        if n not in doc.layers: doc.layers.add(n, color=c, linetype=lt)
        if n in GROSOR: doc.layers.get(n).dxf.lineweight = GROSOR[n]
    B.COLOR_RGB["SEC-JUNTA"] = (70, 70, 70); B.COLOR_RGB["SEC-HUECO"] = (255, 255, 255); B.COLOR_RGB["SEC-SOLADO"] = (200, 200, 200)


def prog(s): return "0+%06.2f" % s


def _valor(Pf, s):
    for i in range(1, len(Pf)):
        if Pf[i][0] >= s - 1e-9:
            a, b = Pf[i - 1], Pf[i]; t = 0 if b[0] == a[0] else (s - a[0]) / (b[0] - a[0])
            return a[1] + t * (b[1] - a[1]), a[2] + t * (b[2] - a[2])
    return Pf[-1][1], Pf[-1][2]


def _tapado(r, s): return any(a - 1e-6 <= s <= b + 1e-6 for a, b in r["tapados"])


def _ancho_en(r, s, anchos, P):
    acc = 0.0
    for t in r["tramos"]:
        if s <= acc + t["L"] + 1e-6: return anchos.get((r["codigo"], t["de"], t["a"]), P["b_int"])
        acc += t["L"]
    t = r["tramos"][-1]; return anchos.get((r["codigo"], t["de"], t["a"]), P["b_int"])


def secciones(R, descargas, anchos, P):
    """{eje: [dict(n, s, nct, ncf, h, b, tap, nota, eje)]} con numeracion correlativa en el orden de los ejes."""
    llegan, recibe = {}, {}
    for r in R["ramales"]: llegan.setdefault(r["nudos"][-1], []).append(r["codigo"])
    for r in R["ramales"]:
        for r2 in R["ramales"]:
            if r2 is not r and r["nudos"][-1] in r2["nudos"][1:]: recibe[r["codigo"]] = r2["codigo"]
    out, k = {}, 0
    for r in R["ramales"]:
        Pf = r["perfil"]; L = r["L"]; cand = []
        acc = 0.0; nodos = [(0.0, r["nudos"][0])]
        for t in r["tramos"]: acc += t["L"]; nodos.append((min(acc, L), t["a"]))
        nodos[-1] = (L, nodos[-1][1])
        for i, (s, n) in enumerate(nodos):
            nota = ""
            if n in llegan and n != r["nudos"][-1]: nota = "Llega " + ", ".join(c for c in llegan[n] if c != r["codigo"])
            if s == 0.0: nota = nota or "Inicio del eje"
            if not nota and 0.0 < s < L:
                sa = (_valor(Pf, nodos[i - 1][0])[1] - _valor(Pf, s)[1]) / max(s - nodos[i - 1][0], 1e-6)
                sb = (_valor(Pf, s)[1] - _valor(Pf, nodos[i + 1][0])[1]) / max(nodos[i + 1][0] - s, 1e-6)
                if abs(sa - sb) < 0.0005 or "~" in n: continue
            if n == r["nudos"][-1]:
                if n in descargas: nota = "Descarga " + n
                elif r["codigo"] in recibe:
                    r2 = next(x for x in R["ramales"] if x["codigo"] == recibe[r["codigo"]])
                    acc2 = s2 = 0.0
                    for t in r2["tramos"]:
                        acc2 += t["L"]
                        if t["a"] == n: s2 = acc2
                    caida = r["perfil"][-1][2] - _valor(r2["perfil"], min(s2, r2["L"]))[1]
                    nota = "Entrega a %s" % r2["codigo"] + ("; caida %.2f m" % caida if caida > 0.02 else "")
            cand.append([s, nota, 3])
        for a, b in r["tapados"]:
            for s in (a, b):
                if 0.2 < s < L - 0.2: cand.append([s, "Inicio de tapado" if s == a else "Fin de tapado", 2])
        for i in range(1, len(Pf)):
            if abs(Pf[i][1] - Pf[i - 1][1]) > 0.02:
                cand.append([Pf[i - 1][0], "Cambio de borde", 1]); cand.append([Pf[i][0], "Cambio de borde", 1])
        cand.sort(key=lambda c: (c[0], -c[2]))
        sel = []
        for c in cand:
            if sel and c[0] - sel[-1][0] < 0.25:
                notas = [t for t in (sel[-1][1], c[1]) if t]
                if c[2] > sel[-1][2]: sel[-1] = list(c)
                sel[-1][1] = "; ".join(dict.fromkeys(t for n_ in notas for t in n_.split("; ")))
                continue
            sel.append(list(c))
        lst = []
        for s, nota, _ in sel:
            nct, ncf = _valor(Pf, s); k += 1
            tap = _tapado(r, s + 0.01) if s < L - 0.01 else _tapado(r, s - 0.01)
            lst.append({"n": k, "s": s, "nct": nct, "ncf": ncf, "h": nct - ncf, "tap": tap, "nota": nota, "eje": r["codigo"],
                        "b": _ancho_en(r, s + 0.01 if s < L - 0.01 else s - 0.01, anchos, P)})
        out[r["codigo"]] = lst
    return out


def _franjas(R):
    f = ESC_P / 1000.0; largo = (ANCHO_LAM - CAB - 14) * f
    franjas, cur, usado = [], [], 0.0
    for r in R["ramales"]:
        n = max(1, math.ceil(r["L"] / largo - 1e-9)); paso = r["L"] / n
        for k in range(n):
            w = CAB + paso / f + 14
            if cur and usado + w > ANCHO_LAM: franjas.append(cur); cur, usado = [], 0.0
            cur.append((r, k * paso, (k + 1) * paso, n)); usado += w
    if cur: franjas.append(cur)
    return franjas


def _filas_cajas(secs, xs, x_min, x_max, ancho):
    paso = ancho + 2.0; filas = 1
    while len(secs) * paso > (x_max - x_min) * filas and filas < 4: filas += 1
    res = [None] * len(secs)
    for f in range(filas):
        idx = [i for i in range(len(secs)) if i % filas == f]; pos = []
        for j, i in enumerate(idx): pos.append(max(xs[i], x_min + ancho / 2) if not pos else max(xs[i], pos[-1] + paso))
        for j in range(len(pos) - 1, -1, -1):
            lim = x_max - ancho / 2 if j == len(pos) - 1 else pos[j + 1] - paso
            pos[j] = min(pos[j], lim)
        for i, c in zip(idx, pos): res[i] = (f, c)
    return res, filas


class Planos:
    def __init__(self, R, red, sitio, P, anchos, proyecto):
        self.R, self.P, self.anchos = R, P, anchos
        self.EL, self.EM = P["e_fondo"], P["e_muro"]
        self.NPT = sitio.borde if sitio.borde is not None else max(p[1] for r in R["ramales"] for p in r["perfil"])
        self.SEC = secciones(R, set(red.descargas), anchos, P)
        rotulo_de(proyecto)

    # ------------------------------------------------------------------- perfiles
    def alto_pieza(self, pz):
        r, s0, s1, n = pz
        Pf = [p for p in r["perfil"] if s0 - 1e-6 <= p[0] <= s1 + 1e-6]
        zmin = min(p[2] for p in Pf) - self.EL
        ztop = max(self.NPT, max(p[1] for p in Pf))
        nref = math.ceil((ztop - zmin) / PASO_REF + 1e-9)
        secs = [x for x in self.SEC[r["codigo"]] if s0 - 1e-6 <= x["s"] <= s1 + 1e-6]
        f = ESC_P / 1000.0
        _, filas = _filas_cajas(secs, [(x["s"] - s0) / f for x in secs], -6, (s1 - s0) / f + 6, CAJA_W)
        return ALTO_FILA * len(FILAS) + 10 + nref * PASO_REF / f + 14 + filas * CAJA_PASO + 9, filas

    def perfil(self, lam, pz, xmm, ymm):
        r, s0, s1, n = pz; f = lam.f; NPT, EL, EM = self.NPT, self.EL, self.EM
        Pf = [p for p in r["perfil"] if s0 - 1e-6 <= p[0] <= s1 + 1e-6]
        secs = [x for x in self.SEC[r["codigo"]] if s0 - 1e-6 <= x["s"] <= s1 + 1e-6]
        zmin = min(p[2] for p in Pf) - EL
        ztop = max(NPT, max(p[1] for p in Pf))
        nref = math.ceil((ztop - zmin) / PASO_REF + 1e-9); nsob = math.ceil((ztop - NPT) / PASO_REF - 1e-9)
        xg0, xd0 = xmm, xmm + CAB
        X = lambda s: lam.P(xd0 + (s - s0) / f, 0)[0]
        yg = ymm; yg1 = yg + ALTO_FILA * len(FILAS); yb = yg1 + 10
        y0 = yb + (nref - nsob) * PASO_REF / f
        Yz = lambda z: lam.P(0, y0 + (z - NPT) / f)[1]
        xfin = X(s1)
        for i, t in enumerate(FILAS + [None]):
            yy = yg1 - i * ALTO_FILA
            lam.linea(lam.P(xg0, yy), (xfin, lam.P(0, yy)[1]), "GUITARRA")
            if t: lam.texto(lam.P(xd0 - 2, yy - ALTO_FILA / 2), t, 1.55, "TEXTOS", TA.MIDDLE_RIGHT)
        lam.linea(lam.P(xd0, yg), lam.P(xd0, yg1), "GUITARRA")
        for i in range(-nsob, nref - nsob + 1):
            z = NPT - i * PASO_REF
            lam.linea((X(s0) - 3 * f, Yz(z)), (xfin, Yz(z)), "PERF-REF")
            lam.texto((X(s0) - 3.5 * f, Yz(z)), "%.2f" % (-i * PASO_REF), 1.15, "TEXTOS", TA.MIDDLE_RIGHT)
        lam.textos(lam.P(xg0, y0 - 3), ["Altura relativa", "al NPT (m)"], 1.6, "TEXTOS", TA.LEFT)
        k = math.ceil(s0 / 5.0 - 1e-9) * 5; marcas = []
        while k <= s1 + 1e-6: marcas.append(k); k += 5
        for k in marcas:
            lam.linea((X(k), lam.P(0, yb)[1]), (X(k), lam.P(0, yg)[1]), "GRILLA")
            if (s1 - k) / f > 18 or abs(s1 - k) < 1e-6:
                lam.texto((X(k), lam.P(0, yg1 + 3)[1]), "0+%02d" % k, 1.6, "TEXTOS", TA.BOTTOM_CENTER)
        if not marcas or abs(s1 - marcas[-1]) > 1e-6:
            lam.texto((xfin, lam.P(0, yg1 + 3)[1]), "0+%.2f" % s1, 1.6, "TEXTOS", TA.BOTTOM_CENTER)
        grupos, cur, est = [], [Pf[0]], None
        for a, b in zip(Pf[:-1], Pf[1:]):
            e = _tapado(r, (a[0] + b[0]) / 2)
            if est is None or e == est: cur.append(b)
            else: grupos.append((est, cur)); cur = [a, b]
            est = e
        grupos.append((est, cur))
        for tap, g in grupos:
            if len(g) < 2: continue
            lam.poli([(X(p[0]), Yz(p[1])) for p in g], "PERF-TAPA" if tap else "PERF-NCT")
            if tap: lam.poli([(X(p[0]), Yz(p[1] - self.P["e_tapa"])) for p in g], "PERF-TAPA")
        lam.poli([(X(p[0]), Yz(p[2])) for p in Pf], "PERF-FONDO")
        lam.poli([(X(p[0]), Yz(p[2] - EL)) for p in Pf], "PERF-FONDO")
        pos, filas = _filas_cajas(secs, [(x["s"] - s0) / f for x in secs], -6, (s1 - s0) / f + 6, CAJA_W)
        ytop = Yz(max(p[1] for p in Pf))
        for x, (fila, xc) in zip(secs, pos):
            xs = X(x["s"])
            lam.linea((xs, Yz(x["nct"])), (xs, Yz(x["ncf"] - EL)), "PERF-SECCION")
            lam.linea((xs, lam.P(0, yg)[1]), (xs, lam.P(0, yg1)[1]), "GUITARRA")
            lineas = ["NCT: %.2f" % x["nct"], "NCF: %.2f" % x["ncf"], " H: %.2f m" % x["h"], " b: %.2f m" % x["b"], " EL: %.2f m" % EL, " EM: %.2f m" % EM]
            if x["nota"]: lineas += x["nota"].split("; ")
            alto = 2.4 + 3.7 * len(lineas)
            cx = lam.P(xd0 + xc, 0)[0]; yc0 = ytop + (12 + fila * CAJA_PASO) * f; w = CAJA_W * f
            lam.rect(cx - w / 2, yc0, cx + w / 2, yc0 + alto * f, "PERF-CAJA")
            for i, t in enumerate(lineas):
                lam.texto((cx - w / 2 + 1.3 * f, yc0 + (alto - 2.8 - 3.7 * i) * f), t, 1.45 if i < 6 else 1.15, "TEXTOS", TA.MIDDLE_LEFT)
            lam.texto((cx, yc0 + (alto + 2.4) * f), "SECCION %02d" % x["n"], 1.8, "TITULOS", TA.BOTTOM_CENTER)
            lam.linea((cx - 11 * f, yc0 + (alto + 1.8) * f), (cx + 11 * f, yc0 + (alto + 1.8) * f), "TITULOS")
            lam.flecha((cx, yc0), (xs, Yz(x["nct"])), "PERF-CAJA", tam_mm=2.0)
            lam.texto((xs + 0.6 * f, lam.P(0, yg1 - ALTO_FILA / 2)[1]), "%.2f" % x["s"], 1.0, "TEXTOS", TA.MIDDLE_CENTER, rot=90)
            lam.texto((xs + 0.6 * f, lam.P(0, yg1 - 1.5 * ALTO_FILA)[1]), "S-%02d" % x["n"], 1.0, "TEXTOS", TA.MIDDLE_CENTER, rot=90)
        todas = sorted(self.SEC[r["codigo"]], key=lambda x: x["s"])
        for A, Bs in zip(todas[:-1], todas[1:]):
            a, b = A["s"], Bs["s"]; va, vb = max(a, s0), min(b, s1)
            if vb - va < 1e-6 or (vb - va) / f < 7: continue
            za, zb = _valor(r["perfil"], a)[1], _valor(r["perfil"], b)[1]
            xm = (X(va) + X(vb)) / 2
            lon = "%.2f" % (b - a)
            if (a < s0 - 1e-6 or b > s1 + 1e-6) and (vb - va) / f > 40: lon += "  (S-%02d a S-%02d)" % (A["n"], Bs["n"])
            lam.texto((xm, lam.P(0, yg1 - 2.5 * ALTO_FILA)[1]), lon, 1.2, "TEXTOS", TA.MIDDLE_CENTER)
            lam.texto((xm, lam.P(0, yg1 - 3.5 * ALTO_FILA)[1]), "%.2f" % (100 * (za - zb) / (b - a)), 1.2, "TEXTOS", TA.MIDDLE_CENTER)
        yt = lam.P(0, (ytop - lam.oy) / f + 12 + filas * CAJA_PASO + 4)[1]
        desc = "DE %s A %s" % (r["nudos"][0], r["nudos"][-1])
        lam.texto((lam.P(xg0, 0)[0], yt), "PERFIL LONGITUDINAL %s - %s - PROG. %s A %s" % (r["codigo"], desc, prog(s0), prog(s1)), 2.0, "TITULOS", TA.LEFT)
        return CAB + (s1 - s0) / f

    def leyenda_perfil(self, lam, xmm, ymm):
        lam.leyenda2(xmm, ymm, [("linea", "PERF-NCT", "Borde superior de cuneta (NCT) - tramo abierto con rejilla"),
                                ("linea", "PERF-TAPA", "Tramo tapado: cara superior e inferior de la losa"),
                                ("linea", "PERF-FONDO", "Cota de fondo (NCF) y cara inferior de la losa de fondo"),
                                ("linea", "PERF-SECCION", "Seccion (corte transversal en las laminas de secciones)"),
                                ("linea", "PERF-REF", "Altura relativa al NPT cada 0.15 m (0.00 = NPT %+.2f)" % self.NPT)],
                     hmm=1.6, ancho_col=150, filas_col=3)

    def perfiles(self, doc, ox0, oy0, sep, num0, pref):
        franjas = _franjas(self.R); f = ESC_P / 1000.0
        lams, i, num = [], 0, num0
        while i < len(franjas):
            lam = B.Lamina(doc, ox0 + (num - num0) * sep, oy0, ESC_P, "%s-%02d" % (pref, num), "PERFILES LONGITUDINALES DE CUNETAS POR EJE",
                           "NCT, NCF, PROFUNDIDAD, ANCHO, LONGITUD Y PENDIENTE POR SECCION - ESC. H = V = 1/%d" % ESC_P)
            ytop = 580.0
            while i < len(franjas):
                a = max(self.alto_pieza(p)[0] for p in franjas[i])
                if ytop - a < 112.0 and ytop < 579: break
                x = 30.0
                for p in franjas[i]: x += self.perfil(lam, p, x, ytop - a) + 14
                ytop -= a + 4; i += 1
            self.leyenda_perfil(lam, 30, 100)
            lams.append(lam); num += 1
        return lams

    # ------------------------------------------------------------------- cortes
    def corte(self, lam, x, x0, y0):
        P = self.P; EL, EM = self.EL, self.EM; b = x["b"]; e = EM; W = 2 * EM + b
        H = x["h"]; tap = x["tap"]; ytop = y0 + EL + H; et = P["e_tapa"]; es = P["e_solado"]
        capa = "SEC-TAPADA" if tap else "SEC-ABIERTA"
        sol = [(x0 - 0.05, y0 - es), (x0 + W + 0.05, y0 - es), (x0 + W + 0.05, y0), (x0 - 0.05, y0)]
        lam.relleno(sol, "SEC-SOLADO"); lam.poli(sol, "SEC-PISO", cerrada=True)
        if tap:
            ext = [(x0, y0), (x0 + W, y0), (x0 + W, ytop), (x0, ytop)]
            hueco = [(x0 + e, y0 + EL), (x0 + e + b, y0 + EL), (x0 + e + b, ytop - et), (x0 + e, ytop - et)]
            lam.relleno(ext, "CONCRETO-ACHURADO"); lam.relleno(hueco, "SEC-HUECO")
            lam.poli(ext, capa, cerrada=True); lam.poli(hueco, capa, cerrada=True)
        else:
            u = [(x0, y0), (x0 + W, y0), (x0 + W, ytop), (x0 + e + b, ytop), (x0 + e + b, y0 + EL), (x0 + e, y0 + EL), (x0 + e, ytop), (x0, ytop)]
            lam.relleno(u, "CONCRETO-ACHURADO"); lam.poli(u, capa, cerrada=True)
            a, t = 0.0254, 0.0048
            for xa, sg in ((x0 + e, 1), (x0 + e + b, -1)):
                lam.poli([(xa, ytop - a), (xa, ytop), (xa + sg * a, ytop)], "SEC-REJILLA")
            lam.rect(x0 + e - 0.012, ytop, x0 + e + b + 0.012, ytop + t, "SEC-REJILLA")
        yp = ytop; j = 0.0254
        piso = [(x0 - j, yp), (x0 - j - 0.34, yp), (x0 - j - 0.34, yp - 0.10), (x0 - j - 0.14, yp - 0.10), (x0 - j - 0.08, yp - 0.24), (x0 - j, yp - 0.24)]
        lam.relleno(piso, "CONCRETO-ACHURADO"); lam.poli(piso, "SEC-PISO", cerrada=True)
        jun = [(x0 - j, yp), (x0, yp), (x0, yp - 0.24), (x0 - j, yp - 0.24)]
        lam.relleno(jun, "SEC-JUNTA"); lam.poli(jun, "SEC-PISO", cerrada=True)
        r = 0.045; con_acero = tap or H >= P["h_acero"] - 1e-6; sep = 0.22 if tap else 0.20
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
        # abajo (bajo el solado): muro, libre, muro y total; derecha: losa de fondo y tapa (6), altura libre (13), excavacion (20)
        yb = y0 - es
        lam.cota((x0, yb), (x0 + e, yb), -6, True); lam.cota((x0 + e, yb), (x0 + e + b, yb), -6, True)
        lam.cota((x0 + e + b, yb), (x0 + W, yb), -6, True); lam.cota((x0, yb), (x0 + W, yb), -13, True)
        lam.cota((x0 + W, y0), (x0 + W, y0 + EL), 6, False)
        lam.cota((x0 + W, y0 + EL), (x0 + W, ytop - (et if tap else 0.0)), 13, False)
        if tap: lam.cota((x0 + W, ytop - et), (x0 + W, ytop), 6, False)
        lam.cota((x0 + W, yb), (x0 + W, ytop), 20, False, texto="EXC. %.2f" % (ytop - yb))
        if con_acero:
            lam.llamada((x0 + r, y0 + r + (ytop - y0) * 0.45), (x0 - 0.62, y0 + (ytop - y0) * 0.30), ['%%%%c3/8"@%.2f' % sep, "Longitudinal"], hmm=1.4)
            lam.llamada((x0 + W - r, ytop - 0.12), (x0 + W + 0.58, ytop + 0.06), ['%%c3/8"@0.25', "Transversal"], hmm=1.4)
        else:
            lam.llamada((x0 + e / 2, y0 + (ytop - y0) * 0.5), (x0 - 0.62, y0 + (ytop - y0) * 0.30), ["CONCRETO SIMPLE", "SIN ACERO (h < %.2f)" % P["h_acero"]], hmm=1.4)
        lam.llamada((x0 - j / 2, yp - 0.05), (x0 - 0.62, yp + 0.20), ["JUNTA", 'ASFALTICA E=1"'], hmm=1.4)
        lam.llamada((x0 + W * 0.3, y0 - es / 2), (x0 - 0.62, y0 - 0.12), ["SOLADO", "E=%.2f" % es], hmm=1.4)
        if not tap:
            lam.llamada((x0 + e + b, ytop + 0.004), (x0 + W + 0.04, ytop + 0.24), ["REJILLA METALICA MOVIL", 'PLATINAS DE 1" X 3/16"'], hmm=1.4)
        lam.texto((x0 + W / 2, ytop + 0.50), "SECCION %02d" % x["n"], 3.0, "TITULOS", TA.BOTTOM_CENTER)
        lam.linea((x0 + W / 2 - 0.32, ytop + 0.48), (x0 + W / 2 + 0.32, ytop + 0.48), "TITULOS")
        lam.texto((x0 + W / 2, ytop + 0.40), "%s - PROG. %s - %s" % (x["eje"], prog(x["s"]), "TAPADA" if tap else "CON REJILLA"), 1.5, "TEXTOS", TA.MIDDLE_CENTER)
        lam.texto((x0 + W / 2, ytop + 0.33), "LIBRE %.2f x %.2f - TOTAL %.2f - EXCAV. %.2f - ESC. 1/%d" % (
            b, H - (et if tap else 0.0), W, H + EL + es, ESC_S), 1.4, "TEXTOS", TA.MIDDLE_CENTER)

    def cortes(self, doc, ox0, oy0, sep, num0, pref):
        todas = [x for lst in self.SEC.values() for x in lst]
        f = ESC_S / 1000.0; cw = 116.0; ncol = int((ANCHO_LAM - 6) // cw)
        P = self.P
        lams, i, num = [], 0, num0
        while i < len(todas):
            lam = B.Lamina(doc, ox0 + (num - num0) * sep, oy0, ESC_S, "%s-%02d" % (pref, num), "SECCIONES TRANSVERSALES DE CUNETAS",
                           "CORTE DE CADA SECCION DE LOS PERFILES: DIMENSIONES, ACERO, REJILLA, LOSA, SOLADO Y JUNTA - ESC. 1/%d" % ESC_S)
            ytop = 578.0
            while i < len(todas):
                fila = todas[i:i + ncol]
                hmax = max(self.EL + P["e_solado"] + x["h"] for x in fila)
                alto = (hmax + 0.62) / f + 22
                if ytop - alto < 112.0: break
                for c, x in enumerate(fila):
                    x0, y0 = lam.P(30 + c * cw + 40, ytop - alto + 20)
                    self.corte(lam, x, x0, y0 + P["e_solado"])
                i += len(fila); ytop -= alto + 2
            lam.notas(30, 100, "NOTAS", [
                "1. Medidas libres interiores b x h; ancho total = b + 2 muros de %.2f m; excavacion = h + losa de fondo %.2f m + solado %.2f m." % (self.EM, self.EL, P["e_solado"]),
                "2. Acero fy = 4200 kg/cm2 solo con h >= %.2f m y en tramos tapados: marco 3/8\" @ 0.25 m; longitudinales 3/8\" @ 0.20 m (rejilla) y @ 0.22 m (tapada). Con h menor: concreto simple." % P["h_acero"],
                "3. Rejilla metalica movil de platinas 1\" x 3/16\" sobre angulos 1\" x 1\" x 3/16\" anclados a los muros (tramos abiertos); losa tapa de %.2f m en los tapados." % P["e_tapa"],
                "4. Junta asfaltica e = 1\" entre la cuneta y el piso, al mismo nivel. H = NCT - NCF; en la tapada incluye la losa tapa.",
                "5. Lloraderos PVC 3\" @ %.2f m con caja filtrante de 0.30 x 0.30 (grava y geotextil) solo en el muro que da a area verde (ver planta)." % P["llor_sep"]],
                hmm=1.6, ancho_mm=590)
            lams.append(lam); num += 1
        return lams


def dxf_planos(ruta, R, red, sitio, P, anchos, proyecto, curvas, V, LLt, LLp, secciones_eje, pref="DC", num0=1, techos=None, sums=None):
    """PLANOS_CUNETAS.dxf: planta general (num0), cuadros (num0 + 1), perfiles y secciones, con una presentacion por lamina.
    Devuelve (ruta, [(codigo, titulo)], numero de secciones)."""
    from . import planta_lamina as PLT
    doc = B.nuevo_documento(); capas(doc); PLT.capas(doc)
    PL = Planos(R, red, sitio, P, anchos, proyecto)
    l1 = PLT.dc01(doc, "%s-%02d" % (pref, num0), R, red, sitio, curvas, P, anchos, V, LLp, proyecto, techos, sums)
    sep_p = 841 * ESC_P / 1000 + 15
    l2 = PLT.dc02(doc, "%s-%02d" % (pref, num0 + 1), -sep_p, 0.0, secciones_eje, V, LLt, P, techos, sums)
    lp = PL.perfiles(doc, 0.0, 0.0, sep_p, num0 + 2, pref)
    xs = len(lp) * sep_p + 20
    ls = PL.cortes(doc, xs, 0.0, 841 * ESC_S / 1000 + 15, num0 + 2 + len(lp), pref)
    todas = [l1, l2] + lp + ls
    LY.presentaciones(doc, {l.codigo: l for l in todas})
    doc.saveas(ruta)
    return ruta, [(l.codigo, l.titulo) for l in todas], sum(len(v) for v in PL.SEC.values())
