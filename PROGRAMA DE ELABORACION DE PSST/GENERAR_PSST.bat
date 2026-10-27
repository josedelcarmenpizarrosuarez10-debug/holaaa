@echo off
REM Arrastrar la carpeta del proyecto sobre este archivo (la carpeta debe tener insumos\DATOS_PROYECTO.xlsx)
python "%~dp0herramientas\generar.py" "%~1"
pause
