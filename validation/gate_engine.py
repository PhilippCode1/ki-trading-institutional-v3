#!/usr/bin/env python3
"""Interpreter der Evidenztore und Monitore aus research/evidence_gates.json (Konzeptpaket v3.0; Technik übernommen aus v2.0).

Wertet Torfälle (examples/valid/gate_cases/*.json) aus und prüft statisch, dass jede Regel syntaktisch
gültig ist, die letzte Regel immer greift, nur deklarierte Variablen verwendet werden und jede Ergebnisregel
durch mindestens einen Fall abgedeckt ist. REFERENZ-Semantik für den späteren Evaluator, kein Produktionscode.

Aufruf:  python validation/gate_engine.py --root .
        python validation/gate_engine.py --root . --gate GATE-G0 --facts g0_facts.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from expr import PARAMS_KEY, ExprError, _param, check_syntax, evaluate, load_param_values, params_used, value, variables  # noqa: E402

OUTCOMES = {"PASS", "FAIL", "INCONCLUSIVE", "INVALID", "ERROR", "BLOCKED_EXTERNAL"}


def load_gates(root: Path) -> dict:
    doc = json.loads((root / "research" / "evidence_gates.json").read_text(encoding="utf-8"))
    return {g["id"]: g for g in doc["gates"]}


def evaluate_gate(g: dict, facts: dict, params: dict | None = None) -> dict:
    """Liefert {'outcome', 'rule', 'flags', 'derived'}; Ausdrucksfehler ergeben ERROR mit Begründung.

    params: Parameterwerte aus parameters.json (Schwellen der Regeln werden als {"param": …} referenziert)."""
    facts = dict(facts)
    if params is not None:
        facts[PARAMS_KEY] = params
    for p in g["prerequisites"]:
        try:
            ok = bool(evaluate(p["expr"], facts))
        except ExprError as e:
            return {"outcome": "ERROR", "rule": p["id"], "flags": [], "derived": {}, "detail": str(e)}
        if not ok:
            return {"outcome": p["on_fail"], "rule": p["id"], "flags": [], "derived": {}}
    derived = {}
    for c in g["computations"]:
        try:
            derived[c["name"]] = value(c["expr"], facts)
        except ExprError as e:
            return {"outcome": "ERROR", "rule": c["name"], "flags": [], "derived": derived, "detail": str(e)}
        facts[c["name"]] = derived[c["name"]]
    outcome, rule = None, None
    for r in g["outcome_rules"]:
        try:
            if bool(evaluate(r["when"], facts)):
                outcome, rule = r["outcome"], r["id"]
                break
        except ExprError as e:
            return {"outcome": "ERROR", "rule": r["id"], "flags": [], "derived": derived, "detail": str(e)}
    flags = []
    for fl in g.get("flags", []):
        try:
            if bool(evaluate(fl["when"], facts)):
                flags.append(fl["name"])
        except ExprError:
            flags.append(fl["name"] + ":NICHT_AUSWERTBAR")
    return {"outcome": outcome, "rule": rule, "flags": flags, "derived": derived}


def _all_exprs(g: dict):
    for p in g["prerequisites"]:
        yield p["id"], p["expr"]
    for c in g["computations"]:
        yield c["name"], c["expr"]
    for r in g["outcome_rules"]:
        yield r["id"], r["when"]
    for fl in g.get("flags", []):
        yield fl["name"], fl["when"]


def static_checks(gates: dict, params: dict | None = None) -> list:
    errs = []
    for gid, g in gates.items():
        if params is not None:
            for where, ex in _all_exprs(g):
                for ref in params_used(ex):
                    try:
                        _param({PARAMS_KEY: params}, list(ref))
                    except ExprError as e:
                        errs.append(f"{gid} {where}: {e}")
        declared = {i["name"] for i in g["inputs"]}
        comp = [c["name"] for c in g["computations"]]
        known = declared | set(comp)
        pre_vars = set()
        for p in g["prerequisites"]:
            errs += [f"{gid} {p['id']}: {e}" for e in check_syntax(p["expr"])]
            if p["on_fail"] not in OUTCOMES:
                errs.append(f"{gid} {p['id']}: on_fail {p['on_fail']} unbekannt")
            pre_vars |= variables(p["expr"])
        known |= pre_vars
        for i, c in enumerate(g["computations"]):
            errs += [f"{gid} {c['name']}: {e}" for e in check_syntax(c["expr"])]
            for var in variables(c["expr"]):
                if var not in declared and var not in comp[:i] and not var.startswith("inputs."):
                    errs.append(f"{gid} {c['name']}: Variable {var} nicht deklariert")
        ids = [r["id"] for r in g["outcome_rules"]]
        if len(ids) != len(set(ids)):
            errs.append(f"{gid}: doppelte Regel-IDs")
        for r in g["outcome_rules"]:
            if r["outcome"] not in OUTCOMES:
                errs.append(f"{gid} {r['id']}: Ergebnis {r['outcome']} unbekannt")
            errs += [f"{gid} {r['id']}: {e}" for e in check_syntax(r["when"])]
            for var in variables(r["when"]):
                if var not in known and not var.startswith("inputs."):
                    errs.append(f"{gid} {r['id']}: Variable {var} nicht deklariert")
        if not g["outcome_rules"] or g["outcome_rules"][-1]["when"] != {"const": True}:
            errs.append(f"{gid}: letzte Regel muss immer greifen")
        for oc in {r["outcome"] for r in g["outcome_rules"]} | {p["on_fail"] for p in g["prerequisites"]}:
            if oc not in g["next_steps"]:
                errs.append(f"{gid}: next_steps fehlt für {oc}")
    return errs


def run_all(root: Path) -> dict:
    gates = load_gates(root)
    params = load_param_values(root)
    res = {"static_errors": static_checks(gates, params), "cases": []}
    hit_rules = {gid: set() for gid in gates}
    pre_hit = {gid: set() for gid in gates}
    for p in sorted((root / "examples" / "valid" / "gate_cases").glob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        g = gates.get(c["gate"])
        if g is None:
            res["cases"].append({"id": c["id"], "passed": False, "errors": [f"Tor {c['gate']} unbekannt"]})
            continue
        r = evaluate_gate(g, c["facts"], params)
        errs = []
        if r["outcome"] != c["expect_outcome"]:
            errs.append(f"Ergebnis {r['outcome']} ({r['rule']}), erwartet {c['expect_outcome']}")
        if "expect_rule" in c and r["rule"] != c["expect_rule"]:
            errs.append(f"Regel {r['rule']}, erwartet {c['expect_rule']}")
        if "expect_flags" in c and sorted(r["flags"]) != sorted(c["expect_flags"]):
            errs.append(f"Flags {r['flags']}, erwartet {c['expect_flags']}")
        if r["rule"] in {x["id"] for x in g["outcome_rules"]}:
            hit_rules[g["id"]].add(r["rule"])
        if r["rule"] in {x["id"] for x in g["prerequisites"]}:
            pre_hit[g["id"]].add(r["rule"])
        res["cases"].append({"file": str(p.relative_to(root)), "id": c["id"], "gate": c["gate"], "outcome": r["outcome"],
                             "rule": r["rule"], "passed": not errs, "errors": errs,
                             "derived": {k: round(v, 6) if isinstance(v, float) else v for k, v in r["derived"].items()}})
    uncovered = []
    for gid, g in gates.items():
        for rr in g["outcome_rules"]:
            if rr["id"] not in hit_rules[gid]:
                uncovered.append(f"{gid}:{rr['id']}")
        for pr in g["prerequisites"]:
            if pr["id"] not in pre_hit[gid]:
                uncovered.append(f"{gid}:{pr['id']}")
    res["uncovered_rules"] = uncovered
    res["passed"] = not res["static_errors"] and all(c["passed"] for c in res["cases"]) and not uncovered
    return res


def evaluate_file(root: Path, gate_id: str, facts_path: Path) -> dict:
    """Ein Tor mit Fakten aus einer JSON-Datei auswerten (G0 in der Repository-CI, später der Evaluator im Prüfmodul).
    Ergebnis mit SHA-256 der Eingaben; Signatur und Laufbeleg ergänzt der Aufrufer (schemas/gate_result.schema.json)."""
    import hashlib
    gates = load_gates(root)
    if gate_id not in gates:
        raise SystemExit(f"Tor {gate_id} unbekannt")
    raw = facts_path.read_bytes()
    r = evaluate_gate(gates[gate_id], json.loads(raw.decode("utf-8")), load_param_values(root))
    return {"gate": gate_id, "inputs_sha256": hashlib.sha256(raw).hexdigest(), "outcome": r["outcome"], "rule_id": r["rule"],
            "flags": r["flags"], "derived": {k: round(v, 9) if isinstance(v, float) else v for k, v in r["derived"].items()}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Evidenztore prüfen und Torfälle auswerten")
    ap.add_argument("--root", default=".")
    ap.add_argument("--gate", default=None, help="nur dieses Tor mit --facts auswerten (z. B. GATE-G0)")
    ap.add_argument("--facts", default=None, help="JSON-Datei mit den Fakten des Tors")
    a = ap.parse_args(argv)
    if a.gate or a.facts:
        if not (a.gate and a.facts):
            raise SystemExit("--gate und --facts nur gemeinsam")
        out = evaluate_file(Path(a.root).resolve(), a.gate, Path(a.facts))
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0 if out["outcome"] not in ("ERROR", None) else 1
    res = run_all(Path(a.root).resolve())
    for e in res["static_errors"]:
        print("STATIK", e)
    for c in res["cases"]:
        print("FALL", c["id"], c.get("outcome"), c.get("rule"), "OK" if c["passed"] else "FEHLER " + "; ".join(c["errors"]))
    if res["uncovered_rules"]:
        print("UNGEDECKT", res["uncovered_rules"])
    print("GATE_ENGINE", "BESTANDEN" if res["passed"] else "NICHT_BESTANDEN")
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
