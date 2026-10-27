"""Reduce PISCOp (SENAMHI, lluvia diaria grillada del Perú) a la lluvia máxima diaria de cada mes en cada celda.

El archivo diario PISCOp_d.nc pesa mucho para subirlo o llevarlo dentro de DrenIE. Este programa lo lee por partes
y escribe PISCO_MAX_24H_MENSUAL.npz: para cada celda de 0.1°, cada año y cada mes, la lluvia máxima de un día
(el mismo formato de las tablas de «precipitación máxima en 24 horas» del SENAMHI).
Con eso DrenIE arma la serie de máximas en 24 h de cualquier punto del Perú (factor 1.13 de la OMM / Manual MTC)
sin internet.

Uso en Windows (Python 3.12 ya instalado para compilar DrenIE):
    py -3.12 -m pip install netCDF4 numpy
    py -3.12 reducir_pisco.py PISCOp_d.nc
    py -3.12 reducir_pisco.py PISCOp_d.nc --punto -6.5116 -76.3199      (opcional: muestra la serie de un punto)

Fuente de los datos: PISCOp v3.0, SENAMHI (https://doi.org/10.6084/m9.figshare.32411886). Los datos son del SENAMHI;
cite el producto como indica su página.
"""
import argparse
import datetime as dt
import json
import os
import sys
import warnings

import numpy as np


def _abrir(ruta):
    try:
        from netCDF4 import Dataset, num2date
    except ImportError:
        sys.exit("Falta la biblioteca netCDF4. Ejecute:  py -3.12 -m pip install netCDF4 numpy")
    return Dataset(ruta), num2date


def _variable_lluvia(nc):
    """La variable de 3 dimensiones (tiempo, latitud, longitud): la de nombre de lluvia o la única que haya."""
    cands = [v for v in nc.variables.values() if v.ndim == 3]
    if not cands: sys.exit("El archivo no tiene una variable de 3 dimensiones (tiempo, latitud, longitud).")
    for v in cands:
        if v.name.lower() in ("prec", "pr", "precip", "precipitation", "p", "variable") or "prec" in v.name.lower(): return v
    return cands[0]


def _eje(nc, var, claves):
    for d in var.dimensions:
        if any(d.lower().startswith(k) for k in claves): return d
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivo", help="PISCOp_d.nc (lluvia diaria)")
    ap.add_argument("--salida", default="PISCO_MAX_24H_MENSUAL.npz")
    ap.add_argument("--inicio", default="1981-01-01", help="primer día, solo si el archivo no trae fechas (PISCOp: 1981-01-01)")
    ap.add_argument("--punto", nargs=2, type=float, metavar=("LAT", "LON"), help="muestra la serie de máximas de un punto")
    a = ap.parse_args()
    nc, num2date = _abrir(a.archivo)
    v = _variable_lluvia(nc)
    dy, dx = _eje(nc, v, ("lat", "y")), _eje(nc, v, ("lon", "x"))
    resto = [d for d in v.dimensions if d not in (dy, dx)]
    if not (dy and dx) or len(resto) != 1:
        sys.exit("No se reconocieron las dimensiones %s de la variable %s." % (v.dimensions, v.name))
    dt_ = resto[0]                                   # el eje de fechas: en PISCOp v3.0 se llama «Z1»
    orden = [v.dimensions.index(d) for d in (dt_, dy, dx)]
    lat = np.asarray(nc.variables[dy][:], dtype="f8")
    lon = np.asarray(nc.variables[dx][:], dtype="f8")
    n = len(nc.dimensions[dt_])
    tv = next((x for x in nc.variables.values() if x.dimensions == (dt_,) and "since" in str(getattr(x, "units", ""))), None)
    if tv is not None:
        fechas = num2date(tv[:], tv.units, getattr(tv, "calendar", "standard"))
        fechas = [dt.date(f.year, f.month, f.day) for f in fechas]
    else:                                            # sin fechas en el archivo: días seguidos desde --inicio
        ini = dt.date.fromisoformat(a.inicio)
        fechas = [ini + dt.timedelta(days=i) for i in range(n)]
        print("AVISO: el archivo no trae fechas en «%s»; se asumen %d días seguidos desde %s (hasta %s). "
              "Si PISCOp no empieza ese día, use --inicio AAAA-MM-DD." % (dt_, n, ini, fechas[-1]))
    anios = np.array([f.year for f in fechas])
    unidades = getattr(v, "units", "mm/day")
    print("Variable: %s %s, unidades %s" % (v.name, v.dimensions, unidades))
    print("Periodo: %s a %s (%d días), malla %d x %d" % (fechas[0].strftime("%Y-%m-%d"), fechas[-1].strftime("%Y-%m-%d"),
                                                         len(fechas), len(lat), len(lon)))
    lista = sorted(set(anios.tolist()))
    meses = np.array([f.month for f in fechas])
    # máxima diaria de cada mes (como las tablas de «precipitación máxima en 24 horas» del SENAMHI): (año, mes, lat, lon)
    maximos = np.full((len(lista), 12, len(lat), len(lon)), 65535, dtype="u2")    # décimas de mm; 65535 = sin dato
    dias = np.zeros((len(lista), 12), dtype="u2")
    for k, an in enumerate(lista):
        idx = np.nonzero(anios == an)[0]
        sl = [slice(None)] * 3; sl[orden[0]] = slice(int(idx[0]), int(idx[-1]) + 1)
        bloque = np.ma.filled(np.ma.masked_invalid(np.ma.asarray(v[tuple(sl)], dtype="f4")), np.nan)
        bloque = np.transpose(bloque, orden)                                       # (tiempo, lat, lon)
        bloque[bloque < 0] = np.nan
        mes_del_dia = meses[idx[0]:idx[-1] + 1]
        pico = float("nan")
        for mes in range(1, 13):
            sel = mes_del_dia == mes
            if not sel.any(): continue
            with warnings.catch_warnings():              # celdas fuera del Perú: todo sin dato
                warnings.simplefilter("ignore", RuntimeWarning)
                m = np.nanmax(bloque[sel], axis=0)
            ok = np.isfinite(m)
            maximos[k, mes - 1][ok] = np.clip(np.round(m[ok] * 10), 0, 65534).astype("u2")
            dias[k, mes - 1] = int(sel.sum())
            if ok.any(): pico = np.nanmax([pico, np.nanmax(m)])
        print("  %d: %d días, máxima del Perú %.1f mm" % (an, len(idx), pico), flush=True)
    meta = {"fuente": "PISCOp (SENAMHI), lluvia diaria grillada; máxima diaria de cada mes por celda",
            "archivo": os.path.basename(a.archivo), "variable": v.name, "unidades": unidades,
            "titulo": getattr(nc, "title", ""), "version": getattr(nc, "version", ""), "creado": dt.date.today().isoformat(),
            "escala": "décimas de mm; 65535 = sin dato", "dimensiones": "anio, mes, lat, lon", "dias_por_mes": dias.tolist()}
    np.savez_compressed(a.salida, lat=lat.astype("f4"), lon=lon.astype("f4"), anios=np.array(lista, dtype="u2"), maximos=maximos,
                        meta=np.array(json.dumps(meta, ensure_ascii=False)))
    print("\nOK · %s (%.1f MB). Súbalo a la conversación para incorporarlo a DrenIE." % (a.salida, os.path.getsize(a.salida) / 1e6))
    if a.punto:
        i = int(np.abs(lat - a.punto[0]).argmin()); j = int(np.abs(lon - a.punto[1]).argmin())
        print("\nPunto %.4f, %.4f -> celda %.3f, %.3f   (máxima en 24 h de cada mes, mm)" % (a.punto[0], a.punto[1], lat[i], lon[j]))
        print("  Año    " + " ".join("%5s" % x for x in ("ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SET", "OCT", "NOV", "DIC")) + "   MÁX")
        for k, an in enumerate(lista):
            fila = [None if x == 65535 else x / 10 for x in maximos[k, :, i, j]]
            vals = [x for x in fila if x is not None]
            print("  %d  " % an + " ".join("%5s" % ("-" if x is None else "%.1f" % x) for x in fila) + "  %5s" % ("%.1f" % max(vals) if vals else "-"))


if __name__ == "__main__":
    main()
