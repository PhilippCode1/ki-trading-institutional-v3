# Steuern: Umfang und Übergabe (§5.3, §15, Umfang nach BQ-03)

> **Betreiberfassung.** Das Paket berät nicht zu Steuern und rechnet keine Steuerszenarien; nach BQ-03 regelt das eine externe Person. In der Wirtschaftsrechnung steht nur eine pauschale Sensitivität, die positive Jahreswerte um <!--v:param:P-ECO-TAX-SENS|pct0-->30 %<!--/v--> kürzt und Verluste ungekürzt lässt. Das System liefert der externen Person einen vollständigen Export aller steuerlich relevanten Vorgänge. Bis zur schriftlichen Bestätigung der Behandlung bleibt der Pilot gesperrt. Für Go/No-Go heißt das: Steuern ändern den Befund nicht, sind aber eine Sperre vor G8. Nächster Schritt: Übergabe des Exportformats an die externe Person (X-TAX-01).

## 1 Was das Paket rechnet

Nur die Sensitivität SZ-STEUER_SENSITIVITAET (`financials/tax_scenarios.py`); Beispielwerte in `financials/tax_sensitivity_example.json`. Kein Verlustvortrag, keine Verlustverrechnungsbeschränkung, keine Kirchensteuer, kein Solidaritätszuschlag, keine Körperschaft- oder Gewerbesteuer.

## 2 Fragen an die externe Person

| Nr. | Frage | Sperre |
|---|---|---|
| ST-1 | Steuerliche Behandlung von Gewinnen und Verlusten aus Futures im Eigenkonto einschließlich Verlustverrechnung nach aktueller Rechtslage | G8 |
| ST-2 | Behandlung von Fremdwährungsgewinnen und -verlusten auf USD-Salden beim Broker | G8 |
| ST-3 | Erklärungspflichten bei einem Broker ohne inländischen Steuerabzug | G8 |
| ST-4 | Abzugsfähigkeit von Kosten (Daten, VPS, KI-Abo, Prüfungen) | G8 |
| ST-5 | benötigte Belege und Aufbewahrungsfristen (`governance/policies/retention_policy.md`) | G8 |

## 3 Exportformat für die externe Person

Je Kalenderjahr als CSV und PDF: jede Order und jeder Deal mit Zeitstempel (UTC und Europe/Berlin), Kontrakt, Menge, Preis, Kommission und Gebühren, realisierter Gewinn oder Verlust in Kontraktwährung und EUR (Umrechnung mit dem EZB-Referenzkurs des Tages, SRC-ECB-FXREF), Rollvorgänge, Zinsen und Gutschriften des Brokers, Ein- und Auszahlungen (aus dem Kundenportal, nicht vom System), Jahresauszug des Brokers als Abgleich. Das System erzeugt den Export; die Bewertung nimmt die externe Person vor.
