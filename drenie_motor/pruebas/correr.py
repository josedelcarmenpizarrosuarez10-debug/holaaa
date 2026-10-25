"""Bateria de pruebas de DrenIE: corre el diseno de los proyectos reales de ejemplo y de los terrenos inventados
(pruebas/sitios/) y resume cada uno:
- CAIDA: el programa se cerro con un error interno o paso el tiempo limite (no debe pasar nunca).
- DATOS: el programa explico en espanol que faltan o estan mal los datos (aceptable si el mensaje es claro).
- PROYECTISTA: diseno completo y revisado; lo que no pudo resolver solo queda marcado como decision del proyectista.
- BIEN: diseno completo, revision general sin fallas.
Ningun cambio del motor se entrega si hay una CAIDA o si un proyecto real deja de estar BIEN.

Uso: python3 pruebas/correr.py [--solo-sitios | --solo-ejemplos] [--hilos 4]
"""
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
EJEMPLOS = ["car_varones", "car_varones_auto", "barranquita_real", "barranquita"]


def correr(ruta, limite=1500):
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, "-m", "drenie_motor", "disenar", ruta], cwd=RAIZ, capture_output=True, text=True, timeout=limite)
    except subprocess.TimeoutExpired:
        return {"proyecto": ruta, "estado": "CAIDA", "detalle": "paso el tiempo limite de %d s" % limite, "segundos": limite}
    seg = round(time.time() - t0, 1)
    if p.returncode != 0:
        try: msg = json.loads(p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "{}")
        except Exception: msg = {}
        if p.returncode == 2: return {"proyecto": ruta, "estado": "DATOS", "detalle": msg.get("error", ""), "segundos": seg}
        cola = (p.stderr or "").strip().splitlines()[-3:]
        return {"proyecto": ruta, "estado": "CAIDA", "detalle": msg.get("error") or " | ".join(cola), "registro": msg.get("registro"), "segundos": seg}
    cfg = json.load(open(ruta, encoding="utf-8"))
    R = json.load(open(os.path.join(os.path.dirname(ruta), cfg.get("salida", "salida"), "resultado.json"), encoding="utf-8"))
    rv = R.get("revision", {}); fallas = rv.get("fallas", []); dec = rv.get("decisiones", [])
    r = R["resumen"]
    estado = "FALLA" if fallas else ("PROYECTISTA" if dec else "BIEN")
    return {"proyecto": ruta, "estado": estado, "segundos": seg, "fallas": fallas, "decisiones": dec,
            "resumen": {k: r.get(k) for k in ("ejes", "descargas", "longitud_m", "uniones_nuevas_m", "profundidad_max_m", "cumple", "comprobaciones", "sin_salida_m")},
            "revision": "%s/%s" % (rv.get("comprobaciones", 0) - rv.get("no_cumple", 0), rv.get("comprobaciones", 0)),
            "observaciones": len(R.get("observaciones", [])), "visor": bool((R.get("archivos") or {}).get("visor"))}


def main():
    hilos = int(sys.argv[sys.argv.index("--hilos") + 1]) if "--hilos" in sys.argv else 4
    rutas = []
    if "--solo-sitios" not in sys.argv:
        rutas += [os.path.join(RAIZ, "ejemplos", e, "proyecto.json") for e in EJEMPLOS]
    if "--solo-ejemplos" not in sys.argv:
        sd = os.path.join(AQUI, "sitios")
        rutas += sorted(os.path.join(sd, d, "proyecto.json") for d in os.listdir(sd)) if os.path.isdir(sd) else []
    out = []
    with cf.ThreadPoolExecutor(hilos) as ex:
        for res in ex.map(correr, rutas):
            out.append(res)
            print("%-12s %-55s %6.0f s  %s" % (res["estado"], os.path.relpath(res["proyecto"], RAIZ), res["segundos"],
                                             res.get("revision", "") + (" obs %d%s" % (res["observaciones"], "" if res.get("visor") else " SIN VISOR") if "observaciones" in res else "") + " " + "; ".join(x[:150] for x in (res.get("fallas") or res.get("decisiones") or [res.get("detalle", "")])[:3])), flush=True)
    json.dump(out, open(os.path.join(AQUI, "RESULTADO_PRUEBAS.json"), "w"), indent=1, ensure_ascii=False)
    cuenta = {}
    for r in out: cuenta[r["estado"]] = cuenta.get(r["estado"], 0) + 1
    print("RESUMEN:", cuenta)
    return 1 if cuenta.get("CAIDA") or cuenta.get("FALLA") else 0


if __name__ == "__main__":
    sys.exit(main())
