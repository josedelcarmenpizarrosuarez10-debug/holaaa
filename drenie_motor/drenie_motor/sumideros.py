"""Sumideros de piso con su tuberia PVC 4" a la cuneta (conocimiento/07_componentes_complementarios.md, seccion 5).

Regla del usuario (24-10-2026): solo en areas libres pavimentadas sin cobertura (patios libres); nunca en areas verdes, veredas
ni bajo techo. Tipos permitidos en "sumidero_tipos" (por defecto: patio y estacionamiento o patio de maniobra).
- Zona: areas libres contiguas del mapa de superficies.
- La parte de la zona a menos de 'dist_cuneta' (8 m) de una cuneta escurre directo a ella por la pendiente del piso; el resto
  necesita sumideros. N.° de sumideros = el mayor de: area lejana / area que atiende uno (capacidad del tubo 4" a S 1 %) y
  area lejana / area de influencia (radio 'radio' = 6 m). Se ubican en el centro de su parte (k-medias sobre celdas de 1 m2).
- Caja de concreto 0.45 x 0.45 con rejilla de platinas 0.25 x 0.25 al ras del piso; salida PVC 4" con un solo codo de 90 (sin
  sifon); tuberia PVC 4" recta a la cuneta mas cercana con S >= 1 %, que debe llegar al muro de la cuneta por encima de su cota de
  fondo (ninguna tuberia enterrada bajo la cuneta: si no llega, aviso).
- Si el proyecto trae sumideros del visor ("sumideros": [{"x", "y"}]) se usan esos.
"""
import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

PARAM = {"dist_cuneta": 8.0, "radio": 6.0, "S_tubo": 0.01, "S_min": 0.005, "n_tubo": 0.010, "D_tubo": 0.1016, "prof_caja": 0.23,
         "caja": 0.45, "rejilla": 0.25, "codos90": 1}


def _q_tubo(tp):
    D = tp["D_tubo"]; A = math.pi * D * D / 4; R = D / 4
    return A * R ** (2 / 3) * math.sqrt(tp["S_tubo"]) / tp["n_tubo"] * 1000.0


def _kmedias(X, k, it=30):
    rng = np.random.default_rng(0)
    c = X[rng.choice(len(X), k, replace=False)] if len(X) >= k else X.copy()
    for _ in range(it):
        d = ((X[:, None, :] - c[None, :, :]) ** 2).sum(2); a = d.argmin(1)
        nc = np.array([X[a == j].mean(0) if (a == j).any() else c[j] for j in range(len(c))])
        if np.allclose(nc, c): break
        c = nc
    return c, a


def zonas(mapa, tipos):
    g = unary_union([c["geom"] for c in mapa.caras if c["tipo"] in tipos])
    if g.is_empty: return []
    return [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.area >= 20.0]       # retazos chicos escurren a la cuneta


def proponer(mapa, ejes_lineas, P, I, cfg):
    """Ubicacion propuesta (sin la red final): lista de {"x", "y", "zona", "A_m2"}; ejes_lineas: lineas de cuneta."""
    tp = dict(PARAM); tp.update(cfg.get("sumidero_parametros", {}))
    tipos = cfg.get("sumidero_tipos", ["patio", "estacionamiento"])
    q_m2 = 0.88 * I / 3.6e6 * P["FS"] * 1000.0
    A_cap = _q_tubo(tp) / q_m2 if q_m2 > 0 else 1e9
    red = unary_union([LineString(l) for l in ejes_lineas if len(l) > 1])
    out = []
    for iz, z in enumerate(zonas(mapa, tipos)):
        x0, y0, x1, y1 = z.bounds
        xs = np.arange(math.floor(x0), math.ceil(x1)) + 0.5; ys = np.arange(math.floor(y0), math.ceil(y1)) + 0.5
        XX, YY = np.meshgrid(xs, ys); X = np.c_[XX.ravel(), YY.ravel()]
        X = X[shapely.contains_xy(z, X[:, 0], X[:, 1])]
        if not len(X): continue
        d = shapely.distance(red, shapely.points(X)) if not red.is_empty else np.full(len(X), 1e9)
        lejos = X[d > tp["dist_cuneta"]]
        if len(lejos) < 10: continue                                     # menos de 10 m2 lejos: escurre a la cuneta
        A = float(len(lejos))
        k = max(1, math.ceil(A / A_cap - 1e-9), math.ceil(A / (math.pi * tp["radio"] ** 2) - 1e-9))
        cs, a = _kmedias(lejos, k)
        for j, c in enumerate(cs):
            p = Point(c)
            if not z.buffer(-0.40).contains(p):                       # dentro de la zona, lejos de su borde
                q = shapely.ops.nearest_points(z.buffer(-0.40) if not z.buffer(-0.40).is_empty else z, p)[0]; c = (q.x, q.y)
            out.append({"x": round(float(c[0]), 3), "y": round(float(c[1]), 3), "zona": iz + 1, "A_m2": float((a == j).sum())})
    return out, {"A_cap": A_cap, "q_m2": q_m2, "tp": tp, "tipos": tipos}


def _cf_en(R, eje, punto):
    """Cota de fondo y borde de la cuneta en el punto del eje mas cercano."""
    r = next(x for x in R["ramales"] if x["codigo"] == eje)
    ls = LineString([R["nudos"][n] for n in r["nudos"]]); s = ls.project(Point(punto))
    Pf = r["perfil"]
    for i in range(1, len(Pf)):
        if Pf[i][0] >= s - 1e-9:
            a, b = Pf[i - 1], Pf[i]; t = 0 if b[0] == a[0] else (s - a[0]) / (b[0] - a[0])
            return a[1] + t * (b[1] - a[1]), a[2] + t * (b[2] - a[2])
    return Pf[-1][1], Pf[-1][2]


def calcular(mapa, sitio, R, P, I, cfg, descargas=(), V=None):
    from . import llegada
    tir = llegada.tirantes(V, P, R) if V else {}
    anc = llegada.anchos(V) if V else {}
    ejes_l = [[R["nudos"][n] for n in r["nudos"]] for r in R["ramales"]]
    prop, K = proponer(mapa, ejes_l, P, I, cfg)
    tp = K["tp"]; Qt = _q_tubo(tp)
    pts = cfg.get("sumideros") or prop
    Nn = R["nudos"]
    # el tubo no llega al tramo que sale por el cerco (descarga) ni a pedazos cortos (chaflanes)
    segs = [(r["codigo"], LineString([Nn[t["de"]], Nn[t["a"]]]), "%s|%s|%s" % (r["codigo"], t["de"], t["a"])) for r in R["ramales"] for t in r["tramos"]
            if t["origen"] != "pase" and t["a"] not in descargas and math.dist(Nn[t["de"]], Nn[t["a"]]) > 1.0]
    libres = unary_union(zonas(mapa, K["tipos"]))
    sums, avisos = [], []
    for i, s in enumerate(pts):
        p = Point(s["x"], s["y"])
        if not libres.is_empty and not libres.buffer(0.5).contains(p):
            avisos.append("El sumidero en (%.2f, %.2f) no esta en un area libre pavimentada sin cobertura: revisar (no van en areas verdes, "
                          "veredas ni bajo techo)." % (s["x"], s["y"]))
        manual = bool(cfg.get("sumideros"))

        def tubo(p):
            # la cuneta mas cercana; si alli el tubo no llega sobre el agua, otra cuneta a no mas de 5 m adicionales donde si llegue
            dmin = min(e[1].distance(p) for e in segs)
            r0 = None
            for e in sorted((e for e in segs if e[1].distance(p) <= dmin + 5.0), key=lambda e: e[1].distance(p)):
                r = _tubo_a(p, e)
                if r[7]: return r
                r0 = r0 or r
            return r0

        def _tubo_a(p, e):
            eje, ln, clave = e
            q = ln.interpolate(ln.project(p)); L = max(p.distance(q) - anc.get(clave, P.get("b_int", 0.30)) / 2.0, 0.10)
            nct, cf = _cf_en(R, eje, (q.x, q.y)); y = tir[clave]((q.x, q.y)) if clave in tir else 0.10
            z_piso = sitio.rasante(p.x, p.y); z_sal = z_piso - tp["prof_caja"] - tp["D_tubo"]
            # 1 %; si no llega sobre el agua de la cuneta + 5 cm, el minimo (0.5 %)
            S_, zl, nivel, ok = llegada.resolver(z_sal, L, cf, y, (tp["S_tubo"], tp["S_min"]))
            return eje, q, L, cf, z_piso, z_sal, S_, ok, clave, y, nivel
        eje, q, L, cf, z_piso, z_sal, S_t, ok, tramo, yv, nivel = tubo(p)
        if not ok and not manual:                                       # propuesta del programa: se acerca a la cuneta hasta que llegue
            for k in range(1, 40):
                p2 = Point(p.x + (q.x - p.x) * k / 40, p.y + (q.y - p.y) * k / 40)
                if libres.buffer(-0.40).contains(p2):                  # sin salir del area libre (nunca a area verde ni vereda)
                    r = tubo(p2)
                    if r[7]: p = p2; eje, q, L, cf, z_piso, z_sal, S_t, ok, tramo, yv, nivel = r; break
        z_lleg = z_sal - S_t * L
        # profundidad que necesita la cuneta en la llegada para recibir el tubo al 0.5 % sobre el agua (la usa el motor para profundizar)
        h_req = round(llegada.h_req(sitio.rasante(q.x, q.y), z_sal, L, yv, tp["S_min"]), 3)
        A = s.get("A_m2") or (math.pi * tp["radio"] ** 2)
        Qs = K["q_m2"] * A
        if ok and S_t < tp["S_tubo"] - 1e-9:
            avisos.append("S-%02d: con %.1f %% el tubo llegaria bajo el agua de %s; se uso la pendiente minima de %.1f %%." % (i + 1, 100 * tp["S_tubo"], eje, 100 * S_t))
        if not ok:
            avisos.append("S-%02d: la tuberia llega a %.3f, bajo el nivel del agua de %s (%.3f = cota de fondo %.3f + tirante + 0.05): "
                          "se profundiza ese tramo o se acerca el sumidero a la cuneta." % (i + 1, z_lleg, eje, nivel, cf))
        if Qs > Qt:
            avisos.append("S-%02d recibe %.2f l/s, mas que su tubo de 4\" (%.2f l/s): agregar otro sumidero en esa zona." % (i + 1, Qs, Qt))
        sums.append({"sumidero": "S-%02d" % (i + 1), "x": round(p.x, 3), "y": round(p.y, 3), "zona": s.get("zona"), "A_m2": round(A, 1),
                     "Q_ls": round(Qs, 2), "cuneta": eje, "hacia": [round(q.x, 3), round(q.y, 3)], "L_tubo_m": round(L, 2), "S_tubo_pct": round(100 * S_t, 2),
                     "z_piso": round(z_piso, 3), "z_salida": round(z_sal, 3), "z_llegada": round(z_lleg, 3), "cf_cuneta": round(cf, 3),
                     "tirante_cuneta": round(yv, 3), "nivel_min": round(nivel, 3), "llega": llegada.estado(ok), "codos90": tp["codos90"],
                     "tramo": tramo, "h_req_cuneta": h_req})
    met = {"sumideros_und": len(sums), "tuberia_4_m": round(sum(x["L_tubo_m"] for x in sums), 2), "codo90_und": sum(x["codos90"] for x in sums), "tee_und": 0}
    return {"sumideros": sums, "metrado": met, "avisos": avisos,
            "criterios": {"tipos": K["tipos"], "Q_tubo_4_ls": round(Qt, 2), "A_por_sumidero_m2": round(K["A_cap"], 1), "parametros": tp,
                          "ubicacion": "visor (proyectista)" if cfg.get("sumideros") else "propuesta del programa"}}


def dibujar(lam, Sm, capa_caja="SUMIDERO", capa_tubo="SUMIDERO-TUBO"):
    tp = Sm["criterios"]["parametros"]
    for s in Sm["sumideros"]:
        x, y = s["x"], s["y"]; c, r = tp["caja"] / 2, tp["rejilla"] / 2
        lam.poli([(x - c, y - c), (x + c, y - c), (x + c, y + c), (x - c, y + c)], capa_caja, cerrada=True)
        lam.poli([(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)], capa_caja, cerrada=True)
        for k in range(1, 10):
            xx = x - r + k * tp["rejilla"] / 10; lam.linea((xx, y - r), (xx, y + r), capa_caja)
        lam.linea((x, y), tuple(s["hacia"]), capa_tubo)


def hoja(wb, Sm):
    from openpyxl.styles import Font
    ws = wb.create_sheet("SUMIDEROS")
    ws["A1"] = "SUMIDEROS DE PISO Y TUBERIA PVC 4\" A LA CUNETA (solo areas libres sin cobertura)"; ws["A1"].font = Font(bold=True, size=12)
    enc = ["SUMIDERO", "ZONA", "AREA (m2)", "Q (l/s)", "CUNETA", "TUBERIA (m)", "CODO 90", "NIVEL PISO", "SALIDA", "LLEGADA", "C.F. CUNETA",
           "TIRANTE", "NIVEL MINIMO (+5 cm)", "LLEGA"]
    for j, h in enumerate(enc): ws.cell(3, 1 + j, h).font = Font(bold=True)
    for i, s in enumerate(Sm["sumideros"]):
        for j, v in enumerate([s["sumidero"], s["zona"], s["A_m2"], s["Q_ls"], s["cuneta"], s["L_tubo_m"], s["codos90"], s["z_piso"], s["z_salida"],
                               s["z_llegada"], s["cf_cuneta"], s.get("tirante_cuneta"), s.get("nivel_min"), s["llega"]]):
            ws.cell(4 + i, 1 + j, v)
    f = 4 + len(Sm["sumideros"])
    m = Sm["metrado"]
    ws.cell(f, 1, "TOTAL").font = Font(bold=True); ws.cell(f, 6, m["tuberia_4_m"]).font = Font(bold=True); ws.cell(f, 7, m["codo90_und"]).font = Font(bold=True)
