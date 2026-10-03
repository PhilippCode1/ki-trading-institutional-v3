#!/usr/bin/env python3
"""Kelly-, Ruin- und Drawdown-Simulator je Profil unter Parameterunsicherheit (§7.4 Nr. 1–2; Modell MOD-KELLY).

Je Profil und Allokation (SYSTEM = nach Lückenregel skaliert; WUNSCHHEBEL = Zins-kalibriert mit L_g = Profilgrenze):
  * Netto-Sharpe je Pfad aus dem Prior: S = D · (g − c̄), g aus den Quantilen der S-TF-Brutto-Verteilung (research/prior_results.json)
  * Kelly: σ* = S, g(σ) ≈ σ·S − σ²/2; erwartetes Wachstum und P(g < 0) über die Prior-Verteilung; Kelly-Bruchteil σ/E[S]
  * Tagesrenditen mit fetten Rändern (t mit 4 Freiheitsgraden, Varianz 1), Volatilitätsregimen (normal/Stress ×2 mit Korrelationsschock),
    Sprüngen in ungünstiger Richtung (Größe bis zur Konstruktionslücke; seltene Sprünge jenseits der Konstruktionslücke)
  * De-Risking-Leiter (Tages- und Drawdown-Stufen) mit und ohne Leiter
  * Kennzahlen: Jahresrendite, maximaler Drawdown über 1/3/5 Jahre, Erholungszeit, P(DD ≥ 10/20/30/50 %), P(Ruin: Verlust ≥ 50 % oder
    Zwangsliquidation), P(Tagesverlust > 9 %), Expected Shortfall der Jahresrendite, Anteil Pfade mit Handelsstopp (DD ≥ 30 %)
Synthetische Pfade, keine Evidenz für eine Edge (R-02). Aufruf: python risk/kelly_ruin_simulator.py [--check]
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.calc import Params, Rng, dumps, expected_shortfall, input_hashes, ladder_factor, load, main_args, mean, quantile, write_or_check  # noqa: E402

OUT = "risk/kelly_ruin_results.json"
SEED = 7_4_2026
YEARS = 0   # Planungshorizont; in main() aus P-ECO-HORIZON-Y gesetzt (§7.4: Drawdowns über 1, 3 und 5 Jahre)
DAYS = 252


def sample_quantile(qs, grid, u):
    """Inverse Verteilungsfunktion aus gespeicherten Quantilen (lineare Interpolation, Ränder konstant)."""
    if u <= grid[0]:
        return qs[0]
    if u >= grid[-1]:
        return qs[-1]
    k = int((u - grid[0]) / (grid[1] - grid[0]))
    k = min(max(k, 0), len(grid) - 2)
    t = (u - grid[k]) / (grid[k + 1] - grid[k])
    return qs[k] + t * (qs[k + 1] - qs[k])


def simulate(sigma, D, cbar, gap_design, prior, P, rng, ladder=True, basis="S-TF"):
    qs, grid = prior["gross_quantiles"][basis], prior["quantile_grid"]
    reg = P("P-SIM-REGIME")
    P_ENTER_STRESS, P_EXIT_STRESS, STRESS_MULT = reg["enter"], reg["exit"], reg["vol_multiple"]
    PATHS = int(P("P-SIM-PATHS"))
    js_lo, js_hi = P("P-SIM-JUMP-SIZE")
    jb_lo, jb_hi = P("P-SIM-BEYOND-SIZE")
    lam = P.f("P-SIM-JUMPS-PER-YEAR") / DAYS
    lam_b = P.f("P-SIM-BEYOND-PER-YEAR") / DAYS
    # Sprünge verändern nur die Verteilung, nicht Mittel und Gesamtvolatilität: Drift kompensiert, Diffusionsanteil reduziert
    ej = gap_design * (js_lo + js_hi) / 2
    ej2 = gap_design ** 2 * (js_hi ** 3 - js_lo ** 3) / (3 * (js_hi - js_lo))
    eb = gap_design * (jb_lo + jb_hi) / 2
    eb2 = gap_design ** 2 * (jb_hi ** 3 - jb_lo ** 3) / (3 * (jb_hi - jb_lo))
    var_jump_ann = DAYS * (lam * ej2 + lam_b * eb2)
    var_diff_ann = max(sigma ** 2 - var_jump_ann, P.f("P-SIM-DIFF-VAR-FLOOR") * sigma ** 2)
    pi_s = P_ENTER_STRESS / (P_ENTER_STRESS + P_EXIT_STRESS)
    base_sd = math.sqrt(var_diff_ann) / math.sqrt(DAYS) / math.sqrt((1 - pi_s) + pi_s * STRESS_MULT ** 2)
    comp = lam * ej + lam_b * eb
    cap = P.f("P-OP-DAILY-LOSS-CAP")
    l3, ddk, slip_l3 = P.f("P-RISK-DL-L3"), P.f("P-RISK-DD-KILL"), P.f("P-RISK-L3-SLIPPAGE")
    ruin_lvl = P.f("P-RISK-RUIN")
    ann, mdd = {1: [], 3: [], 5: []}, {1: [], 3: [], 5: []}
    rec_days, s_draws, day_breach, stopped, ruined = [], [], 0, 0, 0
    for _ in range(PATHS):
        S = D * (sample_quantile(qs, grid, rng.u()) - cbar)
        s_draws.append(S)
        mu = sigma * S / DAYS + comp
        nav, peak, stress, expo, halted = 1.0, 1.0, False, 1.0, False
        maxdd, trough_day, peak_at_trough, rec = 0.0, -1, 1.0, None
        done = {1: False, 3: False, 5: False}
        is_ruined = False
        for d in range(YEARS * DAYS):
            if halted:
                r = 0.0
            else:
                if stress:
                    stress = rng.u() >= P_EXIT_STRESS
                else:
                    stress = rng.u() < P_ENTER_STRESS
                sd = base_sd * (STRESS_MULT if stress else 1.0)
                r = mu + sd * rng.student_t4_unit()
                if rng.u() < lam:
                    r -= gap_design * rng.uniform(js_lo, js_hi)
                if rng.u() < lam_b:
                    r -= gap_design * rng.uniform(jb_lo, jb_hi)
                r *= expo
                if ladder and -r >= l3 and -r < gap_design * 0.999:  # 0,999: numerische Toleranz; Lücken ab Konstruktionsgröße nicht gekappt
                    r = max(r, -l3 - slip_l3)          # Abbau greift intraday mit Zusatzverlust P-RISK-L3-SLIPPAGE
            if -r > cap:
                day_breach += 1
            nav *= (1 + r)
            if nav > peak:
                peak = nav
            if rec is None and trough_day >= 0 and nav >= peak_at_trough:
                rec = d - trough_day
            dd = 1 - nav / peak
            if dd > maxdd:
                maxdd, trough_day, peak_at_trough, rec = dd, d, peak, None
            if ladder and not halted:
                expo = ladder_factor(-r, dd, P)
                if dd >= ddk:
                    halted = True
            if nav <= 1 - ruin_lvl:
                is_ruined = True
                break
            for y in (1, 3, 5):
                if d == y * DAYS - 1:
                    mdd[y].append(maxdd)
                    done[y] = True
                    if y == 1:
                        ann[1].append(nav - 1)
        if is_ruined:
            ruined += 1
            for y in (1, 3, 5):
                if not done[y]:
                    mdd[y].append(max(maxdd, ruin_lvl))
                    if y == 1:
                        ann[1].append(nav - 1)
        elif halted:
            stopped += 1
        if rec is not None:
            rec_days.append(rec)
    n = PATHS
    a1 = sorted(ann[1])
    out = {"sigma": sigma, "sigma_diffusion": math.sqrt(var_diff_ann), "sigma_jumps": math.sqrt(var_jump_ann), "D": D, "mean_cost_sr": cbar,
           "sr_prior": {"mean": mean(s_draws), "p05": quantile(sorted(s_draws), 0.05),
                                                                        "p50": quantile(sorted(s_draws), 0.5), "p95": quantile(sorted(s_draws), 0.95),
                                                                        "p_positive": sum(1 for s in s_draws if s > 0) / n},
           "annual_return": {"mean": mean(a1), "p05": quantile(a1, 0.05), "p50": quantile(a1, 0.5), "p95": quantile(a1, 0.95),
                             "es_97_5": expected_shortfall(a1, 0.975)},
           "max_drawdown": {str(y): {"p50": quantile(sorted(mdd[y]), 0.5), "p95": quantile(sorted(mdd[y]), 0.95)} for y in (1, 3, 5)},
           "p_drawdown_ge": {str(t): sum(1 for x in mdd[5] if x >= t / 100) / n for t in (10, 20, 30, 50)},
           "p_ruin_5y": ruined / n, "p_trading_stop_5y": stopped / n,
           "p_day_loss_over_cap_per_year": day_breach / (n * YEARS),
           "recovery_days": {"p50": quantile(sorted(rec_days), 0.5) if rec_days else None, "recovered_share": len(rec_days) / n}}
    return out


def kelly(S_draws_mean, sigma, s_draws):
    g = [sigma * s - sigma * sigma / 2 for s in s_draws]
    return {"sigma_star_full_kelly": max(0.0, S_draws_mean), "kelly_fraction_of_profile": (sigma / S_draws_mean) if S_draws_mean > 0 else None,
            "expected_growth": mean(g), "p_growth_negative": sum(1 for x in g if x < 0) / len(g), "zero_growth_sigma": max(0.0, 2 * S_draws_mean)}


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    global YEARS
    YEARS = int(P("P-ECO-HORIZON-Y"))
    prior = load("research/prior_results.json")
    lev = load("risk/leverage_results.json")
    st = str(P("P-RISK-STRESS-REF-STAGE"))
    rng = Rng(SEED)
    res = {}
    seen = {}
    for prof in ["H5", "H10", "H15", "H20"]:
        cell = lev["cells"]["U-BREAKEVEN"][st][prof]
        cal = lev["leverage_calibration_via_rates"][st][prof]
        variants = {"SYSTEM": (cell["sigma_achieved"], cell["D"], cell["mean_cost_sr"], cell["gap_loss_achieved"]["DESIGN"], "S-TF")}
        if cal.get("feasible"):
            variants["WUNSCHHEBEL"] = (P.f(f"P-LEV-{prof}-SIGMA"), cal["D"], cal["mean_cost_sr"], cal["gap_loss_design"], "S-TF")
        alt = lev["cells"]["U-KOSTEN-TFD1"][st][prof]
        if alt.get("n"):
            variants["ALTERNATIVE_TFD1"] = (alt["sigma_achieved"], alt["D"], alt["mean_cost_sr"], alt["gap_loss_achieved"]["DESIGN"], "S-BASE-TFD1")
        res[prof] = {}
        for vname, (sig, D, cbar, gap, basis) in variants.items():
            key = (round(sig, 9), round(D, 9), round(cbar, 9), round(gap, 9), basis)
            if key in seen:
                res[prof][vname] = {"same_as": seen[key]}
                continue
            seen[key] = f"{prof}/{vname}"
            r = simulate(sig, D, cbar, gap, prior, P, rng, ladder=True, basis=basis)
            r["basis"] = basis
            qs, grid = prior["gross_quantiles"][basis], prior["quantile_grid"]
            s_draws = [D * (sample_quantile(qs, grid, (k + 0.5) / 2000) - cbar) for k in range(2000)]
            r["kelly"] = kelly(mean(s_draws), sig, s_draws)
            res[prof][vname] = r
        if prof == "H5":
            sig, D, cbar, gap, basis = variants["SYSTEM"]
            res[prof]["SYSTEM_OHNE_LEITER"] = simulate(sig, D, cbar, gap, prior, P, rng, ladder=False, basis=basis)
    out = {"calculator": "risk/kelly_ruin_simulator.py", "model": "MOD-KELLY", "seed": SEED, "paths": int(P("P-SIM-PATHS")), "years": YEARS, "synthetic": True,
           "inputs": input_hashes(["parameters.json", "research/prior_results.json", "risk/leverage_results.json"]),
           "model_setup": {"innovations": "t(4), Varianz 1 (P-SIM-T-DF)", "regimes": "P-SIM-REGIME", "jumps": "P-SIM-JUMPS-PER-YEAR, P-SIM-JUMP-SIZE",
                           "beyond_design": "P-SIM-BEYOND-PER-YEAR, P-SIM-BEYOND-SIZE", "compensation": "Drift um erwartete Sprünge erhöht; Diffusionsvolatilität reduziert",
                           "ruin": "Verlust ≥ P-RISK-RUIN oder Zwangsliquidation", "reference_stage": st},
           "results": res}
    ok = write_or_check(OUT, dumps(out), a.check)
    if not a.check:
        for prof, v in res.items():
            for k, r in v.items():
                if "same_as" in r:
                    print(f"{prof:<4}{k:<20} identisch mit {r['same_as']}")
                    continue
                print(f"{prof:<4}{k:<20} σ={r['sigma']:.3f} S̄={r['sr_prior']['mean']:+.3f} P(S>0)={r['sr_prior']['p_positive']:.2f} "
                      f"Jahr p50={r['annual_return']['p50']:+.3f} MDD5 p95={r['max_drawdown']['5']['p95']:.3f} P(DD≥20%)={r['p_drawdown_ge']['20']:.3f} "
                      f"Ruin={r['p_ruin_5y']:.4f} Stopp={r['p_trading_stop_5y']:.3f} Tag>9%/J={r['p_day_loss_over_cap_per_year']:.4f}")
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
