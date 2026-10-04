@echo off
REM Genera MetraP.exe (un solo archivo, interfaz moderna PyQt6) en la carpeta dist\
REM Requisitos: Python 3.10 a 3.12 instalado en Windows, con pip.
cd /d %~dp0
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name MetraP ^
  --add-data "plantilla\PLANTILLA_METRADO_CUNETAS.xlsx;plantilla" ^
  --add-data "metrap_config.json;." ^
  --hidden-import ezdxf --hidden-import openpyxl ^
  --hidden-import matplotlib.backends.backend_qtagg --hidden-import PyQt6.QtPrintSupport ^
  --collect-all ezdxf --collect-all pycel --collect-submodules openpyxl ^
  metrap_app.py
echo.
echo Listo: dist\MetraP.exe  (copie junto a el metrap_config.json si desea editar la configuracion)
pause
