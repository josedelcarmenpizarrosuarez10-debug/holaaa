# PyInstaller 6 · motor de la red de cunetas para DrenIE 3.1.0 (carpeta drenie-motor con drenie-motor.exe).
# Uso:  python -m PyInstaller --noconfirm --clean --distpath dist --workpath build drenie-motor.spec
# Es programa de consola: DrenIE lo abre sin ventana (CREATE_NO_WINDOW) y le habla por la entrada y la salida estandar.
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

raiz = os.path.abspath(os.path.join(SPECPATH, ".."))
datas = [(os.path.join(raiz, "visor", "visor.html"), "visor")]
# archivos de datos del paquete (biblioteca de normas, límites del INEI y lluvias PISCO)
datas += [(os.path.join(raiz, "drenie_motor", f), "drenie_motor") for f in os.listdir(os.path.join(raiz, "drenie_motor")) if f.endswith((".json", ".npz"))]
for paquete in ("docx", "ezdxf", "openpyxl"):
    datas += collect_data_files(paquete)
# python-docx busca sus plantillas como docx/parts/../templates: la carpeta parts debe existir junto a templates
import docx
datas.append((os.path.join(os.path.dirname(docx.__file__), "parts", "__init__.py"), os.path.join("docx", "parts")))
ocultos = collect_submodules("drenie_motor") + collect_submodules("pycel") + ["matplotlib.backends.backend_agg"]
# motor de EPA SWMM 5 (swmm-toolkit): sus bibliotecas compiladas (swmm5 y swmm-output) van junto a los modulos
ocultos += collect_submodules("swmm.toolkit")
binarios = collect_dynamic_libs("swmm.toolkit")

a = Analysis([os.path.join(SPECPATH, "arranque.py")], pathex=[raiz], datas=datas, binaries=binarios, hiddenimports=ocultos,
             excludes=["tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "IPython", "pytest", "notebook", "matplotlib.backends.backend_tkagg"],
             noarchive=False)
# proteccion del codigo: con DRENIE_MOTOR_COMPILADO (modulo de Nuitka: drenie_motor.*.pyd / .so) el paquete drenie_motor no va como
# bytecode; el analisis anterior uso el codigo fuente solo para encontrar las bibliotecas que necesita
COMPILADO = os.environ.get("DRENIE_MOTOR_COMPILADO")
if COMPILADO:
    a.pure = [x for x in a.pure if not (x[0] == "drenie_motor" or x[0].startswith("drenie_motor."))]
    a.binaries = a.binaries + [(os.path.basename(COMPILADO), COMPILADO, "BINARY")]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="drenie-motor", console=True, upx=False, strip=False,
          version=os.path.join(SPECPATH, "version_motor.txt") if os.name == "nt" else None)
coll = COLLECT(exe, a.binaries, a.datas, name="drenie-motor", upx=False, strip=False)
