"""Sitio: cerco perimetrico (limite de intervencion), techos, veredas, zonas de nivel y superficies para el coeficiente C.

Regla fija del usuario: el cerco es el limite; ninguna cuneta ni obra sale del cerco, solo el agua, por un pase en el cimiento.
"""
import math

import shapely
from shapely.geometry import LineString, Polygon, Point
from shapely.prepared import prep

from . import geom


class Sitio:
    def __init__(self, B, cfg, terreno, P):
        self.cfg, self.T, self.P = cfg, terreno, P
        self.avisos = []
        self.cerco = self._cerco(B, cfg["cerco"])
        if not self.cerco.exterior.is_ccw: self.cerco = Polygon(list(self.cerco.exterior.coords)[::-1])
        self.cerco_p = prep(self.cerco)
        self.interior = self.cerco.buffer(-P["d_cerco"] + 0.30)         # bordes de cuneta (eje +- 0.30) dentro del cerco
        # superficies con nombre (losas deportivas, patios techados, estacionamientos...): capa o poligono, con su tipo
        self.extra = []
        for k, s in enumerate(cfg.get("superficies") or []):
            pols = [Polygon(s["poligono"]).buffer(0)] if "poligono" in s else geom.poligonos(geom.seleccionar(B, s["capa"]), area_min=1.0)
            g = geom.union(pols).intersection(self.cerco)
            if g.is_empty:
                self.avisos.append("La superficie '%s' no se encontro dentro del cerco." % s.get("nombre", k + 1)); continue
            self.extra.append({"nombre": s.get("nombre", "Superficie %d" % (k + 1)), "tipo": s.get("tipo", "pavimento"), "geom": g,
                               "obstaculo": s.get("obstaculo", s.get("tipo") == "techo")})
        sel_t = cfg.get("techos") or []
        sel_t = sel_t if isinstance(sel_t, list) else [sel_t]
        sep = [x for x in sel_t if isinstance(x, dict) and x.get("separados")]
        otros = [x for x in sel_t if x not in sep]
        techos = [p.intersection(self.cerco) for p in geom.poligonos_tolerantes(geom.seleccionar(B, otros))] if otros else []
        # "separados": cada contorno cerrado es un techo aunque toque al vecino (CAR Varones: la losa deportiva y la edificacion 03
        # se tocan); los contornos repetidos o dentro de otro se descartan y la parte comun queda en el techo mas grande
        indiv = []
        for p in sorted((Polygon(pts).buffer(0).intersection(self.cerco) for pts, cl, col, z in geom.seleccionar(B, sep) if cl and len(pts) >= 3),
                        key=lambda q: -q.area):
            if p.area < 4.0 or any(p.intersection(q).area > 0.8 * p.area for q in indiv): continue
            indiv.append(p)
        indiv = [p.difference(geom.union(indiv[:k])) if k else p for k, p in enumerate(indiv)]
        indiv = [max(p.geoms, key=lambda q: q.area) if hasattr(p, "geoms") else p for p in indiv if p.area >= 4.0]
        self.techos_plano = geom.union(techos + indiv)
        resto = geom.union(techos + [e["geom"] for e in self.extra if e["tipo"] == "techo"])
        if indiv: resto = resto.difference(geom.union(indiv))
        self.techos_lista = indiv + [q for q in (resto.geoms if hasattr(resto, "geoms") else [resto]) if q.area > 4.0] if indiv else None
        self.techos = geom.union(techos + indiv + [e["geom"] for e in self.extra if e["tipo"] == "techo"])
        self.veredas_plano = geom.union([p for p in geom.poligonos(geom.seleccionar(B, cfg["veredas"]))]) if cfg.get("veredas") else Polygon()
        self.veredas = geom.union([self.veredas_plano] + [e["geom"] for e in self.extra if e["tipo"] == "pavimento"])
        self.muros = geom.union([p for p in geom.poligonos(geom.seleccionar(B, cfg["muros"]))]) if cfg.get("muros") else Polygon()
        self.no_cruzar = geom.union([e["geom"] for e in self.extra if e["obstaculo"]])
        self.obstaculos = geom.union([g for g in (self.techos, self.muros) if not g.is_empty])
        niv = cfg.get("niveles", {})
        self.modo = niv.get("modo", "nivelado")
        self.npt = niv.get("npt")
        self.borde = niv.get("borde_cuneta", self.npt)
        self.area_verde = niv.get("area_verde")
        self.zonas = [(Polygon(z["poligono"]), z["nivel"], z.get("nombre", ""), z.get("superficie")) for z in niv.get("zonas", [])]
        if self.modo == "nivelado" and self.borde is None:
            raise ValueError("Falta el nivel del borde de cuneta (niveles.borde_cuneta o niveles.npt)")
        self._niveles_por_sector(niv)

    def _niveles_por_sector(self, niv):
        """Plataformas (cada una con su NPT y el rebaje del borde de cuneta), rampas (borde que sigue la pendiente de la rampa),
        escaleras (la cuneta nunca pasa por ellas) y borde por eje (NPT del eje y rebaje: al ras, -0.05, -0.10...)."""
        def pol(x):
            g = Polygon(x["poligono"]).buffer(0)
            if g.is_empty or g.area < 0.5: raise ValueError("El poligono de '%s' no es valido." % x.get("nombre", "nivel"))
            return g
        self.plataformas = []
        for i, x in enumerate(niv.get("plataformas", [])):
            npt = float(x["npt"]); reb = float(x.get("rebaje", 0.0) or 0.0)
            self.plataformas.append({"nombre": x.get("nombre") or "Plataforma %d" % (i + 1), "geom": pol(x), "npt": npt, "rebaje": reb,
                                     "borde": round(npt - reb, 3)})
        self.plataformas.sort(key=lambda q: q["geom"].area)            # la mas chica manda si una esta dentro de otra
        self.rampas = []
        for i, x in enumerate(niv.get("rampas", [])):
            a, b = x["inicio"], x["fin"]
            if math.dist(a, b) < 0.5: raise ValueError("La rampa '%s' necesita un inicio y un fin separados." % x.get("nombre", ""))
            self.rampas.append({"nombre": x.get("nombre") or "Rampa %d" % (i + 1), "geom": pol(x), "a": tuple(a), "b": tuple(b),
                                "za": float(x["npt_inicio"]) - float(x.get("rebaje", 0.0) or 0.0),
                                "zb": float(x["npt_fin"]) - float(x.get("rebaje", 0.0) or 0.0)})
        self.escaleras = [{"nombre": x.get("nombre") or "Escalera %d" % (i + 1), "geom": pol(x)} for i, x in enumerate(niv.get("escaleras", []))]
        if self.escaleras:
            self.no_cruzar = geom.union([g for g in [self.no_cruzar] + [e["geom"] for e in self.escaleras] if not g.is_empty])
        self.bordes_eje = []
        for x in niv.get("bordes_eje", []):
            ln = LineString(x["linea"])
            if ln.length < 0.3: continue
            self.bordes_eje.append({"geom": ln.buffer(0.35, cap_style=2), "npt": x.get("npt"), "rebaje": float(x.get("rebaje", 0.0) or 0.0)})
        self.por_sector = bool(self.plataformas or self.rampas or self.bordes_eje)

    def _rasante_base(self, x, y):
        pt = Point(x, y)
        for r in self.rampas:
            if r["geom"].contains(pt):
                ax, ay = r["a"]; bx, by = r["b"]; L2 = (bx - ax) ** 2 + (by - ay) ** 2
                t = min(1.0, max(0.0, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / L2))
                return r["za"] + t * (r["zb"] - r["za"])
        for q in self.plataformas:
            if q["geom"].contains(pt): return q["borde"]
        return None

    def nivel_en(self, x, y):
        """Nombre del sector de nivel en un punto (plataforma, rampa o nivel general), para los cuadros y los avisos."""
        pt = Point(x, y)
        for r in self.rampas:
            if r["geom"].contains(pt): return r["nombre"]
        for q in self.plataformas:
            if q["geom"].contains(pt): return q["nombre"]
        return "Nivel general"

    def _cerco(self, B, c):
        if isinstance(c, dict) and "poligono" in c:
            return Polygon(c["poligono"]).buffer(0)
        pols = geom.poligonos(geom.seleccionar(B, c), area_min=10.0)
        if not pols: raise ValueError("No se encontro el cerco perimetrico en la capa indicada")
        pol = max(pols, key=lambda p: p.area)
        if len(pols) > 1:
            self.avisos.append("El cerco se tomo como el mayor de %d poligonos de la capa (%.0f m2); confirmar." % (len(pols), pol.area))
        return pol

    def revisar_superficies(self, lineas):
        """Aviso si un poligono de superficie (losa, patio...) se monta sobre una linea de cuneta del usuario."""
        from shapely.geometry import LineString
        for e in self.extra:
            for k, pts in enumerate(lineas):
                L = LineString(pts).intersection(e["geom"]).length
                if L > 0.5:
                    self.avisos.append("La superficie '%s' se monta %.1f m sobre la linea de cuneta N.%d del usuario: ajustar su borde "
                                       "a la cara exterior de la cuneta." % (e["nombre"], L, k + 1))

    def dentro(self, x, y):
        return self.cerco_p.contains(Point(x, y))

    def rasante(self, x, y):
        """Borde superior de la cuneta (nivel del piso terminado junto a ella; por plataforma, rampa o eje si se definieron)."""
        if self.por_sector:
            pt = Point(x, y)
            for b in self.bordes_eje:
                if b["geom"].contains(pt):
                    base = b["npt"] if b["npt"] is not None else self._rasante_base(x, y)
                    if base is None: base = self._rasante_zonas(x, y)
                    return float(base) - b["rebaje"]
            z = self._rasante_base(x, y)
            if z is not None: return z
        return self._rasante_zonas(x, y)

    def _rasante_zonas(self, x, y):
        for pol, nivel, nombre, sup in self.zonas:
            if pol.contains(Point(x, y)): return nivel
        if self.modo == "nivelado" and self.dentro(x, y): return self.borde
        return self.T.z(x, y)

    def tapado(self, x, y):
        """0 = rejilla; 1 = tapada donde la cuneta cruza una vereda del plano (las superficies agregadas no tapan la cuneta);
        2 = tapa vehicular: en estacionamientos nunca hay rejilla, siempre cuneta tapada para el paso de camiones."""
        est = self._estacionamiento()
        if est is not None and est.contains(Point(x, y)): return 2
        return 1 if (not self.veredas_plano.is_empty) and self.veredas_plano.contains(Point(x, y)) else 0

    def _estacionamiento(self):
        clave = id(getattr(self, "mapa", None))
        if getattr(self, "_est_clave", None) != clave:
            g = self.superficies().get("estacionamiento")
            self._est_prep = prep(g.buffer(0.30)) if g is not None and not g.is_empty else None   # la cuneta va al borde
            self._est_clave = clave
        return self._est_prep

    def superficies(self):
        """Poligonos por tipo dentro del cerco, para el C ponderado (el resto es area verde)."""
        if getattr(self, "mapa", None) is not None:
            pt = self.mapa.por_tipo(); return {k: pt[k] for k in pt if k != "sin_asignar"}
        if getattr(self, "_sup", None): return self._sup
        dentro = self.cerco
        techo = self.techos.intersection(dentro) if not self.techos.is_empty else Polygon()
        est = geom.union([p for p, n, nom, s in self.zonas if s == "estacionamiento"] +
                         [e["geom"] for e in self.extra if e["tipo"] == "estacionamiento"]).intersection(dentro).difference(techo)
        pav = self.veredas.intersection(dentro).difference(techo).difference(est) if not self.veredas.is_empty else Polygon()
        verde = dentro.difference(techo).difference(est).difference(pav)
        self._sup = {k: Polygon() for k in self.P["C"]}
        self._sup.update({"techo": techo, "estacionamiento": est, "pavimento": pav, "verde": verde})
        return self._sup

    def cuadro_superficies(self):
        """Cuadro de superficies para mostrar y confirmar: por tipo y por superficie con nombre."""
        sup = self.superficies()
        filas = [{"tipo": k, "area_m2": round(g.area, 1), "C": self.P["C"][k]} for k, g in sup.items()]
        nombradas = [{"nombre": "Techos de la capa de techos", "tipo": "techo", "area_m2": round(self.techos_plano.area, 1)}]
        nombradas += [{"nombre": e["nombre"], "tipo": e["tipo"], "area_m2": round(e["geom"].area, 1)} for e in self.extra]
        nombradas += [{"nombre": n, "tipo": s or "nivel", "area_m2": round(p.intersection(self.cerco).area, 1)} for p, nv, n, s in self.zonas]
        At = sum(f["area_m2"] for f in filas)
        return {"por_tipo": filas, "superficies": nombradas, "area_total_m2": round(At, 1),
                "C_ponderado": round(sum(f["area_m2"] * f["C"] for f in filas) / At, 3) if At else None}

    def c_celdas(self, X, Y):
        """C de cada celda (puntos X, Y) segun su superficie; el resto es area verde."""
        import numpy as np
        C = np.full(len(X), self.P["C"]["verde"]); tipo = np.array(["verde"] * len(X), dtype=object)
        sup = self.superficies()
        for k in sorted((k for k in sup if k != "verde"), key=lambda k: -{"techo": 0, "estacionamiento": 1}.get(k, 5)):
            pol = sup[k]
            if pol.is_empty: continue
            m = shapely.contains_xy(pol, X, Y); C[m] = self.P["C"][k]; tipo[m] = k
        return C, tipo
