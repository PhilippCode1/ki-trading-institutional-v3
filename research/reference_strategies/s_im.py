"""S-IM – Intraday-Momentum über die Kernhandelszeit (vorregistriert).

Mechanismus (Literatur: Gao u. a. 2018; Baltussen u. a. 2021): Die Rendite vom Beginn der Kernzeit bis zum Messpunkt sagt die Richtung
des Rests der Kernzeit voraus. Abweichung zur Literatur: Haltedauer bis Kernzeitende (≈ 4 h, Standard-Haltedauer BQ-04) statt der
letzten 30 Minuten – der Literatur-Prior wird deshalb mit einem Übertragungsabschlag versehen (research/prior_derivation.py).
Höchstens ein Trade je Tag und Instrument; Schutzstopp beim Broker; Ausstieg spätestens am Kernzeitende.
"""
from __future__ import annotations

from .common import BARS_PER_DAY, Book, EwmaVol


def run(bars, prm) -> tuple[Book, dict]:
    """bars: Dicts mit price, hours, in_window, day, window_pos (Stunde innerhalb der Kernzeit, sonst −1), window_len."""
    sig_h = int(round(prm["P-STR-IM-SIGNAL-MIN"] / 60))
    hold_h = prm["P-STR-IM-HOLD-H"]
    book = Book(prm["P-OP-HOLD-MAX-H"], 0.0)
    span = prm["P-STR-VOL-SPAN-D"] * BARS_PER_DAY
    min_move_sd = prm["P-STR-IM-MIN-MOVE-SD"]
    vol = EwmaVol(span)
    prev = None
    open_price = None
    traded_day = None
    for i, b in enumerate(bars):
        p, h = b["price"], b["hours"]
        if prev is not None:
            vol.update(p / prev - 1.0)
        prev = p
        if b["window_pos"] == 0:
            open_price = p
        if book.open is not None:
            t = book.open
            if book.stop_hit(p):
                book.exit(i, p, h, "STOPP")
            elif h - t.entry_hours >= hold_h or b["window_pos"] == b["window_len"] - 1 or not b["in_window"]:
                book.exit(i, p, h, "KERNZEITENDE")
        if (book.open is None and b["window_pos"] == sig_h and open_price is not None and traded_day != b["day"]
                and i > span):
            sd = vol.daily()
            move = p / open_price - 1.0
            if abs(move) >= min_move_sd * sd:
                d = 1 if move > 0 else -1
                book.enter(d, i, p, h, 1.0, prm["P-STR-STOP-ATR"] * sd * prm["P-STR-IM-STOP-FACTOR"])
                traded_day = b["day"]
    if book.open is not None:
        book.exit(len(bars) - 1, bars[-1]["price"], bars[-1]["hours"], "ENDE")
    return book, {"signal_hour": sig_h, "min_move_sd": min_move_sd}
