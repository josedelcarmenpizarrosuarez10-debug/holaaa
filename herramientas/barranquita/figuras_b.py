"""Figuras (PNG) de las memorias de drenaje pluvial de la I.E. N.° 0590 Barranquita."""
import os, sys, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import hidrologia_b as H, diseno_b as DS

DIR = os.path.join(RAIZ, "entregables_barranquita", "figuras_memoria")
VP = os.path.join(RAIZ, "entregables_barranquita", "vistas_previas")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})


def _g(nombre): return os.path.join(DIR, nombre)


def serie(HID):
    A = HID["analisis"]; anos = [a for a, _ in A["serie"]]; tr = [p for _, p in H.maximos()]; bq = [p for _, p in A["serie"]]
    fig, ax = plt.subplots(figsize=(8.5, 3.6)); x = np.arange(len(anos))
    ax.bar(x - 0.2, tr, 0.4, color="#7fa7d9", label="CO Tarapoto (registrada)")
    ax.bar(x + 0.2, bq, 0.4, color="#1f3a68", label="Barranquita (transpuesta x %.3f)" % HID["factor"])
    ax.set_xticks(x); ax.set_xticklabels(anos, rotation=90); ax.set_ylabel("P máx. 24 h (mm)"); ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper left", fontsize=8); fig.tight_layout(); fig.savefig(_g("fig_serie.png"), dpi=170); plt.close(fig)


def frecuencias(HID):
    A = HID["analisis"]; T = H.PERIODOS
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    for k, nom, est in (("normal", "Normal", "--"), ("lognormal", "Log-Normal (adoptada)", "-"), ("lp3", "Log-Pearson III", "-."), ("gumbel", "Gumbel", ":")):
        ax.plot(T, [A["tabla"][t][k] for t in T], est, lw=2 if k == "lognormal" else 1.3, label=nom, marker="o", ms=3)
    xs = [p for p, _ in A["orden"]]; Tr = [1 / (1 - f) for _, f in A["orden"]]
    ax.plot(Tr, xs, "k.", ms=6, label="Serie transpuesta (Weibull)")
    ax.axvline(H.T_DISENO, color="r", lw=0.8); ax.annotate("T = 25 años\nP24 = %.1f mm" % HID["P24"], (H.T_DISENO, HID["P24"]), xytext=(40, HID["P24"] - 55),
                                                          arrowprops=dict(arrowstyle="->", color="r"), fontsize=8, color="r")
    ax.set_xscale("log"); ax.set_xlabel("Periodo de retorno T (años)"); ax.set_ylabel("P máx. 24 h (mm)"); ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(_g("fig_frecuencias.png"), dpi=170); plt.close(fig)


def idf(HID):
    fig, ax = plt.subplots(figsize=(7.5, 4.2)); D = np.array([5, 10, 15, 20, 30, 45, 60, 90, 120])
    for T in (2, 5, 10, 25, 50, 100):
        P24 = HID["p24"][T]; I = P24 * (D / 1440.0) ** 0.25 * 60 / D
        ax.plot(D, I, lw=2.2 if T == 25 else 1.2, label="T = %d años" % T)
    ax.plot([HID["tc"]], [HID["I"]], "ro"); ax.annotate("Diseño: tc = 10 min\nI = %.1f mm/h" % HID["I"], (HID["tc"], HID["I"]), xytext=(25, HID["I"] + 20), fontsize=8, color="r",
                                                       arrowprops=dict(arrowstyle="->", color="r"))
    ax.set_xlabel("Duración (min)"); ax.set_ylabel("Intensidad (mm/h)"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(_g("fig_idf.png"), dpi=170); plt.close(fig)


def superficies():
    import terreno_b as T
    SUP = H.superficies(T.cargar(), DS.CERCO, DS.PATIO); R = json.load(open(os.path.join(RAIZ, "entregables_barranquita", "_calc", "diseno.json")))
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    col = {"verde": "#cfe8c4", "pavimento": "#d0d0d0", "techo": "#f2c48d"}
    for k in ("verde", "pavimento", "techo"):
        g = SUP[k]
        for p in getattr(g, "geoms", [g]):
            if p.is_empty: continue
            x, y = p.exterior.xy; ax.fill(x, y, color=col[k], lw=0)
            for h in p.interiors:
                x, y = h.xy; ax.fill(x, y, color="white", lw=0)
    cx, cy = zip(*(DS.CERCO + [DS.CERCO[0]])); ax.plot(cx, cy, "r-", lw=1.4)
    for r in R["ramales"]:
        p = [R["nudos"][n] for n in r["nudos"]]; ax.plot([a[0] for a in p], [a[1] for a in p], color="#0070c0", lw=1.6)
    for k, v in DS.DESCARGAS.items():
        x, y = R["nudos"][k]; ax.plot(x, y, "o", color="#0070c0"); ax.text(x + 2, y + 2, k, color="#0070c0", fontsize=9, weight="bold")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=col["techo"], label="Techos (C = 0.88)"), Patch(color=col["pavimento"], label="Pavimentos (C = 0.88)"),
                       Patch(color=col["verde"], label="Áreas verdes y terreno (C = 0.40)"), plt.Line2D([], [], color="#0070c0", lw=2, label="Ejes de cuneta"),
                       plt.Line2D([], [], color="r", lw=1.4, label="Cerco perimétrico")], loc="lower left", fontsize=7.5)
    ax.set_aspect("equal"); ax.axis("off"); fig.tight_layout(); fig.savefig(_g("fig_superficies.png"), dpi=170); plt.close(fig)


def recortes():
    """Recortes de las vistas previas de los planos (planta general, seccion tipica y una descarga)."""
    from PIL import Image
    for cod, caja, nombre in (("DC-01", (0.035, 0.03, 0.88, 0.76), "fig_planta.png"), ("DC-02", (0.26, 0.56, 0.86, 0.80), "fig_secciones.png"),
                              ("DC-16", (0.03, 0.02, 0.97, 0.80), "fig_descarga_d1.png"), ("DC-04", (0.03, 0.02, 0.84, 0.45), "fig_perfil.png")):
        f = os.path.join(VP, cod + ".png")
        if not os.path.exists(f): continue
        im = Image.open(f); W, Hh = im.size
        im.crop((int(caja[0] * W), int(caja[1] * Hh), int(caja[2] * W), int(caja[3] * Hh))).save(_g(nombre))


def todas(HID):
    os.makedirs(DIR, exist_ok=True)
    serie(HID); frecuencias(HID); idf(HID); superficies(); recortes()


if __name__ == "__main__":
    todas(H.resultados())
