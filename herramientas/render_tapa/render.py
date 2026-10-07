import sys, json, numpy as np, pyvista as pv, vtk
from PIL import Image, ImageFilter
sys.path.insert(0, '.')
from modelo import modelo, ET

pv.OFF_SCREEN = True
W, H = 1400, 1000
rng = np.random.default_rng(7)

def tex_concreto(tono, sem):
    r = np.random.default_rng(sem); n = 1024
    img = np.zeros((n, n))
    for k, a in ((6, .18), (24, .3), (96, .3), (384, .22), (1024, .12)):
        z = r.random((k, k)); img += a * np.array(Image.fromarray((z * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)) / 255
    img = (img - img.mean()) / img.std()
    base = np.array(tono)[None, None, :] * (1 + 0.045 * img[..., None])
    poros = r.random((n, n)) < 0.0025
    base[poros] *= 0.55
    im = Image.fromarray(np.clip(base * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    return pv.Texture(np.array(im))

TEX = {'concreto': tex_concreto((0.70, 0.69, 0.66), 1), 'tapa': tex_concreto((0.64, 0.63, 0.60), 2)}

def caras_box(b, tile=0.45):
    x0, x1, y0, y1, z0, z1 = b
    V = lambda i, j, k: (x1 if i else x0, y1 if j else y0, z1 if k else z0)
    quads = [(V(0,0,1), V(1,0,1), V(1,1,1), V(0,1,1)), (V(0,1,0), V(1,1,0), V(1,0,0), V(0,0,0)),
             (V(0,0,0), V(1,0,0), V(1,0,1), V(0,0,1)), (V(1,1,0), V(0,1,0), V(0,1,1), V(1,1,1)),
             (V(1,0,0), V(1,1,0), V(1,1,1), V(1,0,1)), (V(0,1,0), V(0,0,0), V(0,0,1), V(0,1,1))]
    out = []
    for q in quads:
        q = np.array(q, float)
        a = np.linalg.norm(q[1] - q[0]); bb = np.linalg.norm(q[3] - q[0])
        if a < 1e-7 or bb < 1e-7: continue
        m = pv.PolyData(q, faces=[4, 0, 1, 2, 3])
        nrm = np.cross(q[1] - q[0], q[3] - q[0]); ax = int(np.argmax(np.abs(nrm)))
        uv = [i for i in range(3) if i != ax]
        tc = q[:, uv] / tile + ax * 0.37
        m.point_data['tc'] = tc
        out.append(m)
    return out

def barra(p0, p1, d, corrugada=True):
    v = p1 - p0; L = np.linalg.norm(v)
    if L < 1e-6: return None
    r0 = d / 2; ns, nt = max(int(L / 0.002), 4), 24
    s = np.linspace(0, L, ns); t = np.linspace(0, 2 * np.pi, nt)
    S, T = np.meshgrid(s, t, indexing='ij')
    R = np.full_like(S, r0)
    if corrugada:
        pitch = 0.7 * d
        R = r0 * (1 + 0.07 * np.clip(np.cos(2 * np.pi * S / pitch + 0.6 * np.sin(T)), 0.3, 1) ** 4)
        R += r0 * 0.06 * (np.exp(-((T - np.pi / 2) ** 2) / 0.02) + np.exp(-((T - 3 * np.pi / 2) ** 2) / 0.02))
    u = v / L; a = np.array([0, 0, 1.0]) if abs(u[2]) < 0.9 else np.array([1.0, 0, 0])
    e1 = np.cross(u, a); e1 /= np.linalg.norm(e1); e2 = np.cross(u, e1)
    P = p0 + S[..., None] * u + R[..., None] * (np.cos(T)[..., None] * e1 + np.sin(T)[..., None] * e2)
    g = pv.StructuredGrid(P[..., 0], P[..., 1], P[..., 2]).extract_surface()
    caps = [pv.Disc(center=p0, normal=-u, inner=0, outer=r0, c_res=24), pv.Disc(center=p1, normal=u, inner=0, outer=r0, c_res=24)]
    # rotula en el quiebre
    return pv.merge([g, *caps, pv.Sphere(radius=r0, center=p1, theta_resolution=16, phi_resolution=12)])

def clamp(b, cut):
    if cut is None: return b
    b = list(b)
    if b[2] >= cut: return None
    b[3] = min(b[3], cut); return b

def clampbar(p0, p1, cut):
    if cut is None: return p0, p1
    if p0[1] > cut + 1e-9 and p1[1] > cut + 1e-9: return None
    if p0[1] <= cut + 1e-9 and p1[1] <= cut + 1e-9: return p0, p1
    a, b = (p0, p1) if p0[1] <= cut else (p1, p0)
    t = (cut - a[1]) / (b[1] - a[1]); return a, a + t * (b - a)

MAT = {
    'angulo': dict(color=(0.20, 0.21, 0.23), specular=0.55, specular_power=35, diffuse=0.85, ambient=0.15),
    'acero': dict(color=(0.43, 0.35, 0.29), specular=0.45, specular_power=25, diffuse=0.9, ambient=0.15),
    'liso': dict(color=(0.47, 0.44, 0.41), specular=0.6, specular_power=40, diffuse=0.9, ambient=0.15),
}

def escena(partes, offs, cut=None, opac=None, cam=None, nombre='v', anclas=None, sombras=True, piso=True):
    p = pv.Plotter(off_screen=True, window_size=(W, H), lighting='none')
    p.set_background((0.97, 0.97, 0.96), top=(0.83, 0.87, 0.92))
    for k, part in partes.items():
        dz = offs.get(k, 0)
        op = (opac or {}).get(k, 1.0)
        if part.mat in ('concreto', 'tapa'):
            faces = []
            for b in part.boxes:
                b = clamp(b, cut)
                if b is None: continue
                b = [b[0], b[1], b[2], b[3], b[4] + dz, b[5] + dz]
                faces += caras_box(b)
            if faces:
                m = pv.merge(faces, merge_points=False)
                m.active_texture_coordinates = m.point_data['tc']
                p.add_mesh(m, texture=TEX[part.mat], ambient=0.28, diffuse=0.8, specular=0.04, opacity=op, smooth_shading=False)
        else:
            ms = []
            for b in part.boxes:
                b = clamp(b, cut)
                if b is None: continue
                ms.append(pv.Box(bounds=(b[0], b[1], b[2], b[3], b[4] + dz, b[5] + dz)))
            for p0, p1, d in part.bars:
                c = clampbar(p0, p1, cut)
                if c is None: continue
                m = barra(c[0] + [0, 0, dz], c[1] + [0, 0, dz], d, corrugada=(part.mat == 'acero'))
                if m is not None: ms.append(m)
            if ms: p.add_mesh(pv.merge(ms), smooth_shading=True, opacity=op, **MAT[part.mat])
    if piso:
        g = pv.Plane(center=(0, 0, -0.69), direction=(0, 0, 1), i_size=8, j_size=8)
        p.add_mesh(g, color=(0.93, 0.93, 0.91), ambient=0.4, diffuse=0.6, specular=0)
    l1 = pv.Light(position=(2.5, -1.6, 4.0), focal_point=(0, 0, 0), intensity=0.85, light_type='scene light')
    l1.positional = False
    l2 = pv.Light(position=(-3, 2, 2), focal_point=(0, 0, 0), intensity=0.35, light_type='scene light')
    l3 = pv.Light(position=(0, -3, 0.5), focal_point=(0, 0, 0), intensity=0.2, light_type='scene light')
    for l in (l1, l2, l3): p.add_light(l)
    if sombras:
        try: p.enable_ssao(radius=0.08, bias=0.004, kernel_size=128)
        except Exception as e: print('sin ssao', e)
    try: p.enable_anti_aliasing('ssaa')
    except Exception: pass
    p.camera_position = cam
    p.camera.view_angle = 26
    p.render()
    pts = {}
    co = vtk.vtkCoordinate(); co.SetCoordinateSystemToWorld()
    for k, xyz in (anclas or {}).items():
        co.SetValue(*xyz); x, y = co.GetComputedDoubleDisplayValue(p.renderer)
        pts[k] = (x, H - y)
    p.screenshot(nombre + '.png')
    p.close()
    return pts

P = modelo()
out = {}
# vista 1: registro armado
cam1 = [(1.55, -1.75, 1.25), (0, 0, -0.18), (0, 0, 1)]
out['v1'] = escena(P, {}, cam=cam1, nombre='v1', anclas={
    '1': (-0.45, -0.55, 0), '4': (0.30, -0.37, 0.0), '9': (0.20, -0.33, 0.0), '8': (-0.1, -0.1, 0), '7': (0.0, 0.22, -0.01), '10': (0.55, -0.2, -0.35)})
# vista 2: despiece
offs = {'contramarco': 0.32, 'anclajes': 0.32, 'parrilla': 0.55, 'asas': 0.80, 'tapa': 1.05, 'marco': 1.33}
cam2 = [(2.35, -2.55, 2.35), (0, 0, 0.45), (0, 0, 1)]
out['v2'] = escena(P, offs, cam=cam2, nombre='v2', anclas={
    '1': (-0.45, -0.6, 0), '4': (0.36, -0.36, 0.32), '5': (0.5, -0.125, 0.29), '6': (-0.31, -0.1, 0.55 - 0.055),
    '7': (0.155, -0.22, 0.80 - 0.06), '8': (0.34, -0.2, 1.05 - 0.04), '9': (0.34, -0.34, 1.33), '10': (0.55, -0.3, -0.35)})
# vista 3: corte a-a por el registro
cam3 = [(0.88, 0.66, 0.12), (0.24, 0, -0.10), (0, 0, 1)]
YC = -0.125
out['v3'] = escena(P, {}, cut=YC, cam=[(0.88, 0.66 + YC, 0.12), (0.24, YC, -0.10), (0, 0, 1)], nombre='v3', anclas={
    '1': (0.05, -0.55, 0.0), '2': (0.42, YC, -0.17), '3': (0.375, YC, -0.045), '4': (0.352, YC, -0.035), '5': (0.44, YC, -0.03),
    '6': (0.0, YC, -0.0545), '8': (0.15, YC, -0.03), '9': (0.338, YC, -0.025), '10': (0.50, YC, -0.40),
    'ap': (0.325, YC, -0.08), 'hg': (0.345, YC, -0.005)})
# vista 4: tapa sola con concreto transparente
T = {k: P[k] for k in ('tapa', 'marco', 'parrilla', 'asas')}
cam4 = [(0.78, -0.95, 0.72), (0, 0, -0.05), (0, 0, 1)]
out['v4'] = escena(T, {}, opac={'tapa': 0.28}, cam=cam4, nombre='v4', sombras=False, piso=False, anclas={
    '6': (-0.31, -0.2, -0.055), '7': (0.06, -0.22, -0.015), '8': (-0.2, -0.34, -0.06), '9': (0.34, 0.1, 0.0), 'h': (-0.12, 0.22, -0.06)})
json.dump(out, open('anclas.json', 'w'))
print('listo')
