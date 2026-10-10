"""Isometrico 3D sencillo para laminas DXF a escala real: caras planas en 3D, orden por profundidad (pintor),
sombreado por la normal y aristas solo en los bordes reales de cada cara. Proyeccion igual a dxf_base.iso:
el observador mira desde (+x, +y, +z); la profundidad de un punto es x + y + z.
"""
import math
import numpy as np

C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
LUZ = np.array([0.35, 0.55, 0.76]); LUZ = LUZ / np.linalg.norm(LUZ)
VISTA = np.array([1.0, 1.0, 1.0]) / math.sqrt(3)


def proy(p):
    x, y, z = p
    return (x * C30 - y * C30, -x * S30 - y * S30 + z)


class Escena:
    def __init__(self):
        self.caras = []            # (pts3d, rgb, bordes, sesgo, relleno, grupo)
        self.g = 0                 # grupo de dibujo: los grupos menores se pintan primero (atras)

    # ------------------------------------------------------------ primitivas
    def cara(self, pts, rgb, bordes=None, sesgo=0.0, relleno=True):
        pts = [np.asarray(p, float) for p in pts]
        self.caras.append((pts, rgb, bordes if bordes is not None else [True] * len(pts), sesgo, relleno, self.g))

    def quad(self, p0, p1, p2, p3, rgb, paso=0.05, sesgo=0.0, relleno=True, bordes=(True, True, True, True)):
        """Cuadrilatero plano subdividido en teselas de ~paso (para que el orden de pintor no falle)."""
        p0, p1, p2, p3 = (np.asarray(p, float) for p in (p0, p1, p2, p3))
        nu = max(1, int(math.ceil(np.linalg.norm(p1 - p0) / paso))); nv = max(1, int(math.ceil(np.linalg.norm(p3 - p0) / paso)))
        P = lambda u, v: (1 - u) * (1 - v) * p0 + u * (1 - v) * p1 + u * v * p2 + (1 - u) * v * p3
        for i in range(nu):
            for j in range(nv):
                a, b = i / nu, (i + 1) / nu; c, d = j / nv, (j + 1) / nv
                bd = [j == 0 and bordes[0], i == nu - 1 and bordes[1], j == nv - 1 and bordes[2], i == 0 and bordes[3]]
                self.cara([P(a, c), P(b, c), P(b, d), P(a, d)], rgb, bd, sesgo, relleno)

    def caja(self, x0, y0, z0, x1, y1, z1, rgb, paso=0.05, relleno=True):
        q = self.quad
        q((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), rgb, paso, relleno=relleno)      # arriba
        q((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), rgb, paso, relleno=relleno)      # abajo
        q((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1), rgb, paso, relleno=relleno)      # +y
        q((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), rgb, paso, relleno=relleno)      # -y
        q((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1), rgb, paso, relleno=relleno)      # +x
        q((x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1), rgb, paso, relleno=relleno)      # -x

    def cilindro(self, a, b, r, rgb, n=20, tapas=True, paso=0.08, aristas_gen=False, relleno=True, anillos=None):
        """Cilindro de a a b. anillos: separacion de lineas de rosca (solo aristas)."""
        a, b = np.asarray(a, float), np.asarray(b, float); ax = b - a; L = np.linalg.norm(ax); u = ax / L
        t = np.cross(u, [0, 0, 1.0]) if abs(u[2]) < 0.9 else np.cross(u, [1.0, 0, 0]); t /= np.linalg.norm(t); s = np.cross(u, t)
        ang = [2 * math.pi * k / n for k in range(n + 1)]
        ring = lambda c, k: c + r * (math.cos(ang[k]) * t + math.sin(ang[k]) * s)
        m = max(1, int(math.ceil(L / paso)))
        for j in range(m):
            c0, c1 = a + ax * j / m, a + ax * (j + 1) / m
            for k in range(n):
                self.cara([ring(c0, k), ring(c0, k + 1), ring(c1, k + 1), ring(c1, k)], rgb,
                          [j == 0, aristas_gen, j == m - 1, aristas_gen], relleno=relleno)
        if tapas:
            for c in (a, b):
                for k in range(n):
                    self.cara([c, ring(c, k), ring(c, k + 1)], rgb, [False, True, False], relleno=relleno)
        if anillos:
            k = anillos
            while k < L - 1e-9:
                c = a + u * k
                for q in range(n):
                    self.cara([ring(c, q), ring(c, q + 1)], rgb, [True, False], sesgo=1e-4, relleno=False)
                k += anillos

    def codo(self, P, a, b, R, r, rgb, rgb_campana=None, campana=0.05, n=18, m=8):
        """Codo de 90 grados: esquina de ejes P, llega en direccion a y sale en b (unitarios), radio de eje R.
        Incluye las dos campanas (largo campana) donde entran los tubos. Devuelve los extremos de las campanas."""
        P, a, b = (np.asarray(v, float) for v in (P, a, b))
        n0 = np.cross(a, b); n0 /= np.linalg.norm(n0)
        S = P - a * R; C = S + b * R
        anillos = []
        for k in range(m + 1):
            th = math.pi / 2 * k / m
            c = C + R * (-b * math.cos(th) + a * math.sin(th)); t = a * math.cos(th) + b * math.sin(th); w = np.cross(t, n0)
            anillos.append([c + r * (math.cos(2 * math.pi * j / n) * n0 + math.sin(2 * math.pi * j / n) * w) for j in range(n + 1)])
        for k in range(m):
            for j in range(n):
                self.cara([anillos[k][j], anillos[k][j + 1], anillos[k + 1][j + 1], anillos[k + 1][j]], rgb, [k == 0, False, k == m - 1, False])
        rc = rgb_campana or rgb
        e1 = S - a * campana; e2 = P + b * R + b * campana
        self.cilindro(e1, S, r + 0.007, rc, n=n, tapas=False, paso=1.0)
        self.cilindro(P + b * R, e2, r + 0.007, rc, n=n, tapas=False, paso=1.0)
        return e1, e2

    def prisma_hex(self, c, eje, ancho, alto, rgb):
        """Cabeza hexagonal (ancho entre caras) con base en c y altura a lo largo de eje."""
        c = np.asarray(c, float); u = np.asarray(eje, float); u /= np.linalg.norm(u)
        t = np.cross(u, [0, 0, 1.0]) if abs(u[2]) < 0.9 else np.cross(u, [1.0, 0, 0]); t /= np.linalg.norm(t); s = np.cross(u, t)
        R = ancho / math.sqrt(3)
        pts0 = [c + R * (math.cos(math.pi / 3 * k) * t + math.sin(math.pi / 3 * k) * s) for k in range(6)]
        pts1 = [p + u * alto for p in pts0]
        for k in range(6):
            self.cara([pts0[k], pts0[(k + 1) % 6], pts1[(k + 1) % 6], pts1[k]], rgb)
        self.cara(pts1, rgb); self.cara(pts0, rgb)

    def disco(self, c, eje, r, rgb, n=16, sesgo=0.0):
        c = np.asarray(c, float); u = np.asarray(eje, float); u /= np.linalg.norm(u)
        t = np.cross(u, [0, 0, 1.0]) if abs(u[2]) < 0.9 else np.cross(u, [1.0, 0, 0]); t /= np.linalg.norm(t); s = np.cross(u, t)
        self.cara([c + r * (math.cos(2 * math.pi * k / n) * t + math.sin(2 * math.pi * k / n) * s) for k in range(n)], rgb, sesgo=sesgo)

    # ------------------------------------------------------------ dibujo
    def dibujar(self, lam, xmm, ymm, capa_rel="ISO-CONCRETO-SUP", capa_ar="ISO-ARISTAS", color_ar=250):
        O = lam.P(xmm, ymm); msp = lam.msp
        P2 = lambda p: (O[0] + proy(p)[0], O[1] + proy(p)[1])
        orden = sorted(self.caras, key=lambda c: (c[5], float(sum(p.sum() for p in c[0]) / len(c[0])) + c[3]))
        for pts, rgb, bordes, _, relleno, _g in orden:
            if relleno and len(pts) >= 3:
                n = np.cross(pts[1] - pts[0], pts[2] - pts[0]); nn = np.linalg.norm(n)
                k = 1.0
                if nn > 1e-12:
                    n = n / nn
                    if n @ VISTA < 0: n = -n
                    k = 0.58 + 0.42 * max(0.0, float(n @ LUZ))
                col = tuple(int(max(0, min(255, c * k))) for c in rgb)
                q = [P2(p) for p in pts]
                tris = [(q[0], q[i], q[i + 1]) for i in range(1, len(q) - 1)]
                if len(q) == 4: tris = [(q[0], q[1], q[3], q[2])]
                for tr in tris:
                    e = msp.add_solid(list(tr), dxfattribs={"layer": capa_rel}); e.rgb = col
            for i, bd in enumerate(bordes):
                if bd:
                    a, b = pts[i], pts[(i + 1) % len(pts)]
                    msp.add_line(P2(a), P2(b), dxfattribs={"layer": capa_ar, "color": color_ar})
        return P2
