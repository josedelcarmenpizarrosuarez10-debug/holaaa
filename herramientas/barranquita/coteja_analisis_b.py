"""Comprueba que la memoria hidrologica (cuerpo y anexo N.° 01) de la I.E. N.° 0590 Barranquita tenga los mismos valores que la hoja
ANALISIS_ESTADISTICO_IE0590_BARRANQUITA.xlsx (formato del usuario): serie, parametros, distribuciones B.1 a B.4, Kolmogorov-Smirnov por dato
y resumen, resumen C.4, cuadros N.° 04 a 06 (modelo de Bell y regresion), K, m, n, intensidades y precipitaciones de diseno (Dick y Peschke).
Compara cada numero con la precision con que se imprime en el Word. Uso: python3 herramientas/barranquita/coteja_analisis_b.py
"""
import os
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import openpyxl, re, sys
from docx import Document
X = openpyxl.load_workbook("entregables_barranquita/ANALISIS_ESTADISTICO_IE0590_BARRANQUITA.xlsx", data_only=True)
d = Document("entregables_barranquita/MEMORIA_HIDROLOGICA_DRENAJE_PLUVIAL_IE0590_BARRANQUITA.docx")
TABLAS = [t for t in d.tables if not (len(t.rows) == 1 and len(t.columns) == 1)]      # sin la franja del titulo de la caratula
T = [[[c.text.strip() for c in r.cells] for r in t.rows] for t in TABLAS]
A, B, C, R, P, I, PD = (X[n] for n in X.sheetnames if n != "CARÁTULA")
tot = [0]; mal = []
def num(s):
    s = s.replace(",", "").replace("%", "").replace("−", "-").strip()
    try: return float(s)
    except: return None
def cmp(mem, ex, lab):
    v = num(mem) if isinstance(mem, str) else mem
    if v is None or ex is None: mal.append((lab, mem, ex, "sin dato")); return
    dec = len(mem.split(".")[1]) if isinstance(mem, str) and "." in mem else 0
    tol = 0.5 * 10 ** (-dec) + 1e-9
    tot[0] += 1
    if abs(v - ex) > tol: mal.append((lab, mem, round(ex, 6)))
# Tabla 08: serie
for i, row in enumerate(T[7][1:]):
    r = 18 + i
    cmp(row[0], A.cell(r, 2).value, "serie año")
    for j in range(12):
        ex = A.cell(r, 3 + j).value
        if isinstance(ex, str): 
            if row[1 + j] != ex: mal.append(("serie S/D", row[1+j], ex))
        else: cmp(row[1 + j], ex, "serie %d mes %d" % (A.cell(r,2).value, j+1))
    if len(row) > 13: cmp(row[13], A.cell(r, 15).value, "serie max %d" % A.cell(r,2).value)
# Tabla 11: parametros
par = {r[0]: r[1] for r in T[10][1:]}
for k, ex in (("Número de datos (n)", B["C41"].value), ("Media (mm)", B["C36"].value), ("Desviación estándar (mm)", B["C38"].value),
              ("Coeficiente de asimetría", B["C39"].value), ("Media de log P", B["D36"].value), ("Desviación estándar de log P", B["D38"].value),
              ("Asimetría de log P", B["D39"].value)):
    cmp(par.get(k), ex, "parametro " + k)
# Tablas 12-15
for i, row in enumerate(T[11][1:]): cmp(row[2], B.cell(11+i, 9).value, "normal z T%s" % row[0]); cmp(row[3], B.cell(11+i, 10).value, "normal P T%s" % row[0])
for i, row in enumerate(T[12][1:]): cmp(row[2], B.cell(58+i, 6).value, "lognormal z T%s" % row[0]); cmp(row[3], B.cell(58+i, 7).value, "lognormal logP"); cmp(row[4], B.cell(58+i, 8).value, "lognormal P T%s" % row[0])
for i, row in enumerate(T[13][1:]): cmp(row[1], B.cell(11+i, 15).value, "lp3 z"); cmp(row[2], B.cell(11+i, 16).value, "lp3 KT T%s" % row[0]); cmp(row[3], B.cell(11+i, 17).value, "lp3 logP"); cmp(row[4], B.cell(11+i, 18).value, "lp3 P T%s" % row[0])
for i, row in enumerate(T[14][1:]): cmp(row[1], B.cell(46+i, 4).value, "gumbel KT"); cmp(row[2], B.cell(46+i, 5).value, "gumbel P T%s" % row[0])
# Tabla 16: K-S por dato
for i, row in enumerate(T[15][1:]):
    r = 22 + i
    cmp(row[1], C.cell(r, 3).value, "KS P m%d" % (i+1)); cmp(row[2], C.cell(r, 5).value, "KS E m%d" % (i+1))
    for j, col in enumerate((9, 13, 21, 26)): cmp(row[3+j], C.cell(r, col).value, "KS D%d m%d" % (j, i+1))
# Tabla 17
for i, col in enumerate(("D52", "E52", "G52", "I52")): cmp(T[16][1+i][1], C[col].value, "KS Dmax " + T[16][1+i][0]); cmp(T[16][1+i][2], C["P52"].value, "KS crit")
# Tabla 18 resumen
for i, row in enumerate(T[17][1:]):
    for j in range(5): cmp(row[1+j], R.cell(10+i, 8+j).value, "resumen T%s col%d" % (row[0], j))
# Tablas 19-20 Bell
for i, row in enumerate(T[18][1:]):
    cmp(row[1], P.cell(12+i, 3).value, "C04 P24 T%s" % row[0])
    for j in range(6): cmp(row[2+j], P.cell(12+i, 4+j).value, "C04 T%s t%d" % (row[0], j))
for i, row in enumerate(T[19][1:]):
    for j in range(6): cmp(row[2+j], P.cell(25+i, 4+j).value, "C05 T%s t%d" % (row[0], j))
# Tabla 21
for k, ref in (("K", "D12"), ("m", "D13"), ("n", "D14")):
    cmp(next(r[1] for r in T[20] if r[0] == k), I[ref].value, "IDF " + k)
# Tablas 22/23 Dick-Peschke vs C. P diseno (T 500, 100, 50, 25, 10)
bloques = {500: 11, 100: 46, 50: 81, 25: 116, 10: 154}
hdr = [int(h.split("=")[1]) for h in T[21][0][1:]]
for tb, esI in ((T[21], False), (T[22], True)):
    for row in tb[1:]:
        dmin = int(row[0])
        for j, Tr in enumerate(hdr):
            if Tr not in bloques: continue
            r0 = bloques[Tr]
            for r in range(r0, r0 + 31):
                if PD.cell(r, 2).value == dmin:
                    cmp(row[1+j], PD.cell(r, 5 if esI else 4).value, ("DP I" if esI else "DP P") + " T%d d%d" % (Tr, dmin)); break
# Tabla 26 (T 25)
for row in T[25][1:]:
    dmin = int(row[0])
    for r in range(116, 131):
        if PD.cell(r, 2).value == dmin: cmp(row[2], PD.cell(r, 4).value, "T25 P d%d" % dmin); cmp(row[3], PD.cell(r, 5).value, "T25 I d%d" % dmin)
# Tabla 10 y 33
cmp(T[9][1][2], R["L14"].value, "P24 diseño tabla 10"); cmp(T[9][1][3], PD["E116"].value, "I diseño tabla 10")
cmp(next(r[1] for r in T[31+1] if r[0] == "Intensidad de diseño").split()[0], PD["E116"].value, "I parametros de diseño")
# Anexo: intensidades B (tabla 43) vs B. Int.maxima C18:I29
an = T[43]; k0 = next(i for i, r in enumerate(an) if r[0] == "(minutos)")
for i in range(12):
    row = an[k0 + 1 + i]
    for j in range(7): cmp(row[1+j], I.cell(18+i, 3+j).value, "anexo Int t%s col%d" % (row[0], j))
an = T[44]; k0 = next(i for i, r in enumerate(an) if r[0] == "D (min)")
for row in an[k0+1:]:
    if num(row[0]) is None: continue
    for r in range(116, 131):
        if PD.cell(r, 2).value == int(row[0]): cmp(row[2], PD.cell(r, 4).value, "anexo C P d%s" % row[0]); cmp(row[3], PD.cell(r, 5).value, "anexo C I d%s" % row[0])
n_cuerpo = tot[0]
def celdas(t):           # filas sin celdas repetidas por combinacion
    out = []
    for r in t.rows:
        fila = []; prev = None
        for c in r.cells:
            if c._tc is prev: continue
            prev = c._tc; fila.append(c.text.strip())
        out.append(fila)
    return out
TT = [celdas(t) for t in TABLAS]
# Anexo 1: registro (tabla 38)
an = TT[38]; k0 = next(i for i, r in enumerate(an) if r and r[0] == "Año")
for i in range(25):
    row = an[k0 + 1 + i]; r = 18 + i
    cmp(row[0], A.cell(r, 2).value, "anx serie año")
    for j in range(12):
        ex = A.cell(r, 3 + j).value
        if isinstance(ex, str):
            if row[1+j] != ex: mal.append(("anx S/D", row[1+j], ex))
        else: cmp(row[1+j], ex, "anx serie")
    cmp(row[13], A.cell(r, 15).value, "anx max")
# Anexo 2: modelos (tabla 39). Columnas izquierda: Año, P, logP; derecha: bloques
an = TT[39]; k0 = next(i for i, r in enumerate(an) if r and r[0] == "Año")
for i in range(25):
    row = an[k0 + 1 + i]; cmp(row[1], B.cell(11+i, 3).value, "anx P año"); cmp(row[2], B.cell(11+i, 4).value, "anx logP año")
txt = [" | ".join(r) for r in an]
raw = T[39]
def bloque(titulo, ncol):
    k = next(i for i, r in enumerate(raw) if any(titulo in c for c in r[4:]))
    return [r[4:4 + ncol] for r in raw[k + 2:k + 11]]
for i, r in enumerate(bloque("B.1.", 5)): cmp(r[4], B.cell(11+i, 10).value, "anx B1 P"); cmp(r[3], B.cell(11+i, 9).value, "anx B1 z")
for i, r in enumerate(bloque("B.2.", 6)): cmp(r[5], B.cell(58+i, 8).value, "anx B2 P"); cmp(r[4], B.cell(58+i, 7).value, "anx B2 logP")
for i, r in enumerate(bloque("B.3.", 7)): cmp(r[6], B.cell(11+i, 18).value, "anx B3 P"); cmp(r[4], B.cell(11+i, 16).value, "anx B3 KT")
k = next(i for i, r in enumerate(an) if any("B.4." in c for c in r))
for i in range(9):
    r = an[k + 2 + i]; cmp(r[1], B.cell(46+i, 4).value, "anx B4 KT"); cmp(r[2], B.cell(46+i, 5).value, "anx B4 P")
for lab, ex in (("m (media)", (B["C36"].value, B["D36"].value)), ("s (desv. est.)", (B["C38"].value, B["D38"].value)), ("Coef. asimetría", (B["C39"].value, B["D39"].value))):
    r = next(r for r in an if r and r[0] == lab); cmp(r[1], ex[0], "anx " + lab); cmp(r[2], ex[1], "anx log " + lab)
# Anexo 3: K-S y C.4 (tabla 40)
an = TT[40]
for nom, ref in (("Normal", "D52"), ("Log Normal", "E52"), ("Log Pearson III", "G52"), ("Gumbel", "I52")):
    r = next(r for r in an if r and r[0] == nom and len(r) >= 3); cmp(r[1], C[ref].value, "anx KS " + nom); cmp(r[2], C["P52"].value, "anx KS crit")
k = next(i for i, r in enumerate(an) if r and r[0] == "Normales")
for i in range(9):
    r = an[k + 1 + i]; vals = r[-6:]
    for j in range(6): cmp(vals[j], R.cell(10+i, 7+j).value, "anx C4 fila %d col %d" % (i, j))
for lab, ref in (("Media aritmética", "E10"), ("Desviación estándar", "E11"), ("Coeficiente de asimetría", "E12"), ("Variación del coef. de asimetría", "E14"), ("Desv. est. coef. de asimetría", "E15")):
    r = next(r for r in an[k:k+8] if r and r[0] == lab); cmp(r[1], R[ref].value, "anx C4 " + lab)
# Anexo 4: cuadros 04 y 05 (tabla 41)
an = TT[41]; ks = [i for i, r in enumerate(an) if r and r[0] == "años"]
for q, (k, f0) in enumerate(zip(ks, (12, 25))):
    for i in range(9):
        r = an[k + 1 + i]; cmp(r[1], P.cell(f0+i, 3).value, "anx C0%d P24" % (4+q))
        for j in range(6): cmp(r[2+j], P.cell(f0+i, 4+j).value, "anx C0%d" % (4+q))
# Anexo 5: regresion (tabla 42) vs A. Parametros B51:I53
an = TT[42]; k = next(i for i, r in enumerate(an) if r and r[0] == "Matriz del sistema")
for i in range(3):
    r = an[k + 1 + i]
    for j in range(4): cmp(r[1+j], P.cell(51+i, 2+j).value, "anx matriz")
    for j in range(3): cmp(r[5+j], P.cell(51+i, 6+j).value, "anx inversa")
r = an[k + 5] if an[k+4][0] != "Resultado" else an[k+4]
r = next(r for r in an if r and r[0] == "Resultado")
cmp(r[1].split("=")[1], P["I51"].value, "anx m"); cmp(r[2].split("=")[1], -P["I52"].value, "anx n"); cmp(r[3].split("=")[1], P["I53"].value, "anx logK"); cmp(r[4].split("=")[1], I["D12"].value, "anx K")

print("Memoria hidrologica vs ANALISIS_ESTADISTICO: %d valores comparados (cuerpo %d, anexo %d); diferencias: %d" % (tot[0], n_cuerpo, tot[0] - n_cuerpo, len(mal)))
for m in mal[:60]: print("  ", m)
sys.exit(1 if mal else 0)
