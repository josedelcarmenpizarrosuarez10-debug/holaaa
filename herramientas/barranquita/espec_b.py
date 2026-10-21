"""Especificaciones tecnicas de drenaje pluvial (red de cunetas) de la I.E. N.° 0590 Barranquita (C.I. 468901).
Las partidas (codigo, descripcion, unidad) son las del metrado (metrado_b.py), en el mismo orden; no se agregan ni se quitan.
Salida: ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import cantidades_b as Q, metrado_b as MB
from word_b import Doc

SAL = os.path.join(RAIZ, "entregables_barranquita", "ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx")
PLANOS = "DC-01 a DC-19"

# texto de cada partida: descripcion, materiales, equipos, ejecucion, control, medicion, pago
E = {
"LIMPIEZA MANUAL DE TERRENO": dict(
    des="Comprende la eliminación manual de malezas, raíces, basura, desmonte y todo elemento que interfiera con el trazo de las cunetas, en la franja de trabajo indicada en los planos.",
    equ="Herramientas manuales (palas, picos, rastrillos, carretillas).",
    eje=["Se limpia la franja de cada eje con el ancho de excavación (0.90 m: cuneta de 0.60 m más 0.15 m a cada lado).",
         "El material retirado se acopia en un lugar autorizado para su eliminación; no se quema ni se deja en las áreas de trabajo."],
    ctrl="El supervisor verifica que la franja quede libre de materia orgánica y obstáculos antes del trazo.",
    med="Metro cuadrado (m²): longitud del eje por el ancho de la franja de trabajo."),
"TRAZO, NIVELES Y REPLANTEO PRELIMINAR": dict(
    des="Comprende el replanteo en el terreno de los ejes de cuneta, los quiebres a 45°, los empalmes, las tapas de inspección y las descargas, y el control de niveles del borde (+184.65; +184.50 en el patio de maniobra) y de la cota de fondo.",
    mat="Yeso, estacas de madera, cordel, pintura esmalte.",
    equ="Estación total o nivel topográfico, wincha, jalones y herramientas manuales.",
    eje=["Se ubican los ejes con las coordenadas de la planta DC-01 y se marcan los quiebres a 45° (chaflanes de 0.60 m).",
         "Se colocan niveletas con la cota de fondo de cada sección según los perfiles DC-03 a DC-11 y el cuadro de tramos DC-02.",
         "Se verifica que la pendiente de la cota de fondo no sea menor de 0.5 % y que no haya contrapendientes."],
    ctrl="El trazo y los niveles se aprueban por el supervisor antes de excavar.",
    med="Metro cuadrado (m²): longitud del eje por el ancho de la franja de trabajo."),
"EXCAVACIÓN MANUAL DE ZANJAS P/CUNETAS": dict(
    des="Comprende la excavación de las zanjas para alojar las cunetas, desde el nivel de piso terminado hasta 0.20 m bajo la cota de fondo (losa de fondo de 0.10 m y solado de 0.10 m), con el ancho de 0.90 m.",
    equ="Herramientas manuales; carretillas.",
    eje=["Se excava respetando las niveletas; las paredes se mantienen estables y, de ser necesario, se entiban.",
         "El fondo se deja plano, sin material suelto, con la pendiente del perfil.",
         "El material apto se acopia para el relleno; el excedente se elimina."],
    ctrl="Se verifican ancho, profundidad y pendiente de la zanja antes del refine.",
    med="Metro cúbico (m³): longitud por ancho de excavación por la profundidad promedio de cada eje (h promedio + 0.20 m)."),
"REFINE, NIVELACIÓN Y COMPACTACIÓN EN TERRENO NORMAL": dict(
    des="Comprende el perfilado del fondo de la zanja, su nivelación con la pendiente de diseño y su compactación, para recibir el solado.",
    equ="Plancha compactadora o pisón manual; herramientas manuales.",
    eje=["Se humedece el fondo a la humedad óptima y se compacta en una capa hasta lograr una superficie firme y uniforme.",
         "Se corrigen los sobreexcavados con material seleccionado compactado, nunca con material suelto."],
    ctrl="Se verifica la cota del fondo cada 5 m y la ausencia de zonas blandas.",
    med="Metro cuadrado (m²): longitud por el ancho exterior de la cuneta (0.60 m)."),
"RELLENO COMPACTADO C/MATERIAL PROPIO SELECCIONADO": dict(
    des="Comprende el relleno de los espacios entre los muros de la cuneta y las paredes de la zanja con material propio seleccionado, libre de materia orgánica y piedras mayores de 2\".",
    equ="Pisón manual o plancha compactadora; herramientas manuales.",
    eje=["El relleno se coloca después del desencofrado y cuando el concreto tiene la resistencia suficiente.",
         "Se coloca en capas de 0.15 m, humedecidas y compactadas en simultáneo a ambos lados para no empujar los muros.",
         "La última capa queda al nivel de la subrasante del piso o del área verde."],
    ctrl="Compactación mínima de 95 % del Proctor modificado en las capas bajo pisos y veredas.",
    med="Metro cúbico (m³): longitud por el ancho de relleno (0.90 − 0.60 m) por la altura promedio."),
"ELIMINACIÓN DE MATERIAL EXCEDENTE D<1Km": dict(
    des="Comprende el carguío y transporte del material excedente de las excavaciones a un botadero autorizado, a una distancia menor de 1 km.",
    equ="Herramientas manuales, carretillas y volquete.",
    eje=["Se elimina el volumen excedente (excavación menos relleno) afectado por el factor de esponjamiento de 1.25.",
         "El material no se deja en vías ni en terrenos vecinos."],
    ctrl="El supervisor verifica el destino del material.",
    med="Metro cúbico (m³): (excavación − relleno) × 1.25."),
"PERFILADO MANUAL DE TERRENO EN DESCARGAS": dict(
    des="Comprende el perfilado manual del terreno natural al pie del cerco, frente a cada descarga (D1 a D4), para que el agua salga libre sobre el terreno exterior.",
    equ="Herramientas manuales.",
    eje=["Se recorta el terreno en un ancho de 0.60 m y en la longitud indicada en las láminas DC-16 a DC-19, hasta quedar por debajo de la cota de fondo de la descarga.",
         "No se construyen obras fuera del cerco; en la descarga D2 se recomienda proteger la entrega contra la erosión, coordinándolo con el propietario del terreno exterior."],
    ctrl="Se verifica que el agua escurra sin empozarse frente al pase del cerco.",
    med="Metro cuadrado (m²): ancho de 0.60 m por la longitud de perfilado de cada descarga."),
"CONCRETO f'c=100 kg/cm2 PARA SOLADO E=4''": dict(
    des="Comprende la capa de concreto pobre de 4\" (0.10 m) de espesor bajo la losa de fondo de las cunetas, para nivelar y limpiar la base.",
    mat="Cemento Portland tipo I, hormigón (o arena gruesa y piedra chancada) y agua limpia.",
    equ="Mezcladora de concreto; herramientas manuales; regla de madera.",
    eje=["Se vacía sobre el fondo refinado y humedecido, con la pendiente de la cota de fondo.",
         "La superficie se deja plana y rugosa, sin depresiones, para recibir la losa de fondo."],
    ctrl="Espesor y nivel verificados cada 5 m; resistencia f'c = 100 kg/cm².",
    med="Metro cuadrado (m²): longitud por el ancho exterior de la cuneta (0.60 m)."),
"CONCRETO f'c=175 kg/cm2 PARA CUNETAS": dict(
    des="Comprende el concreto de los muros (0.10 m), de la losa de fondo (0.10 m) y de la losa tapa de los tramos tapados (0.10 m) de las cunetas de 0.60 m de ancho total y 0.40 m libres, con la profundidad variable de los perfiles.",
    mat="Cemento Portland tipo I; arena gruesa y piedra chancada de 1/2\" según NTP 400.037; agua potable; aditivos solo con aprobación del supervisor.",
    equ="Mezcladora de concreto, vibrador de concreto, herramientas manuales.",
    eje=["Antes del vaciado se verifican encofrados, acero (donde corresponde), niveles y la colocación de las juntas cada 3.00 m.",
         "El concreto se coloca en capas y se vibra sin segregación; los muros se vacían de manera continua entre juntas.",
         "El borde superior queda al ras del piso terminado (+184.65; +184.50 en el patio de maniobra), con el rebaje para el marco de la rejilla en los tramos abiertos.",
         "En los tramos tapados los muros se rebajan 0.10 m para la losa tapa, que queda al nivel de la vereda; se dejan los vanos de las tapas de inspección.",
         "Los quiebres a 45° y los empalmes se vacían con la forma de la planta, sin aristas que obstruyan el flujo; el fondo se acaba liso."],
    ctrl="Resistencia f'c = 175 kg/cm² a 28 días (probetas según NTP 339.033 y 339.034, una serie por cada día de vaciado o cada 50 m³); asentamiento de 3\" a 4\"; tolerancia de la cota de fondo ± 0.5 cm.",
    med="Metro cúbico (m³): volumen de muros, losa de fondo y losa tapa según los perfiles, descontando las tapas de inspección."),
"ENCOFRADO Y DESENCOFRADO DE CUNETAS": dict(
    des="Comprende los encofrados de las caras interiores y exteriores de los muros y del fondo y los cantos de la losa tapa, y su retiro.",
    mat="Madera tornillo o triplay, clavos, alambre negro N° 8, desmoldante.",
    equ="Herramientas manuales.",
    eje=["Los encofrados se construyen alineados, aplomados y estancos, con la forma de los quiebres a 45°.",
         "Se desencofran los muros a las 24 horas y el fondo de la losa tapa a los 7 días como mínimo, sin golpear el concreto."],
    ctrl="Tolerancia de alineamiento y plomo ± 5 mm.",
    med="Metro cuadrado (m²): área de contacto entre el encofrado y el concreto."),
"ACERO f'y=4200 kg/cm2 PARA CUNETA": dict(
    des="Comprende el habilitado y colocación del acero corrugado de 3/8\" en las cunetas con profundidad de 0.40 m o más (de la rejilla al fondo) y en los tramos tapados. Con profundidad menor de 0.40 m la cuneta es de concreto simple.",
    mat="Acero corrugado grado 60 (f'y = 4200 kg/cm²) según NTP 341.031; alambre negro N° 16; separadores de concreto.",
    equ="Cizalla, dobladora, herramientas manuales.",
    eje=["U de 3/8\" @0.25 m en muros y losa de fondo, con ganchos de 0.10 m; barras longitudinales de 3/8\" @0.20 m.",
         "Losa tapa de los tramos tapados: 3/8\" @0.20 m transversal y 3 barras longitudinales.",
         "Recubrimiento de 0.04 m; las barras se amarran y se apoyan en separadores; los traslapes no se ubican en las juntas."],
    ctrl="Diámetros, espaciamientos y recubrimientos verificados antes del vaciado; certificados de calidad del acero.",
    med="Kilogramo (kg): longitud de cada barra por su peso (3/8\" = 0.56 kg/m), según la hoja METRADO ACERO."),
"CURADO DE CONCRETO EN CUNETA": dict(
    des="Comprende el curado de las superficies de concreto expuestas de las cunetas para asegurar su resistencia y evitar fisuras.",
    mat="Agua limpia o curador químico aprobado; arpillera.",
    equ="Mochila pulverizadora; herramientas manuales.",
    eje=["Se inicia apenas el concreto endurece y se mantiene húmedo durante 7 días como mínimo.",
         "Con curador químico se aplica en una capa uniforme según el fabricante."],
    ctrl="El supervisor verifica la continuidad del curado.",
    med="Metro cuadrado (m²): caras interiores de muros, fondo interior, coronas de muro y losa tapa."),
"REJILLA METALICA P/CUNETA C/PL 1''x 3/16'' Y ANGULO 1'' x 1'' x 3/16''": dict(
    des="Comprende la fabricación y colocación de la rejilla móvil de platinas de 1\" x 3/16\" sobre marco de ángulo de 1\" x 1\" x 3/16\" anclado al borde de la cuneta, en los tramos abiertos.",
    mat="Platina de acero de 1\" x 3/16\", ángulo de 1\" x 1\" x 3/16\", soldadura E-6011, anticorrosivo y esmalte.",
    equ="Máquina de soldar, amoladora, herramientas manuales.",
    eje=["Las platinas van transversales al eje de la cuneta, soldadas al marco, en módulos móviles para la limpieza.",
         "El marco se ancla en el rebaje del borde de los muros, de modo que la rejilla quede al ras del piso.",
         "Las piezas se limpian y se pintan con dos capas de anticorrosivo y una de esmalte."],
    ctrl="Nivel de la rejilla al ras del piso; soldaduras continuas; módulos que asienten sin juego.",
    med="Metro (m): longitud de cuneta con rejilla."),
"TAPA DE INSPECCION 0.60m x 0.60m": dict(
    des="Comprende las tapas de inspección de concreto armado de 0.60 x 0.60 m y 0.10 m de espesor, removibles, en los tramos tapados: al inicio y al final, en cada empalme y a 10 m como máximo.",
    mat="Concreto f'c = 175 kg/cm², acero de 3/8\" en parrilla @0.15 m en ambos sentidos, asas de fierro liso de 3/8\".",
    equ="Herramientas manuales.",
    eje=["Las tapas se vacían con molde, con dos asas empotradas, y se colocan en los vanos dejados en la losa tapa.",
         "Quedan al ras de la vereda o del piso, con holgura perimetral de 5 mm."],
    ctrl="Dimensiones, nivel y asiento verificados en obra; ubicación según la planta DC-01.",
    med="Unidad (und): tapa colocada."),
"JUNTA DE DILATACION E=1\" CON SELLADOR ASFALTO": dict(
    des="Comprende las juntas de dilatación de 1\" en toda la sección en U de la cuneta (muros y losa de fondo) cada 3.00 m, rellenas con sellador asfáltico (EG-2013, sección 510).",
    mat="Tecnopor de 1\" como relleno y sellador asfáltico en caliente o elastomérico.",
    equ="Herramientas manuales; calentador.",
    eje=["Se coloca el relleno de 1\" en el encofrado antes del vaciado, perpendicular al eje.",
         "Se limpia la junta y se sella la cara interior con 1\" de profundidad, al ras de la superficie del concreto."],
    ctrl="Continuidad del sello en toda la sección en U.",
    med="Metro (m): número de juntas por el perímetro exterior de la sección en U."),
"JUNTA E=1\" CON SELLADOR ASFALTICO ENTRE CUNETA Y PISO ADYACENTE": dict(
    des="Comprende la junta longitudinal de 1\" entre el borde de la cuneta y el piso o vereda adyacente, sellada con asfalto al mismo nivel del piso terminado.",
    mat="Tecnopor de 1\" y sellador asfáltico.",
    equ="Herramientas manuales; calentador.",
    eje=["Se deja el relleno de 1\" al vaciar el piso contra el muro de la cuneta.",
         "Se retira 1\" superior del relleno y se sella con asfalto al ras del piso."],
    ctrl="Sello continuo y al nivel del piso.",
    med="Metro (m): longitud de los bordes de cuneta junto a piso o vereda."),
}


def generalidades(D):
    D.h(1, "Generalidades")
    D.h(2, "Alcance")
    D.p("Las presentes especificaciones técnicas corresponden a la especialidad de drenaje pluvial (red de cunetas) del proyecto "
        "“Mejoramiento y ampliación del servicio de educación primaria en I.E. N° 0590 distrito de Barranquita de la provincia de Lamas del "
        "departamento de San Martín”, C.I. N° 468901. Comprenden las partidas del metrado, en el mismo orden y con las mismas unidades, y se "
        "complementan con los planos %s, la memoria descriptiva y la memoria hidrológica." % PLANOS)
    D.h(2, "Normas")
    D.vinetas(["Reglamento Nacional de Edificaciones: OS.060, E.060, IS.010, G.050.", "Normas Técnicas Peruanas de cemento, agregados, acero y ensayos de concreto.",
               "Especificaciones Técnicas Generales para Construcción EG-2013 (MTC).", "R.V.M. N° 208-2019-MINEDU (locales educativos)."])
    D.h(2, "Materiales")
    D.vinetas([("Cemento: ", "Portland tipo I (NTP 334.009), almacenado bajo techo y sobre tarimas."),
               ("Agregados: ", "arena gruesa y piedra chancada limpias, según NTP 400.037."),
               ("Agua: ", "potable o limpia, libre de aceites, ácidos y materia orgánica."),
               ("Acero: ", "corrugado grado 60 (NTP 341.031), sin óxido suelto ni grasa.")])
    D.h(2, "Datos de la red de cunetas")
    q = Q.por_eje()
    D.p("Sección rectangular de 0.60 m de ancho total (muros de 0.10 m y 0.40 m libres), losa de fondo de 0.10 m sobre solado de 4\"; "
        "profundidad variable de 0.30 m a %.2f m; cota de fondo con pendiente mínima de 0.5 %%; borde al ras del piso (+184.65; +184.50 "
        "en el patio de maniobra). Longitud total %.2f m (%.2f m tapados). Quiebres a 45° en planta. Cuatro descargas por pase en el "
        "cimiento del cerco (D1 a D4)." % (max(x["h_max"] for x in q), sum(x["L"] for x in q), sum(x["L_tapado"] for x in q)))
    D.h(2, "Seguridad y medio ambiente")
    D.p("Los trabajos se ejecutan según la Norma G.050 y el plan de seguridad de la obra: equipos de protección personal, señalización de "
        "zanjas abiertas y orden y limpieza. El material excedente se dispone en botaderos autorizados.")
    D.h(2, "Pago")
    D.p("Las partidas se pagan al precio unitario del presupuesto por la cantidad realmente ejecutada y aprobada por el supervisor, medida "
        "según lo indicado en cada partida. El precio comprende materiales, mano de obra, equipos, herramientas e imprevistos.")


def construir():
    resumen = MB.construir()                    # mismas partidas del metrado
    def cuerpo(D):
        generalidades(D)
        D.h(1, "Especificaciones por partida")
        for it, desc, und, f in resumen:
            if f is None:
                D.d.add_heading("%s  %s" % (it, desc), level=2); D.indice.append("%s %s" % (it, desc)); continue
            D.d.add_heading("%s  %s" % (it, desc), level=3)
            e = E[desc]
            D.p(e["des"], neg="Descripción. ")
            if e.get("mat"): D.p(e["mat"], neg="Materiales. ")
            if e.get("equ"): D.p(e["equ"], neg="Equipos y herramientas. ")
            D.p("", neg="Método de ejecución.")
            D.vinetas(e["eje"])
            D.p(e["ctrl"], neg="Control de calidad. ")
            D.p(e["med"].replace("(m²)", "").replace("(m³)", "").replace("(kg)", "").replace("(m)", "").replace("(und)", "") if False else e["med"],
                neg="Unidad de medida (%s). " % und)
            D.p("Se paga por %s al precio unitario del presupuesto, previa aprobación del supervisor." % {"m²": "metro cuadrado", "m³": "metro cúbico",
                "kg": "kilogramo", "m": "metro lineal", "und": "unidad"}[und], neg="Forma de pago. ")
    D0 = Doc("ESPECIFICACIONES TÉCNICAS"); cuerpo(D0)
    D = Doc("ESPECIFICACIONES TÉCNICAS"); D.caratula("ESPECIFICACIONES TÉCNICAS", "Drenaje pluvial - red de cunetas")
    D.contenido(D0.indice); cuerpo(D); D.guardar(SAL)


if __name__ == "__main__":
    construir()
