"""Linea de comandos del motor (la usa DrenIE como programa auxiliar).

    python -m drenie_motor leer    proyecto.json
    python -m drenie_motor disenar proyecto.json

Escribe lectura.json o resultado.json en la carpeta de salida del proyecto y un resumen JSON en la salida estandar.
Codigo de salida: 0 bien, 2 error de datos (mensaje en espanol en "error").
"""
import json
import sys

from . import motor


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 2 or argv[0] not in ("leer", "disenar"):
        print(__doc__); return 1
    try:
        out = motor.leer(argv[1]) if argv[0] == "leer" else motor.disenar(argv[1])
    except (ValueError, KeyError, FileNotFoundError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False)); return 2
    corto = {k: out[k] for k in ("accion", "resumen", "avisos", "archivos", "imagen_control", "segundos", "requiere_confirmacion") if k in out}
    if "verificacion" in out:
        corto["comprobaciones"] = [(c["n"], c["estado"]) for c in out["verificacion"]["comprobaciones"]]
    print(json.dumps(corto, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
