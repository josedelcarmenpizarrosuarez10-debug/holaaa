"""Ciclo diseno <-> verificacion: la profundidad minima de cada tramo sube hasta que el tirante del caudal de diseno
deja 0.05 m de borde libre (hmin_req.json). Uso: python3 herramientas/barranquita/calcula_b.py
"""
import os, sys, json
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import diseno_b as DS
import verifica_b as VF

if __name__ == "__main__":
    if os.path.exists(DS.HREQ): os.remove(DS.HREQ)
    prev = None
    for it in range(8):
        DS.main(); VF.main()
        cur = json.load(open(DS.HREQ))
        print("--- iteracion %d: %d tramos con profundidad minima por capacidad" % (it + 1, len(cur)))
        if cur == prev: break
        prev = cur
