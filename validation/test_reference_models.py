#!/usr/bin/env python3
"""Referenztests der Kernrechnungen (Phase P10 der Paketprüfung; Testkatalog T-CALC-*, T-STR-*, T-RISK-GAP-001, T-RISK-MRG-001).

Jeder Test rechnet mit eigener, unabhängiger Formel oder konstruierten Eingaben nach und vergleicht mit den Funktionen der Rechner und mit
den gespeicherten Ergebnissen. Nur Standardbibliothek; Aufruf aus dem Paketverzeichnis:

    python -W error validation/test_reference_models.py [-v] [--report validation/reference_tests_report.json]

Die Testnamen entsprechen dem Feld evidence im Testkatalog (implementation/test_catalog.json).
"""
from __future__ import annotations

import bisect
import json
import math
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from statistics import NormalDist

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from financials import cost_model, decision_montecarlo, tax_scenarios  # noqa: E402
from lib import calc  # noqa: E402
from operations import costdrift_monitor, monitor_simulation  # noqa: E402
from research import operating_characteristics as oc  # noqa: E402
from research import prior_derivation, statistical_calculator  # noqa: E402
from research.reference_strategies import s_base, s_ca, s_im, s_rev, s_tf  # noqa: E402
from risk import kelly_ruin_simulator, leverage_calculator, stress_test_engine  # noqa: E402

N = NormalDist()


def j(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


P = calc.Params()
PRM = {p["id"]: p["value"] for p in j("parameters.json")["parameters"]}
INS = {i["id"]: i for i in j("registers/instruments.json")["instruments"]}
BY_SYMBOL = {i["symbol"]: i for i in INS.values()}
COST = {c["id"]: c for c in j("registers/costs.json")["costs"]}


def bars_24h(prices, window=None, window_start=0):
    """Stundenbalken im Kalender der Umschlagsimulation: 23 Balken je Tag, Tag = 24 Stunden, keine Wochenenden."""
    out = []
    for i, p in enumerate(prices):
        day, k = divmod(i, 23)
        in_w = True if window is None else window_start <= k < window_start + window
        pos = (k - window_start) if (window is not None and in_w) else (k if window is None else -1)
        out.append({"price": p, "hours": float(day * 24 + k), "in_window": in_w, "day": day, "window_pos": pos,
                    "window_len": window if window is not None else 23})
    return out


def _interp(grid, qs, u):
    """Inverse Verteilungsfunktion aus Quantilen: lineare Interpolation, Ränder konstant (unabhängig vom Simulator implementiert)."""
    if u <= grid[0]:
        return qs[0]
    if u >= grid[-1]:
        return qs[-1]
    k = bisect.bisect_right(grid, u) - 1
    return qs[k] + (u - grid[k]) / (grid[k + 1] - grid[k]) * (qs[k + 1] - qs[k])


class ReferenzModelle(unittest.TestCase):
    # ------------------------------------------------------------------------------------------------ Kosten (T-CALC-COST-001)
    def test_cost_round_turn(self):
        comm = Decimal(COST["COST-COMM-FXFLAT"]["amount"])
        slip = Decimal(COST["COST-EXEC-SLIP-TICKS"]["amount"])
        fx = {"EUR": Decimal(1), "USD": Decimal(str(PRM["P-ECO-EURUSD"])), "GBP": Decimal(str(PRM["P-ECO-EURGBP"]))}
        res = {r["id"]: r for r in j("financials/cost_model_results.json")["instruments"]}
        for sym in ("FGBL", "ZN", "6E", "GC", "CL"):
            ins = BY_SYMBOL[sym]
            f = fx[ins["currency"]]
            tv = Decimal(ins["tick_value"])
            notional = Decimal(ins["multiplier"]) * Decimal(ins["planning"]["price"]["value"]) / f
            side = comm + Decimal(str(ins["planning"]["spread_ticks"]["value"])) / 2 * tv / f + slip * tv / f
            bp = float(2 * side / notional * 10000)
            mine = cost_model.per_contract(ins, COST, P, comm, slip)
            self.assertAlmostEqual(bp, float(mine["rt_bp"]), delta=1e-9 * bp, msg=sym)
            self.assertAlmostEqual(bp, float(res[ins["id"]]["cost_rt_bp"]), delta=1e-9 * bp, msg=sym)

    # ------------------------------------------------------------------------------------------------ Entscheidungsrechnung (T-CALC-DMC-001/002)
    def test_dmc_classes(self):
        cls = decision_montecarlo.classify
        v1 = PRM["P-ECO-V1-SR"][0]
        base = {"excess_rate": 0.01, "expected_annual_value_eur": "1000.00", "p_npv_positive": 0.9, "value_per_risk_unit": 0.3}
        self.assertEqual(cls(base, False, ["x"], P, v1)[0], "PROFILE_NOT_ADMISSIBLE")
        self.assertEqual(cls({**base, "excess_rate": 0.0}, True, [], P, v1)[0], "NON_POSITIVE_BASE")
        self.assertEqual(cls({**base, "expected_annual_value_eur": "0.00"}, True, [], P, v1)[0], "NOT_VIABLE_AT_CAPITAL")
        self.assertEqual(cls({**base, "p_npv_positive": PRM["P-ECO-MARGINAL-P"] - 1e-9}, True, [], P, v1)[0], "NOT_VIABLE_AT_CAPITAL")
        self.assertEqual(cls({**base, "value_per_risk_unit": v1}, True, [], P, v1)[0], "DOMINATED_BY_ALTERNATIVE")
        self.assertEqual(cls({**base, "p_npv_positive": PRM["P-ECO-VIABLE-P"]}, True, [], P, v1)[0], "VIABLE")
        self.assertEqual(cls({**base, "p_npv_positive": PRM["P-ECO-VIABLE-P"] - 1e-9}, True, [], P, v1)[0], "MARGINAL")
        # gespeicherte Zellen: Klasse aus Basisergebnis, Zulässigkeit und Robustheitsregel neu abgeleitet
        dmc, lev = j("financials/decision_montecarlo_results.json"), j("risk/leverage_results.json")
        for var, stages in dmc["table"].items():
            for st, profs in stages.items():
                for prof, cell in profs.items():
                    if "base" not in cell:
                        continue
                    lc = lev["cells"][var][st][prof]
                    b = cell["base"]
                    if not lc["admissible"]:
                        want = "PROFILE_NOT_ADMISSIBLE"
                    elif b["excess_rate"] <= 0:
                        want = "NON_POSITIVE_BASE"
                    elif float(b["expected_annual_value_eur"]) <= 0 or b["p_npv_positive"] < PRM["P-ECO-MARGINAL-P"]:
                        want = "NOT_VIABLE_AT_CAPITAL"
                    elif v1 >= b["value_per_risk_unit"]:
                        want = "DOMINATED_BY_ALTERNATIVE"
                    elif b["p_npv_positive"] >= PRM["P-ECO-VIABLE-P"]:
                        want = "VIABLE" if all(cell["sensitivities"][k]["class"] == "VIABLE" for k in ("KOSTEN_X1_5", "PRIOR_MINUS_0_05")) else "MARGINAL"
                    else:
                        want = "MARGINAL"
                    self.assertEqual(cell["class"], want, msg=f"{var}/{st}/{prof}")
        # P(NPV > 0) für ein Normalmodell: fester Prior, keine Kostenstreuung → NPV normalverteilt, geschlossene Form gegen Monte-Carlo
        grid = [k / 100 for k in range(1, 100)]
        prior = {"gross_quantiles": {"S-TF": [0.2] * len(grid)}, "quantile_grid": grid}
        ci = {"basis": "S-TF", "D": 1.5, "cbar": 0.0, "c_imp": 0.0, "sigma": 0.06}
        nav, F, C0, aud = 5e6, Decimal("20000"), Decimal("40000"), Decimal("15000")

        class P0:
            def __call__(self, k):
                return 0.0 if k == "P-ECO-COST-UNC-SD" else P(k)

            def f(self, k):
                return float(self(k))
        p0 = P0()
        n = 20000
        r = decision_montecarlo.simulate(nav, ci, F, C0, aud, prior, p0, calc.Rng(4711), n)
        H, ramp, disc = int(P("P-ECO-HORIZON-Y")), int(P("P-ECO-RAMP-YEARS")), P.f("P-ECO-DISCOUNT")
        opp = nav * P.f("P-ECO-CASH-AT-BROKER") * (P.f("P-ECO-CASH-RATE") - P.f("P-ECO-BROKER-RATE"))
        S = ci["D"] * 0.2
        mu = -float(C0) - float(aud) / (1 + disc) ** int(P("P-ECO-AUDIT-YEAR"))
        mu += sum((nav * ci["sigma"] * S - opp - float(F)) / (1 + disc) ** t for t in range(ramp + 1, H + 1))
        sd = nav * ci["sigma"] * math.sqrt(sum((1 + disc) ** (-2 * t) for t in range(ramp + 1, H + 1)))
        p_exact = N.cdf(mu / sd)
        se = math.sqrt(p_exact * (1 - p_exact) / n)
        self.assertLessEqual(abs(r["p_npv_positive"] - p_exact), 3 * se)

    def test_variant_dominance(self):
        dmc = j("financials/decision_montecarlo_results.json")
        lo, hi = PRM["P-ECO-V1-SR"]
        rate = float(PRM["P-ECO-HOURLY-RATE"])
        for st, v in dmc["variants_V0_V4"].items():
            nav, sig = float(st), float(PRM["P-ECO-V1-SIGMA"])
            t = PRM["P-ECO-V1-OPS-MIN"] * 12 / 60 * rate
            for k, x in enumerate((lo, hi)):
                self.assertAlmostEqual(v["V1"]["value_per_risk_unit_range"][k], (nav * sig * x - t) / (nav * sig), delta=1e-12)
            reg = dmc["table"]["U-KOSTEN"][st]["H5"]
            self.assertEqual(v["V4"]["universe"], "U-KOSTEN")                  # V4 ist die registrierte Familie, nicht das Sensitivitätsuniversum
            if "base" not in reg:
                self.assertEqual(v["decision"], "NICHT_ZULASSUNGSFAEHIG", msg=st)
                continue
            vpr = reg["base"]["value_per_risk_unit"]
            self.assertEqual(v["V4"]["value_per_risk_unit"], vpr)
            v1_lo, v1_hi = sorted(v["V1"]["value_per_risk_unit_range"])
            if reg["class"] in ("PROFILE_NOT_ADMISSIBLE", "NON_POSITIVE_BASE", "NOT_VIABLE_AT_CAPITAL"):
                want = reg["class"]                                            # Prüfreihenfolge §5.7: Klasse vor Dominanz
            else:
                want = "DOMINATED_BY_ALTERNATIVE" if v1_lo >= vpr else ("V1_OBERER_WERT_UEBERLEGEN" if v1_hi >= vpr else "NICHT_DOMINIERT")
            self.assertEqual(v["decision"], want, msg=st)
            if "V3" in v:                                                      # V3: NPV = V4 plus eingesparter Aufbau
                saved = float(v["V4"]["build_effort_bs05_eur"]) - float(v["V3"]["build_effort_bs05_eur"])
                self.assertAlmostEqual(float(v["V3"]["npv_mean_eur_approx"]), float(v["V4"]["npv_mean_eur"]) + saved, delta=0.011)

    # ------------------------------------------------------------------------------------------------ Steuern (T-CALC-TAX-001)
    def test_tax_sensitivity(self):
        rate = PRM["P-ECO-TAX-SENS"]
        for before in (-5000.0, 0.0, 1e-9, 1000.0, 25000.55):
            want = before * (1 - rate) if before > 0 else before
            self.assertEqual(tax_scenarios.after_tax_sensitivity(before, rate), want)
        self.assertEqual(tax_scenarios.after_tax_sensitivity_eur("25000.55", rate), Decimal("17500.38"))
        self.assertEqual(tax_scenarios.after_tax_sensitivity_eur("-1.00", rate), Decimal("-1.00"))

    # ------------------------------------------------------------------------------------------------ Prior und Zulassung (T-CALC-PRIOR-001/002)
    def test_prior_portfolio(self):
        rho_b = PRM["P-PRI-RHO-BETWEEN"]
        rho_w = PRM["P-PRI-RHO-WITHIN"]
        ids = [BY_SYMBOL["GC"]["id"], BY_SYMBOL["CL"]["id"], BY_SYMBOL["ZW"]["id"]]
        rcls = {i: INS[i]["risk_class"] for i in ids}
        q = (3 + 6 * rho_b) / 9            # drei Klassen, gleiche Gewichte
        self.assertAlmostEqual(prior_derivation.div_mult(ids, rcls, P), min(PRM["P-STR-IDM-CAP"], 1 / math.sqrt(q)), delta=1e-9)
        ids2 = [BY_SYMBOL["GC"]["id"], BY_SYMBOL["SI"]["id"]]
        rcls2 = {i: INS[i]["risk_class"] for i in ids2}
        rho = rho_w[INS[ids2[0]]["risk_class"]]
        self.assertAlmostEqual(prior_derivation.div_mult(ids2, rcls2, P), min(PRM["P-STR-IDM-CAP"], 1 / math.sqrt((2 + 2 * rho) / 4)), delta=1e-9)
        pr = j("research/prior_results.json")
        for var, stages in pr["admission"].items():
            for st, a in stages.items():
                if a.get("instruments") and "D" in a:
                    r = {i: INS[i]["risk_class"] for i in a["instruments"]}
                    self.assertAlmostEqual(a["D"], prior_derivation.div_mult(a["instruments"], r, P), delta=1e-9, msg=f"{var}/{st}")

    def test_history_rule(self):
        req = PRM["P-RES-DEV-YEARS"] + PRM["P-RES-HOLDOUT-YEARS"]
        std = {"id": "STD", "standard_ref": None, "data_history": {"years_available": req}}
        micro = {"id": "MIC", "standard_ref": "STD", "data_history": {"years_available": 0.0}}
        short = {"id": "STD2", "standard_ref": None, "data_history": {"years_available": req - 1e-9}}
        u = {"STD": std, "MIC": micro, "STD2": short}
        self.assertGreaterEqual(prior_derivation.hist_years(micro, u, req), req)
        self.assertLess(prior_derivation.hist_years(short, u, req), req)
        pr = j("research/prior_results.json")
        for var, stages in pr["admission"].items():
            if var == "U-HANDELBAR":
                continue
            for a in stages.values():
                for i in a["instruments"]:
                    self.assertGreaterEqual(prior_derivation.hist_years(INS[i], INS, req), req, msg=i)
        excl = sorted(i["id"] for i in INS.values() if i["access"]["status"] == "PRIMAERBROKER_BOERSE_ANGEBOTEN" and not i["blocked"]
                      and prior_derivation.hist_years(i, INS, req) < req)
        self.assertEqual(sorted(pr["admission_rule"]["history_excluded"]), excl)

    # ------------------------------------------------------------------------------------------------ Hebel, Lückenregel, Margin (T-CALC-LEV-001, T-RISK-*)
    def test_gap_rule(self):
        cm = {r["id"]: r for r in j("financials/cost_model_results.json")["instruments"]}
        leverage_calculator.ES_FACTOR = leverage_calculator.es_factor_t(P.f("P-SIM-T-DF"), P.f("P-RISK-ES-CONF"))
        ids = [BY_SYMBOL["GC"]["id"], BY_SYMBOL["CL"]["id"]]
        for prof in ("H5", "H20"):
            ev = leverage_calculator.evaluate(ids, INS, P, prof, cm)
            sig_t = P.f(f"P-LEV-{prof}-SIGMA")
            vols = [INS[i]["planning"]["vol_annual_pct"]["base"] / 100 for i in ids]
            D = 1 / math.sqrt((2 + 2 * PRM["P-PRI-RHO-BETWEEN"]) / 4)
            w = [sig_t * D * 0.5 / v for v in vols]
            gaps = []
            for i in ids:
                ins = INS[i]
                hist = PRM[f"P-GAP-{ins['risk_class'].replace('_', '-')}"] / 100
                gaps.append(max(hist, PRM["P-GAP-K-HYP-HIGH"] * ins["planning"]["vol_annual_pct"]["base"] / 100 / math.sqrt(252)))
            gl = sum(a * b for a, b in zip(w, gaps, strict=True))
            budget = PRM["P-OP-DAILY-LOSS-CAP"] - PRM["P-RISK-GAP-RESERVE"]
            s = min(1.0, budget / (PRM["P-RISK-WEEKEND-FACTOR"] * gl), P.f(f"P-LEV-{prof}-CAP") / sum(w))
            self.assertAlmostEqual(ev["D"], D, delta=1e-9)
            self.assertAlmostEqual(ev["gap_loss_at_target"]["DESIGN"], gl, delta=1e-9)
            self.assertAlmostEqual(ev["sigma_achieved"], sig_t * s, delta=1e-9)
            self.assertAlmostEqual(ev["L_g_achieved"], sum(w) * s, delta=1e-9)

    def test_gap_rule_boundary(self):
        budget = PRM["P-OP-DAILY-LOSS-CAP"] - PRM["P-RISK-GAP-RESERVE"]
        wf = PRM["P-RISK-WEEKEND-FACTOR"]
        self.assertTrue(calc.gap_rule_ok(budget - 0.01, 0.01, P))
        self.assertFalse(calc.gap_rule_ok(budget - 0.01 + 1e-6, 0.01, P))
        self.assertTrue(calc.gap_rule_ok(budget / wf, 0.0, P, weekend=True))
        self.assertFalse(calc.gap_rule_ok(budget / wf + 1e-6, 0.0, P, weekend=True))
        self.assertTrue(calc.gap_rule_ok(budget, -0.02, P))          # Tagesgewinn schafft keinen zusätzlichen Spielraum
        self.assertFalse(calc.gap_rule_ok(budget + 1e-6, -0.02, P))
        lev = j("risk/leverage_results.json")
        for stages in lev["cells"].values():
            for profs in stages.values():
                for c in profs.values():
                    if c.get("n"):
                        self.assertTrue(calc.gap_rule_ok(c["gap_loss_achieved"]["DESIGN"], 0.0, P, weekend=True))

    def test_margin_buffer(self):
        me, inc, trig, phi = 0.05, PRM["P-MRG-STRESS-2"], PRM["P-MRG-DERISK-TRIGGER"], PRM["P-ECO-CASH-AT-BROKER"]
        nav = 1_000_000.0
        at_broker = phi * nav                       # nur dieser Teil deckt die Margin; Verluste werden dort abgerechnet
        margin = me * nav * (1 + inc)
        loss = at_broker - trig * margin            # Margin-Level (Guthaben beim Broker − L) / Margin = Schwelle
        self.assertAlmostEqual(calc.margin_loss_to_level(me, inc, trig, phi), loss / nav, delta=1e-12)
        self.assertEqual(calc.margin_loss_to_level(1.0, 1.0, 2.0, phi), 0.0)
        self.assertGreater(calc.margin_loss_to_level(me, inc, trig, phi), calc.margin_loss_to_level(me, inc, trig + 0.1, phi))
        # nötiger Anteil beim Broker: genau so viel, dass das Level nach dem Verlust auf der Schwelle liegt
        need = calc.broker_share_required(me, inc, trig, 0.03)
        self.assertAlmostEqual(calc.margin_loss_to_level(me, inc, trig, need), 0.03, delta=1e-12)
        # Stressergebnis: Margin-Level = (Anteil beim Broker − Verlust mit Leiter) / M/E-Spitze
        for per in j("risk/stress_results.json")["results"].values():
            for r in per.values():
                for s in r["scenarios"].values():
                    want = max(0.0, phi - s["loss_with_ladder"]) / s["me_peak"]
                    self.assertAlmostEqual(s["margin_level_after"], want, delta=1e-9 * max(1.0, abs(want)))

    # ------------------------------------------------------------------------------------------------ Kelly, Stress (T-CALC-KELLY-001, T-CALC-STRESS-001)
    def test_kelly_ruin(self):
        k = j("risk/kelly_ruin_results.json")
        prior_res = j("research/prior_results.json")
        for per in k["results"].values():
            for r in per.values():
                if "kelly" not in r:
                    continue
                s_star, sig = r["kelly"]["sigma_star_full_kelly"], r["sigma"]
                # volles Kelly: σ* = mittlere Netto-Sharpe des Priors, hier unabhängig als Mittelpunktsquadratur über das Quantilgitter nachgerechnet
                grid = prior_res["quantile_grid"]
                qs = prior_res["gross_quantiles"][r["basis"]]
                nodes = [(k + 0.5) / 2000 for k in range(2000)]
                s_mean = sum(r["D"] * (_interp(grid, qs, u) - r["mean_cost_sr"]) for u in nodes) / len(nodes)
                self.assertAlmostEqual(s_star, max(0.0, s_mean), delta=1e-9)
                self.assertLess(abs(s_mean - r["sr_prior"]["mean"]), 4 * r["sigma"] + 0.05)   # Monte-Carlo-Mittel liegt nahe der Quadratur
                self.assertAlmostEqual(r["kelly"]["zero_growth_sigma"], 2 * s_star, delta=1e-9)
                if s_star > 0:
                    self.assertAlmostEqual(r["kelly"]["kelly_fraction_of_profile"], sig / s_star, delta=1e-7)
                    self.assertAlmostEqual(r["kelly"]["expected_growth"], sig * s_star - sig * sig / 2, delta=1e-7)
        # Monte-Carlo-Stabilität: P(DD ≥ 10 %) mit unabhängigem Seed innerhalb drei Standardfehlern
        lev, prior = j("risk/leverage_results.json"), j("research/prior_results.json")
        st = str(PRM["P-RISK-STRESS-REF-STAGE"])
        cell = lev["cells"]["U-BREAKEVEN"][st]["H5"]
        kelly_ruin_simulator.YEARS = int(P("P-ECO-HORIZON-Y"))
        r2 = kelly_ruin_simulator.simulate(cell["sigma_achieved"], cell["D"], cell["mean_cost_sr"], cell["gap_loss_achieved"]["DESIGN"], prior, P,
                                           calc.Rng(123457), ladder=True, basis="S-TF")
        p1, p2 = k["results"]["H5"]["SYSTEM"]["p_drawdown_ge"]["10"], r2["p_drawdown_ge"]["10"]
        n = int(P("P-SIM-PATHS"))
        pbar = (p1 + p2) / 2
        self.assertLessEqual(abs(p1 - p2), 3 * math.sqrt(max(pbar * (1 - pbar), 1e-6) * 2 / n))

    def test_stress_single(self):
        subst_share, days = PRM["P-RISK-STRESS-SUBST-SHARE"], PRM["P-RISK-STRESS-MULTI-DAYS"]
        checked = 0
        for sc in j("risk/stress_scenarios.json")["historical"]:
            for sym in ("GC", "CL", "6E"):
                ins = BY_SYMBOL[sym]
                key = "FX_CHF" if sym in ("6S", "MSF") else ins["risk_class"]
                m = sc["moves"].get(key) or sc["moves"].get(ins["risk_class"])
                d1, _ = stress_test_engine.move_pct(ins, sc["moves"], P, "d1", sc.get("extra", {}))
                mu, _ = stress_test_engine.move_pct(ins, sc["moves"], P, "multi", sc.get("extra", {}))
                subst = subst_share * leverage_calculator.gap_pct(ins, P, "HIST")
                want_d1 = (m["d1"] / 100 if m and m["d1"] is not None else (subst if not m or m["multi"] is None else min(subst, m["multi"] / 100)))
                want_mu = max(m["multi"] / 100 if m and m["multi"] is not None else want_d1 * math.sqrt(days), want_d1)
                self.assertAlmostEqual(d1, want_d1, delta=1e-12, msg=f"{sc['id']} {sym}")
                self.assertAlmostEqual(mu, want_mu, delta=1e-12, msg=f"{sc['id']} {sym}")
                checked += 1
        self.assertGreater(checked, 0)
        F = PRM["P-RISK-LADDER-FACTORS"]
        l1 = PRM["P-RISK-DL-L1"]
        total, flat = stress_test_engine.ladder_path([l1, 0.02], P)
        self.assertFalse(flat)
        self.assertAlmostEqual(total, l1 + 0.02 * F["DL_L1"], delta=1e-12)      # L1 wirkt am Folgetag
        total, flat = stress_test_engine.ladder_path([PRM["P-RISK-DL-L3"], 0.05], P)
        self.assertTrue(flat)
        self.assertAlmostEqual(total, PRM["P-RISK-DL-L3"], delta=1e-12)       # L3 baut sofort ab
        # Handelsaussetzung: ausgesetzte Positionen laufen trotz Abbau voll weiter
        total, flat = stress_test_engine.ladder_path([PRM["P-RISK-DL-L3"], 0.05], P, fixed=[0.01, 0.04])
        self.assertTrue(flat)
        self.assertAlmostEqual(total, PRM["P-RISK-DL-L3"] + 0.01 + 0.04, delta=1e-12)
        # Zwei Positionen: Verlust des Portfolios = gewichtete Summe der Einzelbewegungen (ungünstigste Richtung)
        sc = next(s for s in j("risk/stress_scenarios.json")["historical"] if s["id"] == "SC-H-1987")
        ins_a, ins_b = BY_SYMBOL["GC"], BY_SYMBOL["6E"]
        alloc = {"ids": [ins_a["id"], ins_b["id"]], "w": [0.5, 1.5], "me": 0.02}
        res = stress_test_engine.evaluate(alloc, {ins_a["id"]: ins_a, ins_b["id"]: ins_b}, P, {}, sc, hyp=False)
        d1a = stress_test_engine.move_pct(ins_a, sc["moves"], P, "d1", sc.get("extra", {}))[0]
        d1b = stress_test_engine.move_pct(ins_b, sc["moves"], P, "d1", sc.get("extra", {}))[0]
        self.assertAlmostEqual(res["loss_day1"], 0.5 * d1a + 1.5 * d1b, delta=1e-12)

    # ------------------------------------------------------------------------------------------------ Statistik und Betriebscharakteristik
    def test_predictive_pass(self):
        for m, v, vf_data, pf in ((0.1, 0.04, 0.5, 0.8), (-0.2, 0.09, 0.25, 0.8), (0.3, 0.01, 1.0, 0.9)):
            z = N.inv_cdf(pf)
            got = oc.predictive_pass(m, v, vf_data, z)
            vf = 1 / (1 / v + 1 / vf_data)
            want = 1 - N.cdf((z * math.sqrt(vf) - m) / math.sqrt(v - vf))   # Vorverteilung des Endposteriormittels: N(m, v − vf)
            self.assertAlmostEqual(got, want, delta=1e-9)

    def test_dsr_example(self):
        ann = 250
        got = statistical_calculator.dsr(2.5 / math.sqrt(ann), 1250, -3.0, 10.0, 0.5 / ann, 46)
        self.assertAlmostEqual(got, 0.9505, delta=1e-4)          # Bailey und López de Prado (2014), Zahlenbeispiel

    def test_power(self):
        a, pw = PRM["P-RES-ALPHA"], PRM["P-RES-POWER"]
        stat = j("research/statistical_results.json")
        for sr in (0.1, 0.3, 0.5):
            want = ((N.inv_cdf(1 - a) + N.inv_cdf(pw)) / sr) ** 2
            self.assertAlmostEqual(statistical_calculator.years_for_power(sr, a, pw), want, delta=1e-9 * want)
            self.assertAlmostEqual(stat["years_for_power"][str(sr)], want, delta=1e-6 * want)

    def test_turnover_determinism(self):
        from research.reference_strategies import turnover_simulation
        self.assertEqual(turnover_simulation.main(["--check"]), 0)

    def test_costdrift_rule(self):
        prob, thr, sd = PRM["P-MON-COSTDRIFT-PROB"], PRM["P-MON-COSTDRIFT-RATIO"], PRM["P-MON-FILL-NOISE"]
        z = N.inv_cdf(prob)
        for n in (5, 40, 400):
            for delta in (-0.2, -1e-6, 1e-6, 0.2):
                mean = thr + z * sd / math.sqrt(n) + delta
                p_above = N.cdf((mean - thr) * math.sqrt(n) / sd)
                self.assertEqual(costdrift_monitor.lower_bound_exceeds(mean, n, sd, z, thr), p_above > prob, msg=f"n={n} δ={delta}")

    # ------------------------------------------------------------------------------------------------ Monitore (T-CALC-MON-001)
    def test_monitor_harm(self):
        mon = j("operations/monitor_results.json")
        m0, s0, prob = mon["harm_prior"]["mean"], mon["harm_prior"]["sd"], PRM["P-MON-HARM-SR"]
        z = N.inv_cdf(prob)
        for s_hat in (-1.5, -0.3, 0.0, 0.4):
            for years in (0.5, 2.0, 10.0):
                prec = 1 / s0 ** 2 + years                                   # unabhängige Normal-Normal-Rechnung
                mean = (m0 / s0 ** 2 + s_hat * years) / prec
                want = 0.5 * (1 + math.erf(-mean * math.sqrt(prec) / math.sqrt(2)))
                self.assertAlmostEqual(monitor_simulation.harm_posterior_negative(s_hat, years, m0, s0), want, delta=1e-12)
                thr = monitor_simulation.harm_threshold_s_hat(years, m0, s0, prob, z)
                self.assertAlmostEqual(monitor_simulation.harm_posterior_negative(thr, years, m0, s0), prob, delta=1e-9)
        n = mon["runs"]
        for name, v in mon["harm"].items():
            closed = N.cdf((monitor_simulation.harm_threshold_s_hat(2.0, m0, s0, prob, z) - v["true_sharpe"]) * math.sqrt(2.0))
            se = math.sqrt(max(closed * (1 - closed), 1e-6) / n)
            self.assertGreaterEqual(v["p_trigger_within_24m"], closed - 3 * se, msg=name)   # „bis Monat 24“ umfasst „in Monat 24“
        h = mon["harm"]
        self.assertGreaterEqual(h["STARK_SCHAEDLICH"]["p_trigger_within_60m"], h["SCHAEDLICH"]["p_trigger_within_60m"])
        self.assertGreaterEqual(h["SCHAEDLICH"]["p_trigger_within_60m"], h["BRAUCHBAR"]["p_trigger_within_60m"])
        vd = mon["vol_drift"]
        self.assertGreaterEqual(vd["FAKTOR_2"]["p_trigger_within_20d"], vd["FAKTOR_1_5"]["p_trigger_within_20d"])

    # ------------------------------------------------------------------------------------------------ Referenzstrategien (T-STR-*)
    def _prm(self):
        return {k: PRM[k] for k in PRM if k.startswith(("P-STR-", "P-OP-HOLD"))}

    def test_strategy_tf(self):
        prm = self._prm()
        for direction in (1, -1):
            prices = [100 * math.exp(direction * 0.001 * t + 0.0001 * (-1) ** t) for t in range(460)]
            book, info = s_tf.run(bars_24h(prices), prm)
            t0 = book.trades[0]
            self.assertEqual(t0.direction, direction)
            self.assertEqual(t0.entry_bar, info["warmup"])
            self.assertEqual(t0.reason, "ZEITSTOPP")
            self.assertEqual(t0.holding_hours, prm["P-OP-HOLD-MAX-H"])
            t1 = book.trades[1]
            self.assertEqual(t1.entry_hours - t0.exit_hours, prm["P-STR-REENTRY-COOLDOWN-H"])

    def test_strategy_im(self):
        prm = self._prm()
        win, start, days, target = 8, 5, 30, 25
        prices = []
        for d in range(days):
            for k in range(23):
                p = 100 * (1 + 0.0001 * (-1) ** (d * 23 + k))
                if d == target and k >= start + 1:
                    p *= 1.03
                prices.append(p)
        bars = bars_24h(prices, window=win, window_start=start)
        book, info = s_im.run(bars, prm)
        self.assertEqual(len(book.trades), 1)
        t = book.trades[0]
        self.assertEqual(t.direction, 1)
        self.assertEqual(bars[t.entry_bar]["day"], target)
        self.assertEqual(bars[t.entry_bar]["window_pos"], info["signal_hour"])
        self.assertEqual(t.reason, "KERNZEITENDE")
        self.assertEqual(t.holding_hours, prm["P-STR-IM-HOLD-H"])

    def test_strategy_rev(self):
        prm = self._prm()
        prices = []
        for i in range(40 * 23):
            lvl = 1.0 if i < 576 else math.exp(0.001 * (min(i, 598) - 575))          # Anstieg über 23 Balken bis zum Beginn von Tag 26
            prices.append(100.0 * lvl * (1 + 0.0001 * (-1) ** i))
        bars = bars_24h(prices)
        book, info = s_rev.run(bars, prm)
        t = book.trades[0]
        self.assertEqual(t.direction, -1)                                  # gegen die Bewegung
        self.assertEqual((bars[t.entry_bar]["day"], bars[t.entry_bar]["window_pos"]), (26, 0))
        self.assertEqual(t.reason, "HALTEDAUER")
        self.assertEqual(t.holding_hours, prm["P-STR-REV-HOLD-H"])

    def test_strategy_base(self):
        prm = self._prm()
        prices = []
        for d in range(90):
            close = 100.0 * (1 + 0.001 * (-1) ** d) if d < 70 else 100.0 * (1.02 + 0.01 * (d - 70))
            prices += [close] * 23
        bars = bars_24h(prices)
        book7, _ = s_base.run(bars, prm, time_stop=True)
        t = book7.trades[0]
        self.assertEqual(t.direction, 1)
        self.assertEqual(bars[t.entry_bar]["day"], 70)                     # erster Schluss über dem 55-Tage-Hoch
        self.assertEqual(t.reason, "ZEITSTOPP")
        self.assertEqual(t.holding_hours, prm["P-OP-HOLD-MAX-H"])
        book, _ = s_base.run(bars, prm, time_stop=False)
        self.assertEqual(book.trades[0].reason, "ENDE")                     # ohne Zeitstopp bis zum Ende gehalten
        self.assertGreater(book.trades[0].holding_hours, prm["P-OP-HOLD-MAX-H"])

    def test_strategy_ca(self):
        c = s_ca.annualized_carry(100.0, 99.0, 91.0)
        self.assertAlmostEqual(c, 0.01 * 365 / 91, delta=1e-15)
        x = PRM["P-STR-CA-TILT"]
        self.assertEqual(s_ca.tilt_factor(c, 1, x), 1 + x)
        self.assertEqual(s_ca.tilt_factor(c, -1, x), 1 - x)
        self.assertEqual(s_ca.tilt_factor(0.001, 1, x, dead_zone=0.01), 1.0)
        prm = self._prm()
        prices = [100 * math.exp(0.001 * t + 0.0001 * (-1) ** t) for t in range(460)]
        bars = bars_24h(prices)
        plain, _ = s_tf.run(bars, prm)
        tilted, _ = s_tf.run(bars, prm, carry_tilt=s_ca.make_tilt([c] * len(bars), x))
        self.assertAlmostEqual(tilted.trades[0].size, plain.trades[0].size * (1 + x), delta=1e-12)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    report = None
    if "--report" in argv:
        i = argv.index("--report")
        report = argv[i + 1]
        del argv[i:i + 2]
    verbosity = 2 if "-v" in argv else 1
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReferenzModelle)
    names = sorted(t.id().split(".")[-1] for t in suite)
    res = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout).run(suite)
    failed = sorted({t.id().split(".")[-1] for t, _ in res.failures + res.errors})
    out = {"tests": names, "failed": failed, "passed": [n for n in names if n not in failed], "result": "PASS" if res.wasSuccessful() else "FAIL"}
    if report:
        (ROOT / report).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("REFERENZTESTS", out["result"], f"{len(out['passed'])}/{len(names)}")
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
