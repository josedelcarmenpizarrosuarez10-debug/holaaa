"""Compila el motor de la red de cunetas (drenie-motor.exe) para el instalador de DrenIE 3.1.0 y lo prueba.

    python construir.py [carpeta_destino] [--sin-compilar]
    (destino por defecto ../../client/src-tauri/motor-dist, la que usa tauri.conf.json)

Proteccion del codigo: primero Nuitka compila el paquete drenie_motor a un modulo binario (C compilado; en Windows usa Visual
Studio si esta instalado o descarga su propio compilador MinGW64 la primera vez); PyInstaller empaqueta ese modulo en lugar del
bytecode (drenie-motor.spec, DRENIE_MOTOR_COMPILADO) y se comprueba que ningun modulo de drenie_motor quede como bytecode.
--sin-compilar: solo para pruebas internas (no se entrega a clientes).

Pruebas del ejecutable compilado: sin la ficha de sesion de DrenIE debe negarse; con ella debe leer las capas del plano de
prueba. Termina con codigo distinto de 0 si algo falla (PROBAR_Y_COMPILAR.ps1 se detiene)."""
import hashlib
import hmac
import json
import os
import shutil
import stat
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SIN_COMPILAR = "--sin-compilar" in sys.argv
DESTINO = os.path.abspath(ARGS[0]) if ARGS else os.path.normpath(os.path.join(RAIZ, "..", "client", "src-tauri", "motor-dist"))
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


def compilar(salida):
    """Modulo binario del paquete drenie_motor con Nuitka; devuelve la ruta del .pyd (Windows) o .so."""
    borrar(salida)
    os.makedirs(salida)
    subprocess.run([sys.executable, "-m", "nuitka", "--module", os.path.join(RAIZ, "drenie_motor"), "--include-package=drenie_motor",
                    "--output-dir=" + salida, "--remove-output", "--no-pyi-file", "--assume-yes-for-downloads"], check=True, cwd=RAIZ)
    mod = [f for f in os.listdir(salida) if f.startswith("drenie_motor.") and f.endswith((".pyd", ".so"))]
    if len(mod) != 1: sys.exit("Nuitka no genero el modulo compilado del motor: %s" % os.listdir(salida))
    return os.path.join(salida, mod[0])


def borrar(carpeta):
    """Borra una carpeta aunque Windows la tenga ocupada un momento (antivirus o indexador): reintenta y quita «solo lectura»."""
    def quitar_lectura(func, ruta, _):
        try: os.chmod(ruta, stat.S_IWRITE); func(ruta)
        except OSError: pass
    for intento in range(5):
        if not os.path.isdir(carpeta): return
        shutil.rmtree(carpeta, onerror=quitar_lectura)
        if os.path.isdir(carpeta): time.sleep(2 * (intento + 1))
    if os.path.isdir(carpeta): sys.exit("No se pudo borrar %s: cierre DrenIE y el explorador en esa carpeta y vuelva a ejecutar" % carpeta)


def empaquetar(trabajo, env):
    """PyInstaller con su propia carpeta de trabajo; si falla (archivo bloqueado en Windows), un segundo intento desde cero."""
    for intento in (1, 2):
        borrar(trabajo); borrar(DESTINO)
        r = subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--distpath", DESTINO, "--workpath", trabajo,
                            os.path.join(AQUI, "drenie-motor.spec")], env=env)
        if r.returncode == 0: return
        print("PyInstaller fallo (intento %d de 2)%s" % (intento, "; se repite desde cero" if intento == 1 else ""), flush=True)
        time.sleep(5)
    sys.exit("PyInstaller no pudo empaquetar el motor (ver los mensajes de arriba)")


def sin_bytecode(trabajo):
    """Ningun modulo del paquete drenie_motor puede quedar como bytecode dentro del ejecutable."""
    from PyInstaller.archive.readers import ZlibArchiveReader
    pyz = [os.path.join(d, f) for d, _, fs in os.walk(trabajo) for f in fs if f.endswith(".pyz")]
    if not pyz: sys.exit("No se encontro el archivo PYZ del empaquetado")
    for p in pyz:
        malos = [n for n in ZlibArchiveReader(p).toc if n == "drenie_motor" or n.startswith("drenie_motor.")]
        if malos: sys.exit("Quedo codigo del motor como bytecode: %s" % ", ".join(malos[:5]))


def main():
    # cada ejecucion en carpetas nuevas: nada de una compilacion anterior (o bloqueado por Windows) entra en esta
    base = os.path.join(AQUI, "build"); borrar(base)
    marca = time.strftime("%Y%m%d-%H%M%S")
    nuitka, trabajo = os.path.join(base, "nuitka-" + marca), os.path.join(base, "pyinstaller-" + marca)
    env = dict(os.environ); env.pop("DRENIE_MOTOR_COMPILADO", None)
    if not SIN_COMPILAR:
        env["DRENIE_MOTOR_COMPILADO"] = compilar(nuitka)
    empaquetar(trabajo, env)
    if not SIN_COMPILAR: sin_bytecode(trabajo)
    exe = os.path.join(DESTINO, "drenie-motor", "drenie-motor.exe" if os.name == "nt" else "drenie-motor")
    if not os.path.isfile(exe): sys.exit("No se genero %s" % exe)
    sin = correr(exe, ["capas", PLANO])
    if "solo funciona desde el programa DrenIE" not in sin.get("error", ""): sys.exit("El motor trabajo sin la ficha de sesion: %s" % sin)
    con = correr(exe, ["capas", PLANO], ficha())
    if con.get("sugeridas", {}).get("cerco") != "CERCO": sys.exit("El motor compilado no leyo el plano de prueba: %s" % con)
    nor = correr(exe, ["normas"], ficha())
    if len(nor.get("datos", [])) < 20: sys.exit("El motor compilado no trae la biblioteca de normas: %s" % str(nor)[:300])
    libs = [f for d, _, fs in os.walk(os.path.dirname(exe)) for f in fs if "swmm5" in f.lower()]
    if not libs: sys.exit("El motor compilado no trae el motor de EPA SWMM (swmm-toolkit)")
    tam = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(os.path.dirname(exe)) for f in fs)
    print("OK · motor de la red de cunetas compilado y probado · %s (%.0f MB)" % (exe, tam / 1e6))


if __name__ == "__main__":
    main()
