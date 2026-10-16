"""Adapta los modulos compartidos (planta, secciones, cuadros, detalles, metrado) al tramo CAR Varones.

Los modulos de Solange importan `diseno as dz` y copian `D = dz.D` al cargarse; aqui se reemplazan por
diseno_v y se fijan los textos/parametros propios de Varones. Importar este modulo ANTES de dibujar.
"""
import os, sys
os.environ.setdefault("CONTRAMARCO", "1.5x1.5x1/8")   # contramarco L 1 1/2"x1 1/2"x1/8", igual que el Hogar de Refugio
os.environ.setdefault("SELLO_JUNTA", "asfaltico")     # sellador asfaltico 1" x 2" (RC-250 + arena) en las juntas, igual que el Refugio
AQUI = os.path.dirname(os.path.abspath(__file__)); HERR = os.path.dirname(AQUI); RAIZ = os.path.dirname(HERR)
for p in (HERR, AQUI):
    if p not in sys.path: sys.path.insert(0, p)
import diseno_v as dz
import dxf_base as B
import dxf_planta as DP, dxf_secciones as DS, dxf_cuadros as DQ, dxf_detalles as DD, metrado_calc as MC

D = dz.D
P = lambda p: "0+%06.2f" % p

# ------------------------------------------------------------------ rotulo
B.PROYECTO = ("CREACION DEL SERVICIO DE PROTECCION INTEGRAL A NINAS, NINOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE PERDERLOS",
              "EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2705619")
B.UBICACION = "UBICACION: PREDIO ALDEA INFANTIL VIRGEN DEL PILAR - MORALES - SAN MARTIN - SAN MARTIN"

# ------------------------------------------------------------------ modulos de dibujo y metrado
for m in (DP, DS, DQ, DD, MC):
    m.dz = dz; m.D = D

# metrado: terreno de Varones, sin cajas propias (la CL es de Solange), registros todos en la losa del colector
MC.TERRENO_JSON = os.path.join(dz.CALC, "terreno.json")
MC.EXTRA_REG = 0
MC.BORDE_PERIM = 2 * D["b"] if D["b"] < 0.70 else 3.00   # b = 0.60 < abertura 0.70: borde engrosado solo en los 2 lados transversales, entre muros
MC.NOMBRE_TRAMO_FINAL = "tramo de empalme con la CL (horizontal)"
MC.cajas = lambda: {}
H_MAX = 1.17          # altura interior maxima (llegada a la CL) redondeada como en la planilla: perimetro de junta 4.64 m


def _juntas():
    n = int(dz.P_FIN // 4.0)
    hmax = H_MAX if H_MAX else dz.techo(dz.P_FIN) - dz.fondo(dz.P_FIN)
    per = 2 * (D["b"] + 2 * D["e_muro"]) + 2 * (D["e_fondo"] + hmax + D["e_losa"])
    # no hay cerco y a ambos lados del colector hay terreno natural: no lleva junta longitudinal; la unica junta con otra
    # estructura es el contacto del colector con el muro este de la caja CL (perimetro de la seccion)
    per_cl = 2 * (D["b"] + 2 * D["e_muro"]) + 2 * (D["e_fondo"] + hmax + D["e_losa"])
    return dict(n=n, L_dilat=n * per, L_tecnopor_cerco=0.0, L_tecnopor_cl=per_cl, L_tecnopor_piso=0.0)


MC.juntas = _juntas

# secciones y detalles tipicos
DS.SECCIONES = [(3.0, "S-01"), (10.0, "S-02"), (20.0, "S-03"), (46.0, "S-04"), (70.0, "S-05"), (90.0, "S-06"), (100.0, "S-07"), (103.5, "S-08")]
DS.TXT_REGISTROS = "11 und (RV-01 a RV-11), todos en la losa del colector"
DS.NOTA_EMPALMES = "* cuneta Eje 01: no entra al colector; cae directamente a la caja de llegada CL por una ventana en su muro norte (ver DP-07)."
DS.REG_SIN = "CL*"
DS.P_EJ_EMPALME = 46.02
DS.SUB_DP06C = "VENTANA EN EL MURO LADO PREDIO, CAIDA AL FONDO, JUNTAS Y REGISTRO - CUNETAS EJES 09, 08, 06 Y 04 - ESC. 1/10"
DS.TXT_CUNETA_06C = "cuneta de arquitectura 0.40 x H, muros 0.10 (NCF segun perfil CAR VARONES, Ejes 09, 08, 06 y 04)"
DS.TXT_CERCO_06C = "no hay cerco perimetrico: la cuneta llega directamente al muro del colector con junta de tecnopor 1\""
DS.TXT_JUNTA_06C = "junta de tecnopor 1\" entre el colector y la cuneta"
DS.CON_CERCO = False
DS.TXT_NPT_LEY = "losa superior = vereda +%.2f (terreno natural a ambos lados)"
DD.CON_CERCO = False
DD.TIT_DD03_C = "C. JUNTA DE TECNOPOR Y SELLADOR CON LA CAJA CL"
DD.MODO_DD03 = "caja_cl"
DD.EJ_DD04 = 46.02
DS.TXT_EJ_EMPALME = "ESC. 1/10 - ejemplo cuneta Eje 06 (0+046.02, registro RV-06); en las demas varia H y la cota de fondo"
_AC = {c["perfil"]: -c["ajuste_L"] for c in dz.CUNETAS}
DESC_TXT = ", ".join("%.2f" % _AC[k] for k in ("09", "08", "06", "04", "01"))
DS.TXT_Q_LEY = "Q = %.1f L/s en la llegada a la CL" % (dz.caudal_en(dz.P_FIN) * 1000)
DS.TXT_LEY_CUNETA_06C = "cuneta existente (arquitectura)"
DS.NOTA_PROLONG = ["NOTA: las cunetas de los Ejes 09, 08, 06 y 04 se acortan",
                   "%s m respecto del plano de arquitectura: terminan" % ", ".join("%.2f" % _AC[k] for k in ("09", "08", "06", "04")),
                   "en la cara del muro lado predio del colector; el tramo que caia dentro",
                   "del colector se descuenta en la partida de cunetas del proyecto."]
DS.NOTAS_DP04 = ["1. Altura interior h segun el perfil longitudinal: 0.70 m en el cruce de camiones (losa e=0.25), 0.85 m en 0+006.08 y 1.17 m en la llegada a la CL.",
                 "2. Tramo normal: un solo marco cerrado 3/8\" @0.20 en el eje de muros y losas (una capa, E.060 14.3.4); recubrimiento 0.04 m en muros y losa de fondo y 0.025 m en la losa superior.",
                 "3. No hay cerco perimetrico y a ambos lados del colector hay terreno natural: no lleva junta longitudinal. La losa superior (+261.15) sirve de vereda. Junta de tecnopor 1\" con sellador asfaltico solo en el contacto con la caja CL.",
                 "4. El cruce de camiones cisterna (S-01, 0+000.00 - 0+006.08) lleva losas e=0.25 y doble marco de 1/2\" @0.15 (marco exterior e interior, recubrimiento 0.04).",
                 "5. Los registros no se ubican dentro del cruce de camiones. No hay cruce de motos en este tramo."]

# cuadros DP-08 y DA-01 a DA-03
DQ.EJ_ZANJA = ((20.0, "ZANJA TIPICA - TRAMO NORMAL"), (3.0, "ZANJA - CRUCE DE CAMIONES"), (103.5, "ZANJA - TRAMO DE EMPALME CON LA CL"))
DQ.EJ_CONCRETO = ((20.0, "TRAMO NORMAL"), (3.0, "CRUCE DE CAMIONES"), (103.5, "TRAMO DE EMPALME (h max.)"))
DQ.EJ_ACERO = ((20.0, "TRAMO NORMAL 3/8\" @0.20"), (3.0, "CRUCE DE CAMIONES 1/2\" @0.15 DOBLE"), (103.5, "TRAMO DE EMPALME 3/8\" @0.20"))
DQ.ESPECIFICACIONES = [
    "CONCRETO ARMADO: f'c = 210 kg/cm2 (colector y tapas). Cemento tipo I; agregados limpios; slump 3\" a 4\".",
    "CONCRETO SIMPLE: solado f'c = 100 kg/cm2, e = 0.05 m.",
    "ACERO DE REFUERZO: fy = 4200 kg/cm2 (grado 60), corrugado. Ganchos de 0.30 m en los marcos.",
    "RECUBRIMIENTOS: 0.04 m en muros y losa de fondo; 0.025 m en losa superior del tramo normal; 0.04 m en el cruce de camiones; 0.025 m en tapas.",
    "TRASLAPES: 3/8\" = 0.40 m ; 1/2\" = 0.50 m, alternados. Barras longitudinales de 9.00 m.",
    "LOSA SUPERIOR: vaciada monoliticamente con los muros en todo el colector; acabado frotachado; sirve de vereda (+261.15).",
    "REGISTROS: tapa ciega de concreto armado 0.68 x 0.68 x 0.08 (parrilla 3/8\" @0.10 y 2 asas de fierro liso 1/2\"), vaciada aparte en obra, en rebaje 0.70 x 0.70 x 0.08 de la losa; sin marco ni contramarco metalico.",
    "JUNTAS: cada 4.00 m, e = 1\", relleno de poliestireno expandido y sellador asfaltico (RC-250 + arena) 1\" x 2\". A ambos lados del colector hay terreno natural: no lleva junta longitudinal. Tecnopor 1\" con sellador en el contacto con la caja CL y tecnopor 1\" en el contacto con las cunetas.",
    "CURADO: humedo minimo 7 dias; no transitar sobre la losa antes de 14 dias; no cargar con camiones antes de 28 dias.",
    "RELLENO: material propio seleccionado, capas de 0.15 m, 95 % del Proctor modificado; incluye la nivelacion del retiro hasta la cota de la losa.",
    "EXCAVACION: zanja de 1.40 m de ancho (0.25 m a cada lado del muro); entibar si el suelo lo requiere (profundidades de 1.10 a 1.75 m).",
    "EMPALME: el colector entrega a la caja de llegada CL del Hogar de Refugio Temporal (CUI 2675514) por la ventana 0.60 x 1.17 de su muro este; verificar la CL antes de vaciar el ultimo tramo.",
    "CUNETAS: las cunetas de arquitectura (Ejes 09, 08, 06 y 04) terminan en la cara del muro del colector; la del Eje 01 entra a la caja CL (ver DP-07)."]
DQ.TXT_CAJAS = ""
DQ.NOTAS_DP08 = ["1. Dimensiones en metros y cotas en m.s.n.m., salvo indicacion.",
                 "2. El colector conduce 221.7 L/s (cunetas Ejes 09, 08, 06 y 04); con la cuneta del Eje 01, que entra directamente a la CL, el CAR Varones entrega 258.7 L/s (TR 25 anos), igual a lo considerado en el expediente del Hogar de Refugio.",
                 "3. Verificaciones hidraulica y estructural segun memoria de calculo del proyecto (RNE CE.040, E.020, E.060; AASHTO LRFD HL-93 en el cruce de camiones).",
                 "4. Las cunetas de arquitectura (Ejes 01 a 09) y sus cotas de fondo son datos del plano PERFIL CAR VARONES; las de los Ejes 09, 08, 06, 04 y 01 llegan al frente.",
                 "5. Confirmar la capacidad portante con el estudio de mecanica de suelos antes del vaciado."]

DQ.CON_CERCO = False
DQ.TXT_NPT_LEY = "losa superior = vereda +%.2f (terreno natural a ambos lados)"
DQ.TXT_TEC_CL = "Junta e=1\" de tecnopor y sellador asfaltico con la caja CL (perimetro de la seccion)"
DQ.TXT_TEC_PISO = "Junta de tecnopor e=1\" con el piso (no aplica: terreno natural a ambos lados)"

# detalles DD-01 a DD-04
DD.SUB_N_REG = "11 REGISTROS"; DD.SUB_N_TAPAS = "11 TAPAS"; DD.SUB_N_JUNTAS = "%d JUNTAS" % int(dz.P_FIN // 4.0)
DD.ANCHO_PROC_DD03 = 262
DD.NOTA4_DD03 = ("4. Junta con la caja CL (02): plancha de 1\" en todo el contacto del colector con el muro este de la CL, con sellador asfaltico 1\" x 2\""
                 " en las caras interiores y en la cara superior. A ambos lados del colector hay terreno natural: no lleva junta longitudinal.")
DD.TXT_REG_A = "1 por registro: 11 en la losa del colector (RV-01 a RV-11)"
DD.TXT_REG_B = "11 und (RV-01 a RV-11)"
DD.TXT_JUNTA_CAJAS = ("El colector lleva tecnopor en su contacto con la caja CL", "del Hogar de Refugio (muro este, 1.30 x 1.52).")
DD.TXT_DD04_SUB = "4 EMPALMES (EJES 09, 08, 06 Y 04): LA CUNETA SE METRA HASTA EL MURO DEL COLECTOR - EJE 01 A LA CL (DP-07) - ESC. INDICADAS"
DD.PARTIDA_EMPALME = None
DQ.TIT_DA03 = "DETALLE DE PARTIDAS: ACERO, REGISTROS Y JUNTAS"
DQ.TIT_RES_DA03 = "RESUMEN DE ACERO, REGISTROS Y JUNTAS"
DD.TXT_DD03_C = "ESC. 1/10 - corte longitudinal por el eje en la llegada a la caja CL (0+105.29)"
DD.N_EMPALMES_TXT = "4 und"
DD.TXT_DD04_CUNETA = "(acortadas hasta la cara del muro del colector)"


def usar_planilla():
    """Los cuadros de las laminas (DA-01 a DA-03) muestran los valores de la planilla del presupuesto (planilla_v)."""
    import planilla_v as PV
    if getattr(MC, "_resumen_calc", None) is None: MC._resumen_calc = MC.resumen
    def resumen():
        T, Rs = MC._resumen_calc()
        v = PV.valor
        Rs.update(trazo_m2=v("01.04.04.01.02"), excav_m3=v("01.04.04.02.01"), refine_m2=v("01.04.04.02.02"), relleno_m3=v("01.04.04.02.03"),
                  elimin_m3=v("01.04.04.02.04"), solado_m2=v("01.04.04.03.01"), encof_m2=v("01.04.04.04.02"), acabado_m2=v("01.04.04.04.04"),
                  curado_m2=v("01.04.04.04.05"), empalmes=None)      # sin partida de empalme: la cuneta se metra hasta el muro del colector
        assert abs(Rs["conc_fondo_m3"] + Rs["conc_muros_m3"] + Rs["conc_losa_m3"] - v("01.04.04.04.01")) < 0.05, "concreto del colector"
        assert abs(Rs["acero_38_kg"] + Rs["acero_12_kg"] - v("01.04.04.04.03")) < 0.05
        J = Rs["juntas"]; assert abs(J["L_dilat"] - v("01.04.04.06.01")) < 0.01 and abs(J["L_tecnopor_cl"] - v("01.04.04.06.02")) < 0.01, J
        Rg = Rs["registros"]; assert Rg["n"] == v("01.04.04.05.01")
        return T, Rs
    MC.resumen = resumen


def cargar():
    """R (diseno), T (terreno) y BP (base de arquitectura de Varones en el marco de Solange)."""
    import json
    R = json.load(open(os.path.join(dz.CALC, "diseno.json"), encoding="utf8"))
    T = json.load(open(os.path.join(dz.CALC, "terreno.json")))
    BP = json.load(open(os.path.join(dz.CALC, "base_planta.json"), encoding="utf8"))
    return R, T, BP
