"""Salidas del modulo: planta de la red en DXF (escala real, 1 unidad = 1 m) y vista previa PNG.

Estilo del usuario: cuneta con rejilla en celeste, tapada en verde, flechas rojas de flujo, tapas de inspeccion en los tapados,
uniones nuevas resaltadas (para que el usuario vea que agrego el programa), cerco = limite de intervencion.
"""
import math

import ezdxf
from ezdxf.enums import TextEntityAlignment
from shapely.geometry import LineString
from shapely.ops import unary_union

CAPAS = {
    "DRN-LIMITE-INTERVENCION": (6, 50), "DRN-CURVAS": (8, 13), "DRN-CURVAS-TXT": (8, 13), "DRN-ARQ-TECHOS": (9, 13),
    "DRN-ARQ-VEREDAS": (9, 13), "DRN-EJES-USUARIO": (6, 18), "DRN-EJE-CUNETA": (5, 18), "DRN-UNION-NUEVA": (30, 35),
    "DRN-CUNETA-REJILLA": (140, 35), "DRN-CUNETA-TAPADA": (84, 35), "DRN-FLECHAS": (1, 25), "DRN-TAPAS": (84, 25),
    "DRN-DESCARGAS": (1, 35), "DRN-TEXTOS": (7, 18), "DRN-NUDOS": (250, 13),
}
H_TXT = 0.45          # 2.25 mm en papel a 1/200


def _contorno(msp, geom, capa):
    gs = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
    for g in gs:
        if g.is_empty: continue
        for anillo in [g.exterior] + list(g.interiors):
            msp.add_lwpolyline(list(anillo.coords), close=True, dxfattribs={"layer": capa})


def _flecha(msp, a, b, capa="DRN-FLECHAS", largo=1.2):
    L = math.dist(a, b)
    if L < 2.0: return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    p = (m[0] + ux * largo / 2, m[1] + uy * largo / 2); q = (m[0] - ux * largo / 2, m[1] - uy * largo / 2)
    w = 0.25
    msp.add_line(q, p, dxfattribs={"layer": capa})
    msp.add_solid([p, (p[0] - ux * 0.5 - uy * w, p[1] - uy * 0.5 + ux * w), (p[0] - ux * 0.5 + uy * w, p[1] - uy * 0.5 - ux * w)],
                  dxfattribs={"layer": capa})


def _tapas(R, P):
    """Tapas de inspeccion en tramos tapados: inicio, fin y cada 10 m como maximo."""
    out = []
    for r in R["ramales"]:
        xy = [tuple(R["nudos"][n]) for n in r["nudos"]]
        acum = [0.0]
        for a, b in zip(xy[:-1], xy[1:]): acum.append(acum[-1] + math.dist(a, b))
        def punto(s):
            for i in range(len(xy) - 1):
                if acum[i] - 1e-9 <= s <= acum[i + 1] + 1e-9:
                    t = (s - acum[i]) / (acum[i + 1] - acum[i]) if acum[i + 1] > acum[i] else 0
                    return (xy[i][0] + t * (xy[i + 1][0] - xy[i][0]), xy[i][1] + t * (xy[i + 1][1] - xy[i][1])), i
            return xy[-1], len(xy) - 2
        for a, b in r["tapados"]:
            if b - a < 1.0: continue
            n = max(1, math.ceil((b - a - P["tapa_lado"]) / P["tapa_sep_max"]))
            for k in range(n + 1):
                s = a + P["tapa_lado"] / 2 + k * (b - a - P["tapa_lado"]) / n
                (x, y), i = punto(s)
                out.append({"eje": r["codigo"], "s": round(s, 2), "x": x, "y": y, "dir": (xy[i], xy[i + 1])})
    return out


def dxf_planta(ruta, R, red, sitio, curvas, P, proyecto):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.M
    for n, (c, lw) in CAPAS.items(): doc.layers.add(n, color=c, lineweight=lw)
    msp = doc.modelspace()
    for z, L in curvas:
        msp.add_lwpolyline(list(L.coords), dxfattribs={"layer": "DRN-CURVAS", "elevation": z})
    for z, L in curvas:
        if abs(z - round(z)) < 1e-6 and L.length > 10:
            p = L.interpolate(0.5, normalized=True)
            msp.add_text("%.2f" % z, height=0.30, dxfattribs={"layer": "DRN-CURVAS-TXT"}).set_placement((p.x, p.y))
    _contorno(msp, sitio.cerco, "DRN-LIMITE-INTERVENCION")
    if not sitio.techos.is_empty: _contorno(msp, sitio.techos, "DRN-ARQ-TECHOS")
    if not sitio.veredas.is_empty: _contorno(msp, sitio.veredas.intersection(sitio.cerco.buffer(5)), "DRN-ARQ-VEREDAS")
    Nn = R["nudos"]
    rej, tap = [], []
    for r in R["ramales"]:
        xy = [tuple(Nn[n]) for n in r["nudos"]]
        acum = [0.0]
        for a, b in zip(xy[:-1], xy[1:]): acum.append(acum[-1] + math.dist(a, b))
        ls = LineString(xy)
        cortes = sorted({0.0, ls.length} | {v for iv in r["tapados"] for v in iv})
        from shapely.ops import substring
        for a, b in zip(cortes[:-1], cortes[1:]):
            if b - a < 0.01: continue
            pz = substring(ls, a, b); m = (a + b) / 2
            es_tap = any(x - 1e-6 <= m <= y + 1e-6 for x, y in r["tapados"])
            (tap if es_tap else rej).append(pz.buffer(P["b_int"] / 2 + P["e_muro"], cap_style=2, join_style=2))
        for t in r["tramos"]:
            capa = "DRN-UNION-NUEVA" if t["origen"] in ("union", "pase") else "DRN-EJE-CUNETA"
            msp.add_line(Nn[t["de"]], Nn[t["a"]], dxfattribs={"layer": capa, "linetype": "CENTER", "ltscale": 0.2})
            _flecha(msp, Nn[t["de"]], Nn[t["a"]])
    U_rej = unary_union(rej) if rej else None
    U_tap = unary_union(tap) if tap else None
    if U_rej is not None: _contorno(msp, U_rej.difference(U_tap) if U_tap is not None else U_rej, "DRN-CUNETA-REJILLA")
    if U_tap is not None:
        _contorno(msp, U_tap, "DRN-CUNETA-TAPADA")
        h = msp.add_hatch(dxfattribs={"layer": "DRN-CUNETA-TAPADA"}); h.rgb = (198, 230, 198)
        for g in (U_tap.geoms if hasattr(U_tap, "geoms") else [U_tap]):
            h.paths.add_polyline_path(list(g.exterior.coords), is_closed=True)
        h.set_solid_fill(color=84, rgb=(198, 230, 198))
    for tp in _tapas(R, P):
        (a, b) = tp["dir"]; L = math.dist(a, b); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; s = P["tapa_lado"] / 2
        c = [(tp["x"] + ux * dx * s - uy * dy * s, tp["y"] + uy * dx * s + ux * dy * s) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        msp.add_lwpolyline(c, close=True, dxfattribs={"layer": "DRN-TAPAS"})
    for n, (x, y) in Nn.items():
        if n in red.descargas:
            msp.add_circle((x, y), 0.6, dxfattribs={"layer": "DRN-DESCARGAS"})
            msp.add_text(n, height=0.8, dxfattribs={"layer": "DRN-DESCARGAS"}).set_placement((x + 0.9, y + 0.9))
        elif not n.endswith("n"):
            msp.add_text(n, height=0.25, dxfattribs={"layer": "DRN-NUDOS"}).set_placement((x + 0.15, y + 0.15))
    for r in R["ramales"]:
        tl = max(r["tramos"], key=lambda t: t["L"])
        a, b = Nn[tl["de"]], Nn[tl["a"]]; ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); off = 0.75
        nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
        msp.add_text(r["codigo"], height=H_TXT, rotation=ang, dxfattribs={"layer": "DRN-TEXTOS"}).set_placement(
            (m[0] + nx * off, m[1] + ny * off), align=TextEntityAlignment.BOTTOM_CENTER)
    doc.header["$EXTMIN"] = sitio.cerco.bounds[:2] + (0,)
    doc.header["$EXTMAX"] = sitio.cerco.bounds[2:] + (0,)
    doc.audit()
    doc.saveas(ruta)
    return ruta


COLOR_SUP = {"techo": "#d6d6d6", "pavimento": "#efe2c2", "estacionamiento": "#c9d6e6", "cuneta": "#9fc5e8", "verde": "#e2f0d9"}
COLORES_SIS = ["#1f6fb4", "#2a9d3c", "#c2571a", "#7b3fa0", "#b8860b", "#0f8a8a", "#a33a5a", "#4a5a8a"]


def png_planta(ruta, R, red, sitio, curvas, ejes_usuario, titulo, candidatos=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x0, y0, x1, y1 = sitio.cerco.buffer(6).bounds
    W = x1 - x0; H = y1 - y0; esc = 14.0 / max(W, H)
    fig, ax = plt.subplots(figsize=(max(6, W * esc) + 0.5, max(5, H * esc) + 1.2), dpi=170)
    for z, L in curvas:
        xs, ys = L.xy; ax.plot(xs, ys, color="#c9c9c9", lw=0.5 if abs(z - round(z)) > 1e-6 else 0.9, zorder=1)
    def poly(g, **kw):
        for p in (g.geoms if hasattr(g, "geoms") else [g]):
            if p.is_empty: continue
            xs, ys = p.exterior.xy; ax.fill(xs, ys, **kw)
    sup = sitio.superficies()
    mapa = getattr(sitio, "mapa", None)
    if mapa is not None:
        # caras grandes primero y las chicas encima (asi los huecos de una cara quedan cubiertos por las caras que los ocupan)
        for c in sorted(mapa.caras, key=lambda c: -c["geom"].area):
            xs, ys = c["geom"].exterior.xy
            if c["tipo"] == "sin_asignar":
                ax.fill(xs, ys, fc="#ff4fd8", ec="#c2008f", lw=0.6, hatch="////", alpha=0.55, zorder=2)
            else:
                ax.fill(xs, ys, fc=COLOR_SUP.get(c["tipo"], "#ffffff"), ec="#ffffff", lw=0.15, zorder=2)
    else:
        for k in ("verde", "estacionamiento", "pavimento", "techo"):        # de abajo hacia arriba: el verde tiene huecos
            if not sup[k].is_empty: poly(sup[k], fc=COLOR_SUP[k], ec="none", zorder=2)
    if not sitio.techos.is_empty:
        for p in (sitio.techos.geoms if hasattr(sitio.techos, "geoms") else [sitio.techos]):
            xs, ys = p.exterior.xy; ax.plot(xs, ys, color="#9a9a9a", lw=0.4, zorder=2)
    for e in sitio.extra:
        c = e["geom"].representative_point()
        ax.text(c.x, c.y, "%s\n(%s, %.0f m2)" % (e["nombre"], e["tipo"], e["geom"].area), fontsize=5.5, ha="center", va="center",
                color="#333", zorder=7, bbox=dict(fc="white", ec="#999", lw=0.3, alpha=0.8, pad=1.0))
    xs, ys = sitio.cerco.exterior.xy; ax.plot(xs, ys, color="#8a1c7c", lw=1.4, zorder=3, label="Cerco = limite de intervencion")
    for ag in getattr(sitio, "aguas", []):            # caida de cada mitad de techo hacia su alero
        c = ag["poligono"].representative_point(); al = ag["alero"]; q = al.interpolate(al.project(c))
        ax.annotate("", xy=(q.x, q.y), xytext=(c.x, c.y), arrowprops=dict(arrowstyle="-|>", color="#1565c0", lw=0.9), zorder=6)
    for pts in ejes_usuario:
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color="#e040fb", lw=2.4, alpha=0.35, zorder=4)
    if candidatos:
        ok = [c for c in candidatos if c["holgura"] > 0]
        ax.scatter([c["q"][0] for c in ok], [c["q"][1] for c in ok], s=3, color="#9ccc65", zorder=4)
    if R:
        Nn = R["nudos"]
        for r in R["ramales"]:
            col = COLORES_SIS[(r["sistema"] - 1) % len(COLORES_SIS)]
            for t in r["tramos"]:
                a, b = Nn[t["de"]], Nn[t["a"]]
                nueva = t["origen"] in ("union", "pase")
                ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=1.6, ls="--" if nueva else "-", zorder=5)
                if math.dist(a, b) > 3:
                    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); ux, uy = (b[0] - a[0]) / math.dist(a, b), (b[1] - a[1]) / math.dist(a, b)
                    ax.annotate("", xy=(m[0] + ux * 0.8, m[1] + uy * 0.8), xytext=(m[0] - ux * 0.8, m[1] - uy * 0.8),
                                arrowprops=dict(arrowstyle="-|>", color="#d32f2f", lw=0.8), zorder=6)
        for r in R["ramales"]:
            tl = max(r["tramos"], key=lambda t: t["L"]); a, b = Nn[tl["de"]], Nn[tl["a"]]
            ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, r["codigo"].replace("EJE-", "E"), fontsize=5, ha="center", va="bottom",
                    color="#222", zorder=7)
        for d in red.descargas:
            x, y = Nn[d]; ax.plot(x, y, "o", ms=7, mfc="#d32f2f", mec="white", zorder=8)
            ax.text(x, y + 1.2, d, fontsize=8, fontweight="bold", color="#d32f2f", ha="center", zorder=8)
    ax.set_aspect("equal"); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    ax.set_title(titulo, fontsize=9)
    ax.tick_params(labelsize=6)
    ax.ticklabel_format(useOffset=False, style="plain")
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    ley = [Patch(fc=COLOR_SUP[k], label="%s (C = %.2f): %.0f m2" % (n, sitio.P["C"][k], sup[k].area))
           for k, n in (("techo", "Techos"), ("pavimento", "Pavimentos y veredas"), ("estacionamiento", "Estacionamiento"),
                        ("cuneta", "Cunetas (franja de 0.60 m)"), ("verde", "Area verde")) if not sup[k].is_empty]
    if mapa is not None and mapa.sin_asignar:
        ley.append(Patch(fc="#ff4fd8", ec="#c2008f", hatch="////", label="SIN ASIGNAR: %.0f m2 (asignar tipo)" % sum(c["geom"].area for c in mapa.sin_asignar)))
    ley += [Line2D([], [], color="#8a1c7c", lw=1.4, label="Cerco (limite de intervencion)"),
           Line2D([], [], color="#e040fb", lw=2.4, alpha=0.35, label="Lineas del usuario"),
           ] + ([Line2D([], [], color="#444", lw=1.6, label="Cuneta sobre linea del usuario"),
                 Line2D([], [], color="#444", lw=1.6, ls="--", label="Union nueva (agregada por el programa)"),
                 Line2D([], [], marker="o", ls="", mfc="#d32f2f", mec="white", ms=7, label="Descarga (pase en el cimiento del cerco)")] if R else [])
    if getattr(sitio, "aguas", None):
        ley.append(Line2D([], [], color="#1565c0", lw=0.9, marker=">", label="Caida del techo hacia su alero (canaleta y cuneta)"))
    ax.legend(handles=ley, loc="lower left", fontsize=6, framealpha=0.9)
    fig.tight_layout(); fig.savefig(ruta); plt.close(fig)
    return ruta
