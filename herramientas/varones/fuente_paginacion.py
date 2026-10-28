# -*- coding: utf-8 -*-
"""Fuente de paginación: Liberation Sans escalada al 82 % en x con el nombre "Arial Narrow", instalada en ~/.fonts.

Solo sirve para que LibreOffice pagine la memoria de arquitectura (escrita en Arial Narrow) casi como Word al calcular el número
de página del índice (corrige_memoria_arquitectura_v.py); no se usa en ningún entregable.
Uso: python3 herramientas/varones/fuente_paginacion.py
"""
import os
import subprocess
from fontTools.ttLib import TTFont
F = 0.82
for est, sub in (('Regular', 'Regular'), ('Bold', 'Bold'), ('Italic', 'Italic'), ('BoldItalic', 'Bold Italic')):
    f = TTFont('/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf' % est)
    glyf = f['glyf']
    for g in f.getGlyphOrder():
        gl = glyf[g]
        if gl.isComposite():
            for c in gl.components:
                c.x = int(round(c.x * F))
        elif gl.numberOfContours > 0:
            gl.coordinates.scale((F, 1)); gl.coordinates.toInt()
            gl.program = None
            from fontTools.ttLib.tables import ttProgram
            gl.program = ttProgram.Program(); gl.program.fromBytecode(b'')
        aw, lsb = f['hmtx'][g]
        f['hmtx'][g] = (int(round(aw * F)), int(round(lsb * F)))
    for t in ('fpgm', 'prep', 'cvt ', 'hdmx', 'LTSH', 'VDMX', 'kern', 'GPOS'):
        if t in f:
            del f[t]
    f['OS/2'].xAvgCharWidth = int(f['OS/2'].xAvgCharWidth * F)
    for rec in f['name'].names:
        if rec.nameID in (1, 16):
            rec.string = 'Arial Narrow'
        elif rec.nameID == 4:
            rec.string = 'Arial Narrow ' + sub
        elif rec.nameID == 6:
            rec.string = 'ArialNarrow-' + est
    f.save(os.path.expanduser('~/.fonts/ArialNarrowPag-%s.ttf' % est))
subprocess.run(['fc-cache', '-f'], check=False)
print('ok')
