# Organisation, Rollen und RACI (§13)

> **Betreiberfassung.** Du bist Betreiber, Portfolioverantwortlicher und einziger Befugter für den Wechsel zwischen Demo und Echtgeld; daran ändert das Paket nichts. Für Echtgeld verlangt es zusätzlich zwei Menschen: eine externe Risikofunktion, die nicht portfolioverantwortlich ist und Profilaufstiege sowie riskante Änderungen blockieren kann, und eine Notfallvertretung, die im Ernstfall nur pausieren und abbauen darf. KI-Agenten zählen nie als zweite Instanz. Fehlt die Vertretung, ist der Pilot gesperrt; fehlt die Risikofunktion, der Standardbetrieb. Für Go/No-Go heißt das: Mindestbesetzung zwei Personen ab G8, drei Rollen ab G9. Nächster Schritt: Benennung der Personen (X-ORG-DEPUTY, X-ORG-RISK).

## 1 Rollen

| Rolle | Person | Befugnisse | ab |
|---|---|---|---|
| Betreiber (B) | Betreiber | Strategie, Parameter, Releases, Grants, Moduswechsel Demo/Echtgeld (BQ-09), Kill-Switch, Budget | sofort |
| Externe Risikofunktion (R) | unabhängige Person, nicht portfolioverantwortlich (X-ORG-RISK) | Lesezugriff auf Cockpit und Berichte; Veto bei Profilaufstieg und Änderungen der Klassen C und D; zweite Freigabe | G9 (empfohlen ab G8) |
| Notfallvertretung (V) | benannte Person (X-ORG-DEPUTY) | Pause, Kill-Switch, Abbau; keine Risikoerhöhung, keine Grants | G8 |
| Externe Person Recht und Steuern (E) | nach BQ-03 | Anwendbarkeit, Steuern, Übergabeformate | vor G8 |
| Externe Prüfer (P) | beauftragt | Gegenprüfung des Pakets (X-REVIEW), Penetrationstest, Audit (G10) | je Stufe |
| KI-Agent (K) | Hermes | Entwürfe, Berichte, Sichtung; keine Freigabewirkung | H1 |
| Coding-Agent (C) | Werkzeug im Systembau (`implementation/CODING_AGENT_START.md`) | Code und Tests nach Arbeitspaket; kein Zugang zu Broker, Secrets, Holdout und Signaturschlüsseln; keine Freigabewirkung; jede Änderung liest ein Mensch | BS-01 bis BS-06 |
| System (S) | Kern, Risikomotor, Prüfmodul | automatische Kontrollen, Leitern, Sperrgründe | BS-05 |

Mindestbesetzung für den Produktionsbetrieb: zwei handlungsfähige Personen (B und V). Fehlt V, sperrt das Tor G8; fehlt R, sperrt G9. Eine zweite Instanz desselben Modells oder ein anderer KI-Agent zählt nicht als unabhängig (EV-11, EV-13).

## 2 RACI

R = verantwortlich (führt aus), A = entscheidet und haftet, C = konsultiert, I = informiert.

| Tätigkeit | B | R | V | E | P | K | S |
|---|---|---|---|---|---|---|---|
| Strategie registrieren (Experiment-Manifest) | A/R | C | – | – | – | C | – |
| Änderung Klasse A0/A1 (Dokumentation, Forschungscode) | A | I | – | – | – | R | – |
| Änderung Klasse B (Infrastruktur, Abhängigkeiten, Agent-Update) | A/R | I | – | – | – | C | – |
| Änderung Klasse C (Handelswirkung) | A/R | A (zweite Freigabe, Veto) | I | – | – | C | – |
| Änderung Klasse D (Grenzen, Rechte, Tore) | A/R | A (zweite Freigabe, Veto) | I | C | – | – | – |
| Profilaufstieg (§7.8) | A/R | A (Veto) | I | – | – | – | C |
| Grant ausstellen oder verlängern | A/R | C | I | C | – | – | C |
| Moduswechsel Demo ↔ Echtgeld | A/R | I | I | – | – | – | C |
| Kill-Switch, Pause, Abbau | A/R | I | R (Vertretung) | – | – | – | R (automatisch) |
| Incident führen und schließen | A/R | I | R (Vertretung) | – | – | C | C |
| Datenkauf und Lizenz | A/R | – | – | C | – | – | – |
| Brokerkonto, Verträge, Zahlungen | A/R | – | – | C | – | – | – |
| Recht und Steuern | A | – | – | R | – | – | – |
| Penetrationstest, Audit, Gegenprüfung | A | C | – | – | R | – | – |
| Täglicher Risikobericht | I | I | I | – | – | R (Entwurf) | R |
| Wöchentliche Risikorunde | A/R | R | I | – | – | C | C |
| Monatliche Performance-Attribution | A/R | C | – | – | – | C | R |
| Quartalsweise Modellprüfung | A/R | R | – | – | – | C | C |
| Jährliche Strategie- und Wirtschaftlichkeitsprüfung | A/R | C | – | C | C | C | – |

## 3 Rhythmus

| Termin | Inhalt | Dauer (Planwert) |
|---|---|---|
| täglich | Risikobericht lesen, Abgleich bestätigen, Alarme quittieren | <!--v:param:P-OPS-DAILY-MIN|d0-->20<!--/v--> Minuten |
| wöchentlich | Risikorunde: Limits, Leiterstufen, Kosten, Incidents, Freigabewarteschlange | <!--v:param:P-OPS-WEEKLY-MIN|d0-->90<!--/v--> Minuten |
| monatlich | Performance-Attribution, NAV-Abgleich mit dem Brokerauszug | <!--v:param:P-OPS-MONTHLY-MIN|d0-->240<!--/v--> Minuten |
| quartalsweise | Modellprüfung, Drills, Nutzenbilanz des KI-Agenten | <!--v:param:P-OPS-QUARTERLY-MIN|d0-->480<!--/v--> Minuten |
| jährlich | Strategie- und Wirtschaftlichkeitsprüfung mit Neuberechnung aller Rechner | Planwert im Quartalsbudget |

## 4 Schlüsselpersonenrisiko (RK-16)

Vertretung (V) mit eigenem Hardware-Schlüssel und Notfallhandbuch; Hinterlegung nach `security/key_management.md`; Übergabeprozess mit Checkliste (Konten, Zugänge, laufende Incidents, offene Freigaben). Ohne bestätigte Erreichbarkeit des Betreibers über <!--v:param:P-OPS-PRESENCE-MAX-D|d0-->7<!--/v--> Tage sperrt das System neue Einstiege; die Vertretung kann dann nur abbauen.
