"""Exportación de la red a EPA SWMM 5 (archivo .inp, unidades SI, caudales en L/s, tránsito por onda dinámica).

- Nudos: los de la red (cota de fondo = la menor de los tramos que llegan o salen; profundidad = hasta el borde de la
  cuneta) y uno más en cada caída de fondo dentro de un tramo; las descargas por el cerco son descargas libres (OUTFALL FREE).
- Conductos: cada tramo de cuneta, partido en las caídas; sección rectangular abierta (rejilla) o cerrada (tapada), con el
  ancho libre del diseño y la altura libre mayor del tramo; desfases de entrada y salida = cota de fondo − cota del nudo.
- Subcuencas: una por tramo con el área que se le suma en ese tramo (techos y pisos impermeables, área verde permeable con
  infiltración de Horton), descarga al nudo inicial del tramo.
- Lluvia: hietograma de bloques alternos de la curva IDF del proyecto (hietograma.py) con bloques del tiempo de concentración
  (mínimo 10 min), de modo que el bloque pico es la intensidad de diseño; pluviómetro de intensidad.
"""
import math

from . import hietograma
from .perfil_flujo import _es_caida


def simular(inp):
    """Corre el archivo con el motor de EPA SWMM 5 (swmm-toolkit) y resume el informe: continuidad, caudal pico en cada descarga,
    nudos que rebalsan y tramos que se llenan. None si el motor de SWMM no está instalado."""
    try:
        from swmm.toolkit import solver
    except ImportError:
        return None
    import os
    base = os.path.splitext(inp)[0]; rpt, out = base + ".rpt", base + ".out"
    solver.swmm_open(inp, rpt, out); solver.swmm_start(1)                 # pasos sin mensajes en pantalla
    while solver.swmm_step() > 0: pass
    solver.swmm_end(); solver.swmm_report(); solver.swmm_close()
    if os.path.exists(out): os.remove(out)
    txt = open(rpt, encoding="latin-1").read().splitlines()

    def tabla(titulo):
        i = next((k for k, l in enumerate(txt) if titulo in l), None)
        if i is None: return []
        filas, guiones = [], 0
        for l in txt[i + 1:]:
            if l.strip() and set(l.strip()) == {"-"}:
                guiones += 1
                if guiones == 3: break
                continue
            if guiones == 2 and not l.strip() and filas: break                # la tabla termina en la primera linea en blanco
            if guiones == 2 and l.strip(): filas.append(l.split())
            if guiones < 2 and ("No nodes" in l or "No conduits" in l): break
        return filas
    cont = [float(l.split()[-1]) for l in txt if "Continuity Error (%)" in l]
    desc = [{"D": f[0], "Q_max_ls": float(f[3]), "volumen_m3": round(float(f[4]) * 1000, 1)} for f in tabla("Outfall Loading Summary") if f[0] != "System"]
    rebalsa = [{"nudo": f[0], "horas": float(f[1]), "Q_ls": float(f[2]), "hora": f[4], "volumen_m3": round(float(f[5]) * 1000, 2)}
               for f in tabla("Node Flooding Summary")]
    llenos = [{"tramo": f[0], "horas_lleno": float(f[1])} for f in tabla("Conduit Surcharge Summary") if len(f) >= 6 and float(f[1]) > 0]
    return {"motor": "EPA SWMM %s" % solver.swmm_version_info() if hasattr(solver, "swmm_version_info") else "EPA SWMM 5",
            "continuidad_escorrentia_pct": cont[0] if cont else None, "continuidad_transito_pct": cont[1] if len(cont) > 1 else None,
            "descargas": desc, "rebalses": rebalsa, "volumen_rebalse_m3": round(sum(r["volumen_m3"] for r in rebalsa), 2),
            "tramos_llenos": llenos, "informe": rpt}


def _nombre(s):
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in str(s))


def exportar(ruta, C, V, P, ll, Rh=None, proyecto=None, duracion=120, dt=None):
    N = C["nudos"]; ram = [r for r in C["ramales"] if r.get("tramos")]
    fila = {(f["eje"], f["de"], f["a"]): f for f in V["hidraulica"]}
    interior = {n for r in ram for n in r["nudos"][:-1]}
    salidas = {r["nudos"][-1] for r in ram if r["nudos"][-1] not in interior}
    inv, prof, xy = {}, {}, {}
    conductos, subcuencas = [], []

    def nudo(n, cf, ras, p):
        inv[n] = min(inv.get(n, cf), cf); prof[n] = max(prof.get(n, ras), ras); xy.setdefault(n, p)     # prof: borde más alto

    for r in ram:
        cod = r["codigo"]; pf = r["perfil"]; s0 = 0.0
        hijos = {}
        for q in ram:
            if q["codigo"] != cod and q["nudos"][-1] in r["nudos"][1:-1]: hijos.setdefault(q["nudos"][-1], []).append(q["codigo"])
        A_ant = [0.0, 0.0, 0.0]
        for t in r["tramos"]:
            f = fila.get((cod, t["de"], t["a"])) or {}
            b = f.get("b", P["b_int"]); s1 = s0 + t["L"]
            pts = [p for p in pf if s0 - 1e-6 <= p[0] <= s1 + 1e-6]
            # caídas dentro del tramo: nudo intermedio al pie de la caída
            cortes = [(s0, t["de"], t["cf_de"], t["ras_de"])]
            for a, c in zip(pts[:-1], pts[1:]):
                if _es_caida({"s": a[0], "z": a[2]}, {"s": c[0], "z": c[2]}):
                    k = len(cortes); nm = "%s_C%d_%s" % (cod, k, t["de"])
                    cortes.append((c[0], nm, c[2], c[1], a[2]))
            cortes.append((s1, t["a"], t["cf_a"], t["ras_a"]))
            pa = N[t["de"]][:2]; pb = N[t["a"]][:2]
            for j, (u, w) in enumerate(zip(cortes[:-1], cortes[1:])):
                L = max(w[0] - u[0], 0.1); k = (u[0] - s0) / max(t["L"], 1e-6)
                p_u = (pa[0] + k * (pb[0] - pa[0]), pa[1] + k * (pb[1] - pa[1]))
                cf_sal = u[2]
                cf_lleg = w[4] if len(w) > 4 else w[2]                       # fondo justo antes de la caída
                nudo(u[1], cf_sal, u[3], p_u)
                kk = (w[0] - s0) / max(t["L"], 1e-6)
                nudo(w[1], w[2], w[3], (pa[0] + kk * (pb[0] - pa[0]), pa[1] + kk * (pb[1] - pa[1])))
                hl = max(t["h_de"], t["h_a"]) - (P["e_tapa"] if t.get("L_tapado", 0) > t["L"] / 2 else 0.0)
                forma = "RECT_CLOSED" if t.get("L_tapado", 0) > t["L"] / 2 else "RECT_OPEN"
                conductos.append({"nombre": _nombre("%s_%s_%s%s" % (cod, t["de"], t["a"], "_%d" % j if len(cortes) > 2 else "")),
                                  "de": u[1], "a": w[1], "L": L, "cf_de": cf_sal, "cf_a": cf_lleg, "forma": forma, "h": max(hl, 0.05), "b": b})
            # área que se suma en el tramo (las acumuladas menos lo que traen los ejes que llegan a su nudo inicial)
            A = [f.get("A_techo_m2", 0.0), f.get("A_pisos_m2", 0.0), f.get("A_verde_m2", 0.0)]
            ent = [0.0, 0.0, 0.0]
            for h_ in hijos.get(t["de"], []):
                q = next(x for x in ram if x["codigo"] == h_); ft = fila.get((h_, q["tramos"][-1]["de"], q["tramos"][-1]["a"])) or {}
                ent = [ent[0] + ft.get("A_techo_m2", 0.0), ent[1] + ft.get("A_pisos_m2", 0.0), ent[2] + ft.get("A_verde_m2", 0.0)]
            dA = [max(0.0, A[i] - A_ant[i] - ent[i]) for i in range(3)]
            if sum(dA) > 0.5:
                subcuencas.append({"nombre": _nombre("S_%s_%s" % (cod, t["de"])), "salida": t["de"], "A": sum(dA),
                                   "imp": 100.0 * (dA[0] + dA[1]) / sum(dA), "ancho": max(1.0, sum(dA) / 20.0), "p": pa})
            A_ant = A; s0 = s1
    for c in conductos:                                                    # el nudo llega a la corona de sus conductos (como SWMM)
        prof[c["de"]] = max(prof[c["de"]], c["cf_de"] + c["h"]); prof[c["a"]] = max(prof[c["a"]], c["cf_a"] + c["h"])
    H = hietograma.diseno(ll, Rh, duracion) if dt is None else hietograma.bloques_alternos(ll, Rh, duracion, dt)
    dt = H["dt_min"]
    fin = len(H["intensidades"]) * dt + 60
    nom = (proyecto or {}).get("nombre", "Red de cunetas")
    L = []
    w = L.append
    w("[TITLE]\n;;Red de cunetas pluviales - %s\n;;Exportado por DrenIE. Lluvia: %s; lamina %.2f mm, pico %.2f mm/h.\n" % (
        nom, H["metodo"], H["lamina_mm"], H["pico_mmh"]))
    w("[OPTIONS]\nFLOW_UNITS           LPS\nINFILTRATION         HORTON\nFLOW_ROUTING         DYNWAVE\nLINK_OFFSETS         ELEVATION\n"
      "MIN_SLOPE            0\nALLOW_PONDING        NO\nSKIP_STEADY_STATE    NO\nSTART_DATE           01/01/2026\nSTART_TIME           00:00:00\n"
      "REPORT_START_DATE    01/01/2026\nREPORT_START_TIME    00:00:00\nEND_DATE             01/01/2026\nEND_TIME             %02d:%02d:00\n"
      "SWEEP_START          01/01\nSWEEP_END            12/31\nDRY_DAYS             0\nREPORT_STEP          00:01:00\nWET_STEP             00:01:00\n"
      "DRY_STEP             01:00:00\nROUTING_STEP         0:00:01\nINERTIAL_DAMPING     PARTIAL\nNORMAL_FLOW_LIMITED  BOTH\n"
      "FORCE_MAIN_EQUATION  H-W\nVARIABLE_STEP        0.75\nLENGTHENING_STEP     0\nMIN_SURFAREA         0.1\nMAX_TRIALS           8\n"
      "HEAD_TOLERANCE       0.0015\nSYS_FLOW_TOL         5\nLAT_FLOW_TOL         5\n" % (fin // 60, fin % 60))
    w("[RAINGAGES]\n;;Nombre Formato Intervalo SCF Fuente\nPLUVIOMETRO INTENSITY 0:%02d 1.0 TIMESERIES HIETOGRAMA\n" % dt)
    w("[SUBCATCHMENTS]\n;;Nombre Pluviometro Salida Area(ha) %Imperm Ancho(m) Pend(%) Curb\n" + "".join(
        "%s PLUVIOMETRO %s %.5f %.1f %.1f 1.0 0\n" % (s["nombre"], _nombre(s["salida"]), s["A"] / 1e4, s["imp"], s["ancho"]) for s in subcuencas))
    w("[SUBAREAS]\n;;Subcuenca N-Imperm N-Perm S-Imperm(mm) S-Perm(mm) %Cero RutaA\n" + "".join(
        "%s 0.012 0.24 1.27 5.08 25 OUTLET\n" % s["nombre"] for s in subcuencas))
    w("[INFILTRATION]\n;;Subcuenca f0(mm/h) fc(mm/h) Decaim(1/h) Secado(d) Max\n" + "".join(
        "%s 75 6 4 7 0\n" % s["nombre"] for s in subcuencas))
    w("[JUNCTIONS]\n;;Nudo Cota(m) Prof.max(m) Prof.ini Sobrecarga Ponding\n" + "".join(
        "%s %.3f %.3f 0 0 0\n" % (_nombre(n), inv[n], max(math.ceil((prof[n] - inv[n]) * 1000 - 1e-6) / 1000 + 0.001, 0.05)) for n in inv if n not in salidas))
    w("[OUTFALLS]\n;;Nudo Cota(m) Tipo\n" + "".join("%s %.3f FREE NO\n" % (_nombre(n), inv[n]) for n in inv if n in salidas))
    w("[CONDUITS]\n;;Conducto Desde Hasta Long(m) n Desfase-ent Desfase-sal Q-ini Q-max\n" + "".join(
        "%s %s %s %.2f %.3f %.3f %.3f 0 0\n" % (c["nombre"], _nombre(c["de"]), _nombre(c["a"]), c["L"], P["n_cap"], c["cf_de"], c["cf_a"])
        for c in conductos))
    w("[XSECTIONS]\n;;Conducto Forma Alto(m) Ancho(m) G3 G4 Barriles\n" + "".join(
        "%s %s %.3f %.3f 0 0 1\n" % (c["nombre"], c["forma"], c["h"], c["b"]) for c in conductos))
    w("[TIMESERIES]\n;;Nombre Hora Intensidad(mm/h)\n" + "".join(
        "HIETOGRAMA %d:%02d %.3f\n" % ((k * dt) // 60, (k * dt) % 60, v) for k, v in enumerate(H["intensidades"] + [0.0])))
    w("[REPORT]\nINPUT NO\nCONTROLS NO\nSUBCATCHMENTS ALL\nNODES ALL\nLINKS ALL\n")
    xs = [p[0] for p in xy.values()]; ys = [p[1] for p in xy.values()]
    w("[MAP]\nDIMENSIONS %.3f %.3f %.3f %.3f\nUnits Meters\n" % (min(xs) - 5, min(ys) - 5, max(xs) + 5, max(ys) + 5))
    w("[COORDINATES]\n;;Nudo X Y\n" + "".join("%s %.3f %.3f\n" % (_nombre(n), p[0], p[1]) for n, p in xy.items()))
    w("[POLYGONS]\n;;Subcuenca X Y\n" + "".join("".join("%s %.3f %.3f\n" % (s["nombre"], s["p"][0] + dx, s["p"][1] + dy)
                                                        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))) for s in subcuencas))
    w("[SYMBOLS]\n;;Pluviometro X Y\nPLUVIOMETRO %.3f %.3f\n" % ((min(xs) + max(xs)) / 2, max(ys) + 3))
    with open(ruta, "w", encoding="utf-8", newline="\r\n") as o: o.write("\n".join(L))
    return {"archivo": ruta, "nudos": len(inv), "descargas": len(salidas & set(inv)), "conductos": len(conductos), "subcuencas": len(subcuencas),
            "area_ha": round(sum(s["A"] for s in subcuencas) / 1e4, 4), "hietograma": H}
