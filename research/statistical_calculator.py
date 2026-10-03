#!/usr/bin/env python3
"""Statistikrechner des Forschungsprotokolls (§6.4, Anhang A; Modell MOD-STAT).

Referenzimplementierungen (nur Standardbibliothek):
  * Standardfehler der Sharpe-Ratio (Lo 2002): SE ≈ √((1 + S²/2)/T)
  * Teststärke: T = ((z_{1−α} + z_{1−β}) / S)²
  * Probabilistic Sharpe Ratio und Deflated Sharpe Ratio (Bailey/López de Prado 2014) – geprüft gegen das Zahlenbeispiel der Quelle
  * Probability of Backtest Overfitting über CSCV (Bailey, Borwein, López de Prado, Zhu)
  * Reality Check (White 2000) und SPA-Test (Hansen 2005) mit stationärem Bootstrap
  * Romano-Wolf-Stepdown (2005) für mehrere Strategien gegen eine Benchmark
Die Demonstrationen laufen auf synthetischen Daten mit festen Seeds (R-02: keine Aussage über reale Strategien).
Aufruf: python research/statistical_calculator.py [--check]
"""
from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.calc import Params, Rng, dumps, input_hashes, main_args, mean, norm_cdf, norm_ppf, stdev, write_or_check  # noqa: E402

OUT = "research/statistical_results.json"
EULER_GAMMA = 0.5772156649015329


# ------------------------------------------------------------------------------------------------ Sharpe-Statistik
def lo_se(sr: float, years: float) -> float:
    return math.sqrt((1 + sr * sr / 2) / years)


def years_for_power(sr: float, alpha: float, power: float) -> float:
    return ((norm_ppf(1 - alpha) + norm_ppf(power)) / sr) ** 2


def psr(sr_hat: float, sr_star: float, n: int, skew: float, kurt: float) -> float:
    """Probabilistic Sharpe Ratio; sr_hat, sr_star je Periode (nicht annualisiert), kurt = Kurtosis (nicht Exzess)."""
    den = math.sqrt(1 - skew * sr_hat + (kurt - 1) / 4 * sr_hat * sr_hat)
    return norm_cdf((sr_hat - sr_star) * math.sqrt(n - 1) / den)


def expected_max_sr(var_sr: float, n_trials: int) -> float:
    """Erwartetes Maximum von n_trials Sharpe-Schätzungen ohne Edge (Anhang A)."""
    return math.sqrt(var_sr) * ((1 - EULER_GAMMA) * norm_ppf(1 - 1 / n_trials) + EULER_GAMMA * norm_ppf(1 - 1 / (n_trials * math.e)))


def dsr(sr_hat: float, n: int, skew: float, kurt: float, var_sr: float, n_trials: int) -> float:
    return psr(sr_hat, expected_max_sr(var_sr, n_trials), n, skew, kurt)


def sharpe(v) -> float:
    s = stdev(v)
    return mean(v) / s if s > 0 else 0.0


# ------------------------------------------------------------------------------------------------ PBO über CSCV
def pbo_cscv(matrix, blocks: int = 8) -> dict:
    """matrix: Liste von T Zeilen mit N Strategierenditen. Liefert PBO und Logit-Verteilung."""
    T, N = len(matrix), len(matrix[0])
    size = T // blocks
    parts = [list(range(b * size, (b + 1) * size)) for b in range(blocks)]
    lambdas = []
    for combo in itertools.combinations(range(blocks), blocks // 2):
        is_rows = [r for b in combo for r in parts[b]]
        oos_rows = [r for b in range(blocks) if b not in combo for r in parts[b]]
        sr_is = [sharpe([matrix[r][j] for r in is_rows]) for j in range(N)]
        sr_oos = [sharpe([matrix[r][j] for r in oos_rows]) for j in range(N)]
        best = max(range(N), key=lambda j: (sr_is[j], -j))
        rank = sum(1 for j in range(N) if sr_oos[j] <= sr_oos[best])
        w = rank / (N + 1)
        lambdas.append(math.log(w / (1 - w)))
    return {"pbo": sum(1 for x in lambdas if x <= 0) / len(lambdas), "combinations": len(lambdas), "logit_mean": mean(lambdas)}


# ------------------------------------------------------------------------------------------------ Bootstrap-Tests
def stationary_bootstrap_indices(T: int, block: float, rng: Rng):
    p = 1.0 / block
    idx = [int(rng.u() * T)]
    while len(idx) < T:
        idx.append(int(rng.u() * T) if rng.u() < p else (idx[-1] + 1) % T)
    return idx


def reality_check_spa(diffs, n_boot: int, block: float, rng: Rng) -> dict:
    """diffs: T×K Überrenditen gegenüber der Benchmark. White-RC (nicht studentisiert) und Hansen-SPA (studentisiert, konsistente Zentrierung)."""
    T, K = len(diffs), len(diffs[0])
    means = [mean([diffs[t][k] for t in range(T)]) for k in range(K)]
    sds = [stdev([diffs[t][k] for t in range(T)]) for k in range(K)]
    v_rc = math.sqrt(T) * max(means)
    v_spa = max(0.0, max(math.sqrt(T) * means[k] / sds[k] for k in range(K) if sds[k] > 0))
    thr = [-sds[k] * math.sqrt(2 * math.log(math.log(T)) / T) for k in range(K)]
    mu_c = [means[k] if means[k] >= thr[k] else 0.0 for k in range(K)]
    c_rc = c_spa = 0
    for _ in range(n_boot):
        idx = stationary_bootstrap_indices(T, block, rng)
        bm = [mean([diffs[t][k] for t in idx]) for k in range(K)]
        if math.sqrt(T) * max(bm[k] - means[k] for k in range(K)) >= v_rc:
            c_rc += 1
        s = max(0.0, max(math.sqrt(T) * (bm[k] - mu_c[k]) / sds[k] for k in range(K) if sds[k] > 0))
        if s >= v_spa:
            c_spa += 1
    return {"p_reality_check": c_rc / n_boot, "p_spa": c_spa / n_boot, "best_mean": max(means)}


def romano_wolf(diffs, n_boot: int, block: float, alpha: float, rng: Rng) -> dict:
    """Stepdown-Verfahren mit studentisierten Statistiken; liefert die verworfenen Nullhypothesen (Strategie ohne Mehrertrag)."""
    T, K = len(diffs), len(diffs[0])
    means = [mean([diffs[t][k] for t in range(T)]) for k in range(K)]
    sds = [stdev([diffs[t][k] for t in range(T)]) for k in range(K)]
    stat = [math.sqrt(T) * means[k] / sds[k] for k in range(K)]
    boots = []
    for _ in range(n_boot):
        idx = stationary_bootstrap_indices(T, block, rng)
        boots.append([math.sqrt(T) * (mean([diffs[t][k] for t in idx]) - means[k]) / sds[k] for k in range(K)])
    active, rejected = set(range(K)), []
    while active:
        mx = sorted(max(b[k] for k in active) for b in boots)
        crit = mx[min(len(mx) - 1, int(math.ceil((1 - alpha) * len(mx))) - 1)]
        new = [k for k in sorted(active) if stat[k] > crit]
        if not new:
            break
        rejected += new
        active -= set(new)
    return {"rejected": sorted(rejected), "statistics": stat}


# ------------------------------------------------------------------------------------------------ Hauptprogramm
def synthetic(T, N, rng, true_sr_daily=None):
    m = []
    for _ in range(T):
        row = [rng.normal(0.0, 0.01) for _ in range(N)]
        if true_sr_daily is not None:
            row[0] += true_sr_daily * 0.01
        m.append(row)
    return m


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    alpha, power = P.f("P-RES-ALPHA"), P.f("P-RES-POWER")
    sr_grid = [0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0]
    se_table = {str(y): {str(s): lo_se(s, y) for s in sr_grid} for y in (1, 2, 5, 8, 10, 20)}
    power_years = {str(s): years_for_power(s, alpha, power) for s in sr_grid}
    # Zahlenbeispiel Bailey/López de Prado (2014): SR 2,5 p. a., T = 1250 Tage, Schiefe −3, Kurtosis 10, V[SR] = 1/2 p. a., N = 46 bzw. 88
    ann = 250
    sr_d = 2.5 / math.sqrt(ann)
    var_d = 0.5 / ann
    ex = {"N46": dsr(sr_d, 1250, -3.0, 10.0, var_d, 46), "N88": dsr(sr_d, 1250, -3.0, 10.0, var_d, 88),
          "source_value_N46": 0.9505, "abs_error_N46": abs(dsr(sr_d, 1250, -3.0, 10.0, var_d, 46) - 0.9505)}
    rng = Rng(6_4_2026)
    noise = synthetic(800, 10, rng)
    signal = synthetic(800, 10, rng, true_sr_daily=0.15)
    pbo = {"noise_only": pbo_cscv(noise), "one_true_strategy": pbo_cscv(signal)}
    rc = {"noise_only": reality_check_spa(noise, 300, 10.0, rng), "one_true_strategy": reality_check_spa(signal, 300, 10.0, rng)}
    rw = {"noise_only": romano_wolf(noise, 300, 10.0, alpha, rng), "one_true_strategy": romano_wolf(signal, 300, 10.0, alpha, rng)}
    out = {"calculator": "research/statistical_calculator.py", "model": "MOD-STAT", "inputs": input_hashes(["parameters.json"]), "synthetic_demos": True,
           "lo_standard_error": se_table, "years_for_power": power_years, "alpha": alpha, "power": power,
           "dsr_source_example": ex, "pbo_cscv_demo": pbo, "reality_check_spa_demo": rc, "romano_wolf_demo": rw,
           "t_hurdle_new_factor": P.f("P-RES-T-HURDLE")}
    ok = write_or_check(OUT, dumps(out), a.check)
    ok &= ex["abs_error_N46"] < 5e-4
    if not a.check:
        print("DSR N=46:", round(ex["N46"], 4), "Quelle 0,9505; N=88:", round(ex["N88"], 4))
        print("Jahre für Teststärke:", {k: round(v, 1) for k, v in power_years.items()})
        print("PBO:", {k: round(v["pbo"], 3) for k, v in pbo.items()}, "RC/SPA:", rc, "RW:", {k: v["rejected"] for k, v in rw.items()})
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
