"""Adapta los modulos compartidos (planta, secciones, cuadros, detalles, metrado) al tramo CAR Varones.

Los modulos de Solange importan `diseno as dz` y copian `D = dz.D` al cargarse; aqui se reemplazan por
diseno_v y se fijan los textos/parametros propios de Varones. Importar este modulo ANTES de dibujar.
"""
import os, sys
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
MC.NOMBRE_TRAMO_FINAL = "tramo de empalme con la CL (horizontal)"
MC.cajas = lambda: {}
H_MAX = 1.17          # altura interior maxima (llegada a la CL) redondeada como en la planilla: perimetro de junta 4.64 m


def _juntas():
    n = int(dz.P_FIN // 4.0)
    hmax = H_MAX if H_MAX else dz.techo(dz.P_FIN) - dz.fondo(dz.P_FIN)
    per = 2 * (D["b"] + 2 * D["e_muro"]) + 2 * (D["e_fondo"] + hmax + D["e_losa"])
    # no hay cerco perimetrico en el frente de Varones: tecnopor solo en los dos bordes de la losa con el piso adyacente y en el
    # contacto del colector con el muro este de la caja CL (perimetro de la seccion)
    per_cl = 2 * (D["b"] + 2 * D["e_muro"]) + 2 * (D["e_fondo"] + hmax + D["e_losa"])
    return dict(n=n, L_dilat=n * per, L_tecnopor_cerco=0.0, L_tecnopor_cl=per_cl, L_tecnopor_piso=2 * dz.P_FIN + per_cl)


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
DD.CON_CERCO = False
DD.TIT_DD03_C = "C. JUNTA DE TECNOPOR CON EL PISO ADYACENTE"
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
                 "3. El frente del CAR Varones no tiene cerco perimetrico: el colector queda bajo el piso exterior (+261.15) con junta de tecnopor de 1\" entre la losa superior y el piso adyacente a ambos lados.",
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
    "LOSA SUPERIOR: vaciada monoliticamente con los muros en todo el colector; acabado frotachado y brunado (a nivel del piso terminado +261.15).",
    "REGISTROS: marco y contramarco de angulo 2\"x2\"x3/16\" y 1 1/2\"x1 1/2\"x1/8\" con anclajes, pintura anticorrosiva y esmalte; tapas de concreto 0.68 x 0.68 x 0.08 con asas.",
    "JUNTAS: cada 4.00 m, e = 1\", relleno de poliestireno expandido y sello elastomerico de poliuretano. Tecnopor de 1\" entre el colector y las cunetas, la caja CL y el piso adyacente (no hay cerco perimetrico en el frente).",
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
DQ.TXT_TEC_CL = "Junta de tecnopor e=1\" con la caja CL (perimetro de la seccion; parte de la 02)"
DQ.TXT_TEC_PISO = "Junta de tecnopor e=1\" (02) total: piso a ambos lados (2 x L) + caja CL"

# detalles DD-01 a DD-04
DD.SUB_N_REG = "11 REGISTROS"; DD.SUB_N_TAPAS = "11 TAPAS"; DD.SUB_N_JUNTAS = "%d JUNTAS" % int(dz.P_FIN // 4.0)
DD.ANCHO_PROC_DD03 = 262
DD.NOTA4_DD03 = ("4. Juntas de tecnopor (02): plancha de 1\" x 0.10 en el borde de la losa, a ambos lados, antes de vaciar el piso adyacente;"
                 " plancha de 1\" en todo el contacto del colector con la caja CL.")
DD.TXT_REG_A = "1 por registro: 11 en la losa del colector (RV-01 a RV-11)"
DD.TXT_REG_B = "11 und (RV-01 a RV-11)"
DD.TXT_JUNTA_CAJAS = ("El colector lleva tecnopor en su contacto con la caja CL", "del Hogar de Refugio (muro este, 1.30 x 1.52).")
DD.TXT_DD04_SUB = "4 EMPALMES AL COLECTOR (CUNETAS EJES 09, 08, 06 Y 04) - LA CUNETA DEL EJE 01 ENTRA A LA CAJA CL (DP-07) - ESC. INDICADAS"
DD.TXT_DD03_C = "ESC. 1/10 - en toda la longitud del colector, a ambos lados (no hay cerco perimetrico)"
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
                  elimin_m3=v("01.04.04.02.04"), solado_m2=v("01.04.04.03.01"), conc_fondo_m3=v("01.04.04.04.01"), conc_muros_m3=v("01.04.04.04.02"),
                  conc_losa_m3=v("01.04.04.04.03"), encof_m2=v("01.04.04.04.04"), acabado_m2=v("01.04.04.04.06"), curado_m2=v("01.04.04.04.07"),
                  empalmes=int(v("01.04.04.06.03")))
        assert abs(Rs["acero_38_kg"] + Rs["acero_12_kg"] - v("01.04.04.04.05")) < 0.05
        J = Rs["juntas"]; assert abs(J["L_dilat"] - v("01.04.04.06.01")) < 0.01 and abs(J["L_tecnopor_piso"] - v("01.04.04.06.02")) < 0.01, J
        Rg = Rs["registros"]; assert Rg["n"] == v("01.04.04.05.01") and abs(Rg["contramarco_kg"] + Rg["marco_kg"] - v("01.04.04.05.03")) < 0.05
        return T, Rs
    MC.resumen = resumen


def cargar():
    """R (diseno), T (terreno) y BP (base de arquitectura de Varones en el marco de Solange)."""
    import json
    R = json.load(open(os.path.join(dz.CALC, "diseno.json"), encoding="utf8"))
    T = json.load(open(os.path.join(dz.CALC, "terreno.json")))
    BP = json.load(open(os.path.join(dz.CALC, "base_planta.json"), encoding="utf8"))
    return R, T, BP
