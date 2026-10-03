# Systementwurf (§10)

> **Betreiberfassung.** Das System besteht aus drei getrennten Bereichen: dem Geldpfad auf deinem Windows-VPS, der Forschungs- und KI-Zone und dem unabhängigen Prüfmodul. Der Geldpfad enthält keinen KI-Agenten, keinen Browser und keinen offenen Fernzugang; die KI-Zone hat keinen Weg zum Broker; das Prüfmodul kann nur stoppen. Alle Entscheidungen sind Ereignisse in einem Journal, sodass jeder Zustand nachgerechnet und jede Abweichung erkannt werden kann. Fällt der Geldpfad aus, schützen die Stopps beim Broker, und eine Ersatzinstanz übernimmt erst nach nachgewiesenem Fencing. Für Go/No-Go heißt das: Die Architektur ist für Demo, Paper und Pilot ausgelegt und bestimmt den Befund nicht. Nächster Schritt: Leistungsdaten des VPS (X-INF-VPS) und die Entscheidung zur Aufteilung (X-INF-ZONES).

## 1 Vertrauensbereiche und Komponenten

| Bereich | Instanz | Komponenten | darf nicht |
|---|---|---|---|
| Geldpfad | Windows-VPS des Betreibers (BQ-07) | Kern (Portfolio-, Risiko-, Ausführungslogik), MT5-Terminal und Adapter, Journal, Guardian (Lease, Heartbeat, Neustartgrenze), Referenzdatendienst (lesend), Betreiber-API und Cockpit-Backend | KI-Agent, Browser, E-Mail, offener RDP-Zugang, Forschungsjobs |
| Forschung und KI | kleine Linux-Instanz | Datenablage mit Hash, Backtest mit dem Produktionskern, Hermes im Container ohne Root, LLM-Gateway, Sandbox ohne Netz | Brokerzugang, Brokercredentials, Holdout, Signaturschlüssel |
| Prüfmodul | kleine Linux-Instanz | unabhängige Nachrechnung von Limits, Positionen und Entscheidungen; Evaluator für Tore mit versiegeltem Holdout; CI | handeln, Orders ändern; Einreichungen außer aus der Forschungszone |
| extern | Kleinstinstanz bei anderem Anbieter | Monitor für Heartbeats aller Instanzen, zwei Alarmkanäle | Schreibrechte irgendwo |

Begründung (DEC-DS-13): Läge der Agent auf dem Geldpfad, kämen Webzugang, Agenten-Terminal und Brokersitzung auf einem System zusammen; läge der Evaluator bei der KI, könnte ein kompromittierter Agent Torergebnisse fälschen (übernommen aus v2.0). Wenn du nur eine Instanz willst (BQ-07, DEC-CF-04), gilt die schwächere Rückfallvariante: getrennte Windows-Benutzer, Firewall-Regeln je Prozess und kein Agent auf dieser Instanz; das Prüfmodul bleibt extern.

## 2 Autoritative Quellen je Zustand (übernommen aus v2.0)

| Zustand | autoritativ | abgeleitet |
|---|---|---|
| Positionen, Orders, Deals, Guthaben, Margin | Broker | Snapshot im Journal mit Alter |
| Absichten, Reservierungen, Sendeversuche, Sperrgründe | Journal | Cockpit, Berichte |
| Grants, Betreiberaktionen | signiertes Grant-Register im Journal | Cockpit |
| Parameter, Regeln, Tore | versionierte Register und Releases | Konfiguration im Kern |
| Forschungs- und Torergebnisse | Evaluator mit signiertem Laufbeleg | Spiegel im Geldpfad, Berichte |
| Projektwissen | Wissensregister | Gedächtnis des Agenten enthält nur Verweise |

Bei Widerspruch zwischen Broker und Journal gilt für Bestände der Broker; der Widerspruch selbst ist ein Sperrgrund.

## 3 Datenfluss

Marktdaten (MT5) → Referenzdatendienst und Kern → Prognosen → Zielpositionen je Strategie → Netting → Pre-Trade-Kontrollen → Journal (fsync) → Adapter → Broker → Abfragen (Polling) → Abgleich → Journal → Cockpit und Berichte. Parallel liest das Prüfmodul Brokerdaten und DecisionRecords und vergleicht. Forschungsdaten liegen in der Forschungszone (nur Entwicklungsjahre) und im Prüfmodul (Holdout versiegelt). Der Agent liest über eine eng begrenzte Projektschnittstelle Gesundheit, Kennzahlen, Incidents und Torergebnisse und schreibt nur Vorschläge, Notizen und Experimente.

## 4 Deterministischer Kern und gleiche Codebasis

Der Kern ist eine reine Funktion aus Ereignissen, Referenzdaten, Parametern und Uhrzeit auf Entscheidungen; Uhr und Adapter werden injiziert. Backtest (Simulationsbroker mit Kostenmodell), Paper (MT5-Demo) und Echtgeld (MT5-Live) unterscheiden sich nur im Adapter und in der Umgebung des Grants. Zufall gibt es im Kern nicht; Simulationen nutzen feste Samen.

## 5 Hochverfügbarkeit, Sicherung und Wiederherstellung

| Komponente | Wiederherstellungspunkt | Wiederherstellungszeit | Verfahren |
|---|---|---|---|
| Journal | <!--v:param:P-OPS-RPO-JOURNAL-MIN|d0-->5<!--/v--> Minuten (verschlüsselte Offsite-Kopie) | <!--v:param:P-OPS-RTO-CORE-H|d0-->4<!--/v--> Stunden | Restore auf Ersatzinstanz, Fencing, Abgleich (RB-16, RB-17) |
| Kernprozess | – | <!--v:param:P-OPS-RESTART-S|d0-->120<!--/v--> Sekunden (Neustart mit Abgleich) | Guardian, höchstens <!--v:param:P-OPS-RESTART-MAX-N|d0-->3<!--/v--> Neustarts in <!--v:param:P-OPS-RESTART-WINDOW-MIN|d0-->15<!--/v--> Minuten, dann Eskalation |
| MT5-Terminal | – | Minuten | Neustart durch den Guardian; Deals seit Cursor nachziehen (RB-02) |
| Forschungszone | täglich | Tage | Neuaufbau aus Release und Datenmanifest |
| Prüfmodul | täglich | ein Arbeitstag | Neuaufbau; ohne Prüfung keine Einstiege |

Aufbewahrt werden <!--v:param:P-OPS-BACKUP-DAILY|d0-->14<!--/v--> tägliche und <!--v:param:P-OPS-BACKUP-WEEKLY|d0-->8<!--/v--> wöchentliche Sicherungen; Restoreprobe alle <!--v:param:P-OPS-RESTORE-DRILL-D|d0-->30<!--/v--> Tage (DR-01). Aktiv-Passiv: Die Ersatzinstanz ist kalt; sie wird erst Writer, wenn die Anmeldung der alten Instanz nach dem Wechsel des Hauptpassworts nachweislich abgewiesen wird. Ohne gültige Lease (<!--v:param:P-EXE-LEASE-S|d0-->15<!--/v--> Sekunden) sendet der Kern nichts. Alle Instanzen und Sicherungen liegen in der EU.

## 6 Beobachtbarkeit

- **Metriken:** Heartbeat alle <!--v:param:P-OPS-HEARTBEAT-S|d0-->5<!--/v--> Sekunden, kritisch nach <!--v:param:P-OPS-HEARTBEAT-CRIT-S|d0-->15<!--/v--> Sekunden; Latenzen, Abfragedauer, Snapshot-Alter, UNKNOWN-Zahl, Tagesverlust, Lückenstress, M/E, L_g, Kostenverhältnis.
- **Logs:** strukturiert, mit Korrelationskennung von der Absicht bis zum Deal; keine Secrets (Secret-Scan).
- **Traces:** je Parent-Order der Weg durch Kontrollen, Journal, Adapter und Abfragen.
- **Uhr und Platte:** Warnung bei Uhrabweichung ab <!--v:param:P-OPS-CLOCK-WARN-S|d0-->1<!--/v--> Sekunde, Einstiegssperre ab <!--v:param:P-OPS-CLOCK-BLOCK-S|d0-->2<!--/v--> Sekunden; Plattenstufen P-OPS-DISK-LEVELS.
- **Alarme:** zwei unabhängige Kanäle über den externen Monitor, täglicher Testalarm mit Quittung binnen <!--v:param:P-OPS-ALERT-ACK-H|d0-->12<!--/v--> Stunden (übernommen aus v2.0).

## 7 Cockpit und Bedienung

| Ansicht | Inhalt | Rechte |
|---|---|---|
| Übersicht | Modus (Paper oder Echtgeld, farblich und textlich), Grant, Sicherheitszustand, NAV, Tagesverlust, Leiterstufe | lesen |
| Risiko | L_g, L_n je Klasse, σ_p, ES, Lückenstress, M/E, Limits mit Auslastung | lesen |
| Positionen und Orders | Brokerposition und Teilpositionen je Strategie, offene Orders, UNKNOWN | lesen |
| Incidents | offene Incidents, Runbook-Verweis, Zeitlinie | lesen, quittieren (signiert) |
| Freigaben | Releases, Parameteränderungen, Profilaufstiege, Grants | Betreiber signiert; Klassen C und D zusätzlich zweite Person |
| mobile Notfallansicht | Übersicht, Pause, Kill-Switch, Abbau | nur risikomindernde Aktionen, signiert |

Paper und Echtgeld laufen in getrennten Instanzen mit getrennten Adressen; jede Ansicht trägt den Modus im Kopf. Den Moduswechsel kann nur der Betreiber signieren (BQ-09).

## 8 Zustandsautomaten und Szenarien

Jeder geldwirksame Zustand gehört genau einem Automaten in `architecture/state_machines.json` (führende Quelle); Zustände, die der Broker kennt, tragen ihr Brokerfeld (`broker_fact_target`). Der Sicherheitszustand ist kein einfacher Automat, sondern ein Verband aus Sperrgründen (SM-SAFETY): Jeder aktive Grund nimmt Aktionen weg, erlaubt bleibt die Schnittmenge, und die Schutzbasis (Abgleich, Notfallschutz, Rollen als Schließen, Stornieren) bleibt außer beim Start immer erhalten. `validation/state_engine.py` prüft alle Automaten an <!--v:calc:traces_total|int-->67<!--/v--> Traces, für den Verband alle <!--v:calc:lattice_combinations|int-->64<!--/v--> Kombinationen der Stufen, und gleicht die Betreiberaktionen mit dem Vertrag `operator_action` ab.

<!-- GEN:BEGIN tab.machines -->
| ID | Automat | Frage | Zustände | Übergänge bzw. Gründe | Traces |
|---|---|---|---|---|---|
| SM-MODE | Betriebsmodus (Demo/Echtgeld nach BQ-09) | In welchem Modus arbeitet das System, und wer darf ihn ändern? | 6 | 11 Übergänge | 3 |
| SM-SAFETY | Kontosicherheitszustand (Sperrgrund-Verband) | Was ist jetzt auf diesem Konto erlaubt? | 7 | 35 Sperrgründe, 7 Stufen | 12 |
| SM-ORDER | Sendeversuch (OrderAttempt) über die MT5-Python-Schnittstelle | Was ist mit genau diesem Auftrag beim Broker geschehen? | 16 | 53 Übergänge | 15 |
| SM-POSITION | Brokerposition je Instrument (Hedging-Konto mit interner Nettung) | Ist die Brokerposition dieses Instruments bekannt, geschützt und mit den Teilpositionen der Strategien stimmig? | 8 | 26 Übergänge | 9 |
| SM-LEVERAGE | Hebelprofil und Stufenleiter (§7.3, §7.8) | Welches Hebelprofil gilt jetzt, und darf es sich ändern? | 7 | 13 Übergänge | 3 |
| SM-WRITER | Einziger Writer und Fencing (MT5) | Darf genau diese Instanz jetzt an den Broker senden? | 6 | 9 Übergänge | 2 |
| SM-GRANT | Grant (PAPER, PILOT, STANDARD) | Ist diese Handelsfreigabe gültig? | 8 | 11 Übergänge | 5 |
| SM-DATAFEED | Datenzustand je Instrument | Darf dieses Instrument jetzt mit diesen Daten gehandelt werden? | 9 | 16 Übergänge | 4 |
| SM-GATERUN | Torauswertung im Prüfmodul | Ist dieses Torergebnis gültig, unverändert und signiert? | 7 | 7 Übergänge | 1 |
| SM-INCIDENT | Incident | Ist dieser Vorfall erkannt, eingedämmt, verstanden und abgeschlossen? | 5 | 6 Übergänge | 1 |
| SM-RELEASE | Release und Änderungsklassen | Darf dieses Artefakt aktiviert werden, und wie wird es zurückgenommen? | 11 | 13 Übergänge | 4 |
| SM-HERMES | Dienstzustand des KI-Agenten (Hermes) | Arbeitet der Agent, und darf er weiterarbeiten? | 6 | 10 Übergänge | 1 |
| SM-MLMODEL | Lebenszyklus einer ML-Komponente (MRM) | Darf diese ML-Komponente Größen oder Regime beeinflussen? | 10 | 13 Übergänge | 4 |
| SM-WORKITEM | Arbeitsauftrag (Agent und Betreiber) | Wer arbeitet woran, mit welchem Budget, und wer prüft? | 12 | 14 Übergänge | 3 |
<!-- GEN:END tab.machines -->

Kritische Abläufe mit erwarteter und verbotener Wirkung, Erkennung, Wiederaufnahme und Abnahme stehen in `architecture/scenario_catalog.json` (<!--v:calc:scenarios_total|int-->81<!--/v--> Szenarien, darunter die Szenarien S01–S21 und N01–N18 übernommen aus v2.0, soweit auf MT5 übertragbar). Szenarien mit Trace sind im Paket geprüft, Stressszenarien im Stressmotor je Profil gerechnet; die übrigen sind spezifiziert und werden mit den genannten Tests im Bau abgenommen.

<!-- GEN:BEGIN tab.scenarios_summary -->
| Kategorie | Szenarien | im Paket geprüft oder gerechnet | spezifiziert | Beispiele |
|---|---|---|---|---|
| AUSFUEHRUNG | 13 | 12 | 1 | OS-EX-01 Einstieg ausgeführt, Antwort geht verloren; OS-EX-02 Teilausführung, Stornierung und restliche Ausführung konkurrieren |
| RISIKO | 14 | 10 | 4 | OS-RI-01 Kleinste Menge überschreitet das Risikobudget; OS-RI-02 Tagesverlust-Leiter L2 |
| GOVERNANCE | 14 | 11 | 3 | OS-GV-01 Verwechslung Demo und Echtgeld; OS-GV-02 Grant läuft bei offenen Positionen ab |
| DATEN | 3 | 2 | 1 | OS-DA-01 Veraltete Kurse oder abweichende Quellen; OS-DA-02 Lücken im Kursstrom |
| BETRIEB | 16 | 7 | 9 | HA-VPS-DOWN Geldpfad-Instanz ausgefallen; HA-RESTART-LIMIT Neustartgrenze erreicht |
| STRESS | 21 | 21 | 0 | SC-H-1987 Aktiencrash 19.10.1987; SC-H-1994 Anleihecrash 1994 |
<!-- GEN:END tab.scenarios_summary -->
