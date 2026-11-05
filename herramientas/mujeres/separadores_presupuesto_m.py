# -*- coding: utf-8 -*-
"""Separadores de la carpeta 07 PRESUPUESTO del expediente técnico del CAR Mujeres (Wilma, CUI 2717013), en PowerPoint.

Mismo diseño que separadores_m.py (estilo de la carátula E, marca de agua con la vista aérea). La lista sale de la carpeta
"07 PRESUPUESTO" del Drive de la usuaria (estructura copiada en insumos/wilma/presupuesto_drive/ARBOL_CARPETA_07_PRESUPUESTO.json):
un separador para la carpeta, uno por cada subcarpeta 01 a 13 y uno para cada componente de 07. GASTOS GENERALES. Los títulos son
los nombres de las subcarpetas con sus tildes.

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
       ('07.03', 'PRESUPUESTO POR COMPONENTE'),
       ('07.04', 'ANÁLISIS DE COSTOS UNITARIOS'),
       ('07.05', 'RELACIÓN DE INSUMOS'),
       ('07.06', 'FÓRMULA POLINÓMICA'),
       ('07.07', 'GASTOS GENERALES'),
       ('07.07.01', 'GASTOS GENERALES - COMPONENTE I'),
       ('07.07.02', 'GASTOS GENERALES - COMPONENTE II'),
       ('07.08', 'GASTOS DE SUPERVISIÓN'),
       ('07.09', 'GASTOS ADMINISTRATIVOS'),
       ('07.10', 'COSTOS DE LA MANO DE OBRA'),
       ('07.11', 'RELACIÓN DE EQUIPO MÍNIMO'),
       ('07.12', 'PROGRAMACIÓN'),
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
