"""Lamina DP-06B rev. 02: registro de limpieza con TAPA CIEGA de concreto armado 0.68 x 0.68 x 0.08 (vaciada aparte en
obra, sin marco ni contramarco metalico), apoyada en un rebaje de concreto 0.70 x 0.70 x 0.08 de la losa (luz libre 0.60 x 0.60),
con 2 asas de fierro liso 1/2" en cajuelas. Papel A1 en mm (1 unidad = 1 mm de papel).

Uso: python3 dxf_tapa_ciega.py <salida.dxf> <refugio|varones|mujeres>
"""
import math, sys, ezdxf
from ezdxf.enums import TextEntityAlignment as TA

OUT, PRY = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "refugio")
PROY = {
    "refugio": dict(b=0.80, bw=0.15, n=10, cb=0.40, nombre="HOGAR DE REFUGIO TEMPORAL (CUI 2675514)",
                    proyecto="CREACION DEL SERVICIO DE ATENCION INTEGRAL A MUJERES VICTIMAS DE VIOLENCIA EN EL HOGAR DE REFUGIO TEMPORAL MUJERES "
                             "VIOLENTADAS, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2675514",
                    ubic="PREDIO RURAL LOS MANGOS - MORALES - SAN MARTIN"),
    "varones": dict(b=0.60, bw=0.15, n=11, cb=0.40, nombre="CAR VARONES (CUI 2705619)",
                    proyecto="CREACION DEL SERVICIO DE PROTECCION INTEGRAL A NINAS, NINOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE "
                             "PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - VARONES, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2705619",
                    ubic="PREDIO ALDEA INFANTIL VIRGEN DEL PILAR - MORALES - SAN MARTIN"),
    "mujeres": dict(b=1.50, bw=0.10, n=15, cb=0.39, nombre="CAR MUJERES (CUI 2717013)",
                    proyecto="CREACION DEL SERVICIO DE PROTECCION INTEGRAL A NINAS, NINOS Y ADOLESCENTES SIN CUIDADOS PARENTALES O EN RIESGO DE "
                             "PERDERLOS EN CENTRO DE ACOGIDA RESIDENCIAL - MUJERES, DISTRITO DE MORALES, PROVINCIA Y DEPARTAMENTO DE SAN MARTIN - CUI N. 2717013",
                    ubic="PREDIO RURAL LOS MANGOS - MORALES - SAN MARTIN"),
}[PRY]
IN = 0.0254
D38, D12 = 3 / 8 * IN, 1 / 2 * IN
R, U, T, ET = 0.35, 0.30, 0.34, 0.08         # medio rebaje, media luz libre, media tapa, espesor de tapa = profundidad del rebaje
LOSA, ENG, RING = 0.10, 0.10, 0.45           # losa superior, borde engrosado (de la luz 0.30 a 0.45 del eje)
BI, BW = PROY["b"] / 2, PROY["bw"]
X = BI + BW
C = PROY["cb"]                               # refuerzo de borde 1/2" (2 barras por lado)
MURO = BI <= U + 1e-6                        # colector igual o mas angosto que la luz: en los lados largos el asiento es la cabeza del muro
ENG_PER = 2 * (2 * BI) if MURO else 4 * 0.75
YA, AG, PATA, GAN = 0.20, 0.075, 0.02, 0.15  # asas: eje a 0.20 del centro, medio agarre 0.075, pata 0.02, gancho 0.15
CJX, CJY, CJZ = 0.095, 0.03, 0.03            # cajuela: 0.19 x 0.06 x 0.03
ZA = -0.015                                  # nivel del agarre del asa
ZP1, ZP2 = -0.055, -0.0455                   # parrilla: barras en X (abajo) y en Y (arriba)
PESO_TAPA = (2 * T) ** 2 * ET * 2400

doc = ezdxf.new('R2010', setup=True, units=4)
msp = doc.modelspace()
doc.styles.add('ARIAL', font='arial.ttf')
doc.styles.add('ARIALB', font='arialbd.ttf')
LY = {
    'LAMINA': (7, 50, 'Continuous'), 'MEMBRETE': (7, 25, 'Continuous'),
    'CONCRETO': (8, 50, 'Continuous'), 'CONCRETO_ACHURADO': (253, 13, 'Continuous'), 'TAPA': (8, 50, 'Continuous'),
    'ACERO': (1, 40, 'Continuous'), 'ACERO_LISO': (30, 40, 'Continuous'),
    'OCULTO': (8, 25, 'DASHED'), 'ACERO_OCULTO': (1, 25, 'DASHED'), 'EJES': (1, 18, 'CENTER'),
    'COTAS': (94, 18, 'Continuous'), 'TEXTO': (7, 25, 'Continuous'), 'TITULOS': (160, 50, 'Continuous'),
    'NOTAS_LLAMADA': (30, 25, 'Continuous'), 'CORTE': (1, 35, 'Continuous'),
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


DS = {10: dimstyle('M_1_10', 0.01), 5: dimstyle('M_1_5', 0.005), 2: dimstyle('M_1_2', 0.002, dec=3)}


class Vista:
    def __init__(self, ox, oy, esc): self.ox, self.oy, self.k, self.esc = ox, oy, 1000 / esc, esc
    def p(self, x, y): return (self.ox + x * self.k, self.oy + y * self.k)
    def line(self, a, b, layer='CONCRETO'): msp.add_line(self.p(*a), self.p(*b), dxfattribs={'layer': layer})
    def pl(self, pts, layer='CONCRETO', close=False, w=0):
        a = {'layer': layer}
        if w: a['const_width'] = w
        msp.add_lwpolyline([self.p(*q) for q in pts], close=close, dxfattribs=a)
    def rect(self, x0, y0, x1, y1, layer='CONCRETO'): self.pl([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, True)
    def conc(self, pts, outline=True, layer='CONCRETO', color=254):
        h = msp.add_hatch(color=color, dxfattribs={'layer': 'CONCRETO_ACHURADO'})
        h.paths.add_polyline_path([self.p(*q) for q in pts], is_closed=True)
        if outline: self.pl(pts, layer, True)
    def barra(self, x, y, d, layer='ACERO', color=1):
        r = max(d / 2 * self.k, 0.55)
        h = msp.add_hatch(color=color, dxfattribs={'layer': layer})
        h.paths.add_edge_path().add_arc(self.p(x, y), r, 0, 360)
        msp.add_circle(self.p(x, y), r, dxfattribs={'layer': layer})
    def dim(self, a, b, off, horiz=True, text=None):
        a2, b2 = self.p(*a), self.p(*b)
        base = (a2[0], a2[1] + off) if horiz else (a2[0] + off, a2[1])
        d = msp.add_linear_dim(base=base, p1=a2, p2=b2, angle=0 if horiz else 90, dimstyle=DS[self.esc], dxfattribs={'layer': 'COTAS'},
                               text=text if text else '<>')
        d.render()


def texto(x, y, s, h=3.5, layer='TEXTO', align=TA.LEFT, style='ARIAL', rot=0):
    t = msp.add_text(s, height=h, dxfattribs={'layer': layer, 'style': style, 'rotation': rot}); t.set_placement((x, y), align=align); return t


def mtexto(x, y, s, h=3.5, w=None, layer='TEXTO', style='ARIAL', attach=7):
    m = msp.add_mtext(s.replace('\n', '\\P'), dxfattribs={'layer': layer, 'style': style, 'char_height': h, 'attachment_point': attach})
    m.set_location((x, y))
    if w: m.dxf.width = w
    return m


def llamada(anc, pos, s, h=3.3, w=70):
    msp.add_circle(anc, 0.7, dxfattribs={'layer': 'NOTAS_LLAMADA'})
    hh = msp.add_hatch(color=30, dxfattribs={'layer': 'NOTAS_LLAMADA'}); hh.paths.add_edge_path().add_arc(anc, 0.7, 0, 360)
    izq = pos[0] < anc[0]
    msp.add_lwpolyline([anc, pos, (pos[0] + (-4 if izq else 4), pos[1])], dxfattribs={'layer': 'NOTAS_LLAMADA'})
    mtexto(pos[0] + (-5 if izq else 5), pos[1] + h * 0.6, s, h, w, attach=(3 if izq else 1))


def titulo(x, y, s, esc, w=150):
    texto(x, y, s, 6, 'TITULOS', style='ARIALB')
    msp.add_line((x, y - 2), (x + w, y - 2), dxfattribs={'layer': 'TITULOS', 'lineweight': 70})
    texto(x, y - 7.5, esc, 4, 'TITULOS')


def corte_marca(v, a, b, letra, horiz=True):
    """Linea de corte entre a y b (coordenadas reales), con flechas hacia abajo / izquierda."""
    for q, s in ((a, -1), (b, 1)):
        P = v.p(*q)
        if horiz:
            e = (P[0] + s * 8, P[1]); f = (e[0], e[1] - 5)
            tri = [(f[0] - 1.6, f[1]), (f[0] + 1.6, f[1]), (f[0], f[1] - 4)]; tp = (e[0], e[1] + 2); al = TA.BOTTOM_CENTER
        else:
            e = (P[0], P[1] + s * 8); f = (e[0] - 5, e[1])
            tri = [(f[0], f[1] - 1.6), (f[0], f[1] + 1.6), (f[0] - 4, f[1])]; tp = (e[0] + 2, e[1]); al = TA.MIDDLE_LEFT
        msp.add_lwpolyline([P, e, f], dxfattribs={'layer': 'CORTE', 'const_width': 0.6})
        msp.add_solid(tri, dxfattribs={'layer': 'CORTE', 'color': 1})
        texto(tp[0], tp[1], letra, 5, 'CORTE', al, 'ARIALB')
    v.line(a, b, 'EJES')


def tapa_seccion(v, cajuela=False):
    """Tapa en seccion (z = 0 en el NPT): bisel 1 x 1 cm en los cantos superiores; con cajuela si el corte pasa por el asa."""
    if cajuela:
        pts = [(-T, -ET), (T, -ET), (T, -0.01), (T - 0.01, 0), (CJX, 0), (CJX, -CJZ), (-CJX, -CJZ), (-CJX, 0), (-T + 0.01, 0), (-T, -0.01)]
    else:
        pts = [(-T, -ET), (T, -ET), (T, -0.01), (T - 0.01, 0), (-T + 0.01, 0), (-T, -0.01)]
    v.conc(pts, layer='TAPA', color=253)


def parrilla(v, x_en_seccion=True):
    v.line((-0.31, ZP1), (0.31, ZP1), 'ACERO')
    for k in range(7): v.barra(-0.30 + 0.1 * k, ZP2, D38)


def asa_alzado(v, layer='ACERO_LISO', w=None):
    pts = [(-AG - GAN, ZA - PATA), (-AG, ZA - PATA), (-AG, ZA), (AG, ZA), (AG, ZA - PATA), (AG + GAN, ZA - PATA)]
    v.pl(pts, layer, w=w or D12 * v.k)


def lado_losa(v, s, xext, zfin, transversal):
    """Concreto de losa, borde engrosado y muro a un lado del registro (s = +1 / -1)."""
    if transversal:                                  # corte A-A: aparecen los muros del colector
        pts = [(s * R, 0), (s * xext, 0), (s * xext, zfin), (s * BI, zfin)]
        if BI > U + 1e-6:
            pts += ([(s * BI, -LOSA), (s * RING, -LOSA), (s * RING, -LOSA - ENG)] if BI >= RING else [(s * BI, -LOSA - ENG)]) + [(s * U, -LOSA - ENG)]
        pts += [(s * U, -ET), (s * R, -ET)]
    else:                                            # corte B-B (eje del colector): losa y borde engrosado
        pts = [(s * R, 0), (s * xext, 0), (s * xext, -LOSA), (s * RING, -LOSA), (s * RING, -LOSA - ENG), (s * U, -LOSA - ENG), (s * U, -ET), (s * R, -ET)]
    v.conc(pts)


# ---------------------------------------------------------------- lamina A1
W, H = 841, 594
msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs={'layer': 'LAMINA'})
msp.add_lwpolyline([(10, 10), (W - 10, 10), (W - 10, H - 10), (10, H - 10)], close=True, dxfattribs={'layer': 'LAMINA', 'lineweight': 70})

# ============ A. PLANTA DEL REGISTRO 1/10 (eje del colector vertical)
LY_ = 0.62
v = Vista(22 + (X + 0.05) * 100, 462, 10)
titulo(22, 572, 'A. PLANTA DEL REGISTRO', 'ESC. 1/10 - colector b = %.2f, muros e = %.2f' % (2 * BI, BW), 175)
for s in (-1, 1):
    v.line((s * X, -LY_), (s * X, LY_), 'CONCRETO'); v.line((s * BI, -LY_), (s * BI, LY_), 'OCULTO')
for yy in (-LY_, LY_):
    v.pl([(-X, yy), (-0.08, yy), (-0.05, yy + 0.03), (-0.01, yy - 0.03), (0.02, yy), (X, yy)], 'CONCRETO')
if MURO:
    for s in (-1, 1): v.rect(-BI, s * U, BI, s * RING, 'OCULTO')
else:
    v.rect(-min(RING, BI), -RING, min(RING, BI), RING, 'OCULTO')
v.rect(-U, -U, U, U, 'OCULTO')                       # luz libre bajo la tapa
v.rect(-R, -R, R, R, 'CONCRETO')                     # rebaje
v.conc([(-T, -T), (T, -T), (T, T), (-T, T)], layer='TAPA', color=253)
v.rect(-T + 0.01, -T + 0.01, T - 0.01, T - 0.01, 'TAPA')   # bisel
for s in (-1, 1):
    v.rect(-CJX, s * YA - CJY, CJX, s * YA + CJY, 'CONCRETO')
    v.pl([(-AG, s * YA), (AG, s * YA)], 'ACERO_LISO', w=1.2)
    v.line((s * C, -LY_ + 0.02), (s * C, LY_ - 0.02), 'ACERO_OCULTO'); v.line((-min(C + 0.25, X - 0.04), s * C), (min(C + 0.25, X - 0.04), s * C), 'ACERO_OCULTO')
corte_marca(v, (-X - 0.04, 0.0), (X + 0.04, 0.0), 'A')
corte_marca(v, (0.0, LY_ + 0.05), (0.0, -LY_ - 0.02), 'B', horiz=False)
v.dim((-T, T), (T, T), 10)
v.dim((-X, -LY_), (X, -LY_), -32)
v.dim((-BI, -LY_), (BI, -LY_), -42, text='%.2f (interior)' % (2 * BI))
v.dim((R, -U), (R, U), 14, horiz=False, text='0.60 (luz)')
v.dim((-R, -R), (-R, R), -12, horiz=False)
ax = 22 + (2 * X + 0.10) * 100 + 14
llamada(v.p(0.10, -0.10), (ax, 548), "Tapa ciega de concreto armado\nf'c=210, 0.68 x 0.68 x 0.08\n(vaciada aparte en obra)", w=80)
llamada(v.p(0.345, 0.25), (ax, 524), 'Holgura 1 cm por lado\ntapa 0.68 / rebaje 0.70', w=80)
llamada(v.p(0.06, YA), (ax, 506), 'Asa de fierro liso 1/2" en\ncajuela 0.19 x 0.06 x 0.03 (2 und)', w=80)
llamada(v.p(-0.25, -0.30), (ax, 486), 'Luz libre 0.60 x 0.60\nbajo la tapa (oculta)', w=80)
llamada(v.p(C, -0.50), (ax, 468), 'Refuerzo de borde 2 de 1/2"\npor lado, L = 1.40 (oculto)', w=80)
if MURO:
    llamada(v.p(0.12, -0.40), (ax, 448), 'Borde engrosado 0.15 x 0.10\nentre muros, 2 lados (oculto)', w=80)
    llamada(v.p(X - 0.05, 0.50), (ax, 428), 'En los lados largos la tapa\napoya en el rebaje sobre la\ncabeza de los muros', w=80)
else:
    llamada(v.p(0.40, 0.42), (ax, 448), 'Borde engrosado 0.15 x 0.10\nbajo la losa (oculto)', w=80)

# ============ B. CORTE A-A (transversal) 1/10
xa = 22 + 175 + 125
v = Vista(xa + (X + 0.10) * 100, 505, 10)
titulo(xa, 572, 'B. CORTE A-A (transversal al colector)', 'ESC. 1/10', 230)
for s in (-1, 1):
    lado_losa(v, s, X, -0.42, True)
    v.barra(s * C, -0.045, D12)
    if (BI > U + 1e-6 and C < min(BI, RING)) or C > BI: v.barra(s * C, -0.155, D12)
    v.pl([(s * X, -0.42), (s * (X - 0.02), -0.40), (s * (BI + 0.02), -0.44), (s * BI, -0.42)], 'CONCRETO')
tapa_seccion(v)
parrilla(v)
texto(v.p(0, -0.34)[0], v.p(0, -0.34)[1], 'INTERIOR DEL COLECTOR', 3.0, align=TA.BOTTOM_CENTER)
texto(v.p(X + 0.03, 0.005)[0], v.p(0, 0.005)[1], 'NPT (vereda)', 3.0)
v.dim((-T, 0), (T, 0), 14); v.dim((-R, 0), (R, 0), 22)
v.dim((-U, -0.22), (U, -0.22), -8, text='0.60 (luz)')
v.dim((-BI, -0.42), (BI, -0.42), -10); v.dim((BI, -0.42), (X, -0.42), -10)
v.dim((-X, 0), (-X, -LOSA), -10, horiz=False)
v.dim((X, 0), (X, -ET), 10, horiz=False)
if BI > U + 1e-6:
    v.dim((U, -LOSA), (U, -LOSA - ENG), -8, horiz=False)
xr = xa + 2 * (X + 0.10) * 100 + 8
llamada(v.p(0.2, -0.03), (xr, 556), 'Tapa ciega 0.68 x 0.08\nal ras del NPT', w=60)
llamada(v.p(0.33, -ET), (xr, 538), 'Asiento en el rebaje\n0.05 por lado', w=60)
llamada(v.p(0.1, ZP1), (xr, 520), 'Parrilla 3/8" @0.10 c/s', w=60)
if MURO:
    llamada(v.p(BI + 0.07, -0.20), (xr, 478), 'Cabeza del muro:\nasiento de la tapa', w=60)
else:
    llamada(v.p(U + 0.06, -0.15), (xr, 478), 'Borde engrosado\n0.15 x 0.10', w=60)
llamada(v.p(C, -0.045), (xr, 498), 'Refuerzo de borde\n2 de 1/2" por lado', w=60)

# ============ C. CORTE B-B (eje del colector) 1/10
v = Vista(xa + 0.72 * 100, 395, 10)
texto(xa, 432, 'C. CORTE B-B (por el eje del colector)  ESC. 1/10', 4.5, 'TITULOS', style='ARIALB')
for s in (-1, 1):
    lado_losa(v, s, 0.70, None, False)
    v.barra(s * C, -0.045, D12); v.barra(s * C, -0.155, D12)
    v.pl([(s * 0.70, 0.01), (s * 0.69, -0.03), (s * 0.71, -0.07), (s * 0.70, -0.11)], 'CONCRETO')
tapa_seccion(v, cajuela=False)
v.line((-0.31, ZP1), (0.31, ZP1), 'ACERO')
for k in range(7): v.barra(-0.30 + 0.1 * k, ZP2, D38)
v.dim((-R, 0), (R, 0), 12); v.dim((-U, -0.20), (U, -0.20), -8, text='0.60 (luz)')
v.dim((U, -0.20), (RING, -0.20), -8); v.dim((0.70, 0), (0.70, -LOSA), 8, horiz=False); v.dim((0.70, -LOSA), (0.70, -LOSA - ENG), 16, horiz=False)

# ============ D. DETALLE 1: ASIENTO DE LA TAPA 1/2 (corte B-B)
xd = 600
v = Vista(xd - 0.22 * 500, 505, 2)
titulo(xd - 10, 572, 'D. DETALLE 1: ASIENTO DE LA TAPA', 'ESC. 1/2 - corte B-B', 230)
x0 = 0.22
v.conc([(R + 0.01, 0), (0.56, 0), (0.56, -LOSA), (RING, -LOSA), (RING, -LOSA - ENG), (U, -LOSA - ENG), (U, -ET), (R, -ET), (R, -0.01)])
v.pl([(0.56, 0.01), (0.552, -0.04), (0.566, -0.07), (0.56, -0.11)], 'CONCRETO')
v.conc([(x0, -ET), (T, -ET), (T, -0.01), (T - 0.01, 0), (x0, 0)], outline=False, color=253)
v.pl([(x0, -ET), (T, -ET), (T, -0.01), (T - 0.01, 0), (x0, 0)], 'TAPA')
v.pl([(x0, 0), (x0 - 0.005, -0.03), (x0 + 0.005, -0.05), (x0, -ET)], 'TAPA')
v.line((x0, ZP1), (0.31, ZP1), 'ACERO'); v.barra(0.30, ZP2, D38)
v.barra(C, -0.045, D12); v.barra(C, -0.155, D12)
v.dim((T, 0), (R, 0), 10, text='0.01')
v.dim((U, -ET), (R, -ET), -40, text='0.05 (asiento)')
v.dim((0.56, 0), (0.56, -ET), 12, horiz=False)
v.dim((0.56, -ET), (0.56, -LOSA), 12, horiz=False, text='0.02')
v.dim((0.56, -LOSA), (0.56, -LOSA - ENG), 12, horiz=False)
v.dim((x0, -ET), (x0, ZP1), -10, horiz=False, text='0.025')
v.dim((T - 0.01, 0), (T, 0), 22, text='bisel 0.01')
llamada(v.p(0.26, -0.02), (xd - 2, 392), "Tapa ciega f'c=210 (sin marco)", w=75)
llamada(v.p(0.29, ZP2), (xd - 2, 380), 'Parrilla 3/8" @0.10', w=75)
llamada(v.p(0.325, -ET), (xd - 2, 368), 'Asiento plano y nivelado 0.05', w=75)
llamada(v.p(R + 0.003, -0.002), (725, 400), 'Chaflan 1 x 1 cm en el rebaje', w=80)
llamada(v.p(R, -0.03), (725, 388), 'Holgura 1 cm (removible, sin sello)', w=80)
llamada(v.p(0.42, -0.13), (725, 376), 'Borde engrosado 0.15 x 0.10', w=80)
llamada(v.p(C, -0.155), (725, 364), 'Refuerzo de borde 1/2"', w=80)

# ============ E. TAPA: PLANTA DE ARMADO 1/5
v = Vista(100, 250, 5)
titulo(22, 338, 'E. TAPA: PLANTA DE ARMADO', 'ESC. 1/5', 160)
v.conc([(-T, -T), (T, -T), (T, T), (-T, T)], layer='TAPA', color=253)
v.rect(-T + 0.01, -T + 0.01, T - 0.01, T - 0.01, 'TAPA')
for k in range(7):
    u = -0.30 + 0.1 * k
    v.line((-0.31, u), (0.31, u), 'ACERO'); v.line((u, -0.31), (u, 0.31), 'ACERO')
for s in (-1, 1):
    v.rect(-CJX, s * YA - CJY, CJX, s * YA + CJY, 'CONCRETO')
    v.pl([(-AG - GAN, s * YA), (-AG, s * YA)], 'ACERO_LISO', w=0.9); v.pl([(AG, s * YA), (AG + GAN, s * YA)], 'ACERO_LISO', w=0.9)
    v.pl([(-AG, s * YA), (AG, s * YA)], 'ACERO_LISO', w=2.0)
corte_marca(v, (-T - 0.04, YA), (T + 0.04, YA), 'C')
v.dim((-T, T), (T, T), 10); v.dim((-0.31, -T), (0.31, -T), -8)
v.dim((-0.30, T), (-0.20, T), 4, text='0.10')
v.dim((T, -0.30), (T, 0.30), 12, horiz=False, text='6 @ 0.10 = 0.60')
v.dim((-CJX, YA + CJY), (CJX, YA + CJY), 8)
v.dim((-T, 0), (-T, YA), -10, horiz=False)
llamada(v.p(0.25, 0.05), (190, 312), '7 barras 3/8" en X, L = 0.62', w=90)
llamada(v.p(0.05, -0.25), (190, 298), '7 barras 3/8" en Y, L = 0.62', w=90)
llamada(v.p(0.0, YA), (190, 284), '2 asas de fierro liso 1/2"\ndesarrollo 0.50 c/u', w=90)
llamada(v.p(0.08, -YA + CJY), (190, 266), 'Cajuela 0.19 x 0.06 x 0.03\n(el asa no sobresale)', w=90)
llamada(v.p(T - 0.005, -0.33), (190, 248), 'Cantos biselados 1 x 1 cm\n(sin marco metalico)', w=90)

# ============ F. TAPA: CORTE C-C (por el asa) 1/5
v = Vista(100, 138, 5)
texto(22, 163, 'F. TAPA: CORTE C-C (por el asa)  ESC. 1/5', 4.5, 'TITULOS', style='ARIALB')
tapa_seccion(v, cajuela=True)
parrilla(v)
asa_alzado(v)
v.dim((-T, 0), (T, 0), 12); v.dim((T, 0), (T, -ET), 10, horiz=False)
v.dim((-CJX, -CJZ), (CJX, -CJZ), -24)
v.dim((-T, -ET), (-T, ZP1), -10, horiz=False, text='0.025')
llamada(v.p(0.0, ZA), (190, 150), 'Agarre del asa en la cajuela', w=80)
llamada(v.p(AG + 0.10, ZA - PATA), (190, 138), 'Ganchos amarrados a la parrilla', w=80)

# ============ G. DETALLE DEL ASA 1/2
v = Vista(300 + (AG + GAN) * 500 - 40, 228, 2)
titulo(232, 338, 'G. DETALLE DEL ASA', 'ESC. 1/2 - fierro liso 1/2" (A36)', 180)
v.conc([(-0.02, 0), (-CJX, 0), (-CJX, -CJZ), (CJX, -CJZ), (CJX, 0), (AG + GAN + 0.02, 0), (AG + GAN + 0.02, -ET), (-0.02, -ET)],
       outline=False, color=253)
v.pl([(-0.02, 0), (-CJX, 0), (-CJX, -CJZ), (CJX, -CJZ), (CJX, 0), (AG + GAN + 0.02, 0)], 'TAPA')
v.line((-0.02, -ET), (AG + GAN + 0.02, -ET), 'TAPA')
v.pl([(0, ZA), (AG, ZA), (AG, ZA - PATA), (AG + GAN, ZA - PATA)], 'ACERO_LISO', w=D12 * v.k)
v.line((0, 0.005), (0, -ET - 0.005), 'EJES')
v.line((0.0, ZP1), (AG + GAN + 0.02, ZP1), 'ACERO')
for xx in (0.0, 0.10, 0.20): v.barra(xx, ZP2, D38)
v.dim((0, 0), (CJX, 0), 10, text='0.095 (1/2 cajuela 0.19)')
v.dim((0, 0), (AG, 0), 22, text='0.075 (1/2 agarre 0.15)')
v.dim((AG, -ET), (AG + GAN, -ET), -10, text='0.15 (gancho)')
v.dim((AG + GAN + 0.02, 0), (AG + GAN + 0.02, ZA), 10, horiz=False, text='0.015')
v.dim((AG + GAN + 0.02, ZA), (AG + GAN + 0.02, ZA - PATA), 22, horiz=False, text='0.02')
texto(300, 166, 'Desarrollo del asa: 0.15 + 2 x 0.02 + 2 x 0.15 = 0.49 m (se toma 0.50 con dobleces) - fierro liso 1/2", 0.99 kg/m.', 3.0)
texto(300, 160, 'Las asas se amarran a la parrilla con alambre N 16 antes del vaciado.', 3.0)

# ============ H. ISOMETRICO 1/10 (tapa sobre su asiento)
iso_o = (705, 200); kk = 92
c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
def P(x, y, z): return (iso_o[0] + (x - y) * c30 * kk, iso_o[1] + ((x + y) * s30 + z) * kk)
def isoline(a, b, layer): msp.add_line(P(*a), P(*b), dxfattribs={'layer': layer})
def isosq(r, z, layer, ry=None):
    ry = r if ry is None else ry
    msp.add_lwpolyline([P(-r, -ry, z), P(r, -ry, z), P(r, ry, z), P(-r, ry, z)], close=True, dxfattribs={'layer': layer})
def isofill(pts, color):
    h = msp.add_hatch(color=color, dxfattribs={'layer': 'CONCRETO_ACHURADO'}); h.paths.add_polyline_path([P(*q) for q in pts], is_closed=True)
titulo(592, 338, 'H. ISOMETRICO: TAPA Y ASIENTO', 'SIN ESCALA', 230)
LX = 0.62
isofill([(-X, -LX, 0), (X, -LX, 0), (X, LX, 0), (-X, LX, 0)], 254)
isofill([(-R, -R, 0), (R, -R, 0), (R, R, 0), (-R, R, 0)], 252)
isosq(X, 0, 'CONCRETO', LX)
for a, b in (((X, -LX, 0), (X, -LX, -LOSA)), ((X, -LX, -LOSA), (X, LX, -LOSA)), ((X, LX, 0), (X, LX, -LOSA)),
             ((-X, -LX, 0), (-X, -LX, -LOSA)), ((-X, -LX, -LOSA), (X, -LX, -LOSA))):
    isoline(a, b, 'CONCRETO')
isosq(R, 0, 'CONCRETO'); isosq(R, -ET, 'CONCRETO'); isosq(U, -ET, 'CONCRETO')
for q in ((-R, -R), (R, -R), (-R, R)): isoline((q[0], q[1], 0), (q[0], q[1], -ET), 'CONCRETO')
zt = 0.42                                            # tapa elevada (montaje)
isofill([(-T, -T, zt), (T, -T, zt), (T, T, zt), (-T, T, zt)], 253)
isosq(T, zt, 'TAPA'); isosq(T - 0.01, zt, 'TAPA')
for a, b in (((T, -T, zt), (T, -T, zt - ET)), ((T, -T, zt - ET), (T, T, zt - ET)), ((T, T, zt), (T, T, zt - ET)),
             ((-T, -T, zt), (-T, -T, zt - ET)), ((-T, -T, zt - ET), (T, -T, zt - ET))):
    isoline(a, b, 'TAPA')
for s in (-1, 1):
    msp.add_lwpolyline([P(-CJX, s * YA - CJY, zt), P(CJX, s * YA - CJY, zt), P(CJX, s * YA + CJY, zt), P(-CJX, s * YA + CJY, zt)], close=True,
                       dxfattribs={'layer': 'CONCRETO'})
    msp.add_lwpolyline([P(-AG, s * YA, zt + ZA), P(AG, s * YA, zt + ZA)], dxfattribs={'layer': 'ACERO_LISO', 'const_width': 1.2})
for q in ((-T, -T), (T, -T), (T, T), (-T, T)):
    msp.add_line(P(q[0], q[1], zt - ET - 0.02), P(q[0], q[1], 0.02), dxfattribs={'layer': 'EJES'})
for lab, pt, pos in (("Tapa ciega\n0.68 x 0.68 x 0.08", (T, 0.0, zt - 0.04), (778, 300)),
                     ('Asas 1/2" liso\nen cajuelas', (0.0, YA, zt), (778, 280)),
                     ('Rebaje (asiento)\n0.70 x 0.70 x 0.08', (R, 0.15, -0.02), (778, 256)),
                     ('Luz libre\n0.60 x 0.60', (U, -0.10, -ET), (778, 234)),
                     ('Losa e = 0.10\n(vereda)', (X, 0.40, 0), (778, 210))):
    llamada(P(*pt), pos, lab, 3.0, 50)

# ============ I. MATERIALES, PROCESO CONSTRUCTIVO, LEYENDA Y MEMBRETE
tx, ty = 22, 96
texto(tx, ty, 'I. MATERIALES POR REGISTRO', 4.5, 'TITULOS', style='ARIALB')
filas = [("Concreto tapa f'c=210 (0.68 x 0.68 x 0.08)", 'm3', '%.3f' % ((2 * T) ** 2 * ET)),
         ('Encofrado lateral de la tapa (4 x 0.68 x 0.08)', 'm2', '%.3f' % (4 * 2 * T * ET)),
         ('Acero 3/8" parrilla (14 x 0.62 m)', 'kg', '%.2f' % (14 * 0.62 * 0.56)),
         ('Fierro liso 1/2" asas (2 x 0.50 m)', 'kg', '%.2f' % (2 * 0.50 * 0.994)),
         ('Acero 1/2" refuerzo de borde (8 x 1.40 m)', 'kg', '%.2f' % (8 * 1.40 * 0.994)),
         ('Borde engrosado (%.2f x 0.15 x 0.10)' % ENG_PER, 'm3', '%.3f' % (ENG_PER * 0.015))]
cw = [96, 14, 18]; rh = 6.0; yy = ty - 4
msp.add_lwpolyline([(tx, yy), (tx + sum(cw), yy), (tx + sum(cw), yy - rh * (len(filas) + 1)), (tx, yy - rh * (len(filas) + 1))], close=True, dxfattribs={'layer': 'MEMBRETE'})
for i, row in enumerate([('DESCRIPCION', 'UND', 'CANT.')] + filas):
    y1 = yy - rh * (i + 1)
    msp.add_line((tx, y1), (tx + sum(cw), y1), dxfattribs={'layer': 'MEMBRETE'})
    x = tx
    for j, cell in enumerate(row):
        texto(x + 1.5 if j == 0 else x + cw[j] / 2, y1 + 1.6, cell, 2.9, 'TEXTO', TA.LEFT if j == 0 else TA.BOTTOM_CENTER, 'ARIALB' if i == 0 else 'ARIAL')
        x += cw[j]
x = tx
for wj in cw[:-1]:
    x += wj; msp.add_line((x, yy), (x, yy - rh * (len(filas) + 1)), dxfattribs={'layer': 'MEMBRETE'})
texto(tx, yy - rh * (len(filas) + 1) - 5, '%s: %d registros con tapa ciega. Peso de la tapa aprox. %.0f kg.' % (PROY["nombre"], PROY["n"], PESO_TAPA), 2.8)

nx, ny = 160, 96
texto(nx, ny, 'J. NOTAS Y PROCESO CONSTRUCTIVO', 4.5, 'TITULOS', style='ARIALB')
notas = ["1. Tapa CIEGA de concreto armado: no lleva marco ni contramarco metalico. Concreto f'c=210 kg/cm2, acero fy=4200 kg/cm2, asas de fierro liso 1/2\" (A36).",
         "2. La tapa se vacia aparte en obra, sobre tablero nivelado y con molde lateral de madera de 0.68 x 0.68 x 0.08; cantos superiores biselados 1 x 1 cm.",
         "3. Parrilla 3/8\" @0.10 en ambos sentidos con recubrimiento de 2.5 cm; las 2 asas se amarran a la parrilla y su agarre queda en la cajuela, sin sobresalir.",
         "4. Curado humedo minimo 7 dias; la tapa se desmolda a las 24 h y se coloca cuando alcanza el 70 % de f'c.",
         "5. El rebaje 0.70 x 0.70 x 0.08 se forma en la losa con un cajon de madera fijado antes del vaciado; el asiento (0.05 por lado) queda plano y nivelado.",
         "6. Holgura de 1 cm por lado entre tapa y rebaje: la tapa queda al ras del NPT (vereda), es removible y no se sella con mortero.",
         "7. Peso aprox. %.0f kg: se levanta entre 2 operarios con ganchos en las asas. Registros fuera de los cruces vehiculares." % PESO_TAPA]
if MURO:
    notas.append("8. Colector b = %.2f: en los lados largos el rebaje queda sobre la cabeza de los muros; borde engrosado solo en los 2 lados transversales." % (2 * BI))
for i, n_ in enumerate(notas): texto(nx, ny - 7 - i * 5.2, n_, 2.75)

lx, ly = 160, 18
for i, (lab, col) in enumerate((('Concreto de losa y muros', 254), ('Concreto de la tapa', 253), ('Acero corrugado', 1), ('Fierro liso (asas)', 30))):
    x = lx + i * 100; y = ly
    h = msp.add_hatch(color=col, dxfattribs={'layer': 'TEXTO'}); h.paths.add_polyline_path([(x, y), (x + 8, y), (x + 8, y + 4), (x, y + 4)], is_closed=True)
    texto(x + 11, y, lab, 3.0)

bx, by = 590, 12
msp.add_lwpolyline([(bx, by), (W - 12, by), (W - 12, by + 78), (bx, by + 78)], close=True, dxfattribs={'layer': 'MEMBRETE', 'lineweight': 50})
for yl in (by + 58, by + 42, by + 24, by + 12): msp.add_line((bx, yl), (W - 12, yl), dxfattribs={'layer': 'MEMBRETE'})
msp.add_line((bx + 150, by), (bx + 150, by + 24), dxfattribs={'layer': 'MEMBRETE'})
mtexto(bx + 2, by + 76.5, 'PROYECTO: ' + PROY["proyecto"], 2.4, 232, attach=1)
mtexto(bx + 2, by + 56, 'ENTIDAD: GERENCIA TERRITORIAL BAJO MAYO - TARAPOTO\\PUBICACION: %s\\PESPECIALIDAD: INSTALACIONES SANITARIAS - DRENAJE PLUVIAL' % PROY["ubic"], 2.5, 232, attach=1)
texto(bx + 2, by + 34, 'PLANO: DETALLE DE REGISTRO DE LIMPIEZA - TAPA CIEGA', 3.4, style='ARIALB')
texto(bx + 2, by + 28, 'DE CONCRETO ARMADO 0.68 x 0.68 x 0.08 EN REBAJE', 3.4, style='ARIALB')
texto(bx + 2, by + 16, 'PROYECTISTA: ________________  CIP: ______', 2.6)
texto(bx + 2, by + 4, 'REVISADO: ________________        FIRMA Y SELLO:', 2.6)
texto(bx + 153, by + 16, 'ESCALA: INDICADA   FECHA: OCT. 2026', 2.6)
texto(bx + 153, by + 4, 'REVISION: 02', 2.6)
texto(W - 16, by + 3, 'DP-06B', 9, 'TITULOS', TA.BOTTOM_RIGHT, 'ARIALB')

doc.saveas(OUT)
print('ok', OUT)
