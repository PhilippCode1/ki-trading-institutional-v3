# Proxy-Regel für kurze Historien (§6.5, EV-08)

> **Betreiberfassung.** Viele kleine Kontrakte (Micro, Mini) gibt es erst seit wenigen Jahren; für die Forschung wird ihre Historie deshalb aus dem Standardkontrakt auf denselben Basiswert rekonstruiert. Das ist nur zulässig, wenn der Basiswert wirklich derselbe ist; ein anderer Basiswert als Ersatz – wie in v2.0 der Micro Ultra 10-Year für die 10-Year Note – ist ohne Nachweis verboten. Kosten, Tick und Liquidität kommen immer vom tatsächlich gehandelten Kontrakt, nie vom Proxy. Die Paketprüfung kontrolliert jede Proxy-Zuordnung maschinell. Für Go/No-Go heißt das: Micro-Kontrakte sind für kleine Kapitalstufen forschungsfähig, SOFR-, €STR- und Renditefutures nicht. Nächster Schritt ist die Bestätigung der Listungsdaten in G2 (X-DATA-HIST).

## Regeln

| Nr. | Regel |
|---|---|
| PX-1 | Proxy nur auf **denselben Basiswert** mit derselben Abrechnungsart; das Feld `standard_ref` im Instrumentregister nennt ihn. Maschinell geprüft werden Risikoklasse, Währung und Notierung (Abweichung höchstens <!--v:param:P-DATA-PROXY-PRICE-TOL|pct0-->2 %<!--/v-->; derselbe Basiswert wird gleich notiert, ein anderer Basiswert gleicher Klasse wie Silber statt Gold fällt auf, `validation/semantic_checks.py::check_proxy`). |
| PX-2 | Aus dem Proxy stammen nur Preisbewegungen (Renditen, Volatilität, Signale). Kosten, Tick, Tickwert, Multiplikator, Mindestvolumen, Margin und Handelszeiten stammen immer vom gehandelten Kontrakt. |
| PX-3 | Abweichungen werden ausgewiesen: Multiplikator-Verhältnis, Tickgröße, Handelszeiten, Liquidität (Spread und Tagesvolumen werden für den Micro-Kontrakt selbst gemessen, X-DATA-VOL). |
| PX-4 | Unzulässig ohne Nachweis gleicher Preisbildung: anderer Basiswert (Micro Ultra 10-Year gegenüber 10-Year Note, SRC-CBOT-MTN; SOFR gegenüber Eurodollar; €STR gegenüber Euribor), Renditefutures gegenüber Preisfutures (2YY, 10Y), andere Währung. |
| PX-5 | Handelsplatzwechsel bei gleichem Basiswert (etwa NYMEX Brent gegenüber ICE Brent) nur mit dokumentiertem Abgleich der Abrechnungspreise; derzeit ist NYMEX Brent wegen widersprüchlicher Tickdaten ohnehin gesperrt. |
| PX-6 | Ein Proxy ersetzt nicht die Zulassungsprüfung: Kosten je Risikoeinheit und Kontraktgröße werden für den gehandelten Kontrakt gerechnet. |

## Zuordnungen im Register

<!-- GEN:BEGIN tab.proxies -->
| Kontrakt | Proxy (Standardkontrakt) | Börse | Multiplikator-Verhältnis | Historie Jahre (eigen / Proxy) | Prüfung | Befund |
|---|---|---|---|---|---|---|
| M6E | 6E | CME / CME | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| M6B | 6B | CME / CME | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MJY | 6J | CME / CME | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MSF | 6S | CME / CME | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MCD | 6C | CME / CME | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| M6A | 6A | CME / CME | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MCL | CL | NYMEX / NYMEX | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| BZ | B | NYMEX / ICEEU | 1,0000 | 0,0 / 8,7 | gleiche Klasse, Währung und Notierung | zulässig |
| QG | NG | NYMEX / NYMEX | 0,2500 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MNG | NG | NYMEX / NYMEX | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MGC | GC | COMEX / COMEX | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| 1OZ | GC | COMEX / COMEX | 0,0100 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| SIL | SI | COMEX / COMEX | 0,2000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| SIC | SI | COMEX / COMEX | 0,0200 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MHG | HG | COMEX / COMEX | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MZC | ZC | CBOT / CBOT | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MZS | ZS | CBOT / CBOT | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MZW | ZW | CBOT / CBOT | 0,1000 | 0,0 / 17,7 | gleiche Klasse, Währung und Notierung | zulässig |
| MBT | BTC | CME / CME | 0,0200 | 0,0 / 9,2 | gleiche Klasse, Währung und Notierung | zulässig |
| MET | ETH | CME / CME | 0,0020 | 0,0 / 5,2 | gleiche Klasse, Währung und Notierung | zulässig |
<!-- GEN:END tab.proxies -->

Die maschinelle Prüfung (`validation/validate_package.py`, Phase Registersemantik, und `validation/semantic_checks.py`) verlangt: Jede `standard_ref` existiert, ist ein Standardkontrakt, hat dieselbe Risikoklasse und Währung, und ein Wechsel des Handelsplatzes trägt einen Vermerk. Eine Mutation, die einen Proxy mit anderem Basiswert einträgt, muss scheitern (`validation/mutation_catalog.json`).
