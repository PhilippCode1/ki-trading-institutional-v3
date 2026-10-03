# Limits-Hierarchie (§7.5, §7.6)

> **Betreiberfassung.** Limits wirken auf fünf Ebenen: Konto, Strategie, Anlageklasse, Instrument und Korrelationscluster. Deine Tagesgrenze von <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v--> ist die oberste harte Grenze; damit sie nie erreicht wird, greifen vorher eine Lückenregel vor jeder Order und eine dreistufige Tagesverlust-Leiter (Halbieren, Einstiegssperre, Abbau). Über mehrere Tage schützen Wochenverlust- und Drawdown-Leiter; der Kill-Switch storniert alle Orders in Sekunden. Jede Grenze ist eine Zeile in `registers/limits.json` mit Verweis auf ihren Wert in `parameters.json`, sodass es keine zweite Wahrheit gibt. Für Go/No-Go heißt das: Die Limits sind vollständig spezifiziert, ihre Wirksamkeit wird erst in Drills und im Paper-Betrieb nachgewiesen. Nächster Schritt ist die Umsetzung im Risikomotor (BS-05) mit den Abnahmetests aus `implementation/test_catalog.json`.

## 1 Register

<!-- GEN:BEGIN tab.limits -->
| ID | Ebene | Art | Wert | Quelle des Werts | Reaktion | Zeitpunkt | Hinweis |
|---|---|---|---|---|---|---|---|
| LIM-ACC-DLC | KONTO | TAGESVERLUST | 0,09 Anteil NAV | P-OP-DAILY-LOSS-CAP | HARTE_GRENZE | INTRADAY | Betreiber-Grenze; wird durch LIM-ACC-GAP vorab erzwungen |
| LIM-ACC-DL1 | KONTO | TAGESVERLUST | 0,03 Anteil NAV | P-RISK-DL-L1 | RISIKOZIEL_HALBIEREN | INTRADAY | – |
| LIM-ACC-DL2 | KONTO | TAGESVERLUST | 0,05 Anteil NAV | P-RISK-DL-L2 | EINSTIEGSSPERRE | INTRADAY | – |
| LIM-ACC-DL3 | KONTO | TAGESVERLUST | 0,065 Anteil NAV | P-RISK-DL-L3 | GEORDNETER_ABBAU | INTRADAY | – |
| LIM-ACC-GAP | KONTO | LUECKENSTRESS | 0,01 Anteil NAV | P-RISK-GAP-RESERVE | ORDER_ABLEHNEN | PRE_TRADE | Lückenstress + Tagesverlust ≤ Grenze − Reserve |
| LIM-ACC-WEEK | KONTO | WOCHENVERLUST | 0,15 Anteil NAV | P-RISK-WEEK-LOSS | EINSTIEGSSPERRE | INTRADAY | – |
| LIM-ACC-DD-L1 | KONTO | DRAWDOWN | 0,10 Anteil NAV | P-RISK-DD-L1 | RISIKOZIEL_075 | EOD_UND_INTRADAY | – |
| LIM-ACC-DD-L2 | KONTO | DRAWDOWN | 0,15 Anteil NAV | P-RISK-DD-L2 | RISIKOZIEL_050_PROFILABSTIEG | EOD_UND_INTRADAY | – |
| LIM-ACC-DD-L3 | KONTO | DRAWDOWN | 0,20 Anteil NAV | P-RISK-DD-L3 | EINSTIEGSSPERRE | EOD_UND_INTRADAY | – |
| LIM-ACC-DD-KILL | KONTO | DRAWDOWN | 0,30 Anteil NAV | P-RISK-DD-KILL | ABBAU_STOPP | EOD_UND_INTRADAY | – |
| LIM-ACC-LG | KONTO | BRUTTO_HEBEL | H5 5; H10 10; H15 15; H20 20 | P-LEV-{PROFIL}-CAP | ORDER_ABLEHNEN | PRE_TRADE | – |
| LIM-ACC-ME | KONTO | MARGIN_AUSLASTUNG | H5 0,25; H10 0,35; H15 0,45; H20 0,50 | P-LEV-{PROFIL}-ME | ORDER_ABLEHNEN | PRE_TRADE | – |
| LIM-ACC-ES | KONTO | EXPECTED_SHORTFALL | H5 0,02; H10 0,03; H15 0,04; H20 0,05 | P-LEV-{PROFIL}-ES | ORDER_ABLEHNEN | PRE_TRADE | – |
| LIM-ACC-MRG | KONTO | MARGIN_LEVEL | 1,50 Anteil der Initial-Margin | P-MRG-DERISK-TRIGGER | ABBAU_BIS_SCHWELLE | INTRADAY | – |
| LIM-STR-BUDGET | STRATEGIE | RISIKOBUDGET | S-TF: 0,60; S-IM: 0,20; S-REV: 0,20 Anteile | P-STR-RISK-SHARES | SKALIEREN | PRE_TRADE | – |
| LIM-CLS-LEV | KLASSE | HEBELDECKEL | je Klasse (Tabelle Hebeldeckel) | risk/leverage_results.json#/class_caps | ORDER_ABLEHNEN | PRE_TRADE | – |
| LIM-INS-ADV | INSTRUMENT | LIQUIDITAET_ORDER | 0,01 Anteil | P-RISK-MAX-ADV-SHARE | ORDER_TEILEN_ODER_ABLEHNEN | PRE_TRADE | – |
| LIM-INS-OI | INSTRUMENT | KONZENTRATION | 0,005 Anteil | P-RISK-MAX-OI-SHARE | ORDER_ABLEHNEN | PRE_TRADE | – |
| LIM-INS-HOLD | INSTRUMENT | HALTEDAUER | 168 Stunden | P-OP-HOLD-MAX-H | ZEITSTOPP_SCHLIESSEN | INTRADAY | – |
| LIM-INS-ROLL | INSTRUMENT | VERFALL | 5 Geschäftstage | P-UNI-ROLL-DAYS | KEIN_EINSTIEG_SCHLIESSEN | PRE_TRADE | – |
| LIM-INS-EVENT | INSTRUMENT | EREIGNIS | 30 Minuten | P-RISK-EVENT-BLACKOUT-MIN | KEIN_EINSTIEG | PRE_TRADE | – |
| LIM-CLU-GAP | CLUSTER | LUECKENSTRESS_CLUSTER | ALLE_UNGUENSTIG Text | P-LEV-CLUSTER-MODE | INFORMATIV | EOD | – |
| LIM-PT-PRICE | INSTRUMENT | PREISKORRIDOR | PTC-01 | execution/pretrade_controls.md#PTC-01 | ORDER_ABLEHNEN | PRE_TRADE | – |
| LIM-PT-QTY | INSTRUMENT | HOECHSTMENGE | PTC-02 | execution/pretrade_controls.md#PTC-02 | ORDER_ABLEHNEN | PRE_TRADE | – |
| LIM-PT-RATE | KONTO | NACHRICHTENRATE | PTC-05 | execution/pretrade_controls.md#PTC-05 | DROSSELN | PRE_TRADE | – |
<!-- GEN:END tab.limits -->

## 2 Tagesverlust-Leiter und Lückenregel

Der Handelstag beginnt um <!--v:param:P-RISK-DAY-START|raw-->00:00 Europe/Berlin<!--/v--> (P-RISK-DAY-START); gemessen wird der Verlust gegenüber dem NAV zu Tagesbeginn, einschließlich unrealisierter Verluste zum aktuellen Kurs.

| Stufe | Schwelle | Wirkung | Heilung |
|---|---|---|---|
| Vorhandelsregel | Lückenstress (über Wochenenden × <!--v:param:P-RISK-WEEKEND-FACTOR|d1-->1,5<!--/v-->) + Tagesverlust ≤ <!--v:calc:gap_budget|pct0-->8 %<!--/v--> | Order wird abgelehnt oder verkleinert (PTC-13) | – |
| L1 | Tagesverlust ≥ <!--v:param:P-RISK-DL-L1|pct0-->3 %<!--/v--> | Risikoziel halbieren; neue Orders nur noch mit halber Größe | nächster Handelstag |
| L2 | Tagesverlust ≥ <!--v:param:P-RISK-DL-L2|pct0-->5 %<!--/v--> | Einstiegssperre, nur Schutz- und Abbauorders | nächster Handelstag, Quittung des Betreibers |
| L3 | Tagesverlust ≥ <!--v:param:P-RISK-DL-L3|pct1-->6,5 %<!--/v--> | geordneter Abbau aller Positionen über die Ausstiegslogik | Ursachenbericht und signierte Wiederaufnahme |
| Grenze | <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v--> | darf nie erreicht werden; Überschreitung ist ein schwerer Incident (RK-29) | neuer Grant nach Ursachenbericht |

Warum die Leiter so früh greift: Zwischen L3 und der Grenze bleiben <!--v:calc:dl_gap_l3|pct1-->2,5 %<!--/v--> Abstand für Kurslücken während des Abbaus. Die Lückenregel sorgt dafür, dass selbst eine gleichzeitige ungünstige Lücke aller Positionen den Tagesverlust nicht über die Grenze treibt, solange die Lücke innerhalb der Konstruktion bleibt. Die Restwahrscheinlichkeit jenseits der Konstruktion ist in `risk/leverage_risk_model.md` ausgewiesen.

## 3 Mehrtagesgrenzen

- **Wochenverlust:** ab <!--v:param:P-RISK-WEEK-LOSS|pct0-->15 %<!--/v--> Einstiegssperre bis zum Wochenende.
- **Drawdown-Leiter** vom Höchststand des NAV: <!--v:param:P-RISK-DD-L1|pct0-->10 %<!--/v--> Risikoziel um ein Viertel senken; <!--v:param:P-RISK-DD-L2|pct0-->15 %<!--/v--> Risikoziel halbieren und Abstieg um eine Profilstufe; <!--v:param:P-RISK-DD-L3|pct0-->20 %<!--/v--> Einstiegssperre und Betreiberprüfung; <!--v:param:P-RISK-DD-KILL|pct0-->30 %<!--/v--> Abbau und Stopp, Neustart nur mit neuem Grant.
- **Pilotverlustbudget:** Im Pilot (G8) endet der Betrieb, wenn der Verlust <!--v:param:P-RES-PILOT-LOSS-BUDGET|pct0-->15 %<!--/v--> des Pilotkapitals erreicht.

## 4 Strategie-, Klassen-, Instrument- und Clustergrenzen

- **Strategie:** Risikobudget je Strategie nach P-STR-RISK-SHARES; keine Strategie darf das Budget einer anderen nutzen.
- **Anlageklasse:** Hebeldeckel je Klasse aus der Lückenregel (`risk/leverage_results.json`, `class_caps`).
- **Instrument:** Order höchstens <!--v:param:P-RISK-MAX-ADV-SHARE|pct0-->1 %<!--/v--> des Tagesvolumens, Position höchstens <!--v:param:P-RISK-MAX-OI-SHARE|pct1-->0,5 %<!--/v--> des Open Interest; Haltedauer höchstens <!--v:param:P-OP-HOLD-MAX-H|d0-->168<!--/v--> Stunden; keine neuen Einstiege <!--v:param:P-UNI-ROLL-DAYS|d0-->5<!--/v--> Geschäftstage vor FND/LTD und <!--v:param:P-RISK-EVENT-BLACKOUT-MIN|d0-->30<!--/v--> Minuten vor registrierten Ereignissen.
- **Korrelationscluster:** Die Lückenregel rechnet ohnehin mit ungünstiger Richtung aller Positionen (Korrelation eins); eine Clusterrechnung ist nur informativ (P-LEV-CLUSTER-MODE).

## 5 Kill-Switch

Stufe 1 storniert alle offenen Orders des Kontos innerhalb von <!--v:param:P-RISK-KILL-CANCEL-S|d0-->5<!--/v--> Sekunden und sperrt Einstiege; Stufe 2 stellt zusätzlich alle Positionen geordnet über die Ausstiegslogik glatt. Auslöser: Betreiber (Cockpit oder mobile Notfallansicht), unabhängiges Prüfmodul (Evaluator) bei Grenzverletzung oder Abweichung, Risikomotor bei L3. Der Kill-Switch storniert nie den Schutzstopp einer offenen Position, solange diese nicht geschlossen ist. Er wird in jedem Quartal im Demokonto geprobt (`operations/drills.md`).

## 6 Post-Trade

Abgleich von Orders, Deals, Positionen und Salden gegen den Broker in festen Intervallen (P-EXE-RECON-ACTIVE-S, P-EXE-RECON-IDLE-S) und gegen den Tagesauszug; täglich P&L-Erklärung je Strategie und Instrument (Preis, Kosten, Rollen, Währung). Jede unerklärte Abweichung über einem Tick je Kontrakt ist ein Incident.
