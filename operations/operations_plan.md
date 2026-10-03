# Betriebsplan (§14.1)

> **Betreiberfassung.** Der Betrieb braucht im Plan rund <!--v:dmc:operator_hours_per_year|d0-->314<!--/v--> Stunden deiner Zeit im Jahr: tägliche Kontrolle, wöchentliche Risikorunde, monatlicher Abgleich, Incidents, Modellprüfung, Drills und die Pflege des KI-Agenten. Diese Zeiten sind Annahmen und werden im Paper-Betrieb gemessen; sie gehen mit <!--v:param:P-ECO-HOURLY-RATE|d0-->50<!--/v--> EUR je Stunde in die Wirtschaftsrechnung ein. Das System arbeitet selbstständig, stoppt aber bei Unklarheit und wartet auf deine signierte Entscheidung. Für kurze Reaktionszeiten im Echtgeldbetrieb braucht es eine Notfallvertretung. Für Go/No-Go heißt das: Der Aufwand ist tragbar, die Einzelbesetzung ist die Schwachstelle. Nächster Schritt: Zeitmessung der Routinen im Paper-Betrieb (G7).

## 1 Routinen

| Routine | Inhalt | Zeit (Planwert) | Parameter |
|---|---|---|---|
| täglich | Tagesbericht lesen (Risiko, Leiterstufe, Kosten, Abweichungen), Abgleich bestätigen, Testalarm quittieren | <!--v:param:P-OPS-DAILY-MIN|d0-->20<!--/v--> Minuten je Handelstag | P-OPS-DAILY-MIN |
| wöchentlich | Risikorunde: Limits, Kostenverhältnis, Incidents, Freigabewarteschlange, gestagte Gedächtniseinträge des Agenten, Erreichbarkeit bestätigen | <!--v:param:P-OPS-WEEKLY-MIN|d0-->90<!--/v--> Minuten | P-OPS-WEEKLY-MIN |
| monatlich | Performance-Attribution, NAV- und Buchhaltungsabgleich mit dem Brokerauszug, Kostenabgleich, Restoreprobe | <!--v:param:P-OPS-MONTHLY-MIN|d0-->240<!--/v--> Minuten | P-OPS-MONTHLY-MIN |
| Incidents | Klärung nach Runbook | <!--v:param:P-OPS-INCIDENT-MIN|d0-->180<!--/v--> Minuten im Monat | P-OPS-INCIDENT-MIN |
| quartalsweise | Modellprüfung, Drills, Nutzenbilanz des Agenten, Rotation der Evaluationsfälle | <!--v:param:P-OPS-QUARTERLY-MIN|d0-->480<!--/v--> Minuten | P-OPS-QUARTERLY-MIN |
| je Agent-Update | Evaluationsbericht prüfen, Release freigeben | <!--v:param:P-AI-UPDATE-EFFORT-H|d0-->3<!--/v--> Stunden | P-AI-UPDATE-EFFORT-H |

Summe im Plan: <!--v:dmc:operator_hours_per_year|d0-->314<!--/v--> Stunden im Jahr (`financials/decision_montecarlo.py`, Funktion der Betreiberzeit).

## 2 Bereitschaft

Handelszeiten der gehandelten Börsen sind nahezu rund um die Uhr; der Betreiber ist nicht ständig erreichbar. Deshalb gilt: Das System schützt sich selbst (Stopps beim Broker, Leitern, Sperrgründe) und eskaliert über zwei Alarmkanäle. Ziele für Quittungen in `operations/sla_slo.md`; ohne Vertretung sind sie für den Echtgeldbetrieb nicht zusicherbar (X-ORG-DEPUTY sperrt G8).

## 3 Incident- und Problemmanagement

Incidents nach `governance/policies/incident_policy.md`; jedes Runbook in `operations/runbooks.md` nennt Auslöser, Schritte und Abschluss. Post-Mortem für kritische und hohe Incidents; wiederkehrende Ursachen werden als Problem mit Maßnahme und Termin geführt und in der wöchentlichen Risikorunde verfolgt.

## 4 NAV, Buchhaltung und Berichte

Täglich: NAV je Konto und Strategie aus Brokerdaten; Abgleich von Positionen, Deals und Kosten mit dem Tagesauszug; P&L-Erklärung (Preis, Kosten, Rollen, Währung). Monatlich: Attribution je Strategie, Instrument und Kostenart; Export für die externe Person (`legal/tax_matrix.md`). Jährlich: Strategie- und Wirtschaftlichkeitsprüfung mit Neuberechnung aller Rechner.

## 5 Notfallprioritäten (übernommen aus v2.0)

1. Positionen schützen (Stopps beim Broker, keine neuen Einstiege).
2. Klarheit über Bestände herstellen (Abgleich, UNKNOWN klären).
3. Ursache beheben und dokumentieren.
4. Erst danach wieder Risiko aufnehmen – nur mit signierter Entscheidung.
