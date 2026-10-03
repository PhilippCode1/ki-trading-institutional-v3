#!/usr/bin/env python3
"""Semantische Querprüfungen des Konzeptpakets v3.0 (§19.2, Phase P09 der Paketprüfung).

Jede Prüffunktion rechnet mit eigenen Formeln aus den Registern nach und vergleicht mit den gespeicherten Rechnerergebnissen oder mit
den Regeln anderer Register. Sie liefert eine Liste von Befunden (leer = bestanden). Nur Standardbibliothek.

  check_costs      Kosten ↔ Spreads ↔ Gebührentabelle; Verbraucher nutzen den aktuellen Kostenstand (EV-01, R-04)
  check_leverage   Hebel ↔ Volatilität ↔ Margin ↔ Limits; Profilzulässigkeit und Go/No-Go (§7.4, R-06)
  check_stress     Stressergebnisse vollständig je Allokation und Profil, Kennzahlen konsistent (§7.9)
  check_tax        Steuer-Sensitivität (§5.3, BQ-03)
  check_capacity   Kapazität ↔ Tagesvolumen (§6.2, §7.5)
  check_proxy      Proxy-Regel und Historie (§6.5, EV-08)
  check_limits     Limits ↔ Parameter ↔ Leitern (§7.5)
  check_runbooks   Runbook-Abdeckung aller Szenarien, Killer-Tests, HA-Ereignisse und Sperrgründe (§14)
  check_gates      Tore ↔ Betriebscharakteristik ↔ externe Eingaben ↔ Bauprogramm; Torfälle mit heutigen Werten (§16)
  check_operator   Betreiberangaben versiegelt, externe Eingaben nur mit Nachweis bestätigt (R-07)
  check_scores     Selbstbewertung K und E: Punkte nur mit Nachweis, E nur mit signiertem Laufbeleg, K ≤ 99 ohne Gegenprüfung (R-08, §20)

Aufruf:  python validation/semantic_checks.py --root . [--only check_costs,check_stress] [--json]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.calc import variant_decision  # noqa: E402  (eine Regel für Variantenbefunde, R-04)

PROFILES = ("H5", "H10", "H15", "H20")
FACTORS = (0, 0.25, 0.5, 0.75, 1)
TOL = 1e-9


class Pkg:
    """Lesezugriff auf das Paket mit Zwischenspeicher."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self._c = {}

    def j(self, rel: str):
        if rel not in self._c:
            self._c[rel] = json.loads((self.root / rel).read_text(encoding="utf-8"))
        return self._c[rel]

    def exists(self, rel: str) -> bool:
        return (self.root / rel).exists()

    @property
    def P(self) -> dict:
        return {p["id"]: p["value"] for p in self.j("parameters.json")["parameters"]}

    @property
    def INS(self) -> dict:
        return {i["id"]: i for i in self.j("registers/instruments.json")["instruments"]}

    @property
    def COST(self) -> dict:
        return {c["id"]: c for c in self.j("registers/costs.json")["costs"]}


def pointer(doc, ptr: str):
    """JSON-Pointer (RFC 6901, ohne Escapes außer ~0/~1)."""
    cur = doc
    for part in [p for p in ptr.split("/") if p != ""]:
        part = part.replace("~1", "/").replace("~0", "~")
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur


def content_hash(pkg: Pkg, rel: str) -> str:
    """Inhalts-Hash wie lib/calc.sha256_content: JSON kanonisch ohne abgeleitete Felder used_in."""
    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items() if k != "used_in"}
        if isinstance(o, list):
            return [strip(v) for v in o]
        return o
    if rel.endswith(".json"):
        canon = json.dumps(strip(pkg.j(rel)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canon.encode("utf-8")).hexdigest()
    return hashlib.sha256((pkg.root / rel).read_bytes()).hexdigest()


def close(a: float, b: float, rel: float = 1e-9, ab: float = 1e-12) -> bool:
    return abs(a - b) <= max(ab, rel * max(abs(a), abs(b)))


# ================================================================================================================ Kosten
def check_costs(pkg: Pkg) -> list:
    """Kosten je Kontrakt aus Registern nachrechnen: Kommission + halber Spread + Schlupf je Seite; Round-Turn in EUR und bp;
    Kosten je Risikoeinheit. Vergleich mit financials/cost_model_results.json und financials/cost_table.csv."""
    out = []
    P, C, INS = pkg.P, pkg.COST, pkg.INS
    res = {r["id"]: r for r in pkg.j("financials/cost_model_results.json")["instruments"]}
    fx = {"EUR": 1.0, "USD": float(P["P-ECO-EURUSD"]), "GBP": float(P["P-ECO-EURGBP"])}
    comm = float(C["COST-COMM-FXFLAT"]["amount"])
    slip = float(C["COST-EXEC-SLIP-TICKS"]["amount"])
    if C["COST-COMM-FXFLAT"]["status"] not in ("BELEGT", "TEILWEISE") or not C["COST-COMM-FXFLAT"]["source"]:
        out.append("COST-COMM-FXFLAT: Gebühr ohne belegte Quelle")
    if set(res) != set(INS):
        out.append(f"Kostenmodell und Instrumentregister decken verschiedene Instrumente ab: {sorted(set(res) ^ set(INS))[:6]}")
    # Eine Quelle der Wahrheit (R-04, Regel in registers/costs.json): nur das Kostenmodell liest das Kostenregister
    for f in sorted(list(pkg.root.glob("financials/*.py")) + list(pkg.root.glob("research/**/*.py")) + list(pkg.root.glob("risk/*.py"))
                    + list(pkg.root.glob("operations/*.py"))):
        rel = f.relative_to(pkg.root).as_posix()
        if rel == "financials/cost_model.py":
            continue
        src = re.sub(r"(?m)#.*$", "", f.read_text(encoding="utf-8"))
        if re.search(r"[\"']registers/costs\.json[\"']|\bcosts\(\)", src):
            out.append(f"{rel}: liest das Kostenregister direkt statt financials/cost_model_results.json (R-04)")
    csv_rows = {}
    csv_path = pkg.root / "financials/cost_table.csv"
    if csv_path.exists():
        with csv_path.open(encoding="utf-8", newline="") as fh:
            csv_rows = {row["id"]: row for row in csv.DictReader(fh, delimiter=";")}
    for iid, ins in INS.items():
        r = res.get(iid)
        if r is None:
            continue
        f = fx[ins["currency"]]
        price = float(ins["planning"]["price"]["value"])
        mult = float(ins["multiplier"])
        tv = float(ins["tick_value"])
        spread = float(ins["planning"]["spread_ticks"]["value"])
        notional = mult * price / f
        half = spread / 2 * tv / f
        sl = slip * tv / f
        side = comm + half + sl
        rt = 2 * side
        bp = rt / notional * 1e4
        vol = notional * ins["planning"]["vol_annual_pct"]["base"] / 100
        checks = [("halber Spread je Seite", half, float(r["half_spread_side_eur"]), 0.005),
                  ("Schlupf je Seite", sl, float(r["slippage_side_eur"]), 0.005),
                  ("Kommission je Seite", comm, float(r["commission_side_eur"]), 0.005),
                  ("Round-Turn EUR", rt, float(r["cost_rt_eur"]), 0.011),
                  ("Nominal EUR", notional, float(r["notional_eur"]), 0.005 + 1e-9 * notional)]
        for name, mine, stored, tol in checks:
            if abs(mine - stored) > tol:
                out.append(f"{ins['symbol']}: {name} nachgerechnet {mine:.4f} ≠ gespeichert {stored:.4f} (Spread, Gebühr oder Kurs ohne Neuberechnung geändert)")
        if not close(bp, float(r["cost_rt_bp"]), rel=1e-6):
            out.append(f"{ins['symbol']}: Round-Turn {bp:.4f} bp ≠ gespeichert {float(r['cost_rt_bp']):.4f} bp")
        if not close(rt / vol, float(r["c_rt_sr"]["base"]), rel=1e-6):
            out.append(f"{ins['symbol']}: Kosten je Risikoeinheit {rt / vol:.6f} ≠ gespeichert {r['c_rt_sr']['base']:.6f}")
        row = csv_rows.get(iid)
        if csv_rows and (row is None or abs(float(row["rt_kosten_eur"]) - float(r["cost_rt_eur"])) > 0.005):
            out.append(f"{ins['symbol']}: financials/cost_table.csv weicht vom Kostenmodell ab")
    # Verbraucher des Kostenmodells müssen den aktuellen Stand gerechnet haben (eine Quelle der Wahrheit)
    h = content_hash(pkg, "financials/cost_model_results.json")
    for rel in ("research/prior_results.json", "risk/leverage_results.json", "research/operating_characteristics_results.json",
                "financials/decision_montecarlo_results.json"):
        stored = pkg.j(rel).get("inputs", {}).get("financials/cost_model_results.json")
        if stored is not None and stored != h:
            out.append(f"{rel}: rechnet mit einem veralteten Kostenmodell (Eingangs-Hash abweichend)")
    return out


# ================================================================================================================ Hebel
def check_leverage(pkg: Pkg) -> list:
    """Hebelzellen gegen Profilgrenzen, Lückenbudget, Margin- und ES-Limits nachprüfen; Zulässigkeit neu ableiten; Profilparameter
    geordnet und unter der Betreibergrenze; unzulässige Profile nie mit Echtgeld-Go."""
    out = []
    P = pkg.P
    L = pkg.j("risk/leverage_results.json")
    lev_max = float(P["P-OP-LEV-MAX"])
    budget = float(P["P-OP-DAILY-LOSS-CAP"]) - float(P["P-RISK-GAP-RESERVE"])
    if not close(float(L["gap_budget"]), budget):
        out.append(f"Lückenbudget {L['gap_budget']} ≠ Tagesgrenze − Reserve {budget}")
    wf = float(P["P-RISK-WEEKEND-FACTOR"])
    if not close(float(L.get("weekend_factor", 1.0)), wf) or wf < 1:
        out.append(f"Hebelrechner rechnet ohne den Wochenendfaktor P-RISK-WEEKEND-FACTOR {wf} (DEC-DS-10)")
    prev = None
    for prof in PROFILES:
        cap, sig, me, es = (float(P[f"P-LEV-{prof}-{k}"]) for k in ("CAP", "SIGMA", "ME", "ES"))
        if cap > lev_max + TOL:
            out.append(f"P-LEV-{prof}-CAP {cap} liegt über der Betreibergrenze P-OP-LEV-MAX {lev_max}")
        if prev and not (cap > prev[0] and sig > prev[1] and me >= prev[2] and es >= prev[3]):
            out.append(f"Profil {prof}: Grenzen nicht aufsteigend gegenüber dem vorigen Profil")
        prev = (cap, sig, me, es)
    derisk_me = float(P["P-ECO-CASH-AT-BROKER"]) / float(P["P-MRG-DERISK-TRIGGER"])   # Margin deckt nur das Guthaben beim Broker
    for var, stages in L["cells"].items():
        for st, profs in stages.items():
            for prof in PROFILES:
                c = profs.get(prof)
                tag = f"{var}/{st}/{prof}"
                if c is None:
                    out.append(f"{tag}: Hebelzelle fehlt")
                    continue
                if c["n"] == 0:
                    if c["admissible"] or not c["reasons"]:
                        out.append(f"{tag}: leeres Universum ohne Unzulässigkeitsbefund")
                    continue
                cap = float(P[f"P-LEV-{prof}-CAP"])
                sig_t = float(P[f"P-LEV-{prof}-SIGMA"])
                if not close(c["sigma_target"], sig_t):
                    out.append(f"{tag}: σ-Ziel {c['sigma_target']} ≠ P-LEV-{prof}-SIGMA {sig_t}")
                if not close(c["scale"], min(c["scale_gap"], c["scale_cap"])):
                    out.append(f"{tag}: Skalierung ≠ Minimum aus Lückenregel und Profilgrenze")
                if not close(c["sigma_achieved"], c["sigma_target"] * c["scale"], rel=1e-7):
                    out.append(f"{tag}: σ erreicht ≠ σ-Ziel × Skalierung")
                if not close(c["L_g_achieved"], c["L_g_at_target"] * c["scale"], rel=1e-7):
                    out.append(f"{tag}: L_g erreicht ≠ L_g am Ziel × Skalierung")
                if not close(c["L_g_at_target"], c["D"] * c["sigma_target"] / c["sigma_h"], rel=1e-6):
                    out.append(f"{tag}: L_g ≠ D·σ_p/σ_h")
                if c["L_g_achieved"] > cap + 1e-9 or c["L_g_achieved"] > lev_max + 1e-9:
                    out.append(f"{tag}: L_g {c['L_g_achieved']:.3f} über Profilgrenze {cap} oder Betreibergrenze {lev_max}")
                if wf * c["gap_loss_achieved"]["DESIGN"] > budget + 1e-9:
                    out.append(f"{tag}: Lückenstress × Wochenendfaktor {wf * c['gap_loss_achieved']['DESIGN']:.4f} über dem Budget {budget}")
                viol = []
                if prof == "H5":
                    if c["sigma_achieved"] < float(P["P-LEV-H5-SIGMA-MIN"]) - TOL:
                        viol.append("σ")
                elif c["scale_gap"] < float(P["P-LEV-SIGMA-TOLERANCE"]) - TOL:
                    viol.append("σ")
                if c["effective_n"] < float(P[f"P-LEV-{prof}-MINDIV"]) - TOL:
                    viol.append("Diversifikation")
                if c["es_1d_parametric"] > float(P[f"P-LEV-{prof}-ES"]) + TOL:
                    viol.append("ES")
                if c["margin_to_equity"]["basis"] > float(P[f"P-LEV-{prof}-ME"]) + TOL:
                    viol.append("M/E")
                if c["margin_to_equity"]["plus100"] > derisk_me + TOL:
                    viol.append("Margin-Pfad")
                if c["admissible"] != (not viol):
                    out.append(f"{tag}: Zulässigkeit {c['admissible']} widerspricht den Grenzen (verletzt: {viol or 'keine'})")
                if not c["admissible"] and len(c["reasons"]) != len(viol):
                    out.append(f"{tag}: {len(c['reasons'])} Gründe genannt, {len(viol)} Verletzungen nachgerechnet")
    # Profilzulässigkeit ↔ Entscheidungsrechnung und Go/No-Go
    dmc = pkg.j("financials/decision_montecarlo_results.json")
    for var, stages in dmc["table"].items():
        for st, profs in stages.items():
            for prof, cell in profs.items():
                lc = L["cells"].get(var, {}).get(st, {}).get(prof)
                if lc is not None and not lc["admissible"] and cell["class"] != "PROFILE_NOT_ADMISSIBLE":
                    if not (lc["n"] == 0 and cell["class"] in ("NOT_VIABLE_AT_CAPITAL", "PROFILE_NOT_ADMISSIBLE")):
                        out.append(f"{var}/{st}/{prof}: Profil unzulässig, Befundklasse aber {cell['class']}")
    for st, profs in dmc["go_no_go"].items():
        for prof, g in profs.items():
            lc = L["cells"]["U-KOSTEN"].get(st, {}).get(prof)
            if g["decision_real_money"] != "NO_GO" and (lc is None or not lc["admissible"]):
                out.append(f"Go/No-Go {st}/{prof}: Echtgeld nicht No-Go, obwohl das Profil unzulässig ist")
    return out


# ================================================================================================================ Stress
def check_stress(pkg: Pkg) -> list:
    """Jede Allokation × Profil hat jedes Szenario aus risk/stress_scenarios.json mit Zahlenwerten; schlimmstes Szenario, Grenzverletzungen
    und Liquidationen folgen aus den Einzelwerten."""
    out = []
    P = pkg.P
    Z = pkg.j("risk/stress_scenarios.json")
    ids = {s["id"] for s in Z["historical"]} | {s["id"] for s in Z["hypothetical"]}
    S = pkg.j("risk/stress_results.json")
    if S.get("scenario_count") != len(ids):
        out.append(f"scenario_count {S.get('scenario_count')} ≠ {len(ids)} Szenarien im Register")
    if S.get("complete") is not True:
        out.append("Stressergebnisse nicht als vollständig gekennzeichnet")
    if str(S.get("reference_stage")) != str(P["P-RISK-STRESS-REF-STAGE"]):
        out.append("Referenzstufe der Stressergebnisse ≠ P-RISK-STRESS-REF-STAGE")
    dlc = float(P["P-OP-DAILY-LOSS-CAP"])
    for kind in ("SYSTEM", "ALTERNATIVE_TFD1", "WUNSCHHEBEL"):
        if kind not in S["results"]:
            out.append(f"Allokation {kind} fehlt")
            continue
        for prof in PROFILES:
            r = S["results"][kind].get(prof)
            if r is None:
                out.append(f"{kind}/{prof}: Ergebnis fehlt")
                continue
            sc = r["scenarios"]
            missing = sorted(ids - set(sc))
            if missing:
                out.append(f"{kind}/{prof}: Szenarien ohne Ergebnis {missing}")
            extra = sorted(set(sc) - ids)
            if extra:
                out.append(f"{kind}/{prof}: Ergebnisse ohne Szenario {extra}")
            bad = [k for k, v in sc.items() if not all(isinstance(v.get(f), (int, float)) and math.isfinite(v.get(f))
                                                        for f in ("loss_day1", "loss_no_ladder", "loss_with_ladder"))]
            if bad:
                out.append(f"{kind}/{prof}: Verlustwerte fehlen oder ungültig in {bad}")
                continue
            if not sc:
                continue
            worst = max(sc, key=lambda k: (sc[k]["loss_with_ladder"], k))
            if r["worst_scenario"] != worst or not close(r["worst_loss_with_ladder"], sc[worst]["loss_with_ladder"]):
                out.append(f"{kind}/{prof}: schlimmstes Szenario {r['worst_scenario']} ≠ nachgerechnet {worst}")
            breaches = sorted(k for k, v in sc.items() if v["loss_day1"] > dlc)
            if sorted(r["daily_cap_breaches"]) != breaches or any(sc[k]["daily_cap_breach"] != (k in breaches) for k in sc):
                out.append(f"{kind}/{prof}: Verletzungen der Tagesgrenze nicht aus den Tagesverlusten abgeleitet")
            liq = sorted(k for k, v in sc.items() if v["liquidation_status"] == "LIQUIDATION")
            if sorted(r["liquidations"]) != liq:
                out.append(f"{kind}/{prof}: Liquidationsliste weicht ab")
            phi, trig = float(P["P-ECO-CASH-AT-BROKER"]), float(P["P-MRG-DERISK-TRIGGER"])
            for k, v in sc.items():
                if v["loss_with_ladder"] > v["loss_no_ladder"] + 1e-12:
                    out.append(f"{kind}/{prof}/{k}: Verlust mit Leiter größer als ohne")
                if v["me_peak"] > 0 and not close(v["margin_level_after"], max(0.0, phi - v["loss_with_ladder"]) / v["me_peak"], rel=1e-9):
                    out.append(f"{kind}/{prof}/{k}: Margin-Level nicht auf das Guthaben beim Broker bezogen")
                if not close(v["broker_share_required"], v["loss_with_ladder"] + trig * v["me_peak"], rel=1e-9):
                    out.append(f"{kind}/{prof}/{k}: nötiger Brokeranteil weicht ab")
            need = max(v["broker_share_required"] for v in sc.values())
            if not close(r["broker_share_required"], need, rel=1e-9) or r["broker_share_sufficient"] != (need <= phi):
                out.append(f"{kind}/{prof}: nötiger Brokeranteil oder Befund „reicht“ weicht ab")
            for s in Z["historical"]:
                if s.get("halt") and s["id"] in sc and sc[s["id"]]["flattened_by_ladder"] and \
                        sc[s["id"]].get("halted_share_of_loss", 0) > 0 and sc[s["id"]]["ladder_effect"] >= sc[s["id"]]["loss_no_ladder"] - 1e-12:
                    out.append(f"{kind}/{prof}/{s['id']}: Leiter baut trotz Handelsaussetzung alles ab")
    return out


# ================================================================================================================ Steuern
def check_tax(pkg: Pkg) -> list:
    """Steuer-Sensitivität kürzt nur positive Jahreswerte um P-ECO-TAX-SENS; Umfang nach BQ-03 (keine Beratung); jede Zelle der
    Entscheidungsrechnung trägt die Sensitivität."""
    out = []
    P = pkg.P
    T = pkg.j("financials/tax_sensitivity_example.json")
    rate = float(P["P-ECO-TAX-SENS"])
    if not close(float(T["rate"]), rate):
        out.append(f"Steuersatz der Sensitivität {T['rate']} ≠ P-ECO-TAX-SENS {rate}")
    if T.get("external_input") != "X-TAX-01":
        out.append("Steuer-Sensitivität ohne Verweis auf die externe Eingabe X-TAX-01")
    for ex in T["examples"]:
        b, a = float(ex["before_eur"]), float(ex["after_sensitivity_eur"])
        want = b * (1 - rate) if b > 0 else b
        if abs(a - want) > 0.005:
            out.append(f"Steuerbeispiel {b}: {a} ≠ {want:.2f}")
    xin = {x["id"]: x for x in pkg.j("external_inputs.json")["inputs"]}
    if "GATE-G8" not in xin.get("X-TAX-01", {}).get("blocks", []):
        out.append("X-TAX-01 sperrt G8 nicht")
    dmc = pkg.j("financials/decision_montecarlo_results.json")
    for var, stages in dmc["table"].items():
        for st, profs in stages.items():
            for prof, cell in profs.items():
                if "base" in cell and "STEUER_SENSITIVITAET" not in cell.get("sensitivities", {}):
                    out.append(f"{var}/{st}/{prof}: Steuer-Sensitivität fehlt")
    return out


# ================================================================================================================ Kapazität
def check_capacity(pkg: Pkg) -> list:
    """Zugelassene Instrumente haben mindestens P-UNI-MIN-ADV Tagesvolumen; die Ordergröße nach Kapazitätsfaktor bleibt je Instrument
    unter P-RISK-MAX-ADV-SHARE des Tagesvolumens; der Kapazitätsfaktor verkleinert die wirksame Volatilität."""
    out = []
    P, INS = pkg.P, pkg.INS
    prior = pkg.j("research/prior_results.json")
    L = pkg.j("risk/leverage_results.json")
    dmc = pkg.j("financials/decision_montecarlo_results.json")
    cm = {r["id"]: r for r in pkg.j("financials/cost_model_results.json")["instruments"]}
    share = float(P["P-RISK-MAX-ADV-SHARE"])
    min_adv = float(P["P-UNI-MIN-ADV"])
    for var, stages in prior["admission"].items():
        for st, a in stages.items():
            for i in a["instruments"]:
                if INS[i]["planning"]["adv_contracts"]["value"] < min_adv and var != "U-HANDELBAR":
                    out.append(f"{var}/{st}: {i} unter dem Mindest-Tagesvolumen P-UNI-MIN-ADV")
    for var, stages in dmc["table"].items():
        for st, profs in stages.items():
            ids = prior["admission"][var][st]["instruments"]
            for prof, cell in profs.items():
                if not ids or "capacity_factor" not in cell:
                    continue
                lc = L["cells"][var][st][prof]
                cf = cell["capacity_factor"]
                if not (0 < cf <= 1 + TOL):
                    out.append(f"{var}/{st}/{prof}: Kapazitätsfaktor {cf} außerhalb (0, 1]")
                    continue
                if not close(cell["sigma_effective"], lc["sigma_achieved"] * min(1.0, cf), rel=1e-7):
                    out.append(f"{var}/{st}/{prof}: wirksame Volatilität ≠ σ erreicht × Kapazitätsfaktor")
                n = len(ids)
                sig_t = float(P[f"P-LEV-{prof}-SIGMA"])
                for i in ids:
                    sig_i = INS[i]["planning"]["vol_annual_pct"]["base"] / 100
                    w = sig_t * lc["D"] * (1.0 / n) / sig_i * lc["scale"]
                    q = max(1.0, w * float(st) / float(cm[i]["notional_eur"]))
                    adv = INS[i]["planning"]["adv_contracts"]["value"]
                    if q * min(1.0, cf) > share * adv * (1 + 1e-6):
                        out.append(f"{var}/{st}/{prof}: {INS[i]['symbol']} Ordergröße {q * cf:.1f} über {share:.0%} des Tagesvolumens ({adv})")
    return out


# ================================================================================================================ Proxy
def check_proxy(pkg: Pkg) -> list:
    """Proxy nur auf denselben Basiswert (gleiche Risikoklasse und Währung, vorhandener Standardkontrakt, Micro/Mini → Standard);
    zugelassen nur mit eigener oder Proxy-Historie ≥ Entwicklungs- plus Holdout-Jahre; Ausschlussliste vollständig."""
    out = []
    P, INS = pkg.P, pkg.INS
    req = float(P["P-RES-DEV-YEARS"]) + float(P["P-RES-HOLDOUT-YEARS"])
    for i in INS.values():
        ref = i["standard_ref"]
        if not ref:
            continue
        s = INS.get(ref)
        if s is None:
            out.append(f"{i['symbol']}: Proxy {ref} fehlt im Register")
            continue
        if s["risk_class"] != i["risk_class"] or s["currency"] != i["currency"]:
            out.append(f"{i['symbol']}: Proxy {s['symbol']} mit anderer Risikoklasse oder Währung (anderer Basiswert, vgl. MTN ≠ ZN)")
        pa, pb = float(i["planning"]["price"]["value"]), float(s["planning"]["price"]["value"])
        if pb <= 0 or abs(pa / pb - 1) > float(P["P-DATA-PROXY-PRICE-TOL"]):
            out.append(f"{i['symbol']}: Proxy {s['symbol']} mit anderer Notierung ({pa} gegenüber {pb}; anderer Basiswert gleicher Klasse, PX-1)")
        if s["standard_ref"]:
            out.append(f"{i['symbol']}: Proxy {s['symbol']} ist selbst ein Proxy-Kontrakt")
        if s["size_class"] != "STANDARD":
            out.append(f"{i['symbol']}: Proxy {s['symbol']} ist kein Standardkontrakt")

    def hist(i):
        h = i["data_history"]["years_available"]
        if h < req and i["standard_ref"] in INS:
            h = max(h, INS[i["standard_ref"]]["data_history"]["years_available"])
        return h

    prior = pkg.j("research/prior_results.json")
    for var, stages in prior["admission"].items():
        if var == "U-HANDELBAR":
            continue
        for st, a in stages.items():
            for iid in a["instruments"]:
                if hist(INS[iid]) < req - TOL:
                    out.append(f"{var}/{st}: {iid} ohne ausreichende Historie ({hist(INS[iid]):.1f} < {req:.0f} Jahre)")
    rule = prior["admission_rule"]
    if not close(float(rule["min_history_years"]), req):
        out.append("Historienregel der Zulassung ≠ P-RES-DEV-YEARS + P-RES-HOLDOUT-YEARS")
    want = sorted(i["id"] for i in INS.values() if i["access"]["status"] == "PRIMAERBROKER_BOERSE_ANGEBOTEN" and not i["blocked"] and hist(i) < req)
    if sorted(rule["history_excluded"]) != want:
        out.append("Liste der wegen Historie ausgeschlossenen Instrumente weicht ab")
    return out


# ================================================================================================================ Limits
def check_limits(pkg: Pkg) -> list:
    """Limits verweisen auf vorhandene Parameter oder Ergebniswerte; Leitern streng geordnet und unter der Betreibergrenze;
    Leiterfaktoren abnehmend; Margin-Schwellen vor dem Stop-out des Brokers."""
    out = []
    P = pkg.P
    f = lambda k: float(P[k])  # noqa: E731
    dl = [f("P-RISK-DL-L1"), f("P-RISK-DL-L2"), f("P-RISK-DL-L3"), f("P-OP-DAILY-LOSS-CAP")]
    if not all(a < b for a, b in itertools.pairwise(dl)):
        out.append("Tagesverlust-Leiter nicht streng steigend bis zur Betreibergrenze")
    if not f("P-RISK-DL-L3") < f("P-OP-DAILY-LOSS-CAP") - f("P-RISK-GAP-RESERVE"):
        out.append("L3 liegt nicht unter Tagesgrenze minus Lückenreserve")
    dd = [f("P-RISK-DD-L1"), f("P-RISK-DD-L2"), f("P-RISK-DD-L3"), f("P-RISK-DD-KILL"), f("P-RISK-RUIN")]
    if not all(a < b for a, b in itertools.pairwise(dd)):
        out.append("Drawdown-Leiter nicht streng steigend bis zur Ruin-Definition")
    F = P["P-RISK-LADDER-FACTORS"]
    if not (0 < F["DL_L2"] <= F["DL_L1"] <= 1 and 0 < F["DD_L3"] <= F["DD_L2"] <= F["DD_L1"] <= 1):
        out.append("Leiterfaktoren nicht abnehmend in (0, 1]")
    if not f("P-MRG-DERISK-TRIGGER") > f("P-MRG-BROKER-STOPOUT"):
        out.append("De-Risking-Schwelle liegt nicht vor dem Stop-out des Brokers")
    if not 0 < f("P-RISK-GAP-RESERVE") < f("P-OP-DAILY-LOSS-CAP"):
        out.append("Lückenreserve außerhalb (0, Tagesgrenze)")
    lim = pkg.j("registers/limits.json")["limits"]
    refs = {x["value_ref"] for x in lim}
    for need in ("P-OP-DAILY-LOSS-CAP", "P-RISK-DL-L1", "P-RISK-DL-L2", "P-RISK-DL-L3", "P-RISK-DD-L1", "P-RISK-DD-L2", "P-RISK-DD-L3",
                 "P-RISK-DD-KILL", "P-RISK-WEEK-LOSS", "P-RISK-MAX-ADV-SHARE", "P-RISK-MAX-OI-SHARE"):
        if need not in refs:
            out.append(f"Limitregister ohne Grenze für {need}")
    for x in lim:
        ref = x["value_ref"]
        if ref.startswith("P-"):
            names = [ref.replace("{PROFIL}", prof) for prof in PROFILES] if "{PROFIL}" in ref else [ref]
            for n in names:
                if n not in P:
                    out.append(f"{x['id']}: Parameter {n} fehlt")
        elif "#" in ref:
            rel, anchor = ref.split("#", 1)
            if rel.endswith(".md"):
                if not pkg.exists(rel) or anchor not in (pkg.root / rel).read_text(encoding="utf-8"):
                    out.append(f"{x['id']}: Wertverweis {ref} nicht auflösbar")
                continue
            try:
                pointer(pkg.j(rel), anchor)
            except (KeyError, IndexError, ValueError, FileNotFoundError):
                out.append(f"{x['id']}: Wertverweis {ref} nicht auflösbar")
    return out


# ================================================================================================================ Runbooks
def check_runbooks(pkg: Pkg) -> list:
    """Jedes Stressszenario, jeder Killer-Test, jedes HA-Ereignis und jeder Sperrgrund hat mindestens ein Runbook; Drills existieren."""
    out = []
    rbs = pkg.j("operations/runbook_register.json")["runbooks"]
    drills = {d["id"] for d in pkg.j("operations/drill_register.json")["drills"]}
    cov = {"scenarios": set(), "killer_tests": set(), "ha_events": set(), "safety_reasons": set()}
    for r in rbs:
        for k in cov:
            cov[k] |= set(r[k])
        for d in r["drills"]:
            if d not in drills:
                out.append(f"{r['id']}: Drill {d} fehlt")
    Z = pkg.j("risk/stress_scenarios.json")
    for s in Z["historical"] + Z["hypothetical"]:
        if s["id"] not in cov["scenarios"]:
            out.append(f"Stressszenario {s['id']} ohne Runbook")
    for t in pkg.j("implementation/test_catalog.json")["tests"]:
        if t["id"].startswith("KT-") and t["id"] not in cov["killer_tests"]:
            out.append(f"Killer-Test {t['id']} ohne Runbook")
    for s in pkg.j("architecture/scenario_catalog.json")["scenarios"]:
        if s["id"].startswith("HA-") and s["id"] not in cov["ha_events"]:
            out.append(f"HA-Ereignis {s['id']} ohne Runbook")
    ms = {m["id"]: m for m in pkg.j("architecture/state_machines.json")["machines"]}
    for reason in ms["SM-SAFETY"]["reasons"]:
        rid = reason["id"] if isinstance(reason, dict) else reason
        if rid not in cov["safety_reasons"]:
            out.append(f"Sperrgrund {rid} ohne Runbook")
    return out


# ================================================================================================================ Tore
def _params_in(e, acc):
    if isinstance(e, dict):
        for k, v in e.items():
            if k == "param":
                acc.add(v if isinstance(v, str) else v[0])
            else:
                _params_in(v, acc)
    elif isinstance(e, list):
        for x in e:
            _params_in(x, acc)
    return acc


def check_gates(pkg: Pkg) -> list:
    """Tore und Monitore gegen Parameter, externe Eingaben, Bauprogramm, Betriebscharakteristik und E-Abbildung; Futility-Regel
    vorhanden und nicht umgehbar; Torfälle mit heutigen Werten aus den aktuellen Rechnerergebnissen."""
    out = []
    P = pkg.P
    E = pkg.j("research/evidence_gates.json")
    gates = {g["id"]: g for g in E["gates"]}
    xin = pkg.j("external_inputs.json")["inputs"]
    classes = set(E["outcome_classes"])
    for g in gates.values():
        rules = g["outcome_rules"]
        if rules[-1]["when"] != {"const": True}:
            out.append(f"{g['id']}: letzte Ergebnisregel ist nicht immer wahr")
        if len({r['id'] for r in rules}) != len(rules):
            out.append(f"{g['id']}: doppelte Regel-IDs")
        if set(g["next_steps"]) != classes:
            out.append(f"{g['id']}: Folgeschritte nicht für alle Ergebnisklassen")
        for pid in sorted(_params_in(g, set())):
            if pid not in P:
                out.append(f"{g['id']}: Parameter {pid} fehlt")
        if g["kind"] == "GATE":
            pre = {m for p in g["prerequisites"] if p["on_fail"] == "BLOCKED_EXTERNAL" for m in re.findall(r"inputs\.(X-[A-Z0-9-]+)", json.dumps(p["expr"]))}
            blk = {x["id"] for x in xin if g["id"] in x["blocks"]}
            if pre != blk:
                out.append(f"{g['id']}: sperrende Eingaben im Tor {sorted(pre - blk)} bzw. im Register {sorted(blk - pre)} nicht abgeglichen")
    # Futility: in G3 und G4 vor PASS, Schwelle wirksam
    fut = float(P["P-RES-FUTILITY"])
    if not 0 < fut < 1:
        out.append(f"P-RES-FUTILITY {fut} unwirksam (muss in (0, 1) liegen)")
    for gid in ("GATE-G3", "GATE-G4"):
        rules = gates[gid]["outcome_rules"]
        idx = [i for i, r in enumerate(rules) if r["outcome"] == "FAIL" and r["when"] == {"lt": [{"var": "p_predictive_final"}, {"param": "P-RES-FUTILITY"}]}]
        pas = [i for i, r in enumerate(rules) if r["outcome"] == "PASS"]
        if not idx or not pas or idx[0] > pas[0]:
            out.append(f"{gid}: Futility-Regel fehlt oder steht hinter PASS (Futility umgangen)")
    need = {"GATE-G3": {"P-RES-DSR-MIN", "P-RES-FUTILITY"}, "GATE-G4": {"P-RES-FUTILITY"}, "GATE-G7": {"P-OC-HARM-SCREEN"},
            "GATE-G8": {"P-OC-HARM-SCREEN", "P-RES-FINAL-P"}}
    for gid, ps in need.items():
        missing = ps - _params_in(gates[gid]["outcome_rules"], set())
        if missing:
            out.append(f"{gid}: Schwellen der Betriebscharakteristik fehlen in den Regeln: {sorted(missing)}")
    oc = pkg.j("research/operating_characteristics_results.json")
    if not close(float(oc["registered_dsr_min"]), float(P["P-RES-DSR-MIN"])):
        out.append("Betriebscharakteristik rechnet mit einer anderen DSR-Schwelle als G3")
    if oc["inputs"].get("parameters.json") != content_hash(pkg, "parameters.json"):
        out.append("Betriebscharakteristik rechnet mit veralteten Parametern (Eingangs-Hash abweichend)")
    # Bauprogramm
    for s in pkg.j("implementation/build_stages.json")["stages"]:
        if s["gate"] not in gates:
            out.append(f"{s['id']}: Tor {s['gate']} fehlt")
            continue
        blk = sorted(x["id"] for x in xin if s["gate"] in x["blocks"])
        if sorted(s["external"]) != blk:
            out.append(f"{s['id']}: externe Eingaben weichen vom Register ab")
        if gates[s["gate"]]["stage"] != s["id"]:
            out.append(f"{s['id']}: Tor {s['gate']} gehört zu Stufe {gates[s['gate']]['stage']}")
    # E-Abbildung
    emap = E["e_score_map"]
    if sorted(emap) != [f"E-{i}" for i in range(1, 10)]:
        out.append("E-Abbildung deckt E-1 bis E-9 nicht genau ab")
    seen = [g for v in emap.values() for g in v]
    if sorted(seen) != sorted(g for g in gates if gates[g]["kind"] == "GATE") or len(seen) != len(set(seen)):
        out.append("jedes Tor muss genau einem E-Baustein zugeordnet sein")
    for k, v in emap.items():
        for gid in v:
            if gates[gid]["e_block"] != k:
                out.append(f"{gid}: E-Baustein {gates[gid]['e_block']} ≠ Abbildung {k}")
    # Torfälle mit heutigen Werten neu ableiten
    dmc = pkg.j("financials/decision_montecarlo_results.json")
    st = str(P["P-RISK-STRESS-REF-STAGE"])
    reg, tfd1, vv = dmc["table"]["U-KOSTEN"][st]["H5"], dmc["table"]["U-KOSTEN-TFD1"][st]["H5"], dmc["variants_V0_V4"][st]
    lo, hi = min(vv["V1"]["value_per_risk_unit_range"]), max(vv["V1"]["value_per_risk_unit_range"])
    dec_tfd1 = variant_decision(tfd1["class"] if "base" in tfd1 else None, tfd1.get("base", {}).get("value_per_risk_unit"), lo, hi)
    n_today = 0
    for p in sorted((pkg.root / "examples/valid/gate_cases").glob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        src = c.get("facts_source")
        if not src:
            continue
        n_today += 1
        f = c["facts"]
        if "/table/U-KOSTEN-TFD1/" in src:
            want = {"finding_class": tfd1["class"], "p_npv_positive": tfd1["base"]["p_npv_positive"], "variant_decision": dec_tfd1}
        else:
            want = {"finding_class": reg["class"], "p_npv_positive": reg.get("base", {}).get("p_npv_positive", 0.0), "variant_decision": vv["decision"]}
        for k, v in want.items():
            if f.get(k) != v:
                out.append(f"{c['id']}: Fakt {k} = {f.get(k)} ≠ heutiger Rechenwert {v} ({src})")
        rel, ptr = src.split("#", 1)
        try:
            pointer(pkg.j(rel), ptr)
        except (KeyError, IndexError, ValueError):
            out.append(f"{c['id']}: Wertquelle {src} nicht auflösbar")
    if n_today == 0:
        out.append("keine Torfälle mit heutigen Rechenwerten")
    return out


# ================================================================================================================ Betreiberangaben
def _h(o) -> str:
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def check_operator(pkg: Pkg) -> list:
    """Betreiberentscheidungen und Betreiberwerte stimmen mit dem Siegel überein (registers/operator_seal.json); externe Eingaben sind nur
    mit Nachweis bestätigt; Standardwerte nur markiert und mit Betreiberentscheidung."""
    out = []
    seal = pkg.j("registers/operator_seal.json")
    dec = {d["id"]: d for d in pkg.j("registers/decision_register.json")["decisions"] if d["type"] == "BETREIBER"}
    sealed = {x["id"]: x for x in seal["decisions"]}
    if set(dec) != set(sealed):
        out.append(f"Betreiberentscheidungen ohne Siegel oder Siegel ohne Entscheidung: {sorted(set(dec) ^ set(sealed))}")
    for did, d in dec.items():
        s = sealed.get(did)
        if s and s["answer_sha256"] != _h(d.get("operator_answer_verbatim")):
            out.append(f"{did}: Wortlaut der Betreiberantwort weicht vom Siegel ab")
    prm = {p["id"]: p for p in pkg.j("parameters.json")["parameters"] if p["status"] == "BETREIBER"}
    sp = {x["id"]: x for x in seal["parameters"]}
    if set(prm) != set(sp):
        out.append(f"Betreiberwerte ohne Siegel oder Siegel ohne Parameter: {sorted(set(prm) ^ set(sp))}")
    for pid, p in prm.items():
        s = sp.get(pid)
        if s and s["value_sha256"] != _h(p["value"]):
            out.append(f"{pid}: Betreiberwert weicht vom Siegel ab (neue Betreiberentscheidung nötig)")
    pprm = {p["id"]: p for p in pkg.j("parameters.json")["parameters"]}
    for x in pkg.j("external_inputs.json")["inputs"]:
        if x["status"] != "UNBESTAETIGT":
            conf = x.get("confirmation") or {}
            ev = conf.get("evidence")
            if not (conf.get("date") and conf.get("signed_by") and ev and pkg.exists(ev.split("#")[0])):
                out.append(f"{x['id']}: Status {x['status']} ohne Nachweis (Datum, Unterschrift, Beleg im Paket)")
        if x["default_value"] is not None and not x["default_marked"]:
            out.append(f"{x['id']}: Standardwert nicht markiert")
        if x["default_marked"]:
            # R-07: ohne ausdrückliche Zulassung nur als markierte Rechenannahme (DEC-CF-08), die keine Sperre löst
            if not (any(r.startswith("DEC-OP-") for r in x["refs"]) or "DEC-CF-08" in x["refs"]):
                out.append(f"{x['id']}: markierter Standardwert ohne Betreiberzulassung und ohne Verweis auf DEC-CF-08")
            if x["status"] != "UNBESTAETIGT" and not x.get("confirmation"):
                out.append(f"{x['id']}: Rechenannahme als Bestätigung ausgegeben")
            for r in x["refs"]:
                if r in pprm and pprm[r]["status"] in ("BELEGT", "BETREIBER"):
                    out.append(f"{x['id']}: Rechenannahme speist Parameter {r} mit Status {pprm[r]['status']}")
    return out


# ================================================================================================================ Selbstbewertung
def check_scores(pkg: Pkg) -> list:
    """Scorecards K und E: Raster aus §20, Faktoren aus {0; 0,25; 0,5; 0,75; 1}, Summen, Nachweise auflösbar, K ≤ 99 ohne
    Gegenprüfung, E-Punkte nur mit signiertem Torergebnis und Laufbeleg im Paket."""
    out = []
    if not (pkg.exists("audit/scorecard_K.json") and pkg.exists("audit/scorecard_E.json")):
        return ["Scorecards K und E fehlen"]
    K = pkg.j("audit/scorecard_K.json")
    tot = 0.0
    for s in K["subcriteria"]:
        if s["factor"] not in FACTORS:
            out.append(f"K {s['id']}: Faktor {s['factor']} nicht zulässig")
        if not close(s["points"], s["factor"] * s["max"]):
            out.append(f"K {s['id']}: Punkte ≠ Faktor × Höchstpunkte")
        if s["factor"] > 0 and not s["evidence"]:
            out.append(f"K {s['id']}: Punkte ohne Nachweis")
        for ev in s["evidence"]:
            rel = ev.split("#")[0].split("::")[0]
            if "/" in rel or rel.endswith((".json", ".md", ".py", ".txt", ".csv")):
                if not pkg.exists(rel):
                    out.append(f"K {s['id']}: Nachweis {ev} fehlt im Paket")
        tot += s["points"]
    if abs(sum(s["max"] for s in K["subcriteria"]) - 100) > TOL:
        out.append("K: Höchstpunkte ergeben nicht 100")
    if not close(K["total"], tot):
        out.append(f"K: Summe {K['total']} ≠ nachgerechnet {tot}")
    review = K.get("independent_review", {})
    if review.get("status") != "BESTANDEN":
        j3 = next((s for s in K["subcriteria"] if s["id"] == "J3"), None)
        if j3 is None or j3["factor"] != 0:
            out.append("K J3: Punkte ohne bestandene unabhängige Gegenprüfung")
        if K["total"] > 99 + TOL:
            out.append("K > 99 ohne unabhängige Gegenprüfung (R-08)")
    Esc = pkg.j("audit/scorecard_E.json")
    emap = pkg.j("research/evidence_gates.json")["e_score_map"]
    etot = 0.0
    for b in Esc["blocks"]:
        etot += b["points"]
        if b["points"] > 0:
            ok = bool(b.get("evidence"))
            for ev in b.get("evidence", []):
                if not pkg.exists(ev):
                    ok = False
                    continue
                gr = pkg.j(ev)
                if gr.get("gate") not in emap.get(b["id"], []) or gr.get("outcome") != "PASS" or gr.get("exit_code") != 0 \
                        or not re.fullmatch(r"SIG-[0-9A-F]{64}", str(gr.get("signature", ""))) or not pkg.exists(str(gr.get("run_log_ref", "")).split("#")[0]):
                    ok = False
            if not ok:
                out.append(f"E {b['id']}: {b['points']} Punkte ohne signiertes Torergebnis mit Laufbeleg")
    if not close(Esc["total"], etot):
        out.append(f"E: Summe {Esc['total']} ≠ nachgerechnet {etot}")
    return out


CHECKS = {f.__name__: f for f in (check_costs, check_leverage, check_stress, check_tax, check_capacity, check_proxy, check_limits, check_runbooks,
                                  check_gates, check_operator, check_scores)}


def run_all(root: Path, only=None) -> dict:
    pkg = Pkg(root)
    res = {}
    for name, fn in CHECKS.items():
        if only and name not in only:
            continue
        try:
            res[name] = fn(pkg)
        except Exception as ex:  # noqa: BLE001 – jede Ausnahme ist ein Befund
            res[name] = [f"Ausnahme {ex.__class__.__name__}: {ex}"]
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--only", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    only = {x for x in a.only.split(",") if x} or None
    res = run_all(Path(a.root).resolve(), only)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for name, errs in res.items():
            print(f"{name:<16} {'BESTANDEN' if not errs else 'BEFUNDE ' + str(len(errs))}")
            for e in errs[:25]:
                print(f"    {e}")
    bad = [n for n, e in res.items() if e]
    print("SEMANTIK", "BESTANDEN" if not bad else f"FEHLER {bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
