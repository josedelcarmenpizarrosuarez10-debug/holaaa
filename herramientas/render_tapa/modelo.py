"""Modelo 3D del registro de limpieza con tapa 0.68 x 0.68 (lamina DP-06B). Unidades: m. z = 0 en NPT."""
import numpy as np

IN = 0.0254
# angulos
CM_L, CM_T = 2 * IN, 3 / 16 * IN          # contramarco L 2"x2"x3/16"
MT_L, MT_T = 1.5 * IN, 1 / 8 * IN         # marco de tapa L 1 1/2"x1 1/2"x1/8"
D38, D12 = 3 / 8 * IN, 1 / 2 * IN
LOSA = 0.10; ENG = 0.10                   # losa superior y borde engrosado (bajo la losa)
REB = 0.70 / 2; LUZ = 0.60 / 2; RING = 0.90 / 2
TAPA = 0.68 / 2; ET = 0.08
BI, BW = 0.40, 0.15                       # interior del colector (medio ancho) y espesor de muro
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

def anillo(p, r_in, r_out, z0, z1, lim=None):
    """marco cuadrado entre r_in y r_out (medios lados)"""
    p.box(-r_out, r_out, r_in, r_out, z0, z1); p.box(-r_out, r_out, -r_out, -r_in, z0, z1)
    p.box(r_in, r_out, -r_in, r_in, z0, z1); p.box(-r_out, -r_in, -r_in, r_in, z0, z1)

def modelo():
    P = {}
    # 1. losa superior del colector con rebaje y luz libre, muros
    L = Parte('losa', 'concreto')
    X = BI + BW
    # capa superior (rebaje 0.70) z -0.08..0
    L.box(-X, X, REB, HY, -ET, 0); L.box(-X, X, -HY, -REB, -ET, 0)
    L.box(REB, X, -REB, REB, -ET, 0); L.box(-X, -REB, -REB, REB, -ET, 0)
    # capa inferior (luz 0.60) z -0.10..-0.08
    L.box(-X, X, LUZ, HY, -LOSA, -ET); L.box(-X, X, -HY, -LUZ, -LOSA, -ET)
    L.box(LUZ, X, -LUZ, LUZ, -LOSA, -ET); L.box(-X, -LUZ, -LUZ, LUZ, -LOSA, -ET)
    # borde engrosado 0.15 x 0.10 bajo la losa (de 0.60 a 0.90)
    E = Parte('engrosado', 'concreto')
    E.box(-BI, BI, LUZ, RING, -LOSA - ENG, -LOSA); E.box(-BI, BI, -RING, -LUZ, -LOSA - ENG, -LOSA)
    E.box(LUZ, BI, -LUZ, LUZ, -LOSA - ENG, -LOSA); E.box(-BI, -LUZ, -LUZ, LUZ, -LOSA - ENG, -LOSA)
    # muros
    M = Parte('muros', 'concreto')
    M.box(BI, X, -HY, HY, -LOSA - HW, -LOSA); M.box(-X, -BI, -HY, HY, -LOSA - HW, -LOSA)
    P['losa'], P['engrosado'], P['muros'] = L, E, M
    # 2. refuerzo de borde 1/2": 2 barras por lado, L = 1.40 (en x: 1.10 + ganchos de 0.15 dentro de los muros)
    R = Parte('refuerzo', 'acero')
    c = (LUZ + RING) / 2
    for z in (-0.045, -LOSA - ENG + 0.045):
        for s in (-1, 1):
            R.bar((s * c, -0.70, z), (s * c, 0.70, z), D12)                  # barras en y (eje del colector)
            xh = X - 0.04
            R.poly([(-xh, s * c, z - 0.15 if z > -0.1 else z + 0.15), (-xh, s * c, z), (xh, s * c, z),
                    (xh, s * c, z - 0.15 if z > -0.1 else z + 0.15)], D12)
    P['refuerzo'] = R
    # 3. contramarco L 2"x2"x3/16": ala vertical en la cara del rebaje, ala horizontal enrasada con NPT hacia afuera
    C = Parte('contramarco', 'angulo')
    e = 0.0004
    anillo(C, REB, REB + CM_T, -CM_L, e)                 # ala vertical
    anillo(C, REB, REB + CM_L, -CM_T, e)                 # ala horizontal
    P['contramarco'] = C
    A = Parte('anclajes', 'acero')                       # 8 anclajes 3/8" L = 0.20 en L, soldados al ala vertical
    for t in (-0.125, 0.125):
        for sx, sy, ax in ((1, t, 'x'), (-1, t, 'x'), (t, 1, 'y'), (t, -1, 'y')):
            if ax == 'x':
                x0 = sx * (REB + CM_T + D38 / 2); x1 = sx * (REB + 0.15)
                A.poly([(x0, sy, -0.03), (x1, sy, -0.03), (x1, sy, -0.08)], D38)
            else:
                y0 = sy * (REB + CM_T + D38 / 2); y1 = sy * (REB + 0.15)
                A.poly([(sx, y0, -0.03), (sx, y1, -0.03), (sx, y1, -0.08)], D38)
    P['anclajes'] = A
    # 4. tapa: concreto con bolsillos para asas
    T = Parte('tapa', 'tapa')
    ri = TAPA - MT_T
    T.box(-ri, ri, -ri, ri, -ET, -0.03)
    py0, py1, px = 0.195, 0.245, 0.08
    T.box(-ri, ri, py1, ri - 0, -0.03, -MT_T)
    T.box(-ri, ri, -ri, -py1, -0.03, -MT_T)
    T.box(-ri, ri, -py0, py0, -0.03, -MT_T)
    for s in (-1, 1):
        lo, hi = sorted((s * py0, s * py1))
        T.box(-ri, -px, lo, hi, -0.03, -MT_T); T.box(px, ri, lo, hi, -0.03, -MT_T)
        T.box(-px, px, lo, hi, -0.03, -0.026)          # fondo del bolsillo
    # capa superior bajo el ala horizontal del marco (rellena el resto)
    P['tapa'] = T
    # 5. marco de tapa L 1 1/2"x1 1/2"x1/8": ala vertical en el canto, ala horizontal en la cara superior
    MT = Parte('marco', 'angulo')
    anillo(MT, TAPA - MT_T, TAPA, -MT_L, 0)
    anillo(MT, TAPA - MT_L, TAPA, -MT_T, 0)
    P['marco'] = MT
    # 6. parrilla 3/8" @0.10: 7 + 7 barras L = 0.62
    G = Parte('parrilla', 'acero')
    for k in range(7):
        u = -0.30 + 0.10 * k
        G.bar((-0.31, u, -ET + 0.025), (0.31, u, -ET + 0.025), D38)
        G.bar((u, -0.31, -ET + 0.025 + D38), (u, 0.31, -ET + 0.025 + D38), D38)
    P['parrilla'] = G
    # 7. asas 3/8" liso (2): agarradera en el bolsillo, patas y ganchos dentro del concreto (0.40 desarrollado)
    H = Parte('asas', 'liso')
    for s in (-1, 1):
        y = s * (py0 + py1) / 2
        H.poly([(-0.155, y, -ET + 0.02), (-0.06, y, -ET + 0.02), (-0.06, y, -0.015), (0.06, y, -0.015),
                (0.06, y, -ET + 0.02), (0.155, y, -ET + 0.02)], D38)
    P['asas'] = H
    return P
