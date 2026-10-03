#!/usr/bin/env python3
"""Steuer-Sensitivität (§5.3) im Umfang der Betreiberentscheidung BQ-03 – keine Steuerberatung (R-11).

BQ-03: Recht und Steuern regelt eine externe Person; das System handelt nur. Deshalb enthält dieses Paket KEINE Steuerszenarien B1/B2
(Abgeltungsteuer, Verlustverrechnung, Körperschaft-/Gewerbesteuer). Es enthält nur:
  1. eine pauschale Sensitivität: positive Jahresergebnisse werden um P-ECO-TAX-SENS gekürzt (runder Rechenwert ohne Rechtsaussage,
     externe Eingabe X-TAX-01), Verluste bleiben ungekürzt (kein Verlustvortrag modelliert – konservativ);
  2. die Beschreibung des Übergabe-Exports für die externe Person (legal/tax_matrix.md).
Die Entscheidungsrechnung weist Ergebnisse „vor Steuern“ und „nach Sensitivitätsabschlag“ aus.
Aufruf: python financials/tax_scenarios.py [--check]   (schreibt financials/tax_sensitivity_example.json)
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.calc import Params, dec, dumps, input_hashes, main_args, money, write_or_check  # noqa: E402

OUT = "financials/tax_sensitivity_example.json"


def after_tax_sensitivity(annual_value, rate) -> float:
    """Pauschaler Abschlag auf positive Jahreswerte; Gleitkomma für Monte-Carlo-Ziehungen."""
    return annual_value * (1.0 - rate) if annual_value > 0 else annual_value


def after_tax_sensitivity_eur(annual_value_eur, rate) -> Decimal:
    v = dec(annual_value_eur)
    return money(v * (1 - dec(rate)) if v > 0 else v)


def main(argv=None) -> int:
    a = main_args(argv)
    P = Params()
    rate = P("P-ECO-TAX-SENS")
    examples = [money(x) for x in ("-5000", "0", "1000", "25000.55")]
    out = {"calculator": "financials/tax_scenarios.py", "scope": "BQ-03: nur pauschale Sensitivität, keine Steuerszenarien (keine Beratung)",
           "inputs": input_hashes(["parameters.json"]), "rate": rate, "external_input": "X-TAX-01",
           "examples": [{"before_eur": x, "after_sensitivity_eur": after_tax_sensitivity_eur(x, rate)} for x in examples]}
    ok = write_or_check(OUT, dumps(out), a.check)
    print("OK" if ok else "FEHLER", OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
