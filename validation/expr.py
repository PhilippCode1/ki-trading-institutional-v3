#!/usr/bin/env python3
"""Deterministische Ausdruckssprache für Wächter (state_machines.json) und Torregeln (evidence_gates.json).

Ein Ausdruck ist ein JSON-Objekt mit genau einem Operator als Schlüssel:
  Logik:      {"all": [a, b, ...]}, {"any": [...]}, {"not": a}, {"const": true|false|Zahl|Text}
  Vergleich:  {"eq": [x, y]}, {"ne": [x, y]}, {"gt": [x, y]}, {"ge": [x, y]}, {"lt": [x, y]}, {"le": [x, y]},
              {"in": [x, [Liste]]}, {"is_null": x}, {"not_null": x}
  Werte:      {"var": "name"} (Punktnotation für verschachtelte Fakten), Literale (Zahl, Text, bool, null),
              {"param": "<Parameter-ID>"} bzw. {"param": ["<Parameter-ID>", "schlüssel"]}: Wert aus parameters.json (führende Quelle;
              der Aufrufer übergibt die Werte unter dem reservierten Faktenschlüssel "__params__")
  Arithmetik: {"add": [...]}, {"sub": [a, b]}, {"mul": [...]}, {"div": [a, b]}, {"sqrt": a}, {"abs": a},
              {"min": [...]}, {"max": [...]}
Fehlende Variablen sind ein Fehler (ExprError), kein stiller Standardwert. Vergleiche mit null liefern nur bei
eq/ne ein Ergebnis; gt/ge/lt/le mit null sind ein Fehler. Zahlenvergleiche (eq, ne, gt, ge, lt, le) runden beide Seiten
auf ROUND_DIGITS = 9 Nachkommastellen: Werte, die nur durch Binärgleitkomma von einer Schwelle abweichen, gelten als gleich
(Grenzfälle der Torregeln). Keine Seiteneffekte, kein eval().
"""
from __future__ import annotations

import math

OPS_LOGIC = {"all", "any", "not", "const"}
OPS_CMP = {"eq", "ne", "gt", "ge", "lt", "le", "in", "is_null", "not_null"}
OPS_ARITH = {"add", "sub", "mul", "div", "sqrt", "abs", "min", "max"}
ALL_OPS = OPS_LOGIC | OPS_CMP | OPS_ARITH | {"var", "param"}
ROUND_DIGITS = 9
PARAMS_KEY = "__params__"


class ExprError(ValueError):
    pass


def _lookup(facts: dict, name: str):
    cur = facts
    for part in name.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise ExprError(f"Variable fehlt: {name}")
        cur = cur[part]
    return cur


def _param(facts: dict, arg):
    params = facts.get(PARAMS_KEY) if isinstance(facts, dict) else None
    if params is None:
        raise ExprError("Parameterwerte fehlen (Faktenschlüssel __params__)")
    pid, *path = [arg] if isinstance(arg, str) else list(arg)
    if pid not in params:
        raise ExprError(f"Parameter fehlt: {pid}")
    cur = params[pid]
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            raise ExprError(f"Parameterpfad fehlt: {pid}/{k}")
        cur = cur[k]
    if cur is None or isinstance(cur, (dict, list)):
        raise ExprError(f"Parameter {pid}{'/' + '/'.join(path) if path else ''} ist kein Einzelwert")
    return cur


def value(x, facts):
    if isinstance(x, dict):
        if len(x) != 1:
            raise ExprError(f"Ausdruck muss genau einen Operator haben: {x}")
        (op, arg), = x.items()
        if op == "var":
            return _lookup(facts, arg)
        if op == "param":
            return _param(facts, arg)
        if op in OPS_ARITH:
            return _arith(op, arg, facts)
        return evaluate(x, facts)
    if isinstance(x, list):
        return [value(e, facts) for e in x]
    return x


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ExprError(f"Zahl erwartet, erhalten: {v!r}")
    if isinstance(v, float) and not math.isfinite(v):
        raise ExprError("nicht endliche Zahl")
    return v


def _arith(op, arg, facts):
    if op in ("sqrt", "abs"):
        a = _num(value(arg, facts))
        if op == "sqrt":
            if a < 0:
                raise ExprError("Wurzel aus negativer Zahl")
            return math.sqrt(a)
        return abs(a)
    vals = [_num(value(a, facts)) for a in arg]
    if op == "add":
        return sum(vals)
    if op == "mul":
        out = 1.0
        for a in vals:
            out *= a
        return out
    if op == "sub":
        if len(vals) != 2:
            raise ExprError("sub braucht zwei Argumente")
        return vals[0] - vals[1]
    if op == "div":
        if len(vals) != 2 or vals[1] == 0:
            raise ExprError("div braucht zwei Argumente und Nenner != 0")
        return vals[0] / vals[1]
    if op == "min":
        return min(vals)
    if op == "max":
        return max(vals)
    raise ExprError(op)


def evaluate(expr, facts) -> bool:
    if not isinstance(expr, dict) or len(expr) != 1:
        raise ExprError(f"ungültiger Ausdruck: {expr!r}")
    (op, arg), = expr.items()
    if op == "const":
        return arg
    if op == "all":
        return all(bool(evaluate(e, facts)) for e in arg)
    if op == "any":
        return any(bool(evaluate(e, facts)) for e in arg)
    if op == "not":
        return not bool(evaluate(arg, facts))
    if op in ("is_null", "not_null"):
        try:
            val = value(arg, facts)
        except ExprError:
            val = None
        return (val is None) if op == "is_null" else (val is not None)
    if op == "in":
        a, lst = value(arg[0], facts), value(arg[1], facts)
        return a in lst
    if op in ("eq", "ne", "gt", "ge", "lt", "le"):
        if not isinstance(arg, list) or len(arg) != 2:
            raise ExprError(f"{op} braucht zwei Argumente")
        a, b = value(arg[0], facts), value(arg[1], facts)
        if _is_num(a) and _is_num(b):
            a, b = round(a, ROUND_DIGITS), round(b, ROUND_DIGITS)
        if op == "eq":
            return a == b
        if op == "ne":
            return a != b
        a, b = _num(a), _num(b)
        return {"gt": a > b, "ge": a >= b, "lt": a < b, "le": a <= b}[op]
    raise ExprError(f"unbekannter Operator: {op}")


def variables(expr) -> set:
    """Alle referenzierten Variablennamen eines Ausdrucks (für statische Prüfungen)."""
    out = set()
    if isinstance(expr, dict):
        for k, v in expr.items():
            if k == "var":
                out.add(v)
            elif k != "param":
                out |= variables(v)
    elif isinstance(expr, list):
        for e in expr:
            out |= variables(e)
    return out


def check_syntax(expr) -> list:
    """Liefert eine Liste von Syntaxfehlern (leer, wenn in Ordnung)."""
    errs = []
    if isinstance(expr, dict):
        if len(expr) != 1:
            return [f"mehr als ein Operator: {sorted(expr)}"]
        (op, arg), = expr.items()
        if op not in ALL_OPS:
            return [f"unbekannter Operator: {op}"]
        if op == "var" and not isinstance(arg, str):
            errs.append("var braucht einen Namen")
        elif op == "param" and not (isinstance(arg, str) or (isinstance(arg, list) and arg and
                                                             all(isinstance(a, str) for a in arg))):
            errs.append("param braucht eine Parameter-ID oder [ID, Schlüssel …]")
        elif op in ("all", "any", "add", "mul", "min", "max") and not isinstance(arg, list):
            errs.append(f"{op} braucht eine Liste")
        if op not in ("var", "param"):
            errs += check_syntax(arg)
    elif isinstance(expr, list):
        for e in expr:
            errs += check_syntax(e)
    return errs


def params_used(expr) -> set:
    """Alle referenzierten Parameter (als Tupel ID, Pfad …) eines Ausdrucks."""
    out = set()
    if isinstance(expr, dict):
        for k, v in expr.items():
            if k == "param":
                out.add(tuple([v]) if isinstance(v, str) else tuple(v))
            else:
                out |= params_used(v)
    elif isinstance(expr, list):
        for e in expr:
            out |= params_used(e)
    return out


def load_param_values(root) -> dict:
    """Parameterwerte aus parameters.json (führende Quelle) für den Faktenschlüssel __params__."""
    import json
    from pathlib import Path
    doc = json.loads((Path(root) / "parameters.json").read_text(encoding="utf-8"))
    return {p["id"]: p["value"] for p in doc["parameters"]}
