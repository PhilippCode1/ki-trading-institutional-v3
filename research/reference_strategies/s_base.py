"""S-BASE – Referenz-Baseline TF-D1 aus v2.0 (Kanalausbruch mit Stopp in ATR; Werte P-STR-BASE-*; übernommen aus v2.0) und Variante TF-D1-7T.

TF-D1 hält Positionen typischerweise Wochen und verletzt damit die Betreiber-Grenze von 7 Tagen (BQ-04); sie dient nur als
Vergleichsbasis. TF-D1-7T ergänzt den Zeitstopp von 168 h und ist damit zulässig. Arbeitet auf Tagesschlusskursen (letzter Stundenbalken).
"""
from __future__ import annotations

from .common import BARS_PER_DAY, Book


def daily_closes(bars):
    out = []
    for i, b in enumerate(bars):
        if (i + 1) % BARS_PER_DAY == 0:
            out.append((i, b["price"], b["hours"]))
    return out


def run(bars, prm, time_stop: bool) -> tuple[Book, dict]:
    entry_n, exit_n = prm["P-STR-BASE-ENTRY-N"], prm["P-STR-BASE-EXIT-N"]
    atr_n, stop_atr = prm["P-STR-BASE-ATR-N"], prm["P-STR-BASE-STOP-ATR"]
    closes = daily_closes(bars)
    max_h = prm["P-OP-HOLD-MAX-H"] if time_stop else 1e12
    book = Book(max_h, prm["P-STR-REENTRY-COOLDOWN-H"] if time_stop else 0.0)
    atr = None
    for k in range(1, len(closes)):
        i, p, h = closes[k]
        tr = abs(p - closes[k - 1][1])
        atr = tr if atr is None else atr + (tr - atr) / atr_n
        if k < entry_n + 1:
            continue
        hist = [c[1] for c in closes[k - entry_n:k]]
        hist_x = [c[1] for c in closes[k - exit_n:k]]
        if book.open is not None:
            t = book.open
            if book.stop_hit(p):
                book.exit(i, p, h, "STOPP")
            elif book.time_stop_due(h):
                book.exit(i, p, h, "ZEITSTOPP")
            elif (t.direction > 0 and p < min(hist_x)) or (t.direction < 0 and p > max(hist_x)):
                book.exit(i, p, h, "KANAL")
        if book.open is None:
            d = 1 if p > max(hist) else (-1 if p < min(hist) else 0)
            if d and book.can_enter(d, h):
                book.enter(d, i, p, h, 1.0, stop_atr * atr / p)
    if book.open is not None:
        i, p, h = closes[-1]
        book.exit(i, p, h, "ENDE")
    return book, {"entry_n": entry_n, "exit_n": exit_n, "time_stop": time_stop}
