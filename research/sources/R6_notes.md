# R6 – Make-or-Buy: Open-Source-Frameworks

Abruf: **2026-09-24** · Maschinenlesbare Belege (URL, wörtliches Zitat, Art der Quelle): `R6_make_or_buy.json`
Statuswerte: `BELEGT` · `TEILWEISE` · `NICHT_GEPRUEFT`.

## Methode und Grenzen

- Nur direkte Abrufe der Projektseiten und der offiziellen Dokumentation mit WebFetch. Das Websuche-Budget der Sitzung war erschöpft, deshalb gab es keine Suche nach weiteren Quellen.
- Das Abruf-Tool fasst Seiten mit einem kleinen Modell zusammen. „Nicht erwähnt“ ist deshalb nur ein schwacher Negativbefund. Die Aussage „keine MT5-Anbindung“ bezieht sich auf die offiziellen Integrationslisten vom 24.09.2026.
- Kommerzielle Plattformen wurden nicht recherchiert: Nach BQ-08 kommt nur MT5 in Frage, und keine dieser Plattformen wurde als MT5-Brücke bewertet (`NICHT_GEPRUEFT`).

## Befunde

| Framework | Lizenz | offizielle Anbindungen (Auszug) | MT5 gelistet | Status |
|---|---|---|---|---|
| NautilusTrader | LGPL-3.0 | Interactive Brokers, Databento, Binance, Bybit, Betfair u. a. (19 Einträge) | nein | BELEGT |
| QuantConnect LEAN | Apache-2.0 | Interactive Brokers, TradeStation, Tradier, Trading Technologies, FIX, OANDA (CFD/FX) u. a. (23 Einträge) | nein | BELEGT |
| pysystemtrade | GPL-3.0 („GNU v3“) | Interactive Brokers über ib_insync | nein | BELEGT |

**Zusätzliche Angaben:**

- NautilusTrader nennt gleiche Strategie- und Ausführungslogik für Backtest und Live.
- pysystemtrade führt Rollkalender und rückwärts angepasste Preise (Panama-Methode). Der Autor schließt jede Gewährleistung und jeden Support aus.
