# Drills (§14.1, Tor G6)

> **Betreiberfassung.** Ein Runbook ist erst etwas wert, wenn es geprobt ist. Die Drills laufen im Demokonto oder auf isolierten Instanzen, nie mit Echtgeld, und jeder wird mit Datum, Ergebnis, Abweichungen und Maßnahmen protokolliert. Tor G6 verlangt bestandene Drills zu Restore, Broker- und Datenausfall, Margin, Kill-Switch und Schlüsselverlust. Danach wiederholen sie sich im festen Rhythmus. Für Go/No-Go heißt das: Ohne bestandene Drills kein Paper-Forward und kein Pilot. Nächster Schritt: erster Drill-Durchgang nach dem Systembau (BS-06).

Quelle: `operations/drill_register.json` (<!--v:calc:drills_total|int-->10<!--/v--> Drills).

<!-- GEN:BEGIN tab.drills -->
| ID | Drill | Rhythmus | Tor | Ablauf | bestanden, wenn |
|---|---|---|---|---|---|
| DR-01 | Restore auf isolierter Instanz | P-OPS-RESTORE-DRILL-D (30 Tage) | GATE-G6 | Journal aus Offsite-Kopie wiederherstellen, Halt und Widerruf unmittelbar vor der letzten Sicherung prüfen, Zeit messen. | Wiederherstellung innerhalb P-OPS-RTO-CORE-H (4 Stunden); kein Datenverlust über P-OPS-RPO-JOURNAL-MIN (5 Minuten); Grants ungültig. |
| DR-02 | Geldpfad-Neustart und Journalfehler | vierteljährlich | GATE-G6 | Prozessabbruch an vier Punkten (vor Commit, nach Commit, nach Senden, nach Antwort) im Demokonto; Journal schreibgeschützt setzen. | Kein Doppelsenden; Wiederanlauf innerhalb P-OPS-RESTART-S (120 Sekunden); Notfalljournal greift. |
| DR-03 | Brokerausfall und Brokerdirektkontrolle | halbjährlich | GATE-G6 | Brokerverbindung im Demokonto trennen; Betreiber führt Schutzaktionen über den eigenen Zugang aus; danach Abgleich. | Schutz erhalten; Eingriff vollständig abgeglichen. |
| DR-04 | Datenausfall | vierteljährlich | GATE-G6 | Kursstrom eines Instruments anhalten und veraltete Kurse einspeisen. | Einstiegssperre nach P-DATA-STALE-S (10 Sekunden); keine Order ohne frische Daten. |
| DR-05 | Margin-Erhöhung und Tagesverlust-Leiter | vierteljährlich | GATE-G6 | Im Demokonto simulierte Margin-Erhöhung um P-MRG-STRESS-2 (1 Anteil Erhöhung) und Verluststufen einspielen. | Größen und Leiter reagieren wie spezifiziert. |
| DR-06 | Schlüsselverlust und Kompromittierungsverdacht | jährlich | GATE-G6 | Verlust des Signaturschlüssels simulieren; Ersatz aus der Hinterlegung; alle Grants widerrufen; Credentials rotieren. | Keine geldwirksame Aktion ohne gültige Signatur; Ersatz binnen eines Arbeitstags. |
| DR-07 | Isolation der KI-Zone | halbjährlich | GATE-G6 | Kanarienwert in einer Anfrage auslösen. | Isolation binnen P-OPS-ISOLATE-MIN (15 Minuten); Geldpfad unverändert. |
| DR-08 | Alarmkanäle und Moduskontrolle | monatlich | GATE-G6 | Testalarm über beide Kanäle; falschen Kontotyp simulieren. | Quittung innerhalb P-OPS-ALERT-ACK-H (12 Stunden); Kill-Switch bei falschem Modus. |
| DR-09 | Fencing mit weiterlaufender Altinstanz | vor G6 und nach jedem Host-Wechsel | GATE-G6 | Neue Instanz aufsetzen, während die alte läuft; Hauptpasswort ändern. | Alte Instanz abgewiesen; genau ein Writer. |
| DR-10 | Kill-Switch und Terminal-Neustart | vierteljährlich | GATE-G6 | Kill-Switch Stufe 1 und 2 im Demokonto; Terminal während offener Orders neu starten. | Alle Orders binnen P-RISK-KILL-CANCEL-S (5 Sekunden) storniert, kein Schutzstopp verloren, Abgleich konsistent. |
<!-- GEN:END tab.drills -->

## Protokoll

Jeder Drill erzeugt einen Eintrag im Journal mit: Drill-ID, Datum, Umgebung (Demo oder isoliert), Beteiligte, Ablauf, gemessene Zeiten, Ergebnis (bestanden oder nicht), Abweichungen, Maßnahmen mit Termin und Signatur des Betreibers. Ein nicht bestandener Drill ist ein Incident der Schwere HOCH; das zugehörige Tor bleibt gesperrt, bis die Wiederholung besteht.
