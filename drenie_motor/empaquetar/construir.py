"""Compila el motor de la red de cunetas (drenie-motor.exe) para el instalador de DrenIE 3.1.0 y lo prueba.

    python construir.py [carpeta_destino]     (por defecto ../../client/src-tauri/motor-dist, la que usa tauri.conf.json)

Pruebas del ejecutable compilado: sin la ficha de sesion de DrenIE debe negarse; con ella debe leer las capas del plano de
prueba. Termina con codigo distinto de 0 si algo falla (PROBAR_Y_COMPILAR.ps1 se detiene)."""
import hashlib
import hmac
import json
import os
import shutil
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DESTINO = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(RAIZ, "..", "client", "src-tauri", "motor-dist"))
CLAVE = bytes.fromhex("5d0e9b3a7c41f26e8a19d4c07b3e52f1a6c98d2e40b71f53c8e6a29d1047fb3c")
PLANO = os.path.join(RAIZ, "pruebas", "sitios", "S04", "PLANO.dxf")


def ficha():
    t = str(int(time.time()))
    return t + "." + hmac.new(CLAVE, t.encode(), hashlib.sha256).hexdigest()


def correr(exe, args, sesion=None):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    env.pop("DRENIE_SESION", None)
    if sesion: env["DRENIE_SESION"] = sesion
    r = subprocess.run([exe] + args, capture_output=True, env=env, timeout=600)
    return json.loads(r.stdout.decode("utf-8").strip() or "{}")


def main():
    trabajo = os.path.join(AQUI, "build")
    if os.path.isdir(DESTINO): shutil.rmtree(DESTINO)
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--distpath", DESTINO, "--workpath", trabajo,
                    os.path.join(AQUI, "drenie-motor.spec")], check=True)
    exe = os.path.join(DESTINO, "drenie-motor", "drenie-motor.exe" if os.name == "nt" else "drenie-motor")
    if not os.path.isfile(exe): sys.exit("No se genero %s" % exe)
    sin = correr(exe, ["capas", PLANO])
    if "solo funciona desde el programa DrenIE" not in sin.get("error", ""): sys.exit("El motor trabajo sin la ficha de sesion: %s" % sin)
    con = correr(exe, ["capas", PLANO], ficha())
    if con.get("sugeridas", {}).get("cerco") != "CERCO": sys.exit("El motor compilado no leyo el plano de prueba: %s" % con)
    nor = correr(exe, ["normas"], ficha())
    if len(nor.get("datos", [])) < 20: sys.exit("El motor compilado no trae la biblioteca de normas: %s" % str(nor)[:300])
    tam = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(os.path.dirname(exe)) for f in fs)
    print("OK · motor de la red de cunetas compilado y probado · %s (%.0f MB)" % (exe, tam / 1e6))


if __name__ == "__main__":
    main()
