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
def _paralelas(a, b, ang=30.0):
    """Dos segmentos con menos de ang grados entre sus direcciones."""
    (x0, y0), (x1, y1) = a.coords[0], a.coords[-1]; (u0, v0), (u1, v1) = b.coords[0], b.coords[-1]
    da, db = math.atan2(y1 - y0, x1 - x0), math.atan2(v1 - v0, u1 - u0)
    d = abs(da - db) % math.pi
    return min(d, math.pi - d) < math.radians(ang)


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
        self.obst_d = obst.buffer(P.get("dist_muro", 0.30)) if not obst.is_empty else obst

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
            if getattr(self.T, "solo", False) and self.T.ln.distance(q) > self.T.ancho: continue     # solo al receptor (colector o canal)
            b = (q.x + nin[0] * self.P["d_cerco"], q.y + nin[1] * self.P["d_cerco"])
            if not self.S.interior.buffer(0.05).contains(Point(b)): continue
            ras = self.S.rasante(*b)
            hol = ras - self.P["h0"] - (min(zs) + self.P["desc_margen"])
            if self.P.get("descarga_alternativa"):       # a pozo de absorcion o camara de bombeo: hasta la profundidad maxima
                hol = max(hol, self.P.get("prof_max_sin_gravedad", self.P["prof_max_objetivo"]) - self.P["h0"])
            out.append({"s": s, "q": (q.x, q.y), "b": b, "nin": nin, "z_req": min(zs), "ras": ras, "holgura": hol})
        return out

    # --------------------------------------------------------------------------------------------- validez de una union
    def _valida(self, a, b, ignorar=()):
        ls = LineString([a, b])
        if ls.length < 0.05: return True
        if not self.S.interior.buffer(0.02).covers(ls): return False
        # a no menos de dist_muro (0.30 m) de las edificaciones, igual que la comprobacion 10
        if not self.obst.is_empty and ls.intersection(self.obst_d).length > 0.05: return False
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
    def _candidatos_union(self, comp):
        """Uniones posibles entre lineas que no se tocan, como las traza un proyectista: perpendicular a la cuneta que recibe
        (llega a su tramo, no a una esquina), o prolongando en linea recta el tramo final; diagonales solo si miden < 3 m.
        Siempre dentro del cerco, sin cruzar edificaciones, losas ni otras cunetas."""
        P = self.P
        grados = defaultdict(list)
        for e in self.E: grados[e["u"]].append(e["v"]); grados[e["v"]].append(e["u"])
        out = []
        aristas = [(e["u"], e["v"], LineString([self.N[e["u"]], self.N[e["v"]]])) for e in self.E]
        for i, ns in enumerate(comp):
            ext = [n for n in ns if len(grados[n]) <= 1] or ns
            for j, ms in enumerate(comp):
                if i == j: continue
                mset = set(ms); op = []
                for n in ext:
                    p0 = self.N[n]
                    for a, b, ls in aristas:
                        if a not in mset: continue
                        s = ls.project(Point(p0)); q = ls.interpolate(s); d = q.distance(Point(p0))
                        if d > P["union_max"]: continue
                        interior = 0.3 < s < ls.length - 0.3
                        if interior or d < 3.0: op.append((d, n, a, b, (q.x, q.y)))
                    if len(grados[n]) == 1:                     # prolongacion del tramo final
                        o = self.N[grados[n][0]]; (ux, uy), Lu = geom.unit(o, p0)
                        rayo = LineString([p0, (p0[0] + ux * P["union_max"], p0[1] + uy * P["union_max"])])
                        for a, b, ls in aristas:
                            if a not in mset: continue
                            x = rayo.intersection(ls)
                            if isinstance(x, Point) and not x.is_empty:
                                op.append((x.distance(Point(p0)), n, a, b, (x.x, x.y)))
                for d, n, a, b, p in sorted(op, key=lambda o: o[0])[:4]:
                    if self._valida(self.N[n], p, ignorar=(n,)):
                        out.append({"L": d, "n": n, "arista": (a, b), "p": p}); break
        return out

    def _sube(self, N, a, b):
        """Penalidad de que el agua corra de a hacia b subiendo de plataforma (borde mas alto en b): el agua va de la plataforma
        alta a la baja; subir solo queda si no hay otro camino (y se avisa en las estructuras)."""
        if not getattr(self.S, "por_sector", False): return 0.0
        cache = self.__dict__.setdefault("_ras_cache", {})
        def ras(n):
            k = (round(N[n][0], 2), round(N[n][1], 2))
            if k not in cache: cache[k] = self.S.rasante(*N[n])
            return cache[k]
        d = ras(b) - ras(a) - self.P["caida_continua_max"]
        return self.P.get("penal_subida", 200.0) * d if d > 0 else 0.0

    def _borde_alto(self, pu, pv, L):
        """Posicion (desde pu) del cambio brusco de nivel de piso mas alto a lo largo de una arista, o None."""
        if not getattr(self.S, "por_sector", False) or L < 1.0: return None
        n = int(L / 0.5); zs = [self.S.rasante(pu[0] + (pv[0] - pu[0]) * k / n, pu[1] + (pv[1] - pu[1]) * k / n) for k in range(n + 1)]
        saltos = [(abs(zs[k + 1] - zs[k]), k) for k in range(n) if abs(zs[k + 1] - zs[k]) > self.P["caida_continua_max"]]
        if not saltos: return None
        k = max(saltos)[1]
        t = (k + (1 if zs[k + 1] > zs[k] else 0)) * L / n          # en el lado alto, justo en el borde
        return min(max(t, 0.10), L - 0.10)

    def resolver(self, recorte=None):
        """Descargas y uniones. Cada descarga posible q del cerco admite un largo maximo de red Lcap(q): con el interior
        nivelado la cota de fondo baja S0 por metro desde h0, y en q debe quedar sobre el terreno exterior (cuneta nunca
        enterrada) y bajo la profundidad objetivo. Se eligen las menos descargas que cubren todas las lineas del usuario
        (cobertura voraz) y luego el arbol de caminos mas cortos define las uniones y el sentido de flujo."""
        P = self.P; recorte = recorte or {}
        comp = self.componentes()
        uniones = self._candidatos_union(comp)
        cand = self.candidatos_descarga()
        if self.descargas_fijas:
            fijos = []
            for k, d in enumerate(self.descargas_fijas):
                c = min(cand, key=lambda c: math.dist(c["q"], (d["x"], d["y"]))) if cand else None
                if c is None or math.dist(c["q"], (d["x"], d["y"])) > 3.0:
                    self.avisos.append("La descarga %s indicada no esta sobre el cerco o fuera del terreno con curvas." % d.get("nombre", k + 1))
                    continue
                c = dict(c); c["nombre"] = d.get("nombre"); c["fija"] = True; fijos.append(c)
            cand = fijos
        else:
            cand = [c for i, c in enumerate(cand) if c["holgura"] > 0 and i % 2 == 0]       # cada 2 m de cerco
        self.candidatos = cand
        Lprof = ((P.get("prof_max_sin_gravedad", P["prof_max_objetivo"]) if P.get("descarga_alternativa") else P["prof_max_objetivo"]) - P["h0"]) / P["S0"]
        N = dict(self.N); ar = []              # aristas: (x, y, costo, largo, tipo)
        # 1) lineas del usuario, partidas donde llega una union
        cortes = defaultdict(list)
        for iu, u in enumerate(uniones):
            a, b = u["arista"]
            if math.dist(u["p"], N[a]) < 0.3: u["m"] = a
            elif math.dist(u["p"], N[b]) < 0.3: u["m"] = b
            else:
                # dos uniones que llegan a menos de 0.30 m en la misma cuneta comparten el nudo (sin tramos de centimetros)
                junto = next((m for m in cortes[(a, b)] if math.dist(N[m], u["p"]) < 0.3), None)
                if junto: u["m"] = junto; continue
                u["m"] = "t%d" % iu; N[u["m"]] = u["p"]; cortes[(a, b)].append(u["m"])
        usuario = []
        for e in self.E:
            a, b = e["u"], e["v"]
            cad = [a] + sorted(cortes.get((a, b), []), key=lambda m: math.dist(N[a], N[m])) + [b]
            for x, y in zip(cad[:-1], cad[1:]):
                L = math.dist(N[x], N[y]); usuario.append((x, y, L)); ar.append((x, y, L, L, "usuario"))
        # 2) uniones rectas entre lineas que no se tocan
        for u in uniones: ar.append((u["n"], u["m"], 3.0 + 1.5 * u["L"], u["L"], "union"))
        # 3) camino perimetral: cuneta a d_cerco del cerco, por donde van las uniones hasta las descargas (sin diagonales
        #    largas cruzando patios). Estaciones: vertices del anillo, pies de los nudos y puntos de descarga.
        off = self.S.cerco.buffer(-P["d_cerco"], join_style=2)
        off = max(off.geoms, key=lambda g: g.area) if hasattr(off, "geoms") else off
        anillo = off.exterior; La = anillo.length
        est = {}                                   # posicion en el anillo -> nudo
        def estacion(s, nombre=None):
            s = s % La
            for s0, n0 in est.items():
                if min(abs(s0 - s), La - abs(s0 - s)) < 0.05: return n0
            n = nombre or "r%d" % len(est); p = anillo.interpolate(s); N[n] = (p.x, p.y); est[s] = n; return n
        for x, y in list(anillo.coords)[:-1]: estacion(anillo.project(Point(x, y)))
        lineas_u = [LineString([N[x], N[y]]) for x, y, L in usuario]
        arbol_u = STRtree(lineas_u) if lineas_u else None
        for n in self.N:
            p = Point(self.N[n]); s = anillo.project(p); f = anillo.interpolate(s); d = p.distance(f)
            if d > P["union_max"]: continue
            if d < 0.05: est_n = estacion(s); ar.append((n, est_n, 0.0, 0.0, "union")); continue
            # extremo de una linea que llega al cerco (entre el camino perimetral y el cerco): ya esta sobre el camino; se une
            # directo aunque la union quede sobre su propia linea
            if d <= P["d_cerco"] + 0.15 and not self.S.cerco.buffer(-0.05).exterior.distance(p) > P["d_cerco"] + 0.05:
                ar.append((n, estacion(s), 0.5 * d, d, "union")); continue
            if self._valida(self.N[n], (f.x, f.y), ignorar=(n,)):
                ar.append((n, estacion(s), 3.0 + 1.5 * d, d, "union"))
        for k, c in enumerate(cand):
            s = anillo.project(Point(c["b"])); bk = estacion(s, "b%d" % k)
            if bk != "b%d" % k: N["b%d" % k] = N[bk]; ar.append(("b%d" % k, bk, 0.0, 0.0, "union"))
            N["q%d" % k] = c["q"]; ar.append(("b%d" % k, "q%d" % k, 0.0, P["d_cerco"], "pase"))
            # extremo de una linea del usuario junto al punto de descarga: se une directo (el filtro de "ya hay cuneta" del
            # camino perimetral descartaria ese tramito y la descarga quedaria aislada)
            for n in self.N:
                dn = math.dist(self.N[n], N["b%d" % k])
                if 0.05 <= dn <= 1.0: ar.append(("b%d" % k, n, 0.5 * dn, dn, "union"))
        orden = sorted(est.items())
        for (s1, n1), (s2, n2) in zip(orden, orden[1:] + [(orden[0][0] + La, orden[0][1])]):
            seg = LineString([N[n1], N[n2]]); L = seg.length
            if L < 0.01: ar.append((n1, n2, 0.0, 0.0, "union")); continue
            if not self.obst.is_empty and seg.intersection(self.obst).length > 0.05: continue
            if arbol_u is not None:
                cerca = [lineas_u[int(i)] for i in arbol_u.query(seg.buffer(0.45))]
                # ya hay cuneta a lo largo del camino (solo cuentan las paralelas; una cuneta que lo cruza no lo reemplaza)
                par = [l for l in cerca if _paralelas(seg, l)]
                if par and seg.intersection(unary_union([l.buffer(0.45) for l in par])).length > 0.2 * L: continue
                # cruza una cuneta lejos de sus extremos (en el extremo, la estacion es justamente ese cruce)
                if any(seg.crosses(l) and min(Point(seg.coords[0]).distance(l), Point(seg.coords[-1]).distance(l)) > 0.05 for l in cerca): continue
            ar.append((n1, n2, 1.5 * L, L, "union"))
        # dos tramos nuevos posibles que se cruzan (sin compartir extremo): se queda el mas corto
        nuevos = sorted([ie for ie, a in enumerate(ar) if a[4] == "union" and a[3] > 0.05], key=lambda ie: ar[ie][3])
        geo_n = {ie: LineString([N[ar[ie][0]], N[ar[ie][1]]]) for ie in nuevos}
        fuera = set(); puestos = []
        for ie in nuevos:
            g = geo_n[ie]; x, y = ar[ie][0], ar[ie][1]
            choca = False
            for je in puestos:
                x2, y2 = ar[je][0], ar[je][1]
                if {x, y} & {x2, y2}: continue
                if g.crosses(geo_n[je]): choca = True; break
            if choca: fuera.add(ie)
            else: puestos.append(ie)
        ar = [a if ie not in fuera else (a[0], a[1], math.inf, a[3], "descartada") for ie, a in enumerate(ar)]
        ady = defaultdict(list)
        for ie, (x, y, c, L, t) in enumerate(ar):
            if t == "descartada": continue
            ady[x].append((y, c, L, ie)); ady[y].append((x, c, L, ie))

        def es_desc(n): return n[0] in "bq" and n[1:].isdigit()
        sube = {}                                  # penalidad acumulada por subir de plataforma en el camino a la descarga

        def dijkstra(fuentes):
            permit = {"q%d" % k for k in fuentes} | {"b%d" % k for k in fuentes}
            dist, fis, pred = {}, {}, {}
            sube.clear()
            pq = []
            for k in fuentes:
                q = "q%d" % k; dist[q] = 0.0; fis[q] = 0.0; heapq.heappush(pq, (0.0, q))
            while pq:
                dd, x = heapq.heappop(pq)
                if dd > dist[x] + 1e-12: continue
                for y, c, L, ie in ady[x]:
                    if es_desc(y) and y not in permit: continue
                    ps = self._sube(N, y, x)                      # el agua iria de y hacia x
                    if dd + c + ps < dist.get(y, math.inf) - 1e-9:
                        dist[y] = dd + c + ps; fis[y] = fis[x] + L; pred[y] = (x, ie); sube[y] = sube.get(x, 0.0) + ps
                        heapq.heappush(pq, (dist[y], y))
            return dist, fis, pred

        def cap(k):
            return min(cand[k]["holgura"] / P["S0"], Lprof) - recorte.get(k, 0.0)

        cubre = {}
        for k in range(len(cand)):
            dist, fis, pred = dijkstra([k]); Lc = cap(k)
            # una linea que solo llega a esta descarga subiendo de plataforma no queda cubierta por ella: se busca otra descarga
            cubre[k] = {i for i, (x, y, L) in enumerate(usuario) if x in fis and y in fis and (fis[x] + fis[y] + L) / 2 <= Lc
                        and max(sube.get(x, 0.0), sube.get(y, 0.0)) <= 0.0}
        falta = set(range(len(usuario))); elegidas = []
        Lc_cerco = self.S.cerco.exterior.length
        if self.descargas_fijas:
            elegidas = list(range(len(cand)))
            for k in elegidas: falta -= cubre[k]
        else:
            while falta:
                mejor = None
                for k, cs in cubre.items():
                    if any(min(abs(cand[k]["s"] - cand[j]["s"]), Lc_cerco - abs(cand[k]["s"] - cand[j]["s"])) < P["desc_sep_min"] for j in elegidas):
                        continue
                    nuevo = sum(usuario[i][2] for i in cs & falta)
                    if nuevo <= 0: continue
                    clave = (round(nuevo, 0), -cand[k]["z_req"])
                    if mejor is None or clave > mejor[0]: mejor = (clave, k)
                if mejor is None: break
                elegidas.append(mejor[1]); falta -= cubre[mejor[1]]
        if falta:
            self.avisos.append("NO HAY SALIDA POR GRAVEDAD para %.1f m de cuneta (quedaria enterrada): ninguna descarga del cerco la "
                               "recibe con el terreno exterior bajo su cota de fondo. Opciones: indicar otra descarga, partir el "
                               "sistema o subir el nivel de esa zona." % sum(usuario[i][2] for i in falta))
        self.sin_cubrir = [(N[usuario[i][0]], N[usuario[i][1]]) for i in falta]
        dist, fis, pred = dijkstra(elegidas)
        usadas = set()
        for n in {x for x, y, L in usuario} | {y for x, y, L in usuario}:
            while n in pred:
                x, ie = pred[n]
                if ie in usadas: break
                usadas.add(ie); n = x
        # grafo final: todas las lineas del usuario (partidas solo donde llega una union usada) y lo usado de lo demas
        usados_n = set()
        for ie in usadas:
            x, y, c, L, t = ar[ie]
            if t != "usuario": usados_n.update((x, y))
        Ef = []
        for e in self.E:
            a, b = e["u"], e["v"]
            ms = [m for m in cortes.get((a, b), []) if m in usados_n]
            cad = [a] + sorted(ms, key=lambda m: math.dist(N[a], N[m])) + [b]
            for x, y in zip(cad[:-1], cad[1:]): Ef.append({"u": x, "v": y, "origen": e["origen"]})
        ren = {}
        self.descargas = {}
        for cont, k in enumerate(sorted(elegidas, key=lambda k: cand[k]["s"])):
            c = cand[k]; dd = c.get("nombre") or "D%d" % (cont + 1)
            ren["q%d" % k], ren["b%d" % k] = dd, dd + "n"
            self.descargas[dd] = {"nombre": dd, "q": c["q"], "b": N["b%d" % k], "z_req": c["z_req"], "nin": c["nin"], "s": c["s"],
                                  "k": k, "L_max": round(cap(k), 1)}
        for ie in usadas:
            x, y, c, L, t = ar[ie]
            if t == "usuario": continue
            Ef.append({"u": ren.get(x, x), "v": ren.get(y, y), "origen": t, "L0": L})
        Nf = {ren.get(k, k): v for k, v in N.items()}
        # nudos a menos de 5 cm se funden (se conserva el del usuario o la descarga)
        def prioridad(n):
            if n in self.descargas or (n.endswith("n") and n[:-1] in self.descargas): return 0
            if n in self.N: return 1
            return 2
        nodos = sorted({e["u"] for e in Ef} | {e["v"] for e in Ef}, key=prioridad)
        alias = {}
        for i, a in enumerate(nodos):
            if a in alias: continue
            for b in nodos[i + 1:]:
                if b not in alias and math.dist(Nf[a], Nf[b]) < 0.05: alias[b] = a
        E2, vistos = [], set()
        for e in Ef:
            a, b = alias.get(e["u"], e["u"]), alias.get(e["v"], e["v"])
            if a == b or (min(a, b), max(a, b)) in vistos: continue
            vistos.add((min(a, b), max(a, b))); E2.append({"u": a, "v": b, "origen": e["origen"]})
        E2 = self._simplificar(E2, Nf)
        usados = {e["u"] for e in E2} | {e["v"] for e in E2}
        self.Nf = {k: v for k, v in Nf.items() if k in usados}
        self.Ef = E2
        self._flujo()
        return self

    def _simplificar(self, E, N):
        """Une tramos nuevos seguidos y alineados (estaciones intermedias del camino perimetral)."""
        while True:
            grado = defaultdict(list)
            for i, e in enumerate(E): grado[e["u"]].append(i); grado[e["v"]].append(i)
            hecho = False
            for n, ies in grado.items():
                if len(ies) != 2 or n in self.N or n in self.descargas or (n.endswith("n") and n[:-1] in self.descargas): continue
                e1, e2 = E[ies[0]], E[ies[1]]
                if e1["origen"] != "union" or e2["origen"] != "union": continue
                a = e1["v"] if e1["u"] == n else e1["u"]; b = e2["v"] if e2["u"] == n else e2["u"]
                if geom.giro(N[a], N[n], N[b]) > 1.0: continue
                E = [e for k, e in enumerate(E) if k not in ies] + [{"u": a, "v": b, "origen": "union"}]
                hecho = True; break
            if not hecho: return E

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
                c = L + self._sube(N, m, n)                       # el agua iria de m hacia n
                if dd + c < dist[m] - 1e-9:
                    dist[m] = dd + c; sis[m] = sis[n]; heapq.heappush(pq, (dist[m], m))
        # cada arista se orienta hacia el extremo mas cercano a la descarga; la que no esta en el camino mas corto se divide
        dirigidas = []
        for e in E:
            u, v, L = e["u"], e["v"], e["L"]
            if not (math.isfinite(dist[u]) and math.isfinite(dist[v])): continue
            if abs(dist[u] + L + self._sube(N, v, u) - dist[v]) < 1e-6: dirigidas.append((v, u, e["origen"]))
            elif abs(dist[v] + L + self._sube(N, u, v) - dist[u]) < 1e-6: dirigidas.append((u, v, e["origen"]))
            else:
                t = (dist[v] - dist[u] + L) / 2.0                     # punto alto: igual distancia a la descarga por ambos lados
                tb = self._borde_alto(N[u], N[v], L)
                if tb is not None: t = tb                              # con plataformas el agua se divide en el borde de la plataforma
                if t < 0.10: dirigidas.append((u, v, e["origen"])); continue       # el punto alto cae en u: todo va a v
                if t > L - 0.10: dirigidas.append((v, u, e["origen"])); continue
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
                if (y, x) in usadas or y in vis: continue
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
                        ent = [y for y in arriba[n] if (y, n) not in usadas]
                        if not ent: break
                        mejor = None
                        for y in ent:
                            Ly, cy = mas_largo(y, {y, n}) if y not in asignados else (0.0, [y])
                            Ly += math.dist(N[y], N[n])
                            if mejor is None or Ly > mejor[0]: mejor = (Ly, cy + [n])
                        cola.append(agregar(mejor[1], d))
        self.origen_arista = origen
        self.ramales = ramales

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
                if ch < 0.10: continue
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
        # chaflanes de dos esquinas seguidas que se encuentran en el mismo punto: un solo nudo
        alias = {}
        for nn in nuevos:
            for a, b in zip(nn[:-1], nn[1:]):
                if a != b and math.dist(N[a], N[b]) < 0.05 and b not in alias: alias[b] = alias.get(a, a)
        for r, nn in zip(self.ramales, nuevos):
            limpio = []
            for n in nn:
                n = alias.get(n, n)
                if not limpio or limpio[-1] != n: limpio.append(n)
            r["nudos"] = limpio
        self.chaflanes_hechos = hechas
        return hechas

    def nombrar(self):
        """EJE-01, EJE-02 ... y nudos P-01, P-02 ... en el orden de los ejes; descargas D1, D2 ..."""
        # nudos seguidos a menos de 2 cm en un mismo eje (estacion del camino perimetral sobre un nudo del usuario): se deja uno
        for r in self.ramales:
            nu = [r["nudos"][0]]
            for n in r["nudos"][1:]:
                if math.dist(self.Nf[nu[-1]], self.Nf[n]) < 0.02 and n not in self.descargas and n != r["nudos"][-1]: continue
                if math.dist(self.Nf[nu[-1]], self.Nf[n]) < 0.02 and len(nu) > 1: nu[-1] = n; continue
                nu.append(n)
            r["nudos"] = nu
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
