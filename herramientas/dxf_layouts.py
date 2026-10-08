"""Presentaciones (layouts) de AutoCAD por lamina y lamina indice DP-00.

Cada lamina tiene su presentacion con el papel ISO full bleed de su formato y una ventana bloqueada a la escala de la
lamina; el espacio modelo queda en A1 para que el dialogo de impresion no pida otro papel. "DWG To PDF.pc3" es solo la
configuracion de pagina que trae los papeles ISO; al imprimir se elige el plotter propio con el mismo papel.
"""
import dxf_base as B

PAPEL = {"A0": ("ISO_full_bleed_A0_(1189.00_x_841.00_MM)", 1189.0, 841.0), "A1": ("ISO_full_bleed_A1_(841.00_x_594.00_MM)", 841.0, 594.0),
         "A2": ("ISO_full_bleed_A2_(594.00_x_420.00_MM)", 594.0, 420.0), "A3": ("ISO_full_bleed_A3_(420.00_x_297.00_MM)", 420.0, 297.0)}
PLOTTER = "DWG To PDF.pc3"


def presentaciones(doc, laminas):
    dm = doc.layouts.get("Model").dxf_layout.dxf
    dm.plot_configuration_file = PLOTTER; dm.paper_size = PAPEL["A1"][0]
    dm.paper_width, dm.paper_height = 841.0, 594.0
    dm.left_margin = dm.right_margin = dm.top_margin = dm.bottom_margin = 0.0
    dm.plot_paper_units = 1
    for cod, lam in laminas.items():
        nombre, W, H = PAPEL[lam.formato]
        if cod in doc.layouts: doc.layouts.delete(cod)
        lay = doc.layouts.new(cod)
        lay.page_setup(size=(W, H), margins=(0, 0, 0, 0), units="mm", offset=(0, 0), rotation=0, scale=16,
                       name=nombre.split("_(")[0], device=PLOTTER)
        vp = lay.add_viewport(center=(W / 2, H / 2), size=(W, H),
                              view_center_point=(lam.ox + W / 2 * lam.f, lam.oy + H / 2 * lam.f), view_height=H * lam.f)
        vp.dxf.flags = vp.dxf.flags | 16384          # ventana bloqueada: la escala no cambia al hacer zoom
        vp.dxf.layer = "MARCO"
    if "Layout1" in doc.layouts and len(doc.layouts) > 2:
        doc.layouts.delete("Layout1")


def indice(doc, ox, oy, lista, titulo="INDICE DE LAMINAS - COLECTOR PLUVIAL FRONTAL"):
    """Lamina DP-00 en A3: lista = [(codigo, descripcion, formato, escala)]."""
    lam = B.Lamina(doc, ox, oy, 25, "DP-00", titulo,
                   "RELACION DE LAMINAS, FORMATO DE PAPEL Y ESCALA - IMPRIMIR CADA PRESENTACION A ESCALA 1:1", formato="A3", escala_txt="S/E")
    filas = [[str(i + 1), cod, tit, form, esc] for i, (cod, tit, form, esc) in enumerate(lista)]
    alto = 6.0 if len(filas) <= 17 else 5.2
    yb = lam.tabla(30, 277, ["N.", "LAMINA", "DESCRIPCION", "FORMATO", "ESCALA"], filas, [10, 20, 268, 40, 32], hmm=1.7, alto_mm=alto,
                   titulo="INDICE DE LAMINAS")
    lam.notas(30, yb - 8, "NOTAS DE IMPRESION", [
        "1. Cada lamina tiene su presentacion (pestana) con el papel ISO full bleed indicado y la ventana bloqueada a su escala.",
        "2. Imprimir desde la pestana de la lamina: area = presentacion, escala 1:1, centrado. Plotter: el del usuario o DWG To PDF.",
        "3. A0 = 1189 x 841 mm; A1 = 841 x 594 mm; A2 = 594 x 420 mm; A3 = 420 x 297 mm."], hmm=1.6, ancho_mm=330)
    return lam
