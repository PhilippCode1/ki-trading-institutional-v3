# Service-Levels und SLOs (§10.6, §14.1)

> **Betreiberfassung.** Die Ziele beschreiben, was der Betrieb leisten soll: Verfügbarkeit des Geldpfads in Handelszeiten, schnelle Alarme, schnelle Wiederherstellung und rechtzeitige Berichte. Wo ein Ziel nur mit einer zweiten Person erreichbar ist, steht das dabei. Jedes Ziel hat eine Messung und eine Reaktion, wenn es verfehlt wird. Die Werte sind Entwürfe und werden nach dem Paper-Betrieb überprüft. Für Go/No-Go heißt das: Die Ziele sind für einen Pilot angemessen, verlangen aber eine Vertretung. Nächster Schritt: Messung im Paper-Betrieb (G7).

| SLO | Ziel | Messung | bei Verfehlung |
|---|---|---|---|
| Verfügbarkeit Geldpfad in Handelszeiten | <!--v:param:P-SLO-CORE-AVAIL|pct1-->99,5 %<!--/v--> je Monat | Heartbeats des externen Monitors | Post-Mortem; Fehlerbudget aufgebraucht → keine Releases außer Korrekturen |
| Zustellung kritischer Alarme | <!--v:param:P-SLO-ALERT-LATENCY-S|d0-->60<!--/v--> Sekunden | Zeitstempel Ereignis gegen Zustellung | Kanal prüfen (RB-09) |
| Quittung kritischer Incidents in Handelszeiten | <!--v:param:P-SLO-INCIDENT-ACK-MIN|d0-->30<!--/v--> Minuten | Journal | nur mit Vertretung zusicherbar (X-ORG-DEPUTY) |
| Wiederanlauf mit Abgleich | <!--v:param:P-OPS-RESTART-S|d0-->120<!--/v--> Sekunden | Journal | Ursache klären (RB-01) |
| Wiederherstellung Geldpfad | <!--v:param:P-OPS-RTO-CORE-H|d0-->4<!--/v--> Stunden | Restoreprobe (DR-01) | Drill wiederholen; G6 gesperrt |
| Datenverlust Journal höchstens | <!--v:param:P-OPS-RPO-JOURNAL-MIN|d0-->5<!--/v--> Minuten | Offsite-Kopie | Sicherung prüfen |
| Snapshot-Alter für Risikoentscheidungen | <!--v:param:P-EXE-SNAPSHOT-MAX-S|d0-->60<!--/v--> Sekunden | Metrik | Einstiegssperre (PTC-09) |
| Tagesbericht nach Handelstagesende | <!--v:param:P-SLO-REPORT-LAG-H|d0-->2<!--/v--> Stunden | Zeitstempel | Bericht nachholen; Ursache |
| Stornierung aller Orders durch Kill-Switch | <!--v:param:P-RISK-KILL-CANCEL-S|d0-->5<!--/v--> Sekunden | Drill DR-10 | Kill-Switch gesperrt → keine Einstiege |

Service-Levels der Dienstleister (Broker, VPS, Datenanbieter, Modellanbieter) werden bei Vertragsschluss erfasst (`governance/policies/outsourcing_policy.md`); das System unterstellt keine zugesicherte Verfügbarkeit des Brokers und schützt Positionen deshalb mit Stopps beim Broker.
