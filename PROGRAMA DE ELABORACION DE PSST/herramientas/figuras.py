# -*- coding: utf-8 -*-
"""Figuras del PSST (PNG a 200 ppp) en entregables/_calc/fig.
Uso:  python3 figuras.py <carpeta del proyecto>      (antes: nucleo.py)"""
import collections, json, os, sys, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": "#8C8C8C", "axes.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "xtick.color": "#404040", "ytick.color": "#404040"})
AZUL = "#1F4E79"; AZUL2 = "#2E75B6"; GRIS = "#7F7F7F"; TINTA = "#262626"
NIV = ["Trivial", "Tolerable", "Moderado", "Importante", "Intolerable"]
COL = {"Trivial": "#70AD47", "Tolerable": "#A9D08E", "Moderado": "#FFD966", "Importante": "#F4B183", "Intolerable": "#E06666"}


def guardar(fig, ruta):
    fig.savefig(ruta, dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig)


def f_personal(D, ruta):
    per = D["personal"]; m = [p[0] for p in per]; n = [p[1] for p in per]
    fig, ax = plt.subplots(figsize=(8.0, 3.2))
    ax.bar(m, n, color=AZUL2, width=0.72, edgecolor="white", linewidth=1.0)
    k = n.index(max(n)); ax.annotate("Máximo: %d trabajadores" % max(n), (m[k], n[k]), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8.5, color=TINTA)
    ax.set_xlabel("Mes de ejecución"); ax.set_ylabel("Trabajadores (promedio)"); ax.set_xticks(m)
    ax.set_ylim(0, max(n) * 1.18); ax.grid(axis="y", color="#E0E0E0", linewidth=0.6); ax.set_axisbelow(True)
    guardar(fig, ruta)


def f_calor(D, ruta):
    R = D["iperc"]
    fig, axs = plt.subplots(1, 2, figsize=(8.2, 4.4))
    for ax, (kip, ks, tit) in zip(axs, (("IP", "S", "Antes de los controles"), ("IPr", "Sr", "Después de los controles"))):
        cnt = collections.Counter((f[kip], f[ks]) for f in R)
        for i, ip in enumerate(range(4, 13)):
            for s in (1, 2, 3):
                nr = ip * s; nv = [x for x, a, b in D["niveles"] if a <= nr <= b][0]
                ax.add_patch(plt.Rectangle((s - 0.5, i - 0.5), 0.97, 0.94, color=COL[nv], alpha=0.95 if cnt[(ip, s)] else 0.28, lw=0))
                if cnt[(ip, s)]: ax.text(s, i, str(cnt[(ip, s)]), ha="center", va="center", fontsize=10, fontweight="bold", color=TINTA)
        ax.set_xlim(0.5, 3.5); ax.set_ylim(-0.5, 8.5); ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["1\nLeve", "2\nTemporal", "3\nPermanente"])
        ax.set_yticks(range(9)); ax.set_yticklabels(range(4, 13)); ax.set_xlabel("Índice de severidad"); ax.set_ylabel("Índice de probabilidad (A+B+C+D)")
        ax.set_title(tit, fontsize=10, color=AZUL, fontweight="bold"); ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)
        ax.tick_params(length=0)
    h = [plt.Rectangle((0, 0), 1, 1, color=COL[n]) for n in NIV]
    fig.legend(h, NIV, loc="lower center", ncol=5, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.06, 1, 1)); guardar(fig, ruta)


def f_niveles(D, ruta):
    R = D["iperc"]; ci = collections.Counter(f["nivel"] for f in R); cr = collections.Counter(f["nivel_r"] for f in R)
    fig, ax = plt.subplots(figsize=(8.0, 3.4)); x = range(len(NIV)); w = 0.36
    b1 = ax.bar([i - w / 2 - 0.01 for i in x], [ci[n] for n in NIV], w, color=[COL[n] for n in NIV], edgecolor="white", hatch="///", linewidth=0)
    b2 = ax.bar([i + w / 2 + 0.01 for i in x], [cr[n] for n in NIV], w, color=[COL[n] for n in NIV], edgecolor="white", linewidth=0)
    for bars in (b1, b2):
        for b in bars:
            if b.get_height(): ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, int(b.get_height()), ha="center", fontsize=8.5, color=TINTA)
    ax.set_xticks(list(x)); ax.set_xticklabels(NIV); ax.set_ylabel("Número de peligros")
    ax.legend([plt.Rectangle((0, 0), 1, 1, facecolor="#BFBFBF", hatch="///", edgecolor="white"), plt.Rectangle((0, 0), 1, 1, color="#BFBFBF")],
              ["Antes de los controles", "Después de los controles"], frameon=False, fontsize=8.5, loc="upper left")
    ax.grid(axis="y", color="#E0E0E0", linewidth=0.6); ax.set_axisbelow(True); ax.set_ylim(0, max(max(ci.values()), max(cr.values())) * 1.15)
    guardar(fig, ruta)


def f_procesos(D, ruta):
    R = D["iperc"]; procs = list(dict.fromkeys(f["proceso"] for f in R))[::-1]
    s = [sum(1 for f in R if f["proceso"] == p and f["tipo"] == "S") for p in procs]
    so = [sum(1 for f in R if f["proceso"] == p and f["tipo"] == "SO") for p in procs]
    fig, ax = plt.subplots(figsize=(8.0, 0.36 * len(procs) + 1.0))
    ax.barh(procs, s, color=AZUL2, height=0.62, edgecolor="white", linewidth=1.5, label="Seguridad (S)")
    ax.barh(procs, so, left=s, color="#9DC3E6", height=0.62, edgecolor="white", linewidth=1.5, label="Salud ocupacional (SO)")
    for i, (a, b) in enumerate(zip(s, so)): ax.text(a + b + 0.3, i, str(a + b), va="center", fontsize=8.5, color=TINTA)
    ax.set_xlabel("Número de peligros evaluados"); ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax.grid(axis="x", color="#E0E0E0", linewidth=0.6); ax.set_axisbelow(True)
    guardar(fig, ruta)


def caja(ax, x, y, w, h, txt, fc="#DDEBF7", ec=AZUL, fs=8, bold=False, col=TINTA):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=ec, lw=1.0))
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", color=col, wrap=True)


def linea(ax, pts, col=GRIS):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=1.0, zorder=0)


def f_organigrama(D, ruta):
    fig, ax = plt.subplots(figsize=(8.4, 4.8)); ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")
    org = "Comité de SST\n(paritario)" if D["organizacion"] == "comite" else "Supervisor de SST"
    caja(ax, 5, 5.6, 3.0, 0.6, "Entidad / Supervisión de obra", fc="#F2F2F2", ec=GRIS)
    caja(ax, 5, 4.6, 3.0, 0.6, "Residente de obra", fc=AZUL, ec=AZUL, bold=True, col="white")
    caja(ax, 8.4, 4.6, 2.6, 0.6, org, fc="#E2EFDA", ec="#548235")
    caja(ax, 5, 3.5, 3.4, 0.6, "Responsable de SST de la obra\n(ingeniero prevencionista)", fc="#DDEBF7", bold=True)
    caja(ax, 1.6, 3.5, 2.6, 0.6, "Médico ocupacional /\nenfermería", fc="#FCE4D6", ec="#C55A11")
    caja(ax, 8.4, 3.5, 2.6, 0.6, "Brigadas de emergencia", fc="#FCE4D6", ec="#C55A11")
    xs = [1.3, 3.75, 6.25, 8.7]
    for x, t in zip(xs, ["Ingenieros de\nfrente / campo", "Supervisores de SST\n(prevencionistas)", "Maestro de obra\ny capataces", "Subcontratistas\ny proveedores"]):
        caja(ax, x, 2.3, 2.2, 0.62, t)
    caja(ax, 5, 1.05, 6.0, 0.6, "Trabajadores (operarios, oficiales, peones, operadores y choferes)", fc="#F2F2F2", ec=GRIS)
    linea(ax, [(5, 5.3), (5, 4.9)]); linea(ax, [(6.5, 4.6), (7.1, 4.6)]); linea(ax, [(5, 4.3), (5, 3.8)])
    linea(ax, [(3.3, 3.5), (2.9, 3.5)]); linea(ax, [(6.7, 3.5), (7.1, 3.5)])
    linea(ax, [(5, 3.2), (5, 2.85)]); linea(ax, [(xs[0], 2.85), (xs[-1], 2.85)])
    for x in xs: linea(ax, [(x, 2.85), (x, 2.61)])
    linea(ax, [(xs[0], 1.72), (xs[-1], 1.72)]); linea(ax, [(5, 1.72), (5, 1.35)])
    for x in xs: linea(ax, [(x, 1.99), (x, 1.72)])
    guardar(fig, ruta)


def f_jerarquia(D, ruta):
    R = D["iperc"]; N = "No aplica"
    cnt = [sum(1 for f in R if f[k] and f[k] != N) for k in ("elim", "sust", "ing", "adm", "epp")]
    et = ["Eliminación", "Sustitución", "Controles de ingeniería", "Controles\nadministrativos", "Equipo de\nprotección personal"]
    cols = ["#1F4E79", "#2E75B6", "#5B9BD5", "#9DC3E6", "#DDEBF7"]
    fig, ax = plt.subplots(figsize=(8.0, 4.0)); ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis("off")
    for i in range(5):
        y0, y1 = 5 - i, 4 - i; w0, w1 = 6.6 - i * 0.95, 5.65 - i * 0.95
        ax.add_patch(Polygon([(3.5 - w0 / 2, y0), (3.5 + w0 / 2, y0), (3.5 + w1 / 2, y1 + 0.06), (3.5 - w1 / 2, y1 + 0.06)], closed=True, fc=cols[i], ec="white", lw=1.5))
        ax.text(3.5, (y0 + y1) / 2 + 0.03, et[i], ha="center", va="center", fontsize=8.5, color="white" if i < 3 else TINTA, fontweight="bold")
        ax.text(7.2, (y0 + y1) / 2, "%d peligros con esta medida" % cnt[i], va="center", fontsize=8.5, color=TINTA)
        linea(ax, [(3.5 + w0 / 2 - 0.4, (y0 + y1) / 2), (7.1, (y0 + y1) / 2)], col="#BFBFBF")
    ax.annotate("", xy=(0.2, 0.2), xytext=(0.2, 4.9), arrowprops=dict(arrowstyle="->", color=GRIS, lw=1.0))
    ax.text(0.05, 2.6, "Mayor a menor eficacia", rotation=90, va="center", fontsize=8, color=GRIS)
    guardar(fig, ruta)


def f_emergencia(D, ruta):
    fig, ax = plt.subplots(figsize=(8.4, 5.0)); ax.set_xlim(0, 10); ax.set_ylim(0, 7.4); ax.axis("off")
    pasos = [(5, 6.9, "Ocurre la emergencia (accidente, incendio, sismo, crecida, mordedura)", "#FCE4D6"),
             (5, 5.95, "El testigo da la alerta por radio o teléfono al capataz y al supervisor de SST", "#F2F2F2"),
             (5, 5.0, "Evaluación inicial: ¿la escena es segura? Se detienen los trabajos en el área", "#F2F2F2")]
    for x, y, t, c in pasos: caja(ax, x, y, 7.4, 0.62, t, fc=c, ec="#C55A11" if c == "#FCE4D6" else GRIS)
    for y in (6.59, 5.64): ax.annotate("", xy=(5, y - 0.32), xytext=(5, y), arrowprops=dict(arrowstyle="->", color=GRIS))
    ax.annotate("", xy=(2.5, 3.9), xytext=(4.0, 4.69), arrowprops=dict(arrowstyle="->", color=GRIS))
    ax.annotate("", xy=(7.5, 3.9), xytext=(6.0, 4.69), arrowprops=dict(arrowstyle="->", color=GRIS))
    caja(ax, 2.5, 3.55, 4.2, 0.62, "Persona herida: brigada de primeros auxilios\nestabiliza y prepara la evacuación", fc="#DDEBF7")
    caja(ax, 7.5, 3.55, 4.2, 0.62, "Incendio, sismo o crecida: brigadas de incendio\ny evacuación; personal a la zona segura", fc="#DDEBF7")
    ax.annotate("", xy=(2.5, 2.6), xytext=(2.5, 3.24), arrowprops=dict(arrowstyle="->", color=GRIS))
    ax.annotate("", xy=(7.5, 2.6), xytext=(7.5, 3.24), arrowprops=dict(arrowstyle="->", color=GRIS))
    caja(ax, 2.5, 2.25, 4.2, 0.62, "Traslado en la unidad de emergencia al\nestablecimiento de salud (directorio)", fc="#E2EFDA", ec="#548235")
    caja(ax, 7.5, 2.25, 4.2, 0.62, "Conteo del personal y aviso a bomberos,\nPNP o Defensa Civil según el caso", fc="#E2EFDA", ec="#548235")
    ax.annotate("", xy=(5, 1.25), xytext=(2.5, 1.94), arrowprops=dict(arrowstyle="->", color=GRIS))
    ax.annotate("", xy=(5, 1.25), xytext=(7.5, 1.94), arrowprops=dict(arrowstyle="->", color=GRIS))
    caja(ax, 5, 0.9, 9.0, 0.66, "Notificación (accidente mortal o incidente peligroso: al MTPE dentro de las 24 h), investigación,\nregistro y medidas correctivas", fc="#FFF2CC", ec="#BF9000", fs=7.6)
    guardar(fig, ruta)


def f_capacitacion(D, ruta):
    C = D["capacitacion"]; m = D["meses"]
    fig, ax = plt.subplots(figsize=(8.4, 0.3 * len(C) + 1.2))
    for i, c in enumerate(C):
        y = len(C) - 1 - i
        for k in c["meses"]: ax.add_patch(plt.Rectangle((k - 0.42, y - 0.32), 0.84, 0.64, color=AZUL2 if c["frecuencia"] != "al ingreso" else "#9DC3E6", lw=0))
    ax.set_xlim(0.4, m + 0.6); ax.set_ylim(-0.6, len(C) - 0.4)
    ax.set_yticks(range(len(C))); ax.set_yticklabels([textwrap.shorten(c["tema"], 62, placeholder="…") for c in C][::-1], fontsize=7)
    ax.set_xticks(range(1, m + 1)); ax.set_xticklabels(range(1, m + 1), fontsize=7); ax.set_xlabel("Mes de ejecución")
    ax.grid(axis="x", color="#EDEDED", linewidth=0.5); ax.set_axisbelow(True); ax.tick_params(length=0)
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=AZUL2), plt.Rectangle((0, 0), 1, 1, color="#9DC3E6")], ["Programada", "Inducción (cada ingreso de personal)"],
              frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    guardar(fig, ruta)


def main(carpeta):
    D = json.load(open(os.path.join(carpeta, "entregables", "_calc", "psst.json")))
    out = os.path.join(carpeta, "entregables", "_calc", "fig"); os.makedirs(out, exist_ok=True)
    for nombre, fn in [("f1_personal", f_personal), ("f2_calor", f_calor), ("f3_niveles", f_niveles), ("f4_procesos", f_procesos),
                       ("f5_organigrama", f_organigrama), ("f6_jerarquia", f_jerarquia), ("f7_emergencia", f_emergencia), ("f8_capacitacion", f_capacitacion)]:
        fn(D, os.path.join(out, nombre + ".png"))
    print(sorted(os.listdir(out)))


if __name__ == "__main__":
    main(sys.argv[1])
