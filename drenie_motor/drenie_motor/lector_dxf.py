"""Lectura del plano DXF del usuario.

Abre el DXF (tambien un ZIP con el DXF, o un ZIP partido en varias partes), explota los bloques hasta 6 niveles, lleva todo a
coordenadas reales y guarda una base reducida por capa: polilineas (puntos, cerrada, color, elevacion) y textos (texto, x, y,
altura). La base se guarda en un archivo .pkl junto al proyecto para no volver a leer un DXF de cientos de MB.
"""
import os
import io
import zipfile
import pickle
import hashlib

import ezdxf
from ezdxf import recover

PROF_MAX = 6


def _abrir(ruta):
    if ruta.lower().endswith(".zip") or os.path.isdir(ruta):
        partes = sorted(os.path.join(ruta, f) for f in os.listdir(ruta)) if os.path.isdir(ruta) else [ruta]
        datos = b"".join(open(p, "rb").read() for p in partes)
        with zipfile.ZipFile(io.BytesIO(datos)) as z:
            nombre = next(n for n in z.namelist() if n.lower().endswith(".dxf"))
            texto = z.read(nombre)
        doc, auditor = recover.read(io.BytesIO(texto))
        return doc
    try:
        return ezdxf.readfile(ruta)
    except ezdxf.DXFStructureError:
        doc, auditor = recover.readfile(ruta)
        return doc


def _color(e, doc, color_padre):
    c = e.dxf.get("color", 256)
    if c == 256:
        capa = doc.layers.get(e.dxf.layer) if doc.layers.has_entry(e.dxf.layer) else None
        return abs(capa.color) if capa is not None else 7
    if c == 0: return color_padre
    return c


def leer(ruta, capas=None):
    """Base del sitio: {"geo": {capa: [(pts[(x, y)], cerrada, color, z)]}, "txt": [(capa, texto, x, y, altura, color)],
    "resumen": {...}}. Si se da `capas`, solo se guardan esas capas (y todos los textos)."""
    doc = _abrir(ruta)
    geo, txt, cuenta = {}, [], {}

    def guardar_pl(capa, pts, cerrada, color, z):
        if capas and capa not in capas: return
        if len(pts) < 2: return
        geo.setdefault(capa, []).append((pts, cerrada, color, z))
        cuenta[capa] = cuenta.get(capa, 0) + 1

    def recorrer(entidades, prof, capa_padre, color_padre):
        for e in entidades:
            t = e.dxftype()
            capa = e.dxf.get("layer", "0")
            if capa == "0" and capa_padre: capa = capa_padre
            color = _color(e, doc, color_padre)
            try:
                if t == "INSERT":
                    if prof < PROF_MAX:
                        recorrer(list(e.virtual_entities()), prof + 1, capa, color)
                    for a in e.attribs:
                        p = a.dxf.insert; txt.append((capa, a.dxf.text, p.x, p.y, a.dxf.height, color))
                elif t == "LWPOLYLINE":
                    guardar_pl(capa, [(p[0], p[1]) for p in e.get_points("xy")], bool(e.closed), color, float(e.dxf.elevation))
                elif t == "POLYLINE":
                    vs = [v.dxf.location for v in e.vertices]
                    if vs: guardar_pl(capa, [(v.x, v.y) for v in vs], bool(e.is_closed), color, float(vs[0].z))
                elif t == "LINE":
                    a, b = e.dxf.start, e.dxf.end
                    guardar_pl(capa, [(a.x, a.y), (b.x, b.y)], False, color, float(a.z) if abs(a.z - b.z) < 1e-6 else None)
                elif t in ("ARC", "CIRCLE", "ELLIPSE", "SPLINE"):
                    pts = [(p.x, p.y) for p in e.flattening(0.05)]
                    guardar_pl(capa, pts, t == "CIRCLE", color, None)
                elif t == "HATCH":
                    # cada contorno del sombreado como polilinea cerrada (sirve para la leyenda de colores)
                    for camino in e.paths.rendering_paths(e.dxf.hatch_style):
                        pts = [(p.x, p.y) for p in camino.flattening(0.05)] if hasattr(camino, "flattening") else []
                        if not pts:
                            from ezdxf.path import from_hatch_boundary_path
                            pts = [(p.x, p.y) for p in from_hatch_boundary_path(camino).flattening(0.05)]
                        guardar_pl(capa, pts, True, color, None)
                        cuenta["_hatch"] = cuenta.get("_hatch", 0) + 1
                elif t == "TEXT":
                    p = e.dxf.insert; txt.append((capa, e.dxf.text, p.x, p.y, e.dxf.height, color))
                elif t == "MTEXT":
                    p = e.dxf.insert; txt.append((capa, e.plain_text(), p.x, p.y, e.dxf.char_height, color))
            except Exception:
                cuenta["_no_leidas"] = cuenta.get("_no_leidas", 0) + 1

    recorrer(list(doc.modelspace()), 0, "", 7)
    return {"geo": geo, "txt": txt, "resumen": {"archivo": os.path.basename(ruta), "capas": cuenta, "textos": len(txt)}}


def base(ruta, cache=None, capas=None):
    """Lee el DXF o la base guardada (si el DXF no cambio)."""
    huella = hashlib.sha1(("%s|%s|%s" % (os.path.abspath(ruta), os.path.getsize(ruta) if os.path.isfile(ruta) else 0,
                                          os.path.getmtime(ruta))).encode()).hexdigest()
    if cache and os.path.exists(cache):
        try:
            B = pickle.load(open(cache, "rb"))
            if B.get("huella") == huella: return B
        except Exception:
            pass
    B = leer(ruta, capas)
    B["huella"] = huella
    if cache:
        os.makedirs(os.path.dirname(os.path.abspath(cache)), exist_ok=True)
        pickle.dump(B, open(cache, "wb"))
    return B


def capas_disponibles(B):
    """Lista de capas con cantidad de entidades y colores (para que el usuario elija en DrenIE)."""
    out = []
    for capa, ents in sorted(B["geo"].items()):
        colores = {}
        for pts, cl, col, z in ents: colores[col] = colores.get(col, 0) + 1
        out.append({"capa": capa, "entidades": len(ents), "cerradas": sum(1 for e in ents if e[1]), "colores": colores})
    return out
