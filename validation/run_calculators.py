#!/usr/bin/env python3
"""Führt alle Referenzrechner in Abhängigkeitsreihenfolge aus (Schreiben oder --check).

Reihenfolge: Umschlag → Kosten → Prior → Hebel → Stress → Kelly/Ruin → Statistik → Betriebscharakteristik → Kostendrift → Steuer-Sensitivität
→ Entscheidungs-Monte-Carlo. Mit --check wird nichts geschrieben; Exitcode 1, wenn ein Rechner abweicht oder scheitert.
Aufruf: python validation/run_calculators.py [--check] [--python PFAD]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CALCULATORS = [
    "research/reference_strategies/turnover_simulation.py", "financials/cost_model.py", "research/prior_derivation.py",
    "risk/leverage_calculator.py", "risk/stress_test_engine.py", "risk/kelly_ruin_simulator.py", "research/statistical_calculator.py",
    "research/operating_characteristics.py", "operations/costdrift_monitor.py", "operations/monitor_simulation.py", "financials/tax_scenarios.py",
    "financials/decision_montecarlo.py",
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args(argv)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    bad = []
    for c in CALCULATORS:
        t0 = time.time()
        p = subprocess.run([a.python, "-W", "error", c] + (["--check"] if a.check else []), cwd=ROOT, env=env, capture_output=True, text=True)
        last = (p.stdout.strip().splitlines() or [""])[-1]
        print(f"{p.returncode:>2} {time.time() - t0:6.1f}s {c}: {last}")
        if p.returncode != 0:
            bad.append(c)
            print(p.stdout[-2000:], p.stderr[-2000:])
    print("ERGEBNIS", "PASS" if not bad else f"FAIL {bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
