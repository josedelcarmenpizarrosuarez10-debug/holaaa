"""Orquestador del modulo Terreno y red de cunetas en planta.

Dos acciones, pensadas para que DrenIE las llame en orden:
- leer: abre el DXF, lista las capas, arma el terreno, toma el cerco y genera la imagen de control (para que el usuario
  confirme el cerco y las capas antes de disenar).
- disenar: arma la red (uniones y descargas), calcula cotas de fondo, verifica (11 comprobaciones) en ciclo con la capacidad
  y entrega resultado.json, la planta en DXF y la vista previa PNG.
"""
import json
import os
import time

from . import lector_dxf, terreno, sitio as sitio_mod, red as red_mod, cotas, verificacion, salidas, geom, superficies, escena, hidrologia, lloraderos, dimensionamiento
from .parametros import combinar

VERSION = "0.1.0"


def _ruta(base, r):
    return r if os.path.isabs(r) else os.path.normpath(os.path.join(base, r))


def _cargar(cfg_ruta):
    cfg = json.load(open(cfg_ruta, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(cfg_ruta))
    salida = _ruta(base, cfg.get("salida", "salida_drenie"))
    os.makedirs(salida, exist_ok=True)
    ed = _ruta(base, cfg.get("ediciones", "ediciones.json"))
    if os.path.exists(ed): _sumar_ediciones(cfg, json.load(open(ed, encoding="utf-8")))
    return cfg, base, salida


def _sumar_ediciones(cfg, ed):
    """Lo dibujado o marcado en el visor manda sobre lo leido del plano: asignaciones por clic, poligonos de superficie,
    flechas de caida, lineas de cuneta y descargas fijadas."""
    sc = cfg.setdefault("superficies_cfg", {})
    sc["asignaciones"] = list(sc.get("asignaciones", [])) + list(ed.get("asignaciones", []))
    cfg["superficies"] = list(cfg.get("superficies", [])) + list(ed.get("superficies", []))
    cfg["flechas_techo"] = list(cfg.get("flechas_techo", [])) + list(ed.get("flechas_techo", []))
    cfg["ejes_lineas"] = list(cfg.get("ejes_lineas", [])) + list(ed.get("ejes_lineas", []))
    if ed.get("descargas"): cfg["descargas"] = ed["descargas"]


def _preparar(cfg, base, salida):
    P = combinar(cfg.get("parametros"))
    dxf = _ruta(base, cfg["dxf"])
    capas = cfg["capas"]
    cv = capas.get("ventana_por_capa")
    if cv is None and isinstance(capas.get("curvas"), dict) and os.path.getsize(dxf) > 50e6: cv = capas["curvas"].get("capa")
    B = lector_dxf.base(dxf, cache=os.path.join(salida, "_base_sitio.pkl"), ventana=capas.get("ventana"), capa_ventana=cv)
    cur, rep_t = terreno.curvas(B, {"curvas": capas["curvas"], "curvas_texto": capas.get("curvas_texto"),
                                    "equidistancia": capas.get("equidistancia"), "z_min": capas.get("z_min", -500),
                                    "z_max": capas.get("z_max", 9000)})
    T = terreno.Terreno(cur)
    S = sitio_mod.Sitio(B, {"cerco": capas["cerco"], "techos": capas.get("techos"), "veredas": capas.get("veredas"),
                            "muros": capas.get("muros"), "niveles": cfg.get("niveles", {}),
                            "superficies": cfg.get("superficies", [])}, T, P)
    ejes = [e[0] for e in geom.seleccionar(B, capas["ejes"])] if capas.get("ejes") else []
    ejes += [[tuple(p) for p in l] for l in cfg.get("ejes_lineas", [])]        # lineas trazadas en el visor
    S.revisar_superficies(ejes)
    S.flechas = superficies.flechas_de(B, cfg)
    S.aguas, av = superficies.aguas_de_techos(S, cfg, S.flechas); S.avisos += av
    return P, B, cur, rep_t, T, S, ejes


def _mapa(B, S, cfg, P, segmentos):
    """Mapa de superficies (sin montajes ni huecos) con la franja real de las cunetas."""
    M = superficies.Mapa(B, S, cfg, P, segmentos)
    S.mapa = M
    return M


def leer(cfg_ruta):
    cfg, base, salida = _cargar(cfg_ruta)
    t0 = time.time()
    P, B, cur, rep_t, T, S, ejes = _preparar(cfg, base, salida)
    M = _mapa(B, S, cfg, P, [(a, b) for p in ejes for a, b in zip(p[:-1], p[1:])])
    png = salidas.png_planta(os.path.join(salida, "CONTROL_LECTURA.png"), None, None, S, cur, ejes,
                             "Lectura del plano: curvas, cerco (limite de intervencion) y lineas de cuneta del usuario - confirmar")
    esc = escena.escribir(os.path.join(salida, "escena.json"), B, S, M, ejes, cur, cfg.get("proyecto", {}), getattr(S, "aguas", []))
    out = {"accion": "leer", "version": VERSION, "escena": esc, "dxf": B["resumen"], "capas": lector_dxf.capas_disponibles(B), "terreno": rep_t,
           "cerco": {"area_m2": round(S.cerco.area, 1), "perimetro_m": round(S.cerco.length, 1),
                     "vertices": [[round(x, 3), round(y, 3)] for x, y in list(S.cerco.exterior.coords)[:-1]]},
           "mapa_superficies": M.cuadro(),
           "ejes_usuario": {"lineas": len(ejes), "longitud_m": round(sum(geom.dist(a, b) for p in ejes for a, b in zip(p[:-1], p[1:])), 1)},
           "avisos": S.avisos + M.avisos, "imagen_control": png, "segundos": round(time.time() - t0, 1),
           "requiere_confirmacion": ["cerco", "niveles", "capas"]}
    json.dump(out, open(os.path.join(salida, "lectura.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return out


def _lluvia_diseno(cfg, base):
    """Lluvia para el diseno: calculada desde la serie de la estacion si el proyecto la trae; si no, I_mmh o P24 dados."""
    ll = cfg.get("lluvia", {"I_mmh": 0})
    R = hidrologia.calcular(ll, base)
    if R is None: return ll, None
    return {"I_mmh": R["I"], "fuente": "%s, %s, T = %d anios, tc = %.0f min" % (R["estacion"].get("nombre", "estacion"), R["distribucion_nombre"],
                                                                              R["T"], R["tc_min"])}, R


def lluvia(cfg_ruta):
    """Lluvia de diseno sola: hidrologia.json, HIDROLOGIA.xlsx y CURVAS_IDF.png."""
    cfg, base, salida = _cargar(cfg_ruta)
    ll, R = _lluvia_diseno(cfg, base)
    if R is None: raise ValueError("El proyecto no trae datos de lluvia de una estacion (lluvia.archivo, lluvia.serie o lluvia.maximos)")
    res = hidrologia.resumen(R)
    xl = hidrologia.excel(R, os.path.join(salida, "HIDROLOGIA.xlsx")); png = hidrologia.png_idf(R, os.path.join(salida, "CURVAS_IDF.png"))
    out = {"accion": "lluvia", "version": VERSION, "resumen": res, "avisos": R["avisos"], "archivos": [xl, png]}
    json.dump(out, open(os.path.join(salida, "hidrologia.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return out


def disenar(cfg_ruta):
    cfg, base, salida = _cargar(cfg_ruta)
    t0 = time.time()
    P, B, cur, rep_t, T, S, ejes = _preparar(cfg, base, salida)
    if not ejes: raise ValueError("No hay lineas de cuneta del usuario (capas.ejes o ejes_lineas)")
    LL, _ = _lluvia_diseno(cfg, base)
    # ancho libre adoptado por el proyectista: hoja DIMENSIONAMIENTO llenada, o {"EJE-01": 0.45} en el proyecto
    adop = {}
    if cfg.get("dimensionamiento_adoptado"): adop.update(dimensionamiento.leer_adoptado(_ruta(base, cfg["dimensionamiento_adoptado"])))
    adop.update(cfg.get("secciones") or {})
    if adop: P["secciones"] = adop
    M0 = _mapa(B, S, cfg, P, [(a, b) for p in ejes for a, b in zip(p[:-1], p[1:])])
    if M0.sin_asignar:
        raise ValueError("Hay %d areas sin asignar (%.1f m2) en el mapa de superficies: asignar su tipo antes de disenar "
                         "(ver lectura.json, mapa_superficies.sin_asignar)." % (len(M0.sin_asignar), sum(c["geom"].area for c in M0.sin_asignar)))
    recorte = {}
    for intento in range(1, 6):
        R = red_mod.Red(S, T, P, ejes, cfg.get("descargas")).resolver(recorte)
        R.chaflanes(); R.nombrar()
        M = _mapa(B, S, cfg, P, [(R.Nf[a], R.Nf[b]) for r in R.ramales for a, b in zip(r["nudos"][:-1], r["nudos"][1:])
                                 if not (b in R.descargas)])
        hq, vueltas = {}, 0
        for vueltas in range(1, P["vueltas_max"] + 1):
            C = cotas.calcular(R, S, P, hq)
            V, hq2 = verificacion.verificar(C, R, S, T, P, LL, hq)
            if hq2 == hq: break
            hq = hq2
        # cuneta nunca enterrada: si una descarga no sale con las cotas reales, se reduce lo que puede recibir y se repite
        malas = [d for d in V["descargas"] if d["estado"] != "SALE POR GRAVEDAD"]
        if not malas or cfg.get("descargas"): break
        for d in malas:
            info = R.descargas[d["D"]]
            falta = info["z_req"] + P["desc_margen"] - d["cf"]
            recorte[info["k"]] = recorte.get(info["k"], 0.0) + max(falta, 0.01) / P["S0"] + 2.0
    anchos = {(f["eje"], f["de"], f["a"]): f["b"] for f in V["hidraulica"]}
    verde = M.por_tipo().get("verde")
    LLt, LLp = lloraderos.calcular(C, verde, P, anchos)
    secciones = {}
    for f in V["hidraulica"]:
        e = secciones.setdefault(f["eje"], {"sector": f["sector"], "eje": f["eje"], "L_m": 0.0, "b_pide": 0, "b": f["b"],
                                            "b_adoptado": (P.get("secciones") or {}).get(f["eje"], f["b"]), "ancho_total": f["ancho_total"],
                                            "h_min": 9, "h_max": 0, "excavacion_max": 0, "Q_max_ls": 0, "ancho_por": f["ancho_por"]})
        e["L_m"] = round(e["L_m"] + f["L"], 2); e["b_pide"] = max(e["b_pide"], f["b_pide"])
        e["h_min"] = round(min(e["h_min"], f["h_de"], f["h_a"]), 3); e["h_max"] = round(max(e["h_max"], f["h_de"], f["h_a"]), 3)
        e["excavacion_max"] = max(e["excavacion_max"], f["excavacion_max"]); e["Q_max_ls"] = max(e["Q_max_ls"], f["Q_ls"])
    secciones = dict(sorted(secciones.items(), key=lambda e: (e[1]["sector"], e[0])))
    xls = dimensionamiento.escribir(os.path.join(salida, "DIMENSIONAMIENTO.xlsx"), V["hidraulica"], list(secciones.values()), P)
    nuevas = sum(t["L"] for r in C["ramales"] for t in r["tramos"] if t["origen"] in ("union", "pase"))
    Ltot = sum(r["L"] for r in C["ramales"]); Ltap = sum(t["L_tapado"] for r in C["ramales"] for t in r["tramos"])
    resumen = {"ejes": len(C["ramales"]), "descargas": len(R.descargas), "longitud_m": round(Ltot, 2), "tapado_m": round(Ltap, 2),
               "rejilla_m": round(Ltot - Ltap, 2), "uniones_nuevas_m": round(nuevas, 2),
               "lineas_usuario_m": round(Ltot - nuevas, 2), "chaflanes": len(R.chaflanes_hechos),
               "profundidad_max_m": max(t["h_max"] for r in C["ramales"] for t in r["tramos"]),
               "cumple": sum(1 for c in V["comprobaciones"] if c["estado"] in ("CUMPLE", "CUMPLE CON GRADAS")),
               "comprobaciones": len(V["comprobaciones"]), "vueltas_ciclo": vueltas, "intentos_descargas": intento,
               "sin_salida_m": round(sum(geom.dist(a, b) for a, b in R.sin_cubrir), 1),
               "anchos_libres_m": sorted({f["b"] for f in V["hidraulica"]}), "lloraderos": lloraderos.resumen(LLt)}
    proyecto = cfg.get("proyecto", {})
    dxf = salidas.dxf_planta(os.path.join(salida, "PLANTA_RED_CUNETAS.dxf"), C, R, S, cur, P, proyecto, anchos, LLp)
    png = salidas.png_planta(os.path.join(salida, "PLANTA_RED_CUNETAS.png"), C, R, S, cur, ejes,
                             "%s - red de cunetas: %d ejes, %d descargas, %.1f m (%.1f m de uniones nuevas)" % (
                                 proyecto.get("nombre_corto", ""), resumen["ejes"], resumen["descargas"], Ltot, nuevas))
    out = {"accion": "disenar", "version": VERSION, "proyecto": proyecto, "resumen": resumen, "parametros": P,
           "mapa_superficies": M.cuadro(),
           "terreno": rep_t, "avisos": S.avisos + M.avisos + R.avisos + ([
               "%d mitades de techo (%d m2) no tienen cuneta bajo su alero: esa agua se mando a la cuneta mas cercana. Revisar si "
               "falta cuneta o si cae al terreno." % (len(V["hidrologia"]["aleros_sin_cuneta"]), sum(a["area_m2"] for a in V["hidrologia"]["aleros_sin_cuneta"]))]
               if V["hidrologia"]["aleros_sin_cuneta"] else []), "chaflanes": R.chaflanes_hechos, "red": C,
           "descargas_propuestas": [{"D": k, "x": round(v["q"][0], 3), "y": round(v["q"][1], 3), "L_max_m": v["L_max"],
                                     "terreno_exterior_min": round(v["z_req"], 2)} for k, v in R.descargas.items()],
           "sin_salida": [[list(a), list(b)] for a, b in R.sin_cubrir], "verificacion": V,
           "secciones_por_eje": list(secciones.values()), "lloraderos": {"resumen": lloraderos.resumen(LLt), "tramos": LLt},
           "profundidad_minima_por_capacidad": hq, "archivos": {"dxf": dxf, "png": png, "dimensionamiento": xls}, "segundos": round(time.time() - t0, 1),
           "requiere_confirmacion": ["descargas"] if not cfg.get("descargas") else []}
    json.dump(out, open(os.path.join(salida, "resultado.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return out
