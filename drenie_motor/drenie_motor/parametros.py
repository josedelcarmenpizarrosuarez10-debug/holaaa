"""Valores por defecto del modulo Terreno y red de cunetas en planta.

Cada valor sale de los criterios del usuario guardados en conocimiento/04_cunetas_sobre_terreno.md (seccion 19) y
conocimiento/02_hidrologia_e_hidraulica.md (seccion 12). Todos se pueden cambiar en el archivo del proyecto (bloque "parametros").
"""
import copy

PARAMETROS = {
    # seccion de la cuneta
    "b_int": 0.40,            # ancho libre interior (m)
    "e_muro": 0.10,           # espesor de muro (m): ancho total 0.60
    "e_tapa": 0.10,           # losa de los tramos tapados (m)
    "h0": 0.30,               # profundidad al inicio de cada eje (m)
    "hmin": 0.25,             # altura libre minima (bajo la losa en los tapados)
    "S0": 0.005,              # pendiente minima de la cota de fondo (0.5 %)
    "h_acero": 0.40,          # con h >= 0.40 m lleva acero (o si es tapada); menor, concreto simple
    # hidraulica (CE.040)
    "n_cap": 0.015,           # Manning para la capacidad
    "n_vel": 0.013,           # Manning para la velocidad
    "BL": 0.05,               # borde libre minimo (m)
    "Vmax": 3.0,              # velocidad maxima en concreto (m/s); si pasa, gradas
    "FS": 1.15,               # factor de seguridad de los caudales
    # trazo en planta
    "d_cerco": 0.60,          # eje de la cuneta perimetral a 0.60 m del cerco (borde exterior a 0.30 m)
    "chaflan": 0.60,          # quiebre a 45 grados: corte de 0.60 m por lado
    "ang_chaflan": 50.0,      # esquinas con giro mayor se ochavan
    "paso": 0.50,             # muestreo del perfil (m)
    "tol_union": 0.60,        # extremos de lineas a menos de esta distancia se unen
    "union_max": 40.0,        # largo maximo de una union nueva entre lineas o hasta el cerco (m)
    "dist_muro": 0.30,        # el eje no se acerca a menos de 0.30 m de un muro o techo
    # descargas por el cerco
    "desc_dist_ext": 2.0,     # el terreno exterior debe quedar bajo la cota de fondo a <= 2.0 m del cerco
    "desc_margen": 0.05,      # margen bajo la cota de fondo (m)
    "desc_sep_min": 15.0,     # separacion minima entre dos descargas propuestas (m)
    "prof_max_objetivo": 1.00,  # si una red pasa de esta profundidad, se busca otra descarga
    # tapas de inspeccion en tramos tapados
    "tapa_lado": 0.60,
    "tapa_sep_max": 10.0,
    # coeficientes de escorrentia por superficie
    "C": {"techo": 0.88, "pavimento": 0.88, "estacionamiento": 0.88, "verde": 0.40},
    # ciclo diseno <-> verificacion
    "vueltas_max": 8,
}


def combinar(usuario):
    """Parametros por defecto con los cambios del proyecto."""
    p = copy.deepcopy(PARAMETROS)
    for k, v in (usuario or {}).items():
        if isinstance(v, dict) and isinstance(p.get(k), dict): p[k].update(v)
        else: p[k] = v
    return p
