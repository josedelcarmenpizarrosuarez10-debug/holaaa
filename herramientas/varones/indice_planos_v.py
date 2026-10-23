# -*- coding: utf-8 -*-
"""Índice de planos de drenaje pluvial - CAR Varones (CUI 2705619), en Word.

Fuente: el juego de láminas en PDF de la usuaria Katiuska (insumos/katiuska/PLANOS_DRENAJE_PLUVIAL_CAR_VARONES_LAMINAS.pdf,
44 láminas DPLV, setiembre 2026). Mismo motor que el índice del Hogar de Refugio (indice_planos_refugio.py): código y título de cada
rótulo tal como están; a pedido de la usuaria, ordenado por número de lámina, de la DPLV-01 a la DPLV-44.

Uso: python3 herramientas/varones/indice_planos_v.py
Salida: entregables_varones/INDICE_DE_PLANOS_DRENAJE_PLUVIAL_CAR_VARONES.docx y entregables_varones/_calc/indice_planos.json
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.dirname(AQUI))
import indice_planos_refugio as I

I.PDF = os.path.join(RAIZ, 'insumos/katiuska/PLANOS_DRENAJE_PLUVIAL_CAR_VARONES_LAMINAS.pdf')
I.DATOS = os.path.join(RAIZ, 'entregables_varones/_calc/indice_planos.json')
I.SALIDA = os.path.join(RAIZ, 'entregables_varones/INDICE_DE_PLANOS_DRENAJE_PLUVIAL_CAR_VARONES.docx')
I.CUI = '2705619'
I.PROYECTO = ('“CREACIÓN DEL SERVICIO DE PROTECCIÓN INTEGRAL A NIÑAS, NIÑOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE '
              'PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES DISTRITO DE MORALES DE LA PROVINCIA DE SAN MARTÍN DEL '
              'DEPARTAMENTO DE SAN MARTÍN”')
I.CORTO = 'CAR VARONES - MORALES, SAN MARTÍN'
I.UBIC = 'Distrito de Morales, provincia y departamento de San Martín'
I.ORDEN = 'numero'                         # pedido de la usuaria: de la lámina 1 a la última, sucesivamente

# Título de cada rótulo (código tal cual el rótulo, incluso DPVL-09, DPVL-10 y DVPL-11); se comprueba contra el PDF.
I.TITULOS = {
    'DPLV-01': 'RED GENERAL DRENAJE PLUVIAL',
    'DPLV-02': 'SECCIONES TRANSVERSALES 01', 'DPLV-03': 'SECCIONES TRANSVERSALES 02', 'DPLV-04': 'SECCIONES TRANSVERSALES 03',
    'DPLV-05': 'PERFILES LONGITUDINALES 01', 'DPLV-06': 'PERFILES LONGITUDINALES 02',
    'DPLV-07': 'DETALLE MONTANTE EDIFICACIÓN 01', 'DPLV-08': 'DETALLE MONTANTE EDIFICACIÓN 02',
    'DPVL-09': 'DETALLE MONTANTE EDIFICACIÓN 03', 'DPVL-10': 'DETALLE MONTANTE EDIFICACIÓN 04',
    'DVPL-11': 'DETALLE MONTANTE EDIFICACIÓN 05', 'DPLV-12': 'DETALLE MONTANTE EDIFICACIÓN 06',
    'DPLV-13': 'DETALLE MONTANTE EDIFICACIÓN 07', 'DPLV-14': 'DETALLE MONTANTE EDIFICACIÓN 08',
    'DPLV-15': 'DETALLE MONTANTE EDIFICACIÓN 09', 'DPLV-16': 'DETALLE MONTANTE EDIFICACIÓN 10',
    'DPLV-17': 'PLANTA DEL COLECTOR PLUVIAL',
    'DPLV-18': 'PERFIL LONGITUDINAL GENERAL DEL COLECTOR',
    'DPLV-19': 'PERFIL LONGITUDINAL DETALLADO DEL COLECTOR', 'DPLV-20': 'PERFIL LONGITUDINAL DETALLADO DEL COLECTOR',
    'DPLV-21': 'SECCIONES TRANSVERSALES DEL COLECTOR', 'DPLV-22': 'SECCIONES TRANSVERSALES DEL COLECTOR',
    'DPLV-23': 'DETALLE DE REGISTRO DE LIMPIEZA - TAPA CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08',
    'DPLV-24': 'DETALLE DEL EMPALME DE CUNETA AL COLECTOR',
    'DPLV-25': 'EMPALME DEL COLECTOR CON LA CAJA DE LLEGADA CL DEL HOGAR DE REFUGIO',
    'DPLV-26': 'REGISTRO DE LIMPIEZA CON TAPA CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08 - COMPONENTES',
    'DPLV-27': 'DETALLE CONSTRUCTIVO: REBAJE DE ASIENTO DE LA TAPA CIEGA Y REFUERZO DE BORDE DEL REGISTRO',
    'DPLV-28': 'DETALLE CONSTRUCTIVO: TAPA CIEGA DE CONCRETO ARMADO 0.68x0.68x0.08 - FABRICACIÓN EN OBRA Y COLOCACIÓN',
    'DPLV-29': 'DETALLE CONSTRUCTIVO: JUNTAS E=1" CON TECNOPOR Y SELLADOR ASFÁLTICO (COLECTOR Y CAJA CL)',
    'DPLV-30': 'DETALLE CONSTRUCTIVO: EMPALME DE CUNETA AL COLECTOR (VENTANA EN MURO Y CAÍDA)',
    'DPLV-31': 'DETALLE DE JUNTA DE DILATACIÓN E=1" CON SELLADOR ASFÁLTICO EN CUNETAS (TODA LA SECCIÓN)',
    'DPLV-32': 'JUNTA DE DILATACIÓN EN CUNETAS: PROCESO CONSTRUCTIVO EN ISOMÉTRICO',
    'DPLV-33': 'REJILLA METÁLICA MÓVIL EN CUNETA DE PISO: DETALLE, DESPIECE E ISOMÉTRICOS',
    'DPLV-34': 'DETALLE ISOMÉTRICO INSTALACIÓN LLORADEROS PLUVIALES',
    'DPLV-35': 'DETALLE DE LLORADERO: CORTE, TUBO PERFORADO Y DESAGREGADO',
    'DPLV-36': 'DETALLES DE CANALETA DE TECHO, SOPORTE Y ACCESORIOS',
    'DPLV-37': 'ISOMÉTRICO DE CANALETA, SOPORTES, PERNOS, TAPA Y BOQUILLA',
    'DPLV-38': 'DETALLES 3D DE LOS ELEMENTOS DEL MONTANTE',
    'DPLV-39': 'ISOMÉTRICO DE LA CAJA SUMIDERO DE PISO',
    'DPLV-40': 'DETALLE DE CAJA SUMIDERO DE PISO: CORTE, PLANTA Y DESAGREGADO',
    'DPLV-41': 'ELEVACIÓN DE CANALETA Y CORTE DEL MONTANTE PLUVIAL',
    'DPLV-42': 'ISOMÉTRICO DEL MONTANTE PLUVIAL TÍPICO',
    'DPLV-43': 'PLANTA DE UBICACIÓN DE LLORADEROS EN CUNETAS COLINDANTES CON ÁREA VERDE',
    'DPLV-44': 'DETALLE CONTRUCTIVO FALSA COLUMNA PARA MONTANTE PLUVIAL',
}


def contenido(cod, t):
    """Lo que distingue a la lámina, leído de sus dibujos."""
    tit = I.TITULOS.get(cod, '')
    if tit.startswith(('SECCIONES TRANSVERSALES 0', 'PERFILES LONGITUDINALES')):
        s = sorted(set(int(x) for x in re.findall(r'SECCI[OÓ]N\s*(\d+)\b', t)))
        e = sorted(set(int(x) for x in re.findall(r'EJE\s*0?(\d+)', t)))
        txt = 'SECCIONES %02d A %02d' % (s[0], s[-1]) if s else ''
        return ('EJES %02d A %02d, CON LAS ' % (e[0], e[-1]) + txt) if tit.startswith('PERFILES') and e else txt
    m = re.findall(r'(PERFIL|TRAMO) (\d+): (\d\+\d{3}\.\d\d) A (\d\+\d{3}\.\d\d)', t)
    if m:
        return '%s %s A %s: PROG. %s A %s' % ({'PERFIL': 'PERFILES', 'TRAMO': 'TRAMOS'}[m[0][0]], m[0][1], m[-1][1], m[0][2], m[-1][3])
    s = sorted(set(int(x) for x in re.findall(r'SECCION S-(\d+)', t)))
    if s:
        return 'SECCIONES S-%02d A S-%02d' % (s[0], s[-1])
    if tit.startswith('DETALLE MONTANTE'):
        c = sorted(set(re.findall(r'CORTE ([A-Z])-\1', t)))
        return ('CORTE %s-%s' % (c[0], c[0]) if len(c) == 1 else 'CORTES ' + ' Y '.join('%s-%s' % (x, x) for x in c)) if c else ''
    return ''


I.contenido = contenido

if __name__ == '__main__':
    planos = I.leer_pdf()
    for p in planos:
        print('%-8s p%-3s %-3s %-9s %-62s | %s | %s' % (p['codigo'], p['pagina'], p['formato'], p['escala'], p['titulo'][:62],
                                                    p['contenido'][:60], ','.join(p['escalas_dibujo'])))
    print(I.generar(planos))
