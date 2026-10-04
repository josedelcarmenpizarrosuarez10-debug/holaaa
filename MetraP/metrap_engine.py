"""MetraP - motor de metrado de cunetas a partir de un DXF de perfiles longitudinales y secciones.

Lee el DXF (perfiles por eje: lineas azules = tramo abierto, verdes = tramo tapado; rotulos NCT/NCF/H de cada seccion;
progresivas rotuladas) y llena, hoja por hoja, la plantilla Excel del proyecto (misma estructura de la planilla de
metrados de drenaje pluvial): CONCRETO EN CUNETAS, ENCOFRADO Y DESENCOFRADO, METRADO ACERO, METRADO DE CURADO,
METRADO DE REJILLAS, METRADO JUNTA DE DILATACION, PLANILLA GENERAL DE METRADOS y PARAMETROS.
Regla de acero: solo los tramos con H (desde el NCT) > 0.40 m; los tramos tapados llevan acero siempre.
Todo lo configurable esta en metrap_config.json (capas, colores, umbrales, acortamientos, nombre del proyecto).
"""
import os, sys, json, math, re, copy, zipfile, shutil
import openpyxl

AQUI = os.path.dirname(os.path.abspath(__file__))
CONFIG_DEFAULT = {
    "proyecto": "NOMBRE DEL PROYECTO, con CUI N.° 0000000",
    "entidad": None,
    "ubicacion": None,
    "capa_ejes": "A-AREA-IDEN",            # capa de los rotulos "EJE 01", "EJE 02", ... (uno por perfil, ordenados de arriba hacia abajo)
    "capa_progresivas": "GRID_TEXT",       # capa de los textos "0+000.00", "0+005.00", ...
    "x0_progresivas": None,                # x (en el DXF) de la progresiva 0+000; null = se toma del primer texto "0+000"
    "x_max_perfiles": None,                # los perfiles estan a la izquierda de esta x (las secciones a la derecha); null = automatico
    "desfase_inicio_perfil": 0.87,         # distancia entre el origen interno de progresivas y el inicio de las lineas de perfil (no cambiar)
    "color_abierto": 5,                    # azul: tramo abierto
    "color_cerrado": 84,                   # verde: tramo cerrado (tapado)
    "ancho_interior": 0.40, "espesor_muro": 0.10, "espesor_losa": 0.10,
    "h_minima_acero": 0.40,                # las cunetas con H > 0.40 (desde el NCT) llevan acero; las tapadas siempre
    "sep_transversal_tapa": 0.25, "ancho_transversal_tapa": 0.56,
    "separaciones_marco": [[0.45, 0.20], [0.60, 0.22], [99, 0.25]],   # [H media < limite, separacion]
    "correcciones_ncf": {},                # {"EJE 04": {"ultima": 260.42}} fuerza el NCF de la ultima seccion de ese eje
    "acortamientos": {},                   # {"4": [3.39, "colector"], "1": [2.77, "caja"]}: metros que se descuentan del ultimo tramo del eje
    "tapas_por_tramo_tapado": 1,
    "nombre_hoja_descuentos": "CUNETAS - LLEGADA AL COLECTOR",
}
CFG = dict(CONFIG_DEFAULT)
PENDIENTES = []
LOG = []


def log(msg):
    LOG.append(msg); print(msg)


def cargar_config(fn=None):
    global CFG
    CFG = dict(CONFIG_DEFAULT)
    if fn and os.path.exists(fn):
        CFG.update(json.load(open(fn, encoding="utf8")))
    return CFG


from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.styles.colors import Color
from openpyxl.utils import get_column_letter as L

# ----------------------------------------------------------------------------- formato de la planilla
FN = "Arial Narrow"
AZUL = Color(theme=4, tint=-0.249977111117893)          # cabeceras (igual a METRADO DE CURADO / METRADO ACERO)
F_CAB = PatternFill("solid", fgColor=AZUL)
F_DATO = PatternFill("solid", fgColor="FFF2CC")          # dato de entrada (planos / memoria)
F_FORM = PatternFill("solid", fgColor="F0F7E8")          # celda calculada
F_UND = PatternFill("solid", fgColor="F2F2F2")           # unidad
F_TIPO = PatternFill("solid", fgColor="E4DFEC")          # tipo / zona
F_TOT = PatternFill("solid", fgColor="F4B183")           # total de la fila
F_BARRA = PatternFill("solid", fgColor="17365D")         # barra de totales
F_SUB = PatternFill("solid", fgColor="D9EAF7")           # subtitulos
THIN = Side(style="thin"); BD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
NOMBRES = {"PAR": "COLECTOR PARAMETROS", "MT": "COLECTOR MOV. TIERRAS", "CO": "COLECTOR CONCRETO", "EN": "COLECTOR ENCOFRADO",
           "AC": "COLECTOR ACERO", "RT": "COLECTOR REGISTROS Y TAPAS", "JE": "COLECTOR JUNTAS Y EMPALMES", "IN": "COLECTOR INSUMOS"}
Q = {k: "'%s'" % v for k, v in NOMBRES.items()}


def celda(ws, r, c, v, tipo="txt", nf=None, size=12, bold=None, al="center", wrap=False):
    cell = ws.cell(row=r, column=c, value=v)
    color = None; fill = None; b = bool(bold)
    if tipo == "cab": fill = F_CAB; color = "FFFFFF"; b = True; wrap = True
    elif tipo == "barra": fill = F_BARRA; color = "FFFFFF"; b = True
    elif tipo == "dato": fill = F_DATO
    elif tipo == "form": fill = F_FORM
    elif tipo == "und": fill = F_UND
    elif tipo == "tipo": fill = F_TIPO; b = True
    elif tipo == "tot": fill = F_TOT; b = True
    elif tipo == "sub": fill = F_SUB; b = True
    elif tipo == "sust": al = "left"; wrap = True; size = min(size, 11)
    elif tipo == "auto":
        if isinstance(v, str) and v.startswith("="): fill = F_FORM
        elif isinstance(v, (int, float)): fill = F_DATO
    if bold is not None: b = bold
    cell.font = Font(name=FN, size=size, bold=b, color=color)
    if fill is not None: cell.fill = fill
    cell.border = BD
    cell.alignment = Alignment(horizontal=al, vertical="center", wrap_text=wrap)
    if nf: cell.number_format = nf
    elif isinstance(v, float) or (isinstance(v, str) and v.startswith("=")): cell.number_format = "0.00"
    return cell


def cabecera(ws, titulo, ncols, subtitulo=None):
    """Bloque de cabecera igual al de las hojas de la planilla: titulo, ENTIDAD, PROYECTO, UBICACION, FECHA."""
    ncols = max(ncols, 6)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    celda(ws, 1, 1, titulo, "cab", size=16); ws.row_dimensions[1].height = 27
    for j in range(2, ncols + 1): ws.cell(row=1, column=j).fill = F_CAB
    datos = [("ENTIDAD", "=+RESUMEN!B4", 25), ("PROYECTO", "=+RESUMEN!B5", 59), ("UBICACIÓN", "=+RESUMEN!B6", 25), ("FECHA", "=+RESUMEN!B7", 25)]
    for i, (k, f, h) in enumerate(datos):
        r = 2 + i
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2); ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=ncols)
        celda(ws, r, 1, k, "txt", size=14, bold=True); ws.cell(row=r, column=2).border = BD
        celda(ws, r, 3, f, "txt", size=14, al="left", wrap=True, nf="mmm-yy" if k == "FECHA" else "General")
        for j in range(4, ncols + 1): ws.cell(row=r, column=j).border = BD
        ws.row_dimensions[r].height = h
    r = 6
    if subtitulo:
        ws.merge_cells(start_row=7, start_column=1, end_row=7, end_column=ncols)
        celda(ws, 7, 1, subtitulo, "sub", size=12, al="left", wrap=True); ws.row_dimensions[7].height = 48
        for j in range(2, ncols + 1): ws.cell(row=7, column=j).border = BD
        r = 8
    return r + 1


def encabezado(ws, r, cols, alto=48):
    """cols: lista de (titulo, ancho, tipo, formato). Devuelve dict titulo -> letra."""
    letras = {}
    for j, (t, w, tipo, nf) in enumerate(cols):
        celda(ws, r, j + 1, t, "cab", size=12); ws.column_dimensions[L(j + 1)].width = w; letras[t] = L(j + 1)
    ws.row_dimensions[r].height = alto
    return letras


def fila(ws, r, cols, vals, alto=None):
    for j, ((t, w, tipo, nf), v) in enumerate(zip(cols, vals)):
        if v is None:
            c = ws.cell(row=r, column=j + 1); c.border = BD; continue
        celda(ws, r, j + 1, v, tipo, nf=nf)
    if alto: ws.row_dimensions[r].height = alto


def barra_total(ws, r, ncols, texto, sumas, nf="0.00"):
    """Fila de totales en barra azul oscuro. sumas: dict letra -> formula."""
    for j in range(1, ncols + 1): celda(ws, r, j, None, "barra")
    celda(ws, r, 1, texto, "barra", al="left")
    for col, f in sumas.items(): celda(ws, r, openpyxl.utils.column_index_from_string(col), f, "barra", nf=nf)
    ws.row_dimensions[r].height = 22


def subtitulo(ws, r, ncols, texto):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
    celda(ws, r, 1, texto, "sub", al="left")
    for j in range(2, ncols + 1): ws.cell(row=r, column=j).border = BD; ws.cell(row=r, column=j).fill = F_SUB
    ws.row_dimensions[r].height = 20


def nota(ws, r, ncols, texto, alto=34):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
    c = ws.cell(row=r, column=1, value=texto); c.font = Font(name=FN, size=11, italic=True); c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[r].height = alto



def _rels_hojas(rels_xml):
    """rId -> worksheets/sheetN.xml, sin depender del orden de los atributos."""
    out = {}
    for el in re.findall(r'<Relationship [^>]*>', rels_xml):
        mi = re.search(r'Id="(rId\d+)"', el); mt = re.search(r'Target="/?(?:xl/)?(worksheets/sheet\d+\.xml)"', el)
        if mi and mt: out[mi.group(1)] = mt.group(1)
    return out


def reinyectar_vml(orig, nuevo):
    """openpyxl descarta las imagenes de encabezado (legacyDrawingHF). Se copian de vuelta."""
    zo = zipfile.ZipFile(orig); zn = zipfile.ZipFile(nuevo)
    wbx = zo.read("xl/workbook.xml").decode("utf8"); rels = zo.read("xl/_rels/workbook.xml.rels").decode("utf8")
    nombre_por_rid = dict((m[1], m[0]) for m in re.findall(r'<sheet [^>]*name="([^"]*)"[^>]*r:id="(rId\d+)"', wbx))
    target_por_rid = _rels_hojas(rels)
    hojas_orig = {nombre_por_rid[k]: v for k, v in target_por_rid.items() if k in nombre_por_rid}
    wbn = zn.read("xl/workbook.xml").decode("utf8"); relsn = zn.read("xl/_rels/workbook.xml.rels").decode("utf8")
    nombre_por_rid_n = dict((m[1], m[0]) for m in re.findall(r'<sheet [^>]*name="([^"]*)"[^>]*r:id="(rId\d+)"', wbn))
    target_por_rid_n = _rels_hojas(relsn)
    hojas_nuevo = {nombre_por_rid_n[k]: v for k, v in target_por_rid_n.items() if k in nombre_por_rid_n}
    extra = {}; parches = {}
    for nombre, tgt in hojas_orig.items():
        sx = zo.read("xl/" + tgt).decode("utf8")
        m = re.search(r'<legacyDrawingHF r:id="(rId\d+)"\s*/>', sx)
        if not m or nombre not in hojas_nuevo: continue
        relp = "xl/worksheets/_rels/" + tgt.split("/")[-1] + ".rels"
        rx = zo.read(relp).decode("utf8")
        mt = re.search(r'<Relationship Id="%s"[^>]*Target="([^"]*)"' % m.group(1), rx)
        vml = mt.group(1).replace("../", "xl/")
        extra[vml] = zo.read(vml)
        vrel = vml.replace("drawings/", "drawings/_rels/") + ".rels"
        if vrel in zo.namelist():
            extra[vrel] = zo.read(vrel)
            for img in re.findall(r'Target="([^"]*)"', zo.read(vrel).decode("utf8")):
                extra[img.replace("../", "xl/")] = zo.read(img.replace("../", "xl/"))
        parches[hojas_nuevo[nombre]] = vml
    if not parches:
        return
    tmp = nuevo + ".tmp"; zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    for n in zn.namelist():
        data = zn.read(n)
        if n == "[Content_Types].xml":
            s = data.decode("utf8")
            if 'Extension="vml"' not in s: s = s.replace("</Types>", '<Default Extension="vml" ContentType="application/vnd.openxmlformats-officedocument.vmlDrawing"/></Types>')
            if 'Extension="jpeg"' not in s: s = s.replace("</Types>", '<Default Extension="jpeg" ContentType="image/jpeg"/></Types>')
            if 'Extension="png"' not in s: s = s.replace("</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')
            data = s.encode("utf8")
        for tgt, vml in parches.items():
            if n == "xl/" + tgt:
                s = data.decode("utf8")
                rid = "rIdHF1"
                tag = '<legacyDrawingHF r:id="%s"/>' % rid
                if "<legacyDrawingHF" not in s:
                    # orden del esquema CT_Worksheet: ... drawing, legacyDrawing, legacyDrawingHF, picture, oleObjects, controls, webPublishItems, tableParts, extLst
                    pos = len(s) - len("</worksheet>") - (len(s) - s.rfind("</worksheet>") - len("</worksheet>"))
                    pos = s.rfind("</worksheet>")
                    for sig in ("<picture", "<oleObjects", "<controls", "<webPublishItems", "<tableParts", "<extLst"):
                        k = s.find(sig)
                        if k != -1 and k < pos: pos = k
                    s = s[:pos] + tag + s[pos:]
                if 'xmlns:r=' not in s.split(">", 2)[1] + s.split(">", 2)[0]:
                    s = re.sub(r'<worksheet\b', '<worksheet xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"', s, count=1)
                data = s.encode("utf8")
                relp = "xl/worksheets/_rels/" + tgt.split("/")[-1] + ".rels"
                rel = '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/vmlDrawing" Target="../%s"/>' % (rid, vml.replace("xl/", ""))
                if relp in zn.namelist():
                    rs = zn.read(relp).decode("utf8").replace("</Relationships>", rel + "</Relationships>")
                else:
                    rs = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + rel + "</Relationships>"
                extra[relp] = rs.encode("utf8")
        if n in extra: continue
        zout.writestr(n, data)
    for n, d in extra.items(): zout.writestr(n, d)
    zout.close(); zn.close(); shutil.move(tmp, nuevo)





# ----------------------------------------------------------------------------- lectura del DXF
def leer_dxf(DXF):
    import ezdxf
    doc = ezdxf.readfile(DXF); msp = doc.modelspace()
    CAPA_EJES, CAPA_PROG = CFG["capa_ejes"], CFG["capa_progresivas"]
    # origen de progresivas y limite de los perfiles
    textos_prog = [e for e in msp if e.dxftype() == "TEXT" and e.dxf.layer == CAPA_PROG and e.dxf.text.strip().startswith("0+")]
    ceros = [e for e in textos_prog if re.match(r"0\+0*0?(\.0+)?$", e.dxf.text.strip().replace(" ", ""))]
    XMAX = CFG["x_max_perfiles"]
    if XMAX is None:
        xs = sorted(e.dxf.insert.x for e in textos_prog)
        XMAX = xs[-1] + 5.0 if xs else 1e9; log("limite derecho de los perfiles = %.2f" % XMAX)
    C_AB, C_CE = CFG["color_abierto"], CFG["color_cerrado"]
    def _color(e):
        c = e.dxf.color
        return doc.layers.get(e.dxf.layer).color if c == 256 else c
    X0 = CFG["x0_progresivas"]
    if X0 is None:
        # las progresivas se miden desde el inicio de las lineas de perfil (0+000 = extremo izquierdo de las lineas azul/verde)
        ini = [min(e.dxf.start.x, e.dxf.end.x) for e in msp if e.dxftype() == "LINE" and _color(e) in (C_AB, C_CE) and e.dxf.start.x < XMAX]
        ini += [min(p[0] for p in e.get_points("xy")) for e in msp if e.dxftype() == "LWPOLYLINE" and _color(e) in (C_AB, C_CE) and list(e.get_points("xy"))[0][0] < XMAX]
        if not ini: raise RuntimeError("No se encontraron lineas de perfil de color %d / %d; revise color_abierto y color_cerrado" % (C_AB, C_CE))
        X0 = min(ini) - CFG["desfase_inicio_perfil"]; log("origen de progresivas: inicio de los perfiles en x = %.2f" % min(ini))
    ejes = sorted([(e.dxf.insert.y, (e.plain_text().strip() if e.dxftype() == "MTEXT" else e.dxf.text)) for e in msp if e.dxf.layer == CAPA_EJES], reverse=True)
    bandas = [(n, y + 1.0, (ejes[i + 1][0] if i + 1 < len(ejes) else 1360) + 1.0) for i, (y, n) in enumerate(ejes)]
    def banda(y):
        for n, a, b in bandas:
            if b < y <= a: return n
    def color(e):
        c = e.dxf.color
        return doc.layers.get(e.dxf.layer).color if c == 256 else c
    out = {}
    for n, _, _ in bandas: out[n] = dict(sec=[], abierto=[], cerrado=[], L=0.0)
    # anotaciones de las secciones en los perfiles
    cols = {}
    for e in msp:
        if e.dxftype() == "TEXT" and e.dxf.insert.x < XMAX:
            t = e.dxf.text.strip(); x, y = e.dxf.insert.x, e.dxf.insert.y
            if t.startswith("%%USECCION") or re.match(r"(NCT|NCF|H):", t):
                key = (banda(y), round((x - X0) / 0.5) * 0.5)
                d = cols.setdefault(key, {})
                if ":" in t: d[t.split(":")[0]] = float(re.sub(r"[^\d.]", "", t.split(":")[1]))
                else: d["SEC"] = int(re.sub(r"\D", "", t))
    for (n, x), d in cols.items():
        if "H" in d: out[n]["sec"].append(dict(x=round(x, 2), sec=d.get("SEC"), NCT=d.get("NCT"), NCF=d.get("NCF"), H=d["H"]))
    for e in msp:
        if e.dxftype() == "TEXT" and e.dxf.layer == CAPA_PROG and e.dxf.insert.x < XMAX and e.dxf.text.strip().startswith("0+"):
            try: out[banda(e.dxf.insert.y)].setdefault("prog", []).append(float(e.dxf.text.strip()[2:]))
            except ValueError: pass
    for n in out:
        s = sorted(out[n]["sec"], key=lambda r: r["x"]); s[0]["x"] = 0.0      # la primera seccion es el 0+000
        for i, r in enumerate(s): r["sec"] = s[0]["sec"] + i                   # numeracion consecutiva por eje (rotulos desplazados)
        out[n]["sec"] = s
        corr = CFG["correcciones_ncf"].get(n)
        if corr and "ultima" in corr: log("%s: NCF de la ultima seccion forzado a %.2f (configuracion)" % (n, corr["ultima"])); s[-1]["NCF"] = corr["ultima"]
    # tramos por color: 5 azul = abierto, 84 verde = cerrado; se toman las lineas horizontales del perfil
    for e in msp:
        c = color(e)
        if e.dxftype() == "LINE" and c in (C_AB, C_CE) and e.dxf.start.x < XMAX and abs(e.dxf.start.y - e.dxf.end.y) < 0.05:
            n = banda(e.dxf.start.y); a, b = sorted([e.dxf.start.x - X0, e.dxf.end.x - X0])
            out[n]["abierto" if c == C_AB else "cerrado"].append((a, b))
        elif e.dxftype() == "LWPOLYLINE" and c in (C_AB, C_CE):
            pts = list(e.get_points("xy"))
            if pts[0][0] > XMAX: continue
            xs = [p[0] - X0 for p in pts]; n = banda(pts[0][1])
            if max(xs) - min(xs) > 0.5: out[n]["abierto" if c == C_AB else "cerrado"].append((min(xs), max(xs)))
    return out


def tramos_eje(d):
    """Une los segmentos de color en tramos consecutivos abierto / cerrado desde 0+000 (las lineas duplicadas
    del dibujo se funden por union de intervalos)."""
    def union(ivs):
        ivs = sorted((max(a, 0.87) - 0.87, b - 0.87) for a, b in ivs)
        out = []
        for a, b in ivs:
            if out and a <= out[-1][1] + 0.3: out[-1][1] = max(out[-1][1], b)
            else: out.append([a, b])
        return [(a, b) for a, b in out if b - a > 0.3]
    segs = [("ABIERTA", a, b) for a, b in union(d["abierto"])] + [("TAPADA", a, b) for a, b in union(d["cerrado"])]
    segs.sort(key=lambda s: s[1])
    out = []
    progs = d.get("prog", [])
    for i, (t, a, b) in enumerate(segs):
        a2 = 0.0 if i == 0 else out[-1][2]
        cerca = [p for p in progs if abs(p - b) < 0.15]
        out.append([t, a2, round(cerca[0] if cerca else b, 2)])        # el limite se ajusta a la progresiva rotulada
    return out


def H_en(d, x):
    """Altura interior en la progresiva x, interpolando entre las secciones rotuladas."""
    s = d["sec"]; xs = [r["x"] for r in s]; hs = [r["H"] for r in s]
    if x <= xs[0]: return hs[0]
    if x >= xs[-1]: return hs[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            f = (x - xs[i]) / (xs[i + 1] - xs[i]); return hs[i] + f * (hs[i + 1] - hs[i])


def area_muro(d, a, b, n=200):
    """Integral de H entre a y b (area de una cara del muro, en m2)."""
    tot = 0.0
    for i in range(n):
        x1 = a + (b - a) * i / n; x2 = a + (b - a) * (i + 1) / n
        tot += 0.5 * (H_en(d, x1) + H_en(d, x2)) * (x2 - x1)
    return tot


def sec_cercana(d, x):
    return min(d["sec"], key=lambda r: abs(r["x"] - x))


# ----------------------------------------------------------------------------- llenado de la plantilla
def limpiar(ws, celdas):
    for c in celdas: ws[c].value = None


def analizar(DXF):
    """Lee el DXF y devuelve (D, E): perfiles crudos por eje y ejes con sus tramos, alturas, areas y descuentos."""
    PENDIENTES.clear(); LOG.clear()
    DESCUENTOS = {int(k): (float(v[0]), v[1]) for k, v in CFG["acortamientos"].items()}
    D = leer_dxf(DXF)
    nombres = sorted(D.keys())                       # EJE 01 .. EJE 09
    E = []
    for n in nombres:
        d = D[n]; tr = tramos_eje(d); L = tr[-1][2]
        num = int(n.split()[1]); L_dib = L
        if num in DESCUENTOS:
            dL = DESCUENTOS[num][0]; L = round(L - dL, 2); tr[-1][2] = L            # el ultimo tramo termina en el muro del colector / de la CL
        tramos = []
        for i, (t, a, b) in enumerate(tr):
            tramos.append(dict(tipo=t, a=a, b=b, L=round(b - a, 2), Hi=round(H_en(d, a), 2), Hf=round(H_en(d, b), 2), area=area_muro(d, a, b),
                               sec_i=sec_cercana(d, a)["sec"], sec_f=sec_cercana(d, b)["sec"]))
        E.append(dict(nombre=n, num=num, L=round(L, 2), L_dib=round(L_dib, 2), desc=DESCUENTOS.get(num, (0.0, ""))[0], entra_en=DESCUENTOS.get(num, (0.0, ""))[1], tramos=tramos, area=area_muro(d, 0, L), L_tap=round(sum(t["L"] for t in tramos if t["tipo"] == "TAPADA"), 2),
                      L_ab=round(sum(t["L"] for t in tramos if t["tipo"] == "ABIERTA"), 2), Hprom=area_muro(d, 0, L) / L, NCF_ini=d["sec"][0]["NCF"], NCF_fin=d["sec"][-1]["NCF"]))
    return D, E


def filas_acero(D, E):
    """Tramos que llevan acero: solo donde H (desde el NCT) > h_minima_acero; los tapados siempre."""
    H_MIN = CFG["h_minima_acero"]
    filas = []
    for e in E:
        d = D[e["nombre"]]; k = 0
        for t in e["tramos"]:
            if t["tipo"] == "TAPADA":
                filas.append((e, k, t)); k += 1
            elif t["Hf"] >= H_MIN - 1e-9:
                if t["Hi"] >= H_MIN - 1e-9:
                    filas.append((e, k, t)); k += 1
                else:
                    x40 = t["a"]
                    while H_en(d, x40) < H_MIN - 1e-9 and x40 < t["b"]: x40 += 0.01
                    x40 = round(x40, 2)
                    cerca = [p for p in d.get("prog", []) if abs(p - x40) < 0.3]
                    if cerca: x40 = cerca[0]
                    t2 = dict(t); t2.update(a=x40, L=round(t["b"] - x40, 2), Hi=round(H_en(d, x40), 2), sec_i=sec_cercana(d, x40)["sec"])
                    filas.append((e, k, t2)); k += 1
    return filas


def construir(DXF, PLANTILLA, SALIDA, DE=None):
    B_INT, E_MURO, E_LOSA = CFG["ancho_interior"], CFG["espesor_muro"], CFG["espesor_losa"]; B_EXT = B_INT + 2 * E_MURO
    SEP_TRANSV = CFG["sep_transversal_tapa"]
    DESCUENTOS = {int(k): (float(v[0]), v[1]) for k, v in CFG["acortamientos"].items()}
    D, E = DE if DE else analizar(DXF)
    wb = openpyxl.load_workbook(PLANTILLA)
    # ---------------- RESUMEN (datos del proyecto)
    wr = wb["RESUMEN"]
    wr["B5"] = CFG["proyecto"]
    if CFG.get("entidad"): wr["B4"] = CFG["entidad"]
    if CFG.get("ubicacion"): wr["B6"] = CFG["ubicacion"]
    # ---------------- CONCRETO EN CUNETAS: bloques de 12 filas; ejes 1-6 columna E, 7-12 columna M
    wc = wb["CONCRETO EN CUNETAS"]
    for k in range(12):
        r0 = 10 + 12 * (k % 6); col = "E" if k < 6 else "M"; lab = "B" if k < 6 else "J"
        if k < len(E):
            e = E[k]
            wc["%s%d" % (lab, r0)] = "CUNETA EJE %02d" % e["num"]
            wc["%s%d" % (col, r0)] = round(e["area"], 2); wc["%s%d" % (col, r0 + 4)] = e["L"]; wc["%s%d" % (col, r0 + 6)] = e["L_tap"]
        else:
            wc["%s%d" % (lab, r0)] = None; wc["%s%d" % (col, r0)] = 0; wc["%s%d" % (col, r0 + 4)] = 0; wc["%s%d" % (col, r0 + 6)] = 0
    # ---------------- ENCOFRADO: bloque k en fila [12,12,23,23,34,34,45,45,57,57,69,69], columna F (impar) / N (par)
    we = wb["ENCOFRADO Y DESENCOFRADO"]; filas_e = [12, 12, 23, 23, 34, 34, 45, 45, 57, 57, 69, 69]
    for k in range(12):
        r = filas_e[k]; col = "F" if k % 2 == 0 else "N"; lab = "B" if k % 2 == 0 else "J"; tipo = "C" if k % 2 == 0 else "K"
        if k < len(E):
            e = E[k]
            ab = [t for t in e["tramos"] if t["tipo"] == "ABIERTA"]; tp = [t for t in e["tramos"] if t["tipo"] == "TAPADA"]
            a_ab = sum(t["area"] for t in ab); L_ab = sum(t["L"] for t in ab); a_tp = sum(t["area"] for t in tp); L_tp = sum(t["L"] for t in tp)
            we["%s%d" % (lab, r)] = "EJE %d" % e["num"]; we["%s%d" % (tipo, r)] = "ABIERTA"
            we["%s%d" % (col, r)] = round(a_ab + E_LOSA * L_ab, 2)        # muro externo abierta: H + losa de fondo
            we["%s%d" % (col, r + 2)] = round(a_ab, 2)                     # muro interno abierta: H
            we["%s%d" % (col, r + 4)] = round(a_tp + 2 * E_LOSA * L_tp, 2)  # muro externo tapada: H + losa de fondo + tapa
            we["%s%d" % (col, r + 6)] = round(a_tp, 2)                     # muro interno tapada: H
            we["%s%d" % (col, r + 8)] = "=%s*%s" % (L_tp, B_INT) if L_tp > 0 else 0   # fondo de la tapa: L x 0.40
        else:
            we["%s%d" % (lab, r)] = None; we["%s%d" % (tipo, r)] = None
            for off in (0, 2, 4, 6, 8): we["%s%d" % (col, r + off)] = 0
    # ---------------- METRADO ACERO (filas 11-37), CURADO (7-36), REJILLAS (7-36): una fila por tramo
    wa = wb["METRADO ACERO"]; wk = wb["METRADO DE CURADO"]; wj = wb["METRADO DE REJILLAS"]
    filas = filas_acero(D, E)
    assert len(filas) <= 27, "mas tramos que filas en la plantilla"
    sep_long = {}
    for e in E:
        for s in D[e["nombre"]]["sec"]:
            sep_long[s["sec"]] = None
    todos = [(e, i, t) for e in E for i, t in enumerate(e["tramos"])]      # curado y rejillas: todos los tramos
    for i in range(27):
        ra = 11 + i
        if i < len(filas):
            e, j, t = filas[i]
            Hm = (t["Hi"] + t["Hf"]) / 2
            sep = next(sp for lim, sp in CFG["separaciones_marco"] if Hm < lim)
            wa["A%d" % ra] = i + 1; wa["B%d" % ra] = "EJE %02d" % e["num"]; wa["C%d" % ra] = "TRAMO %02d" % (j + 1); wa["D%d" % ra] = t["tipo"]
            wa["E%d" % ra] = "SEC %02d" % t["sec_i"]; wa["F%d" % ra] = "SEC %02d" % t["sec_f"]; wa["G%d" % ra] = t["L"]; wa["H%d" % ra] = '3/8"'
            wa["J%d" % ra] = sep
            wa["K%d" % ra] = math.ceil((B_EXT + 2 * t["Hi"]) / sep); wa["L%d" % ra] = math.ceil((B_EXT + 2 * t["Hf"]) / sep)
            wa["P%d" % ra] = SEP_TRANSV; wa["Q%d" % ra] = round(B_EXT + 2 * (t["Hi"] + 0.05), 2); wa["R%d" % ra] = round(B_EXT + 2 * (t["Hf"] + 0.05), 2)
            if t["tipo"] == "TAPADA":
                wa["X%d" % ra] = '3/8"'; wa["Y%d" % ra] = CFG["ancho_transversal_tapa"]; wa["Z%d" % ra] = SEP_TRANSV; wa["AA%d" % ra] = CFG["ancho_transversal_tapa"]; wa["AB%d" % ra] = CFG["ancho_transversal_tapa"]
            else:
                wa["X%d" % ra] = None; wa["Y%d" % ra] = ""; wa["Z%d" % ra] = None; wa["AA%d" % ra] = None; wa["AB%d" % ra] = None
        else:
            limpiar(wa, ["%s%d" % (c, ra) for c in ("A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "P", "Q", "R", "X", "Z", "AA", "AB")]); wa["Y%d" % ra] = ""
    for i in range(30):
        rk = rj = 7 + i
        if i < len(todos):
            e, j, t = todos[i]
            for ws_, r in ((wk, rk), (wj, rj)):
                ws_["A%d" % r] = i + 1; ws_["B%d" % r] = "EJE %02d" % e["num"]; ws_["C%d" % r] = "TRAMO %02d" % (j + 1); ws_["D%d" % r] = t["tipo"]; ws_["E%d" % r] = t["L"]
            wk["F%d" % rk] = B_INT; wk["G%d" % rk] = t["Hi"]; wk["H%d" % rk] = t["Hf"]
            wj["F%d" % rj] = 0
        else:
            limpiar(wk, ["%s%d" % (c, rk) for c in ("A", "B", "C", "D", "E", "F", "G", "H")])
            limpiar(wj, ["%s%d" % (c, rj) for c in ("A", "B", "C", "D", "E", "F")])
    # ---------------- JUNTA DE DILATACION: filas 13-24, un eje por fila (D longitud; E apunta al bloque de CONCRETO)
    wjd = wb["METRADO JUNTA DE DILATACION"]
    for k in range(12):
        r = 13 + k
        if k < len(E): wjd["B%d" % r] = "EJE %02d" % E[k]["num"]; wjd["D%d" % r] = E[k]["L"]
        else: limpiar(wjd, ["%s%d" % (c, r) for c in "ABDEFGHIJ"])
    # ---------------- PLANILLA GENERAL: filas por eje
    wp = wb["PLANILLA GENERAL DE METRADOS"]
    bloques = {"limpieza": (12, "D", None), "trazo": (25, "D", None), "excav": (39, "D", "F"), "refine": (55, "D", None), "relleno": (68, "D", "F"), "solado": (85, "D", None)}
    for nombre, (r0, cL, cH) in bloques.items():
        for k in range(12):
            r = r0 + k
            if k < len(E):
                wp["B%d" % r] = "EJE %d" % E[k]["num"]; wp["C%d" % r] = 1; wp["%s%d" % (cL, r)] = E[k]["L"]
                if cH: wp["%s%d" % (cH, r)] = round(E[k]["Hprom"] + E_LOSA, 2)     # altura promedio + losa de fondo (el solado lo suma PARAMETROS!B15)
            else:
                wp["B%d" % r] = None; wp["C%d" % r] = None; wp["%s%d" % (cL, r)] = None
                if cH: wp["%s%d" % (cH, r)] = None
    for r0 in (102, 115):
        for k in range(12):
            wp["B%d" % (r0 + k)] = ("EJE %d" % E[k]["num"]) if k < len(E) else None
    # dados, montantes, sumideros: sin datos de Varones
    for c in ("C51", "C97", "K139", "C140", "C142", "C145"): wp[c] = 0
    PENDIENTES.append("PLANILLA GENERAL: dados de concreto (C51, C97) y falsas columnas de montantes (K139, C140, C142, C145) en 0: falta la cantidad de montantes de Varones.")
    wm = wb["METRADO MONTANTES"]
    for r in range(11, 57):
        for c in "CDEGHJKMNPQ":
            cell = wm["%s%d" % (c, r)]
            if not (isinstance(cell.value, str) and cell.value.startswith("=")): cell.value = None
    PENDIENTES.append("METRADO MONTANTES: hoja vaciada; falta el calculo de montantes por edificacion de Varones (plano de techos).")
    wsu = wb["METRADO  EN PISO (SUMIDERO)"]
    for r in range(8, 12):
        for c in "BCDEF": wsu["%s%d" % (c, r)] = 0
        wsu["G%d" % r] = "Sin datos de Varones"
    PENDIENTES.append("METRADO EN PISO (SUMIDERO): sectores en 0; falta la red de piso y sumideros de Varones.")
    # tapas de registro en cunetas tapadas: 1 por tramo tapado (provisional)
    n_tap = CFG["tapas_por_tramo_tapado"] * sum(1 for e in E for t in e["tramos"] if t["tipo"] == "TAPADA")
    wb["PARAMETROS"]["B4"] = n_tap; wb["PARAMETROS"]["D4"] = "Provisional: 1 tapa por tramo tapado (%d tramos); confirmar con el plano" % n_tap
    PENDIENTES.append("PARAMETROS!B4: tapas de registro en cunetas tapadas = %d (1 por tramo tapado, provisional)." % n_tap)
    # ---------------- hoja de sustento del acortamiento de las cunetas que llegan al colector
    if DESCUENTOS:
        _cab, _enc, _fila, _nota = cabecera, encabezado, fila, nota
        wd = wb.create_sheet(CFG["nombre_hoja_descuentos"], wb.sheetnames.index("PARAMETROS"))
        cols = [("N°", 5, "txt", None), ("CUNETA", 14, "txt", None), ("LONGITUD DIBUJADA (m)", 14, "dato", "0.00"), ("ACORTAMIENTO (m)", 14, "dato", "0.00"), ("LONGITUD METRADA (m)", 14, "form", "0.00"),
                ("TERMINA EN", 30, "txt", None), ("SUSTENTO", 70, "sust", None)]
        r = _cab(wd, "CUNETAS - ACORTAMIENTO EN LA LLEGADA AL COLECTOR PLUVIAL FRONTAL", len(cols),
                 "Las cunetas estan dibujadas hasta la franja exterior del frente. El colector pluvial frontal ocupa esa franja, por lo que cada cuneta termina en la cara del muro "
                 "lado predio del colector (ventana de empalme, lamina DP-06C) o en el muro norte de la caja de llegada CL del Hogar de Refugio (Eje 01, lamina DP-07). "
                 "El tramo que caia dentro del colector se descuenta de la longitud de la cuneta en todas las hojas de este metrado (concreto, encofrado, acero, curado, rejillas, juntas, movimiento de tierras).")
        _enc(wd, r, cols, 40); rr = r + 1
        for i, e in enumerate([e for e in E if e["desc"] > 0]):
            _fila(wd, rr, cols, [i + 1, "EJE %02d" % e["num"], e["L_dib"], e["desc"], "=C%d-D%d" % (rr, rr),
                                 "muro del colector (ventana)" if e["entra_en"] == "colector" else "muro norte de la caja CL",
                                 "Lamina DP-01 del colector (planta: tramo de cuneta que se descuenta) y memoria de calculo del colector, hoja CUNETAS"], 26)
            rr += 1
        _nota(wd, rr + 1, len(cols), "Nota: el acortamiento se aplica al ultimo tramo de cada eje (el que llega al frente); las alturas H se mantienen las del perfil. Las cunetas de los Ejes 02, 03, 05 y 07 no llegan al frente y no cambian.")
    SALIDA = os.path.abspath(SALIDA); os.makedirs(os.path.dirname(SALIDA), exist_ok=True); wb.save(SALIDA)
    reinyectar_vml(PLANTILLA, SALIDA)
    return E, SALIDA




def ejecutar(dxf, plantilla, salida, config=None, DE=None):
    """Punto de entrada: devuelve (ejes, ruta de salida, pendientes, log)."""
    if config is not None or not DE: cargar_config(config)
    E, fn = construir(dxf, plantilla, salida, DE)
    for e in E:
        log("%s L=%.2f (dibujada %.2f, descuento %.2f) Hprom=%.3f area muro=%.2f tapada=%.2f  NCF %.2f -> %.2f" % (e["nombre"], e["L"], e["L_dib"], e["desc"], e["Hprom"], e["area"], e["L_tap"], e["NCF_ini"], e["NCF_fin"]))
        for t in e["tramos"]: log("    %-8s %7.2f - %7.2f  L=%6.2f  H %.2f -> %.2f  sec %s-%s" % (t["tipo"], t["a"], t["b"], t["L"], t["Hi"], t["Hf"], t["sec_i"], t["sec_f"]))
    for p in PENDIENTES: log("PENDIENTE: " + p)
    return E, fn, list(PENDIENTES), list(LOG)
