# -*- coding: utf-8 -*-
"""Calcula la mira y la focal para que todo el predio quepa en una vista aérea 16:9 sin cortar nada (sensor de 36 mm).
No requiere Blender. Uso:
    python encuadre.py --predio x0 y0 x1 y1 [--alto 3.3] [--punto x y z ...] --camara A1 x y z [--camara A2 x y z ...]
--predio: esquinas en metros locales (cerco y lo que deba verse delante, como la vereda)
--alto:   altura de lo más alto en el contorno (cerco)
--punto:  puntos extra que deben caber (tanque elevado, torre)
Si la focal sale menor de unos 28 mm, alejar la cámara: la perspectiva deforma las edificaciones."""
import argparse
import math


def proyecta(p, cam, mira):
    fx, fy, fz = mira[0] - cam[0], mira[1] - cam[1], mira[2] - cam[2]
    L = math.sqrt(fx * fx + fy * fy + fz * fz); fx, fy, fz = fx / L, fy / L, fz / L
    rx, ry = fy, -fx
    R = math.hypot(rx, ry); rx, ry = rx / R, ry / R
    ux, uy, uz = ry * fz, -rx * fz, rx * fy - ry * fx
    dx, dy, dz = p[0] - cam[0], p[1] - cam[1], p[2] - cam[2]
    d = dx * fx + dy * fy + dz * fz
    return (dx * rx + dy * ry) / d, (dx * ux + dy * uy + dz * uz) / d


def encuadra(cam, pts, margen=1.06):
    mira = [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts), 0.0]
    for _ in range(80):                                                # centra la mira en el cuadro
        us = [proyecta(p, cam, mira) for p in pts]
        cu = (min(u for u, v in us) + max(u for u, v in us)) / 2
        cv = (min(v for u, v in us) + max(v for u, v in us)) / 2
        fx, fy = mira[0] - cam[0], mira[1] - cam[1]; L = math.hypot(fx, fy); rx, ry = fy / L, -fx / L
        D = math.dist(cam, mira)
        mira[0] += (rx * cu + fx / L * cv) * D * 0.6; mira[1] += (ry * cu + fy / L * cv) * D * 0.6
    us = [proyecta(p, cam, mira) for p in pts]
    au = max(u for u, v in us) - min(u for u, v in us); av = max(v for u, v in us) - min(v for u, v in us)
    return [round(m, 2) for m in mira], round(min(36 / (au * margen), 36 * 9 / 16 / (av * margen)), 1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--predio', nargs=4, type=float, required=True)
    ap.add_argument('--alto', type=float, default=3.3)
    ap.add_argument('--punto', nargs=3, type=float, action='append', default=[])
    ap.add_argument('--camara', nargs=4, action='append', required=True)
    a = ap.parse_args()
    x0, y0, x1, y1 = a.predio
    pts = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (0.0, a.alto)] + [tuple(p) for p in a.punto]
    for c in a.camara:
        cam = tuple(float(q) for q in c[1:])
        mira, f = encuadra(cam, pts)
        print(c[0], 'pos', list(cam), 'mira', mira, 'focal', f, '(alejar la camara)' if f < 28 else '')
