import json
from PIL import Image, ImageDraw, ImageFont

FD = '/usr/share/fonts/truetype/dejavu/'
f = lambda s, b=False: ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf'), s)
A = json.load(open('anclas.json'))
W, H = 1400, 1000
M = 40; TOP = 150; GAP = 30; TT = 56
LEG = 520
SW = M * 2 + W * 2 + GAP
SH = TOP + 2 * (H + TT) + GAP + LEG + M
S = Image.new('RGB', (SW, SH), 'white'); d = ImageDraw.Draw(S)
AZ = (31, 78, 121); NAR = (192, 80, 20)

d.rectangle([M, 30, SW - M, TOP - 20], fill=AZ)
d.text((M + 30, 42), 'REGISTRO DE LIMPIEZA CON TAPA 0.68 x 0.68 C/MARCO Y CONTRAMARCO - COMPONENTES', font=f(44, True), fill='white')
d.text((M + 30, 96), 'Colector pluvial frontal - Hogar de Refugio Temporal "Mujeres Violentadas" (CUI 2675514) - detalle igual en CAR Mujeres (CUI 2717013) y CAR Varones (CUI 2705619) - lamina DP-06B',
       font=f(24), fill=(220, 232, 245))

TIT = {'v1': '1. REGISTRO ARMADO (vista general)', 'v2': '2. DESPIECE: CADA COMPONENTE SEPARADO',
       'v3': '3. CORTE POR EL REGISTRO: APOYO DE LA TAPA Y REFUERZOS', 'v4': '4. TAPA: ARMADO INTERIOR (concreto transparente)'}
LAB = {'ap': 'apoyo 0.05', 'hg': 'holgura 1 cm', 'h': 'bolsillo del asa'}
OFF = {  # desplazamiento del numero respecto al punto (px)
    'v1': {'1': (-90, 60), '4': (60, 90), '9': (-40, -110), '8': (-120, -40), '7': (90, -90), '10': (90, 60)},
    'v2': {'1': (-110, 70), '4': (140, 40), '5': (140, 10), '6': (-170, 30), '7': (160, -30), '8': (160, 20), '9': (150, -20), '10': (110, 60)},
    'v3': {'1': (-60, -90), '2': (-150, 90), '3': (-170, 40), '4': (60, -140), '5': (-120, -110), '6': (60, 140), '8': (60, -150),
           '9': (-90, -150), '10': (120, 90), 'ap': (-200, 150), 'hg': (150, -170)},
    'v4': {'6': (-120, 80), '7': (60, -130), '8': (-90, 90), '9': (110, -60), 'h': (-120, -120)},
}
for i, v in enumerate(('v1', 'v2', 'v3', 'v4')):
    x0 = M + (i % 2) * (W + GAP); y0 = TOP + (i // 2) * (H + TT + GAP)
    d.rectangle([x0, y0, x0 + W, y0 + TT], fill=(235, 241, 248), outline=AZ, width=2)
    d.text((x0 + 18, y0 + 12), TIT[v], font=f(28, True), fill=AZ)
    im = Image.open(v + '.png'); S.paste(im, (x0, y0 + TT)); d.rectangle([x0, y0 + TT, x0 + W, y0 + TT + H], outline=AZ, width=2)
    for k, (px, py) in A[v].items():
        if k == '3b': continue
        ox, oy = OFF[v].get(k, (80, -80))
        if not (0 <= px <= W and 0 <= py <= H): continue
        ax, ay = x0 + px, y0 + TT + py; bx, by = ax + ox, ay + oy
        bx = min(max(bx, x0 + 40), x0 + W - 40); by = min(max(by, y0 + TT + 40), y0 + TT + H - 40)
        d.line([ax, ay, bx, by], fill=NAR, width=3); d.ellipse([ax - 6, ay - 6, ax + 6, ay + 6], fill=NAR)
        if k in LAB:
            t = LAB[k]; tw = d.textlength(t, font=f(26, True))
            d.rounded_rectangle([bx - tw / 2 - 12, by - 22, bx + tw / 2 + 12, by + 22], 8, fill='white', outline=NAR, width=3)
            d.text((bx - tw / 2, by - 16), t, font=f(26, True), fill=NAR)
        else:
            d.ellipse([bx - 26, by - 26, bx + 26, by + 26], fill='white', outline=NAR, width=4)
            tw = d.textlength(k, font=f(28, True)); d.text((bx - tw / 2, by - 17), k, font=f(28, True), fill=NAR)

# leyenda
y = TOP + 2 * (H + TT) + GAP + 10
d.rectangle([M, y, SW - M, SH - M], outline=AZ, width=2)
d.rectangle([M, y, SW - M, y + 50], fill=AZ)
d.text((M + 20, y + 10), 'COMPONENTES (cantidades por registro)', font=f(28, True), fill='white')
d.text((M + 1480, y + 10), 'DATOS CLAVE', font=f(28, True), fill='white')
items = [
    ('1', "Losa superior del colector e = 0.10 m, concreto f'c=210: rebaje 0.70 x 0.70 x 0.08 m y luz libre 0.60 x 0.60 m"),
    ('2', 'Borde engrosado 0.15 x 0.10 m bajo la losa, alrededor de la abertura (0.045 m3)'),
    ('3', 'Refuerzo de borde: 2 barras de 1/2" por lado, L = 1.40 m (8 barras, 11.1 kg)'),
    ('4', 'Contramarco angulo L 2" x 2" x 3/16", luz 0.70 x 0.70, enrasado con el piso (2.80 m, 10.2 kg)'),
    ('5', 'Anclajes de 3/8" L = 0.20 m soldados al contramarco, 2 por lado (8 und)'),
    ('6', 'Parrilla de la tapa: 7 + 7 barras de 3/8" @ 0.10 m, L = 0.62 m, recubrimiento 2.5 cm (4.9 kg)'),
    ('7', 'Asas: 2 barras de 3/8" liso de 0.40 m, embutidas en bolsillo (no sobresalen del piso)'),
    ('8', "Tapa de concreto f'c=210: 0.68 x 0.68 x 0.08 m (0.037 m3)"),
    ('9', 'Marco de tapa angulo L 1 1/2" x 1 1/2" x 1/8", 0.68 x 0.68 exterior (2.72 m, 5.0 kg)'),
    ('10', 'Muros del colector e = 0.15 m (ancho interior 0.80 m)'),
]
yy = y + 66
for i, (n, t) in enumerate(items):
    cx = M + 46 + (i // 5) * 0; ry = yy + i * 43
    d.ellipse([M + 22, ry - 2, M + 58, ry + 34], fill='white', outline=NAR, width=3)
    tw = d.textlength(n, font=f(20, True)); d.text((M + 40 - tw / 2, ry + 4), n, font=f(20, True), fill=NAR)
    d.text((M + 74, ry + 3), t, font=f(23), fill=(30, 30, 30))
datos = [
    'Holgura entre marco y contramarco: (0.70 - 0.68) / 2 = 1 cm por lado',
    'Apoyo de la tapa sobre el concreto: (0.70 - 0.60) / 2 = 5 cm por lado',
    'Peso de la tapa: 0.037 m3 x 2,400 kg/m3 + marco 5.0 kg = 94 kg aprox.',
    'Se levanta entre 2 operarios con ganchos en las 2 asas',
    'Tapa a ras del piso terminado: no hay resaltes ni tropiezos',
    'Angulos con pintura anticorrosiva y esmalte (0.98 m2 por registro)',
    'Registros: Hogar de Refugio 10 und; CAR Mujeres 15 und; CAR Varones 11 und',
]
for i, t in enumerate(datos):
    ry = yy + i * 50
    d.rectangle([M + 1480, ry + 10, M + 1494, ry + 24], fill=NAR)
    d.text((M + 1506, ry + 2), t, font=f(24), fill=(30, 30, 30))
d.text((SW - M - 900, SH - M - 40), 'Medidas en metros salvo indicacion. Ref.: lamina DP-06B y metrado del colector.', font=f(20), fill=(90, 90, 90))
S.save('LAMINA_TAPA_REGISTRO_4_VISTAS.png', optimize=True)
S.resize((SW // 2, SH // 2)).save('lam_prev.png')
print(S.size)
