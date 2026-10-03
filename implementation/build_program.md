# Bauprogramm (§17)

> **Betreiberfassung.** Das Programm hat elf Stufen, BS-00 bis BS-10. Jede Stufe endet an einem Tor, und nur ein bestandenes Tor gibt die nächste frei. Der Aufwand ist in Personentagen (Mensch) und Agententagen (Coding-Agent) geschätzt, jeweils als Spanne mit Schätzbasis: zusammen <!--v:calc:build_person_days_low|d0-->44<!--/v--> bis <!--v:calc:build_person_days_high|d0-->124<!--/v--> Personentage (Basis <!--v:calc:build_person_days_base|d0-->73<!--/v-->) und <!--v:calc:build_agent_days_low|d0-->55<!--/v--> bis <!--v:calc:build_agent_days_high|d0-->118<!--/v--> Agententage (Basis <!--v:calc:build_agent_days_base|d0-->82<!--/v-->). v2.0 nannte <!--v:v2map:comparisons/v2_agent_days/low|int-->45<!--/v--> bis <!--v:v2map:comparisons/v2_agent_days/high|int-->71<!--/v--> Agententage ohne Messbasis; die neue Schätzung ist höher, weil sie jede Komponente einzeln schätzt und die menschliche Prüfung mitrechnet. Bis zum Ende des Piloten kostet der Weg <!--v:dmc:build_cost_until_pilot_eur|eur-->58.147 EUR<!--/v-->, wenn deine Stunde mit <!--v:param:P-ECO-HOURLY-RATE|d0-->50<!--/v--> EUR bewertet wird (Annahme, bis du X-OP-RATE bestätigst); der Systembau selbst ist mit <!--v:stagecost:BS-05/total_eur|eur-->18.871 EUR<!--/v--> der größte Einzelposten und kommt erst nach den Forschungstoren. Für Go/No-Go heißt das: Heute ist nur BS-00 sinnvoll, weil es kein Geld kostet und über alles Weitere entscheidet. Nächster Schritt ist BS-00 mit den fünf G0-Eingaben.

Führende Quelle: `implementation/build_stages.json` (Stufen, Aufwand, Dauer, Abhängigkeiten, externe Eingaben, Definition of Done). Kosten je Stufe rechnet `financials/stage_costs.py`; Tests stehen in `implementation/test_catalog.json`; die ersten Schritte für den Coding-Agenten in `implementation/CODING_AGENT_START.md`.

## 1 Schätzbasis

Der Umfang des Systembaus (BS-05) ist je Komponente in Tausend Zeilen getesteten Produktionscodes einschließlich Tests geschätzt (KLOC, Annahme). Daraus folgen Agententage über die Produktivität des Coding-Agenten (<!--v:build:estimation_basis/productivity_kloc_per_agent_day/low|d1-->1,0<!--/v--> / <!--v:build:estimation_basis/productivity_kloc_per_agent_day/base|d1-->0,7<!--/v--> / <!--v:build:estimation_basis/productivity_kloc_per_agent_day/high|d1-->0,5<!--/v--> KLOC je Agententag im niedrigen, Basis- und hohen Fall) und Personentage über die menschliche Prüfung (<!--v:build:estimation_basis/review_person_days_per_agent_day/low|d2-->0,20<!--/v--> / <!--v:build:estimation_basis/review_person_days_per_agent_day/base|d2-->0,30<!--/v--> / <!--v:build:estimation_basis/review_person_days_per_agent_day/high|d2-->0,45<!--/v--> Personentage je Agententag) plus feste Koordination je Stufe. Stufen ohne Code (Tore, Drills, Betrieb) sind mit festen Spannen geschätzt. Alle Werte sind Annahmen; ab BS-05 wird die tatsächliche Produktivität je Komponente gemessen (Soll-Ist, Abschnitt 8).

<!-- GEN:BEGIN tab.components -->
| Komponente | Inhalt | KLOC (Schätzung) | Agententage (Basis) |
|---|---|---|---|
| C-MT5 | MT5-Adapter (Python-Schnittstelle, Polling, Korrelation magic/comment, Zeitstempel) | 4,0 | 5,7 |
| C-OMS | OMS/EMS mit Zustandsautomaten (SM-ORDER, SM-POSITION), Persistenz vor Netzwerk, UNKNOWN, Abgleich | 6,0 | 8,6 |
| C-RISK | Risikomotor: Vorhandelsprüfungen, Lückenregel, Tages- und Drawdown-Leiter, Kill-Switch, Margin-Überwachung | 6,0 | 8,6 |
| C-STRAT | Strategiemotor: S-TF, S-IM, S-REV, Carry-Filter, Kombination, Pufferung, Zeitstopp | 4,0 | 5,7 |
| C-DATA | Markt- und Referenzdatendienst: Balken, Rollkalender, Kontrakt- und Gebührendaten mit Gültigkeit | 4,0 | 5,7 |
| C-BT | Backtest mit demselben Kern (Ereignisjournal, deterministische Wiedergabe) | 3,0 | 4,3 |
| C-EVAL | Unabhängiger Evaluator, Torregeln, signierte Ergebnisse | 2,5 | 3,6 |
| C-NAV | NAV, Abgleich mit Brokerauszug, Berichte, Steuer-/Rechtsübergabe-Export | 2,5 | 3,6 |
| C-OBS | Beobachtbarkeit: Metriken, Logs, zwei Alarmwege, Watchdog | 2,0 | 2,9 |
| C-UI | Betreibercockpit (Web) und mobile Notfallansicht; Moduswechsel Demo/Echtgeld (SM-MODE) | 3,5 | 5,0 |
| C-SEC | Schlüssel, Grants, Hardware-Signaturen, Netztrennung, SBOM/CI | 2,5 | 3,6 |
| C-AI | Hermes-Anbindung außerhalb des Geldpfads, Evaluationssuite, Nutzenmessung | 2,0 | 2,9 |
<!-- GEN:END tab.components -->

Summe: <!--v:calc:build_kloc_total|d1-->42,0<!--/v--> KLOC in <!--v:calc:build_components_total|int-->12<!--/v--> Komponenten.

## 2 Stufen, Aufwand und Abhängigkeiten

<!-- GEN:BEGIN tab.build_program -->
| Stufe | Tor | Inhalt | Personentage (niedrig / Basis / hoch) | Agententage (niedrig / Basis / hoch) | Wochen (niedrig / Basis / hoch) | hängt ab von | externe Eingaben |
|---|---|---|---|---|---|---|---|
| BS-00 | GATE-G0 | Betreibereingaben, Wirtschaftlichkeit mit echten Gebühren, Kauf-statt-Bau-Entscheidung | 2,0 / 3,0 / 5,0 | 0,0 / 0,0 / 0,0 | 1 / 2 / 3 | – | X-BRK-FEES, X-BRK-INTEREST, X-OP-BUDGET, X-OP-RATE, X-V1-PRODUCTS |
| BS-01 | GATE-G1 | Kontozugang (Demo und kleines Echtgeldkonto), frühe Killer-Tests KT-01…KT-16 | 3,0 / 5,0 / 8,0 | 2,0 / 4,0 / 6,0 | 2 / 3 / 6 | BS-00 | X-BRK-ACCOUNT, X-BRK-API, X-BRK-CONTRACTS, X-BRK-DEMO, X-BRK-LIQ, X-BRK-MARGIN, X-BRK-NACHSCHUSS |
| BS-02 | GATE-G2 | Datenlizenz, Abgleich zweier Quellen, Leckagetests | 3,0 / 4,0 / 6,0 | 3,0 / 5,0 / 8,0 | 2 / 4 / 6 | BS-00 | X-DATA-LIC, X-DATA-ND |
| BS-03 | GATE-G3 | Forschung auf Entwicklungsdaten mit Futility-Regel | 5,0 / 8,0 / 12,0 | 6,0 / 10,0 / 15,0 | 3 / 5 / 8 | BS-02 | X-DATA-HIST, X-DATA-LIQ, X-DATA-VOL |
| BS-04 | GATE-G4 | Einmalige Holdout-Prüfung | 1,0 / 2,0 / 3,0 | 1,0 / 1,0 / 2,0 | 1 / 1 / 2 | BS-03 | – |
| BS-05 | GATE-G5 | Systembau, Abnahmetests, unabhängiges Prüfmodul ohne Abweichung | 16,4 / 30,0 / 55,8 | 42,0 / 60,0 / 84,0 | 10 / 16 / 26 | BS-04, BS-01 | X-INF-VPS, X-INF-ZONES, X-OP-BUDGET |
| BS-06 | GATE-G6 | Drills: Restore, Broker- und Datenausfall, Margin, Kill-Switch, Schlüsselverlust | 3,0 / 4,0 / 6,0 | 1,0 / 2,0 / 3,0 | 2 / 2 / 4 | BS-05 | – |
| BS-07 | GATE-G7 | Paper-Forward (Mindestdauer P-RES-PAPER-MONTHS (6 Monate)) | 4,0 / 6,0 / 10,0 | 0,0 / 0,0 / 0,0 | 26 / 26 / 39 | BS-06 | – |
| BS-08 | GATE-G8 | Pilot mit Echtgeld im Profil H5 (Pilotgröße P-LEV-PILOT-SIZE (0,50 Anteil), Pilotverlustbudget P-RES-PILOT-LOSS-BUDGET (0,15 Anteil)) | 4,0 / 6,0 / 10,0 | 0,0 / 0,0 / 0,0 | 26 / 26 / 39 | BS-07 | X-DATA-ND, X-EXEC-TCA, X-LEGAL-01, X-OP-CAPITAL, X-OP-DLC-MODE, X-OP-RISK-ACCEPT, X-ORG-DEPUTY, X-TAX-01 |
| BS-09 | GATE-G9 | Standardbetrieb mit Hebel-Stufenleiter | 0,0 / 0,0 / 0,0 | 0,0 / 0,0 / 0,0 | 52 / 52 / 52 | BS-08 | X-OP-CAPITAL, X-OP-RISK-ACCEPT, X-ORG-RISK |
| BS-10 | GATE-G10 | Externes Audit (Technik, Risiko, Prozesse) | 3,0 / 5,0 / 8,0 | 0,0 / 0,0 / 0,0 | 4 / 6 / 8 | BS-09 | – |
<!-- GEN:END tab.build_program -->

Die externen Eingaben je Stufe stammen aus `external_inputs.json` (Feld „sperrt“) und sind dieselben, die das zugehörige Tor als Voraussetzung prüft.

## 3 Kritischer Pfad

<!--v:build:critical_path|chain-->BS-00 → BS-02 → BS-03 → BS-04 → BS-05 → BS-06 → BS-07 → BS-08 → BS-09 → BS-10<!--/v-->; parallel laufen <!--v:build:parallel/0|list-->BS-01, BS-02<!--/v--> (beide nach G0). BS-05 braucht zusätzlich G1, das früher fertig ist. Dauer entlang des kritischen Pfads bis zum abgenommenen System (G5): <!--v:calc:build_weeks_until/BS-05/low|d0-->17<!--/v--> / <!--v:calc:build_weeks_until/BS-05/base|d0-->28<!--/v--> / <!--v:calc:build_weeks_until/BS-05/high|d0-->45<!--/v--> Wochen; bis zum Ende des Piloten (G8) <!--v:calc:build_weeks_until/BS-08/base|d0-->82<!--/v--> Wochen im Basisfall; bis zum Audit (G10) <!--v:calc:build_weeks_critical/base|d0-->140<!--/v--> Wochen. Überschreitet die Dauer bis G5 den Deckel P-ECO-MAX-MONTHS-G5 (<!--v:param:P-ECO-MAX-MONTHS-G5|d0-->12<!--/v--> Monate), scheitert G5 (Voraussetzung PRE-G5-6).

## 4 Kosten je Stufe

<!-- GEN:BEGIN tab.stage_costs -->
| Stufe | Tor | Monate | Mensch (Projekt) EUR | Agent EUR | einmalig EUR | laufend EUR | Betreiberroutinen EUR | Risikofunktion EUR | gesamt EUR |
|---|---|---|---|---|---|---|---|---|---|
| BS-00 | GATE-G0 | 0,5 | 1.200 | 0 | 0 | 0 | 0 | 0 | 1.200 |
| BS-01 | GATE-G1 | 0,7 | 2.000 | 138 | 0 | 190 | 0 | 0 | 2.328 |
| BS-02 | GATE-G2 | 0,9 | 1.600 | 184 | 3.477 | 254 | 0 | 0 | 5.515 |
| BS-03 | GATE-G3 | 1,1 | 3.200 | 230 | 0 | 317 | 0 | 0 | 3.747 |
| BS-04 | GATE-G4 | 0,2 | 800 | 46 | 0 | 63 | 0 | 0 | 909 |
| BS-05 | GATE-G5 | 3,7 | 12.000 | 736 | 5.120 | 1.015 | 0 | 0 | 18.871 |
| BS-06 | GATE-G6 | 0,5 | 1.600 | 92 | 0 | 127 | 0 | 0 | 1.819 |
| BS-07 | GATE-G7 | 6,0 | 2.400 | 0 | 0 | 1.649 | 7.829 | 0 | 11.878 |
| BS-08 | GATE-G8 | 6,0 | 2.400 | 0 | 0 | 1.649 | 7.829 | 0 | 11.878 |
| BS-09 | GATE-G9 | 12,0 | 0 | 0 | 0 | 3.299 | 15.658 | 3.590 | 22.547 |
| BS-10 | GATE-G10 | 1,4 | 2.000 | 0 | 15.000 | 381 | 0 | 0 | 17.381 |
<!-- GEN:END tab.stage_costs -->

Mensch = Personentage × <!--v:param:P-ECO-HOURS-PER-PERSON-DAY|d0-->8<!--/v--> Stunden × Stundensatz P-ECO-HOURLY-RATE; Agent = Abo des Coding-Agenten während der Stufen mit Agententagen; einmalig = Datenkauf, Hardware-Schlüssel, Penetrationstest, Audit; laufend = Infrastruktur, Marktdaten und KI-Abo während der Stufe; Risikofunktion = externe unabhängige Risikofunktion im Standardbetrieb (X-ORG-RISK). Die Summe bis zum Ende des Piloten (<!--v:dmc:build_cost_until_pilot_eur|eur-->58.147 EUR<!--/v-->) geht als Aufbaukosten in die Entscheidungsrechnung ein (§5.4); das Audit (<!--v:dmc:audit_cost_eur|eur-->17.381 EUR<!--/v-->) fällt erst nach einem Jahr Standardbetrieb an.

## 5 Personal

| Rolle | Aufgabe im Bau | ab |
|---|---|---|
| Betreiber | Auftraggeber; entscheidet an jedem Tor, signiert Grants, eröffnet Konten, beschafft externe Eingaben; prüft oder beauftragt die Prüfung des Codes | BS-00 |
| Coding-Agent | schreibt Code und Tests nach Arbeitspaket; kein Zugang zu Broker, Secrets, Holdout oder Signaturschlüsseln; keine Freigabewirkung; Abo nur in Stufen mit Agententagen | BS-01 |
| menschliche Prüfung | liest jede Änderung vor dem Zusammenführen (Personentage der Tabelle); Betreiber oder eine von ihm beauftragte fachkundige Person | BS-01 |
| externe Prüfer | Penetrationstest (BS-05), Gegenprüfung des Pakets (X-REVIEW), Audit (BS-10) | je Stufe |
| externe Risikofunktion und Notfallvertretung | nach `governance/organisation_raci.md`; Voraussetzung für G8 und G9 (X-ORG-DEPUTY, X-ORG-RISK) | BS-08 |

Die Personentage sind mit dem Stundensatz des Betreibers bewertet. Übernimmt eine beauftragte Person die Codeprüfung, gilt ihr Satz; das ändert die Aufbaukosten, nicht den Befund, solange die Entscheidungsrechnung ohnehin keine Stufe als wirtschaftlich ausweist.

## 6 Definition of Done

<!-- GEN:BEGIN tab.dod -->
| Stufe | Definition of Done |
|---|---|
| BS-00 | X-BRK-FEES, X-OP-RATE, X-OP-BUDGET, X-BRK-INTEREST und X-V1-PRODUCTS bestätigt; Rechner mit echten Gebühren neu gerechnet (--check bestanden); Kauf-statt-Bau-Befund signiert; GATE-G0 mit signiertem Ergebnis PASS |
| BS-01 | Repository mit CI und Secret-Scan (T-SEC-008) eingerichtet, bevor das erste Zugangsdatum existiert; KT-01 bis KT-16 mit Orakel bestanden oder Rückfallvariante signiert (GATE-G1); Kontraktliste, Margins und Liquidationsregel schriftlich; Echtgeldorders nur vom Betreiber ausgelöst, Verlust höchstens P-EXE-KT-LOSS-CAP-EUR (250 EUR) (T-GOV-002); T-SEC-007 bestanden |
| BS-02 | Zwei Quellen je Instrument abgeglichen (T-DAT-001); Holdout versiegelt (Hash im Prüfmodul); Leckagetests bestanden (T-DAT-LEAK-001); Volatilitäten, Spreads, Tagesvolumen, Liquiditätsfenster und Historie gemessen (X-DATA-VOL, X-DATA-LIQ, X-DATA-HIST); GATE-G2 PASS |
| BS-03 | Vorregistrierung vor Ergebnisansicht (T-RES-PREREG-001); DSR, PBO, SPA bzw. Reality Check und Romano-Wolf berechnet; Futility-Wahrscheinlichkeit berechnet; GATE-G3 mit signiertem Ergebnis |
| BS-04 | Holdout genau einmal geöffnet (T-RES-HOLDOUT-001); GATE-G4 mit signiertem Ergebnis |
| BS-05 | Alle Abnahmetests der Stufe BS-05 aus implementation/test_catalog.json bestanden; Mutationsanteil ≥ P-QA-MUTATION-MIN (0,80 Anteil) und Zweigabdeckung ≥ P-QA-COVERAGE-MIN (0,90 Anteil); Penetrationstest ohne kritische Befunde (T-SEC-014); Kein Sprachmodell im Geldpfad nachgewiesen (T-AI-001 bis T-AI-004); Prüfmodul ohne Abweichung; GATE-G5 PASS |
| BS-06 | DR-01 bis DR-10 mit Protokoll bestanden; Dauerlauf P-QA-SOAK-H (72 Stunden) ohne Incident HOCH (T-QA-SOAK-001); Hardware-Schlüssel und Break-glass geprüft (T-SEC-013); GATE-G6 PASS |
| BS-07 | Mindestdauer P-RES-PAPER-MONTHS (6 Monate) erreicht; Harm-Screen, Kostendrift und Limits ohne Auslösung (MON-HARM, MON-COSTDRIFT, MON-LIMITS); SLOs gemessen (T-OPS-SLO-001); GATE-G7 PASS |
| BS-08 | Pilot ohne Limitverletzung und unter dem Pilotverlustbudget; Kosten im Modellband (X-EXEC-TCA, MON-COSTDRIFT); Endtor: Posterior P(Sharpe > 0) ≥ P-RES-FINAL-P (0,80 Anteil) (GATE-G8) |
| BS-09 | Mindestdauer P-RES-STANDARD-MONTHS (12 Monate) ohne schwere Incidents; Stufenleiter regelkonform (keine Aufstiege ohne Evidenz und zweite Freigabe); GATE-G9 PASS |
| BS-10 | Unabhängiges Audit ohne wesentliche Feststellung (GATE-G10) |
<!-- GEN:END tab.dod -->

## 7 Reihenfolge nach Informationswert (§17.4)

Die billigsten Prüfungen mit der größten Abbruchwirkung kommen zuerst:

1. **Wirtschaftlichkeit mit echten Gebühren** (BS-00, GATE-G0): kostet <!--v:stagecost:BS-00/total_eur|eur-->1.200 EUR<!--/v--> Betreiberzeit und keine Ausgabe; mit den heutigen Rechenwerten scheitert hier bereits die registrierte Familie (§16.4 des Masterkonzepts).
2. **Kauf-statt-Bau-Vergleich** (BS-00, GATE-G0, Regeln G0-R3 und G0-R4): Geldmarkt (V0) und Fondslösung (V1) gegen den Eigenbau; die Produktauswahl für V1 (X-V1-PRODUCTS) ist eine G0-Eingabe.
3. **Killer-Tests beim Broker** (BS-01, GATE-G1): <!--v:calc:killer_tests_total|int-->16<!--/v--> Tests, zuerst die mit Projektabbruchwirkung (KT-04 bis KT-06), vor jeder weiteren Entwicklung.
4. **Kostenmessung**: Kommission gegen Auszug (KT-14) in BS-01, Spreads und Liquiditätsfenster aus den gekauften Daten in BS-02 (X-DATA-VOL, X-DATA-LIQ), Schlupf im Demo und im Paper-Betrieb (X-EXEC-TCA) vor dem Pilot.

Bis einschließlich BS-02 kostet der Weg <!--v:oc:cumulative_cost_eur/BS-02|eur-->9.044 EUR<!--/v-->; erst danach und nach den Forschungstoren G3 und G4 beginnt der teure Systembau.

## 8 Steuerung im Bau

- **Soll-Ist:** Je Komponente werden KLOC, Agententage und Personentage erfasst. Liegt eine Komponente über dem hohen Fall, wird der Rest der Stufe neu geschätzt und die Entscheidungsrechnung mit den neuen Aufbaukosten wiederholt.
- **Ausgabendeckel:** Das Budget X-OP-BUDGET ist Voraussetzung von G0 und G5; es wird je Stufe gegen die Kosten aus Abschnitt 4 geführt.
- **Abbruch:** Scheitert ein Tor, gilt dessen Folgeschritt für FAIL; ein bereits bezahlter Aufwand ist kein Grund für eine Fortsetzung (Abbruchkriterien, Masterkonzept §5.8).
- **Tests zuerst:** Jede Stufe beginnt mit den Tests ihres Abschnitts im Testkatalog; Abnahme heißt, dass alle Tests der Stufe mit ihrem Bestehenskriterium bestanden sind.

Qualitätsziele des Systembaus (Parameter, geprüft in GATE-G5 und GATE-G6):

<!-- GEN:BEGIN tab.params:P-QA -->
| ID | Bedeutung | Wert | Einheit | Status |
|---|---|---|---|---|
| P-QA-MUTATION-MIN | Mindestanteil erkannter Mutanten im Geldpfad (Mutationstests) | 0,80 | Anteil | ENTWURF |
| P-QA-COVERAGE-MIN | Mindest-Zweigabdeckung des Geldpfads (Kern, Risikomotor, OMS, Adapter) | 0,90 | Anteil | ENTWURF |
| P-QA-SOAK-H | Dauer des Dauerlaufs im Demokonto vor G6 | 72 | Stunden | ENTWURF |
| P-QA-LOAD-FACTOR | Lasttest: Vielfaches der erwarteten Spitzenrate von Abfragen und Nachrichten | 5 | Faktor | ENTWURF |
| P-QA-FAULT-REPEATS | Wiederholungen je Fehlerinjektionsfall (Abbruch, Zeitüberschreitung, Verbindungsverlust) | 50 | Anzahl | ENTWURF |
| P-QA-PROPERTY-CASES | Zufallsbeispiele je Eigenschaftstest (Lückenregel, Größenregel, Leitern, Verband) | 1.000 | Anzahl | ENTWURF |
<!-- GEN:END tab.params:P-QA -->

<!-- GEN:BEGIN tab.tests_summary -->
| Ausführung | Tests | Ebenen |
|---|---|---|
| im Paket ausgeführt | 40 | MUTATION 1, SIMULATION 3, STATIC 17, UNIT 19 |
| Killer-Tests beim Broker (BS-01) | 17 | BROKER_CERT 16, INTEGRATION 1 |
| Abnahme im Systembau | 79 | CHAOS 1, FAULT_INJECTION 5, INTEGRATION 24, LOAD 2, MUTATION 1, PROPERTY 5, SECURITY 17, SIMULATION 9, STATIC 4, UNIT 11 |
| Drills, Dauerläufe, Messungen im Betrieb | 15 | CHAOS 1, DRILL 10, INTEGRATION 1, SIMULATION 1, SOAK 2 |
<!-- GEN:END tab.tests_summary -->
