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

from . import lector_dxf, terreno, sitio as sitio_mod, red as red_mod, cotas, verificacion, salidas, geom, superficies, escena, hidrologia, lloraderos, dimensionamiento, planos, techo, sumideros, metrado, planta_lamina, memorias, especificaciones, revision, render, memoria_calculo, caratulas, planteamiento
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
    if ed.get("montantes"): cfg["montantes"] = ed["montantes"]
    if ed.get("sumideros") is not None and ed.get("sumideros_visor"): cfg["sumideros"] = ed["sumideros"]          # todos los montantes que dejo el proyectista en el visor


def _preparar(cfg, base, salida):
    P = combinar(cfg.get("parametros"))
    dxf = _ruta(base, cfg["dxf"])
    capas = cfg["capas"]
    cv = capas.get("ventana_por_capa")
    if cv is None and isinstance(capas.get("curvas"), dict) and os.path.getsize(dxf) > 50e6: cv = capas["curvas"].get("capa")
    B = lector_dxf.base(dxf, cache=os.path.join(salida, "_base_sitio.pkl"), ventana=capas.get("ventana"), capa_ventana=cv)
    tcfg = cfg.get("terreno") or {}
    if tcfg.get("landxml"):
        # superficie topografica LandXML (con su transformacion al plano) en lugar de las curvas del plano
        pc = (capas.get("cerco") or {}).get("poligono")
        if not capas.get("ventana") and not pc: raise ValueError("Con terreno LandXML hace falta capas.ventana o el poligono del cerco")
        cb = capas.get("ventana") or (min(p[0] for p in pc) - 30, min(p[1] for p in pc) - 30, max(p[0] for p in pc) + 30, max(p[1] for p in pc) + 30)
        Pt = terreno.puntos_landxml(_ruta(base, tcfg["landxml"]), cb, tcfg.get("transformacion"), os.path.join(salida, "_topo.pkl"))
        T = terreno.Terreno.desde_puntos(Pt)
        cur = terreno.curvas_de_puntos(T, cb, tcfg.get("equidistancia", 0.25))
        rep_t = {"fuente": "superficie LandXML", "puntos": int(len(Pt)), "curvas_generadas": len(cur),
                 "z_min": round(float(Pt[:, 2].min()), 2), "z_max": round(float(Pt[:, 2].max()), 2)}
    else:
        cur, rep_t = terreno.curvas(B, {"curvas": capas["curvas"], "curvas_texto": capas.get("curvas_texto"),
                                        "equidistancia": capas.get("equidistancia"), "z_min": capas.get("z_min", -500),
                                        "z_max": capas.get("z_max", 9000)})
        T = terreno.Terreno(cur)
    S = sitio_mod.Sitio(B, {"cerco": capas["cerco"], "techos": capas.get("techos"), "veredas": capas.get("veredas"),
                            "muros": capas.get("muros"), "niveles": cfg.get("niveles", {}),
                            "superficies": cfg.get("superficies", [])}, T, P)
    if cfg.get("receptor"):
        # las cunetas entregan a un colector o canal existente: su nivel reemplaza al terreno exterior en las descargas
        rc = cfg["receptor"]
        T = terreno.ConReceptor(T, rc["linea"], rc["perfil"], rc.get("ancho", 2.5), S.cerco, rc.get("solo_receptor", True))
        rep_t["receptor"] = rc.get("nombre", "receptor")
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
    LL, _ = _lluvia_diseno(cfg, base)
    lados_t, _, _ = techo.ubicar(S, P, float(LL.get("I_mmh") or 0) or verificacion.intensidad(LL)[0], cfg)
    mont = [{"x": c[0], "y": c[1], "V": V, "u": h, "n": l["nrm"]} for l in lados_t for (c, V, h) in l["pos"]]
    sums, _ = sumideros.proponer(M, ejes, P, float(LL.get("I_mmh") or 0) or verificacion.intensidad(LL)[0], cfg)
    esc = escena.escribir(os.path.join(salida, "escena.json"), B, S, M, ejes, cur, cfg.get("proyecto", {}), getattr(S, "aguas", []), mont, sums)
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
    LL, Rh = _lluvia_diseno(cfg, base)
    # planteamiento de cunetas para edificaciones y losa deportiva: cada montante debe tener una cuneta a su alcance (planteamiento.py)
    modo_pl = cfg.get("planteamiento", "completar")
    lineas_pl, plan_inf, plan_av = planteamiento.proponer(S, P, float(LL.get("I_mmh") or 0) or verificacion.intensidad(LL)[0], cfg, ejes)
    if modo_pl == "automatico": ejes = []
    ejes = ejes + lineas_pl
    if not ejes: raise ValueError("No hay lineas de cuneta del usuario (capas.ejes o ejes_lineas) ni techos para plantearlas")
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
        R = _red(S, T, P, ejes, cfg, recorte)
        R.chaflanes(); R.nombrar()
        if not R.ramales:
            dz, det = _nivel_necesario(R, P)
            verif, probado = _nivel_verificado(cfg, base, salida, dz)
            raise ValueError("Con los niveles dados el agua no tiene salida por gravedad por ningun lado del cerco (%s). Solucion: %s." % (
                det or "ninguna cuneta llega a una descarga", _texto_nivel(cfg, dz, verif, probado)))
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
    TT = techo.calcular(S, C, P, V["hidrologia"]["I"], cfg, set(R.descargas), V)
    SM = sumideros.calcular(M, S, C, P, V["hidrologia"]["I"], cfg, set(R.descargas), V)
    # ninguna tuberia (de sumidero o de montante) llega bajo el agua de la cuneta (+5 cm): se profundiza el tramo que la recibe, sin
    # pasar de la profundidad maxima objetivo (1.00 m) en la llegada, y se recalcula (llegada.py)
    for _ in range(3):
        bajo = [x for x in SM["sumideros"] + [m for m in TT["montantes"] if m.get("llega")]
                if x["llega"] != "SOBRE EL AGUA" and x.get("tramo") and x["h_req_cuneta"] <= P.get("h_llegada_max", P["prof_max_objetivo"])]
        if not bajo: break
        for x in bajo:
            hq[x["tramo"]] = round(max(hq.get(x["tramo"], P["hmin"]), x["h_req_cuneta"]), 3)
            # los tramos cortos (< 3 m) que van antes en el mismo eje toman la misma profundidad: sin caida brusca (ni gradas)
            eje, de, a = x["tramo"].split("|")
            rr = next((r for r in C["ramales"] if r["codigo"] == eje), None)
            if rr:
                k = next((i for i, t in enumerate(rr["tramos"]) if t["de"] == de and t["a"] == a), None)
                while k is not None and k > 0 and rr["tramos"][k - 1]["L"] < 3.0:
                    k -= 1; t = rr["tramos"][k]; c = "%s|%s|%s" % (eje, t["de"], t["a"])
                    hq[c] = round(max(hq.get(c, P["hmin"]), x["h_req_cuneta"]), 3)
        for _v in range(P["vueltas_max"]):
            C = cotas.calcular(R, S, P, hq)
            V, hq2 = verificacion.verificar(C, R, S, T, P, LL, hq)
            if hq2 == hq: break
            hq = hq2
        TT = techo.calcular(S, C, P, V["hidrologia"]["I"], cfg, set(R.descargas), V)
        SM = sumideros.calcular(M, S, C, P, V["hidrologia"]["I"], cfg, set(R.descargas), V)
        SM["avisos"].append("Se profundizaron los tramos %s para recibir la tuberia de %s sobre el nivel del agua de la cuneta (+5 cm)." % (
            ", ".join(sorted({x["tramo"].replace("|", " ") for x in bajo})), ", ".join(x.get("sumidero") or x.get("montante") for x in bajo)))
    anchos = {(f["eje"], f["de"], f["a"]): f["b"] for f in V["hidraulica"]}
    xls_t = techo.excel(TT, os.path.join(salida, "CANALETAS_MONTANTES_Y_SUMIDEROS.xlsx"), SM)
    verde = M.por_tipo().get("verde")
    LLt, LLp = lloraderos.calcular(C, verde, P, anchos)
    tapas_i = planta_lamina.tapas_de(C, set(R.descargas), anchos, P)
    xls_m, q_m, partidas = metrado.libro(os.path.join(salida, "METRADO_DRENAJE_PLUVIAL.xlsx"), C, R, M, P, anchos, V, LLt, TT, SM, cfg.get("proyecto", {}), cfg, tapas_i)
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
               "anchos_libres_m": sorted({f["b"] for f in V["hidraulica"]}), "lloraderos": lloraderos.resumen(LLt),
               "techos": TT["metrado"], "sumideros": SM["metrado"]}
    proyecto = cfg.get("proyecto", {})
    dxf = salidas.dxf_planta(os.path.join(salida, "PLANTA_RED_CUNETAS.dxf"), C, R, S, cur, P, proyecto, anchos, LLp)
    pl = cfg.get("planos", {})
    dxf_pf, laminas, n_sec, marcos = planos.dxf_planos(os.path.join(salida, "PLANOS_CUNETAS.dxf"), C, R, S, P, anchos, proyecto, cur, V, LLt, LLp,
                                               list(secciones.values()), pl.get("prefijo", "DC"), pl.get("inicio", 1), TT, SM,
                                                       T, _niveles_txt(cfg), tapas_i)
    png = salidas.png_planta(os.path.join(salida, "PLANTA_RED_CUNETAS.png"), C, R, S, cur, ejes,
                             "%s - red de cunetas: %d ejes, %d descargas, %.1f m (%.1f m de uniones nuevas)" % (
                                 proyecto.get("nombre_corto", ""), resumen["ejes"], resumen["descargas"], Ltot, nuevas))
    # vista previa PNG de cada lamina (LAMINA_<codigo>.png)
    import ezdxf
    dxf_doc = ezdxf.readfile(dxf_pf)
    pngs = render.laminas_png(dxf_doc, [dict(m, codigo=c) for (c, _), m in zip(laminas, marcos)], salida) if cfg.get("png_laminas", True) else []
    lams_idx = [dict(codigo=c, titulo=t, escala="1/%d" % m["esc"]) for (c, t), m in zip(laminas, marcos)]
    doc_i = caratulas.indice_planos(os.path.join(salida, "CARATULA_E_INDICE_DE_PLANOS.docx"), proyecto, lams_idx,
                                    caratulas.detalle_laminas(dxf_doc, marcos))
    doc_c = caratulas.caratulas(os.path.join(salida, "CARATULAS_DRENAJE_PLUVIAL.docx"), proyecto)
    # documentos: memoria hidrologica, memoria descriptiva y especificaciones tecnicas (Word)
    lams = [{"codigo": c_, "titulo": t_} for c_, t_ in laminas]
    fig = {"planta": png}
    if Rh:
        hidrologia.excel(Rh, os.path.join(salida, "HIDROLOGIA.xlsx")); fig["idf"] = hidrologia.png_idf(Rh, os.path.join(salida, "CURVAS_IDF.png"))
    xls_mc = memoria_calculo.libro(os.path.join(salida, "MEMORIA_CALCULO_DRENAJE_PLUVIAL.xlsx"), proyecto, P, Rh, LL, V, list(secciones.values()), TT, SM)
    xls_mc_rc = metrado.recalcular(xls_mc, os.path.join(salida, "_recalculado"))
    xls_rc = metrado.recalcular(xls_m, os.path.join(salida, "_recalculado"))
    tot = metrado.totales(xls_rc)
    metas = [dict(x, total=tot.get(x["codigo"])) for x in partidas]
    ctx = memorias.Contexto(cfg, P, Rh, LL, V, C, R, list(secciones.values()), TT, SM, LLt, lams, metas, rep_t, M.cuadro(), fig)
    ctx.plan = plan_inf
    ctx.hmax = max((x["h_max"] for x in q_m), default=ctx.hmax)       # una sola cifra en todos los documentos (la del metrado)
    doc_h, doc_d = memorias.escribir(salida, ctx)
    doc_e = especificaciones.construir(os.path.join(salida, "ESPECIFICACIONES_TECNICAS_DRENAJE_PLUVIAL.docx"), partidas, P, cfg, q_m, V, lams, TT, SM, LLt)
    # revision general de todo lo entregado (conocimiento/01, seccion 8.2)
    nivel = _nivel_necesario(R, P, V)
    if nivel[0] > 0:
        verif, probado = _nivel_verificado(cfg, base, salida, nivel[0])
        nivel = (verif or nivel[0], nivel[1], _texto_nivel(cfg, nivel[0], verif, probado), verif is not None)
    rev = _revisar(salida, P, V, C, list(secciones.values()), TT, SM, LLt, M, xls_rc, tot, partidas, q_m, tapas_i, lams, marcos, Rh, proyecto,
                   [doc_h, doc_d, doc_e, doc_i, doc_c, xls_m, xls, xls_t, xls_mc, dxf_pf, dxf] + ([os.path.join(salida, "HIDROLOGIA.xlsx")] if Rh else []),
                   {"memoria hidrológica": doc_h, "memoria descriptiva": doc_d, "especificaciones": doc_e}, hq,
                   [a for a in S.avisos + M.avisos + R.avisos + SM["avisos"] if "no tiene cuneta" not in a], dxf_doc, xls_mc_rc, nivel,
                   [t["techo"] for t in plan_inf if t.get("decision") == "sin solucion automatica"])
    out = {"accion": "disenar", "version": VERSION, "proyecto": proyecto, "resumen": resumen, "parametros": P,
           "mapa_superficies": M.cuadro(),
           "terreno": rep_t, "avisos": S.avisos + M.avisos + R.avisos + TT["avisos"] + SM["avisos"] + plan_av + (
               ["SALIDA POR GRAVEDAD (%s). Solucion: %s." % (nivel[1], nivel[2])] if nivel[0] > 0 else []),
           "solucion_nivel": {"subir_npt_m": nivel[0], "detalle": nivel[1], "solucion": nivel[2], "verificado": nivel[3]} if nivel[0] > 0 else None,
           "planteamiento": {"modo": modo_pl, "lineas_nuevas": lineas_pl, "longitud_nueva_m": round(sum(geom.dist(a, b) for l in lineas_pl for a, b in zip(l[:-1], l[1:])), 2), "techos": plan_inf}, "chaflanes": R.chaflanes_hechos, "red": C,
           "descargas_propuestas": [{"D": k, "x": round(v["q"][0], 3), "y": round(v["q"][1], 3), "L_max_m": v["L_max"],
                                     "terreno_exterior_min": round(v["z_req"], 2)} for k, v in R.descargas.items()],
           "sin_salida": [[list(a), list(b)] for a, b in R.sin_cubrir], "verificacion": V,
           "secciones_por_eje": list(secciones.values()), "techos": TT, "sumideros": SM, "lloraderos": {"resumen": lloraderos.resumen(LLt), "tramos": LLt},
           "profundidad_minima_por_capacidad": hq, "archivos": {"dxf": dxf, "png": png, "dimensionamiento": xls, "canaletas_montantes_y_sumideros": xls_t, "metrado": xls_m, "planos": dxf_pf,
                                                 "memoria_hidrologica": doc_h, "memoria_descriptiva": doc_d, "especificaciones": doc_e,
                                                 "revision": rev[0], "png_laminas": pngs, "memoria_calculo": xls_mc, "indice_planos": doc_i, "caratulas": doc_c},
           "revision": rev[1],
           "metrado_resumen": metas,
           "laminas": [dict(codigo=c, titulo=t, marco=[round(m["x0"], 3), round(m["y0"], 3), round(m["x1"], 3), round(m["y1"], 3)], escala="1/%d" % m["esc"])
                       for (c, t), m in zip(laminas, marcos)], "secciones_dibujadas": n_sec, "segundos": round(time.time() - t0, 1),
           "requiere_confirmacion": ["descargas"] if not cfg.get("descargas") else []}
    json.dump(out, open(os.path.join(salida, "resultado.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return out


def _niveles_txt(cfg):
    """Niveles del proyecto en una frase para las notas de los planos."""
    nv = cfg.get("niveles", {}) or {}
    b = nv.get("borde_cuneta") or nv.get("npt")
    if b is None: return ""
    t = ["NPT y borde de cuneta +%.2f (al ras)" % b]
    if nv.get("area_verde") is not None: t.append("area verde +%.2f" % nv["area_verde"])
    t += ["%s +%.2f" % (z.get("nombre", "zona").lower(), z["nivel"]) for z in nv.get("zonas", []) if z.get("nivel") is not None]
    return "; ".join(t)


def _red(S, T, P, ejes, cfg, recorte):
    """Red con busqueda adaptativa: si quedan cunetas sin salida se admiten uniones mas largas (x2, x3) y se queda la red con
    menos cuneta sin salida."""
    mejor = None
    for k in (1, 2, 3):
        Pk = P if k == 1 else dict(P, union_max=P["union_max"] * k)
        R = red_mod.Red(S, T, Pk, ejes, cfg.get("descargas")).resolver(recorte)
        L_sin = sum(geom.dist(a, b) for a, b in R.sin_cubrir)
        if mejor is None or L_sin < mejor[0] - 0.5: mejor = (L_sin, R, k)
        if L_sin < 0.5: break
    if mejor[0] >= 0.5:
        # ultimo recurso: cada pedazo suelto se une en linea recta a la cuneta mas cercana que ya tiene salida, sin cruzar techos
        # ni salir del cerco, y se rehace la red
        from shapely.geometry import LineString
        from shapely.ops import nearest_points, unary_union
        R = mejor[1]
        red_ok = unary_union([LineString([R.Nf[a], R.Nf[b]]) for r in R.ramales for a, b in zip(r["nudos"][:-1], r["nudos"][1:])])
        sueltas = unary_union([LineString([a, b]) for a, b in R.sin_cubrir])
        techos = S.techos.buffer(-0.05) if not S.techos.is_empty else S.techos
        puentes = []
        if not red_ok.is_empty:
            for comp in (sueltas.geoms if hasattr(sueltas, "geoms") else [sueltas]):
                a, b = nearest_points(comp, red_ok)
                pz = LineString([a, b])
                if pz.length < 0.05: continue
                if S.interior.buffer(0.02).covers(pz) and (techos.is_empty or pz.intersection(techos).length < 0.05):
                    puentes.append([(a.x, a.y), (b.x, b.y)])
        if puentes:
            R2 = red_mod.Red(S, T, P, ejes + puentes, cfg.get("descargas")).resolver(recorte)
            L2 = sum(geom.dist(a, b) for a, b in R2.sin_cubrir)
            if L2 < mejor[0] - 0.5:
                R2.avisos.append("%d cunetas sueltas se unieron en linea recta a la cuneta mas cercana con salida (%.1f m)." % (
                    len(puentes), sum(geom.dist(*p) for p in puentes)))
                mejor = (L2, R2, mejor[2])
    if mejor[2] > 1:
        mejor[1].avisos.append("Para dar salida a todas las cunetas se admitieron uniones de hasta %.0f m." % (P["union_max"] * mejor[2]))
    return mejor[1]


def _nivel_necesario(R, P, V=None):
    """Cuanto hay que subir el nivel del piso (NPT, y con el todas las cotas de fondo) para que el agua salga por gravedad:
    - cuneta sin salida: lo que le falta a la mejor descarga posible del cerco para recibirla (S0 x recorrido - holgura);
    - descarga que no sale: terreno exterior + margen - cota de fondo.
    Devuelve (metros, detalle)."""
    from shapely.geometry import LineString, Point
    from shapely.ops import unary_union
    falta, det = 0.0, []
    if R.sin_cubrir:
        cand = R.candidatos_descarga()
        g = unary_union([LineString([a, b]) for a, b in R.sin_cubrir])
        for comp in (g.geoms if hasattr(g, "geoms") else [g]):
            pts = [Point(c) for c in comp.coords] if comp.geom_type == "LineString" else []
            if not pts or not cand: continue
            d = min(max(0.0, P["S0"] * 1.15 * max(Point(c["b"]).distance(p) for p in pts) - c["holgura"]) for c in cand)
            if d > falta: falta = d
        det.append("%.1f m de cuneta sin salida por gravedad" % sum(geom.dist(a, b) for a, b in R.sin_cubrir))
    for d in (V or {}).get("descargas", []):
        if d["estado"] != "SALE POR GRAVEDAD":
            info = R.descargas.get(d["D"], {})
            x = info.get("z_req", d["cf"]) + P["desc_margen"] - d["cf"]
            if x > falta: falta = x
            det.append("descarga %s no sale (cota de fondo %.3f)" % (d["D"], d["cf"]))
    import math as _m
    return (_m.ceil(falta * 20 - 1e-9) / 20.0 if falta > 0 else 0.0), "; ".join(det)


def _con_nivel(cfg, dz):
    """Copia del proyecto con el piso (NPT, borde de cuneta, area verde y zonas) dz m mas alto."""
    import copy
    c = copy.deepcopy(cfg); nv = c.setdefault("niveles", {})
    for k in ("npt", "borde_cuneta", "area_verde"):
        if isinstance(nv.get(k), (int, float)): nv[k] = round(nv[k] + dz, 3)
    for z in nv.get("zonas", []):
        if isinstance(z.get("nivel"), (int, float)): z["nivel"] = round(z["nivel"] + dz, 3)
    return c


def _ensayo(cfg, base, salida, dz):
    """Diseno rapido (planteamiento, red, cotas y verificacion; sin documentos) con el piso dz m mas alto.
    True si toda la red sale por gravedad."""
    c = _con_nivel(cfg, dz)
    P, B, cur, rep_t, T, S, ejes = _preparar(c, base, salida)
    LL, Rh = _lluvia_diseno(c, base)
    I = float(LL.get("I_mmh") or 0) or verificacion.intensidad(LL)[0]
    lin, _, _ = planteamiento.proponer(S, P, I, c, ejes)
    if c.get("planteamiento", "completar") == "automatico": ejes = []
    ejes = ejes + lin
    if not ejes: return False
    recorte = {}
    for _i in range(3):
        R = _red(S, T, P, ejes, c, recorte); R.chaflanes(); R.nombrar()
        if not R.ramales: return False
        _mapa(B, S, c, P, [(R.Nf[a], R.Nf[b]) for r in R.ramales for a, b in zip(r["nudos"][:-1], r["nudos"][1:]) if not (b in R.descargas)])
        hq = {}
        for _v in range(P["vueltas_max"]):
            C = cotas.calcular(R, S, P, hq)
            V, hq2 = verificacion.verificar(C, R, S, T, P, LL, hq)
            if hq2 == hq: break
            hq = hq2
        malas = [d for d in V["descargas"] if d["estado"] != "SALE POR GRAVEDAD"]
        if not malas and not R.sin_cubrir: return True
        if c.get("descargas"): return False
        for d in malas:
            info = R.descargas[d["D"]]
            recorte[info["k"]] = recorte.get(info["k"], 0.0) + max(info["z_req"] + P["desc_margen"] - d["cf"], 0.01) / P["S0"] + 2.0
    return False


def _nivel_verificado(cfg, base, salida, dz0):
    """Prueba el piso mas alto (desde lo estimado, de 5 en 5 cm y luego mas) hasta que todo salga por gravedad.
    Devuelve (dz verificado o None, ultimo probado). Solo con el interior nivelado y un NPT dado."""
    nv = cfg.get("niveles") or {}
    if nv.get("modo", "nivelado") != "nivelado" or not isinstance(nv.get("npt"), (int, float)): return None, 0.0
    d0 = max(round(dz0, 2), 0.05); probado = 0.0
    for extra in (0.0, 0.05, 0.10, 0.20, 0.35, 0.50, 0.75, 1.00, 1.50):
        probado = round(d0 + extra, 2)
        try:
            if _ensayo(cfg, base, salida, probado): return probado, probado
        except Exception:
            return None, probado
    return None, probado


def _texto_nivel(cfg, dz, verif, probado):
    npt = (cfg.get("niveles") or {}).get("npt")
    a = lambda d: (" (NPT %.2f)" % (npt + d)) if isinstance(npt, (int, float)) else ""
    if verif is not None:
        return "subir el nivel de piso %.2f m%s: verificado, con ese nivel toda la red sale por gravedad" % (verif, a(verif))
    if probado:
        return ("se probo subir el piso hasta %.2f m%s sin lograr salida por gravedad: indicar una descarga a un colector o canal "
                "existente (receptor) o con su cota" % (probado, a(probado)))
    return "subir el nivel de piso al menos %.2f m%s o indicar una descarga a un colector o canal existente" % (dz, a(dz))


def _revisar(salida, P, V, C, sec, TT, SM, LLt, M, xls_rc, tot, partidas, q, tapas, lams, marcos, Rh, proyecto, archivos, docs, hq=None, avisos=(), dxf_doc=None, xls_mc_rc=None, nivel=None, sin_plan=()):
    import ezdxf
    from shapely.geometry import Point
    I = revision.Informe()
    revision.diseno(I, P, V, C, sec, hq)
    tipo = lambda x, y: next((c["tipo"] for c in M.caras if c["geom"].contains(Point(x, y))), None)
    revision.componentes(I, P, TT, SM, LLt, tipo)
    Lt = sum(r["L"] for r in C["ramales"]); Lta = sum(t["L_tapado"] for r in C["ramales"] for t in r["tramos"])
    m, sm = TT["metrado"], SM["metrado"]
    revision.metrado(I, xls_rc, tot, partidas, [
        ("Limpieza (L x franja)", ("LIMPIEZA",), "m²", sum(x["L"] * x["bexc"] for x in q), 0.05),
        ("Excavación de zanjas", ("EXCAVACI", "CUNETAS"), "m³", sum(x["excavacion"] for x in q), 0.05),
        ("Rejilla (L - tapado)", ("REJILLA",), "m", Lt - Lta, 0.1),
        ("Tapas de inspección", ("TAPA DE INSPECCION",), "und", len(tapas), 0),
        ("Lloraderos", ("LLORADERO",), "und", sum(x["n"] for x in LLt), 0),
        ("Codos de 90° en piso (sumideros y dados)", ("CODO DESAG",), "und", sm.get("codo90_und", 0) + m.get("codo_dado_und", 0), 0),
        ("Falsas columnas", ("FALSA COLUMNA",), "und", m.get("falsas_columnas_und", 0), 0),
        ("Canaletas", ("CANALETA DE PLANCHA",), "m", m.get("canaleta_m", 0), 0.05),
        ("Soportes de canaleta", ("SOPORTE",), "und", m.get("soportes_und", 0), 0),
        ("Tapas laterales", ("TAPA LATERAL",), "und", m.get("tapas_und", 0), 0),
        ("Boquillas", ("BOQUILLA",), "und", m.get("boquillas_und", 0), 0),
        ("Sumideros", ("SUMIDERO",), "und", sm.get("sumideros_und", 0), 0),
        ("Tubería de sumideros y salidas enterradas", ("TUBERIA DESAG",), "m", sm.get("tuberia_4_m", 0) + m.get("tuberia_enterrada_m", 0), 0.05)])
    revision.memoria_calculo(I, xls_mc_rc, V, Rh, TT, SM)
    if dxf_doc is None: dxf_doc = ezdxf.readfile(next(a for a in archivos if a and a.endswith("PLANOS_CUNETAS.dxf")))
    revision.documentos(I, archivos, proyecto, lams, dxf_doc)
    f2 = lambda v: "%.2f" % v
    todos = ("memoria hidrológica", "memoria descriptiva", "especificaciones")
    cif = [("Longitud total de cuneta %s m" % f2(Lt), "{:,.2f}".format(Lt), ("memoria descriptiva", "especificaciones")),
           ("Profundidad máxima %s m" % f2(max(x["h_max"] for x in q)), f2(max(x["h_max"] for x in q)), ("memoria descriptiva", "especificaciones"))]
    if LLt: cif.append(("%d lloraderos" % sum(x["n"] for x in LLt), "%d lloraderos" % sum(x["n"] for x in LLt), ("memoria descriptiva", "especificaciones")))
    if TT["montantes"]:
        cif += [("%d montantes" % m["montantes_und"], "%d montantes" % m["montantes_und"], ("memoria descriptiva",)),
                ("Canaleta %s m" % f2(m["canaleta_m"]), "{:,.2f}".format(m["canaleta_m"]), todos)]
    if Rh: cif += [("Intensidad %.2f mm/h" % Rh["I"], "%.2f mm/h" % Rh["I"], ("memoria hidrológica", "memoria descriptiva")),
                   ("P24 %.2f mm" % Rh["P24"], "%.2f mm" % Rh["P24"], ("memoria hidrológica", "memoria descriptiva"))]
    revision.cifras(I, docs, cif)
    revision.planos(I, dxf_doc, marcos)
    revision.entregables(I, salida, archivos, lams)
    revision.avisos_diseno(I, avisos)
    if sin_plan:
        I.decision(("llega a una cuneta",), "%s: alrededor del techo no cabe una cuneta automatica (cerco u otras edificaciones); "
                   "plantear a mano la cuneta que reciba esos montantes o cambiarlos de esquina" % ", ".join(sin_plan))
    if nivel and nivel[0] > 0:
        I.decision(("Conectividad", "Descarga ", "Comprobación 1:", "Comprobación 6:", "Comprobación 12:", "llega a una cuneta", "Todas las lineas"),
                   "con el nivel de piso dado el terreno no da salida por gravedad a toda la red (%s). Solucion: %s; la parte que si sale "
                   "queda disenada completa" % (nivel[1], nivel[2]))
    return revision.escribir(os.path.join(salida, "REVISION_GENERAL.xlsx"), I), I.resumen()
