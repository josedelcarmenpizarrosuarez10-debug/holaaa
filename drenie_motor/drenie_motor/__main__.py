"""Linea de comandos del motor (la usa DrenIE como programa auxiliar).

    python -m drenie_motor lluvia  proyecto.json   (lluvia de diseno desde los datos de la estacion)
    python -m drenie_motor leer    proyecto.json
    python -m drenie_motor disenar proyecto.json
    python -m drenie_motor aplicar proyecto.json OBSERVACION OPCION   (solucion de la ventana de soluciones y nuevo calculo)
    python -m drenie_motor capas plano.dxf | crear (JSON por stdin) | vista proyecto.json | ediciones proyecto.json (JSON por stdin)
                           | datos proyecto.json (JSON por stdin) | entregables proyecto.json | abrir proyecto.json [ARCHIVO]
                           (ordenes de la pagina Red de cunetas)
    python -m drenie_motor ubicacion proyecto.json | pisco | vial [CARPETA] | vial_entregables CARPETA
                           (JSON por stdin; vial = drenaje vial MTC: calculo, o con CARPETA los entregables)

Escribe lectura.json o resultado.json en la carpeta de salida del proyecto y un resumen JSON en la salida estandar.
Codigo de salida: 0 bien, 2 error de datos, 3 error interno (mensaje en espanol en "error"; el detalle tecnico queda en
REGISTRO_DE_ERROR.txt de la carpeta de salida).
"""
import hashlib
import hmac
import json
import os
import sys
import time

from . import motor

# Ficha de sesion: el motor empaquetado solo trabaja cuando lo llama DrenIE (la misma clave esta en motor_red.rs).
_CLAVE_SESION = bytes.fromhex("5d0e9b3a7c41f26e8a19d4c07b3e52f1a6c98d2e40b71f53c8e6a29d1047fb3c")


def _sesion_valida():
    if not getattr(sys, "frozen", False): return True            # desde el codigo fuente (desarrollo y pruebas)
    ficha = os.environ.get("DRENIE_SESION", "")
    try:
        ts, firma = ficha.split(".", 1); t = int(ts)
    except ValueError:
        return False
    esperada = hmac.new(_CLAVE_SESION, ts.encode(), hashlib.sha256).hexdigest()
    return abs(time.time() - t) < 300 and hmac.compare_digest(esperada, firma)


_SALIDA = sys.stdout


def _emitir(obj, **kw):
    """Unica escritura en la salida estandar (UTF-8): lo que impriman las bibliotecas durante el calculo va al registro (stderr)."""
    _SALIDA.write(json.dumps(obj, ensure_ascii=False, **kw) + "\n"); _SALIDA.flush()


def _entrada():
    datos = sys.stdin.buffer.read().decode("utf-8-sig").strip()
    return json.loads(datos) if datos else {}


ESCRITORIO = {"capas": (1, 1), "crear": (0, 0), "vista": (1, 1), "ediciones": (1, 1), "datos": (1, 1), "entregables": (1, 1), "abrir": (1, 2), "normas": (0, 0), "para_drenie": (1, 1), "ubicacion": (1, 1), "pisco": (0, 0), "vial": (0, 1), "vial_entregables": (1, 1)}


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
    global _SALIDA
    argv = argv if argv is not None else sys.argv[1:]
    _SALIDA = sys.stdout
    try: _SALIDA.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError): pass
    sys.stdout = sys.stderr
    try: return _main(argv)
    finally: sys.stdout = _SALIDA


def _main(argv):
    if not _sesion_valida():
        _emitir({"error": "El motor de DrenIE solo funciona desde el programa DrenIE.", "tipo": "datos"}); return 2
    if argv and argv[0] in ESCRITORIO:
        return _escritorio(argv)
    if not ((len(argv) == 2 and argv[0] in ("lluvia", "leer", "disenar")) or (len(argv) == 4 and argv[0] == "aplicar")):
        _SALIDA.write(__doc__); return 1
    try:
        if argv[0] == "aplicar": out = motor.aplicar(argv[1], argv[2], argv[3])
        else: out = {"lluvia": motor.lluvia, "leer": motor.leer, "disenar": motor.disenar}[argv[0]](argv[1])
    except (ValueError, FileNotFoundError) as e:
        _emitir({"error": str(e), "tipo": "datos"}); return 2
    except Exception as e:                                          # nunca se cae sin explicar: registro y mensaje en espanol
        reg = _registrar(argv[1], argv[0])
        _emitir({"error": "El programa no pudo terminar el calculo (%s). No es un error de sus datos: envie el archivo de registro "
                                   "%s al soporte de DrenIE. Lo que se alcanzo a generar queda en la carpeta de salida." % (
                                       type(e).__name__, reg or "(sin registro)"), "tipo": "interno", "registro": reg})
        return 3
    corto = {k: out[k] for k in ("accion", "resumen", "avisos", "archivos", "imagen_control", "segundos", "requiere_confirmacion") if k in out}
    if out.get("observaciones"):
        corto["observaciones"] = [{"id": o["id"], "titulo": o["titulo"], "estado": o["estado"],
                                   "opciones": ["%s) %s" % (p["id"], p["texto"]) for p in o["opciones"]]} for o in out["observaciones"]]
    if isinstance(out.get("revision"), dict):
        corto["revision"] = {k: out["revision"].get(k) for k in ("comprobaciones", "no_cumple", "decisiones_proyectista")}
    if "verificacion" in out:
        corto["comprobaciones"] = [(c["n"], c["estado"]) for c in out["verificacion"]["comprobaciones"]]
    _emitir(corto, indent=1)
    return 0


def _escritorio(argv):
    """Ordenes de la pagina Red de cunetas: siempre responden un JSON (con "error" en espanol si algo falla)."""
    from . import escritorio
    lo, hi = ESCRITORIO[argv[0]]
    if not lo <= len(argv) - 1 <= hi:
        _emitir({"error": "Orden incompleta: %s" % argv[0], "tipo": "datos"}); return 1
    try:
        a = argv[0]
        if a == "capas": out = escritorio.capas(argv[1])
        elif a == "crear": out = escritorio.crear(_entrada())
        elif a == "vista": out = escritorio.vista(argv[1])
        elif a == "ediciones": out = escritorio.ediciones(argv[1], _entrada())
        elif a == "datos": out = escritorio.datos(argv[1], _entrada())
        elif a == "entregables": out = escritorio.entregables(argv[1])
        elif a == "normas": out = escritorio.normas_fuentes()
        elif a == "para_drenie": out = escritorio.para_drenie(argv[1])
        elif a == "ubicacion": out = escritorio.ubicacion(argv[1], _entrada())
        elif a == "pisco": out = escritorio.pisco(_entrada())
        elif a == "vial": out = escritorio.vial(_entrada(), argv[1] if len(argv) > 1 else None)
        elif a == "vial_entregables": out = escritorio.vial(_entrada(), argv[1])
        else: out = escritorio.abrir(argv[1], argv[2] if len(argv) > 2 else None)
    except (ValueError, FileNotFoundError, KeyError) as e:
        _emitir({"error": str(e).strip("'\"") or type(e).__name__, "tipo": "datos"}); return 2
    except Exception as e:
        _emitir({"error": "No se pudo completar la orden %s (%s: %s)." % (argv[0], type(e).__name__, e), "tipo": "interno"}); return 3
    _emitir(out, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
