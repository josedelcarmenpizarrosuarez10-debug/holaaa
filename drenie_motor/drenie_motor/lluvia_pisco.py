"""Serie de precipitación máxima en 24 h por mes de cualquier punto del Perú, desde PISCOp v3.0 (SENAMHI).

Datos: lluvia_pisco_mensual.npz (herramientas_lluvia/reducir_pisco.py sobre PISCOp_d.nc): máxima diaria de cada mes, 1981-2025,
en celdas de 0.1°. Es una serie REFERENCIAL: la lluvia grillada promedia ~10 x 10 km y subestima las máximas puntuales, por eso
se corrige con un factor estación / PISCO calibrado con estaciones del SENAMHI (solo el factor: las series certificadas de las
estaciones no se reproducen). Donde no hay calibración, el factor es 1.00 y se avisa.
"""
import os
from functools import lru_cache

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lluvia_pisco_mensual.npz")
FUENTE = "PISCOp v3.0 (SENAMHI), precipitación diaria grillada 1981-2025; máxima en 24 h de cada mes"
# factor estación / PISCO (promedio de las máximas anuales en los años comunes), por departamento (ubigeo de 2 dígitos)
FACTORES = {
    "22": (1.40, "San Martín: calibrado con las estaciones SENAMHI CO Tarapoto (1.35) y Pongo de Caynarachi (1.45)"),
}
SIN_CALIBRAR = ("La lluvia de PISCO promedia ~10 x 10 km y suele dar máximas menores que una estación (en San Martín, 25 a 30 % "
                "menos). En este departamento no hay factor calibrado: ingrese uno o use la serie de la estación más cercana.")


def disponible():
    return os.path.exists(RUTA)


@lru_cache(maxsize=1)
def _datos():
    import numpy as np
    if not disponible(): raise FileNotFoundError("Esta instalación no trae la base de lluvias PISCO (lluvia_pisco_mensual.npz).")
    z = np.load(RUTA, allow_pickle=False)
    return {"lat": z["lat"].astype("f8"), "lon": z["lon"].astype("f8"), "anios": [int(a) for a in z["anios"]], "max": z["maximos"]}


def _celda(lat, lon):
    """Celda con datos más cercana al punto (si el punto cae en una celda sin datos, la vecina más próxima que sí tenga)."""
    import numpy as np
    D = _datos()
    i0 = int(np.abs(D["lat"] - lat).argmin()); j0 = int(np.abs(D["lon"] - lon).argmin())
    for r in range(0, 4):
        mejor = None
        for i in range(max(0, i0 - r), min(len(D["lat"]), i0 + r + 1)):
            for j in range(max(0, j0 - r), min(len(D["lon"]), j0 + r + 1)):
                if (D["max"][:, :, i, j] != 65535).any():
                    dd = (D["lat"][i] - lat) ** 2 + (D["lon"][j] - lon) ** 2
                    if mejor is None or dd < mejor[0]: mejor = (dd, i, j)
        if mejor: return mejor[1], mejor[2]
    raise ValueError("El punto %.4f, %.4f está fuera del Perú o sin datos de PISCO." % (lat, lon))


def serie(lat=None, lon=None, ubigeo=None, factor=None):
    """{celda, punto, ubicacion, anios, filas (12 meses, mm, corregidas), filas_pisco (sin corregir), factor, ...}."""
    from . import ubicacion as UBI
    lugar = None
    if ubigeo:
        x = UBI.limites()["por_u"].get(str(ubigeo))
        if x is None: raise ValueError("Ubigeo %s no encontrado." % ubigeo)
        c = x["geom"].representative_point(); lat, lon = c.y, c.x
        lugar = UBI._jerarquia(x, {}) if len(str(ubigeo)) == 6 else None
    if lat is None or lon is None: raise ValueError("Indique el distrito o las coordenadas (latitud y longitud) del proyecto.")
    lat, lon = float(lat), float(lon)
    if lugar is None:
        d = UBI.distrito_en(lon, lat)
        lugar = UBI._jerarquia(d, {}) if d else None
    dep = (lugar or {}).get("ubigeo", "")[:2]
    f_def, detalle = FACTORES.get(dep, (1.0, None))
    f = float(factor) if factor not in (None, "") else f_def
    if not (0.5 <= f <= 3.0): raise ValueError("El factor de corrección debe estar entre 0.50 y 3.00.")
    D = _datos(); i, j = _celda(lat, lon)
    filas_p, filas = [], []
    for k, an in enumerate(D["anios"]):
        mm = [None if v == 65535 else round(v / 10.0, 1) for v in D["max"][k, :, i, j].tolist()]
        filas_p.append(mm); filas.append([None if v is None else round(v * f, 1) for v in mm])
    avisos = ["Serie referencial PISCOp v3.0 (SENAMHI) multiplicada por %.2f. Para el expediente se recomienda la serie certificada "
              "de la estación SENAMHI más cercana." % f]
    if detalle is None and factor in (None, ""): avisos.append(SIN_CALIBRAR)
    anuales = [max(v for v in fl if v is not None) for fl in filas if any(v is not None for v in fl)]
    return {"accion": "pisco", "fuente": FUENTE, "punto": {"lat": round(lat, 5), "lon": round(lon, 5)},
            "celda": {"lat": round(float(D["lat"][i]), 3), "lon": round(float(D["lon"][j]), 3)},
            "ubicacion": {k: (lugar or {}).get(k, "") for k in ("ubigeo", "departamento", "provincia", "distrito")},
            "anios": D["anios"], "filas": filas, "filas_pisco": filas_p, "factor": f, "factor_sugerido": f_def,
            "calibracion": detalle or "", "periodo": "%d-%d" % (D["anios"][0], D["anios"][-1]),
            "resumen": {"max_anual_media_mm": round(sum(anuales) / len(anuales), 1) if anuales else None,
                        "max_anual_mm": max(anuales) if anuales else None, "anios": len(anuales)},
            "avisos": avisos}
