"""Cotas del terreno existente (superficie TOPO FINAL) a lo largo del eje del colector de Varones."""
import os, sys, json, numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(AQUI)); sys.path.insert(0, AQUI)
import diseno_v as dz, terreno as TE

def main():
    P = TE.cargar_tin()
    pr = np.arange(0, dz.P_FIN + 0.01, 0.5); pr[-1] = dz.P_FIN
    pts = [dz.local_a_utm(*dz.eje_local(p)[:2]) for p in pr]
    E = [p[0] for p in pts]; N = [p[1] for p in pts]
    f = TE.interpolador(P, min(E) - 60, max(E) + 60, min(N) - 60, max(N) + 60)
    out = [dict(p=round(float(p), 2), E=round(e, 3), N=round(n, 3), z=round(float(f(e, n)), 3)) for p, (e, n) in zip(pr, pts)]
    os.makedirs(dz.CALC, exist_ok=True); json.dump(out, open(os.path.join(dz.CALC, "terreno.json"), "w"), indent=0)
    zs = [o["z"] for o in out]; print("terreno: min %.2f max %.2f (NPT %.2f)" % (min(zs), max(zs), dz.D["NPT"]))
    for o in out[::20]: print("  0+%06.2f  z %.3f" % (o["p"], o["z"]))
if __name__ == "__main__": main()
