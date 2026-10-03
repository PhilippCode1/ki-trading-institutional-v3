#!/usr/bin/env python3
"""Prior-Herleitung (§6.3, Befund CR-5 „Prior nur erzählend“; Modell MOD-PRIOR).

Leitet die Erwartung je Strategie und für das Portfolio rechnerisch aus der Literaturtabelle ab
(research/sources/R3_literature_prior.json; Anker und Abschläge in parameters.json, Gruppe PRIOR):

  Brutto-Sharpe je Instrument (gemeinsamer Faktor je Strategie, Monte-Carlo über die Unsicherheit der Faktoren):
    S-TF  = Anker12M · Verhältnis(1M/12M) · h_TF · Veröffentlichung · Mehrfachtest_TF · Umsetzung + Carry-Filter-Zuschlag
    S-IM  = Klassen-Sharpe/√N_eff · h_IM · Veröffentlichung · Mehrfachtest_IM · Umsetzung   (N_eff = N/(1+(N−1)ρ))
    S-REV = Normal(0, σ)                                                                          (Prior bei null, Hürde t > 3)
    TF-D1 = Anker12M · Verhältnis(3M/12M) · Veröffentlichung · Mehrfachtest_TF · Umsetzung ; TF-D1-7T zusätzlich · Zeitstoppfaktor
  Netto je Instrument = Brutto − Kosten in Sharpe-Einheiten (financials/cost_model_results.json, Basisszenario).
  Zulassung je Kapitalstufe: Börsenzugang, keine Sperre, Tagesvolumen, Kosten ≤ Anteil × Median-Brutto (S-TF), Kontraktgröße ≤ Anteil des
    Instrumentbudgets (Referenz Profil H5), je Basiswert nur ein Kontrakt (der günstigste zulässige).
  Portfolio je Strategie: SR = D · Mittel(Netto_i) bei gleichen Risikoanteilen; D = 1/√(rᵀΡr), gedeckelt.
  Kombination der Strategien: SR = Σ a_k SR_k / √(aᵀΨa).

Synthetische Monte-Carlo-Ziehungen über Parameterunsicherheit; keine Aussage über eine tatsächlich vorhandene Edge (R-02).
Aufruf: python research/prior_derivation.py [--check]
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from financials.cost_model import impact_fraction  # noqa: E402
from lib.calc import Params, Rng, dumps, input_hashes, instruments, load, main_args, mean, quantile, write_or_check  # noqa: E402

OUT = "research/prior_results.json"
SEED = 6_3_2026
STRATS = ["S-TF", "S-IM", "S-REV"]
BASES = ["S-BASE-TFD1", "S-BASE-TFD1-7T"]
Q_GRID = [i / 200 for i in range(1, 200)]
RATES = {"STIR", "ANLEIHE_KURZ", "ANLEIHE_MITTEL", "ANLEIHE_LANG", "RENDITE"}


def lit(study: str, name: str) -> float:
    for s in load("research/sources/R3_literature_prior.json")["studies"]:
        if s["id"] == study:
            for k in s["other_key_numbers"]:
                if k["name"] == name:
                    return float(k["value"])
    raise KeyError(f"{study}: {name}")


def im_class(ins) -> str:
    if ins["asset_class"] in ("STIR", "ANLEIHE", "RENDITE"):
        return "ANLEIHE"
    if ins["asset_class"] == "FX":
        return "FX"
    return "ROHSTOFF"


def summary(vals) -> dict:
    v = sorted(vals)
    return {"mean": mean(v), "p05": quantile(v, 0.05), "p25": quantile(v, 0.25), "p50": quantile(v, 0.5), "p75": quantile(v, 0.75),
            "p95": quantile(v, 0.95), "p_positive": sum(1 for x in v if x > 0) / len(v)}


def hist_years(ins, INS, req_hist) -> float:
    """Verfügbare Intraday-Historie; Micro- und Mini-Kontrakte dürfen den Standardkontrakt auf denselben Basiswert nutzen (Proxy-Regel §6.5)."""
    h = ins["data_history"]["years_available"]
    if h < req_hist and ins["standard_ref"] in INS:
        h = max(h, INS[ins["standard_ref"]]["data_history"]["years_available"])
    return h


def corr_matrix(ids, rcls, P):
    within = P("P-PRI-RHO-WITHIN")
    rate_grp = P.f("P-PRI-RHO-ANLEIHE-GROUP")
    between = P.f("P-PRI-RHO-BETWEEN")
    n = len(ids)
    M = [[0.0] * n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            ca, cb = rcls[ids[a]], rcls[ids[b]]
            if a == b:
                M[a][b] = 1.0
            elif ca == cb:
                M[a][b] = within[ca]
            elif ca in RATES and cb in RATES:
                M[a][b] = rate_grp
            else:
                M[a][b] = between
    return M


def div_mult(ids, rcls, P, shares=None) -> float:
    n = len(ids)
    if n == 0:
        return 0.0
    r = shares or [1.0 / n] * n
    M = corr_matrix(ids, rcls, P)
    q = math.fsum(r[a] * r[b] * M[a][b] for a in range(n) for b in range(n))
    return min(P.f("P-STR-IDM-CAP"), 1.0 / math.sqrt(q))


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    A = P("P-PRI-ANCHORS")
    cm = {r["id"]: r for r in load("financials/cost_model_results.json")["instruments"]}
    INS = {i["id"]: i for i in instruments()}
    rcls = {k: v["risk_class"] for k, v in INS.items()}

    # ------------------------------------------------------------------------------------------ Anker aus der Literaturtabelle
    tf12 = [lit(*x) for x in A["TF12_INSTR"]]
    r1m = [lit(*n) / lit(*d) for n, d in A["TF_RATIO_1M_12M"]]
    r3m = [lit(*n) / lit(*d) for n, d in A["TF_RATIO_3M_12M"]]
    im_sr = {c: lit(*v) for c, v in A["IM_CLASS_SR"].items()}
    im_n = {c: lit(*v) for c, v in A["IM_CLASS_N"].items()}
    rho_im = P.f("P-PRI-IM-RHO-CLASS")
    im_neff = {c: im_n[c] / (1 + (im_n[c] - 1) * rho_im) for c in im_n}
    im_inst = {c: im_sr[c] / math.sqrt(im_neff[c]) for c in im_sr}
    decay_low_lit = 1 - lit(*A["DECAY_POST_PUB"]) / 100
    mt_low_lit = lit(*A["MT_EXAMPLE"][0]) / lit(*A["MT_EXAMPLE"][1])
    plaus = [lit(*x) for x in A["PLAUS_NET"]]
    checks = {"decay_lower_bound_matches_literature": abs(P("P-PRI-DECAY")[0] - round(decay_low_lit, 2)) < 1e-9,
              "multiple_testing_lower_bound_matches_literature": abs(P("P-PRI-MT-IM")[0] - round(mt_low_lit, 2)) < 1e-9}

    # ------------------------------------------------------------------------------------------ Monte-Carlo über die Faktoren
    rng = Rng(SEED)
    n = int(P("P-RES-PRIOR-DRAWS"))
    lo_hi = lambda pid: (P(pid)[0], P(pid)[1])  # noqa: E731
    h_tf, h_im, dec, mt_tf, mt_im, impl, ca, t7 = (lo_hi(x) for x in ["P-PRI-H-TF", "P-PRI-H-IM", "P-PRI-DECAY", "P-PRI-MT-TF", "P-PRI-MT-IM",
                                                                        "P-PRI-IMPL", "P-PRI-CA-UPLIFT", "P-PRI-TFD1-7T"])
    rev_sd = P.f("P-PRI-REV-SD")
    G = {"S-TF": [], "S-TF-OHNE-CA": [], "S-REV": [], "S-BASE-TFD1": [], "S-BASE-TFD1-7T": []}
    G_IM = {c: [] for c in im_inst}
    for _ in range(n):
        d = rng.uniform(*dec)
        im = rng.uniform(*impl)
        anc = rng.choice(tf12)
        m_tf = rng.uniform(*mt_tf)
        g = anc * rng.choice(r1m) * rng.uniform(*h_tf) * d * m_tf * im
        G["S-TF-OHNE-CA"].append(g)
        G["S-TF"].append(g + rng.uniform(*ca))
        hi = rng.uniform(*h_im)
        mi = rng.uniform(*mt_im)
        for c in im_inst:
            G_IM[c].append(im_inst[c] * hi * d * mi * im)
        G["S-REV"].append(rng.normal(0.0, rev_sd))
        gb = anc * rng.choice(r3m) * d * m_tf * im
        G["S-BASE-TFD1"].append(gb)
        G["S-BASE-TFD1-7T"].append(gb * rng.uniform(*t7))

    def gross_draws(strategy, ins):
        return G_IM[im_class(ins)] if strategy == "S-IM" else G[strategy]

    med_tf = quantile(sorted(G["S-TF"]), 0.5)

    # ------------------------------------------------------------------------------------------ je Instrument: Kosten und Netto
    per_ins = []
    for iid, ins in INS.items():
        c = cm[iid]["strategies"]
        row = {"id": iid, "symbol": ins["symbol"], "risk_class": ins["risk_class"], "size_class": ins["size_class"], "im_class": im_class(ins),
               "cost_sr": {k: c[k]["sr_cost_per_year"]["base"] for k in STRATS + BASES}}
        for k in ["S-TF", "S-IM", "S-BASE-TFD1"]:
            gd = gross_draws(k, ins)
            nets = [g - row["cost_sr"][k] for g in gd]
            row[f"net_{k}"] = {"p50": quantile(sorted(nets), 0.5), "p_positive": sum(1 for x in nets if x > 0) / len(nets)}
        row["cost_share_of_median_gross_S-TF"] = row["cost_sr"]["S-TF"] / med_tf if med_tf > 0 else None
        per_ins.append(row)

    # ------------------------------------------------------------------------------------------ Zulassung je Kapitalstufe
    stages = P("P-ECO-CAPITAL-STAGES")
    share_max = P.f("P-UNI-COST-SHARE-MAX")
    min_adv = P.f("P-UNI-MIN-ADV")
    max_cr = P.f("P-UNI-MAX-CONTRACT-RISK")
    sig_ref = P.f("P-LEV-H5-SIGMA")
    variants = {"U-KOSTEN": ("S-TF", share_max), "U-BREAKEVEN": ("S-TF", 1.0), "U-ALLE": ("S-TF", None),
                "U-KOSTEN-TFD1-7T": ("S-BASE-TFD1-7T", share_max), "U-KOSTEN-TFD1": ("S-BASE-TFD1", share_max)}

    imp_model = load("financials/cost_model_results.json")["impact_model"]      # Marktwirkung nur über das Kostenmodell (R-04, costs.json rules)
    Y, free = float(imp_model["Y"]), float(imp_model["free_share"])
    turn = load("research/turnover_results.json")["strategies"]
    med = {k: quantile(sorted(G[k]), 0.5) for k in ("S-TF", "S-BASE-TFD1", "S-BASE-TFD1-7T")}

    def total_cost(ins, budget_eur, basis="S-TF"):
        """Kosten der Basisstrategie in Sharpe-Einheiten je Jahr inklusive Marktwirkung bei der typischen Positionsgröße dieser Kapitalstufe."""
        c = cm[ins["id"]]
        vol = float(c["vol_eur_per_year"]["base"])
        q = max(1.0, budget_eur / vol)
        imp = impact_fraction(ins, q, Y, free) * float(c["notional_eur"])
        n_rt = c["strategies"][basis]["rt_per_year"]
        return c["strategies"][basis]["sr_cost_per_year"]["base"] + n_rt * 2 * imp / vol / math.sqrt(turn[basis]["time_in_market"])

    req_hist = P.f("P-RES-DEV-YEARS") + P.f("P-RES-HOLDOUT-YEARS")

    def base_ok(ins, history=True):
        if ins["access"]["status"] != "PRIMAERBROKER_BOERSE_ANGEBOTEN" or ins["blocked"]:
            return False
        return ins["planning"]["adv_contracts"]["value"] >= min_adv and (not history or hist_years(ins, INS, req_hist) >= req_hist)

    history_excluded = sorted(i["id"] for i in INS.values() if i["access"]["status"] == "PRIMAERBROKER_BOERSE_ANGEBOTEN" and not i["blocked"]
                              and hist_years(i, INS, req_hist) < req_hist)

    def admit(nav, cost_cap, basis="S-TF", history=True):
        """Größtes zulässiges Universum: je Basiswert der günstigste Kontrakt; bei Kostenobergrenze wird die größte Zahl k der nach
        Grundkosten günstigsten Basiswerte gesucht, bei der alle k Kosten- und Kontraktgrößenregel bei der Positionsgröße dieser
        Kapitalstufe erfüllen (mehr Instrumente = kleinere Positionen = weniger Marktwirkung).
        history=False nur für die hypothetische Hebelkalibrierung (U-HANDELBAR): handelbar, aber ohne Forschungshistorie."""
        cand = [i for i in INS.values() if base_ok(i, history)]
        groups = {}
        for i in cand:
            groups.setdefault(i["standard_ref"] or i["id"], []).append(i)

        def pick(gkeys, budget):
            out = []
            for g in gkeys:
                ok = []
                for m in groups[g]:
                    if float(cm[m["id"]]["vol_eur_per_year"]["base"]) > max_cr * budget:
                        continue
                    tc = total_cost(m, budget, basis)
                    if cost_cap is not None and tc > cost_cap * med[basis]:
                        continue
                    ok.append((tc, m["id"]))
                if ok:
                    out.append(sorted(ok)[0][1])
            return sorted(out)

        if cost_cap is None:
            ids = sorted({g: v[0]["id"] for g, v in groups.items()}.values())
            for _ in range(30):
                if not ids:
                    break
                budget = nav * sig_ref * div_mult(ids, rcls, P) / len(ids)
                new = pick(sorted(groups), budget)
                if new == ids:
                    break
                ids = new
        else:
            ids = []
            for k in range(len(groups), 0, -1):
                sel = None
                D = 1.0
                for _ in range(3):
                    budget = nav * sig_ref * D / k
                    passing = []
                    for g in sorted(groups):
                        best = None
                        for m in groups[g]:
                            if float(cm[m["id"]]["vol_eur_per_year"]["base"]) > max_cr * budget:
                                continue
                            tc = total_cost(m, budget, basis)
                            if tc <= cost_cap * med[basis] and (best is None or tc < best[0]):
                                best = (tc, m["id"])
                        if best:
                            passing.append(best)
                    if len(passing) < k:
                        sel = None
                        break
                    sel = sorted(x[1] for x in sorted(passing)[:k])
                    D = div_mult(sel, rcls, P)
                if sel is not None:
                    ids = sel
                    break
        budget = nav * sig_ref * div_mult(ids, rcls, P) / len(ids) if ids else 0.0
        return ids, ({i: total_cost(INS[i], budget, basis) for i in ids} if ids else {})

    adm = {}
    port = {}
    for vname, (basis, cap_share) in variants.items():
        adm[vname], port[vname] = {}, {}
        for nav in stages:
            ids, tcost = admit(nav, cap_share, basis)
            D = div_mult(ids, rcls, P) if ids else 0.0
            adm[vname][str(nav)] = {"basis": basis, "instruments": ids, "n": len(ids), "D": D,
                                    "classes": sorted({rcls[i] for i in ids}),
                                    "mean_total_cost_sr_basis_incl_impact": mean(list(tcost.values())) if ids else None,
                                    "mean_cost_sr": {k: (mean([cm[i]["strategies"][k]["sr_cost_per_year"]["base"] for i in ids]) if ids else None)
                                                     for k in STRATS + BASES}}
            res = {}
            for k in STRATS + BASES:
                if not ids:
                    res[k] = None
                    continue
                costs_k = [cm[i]["strategies"][k]["sr_cost_per_year"]["base"] + (tcost[i] - cm[i]["strategies"][basis]["sr_cost_per_year"]["base"])
                           * (cm[i]["strategies"][k]["rt_per_year"] / cm[i]["strategies"][basis]["rt_per_year"]) for i in ids]
                if k == "S-IM":
                    draws = [D * mean([G_IM[im_class(INS[i])][j] - costs_k[t] for t, i in enumerate(ids)]) for j in range(n)]
                else:
                    cbar = mean(costs_k)
                    draws = [D * (g - cbar) for g in G[k]]
                res[k] = draws
            # Kombination der registrierten Strategien
            shares = P("P-STR-RISK-SHARES")
            rho = P("P-PRI-RHO-STRAT")

            def comb(included, ids=ids, res=res, shares=shares, rho=rho):
                if not ids or not included:
                    return None
                aw = [shares[k] for k in included]
                var = 0.0
                for x, kx in enumerate(included):
                    for y, ky in enumerate(included):
                        r = 1.0 if kx == ky else rho.get(f"{kx}|{ky}", rho.get(f"{ky}|{kx}", 0.0))
                        var += aw[x] * aw[y] * r
                return [math.fsum(aw[x] * res[k][j] for x, k in enumerate(included)) / math.sqrt(var) for j in range(n)]

            reg = comb(STRATS)
            if basis == "S-TF":
                dec_set = [k for k in STRATS if res[k] is not None and sum(1 for v in res[k] if v > 0) / n > 0.5]
                decision = comb(dec_set)
            else:
                dec_set = [basis] if res[basis] is not None and sum(1 for v in res[basis] if v > 0) / n > 0.5 else []
                decision = res[basis] if dec_set else None
            port[vname][str(nav)] = {k: (summary(v) if v is not None else None) for k, v in res.items()}
            port[vname][str(nav)]["KOMBINIERT_REGISTRIERT"] = summary(reg) if reg else None
            port[vname][str(nav)]["ENTSCHEIDUNG"] = {"strategies": dec_set, "summary": summary(decision) if decision else None}
            if res[basis] is not None:
                port[vname][str(nav)]["PLAUSIBILITAET"] = {
                    "index_net_sharpe_range": plaus, "median_portfolio": quantile(sorted(res[basis]), 0.5),
                    "p_above_upper_index_value": sum(1 for v in res[basis] if v > max(plaus)) / n,
                    "flag_above_realized_index": quantile(sorted(res[basis]), 0.5) > max(plaus)}

    # Hypothetisches Universum für die Hebelkalibrierung (§7.2): handelbar, ohne Kosten- und Historienfilter; nicht forschungsfähig
    adm["U-HANDELBAR"] = {}
    for nav in stages:
        ids, _ = admit(nav, None, "S-TF", history=False)
        adm["U-HANDELBAR"][str(nav)] = {"basis": "S-TF", "instruments": ids, "n": len(ids), "D": div_mult(ids, rcls, P) if ids else 0.0,
                                        "classes": sorted({rcls[i] for i in ids}), "research_admissible": False,
                                        "without_history": sorted(i for i in ids if hist_years(INS[i], INS, req_hist) < req_hist)}

    # ------------------------------------------------------------------------------------------ Ausgabe
    out = {
        "calculator": "research/prior_derivation.py", "model": "MOD-PRIOR", "seed": SEED, "draws": n, "synthetic_uncertainty_draws": True,
        "inputs": input_hashes(["parameters.json", "research/sources/R3_literature_prior.json", "financials/cost_model_results.json",
                                "registers/instruments.json"]),
        "anchors": {"tf12_per_instrument": tf12, "ratio_1m_12m": r1m, "ratio_3m_12m": r3m, "im_class_sr": im_sr, "im_class_n": im_n,
                    "im_class_neff": im_neff, "im_per_instrument": im_inst, "decay_lower_bound_literature": decay_low_lit,
                    "multiple_testing_lower_bound_literature": mt_low_lit, "plausibility_net_realized": plaus, "consistency_checks": checks},
        "gross_per_instrument": {k: summary(v) for k, v in G.items()} | {f"S-IM:{c}": summary(v) for c, v in G_IM.items()},
        "gross_quantiles": {k: [quantile(sorted(v), q) for q in Q_GRID] for k, v in G.items()} | {f"S-IM:{c}": [quantile(sorted(v), q) for q in Q_GRID]
                                                                                              for c, v in G_IM.items()},
        "quantile_grid": Q_GRID,
        "median_gross_S-TF": med_tf, "median_gross": med,
        "admission_rule": {"cost_share_max": share_max, "cost_threshold_sr": share_max * med_tf, "variants": {k: list(v) for k, v in variants.items()},
                           "min_adv": min_adv, "max_contract_risk_share": max_cr,
                           "reference_sigma": sig_ref, "one_contract_per_underlying": True,
                           "cost_includes_impact_at_stage_size": True,
                           "min_history_years": req_hist, "history_excluded": history_excluded},
        "instruments": per_ins,
        "admission": adm,
        "portfolio": port,
    }
    ok = write_or_check(OUT, dumps(out), a.check)
    if not a.check:
        print("Median Brutto S-TF je Instrument:", round(med_tf, 4), "Kostenschwelle:", round(share_max * med_tf, 4))
        for v in variants:
            for nav in stages:
                ad = adm[v][str(nav)]
                pe = port[v][str(nav)]
                tf = pe[ad["basis"]]
                print(f"{v:<17} {nav:>10} n={ad['n']:>2} D={ad['D']:.2f} {ad['basis']} p50={tf['p50'] if tf else float('nan'):+.3f} P>0={tf['p_positive'] if tf else 0:.2f}"
                      f"  Entscheidung {pe['ENTSCHEIDUNG']['strategies']}")
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
