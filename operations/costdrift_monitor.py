#!/usr/bin/env python3
"""Kostendrift-Überwachung mit Trennschärfe: Simulation der Auslösezeit (§14.2, EV-07; Modell MOD-DRIFT).

Messgröße je Fill: Verhältnis gemessene Kosten (Implementation Shortfall) / Modellkosten aus financials/cost_model_results.json.
Schätzung: gepoolt über alle Instrumente (Normalmodell, flacher Prior) und je Instrument mit Schrumpfung zum Pool (Pseudo-Fills
P-MON-COSTDRIFT-SHRINK). Auslösung, wenn P(Verhältnis > P-MON-COSTDRIFT-RATIO) > P-MON-COSTDRIFT-PROB.
Fill-Frequenz aus der Umschlagssimulation und dem Referenzuniversum (U-BREAKEVEN, Referenzstufe). Streuung je Fill: P-MON-FILL-NOISE.
Vergleich: v2.0-Verfahren je Instrument ohne Pooling mit mindestens 20 Fills.
Aufruf: python operations/costdrift_monitor.py [--check]
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.calc import Params, Rng, dumps, input_hashes, load, main_args, norm_ppf, quantile, write_or_check  # noqa: E402

OUT = "operations/costdrift_results.json"
SEED = 14_2_2026
RUNS = 1000
MAX_MONTHS = 36


def lower_bound_exceeds(mean: float, n_eff: float, sd: float, z: float, thr: float) -> bool:
    """Auslöseregel des Monitors: untere Konfidenzgrenze des Kostenverhältnisses liegt über der Schwelle. Bei Normalannahme gleichwertig mit
    P(Verhältnis > Schwelle) = Φ((mean − thr)·√n/sd) > P-MON-COSTDRIFT-PROB, wenn z = Φ⁻¹(P-MON-COSTDRIFT-PROB)."""
    return mean - z * sd / math.sqrt(n_eff) > thr


def simulate(ratio, fills_per_month_per_ins, n_ins, P, rng, pooled=True, min_fills_unpooled=20):
    thr, prob = P.f("P-MON-COSTDRIFT-RATIO"), P.f("P-MON-COSTDRIFT-PROB")
    kappa = P.f("P-MON-COSTDRIFT-SHRINK")
    sd = P.f("P-MON-FILL-NOISE")
    z = norm_ppf(prob)
    months = []
    for _ in range(RUNS):
        sums = [0.0] * n_ins
        cnt = [0] * n_ins
        hit = None
        for m in range(1, MAX_MONTHS + 1):
            for i in range(n_ins):
                k = rng.poisson(fills_per_month_per_ins)
                for _ in range(k):
                    sums[i] += ratio + sd * rng.normal()
                cnt[i] += k
            N = sum(cnt)
            if N == 0:
                continue
            pool = sum(sums) / N
            if pooled:
                if lower_bound_exceeds(pool, N, sd, z, thr):
                    hit = m
                    break
                for i in range(n_ins):
                    if cnt[i] == 0:
                        continue
                    shr = (sums[i] + kappa * pool) / (cnt[i] + kappa)
                    if lower_bound_exceeds(shr, cnt[i] + kappa, sd, z, thr):
                        hit = m
                        break
                if hit:
                    break
            else:
                if any(cnt[i] >= min_fills_unpooled and lower_bound_exceeds(sums[i] / cnt[i], cnt[i], sd, z, thr) for i in range(n_ins)):
                    hit = m
                    break
        months.append(hit if hit is not None else MAX_MONTHS + 1)
    s = sorted(months)
    return {"median_months": quantile(s, 0.5), "p90_months": quantile(s, 0.9),
            "p_trigger_within_pilot": sum(1 for x in months if x <= P.f("P-RES-PILOT-MONTHS")) / RUNS,
            "p_trigger_within_24m": sum(1 for x in months if x <= 24) / RUNS, "never_within_36m": sum(1 for x in months if x > MAX_MONTHS) / RUNS}


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    turn = load("research/turnover_results.json")["strategies"]["S-TF"]
    prior = load("research/prior_results.json")
    st = str(P("P-RISK-STRESS-REF-STAGE"))
    ins = prior["admission"]["U-BREAKEVEN"][st]["instruments"]
    cm = {r["id"]: r for r in load("financials/cost_model_results.json")["instruments"]}
    rt = sum(cm[i]["strategies"]["S-TF"]["rt_per_year"] for i in ins) / len(ins)
    fpm = 2 * rt / 12
    rng = Rng(SEED)
    # Szenarien des wahren Kostenverhältnisses (gemessen/Modell): ohne Drift, genau auf der Auslöseschwelle, 1,5-fach, 2-fach
    grid = {"OHNE_DRIFT": 1.0, "AN_SCHWELLE": P.f("P-MON-COSTDRIFT-RATIO"), "FAKTOR_1_5": 1.5, "FAKTOR_2": 2.0}
    res = {"pooled": {}, "v2_unpooled_min20": {}}
    for name, r in grid.items():
        res["pooled"][name] = {"true_ratio": r, **simulate(r, fpm, len(ins), P, rng, pooled=True)}
    for name in ("FAKTOR_1_5", "FAKTOR_2"):
        res["v2_unpooled_min20"][name] = {"true_ratio": grid[name], **simulate(grid[name], fpm, len(ins), P, rng, pooled=False)}
    v2_fills = 2 * load("research/turnover_results.json")["strategies"]["S-BASE-TFD1"]["round_turns_per_year"] / 12
    res["v2_frequency_unpooled_min20"] = {"FAKTOR_2": {"true_ratio": grid["FAKTOR_2"], **simulate(grid["FAKTOR_2"], v2_fills, len(ins), P, rng, pooled=False)}}
    out = {"calculator": "operations/costdrift_monitor.py", "model": "MOD-DRIFT", "seed": SEED, "runs": RUNS,
           "inputs": input_hashes(["parameters.json", "research/turnover_results.json", "research/prior_results.json", "financials/cost_model_results.json"]),
           "reference": {"instruments": len(ins), "round_turns_per_year_per_instrument": rt, "fills_per_month_per_instrument": fpm,
                         "time_in_market": turn["time_in_market"], "v2_like_fills_per_month_per_instrument": v2_fills},
           "results": res, "pilot_months": P.f("P-RES-PILOT-MONTHS")}
    ok = write_or_check(OUT, dumps(out), a.check)
    if not a.check:
        print("Fills je Monat und Instrument:", round(fpm, 1))
        for k, v in res.items():
            for r, x in v.items():
                print(f"{k:<28} Verhältnis {r}: Median {x['median_months']} Monate, P(im Pilot) {x['p_trigger_within_pilot']:.3f}, P(≤24 M) {x['p_trigger_within_24m']:.3f}")
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
