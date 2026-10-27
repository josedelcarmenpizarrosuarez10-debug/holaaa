# -*- coding: utf-8 -*-
"""Memoria descriptiva de drenaje pluvial - CAR Varones (CUI 2705619).

Misma estructura y formato que la del Hogar de Refugio (memoria_descriptiva_refugio.py, de donde se toman la clase Memoria,
la carátula, el encabezado y los lectores del metrado), con los datos de este proyecto:
  - metrado vigente de la usuaria (insumos/metrados_vigentes/METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx; solo lectura),
  - memoria hidrológica de la usuaria (intensidad, coeficientes, secciones de canaletas y cunetas) y diseño del colector
    (entregables_varones/_calc/diseno.json),
  - juego de 44 láminas DPLV (entregables_varones/_calc/indice_planos.json, de varones/indice_planos_v.py).

Uso: python3 herramientas/varones/memoria_descriptiva_v.py
Salida: entregables_varones/MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL_CAR_VARONES.docx
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.dirname(AQUI))
import memoria_descriptiva_refugio as R
from memoria_descriptiva_refugio import f2

SAL = os.path.join(RAIZ, 'entregables_varones')
R.VIG = os.path.join(RAIZ, 'insumos/metrados_vigentes/METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx')
R.PDF = os.path.join(RAIZ, 'insumos/katiuska/PLANOS_DRENAJE_PLUVIAL_CAR_VARONES_LAMINAS.pdf')
R.INDICE = os.path.join(SAL, '_calc/indice_planos.json')
R.FIG = os.path.join(SAL, 'figuras_memoria_descriptiva')
R.PREV_OC = os.path.join(SAL, '_sin_vistas')
R.SALIDA = os.path.join(SAL, 'MEMORIA_DESCRIPTIVA_DRENAJE_PLUVIAL_CAR_VARONES.docx')
R.CUI = CUI = '2705619'
R.CORTO = 'CAR VARONES'
R.UBIC = 'Distrito de Morales, provincia y departamento de San Martín'
R.FECHA = 'SETIEMBRE 2026'                                            # fecha de los rotulos de los planos DPLV
R.LAM_CAR = ('DPLV-01', 'Red general de drenaje pluvial del CAR Varones')
DJ = json.load(open(os.path.join(SAL, '_calc/diseno.json')))
D = DJ['datos']
I10 = 210.98                                     # memoria hidrológica de la usuaria: TR 25 años, duración 10 min (Dick-Peschke)


def generar():
    wb = R.libro(); proyecto, Rz = R.resumen(wb); res = {it: (de, un, to) for it, de, un, to in Rz}
    cun = R.cunetas(wb); tramos_ll, tot_ll = R.lloraderos(wb)
    planos = json.load(open(R.INDICE, encoding='utf-8'))
    g = DJ['geom']; perfil = DJ['perfil']
    llen = max(p['y'] / p['h'] for p in perfil); bl = min(p['techo'] - p['NA'] for p in perfil)
    M = R.Memoria()
    R.caratula(M, proyecto)
    R.encabezado(M)
    R.indice(M)

    def q(it):
        de, un, to = res[it]
        return ('%s %s' % (f2(to), un)) if un in ('m', 'm²', 'm³', 'kg') else '%d %s' % (round(to), un)

    # ---------------------------------------------------------------- 1
    M.t1('INFORMACIÓN DEL PROYECTO')
    M.tabla('Datos generales del proyecto', ['DATO', 'DESCRIPCIÓN'], [
        ['Unidad ejecutora', 'Gerencia Territorial Bajo Mayo - Dirección de Infraestructura'],
        ['Proyecto', '“' + proyecto + '”'],
        ['Código único de inversiones', 'CUI N.° ' + CUI],
        ['Ubicación', 'Distrito de Morales, provincia y departamento de San Martín'],
        ['Especialidad', 'Instalaciones sanitarias - drenaje pluvial'],
        ['Componentes de la especialidad', 'Red de drenaje pluvial del predio (partida 01.04.03) y colector pluvial frontal (partida 01.04.04)']],
        [4.5, M.ancho - 4.5], izq=(0, 1))

    # ---------------------------------------------------------------- 2
    M.t1('ANTECEDENTES DEL PROYECTO')
    M.t2('Introducción')
    M.par('La presente memoria describe el sistema de drenaje pluvial del Centro de Acogida Residencial (CAR) Varones (CUI %s), que '
          'capta las aguas de lluvia de los techos de las edificaciones y de las superficies exteriores del predio, las conduce por '
          'canaletas, montantes, red de piso y cunetas de concreto armado, y las entrega a un colector pluvial frontal cubierto. El '
          'colector forma parte de un colector continuo compartido con los dos proyectos vecinos: el CAR Varones es el tramo inicial y '
          'entrega su caudal a la caja de llegada CL del colector del Hogar de Refugio Temporal (CUI 2675514), que a su vez entrega al '
          'registro R-01 del CAR Mujeres (CUI 2717013).' % CUI)
    M.par('El dimensionamiento hidráulico se sustenta en el Estudio Hidrológico y de Drenaje Pluvial del proyecto, con el capítulo del '
          'colector frontal, y en la memoria de cálculo del colector. Las cantidades citadas son las del metrado de la especialidad y '
          'los planos son los del juego de láminas DPLV de drenaje pluvial (relación al final de esta memoria).')
    M.t2('Normas aplicables')
    for t in ('Reglamento Nacional de Edificaciones, Norma CE.040 Drenaje Pluvial (R.M. N.° 126-2021-VIVIENDA).',
              'Reglamento Nacional de Edificaciones, Norma IS.010 Instalaciones Sanitarias para Edificaciones.',
              'Reglamento Nacional de Edificaciones, Normas E.020 Cargas, E.050 Suelos y Cimentaciones y E.060 Concreto Armado.',
              'Manual de Hidrología, Hidráulica y Drenaje del Ministerio de Transportes y Comunicaciones.',
              'AASHTO LRFD Bridge Design Specifications y Manual de Puentes del MTC (carga de rueda en el portón de camiones).',
              'Norma G.050 Seguridad durante la Construcción y D.S. N.° 011-2019-TR.'):
        M.vin(t)

    # ---------------------------------------------------------------- 3
    M.t1('UBICACIÓN DEL PROYECTO')
    M.par('El proyecto se ubica en el distrito de Morales, provincia y departamento de San Martín, junto al Hogar de Refugio Temporal '
          '(CUI 2675514) y al CAR Mujeres (CUI 2717013), con los que comparte el colector pluvial frontal. El colector del CAR Varones '
          'corre a lo largo del frente del predio y termina en la caja de llegada CL del Hogar de Refugio.')
    M.tabla('Ubicación política', ['NIVEL', 'NOMBRE'], [['Departamento', 'San Martín'], ['Provincia', 'San Martín'], ['Distrito', 'Morales']],
            [5.0, M.ancho - 5.0], izq=(0, 1))

    # ---------------------------------------------------------------- 4
    M.t1('FINALIDAD Y OBJETIVOS')
    M.t2('Finalidad')
    M.par('Evacuar de forma ordenada y segura las aguas pluviales del CAR Varones, evitando empozamientos, humedad en las '
          'edificaciones, erosión y deterioro de pisos y veredas, y entregarlas al colector compartido en condiciones compatibles con '
          'el tramo receptor del Hogar de Refugio.')
    M.t2('Objetivos')
    for t in ('Captar el agua de los techos de las edificaciones 01 a 10, la guardianía, las entradas y la losa deportiva mediante canaletas de plancha galvanizada.',
              'Conducir el agua de techo por montantes de PVC de Ø 4" protegidas en su tramo inferior por falsas columnas de concreto armado.',
              'Recoger el agua de pisos, veredas, patios y áreas verdes con sumideros, red de piso y cunetas de concreto armado con rejilla.',
              'Aliviar el agua del suelo de las áreas verdes que colindan con las cunetas mediante lloraderos de PVC.',
              'Conducir el caudal del predio por el colector pluvial frontal cubierto hasta la caja de llegada CL del Hogar de Refugio.'):
        M.vin(t)

    # ---------------------------------------------------------------- 5
    M.t1('PARÁMETROS Y CRITERIOS DE DISEÑO')
    M.par('Los caudales se calculan con el método racional, Q = C · I · A · FS, con la intensidad del estudio hidrológico (análisis de '
          'frecuencia de la precipitación máxima en 24 horas de la estación CO Tarapoto, período de retorno de %d años, duración de '
          '10 minutos). El sistema se divide en 14 sectores de drenaje: losa deportiva, edificaciones 01 a 10, guardianía, entrada 01 '
          'y entrada 02, cada uno con la secuencia techo, canaleta, montante, cuneta de piso y punto de entrega.' % D['TR'])
    M.tabla('Parámetros de diseño del sistema de drenaje pluvial', ['PARÁMETRO', 'VALOR', 'APLICACIÓN'], [
        ['Período de retorno', '%d años' % D['TR'], 'Todo el sistema'],
        ['Intensidad de diseño (tc = 10 min, Dick-Peschke)', '%.2f mm/h' % I10, 'Canaletas, montantes, cunetas y colector'],
        ['Factor de seguridad FS', '%.2f' % D['FS'], 'Todos los caudales'],
        ['Coeficiente de escorrentía', '0.88 techos y veredas; 0.86 estacionamiento; 0.40 patios; 0.29 áreas verdes', 'Método racional'],
        ['Rugosidad de Manning n', '0.013 canaletas; 0.015 cunetas y colector', 'Ecuación de Manning'],
        ['Pendiente longitudinal', '1.0 % canaletas; 0.5 % cunetas; 0.3 % colector', 'Perfiles'],
        ['Diámetro de montantes', 'Ø 4" (Wyly-Eaton, rs = 0.25)', 'Montantes y bajadas'],
        ['Llenado máximo / borde libre mínimo', '85 % / 0.05 m', 'Colector']],
        [5.4, 5.0, M.ancho - 10.4], izq=(0, 1, 2), fuente_txt='Fuente: Estudio hidrológico y de drenaje pluvial del proyecto.')
    M.tabla('Área de drenaje del predio y caudal entregado', ['CONCEPTO', 'VALOR'], [
        ['Área total de drenaje del predio', '%s m²' % f2(D['A_total'])],
        ['Coeficiente de escorrentía ponderado', '%.3f' % D['C_pond']],
        ['Caudal del colector en su tramo final', '%.1f L/s' % DJ['Q']],
        ['Caudal de la cuneta del Eje 01 que entra directamente a la caja CL', '%.1f L/s' % DJ['Q_directo_CL']],
        ['Caudal total entregado a la caja CL del Hogar de Refugio', '%.1f L/s' % DJ['Q_CL']]],
        [M.ancho - 4.0, 4.0], izq=(0,), fuente_txt='Fuente: Estudio hidrológico y de drenaje pluvial (capítulo del colector).')

    # ---------------------------------------------------------------- 6
    M.t1('DESCRIPCIÓN DEL SISTEMA DE DRENAJE PLUVIAL')
    M.t2('Esquema general')
    M.par('El agua de los techos cae a canaletas de plancha galvanizada y baja por montantes de PVC de Ø 4" hasta las cunetas o la red de '
          'piso; el agua de pisos y áreas exteriores entra a las cunetas por sus rejillas y por sumideros conectados a la red de piso. Las '
          'cunetas de concreto armado, con pendiente de 0.5 %, recorren el predio por los ejes 01 a 09 y llegan al frente, donde descargan '
          'al colector pluvial frontal (ejes 09, 08, 06 y 04) o a la caja CL (eje 01). La red general está en la lámina DPLV-01, los '
          'perfiles de cunetas en DPLV-05 y DPLV-06 y sus secciones en DPLV-02 a DPLV-04.')
    M.figura('DPLV-01', 'Red general de drenaje pluvial del CAR Varones')
    M.t2('Canaletas de techo')
    M.par('Los techos de las edificaciones (cobertura de planchas TR4 de aluzinc) descargan en canaletas de plancha de acero galvanizado, '
          'con soportes de platina de F°G° de 1" x 1/8", tapas laterales en los extremos y boquillas de conexión a las montantes (láminas '
          'DPLV-36, DPLV-37 y DPLV-41). Metrado: %s de canaleta (%s), %s de soportes, %s de tapas laterales y %s de boquillas.'
          % (q('01.04.03.05.01.03'), res['01.04.03.05.01.03'][0].split(',', 1)[-1].strip().lower(), q('01.04.03.05.01.04'),
             q('01.04.03.05.01.05'), q('01.04.03.05.01.06')))
    M.t2('Montantes pluviales y falsas columnas')
    M.par('Las montantes son de tubería PVC de Ø 4" (%s), fijadas con abrazaderas de F°G° (%s) y colgadores en los desvíos bajo el alero '
          '(%s); su tramo inferior se aloja en una falsa columna de concreto armado de 0.20 x 0.15 x 1.30 m (%s). Los detalles por '
          'edificación están en las láminas DPLV-07 a DPLV-16, el montante típico en DPLV-38 y DPLV-42 y la falsa columna en DPLV-44.'
          % (q('01.04.03.05.01.01'), q('01.04.03.05.03.05'), q('01.04.03.05.03.04'), q('01.04.03.05.01.02')))
    M.t2('Sumideros y red de piso')
    M.par('Las superficies interiores que no llegan directamente a una cuneta drenan a sumideros metálicos con platina de 1" x 3/16" '
          '(%s), en caja sumidero de piso (láminas DPLV-39 y DPLV-40), conectados por tubería PVC-CP de Ø 4" (%s) con sus codos y tees '
          'hasta la cuneta más próxima.' % (q('01.04.03.05.02.02'), q('01.04.03.05.02.01')))
    M.t2('Cunetas de concreto armado')
    M.par('Las cunetas son de concreto armado f\'c = 175 kg/cm², de sección interior 0.40 m de ancho y altura variable según su perfil '
          '(muros y losa de 0.10 m, ancho exterior 0.60 m), con pendiente de 0.5 %%, rejilla metálica móvil en los tramos abiertos '
          '(%s; lámina DPLV-33), tapas de inspección de 0.60 x 0.60 m (%s) y juntas de dilatación de 1" con sellador asfáltico en toda '
          'la sección (%s; láminas DPLV-31 y DPLV-32). En los cruces y pasos de circulación la cuneta se cubre con losa de concreto armado.'
          % (q('01.04.03.04.03.01'), q('01.04.03.04.03.02'), q('01.04.03.04.03.03')))
    filas = [[c['eje'].title(), f2(c['L']), f2(c['tapa']) if c['tapa'] else '-', f2(c['conc'])] for c in cun]
    filas.append(['TOTAL', f2(sum(c['L'] for c in cun)), f2(sum(c['tapa'] for c in cun)), f2(sum(c['conc'] for c in cun))])
    M.tabla('Cunetas de concreto armado por eje', ['EJE', 'LONGITUD (m)', 'TRAMO CUBIERTO (m)', 'CONCRETO (m³)'], filas, [3.5, 3.5, 4.0, 3.5],
            izq=(), total=True, fuente_txt='Fuente: Metrado de la especialidad, hoja CONCRETO EN CUNETAS.')
    M.t2('Lloraderos en cunetas colindantes con área verde')
    M.par('En los tramos en que el muro de la cuneta colinda con un área verde se colocan lloraderos de tubería PVC de Ø 3" cada 1.50 m, '
          'con filtro de grava de 20 a 40 mm envuelto en geotextil no tejido, para aliviar el empuje del agua infiltrada en el jardín sin '
          'arrastrar finos: %d lloraderos en %.2f m de muro (lámina DPLV-43 de ubicación, DPLV-35 de detalle y DPLV-34 de instalación). '
          'Los materiales (tubo, grava, geotextil y mortero) están desagregados en la hoja DESAGREGADO LLORADEROS del metrado.'
          % (tot_ll[2], tot_ll[1]))
    M.tabla('Tramos de cuneta con lloraderos', ['EJE', 'PROGRESIVAS', 'LADO', 'LONGITUD (m)', 'N.°'],
            [[r[1], r[2], r[3], f2(r[4]), '%d' % r[6]] for r in tramos_ll] + [['TOTAL', '', '', f2(tot_ll[1]), '%d' % tot_ll[2]]],
            [2.4, 4.4, 3.2, 2.8, 1.8], izq=(), total=True, fuente_txt='Fuente: Metrado de la especialidad, hoja METRADO LLORADEROS.')
    M.figura('DPLV-43', 'Planta de ubicación de lloraderos en cunetas colindantes con área verde')

    # ---------------------------------------------------------------- 7
    M.t1('COLECTOR PLUVIAL FRONTAL')
    M.t2('Descripción general')
    M.par('El colector es un canal rectangular cubierto de concreto armado f\'c = 210 kg/cm² que corre a lo largo del frente del predio, '
          'con la losa superior a nivel de vereda (NPT +%.2f). Mide %.2f m (0+000.00 a 0+%06.2f): un tramo recto hasta el quiebre '
          '(0+%06.2f) y un tramo de empalme horizontal hasta la cara este de la caja de llegada CL del Hogar de Refugio (CUI 2675514), '
          'a la que entrega por caída libre. Planta en la lámina DPLV-17 y perfiles en DPLV-18 a DPLV-20.'
          % (D['NPT'], g['P_FIN'], g['P_FIN'], g['P_QUIEBRE']))
    for t in ('Sección: ancho interior b = %.2f m, muros de %.2f m, losa de fondo de %.2f m, losa superior de %.2f m (%.2f m en el portón de camiones).' % (D['b'], D['e_muro'], D['e_fondo'], D['e_losa'], D['e_losa_camion']),
              'Pendiente S = %.1f ‰; cota de fondo %.2f msnm en el inicio.' % (D['S'] * 1000, D['CF0']),
              'Altura interior variable de %.2f a %.2f m (losa superior a nivel fijo).' % (min(p['h'] for p in perfil), max(p['h'] for p in perfil)),
              'Cruce: portón de camiones cisterna de %.2f m (0+000.00 a 0+006.08), con doble marco de acero y losa superior de %.2f m.' % (D['porton_camiones'], D['e_losa_camion'])):
        M.vin(t)
    M.figura('DPLV-17', 'Planta del colector pluvial frontal')
    M.t2('Secciones del colector')
    M.tabla('Secciones del colector pluvial frontal', ['TRAMO', 'MUROS / FONDO (m)', 'LOSA SUPERIOR (m)', 'ARMADURA'], [
        ['Tramo normal (vereda)', '%.2f / %.2f' % (D['e_muro'], D['e_fondo']), f2(D['e_losa']), 'Marco cerrado de 3/8" @0.20 m; longitudinales 3/8" @0.25 m'],
        ['Portón de camiones (0+000.00 a 0+006.08)', '%.2f / %.2f' % (D['e_muro'], D['e_fondo']), f2(D['e_losa_camion']), 'Doble marco de 1/2" @0.15 m; longitudinales 3/8" @0.20 m']],
        [4.6, 2.8, 2.5, M.ancho - 9.9], izq=(0, 3), fuente_txt='Fuente: Láminas DPLV-21 y DPLV-22 y memoria de cálculo del colector.')
    M.figura('DPLV-21', 'Secciones transversales del colector')
    M.t2('Registros de limpieza')
    M.par('Los registros se ubican a no más de 12 m entre sí, en cada llegada de cuneta y en el quiebre, fuera del portón de camiones, con '
          'tapa ciega de concreto armado de 0.68 x 0.68 x 0.08 m en rebaje de la losa (láminas DPLV-23 y DPLV-26 a DPLV-28): %s en total '
          '(partida 01.04.04.05.01).' % q('01.04.04.05.01'))
    M.tabla('Registros y puntos singulares del colector', ['ELEMENTO', 'PROGRESIVA', 'FUNCIÓN'],
            [[r['nombre'], '0+%06.2f' % r['prog'], (r['tipo'] + ': ' + r['nota']).replace('tambien', 'también')] for r in DJ['registros']],
            [2.4, 2.6, M.ancho - 5.0], izq=(2,), fuente_txt='Fuente: Lámina DPLV-17 y memoria de cálculo del colector.')
    M.figura('DPLV-23', 'Detalle de registro de limpieza con tapa ciega de concreto armado')
    M.t2('Empalmes de cunetas al colector')
    M.par('Las cunetas de los ejes 09, 08, 06 y 04 llegan al colector por una ventana de 0.40 x H en el muro del lado del predio, con '
          'caída libre al fondo, junta de 1" y registro sobre el empalme; la del eje 01 entra directamente a la caja CL por su muro norte '
          '(láminas DPLV-24 y DPLV-30). En todos los casos la cota de fondo de la cuneta queda sobre el nivel de agua del colector.')
    M.tabla('Empalmes de cunetas al colector', ['CUNETA', 'ENTRA EN', 'PROG.', 'COTA DE FONDO (msnm)', 'H VENTANA (m)', 'CAÍDA LIBRE (m)'],
            [[c['nombre'], 'Caja CL' if c['entra_en'] == 'CL' else 'Colector', '0+%06.2f' % c['prog'], f2(c['NCF_fin']), f2(c['H_ventana']),
              f2(c['caida_libre'])] for c in DJ['cunetas']], [2.3, 2.0, 2.4, 3.0, 2.5, 2.5], izq=(0,),
            fuente_txt='Fuente: Memoria de cálculo del colector y hoja CUNETAS - LLEGADA AL COLECTOR del metrado.')
    M.t2('Empalme con la caja de llegada CL')
    M.par('El colector termina en la cara este de la caja de llegada CL del Hogar de Refugio, a la que entra por una ventana de 0.60 x %.2f m '
          'con caída libre de %.2f m sobre su nivel de agua; la tapa de la CL queda en +%.2f, al nivel del piso del CAR Varones. La junta '
          'entre el colector y la caja es de tecnopor de 1" con sellador asfáltico (lámina DPLV-25 y DPLV-29).'
          % (DJ['caja_llegada'].get('ventana_alto', 1.17), DJ['caja_llegada'].get('caida_libre', 0), D['NPT_CL']))
    M.figura('DPLV-25', 'Empalme del colector con la caja de llegada CL del Hogar de Refugio')
    M.t2('Juntas')
    M.par('Juntas de dilatación cada 4.00 m en toda la sección con tecnopor de 1" y sellador asfáltico de 1" x 2" (%s) y junta de 1" con el '
          'mismo sellador entre el colector y la caja CL (%s); a ambos lados del colector hay terreno natural, sin junta longitudinal (lámina DPLV-29).'
          % (q('01.04.04.06.01'), q('01.04.04.06.02')))
    M.t2('Funcionamiento hidráulico')
    M.par('Con el caudal de diseño de %.1f L/s el tirante normal es %.3f m, la velocidad %.2f m/s y el número de Froude %.2f: régimen '
          'subcrítico en todo el tramo. El llenado máximo es %.0f %% y el borde libre mínimo %.2f m; la velocidad cumple los criterios de '
          'la norma CE.040 y el colector se autolimpia aun con caudales parciales.' % (DJ['Q'], DJ['yn'], DJ['V_n'], DJ['F_n'], llen * 100, bl))
    M.t2('Verificación estructural')
    M.par('El colector se verifica como marco cerrado de concreto armado con el empuje del relleno, las sobrecargas peatonales (Norma E.020) '
          'y, en el portón, la carga de rueda del camión cisterna con impacto (AASHTO LRFD); el diseño por resistencia sigue la Norma E.060. '
          'Todas las verificaciones de flexión y cortante cumplen (memoria de cálculo del colector).')

    # ---------------------------------------------------------------- 8
    M.t1('ENTREGA AL PROYECTO COLINDANTE')
    M.tabla('Caudales del CAR Varones entregados al colector compartido', ['APORTE', 'Q (L/s)'], [
        ['Colector pluvial frontal (tramo final, ejes 09, 08, 06 y 04)', '%.1f' % DJ['Q']],
        ['Cuneta del Eje 01, directa a la caja CL', '%.1f' % DJ['Q_directo_CL']],
        ['Caudal total entregado a la caja CL del Hogar de Refugio (CUI 2675514)', '%.1f' % DJ['Q_CL']]],
        [M.ancho - 3.0, 3.0], izq=(0,), total=True, fuente_txt='Fuente: Memoria hidrológica (capítulo del colector).')
    M.par('El caudal total coincide con el aporte previsto por el Hogar de Refugio en su caja CL; la tapa de la caja, las ventanas y las '
          'cotas de fondo de llegada están coordinadas en ambos expedientes.')

    # ---------------------------------------------------------------- 9
    M.t1('METAS FÍSICAS')
    for raiz, titulo in (('01.04.03.', 'Metas físicas del sistema de drenaje pluvial del predio (partida 01.04.03)'),
                         ('01.04.04.', 'Metas físicas del colector pluvial frontal (partida 01.04.04)')):
        filas = [[it, de, un or '', (f2(to) if un in ('m', 'm²', 'm³', 'kg') else '%d' % round(to)) if un else '']
                 for it, de, un, to in Rz if it.startswith(raiz)]
        M.tabla(titulo, ['ÍTEM', 'DESCRIPCIÓN', 'UND', 'METRADO'], filas, [3.6, M.ancho - 7.2, 1.4, 2.2], tam=8.5, izq=(0, 1),
                fuente_txt='Fuente: Metrado de la especialidad (hoja RESUMEN).')

    # ---------------------------------------------------------------- 10-12
    M.t1('OPERACIÓN Y MANTENIMIENTO')
    for t in ('Antes de la temporada de lluvias (setiembre a abril) y después de cada lluvia intensa, limpiar canaletas, boquillas y rejillas de hojas y basura.',
              'Revisar el estado de soportes, abrazaderas y colgadores; reponer los sueltos o corroídos y repintar con pintura rica en zinc.',
              'Retirar sedimentos de cunetas, cajas sumidero y del fondo del colector a través de los registros, al menos dos veces al año.',
              'Verificar que los lloraderos no estén obstruidos y que el área verde no se riegue en exceso contra los muros de las cunetas.',
              'Revisar y reponer el sellador de las juntas cuando presente fisuras o desprendimientos.',
              'Mantener las tapas de los registros en su sitio y no colocar cargas vehiculares fuera del portón de camiones.'):
        M.vin(t)
    M.t1('CONCLUSIONES')
    for t in ('El sistema de drenaje pluvial capta y conduce el agua de techos y superficies exteriores de los 14 sectores del predio con canaletas, montantes de Ø 4", red de piso y cunetas de concreto armado de 0.40 m de ancho interior.',
              'El colector pluvial frontal de %.2f m de ancho conduce %.1f L/s en régimen subcrítico, con llenado máximo de %.0f %% y borde libre mínimo de %.2f m, y con la cuneta del Eje 01 entrega %.1f L/s a la caja CL del Hogar de Refugio.' % (D['b'], DJ['Q'], llen * 100, bl, DJ['Q_CL']),
              'Las cunetas colindantes con área verde llevan %d lloraderos de PVC de Ø 3" con filtro de grava y geotextil.' % tot_ll[2],
              'Las cantidades de esta memoria son las del metrado de la especialidad y los planos son los del juego de láminas DPLV de drenaje pluvial.'):
        M.vin(t)
    M.t1('RECOMENDACIONES')
    for t in ('Verificar en el replanteo la ubicación del colector y las cotas de fondo de llegada a la caja CL del Hogar de Refugio.',
              'Coordinar la ejecución con el Hogar de Refugio: si la caja CL se construye antes, sus ventanas se dejan tapadas con muro de ladrillo sin mortero de unión, para retirarlo al empalmar.',
              'Comparar la presión transmitida al suelo con la capacidad portante del estudio de mecánica de suelos del proyecto.',
              'Ejecutar las pruebas con agua de canaletas, montantes y red de piso antes de cerrar falsas columnas y rellenos.'):
        M.vin(t)

    # ---------------------------------------------------------------- 13
    M.t1('RELACIÓN DE PLANOS')
    M.tabla('Relación de planos de drenaje pluvial', ['N.°', 'LÁMINA', 'DESCRIPCIÓN', 'FORMATO'],
            [['%02d' % i, p['codigo'], p['titulo'], p['formato']] for i, p in enumerate(planos, 1)], [1.0, 1.8, M.ancho - 4.6, 1.8],
            tam=8.5, izq=(2,), fuente_txt='Fuente: Índice de planos de drenaje pluvial (orden del juego de láminas, por formato de hoja).')
    M.d.core_properties.author = ''
    M.d.core_properties.title = 'Memoria descriptiva - Drenaje pluvial - CAR Varones'
    M.d.save(R.SALIDA)
    return R.SALIDA


if __name__ == '__main__':
    print(generar())
