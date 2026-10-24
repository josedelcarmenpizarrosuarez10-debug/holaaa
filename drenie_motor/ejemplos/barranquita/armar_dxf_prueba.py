"""Arma el DXF de prueba de la I.E. N.° 0590 Barranquita (C.I. N.° 468901) como si fuera el plano que entrega el usuario.

El DXF original del usuario (PLANTA_GENERAL_590, 332 MB) no se versiona. Para probar el motor se toman del juego entregado
(entregables_barranquita/PLANTEAMIENTO_CUNETAS_IE0590_BARRANQUITA.dxf) solo los datos de entrada: curvas de nivel a cota 0 con
sus rotulos, techos, veredas y el cerco confirmado, y las lineas magenta del usuario (insumos/barranquita/cunetas_magenta_usuario.json).
No se copia nada del diseno anterior (ejes, uniones ni descargas): el motor los tiene que encontrar solo.

Uso: python3 drenie_motor/ejemplos/barranquita/armar_dxf_prueba.py  -> drenie_motor/ejemplos/barranquita/PLANO_PRUEBA_BARRANQUITA.dxf
"""
import json
import os

import ezdxf

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(AQUI)))
FUENTE = os.path.join(RAIZ, "entregables_barranquita", "PLANTEAMIENTO_CUNETAS_IE0590_BARRANQUITA.dxf")
MAGENTA = os.path.join(RAIZ, "insumos", "barranquita", "cunetas_magenta_usuario.json")
SALIDA = os.path.join(AQUI, "PLANO_PRUEBA_BARRANQUITA.dxf")

BLOQUES = {"ARQUITECTURA_BASE": ("ARQ-TECHO", "ARQ-VEREDA", "ARQ-BASE"), "CURVAS_DE_NIVEL": ("CURVAS", "CURVAS-TXT"),
           "LIMITE_DE_INTERVENCION": ("LIMITE-INTERV",)}


def main():
    src = ezdxf.readfile(FUENTE)
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for capa in ("ARQ-TECHO", "ARQ-VEREDA", "ARQ-BASE", "CURVAS", "CURVAS-TXT", "LIMITE-INTERV"):
        doc.layers.add(capa, color=8)
    n = 0
    for b, capas in BLOQUES.items():
        for e in src.blocks[b]:
            if e.dxf.layer not in capas: continue
            if e.dxftype() == "LWPOLYLINE":
                msp.add_lwpolyline(list(e.get_points("xy")), close=e.closed, dxfattribs={"layer": e.dxf.layer}); n += 1
            elif e.dxftype() == "TEXT":
                msp.add_text(e.dxf.text, height=e.dxf.height, rotation=e.dxf.rotation,
                             dxfattribs={"layer": e.dxf.layer, "insert": e.dxf.insert}); n += 1
    for linea in json.load(open(MAGENTA))["lineas"]:
        msp.add_lwpolyline(linea, dxfattribs={"layer": "0", "color": 6}); n += 1
    doc.saveas(SALIDA)
    print(n, "entidades ->", SALIDA)


if __name__ == "__main__":
    main()
