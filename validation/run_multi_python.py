#!/usr/bin/env python3
"""Mehrversionslauf der Paketprüfung (§19.2, §19.4; Test T-PKG-MULTI-001).

Je Interpreter, jeweils mit -W error (Warnungen sind Fehler):
  1. Pins        installierte Versionen = validation/requirements-validation.txt
  2. Rechner     validation/run_calculators.py --check (bytegleiche Neuberechnung aller Rechner)
  3. Bindungen   validation/render_blocks.py --check
  4. Referenz    validation/test_reference_models.py
  5. Semantik    validation/semantic_checks.py
  6. Prüfung     validation/validate_package.py --strict --stage prepack (P01–P13; P07 im Hash-Modus, weil Schritt 2 vollständig nachrechnet)
  7. Linter      python -m ruff check --no-cache . (Konfiguration ruff.toml)
Schreibt validation/execution_log.txt mit dem Paketstand (lib/pkgstate.py), auf dem der Lauf stattfand.

Aufruf:
  python validation/run_multi_python.py --root . --python PFAD_3.11 --python PFAD_3.12 --python PFAD_3.13

Je Version eine virtuelle Umgebung außerhalb des Paketordners mit den gepinnten Abhängigkeiten, zum Beispiel:
  python3.11 -m venv ../venv311 && ../venv311/bin/pip install --require-hashes -r validation/requirements-validation.txt
Der Mehrversionslauf ist der erste Schritt des Belegzyklus; Mutationsbericht und Prüfbericht entstehen danach und werden der Paketprüfung
deshalb als --pending-evidence genannt. Die strenge Prüfung nach frischem Entpacken prüft alle drei Belege ohne diese Ausnahme.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
LOG = "validation/execution_log.txt"
PENDING = "validation/execution_log.txt,validation/mutation_report.json,validation/validation_report.json"
PINS = "validation/requirements-validation.txt"

STEPS = [
    ("Rechner", ["validation/run_calculators.py", "--check"], r"^ERGEBNIS PASS$"),
    ("Bindungen", ["validation/render_blocks.py", "--root", ".", "--check"], r"PRÜFUNG 0 Dateien abweichend 0 Fehler"),
    ("Referenztests", ["validation/test_reference_models.py"], r"^REFERENZTESTS PASS (\d+/\d+)$"),
    ("Semantik", ["validation/semantic_checks.py", "--root", "."], r"^SEMANTIK BESTANDEN$"),
    ("Paketprüfung", ["validation/validate_package.py", "--root", ".", "--strict", "--stage", "prepack", "--calc-mode", "hash",
                      "--pending-evidence", PENDING], r"^ERGEBNIS PASS$"),
    ("Linter", ["-m", "ruff", "check", "--no-cache", "."], r"All checks passed!"),
]

# Wird im geprüften Interpreter ausgeführt: vergleicht installierte Versionen mit den Pins (Marker nur für python_(full_)version)
PIN_PROBE = r'''
import re, sys
from importlib.metadata import version, PackageNotFoundError
ops = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b,
       "==": lambda a, b: a == b, "!=": lambda a, b: a != b}
cur = tuple(sys.version_info[:3])
ok = bad = 0
for ln in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"^([A-Za-z0-9_.-]+)==([^\s;\\]+)\s*(?:;\s*python(?:_full)?_version\s*(<=|>=|==|!=|<|>)\s*'([\d.]+)')?", ln)
    if not m:
        continue
    name, want, op, ver = m.groups()
    if op and not ops[op](cur, tuple(int(x) for x in ver.split("."))):
        continue
    try:
        have = version(name)
    except PackageNotFoundError:
        have = "fehlt"
    if have == want:
        ok += 1
    else:
        bad += 1
        print(f"ABWEICHUNG {name}: gepinnt {want}, installiert {have}")
print(f"PINS {ok}/{ok + bad}")
'''


def clean(line: str, root: Path) -> str:
    """Entfernt lokale Pfade aus Protokollzeilen (R-13, Hygiene P11)."""
    line = line.replace(str(root), ".")
    return re.sub(r"(?:/home|/root|/tmp|/mnt|/Users)/\S*", "<lokaler Pfad>", line)


def run(py: str, args, root: Path, timeout=3600):
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONWARNINGS")}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})
    t0 = time.time()
    r = subprocess.run([py, "-W", "error"] + args, cwd=root, capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or ""), time.time() - t0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--python", action="append", required=True, help="Interpreter (mehrfach); je Version einer")
    ap.add_argument("--log", default=LOG)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    sys.path.insert(0, str(root))
    from lib.pkgstate import state_hash  # noqa: PLC0415
    state = state_hash(root)
    stamp = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Ausführungsprotokoll – Mehrversionslauf (T-PKG-MULTI-001; §19.2, §19.4)",
        f"# Erzeugt von validation/run_multi_python.py am {stamp} auf {platform.system()} {platform.machine()}.",
        "# Paketstand: SHA-256 über alle Inhaltsdateien ohne Laufbelege (lib/pkgstate.py); P13 vergleicht ihn mit dem geprüften Paket.",
        "# Je Interpreter mit -W error: Pins, Rechner --check, render_blocks --check, Referenztests, semantische Querprüfungen,",
        "# Paketprüfung P01–P13 (Stufe prepack, strict, P07 im Hash-Modus), Linter (ruff, ruff.toml).",
        f"PAKETSTAND {state}",
    ]
    summary, all_ok = [], True
    for py in a.python:
        rc, out, _ = run(py, ["-c", "import sys, platform; print(platform.python_version())"], root, timeout=60)
        ver = out.strip().splitlines()[-1] if rc == 0 and out.strip() else "unbekannt"
        parts, ok = [], rc == 0
        rc, out, secs = run(py, ["-c", PIN_PROBE, str(root / PINS)], root, timeout=120)
        m = re.search(r"^PINS (\d+)/(\d+)$", out, re.M)
        pin_ok = rc == 0 and m is not None and m.group(1) == m.group(2) and m.group(2) != "0"
        ok &= pin_ok
        parts.append(f"Pins {'PASS' if pin_ok else 'FAIL'} {m.group(0)[5:] if m else ''}".rstrip())
        lines.append(f"SCHRITT {ver} Pins {'PASS' if pin_ok else 'FAIL'} rc={rc} {secs:.1f} s")
        for ln in out.splitlines():
            if ln.startswith("ABWEICHUNG"):
                lines.append(f"    {clean(ln, root)[:200]}")
        for name, args, pattern in STEPS:
            rc, out, secs = run(py, args, root)
            hit = re.search(pattern, out, re.M)
            step_ok = rc == 0 and hit is not None
            ok &= step_ok
            extra = f" {hit.group(1)}" if hit and hit.groups() else ""
            parts.append(f"{name} {'PASS' if step_ok else 'FAIL'}{extra}")
            last = clean(out.strip().splitlines()[-1], root)[:160] if out.strip() else ""
            lines.append(f"SCHRITT {ver} {name} {'PASS' if step_ok else 'FAIL'} rc={rc} {secs:.1f} s | {last}")
            if not step_ok:
                for ln in [x for x in out.splitlines() if "FEHLER" in x or "Error" in x or "Warning" in x][:12]:
                    lines.append(f"    {clean(ln, root)[:200]}")
        all_ok &= ok
        summary.append(f"PYTHON {ver} -W error | " + " | ".join(parts) + f" | ERGEBNIS {'PASS' if ok else 'FAIL'}")
        print(summary[-1], flush=True)
    if state_hash(root) != state:
        print("ABBRUCH: Paketstand hat sich während des Laufs geändert; kein Protokoll geschrieben")
        return 1
    lines += summary + [f"GESAMT {'PASS' if all_ok else 'FAIL'}"]
    (root / a.log).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"GESAMT {'PASS' if all_ok else 'FAIL'} → {a.log}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
