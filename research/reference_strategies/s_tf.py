"""S-TF – Trendfolge mehrerer Geschwindigkeiten (schnell), vorregistriert in research/strategy_family.md.

Mechanismus: kontinuierliche EWMA-Crossover-Prognosen je Geschwindigkeit, Prognoseskalierung und -kappung, Kombination mit gedeckeltem
Diversifikationsmultiplikator; diskrete Trades mit Einstiegs- und Ausstiegsschwelle (Hysterese), serverseitigem Schutzstopp,
Zeitstopp (Betreiber: höchstens 168 h) und Sperrzeit nach Zeitstopp. Einstiege nur im Liquiditätsfenster; Schutz- und Zeitausstiege jederzeit.
"""
from __future__ import annotations

from .common import BARS_PER_DAY, Book, Ewma, EwmaVol, cap, fdm, forecast_scalar


def raw_forecasts(prices, speeds, vol_span_h):
    """Rohprognosen je Geschwindigkeit: (EWMA_schnell − EWMA_langsam) / (Preis · σ_Tag)."""
    ew = [(Ewma(f), Ewma(s)) for f, s in speeds]
    vol = EwmaVol(vol_span_h)
    out = [[] for _ in speeds]
    prev = None
    for p in prices:
        if prev is not None:
            vol.update(p / prev - 1.0)
        prev = p
        sd = vol.daily() if vol.var is not None else 0.01
        for k, (a, b) in enumerate(ew):
            out[k].append((a.update(p) - b.update(p)) / (p * sd))
    return out


def combined_forecast(prices, speeds, fc_cap, fdm_cap, fc_scale, vol_span_h, warmup=None):
    raws = raw_forecasts(prices, speeds, vol_span_h)
    warm = warmup if warmup is not None else max(s for _, s in speeds)
    scalars = [forecast_scalar(r[warm:], fc_scale) for r in raws]
    scaled = [[cap(x * sc, fc_cap) for x in r] for r, sc in zip(raws, scalars, strict=True)]
    mult = fdm([s[warm:] for s in scaled], fdm_cap)
    comb = [cap(mult * sum(s[i] for s in scaled) / len(scaled), fc_cap) for i in range(len(prices))]
    return comb, {"scalars": scalars, "fdm": mult, "warmup": warm}


def run(bars, prm, carry_tilt=None) -> tuple[Book, dict]:
    """bars: Liste von Dicts mit price, hours, in_window. prm: Parameterwerte aus parameters.json."""
    prices = [b["price"] for b in bars]
    speeds = [tuple(x) for x in prm["P-STR-TF-SPEEDS"]]
    span = prm["P-STR-VOL-SPAN-D"] * BARS_PER_DAY
    comb, info = combined_forecast(prices, speeds, prm["P-STR-FC-CAP"], prm["P-STR-FDM-CAP"], prm["P-STR-FC-SCALE"], span)
    entry, exit_ = prm["P-STR-TF-ENTRY"], prm["P-STR-TF-EXIT"]
    book = Book(prm["P-OP-HOLD-MAX-H"], prm["P-STR-REENTRY-COOLDOWN-H"])
    vol = EwmaVol(span)
    prev = None
    for i, b in enumerate(bars):
        p, h = b["price"], b["hours"]
        if prev is not None:
            vol.update(p / prev - 1.0)
        prev = p
        if i < info["warmup"]:
            continue
        f = comb[i]
        sd = vol.daily()
        if book.open is not None:
            t = book.open
            if book.stop_hit(p):
                book.exit(i, p, h, "STOPP")
            elif book.time_stop_due(h):
                book.exit(i, p, h, "ZEITSTOPP")
            elif b["in_window"] and (t.direction * f < exit_):
                book.exit(i, p, h, "SIGNAL")
        if book.open is None and b["in_window"] and abs(f) >= entry:
            d = 1 if f > 0 else -1
            if book.can_enter(d, h):
                size = min(abs(f), prm["P-STR-FC-CAP"]) / prm["P-STR-FC-SCALE"]
                if carry_tilt is not None:
                    size *= carry_tilt(i, d)
                book.enter(d, i, p, h, size, prm["P-STR-STOP-ATR"] * sd)
    if book.open is not None:
        book.exit(len(bars) - 1, bars[-1]["price"], bars[-1]["hours"], "ENDE")
    return book, info
