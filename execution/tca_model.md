# Ausführungsqualität und Transaktionskostenanalyse (§8.4, §14.2)

> **Betreiberfassung.** Weil Kosten bei deinem Haltehorizont über Erfolg oder Misserfolg entscheiden, misst das System jede Ausführung gegen den Kurs zum Entscheidungszeitpunkt und gegen das Kostenmodell. Die Messung beginnt mit den Killer-Tests, wird im Paper-Betrieb vorbereitet und erst im Pilot mit echten Fills belastbar, weil Demo-Fills vom Broker simuliert sind. Eine gepoolte Kostendrift-Überwachung erkennt zu hohe Kosten schneller als die Prüfung je Instrument aus v2.0 und stoppt dann Einstiege. Planwerte für Spread und Schlupf werden ersetzt, sobald Messungen vorliegen. Für Go/No-Go heißt das: Ohne gemessene Kosten im Modellband kein Aufstieg der Hebelstufe und kein Standardbetrieb. Nächster Schritt ist die Messung von Spreads in G2 (X-DATA-VOL) und von Schlupf im Pilot (X-EXEC-TCA).

## 1 Kennzahlen

| Kennzahl | Definition |
|---|---|
| Entscheidungskurs | Mittelkurs zum Zeitpunkt der Absicht des Portfoliomotors |
| Ankunftskurs | Mittelkurs, wenn die Order den Adapter verlässt |
| Implementation Shortfall | (Ausführungspreis − Entscheidungskurs) × Richtung × Menge × Multiplikator + Kommission + Opportunitätskosten nicht ausgeführter Menge |
| Zerlegung | Verzögerung (Entscheidung → Ankunft), halber Spread, Marktwirkung und Timing (Ankunft → Ausführung), Kommission, Opportunität |
| Kostenverhältnis | gemessene Kosten je Fill geteilt durch Modellkosten desselben Kontrakts und derselben Größe |

Gemessen wird je Fill und je Parent-Order, getrennt nach Instrument, Strategie, Tageszeit (Liquiditätsfenster oder nicht) und Ordergröße relativ zum Tagesvolumen.

## 2 Modell (MOD-SLIP)

Kosten je Seite = Kommission + halber Spread + Schlupf + Marktwirkung (`financials/cost_model.py`): Schlupf <!--v:costreg:COST-EXEC-SLIP-TICKS|d2-->0,25<!--/v--> Tick (außerhalb des Liquiditätsfensters <!--v:costreg:COST-EXEC-SLIP-TICKS-OFF|d2-->1,00<!--/v--> Tick), Marktwirkung Y · σ_Tag · √(max(0, q − a · ADV) / ADV) mit Y = <!--v:costreg:COST-EXEC-IMPACT-Y|d1-->0,7<!--/v--> und freier Tiefe a = <!--v:costreg:COST-EXEC-IMPACT-FREE-SHARE|pct2-->0,01 %<!--/v--> des Tagesvolumens. Parent-Orders über <!--v:param:P-EXE-ALGO-THRESHOLD|d0-->10<!--/v--> Kontrakten werden zeitlich zerlegt; die Obergrenze je Order beträgt <!--v:param:P-RISK-MAX-ADV-SHARE|pct0-->1 %<!--/v--> des Tagesvolumens (PTC-02).

## 3 Kalibrierung

| Stufe | Datenquelle | Zweck | Grenze |
|---|---|---|---|
| G1 (BS-01) | Killer-Test-Fills, Minimalgröße | Plausibilität von Kommission und Ausführungsweg | sehr wenige Fills |
| G2 (BS-02) | Intraday-Daten mit Geld- und Briefkursen | Spread je Instrument und Tageszeit, Tagesvolumen, Liquiditätsfenster | keine eigenen Fills |
| G7 (Paper) | simulierte Fills des Demokontos und eigene Schattenrechnung gegen Marktdaten | Prozess, Verzögerung, Abgleich | Demo-Fills sind nicht belastbar |
| G8 (Pilot) | echte Fills in H5 mit halber Größe | Schlupf und Kostenverhältnis je Instrumentgruppe (X-EXEC-TCA) | kleine Stichprobe; daher gepoolte Schätzung |

## 4 Kostendrift-Überwachung

Die Überwachung schätzt das Kostenverhältnis gepoolt über alle Instrumente mit Schrumpfung der Einzelschätzungen zum Poolmittel (Gewicht <!--v:param:P-MON-COSTDRIFT-SHRINK|d0-->20<!--/v--> Pseudo-Fills) und löst aus, wenn die Posterior-Wahrscheinlichkeit, dass das Verhältnis über <!--v:param:P-MON-COSTDRIFT-RATIO|d1-->1,3<!--/v--> liegt, <!--v:param:P-MON-COSTDRIFT-PROB|pct0-->90 %<!--/v--> übersteigt. Die Streuung je Fill (P-MON-FILL-NOISE) ist ein Planwert bis zur Kalibrierung. Simulierte Auslösezeiten (`operations/costdrift_monitor.py`, <!--v:drift:runs|int-->1.000<!--/v--> Läufe, Referenz: <!--v:drift:reference/instruments|d0-->4<!--/v--> Instrumente mit je rund <!--v:drift:reference/fills_per_month_per_instrument|d0-->14<!--/v--> Fills im Monat):

<!-- GEN:BEGIN tab.costdrift -->
| Verfahren | wahres Kostenverhältnis | Median Monate bis Auslösung | P(Auslösung im Pilot) | P(Auslösung ≤ 24 Monate) |
|---|---|---|---|---|
| gepoolt mit Schrumpfung (v3.0) | 1,00 | 37 | 3,7 % | 3,7 % |
| gepoolt mit Schrumpfung (v3.0) | 1,30 | 5 | 54,7 % | 76,8 % |
| gepoolt mit Schrumpfung (v3.0) | 1,50 | 1 | 98,0 % | 100,0 % |
| gepoolt mit Schrumpfung (v3.0) | 2,00 | 1 | 100,0 % | 100,0 % |
| je Instrument, mindestens 20 Fills (wie v2.0) | 1,50 | 2 | 98,1 % | 100,0 % |
| je Instrument, mindestens 20 Fills (wie v2.0) | 2,00 | 2 | 100,0 % | 100,0 % |
| wie v2.0 mit Umschlag von TF-D1 | 2,00 | 15 | 0,0 % | 100,0 % |
<!-- GEN:END tab.costdrift -->

Lesart: Bei doppelten Kosten löst die gepoolte Überwachung im Median nach <!--v:drift:results/pooled/FAKTOR_2/median_months|d0-->1<!--/v--> Monat aus; die Prüfung je Instrument wie in v2.0 braucht bei der Handelsfrequenz von TF-D1 <!--v:drift:results/v2_frequency_unpooled_min20/FAKTOR_2/median_months|d0-->15<!--/v--> Monate. Ohne Drift gibt es während des Pilots in <!--v:drift:results/pooled/OHNE_DRIFT/p_trigger_within_pilot|pct1-->3,7 %<!--/v--> der Läufe einen Fehlalarm. **Reaktion:** Einstiegssperre für die betroffene Instrumentgruppe, Neuberechnung der Wirtschaftlichkeit mit gemessenen Kosten, Freigabe nur nach Betreiberentscheidung.

## 5 Rückkopplung

Gemessene Kosten ersetzen die Planwerte in `registers/costs.json` bzw. `registers/instruments.json` mit Datum und Quelle; danach laufen alle Rechner neu. Ein Aufstieg der Hebelstufe verlangt gemessene Kosten höchstens <!--v:param:P-LEV-STEP-COST-BAND|pct0-->25 %<!--/v--> über dem Modell (§7.8).
