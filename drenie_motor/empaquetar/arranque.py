"""Punto de entrada del motor empaquetado (drenie-motor.exe) que DrenIE llama como programa auxiliar."""
import os
import sys
import tempfile

if getattr(sys, "frozen", False):
    # cache de matplotlib fuera de la carpeta de instalacion (que puede ser de solo lectura)
    os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.environ.get("LOCALAPPDATA") or tempfile.gettempdir(), "DrenIE", "motor", "mpl"))
    os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

from drenie_motor.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
