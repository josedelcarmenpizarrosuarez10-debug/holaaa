"""Linea de comandos del motor (la usa DrenIE como programa auxiliar).

    python -m drenie_motor lluvia  proyecto.json   (lluvia de diseno desde los datos de la estacion)
    python -m drenie_motor leer    proyecto.json
    python -m drenie_motor disenar proyecto.json

Escribe lectura.json o resultado.json en la carpeta de salida del proyecto y un resumen JSON en la salida estandar.
Codigo de salida: 0 bien, 2 error de datos, 3 error interno (mensaje en espanol en "error"; el detalle tecnico queda en
REGISTRO_DE_ERROR.txt de la carpeta de salida).
"""
import json
import sys

from . import motor


def _registrar(cfg_ruta, accion):
    """Guarda el detalle tecnico del error en la carpeta de salida del proyecto (o junto al proyecto)."""
    import os, time, traceback
    try:
        cfg = json.load(open(cfg_ruta, encoding="utf-8"))
        base = os.path.dirname(os.path.abspath(cfg_ruta))
        sal = os.path.join(base, cfg.get("salida", "salida")); os.makedirs(sal, exist_ok=True)
    except Exception:
        sal = os.path.dirname(os.path.abspath(cfg_ruta))
    ruta = os.path.join(sal, "REGISTRO_DE_ERROR.txt")
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("DrenIE %s - %s - %s\n\n" % (getattr(motor, "VERSION", ""), accion, time.strftime("%Y-%m-%d %H:%M:%S")))
            f.write(traceback.format_exc())
        return ruta
    except Exception:
        return None


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 2 or argv[0] not in ("lluvia", "leer", "disenar"):
        print(__doc__); return 1
    try:
        out = {"lluvia": motor.lluvia, "leer": motor.leer, "disenar": motor.disenar}[argv[0]](argv[1])
    except (ValueError, FileNotFoundError) as e:
        print(json.dumps({"error": str(e), "tipo": "datos"}, ensure_ascii=False)); return 2
    except Exception as e:                                          # nunca se cae sin explicar: registro y mensaje en espanol
        reg = _registrar(argv[1], argv[0])
        print(json.dumps({"error": "El programa no pudo terminar el calculo (%s). No es un error de sus datos: envie el archivo de registro "
                                   "%s al soporte de DrenIE. Lo que se alcanzo a generar queda en la carpeta de salida." % (
                                       type(e).__name__, reg or "(sin registro)"), "tipo": "interno", "registro": reg}, ensure_ascii=False))
        return 3
    corto = {k: out[k] for k in ("accion", "resumen", "avisos", "archivos", "imagen_control", "segundos", "requiere_confirmacion") if k in out}
    if "verificacion" in out:
        corto["comprobaciones"] = [(c["n"], c["estado"]) for c in out["verificacion"]["comprobaciones"]]
    print(json.dumps(corto, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
