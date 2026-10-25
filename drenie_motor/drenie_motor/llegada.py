"""Llegada de una tuberia enterrada (salida de montante desde su dado o tubo de sumidero) a la cuneta.

Criterio del usuario (25-10-2026): el fondo del tubo llega por encima del nivel del agua de diseno de la cuneta, dentro del borde
libre, con 5 cm de margen: cota de llegada >= cota de fondo + tirante del tramo + 0.05. Si llegara a la cota de fondo, al llover
la cuneta lo ahoga, el agua se empoza y regresa por el tubo.
Si no llega se busca la salida en este orden: pendiente minima (0.5 %), tubo embebido mas alto (fondo a 0.15 bajo el piso), otra
cuneta al alcance, y por ultimo profundizar el tramo
que la recibe (lo hace el motor con h_req, sin pasar de la profundidad maxima objetivo, 1.00 m).
"""
from .techo import tirante

MARGEN = 0.05


def tirantes(V, P, R=None):
    """{"EJE|de|a": funcion(punto) -> tirante (m) en ese punto del tramo}. El caudal crece a lo largo del tramo, del que entra al de su
    final (como en la verificacion punto a punto); sin la red, el del final del tramo."""
    import math
    out = {}
    for f in V["hidraulica"]:
        S = max(f["S_pct"] / 100.0, 1e-4); b = f["b"]; Q1 = f["Q_ls"]; Q0 = min(f.get("Q_in_ls", Q1), Q1)
        a = R["nudos"][f["de"]] if R else None; L = f["L"] or 1.0

        def y_en(pt=None, a=a, L=L, Q0=Q0, Q1=Q1, S=S, b=b):
            fr = min(max(math.dist(a, pt) / L, 0.0), 1.0) if (a is not None and pt is not None) else 1.0
            Q = Q0 + (Q1 - Q0) * fr
            return tirante(Q / 1000.0, S, P.get("n_cap", 0.015), b) if Q > 0 else 0.0
        out["%s|%s|%s" % (f["eje"], f["de"], f["a"])] = y_en
    return out


def anchos(V):
    return {"%s|%s|%s" % (f["eje"], f["de"], f["a"]): f["b"] for f in V["hidraulica"]}


def resolver(z_ini, L, cf, y, pendientes=(0.01, 0.005), margen=MARGEN):
    """Pendiente con la que el tubo llega sobre el agua. Devuelve (S, z_llegada, nivel_minimo, ok)."""
    nivel = cf + y + margen
    for S in pendientes:
        if z_ini - S * L >= nivel - 1e-6: return S, z_ini - S * L, nivel, True
    S = pendientes[-1]
    return S, z_ini - S * L, nivel, False


def h_req(rasante, z_ini, L, y, S_min=0.005, margen=MARGEN):
    """Altura de cuneta que hace falta en la llegada para recibir el tubo al S_min sobre el agua."""
    return rasante - (z_ini - S_min * L - y - margen) + 0.005


def estado(ok):
    return "SOBRE EL AGUA" if ok else "BAJO EL AGUA"
