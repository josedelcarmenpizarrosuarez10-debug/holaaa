"""VISOR_DRENIE.html: el visor (visor/visor.html) con la escena incluida y, si se da, el resultado del diseño con sus
observaciones y soluciones."""
import json
import os

VISOR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "visor", "visor.html")


def armar(escena, salida, resultado=None):
    base = open(VISOR, encoding="utf-8").read()
    datos = open(escena, encoding="utf-8").read().replace("</", "<\\/")
    marca = '<script id="escena-datos" type="application/json">null</script>'
    if marca not in base: raise ValueError("visor.html sin el bloque escena-datos")
    html = base.replace(marca, '<script id="escena-datos" type="application/json">' + datos + "</script>")
    if resultado and os.path.exists(resultado):
        R = json.load(open(resultado, encoding="utf-8"))
        res = {"observaciones": R.get("observaciones", []), "resumen": R.get("resumen", {}), "proyecto": R.get("proyecto", {})}
        marca_r = '<script id="resultado-datos" type="application/json">null</script>'
        if marca_r in html:
            html = html.replace(marca_r, '<script id="resultado-datos" type="application/json">' + json.dumps(res, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    with open(salida, "w", encoding="utf-8") as f: f.write(html)
    return salida

