"""S-CA – Carry als Filter (vorregistriert).

Mechanismus: Rollrendite aus Front- und Folgekontrakt, annualisiert: carry = (P_front − P_next) / P_front · 365 / Tage zwischen den Verfällen.
Trades der Trendfolge in Carry-Richtung werden um den Faktor (1 + x) vergrößert, dagegen um (1 − x) verkleinert (x = P-STR-CA-TILT).
Ein eigenständiger Carry-Handel scheitert an der 7-Tage-Grenze (Wiedereinstieg jede Woche → Umschlag); er ist nur Forschungsvariante.
"""
from __future__ import annotations


def annualized_carry(p_front: float, p_next: float, days_between: float) -> float:
    if p_front <= 0 or days_between <= 0:
        raise ValueError("ungültige Eingabe")
    return (p_front - p_next) / p_front * 365.0 / days_between


def tilt_factor(carry: float, direction: int, x: float, dead_zone: float = 0.0) -> float:
    """Größenfaktor für einen Trade in Richtung direction (+1/−1)."""
    if abs(carry) <= dead_zone:
        return 1.0
    return 1.0 + x if (carry > 0) == (direction > 0) else 1.0 - x


def make_tilt(carries, x: float):
    """Liefert eine Funktion (bar, direction) → Faktor für s_tf.run(carry_tilt=…)."""
    return lambda i, d: tilt_factor(carries[i], d, x)
