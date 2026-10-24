"""Arma un visor con la escena incluida: python visor/armar_visor.py escena.json salida.html"""
import os
import sys


def armar(escena, salida):
    base = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "visor.html"), encoding="utf-8").read()
    datos = open(escena, encoding="utf-8").read().replace("</", "<\\/")
    marca = '<script id="escena-datos" type="application/json">null</script>'
    if marca not in base: raise ValueError("visor.html sin el bloque escena-datos")
    html = base.replace(marca, '<script id="escena-datos" type="application/json">' + datos + "</script>")
    with open(salida, "w", encoding="utf-8") as f: f.write(html)
    return salida


if __name__ == "__main__":
    print(armar(sys.argv[1], sys.argv[2]))
