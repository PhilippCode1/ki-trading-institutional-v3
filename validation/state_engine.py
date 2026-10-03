#!/usr/bin/env python3
"""Interpreter der Zustandsautomaten aus architecture/state_machines.json (Konzeptpaket v3.0; Technik übernommen aus v2.0).

Zweck: Die Regeln in state_machines.json sind ausführbar. Dieses Modul spielt Beispiel-Traces
(examples/valid/state_traces/*.json) gegen die Automaten ab und prüft statische Eigenschaften:
Erreichbarkeit, definierte Ziel- und Ausgangszustände, eindeutige Kennungen, Parameterverweise der Wächter,
Vollständigkeit der Betreiberaktionen und – für den Sperrgrund-Verband SM-SAFETY – die Schutzbasis über ALLE
Kombinationen von Stufen (keine Kombination aktiver Sperrgründe entzieht Schutzaktionen, keine Kombination erweitert
Rechte). Es ist eine REFERENZ-Semantik für die spätere Implementierung, kein Produktionscode.

Aufruf:  python validation/state_engine.py --root .      (alle Traces und statischen Prüfungen)
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from expr import PARAMS_KEY, ExprError, _param, check_syntax, evaluate, load_param_values, params_used  # noqa: E402

TERMINAL_EXCEPTION_EVENTS = {"LATE_FILL": "Brokerfakt nach Endzustand (Incident)", "REOPEN": "neue Evidenz",
                             "FILL_DUPLICATE": "bekannte Ausführungs-ID (nur SELF, verworfen)"}


class EngineError(Exception):
    pass


def load_doc(root: Path) -> dict:
    return json.loads((root / "architecture" / "state_machines.json").read_text(encoding="utf-8"))


def load_machines(root: Path) -> dict:
    return {m["id"]: m for m in load_doc(root)["machines"]}


def _ctx(context: dict, params: dict | None) -> dict:
    c = dict(context or {})
    if params is not None:
        c[PARAMS_KEY] = params
    return c


# ----------------------------------------------------------------------------------------------- FSM
def fsm_step(m: dict, state: str, event: str, ctx: dict):
    """Liefert (neuer_zustand, transition_id oder None). None = ungültiges Ereignis im Zustand.

    Bei Automaten mit broker_fact_target führt ein nicht vorgesehenes Broker- oder Abgleichsereignis in diesen Zustand
    (Brokerfakt gewinnt, Abgleich erzwingen); das Ereignis gilt trotzdem als ungültig (Incident)."""
    for t in m["transitions"]:
        if event != t["event"] or state not in t["from"]:
            continue
        try:
            ok = bool(evaluate(t["guard"], ctx))
        except ExprError as e:
            raise EngineError(f"{m['id']} {t['id']}: Wächter nicht auswertbar ({e})") from e
        if ok:
            return (state if t["to"] == "SELF" else t["to"]), t["id"]
    target = m.get("broker_fact_target")
    if target and state not in set(m.get("broker_fact_exempt_states", [])):
        src = {e["id"]: e["source"] for e in m["events"]}.get(event)
        terminal = {s["id"] for s in m["states"] if s["terminal"]}
        if src in set(m.get("broker_fact_sources", [])) and state not in terminal:
            return target, None
    return state, None


# ----------------------------------------------------------------------------------------------- Verband
def lattice_apply(m: dict, reasons: set, event: str, ctx: dict) -> tuple:
    changed = False
    new = set(reasons)
    for r in m["reasons"]:
        if event in r["set_events"] and r["id"] not in new:
            new.add(r["id"])
            changed = True
    for r in m["reasons"]:
        if r["id"] in new and event in r["clear_events"] and event not in r["set_events"]:
            try:
                ok = bool(evaluate(r["clear_guard"], ctx))
            except ExprError:
                ok = False
            if ok:
                new.discard(r["id"])
                changed = True
    return new, changed


def lattice_state(m: dict, reasons: set) -> str:
    level_of = {r["id"]: r["level"] for r in m["reasons"]}
    if not reasons:
        return "READY"
    return max((level_of[r] for r in reasons), key=lambda lv: m["level_rank"][lv])


def allowed_for_levels(m: dict, levels) -> list:
    """Erlaubte Aktionen = Schutzbasis (außer in ausgeschlossenen Stufen) ∪ Schnittmenge der Verfeinerungen aller Stufen."""
    levels = set(levels)
    refine = m["allowed_actions"]
    sets = [set(refine[lv]) for lv in levels] if levels else [set(refine["READY"])]
    out = set.intersection(*sets)
    if not levels & set(m.get("protection_base_excluded_levels", [])):
        out |= set(m.get("protection_base", []))
    return sorted(out)


def lattice_allowed(m: dict, reasons: set) -> list:
    level_of = {r["id"]: r["level"] for r in m["reasons"]}
    return allowed_for_levels(m, {level_of[r] for r in reasons})


# ----------------------------------------------------------------------------------------------- Traces
def run_trace(machines: dict, trace: dict, params: dict | None = None) -> list:
    """Spielt einen Trace ab; liefert Liste von Abweichungen (leer = bestanden)."""
    m = machines.get(trace["machine"])
    if m is None:
        return [f"{trace['id']}: Automat {trace['machine']} unbekannt"]
    errs = []
    if m["kind"] == "LATTICE":
        reasons = set(trace.get("initial_reasons") or [])
        known = {r["id"] for r in m["reasons"]}
        if reasons - known:
            return [f"{trace['id']}: unbekannte Startgründe {sorted(reasons - known)}"]
        for i, st in enumerate(trace["steps"], 1):
            reasons, _ = lattice_apply(m, reasons, st["event"], _ctx(st.get("context"), params))
            state = lattice_state(m, reasons)
            if state != st["expect_state"]:
                errs.append(f"{trace['id']} Schritt {i} ({st['event']}): Zustand {state}, erwartet {st['expect_state']}")
            if "expect_reasons" in st and sorted(reasons) != sorted(st["expect_reasons"]):
                errs.append(f"{trace['id']} Schritt {i}: Gründe {sorted(reasons)}, erwartet {sorted(st['expect_reasons'])}")
            if "expect_allowed" in st and lattice_allowed(m, reasons) != sorted(st["expect_allowed"]):
                errs.append(f"{trace['id']} Schritt {i}: erlaubt {lattice_allowed(m, reasons)}, erwartet {sorted(st['expect_allowed'])}")
        return errs
    state = trace.get("start") or m["initial"]
    for i, st in enumerate(trace["steps"], 1):
        try:
            new, tid = fsm_step(m, state, st["event"], _ctx(st.get("context"), params))
        except EngineError as e:
            errs.append(f"{trace['id']} Schritt {i}: {e}")
            break
        invalid = tid is None
        if invalid != bool(st.get("expect_invalid", False)):
            errs.append(f"{trace['id']} Schritt {i} ({st['event']} in {state}): ungültig={invalid}, erwartet {st.get('expect_invalid', False)}")
        state = new
        if state != st["expect_state"]:
            errs.append(f"{trace['id']} Schritt {i} ({st['event']}): Zustand {state}, erwartet {st['expect_state']}")
    return errs


# ----------------------------------------------------------------------------------------------- Statik
def _param_errors(where: str, expr, params: dict | None) -> list:
    if params is None:
        return []
    out = []
    for ref in params_used(expr):
        try:
            _param({PARAMS_KEY: params}, list(ref))
        except ExprError as e:
            out.append(f"{where}: {e}")
    return out


def lattice_static(mid: str, m: dict, params: dict | None) -> list:
    errs = []
    states = {s["id"] for s in m["states"]}
    levels = list(m["levels"])
    if states != set(levels):
        errs.append(f"{mid}: Zustände ≠ Stufen")
    ids = [r["id"] for r in m["reasons"]]
    if len(ids) != len(set(ids)):
        errs.append(f"{mid}: doppelte Sperrgründe")
    for r in m["reasons"]:
        if r["level"] not in levels or r["level"] == "READY":
            errs.append(f"{mid}: {r['id']} mit unzulässiger Stufe {r['level']}")
        if r["class"] not in m["reason_classes"]:
            errs.append(f"{mid}: {r['id']} mit unbekannter Klasse {r['class']}")
        if not r["set_events"] or not r["clear_events"]:
            errs.append(f"{mid}: {r['id']} ohne setzendes oder lösendes Ereignis")
        if set(r["set_events"]) & set(r["clear_events"]):
            errs.append(f"{mid}: {r['id']}: Ereignis setzt und löst zugleich")
        errs += [f"{mid} {r['id']}: {e}" for e in check_syntax(r["clear_guard"])]
        errs += _param_errors(f"{mid} {r['id']}", r["clear_guard"], params)
        if r["class"].startswith("LATCHED") and r["clear_guard"] == {"const": True}:
            errs.append(f"{mid}: {r['id']}: verriegelter Grund ohne Wächter")
    actions = set(m.get("actions", {}))
    for lv in levels:
        if lv not in m["allowed_actions"]:
            errs.append(f"{mid}: Stufe {lv} ohne allowed_actions")
            continue
        unknown = set(m["allowed_actions"][lv]) - actions
        if unknown:
            errs.append(f"{mid}: Stufe {lv} mit unbekannten Aktionen {sorted(unknown)}")
        for a, implied in m.get("action_implications", {}).items():
            if a in m["allowed_actions"][lv] and not set(implied) <= set(m["allowed_actions"][lv]):
                errs.append(f"{mid}: Stufe {lv} erlaubt {a}, aber nicht die daraus folgenden {implied}")
    base = set(m.get("protection_base", []))
    if base - actions:
        errs.append(f"{mid}: Schutzbasis mit unbekannten Aktionen {sorted(base - actions)}")
    if "ENTRY" in base:
        errs.append(f"{mid}: ENTRY in der Schutzbasis")
    if "ENTRY" in set().union(*[set(v) for k, v in m["allowed_actions"].items() if k != "READY"]):
        errs.append(f"{mid}: ENTRY außerhalb von READY erlaubt")
    # Kombinationsprüfung über alle Teilmengen der Stufen (ohne READY): Schutzbasis, Monotonie, Einstieg nur ohne Grund
    reason_levels = [lv for lv in levels if lv != "READY"]
    excluded = set(m.get("protection_base_excluded_levels", []))
    required = set(m.get("required_in_every_combination", []))
    combos = 0
    for k in range(0, len(reason_levels) + 1):
        for combo in itertools.combinations(reason_levels, k):
            combos += 1
            s = set(combo)
            allowed = set(allowed_for_levels(m, s))
            if not (s & excluded) and not required <= allowed:
                errs.append(f"{mid}: Kombination {sorted(s)} entzieht Schutzaktionen {sorted(required - allowed)}")
            if ("ENTRY" in allowed) != (not s):
                errs.append(f"{mid}: Kombination {sorted(s)}: ENTRY-Regel verletzt")
            for lv in reason_levels:
                if lv not in s and not set(allowed_for_levels(m, s | {lv})) <= allowed:
                    errs.append(f"{mid}: zusätzlicher Grund der Stufe {lv} erweitert Rechte von {sorted(s)}")
    m["_combinations_checked"] = combos
    return errs


def fsm_static(mid: str, m: dict, params: dict | None) -> list:
    errs = []
    states = {s["id"] for s in m["states"]}
    terminal = {s["id"] for s in m["states"] if s["terminal"]}
    events = {e["id"] for e in m["events"]}
    tids = [t["id"] for t in m["transitions"]]
    if len(tids) != len(set(tids)):
        errs.append(f"{mid}: doppelte Übergangs-IDs")
    if m["initial"] not in states:
        errs.append(f"{mid}: Startzustand unbekannt")
    reach = {m["initial"]}
    grown = True
    while grown:
        grown = False
        for t in m["transitions"]:
            if set(t["from"]) & reach:
                to = t["to"]
                if to != "SELF" and to not in reach:
                    reach.add(to)
                    grown = True
    for t in m["transitions"]:
        for f in t["from"]:
            if f not in states:
                errs.append(f"{mid} {t['id']}: from {f} unbekannt")
        if t["to"] != "SELF" and t["to"] not in states:
            errs.append(f"{mid} {t['id']}: to {t['to']} unbekannt")
        if t["event"] not in events:
            errs.append(f"{mid} {t['id']}: Ereignis {t['event']} nicht deklariert")
        if set(t["from"]) & terminal:
            if t["event"] not in TERMINAL_EXCEPTION_EVENTS:
                errs.append(f"{mid} {t['id']}: Übergang aus Endzustand ohne Ausnahmeregel")
            elif t["event"] == "FILL_DUPLICATE" and t["to"] != "SELF":
                errs.append(f"{mid} {t['id']}: FILL_DUPLICATE darf den Zustand nicht ändern")
        errs += [f"{mid} {t['id']}: {e}" for e in check_syntax(t["guard"])]
        errs += _param_errors(f"{mid} {t['id']}", t["guard"], params)
    unreachable = states - reach
    if unreachable:
        errs.append(f"{mid}: unerreichbare Zustände {sorted(unreachable)}")
    if m["invalid_event_policy"] not in ("IGNORE_AND_LOG", "REJECT_AND_LOG_SECURITY_EVENT", "BROKER_FACT_WINS_INCIDENT_AND_SYNC"):
        errs.append(f"{mid}: unbekannte invalid_event_policy")
    if m.get("broker_fact_target") and m["broker_fact_target"] not in states:
        errs.append(f"{mid}: broker_fact_target unbekannt")
    # Vollständigkeit: jedes Broker- und Abgleichsereignis ist in jedem nicht terminalen Zustand behandelt – durch einen
    # Übergang, durch broker_fact_target oder durch eine ausdrückliche Ausnahme (not_applicable).
    if m["invalid_event_policy"] == "BROKER_FACT_WINS_INCIDENT_AND_SYNC":
        srcs = set(m.get("broker_fact_sources", []))
        na = {(x["state"], x["event"]) for x in m.get("not_applicable", [])}
        for e in m["events"]:
            if e["source"] not in srcs:
                continue
            for s in states - terminal:
                handled = any(e["id"] == t["event"] and s in t["from"] for t in m["transitions"])
                if not handled and not m.get("broker_fact_target") and (s, e["id"]) not in na:
                    errs.append(f"{mid}: Brokerereignis {e['id']} im Zustand {s} weder behandelt noch als nicht anwendbar begründet")
    return errs


def cross_checks(doc: dict, machines: dict, op_enum: set | None) -> list:
    errs = []
    op_map = doc.get("operator_event_actions", {})
    outside = set(doc.get("operator_actions_outside_machines", {}))
    used_actions = set()
    for mid, m in machines.items():
        if m["kind"] == "LATTICE":
            srcs = {e["id"]: e["source"] for e in m["events"]}
            for r in m["reasons"]:
                for ev in r["clear_events"]:
                    if srcs.get(ev) == "OPERATOR":
                        if ev not in op_map:
                            errs.append(f"{mid} {r['id']}: Betreiberereignis {ev} ohne Aktionstyp")
                        else:
                            used_actions.add(op_map[ev])
            for ev in {e for r in m["reasons"] for e in r["set_events"]}:
                if srcs.get(ev) == "OPERATOR":
                    if ev not in op_map:
                        errs.append(f"{mid}: Betreiberereignis {ev} ohne Aktionstyp")
                    else:
                        used_actions.add(op_map[ev])
            continue
        for t in m["transitions"]:
            if t["authorization"] == "OPERATOR_SIGNED":
                if t["event"] not in op_map:
                    errs.append(f"{mid} {t['id']}: signiertes Betreiberereignis {t['event']} ohne Aktionstyp")
                else:
                    used_actions.add(op_map[t["event"]])
    if op_enum is not None:
        for ev, act in op_map.items():
            if act not in op_enum:
                errs.append(f"operator_event_actions: {ev} → {act} fehlt in schemas/operator_action.schema.json")
        for act in sorted(op_enum - used_actions - outside):
            errs.append(f"operator_action {act}: weder von einem Automaten noch als Aktion außerhalb der Automaten belegt")
        for act in sorted(outside - op_enum):
            errs.append(f"operator_actions_outside_machines: {act} fehlt im Schema")
    safety = machines.get("SM-SAFETY")
    order = machines.get("SM-ORDER")
    if safety and order and "order_kind_permissions" in order:
        acts = set(safety.get("actions", {}))
        for kind, perms in order["order_kind_permissions"].items():
            if set(perms) - acts:
                errs.append(f"SM-ORDER order_kind_permissions {kind}: unbekannte Aktionen {sorted(set(perms) - acts)}")
        covered = {p for perms in order["order_kind_permissions"].values() for p in perms}
        if acts - covered - {"RECONCILE"}:
            errs.append(f"SM-SAFETY Aktionen ohne Auftragsart: {sorted(acts - covered - {'RECONCILE'})}")
    return errs


def static_checks(machines: dict, params: dict | None = None, doc: dict | None = None, op_enum: set | None = None) -> list:
    errs = []
    for mid, m in machines.items():
        errs += lattice_static(mid, m, params) if m["kind"] == "LATTICE" else fsm_static(mid, m, params)
    if doc is not None:
        errs += cross_checks(doc, machines, op_enum)
    return errs


def load_operator_enum(root: Path) -> set | None:
    p = root / "schemas" / "operator_action.schema.json"
    if not p.exists():
        return None
    s = json.loads(p.read_text(encoding="utf-8"))
    return set(s["properties"]["action"]["enum"])


def run_all(root: Path) -> dict:
    doc = load_doc(root)
    machines = {m["id"]: m for m in doc["machines"]}
    params = load_param_values(root)
    res = {"static_errors": static_checks(machines, params, doc, load_operator_enum(root)), "traces": []}
    res["lattice_combinations_checked"] = {mid: m.get("_combinations_checked") for mid, m in machines.items() if m["kind"] == "LATTICE"}
    tdir = root / "examples" / "valid" / "state_traces"
    covered = set()
    for p in sorted(tdir.glob("*.json")):
        tr = json.loads(p.read_text(encoding="utf-8"))
        errs = run_trace(machines, tr, params)
        covered.add(tr["machine"])
        res["traces"].append({"file": str(p.relative_to(root)), "id": tr["id"], "passed": not errs, "errors": errs})
    res["machines_without_trace"] = sorted(set(machines) - covered)
    res["passed"] = not res["static_errors"] and all(t["passed"] for t in res["traces"]) and not res["machines_without_trace"]
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Zustandsautomaten prüfen und Traces abspielen")
    ap.add_argument("--root", default=".")
    a = ap.parse_args(argv)
    res = run_all(Path(a.root).resolve())
    for e in res["static_errors"]:
        print("STATIK", e)
    for mid, n in res["lattice_combinations_checked"].items():
        print("KOMBINATIONEN", mid, n)
    for t in res["traces"]:
        print("TRACE", t["id"], "OK" if t["passed"] else "FEHLER", "; ".join(t["errors"]))
    if res["machines_without_trace"]:
        print("OHNE_TRACE", res["machines_without_trace"])
    print("STATE_ENGINE", "BESTANDEN" if res["passed"] else "NICHT_BESTANDEN")
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
