"""Tapa vehicular de las cunetas en estacionamientos y accesos (regla del proyectista: en estacionamiento nunca hay rejilla,
siempre cuneta tapada, diseñada para que pasen camiones).

Carga: rueda del camión de diseño HL-93 del Manual de Puentes del MTC, P = 72.5 kN (eje de 145 kN), incremento por carga
dinámica 33 % y factor de carga 1.75 (Resistencia I): Pu = 1.75 · 1.33 · 72.5 kN. Huella de la llanta 0.51 m × 0.25 m.
Losa simplemente apoyada sobre los muros de la cuneta, luz L = ancho libre + espesor de muro; la rueda en el centro:
Mu = Pu · L / 4 repartido en el ancho de la huella más dos veces el espesor (reparto a 45°). Flexión con φ = 0.90, corte por
punzonamiento alrededor de la huella con φVc = 0.75 · 0.33 · √f'c · b0 · d (MPa). Acero mínimo 0.0018 · h (E.060).
"""
import math

RUEDA_KN = 72.5
IM = 1.33
FC_CARGA = 1.75
HUELLA = (0.51, 0.25)
BARRAS = {"3/8\"": (0.71, 0.952), "1/2\"": (1.29, 1.27), "5/8\"": (2.00, 1.588)}   # área cm², diámetro cm


def disenar(b_libre, P, fc=28.0, fy=420.0, recub=0.04):
    """Espesor y acero de la tapa vehicular para un ancho libre b (m). fc y fy en MPa (280 y 4200 kg/cm²)."""
    L = b_libre + P["e_muro"]
    Pu = FC_CARGA * IM * RUEDA_KN
    for h in [0.15, 0.20, 0.25, 0.30]:
        for barra in ("1/2\"", "5/8\""):
            ab, db = BARRAS[barra]; d = h - recub - db / 200.0
            Ew = HUELLA[0] + 2 * h
            Mu = Pu * L / 4.0 / Ew                              # kN·m por metro de ancho
            # As de la ecuación de flexión: Mu = φ As fy (d − a/2), a = As fy / (0.85 f'c)
            phi = 0.9; k = Mu / 1000.0 / phi                    # MN·m
            disc = d * d - 2 * k / (0.85 * fc)
            if disc <= 0: continue
            a = d - math.sqrt(disc); As = 0.85 * fc * a / fy    # m² por m
            As_min = 0.0018 * h
            As_d = max(As, As_min) * 1e4                        # cm²/m
            s = math.floor(min(ab / As_d, 0.20 if h < 0.20 else 0.25, 3 * h) / 0.025 + 1e-9) * 0.025
            if s < 0.10: continue
            b0 = 2 * (HUELLA[0] + d) + 2 * (HUELLA[1] + d)
            phiVc = 0.75 * 0.33 * math.sqrt(fc) * b0 * d * 1000.0    # kN
            if phiVc < Pu: continue
            return {"h": h, "luz": round(L, 3), "Pu_kN": round(Pu, 1), "Mu_kNm_m": round(Mu, 2), "d": round(d, 3), "As_cm2_m": round(As_d, 2),
                    "barra": barra, "sep": round(s, 3), "acero": "Ø %s @ %.3f m en ambos sentidos (abajo)" % (barra, s),
                    "phiVc_kN": round(phiVc, 1), "fc_kgcm2": 280, "kg_m2": round(2 * (1 / s) * ab * 100 * 0.785 / 100, 2),
                    "texto": "Losa de concreto armado f'c = 280 kg/cm², e = %.2f m, %s; rueda HL-93 (MTC) %.1f kN con IM 33 %% y factor 1.75: "
                             "Mu = %.2f kN·m/m, φVc = %.0f kN ≥ Pu = %.0f kN." % (h, "Ø %s @ %.3f m" % (barra, s), RUEDA_KN, Mu, phiVc, Pu)}
    raise ValueError("No se encontró un espesor de tapa vehicular hasta 0.30 m para un ancho libre de %.2f m." % b_libre)
