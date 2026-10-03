#!/usr/bin/env python3
"""Auslösezeiten der Monitore MON-HARM und MON-DRIFT (Volatilität) (§14.2, §16; Modell MOD-MON).

MON-HARM (Regel MH-R1): Posterior P(Netto-Sharpe < 0) ≥ P-MON-HARM-SR, monatlich ausgewertet. Normal-Normal-Modell wie in
research/operating_characteristics.py: registrierter Prior (Mittel m0, Streuung s0), Schätzer der Sharpe-Ratio nach T Jahren ~ N(S, 1/√T).
Simuliert werden Monatsrenditen in Einheiten der Jahresvolatilität, r ~ N(S/12, 1/12); nach m Monaten ist Ŝ = Σr / (m/12).
Die Futility-Regel MH-R2 ist nicht simuliert (sie setzt die Endtor-Kette voraus).
MON-DRIFT (Regel MD-R3): realisierte Volatilität über P-MON-VOL-WINDOW-D Handelstage / Zielvolatilität weicht um mehr als P-MON-VOL-BAND ab;
täglich ausgewertet. Tagesrenditen t-verteilt mit P-SIM-T-DF Freiheitsgraden (Varianz 1); das Fenster ist zu Beginn mit Renditen ohne Drift
gefüllt, ab dem ersten Tag gilt das wahre Verhältnis. Ergebnis: Fehlalarme ohne Drift und Erkennungszeit nach einem Volatilitätssprung.
Aufruf: python operations/monitor_simulation.py [--check]
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.calc import Params, Rng, dumps, input_hashes, load, main_args, norm_cdf, quantile, write_or_check  # noqa: E402

OUT = "operations/monitor_results.json"
SEED = 14_2_2027
RUNS = 1000
HARM_MAX_MONTHS = 120          # zehn Jahre Standardbetrieb
DRIFT_DAYS = 252               # ein Jahr Handelstage
DESIGN_WINDOWS = (63, 126)     # Vergleich für die Wahl von P-MON-VOL-WINDOW-D und P-MON-VOL-BAND
DESIGN_BANDS = (0.3, 0.4, 0.5)
DESIGN_RUNS = 500


def harm_posterior_negative(s_hat: float, years: float, m0: float, s0: float) -> float:
    """P(S < 0 | Daten) im Normal-Normal-Modell: Präzision 1/s0² + T, Mittel (m0/s0² + Ŝ·T) / Präzision."""
    prec = 1.0 / (s0 * s0) + years
    mean = (m0 / (s0 * s0) + s_hat * years) / prec
    return norm_cdf(-mean * math.sqrt(prec))


def harm_threshold_s_hat(years: float, m0: float, s0: float, prob: float, z: float) -> float:
    """Größtes Ŝ, bei dem MH-R1 nach T Jahren auslöst: −mean·√prec ≥ z  ⇔  Ŝ ≤ −(z·√prec + m0/s0²) / T (z = Φ⁻¹(prob))."""
    prec = 1.0 / (s0 * s0) + years
    return -(z * math.sqrt(prec) + m0 / (s0 * s0)) / years


def simulate_harm(true_s: float, P, prior, rng) -> dict:
    prob = P.f("P-MON-HARM-SR")
    m0, s0 = prior["mean"], prior["sd"]
    months = []
    for _ in range(RUNS):
        x, hit = 0.0, None
        for m in range(1, HARM_MAX_MONTHS + 1):
            x += true_s / 12 + rng.normal() / math.sqrt(12)
            years = m / 12
            if harm_posterior_negative(x / years, years, m0, s0) >= prob:
                hit = m
                break
        months.append(hit if hit is not None else HARM_MAX_MONTHS + 1)
    s = sorted(months)
    n = len(months)
    return {"true_sharpe": true_s, "median_months": quantile(s, 0.5),
            "p_trigger_within_pilot": sum(1 for v in months if v <= P.f("P-RES-PILOT-MONTHS")) / n,
            "p_trigger_within_24m": sum(1 for v in months if v <= 24) / n,
            "p_trigger_within_60m": sum(1 for v in months if v <= 60) / n,
            "p_never_within_horizon": sum(1 for v in months if v > HARM_MAX_MONTHS) / n}


def simulate_vol_drift(ratio: float, P, rng, win=None, band=None, runs=RUNS) -> dict:
    win = int(P("P-MON-VOL-WINDOW-D")) if win is None else win
    band = P.f("P-MON-VOL-BAND") if band is None else band
    df = int(P("P-SIM-T-DF"))
    days = []
    for _ in range(runs):
        # Vorlauf: Fenster mit Renditen ohne Drift füllen; ab Tag 1 gilt das wahre Verhältnis, täglich ausgewertet
        buf = [rng.student_t4_unit() if df == 4 else rng.student_t_unit(df) for _ in range(win)]
        s1, s2, hit = sum(buf), sum(x * x for x in buf), None
        for d in range(1, DRIFT_DAYS + 1):
            r = ratio * (rng.student_t4_unit() if df == 4 else rng.student_t_unit(df))
            old = buf.pop(0)
            buf.append(r)
            s1 += r - old
            s2 += r * r - old * old
            var = max(0.0, (s2 - s1 * s1 / win) / (win - 1))
            if abs(math.sqrt(var) - 1.0) > band:
                hit = d
                break
        days.append(hit if hit is not None else DRIFT_DAYS + 1)
    s = sorted(days)
    n = len(days)
    return {"true_ratio": ratio, "window_days": win, "band": band, "median_days": quantile(s, 0.5), "p_trigger_within_20d": sum(1 for v in days if v <= 20) / n,
            "p_trigger_within_63d": sum(1 for v in days if v <= 63) / n, "p_trigger_within_252d": sum(1 for v in days if v <= DRIFT_DAYS) / n}


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    oc = load("research/operating_characteristics_results.json")
    prior = oc["priors"][oc["priors"]["registered"]]
    rng = Rng(SEED)
    harm = {}
    for name, s in (("SCHAEDLICH", P.f("P-RES-SR-HARMFUL")), ("STARK_SCHAEDLICH", P.f("P-OC-HARM-SCREEN")), ("WERTLOS", 0.0),
                    ("BRAUCHBAR", P.f("P-RES-SR-USEFUL"))):
        harm[name] = simulate_harm(s, P, prior, rng)
    vol = {name: simulate_vol_drift(r, P, rng) for name, r in (("OHNE_DRIFT", 1.0), ("FAKTOR_1_5", 1.5), ("FAKTOR_2", 2.0))}
    # Auslegung von Fenster und Band: Fehlalarme ohne Drift gegen Erkennung einer Verdopplung (Grundlage der Parameterwahl)
    grid = []
    for win in DESIGN_WINDOWS:
        for band in DESIGN_BANDS:
            f = simulate_vol_drift(1.0, P, rng, win, band, DESIGN_RUNS)
            d2 = simulate_vol_drift(2.0, P, rng, win, band, DESIGN_RUNS)
            grid.append({"window_days": win, "band": band, "false_alarm_within_252d": f["p_trigger_within_252d"],
                         "doubling_median_days": d2["median_days"], "doubling_within_63d": d2["p_trigger_within_63d"]})
    out = {"calculator": "operations/monitor_simulation.py", "model": "MOD-MON", "seed": SEED, "runs": RUNS,
           "inputs": input_hashes(["parameters.json", "research/operating_characteristics_results.json"]),
           "harm_prior": {"name": oc["priors"]["registered"], **prior}, "harm_max_months": HARM_MAX_MONTHS, "harm": harm,
           "vol_window_days": int(P("P-MON-VOL-WINDOW-D")), "vol_band": P.f("P-MON-VOL-BAND"), "vol_horizon_days": DRIFT_DAYS, "vol_drift": vol,
           "vol_design_grid": grid, "vol_design_runs": DESIGN_RUNS,
           "not_simulated": ["MH-R2 (Futility im Betrieb)", "MD-R1 (Höchsthaltedauer: löst sofort aus)", "MD-R2 (Umschlag)"]}
    ok = write_or_check(OUT, dumps(out), a.check)
    if not a.check:
        for k, v in harm.items():
            print(f"MON-HARM {k:<17} S={v['true_sharpe']:+.2f}: Median {v['median_months']} Monate, P(≤24 M) {v['p_trigger_within_24m']:.3f}, "
                  f"nie in {HARM_MAX_MONTHS} M {v['p_never_within_horizon']:.3f}")
        for k, v in vol.items():
            print(f"MON-DRIFT Vola {k:<11}: Median {v['median_days']} Tage, P(≤63 T) {v['p_trigger_within_63d']:.3f}, P(≤252 T) {v['p_trigger_within_252d']:.3f}")
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
