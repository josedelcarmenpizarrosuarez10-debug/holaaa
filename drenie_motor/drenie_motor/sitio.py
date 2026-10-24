"""Sitio: cerco perimetrico (limite de intervencion), techos, veredas, zonas de nivel y superficies para el coeficiente C.

Regla fija del usuario: el cerco es el limite; ninguna cuneta ni obra sale del cerco, solo el agua, por un pase en el cimiento.
"""
import shapely
from shapely.geometry import Polygon, Point
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
        techos = [p.intersection(self.cerco) for p in geom.poligonos(geom.seleccionar(B, cfg["techos"]))] if cfg.get("techos") else []
        self.techos_plano = geom.union(techos)
        self.techos = geom.union(techos + [e["geom"] for e in self.extra if e["tipo"] == "techo"])
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
        """Borde superior de la cuneta (nivel del piso terminado junto a ella)."""
        for pol, nivel, nombre, sup in self.zonas:
            if pol.contains(Point(x, y)): return nivel
        if self.modo == "nivelado" and self.dentro(x, y): return self.borde
        return self.T.z(x, y)

    def tapado(self, x, y):
        """Tramo tapado donde la cuneta cruza una vereda del plano (las superficies agregadas no tapan la cuneta)."""
        return (not self.veredas_plano.is_empty) and self.veredas_plano.contains(Point(x, y))

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
