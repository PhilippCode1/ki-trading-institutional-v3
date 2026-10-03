#!/usr/bin/env python3
"""Referenzimplementierung der Strategieregeln TF-D1 (Konzeptpaket v2.0).

Status
------
REFERENZFUNKTION des Konzeptpakets, kein Produktionscode. Sie legt die Semantik der registrierten
Strategie TF-D1 (Masterkonzept_v2.0.md, Abschnitt MK-5.5) ausführbar fest und dient

1. als unabhängiges Orakel für die spätere Implementierung im Fachkern (Anforderungen REQ-STR-*),
2. als Regelkern des Aktivitätsmodells (research/activity_model.py).

Nur Python-Standardbibliothek. Preise als float (Forschungsnumerik; Toleranzen in den Tests).
Geldbeträge werden hier nicht berechnet (siehe financials/financial_calculator.py).

Regeln TF-D1 (führende Quelle der Zahlenwerte: parameters.json)
----------------------------------------------------------------
R1  Tageskerze = Handelstag der Heimatbörse, Close = offizieller Settlement-Preis (P-STR-001).
    Signale nur aus abgeschlossenen, finalen Kerzen (P-STR-007, P-DAT-008).
R2  Einstieg bei KREUZUNG des 55-Kerzen-Kanals (P-STR-002): Long, wenn C_t > U55_t und C_{t-1} <= U55_{t-1}.
    U55_t = Maximum der Highs der 55 Kerzen t-55..t-1 (ohne t). Short spiegelbildlich.
R3  Ausführung im Ausführungsfenster der nächsten Sitzung t+1 (P-STR-010). Ist t+1 verkürzt (kein
    Fenster), verfällt das Signal (P-STR-014). Keine Nachholung in späteren Sitzungen (P-STR-013).
R4  Anfangsstop an der Einstiegsorder angehängt und vor dem Fill festgelegt: S = L -/+ D mit D = 2,0 x ATR20_t
    (Wilder, P-STR-004/005) und L = Limitpreis der Einstiegsorder. Weil der Fill höchstens L erreicht, ist der
    Abstand zum Fill höchstens D; der Stop wird nach dem Fill nie erweitert. Replay-Näherung RA-3: Fill = L =
    Eröffnung t+1 +/- halber Spread, also Abstand genau D.
R5  Stopnachführung nach jedem Kerzenschluss s: Long-Stop = max(Stop, L20) mit L20 = Minimum der Lows der
    20 Kerzen s-19..s (Kanal der Folgekerze, P-STR-003). Short spiegelbildlich. Nur enger, nie weiter.
    Enthält das 20er-Fenster eine ungültige Kerze, bleibt der Stop unverändert.
R6  Einziger regulärer Ausstieg ist der brokerseitige Stop (Anfangsstop oder nachgeführter Kanalstop).
    Kurslücke durch den Stop: Füllung zum Eröffnungskurs, nicht zum Stoppreis.
R7  Keine Positionsaufstockung, kein Flip, keine Höchsthaltedauer, kein Wochenschluss-Zwangsausstieg.
R8  Lückenpolitik: Ein Kanal existiert nur, wenn alle Kerzen seines Fensters gültig sind (P-DAT-006).
    True Range der ersten gültigen Kerze: High - Low; sonst mit dem Schluss der letzten GÜLTIGEN Kerze.
    Aufwärmphase und Lückenpolitik sind dieselbe Regel: ein Signal an Kerze t braucht die Kerzen t-56 .. t gültig,
    also WARMUP_BARS = ENTRY_N + 2 = 57 aufeinanderfolgende gültige Kerzen (P-DAT-004).

Replay-Näherungen (nur Tagesdaten; live gelten Kalender, Quote und Brokerstop):
RA-1 Ist die Ausführungskerze t+1 in den Daten ungültig, gibt es im Replay keinen simulierbaren Fill; der Einstieg
     wird als ENTRY_DATA_GAP_REPLAY gezählt und berichtet (live entscheidet allein der Kalender, R3).
RA-2 Auf ungültigen Kerzen wird kein Stop geprüft; die nächste gültige Kerze prüft ihn mit Lückenregel R6.
RA-3 siehe R4.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

ENTRY_N = 55
TRAIL_N = 20
ATR_N = 20
STOP_K = 2.0
WARMUP_BARS = ENTRY_N + 2


@dataclass(frozen=True)
class Bar:
    """Eine Tageskerze (Mid-Preise). valid=False markiert eine Datenlücke."""
    high: float
    low: float
    close: float
    open: float
    valid: bool = True
    short_session: bool = False         # verkürzte Sitzung ohne Ausführungsfenster: keine neuen Einstiege


def true_ranges(bars: Sequence[Bar]) -> List[Optional[float]]:
    """True Range je Kerze; None für ungültige Kerzen (R8)."""
    out: List[Optional[float]] = []
    prev_close: Optional[float] = None
    for b in bars:
        if not b.valid:
            out.append(None)
            continue
        if prev_close is None:
            tr = b.high - b.low
        else:
            tr = max(b.high - b.low, abs(b.high - prev_close), abs(b.low - prev_close))
        out.append(tr)
        prev_close = b.close
    return out


def wilder_atr(bars: Sequence[Bar], n: int = ATR_N) -> List[Optional[float]]:
    """ATR nach Wilder über gültige Kerzen.

    Initialisierung: arithmetisches Mittel der ersten n gültigen True Ranges (Wert an der n-ten gültigen
    Kerze). Danach ATR_t = ((n-1) * ATR_prev + TR_t) / n. Ungültige Kerzen erhalten None und verändern den
    Rekursionszustand nicht.
    """
    trs = true_ranges(bars)
    out: List[Optional[float]] = []
    seen: List[float] = []
    atr: Optional[float] = None
    for tr in trs:
        if tr is None:
            out.append(None)
            continue
        if atr is None:
            seen.append(tr)
            if len(seen) == n:
                atr = sum(seen) / n
                out.append(atr)
            else:
                out.append(None)
        else:
            atr = ((n - 1) * atr + tr) / n
            out.append(atr)
    return out


def channel(bars: Sequence[Bar], t: int, n: int, kind: str) -> Optional[float]:
    """Kanalwert für Kerze t aus den n vorhergehenden Kerzen t-n .. t-1 (ohne t).

    kind='upper' -> Maximum der Highs, kind='lower' -> Minimum der Lows. None, wenn das Fenster nicht
    vollständig existiert oder eine ungültige Kerze enthält (R8).
    """
    if kind not in ("upper", "lower"):
        raise ValueError("kind muss 'upper' oder 'lower' sein")
    if t - n < 0 or t > len(bars):
        return None
    window = bars[t - n:t]
    if any(not b.valid for b in window):
        return None
    return max(b.high for b in window) if kind == "upper" else min(b.low for b in window)


@dataclass
class EntrySignal:
    long_entry: bool = False
    short_entry: bool = False
    blocked_reason: Optional[str] = None   # BAR_INVALID, PREV_BAR_INVALID, GAP_OR_WARMUP_IN_ENTRY_WINDOW, ATR_UNAVAILABLE


def entry_signal_at(bars: Sequence[Bar], atr: Sequence[Optional[float]], t: int,
                    entry_n: int = ENTRY_N) -> EntrySignal:
    """Einstiegssignal an der abgeschlossenen Kerze t (R2, R8)."""
    s = EntrySignal()
    b = bars[t]
    if not b.valid:
        s.blocked_reason = "BAR_INVALID"
        return s
    if t < 1 or not bars[t - 1].valid:
        s.blocked_reason = "PREV_BAR_INVALID"
        return s
    u_t = channel(bars, t, entry_n, "upper")
    l_t = channel(bars, t, entry_n, "lower")
    u_p = channel(bars, t - 1, entry_n, "upper")
    l_p = channel(bars, t - 1, entry_n, "lower")
    if None in (u_t, l_t, u_p, l_p):
        s.blocked_reason = "GAP_OR_WARMUP_IN_ENTRY_WINDOW"
        return s
    if atr[t] is None:
        s.blocked_reason = "ATR_UNAVAILABLE"
        return s
    c_prev = bars[t - 1].close
    if b.close > u_t and c_prev <= u_p:
        s.long_entry = True
    if b.close < l_t and c_prev >= l_p:
        s.short_entry = True
    return s


def trailed_stop(bars: Sequence[Bar], s: int, direction: int, current_stop: float,
                 trail_n: int = TRAIL_N) -> float:
    """Stop für die Kerze s+1 nach Abschluss von Kerze s (R5). Nur enger, nie weiter."""
    if direction > 0:
        lvl = channel(bars, s + 1, trail_n, "lower")
        return current_stop if lvl is None else max(current_stop, lvl)
    lvl = channel(bars, s + 1, trail_n, "upper")
    return current_stop if lvl is None else min(current_stop, lvl)


def execution_bar_index(bars: Sequence[Bar], t: int) -> Optional[int]:
    """Index der Kerze, in deren Ausführungsfenster ein Signal von Kerze t ausgeführt wird (R3): t+1."""
    j = t + 1
    return j if j < len(bars) else None


def priority_key(date_iso: str, instrument_id: str) -> str:
    """Deterministische, über die Zeit neutrale Reihenfolge gleichzeitiger Einstiege (P-RSK-012).

    Sortierschlüssel = SHA-256(date_iso + '|' + instrument_id) als Hex-String, aufsteigend.
    Ersetzt die feste Symbolreihenfolge aus v1.0 (Befund N-5).
    """
    return hashlib.sha256(f"{date_iso}|{instrument_id}".encode("utf-8")).hexdigest()


def stop_hit(bar: Bar, direction: int, stop: float, half_spread: float, entry_bar: bool,
             entry_bar_mode: str = "full_bar") -> Optional[float]:
    """Prüft, ob der Schutzstop in 'bar' auslöst, und liefert den Füllpreis (R6).

    Long-Stops lösen auf der Bid-Seite aus (Bid = Mid - halber Spread), Short-Stops auf der Ask-Seite.
    Kurslücke durch den Stop: Füllung zum Eröffnungskurs (T19 aus v1.0). Einstiegskerze mit Tagesdaten:
    'full_bar' wertet die ganze Kerze (konservativ, Entwicklung), 'close_only' nur den Schluss
    (Sensitivität). Mit Intraday-Daten entfällt die Näherung (research/research_plan.md#RP-4).
    """
    if entry_bar_mode not in ("full_bar", "close_only"):
        raise ValueError("entry_bar_mode unbekannt")
    if direction > 0:
        o_bid, l_bid, c_bid = bar.open - half_spread, bar.low - half_spread, bar.close - half_spread
        if not entry_bar and o_bid <= stop:
            return o_bid
        probe = c_bid if (entry_bar and entry_bar_mode == "close_only") else l_bid
        return stop if probe <= stop else None
    o_ask, h_ask, c_ask = bar.open + half_spread, bar.high + half_spread, bar.close + half_spread
    if not entry_bar and o_ask >= stop:
        return o_ask
    probe = c_ask if (entry_bar and entry_bar_mode == "close_only") else h_ask
    return stop if probe >= stop else None


@dataclass
class Trade:
    direction: int            # +1 long, -1 short
    signal_bar: int
    entry_bar: int
    entry_price: float
    initial_stop: float
    stop_distance: float
    stop: float
    exit_bar: Optional[int] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None   # INITIAL_STOP oder TRAIL_STOP

    def r_multiple(self) -> Optional[float]:
        if self.exit_price is None:
            return None
        return self.direction * (self.exit_price - self.entry_price) / self.stop_distance


@dataclass
class InstrumentRun:
    trades: List[Trade] = field(default_factory=list)
    open_trade: Optional[Trade] = None
    blocked: dict = field(default_factory=dict)


def run_single_instrument(bars: Sequence[Bar], half_spread: float,
                          entry_bar_mode: str = "full_bar",
                          stop_k: float = STOP_K) -> InstrumentRun:
    """Einzelinstrument-Referenzlauf ohne Portfolio-Kappungen (Orakel für Tests und Diagnosen).

    Ausführung im Handelsfenster zum Eröffnungs-Mid +/- halber Spread (Tagesdaten-Näherung APPROX_EXEC,
    nur Entwicklung; research/research_plan.md#RP-4). Reihenfolge je Kerze t:
    (0) fälliger Einstieg, (1) Stopprüfung, (2) Stopnachführung nach Schluss, (3) Einstiegssignal.
    """
    atr = wilder_atr(bars)
    run = InstrumentRun()
    pos: Optional[Trade] = None
    pending: Optional[tuple] = None   # (direction, signal_bar, exec_bar)
    for t, bar in enumerate(bars):
        just_entered = False
        if pending is not None and pending[2] == t:
            direction, sig_bar, _ = pending
            pending = None
            if pos is None and not bar.short_session and bar.valid:
                d = stop_k * atr[sig_bar]
                px = bar.open + half_spread if direction > 0 else bar.open - half_spread
                stop = px - d if direction > 0 else px + d
                pos = Trade(direction, sig_bar, t, px, stop, d, stop)
                just_entered = True
            elif pos is not None or bar.short_session:
                run.blocked["ENTRY_NOT_EXECUTABLE"] = run.blocked.get("ENTRY_NOT_EXECUTABLE", 0) + 1
            else:
                run.blocked["ENTRY_DATA_GAP_REPLAY"] = run.blocked.get("ENTRY_DATA_GAP_REPLAY", 0) + 1
        if pos is not None and bar.valid:
            fill = stop_hit(bar, pos.direction, pos.stop, half_spread, just_entered, entry_bar_mode)
            if fill is not None:
                pos.exit_bar, pos.exit_price = t, fill
                pos.exit_reason = "INITIAL_STOP" if pos.stop == pos.initial_stop else "TRAIL_STOP"
                run.trades.append(pos)
                pos = None
        if pos is not None:
            pos.stop = trailed_stop(bars, t, pos.direction, pos.stop)
        sig = entry_signal_at(bars, atr, t)
        if sig.blocked_reason:
            run.blocked[sig.blocked_reason] = run.blocked.get(sig.blocked_reason, 0) + 1
        j = execution_bar_index(bars, t)
        if j is None or pos is not None:
            continue
        if sig.long_entry and not sig.short_entry:
            pending = (1, t, j)
        elif sig.short_entry and not sig.long_entry:
            pending = (-1, t, j)
    run.open_trade = pos
    return run


if __name__ == "__main__":
    # Selbsttest: Seitwärtsphase, Aufwärtstrend, Umkehr -> genau ein Long-Trade mit nachgeführtem Stop.
    bars = []
    price = 100.0
    for i in range(160):
        if 80 <= i < 120:
            price += 0.5
        elif i >= 120:
            price -= 0.8
        bars.append(Bar(high=price + 0.2, low=price - 0.2, close=price, open=price))
    r = run_single_instrument(bars, half_spread=0.01)
    print("Trades:", [(tr.direction, tr.signal_bar, tr.entry_bar, tr.exit_bar, tr.exit_reason,
                       round(tr.r_multiple(), 3)) for tr in r.trades])
    print("Blockiert:", r.blocked)
