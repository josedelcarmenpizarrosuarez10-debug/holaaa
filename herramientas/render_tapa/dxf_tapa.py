"""Lamina DP-06B (rev. 01): detalle del registro de limpieza con tapa 0.68 x 0.68 c/marco y contramarco. Papel A1 en mm."""
import math, sys, ezdxf
from ezdxf.enums import TextEntityAlignment as TA

OUT = sys.argv[1]
IN = 0.0254
CM_L, CM_T = 2 * IN, 3 / 16 * IN
MT_L, MT_T = 1.5 * IN, 1 / 8 * IN
D38, D12 = 3 / 8 * IN, 1 / 2 * IN
REB, LUZ, RING, TAPA, ET = 0.35, 0.30, 0.45, 0.34, 0.08
BI, BW, LOSA, ENG = 0.40, 0.15, 0.10, 0.10
X = BI + BW

doc = ezdxf.new('R2010', setup=True, units=4)
msp = doc.modelspace()
doc.styles.add('ARIAL', font='arial.ttf')
doc.styles.add('ARIALB', font='arialbd.ttf')
LY = {  # nombre: (color ACI, grosor en 1/100 mm, tipo de linea)
    'LAMINA': (7, 50, 'Continuous'), 'MEMBRETE': (7, 25, 'Continuous'),
    'CONCRETO': (8, 50, 'Continuous'), 'CONCRETO_ACHURADO': (253, 13, 'Continuous'),
    'ANGULOS': (5, 50, 'Continuous'), 'ACERO': (1, 40, 'Continuous'), 'ACERO_LISO': (30, 40, 'Continuous'),
    'OCULTO': (8, 25, 'DASHED'), 'ACERO_OCULTO': (1, 25, 'DASHED'), 'EJES': (1, 18, 'CENTER'),
    'COTAS': (94, 18, 'Continuous'), 'TEXTO': (7, 25, 'Continuous'), 'TITULOS': (160, 50, 'Continuous'),
    'NOTAS_LLAMADA': (30, 25, 'Continuous'), 'CORTE': (1, 35, 'Continuous'), 'SELLO': (250, 25, 'Continuous'),
}
for n, (c, lw, lt) in LY.items():
    doc.layers.add(n, color=c, lineweight=lw, linetype=lt)
doc.header['$LTSCALE'] = 8

def dimstyle(nombre, lfac, dec=2, txt=2.8):
    ds = doc.dimstyles.new(nombre)
    ds.dxf.dimtxsty = 'ARIAL'; ds.dxf.dimtxt = txt; ds.dxf.dimlfac = lfac; ds.dxf.dimdec = dec
    ds.dxf.dimasz = 2.2; ds.dxf.dimtsz = 1.6; ds.dxf.dimexo = 1.5; ds.dxf.dimexe = 1.6; ds.dxf.dimgap = 1.0
    ds.dxf.dimtad = 1; ds.dxf.dimtih = 0; ds.dxf.dimtoh = 0; ds.dxf.dimclrd = 94; ds.dxf.dimclre = 94; ds.dxf.dimclrt = 7
    ds.dxf.dimzin = 0; ds.dxf.dimdsep = ord('.'); ds.dxf.dimtmove = 1
    return nombre
DS = {10: dimstyle('M_1_10', 0.01), 5: dimstyle('M_1_5', 0.005), 2: dimstyle('M_1_2', 0.002, dec=3), 1: dimstyle('MM_1_1', 1.0, dec=1)}

class Vista:
    def __init__(self, ox, oy, esc): self.ox, self.oy, self.k, self.esc = ox, oy, 1000 / esc, esc
    def p(self, x, y): return (self.ox + x * self.k, self.oy + y * self.k)
    def line(self, a, b, layer='CONCRETO'): msp.add_line(self.p(*a), self.p(*b), dxfattribs={'layer': layer})
    def pl(self, pts, layer='CONCRETO', close=False):
        msp.add_lwpolyline([self.p(*q) for q in pts], close=close, dxfattribs={'layer': layer})
    def rect(self, x0, y0, x1, y1, layer='CONCRETO'): self.pl([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, True)
    def fill(self, pts, color, layer):
        h = msp.add_hatch(color=color, dxfattribs={'layer': layer}); h.paths.add_polyline_path([self.p(*q) for q in pts], is_closed=True)
    def ring(self, ri_, ro_, color, layer='ANGULOS'):
        h = msp.add_hatch(color=color, dxfattribs={'layer': layer})
        h.paths.add_polyline_path([self.p(-ro_, -ro_), self.p(ro_, -ro_), self.p(ro_, ro_), self.p(-ro_, ro_)], is_closed=True, flags=1)
        h.paths.add_polyline_path([self.p(-ri_, -ri_), self.p(ri_, -ri_), self.p(ri_, ri_), self.p(-ri_, ri_)], is_closed=True, flags=16)
        self.rect(-ro_, -ro_, ro_, ro_, layer); self.rect(-ri_, -ri_, ri_, ri_, layer)
    def conc(self, pts, outline=True):
        h = msp.add_hatch(color=254, dxfattribs={'layer': 'CONCRETO_ACHURADO'})
        h.paths.add_polyline_path([self.p(*q) for q in pts], is_closed=True)
        if outline: self.pl(pts, 'CONCRETO', True)
    def fillrect(self, x0, y0, x1, y1, color, layer):
        self.fill([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, layer); self.rect(x0, y0, x1, y1, layer)
    def barra(self, x, y, d, layer='ACERO', color=1):
        r = max(d / 2 * self.k, 0.55)
        h = msp.add_hatch(color=color, dxfattribs={'layer': layer})
        h.paths.add_edge_path().add_arc(self.p(x, y), r, 0, 360)
        msp.add_circle(self.p(x, y), r, dxfattribs={'layer': layer})
    def dim(self, a, b, off, horiz=True, text=None, ds=None):
        a2, b2 = self.p(*a), self.p(*b)
        if horiz: base = (a2[0], a2[1] + off); ang = 0
        else: base = (a2[0] + off, a2[1]); ang = 90
        d = msp.add_linear_dim(base=base, p1=a2, p2=b2, angle=ang, dimstyle=ds or DS[self.esc], dxfattribs={'layer': 'COTAS'},
                               text=text if text else '<>')
        d.render()

def texto(x, y, s, h=3.5, layer='TEXTO', align=TA.LEFT, style='ARIAL', rot=0):
    t = msp.add_text(s, height=h, dxfattribs={'layer': layer, 'style': style, 'rotation': rot}); t.set_placement((x, y), align=align); return t

def mtexto(x, y, s, h=3.5, w=None, layer='TEXTO', style='ARIAL', attach=7):
    s = s.replace('\n', '\\P')
    m = msp.add_mtext(s, dxfattribs={'layer': layer, 'style': style, 'char_height': h, 'attachment_point': attach})
    m.set_location((x, y))
    if w: m.dxf.width = w
    return m

def llamada(anc, pos, s, h=3.5, w=60):
    """anc: punto en papel; pos: punto donde arranca el texto (en papel)"""
    msp.add_circle(anc, 0.7, dxfattribs={'layer': 'NOTAS_LLAMADA'})
    hh = msp.add_hatch(color=30, dxfattribs={'layer': 'NOTAS_LLAMADA'}); hh.paths.add_edge_path().add_arc(anc, 0.7, 0, 360)
    izq = pos[0] < anc[0]
    msp.add_lwpolyline([anc, pos, (pos[0] + (-4 if izq else 4), pos[1])], dxfattribs={'layer': 'NOTAS_LLAMADA'})
    mtexto(pos[0] + (-5 if izq else 5), pos[1] + h * 0.6, s, h, w, attach=(3 if izq else 1))

def titulo(x, y, s, esc, w=150):
    texto(x, y, s, 6, 'TITULOS', style='ARIALB')
    msp.add_line((x, y - 2), (x + w, y - 2), dxfattribs={'layer': 'TITULOS', 'lineweight': 70})
    texto(x, y - 7.5, esc, 4, 'TITULOS')

def corte_marca(v, x0, x1, y, letra):
    for x, s in ((x0, -1), (x1, 1)):
        a = v.p(x, y)
        msp.add_lwpolyline([(a[0] - s * 0, a[1]), (a[0] + s * 8, a[1])], dxfattribs={'layer': 'CORTE', 'const_width': 0.6})
        msp.add_lwpolyline([(a[0] + s * 8, a[1]), (a[0] + s * 8, a[1] - 5)], dxfattribs={'layer': 'CORTE', 'const_width': 0.6})
        msp.add_solid([(a[0] + s * 8 - 1.6, a[1] - 5), (a[0] + s * 8 + 1.6, a[1] - 5), (a[0] + s * 8, a[1] - 9)], dxfattribs={'layer': 'CORTE', 'color': 1})
        texto(a[0] + s * 8, a[1] + 2, letra, 5, 'CORTE', TA.BOTTOM_CENTER, 'ARIALB')
    v.line((x0, y), (x1, y), 'EJES')

# ---------------------------------------------------------------- lamina A1
W, H = 841, 594
msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs={'layer': 'LAMINA'})
msp.add_lwpolyline([(10, 10), (W - 10, 10), (W - 10, H - 10), (10, H - 10)], close=True, dxfattribs={'layer': 'LAMINA', 'lineweight': 70})

# ============ 1. PLANTA 1/10
v = Vista(105, 462, 10)
titulo(22, 572, 'A. PLANTA DEL REGISTRO', 'ESC. 1/10', 160)
# losa (vereda) con lineas de corte
v.pl([(-X, -0.62), (-X, 0.62)]); v.pl([(X, -0.62), (X, 0.62)])
for yy in (-0.62, 0.62):
    v.pl([(-X, yy), (-0.08, yy), (-0.05, yy + 0.03), (-0.01, yy - 0.03), (0.02, yy), (X, yy)], 'CONCRETO')
v.line((-BI, -0.62), (-BI, 0.62), 'OCULTO'); v.line((BI, -0.62), (BI, 0.62), 'OCULTO')
v.rect(-LUZ, -LUZ, LUZ, LUZ, 'OCULTO'); v.rect(-RING, -RING, RING, RING, 'OCULTO')
# refuerzo de borde (oculto) y anclajes
c = 0.375
for s in (-1, 1):
    v.line((s * c, -0.60), (s * c, 0.60), 'ACERO_OCULTO'); v.line((-0.51, s * c), (0.51, s * c), 'ACERO_OCULTO')
    for t in (-0.125, 0.125):
        v.line((s * (REB + CM_T), t), (s * 0.50, t), 'ACERO_OCULTO'); v.line((t, s * (REB + CM_T)), (t, s * 0.50), 'ACERO_OCULTO')
# contramarco (ala horizontal visible), marco y tapa
ro = REB + CM_L
v.ring(REB, ro, 5)
ri = TAPA - MT_L
v.ring(ri, TAPA, 140)
v.conc([(-ri, -ri), (ri, -ri), (ri, ri), (-ri, ri)])
for s in (-1, 1):
    v.rect(-0.08, s * 0.22 - 0.025, 0.08, s * 0.22 + 0.025, 'CONCRETO')
    v.line((-0.06, s * 0.22), (0.06, s * 0.22), 'ACERO_LISO')
corte_marca(v, -X - 0.05, X + 0.05, 0.125, 'A')
v.dim((-TAPA, -TAPA), (TAPA, -TAPA), -16 - 0)
v.dim((-REB, -REB), (REB, -REB), -24)
v.dim((-ro, -ro), (ro, -ro), -32)
v.dim((-X, -0.62), (X, -0.62), -41 + 6)
v.dim((-LUZ, LUZ), (LUZ, LUZ), 28)
v.dim((-RING, RING), (RING, RING), 28)
v.dim((ro, -0.125), (ro, 0.125), 30, horiz=False)
llamada(v.p(0.38, 0.38), (200, 552), 'Contramarco L 2"x2"x3/16"\nala horizontal enrasada con el piso', w=82)
llamada(v.p(0.33, 0.15), (200, 530), 'Marco de tapa L 1 1/2"x1 1/2"x1/8"', w=82)
llamada(v.p(0.12, 0.05), (200, 512), "Tapa de concreto f'c=210\n0.68 x 0.68 x 0.08 m", w=82)
llamada(v.p(0.06, 0.22), (200, 492), 'Asa 3/8" liso en bolsillo\n0.16 x 0.05 x 0.03 m', w=82)
llamada(v.p(0.50, -0.125), (200, 474), 'Anclajes 3/8" L=0.20 (8 und)', w=82)
llamada(v.p(0.375, -0.5), (200, 458), 'Refuerzo de borde\n2 de 1/2" por lado (oculto)', w=82)
llamada(v.p(0.45, -0.42), (200, 438), 'Borde engrosado 0.15 x 0.10\nbajo la losa (oculto)', w=82)
llamada(v.p(0.30, -0.30), (200, 420), 'Luz libre 0.60 x 0.60 (oculto)', w=82)
texto(v.p(-0.48, -0.50)[0], v.p(0, -0.50)[1], 'Losa superior (vereda)', 3, 'TEXTO', rot=90)

# ============ 2. CORTE A-A 1/10
v = Vista(405, 480, 10)
titulo(292, 572, 'B. CORTE A-A (por la linea de anclajes)', 'ESC. 1/10', 245)
for s in (-1, 1):
    pts = [(s * REB, 0), (s * X, 0), (s * X, -0.45), (s * BI, -0.45), (s * BI, -LOSA - ENG), (s * LUZ, -LOSA - ENG), (s * LUZ, -ET), (s * REB, -ET)]
    v.conc(pts)
    # contramarco
    v.fill([(s * REB, 0), (s * ro, 0), (s * ro, -CM_T), (s * (REB + CM_T), -CM_T), (s * (REB + CM_T), -CM_L), (s * REB, -CM_L)], 5, 'ANGULOS')
    # marco
    v.fill([(s * TAPA, 0), (s * (TAPA - MT_L), 0), (s * (TAPA - MT_L), -MT_T), (s * (TAPA - MT_T), -MT_T), (s * (TAPA - MT_T), -MT_L), (s * TAPA, -MT_L)], 140, 'ANGULOS')
    # anclaje en L
    v.pl([(s * (REB + CM_T), -0.03), (s * 0.50, -0.03), (s * 0.50, -0.08)], 'ACERO')
    # refuerzo de borde (barras en el eje del colector, cortadas)
    v.barra(s * c, -0.045, D12); v.barra(s * c, -0.155, D12)
    for yb in (-0.45,):
        v.pl([(s * X, yb), (s * BI, yb)], 'CONCRETO')
v.conc([(-(TAPA - MT_T), -MT_T), (TAPA - MT_T, -MT_T), (TAPA - MT_T, -ET), (-(TAPA - MT_T), -ET)])
v.line((-0.31, -0.055), (0.31, -0.055), 'ACERO')
for k in range(7): v.barra(-0.30 + 0.1 * k, -0.0455, D38)
v.line((-X - 0.08, 0), (-X, 0), 'CONCRETO'); v.line((X, 0), (X + 0.08, 0), 'CONCRETO')
texto(v.p(0, -0.36)[0], v.p(0, -0.36)[1], 'INTERIOR DEL COLECTOR', 3.0, align=TA.BOTTOM_CENTER)
texto(v.p(X + 0.02, 0.01)[0], v.p(0, 0.01)[1], 'NPT', 3.2)
v.dim((-TAPA, 0), (TAPA, 0), 22); v.dim((-REB, 0), (REB, 0), 30); v.dim((-ro, 0), (ro, 0), 38)
v.dim((-LUZ, -0.20), (LUZ, -0.20), -10); v.dim((-BI, -0.45), (BI, -0.45), -8); v.dim((BI, -0.45), (X, -0.45), -8)
v.dim((LUZ, -0.20), (RING, -0.20), -18)
v.dim((X, 0), (X, -LOSA), 14, horiz=False); v.dim((X, -LOSA), (X, -LOSA - ENG), 14, horiz=False)
v.dim((-X, 0), (-X, -ET), -14, horiz=False)
llamada(v.p(0.32, -0.08), (490, 458), 'Apoyo de la\ntapa 0.05', w=55)
llamada(v.p(-0.375, -0.155), (345, 442), 'Refuerzo de borde\n2 de 1/2" por lado', w=45)
llamada(v.p(0.36, -0.20), (490, 436), 'Borde engrosado\n0.15 x 0.10', w=55)
llamada(v.p(-0.45, -0.03), (345, 470), 'Anclaje 3/8" en L\n0.15 + 0.05', w=45)
llamada(v.p(0.0, -0.0455), (490, 540), 'Parrilla 3/8"\n@0.10', w=55)
llamada(v.p(-0.12, -0.055), (345, 505), 'Recubrimiento\n2.5 cm', w=45)

# ============ 3. DETALLE 1 - APOYO 1/2.5
v = Vista(445, 505, 2)
titulo(552, 572, 'C. DETALLE 1: APOYO DE LA TAPA', 'ESC. 1/2', 270)
x0 = 0.24
v.conc([(REB, 0), (0.53, 0), (0.53, -0.22), (BI, -0.22), (BI, -0.20), (LUZ, -0.20), (LUZ, -ET), (REB, -ET)])
v.fill([(REB, 0), (ro, 0), (ro, -CM_T), (REB + CM_T, -CM_T), (REB + CM_T, -CM_L), (REB, -CM_L)], 5, 'ANGULOS')
v.pl([(REB, 0), (ro, 0), (ro, -CM_T), (REB + CM_T, -CM_T), (REB + CM_T, -CM_L), (REB, -CM_L)], 'ANGULOS', True)
v.fill([(TAPA, 0), (TAPA - MT_L, 0), (TAPA - MT_L, -MT_T), (TAPA - MT_T, -MT_T), (TAPA - MT_T, -MT_L), (TAPA, -MT_L)], 140, 'ANGULOS')
v.pl([(TAPA, 0), (TAPA - MT_L, 0), (TAPA - MT_L, -MT_T), (TAPA - MT_T, -MT_T), (TAPA - MT_T, -MT_L), (TAPA, -MT_L)], 'ANGULOS', True)
v.conc([(x0, -MT_T), (TAPA - MT_L, -MT_T), (TAPA - MT_L, 0), (TAPA - MT_T, 0), (TAPA - MT_T, -MT_L), (TAPA, -MT_L), (TAPA, -ET), (x0, -ET)])
# corte de rotura
for xa, za, zb in ((x0, 0, -ET),):
    v.pl([(xa, za), (xa - 0.005, -0.03), (xa + 0.005, -0.05), (xa, zb)], 'CONCRETO')
v.pl([(0.53, -0.22), (0.52, -0.21), (0.54, -0.20)], 'CONCRETO')
v.pl([(REB + CM_T, -0.03), (0.50, -0.03), (0.50, -0.08)], 'ACERO')
v.barra(c, -0.045, D12); v.barra(c, -0.155, D12)
v.line((x0, -0.055), (0.31, -0.055), 'ACERO'); v.barra(0.30, -0.0455, D38)
v.dim((TAPA, 0), (REB, 0), 10, text='0.01')
v.dim((LUZ, -ET), (REB, -ET), -14, text='0.05')
v.dim((REB, 0), (ro, 0), 18, text='2"')
v.dim((TAPA - MT_L, 0), (TAPA, 0), 18, text='1 1/2"')
v.dim((0.53, 0), (0.53, -ET), 12, horiz=False)
v.dim((0.53, -ET), (0.53, -LOSA), 12, horiz=False, text='0.02')
v.dim((REB + CM_T, -0.03), (0.50, -0.03), -40, text='0.15')
v.dim((x0, -ET), (x0, -0.055), -10, horiz=False, text='0.025')
llamada(v.p(REB + 0.002, -0.04), (725, 558), 'Contramarco L 2"x2"x3/16"\nala vertical forra el rebaje', w=95)
llamada(v.p(ro - 0.01, -0.002), (725, 540), 'Ala horizontal enrasada\ncon el piso terminado', w=95)
llamada(v.p(TAPA - 0.01, -0.001), (725, 522), 'Marco L 1 1/2"x1 1/2"x1/8"', w=95)
llamada(v.p(0.345, -0.03), (725, 505), 'Holgura 1 cm por lado\n(0.70 - 0.68) / 2', w=95)
llamada(v.p(0.32, -ET), (725, 485), 'Tapa apoyada 5 cm\nsobre el concreto', w=95)
llamada(v.p(0.46, -0.03), (725, 465), 'Anclaje 3/8" soldado al\ncontramarco (L = 0.20)', w=95)
llamada(v.p(c, -0.155), (725, 440), 'Refuerzo de borde 1/2"', w=95)
llamada(v.p(0.30, -0.0455), (725, 422), 'Parrilla de la tapa 3/8" @0.10', w=95)

# ============ 4. TAPA - PLANTA DE ARMADO 1/5 y CORTE B-B 1/5
v = Vista(95, 242, 5)
titulo(22, 338, 'D. TAPA: PLANTA DE ARMADO', 'ESC. 1/5', 160)
v.ring(ri, TAPA, 140)
for k in range(7):
    u = -0.30 + 0.1 * k
    v.line((-0.31, u), (0.31, u), 'ACERO'); v.line((u, -0.31), (u, 0.31), 'ACERO')
for s in (-1, 1):
    v.rect(-0.08, s * 0.22 - 0.025, 0.08, s * 0.22 + 0.025, 'CONCRETO')
    v.pl([(-0.155, s * 0.22), (-0.06, s * 0.22)], 'ACERO_LISO'); v.pl([(0.06, s * 0.22), (0.155, s * 0.22)], 'ACERO_LISO')
    msp.add_lwpolyline([v.p(-0.06, s * 0.22), v.p(0.06, s * 0.22)], dxfattribs={'layer': 'ACERO_LISO', 'const_width': 1.0})
corte_marca(v, -TAPA - 0.04, TAPA + 0.04, -0.22, 'B')
v.dim((-TAPA, TAPA), (TAPA, TAPA), 12); v.dim((-0.31, -TAPA), (0.31, -TAPA), -12)
v.dim((-0.30, -TAPA), (-0.20, -TAPA), -22, text='0.10')
v.dim((TAPA, -0.30), (TAPA, 0.30), 14, horiz=False, text='6 @ 0.10 = 0.60')
v.dim((-0.08, 0.22 + 0.025), (0.08, 0.22 + 0.025), 10)
v.dim((-TAPA, 0), (-TAPA, 0.22), -12, horiz=False)
llamada(v.p(0.2, 0.0), (190, 300), '7 barras 3/8" en X\nL = 0.62', w=85)
llamada(v.p(0.0, -0.1), (190, 282), '7 barras 3/8" en Y\nL = 0.62', w=85)
llamada(v.p(0.0, 0.22), (190, 264), 'Asa 3/8" liso (2 und)\n0.40 m desarrollado', w=85)
llamada(v.p(TAPA - 0.01, -0.2), (190, 240), 'Marco L 1 1/2"\n(perimetro 2.72 m)', w=85)

v = Vista(95, 112, 5)
texto(22, 140, 'CORTE B-B (por el asa)  ESC. 1/5', 4.5, 'TITULOS', style='ARIALB')
v.conc([(-ri, -MT_T), (-0.08, -MT_T), (-0.08, -0.03), (0.08, -0.03), (0.08, -MT_T), (ri, -MT_T), (ri, -ET), (-ri, -ET)])
for s in (-1, 1):
    v.fill([(s * TAPA, 0), (s * (TAPA - MT_L), 0), (s * (TAPA - MT_L), -MT_T), (s * (TAPA - MT_T), -MT_T), (s * (TAPA - MT_T), -MT_L), (s * TAPA, -MT_L)], 140, 'ANGULOS')
v.conc([(TAPA - MT_T, -MT_L), (TAPA, -MT_L), (TAPA, -ET), (TAPA - MT_T, -ET)], outline=False)
v.conc([(-TAPA, -MT_L), (-TAPA + MT_T, -MT_L), (-TAPA + MT_T, -ET), (-TAPA, -ET)], outline=False)
msp.add_lwpolyline([v.p(-0.155, -0.06), v.p(-0.06, -0.06), v.p(-0.06, -0.015), v.p(0.06, -0.015), v.p(0.06, -0.06), v.p(0.155, -0.06)],
                   dxfattribs={'layer': 'ACERO_LISO', 'const_width': D38 * 200})
v.line((-0.31, -0.055), (0.31, -0.055), 'ACERO')
for k in range(7): v.barra(-0.30 + 0.1 * k, -0.0455, D38)
v.dim((-TAPA, 0), (TAPA, 0), 14); v.dim((TAPA, 0), (TAPA, -ET), 12, horiz=False)
v.dim((-TAPA, -ET), (-TAPA, -0.055), -10, horiz=False, text='0.025')
v.dim((-0.08, -0.03), (0.08, -0.03), -26)
llamada(v.p(0.0, -0.015), (190, 122), 'Agarradera del asa en el\nbolsillo (no sobresale)', w=85)
llamada(v.p(0.13, -0.06), (190, 104), 'Gancho del asa anclado\nen el concreto', w=85)

# ============ 5. CONTRAMARCO CON ANCLAJES 1/10 + PERFILES 1/1
v = Vista(350, 252, 10)
titulo(292, 338, 'E. CONTRAMARCO CON ANCLAJES', 'ESC. 1/10', 140)
v.ring(REB, ro, 5)
for s in (-1, 1):
    v.line((-ro, s * ro), (-REB, s * REB), 'ANGULOS'); v.line((ro, s * ro), (REB, s * REB), 'ANGULOS')
    for t in (-0.125, 0.125):
        v.line((s * ro, t), (s * 0.50, t), 'ACERO'); v.line((t, s * ro), (t, s * 0.50), 'ACERO')
        v.barra(s * 0.50, t, D38); v.barra(t, s * 0.50, D38)
v.dim((-REB, -0.50), (REB, -0.50), -10); v.dim((-0.125, -0.50), (0.125, -0.50), -18)
v.dim((ro, 0.125), (0.50, 0.125), 22, text='0.10')
llamada(v.p(-0.37, 0.2), (300, 180), 'Esquinas a 45 grados\ny soldadas', w=55)
llamada(v.p(0.5, -0.125), (402, 180), 'Anclaje 3/8":\n0.15 + 0.05', w=40)

titulo(445, 338, 'F. PERFILES DE ANGULOS', 'ESC. 1/1 (cotas en mm)', 130)
def perfil(ox, oy, L, t, nombre):
    Lm, tm = L * 1000, t * 1000
    pts = [(ox, oy), (ox + Lm, oy), (ox + Lm, oy + tm), (ox + tm, oy + tm), (ox + tm, oy + Lm), (ox, oy + Lm)]
    h = msp.add_hatch(color=5, dxfattribs={'layer': 'ANGULOS'}); h.paths.add_polyline_path(pts, is_closed=True)
    msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'ANGULOS'})
    for a, b, base, ang in (((ox, oy), (ox + Lm, oy), (ox, oy - 7), 0), ((ox, oy), (ox, oy + Lm), (ox - 7, oy), 90),
                            ((ox + Lm, oy), (ox + Lm, oy + tm), (ox + Lm + 7, oy), 90)):
        msp.add_linear_dim(base=base, p1=a, p2=b, angle=ang, dimstyle=DS[1], dxfattribs={'layer': 'COTAS'}).render()
    mtexto(ox + Lm + 14, oy + Lm, nombre, 3.2, 60, attach=1)
perfil(462, 252, CM_L, CM_T, 'CONTRAMARCO\nL 2" x 2" x 3/16"\n3.63 kg/m\n4 x 0.70 = 2.80 m\n10.2 kg / registro')
perfil(462, 172, MT_L, MT_T, 'MARCO DE TAPA\nL 1 1/2" x 1 1/2" x 1/8"\n1.83 kg/m\n4 x 0.68 = 2.72 m\n5.0 kg / registro')

# ============ 6. ISOMETRICO DE DESPIECE (lineas) 1/10
iso_o = (668, 198); kk = 68
c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
def P(x, y, z): return (iso_o[0] + (x - y) * c30 * kk, iso_o[1] + ((x + y) * s30 + z) * kk)
def isoline(a, b, layer): msp.add_line(P(*a), P(*b), dxfattribs={'layer': layer})
def isosq(r, z, layer, cx=0, cy=0):
    msp.add_lwpolyline([P(cx - r, cy - r, z), P(cx + r, cy - r, z), P(cx + r, cy + r, z), P(cx - r, cy + r, z)], close=True, dxfattribs={'layer': layer})
def isobox(x0, x1, y0, y1, z0, z1, layer):
    for a, b in (((x0, y0, z1), (x1, y0, z1)), ((x1, y0, z1), (x1, y1, z1)), ((x1, y1, z1), (x0, y1, z1)), ((x0, y1, z1), (x0, y0, z1)),
                 ((x0, y0, z0), (x0, y0, z1)), ((x1, y0, z0), (x1, y0, z1)), ((x0, y1, z0), (x0, y1, z1)),
                 ((x0, y0, z0), (x1, y0, z0)), ((x0, y0, z0), (x0, y1, z0))):
        isoline(a, b, layer)
titulo(590, 338, 'G. ISOMETRICO DE DESPIECE', 'SIN ESCALA', 235)
# losa con abertura
isobox(-X, X, -0.6, 0.6, -0.10, 0, 'CONCRETO')
isosq(REB, 0, 'CONCRETO'); isosq(LUZ, -ET, 'OCULTO')
for q in ((-REB, -REB), (REB, -REB), (-REB, REB)): isoline((q[0], q[1], 0), (q[0], q[1], -ET), 'CONCRETO')
# contramarco +0.30
z = 0.30
isosq(ro, z, 'ANGULOS'); isosq(REB, z, 'ANGULOS'); isosq(REB, z - CM_L, 'ANGULOS')
for q in ((-REB, -REB), (REB, -REB), (-REB, REB)): isoline((q[0], q[1], z), (q[0], q[1], z - CM_L), 'ANGULOS')
for s in (-1, 1):
    for t in (-0.125, 0.125):
        msp.add_lwpolyline([P(s * ro, t, z - 0.03), P(s * 0.50, t, z - 0.03), P(s * 0.50, t, z - 0.08)], dxfattribs={'layer': 'ACERO'})
        msp.add_lwpolyline([P(t, s * ro, z - 0.03), P(t, s * 0.50, z - 0.03), P(t, s * 0.50, z - 0.08)], dxfattribs={'layer': 'ACERO'})
# parrilla +0.55
z = 0.55
for k in range(7):
    u = -0.30 + 0.1 * k
    isoline((-0.31, u, z - 0.055), (0.31, u, z - 0.055), 'ACERO'); isoline((u, -0.31, z - 0.045), (u, 0.31, z - 0.045), 'ACERO')
# asas +0.80
z = 0.80
for s in (-1, 1):
    y = s * 0.22
    msp.add_lwpolyline([P(-0.155, y, z - 0.06), P(-0.06, y, z - 0.06), P(-0.06, y, z - 0.015), P(0.06, y, z - 0.015), P(0.06, y, z - 0.06), P(0.155, y, z - 0.06)],
                       dxfattribs={'layer': 'ACERO_LISO'})
# tapa +1.05
z = 1.05
isobox(-ri, ri, -ri, ri, z - ET, z - MT_T, 'CONCRETO')
for s in (-1, 1):
    msp.add_lwpolyline([P(-0.08, s * 0.22 - 0.025, z - MT_T), P(0.08, s * 0.22 - 0.025, z - MT_T), P(0.08, s * 0.22 + 0.025, z - MT_T), P(-0.08, s * 0.22 + 0.025, z - MT_T)],
                       close=True, dxfattribs={'layer': 'CONCRETO'})
# marco +1.33
z = 1.33
isosq(TAPA, z, 'ANGULOS'); isosq(ri, z, 'ANGULOS'); isosq(TAPA, z - MT_L, 'ANGULOS')
for q in ((-TAPA, -TAPA), (TAPA, -TAPA), (-TAPA, TAPA)): isoline((q[0], q[1], z), (q[0], q[1], z - MT_L), 'ANGULOS')
for lab, pt, pos in (('Marco de tapa\nL 1 1/2"', (TAPA, 0, 1.33), (760, 318)), ("Concreto de la\ntapa f'c=210", (ri, 0.1, 1.0), (760, 296)),
                     ('Asas 3/8" liso (2)', (0.155, 0.22, 0.74), (760, 274)), ('Parrilla 3/8"\n@0.10', (0.31, 0.1, 0.495), (760, 254)),
                     ('Contramarco L 2"\ncon anclajes', (ro, 0.1, 0.30), (760, 228)), ('Losa con rebaje\n0.70 y luz 0.60', (X, 0.3, 0), (760, 192))):
    llamada(P(*pt), pos, lab, 3.3, 66)

# ============ 7. CUADRO DE MATERIALES, NOTAS Y MEMBRETE
tx, ty = 292, 142
texto(tx, ty, 'H. MATERIALES POR REGISTRO', 4.5, 'TITULOS', style='ARIALB')
filas = [('Contramarco L 2"x2"x3/16" (2.80 m)', 'kg', '10.16'), ('Marco L 1 1/2"x1 1/2"x1/8" (2.72 m)', 'kg', '4.98'),
         ('Anclajes 3/8" L = 0.20 m', 'und', '8'), ("Concreto tapa f'c=210", 'm3', '0.037'), ('Acero tapa 3/8" (14 x 0.62 m)', 'kg', '4.86'),
         ('Asas 3/8" liso (2 x 0.40 m)', 'kg', '0.45'), ('Refuerzo de borde 1/2" (8 x 1.40 m)', 'kg', '11.13'),
         ('Borde engrosado (3.00 x 0.15 x 0.10)', 'm3', '0.045'), ('Pintura en angulos', 'm2', '0.98')]
cw = [92, 14, 18]; rh = 6.2; yy = ty - 5
msp.add_lwpolyline([(tx, yy), (tx + sum(cw), yy), (tx + sum(cw), yy - rh * (len(filas) + 1)), (tx, yy - rh * (len(filas) + 1))], close=True, dxfattribs={'layer': 'MEMBRETE'})
for i, row in enumerate([('DESCRIPCION', 'UND', 'CANT.')] + filas):
    y1 = yy - rh * (i + 1)
    msp.add_line((tx, y1), (tx + sum(cw), y1), dxfattribs={'layer': 'MEMBRETE'})
    x = tx
    for j, cell in enumerate(row):
        texto(x + 1.5 if j == 0 else x + cw[j] / 2, y1 + 1.6, cell, 3.0, 'TEXTO', TA.LEFT if j == 0 else TA.BOTTOM_CENTER, 'ARIALB' if i == 0 else 'ARIAL')
        x += cw[j]
x = tx
for wj in cw[:-1]:
    x += wj; msp.add_line((x, yy), (x, yy - rh * (len(filas) + 1)), dxfattribs={'layer': 'MEMBRETE'})
texto(tx, yy - rh * (len(filas) + 1) - 5, 'Registros: Hogar de Refugio 10 - CAR Mujeres 15 - CAR Varones 11', 2.8)

nx, ny = 430, 142
texto(nx, ny, 'NOTAS', 4.5, 'TITULOS', style='ARIALB')
notas = ["1. Concreto f'c=210 kg/cm2 en losa, borde engrosado y tapa. Acero fy=4200 kg/cm2; asas de 3/8\" liso.",
         '2. Angulos ASTM A36; soldadura E6011 1/8" en esquinas (corte a 45 grados) y en los anclajes.',
         '3. El contramarco se nivela y fija antes de vaciar la losa; su ala horizontal queda enrasada con el NPT.',
         '4. El marco se fabrica primero y sirve de encofrado lateral de la tapa. Recubrimiento de la parrilla 2.5 cm.',
         '5. Holgura 1 cm por lado entre marco y contramarco; la tapa apoya 5 cm sobre el concreto.',
         '6. Angulos con 2 manos de pintura anticorrosiva y 2 manos de esmalte.',
         '7. Peso de la tapa aprox. 94 kg: se retira entre 2 operarios con ganchos en las asas.',
         '8. Los registros no se ubican dentro de los cruces vehiculares.']
for i, n_ in enumerate(notas): texto(nx, ny - 7 - i * 5.3, n_, 3.0)
# membrete
bx, by = 590, 12
msp.add_lwpolyline([(bx, by), (W - 12, by), (W - 12, by + 78), (bx, by + 78)], close=True, dxfattribs={'layer': 'MEMBRETE', 'lineweight': 50})
for yl in (by + 58, by + 42, by + 24, by + 12): msp.add_line((bx, yl), (W - 12, yl), dxfattribs={'layer': 'MEMBRETE'})
msp.add_line((bx + 150, by), (bx + 150, by + 24), dxfattribs={'layer': 'MEMBRETE'})
mtexto(bx + 2, by + 76.5, 'PROYECTO: CREACION DEL SERVICIO DE ATENCION INTEGRAL A MUJERES VICTIMAS DE VIOLENCIA EN EL HOGAR DE REFUGIO TEMPORAL '
       'MUJERES VIOLENTADAS, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2675514', 2.5, 232, attach=1)
mtexto(bx + 2, by + 56, 'ENTIDAD: GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO\\PUBICACION: PREDIO RURAL LOS MANGOS - MORALES - SAN MARTIN\\PESPECIALIDAD: INSTALACIONES SANITARIAS - DRENAJE PLUVIAL', 2.5, 232, attach=1)
texto(bx + 2, by + 34, 'PLANO: DETALLE DE REGISTRO DE LIMPIEZA - TAPA 0.68 x 0.68', 3.4, style='ARIALB')
texto(bx + 2, by + 28, 'C/MARCO Y CONTRAMARCO, ANCLAJES Y REFUERZO DE BORDE', 3.4, style='ARIALB')
texto(bx + 2, by + 16, 'ELABORADO: HIDROCONSULT        PROYECTISTA: ________________  CIP: ______', 2.6)
texto(bx + 2, by + 4, 'REVISADO: ________________        FIRMA Y SELLO:', 2.6)
texto(bx + 153, by + 16, 'ESCALA: INDICADA   FECHA: OCT. 2026', 2.6)
texto(bx + 153, by + 4, 'REVISION: 01', 2.6)
texto(W - 16, by + 3, 'DP-06B', 9, 'TITULOS', TA.BOTTOM_RIGHT, 'ARIALB')

# leyenda de colores
lx, ly = 292, 34
texto(lx, ly + 8, 'LEYENDA', 3.5, 'TITULOS', style='ARIALB')
for i, (lab, col) in enumerate((('Concreto', 253), ('Angulos', 5), ('Acero corrugado', 1), ('Acero liso (asas)', 30))):
    x = lx + (i % 2) * 60; y = ly - (i // 2) * 8
    h = msp.add_hatch(color=col, dxfattribs={'layer': 'TEXTO'}); h.paths.add_polyline_path([(x, y), (x + 8, y), (x + 8, y + 4), (x, y + 4)], is_closed=True)
    texto(x + 11, y, lab, 3.0)

doc.saveas(OUT)
print('ok', OUT)
