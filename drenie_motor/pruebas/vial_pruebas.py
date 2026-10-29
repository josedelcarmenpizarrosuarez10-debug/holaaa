"""Pruebas del drenaje vial (vial.py y vial_excel.py): valores a mano, casos difíciles y datos con errores.

    python3 pruebas/vial_pruebas.py
"""
import copy
import json
import math
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from drenie_motor import vial as V, vial_excel  # noqa: E402

BASE = json.load(open(os.path.join(os.path.dirname(__file__), "..", "ejemplos", "vial", "vial_ejemplo.json"), encoding="utf-8"))
ok = 0


def caso(nombre, f):
    global ok
    f(); ok += 1; print("OK  ", nombre)


def cerca(a, b, tol=1e-3): assert abs(a - b) <= tol * max(1.0, abs(b)), (a, b)


def a_mano():
    R = V.calcular(BASE); c = R["cunetas"][0]
    A = 0.4 ** 2 * (3 + 0.5) / 2; P = 0.4 * (math.sqrt(10) + math.sqrt(1.25)); Vll = (A / P) ** (2 / 3) * math.sqrt(0.012) / 0.015
    cerca(c["V_lleno"], round(Vll, 2), 1e-2); cerca(c["Q_lleno"], A * Vll, 1e-3)
    T = 1 / (1 - 0.6 ** (1 / 15)); assert R["periodo_plataforma"]["T"] == math.ceil(T) == 30
    I = 60 * R["lluvia"]["P24_por_T"]["30"] * (10 / 1440) ** 0.25 / 10; cerca(c["I_mmh"], I, 1e-3)
    assert all(t["longitud"] <= 200 + 1e-9 for t in c["tramos"])           # región muy lluviosa: 200 m
    ac = next(a for a in R["alcantarillas"] if a["id"] == "AC-01")
    assert ac["tirante_rel"] <= 0.75 + 1e-9 and ac["Q_cunetas"] > 0           # borde libre 25 % y recibe CU-01


def sin_lluvia_serie():
    d = copy.deepcopy(BASE); d["lluvia"] = {"P24_por_T": {"25": 191.27, "50": 211.81, "100": 233.35}}
    R = V.calcular(d); assert 191 < R["lluvia"]["P24_por_T"]["30"] < 212


def region_seca_y_trapezoidal():
    d = copy.deepcopy(BASE); d["via"]["precipitacion_anual_mm"] = 350
    for c in d["cunetas"]: c.pop("seccion")
    R = V.calcular(d); c = R["cunetas"][0]
    assert c["seccion"]["d"] == 0.20 and c["L_norma"] == 250
    d["via"]["precipitacion_anual_mm"] = 3500; R = V.calcular(d)
    assert R["cunetas"][0]["seccion"]["tipo"] == "trapezoidal"


def velocidad_limita():
    d = copy.deepcopy(BASE); d["cunetas"][1]["pendiente"] = 0.12; d["cunetas"][1]["revestimiento"] = "tierra"
    d["cunetas"][1]["superficie"] = "Hierba"
    R = V.calcular(d); c = R["cunetas"][1]
    assert c["Q_capacidad"] < c["Q_lleno"] and c["tirante_capacidad"] < c["seccion"]["d"]


def marco_y_temez():
    d = copy.deepcopy(BASE)
    d["alcantarillas"].append({"id": "AC-03", "prog": 1100, "tipo": "cruce", "area_km2": 10.5, "L_m": 5200, "H_m": 380, "CN": 55,
                               "tipo_conducto": "MCA", "pendiente": 0.01})
    R = V.calcular(d); a = next(x for x in R["alcantarillas"] if x["id"] == "AC-03")
    assert "Témez" in a["hidrologia"]["metodo"] and a["seccion"]["tipo"] == "marco" and a["tirante_rel"] <= 0.75 + 1e-9


def selva_alta():
    d = copy.deepcopy(BASE); d["via"]["selva_alta"] = True
    R = V.calcular(d); assert all(a["seccion"]["pulg"] >= 48 for a in R["alcantarillas"] if a["seccion"]["tipo"] == "circular")


def errores_claros():
    for cambio, texto in ((lambda d: d["cunetas"][0].pop("pendiente"), "falta pendiente"),
                          (lambda d: d["alcantarillas"][0].update(H_m="abc"), "no es un número"),
                          (lambda d: d["alcantarillas"][0].update(H_m=0), "mayor que cero"),
                          (lambda d: d["cunetas"].append(dict(d["cunetas"][0])), "repetida"),
                          (lambda d: d.update(lluvia={}), "Falta la lluvia"),
                          (lambda d: d["alcantarillas"][0].update(area_km2=900), "770 km²")):
        d = copy.deepcopy(BASE); cambio(d)
        try: V.calcular(d)
        except ValueError as e: assert texto in str(e), (texto, str(e))
        else: raise AssertionError("no avisó: " + texto)


def caudal_grande():
    d = copy.deepcopy(BASE); d["alcantarillas"][1]["area_km2"] = 9.9; d["alcantarillas"][1]["L_m"] = 6000
    R = V.calcular(d); a = next(x for x in R["alcantarillas"] if x["id"] == "AC-02")
    assert a["seccion"].get("celdas", 1) >= 1 and a["Q"] > 30


def sin_cunetas():
    d = copy.deepcopy(BASE); d["cunetas"] = []
    for a in d["alcantarillas"]: a.pop("cunetas", None)
    d["badenes"][0].pop("cunetas", None)
    R = V.calcular(d); assert R["totales"]["alivios"] == 0 and len(R["alcantarillas"]) == 2


def plantilla_ida_y_vuelta():
    from drenie_motor import vial_plantilla
    with tempfile.TemporaryDirectory() as t:
        ruta = vial_plantilla.crear(os.path.join(t, "p.xlsx"), BASE)
        d = vial_plantilla.leer(ruta); d["lluvia"] = BASE["lluvia"]
        b = copy.deepcopy(BASE); b["alcantarillas"][0]["coberturas"] = b["alcantarillas"][0]["coberturas"][:1]   # la plantilla lleva una cobertura
        R1, R2 = V.calcular(b), V.calcular(d)
        assert R1["totales"] == R2["totales"], (R1["totales"], R2["totales"])
        assert [a["Q"] for a in R1["alcantarillas"]] == [a["Q"] for a in R2["alcantarillas"]]
        vacia = vial_plantilla.leer(vial_plantilla.crear(os.path.join(t, "v.xlsx")))
        assert vacia["cunetas"] == [] and vacia["via"]["velocidad_kmh"] == 40


def excel():
    R = V.calcular(BASE)
    with tempfile.TemporaryDirectory() as t:
        assert os.path.getsize(vial_excel.libro(os.path.join(t, "m.xlsx"), R)) > 10000


for n, f in list(globals().items()):
    if callable(f) and n not in ("caso", "cerca") and f.__module__ == "__main__": caso(n, f)
print("%d pruebas del drenaje vial correctas" % ok)
