"""Red de cunetas en planta a partir de las lineas que traza el usuario.

Reglas (conocimiento/04_cunetas_sobre_terreno.md):
- Las lineas del usuario mandan: no se mueven ni se juntan; solo se agregan las uniones necesarias hasta las descargas.
- Ninguna cuneta sale del cerco; el agua sale por un pase en el cimiento del cerco (descarga D1, D2, ...), donde el terreno
  exterior queda bajo la cota de fondo a pocos metros. Todo por gravedad.
- Las descargas van en los lados bajos que muestran las curvas; si una red se hace muy profunda, se busca otra descarga.
- Quiebres a 45 grados: cada esquina de mas de 50 grados se ochava con un chaflan de 0.60 m por lado.

Pasos: 1) grafo con las lineas (uniones en extremos, cruces y llegadas en T); 2) candidatos de descarga a lo largo del cerco;
3) uniones nuevas validas (dentro del cerco, sin cruzar edificaciones ni otras cunetas); 4) eleccion de uniones y descargas
(arbol de menor longitud con el cerco como sumidero) con revision de profundidad y salida; 5) sentido de flujo (cada punto va a
la descarga por el camino mas corto; en un circuito cerrado el agua se divide en el punto alto); 6) ejes (ramales) y chaflanes.
"""
import heapq
import math
from collections import defaultdict

import numpy as np
from shapely.geometry import LineString, Point, MultiPoint
from shapely.ops import substring, unary_union
from shapely.strtree import STRtree

from . import geom


class UF:
    def __init__(self): self.p = {}
    def f(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]; a = self.p[a]
        return a
    def u(self, a, b):
        ra, rb = self.f(a), self.f(b)
        if ra == rb: return False
        self.p[ra] = rb; return True


# ----------------------------------------------------------------------------------------------------------- grafo base
def grafo_usuario(polilineas, tol):
    """Nodos y aristas rectas con las lineas del usuario. Une extremos cercanos (tol), corta en cruces y en llegadas en T."""
    L = []
    for pts in polilineas:
        ls = LineString(pts).simplify(0.02)
        if ls.length > 0.05: L.append(ls)
    cortes = [set() for _ in L]
    arbol = STRtree(L)
    for i, Li in enumerate(L):
        for j in arbol.query(Li.buffer(tol)):
            j = int(j)
            if j == i: continue
            Lj = L[j]
            x = Li.intersection(Lj)
            for p in (list(x.geoms) if hasattr(x, "geoms") else [x]):
                if isinstance(p, Point) and not p.is_empty: cortes[i].add(round(Li.project(p), 4))
            for e in (Lj.coords[0], Lj.coords[-1]):
                pe = Point(e)
                if Li.distance(pe) <= tol:
                    s = Li.project(pe)
                    if tol < s < Li.length - tol: cortes[i].add(round(s, 4))
    piezas = []
    for i, Li in enumerate(L):
        ss = [0.0] + sorted(s for s in cortes[i] if 0.05 < s < Li.length - 0.05) + [Li.length]
        for a, b in zip(ss[:-1], ss[1:]):
            if b - a > 0.05:
                pz = substring(Li, a, b); cs = list(pz.coords)
                for k in range(len(cs) - 1): piezas.append((cs[k], cs[k + 1]))
    # nodos: extremos agrupados a menos de tol
    ext = [p for pz in piezas for p in pz]
    uf = UF()
    P = np.array(ext)
    for k in range(len(ext)):
        d = np.hypot(P[:, 0] - ext[k][0], P[:, 1] - ext[k][1])
        for m in np.nonzero(d <= tol)[0]: uf.u(k, int(m))
    grupos = defaultdict(list)
    for k in range(len(ext)): grupos[uf.f(k)].append(k)
    N, id_de = {}, {}
    for n, (g, ks) in enumerate(sorted(grupos.items(), key=lambda e: (round(ext[e[1][0]][0], 2), round(ext[e[1][0]][1], 2)))):
        nid = "n%d" % n
        N[nid] = (float(np.mean([ext[k][0] for k in ks])), float(np.mean([ext[k][1] for k in ks])))
        for k in ks: id_de[k] = nid
    E, vistos = [], set()
    for k, (a, b) in enumerate(piezas):
        u, v = id_de[2 * k], id_de[2 * k + 1]
        if u == v or (min(u, v), max(u, v)) in vistos: continue
        vistos.add((min(u, v), max(u, v)))
        E.append({"u": u, "v": v, "origen": "usuario"})
    return N, E


class Red:
    def __init__(self, sitio, terreno, P, polilineas, descargas_fijas=None):
        self.S, self.T, self.P = sitio, terreno, P
        self.avisos = []
        self.N, self.E = grafo_usuario(polilineas, P["tol_union"])
        self.n_usuario = len(self.E)
        fuera = [e for e in self.E if not self.S.interior.buffer(0.02).covers(LineString([self.N[e["u"]], self.N[e["v"]]]))]
        if fuera:
            self.avisos.append("%d tramos de las lineas del usuario quedan a menos de 0.30 m del cerco o fuera de el; se conservan "
                               "como los trazo el usuario (revisar)." % len(fuera))
        self.descargas_fijas = descargas_fijas or []
        obst = self.S.muros if not self.S.muros.is_empty else self.S.techos_plano.buffer(-1.0)
        if not self.S.no_cruzar.is_empty: obst = geom.union([obst, self.S.no_cruzar.buffer(-0.5)])
        self.obst = obst

    # --------------------------------------------------------------------------------------------- candidatos de descarga
    def candidatos_descarga(self, paso=1.0):
        """Puntos del cerco cada 1 m con la cota del terreno exterior que debe quedar bajo la cota de fondo."""
        anillo = self.S.cerco.exterior
        out = []
        n = int(anillo.length / paso)
        for k in range(n):
            s = k * paso
            q = anillo.interpolate(s); q2 = anillo.interpolate(min(anillo.length, s + 0.1))
            ux, uy = q2.x - q.x, q2.y - q.y; Lu = math.hypot(ux, uy)
            if Lu == 0: continue
            ux, uy = ux / Lu, uy / Lu
            nin = (-uy, ux)                                   # cerco antihorario: interior a la izquierda
            zs = []
            for d in np.arange(0.25, self.P["desc_dist_ext"] + 1e-9, 0.25):
                zt = self.T.z(q.x - nin[0] * d, q.y - nin[1] * d)
                if np.isfinite(zt): zs.append(zt)
            if not zs: continue
            b = (q.x + nin[0] * self.P["d_cerco"], q.y + nin[1] * self.P["d_cerco"])
            if not self.S.interior.buffer(0.05).contains(Point(b)): continue
            ras = self.S.rasante(*b)
            out.append({"s": s, "q": (q.x, q.y), "b": b, "nin": nin, "z_req": min(zs), "ras": ras,
                        "holgura": ras - self.P["h0"] - (min(zs) + self.P["desc_margen"])})
        return out

    # --------------------------------------------------------------------------------------------- validez de una union
    def _valida(self, a, b, ignorar=()):
        ls = LineString([a, b])
        if ls.length < 0.05: return True
        if not self.S.interior.buffer(0.02).covers(ls): return False
        if not self.obst.is_empty and ls.intersection(self.obst).length > 0.05: return False
        for e in self.E:
            if e["u"] in ignorar or e["v"] in ignorar: continue
            le = LineString([self.N[e["u"]], self.N[e["v"]]])
            if ls.crosses(le) or (ls.distance(le) < 0.05 and not ls.touches(le)):
                x = ls.intersection(le)
                if not x.is_empty and (Point(a).distance(x) > 0.1 and Point(b).distance(x) > 0.1): return False
        return True

    def componentes(self):
        uf = UF()
        for n in self.N: uf.f(n)
        for e in self.E: uf.u(e["u"], e["v"])
        g = defaultdict(list)
        for n in self.N: g[uf.f(n)].append(n)
        return list(g.values())

    def _punto_en_arista(self, p, nodos):
        """Punto mas cercano a p sobre las aristas de un conjunto de nodos: (distancia, arista, punto)."""
        mejor = None
        for e in self.E:
            if e["u"] not in nodos: continue
            ls = LineString([self.N[e["u"]], self.N[e["v"]]])
            d = ls.distance(Point(p))
            if mejor is None or d < mejor[0]:
                q = ls.interpolate(ls.project(Point(p))); mejor = (d, e, (q.x, q.y))
        return mejor

    # --------------------------------------------------------------------------------------------- eleccion de uniones y descargas
    def resolver(self):
        P = self.P
        comp = self.componentes()
        cid = {n: k for k, ns in enumerate(comp) for n in ns}
        grados = defaultdict(int)
        for e in self.E: grados[e["u"]] += 1; grados[e["v"]] += 1
        # uniones entre componentes: desde un extremo (grado 1) de una a la arista mas cercana de la otra
        uniones = []
        for i, ns in enumerate(comp):
            ext = [n for n in ns if grados[n] <= 1] or ns
            for j, ms in enumerate(comp):
                if i == j: continue
                mset = set(ms); best = None
                for n in ext:
                    r = self._punto_en_arista(self.N[n], mset)
                    if r and r[0] <= P["union_max"] and (best is None or r[0] < best[0]) and self._valida(self.N[n], r[2], ignorar=(n,)):
                        best = (r[0], n, r[1], r[2])
                if best: uniones.append({"costo": best[0], "i": i, "j": j, "n": best[1], "arista": best[2], "p": best[3]})
        # descargas: desde cualquier nodo hasta el cerco (pase perpendicular al cerco)
        cand = self.candidatos_descarga()
        if self.descargas_fijas:
            fijos = []
            for k, d in enumerate(self.descargas_fijas):
                c = min(cand, key=lambda c: math.dist(c["q"], (d["x"], d["y"]))) if cand else None
                if c is None or math.dist(c["q"], (d["x"], d["y"])) > 3.0:
                    self.avisos.append("La descarga %s indicada no esta sobre el cerco o fuera del terreno con curvas." % d.get("nombre", k + 1))
                    continue
                c = dict(c); c["nombre"] = d.get("nombre"); fijos.append(c)
            cand = fijos
        self.candidatos = cand
        zloc = []
        for c in cand:
            vec = [o["z_req"] for o in cand if abs(o["s"] - c["s"]) <= 30 or abs(abs(o["s"] - c["s"]) - self.S.cerco.exterior.length) <= 30]
            zloc.append(min(vec))
        # salidas: para cada nudo, la mejor descarga a su alcance (union recta y valida hasta el cerco)
        salidas = []
        for i, ns in enumerate(comp):
            for n in ns:
                x = self.N[n]; op = []
                for k, c in enumerate(cand):
                    dl = math.dist(x, c["b"])
                    if dl > P["union_max"] or c["holgura"] <= 0: continue
                    op.append((dl + 10.0 * (c["z_req"] - zloc[k]), k, dl))
                op.sort()
                for costo, k, dl in op[:6]:
                    if self._valida(x, cand[k]["b"], ignorar=(n,)):
                        salidas.append({"costo": costo, "i": i, "k": k, "n": n, "L": dl}); break
        self.comp, self.uniones, self.salidas = comp, uniones, salidas
        ban_q, ban_u, forzadas = set(), set(), []
        for vuelta in range(60):
            elegidas = self._kruskal(len(comp), uniones, salidas, ban_q, ban_u, forzadas)
            if elegidas is None:
                self.avisos.append("Hay lineas que no pueden llegar a ninguna descarga por gravedad sin salir del cerco o cruzar una "
                                   "edificacion: trace la union o indique la descarga.")
                elegidas = self._kruskal(len(comp), uniones, salidas, ban_q, ban_u, forzadas, parcial=True)
                self._armar(elegidas, cand); break
            self._armar(elegidas, cand)
            prob = self._revisar(cand, elegidas)
            if not prob: break
            tipo, dato = prob
            if tipo == "prohibir": ban_q.update(dato)
            elif tipo == "forzar": forzadas.append(dato)
            elif tipo == "cortar": ban_u.add(dato)
        else:
            self.avisos.append("No se logro dejar todos los sistemas bajo la profundidad objetivo de %.2f m; revisar descargas." % P["prof_max_objetivo"])
        return self

    def _kruskal(self, nc, uniones, salidas, ban_q, ban_u, forzadas, parcial=False):
        """Arbol de menor longitud: uniones y salidas al cerco (sumidero). Las salidas forzadas entran siempre (una red puede
        tener varias descargas)."""
        SUM = nc; Lc = self.S.cerco.exterior.length
        uf = UF(); out = []
        for k in range(nc + 1): uf.f(k)
        usadas_q = []
        def cerca(k):
            qd = self.candidatos[k]["s"]
            return any(min(abs(qd - q2), Lc - abs(qd - q2)) < self.P["desc_sep_min"] and k != k2 for q2, k2 in usadas_q)
        for si in forzadas:
            s = salidas[si]
            if s["k"] in ban_q: continue
            uf.u(s["i"], SUM); out.append(("s", s)); usadas_q.append((self.candidatos[s["k"]]["s"], s["k"]))
        ar = [("u", u["costo"], iu, u) for iu, u in enumerate(uniones) if iu not in ban_u] + \
             [("s", s["costo"], si, s) for si, s in enumerate(salidas) if s["k"] not in ban_q and si not in forzadas]
        ar.sort(key=lambda e: e[1])
        for t, c, idx, d in ar:
            if t == "u":
                if uf.u(d["i"], d["j"]): out.append((t, dict(d, idx=idx)))
            else:
                if uf.f(d["i"]) == uf.f(SUM) or cerca(d["k"]): continue
                uf.u(d["i"], SUM); out.append((t, d)); usadas_q.append((self.candidatos[d["k"]]["s"], d["k"]))
        raiz = uf.f(SUM)
        if not parcial and any(uf.f(k) != raiz for k in range(nc)): return None
        return out

    def _armar(self, elegidas, cand):
        """Grafo final: lineas del usuario + uniones + tramos a las descargas."""
        N = {k: v for k, v in self.N.items()}
        E = [dict(e) for e in self.E]
        self.descargas = {}
        cont = 0
        for t, d in sorted(elegidas, key=lambda e: 0 if e[0] == "u" else 1):
            if t == "u":
                # la union llega en T a una arista de otra componente: se parte esa arista
                e0 = next(e for e in E if {e["u"], e["v"]} == {d["arista"]["u"], d["arista"]["v"]})
                pa, pb = N[e0["u"]], N[e0["v"]]
                if math.dist(d["p"], pa) < 0.3: m = e0["u"]
                elif math.dist(d["p"], pb) < 0.3: m = e0["v"]
                else:
                    m = "t%d" % len(N); N[m] = d["p"]
                    E.remove(e0)
                    E.append({"u": e0["u"], "v": m, "origen": e0["origen"]}); E.append({"u": m, "v": e0["v"], "origen": e0["origen"]})
                E.append({"u": d["n"], "v": m, "origen": "union"})
        # descargas ordenadas por su posicion a lo largo del cerco
        sal = [d for t, d in elegidas if t == "s"]
        porq = defaultdict(list)
        for d in sal: porq[d["k"]].append(d)
        for k in sorted(porq, key=lambda k: cand[k]["s"]):
            cont += 1; c = cand[k]
            nombre = c.get("nombre") or "D%d" % cont
            dn, dd = nombre + "n", nombre
            N[dn] = c["b"]; N[dd] = c["q"]
            for d in porq[k]:
                if math.dist(N[d["n"]], c["b"]) < 0.3:
                    N[dn] = N[d["n"]]
                else:
                    E.append({"u": d["n"], "v": dn, "origen": "union"})
            E.append({"u": dn, "v": dd, "origen": "pase"})
            self.descargas[dd] = {"nombre": dd, "q": c["q"], "b": c["b"], "z_req": c["z_req"], "nin": c["nin"], "s": c["s"]}
        # nodos sin uso (union que llego a un extremo)
        usados = {e["u"] for e in E} | {e["v"] for e in E}
        self.Nf = {k: v for k, v in N.items() if k in usados}
        self.Ef = [e for e in E if e["u"] != e["v"]]
        self._flujo()

    # --------------------------------------------------------------------------------------------- sentido de flujo
    def _flujo(self):
        N, E = self.Nf, self.Ef
        ady = defaultdict(list)
        for k, e in enumerate(E):
            L = math.dist(N[e["u"]], N[e["v"]]); e["L"] = L
            ady[e["u"]].append((e["v"], L, k)); ady[e["v"]].append((e["u"], L, k))
        dist = {n: math.inf for n in N}; sis = {}
        pq = []
        for d in self.descargas:
            dist[d] = 0.0; sis[d] = d; heapq.heappush(pq, (0.0, d))
        while pq:
            dd, n = heapq.heappop(pq)
            if dd > dist[n]: continue
            for m, L, k in ady[n]:
                if dd + L < dist[m] - 1e-9:
                    dist[m] = dd + L; sis[m] = sis[n]; heapq.heappush(pq, (dist[m], m))
        # cada arista se orienta hacia el extremo mas cercano a la descarga; la que no esta en el camino mas corto se divide
        dirigidas = []
        for e in E:
            u, v, L = e["u"], e["v"], e["L"]
            if not (math.isfinite(dist[u]) and math.isfinite(dist[v])): continue
            if abs(dist[u] + L - dist[v]) < 1e-6: dirigidas.append((v, u, e["origen"]))
            elif abs(dist[v] + L - dist[u]) < 1e-6: dirigidas.append((u, v, e["origen"]))
            else:
                t = (dist[v] - dist[u] + L) / 2.0                     # punto alto: igual distancia a la descarga por ambos lados
                pu, pv = N[u], N[v]
                m = "h%d" % len(N); N[m] = (pu[0] + (pv[0] - pu[0]) * t / L, pu[1] + (pv[1] - pu[1]) * t / L)
                dist[m] = dist[u] + t; sis[m] = sis[u]
                dirigidas.append((m, u, e["origen"])); dirigidas.append((m, v, e["origen"]))
        self.dist, self.sistema_de = dist, sis
        self.sin_salida = [n for n in N if not math.isfinite(dist[n])]
        self._ramales(dirigidas)

    def _ramales(self, dirigidas):
        """Ejes: el principal de cada descarga es el recorrido mas largo; los demas llegan a el (y asi sucesivamente).
        Un punto alto (divisoria) puede ser el inicio de dos ejes, uno hacia cada lado."""
        N = self.Nf
        arriba = defaultdict(list); origen = {}
        for a, b, o in dirigidas:
            arriba[b].append(a); origen[(a, b)] = o
        usadas, asignados = set(), set()

        def libre(y):
            return y not in asignados or not arriba[y]

        def mas_largo(x, vis):
            """Recorrido mas largo aguas arriba que termina en x, por aristas no usadas."""
            mejor = (0.0, [x])
            for y in arriba[x]:
                if (y, x) in usadas or y in vis or not libre(y): continue
                L, c = mas_largo(y, vis | {y}) if not (y in asignados) else (0.0, [y])
                L += math.dist(N[y], N[x])
                if L > mejor[0]: mejor = (L, c + [x])
            return mejor

        def agregar(cam, d):
            r = {"nudos": cam, "descarga": d, "L": sum(math.dist(N[a], N[b]) for a, b in zip(cam[:-1], cam[1:]))}
            ramales.append(r)
            for a, b in zip(cam[:-1], cam[1:]): usadas.add((a, b))
            asignados.update(cam)
            return r

        import sys
        sys.setrecursionlimit(20000)
        ramales = []
        for d in sorted(self.descargas, key=lambda d: self.descargas[d]["s"]):
            L, cam = mas_largo(d, {d})
            if len(cam) < 2: continue
            cola = [agregar(cam, d)]
            while cola:
                r = cola.pop(0)
                for n in r["nudos"][1:]:
                    while True:
                        ent = [y for y in arriba[n] if (y, n) not in usadas and libre(y)]
                        if not ent: break
                        mejor = None
                        for y in ent:
                            Ly, cy = mas_largo(y, {y, n}) if y not in asignados else (0.0, [y])
                            Ly += math.dist(N[y], N[n])
                            if mejor is None or Ly > mejor[0]: mejor = (Ly, cy + [n])
                        cola.append(agregar(mejor[1], d))
        self.origen_arista = origen
        self.ramales = ramales

    # --------------------------------------------------------------------------------------------- revision rapida
    def _revisar(self, cand, elegidas):
        """Profundidad y salida de cada descarga (interior nivelado: la cota de fondo baja S0 por metro desde h0)."""
        P = self.P; Lc = self.S.cerco.exterior.length
        peor = None
        for d, info in self.descargas.items():
            nodos = [n for n in self.Nf if self.sistema_de.get(n) == d and math.isfinite(self.dist[n])]
            if not nodos: continue
            Lmax = max(self.dist[n] for n in nodos)
            ras0 = min(self.S.rasante(*self.Nf[n]) for n in nodos)
            cf = ras0 - P["h0"] - P["S0"] * Lmax
            prof = self.S.rasante(*info["b"]) - cf
            if cf < info["z_req"] + P["desc_margen"] and not self.descargas_fijas:
                # se descarta todo el tramo de cerco alrededor que no es mas bajo
                return ("prohibir", {k for k, c in enumerate(cand)
                                     if min(abs(c["s"] - info["s"]), Lc - abs(c["s"] - info["s"])) < P["desc_sep_min"]
                                     and c["z_req"] >= info["z_req"] - 0.02})
            if prof > P["prof_max_objetivo"] and (peor is None or prof > peor[0]): peor = (prof, d, Lmax)
        if not peor or self.descargas_fijas: return None
        prof, d, Lmax = peor
        usadas = [info["s"] for info in self.descargas.values()]
        forz = {id(s) for t, s in elegidas if t == "s"}
        # 1) otra descarga para la parte mas lejana del sistema
        mejor = None
        for si, s in enumerate(self.salidas):
            n = s["n"]
            if self.sistema_de.get(n) != d or id(s) in forz: continue
            c = cand[s["k"]]
            if any(min(abs(c["s"] - u), Lc - abs(c["s"] - u)) < P["desc_sep_min"] for u in usadas): continue
            if self.dist[n] < 0.35 * Lmax: continue
            v = (Lmax - self.dist[n]) + s["L"]
            if mejor is None or v < mejor[0]: mejor = (v, si)
        if mejor: return ("forzar", mejor[1])
        # 2) cortar una union del sistema para que la parte de aguas arriba busque su propia descarga
        for t, u in sorted(elegidas, key=lambda e: -self.dist.get(e[1].get("n", ""), 0) if e[0] == "u" else 0):
            if t == "u" and self.sistema_de.get(u["n"]) == d and any(s["i"] == u["i"] for s in self.salidas):
                return ("cortar", u["idx"])
        return None

    # --------------------------------------------------------------------------------------------- quiebres a 45 grados
    def chaflanes(self):
        P = self.P; N = self.Nf
        nuevos = [list(r["nudos"]) for r in self.ramales]
        hechas = []
        for ir, r in enumerate(self.ramales):
            nudos = r["nudos"]
            for i in range(1, len(nudos) - 1):
                X = nudos[i]; a, x, c = N[nudos[i - 1]], N[X], N[nudos[i + 1]]
                g = geom.giro(a, x, c)
                if g < P["ang_chaflan"] or X in self.descargas or X.endswith("n") and X[:-1] in self.descargas: continue
                (u, Lin), (v, Lout) = geom.unit(a, x), geom.unit(x, c)
                ch = min(P["chaflan"], 0.5 * Lin, 0.5 * Lout)
                xa, xb = X + "~a", X + "~b"
                N[xa] = (x[0] - u[0] * ch, x[1] - u[1] * ch); N[xb] = (x[0] + v[0] * ch, x[1] + v[1] * ch)
                k = nuevos[ir].index(X); nuevos[ir][k:k + 1] = [xa, xb]
                hechas.append({"eje": ir, "nudo": X, "giro": round(g), "chaflan": round(ch, 2)})
                for jr, r2 in enumerate(self.ramales):              # ejes que terminan en la esquina: entran en diagonal
                    if jr != ir and nuevos[jr][-1] == X:
                        w, Lw = geom.unit(N[nuevos[jr][-2]], x)
                        if geom.giro(N[nuevos[jr][-2]], x, c) >= P["ang_chaflan"]:
                            chq = min(P["chaflan"], 0.5 * Lw, ch); xq = X + "~%d" % jr
                            N[xq] = (x[0] - w[0] * chq, x[1] - w[1] * chq); nuevos[jr][-1:] = [xq, xb]
                        else:
                            nuevos[jr][-1:] = [xb]
        for r, nn in zip(self.ramales, nuevos): r["nudos"] = nn
        self.chaflanes_hechos = hechas
        return hechas

    def nombrar(self):
        """EJE-01, EJE-02 ... y nudos P-01, P-02 ... en el orden de los ejes; descargas D1, D2 ..."""
        nombre = {}
        for k, r in enumerate(self.ramales):
            r["codigo"] = "EJE-%02d" % (k + 1)
            for n in r["nudos"]:
                if n not in nombre:
                    nombre[n] = n if n in self.descargas else "P-%02d" % (1 + sum(1 for v in nombre.values() if v.startswith("P")))
        self.nombre = nombre
        sis = {d: i + 1 for i, d in enumerate(sorted(self.descargas, key=lambda d: self.descargas[d]["s"]))}
        for r in self.ramales: r["sistema"] = sis[r["descarga"]]
        return nombre
