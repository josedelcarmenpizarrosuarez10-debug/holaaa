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
    # abertura 0.70 x 0.70 en todo el espesor de la losa (z 0 a -0.10)
    L.box(-X, X, REB, HY, -LOSA, 0); L.box(-X, X, -HY, -REB, -LOSA, 0)
    L.box(REB, X, -REB, REB, -LOSA, 0); L.box(-X, -REB, -REB, REB, -LOSA, 0)
    # borde engrosado 0.15 x 0.10 bajo la losa (de la luz 0.60 a 0.90); rellena tambien bajo el asiento del contramarco
    E = Parte('engrosado', 'concreto')
    zt = -ET - CM_T; zv = -ET - CM_L
    for (ri_, ro_, z0, z1) in ((LUZ, RING, -LOSA - ENG, zv), (REB, RING, zv, -LOSA), (LUZ, REB - CM_T, zv, zt)):
        ro2 = min(ro_, BI) if ro_ > BI else ro_
        E.box(-BI, BI, ri_, ro_, z0, z1); E.box(-BI, BI, -ro_, -ri_, z0, z1)
        E.box(ri_, min(ro_, BI), -ri_, ri_, z0, z1); E.box(-min(ro_, BI), -ri_, -ri_, ri_, z0, z1)
    # muros
    M = Parte('muros', 'concreto')
    M.box(BI, X, -HY, HY, -LOSA - HW, -LOSA); M.box(-X, -BI, -HY, HY, -LOSA - HW, -LOSA)
    P['losa'], P['engrosado'], P['muros'] = L, E, M
    # 2. refuerzo de borde 1/2": 2 barras por lado, L = 1.40 (en x: 1.10 + ganchos de 0.15 dentro de los muros)
    R = Parte('refuerzo', 'acero')
    c = 0.40                                   # a 0.05 de la cara de la abertura
    for z in (-0.045, -LOSA - ENG + 0.045):
        for s in (-1, 1):
            R.bar((s * c, -0.70, z), (s * c, 0.70, z), D12)                  # barras en y (eje del colector)
            xh = X - 0.04
            R.poly([(-xh, s * c, z - 0.15 if z > -0.1 else z + 0.15), (-xh, s * c, z), (xh, s * c, z),
                    (xh, s * c, z - 0.15 if z > -0.1 else z + 0.15)], D12)
    P['refuerzo'] = R
    # 3. contramarco L 2"x2"x3/16": asiento de la tapa a 0.08 bajo el NPT; ala horizontal hacia adentro (asiento),
    #    ala vertical hacia abajo con su cara exterior al ras de la abertura
    C = Parte('contramarco', 'angulo')
    anillo(C, REB - CM_L, REB, -ET - CM_T, -ET)          # ala horizontal (asiento)
    anillo(C, REB - CM_T, REB, -ET - CM_L, -ET - CM_T)    # ala vertical
    P['contramarco'] = C
    A = Parte('anclajes', 'acero')                       # 8 anclajes 3/8" L = 0.20 soldados al ala vertical, inclinados hacia la losa
    for t in (-0.125, 0.125):
        for s_ in (-1, 1):
            A.bar((s_ * (REB + D38 / 2), t, -0.115), (s_ * (REB + 0.18), t, -0.025), D38)
            A.bar((t, s_ * (REB + D38 / 2), -0.115), (t, s_ * (REB + 0.18), -0.025), D38)
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
