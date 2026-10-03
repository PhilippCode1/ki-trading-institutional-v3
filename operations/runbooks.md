# Runbooks (§14.1)

> **Betreiberfassung.** Für jede Störung, die das Paket kennt – alle Stressszenarien, alle Killer-Tests, alle Ausfälle der Infrastruktur – gibt es ein Runbook mit Auslöser, Schritten und Abschlusskriterium. Das System führt die automatischen Schritte selbst aus (Sperren, Leitern, Kill-Switch); du führst die Schritte aus, die eine Entscheidung brauchen. Die Zuordnung ist maschinell geprüft: Kein Szenario und kein Killer-Test bleibt ohne Runbook. Die wichtigsten Runbooks werden regelmäßig geprobt (`operations/drills.md`). Für Go/No-Go heißt das: Der Betrieb ist für bekannte Störungen vorbereitet; die Wirksamkeit belegen erst die Drills. Nächster Schritt: Drills im Demokonto nach dem Systembau (G6).

Quelle: `operations/runbook_register.json` (<!--v:calc:runbooks_total|int-->35<!--/v--> Runbooks). Parameterwerte stehen in Klammern hinter der Kennung.

## Übersicht

<!-- GEN:BEGIN tab.runbooks -->
| ID | Runbook | Schwere | Auslöser (Szenario, Killer-Test, HA) | Sperrgründe | Drills |
|---|---|---|---|---|---|
| RB-01 | Geldpfad-Instanz ausgefallen oder startet nicht | KRITISCH | HA-VPS-DOWN, HA-RESTART-LIMIT | BOOT, SYNC_REQUIRED, GUARDIAN_LEASE_EXPIRED | DR-01, DR-02 |
| RB-02 | MT5-Terminal oder Brokersitzung getrennt | HOCH | KT-12, HA-SESSION-LOST | BROKER_SESSION_DOWN, SNAPSHOT_STALE | DR-10 |
| RB-03 | Schutzstopp fehlt oder ist unbestätigt | KRITISCH | KT-06, KT-07 | STOP_MISSING | DR-10 |
| RB-04 | Journal nicht beschreibbar | KRITISCH | HA-JOURNAL | JOURNAL_WRITE_FAILURE | DR-02 |
| RB-05 | UNKNOWN-Klärung | HOCH | KT-04, KT-05 | UNKNOWN_ORDER | DR-10 |
| RB-06 | Fremde Position, fremde Order oder Stornierung durch die Börse | HOCH | SC-H-2022NI | FOREIGN_POSITION | – |
| RB-07 | Tagesverlust-Leiter ausgelöst oder Tagesgrenze erreicht | HOCH | SC-X-GAP5, SC-X-GAP10 | DAILY_LOSS_PAUSE, DAILY_LOSS_EXIT, DAILY_LOSS_CAP_BREACH | DR-05 |
| RB-08 | Drawdown-Leiter und Wochenverlust | HOCH | – | DRAWDOWN_REVIEW, DRAWDOWN_EXIT, WEEKLY_LOSS_PAUSE | – |
| RB-09 | Alarmkanal ausgefallen | MITTEL | HA-ALERT | ALERT_CHANNEL_DOWN | DR-08 |
| RB-10 | Uhrabweichung oder Plattenbelegung | MITTEL | HA-CLOCK, HA-DISK | CLOCK_DRIFT, DISK_HIGH | – |
| RB-11 | KI-Zone oder Evaluator ausgefallen, KI-Kontingent erschöpft | NIEDRIG | HA-AI-DOWN, HA-EVALUATOR-DOWN | AUDIT_NOT_RUN | – |
| RB-12 | KI-Agent isolieren (Kompromittierungsverdacht) | KRITISCH | HA-AI-COMPROMISE | – | DR-07 |
| RB-13 | Kompromittierung der Geldpfad-Instanz oder des Brokerkontos | KRITISCH | HA-COMPROMISE | CREDENTIAL_SUSPECT, INTEGRITY_ERROR | DR-06 |
| RB-14 | Daten verspätet, ungültig oder revidiert | MITTEL | SC-X-DATA | MARKET_DATA_DOWN | DR-04 |
| RB-15 | Kombinationsausfall und Brokerdirektkontrolle | KRITISCH | HA-COMBINED | – | DR-03 |
| RB-16 | Restore aus Sicherung | HOCH | HA-RESTORE | RESTORED_FROM_BACKUP | DR-01 |
| RB-17 | Credential-Rotation und Fencing-Nachweis | HOCH | KT-16, HA-FENCING | WRITER_NOT_FENCED | DR-09 |
| RB-18 | Rollfenster, Verfall und Liefervermeidung | MITTEL | KT-11 | – | – |
| RB-19 | Grant: Ablauf, Widerruf, Schlüsselverlust | HOCH | – | GRANT_MISSING_OR_EXPIRED, GRANT_LOSS_LIMIT_REACHED | DR-06 |
| RB-20 | Release aktivieren und zurücknehmen | MITTEL | – | – | – |
| RB-21 | Unabhängige Prüfung meldet Abweichung | HOCH | – | DECISION_AUDIT_MISMATCH | – |
| RB-22 | Geordneter Abbau und Projektende | MITTEL | – | MODE_WIND_DOWN | – |
| RB-23 | Angekündigter Betreibereingriff | MITTEL | – | MANUAL_INTERVENTION | – |
| RB-24 | Margin-Erhöhung, Margin-Defizit, Liquidationswarnung | HOCH | SC-H-2008, SC-H-2020, SC-H-2022GILT, KT-13 | MARGIN_DEFICIT | DR-05 |
| RB-25 | Kurslücke, Limit-Move oder Handelsaussetzung | HOCH | SC-H-1987, SC-H-2010, SC-H-2015, SC-H-2018, SC-H-2022NI, SC-H-2025, SC-X-GAP5, SC-X-GAP10, KT-08, KT-10 | – | – |
| RB-26 | Negativer Preis oder auslaufender Energiekontrakt | HOCH | SC-H-2020WTI | – | – |
| RB-27 | Brokerausfall oder Insolvenzverdacht | KRITISCH | SC-X-BROKER, SC-H-2023 | – | DR-03 |
| RB-28 | Börsenausfall | HOCH | SC-X-EXCH | – | – |
| RB-29 | Liquiditätsausfall oder Korrelationsschock | HOCH | SC-H-1998, SC-H-2008, SC-H-2020, SC-X-CORR1, SC-X-LIQ, SC-H-1987, SC-H-2025 | – | – |
| RB-30 | Zinsschock und Anleihestress | HOCH | SC-H-1994, SC-H-2022GILT, SC-H-2023, SC-X-RATESHOCK | – | – |
| RB-31 | Killer-Test gescheitert | HOCH | KT-01, KT-02, KT-03, KT-04, KT-05, KT-06, KT-07, KT-08, KT-09, KT-10, KT-11, KT-12, KT-13, KT-14, KT-15, KT-16 | – | – |
| RB-32 | Kostendrift ausgelöst | MITTEL | – | – | – |
| RB-33 | Verwechslung Demo und Echtgeld | KRITISCH | KT-16 | MODE_MISMATCH | DR-08 |
| RB-34 | Kill-Switch oder Pause ausgelöst | HOCH | HA-KILL | KILL_SWITCH, KILL_SWITCH_EXIT, OPERATOR_PAUSE | DR-10 |
| RB-35 | Betreiber nicht erreichbar | HOCH | HA-OPERATOR-ABSENT | OPERATOR_ABSENT | – |
<!-- GEN:END tab.runbooks -->

## Abdeckung

<!-- GEN:BEGIN tab.runbook_coverage -->
| Szenario oder Killer-Test | Runbooks |
|---|---|
| SC-H-1987 | RB-25, RB-29 |
| SC-H-1994 | RB-30 |
| SC-H-1998 | RB-29 |
| SC-H-2008 | RB-24, RB-29 |
| SC-H-2010 | RB-25 |
| SC-H-2015 | RB-25 |
| SC-H-2018 | RB-25 |
| SC-H-2020 | RB-24, RB-29 |
| SC-H-2020WTI | RB-26 |
| SC-H-2022NI | RB-06, RB-25 |
| SC-H-2022GILT | RB-24, RB-30 |
| SC-H-2023 | RB-27, RB-30 |
| SC-H-2025 | RB-25, RB-29 |
| SC-X-CORR1 | RB-29 |
| SC-X-LIQ | RB-29 |
| SC-X-BROKER | RB-27 |
| SC-X-EXCH | RB-28 |
| SC-X-DATA | RB-14 |
| SC-X-GAP5 | RB-07, RB-25 |
| SC-X-GAP10 | RB-07, RB-25 |
| SC-X-RATESHOCK | RB-30 |
| KT-01 | RB-31 |
| KT-02 | RB-31 |
| KT-03 | RB-31 |
| KT-04 | RB-05, RB-31 |
| KT-05 | RB-05, RB-31 |
| KT-06 | RB-03, RB-31 |
| KT-07 | RB-03, RB-31 |
| KT-08 | RB-25, RB-31 |
| KT-09 | RB-31 |
| KT-10 | RB-25, RB-31 |
| KT-11 | RB-18, RB-31 |
| KT-12 | RB-02, RB-31 |
| KT-13 | RB-24, RB-31 |
| KT-14 | RB-31 |
| KT-15 | RB-31 |
| KT-16 | RB-17, RB-31, RB-33 |
<!-- GEN:END tab.runbook_coverage -->

## Runbooks im Einzelnen

<!-- GEN:BEGIN gen.runbooks -->
### RB-01 Geldpfad-Instanz ausgefallen oder startet nicht

**Schwere:** KRITISCH · **Auslöser:** Heartbeat fehlt länger als P-OPS-HEARTBEAT-CRIT-S (15 Sekunden); Neustartgrenze erreicht

1. Externer Monitor alarmiert über beide Kanäle; offene Positionen sind durch Stopps beim Broker geschützt.
2. Betreiber prüft im Broker-Webterminal oder mobilen MT5-Zugang Positionen und Stopps (nur lesend, keine Eingriffe ohne RB-23).
3. Neustart der Instanz; der Kern startet in BOOTING, dann SYNCING mit Vollabgleich.
4. Scheitert der Neustart binnen P-OPS-RTO-CORE-H (4 Stunden): Restore auf Ersatzinstanz nach RB-16 mit Fencing nach RB-17.
5. Incident mit Zeitlinie und Ursache; Post-Mortem nach operations/operations_plan.md.

**Abschluss:** Kern in READY oder ENTRY_PAUSED mit konsistentem Snapshot; Incident geschlossen.

### RB-02 MT5-Terminal oder Brokersitzung getrennt

**Schwere:** HOCH · **Auslöser:** Adapter meldet IPC- oder Sitzungsfehler; Abfragen scheitern

1. Einstiegssperre (BROKER_SESSION_DOWN); Schutz liegt beim Broker.
2. Terminal-Neustart durch den Guardian; Anmeldung prüfen.
3. Nach Wiederverbindung Deals seit dem Cursor nachziehen (KT-12) und Vollabgleich.
4. Offene Versuche ohne Antwort als UNKNOWN nach RB-05 klären.

**Abschluss:** Sitzung fünf Minuten stabil, Abgleich konsistent.

### RB-03 Schutzstopp fehlt oder ist unbestätigt

**Schwere:** KRITISCH · **Auslöser:** Position ohne bestätigten SL nach P-EXE-STOP-CONFIRM-S (30 Sekunden)

1. Genau ein Schutzversuch je Brokerrevision (SL setzen oder anpassen).
2. Scheitert er: Position über `position=Ticket` schließen.
3. Sperrgrund STOP_MISSING bis zur Quittung des Betreibers; Incident.

**Abschluss:** Jede offene Position hat einen bestätigten SL über die volle Menge.

### RB-04 Journal nicht beschreibbar

**Schwere:** KRITISCH · **Auslöser:** Schreibfehler oder fsync-Fehler im Journal

1. Kein Senden neuer Orders; Wechsel auf das Notfalljournal.
2. Nur Schutzaktionen mit Snapshot jünger als P-EXE-SNAPSHOT-MAX-S (60 Sekunden).
3. Scheitert auch das Notfalljournal: Fail-Stop; Neustart in BOOTING mit Integritätsprüfung.
4. Nach Wiederherstellung Notfallaktionen rekonstruieren und kennzeichnen.

**Abschluss:** Journal beschreibbar, Integritätsprüfung bestanden, Betreiberfreigabe.

### RB-05 UNKNOWN-Klärung

**Schwere:** HOCH · **Auslöser:** Sendeversuch ohne eindeutige Antwort (Zeitüberschreitung, IPC-Fehler)

1. Reservierung und Einstiegssperre des Instruments bleiben.
2. Abfragen nach P-EXE-UNKNOWN-POLL-S ([5; 15; 60] Sekunden), danach im Intervall P-EXE-UNKNOWN-POLL-LATER-S (300 Sekunden).
3. Negativnachweis nur nach Ablauf der Gültigkeit und P-EXE-NEGPROOF-CYCLES (2 Anzahl) sauberen Abfragezyklen.
4. Nach P-EXE-UNKNOWN-MAX-H (24 Stunden) Eskalation an den Betreiber; nie erneut senden.

**Abschluss:** Alle UNKNOWN geklärt (FILLED, CANCELLED, EXPIRED oder NOT_EXECUTED_PROVEN).

### RB-06 Fremde Position, fremde Order oder Stornierung durch die Börse

**Schwere:** HOCH · **Auslöser:** Abgleich findet unbekannte Bestände oder stornierte Deals

1. Sperrgrund FOREIGN_POSITION; das System schließt nie still.
2. Betreiber prüft Herkunft (eigener Eingriff, Broker, Börsenstornierung).
3. Stornierte Deals der Börse als Korrektur verbuchen; P&L und Risiko neu.
4. Freigabe nur mit signierter Quittung.

**Abschluss:** Bestände erklärt und abgeglichen.

### RB-07 Tagesverlust-Leiter ausgelöst oder Tagesgrenze erreicht

**Schwere:** HOCH · **Auslöser:** Tagesverlust erreicht P-RISK-DL-L1 (0,03 Anteil NAV), P-RISK-DL-L2 (0,05 Anteil NAV), P-RISK-DL-L3 (0,065 Anteil NAV) oder P-OP-DAILY-LOSS-CAP (0,09 Anteil NAV)

1. L1: Risikoziel halbieren (automatisch).
2. L2: Einstiegssperre (automatisch); Betreiber informiert.
3. L3: geordneter Abbau über Child-Orders (automatisch).
4. Grenze erreicht: schwerer Incident, Ursachenbericht, neuer Grant nötig (RK-29).

**Abschluss:** Nächster Handelstag oder signierte Wiederaufnahme nach Ursachenbericht.

### RB-08 Drawdown-Leiter und Wochenverlust

**Schwere:** HOCH · **Auslöser:** Drawdown vom Höchststand oder Wochenverlust über Schwelle

1. Stufe je P-RISK-DD-L1 (0,10 Anteil NAV) bis P-RISK-DD-KILL (0,30 Anteil NAV) anwenden (automatisch).
2. Profilabstieg nach §7.8 (automatisch).
3. Ab Stufe 3 Betreiberprüfung; ab Stopp neuer Grant.

**Abschluss:** Signierte Entscheidung des Betreibers; bei Stopp neuer Grant.

### RB-09 Alarmkanal ausgefallen

**Schwere:** MITTEL · **Auslöser:** Testalarm nicht quittiert oder Kanal länger als P-OPS-ALERT-DOWN-H (24 Stunden) gestört

1. Zweiten Kanal prüfen; Einstiegssperre nach P-OPS-ALERT-DOWN-H (24 Stunden), sofort wenn beide ausfallen.
2. Kanal reparieren, Testalarm quittieren.

**Abschluss:** Beide Kanäle quittiert.

### RB-10 Uhrabweichung oder Plattenbelegung

**Schwere:** MITTEL · **Auslöser:** Uhr über P-OPS-CLOCK-WARN-S (1 Sekunden) oder Platte über den Stufen P-OPS-DISK-LEVELS ([0,75; 0,85; 0,90] Anteile)

1. Warnung; ab P-OPS-CLOCK-BLOCK-S (2 Sekunden) bzw. oberster Plattenstufe Einstiegssperre.
2. NTP prüfen, Platz schaffen (Nebenaufgaben stoppen, alte Sicherungen verschieben).

**Abschluss:** Werte fünf Minuten im Normalbereich.

### RB-11 KI-Zone oder Evaluator ausgefallen, KI-Kontingent erschöpft

**Schwere:** NIEDRIG · **Auslöser:** Heartbeat der KI- oder Prüfinstanz fehlt; Abo-Kontingent verbraucht

1. Geldpfad unberührt; ohne Evaluator keine neuen Torergebnisse und keine Einstiege, wenn die tägliche Prüfung ausfällt (AUDIT_NOT_RUN).
2. KI-Aufgaben pausieren (SM-HERMES PAUSED_BUDGET oder OFFLINE); System läuft in Stufe H0.

**Abschluss:** Instanzen wieder verfügbar; Prüfung nachgeholt.

### RB-12 KI-Agent isolieren (Kompromittierungsverdacht)

**Schwere:** KRITISCH · **Auslöser:** Kanarientreffer am Gateway, unerwartete Werkzeugnutzung, Egress-Verstoß

1. Binnen P-OPS-ISOLATE-MIN (15 Minuten): Netz der KI-Zone trennen, Tokens widerrufen, Projektschnittstelle sperren.
2. Spuren sichern; Geldpfad bleibt unberührt.
3. Rückkehr nur über saubere, signierte Neuinstallation und bestandene Evaluationssuite.

**Abschluss:** Neuinstallation abgenommen; Incident geschlossen.

### RB-13 Kompromittierung der Geldpfad-Instanz oder des Brokerkontos

**Schwere:** KRITISCH · **Auslöser:** Unerwartete Anmeldung, fremde Orders, Secret im Log, Brokerwarnung

1. Kill-Switch Stufe 1; Broker telefonisch sperren lassen, falls Fremdaktivität.
2. Hauptpasswort ändern (Fencing), alle Credentials rotieren (RB-17).
3. Instanz vom Netz, forensische Kopie; Neuaufbau aus signiertem Release.
4. Meldungen an Broker und externe Person (BQ-03).

**Abschluss:** Neuaufbau abgenommen, Credentials rotiert, Ursache geklärt.

### RB-14 Daten verspätet, ungültig oder revidiert

**Schwere:** MITTEL · **Auslöser:** Kurse älter als P-DATA-STALE-S (10 Sekunden), Lücken, Revisionen, Datenausfall

1. Datenzustand DEGRADED; Einstiegssperre für betroffene Instrumente.
2. Schutzstopps beim Broker bleiben aktiv; keine neuen Orders ohne Daten.
3. Revisionen nur im Revisionsfenster übernehmen; sonst neue Version mit Begründung.

**Abschluss:** Daten fünf Minuten gesund; Abgleich bestanden.

### RB-15 Kombinationsausfall und Brokerdirektkontrolle

**Schwere:** KRITISCH · **Auslöser:** Geldpfad und Monitor gleichzeitig ohne Verbindung

1. Betreiber nutzt den eigenen Zugang des Brokers (Web oder mobil), nie den Systembenutzer.
2. Nur schützen oder abbauen; jede Aktion notieren.
3. Nach Rückkehr des Systems: angekündigter Eingriff nach RB-23, Vollabgleich.

**Abschluss:** System wieder führend; Eingriffe abgeglichen.

### RB-16 Restore aus Sicherung

**Schwere:** HOCH · **Auslöser:** Totalverlust der Geldpfad-Instanz oder Datenkorruption

1. Ersatzinstanz aus signiertem Release aufsetzen.
2. Journal aus der jüngsten Offsite-Kopie (höchstens P-OPS-RPO-JOURNAL-MIN (5 Minuten) alt) wiederherstellen.
3. Start mit RESTORED_FROM_BACKUP und SYNC_REQUIRED, nur lesend; Grants sind ungültig.
4. Fencing nach RB-17; neuer Grant nach Prüfung.

**Abschluss:** Abgleich konsistent, Fencing belegt, neuer Grant.

### RB-17 Credential-Rotation und Fencing-Nachweis

**Schwere:** HOCH · **Auslöser:** Host-Wechsel, Restore, Verdacht, Ablauf von P-SEC-CRED-ROTATION-D (90 Tage)

1. Hauptpasswort des MT5-Kontos ändern; alte Instanz muss abgewiesen werden (Nachweis, KT-16).
2. Dienst-Credentials und Token rotieren.
3. Erst danach wird die neue Instanz Writer (SM-WRITER).

**Abschluss:** Ablehnungsnachweis der alten Anmeldung im Journal.

### RB-18 Rollfenster, Verfall und Liefervermeidung

**Schwere:** MITTEL · **Auslöser:** Kontrakt erreicht das Rollfenster P-UNI-ROLL-DAYS (5 Geschäftstage) oder die Energie-Sonderregel

1. Keine neuen Einstiege; offene Positionen schließen (ROLL_AS_CLOSE).
2. Scheitert das Schließen: Eskalation an den Betreiber vor der Brokerglattstellung.
3. Phase CLOSEONLY beim Broker mit Kalender abgleichen (KT-11).

**Abschluss:** Keine Position im Liefer- oder Verfallsfenster.

### RB-19 Grant: Ablauf, Widerruf, Schlüsselverlust

**Schwere:** HOCH · **Auslöser:** Grant läuft ab, wird widerrufen oder der Signaturschlüssel ist verloren

1. Ohne Grant gilt EXIT_ONLY: keine neue Exposure, Schutz läuft weiter.
2. Schlüsselverlust: alle Grants widerrufen, Ersatzschlüssel aus der Hinterlegung (security/key_management.md).

**Abschluss:** Neuer Grant mit Risikoakzeptanz oder geordneter Abbau.

### RB-20 Release aktivieren und zurücknehmen

**Schwere:** MITTEL · **Auslöser:** Freigegebenes Release oder Fehler nach Aktivierung

1. Aktivierung nur ohne UNKNOWN und außerhalb des Einstiegsfensters; Klassen C und D nur bei flachem Konto.
2. Beobachtungsphase; bei Fehler Rücknahme auf das vorige signierte Release.
3. Releasewechsel invalidiert Grants (neuer Grant).

**Abschluss:** Release stabil oder zurückgenommen.

### RB-21 Unabhängige Prüfung meldet Abweichung

**Schwere:** HOCH · **Auslöser:** Prüfmodul weicht von Entscheidungen oder Limits des Kerns ab

1. Sperrgrund DECISION_AUDIT_MISMATCH (verriegelt); Einstiegssperre.
2. Ursache klären: Kern, Prüfmodul oder Daten.
3. Freigabe nur nach geschlossenem Incident.

**Abschluss:** Abweichung erklärt und behoben.

### RB-22 Geordneter Abbau und Projektende

**Schwere:** MITTEL · **Auslöser:** Abbruchkriterium §5.8, Betreiberentscheidung oder Kill-Stufe der Drawdown-Leiter

1. Modus WIND_DOWN: keine neuen Einstiege, Abbau über Child-Orders im Liquiditätsfenster.
2. Nach flachem Konto: Grants widerrufen, Daten archivieren, Bericht.

**Abschluss:** Konto flach, Bericht abgelegt.

### RB-23 Angekündigter Betreibereingriff

**Schwere:** MITTEL · **Auslöser:** Betreiber will selbst über den Broker eingreifen

1. Eingriff vorher signiert ankündigen (Sperrgrund MANUAL_INTERVENTION).
2. Eingriff nur mit eigenem Zugang, nie mit dem Systembenutzer.
3. Danach Vollabgleich und Quittung.

**Abschluss:** Abgleich konsistent, Quittung signiert.

### RB-24 Margin-Erhöhung, Margin-Defizit, Liquidationswarnung

**Schwere:** HOCH · **Auslöser:** Börse oder Broker erhöhen Margins; Margin-Level unter P-MRG-DERISK-TRIGGER (1,50 Anteil der Initial-Margin)

1. Größen mit neuer Margin rechnen; Abbau, bis das Margin-Level wieder über der Schwelle liegt.
2. Ist Abbau unmöglich (Limit, Aussetzung): Nachschussbedarf melden; nur der Betreiber überweist.
3. Sperrgrund MARGIN_DEFICIT bis zur Quittung.

**Abschluss:** Margin-Level über der Schwelle; Quittung.

### RB-25 Kurslücke, Limit-Move oder Handelsaussetzung

**Schwere:** HOCH · **Auslöser:** Bewegung über k·σ_Tag, Tageslimit erreicht, Aussetzung

1. Keine Panikorders; Stopps können im gesperrten Markt nicht ausführen (KT-10).
2. Tagesverlust-Leiter wirkt automatisch; bei Wiedereröffnung Abbau nach Leiterstufe.
3. Stornierungen der Börse nach RB-06 verbuchen.

**Abschluss:** Markt wieder offen, Positionen innerhalb der Grenzen.

### RB-26 Negativer Preis oder auslaufender Energiekontrakt

**Schwere:** HOCH · **Auslöser:** Frontmonat Energie nahe LTD; Preis unter null

1. Energie-Frontmonate P-UNI-ENERGY-EXPIRY-DAYS (7 Geschäftstage) Geschäftstage vor LTD nicht halten (Regel verhindert den Fall).
2. Preisprüfung akzeptiert negative Preise; Abbau über `position=Ticket`.

**Abschluss:** Keine Position im auslaufenden Energiekontrakt.

### RB-27 Brokerausfall oder Insolvenzverdacht

**Schwere:** KRITISCH · **Auslöser:** Broker nicht erreichbar über längere Zeit; Meldungen zur Solvenz

1. Keine neuen Einstiege; Brokerdirektkontrolle nach RB-15.
2. Nur das Brokerguthaben (P-ECO-CASH-AT-BROKER (0,25 Anteil)) ist exponiert; kein Nachschuss.
3. Zweitbroker nur nach neuer Testrunde (KT-01 bis KT-16).

**Abschluss:** Broker wieder erreichbar oder Konto aufgelöst.

### RB-28 Börsenausfall

**Schwere:** HOCH · **Auslöser:** Größte Börse des Portfolios handelt nicht

1. Positionen dieser Börse eingefroren; Einstiege dort gesperrt.
2. Lückenregel rechnet Wiedereröffnung mit P-GAP-K-HYP-LOW (5 σ (Tag)) σ; übrige Börsen normal.

**Abschluss:** Börse wieder offen, Abgleich konsistent.

### RB-29 Liquiditätsausfall oder Korrelationsschock

**Schwere:** HOCH · **Auslöser:** Spreads über dem Mehrfachen des Modells, Korrelationen gegen eins

1. Einstiege sperren; Abbau nur im Liquiditätsfenster und mit Child-Orders.
2. Kostendrift-Überwachung und Risiko neu rechnen.

**Abschluss:** Spreads im Modellband.

### RB-30 Zinsschock und Anleihestress

**Schwere:** HOCH · **Auslöser:** Starke Zinsbewegung, Anleihecrash, Gilt-Krise, Bankenstress

1. Zinsallokation prüfen; Lückenregel und Leiter wirken.
2. Margin-Mitteilungen der Börsen beobachten (RB-24).

**Abschluss:** Allokation innerhalb der Grenzen.

### RB-31 Killer-Test gescheitert

**Schwere:** HOCH · **Auslöser:** Ein Killer-Test besteht nicht

1. Rückfallvariante laut execution/broker_killer_tests.md prüfen.
2. Ohne tragfähige Variante: Tor G1 nicht bestanden; Stopp oder Zweitbroker.
3. Register und Rechner aktualisieren; Entscheidung signieren.

**Abschluss:** Entscheidung im Entscheidungsregister.

### RB-32 Kostendrift ausgelöst

**Schwere:** MITTEL · **Auslöser:** Kostendrift-Überwachung löst aus (§14.2)

1. Einstiegssperre für die betroffene Instrumentgruppe.
2. Kostenmodell mit gemessenen Kosten neu rechnen; Wirtschaftlichkeit neu bewerten.

**Abschluss:** Betreiberentscheidung auf Basis der Neuberechnung.

### RB-33 Verwechslung Demo und Echtgeld

**Schwere:** KRITISCH · **Auslöser:** Kontotyp laut Broker passt nicht zum signierten Modus

1. Sofort Kill-Switch Stufe 1; Sperrgrund und Alarm.
2. Nur der Betreiber klärt und signiert den Modus (BQ-09).

**Abschluss:** Modus eindeutig und signiert.

### RB-34 Kill-Switch oder Pause ausgelöst

**Schwere:** HOCH · **Auslöser:** Betreiber, Vertretung, Prüfmodul oder Risikomotor löst Kill-Switch Stufe 1 oder 2 bzw. eine Pause aus

1. Stufe 1: alle nicht schützenden Orders binnen P-RISK-KILL-CANCEL-S (5 Sekunden) stornieren; Einstiegssperre (KILL_SWITCH).
2. Stufe 2: zusätzlich geordnet glattstellen über `position=Ticket` (KILL_SWITCH_EXIT); Schutzstopps bleiben bis zum Schließen aktiv.
3. Auslöser und Zeitpunkt im Incident festhalten; Stornierungen im Abgleich nachweisen.
4. Fortsetzen nur durch den Betreiber: nach Stufe 1 mit Stornierungsnachweis, nach Stufe 2 mit flachem Konto.

**Abschluss:** Ursache geklärt; der Betreiber signiert die Fortsetzung.

### RB-35 Betreiber nicht erreichbar

**Schwere:** HOCH · **Auslöser:** Keine bestätigte Erreichbarkeit seit P-OPS-PRESENCE-MAX-D (7 Tage)

1. Einstiegssperre (OPERATOR_ABSENT); Schutz, Zeitstopps und Abbau laufen weiter.
2. Vertretung wird über beide Alarmwege benachrichtigt; sie darf pausieren, den Kill-Switch auslösen und abbauen, aber nicht fortsetzen.
3. Läuft der Grant während der Abwesenheit ab, gilt EXIT_ONLY (RB-19).

**Abschluss:** Betreiber bestätigt die Erreichbarkeit signiert.
<!-- GEN:END gen.runbooks -->
