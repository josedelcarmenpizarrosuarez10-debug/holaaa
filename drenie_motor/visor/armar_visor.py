"""Arma un visor con la escena incluida (y, si se da, el resultado del diseno con sus observaciones y soluciones):
python visor/armar_visor.py escena.json salida.html [resultado.json]"""
import json
import os
import sys


def armar(escena, salida, resultado=None):
    base = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "visor.html"), encoding="utf-8").read()
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


if __name__ == "__main__":
    print(armar(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
