"""Base comun de los planos DXF: documento, capas, estilos, bloques, marco A1,
rotulo, leyenda y utilidades de dibujo (texto, cotas, achurados).

Escala real: 1 unidad = 1 m. Cada lamina se dibuja en una zona del modelo con
un factor f = escala/1000 (m por mm de papel); p.ej. 1:25 -> f = 0.025.
"""
import math
import ezdxf
from ezdxf.enums import TextEntityAlignment as TA
from ezdxf.math import Vec2

PROYECTO = ("CREACION DEL SERVICIO DE ATENCION INTEGRAL A MUJERES VICTIMAS DE VIOLENCIA EN EL HOGAR DE REFUGIO TEMPORAL",
            "MUJERES VIOLENTADAS, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2675514")
UBICACION = "UBICACION: PREDIO RURAL LOS MANGOS - MORALES - SAN MARTIN - SAN MARTIN"
ESPECIALIDAD = "ESPECIALIDAD: INSTALACIONES SANITARIAS - DRENAJE PLUVIAL"
FECHA = "OCT. 2026"
ELABORADO = "HIDROCONSULT"

# capas (nombre, color, tipo de linea) - mismas del tramo CAR Mujeres
CAPAS = [
    # (nombre, color ACI, tipo de linea). Paleta pensada para fondo blanco: sin amarillo ni cian claro.
    ("MARCO", 7, "CONTINUOUS"), ("ROTULO", 7, "CONTINUOUS"), ("ROTULO-TEXTO", 7, "CONTINUOUS"),
    ("TITULOS", 7, "CONTINUOUS"), ("TEXTOS", 7, "CONTINUOUS"), ("TEXTOS-NOTAS", 7, "CONTINUOUS"),
    ("LEYENDA", 7, "CONTINUOUS"), ("COTAS", 6, "CONTINUOUS"), ("NIVELES", 7, "CONTINUOUS"),
    ("LLAMADAS", 8, "CONTINUOUS"), ("EJE-COLECTOR", 8, "CENTER"), ("CONCRETO", 94, "CONTINUOUS"),
    ("CONCRETO-OCULTO", 94, "HIDDEN"), ("CONCRETO-ACHURADO", 8, "CONTINUOUS"), ("SOLADO", 8, "CONTINUOUS"),
    ("ACERO", 1, "CONTINUOUS"), ("ACERO-LONG", 5, "CONTINUOUS"), ("ACERO-PUNTOS", 5, "CONTINUOUS"), ("REGISTRO", 32, "CONTINUOUS"),
    ("REGISTRO-TAPA", 30, "CONTINUOUS"), ("MARCO-METALICO", 32, "CONTINUOUS"), ("JUNTAS", 8, "DASHED"),
    ("CRUCE-VEHICULAR", 30, "CONTINUOUS"), ("CUNETA", 3, "CONTINUOUS"), ("CUNETA-OCULTA", 3, "HIDDEN"),
    ("POZA", 34, "CONTINUOUS"), ("TERRENO", 7, "CONTINUOUS"), ("TERRENO-EXISTENTE", 8, "DASHED"),
    ("TERRENO-ACHURADO", 8, "CONTINUOUS"), ("EXCAVACION", 8, "HIDDEN"), ("RELLENO", 32, "CONTINUOUS"),
    ("AGUA", 150, "DASHED"), ("AGUA-SIMBOLO", 150, "CONTINUOUS"), ("AGUA-RELLENO", 150, "CONTINUOUS"), ("FLUJO", 150, "CONTINUOUS"),
    ("CORTES", 6, "CONTINUOUS"), ("PROGRESIVAS", 5, "CONTINUOUS"), ("GRILLA", 9, "CONTINUOUS"),
    ("GUITARRA", 8, "CONTINUOUS"), ("LINDERO", 6, "PHANTOM"), ("CERCO", 14, "CONTINUOUS"),
    ("ARQ-BASE", 8, "CONTINUOUS"), ("ARQ-TEXTO", 8, "CONTINUOUS"), ("VIA", 8, "CONTINUOUS"),
    ("ISO-CONCRETO-SUP", 254, "CONTINUOUS"), ("ISO-CONCRETO-LAT1", 253, "CONTINUOUS"),
    ("ISO-CONCRETO-LAT2", 252, "CONTINUOUS"), ("ISO-TAPA", 255, "CONTINUOUS"), ("ISO-ARISTAS", 8, "CONTINUOUS"),
    ("ISO-AGUA", 150, "CONTINUOUS"), ("ISO-TERRENO", 94, "CONTINUOUS"), ("ISO-PIEDRA", 34, "CONTINUOUS"),
    ("ISO-CUNETA", 94, "CONTINUOUS"), ("ISO-CERCO", 14, "CONTINUOUS"),
]
ESCALAS = [10, 20, 25, 50, 100, 200, 250]
COLOR_RGB = {
    "ISO-CONCRETO-SUP": (232, 232, 232), "ISO-CONCRETO-LAT1": (206, 206, 206), "ISO-CONCRETO-LAT2": (178, 178, 178),
    "ISO-TAPA": (248, 244, 230), "ISO-AGUA": (130, 190, 240), "ISO-TERRENO": (214, 226, 196), "ISO-PIEDRA": (196, 176, 146),
    "ISO-CUNETA": (168, 214, 168), "ISO-CERCO": (226, 200, 200), "AGUA-RELLENO": (205, 228, 246), "CONCRETO-ACHURADO": (120, 120, 120),
}


def nuevo_documento():
    doc = ezdxf.new("R2010", setup=["linetypes"])
    doc.header["$LTSCALE"] = 0.25
    doc.header["$INSUNITS"] = 6          # metros
    doc.header["$LUPREC"] = 2
    if "HIDDEN" not in doc.linetypes:
        doc.linetypes.add("HIDDEN", pattern=[0.375, 0.25, -0.125], description="Hidden __ __ __ __ __ __ __ __ __ __ __ __ __ __")
    for n, c, lt in CAPAS:
        if n not in doc.layers:
            ly = doc.layers.add(n, color=c, linetype=lt)
            if n in COLOR_RGB: ly.rgb = COLOR_RGB[n]
    if "TITULOS" not in doc.styles:
        doc.styles.add("TITULOS", font="romand.shx")
    doc.styles.get("STANDARD").dxf.font = "romans.shx"
    for e in ESCALAS:
        ds = doc.dimstyles.add(f"COT-{e}")
        ds.dxf.dimscale = e / 1000.0
        ds.dxf.dimtxt = 2.5; ds.dxf.dimasz = 2.0; ds.dxf.dimexe = 1.5; ds.dxf.dimexo = 1.0; ds.dxf.dimgap = 0.8
        ds.dxf.dimtad = 1; ds.dxf.dimtih = 0; ds.dxf.dimtoh = 0; ds.dxf.dimdec = 2; ds.dxf.dimlfac = 1.0
        ds.dxf.dimclrd = 256; ds.dxf.dimclre = 256; ds.dxf.dimclrt = 7; ds.dxf.dimtxsty = "STANDARD"   # lineas de cota por capa (COTAS)
        ds.dxf.dimtsz = 1.0                      # tic oblicuo (sin bloque de flecha)
        ds.dxf.dimpost = "<>"; ds.dxf.dimapost = ""; ds.dxf.dimblk = ""; ds.dxf.dimblk1 = ""; ds.dxf.dimblk2 = ""   # grupos 3-7 presentes
        ds.dxf.dimzin = 0; ds.dxf.dimdsep = ord(".")
    crear_bloques(doc)
    return doc


def crear_bloques(doc):
    b = doc.blocks.new("SIMB-FLECHA")
    b.add_lwpolyline([(-4, 0), (4, 0)], dxfattribs={"layer": "FLUJO"})
    b.add_solid([(4, 0), (1, 1.2), (1, -1.2)], dxfattribs={"layer": "FLUJO"})
    b = doc.blocks.new("SIMB-NIVEL")
    b.add_lwpolyline([(0, 0), (-1.5, 2.2), (1.5, 2.2)], close=True, dxfattribs={"layer": "NIVELES"})
    b.add_line((-3, 0), (3, 0), dxfattribs={"layer": "NIVELES"})
    b = doc.blocks.new("SIMB-AGUA")
    b.add_solid([(0, 0), (-1.2, 1.8), (1.2, 1.8)], dxfattribs={"layer": "AGUA-SIMBOLO"})
    b.add_line((-2.5, -0.6), (2.5, -0.6), dxfattribs={"layer": "AGUA-SIMBOLO"})
    b.add_line((-1.5, -1.2), (1.5, -1.2), dxfattribs={"layer": "AGUA-SIMBOLO"})
    b = doc.blocks.new("SIMB-CORTE")
    b.add_solid([(0, 0), (0, 4), (3, 0)], dxfattribs={"layer": "CORTES"})
    b.add_line((0, 0), (0, -6), dxfattribs={"layer": "CORTES"})
    b = doc.blocks.new("SIMB-NORTE")
    b.add_circle((0, 0), 8, dxfattribs={"layer": "TEXTOS"})
    b.add_solid([(0, 10), (-3, -5), (0, -2)], dxfattribs={"layer": "TEXTOS"})
    b.add_lwpolyline([(0, 10), (3, -5), (0, -2)], close=True, dxfattribs={"layer": "TEXTOS"})
    b.add_text("N", height=4, dxfattribs={"layer": "TEXTOS"}).set_placement((0, 12), align=TA.MIDDLE_CENTER)
    # barras longitudinales vistas en seccion: circulo relleno (radio 1 unidad; se inserta con escala = lam.f x 1.3 -> 1.3 mm de radio en papel)
    for nombre, rad in (("ACERO-38", 1.0), ("ACERO-12", 1.25)):
        b = doc.blocks.new(nombre)
        b.add_circle((0, 0), rad, dxfattribs={"layer": "ACERO-PUNTOS", "color": 5})
        h = b.add_hatch(dxfattribs={"layer": "ACERO-PUNTOS", "color": 5}); h.set_solid_fill(color=5)
        h.paths.add_polyline_path([(-rad, 0, 1.0), (rad, 0, 1.0)], is_closed=True)
    b = doc.blocks.new("REGISTRO-PLANTA")
    b.add_lwpolyline([(-0.35, -0.35), (0.35, -0.35), (0.35, 0.35), (-0.35, 0.35)], close=True, dxfattribs={"layer": "MARCO-METALICO"})
    b.add_lwpolyline([(-0.30, -0.30), (0.30, -0.30), (0.30, 0.30), (-0.30, 0.30)], close=True, dxfattribs={"layer": "REGISTRO"})
    for k in range(-5, 6):
        d = k * 0.1133
        a = (max(-0.29, d - 0.29), max(-0.29, -0.29 - d)); bb = (min(0.29, d + 0.29), min(0.29, 0.29 - d))
        p1 = (-0.29 + max(0, d), -0.29 - min(0, d)); p2 = (0.29 + min(0, d), 0.29 - max(0, d))
        b.add_line(p1, p2, dxfattribs={"layer": "REGISTRO-TAPA"})
    b.add_circle((-0.12, 0), 0.015, dxfattribs={"layer": "MARCO-METALICO"})
    b.add_circle((0.12, 0), 0.015, dxfattribs={"layer": "MARCO-METALICO"})
    b = doc.blocks.new("SIMB-CUNETA-LLEGA")   # ventana de empalme en planta
    b.add_lwpolyline([(-0.2, 0), (-0.2, -0.6), (0.2, -0.6), (0.2, 0)], dxfattribs={"layer": "CUNETA"})
    b.add_lwpolyline([(-0.3, -0.6), (-0.3, -1.4), (0.3, -1.4), (0.3, -0.6)], dxfattribs={"layer": "CUNETA"})


# ----------------------------------------------------------------------------
class Lamina:
    """Una lamina A1 (841 x 594 mm) dibujada en el modelo con origen (ox, oy) y escala 1:esc."""
    A1 = (841.0, 594.0)

    def __init__(self, doc, ox, oy, esc, codigo, titulo, subtitulo):
        self.doc, self.msp = doc, doc.modelspace()
        self.ox, self.oy, self.esc, self.f = ox, oy, esc, esc / 1000.0
        self.codigo, self.titulo, self.subtitulo = codigo, titulo, subtitulo
        self.dimstyle = f"COT-{esc}" if esc in ESCALAS else "COT-25"
        self.marco()
        self.rotulo()

    # --- conversion papel (mm) -> modelo (m)
    def P(self, xmm, ymm):
        return (self.ox + xmm * self.f, self.oy + ymm * self.f)

    def mm(self, v):
        return v * self.f

    # --- primitivas
    def linea(self, p1, p2, capa, **kw):
        a = {"layer": capa}; a.update(kw)
        return self.msp.add_line(p1, p2, dxfattribs=a)

    def poli(self, pts, capa, cerrada=False, ancho=0.0, **kw):
        a = {"layer": capa}; a.update(kw)
        if ancho: a["const_width"] = ancho
        return self.msp.add_lwpolyline(pts, close=cerrada, dxfattribs=a)

    def rect(self, x1, y1, x2, y2, capa, **kw):
        return self.poli([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], capa, cerrada=True, **kw)

    def circulo(self, c, r, capa):
        return self.msp.add_circle(c, r, dxfattribs={"layer": capa})

    def solido(self, pts, capa):
        e = self.msp.add_solid(pts, dxfattribs={"layer": capa})
        if capa in COLOR_RGB: e.rgb = COLOR_RGB[capa]      # color verdadero en la entidad: igual en AutoCAD y en cualquier visor
        return e

    def texto(self, p, t, hmm=2.5, capa="TEXTOS", al=TA.LEFT, rot=0, estilo="STANDARD", color=None):
        a = {"layer": capa, "style": estilo, "rotation": rot}
        if color is not None: a["color"] = color
        e = self.msp.add_text(t, height=hmm * self.f, dxfattribs=a)
        e.set_placement(p, align=al)
        return e

    def textos(self, p, lineas, hmm=2.5, capa="TEXTOS", al=TA.LEFT, inter=1.6):
        x, y = p
        for i, t in enumerate(lineas):
            self.texto((x, y - i * hmm * inter * self.f), t, hmm, capa, al)

    def bloque(self, nombre, p, escala=None, rot=0, capa=None):
        s = escala if escala is not None else self.f
        a = {"xscale": s, "yscale": s, "rotation": rot}
        if capa: a["layer"] = capa
        return self.msp.add_blockref(nombre, p, dxfattribs=a)

    def cota(self, p1, p2, dist_mm, horizontal=True, texto=None, estilo=None, angulo=None):
        """Cota lineal alineada (DIMENSION) entre p1 y p2, con linea de cota a dist_mm (papel) del lado positivo."""
        ds = estilo or self.dimstyle
        d = dist_mm * self.f
        if angulo is None:
            if horizontal:
                base = (p1[0], max(p1[1], p2[1]) + d) if d >= 0 else (p1[0], min(p1[1], p2[1]) + d)
                dim = self.msp.add_linear_dim(base=base, p1=p1, p2=p2, dimstyle=ds, dxfattribs={"layer": "COTAS"}, text=texto or "<>")
            else:
                base = (max(p1[0], p2[0]) + d, p1[1]) if d >= 0 else (min(p1[0], p2[0]) + d, p1[1])
                dim = self.msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=90, dimstyle=ds, dxfattribs={"layer": "COTAS"}, text=texto or "<>")
        else:
            dim = self.msp.add_aligned_dim(p1=p1, p2=p2, distance=d, dimstyle=ds, dxfattribs={"layer": "COTAS"}, text=texto or "<>")
        dim.render()
        return dim

    def achurado(self, pts, capa="CONCRETO-ACHURADO", patron="ANSI31", escala_mm=1.0):
        h = self.msp.add_hatch(dxfattribs={"layer": capa})
        h.set_pattern_fill(patron, scale=escala_mm * self.f * 25.4 / 25.4 * 10, angle=0)
        h.paths.add_polyline_path(pts, is_closed=True)
        return h

    def relleno(self, pts, capa):
        h = self.msp.add_hatch(dxfattribs={"layer": capa})
        if capa in COLOR_RGB:
            h.rgb = COLOR_RGB[capa]; h.set_solid_fill(rgb=COLOR_RGB[capa])
        else:
            h.set_solid_fill()
        h.paths.add_polyline_path(pts, is_closed=True)
        return h

    def flecha(self, p_from, p_to, capa="LLAMADAS", tam_mm=2.2):
        """Linea con punta de flecha (triangulo relleno) en p_to."""
        self.linea(p_from, p_to, capa)
        dx, dy = p_to[0] - p_from[0], p_to[1] - p_from[1]; L = math.hypot(dx, dy)
        if L < 1e-9: return
        ux, uy = dx / L, dy / L; t = tam_mm * self.f; w = 0.35 * t
        base = (p_to[0] - ux * t, p_to[1] - uy * t)
        tri = [p_to, (base[0] - uy * w, base[1] + ux * w), (base[0] + uy * w, base[1] - ux * w)]
        self.solido([tri[0], tri[1], tri[2], tri[2]], capa)

    def llamada(self, p_obj, p_txt, lineas, hmm=2.0, capa="LLAMADAS", al=TA.LEFT):
        """Llamada con flecha: texto en p_txt, tramo horizontal de apoyo y linea con punta de flecha hasta el objeto."""
        apoyo = 4.0 * self.f
        if al == TA.LEFT:
            p_ap = (p_txt[0] - apoyo, p_txt[1]); self.linea(p_txt, p_ap, capa)
        else:
            p_ap = (p_txt[0] + apoyo, p_txt[1]); self.linea(p_txt, p_ap, capa)
        self.flecha(p_ap, p_obj, capa)
        dx = 1.0 * self.f if al == TA.LEFT else -1.0 * self.f
        self.textos((p_txt[0] + dx, p_txt[1] + 0.3 * hmm * self.f), lineas, hmm, "TEXTOS", al)

    def nivel(self, p, cota, texto=None, lado=1, hmm=2.0):
        self.bloque("SIMB-NIVEL", p, self.f, capa="NIVELES")
        self.texto((p[0] + lado * 3.5 * self.f, p[1] + 2.6 * self.f), texto or ("%.2f" % cota), hmm, "NIVELES", TA.LEFT if lado > 0 else TA.RIGHT)

    def titulo_vista(self, xmm, ymm, titulo, sub=None, ancho_mm=90):
        p = self.P(xmm, ymm)
        self.texto(p, titulo, 4.0, "TITULOS", TA.MIDDLE_CENTER)
        self.linea(self.P(xmm - ancho_mm / 2, ymm - 3.5), self.P(xmm + ancho_mm / 2, ymm - 3.5), "TITULOS")
        if sub: self.texto(self.P(xmm, ymm - 7.5), sub, 2.2, "TEXTOS", TA.MIDDLE_CENTER)

    # --- marco y rotulo (formato de las laminas del tramo CAR Mujeres)
    def marco(self):
        W, H = self.A1
        self.rect(*self.P(0, 0), *self.P(W, H), "MARCO")
        self.rect(*self.P(25, 10), *self.P(W - 10, H - 10), "MARCO", const_width=0.6 * self.f)

    def rotulo(self):
        W, H = self.A1
        x0, y0, x1, y1 = W - 10 - 185, 10, W - 10, 10 + 95
        self.rect(*self.P(x0, y0), *self.P(x1, y1), "ROTULO", const_width=0.5 * self.f)
        ys = [y1 - 22, y1 - 40, y1 - 52, y1 - 62, y1 - 74, y1 - 85]
        for y in ys: self.linea(self.P(x0, y), self.P(x1, y), "ROTULO")
        t = lambda x, y, s, h=2.0, al=TA.LEFT, capa="ROTULO-TEXTO": self.texto(self.P(x, y), s, h, capa, al)
        t(x0 + 2, y1 - 3.5, "PROYECTO:", 2.0)
        t(x0 + 2, y1 - 8, PROYECTO[0], 1.6); t(x0 + 2, y1 - 11.5, PROYECTO[1], 1.6)
        t(x0 + 2, y1 - 17.5, "ENTIDAD: GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO", 1.6)
        t(x0 + 2, y1 - 27, UBICACION, 1.8); t(x0 + 2, y1 - 33, ESPECIALIDAD, 1.8)
        t(x0 + 2, y1 - 44.5, "PLANO:", 2.0); t(x0 + 14, y1 - 44.5, self.titulo, 2.4)
        t(x0 + 14, y1 - 49, self.subtitulo, 1.8)
        t(x0 + 2, y1 - 57.5, "PROYECTISTA: ______________________        CIP: ________", 1.8)
        t(x0 + 2, y1 - 68, "ELABORADO: " + ELABORADO, 1.8)
        self.linea(self.P(x0 + 125, y1 - 62), self.P(x0 + 125, y0), "ROTULO")
        self.linea(self.P(x0 + 165, y1 - 74), self.P(x0 + 165, y0), "ROTULO")
        t(x0 + 127, y1 - 68, "ESCALA:", 1.8); t(x0 + 143, y1 - 68, "1/%d" % self.esc, 2.4)
        t(x0 + 2, y1 - 79.5, "REVISADO: ________________", 1.8)
        t(x0 + 127, y1 - 79.5, "FECHA:", 1.8); t(x0 + 143, y1 - 79.5, FECHA, 2.0)
        t(x0 + 167, y1 - 79.5, "LAMINA:", 1.8)
        t(x0 + 2, y1 - 91, "FIRMA Y SELLO:", 1.8); t(x0 + 127, y1 - 91, "REVISION: 00", 1.8)
        t(x0 + 167, y1 - 92, self.codigo, 6.0)

    def leyenda(self, xmm, ymm, items, hmm=2.0):
        """items: lista de (tipo, capa, texto); tipo: 'linea', 'rect', 'relleno', 'punto', 'circ', 'bloque:NOMBRE'."""
        p = self.P(xmm, ymm)
        self.texto(p, "LEYENDA", 3.0, "TITULOS", TA.LEFT)
        self.linea(self.P(xmm, ymm - 2), self.P(xmm + 30, ymm - 2), "TITULOS")
        y = ymm - 8
        for tipo, capa, txt in items:
            if tipo == "linea":
                self.linea(self.P(xmm, y + 1), self.P(xmm + 12, y + 1), capa)
            elif tipo == "linea2":
                self.linea(self.P(xmm, y + 1), self.P(xmm + 12, y + 1), capa, const_width=0.6 * self.f) if False else self.poli([self.P(xmm, y + 1), self.P(xmm + 12, y + 1)], capa, ancho=0.5 * self.f)
            elif tipo == "rect":
                self.rect(*self.P(xmm, y - 1), *self.P(xmm + 12, y + 3), capa)
            elif tipo == "relleno":
                self.rect(*self.P(xmm, y - 1), *self.P(xmm + 12, y + 3), capa)
                self.relleno([self.P(xmm, y - 1), self.P(xmm + 12, y - 1), self.P(xmm + 12, y + 3), self.P(xmm, y + 3)], capa)
            elif tipo == "achurado":
                self.rect(*self.P(xmm, y - 1), *self.P(xmm + 12, y + 3), "CONCRETO")
                self.achurado([self.P(xmm, y - 1), self.P(xmm + 12, y - 1), self.P(xmm + 12, y + 3), self.P(xmm, y + 3)], capa)
            elif tipo == "circ":
                self.circulo(self.P(xmm + 6, y + 1), 1.2 * self.f, capa)
            elif tipo.startswith("bloque:"):
                self.bloque(tipo.split(":")[1], self.P(xmm + 6, y + 1), self.f * 1.3, capa=capa)
            self.texto(self.P(xmm + 15, y + 1), txt, hmm, "LEYENDA", TA.MIDDLE_LEFT)
            y -= 5.5
        return y

    def notas(self, xmm, ymm, titulo, lineas, hmm=2.0):
        self.texto(self.P(xmm, ymm), titulo, 3.0, "TITULOS")
        self.linea(self.P(xmm, ymm - 2), self.P(xmm + 25, ymm - 2), "TITULOS")
        for i, t in enumerate(lineas):
            self.texto(self.P(xmm, ymm - 7 - i * 4.2), t, hmm, "TEXTOS-NOTAS")

    def tabla(self, xmm, ymm, cabeceras, filas, anchos_mm, hmm=1.8, alto_mm=4.5, titulo=None):
        """Tabla con lineas; devuelve y final (mm)."""
        if titulo:
            self.texto(self.P(xmm, ymm + 4), titulo, 3.0, "TITULOS"); ymm -= 2
        W = sum(anchos_mm); n = len(filas) + 1
        for i in range(n + 1):
            self.linea(self.P(xmm, ymm - i * alto_mm), self.P(xmm + W, ymm - i * alto_mm), "GRILLA" if 0 < i < n else "TEXTOS")
        x = xmm
        for a in anchos_mm + [0]:
            self.linea(self.P(x, ymm), self.P(x, ymm - n * alto_mm), "TEXTOS"); x += a
        x = xmm
        for j, h in enumerate(cabeceras):
            self.texto(self.P(x + anchos_mm[j] / 2, ymm - alto_mm / 2), h, hmm, "TEXTOS", TA.MIDDLE_CENTER); x += anchos_mm[j]
        for i, fr in enumerate(filas):
            x = xmm
            for j, v in enumerate(fr):
                self.texto(self.P(x + anchos_mm[j] / 2, ymm - (i + 1.5) * alto_mm), str(v), hmm, "TEXTOS", TA.MIDDLE_CENTER); x += anchos_mm[j]
        return ymm - n * alto_mm


# ----------------------------------------------------------------------------
def iso(x, y, z, ex=1.0):
    """Proyeccion isometrica: x hacia la derecha-abajo (30 grados), y hacia la izquierda-abajo, z vertical (exagerado ex)."""
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    return (x * c30 - y * c30, -x * s30 - y * s30 + z * ex)


def caja_iso(lam, x0, y0, z0, dx, dy, dz, capas=("ISO-CONCRETO-SUP", "ISO-CONCRETO-LAT1", "ISO-CONCRETO-LAT2"), ex=1.0, origen=(0, 0), esc=1.0, aristas=True, solido=True, capa_aristas="ISO-ARISTAS"):
    """Dibuja un paralelepipedo en isometrico: caras visibles = superior, frontal (y = y0+dy) y lateral derecha (x = x0+dx).
    El observador mira desde +x, +y, +z (la esquina mas baja en el papel es la mas cercana)."""
    def T(x, y, z):
        px, py = iso(x, y, z, ex)
        return (origen[0] + px * esc, origen[1] + py * esc)
    sup = [T(x0, y0, z0 + dz), T(x0 + dx, y0, z0 + dz), T(x0 + dx, y0 + dy, z0 + dz), T(x0, y0 + dy, z0 + dz)]
    fre = [T(x0, y0 + dy, z0), T(x0 + dx, y0 + dy, z0), T(x0 + dx, y0 + dy, z0 + dz), T(x0, y0 + dy, z0 + dz)]
    lat = [T(x0 + dx, y0, z0), T(x0 + dx, y0 + dy, z0), T(x0 + dx, y0 + dy, z0 + dz), T(x0 + dx, y0, z0 + dz)]
    for pts, capa in ((lat, capas[2]), (fre, capas[1]), (sup, capas[0])):
        if solido: lam.solido([pts[0], pts[1], pts[3], pts[2]], capa)
        if aristas: lam.poli(pts, capa_aristas, cerrada=True)
    return T
