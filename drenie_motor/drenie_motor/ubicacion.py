"""Ubicación del proyecto y mapas de ubicación (Perú, departamento, provincia y local).

- Ubicación automática: el plano está en coordenadas UTM WGS 84; se prueba la zona 17, 18 y 19 sur y se toma la que cae dentro de un
  distrito del Perú (si cae en más de una, la que coincide con el texto de ubicación del proyecto; si no, la indicada en el editor).
  Con el punto en latitud y longitud se busca el distrito, su provincia y su departamento (ubigeo del INEI).
- Límites: limites_peru.json (herramientas_mapas/armar_limites.py), fuente INEI; países vecinos de Natural Earth.
- Mapas: N° 01 el Perú con el departamento resaltado, N° 02 el departamento con la provincia, N° 03 la provincia con el distrito y
  N° 04 el local: foto aérea propia (ubicada con sus coordenadas UTM), o el mapa de calles de OpenStreetMap (con su atribución), o, sin
  internet, el plano del sitio. Cada mapa con norte, escala gráfica, coordenadas y el recuadro rojo de la zona siguiente.
- Todo lo que el usuario cambia en el editor de Ubicación del visor va en cfg["ubicacion"]: zona_utm, ubigeo, nombres (por ubigeo),
  titulos (4), colores (resaltado, recuadro, cerco), foto {ruta, xmin, ymin, xmax, ymax} y osm (False para no usar internet).
"""
import io
import json
import math
import os
import unicodedata
import urllib.request
from functools import lru_cache

from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.prepared import prep

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "limites_peru.json")
PASTEL = ["#F6D186", "#B5E3A1", "#A9C5EB", "#F3B5CF", "#9FDCCB", "#FCC89B", "#D4B5E8", "#E9E39A", "#B9D7F0", "#F2B8A2", "#C3E6B6", "#E7C6E9"]
TITULOS = ["Mapa N° 01: Mapa del Perú", "Mapa N° 02: Mapa del Departamento de {dep}", "Mapa N° 03: Mapa de la Provincia de {prov} ({dist})",
           "Mapa N° 04: Mapa de ubicación del proyecto ({dist})"]
UA = "DrenIE/3.1 (mapas de ubicacion de proyectos; HIDROCONSULT)"


# ------------------------------------------------------------------ coordenadas
def utm_a_geo(E, N, zona, sur=True):
    """UTM WGS 84 -> (latitud, longitud) en grados (Snyder, USGS 1987; error menor a 1 mm dentro de la zona)."""
    a = 6378137.0; f = 1 / 298.257223563; k0 = 0.9996; e2 = f * (2 - f); ep2 = e2 / (1 - e2)
    x = E - 500000.0; y = N - (10000000.0 if sur else 0.0)
    mu = y / k0 / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    p1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu) + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
          + (151 * e1 ** 3 / 96) * math.sin(6 * mu) + (1097 * e1 ** 4 / 512) * math.sin(8 * mu))
    C1 = ep2 * math.cos(p1) ** 2; T1 = math.tan(p1) ** 2; N1 = a / math.sqrt(1 - e2 * math.sin(p1) ** 2)
    R1 = a * (1 - e2) / (1 - e2 * math.sin(p1) ** 2) ** 1.5; D = x / (N1 * k0)
    lat = p1 - (N1 * math.tan(p1) / R1) * (D ** 2 / 2 - (5 + 3 * T1 + 10 * C1 - 4 * C1 ** 2 - 9 * ep2) * D ** 4 / 24
                                           + (61 + 90 * T1 + 298 * C1 + 45 * T1 ** 2 - 252 * ep2 - 3 * C1 ** 2) * D ** 6 / 720)
    lon = (D - (1 + 2 * T1 + C1) * D ** 3 / 6 + (5 - 2 * C1 + 28 * T1 - 3 * C1 ** 2 + 8 * ep2 + 24 * T1 ** 2) * D ** 5 / 120) / math.cos(p1)
    return math.degrees(lat), (zona * 6 - 183) + math.degrees(lon)


def es_utm_peru(x, y):
    return 150000 <= x <= 850000 and 7900000 <= y <= 10000000


def _norm(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().upper()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in t).split())


# ------------------------------------------------------------------ límites
def _geom(anillos_lista):
    polis = [Polygon(a[0], a[1:]) for a in anillos_lista if len(a[0]) >= 4]
    return MultiPolygon(polis) if len(polis) > 1 else polis[0]


@lru_cache(maxsize=1)
def limites():
    d = json.load(open(RUTA, encoding="utf-8"))
    out = {"fuente": d.get("fuente", "INEI"), "fuente_corta": d.get("fuente_corta")}
    for k in ("departamentos", "provincias", "distritos", "paises"):
        out[k] = [dict(x, geom=_geom(x["g"])) for x in d[k] if x.get("g")]
        for x in out[k]: x.pop("g")
    out["por_u"] = {x["u"]: x for k in ("departamentos", "provincias", "distritos") for x in out[k]}
    out["prep_dist"] = [(prep(x["geom"]), x) for x in out["distritos"]]
    return out


def distrito_en(lon, lat):
    p = Point(lon, lat)
    for pg, x in limites()["prep_dist"]:
        if pg.contains(p): return x
    return None


def _jerarquia(dist, nombres):
    L = limites(); u = dist["u"]
    dep = L["por_u"].get(u[:2]); prov = L["por_u"].get(u[:4])
    nom = lambda x: (nombres or {}).get(x["u"], x["n"]) if x else ""
    return {"ubigeo": u, "distrito": nom(dist), "provincia": nom(prov), "departamento": nom(dep), "capital": dist.get("cap", ""),
            "_d": dist, "_p": prov, "_dp": dep}


def ubicar(cerco_xy, cfg_u=None, texto=""):
    """Ubicación del proyecto: {georef, zona, este, norte, lat, lon, ubigeo, distrito, provincia, departamento, automatica, avisos, candidatos}."""
    u = cfg_u or {}; avisos = []
    xs = [p[0] for p in cerco_xy]; ys = [p[1] for p in cerco_xy]
    cx, cy = (sum(xs) / len(xs), sum(ys) / len(ys)) if xs else (None, None)
    este, norte = u.get("este", cx), u.get("norte", cy)
    nombres = u.get("nombres") or {}
    res = {"georef": False, "zona": None, "este": este, "norte": norte, "lat": None, "lon": None, "automatica": True, "avisos": avisos, "candidatos": []}
    if este is not None and es_utm_peru(este, norte):
        zonas = [int(u["zona_utm"])] if u.get("zona_utm") else [18, 17, 19]
        cands = []
        for z in zonas:
            la, lo = utm_a_geo(este, norte, z); d = distrito_en(lo, la)
            if d: cands.append((z, la, lo, d))
        res["candidatos"] = [{"zona": z, "ubigeo": d["u"], "distrito": _jerarquia(d, nombres)["distrito"]} for z, la, lo, d in cands]
        if cands:
            if len(cands) > 1:
                t = _norm(texto)
                pts = [(sum(1 for n in (_jerarquia(d, {})["distrito"], _jerarquia(d, {})["provincia"], _jerarquia(d, {})["departamento"])
                            if n and _norm(n) in t), -k) for k, (z, la, lo, d) in enumerate(cands)]
                k = max(range(len(cands)), key=lambda i: pts[i])
                if pts[k][0] == 0:
                    avisos.append("Las coordenadas caben en más de una zona UTM (%s): se tomó la zona %dS; confírmela en el editor de Ubicación."
                                  % (", ".join("%dS %s" % (z, d["n"]) for z, la, lo, d in cands), cands[k][0]))
                z, la, lo, d = cands[k]
            else:
                z, la, lo, d = cands[0]
            res.update(georef=True, zona=z, lat=la, lon=lo, automatica=not u.get("zona_utm"), **_jerarquia(d, nombres))
            fijo = limites()["por_u"].get(str(u.get("ubigeo") or ""))
            if fijo is not None and fijo["u"] != d["u"] and len(fijo["u"]) == 6:
                # el distrito elegido en el editor manda; las coordenadas siguen sirviendo para el mapa 4 y la lámina
                avisos.append("Las coordenadas del plano caen en el distrito %s, pero en el editor de Ubicación se fijó %s: se usa %s."
                              % (d["n"], fijo["n"], fijo["n"]))
                res.update(automatica=False, **_jerarquia(fijo, nombres))
            elif fijo is not None: res["automatica"] = False
        else:
            avisos.append("Las coordenadas del plano (E %.0f, N %.0f) no caen en ningún distrito del Perú en las zonas 17S, 18S ni 19S: "
                          "revise que el plano esté en UTM WGS 84 o indique la ubicación en el editor." % (este, norte))
    elif este is not None:
        avisos.append("El plano no está en coordenadas UTM (está en coordenadas locales): los mapas 1 a 3 salen con el distrito que se "
                      "indique en el editor de Ubicación y el mapa 4 con el plano del sitio.")
    if not res.get("ubigeo"):
        # sin coordenadas útiles: ubigeo del editor o el distrito escrito en la memoria / ubicación del proyecto
        d = None
        if u.get("ubigeo"): d = limites()["por_u"].get(str(u["ubigeo"]))
        if d is None and texto:
            t = _norm(texto)
            hallados = [x for x in limites()["distritos"] if _norm(x["n"]) and (" " + _norm(x["n"]) + " ") in (" " + t + " ")]
            if len(hallados) > 1:
                hallados = [x for x in hallados if _norm(limites()["por_u"].get(x["u"][:4], {}).get("n", "")) in t] or hallados
            d = hallados[0] if len(hallados) == 1 else None
        if d is not None:
            res.update(automatica=False, **_jerarquia(d, nombres))
            c = d["geom"].representative_point(); res.setdefault("lat", None)
            if res["lat"] is None: res.update(lat=c.y, lon=c.x)
        else:
            avisos.append("No se pudo ubicar el distrito del proyecto: elíjalo en el editor de Ubicación.")
    return res


# ------------------------------------------------------------------ dibujo
def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _colores(items):
    """Coloreo de vecinos con colores distintos (voraz)."""
    col = {}
    for i, x in enumerate(items):
        usados = {col[y["u"]] for y in items[:i] if y["u"] in col and x["geom"].buffer(1e-4).intersects(y["geom"])}
        col[x["u"]] = next(c for c in PASTEL + PASTEL if c not in usados) if len(usados) < len(PASTEL) else PASTEL[i % len(PASTEL)]
    return col


def _poligono(ax, g, **kw):
    from matplotlib.patches import Polygon as MPoly
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.is_empty: continue
        ax.add_patch(MPoly(list(p.exterior.coords), closed=True, **kw))
        for h in p.interiors: ax.add_patch(MPoly(list(h.coords), closed=True, facecolor="white", edgecolor=kw.get("edgecolor", "none"), lw=kw.get("lw", 0.5)))


def _norte(ax, x, y, tam):
    ax.annotate("", xy=(x, y + tam), xytext=(x, y), arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#0B2545", mutation_scale=16), annotation_clip=False)
    ax.text(x, y + tam * 1.12, "N", ha="center", va="bottom", fontsize=11, fontweight="bold", color="#0B2545")


def _escala(ax, x0, y0, km_por_unidad, ancho_vista):
    """Escala gráfica de 1-2-5 × 10^n km que ocupa cerca de un 22 % del ancho."""
    obj = ancho_vista * 0.22 * km_por_unidad
    n = 10 ** math.floor(math.log10(obj)); paso = max([m * n for m in (1, 2, 5) if m * n <= obj] or [n])
    largo = paso / km_por_unidad; h = ancho_vista * 0.012
    for k in range(4):
        ax.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle((x0 + k * largo / 4, y0), largo / 4, h,
                     facecolor="#0B2545" if k % 2 == 0 else "white", edgecolor="#0B2545", lw=0.8, zorder=20))
    txt = ("%g km" % paso) if paso >= 1 else ("%g m" % (paso * 1000))
    ax.text(x0, y0 + h * 1.6, "0", fontsize=7, ha="center", zorder=20); ax.text(x0 + largo, y0 + h * 1.6, txt, fontsize=7, ha="center", zorder=20)


def _marco(ax, titulo, fuente):
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_edgecolor("#0B2545"); s.set_linewidth(1.2)
    ax.set_title(titulo, fontsize=11, fontweight="bold", color="#0B2545", pad=6)
    ax.text(0.99, 0.005, fuente, transform=ax.transAxes, ha="right", va="bottom", fontsize=6, color="#5C7390", zorder=30,
            bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=1))


def _vista(ax, g, margen=0.08, cuadrado=True):
    x0, y0, x1, y1 = g.bounds; w, h = x1 - x0, y1 - y0
    lat0 = (y0 + y1) / 2; k = 1 / max(0.2, math.cos(math.radians(lat0)))
    if cuadrado:   # vista cuadrada en km: alarga el lado corto
        wkm, hkm = w / k, h
        if wkm > hkm: d = (wkm - hkm) / 2; y0 -= d; y1 += d
        else: d = (hkm - wkm) * k / 2; x0 -= d; x1 += d
        w, h = x1 - x0, y1 - y0
    ax.set_xlim(x0 - w * margen, x1 + w * margen); ax.set_ylim(y0 - h * margen, y1 + h * margen)
    ax.set_aspect(k)
    return ax.get_xlim(), ax.get_ylim(), k


def _etiquetas(ax, items, vista, color="#1B2A3A", minimo=0.0025, grande=None):
    (x0, x1), (y0, y1) = vista; area_vista = (x1 - x0) * (y1 - y0)
    for x in items:
        g = x["geom"]; fr = g.area / area_vista
        if fr < minimo and x is not grande: continue
        c = g.representative_point()
        if not (x0 < c.x < x1 and y0 < c.y < y1): continue
        tam = 6.5 if fr < 0.01 else 7.5 if fr < 0.04 else 9
        ax.text(c.x, c.y, x["n"].upper() if x is not grande else x["n"].upper(), ha="center", va="center", fontsize=tam + (1 if x is grande else 0),
                color=color, fontweight="bold" if x is grande else "normal", zorder=15,
                bbox=dict(facecolor="white", alpha=0.55, edgecolor="none", pad=0.6) if x is grande else None)


def _recuadro(ax, g, color, margen=0.25):
    from matplotlib.patches import Rectangle
    x0, y0, x1, y1 = g.bounds; w, h = max(x1 - x0, 0.02), max(y1 - y0, 0.02); m = max(w, h) * margen
    ax.add_patch(Rectangle((x0 - m, y0 - m), w + 2 * m, h + 2 * m, fill=False, edgecolor=color, lw=2.2, zorder=25))


def _mapa_division(ruta, titulo, fondo_items, items, foco, siguiente, cfg_u, fuente, paises=None, mar=False):
    plt = _plt(); colres = (cfg_u.get("colores") or {}).get("resaltado", "#E4572E"); colrec = (cfg_u.get("colores") or {}).get("recuadro", "#D90429")
    fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=220); ax.set_facecolor("#DCEEFB" if mar else "white")
    vista = _vista(ax, foco["geom"] if isinstance(foco, dict) else foco)
    for p in paises or []:
        _poligono(ax, p["geom"], facecolor="#ECEFF3", edgecolor="#9AA8B8", lw=0.6, zorder=1)
    for x in fondo_items:
        _poligono(ax, x["geom"], facecolor="#F4F6F8", edgecolor="#B9C5D2", lw=0.4, zorder=2)
    col = _colores(items)
    for x in items:
        es = siguiente is not None and x["u"] == siguiente["u"][:len(x["u"])]
        _poligono(ax, x["geom"], facecolor=colres if es else col[x["u"]], edgecolor="#5A6B7D", lw=0.7 if es else 0.5, zorder=3, alpha=0.95)
    grande = next((x for x in items if siguiente is not None and x["u"] == siguiente["u"][:len(x["u"])]), None)
    _etiquetas(ax, items, vista[:2], grande=grande)
    if paises:
        (x0, x1), (y0, y1) = vista[:2]
        for p in paises:
            if p["iso"] == "PER": continue
            c = p["geom"].intersection(box(x0, y0, x1, y1))
            if c.is_empty or c.area < (x1 - x0) * (y1 - y0) * 0.01: continue
            q = c.representative_point(); ax.text(q.x, q.y, p["n"], ha="center", va="center", fontsize=9, color="#6A7889", fontweight="bold", zorder=4)
    if mar:
        (x0, x1), (y0, y1) = vista[:2]
        ax.text(x0 + (x1 - x0) * 0.16, y0 + (y1 - y0) * 0.36, "OCÉANO\nPACÍFICO", ha="center", fontsize=9, color="#3D7DB8", style="italic", zorder=4)
    if siguiente is not None: _recuadro(ax, siguiente["geom"], colrec, 0.12)
    (x0, x1), (y0, y1), k = vista
    _norte(ax, x1 - (x1 - x0) * 0.07, y1 - (y1 - y0) * 0.16, (y1 - y0) * 0.07)
    _escala(ax, x0 + (x1 - x0) * 0.05, y0 + (y1 - y0) * 0.04, 111.32 / k, x1 - x0)
    _marco(ax, titulo, fuente)
    fig.tight_layout(pad=0.4); fig.savefig(ruta, dpi=220, facecolor="white"); plt.close(fig)
    return ruta


# ------------------------------------------------------------------ mapa 4: el local
def _tile_xy(lat, lon, z):
    n = 2 ** z; x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def _osm(lat0, lon0, lat1, lon1, z, cache, bajar=None):
    """Mosaico de OpenStreetMap del recuadro (con caché en disco). Devuelve (imagen PIL, x0, y0 en coordenadas de mosaico) o None."""
    from PIL import Image
    bajar = bajar or (lambda url: urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=10).read())
    xa, ya = _tile_xy(lat1, lon0, z); xb, yb = _tile_xy(lat0, lon1, z)
    tx0, tx1, ty0, ty1 = int(xa), int(xb), int(ya), int(yb)
    if (tx1 - tx0 + 1) * (ty1 - ty0 + 1) > 36: return None
    os.makedirs(cache, exist_ok=True); im = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256), "white")
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            f = os.path.join(cache, "%d_%d_%d.png" % (z, tx, ty))
            if not os.path.exists(f):
                try: datos = bajar("https://tile.openstreetmap.org/%d/%d/%d.png" % (z, tx, ty))
                except Exception: return None
                open(f, "wb").write(datos)
            im.paste(Image.open(f).convert("RGB"), ((tx - tx0) * 256, (ty - ty0) * 256))
    return im, tx0, ty0


def _mapa_local(ruta, titulo, U, cerco_xy, techos, cfg_u, salida, bajar=None):
    plt = _plt(); colc = (cfg_u.get("colores") or {}).get("cerco", "#FFD60A")
    fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=220)
    xs = [p[0] for p in cerco_xy]; ys = [p[1] for p in cerco_xy]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    lado = max(max(xs) - min(xs), max(ys) - min(ys)) * 2.2 + 60
    x0, x1, y0, y1 = cx - lado / 2, cx + lado / 2, cy - lado / 2, cy + lado / 2
    fondo, fuente = None, "Plano del proyecto"
    foto = cfg_u.get("foto") or {}
    if foto.get("ruta") and os.path.exists(foto["ruta"]) and all(k in foto for k in ("xmin", "ymin", "xmax", "ymax")):
        from PIL import Image
        ax.imshow(Image.open(foto["ruta"]).convert("RGB"), extent=(foto["xmin"], foto["xmax"], foto["ymin"], foto["ymax"]), zorder=0)
        fondo, fuente = "foto", foto.get("fuente") or "Imagen aérea del proyecto"
    elif U.get("georef") and cfg_u.get("osm", True):
        la_s, lo_w = utm_a_geo(x0, y0, U["zona"]); la_n, lo_e = utm_a_geo(x1, y1, U["zona"])
        z = 18 if lado < 400 else 17 if lado < 900 else 16
        r = _osm(la_s, lo_w, la_n, lo_e, z, os.path.join(salida, "_mapas_osm"), bajar)
        if r is not None:
            im, tx0, ty0 = r
            # cada esquina del recuadro UTM -> pixel del mosaico; el mosaico se dibuja en UTM con su caja (el giro de la cuadrícula es menor de 1°)
            def px(E, N):
                la, lo = utm_a_geo(E, N, U["zona"]); x, y = _tile_xy(la, lo, z); return (x - tx0) * 256, (y - ty0) * 256
            (pa, pb), (pc, pd) = px(x0, y1), px(x1, y0)
            ax.imshow(im.crop((int(pa), int(pb), int(pc), int(pd))), extent=(x0, x1, y0, y1), zorder=0)
            fondo, fuente = "osm", "© colaboradores de OpenStreetMap"
    if fondo is None:
        ax.set_facecolor("#F3F0E6")
        for t in techos or []:
            _poligono(ax, t, facecolor="#C9CED6", edgecolor="#5A6B7D", lw=0.6, zorder=2)
    _poligono(ax, Polygon(cerco_xy), facecolor="none", edgecolor=colc, lw=3.0, zorder=10)
    if fondo is None: _poligono(ax, Polygon(cerco_xy), facecolor="none", edgecolor="#0B2545", lw=0.8, zorder=11)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect(1)
    ax.text(cx, max(ys) + lado * 0.035, "ÁREA DEL PROYECTO", ha="center", fontsize=8.5, fontweight="bold", color="#0B2545", zorder=12,
            bbox=dict(facecolor=colc, edgecolor="none", pad=1.5, alpha=0.95))
    _norte(ax, x1 - lado * 0.07, y1 - lado * 0.16, lado * 0.07)
    _escala(ax, x0 + lado * 0.05, y0 + lado * 0.04, 0.001, lado)
    if U.get("georef"):
        ax.text(0.01, 0.995, "UTM WGS 84 - %dS\nE %.0f  N %.0f" % (U["zona"], U["este"], U["norte"]), transform=ax.transAxes, ha="left", va="top",
                fontsize=6.5, color="#0B2545", zorder=30, bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1))
    _marco(ax, titulo, fuente)
    fig.tight_layout(pad=0.4); fig.savefig(ruta, dpi=220, facecolor="white"); plt.close(fig)
    return ruta, fondo, [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)]


def titulos(U, cfg_u):
    t = list((cfg_u or {}).get("titulos") or [])
    base = [x.format(dep=U.get("departamento", ""), prov=U.get("provincia", ""), dist=U.get("distrito", "")) for x in TITULOS]
    return [t[i] if i < len(t) and t[i] else base[i] for i in range(4)]


def generar(salida, cerco_xy, techos, cfg, bajar=None):
    """Ubica el proyecto y dibuja los 4 mapas en salida/mapas_ubicacion. Devuelve el resultado de ubicar() con «mapas», «titulos», «fondo_local»."""
    cfg_u = cfg.get("ubicacion") or {}; pr = cfg.get("proyecto") or {}; mem = cfg.get("memoria") or {}
    texto = " ".join(str(x) for x in (pr.get("ubicacion"), mem.get("distrito"), mem.get("provincia"), mem.get("departamento"), mem.get("localidad")) if x)
    U = ubicar(cerco_xy, cfg_u, texto)
    U["titulos"] = titulos(U, cfg_u); U["mapas"] = []; U["fuente_limites"] = limites()["fuente"]
    if not U.get("ubigeo"): return U
    L = limites(); dist, prov, dep = U["_d"], U["_p"], U["_dp"]
    nombres = cfg_u.get("nombres") or {}
    ren = lambda lst: [dict(x, n=nombres.get(x["u"], x["n"])) for x in lst]
    carpeta = os.path.join(salida, "mapas_ubicacion"); os.makedirs(carpeta, exist_ok=True)
    fte = L.get("fuente_corta") or "Límites: INEI"
    peru = MultiPolygon([p for x in L["departamentos"] for p in (x["geom"].geoms if hasattr(x["geom"], "geoms") else [x["geom"]])])
    U["mapas"].append(_mapa_division(os.path.join(carpeta, "MAPA_01_PERU.png"), U["titulos"][0], [], ren(L["departamentos"]),
                                     peru, dep, cfg_u, fte + "; países: Natural Earth", paises=L["paises"], mar=True))
    provs = ren([x for x in L["provincias"] if x["u"][:2] == dep["u"]])
    vecinos = [x for x in L["departamentos"] if x["u"] != dep["u"] and x["geom"].intersects(dep["geom"].buffer(0.2))]
    U["mapas"].append(_mapa_division(os.path.join(carpeta, "MAPA_02_DEPARTAMENTO.png"), U["titulos"][1], vecinos, provs, dep["geom"], prov, cfg_u, fte))
    dists = ren([x for x in L["distritos"] if x["u"][:4] == prov["u"]])
    vecinas = [x for x in L["provincias"] if x["u"] != prov["u"] and x["geom"].intersects(prov["geom"].buffer(0.05))]
    U["mapas"].append(_mapa_division(os.path.join(carpeta, "MAPA_03_PROVINCIA.png"), U["titulos"][2], vecinas, dists, prov["geom"], dist, cfg_u, fte))
    ruta4, fondo, U["extension_local"] = _mapa_local(os.path.join(carpeta, "MAPA_04_LOCAL.png"), U["titulos"][3], U, cerco_xy, techos, cfg_u, salida, bajar)
    U["mapas"].append(ruta4); U["fondo_local"] = fondo
    if fondo is None and U.get("georef") and cfg_u.get("osm", True) and not (cfg_u.get("foto") or {}).get("ruta"):
        U["avisos"].append("Mapa 4 sin fondo de calles (sin internet en este cálculo): sale el plano del sitio. Con internet se usa OpenStreetMap; "
                           "también puede cargar su foto aérea en el editor de Ubicación.")
    for k in ("_d", "_p", "_dp"): U.pop(k, None)
    return U


def guardar_sitio(salida, cerco_xy, techos):
    """Cerco y techos del último plano leído (mapas_ubicacion/sitio.json): el editor de Ubicación rehace los mapas sin leer el plano."""
    carpeta = os.path.join(salida, "mapas_ubicacion"); os.makedirs(carpeta, exist_ok=True)
    polis = []
    for t in techos or []:
        for p in (t.geoms if hasattr(t, "geoms") else [t]):
            if isinstance(p, Polygon) and not p.is_empty: polis.append([[round(x, 2), round(y, 2)] for x, y in p.exterior.coords])
    json.dump({"cerco": [[round(x, 3), round(y, 3)] for x, y in cerco_xy], "techos": polis},
              open(os.path.join(carpeta, "sitio.json"), "w", encoding="utf-8"))


def leer_sitio(salida):
    r = os.path.join(salida, "mapas_ubicacion", "sitio.json")
    if not os.path.exists(r): return None, None
    d = json.load(open(r, encoding="utf-8"))
    return [tuple(p) for p in d["cerco"]], [Polygon(p) for p in d["techos"] if len(p) >= 4]


def buscar(texto, maximo=25):
    """Distritos cuyo nombre (o el de su provincia o departamento, o el ubigeo) contiene el texto."""
    t = _norm(texto)
    if len(t) < 2: return []
    L = limites(); out = []
    for d in L["distritos"]:
        j = _jerarquia(d, {})
        cad = " ".join(_norm(j[k]) for k in ("distrito", "provincia", "departamento"))
        if t in d["u"] or all(p in cad for p in t.split()):
            out.append(dict(ubigeo=d["u"], **{k: j[k] for k in ("distrito", "provincia", "departamento")}))
            if len(out) >= maximo: break
    return out


def resumen(U):
    """Versión para resultado.json (sin geometrías)."""
    return {k: v for k, v in U.items() if not k.startswith("_")}
