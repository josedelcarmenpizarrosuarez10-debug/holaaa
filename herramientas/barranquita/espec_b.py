"""Especificaciones tecnicas de drenaje pluvial (red de cunetas) de la I.E. N.° 0590 Barranquita (C.I. 468901).

Mismo formato y motor de las especificaciones de los CAR (herramientas/especificaciones: espec.py -> JSON -> docx_espec.js):
portada, indice, capitulo I de generalidades y capitulo II con una ficha por partida (descripcion, materiales, equipos,
procedimiento, control de calidad, seguridad, unidad, metodo de medicion y forma de pago).
Las partidas (codigo, descripcion, unidad) son las del metrado (metrado_b.py), en el mismo orden; no se agregan ni se quitan.
Los textos comunes vienen de espec.py; lo propio de este proyecto (seccion de la cuneta, acero solo con h >= 0.40 m o tapado,
rejilla, tapas de inspeccion, descargas por el cerco, juntas) se escribe aqui con los datos de los planos DC-01 a DC-19.
Salida: entregables_barranquita/ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx
"""
import os, sys, json, copy, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
ESP = os.path.join(RAIZ, "herramientas", "especificaciones")
sys.path.insert(0, AQUI); sys.path.insert(0, ESP)
import cantidades_b as Q, metrado_b as MB
import espec as E
from espec import p, l, t, bloque, EPP

SAL = os.path.join(RAIZ, "entregables_barranquita", "ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx")
JSON = os.path.join(ESP, "_json", "barranquita.json")
PLANOS = "DC-01 a DC-19"
PROYECTO = ("MEJORAMIENTO Y AMPLIACIÓN DEL SERVICIO DE EDUCACIÓN PRIMARIA EN I.E. N° 0590 DISTRITO DE BARRANQUITA DE LA PROVINCIA DE "
            "LAMAS DEL DEPARTAMENTO DE SAN MARTÍN")

# datos de la cuneta de este proyecto (planos DC-02 y hoja PARAMETROS del metrado)
K = dict(E.CUNETA, b=Q.B, em=Q.E, ef=Q.EF, et=Q.ET, be=Q.BT, acero_long="3/8\" @%.2f m en muros y losa de fondo" % Q.SEP_L,
         acero_tr="3/8\" en U @%.2f m con ganchos de 0.10 m" % Q.SEP_T, junta=Q.JUNTA_CADA, tapa=Q.TAPA,
         tapa_acero="parrilla simple de 3/8\" @0.15 m en ambos sentidos y dos asas de fierro liso de 3/8\"", S=0.50, rej_reb=0.05)
P = dict(clave="barranquita", corto="I.E. N° 0590 BARRANQUITA", cui="468901", proyecto=PROYECTO, junta_cuneta_seccion=True, lamina_rejilla=None,
         colector=dict(nombre="red de cunetas", receptor="el terreno exterior por pases en el cimiento del cerco (descargas D1 a D4)", sello="asfaltico",
                       cajas=None, cerco=False, vereda=False))


def _sec(secciones, nombre, contenido):
    """Reemplaza (o agrega antes de la unidad de medida) un apartado de la ficha de una partida."""
    for s in secciones:
        if s[0] == nombre:
            s[1] = contenido; return secciones
    i = next(k for k, s in enumerate(secciones) if s[0] == "UNIDAD DE MEDIDA")
    secciones.insert(i, [nombre, contenido]); return secciones


def _med(secciones, texto): return _sec(secciones, "METODO DE MEDICION", [p(texto)])


def ficha(pt, q):
    d = pt["desc"].upper(); und = pt["und"]
    L = sum(x["L"] for x in q); Lt = sum(x["L_tapado"] for x in q); hmax = max(x["h_max"] for x in q)
    # ---------------------------------------------------------------- partidas propias de este proyecto
    if "PERFILADO" in d:
        return bloque([p("Comprende el perfilado manual del terreno natural al pie del cerco, frente a cada descarga (D1 a D4), para que el agua que sale por el pase "
                         "en el cimiento del cerco escurra libre sobre el terreno exterior, sin empozarse. No se construyen obras fuera del cerco.")],
                      equ=l("Pico, lampa, rastrillo, carretilla, nivel y wincha."),
                      proc=l("Ubicar cada descarga segun la planta DC-01 y las laminas DC-16 a DC-19.",
                             "Recortar el terreno en un ancho de %.2f m y en la longitud indicada en cada lamina, hasta quedar por debajo de la cota de fondo de la descarga, con pendiente hacia afuera." % Q.BT,
                             "En la descarga D2, donde el terreno exterior baja en talud, coordinar con el propietario del terreno exterior la proteccion de la entrega contra la erosion."),
                      ctrl=l("Se verificara con agua que el escurrimiento salga libre frente al pase del cerco, sin empozamiento."),
                      seg=l(EPP, "Senalizar la zona de trabajo junto al cerco."), und=und,
                      medicion=[p("Se medira el area perfilada: ancho de %.2f m por la longitud de perfilado de cada descarga, segun el metrado." % Q.BT)])
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
    s = E.espec(pt, P, dict(colector=False))
    # ---------------------------------------------------------------- ajustes a los textos comunes con los datos de este proyecto
    if "LIMPIEZA" in d:
        _med(s, "Se medira el area limpiada en proyeccion horizontal: longitud de cada eje por el ancho de la franja de trabajo (%.2f m: cuneta de %.2f m mas %.2f m a cada lado), "
                "segun la PLANILLA GENERAL DE METRADOS." % (Q.B_EXC, Q.BT, Q.SOBREANCHO))
    elif "TRAZO" in d:
        _sec(s, "DESCRIPCION", [p("Comprende el replanteo en el terreno de los ejes de cuneta (%.2f m en total), los quiebres a 45 grados en planta (chaflanes de 0.60 m), los empalmes, "
                                  "las tapas de inspeccion y las descargas D1 a D4, y el control de los niveles del borde de la cuneta (+184.65 al ras del piso terminado; +184.50 junto "
                                  "al patio de maniobra) y de la cota de fondo de cada seccion, segun la planta DC-01, los perfiles y el cuadro de tramos." % L)])
        _sec(s, "PROCEDIMIENTO DE EJECUCION", [l("Ubicar y monumentar los BM y puntos de control fuera de la zona de excavacion.",
                                                 "Marcar los ejes con las coordenadas de la planta DC-01, con estacas cada 5.00 m en recta y en cada quiebre, empalme, tapa de inspeccion y descarga.",
                                                 "Colocar niveletas con la cota de fondo de cada seccion segun los perfiles longitudinales; la pendiente de la cota de fondo no sera menor de 0.50 %.",
                                                 "El trazo sera aprobado por la Supervision y anotado en el cuaderno de obra antes de iniciar la excavacion.")])
        _sec(s, "CONTROL DE CALIDAD Y TOLERANCIAS", [l("Tolerancias: 0.02 m en alineamiento y 0.01 m en las cotas de fondo; la cota de fondo baja en todo el recorrido hacia la descarga, sin contrapendientes ni depresiones.")])
        _med(s, "Se medira el area replanteada en proyeccion horizontal: longitud de cada eje por el ancho de la franja de trabajo (%.2f m), segun el metrado." % Q.B_EXC)
    elif "EXCAVA" in d:
        _sec(s, "DESCRIPCION", [p("Comprende la excavacion manual de las zanjas para las cunetas de concreto (ancho interior %.2f m, muros y losa de fondo de %.2f m, ancho exterior %.2f m), "
                                  "con un ancho de zanja de %.2f m, desde el nivel del terreno hasta %.2f m bajo la cota de fondo (losa de fondo y solado), con la profundidad variable de "
                                  "cada eje segun su perfil (0.30 m al inicio; hasta %.2f m)." % (K["b"], K["em"], K["be"], Q.B_EXC, Q.EF + Q.SOLADO, hmax)),
                                p("Incluye el perfilado de las paredes y el acarreo del material excavado a la zona de acopio dentro de la obra.")])
        _med(s, "Se medira el volumen excavado en su posicion original (sin esponjamiento): longitud de cada eje por el ancho de zanja (%.2f m) por la profundidad promedio del perfil "
                "mas %.2f m (losa de fondo y solado), segun la PLANILLA GENERAL DE METRADOS." % (Q.B_EXC, Q.EF + Q.SOLADO))
    elif "REFINE" in d:
        _med(s, "Se medira el area del fondo refinado y compactado: longitud de cada eje por el ancho exterior de la cuneta (%.2f m)." % Q.BT)
    elif "RELLENO" in d:
        _med(s, "Se medira el volumen compactado: longitud de cada eje por el ancho de relleno a los lados de la cuneta (%.2f - %.2f m) por la profundidad promedio mas %.2f m, segun el metrado."
             % (Q.B_EXC, Q.BT, Q.EF + Q.SOLADO))
    elif "ELIMINACI" in d:
        _med(s, "Se medira el volumen excedente esponjado: (volumen excavado - volumen de relleno) por el factor de esponjamiento de %.2f, segun el metrado." % Q.ESPONJ)
    elif "SOLADO" in d:
        _med(s, "Se medira el area de solado ejecutado: longitud de cada eje por el ancho exterior de la cuneta (%.2f m)." % Q.BT)
    elif "CONCRETO" in d and "CUNETA" in d:
        _sec(s, "DESCRIPCION", [p("Comprende la preparacion, transporte, colocacion, compactacion y acabado del concreto f'c = 175 kg/cm² de las cunetas en U de %.2f m de ancho total "
                                  "(muros de %.2f m y %.2f m libres) y losa de fondo de %.2f m, con la profundidad variable de cada eje segun su perfil (0.30 m a %.2f m), y de la losa tapa "
                                  "de %.2f m de los tramos tapados (%.2f m), descontando los vanos de las tapas de inspeccion." % (K["be"], K["em"], K["b"], K["ef"], hmax, K["et"], Lt)),
                                p("Donde la profundidad es menor de 0.40 m (de la rejilla al fondo) y el tramo es abierto, la cuneta es de concreto simple; en el resto lleva el acero de la partida correspondiente.")])
        proc = [x for x in next(z for z in s if z[0] == "PROCEDIMIENTO DE EJECUCION")[1][0][1]
                if "detalle 1" not in x and "pendiente longitudinal" not in x]
        proc[-2:-2] = ["El borde superior de la cuneta queda al ras del piso terminado (+184.65; +184.50 junto al patio de maniobra); en los tramos abiertos se deja en el borde interior de los muros el rebaje de %.2f m para asentar el marco de la rejilla." % K["rej_reb"],
                       "En los tramos tapados los muros se rebajan para recibir la losa tapa, que queda al nivel de la vereda, y se dejan los vanos de las tapas de inspeccion.",
                       "Los quiebres a 45 grados y los empalmes se vacian con la forma de la planta, sin aristas que obstruyan el flujo; el fondo se acaba liso con la pendiente de la cota de fondo (minimo 0.50 %) hacia la descarga."]
        _sec(s, "PROCEDIMIENTO DE EJECUCION", [l(*proc)])
        _med(s, "Se medira el volumen de concreto colocado: muros (area de muro del perfil por su espesor, dos muros), losa de fondo y losa tapa, descontando las tapas de inspeccion, segun la hoja CONCRETO EN CUNETAS.")
    elif "ENCOFRADO" in d:
        _sec(s, "DESCRIPCION", [p("Comprende el suministro, habilitacion, colocacion y retiro del encofrado de las caras interiores y exteriores de los muros de las cunetas, con la forma de los quiebres "
                                  "a 45 grados, y del fondo y los cantos de la losa tapa en los tramos tapados.")])
        _med(s, "Se medira el area de contacto entre el encofrado y el concreto: caras interiores y exteriores de los dos muros (longitud por altura del perfil; la exterior con la losa de fondo) "
                "y fondo y cantos de la losa tapa, segun la hoja ENCOFRADO Y DESENCOFRADO.")
    elif "ACERO" in d:
        _sec(s, "DESCRIPCION", [p("Comprende el suministro, corte, doblado, colocacion y amarre del acero de refuerzo corrugado grado 60 (fy = 4200 kg/cm²) de las cunetas donde la profundidad "
                                  "es de 0.40 m o mas (de la rejilla al fondo) y en todos los tramos tapados: U de %s, barras longitudinales de %s y, en la losa tapa, barras de 3/8\" @0.20 m "
                                  "transversales y 3 barras longitudinales. Con profundidad menor de 0.40 m en tramo abierto la cuneta es de concreto simple." % (K["acero_tr"], K["acero_long"])),
                                p("Recubrimiento libre: %.2f m." % Q.REC)])
        _med(s, "Se medira el peso del acero colocado: longitud de cada barra (U, longitudinales y losa tapa) por el peso nominal de 3/8\" (%.2f kg/m), sin desperdicios ni alambre, segun la hoja METRADO ACERO." % Q.KG38)
    elif "CURADO" in d:
        _med(s, "Se medira el area de concreto curada: caras interiores de los dos muros, fondo interior, coronas de muro en los tramos con rejilla y cara superior de la losa tapa, segun la hoja METRADO DE CURADO.")
    elif "REJILLA" in d:
        _sec(s, "DESCRIPCION", [p("Comprende la fabricacion y colocacion de la rejilla metalica movil de los tramos abiertos de las cunetas: platinas de 1\" x 3/16\" colocadas de canto, transversales "
                                  "al eje de la cuneta, soldadas por sus extremos a dos angulos L 1\" x 1\" x 3/16\" que forman el marco, en modulos removibles que se apoyan en el rebaje de %.2f m "
                                  "del borde interior de cada muro, al ras del piso terminado (planta DC-01 y seccion tipica DC-02)." % K["rej_reb"]),
                                p("El ancho del modulo es el ancho libre de la cuneta (%.2f m) mas el apoyo en el rebaje de cada borde; en los quiebres a 45 grados los modulos se cortan a la forma de la planta." % K["b"])])
        _sec(s, "PROCEDIMIENTO DE EJECUCION", [l("Cortar los angulos y platinas a la medida de cada modulo y presentar las platinas sobre una plantilla con su separacion.",
                                                 "Soldar cada platina por ambos extremos a los angulos del marco, verificando escuadra y planitud; las platinas quedan de canto.",
                                                 "Esmerilar las soldaduras, limpiar con escobilla y aplicar dos manos de pintura anticorrosiva y dos de esmalte.",
                                                 "Colocar los modulos en el rebaje de la cuneta, apoyados en todo su perimetro, al ras del piso terminado y sin cojear.")])
        _med(s, "Se medira la longitud de rejilla colocada a lo largo del eje de la cuneta, solo en los tramos abiertos (longitud del eje menos los tramos tapados), segun la hoja METRADO DE REJILLAS.")
    elif "TAPA DE INSPECCION" in d:
        _sec(s, "DESCRIPCION", [p("Comprende la fabricacion y colocacion de las tapas de inspeccion removibles de concreto armado de %.2f x %.2f x %.2f m sobre los tramos tapados de las cunetas, "
                                  "con %s, ubicadas al inicio y al final de cada tramo tapado, en cada empalme y a 10 m como maximo entre tapas (planta DC-01)." % (K["tapa"] + (K["tapa_acero"],)))])
        _sec(s, "MATERIALES", [l("Concreto f'c = 175 kg/cm²; acero corrugado de 3/8\" fy = 4200 kg/cm²; acero liso de 3/8\" para asas; madera para el molde.")])
        _med(s, "Se contara el numero de tapas fabricadas y colocadas, segun la hoja PLANILLA TAPAS INSPECCION.")
    elif "JUNTA" in d and "DILAT" in d:
        des = s[0][1][0][1].replace(", segun las laminas DJ-01 y DJ-02", "")
        _sec(s, "DESCRIPCION", [p(des)])
        _med(s, "Se medira en metros lineales de junta sellada: por cada junta, el perimetro exterior de la seccion en U (2 x (altura promedio del eje + %.2f m) + %.2f m), "
                "por el numero de juntas de cada eje (una cada %.2f m), segun la hoja METRADO JUNTA DE DILATACION." % (Q.EF, Q.BT, Q.JUNTA_CADA))
    return s


def generalidades(q):
    L = sum(x["L"] for x in q); Lt = sum(x["L_tapado"] for x in q); hmax = max(x["h_max"] for x in q)
    cap = E.generalidades(P, [])
    cap = [c for c in cap if c[0] not in ("GENERALIDADES", "UBICACION")]
    cap.insert(0, ["GENERALIDADES", [
        p("Las presentes especificaciones tecnicas definen la calidad de los materiales, los procedimientos de ejecucion, los controles, la seguridad, la unidad de medida, "
          "el metodo de medicion y la forma de pago de cada partida de la especialidad de drenaje pluvial (red de cunetas) del proyecto %s, con C.I. N.° %s." % (PROYECTO, P["cui"])),
        p("Comprenden la red de cunetas de concreto dentro del cerco perimétrico del local educativo, con rejilla metalica en los tramos abiertos y losa con tapas de inspeccion en "
          "los tramos tapados, que conduce por gravedad las aguas de lluvia de techos, veredas, patios, losa multiusos, patio de maniobra y areas verdes hasta cuatro descargas "
          "(D1 a D4) por pases en el cimiento del cerco."),
        p("Su numeracion, la descripcion y la unidad de cada partida son las del metrado de la especialidad (hoja RESUMEN). Los planos %s, la memoria descriptiva, la memoria "
          "hidrologica, la memoria de calculo y el metrado forman parte de este documento." % PLANOS)]])
    cap.insert(1, ["UBICACION", [p("Entidad: Gobierno Regional San Martin - Gerencia Territorial Bajo Mayo - Tarapoto. Ubicacion: localidad y distrito de Barranquita, provincia de Lamas, "
                                   "departamento de San Martin."),
                                 p("Clima calido y muy lluvioso de llanura amazónica: el vaciado de concreto y el curado se programaran considerando la temperatura ambiente y las lluvias (ACI 305R); "
                                   "las zanjas abiertas se protegerán de la lluvia.")]])
    cap.insert(2, ["DATOS DE LA RED DE CUNETAS", [
        t(["ELEMENTO", "VALOR", "FUENTE"], [
            ["Seccion", "Rectangular en U: ancho total %.2f m (muros de %.2f m y %.2f m libres), losa de fondo de %.2f m sobre solado de 4\"" % (K["be"], K["em"], K["b"], K["ef"]), "Plano DC-02"],
            ["Profundidad", "Variable: 0.30 m al inicio de cada eje y hasta %.2f m" % hmax, "Perfiles longitudinales"],
            ["Pendiente de la cota de fondo", "Minimo 0.50 %, sin contrapendientes", "Perfiles longitudinales"],
            ["Borde de la cuneta", "+184.65 al ras del piso terminado (area verde +184.60); +184.50 junto al patio de maniobra", "Plano DC-01"],
            ["Longitud total", "%.2f m en %d ejes (%.2f m tapados con losa y tapas de inspeccion)" % (L, len(q), Lt), "Metrado"],
            ["Acero", "Solo con profundidad de 0.40 m o mas o en tramo tapado: U de 3/8\" @0.25 m, longitudinales de 3/8\" @0.20 m", "Plano DC-02"],
            ["Juntas", "De dilatacion cada %.2f m en toda la seccion en U; junta con el piso adyacente" % Q.JUNTA_CADA, "Plano DC-02"],
            ["Descargas", "D1 a D4 por pase en el cimiento del cerco, sin obras fuera del cerco", "Planos DC-16 a DC-19"]])]])
    out = []
    for nom, cont in cap:
        cont = copy.deepcopy(cont)
        for b in cont:
            if b[0] == "l":
                b[1] = [x.replace("Norma OS.060 Drenaje Pluvial Urbano; Norma CE.040 Drenaje Pluvial", "Norma CE.040 Drenaje Pluvial (R.M. N.° 126-2021-VIVIENDA)")
                        .replace("ganchos de cierre de los marcos de 0.15 m a cada lado (0.30 m por marco)", "ganchos de 0.10 m en los extremos de las U de las cunetas")
                        .replace("costados de muros, cunetas y falsas columnas a las 24 horas como minimo; fondos de losas (losa superior del colector y tapas) a los 7 dias",
                                 "costados de los muros de las cunetas a las 24 horas como minimo; fondo de la losa tapa y tapas de inspeccion a los 7 dias")
                        .replace("los trabajos en altura (canaletas y montantes) se haran con andamios certificados y arnes de cuerpo entero con linea de vida",
                                 "en el local educativo en funcionamiento se aislara la zona de trabajo de los alumnos con cerco provisional")
                        .replace("trabajos en altura, en caliente", "trabajos en caliente")
                        for x in b[1]]
                if nom == "NORMAS APLICABLES":
                    b[1] += ["Especificaciones Tecnicas Generales para Construccion EG-2013 del MTC, Seccion 510 (cunetas revestidas de concreto).",
                             "R.V.M. N.° 208-2019-MINEDU, Norma Tecnica de criterios generales de diseno para infraestructura educativa."]
            elif b[0] == "t":
                b[2] = [f for f in b[2] if not any(k in f[0] for k in ("Tuberia", "Plancha galvanizada", "Prueba hidraulica"))]
            elif b[0] == "p" and nom == "CONCRETO" and b[1].startswith("Calidades"):
                b[1] = "Calidades: f'c = 100 kg/cm² (solado) y 175 kg/cm² (cunetas, losa tapa de los tramos tapados y tapas de inspeccion). La resistencia corresponde a 28 dias."
        out.append([nom, cont])
    return out


# frases de los textos comunes que no aplican a este proyecto (sin colector, montantes ni dados)
LIMPIA = [("las cunetas, dados y obras de la red de drenaje pluvial del predio", "las cunetas de la red de drenaje pluvial del local"),
          ("; en el colector, despues de la prueba de la losa superior", ""), (" o el colector", ""), (" y del colector", ""),
          ("Dejar las ventanas y pases indicados en los planos (ventanas de llegada de cunetas, pases de tuberia, bordes de registros).",
           "Dejar los pases de las descargas en el cimiento del cerco y los vanos de las tapas de inspeccion indicados en los planos.")]


def _limpia(x):
    if isinstance(x, str):
        for a, b in LIMPIA: x = x.replace(a, b)
        return x
    if isinstance(x, list): return [_limpia(v) for v in x]
    return x


def construir():
    resumen = MB.construir()                                        # mismas partidas del metrado
    q = Q.por_eje()
    pts = [dict(codigo=it, desc=d, und=u or "") for it, d, u, f in resumen]
    old = E.CUNETA; E.CUNETA = K                                    # textos comunes con la cuneta de este proyecto
    try:
        doc = dict(proyecto=PROYECTO, cui=P["cui"], codigo="C.I. N.° %s" % P["cui"], corto=P["corto"],
                   entidad="GOBIERNO REGIONAL SAN MARTIN - GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO", especialidad=E.ESPECIALIDAD,
                   ubicacion="SAN MARTIN - LAMAS - BARRANQUITA", fecha=MB.FECHA, generalidades=generalidades(q), partidas=[])
        base = min(len(x["codigo"].split(".")) for x in pts)
        for x in pts:
            it = dict(codigo=x["codigo"], desc=x["desc"], und=x["und"], nivel=len(x["codigo"].split(".")) - base)
            if x["und"]: it["secciones"] = ficha(x, q)
            doc["partidas"].append(it)
    finally:
        E.CUNETA = old
    doc["generalidades"] = E._acentuar(_limpia(doc["generalidades"]))
    for it in doc["partidas"]:
        if "secciones" in it: it["secciones"] = E._acentuar(_limpia(it["secciones"]))
    os.makedirs(os.path.dirname(JSON), exist_ok=True)
    json.dump(doc, open(JSON, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    subprocess.run(["node", os.path.join(ESP, "docx_espec.js"), JSON, SAL], check=True)


if __name__ == "__main__":
    construir()
