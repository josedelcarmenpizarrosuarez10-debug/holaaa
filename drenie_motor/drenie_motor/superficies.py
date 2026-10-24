"""Mapa de superficies: todo el interior del cerco partido en areas que encajan (sin montajes ni huecos), cada una con su
tipo (techo, pavimento, estacionamiento, area verde, cuneta), su coeficiente C y su nivel.

1. Caras: se juntan todas las lineas que delimitan algo (cerco, techos, veredas, sombreados, superficies con nombre, zonas) y
   se parte el cerco en caras cerradas, como el comando CONTORNO de AutoCAD. Lo que no quede cerrado por ninguna linea es
   otra cara (el resto). La suma de las caras es el area del cerco: por construccion no hay montajes ni huecos.
2. Imán: los vertices a menos de 5 cm de otra linea se pegan antes de partir.
3. Cunetas: cada cuneta ocupa su franja real (0.60 m); las superficies de piso se recortan en la cara exterior de la cuneta.
   Bajo los techos manda el techo (la lluvia cae sobre el techo).
4. Astillas: caras de menos de 0.10 m2 o de menos de 5 cm de ancho se suman a la cara vecina con mas borde comun.
   Franjas: caras sin tipo de menos de 0.35 m de ancho o de menos de 1 m2 (sardineles, juntas, el espacio entre el borde de un
   sombreado y la linea del plano) toman el tipo de la vecina con mas borde comun; quedan como area aparte (se pueden cambiar).
5. Tipo de cada cara, en este orden: asignacion manual (clic en el visor) > leyenda de colores (sombreados) > superficie con
   nombre > capa de techos > zona de estacionamiento > capa de veredas > rotulo de texto > valor por defecto del proyecto.
   Sin tipo: "sin_asignar" (el diseno no corre hasta asignarlo, salvo que el proyecto fije un valor por defecto).
"""
import math
import re
import unicodedata

import shapely
from shapely.geometry import LineString, Point, Polygon, MultiPolygon
from shapely.ops import polygonize, unary_union

from . import geom

TIPOS = ("techo", "vereda", "patio", "pavimento", "estacionamiento", "juegos", "cuneta", "verde")
PRIORIDAD = {"techo": 0, "estacionamiento": 1, "vereda": 2, "patio": 3, "pavimento": 4, "juegos": 5, "cuneta": 6, "verde": 7}
NOMBRE_TIPO = {"techo": "Techos", "vereda": "Veredas y circulaciones", "patio": "Patios libres pavimentados",
               "pavimento": "Otros pisos de concreto", "estacionamiento": "Estacionamiento y patio de maniobra",
               "juegos": "Area de juegos (piso de caucho)", "cuneta": "Cunetas (franja de 0.60 m)", "verde": "Area verde"}
ROTULOS = {"AREA VERDE": "verde", "AREAS VERDES": "verde", "JARDIN": "verde", "JARDINERA": "verde", "GRASS": "verde",
           "VEREDA": "vereda", "PATIO": "patio", "CIRCULACION": "vereda", "LOSA": "patio", "ATRIO": "patio", "JUEGO": "juegos",
           "ESTACIONAMIENTO": "estacionamiento", "PATIO DE MANIOBRA": "estacionamiento", "TECHO": "techo", "COBERTURA": "techo",
           "EDIFICACION": "techo"}


def _norm(t):
    t = unicodedata.normalize("NFD", t.upper()); return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _ancho(p):
    return 2 * p.area / p.length if p.length else 0.0


class Mapa:
    def __init__(self, B, sitio, cfg, P, ejes_red):
        """ejes_red: lista de segmentos (a, b) de cuneta (lineas del usuario al leer; red final al disenar)."""
        self.S, self.P, self.cfg = sitio, P, cfg
        self.avisos, self.ajustes = [], []
        ce = sitio.cerco
        sup = cfg.get("superficies_cfg", {})
        # --- fuentes de clasificacion
        self.leyenda = []                               # sombreados / polilineas cerradas por color o capa
        for regla in sup.get("leyenda", []):
            pols = geom.poligonos([e for e in geom.seleccionar(B, regla["sel"]) if e[1]], area_min=0.05)
            if pols: self.leyenda.append((geom.union(pols), regla["tipo"], regla.get("nivel"), "leyenda %s" % regla["sel"]))
        self.nombradas = [(e["geom"], e["tipo"], None, e["nombre"]) for e in sitio.extra]
        self.manual = [(Point(a["x"], a["y"]), a["tipo"], a.get("nivel"), "asignacion manual") for a in sup.get("asignaciones", [])]
        # rotulos de ambientes: los del proyecto (p. ej. OE-04 = juegos) mandan sobre las capas y sombreados del plano;
        # los de fabrica (AREA VERDE, VEREDA...) solo se usan si nada mas identifica el area
        self.rotulos_pry, self.rotulos = [], []
        propios = {_norm(k): v for k, v in sup.get("rotulos", {}).items()}
        capas_rot = sup.get("rotulos_capas")
        for capa, s, x, y, h, col in B["txt"]:
            if capas_rot and capa not in capas_rot: continue
            if not ce.contains(Point(x, y)): continue
            n = _norm(s.strip().split("\n")[0])
            if n in propios: self.rotulos_pry.append((Point(x, y), propios[n], s.strip())); continue
            for clave, tipo in sorted(ROTULOS.items(), key=lambda e: -len(e[0])):
                if n.startswith(clave):
                    self.rotulos.append((Point(x, y), tipo, s.strip())); break
        self.por_defecto = sup.get("por_defecto")      # None: lo no identificado queda "sin_asignar"
        # --- lineas que delimitan
        lineas = [ce.exterior]
        for g in [sitio.techos_plano, sitio.veredas_plano, sitio.muros] + [g for g, t, n, o in self.leyenda] + \
                 [g for g, t, n, o in self.nombradas] + [p for p, n, nom, s in sitio.zonas]:
            if g is None or g.is_empty: continue
            for p in (g.geoms if hasattr(g, "geoms") else [g]):
                if isinstance(p, Polygon): lineas.append(p.exterior); lineas.extend(p.interiors)
        self.ambientes = []
        for sel in sup.get("lineas_extra", []):
            # {"sel": capa, "area_min": 20}: solo poligonos cerrados de al menos esa area (deja fuera recuadros de rotulos)
            amin = sel.get("area_min") if isinstance(sel, dict) and "sel" in sel else None
            ents = geom.seleccionar(B, sel["sel"] if amin is not None else sel)
            for e in ents:
                if amin is None: lineas.append(LineString(e[0]))
                elif e[1] and len(e[0]) >= 3 and Polygon(e[0]).buffer(0).area >= amin:
                    lineas.append(LineString(list(e[0]) + [e[0][0]]))
                    self.ambientes.append(Polygon(e[0]).buffer(0))
        todas = unary_union([LineString(l.coords) for l in lineas])
        todas = shapely.snap(todas, todas, 0.05)                 # iman de 5 cm
        caras = [c.intersection(ce) for c in polygonize(unary_union(todas))]
        caras = [c for c in caras if not c.is_empty and c.area > 1e-4]
        resto = ce.difference(unary_union(caras)) if caras else ce
        caras += [p for p in (resto.geoms if hasattr(resto, "geoms") else [resto]) if p.area > 1e-4]
        caras = [p for c in caras for p in (c.geoms if hasattr(c, "geoms") else [c]) if isinstance(p, Polygon)]
        # --- rotulos del proyecto: valen para todo el ambiente (el poligono mas chico que contiene el rotulo), no solo para el
        #     pedazo donde cae el texto (dentro de un ambiente hay juegos, bancas, veredas que lo parten)
        self.zonas_rot = []
        for p, tipo, txt in self.rotulos_pry:
            amb = [a for a in self.ambientes if a.contains(p)]
            if amb: self.zonas_rot.append((min(amb, key=lambda a: a.area), tipo, txt))
        # --- tipo de cada cara
        self.caras = [self._clasificar(c) for c in caras]
        # --- cunetas: franja real; recortan las superficies de piso (no los techos)
        self.franja = Polygon()
        if ejes_red:
            ancho = P["b_int"] / 2 + P["e_muro"]
            f = unary_union([LineString([a, b]).buffer(ancho, cap_style=2, join_style=2) for a, b in ejes_red if math.dist(a, b) > 0.01])
            self.franja = f.intersection(ce)
        if not self.franja.is_empty:
            nuevas = []
            for c in self.caras:
                if c["tipo"] == "techo" and c["fuente"] == "capa de techos":
                    nuevas.append(c); continue
                corte = c["geom"].intersection(self.franja).area
                if corte > 0.01:
                    resto = c["geom"].difference(self.franja)
                    if c["fuente"] not in ("resto", "por defecto", "sin tipo") and corte > 0.10:
                        self.ajustes.append({"superficie": c["nombre"], "tipo": c["tipo"], "recorte_m2": round(corte, 2),
                                             "motivo": "recortada en la cara exterior de la cuneta"})
                    for p in (resto.geoms if hasattr(resto, "geoms") else [resto]):
                        if isinstance(p, Polygon) and p.area > 1e-4: nuevas.append(dict(c, geom=p))
                else:
                    nuevas.append(c)
            techo_capa = geom.union([c["geom"] for c in self.caras if c["tipo"] == "techo" and c["fuente"] == "capa de techos"])
            cun = self.franja.difference(techo_capa) if not techo_capa.is_empty else self.franja
            for p in (cun.geoms if hasattr(cun, "geoms") else [cun]):
                if isinstance(p, Polygon) and p.area > 1e-4:
                    nuevas.append({"geom": p, "tipo": "cuneta", "nivel": None, "fuente": "red de cunetas", "nombre": "Cuneta"})
            self.caras = nuevas
        self._astillas()
        self._franjas(sup.get("franja_ancho", 0.35), sup.get("franja_area", 1.0))
        for k, c in enumerate(self.caras): c["id"] = k + 1
        self.cerrar()

    def _clasificar(self, cara):
        rp = cara.representative_point()
        def dentro(g): return not g.is_empty and g.contains(rp)
        for p, tipo, nivel, fuente in self.manual:
            if cara.contains(p): return {"geom": cara, "tipo": tipo, "nivel": nivel, "fuente": fuente, "nombre": "Asignada"}
        for zona, tipo, txt in self.zonas_rot:
            if zona.contains(rp): return {"geom": cara, "tipo": tipo, "nivel": None, "fuente": "rotulo del proyecto '%s'" % txt, "nombre": txt}
        for p, tipo, txt in self.rotulos_pry:
            if cara.contains(p): return {"geom": cara, "tipo": tipo, "nivel": None, "fuente": "rotulo del proyecto '%s'" % txt, "nombre": txt}
        cands = [(g, t, n, o) for g, t, n, o in self.leyenda if dentro(g)]
        if cands:
            g, t, n, o = min(cands, key=lambda e: PRIORIDAD.get(e[1], 9)); return {"geom": cara, "tipo": t, "nivel": n, "fuente": o, "nombre": t}
        for g, t, n, nom in self.nombradas:
            if dentro(g): return {"geom": cara, "tipo": t, "nivel": n, "fuente": "superficie con nombre", "nombre": nom}
        if dentro(self.S.techos_plano): return {"geom": cara, "tipo": "techo", "nivel": None, "fuente": "capa de techos", "nombre": "Techo"}
        for p, nivel, nom, s in self.S.zonas:
            if s and p.contains(rp): return {"geom": cara, "tipo": s, "nivel": nivel, "fuente": "zona", "nombre": nom}
        if dentro(self.S.veredas_plano): return {"geom": cara, "tipo": "pavimento", "nivel": None, "fuente": "capa de veredas", "nombre": "Vereda"}
        for p, tipo, txt in self.rotulos:
            if cara.contains(p): return {"geom": cara, "tipo": tipo, "nivel": None, "fuente": "rotulo '%s'" % txt, "nombre": txt}
        if self.por_defecto:
            return {"geom": cara, "tipo": self.por_defecto, "nivel": None, "fuente": "por defecto", "nombre": "Sin identificar (%s por defecto)" % self.por_defecto}
        return {"geom": cara, "tipo": "sin_asignar", "nivel": None, "fuente": "sin tipo", "nombre": "Sin asignar"}

    def _astillas(self):
        """Caras de menos de 0.10 m2 o de menos de 5 cm de ancho se suman a la vecina con mas borde comun."""
        for vuelta in range(3):
            chicas = [c for c in self.caras if c["geom"].area < 0.10 or _ancho(c["geom"]) < 0.05]
            if not chicas: return
            for c in chicas:
                if c not in self.caras: continue
                vec = [(c["geom"].boundary.intersection(o["geom"].boundary).length, o) for o in self.caras if o is not c]
                vec = [v for v in vec if v[0] > 1e-6]
                if not vec: continue
                L, o = max(vec, key=lambda v: v[0])
                o["geom"] = unary_union([o["geom"], c["geom"]])
                if hasattr(o["geom"], "geoms"): o["geom"] = max(o["geom"].geoms, key=lambda g: g.area)
                self.caras.remove(c)

    def _franjas(self, ancho_max, area_max):
        """Franjas angostas sin tipo: toman el tipo de la vecina con mas borde comun (primero pisos y areas verdes; el techo o
        la cuneta solo si no hay otra vecina). Se repite para las franjas que solo tocan otras franjas."""
        franjas = []
        for vuelta in range(4):
            cambio = False
            for c in self.caras:
                g = c["geom"]
                if c["tipo"] != "sin_asignar" or not (_ancho(g) < ancho_max or g.area < area_max): continue
                vec = {}
                for o in self.caras:
                    if o is c or o["tipo"] == "sin_asignar" or not g.envelope.intersects(o["geom"].envelope): continue
                    L = g.boundary.intersection(o["geom"].boundary).length
                    if L > 1e-3: vec[o["tipo"]] = vec.get(o["tipo"], 0.0) + L
                if not vec: continue
                pref = {t: L for t, L in vec.items() if t not in ("techo", "cuneta")} or vec
                t = max(pref, key=pref.get)
                c.update(tipo=t, fuente="franja angosta: tipo de la vecina", nombre="Franja (sardinel o borde)")
                franjas.append(c); cambio = True
            if not cambio: break
        if franjas:
            self.avisos.append("%d franjas angostas sin tipo (%.1f m2: sardineles, juntas o bordes de dibujo) tomaron el tipo de su "
                               "vecina; se pueden cambiar en el visor." % (len(franjas), sum(c["geom"].area for c in franjas)))

    def cerrar(self):
        """Control: suma de areas = area del cerco; sin montajes."""
        At = sum(c["geom"].area for c in self.caras); Ac = self.S.cerco.area
        self.cuadre = {"suma_caras_m2": round(At, 2), "area_cerco_m2": round(Ac, 2), "diferencia_m2": round(At - Ac, 2)}
        if abs(At - Ac) > 0.5:
            self.avisos.append("El mapa de superficies no cuadra con el area del cerco (%.2f m2 de diferencia)." % (At - Ac))
        self.sin_asignar = [c for c in self.caras if c["tipo"] == "sin_asignar"]
        if self.sin_asignar:
            self.avisos.append("%d areas sin asignar (%.1f m2): asignar su tipo en el visor (clic dentro del area) o fijar un valor "
                               "por defecto en el proyecto." % (len(self.sin_asignar), sum(c["geom"].area for c in self.sin_asignar)))
        por_def = [c for c in self.caras if c["fuente"] == "por defecto"]
        if por_def:
            self.avisos.append("%.1f m2 sin identificar en el plano se tomaron como '%s' por el valor por defecto del proyecto; confirmar." % (
                sum(c["geom"].area for c in por_def), self.por_defecto))

    # ------------------------------------------------------------------------------------------- resultados
    def por_tipo(self):
        out = {}
        for t in TIPOS + ("sin_asignar",):
            g = [c["geom"] for c in self.caras if c["tipo"] == t]
            out[t] = unary_union(g) if g else Polygon()
        return out

    def cuadro(self):
        C = self.P["C"]
        filas = []
        for t, g in self.por_tipo().items():
            if g.is_empty: continue
            filas.append({"tipo": t, "area_m2": round(g.area, 1), "C": C.get(t)})
        At = sum(f["area_m2"] for f in filas)
        AC = sum(f["area_m2"] * (f["C"] or 0) for f in filas if f["tipo"] != "sin_asignar")
        nombres = {}
        for c in self.caras:
            if c["fuente"] in ("resto", "sin tipo", "por defecto", "red de cunetas", "capa de techos", "capa de veredas"): continue
            k = (c["nombre"], c["tipo"]); nombres[k] = nombres.get(k, 0) + c["geom"].area
        return {"por_tipo": filas, "area_total_m2": round(At, 1),
                "C_ponderado": round(AC / (At - sum(f["area_m2"] for f in filas if f["tipo"] == "sin_asignar")), 3) if At else None,
                "superficies_con_nombre": [{"nombre": k[0], "tipo": k[1], "area_m2": round(v, 1)} for k, v in sorted(nombres.items())],
                "cuadre": self.cuadre, "ajustes": self.ajustes, "caras": len(self.caras),
                "sin_asignar": [{"id": c["id"], "area_m2": round(c["geom"].area, 2),
                                 "punto": [round(c["geom"].representative_point().x, 3), round(c["geom"].representative_point().y, 3)]}
                                for c in self.sin_asignar]}


# ------------------------------------------------------------------------------------------------ caida de los techos
def flechas_de(B, cfg):
    """Flechas de caida dibujadas por el usuario: del proyecto ("flechas_techo": [{"desde": [x, y], "hacia": [x, y]}]) o de una
    capa del DXF (capas.flechas_techo: cada linea o polilinea va del primer punto al ultimo, en el sentido en que cae el agua)."""
    out = [(tuple(f["desde"]), tuple(f["hacia"])) for f in cfg.get("flechas_techo", [])]
    sel = cfg.get("capas", {}).get("flechas_techo")
    if sel:
        for pts, cl, col, z in geom.seleccionar(B, sel):
            if len(pts) >= 2 and math.dist(pts[0], pts[-1]) > 0.1: out.append((tuple(pts[0]), tuple(pts[-1])))
    return out


def aguas_de_techos(sitio, cfg, flechas=None):
    """Partes de cada techo con hacia donde cae el agua.
    - Con flechas del usuario dentro del techo (mandan): cada parte del techo sigue la flecha mas cercana (1 flecha: una agua;
      2 opuestas: dos aguas; 4: cuatro aguas; techos en L: cada ala con su flecha). Cada m2 sigue su flecha hasta el borde.
    - Sin flechas: dos aguas con la cumbrera en el eje largo (criterio del usuario en Barranquita) y se avisa para confirmar."""
    flechas = flechas or []
    t_cfg = cfg.get("techos_caida", [])
    defecto = cfg.get("caida_por_defecto", "dos_aguas_eje_largo")
    g = sitio.techos
    if g.is_empty: return [], []
    avisos = []
    pols = [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.area > 4.0]
    out = []
    sin_dato = 0
    for k, p in enumerate(pols):
        propias = [(a, b) for a, b in flechas if p.buffer(0.3).contains(Point(a))]
        if propias:
            if len(propias) == 1:
                partes = [(p, propias[0])]
            else:
                vor = shapely.voronoi_polygons(shapely.MultiPoint([a for a, b in propias]), extend_to=p.buffer(50))
                partes = []
                for celda in vor.geoms:
                    f = next(fl for fl in propias if celda.contains(Point(fl[0])) or celda.distance(Point(fl[0])) < 1e-6)
                    parte = celda.intersection(p)
                    if not parte.is_empty: partes.append((parte, f))
            for parte, (a, b) in partes:
                (ux, uy), L = geom.unit(a, b)
                out.append({"techo": k, "poligono": parte, "techo_poligono": p, "flecha": (ux, uy), "tipo": "flecha"})
            continue
        dato = next((d for d in t_cfg if p.contains(Point(d["punto"]))), None)
        rect = p.minimum_rotated_rectangle; cs = list(rect.exterior.coords)[:4]
        lados = [(cs[i], cs[(i + 1) % 4]) for i in range(4)]
        largo = max(lados, key=lambda l: math.dist(*l))
        (ux, uy), Lr = geom.unit(*largo)
        c = rect.centroid
        if dato and dato.get("tipo") == "una_agua":
            out.append({"techo": k, "poligono": p, "alero": LineString(dato["lado_bajo"]), "tipo": "una_agua"}); continue
        if dato and dato.get("cumbrera"):
            a, b = dato["cumbrera"]; (ux, uy), _ = geom.unit(a, b); c = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        else:
            sin_dato += 1
            if defecto != "dos_aguas_eje_largo": continue
        nx, ny = -uy, ux; R = 1e4
        izq = Polygon([(c.x - ux * R, c.y - uy * R), (c.x + ux * R, c.y + uy * R), (c.x + ux * R + nx * R, c.y + uy * R + ny * R),
                       (c.x - ux * R + nx * R, c.y - uy * R + ny * R)])
        for lado, mitad in ((1, p.intersection(izq)), (-1, p.difference(izq))):
            if mitad.is_empty or mitad.area < 0.5: continue
            al = max(lados, key=lambda l: (((l[0][0] + l[1][0]) / 2 - c.x) * nx + ((l[0][1] + l[1][1]) / 2 - c.y) * ny) * lado)
            out.append({"techo": k, "poligono": mitad, "alero": LineString(al), "tipo": "dos_aguas"})
    if sin_dato:
        avisos.append("%d techos sin flecha de caida: se tomaron a dos aguas con la cumbrera en el eje largo; confirmar o poner "
                      "las flechas de caida en el visor." % sin_dato)
    return out, avisos
