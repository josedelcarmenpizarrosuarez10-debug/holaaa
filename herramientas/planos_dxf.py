"""Genera el DXF con todas las laminas del colector pluvial (tramo Hogar de Refugio)."""
import os, sys, json
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import diseno as dz, dxf_base as B, dxf_planta as DP

SALIDA = os.path.join(RAIZ, "entregables", "PLANOS_COLECTOR_PLUVIAL_HOGAR_REFUGIO.dxf")
# origen de la planta: coordenadas locales del plano de arquitectura (la planta queda en su sitio)
OX1, OY1 = dz.X_SO - 50.0, dz.Y_CERCO - 78.0
LAMINAS = {}

def construir(solo=None):
    R, T, BP = DP.cargar()
    doc = B.nuevo_documento()
    lam = DP.dp01(doc, OX1, OY1, R, T, BP); LAMINAS["DP-01"] = lam
    lam = DP.dp02(doc, OX1 + 200, OY1, R, T); LAMINAS["DP-02"] = lam
    for lam in DP.dp03(doc, OX1 + 400, OY1, R, T): LAMINAS[lam.codigo] = lam
    try:
        import dxf_secciones as DS
        for lam in DS.todas(doc, OX1, OY1 - 200, R, T): LAMINAS[lam.codigo] = lam
    except ImportError: pass
    try:
        import dxf_cajas_iso as DC
        for lam in DC.todas(doc, OX1, OY1 - 400, R, T): LAMINAS[lam.codigo] = lam
    except ImportError: pass
    try:
        import dxf_cuadros as DQ
        for lam in DQ.todas(doc, OX1, OY1 - 600, R, T): LAMINAS[lam.codigo] = lam
    except ImportError: pass
    doc.saveas(SALIDA)
    cajas = {k: (l.ox, l.oy, l.ox + 841 * l.f, l.oy + 594 * l.f) for k, l in LAMINAS.items()}
    json.dump(cajas, open(os.path.join(RAIZ, "entregables", "_calc", "laminas.json"), "w"), indent=1)
    return SALIDA, cajas

if __name__ == "__main__":
    fn, cajas = construir()
    print(fn); [print(' ', k, [round(v, 2) for v in c]) for k, c in cajas.items()]
