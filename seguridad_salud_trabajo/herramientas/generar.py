# -*- coding: utf-8 -*-
"""Genera el Plan de Seguridad y Salud en el Trabajo completo de un proyecto: IPERC, Excel, figuras y Word.

Uso:  python3 generar.py <carpeta del proyecto>
La carpeta debe tener insumos/DATOS_PROYECTO.xlsx (crear con importar_s10.py desde el presupuesto S10 o con --plantilla).
Salidas en <carpeta>/entregables:  PLAN_SEGURIDAD_SALUD_TRABAJO_<codigo>.docx  y  MATRIZ_IPERC_PSST_<codigo>.xlsx"""
import os, sys

AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import nucleo, iperc_xlsx, figuras, psst_docx

if __name__ == "__main__":
    carpeta = os.path.abspath(sys.argv[1])
    o = nucleo.construir(carpeta); r = o["resumen"]
    print("Actividades: %d | peligros: %d | significativos antes/después de los controles: %d / %d" % (r["n_act"], r["n"], r["sig_i"], r["sig_r"]))
    if o["sin_actividad"]:
        print("ATENCIÓN - partidas sin actividad reconocida (agregar palabras clave en biblioteca.py):")
        for s in o["sin_actividad"]: print("   ", s)
    iperc_xlsx.main(carpeta); figuras.main(carpeta); psst_docx.main(carpeta)
