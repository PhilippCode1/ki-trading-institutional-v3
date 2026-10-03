"""Kosten je Baustufe (Decimal) aus implementation/build_stages.json, registers/costs.json (über financials/cost_model_results.json) und parameters.json.

Eine Quelle der Wahrheit für Aufbaukosten (§5.4): Personentage × P-ECO-HOURS-PER-PERSON-DAY × Stundensatz, Coding-Agent-Abo über die Aufbaudauer,
laufende Infrastruktur-, Daten- und KI-Kosten während der Stufe, einmalige Posten der Stufe und – in Stufen mit laufendem Handel (Kostenposten
operator_routines: Paper, Pilot, Standardbetrieb) – die Betreiberroutinen (ops_hours) über die Stufendauer. Wird von der Betriebscharakteristik
und der Entscheidungs-Monte-Carlo importiert.
"""
from __future__ import annotations

from decimal import Decimal

from lib.calc import Params, dec, load, money

WEEKS_PER_MONTH = Decimal("4.345")


def ops_hours(P) -> Decimal:
    """Betreiberstunden je Jahr: Routinen (P-OPS-*) plus Pflege des KI-Agenten (höchstens ein Update je P-AI-UPDATE-MIN-DAYS, §11.3)."""
    m = (dec(P("P-OPS-DAILY-MIN")) * 252 + dec(P("P-OPS-WEEKLY-MIN")) * 52 + dec(P("P-OPS-MONTHLY-MIN")) * 12 + dec(P("P-OPS-INCIDENT-MIN")) * 12
         + dec(P("P-OPS-QUARTERLY-MIN")) * 4)
    ai_updates = (Decimal(365) / dec(P("P-AI-UPDATE-MIN-DAYS"))).to_integral_value(rounding="ROUND_FLOOR")
    return m / 60 + ai_updates * dec(P("P-AI-UPDATE-EFFORT-H"))


def fixed_monthly(fc, P, data_scenario: str = "ANZEIGE") -> Decimal:
    """Laufende Monatskosten ohne Handelskosten: Infrastruktur, Marktdaten (Szenario), KI-Abo (Basisstufe)."""
    ai = dec(fc["ai_subscription_monthly_eur"][P("P-AI-PORTAL-TIER")])
    return dec(fc["infrastructure_monthly_eur"]) + dec(fc["market_data_monthly_eur"][data_scenario]["monthly_eur"]) + ai


def stage_costs(case: str = "base", rate=None, data_scenario: str = "ANZEIGE") -> dict:
    P = Params()
    fc = load("financials/cost_model_results.json")["fixed_costs"]
    bs = load("implementation/build_stages.json")["stages"]
    hourly = dec(rate if rate is not None else P("P-ECO-HOURLY-RATE"))
    monthly_run = fixed_monthly(fc, P, data_scenario)
    ci = {"historical_data_once_eur": dec(fc["historical_data_once_eur"]), "hardware_keys_once_eur": dec(fc["hardware_keys_once_eur"]),
          "external_once_eur.pentest": dec(fc["external_once_eur"]["pentest"]), "external_once_eur.audit": dec(fc["external_once_eur"]["audit"])}
    idx = {"low": 0, "base": 1, "high": 2}[case]
    out = {}
    for s in bs:
        e = s["effort"][case]
        months = dec(s["duration_weeks"][idx]) / WEEKS_PER_MONTH
        human = dec(e["person_days"]) * dec(P("P-ECO-HOURS-PER-PERSON-DAY")) * hourly
        agent = dec(fc["coding_agent_monthly_eur"]) * months if "coding_agent_monthly_eur" in s["cost_items"] else Decimal(0)
        once = sum((ci[k] for k in s["cost_items"] if k in ci), Decimal(0))
        running = monthly_run * months if s["id"] not in ("BS-00",) else Decimal(0)
        risk_fn = dec(fc["external_risk_function_monthly_eur"]) * months if "external_risk_function_monthly_eur" in s["cost_items"] else Decimal(0)
        routines = ops_hours(P) * months / 12 * hourly if "operator_routines" in s["cost_items"] else Decimal(0)
        out[s["id"]] = {"gate": s["gate"], "months": money(months), "human_eur": money(human), "agent_eur": money(agent), "once_eur": money(once),
                        "running_eur": money(running), "external_risk_function_eur": money(risk_fn), "operator_routines_eur": money(routines),
                        "total_eur": money(human + agent + once + running + risk_fn + routines)}
    return out


def build_cost_until(stage_id: str, costs: dict) -> Decimal:
    """Summe der Kosten aller Stufen bis einschließlich stage_id (kritischer Pfad in ID-Reihenfolge)."""
    tot = Decimal(0)
    for sid in sorted(costs):
        tot += dec(costs[sid]["total_eur"])
        if sid == stage_id:
            break
    return tot
