"""Valores del metrado del colector del CAR Varones (partidas 01.04.04) tal como los calcula la planilla.

La planilla METRADO_DRENAJE_PLUVIAL_CAR_VARONES_CON_COLECTOR.xlsx guarda formulas sin valores calculados; se recalcula
una copia con LibreOffice (sin tocar el original) y se guarda el resultado en _calc/metrado_planilla.json. Los cuadros
de las laminas leen ese archivo: los planos muestran el metrado del presupuesto, no un recalculo propio.
"""
import os, json, shutil, subprocess, tempfile, hashlib
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
import sys; sys.path.insert(0, AQUI)
import diseno_v as dz

XLSX = os.path.join(dz.SAL, "METRADO_DRENAJE_PLUVIAL_CAR_VARONES_CON_COLECTOR.xlsx")
JSON = os.path.join(dz.CALC, "metrado_planilla.json")


def _md5(fn):
    return hashlib.md5(open(fn, "rb").read()).hexdigest()


def _recalcular():
    import openpyxl, warnings
    tmp = tempfile.mkdtemp()
    try:
        src = os.path.join(tmp, "metrado.xlsx"); shutil.copy(XLSX, src)
        subprocess.run(["soffice", "--headless", "--convert-to", "xlsx:Calc MS Excel 2007 XML", "--outdir", os.path.join(tmp, "out"), src],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wb = openpyxl.load_workbook(os.path.join(tmp, "out", "metrado.xlsx"), data_only=True)
        part = {}
        for r in wb["RESUMEN"].iter_rows(values_only=True):
            if r[0] and str(r[0]).startswith("01.04.04."):
                part[str(r[0])] = dict(desc=str(r[1]), und=r[2] or "", valor=r[3])
        return part
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def planilla():
    """{codigo: {desc, und, valor}} de las partidas 01.04.04; se recalcula solo si la planilla cambio."""
    md5 = _md5(XLSX)
    if os.path.exists(JSON):
        d = json.load(open(JSON, encoding="utf8"))
        if d.get("md5") == md5: return d["partidas"]
    part = _recalcular()
    json.dump(dict(fuente=os.path.relpath(XLSX, RAIZ), md5=md5, partidas=part), open(JSON, "w", encoding="utf8"), indent=1, ensure_ascii=False)
    return part


def valor(cod):
    return planilla()[cod]["valor"]


if __name__ == "__main__":
    for k, v in planilla().items():
        print(k, v["und"], v["valor"], v["desc"][:70])
