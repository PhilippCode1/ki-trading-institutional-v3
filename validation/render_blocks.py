#!/usr/bin/env python3
"""Bindet Zahlen und Tabellen der Markdown-Dateien an Rechnerergebnisse und Register (R-03; Technik übernommen aus v2.0, erweitert).

Markierungen im Text:
  Einzelwert:  <!--v:QUELLE:PFAD|FORMAT-->wert<!--/v-->      z. B. <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v-->
  Tabelle:     <!-- GEN:BEGIN name --> … <!-- GEN:END name -->
Quellen: param, costreg, ins, x (externe Eingaben), cost, costsym (Kostenmodell je Symbol), turn, prior, lev, stress, kelly, stat, oc, drift,
dmc, stagecost, build, stressreg, tax, src, calc.
Formate: d0–d4, pct0–pct2 (Anteil → %), pp0–pp2 (Wert in %), eur, eur2, teur, mio, mio1, mio2, x0–x2, int, raw.

Außerdem erzeugt das Werkzeug abgeleitete Register: registers/traceability.json und die Felder used_in in registers/source_register.json
und parameters.json.
Aufruf: python validation/render_blocks.py --root . [--check]      (--check: nur prüfen, Exitcode 1 bei Abweichung)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.calc import margin_loss_to_level  # noqa: E402
from lib.pkgstate import EVIDENCE_FILES  # noqa: E402

VALUE_RE = re.compile(r"<!--v:([^>]+?)-->(.*?)<!--/v-->", re.S)
BLOCK_RE = re.compile(r"(<!-- GEN:BEGIN ([A-Za-z0-9_.:-]+) -->\n)(.*?)(<!-- GEN:END \2 -->)", re.S)
ID_RE = re.compile(r"\b(?:SRC|DEC|P|X|COST|INS|RK|MOD|LIM|REQ|T|KT|GATE|SM|SC|EV|CR5|BS|PTC|RB|DR)-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
RESULTS = {"cost": "financials/cost_model_results.json", "turn": "research/turnover_results.json", "prior": "research/prior_results.json",
           "lev": "risk/leverage_results.json", "stress": "risk/stress_results.json", "kelly": "risk/kelly_ruin_results.json",
           "stat": "research/statistical_results.json", "oc": "research/operating_characteristics_results.json", "drift": "operations/costdrift_results.json",
           "mon": "operations/monitor_results.json",
           "dmc": "financials/decision_montecarlo_results.json", "build": "implementation/build_stages.json", "stressreg": "risk/stress_scenarios.json",
           "tax": "financials/tax_sensitivity_example.json", "r1": "research/sources/R1_mt5_brokers.json", "r4": "research/sources/R4_stress_scenarios.json",
           "r5": "research/sources/R5_data_index_hermes.json", "rb": "operations/runbook_register.json", "dr": "operations/drill_register.json",
           "v2map": "audit/v2_to_v3_mapping.json"}
DERIVED = {"registers/traceability.json", *EVIDENCE_FILES}          # abgeleitet oder Laufbeleg: zählt nie als Verwendung einer Kennung


# ------------------------------------------------------------------------------------------------ Formatierung (deutsch)
def de(x, nd=2) -> str:
    s = f"{float(x):,.{nd}f}"
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")
    return "0" + s[2:] if s.startswith("-0") and float(x) == 0 else s


def fmt(v, f: str) -> str:
    if f == "raw":
        return str(v)
    if f in ("chain", "list"):
        if not isinstance(v, list):
            raise ValueError(f"Format {f} verlangt eine Liste")
        return (" → " if f == "chain" else ", ").join(str(x) for x in v)
    if v is None:
        return "–"
    if f == "int":
        return de(round(float(v)), 0)
    m = re.fullmatch(r"(d|pct|pp|x)(\d)", f)
    if m:
        kind, nd = m.group(1), int(m.group(2))
        if kind == "d":
            return de(v, nd)
        if kind == "pct":
            return de(float(v) * 100, nd) + " %"
        if kind == "pp":
            return de(v, nd) + " %"
        return de(v, nd) + "×"
    if f == "eur":
        return de(round(float(v)), 0) + " EUR"
    if f == "eur2":
        return de(v, 2) + " EUR"
    if f == "teur":
        return de(float(v) / 1000, 0) + " Tsd. EUR"
    if f == "mio1":
        return de(float(v) / 1e6, 1) + " Mio. EUR"
    if f == "mio2":
        return de(float(v) / 1e6, 2) + " Mio. EUR"
    if f == "mio":
        s = de(float(v) / 1e6, 2)
        return (s.rstrip("0").rstrip(",") if "," in s else s) + " Mio. EUR"
    raise ValueError(f"unbekanntes Format {f}")


def md_table(header, rows) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in r) + " |")
    return "\n".join(out)


# ------------------------------------------------------------------------------------------------ Daten
class Data:
    def __init__(self, root: Path):
        self.root = root
        self.cache = {}

    def j(self, rel):
        if rel not in self.cache:
            self.cache[rel] = json.loads((self.root / rel).read_text(encoding="utf-8"))
        return self.cache[rel]

    @property
    def params(self):
        return {p["id"]: p for p in self.j("parameters.json")["parameters"]}

    @property
    def costreg(self):
        return {c["id"]: c for c in self.j("registers/costs.json")["costs"]}

    @property
    def ins(self):
        return {i["id"]: i for i in self.j("registers/instruments.json")["instruments"]}

    @property
    def xin(self):
        return {x["id"]: x for x in self.j("external_inputs.json")["inputs"]}

    @property
    def sources(self):
        return {s["id"]: s for s in self.j("registers/source_register.json")["sources"]}


PROFILES = ["H5", "H10", "H15", "H20"]


def walk(obj, path: str):
    for part in [p for p in path.split("/") if p != ""]:
        if isinstance(obj, list):
            obj = obj[int(part)]
        else:
            obj = obj[part]
    return obj


def calc(d: Data, name: str):
    """Abgeleitete Kennzahlen, die sich nicht als einzelner Pfad lesen lassen."""
    if name == "hold_max_days":
        return d.params["P-OP-HOLD-MAX-H"]["value"] / 24
    if name == "hold_std_max_days":
        return d.params["P-OP-HOLD-STD-MAX-H"]["value"] / 24
    if name == "gap_budget":
        return d.params["P-OP-DAILY-LOSS-CAP"]["value"] - d.params["P-RISK-GAP-RESERVE"]["value"]
    if name == "operator_hours_per_week":
        return d.j("financials/decision_montecarlo_results.json")["operator_hours_per_year"] / 52
    if name == "rate_share_H10":
        return d.j("risk/leverage_results.json")["leverage_calibration_via_rates"][str(d.params["P-RISK-STRESS-REF-STAGE"]["value"])]["H10"]["rate_risk_share"]
    if name == "rate_share_H20":
        return d.j("risk/leverage_results.json")["leverage_calibration_via_rates"][str(d.params["P-RISK-STRESS-REF-STAGE"]["value"])]["H20"]["rate_risk_share"]
    if name == "gap_H10":
        return d.j("risk/leverage_results.json")["leverage_calibration_via_rates"][str(d.params["P-RISK-STRESS-REF-STAGE"]["value"])]["H10"]["gap_loss_design"]
    if name == "gap_H20":
        return d.j("risk/leverage_results.json")["leverage_calibration_via_rates"][str(d.params["P-RISK-STRESS-REF-STAGE"]["value"])]["H20"]["gap_loss_design"]
    if name == "max_Lg_admissible_operator_rules":
        cells = d.j("risk/leverage_results.json")["cells"]
        return max((c.get("L_g_achieved", 0.0) for v in ("U-KOSTEN", "U-BREAKEVEN", "U-KOSTEN-TFD1-7T") for st in cells[v].values() for c in st.values()),
                   default=0.0)
    if name == "sources_total":
        return len(d.sources)
    if name.startswith("sources_status_"):
        return sum(1 for s in d.sources.values() if s["status"] == name.split("_")[-1])
    if name == "instruments_total":
        return len(d.ins)
    if name == "instruments_access_primary":
        return sum(1 for i in d.ins.values() if i["access"]["status"].startswith("PRIMAER") and not i["blocked"])
    if name == "index_candidates":
        return len(d.j("registers/instruments.json")["equity_index_candidates"])
    if name == "parameters_total":
        return len(d.params)
    if name == "external_inputs_total":
        return len(d.xin)
    if name == "decisions_total":
        return len(d.j("registers/decision_register.json")["decisions"])
    if name == "conflicts_total":
        return sum(1 for x in d.j("registers/decision_register.json")["decisions"] if x["type"] == "KONFLIKT")
    if name == "risks_total":
        return len(d.j("registers/risk_register.json")["risks"])
    if name == "admissible_cells_registered":
        t = d.j("financials/decision_montecarlo_results.json")["table"]["U-KOSTEN"]
        return sum(1 for st in t.values() for c in st.values() if c["class"] in ("VIABLE", "MARGINAL"))
    if name == "stress_scenarios_total":
        s = d.j("risk/stress_scenarios.json")
        return len(s["historical"]) + len(s["hypothetical"])
    if name == "build_agent_days_base":
        return sum(s["effort"]["base"]["agent_days"] for s in d.j("implementation/build_stages.json")["stages"])
    if name == "build_person_days_base":
        return sum(s["effort"]["base"]["person_days"] for s in d.j("implementation/build_stages.json")["stages"])
    if name == "build_agent_days_low":
        return sum(s["effort"]["low"]["agent_days"] for s in d.j("implementation/build_stages.json")["stages"])
    if name == "build_agent_days_high":
        return sum(s["effort"]["high"]["agent_days"] for s in d.j("implementation/build_stages.json")["stages"])
    if name == "build_person_days_low":
        return sum(s["effort"]["low"]["person_days"] for s in d.j("implementation/build_stages.json")["stages"])
    if name == "build_person_days_high":
        return sum(s["effort"]["high"]["person_days"] for s in d.j("implementation/build_stages.json")["stages"])
    if name == "min_instruments_registered":
        t = d.j("research/prior_results.json")["admission"]["U-KOSTEN"]
        return min(v["n"] for v in t.values())
    if name == "max_instruments_registered":
        t = d.j("research/prior_results.json")["admission"]["U-KOSTEN"]
        return max(v["n"] for v in t.values())
    if name == "max_instruments_breakeven":
        t = d.j("research/prior_results.json")["admission"]["U-BREAKEVEN"]
        return max(v["n"] for v in t.values())
    if name == "max_instruments_tfd1":
        t = d.j("research/prior_results.json")["admission"]["U-KOSTEN-TFD1"]
        return max(v["n"] for v in t.values())
    if name == "max_instruments_tfd1_7t":
        t = d.j("research/prior_results.json")["admission"]["U-KOSTEN-TFD1-7T"]
        return max(v["n"] for v in t.values())
    if name.startswith("mdd_eur/"):
        _, prof, kind, years, q = name.split("/")
        r = d.j("risk/kelly_ruin_results.json")["results"][prof][kind]
        return r["max_drawdown"][years][q] * d.params["P-RISK-STRESS-REF-STAGE"]["value"]
    if name.startswith("stress_eur/"):
        _, kind, prof = name.split("/")
        return d.j("risk/stress_results.json")["results"][kind][prof]["worst_loss_with_ladder"] * d.params["P-RISK-STRESS-REF-STAGE"]["value"]
    if name == "eurex_full_history_cost_eur":
        c, p = d.costreg, d.params
        months = 12 * (p["P-RES-DEV-YEARS"]["value"] + p["P-RES-HOLDOUT-YEARS"]["value"])
        usd = float(c["COST-HIST-CQG-MIN"]["amount"]) * months * float(c["COST-HIST-EUREX-MARKETS"]["amount"])
        return usd / p["P-ECO-EURUSD"]["value"]
    if name == "models_total":
        return len(d.j("registers/model_inventory.json")["models"])
    if name == "ai_maintenance_hours_year":
        return (365 // d.params["P-AI-UPDATE-MIN-DAYS"]["value"]) * d.params["P-AI-UPDATE-EFFORT-H"]["value"]
    if name == "runbooks_total":
        return len(d.j("operations/runbook_register.json")["runbooks"])
    if name == "drills_total":
        return len(d.j("operations/drill_register.json")["drills"])
    if name == "dl_gap_l3":
        return d.params["P-OP-DAILY-LOSS-CAP"]["value"] - d.params["P-RISK-DL-L3"]["value"]
    if name == "history_excluded_count":
        return len(d.j("research/prior_results.json")["admission_rule"]["history_excluded"])
    if name == "history_excluded_symbols":
        return ", ".join(d.ins[i]["symbol"] for i in d.j("research/prior_results.json")["admission_rule"]["history_excluded"])
    if name == "calib_research_feasible":
        cal = d.j("risk/leverage_results.json")["leverage_calibration_research_admissible"]
        return sum(1 for st in cal.values() for c in st.values() if c.get("feasible"))
    if name.startswith("stress_worst_name/"):
        _, kind, prof = name.split("/")
        sid = d.j("risk/stress_results.json")["results"][kind][prof]["worst_scenario"]
        reg = d.j("risk/stress_scenarios.json")
        return next(s["name"] for s in reg["historical"] + reg["hypothetical"] if s["id"] == sid)
    if name.startswith("stress_breaches/"):
        _, kind, prof = name.split("/")
        return len(d.j("risk/stress_results.json")["results"][kind][prof]["daily_cap_breaches"])
    if name == "cash_drag_ref":
        p = d.params
        return p["P-ECO-CASH-AT-BROKER"]["value"] * (p["P-ECO-CASH-RATE"]["value"] - p["P-ECO-BROKER-RATE"]["value"]) * p["P-RISK-STRESS-REF-STAGE"]["value"]
    if name.startswith("cost_below_threshold_"):
        strat = {"stf": "S-TF", "tfd1": "S-BASE-TFD1", "tfd17t": "S-BASE-TFD1-7T"}[name.split("_")[-1]]
        pr = d.j("research/prior_results.json")
        thr = pr["admission_rule"]["cost_share_max"] * pr["median_gross"][strat]
        return sum(1 for r in d.j(RESULTS["cost"])["instruments"] if r["access"].startswith("PRIMAER") and not r["blocked"]
                   and r["strategies"][strat]["sr_cost_per_year"]["base"] <= thr)
    if name == "cheapest_stir_cost_stf":
        return min(r["strategies"]["S-TF"]["sr_cost_per_year"]["base"] for r in d.j(RESULTS["cost"])["instruments"]
                   if r["risk_class"] == "STIR" and r["access"].startswith("PRIMAER"))
    if name == "cheapest_im_cost":
        return min(r["strategies"]["S-IM"]["sr_cost_per_year"]["base"] for r in d.j(RESULTS["cost"])["instruments"]
                   if r["access"].startswith("PRIMAER") and not r["blocked"])
    if name == "spend_to_BS05":
        return float(d.j("research/operating_characteristics_results.json")["cumulative_cost_eur"]["BS-05"])
    if name == "spend_to_BS04":
        return float(d.j("research/operating_characteristics_results.json")["cumulative_cost_eur"]["BS-04"])
    if name == "tests_total":
        return len(d.j("implementation/test_catalog.json")["tests"])
    if name == "requirements_total":
        return len(d.j("requirements.json")["requirements"])
    if name == "killer_tests_total":
        return sum(1 for t in d.j("implementation/test_catalog.json")["tests"] if t["id"].startswith("KT-"))
    if name == "mutations_total":
        return len(d.j("validation/mutation_catalog.json")["mutations"])
    if name in ("gates_total", "monitors_total"):
        kind = "GATE" if name == "gates_total" else "MONITOR"
        return sum(1 for g in d.j("research/evidence_gates.json")["gates"] if g["kind"] == kind)
    if name == "gate_cases_total":
        return len(list((d.root / "examples/valid/gate_cases").glob("*.json")))
    if name == "gate_rules_total":
        return sum(len(g["outcome_rules"]) + len(g["prerequisites"]) for g in d.j("research/evidence_gates.json")["gates"])
    if name == "machines_total":
        return len(d.j("architecture/state_machines.json")["machines"])
    if name == "traces_total":
        return len(list((d.root / "examples/valid/state_traces").glob("*.json")))
    if name == "transitions_total":
        return sum(len(m["transitions"]) for m in d.j("architecture/state_machines.json")["machines"])
    if name == "safety_reasons_total":
        return len(next(m for m in d.j("architecture/state_machines.json")["machines"] if m["id"] == "SM-SAFETY")["reasons"])
    if name == "lattice_combinations":
        return 2 ** (len(next(m for m in d.j("architecture/state_machines.json")["machines"] if m["id"] == "SM-SAFETY")["levels"]) - 1)
    if name.startswith("tests_by_exec/"):
        return sum(1 for x in d.j("implementation/test_catalog.json")["tests"] if x["execution"] == name.split("/")[1])
    if name.startswith("requirements_by_status/"):
        return sum(1 for x in d.j("requirements.json")["requirements"] if x["status"] == name.split("/")[1])
    if name == "scenarios_total":
        return len(d.j("architecture/scenario_catalog.json")["scenarios"])
    if name.startswith("scenarios_by_status/"):
        return sum(1 for x in d.j("architecture/scenario_catalog.json")["scenarios"] if x["status"] == name.split("/")[1])
    if name in ("examples_valid", "examples_invalid"):
        want = name == "examples_valid"
        return sum(1 for x in d.j("examples/EXAMPLES.json")["examples"] if x["valid"] == want)
    if name == "contracts_total":
        return len({x["schema"] for x in d.j("examples/EXAMPLES.json")["examples"]})
    if name == "schemas_total":
        return len(list((d.root / "schemas").glob("*.schema.json")))
    if name in ("score_k_total", "score_e_total"):
        return d.j("audit/scorecard_K.json" if name == "score_k_total" else "audit/scorecard_E.json")["total"]
    if name.startswith("score_k_area/"):
        return next(a["points"] for a in d.j("audit/scorecard_K.json")["areas"] if a["id"] == name.split("/")[1])
    if name.startswith("score_k_factor_count/"):
        f = float(name.split("/")[1])
        return sum(1 for s in d.j("audit/scorecard_K.json")["subcriteria"] if s["factor"] == f)
    if name == "score_k_lost":
        return sum(s["max"] - s["points"] for s in d.j("audit/scorecard_K.json")["subcriteria"])
    if name in ("mutations_total", "mutations_required", "known_limits_total"):
        mc = d.j("validation/mutation_catalog.json")
        return {"mutations_total": len(mc["mutations"]), "mutations_required": sum(1 for x in mc["mutations"] if x.get("required")),
                "known_limits_total": len(mc["known_limits"])}[name]
    if name == "semantic_checks_total":
        src = (d.root / "validation/semantic_checks.py").read_text(encoding="utf-8")
        return len(re.findall(r"(?m)^def check_\w+\(pkg", src))
    if name == "reference_tests_total":
        src = (d.root / "validation/test_reference_models.py").read_text(encoding="utf-8")
        return len(re.findall(r"(?m)^    def test_\w+\(self", src))
    if name.startswith("gonogo_count/"):
        want = name.split("/")[1]
        return sum(1 for st in d.j(RESULTS["dmc"])["go_no_go"].values() for g in st.values() if g["decision_real_money"] == want)
    if name == "gonogo_cells":
        return sum(len(st) for st in d.j(RESULTS["dmc"])["go_no_go"].values())
    if name == "tests_in_package":
        return sum(1 for x in d.j("implementation/test_catalog.json")["tests"] if x["execution"] == "IM_PAKET")
    if name == "adoptions_total":
        return len(d.j("audit/v2_to_v3_mapping.json")["adoptions"])
    if name == "v2_files_total":
        return len(d.j("audit/v2_to_v3_mapping.json")["artifacts"])
    if name.startswith("findings_by_status/"):
        return sum(1 for x in d.j("registers/resolution_matrix.json")["findings"] if x["status"] == name.split("/")[1])
    if name.startswith(("build_weeks_critical/", "build_weeks_until/")):
        # Wochen entlang des kritischen Pfads (gesamt oder bis einschließlich einer Stufe); Fall low, base oder high
        parts = name.split("/")
        idx = {"low": 0, "base": 1, "high": 2}[parts[-1]]
        bs = d.j("implementation/build_stages.json")
        wk = {s["id"]: s["duration_weeks"][idx] for s in bs["stages"]}
        path = bs["critical_path"]
        if parts[0] == "build_weeks_until":
            path = path[:path.index(parts[1]) + 1]
        return sum(wk[s] for s in path)
    if name.startswith("gate_today/"):
        _, cid, field = name.split("/")
        c = json.loads((d.root / "examples/valid/gate_cases" / f"{cid}.json").read_text(encoding="utf-8"))
        return c["expect_outcome"] if field == "outcome" else c["expect_rule"]
    if name.startswith("dmc_class_count/"):
        _, var, cls = name.split("/")
        return sum(1 for st in d.j(RESULTS["dmc"])["table"][var].values() for c in st.values() if c["class"] == cls)
    if name.startswith("dmc_empty_cells/"):
        return sum(1 for st in d.j(RESULTS["dmc"])["table"][name.split("/")[1]].values() for c in st.values() if c.get("universe_size") == 0)
    if name.startswith("dmc_cells/"):
        return sum(len(st) for st in d.j(RESULTS["dmc"])["table"][name.split("/")[1]].values())
    if name.startswith("lev_admissible/"):
        return sum(1 for st in d.j(RESULTS["lev"])["cells"][name.split("/")[1]].values() for c in st.values() if c.get("admissible"))
    if name.startswith("variants_count/"):
        # variants_count/computed: Stufen mit gerechneter V4; v1_better: davon Stufen, in denen die V1-Untergrenze mindestens V4 erreicht
        what = name.split("/")[1]
        vv = d.j(RESULTS["dmc"])["variants_V0_V4"].values()
        if what == "computed":
            return sum(1 for v in vv if "value_per_risk_unit" in v["V4"])
        if what == "v1_better":
            return sum(1 for v in vv if v["v1_lower_bound_at_least_v4"])
        if what == "stages":
            return len(vv)
        raise KeyError(name)
    if name.startswith("stress_margin/"):
        # stress_margin/<Allokation>/<Kennzahl>: Zählwerte über die Profile bzw. größter nötiger Brokeranteil
        _, kind, what = name.split("/")
        per = d.j("risk/stress_results.json")["results"][kind]
        if what == "insufficient":
            return sum(1 for r in per.values() if not r["broker_share_sufficient"])
        if what == "with_liquidation":
            return sum(1 for r in per.values() if r["liquidations"])
        if what == "with_derisk":
            return sum(1 for r in per.values() if r["derisk_needed"])
        if what == "required_max":
            return max(r["broker_share_required"] for r in per.values())
        if what == "profiles":
            return len(per)
        raise KeyError(name)
    if name == "build_components_total":
        return sum(len(s.get("components", [])) for s in d.j("implementation/build_stages.json")["stages"])
    if name == "build_kloc_total":
        return sum(c["kloc"] for s in d.j("implementation/build_stages.json")["stages"] for c in s.get("components", []))
    raise KeyError(name)


def resolve(d: Data, key: str) -> str:
    body, _, f = key.partition("|")
    src, _, path = body.partition(":")
    f = f or "raw"
    if src == "param":
        pid, _, sub = path.partition("/")
        v = d.params[pid]["value"]
        v = walk(v, sub) if sub else v
    elif src == "costreg":
        cid, _, sub = path.partition("/")
        v = walk(d.costreg[cid], sub or "amount")
    elif src == "ins":
        iid, _, sub = path.partition("/")
        v = walk(d.ins[iid], sub)
    elif src == "x":
        xid, _, sub = path.partition("/")
        v = walk(d.xin[xid], sub or "default_value")
    elif src == "src":
        sid, _, sub = path.partition("/")
        v = walk(d.sources[sid], sub or "status")
    elif src == "stagecost":
        sys.path.insert(0, str(d.root))
        from financials.stage_costs import stage_costs  # noqa: PLC0415 – nur bei Bedarf
        v = walk(stage_costs(), path)
    elif src == "costsym":
        sym, _, sub = path.partition("/")
        rows = [r for r in d.j(RESULTS["cost"])["instruments"] if r["symbol"] == sym]
        if len(rows) != 1:
            raise KeyError(f"Symbol {sym} nicht eindeutig im Kostenmodell")
        v = walk(rows[0], sub)
    elif src == "ocs":
        prior_mode, dsr, rest = path.split("/", 2)
        v = walk(d.j(RESULTS["oc"])["sensitivity"][f"{prior_mode}|{dsr}"], rest)
    elif src == "calc":
        v = calc(d, path)
    elif src in RESULTS:
        v = walk(d.j(RESULTS[src]), path)
    else:
        raise KeyError(f"unbekannte Quelle {src}")
    return fmt(v, f)


# ------------------------------------------------------------------------------------------------ Tabellen
def _pr(v, nd=3):
    return "–" if v is None else de(v, nd)


CMP_SYM = {"eq": "=", "ne": "≠", "lt": "<", "le": "≤", "gt": ">", "ge": "≥"}


def _same_eq(items):
    """Liefert (Variablennamen, Konstante), wenn alle Glieder die Form {eq: [{var: …}, Konstante]} mit derselben Konstante haben (ab 4 Gliedern)."""
    if len(items) < 4:
        return None
    names, consts = [], set()
    for x in items:
        if not (isinstance(x, dict) and set(x) == {"eq"} and isinstance(x["eq"][0], dict) and set(x["eq"][0]) == {"var"}
                and isinstance(x["eq"][1], (str, int, float, bool))):
            return None
        names.append(x["eq"][0]["var"])
        consts.add(json.dumps(x["eq"][1]))
    return (names, json.loads(consts.pop())) if len(consts) == 1 else None


def _ranges(names) -> str:
    """Fasst aufeinanderfolgende Namen gleicher Form (präfix_nn) zu „a … b“ zusammen."""
    out, run = [], []
    for n in names:
        m = re.fullmatch(r"(.*?)(\d+)", n)
        if run and m and (mp := re.fullmatch(r"(.*?)(\d+)", run[-1])) and mp.group(1) == m.group(1) and int(m.group(2)) == int(mp.group(2)) + 1:
            run.append(n)
            continue
        if run:
            out.append(run[0] if len(run) < 3 else f"{run[0]} … {run[-1]}")
            if 1 < len(run) < 3:
                out.append(run[1])
        run = [n]
    if run:
        out.append(run[0] if len(run) < 3 else f"{run[0]} … {run[-1]}")
        if 1 < len(run) < 3:
            out.append(run[1])
    return "{" + ", ".join(out) + "}"


def expr_text(e) -> str:
    """Kurzform eines Ausdrucks aus validation/expr.py für Tabellen (Variablen als Name, Parameter als ID)."""
    if isinstance(e, bool):
        return "wahr" if e else "falsch"
    if isinstance(e, (int, float)):
        return de(e, 0) if float(e).is_integer() else de(e, 2)
    if isinstance(e, str):
        return e
    if isinstance(e, list):
        return "{" + ", ".join(expr_text(x) for x in e) + "}"
    (op, a), = e.items()
    if op == "var":
        return a
    if op == "param":
        return a if isinstance(a, str) else f"{a[0]}[{']['.join(a[1:])}]"
    if op == "const":
        return expr_text(a)
    if op in CMP_SYM:
        return f"{expr_text(a[0])} {CMP_SYM[op]} {expr_text(a[1])}"
    if op == "in":
        return f"{expr_text(a[0])} ∈ {expr_text(a[1])}"
    if op in ("any", "all"):
        same = _same_eq(a)
        if same:
            names, const = same
            return f"{'mindestens eines' if op == 'any' else 'alle'} von {_ranges(names)} = {expr_text(const)}"
        parts = [expr_text(x) for x in a]
        return "(" + (" oder " if op == "any" else " und ").join(parts) + ")" if len(parts) > 1 else parts[0]
    if op == "not":
        return f"nicht ({expr_text(a)})"
    if op == "abs":
        return f"|{expr_text(a)}|"
    if op == "sub":
        return f"{expr_text(a[0])} − {expr_text(a[1])}"
    if op == "add":
        return " + ".join(expr_text(x) for x in a)
    return f"{op}({expr_text(a)})"


def e6_tables(d: Data, T: dict, with_values) -> None:
    """Tabellen aus Toren, Automaten, Katalogen und Bauprogramm (Etappe E6)."""
    root = d.root
    if (root / "research/evidence_gates.json").exists():
        gates = d.j("research/evidence_gates.json")["gates"]
        cases = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / "examples/valid/gate_cases").glob("*.json"))]
        ncase = {}
        for c in cases:
            ncase[c["gate"]] = ncase.get(c["gate"], 0) + 1
        rows = []
        for g in gates:
            if g["kind"] != "GATE":
                continue
            ext = sorted({m.group(0) for p in g["prerequisites"] if p["on_fail"] == "BLOCKED_EXTERNAL"
                          for m in [re.search(r"X-[A-Z0-9-]+", p["description"])] if m})
            crit = "; ".join(f"{r['id']}: {expr_text(r['when'])} ({r['reason']})" for r in g["outcome_rules"] if r["outcome"] == "FAIL") or "–"
            rows.append([g["id"], g["name"], g["stage"], g["e_block"] or "–", ", ".join(ext) or "–", with_values(crit), with_values(g["next_steps"]["PASS"]),
                         str(ncase.get(g["id"], 0))])
        T["tab.gates"] = md_table(["ID", "Tor", "Stufe", "E-Baustein", "sperrende externe Eingaben", "scheitert, wenn (FAIL-Regeln)", "Folgeschritt bei PASS",
                                   "Torfälle"], rows)
        rows = []
        for g in gates:
            if g["kind"] != "MONITOR":
                continue
            rows.append([g["id"], g["name"], with_values("; ".join(f"{r['id']}: {expr_text(r['when'])} ({r['reason']})" for r in g["outcome_rules"]
                                                                   if r["outcome"] in ("FAIL", "INCONCLUSIVE"))),
                         with_values(g["next_steps"]["FAIL"]), str(ncase.get(g["id"], 0))])
        T["tab.monitors"] = md_table(["ID", "Monitor", "löst aus, wenn", "Folge", "Torfälle"], rows)
        rows = [[c["id"], c["gate"], c["description"], c["expect_outcome"], c["expect_rule"], ", ".join(c.get("expect_flags", [])) or "–", c["facts_source"]]
                for c in cases if c.get("facts_source")]
        T["tab.gate_today"] = md_table(["Fall", "Tor", "Lage", "Ergebnis", "Regel", "Flags", "Werte aus"], rows)
        gname = {g["id"]: g["name"] for g in gates}
        emap = d.j("research/evidence_gates.json")["e_score_map"]
        T["tab.e_map"] = md_table(["E-Baustein", "Tore", "Nachweis durch"], [[k, ", ".join(v), "; ".join(gname[g] for g in v)] for k, v in emap.items()])
    if (root / "architecture/state_machines.json").exists():
        ms = d.j("architecture/state_machines.json")["machines"]
        traces = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / "examples/valid/state_traces").glob("*.json"))]
        rows = []
        for m in ms:
            nt = sum(1 for x in traces if x["machine"] == m["id"])
            size = f"{len(m['reasons'])} Sperrgründe, {len(m['levels'])} Stufen" if m["kind"] == "LATTICE" else f"{len(m['transitions'])} Übergänge"
            rows.append([m["id"], m["name"], m["question"], str(len(m["states"])), size, str(nt)])
        T["tab.machines"] = md_table(["ID", "Automat", "Frage", "Zustände", "Übergänge bzw. Gründe", "Traces"], rows)
    if (root / "implementation/test_catalog.json").exists():
        tests = d.j("implementation/test_catalog.json")["tests"]
        kts = sorted((x for x in tests if x["id"].startswith("KT-")), key=lambda x: x["killer_first_rank"])
        T["tab.killer_tests"] = md_table(["ID", "Thema", "Durchführung", "Orakel (bestanden, wenn …)", "Rückfallvariante", "Folge bei Scheitern", "Konto"],
                                         [[x["id"], x["title"], x["procedure"], with_values(x["oracle"]), x["fallback"], x["failure_effect"], x["account"]] for x in kts])
        T["tab.sec_tests"] = md_table(["Test", "Inhalt", "Stufe"], [[x["id"], x["title"], f"{x['stage']} ({x['gate']})"] for x in tests if x["id"].startswith("T-SEC-")])
        rows = []
        for ex, label in (("IM_PAKET", "im Paket ausgeführt"), ("BROKER", "Killer-Tests beim Broker (BS-01)"), ("BAU", "Abnahme im Systembau"),
                          ("BETRIEB", "Drills, Dauerläufe, Messungen im Betrieb")):
            sel = [x for x in tests if x["execution"] == ex]
            lv = {}
            for x in sel:
                lv[x["level"]] = lv.get(x["level"], 0) + 1
            rows.append([label, str(len(sel)), ", ".join(f"{k} {v}" for k, v in sorted(lv.items()))])
        T["tab.tests_summary"] = md_table(["Ausführung", "Tests", "Ebenen"], rows)
    if (root / "requirements.json").exists():
        reqs = d.j("requirements.json")["requirements"]
        areas = {}
        for r in reqs:
            a = r["id"].split("-")[1]
            areas.setdefault(a, {"IM_PAKET_NACHGEWIESEN": 0, "TEILWEISE_NACHGEWIESEN": 0, "SPEZIFIZIERT": 0})[r["status"]] += 1
        names = {"ECO": "Wirtschaft", "RES": "Forschung", "RSK": "Risiko", "EXE": "Ausführung", "PTC": "Pre-Trade", "DAT": "Daten", "ARC": "Architektur",
                 "SEC": "Sicherheit", "AI": "KI-Schicht", "ML": "ML-Komponenten", "GOV": "Governance", "OPS": "Betrieb", "LEG": "Recht und Steuern",
                 "QA": "Qualitätssicherung", "PKG": "Paket"}
        T["tab.requirements_summary"] = md_table(["Bereich", "Anforderungen", "im Paket nachgewiesen", "teilweise", "nur spezifiziert"],
                                                 [[names.get(a, a), str(sum(v.values())), str(v["IM_PAKET_NACHGEWIESEN"]), str(v["TEILWEISE_NACHGEWIESEN"]),
                                                   str(v["SPEZIFIZIERT"])] for a, v in areas.items()])
    if (root / "architecture/scenario_catalog.json").exists():
        sc = d.j("architecture/scenario_catalog.json")["scenarios"]
        cats = {}
        for s in sc:
            cats.setdefault(s["category"], []).append(s)
        T["tab.scenarios_summary"] = md_table(["Kategorie", "Szenarien", "im Paket geprüft oder gerechnet", "spezifiziert", "Beispiele"],
                                              [[k, str(len(v)), str(sum(1 for s in v if s["status"] != "SPEZIFIZIERT")),
                                                str(sum(1 for s in v if s["status"] == "SPEZIFIZIERT")), "; ".join(f"{s['id']} {s['title']}" for s in v[:2])]
                                               for k, v in cats.items()])
    if (root / "implementation/build_stages.json").exists():
        bs = d.j("implementation/build_stages.json")

        def span(s, key):
            e = s["effort"]
            return f"{de(e['low'][key], 1)} / {de(e['base'][key], 1)} / {de(e['high'][key], 1)}"
        rows = [[s["id"], s["gate"], with_values(s["name"]), span(s, "person_days"), span(s, "agent_days"), " / ".join(str(w) for w in s["duration_weeks"]),
                 ", ".join(s["depends_on"]) or "–", ", ".join(s["external"]) or "–"] for s in bs["stages"]]
        T["tab.build_program"] = md_table(["Stufe", "Tor", "Inhalt", "Personentage (niedrig / Basis / hoch)", "Agententage (niedrig / Basis / hoch)",
                                           "Wochen (niedrig / Basis / hoch)", "hängt ab von", "externe Eingaben"], rows)
        prod = bs["estimation_basis"]["productivity_kloc_per_agent_day"]["base"]
        T["tab.components"] = md_table(["Komponente", "Inhalt", "KLOC (Schätzung)", "Agententage (Basis)"],
                                       [[c["id"], c["name"], de(c["kloc"], 1), de(c["kloc"] / prod, 1)] for s in bs["stages"] for c in s.get("components", [])])
        T["tab.dod"] = md_table(["Stufe", "Definition of Done"], [[s["id"], with_values("; ".join(s["dod"]))] for s in bs["stages"]])
    if (root / "registers/resolution_matrix.json").exists():
        T["tab.resolution"] = md_table(["ID", "Befund", "Status", "Behandlung", "Nachweis", "Restrisiko"],
                                       [[f["id"], f["finding"], f["status"], with_values(f["treatment"]), ", ".join(f["evidence"]), with_values(f["residual"])]
                                        for f in d.j("registers/resolution_matrix.json")["findings"]])
    if (root / "examples/EXAMPLES.json").exists():
        ex = d.j("examples/EXAMPLES.json")["examples"]
        by = {}
        for x in ex:
            by.setdefault(x["schema"], [0, 0, set()])
            by[x["schema"]][0 if x["valid"] else 1] += 1
            if not x["valid"] and x["expected"]["type"] == "SEMANTIC":
                by[x["schema"]][2].add(x["expected"]["rule"])
        T["tab.contracts"] = md_table(["Vertrag (schemas/…)", "gültige Beispiele", "ungültige Beispiele", "semantische Regeln"],
                                      [[f"`{k}`", str(v[0]), str(v[1]), ", ".join(sorted(v[2])) or "–"] for k, v in sorted(by.items())])


def gen_tables(d: Data) -> dict:
    T = {}
    P = d.params
    stages = P["P-ECO-CAPITAL-STAGES"]["value"]
    prior = d.j("research/prior_results.json")
    lev = d.j("risk/leverage_results.json")
    dmc = d.j("financials/decision_montecarlo_results.json")
    cost = d.j("financials/cost_model_results.json")
    turn = d.j("research/turnover_results.json")

    def mio(x):
        return de(float(x) / 1e6, 2).rstrip("0").rstrip(",")

    # Umschlag
    rows = []
    names = {"S-TF": "S-TF schnelle Trendfolge", "S-IM": "S-IM Intraday-Momentum", "S-REV": "S-REV Kurzfrist-Umkehr",
             "S-BASE-TFD1": "TF-D1 (v2.0, ohne Zeitstopp)", "S-BASE-TFD1-7T": "TF-D1-7T (mit 7-Tage-Zeitstopp)"}
    for k, v in turn["strategies"].items():
        rows.append([names[k], de(v["round_turns_per_year"], 1), de(v["time_in_market"] * 100, 0) + " %", de(v["holding_hours_median"], 1) + " h",
                     de(v["share_within_4h_4d"] * 100, 0) + " %", de(v["share_timestop"] * 100, 1) + " %", de(v["max_holding_hours"], 0) + " h",
                     "ja" if v["admissible_holding"] else "nein"])
    T["tab.turnover"] = md_table(["Strategie", "Round-Turns je Jahr und Instrument", "Zeit im Markt", "Median-Haltedauer", "Anteil 4 h–4 T",
                                  "Anteil Zeitstopp", "längste Haltedauer", "7-Tage-Grenze eingehalten"], rows)
    # Kosten je Instrument (Auswahl: zugängliche, nicht gesperrte)
    rows = []
    for r in sorted(cost["instruments"], key=lambda x: x["strategies"]["S-TF"]["sr_cost_per_year"]["base"]):
        if r["access"] != "PRIMAERBROKER_BOERSE_ANGEBOTEN" or r["blocked"]:
            continue
        rows.append([r["symbol"], r["risk_class"], r["size_class"], de(float(r["notional_eur"]), 0), de(float(r["cost_rt_eur"]), 2), de(r["cost_rt_bp"], 2),
                     de(r["c_rt_sr"]["base"], 5), de(r["strategies"]["S-TF"]["sr_cost_per_year"]["base"], 3),
                     de(r["strategies"]["S-BASE-TFD1"]["sr_cost_per_year"]["base"], 3)])
    T["tab.cost_instruments"] = md_table(["Symbol", "Risikoklasse", "Größe", "Nominal EUR", "Round-Turn EUR", "Round-Turn bp", "c_RT (Sharpe je RT)",
                                          "Kosten S-TF (Sharpe/Jahr)", "Kosten TF-D1 (Sharpe/Jahr)"], rows)
    fc = cost["fixed_costs"]
    rows = [["Marktdaten Anzeige (Broker)", de(float(fc["market_data_monthly_eur"]["ANZEIGE"]["monthly_eur"]), 2) + " EUR/Monat",
             "Basisfall; entfällt je Börse ab Kommissionsschwelle"],
            ["Marktdaten Non-Display (Managed)", de(float(fc["market_data_monthly_eur"]["NON_DISPLAY_MANAGED"]["monthly_eur"]), 2) + " EUR/Monat", "Sensitivität X-DATA-ND"],
            ["Marktdaten Non-Display (direkt)", de(float(fc["market_data_monthly_eur"]["NON_DISPLAY_USER"]["monthly_eur"]), 2) + " EUR/Monat", "Sensitivität X-DATA-ND"],
            ["Historische Daten (einmalig)", de(float(fc["historical_data_once_eur"]), 2) + " EUR", "Kibot, CQG-Abgleich, Databento"],
            ["Infrastruktur (drei Instanzen, Sicherung, Alarm)", de(float(fc["infrastructure_monthly_eur"]), 2) + " EUR/Monat", "ANNAHME (X-INF-VPS)"],
            ["KI-Abo (Basis " + fc["ai_tier_base"] + ")", de(float(fc["ai_subscription_monthly_eur"][fc["ai_tier_base"]]), 2) + " EUR/Monat", "Nous Portal"],
            ["Coding-Agent im Aufbau", de(float(fc["coding_agent_monthly_eur"]), 2) + " EUR/Monat", "ANNAHME"],
            ["Externe Risikofunktion (ab G9)", de(float(fc["external_risk_function_monthly_eur"]), 2) + " EUR/Monat", "ANNAHME (X-ORG-RISK)"],
            ["Penetrationstest / Audit / Gegenprüfung", " / ".join(de(float(fc["external_once_eur"][k]), 0) for k in ("pentest", "audit", "review")) + " EUR", "ANNAHME"]]
    T["tab.fixed_costs"] = md_table(["Posten", "Betrag", "Status"], rows)
    rows = [[c["symbol"], de(c["future_rt_bp"], 2), de(c["cfd_spread_rt_bp"], 2), de(c["cfd_financing_rt_bp_long"], 2), de(c["cfd_financing_rt_bp_short"], 2)]
            for c in cost["cfd_comparison"]]
    T["tab.cfd"] = md_table(["Symbol", "Future Round-Turn bp", "CFD-Spread Round-Turn bp", "CFD-Finanzierung long bp", "CFD-Finanzierung short bp"], rows)
    # Prior
    g = prior["gross_per_instrument"]
    lbl = {"S-TF": "S-TF mit Carry-Filter", "S-TF-OHNE-CA": "S-TF ohne Carry-Filter", "S-REV": "S-REV", "S-BASE-TFD1": "TF-D1",
           "S-BASE-TFD1-7T": "TF-D1-7T", "S-IM:ANLEIHE": "S-IM Zinsen/Anleihen", "S-IM:ROHSTOFF": "S-IM Rohstoffe/Krypto", "S-IM:FX": "S-IM Devisen"}
    rows = [[lbl[k], de(v["p05"], 3), de(v["p50"], 3), de(v["p95"], 3), de(v["mean"], 3)] for k, v in g.items()]
    T["tab.prior_gross"] = md_table(["Strategie (je Instrument, brutto)", "5 %-Quantil", "Median", "95 %-Quantil", "Mittel"], rows)
    rows = []
    for v in ["U-KOSTEN", "U-BREAKEVEN", "U-KOSTEN-TFD1-7T", "U-KOSTEN-TFD1", "U-ALLE"]:
        for st in stages:
            a = prior["admission"][v][str(st)]
            pe = prior["portfolio"][v][str(st)][a["basis"]]
            syms = [d.ins[i]["symbol"] for i in a["instruments"]]
            rows.append([v, mio(st), a["n"], de(a["D"], 2), ", ".join(syms) if len(syms) <= 9 else ", ".join(syms[:9]) + f" … (+{len(syms) - 9})",
                         _pr(pe["p50"] if pe else None, 3), _pr(pe["p_positive"] if pe else None, 2)])
    T["tab.admission"] = md_table(["Variante", "Kapital (Mio. EUR)", "Instrumente", "D", "zugelassen", "Netto-Sharpe Portfolio (Median)", "P(> 0)"], rows)
    # Hebel
    rows = []
    for v in ["U-KOSTEN", "U-BREAKEVEN", "U-KOSTEN-TFD1-7T", "U-KOSTEN-TFD1", "U-ALLE"]:
        for st in stages:
            for prof in ["H5", "H10", "H15", "H20"]:
                c = lev["cells"][v][str(st)][prof]
                rows.append([v, mio(st), prof, "zulässig" if c["admissible"] else "unzulässig", _pr(c.get("sigma_achieved"), 3), _pr(c.get("L_g_achieved"), 2),
                             _pr(c.get("gap_loss_achieved", {}).get("DESIGN"), 3), "; ".join(c["reasons"])[:160] or "–"])
    T["tab.leverage_cells"] = md_table(["Variante", "Kapital (Mio. EUR)", "Profil", "Befund", "σ_p erreicht", "L_g", "Lückenstress", "Gründe"], rows)
    rows = []
    for st in stages:
        for prof, c in lev["leverage_calibration_via_rates"][str(st)].items():
            if not c.get("feasible"):
                rows.append([mio(st), prof, "–", "–", "–", "–", c.get("reason", "")])
                continue
            rows.append([mio(st), prof, de(c["rate_risk_share"] * 100, 0) + " %", de(c["L_g"], 1) + "×", de(c["gap_loss_design"] * 100, 1) + " %",
                         de(c["mean_cost_sr"], 3), "innerhalb" if c["within_loss_budget"] else "über Budget"])
    T["tab.leverage_calibration"] = md_table(["Kapital (Mio. EUR)", "Profil", "Zins-Risikoanteil", "L_g", "Lückenstress", "mittlere Kosten (Sharpe/Jahr)",
                                              "Verlustbudget"], rows)
    rows = [[k, de(v["design_gap_median"] * 100, 2) + " %", de(v["standalone_cap_typical"], 2) + "×", v["binding_instrument"],
             de(v["standalone_cap_strictest"], 2) + "×"] for k, v in lev["class_caps"].items()]
    T["tab.class_caps"] = md_table(["Risikoklasse", "Konstruktionslücke (Median)", "Hebeldeckel typisch", "strengstes Instrument", "Hebeldeckel streng"], rows)
    # Stress
    st_ = d.j("risk/stress_results.json")
    scen = d.j("risk/stress_scenarios.json")
    names_sc = {s["id"]: s["name"] for s in scen["historical"] + scen["hypothetical"]}
    cols = [("SYSTEM", "H5"), ("ALTERNATIVE_TFD1", "H5"), ("WUNSCHHEBEL", "H5"), ("WUNSCHHEBEL", "H10"), ("WUNSCHHEBEL", "H15"), ("WUNSCHHEBEL", "H20")]
    rows = []
    for sid in names_sc:
        row = [sid, names_sc[sid]]
        for kind, prof in cols:
            r = st_["results"].get(kind, {}).get(prof)
            if not r:
                row.append("–")
                continue
            x = r["scenarios"][sid]
            flag = " ⚠" if x["daily_cap_breach"] else ""
            row.append(de(x["loss_with_ladder"] * 100, 1) + " %" + flag)
        rows.append(row)
    T["tab.stress"] = md_table(["ID", "Szenario", "SYSTEM H5", "ALTERNATIVE TF-D1 H5", "WUNSCHHEBEL H5", "WUNSCHHEBEL H10", "WUNSCHHEBEL H15",
                                "WUNSCHHEBEL H20"], rows)
    rows = []
    for kind, per in st_["results"].items():
        for prof, r in per.items():
            rows.append([kind, prof, de(r["L_g"], 1) + "×", de(r["margin_to_equity"] * 100, 1) + " %", r["worst_scenario"], de(r["worst_loss_with_ladder"] * 100, 1) + " %",
                         len(r["daily_cap_breaches"]), len(r["liquidations"])])
    T["tab.stress_summary"] = md_table(["Allokation", "Profil", "L_g", "M/E", "schlimmstes Szenario", "Verlust mit Leiter", "Szenarien > 9 % am Tag",
                                        "Liquidationen"], rows)
    # Kelly
    k = d.j("risk/kelly_ruin_results.json")["results"]
    rows = []
    for prof, per in k.items():
        for kind, r in per.items():
            if "same_as" in r:
                rows.append([prof, kind, "wie " + r["same_as"], "", "", "", "", "", ""])
                continue
            rows.append([prof, kind, de(r["sigma"] * 100, 1) + " %", de(r["sr_prior"]["mean"], 3), de(r["annual_return"]["p50"] * 100, 1) + " %",
                         de(r["max_drawdown"]["5"]["p95"] * 100, 1) + " %", de(r["p_drawdown_ge"]["20"] * 100, 1) + " %", de(r["p_ruin_5y"] * 100, 2) + " %",
                         de(r["p_day_loss_over_cap_per_year"] * 100, 2) + " %"])
    T["tab.kelly"] = md_table(["Profil", "Allokation", "σ_p", "E[Netto-Sharpe]", "Jahresrendite Median", "max. Drawdown 5 J (95 %)", "P(DD ≥ 20 %)",
                               "P(Ruin 5 J)", "P(Tag > 9 %) je Jahr"], rows)
    # Betriebscharakteristik
    oc = d.j("research/operating_characteristics_results.json")
    rows = []
    for label, res in [("registriert", oc["registered"])] + [(k2, v2) for k2, v2 in oc["sensitivity"].items()]:
        for cname, r in res.items():
            for mode in ("ohne_futility", "mit_futility"):
                x = r[mode]["rates"]
                rows.append([label, cname, mode.replace("_", " "), de(x["passed_G3"] * 100, 1) + " %", de(x["reached_G5_build"] * 100, 1) + " %",
                             de(x["passed_G8"] * 100, 1) + " %", de(x["accepted_final"] * 100, 1) + " %", de(float(r[mode]["expected_cost_eur"]), 0)])
    T["tab.oc"] = md_table(["Konfiguration", "Klasse", "Futility", "besteht G3", "erreicht Bau (G5)", "besteht G8", "Endtor", "erwartete Kosten EUR"], rows)
    # Kostendrift
    dr = d.j("operations/costdrift_results.json")
    rows = []
    names_dr = {"pooled": "gepoolt mit Schrumpfung (v3.0)", "v2_unpooled_min20": "je Instrument, mindestens 20 Fills (wie v2.0)",
                "v2_frequency_unpooled_min20": "wie v2.0 mit Umschlag von TF-D1"}
    for k2, v2 in dr["results"].items():
        for _, x in v2.items():
            rows.append([names_dr.get(k2, k2), de(x["true_ratio"], 2), de(x["median_months"], 0), de(x["p_trigger_within_pilot"] * 100, 1) + " %",
                         de(x["p_trigger_within_24m"] * 100, 1) + " %"])
    T["tab.costdrift"] = md_table(["Verfahren", "wahres Kostenverhältnis", "Median Monate bis Auslösung", "P(Auslösung im Pilot)", "P(Auslösung ≤ 24 Monate)"], rows)
    # Statistik
    stat = d.j("research/statistical_results.json")
    rows = [[k2.replace(".", ","), de(v2, 1)] for k2, v2 in stat["years_for_power"].items()]
    T["tab.power"] = md_table(["Netto-Sharpe p. a.", "Jahre Daten für α = 5 %, Teststärke 80 %"], rows)
    # Entscheidung
    rows = []
    for v in ["U-KOSTEN", "U-BREAKEVEN", "U-KOSTEN-TFD1-7T", "U-KOSTEN-TFD1"]:
        for st in stages:
            for prof in ["H5", "H10", "H15", "H20"]:
                c = dmc["table"][v][str(st)][prof]
                b = c.get("base")
                rows.append([v, mio(st), prof, c["class"], de(float(b["expected_annual_value_eur"]), 0) if b else "–", _pr(b["p_npv_positive"], 2) if b else "–",
                             de(float(b["npv_mean_eur"]), 0) if b else "–", _pr(b["value_per_risk_unit"], 3) if b else "–",
                             de(float(b["break_even_capital_eur"]), 0) if b and b["break_even_capital_eur"] else "–"])
    T["tab.dmc"] = md_table(["Variante", "Kapital (Mio. EUR)", "Profil", "Befund", "E[Jahreswert] EUR", "P(NPV > 0)", "NPV Mittel EUR", "Wert je Risikoeinheit",
                             "Break-even-Kapital EUR"], rows)
    rows = []
    for st in stages:
        row = [mio(st)]
        for prof in ["H5", "H10", "H15", "H20"]:
            g2 = dmc["go_no_go"][str(st)][prof]
            row.append(f"{g2['decision_real_money']} ({g2['class_registered']})")
        row.append(dmc["go_no_go"][str(st)]["H5"]["class_alternative_TFD1_needs_operator_decision"])
        rows.append(row)
    T["tab.gonogo"] = md_table(["Kapital (Mio. EUR)", "H5", "H10", "H15", "H20", "Alternative TF-D1 H5 (Betreiberentscheidung nötig)"], rows)
    rows = []
    for st in stages:
        c = dmc["table"]["U-KOSTEN-TFD1"][str(st)]["H5"]
        if "sensitivities" not in c:
            continue
        for name, s2 in c["sensitivities"].items():
            rows.append([mio(st), name.replace("_", " "), s2["class"], de(s2["p_npv_positive"], 2), de(float(s2["expected_annual_value_eur"]), 0)])
    T["tab.dmc_sens_tfd1"] = md_table(["Kapital (Mio. EUR)", "Sensitivität", "Befund", "P(NPV > 0)", "E[Jahreswert] EUR"], rows)
    rows = []
    for st, v in dmc["variants_V0_V4"].items():
        v1 = v["V1"]
        v4 = v.get("V4", {})
        alt = v.get("V4_ALTERNATIVE_TFD1", {})
        rows.append([mio(st), " / ".join(de(x, 2) for x in v1["value_per_risk_unit_range"]), _pr(v4.get("value_per_risk_unit"), 3),
                     _pr(alt.get("value_per_risk_unit"), 3), v["decision"]])
    v1r = P["P-ECO-V1-SR"]["value"]
    T["tab.variants"] = md_table(["Kapital (Mio. EUR)", f"V1 Wert je Risikoeinheit (Index {de(v1r[0], 2)}/{de(v1r[1], 2)})", "V4 S-TF", "V4 Alternative TF-D1", "Befund"], rows)
    rows = [[sid, s["gate"], de(float(s["months"]), 1), de(float(s["human_eur"]), 0), de(float(s["agent_eur"]), 0), de(float(s["once_eur"]), 0),
             de(float(s["running_eur"]), 0), de(float(s["operator_routines_eur"]), 0), de(float(s["external_risk_function_eur"]), 0),
             de(float(s["total_eur"]), 0)] for sid, s in dmc["stage_costs"].items()]
    T["tab.stage_costs"] = md_table(["Stufe", "Tor", "Monate", "Mensch (Projekt) EUR", "Agent EUR", "einmalig EUR", "laufend EUR", "Betreiberroutinen EUR",
                                     "Risikofunktion EUR", "gesamt EUR"], rows)
    # Register-Auszüge
    rows = [[x["id"], x["name"], x["owner"], ", ".join(x["blocks"]), ("Standard " + str(x["default_value"])) if x["default_marked"] else "–"]
            for x in d.j("external_inputs.json")["inputs"]]
    T["tab.external_inputs"] = md_table(["ID", "Eingabe", "zuständig", "sperrt", "markierter Standardwert"], rows)
    xreg = d.j("external_inputs.json")
    gates = d.j("research/evidence_gates.json")["gates"]
    labels = {**{g["id"]: g["name"] for g in gates}, **xreg["block_targets"]}
    order = [g["id"] for g in gates] + list(xreg["block_targets"])
    by = {}
    for x in xreg["inputs"]:
        for tgt in x["blocks"]:
            by.setdefault(tgt, []).append(f"{x['id']}" + ("" if x["status"] == "UNBESTAETIGT" else f" ({x['status']})"))
    T["tab.external_by_gate"] = md_table(["Gesperrt ist", "bis bestätigt sind"], [[labels[k], ", ".join(by[k])] for k in order if k in by])
    rows = [[x["id"], x["title"], x["decision"], " ".join(x.get("consequences", []))] for x in d.j("registers/decision_register.json")["decisions"]
            if x["type"] == "KONFLIKT"]
    T["tab.conflicts"] = md_table(["ID", "Konflikt", "Behandlung (R-09)", "Folgen und nötige Betreiberentscheidung"], rows)
    rows = [[x["id"], x["title"], x["operator_answer_verbatim"]] for x in d.j("registers/decision_register.json")["decisions"] if x["type"] == "BETREIBER"]
    T["tab.operator_decisions"] = md_table(["ID", "Frage", "Antwort des Betreibers (Wortlaut)"], rows)
    rows = [[r["id"], r["title"], r["likelihood"], r["impact"], r["score"], "; ".join(r["controls"])[:140]] for r in
            sorted(d.j("registers/risk_register.json")["risks"], key=lambda z: -z["score"])]
    T["tab.risks"] = md_table(["ID", "Risiko", "W", "A", "Score", "Kontrollen"], rows)
    cnt = {}
    for i in d.ins.values():
        key = (i["asset_class"], i["access"]["status"].startswith("PRIMAER") and not i["blocked"])
        cnt[key] = cnt.get(key, 0) + 1
    classes = sorted({k[0] for k in cnt})
    rows = [[c, cnt.get((c, True), 0) + cnt.get((c, False), 0), cnt.get((c, True), 0)] for c in classes]
    T["tab.universe"] = md_table(["Anlageklasse", "Kandidaten", "davon beim Primärbroker handelbar (Börse angeboten, nicht gesperrt)"], rows)
    # Parameterauszüge je Gruppe (Werte nur aus parameters.json)
    def pval(v):
        if isinstance(v, bool):
            return "ja" if v else "nein"
        if isinstance(v, (int, float)):
            return de(v, 0) if float(v).is_integer() else de(v, max(2, min(4, len(repr(v).split(".")[-1]))))
        if isinstance(v, list):
            return "[" + "; ".join(pval(x) for x in v) + "]"
        if isinstance(v, dict):
            return "; ".join(f"{k2}: {pval(v2)}" for k2, v2 in v.items())
        return str(v)

    for pref in ("P-OP", "P-RISK", "P-GAP", "P-LEV", "P-SIM", "P-MRG", "P-UNI", "P-STR", "P-PRI", "P-RES", "P-OC", "P-ECO", "P-AI", "P-OPS", "P-MON",
                 "P-EXE", "P-PTC", "P-DATA", "P-SEC", "P-SLO", "P-QA"):
        rows = [[x["id"], x["name"], pval(x["value"]), x["unit"], x["status"]] for x in d.j("parameters.json")["parameters"] if x["id"].startswith(pref + "-")]
        T[f"tab.params:{pref}"] = md_table(["ID", "Bedeutung", "Wert", "Einheit", "Status"], rows)
    # Runbooks und Drills (§14.1)
    PID = re.compile(r"\bP-[A-Z0-9]+(?:-[A-Z0-9]+)+\b")

    def with_values(text):
        def rep(m):
            x = P.get(m.group(0))
            return f"{m.group(0)} ({pval(x['value'])} {x['unit']})" if x else m.group(0)
        return PID.sub(rep, text)

    if (d.root / "operations/runbook_register.json").exists():
        rbr = d.j("operations/runbook_register.json")
        rows = [[r["id"], r["title"], r["severity"], ", ".join(r["scenarios"] + r["killer_tests"] + r["ha_events"]) or "–",
                 ", ".join(r["safety_reasons"]) or "–", ", ".join(r["drills"]) or "–"] for r in rbr["runbooks"]]
        T["tab.runbooks"] = md_table(["ID", "Runbook", "Schwere", "Auslöser (Szenario, Killer-Test, HA)", "Sperrgründe", "Drills"], rows)
        secs = []
        for r in rbr["runbooks"]:
            secs.append(f"### {r['id']} {r['title']}\n\n**Schwere:** {r['severity']} · **Auslöser:** {with_values(r['triggers'])}\n")
            secs.append("\n".join(f"{k + 1}. {with_values(st)}" for k, st in enumerate(r["steps"])))
            secs.append(f"\n**Abschluss:** {with_values(r['exit_criteria'])}\n")
        T["gen.runbooks"] = "\n".join(secs).rstrip()
        rows = [[k, ", ".join(v)] for k, v in rbr["coverage"]["scenarios"].items()] + [[k, ", ".join(v)] for k, v in rbr["coverage"]["killer_tests"].items()]
        T["tab.runbook_coverage"] = md_table(["Szenario oder Killer-Test", "Runbooks"], rows)
    if (d.root / "operations/drill_register.json").exists():
        rows = [[x["id"], x["title"], with_values(x["interval"]), x["gate"], with_values(x["procedure"]), with_values(x["pass"])]
                for x in d.j("operations/drill_register.json")["drills"]]
        T["tab.drills"] = md_table(["ID", "Drill", "Rhythmus", "Tor", "Ablauf", "bestanden, wenn"], rows)
    e6_tables(d, T, with_values)
    # Datenanbieter und Marktdatengebühren (§9.1) aus den Rohbelegen der Recherche
    r5 = d.j("research/sources/R5_data_index_hermes.json")

    def flat(o, n=6):
        if o is None:
            return "–"
        if isinstance(o, dict):
            items = [f"{k2}: {flat(v2, n)}" for k2, v2 in o.items() if v2 not in (None, "", [], {})]
            return "; ".join(items[:n]) if items else "–"
        if isinstance(o, list):
            return ", ".join(flat(x, n) for x in o)
        return str(o)

    rows = []
    for v in r5["historical_data_vendors"]:
        sid = "SRC-HIST-" + v["id"].replace("_", "-")
        rows.append([v.get("vendor") or v["id"], flat(v.get("coverage")), flat(v.get("granularity")),
                     {True: "ja", False: "nein"}.get(v.get("expired_contracts_included"), "nicht belegt"), flat(v.get("pricing"), 4),
                     flat(v.get("license"), 3), v["status"], sid if sid in d.sources else "–"])
    T["tab.vendors_hist"] = md_table(["Anbieter", "Abdeckung", "Auflösung", "verfallene Kontrakte", "Preis (laut Anbieter)", "Lizenz", "Status",
                                      "Quelle"], rows)
    rows = []
    for v in r5["market_data_fees"]:
        sid = "SRC-MDF-" + v["id"].replace("_", "-")
        rows.append([v.get("exchange") or v["id"], v.get("document") or "–", v.get("effective_date") or "–", flat(v.get("fees"), 5),
                     v.get("status", "–"), sid if sid in d.sources else "–"])
    T["tab.md_fees"] = md_table(["Börse", "Dokument", "gültig ab", "Gebühren (Auszug, Originalwährung je Monat)", "Status", "Quelle"], rows)
    # Proxy-Regel (§6.5)
    rows = []
    for i in d.ins.values():
        if not i["standard_ref"]:
            continue
        s2 = d.ins.get(i["standard_ref"])
        if s2 is None:
            rows.append([i["symbol"], i["standard_ref"], "–", "–", "–", "–", "FEHLT"])
            continue
        ratio = float(i["multiplier"]) / float(s2["multiplier"])
        pa, pb = float(i["planning"]["price"]["value"]), float(s2["planning"]["price"]["value"])
        same = (s2["risk_class"] == i["risk_class"] and s2["currency"] == i["currency"]
                and pb > 0 and abs(pa / pb - 1) <= P["P-DATA-PROXY-PRICE-TOL"]["value"])
        rows.append([i["symbol"], s2["symbol"], f"{i['exchange']} / {s2['exchange']}", de(ratio, 4),
                     de(i["data_history"]["years_available"], 1) + " / " + de(s2["data_history"]["years_available"], 1),
                     "gleiche Klasse, Währung und Notierung" if same else "ABWEICHUNG", "zulässig" if same else "unzulässig ohne Nachweis"])
    T["tab.proxies"] = md_table(["Kontrakt", "Proxy (Standardkontrakt)", "Börse", "Multiplikator-Verhältnis", "Historie Jahre (eigen / Proxy)", "Prüfung",
                                 "Befund"], rows)
    # Limits (§7.5)
    def limit_value(ref):
        if ref.startswith("P-") and "{PROFIL}" in ref:
            return "; ".join(f"{pr} {pval(P[ref.replace('{PROFIL}', pr)]['value'])}" for pr in ("H5", "H10", "H15", "H20"))
        if ref in P:
            x = P[ref]
            return f"{pval(x['value'])} {x['unit']}"
        if ref.startswith("risk/leverage_results.json#/class_caps"):
            return "je Klasse (Tabelle Hebeldeckel)"
        return ref.split("#")[-1]

    rows = [[x["id"], x["level"], x["type"], limit_value(x["value_ref"]), x["value_ref"], x["action"], x["timing"], x["note"] or "–"]
            for x in d.j("registers/limits.json")["limits"]]
    T["tab.limits"] = md_table(["ID", "Ebene", "Art", "Wert", "Quelle des Werts", "Reaktion", "Zeitpunkt", "Hinweis"], rows)
    # Skalierungsstufen (§4.3)
    rows = []
    for st in stages:
        adm = {v: prior["admission"][v][str(st)] for v in ("U-KOSTEN", "U-BREAKEVEN", "U-KOSTEN-TFD1-7T", "U-KOSTEN-TFD1")}
        tf = adm["U-KOSTEN-TFD1"]["instruments"]
        micro = sum(1 for i in tf if d.ins[i]["size_class"] == "MICRO")
        cell = dmc["table"]["U-KOSTEN-TFD1"][str(st)]["H5"]
        fca = cell.get("fixed_costs_annual")
        com = cell.get("commission_monthly_eur") or {}
        rows.append([mio(st), adm["U-KOSTEN"]["n"], adm["U-BREAKEVEN"]["n"], adm["U-KOSTEN-TFD1-7T"]["n"], adm["U-KOSTEN-TFD1"]["n"],
                     f"{micro} / {len(tf) - micro}", de(float(fca["total_eur"]), 0) if fca else "–",
                     de(sum(float(x) for x in com.values()), 0) if com else "–", cell["class"]])
    T["tab.stages"] = md_table(["Kapital (Mio. EUR)", "Instrumente U-KOSTEN", "U-BREAKEVEN", "TF-D1-7T", "TF-D1", "TF-D1: Micro / Standard",
                                "Fixkosten je Jahr EUR (inkl. Betreiberzeit)", "Kommission je Monat EUR (TF-D1)", "Befund TF-D1 H5"], rows)
    # Hebelprofile (§7.3)
    ref = str(P["P-RISK-STRESS-REF-STAGE"]["value"])
    rows = []
    for prof in ["H5", "H10", "H15", "H20"]:
        adm = [f"{v} {mio(st)}" for v in ("U-KOSTEN", "U-BREAKEVEN", "U-KOSTEN-TFD1-7T", "U-KOSTEN-TFD1") for st in stages
               if lev["cells"][v][str(st)][prof]["admissible"]]
        sig = de(P[f"P-LEV-{prof}-SIGMA"]["value"] * 100, 0) + " %"
        if prof == "H5":
            sig += " (Obergrenze; mindestens " + de(P["P-LEV-H5-SIGMA-MIN"]["value"] * 100, 0) + " %)"
        rows.append([prof, de(P[f"P-LEV-{prof}-CAP"]["value"], 0) + "×", sig, de(P[f"P-LEV-{prof}-ME"]["value"] * 100, 0) + " %",
                     de(P[f"P-LEV-{prof}-ES"]["value"] * 100, 0) + " %", P[f"P-LEV-{prof}-MINDIV"]["value"], ", ".join(adm) if adm else "keine"])
    T["tab.profiles"] = md_table(["Profil", "Obergrenze L_g", "σ-Ziel p. a.", "M/E höchstens", "ES-Limit (97,5 %, 1 Tag)", "Mindestdiversifikation",
                                  "zulässig in (Variante, Mio. EUR)"], rows)
    # Lücken und Margin-Pfade in der Referenzstufe (§7.4 Nr. 3 und 4)
    rows = []
    for v in ("U-KOSTEN", "U-BREAKEVEN", "U-KOSTEN-TFD1-7T", "U-KOSTEN-TFD1"):
        for prof in ["H5", "H10", "H15", "H20"]:
            c = lev["cells"][v][ref][prof]
            g2, m = c["gap_loss_achieved"], c["margin_to_equity"]
            rows.append([v, prof, de(c["sigma_achieved"] * 100, 1) + " %", de(c["L_g_achieved"], 2) + "×", de(g2["HIST"] * 100, 1) + " %",
                         de(g2["K5"] * 100, 1) + " %", de(g2["K10"] * 100, 1) + " %", de(g2["DESIGN"] * 100, 1) + " %",
                         " / ".join(de(m[k] * 100, 1) for k in ("basis", "plus50", "plus100")) + " %", "ja" if c["admissible"] else "nein"])
    T["tab.gaps"] = md_table(["Variante", "Profil", "σ_p erreicht", "L_g", "Lücke historisch", "Lücke 5 σ", "Lücke 10 σ", "Konstruktionslücke",
                              "M/E Basis / +50 % / +100 %", "zulässig"], rows)
    # Betriebsband (§7.3)
    rows = []
    for v in ("U-KOSTEN", "U-BREAKEVEN", "U-KOSTEN-TFD1-7T", "U-KOSTEN-TFD1"):
        for prof in ["H5", "H20"]:
            b = lev["cells"][v][ref][prof]["band"]
            rows.append([v, prof, de(b["share_zero"] * 100, 1) + " %", de(b["share_below_band"] * 100, 1) + " %", de(b["share_in_band"] * 100, 1) + " %",
                         de(b["share_at_cap"] * 100, 1) + " %"])
    T["tab.band"] = md_table(["Variante", "Profil", "Zeitanteil L_g = 0", "unter dem Band", "im Band", "an der Profilgrenze"], rows)
    # Drawdown-Verteilungen (§7.4 Nr. 2)
    rows = []
    for prof, per in k.items():
        for kind, r in per.items():
            if "same_as" in r:
                continue
            md = r["max_drawdown"]
            rows.append([prof, kind] + [de(md[y]["p50"] * 100, 1) + " / " + de(md[y]["p95"] * 100, 1) + " %" for y in ("1", "3", "5")]
                        + [de(r["p_drawdown_ge"][x] * 100, 1) + " %" for x in ("10", "20", "30", "50")]
                        + [de(r["recovery_days"]["p50"], 0) if r["recovery_days"]["p50"] is not None else "–", de(r["p_trading_stop_5y"] * 100, 1) + " %",
                           de(r["annual_return"]["es_97_5"] * 100, 1) + " %"])
    T["tab.kelly_dd"] = md_table(["Profil", "Allokation", "max. DD 1 J (Median / 95 %)", "3 J", "5 J", "P(DD ≥ 10 %)", "P(DD ≥ 20 %)", "P(DD ≥ 30 %)",
                                  "P(DD ≥ 50 %)", "Erholung Median (Handelstage)", "P(Handelsstopp 5 J)", "ES 97,5 % Jahresrendite"], rows)
    # Margin und Liquidation (§7.7, EV-09)
    rows = []
    trig, so = P["P-MRG-DERISK-TRIGGER"]["value"], P["P-MRG-BROKER-STOPOUT"]["value"]
    s2 = P["P-MRG-STRESS-2"]["value"]
    phi = P["P-ECO-CASH-AT-BROKER"]["value"]
    for kind, per in st_["results"].items():
        for prof in PROFILES:
            r = per[prof]
            me = r["margin_to_equity"]
            worst_level = min(x["margin_level_after"] for x in r["scenarios"].values() if x["margin_level_after"] is not None)
            rows.append([kind, prof, de(me * 100, 1) + " %", de(me * (1 + s2) * 100, 1) + " %", de(phi / me * 100, 0) + " %",
                         de(worst_level * 100, 0) + " %", de(margin_loss_to_level(me, s2, trig, phi) * 100, 1) + " %",
                         de(margin_loss_to_level(me, s2, so, phi) * 100, 1) + " %", de(r["broker_share_required"] * 100, 1) + " %",
                         "ja" if r["broker_share_sufficient"] else "nein", str(len(r["liquidations"]))])
    if (d.root / "audit/scorecard_K.json").exists():
        sk = d.j("audit/scorecard_K.json")
        T["tab.score_k"] = md_table(["UK", "Unterkriterium", "Pkt.", "Faktor", "Punkte", "Abzug begründet durch"],
                                    [[s["id"], s["name"], de(s["max"], 0), de(s["factor"], 2), de(s["points"], 2), s["deduction"] or "–"]
                                     for s in sk["subcriteria"]])
        base = {a["area"]: a for a in d.j("audit/v2_to_v3_mapping.json")["baseline"]["areas"]}
        rows = []
        for a2 in sk["areas"]:
            b2 = base[a2["id"]]
            main = max((s for s in sk["subcriteria"] if s["area"] == a2["id"]), key=lambda s: (s["max"] - s["points"], s["id"]))
            rows.append([a2["id"], a2["name"], de(a2["max"], 0), de(b2["v2_independent"], 1), de(a2["points"], 2), b2["main_deficit"],
                         f"{main['id']}: {main['deduction'] or '–'}"])
        rows.append(["", "Summe", "100", de(sum(b2["v2_independent"] for b2 in base.values()), 1), de(sk["total"], 2), "", ""])
        T["tab.score_compare"] = md_table(["Bereich", "Name", "Pkt.", "v2.0 unabhängig (§3.4)", "v3.0 Selbstbewertung", "Hauptmangel v2.0",
                                           "größter Abzug v3.0"], rows)
    if (d.root / "audit/scorecard_E.json").exists():
        se = d.j("audit/scorecard_E.json")
        T["tab.score_e"] = md_table(["Baustein", "Pkt.", "Nachweis nach §20.3", "Tore", "Punkte", "Stand"],
                                    [[b["id"], de(b["max"], 0), b["requirement"], ", ".join(b["gates"]), de(b["points"], 0), b["status"]] for b in se["blocks"]])
    mc = d.j("validation/mutation_catalog.json")
    T["tab.check_limits"] = md_table(["ID", "Bekannte Prüfgrenze"], [[x["id"], x["text"]] for x in mc["known_limits"]])
    cats = {}
    for x in mc["mutations"]:
        cats[x["category"]] = cats.get(x["category"], 0) + 1
    T["tab.mutation_categories"] = md_table(["Kategorie", "Mutationen", "Beispiele"],
                                            [[c, str(n), "; ".join(x["title"] for x in mc["mutations"] if x["category"] == c)[:220]]
                                             for c, n in sorted(cats.items())])
    mon = d.j(RESULTS["mon"])
    names = {"SCHAEDLICH": "schädlich", "STARK_SCHAEDLICH": "stark schädlich (Harm-Screen)", "WERTLOS": "wertlos", "BRAUCHBAR": "brauchbar"}
    rows = [["MON-HARM (MH-R1)", f"{names[k]}, wahre Sharpe {de(v['true_sharpe'], 1)}",
             (de(v["median_months"], 0) + " Monate") if v["median_months"] <= mon["harm_max_months"] else f"über {mon['harm_max_months']} Monate",
             de(v["p_trigger_within_pilot"] * 100, 1) + " % (Pilot)", de(v["p_trigger_within_24m"] * 100, 1) + " % (24 M)",
             de(v["p_trigger_within_60m"] * 100, 1) + " % (60 M)"]
            for k, v in mon["harm"].items()]
    rows += [["MON-DRIFT (MD-R3)", f"Volatilität ×{de(v['true_ratio'], 1)}",
              (de(v["median_days"], 0) + " Handelstage") if v["median_days"] <= mon["vol_horizon_days"] else f"über {mon['vol_horizon_days']} Handelstage",
              de(v["p_trigger_within_20d"] * 100, 1) + " % (20 T)", de(v["p_trigger_within_63d"] * 100, 1) + " % (63 T)",
              de(v["p_trigger_within_252d"] * 100, 1) + " % (252 T)"] for v in mon["vol_drift"].values()]
    T["tab.vol_design"] = md_table(["Fenster (Handelstage)", "Band", "Fehlalarm im Jahr ohne Drift", "Verdopplung: Median bis Auslösung", "Verdopplung: erkannt in 63 Tagen"],
                                   [[str(g["window_days"]), de(g["band"] * 100, 0) + " %", de(g["false_alarm_within_252d"] * 100, 1) + " %",
                                     de(g["doubling_median_days"], 0) + " Handelstage", de(g["doubling_within_63d"] * 100, 1) + " %"]
                                    for g in mon["vol_design_grid"]])
    T["tab.monitor_triggers"] = md_table(["Monitor", "Lage", "Median bis Auslösung", "P(Auslösung) kurz", "P(Auslösung) mittel", "P(Auslösung) lang"], rows)
    T["tab.margin"] = md_table(["Allokation", "Profil", "M/E (Anteil NAV)", "M/E +100 %", "Margin-Level am Broker ohne Verlust",
                                "Margin-Level nach schlimmstem Szenario", "Verlust bis De-Risking-Schwelle (Margin +100 %)",
                                "Verlust bis Stop-out (Margin +100 %)", "nötiger Anteil beim Broker", "Anteil beim Broker reicht",
                                "Szenarien mit Liquidation"], rows)
    return T


# ------------------------------------------------------------------------------------------------ Rendern
def render_text(text: str, d: Data, T: dict, errors: list, fname: str) -> str:
    def vrep(m):
        try:
            return f"<!--v:{m.group(1)}-->{resolve(d, m.group(1))}<!--/v-->"
        except Exception as ex:  # noqa: BLE001
            errors.append(f"{fname}: Wert {m.group(1)}: {ex.__class__.__name__}: {ex}")
            return m.group(0)

    def brep(m):
        name = m.group(2)
        if name not in T:
            errors.append(f"{fname}: unbekannter Block {name}")
            return m.group(0)
        return m.group(1) + T[name] + "\n" + m.group(4)

    return VALUE_RE.sub(vrep, BLOCK_RE.sub(brep, text))


def markdown_files(root: Path):
    return sorted(p for p in root.rglob("*.md") if "research/sources" not in p.as_posix())


def used_in(root: Path, ids) -> dict:
    out = {i: set() for i in ids}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if not p.is_file() or rel in DERIVED or rel.startswith("research/sources/") or p.suffix not in (".md", ".json", ".py", ".csv"):
            continue
        if rel in ("registers/source_register.json", "parameters.json"):
            continue
        text = p.read_text(encoding="utf-8")
        for m in set(ID_RE.findall(text)):
            if m in out:
                out[m].add(rel)
    return {k: sorted(v) for k, v in out.items()}


def traceability(d: Data) -> dict:
    tr = {"schema_version": "3.0", "document": "Rückverfolgbarkeit (abgeleitet)", "requirements": [], "findings": [], "parameters_unused": [], "sources_unused": []}
    if (d.root / "requirements.json").exists():
        tests = {t["id"]: t for t in d.j("implementation/test_catalog.json")["tests"]} if (d.root / "implementation/test_catalog.json").exists() else {}
        for r in d.j("requirements.json")["requirements"]:
            tr["requirements"].append({"id": r["id"], "tests": r["tests"], "tests_known": all(t in tests for t in r["tests"]), "stage": r["stage"],
                                       "status": r["status"], "basis": r["basis"]})
    if (d.root / "registers/resolution_matrix.json").exists():
        for f in d.j("registers/resolution_matrix.json")["findings"]:
            tr["findings"].append({"id": f["id"], "status": f["status"], "evidence": f["evidence"]})
    if (d.root / "implementation/test_catalog.json").exists():
        tr["tests_unreferenced"] = sorted(t["id"] for t in d.j("implementation/test_catalog.json")["tests"] if not t["requirements"] and not t["scenarios"])
    if (d.root / "architecture/scenario_catalog.json").exists():
        tr["scenarios_without_test"] = sorted(s["id"] for s in d.j("architecture/scenario_catalog.json")["scenarios"] if not s["tests"])
    return tr


def run(root: Path, check: bool) -> int:
    d = Data(root)
    T = gen_tables(d)
    errors, changed = [], []
    for p in markdown_files(root):
        rel = p.relative_to(root).as_posix()
        old = p.read_text(encoding="utf-8")
        new = render_text(old, d, T, errors, rel)
        if new != old:
            changed.append(rel)
            if not check:
                p.write_text(new, encoding="utf-8")
    # abgeleitete Register
    src = d.j("registers/source_register.json")
    ui = used_in(root, [s["id"] for s in src["sources"]])
    for s in src["sources"]:
        s["used_in"] = ui[s["id"]]
    prm = d.j("parameters.json")
    up = used_in(root, [x["id"] for x in prm["parameters"]])
    for x in prm["parameters"]:
        x["used_in"] = up[x["id"]]
    tr = traceability(d)
    tr["parameters_unused"] = sorted(k for k, v in up.items() if not v)
    tr["sources_unused"] = sorted(k for k, v in ui.items() if not v)
    for rel, obj in [("registers/source_register.json", src), ("parameters.json", prm), ("registers/traceability.json", tr)]:
        text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
        p = root / rel
        old = p.read_text(encoding="utf-8") if p.exists() else ""
        if text != old:
            changed.append(rel)
            if not check:
                p.write_text(text, encoding="utf-8")
    for e in errors:
        print("FEHLER", e)
    if check and changed:
        print("ABWEICHUNG in", ", ".join(changed))
    print("render_blocks:", "PRÜFUNG" if check else "GESCHRIEBEN", f"{len(changed)} Dateien abweichend" if check else f"{len(changed)} Dateien aktualisiert",
          f"{len(errors)} Fehler")
    return 1 if errors or (check and changed) else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    return run(Path(a.root).resolve(), a.check)


if __name__ == "__main__":
    sys.exit(main())
