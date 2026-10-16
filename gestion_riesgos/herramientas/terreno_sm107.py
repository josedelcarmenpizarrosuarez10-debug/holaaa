"""Eje y terreno de la carretera SM-107, tramo Tingo de Ponasa - Shamboyacu (CUI 2673852).

1. Extrae el eje de via del plano clave PC-01 (PDF vectorial, esc. 1/20,000) y lo georreferencia con la
   cuadricula UTM del propio plano (lineas cada 2,000 m; WGS 84 / UTM 18S). Control: los puntos geodesicos y BM
   del inventario vial quedan a 6-57 m del eje y las progresivas resultantes coinciden con las del inventario.
2. Recorta el modelo digital Copernicus GLO-30 (DSM, 30 m) al corredor y calcula, cada 100 m, la cota, la
   pendiente longitudinal y la pendiente transversal maxima del entorno (franja de 150 m a cada lado).
   El DSM incluye la altura de la vegetacion: los valores son referenciales y no sustituyen la topografia.
Uso: python3 terreno_sm107.py [carpeta_con_los_tif_de_copernicus]
"""
import os, sys, json, math
import numpy as np
import pymupdf

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)          # carpeta gestion_riesgos
PROY = os.path.join(RAIZ, "proyectos", "SM-107_TINGO_DE_PONASA_SHAMBOYACU")
INS = os.path.join(PROY, "insumos"); CALC = os.path.join(PROY, "entregables", "_calc")
PDF = os.path.join(INS, "PLANO_CLAVE_PC-01_SM107.pdf")
PROG0 = 19343.39                      # progresiva del inicio del tramo (Tingo de Ponasa)
FIN_INV = (374968.0, 9223432.0)       # fin del tramo segun el inventario vial (km 44+693.39)
# cuadricula del PC-01: lineas verticales x = 182.7 (E 360 000) ... y horizontales y = 281.0 (N 9 232 000) ...
X0, E0, Y0, N0, PASO_PT, PASO_M = 182.7, 360000.0, 281.0, 9232000.0, 283.5, 2000.0


def eje_pdf():
    p = pymupdf.open(PDF)[0]; pts = set()
    for g in p.get_drawings():
        col = tuple(round(c, 2) for c in (g.get("color") or ()))
        if col != (0.0, 0.0, 0.87) or round(g.get("width") or 0, 2) != 0: continue
        for it in g["items"]:
            if it[0] == "l": seq = [it[1], it[2]]
            elif it[0] == "c": seq = [it[1], it[4]]
            else: continue
            for q in seq:
                if q.x > 2200 and q.y < 120: continue          # simbolo de la leyenda
                pts.add((round(q.x, 2), round(q.y, 2)))
    P = np.array(sorted(pts)); k = PASO_M / PASO_PT
    cur = int(np.argmin((P[:, 0] - 420) ** 2 + (P[:, 1] - 80) ** 2)); usado = np.zeros(len(P), bool); usado[cur] = True; orden = [cur]
    while True:                                                  # recorrido por vecino mas cercano
        d = ((P - P[cur]) ** 2).sum(1); d[usado] = 1e18; j = int(np.argmin(d))
        if d[j] > 30 ** 2: break
        usado[j] = True; orden.append(j); cur = j
    Q = P[orden]
    E = E0 + (Q[:, 0] - X0) * k; N = N0 - (Q[:, 1] - Y0) * k
    return np.c_[E, N]


def remuestrear(XY, paso):
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(XY, axis=0).T))]
    si = np.arange(0, s[-1], paso); si = np.r_[si, s[-1]]
    return np.c_[np.interp(si, s, XY[:, 0]), np.interp(si, s, XY[:, 1])], si


def dem_utm(carpeta, bbox, res=30.0):
    import rasterio
    from rasterio.warp import reproject, Resampling
    from rasterio.transform import from_origin
    e0, n0, e1, n1 = bbox
    W = int((e1 - e0) / res); H = int((n1 - n0) / res); dst = np.full((H, W), np.nan, "float32")
    tr = from_origin(e0, n1, res, res)
    for f in sorted(os.listdir(carpeta)):
        if not f.endswith("_DEM.tif"): continue
        with rasterio.open(os.path.join(carpeta, f)) as src:
            tmp = np.full((H, W), np.nan, "float32")
            reproject(rasterio.band(src, 1), tmp, dst_transform=tr, dst_crs="EPSG:32718", resampling=Resampling.bilinear, dst_nodata=np.nan)
            dst = np.where(np.isnan(dst), tmp, dst)
    return dst, tr


def muestrear(Z, tr, E, N):
    c = (np.asarray(E) - tr.c) / tr.a - 0.5; r = (np.asarray(N) - tr.f) / tr.e - 0.5
    c0 = np.clip(np.floor(c).astype(int), 0, Z.shape[1] - 2); r0 = np.clip(np.floor(r).astype(int), 0, Z.shape[0] - 2)
    fc = c - c0; fr = r - r0
    return (Z[r0, c0] * (1 - fc) * (1 - fr) + Z[r0, c0 + 1] * fc * (1 - fr) + Z[r0 + 1, c0] * (1 - fc) * fr + Z[r0 + 1, c0 + 1] * fc * fr)


def main():
    os.makedirs(CALC, exist_ok=True)
    XY = eje_pdf()
    # tramo final (44+109 a 44+693): el PC-01 termina en 44+090; se completa en recta hasta el fin del inventario
    XYf = np.vstack([XY, FIN_INV])
    eje, s = remuestrear(XYf, 10.0)
    L_pc = float(np.hypot(*np.diff(XY, axis=0).T).sum())
    out = {"fuente": "Plano clave PC-01 (DRTC San Martin, nov. 2024), eje georreferenciado con su cuadricula UTM WGS 84 zona 18 S",
           "prog0": PROG0, "longitud_pc01_m": round(L_pc, 1), "longitud_total_m": round(float(s[-1]), 1),
           "eje": [[round(e, 2), round(n, 2), round(PROG0 + d, 1)] for (e, n), d in zip(eje, s)]}
    # control con los puntos geodesicos del inventario
    ctrl = {"PG 1009558 (Leoncio Prado)": (363732.742, 9227088.122), "BM Huañipo": (367812.896, 9225381.96), "BM Aypena": (360956.861, 9230854.36),
            "PC-2 TERRA": (366089.772, 9226258.94), "PC-4 TERRA": (370554.943, 9226693.71), "PC-6 TERRA": (361498.631, 9227764.43),
            "PC-8 TERRA": (361546.188, 9233404.28), "PC-9 TERRA": (371134.512, 9226417.5), "PC-10 TERRA": (372951.339, 9223765.97)}
    out["control"] = []
    for n_, (e, n) in ctrl.items():
        d = np.hypot(eje[:, 0] - e, eje[:, 1] - n); i = int(d.argmin())
        out["control"].append([n_, round(float(d[i]), 1), round(PROG0 + float(s[i]), 0)])
    carpeta = sys.argv[1] if len(sys.argv) > 1 else None
    if carpeta:
        bb = (eje[:, 0].min() - 2500, eje[:, 1].min() - 2500, eje[:, 0].max() + 2500, eje[:, 1].max() + 2500)
        bb = tuple(math.floor(v / 30) * 30 for v in bb)
        Z, tr = dem_utm(carpeta, bb)
        np.savez_compressed(os.path.join(CALC, "dem_corredor.npz"), Z=Z.astype("float32"), tr=np.array([tr.c, tr.f, tr.a, tr.e]))
        gy, gx = np.gradient(Z, 30.0)
        pend = np.degrees(np.arctan(np.hypot(gx, gy)))
        # cada 100 m: cota, pendiente longitudinal y pendiente transversal maxima en 150 m a cada lado
        e100, s100 = remuestrear(XYf, 100.0)
        z100 = muestrear(Z, tr, e100[:, 0], e100[:, 1])
        tramos = []
        for i in range(len(e100) - 1):
            a, b = e100[i], e100[i + 1]; t = (b - a) / max(np.hypot(*(b - a)), 1e-6); nrm = np.array([-t[1], t[0]])
            m = (a + b) / 2; off = np.arange(-150, 151, 15)
            lado = m[None, :] + off[:, None] * nrm[None, :]
            pz = muestrear(pend, tr, lado[:, 0], lado[:, 1]); zz = muestrear(Z, tr, lado[:, 0], lado[:, 1])
            tramos.append({"pi": round(PROG0 + s100[i], 0), "pf": round(PROG0 + s100[i + 1], 0), "z": round(float((z100[i] + z100[i + 1]) / 2), 1),
                           "i_long_%": round(float((z100[i + 1] - z100[i]) / max(s100[i + 1] - s100[i], 1) * 100), 2),
                           "pend_max_grados": round(float(np.nanmax(pz)), 1), "relieve_m": round(float(np.nanmax(zz) - np.nanmin(zz)), 1)})
        out["tramos_100m"] = tramos
    json.dump(out, open(os.path.join(CALC, "eje_terreno.json"), "w"), indent=0, ensure_ascii=False)
    print("eje", out["longitud_pc01_m"], out["longitud_total_m"]); [print(" ", c) for c in out["control"]]


if __name__ == "__main__":
    main()
