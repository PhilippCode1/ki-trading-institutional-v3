"""S-REV – Kurzfrist-Umkehr über 1–3 Tage (vorregistriert, Prior nahe null, Hürde t > 3).

Mechanismus: Nach einer außergewöhnlichen 3-Tage-Bewegung (|z| ≥ Schwelle) wird dagegen gehandelt; Ausstieg bei Rückkehr (z kreuzt 0),
nach höchstens 72 h oder am Schutzstopp. Einstiege einmal je Tag zu Beginn der Kernzeit.
"""
from __future__ import annotations

import math

from .common import BARS_PER_DAY, Book, EwmaVol


def run(bars, prm) -> tuple[Book, dict]:
    zthr = prm["P-STR-REV-Z"]
    hold = prm["P-STR-REV-HOLD-H"]
    book = Book(prm["P-OP-HOLD-MAX-H"], prm["P-STR-REENTRY-COOLDOWN-H"])
    span = prm["P-STR-VOL-SPAN-D"] * BARS_PER_DAY
    vol = EwmaVol(span)
    prev = None
    lb = prm["P-STR-REV-LOOKBACK-D"]
    lag = lb * BARS_PER_DAY
    for i, b in enumerate(bars):
        p, h = b["price"], b["hours"]
        if prev is not None:
            vol.update(p / prev - 1.0)
        prev = p
        if i < max(lag, span):
            continue
        sd = vol.daily()
        z = (p / bars[i - lag]["price"] - 1.0) / (sd * math.sqrt(lb))
        if book.open is not None:
            t = book.open
            if book.stop_hit(p):
                book.exit(i, p, h, "STOPP")
            elif h - t.entry_hours >= hold:
                book.exit(i, p, h, "HALTEDAUER")
            elif book.time_stop_due(h):
                book.exit(i, p, h, "ZEITSTOPP")
            elif b["in_window"] and t.direction * z >= 0:
                book.exit(i, p, h, "SIGNAL")
        if book.open is None and b["window_pos"] == 0 and abs(z) >= zthr:
            d = -1 if z > 0 else 1
            if book.can_enter(d, h):
                book.enter(d, i, p, h, 1.0, prm["P-STR-REV-STOP-FACTOR"] * prm["P-STR-STOP-ATR"] * sd)
    if book.open is not None:
        book.exit(len(bars) - 1, bars[-1]["price"], bars[-1]["hours"], "ENDE")
    return book, {"z_threshold": zthr}
