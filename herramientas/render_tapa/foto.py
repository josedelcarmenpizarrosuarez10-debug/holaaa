"""Vistas fotorrealistas del registro instalado en la vereda (losa superior del colector)."""
import numpy as np, pyvista as pv, vtk
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
src = open('render.py').read(); exec(src[:src.index('P = modelo()')])
from modelo import modelo, Parte, ET

FW, FH = 2000, 1330
MAT.update({
    'angulo': dict(color=(0.34, 0.35, 0.36), specular=0.5, specular_power=22, diffuse=0.85, ambient=0.18),
})
def tex(tono, sem, grano=0.05, poros=0.003, manchas=0.0):
    r = np.random.default_rng(sem); n = 1024
    def ruido(beta):
        w = r.normal(size=(n, n)); fx = np.fft.fftfreq(n); f = np.hypot(*np.meshgrid(fx, fx)); f[0, 0] = 1
        z = np.real(np.fft.ifft2(np.fft.fft2(w) / f ** beta)); return (z - z.mean()) / z.std()
    img = 0.55 * ruido(1.0) + 0.45 * ruido(0.4)
    yy, xx = np.mgrid[0:n, 0:n] / n
    arc = 0.25 * np.sin(2 * np.pi * (7 * xx + 2 * np.sin(2 * np.pi * yy)))      # marcas de frotachado (periodicas)
    base = np.array(tono)[None, None, :] * (1 + grano * (img + arc)[..., None])
    if manchas: base *= (1 - manchas * np.clip(ruido(1.6) * 0.5, 0, 1))[..., None]
    p = r.random((n, n)) < poros; base[p] *= 0.62
    im = Image.fromarray(np.clip(base * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    return pv.Texture(np.array(im))
TEX.update({
    'concreto': tex((0.71, 0.70, 0.67), 1, 0.06, 0.003, 0.08),
    'tapa': tex((0.66, 0.655, 0.635), 2, 0.06, 0.004, 0.05),
    'piso': tex((0.62, 0.60, 0.57), 3, 0.07, 0.004, 0.05),
    'muro': tex((0.96, 0.91, 0.80), 4, 0.02, 0.0005, 0.06),
    'zocalo': tex((0.62, 0.60, 0.57), 5, 0.045, 0.002, 0.15),
})

def escena_ext(P):
    E = {}
    X = 0.55
    v = Parte('vereda', 'concreto')
    juntas = [-8, -4, 4, 8]                      # juntas de dilatacion cada 4.00 m
    cortes = sorted([-12, -0.75, 0.75, 12] + [j for j in juntas])
    tramos = [(-12, -8), (-8, -4), (-4, -0.75), (0.75, 4), (4, 8), (8, 12)]
    for a, b in tramos:
        a2 = a + (0.0127 if a in juntas else 0); b2 = b - (0.0127 if b in juntas else 0)
        v.box(-X, X, a2, b2, -0.10, 0)
    E['vereda'] = v
    js = Parte('juntas', 'sello')
    for j in juntas: js.box(-X, X, j - 0.0127, j + 0.0127, -0.10, -0.003)
    js.box(X, X + 0.0254, -12, 12, -0.10, -0.003)                     # junta 1" colector / piso adyacente
    E['juntas'] = js
    pz = Parte('piso', 'piso'); pz.box(X + 0.0254, 7, -12, 12, -0.10, 0)
    for k in range(-3, 4):                                             # bruñas del piso adyacente cada 3 m
        pass
    E['piso'] = pz
    mu = Parte('muro', 'muro'); mu.box(-0.80, -X, -12, 12, 0.15, 2.4); E['muro'] = mu
    zo = Parte('zocalo', 'zocalo'); zo.box(-0.80, -X + 0.012, -12, 12, -0.10, 0.15); E['zocalo'] = zo
    # segundo registro a 10.73 m (RS-01 a RS-02)
    for dy in (10.73, -10.73):
        t2 = Parte('t2', 'tapa'); t2.box(-0.337, 0.337, dy - 0.337, dy + 0.337, -0.08, 0.0006)
        m2 = Parte('m2', 'angulo')
        for r_in, r_out in ((0.3285, 0.34),):
            m2.box(-r_out, r_out, dy + r_in, dy + r_out, -0.004, 0.0009); m2.box(-r_out, r_out, dy - r_out, dy - r_in, -0.004, 0.0009)
            m2.box(r_in, r_out, dy - r_in, dy + r_in, -0.004, 0.0009); m2.box(-r_out, -r_in, dy - r_in, dy + r_in, -0.004, 0.0009)
        gap = Parte('g2', 'sello'); gap.box(-0.35, 0.35, dy - 0.35, dy + 0.35, -0.03, 0.0003)
        E['t2%s' % dy], E['m2%s' % dy], E['g2%s' % dy] = t2, m2, gap
    return E

MAT['sello'] = dict(color=(0.22, 0.22, 0.22), specular=0.2, specular_power=10, diffuse=0.8, ambient=0.2)

def foto(cam, nombre, fov=40, dof=None):
    P = modelo(); P.update(escena_ext(P))
    p = pv.Plotter(off_screen=True, window_size=(FW, FH), lighting='none')
    p.set_background((0.93, 0.95, 0.97), top=(0.55, 0.72, 0.92))
    for k, part in P.items():
        if part.mat in TEX:
            faces = []
            for b in part.boxes: faces += caras_box(b, tile={'piso': 2.4, 'muro': 2.0}.get(part.mat, 1.3))
            if faces:
                m = pv.merge(faces, merge_points=False); m.active_texture_coordinates = m.point_data['tc']
                p.add_mesh(m, texture=TEX[part.mat], ambient=0.36, diffuse=0.80, specular=0.04, specular_power=8)
        else:
            ms = [pv.Box(bounds=b) for b in part.boxes]
            for p0, p1, d in part.bars:
                mm = barra(p0, p1, d, corrugada=(part.mat == 'acero'))
                if mm is not None: ms.append(mm)
            if ms: p.add_mesh(pv.merge(ms), smooth_shading=True, **MAT[part.mat])
    sol = pv.Light(position=(3.0, -2.2, 6.5), focal_point=(0, 0, 0), intensity=0.95, light_type='scene light', color=(1.0, 0.96, 0.88))
    cielo = pv.Light(position=(3, 4, 6), focal_point=(0, 0, 0), intensity=0.30, light_type='scene light', color=(0.75, 0.83, 1.0))
    reb = pv.Light(position=(4, -2, 0.6), focal_point=(0, 0, 0), intensity=0.12, light_type='scene light', color=(1.0, 0.95, 0.9))
    for l in (sol, cielo, reb): p.add_light(l)
    try: p.enable_ssao(radius=0.06, bias=0.003, kernel_size=128)
    except Exception: pass
    try: p.enable_anti_aliasing('ssaa')
    except Exception: pass
    p.camera_position = cam; p.camera.view_angle = fov
    p.render()
    img = p.screenshot(None, return_img=True)
    z = p.get_image_depth(fill_value=np.nan)
    p.close()
    im = Image.fromarray(img).convert('RGB')
    # profundidad de campo suave
    if dof:
        zf = np.nan_to_num(-z, nan=50.0); d0 = dof
        k = np.clip(np.abs(zf - d0) / (d0 * 1.6), 0, 1)
        bl = im.filter(ImageFilter.GaussianBlur(5))
        mask = Image.fromarray((k * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
        im = Image.composite(bl, im, mask)
    # gradacion de color, vineta y grano
    im = ImageEnhance.Contrast(im).enhance(1.08); im = ImageEnhance.Color(im).enhance(1.06)
    a = np.asarray(im).astype(float) / 255
    a = a ** 0.92 * np.array([1.015, 1.0, 0.985])
    yy, xx = np.mgrid[0:FH, 0:FW]; rr = np.hypot((xx - FW / 2) / (FW / 2), (yy - FH / 2) / (FH / 2))
    a *= (1 - 0.15 * np.clip(rr - 0.65, 0, 1) ** 1.5)[..., None]
    a += np.random.default_rng(3).normal(0, 0.012, a.shape)
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(1.2, 40, 2))
    im.save(nombre + '.png')

# vista 1: persona de pie sobre la vereda, mirando el registro
foto([(0.15, -3.1, 1.62), (0.0, 0.1, -0.05), (0, 0, 1)], 'foto1', fov=42, dof=3.3)
# vista 2: agachado junto al registro, a 45 grados
foto([(1.05, -0.95, 0.55), (0.0, 0.05, -0.04), (0, 0, 1)], 'foto2', fov=40, dof=1.45)
print('ok')
