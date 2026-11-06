"""Validación de los cálculos del motor con ejemplos resueltos de la bibliografía.

Cada caso toma los datos de un ejemplo publicado y compara el resultado del motor con el del libro (tolerancia indicada: los
libros redondean y algunos leen ábacos). Los datos en pies se pasan a metros; la ecuación de Manning en unidades SI usa el
mismo n. Solo se usan los datos y resultados numéricos; el texto de los libros no se reproduce.

    python3 pruebas/validacion_bibliografia.py

Fuentes:
  PR  = Pedro Rodríguez Ruiz, Hidráulica de canales (Hidráulica II).
  FE  = Hidráulica de canales: fundamentos y ejercicios.
  FF  = Sergio Fattorelli y Pedro C. Fernández, Diseño hidrológico (2.ª ed. digital, 2011).
  MV  = Máximo Villón Béjar, Hidrología (Instituto Tecnológico de Costa Rica).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from drenie_motor import hidrologia as HI, perfil_flujo as PF, verificacion as VE, vial as V  # noqa: E402

FT, CFS = 0.3048, 0.028316846592
G = 9.81
CASOS = []
NOTAS = []


def caso(fuente, ejemplo, que, calculado, libro, tol):
    CASOS.append((fuente, ejemplo, que, calculado, libro, tol, abs(calculado - libro) <= tol * abs(libro)))


def trap(b, z): return {"tipo": "trapezoidal", "b": b, "z1": z, "z2": z}


# --------------------------------------------------------------- flujo uniforme (Manning)
Q, _ = V.manning(trap(3.0, 1.5), 2.60, 0.0016, 0.013)
caso("PR", "Ejemplo 1.1", "Caudal de un canal trapecial b = 3 m, z = 1.5, y = 2.60 m (m³/s)", Q, 70.66, 0.01)

A, P, _ = V.geometria(trap(6.0, 2.0), 1.02); R = A / P
S = (11.32 * 0.025 / (A * R ** (2 / 3))) ** 2
caso("PR", "Ejemplo 1.10", "Pendiente normal de un canal trapecial b = 6 m, z = 2, y = 1.02 m, Q = 11.32 m³/s", S, 0.00167, 0.02)

y = V.tirante(trap(20 * FT, 2.0), 400 * CFS, 0.0016, 0.025, 5.0)
caso("PR", "Ejemplo 1.7", "Tirante normal de un canal trapecial b = 20 pies, z = 2, Q = 400 pies³/s (pies)", y / FT, 3.36, 0.01)

A, P, _ = V.geometria({"tipo": "rectangular", "b": 19.7 * FT}, 3.30 * FT); R = A / P
S = (388 * CFS * 0.020 / (A * R ** (2 / 3))) ** 2
caso("PR", "Ejemplo 1.11", "Pendiente normal de un canal rectangular b = 19.7 pies, y = 3.30 pies, Q = 388 pies³/s", S, 0.0019, 0.03)

y = VE.yn(388 * CFS, 0.0019, 0.020, 19.7 * FT)
caso("PR", "Ejemplo 1.11", "Tirante normal de la cuneta rectangular del motor con la pendiente del libro (pies)", y / FT, 3.30, 0.01)

y = V.tirante({"tipo": "circular", "D": 3 * FT}, 20 * CFS, 0.0016, 0.015, 3 * FT * 0.9999)
caso("PR", "Ejemplo 1.5", "Tirante normal de una alcantarilla circular de 36\", Q = 20 pies³/s (pies; el libro lee un ábaco)", y / FT, 2.16, 0.03)

# --------------------------------------------------------------- tirante crítico
yc = PF.critico(400 * CFS, 10 * FT)
caso("PR", "Ejemplo 2.2", "Tirante crítico de un canal rectangular b = 10 pies, Q = 400 pies³/s (pies)", yc / FT, 3.678, 0.005)

# --------------------------------------------------------------- flujo gradualmente variado (paso estándar del motor)
Q, b, S0, n = 300 * CFS, 10 * FT, 0.0025, 0.016                         # PR ejemplo 4.6: canal que termina en caída libre
caso("PR", "Ejemplo 4.6", "Tirante normal del canal rectangular b = 10 pies, Q = 300 pies³/s, S = 0.0025, n = 0.016 (pies)",
     VE.yn(Q, S0, n, b) / FT, 3.842, 0.005)
caso("PR", "Ejemplo 4.6", "Tirante crítico en la caída libre (pies)", PF.critico(Q, b) / FT, 3.035, 0.002)
Lt, N = 700 * FT, 1401
est = [{"s": Lt * i / (N - 1), "z": S0 * (Lt - Lt * i / (N - 1)), "Q": Q, "b": b, "h": 5.0} for i in range(N)]
perfil = PF.perfil_eje(est, PF.critico(Q, b), n)
xs = [Lt - o["s"] for o in reversed(perfil)]; ys = [o["y"] for o in reversed(perfil)]
for L_libro, y_libro in ((75.228, 3.5), (138.561, 3.6), (243.561, 3.7)):
    y = float(HI.np.interp(L_libro * FT, xs, ys)) / FT
    caso("PR", "Ejemplo 4.6", "Perfil M2 (paso estándar del motor): tirante a %.1f pies aguas arriba de la caída (pies)" % L_libro, y, y_libro, 0.005)

# --------------------------------------------------------------- resalto hidráulico (fuerza específica)
Q, b, y1 = 50.0, 6.0, 0.40
f1 = PF.fuerza(Q, b, y1)
y2 = PF._biseccion(lambda y: PF.fuerza(Q, b, y) - f1, PF.critico(Q, b), 20.0)   # rama subcrítica: F crece con y
caso("FE", "Resalto, ejemplo 1", "Tirante conjugado mayor, canal rectangular b = 6 m, Q = 50 m³/s, y1 = 0.40 m (m)", y2, 5.75, 0.01)
dE = (y2 - y1) ** 3 / (4 * y1 * y2)
caso("FE", "Resalto, ejemplo 1", "Pérdida de energía en el resalto (m)", dE, 16.64, 0.01)
E1 = y1 + (Q / (b * y1)) ** 2 / (2 * G); E2 = y2 + (Q / (b * y2)) ** 2 / (2 * G)
caso("FE", "Resalto, ejemplo 1", "Misma pérdida por diferencia de energía específica E1 − E2 (m)", E1 - E2, 16.64, 0.01)

# --------------------------------------------------------------- análisis de frecuencias (Gumbel)
MENDOZA = [184, 218, 130, 182, 115, 398, 195, 162, 129, 243, 401, 140, 112, 144, 201, 117, 127, 195, 115, 82]   # FF tabla 4.16
n, m, s, _ = HI.estad(MENDOZA)
caso("FF", "Ejemplo 4.16", "Media de los caudales máximos del río Mendoza en Guido, 20 años (m³/s)", m, 179.5, 0.001)
import statistics
caso("FF", "Ejemplo 4.16", "Desviación estándar de la muestra, contra statistics.stdev (m³/s)", s, statistics.stdev(MENDOZA), 1e-9)
NOTAS.append("FF ejemplo 4.16: el libro da σ = 87.89 m³/s, pero la desviación de los 20 caudales de su tabla 4.16 es 85.98 m³/s "
             "(comprobado con la biblioteca estándar de Python); por eso su Q100 = 516 m³/s baja a %.0f m³/s con el mismo método." % (m + 3.84 * s))
caso("FF", "Tabla 4.15", "Factor de frecuencia de Gumbel por momentos (Ven Te Chow, N → ∞) para T = 100 años", HI.kt_gumbel(100), 3.14, 0.005)
yn = float(HI.np.interp(20, [t[0] for t in HI.GUMBEL_YN_SN], [t[1] for t in HI.GUMBEL_YN_SN]))
sn = float(HI.np.interp(20, [t[0] for t in HI.GUMBEL_YN_SN], [t[2] for t in HI.GUMBEL_YN_SN]))
k20 = (-math.log(-math.log(1 - 1 / 100.0)) - yn) / sn
caso("FF", "Tabla 4.15", "Factor de frecuencia de Gumbel con yn y σn para N = 20 años y T = 100 años", k20, 3.84, 0.005)
caso("FF", "Ejemplo 4.16", "Caudal de T = 100 años con el factor para N = 20 años, σ corregida (m³/s)", m + k20 * s, 179.5 + 3.84 * s, 0.005)
A = HI.analisis([(1977 + i, q) for i, q in enumerate(MENDOZA)], [100])
caso("FF", "Ejemplo 4.16", "Caudal de T = 100 años del análisis del motor, Gumbel por momentos (m³/s)", A["tabla"][100]["gumbel"],
     179.5 + 3.14 * s, 0.005)

# --------------------------------------------------------------- Villón: Gumbel con yn y σn, Kirpich y método racional
ANGOSTURA = [1660, 917, 3800, 1410, 2280, 618, 683, 934, 779, 921, 876, 740, 1120, 610, 1150, 563, 520, 360, 367, 658, 824, 850,
             1230, 522, 581, 557, 818, 1030, 418, 953]                     # MV tabla 6.15, estación Angostura 1970-1999
n, m, s, _ = HI.estad(ANGOSTURA)
caso("MV", "Ejemplo 6.7", "Caudal medio de 30 años (m³/s)", m, 958.30, 0.0005)
caso("MV", "Ejemplo 6.7", "Desviación estándar (m³/s)", s, 670.6893, 0.0005)
tab = {t[0]: t[1:] for t in HI.GUMBEL_YN_SN}
for N, yn_l, sn_l in ((30, 0.53622, 1.11238), (45, 0.5463, 1.15185), (60, 0.55208, 1.17467), (100, 0.56002, 1.20649)):
    caso("MV", "Tabla 6.13", "yn de Gumbel para N = %d años en la tabla del motor" % N, tab[N][0], yn_l, 1e-6)
    caso("MV", "Tabla 6.13", "σn de Gumbel para N = %d años en la tabla del motor" % N, tab[N][1], sn_l, 1e-6)
yn, sn = tab[30]
for T, Q_l in ((50, 2993.68), (100, 3411.60)):
    caso("MV", "Ejemplo 6.7", "Caudal de Gumbel Q = Qm − σQ/σN (yN − ln T) para T = %d años (m³/s)" % T, m - s / sn * (yn - math.log(T)), Q_l, 0.0005)
tc = V.tiempos({"L_m": 500, "H_m": 12})["California Culverts Practice"]
caso("MV", "Ejemplo 6.2", "Tiempo de concentración de Kirpich, L = 500 m, H = 12 m (min)", tc, 9.8143, 0.002)
C = (0.95 * 6.9817 + 0.30 * 10.4146 + 0.5 * 2.6037) / 20
caso("MV", "Ejemplo 6.2", "Coeficiente de escorrentía ponderado de 20 ha", C, 0.5529, 0.001)
caso("MV", "Ejemplo 6.2", "Caudal racional Q = C I A / 360 con I = 177 mm/h y A = 20 ha (m³/s)", C * 177 * 20 / 360, 5.4373, 0.002)


def main():
    ok = sum(1 for c in CASOS if c[6])
    for f, e, q, c, l, t, b in CASOS:
        print("%s  %-4s %-22s %-95s motor %10.5g  libro %10.5g  (±%.1f %%)" % ("OK  " if b else "FALLA", f, e, q, c, l, 100 * t))
    for t in NOTAS: print("NOTA:", t)
    print("%d de %d casos coinciden con la bibliografía" % (ok, len(CASOS)))
    return 0 if ok == len(CASOS) else 1


if __name__ == "__main__":
    sys.exit(main())
