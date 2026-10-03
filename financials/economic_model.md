# Wirtschaftsmodell und Entscheidungsrechnung (§5)

> **Betreiberfassung.** Dieses Dokument erklärt, wie das Paket Kosten, Erträge und Kapitalwert rechnet und warum die Empfehlung für Echtgeld in allen Stufen No-Go lautet. Die Handelskosten je Risikoeinheit übersteigen bei deinem Haltehorizont den erwarteten Bruttoertrag fast aller Kontrakte, und das beim Broker liegende Guthaben kostet ohne Verzinsung zusätzlich Ertrag. Auch die langsame Trendfolge ohne Sieben-Tage-Grenze ist nach der Größenregel mit Wochenendfaktor in <!--v:calc:dmc_class_count/U-KOSTEN-TFD1/PROFILE_NOT_ADMISSIBLE|int-->24<!--/v--> von <!--v:calc:dmc_cells/U-KOSTEN-TFD1|int-->24<!--/v--> Zellen unzulässig. Alle Werte sind Planungswerte, bis Gebühren, Margins und Spreads gemessen oder schriftlich bestätigt sind. Für Go/No-Go heißt das: Demo und Forschung ja, Echtgeld nein. Nächster Schritt sind die Brokerbestätigungen X-BRK-FEES und X-BRK-INTEREST.

## 1 Rechenkette und Quellen der Wahrheit

| Schritt | Rechner | Ergebnis | liest |
|---|---|---|---|
| Umschlag und Haltedauer | `research/reference_strategies/turnover_simulation.py` | `research/turnover_results.json` | Parameter P-STR-* |
| Kosten je Instrument | `financials/cost_model.py` | `financials/cost_model_results.json`, `financials/cost_table.csv` | `registers/costs.json`, `registers/instruments.json`, Umschlag |
| Prior und Zulassung | `research/prior_derivation.py` | `research/prior_results.json` | Literatur (R3), Kosten, Instrumente |
| Hebel und Profile | `risk/leverage_calculator.py` | `risk/leverage_results.json` | Zulassung, Kosten, Lückenparameter |
| Entscheidung | `financials/decision_montecarlo.py` | `financials/decision_montecarlo_results.json` | alle obigen, `financials/stage_costs.py`, `financials/tax_scenarios.py` |

Jeder Rechner vermerkt die SHA-256 seiner Eingaben; `python validation/run_calculators.py --check` rechnet die Kette neu und vergleicht byteweise. Werte stehen nur in `parameters.json`, `registers/costs.json` und `implementation/build_stages.json`; `financials/assumptions.json` enthält nur Verweise und die Szenariodefinitionen (R-04).

## 2 Handelskosten je Instrument

Kosten je Seite = Kommission + halber Spread + Schlupf (+ Marktwirkung bei größeren Orders). Die Kommission ist die All-in-Gebühr des Primärbrokers (<!--v:costreg:COST-COMM-FXFLAT|eur2-->1,00 EUR<!--/v--> je Kontrakt und Seite, Staffel ab <!--v:costreg:COST-COMM-FXFLAT-LOW|eur2-->0,80 EUR<!--/v-->; SRC-BRK-FXFLAT); Börsen- und Clearinggebühren sind darin nach Angabe des Brokers enthalten, die schriftliche Bestätigung fehlt (X-BRK-FEES). Der Spread ist ein Planwert in Ticks je Kontrakt bis zur Messung in G1/G2 (X-DATA-VOL), der Schlupf beträgt <!--v:costreg:COST-EXEC-SLIP-TICKS|d2-->0,25<!--/v--> Tick je Seite. Die Marktwirkung folgt dem Quadratwurzelmodell Y · σ_Tag · √(max(0, q − a·ADV)/ADV) mit Y = <!--v:costreg:COST-EXEC-IMPACT-Y|d1-->0,7<!--/v--> und freier Tiefe a = <!--v:costreg:COST-EXEC-IMPACT-FREE-SHARE|pct2-->0,01 %<!--/v--> des Tagesvolumens (SRC-LIT-AC-2000); einzelne Kontrakte haben damit keine Marktwirkung, erst größere Orders in hohen Stufen.

Die Größe, die über Zulassung und Wirtschaftlichkeit entscheidet, ist **c_RT**, die Round-Turn-Kosten geteilt durch die Jahresvolatilität eines Kontrakts in Euro: Sie gibt an, wie viel Sharpe-Ratio ein einzelner Round-Turn kostet. Mal Umschlag und geteilt durch √τ (Zeit im Markt) ergibt sich die Jahreskostenbelastung einer Strategie in Sharpe-Einheiten. Die Tabelle zeigt alle beim Primärbroker handelbaren Kontrakte, sortiert nach den Kosten der schnellen Trendfolge:

<!-- GEN:BEGIN tab.cost_instruments -->
| Symbol | Risikoklasse | Größe | Nominal EUR | Round-Turn EUR | Round-Turn bp | c_RT (Sharpe je RT) | Kosten S-TF (Sharpe/Jahr) | Kosten TF-D1 (Sharpe/Jahr) |
|---|---|---|---|---|---|---|---|---|
| GC | EDELMETALL | STANDARD | 370.520 | 15,15 | 0,41 | 0,00023 | 0,025 | 0,003 |
| BTC | KRYPTO | STANDARD | 481.991 | 56,77 | 1,18 | 0,00024 | 0,027 | 0,004 |
| RB | ENERGIE | STANDARD | 88.336 | 7,52 | 0,85 | 0,00024 | 0,027 | 0,004 |
| HO | ENERGIE | STANDARD | 95.697 | 7,52 | 0,79 | 0,00025 | 0,028 | 0,004 |
| SI | EDELMETALL | STANDARD | 292.262 | 34,86 | 1,19 | 0,00040 | 0,043 | 0,006 |
| PL | EDELMETALL | STANDARD | 61.344 | 8,57 | 1,40 | 0,00047 | 0,050 | 0,007 |
| ETH | KRYPTO | STANDARD | 175.269 | 56,77 | 3,24 | 0,00046 | 0,052 | 0,008 |
| MGC | EDELMETALL | MICRO | 37.052 | 3,31 | 0,89 | 0,00050 | 0,054 | 0,007 |
| HG | INDUSTRIEMETALL | STANDARD | 134.675 | 18,43 | 1,37 | 0,00055 | 0,059 | 0,007 |
| CL | ENERGIE | STANDARD | 71.773 | 15,15 | 2,11 | 0,00060 | 0,068 | 0,011 |
| MBT | KRYPTO | MICRO | 9.640 | 3,10 | 3,21 | 0,00064 | 0,072 | 0,012 |
| SIL | EDELMETALL | MICRO | 58.452 | 12,95 | 2,22 | 0,00074 | 0,080 | 0,010 |
| 6S | FX | STANDARD | 133.120 | 10,22 | 0,77 | 0,00096 | 0,102 | 0,012 |
| NG | ENERGIE | STANDARD | 27.605 | 15,15 | 5,49 | 0,00091 | 0,103 | 0,017 |
| 6E | FX | STANDARD | 125.000 | 10,22 | 0,82 | 0,00109 | 0,116 | 0,014 |
| GF | VIEH | STANDARD | 140.216 | 29,39 | 2,10 | 0,00116 | 0,126 | 0,016 |
| LE | VIEH | STANDARD | 77.119 | 15,15 | 1,96 | 0,00131 | 0,142 | 0,018 |
| ZL | AGRAR | STANDARD | 26.290 | 9,89 | 3,76 | 0,00134 | 0,144 | 0,018 |
| 6A | FX | STANDARD | 61.935 | 8,57 | 1,38 | 0,00138 | 0,147 | 0,018 |
| MCL | ENERGIE | MICRO | 7.177 | 3,31 | 4,62 | 0,00132 | 0,149 | 0,024 |
| MHG | INDUSTRIEMETALL | MICRO | 13.467 | 4,74 | 3,52 | 0,00141 | 0,151 | 0,019 |
| 6J | FX | STANDARD | 69.367 | 10,22 | 1,47 | 0,00147 | 0,157 | 0,019 |
| 6N | FX | STANDARD | 49.878 | 8,57 | 1,72 | 0,00172 | 0,183 | 0,022 |
| 6B | FX | STANDARD | 72.717 | 10,22 | 1,40 | 0,00176 | 0,187 | 0,022 |
| HE | VIEH | STANDARD | 33.301 | 15,15 | 4,55 | 0,00182 | 0,197 | 0,026 |
| ZS | AGRAR | STANDARD | 55.333 | 18,43 | 3,33 | 0,00185 | 0,199 | 0,025 |
| FBTP | ANLEIHE_MITTEL | STANDARD | 120.000 | 17,00 | 1,42 | 0,00189 | 0,201 | 0,024 |
| FGBX | ANLEIHE_LANG | STANDARD | 115.000 | 32,00 | 2,78 | 0,00199 | 0,212 | 0,025 |
| FGBL | ANLEIHE_MITTEL | STANDARD | 128.000 | 17,00 | 1,33 | 0,00204 | 0,218 | 0,026 |
| FOAT | ANLEIHE_MITTEL | STANDARD | 122.000 | 17,00 | 1,39 | 0,00205 | 0,218 | 0,026 |
| 6C | FX | STANDARD | 62.201 | 8,57 | 1,38 | 0,00230 | 0,245 | 0,029 |
| ZW | AGRAR | STANDARD | 28.322 | 18,43 | 6,51 | 0,00232 | 0,249 | 0,031 |
| ALI | INDUSTRIEMETALL | STANDARD | 56.963 | 26,65 | 4,68 | 0,00234 | 0,251 | 0,031 |
| KE | AGRAR | STANDARD | 27.605 | 18,43 | 6,68 | 0,00238 | 0,256 | 0,032 |
| ZM | AGRAR | STANDARD | 26.290 | 15,15 | 5,76 | 0,00262 | 0,281 | 0,035 |
| PA | EDELMETALL | STANDARD | 105.162 | 111,54 | 10,61 | 0,00265 | 0,287 | 0,037 |
| 6M | FX | STANDARD | 23.661 | 8,57 | 3,62 | 0,00279 | 0,297 | 0,035 |
| UB | ANLEIHE_LANG | STANDARD | 106.914 | 43,08 | 4,03 | 0,00288 | 0,307 | 0,037 |
| SIC | EDELMETALL | MICRO | 5.845 | 5,07 | 8,67 | 0,00289 | 0,312 | 0,041 |
| TN | ANLEIHE_LANG | STANDARD | 100.780 | 22,54 | 2,24 | 0,00298 | 0,318 | 0,038 |
| MNG | ENERGIE | MICRO | 2.760 | 5,07 | 18,36 | 0,00306 | 0,345 | 0,056 |
| ZF | ANLEIHE_MITTEL | STANDARD | 95.084 | 12,27 | 1,29 | 0,00340 | 0,362 | 0,043 |
| ZB | ANLEIHE_LANG | STANDARD | 103.409 | 43,08 | 4,17 | 0,00379 | 0,404 | 0,048 |
| FGBM | ANLEIHE_MITTEL | STANDARD | 117.000 | 17,00 | 1,45 | 0,00382 | 0,407 | 0,049 |
| ZC | AGRAR | STANDARD | 21.938 | 18,43 | 8,40 | 0,00382 | 0,410 | 0,051 |
| 1OZ | EDELMETALL | MICRO | 3.705 | 2,55 | 6,88 | 0,00382 | 0,413 | 0,054 |
| M6E | FX | MICRO | 12.500 | 3,64 | 2,91 | 0,00389 | 0,414 | 0,049 |
| ZN | ANLEIHE_MITTEL | STANDARD | 98.151 | 22,54 | 2,30 | 0,00396 | 0,422 | 0,050 |
| ZT | ANLEIHE_KURZ | STANDARD | 182.280 | 12,27 | 0,67 | 0,00421 | 0,448 | 0,054 |
| 2YY | RENDITE | MICRO | 3.155 | 4,19 | 13,28 | 0,00531 | 0,566 | 0,068 |
| MSF | FX | MICRO | 13.312 | 5,83 | 4,38 | 0,00548 | 0,584 | 0,070 |
| FGBS | ANLEIHE_KURZ | STANDARD | 107.000 | 9,50 | 0,89 | 0,00555 | 0,591 | 0,071 |
| M6B | FX | MICRO | 7.272 | 3,37 | 4,63 | 0,00579 | 0,617 | 0,074 |
| 10Y | RENDITE | MICRO | 3.681 | 4,19 | 11,39 | 0,00599 | 0,639 | 0,076 |
| M6A | FX | MICRO | 6.194 | 4,19 | 6,77 | 0,00677 | 0,721 | 0,086 |
| MJY | FX | MICRO | 6.937 | 4,74 | 6,83 | 0,00683 | 0,728 | 0,087 |
| QG | ENERGIE | MINI | 6.901 | 29,39 | 42,58 | 0,00710 | 0,801 | 0,129 |
| MZS | AGRAR | MICRO | 5.533 | 7,48 | 13,51 | 0,00751 | 0,806 | 0,101 |
| MET | KRYPTO | MICRO | 351 | 2,11 | 60,18 | 0,00860 | 0,970 | 0,156 |
| MZW | AGRAR | MICRO | 2.832 | 7,48 | 26,40 | 0,00943 | 1,012 | 0,126 |
| SR3 | STIR | STANDARD | 211.200 | 18,43 | 0,87 | 0,00970 | 1,033 | 0,123 |
| FST3 | STIR | STANDARD | 244.000 | 17,62 | 0,72 | 0,01204 | 1,283 | 0,153 |
| MCD | FX | MICRO | 6.220 | 5,07 | 8,15 | 0,01358 | 1,447 | 0,173 |
| MZC | AGRAR | MICRO | 2.194 | 7,48 | 34,08 | 0,01549 | 1,663 | 0,208 |
| SR1 | STIR | STANDARD | 351.663 | 29,39 | 0,84 | 0,01671 | 1,781 | 0,213 |
<!-- GEN:END tab.cost_instruments -->

Nur <!--v:calc:cost_below_threshold_stf|int-->4<!--/v--> Kontrakte liegen für S-TF unter der Kostenschwelle von <!--v:prior:admission_rule/cost_threshold_sr|d3-->0,030<!--/v-->; für die langsame Trendfolge TF-D1 sind es <!--v:calc:cost_below_threshold_tfd1|int-->49<!--/v-->, für TF-D1-7T <!--v:calc:cost_below_threshold_tfd17t|int-->14<!--/v-->. Rollkosten: je Roll ein zusätzlicher Round-Turn, gewichtet mit der Zeit im Markt (Rollen je Jahr aus P-UNI-ROLLS-PER-YEAR).

## 3 Fixkosten, Betreiberzeit und Zinseffekt

<!-- GEN:BEGIN tab.fixed_costs -->
| Posten | Betrag | Status |
|---|---|---|
| Marktdaten Anzeige (Broker) | 53,00 EUR/Monat | Basisfall; entfällt je Börse ab Kommissionsschwelle |
| Marktdaten Non-Display (Managed) | 1.568,12 EUR/Monat | Sensitivität X-DATA-ND |
| Marktdaten Non-Display (direkt) | 2.440,96 EUR/Monat | Sensitivität X-DATA-ND |
| Historische Daten (einmalig) | 3.477,35 EUR | Kibot, CQG-Abgleich, Databento |
| Infrastruktur (drei Instanzen, Sicherung, Alarm) | 135,00 EUR/Monat | ANNAHME (X-INF-VPS) |
| KI-Abo (Basis SUPER) | 87,63 EUR/Monat | Nous Portal |
| Coding-Agent im Aufbau | 200,00 EUR/Monat | ANNAHME |
| Externe Risikofunktion (ab G9) | 300,00 EUR/Monat | ANNAHME (X-ORG-RISK) |
| Penetrationstest / Audit / Gegenprüfung | 5.000 / 15.000 / 1.500 EUR | ANNAHME |
<!-- GEN:END tab.fixed_costs -->

Marktdaten: Die Kursgebühren des Brokers entfallen je Börse ab <!--v:costreg:COST-MD-FXFLAT-WAIVER|eur-->300 EUR<!--/v--> Kommission im Monat. Ob der automatisierte Handel eine Non-Display-Lizenz verlangt, klären Broker und Börsen (X-DATA-ND); die Sensitivitäten FIXKOSTEN_HOCH und DATEN_NON_DISPLAY_USER rechnen beide Fälle.

Betreiberzeit (EV-02): tägliche Routine <!--v:param:P-OPS-DAILY-MIN|d0-->20<!--/v--> Minuten, wöchentliche Risikorunde <!--v:param:P-OPS-WEEKLY-MIN|d0-->90<!--/v--> Minuten, monatliche Attribution <!--v:param:P-OPS-MONTHLY-MIN|d0-->240<!--/v--> Minuten, Incidents <!--v:param:P-OPS-INCIDENT-MIN|d0-->180<!--/v--> Minuten im Monat und quartalsweise Modellprüfung und Drills <!--v:param:P-OPS-QUARTERLY-MIN|d0-->480<!--/v--> Minuten; zusammen <!--v:dmc:operator_hours_per_year|d0-->314<!--/v--> Stunden im Jahr, bewertet mit <!--v:param:P-ECO-HOURLY-RATE|d0-->50<!--/v--> EUR je Stunde (markierter Standard X-OP-RATE). Ab G9 kommt die externe Risikofunktion mit <!--v:costreg:COST-EXT-RISK-ROLE|eur-->300 EUR<!--/v--> im Monat hinzu (X-ORG-RISK).

Zinseffekt: Von jedem Euro Kapital liegen <!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v--> beim Broker (P-ECO-CASH-AT-BROKER, Entwurf: Margin plus Puffer), der Rest bleibt im Geldmarkt zum Satz <!--v:param:P-ECO-CASH-RATE|pct2-->2,44 %<!--/v--> (€STR, SRC-ECB-ESTR). Verzinst der Broker nicht (Planwert <!--v:param:P-ECO-BROKER-RATE|pct1-->0,0 %<!--/v-->, X-BRK-INTEREST), kostet das φ · (r_Geldmarkt − r_Broker) · NAV; in der Referenzstufe <!--v:calc:cash_drag_ref|eur-->30.500 EUR<!--/v--> im Jahr. Deshalb verlangt jede Variante eine Überrendite gegenüber dem Geldmarkt und nicht bloß einen positiven Ertrag.

## 4 CFD-Vergleich (Rückfalloption, BQ-08a)

Der CFD-Pfad ist spezifiziert, aber abgeschaltet (DEC-CF-05, X-OP-CFD). Gerechnet ist ein typischer Aufschlag des CFD-Spreads (Faktor <!--v:costreg:COST-CFD-SPREAD-MULT|d1-->2,0<!--/v--> auf den Futures-Spread, ANNAHME bis zur Messung X-CFD-SPREADS) und die Übernachtfinanzierung nach der Formel des Beispielbrokers (Referenzsatz plus <!--v:costreg:COST-CFD-FIN-MARKUP|pct1-->2,5 %<!--/v-->, SRC-CFD-FIN-PEPPERSTONE) bei der Median-Haltedauer von S-TF. Für Privatkunden gelten die Hebelgrenzen, die Glattstellung bei der Hälfte der Initial-Margin und der Negativsaldoschutz (SRC-REG-ESMA-CFD, SRC-BAFIN-AV-CFD).

<!-- GEN:BEGIN tab.cfd -->
| Symbol | Future Round-Turn bp | CFD-Spread Round-Turn bp | CFD-Finanzierung long bp | CFD-Finanzierung short bp |
|---|---|---|---|---|
| 6E | 0,82 | 1,10 | 2,73 | 0,03 |
| GC | 0,41 | 0,59 | 2,73 | 0,03 |
| CL | 2,11 | 3,05 | 2,73 | 0,03 |
| FGBL | 1,33 | 1,95 | 2,73 | 0,03 |
| BTC | 1,18 | 2,05 | 2,73 | 0,03 |
<!-- GEN:END tab.cfd -->

Befund: Schon ohne Finanzierung ist der CFD-Round-Turn teurer als der Future; bei Long-Positionen kommt die Finanzierung dazu. Der CFD-Pfad löst das Kostenproblem also nicht.

## 5 Entscheidungs-Monte-Carlo

Je Ziehung: Netto-Sharpe S = D · (g − c̄ · k · u) − Δ mit Brutto-Prior g (§6.3), mittleren Kosten c̄ einschließlich Marktwirkung, Kostenunsicherheit u (Standardabweichung P-ECO-COST-UNC-SD) und den Sensitivitätsfaktoren k und Δ. Jahreswert V = NAV · σ_eff · (S + ε) − NAV · φ · (r_Geldmarkt − r_Broker) − Fixkosten, mit dem unter der Lückenregel erreichten σ_eff und einem Jahresrauschen ε. Kapitalwert: Aufbaukosten bis zum Pilot (<!--v:dmc:build_cost_until_pilot_eur|eur-->58.147 EUR<!--/v-->) und Audit im Jahr P-ECO-AUDIT-YEAR (<!--v:dmc:audit_cost_eur|eur-->17.381 EUR<!--/v-->) gegen die diskontierten Jahreswerte über <!--v:param:P-ECO-HORIZON-Y|d0-->5<!--/v--> Jahre; das erste Jahr ist ohne Standardhandel (P-ECO-RAMP-YEARS). Ausgegeben werden E[Jahreswert], P(NPV > 0), NPV-Quantile, Expected Shortfall des NPV, Break-even-Kapital und Wert je Risikoeinheit.

<!-- GEN:BEGIN tab.dmc -->
| Variante | Kapital (Mio. EUR) | Profil | Befund | E[Jahreswert] EUR | P(NPV > 0) | NPV Mittel EUR | Wert je Risikoeinheit | Break-even-Kapital EUR |
|---|---|---|---|---|---|---|---|---|
| U-KOSTEN | 0,25 | H5 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 0,25 | H10 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 0,25 | H15 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 0,25 | H20 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 0,5 | H5 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 0,5 | H10 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 0,5 | H15 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 0,5 | H20 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 1 | H5 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 1 | H10 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 1 | H15 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 1 | H20 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 5 | H5 | PROFILE_NOT_ADMISSIBLE | -24.145 | 0,38 | -153.346 | -0,084 | – |
| U-KOSTEN | 5 | H10 | PROFILE_NOT_ADMISSIBLE | -24.487 | 0,37 | -157.433 | -0,085 | – |
| U-KOSTEN | 5 | H15 | PROFILE_NOT_ADMISSIBLE | -24.516 | 0,37 | -156.057 | -0,085 | – |
| U-KOSTEN | 5 | H20 | PROFILE_NOT_ADMISSIBLE | -24.336 | 0,38 | -147.385 | -0,084 | – |
| U-KOSTEN | 25 | H5 | PROFILE_NOT_ADMISSIBLE | -62.395 | 0,46 | -292.786 | -0,042 | – |
| U-KOSTEN | 25 | H10 | PROFILE_NOT_ADMISSIBLE | -123.212 | 0,45 | -412.719 | -0,058 | – |
| U-KOSTEN | 25 | H15 | PROFILE_NOT_ADMISSIBLE | -121.947 | 0,44 | -496.081 | -0,058 | – |
| U-KOSTEN | 25 | H20 | PROFILE_NOT_ADMISSIBLE | -123.988 | 0,44 | -508.502 | -0,059 | – |
| U-KOSTEN | 100 | H5 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 100 | H10 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 100 | H15 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN | 100 | H20 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-BREAKEVEN | 0,25 | H5 | PROFILE_NOT_ADMISSIBLE | -23.459 | 0,00 | -150.248 | -1,562 | – |
| U-BREAKEVEN | 0,25 | H10 | PROFILE_NOT_ADMISSIBLE | -23.179 | 0,00 | -149.853 | -1,094 | – |
| U-BREAKEVEN | 0,25 | H15 | PROFILE_NOT_ADMISSIBLE | -23.173 | 0,00 | -149.251 | -1,094 | – |
| U-BREAKEVEN | 0,25 | H20 | PROFILE_NOT_ADMISSIBLE | -23.183 | 0,00 | -149.234 | -1,094 | – |
| U-BREAKEVEN | 0,5 | H5 | PROFILE_NOT_ADMISSIBLE | -24.309 | 0,00 | -153.292 | -0,809 | – |
| U-BREAKEVEN | 0,5 | H10 | PROFILE_NOT_ADMISSIBLE | -23.751 | 0,02 | -151.171 | -0,560 | – |
| U-BREAKEVEN | 0,5 | H15 | PROFILE_NOT_ADMISSIBLE | -23.761 | 0,02 | -151.093 | -0,561 | – |
| U-BREAKEVEN | 0,5 | H20 | PROFILE_NOT_ADMISSIBLE | -23.761 | 0,02 | -151.811 | -0,561 | – |
| U-BREAKEVEN | 1 | H5 | PROFILE_NOT_ADMISSIBLE | -26.026 | 0,05 | -159.524 | -0,433 | – |
| U-BREAKEVEN | 1 | H10 | PROFILE_NOT_ADMISSIBLE | -24.899 | 0,13 | -154.013 | -0,294 | – |
| U-BREAKEVEN | 1 | H15 | PROFILE_NOT_ADMISSIBLE | -24.892 | 0,13 | -155.421 | -0,294 | – |
| U-BREAKEVEN | 1 | H20 | PROFILE_NOT_ADMISSIBLE | -24.852 | 0,13 | -156.534 | -0,293 | – |
| U-BREAKEVEN | 5 | H5 | PROFILE_NOT_ADMISSIBLE | -30.731 | 0,32 | -177.222 | -0,137 | – |
| U-BREAKEVEN | 5 | H10 | PROFILE_NOT_ADMISSIBLE | -30.866 | 0,32 | -177.020 | -0,138 | – |
| U-BREAKEVEN | 5 | H15 | PROFILE_NOT_ADMISSIBLE | -30.598 | 0,32 | -176.836 | -0,137 | – |
| U-BREAKEVEN | 5 | H20 | PROFILE_NOT_ADMISSIBLE | -30.675 | 0,32 | -170.683 | -0,137 | – |
| U-BREAKEVEN | 25 | H5 | PROFILE_NOT_ADMISSIBLE | -66.606 | 0,45 | -287.768 | -0,049 | – |
| U-BREAKEVEN | 25 | H10 | PROFILE_NOT_ADMISSIBLE | -65.715 | 0,44 | -310.995 | -0,049 | – |
| U-BREAKEVEN | 25 | H15 | PROFILE_NOT_ADMISSIBLE | -66.252 | 0,45 | -289.500 | -0,049 | – |
| U-BREAKEVEN | 25 | H20 | PROFILE_NOT_ADMISSIBLE | -65.841 | 0,45 | -278.208 | -0,049 | – |
| U-BREAKEVEN | 100 | H5 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-BREAKEVEN | 100 | H10 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-BREAKEVEN | 100 | H15 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-BREAKEVEN | 100 | H20 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN-TFD1-7T | 0,25 | H5 | PROFILE_NOT_ADMISSIBLE | -22.878 | 0,00 | -148.365 | -1,524 | – |
| U-KOSTEN-TFD1-7T | 0,25 | H10 | PROFILE_NOT_ADMISSIBLE | -22.357 | 0,00 | -146.765 | -1,056 | 22.545.478 |
| U-KOSTEN-TFD1-7T | 0,25 | H15 | PROFILE_NOT_ADMISSIBLE | -22.358 | 0,00 | -146.408 | -1,056 | 22.604.023 |
| U-KOSTEN-TFD1-7T | 0,25 | H20 | PROFILE_NOT_ADMISSIBLE | -22.358 | 0,00 | -146.858 | -1,056 | 22.687.540 |
| U-KOSTEN-TFD1-7T | 0,5 | H5 | PROFILE_NOT_ADMISSIBLE | -23.138 | 0,00 | -149.275 | -0,771 | – |
| U-KOSTEN-TFD1-7T | 0,5 | H10 | PROFILE_NOT_ADMISSIBLE | -22.087 | 0,02 | -146.440 | -0,521 | 21.718.559 |
| U-KOSTEN-TFD1-7T | 0,5 | H15 | PROFILE_NOT_ADMISSIBLE | -22.099 | 0,02 | -146.187 | -0,522 | 22.226.710 |
| U-KOSTEN-TFD1-7T | 0,5 | H20 | PROFILE_NOT_ADMISSIBLE | -22.094 | 0,02 | -145.255 | -0,522 | 22.022.657 |
| U-KOSTEN-TFD1-7T | 1 | H5 | PROFILE_NOT_ADMISSIBLE | -22.380 | 0,07 | -146.201 | -0,373 | 99.216.839 |
| U-KOSTEN-TFD1-7T | 1 | H10 | PROFILE_NOT_ADMISSIBLE | -22.247 | 0,07 | -147.223 | -0,362 | 62.780.452 |
| U-KOSTEN-TFD1-7T | 1 | H15 | PROFILE_NOT_ADMISSIBLE | -22.245 | 0,07 | -146.500 | -0,362 | 62.415.648 |
| U-KOSTEN-TFD1-7T | 1 | H20 | PROFILE_NOT_ADMISSIBLE | -22.235 | 0,07 | -146.812 | -0,362 | 60.756.628 |
| U-KOSTEN-TFD1-7T | 5 | H5 | PROFILE_NOT_ADMISSIBLE | -19.456 | 0,36 | -137.140 | -0,087 | 35.861.584 |
| U-KOSTEN-TFD1-7T | 5 | H10 | PROFILE_NOT_ADMISSIBLE | -19.409 | 0,36 | -133.207 | -0,087 | 35.343.719 |
| U-KOSTEN-TFD1-7T | 5 | H15 | PROFILE_NOT_ADMISSIBLE | -19.412 | 0,35 | -138.101 | -0,087 | 35.374.820 |
| U-KOSTEN-TFD1-7T | 5 | H20 | PROFILE_NOT_ADMISSIBLE | -19.230 | 0,35 | -138.294 | -0,086 | 33.464.976 |
| U-KOSTEN-TFD1-7T | 25 | H5 | PROFILE_NOT_ADMISSIBLE | -8.151 | 0,48 | -100.889 | -0,008 | 39.094.447 |
| U-KOSTEN-TFD1-7T | 25 | H10 | PROFILE_NOT_ADMISSIBLE | -7.349 | 0,48 | -82.502 | -0,007 | 37.041.558 |
| U-KOSTEN-TFD1-7T | 25 | H15 | PROFILE_NOT_ADMISSIBLE | -8.124 | 0,48 | -100.792 | -0,008 | 39.021.506 |
| U-KOSTEN-TFD1-7T | 25 | H20 | PROFILE_NOT_ADMISSIBLE | -8.106 | 0,48 | -95.303 | -0,008 | 38.973.015 |
| U-KOSTEN-TFD1-7T | 100 | H5 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN-TFD1-7T | 100 | H10 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN-TFD1-7T | 100 | H15 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN-TFD1-7T | 100 | H20 | NOT_VIABLE_AT_CAPITAL | – | – | – | – | – |
| U-KOSTEN-TFD1 | 0,25 | H5 | PROFILE_NOT_ADMISSIBLE | -20.810 | 0,00 | -141.586 | -1,519 | 3.143.998 |
| U-KOSTEN-TFD1 | 0,25 | H10 | PROFILE_NOT_ADMISSIBLE | -20.804 | 0,00 | -141.529 | -1,519 | 3.133.830 |
| U-KOSTEN-TFD1 | 0,25 | H15 | PROFILE_NOT_ADMISSIBLE | -20.809 | 0,00 | -141.625 | -1,519 | 3.142.693 |
| U-KOSTEN-TFD1 | 0,25 | H20 | PROFILE_NOT_ADMISSIBLE | -20.795 | 0,00 | -141.621 | -1,518 | 3.118.516 |
| U-KOSTEN-TFD1 | 0,5 | H5 | PROFILE_NOT_ADMISSIBLE | -20.236 | 0,00 | -139.546 | -1,058 | 4.766.490 |
| U-KOSTEN-TFD1 | 0,5 | H10 | PROFILE_NOT_ADMISSIBLE | -20.254 | 0,00 | -139.648 | -1,059 | 4.803.514 |
| U-KOSTEN-TFD1 | 0,5 | H15 | PROFILE_NOT_ADMISSIBLE | -20.239 | 0,00 | -140.086 | -1,058 | 4.771.908 |
| U-KOSTEN-TFD1 | 0,5 | H20 | PROFILE_NOT_ADMISSIBLE | -20.251 | 0,00 | -140.296 | -1,059 | 4.797.521 |
| U-KOSTEN-TFD1 | 1 | H5 | PROFILE_NOT_ADMISSIBLE | -15.015 | 0,03 | -122.397 | -0,396 | 2.977.609 |
| U-KOSTEN-TFD1 | 1 | H10 | PROFILE_NOT_ADMISSIBLE | -15.055 | 0,03 | -123.077 | -0,398 | 2.993.244 |
| U-KOSTEN-TFD1 | 1 | H15 | PROFILE_NOT_ADMISSIBLE | -15.067 | 0,03 | -123.074 | -0,398 | 2.998.052 |
| U-KOSTEN-TFD1 | 1 | H20 | PROFILE_NOT_ADMISSIBLE | -15.010 | 0,03 | -123.353 | -0,396 | 2.975.585 |
| U-KOSTEN-TFD1 | 5 | H5 | PROFILE_NOT_ADMISSIBLE | 8.155 | 0,42 | -46.197 | 0,063 | 3.674.568 |
| U-KOSTEN-TFD1 | 5 | H10 | PROFILE_NOT_ADMISSIBLE | 8.088 | 0,41 | -47.205 | 0,063 | 3.682.605 |
| U-KOSTEN-TFD1 | 5 | H15 | PROFILE_NOT_ADMISSIBLE | 8.024 | 0,42 | -45.995 | 0,062 | 3.690.254 |
| U-KOSTEN-TFD1 | 5 | H20 | PROFILE_NOT_ADMISSIBLE | 7.994 | 0,42 | -45.810 | 0,062 | 3.693.823 |
| U-KOSTEN-TFD1 | 25 | H5 | PROFILE_NOT_ADMISSIBLE | 131.042 | 0,63 | 353.217 | 0,206 | 3.623.333 |
| U-KOSTEN-TFD1 | 25 | H10 | PROFILE_NOT_ADMISSIBLE | 130.056 | 0,63 | 357.376 | 0,205 | 3.646.787 |
| U-KOSTEN-TFD1 | 25 | H15 | PROFILE_NOT_ADMISSIBLE | 130.210 | 0,63 | 350.390 | 0,205 | 3.643.118 |
| U-KOSTEN-TFD1 | 25 | H20 | PROFILE_NOT_ADMISSIBLE | 130.076 | 0,62 | 327.839 | 0,205 | 3.646.312 |
| U-KOSTEN-TFD1 | 100 | H5 | PROFILE_NOT_ADMISSIBLE | 553.164 | 0,65 | 1.757.108 | 0,210 | 3.860.356 |
| U-KOSTEN-TFD1 | 100 | H10 | PROFILE_NOT_ADMISSIBLE | 556.929 | 0,65 | 1.729.782 | 0,211 | 3.835.265 |
| U-KOSTEN-TFD1 | 100 | H15 | PROFILE_NOT_ADMISSIBLE | 551.179 | 0,65 | 1.697.093 | 0,209 | 3.873.722 |
| U-KOSTEN-TFD1 | 100 | H20 | PROFILE_NOT_ADMISSIBLE | 549.572 | 0,65 | 1.723.553 | 0,208 | 3.884.609 |
<!-- GEN:END tab.dmc -->

**Befundklassen** (Reihenfolge der Prüfung): PROFILE_NOT_ADMISSIBLE, wenn das Profil nach §7.4 unzulässig ist; NON_POSITIVE_BASE, wenn die Mehrertragsrate σ_eff · E[S] − φ · (r_Geldmarkt − r_Broker) nicht positiv ist; NOT_VIABLE_AT_CAPITAL, wenn bei diesem Kapital kein Instrument zugelassen ist (leeres Universum, DEC-DS-25) oder der erwartete Jahreswert nicht positiv ist oder P(NPV > 0) unter <!--v:param:P-ECO-MARGINAL-P|pct0-->50 %<!--/v--> liegt; DOMINATED_BY_ALTERNATIVE, wenn der Wert je Risikoeinheit die Untergrenze von V1 (<!--v:param:P-ECO-V1-SR/0|d2-->0,05<!--/v-->) nicht übertrifft; VIABLE ab P(NPV > 0) ≥ <!--v:param:P-ECO-VIABLE-P|pct0-->80 %<!--/v-->; sonst MARGINAL.

## 6 Sensitivitäten der Alternative TF-D1 in H5

<!-- GEN:BEGIN tab.dmc_sens_tfd1 -->
| Kapital (Mio. EUR) | Sensitivität | Befund | P(NPV > 0) | E[Jahreswert] EUR |
|---|---|---|---|---|
| 0,25 | KOSTEN X1 5 | PROFILE_NOT_ADMISSIBLE | 0,00 | -20.997 |
| 0,25 | KOSTEN X2 | PROFILE_NOT_ADMISSIBLE | 0,00 | -21.254 |
| 0,25 | KOSTEN X3 | PROFILE_NOT_ADMISSIBLE | 0,00 | -21.670 |
| 0,25 | PRIOR MINUS 0 05 | PROFILE_NOT_ADMISSIBLE | 0,00 | -21.492 |
| 0,25 | PRIOR MINUS 0 10 | PROFILE_NOT_ADMISSIBLE | 0,00 | -22.177 |
| 0,25 | FIXKOSTEN HOCH | PROFILE_NOT_ADMISSIBLE | 0,00 | -49.725 |
| 0,25 | BETREIBERZEIT HOCH | PROFILE_NOT_ADMISSIBLE | 0,00 | -36.500 |
| 0,25 | DATEN NON DISPLAY USER | PROFILE_NOT_ADMISSIBLE | 0,00 | -49.469 |
| 0,25 | STEUER SENSITIVITAET | PROFILE_NOT_ADMISSIBLE | 0,00 | -20.807 |
| 0,25 | ALLES BEIM BROKER | PROFILE_NOT_ADMISSIBLE | 0,00 | -25.375 |
| 0,25 | BROKER ZAHLT GELDMARKTZINS | PROFILE_NOT_ADMISSIBLE | 0,00 | -19.249 |
| 0,25 | PRIOR AUF INDEXNIVEAU | PROFILE_NOT_ADMISSIBLE | 0,00 | -21.877 |
| 0,5 | KOSTEN X1 5 | PROFILE_NOT_ADMISSIBLE | 0,00 | -20.627 |
| 0,5 | KOSTEN X2 | PROFILE_NOT_ADMISSIBLE | 0,00 | -21.013 |
| 0,5 | KOSTEN X3 | PROFILE_NOT_ADMISSIBLE | 0,00 | -21.769 |
| 0,5 | PRIOR MINUS 0 05 | PROFILE_NOT_ADMISSIBLE | 0,00 | -21.201 |
| 0,5 | PRIOR MINUS 0 10 | PROFILE_NOT_ADMISSIBLE | 0,00 | -22.230 |
| 0,5 | FIXKOSTEN HOCH | PROFILE_NOT_ADMISSIBLE | 0,00 | -49.234 |
| 0,5 | BETREIBERZEIT HOCH | PROFILE_NOT_ADMISSIBLE | 0,00 | -35.972 |
| 0,5 | DATEN NON DISPLAY USER | PROFILE_NOT_ADMISSIBLE | 0,00 | -48.942 |
| 0,5 | STEUER SENSITIVITAET | PROFILE_NOT_ADMISSIBLE | 0,00 | -20.230 |
| 0,5 | ALLES BEIM BROKER | PROFILE_NOT_ADMISSIBLE | 0,00 | -29.423 |
| 0,5 | BROKER ZAHLT GELDMARKTZINS | PROFILE_NOT_ADMISSIBLE | 0,00 | -17.196 |
| 0,5 | PRIOR AUF INDEXNIVEAU | PROFILE_NOT_ADMISSIBLE | 0,00 | -22.517 |
| 1 | KOSTEN X1 5 | PROFILE_NOT_ADMISSIBLE | 0,02 | -15.773 |
| 1 | KOSTEN X2 | PROFILE_NOT_ADMISSIBLE | 0,02 | -16.432 |
| 1 | KOSTEN X3 | PROFILE_NOT_ADMISSIBLE | 0,02 | -17.776 |
| 1 | PRIOR MINUS 0 05 | PROFILE_NOT_ADMISSIBLE | 0,02 | -16.972 |
| 1 | PRIOR MINUS 0 10 | PROFILE_NOT_ADMISSIBLE | 0,02 | -18.797 |
| 1 | FIXKOSTEN HOCH | PROFILE_NOT_ADMISSIBLE | 0,00 | -44.020 |
| 1 | BETREIBERZEIT HOCH | PROFILE_NOT_ADMISSIBLE | 0,00 | -30.630 |
| 1 | DATEN NON DISPLAY USER | PROFILE_NOT_ADMISSIBLE | 0,00 | -43.636 |
| 1 | STEUER SENSITIVITAET | PROFILE_NOT_ADMISSIBLE | 0,01 | -15.179 |
| 1 | ALLES BEIM BROKER | PROFILE_NOT_ADMISSIBLE | 0,00 | -33.348 |
| 1 | BROKER ZAHLT GELDMARKTZINS | PROFILE_NOT_ADMISSIBLE | 0,05 | -8.940 |
| 1 | PRIOR AUF INDEXNIVEAU | PROFILE_NOT_ADMISSIBLE | 0,01 | -22.478 |
| 5 | KOSTEN X1 5 | PROFILE_NOT_ADMISSIBLE | 0,38 | 4.342 |
| 5 | KOSTEN X2 | PROFILE_NOT_ADMISSIBLE | 0,38 | 744 |
| 5 | KOSTEN X3 | PROFILE_NOT_ADMISSIBLE | 0,32 | -6.260 |
| 5 | PRIOR MINUS 0 05 | PROFILE_NOT_ADMISSIBLE | 0,38 | 2.132 |
| 5 | PRIOR MINUS 0 10 | PROFILE_NOT_ADMISSIBLE | 0,34 | -4.904 |
| 5 | FIXKOSTEN HOCH | PROFILE_NOT_ADMISSIBLE | 0,26 | -20.876 |
| 5 | BETREIBERZEIT HOCH | PROFILE_NOT_ADMISSIBLE | 0,32 | -7.183 |
| 5 | DATEN NON DISPLAY USER | PROFILE_NOT_ADMISSIBLE | 0,26 | -20.662 |
| 5 | STEUER SENSITIVITAET | PROFILE_NOT_ADMISSIBLE | 0,31 | 7.908 |
| 5 | ALLES BEIM BROKER | PROFILE_NOT_ADMISSIBLE | 0,06 | -83.275 |
| 5 | BROKER ZAHLT GELDMARKTZINS | PROFILE_NOT_ADMISSIBLE | 0,59 | 38.700 |
| 5 | PRIOR AUF INDEXNIVEAU | PROFILE_NOT_ADMISSIBLE | 0,21 | -32.102 |
| 25 | KOSTEN X1 5 | PROFILE_NOT_ADMISSIBLE | 0,59 | 106.888 |
| 25 | KOSTEN X2 | PROFILE_NOT_ADMISSIBLE | 0,57 | 81.616 |
| 25 | KOSTEN X3 | PROFILE_NOT_ADMISSIBLE | 0,51 | 30.755 |
| 25 | PRIOR MINUS 0 05 | PROFILE_NOT_ADMISSIBLE | 0,58 | 97.053 |
| 25 | PRIOR MINUS 0 10 | PROFILE_NOT_ADMISSIBLE | 0,55 | 67.144 |
| 25 | FIXKOSTEN HOCH | PROFILE_NOT_ADMISSIBLE | 0,60 | 100.765 |
| 25 | BETREIBERZEIT HOCH | PROFILE_NOT_ADMISSIBLE | 0,59 | 113.185 |
| 25 | DATEN NON DISPLAY USER | PROFILE_NOT_ADMISSIBLE | 0,60 | 101.788 |
| 25 | STEUER SENSITIVITAET | PROFILE_NOT_ADMISSIBLE | 0,51 | 125.151 |
| 25 | ALLES BEIM BROKER | PROFILE_NOT_ADMISSIBLE | 0,15 | -324.381 |
| 25 | BROKER ZAHLT GELDMARKTZINS | PROFILE_NOT_ADMISSIBLE | 0,78 | 281.272 |
| 25 | PRIOR AUF INDEXNIVEAU | PROFILE_NOT_ADMISSIBLE | 0,39 | -70.293 |
| 100 | KOSTEN X1 5 | PROFILE_NOT_ADMISSIBLE | 0,62 | 446.723 |
| 100 | KOSTEN X2 | PROFILE_NOT_ADMISSIBLE | 0,60 | 342.172 |
| 100 | KOSTEN X3 | PROFILE_NOT_ADMISSIBLE | 0,53 | 127.870 |
| 100 | PRIOR MINUS 0 05 | PROFILE_NOT_ADMISSIBLE | 0,62 | 433.648 |
| 100 | PRIOR MINUS 0 10 | PROFILE_NOT_ADMISSIBLE | 0,58 | 295.038 |
| 100 | FIXKOSTEN HOCH | PROFILE_NOT_ADMISSIBLE | 0,65 | 523.473 |
| 100 | BETREIBERZEIT HOCH | PROFILE_NOT_ADMISSIBLE | 0,66 | 533.994 |
| 100 | DATEN NON DISPLAY USER | PROFILE_NOT_ADMISSIBLE | 0,65 | 524.224 |
| 100 | STEUER SENSITIVITAET | PROFILE_NOT_ADMISSIBLE | 0,56 | 549.701 |
| 100 | ALLES BEIM BROKER | PROFILE_NOT_ADMISSIBLE | 0,17 | -1.267.371 |
| 100 | BROKER ZAHLT GELDMARKTZINS | PROFILE_NOT_ADMISSIBLE | 0,80 | 1.165.110 |
| 100 | PRIOR AUF INDEXNIVEAU | PROFILE_NOT_ADMISSIBLE | 0,42 | -206.849 |
<!-- GEN:END tab.dmc_sens_tfd1 -->

Lesart: Die Tabelle zeigt, wie die Alternative auf Kosten, Prior, Fixkosten und Zinsen reagiert; die Befundklasse je Zeile bleibt die der Basis, weil die Zulässigkeit des Profils nicht von diesen Annahmen abhängt. Am stärksten wirken ein Guthaben vollständig beim Broker, ein Prior auf dem Niveau realisierter Trendfolge-Indizes und die Verzinsung des Brokerguthabens (X-BRK-INTEREST).

## 7 Go/No-Go je Kapitalstufe und Profil

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

Demo- und Paper-Betrieb sind in allen Zellen zulässig, begrenzt durch den Ausgabendeckel (P-ECO-SPEND-CAP, X-OP-BUDGET). Echtgeld ist in allen Zellen No-Go; die Alternative TF-D1 ist keine Empfehlung, weil sie deine Höchsthaltedauer aufgibt (R-09), ihr Prior über realisierten Indexwerten liegt und sie nach der Größenregel mit Wochenendfaktor in <!--v:calc:dmc_class_count/U-KOSTEN-TFD1/PROFILE_NOT_ADMISSIBLE|int-->24<!--/v--> von <!--v:calc:dmc_cells/U-KOSTEN-TFD1|int-->24<!--/v--> Zellen unzulässig ist.

## 8 Grenzen des Modells

- Die Ziehungen sind synthetisch; sie beschreiben Unsicherheit über Parameter, nicht beobachtete Erträge (R-02).
- Spreads, Volatilitäten, Tagesvolumina und Margins sind Planungswerte (Status ANNAHME), bis G1/G2 sie messen.
- Steuern sind nur als pauschale Sensitivität enthalten (BQ-03); B2 bis B4 sind nicht gerechnet (BQ-02).
- Die Korrelationen zwischen Instrumenten sind Klassenannahmen (P-PRI-RHO-*); eine geschätzte Kovarianz ersetzt sie in G3 (MOD-COV).
