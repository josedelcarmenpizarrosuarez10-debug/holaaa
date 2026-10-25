"""Hietograma de diseño por el método de bloques alternos (Chow, Maidment y Mays, Hidrología aplicada, 14.4).

De la curva IDF del proyecto (la de la estación calculada o la de la pestaña LLUVIA de DrenIE) se toma la lluvia acumulada
P(D) = I(D)·D/60 para D = Δt, 2Δt, ... hasta la duración de la tormenta; los incrementos se ordenan de mayor a menor y se
colocan alternando a la derecha y a la izquierda del bloque central. La curva se interpola en escala logarítmica entre
sus puntos y, fuera de ellos, con la recta log-log de los dos puntos extremos.
Si no hay curva IDF, una lluvia uniforme con la intensidad de diseño durante el tiempo de concentración (mínimo 10 min).
"""
import math


def curva(ll, Rh=None):
    """[(D min, I mm/h)] de la estación calculada (periodo de diseño) o de la pestaña LLUVIA."""
    if Rh and Rh.get("idf") and Rh.get("T") in Rh["idf"]:
        return sorted((float(d), float(i)) for d, i in Rh["idf"][Rh["T"]].items())
    return sorted((float(d), float(i)) for d, i in (ll.get("idf") or []) if float(d) > 0 and float(i) > 0)


def intensidad(c, D):
    if len(c) == 1: return c[0][1]
    lx = math.log(D)
    for (d0, i0), (d1, i1) in zip(c[:-1], c[1:]):
        if d0 <= D <= d1: break
    else: (d0, i0), (d1, i1) = (c[0], c[1]) if D < c[0][0] else (c[-2], c[-1])
    k = (lx - math.log(d0)) / (math.log(d1) - math.log(d0))
    return math.exp(math.log(i0) + k * (math.log(i1) - math.log(i0)))


def bloques_alternos(ll, Rh=None, duracion=120, dt=5):
    """{"dt_min", "intensidades" (mm/h por bloque), "lamina_mm", "pico_mmh", "metodo"}."""
    c = curva(ll, Rh)
    if not c:
        I = float(ll.get("I_mmh") or 0); tc = max(10.0, float(ll.get("tc_min") or 10))
        n = int(math.ceil(tc / dt)); m = max(n, int(math.ceil(60 / dt)))
        bl = [I] * n + [0.0] * (m - n)
        return {"dt_min": dt, "intensidades": bl, "lamina_mm": round(I * n * dt / 60, 2), "pico_mmh": I,
                "metodo": "lluvia uniforme de %.2f mm/h durante %d min (sin curva IDF)" % (I, n * dt)}
    n = int(duracion // dt)
    P = [intensidad(c, k * dt) * k * dt / 60.0 for k in range(1, n + 1)]
    inc = sorted([P[0]] + [b - a for a, b in zip(P[:-1], P[1:])], reverse=True)
    orden = [0] * n; centro = (n - 1) // 2
    for k, v in enumerate(inc):
        pos = centro + ((k + 1) // 2 if k % 2 else -(k // 2))
        orden[min(max(pos, 0), n - 1)] = v
    bl = [v * 60.0 / dt for v in orden]
    return {"dt_min": dt, "intensidades": [round(v, 3) for v in bl], "lamina_mm": round(sum(orden), 2), "pico_mmh": round(max(bl), 2),
            "metodo": "bloques alternos de %d min, tormenta de %d min, curva IDF %s" % (dt, duracion, "de la estación" if Rh else "de la pestaña LLUVIA")}
