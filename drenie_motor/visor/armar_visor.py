"""Arma un visor con la escena incluida (y, si se da, el resultado del diseno con sus observaciones y soluciones):
python visor/armar_visor.py escena.json salida.html [resultado.json]   (la logica esta en drenie_motor/visor_html.py)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from drenie_motor.visor_html import armar  # noqa: E402

if __name__ == "__main__":
    print(armar(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
