# Kurzfassung für den Betreiber – KI-Trading Institutional v3.0

Stand 24.09.2026. Konzeptpaket; keine Anlage-, Rechts- oder Steuerberatung und keine Handelsempfehlung. Jede Zahl ist an einen Rechner oder ein Register gebunden; Begründungen stehen in `Masterkonzept_v3.0.md`.

## Entscheidung

**Echtgeld: No-Go in <!--v:calc:gonogo_count/NO_GO|int-->24<!--/v--> von <!--v:calc:gonogo_cells|int-->24<!--/v--> Zellen** aus Kapitalstufe und Hebelprofil. Zulässig sind Demo- und Paper-Betrieb innerhalb des Ausgabendeckels. Empfohlen ist heute nur die kostenlose Stufe BS-00: die Eingaben für das Tor G0 beschaffen und die Wirtschaftlichkeit mit echten Gebühren prüfen. G0 steht heute auf <!--v:calc:gate_today/GC-G0-101/outcome|raw-->BLOCKED_EXTERNAL<!--/v-->, weil diese Eingaben fehlen.

## Warum

- **Kosten schlagen die erwartete Kante.** Bei deiner Haltedauer (in der Regel <!--v:param:P-OP-HOLD-STD-MIN-H|d0-->4<!--/v--> h bis <!--v:calc:hold_std_max_days|d0-->4<!--/v--> Tage, höchstens <!--v:calc:hold_max_days|d0-->7<!--/v--> Tage) kostet der Handel je Instrument meist mehr Sharpe-Ratio im Jahr, als die Literatur brutto erwarten lässt (Median der Brutto-Sharpe-Ratio je Instrument <!--v:prior:median_gross/S-TF|d3-->0,092<!--/v-->); nur <!--v:calc:cost_below_threshold_stf|int-->4<!--/v--> von <!--v:calc:instruments_access_primary|int-->65<!--/v--> handelbaren Kontrakten liegen unter der Kostenschwelle.
- **Deine Tagesgrenze bestimmt den Hebel.** Damit die Grenze von <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v--> Tagesverlust auch bei Kurslücken hält, begrenzt eine Größenregel jede Position. H10, H15 und H20 sind deshalb in keiner Stufe zulässig; H5 scheitert an der Mindestdiversifikation von <!--v:param:P-LEV-H5-MINDIV|int-->8<!--/v--> Instrumenten, und in <!--v:calc:dmc_empty_cells/U-KOSTEN|int-->16<!--/v--> der <!--v:calc:dmc_cells/U-KOSTEN|int-->24<!--/v--> Zellen ist gar kein Instrument zugelassen.
- **Der Aufbau ist teuer.** Bis zum Ende des Piloten kostet er rund <!--v:dmc:build_cost_until_pilot_eur|eur-->58.147 EUR<!--/v--> und liegt damit über dem markierten Ausgabendeckel von <!--v:param:P-ECO-SPEND-CAP|eur-->25.000 EUR<!--/v-->; dazu kommen rund <!--v:dmc:operator_hours_per_year|d0-->314<!--/v--> Betreiberstunden im Jahr.
- **Die Alternative trägt nicht.** Die langsame Trendfolge TF-D1 bräuchte eine neue Entscheidung zur Haltedauer und ist trotzdem in <!--v:calc:dmc_class_count/U-KOSTEN-TFD1/PROFILE_NOT_ADMISSIBLE|int-->24<!--/v--> von <!--v:calc:dmc_cells/U-KOSTEN-TFD1|int-->24<!--/v--> Zellen unzulässig. Vergleichsgröße ist ein fertiges Trendfolgeprodukt (V1); konkrete Produkte fehlen noch (X-V1-PRODUCTS).
- **Ein Nachweis dauert.** Selbst eine echte Kante mit Sharpe-Ratio <!--v:param:P-RES-SR-USEFUL|d1-->0,3<!--/v--> bräuchte rund <!--v:stat:years_for_power/0.3|d0-->69<!--/v--> Jahre Daten für einen statistischen Nachweis.

## Go/No-Go je Kapitalstufe und Hebelprofil

<!-- GEN:BEGIN tab.gonogo -->
| Kapital (Mio. EUR) | H5 | H10 | H15 | H20 | Alternative TF-D1 H5 (Betreiberentscheidung nötig) |
|---|---|---|---|---|---|
| 0,25 | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | PROFILE_NOT_ADMISSIBLE |
| 0,5 | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | PROFILE_NOT_ADMISSIBLE |
| 1 | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | PROFILE_NOT_ADMISSIBLE |
| 5 | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | PROFILE_NOT_ADMISSIBLE |
| 25 | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | PROFILE_NOT_ADMISSIBLE |
| 100 | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | PROFILE_NOT_ADMISSIBLE |
<!-- GEN:END tab.gonogo -->

Jede Zelle nennt die Empfehlung für Echtgeld und in Klammern den Befund der Entscheidungsrechnung (`financials/decision_montecarlo_results.json`): PROFILE_NOT_ADMISSIBLE heißt, das Profil verletzt eine deiner Vorgaben oder eine Risikogrenze; NOT_VIABLE_AT_CAPITAL heißt, bei diesem Kapital ist der Weg nicht wirtschaftlich oder kein Instrument zugelassen. Die letzte Spalte ist keine Empfehlung, sondern die beste gerechnete Alternative. Demo und Paper sind in jeder Zelle mit Ausgabendeckel zulässig.

## Risiken in Zahlen

- Schlimmstes Stressszenario der registrierten Allokation in H5: <!--v:calc:stress_worst_name/SYSTEM/H5|raw-->LME-Nickel März 2022<!--/v--> (<!--v:stress:results/SYSTEM/H5/worst_scenario|raw-->SC-H-2022NI<!--/v-->) mit <!--v:stress:results/SYSTEM/H5/worst_loss_with_ladder|pct1-->20,4 %<!--/v--> Verlust nach Tagesverlust- und Drawdown-Leiter (`risk/stress_results.json`).
- Damit das Margin-Level auch im schlimmsten Szenario über der eigenen Abbauschwelle bleibt, müssten mindestens <!--v:calc:stress_margin/SYSTEM/required_max|pct1-->25,5 %<!--/v--> des Kapitals beim Broker liegen; geplant sind <!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v-->.
- Die Tagesgrenze kann trotz Größenregel überschritten werden, in der Simulation mit einer Wahrscheinlichkeit von <!--v:kelly:results/H5/SYSTEM/p_day_loss_over_cap_per_year|pct1-->0,7 %<!--/v--> je Jahr. Eine absolute Garantie gibt es nicht; wie „niemals“ gilt, entscheidest du (X-OP-DLC-MODE).

## Externe Eingaben mit Sperrwirkung

Alle <!--v:calc:external_inputs_total|int-->34<!--/v--> externen Eingaben sind unbestätigt; markierte Rechenannahmen lösen keine Sperre (`external_inputs.json`).

<!-- GEN:BEGIN tab.external_by_gate -->
| Gesperrt ist | bis bestätigt sind |
|---|---|
| G0 Betreibereingaben, Wirtschaftlichkeit mit echten Gebühren, Kauf-statt-Bau | X-OP-RATE, X-OP-BUDGET, X-BRK-FEES, X-BRK-INTEREST, X-V1-PRODUCTS |
| G1 Kontozugang und frühe Killer-Tests | X-BRK-ACCOUNT, X-BRK-CONTRACTS, X-BRK-MARGIN, X-BRK-LIQ, X-BRK-NACHSCHUSS, X-BRK-API, X-BRK-DEMO |
| G2 Datenlizenz, Abgleich zweier Quellen, Leckagetests | X-DATA-ND, X-DATA-LIC |
| G3 Forschung auf Entwicklungsdaten mit Futility-Regel | X-DATA-VOL, X-DATA-LIQ, X-DATA-HIST |
| G5 System gebaut, Abnahmetests bestanden, Prüfmodul ohne Abweichung | X-OP-BUDGET, X-INF-ZONES, X-INF-VPS |
| G8 Pilot mit Echtgeld im Profil H5 (Endtor) | X-OP-CAPITAL, X-OP-RISK-ACCEPT, X-OP-DLC-MODE, X-ORG-DEPUTY, X-DATA-ND, X-EXEC-TCA, X-LEGAL-01, X-TAX-01 |
| G9 Standardbetrieb mit Hebel-Stufenleiter | X-OP-CAPITAL, X-OP-RISK-ACCEPT, X-ORG-RISK |
| CFD-Rückfallpfad (BQ-09: CFD optional) | X-OP-CFD, X-CFD-SPREADS |
| Nutzung für Gelder Dritter | X-SCOPE-THIRD |
| Aktienindex-Futures im Universum (BQ-06) | X-EQ-INDEX |
| Kontrakte an ICE und Euronext | X-BRK-ALT |
| KI-Schicht mit nicht öffentlichen Daten | X-AI-DPA |
| K-Score über der Obergrenze ohne Gegenprüfung | X-REVIEW |
<!-- GEN:END tab.external_by_gate -->

## Deine nächsten Schritte

1. Für G0 schriftlich beschaffen: Gebühren (X-BRK-FEES), Verzinsung des Guthabens (X-BRK-INTEREST), deinen Stundensatz (X-OP-RATE), Budget mit Ausgabendeckel (X-OP-BUDGET) und Vergleichsprodukte (X-V1-PRODUCTS).
2. Entscheiden, wie die Tagesgrenze gilt (DEC-CF-02, X-OP-DLC-MODE) und ob die Höchsthaltedauer bleibt (§5.7).
3. Notfallvertretung und externe Risikofunktion benennen (X-ORG-DEPUTY, X-ORG-RISK).
4. Die unabhängige Gegenprüfung beauftragen (X-REVIEW, `audit/independent_review_request.md`).
5. Die externe Person für Recht und Steuern mit `legal/handover_external.md` beauftragen (X-LEGAL-01, X-TAX-01).

## Bewertung

Selbstbewertung K = <!--v:calc:score_k_total|d2-->64,75<!--/v--> von <!--v:param:P-SCORE-MAX|d0-->100<!--/v-->, ohne unabhängige Gegenprüfung höchstens <!--v:param:P-SCORE-K-CAP|d0-->99<!--/v-->; E = <!--v:calc:score_e_total|d0-->0<!--/v-->, weil noch kein Tor in der realen Welt bestanden ist (`audit/scorecard_K.json`, `audit/scorecard_E.json`). Die größten Abzüge betreffen Recht, Steuern und Betriebsmodelle, die nach deinen Entscheidungen BQ-02 und BQ-03 außerhalb des Systemumfangs liegen, das unvollständige Zinsuniversum, unbesetzte Rollen, die Brokersemantik je Börse und die fehlende Gegenprüfung.

## Was dieses Paket nicht tut

Es eröffnet keine Konten, schließt keine Verträge, bewegt kein Kapital, sendet keine Orders und gibt kein produktives System frei. Zwischen Demo und Echtgeld schaltest nur du (SM-MODE); ein Echtgeld-Grant braucht bestandene Tore und deine Signatur.
