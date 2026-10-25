"""Ordenes del motor para el programa de escritorio DrenIE (pagina Red de cunetas).

DrenIE (Tauri) llama al motor empaquetado como programa auxiliar con una orden y, si hace falta, un JSON por la entrada estandar;
el motor responde un JSON por la salida estandar. Ordenes (ademas de leer, disenar y aplicar):
    capas DXF                  capas del plano con lo que el programa propone para cerco, techos, curvas, veredas, muros y ejes
    crear                      (JSON por stdin) crea la carpeta del proyecto y su proyecto.json; devuelve la ruta
    vista proyecto.json        escena, resultado (observaciones) y ediciones del proyecto, para el visor
    ediciones proyecto.json    (JSON por stdin) guarda lo editado en el visor (ediciones.json)
    entregables proyecto.json  lista de entregables del ultimo calculo
    abrir proyecto.json [ARCH] abre la carpeta de salida o un entregable con el programa del sistema
Ningun error cierra el programa: __main__ devuelve {"error": mensaje en espanol}.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

from . import lector_dxf

PISTAS = {"cerco": ("CERCO", "LIMITE", "PERIMETR", "LINDERO"), "techos": ("TECHO", "PROYECC", "COBERT", "CUBIERTA"),
          "curvas": ("CURVA", "TOPO", "NIVEL"), "veredas": ("VEREDA", "PISO", "PAVIM"), "muros": ("MURO", "WALL"), "ejes": ("CUNETA",)}


def _cache_dir():
    d = os.path.join(os.environ.get("LOCALAPPDATA") or tempfile.gettempdir(), "DrenIE", "motor")
    os.makedirs(d, exist_ok=True)
    return d


def capas(dxf):
    if not dxf or not os.path.exists(dxf): raise FileNotFoundError("No se encuentra el plano: %s" % dxf)
    cache = os.path.join(_cache_dir(), "plano_%s.pkl" % hashlib.sha1(os.path.abspath(dxf).encode()).hexdigest()[:12])
    B = lector_dxf.base(dxf, cache=cache)
    lista = lector_dxf.capas_disponibles(B)
    for c in lista:
        c["con_cota"] = sum(1 for e in B["geo"].get(c["capa"], []) if e[3] not in (None, 0, 0.0))
        c["colores"] = {str(k): v for k, v in c["colores"].items()}
    sug = {}
    for k, claves in PISTAS.items():
        cand = [c for c in lista if any(x in c["capa"].upper() for x in claves)]
        if k == "curvas": cand.sort(key=lambda c: -c["con_cota"])
        elif k in ("cerco", "techos"): cand.sort(key=lambda c: -c["cerradas"])
        else: cand.sort(key=lambda c: -c["entidades"])
        if cand: sug[k] = cand[0]["capa"]
    return {"accion": "capas", "dxf": os.path.abspath(dxf), "capas": lista, "sugeridas": sug}


def crear(d):
    """d: {nombre, codigo, entidad, ubicacion, dxf, carpeta, capas{cerco, techos, curvas, veredas, muros, ejes}, landxml, npt,
    area_verde, I_mmh, planteamiento, por_defecto}."""
    nombre = (d.get("nombre") or "").strip() or "Proyecto DrenIE"
    carpeta = d.get("carpeta") or os.path.join(os.path.expanduser("~"), "Documents", "DrenIE",
                                                re.sub(r"[^\w\- ]", "", nombre)[:60].strip() or "Proyecto")
    dxf = d.get("dxf")
    if not dxf or not os.path.exists(dxf): raise FileNotFoundError("Elija el plano DXF del proyecto.")
    c = d.get("capas") or {}
    if not c.get("cerco"): raise ValueError("Elija la capa del cerco perimetrico (limite de intervencion).")
    if not c.get("curvas") and not d.get("landxml"): raise ValueError("Elija la capa de las curvas de nivel o un archivo LandXML del terreno.")
    try: npt = float(str(d.get("npt")).replace(",", "."))
    except (TypeError, ValueError): raise ValueError("Escriba el NPT (nivel de piso terminado) en metros.")
    try: imm = float(str(d.get("I_mmh")).replace(",", "."))
    except (TypeError, ValueError): imm = 0.0
    if not imm > 0: raise ValueError("Escriba la intensidad de lluvia de diseno en mm/h.")
    os.makedirs(carpeta, exist_ok=True)
    capas_cfg = {"cerco": {"capa": c["cerco"]}}
    for k in ("techos", "veredas", "muros", "ejes"):
        if c.get(k): capas_cfg[k] = c[k]
    if c.get("curvas"):
        capas_cfg["curvas"] = {"capa": c["curvas"]}; capas_cfg["equidistancia"] = float(d.get("equidistancia") or 0.5)
    verde = d.get("area_verde")
    cfg = {"proyecto": {"nombre": nombre.upper(), "nombre_corto": nombre, "codigo": d.get("codigo", ""), "entidad": d.get("entidad", ""),
                        "ubicacion": d.get("ubicacion", ""), "fecha": time.strftime("%d/%m/%Y")},
           "dxf": os.path.abspath(dxf), "salida": "salida", "capas": capas_cfg,
           "niveles": {"modo": "nivelado", "npt": npt, "borde_cuneta": npt,
                       "area_verde": round(float(str(verde).replace(",", ".")) if verde not in (None, "") else npt - 0.05, 3)},
           "lluvia": {"I_mmh": imm}, "superficies_cfg": {"por_defecto": d.get("por_defecto") or "verde"},
           "planteamiento": d.get("planteamiento") or "completar"}
    if d.get("landxml"): cfg["terreno"] = {"landxml": os.path.abspath(d["landxml"]), "equidistancia": 0.25}
    ruta = os.path.join(carpeta, "proyecto.json")
    json.dump(cfg, open(ruta, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return {"accion": "crear", "proyecto": ruta}


def _cargar(ruta):
    if not ruta or not os.path.exists(ruta): raise FileNotFoundError("No se encuentra el proyecto: %s" % ruta)
    cfg = json.load(open(ruta, encoding="utf-8"))
    return cfg, os.path.dirname(os.path.abspath(ruta)), os.path.join(os.path.dirname(os.path.abspath(ruta)), cfg.get("salida", "salida"))


def vista(ruta):
    cfg, base, sal = _cargar(ruta)
    lee = lambda r: json.load(open(r, encoding="utf-8")) if os.path.exists(r) else None
    R = lee(os.path.join(sal, "resultado.json"))
    p = cfg.get("proyecto") or {}
    return {"accion": "vista", "proyecto": os.path.abspath(ruta), "nombre": p.get("nombre_corto") or p.get("nombre") or os.path.basename(base),
            "escena": lee(os.path.join(sal, "escena.json")), "ediciones": lee(os.path.join(base, "ediciones.json")),
            "resultado": {"observaciones": R.get("observaciones", []), "resumen": R.get("resumen", {}), "avisos": R.get("avisos", []),
                          "revision": {k: (R.get("revision") or {}).get(k) for k in ("comprobaciones", "no_cumple", "decisiones_proyectista")}} if R else None}


def ediciones(ruta, ed):
    cfg, base, sal = _cargar(ruta)
    if not isinstance(ed, dict): raise ValueError("Ediciones invalidas.")
    json.dump(ed, open(os.path.join(base, "ediciones.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return {"accion": "ediciones", "guardado": True}


def entregables(ruta):
    cfg, base, sal = _cargar(ruta)
    ext = (".docx", ".xlsx", ".dxf", ".png")
    arch = sorted(f for f in os.listdir(sal) if f.lower().endswith(ext) and not f.startswith("_")) if os.path.isdir(sal) else []
    return {"accion": "entregables", "carpeta": sal, "archivos": arch}


def abrir(ruta, nombre=None):
    cfg, base, sal = _cargar(ruta)
    if nombre and (os.path.basename(nombre) != nombre or nombre.startswith(".")): raise ValueError("Nombre de archivo invalido.")
    r = os.path.join(sal, nombre) if nombre else sal
    if not os.path.exists(r): raise FileNotFoundError("No existe %s" % r)
    if sys.platform.startswith("win"): os.startfile(r)                       # noqa: Windows
    elif sys.platform == "darwin": subprocess.Popen(["open", r])
    else: subprocess.Popen(["xdg-open", r], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"accion": "abrir", "abierto": r}
