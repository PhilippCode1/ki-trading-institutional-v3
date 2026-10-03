#!/usr/bin/env python3
"""Stresstest-Engine (§7.9; Modell MOD-STRESS).

Wendet 13 historische und 8 hypothetische Szenarien (risk/stress_scenarios.json) auf je zwei Allokationen und alle Profile H5–H20 an:
  SYSTEM       – Allokation, wie der Risikomotor sie fahren würde (Sensitivitätsuniversum U-BREAKEVEN, Referenzstufe, nach Lückenregel skaliert)
  ALTERNATIVE_TFD1 – langsame Trendfolge ohne 7-Tage-Grenze (Universum U-KOSTEN-TFD1; nur mit Betreiberentscheidung zulässig)
  WUNSCHHEBEL  – Zins-kalibrierte Allokation mit L_g = Profilgrenze ohne Lückenregel (zeigt, warum H10–H20 unzulässig sind)
Ergebnisse je Szenario: Verlust in % NAV am ersten Tag, über den Szenariohorizont ohne und mit De-Risking-Leiter, Leiterwirkung,
Spitze von M/E (Margin-Erhöhung des Szenarios oder Standardpfad), Margin-Level am Broker nach Verlust und Liquidationsstatus.
Margin-Level = Guthaben beim Broker / Initial Margin; beim Broker liegt der Anteil P-ECO-CASH-AT-BROKER des NAV, Verluste werden dort
abgerechnet. Je Allokation: nötiger Anteil beim Broker, damit das Level in keinem Szenario unter die eigene De-Risking-Schwelle fällt.
Mehrtägige Handelsaussetzungen (Feld halt): Positionen der ausgesetzten Klassen kann die Leiter nicht abbauen.
Brokerausfall (SC-X-BROKER): zusätzlich ist das Guthaben beim Broker nicht verfügbar (eigenes Feld, nicht im Marktverlust).
Ungünstigste Richtung je Position (Beträge ohne Vorzeichen). Fehlende Szenariowerte: Ersatzwert = halbe Konstruktionslücke (markiert).
Aufruf: python risk/stress_test_engine.py [--check]
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.calc import Params, broker_share_required, dumps, input_hashes, instruments, ladder_factor, load, main_args, write_or_check  # noqa: E402
from risk.leverage_calculator import gap_pct, portfolio  # noqa: E402

OUT = "risk/stress_results.json"
PROFILES = ["H5", "H10", "H15", "H20"]


def cls_key(ins) -> str:
    if ins["symbol"] in ("6S", "MSF"):
        return "FX_CHF"
    return ins["risk_class"]


def move_pct(ins, cls_moves, P, which: str, extra) -> tuple[float, bool]:
    """Bewegung in Anteilen des Preises (d1 oder multi); zweiter Wert: Ersatzwert verwendet."""
    rc = ins["risk_class"]
    m = cls_moves.get(cls_key(ins)) or cls_moves.get(rc)
    price = float(ins["planning"]["price"]["value"])
    subst = P.f("P-RISK-STRESS-SUBST-SHARE") * gap_pct(ins, P, "HIST")

    def conv(v):
        if rc == "STIR" or rc == "RENDITE":
            return v / price
        if rc.startswith("ANLEIHE"):
            return ins["planning"]["duration_years"]["value"] * v / 100
        return v / 100

    d1 = conv(m["d1"]) if m and m["d1"] is not None else None
    mu = conv(m["multi"]) if m and m["multi"] is not None else None
    if which == "multi" and rc == "ANLEIHE_LANG" and extra.get("ANLEIHE_LANG_price_pct_multi"):
        mu = max(mu or 0.0, extra["ANLEIHE_LANG_price_pct_multi"] / 100)
    used_subst = False
    if d1 is None:
        d1 = subst if mu is None else min(subst, mu)
        used_subst = True
    if mu is None:
        mu = d1 * math.sqrt(P.f("P-RISK-STRESS-MULTI-DAYS"))
        used_subst = True
    mu = max(mu, d1)
    return (d1 if which == "d1" else mu), used_subst


def ladder_path(day_losses, P, fixed=None):
    """Verlust über mehrere Tage mit Tagesleiter und Drawdown-Leiter im Tagesraster: Stufen L1/L2 und DD-L1 bis DD-L3 wirken am Folgetag
    (ladder_factor); L3 und die Kill-Stufe bauen sofort ab. Tagesbewegungen gelten als Lücken und werden nicht gekappt (konservativ).
    fixed: Tagesverluste nicht abbaubarer Positionen (Handelsaussetzung); sie zählen für die Leiterstufen mit, laufen aber voll weiter."""
    l3, kill = P.f("P-RISK-DL-L3"), P.f("P-RISK-DD-KILL")
    fixed = list(fixed) if fixed is not None else [0.0] * len(day_losses)
    expo, total, flat = 1.0, 0.0, False
    for full, fx in zip(day_losses, fixed, strict=True):
        loss = full * expo + fx
        total += loss
        if flat:
            continue
        if loss >= l3 or total >= kill:
            flat, expo = True, 0.0
            continue
        expo = ladder_factor(loss, total, P)
    return total, flat


def evaluate(alloc, INS, P, cm, sc, hyp: bool):
    ids, w, me_base = alloc["ids"], alloc["w"], alloc["me"]
    subst_classes = set()
    extra_out = {}
    if not hyp:
        moves = sc["moves"]
        if sc.get("expiring_contract_only"):
            # Die Bewegung betraf nur den auslaufenden Kontrakt; die Verfallsregel (P-UNI-ENERGY-EXPIRY-DAYS) schließt ihn aus.
            raw = math.fsum(wi * move_pct(INS[i], moves, P, "d1", sc["extra"])[0] for i, wi in zip(ids, w, strict=True))
            extra_out["loss_without_expiry_rule"] = raw
            moves = {k: (v if k != "ENERGIE" else {"d1": None, "d1_status": "ERSATZWERT", "multi": None, "multi_status": "ERSATZWERT",
                                                    "basis": "Folgekontrakt: Ersatzwert"}) for k, v in moves.items()}
        halted = set(sc.get("halt", {}).get("classes", []))
        d1 = mu = d1_h = mu_h = 0.0
        for i, wi in zip(ids, w, strict=True):
            a, s1 = move_pct(INS[i], moves, P, "d1", sc["extra"])
            b, s2 = move_pct(INS[i], moves, P, "multi", sc["extra"])
            d1 += wi * a
            mu += wi * b
            if cls_key(INS[i]) in halted or INS[i]["risk_class"] in halted:
                d1_h += wi * a
                mu_h += wi * b
            if s1 or s2:
                subst_classes.add(cls_key(INS[i]))
        days = 5
        free_d1, free_mu = d1 - d1_h, mu - mu_h
        with_ladder, flattened = ladder_path([free_d1] + [(free_mu - free_d1) / (days - 1)] * (days - 1), P,
                                             fixed=[d1_h] + [(mu_h - d1_h) / (days - 1)] * (days - 1))
        if halted:
            extra_out["halted_share_of_loss"] = mu_h / mu if mu > 0 else 0.0
        no_ladder = mu
        m_inc = sc["margin_increase"] if sc["margin_increase"] is not None else P.f("P-MRG-STRESS-1")
    else:
        sd = {i: INS[i]["planning"]["vol_annual_pct"]["base"] / 100 / math.sqrt(252) for i in ids}
        k = sc.get("k_sigma", 0.0)
        if sc["id"] == "SC-X-RATESHOCK":
            def rate_move(i, pp):
                ins = INS[i]
                rc = ins["risk_class"]
                if rc in ("STIR", "RENDITE"):
                    return pp / float(ins["planning"]["price"]["value"])
                if rc.startswith("ANLEIHE"):
                    return ins["planning"]["duration_years"]["value"] * pp / 100
                return 0.0
            d1 = math.fsum(wi * rate_move(i, sc["d1_pp"]) for i, wi in zip(ids, w, strict=True))
            mu = math.fsum(wi * rate_move(i, sc["multi_pp"]) for i, wi in zip(ids, w, strict=True))
            with_ladder, flattened = ladder_path([d1] + [(mu - d1) / 4] * 4, P)
        elif sc["id"] == "SC-X-EXCH":
            ex = {}
            for i, wi in zip(ids, w, strict=True):
                ex[INS[i]["exchange"]] = ex.get(INS[i]["exchange"], 0.0) + wi
            big = max(sorted(ex), key=lambda e: ex[e])
            d1 = mu = math.fsum(wi * k * sd[i] for i, wi in zip(ids, w, strict=True) if INS[i]["exchange"] == big)
            with_ladder, flattened = d1, False
        elif sc["id"] == "SC-X-LIQ":
            d1 = mu = math.fsum(wi * (k * sd[i] + sc["spread_multiple"] * float(cm[i]["half_spread_side_eur"]) / float(cm[i]["notional_eur"]))
                                for i, wi in zip(ids, w, strict=True))
            with_ladder, flattened = d1, False
        elif sc["id"] == "SC-X-BROKER":
            d1 = math.fsum(wi * k * sd[i] for i, wi in zip(ids, w, strict=True))
            mu = d1 * math.sqrt(sc["days"])
            with_ladder, flattened = mu, False           # kein Zugang: Leiter wirkungslos
            extra_out["broker_cash_unavailable"] = P.f("P-ECO-CASH-AT-BROKER")
            extra_out["loss_incl_unavailable_cash"] = mu + P.f("P-ECO-CASH-AT-BROKER")
        else:
            d1 = mu = math.fsum(wi * k * sd[i] for i, wi in zip(ids, w, strict=True))
            with_ladder, flattened = d1, False
        no_ladder = mu
        m_inc = P.f("P-MRG-STRESS-2") if sc["id"] in ("SC-X-CORR1", "SC-X-GAP10") else P.f("P-MRG-STRESS-1")
    me_peak = me_base * (1 + m_inc)
    phi = P.f("P-ECO-CASH-AT-BROKER")
    eq = max(0.0, phi - with_ladder)                  # Guthaben beim Broker nach dem Verlust (Anteile des NAV)
    level = eq / me_peak if me_peak > 0 else float("inf")
    status = "LIQUIDATION" if level < P.f("P-MRG-BROKER-STOPOUT") else ("DERISK" if level < P.f("P-MRG-DERISK-TRIGGER") else "OK")
    return {"loss_day1": d1, "loss_no_ladder": no_ladder, "loss_with_ladder": with_ladder, "ladder_effect": no_ladder - with_ladder,
            "flattened_by_ladder": flattened, "daily_cap_breach": d1 > P.f("P-OP-DAILY-LOSS-CAP"), "margin_increase": m_inc,
            "me_peak": me_peak, "margin_level_after": level if math.isfinite(level) else None, "liquidation_status": status,
            "broker_share_required": broker_share_required(me_base, m_inc, P.f("P-MRG-DERISK-TRIGGER"), with_ladder),
            "substitute_classes": sorted(subst_classes), **extra_out}


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    INS = {i["id"]: i for i in instruments()}
    lev = load("risk/leverage_results.json")
    prior = load("research/prior_results.json")
    cm = {r["id"]: r for r in load("financials/cost_model_results.json")["instruments"]}
    S = load("risk/stress_scenarios.json")
    st = str(P("P-RISK-STRESS-REF-STAGE"))
    allocs = {}
    for prof in PROFILES:
        ids = prior["admission"]["U-BREAKEVEN"][st]["instruments"]
        cell = lev["cells"]["U-BREAKEVEN"][st][prof]
        pf = portfolio(ids, INS, P, P.f(f"P-LEV-{prof}-SIGMA"))
        w = [x * cell["scale"] for x in pf["w"]]
        me = math.fsum(wi * INS[i]["planning"]["initial_margin_pct"]["value"] / 100 for i, wi in zip(ids, w, strict=True))
        allocs[("SYSTEM", prof)] = {"ids": ids, "w": w, "me": me, "L_g": math.fsum(w)}
        ids_a = prior["admission"]["U-KOSTEN-TFD1"][st]["instruments"]
        if ids_a:
            cell_a = lev["cells"]["U-KOSTEN-TFD1"][st][prof]
            pfa = portfolio(ids_a, INS, P, P.f(f"P-LEV-{prof}-SIGMA"))
            wa = [x * cell_a["scale"] for x in pfa["w"]]
            mea = math.fsum(wi * INS[i]["planning"]["initial_margin_pct"]["value"] / 100 for i, wi in zip(ids_a, wa, strict=True))
            allocs[("ALTERNATIVE_TFD1", prof)] = {"ids": ids_a, "w": wa, "me": mea, "L_g": math.fsum(wa)}
        cal = lev["leverage_calibration_via_rates"][st][prof]
        if cal.get("feasible"):
            ids2 = cal["instruments"]
            n_rate = sum(1 for i in ids2 if INS[i]["risk_class"] in ("STIR", "ANLEIHE_KURZ"))
            n_base = len(ids2) - n_rate
            sh = [(1 - cal["rate_risk_share"]) / n_base if INS[i]["risk_class"] not in ("STIR", "ANLEIHE_KURZ") else cal["rate_risk_share"] / n_rate for i in ids2]
            pf2 = portfolio(ids2, INS, P, P.f(f"P-LEV-{prof}-SIGMA"), sh)
            me2 = math.fsum(wi * INS[i]["planning"]["initial_margin_pct"]["value"] / 100 for i, wi in zip(ids2, pf2["w"], strict=True))
            allocs[("WUNSCHHEBEL", prof)] = {"ids": ids2, "w": pf2["w"], "me": me2, "L_g": pf2["L_g"]}
    results = {}
    for (kind, prof), al in sorted(allocs.items()):
        rows = {}
        for sc in S["historical"]:
            rows[sc["id"]] = evaluate(al, INS, P, cm, sc, hyp=False)
        for sc in S["hypothetical"]:
            rows[sc["id"]] = evaluate(al, INS, P, cm, sc, hyp=True)
        worst = max(rows.values(), key=lambda r: r["loss_with_ladder"])
        results.setdefault(kind, {})[prof] = {
            "L_g": al["L_g"], "margin_to_equity": al["me"], "n_instruments": len(al["ids"]), "scenarios": rows,
            "worst_loss_with_ladder": worst["loss_with_ladder"], "worst_scenario": max(rows, key=lambda k: rows[k]["loss_with_ladder"]),
            "daily_cap_breaches": sorted(k for k, r in rows.items() if r["daily_cap_breach"]),
            "liquidations": sorted(k for k, r in rows.items() if r["liquidation_status"] == "LIQUIDATION"),
            "derisk_needed": sorted(k for k, r in rows.items() if r["liquidation_status"] == "DERISK"),
            "broker_share": P.f("P-ECO-CASH-AT-BROKER"),
            "broker_share_required": max(r["broker_share_required"] for r in rows.values()),
            "broker_share_sufficient": max(r["broker_share_required"] for r in rows.values()) <= P.f("P-ECO-CASH-AT-BROKER")}
    expected = len(S["historical"]) + len(S["hypothetical"])
    complete = all(len(v["scenarios"]) == expected for kind in results.values() for v in kind.values())
    out = {"calculator": "risk/stress_test_engine.py", "model": "MOD-STRESS",
           "inputs": input_hashes(["parameters.json", "registers/instruments.json", "risk/stress_scenarios.json", "risk/leverage_results.json",
                                   "research/prior_results.json", "financials/cost_model_results.json"]),
           "reference_stage": st, "scenario_count": expected, "complete": complete, "results": results}
    ok = write_or_check(OUT, dumps(out), a.check)
    if not a.check:
        for kind, per in results.items():
            for prof, r in per.items():
                print(f"{kind:<12}{prof:<4} L_g={r['L_g']:5.1f} M/E={r['margin_to_equity']:.3f} schlimmster={r['worst_scenario']} "
                      f"{r['worst_loss_with_ladder']:.1%} Tagesgrenze verletzt in {len(r['daily_cap_breaches'])} Liquidation in {len(r['liquidations'])} "
                      f"De-Risking in {len(r['derisk_needed'])} Brokeranteil nötig {r['broker_share_required']:.1%}")
    print("OK" if ok and complete else "FEHLER", OUT)
    return 0 if ok and complete else 1


if __name__ == "__main__":
    sys.exit(main())
