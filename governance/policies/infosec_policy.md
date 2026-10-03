# Richtlinie Informationssicherheit

1. **Minimale Rechte:** Jede Identität erhält nur die Rechte ihrer Aufgabe (`security/security_architecture.md`).
2. **Schlüssel:** Freigaben nur mit Hardware-Schlüssel; Rotation nach `security/key_management.md`; Break-glass nur für Schutz und Abbau.
3. **Netz:** getrennte Vertrauensbereiche, Standardverbot, WireGuard und gegenseitige TLS-Authentifizierung; kein öffentlicher Fernzugang zum Geldpfad.
4. **Härtung und Updates:** kritische Sicherheitsupdates binnen <!--v:param:P-SEC-PATCH-CRIT-D|d0-->14<!--/v--> Tagen, im Wartungsfenster außerhalb der Handelszeiten.
5. **Secrets:** nie in Repository, Logs, Tickets, Chats oder Umgebungsvariablen von Agentenprozessen; automatischer Scan.
6. **Protokolle:** zentrale Auswertung mit Alarmregeln; Manipulationsschutz durch Hash-Ketten im Journal.
7. **Prüfung:** Penetrationstest vor G8; Sicherheitstests T-SEC-001 bis T-SEC-015 in der Abnahme; Orientierung an ISO/IEC 27001 und BSI IT-Grundschutz.
