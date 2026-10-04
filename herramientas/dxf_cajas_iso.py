"""Laminas DP-07 (cajas de llegada y de caida), DP-09 (isometricos constructivos) y DP-10 (isometrico general)."""
import os, sys, math
import numpy as np
from ezdxf.enums import TextEntityAlignment as TA
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import diseno as dz
import dxf_base as B
from dxf_planta import prog_txt, perfil_en, terreno_en, eje_puntos
from dxf_secciones import geometria, iso_colector
import metrado_calc as MC

D = dz.D


# ----------------------------------------------------------------------------
def dp07(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 25, "DP-07", "CAJA DE LLEGADA (0+000) Y CAJA DE CAIDA CON POZA DE DISIPACION (ENTREGA AL CAR MUJERES)",
                   "PLANTAS, CORTES, ARMADO Y CUADRO DE MATERIALES - ESC. 1/25")
    f = lam.f; e = D["e_muro"]; ef = D["e_fondo"]; es = D["e_solado"]; et = D["e_losa"]
    C = MC.cajas()
    # ================= CAJA DE LLEGADA CL =================
    # planta: colector sale hacia la izquierda (aguas abajo), CL a la derecha; aporte externo entra por la derecha (NE)
    Li, Bi = D["CL_largo"], D["CL_ancho"]
    ox_, oy_ = lam.P(150, 505)
    Lt = Li + e                                   # interior total: murete del escalon (e) + poza (Li)
    lam.rect(ox_, oy_ - Bi / 2 - e, ox_ + Lt + e, oy_ + Bi / 2 + e, "CONCRETO", const_width=0.004)
    lam.rect(ox_, oy_ - Bi / 2, ox_ + Lt, oy_ + Bi / 2, "CONCRETO")
    lam.rect(ox_ - 2.0, oy_ - D["b"] / 2 - e, ox_, oy_ + D["b"] / 2 + e, "CONCRETO", const_width=0.004)
    lam.rect(ox_ - 2.0, oy_ - D["b"] / 2, ox_, oy_ + D["b"] / 2, "CONCRETO-OCULTO")
    lam.poli([(ox_, oy_ - D["b"] / 2), (ox_, oy_ + D["b"] / 2)], "CONCRETO-OCULTO")
    lam.poli([(ox_ + e, oy_ - Bi / 2), (ox_ + e, oy_ + Bi / 2)], "CONCRETO-OCULTO")   # escalon de la poza (murete e=0.15 bajo el fondo del colector)
    for pts in ([(ox_, oy_ + Bi / 2), (ox_ + Lt + e, oy_ + Bi / 2), (ox_ + Lt + e, oy_ + Bi / 2 + e), (ox_, oy_ + Bi / 2 + e)],
                [(ox_, oy_ - Bi / 2 - e), (ox_ + Lt + e, oy_ - Bi / 2 - e), (ox_ + Lt + e, oy_ - Bi / 2), (ox_, oy_ - Bi / 2)],
                [(ox_ + Lt, oy_ - Bi / 2), (ox_ + Lt + e, oy_ - Bi / 2), (ox_ + Lt + e, oy_ + Bi / 2), (ox_ + Lt, oy_ + Bi / 2)],
                [(ox_ - 2.0, oy_ + D["b"] / 2), (ox_, oy_ + D["b"] / 2), (ox_, oy_ + D["b"] / 2 + e), (ox_ - 2.0, oy_ + D["b"] / 2 + e)],
                [(ox_ - 2.0, oy_ - D["b"] / 2 - e), (ox_, oy_ - D["b"] / 2 - e), (ox_, oy_ - D["b"] / 2), (ox_ - 2.0, oy_ - D["b"] / 2)]):
        lam.achurado(pts, escala_mm=0.5)
    # ventana de llegada del colector del CAR Varones (muro este, cara de la derecha): 0.60 de ancho, hasta el techo de la CL
    bv = D["b_varones"]; tCL = D["NPT_CL"]
    lam.rect(ox_ + Lt, oy_ - bv / 2, ox_ + Lt + e, oy_ + bv / 2, "CONCRETO-OCULTO")
    lam.rect(ox_ + Lt + e + 0.025, oy_ - bv / 2 - e, ox_ + Lt + e + 1.5, oy_ + bv / 2 + e, "ARQ-BASE"); lam.rect(ox_ + Lt + e + 0.025, oy_ - bv / 2, ox_ + Lt + e + 1.5, oy_ + bv / 2, "ARQ-BASE")
    lam.bloque("SIMB-FLECHA", (ox_ + Lt + e + 1.0, oy_), f, rot=180, capa="FLUJO"); lam.bloque("SIMB-FLECHA", (ox_ - 1.2, oy_), f, rot=180, capa="FLUJO")
    # cuneta Eje 01 del CAR Varones: entra por el muro norte de la CL a 1.20 de la cara este
    xc1 = ox_ + Lt + e - D["E01_u"]; lam.rect(xc1 - 0.3, oy_ + Bi / 2 + e, xc1 + 0.3, oy_ + Bi / 2 + e + 0.9, "CUNETA"); lam.rect(xc1 - 0.2, oy_ + Bi / 2, xc1 + 0.2, oy_ + Bi / 2 + e, "CONCRETO-OCULTO")
    lam.bloque("SIMB-FLECHA", (xc1, oy_ + Bi / 2 + e + 0.6), f, rot=-90, capa="FLUJO")
    # cuneta Eje 01 de este proyecto: entra al colector por el muro lado predio en 0+001.07
    xs1 = ox_ - 1.07; lam.rect(xs1 - 0.3, oy_ + D["b"] / 2 + e, xs1 + 0.3, oy_ + D["b"] / 2 + e + 0.9, "CUNETA"); lam.rect(xs1 - 0.2, oy_ + D["b"] / 2, xs1 + 0.2, oy_ + D["b"] / 2 + e, "CONCRETO-OCULTO")
    lam.bloque("REGISTRO-PLANTA", (ox_ + 0.90, oy_), 1.0)
    lam.linea((ox_ - 2.0, oy_), (ox_ + Lt + 1.6, oy_), "EJE-COLECTOR")
    lam.linea((ox_, oy_ - Bi / 2 - e - 0.7), (ox_, oy_ + Bi / 2 + e + 1.2), "LINDERO"); lam.texto((ox_ - 0.05, oy_ + Bi / 2 + e + 1.0), "LINDERO (x = 349162.00)", 1.5, "LINDERO", TA.RIGHT)
    lam.cota((ox_, oy_ - Bi / 2 - e), (ox_ + e, oy_ - Bi / 2 - e), -8); lam.cota((ox_ + e, oy_ - Bi / 2 - e), (ox_ + Lt, oy_ - Bi / 2 - e), -8); lam.cota((ox_ + Lt, oy_ - Bi / 2 - e), (ox_ + Lt + e, oy_ - Bi / 2 - e), -8)
    lam.cota((ox_ + Lt + e, oy_ - Bi / 2 - e), (ox_ + Lt + e, oy_ - Bi / 2), 6, horizontal=False); lam.cota((ox_ + Lt + e, oy_ - Bi / 2), (ox_ + Lt + e, oy_ + Bi / 2), 6, horizontal=False); lam.cota((ox_ + Lt + e, oy_ + Bi / 2), (ox_ + Lt + e, oy_ + Bi / 2 + e), 6, horizontal=False)
    lam.cota((ox_ - 2.0, oy_ - D["b"] / 2), (ox_ - 2.0, oy_ + D["b"] / 2), -6, horizontal=False)
    lam.cota((ox_ + Lt, oy_ - bv / 2), (ox_ + Lt, oy_ + bv / 2), 0, horizontal=False, texto="0.60")
    lam.cota((xc1 - 0.2, oy_ + Bi / 2 + e + 0.9), (xc1 + 0.2, oy_ + Bi / 2 + e + 0.9), 5, texto="0.40"); lam.cota((xc1, oy_ + Bi / 2 + e + 0.9), (ox_ + Lt + e, oy_ + Bi / 2 + e + 0.9), 11, texto="%.2f" % D["E01_u"])
    lam.texto((ox_ - 1.0, oy_ + 0.75), "0+000.00", 1.8, "PROGRESIVAS", TA.MIDDLE_CENTER); lam.linea((ox_, oy_ + Bi / 2 + e), (ox_, oy_ + Bi / 2 + e + 0.4), "PROGRESIVAS")
    xt = ox_ + Lt + e + 1.9
    lam.llamada((xc1 + 0.3, oy_ + Bi / 2 + e + 0.5), (xt, oy_ + 1.6), ["cuneta Eje 01 del CAR Varones (0.40 x 0.77, NCF %.3f, 37.0 L/s): ventana 0.40 x %.2f en el muro norte" % (D["E01_NCF"], tCL - et - D["E01_NCF"])], 1.8)
    lam.llamada((ox_ + Lt + e + 0.8, oy_ + bv / 2 + e), (xt, oy_ + 1.1), ["LLEGADA DEL COLECTOR DEL CAR VARONES (CUI 2705619): b = 0.60, muros 0.15, 221.7 L/s; tecnopor 1\" en el contacto", "ventana 0.60 x %.2f en el muro este (fondo %.3f, hasta el techo de la CL %.2f, sin dintel)" % (tCL - et - D["CF_varones_sup"], D["CF_varones_sup"], tCL - et)], 1.8)
    lam.llamada((ox_ + 0.90 + 0.3, oy_ - 0.2), (xt, oy_ - 0.3), ["registro 0.68 x 0.68 sobre la caja, tapa al ras de +%.2f (piso del CAR Varones)" % tCL], 1.8)
    lam.llamada((ox_ + 0.3, oy_ - Bi / 2), (xt, oy_ - 0.8), ["caja interior 1.50 x 1.00 (mas murete de 0.15 en el escalon); poza 0.30 m bajo el fondo del colector", "la caja queda del lado del CAR Varones (x = 349162.00 a 349163.80): tapa en +261.15"], 1.8)
    lam.llamada((xs1 - 0.3, oy_ + D["b"] / 2 + e + 0.7), (ox_ - 2.0, oy_ + Bi / 2 + e + 1.25), ["cuneta Eje 01 de este proyecto (perfil 01): ventana 0.40 x H", "en el muro lado predio del colector, 0+001.07 (DP-06C)"], 1.8)
    lam.titulo_vista(165, 440, "CL-1. CAJA DE LLEGADA - PLANTA", "ESC. 1/25 - losa superior retirada", 120)
    # corte longitudinal CL (por el eje)
    ox_, oy_ = lam.P(150, 285); z0 = oy_; piso = D["CF0"] - D["CL_poza"]; Z = lambda z: z0 + (z - (piso - ef - es))
    zv1 = D["CF_varones_sup"]; zv2 = tCL - et                           # ventana este: del fondo del colector de Varones al techo de la CL
    NPT = D["NPT"]; CF0 = D["CF0"]
    xa = ox_; xb = ox_ + e; xc = xb + Li; xd = xc + e                      # cara oeste (lindero) - murete del escalon - interior de la poza - muro este
    xr = ox_ + 0.90                                                      # registro de la CL
    # contorno exterior: colector (losa en NPT) -> CL (tapa en tCL, escalon de 0.55 en la cara oeste = lindero)
    lam.poli([(ox_ - 2.0, Z(CF0 - ef)), (xa, Z(CF0 - ef)), (xa, Z(piso - ef)), (xd, Z(piso - ef)), (xd, Z(zv1)), (xd, Z(zv2)), (xd, Z(tCL)), (xa, Z(tCL)), (xa, Z(NPT)), (ox_ - 2.0, Z(NPT))], "CONCRETO", ancho=0.004)
    # contorno interior: fondo del colector, murete, poza, muro este bajo la ventana, techo de la CL, muro oeste sobre la salida al colector
    lam.poli([(ox_ - 2.0, Z(CF0)), (xb, Z(CF0)), (xb, Z(piso)), (xc, Z(piso)), (xc, Z(zv1)), (xd, Z(zv1)), (xd, Z(zv2)), (xb, Z(zv2)), (xb, Z(NPT - et)), (ox_ - 2.0, Z(NPT - et))], "CONCRETO")
    lam.poli([(ox_ - 2.05, Z(CF0 - ef - es)), (xa + 0.05, Z(CF0 - ef - es)), (xa + 0.05, Z(piso - ef - es)), (xd + 0.05, Z(piso - ef - es)), (xd + 0.05, Z(piso - ef)), (xa, Z(piso - ef)), (xa, Z(CF0 - ef)), (ox_ - 2.05, Z(CF0 - ef))], "SOLADO", cerrada=True)
    for p_ in ([(ox_ - 2.0, Z(CF0 - ef)), (xa, Z(CF0 - ef)), (xa, Z(piso - ef)), (xd, Z(piso - ef)), (xd, Z(piso)), (xc, Z(piso)), (xb, Z(piso)), (xb, Z(CF0)), (ox_ - 2.0, Z(CF0))],
               [(ox_ - 2.0, Z(NPT - et)), (xa, Z(NPT - et)), (xa, Z(NPT)), (ox_ - 2.0, Z(NPT))],
               [(xa, Z(NPT - et)), (xb, Z(NPT - et)), (xb, Z(zv2)), (xa, Z(zv2))],
               [(xa, Z(zv2)), (xr - 0.35, Z(zv2)), (xr - 0.35, Z(tCL)), (xa, Z(tCL))], [(xr + 0.35, Z(zv2)), (xd, Z(zv2)), (xd, Z(tCL)), (xr + 0.35, Z(tCL))],
               [(xc, Z(piso)), (xd, Z(piso)), (xd, Z(zv1)), (xc, Z(zv1))]):
        lam.achurado(p_, escala_mm=0.5)
    lam.rect(xr - 0.34, Z(tCL - 0.08), xr + 0.34, Z(tCL), "REGISTRO-TAPA")
    # ventana del muro norte (fondo de la vista) para la cuneta Eje 01 del CAR Varones
    xe1 = xd - D["E01_u"]
    lam.rect(xe1 - 0.2, Z(D["E01_NCF"]), xe1 + 0.2, Z(zv2), "CUNETA"); lam.relleno([(xe1 - 0.2, Z(D["E01_NCF"])), (xe1 + 0.2, Z(D["E01_NCF"])), (xe1 + 0.2, Z(zv2)), (xe1 - 0.2, Z(zv2))], "ISO-CUNETA")
    # colector del CAR Varones (referencia): llega con su seccion completa por la ventana del muro este
    lam.rect(xd + 0.025, Z(zv1 - 0.15), xd + 1.2, Z(tCL), "ARQ-BASE"); lam.rect(xd + 0.025, Z(zv1), xd + 1.2, Z(zv2), "ARQ-BASE")
    lam.poli([(xd, Z(tCL)), (xd + 1.4, Z(tCL))], "TERRENO", ancho=0.3 * f); lam.poli([(ox_ - 2.0, Z(NPT)), (ox_ - 2.3, Z(NPT))], "TERRENO", ancho=0.3 * f)
    # agua
    na0 = R["perfil"][0]["NA"]; na_v = zv1 + 0.24
    lam.poli([(ox_ - 2.0, Z(na0)), (xc, Z(na0))], "AGUA"); lam.bloque("SIMB-AGUA", (ox_ - 1.0, Z(na0)), f)
    lam.poli([(xd + 1.2, Z(na_v)), (xd, Z(na_v)), (xc - 0.2, Z(na_v - 0.12)), (xc - 0.45, Z(na0 + 0.05))], "AGUA")
    lam.bloque("SIMB-FLECHA", (xd + 0.7, Z(na_v + 0.3)), f, rot=180, capa="FLUJO"); lam.bloque("SIMB-FLECHA", (ox_ - 1.5, Z(CF0 + 0.25)), f, rot=180, capa="FLUJO")
    # acero: malla 3/8" @0.20 en ambas caras de la caja (marco exterior e interior), interrumpida en las ventanas
    r = 0.04
    lam.poli([(ox_ - 2.0, Z(CF0 - ef + r)), (xa + r, Z(CF0 - ef + r)), (xa + r, Z(piso - ef + r)), (xd - r, Z(piso - ef + r)), (xd - r, Z(zv1 - r)), (xc + r, Z(zv1 - r))], "ACERO")
    lam.poli([(xd - r, Z(zv2 + r)), (xd - r, Z(tCL - r)), (xa + r, Z(tCL - r)), (xa + r, Z(NPT - r)), (ox_ - 2.0, Z(NPT - r))], "ACERO")
    lam.poli([(ox_ - 2.0, Z(CF0 - r)), (xb - r, Z(CF0 - r)), (xb - r, Z(piso - r)), (xc + r, Z(piso - r)), (xc + r, Z(zv1 - r))], "ACERO")
    lam.poli([(xd - r, Z(zv2 + r)), (xb - r, Z(zv2 + r)), (xb - r, Z(NPT - et + r)), (ox_ - 2.0, Z(NPT - et + r))], "ACERO")
    for k in range(int(round((xd - (ox_ - 2.0)) / 0.20)) + 1):
        x = ox_ - 2.0 + k * 0.20
        if x > xd - r: continue
        zb_ = Z(piso - ef + r) if x > xa + r else Z(CF0 - ef + r)
        zt_ = Z(tCL - r) if x > xa + r else Z(NPT - r)
        for z in (zb_, zt_):
            lam.bloque("ACERO-38", (x, z), 1.0)
    lam.nivel((ox_ - 1.2, Z(NPT)), NPT, texto="NPT +%.2f (este tramo)" % NPT); lam.nivel((ox_ - 1.2, Z(CF0)), CF0, texto="CF %.2f (0+000)" % CF0)
    lam.nivel((xb + 0.75, Z(piso)), piso, texto="piso de poza %.2f" % piso); lam.nivel((xd + 0.6, Z(zv1)), zv1, texto="CF %.3f (colector CAR Varones)" % zv1)
    lam.nivel((xr + 0.5, Z(tCL)), tCL, texto="tapa CL +%.2f (piso del CAR Varones)" % tCL); lam.nivel((ox_ - 1.7, Z(na0)), na0, texto="NA %.3f" % na0, hmm=1.6)
    lam.cota((xa, Z(piso - ef - es)), (xb, Z(piso - ef - es)), -8); lam.cota((xb, Z(piso - ef - es)), (xc, Z(piso - ef - es)), -8); lam.cota((xc, Z(piso - ef - es)), (xd, Z(piso - ef - es)), -8)
    lam.cota((xd + 1.3, Z(piso)), (xd + 1.3, Z(zv1)), 8, horizontal=False, texto="caida %.2f" % (zv1 - piso)); lam.cota((xd + 1.3, Z(zv1)), (xd + 1.3, Z(zv2)), 8, horizontal=False, texto="ventana %.2f" % (zv2 - zv1))
    lam.cota((xa - 0.3, Z(NPT)), (xa - 0.3, Z(tCL)), -6, horizontal=False, texto="0.55")
    lam.linea((xa, Z(piso - ef - es - 0.3)), (xa, Z(tCL + 0.7)), "LINDERO"); lam.texto((xa - 0.05, Z(tCL + 0.45)), "LINDERO", 1.5, "LINDERO", TA.RIGHT, rot=90)
    xt = xd + 2.0
    lam.llamada((xr + 0.2, Z(tCL - 0.04)), (xt, Z(tCL + 0.75)), ["losa superior e=0.10 en +%.2f con registro 0.68 x 0.68" % tCL], 1.8)
    lam.llamada((xd + 0.9, Z(zv2 - 0.2)), (xt, Z(tCL + 0.3)), ["colector del CAR Varones (referencia): b=0.60, fondo %.3f, losa +%.2f; 221.7 L/s" % (zv1, tCL)], 1.8)
    lam.llamada((xe1, Z((D["E01_NCF"] + zv2) / 2)), (xt, Z(tCL - 0.15)), ["ventana 0.40 x %.2f en el muro norte: cuneta Eje 01 del CAR Varones (NCF %.3f, 37.0 L/s)" % (zv2 - D["E01_NCF"], D["E01_NCF"])], 1.8)
    lam.llamada((xc - 0.3, Z(na0 + 0.1)), (xt, Z(tCL - 0.6)), ["caida libre de %.2f m del fondo de Varones al NA; colchon de agua de %.2f m" % (zv1 - na0, na0 - piso)], 1.8)
    lam.llamada((xd - e / 2, Z(zv1 - 0.5)), (xt, Z(tCL - 1.05)), ["muros e=0.15, malla 3/8\" @0.20 en ambas caras; muro oeste hasta +261.15 (escalon de 0.55 entre pisos en el lindero)"], 1.8)
    lam.llamada((xb + 0.75, Z(piso - ef / 2)), (xt, Z(piso + 0.3)), ["losa de fondo e=0.15 sobre solado e=0.05"], 1.8)
    lam.titulo_vista(165, 240, "CL-2. CAJA DE LLEGADA - CORTE LONGITUDINAL POR EL EJE", "ESC. 1/25 - a la derecha, el colector del CAR Varones (referencia)", 150)
    # ================= CAJA DE CAIDA CC =================
    Li, Bi = D["CC_poza_largo"], D["CC_ancho"]; piso = D["CF_R01"] - D["CC_poza_prof"]
    # planta: colector 0.80 llega por la derecha (aguas arriba), poza 1.50 x 3.50, umbral, R-01 a la izquierda
    ox_, oy_ = lam.P(580, 505)   # ox_ = cara aguas arriba de la poza (brink), eje en oy_
    lam.rect(ox_ - Li - e, oy_ - Bi / 2 - e, ox_ + e, oy_ + Bi / 2 + e, "CONCRETO", const_width=0.004)
    lam.rect(ox_ - Li, oy_ - Bi / 2, ox_, oy_ + Bi / 2, "POZA")
    lam.rect(ox_ + e, oy_ - D["b"] / 2 - e, ox_ + 2.0, oy_ + D["b"] / 2 + e, "CONCRETO", const_width=0.004); lam.rect(ox_, oy_ - D["b"] / 2, ox_ + 2.0, oy_ + D["b"] / 2, "CONCRETO-OCULTO")
    for pts in ([(ox_ - Li - e, oy_ + Bi / 2), (ox_ + e, oy_ + Bi / 2), (ox_ + e, oy_ + Bi / 2 + e), (ox_ - Li - e, oy_ + Bi / 2 + e)],
                [(ox_ - Li - e, oy_ - Bi / 2 - e), (ox_ + e, oy_ - Bi / 2 - e), (ox_ + e, oy_ - Bi / 2), (ox_ - Li - e, oy_ - Bi / 2)],
                [(ox_ - Li - e, oy_ - Bi / 2), (ox_ - Li, oy_ - Bi / 2), (ox_ - Li, oy_ + Bi / 2), (ox_ - Li - e, oy_ + Bi / 2)],
                [(ox_ + e, oy_ + D["b"] / 2), (ox_ + 2.0, oy_ + D["b"] / 2), (ox_ + 2.0, oy_ + D["b"] / 2 + e), (ox_ + e, oy_ + D["b"] / 2 + e)],
                [(ox_ + e, oy_ - D["b"] / 2 - e), (ox_ + 2.0, oy_ - D["b"] / 2 - e), (ox_ + 2.0, oy_ - D["b"] / 2), (ox_ + e, oy_ - D["b"] / 2)]):
        lam.achurado(pts, escala_mm=0.5)
    # muro de cabecera (brink) entre el colector y la poza: tabiques a ambos lados del canal 0.80 -> 1.50 y murete bajo el fondo del colector
    lam.rect(ox_, oy_ + D["b"] / 2, ox_ + e, oy_ + Bi / 2, "CONCRETO"); lam.rect(ox_, oy_ - Bi / 2, ox_ + e, oy_ - D["b"] / 2, "CONCRETO")
    lam.achurado([(ox_, oy_ + D["b"] / 2), (ox_ + e, oy_ + D["b"] / 2), (ox_ + e, oy_ + Bi / 2), (ox_, oy_ + Bi / 2)], escala_mm=0.5)
    lam.achurado([(ox_, oy_ - Bi / 2), (ox_ + e, oy_ - Bi / 2), (ox_ + e, oy_ - D["b"] / 2), (ox_, oy_ - D["b"] / 2)], escala_mm=0.5)
    lam.poli([(ox_, oy_ - D["b"] / 2), (ox_, oy_ + D["b"] / 2)], "CONCRETO-OCULTO")   # brink: escalon a la poza
    # umbral: ventana de salida en el muro aguas abajo (1.50 x h) sobre el umbral
    lam.rect(ox_ - Li - e, oy_ - Bi / 2, ox_ - Li, oy_ + Bi / 2, "CONCRETO-OCULTO")
    lam.poli([(ox_ - Li + 0.25, oy_ - Bi / 2), (ox_ - Li + 0.25, oy_ + Bi / 2)], "POZA")
    # cuneta Eje 12 entra por el muro lado predio de la poza
    xc12 = ox_ - Li + 1.0; lam.rect(xc12 - 0.3, oy_ + Bi / 2 + e, xc12 + 0.3, oy_ + Bi / 2 + e + 1.0, "CUNETA"); lam.rect(xc12 - 0.2, oy_ + Bi / 2, xc12 + 0.2, oy_ + Bi / 2 + e, "CONCRETO-OCULTO")
    lam.bloque("REGISTRO-PLANTA", (ox_ - 0.6, oy_), 1.0); lam.bloque("REGISTRO-PLANTA", (ox_ - Li + 1.0, oy_), 1.0)
    lam.linea((ox_ - Li - 1.5, oy_), (ox_ + 2.0, oy_), "EJE-COLECTOR")
    lam.bloque("SIMB-FLECHA", (ox_ + 1.2, oy_), f, rot=180, capa="FLUJO"); lam.bloque("SIMB-FLECHA", (ox_ - Li - 0.9, oy_), f, rot=180, capa="FLUJO")
    # R-01 de CAR Mujeres (referencia)
    lam.rect(ox_ - Li - e - 1.5, oy_ - Bi / 2 - 0.10, ox_ - Li - e, oy_ + Bi / 2 + 0.10, "ARQ-BASE"); lam.texto((ox_ - Li - e - 0.75, oy_ - Bi / 2 - 0.35), "R-01 / 0+000 CAR MUJERES (CUI 2717013)", 1.6, "ARQ-TEXTO", TA.MIDDLE_CENTER)
    lam.texto((ox_ + 1.0, oy_ + 0.9), prog_txt(dz.P_BRINK) + " (brink)", 1.8, "PROGRESIVAS", TA.MIDDLE_CENTER); lam.texto((ox_ - Li - e, oy_ + 1.2), prog_txt(dz.P_FIN), 1.8, "PROGRESIVAS", TA.MIDDLE_CENTER)
    lam.cota((ox_ - Li, oy_ - Bi / 2 - e), (ox_, oy_ - Bi / 2 - e), -8); lam.cota((ox_ - Li - e, oy_ - Bi / 2 - e), (ox_ - Li, oy_ - Bi / 2 - e), -8); lam.cota((ox_ - Li, oy_ - Bi / 2 - e), (ox_ - Li + 0.25, oy_ - Bi / 2 - e), -4)
    lam.cota((ox_ + 2.0, oy_ - D["b"] / 2), (ox_ + 2.0, oy_ + D["b"] / 2), 6, horizontal=False); lam.cota((ox_, oy_ - Bi / 2 - e), (ox_ + e, oy_ - Bi / 2 - e), -8)
    lam.cota((ox_ - Li - e, oy_ - Bi / 2), (ox_ - Li - e, oy_ + Bi / 2), -6, horizontal=False); lam.cota((ox_ - Li - e, oy_ + Bi / 2), (ox_ - Li - e, oy_ + Bi / 2 + e), -6, horizontal=False)
    xt = ox_ + 2.4
    lam.llamada((xc12, oy_ + Bi / 2 + e + 0.5), (xt, oy_ + 1.4), ["cuneta Eje 12 (perfil 12), prolongada 5.39 m: ventana 0.40 x 0.80"], 1.8)
    lam.llamada((ox_ - 1.0, oy_ + 0.55), (xt, oy_ + 1.0), ["poza de disipacion 1.50 x 3.50, piso 258.32 (0.40 bajo el fondo del receptor)"], 1.8)
    lam.llamada((ox_, oy_ + 0.3), (xt, oy_ + 0.6), ["brink: fin del colector b=0.80 (CF %.3f); caida libre a la poza" % dz.fondo(dz.P_BRINK)], 1.8)
    lam.llamada((ox_ - 0.6 + 0.3, oy_ - 0.2), (xt, oy_ + 0.2), ["registros 0.68 x 0.68 (2 und) sobre la poza"], 1.8)
    lam.llamada((ox_ - Li - e / 2, oy_ - 0.3), (xt, oy_ - 0.3), ["muro aguas abajo con ventana 1.50 x 0.60 sobre el umbral: entrega al R-01 (junta de 1\")"], 1.8)
    lam.llamada((ox_ - Li + 0.12, oy_ - 0.55), (xt, oy_ - 0.75), ["umbral de salida 0.25 x 0.40 (corona 258.72 = CF del R-01)"], 1.8)
    lam.titulo_vista(560, 440, "CC-1. CAJA DE CAIDA - PLANTA", "ESC. 1/25 - losa superior retirada", 120)
    # corte longitudinal CC
    ox_, oy_ = lam.P(580, 285); z0 = oy_; Z = lambda z: z0 + (z - (piso - ef - es))
    zb = dz.fondo(dz.P_BRINK)
    zw1, zw2 = D["CF_R01"], D["CF_R01"] + 0.60          # ventana de salida al R-01 (sobre el umbral)
    xm = ox_ + e                                          # murete del escalon entre el fondo del colector y la poza
    # solado escalonado
    lam.poli([(ox_ + 2.0, Z(zb - ef - es)), (xm + 0.05, Z(zb - ef - es)), (xm + 0.05, Z(piso - ef - es)), (ox_ - Li - e - 0.05, Z(piso - ef - es)), (ox_ - Li - e - 0.05, Z(piso - ef)), (xm, Z(piso - ef)), (xm, Z(zb - ef)), (ox_ + 2.0, Z(zb - ef))], "SOLADO", cerrada=True)
    # contorno exterior (escalonado en xm) e interior (colector hasta el brink, poza, umbral, ventana de salida)
    lam.poli([(ox_ + 2.0, Z(zb - ef)), (xm, Z(zb - ef)), (xm, Z(piso - ef)), (ox_ - Li - e, Z(piso - ef)), (ox_ - Li - e, Z(zw1)), (ox_ - Li - e, Z(zw2)), (ox_ - Li - e, Z(D["NPT"])), (ox_ + 2.0, Z(D["NPT"]))], "CONCRETO", cerrada=True, ancho=0.004)
    lam.poli([(ox_ + 2.0, Z(zb)), (ox_, Z(zb)), (ox_, Z(piso)), (ox_ - Li + 0.25, Z(piso)), (ox_ - Li + 0.25, Z(zw1)), (ox_ - Li, Z(zw1)), (ox_ - Li - e, Z(zw1)), (ox_ - Li - e, Z(zw2)), (ox_ - Li, Z(zw2)), (ox_ - Li, Z(D["NPT"] - et)), (ox_ + 2.0, Z(D["NPT"] - et))], "CONCRETO")
    for p_ in ([(ox_ + 2.0, Z(zb - ef)), (xm, Z(zb - ef)), (xm, Z(piso - ef)), (ox_ - Li - e, Z(piso - ef)), (ox_ - Li - e, Z(zw1)), (ox_ - Li, Z(zw1)), (ox_ - Li + 0.25, Z(zw1)), (ox_ - Li + 0.25, Z(piso)), (ox_, Z(piso)), (ox_, Z(zb)), (ox_ + 2.0, Z(zb))],
               [(ox_ - Li - e, Z(D["NPT"] - et)), (ox_ + 2.0, Z(D["NPT"] - et)), (ox_ + 2.0, Z(D["NPT"])), (ox_ - Li - e, Z(D["NPT"]))],
               [(ox_ - Li - e, Z(zw2)), (ox_ - Li, Z(zw2)), (ox_ - Li, Z(D["NPT"] - et)), (ox_ - Li - e, Z(D["NPT"] - et))]):
        lam.achurado(p_, escala_mm=0.5)
    # agua: perfil en el colector (yc en el brink), chorro, resalto ahogado, NA receptor
    y_b = R["brink"]["yc"]; y1 = R["poza"]["y1"]; NAr = D["NA_R01"]
    lam.poli([(ox_ + 2.0, Z(perfil_en(R, dz.P_BRINK - 2.0, "NA"))), (ox_ + 0.5, Z(zb + y_b + 0.02)), (ox_, Z(zb + y_b))], "AGUA")
    lam.poli([(ox_, Z(zb + y_b)), (ox_ - 0.25, Z(zb + 0.4 * y_b)), (ox_ - 0.55, Z(piso + y1 + 0.05)), (ox_ - 0.9, Z(piso + 0.45)), (ox_ - 1.6, Z(NAr - 0.02)), (ox_ - Li - e - 1.0, Z(NAr))], "AGUA")
    lam.bloque("SIMB-AGUA", (ox_ - Li - 0.5, Z(NAr)), f); lam.bloque("SIMB-AGUA", (ox_ + 1.2, Z(perfil_en(R, dz.P_BRINK - 1.2, "NA"))), f)
    lam.bloque("SIMB-FLECHA", (ox_ + 1.5, Z(zb + 0.2)), f, rot=180, capa="FLUJO"); lam.bloque("SIMB-FLECHA", (ox_ - Li - e - 0.7, Z(D["CF_R01"] + 0.2)), f, rot=180, capa="FLUJO")
    # R-01 referencia
    lam.rect(ox_ - Li - e - 1.5, Z(D["CF_R01"] - 0.10), ox_ - Li - e, Z(D["NPT_wilma"]), "ARQ-BASE"); lam.texto((ox_ - Li - e - 0.75, Z(D["NPT_wilma"] + 0.15)), "R-01 CAR MUJERES", 1.6, "ARQ-TEXTO", TA.MIDDLE_CENTER)
    lam.texto((ox_ - Li - e - 0.75, Z(D["CF_R01"] + 0.15)), "b = 1.50, CF 258.72", 1.5, "ARQ-TEXTO", TA.MIDDLE_CENTER)
    # acero: malla 3/8" @0.20 en ambas caras (marco exterior e interior), interrumpida en la ventana de salida
    r = 0.04
    lam.poli([(ox_ + 2.0, Z(zb - ef + r)), (xm - r, Z(zb - ef + r)), (xm - r, Z(piso - ef + r)), (ox_ - Li - e + r, Z(piso - ef + r)), (ox_ - Li - e + r, Z(zw1 - r)), (ox_ - Li - r, Z(zw1 - r))], "ACERO")
    lam.poli([(ox_ - Li - r, Z(zw2 + r)), (ox_ - Li - e + r, Z(zw2 + r)), (ox_ - Li - e + r, Z(D["NPT"] - r)), (ox_ + 2.0, Z(D["NPT"] - r))], "ACERO")
    lam.poli([(ox_ + 2.0, Z(zb - r)), (ox_ + r, Z(zb - r)), (ox_ + r, Z(piso - r)), (ox_ - Li + r, Z(piso - r)), (ox_ - Li + r, Z(zw1 - r)), (ox_ - Li - r, Z(zw1 - r))], "ACERO")
    lam.poli([(ox_ - Li - r, Z(zw2 + r)), (ox_ - Li + r, Z(zw2 + r)), (ox_ - Li + r, Z(D["NPT"] - et + r)), (ox_ + 2.0, Z(D["NPT"] - et + r))], "ACERO")
    for k in range(int(round((Li + e + 2.0) / 0.20)) + 1):
        x = ox_ + 2.0 - k * 0.20
        if x < ox_ - Li - e + r: continue
        lam.bloque("ACERO-38", (x, Z(zb - ef + r) if x > xm - r else Z(piso - ef + r)), 1.0); lam.bloque("ACERO-38", (x, Z(D["NPT"] - r)), 1.0)
    lam.nivel((ox_ + 1.2, Z(D["NPT"])), D["NPT"], texto="NPT +260.60"); lam.nivel((ox_ + 1.0, Z(zb)), zb, texto="CF brink %.3f" % zb)
    lam.nivel((ox_ - 1.5, Z(piso)), piso, texto="piso de poza 258.32"); lam.nivel((ox_ - Li + 0.12, Z(D["CF_R01"])), D["CF_R01"], texto="umbral 258.72")
    lam.nivel((ox_ - Li - 0.6, Z(NAr)), NAr, texto="NA receptor 259.062", hmm=1.6)
    lam.cota((ox_ - Li, Z(piso - ef - es)), (ox_, Z(piso - ef - es)), -8); lam.cota((ox_ - Li, Z(piso - ef - es)), (ox_ - Li + 0.25, Z(piso - ef - es)), -4)
    lam.cota((ox_ + 2.0, Z(piso)), (ox_ + 2.0, Z(zb)), 8, horizontal=False, texto="%.2f" % (zb - piso)); lam.cota((ox_ + 2.0, Z(zb)), (ox_ + 2.0, Z(D["NPT"] - et)), 8, horizontal=False)
    lam.cota((ox_, Z(piso - ef - es)), (xm, Z(piso - ef - es)), -4)
    lam.cota((ox_ - Li - e, Z(piso)), (ox_ - Li - e, Z(D["CF_R01"])), -8, horizontal=False); lam.cota((ox_ - Li - e, Z(D["CF_R01"])), (ox_ - Li - e, Z(D["CF_R01"] + 0.60)), -8, horizontal=False)
    xt = ox_ + 2.4
    lam.llamada((ox_ - Li - e / 2, Z(D["CF_R01"] + 0.3)), (xt, Z(D["NPT"] + 0.5)), ["ventana de salida 1.50 x 0.60 en el muro de la caja; junta de 1\" con el muro del R-01"], 1.8)
    lam.llamada((ox_ - 0.2, Z(zb + 0.05)), (xt, Z(D["NPT"] + 0.1)), ["caida libre 0.57 m: y1 = 0.16, F1 = 3.5; conjugado y2 = 0.71 < tirante disponible 0.74: resalto ahogado"], 1.8)
    lam.llamada((ox_ - 1.0, Z(piso - ef / 2)), (xt, Z(piso - 0.25)), ["losa de fondo e=0.15 sobre solado; malla 3/8\" @0.20 ambas caras en losas y muros"], 1.8)
    lam.llamada((ox_ - Li + 0.12, Z(D["CF_R01"] - 0.25)), (xt, Z(piso + 0.35)), ["umbral de concreto 0.25 x 0.40; corona = fondo del R-01"], 1.8)
    lam.titulo_vista(560, 240, "CC-2. CAJA DE CAIDA - CORTE LONGITUDINAL POR EL EJE", "ESC. 1/25", 160)
    # cuadro de materiales de las cajas
    filas = []
    for k in ("CL", "CC"):
        c = C[k]
        filas += [[c["nombre"], "concreto f'c=210 (losas + muros)", "%.2f" % (c["c_fondo"] + c["c_muros"] + c["c_losa"]), "m3"],
                  ["", "encofrado", "%.2f" % c["encof"], "m2"], ["", "acero 3/8\" @0.20", "%.1f" % c["acero_kg"], "kg"],
                  ["", "excavacion / solado", "%.2f / %.2f" % (c["excav"], c["solado"]), "m3 / m2"]]
    lam.tabla(32, 170, ["CAJA", "PARTIDA", "CANTIDAD", "UND"], filas, [40, 70, 30, 18], 1.7, 4.2, "CUADRO DE MATERIALES DE LAS CAJAS")
    lam.leyenda(230, 170, [("achurado", "CONCRETO-ACHURADO", "concreto armado f'c=210 kg/cm2"), ("rect", "SOLADO", "solado f'c=100 e=0.05"), ("linea", "ACERO", "acero transversal (marcos y malla, rojo)"), ("bloque:ACERO-38", "ACERO-PUNTOS", "acero perpendicular al corte (azul)"),
                           ("linea", "AGUA", "nivel de agua / chorro"), ("rect", "POZA", "poza de disipacion y umbral"), ("rect", "ARQ-BASE", "receptor (CAR Mujeres), referencia"), ("linea", "CUNETA", "cuneta que llega")], 1.8)
    lam.notas(430, 170, "NOTAS", ["1. Ambas cajas quedan dentro del predio, cubiertas con losa e=0.10 y registros de 0.68 x 0.68.",
                                    "2. La caja de llegada recibe el colector del CAR Varones (CUI 2705619) por su muro este (ventana 0.60 x 1.17, fondo 259.884) y la cuneta Eje 01 de ese proyecto por el muro norte (ventana 0.40 x 0.66); su tapa queda en +261.15 (piso del CAR Varones).",
                                    "3. La caja de caida entrega al R-01 del colector del CAR Mujeres (CUI 2717013) con fondo del umbral 258.72; el resalto queda ahogado por el tirante del receptor (memoria, hoja EMPALME).",
                                    "4. Secciones transversales de las cajas: muros e=0.15, losa de fondo e=0.15, malla 3/8\" @0.20 en ambas caras; esquinas con ganchos de 0.40 m.",
                                    "5. Junta de tecnopor 1\" + sello entre la caja CC y el muro del R-01, y entre la caja CL y el colector de llegada."], 1.7)
    return lam


# ----------------------------------------------------------------------------
def dp09(doc, ox, oy, R, T):
    lam = B.Lamina(doc, ox, oy, 25, "DP-09", "ISOMETRICOS CONSTRUCTIVOS", "COLECTOR JUNTO AL CERCO, REGISTRO DE LIMPIEZA, EMPALME DE CUNETA Y CAJA DE CAIDA")
    f = lam.f; e = D["e_muro"]; ef = D["e_fondo"]; et = D["e_losa"]; be = D["b_ext"]
    # ISO 1: tramo de 3 m junto al cerco, con junta y piso
    o = lam.P(120, 330); esc = 0.8
    Tt = lambda x, y, z: (o[0] + B.iso(x, y, z)[0] * esc, o[1] + B.iso(x, y, z)[1] * esc)
    kw = dict(origen=o, esc=esc); g = geometria(10.0); h = g["h"]
    # cerco al lado predio (lado lejano, x < 0) con su cimiento
    xc = -D["junta_cerco"] - 0.15
    B.caja_iso(lam, xc - 0.25, 0, ef + h + et - 0.9, 0.40, 3.0, 0.30, capas=("ISO-CERCO", "ISO-CERCO", "ISO-CERCO"), **kw)
    B.caja_iso(lam, xc, 0, ef + h + et - 0.9, 0.15, 3.0, 1.5, capas=("ISO-CERCO", "ISO-CERCO", "ISO-CERCO"), **kw)
    iso_colector(lam, 120, 330, 10.0, R, 3.0, esc, con_tapa=True, con_agua=True)
    B.caja_iso(lam, be, 0, ef + h + et - 0.10, 0.6, 3.0, 0.10, capas=("ISO-TERRENO", "ISO-TERRENO", "ISO-TERRENO"), **kw)   # piso del retiro lado via
    # junta de dilatacion en la mitad
    for z in (0, ef + h + et):
        lam.poli([Tt(0, 1.5, z), Tt(be, 1.5, z)], "JUNTAS")
    lam.poli([Tt(be, 1.5, 0), Tt(be, 1.5, ef + h + et)], "JUNTAS"); lam.poli([Tt(0, 1.5, 0), Tt(0, 1.5, ef + h + et)], "JUNTAS")
    xt = Tt(be + 1.3, 3.0, ef + h + et + 0.3)
    lam.llamada(Tt(be / 2, 3.0, ef + h + et), (xt[0], xt[1] + 0.9), ["losa superior del colector = piso terminado (NPT +260.60)"], 1.8)
    lam.llamada(Tt(be, 1.5, ef + h + et), (xt[0], xt[1] + 0.6), ["junta de dilatacion cada 4.00 m (tecnopor 1\" + sello)"], 1.8)
    lam.llamada(Tt(xc, 3.0, ef + h + et + 0.5), (xt[0], xt[1] + 0.3), ["cerco perimetrico existente (lado predio); junta de tecnopor 1\" con el muro"], 1.8)
    lam.llamada(Tt(be - e / 2, 3.0, ef + h / 2), (xt[0], xt[1]), ["muro e=0.15, marco 3/8\" @0.20; altura interior 1.40 a 1.61 m"], 1.8)
    lam.llamada(Tt(be / 2, 3.0, ef / 2), (xt[0], xt[1] - 0.3), ["losa de fondo e=0.15 sobre solado e=0.05"], 1.8)
    lam.llamada(Tt(be + 0.4, 3.0, ef + h + et), (xt[0], xt[1] - 0.6), ["piso del retiro (lado via) nivelado hasta la cota de la losa"], 1.8)
    lam.titulo_vista(150, 215, "ISOMETRICO 1: COLECTOR JUNTO AL CERCO", "tramo tipico de 3.00 m - sin escala", 140)
    # ISO 2: registro explotado
    o = lam.P(520, 330); esc = 1.2
    Tt = lambda x, y, z: (o[0] + B.iso(x, y, z)[0] * esc, o[1] + B.iso(x, y, z)[1] * esc); kw = dict(origen=o, esc=esc)
    B.caja_iso(lam, 0, 0, 0, be, 1.5, 0.10, capas=("ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2"), **kw)
    # abertura (dibujada como rectangulo sobre la losa)
    ab = [Tt(be / 2 - 0.35, 0.75 - 0.35, 0.10), Tt(be / 2 + 0.35, 0.75 - 0.35, 0.10), Tt(be / 2 + 0.35, 0.75 + 0.35, 0.10), Tt(be / 2 - 0.35, 0.75 + 0.35, 0.10)]
    lam.solido([ab[0], ab[1], ab[3], ab[2]], "ISO-CONCRETO-LAT2"); lam.poli(ab, "ISO-ARISTAS", cerrada=True)
    B.caja_iso(lam, be / 2 - 0.35, 0.75 - 0.35, 0.10, 0.70, 0.70, 0.02, solido=False, capa_aristas="MARCO-METALICO", **kw)
    B.caja_iso(lam, be / 2 - 0.30, 0.75 - 0.30, 0.10, 0.60, 0.60, 0.02, solido=False, capa_aristas="MARCO-METALICO", **kw)
    B.caja_iso(lam, be / 2 - 0.34, 0.75 - 0.34, 0.55, 0.68, 0.68, 0.08, capas=("ISO-TAPA", "ISO-TAPA", "ISO-TAPA"), **kw)
    B.caja_iso(lam, be / 2 - 0.34, 0.75 - 0.34, 0.95, 0.68, 0.68, 0.02, solido=False, capa_aristas="MARCO-METALICO", **kw)
    B.caja_iso(lam, be / 2 - 0.30, 0.75 - 0.30, 0.95, 0.60, 0.60, 0.02, solido=False, capa_aristas="MARCO-METALICO", **kw)
    for dx_ in (-0.12, 0.12):
        p1 = Tt(be / 2 + dx_, 0.75, 1.0); lam.circulo(p1, 0.02 * esc, "MARCO-METALICO")
    xt = Tt(be + 0.9, 1.5, 1.2)
    lam.llamada(Tt(be / 2, 0.75 + 0.34, 0.97), (xt[0], xt[1] + 0.5), ["marco de tapa L 1 1/2\"x1 1/2\"x1/8\" (0.68 x 0.68)"], 1.8)
    lam.llamada(Tt(be / 2 + 0.34, 0.75, 0.6), (xt[0], xt[1] + 0.2), ["tapa de concreto 0.68 x 0.68 x 0.08 con asas"], 1.8)
    lam.llamada(Tt(be / 2 + 0.35, 0.75, 0.12), (xt[0], xt[1] - 0.1), ["contramarco L 2\"x2\"x3/16\" con 8 anclajes 3/8\", enrasado con NPT"], 1.8)
    lam.llamada(Tt(be / 2 + 0.35, 1.1, 0.0), (xt[0], xt[1] - 0.4), ["abertura 0.70 x 0.70 en la losa; borde engrosado 0.15 x 0.10 y refuerzo 1/2\""], 1.8)
    lam.titulo_vista(560, 215, "ISOMETRICO 2: REGISTRO DE LIMPIEZA", "vista explotada: contramarco, tapa y marco - sin escala", 140)
    # ISO 3: empalme de cuneta (colector cortado + cuneta entrando por ventana + cerco con abertura)
    o = lam.P(150, 95); esc = 0.9
    Tt = lambda x, y, z: (o[0] + B.iso(x, y, z)[0] * esc, o[1] + B.iso(x, y, z)[1] * esc); kw = dict(origen=o, esc=esc)
    g = geometria(11.27); h = g["h"]; c02 = [c for c in R["cunetas"] if c["perfil"] == "02"][0]; Hc = D["NPT"] - c02["NCF_fin"]
    zc = ef + h + et - Hc; xq = -D["junta_cerco"] - 0.15 - 0.9   # inicio de la cuneta (lado predio, lejano)
    # cuneta (fondo y dos muros) desde el predio hasta el muro del colector, pasando por el cerco
    B.caja_iso(lam, xq, 0.7, zc - 0.10, 0.9 + 0.15 + D["junta_cerco"] + e, 0.60, 0.10, capas=("ISO-CUNETA", "ISO-CUNETA", "ISO-CUNETA"), **kw)
    B.caja_iso(lam, xq, 0.7, zc, 0.9 + 0.15 + D["junta_cerco"], 0.10, Hc, capas=("ISO-CUNETA", "ISO-CUNETA", "ISO-CUNETA"), **kw)
    B.caja_iso(lam, xq, 1.2, zc, 0.9 + 0.15 + D["junta_cerco"], 0.10, Hc, capas=("ISO-CUNETA", "ISO-CUNETA", "ISO-CUNETA"), **kw)
    xc = -D["junta_cerco"] - 0.15
    B.caja_iso(lam, xc, 0, ef + h + et - 0.9, 0.15, 0.7, 1.5, capas=("ISO-CERCO", "ISO-CERCO", "ISO-CERCO"), **kw)
    B.caja_iso(lam, xc, 1.3, ef + h + et - 0.9, 0.15, 0.7, 1.5, capas=("ISO-CERCO", "ISO-CERCO", "ISO-CERCO"), **kw)
    iso_colector(lam, 150, 95, 11.27, R, 2.0, esc, con_tapa=False, con_agua=True)
    # ventana en la cara interior del muro lejano (x = e): 0.40 x (zc .. zt)
    v = [Tt(e, 0.8, zc), Tt(e, 1.2, zc), Tt(e, 1.2, ef + h), Tt(e, 0.8, ef + h)]
    lam.solido([v[0], v[1], v[3], v[2]], "ISO-CONCRETO-SUP"); lam.poli(v, "ISO-ARISTAS", cerrada=True)
    B.caja_iso(lam, be / 2 - 0.34, 1.0 - 0.34, ef + h + et, 0.68, 0.68, 0.012, capas=("ISO-TAPA", "ISO-TAPA", "ISO-TAPA"), **kw)
    xt = Tt(be + 1.2, 2.0, ef + h + et + 0.2)
    lam.llamada(Tt(xq + 0.3, 1.0, zc + Hc), (xt[0], xt[1] + 0.8), ["cuneta de arquitectura 0.40 x H que llega al frente (lado predio)"], 1.8)
    lam.llamada(Tt(xc + 0.15, 1.0, zc + Hc + 0.5), (xt[0], xt[1] + 0.5), ["paso por el cerco (abertura 0.60) con junta de tecnopor 1\""], 1.8)
    lam.llamada(Tt(e, 1.0, zc + 0.3), (xt[0], xt[1] + 0.2), ["ventana 0.40 x (altura hasta la losa) en el muro lado predio"], 1.8)
    lam.llamada(Tt(be / 2, 1.0, ef + h + et + 0.012), (xt[0], xt[1] - 0.1), ["registro encima del empalme"], 1.8)
    lam.llamada(Tt(be / 2, 2.0, ef + 0.3), (xt[0], xt[1] - 0.4), ["caida libre al fondo del colector"], 1.8)
    lam.titulo_vista(180, 30, "ISOMETRICO 3: EMPALME DE CUNETA", "cunetas Ejes 01, 02, 06, 07, 11 y 12 - losa superior cortada - sin escala", 140)
    # ISO 4: caja de caida (poza) con el colector llegando y el R-01
    o = lam.P(470, 130); esc = 0.6
    Tt = lambda x, y, z: (o[0] + B.iso(x, y, z)[0] * esc, o[1] + B.iso(x, y, z)[1] * esc); kw = dict(origen=o, esc=esc)
    Li, Bi = D["CC_poza_largo"], D["CC_ancho"]; piso = D["CF_R01"] - D["CC_poza_prof"]; zb = dz.fondo(dz.P_BRINK); top = D["NPT"]
    # coordenadas: x transversal (0..Bi+2e), y longitudinal (flujo hacia -y: colector en y>Li, poza 0..Li), z desde piso-ef
    z0 = piso - ef
    B.caja_iso(lam, 0, 0, 0, Bi + 2 * e, Li + e, ef, **kw)                                         # losa de fondo de la poza
    B.caja_iso(lam, 0, 0, ef, e, Li + e, top - et - piso, **kw)                                     # muro izquierdo (lejano)
    # cara interior del muro lejano
    pts = [Tt(e, 0, ef), Tt(e, Li + e, ef), Tt(e, Li + e, ef + top - et - piso), Tt(e, 0, ef + top - et - piso)]
    lam.solido([pts[0], pts[1], pts[3], pts[2]], "ISO-CONCRETO-LAT2"); lam.poli(pts, "ISO-ARISTAS", cerrada=True)
    B.caja_iso(lam, e, 0, ef, Bi, e, top - et - piso, **kw)                                         # muro aguas abajo (y=0) con umbral
    B.caja_iso(lam, e, e, ef, Bi, 0.25, D["CC_poza_prof"], capas=("ISO-PIEDRA", "ISO-PIEDRA", "ISO-PIEDRA"), **kw)   # umbral
    # agua en la poza
    NAr = D["NA_R01"]
    pa = [Tt(e, e, ef + NAr - piso), Tt(Bi + e, e, ef + NAr - piso), Tt(Bi + e, Li, ef + NAr - piso), Tt(e, Li, ef + NAr - piso)]
    lam.solido([pa[0], pa[1], pa[3], pa[2]], "ISO-AGUA"); lam.poli(pa, "ISO-ARISTAS", cerrada=True)
    # colector llegando (y > Li): b 0.80 centrado
    xc0 = (Bi + 2 * e) / 2 - be / 2
    B.caja_iso(lam, xc0, Li, zb - ef - z0, be, 2.0, ef, **kw)
    B.caja_iso(lam, xc0, Li, zb - z0, e, 2.0, top - et - zb, **kw)
    B.caja_iso(lam, xc0 + be - e, Li, zb - z0, e, 2.0, top - et - zb, **kw)
    yw = perfil_en(R, dz.P_BRINK - 1.0, "NA") - zb
    pw = [Tt(xc0 + e, Li, zb - z0 + yw), Tt(xc0 + be - e, Li, zb - z0 + yw), Tt(xc0 + be - e, Li + 2.0, zb - z0 + yw), Tt(xc0 + e, Li + 2.0, zb - z0 + yw)]
    lam.solido([pw[0], pw[1], pw[3], pw[2]], "ISO-AGUA"); lam.poli(pw, "ISO-ARISTAS", cerrada=True)
    # muro de cabecera (brink) a ambos lados del canal
    B.caja_iso(lam, e, Li, ef, xc0 - e, e, top - et - piso, **kw); B.caja_iso(lam, xc0 + be, Li, ef, Bi + e - xc0 - be, e, top - et - piso, **kw)
    B.caja_iso(lam, Bi + e, 0, ef, e, Li + e, top - et - piso, **kw)                                 # muro derecho (cercano)
    B.caja_iso(lam, xc0, Li + e, zb - z0 + top - et - zb, be, 2.0 - e, et, capas=("ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2"), **kw)   # losa colector
    # losa superior de la caja (parcial, cortada para ver la poza): solo franja aguas abajo 1.0 m
    B.caja_iso(lam, 0, 0, ef + top - et - piso, Bi + 2 * e, 1.0, et, capas=("ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2"), **kw)
    B.caja_iso(lam, (Bi + 2 * e) / 2 - 0.34, 0.16, ef + top - piso, 0.68, 0.68, 0.012, capas=("ISO-TAPA", "ISO-TAPA", "ISO-TAPA"), **kw)
    xt = Tt(Bi + 2 * e + 1.8, Li + 2.0, top - piso + 0.2)
    lam.llamada(Tt(xc0 + be / 2, Li + 1.0, zb - z0 + yw), (xt[0], xt[1] + 1.0), ["colector b=0.80 llega al brink (CF %.3f)" % zb], 1.8)
    lam.llamada(Tt(e + Bi / 2, Li - 0.5, ef + NAr - piso), (xt[0], xt[1] + 0.6), ["poza de disipacion 1.50 x 3.50, piso 258.32; resalto ahogado"], 1.8)
    lam.llamada(Tt(e + Bi / 2, e + 0.12, ef + D["CC_poza_prof"]), (xt[0], xt[1] + 0.2), ["umbral 0.25 x 0.40, corona 258.72 = fondo del R-01 del CAR Mujeres"], 1.8)
    lam.llamada(Tt(e + Bi / 2, 0, ef + 0.9), (xt[0], xt[1] - 0.2), ["ventana de salida 1.50 x 0.60 hacia el R-01 (junta 1\")"], 1.8)
    lam.llamada(Tt((Bi + 2 * e) / 2, 0.5, ef + top - piso + 0.012), (xt[0], xt[1] - 0.6), ["losa superior e=0.10 (cortada en el dibujo) con 2 registros"], 1.8)
    lam.titulo_vista(520, 30, "ISOMETRICO 4: CAJA DE CAIDA CON POZA", "entrega al R-01 del CAR Mujeres - losa superior cortada - sin escala", 140)
    lam.leyenda(650, 330, [("relleno", "ISO-CONCRETO-SUP", "concreto armado"), ("relleno", "ISO-TAPA", "tapa de registro"), ("relleno", "ISO-AGUA", "agua"), ("relleno", "ISO-CUNETA", "cuneta que llega"),
                           ("relleno", "ISO-CERCO", "cerco perimetrico existente"), ("relleno", "ISO-TERRENO", "piso / relleno del retiro"), ("relleno", "ISO-PIEDRA", "umbral de la poza"), ("linea", "MARCO-METALICO", "marco y contramarco metalico")], 1.8)
    return lam


# ----------------------------------------------------------------------------
def dp10(doc, ox, oy, R, T):
    """Isometrico general con el trazo real (recta frontal, dos quiebres a 45 grados, recta final), cajas, registros,
    cunetas que llegan y el colector receptor. Exageracion vertical x2 para leer el relieve."""
    from dxf_planta import offset_poli
    lam = B.Lamina(doc, ox, oy, 200, "DP-10", "ISOMETRICO GENERAL DEL COLECTOR PLUVIAL", "VISTA DE CONJUNTO CON EL TRAZO REAL: CAJA DE LLEGADA, COLECTOR CUBIERTO, REGISTROS, EMPALMES DE CUNETAS, QUIEBRES A 45 GRADOS Y CAJA DE CAIDA")
    f = lam.f; e = D["e_muro"]; ef = D["e_fondo"]; et = D["e_losa"]; be = D["b_ext"]
    o = lam.P(300, 330); esc = 1.0; EX = 2.0
    def UV(p):
        x, y, _ = dz.eje_local(p); return (dz.X_NE - x, y - dz.Y_EJE)      # u a lo largo del frente, v hacia el predio (+)
    def Tt(u, v, z):
        px, py = B.iso(u, v, z, EX); return (o[0] + px * esc, o[1] + py * esc)
    ztop = D["NPT"] - 258.0
    zb = lambda p: dz.fondo(min(p, dz.P_BRINK)) - ef - 258.0
    def cara(pts3, capa, aristas=True):
        pts = [Tt(*q) for q in pts3]
        if len(pts) == 4: lam.solido([pts[0], pts[1], pts[3], pts[2]], capa)
        else: lam.relleno(pts, capa)
        if aristas: lam.poli(pts, "ISO-ARISTAS", cerrada=True)
    def caja(u1, u2, v1, v2, z1, z2, capas=("ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2"), frente_u=True):
        """Prisma alineado con u, v; caras visibles: superior, lateral +v (frente) y extremo +u (lateral)."""
        if frente_u: cara([(u2, v1, z1), (u2, v2, z1), (u2, v2, z2), (u2, v1, z2)], capas[2])
        cara([(u1, v2, z1), (u2, v2, z1), (u2, v2, z2), (u1, v2, z2)], capas[1])
        cara([(u1, v1, z2), (u2, v1, z2), (u2, v2, z2), (u1, v2, z2)], capas[0])
    # ---------- caja de llegada CL (lado lejano, se dibuja primero)
    v0 = UV(0.0)[1]
    caja(-D["CL_largo"] - 2 * e, 0.0, v0 - D["CL_ancho"] / 2 - e, v0 + D["CL_ancho"] / 2 + e, D["CF0"] - D["CL_poza"] - ef - 258.0, D["NPT_CL"] - 258.0, frente_u=False)
    # ---------- colector con el trazo real: caras laterales lado predio (+v) de cada tramo recto y cara superior continua
    progs = [0.0, dz.P_B1, dz.P_B2, dz.P_BRINK]
    ejes = [UV(p) for p in progs]
    izq = offset_poli(ejes, be / 2); der = offset_poli(ejes, -be / 2)
    for k in range(3):
        a, b_ = progs[k], progs[k + 1]
        cara([(izq[k][0], izq[k][1], zb(a)), (izq[k + 1][0], izq[k + 1][1], zb(b_)), (izq[k + 1][0], izq[k + 1][1], ztop), (izq[k][0], izq[k][1], ztop)], "ISO-CONCRETO-LAT1")
    cara([(q[0], q[1], ztop) for q in izq] + [(q[0], q[1], ztop) for q in reversed(der)], "ISO-CONCRETO-SUP")
    # cara interior visible en los quiebres (lado via, -v) del tramo diagonal: lateral oscuro
    cara([(der[1][0], der[1][1], zb(progs[1])), (der[2][0], der[2][1], zb(progs[2])), (der[2][0], der[2][1], ztop), (der[1][0], der[1][1], ztop)], "ISO-CONCRETO-LAT2")
    # ---------- caja de caida CC y colector receptor (lado cercano)
    ub, vf = UV(dz.P_BRINK)[0], UV(dz.P_FIN)[1]; uf = UV(dz.P_FIN)[0]; zcc = D["CF_R01"] - D["CC_poza_prof"] - ef - 258.0
    caja(ub - e, uf + e, vf - D["CC_ancho"] / 2 - e, vf + D["CC_ancho"] / 2 + e, zcc, ztop)
    caja(uf + e, uf + e + 6.0, vf - D["b_wilma"] / 2 - 0.10, vf + D["b_wilma"] / 2 + 0.10, D["CF_R01"] - 0.15 - 258.0, D["NPT_wilma"] - 258.0, capas=("ISO-TERRENO", "ISO-TERRENO", "ISO-TERRENO"))
    # ---------- registros (tapas sobre la losa)
    def tapa(p, nm=None, du=0.0):
        u, v = UV(p); u += du
        cara([(u - 0.34, v - 0.34, ztop), (u + 0.34, v - 0.34, ztop), (u + 0.34, v + 0.34, ztop), (u - 0.34, v + 0.34, ztop)], "ISO-TAPA")
        if nm:
            q = Tt(u, v - 0.34, ztop); lam.texto((q[0], q[1] - 1.6 * f), nm, 1.6, "REGISTRO", TA.TOP_CENTER)
    for rg in R["registros"]:
        if rg["nombre"] not in ("CL", "CC"): tapa(rg["prog"], rg["nombre"])
    tapa(0.0, "CL", du=-0.75); tapa(dz.P_BRINK + 0.6, "CC"); tapa(dz.P_FIN - 1.0)
    # ---------- cunetas que llegan desde el predio (+v): prisma 0.60 x H que entra por la ventana del muro
    for c in R["cunetas"]:
        p = c["prog"]; u, v = UV(p); zc = c["NCF_fin"] - 258.0; Lq = 3.0 + c["prolong"]
        vb = v + be / 2 - 0.02
        caja(u - 0.30, u + 0.30, vb, vb + Lq, zc - 0.10, ztop, capas=("ISO-CUNETA", "ISO-CUNETA", "ISO-CUNETA"))
        q = Tt(u, vb + Lq, ztop); lam.texto((q[0], q[1] + 2 * f), "Eje %s (cuneta)" % c["perfil"].lstrip("0"), 1.6, "CUNETA", TA.BOTTOM_CENTER)
    # ---------- cerco perimetrico (referencia, lado predio, detras de las cunetas): franja baja para no tapar
    u1, v1 = UV(0.0); u2 = dz.P_B1
    # ---------- textos
    for p, nm in ((dz.P_B1, "QUIEBRE 1 (45 grados) - RS-06"), (dz.P_B2, "QUIEBRE 2 (45 grados) - RS-07")):
        u, v = UV(p); q = Tt(u, v - be / 2, zb(p)); lam.llamada(q, (q[0] - 10 * f, q[1] - 14 * f), [nm], 1.8, al=TA.RIGHT)
    q = Tt(-D["CL_largo"], v0 + D["CL_ancho"] / 2 + e, ztop); lam.llamada(q, (q[0] - 12 * f, q[1] + 16 * f), ["CAJA DE LLEGADA CL (0+000): llegada de CAR Varones (CUI 2705619)", "poza 0.30 m con colchon de agua"], 1.8, al=TA.RIGHT)
    q = Tt(uf, vf - D["CC_ancho"] / 2 - e, ztop); lam.llamada(q, (q[0] - 24 * f, q[1] - 26 * f), ["CAJA DE CAIDA CC: poza de disipacion 1.50 x 3.50, piso 258.32", "entrega al R-01 del CAR Mujeres (CUI 2717013)"], 1.8, al=TA.RIGHT)
    q = Tt(uf + e + 4.0, vf + D["b_wilma"] / 2, D["NPT_wilma"] - 258.0); lam.llamada(q, (q[0] + 6 * f, q[1] + 14 * f), ["colector del CAR Mujeres b=1.50 (referencia)"], 1.8, al=TA.LEFT)
    q = Tt(30.0, v0 - be / 2, ztop); lam.llamada(q, (q[0] - 6 * f, q[1] - 18 * f), ["COLECTOR CUBIERTO b=0.80 m, S=0.30 %, losa superior a nivel del piso terminado +260.60", "registros cada <= 12 m y en cada llegada de cuneta"], 1.8, al=TA.RIGHT)
    for z in R["zonas"]:
        u, v = UV((z["p1"] + z["p2"]) / 2); q = Tt(u, v, ztop); lam.texto((q[0], q[1] + 3 * f), "CRUCE DE %s" % ("CAMIONES" if z["tipo"] == "CAMION" else "MOTOS"), 1.5, "CRUCE-VEHICULAR", TA.BOTTOM_CENTER)
    q = Tt(-2.0, v0 - 2.0, ztop); lam.texto((q[0], q[1]), "0+000", 1.6, "PROGRESIVAS", TA.RIGHT)
    for p in (10.0, 20.0, 30.0, 40.0, 50.0):
        u, v = UV(p); q = Tt(u, v - be / 2 - 0.3, ztop); lam.texto((q[0], q[1] - 1.5 * f), prog_txt(p), 1.4, "PROGRESIVAS", TA.TOP_CENTER)
    lam.texto(lam.P(40, 90), "Vista isometrica de conjunto con el trazo real (recta frontal, dos quiebres a 45 grados y recta final hasta la caja de caida); escala vertical ampliada x2 para leer el relieve. Medidas reales en las laminas DP-01 a DP-09.", 2.0, "TEXTOS-NOTAS")
    lam.leyenda(40, 170, [("relleno", "ISO-CONCRETO-SUP", "colector y cajas de concreto armado (losa superior)"), ("relleno", "ISO-CONCRETO-LAT1", "muro lado predio"), ("relleno", "ISO-TAPA", "tapa de registro"),
                          ("relleno", "ISO-CUNETA", "cuneta que llega (0.40 x H, muros 0.10)"), ("relleno", "ISO-TERRENO", "colector receptor (CAR Mujeres), referencia")], 1.8)
    return lam


def todas(doc, ox, oy, R, T):
    return [dp07(doc, ox, oy, R, T), dp09(doc, ox + 30, oy, R, T), dp10(doc, ox + 60, oy, R, T)]
