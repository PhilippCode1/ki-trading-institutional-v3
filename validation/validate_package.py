#!/usr/bin/env python3
"""Paketprüfung des Konzeptpakets v3.0 (§19).

Aufruf:
  python validation/validate_package.py --root . [--strict] [--stage prepack|full] [--only P01,P02] [--calc-mode full|hash]
                                        [--report-out PFAD] [--pending-evidence DATEI,DATEI]

Phasen:
  P01 Struktur (§18)                        P08 Beispiele, Torfälle, Zustandstraces
  P02 JSON-Syntax, doppelte Schlüssel       P09 Semantische Querprüfungen (validation/semantic_checks.py)
  P03 Schemas (Draft 2020-12)               P10 Referenztests (validation/test_reference_models.py)
  P04 Registersemantik und Querverweise     P11 Hygiene (Platzhalter, Geheimnisse, personenbezogene Daten, Pfade)
  P05 Verweise im Text                      P12 Selbstbewertung K und E
  P06 Bindungen, erzeugte Inhalte, Zahlen,  P13 Statuswahrheit
      Betreiberfassungen                    P14 Manifest und Prüfsummen (nur Stufe full)
  P07 Referenzrechner --check (--calc-mode hash: nur Eingangs-Hashes; für Mutationsläufe)

Exitcode 0 nur, wenn keine Phase FAIL meldet. Deterministisch bis auf Zeitstempel und Laufzeiten im Bericht.

Belegzyklus (§19.4): Mehrversionslauf (validation/run_multi_python.py) → Mutationslauf (validation/mutation_tests.py) → Prüfung vor dem Packen
(--report-out validation/validation_report.json) → Manifest und Prüfsummen → ZIP → strenge Prüfung nach frischem Entpacken (--stage full).
Laufbelege, die im laufenden Zyklus erst entstehen, nennt --pending-evidence; P01, P05 und P13 verlangen sie dann nicht. Die Prüfung nach dem
Entpacken läuft ohne diese Option und prüft alle Belege samt ihrem Paketstand (lib/pkgstate.py).
Bekannte Prüfgrenzen stehen in README.md (Abschnitt „Grenzen der Prüfung“) und in validation/mutation_catalog.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode = True

PKG_NAME = "KI_Trading_Institutional_v3_0"
MANIFEST = "PACKAGE_MANIFEST.json"
CHECKSUMS = "CHECKSUMS.sha256"
TIMEOUT_S = 3600

# Pflichtdateien nach §18 (Namen dürfen begründet abweichen; Abweichungen stehen in README.md)
REQUIRED = [
    "README.md", "KURZFASSUNG_BETREIBER.md", "Masterkonzept_v3.0.md", "STATUS.md", "requirements.json", "parameters.json", "external_inputs.json",
    "registers/decision_register.json", "registers/risk_register.json", "registers/source_register.json", "registers/resolution_matrix.json",
    "registers/traceability.json", "registers/model_inventory.json", "registers/limits.json", "registers/instruments.json", "registers/costs.json",
    "architecture/system_design.md", "architecture/interfaces.md", "architecture/state_machines.json", "architecture/scenario_catalog.json",
    "architecture/threat_model.md",
    "research/research_plan.md", "research/strategy_family.md", "research/prior_derivation.py", "research/evidence_gates.json",
    "research/statistical_calculator.py", "research/operating_characteristics.py", "research/reference_strategies/turnover_simulation.py",
    "risk/leverage_risk_model.md", "risk/leverage_calculator.py", "risk/kelly_ruin_simulator.py", "risk/stress_test_engine.py",
    "risk/stress_scenarios.json", "risk/limits.md", "risk/margin_liquidity.md",
    "financials/economic_model.md", "financials/cost_model.py", "financials/assumptions.json", "financials/tax_scenarios.py",
    "financials/decision_montecarlo.py", "financials/buy_vs_build.md",
    "execution/oms_ems.md", "execution/broker_killer_tests.md", "execution/tca_model.md", "execution/pretrade_controls.md",
    "data/data_plan.md", "data/vendor_matrix.md", "data/proxy_rules.md", "data/reference_data_spec.md",
    "ai/ai_layer.md", "ai/hermes_integration.md", "ai/eval_suite_spec.md", "ai/mrm_policy.md",
    "security/security_architecture.md", "security/key_management.md",
    "governance/organisation_raci.md", "governance/grants_and_risk_acceptance.md",
    "operations/operations_plan.md", "operations/runbooks.md", "operations/drills.md", "operations/sla_slo.md",
    "legal/applicability_matrix.md", "legal/tax_matrix.md",
    "implementation/build_program.md", "implementation/build_stages.json", "implementation/test_catalog.json",
    "implementation/CODING_AGENT_START.md", "implementation/make_or_buy.md",
    "audit/scorecard_K.json", "audit/scorecard_E.json", "audit/concept_review.md", "audit/independent_review_request.md", "audit/v2_to_v3_mapping.json",
    "validation/validate_package.py", "validation/semantic_checks.py", "validation/mutation_tests.py", "validation/render_blocks.py",
    "validation/gate_engine.py", "validation/state_engine.py", "validation/test_reference_models.py", "validation/execution_log.txt",
    "validation/run_multi_python.py", "validation/requirements-validation.txt", "validation/mutation_catalog.json", "validation/mutation_report.json",
    "validation/validation_report.json", "lib/pkgstate.py", "ruff.toml",
]
REQUIRED_DIRS = ["governance/policies", "schemas", "examples/valid", "examples/invalid", "examples/valid/gate_cases", "examples/valid/state_traces",
                 "research/reference_strategies"]

# Datei → Schema (P03)
SCHEMA_MAP = {
    "registers/source_register.json": "source_register", "parameters.json": "parameters", "registers/costs.json": "costs",
    "registers/instruments.json": "instruments", "registers/decision_register.json": "decision_register", "registers/risk_register.json": "risk_register",
    "registers/model_inventory.json": "model_inventory", "registers/limits.json": "limits", "external_inputs.json": "external_inputs",
    "audit/scorecard_K.json": "scorecard_K", "audit/scorecard_E.json": "scorecard_E",
}

ID_RE = re.compile(r"\b(?:SRC|DEC|P|X|COST|INS|RK|MOD|LIM|REQ|T|KT|GATE|SM|SC|EV|CR5)-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")


class DuplicateKeyError(ValueError):
    pass


def _no_dup(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise DuplicateKeyError(f"doppelter Schlüssel {k!r}")
        seen[k] = v
    return seen


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"), object_pairs_hook=_no_dup)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Phase:
    def __init__(self, pid, title):
        self.id, self.title = pid, title
        self.errors, self.warnings, self.info = [], [], []
        self.status = "PASS"
        self.secs = 0.0

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


class Ctx:
    def __init__(self, root: Path, strict: bool, stage: str, calc_mode: str = "full", pending=()):
        self.root, self.strict, self.stage, self.calc_mode = root, strict, stage, calc_mode
        self.pending = set(pending)    # Laufbelege, die im laufenden Belegzyklus erst entstehen
        self.cache = {}
        self.results = {}          # Ergebnisse einzelner Phasen für P13 (Statuswahrheit)

    def j(self, rel):
        if rel not in self.cache:
            self.cache[rel] = load_json(self.root / rel)
        return self.cache[rel]

    def exists(self, rel):
        return (self.root / rel).exists()

    def run(self, args, timeout=TIMEOUT_S):
        return subprocess.run([sys.executable, "-W", "error"] + args, cwd=self.root, capture_output=True, text=True, timeout=timeout,
                              env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin", "PYTHONHASHSEED": "0",
                                   "PYTHONIOENCODING": "utf-8"})


# ------------------------------------------------------------------------------------------------------------------------ P01
def p01_structure(ctx, ph):
    for rel in REQUIRED:
        if not ctx.exists(rel):
            if rel in ctx.pending:
                ph.info.append(f"Laufbeleg entsteht in diesem Zyklus: {rel}")
            else:
                ph.err(f"Pflichtdatei fehlt: {rel}")
    for rel in REQUIRED_DIRS:
        if not (ctx.root / rel).is_dir():
            ph.err(f"Pflichtordner fehlt: {rel}")
    for p in ctx.root.rglob("*"):
        rel = p.relative_to(ctx.root).as_posix()
        if p.is_symlink():
            ph.err(f"symbolischer Link: {rel}")
        if "__pycache__" in rel or rel.endswith(".pyc"):
            ph.err(f"Bytecode im Paket: {rel}")
    if ctx.stage == "full":
        for rel in (MANIFEST, CHECKSUMS):
            if not ctx.exists(rel):
                ph.err(f"fehlt in Stufe full: {rel}")


# ------------------------------------------------------------------------------------------------------------------------ P02
def p02_json(ctx, ph):
    n = 0
    for p in sorted(ctx.root.rglob("*.json")):
        rel = p.relative_to(ctx.root).as_posix()
        try:
            ctx.cache[rel] = load_json(p)
            n += 1
        except (ValueError, DuplicateKeyError) as ex:
            ph.err(f"{rel}: {ex}")
    ph.info.append(f"{n} JSON-Dateien gelesen")


# ------------------------------------------------------------------------------------------------------------------------ P03
def schema_errors(ctx, name, doc):
    import jsonschema
    sc = ctx.j(f"schemas/{name}.schema.json")
    v = jsonschema.Draft202012Validator(sc, format_checker=jsonschema.FormatChecker())
    return sorted(v.iter_errors(doc), key=lambda e: [str(x) for x in e.path])


def p03_schemas(ctx, ph):
    import jsonschema
    for p in sorted((ctx.root / "schemas").glob("*.schema.json")):
        try:
            jsonschema.Draft202012Validator.check_schema(ctx.j(p.relative_to(ctx.root).as_posix()))
        except jsonschema.SchemaError as ex:
            ph.err(f"ungültiges Schema {p.name}: {ex.message}")
    for rel, name in SCHEMA_MAP.items():
        if not ctx.exists(rel):
            continue
        for e in schema_errors(ctx, name, ctx.j(rel))[:20]:
            ph.err(f"{rel} {'/'.join(str(x) for x in e.path)}: {e.message[:200]}")
    for rel, name in extra_schema_targets(ctx):
        for e in schema_errors(ctx, name, ctx.j(rel))[:20]:
            ph.err(f"{rel} {'/'.join(str(x) for x in e.path)}: {e.message[:200]}")
    for sub, name in (("examples/valid/gate_cases", "gate_case"), ("examples/valid/state_traces", "state_trace")):
        for f in sorted((ctx.root / sub).glob("*.json")):
            rel = f.relative_to(ctx.root).as_posix()
            for e in schema_errors(ctx, name, ctx.j(rel))[:5]:
                ph.err(f"{rel} {'/'.join(str(x) for x in e.path)}: {e.message[:200]}")


def extra_schema_targets(ctx):
    """Weitere Dateien mit Schema: Rechnerergebnisse und Register späterer Etappen (falls vorhanden)."""
    out = []
    for rel, name in [("registers/resolution_matrix.json", "resolution_matrix"), ("requirements.json", "requirements"),
                      ("registers/traceability.json", "traceability"), ("research/evidence_gates.json", "evidence_gates"),
                      ("architecture/state_machines.json", "state_machines"), ("architecture/scenario_catalog.json", "scenario_catalog"),
                      ("implementation/test_catalog.json", "test_catalog"), ("implementation/build_stages.json", "build_stages"),
                      ("risk/stress_scenarios.json", "stress_scenarios"), ("audit/scorecard_K.json", "scorecard_K"), ("audit/scorecard_E.json", "scorecard_E"),
                      ("audit/v2_to_v3_mapping.json", "v2_to_v3_mapping"), ("financials/assumptions.json", "assumptions"),
                      ("operations/runbook_register.json", "runbook_register"), ("operations/drill_register.json", "drill_register"),
                      ("examples/EXAMPLES.json", "examples_index"), ("registers/operator_seal.json", "operator_seal")]:
        if ctx.exists(rel) and ctx.exists(f"schemas/{name}.schema.json"):
            out.append((rel, name))
    return out


# ------------------------------------------------------------------------------------------------------------------------ P04
def id_universe(ctx) -> dict:
    ids = {}

    def add(kind, seq, key="id"):
        s = ids.setdefault(kind, set())
        for x in seq:
            s.add(x[key])

    add("SRC", ctx.j("registers/source_register.json")["sources"])
    add("P", ctx.j("parameters.json")["parameters"])
    add("COST", ctx.j("registers/costs.json")["costs"])
    add("INS", ctx.j("registers/instruments.json")["instruments"])
    add("DEC", ctx.j("registers/decision_register.json")["decisions"])
    add("RK", ctx.j("registers/risk_register.json")["risks"])
    add("MOD", ctx.j("registers/model_inventory.json")["models"])
    add("LIM", ctx.j("registers/limits.json")["limits"])
    add("X", ctx.j("external_inputs.json")["inputs"])
    if ctx.exists("requirements.json"):
        add("REQ", ctx.j("requirements.json")["requirements"])
    if ctx.exists("implementation/test_catalog.json"):
        add("T", ctx.j("implementation/test_catalog.json")["tests"])
    if ctx.exists("research/evidence_gates.json"):
        add("GATE", ctx.j("research/evidence_gates.json")["gates"])
    if ctx.exists("architecture/state_machines.json"):
        add("SM", ctx.j("architecture/state_machines.json")["machines"])
    if ctx.exists("architecture/scenario_catalog.json"):
        add("SC", ctx.j("architecture/scenario_catalog.json")["scenarios"])
    return ids


def resolvable(ref: str, ids: dict, ctx) -> bool:
    kind = ref.split("-")[0]
    if kind in ids:
        if "{" in ref:
            return True
        return ref in ids[kind]
    return True  # andere Präfixe (z. B. Dateiverweise) prüft P05


def p04_registers(ctx, ph):
    ids = id_universe(ctx)
    ctx.ids = ids
    # Eindeutigkeit
    for rel, key in [("registers/source_register.json", "sources"), ("parameters.json", "parameters"), ("registers/costs.json", "costs"),
                     ("registers/instruments.json", "instruments"), ("registers/decision_register.json", "decisions"),
                     ("registers/risk_register.json", "risks"), ("registers/model_inventory.json", "models"), ("registers/limits.json", "limits"),
                     ("external_inputs.json", "inputs")]:
        seq = [x["id"] for x in ctx.j(rel)[key]]
        dup = {i for i in seq if seq.count(i) > 1}
        if dup:
            ph.err(f"{rel}: doppelte IDs {sorted(dup)}")
    src = {s["id"]: s for s in ctx.j("registers/source_register.json")["sources"]}
    # Parameter: Status ↔ Belege
    for prm in ctx.j("parameters.json")["parameters"]:
        for ref in prm["refs"]:
            if not resolvable(ref, ids, ctx):
                ph.err(f"{prm['id']}: unbekannter Verweis {ref}")
        srcs = [r for r in prm["refs"] if r.startswith("SRC-")]
        if prm["status"] == "BELEGT":
            if not srcs:
                ph.err(f"{prm['id']}: Status BELEGT ohne Quelle")
            elif all(src[s]["status"] == "NICHT_GEPRUEFT" for s in srcs if s in src):
                ph.err(f"{prm['id']}: BELEGT stützt sich nur auf NICHT_GEPRUEFT-Quellen")
        if prm["status"] == "BETREIBER" and not any(r.startswith("DEC-OP-") for r in prm["refs"]):
            ph.err(f"{prm['id']}: Betreiberwert ohne Betreiberentscheidung (R-07)")
        if prm["status"] == "ANNAHME" and prm.get("external_input") and prm["external_input"] not in ids["X"]:
            ph.err(f"{prm['id']}: externe Eingabe {prm['external_input']} fehlt")
    # Kosten: Quelle ↔ Status
    for c in ctx.j("registers/costs.json")["costs"]:
        if c["source"] and c["source"] not in src:
            ph.err(f"{c['id']}: Quelle {c['source']} fehlt")
        if c["status"] in ("BELEGT", "TEILWEISE") and not c["source"]:
            ph.err(f"{c['id']}: Status {c['status']} ohne Quelle")
        if c["status"] == "BELEGT" and c["source"] and src[c["source"]]["status"] != "BELEGT":
            ph.err(f"{c['id']}: BELEGT, Quelle aber {src[c['source']]['status']}")
        if c.get("external_input") and c["external_input"] not in ids["X"]:
            ph.err(f"{c['id']}: externe Eingabe {c['external_input']} fehlt")
    # Instrumente: Tickwert = Multiplikator × Tick; Quelle; Standardverweis
    ins = ctx.j("registers/instruments.json")["instruments"]
    ins_ids = {i["id"] for i in ins}
    for i in ins:
        if Decimal(i["multiplier"]) * Decimal(i["tick_size"]) != Decimal(i["tick_value"]):
            ph.err(f"{i['id']}: Tickwert {i['tick_value']} ≠ Multiplikator × Tick")
        if i["source"] not in src:
            ph.err(f"{i['id']}: Quelle {i['source']} fehlt")
        if i["standard_ref"] and i["standard_ref"] not in ins_ids:
            ph.err(f"{i['id']}: Standardkontrakt {i['standard_ref']} fehlt")
        pr = i["planning"]["price"]
        if pr["status"] in ("BELEGT", "TEILWEISE") and (not pr["source"] or pr["source"] not in src):
            ph.err(f"{i['id']}: belegter Preis ohne gültige Quelle")
        if pr["status"] == "ANNAHME" and pr["source"]:
            ph.err(f"{i['id']}: Preis ANNAHME mit Quellenangabe (widersprüchlich)")
        v = i["planning"]["vol_annual_pct"]
        if not v["low"] <= v["base"] <= v["high"]:
            ph.err(f"{i['id']}: Volatilitätsspanne ungeordnet")
    if len(ins) < 60:
        ph.err(f"Kandidatenliste mit {len(ins)} < 60 Futures (§6.2)")
    # Entscheidungen, Risiken, Modelle, Limits, externe Eingaben: Verweise
    for d in ctx.j("registers/decision_register.json")["decisions"]:
        for ref in d["refs"]:
            if not resolvable(ref, ids, ctx):
                ph.err(f"{d['id']}: unbekannter Verweis {ref}")
        if d["type"] == "BETREIBER" and "operator_answer_verbatim" not in d:
            ph.err(f"{d['id']}: Betreiberentscheidung ohne Wortlaut")
    for lm in ctx.j("registers/limits.json")["limits"]:
        ref = lm["value_ref"]
        if ref.startswith("P-") and not resolvable(ref, ids, ctx):
            ph.err(f"{lm['id']}: Parameter {ref} fehlt")
        if "/" in ref and not ctx.exists(ref.split("#")[0]) and ctx.stage != "e2":
            ph.err(f"{lm['id']}: Datei {ref.split('#')[0]} fehlt")
    xreg = ctx.j("external_inputs.json")
    gate_ids = {g["id"] for g in ctx.j("research/evidence_gates.json")["gates"]} if ctx.exists("research/evidence_gates.json") else None
    for x in xreg["inputs"]:
        for ref in x["refs"]:
            if not resolvable(ref, ids, ctx):
                ph.err(f"{x['id']}: unbekannter Verweis {ref}")
        for tgt in x["blocks"]:
            if tgt.startswith("GATE-") and gate_ids is not None and tgt not in gate_ids:
                ph.err(f"{x['id']}: sperrt unbekanntes Tor {tgt}")
            if not tgt.startswith("GATE-") and tgt not in xreg["block_targets"]:
                ph.err(f"{x['id']}: Sperrziel {tgt} ohne Beschriftung in block_targets")
    for rk in ctx.j("registers/risk_register.json")["risks"]:
        if rk["score"] != rk["likelihood"] * rk["impact"]:
            ph.err(f"{rk['id']}: Score ≠ Wahrscheinlichkeit × Wirkung")
    need = ["Kurslücken", "Margin-Erhöhungen", "Zwangsliquidation", "Korrelationen", "Zinsfutures", "Betreiberverhalten", "Kovarianz"]
    titles = " ".join(r["title"] for r in ctx.j("registers/risk_register.json")["risks"])
    for n in need:
        if n not in titles:
            ph.err(f"Pflichtrisiko §7.11 fehlt: {n}")
    for s in src.values():
        if s["status"] == "NICHT_GEPRUEFT" and s["origin"].startswith("übernommen") is False and s["kind"] not in ("LITERATUR", "ANBIETER", "PRIMAER", "ANBIETERDOKU"):
            ph.warn(f"{s['id']}: NICHT_GEPRUEFT")



# ------------------------------------------------------------------------------------------------------------------------ P05
REF_RE = re.compile(r"\b(?:SRC|DEC|X|COST|INS|RK|MOD|LIM|REQ|KT|GATE|SM|RB|DR|BS|TR|GC|OS|HA|EV|CR5|SC)-[A-Z0-9]+(?:[-_][A-Z0-9]+)*\b|\bT-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}\b"
                    r"|\bP-[A-Z0-9]+(?:-[A-Z0-9{}*]+)+\b")
PATH_RE = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|json|py|csv|txt|sha256|toml))((?:#|::)[^`\s]*)?`")
FUTURE_PREFIXES = ("contract/", "src/")


def ref_universe(ctx) -> dict:
    ids = dict(ctx.ids) if hasattr(ctx, "ids") else id_universe(ctx)
    extra = {"RB": ("operations/runbook_register.json", "runbooks"), "DR": ("operations/drill_register.json", "drills"),
             "BS": ("implementation/build_stages.json", "stages"), "EV": ("registers/resolution_matrix.json", "findings")}
    for k, (rel, key) in extra.items():
        if ctx.exists(rel):
            ids[k] = {x["id"] for x in ctx.j(rel)[key]}
    ids["CR5"] = ids.get("EV", set())
    ids["TR"] = {json.loads(f.read_text(encoding="utf-8"))["id"] for f in (ctx.root / "examples/valid/state_traces").glob("*.json")}
    ids["GC"] = {json.loads(f.read_text(encoding="utf-8"))["id"] for f in (ctx.root / "examples/valid/gate_cases").glob("*.json")}
    scen = ids.get("SC", set())
    ids["OS"] = ids["HA"] = scen
    ids["SC"] = scen
    ids["KT"] = ids.get("T", set())
    return ids


def p05_references(ctx, ph):
    ids = ref_universe(ctx)
    allp = ids["P"]
    n_ids = n_paths = 0
    for f in sorted(list(ctx.root.rglob("*.md")) + list(ctx.root.rglob("*.json"))):
        rel = f.relative_to(ctx.root).as_posix()
        if rel.startswith(("research/sources/", "audit/v2_to_v3_mapping")) or rel in ("PACKAGE_MANIFEST.json", "validation/validation_report.json"):
            continue
        text = f.read_text(encoding="utf-8")
        scan = re.sub(r"aus v2\.0 \([^)]*\)", "aus v2.0", text)          # Kennungen des v2.0-Pakets sind keine v3-Verweise
        if rel.startswith("schemas/"):                                     # reguläre Ausdrücke der Schemas sind keine Verweise
            scan = re.sub(r'"pattern":\s*"(?:[^"\\]|\\.)*"', '"pattern": ""', scan)
        for m in set(REF_RE.findall(scan)):
            n_ids += 1
            kind = m.split("-")[0]
            if kind == "P":
                if "{" in m or "*" in m:                                      # Parametergruppe: {PROFIL} oder * als Platzhalter
                    pattern = re.sub(r"\{[^}]*\}", "*", m)
                    if not any(fnmatch.fnmatchcase(q, pattern) for q in allp):
                        ph.err(f"{rel}: Parametergruppe {m} ohne Parameter")
                elif m not in allp and not any(q.startswith(m + "-") for q in allp):
                    ph.err(f"{rel}: Parameter {m} unbekannt")
                continue
            if kind == "SC" and m.startswith("SC-X-") is False and not m.startswith(("SC-H-", "SC-X-")):
                continue
            pool = ids.get(kind)
            if pool is None:
                continue
            if m not in pool and not any(q.startswith(m + "-") for q in pool):
                ph.err(f"{rel}: Verweis {m} unbekannt")
        if rel.endswith(".md"):
            for m in PATH_RE.finditer(text):
                target, anchor = m.group(1), m.group(2) or ""
                if target.startswith(FUTURE_PREFIXES) or "*" in target or target in ctx.pending:
                    continue
                if target in (MANIFEST, CHECKSUMS) and ctx.stage != "full":        # entstehen erst beim Packen (§19.4)
                    continue
                n_paths += 1
                if not ctx.exists(target):
                    local = (f.parent / target).relative_to(ctx.root).as_posix()
                    if ctx.exists(local):
                        target = local
                    else:
                        ph.err(f"{rel}: Datei {target} fehlt")
                        continue
                if anchor.startswith("::") and target.endswith(".py"):
                    fn = anchor[2:]
                    if not re.search(rf"^\s*def {re.escape(fn)}\(", (ctx.root / target).read_text(encoding="utf-8"), re.M):
                        ph.err(f"{rel}: Funktion {target}{anchor} fehlt")
                elif anchor.startswith("#/") and target.endswith(".json"):
                    try:
                        _pointer(ctx.j(target), anchor[1:])
                    except (KeyError, IndexError, ValueError):
                        ph.err(f"{rel}: JSON-Pointer {target}{anchor} nicht auflösbar")
    # Nachweise im Testkatalog und Quellenregister
    for t in ctx.j("implementation/test_catalog.json")["tests"]:
        ev = t.get("evidence")
        if not ev:
            continue
        target, _, fn = ev.partition("::")
        target = target.split(" ")[0]
        if target in ctx.pending:
            continue
        if not ctx.exists(target):
            ph.err(f"{t['id']}: Nachweisdatei {target} fehlt")
        elif fn and not re.search(rf"^\s*def {re.escape(fn)}\(", (ctx.root / target).read_text(encoding="utf-8"), re.M):
            ph.err(f"{t['id']}: Nachweisfunktion {ev} fehlt")
    for s in ctx.j("registers/source_register.json")["sources"]:
        ev = s["evidence"].split(" ")[0].split("#")[0]
        if ev.startswith(("research/", "registers/", "financials/", "risk/")) and not ctx.exists(ev):
            ph.err(f"{s['id']}: Beleg {ev} fehlt")
    ph.info.append(f"{n_ids} Kennungen, {n_paths} Dateiverweise geprüft")


def _pointer(doc, ptr: str):
    cur = doc
    for part in [x for x in ptr.split("/") if x != ""]:
        part = part.replace("~1", "/").replace("~0", "~")
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur


# ------------------------------------------------------------------------------------------------------------------------ P06
NUM_STRIP = [(re.compile(r"```.*?```", re.S), " "), (re.compile(r"`[^`\n]*`"), " "), (re.compile(r"<!--v:[^>]*-->.*?<!--/v-->", re.S), " "),
             (re.compile(r"<!-- GEN:BEGIN (\S+) -->.*?<!-- GEN:END \1 -->", re.S), " "), (re.compile(r"<!--.*?-->", re.S), " "),
             (re.compile(r"\]\([^)]*\)"), "]"), (re.compile(r"https?://\S+"), " ")]
# Strukturzahlen, die keine Ergebnis- oder Regelwerte sind (Gliederung, Kennungen, Daten, Versionen, Rechtsakte, Formelkonstanten)
NUM_ALLOW = [re.compile(x, re.M) for x in (
    r"^#+\s+\d+(?:\.\d+)*\s", r"^\s*\d+\.\s", r"^\|\s*\d+\s*\|", r"\(\d+\)", r"\bund \d\.\s", r"JSON Schema 2020-12",
    r"\(EU\)\s?(?:Nr\.\s?)?\d+/\d+", r"\b\d+/\d+/E[GU]\b", r"ISO(?:/IEC)?\s?\d+", r"SR 11-7", r"\bRule\s?\d+\w*", r"§\s?\d+(?:\.\d+)*[a-z]?",
    r"\b\d{1,2}\.\d{1,2}\.\d{4}\b", r"\b\d{4}-\d{2}-\d{2}\b", r"\b(?:19|20)\d{2}\b", r"\bv\d+(?:\.\d+)*\b",
    r"\bPython \d+\.\d+(?:\s?(?:bis|–|/|und)\s?\d+\.\d+)*", r"\b3\.1[123]\b", r"SHA-256", r"Ed25519", r"\b(?:L?GPL|Apache)-\d\.\d\b",
    r"\bA\d\.\d\b", r"\bRang\s\d\b", r"\b[A-Z]+\d+(?:-[A-Z0-9]+[a-z]?)+\b", r"\b[A-Z][A-Za-z]*(?:-[A-Z0-9]+[a-z]?)+\b", r"\b[A-Z][A-Z0-9]*-[A-Z0-9_]+\b",
    r"\b[A-Z]{1,4}\d+[A-Za-z]?\b",
    r"\b\d+[A-Z]{1,3}\b", r"\bA\d\.\d\b", r"\b(?:Art\.|Artikel|Nr\.|Rn\.)\s?\d+\w*", r"\bMetaTrader\s?5\b", r"\bJust2Trade\b", r"\b\d+-Year\b",
    r"\bSchritte?\s\d+(?:\s(?:und|bis)\s\d+)?", r"\bAbschnitt\s\d+", r"\bBaustein\s\d+", r"\bStufe\s[12]\b", r"\b[KE]\s?[=≤]\s?\d+\b", r"\bvon 100\b",
    r"max\(0,", r"σ²/2", r"\b\d\s?·\s?S\b", r"(?<![\d,.])[01](?![\d,.%])")]
SUMMARY_EXEMPT = ("README.md", "STATUS.md", "KURZFASSUNG_BETREIBER.md")


def unbound_numbers(text: str) -> list:
    for rx, rep in NUM_STRIP:
        text = rx.sub(rep, text)
    hits = []
    for ln in text.splitlines():
        if ln.lstrip().startswith("|---"):
            continue
        s = ln
        for rx in NUM_ALLOW:
            s = rx.sub(" ", s)
        hits += [(m.group(0), ln.strip()[:140]) for m in re.finditer(r"\d+(?:[.,]\d+)*", s)]
    return hits


ABBREV = ("z. B.", "d. h.", "u. a.", "o. Ä.", "bzw.", "ggf.", "vgl.", "etc.", "Nr.", "ca.", "p. a.", "Mio.", "Tsd.", "Art.", "inkl.", "evtl.", "max.", "min.",
          "sog.", "usw.", "i. d. R.", "Abs.", "S.", "St.")


def count_sentences(text: str) -> int:
    t = re.sub(r"<!--v:[^>]*-->(.*?)<!--/v-->", r"\1", text)
    t = re.sub(r"`[^`]*`", "X", t)
    for a in ABBREV:
        t = t.replace(a, a.replace(".", ""))
    t = re.sub(r"(\d)\.(\d)", r"\1\2", t)
    t = re.sub(r"\b(\d+)\.\s", r"\1 ", t)
    parts = [x for x in re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ„(])", t.strip()) if x.strip()]
    return len(parts)


def summary_problems(rel: str, text: str) -> list:
    """R-12: Hauptdokumente und Hauptkapitel beginnen mit einer Betreiberfassung von höchstens sechs Sätzen."""
    out = []
    if rel == "Masterkonzept_v3.0.md":
        chapters = re.split(r"(?m)^## (?=§)", text)[1:]
        for ch in chapters:
            head = ch.splitlines()[0]
            num = int(re.match(r"§(\d+)", head).group(1))
            if num < 4:
                continue
            body = "\n".join(ch.splitlines()[1:]).lstrip("\n")
            m = re.match(r"> \*\*Betreiberfassung\.\*\*(.*?)(?:\n\n|\Z)", body, re.S)
            if not m:
                out.append(f"§{num}: keine Betreiberfassung am Kapitelanfang")
            elif count_sentences(m.group(1)) > 6:
                out.append(f"§{num}: Betreiberfassung mit {count_sentences(m.group(1))} Sätzen (höchstens sechs)")
        return out
    lines = text.lstrip("\n").splitlines()
    if not lines or not lines[0].startswith("# "):
        return out
    body = "\n".join(lines[1:]).lstrip("\n")
    m = re.match(r"> \*\*Betreiberfassung\.\*\*(.*?)(?:\n\n|\Z)", body, re.S)
    if not m:
        out.append("keine Betreiberfassung nach der Überschrift")
    elif count_sentences(m.group(1)) > 6:
        out.append(f"Betreiberfassung mit {count_sentences(m.group(1))} Sätzen (höchstens sechs)")
    return out


def p06_bindings(ctx, ph):
    sys.path.insert(0, str(ctx.root))
    import contextlib
    import io

    from validation.render_blocks import run as render_run  # noqa: PLC0415
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = render_run(ctx.root, check=True)
    if rc != 0:
        ph.err("render_blocks --check: " + buf.getvalue().strip().splitlines()[-1][:300] if buf.getvalue().strip() else "render_blocks --check fehlgeschlagen")
    n_files = 0
    for f in sorted(ctx.root.rglob("*.md")):
        rel = f.relative_to(ctx.root).as_posix()
        text = f.read_text(encoding="utf-8")
        begins = re.findall(r"<!-- GEN:BEGIN (\S+) -->", text)
        ends = re.findall(r"<!-- GEN:END (\S+) -->", text)
        if begins != ends:
            ph.err(f"{rel}: GEN-Blöcke nicht paarweise")
        if text.count("<!--v:") != text.count("<!--/v-->"):
            ph.err(f"{rel}: Wertmarkierungen nicht paarweise")
        if rel.startswith("research/sources/") or rel in ("STATUS.md",):
            continue
        n_files += 1
        for num, ln in unbound_numbers(text)[:5]:
            ph.err(f"{rel}: ungebundene Zahl {num!r} in „{ln}“ (R-03)")
        if rel not in SUMMARY_EXEMPT and not rel.startswith("governance/policies/"):
            for s in summary_problems(rel, text):
                ph.err(f"{rel}: {s} (R-12)")
    ph.info.append(f"{n_files} Markdown-Dateien auf ungebundene Zahlen und Betreiberfassungen geprüft")


# ------------------------------------------------------------------------------------------------------------------------ P07
RESULT_FILES = ["research/turnover_results.json", "financials/cost_model_results.json", "research/prior_results.json", "risk/leverage_results.json",
                "risk/stress_results.json", "risk/kelly_ruin_results.json", "research/statistical_results.json",
                "research/operating_characteristics_results.json", "operations/costdrift_results.json", "financials/tax_sensitivity_example.json",
                "financials/decision_montecarlo_results.json"]


def p07_calculators(ctx, ph):
    sys.path.insert(0, str(ctx.root))
    import importlib  # noqa: PLC0415
    calc = importlib.import_module("lib.calc")
    calc.ROOT = ctx.root                       # Inhalts-Hashes gegen das geprüfte Paket
    for rel in RESULT_FILES:
        if not ctx.exists(rel):
            ph.err(f"Ergebnisdatei fehlt: {rel}")
            continue
        for inp, h in ctx.j(rel).get("inputs", {}).items():
            if not ctx.exists(inp):
                ph.err(f"{rel}: Eingabe {inp} fehlt")
            elif calc.sha256_content(inp) != h:
                ph.err(f"{rel}: Eingabe {inp} seit der Rechnung geändert (Eingangs-Hash; Rechner neu laufen lassen)")
    if ctx.calc_mode == "hash":
        ph.info.append("nur Eingangs-Hashes geprüft (--calc-mode hash)")
        return
    r = ctx.run(["validation/run_calculators.py", "--check"])
    last = (r.stdout.strip().splitlines() or [""])[-1]
    if r.returncode != 0:
        ph.err(f"run_calculators --check: {last[:300]}")
    ph.info.append(last)


# ------------------------------------------------------------------------------------------------------------------------ P08
def registry(ctx):
    from referencing import Registry, Resource  # noqa: PLC0415
    res = []
    for f in sorted((ctx.root / "schemas").glob("*.schema.json")):
        sc = ctx.j(f.relative_to(ctx.root).as_posix())
        res.append((sc["$id"], Resource.from_contents(sc)))
    return Registry().with_resources(res)


def p08_examples(ctx, ph):
    import jsonschema  # noqa: PLC0415
    sys.path.insert(0, str(ctx.root))
    from validation import example_rules, gate_engine, state_engine  # noqa: PLC0415
    reg = registry(ctx)
    P = example_rules.load_params(ctx.root)
    idx = ctx.j("examples/EXAMPLES.json")["examples"]
    listed = {e["file"] for e in idx}
    on_disk = {f.relative_to(ctx.root).as_posix() for sub in ("examples/valid/contracts", "examples/invalid") for f in (ctx.root / sub).glob("*.json")}
    for f in sorted(on_disk - listed):
        ph.err(f"Beispiel ohne Eintrag in examples/EXAMPLES.json: {f}")
    for f in sorted(listed - on_disk):
        ph.err(f"Eintrag ohne Beispieldatei: {f}")
    n_ok = 0
    for e in idx:
        if e["file"] not in on_disk:
            continue
        doc = ctx.j(e["file"])
        sc = ctx.j(f"schemas/{e['schema']}.schema.json")
        errs = list(jsonschema.Draft202012Validator(sc, registry=reg, format_checker=jsonschema.FormatChecker()).iter_errors(doc))
        viol = example_rules.violations(e["schema"], doc, P)
        exp = e.get("expected") or {}
        if e["valid"]:
            ok = not errs and not viol
        elif exp.get("type") == "SCHEMA":
            ok = bool(errs)
        else:
            ok = not errs and exp.get("rule") in viol
        if ok:
            n_ok += 1
        else:
            ph.err(f"{e['file']}: Erwartung verfehlt (Schemafehler {len(errs)}, Regeln {viol}, erwartet {exp or 'gültig'})")
    g = gate_engine.run_all(ctx.root)
    if not g["passed"]:
        ph.err(f"gate_engine: {len(g['static_errors'])} statische Fehler, {sum(1 for c in g['cases'] if not c['passed'])} Fälle abweichend, "
               f"ungedeckt {g['uncovered_rules'][:5]}")
    s = state_engine.run_all(ctx.root)
    if not s["passed"]:
        ph.err(f"state_engine: {len(s['static_errors'])} statische Fehler, {sum(1 for x in s['traces'] if not x['passed'])} Traces abweichend")
    ctx.results["P08"] = {"examples_ok": n_ok, "gate_cases": len(g["cases"]), "traces": len(s["traces"]), "gate_passed": g["passed"], "state_passed": s["passed"]}
    ph.info.append(f"{n_ok}/{len(idx)} Beispiele wie erwartet; {len(g['cases'])} Torfälle; {len(s['traces'])} Traces")


# ------------------------------------------------------------------------------------------------------------------------ P09
def p09_semantics(ctx, ph):
    sys.path.insert(0, str(ctx.root))
    from validation import semantic_checks  # noqa: PLC0415
    res = semantic_checks.run_all(ctx.root)
    ctx.results["P09"] = {k: not v for k, v in res.items()}
    for name, errs in res.items():
        if name == "check_scores":          # Selbstbewertung prüft P12
            continue
        for e in errs[:10]:
            ph.err(f"{name}: {e}")
    ph.info.append(f"{sum(1 for v in res.values() if not v)}/{len(res)} semantische Prüfungen bestanden")


# ------------------------------------------------------------------------------------------------------------------------ P10
def p10_reference_tests(ctx, ph):
    r = ctx.run(["validation/test_reference_models.py", "-v"])
    out = r.stdout + r.stderr
    passed = sorted(set(re.findall(r"^(test_\w+) \(.*?\) \.\.\. (?:.*\n)?ok$", out, re.M)))
    failed = sorted(set(re.findall(r"^(test_\w+) \(.*?\) \.\.\. (?:FAIL|ERROR)", out, re.M)))
    ctx.results["P10"] = {"passed": passed, "failed": failed}
    if r.returncode != 0 or failed:
        ph.err(f"Referenztests: {len(failed)} fehlgeschlagen {failed[:8]}; {out.strip().splitlines()[-1][:200] if out.strip() else ''}")
    ph.info.append(f"{len(passed)} Referenztests bestanden")


# ------------------------------------------------------------------------------------------------------------------------ P11
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME|XXX+|Lorem ipsum)\b|<PLATZHALTER>|\?\?\?")
SECRET_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bsk-[A-Za-z0-9]{20,}\b"
                       r"|(?i:\b(?:password|passwort|api[_-]?key|secret|token)\s*[:=]\s*[\"']?[A-Za-z0-9/+_-]{12,})")
MAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
MAIL_OK = re.compile(r"(?:^|\.)(?:example\.(?:com|org|net)|invalid|test|example|localhost)$")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}\b")
PHONE_RE = re.compile(r"(?<![\w-])\+?\d{2,4}[ /-]\d{3,4}[ /-]\d{3,8}\b")
ABS_PATH_RE = re.compile(r"(?:/home/|/root/|/tmp/|/mnt/|[A-Z]:\\\\Users\\\\|/Users/)")
ALLOWED_EXT = {".md", ".json", ".py", ".csv", ".txt", ".sha256", ".toml"}


def p11_hygiene(ctx, ph):
    for f in sorted(ctx.root.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(ctx.root).as_posix()
        if f.suffix not in ALLOWED_EXT:
            ph.err(f"unzulässige Dateiendung: {rel}")
            continue
        text = f.read_text(encoding="utf-8")
        own = rel == "validation/validate_package.py"
        for m in PLACEHOLDER_RE.finditer(text):
            if not own:
                ph.err(f"{rel}: Platzhalter {m.group(0)!r}")
                break
        for m in SECRET_RE.finditer(text):
            if not own:
                ph.err(f"{rel}: mögliches Geheimnis {m.group(0)[:24]!r}")
                break
        for m in MAIL_RE.finditer(text):
            if not MAIL_OK.search(m.group(1).lower()):
                ph.err(f"{rel}: E-Mail-Adresse {m.group(0)!r} (R-13)")
                break
        plain = re.sub(r"https?://\S+", " ", text)
        for rx, what in ((IBAN_RE, "Kontonummer (IBAN)"), (PHONE_RE, "Telefonnummer")):
            m = rx.search(plain)
            if m and not own and not rel.startswith(("research/sources/", "examples/")):
                ph.err(f"{rel}: mögliche {what} {m.group(0)!r}")
        if ABS_PATH_RE.search(text) and not own:
            ph.err(f"{rel}: absoluter lokaler Pfad")


# ------------------------------------------------------------------------------------------------------------------------ P12
K_GRID = {"A1": 5, "A2": 4, "A3": 5, "A4": 3, "A5": 3, "B1": 4, "B2": 4, "B3": 4, "B4": 3, "C1": 3, "C2": 4, "C3": 3, "D1": 3, "D2": 3, "D3": 2, "D4": 2,
          "E1": 3, "E2": 3, "E3": 2, "E4": 2, "F1": 3, "F2": 3, "F3": 2, "F4": 2, "G1": 3, "G2": 3, "G3": 2, "H1": 2, "H2": 2, "H3": 1, "I1": 3, "I2": 2,
          "I3": 2, "J1": 2, "J2": 2, "J3": 1}
E_GRID = {"E-1": 10, "E-2": 10, "E-3": 10, "E-4": 10, "E-5": 15, "E-6": 10, "E-7": 10, "E-8": 10, "E-9": 15}


def p12_scores(ctx, ph):
    if not (ctx.exists("audit/scorecard_K.json") and ctx.exists("audit/scorecard_E.json")):
        ph.err("Scorecards K und E fehlen")
        return
    K, E = ctx.j("audit/scorecard_K.json"), ctx.j("audit/scorecard_E.json")
    got = {s["id"]: s["max"] for s in K["subcriteria"]}
    if got != K_GRID:
        ph.err(f"Raster K weicht von §20.1 ab: {sorted(set(got.items()) ^ set(K_GRID.items()))[:6]}")
    gotE = {b["id"]: b["max"] for b in E["blocks"]}
    if gotE != E_GRID:
        ph.err(f"Raster E weicht von §20.3 ab: {sorted(set(gotE.items()) ^ set(E_GRID.items()))[:6]}")
    if K.get("self_assessment") is not True or E.get("self_assessment") is not True:
        ph.err("Scorecards nicht als Selbstbewertung gekennzeichnet (R-08)")
    sys.path.insert(0, str(ctx.root))
    from validation import semantic_checks  # noqa: PLC0415
    for e in semantic_checks.check_scores(semantic_checks.Pkg(ctx.root)):
        ph.err(e)
    mp = ctx.j("audit/v2_to_v3_mapping.json")
    for c in mp["criteria_mapping"]:
        for k in c["k_subcriteria"]:
            if k not in K_GRID:
                ph.err(f"Abbildung v2 {c['v2']}: Unterkriterium {k} unbekannt")


# ------------------------------------------------------------------------------------------------------------------------ P13
def p13_status_truth(ctx, ph):
    tests = ctx.j("implementation/test_catalog.json")["tests"]
    tmap = {t["id"]: t for t in tests}
    sem = ctx.results.get("P09", {})
    ref = ctx.results.get("P10", {})
    p08 = ctx.results.get("P08", {})
    for t in tests:
        if t["execution"] != "IM_PAKET":
            if t["status"] != "SPEZIFIZIERT":
                ph.err(f"{t['id']}: Status {t['status']} ohne Ausführung im Paket")
            continue
        ev = t.get("evidence", "")
        target, _, fn = ev.partition("::")
        target = target.split(" ")[0]
        if target in ctx.pending:
            continue
        if target == "validation/semantic_checks.py":
            if sem and not sem.get(fn):
                ph.err(f"{t['id']}: {fn} nicht bestanden, Status {t['status']}")
        elif target == "validation/test_reference_models.py":
            if ref and fn not in ref.get("passed", []):
                ph.err(f"{t['id']}: Referenztest {fn} nicht bestanden oder nicht ausgeführt")
        elif target == "validation/gate_engine.py":
            if p08 and not p08.get("gate_passed"):
                ph.err(f"{t['id']}: gate_engine nicht bestanden")
        elif target == "validation/state_engine.py":
            if p08 and not p08.get("state_passed"):
                ph.err(f"{t['id']}: state_engine nicht bestanden")
        elif target == "validation/execution_log.txt":
            log = (ctx.root / target).read_text(encoding="utf-8") if ctx.exists(target) else ""
            for v in ("3.11", "3.12", "3.13"):
                if not re.search(rf"^PYTHON {re.escape(v)}\S* .*ERGEBNIS PASS", log, re.M):
                    ph.err(f"{t['id']}: kein bestandener Lauf unter Python {v} in {target}")
            m = re.search(r"^PAKETSTAND ([0-9a-f]{64})$", log, re.M)
            if log and (not m or m.group(1) != package_state(ctx)):
                ph.err(f"{t['id']}: {target} gehört zu einem anderen Paketstand (Mehrversionslauf wiederholen)")
        elif target == "validation/mutation_tests.py":
            rep = "validation/mutation_report.json"
            if rep in ctx.pending:
                continue
            if not ctx.exists(rep):
                ph.err(f"{t['id']}: {rep} fehlt")
            else:
                m = ctx.j(rep)
                if m.get("result") != "PASS" or m.get("detected", 0) < 40 or m.get("detected") != m.get("total"):
                    ph.err(f"{t['id']}: Mutationstests nicht vollständig erkannt ({m.get('detected')}/{m.get('total')})")
                if m.get("package_state") != package_state(ctx):
                    ph.err(f"{t['id']}: {rep} gehört zu einem anderen Paketstand (Mutationslauf wiederholen)")
        elif not ctx.exists(target):
            ph.err(f"{t['id']}: Nachweis {target} fehlt")
    for r in ctx.j("requirements.json")["requirements"]:
        ex = {tmap[t]["execution"] for t in r["tests"] if t in tmap}
        want = "IM_PAKET_NACHGEWIESEN" if ex == {"IM_PAKET"} else ("TEILWEISE_NACHGEWIESEN" if "IM_PAKET" in ex else "SPEZIFIZIERT")
        if r["status"] != want:
            ph.err(f"{r['id']}: Status {r['status']}, aus den Tests folgt {want}")
    ids = ref_universe(ctx)
    for f in ctx.j("registers/resolution_matrix.json")["findings"]:
        for ev in f["evidence"]:
            head = ev.split(" ")[0].split("#")[0].split("::")[0]
            if "/" in head or head.endswith((".json", ".md", ".py")):
                if not ctx.exists(head) and head not in ctx.pending:
                    ph.err(f"{f['id']}: Nachweis {head} fehlt")
            else:
                kind = head.split("-")[0]
                if kind in ids and head not in ids[kind] and not any(q.startswith(head + "-") for q in ids[kind]):
                    ph.err(f"{f['id']}: Nachweis {head} unbekannt")
        if f["status"] == "OFFEN_EXTERN" and not re.search(r"X-[A-Z]", json.dumps(f, ensure_ascii=False)):
            ph.err(f"{f['id']}: OFFEN_EXTERN ohne externe Eingabe")
    src = ctx.j("registers/source_register.json")["sources"]
    for s in src:
        if s["status"] == "BELEGT" and not s["evidence"]:
            ph.err(f"{s['id']}: BELEGT ohne Beleg")
    if ctx.exists("KURZFASSUNG_BETREIBER.md"):
        kf = (ctx.root / "KURZFASSUNG_BETREIBER.md").read_text(encoding="utf-8")
        words = len(re.findall(r"\w+", re.sub(r"<!--.*?-->", " ", kf, flags=re.S)))
        if words > 1100:
            ph.err(f"KURZFASSUNG_BETREIBER.md mit {words} Wörtern länger als zwei Seiten (§18)")
        if "GEN:BEGIN tab.gonogo" not in kf:
            ph.err("KURZFASSUNG_BETREIBER.md ohne Go/No-Go-Tabelle aus der Entscheidungsrechnung")
    vr = "validation/validation_report.json"
    if ctx.exists(vr) and vr not in ctx.pending:
        v = ctx.j(vr)
        if v.get("result") != "PASS":
            ph.err(f"{vr}: Prüfung vor dem Packen nicht bestanden ({v.get('result')})")
        if v.get("package_state") != package_state(ctx):
            ph.err(f"{vr} gehört zu einem anderen Paketstand (Prüfung vor dem Packen wiederholen)")
    gng = ctx.j("financials/decision_montecarlo_results.json")["go_no_go"]
    lev = ctx.j("risk/leverage_results.json")["cells"]["U-KOSTEN"]
    for st, profs in gng.items():
        for prof, g in profs.items():
            if g["decision_real_money"] != "NO_GO" and not lev[st][prof].get("admissible"):
                ph.err(f"Go/No-Go {st}/{prof} widerspricht der Profilzulässigkeit")


# ------------------------------------------------------------------------------------------------------------------------ P14
def p14_manifest(ctx, ph):
    if ctx.stage != "full":
        ph.status = "SKIPPED"
        ph.info.append("nur in Stufe full")
        return
    man = ctx.j(MANIFEST)
    files = {f["path"]: f for f in man["files"]}
    on_disk = {f.relative_to(ctx.root).as_posix() for f in ctx.root.rglob("*") if f.is_file()} - {MANIFEST, CHECKSUMS}
    for rel in sorted(on_disk - set(files)):
        ph.err(f"Datei nicht im Manifest: {rel}")
    for rel in sorted(set(files) - on_disk):
        ph.err(f"Manifesteintrag ohne Datei: {rel}")
    for rel in sorted(on_disk & set(files)):
        p = ctx.root / rel
        if files[rel]["sha256"] != sha256(p) or files[rel]["bytes"] != p.stat().st_size:
            ph.err(f"Manifest: Hash oder Größe weicht ab: {rel}")
    lines = (ctx.root / CHECKSUMS).read_text(encoding="utf-8").splitlines()
    seen = set()
    for ln in lines:
        m = re.fullmatch(r"([0-9a-f]{64})  (.+)", ln)
        if not m:
            ph.err(f"CHECKSUMS.sha256: ungültige Zeile {ln[:80]!r}")
            continue
        h, rel = m.groups()
        seen.add(rel)
        if not ctx.exists(rel) or sha256(ctx.root / rel) != h:
            ph.err(f"CHECKSUMS.sha256: {rel} weicht ab")
    want = (on_disk | {MANIFEST})
    if seen != want:
        ph.err(f"CHECKSUMS.sha256 deckt nicht genau alle Dateien ab: {sorted(want ^ seen)[:6]}")


PHASES = [("P01", "Struktur", p01_structure), ("P02", "JSON-Syntax", p02_json), ("P03", "Schemas", p03_schemas),
          ("P04", "Registersemantik und Querverweise", p04_registers), ("P05", "Verweise im Text", p05_references),
          ("P06", "Bindungen, Zahlen und Betreiberfassungen", p06_bindings), ("P07", "Referenzrechner", p07_calculators),
          ("P08", "Beispiele, Torfälle, Zustandstraces", p08_examples), ("P09", "Semantische Querprüfungen", p09_semantics),
          ("P10", "Referenztests", p10_reference_tests), ("P11", "Hygiene", p11_hygiene), ("P12", "Selbstbewertung K und E", p12_scores),
          ("P13", "Statuswahrheit", p13_status_truth), ("P14", "Manifest und Prüfsummen", p14_manifest)]


def package_state(ctx) -> str:
    if not hasattr(ctx, "state"):
        sys.path.insert(0, str(ctx.root))
        from lib.pkgstate import state_hash  # noqa: PLC0415
        ctx.state = state_hash(ctx.root)
    return ctx.state


def validate(root: Path, strict: bool, stage: str, only=None, calc_mode: str = "full", pending=()) -> dict:
    ctx = Ctx(root, strict, stage, calc_mode, pending)
    phases = []
    for pid, title, fn in PHASES:
        ph = Phase(pid, title)
        if only and pid not in only:
            ph.status = "SKIPPED"
            phases.append(ph)
            continue
        t0 = time.time()
        try:
            if pid in ("P05", "P13") and not hasattr(ctx, "ids"):
                ctx.ids = id_universe(ctx)
            fn(ctx, ph)
        except Exception as ex:  # noqa: BLE001 – jede Ausnahme ist ein Prüffehler
            ph.err(f"Ausnahme: {ex.__class__.__name__}: {ex}")
        ph.secs = time.time() - t0
        if ph.errors:
            ph.status = "FAIL"
        elif ph.status != "SKIPPED" and ph.warnings and strict:
            ph.status = "PASS_MIT_HINWEISEN"
        phases.append(ph)
    ok = all(p.status in ("PASS", "PASS_MIT_HINWEISEN", "SKIPPED") for p in phases)
    return {"package": PKG_NAME, "stage": stage, "strict": strict, "calc_mode": calc_mode, "result": "PASS" if ok else "FAIL",
            "package_state": package_state(ctx), "pending_evidence": sorted(ctx.pending), "phases_run": sorted(only) if only else "alle",
            "generated_utc": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "environment": {"python": platform.python_version(), "platform": platform.system()},
            "phases": [{"id": p.id, "title": p.title, "status": p.status, "errors": p.errors, "warnings": p.warnings, "info": p.info,
                        "seconds": round(p.secs, 2)} for p in phases]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--stage", default="prepack", choices=["e2", "prepack", "full"])
    ap.add_argument("--only", default="")
    ap.add_argument("--calc-mode", default="full", choices=["full", "hash"])
    ap.add_argument("--report-out", default="")
    ap.add_argument("--pending-evidence", default="", help="Laufbelege, die im laufenden Belegzyklus erst entstehen (kommagetrennt)")
    a = ap.parse_args(argv)
    only = set(x for x in a.only.split(",") if x) or None
    root = Path(a.root).resolve()
    pending = {x for x in a.pending_evidence.split(",") if x}
    if a.report_out:
        out = Path(a.report_out).resolve()
        if out.is_relative_to(root):
            pending.add(out.relative_to(root).as_posix())            # der eigene Bericht entsteht erst mit diesem Lauf
    unknown = pending - {"validation/execution_log.txt", "validation/mutation_report.json", "validation/validation_report.json"}
    if unknown:
        ap.error(f"--pending-evidence nur für Laufbelege zulässig, nicht für {sorted(unknown)}")
    if a.stage == "full" and pending:
        ap.error("Stufe full prüft alle Laufbelege; --pending-evidence und ein Bericht im Paket sind dort nicht zulässig")
    rep = validate(root, a.strict, a.stage, only, a.calc_mode, pending)
    for p in rep["phases"]:
        print(f"{p['id']} {p['status']:<18} {p['title']} ({len(p['errors'])} Fehler, {len(p['warnings'])} Hinweise) {p['seconds']:.1f}s")
        for e in p["errors"][:30]:
            print(f"    FEHLER  {e}")
        for w in p["warnings"][:10]:
            print(f"    HINWEIS {w}")
    if pending:
        print("LAUFBELEGE IM ZYKLUS", ", ".join(sorted(pending)))
    print("PAKETSTAND", rep["package_state"])
    print("ERGEBNIS", rep["result"])
    if a.report_out:
        Path(a.report_out).write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if rep["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
