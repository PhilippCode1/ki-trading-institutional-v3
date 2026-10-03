#!/usr/bin/env python3
"""Betriebscharakteristik der Tore mit und ohne Futility-Regel (§6.6, §16, EV-05; Modell MOD-OC).

Simuliert Strategien bekannter wahrer Netto-Sharpe (schädlich, wertlos, brauchbar; parameters.json) durch die registrierten Tore:
  G3  Entwicklungsdaten (P-RES-DEV-YEARS): beste von N_eff Varianten; Bestehen, wenn der deflationierte Test PSR(SR0) ≥ P-RES-DSR-MIN
      (SR0 = erwartetes Maximum von P-OC-TRIALS Versuchen ohne Edge)
  G4  Holdout (P-RES-HOLDOUT-YEARS): Bestehen, wenn geschätzte Sharpe > 0
  G5/G6  Bau und Drills (Kosten)
  G7/G8  Paper und Pilot (je P-RES-*-MONTHS): Harm-Screen (P-OC-HARM-SCREEN)
  Endtor: Posterior P(Sharpe > 0) ≥ P-RES-FINAL-P aus Prior (P-OC-PRIOR-MODE), deflationierter Entwicklung (Varianz × P-OC-DEV-VAR-FACTOR), Holdout,
          Paper und Pilot
Futility (DEC-DS-21): nach G3 und G4 prädiktive Wahrscheinlichkeit, das Endtor zu bestehen (geschlossene Normal-Normal-Form); unter
P-RES-FUTILITY → Stopp vor den teuren Stufen. Gemeinsame Zufallszahlen für alle Varianten (faire Vergleiche).
Ausgewiesen: Anteile je Stufe und Klasse, erwartete Kosten, eingesparte Kosten; Sensitivität für DSR-Schwelle und Prior.
Aufruf: python research/operating_characteristics.py [--check]
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from financials.stage_costs import stage_costs  # noqa: E402
from lib.calc import Params, Rng, dec, dumps, input_hashes, load, main_args, money, norm_cdf, norm_ppf, write_or_check  # noqa: E402
from research.statistical_calculator import expected_max_sr, lo_se  # noqa: E402

OUT = "research/operating_characteristics_results.json"
SEED = 6_6_2026
ORDER = ["BS-00", "BS-01", "BS-02", "BS-03", "BS-04", "BS-05", "BS-06", "BS-07", "BS-08"]


def e_max_std_normal(n: int) -> float:
    g = 0.5772156649015329
    return (1 - g) * norm_ppf(1 - 1 / n) + g * norm_ppf(1 - 1 / (n * math.e))


def combine(m, v, x, vx):
    w = 1 / v + 1 / vx
    return (m / v + x / vx) / w, 1 / w


def predictive_pass(m, v, var_future, z_final):
    """P(Endposterior besteht) bei künftigen, unverzerrten Daten mit Varianz var_future (Normal-Normal)."""
    vf = 1 / (1 / v + 1 / var_future)
    thr = (z_final * math.sqrt(vf) / vf - m / v) * var_future
    return 1 - norm_cdf((thr - m) / math.sqrt(v + var_future))


def draws(n, n_eff, rng):
    """Standardnormale Ziehungen je Strategie: n_eff Entwicklungsvarianten, Holdout, Paper, Pilot (gemeinsame Zufallszahlen)."""
    return [([rng.normal() for _ in range(n_eff)], rng.normal(), rng.normal(), rng.normal()) for _ in range(n)]


def run(s, Z, P, prior_m, prior_v, futility: bool, dsr_min: float):
    T_dev, T_ho = P.f("P-RES-DEV-YEARS"), P.f("P-RES-HOLDOUT-YEARS")
    T_pa, T_pi = P.f("P-RES-PAPER-MONTHS") / 12, P.f("P-RES-PILOT-MONTHS") / 12
    n_trials, n_eff = int(P("P-OC-TRIALS")), int(P("P-OC-NEFF"))
    z_dsr, z_final = norm_ppf(dsr_min), norm_ppf(P.f("P-RES-FINAL-P"))
    fut, harm = P.f("P-RES-FUTILITY"), P.f("P-OC-HARM-SCREEN")
    dev_var = P.f("P-OC-DEV-VAR-FACTOR")
    se_dev, se_ho, se_pa, se_pi = lo_se(s, T_dev), lo_se(s, T_ho), lo_se(s, T_pa), lo_se(s, T_pi)
    sr0 = expected_max_sr(se_dev ** 2, n_trials)
    bias = se_dev * e_max_std_normal(n_eff)
    c = {"passed_G3": 0, "stopped_futility_G3": 0, "passed_G4": 0, "stopped_futility_G4": 0, "reached_G5_build": 0, "passed_G7": 0,
         "passed_G8": 0, "accepted_final": 0}
    last = {}

    def stop(stage):
        last[stage] = last.get(stage, 0) + 1

    for dev, zh, zp, zq in Z:
        obs = max(s + se_dev * z for z in dev)
        if (obs - sr0) / se_dev < z_dsr:
            stop("BS-03")
            continue
        c["passed_G3"] += 1
        m, v = combine(prior_m, prior_v, obs - bias, dev_var * se_dev ** 2)
        if futility and predictive_pass(m, v, 1 / (T_ho + T_pa + T_pi), z_final) < fut:
            c["stopped_futility_G3"] += 1
            stop("BS-03")
            continue
        ho = s + se_ho * zh
        if ho <= 0:
            stop("BS-04")
            continue
        c["passed_G4"] += 1
        m, v = combine(m, v, ho, se_ho ** 2)
        if futility and predictive_pass(m, v, 1 / (T_pa + T_pi), z_final) < fut:
            c["stopped_futility_G4"] += 1
            stop("BS-04")
            continue
        c["reached_G5_build"] += 1
        pa = s + se_pa * zp
        if pa < harm:
            stop("BS-07")
            continue
        c["passed_G7"] += 1
        pi = s + se_pi * zq
        if pi < harm:
            stop("BS-08")
            continue
        c["passed_G8"] += 1
        m, v = combine(m, v, pa, se_pa ** 2)
        m, v = combine(m, v, pi, se_pi ** 2)
        if m / math.sqrt(v) >= z_final:
            c["accepted_final"] += 1
        stop("BS-08")
    n = len(Z)
    return {k: x / n for k, x in c.items()}, last


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    prior = load("research/prior_results.json")
    st = str(P("P-RISK-STRESS-REF-STAGE"))
    pf = prior["portfolio"]["U-BREAKEVEN"][st]["S-TF"]
    lit_m, lit_sd = pf["mean"], (pf["p95"] - pf["p05"]) / (2 * 1.6448536269514722)
    sk_sd = P.f("P-OC-PRIOR-SD")
    priors = {"SKEPTISCH": (0.0, sk_sd ** 2), "LITERATUR": (lit_m, lit_sd ** 2)}
    reg_prior = P("P-OC-PRIOR-MODE")
    classes = {"SCHAEDLICH": P.f("P-RES-SR-HARMFUL"), "WERTLOS": 0.0, "BRAUCHBAR": P.f("P-RES-SR-USEFUL")}
    n = int(P("P-RES-OC-STRATEGIES"))
    costs = stage_costs()
    cum, tot = {}, dec(0)
    for sid in ORDER:
        tot += dec(costs[sid]["total_eur"])
        cum[sid] = tot
    rng = Rng(SEED)
    Zc = {c: draws(n, int(P("P-OC-NEFF")), rng) for c in classes}

    def evaluate(prior_mode, dsr_min):
        pm, pv = priors[prior_mode]
        out = {}
        for cname, s in classes.items():
            out[cname] = {"true_sharpe": s}
            for mode in ("ohne_futility", "mit_futility"):
                rates, last = run(s, Zc[cname], P, pm, pv, mode == "mit_futility", dsr_min)
                out[cname][mode] = {"rates": rates, "expected_cost_eur": money(sum(cum[k] * dec(v) for k, v in last.items()) / n)}
            out[cname]["saved_cost_eur_per_strategy"] = money(dec(out[cname]["ohne_futility"]["expected_cost_eur"])
                                                              - dec(out[cname]["mit_futility"]["expected_cost_eur"]))
        return out

    registered = evaluate(reg_prior, P.f("P-RES-DSR-MIN"))
    sens = {}
    for pmode in ("SKEPTISCH", "LITERATUR"):
        for dmin in [P.f("P-RES-DSR-MIN")] + list(P("P-OC-DSR-SENS")):
            key = f"{pmode}|DSR{dmin}"
            if pmode == reg_prior and dmin == P.f("P-RES-DSR-MIN"):
                continue
            sens[key] = evaluate(pmode, dmin)
    out = {"calculator": "research/operating_characteristics.py", "model": "MOD-OC", "seed": SEED, "strategies_per_class": n,
           "inputs": input_hashes(["parameters.json", "research/prior_results.json", "implementation/build_stages.json", "financials/cost_model_results.json"]),
           "priors": {"SKEPTISCH": {"mean": 0.0, "sd": sk_sd}, "LITERATUR": {"mean": lit_m, "sd": lit_sd},
                      "source": f"research/prior_results.json#/portfolio/U-BREAKEVEN/{st}/S-TF", "registered": reg_prior},
           "registered_dsr_min": P.f("P-RES-DSR-MIN"), "cumulative_cost_eur": {k: money(v) for k, v in cum.items()},
           "v2_reference": "v2.0: Strategie ohne Edge bestand E1 und E2 zu etwa 89 % (EV-05)",
           "registered": registered, "sensitivity": sens}
    ok = write_or_check(OUT, dumps(out), a.check)
    if not a.check:
        for label, res in [("REGISTRIERT", registered)] + list(sens.items()):
            for c, r in res.items():
                for mode in ("ohne_futility", "mit_futility"):
                    x = r[mode]["rates"]
                    print(f"{label:<22}{c:<11}{mode:<14} G3 {x['passed_G3']:.3f} Bau {x['reached_G5_build']:.3f} G8 {x['passed_G8']:.3f} "
                          f"Endtor {x['accepted_final']:.3f} Kosten {r[mode]['expected_cost_eur']}")
                print(f"{'':<33}eingespart je Strategie {r['saved_cost_eur_per_strategy']}")
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
