"""Gemeinsame Hilfen der Referenzrechner.

* nur Standardbibliothek, keine Zeitstempel, sortierte und gerundete Ausgaben → bytegleiche Wiederholung (--check, R-10)
* eigener Zufallsgenerator auf Basis von random.Random (Mersenne Twister) mit eigener Normal-, t- und Poisson-Ziehung,
  damit die Ziehungen nicht von Implementierungsdetails der Python-Version abhängen
* Geldbeträge als Decimal (R-03)
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
CENT = Decimal("0.01")


# ----------------------------------------------------------------------------------------------- Ein- und Ausgabe
def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha256_file(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


DERIVED_KEYS = frozenset({"used_in"})


def _strip_derived(o):
    if isinstance(o, dict):
        return {k: _strip_derived(v) for k, v in o.items() if k not in DERIVED_KEYS}
    if isinstance(o, list):
        return [_strip_derived(v) for v in o]
    return o


def sha256_content(rel: str) -> str:
    """SHA-256 des Inhalts. JSON-Dateien werden kanonisch (sortierte Schlüssel) und ohne abgeleitete Felder (used_in) gehasht:
    validation/render_blocks.py führt used_in nach jedem Lauf nach; das darf die Rechnerergebnisse nicht ungültig machen."""
    if not rel.endswith(".json"):
        return sha256_file(rel)
    canon = json.dumps(_strip_derived(load(rel)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def input_hashes(rels) -> dict:
    """Eingangs-Hashes der Rechner (Inhalts-Hash nach sha256_content)."""
    return {r: sha256_content(r) for r in sorted(rels)}


def rnd(x, sig: int = 10):
    """Rundet Gleitkommazahlen auf signifikante Stellen (stabile Textdarstellung)."""
    if isinstance(x, bool) or x is None or isinstance(x, (int, str, Decimal)):
        return x
    if isinstance(x, float):
        if x == 0.0 or not math.isfinite(x):
            return 0.0 if x == 0.0 else x
        d = sig - int(math.floor(math.log10(abs(x)))) - 1
        v = round(x, d)
        return 0.0 if v == 0 else v
    if isinstance(x, dict):
        return {k: rnd(v, sig) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v, sig) for v in x]
    return x


def _default(o):
    if isinstance(o, Decimal):
        return str(o)
    raise TypeError(type(o))


def dumps(obj) -> str:
    return json.dumps(rnd(obj), ensure_ascii=False, indent=1, sort_keys=False, default=_default) + "\n"


def write_or_check(rel: str, text: str, check: bool) -> bool:
    """Schreibt die Datei oder vergleicht bytegleich (Modus --check). Rückgabe True = in Ordnung."""
    p = ROOT / rel
    if check:
        if not p.exists():
            print(f"FEHLT: {rel}")
            return False
        old = p.read_text(encoding="utf-8")
        if old != text:
            a, b = old.splitlines(), text.splitlines()
            for i, (x, y) in enumerate(zip(a, b, strict=False)):
                if x != y:
                    print(f"ABWEICHUNG {rel} Zeile {i + 1}:\n  gespeichert: {x[:160]}\n  berechnet:   {y[:160]}")
                    break
            else:
                print(f"ABWEICHUNG {rel}: Länge {len(a)} gegenüber {len(b)} Zeilen")
            return False
        return True
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return True


def csv_text(header, rows) -> str:
    out = [";".join(header)]
    for r in rows:
        out.append(";".join("" if v is None else (str(rnd(v)) if isinstance(v, float) else str(v)) for v in r))
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------------------------------- Register
class Params:
    def __init__(self):
        self.reg = load("parameters.json")
        self.by = {p["id"]: p for p in self.reg["parameters"]}

    def __call__(self, pid):
        return self.by[pid]["value"]

    def f(self, pid) -> float:
        return float(self.by[pid]["value"])


def costs() -> dict:
    return {c["id"]: c for c in load("registers/costs.json")["costs"]}


def instruments():
    return load("registers/instruments.json")["instruments"]


def dec(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def money(x) -> Decimal:
    return dec(x).quantize(CENT, rounding=ROUND_HALF_EVEN)


# ----------------------------------------------------------------------------------------------- Statistik
def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def norm_ppf(p: float) -> float:
    """Inverse Normalverteilung (Acklam) mit zwei Newton-Schritten; Genauigkeit < 1e-12 im Bereich 1e-12 … 1−1e-12."""
    if not 0.0 < p < 1.0:
        raise ValueError("p außerhalb (0,1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    pl = 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    elif p > 1 - pl:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    else:
        q = p - 0.5
        r = q * q
        x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    for _ in range(2):
        e = norm_cdf(x) - p
        x -= e / norm_pdf(x)
    return x


def quantile(sorted_vals, q: float) -> float:
    """Empirisches Quantil (lineare Interpolation, Typ 7)."""
    n = len(sorted_vals)
    if n == 0:
        raise ValueError("leer")
    h = (n - 1) * q
    lo = int(math.floor(h))
    hi = min(lo + 1, n - 1)
    return sorted_vals[lo] + (h - lo) * (sorted_vals[hi] - sorted_vals[lo])


def mean(v) -> float:
    return math.fsum(v) / len(v)


def stdev(v) -> float:
    m = mean(v)
    return math.sqrt(math.fsum((x - m) ** 2 for x in v) / (len(v) - 1))


def expected_shortfall(sorted_vals, alpha: float) -> float:
    """Mittel der schlechtesten (1−alpha)-Anteile einer aufsteigend sortierten Liste (Verluste negativ)."""
    k = max(1, int(math.floor(len(sorted_vals) * (1 - alpha))))
    return mean(sorted_vals[:k])


# ----------------------------------------------------------------------------------------------- Zufall
class Rng:
    """Deterministischer Zufallsgenerator mit eigenen Verteilungen (versionsstabil)."""

    def __init__(self, seed: int):
        self._r = random.Random(seed)
        self._spare = None

    def u(self) -> float:
        return self._r.random()

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self._r.random()

    def normal(self, mu: float = 0.0, sd: float = 1.0) -> float:
        if self._spare is not None:
            z, self._spare = self._spare, None
            return mu + sd * z
        while True:
            u1 = self._r.random()
            if u1 > 1e-300:
                break
        u2 = self._r.random()
        rad = math.sqrt(-2.0 * math.log(u1))
        z0 = rad * math.cos(2.0 * math.pi * u2)
        self._spare = rad * math.sin(2.0 * math.pi * u2)
        return mu + sd * z0

    def chi2(self, df: int) -> float:
        return math.fsum(self.normal() ** 2 for _ in range(df))

    def student_t_unit(self, df: int) -> float:
        """t-verteilte Ziehung, auf Varianz 1 skaliert (fette Ränder bei gleicher Volatilität)."""
        z = self.normal()
        t = z / math.sqrt(self.chi2(df) / df)
        return t * math.sqrt((df - 2) / df)

    def student_t4_unit(self) -> float:
        """t(4)-Ziehung mit Varianz 1: χ²₄ = −2·ln(u₁·u₂) (schnell, exakt)."""
        z = self.normal()
        u = self._r.random() * self._r.random()
        chi = -2.0 * math.log(u if u > 1e-300 else 1e-300)
        return z / math.sqrt(chi / 4.0) * math.sqrt(0.5)

    def poisson(self, lam: float) -> int:
        lim, k, prod = math.exp(-lam), 0, self._r.random()
        while prod > lim:
            k += 1
            prod *= self._r.random()
        return k

    def choice(self, seq):
        return seq[int(self._r.random() * len(seq))]

    def lognormal_mean_sd(self, m: float, s: float) -> float:
        """Lognormal mit gegebenem Mittelwert und Standardabweichung."""
        v = math.log(1 + (s / m) ** 2)
        return math.exp(math.log(m) - v / 2 + math.sqrt(v) * self.normal())


def main_args(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="nur prüfen (bytegleiche Neuberechnung), nichts schreiben")
    return ap.parse_args(argv)


# ----------------------------------------------------------------------------------------------- Leitern (gemeinsam für Stress und Kelly/Ruin)
def ladder_factor(day_loss: float, drawdown: float, P) -> float:
    """Exposure am Folgetag nach Tages- und Drawdown-Leiter (P-RISK-LADDER-FACTORS); genutzt von risk/stress_test_engine.py und risk/kelly_ruin_simulator.py."""
    F = P("P-RISK-LADDER-FACTORS")
    day = F["DL_L2"] if day_loss >= P.f("P-RISK-DL-L2") else (F["DL_L1"] if day_loss >= P.f("P-RISK-DL-L1") else 1.0)
    if drawdown >= P.f("P-RISK-DD-L3"):
        dd = F["DD_L3"]
    elif drawdown >= P.f("P-RISK-DD-L2"):
        dd = F["DD_L2"]
    elif drawdown >= P.f("P-RISK-DD-L1"):
        dd = F["DD_L1"]
    else:
        dd = 1.0
    return min(day, dd)


# ----------------------------------------------------------------------------------------------- Referenzsemantik von Risikoregeln
def gap_rule_ok(gap_stress: float, day_loss: float, P, weekend: bool = False) -> bool:
    """Größenregel PTC-13 (DEC-DS-10): risikoerhöhende Order nur, wenn Lückenstress nach der Order (über Wochenenden und Feiertage mit
    P-RISK-WEEKEND-FACTOR) plus heutiger Verlust höchstens Tagesgrenze − Reserve beträgt. Gleichheit ist zulässig."""
    f = P.f("P-RISK-WEEKEND-FACTOR") if weekend else 1.0
    budget = P.f("P-OP-DAILY-LOSS-CAP") - P.f("P-RISK-GAP-RESERVE")
    return f * gap_stress + max(0.0, day_loss) <= budget + 1e-12


def margin_loss_to_level(me: float, increase: float, level: float, phi: float) -> float:
    """Verlust in Anteilen des NAV, bis das Margin-Level am Broker (Guthaben beim Broker / Initial Margin) nach einer Margin-Erhöhung um
    increase auf level fällt. Beim Broker liegt der Anteil phi des NAV (P-ECO-CASH-AT-BROKER); Verluste werden dort abgerechnet, das
    Kapital außerhalb hilft erst nach einer Überweisung (P-MRG-TOPUP-DAYS). me ist die Initial Margin in Anteilen des gesamten NAV:
    (phi − L) / (me · (1 + increase)) = level  →  L = phi − level · me · (1 + increase); nie negativ."""
    return max(0.0, phi - level * me * (1.0 + increase))


EARLY_CLASSES = ("PROFILE_NOT_ADMISSIBLE", "NON_POSITIVE_BASE", "NOT_VIABLE_AT_CAPITAL")


def variant_decision(cls, vpr, v1_low: float, v1_high: float) -> str:
    """Befund des Variantenvergleichs (§5.5, §5.7) in der Prüfreihenfolge: zuerst die Befundklasse der Eigenentwicklung (Profil unzulässig,
    keine positive Mehrertragsrate, nicht wirtschaftlich), erst danach die Dominanz durch die Fondslösung V1 (Wert je Risikoeinheit).
    cls None: keine Simulation, weil das Universum bei diesem Kapital leer ist."""
    if cls is None:
        return "NICHT_ZULASSUNGSFAEHIG"
    if cls in EARLY_CLASSES:
        return cls
    if v1_low >= vpr:
        return "DOMINATED_BY_ALTERNATIVE"
    if v1_high >= vpr:
        return "V1_OBERER_WERT_UEBERLEGEN"
    return "NICHT_DOMINIERT"


def broker_share_required(me: float, increase: float, level: float, loss: float) -> float:
    """Anteil des NAV, der beim Broker liegen muss, damit das Margin-Level nach dem Verlust loss (Anteil NAV) und einer Margin-Erhöhung
    um increase nicht unter level fällt: phi = loss + level · me · (1 + increase)."""
    return loss + level * me * (1.0 + increase)

