"""Genera el DXF con todas las laminas del colector pluvial (tramo Hogar de Refugio)."""
import os, sys, json
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import diseno as dz, dxf_base as B, dxf_planta as DP, dxf_layouts as L

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
    import dxf_detalles as DD
    for lam in DD.todas(doc, OX1, OY1 - 800, R, T): LAMINAS[lam.codigo] = lam
    # indice DP-00 (A3) y orden de las laminas por codigo
    orden = ["DP-01", "DP-02", "DP-03A", "DP-03B", "DP-04A", "DP-04B", "DP-05A", "DP-05B", "DP-06A", "DP-06B", "DP-06C", "DP-07", "DP-08", "DP-09", "DP-10",
             "DA-01", "DA-02", "DA-03", "DD-01", "DD-02", "DD-03", "DD-04"]
    orden = [c for c in orden if c in LAMINAS] + [c for c in LAMINAS if c not in orden]
    indicadas = ("DP-06B", "DD-01", "DD-02", "DD-03", "DD-04")
    lista = [("DP-00", "INDICE DE LAMINAS", "A3", "S/E")] + [(c, LAMINAS[c].titulo, LAMINAS[c].formato, "INDICADA" if c in indicadas else LAMINAS[c].escala_txt) for c in orden]
    lam0 = L.indice(doc, OX1 - 20.0, OY1 - 200.0, lista)
    ordenadas = {"DP-00": lam0}; ordenadas.update((c, LAMINAS[c]) for c in orden)
    LAMINAS.clear(); LAMINAS.update(ordenadas)
    # rellenos al fondo: las lineas quedan siempre visibles encima
    msp = doc.modelspace()
    msp.set_redraw_order({e.dxf.handle: "1" for e in msp.query("HATCH") if e.dxf.layer in ("CONCRETO-ACHURADO", "AGUA-RELLENO")})
    L.presentaciones(doc, LAMINAS)          # una presentacion por lamina, lista para imprimir a escala 1:1
    doc.saveas(SALIDA)
    cajas = {k: (l.ox, l.oy, l.ox + l.W * l.f, l.oy + l.H * l.f) for k, l in LAMINAS.items()}
    json.dump(cajas, open(os.path.join(RAIZ, "entregables", "_calc", "laminas.json"), "w"), indent=1)
    return SALIDA, cajas

if __name__ == "__main__":
    fn, cajas = construir()
    print(fn); [print(' ', k, [round(v, 2) for v in c]) for k, c in cajas.items()]
