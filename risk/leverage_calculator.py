#!/usr/bin/env python3
"""Hebel- und Profilrechner (§7.2–§7.4, D3-02; Modell MOD-LEV).

Rechnet je Universumsvariante (aus research/prior_results.json), Kapitalstufe und Profil H5–H20:
  * Gewichte bei Risikoparität: w_i = k · r_i / σ_i mit k = σ_p · D  →  L_g = Σ|w_i| = D · σ_p / σ_h  (Anhang A)
  * Lückenverlust ΔNAV ≈ −Σ|w_i|·Lücke_i (ungünstigste Richtung, Korrelation 1): historische Klassenlücke und k·σ_Tag (k = 5, 10)
  * Größenregel der Betreiber-Grenze: Wochenendfaktor × Lückenstress ≤ Tagesgrenze − Reserve (DEC-DS-10; dauerhaft, weil die Positionen
    außer S-IM über Wochenenden gehalten werden)  →  Skalierung von σ_p und L_g
  * Margin-Auslastung M/E (Basis, +50 %, +100 %) gegen Profilgrenze und De-Risking-Schwelle
  * Hebeldeckel je Risikoklasse (Klasse allein darf das Lückenbudget nicht überschreiten)
  * Hebelkalibrierung: Zins-Risikoanteil, der L_g = Profilgrenze bei Ziel-σ_p ergibt, und seine Kosten
  * Bandbericht: Zeitanteile L_g < 5×, im Band, an der Grenze (Simulation diskreter Positionen, τ aus der Umschlagssimulation)
  * Zulässigkeit je Profil (PROFILE_NOT_ADMISSIBLE mit Gründen)
Aufruf: python risk/leverage_calculator.py [--check]
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.calc import Params, Rng, dumps, gap_rule_ok, input_hashes, instruments, load, main_args, write_or_check  # noqa: E402
from research.prior_derivation import corr_matrix  # noqa: E402

OUT = "risk/leverage_results.json"
PROFILES = ["H5", "H10", "H15", "H20"]
VARIANTS = ["U-KOSTEN", "U-BREAKEVEN", "U-ALLE", "U-KOSTEN-TFD1-7T", "U-KOSTEN-TFD1"]
RATE_CLASSES = ("STIR", "ANLEIHE_KURZ")
SEED = 7_2_2026
ES_FACTOR = 0.0   # wird in main() aus P-SIM-T-DF und P-RISK-ES-CONF berechnet


def gap_pct(ins, P, which: str) -> float:
    """Ungünstigste Tageslücke in Anteilen des Preises."""
    rc = ins["risk_class"]
    price = float(ins["planning"]["price"]["value"])
    sd_day = ins["planning"]["vol_annual_pct"]["base"] / 100 / math.sqrt(252)
    if which in ("K5", "K10"):
        return P.f("P-GAP-K-HYP-LOW" if which == "K5" else "P-GAP-K-HYP-HIGH") * sd_day
    key = {"FX": "FX_CHF" if ins["symbol"] in ("6S", "MSF") else "FX"}.get(rc, rc)
    g = P.f(f"P-GAP-{key.replace('_', '-')}")
    if rc == "STIR":
        hist = g / price
    elif rc == "RENDITE":
        hist = g / price
    elif rc.startswith("ANLEIHE"):
        hist = ins["planning"]["duration_years"]["value"] * g / 100
    else:
        hist = g / 100
    if which == "HIST":
        return hist
    return max(hist, P.f("P-GAP-K-HYP-HIGH") * sd_day)   # Größenregel (DEC-DS-10)


def es_factor_t(nu: float, conf: float) -> float:
    """Expected Shortfall einer Student-t-Verteilung mit Varianz 1 in Vielfachen der Standardabweichung (numerisch, Simpson)."""
    c = math.exp(math.lgamma((nu + 1) / 2) - math.lgamma(nu / 2)) / math.sqrt(nu * math.pi)

    def pdf(t):
        return c * (1 + t * t / nu) ** (-(nu + 1) / 2)

    def integral(f, a, b, n=20000):
        h = (b - a) / n
        return h / 3 * (f(a) + f(b) + math.fsum((4 if k % 2 else 2) * f(a + k * h) for k in range(1, n)))

    tail = 1 - conf
    lo, hi = 0.0, 50.0
    for _ in range(80):                                   # Quantil per Bisektion: P(T > q) = tail
        mid = (lo + hi) / 2
        if 0.5 - integral(pdf, 0.0, mid, 4000) > tail:
            lo = mid
        else:
            hi = mid
    q = (lo + hi) / 2
    es = integral(lambda t: t * pdf(t), q, 400.0) / tail
    return es * math.sqrt((nu - 2) / nu)


def portfolio(ids, INS, P, sigma_target, shares=None):
    n = len(ids)
    r = shares or [1.0 / n] * n
    rcls = {i: INS[i]["risk_class"] for i in ids}
    M = corr_matrix(ids, rcls, P)
    q = math.fsum(r[a] * r[b] * M[a][b] for a in range(n) for b in range(n))
    D = 1.0 / math.sqrt(q)
    sig = [INS[i]["planning"]["vol_annual_pct"]["base"] / 100 for i in ids]
    k = sigma_target * D
    w = [k * r[j] / sig[j] for j in range(n)]
    return {"w": w, "D": D, "sigma_h": 1.0 / math.fsum(r[j] / sig[j] for j in range(n)), "L_g": math.fsum(w)}


def evaluate(ids, INS, P, prof, cm, shares=None, force_scale=None, basis="S-TF"):
    sig_t = P.f(f"P-LEV-{prof}-SIGMA")
    cap = P.f(f"P-LEV-{prof}-CAP")
    budget = P.f("P-OP-DAILY-LOSS-CAP") - P.f("P-RISK-GAP-RESERVE")
    wf = P.f("P-RISK-WEEKEND-FACTOR")   # Größenregel über Wochenenden und Feiertage (DEC-DS-10); Planung dauerhaft, da nur S-IM nicht übers Wochenende hält
    pf = portfolio(ids, INS, P, sig_t, shares)
    w = pf["w"]
    gaps = {m: [gap_pct(INS[i], P, m) for i in ids] for m in ("HIST", "K5", "K10", "DESIGN")}
    gl = {m: math.fsum(w[j] * gaps[m][j] for j in range(len(ids))) for m in gaps}
    me = math.fsum(w[j] * INS[i]["planning"]["initial_margin_pct"]["value"] / 100 for j, i in enumerate(ids))
    # Skalierung: Lückenbudget und Profilgrenze
    s_gap = min(1.0, budget / (wf * gl["DESIGN"])) if gl["DESIGN"] > 0 else 1.0
    s_cap = min(1.0, cap / pf["L_g"]) if pf["L_g"] > 0 else 1.0
    s = min(s_gap, s_cap) if force_scale is None else force_scale
    if force_scale is None and not gap_rule_ok(gl["DESIGN"] * s, 0.0, P, weekend=True):
        raise AssertionError("Skalierung verletzt die Größenregel PTC-13")
    me_cap = P.f(f"P-LEV-{prof}-ME")
    # Die Margin deckt nur das Guthaben beim Broker (Anteil P-ECO-CASH-AT-BROKER des NAV): M/E (Anteil NAV) ≤ Anteil / De-Risking-Schwelle
    derisk_me = P.f("P-ECO-CASH-AT-BROKER") / P.f("P-MRG-DERISK-TRIGGER")
    stress_me = {"basis": me * s, "plus50": me * s * (1 + P.f("P-MRG-STRESS-1")), "plus100": me * s * (1 + P.f("P-MRG-STRESS-2"))}
    eff_n = 1.0 / math.fsum(x * x for x in (shares or [1.0 / len(ids)] * len(ids)))
    es_1d = ES_FACTOR * sig_t * s / math.sqrt(252)
    reasons = []
    notes = []
    if prof == "H5":
        if sig_t * s < P.f("P-LEV-H5-SIGMA-MIN"):
            reasons.append(f"Verlustbudget: nach der Lückenregel nur σ_p {sig_t * s:.1%} < Mindest-σ {P.f('P-LEV-H5-SIGMA-MIN'):.0%}")
        elif s_gap < 1.0:
            notes.append(f"H5 läuft mit σ_p {sig_t * s:.1%} statt {sig_t:.0%}; die Lückenregel skaliert automatisch")
    elif s_gap < P.f("P-LEV-SIGMA-TOLERANCE"):
        reasons.append(f"Verlustbudget: Ziel-σ_p {sig_t:.0%} nur zu {s_gap:.0%} erreichbar (Lückenstress × Wochenendfaktor {wf * gl['DESIGN']:.1%} > {budget:.0%}); "
                       "vom Grundprofil nicht unterscheidbar")
    elif s_gap < 1.0:
        notes.append(f"σ-Ziel zu {s_gap:.0%} erreichbar; die Lückenregel skaliert automatisch")
    if eff_n < P.f(f"P-LEV-{prof}-MINDIV") - 1e-9:
        reasons.append(f"Mindestdiversifikation: {eff_n:.1f} < {P(f'P-LEV-{prof}-MINDIV')} effektive Instrumente")
    if es_1d > P.f(f"P-LEV-{prof}-ES"):
        reasons.append(f"ES-Limit: ES {P.f('P-RISK-ES-CONF'):.1%} 1 Tag {es_1d:.2%} > {P.f(f'P-LEV-{prof}-ES'):.0%}")
    if stress_me["basis"] > me_cap:
        reasons.append(f"Margin: M/E {stress_me['basis']:.1%} > Profilgrenze {me_cap:.0%}")
    if stress_me["plus100"] > derisk_me:
        reasons.append(f"Margin-Pfad +100 %: M/E {stress_me['plus100']:.1%} über der Grenze aus Guthaben beim Broker und De-Risking-Schwelle "
                       f"{derisk_me:.1%}")
    cls = {}
    for j, i in enumerate(ids):
        c = INS[i]["risk_class"]
        cls[c] = cls.get(c, 0.0) + w[j] * s
    cost = [cm[i]["strategies"][basis]["sr_cost_per_year"]["base"] for i in ids]
    rsh = shares or [1.0 / len(ids)] * len(ids)
    return {"n": len(ids), "effective_n": eff_n, "D": pf["D"], "sigma_h": pf["sigma_h"], "sigma_target": sig_t, "L_g_at_target": pf["L_g"],
            "scale_gap": s_gap, "scale_cap": s_cap, "scale": s, "sigma_achieved": sig_t * s, "L_g_achieved": pf["L_g"] * s,
            "gap_loss_at_target": gl, "gap_loss_achieved": {m: v * s for m, v in gl.items()}, "margin_to_equity": stress_me, "es_1d_parametric": es_1d,
            "class_gross_leverage": dict(sorted(cls.items())), "basis": basis, "mean_cost_sr": math.fsum(r * c for r, c in zip(rsh, cost, strict=True)),
            "admissible": not reasons, "reasons": reasons, "notes": notes}


def band_report(ids, INS, P, prof, w_scaled, tau, rng, snaps=4000):
    cap = P.f(f"P-LEV-{prof}-CAP")
    low = P.f("P-LEV-BAND-LOW")
    fsc = P.f("P-STR-FC-SCALE")
    fc_cap = P.f("P-STR-FC-CAP") / fsc
    sd_fc = fsc * math.sqrt(math.pi / 2)                  # E|N(0, sd_fc)| = mittlerer Prognosebetrag P-STR-FC-SCALE
    under = inb = at_cap = zero = 0
    for _ in range(snaps):
        lg = 0.0
        for j in range(len(ids)):
            if rng.u() < tau:
                size = min(abs(rng.normal(0.0, sd_fc)) / fsc, fc_cap)
                lg += w_scaled[j] * size
        if lg == 0.0:
            zero += 1
        if lg > cap:
            at_cap += 1
        elif lg >= low:
            inb += 1
        else:
            under += 1
    return {"share_below_band": under / snaps, "share_in_band": inb / snaps, "share_at_cap": at_cap / snaps, "share_zero": zero / snaps}


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    global ES_FACTOR
    ES_FACTOR = es_factor_t(P.f("P-SIM-T-DF"), P.f("P-RISK-ES-CONF"))
    INS = {i["id"]: i for i in instruments()}
    prior = load("research/prior_results.json")
    cm = {r["id"]: r for r in load("financials/cost_model_results.json")["instruments"]}
    tau = load("research/turnover_results.json")["strategies"]["S-TF"]["time_in_market"]
    rng = Rng(SEED)
    stages = [str(x) for x in P("P-ECO-CAPITAL-STAGES")]
    budget = P.f("P-OP-DAILY-LOSS-CAP") - P.f("P-RISK-GAP-RESERVE")
    wf = P.f("P-RISK-WEEKEND-FACTOR")
    cells = {}
    for v in VARIANTS:
        cells[v] = {}
        for st in stages:
            ids = prior["admission"][v][st]["instruments"]
            basis = prior["admission"][v][st]["basis"]
            cells[v][st] = {}
            for prof in PROFILES:
                if not ids:
                    cells[v][st][prof] = {"n": 0, "admissible": False, "reasons": ["Leeres Universum: kein Instrument erfüllt die Zulassung"]}
                    continue
                ev = evaluate(ids, INS, P, prof, cm, basis=basis)
                pf = portfolio(ids, INS, P, P.f(f"P-LEV-{prof}-SIGMA"))
                ev["band"] = band_report(ids, INS, P, prof, [x * ev["scale"] for x in pf["w"]], tau, rng)
                cells[v][st][prof] = ev
    # ---------------------------------------------------------------------------------------- Hebelkalibrierung über Zinsinstrumente
    def calibrate(rate_universe):
        """Kleinster Zins-Risikoanteil, mit dem das Profil seine Hebelobergrenze bei seinem σ-Ziel erreicht (WUNSCHHEBEL, §7.3 kein Zwangshebel:
        nur als Gegenrechnung)."""
        out = {}
        for st in stages:
            base_ids = prior["admission"]["U-KOSTEN"][st]["instruments"] or prior["admission"]["U-BREAKEVEN"][st]["instruments"]
            rate_ids = [i for i in prior["admission"][rate_universe][st]["instruments"] if INS[i]["risk_class"] in RATE_CLASSES]
            out[st] = {}
            for prof in PROFILES:
                if not base_ids or not rate_ids:
                    out[st][prof] = {"feasible": False, "reason": "kein Basis- oder Zinsuniversum"}
                    continue
                ids = base_ids + rate_ids
                cap = P.f(f"P-LEV-{prof}-CAP")
                best = None
                for step in range(0, 100):
                    s_rate = step / 100
                    shares = [(1 - s_rate) / len(base_ids)] * len(base_ids) + [s_rate / len(rate_ids)] * len(rate_ids)
                    pf = portfolio(ids, INS, P, P.f(f"P-LEV-{prof}-SIGMA"), shares)
                    if pf["L_g"] >= cap:
                        best = (s_rate, shares)
                        break
                if best is None:
                    out[st][prof] = {"feasible": False, "reason": "Profilgrenze auch mit 99 % Zins-Risikoanteil nicht erreichbar"}
                    continue
                ev = evaluate(ids, INS, P, prof, cm, best[1], force_scale=1.0)
                no_hist = sorted(set(prior["admission"]["U-HANDELBAR"][st]["without_history"]) & set(ids))
                out[st][prof] = {"feasible": True, "rate_risk_share": best[0], "instruments": ids, "L_g": ev["L_g_achieved"],
                                 "gap_loss_design": ev["gap_loss_achieved"]["DESIGN"], "gap_budget": budget,
                                 "within_loss_budget": wf * ev["gap_loss_achieved"]["DESIGN"] <= budget, "margin_to_equity": ev["margin_to_equity"],
                                 "mean_cost_sr": ev["mean_cost_sr"], "D": ev["D"], "instruments_without_research_history": no_hist,
                                 "cost_increase_vs_base": ev["mean_cost_sr"] - prior["admission"]["U-KOSTEN" if prior["admission"]["U-KOSTEN"][st]["instruments"]
                                                                                             else "U-BREAKEVEN"][st]["mean_cost_sr"]["S-TF"]}
        return out

    calib = calibrate("U-HANDELBAR")
    calib_research = calibrate("U-ALLE")
    # ---------------------------------------------------------------------------------------- Klassendeckel und Beispielrechnung
    class_caps = {}
    per_ins_caps = {}
    for i in INS.values():
        per_ins_caps[i["symbol"]] = budget / (wf * gap_pct(i, P, "DESIGN"))
    for rc in sorted({i["risk_class"] for i in INS.values()}):
        mem = sorted((gap_pct(i, P, "DESIGN"), i["symbol"]) for i in INS.values() if i["risk_class"] == rc)
        med = mem[len(mem) // 2][0]
        class_caps[rc] = {"standalone_cap_strictest": budget / (wf * mem[-1][0]), "binding_instrument": mem[-1][1], "design_gap_max": mem[-1][0],
                          "standalone_cap_typical": budget / (wf * med), "design_gap_median": med}
    # Rechenbeispiel aus §7.2 des Auftrags (keine Parameter, nur Nachrechnung der Formel L_g = D·σ_p/σ_h)
    ex = {"D": 2.0, "sigma_h": 0.15, "Lg_low": 5.0, "Lg_high": 20.0, "stir_share": 0.4, "stir_sigma": 0.007, "sigma_p": 0.10, "gap": 0.05}
    example = {"inputs": ex, "source": "Masterprompt v3.0 §7.2, Rechenbeispiel",
               "D2_no_stir_sigma_h_15": {"sigma_p_for_Lg5": ex["Lg_low"] * ex["sigma_h"] / ex["D"], "sigma_p_for_Lg20": ex["Lg_high"] * ex["sigma_h"] / ex["D"]},
               "D2_40pct_stir_rest_15_sigma_p_10": {"L_g": ex["D"] * ex["sigma_p"] * (ex["stir_share"] / ex["stir_sigma"] + (1 - ex["stir_share"]) / ex["sigma_h"])},
               "gap_5pct_at_20x": ex["Lg_high"] * ex["gap"]}
    contract_lev = {i["symbol"]: 100.0 / i["planning"]["initial_margin_pct"]["value"] for i in INS.values()}
    out = {"calculator": "risk/leverage_calculator.py", "model": "MOD-LEV", "seed": SEED,
           "inputs": input_hashes(["parameters.json", "registers/instruments.json", "research/prior_results.json", "financials/cost_model_results.json",
                                   "research/turnover_results.json"]),
           "definitions": {"L_g": "Σ|q·M·P·FX|/NAV", "formula": "L_g = D·σ_p/σ_h",
                           "gap_rule": "P-RISK-WEEKEND-FACTOR · Σ|w_i|·max(Klassenlücke_i, k·σ_Tag,i) + Tagesverlust ≤ P-OP-DAILY-LOSS-CAP − P-RISK-GAP-RESERVE; "
                                       "k = P-GAP-K-HYP-HIGH; Wochenendfaktor in der Planung dauerhaft (Positionen halten über Wochenenden)",
                           "correlation_in_gap": "ungünstigste Richtung aller Positionen (P-LEV-CLUSTER-MODE)"},
           "gap_budget": budget, "weekend_factor": wf, "cells": cells, "leverage_calibration_via_rates": calib,
           "leverage_calibration_via_rates_note": "hypothetisch: handelbare Zinskontrakte ohne Kosten- und Historienfilter (U-HANDELBAR); nicht forschungsfähig",
           "leverage_calibration_research_admissible": calib_research,
           "class_caps": class_caps, "instrument_caps": dict(sorted(per_ins_caps.items())),
           "masterprompt_example_check": example, "contract_leverage_informative": contract_lev, "time_in_market_S-TF": tau}
    ok = write_or_check(OUT, dumps(out), a.check)
    if not a.check:
        for v in VARIANTS:
            for st in stages:
                row = [f"{v:<11}{st:>10}"]
                for prof in PROFILES:
                    c = cells[v][st][prof]
                    row.append(f"{prof}:{'OK ' if c['admissible'] else 'NEIN'} Lg={c.get('L_g_achieved', 0):4.1f} σ={c.get('sigma_achieved', 0):.3f}")
                print(" | ".join(row))
        for st in stages:
            print(st, {p: (round(c['rate_risk_share'], 2), round(c['gap_loss_design'], 3), round(c["mean_cost_sr"], 3)) if c.get('feasible') else c.get('reason')
                       for p, c in calib[st].items()})
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
