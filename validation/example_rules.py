#!/usr/bin/env python3
"""Semantische Beispielregeln der Datenverträge (R-EX-01 … R-EX-12).

JSON Schema prüft Form und bedingte Pflichtfelder; diese Regeln prüfen Beziehungen zwischen Feldern und gegen parameters.json
(führende Quelle der Schwellen). Sie sind die Referenzsemantik für die spätere Implementierung und werden in der Paketprüfung (P08)
auf alle Beispiele unter examples/ angewandt.

Aufruf:  python validation/example_rules.py --root .
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode = True


def _t(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def _d(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def r01(doc, P):
    """Verkleinerung rundet ab: qty_approved ≤ qty_requested."""
    return doc["qty_approved"] <= doc["qty_requested"]


def r02(doc, P):
    """Signaturgültigkeit höchstens P-SEC-SIG-EXPIRY-MIN nach Erstellung."""
    return (_t(doc["expires_utc"]) - _t(doc["created_utc"])).total_seconds() <= 60 * P["P-SEC-SIG-EXPIRY-MIN"]


def r03(doc, P):
    """Grant-Laufzeit höchstens P-SEC-GRANT-DAYS je Art."""
    days = (_t(doc["valid_until_utc"]) - _t(doc["valid_from_utc"])).total_seconds() / 86400
    return 0 < days <= P["P-SEC-GRANT-DAYS"][doc["kind"]]


def r04(doc, P):
    """Entwicklungsfenster endet vor dem Holdout."""
    return _d(doc["dev_window"]["end"]) < _d(doc["holdout_window"]["start"])


def r05(doc, P):
    """Registrierung vor Ergebnisansicht; Versuch im Budget; Budget ≤ P-OC-TRIALS."""
    viewed = doc["results_viewed_utc"]
    in_time = viewed is None or _t(viewed) >= _t(doc["registered_utc"])
    return in_time and doc["trial_number"] <= doc["trials_budget"] <= P["P-OC-TRIALS"]


def r06(doc, P):
    """Autor ≠ Prüfer (und ≠ zweite Freigabe)."""
    keys = [doc["author_key"], doc["reviewer_key"]] + ([doc["second_approval_key"]] if "second_approval_key" in doc else [])
    return len(set(keys)) == len(keys)


def r07(doc, P):
    """Prüfrunden höchstens P-AI-REVIEW-ROUNDS."""
    return doc["review_round"] <= P["P-AI-REVIEW-ROUNDS"]


def r08(doc, P):
    """Nutzlast höchstens P-AI-PAYLOAD-MAX-MIB."""
    return doc["payload_bytes"] <= P["P-AI-PAYLOAD-MAX-MIB"] * 1048576


def r09(doc, P):
    """Tickwert = Multiplikator × Tick."""
    return Decimal(doc["multiplier"]) * Decimal(doc["tick_size"]) == Decimal(doc["tick_value"])


def r10(doc, P):
    """Summe der Teilpositionen = Brokerposition."""
    return sum(a["qty"] for a in doc["strategy_allocations"]) == doc["qty"]


def r11(doc, P):
    """Negativnachweis mit mindestens P-EXE-NEGPROOF-CYCLES sauberen Zyklen."""
    if doc["state"] != "NOT_EXECUTED_PROVEN":
        return True
    return doc["negative_proof"]["cycles"] >= P["P-EXE-NEGPROOF-CYCLES"]


def r12(doc, P):
    """Margin-Level = Equity / Margin (Rundung auf 1e-3), ohne Margin null."""
    m = Decimal(doc["margin"])
    if m == 0:
        return doc["margin_level"] is None
    return doc["margin_level"] is not None and abs(Decimal(doc["equity"]) / m - Decimal(doc["margin_level"])) <= Decimal("0.001")


RULES = {"R-EX-01": ("risk_decision", r01), "R-EX-02": ("operator_action", r02), "R-EX-03": ("live_grant", r03), "R-EX-04": ("data_manifest", r04),
         "R-EX-05": ("experiment_manifest", r05), "R-EX-06": ("release_manifest", r06), "R-EX-07": ("work_item", r07), "R-EX-08": ("mcp_request", r08),
         "R-EX-09": ("contract_spec", r09), "R-EX-10": ("position", r10), "R-EX-11": ("order_attempt", r11), "R-EX-12": ("account_snapshot", r12)}


def violations(schema: str, doc: dict, params: dict) -> list:
    out = []
    for rid, (sname, fn) in RULES.items():
        if sname != schema:
            continue
        try:
            good = bool(fn(doc, params))
        except (KeyError, TypeError, ValueError, ArithmeticError):
            good = False
        if not good:
            out.append(rid)
    return out


def load_params(root: Path) -> dict:
    doc = json.loads((root / "parameters.json").read_text(encoding="utf-8"))
    return {p["id"]: p["value"] for p in doc["parameters"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Semantische Beispielregeln auf examples/ anwenden")
    ap.add_argument("--root", default=".")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    P = load_params(root)
    idx = json.loads((root / "examples" / "EXAMPLES.json").read_text(encoding="utf-8"))["examples"]
    bad = 0
    for e in idx:
        doc = json.loads((root / e["file"]).read_text(encoding="utf-8"))
        v = violations(e["schema"], doc, P)
        exp = e.get("expected") or {}
        if e["valid"] and v:
            bad += 1
            print("FEHLER", e["file"], "verletzt", v)
        elif not e["valid"] and exp.get("type") == "SEMANTIC" and exp.get("rule") not in v:
            bad += 1
            print("FEHLER", e["file"], "erwartet", exp.get("rule"), "erhalten", v)
    print("EXAMPLE_RULES", "BESTANDEN" if not bad else "NICHT_BESTANDEN", len(idx), "Beispiele")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
