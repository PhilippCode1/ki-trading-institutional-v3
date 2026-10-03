# Datenplan (§9)

> **Betreiberfassung.** Der Datenplan legt fest, welche Daten gekauft, wie sie geprüft, eingefroren und versiegelt werden und wer sie sehen darf. Für die CME-Gruppe reicht die Historie für Entwicklung und Holdout; für Eurex-Anleihen, SOFR- und €STR-Futures ist sie mit dem geplanten Datensatz zu kurz, deshalb sind diese Kontrakte derzeit nicht forschungsfähig. Eine längere Eurex-Historie über CQG würde rund <!--v:calc:eurex_full_history_cost_eur|eur-->10.306 EUR<!--/v--> zusätzlich kosten. Kursrohdaten bleiben in der Forschungszone und gehen nie an einen Sprachmodellanbieter. Für Go/No-Go heißt das: Der Datenplan trägt Demo und Forschung, das Universum bleibt aber auf Kontrakte mit ausreichender Historie beschränkt. Nächster Schritt ist G2: Lizenz prüfen, kaufen, abgleichen, einfrieren.

## 1 Datenarten

| Art | Inhalt | Quelle | Verwendung |
|---|---|---|---|
| Intraday-Historie | Minutenbalken aller Kontraktmonate einschließlich verfallener | Kibot (CME-Gruppe), Databento (Eurex ab 2018), CQG (Abgleich) | Forschung, Umschlag, Kosten, Backtest mit Produktionskern |
| Geld- und Briefkurse | Quotes im Liquiditätsfenster | Databento, CQG | Spread-Messung (X-DATA-VOL), Kostenmodell |
| Live-Kurse | Ticks und Balken über das MT5-Terminal | Broker (CQG-Anbindung) | Signale, Risiko, Pre-Trade-Kontrollen |
| Referenzdaten | Tick, Multiplikator, Tickwert, Handels- und Liquiditätszeiten, FND/LTD, Tageslimits | Börsen-Spezifikationen (R2a, R2b), Broker (`symbol_info`) | Referenzdatendienst (`data/reference_data_spec.md`) |
| Gebühren und Margins | Kommission, Börsengebühren, Initial- und Maintenance-Margin | Broker (X-BRK-FEES, X-BRK-MARGIN), Börse | Kostenmodell, Margin-Rechnung |
| Kalender | Handelstage, Feiertage, Notenbanktermine, Verfall | Börsen, Notenbanken | Ereignissperre (PTC-11), Rollfenster |
| Konto- und Ausführungsdaten | Orders, Deals, Positionen, Salden, Tagesauszüge | Broker | Abgleich, TCA, NAV |

## 2 Historie und Zulassung

Die Zulassung verlangt <!--v:prior:admission_rule/min_history_years|d0-->10<!--/v--> Jahre Intraday-Historie oder einen Proxy auf denselben Basiswert (§6.2, DEC-DS-24). Mit dem geplanten Datensatz fallen <!--v:calc:history_excluded_count|int-->16<!--/v--> handelbare Kontrakte heraus (<!--v:calc:history_excluded_symbols|raw-->10Y, 2YY, BTC, ETH, MBT, MET, SR1, SR3, ALI, FBTP, FGBL, FGBM, FGBS, FGBX, FOAT, FST3<!--/v-->). Zwei Wege würden das ändern: eine längere Eurex-Historie über CQG Data Factory (über zehn Jahre Intraday laut Anbieter; rund <!--v:calc:eurex_full_history_cost_eur|eur-->10.306 EUR<!--/v--> für die Eurex-Märkte) oder eine Anbieterbestätigung, dass die Historie länger ist als angenommen (X-DATA-HIST). Für SOFR- und €STR-Futures gibt es keinen Proxy mit gleichem Basiswert; sie bleiben bis zum Ablauf der nötigen Jahre ausgeschlossen.

## 3 Ablauf je Datensatz

1. **Lizenzprüfung** vor dem Kauf (X-DATA-LIC): interne Nutzung, automatisierter Handel, Speicherung, keine Weitergabe.
2. **Eingang:** Rohdateien unverändert ablegen, SHA-256 je Datei, Herkunft und Abrufdatum im Datenmanifest.
3. **Prüfung:** Lücken im Liquiditätsfenster (höchstens <!--v:param:P-DATA-GAP-MAX-MIN|d0-->15<!--/v--> Minuten, sonst Tag ungültig), Ausreißer gegen Tagesvolatilität, doppelte Zeitstempel, Handelszeiten gegen Referenzdaten.
4. **Abgleich zweier Quellen:** Schlusskurse je Balken auf <!--v:param:P-DATA-XCHECK-TOL-TICKS|d0-->1<!--/v--> Tick; mindestens <!--v:param:P-DATA-XCHECK-SHARE-MIN|pct0-->99 %<!--/v--> Übereinstimmung, sonst ist der Datensatz gesperrt bis zur Klärung.
5. **Einfrieren:** Nach <!--v:param:P-DATA-REVISION-DAYS|d0-->5<!--/v--> Geschäftstagen Revisionsfenster wird der Datensatz eingefroren; spätere Korrekturen nur als neue Version mit Begründung.
6. **Versiegeln:** Der Holdout (<!--v:param:P-RES-HOLDOUT-YEARS|d0-->2<!--/v--> Jahre, jüngster Abschnitt) wird bei G2 mit Hash versiegelt und in G4 genau einmal geöffnet (übernommen aus v2.0).
7. **Leckagetests:** Kein Signal darf Daten nach seinem Zeitstempel sehen; Prüfung durch Verschieben der Daten und Vergleich (übernommen aus v2.0).

## 4 Speicherung, Zugriff und Aufbewahrung

- Speicherung in der Forschungszone, unveränderlich mit Hash; der Geldpfad erhält nur Live-Kurse und Referenzdaten.
- Zugriff: Betreiber und Forschungsprozesse; Hermes nur auf abgeleitete Kennzahlen, Metadaten und Berichte (DEC-CF-07).
- Aufbewahrung: Rohdaten für die Lizenzdauer; Journale, Konto- und Ausführungsdaten nach Vorgabe der externen Person (BQ-03).

## 5 Kosten

Einmalige Datenkosten <!--v:cost:fixed_costs/historical_data_once_eur|eur-->3.477 EUR<!--/v-->; laufende Marktdaten im Basisfall <!--v:cost:fixed_costs/market_data_monthly_eur/ANZEIGE/monthly_eur|eur-->53 EUR<!--/v--> im Monat, bei Non-Display-Einstufung bis <!--v:cost:fixed_costs/market_data_monthly_eur/NON_DISPLAY_USER/monthly_eur|eur-->2.441 EUR<!--/v--> (X-DATA-ND). Details: `data/vendor_matrix.md`, `financials/economic_model.md`.
