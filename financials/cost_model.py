#!/usr/bin/env python3
"""Kostenmodell je Instrument – eine Quelle der Wahrheit für Handelskosten (§5.1, EV-01, Modell MOD-COST).

Rechnet je Kontrakt (Basisszenario und Sensitivitäten):
  * Kosten je Seite = Kommission (Broker, All-in) + halber Spread + Schlupf (Ticks) [+ Marktwirkung Y·σ_Tag·√(q/ADV) je Ordergröße q]
  * Round-Turn-Kosten in EUR und in Basispunkten des Nominals
  * Kosten je Risikoeinheit c_RT = Round-Turn-Kosten / Jahresvolatilität je Kontrakt (Sharpe-Einheiten je Round-Turn)
  * Kosten je Strategie und Jahr in Sharpe-Einheiten: C = (N_RT + N_Roll) · c_RT / √τ  (N_RT, τ aus research/turnover_results.json)
  * feste Kosten: Marktdaten je Szenario, historische Daten, Infrastruktur, KI-Abo, externe Prüfungen
  * CFD-Vergleich (Rückfalloption BQ-08a): Spread × Faktor plus Übernachtfinanzierung

Geldbeträge mit Decimal (R-03). Alle anderen Dateien lesen die Ergebnisse aus financials/cost_model_results.json (R-04).
Aufruf: python financials/cost_model.py [--check]
"""
from __future__ import annotations

import math
import sys
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.calc import Params, costs, csv_text, dec, dumps, input_hashes, instruments, load, main_args, money, write_or_check  # noqa: E402

OUT = "financials/cost_model_results.json"
OUT_CSV = "financials/cost_table.csv"
STRATS = ["S-TF", "S-IM", "S-REV", "S-BASE-TFD1", "S-BASE-TFD1-7T"]
Q_LEVELS = [1, 10, 100, 1000]


def fx_to_eur(ccy: str, P) -> Decimal:
    """Einheiten der Kontraktwährung je EUR."""
    return {"EUR": Decimal(1), "USD": dec(P("P-ECO-EURUSD")), "GBP": dec(P("P-ECO-EURGBP"))}[ccy]


def per_contract(ins, C, P, comm_eur: Decimal, slip_ticks: Decimal, spread_mult: Decimal = Decimal(1)):
    fx = fx_to_eur(ins["currency"], P)
    price = dec(ins["planning"]["price"]["value"])
    mult = dec(ins["multiplier"])
    tv = dec(ins["tick_value"])
    spread = dec(ins["planning"]["spread_ticks"]["value"]) * spread_mult
    notional = mult * price / fx
    half_spread = spread / 2 * tv / fx
    slip = slip_ticks * tv / fx
    side = comm_eur + half_spread + slip
    rt = 2 * side
    v = ins["planning"]["vol_annual_pct"]
    vol = {k: notional * dec(v[k]) / 100 for k in ("base", "low", "high")}
    return {"fx": fx, "notional_eur": notional, "half_spread_eur": half_spread, "slippage_eur": slip, "commission_eur": comm_eur,
            "side_eur": side, "rt_eur": rt, "rt_bp": rt / notional * 10000, "vol_eur": vol,
            "c_rt": {k: float(rt / vol[k]) for k in vol}}


def impact_fraction(ins, q: float, Y: float, free_share: float) -> float:
    """Marktwirkung je Seite als Anteil des Nominals: Y · σ_Tag · √(max(0, q − q_frei)/ADV), q_frei = Anteil × ADV (sichtbare Tiefe)."""
    sd_day = ins["planning"]["vol_annual_pct"]["base"] / 100 / math.sqrt(252)
    adv = ins["planning"]["adv_contracts"]["value"]
    return Y * sd_day * math.sqrt(max(0.0, q - free_share * adv) / adv)


def impact_side_eur(ins, notional: Decimal, q: int, Y: float, free_share: float) -> Decimal:
    return notional * dec(impact_fraction(ins, q, Y, free_share))


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    C = costs()
    T = load("research/turnover_results.json")["strategies"]
    rolls = P("P-UNI-ROLLS-PER-YEAR")
    comm_base = dec(C["COST-COMM-FXFLAT"]["amount"])
    comm_low = dec(C["COST-COMM-FXFLAT-LOW"]["amount"])
    slip = dec(C["COST-EXEC-SLIP-TICKS"]["amount"])
    Y = float(C["COST-EXEC-IMPACT-Y"]["amount"])
    free = float(C["COST-EXEC-IMPACT-FREE-SHARE"]["amount"])
    rows, table = [], []
    for ins in instruments():
        base = per_contract(ins, C, P, comm_base, slip)
        low = per_contract(ins, C, P, comm_low, Decimal(0))
        n_roll = rolls[ins["risk_class"]]
        strat = {}
        for s in STRATS:
            t = T[s]
            n = t["round_turns_per_year"] + n_roll * t["time_in_market"]
            sq = math.sqrt(max(t["time_in_market"], 1e-9))
            strat[s] = {"rt_per_year": n, "sr_cost_per_year": {k: n * base["c_rt"][k] / sq for k in ("base", "low", "high")},
                        "sr_cost_per_year_low_fees": n * low["c_rt"]["base"] / sq}
        imp = {str(q): money(impact_side_eur(ins, base["notional_eur"], q, Y, free)) for q in Q_LEVELS}
        rec = {"id": ins["id"], "symbol": ins["symbol"], "risk_class": ins["risk_class"], "asset_class": ins["asset_class"],
               "size_class": ins["size_class"], "currency": ins["currency"], "access": ins["access"]["status"], "blocked": bool(ins["blocked"]),
               "notional_eur": money(base["notional_eur"]), "vol_eur_per_year": {k: money(v) for k, v in base["vol_eur"].items()},
               "commission_side_eur": money(base["commission_eur"]), "half_spread_side_eur": money(base["half_spread_eur"]),
               "slippage_side_eur": money(base["slippage_eur"]), "cost_side_eur": money(base["side_eur"]), "cost_rt_eur": money(base["rt_eur"]),
               "cost_rt_bp": float(base["rt_bp"]), "c_rt_sr": base["c_rt"], "c_rt_sr_low_fees": low["c_rt"]["base"],
               "impact_side_eur_by_order_size": imp, "rolls_per_year": n_roll, "strategies": strat}
        rows.append(rec)
        table.append([ins["id"], ins["symbol"], ins["risk_class"], ins["size_class"], str(rec["notional_eur"]), str(rec["vol_eur_per_year"]["base"]),
                      str(rec["cost_rt_eur"]), round(float(base["rt_bp"]), 3), round(base["c_rt"]["base"], 6),
                      round(strat["S-TF"]["sr_cost_per_year"]["base"], 4), round(strat["S-IM"]["sr_cost_per_year"]["base"], 4),
                      round(strat["S-BASE-TFD1"]["sr_cost_per_year"]["base"], 4)])
    # ------------------------------------------------------------------ feste Kosten (EUR)
    eurusd = dec(P("P-ECO-EURUSD"))

    def eur(cid):
        c = C[cid]
        v = dec(c["amount"])
        return v / eurusd if c["currency"] == "USD" else v

    n_cme = dec(C["COST-MD-CME-EXCHANGES"]["amount"])
    md = {
        "ANZEIGE": {"monthly_eur": money(eur("COST-MD-FXFLAT-EUREX") + eur("COST-MD-FXFLAT-CME")),
                    "per_exchange_monthly_eur": {"CME": money(eur("COST-MD-FXFLAT-CME")), "EUREX": money(eur("COST-MD-FXFLAT-EUREX"))},
                    "waiver_commission_eur_per_exchange": money(eur("COST-MD-FXFLAT-WAIVER")),
                    "note": "Broker-Kursgebühren; entfallen je Börse ab 300 € Kommission im Monat"},
        "NON_DISPLAY_MANAGED": {"monthly_eur": money(eur("COST-MD-FXFLAT-EUREX") + eur("COST-MD-FXFLAT-CME") + n_cme * eur("COST-MD-CME-ND-MANAGED")
                                                     + eur("COST-MD-EUREX-ND")),
                                "note": "zusätzlich CME Managed User Non-Display ×4 und Eurex Non-Display Entry"},
        "NON_DISPLAY_USER": {"monthly_eur": money(eur("COST-MD-FXFLAT-EUREX") + eur("COST-MD-FXFLAT-CME") + n_cme * eur("COST-MD-CME-ND-USER")
                                                  + eur("COST-MD-EUREX-ND-USER")),
                             "note": "zusätzlich CME User Non-Display ×4 und Eurex Non-Display Entry"},
    }
    hist_once = money(eur("COST-HIST-KIBOT") + dec(C["COST-HIST-EUREX-MARKETS"]["amount"]) * dec(C["COST-HIST-CQG-MONTHS"]["amount"]) * eur("COST-HIST-CQG-MIN")
                      + dec(C["COST-HIST-UPDATE-MONTHS"]["amount"]) * eur("COST-HIST-UPDATE"))
    infra_monthly = money(sum(eur(k) for k in ["COST-INF-VPS-MONEY", "COST-INF-VPS-RESEARCH", "COST-INF-EVALUATOR", "COST-INF-BACKUP", "COST-INF-ALERT"]))
    ai = {"PLUS": money(eur("COST-AI-PORTAL-PLUS")), "SUPER": money(eur("COST-AI-PORTAL-SUPER")), "ULTRA": money(eur("COST-AI-PORTAL-ULTRA"))}
    fixed = {"market_data_monthly_eur": md, "historical_data_once_eur": hist_once, "infrastructure_monthly_eur": infra_monthly,
             "hardware_keys_once_eur": money(eur("COST-INF-KEYS")), "ai_subscription_monthly_eur": ai,
             "ai_tier_base": P("P-AI-PORTAL-TIER"), "coding_agent_monthly_eur": money(eur("COST-AI-CODING-AGENT")),
             "external_once_eur": {"review": money(eur("COST-EXT-REVIEW")), "pentest": money(eur("COST-EXT-PENTEST")), "audit": money(eur("COST-EXT-AUDIT"))},
             "external_risk_function_monthly_eur": money(eur("COST-EXT-RISK-ROLE"))}
    # ------------------------------------------------------------------ CFD-Vergleich (nur zugängliche Klassen; Aktienindex gesperrt)
    cfd = []
    fin_mark = float(C["COST-CFD-FIN-MARKUP"]["amount"])
    spread_mult = dec(C["COST-CFD-SPREAD-MULT"]["amount"])
    hold_nights = T["S-TF"]["holding_hours_median"] / 24.0
    cash = P.f("P-ECO-CASH-RATE")
    for sym in ["6E", "GC", "CL", "FGBL", "BTC"]:
        ins = next(i for i in instruments() if i["symbol"] == sym)
        fut = per_contract(ins, C, P, comm_base, slip)
        cf = per_contract(ins, C, P, Decimal(0), slip, spread_mult)
        fin_long = float(cf["notional_eur"]) * (fin_mark + cash) * hold_nights / 360
        fin_short = float(cf["notional_eur"]) * max(0.0, fin_mark - cash) * hold_nights / 360
        cfd.append({"symbol": sym, "future_rt_bp": float(fut["rt_bp"]), "cfd_spread_rt_bp": float(cf["rt_bp"]),
                    "cfd_financing_rt_bp_long": fin_long / float(cf["notional_eur"]) * 1e4, "cfd_financing_rt_bp_short": fin_short / float(cf["notional_eur"]) * 1e4,
                    "median_nights": hold_nights})
    out = {"calculator": "financials/cost_model.py", "model": "MOD-COST",
           "inputs": input_hashes(["registers/instruments.json", "registers/costs.json", "parameters.json", "research/turnover_results.json"]),
           "scenario": "BASIS: FXFlat 1,00 € je Seite; halber Spread; 0,25 Tick Schlupf; Marktwirkung separat je Ordergröße",
           "formulas": {"c_rt": "Round-Turn-Kosten / (Nominal × σ p. a.)", "sr_cost_per_year": "(N_RT + Rollen/Jahr × τ) × c_RT / √τ",
                        "impact": "Y × σ_Tag × √(max(0, q − Anteil·ADV)/ADV) × Nominal je Seite"},
           "impact_model": {"Y": Y, "free_share": free, "source": ["COST-EXEC-IMPACT-Y", "COST-EXEC-IMPACT-FREE-SHARE"]},
           "instruments": rows, "fixed_costs": fixed, "cfd_comparison": cfd}
    ok = write_or_check(OUT, dumps(out), a.check)
    ok &= write_or_check(OUT_CSV, csv_text(["id", "symbol", "risikoklasse", "groesse", "nominal_eur", "vola_eur_pa", "rt_kosten_eur", "rt_bp", "c_rt_sr",
                                            "sr_kosten_pa_S-TF", "sr_kosten_pa_S-IM", "sr_kosten_pa_TFD1"], table), a.check)
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
