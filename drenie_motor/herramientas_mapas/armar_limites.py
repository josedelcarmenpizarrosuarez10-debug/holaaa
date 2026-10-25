"""Arma drenie_motor/limites_peru.json: límites de departamentos, provincias y distritos del Perú (con ubigeo) y de los países
vecinos, simplificados para los mapas de ubicación. No se ejecuta en el programa: se corre aquí cuando cambia la fuente.

    python herramientas_mapas/armar_limites.py <departamentos> <provincias> <distritos> <paises.zip|shp> [--fuente "texto"]

Cada capa del Perú puede ser GeoJSON o shapefile (.shp con su .dbf; geográficas WGS 84 o UTM WGS 84 17S/18S/19S según el .prj).
Campos reconocidos (INEI y sus copias): ubigeo IDDIST / UBIGEO / IDPROV / FIRST_IDPR / IDDPTO / FIRST_IDDP / CCDD..;
nombres NOMBDIST / NOMBPROV / NOMBDEP / DISTRITO / PROVINCIA / DEPARTAMEN / FIRST_NOMB. Países: Natural Earth admin 0.
"""
import json
import math
import os
import struct
import sys
import zipfile

from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "..", "drenie_motor", "limites_peru.json")
VECINOS = {"ECU": "ECUADOR", "COL": "COLOMBIA", "BRA": "BRASIL", "BOL": "BOLIVIA", "CHL": "CHILE", "PER": "PERÚ"}
TOL = {"departamentos": 0.004, "provincias": 0.0015, "distritos": 0.0006, "paises": 0.02}


# ------------------------------------------------------------------ lectura de shapefiles (polígonos) sin bibliotecas externas
def _dbf(datos):
    n, cab, reg = struct.unpack("<xxxxIHH", datos[:12])
    campos, i = [], 32
    while datos[i] != 0x0D:
        nombre = datos[i:i + 11].split(b"\x00")[0].decode("latin-1"); tipo = chr(datos[i + 11]); largo = datos[i + 16]
        campos.append((nombre, tipo, largo)); i += 32
    filas = []
    for k in range(n):
        p = cab + k * reg + 1; fila = {}
        for nombre, tipo, largo in campos:
            v = datos[p:p + largo]; p += largo
            try: t = v.decode("utf-8").strip()
            except UnicodeDecodeError: t = v.decode("latin-1").strip()
            fila[nombre] = t
        filas.append(fila)
    return filas


def _shp(datos):
    geoms, p = [], 100
    while p < len(datos):
        _, largo = struct.unpack(">ii", datos[p:p + 8]); cont = datos[p + 8:p + 8 + 2 * largo]; p += 8 + 2 * largo
        tipo = struct.unpack("<i", cont[:4])[0]
        if tipo == 0: geoms.append(None); continue
        if tipo not in (5, 15, 25): raise SystemExit("El shapefile no es de polígonos (tipo %d)" % tipo)
        npar, npts = struct.unpack("<ii", cont[36:44])
        partes = list(struct.unpack("<%di" % npar, cont[44:44 + 4 * npar])) + [npts]
        xy = struct.unpack("<%dd" % (2 * npts), cont[44 + 4 * npar:44 + 4 * npar + 16 * npts])
        pts = [(xy[2 * j], xy[2 * j + 1]) for j in range(npts)]
        anillos = [pts[partes[j]:partes[j + 1]] for j in range(npar)]
        geoms.append(anillos)
    return geoms


def _area(r):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1])) / 2


def _anillos_a_geom(anillos):
    """Shapefile: anillos exteriores en sentido horario, huecos en antihorario."""
    ext, huecos = [], []
    for r in anillos:
        (ext if _area(r) < 0 else huecos).append(r)
    polis = [Polygon(e) for e in ext]
    for h in huecos:
        ph = Polygon(h)
        for k, pe in enumerate(polis):
            if pe.contains(ph.representative_point()): polis[k] = pe.difference(ph); break
    g = unary_union(polis) if polis else None
    return g.buffer(0) if g is not None else None


def leer(ruta):
    """[(geometría shapely en lon/lat, propiedades)] de un GeoJSON, un .shp o un .zip con un .shp."""
    if ruta.lower().endswith((".geojson", ".json")):
        d = json.load(open(ruta, encoding="utf-8"))
        return [(shape(f["geometry"]).buffer(0), f["properties"]) for f in d["features"] if f.get("geometry")]
    if ruta.lower().endswith(".zip"):
        z = zipfile.ZipFile(ruta); shp = [n for n in z.namelist() if n.lower().endswith(".shp")][0]; base = shp[:-4]
        datos = {e: z.read(n) for n in z.namelist() for e in (".shp", ".dbf", ".prj") if n.lower() == (base + e).lower()}
    else:
        base = ruta[:-4]; datos = {e: open(base + e, "rb").read() for e in (".shp", ".dbf", ".prj") if os.path.exists(base + e)}
    geoms, filas = _shp(datos[".shp"]), _dbf(datos[".dbf"])
    prj = datos.get(".prj", b"").decode("latin-1").upper()
    zona = None
    for z in (17, 18, 19):
        if "ZONE_%dS" % z in prj or "UTM ZONE %dS" % z in prj or "ZONE %dS" % z in prj: zona = z
    out = []
    for anillos, fila in zip(geoms, filas):
        if not anillos: continue
        if zona: anillos = [[utm_a_geo(x, y, zona)[::-1] for x, y in r] for r in anillos]
        out.append((_anillos_a_geom(anillos), fila))
    return out


def utm_a_geo(E, N, zona, sur=True):
    """UTM WGS 84 -> (latitud, longitud) en grados (fórmulas de Snyder, error menor a 1 mm en la zona)."""
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


# ------------------------------------------------------------------ campos
def _campo(p, *nombres):
    for n in nombres:
        for k, v in p.items():
            if k.upper() == n and str(v).strip(): return str(v).strip()
    return ""


# tildes que el INEI omite en sus nombres en mayúsculas (departamentos y palabras frecuentes); el resto se corrige en el editor
TILDES = {"ANCASH": "Áncash", "APURIMAC": "Apurímac", "HUANUCO": "Huánuco", "JUNIN": "Junín", "MARTIN": "Martín", "PERU": "Perú",
          "LIMA": "Lima", "CALLAO": "Callao", "JOSE": "José", "MARIA": "María", "JESUS": "Jesús", "ANDRES": "Andrés", "RIO": "Río",
          "ANGELES": "Ángeles", "CONCEPCION": "Concepción", "ASUNCION": "Asunción", "AYACUCHO": "Ayacucho", "TUMBES": "Tumbes",
          "BELEN": "Belén", "PUERTO": "Puerto", "INDEPENDENCIA": "Independencia", "VICTOR": "Víctor", "RAMON": "Ramón",
          "MARAÑON": "Marañón", "MARANON": "Marañón", "TAMBOPATA": "Tambopata", "UCAYALI": "Ucayali", "HUALLAGA": "Huallaga",
          "MOYOBAMBA": "Moyobamba", "RIOJA": "Rioja", "BELLAVISTA": "Bellavista", "PICOTA": "Picota", "TOCACHE": "Tocache",
          "CACERES": "Cáceres", "LEON": "León", "PAMPAS": "Pampas", "ALAMEDA": "Alameda", "CHICLAYO": "Chiclayo", "PIURA": "Piura",
          "TRUJILLO": "Trujillo", "CAJAMARCA": "Cajamarca", "AREQUIPA": "Arequipa", "CUSCO": "Cusco", "PUNO": "Puno",
          "MOQUEGUA": "Moquegua", "TACNA": "Tacna", "ICA": "Ica", "PASCO": "Pasco", "HUANCAVELICA": "Huancavelica",
          "LAMBAYEQUE": "Lambayeque", "LORETO": "Loreto", "AMAZONAS": "Amazonas", "TUMBES": "Tumbes", "MADRE": "Madre", "DIOS": "Dios"}


def _titulo(t):
    """Nombres en mayúsculas del INEI -> como se escriben («LA BANDA DE SHILCAYO» -> «La Banda de Shilcayo»)."""
    menores = {"DE", "DEL", "LA", "LAS", "LOS", "EL", "Y", "E"}
    pal = t.strip().split()
    return " ".join(TILDES.get(w.upper(), w.capitalize()) if (i == 0 or w.upper() not in menores) else w.lower() for i, w in enumerate(pal))


def _coords(g, tol):
    g = g.simplify(tol, preserve_topology=True)
    if g.is_empty: return []
    polis = list(g.geoms) if isinstance(g, MultiPolygon) else [g] if isinstance(g, Polygon) else [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]
    r = lambda c: [[round(x, 5), round(y, 5)] for x, y in c]
    return [[r(p.exterior.coords)] + [r(h.coords) for h in p.interiors] for p in polis if p.area > 0]


def armar(dep, prov, dist, paises, fuente):
    out = {"fuente": fuente, "nota": "Límites referenciales para mapas de ubicación (no son límites de demarcación).",
           "departamentos": [], "provincias": [], "distritos": [], "paises": []}
    for g, p in leer(dep):
        u = _campo(p, "FIRST_IDDP", "IDDPTO", "CCDD", "UBIGEO", "IDDEP")[:2]
        out["departamentos"].append({"u": u, "n": _titulo(_campo(p, "NOMBDEP", "DEPARTAMEN", "DEPARTAMENTO", "NOMBRE")), "g": _coords(g, TOL["departamentos"])})
    for g, p in leer(prov):
        u = _campo(p, "FIRST_IDPR", "IDPROV", "CCPP", "UBIGEO")[:4]
        out["provincias"].append({"u": u, "n": _titulo(_campo(p, "NOMBPROV", "PROVINCIA", "NOMBRE")), "g": _coords(g, TOL["provincias"])})
    for g, p in leer(dist):
        u = _campo(p, "IDDIST", "UBIGEO", "CCDI", "IDDISTRITO")[:6]
        out["distritos"].append({"u": u, "n": _titulo(_campo(p, "NOMBDIST", "DISTRITO", "NOMBRE")), "cap": _titulo(_campo(p, "NOM_CAP", "CAPITAL")),
                                 "g": _coords(g, TOL["distritos"])})
    caja = Polygon([(-86, -21), (-64, -21), (-64, 3), (-86, 3)])
    for g, p in leer(paises):
        iso = _campo(p, "ADM0_A3", "ISO_A3", "SOV_A3")
        if iso in VECINOS: out["paises"].append({"iso": iso, "n": VECINOS[iso], "g": _coords(g.intersection(caja), TOL["paises"])})
    for k in ("departamentos", "provincias", "distritos"):
        out[k] = [x for x in out[k] if x["g"]]; out[k].sort(key=lambda x: x["u"])
    vacios = [k for k in ("departamentos", "provincias", "distritos", "paises") if not out[k]]
    if vacios: raise SystemExit("Capas vacías: %s (revise los nombres de campos)" % ", ".join(vacios))
    json.dump(out, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("OK · %d departamentos, %d provincias, %d distritos, %d países · %s (%.1f MB)" % (
        len(out["departamentos"]), len(out["provincias"]), len(out["distritos"]), len(out["paises"]), os.path.normpath(SALIDA), os.path.getsize(SALIDA) / 1e6))


if __name__ == "__main__":
    args = sys.argv[1:]; fuente = "INEI"
    if "--fuente" in args: i = args.index("--fuente"); fuente = args[i + 1]; del args[i:i + 2]
    a = [x for x in args if not x.startswith("--")]
    if len(a) < 4: raise SystemExit(__doc__)
    armar(a[0], a[1], a[2], a[3], fuente)
