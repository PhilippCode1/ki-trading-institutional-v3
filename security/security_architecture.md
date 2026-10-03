# Sicherheitsarchitektur (§12)

> **Betreiberfassung.** Sicherheit heißt hier vor allem: Niemand außer dir kann Geld bewegen, niemand außer dem Geldpfad kann handeln, und der KI-Agent kann nichts von beidem. Dafür gibt es getrennte Identitäten mit minimalen Rechten, getrennte Netzbereiche, signierte Freigaben mit Hardware-Schlüssel und eine zentrale Auswertung der Protokolle. Der Windows-VPS des Geldpfads wird gehärtet und ist nur über ein privates Netz erreichbar. Vor dem ersten Echtgeld prüft ein externer Penetrationstest die Umsetzung. Für Go/No-Go heißt das: Sicherheit ist spezifiziert und prüfbar, aber erst mit Abnahme und Penetrationstest belegt. Nächster Schritt: Klärung, ob der Broker einen Lesezugang und IP-Beschränkungen anbietet (X-BRK-API).

## 1 Identitäten und Rechte

| Identität | Bereich | darf | darf nicht |
|---|---|---|---|
| `svc-core` | Geldpfad | Journal schreiben, Brokeraufrufe als aktiver Writer über das MT5-Terminal | Netz außer Broker, Zeitdienst, Sicherung, Monitor; Konfiguration ändern |
| `svc-guardian` | Geldpfad | Lease, Heartbeat, technische Sperrgründe setzen | verriegelte Sperrgründe lösen, Orders |
| `svc-ops` | Geldpfad | signierte Betreiberaktionen und Grants prüfen und ausführen | unsignierte geldwirksame Aktionen |
| `svc-projectops` | Geldpfad | Register nach Allowlist lesen und Vorschläge schreiben | Brokerzugriff, Grants, Sperrgründe lösen |
| `svc-release` | Geldpfad | Quarantäne, Prüfung, Aktivierung im erlaubten Zustand | eigene Kandidaten freigeben |
| `svc-hermes` | KI-Zone (Container, kein Root) | Projektschnittstelle, eigene Arbeitsablage, Sandbox, LLM-Gateway | Broker, Secrets, Anbieter-Schlüssel, Governance-Dateien, Docker-Socket |
| `svc-llmgw` | KI-Zone | Anbieter-Schlüssel nutzen, geprüfte Anfragen weiterleiten | andere Ziele |
| `svc-evaluator` | Prüfmodul | Holdout einmal je Registrierung entschlüsseln, Torergebnisse signieren; Brokerdaten lesend | Kandidaten ändern, handeln |
| Betreiber | eigene Geräte mit Hardware-Schlüssel | signierte Aktionen, Grants, Freigaben, Moduswechsel; Kundenportal des Brokers | den Systemzugang zum Broker für eigene Eingriffe nutzen |
| externe Risikofunktion | eigene Geräte | Berichte und Cockpit lesen, Veto bei Profilaufstieg und Klassen C/D (signiert) | handeln, Parameter ändern |
| Notfallvertretung | eigene Geräte | Pause, Kill-Switch, Abbau (signiert) | Risiko erhöhen, Grants |

(Übernommen aus v2.0 und auf MT5 und Windows angepasst.)

## 2 Broker-Zugänge

- **Systemanmeldung (Geldpfad):** MT5-Hauptpasswort; handeln ja, Auszahlung nein (Auszahlungen nur über das Kundenportal). Nachweis vor jedem Grant (T-SEC-007).
- **Lesezugang (Prüfmodul, Monitor):** ein Zugang ohne Handelsrecht, falls der Broker ihn für Futures-Konten anbietet (etwa ein Investor-Passwort); sonst gleicht der Betreiber im Pilot täglich manuell ab. Zu klären mit X-BRK-API und KT-16.
- **Betreiberzugang:** Kundenportal mit Zwei-Faktor-Anmeldung; eigene Terminal-Anmeldung nur für angekündigte Eingriffe (RB-23).
- **IP-Beschränkung:** falls vom Broker angeboten, nur die Adresse des Geldpfad-VPS (X-BRK-API).

## 3 Netz

| Verbindung | erlaubt | Schutz |
|---|---|---|
| Geldpfad → Broker | ja | TLS des Terminals; ausgehende Firewall-Regel nur zu den Serveradressen des Brokers |
| Geldpfad → Zeitdienst, Offsite-Sicherung, Monitor | ja | ausgehende Allowlist |
| Betreiber → Geldpfad | nur über WireGuard | Hardware-Schlüssel, kein öffentlicher RDP-Port |
| KI-Zone → Geldpfad | nur Projektschnittstelle | WireGuard, mTLS, Token, Allowlist der Werkzeuge |
| KI-Zone → Internet | nur über Allowlist-Proxy; Modellanbieter nur über LLM-Gateway | Protokoll der Ziele; unbekannte Ziele abgewiesen |
| Prüfmodul → Geldpfad | nur signierte Torergebnisse und lesende Abfragen | WireGuard, mTLS |
| alles andere | verboten | Standardverbot |

Änderungen der Allowlists sind Änderungen der Klasse D (§13).

## 4 Härtung des Windows-VPS

Minimalinstallation ohne Browser und E-Mail; Anwendungs-Allowlist (nur Python-Laufzeit des Releases, MT5-Terminal, Dienste); Datenträgerverschlüsselung; automatische Sicherheitsupdates im Wartungsfenster außerhalb der Handelszeiten, kritische binnen <!--v:param:P-SEC-PATCH-CRIT-D|d0-->14<!--/v--> Tagen; Dienstkonten ohne Administratorrechte; Protokollweiterleitung an die zentrale Auswertung; Zeitsynchronisation mit Überwachung (P-OPS-CLOCK-*). Abnahme mit T-SEC-015.

## 5 Secrets, Inhalte, Lieferkette

- **Secrets** nur in geschützten Dateien oder dem Anmeldeinformationsspeicher des jeweiligen Dienstkontos, nie in Umgebungsvariablen von Agentenprozessen, Logs, Tickets oder im Repository; automatischer Scan (T-SEC-008). Dieses Paket enthält keine Secrets und keine personenbezogenen Werte; die Paketprüfung scannt danach.
- **Inhalte** aus Web, Logs, Daten, Brokerfehlertexten und fremden Repositories sind Daten, nie Anweisungen (T-SEC-002).
- **Lieferkette:** gepinnte Abhängigkeiten mit Hashes, SBOM je Release, Schwachstellenprüfung, Importer mit eigenem Digest und Quarantäne, kein Installieren aus Agenten-Hubs (T-SEC-006).

## 6 Protokollauswertung und Incident Response

Zentrale Auswertung (SIEM im kleinen Maßstab) der Ereignisprotokolle von Windows, Linux, Proxy, LLM-Gateway und Journal mit Regeln für: neue Anmeldungen, fehlgeschlagene Signaturen, abgewiesene Werkzeugaufrufe, unbekannte Egress-Ziele, Kanarientreffer, Änderungen an Allowlists. Incident Response: Erkennen → Eindämmen (Kill-Switch, Isolation, Sperre beim Broker) → Beseitigen (Neuaufbau aus Release, Rotation) → Wiederherstellen (Restore, Fencing, neuer Grant) → Lernen (Post-Mortem); Runbooks RB-12, RB-13, RB-17.

## 7 Penetrationstest und Orientierung

Externer Penetrationstest vor G8 (<!--v:costreg:COST-EXT-PENTEST|eur-->5.000 EUR<!--/v-->): Geldpfad-VPS, WireGuard-Zugang, Cockpit, Projektschnittstelle, LLM-Gateway; bestanden ohne offene kritische Befunde (T-SEC-014). Die Maßnahmen sind nach ISO/IEC 27001 und BSI IT-Grundschutz gegliedert (Organisation, Personen, physische und technologische Maßnahmen); eine Zertifizierung ist nicht vorgesehen. DORA (SRC-REG-DORA, nicht geprüft) beträfe nur Finanzunternehmen und damit B3/B4, die nach BQ-02 ausgeschlossen sind.
