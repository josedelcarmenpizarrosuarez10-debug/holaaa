"""Escena para el visor de DrenIE (escena.json): el plano leido, el mapa de superficies, las cunetas, el cerco y la caida de
techos, en coordenadas locales (origen en la esquina del cerco) y en centimetros enteros con diferencias sucesivas, para que
pese poco. El visor suma el origen para volver a coordenadas reales (UTM).
"""
import json

import ezdxf.colors
from shapely.geometry import LineString

# tolerancia de simplificacion por capa (m); las demas 0.02 m (sin cambio visible a la escala del plano)
TOL = {"ARBOLES": 0.15, "C-TOPO": 0.10, "LTOPO": 0.10}


def _hex(aci):
    try:
        r, g, b = ezdxf.colors.aci2rgb(int(aci))
    except Exception:
        r, g, b = (200, 200, 200)
    if (r, g, b) == (255, 255, 255) or aci == 7: r, g, b = (225, 225, 225)       # blanco/negro de AutoCAD sobre fondo oscuro
    return "#%02x%02x%02x" % (r, g, b)


def _cod(pts, ox, oy):
    """Lista plana de enteros (cm): primer punto absoluto (local) y luego diferencias."""
    out, px, py = [], None, None
    for x, y in pts:
        cx, cy = int(round((x - ox) * 100)), int(round((y - oy) * 100))
        if px is None: out += [cx, cy]
        else:
            if cx == px and cy == py: continue
            out += [cx - px, cy - py]
        px, py = cx, cy
    return out


def _anillos(g, ox, oy):
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.is_empty: continue
        out.append([_cod(list(p.exterior.coords), ox, oy)] + [_cod(list(h.coords), ox, oy) for h in p.interiors])
    return out


def _punto(g, ox, oy):
    """Un punto dentro del area (el visor lo usa para asignarle su tipo)."""
    p = g.representative_point(); return [round(p.x - ox, 2), round(p.y - oy, 2)]


def escribir(ruta, B, S, M, ejes, curvas, proyecto, aguas=None):
    x0, y0, x1, y1 = S.cerco.buffer(40).bounds
    ox, oy = round(S.cerco.bounds[0], 0), round(S.cerco.bounds[1], 0)
    capas = []
    for capa, ents in sorted(B["geo"].items()):
        grupos = {}
        tol = TOL.get(capa, 0.02)
        for pts, cl, col, z in ents:
            if not any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in pts[:: max(1, len(pts) // 8)]): continue
            if len(pts) > 4 and tol > 0:
                ls = LineString(list(pts) + ([pts[0]] if cl else [])).simplify(tol)
                pp = list(ls.coords)
                if cl and len(pp) > 1: pp = pp[:-1]
            else:
                pp = list(pts)
            if len(pp) < 2: continue
            g = grupos.setdefault(col, {"color": _hex(col), "p": [], "c": []})
            g["p"].append(_cod(pp, ox, oy)); g["c"].append(1 if cl else 0)
        if grupos:
            capas.append({"nombre": capa, "grupos": list(grupos.values()), "n": sum(len(g["p"]) for g in grupos.values())})
    caras = [{"id": c["id"], "tipo": c["tipo"], "nombre": c.get("nombre", ""), "fuente": c["fuente"],
              "area": round(c["geom"].area, 2), "p": _punto(c["geom"], ox, oy), "a": _anillos(c["geom"], ox, oy)} for c in M.caras]
    textos = [{"t": s.split("\n")[0][:60], "x": round(x - ox, 2), "y": round(y - oy, 2), "h": round(h or 0.3, 2), "c": capa}
              for capa, s, x, y, h, col in B["txt"] if x0 <= x <= x1 and y0 <= y <= y1 and s.strip()]
    flechas = []
    for ag in aguas or []:
        c = ag["poligono"].representative_point()
        if ag["tipo"] == "flecha": dx, dy = ag["flecha"]
        else:
            al = ag["alero"]; q = al.interpolate(al.project(c)); L = max(1e-6, ((q.x - c.x) ** 2 + (q.y - c.y) ** 2) ** 0.5)
            dx, dy = (q.x - c.x) / L, (q.y - c.y) / L
        flechas.append({"x": round(c.x - ox, 2), "y": round(c.y - oy, 2), "dx": round(dx, 3), "dy": round(dy, 3), "usuario": ag["tipo"] == "flecha"})
    esc = {"version": 1, "proyecto": proyecto, "origen": [ox, oy], "unidad": "cm",
           "cerco": _cod(list(S.cerco.exterior.coords), ox, oy),
           "ejes": [_cod(p, ox, oy) for p in ejes], "capas": capas, "caras": caras, "textos": textos, "caidas": flechas,
           "C": S.P["C"], "cuadre": M.cuadre}
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(esc, f, ensure_ascii=False, separators=(",", ":"))
    return ruta
