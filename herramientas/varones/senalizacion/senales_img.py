# -*- coding: utf-8 -*-
"""Imágenes de las señales de seguridad del CAR Varones (CUI 2705619) para la memoria descriptiva y las especificaciones.

Dos imágenes por partida:
  - SEÑAL: la señal tal como se fabrica, dibujada a escala de sus dimensiones con la forma, el color de seguridad y el color de
    contraste de la NTP 399.010-1 (verde = evacuación y emergencia, rojo = equipos contra incendio y prohibición, amarillo =
    advertencia, azul = información), su pictograma y su texto, con la placa inferior en braille (grado 1, Norma A.120) que
    reproduce el texto de la señal punto por punto;
  - SÍMBOLO: el bloque de la leyenda de la lámina SE-S-01 tal como está dibujado en el plano (para las señales que el plano
    trae como imagen pegada sin ubicación en el DXF, solo la señal).

Uso: python3 herramientas/varones/senalizacion/senales_img.py
Salida: entregables_varones/figuras_senalizacion/senal_<clave>.png y simbolo_<clave>.png
"""
import math
import os
import re
import sys
import unicodedata

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import datos_se as D  # noqa: E402

FIG = os.path.join(D.SAL, 'figuras_senalizacion')
PX = 20                                   # píxeles por centímetro
VERDE, ROJO, AMARILLO, AZUL, BLANCO, NEGRO = (0, 135, 75), (204, 20, 30), (255, 205, 0), (0, 70, 150), (255, 255, 255), (20, 20, 20)
FUENTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FUENTE_N = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def fuente(t, bold=True):
    return ImageFont.truetype(FUENTE if bold else FUENTE_N, max(6, int(t)))


def texto(d, cx, cy, s, ancho_max, alto_max, color, bold=True):
    """Texto centrado en (cx, cy), en una o varias líneas (separadas por |), del mayor tamaño que entra en la caja."""
    lineas = s.split('|')
    t = int(alto_max / len(lineas) / 1.15)
    while t > 6:
        f = fuente(t, bold)
        anchos = [d.textbbox((0, 0), l, font=f)[2] for l in lineas]
        if max(anchos) <= ancho_max:
            break
        t -= 1
    f = fuente(t, bold); h = t * 1.15
    y = cy - h * len(lineas) / 2
    for l in lineas:
        w = d.textbbox((0, 0), l, font=f)[2]
        d.text((cx - w / 2, y), l, font=f, fill=color); y += h


# ---------------------------------------------------------------------------------------------- pictogramas
def persona(d, cx, top, h, color, mujer=False):
    r = h * 0.11
    d.ellipse((cx - r, top, cx + r, top + 2 * r), fill=color)
    y0 = top + 2.35 * r; w = h * 0.30
    if mujer:
        d.polygon([(cx - w * 0.30, y0), (cx + w * 0.30, y0), (cx + w * 0.62, y0 + h * 0.42), (cx - w * 0.62, y0 + h * 0.42)], fill=color)
        d.rounded_rectangle((cx - w * 0.70, y0, cx - w * 0.45, y0 + h * 0.30), radius=w * 0.1, fill=color)
        d.rounded_rectangle((cx + w * 0.45, y0, cx + w * 0.70, y0 + h * 0.30), radius=w * 0.1, fill=color)
        d.rectangle((cx - w * 0.28, y0 + h * 0.42, cx - w * 0.08, y0 + h * 0.70), fill=color)
        d.rectangle((cx + w * 0.08, y0 + h * 0.42, cx + w * 0.28, y0 + h * 0.70), fill=color)
    else:
        d.rounded_rectangle((cx - w * 0.5, y0, cx + w * 0.5, y0 + h * 0.36), radius=w * 0.18, fill=color)
        d.rounded_rectangle((cx - w * 0.75, y0, cx - w * 0.55, y0 + h * 0.32), radius=w * 0.1, fill=color)
        d.rounded_rectangle((cx + w * 0.55, y0, cx + w * 0.75, y0 + h * 0.32), radius=w * 0.1, fill=color)
        d.rectangle((cx - w * 0.45, y0 + h * 0.33, cx - w * 0.05, y0 + h * 0.66), fill=color)
        d.rectangle((cx + w * 0.05, y0 + h * 0.33, cx + w * 0.45, y0 + h * 0.66), fill=color)


def corredor(d, cx, cy, h, color):
    """Figura humana corriendo (pictograma de salida)."""
    k = h / 10; lw = int(k * 1.4)
    d.ellipse((cx + 0.6 * k, cy - 5.2 * k, cx + 2.4 * k, cy - 3.4 * k), fill=color)
    tronco = [(cx + 1.0 * k, cy - 3.0 * k), (cx - 0.4 * k, cy + 0.6 * k)]
    d.line(tronco, fill=color, width=int(lw * 1.4))
    for seg in ([(cx + 0.8 * k, cy - 2.4 * k), (cx + 2.4 * k, cy - 1.2 * k), (cx + 3.4 * k, cy - 2.0 * k)],
                [(cx + 0.6 * k, cy - 2.2 * k), (cx - 1.2 * k, cy - 2.6 * k), (cx - 2.2 * k, cy - 1.4 * k)],
                [(cx - 0.4 * k, cy + 0.6 * k), (cx + 1.4 * k, cy + 2.0 * k), (cx + 1.4 * k, cy + 4.4 * k)],
                [(cx - 0.4 * k, cy + 0.6 * k), (cx - 1.6 * k, cy + 2.6 * k), (cx - 3.6 * k, cy + 2.8 * k)]):
        d.line(seg, fill=color, width=lw, joint='curve')
        for p in seg:
            d.ellipse((p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2), fill=color)


def flecha(d, cx, cy, L, color):
    t = L * 0.22
    d.rectangle((cx - L / 2, cy - t / 2, cx + L * 0.12, cy + t / 2), fill=color)
    d.polygon([(cx + L * 0.05, cy - t * 1.4), (cx + L / 2, cy), (cx + L * 0.05, cy + t * 1.4)], fill=color)


def extintor(d, cx, cy, h, color, co2=False):
    w = h * 0.30
    d.rounded_rectangle((cx - w / 2, cy - h * 0.25, cx + w / 2, cy + h * 0.5), radius=w * 0.45, fill=color)
    d.rectangle((cx - w * 0.15, cy - h * 0.36, cx + w * 0.15, cy - h * 0.24), fill=color)
    d.polygon([(cx - w * 0.15, cy - h * 0.40), (cx + w * 0.9, cy - h * 0.46), (cx + w * 0.9, cy - h * 0.40), (cx + w * 0.15, cy - h * 0.34)], fill=color)
    if co2:                                   # corneta del CO2
        d.line([(cx + w * 0.10, cy - h * 0.34), (cx + w * 0.85, cy - h * 0.10)], fill=color, width=int(w * 0.10))
        d.polygon([(cx + w * 0.75, cy - h * 0.12), (cx + w * 1.15, cy + h * 0.10), (cx + w * 0.55, cy + h * 0.06)], fill=color)
    else:                                     # manguera
        d.arc((cx - w * 1.1, cy - h * 0.38, cx - w * 0.2, cy + h * 0.25), 100, 260, fill=color, width=int(w * 0.10))


def campana(d, cx, cy, h, color, fondo):
    w = h * 0.8
    d.pieslice((cx - w / 2, cy - h / 2, cx + w / 2, cy + h * 0.5), 180, 360, fill=color)
    d.rectangle((cx - w / 2, cy, cx + w / 2, cy + h * 0.25), fill=color)
    d.rectangle((cx - w * 0.62, cy + h * 0.22, cx + w * 0.62, cy + h * 0.32), fill=color)
    d.ellipse((cx - h * 0.09, cy + h * 0.32, cx + h * 0.09, cy + h * 0.50), fill=color)
    d.ellipse((cx - h * 0.06, cy - h * 0.62, cx + h * 0.06, cy - h * 0.50), fill=color)


def sirena(d, cx, cy, h, color):
    d.rectangle((cx - h * 0.42, cy - h * 0.14, cx - h * 0.22, cy + h * 0.14), fill=color)
    d.polygon([(cx - h * 0.22, cy - h * 0.14), (cx + h * 0.02, cy - h * 0.34), (cx + h * 0.02, cy + h * 0.34), (cx - h * 0.22, cy + h * 0.14)], fill=color)
    for k, r in enumerate((0.20, 0.32, 0.44)):
        d.arc((cx - r * h + h * 0.06, cy - r * h, cx + r * h + h * 0.06, cy + r * h), -50, 50, fill=color, width=int(h * 0.05))


def panel(d, cx, cy, h, color, fondo):
    w = h * 0.9
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h * 0.08, fill=color)
    d.rectangle((cx - w * 0.36, cy - h * 0.36, cx + w * 0.36, cy - h * 0.08), fill=fondo)
    for i in range(4):
        x = cx - w * 0.33 + i * w * 0.22
        d.ellipse((x - h * 0.05, cy + h * 0.08, x + h * 0.05, cy + h * 0.18), fill=fondo)
        d.rectangle((x - h * 0.06, cy + h * 0.25, x + h * 0.06, cy + h * 0.36), fill=fondo)


def rayo(d, cx, cy, h, color):
    d.polygon([(cx + h * 0.10, cy - h * 0.50), (cx - h * 0.22, cy + h * 0.05), (cx - h * 0.02, cy + h * 0.05),
               (cx - h * 0.12, cy + h * 0.50), (cx + h * 0.24, cy - h * 0.08), (cx + h * 0.03, cy - h * 0.08)], fill=color)


def triangulo(d, cx, cy, L, borde=NEGRO):
    h = L * math.sqrt(3) / 2
    p = [(cx, cy - h * 0.62), (cx + L / 2, cy + h * 0.38), (cx - L / 2, cy + h * 0.38)]
    d.polygon(p, fill=borde)
    q = [(cx + (x - cx) * 0.80, cy + (y - cy) * 0.80 + h * 0.03) for x, y in p]
    d.polygon(q, fill=AMARILLO)
    rayo(d, cx, cy + h * 0.06, h * 0.52, NEGRO)


def glifo(d, cx, cy, ch, alto, color):
    f = fuente(alto)
    b = d.textbbox((0, 0), ch, font=f)
    d.text((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2), ch, font=f, fill=color)


# ---------------------------------------------------------------------------------------------- braille
_BR = {'a': '1', 'b': '12', 'c': '14', 'd': '145', 'e': '15', 'f': '124', 'g': '1245', 'h': '125', 'i': '24', 'j': '245',
       'k': '13', 'l': '123', 'm': '134', 'n': '1345', 'o': '135', 'p': '1234', 'q': '12345', 'r': '1235', 's': '234', 't': '2345',
       'u': '136', 'v': '1236', 'w': '2456', 'x': '1346', 'y': '13456', 'z': '1356', 'á': '12356', 'é': '2346', 'í': '34',
       'ó': '346', 'ú': '23456', 'ñ': '12456', 'ü': '1256', '.': '3', ',': '2', '-': '36', '/': '2'}


def celdas_braille(s):
    out = []; num = False
    for ch in s.lower():
        if ch.isdigit():
            if not num:
                out.append('3456'); num = True
            out.append(_BR['jabcdefghi'[int(ch)]])
            continue
        num = False
        if ch == ' ':
            out.append('')
        elif ch in _BR:
            out.append(_BR[ch])
    return out


def placa_braille(ancho, texto_br, rotulo):
    """Placa de acrílico con el texto en braille (celdas de 6 puntos) y el texto en tinta debajo."""
    cel = celdas_braille(texto_br)
    paso = ancho * 0.92 / max(len(cel), 12); r = paso * 0.11
    h = int(paso * 1.9 + 0.08 * ancho)
    im = Image.new('RGB', (ancho, h), (238, 238, 238)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, ancho - 1, h - 1), outline=(150, 150, 150), width=2)
    x0 = (ancho - paso * len(cel)) / 2 + paso * 0.25; y0 = paso * 0.35
    for k, c in enumerate(cel):
        for n in '123456':
            col = 0 if n in '123' else 1; fil = (int(n) - 1) % 3
            x = x0 + k * paso + col * paso * 0.42; y = y0 + fil * paso * 0.42
            if n in c:
                d.ellipse((x - r, y - r, x + r, y + r), fill=(40, 40, 40))
    texto(d, ancho / 2, h - 0.045 * ancho - 2, rotulo, ancho * 0.9, 0.06 * ancho, (90, 90, 90), bold=False)
    return im


# ---------------------------------------------------------------------------------------------- señales
def lienzo(w_cm, h_cm, fondo, borde=None):
    W, H = int(w_cm * PX), int(h_cm * PX)
    im = Image.new('RGB', (W, H), BLANCO); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=int(W * 0.04), fill=borde or fondo)
    m = int(W * 0.025) if borde else 0
    d.rounded_rectangle((m, m, W - 1 - m, H - 1 - m), radius=int(W * 0.035), fill=fondo)
    return im, d, W, H


def senal(clave):
    """(imagen, texto en braille) de la señal de la partida con esa clave del catálogo."""
    k = clave.upper()
    if k.startswith('SALIDA'):                                   # 0.30 x 0.20 horizontal
        im, d, W, H = lienzo(30, 20, VERDE, BLANCO)
        corredor(d, W * 0.22, H * 0.40, H * 0.55, BLANCO); flecha(d, W * 0.70, H * 0.40, W * 0.38, BLANCO)
        texto(d, W / 2, H * 0.82, 'SALIDA', W * 0.8, H * 0.24, BLANCO); return im, 'salida'
    if k.startswith('ZONA SEGURA EN'):
        im, d, W, H = lienzo(20, 30, VERDE, BLANCO)
        d.ellipse((W * 0.18, H * 0.06, W * 0.82, H * 0.06 + W * 0.64), outline=BLANCO, width=int(W * 0.04))
        glifo(d, W / 2, H * 0.06 + W * 0.32, 'S', W * 0.48, BLANCO)
        for i in range(-2, 9):                                   # franjas diagonales de la parte inferior
            x = i * W * 0.14
            d.polygon([(x, H * 0.97), (x + W * 0.07, H * 0.97), (x + W * 0.28, H * 0.53), (x + W * 0.21, H * 0.53)], fill=(0, 105, 55))
        d.rectangle((W * 0.10, H * 0.60, W * 0.90, H * 0.90), fill=BLANCO)
        texto(d, W / 2, H * 0.75, 'ZONA SEGURA|EN CASO|DE SISMOS', W * 0.72, H * 0.26, VERDE); return im, 'zona segura en caso de sismos'
    if k.startswith('LETRERO DE AFORO'):
        im, d, W, H = lienzo(30, 20, AZUL, BLANCO)
        texto(d, W / 2, H * 0.18, 'AFORO', W * 0.6, H * 0.20, BLANCO)
        d.rectangle((W * 0.08, H * 0.34, W * 0.92, H * 0.86), fill=BLANCO)
        texto(d, W / 2, H * 0.47, 'CAPACIDAD MÁXIMA', W * 0.76, H * 0.12, AZUL)
        texto(d, W / 2, H * 0.68, '__ PERSONAS', W * 0.6, H * 0.16, NEGRO); return im, 'aforo capacidad máxima'
    if k.startswith('ZONA DE REUNI'):
        im = Image.new('RGB', (600, 600), (205, 205, 200)); d = ImageDraw.Draw(im)
        d.ellipse((30, 30, 570, 570), outline=AMARILLO, width=36)
        glifo(d, 300, 300, 'S1', 230, (190, 150, 0)); return im, None
    if k.startswith('SEÑAL DE UBICACIÓN DE EXTINTOR'):
        co2 = 'CO2' in k
        im, d, W, H = lienzo(20, 30, ROJO, BLANCO)
        extintor(d, W * 0.46, H * 0.36, H * 0.48, BLANCO, co2)
        d.rectangle((W * 0.05, H * 0.72, W * 0.95, H * 0.73), fill=BLANCO)
        texto(d, W / 2, H * 0.85, 'EXTINTOR|%s' % ('CO₂' if co2 else 'PQS'), W * 0.8, H * 0.20, BLANCO)
        return im, 'extintor %s' % ('co2' if co2 else 'pqs')
    if k.startswith('ALARMA CONTRA'):
        im, d, W, H = lienzo(20, 30, ROJO, BLANCO)
        campana(d, W / 2, H * 0.33, H * 0.36, BLANCO, ROJO)
        texto(d, W / 2, H * 0.80, 'ALARMA|CONTRA|INCENDIOS', W * 0.82, H * 0.30, BLANCO); return im, 'alarma contra incendios'
    if k.startswith('AVISADOR SONORO'):
        im, d, W, H = lienzo(20, 30, ROJO, BLANCO)
        sirena(d, W / 2, H * 0.33, H * 0.40, BLANCO)
        texto(d, W / 2, H * 0.80, 'AVISADOR|SONORO', W * 0.82, H * 0.22, BLANCO); return im, 'avisador sonoro'
    if k.startswith('CENTRAL DE ALARMA'):
        im, d, W, H = lienzo(20, 30, ROJO, BLANCO)
        panel(d, W / 2, H * 0.33, H * 0.34, BLANCO, ROJO)
        texto(d, W / 2, H * 0.80, 'CENTRAL DE|ALARMA CONTRA|INCENDIO', W * 0.84, H * 0.30, BLANCO); return im, 'central de alarma'
    if k.startswith('ATENCIÓN RIESGO') or k.startswith('RIESGO DE DESCARGA'):
        im, d, W, H = lienzo(20, 30, BLANCO, (60, 60, 60))
        triangulo(d, W / 2, H * 0.36, W * 0.84)
        d.rectangle((W * 0.06, H * 0.66, W * 0.94, H * 0.95), fill=AMARILLO)
        t = 'ATENCIÓN|RIESGO|ELÉCTRICO' if k.startswith('ATENCIÓN') else 'RIESGO DE|DESCARGA|ELÉCTRICA'
        texto(d, W / 2, H * 0.805, t, W * 0.80, H * 0.26, NEGRO)
        return im, 'riesgo eléctrico' if k.startswith('ATENCIÓN') else 'riesgo de descarga'
    if k.startswith('PROHIBIDO'):
        im, d, W, H = lienzo(30, 20, BLANCO, (60, 60, 60))
        cx, cy, r = W * 0.21, H * 0.50, H * 0.36
        persona(d, cx, cy - r * 0.78, r * 1.55, NEGRO)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ROJO, width=int(r * 0.20))
        a = math.radians(45); dx, dy = r * 0.9 * math.cos(a), r * 0.9 * math.sin(a)
        d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=ROJO, width=int(r * 0.20))
        texto(d, W * 0.705, H * 0.50, 'PROHIBIDO|EL INGRESO|SOLO PERSONAL|AUTORIZADO', W * 0.46, H * 0.62, NEGRO)
        return im, 'solo personal autorizado'
    if k.startswith('SEÑALES DE SERVICIOS'):
        im, d, W, H = lienzo(20, 20, AZUL, BLANCO)
        if 'PHD' in k:
            glifo(d, W / 2, H * 0.40, '♿', H * 0.52, BLANCO); br = 'ss.hh. discapacitados'
        elif 'MIXTO' in k:
            persona(d, W * 0.32, H * 0.12, H * 0.62, BLANCO); persona(d, W * 0.68, H * 0.12, H * 0.62, BLANCO, mujer=True); br = 'ss.hh. mixto'
        elif 'MUJER' in k:
            persona(d, W / 2, H * 0.10, H * 0.64, BLANCO, mujer=True); br = 'ss.hh. mujeres'
        else:
            persona(d, W / 2, H * 0.10, H * 0.64, BLANCO); br = 'ss.hh. varones'
        texto(d, W / 2, H * 0.85, 'SS.HH.', W * 0.7, H * 0.16, BLANCO); return im, br
    if k.startswith('BOTIQUIN'):
        im, d, W, H = lienzo(20, 30, VERDE, BLANCO)
        c, s = (W / 2, H * 0.34), W * 0.50
        d.rectangle((c[0] - s / 2, c[1] - s / 6, c[0] + s / 2, c[1] + s / 6), fill=BLANCO)
        d.rectangle((c[0] - s / 6, c[1] - s / 2, c[0] + s / 6, c[1] + s / 2), fill=BLANCO)
        texto(d, W / 2, H * 0.80, 'PRIMEROS|AUXILIOS', W * 0.82, H * 0.22, BLANCO); return im, 'primeros auxilios'
    if k.startswith('PUNTO ECOL'):
        im, d, W, H = lienzo(30, 20, VERDE, BLANCO)
        glifo(d, W * 0.24, H * 0.48, '♻', H * 0.66, BLANCO)
        texto(d, W * 0.66, H * 0.48, 'PUNTO|ECOLÓGICO', W * 0.56, H * 0.46, BLANCO); return im, 'punto ecológico'
    if k.startswith('UNIDAD DE LUCES'):
        im = Image.new('RGB', (600, 420), BLANCO); d = ImageDraw.Draw(im)
        d.rounded_rectangle((60, 150, 540, 380), radius=24, fill=(235, 235, 235), outline=(120, 120, 120), width=4)
        for x in (190, 410):
            d.rounded_rectangle((x - 70, 40, x + 70, 170), radius=40, fill=(90, 90, 90))
            d.ellipse((x - 48, 62, x + 48, 150), fill=(255, 245, 190))
        d.rectangle((110, 300, 230, 340), fill=(40, 160, 70)); d.rectangle((380, 300, 490, 340), fill=(60, 60, 60))
        texto(d, 300, 245, 'LUZ DE EMERGENCIA', 420, 36, (60, 60, 60)); return im, None
    if k.startswith('DETECTOR'):
        im = Image.new('RGB', (520, 520), BLANCO); d = ImageDraw.Draw(im)
        d.ellipse((40, 40, 480, 480), fill=(240, 240, 240), outline=(130, 130, 130), width=6)
        d.ellipse((130, 130, 390, 390), fill=(225, 225, 225), outline=(150, 150, 150), width=4)
        for a in range(0, 360, 30):
            x = 260 + 165 * math.cos(math.radians(a)); y = 260 + 165 * math.sin(math.radians(a))
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(150, 150, 150))
        d.ellipse((330, 175, 352, 197), fill=ROJO); return im, None
    if k.startswith('EXTINTOR DE POLVO') or k.startswith('EXTINTOR DE DIÓXIDO'):
        co2 = 'DIÓXIDO' in k
        im = Image.new('RGB', (400, 640), BLANCO); d = ImageDraw.Draw(im)
        extintor(d, 190, 340, 520, ROJO, co2)
        d.rounded_rectangle((135, 330, 245, 470), radius=10, fill=BLANCO)
        texto(d, 190, 400, ('CO₂|10 lb' if co2 else 'PQS|ABC|6 kg'), 100, 120, NEGRO); return im, None
    raise KeyError(clave)


def con_braille(im, br, rotulo):
    if not br:
        return im
    pl = placa_braille(im.width, br, rotulo)
    out = Image.new('RGB', (im.width, im.height + pl.height + int(im.width * 0.04)), BLANCO)
    out.paste(im, (0, 0)); out.paste(pl, (0, im.height + int(im.width * 0.04)))
    return out


def nombre(clave):
    s = unicodedata.normalize('NFKD', clave).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')


# ---------------------------------------------------------------------------------------------- símbolos del plano
def simbolos(P):
    """Bloque de cada fila de la leyenda de SE-S-01 dibujado como en el plano (vistas_se.Lienzo)."""
    import lee_plano_se as LP
    import vistas_se as VS
    from ezdxf import bbox
    doc = LP.abrir(); msp = doc.modelspace()
    sel = []
    for e in msp.query('INSERT'):
        try:
            b = bbox.extents([e])
        except Exception:
            continue
        if b.has_data and LP.dentro((b.center.x, b.center.y), (3021.0, 1740, 3025.0, 1786)) and max(b.size.x, b.size.y) < 3:
            sel.append((e, b))
    out = {}
    for f in P['leyenda']:
        if not f['bloque']:
            continue
        e, b = min(((e, b) for e, b in sel if e.dxf.name == f['bloque']), key=lambda x: abs(x[1].center.x - 3023) + 0)
        m = 0.08 * max(b.size.x, b.size.y)
        L = VS.Lienzo((b.extmin.x - m, b.extmin.y - m, b.extmax.x + m, b.extmax.y + m))
        L.entidad(e)
        ruta = os.path.join(FIG, 'simbolo_%s.png' % nombre(f['descripcion'][:40]))
        L.guardar(ruta, ancho_pulg=2.2, dpi=150)
        out[f['descripcion']] = ruta
    return out


def generar(con_simbolos=False):
    os.makedirs(FIG, exist_ok=True)
    P = D.plano(); res = {}
    for p in D.partidas(P):
        if not p['und']:
            continue
        clave = p['desc'] if p['item'].startswith('05') else p['clave']
        im, br = senal(clave)
        im = con_braille(im, br, br.upper() if br else '')
        ruta = os.path.join(FIG, 'senal_%s.png' % nombre(p['desc']))
        im.save(ruta); res[p['item']] = ruta
    if con_simbolos:
        simbolos(P)
    return res


if __name__ == '__main__':
    r = generar(con_simbolos='--simbolos' in sys.argv)
    print(len(r), 'señales en', FIG)
