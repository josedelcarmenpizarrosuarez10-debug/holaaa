"""Ordenes del motor para el programa de escritorio DrenIE (pagina Red de cunetas).

DrenIE (Tauri) llama al motor empaquetado como programa auxiliar con una orden y, si hace falta, un JSON por la entrada estandar;
el motor responde un JSON por la salida estandar. Ordenes (ademas de leer, disenar y aplicar):
    capas DXF                  capas del plano con lo que el programa propone para cerco, techos, curvas, veredas, muros y ejes
    crear                      (JSON por stdin) crea la carpeta del proyecto y su proyecto.json; devuelve la ruta
    vista proyecto.json        escena, resultado (observaciones) y ediciones del proyecto, para el visor
    ediciones proyecto.json    (JSON por stdin) guarda lo editado en el visor (ediciones.json)
    datos proyecto.json        (JSON por stdin) actualiza datos que vienen de DrenIE (la lluvia de la pestana LLUVIA)
    entregables proyecto.json  lista de entregables del ultimo calculo
    normas                     biblioteca de normas y fuentes (cada dato con su norma, articulo o tabla y su estado)
    para_drenie proyecto.json  la red calculada en el formato de DrenIE (perfiles de CUNETAS, modulos de MONTANTES y partidas
                               de METRADO) para pasarla a sus pestanas
    abrir proyecto.json [ARCH] abre la carpeta de salida o un entregable con el programa del sistema
Ningun error cierra el programa: __main__ devuelve {"error": mensaje en espanol}.
"""
import hashlib
import io
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
    if not c.get("cerco"): raise ValueError("Elija la capa del cerco perimétrico (límite de intervención).")
    if not c.get("curvas") and not d.get("landxml"): raise ValueError("Elija la capa de las curvas de nivel o un archivo LandXML del terreno.")
    try: npt = float(str(d.get("npt")).replace(",", "."))
    except (TypeError, ValueError): raise ValueError("Escriba el NPT (nivel de piso terminado) en metros.")
    lluvia = _lluvia(d.get("lluvia") if d.get("lluvia") is not None else {"I_mmh": d.get("I_mmh")})
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
           "lluvia": lluvia, "superficies_cfg": {"por_defecto": d.get("por_defecto") or "verde"},
           "planteamiento": d.get("planteamiento") or "completar"}
    if d.get("landxml"): cfg["terreno"] = {"landxml": os.path.abspath(d["landxml"]), "equidistancia": 0.25}
    ruta = os.path.join(carpeta, "proyecto.json")
    json.dump(cfg, open(ruta, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return {"accion": "crear", "proyecto": ruta}


def _lluvia(ll):
    """Lluvia de diseno que manda DrenIE: I (mm/h) para el tiempo de concentracion de diseno, con la curva IDF y su fuente."""
    if not isinstance(ll, dict): raise ValueError("Lluvia de diseño inválida.")
    try: imm = float(str(ll.get("I_mmh")).replace(",", "."))
    except (TypeError, ValueError): imm = 0.0
    if not 0 < imm < 1000:
        raise ValueError("Falta la lluvia de diseño: complete la curva IDF en la pestaña LLUVIA de DrenIE.")
    out = {"I_mmh": round(imm, 2)}
    if ll.get("tc_min") not in (None, ""): out["tc_min"] = float(ll["tc_min"])
    idf = [[float(a), float(b)] for a, b in (ll.get("idf") or []) if float(a) > 0 and float(b) > 0]
    if idf: out["idf"] = sorted(idf)
    for k in ("fuente", "metodo_tc", "ejemplo"):
        if ll.get(k) not in (None, ""): out[k] = ll[k]
    return out


def datos(ruta, d):
    """Datos que manda DrenIE antes de cada calculo (hoy, la lluvia de la pestana LLUVIA); no toca nada mas del proyecto."""
    cfg, base, sal = _cargar(ruta)
    if not isinstance(d, dict): raise ValueError("Datos inválidos.")
    cambios = []
    if "lluvia" in d:
        nueva = _lluvia(d["lluvia"])
        if nueva != cfg.get("lluvia"): cfg["lluvia"] = nueva; cambios.append("lluvia")
    if cambios: json.dump(cfg, open(ruta, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return {"accion": "datos", "cambios": cambios}


COLOR_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _ubic_limpia(u):
    """Lo que el editor de Ubicación puede guardar en el proyecto (cfg["ubicacion"]), revisado."""
    from . import ubicacion as UBI
    if not isinstance(u, dict): raise ValueError("Datos de ubicación inválidos.")
    o = {}
    if u.get("zona_utm") not in (None, "", 0):
        z = int(u["zona_utm"])
        if z not in (17, 18, 19): raise ValueError("La zona UTM del Perú es 17, 18 o 19.")
        o["zona_utm"] = z
    if u.get("ubigeo"):
        ub = str(u["ubigeo"]).strip()
        if ub not in UBI.limites()["por_u"] or len(ub) != 6: raise ValueError("Ubigeo %s no encontrado en los límites del INEI." % ub)
        o["ubigeo"] = ub
    if isinstance(u.get("nombres"), dict):
        o["nombres"] = {str(k): str(v).strip()[:80] for k, v in u["nombres"].items() if str(v).strip()}
    if isinstance(u.get("titulos"), list):
        t = [str(x or "").strip()[:150] for x in u["titulos"][:4]]
        if any(t): o["titulos"] = t
    if isinstance(u.get("colores"), dict):
        o["colores"] = {k: v for k, v in u["colores"].items() if k in ("resaltado", "recuadro", "cerco") and isinstance(v, str) and COLOR_HEX.match(v)}
    f = u.get("foto")
    if isinstance(f, dict) and f.get("ruta"):
        if not os.path.exists(f["ruta"]): raise FileNotFoundError("No se encuentra la foto: %s" % f["ruta"])
        o["foto"] = {"ruta": f["ruta"], "fuente": str(f.get("fuente") or "").strip()[:120]}
        for k in ("xmin", "ymin", "xmax", "ymax"): o["foto"][k] = float(f[k])
        if o["foto"]["xmax"] <= o["foto"]["xmin"] or o["foto"]["ymax"] <= o["foto"]["ymin"]:
            raise ValueError("Las esquinas de la foto están invertidas: la esquina superior derecha debe tener mayor Este y mayor Norte.")
    if "osm" in u: o["osm"] = bool(u["osm"])
    if u.get("codigo_lamina"): o["codigo_lamina"] = str(u["codigo_lamina"]).strip()[:12]
    return o


def ubicacion(ruta, d):
    """Editor de Ubicación del visor. d: {"buscar": texto} lista distritos; {"guardar": {...}} guarda en el proyecto;
    {"generar": true} (o junto con guardar) rehace los 4 mapas con lo guardado y los devuelve como imágenes de vista previa."""
    from . import ubicacion as UBI
    import base64
    cfg, base, sal = _cargar(ruta)
    d = d if isinstance(d, dict) else {}
    if d.get("buscar") is not None:
        return {"accion": "ubicacion", "distritos": UBI.buscar(d["buscar"])}
    guardado = False
    if "guardar" in d:
        nueva = _ubic_limpia(d["guardar"])
        if nueva != (cfg.get("ubicacion") or {}):
            if nueva: cfg["ubicacion"] = nueva
            else: cfg.pop("ubicacion", None)
            json.dump(cfg, open(ruta, "w", encoding="utf-8"), indent=1, ensure_ascii=False); guardado = True
    cerco, techos = UBI.leer_sitio(sal)
    if cerco is None: raise ValueError("Primero lea el plano del proyecto (el visor lo hace al abrirlo) para ubicar el cerco.")
    U = UBI.generar(sal, cerco, techos, cfg) if (d.get("generar", True)) else UBI.ubicar(cerco, cfg.get("ubicacion"), "")
    imgs = []
    for r in U.get("mapas") or []:
        from PIL import Image
        im = Image.open(r).convert("RGB"); im.thumbnail((640, 640))
        b = io.BytesIO(); im.save(b, "JPEG", quality=82)
        imgs.append("data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode())
    return {"accion": "ubicacion", "guardado": guardado, "config": cfg.get("ubicacion") or {}, "ubicacion": UBI.resumen(U), "imagenes": imgs}


def pisco(d):
    """Serie de máximas en 24 h por mes de PISCOp v3.0 (SENAMHI) para la pestaña LLUVIA. d: {ubigeo} o {lat, lon}, y factor opcional."""
    from . import lluvia_pisco
    d = d if isinstance(d, dict) else {}
    return lluvia_pisco.serie(d.get("lat"), d.get("lon"), d.get("ubigeo"), d.get("factor"))


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
    if not isinstance(ed, dict): raise ValueError("Ediciones inválidas.")
    json.dump(ed, open(os.path.join(base, "ediciones.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return {"accion": "ediciones", "guardado": True}


def normas_fuentes():
    from . import normas
    return dict(normas.para_drenie(), accion="normas")


def para_drenie(ruta):
    """Red calculada -> DrenIE. Cada eje es un perfil de cuneta (tramos partidos en las estructuras de caida, los tramos tapados y
    los vehiculares, con la misma cota de fondo de la red), conectado a la cuneta que lo recibe o a su descarga; cada techo es un
    modulo con sus montantes; las estructuras de caida van como partidas adicionales del metrado."""
    cfg, base, sal = _cargar(ruta)
    rr = os.path.join(sal, "resultado.json")
    if not os.path.exists(rr): raise FileNotFoundError("Primero calcule la red (Calcular todo).")
    R = json.load(open(rr, encoding="utf-8")); P = R["parametros"]; C = R["red"]
    fila = {(f["eje"], f["de"], f["a"]): f for f in R["verificacion"]["hidraulica"]}
    N = C["nudos"]; x0 = min(v[0] for v in N.values()); y0 = min(v[1] for v in N.values())
    pid = lambda cod: "pf-red-" + cod
    prog = {}
    for r in C["ramales"]:
        s = 0.0; prog[r["codigo"]] = {r["nudos"][0]: 0.0}
        for t in r["tramos"]: s += t["L"]; prog[r["codigo"]][t["a"]] = round(s, 2)

    def interp(perfil, x, k):
        if x <= perfil[0][0]: return perfil[0][k]
        for a, b in zip(perfil[:-1], perfil[1:]):
            if a[0] <= x <= b[0]: return a[k] + (b[k] - a[k]) * ((x - a[0]) / (b[0] - a[0]) if b[0] > a[0] else 0)
        return perfil[-1][k]
    # caudal propio de cada eje como aportes por progresiva: lo que crece el caudal de un tramo al siguiente menos lo que entra
    # por otros ejes (DrenIE suma por su cuenta los ejes conectados, así el caudal no se cuenta dos veces)
    q_fin = {r["codigo"]: (fila.get((r["codigo"], r["tramos"][-1]["de"], r["tramos"][-1]["a"])) or {}).get("Q_ls", 0.0) for r in C["ramales"] if r["tramos"]}
    llega = {}
    for r in C["ramales"]:
        fin = r["nudos"][-1]
        for q in C["ramales"]:
            if q["codigo"] != r["codigo"] and fin in q["nudos"][1:-1]: llega.setdefault((q["codigo"], fin), []).append(r["codigo"])
    perfiles = []
    for r in C["ramales"]:
        pf = r["perfil"]; L = r["L"]; cod = r["codigo"]
        aportes = []; q_ant = 0.0
        for t in r["tramos"]:
            q = (fila.get((cod, t["de"], t["a"])) or {}).get("Q_ls", q_ant)
            dq = q - q_ant - sum(q_fin.get(h, 0.0) for h in llega.get((cod, t["de"]), []))
            if dq > 0.0005: aportes.append({"id": "ap-red-%s-%d" % (cod, len(aportes)), "tipo": "caudal", "x": prog[cod][t["de"]], "q": round(dq, 3)})
            q_ant = q
        cortes = {0.0, round(L, 2)}
        lim = []; s = 0.0
        for t in r["tramos"]: lim.append((s, s + t["L"], t)); s += t["L"]; cortes.add(round(s, 2))
        caidas = {}
        for c in r.get("cambios_nivel", []):
            if c["sentido"] == "baja" and c["caida_fondo"] > 0.05:
                cortes.add(round(c["s"], 2)); caidas[round(c["s"], 2)] = c
        for a, b in r.get("tapados", []) + r.get("vehiculares", []): cortes.update((round(a, 2), round(b, 2)))
        cortes = sorted(x for x in cortes if 0 <= x <= L + 1e-6)
        tramos = []; cf_prev = interp(pf, 0, 2)
        for a, b in zip(cortes[:-1], cortes[1:]):
            if b - a < 0.05: continue
            m = (a + b) / 2
            t = next((q for q in lim if q[0] - 1e-6 <= m <= q[1] + 1e-6), lim[-1])[2]
            f = fila.get((cod, t["de"], t["a"])) or {}
            veh = any(x <= m <= y for x, y in r.get("vehiculares", [])); tap = any(x <= m <= y for x, y in r.get("tapados", []))
            drop = 0.0; cf0 = cf_prev
            if round(a, 2) in caidas: c = caidas[round(a, 2)]; drop = round(max(0.0, c["cf_arriba"] - c["cf_abajo"]), 3); cf0 = cf_prev - drop
            c_fin = caidas.get(round(b, 2))
            cf1 = c_fin["cf_arriba"] if c_fin else interp(pf, b, 2)
            S = max(0.0, (cf0 - cf1) / (b - a)) * 100
            tr = {"id": "t-red-%s-%d" % (cod, len(tramos)), "L": round(b - a, 2), "S": round(S, 3), "b": f.get("b", P["b_int"]),
                  "EM": P["e_muro"], "EL": P["e_fondo"], "tipo": "cajon" if (tap or veh) else "abierta"}
            if tap or veh: tr["uso"] = "vehicular" if veh else "peatonal"; tr["ET"] = P.get("e_tapa_veh", P["e_tapa"]) if veh else P["e_tapa"]
            if drop: tr["drop"] = drop
            u = tramos[-1] if tramos else None
            if u and not drop and all(u.get(k) == tr.get(k) for k in ("tipo", "uso", "b", "ET")) and abs(u["S"] - tr["S"]) < (0.15 if min(u["L"], tr["L"]) < 2.0 else 0.05):
                Lm = u["L"] + tr["L"]; u["S"] = round(max(0.0, (u["_cf0"] - cf1) / Lm) * 100, 3); u["L"] = round(Lm, 2)    # misma sección y pendiente: un tramo
            else: tr["_cf0"] = cf0; tramos.append(tr)
            cf_prev = cf1
        for tr in tramos: tr.pop("_cf0", None)
        fin = r["nudos"][-1]
        rec = next((q for q in C["ramales"] if q["codigo"] != cod and fin in q["nudos"][1:-1]), None)
        outlet = {"type": "channel", "targetId": pid(rec["codigo"]), "at": prog[rec["codigo"]].get(fin, 0.0)} if rec else {"type": "external"}
        hmax = max(p[1] - p[2] for p in pf)
        perfiles.append({"id": pid(cod), "name": "%s · red de cunetas" % cod, "origen": "red", "redEje": cod, "sectorId": "", "qManual": "", "qInicio": 0,
            "aportes": aportes, "nct": "%.3f" % pf[0][1], "ncf0": "%.3f" % pf[0][2],
            "nctPts": [{"x": round(q[0], 2), "z": round(q[1], 3)} for q in pf[::4]] + [{"x": round(pf[-1][0], 2), "z": round(pf[-1][1], 3)}],
            "sFija": False, "hMax": round(max(1.0, hmax + 0.10), 2), "hArm": P["h_acero"], "tramos": tramos,
            "routing": {"buildings": [], "outlet": outlet},
            "plan": {"points": [{"x": round(N[n][0] - x0, 3), "y": round(N[n][1] - y0, 3)} for n in r["nudos"]]}})
    modulos = {}
    for l in R["techos"]["lados"]:
        m = modulos.setdefault(l["techo"], {"id": "sec-red-" + l["techo"], "name": "%s · red de cunetas" % l["techo"], "origen": "red", "area": 0.0,
                                            "runoffC": P["C"]["techo"], "roofType": "one", "downspoutsPerSide": 1, "lados": 0})
        m["area"] = round(m["area"] + l["A_m2"], 2); m["lados"] += 1; m["downspoutsPerSide"] = max(m["downspoutsPerSide"], l["montantes"])
        if m["lados"] >= 2: m["roofType"] = "two"
    adicionales = []
    for e in R.get("estructuras", {}).get("estructuras", []):
        if not e.get("codigo"): continue
        mt = e["metrado"]
        for k, nom, und in (("concreto_m3", "CONCRETO f'c=210 kg/cm2 EN ESTRUCTURA", "m³"), ("encofrado_m2", "ENCOFRADO Y DESENCOFRADO EN ESTRUCTURA", "m²"),
                            ("acero_kg", "ACERO f'y=4200 kg/cm2 EN ESTRUCTURA", "kg")):
            adicionales.append({"id": "mm-red-%s-%s" % (e["codigo"], k), "code": "RED.%s" % e["codigo"], "name": "%s %s (%s, %s prog. %.2f)" % (
                nom, e["codigo"], e["descripcion"].split(" (")[0].lower(), e["eje"], e["progresiva"]), "unit": und, "qty": str(mt[k]), "origen": "red"})
        if e["tipo"] == "muro":
            adicionales.append({"id": "mm-red-%s-marco" % e["codigo"], "code": "RED.%s" % e["codigo"], "name": "MARCO DE CONCRETO ARMADO PARA PASE EN MURO "
                                "DE CONTENCION %s (%.2f x %.2f m)" % (e["codigo"], e["marco_ancho"], e["marco_alto"]), "unit": "und", "qty": "1", "origen": "red"})
    tm = R["techos"]["metrado"]
    for k, nom, und in (("tuberia_enterrada_m", "TUBERIA PVC Ø4\" ENTERRADA DADO - CUNETA (red)", "m"), ("dados_und", "DADO DE CONCRETO DE MONTANTE (red)", "und"),
                        ("codo_dado_und", "CODO PVC Ø4\" x 90° EN DADO (red)", "und"), ("falsas_columnas_und", "FALSA COLUMNA 0.20 x 0.15 x 1.30 (red)", "und")):
        if tm.get(k): adicionales.append({"id": "mm-red-%s" % k, "code": "RED.MON", "name": nom, "unit": und, "qty": str(tm[k]), "origen": "red"})
    return {"accion": "para_drenie", "perfiles": perfiles, "modulos": list(modulos.values()), "metrado_adicional": adicionales,
            "resumen": {"ejes": len(perfiles), "modulos": len(modulos), "partidas": len(adicionales)}}


def entregables(ruta):
    cfg, base, sal = _cargar(ruta)
    ext = (".docx", ".xlsx", ".dxf", ".png", ".inp")
    arch = sorted(f for f in os.listdir(sal) if f.lower().endswith(ext) and not f.startswith("_")) if os.path.isdir(sal) else []
    return {"accion": "entregables", "carpeta": sal, "archivos": arch}


def abrir(ruta, nombre=None):
    cfg, base, sal = _cargar(ruta)
    if nombre and (os.path.basename(nombre) != nombre or nombre.startswith(".")): raise ValueError("Nombre de archivo inválido.")
    r = os.path.join(sal, nombre) if nombre else sal
    if not os.path.exists(r): raise FileNotFoundError("No existe %s" % r)
    if sys.platform.startswith("win"): os.startfile(r)                       # noqa: Windows
    elif sys.platform == "darwin": subprocess.Popen(["open", r])
    else: subprocess.Popen(["xdg-open", r], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"accion": "abrir", "abierto": r}


def vial(d, carpeta=None):
    """Drenaje vial (Manual de Hidrología, Hidráulica y Drenaje del MTC): cunetas, alcantarillas de alivio y de paso, badenes.
    Con CARPETA escribe ahí la memoria de cálculo en Excel y el resultado en JSON. {"plantilla": ruta} lee los datos de la
    plantilla Excel (la lluvia de DrenIE, si viene, manda); {"crear_plantilla": true} solo escribe la plantilla en CARPETA."""
    from . import vial as V, vial_excel, vial_plantilla
    if d.get("crear_plantilla"):
        if not carpeta: raise ValueError("Indique la carpeta donde guardar la plantilla.")
        os.makedirs(carpeta, exist_ok=True)
        return {"accion": "vial", "archivos": [vial_plantilla.crear(os.path.join(carpeta, "DATOS_DRENAJE_VIAL.xlsx"), d.get("datos"))]}
    if d.get("plantilla"):
        x = vial_plantilla.leer(d["plantilla"])
        if d.get("lluvia"): x["lluvia"] = d["lluvia"]
        if d.get("proyecto"): x["proyecto"] = {**x["proyecto"], **d["proyecto"]}
        d = x
    R = V.calcular(d, carpeta or ".")
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
        R["archivos"] = [vial_excel.libro(os.path.join(carpeta, "MEMORIA_CALCULO_DRENAJE_VIAL.xlsx"), R)]
        ruta = os.path.join(carpeta, "resultado_vial.json")
        json.dump(R, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str); R["archivos"].append(ruta)
    return R

