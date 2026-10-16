"""Laminas isometricas de la tapa de registro: una imagen por vista, letra grande, fondo blanco."""
import json, textwrap, numpy as np, pyvista as pv, vtk
from PIL import Image, ImageDraw, ImageFont
src = open('render.py').read(); exec(src[:src.index('P = modelo()')])   # reutiliza texturas y geometria
from modelo import modelo, ET, REB, LUZ, TAPA, GANCHO, BI, BW, YA, CJZ
LZ = '%.2f' % (2 * LUZ)

RW, RH = 1300, 1060
MAT.update({
    'angulo': dict(color=(0.16, 0.30, 0.45), specular=0.6, specular_power=40, diffuse=0.85, ambient=0.2),
    'acero': dict(color=(0.62, 0.33, 0.18), specular=0.45, specular_power=25, diffuse=0.9, ambient=0.2),
    'liso': dict(color=(0.60, 0.62, 0.65), specular=0.7, specular_power=50, diffuse=0.9, ambient=0.2),
})
TEX['concreto'] = tex_concreto((0.80, 0.79, 0.76), 1); TEX['tapa'] = tex_concreto((0.74, 0.73, 0.70), 2)

def vista(partes, offs, cut=None, opac=None, direc=(1, -1, 0.82), foco=(0, 0, -0.1), escala=0.8, anclas=None, nombre='x'):
    p = pv.Plotter(off_screen=True, window_size=(RW, RH), lighting='none')
    p.set_background('white')
    for k, part in partes.items():
        dz = offs.get(k, 0); op = (opac or {}).get(k, 1.0)
        if part.mat in ('concreto', 'tapa'):
            faces = []
            for b in part.boxes:
                b = clamp(b, cut)
                if b is None: continue
                faces += caras_box([b[0], b[1], b[2], b[3], b[4] + dz, b[5] + dz])
            if faces:
                m = pv.merge(faces, merge_points=False); m.active_texture_coordinates = m.point_data['tc']
                p.add_mesh(m, texture=TEX[part.mat], ambient=0.32, diffuse=0.75, specular=0.03, opacity=op)
                if op < 1:
                    p.add_mesh(pv.merge([pv.Box(bounds=(b[0], b[1], b[2], b[3], b[4] + dz, b[5] + dz)) for b in part.boxes if clamp(b, cut)]).extract_feature_edges(),
                               color=(0.45, 0.45, 0.45), line_width=1.5)
        else:
            ms = [pv.Box(bounds=(b[0], b[1], b[2], b[3], b[4] + dz, b[5] + dz)) for b in (clamp(x, cut) for x in part.boxes) if b]
            for p0, p1, d in part.bars:
                c = clampbar(p0, p1, cut)
                if c is None: continue
                m = barra(c[0] + [0, 0, dz], c[1] + [0, 0, dz], d, corrugada=(part.mat == 'acero'))
                if m is not None: ms.append(m)
            if ms: p.add_mesh(pv.merge(ms), smooth_shading=True, opacity=op, **MAT[part.mat])
    for pos, it in (((2.5, -1.6, 4.0), 0.8), ((-3, 2, 2), 0.35), ((0, -3, 0.5), 0.25), ((0, 0, -3), 0.15)):
        p.add_light(pv.Light(position=pos, focal_point=(0, 0, 0), intensity=it, light_type='scene light'))
    try: p.enable_ssao(radius=0.05, bias=0.003, kernel_size=128)
    except Exception: pass
    try: p.enable_anti_aliasing('ssaa')
    except Exception: pass
    d = np.array(direc, float); d /= np.linalg.norm(d); f = np.array(foco)
    p.camera_position = [tuple(f + 5 * d), tuple(f), (0, 0, 1)]
    p.enable_parallel_projection(); p.camera.parallel_scale = escala / 2
    p.render()
    co = vtk.vtkCoordinate(); co.SetCoordinateSystemToWorld(); pts = {}
    for k, xyz in (anclas or {}).items():
        co.SetValue(*xyz); x, y = co.GetComputedDoubleDisplayValue(p.renderer); pts[k] = (x, RH - y)
    p.screenshot(nombre + '_r.png'); p.close()
    return pts

FD = '/usr/share/fonts/truetype/dejavu/'
F = lambda s, b=False: ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf'), s)
AZ = (22, 72, 120); NAR = (205, 90, 20); TXT = (25, 35, 45)
MG = 470; TH = 190; CW = RW + 2 * MG; CH = TH + RH + 120
FS = 36

def lamina(nombre, titulo, sub, pts, labels, nota=None):
    S = Image.new('RGB', (CW, CH), 'white'); d = ImageDraw.Draw(S)
    d.rectangle([0, 0, CW, TH - 30], fill=AZ)
    d.text((40, 22), titulo, font=F(62, True), fill='white')
    d.text((40, 104), sub, font=F(34), fill=(215, 230, 245))
    S.paste(Image.open(nombre + '_r.png'), (MG, TH))
    items = []
    for k, txt in labels.items():
        if k not in pts: continue
        x, y = pts[k]
        lines = []
        for part in txt.split('\n'): lines += textwrap.wrap(part, 19) or ['']
        h = len(lines) * (FS + 8) + 16
        items.append([y, h, lines, (MG + x, TH + y), k, x])
    disp = CH - 20 - TH - 10
    items.sort(key=lambda b: b[5])
    best = None
    for n in range(len(items) + 1):
        hl = sum(b[1] + 18 for b in items[:n]); hr = sum(b[1] + 18 for b in items[n:])
        cost = max(hl, hr) + 0.4 * abs(n - sum(1 for b in items if b[5] < RW / 2)) * 100
        if hl <= disp and hr <= disp and (best is None or cost < best[0]): best = (cost, n)
    n = best[1] if best else len(items) // 2
    blocks = {'L': [b[:5] for b in items[:n]], 'R': [b[:5] for b in items[n:]]}
    for side, bl in blocks.items():
        bl.sort(key=lambda b: b[0])
        ys = []; top = TH + 10
        for b in bl:
            yc = max(TH + b[0] - b[1] / 2, top); ys.append(yc); top = yc + b[1] + 18
        over = top - (CH - 20)
        if over > 0:
            for i in range(len(ys) - 1, -1, -1):
                lim = (CH - 20 - sum(b[1] + 18 for b in bl[i:])) + 18
                ys[i] = min(ys[i], lim)
        for b, y0 in zip(bl, ys):
            _, h, lines, (ax, ay), k = b
            x0 = 18 if side == 'L' else CW - MG + 18; x1 = x0 + MG - 36
            d.rounded_rectangle([x0, y0, x1, y0 + h], 14, fill=(255, 247, 238), outline=NAR, width=3)
            for i, ln in enumerate(lines):
                d.text((x0 + 14, y0 + 8 + i * (FS + 8)), ln, font=F(FS, i == 0), fill=TXT if i else AZ)
            ex = x1 if side == 'L' else x0; ey = y0 + h / 2
            d.line([ex, ey, ax, ay], fill=NAR, width=4)
            d.ellipse([ax - 9, ay - 9, ax + 9, ay + 9], fill=NAR, outline='white', width=2)
    if nota:
        d.text((40, CH - 80), nota, font=F(32), fill=(70, 70, 70))
    S.save('ISO_' + nombre + '.png', optimize=True)

P = modelo()
X = BI + BW
# 1 isometrico general
pts = vista(P, {}, foco=(0, 0, -0.15), escala=1.65, nombre='g1', anclas={
    'losa': (-0.45, -0.5, 0), 'hg': (0.345, -0.2, 0), 'tapa': (-0.12, -0.05, 0), 'asa': (0.0, -YA, -0.01),
    'muro': (X, -0.4, -0.35), 'npt': (0.4, 0.5, 0)})
lamina('g1', '1. ISOMETRICO GENERAL - REGISTRO CON TAPA CIEGA', 'Tapa de concreto armado en su rebaje, a ras del piso terminado (vereda)', pts, {
    'losa': 'Losa superior del colector\ne = 0.10 m (vereda)', 'hg': 'Holgura 1 cm por lado\n(tapa 0.68 en\nrebaje 0.70)',
    'tapa': "Tapa ciega de concreto\narmado f'c=210\n0.68 x 0.68 x 0.08 m\npeso aprox. 89 kg",
    'asa': 'Cajuela del asa\n(asa embutida, no sobresale)', 'muro': 'Muro del colector\ne = %.2f m' % BW, 'npt': 'Piso terminado (NPT)\nsin resaltes'})
# 2 despiece
offs = {'parrilla': 0.32, 'asas': 0.52, 'tapa': 0.80}
pts = vista(P, offs, foco=(0, 0, 0.35), escala=2.10, direc=(1, -1, 0.75), nombre='g2', anclas={
    'tapa': (-0.34, 0.1, 0.76), 'asa': (-0.225, YA, 0.52 - 0.035), 'par': (0.31, 0.2, 0.32 - 0.055), 'reb': (0.0, -0.35, -0.04),
    'luz': (0.25, 0.30, -0.10), 'losa': (-0.5, -0.5, 0)})
lamina('g2', '2. ISOMETRICO DESPIECE - TAPA CIEGA Y REBAJE', 'La tapa se fabrica aparte en obra y se coloca en el rebaje de la losa', pts, {
    'tapa': "TAPA CIEGA\nconcreto f'c=210\n0.68 x 0.68 x 0.08 m\n0.037 m3 (sin marco)",
    'asa': 'ASAS (2 und)\nfierro liso 1/2"\n0.50 m cada una',
    'par': 'PARRILLA\n7 + 7 barras 3/8"\n@ 0.10 m, L = 0.62 m\n4.9 kg',
    'reb': 'REBAJE 0.70 x 0.70\nx 0.08 en la losa\n(asiento de la tapa)',
    'luz': 'LUZ LIBRE\n0.60 x 0.60 m',
    'losa': 'LOSA DEL COLECTOR\ne = 0.10 m'})
# 3 corte isometrico por el eje del colector
YC = 0.0
pts = vista(P, {}, cut=YC, foco=(0.22, YC, -0.10), escala=0.95, direc=(1, 1.1, 0.55), nombre='g3', anclas={
    'losa': (0.05, -0.6, 0), 'hg': (0.345, YC, -0.003), 'ap': (0.325, YC, -0.08), 'rb': (0.40, YC - 0.4, -0.045),
    'eng': (0.38, YC, -0.17), 'par': (0.0, YC, -0.0545), 'tapa': (0.12, YC, -0.03), 'luz': (0.30, YC, -0.13)})
lamina('g3', '3. ISOMETRICO EN CORTE - ASIENTO DE LA TAPA', 'Corte por el eje del colector: la tapa apoya en el rebaje de concreto de la losa', pts, {
    'losa': 'Losa superior e = 0.10', 'hg': 'Holgura 1 cm por lado\n(0.70 - 0.68) / 2', 'ap': 'Asiento de la tapa:\nrebaje de concreto\n0.05 por lado, a 0.08\nbajo el piso',
    'rb': 'Refuerzo de borde\n2 barras 1/2" por lado\nL = 1.40 m', 'eng': 'Borde engrosado\n0.15 x 0.10 m\nbajo la losa',
    'par': 'Parrilla 3/8" @ 0.10\nrecubrimiento 2.5 cm', 'tapa': 'Tapa ciega e = 0.08 m', 'luz': 'Luz libre %s x %s' % (LZ, LZ)})
# 4 tapa: armado interior
T = {k: P[k] for k in ('tapa', 'parrilla', 'asas')}
pts = vista(T, {}, opac={'tapa': 0.22}, foco=(0, 0, -0.04), escala=0.95, nombre='g4', anclas={
    'par1': (-0.31, -0.2, -0.055), 'par2': (0.2, -0.31, -0.045), 'asa': (0.06, -YA, -0.015), 'caj': (-0.06, YA, -CJZ),
    'gan': (0.225, YA, -0.035), 'conc': (-0.2, 0.34, -0.04)})
lamina('g4', '4. ISOMETRICO DE LA TAPA - ARMADO INTERIOR', 'Concreto mostrado transparente para ver el acero', pts, {
    'par1': 'Barras en X\n7 de 3/8", L = 0.62', 'par2': 'Barras en Y\n7 de 3/8", L = 0.62\n@ 0.10 m',
    'asa': 'Agarre del asa\nfierro liso 1/2"', 'caj': 'Cajuela del asa\n0.19 x 0.06 x 0.03', 'gan': 'Ganchos del asa\namarrados a la parrilla',
    'conc': "Concreto f'c=210\n0.68 x 0.68 x 0.08\ncantos biselados"})
# 5 rebaje de asiento en la losa (sin la tapa)
R5 = {k: P[k] for k in ('losa', 'engrosado', 'muros')}
pts = vista(R5, {}, foco=(0, 0, -0.10), escala=1.25, direc=(1, -1, 0.9), nombre='g5', anclas={
    'reb': (0.35, -0.2, 0), 'ap': (0.0, -0.325, -0.08), 'luz': (-0.1, -0.30, -0.10), 'esq': (-0.35, -0.35, 0), 'losa': (-0.5, -0.6, 0)})
lamina('g5', '5. ISOMETRICO DEL REBAJE DE ASIENTO (sin tapa)', 'Se forma en la losa con un cajon de madera antes del vaciado', pts, {
    'reb': 'Rebaje 0.70 x 0.70\nprofundidad 0.08\n(= espesor de la tapa)', 'ap': 'Asiento plano y\nnivelado: 0.05 m\npor lado',
    'luz': 'Luz libre %s x %s m\nbajo el asiento' % (LZ, LZ), 'esq': 'Arista superior con\nchaflan 1 x 1 cm', 'losa': 'Losa del colector\ne = 0.10 (vereda)'})
# 6 losa vista desde abajo con concreto transparente: refuerzo de borde
L6 = {k: P[k] for k in ('losa', 'engrosado', 'muros', 'refuerzo')}
pts = vista(L6, {}, opac={'losa': 0.25, 'engrosado': 0.25, 'muros': 0.25}, foco=(0, 0, -0.12), escala=1.75, direc=(1, -1, -0.75), nombre='g6', anclas={
    'rb': (0.40, -0.6, -0.045), 'rbx': (-0.2, -0.40, -0.155), 'gan': (X - 0.04, -0.40, -0.2), 'eng': (-0.375 if BI > LUZ else 0.0, 0.40, -0.2),
    'luz': (0.0, -0.3, -0.2), 'muro': (-X, 0.5, -0.4)})
lamina('g6', '6. ISOMETRICO DESDE ABAJO - REFUERZO DEL BORDE', 'Losa y muros transparentes: barras de 1/2" alrededor de la luz libre', pts, {
    'rb': 'Barras 1/2" en el eje\n2 por lado, L = 1.40 m', 'rbx': 'Barra inferior 1/2"\nen el borde engrosado',
    'gan': 'Gancho %.2f m dentro\ndel muro (L = 1.40)' % GANCHO, 'eng': 'Borde engrosado\n0.15 x 0.10 m\n(de %s a 0.90)' % LZ, 'luz': 'Luz libre %s x %s' % (LZ, LZ),
    'muro': 'Muros del colector\ne = %.2f m' % BW})
# 7 detalle ampliado de la esquina
pts = vista(P, {}, cut=YC, foco=(0.36, YC, -0.07), escala=0.32, direc=(1, 1.4, 0.35), nombre='g7', anclas={
    'tapa': (0.27, YC, -0.04), 'hg': (0.345, YC, 0), 'ap': (0.325, YC, -0.08), 'reb': (0.35, YC, -0.04), 'luz': (0.30, YC, -0.095),
    'eng': (0.42, YC, -0.15), 'rb': (0.40, YC, -0.045), 'losa': (0.47, YC, -0.02)})
lamina('g7', '7. DETALLE AMPLIADO - ASIENTO TAPA / REBAJE', 'Esquina del registro en corte, escala grande', pts, {
    'tapa': 'Tapa ciega 0.08 m\n(sin marco metalico)', 'hg': 'Holgura 1 cm', 'ap': 'Asiento 0.05 m\nplano y nivelado', 'reb': 'Cara del rebaje 0.70',
    'luz': 'Cara de la luz libre 0.60', 'eng': 'Borde engrosado', 'rb': 'Refuerzo de borde 1/2"', 'losa': 'Losa e = 0.10'})
print('ok')
