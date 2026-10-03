# Spezifikation des Referenzdatendienstes (§4.1 Baustein 5, §9.2)

> **Betreiberfassung.** Der Referenzdatendienst hält alle Kontraktdaten, die Kosten, Größen und Termine bestimmen – Tick, Multiplikator, Gebühren, Margins, Handels- und Liquiditätszeiten, Verfalls- und Liefertermine – mit Gültigkeitsdatum und Quelle. Nichts wird überschrieben; jede Änderung ist eine neue Version, damit jede frühere Entscheidung mit den damals gültigen Daten nachvollziehbar bleibt. Der Dienst gleicht täglich gegen die Angaben des Brokers in MT5 ab und sperrt ein Instrument bei Widerspruch. Heute sind viele Felder noch Planungswerte mit Status ANNAHME; G1 und G2 ersetzen sie durch Belege. Für Go/No-Go heißt das: Ohne bestätigte Referenzdaten kein Echtgeld. Nächster Schritt ist die Kontraktliste des Brokers (X-BRK-CONTRACTS).

## 1 Datensätze und Felder

| Datensatz | Felder | Quelle | Status heute |
|---|---|---|---|
| Kontraktspezifikation | Instrument-ID, Börse, Symbol, Broker-Symbol (MT5), Multiplikator, Tick, Tickwert, Währung, Abrechnung (bar/physisch), Standardkontrakt (Proxy) | Börsen-Rulebook (SRC-SPEC-*), `symbol_info` | belegt oder teilweise (`registers/instruments.json`) |
| Handelszeiten | Sitzungen je Wochentag in Börsenzeit und UTC, Pausen, Feiertage | Börse; in MT5 nur über MQL5 abrufbar | teilweise |
| Liquiditätsfenster | Kernzeit mit engem Spread je Instrument | Messung aus Intraday-Daten (X-DATA-LIQ) | Annahme |
| Termine | First Notice Day, Last Trading Day, Rollfenster (P-UNI-ROLL-DAYS), Energie-Sonderregel (P-UNI-ENERGY-EXPIRY-DAYS) | Börse, Broker (Phase CLOSEONLY) | Regeln belegt, Kalender je Kontraktmonat offen |
| Tageslimits und Preisbänder | Limit-Regeln je Kontrakt, Ausweitungsstufen | Börse (SRC-LIMIT-*) | teilweise |
| Margins | Initial und Maintenance je Kontrakt, Börse und Broker, Intraday und Übernacht | Broker (X-BRK-MARGIN), Börse | Annahme je Risikoklasse |
| Gebühren | Kommission je Seite, Staffel, Börsen- und Clearinggebühren, Marktdaten | Broker (X-BRK-FEES), `registers/costs.json` | Kommission belegt, Rest offen |
| Kalender | Notenbanktermine, wichtige Berichte, Verfall | Notenbanken, Börsen | offen (Pflege ab BS-05) |

Jeder Eintrag trägt `valid_from`, `valid_to` (leer = gültig), `source` (Quellen-ID), `retrieved` (Abrufdatum) und `status` (BELEGT, TEILWEISE, ANNAHME, WIDERSPRUCH). Das Datenschema für Verträge und Beispiele liegt in `schemas/`.

## 2 Versionierung

- Nur Anhängen: Eine Änderung schließt die alte Version mit `valid_to` und legt eine neue an; nichts wird gelöscht.
- Punktgenau: Forschung und Abgleich lesen die Version, die zum jeweiligen Zeitpunkt galt.
- Jede Version hat einen Hash; Rechner und Journal vermerken den Hash der verwendeten Referenzdaten.

## 3 Prüfungen

| Prüfung | Regel | Reaktion |
|---|---|---|
| Tickwert | Tickwert = Multiplikator × Tick (Validator, Phase Registersemantik) | Instrument gesperrt |
| Broker-Abgleich | täglich `symbol_info` gegen die gültige Version: Kontraktgröße, Tick, Tickwert, Volumenschritt, Handelsmodus, Margins | Sperrgrund und Incident bei Abweichung |
| Termine | FND ≤ LTD; Rollfenster vor FND/LTD; CLOSEONLY-Beginn beim Broker passt zum Kalender (KT-11) | Einstiegssperre für den Kontraktmonat |
| Sitzungen | keine Überlappung; Liquiditätsfenster innerhalb der Sitzung | Instrument gesperrt |
| Status | Echtgeld nur mit Status BELEGT für Tick, Tickwert, Multiplikator, Margins und Gebühren | Grant verweigert (G8) |

## 4 Nutzer

Kostenmodell und alle Rechner (über `registers/instruments.json` und `registers/costs.json`), Portfoliomotor (Größen), Risikomotor (Margin, Lückenregel, Handelszeiten, Ereignissperre), OMS (Rollfenster, Sitzungen), Prüfmodul (unabhängige Nachrechnung) und das Betreibercockpit (Anzeige der gültigen Werte mit Status).
