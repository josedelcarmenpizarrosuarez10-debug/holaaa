"""Especificaciones tecnicas de drenaje pluvial (ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL.docx).

Capitulo I de generalidades y capitulo II con una ficha por partida (descripcion, materiales, equipos, procedimiento,
control de calidad, seguridad, unidad, metodo de medicion y forma de pago), en el formato de los expedientes de CAR Mujeres
(CUI 2717013) y de la I.E. N.° 0590 Barranquita (C.I. 468901). Las partidas (codigo, descripcion, unidad) son las del metrado
de este proyecto (metrado.libro), en el mismo orden: no se agregan ni se quitan. Los textos comunes vienen de espec_textos;
lo propio de la red de cunetas (secciones por sector, acero solo con h >= 0.40 m o tapado, rejilla, tapas de inspeccion,
lloraderos, descargas por el cerco, montantes de 4" y sumideros) se escribe aqui con los datos del diseno.
"""
import copy

from . import espec_textos as E, word
from .espec_textos import p, l, t, bloque, EPP
from .metrado import SOBREANCHO, ESPONJ, JUNTA_CADA, REC, KG38, SEP_T, SEP_L, DADO, FC

SEG_ALTURA = l(EPP, "Trabajo en altura en aleros y muros: andamio certificado o escalera estable, arnes de cuerpo entero con linea de vida sobre 1.80 m (Norma G.050).",
               "Guantes de cuero para manipular la plancha; proteger los bordes cortados.")


def _sec(secciones, nombre, contenido):
    """Reemplaza (o agrega antes de la unidad de medida) un apartado de la ficha de una partida."""
    for s in secciones:
        if s[0] == nombre:
            s[1] = contenido; return secciones
    i = next(k for k, s in enumerate(secciones) if s[0] == "UNIDAD DE MEDIDA")
    secciones.insert(i, [nombre, contenido]); return secciones


def _med(secciones, texto): return _sec(secciones, "METODO DE MEDICION", [p(texto)])


def _m(v): return ("%.2f" % v)


class Datos:
    """Lo que las fichas necesitan del diseno: secciones por eje, niveles, descargas, laminas y cantidades."""

    def __init__(self, P, cfg, q, V, laminas, TT, SM, LLt):
        self.P, self.q = P, q
        self.L = sum(x["L"] for x in q); self.Lt = sum(x["L_tapado"] for x in q); self.hmax = max((x["h_max"] for x in q), default=0.30)
        self.bs = sorted({x["b"] for x in q}) or [P["b_int"]]
        self.b = self.bs[-1]; self.be = self.b + 2 * P["e_muro"]; self.bexc = self.be + 2 * SOBREANCHO
        niv = cfg.get("niveles", {}) or {}
        self.npt = niv.get("borde_cuneta") or niv.get("npt")
        self.zonas = [(z.get("nombre", "zona"), z["nivel"]) for z in niv.get("zonas", []) if z.get("nivel") is not None]
        self.D = [d["D"] for d in V.get("descargas", [])]
        cod = [x["codigo"] for x in laminas]
        self.planos = ("%s a %s" % (cod[0], cod[-1])) if cod else "de drenaje pluvial"
        self.planta = cod[0] if cod else "de planta"
        self.cortes = cod[1] if len(cod) > 1 else self.planta
        self.TT, self.SM, self.LLt = TT, SM, LLt

    def anchos_txt(self):
        if len(self.bs) == 1:
            return "%.2f m libres (ancho total %.2f m)" % (self.b, self.b + 2 * self.P["e_muro"])
        return "%s m libres segun el eje (anchos totales de %s m; una medida por sector de descarga, cuadro de ejes)" % (
            " o ".join(_m(b) for b in self.bs), " o ".join(_m(b + 2 * self.P["e_muro"]) for b in self.bs))

    def niveles_txt(self):
        if self.npt is None: return "al ras del piso terminado"
        s = "+%.2f al ras del piso terminado" % self.npt
        if self.zonas: s += "; " + "; ".join("+%.2f en %s" % (n, nom.lower()) for nom, n in self.zonas)
        return s

    def descargas_txt(self):
        if not self.D: return "las descargas"
        return ("la descarga %s" % self.D[0]) if len(self.D) == 1 else "las descargas %s a %s" % (self.D[0], self.D[-1])


def cuneta(D):
    """Datos de la cuneta de este proyecto para los textos comunes (espec_textos.CUNETA)."""
    P = D.P
    return dict(E.CUNETA, b=D.b, em=P["e_muro"], ef=P["e_fondo"], et=P["e_tapa"], be=D.be,
                acero_long="3/8\" @%.2f m en muros y losa de fondo" % SEP_L, acero_tr="3/8\" en U @%.2f m con ganchos de 0.10 m" % SEP_T,
                junta=JUNTA_CADA, tapa=(P["tapa_lado"], P["tapa_lado"], 0.10),
                tapa_acero="parrilla simple de 3/8\" @0.15 m en ambos sentidos y dos asas de fierro liso de 3/8\"", S=100 * P["S0"], rej_reb=0.05,
                dado=DADO, fcol=(0.20, 0.15, 1.30), S_can=1.00, n_cun=P["n_cap"], n_can=0.013, sep_sop=0.60)


def ficha(pt, D, Pd):
    d = pt["desc"].upper(); und = pt["und"]; P = D.P; K = E.CUNETA
    hfs = P["e_fondo"] + P["e_solado"]
    # ---------------------------------------------------------------- partidas propias de la red de cunetas
    if "PERFILADO" in d:
        return bloque([p("Comprende el perfilado manual del terreno natural al pie del cerco, frente a %s, para que el agua que sale por el pase en el cimiento "
                         "del cerco escurra libre sobre el terreno exterior, sin empozarse. No se construyen obras fuera del cerco." % D.descargas_txt())],
                      equ=l("Pico, lampa, rastrillo, carretilla, nivel y wincha."),
                      proc=l("Ubicar cada descarga segun la planta %s y su perfil longitudinal." % D.planta,
                             "Recortar el terreno en el ancho exterior de la cuneta y en la longitud indicada en el metrado, hasta quedar por debajo de la cota de fondo de la descarga, con pendiente hacia afuera.",
                             "Donde el terreno exterior baje en talud, proteger la entrega contra la erosion segun indique la Supervision."),
                      ctrl=l("Se verificara con agua que el escurrimiento salga libre frente al pase del cerco, sin empozamiento."),
                      seg=l(EPP, "Senalizar la zona de trabajo junto al cerco."), und=und,
                      medicion=[p("Se medira el area perfilada: ancho exterior de la cuneta por la longitud de perfilado de cada descarga, segun el metrado.")])
    if "JUNTA" in d and "PISO" in d:
        return bloque([p("Comprende la junta longitudinal de 1\" (25 mm) entre el borde exterior de la cuneta y el piso, vereda o patio de concreto adyacente, de modo que "
                         "ambos trabajen en forma independiente, rellena con plancha de poliestireno expandido (tecnopor) y sellada en su cara superior con sellador "
                         "asfaltico de 1\" x 2\" (asfalto liquido RC-250 y arena gruesa) al ras del piso terminado. En los bordes junto a area verde no se coloca.")],
                      mat=l("Plancha de tecnopor de 1\" (densidad 10 a 15 kg/m³) en tiras de la altura del piso; asfalto liquido RC-250 (NTP 321.028); arena gruesa limpia y seca."),
                      equ=l("Cuchilla, regla, wincha, recipiente para calentar el asfalto, tacos de madera, escobilla."),
                      proc=l("Fijar la tira de tecnopor contra la cara exterior del muro de la cuneta antes de vaciar el piso adyacente.",
                             "Vaciar el piso contra la plancha; mantenerla vertical y continua en todo el borde.",
                             "Retirar 2\" (50 mm) superiores de tecnopor; limpiar y secar; colocar el sellador asfaltico compactándolo con tacos hasta el ras del piso."),
                      ctrl=l("Junta continua en toda la longitud del borde junto al piso, sin contacto directo entre el concreto de la cuneta y el del piso; sello compacto y al ras."),
                      seg=l(EPP, "Calentar el asfalto lejos de materiales inflamables, con extintor a la mano."), und=und,
                      medicion=[p("Se medira la longitud de los bordes de cuneta que colindan con piso, vereda o patio, a cada lado del eje, segun la hoja METRADO JUNTA DE DILATACION.")])
    if "LLORADERO" in d:
        n = sum(x["n"] for x in D.LLt)
        return bloque([p("Comprende los lloraderos del muro de la cuneta que está en contacto con area verde (en el muro que da a vereda, patio o piso no se colocan), que "
                         "alivian la presion del agua infiltrada en el terreno y la descargan dentro de la cuneta; reemplazan a los drenes franceses. Cada unidad comprende: pase "
                         "de tuberia PVC-U de 3\" a traves del muro, a media altura entre el fondo y el borde, con pendiente hacia el interior de la cuneta; caja filtrante de "
                         "0.30 x 0.30 x 0.30 m de grava de 3/4\" a 1 1/2\" en el lado del terreno, envuelta integramente en geotextil no tejido; y la excavacion local y el relleno "
                         "compactado alrededor del filtro."),
                       p("Espaciamiento de %.2f m a lo largo del muro en contacto con area verde: %d lloraderos en %d tramos, segun la planta %s y el cuadro de lloraderos." % (
                           P["llor_sep"], n, len(D.LLt), D.planta))],
                      mat=l("Tuberia PVC-U de 3\" (NTP 399.003), 0.30 m por lloradero (ancho del muro mas el ingreso a la caja filtrante).",
                            "Grava zarandeada limpia de 3/4\" a 1 1/2\": 0.027 m³ por lloradero.",
                            "Geotextil no tejido de 200 g/m² como minimo, con traslapes de 0.10 m: 0.60 m² por lloradero."),
                      equ=l("Sierra para PVC, lima, wincha, nivel de mano, lampa, pison de mano."),
                      proc=l("Colocar los niples de PVC en el encofrado del muro antes del vaciado, en la ubicacion y a la altura del detalle, con pendiente hacia la cuneta; taponar provisionalmente los extremos.",
                             "Desencofrado el muro, excavar en el lado del area verde el hueco de la caja filtrante de 0.30 x 0.30 x 0.30 m frente a cada niple.",
                             "Forrar el hueco con el geotextil, llenar con la grava sin contaminarla con tierra, cerrar el geotextil por encima con su traslape y rellenar y compactar alrededor con material propio.",
                             "Retirar los tapones provisionales y verificar que cada lloradero quede libre."),
                      ctrl=l("Lloraderos alineados, a la separacion indicada y libres; el agua vertida en la caja filtrante sale por el niple a la cuneta; geotextil sin roturas."),
                      seg=l(EPP), und=und, medicion=[p("Se contara el numero de lloraderos instalados y aprobados, segun la hoja METRADO LLORADEROS.")])
    if "MONTANTE" in d and "TUBER" in d:
        return bloque([p("Comprende el suministro e instalacion de las montantes de tuberia PVC-SAP para desague de 4\" que bajan el agua de las canaletas de los techos a las cunetas. "
                         "Cada montante va en la esquina de la edificacion, adosada al muro y protegida en su tramo inferior por una falsa columna de concreto; su codo inferior entrega en la "
                         "cuneta del tramo con rejilla mas cercano. Todas las montantes son de 4\": donde el area de techo lo pide se colocan 3 o 4 montantes por lado en lugar de un diametro mayor."),
                       p("Numero de montantes: %d; longitud total %.2f m (altura del alero mas la salida a la cuneta), segun la planta %s y la hoja METRADO MONTANTES." % (
                           D.TT["metrado"]["montantes_und"], D.TT["metrado"]["montante_m"], D.planta))],
                      mat=l("Tuberia PVC para desague de 4\" (NTP 399.003) en tubos de 3 m; cemento solvente y limpiador; abrazaderas, colgadores y codos de las partidas de accesorios."),
                      equ=l("Sierra para PVC, lima, nivel, plomada, taladro, andamio o escalera."),
                      proc=l("Replantear cada montante en la esquina indicada en la planta, a plomo y adosada al muro.",
                             "Unir la boquilla de la canaleta con el codo superior y bajar la tuberia fijandola al muro con una abrazadera cada 4.00 m como maximo (minimo una).",
                             "En la base, unir el codo de 90° y el tramo horizontal que entrega a la cuneta sobre su rejilla o por el muro, con pendiente hacia la cuneta.",
                             "Vaciar la falsa columna que protege el tramo inferior de la montante."),
                      ctrl=l("Montantes a plomo, uniones estancas; prueba de llenado con agua desde la canaleta sin fugas."), seg=SEG_ALTURA, und=und,
                      medicion=[p("Se medira la longitud de tuberia instalada desde la boquilla de la canaleta hasta la entrega en la cuneta, segun la hoja METRADO MONTANTES.")])
    if "SUMIDERO" in d and und == "und":
        sm = D.SM["metrado"]
        return bloque([p("Comprende el suministro e instalacion de los sumideros de piso en las areas libres sin cobertura (patios, estacionamientos y pavimentos; no en areas verdes ni en veredas) "
                         "que no alcanzan a escurrir a una cuneta: rejilla metalica de platinas de 1\" x 3/16\" de 0.25 m de lado sobre marco de angulo L 1\" x 1\" x 3/16\" anclado al concreto, "
                         "caja bajo la rejilla con fondo inclinado hacia la salida, salida de PVC de 4\" y codo de 90° hacia la tuberia de 4\" que descarga en la cuneta mas cercana."),
                       p("Numero de sumideros: %d, segun la planta %s." % (sm["sumideros_und"], D.planta))],
                      mat=l("Platina de 1\" x 3/16\" y angulo L 1\" x 1\" x 3/16\" de acero A36; anclajes de fierro de 3\" x 3/8\"; accesorios de PVC de 4\"; pintura anticorrosiva y esmalte; mortero 1:4 para el asentado."),
                      equ=l("Maquina de soldar, amoladora, herramientas de albanileria."),
                      proc=l("Fabricar la rejilla y el marco, soldar los anclajes al marco y proteger todo con anticorrosivo y esmalte.",
                             "Formar la caja con fondo inclinado hacia la salida y conectarla con el codo de 90° a la tuberia que va a la cuneta.",
                             "Asentar el sumidero al ras del piso terminado, en el punto bajo, con la pendiente del piso hacia el sumidero."),
                      ctrl=l("Ras con el piso; el agua de la superficie escurre sin empozarse."), seg=E.SEG_SOLD, und=und, medicion=[p("Se contara el numero de sumideros instalados.")])
    if "TUBER" in d and "4" in d:
        s = E.espec(pt, Pd, dict(colector=False))
        _sec(s, "DESCRIPCION", [p("Comprende el suministro e instalacion de la tuberia PVC para desague de 4\" de la red de recoleccion de piso, que une cada sumidero con la cuneta mas cercana, "
                                  "con pendiente de 1 % (minimo 0.5 %), llegando sobre la cota de fondo de la cuneta (Norma CE.040).")])
        return s
    s = E.espec(pt, Pd, dict(colector=False))
    # ---------------------------------------------------------------- ajustes a los textos comunes con los datos de este proyecto
    if "LIMPIEZA" in d:
        _med(s, "Se medira el area limpiada en proyeccion horizontal: longitud de cada eje por el ancho de la franja de trabajo (ancho total de la cuneta mas %.2f m a cada lado), "
                "segun la PLANILLA GENERAL DE METRADOS." % SOBREANCHO)
    elif "TRAZO" in d:
        _sec(s, "DESCRIPCION", [p("Comprende el replanteo en el terreno de los ejes de cuneta (%.2f m en total), los quiebres a 45 grados en planta (chaflanes de %.2f m), los empalmes, "
                                  "las tapas de inspeccion y %s, y el control de los niveles del borde de la cuneta (%s) y de la cota de fondo de cada seccion, segun la planta %s, "
                                  "los perfiles y el cuadro de ejes." % (D.L, P["chaflan"], D.descargas_txt(), D.niveles_txt(), D.planta))])
        _sec(s, "PROCEDIMIENTO DE EJECUCION", [l("Ubicar y monumentar los BM y puntos de control fuera de la zona de excavacion.",
                                                 "Marcar los ejes con las coordenadas de la planta %s, con estacas cada 5.00 m en recta y en cada quiebre, empalme, tapa de inspeccion y descarga." % D.planta,
                                                 "Colocar niveletas con la cota de fondo de cada seccion segun los perfiles longitudinales; la pendiente de la cota de fondo no sera menor de %.2f %%." % (100 * P["S0"]),
                                                 "El trazo sera aprobado por la Supervision y anotado en el cuaderno de obra antes de iniciar la excavacion.")])
        _sec(s, "CONTROL DE CALIDAD Y TOLERANCIAS", [l("Tolerancias: 0.02 m en alineamiento y 0.01 m en las cotas de fondo; la cota de fondo baja en todo el recorrido hacia la descarga, sin contrapendientes ni depresiones.")])
        _med(s, "Se medira el area replanteada en proyeccion horizontal: longitud de cada eje por el ancho de la franja de trabajo, segun el metrado.")
    elif "EXCAVA" in d and "DADO" not in d:
        _sec(s, "DESCRIPCION", [p("Comprende la excavacion manual de las zanjas para las cunetas de concreto (ancho %s; muros y losa de fondo de %.2f m), con un ancho de zanja igual "
                                  "al ancho total mas %.2f m a cada lado, desde el nivel del terreno hasta %.2f m bajo la cota de fondo (losa de fondo y solado), con la profundidad "
                                  "variable de cada eje segun su perfil (%.2f m al inicio; hasta %.2f m)." % (D.anchos_txt(), P["e_muro"], SOBREANCHO, hfs, P["h0"], D.hmax)),
                                p("Incluye el perfilado de las paredes y el acarreo del material excavado a la zona de acopio dentro de la obra.")])
        _med(s, "Se medira el volumen excavado en su posicion original (sin esponjamiento): longitud de cada eje por el ancho de zanja por la profundidad promedio del perfil "
                "mas %.2f m (losa de fondo y solado), segun la PLANILLA GENERAL DE METRADOS." % hfs)
    elif "REFINE" in d:
        _med(s, "Se medira el area del fondo refinado y compactado: longitud de cada eje por el ancho total de la cuneta.")
    elif "RELLENO" in d:
        _med(s, "Se medira el volumen compactado: longitud de cada eje por el ancho de relleno a los lados de la cuneta (%.2f m a cada lado) por la profundidad promedio mas %.2f m, segun el metrado."
             % (SOBREANCHO, hfs))
    elif "ELIMINACI" in d:
        _med(s, "Se medira el volumen excedente esponjado: (volumen excavado + dados - volumen de relleno) por el factor de esponjamiento de %.2f, segun el metrado." % ESPONJ)
    elif "SOLADO" in d:
        _med(s, "Se medira el area de solado ejecutado: longitud de cada eje por el ancho total de la cuneta.")
    elif "CONCRETO" in d and "CUNETA" in d:
        _sec(s, "DESCRIPCION", [p("Comprende la preparacion, transporte, colocacion, compactacion y acabado del concreto f'c = 175 kg/cm² de las cunetas en U de %s, muros de %.2f m y losa "
                                  "de fondo de %.2f m, con la profundidad variable de cada eje segun su perfil (%.2f m a %.2f m), y de la losa tapa de %.2f m de los tramos tapados (%.2f m), "
                                  "descontando los vanos de las tapas de inspeccion." % (D.anchos_txt(), P["e_muro"], P["e_fondo"], P["h0"], D.hmax, P["e_tapa"], D.Lt)),
                                p("Donde la profundidad es menor de %.2f m (de la rejilla al fondo) y el tramo es abierto, la cuneta es de concreto simple; en el resto lleva el acero de la partida correspondiente." % P["h_acero"])])
        proc = [x for x in next(z for z in s if z[0] == "PROCEDIMIENTO DE EJECUCION")[1][0][1] if "detalle 1" not in x and "pendiente longitudinal" not in x]
        proc[-2:-2] = ["El borde superior de la cuneta queda %s; en los tramos abiertos se deja en el borde interior de los muros el rebaje de %.2f m para asentar el marco de la rejilla." % (D.niveles_txt(), K["rej_reb"]),
                       "En los tramos tapados los muros se rebajan para recibir la losa tapa, que queda al nivel del piso, y se dejan los vanos de las tapas de inspeccion.",
                       "Los quiebres a 45 grados y los empalmes se vacian con la forma de la planta, sin aristas que obstruyan el flujo; el fondo se acaba liso con la pendiente de la cota de fondo (minimo %.2f %%) hacia la descarga." % (100 * P["S0"])]
        _sec(s, "PROCEDIMIENTO DE EJECUCION", [l(*proc)])
        _med(s, "Se medira el volumen de concreto colocado: muros (area de muro del perfil por su espesor, dos muros), losa de fondo y losa tapa, descontando las tapas de inspeccion, segun la hoja CONCRETO EN CUNETAS.")
    elif "ENCOFRADO" in d and "CUNETA" in d:
        _sec(s, "DESCRIPCION", [p("Comprende el suministro, habilitacion, colocacion y retiro del encofrado de las caras interiores y exteriores de los muros de las cunetas, con la forma de los quiebres "
                                  "a 45 grados, y del fondo y los cantos de la losa tapa en los tramos tapados.")])
        _med(s, "Se medira el area de contacto entre el encofrado y el concreto: caras interiores y exteriores de los dos muros (longitud por altura del perfil; la exterior con la losa de fondo) "
                "y fondo y cantos de la losa tapa, segun la hoja ENCOFRADO Y DESENCOFRADO.")
    elif "ACERO" in d and "CUNETA" in d:
        _sec(s, "DESCRIPCION", [p("Comprende el suministro, corte, doblado, colocacion y amarre del acero de refuerzo corrugado grado 60 (fy = 4200 kg/cm²) de las cunetas donde la profundidad "
                                  "es de %.2f m o mas (de la rejilla al fondo) y en todos los tramos tapados: U de %s, barras longitudinales de %s y, en la losa tapa, barras de 3/8\" @0.20 m "
                                  "transversales y 3 barras longitudinales. Con profundidad menor de %.2f m en tramo abierto la cuneta es de concreto simple." % (P["h_acero"], K["acero_tr"], K["acero_long"], P["h_acero"])),
                                p("Recubrimiento libre: %.2f m." % REC)])
        _med(s, "Se medira el peso del acero colocado: longitud de cada barra (U, longitudinales y losa tapa) por el peso nominal de 3/8\" (%.2f kg/m), sin desperdicios ni alambre, segun la hoja METRADO ACERO." % KG38)
    elif "CURADO" in d:
        _med(s, "Se medira el area de concreto curada: caras interiores de los dos muros, fondo interior, coronas de muro en los tramos con rejilla y cara superior de la losa tapa, segun la hoja METRADO DE CURADO.")
    elif "REJILLA" in d:
        _sec(s, "DESCRIPCION", [p("Comprende la fabricacion y colocacion de la rejilla metalica movil de los tramos abiertos de las cunetas: platinas de 1\" x 3/16\" colocadas de canto, transversales "
                                  "al eje de la cuneta, soldadas por sus extremos a dos angulos L 1\" x 1\" x 3/16\" que forman el marco, en modulos removibles que se apoyan en el rebaje de %.2f m "
                                  "del borde interior de cada muro, al ras del piso terminado (planta %s y secciones %s)." % (K["rej_reb"], D.planta, D.cortes)),
                                p("El ancho del modulo es el ancho libre de la cuneta de cada eje (%s m) mas el apoyo en el rebaje de cada borde; en los quiebres a 45 grados los modulos se cortan a la forma de la planta." % " o ".join(_m(b) for b in D.bs))])
        _sec(s, "PROCEDIMIENTO DE EJECUCION", [l("Cortar los angulos y platinas a la medida de cada modulo y presentar las platinas sobre una plantilla con su separacion.",
                                                 "Soldar cada platina por ambos extremos a los angulos del marco, verificando escuadra y planitud; las platinas quedan de canto.",
                                                 "Esmerilar las soldaduras, limpiar con escobilla y aplicar dos manos de pintura anticorrosiva y dos de esmalte.",
                                                 "Colocar los modulos en el rebaje de la cuneta, apoyados en todo su perimetro, al ras del piso terminado y sin cojear.")])
        _med(s, "Se medira la longitud de rejilla colocada a lo largo del eje de la cuneta, solo en los tramos abiertos (longitud del eje menos los tramos tapados), segun la hoja METRADO DE REJILLAS.")
    elif "TAPA DE INSPECCION" in d:
        _sec(s, "DESCRIPCION", [p("Comprende la fabricacion y colocacion de las tapas de inspeccion removibles de concreto armado de %.2f x %.2f x %.2f m sobre los tramos tapados de las cunetas, "
                                  "con %s, ubicadas al inicio y al final de cada tramo tapado, en cada empalme y a %.0f m como maximo entre tapas (planta %s)." % (
                                      K["tapa"] + (K["tapa_acero"], P["tapa_sep_max"], D.planta)))])
        _sec(s, "MATERIALES", [l("Concreto f'c = 175 kg/cm²; acero corrugado de 3/8\" fy = 4200 kg/cm²; acero liso de 3/8\" para asas; madera para el molde.")])
        _med(s, "Se contara el numero de tapas fabricadas y colocadas, segun la hoja PLANILLA TAPAS INSPECCION.")
    elif "JUNTA" in d and "DILAT" in d:
        des = s[0][1][0][1].replace(", segun las laminas DJ-01 y DJ-02", "")
        _sec(s, "DESCRIPCION", [p(des)])
        _med(s, "Se medira en metros lineales de junta sellada: por cada junta, el perimetro exterior de la seccion en U (2 x (altura promedio del eje + %.2f m) + ancho total), "
                "por el numero de juntas de cada eje (una cada %.2f m), segun la hoja METRADO JUNTA DE DILATACION." % (P["e_fondo"], JUNTA_CADA))
    elif "FALSA COLUMNA" in d and und == "und":
        _med(s, "Se contara una falsa columna por montante, segun la hoja METRADO MONTANTES; su concreto, encofrado y acero se pagan en las subpartidas siguientes.")
    elif d.startswith("CANALETA"):
        _sec(s, "DESCRIPCION", [p("Comprende la fabricacion y colocacion de las canaletas de plancha de acero galvanizado de 0.9 mm de seccion 0.25 x 0.20 m en los aleros de los techos, con "
                                  "pendiente de 1 %% hacia las boquillas de las montantes de 4\": %.2f m en %d lados de techo, segun la planta %s y la hoja METRADO CANALETAS." % (
                                      D.TT["metrado"]["canaleta_m"], len(D.TT["lados"]), D.planta))])
    return s


def generalidades(D, proyecto, Pd):
    P = D.P
    cod = word.codigo_de(proyecto); nom = proyecto.get("nombre", "").strip("“”\"")
    cap = E.generalidades(Pd, [])
    cap = [c for c in cap if c[0] not in ("GENERALIDADES", "UBICACION")]
    comp = ["la red de cunetas de concreto dentro del cerco perimetrico, con rejilla metalica en los tramos abiertos y losa con tapas de inspeccion en los tramos tapados"]
    if D.LLt: comp.append("lloraderos en el muro de las cunetas en contacto con area verde")
    if D.TT["montantes"]: comp.append("canaletas y montantes de 4\" de los techos")
    if D.SM["sumideros"]: comp.append("sumideros de piso con tuberia PVC de 4\" a la cuneta")
    cap.insert(0, ["GENERALIDADES", [
        p("Las presentes especificaciones tecnicas definen la calidad de los materiales, los procedimientos de ejecucion, los controles, la seguridad, la unidad de medida, "
          "el metodo de medicion y la forma de pago de cada partida de la especialidad de drenaje pluvial del proyecto %s%s." % (nom, (", con " + cod) if cod else "")),
        p("Comprenden %s, que conducen por gravedad las aguas de lluvia de techos, pisos y areas verdes hasta %s por pases en el cimiento del cerco." % (
            ", ".join(comp[:-1]) + (" y " if len(comp) > 1 else "") + comp[-1], D.descargas_txt())),
        p("Su numeracion, la descripcion y la unidad de cada partida son las del metrado de la especialidad (hoja RESUMEN). Los planos %s, la memoria descriptiva, la memoria "
          "hidrologica y el metrado forman parte de este documento." % D.planos)]])
    ub = [p(("Entidad: %s. " % proyecto["entidad"] if proyecto.get("entidad") else "") + ("Ubicacion: %s." % proyecto["ubicacion"] if proyecto.get("ubicacion") else "")
            )] if (proyecto.get("entidad") or proyecto.get("ubicacion")) else []
    ub.append(p("El vaciado de concreto y el curado se programaran considerando la temperatura ambiente y las lluvias (ACI 305R); las zanjas abiertas se protegeran de la lluvia."))
    cap.insert(1, ["UBICACION", ub])
    filas = [["Seccion", "Rectangular en U: %s, muros de %.2f m, losa de fondo de %.2f m sobre solado de %.2f m" % (D.anchos_txt(), P["e_muro"], P["e_fondo"], P["e_solado"]), "Secciones %s" % D.cortes],
             ["Profundidad", "Variable: %.2f m al inicio de cada eje y hasta %.2f m" % (P["h0"], D.hmax), "Perfiles longitudinales"],
             ["Pendiente de la cota de fondo", "Minimo %.2f %%, sin contrapendientes" % (100 * P["S0"]), "Perfiles longitudinales"],
             ["Borde de la cuneta", D.niveles_txt()[0].upper() + D.niveles_txt()[1:], "Planta %s" % D.planta],
             ["Longitud total", "%.2f m en %d ejes (%.2f m tapados con losa y tapas de inspeccion)" % (D.L, len(D.q), D.Lt), "Metrado"],
             ["Acero", "Solo con profundidad de %.2f m o mas o en tramo tapado: U de 3/8\" @%.2f m, longitudinales de 3/8\" @%.2f m" % (P["h_acero"], SEP_T, SEP_L), "Secciones %s" % D.cortes],
             ["Juntas", "De dilatacion cada %.2f m en toda la seccion en U; junta con el piso adyacente" % JUNTA_CADA, "Secciones %s" % D.cortes],
             ["Descargas", "%s por pase en el cimiento del cerco, sin obras fuera del cerco" % (", ".join(D.D) or "-"), "Perfiles de descarga"]]
    if D.LLt: filas.append(["Lloraderos", "PVC 3\" @%.2f m con caja filtrante de 0.30 x 0.30 m de grava y geotextil, solo en el muro en contacto con area verde" % P["llor_sep"], "Planta %s" % D.planta])
    if D.TT["montantes"]: filas.append(["Montantes", "PVC 4\" en las esquinas de las edificaciones, en falsa columna de 0.20 x 0.15 m", "Planta %s" % D.planta])
    cap.insert(2, ["DATOS DE LA RED DE CUNETAS", [t(["ELEMENTO", "VALOR", "FUENTE"], filas)]])
    out = []
    techo = bool(D.TT["montantes"]); piso = bool(D.SM["sumideros"])
    for nom_, cont in cap:
        cont = copy.deepcopy(cont)
        for b in cont:
            if b[0] == "l":
                b[1] = [x.replace("Norma OS.060 Drenaje Pluvial Urbano; Norma CE.040 Drenaje Pluvial", "Norma CE.040 Drenaje Pluvial (R.M. N.° 126-2021-VIVIENDA)")
                        .replace("ganchos de cierre de los marcos de 0.15 m a cada lado (0.30 m por marco)", "ganchos de 0.10 m en los extremos de las U de las cunetas")
                        .replace("costados de muros, cunetas y falsas columnas a las 24 horas como minimo; fondos de losas (losa superior del colector y tapas) a los 7 dias",
                                 "costados de los muros de las cunetas y falsas columnas a las 24 horas como minimo; fondo de la losa tapa y tapas de inspeccion a los 7 dias")
                        for x in b[1]]
                if not techo:
                    b[1] = [x.replace("los trabajos en altura (canaletas y montantes) se haran con andamios certificados y arnes de cuerpo entero con linea de vida",
                                      "la zona de trabajo se aislara del publico con cerco provisional").replace("trabajos en altura, en caliente", "trabajos en caliente") for x in b[1]]
                if nom_ == "NORMAS APLICABLES":
                    b[1] += ["Especificaciones Tecnicas Generales para Construccion EG-2013 del MTC, Seccion 510 (cunetas revestidas de concreto)."]
            elif b[0] == "t":
                quita = [] if (techo or piso) else ["Tuberia", "Plancha galvanizada", "Prueba hidraulica"]
                if not techo: quita.append("Plancha galvanizada")
                b[2] = [f for f in b[2] if not any(k in f[0] for k in quita)]
            elif b[0] == "p" and nom_ == "CONCRETO" and b[1].startswith("Calidades"):
                b[1] = ("Calidades: f'c = 100 kg/cm² (solado), %s175 kg/cm² (cunetas, losa tapa de los tramos tapados, tapas de inspeccion%s). La resistencia corresponde a 28 dias." % (
                    "140 kg/cm² (dados de montante) y " if techo else "", " y falsas columnas" if techo else ""))
        out.append([nom_, cont])
    return out


LIMPIA = [("las cunetas, dados y obras de la red de drenaje pluvial del predio", "las cunetas de la red de drenaje pluvial"),
          ("; en el colector, despues de la prueba de la losa superior", ""), (" o el colector", ""), (" y del colector", ""),
          ("Dejar las ventanas y pases indicados en los planos (ventanas de llegada de cunetas, pases de tuberia, bordes de registros).",
           "Dejar los pases de las descargas en el cimiento del cerco, los niples de los lloraderos y los vanos de las tapas de inspeccion indicados en los planos.")]


def _limpia(x):
    if isinstance(x, str):
        for a, b in LIMPIA: x = x.replace(a, b)
        return x
    if isinstance(x, list): return [_limpia(v) for v in x]
    return x


def construir(ruta, partidas, P, cfg, q, V, laminas, TT, SM, LLt):
    proyecto = cfg.get("proyecto", {})
    D = Datos(P, cfg, q, V, laminas, TT, SM, LLt)
    Pd = dict(clave="drenie", corto=proyecto.get("nombre_corto", ""), cui="", proyecto=proyecto.get("nombre", ""), junta_cuneta_seccion=True,
              lamina_rejilla=None, colector=dict(nombre="red de cunetas", receptor="el terreno exterior por pases en el cimiento del cerco",
                                                 sello="asfaltico", cajas=None, cerco=False, vereda=False))
    nl = sum(x["n"] for x in LLt)
    if nl:
        Pd["desagregado_llor"] = [["Tuberia PVC-U de 3\"", "m", "0.30", str(nl), "%.2f" % (0.30 * nl)],
                                  ["Grava de 3/4\" a 1 1/2\"", "m³", "0.027", str(nl), "%.2f" % (0.027 * nl)],
                                  ["Geotextil no tejido", "m²", "0.60", str(nl), "%.2f" % (0.60 * nl)]]
    old = E.CUNETA; E.CUNETA = cuneta(D)
    try:
        J = dict(generalidades=generalidades(D, proyecto, Pd), partidas=[])
        base = min(len(x["codigo"].split(".")) for x in partidas)
        for x in partidas:
            it = dict(codigo=x["codigo"], desc=x["desc"], und=x["und"], nivel=len(x["codigo"].split(".")) - base)
            if x["und"]: it["secciones"] = ficha(x, D, Pd)
            J["partidas"].append(it)
    finally:
        E.CUNETA = old
    J["generalidades"] = E._acentuar(_limpia(J["generalidades"]))
    for it in J["partidas"]:
        if "secciones" in it: it["secciones"] = E._acentuar(_limpia(it["secciones"]))
    return word.especificaciones(J, ruta, proyecto)
