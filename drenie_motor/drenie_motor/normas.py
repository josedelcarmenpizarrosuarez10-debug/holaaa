"""Biblioteca de normas y fuentes (normas_biblioteca.json): cada valor normativo con su norma, artículo o tabla, la
consideración adoptada y su estado de verificación. La usan el Excel de la memoria de cálculo, las memorias en Word y DrenIE
(orden `normas` del motor), así ningún documento cita una fuente distinta para el mismo dato.
"""
import json
import os

_RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "normas_biblioteca.json")
_B = None
CLASES = {"norma": "Norma", "referencia": "Referencia técnica", "criterio": "Criterio del proyectista"}
ESTADOS = {"verificado": "Verificado", "por_verificar": "Por verificar con el texto oficial"}


def biblioteca():
    global _B
    if _B is None:
        _B = json.load(open(_RUTA, encoding="utf-8"))
        _B["_datos"] = {d["id"]: d for d in _B["datos"]}
        _B["_cuadros"] = {c["id"]: c for c in _B["cuadros"]}
    return _B


def dato(clave):
    return biblioteca()["_datos"][clave]


def cuadro(clave):
    return biblioteca()["_cuadros"][clave]


def norma(sigla_id):
    return biblioteca()["normas"][sigla_id]


def cita(clave):
    """Cita corta de un dato o cuadro: «CE.040, artículo 12.5» / «Criterio del proyectista»."""
    b = biblioteca(); d = b["_datos"].get(clave) or b["_cuadros"][clave]
    n = b["normas"][d["fuente"]]
    return n["sigla"] + (", " + d["ref"] if d.get("ref") else "")


def cita_larga(clave):
    """Cita con el nombre completo y el dispositivo que la aprueba."""
    b = biblioteca(); d = b["_datos"].get(clave) or b["_cuadros"][clave]
    n = b["normas"][d["fuente"]]
    txt = n["nombre"] + (" (" + n["dispositivo"] + ")" if n.get("dispositivo") else "")
    return txt + (", " + d["ref"] if d.get("ref") else "")


def recuadro(clave):
    """Texto del recuadro de fuente: cita, consideración adoptada y estado."""
    b = biblioteca(); d = b["_datos"].get(clave) or b["_cuadros"][clave]
    partes = ["Fuente: " + cita_larga(clave) + "."]
    if d.get("consideracion"): partes.append("Consideración: " + d["consideracion"])
    partes.append("Tipo: %s · %s." % (CLASES[d["clase"]], ESTADOS[d["estado"]]))
    return " ".join(partes)


def para_drenie():
    """Biblioteca para la pantalla de DrenIE (sin los índices internos)."""
    b = biblioteca()
    return {"version": b["version"], "nota": b["nota"], "normas": b["normas"], "datos": b["datos"], "cuadros": b["cuadros"],
            "clases": CLASES, "estados": ESTADOS,
            "pendientes": sum(1 for x in b["datos"] + b["cuadros"] if x["estado"] != "verificado")}


def hoja_excel(wb, titulo="NORMAS Y FUENTES"):
    """Hoja con todos los datos y cuadros normativos, su fuente, consideración y estado."""
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    b = biblioteca(); ws = wb.create_sheet(titulo)
    fino = Side(style="thin", color="9FB3C8"); borde = Border(left=fino, right=fino, top=fino, bottom=fino)
    cab = PatternFill("solid", fgColor="0B2545"); gris = PatternFill("solid", fgColor="F3F7FB"); amar = PatternFill("solid", fgColor="FFF4D6")
    ws["A1"] = "NORMAS, REFERENCIAS Y CRITERIOS DEL DISEÑO DE DRENAJE PLUVIAL"; ws["A1"].font = Font(bold=True, size=12, color="0B2545")
    ws["A2"] = ("Cada valor con su fuente. Tipo: norma (exigencia normativa), referencia técnica (manual o libro) o criterio del "
                "proyectista. «Por verificar»: transcrito de los expedientes, falta cotejar con el texto oficial vigente.")
    ws["A2"].alignment = Alignment(wrap_text=True); ws.merge_cells("A2:G2"); ws.row_dimensions[2].height = 30
    r = 4
    for i, t in enumerate(["Grupo", "Dato", "Valor", "Unidad", "Fuente", "Consideración adoptada", "Tipo y estado"]):
        c = ws.cell(r, i + 1, t); c.font = Font(bold=True, color="FFFFFF"); c.fill = cab; c.border = borde
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for d in b["datos"]:
        r += 1
        fila = [d["grupo"], d["texto"], d["valor"], d["unidad"], cita_larga(d["id"]), d.get("consideracion", ""),
                CLASES[d["clase"]] + " · " + ESTADOS[d["estado"]]]
        for i, v in enumerate(fila):
            c = ws.cell(r, i + 1, v); c.border = borde; c.alignment = Alignment(wrap_text=True, vertical="top")
            if d["estado"] != "verificado" and i == 6: c.fill = amar
    r += 2
    for q in b["cuadros"]:
        ws.cell(r, 1, q["titulo"]).font = Font(bold=True, color="0B2545")
        ws.cell(r + 1, 1, "Fuente: " + cita_larga(q["id"]) + ". " + CLASES[q["clase"]] + " · " + ESTADOS[q["estado"]] + ".").font = Font(italic=True, size=9)
        r += 2
        for i, t in enumerate(q["columnas"]):
            c = ws.cell(r, i + 1, t); c.font = Font(bold=True); c.fill = gris; c.border = borde
        for f in q["filas"]:
            r += 1
            for i, v in enumerate(f):
                c = ws.cell(r, i + 1, v); c.border = borde; c.alignment = Alignment(wrap_text=True, vertical="top")
        if q.get("consideracion"):
            r += 1; ws.cell(r, 1, "Consideración: " + q["consideracion"]).font = Font(size=9)
        r += 2
    for col, w in zip("ABCDEFG", (16, 42, 22, 14, 46, 52, 26)): ws.column_dimensions[col].width = w
    return ws


def recuadro_word(D, *claves):
    """Recuadro de fuente en una memoria Word (una línea por dato)."""
    D.recuadro(" ".join(recuadro(k).replace("Fuente: ", "", 1) for k in claves), "Fuente" if len(claves) == 1 else "Fuentes")


def anexo_word(D, titulo="Normas, referencias y criterios"):
    """Anexo de las memorias en Word: los cuadros normativos y la tabla de datos con su fuente (D = word.Doc del motor)."""
    b = biblioteca()
    D.h(1, titulo)
    D.p("Cada valor usado en el diseño se indica con su fuente: norma peruana, referencia técnica o criterio del proyectista. "
        "Los marcados «por verificar» se transcribieron de los expedientes y deben cotejarse con el texto oficial vigente.")
    D.tabla("Datos de diseño y su fuente", ["Dato", "Valor", "Fuente", "Consideración", "Estado"],
            [[d["texto"], ("%s %s" % (d["valor"], d["unidad"])).strip(), cita(d["id"]) + ("" if d["clase"] == "criterio" else " (" + CLASES[d["clase"]].lower() + ")"),
              d.get("consideracion", ""), "verificado" if d["estado"] == "verificado" else "por verificar"] for d in b["datos"]],
            [3.2, 2.2, 3.2, 4.6, 1.6], tam=7)
    for q in b["cuadros"]:
        D.tabla(q["titulo"], q["columnas"], [[str(v) for v in f] for f in q["filas"]], None, tam=8,
                fuente=cita_larga(q["id"]) + ". " + CLASES[q["clase"]] + ", " + ESTADOS[q["estado"]].lower() + "." +
                (" " + q["consideracion"] if q.get("consideracion") else ""))
