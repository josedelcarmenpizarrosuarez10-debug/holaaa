# -*- coding: utf-8 -*-
"""Figuras del estudio de gestión de riesgos SM-107 (PNG en entregables_vial_sm107/_calc/fig)."""
import os, sys, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, ListedColormap
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import riesgos_sm107 as RS
import plano_riesgos_dxf as PL
CALC = RS.CALC; FIG = os.path.join(CALC, "fig"); os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
def nombre(t):
    pal = t.lower().replace("huanipo", "huañipo").replace("america", "américa").split()
    return " ".join(w if w in ("de", "la", "del") else (w.upper() if w.startswith("l=") else w.capitalize()) for w in pal).replace("L=", "L = ")


COL = {"R-INUNDACION": "#2870dc", "R-EROSION": "#dc00dc", "R-TALUDES": "#e60000", "R-RIEGO": "#008c8c", "R-PLATAFORMA": "#808080",
       "R-INTERFERENCIAS": "#00b400", "R-PREDIOS": "#e68200"}
NIV = {"ALTO": "#ff7c80", "MODERADO": "#ffd966", "BAJO": "#a9d08e"}


def fig_mapa():
    d = np.load(os.path.join(CALC, "dem_corredor.npz")); Z = d["Z"].astype(float); c, f, a, e = d["tr"]
    ext = [c, c + a * Z.shape[1], f + e * Z.shape[0], f]
    ls = LightSource(azdeg=315, altdeg=45); hs = ls.hillshade(np.nan_to_num(Z, nan=np.nanmean(Z)), vert_exag=3, dx=30, dy=30)
    X = PL.XYP
    fig, ax = plt.subplots(figsize=(10, 7.4))
    ax.imshow(Z, extent=ext, cmap="terrain", vmin=200, vmax=420, alpha=0.55)
    ax.imshow(hs, extent=ext, cmap="gray", alpha=0.35)
    pc = PL.EJE["prog0"] + PL.EJE["longitud_pc01_m"]; m = X[:, 2] <= pc
    ax.plot(X[m, 0], X[m, 1], color="#1f3b8c", lw=2.0, label="Eje de vía (PC-01)")
    ax.plot(X[~m, 0], X[~m, 1], color="#1f3b8c", lw=1.6, ls="--", label="Tramo 44+090 a 44+693 (referencial)")
    vistos = set()
    for capa, a_, b_, et, cod in sorted(PL.SECTORES, key=lambda s: s[0] != "R-PLATAFORMA"):
        T = np.array(PL.tramo(a_, b_))
        ax.plot(T[:, 0], T[:, 1], color=COL[capa], lw=3 if capa == "R-PLATAFORMA" else 5, solid_capstyle="butt",
                label=None if capa in vistos else {"R-INUNDACION": "Inundación / empozamiento (R-06)", "R-EROSION": "Erosión (R-05)",
                                                    "R-TALUDES": "Taludes inestables (R-04)", "R-RIEGO": "Canal de riego (R-12)",
                                                    "R-PLATAFORMA": "Plataforma angosta (R-20, R-27)"}[capa]); vistos.add(capa)
    for capa, pr, et, cod in PL.PUNTOS:
        p, _ = PL.pk(pr); ax.plot(*p, "o", color=COL[capa], ms=6, mec="k", mew=0.4,
                                  label=None if capa + "p" in vistos else ("Interferencia (R-11)" if capa == "R-INTERFERENCIAS" else
                                                                         ("Empozamiento sin descarga (R-06)" if capa == "R-INUNDACION" else "Cruce de canal (R-12)")))
        vistos.add(capa + "p")
    for nom, pr in PL.PUENTES:
        p, _ = PL.pk(pr); ax.plot(*p, marker="s", color="#e60000", ms=8, mec="k", mew=0.6, label=None if "pte" in vistos else "Puente a reemplazar (R-03, R-34)")
        vistos.add("pte")
        ax.annotate(nombre(nom.replace("PTE. ", "")), p, xytext=(8, -12), textcoords="offset points", fontsize=7, color="#7a0000")
    for nom, pr in PL.LOCALIDADES:
        p, _ = PL.pk(pr); ax.annotate(nombre(nom), p, xytext=(-10, 9), textcoords="offset points",
                                       fontsize=8, fontweight="bold")
    for k in range(20, 45, 2):
        p, _ = PL.pk(k * 1000.0); ax.plot(*p, "|", color="k", ms=8); ax.annotate("km %d" % k, p, xytext=(4, 4), textcoords="offset points", fontsize=6.5, color="#1f3b8c")
    ax.set_xlim(360500, 375600); ax.set_ylim(9222600, 9234000); ax.set_aspect("equal")
    ax.ticklabel_format(useOffset=False, style="plain"); ax.tick_params(labelsize=7)
    ax.set_xlabel("Este (m) - UTM WGS 84 zona 18 S"); ax.set_ylabel("Norte (m)")
    ax.legend(loc="upper right", fontsize=7, framealpha=0.9)
    ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "f1_mapa.png"), dpi=170); plt.close(fig)


def fig_perfil():
    T = PL.EJE["tramos_100m"]; x = np.array([(t["pi"] + t["pf"]) / 2 for t in T]) / 1000; z = np.array([t["z"] for t in T]); pm = np.array([t["pend_max_grados"] for t in T])
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 5.2), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    a1.plot(x, z, color="#5a3d1e", lw=1.2); a1.fill_between(x, 220, z, color="#d9c7a5", alpha=0.6); a1.set_ylim(225, 335); a1.set_ylabel("Cota (msnm)")
    for capa, a_, b_, et, cod in PL.SECTORES:
        if capa == "R-PLATAFORMA": continue
        a1.axvspan(a_ / 1000, b_ / 1000, color=COL[capa], alpha=0.35, lw=0)
    for nom, pr in PL.PUENTES: a1.axvline(pr / 1000, color="#e60000", lw=0.8, ls=":"); a1.text(pr / 1000, 330, nombre(nom.replace("PTE. ", "").split(" L")[0]), rotation=90, fontsize=6.5, va="top", ha="right")
    a1.grid(alpha=0.3); a1.set_title("Cota del terreno a lo largo del eje y sectores críticos del inventario (modelo Copernicus GLO-30, referencial)", fontsize=9)
    colors = np.where(pm >= 25, "#e64040", np.where(pm >= 15, "#f5be28", "#6eb45a"))
    a2.bar(x, pm, width=0.1, color=colors); a2.set_ylabel("Pendiente máx.\ndel entorno (°)"); a2.set_xlabel("Progresiva (km)")
    a2.axhline(15, color="#888", lw=0.6, ls="--"); a2.axhline(25, color="#888", lw=0.6, ls="--"); a2.grid(alpha=0.3)
    a2.set_xlim(19.3, 44.75)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "f2_perfil.png"), dpi=170); plt.close(fig)


def fig_lluvia():
    L = json.load(open(os.path.join(CALC, "lluvia_ghcn.json")))
    m = np.arange(1, 13); t = [L["Tarapoto"]["meses"][str(i)][0] for i in m]; j = [L["Juanjuí"]["meses"][str(i)][0] for i in m]; pr = (np.array(t) + np.array(j)) / 2
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.bar(m - 0.2, t, 0.4, label="Tarapoto (1,020 mm/año)", color="#7fb3d5"); ax.bar(m + 0.2, j, 0.4, label="Juanjuí (1,471 mm/año)", color="#2e86c1")
    ax.plot(m, pr, "k-o", ms=3, lw=1, label="Promedio")
    for i, v in zip(m, pr):
        ax.axvspan(i - 0.5, i + 0.5, color="#ff7c80" if v >= 110 else ("#ffd966" if v >= 75 else "#a9d08e"), alpha=0.18, lw=0)
    ax.set_xticks(m); ax.set_xticklabels(["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"])
    ax.set_ylabel("Lluvia media mensual (mm)"); ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)
    ax.set_title("Lluvia mensual de referencia (NOAA GHCN-Daily). Fondo: rojo lluviosa, ámbar transición, verde estiaje", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "f3_lluvia.png"), dpi=170); plt.close(fig)


def fig_calor():
    RS.calcular()
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, kp, tit in zip(axs, ("p", "pr"), ("Inherente (antes de la respuesta)", "Residual (con la respuesta ejecutada)")):
        for i in range(5):
            for j in range(5):
                v = RS.PROB[i][1] * RS.IMP[j][1]
                col = NIV["ALTO"] if v >= RS.UMBRAL_ALTO - 1e-9 else (NIV["MODERADO"] if v >= RS.UMBRAL_MOD - 1e-9 else NIV["BAJO"])
                ax.add_patch(plt.Rectangle((j, i), 1, 1, color=col, ec="white", lw=2))
                cods = [r["cod"].replace("R-", "") for r in RS.R if r[kp] == i and r["i"] == j]
                lineas = [", ".join(cods[k:k + 4]) for k in range(0, len(cods), 4)]
                ax.text(j + 0.5, i + 0.5, "\n".join(lineas), ha="center", va="center", fontsize=7)
        ax.set_xlim(0, 5); ax.set_ylim(0, 5); ax.set_xticks(np.arange(5) + 0.5); ax.set_yticks(np.arange(5) + 0.5)
        ax.set_xticklabels([t + "\n%.2f" % v for t, v in RS.IMP], fontsize=7); ax.set_yticklabels([t + "  %.1f" % v for t, v in RS.PROB], fontsize=7)
        ax.set_xlabel("Impacto"); ax.set_ylabel("Probabilidad"); ax.set_title(tit, fontsize=9)
    fig.suptitle("Ubicación de los riesgos en la matriz P x I (números = código R-xx)", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "f4_calor.png"), dpi=170); plt.close(fig)


def fig_mc():
    MC = json.load(open(os.path.join(CALC, "riesgos.json")))["montecarlo"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.9))
    for k, col, et in (("inherente", "#c0504d", "Inherente"), ("residual", "#4f81bd", "Residual")):
        s = np.array(MC[k]["muestras_entidad"]) / 1e6; a1.plot(s, np.linspace(0, 100, len(s)), color=col, lw=1.6, label=et)
        p80 = MC[k]["entidad"]["80"] / 1e6; a1.axvline(p80, color=col, ls="--", lw=0.8); a1.text(p80, 5, " P80 = %.2f" % p80, color=col, fontsize=7)
        s = np.array(MC[k]["muestras_dias"]); a2.plot(s, np.linspace(0, 100, len(s)), color=col, lw=1.6, label=et)
        d80 = MC[k]["dias"]["80"]; a2.axvline(d80, color=col, ls="--", lw=0.8); a2.text(d80, 5, " P80 = %d d" % d80, color=col, fontsize=7)
    a1.set_xlabel("Costo para la Entidad (S/ millones)"); a1.set_ylabel("Probabilidad acumulada (%)"); a1.grid(alpha=0.3); a1.legend(fontsize=8)
    a2.set_xlabel("Retraso total de la obra (días)"); a2.grid(alpha=0.3); a2.legend(fontsize=8)
    fig.suptitle("Simulación de Monte Carlo (20,000 iteraciones): curvas de probabilidad acumulada", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "f5_montecarlo.png"), dpi=170); plt.close(fig)


if __name__ == "__main__":
    fig_mapa(); fig_perfil(); fig_lluvia(); fig_calor(); fig_mc(); print(sorted(os.listdir(FIG)))
