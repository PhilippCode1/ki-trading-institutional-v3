"""Gemeinsame Bausteine der Referenzstrategien (deterministisch, nur Standardbibliothek).

Die Strategien arbeiten auf Stundenbalken. Ein Handelstag hat 23 Balken (Futures mit einer Stunde Pause), eine Woche fünf Handelstage;
das Wochenende zählt 48 Kalenderstunden zusätzlich. Die Referenzimplementierungen dienen Tests und der Umschlagsmessung auf
synthetischen Preisen – sie sind kein Beleg für eine Edge (R-02).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

BARS_PER_DAY = 23


class Ewma:
    """Exponentiell gewichteter Mittelwert mit Spanne n (alpha = 2/(n+1))."""

    def __init__(self, span: float):
        self.a = 2.0 / (span + 1.0)
        self.v = None

    def update(self, x: float) -> float:
        self.v = x if self.v is None else self.v + self.a * (x - self.v)
        return self.v


class EwmaVol:
    """EWMA-Volatilität der Stundenrenditen; liefert Tagesvolatilität (Anteil) über √23."""

    def __init__(self, span_hours: float, floor: float = 1e-6):
        self.a = 2.0 / (span_hours + 1.0)
        self.var = None
        self.floor = floor

    def update(self, r: float) -> float:
        self.var = r * r if self.var is None else self.var + self.a * (r * r - self.var)
        return self.daily()

    def daily(self) -> float:
        return max(self.floor, math.sqrt(self.var if self.var else 0.0) * math.sqrt(BARS_PER_DAY))


def cap(x: float, c: float) -> float:
    return max(-c, min(c, x))


def forecast_scalar(raws, target_abs: float) -> float:
    """Skalar, der den mittleren Betrag der Rohprognose auf target_abs bringt (Carver 2015)."""
    m = math.fsum(abs(r) for r in raws) / max(1, len(raws))
    return target_abs / m if m > 0 else 0.0


def fdm(series_list, cap_value: float) -> float:
    """Prognose-Diversifikationsmultiplikator 1/√(wᵀΡw) bei Gleichgewichtung; gedeckelt."""
    k = len(series_list)
    if k == 1:
        return 1.0
    n = min(len(s) for s in series_list)

    def corr(a, b):
        ma, mb = math.fsum(a[:n]) / n, math.fsum(b[:n]) / n
        cov = math.fsum((a[i] - ma) * (b[i] - mb) for i in range(n))
        va = math.fsum((a[i] - ma) ** 2 for i in range(n))
        vb = math.fsum((b[i] - mb) ** 2 for i in range(n))
        return cov / math.sqrt(va * vb) if va > 0 and vb > 0 else 0.0

    w = 1.0 / k
    tot = 0.0
    for i in range(k):
        for j in range(k):
            tot += w * w * (1.0 if i == j else max(0.0, corr(series_list[i], series_list[j])))
    return min(cap_value, 1.0 / math.sqrt(tot))


@dataclass
class Trade:
    direction: int
    entry_bar: int
    entry_price: float
    entry_hours: float
    size: float = 1.0
    stop_frac: float = 1.0
    exit_bar: int = -1
    exit_price: float = 0.0
    exit_hours: float = 0.0
    reason: str = ""

    @property
    def holding_hours(self) -> float:
        return self.exit_hours - self.entry_hours

    @property
    def ret(self) -> float:
        return self.direction * (self.exit_price / self.entry_price - 1.0)


@dataclass
class Book:
    """Führt Trades einer Strategie auf einem Instrument; erzwingt Zeitstopp und Sperrzeit nach Zeitstopp."""
    max_hold_h: float
    cooldown_h: float
    trades: list = field(default_factory=list)
    open: Trade | None = None
    last_timestop: dict = field(default_factory=dict)

    def can_enter(self, direction: int, hours: float) -> bool:
        t = self.last_timestop.get(direction)
        return self.open is None and (t is None or hours - t >= self.cooldown_h)

    def enter(self, direction: int, bar: int, price: float, hours: float, size: float = 1.0, stop_frac: float = 1.0):
        self.open = Trade(direction, bar, price, hours, size, stop_frac)

    def exit(self, bar: int, price: float, hours: float, reason: str):
        t = self.open
        t.exit_bar, t.exit_price, t.exit_hours, t.reason = bar, price, hours, reason
        if reason == "ZEITSTOPP":
            self.last_timestop[t.direction] = hours
        self.trades.append(t)
        self.open = None

    def time_stop_due(self, hours: float) -> bool:
        return self.open is not None and hours - self.open.entry_hours >= self.max_hold_h

    def stop_hit(self, price: float) -> bool:
        t = self.open
        return t is not None and t.direction * (price / t.entry_price - 1.0) <= -t.stop_frac


def summarize(trades, total_hours: float, years: float) -> dict:
    """Umschlagskennzahlen: Round-Turns je Jahr, Zeit im Markt, Haltedauern, Ausstiegsgründe."""
    if not trades:
        return {"round_turns_per_year": 0.0, "time_in_market": 0.0, "holding_hours_mean": 0.0, "holding_hours_median": 0.0,
                "share_within_4h_4d": 0.0, "share_over_4d": 0.0, "share_timestop": 0.0, "exit_reasons": {}, "trades": 0}
    h = sorted(t.holding_hours for t in trades)
    n = len(h)
    med = h[n // 2] if n % 2 else 0.5 * (h[n // 2 - 1] + h[n // 2])
    reasons = {}
    for t in trades:
        reasons[t.reason] = reasons.get(t.reason, 0) + 1
    return {"round_turns_per_year": n / years, "time_in_market": math.fsum(h) / total_hours, "holding_hours_mean": math.fsum(h) / n,
            "holding_hours_median": med, "share_within_4h_4d": sum(1 for x in h if 4 <= x <= 96) / n, "share_over_4d": sum(1 for x in h if x > 96) / n,
            "share_timestop": reasons.get("ZEITSTOPP", 0) / n, "exit_reasons": {k: v / n for k, v in sorted(reasons.items())}, "trades": n,
            "max_holding_hours": h[-1]}
