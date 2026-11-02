# -*- coding: utf-8 -*-
"""Carátula del estudio de gestión de riesgos en la planificación de la ejecución de la obra - CAR Mujeres (CUI 2717013).
Mismo diseño e imágenes que las carátulas de drenaje del proyecto (herramientas/mujeres/caratulas_m.py): logo del Gobierno
Regional San Martín, vista 3D del CAR, franja granate con el título y vista aérea del terreno. Sin nombre ni CIP del especialista.
Uso: python3 gestion_riesgos/herramientas/caratula_car_mujeres.py"""
import os, sys

import docx
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "herramientas", "mujeres"))
import caratulas_m as CM

SALIDA = os.path.join(RAIZ, "gestion_riesgos", "proyectos", "CAR_MUJERES_MORALES", "entregables",
                      "CARATULA_GESTION_RIESGOS_EJECUCION_OBRA_CAR_MUJERES.docx")
CM.SERVICIO = "EXPEDIENTE TÉCNICO DEL PROYECTO DE INVERSIÓN:"
CM.FECHA = "NOVIEMBRE - 2026"
TITULO, SUBTITULO = "GESTIÓN DE RIESGOS", "EN LA PLANIFICACIÓN DE LA EJECUCIÓN DE LA OBRA"


def generar():
    img = CM.imagenes()
    d = docx.Document()
    st = d.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial"); st.paragraph_format.space_after = Pt(0)
    s = d.sections[0]; s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = Cm(2.3); s.bottom_margin = Cm(1.2)
    if d.paragraphs: d.element.body.remove(d.paragraphs[0]._p)
    CM.caratula(d, img, TITULO, SUBTITULO, True)
    d.core_properties.author = ""
    d.core_properties.title = "Carátula - Gestión de riesgos en la ejecución de la obra - CAR Mujeres"
    d.save(SALIDA)
    return SALIDA


if __name__ == "__main__":
    print(generar())
