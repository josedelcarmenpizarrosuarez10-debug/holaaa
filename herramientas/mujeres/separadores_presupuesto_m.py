# -*- coding: utf-8 -*-
"""Separadores de la carpeta 07 PRESUPUESTO del expediente técnico del CAR Mujeres (Wilma, CUI 2717013), en PowerPoint.

Mismo diseño que separadores_m.py (estilo de la carátula E, marca de agua con la vista aérea). La lista sale de la carpeta
"07 PRESUPUESTO" del Drive de la usuaria (estructura copiada en insumos/wilma/presupuesto_drive/ARBOL_CARPETA_07_PRESUPUESTO.json):
un separador para la carpeta, uno por cada subcarpeta 01 a 13, uno por cada sub-subcarpeta (componentes de 07. GASTOS GENERALES) y
uno por cada archivo de dentro (salvo cuando la carpeta tiene un solo archivo con su mismo nombre: 01 MEMORIA DE COSTOS y 13 JRD).
Los títulos son los nombres del Drive con sus tildes; "1"/"2" de los archivos se escribe "I"/"II" como en los demás.

Uso: python3 herramientas/mujeres/separadores_presupuesto_m.py
Salida: entregables_mujeres/SEPARADORES_PRESUPUESTO_CAR_MUJERES.pptx
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI); RAIZ = os.path.dirname(HER)
sys.path.insert(0, AQUI); sys.path.insert(0, HER)
import separadores_m as S  # noqa: E402
import caratulas_tomos_pptx as C  # noqa: E402

SALIDA = os.path.join(RAIZ, 'entregables_mujeres/SEPARADORES_PRESUPUESTO_CAR_MUJERES.pptx')
CAP = ('07', 'PRESUPUESTO')
SUB = [('07.01', 'MEMORIA DE COSTOS'),
       ('07.02', 'RESUMEN DE PRESUPUESTO'),
       ('07.02.01', 'RESUMEN GENERAL DEL PRESUPUESTO'),
       ('07.02.02', 'RESUMEN DEL PRESUPUESTO - COMPONENTE I'),
       ('07.02.03', 'RESUMEN DEL PRESUPUESTO - COMPONENTE II'),
       ('07.03', 'PRESUPUESTO POR COMPONENTE'),
       ('07.03.01', 'PRESUPUESTO - COMPONENTE I'),
       ('07.03.02', 'PRESUPUESTO - COMPONENTE II'),
       ('07.04', 'ANÁLISIS DE COSTOS UNITARIOS'),
       ('07.04.01', 'ANÁLISIS DE COSTOS UNITARIOS - COMPONENTE I'),
       ('07.04.02', 'ANÁLISIS DE COSTOS UNITARIOS - COMPONENTE II'),
       ('07.05', 'RELACIÓN DE INSUMOS'),
       ('07.05.01', 'RELACIÓN DE INSUMOS - COMPONENTE I'),
       ('07.05.02', 'RELACIÓN DE INSUMOS - COMPONENTE II'),
       ('07.06', 'FÓRMULA POLINÓMICA'),
       ('07.06.01', 'FÓRMULA POLINÓMICA - COMPONENTE I'),
       ('07.06.02', 'FÓRMULA POLINÓMICA - COMPONENTE II'),
       ('07.07', 'GASTOS GENERALES'),
       ('07.07.01', 'GASTOS GENERALES - COMPONENTE I'),
       ('07.07.01.01', 'CÁLCULO DE REMUNERACIONES - COMPONENTE I'),
       ('07.07.01.02', 'DESAGREGADO DE GASTOS GENERALES - COMPONENTE I'),
       ('07.07.01.03', 'GASTOS FIJOS - COMPONENTE I'),
       ('07.07.02', 'GASTOS GENERALES - COMPONENTE II'),
       ('07.07.02.01', 'CÁLCULO DE REMUNERACIONES - COMPONENTE II'),
       ('07.07.02.02', 'DESAGREGADO DE GASTOS GENERALES - COMPONENTE II'),
       ('07.07.02.03', 'GASTOS GENERALES FIJOS - COMPONENTE II'),
       ('07.07.03', 'RESUMEN DE GASTOS GENERALES'),
       ('07.08', 'GASTOS DE SUPERVISIÓN'),
       ('07.08.01', 'DESAGREGADO DE GASTOS DE SUPERVISIÓN'),
       ('07.08.02', 'DESAGREGADO DE GASTOS GENERALES DE SUPERVISIÓN'),
       ('07.08.03', 'DETALLES GENERALES DE SUPERVISIÓN'),
       ('07.09', 'GASTOS ADMINISTRATIVOS'),
       ('07.09.01', 'DESAGREGADO DE GASTOS ADMINISTRATIVOS'),
       ('07.10', 'COSTOS DE LA MANO DE OBRA'),
       ('07.10.01', 'CÁLCULO DE MANO DE OBRA'),
       ('07.11', 'RELACIÓN DE EQUIPO MÍNIMO'),
       ('07.12', 'PROGRAMACIÓN'),
       ('07.12.01', 'CALENDARIO DE AVANCE DE OBRA (CAO)'),
       ('07.12.02', 'PROGRAMACIÓN DE EJECUCIÓN DE OBRA'),
       ('07.13', 'JUNTA DE RESOLUCIÓN DE DISPUTAS (JRD)')]


def items():
    out, padres = [dict(cod=CAP[0], tit=CAP[1], nivel=0, ruta=[])], {0: CAP}
    for cod, tit in SUB:
        nivel = cod.count('.')
        padres[nivel] = (cod, tit)
        out.append(dict(cod=cod, tit=tit, nivel=nivel, ruta=[padres[k] for k in range(nivel)]))
    return out


def generar():
    marca = S.marca_agua()
    prs = C.presentacion()
    lista = items()
    for it in lista:
        S.separador(C.nueva(prs), it, marca)
    prs.core_properties.title = 'Separadores de presupuesto - CAR Mujeres'; prs.core_properties.author = ''
    prs.save(SALIDA)
    return SALIDA, lista


if __name__ == '__main__':
    s, lista = generar()
    for it in lista:
        print('%-10s %s' % (it['cod'], it['tit']))
    print(len(lista), 'separadores ->', s)
