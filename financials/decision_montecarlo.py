#!/usr/bin/env python3
"""Entscheidungs-Monte-Carlo (§5.6, §5.7, EV-03; Modell MOD-DMC).

Je Universumsvariante (registriert U-KOSTEN; Sensitivitäten U-BREAKEVEN, U-KOSTEN-TFD1-7T, U-KOSTEN-TFD1), Kapitalstufe (P-ECO-CAPITAL-STAGES) und Profil (H5–H20),
Betriebsmodell: nur Eigenkonto des Betreibers (BQ-02: B1–B4 nicht Systemaufgabe):
  Netto-Sharpe je Ziehung  S = D · (g − (c̄ + c_Impact) · k · u) − Δ         g aus dem Prior (S-TF), u Kostenunsicherheit, k/Δ Sensitivität
  Jahreswert (Handelsjahr) V_t = NAV · σ_eff · (S + ε_t) − NAV · φ · (r_Geldmarkt − r_Broker) − Fixkosten
  NPV über P-ECO-HORIZON-Y Jahre = − Aufbaukosten (BS-00…BS-08) + Σ V_t/(1+r)^t − Audit/(1+r)^Jahr   (erstes Jahr ohne Standardhandel)
Ausgaben: Verteilung von Jahreswert und NPV, P(NPV > 0), Expected Shortfall 5 % des NPV, Break-even-Kapital, Wert je Risikoeinheit
(E[Jahreswert] / Standardabweichung des Jahres-P&L), Sensitivitäten (Kosten ×1,5/×2/×3, Prior −0,05/−0,10, Fixkosten hoch, Betreiberzeit
hoch, Non-Display-Daten, Steuer-Sensitivität), Befundklasse nach §5.7, Varianten V0–V4 (§5.5) und Go/No-Go je Stufe und Profil.
Ziehungen in Gleitkomma (statistische Größen); Gebühren, Fix- und Aufbaukosten sowie alle ausgewiesenen Geldbeträge in Decimal (R-03).
Aufruf: python financials/decision_montecarlo.py [--check]
"""
from __future__ import annotations

import math
import sys
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from financials.cost_model import impact_fraction  # noqa: E402
from financials.stage_costs import fixed_monthly, ops_hours, stage_costs  # noqa: E402
from financials.tax_scenarios import after_tax_sensitivity  # noqa: E402
from lib.calc import Params, Rng, dec, dumps, input_hashes, instruments, load, main_args, mean, money, quantile, stdev, variant_decision, write_or_check  # noqa: E402
from risk.kelly_ruin_simulator import sample_quantile  # noqa: E402
from risk.leverage_calculator import portfolio  # noqa: E402

OUT = "financials/decision_montecarlo_results.json"
SEED = 5_6_2026
PROFILES = ["H5", "H10", "H15", "H20"]
VARIANTS = ["U-KOSTEN", "U-BREAKEVEN", "U-KOSTEN-TFD1-7T", "U-KOSTEN-TFD1"]
BUILD_UNTIL = ["BS-00", "BS-01", "BS-02", "BS-03", "BS-04", "BS-05", "BS-06", "BS-07", "BS-08"]
SENS = {"KOSTEN_X1_5": {"k": 1.5}, "KOSTEN_X2": {"k": 2.0}, "KOSTEN_X3": {"k": 3.0}, "PRIOR_MINUS_0_05": {"shift": 0.05},
        "PRIOR_MINUS_0_10": {"shift": 0.10}, "FIXKOSTEN_HOCH": {"fix_mult": 1.5, "data": "NON_DISPLAY_MANAGED"}, "BETREIBERZEIT_HOCH": {"ops_mult": 2.0},
        "DATEN_NON_DISPLAY_USER": {"data": "NON_DISPLAY_USER"}, "STEUER_SENSITIVITAET": {"tax": True},
        "ALLES_BEIM_BROKER": {"cash_at_broker": 1.0}, "BROKER_ZAHLT_GELDMARKTZINS": {"broker_pays_cash_rate": True},
        "PRIOR_AUF_INDEXNIVEAU": {"sr_index": True}}


def cell_inputs(variant, stage, prof, P, INS, prior, lev, cm, fc):
    ids = prior["admission"][variant][str(stage)]["instruments"]
    basis = prior["admission"][variant][str(stage)]["basis"]
    cell = lev["cells"][variant][str(stage)][prof]
    if not ids:
        return None
    pf = portfolio(ids, INS, P, P.f(f"P-LEV-{prof}-SIGMA"))
    w = [x * cell["scale"] for x in pf["w"]]
    imp_model = load("financials/cost_model_results.json")["impact_model"]      # Marktwirkung nur über das Kostenmodell (R-04, costs.json rules)
    Y, free = float(imp_model["Y"]), float(imp_model["free_share"])
    tau = load("research/turnover_results.json")["strategies"][basis]["time_in_market"]
    nav = float(stage)
    imp_sr, cap_f, comm_month = [], 1.0, {"CME": Decimal(0), "EUREX": Decimal(0)}
    for i, wi in zip(ids, w, strict=True):
        ins, c = INS[i], cm[i]
        notional = float(c["notional_eur"])
        q = max(1.0, wi * nav / notional)
        adv = ins["planning"]["adv_contracts"]["value"]
        imp_side = impact_fraction(ins, q, Y, free) * notional
        n_rt = c["strategies"][basis]["rt_per_year"]
        imp_sr.append(n_rt * 2 * imp_side / float(c["vol_eur_per_year"]["base"]) / math.sqrt(tau))
        cap_f = min(cap_f, P.f("P-RISK-MAX-ADV-SHARE") * adv / q)
        grp = "EUREX" if ins["exchange"] == "EUREX" else "CME"
        comm_month[grp] += dec(n_rt) * 2 * dec(q) * dec(c["commission_side_eur"]) / 12
    md = fc["market_data_monthly_eur"]["ANZEIGE"]
    waiver = dec(md["waiver_commission_eur_per_exchange"])
    # Kursgebühr je Börse entfällt ab der Kommissionsschwelle (Beträge aus registers/costs.json über das Kostenmodell, R-04)
    data_saving = sum((dec(md["per_exchange_monthly_eur"][grp]) for grp in ("CME", "EUREX") if comm_month[grp] >= waiver), Decimal(0))
    return {"ids": ids, "basis": basis, "cell": cell, "sigma": cell["sigma_achieved"] * min(1.0, cap_f), "capacity_factor": min(1.0, cap_f), "D": cell["D"],
            "cbar": cell["mean_cost_sr"], "c_imp": mean(imp_sr), "data_waiver_monthly_eur": data_saving,
            "commission_monthly_eur": {k: money(v) for k, v in comm_month.items()}}


def fixed_annual(P, fc, ci, data="ANZEIGE", fix_mult=1.0, ops_mult=1.0) -> dict:
    base_m = fixed_monthly(fc, P, data)
    if data == "ANZEIGE":
        base_m -= ci["data_waiver_monthly_eur"]
    ops = ops_hours(P) * dec(ops_mult) * dec(P("P-ECO-HOURLY-RATE"))
    risk_fn = dec(fc["external_risk_function_monthly_eur"]) * 12
    total = base_m * 12 * dec(fix_mult) + ops + risk_fn
    return {"running_eur": money(base_m * 12 * dec(fix_mult)), "operator_time_eur": money(ops), "risk_function_eur": money(risk_fn), "total_eur": money(total)}


def simulate(nav, ci, F, C0, audit, prior, P, rng, n, k=1.0, shift=0.0, tax=False, cash_at_broker=None, broker_pays_cash_rate=False, sr_index=False):
    qs, grid = prior["gross_quantiles"][ci["basis"]], prior["quantile_grid"]
    H, ramp = int(P("P-ECO-HORIZON-Y")), int(P("P-ECO-RAMP-YEARS"))
    r = P.f("P-ECO-DISCOUNT")
    phi = P.f("P-ECO-CASH-AT-BROKER") if cash_at_broker is None else cash_at_broker
    spread = 0.0 if broker_pays_cash_rate else (P.f("P-ECO-CASH-RATE") - P.f("P-ECO-BROKER-RATE"))
    opp = nav * phi * spread
    unc = P.f("P-ECO-COST-UNC-SD")
    sig = ci["sigma"]
    Ff, C0f, audf = float(F), float(C0), float(audit)
    ay = int(P("P-ECO-AUDIT-YEAR"))
    tax_rate = P.f("P-ECO-TAX-SENS")
    npv, srs, annual = [], [], []
    for _ in range(n):
        g = sample_quantile(qs, grid, rng.u())
        u = rng.lognormal_mean_sd(1.0, unc)
        S = ci["D"] * (g - (ci["cbar"] + ci["c_imp"]) * k * u) - shift
        if sr_index:
            lo, hi = P("P-ECO-V1-SR")
            S = lo + (hi - lo) * rng.u()           # realisierte Netto-Sharpe großer Trendfolger (Indexniveau) statt hergeleitetem Prior
        srs.append(S)
        tot = -C0f - audf / (1 + r) ** ay
        for t in range(1, H + 1):
            if t <= ramp:
                continue
            v = nav * sig * (S + rng.normal()) - opp - Ff
            if tax:
                v = after_tax_sensitivity(v, tax_rate)
            annual.append(v)
            tot += v / (1 + r) ** t
        npv.append(tot)
    sn = sorted(npv)
    k5 = max(1, len(sn) // 20)
    mS = mean(srs)
    e_annual = nav * sig * mS - opp - Ff
    sd_annual = nav * sig * math.sqrt(1 + stdev(srs) ** 2)
    rate = sig * mS - phi * spread
    return {"sr_mean": mS, "sr_p05": quantile(sorted(srs), 0.05), "sr_p95": quantile(sorted(srs), 0.95), "p_sr_positive": sum(1 for s in srs if s > 0) / n,
            "excess_rate": rate, "expected_annual_value_eur": money(e_annual), "sd_annual_pnl_eur": money(sd_annual),
            "value_per_risk_unit": e_annual / sd_annual if sd_annual > 0 else 0.0, "npv_mean_eur": money(mean(npv)), "npv_p05_eur": money(quantile(sn, 0.05)),
            "npv_p50_eur": money(quantile(sn, 0.5)), "npv_p95_eur": money(quantile(sn, 0.95)), "npv_es5_eur": money(mean(sn[:k5])),
            "p_npv_positive": sum(1 for x in npv if x > 0) / n,
            "break_even_capital_eur": money(Ff / rate) if rate > 0 else None}


def classify(res, admissible, reasons, P, v1_low):
    if not admissible:
        return "PROFILE_NOT_ADMISSIBLE", reasons
    if res["excess_rate"] <= 0:
        return "NON_POSITIVE_BASE", ["Mehrertragsrate σ·E[S] − φ·(r_Geldmarkt − r_Broker) ≤ 0"]
    if float(res["expected_annual_value_eur"]) <= 0 or res["p_npv_positive"] < P.f("P-ECO-MARGINAL-P"):
        return "NOT_VIABLE_AT_CAPITAL", [f"E[Jahreswert] {res['expected_annual_value_eur']} EUR; P(NPV > 0) = {res['p_npv_positive']:.2f}"]
    if v1_low >= res["value_per_risk_unit"]:
        return "DOMINATED_BY_ALTERNATIVE", [f"V1-Untergrenze Sharpe {v1_low} ≥ Wert je Risikoeinheit {res['value_per_risk_unit']:.3f}"]
    if res["p_npv_positive"] >= P.f("P-ECO-VIABLE-P"):
        return "VIABLE", []
    return "MARGINAL", [f"P(NPV > 0) = {res['p_npv_positive']:.2f} unter {P('P-ECO-VIABLE-P')}"]


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    INS = {i["id"]: i for i in instruments()}
    prior = load("research/prior_results.json")
    lev = load("risk/leverage_results.json")
    cmr = load("financials/cost_model_results.json")
    cm = {r["id"]: r for r in cmr["instruments"]}
    fc = cmr["fixed_costs"]
    sc = stage_costs()
    C0 = sum((dec(sc[s]["total_eur"]) for s in BUILD_UNTIL), Decimal(0))
    audit = dec(sc["BS-10"]["total_eur"])
    rng = Rng(SEED)
    n_base = int(P("P-ECO-MC-DRAWS"))
    n_sens = max(2000, n_base // 5)
    v1 = P("P-ECO-V1-SR")
    stages = P("P-ECO-CAPITAL-STAGES")
    table = {}
    for variant in VARIANTS:
        table[variant] = {}
        for stage in stages:
            table[variant][str(stage)] = {}
            for prof in PROFILES:
                ci = cell_inputs(variant, stage, prof, P, INS, prior, lev, cm, fc)
                if ci is None:
                    table[variant][str(stage)][prof] = {"class": "NOT_VIABLE_AT_CAPITAL",
                                                         "reasons": ["Kein Instrument erfüllt bei diesem Kapital die Zulassung (Kosten je Risikoeinheit, Kontraktgröße)"],
                                                         "universe_size": 0}
                    continue
                F = fixed_annual(P, fc, ci)
                base = simulate(float(stage), ci, dec(F["total_eur"]), C0, audit, prior, P, rng, n_base)
                cls, why = classify(base, ci["cell"]["admissible"], ci["cell"]["reasons"], P, v1[0])
                rec = {"class": cls, "reasons": why, "universe_size": len(ci["ids"]), "sigma_effective": ci["sigma"], "capacity_factor": ci["capacity_factor"],
                       "impact_sr_cost": ci["c_imp"], "commission_monthly_eur": ci["commission_monthly_eur"], "fixed_costs_annual": F, "base": base}
                if True:
                    sens = {}
                    for name, sp in SENS.items():
                        Fs = fixed_annual(P, fc, ci, data=sp.get("data", "ANZEIGE"), fix_mult=sp.get("fix_mult", 1.0), ops_mult=sp.get("ops_mult", 1.0))
                        r = simulate(float(stage), ci, dec(Fs["total_eur"]), C0, audit, prior, P, rng, n_sens, k=sp.get("k", 1.0), shift=sp.get("shift", 0.0),
                                     tax=sp.get("tax", False), cash_at_broker=sp.get("cash_at_broker"), broker_pays_cash_rate=sp.get("broker_pays_cash_rate", False),
                                     sr_index=sp.get("sr_index", False))
                        c2, _ = classify(r, ci["cell"]["admissible"], ci["cell"]["reasons"], P, v1[0])
                        sens[name] = {"class": c2, "p_npv_positive": r["p_npv_positive"], "npv_mean_eur": r["npv_mean_eur"],
                                      "expected_annual_value_eur": r["expected_annual_value_eur"]}
                    rec["sensitivities"] = sens
                    rec["sensitivities_rate_only"] = {k2: v2["expected_annual_value_eur"] for k2, v2 in sens.items()}
                    if cls == "VIABLE" and any(sens[k]["class"] != "VIABLE" for k in ("KOSTEN_X1_5", "PRIOR_MINUS_0_05")):
                        rec["class"] = "MARGINAL"
                        rec["reasons"] = ["Sensitivität Kosten ×1,5 oder Prior −0,05 kippt den Befund"]
                table[variant][str(stage)][prof] = rec
    # ---------------------------------------------------------------------------------------- Varianten V0–V4 (Profil H5)
    variants_cmp = {}
    ops_rate = dec(P("P-ECO-HOURLY-RATE"))
    b5 = sc["BS-05"]
    b5_build = dec(b5["human_eur"]) + dec(b5["agent_eur"])
    for stage in stages:
        nav = Decimal(stage)
        v = {"V0": {"expected_annual_value_eur": money(0), "value_per_risk_unit": None, "note": "Geldmarkt; Vergleichsmaßstab (Überrendite 0)"}}
        v1_time = dec(P("P-ECO-V1-OPS-MIN")) * 12 / 60 * ops_rate
        v1_sig = dec(P("P-ECO-V1-SIGMA"))
        v["V1"] = {"sharpe_range": v1, "expected_annual_value_eur_range": [money(nav * v1_sig * dec(x) - v1_time) for x in v1],
                   "value_per_risk_unit_range": [float((nav * v1_sig * dec(x) - v1_time) / (nav * v1_sig)) for x in v1], "build_effort_bs05_eur": money(0),
                   "note": "Produkte X-V1-PRODUCTS offen; Indexwerte nach Gebühren"}
        alt = table["U-KOSTEN-TFD1"][str(stage)]["H5"]
        if "base" in alt:
            v["V4_ALTERNATIVE_TFD1"] = {"expected_annual_value_eur": alt["base"]["expected_annual_value_eur"], "value_per_risk_unit": alt["base"]["value_per_risk_unit"],
                                        "p_npv_positive": alt["base"]["p_npv_positive"], "class": alt["class"],
                                        "note": "langsame Trendfolge ohne 7-Tage-Grenze; nur mit Betreiberentscheidung (BQ-04)"}
        # V4 = registrierte Strategiefamilie (Universum U-KOSTEN, Profil H5); das Sensitivitätsuniversum U-BREAKEVEN steht nur zur Information
        # daneben. V2 und V3 nutzen dieselben Kontrakte und Kosten wie die jeweils gerechnete V4-Zelle (Feld universe).
        v1_lo, v1_hi = min(v["V1"]["value_per_risk_unit_range"]), max(v["V1"]["value_per_risk_unit_range"])
        for key, var in (("V4", "U-KOSTEN"), ("V4_SENSITIVITY", "U-BREAKEVEN")):
            cell = table[var][str(stage)]["H5"]
            if "base" not in cell:
                v[key] = {"universe": var, "class": cell["class"], "note": "keine Simulation: Universum bei diesem Kapital leer"}
                continue
            b = cell["base"]
            ci = cell_inputs(var, stage, "H5", P, INS, prior, lev, cm, fc)
            v[key] = {"universe": var, "expected_annual_value_eur": b["expected_annual_value_eur"], "value_per_risk_unit": b["value_per_risk_unit"],
                      "npv_mean_eur": b["npv_mean_eur"], "p_npv_positive": b["p_npv_positive"], "build_effort_bs05_eur": money(b5_build),
                      "class": cell["class"]}
            if key != "V4":
                continue
            orders = sum(cm[i]["strategies"][ci["basis"]]["rt_per_year"] * 2 for i in ci["ids"])
            v2_time = dec(orders) * dec(P("P-ECO-V2-MIN-PER-ORDER")) / 60 * ops_rate
            v2_sr = ci["D"] * (prior["median_gross"][ci["basis"]] * P.f("P-ECO-V2-EDGE-FACTOR") - ci["cbar"] - ci["c_imp"])
            v2_cash = nav * dec(P("P-ECO-CASH-AT-BROKER")) * (dec(P("P-ECO-CASH-RATE")) - dec(P("P-ECO-BROKER-RATE")))
            v2_md = dec(fc["market_data_monthly_eur"]["ANZEIGE"]["monthly_eur"]) * 12
            v2_val = nav * dec(ci["sigma"]) * dec(v2_sr) - v2_time - v2_cash - v2_md
            v2_build = b5_build * dec(P("P-ECO-V2-BUILD-FACTOR"))
            v3_build = b5_build * dec(P("P-ECO-V3-BUILD-FACTOR"))
            v["V2"] = {"universe": var, "expected_annual_value_eur_approx": money(v2_val),
                       "value_per_risk_unit_approx": float(v2_val / (nav * dec(ci["sigma"]))) if ci["sigma"] > 0 else None,
                       "operator_time_eur": money(v2_time), "cash_drag_eur": money(v2_cash), "market_data_eur": money(v2_md),
                       "build_effort_bs05_eur": money(v2_build),
                       "note": "Näherung ohne Monte-Carlo: Median-Prior, Wert je Risikoeinheit ohne Unsicherheit der Sharpe-Ratio; Signal-Skript, "
                               "manuelle Orders mit Schutzstopps"}
            v["V3"] = {"universe": var, "expected_annual_value_eur": b["expected_annual_value_eur"], "value_per_risk_unit": b["value_per_risk_unit"],
                       "npv_mean_eur_approx": money(dec(b["npv_mean_eur"]) + (b5_build - v3_build)),
                       "build_effort_bs05_eur": money(v3_build),
                       "note": "gleiche Kontrakte, Kosten und Jahreswerte wie V4; nur der Aufbau ist kleiner (NPV = V4 plus eingesparter Aufbau)"}
        v4 = v["V4"]
        v["decision"] = variant_decision(v4["class"] if "value_per_risk_unit" in v4 else None, v4.get("value_per_risk_unit"), v1_lo, v1_hi)
        v["v1_lower_bound_at_least_v4"] = ("value_per_risk_unit" in v4 and v1_lo >= v4["value_per_risk_unit"])
        variants_cmp[str(stage)] = v
    # ---------------------------------------------------------------------------------------- Go/No-Go
    gonogo = {}
    for stage in stages:
        gonogo[str(stage)] = {}
        for prof in PROFILES:
            c = table["U-KOSTEN"][str(stage)][prof]["class"]
            dec_ = "GO" if c == "VIABLE" else ("PILOT_GEDECKELT" if c == "MARGINAL" else "NO_GO")
            gonogo[str(stage)][prof] = {"decision_real_money": dec_, "class_registered": c,
                                        "class_sensitivity_breakeven_universe": table["U-BREAKEVEN"][str(stage)][prof]["class"],
                                        "class_alternative_TFD1_7T_within_operator_limits": table["U-KOSTEN-TFD1-7T"][str(stage)][prof]["class"],
                                        "class_alternative_TFD1_needs_operator_decision": table["U-KOSTEN-TFD1"][str(stage)][prof]["class"],
                                        "demo_paper": "ZULAESSIG_MIT_AUSGABENDECKEL"}
    out = {"calculator": "financials/decision_montecarlo.py", "model": "MOD-DMC", "seed": SEED, "draws_base": n_base, "draws_sensitivity": n_sens,
           "inputs": input_hashes(["parameters.json", "research/prior_results.json", "risk/leverage_results.json", "financials/cost_model_results.json",
                                   "implementation/build_stages.json", "registers/instruments.json", "research/turnover_results.json"]),
           "operating_model": "Eigenkonto des Betreibers; B1–B4 nicht bewertet (BQ-02)", "taxes": "vor Steuern; Steuer nur als Sensitivität (BQ-03)",
           "build_cost_until_pilot_eur": money(C0), "audit_cost_eur": money(audit), "operator_hours_per_year": float(ops_hours(P)),
           "stage_costs": sc, "table": table, "variants_V0_V4": variants_cmp, "go_no_go": gonogo}
    ok = write_or_check(OUT, dumps(out), a.check)
    if not a.check:
        print("Aufbaukosten bis Pilot:", money(C0), "Betreiberstunden/Jahr:", round(float(ops_hours(P)), 1))
        for variant in VARIANTS:
            for stage in stages:
                row = [f"{variant:<17}{stage:>10}"]
                for prof in PROFILES:
                    r = table[variant][str(stage)][prof]
                    b = r.get("base")
                    row.append(f"{prof}:{r['class'][:14]:<14}" + (f" P={b['p_npv_positive']:.2f} E={b['expected_annual_value_eur']}" if b else ""))
                print(" | ".join(row))
        for st, v in variants_cmp.items():
            print(st, v["decision"])
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
