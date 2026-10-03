# Forschungsplan (§6.4–§6.6, Tore G2 bis G4)

> **Betreiberfassung.** Die Forschung soll mit wenig Geld herausfinden, ob die registrierte Familie nach Kosten überhaupt eine Kante hat, und früh stoppen, wenn nicht. Sie läuft auf gekauften historischen Daten und im Demokonto, nie mit Echtgeld. Der wichtigste Befund vorab: Kleine Kanten lassen sich in realistischen Zeiträumen statistisch nicht nachweisen (<!--v:stat:years_for_power/0.3|d0-->69<!--/v--> Jahre Daten für eine Sharpe-Ratio von <!--v:param:P-RES-SR-USEFUL|d1-->0,3<!--/v-->), deshalb sind die Tore streng und halten auch brauchbare Strategien oft auf. Bis einschließlich G3 kostet der Weg <!--v:oc:cumulative_cost_eur/BS-03|eur-->12.791 EUR<!--/v-->. Für Go/No-Go heißt das: Forschung ist eine gedeckelte Lernausgabe, kein Weg zu schnellem Echtgeld. Nächster Schritt ist G2 mit Datenlizenz und Abgleich zweier Quellen.

## 1 Ablauf und Tore

| Tor | Stufe | Inhalt | besteht, wenn |
|---|---|---|---|
| GATE-G2 | BS-02 | Datenlizenz (X-DATA-LIC), Kauf, Abgleich zweier Quellen, Leckagetests, Messung von Spreads, Volatilitäten, Tagesvolumen und Liquiditätsfenstern (X-DATA-VOL, X-DATA-LIQ), Bestätigung der Historie (X-DATA-HIST) | Abgleichquote ≥ <!--v:param:P-DATA-XCHECK-SHARE-MIN|pct0-->99 %<!--/v-->, keine Leckage, Messbericht vollständig |
| GATE-G3 | BS-03 | Forschung auf den Entwicklungsjahren (P-RES-DEV-YEARS) nach Vorregistrierung | DSR ≥ <!--v:param:P-RES-DSR-MIN|d2-->0,95<!--/v-->, PBO ≤ <!--v:param:P-RES-PBO-MAX|pct0-->20 %<!--/v-->, Reality Check bzw. SPA signifikant auf <!--v:param:P-RES-ALPHA|pct0-->5 %<!--/v-->, Futility-Wahrscheinlichkeit ≥ <!--v:param:P-RES-FUTILITY|pct0-->10 %<!--/v--> |
| GATE-G4 | BS-04 | einmalige Öffnung des versiegelten Holdouts (P-RES-HOLDOUT-YEARS) | Netto-Sharpe im Holdout positiv und Futility-Wahrscheinlichkeit ≥ <!--v:param:P-RES-FUTILITY|pct0-->10 %<!--/v-->; der Posterior wird fortgeschrieben, die Schwelle P(S > 0) ≥ <!--v:param:P-RES-FINAL-P|pct0-->80 %<!--/v--> gilt erst im Endtor nach dem Pilot (GATE-G8) |

Die Torlogik ist maschinenlesbar in `research/evidence_gates.json` und wird mit `validation/gate_engine.py` an Beispielfällen geprüft. Ein nicht bestandenes Tor stoppt das Projekt oder verlangt eine signierte Betreiberentscheidung (§16).

## 2 Vorregistrierung und Mehrfachtest-Budget

Vor jeder Ergebnisansicht legt ein Experiment-Manifest fest: Hypothese, Strategie-ID und Parametersatz, Universum je Kapitalstufe, Datenfenster, Kostenszenario, Metriken, Entscheidungsregel, Zufallssamen und Code-Hash (Schema in `schemas/`). Jede Kampagne hat ein Budget von <!--v:param:P-OC-TRIALS|d0-->20<!--/v--> Versuchen; die DSR rechnet mit der Zahl effektiv unabhängiger Versuche (P-OC-NEFF). Nicht registrierte Varianten zählen gegen das Budget, wenn sie angesehen wurden.

## 3 Statistik

- **Deflated Sharpe Ratio** (SRC-LIT-BLP-2014-DSR): korrigiert die Sharpe-Ratio für Auswahl unter mehreren Versuchen, Schiefe und Wölbung. Der Rechner trifft das Quellenbeispiel (<!--v:stat:dsr_source_example/N46|d4-->0,9505<!--/v--> gegenüber <!--v:stat:dsr_source_example/source_value_N46|d4-->0,9505<!--/v-->).
- **PBO mit CSCV** (SRC-LIT-BBLZ-PBO): Anteil der Kombinationen, in denen die beste Konfiguration der Entwicklungshälfte außerhalb unter dem Median liegt. Synthetische Kontrolle: reines Rauschen ergibt <!--v:stat:pbo_cscv_demo/noise_only/pbo|d2-->0,90<!--/v-->, eine echte Strategie unter Rauschen <!--v:stat:pbo_cscv_demo/one_true_strategy/pbo|d2-->0,07<!--/v-->.
- **Reality Check und SPA** (SRC-LIT-WHITE-2000, SRC-LIT-HANSEN-2005) mit stationärem Bootstrap: reines Rauschen ergibt p = <!--v:stat:reality_check_spa_demo/noise_only/p_reality_check|d2-->0,96<!--/v-->, eine echte Strategie p = <!--v:stat:reality_check_spa_demo/one_true_strategy/p_reality_check|d2-->0,03<!--/v--> (Reality Check) bzw. <!--v:stat:reality_check_spa_demo/one_true_strategy/p_spa|d2-->0,04<!--/v--> (SPA).
- **Romano-Wolf-Schrittverfahren** (SRC-LIT-RW-2005) für die Frage, welche einzelnen Konfigurationen signifikant sind.
- **Neue Faktoren ohne Literatur-Prior:** t > <!--v:param:P-RES-T-HURDLE|d1-->3,0<!--/v--> nach Korrektur (SRC-LIT-DECAY-HLZ-2016).
- **ML:** bereinigte Kreuzvalidierung mit Embargo von <!--v:param:P-RES-EMBARGO-H|d0-->168<!--/v--> Stunden (SRC-LIT-LDP-2018).

## 4 Teststärke

Der Standardfehler der Sharpe-Ratio nach Lo (SRC-LIT-LO-2002) schrumpft nur mit der Wurzel der Beobachtungszeit. Für α = <!--v:param:P-RES-ALPHA|d2-->0,05<!--/v--> und Teststärke <!--v:param:P-RES-POWER|pct0-->80 %<!--/v-->:

<!-- GEN:BEGIN tab.power -->
| Netto-Sharpe p. a. | Jahre Daten für α = 5 %, Teststärke 80 % |
|---|---|
| 0,05 | 2.473,0 |
| 0,1 | 618,3 |
| 0,2 | 154,6 |
| 0,3 | 68,7 |
| 0,5 | 24,7 |
| 0,75 | 11,0 |
| 1,0 | 6,2 |
<!-- GEN:END tab.power -->

Folgerung: Mit <!--v:param:P-RES-DEV-YEARS|d0-->8<!--/v--> Entwicklungsjahren sind nur Netto-Sharpe-Ratios nahe eins nachweisbar; eine realistische Kante von <!--v:param:P-RES-SR-USEFUL|d1-->0,3<!--/v--> bräuchte <!--v:stat:years_for_power/0.3|d0-->69<!--/v--> Jahre. Die Tore stützen sich deshalb auf Literatur-Prior plus Posterior-Aktualisierung, nicht auf Signifikanz allein, und die Entscheidungsrechnung rechnet mit einem skeptischen Prior (P-OC-PRIOR-MODE).

## 5 Robustheit

Walk-forward mit festen Neuanpassungsintervallen, Parameternachbarschaft (jede Nachbarkonfiguration im Raster muss dasselbe Vorzeichen zeigen), Teilperioden und Regime (hohe und niedrige Volatilität, Zinsanstieg und -senkung), Kostenszenarien (SZ-KOSTEN_X1_5, SZ-KOSTEN_X2, SZ-KOSTEN_X3) und Kapazität (Marktwirkung bei der Positionsgröße jeder Kapitalstufe, §5.1).

## 6 Daten, Holdout, Forward und Posterior

Entwicklung auf <!--v:param:P-RES-DEV-YEARS|d0-->8<!--/v--> Jahren, danach ein versiegelter Holdout von <!--v:param:P-RES-HOLDOUT-YEARS|d0-->2<!--/v--> Jahren (Hash bei G2, genau eine Öffnung in G4; übernommen aus v2.0). Danach Paper-Forward über <!--v:param:P-RES-PAPER-MONTHS|d0-->6<!--/v--> Monate im Demokonto (G7) und Pilot über <!--v:param:P-RES-PILOT-MONTHS|d0-->6<!--/v--> Monate (G8). Nach jedem Abschnitt wird der Prior der Netto-Sharpe-Ratio mit der beobachteten Sharpe-Ratio und ihrem Standardfehler normal-normal aktualisiert; die Posterior-Wahrscheinlichkeit P(S < 0) speist den Harm-Monitor (P-MON-HARM-SR).

## 7 Futility-Regel (EV-05)

Nach G3 und G4 wird die prädiktive Wahrscheinlichkeit berechnet, das Endtor zu bestehen, gegeben die bisherigen Daten und den Prior. Liegt sie unter <!--v:param:P-RES-FUTILITY|pct0-->10 %<!--/v-->, stoppt das Projekt vor dem Systembau (DEC-DS-21). Die Betriebscharakteristik (Technik übernommen aus v2.0, erweitert um die Futility-Regel) rechnet je <!--v:param:P-RES-OC-STRATEGIES|int-->4.000<!--/v--> Strategien der Klassen schädlich, wertlos und brauchbar mit und ohne Regel; die Tabelle steht in §6.6 des Masterkonzepts. Kernwerte der registrierten Konfiguration: Eine wertlose Strategie erreicht den Systembau in <!--v:oc:registered/WERTLOS/ohne_futility/rates/reached_G5_build|pct2-->0,05 %<!--/v--> der Fälle (Vergleich: <!--v:oc:v2_reference|raw-->v2.0: Strategie ohne Edge bestand E1 und E2 zu etwa 89 % (EV-05)<!--/v-->), eine brauchbare in <!--v:oc:registered/BRAUCHBAR/ohne_futility/rates/reached_G5_build|pct2-->1,40 %<!--/v-->. In der registrierten Konfiguration stoppt die Regel zusätzlich nichts, weil G3 schon über die DSR-Schwelle fast alle Strategien ohne Kante abweist. Bei gelockerter DSR-Schwelle (<!--v:param:P-OC-DSR-SENS/1|d1-->0,5<!--/v-->) wirkt sie vor allem auf brauchbare Strategien: Ihr Anteil am Endtor sinkt von <!--v:ocs:SKEPTISCH/DSR0.5/BRAUCHBAR/ohne_futility/rates/accepted_final|pct1-->9,5 %<!--/v--> auf <!--v:ocs:SKEPTISCH/DSR0.5/BRAUCHBAR/mit_futility/rates/accepted_final|pct1-->6,9 %<!--/v-->; die Kostenersparnis von <!--v:ocs:SKEPTISCH/DSR0.5/BRAUCHBAR/saved_cost_eur_per_strategy|eur-->7.939 EUR<!--/v--> je brauchbarer Strategie ist deshalb kein reiner Gewinn.

## 8 Wissensregister

Jeder Befund wird mit Status (Hypothese, bestätigt, widerlegt), Datenfenster, Gültigkeit und Quelle abgelegt; Hermes darf Einträge vorschlagen, aber nicht als Tatsache markieren (`ai/hermes_integration.md`). Widerlegte Hypothesen bleiben sichtbar, damit sie nicht erneut unbemerkt getestet werden.

## 9 Zeit und Kosten

Die Stufen BS-02 bis BS-04 sind in `implementation/build_stages.json` mit Aufwand geschätzt; kumuliert kostet der Weg bis einschließlich G4 <!--v:calc:spend_to_BS04|eur-->13.700 EUR<!--/v-->. Die Höchstdauer bis G5 beträgt <!--v:param:P-ECO-MAX-MONTHS-G5|d0-->12<!--/v--> Monate (§5.8).
