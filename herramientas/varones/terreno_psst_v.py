# -*- coding: utf-8 -*-
"""CAR Varones (CUI 2705619): área y perímetro del terreno en el PSST del usuario (versión con el presupuesto actualizado, 13-11-2026).

Dato nuevo: cuadro de datos técnicos del plano de ubicación (vértices A-J): 9,686.08 m² (0.96861 ha) y 398.86 ml.
Antes el PSST decía 6,999.98 m² y 336.89 m. Los linderos del cuadro N.° 2 ya eran los del polígono nuevo y no se tocan.
Solo cambian esos dos datos; el resto del Word queda igual. Las especificaciones técnicas y el Excel del presupuesto del PSST
no citan el terreno y no se modifican.

Uso: python3 herramientas/varones/terreno_psst_v.py
Entrada: insumos/katiuska/psst/PSST - VARONES.docx (no se modifica)
Salida: entregables_varones/psst/PSST - VARONES.docx
"""
import os
import sys

import docx
from docx.oxml.ns import qn

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas', 'mujeres'))
from terreno_actualizado_m import reemplazar  # noqa: E402  (reemplazo dentro del párrafo aunque esté partido en runs)

ENT = os.path.join(RAIZ, 'insumos/katiuska/psst/PSST - VARONES.docx')
SAL = os.path.join(RAIZ, 'entregables_varones/psst/PSST - VARONES.docx')
CAMBIOS = [('Terreno de 6,999.98 m² y 336.89 m de perímetro', 'Terreno de 9,686.08 m² y 398.86 m de perímetro'),
           ('terreno de 6,999.98 m² con frente', 'terreno de 9,686.08 m² con frente')]


def generar():
    d = docx.Document(ENT)
    n = 0
    for p in d.element.body.iter(qn('w:p')):
        for viejo, nuevo in CAMBIOS:
            while reemplazar(p, viejo, nuevo):
                n += 1
    os.makedirs(os.path.dirname(SAL), exist_ok=True)
    d.save(SAL)
    return n


if __name__ == '__main__':
    print(generar(), 'cambios ->', SAL)
