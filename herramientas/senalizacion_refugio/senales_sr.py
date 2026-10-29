# -*- coding: utf-8 -*-
"""Imágenes de las señales y equipos del Hogar de Refugio Temporal (CUI 2675514) para la memoria y las especificaciones.

Mismo dibujo de las señales del expediente (varones/senalizacion/senales_img.py: forma, color de seguridad y de contraste de la
NTP 399.010-1, pictograma, texto y placa en braille grado 1 de la Norma A.120), con lo propio de este hogar:
  - señal de dirección de evacuación (flecha y SALIDA, 0.20 x 0.30 m), sin braille como en la leyenda del plano;
  - señales de servicios higiénicos de 0.20 x 0.30 m (proporción de los símbolos del plano);
  - extintor PQS tipo ABC de 9 kg.

Uso: python3 herramientas/senalizacion_refugio/senales_sr.py
Salida: entregables/figuras_senalizacion/senal_<partida>.png
"""
import os
import sys

from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__)); HER = os.path.dirname(AQUI)
for d in (AQUI, os.path.join(HER, 'varones', 'senalizacion')):
    sys.path.insert(0, d)
import datos_sr as D  # noqa: E402
import senales_img as SI  # noqa: E402

FIG = os.path.join(D.SAL, 'figuras_senalizacion')
nombre = SI.nombre


def senal(p):
    """(imagen, texto en braille) de la partida."""
    k = p['desc'].upper()
    if k.startswith('SEÑAL DE DIRECCIÓN'):
        im, d, W, H = SI.lienzo(20, 30, SI.VERDE, SI.BLANCO)
        SI.flecha(d, W / 2, H * 0.33, W * 0.72, SI.BLANCO)
        d.rectangle((W * 0.06, H * 0.64, W * 0.94, H * 0.65), fill=SI.BLANCO)
        SI.texto(d, W / 2, H * 0.81, 'SALIDA', W * 0.80, H * 0.20, SI.BLANCO)
        return im, None
    if k.startswith('SEÑAL DE SERVICIOS'):
        im, d, W, H = SI.lienzo(20, 30, SI.AZUL, SI.BLANCO)
        if 'DISCAPACIDAD' in k:
            SI.glifo(d, W / 2, H * 0.36, '♿', W * 0.62, SI.BLANCO); br = 'ss.hh. discapacitados'
        elif 'MIXTO' in k:
            SI.persona(d, W * 0.31, H * 0.10, H * 0.50, SI.BLANCO); SI.persona(d, W * 0.69, H * 0.10, H * 0.50, SI.BLANCO, mujer=True)
            br = 'ss.hh. mixto'
        elif 'MUJER' in k:
            SI.persona(d, W / 2, H * 0.08, H * 0.54, SI.BLANCO, mujer=True); br = 'ss.hh. mujeres'
        else:
            SI.persona(d, W / 2, H * 0.08, H * 0.54, SI.BLANCO); br = 'ss.hh. varones'
        d.rectangle((W * 0.06, H * 0.69, W * 0.94, H * 0.70), fill=SI.BLANCO)
        SI.texto(d, W / 2, H * 0.84, 'SS.HH.', W * 0.72, H * 0.17, SI.BLANCO)
        return im, br
    if k.startswith('EXTINTOR DE POLVO'):
        im = Image.new('RGB', (400, 640), SI.BLANCO); d = ImageDraw.Draw(im)
        SI.extintor(d, 190, 340, 520, SI.ROJO, False)
        d.rounded_rectangle((135, 330, 245, 470), radius=10, fill=SI.BLANCO)
        SI.texto(d, 190, 400, 'PQS|ABC|9 kg', 100, 120, SI.NEGRO)
        return im, None
    clave = p['desc'] if p['item'].startswith('05') else p['clave']
    return SI.senal(clave)


def generar():
    os.makedirs(FIG, exist_ok=True)
    res = {}
    for p in D.partidas():
        if not p['und']:
            continue
        im, br = senal(p)
        im = SI.con_braille(im, br, br.upper() if br else '')
        ruta = os.path.join(FIG, 'senal_%s.png' % nombre(p['desc']))
        im.save(ruta); res[p['item']] = ruta
    return res


if __name__ == '__main__':
    r = generar()
    print(len(r), 'señales en', FIG)
