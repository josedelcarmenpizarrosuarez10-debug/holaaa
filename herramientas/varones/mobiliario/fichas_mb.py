# -*- coding: utf-8 -*-
"""Características técnicas por familia de equipo, mueble e implemento (CAR Varones): las usan la memoria descriptiva y las
especificaciones técnicas, para que digan lo mismo. Cada partida se asigna a su familia por su código o su descripción."""
import re

FAMILIAS = {
    'informatica': dict(
        nombre='Equipos informáticos y audiovisuales',
        mat=['Equipos nuevos, de marca reconocida, con garantía del fabricante no menor de un año y soporte técnico en el país.',
             'Computadoras con procesador Intel Core i5 de última generación disponible (o equivalente), memoria RAM de 16 GB, '
             'almacenamiento SSD de 512 GB, monitor de 23.8", teclado y mouse en español, sistema operativo licenciado y estabilizador o UPS.',
             'Proyectores con resolución mínima WXGA, 3 500 lúmenes o más, entradas HDMI, control remoto y cable de 10 m; el interactivo con '
             'lápiz o táctil y software de pizarra; ecran retráctil de tela matte blanca; impresoras multifuncionales láser con red.'],
        proc=['Verificar con la Supervisión la marca, el modelo y las características antes de la compra.',
              'Entregar los equipos en su embalaje original, con manuales, licencias, cables y accesorios.',
              'Instalar, configurar y probar cada equipo en su ambiente (red, impresión, proyección); fijar el proyector a su rack de techo.'],
        ctrl=['Certificado de garantía y factura; prueba de encendido y funcionamiento de cada equipo en presencia de la Supervisión.',
              'Características iguales o superiores a las especificadas; números de serie anotados en el acta de entrega.']),
    'electro': dict(
        nombre='Electrodomésticos y equipos de cocina y lavandería',
        mat=['Equipos nuevos, de marca reconocida, 220 V - 60 Hz, con garantía no menor de un año y servicio técnico en la región.',
             'Lavadoras de 20 kg de carga superior con tina de acero inoxidable; refrigeradora de 315 L no frost; horno microondas de 31 L; '
             'licuadora de 1.5 L con vaso de vidrio; cocina industrial de 2 hornillas de fierro fundido con quemadores de alta presión para '
             'gas licuado; reloj de pared de 30 cm de diámetro.'],
        proc=['Verificar con la Supervisión la marca y el modelo antes de la compra.',
              'Entregar en su embalaje original; instalar en su ubicación de la lámina, con las conexiones de agua, desagüe, electricidad o '
              'gas previstas en las instalaciones del proyecto.',
              'Probar el funcionamiento de cada equipo; la cocina con prueba de hermeticidad de las conexiones de gas (agua jabonosa).'],
        ctrl=['Funcionamiento correcto en la prueba de entrega; conexiones de gas sin fugas; garantía y manuales entregados.']),
    'gas': dict(
        nombre='Balón de gas licuado',
        mat=['Balón de gas licuado de petróleo de 45 kg (uso comercial), con válvula, regulador de presión, manguera y abrazaderas, '
             'de distribuidor autorizado por OSINERGMIN.'],
        proc=['Ubicar los balones en el cuarto de gas, sobre piso nivelado, ventilados y sujetos a la pared con cadena.',
              'Conectar a la red de la cocina y probar la hermeticidad con agua jabonosa.'],
        ctrl=['Balón con precinto y sin abolladuras; conexión sin fugas.']),
    'silla': dict(
        nombre='Sillas y mesas de madera y metal',
        mat=['Estructura de tubo de acero LAC de 1" x 1/16" (o el indicado), soldado, con pintura en polvo electrostática horneada.',
             'Asiento y respaldo de madera tornillo o contraplacado de 18 mm, lijados, con cantos redondeados, sellador y barniz poliuretano.',
             'Tapones de polipropileno en las patas. Las piezas regulables (M03 y M04) tienen sistema de regulación de altura con pernos y '
             'perillas, para el uso de niños de distintas edades.'],
        proc=['Fabricar según las dimensiones de la partida; ensamblar con pernos y tuercas de seguridad.',
              'Entregar armado, limpio y protegido; ubicar en el ambiente según la lámina MB.'],
        ctrl=['Dimensiones con tolerancia de ± 1 cm; estructura sin rebabas ni filos; soldaduras continuas; estabilidad sin balanceo.',
              'Prueba de carga: el mueble no debe deformarse con el uso normal.']),
    'melamina': dict(
        nombre='Muebles de melamina',
        mat=['Tableros de melamina de 18 mm (fondos de 5.5 mm), de primera calidad y resistentes a la humedad, color a definir con la '
             'Supervisión.', 'Cantos de PVC de 2 mm pegados con adhesivo termofusible en todo borde visto.',
             'Bisagras cangrejo de cierre suave, correderas telescópicas en cajones, tiradores metálicos, chapas en puertas y cajones '
             'cuando lo indique la partida, regatones regulables.'],
        proc=['Fabricar con cortes de máquina escuadradora y canteado mecánico; uniones con minifix y tarugos.',
              'Armar en obra; fijar a la pared con escuadras y tarugos todo mueble de más de 1.20 m de altura (armarios, estantes, '
              'archivadores, casilleros), para evitar su volteo en un sismo.'],
        ctrl=['Dimensiones con tolerancia de ± 1 cm; puertas y cajones alineados y de cierre suave; cantos sin despegues.',
              'Mueble alto fijado a la pared.']),
    'metal': dict(
        nombre='Muebles y elementos metálicos',
        mat=['Plancha y perfiles de acero LAF o LAC de los espesores del fabricante, con pintura en polvo electrostática horneada.',
             'Estantes ranurados con parantes perforados, bandejas de plancha de 1/32" y pernos; ruedas con freno donde la partida '
             'indique ruedas.'],
        proc=['Armar en obra según el fabricante; nivelar; fijar a la pared los estantes de 1.80 m.',
              'Rack de proyector: fijar al techo con pernos de expansión y regular la inclinación.'],
        ctrl=['Pintura uniforme sin óxido ni rayas; armado firme; estantes nivelados y fijados.']),
    'inox': dict(
        nombre='Mobiliario de acero inoxidable',
        mat=['Acero inoxidable AISI 304 calidad alimentaria, plancha de 1.2 mm en superficies de trabajo y tubo de 1 1/2" en la estructura, '
             'acabado satinado, con regatones regulables o ruedas con freno.'],
        proc=['Fabricar con soldadura TIG pulida; armar y nivelar en su ubicación.'],
        ctrl=['Superficies lisas, sin soldaduras porosas ni bordes cortantes; estabilidad y nivelación.']),
    'cama': dict(
        nombre='Camas',
        mat=['Cama de una plaza de 0.90 x 1.90 m con cabecera, de madera tornillo cepillada o estructura metálica con pintura '
             'electrostática, tarima de listones de madera; cama de dos plazas con tarima incluida.',
             'Colchón de espuma de alta densidad con forro lavable (si lo considera el presupuesto del equipamiento).'],
        proc=['Armar en el dormitorio según la lámina; verificar que no queden aristas ni tornillos salientes.'],
        ctrl=['Estructura firme, sin balanceo; madera sin rajaduras; acabados lisos.']),
    'tapizado': dict(
        nombre='Sofás y sillones',
        mat=['Estructura de madera tornillo, espuma de alta densidad, tapiz de tela antimanchas o cuero sintético lavable, patas de madera o metálicas.'],
        proc=['Entregar armado y protegido; ubicar en la oficina de entrevista y estar o en la sala de espera.'],
        ctrl=['Tapiz sin arrugas ni costuras abiertas; estructura firme.']),
    'pizarra': dict(
        nombre='Pizarra acrílica',
        mat=['Pizarra acrílica blanca de 4.20 x 1.20 m con marco de aluminio, porta plumones y accesorios de fijación.'],
        proc=['Fijar a la pared con tarugos y tornillos, con el borde inferior a 0.90 m del piso.'],
        ctrl=['Superficie sin rayas; nivelada y firme.']),
    'higiene': dict(
        nombre='Papeleras, cestos, contenedores y dispensadores',
        mat=['Papeleras de plástico de alta densidad con pedal y tapa; cestos de acero inoxidable con pedal y balde interior; '
             'contenedores de polietileno con tapa y ruedas para residuos sólidos (colores de la NTP 900.058).',
             'Dispensadores de papel higiénico y de papel toalla interfoliado de plástico ABS o acero inoxidable, con llave.'],
        proc=['Fijar los dispensadores a la pared con tarugos y tornillos a la altura del aparato sanitario (papel higiénico a 0.60 m, '
              'papel toalla a 1.20 m); ubicar papeleras y contenedores según la lámina.'],
        ctrl=['Dispensadores firmes y operativos; tapas y pedales funcionando.']),
    'topico': dict(
        nombre='Mobiliario e implementos del tópico',
        mat=['Camillas de estructura de acero inoxidable o pintado al horno, colchoneta tapizada en vinil, respaldo reclinable y ruedas '
             'con freno; escalera de dos peldaños con antideslizante; biombo de 3 cuerpos con tela lavable; silla de ruedas plegable '
             'estándar; botiquín de madera con medicamentos básicos; coche multiusos de acero inoxidable.',
             'Bidón de oxígeno medicinal con manómetro y regulador, tensiómetro aneroide con estetoscopio, termómetro digital, con '
             'registro sanitario (DIGEMID) cuando corresponda.'],
        proc=['Entregar con certificados y registros sanitarios; armar y probar camillas, silla de ruedas y equipos.'],
        ctrl=['Registro sanitario y garantía; funcionamiento de frenos, reclinación y regulación.']),
    'implemento': dict(
        nombre='Implementos deportivos y de psicomotricidad',
        mat=['Implementos nuevos, de material no tóxico y resistente al uso intensivo, de las medidas y pesos indicados (pelotas oficiales '
             'por número, jabalinas, bala y disco de las masas indicadas, colchonetas forradas, piso encastrable de goma EVA de 25 mm).',
             'Juegos de psicomotricidad (tobogán, piscina de pelotas, juegos de cocina, lavandería y teatro, cojines) de plástico o espuma '
             'de alta densidad con forro lavable, sin piezas pequeñas desprendibles, aptos para niños de 3 a 5 años.'],
        proc=['Entregar en su embalaje con la ficha del fabricante; armar los juegos y fijar el soporte de la pera de box.'],
        ctrl=['Conformidad con las cantidades y características; ausencia de bordes cortantes y de piezas sueltas.']),
    'otros': dict(
        nombre='Otros elementos',
        mat=['Macetero de concreto o fibra de vidrio con drenaje; atril de mesa de madera para dibujo; parihuelas de madera tornillo '
             'de 0.90 x 0.50 x 0.20 m para el almacenaje sobre el piso.'],
        proc=['Entregar y ubicar según la lámina.'],
        ctrl=['Dimensiones y acabados conformes.']),
}

POR_CODIGO = {
    'E1': 'informatica', 'E2': 'informatica', 'E3': 'informatica', 'E6': 'informatica', 'E7': 'informatica', 'E9': 'informatica',
    'E18': 'informatica', 'E4': 'electro', 'E5': 'electro', 'E13': 'electro', 'E16': 'electro', 'E17': 'electro', 'E19': 'electro',
    'E20': 'gas', 'M3': 'silla', 'M4': 'silla', 'M7': 'silla', 'M8': 'silla', 'M16': 'silla', 'M21': 'melamina', 'M28': 'melamina',
    'M30': 'melamina', 'M31': 'melamina', 'M36': 'melamina', 'M37': 'melamina', 'M39': 'melamina', 'M42': 'melamina', 'M54': 'melamina',
    'M56': 'melamina', 'M57': 'melamina', 'M61': 'melamina', 'M13': 'metal', 'M51': 'metal', 'M64': 'metal', 'M26': 'inox',
    'M52': 'inox', 'M71': 'topico', 'M73': 'inox', 'M55': 'cama', 'M78': 'cama', 'M32': 'tapizado', 'M34': 'tapizado', 'M63': 'tapizado',
    'M69': 'pizarra', 'M60': 'higiene', 'M62': 'higiene', 'M75': 'higiene', 'M76': 'higiene', 'M77': 'higiene', 'M20': 'topico',
    'M27': 'topico', 'M65': 'topico', 'M67': 'topico', 'M70': 'topico', 'M14': 'otros', 'M15': 'otros', 'M68': 'otros',
}


def familia(cod, desc='', ambiente=''):
    if cod in POR_CODIGO:
        return POR_CODIGO[cod]
    if re.search('TOPICO|TÓPICO', ambiente or ''):
        return 'topico'
    return 'implemento'
