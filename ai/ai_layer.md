# KI-Schicht: Rollen, Grenzen, Nutzen (§11.1, §11.4, §11.6)

> **Betreiberfassung.** Die KI-Schicht soll dir Arbeit abnehmen, nicht Entscheidungen über Geld: Hermes recherchiert, schreibt Entwürfe, sichtet Daten und Incidents und verfasst Berichte, jeweils unter deiner Prüfung. Das System läuft ohne ihn vollständig (Stufe H0), und seine Rechte wachsen nur, wenn gemessener Nutzen es rechtfertigt. Die Kosten sind ein Abo mit harter Monatsgrenze und stehen in der Wirtschaftsrechnung als eigene Zeile. Bleibt die Nutzenbilanz <!--v:param:P-AI-ROLLBACK-QUARTERS|d0-->2<!--/v--> Quartale in Folge negativ, wird der Agent zurückgebaut. Für Go/No-Go heißt das: Die KI-Schicht ist ein Werkzeug der Forschung und des Betriebs und für den Befund unerheblich. Nächster Schritt ist die Klärung der Datenverarbeitung beim Anbieter (X-AI-DPA).

## 1 Aufgaben

| Aufgabe | Ergebnis | Prüfung durch |
|---|---|---|
| Forschungsassistenz | Literaturauszüge mit Quellen, Experimententwürfe (Vorregistrierung), Auswertungen in der Sandbox | Betreiber; Tore im Prüfmodul |
| Code-Entwürfe | Änderungsvorschläge mit Tests in der eigenen Arbeitsablage | Betreiber und CI; zweite menschliche Freigabe für Klassen C und D |
| Datenqualität | Anomalie-Hinweise und Erklärungen zu Lücken, Ausreißern, Revisionen | Datenregeln (§9.3) entscheiden, nicht der Agent |
| Incident-Triage | Zusammenfassung, wahrscheinliche Ursache, passendes Runbook | Betreiber führt das Runbook aus |
| Berichte, Dokumentation, Wissensregister | Tages-, Wochen- und Incidentberichte; Wissenseinträge mit Quelle, Gültigkeit und Klasse | Betreiber; Hypothesen dürfen nicht als Tatsache gespeichert werden |

## 2 Autonomieleiter (übernommen aus v2.0)

| Stufe | darf selbstständig | braucht Freigabe |
|---|---|---|
| H0 | nichts; System ohne Agent | – |
| H1 (Start) | Sandbox-Forschung, Diagnose, Entwürfe in eigener Arbeitsablage, Berichte, Wissenseinträge, Arbeitsaufträge, Upstream-Sichtung | jede Aktivierung von Artefakten |
| H2 | zusätzlich eigene Kandidaten der Klassen A0, A1 und B durch CI und Evaluation schicken | Freigabe durch den Betreiber (Autor ≠ Freigeber) |
| H3 | zusätzlich reine Dokumentationsänderungen nach bestandener Evaluation und Einspruchsfrist | alles außer Dokumentation |

In keiner Stufe erhält der Agent Brokerzugang, Freigabeschlüssel, Grant- oder Limitrechte. Offene Vorschläge höchstens <!--v:param:P-AI-PROPOSALS-OPEN-MAX|d0-->3<!--/v-->, neue höchstens <!--v:param:P-AI-PROPOSALS-WEEK-MAX|d0-->5<!--/v--> je Woche; Arbeitsaufträge höchstens <!--v:param:P-AI-WORK-BUDGET-H|d0-->40<!--/v--> Stunden und <!--v:param:P-AI-REVIEW-ROUNDS|d0-->3<!--/v--> Prüfrunden.

## 3 Alternativen

| Option | Bewertung |
|---|---|
| H0 – kein Agent | voll funktionsfähig; mehr Betreiberzeit für Berichte und Sichtung |
| allgemeiner Coding-Agent nur im Bau | beschleunigt BS-05 (in den Agententagen des Bauprogramms enthalten); keine Rolle im Betrieb |
| Hermes (BQ-10) | gewählt vom Betreiber; Stärken Werkzeuge, Gedächtnis, Integration über MCP; Schwächen hohe Änderungsrate des Upstreams und Voreinstellungen, die eine kontrollierte Governance erst durch Netz und Dateisystem erzwingen lassen (`ai/hermes_integration.md`) |

Andere Agenten-Frameworks sind nicht recherchiert; eine Auswahl wäre eine Änderung der Klasse D mit eigener Evaluation.

## 4 Nutzenmessung und Rückbau

Quartalsweise Bilanz gegen eine Basislinie ohne Agent: Nettozeitgewinn (gemessene Zeit mit Agent gegen geschätzte Zeit ohne), Annahmequote der Vorschläge (Ziel mindestens <!--v:param:P-AI-ACCEPT-MIN|pct0-->50 %<!--/v-->), Fehlerquote (Vorschläge, die nach Annahme korrigiert werden mussten) und Kosten (Abo <!--v:cost:fixed_costs/ai_subscription_monthly_eur/SUPER|eur2-->87,63 EUR<!--/v--> im Monat plus Pflegezeit). Ist die Bilanz <!--v:param:P-AI-ROLLBACK-QUARTERS|d0-->2<!--/v--> Quartale in Folge negativ, wird der Agent auf H0 zurückgebaut; eine Rückkehr ist eine Änderung der Klasse D.

## 5 Regulierung und Datenschutz

Anwendbarkeit der KI-Verordnung (EU) 2024/1689 und der DSGVO prüft die externe Person (BQ-03; SRC-REG-AIACT, SRC-REG-DSGVO, nicht geprüft). Due Diligence des Anbieters vor der ersten Nutzung nicht öffentlicher Daten: Region der Verarbeitung, Speicherdauer, Nutzung für Training, Unterauftragnehmer (X-AI-DPA). Unabhängig davon verlassen keine personenbezogenen Daten, keine Secrets und keine lizenzierten Rohdaten die KI-Zone; das LLM-Gateway prüft das mit Kanarienwerten (T-SEC-012).
