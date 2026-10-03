#!/usr/bin/env python3
"""Umschlagssimulation der vorregistrierten Strategiefamilie auf synthetischen Stundenpreisen (Modell MOD-TURN).

Zweck: Round-Turns je Jahr, Zeit im Markt, Haltedauern und Ausstiegsgründe je Strategie messen. Diese Größen speisen das Kostenmodell
(Kosten je Jahr = Round-Turns × Kosten je Round-Turn) und die Prior-Herleitung (Kosten in Sharpe-Einheiten).

Grenzen (R-02): Die Preise sind synthetisch (Zufallspfad mit Volatilitätsregimen, fetten Rändern und Wochenendlücken) und enthalten keine
Edge. Gemessen wird nur das Handelsverhalten der Regeln; Renditen dieser Simulation sind bedeutungslos und werden nicht ausgegeben.

Aufruf:  python research/reference_strategies/turnover_simulation.py [--check]
Ausgabe: research/turnover_results.json
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.calc import Params, Rng, dumps, input_hashes, main_args, write_or_check  # noqa: E402
from research.reference_strategies import s_base, s_im, s_rev, s_tf  # noqa: E402
from research.reference_strategies.common import BARS_PER_DAY, summarize  # noqa: E402

OUT = "research/turnover_results.json"
SEED = 20260924
N_INSTR = 6
YEARS = 8
WINDOW_START, WINDOW_LEN = 14, 7   # Kernzeit: 7 Stundenbalken (z. B. 14:00–21:00 MEZ)


def synthetic_bars(rng: Rng, sigma_annual: float, years: int):
    """Stundenbalken: 23 je Tag, 5 Tage je Woche; Regime normal/hoch (×2), t(5)-Innovationen, Wochenendlücke."""
    h_sd = sigma_annual / math.sqrt(252 * BARS_PER_DAY)
    bars, price, hours, high = [], 100.0, 0.0, False
    days = years * 252
    for day in range(days):
        if high and rng.u() < 0.05:
            high = False
        elif not high and rng.u() < 0.01:
            high = True
        reg = 2.0 if high else 1.0
        for k in range(BARS_PER_DAY):
            in_w = WINDOW_START <= k < WINDOW_START + WINDOW_LEN
            intraday = 1.35 if in_w else 0.85
            extra = math.sqrt(4.0) if (k == 0 and day % 5 == 0 and day > 0) else 1.0
            r = h_sd * reg * intraday * extra * rng.student_t_unit(5)
            price *= math.exp(r - 0.5 * (h_sd * reg * intraday * extra) ** 2)
            bars.append({"price": price, "hours": hours, "in_window": in_w, "day": day,
                         "window_pos": (k - WINDOW_START) if in_w else -1, "window_len": WINDOW_LEN})
            hours += 1.0
        hours += 1.0                       # tägliche Pause
        if day % 5 == 4:
            hours += 48.0                  # Wochenende
    return bars, hours


def pooled(summaries):
    keys = ["round_turns_per_year", "time_in_market", "holding_hours_mean", "holding_hours_median", "share_within_4h_4d", "share_over_4d",
            "share_timestop"]
    out = {k: math.fsum(s[k] for s in summaries) / len(summaries) for k in keys}
    out["round_turns_per_year_min"] = min(s["round_turns_per_year"] for s in summaries)
    out["round_turns_per_year_max"] = max(s["round_turns_per_year"] for s in summaries)
    out["max_holding_hours"] = max(s.get("max_holding_hours", 0.0) for s in summaries)
    reasons = {}
    for s in summaries:
        for k, v in s["exit_reasons"].items():
            reasons[k] = reasons.get(k, 0.0) + v / len(summaries)
    out["exit_reasons"] = dict(sorted(reasons.items()))
    out["trades_total"] = sum(s["trades"] for s in summaries)
    return out


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    prm = {k: P(k) for k in ["P-STR-TF-SPEEDS", "P-STR-FC-CAP", "P-STR-FDM-CAP", "P-STR-FC-SCALE", "P-STR-TF-ENTRY", "P-STR-TF-EXIT",
                             "P-STR-STOP-ATR", "P-OP-HOLD-MAX-H", "P-STR-REENTRY-COOLDOWN-H", "P-STR-IM-SIGNAL-MIN", "P-STR-IM-HOLD-H",
                             "P-STR-REV-Z", "P-STR-REV-HOLD-H", "P-STR-VOL-SPAN-D", "P-STR-IM-MIN-MOVE-SD", "P-STR-IM-STOP-FACTOR",
                             "P-STR-REV-LOOKBACK-D", "P-STR-REV-STOP-FACTOR", "P-STR-BASE-ENTRY-N", "P-STR-BASE-EXIT-N", "P-STR-BASE-ATR-N",
                             "P-STR-BASE-STOP-ATR"]}
    rng = Rng(SEED)
    res = {"S-TF": [], "S-IM": [], "S-REV": [], "S-BASE-TFD1": [], "S-BASE-TFD1-7T": []}
    tf_info = []
    for k in range(N_INSTR):
        sig = 0.15 + 0.04 * k
        bars, total_h = synthetic_bars(rng, sig, YEARS)
        book, info = s_tf.run(bars, prm)
        res["S-TF"].append(summarize(book.trades, total_h, YEARS))
        tf_info.append(info)
        res["S-IM"].append(summarize(s_im.run(bars, prm)[0].trades, total_h, YEARS))
        res["S-REV"].append(summarize(s_rev.run(bars, prm)[0].trades, total_h, YEARS))
        res["S-BASE-TFD1"].append(summarize(s_base.run(bars, prm, time_stop=False)[0].trades, total_h, YEARS))
        res["S-BASE-TFD1-7T"].append(summarize(s_base.run(bars, prm, time_stop=True)[0].trades, total_h, YEARS))
    strategies = {k: pooled(v) for k, v in res.items()}
    for v in strategies.values():
        v["admissible_holding"] = v["max_holding_hours"] <= prm["P-OP-HOLD-MAX-H"] + 24.0
    out = {
        "calculator": "research/reference_strategies/turnover_simulation.py", "model": "MOD-TURN",
        "inputs": input_hashes(["parameters.json"]), "seed": SEED, "synthetic": True,
        "setup": {"instruments": N_INSTR, "years": YEARS, "bars_per_day": BARS_PER_DAY, "window_bars": WINDOW_LEN, "window_start_bar": WINDOW_START,
                  "sigma_annual": [round(0.15 + 0.04 * k, 2) for k in range(N_INSTR)], "innovations": "t(5), Varianz 1",
                  "regime": {"enter_per_day": 0.01, "exit_per_day": 0.05, "vol_multiple": 2.0}, "intraday_vol_factor": {"kernzeit": 1.35, "sonst": 0.85},
                  "weekend_gap_vol_factor": 2.0,
                  "note": "Testumgebung (keine Parameter des Systems): synthetische Preise ohne Edge; nur Umschlag und Haltedauer sind aussagekräftig (R-02)."},
        "tf_forecast": {"fdm_mean": math.fsum(i["fdm"] for i in tf_info) / len(tf_info),
                        "scalars_mean": [math.fsum(i["scalars"][j] for i in tf_info) / len(tf_info) for j in range(len(tf_info[0]["scalars"]))]},
        "strategies": strategies,
    }
    ok = write_or_check(OUT, dumps(out), a.check)
    if not a.check:
        for k, v in strategies.items():
            print(f"{k:<16} RT/Jahr {v['round_turns_per_year']:7.1f}  Zeit im Markt {v['time_in_market']:.2f}  Median {v['holding_hours_median']:6.1f} h"
                  f"  4h–4T {v['share_within_4h_4d']:.2f}  Zeitstopp {v['share_timestop']:.3f}  max {v['max_holding_hours']:.0f} h")
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
