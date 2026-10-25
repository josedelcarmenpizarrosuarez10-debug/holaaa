"""Lámina U-01 «Plano de ubicación y localización» (DXF): mapas esquemáticos del Perú, el departamento y la provincia con su
resaltado y recuadro (sin escala), el local a escala real con el cerco y la cuadrícula UTM, el cuadro de datos de ubicación y el cuadro
de coordenadas UTM de los vértices del cerco. El local se dibuja a escala real (1 unidad = 1 m) trasladado a la lámina: sus coordenadas
UTM verdaderas van en la cuadrícula y en el cuadro de coordenadas."""
import math

from shapely.geometry import MultiPolygon, Polygon, box
from ezdxf.enums import TextEntityAlignment as TA

from . import dxf_base as B
from . import ubicacion as UBI

CAPAS = (("UBIC-LIMITES", 8), ("UBIC-RELLENO", 9), ("UBIC-RESALTE", 30), ("UBIC-RECUADRO", 1), ("UBIC-TEXTOS", 7), ("UBIC-CERCO", 1),
         ("UBIC-TECHOS", 8), ("UBIC-CUADRICULA", 9))
MAPAS = ((35, 332, 290, 558), (300, 332, 555, 558), (565, 332, 820, 558))      # mm de papel: x0, y0, x1, y1
LOCAL = (35, 25, 415, 302)


def capas(doc):
    for n, c in CAPAS:
        if n not in doc.layers: doc.layers.add(n, color=c)


def _rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class _Marco:
    """Transformación lon/lat -> mm de papel dentro de un marco, con la vista del foco y la corrección por la latitud."""
    def __init__(self, lam, caja, foco, margen=0.08):
        self.lam = lam; x0, y0, x1, y1 = caja; self.caja = caja
        a, b, c, d = foco.bounds; lat0 = (b + d) / 2; self.k = math.cos(math.radians(lat0))
        w0, h0 = c - a, d - b; a -= w0 * margen; c += w0 * margen; b -= h0 * margen; d += h0 * margen
        w, h = (c - a) * self.k, d - b
        self.s = min((x1 - x0) / w, (y1 - y0) / h)
        self.cx, self.cy = (a + c) / 2, (b + d) / 2; self.mx, self.my = (x0 + x1) / 2, (y0 + y1) / 2
        hw, hh = (x1 - x0) / 2 / self.s / self.k, (y1 - y0) / 2 / self.s
        self.vista = box(self.cx - hw, self.cy - hh, self.cx + hw, self.cy + hh)

    def mm(self, lon, lat):
        return (self.mx + (lon - self.cx) * self.k * self.s, self.my + (lat - self.cy) * self.s)

    def P(self, lon, lat):
        return self.lam.P(*self.mm(lon, lat))

    def km_por_mm(self):
        return 111.32 / self.s


def _polis(g):
    if g.is_empty: return []
    if isinstance(g, Polygon): return [g]
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon) and not p.is_empty]


def _dibujar(lam, M, g, relleno=None, capa_borde="UBIC-LIMITES", ancho=0.0):
    for p in _polis(g.intersection(M.vista)):
        pts = [M.P(x, y) for x, y in p.exterior.coords]
        if relleno:
            h = lam.msp.add_hatch(dxfattribs={"layer": "UBIC-RESALTE" if capa_borde == "UBIC-RESALTE" else "UBIC-RELLENO"})
            h.rgb = _rgb(relleno); h.set_solid_fill(rgb=_rgb(relleno)); h.paths.add_polyline_path(pts, is_closed=True)
        lam.poli(pts, capa_borde, cerrada=True, const_width=lam.mm(ancho) if ancho else 0.0)


def _norte(lam, x, y, alto=14):
    """Flecha del norte: mitad izquierda rellena y mitad derecha en contorno, con la «N» encima."""
    p = lambda a, b: lam.P(x + a, y + b)
    h = lam.msp.add_hatch(color=250, dxfattribs={"layer": "UBIC-TEXTOS"}); h.set_solid_fill(color=250)
    h.paths.add_polyline_path([p(0, alto), p(-3.2, 0), p(0, 3.5)], is_closed=True)
    lam.poli([p(0, alto), p(-3.2, 0), p(0, 3.5), p(3.2, 0)], "UBIC-TEXTOS", cerrada=True)
    lam.texto(p(0, alto + 2), "N", 3.2, "UBIC-TEXTOS", TA.BOTTOM_CENTER)


def _escala(lam, x, y, km_mm, ancho_mm=60):
    obj = km_mm * ancho_mm; n = 10 ** math.floor(math.log10(obj)); paso = max(m * n for m in (1, 2, 5) if m * n <= obj)
    largo = paso / km_mm
    for k in range(4):
        pts = [lam.P(x + k * largo / 4, y), lam.P(x + (k + 1) * largo / 4, y), lam.P(x + (k + 1) * largo / 4, y + 2), lam.P(x + k * largo / 4, y + 2)]
        (lam.solido([pts[0], pts[1], pts[3], pts[2]], "UBIC-TEXTOS") if k % 2 == 0 else lam.poli(pts, "UBIC-TEXTOS", cerrada=True))
    lam.texto(lam.P(x, y + 3.2), "0", 2.0, "UBIC-TEXTOS", TA.BOTTOM_CENTER)
    lam.texto(lam.P(x + largo, y + 3.2), ("%g km" % paso) if paso >= 1 else ("%g m" % (paso * 1000)), 2.0, "UBIC-TEXTOS", TA.BOTTOM_CENTER)


def _mapa(lam, caja, titulo, fondo, items, foco, siguiente, colores, paises=None):
    x0, y0, x1, y1 = caja
    M = _Marco(lam, caja, foco)
    for p in paises or []:
        if p["iso"] != "PER": _dibujar(lam, M, p["geom"], "#ECEFF3")
    for x in fondo: _dibujar(lam, M, x["geom"], "#F4F6F8")
    col = UBI._colores(items)
    for x in items:
        es = siguiente is not None and siguiente["u"].startswith(x["u"])
        _dibujar(lam, M, x["geom"], colores.get("resaltado", "#E4572E") if es else col[x["u"]], "UBIC-RESALTE" if es else "UBIC-LIMITES", 0.35 if es else 0.0)
    area_vista = M.vista.area
    for x in items:
        g = x["geom"].intersection(M.vista)
        if g.is_empty: continue
        es = siguiente is not None and siguiente["u"].startswith(x["u"])
        if g.area / area_vista < 0.004 and not es: continue
        c = g.representative_point()
        lam.texto(M.P(c.x, c.y), x["n"].upper(), 2.6 if es else (1.8 if g.area / area_vista < 0.03 else 2.2), "UBIC-TEXTOS", TA.MIDDLE_CENTER)
    for p in paises or []:
        if p["iso"] == "PER": continue
        g = p["geom"].intersection(M.vista)
        if g.is_empty or g.area < area_vista * 0.02: continue
        c = g.representative_point(); lam.texto(M.P(c.x, c.y), p["n"], 2.8, "UBIC-TEXTOS", TA.MIDDLE_CENTER)
    if siguiente is not None:
        a, b, c, d = siguiente["geom"].bounds; m = max(c - a, d - b) * 0.12
        q0, q1 = M.mm(a - m, b - m), M.mm(c + m, d + m)
        q0 = (max(q0[0], x0), max(q0[1], y0)); q1 = (min(q1[0], x1), min(q1[1], y1))
        lam.rect(*lam.P(*q0), *lam.P(*q1), "UBIC-RECUADRO", const_width=lam.mm(0.7))
    lam.rect(*lam.P(x0, y0), *lam.P(x1, y1), "MARCO", const_width=lam.mm(0.5))
    _norte(lam, x1 - 12, y1 - 24); _escala(lam, x0 + 8, y0 + 6, M.km_por_mm(), (x1 - x0) * 0.25)
    lam.titulo_vista((x0 + x1) / 2, y1 + 12, titulo.upper(), "SIN ESCALA", ancho_mm=min(240, max(90, 2.6 * len(titulo))))


def escala_local(cerco_xy):
    """Escala de la localización para que el cerco entre en su marco con holgura (sirve también para ubicar la lámina en el modelo)."""
    xs = [p[0] for p in cerco_xy]; ys = [p[1] for p in cerco_xy]
    ancho, alto = max(xs) - min(xs), max(ys) - min(ys)
    lx0, ly0, lx1, ly1 = LOCAL
    return next((e for e in (100, 200, 250, 500, 750, 1000, 1500, 2000, 2500, 5000)
                 if ancho * 1.25 <= (lx1 - lx0) * e / 1000 and alto * 1.25 <= (ly1 - ly0 - 20) * e / 1000), 5000)


def lamina(doc, codigo, ox, oy, U, cerco_xy, techos, cfg_u=None):
    """Lámina U-01 con la escala del local elegida para que el cerco entre en su marco. Devuelve la lámina."""
    cfg_u = cfg_u or {}; colores = cfg_u.get("colores") or {}
    capas(doc)
    xs = [p[0] for p in cerco_xy]; ys = [p[1] for p in cerco_xy]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    lx0, ly0, lx1, ly1 = LOCAL
    esc = escala_local(cerco_xy)
    lam = B.Lamina(doc, ox, oy, esc, codigo, "PLANO DE UBICACION Y LOCALIZACION",
                   "%s - %s - %s" % (U.get("departamento", "").upper(), U.get("provincia", "").upper(), U.get("distrito", "").upper()),
                   escala_txt="INDICADA")
    L = UBI.limites(); d = L["por_u"].get(U.get("ubigeo", "")); prov = L["por_u"].get(U.get("ubigeo", "")[:4]); dep = L["por_u"].get(U.get("ubigeo", "")[:2])
    tit = U.get("titulos") or UBI.titulos(U, cfg_u)
    nombres = cfg_u.get("nombres") or {}
    ren = lambda lst: [dict(x, n=nombres.get(x["u"], x["n"])) for x in lst]
    if d is not None:
        peru = MultiPolygon([p for x in L["departamentos"] for p in _polis(x["geom"])])
        _mapa(lam, MAPAS[0], tit[0].split(": ", 1)[-1], [], ren(L["departamentos"]), peru, dep, colores, L["paises"])
        vec_dep = [x for x in L["departamentos"] if x["u"] != dep["u"] and x["geom"].intersects(dep["geom"].buffer(0.2))]
        _mapa(lam, MAPAS[1], tit[1].split(": ", 1)[-1], vec_dep, ren([x for x in L["provincias"] if x["u"][:2] == dep["u"]]), dep["geom"], prov, colores)
        vec_prov = [x for x in L["provincias"] if x["u"] != prov["u"] and x["geom"].intersects(prov["geom"].buffer(0.05))]
        _mapa(lam, MAPAS[2], tit[2].split(": ", 1)[-1], vec_prov, ren([x for x in L["distritos"] if x["u"][:4] == prov["u"]]), prov["geom"], d, colores)
    # ---------------------------------------------------------------- el local a escala real
    mx, my = (lx0 + lx1) / 2, (ly0 + ly1) / 2 - 8
    T = lambda x, y: (lam.P(mx, my)[0] + (x - cx), lam.P(mx, my)[1] + (y - cy))
    for t in techos or []:
        for p in _polis(t):
            pts = [T(x, y) for x, y in p.exterior.coords]
            h = lam.msp.add_hatch(dxfattribs={"layer": "UBIC-TECHOS"}); h.rgb = (205, 210, 218); h.set_solid_fill(rgb=(205, 210, 218)); h.paths.add_polyline_path(pts, is_closed=True)
            lam.poli(pts, "UBIC-TECHOS", cerrada=True)
    lam.poli([T(x, y) for x, y in cerco_xy], "UBIC-CERCO", cerrada=True, const_width=lam.mm(0.9))
    lam.texto((T(cx, max(ys))[0], T(cx, max(ys))[1] + lam.mm(3)), "ÁREA DEL PROYECTO", 2.8, "UBIC-TEXTOS", TA.BOTTOM_CENTER)
    # cuadrícula UTM verdadera en el borde del marco
    paso = next(p for p in (5, 10, 20, 25, 50, 100, 200, 250, 500) if (lx1 - lx0) * esc / 1000 / p <= 8)
    e0, e1 = cx - (mx - lx0) * esc / 1000, cx + (lx1 - mx) * esc / 1000; n0, n1 = cy - (my - ly0) * esc / 1000, cy + (ly1 - my) * esc / 1000
    # sin rótulos de cuadrícula sobre la barra de escala (esquina inferior izquierda) ni sobre el norte (superior derecha)
    (ex0, ey0), (ex1, ey1) = lam.P(lx0, ly0), lam.P(lx0 + 80, ly0 + 18)
    (nx0, ny0), (nx1, ny1) = lam.P(lx1 - 26, ly1 - 30), lam.P(lx1, ly1)
    libre = lambda x, y, w: not (x - w < ex1 and x + w > ex0 and y < ey1 and y > ey0 - lam.mm(3)) and not (x + w > nx0 and y > ny0)
    for E in range(int(math.ceil(e0 / paso)) * paso, int(e1) + 1, paso):
        a, b = T(E, n0), T(E, n1); lam.linea(a, b, "UBIC-CUADRICULA")
        if U.get("georef") and libre(a[0], a[1] + lam.mm(1), lam.mm(9)):
            lam.texto((a[0], a[1] + lam.mm(1)), "E %d" % E, 1.6, "UBIC-TEXTOS", TA.BOTTOM_CENTER)
    for N in range(int(math.ceil(n0 / paso)) * paso, int(n1) + 1, paso):
        a, b = T(e0, N), T(e1, N); lam.linea(a, b, "UBIC-CUADRICULA")
        if U.get("georef") and libre(a[0] + lam.mm(10), a[1] + lam.mm(0.6), lam.mm(10)):
            lam.texto((a[0] + lam.mm(1), a[1] + lam.mm(0.6)), "N %d" % N, 1.6, "UBIC-TEXTOS", TA.BOTTOM_LEFT)
    lam.rect(*lam.P(lx0, ly0), *lam.P(lx1, ly1), "MARCO", const_width=lam.mm(0.5))
    _norte(lam, lx1 - 12, ly1 - 24)
    _escala(lam, lx0 + 8, ly0 + 6, esc / 1e6, 60)
    lam.titulo_vista((lx0 + lx1) / 2, ly1 + 12, "LOCALIZACIÓN DEL PROYECTO", "ESC. 1/%d - COORDENADAS UTM WGS 84%s" % (esc, (" ZONA %dS" % U["zona"]) if U.get("zona") else ""),
                     ancho_mm=150)
    # ---------------------------------------------------------------- cuadros
    filas = [["Departamento", U.get("departamento", "")], ["Provincia", U.get("provincia", "")], ["Distrito", U.get("distrito", "")],
             ["Ubigeo (INEI)", U.get("ubigeo", "")]]
    if U.get("georef"):
        filas += [["Coordenadas UTM (centro)", "E %.1f  N %.1f" % (cx, cy)], ["Sistema", "WGS 84 - UTM %dS" % U["zona"]],
                  ["Latitud / longitud", "%.5f° / %.5f°" % (U["lat"], U["lon"])]]
    lam.tabla(430, 315, ["DATO", "VALOR"], filas, [55, 150], hmm=2.0, alto_mm=6.0, titulo="DATOS DE UBICACIÓN")
    if U.get("georef"):
        vert = [["V%d" % (i + 1), "%.3f" % x, "%.3f" % y] for i, (x, y) in enumerate(cerco_xy)]
        filas_max = 18
        lam.tabla(430, 315 - 6.0 * (len(filas) + 1) - 18, ["VÉRTICE", "ESTE (m)", "NORTE (m)"], vert[:filas_max], [30, 50, 50], hmm=1.8, alto_mm=5.0,
                  titulo="CUADRO DE COORDENADAS UTM DEL CERCO")
    lam.notas(430, 70, "NOTAS", ["1. Límites políticos referenciales: %s." % U.get("fuente_limites", "INEI"),
                                 "2. Mapas 1 a 3 sin escala; localización a la escala indicada.",
                                 "3. Coordenadas UTM WGS 84 del plano general del proyecto."], hmm=1.8, ancho_mm=205)
    return lam
