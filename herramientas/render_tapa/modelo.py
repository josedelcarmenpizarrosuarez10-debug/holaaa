"""Modelo 3D del registro de limpieza con TAPA CIEGA de concreto armado 0.68 x 0.68 x 0.08 (lamina DP-06B rev. 02).
Sin marco ni contramarco metalico: la tapa asienta en un rebaje de concreto 0.70 x 0.70 x 0.08 de la losa; luz libre
0.60 x 0.60; 2 asas de fierro liso 1/2" en cajuelas. Unidades: m. z = 0 en NPT.
Variables de entorno: COLECTOR_B (ancho interior: Refugio 0.80, CAR Varones 0.60, CAR Mujeres 1.50) y MURO_E (0.15; Mujeres 0.10)."""
import os
import numpy as np

IN = 0.0254
D38, D12 = 3 / 8 * IN, 1 / 2 * IN
LOSA = 0.10; ENG = 0.10                   # losa superior y borde engrosado (bajo la losa)
REB = 0.70 / 2                            # medio lado del rebaje (asiento de la tapa)
LUZ = 0.60 / 2                            # media luz libre bajo el rebaje
RING = 0.90 / 2                           # borde engrosado de la luz libre a 0.90
TAPA = 0.68 / 2; ET = 0.08                # tapa ciega; su espesor es la profundidad del rebaje
BI = float(os.environ.get("COLECTOR_B", "0.80")) / 2   # interior del colector (medio ancho)
BW = float(os.environ.get("MURO_E", "0.15"))           # espesor de muro
MURO_APOYO = BI <= LUZ + 1e-6             # colector tan angosto como la luz (CAR Varones): los muros son el asiento en los lados largos
C_BORDE = 0.40                            # refuerzo de borde 1/2": 2 barras por lado
GANCHO = round((1.40 - 2 * (BI + BW - 0.04)) / 2, 2)   # ganchos de las barras transversales de borde (L total = 1.40)
YA, AG, PATA, GAN = 0.20, 0.075, 0.02, 0.15            # asas: eje, medio agarre, pata, gancho (desarrollo 0.49 ~ 0.50)
CJX, CJY, CJZ = 0.095, 0.03, 0.03                      # cajuela del asa 0.19 x 0.06 x 0.03
ZA = -0.015                                            # agarre del asa
HY = 0.75                                 # medio largo del tramo mostrado
HW = 0.55                                 # altura visible de muro bajo la losa


class Parte:
    def __init__(self, clave, mat):
        self.clave, self.mat, self.boxes, self.bars = clave, mat, [], []
    def box(self, x0, x1, y0, y1, z0, z1): self.boxes.append([x0, x1, y0, y1, z0, z1]); return self
    def bar(self, p0, p1, d): self.bars.append((np.array(p0, float), np.array(p1, float), d)); return self
    def poly(self, pts, d):
        for a, b in zip(pts[:-1], pts[1:]): self.bar(a, b, d)
        return self


def marco_cuadrado(p, r_in, r_out, z0, z1, xlim):
    """anillo cuadrado entre r_in y r_out; en x hasta xlim (cara exterior del muro)"""
    p.box(-xlim, xlim, r_in, r_out, z0, z1); p.box(-xlim, xlim, -r_out, -r_in, z0, z1)
    p.box(r_in, xlim, -r_in, r_in, z0, z1); p.box(-xlim, -r_in, -r_in, r_in, z0, z1)


def modelo():
    P = {}
    X = BI + BW
    # 1. losa superior: rebaje 0.70 x 0.70 hasta 0.08 y luz 0.60 x 0.60 en los 0.02 restantes
    L = Parte('losa', 'concreto')
    L.box(-X, X, REB, HY, -ET, 0); L.box(-X, X, -HY, -REB, -ET, 0); L.box(REB, X, -REB, REB, -ET, 0); L.box(-X, -REB, -REB, REB, -ET, 0)
    L.box(-X, X, LUZ, HY, -LOSA, -ET); L.box(-X, X, -HY, -LUZ, -LOSA, -ET); L.box(LUZ, X, -LUZ, LUZ, -LOSA, -ET); L.box(-X, -LUZ, -LUZ, LUZ, -LOSA, -ET)
    # 2. borde engrosado 0.15 x 0.10 bajo la losa (de la luz libre a 0.90), solo entre muros
    E = Parte('engrosado', 'concreto')
    xs = min(RING, BI)
    E.box(-xs, xs, LUZ, RING, -LOSA - ENG, -LOSA); E.box(-xs, xs, -RING, -LUZ, -LOSA - ENG, -LOSA)
    if not MURO_APOYO:
        E.box(LUZ, xs, -LUZ, LUZ, -LOSA - ENG, -LOSA); E.box(-xs, -LUZ, -LUZ, LUZ, -LOSA - ENG, -LOSA)
    M = Parte('muros', 'concreto')
    M.box(BI, X, -HY, HY, -LOSA - HW, -LOSA); M.box(-X, -BI, -HY, HY, -LOSA - HW, -LOSA)
    P['losa'], P['engrosado'], P['muros'] = L, E, M
    # 3. refuerzo de borde 1/2": 2 barras por lado, L = 1.40 (las transversales con ganchos dentro de los muros)
    R = Parte('refuerzo', 'acero')
    for z in (-0.045, -LOSA - ENG + 0.045):
        for s in (-1, 1):
            R.bar((s * C_BORDE, -0.70, z), (s * C_BORDE, 0.70, z), D12)
            xh = X - 0.04
            R.poly([(-xh, s * C_BORDE, z - GANCHO), (-xh, s * C_BORDE, z), (xh, s * C_BORDE, z), (xh, s * C_BORDE, z - GANCHO)], D12)
    P['refuerzo'] = R
    # 4. tapa ciega con 2 cajuelas
    T = Parte('tapa', 'tapa')
    T.box(-TAPA, TAPA, -TAPA, TAPA, -ET, -CJZ)
    y1, y0 = YA + CJY, YA - CJY
    T.box(-TAPA, TAPA, y1, TAPA, -CJZ, 0); T.box(-TAPA, TAPA, -TAPA, -y1, -CJZ, 0); T.box(-TAPA, TAPA, -y0, y0, -CJZ, 0)
    for s in (-1, 1):
        lo, hi = sorted((s * y0, s * y1))
        T.box(-TAPA, -CJX, lo, hi, -CJZ, 0); T.box(CJX, TAPA, lo, hi, -CJZ, 0)
    P['tapa'] = T
    # 5. parrilla 3/8" @0.10: 7 + 7 barras L = 0.62
    G = Parte('parrilla', 'acero')
    for k in range(7):
        u = -0.30 + 0.10 * k
        G.bar((-0.31, u, -ET + 0.025), (0.31, u, -ET + 0.025), D38)
        G.bar((u, -0.31, -ET + 0.025 + D38), (u, 0.31, -ET + 0.025 + D38), D38)
    P['parrilla'] = G
    # 6. asas de fierro liso 1/2" (2): agarre en la cajuela, patas y ganchos amarrados sobre la parrilla
    H = Parte('asas', 'liso')
    for s in (-1, 1):
        y = s * YA
        H.poly([(-AG - GAN, y, ZA - PATA), (-AG, y, ZA - PATA), (-AG, y, ZA), (AG, y, ZA), (AG, y, ZA - PATA), (AG + GAN, y, ZA - PATA)], D12)
    P['asas'] = H
    return P
