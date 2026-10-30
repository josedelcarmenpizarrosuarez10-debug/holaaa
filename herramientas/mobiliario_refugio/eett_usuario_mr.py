# -*- coding: utf-8 -*-
"""Especificaciones técnicas de equipamiento y mobiliario del Word del usuario, ajustadas al metrado - Hogar de Refugio Temporal
"Mujeres Violentadas" (CUI 2675514).

Parte del Word del usuario (insumos/solange/mobiliario/eett/, copia; el original no se toca) y:
  - deja solo las partidas del metrado de equipamiento y mobiliario (datos_mr.numerar: numeración, nombre y orden del metrado);
  - conserva tal cual el texto, las tablas y las imágenes de cada partida del Word que corresponde a una partida del metrado;
  - borra las partidas del Word que no están en el metrado (y las que tienen otra medida o tipo, p. ej. pelotas de otro número);
  - completa, con el formato del Word (DESCRIPCIÓN, CARACTERÍSTICAS, MEDICIÓN, FORMA DE PAGO), las partidas del metrado que en el
    Word no tienen texto o no están; las que se repiten en otro ambiente remiten a la primera ("Ídem");
  - pone el proyecto y el CUI del hogar en los datos iniciales y el encabezado del hogar en todas las páginas (el Word traía el
    del CAR Mujeres y encabezados de la I.E. Ofelia Velásquez).

Uso: python3 herramientas/mobiliario_refugio/eett_usuario_mr.py
Salida: entregables/EETT-EQUIP_Y_MOBILIARIO-HOGAR_DE_REFUGIO_TEMPORAL_MUJERES_VIOLENTADAS.docx
"""
import copy
import os
import re
import sys

import docx
from docx.oxml.ns import qn

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI); RAIZ = os.path.dirname(HER)
for d in (AQUI, HER):
    sys.path.insert(0, d)
import datos_mr as D  # noqa: E402
import espec_mr as E  # noqa: E402

NOMBRE = 'EETT-EQUIP_Y_MOBILIARIO-HOGAR_DE_REFUGIO_TEMPORAL_MUJERES_VIOLENTADAS.docx'
ENTRADA = os.path.join(RAIZ, 'insumos', 'solange', 'mobiliario', 'eett', NOMBRE)
SALIDA = os.path.join(D.SAL, NOMBRE)

# partida del Word del usuario -> partida del metrado (clave de datos_mr); las que no figuran se borran
WORD_A_METRADO = {
    '02.01.01': 'E1', '02.01.02': 'E2', '02.01.03': 'E3', '02.01.04': 'E10', '02.01.05': 'E5', '02.01.06': 'E6', '02.01.07': 'E7',
    '02.01.08': 'E9', '02.01.09': 'E13', '02.01.10': 'E16', '02.01.11': 'E17', '02.01.12': 'E18', '02.01.13': 'E19',
    '02.02.01': 'M4', '02.02.02': 'M7', '02.02.03': 'M8', '02.02.04': 'M13', '02.02.05': 'M15', '02.02.06': 'M16',
    '02.02.08': 'M20', '02.02.09': 'M21', '02.02.10': 'M26', '02.02.11': 'M27', '02.02.12': 'M28', '02.02.13': 'M31',
    '02.02.14': 'M34', '02.02.15': 'M35', '02.02.16': 'M36', '02.02.17': 'M37', '02.02.18': 'M39', '02.02.19': 'M51',
    '02.02.20': 'M52', '02.02.21': 'M54', '02.02.22': 'M56', '02.02.23': 'M57', '02.02.24': 'M63', '02.02.26': 'M61',
    '02.02.27': 'M62', '02.02.28': 'M65', '02.02.29': 'M64', '02.02.30': 'M69', '02.02.31': 'M70', '02.02.32': 'M73',
    '02.02.33': 'M75', '02.02.34': 'M76', '02.02.35': 'M77', '02.02.36': 'M78', '02.02.37': 'M79',
    '02.03.01.01': 'K:E-02:K32', '02.03.01.02': 'K:E-02:K33', '02.03.01.03': 'K:E-02:K34', '02.03.01.04': 'K:E-02:K35',
    '02.03.02.01': 'K:K78', '02.03.02.04': 'K:E-05:K32', '02.03.02.05': 'K:K31', '02.03.02.06': 'K:E-05:K33',
    '02.03.02.07': 'K:K20', '02.03.03.02': 'K:K38', '02.03.03.07.01': 'K:K43', '02.03.03.07.07': 'K:K44',
    '02.03.03.07.08': 'K:K53', '02.03.03.07.10': 'K:K52', '02.03.03.06.02': 'K:K73',
}
# borradas por no estar en el metrado o por ser otro tipo o medida (el metrado manda):
#   02.02.07 caballete, 02.02.25 papelera vaivén (metrado: papelera con pedal), 02.03.02.02/03 juegos de cocina y lavandería,
#   02.03.03.03 básquet N.° 5 (metrado N.° 6), 02.03.03.04 torre de básquet, 02.03.03.05.01/02 futsal (metrado: fútbol N.° 5),
#   conos, vóley N.° 5 (metrado N.° 4), barra de equilibrio de 5 m (metrado: riel de equilibrio), ula ula (metrado: aros de
#   aluminio), pelota de rebote, cinta métrica, balanza, flexaband, cronómetro, ajedrez, linterna, megáfono y chaleco.

FORMA_PAGO = {
    'E': 'El pago se efectuará por unidad colocado en la edificación, previa inspección, revisión de componentes y aprobación del '
         'Supervisor.',
    'M': 'El mobiliario será recepcionado, conservando sus características intactas antes del uso, previa inspección y aprobación del '
         'Residente y el Supervisor.',
    'K': 'Los implementos serán recepcionados, conservando sus características intactas antes del uso, previa inspección y '
         'aprobación del Residente y el Supervisor.',
}

# características de las partidas del metrado que el Word no tiene (o tiene sin texto)
CARACT = {
    'E4': ['Reloj analógico para adosar a la pared, de 30 cm de diámetro, caja de plástico ABS y luna de vidrio o acrílico.',
           'Mecanismo de cuarzo silencioso (sin tic-tac), a pilas AA; números grandes legibles a distancia.',
           'Se fija a la pared con tarugo y tornillo, a 2.10 m de altura aproximadamente.'],
    'E5': ['Lavadora automática de carga superior, capacidad de 20 kg de ropa seca, tina de acero inoxidable.',
           'Panel digital con programas de lavado, nivel de agua regulable y centrifugado; 220 V - 60 Hz.',
           'Garantía no menor de un año y servicio técnico en la región; incluye mangueras de ingreso y desagüe.'],
    'E10': ['Máquina de corte textil eléctrica (cortadora vertical de tela), 220 V - 60 Hz, con cuchilla de acero y guarda de '
            'protección de la mano.',
            'Afilador incorporado y base para trabajar sobre la mesa de corte textil del taller de costura.',
            'Garantía no menor de un año y servicio técnico en la región.'],
    'E13': ['Cocina industrial de 2 hornillas, estructura de fierro angular con pintura al horno, parrillas de fierro fundido.',
            'Quemadores de alta presión para gas licuado de petróleo, con válvula de control por hornilla, manguera y regulador.',
            'Instalación con la manguera y el regulador normalizados y prueba de hermeticidad de las conexiones.'],
    'E17': ['Licuadora de 1.5 litros con vaso de vidrio templado graduado y tapa con dosificador.',
            'Cuchillas de acero inoxidable, motor no menor de 600 W, de 3 velocidades y función pulso; 220 V - 60 Hz.',
            'Base antideslizante; garantía no menor de un año.'],
    'E19': ['Refrigeradora de 315 litros, sistema no frost, con congelador y compartimiento de refrigeración.',
            'Bandejas de vidrio templado, cajón de verduras, control de temperatura; 220 V - 60 Hz, eficiencia energética A.',
            'Garantía no menor de un año y servicio técnico en la región.'],
    'M3': ['Silla regulable de estudiante de 0.30 x 0.27 x 0.32 m (asiento), estructura de tubo de acero LAC con pintura en polvo '
           'electrostática horneada.',
           'Asiento y respaldo de madera tipo B de 18 mm, lijados, con cantos redondeados, sellador y barniz poliuretano.',
           'Regulación de altura con pernos y perillas; regatones de polipropileno en las patas.'],
    'M4': ['Mesa regulable de 0.56 x 0.50 x 0.60 m, estructura de tubo de acero LAC con pintura en polvo electrostática horneada.',
           'Tablero de madera tipo B o contraplacado de 18 mm, con cantos redondeados, sellador y barniz poliuretano.',
           'Regulación de altura con pernos y perillas; regatones de polipropileno en las patas.'],
    'M8': ['Mesa de 1.00 x 0.50 x 0.75 m, estructura de tubo de acero LAC de 1" x 1/16" soldada, con pintura en polvo electrostática '
           'horneada.',
           'Tablero de madera tipo B de 25 mm con faldón de refuerzo, cantos redondeados, sellador y barniz poliuretano.',
           'Regatones de polipropileno en las patas.'],
    'M9': ['Maniquí de costura de busto ajustable (talla regulable con perillas), de fibra o espuma forrada en tela.',
           'Pedestal metálico regulable en altura, con base estable de tres o cuatro apoyos.'],
    'M15': ['Atril de mesa de madera para dibujo y pintura, con tablero de inclinación regulable y reborde inferior para apoyar la '
            'lámina o el lienzo.',
            'Madera lijada con cantos redondeados, sellador y barniz.'],
    'M16': ['Mesa de 0.90 x 1.80 m, estructura de tubo de acero LAC de 1" x 1/16" soldada, con pintura en polvo electrostática '
            'horneada.',
            'Tablero de madera tipo B de 25 mm con faldón de refuerzo, cantos redondeados, sellador y barniz poliuretano.',
            'Regatones de polipropileno en las patas.'],
    'M16-T': ['Mesa de corte textil de 0.80 x 1.50 x 0.75 m con tablero de melamina de 25 mm y cantos de PVC.',
              'Estructura metálica de tubo de acero con pintura en polvo electrostática horneada, nivelada y firme.'],
    'M19': ['Mesa de 1.00 x 1.80 x 0.75 m, estructura de tubo de acero LAC de 1" x 1/16" soldada, con pintura en polvo '
            'electrostática horneada.',
            'Tablero de madera tipo B de 25 mm con faldón de refuerzo, cantos redondeados, sellador y barniz poliuretano.'],
    'M22': ['Mesa de 1.00 x 1.80 x 0.75 m, estructura de tubo de acero LAC de 1" x 1/16" soldada, con pintura en polvo '
            'electrostática horneada.',
            'Tablero de madera tipo B de 25 mm con faldón de refuerzo, cantos redondeados, sellador y barniz poliuretano.'],
    'M23': ['Mesa de 1.00 x 2.00 x 0.75 m, estructura de tubo de acero LAC de 1" x 1/16" soldada, con pintura en polvo '
            'electrostática horneada.',
            'Tablero de madera tipo B de 25 mm con faldón de refuerzo, cantos redondeados, sellador y barniz poliuretano.'],
    'M26': ['Mesa de 0.90 x 0.60 x 0.90 m de acero inoxidable AISI 304, tablero de 1.2 mm con refuerzo inferior.',
            'Patas de tubo de acero inoxidable con niveladores regulables y entrepaño inferior.',
            'Soldaduras pulidas, sin aristas cortantes.'],
    'M32': ['Sillón para acoplar de 0.44 x 0.55 x 0.60 m, estructura de madera maciza tipo B.',
            'Asiento y respaldo de espuma de alta densidad, tapizado en tela o cuerina lavable de alto tránsito.',
            'Patas con regatones; se acopla a otros sillones o sofás de la sala.'],
    'M60': ['Papelera de plástico con pedal, de polipropileno de alta resistencia, con tapa y balde interior removible.',
            'Pedal de accionamiento y bisagra reforzados; superficie lavable.'],
    'M61': ['Velador de madera tornillo de 0.45 x 0.50 m, con cajón con corredera y manija.',
            'Cantos redondeados, acabado con sellador y barniz poliuretano.'],
    'M62': ['Cesto bota papeles de acero inoxidable con pedal, tapa y balde interior removible.',
            'Base con protector de goma para no dañar el piso.'],
    'M63': ['Sofá de 3 cuerpos de 0.55 x 1.50 x 0.44 m, estructura de madera maciza tipo B.',
            'Asiento y respaldo de espuma de alta densidad, tapizado en tela o cuerina lavable de alto tránsito.',
            'Patas con regatones.'],
    'M64': ['Camarote de una plaza y media (dos camas superpuestas) de madera tornillo cepillada o estructura metálica con pintura '
            'electrostática.',
            'Baranda de protección en la cama superior, escalera fija y tarima de listones.',
            'Colchón de espuma de alta densidad con forro lavable para cada plaza, incluido en la partida; el camarote se fija a la pared.'],
    'M64-C': ['Canastilla móvil para pelotas de 1.00 x 0.80 x 1.00 m, estructura de tubo y malla de acero con pintura electrostática.',
              'Cuatro ruedas giratorias, dos con freno.'],
    'M67': ['Escalera metálica de dos peldaños de 0.40 x 0.40 x 0.36 m, de tubo de acero con pintura electrostática o cromado.',
            'Peldaños con jebe antideslizante y regatones en las patas.'],
    'M68': ['Parihuela de madera tornillo de 0.90 x 0.50 x 0.20 m, de listones cepillados, para el almacenaje sobre el piso.',
            'Madera tratada contra la humedad y los insectos.'],
    'M71': ['Coche multiusos móvil de 0.80 x 0.40 x 0.90 m, de acero inoxidable AISI 304, con dos bandejas con reborde.',
            'Cuatro ruedas giratorias, dos con freno, y asa de empuje.'],
    'M73': ['Estación de servido de 1.20 x 0.70 x 0.90 m de acero inoxidable AISI 304, con tres bandejas, una puerta y una cubierta.',
            'Soldaduras pulidas, sin aristas cortantes; patas con niveladores.'],
    'M75': ['Contenedor con tapa para residuos sólidos de 0.80 x 1.00 x 1.00 m, de polietileno de alta densidad.',
            'Tapa con bisagras y ruedas; color según la NTP 900.058 (código de colores para residuos).'],
    'M76': ['Portapapel higiénico de acero inoxidable o plástico ABS, para rollo estándar, fijado a la pared con tarugo y tornillo.'],
    'M77': ['Dispensador de papel toalla interfoliado de plástico ABS, con visor de nivel y cerradura, fijado a la pared.'],
    'M78': ['Cama de dos plazas de madera tornillo cepillada, con cabecera y tarima de listones.',
            'Colchón de espuma de alta densidad de dos plazas con forro lavable, incluido en la partida.'],
    'M79': ['Cama cuna de una plaza de madera tornillo cepillada, con barandas laterales de protección y tarima de listones.',
            'Colchón de espuma de alta densidad con forro lavable, incluido en la partida; acabado con barniz no tóxico.'],
    'K20': ['Cojines cuadrados de espuma de alta densidad, con forro de tela lavable y cierre.',
            'Sin piezas pequeñas desprendibles, aptos para niñas y niños pequeños.'],
    'K78': ['Piso encastrable de goma EVA de 25 mm de espesor, en planchas con bordes encastrables.',
            'Superficie antideslizante, lavable, no tóxica y amortiguadora de impactos.'],
    'K31': ['Piscina de pelotas de 1.50 m de diámetro x 0.33 m de altura, inflable o de espuma forrada.',
            'Incluye las pelotas de plástico no tóxico; sin piezas pequeñas desprendibles.'],
    'K32': ['Tobogán con escalador de plástico rotomoldeado, de uso infantil, con baranda y peldaños antideslizantes.',
            'Cantos redondeados, material no tóxico y resistente a la intemperie.'],
    'K33': ['Juego de teatro para niños: teatrín o retablo de títeres con telón y juego de títeres de tela.',
            'Materiales no tóxicos y lavables; sin piezas pequeñas desprendibles.'],
    'K37': ['Pelota de básquet N.° 6, de cuero sintético o caucho, con cámara de butilo.', 'Medida y peso oficiales del número 6.'],
    'K40': ['Pelota de fútbol N.° 5, de cuero sintético cosido, con cámara de butilo.', 'Medida y peso oficiales del número 5.'],
    'K41': ['Pelota de vóley N.° 4, de cuero sintético, con cámara de butilo.', 'Medida y peso oficiales del número 4.'],
    'K45': ['Riel de equilibrio de madera, bajo, con apoyos estables y tacos de goma en la base.',
            'Superficie lijada y barnizada, cantos redondeados.'],
    'K46': ['Aros de aluminio (ula ula) de tubo de aluminio liviano, de diámetro para uso escolar y adulto.'],
    'K47': ['Disco de goma de 1 kg para lanzamiento, de medida reglamentaria.'],
    'K48': ['Bala de 1 kg para lanzamiento, de hierro o de goma rellena, de medida reglamentaria.'],
    'K49': ['Jabalina de 600 g de aluminio, con punta metálica y agarre de cuerda.'],
    'K50': ['Jabalina de 700 g de aluminio, con punta metálica y agarre de cuerda.'],
    'K51': ['Valla de obstáculo regulable en altura, de tubo metálico con travesaño de PVC o madera y base con contrapeso.'],
    'K74': ['Guantes de entrenamiento (box) de cuero sintético con relleno de espuma y cierre de velcro.'],
    'K75': ['Saco de boxeo de cuero sintético o lona, relleno de tela prensada, con cadena y gancho de colgar.'],
    'K76': ['Pera de box de cuero sintético con cámara inflable.'],
    'K77': ['Soporte metálico para pera de box, de tubo de acero con pintura electrostática, fijado a la pared.'],
    'K79': ['Mica protectora de policarbonato transparente, resistente al impacto.'],
    'K81': ['Codera de espuma ergonómica con forro de tela y ajuste elástico.'],
    'K82': ['Guantes de espuma de alto impacto, con forro de tela y cierre de velcro.'],
}


def texto(el):
    return ''.join(t.text or '' for t in el.iter(qn('w:t')))


def codigo_word(el):
    m = re.match(r'\s*(02(?:\.\d{2})+)\s', texto(el) + ' ')
    return m.group(1) if m and el.tag == qn('w:p') else None


def clave_word(c):
    """Clave del metrado para una partida del Word (las K se cotejan por código y, si se repite, por edificación)."""
    return WORD_A_METRADO.get(c)


def coincide(cw, clave):
    if cw is None:
        return False
    if not cw.startswith('K:'):
        return cw == clave
    partes = cw.split(':'); k = clave.split(':')
    return k[0] == 'K' and k[-1] == partes[-1] and (len(partes) == 2 or k[1] == partes[1])


def con_contenido(bloque):
    """Bloque con texto propio o imagen (no solo el título, DESCRIPCIÓN.- y la unidad)."""
    if any(True for e in bloque for _ in e.iter(qn('a:blip'))):
        return True
    t = ' '.join(texto(e) for e in bloque[1:])
    t = re.sub(r'DESCRIPCI[OÓ]N\.?-?|\(?unidad de medida:?\s*und\)?|CARACTER[IÍ]STICAS', '', t, flags=re.I)
    return len(t.strip()) > 40


def generar():
    doc = docx.Document(ENTRADA)
    body = doc.element.body
    hijos = list(body.iterchildren())
    sect_final = hijos[-1]
    plant = {k: copy.deepcopy(hijos[i]) for k, i in (('grupo', 11), ('titulo', 12), ('desc', 14), ('txt', 15), ('car', 16),
                                                       ('vin', 53), ('med', 42), ('medt', 43), ('pago', 44))}
    # bloques del Word: del título de una partida al siguiente
    pos = [i for i, e in enumerate(hijos) if codigo_word(e)]
    pre = hijos[:pos[0]]
    bloques = []
    for a, b in zip(pos, pos[1:] + [len(hijos) - 1]):
        bloques.append((codigo_word(hijos[a]), hijos[a:b]))

    def parrafo(tipo, t):
        p = copy.deepcopy(plant[tipo])
        rs = p.findall(qn('w:r'))
        for x in list(p):
            if x.tag in (qn('w:r'), qn('w:proofErr')):
                p.remove(x)
        r = copy.deepcopy(rs[0]); r.find(qn('w:t')).text = t; r.find(qn('w:t')).set(qn('xml:space'), 'preserve')
        p.append(r)
        return p

    def titulo(item, desc, und=True):
        p = copy.deepcopy(plant['titulo'])
        rs = p.findall(qn('w:r'))
        r_cod, r_nom, r_und = rs[0], rs[1], rs[3]
        for x in list(p):
            if x.tag in (qn('w:r'), qn('w:proofErr')):
                p.remove(x)
        for r, t in ((r_cod, item + ' '), (r_nom, desc + '  '), (r_und, '(unidad de medida: und)' if und else '')):
            r = copy.deepcopy(r); r.find(qn('w:t')).text = t; r.find(qn('w:t')).set(qn('xml:space'), 'preserve'); p.append(r)
        return p

    def grupo(item, desc):
        return parrafo('grupo', '%s %s' % (item, desc))

    def ficha(f, donde):
        g = f['clave'][0] if not f['clave'].startswith('K:') else 'K'
        cod = f['clave'] if g != 'K' else f['clave'].split(':')[-1]
        verbo = ('el suministro' if g == 'K' else 'el suministro, el transporte, el armado y la instalación')
        out = [parrafo('desc', 'DESCRIPCIÓN.-'),
               parrafo('txt', 'Comprende %s de %s, con las características indicadas, en los ambientes de las láminas EM-01 a EM-07. '
                              'Las características son las mínimas requeridas, pero no limitativas; el contratista presentará la '
                              'ficha técnica o una muestra para la aprobación de la Supervisión.' % (verbo, f['desc'].lower())),
               parrafo('txt', 'Ubicación: ' + '; '.join(donde) + '.'),
               parrafo('car', 'CARACTERISTICAS')]
        out += [parrafo('vin', c) for c in CARACT[cod]]
        out += [parrafo('med', 'MEDICIÓN'), parrafo('medt', 'La medición será por UNIDAD.'), parrafo('pago', 'FORMA DE PAGO'),
                parrafo('medt', FORMA_PAGO[g])]
        return out

    u = E.ubicaciones()
    usados = set(); primera = {}; nuevo = []; informe = []
    for f in D.numerar():
        if f.get('tipo') != 'item':
            nuevo.append(grupo(f['item'], f['desc'])); continue
        clave = f['clave']; base = clave.split(':')[-1] if clave.startswith('K:') else clave
        if clave.startswith('K:') and base in primera and base not in ('K32', 'K33'):
            nuevo += [titulo(f['item'], f['desc']), parrafo('desc', 'DESCRIPCIÓN.-'),
                      parrafo('txt', 'Ídem partida %s. Ubicación: %s.' % (primera[base], '; '.join(u[clave])))]
            informe.append((f['item'], f['desc'], 'ídem ' + primera[base])); continue
        primera.setdefault(base, f['item'])
        b = next(((cw, bl) for cw, bl in bloques if coincide(clave_word(cw), clave) and cw not in usados), None)
        if b is not None and con_contenido(b[1]):
            usados.add(b[0])
            nuevo.append(titulo(f['item'], f['desc'])); nuevo += b[1][1:]
            informe.append((f['item'], f['desc'], 'del Word (%s)' % b[0]))
        else:
            if b is not None:
                usados.add(b[0])
            nuevo.append(titulo(f['item'], f['desc'])); nuevo += ficha(f, u[clave])
            informe.append((f['item'], f['desc'], 'completada'))
    borrados = [(cw, texto(bl[0]).strip()) for cw, bl in bloques if cw not in usados and 'unidad' in ' '.join(texto(e) for e in bl[:2])]
    # cuerpo nuevo: datos iniciales + partidas del metrado + sección final
    for e in hijos:
        body.remove(e)
    for e in pre + nuevo + [sect_final]:
        body.append(e)
    for p in list(body.iter(qn('w:p'))):                          # "DESCRIPCION" repetido con numeración automática de títulos
        n = p.find('.//' + qn('w:numPr'))
        if (n is not None and n.find(qn('w:numId')).get(qn('w:val')) == '8' and texto(p).strip() == 'DESCRIPCION'
                and p.find('.//' + qn('a:blip')) is None):
            p.getparent().remove(p)
    datos_iniciales(pre)
    for e in body.iter(qn('w:t')):                                # texto de colegio en la partida del proyector multimedia
        if e.text and 'sala de profesores' in e.text:
            e.text = e.text.replace('sala de profesores, bibliotecas', 'talleres')
    encabezados(doc)
    usadas = {b.get(qn('r:embed')) for b in body.iter(qn('a:blip'))} | {x.get(qn('r:id')) for x in body.iter() if x.get(qn('r:id'))}
    for rid, rel in list(doc.part.rels.items()):                  # imágenes de las partidas borradas: fuera del paquete
        if rel.reltype.endswith('/image') and rid not in usadas:
            doc.part.drop_rel(rid)
    doc.core_properties.author = ''; doc.core_properties.last_modified_by = ''
    doc.save(SALIDA)
    return SALIDA, informe, borrados


def poner(p, t_nuevo, desde=1):
    """Deja el rótulo (primer run) y reemplaza el resto del texto del párrafo."""
    rs = [r for r in p.iter(qn('w:r')) if r.find(qn('w:t')) is not None]
    rs[desde].find(qn('w:t')).text = t_nuevo; rs[desde].find(qn('w:t')).set(qn('xml:space'), 'preserve')
    for r in rs[desde + 1:]:
        r.getparent().remove(r)


def datos_iniciales(pre):
    for p in pre:
        t = texto(p)
        if t.startswith('PROYECTO'):
            poner(p, ' “%s”, CON CUI N° %s' % (D.PROYECTO, D.CUI))
        elif t.startswith('PRESUPUESTO'):
            poner(p, ' ARQUITECTURA - MOBILIARIO Y EQUIPAMIENTO')


def encabezados(doc):
    """Todas las secciones con el encabezado del hogar (header2); el Word traía encabezados de la I.E. Ofelia Velásquez."""
    rels = doc.part.rels
    rid_hogar = None; otros = set()
    for rid, rel in rels.items():
        if rel.reltype.endswith('/header'):
            txt = ''.join(re.findall(r'<w:t[^>]*>([^<]*)', rel.target_part.blob.decode('utf-8', 'ignore')))
            if 'OFELIA' in txt.upper():
                otros.add(rid)
            elif '2675514' in txt:
                rid_hogar = rid
    for h in doc.element.body.iter(qn('w:headerReference')):
        if h.get(qn('r:id')) in otros:
            h.set(qn('r:id'), rid_hogar)
    for rid in otros:                                              # partes sin uso: fuera del paquete
        doc.part.drop_rel(rid)


if __name__ == '__main__':
    s, inf, bor = generar()
    for x in inf:
        print('%-16s %-70s %s' % (x[0], x[1][:70], x[2]))
    print('BORRADAS:')
    for x in bor:
        print('  ', x[1][:100])
    print(s)
