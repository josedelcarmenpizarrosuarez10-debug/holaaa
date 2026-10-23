# -*- coding: utf-8 -*-
"""CAR Varones (CUI 2705619): cambia en el metrado vigente los códigos de lámina de trabajo (DP-, DA-, DD-, DJ-, DL-) por los
códigos DPLV del juego final de planos de la usuaria (insumos/katiuska/PLANOS_DRENAJE_PLUVIAL_CAR_VARONES_LAMINAS.pdf).

Solo cambia texto donde va un código de lámina (sustentos, criterios, notas); no toca valores, fórmulas, formatos ni otras
celdas. Se edita el XML del libro (sharedStrings y valores de texto en caché de las fórmulas), sin reescribirlo con openpyxl.
Equivalencias (por contenido de cada lámina):
  DP-01 planta del colector -> DPLV-17          DP-02 perfil -> DPLV-18           DP-04 secciones -> DPLV-21 y DPLV-22
  DP-06B tapa ciega -> DPLV-23                  DP-06C empalme de cuneta -> DPLV-24 DP-07 empalme con la caja CL -> DPLV-25
  DP-08 cuadro de doblado y DA-01 a DA-03 (cuadros de metrado del colector): no están en el juego final; la geometría, la
        armadura y la excavación están en las secciones del colector -> DPLV-21 y DPLV-22
  DD-01 rebaje -> DPLV-27   DD-02 tapa -> DPLV-28   DD-03 juntas colector/CL -> DPLV-29   DD-04 empalme -> DPLV-30
  DJ-01 junta de cunetas -> DPLV-31   DL-01 isométrico de instalación del lloradero -> DPLV-34   DL-02 detalle -> DPLV-35
Uso: python3 herramientas/varones/codigos_laminas_metrado_v.py
"""
import os
import re
import shutil
import sys
import tempfile
import zipfile

import openpyxl

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENT = os.path.join(RAIZ, 'insumos', 'metrados_vigentes', 'METRADO_DRENAJE_PLUVIAL_CAR_VARONES.xlsx')
SAL = os.path.join(RAIZ, 'entregables_varones', 'METRADO_DRENAJE_PLUVIAL_CAR_VARONES_23-10-2026.xlsx')
S = 'DPLV-21 y DPLV-22'
# primero las frases compuestas (para no repetir láminas), luego cada código suelto
FRASES = [
    ('los planos DP-01 a DP-08, DA-01 a DA-03 y DD-01 a DD-04', 'las laminas DPLV-17 a DPLV-30'),
    ('planos DP-01 a DP-08, DA-01 a DA-03 y DD-01 a DD-04', 'laminas DPLV-17 a DPLV-30'),
    ('DP-06B rev. 02', 'DPLV-23'),
    ('DP-04 (seccion S-01), DP-08 (cuadro de doblado), DA-03', 'DPLV-21 (seccion S-01; armadura)'),
    ('DP-04 (seccion S-02 a S-08), DP-08 (cuadro de doblado), DA-03', S + ' (secciones S-02 a S-08; armadura)'),
    ('DP-04 (secciones), DP-02 (h por tramo), DA-02 (areas por metro)', S + ' (secciones y areas por metro), DPLV-18 (h por tramo)'),
    ('DP-04 (secciones), DA-02 (areas por metro)', S + ' (secciones y areas por metro)'),
    ('DP-04 (seccion), DA-01 (criterio)', S + ' (seccion y criterio)'),
    ('DP-04 (seccion S-01) y DP-08', 'DPLV-21 (seccion S-01)'),
    ('DP-04 (seccion S-01)', 'DPLV-21 (seccion S-01)'),
    ('DP-04 y DP-08', S), ('DP-04 y DA-02', S),
    ('DP-04 y DD-03', 'DPLV-21, DPLV-22 y DPLV-29'),
    ('DP-08, cuadro de doblado', S + ', armadura'), ('DP-08 (cuadro de doblado)', S + ' (armadura)'),
    ('DA-01, nota 2', S),
]
CODIGOS = [('DP-01', 'DPLV-17'), ('DP-02', 'DPLV-18'), ('DP-04', S), ('DP-06B', 'DPLV-23'), ('DP-06C', 'DPLV-24'),
           ('DP-07', 'DPLV-25'), ('DP-08', S), ('DA-01', S), ('DA-02', S), ('DA-03', S),
           ('DD-01', 'DPLV-27'), ('DD-02', 'DPLV-28'), ('DD-03', 'DPLV-29'), ('DD-04', 'DPLV-30'),
           ('DJ-01', 'DPLV-31'), ('DJ-02', 'DPLV-32'), ('DJ-03', 'DPLV-33'), ('DL-01', 'DPLV-34'), ('DL-02', 'DPLV-35')]
VIEJO = re.compile(r'\b(?:DP|DA|DD|DJ|DL)-\d')


def cambiar(txt):
    for a, b in FRASES:
        txt = txt.replace(a, b)
    for a, b in CODIGOS:
        txt = re.sub(r'\b%s\b' % re.escape(a), b, txt)
    txt = re.sub(r'\b([Ll])amina (DPLV-\d\d y DPLV-\d\d)', r'\1aminas \2', txt)      # plural cuando son dos láminas
    return txt


def textos(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    return {(ws.title, c.coordinate): c.value for ws in wb.worksheets for r in ws.iter_rows() for c in r if c.value is not None}


def main():
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(ENT) as z:
        z.extractall(tmp); nombres = z.namelist()
    n = 0
    for nom in nombres:
        if nom == 'xl/sharedStrings.xml' or (nom.startswith('xl/worksheets/') and nom.endswith('.xml')):
            p = os.path.join(tmp, nom); s = open(p, encoding='utf-8').read()
            if nom == 'xl/sharedStrings.xml':
                nuevo = re.sub(r'(<t[^>]*>)([^<]*)(</t>)', lambda m: m.group(1) + cambiar(m.group(2)) + m.group(3), s)
            else:                                            # texto en caché de fórmulas que devuelven texto (t="str")
                nuevo = re.sub(r'(<c [^>]*t="str"[^>]*>(?:<f[^>]*>[^<]*</f>|<f[^>]*/>)?<v>)([^<]*)(</v>)',
                               lambda m: m.group(1) + cambiar(m.group(2)) + m.group(3), s)
            if nuevo != s:
                n += 1; open(p, 'w', encoding='utf-8').write(nuevo)
    os.makedirs(os.path.dirname(SAL), exist_ok=True)
    with zipfile.ZipFile(SAL, 'w', zipfile.ZIP_DEFLATED) as z:
        for nom in nombres:
            z.write(os.path.join(tmp, nom), nom)
    shutil.rmtree(tmp)
    # control: solo cambian textos con código de lámina; todo lo demás igual
    a, b = textos(ENT), textos(SAL)
    dif = [(k, a[k], b.get(k)) for k in a if a[k] != b.get(k)]
    otros = [d for d in dif if not (isinstance(d[1], str) and VIEJO.search(d[1]))]
    quedan = [(k, v) for k, v in b.items() if isinstance(v, str) and VIEJO.search(v)]
    assert set(a) == set(b) and not otros and not quedan, (otros[:5], quedan[:5])
    print('%d celdas con código de lámina cambiadas (%d archivos XML); ningún otro valor cambia' % (len(dif), n))
    for (h, c), x, y in dif:
        print('  %-28s %-5s %s\n  %-34s -> %s' % (h, c, x[:110], '', y[:110]))
    print(SAL)


if __name__ == '__main__':
    main()
