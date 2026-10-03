# Incident-Richtlinie

| Schwere | Beispiele | Reaktion | Quittung |
|---|---|---|---|
| KRITISCH | Schutzstopp fehlt, Kompromittierung, Tagesgrenze erreicht, Demo/Echtgeld verwechselt | automatische Sperre oder Kill-Switch; Alarm über beide Kanäle | Ziel <!--v:param:P-SLO-INCIDENT-ACK-MIN|d0-->30<!--/v--> Minuten in Handelszeiten (Vertretung nötig) |
| HOCH | UNKNOWN, Brokersitzung getrennt, Leiterstufe L3, Margin-Defizit | Einstiegssperre, Runbook | am selben Handelstag |
| MITTEL | Datenlücke, Alarmkanal gestört, Kostendrift | Sperre für betroffene Instrumente | binnen eines Arbeitstags |
| NIEDRIG | KI-Zone ausgefallen, Kontingent erschöpft | keine Wirkung auf den Geldpfad | wöchentliche Risikorunde |

1. Jeder Incident hat Zeitlinie, Runbook-Verweis, Ursache, Maßnahmen und Abschluss durch signierte Aktion.
2. Kritische und hohe Incidents erhalten ein Post-Mortem ohne Schuldzuweisung mit Maßnahmen und Termin; wiederkehrende Ursachen werden als Problem geführt.
3. Verriegelte Sperrgründe löst nur die dafür vorgesehene signierte Aktion; technische Heilung entfernt nie einen verriegelten Grund.
