# Bedrohungsmodell (§12)

> **Betreiberfassung.** Das Modell fragt, wer dem System schaden könnte und wie: externe Angreifer, Innentäter und Bedienfehler, ein kompromittierter KI-Agent, eine vergiftete Lieferkette und die Übernahme des Brokerkontos. Für jeden Angreifer gibt es einen Angriffsbaum, die Gegenmaßnahmen und einen Test, der zeigt, ob die Maßnahme wirkt. Der größte mögliche Schaden bleibt auf das Guthaben beim Broker und eine Kurslücke darüber hinaus begrenzt, weil das System nie Geld bewegen kann. Die Tests laufen vor dem Systembau (Konzept), im Bau (Abnahme) und vor dem Pilot (Penetrationstest). Für Go/No-Go heißt das: Ohne bestandene Sicherheitstests kein Echtgeld. Nächster Schritt ist der Test der Broker-Zugänge in den Killer-Tests (KT-16).

## 1 Schutzgüter

(1) Guthaben beim Broker, (2) Integrität von Entscheidungen, Limits und Grants, (3) Signaturschlüssel des Betreibers und des Evaluators, (4) Holdout, Evidenz und Torergebnisse, (5) Broker-, Daten- und Anbieter-Credentials, (6) Verfügbarkeit des Schutzes offener Positionen, (7) Vertraulichkeit von Konto- und Betreiberdaten, (8) lizenzierte Daten.

## 2 Vertrauensgrenzen

Geldpfad ↔ Broker; KI-Zone ↔ Internet (nur über Allowlist-Proxy und LLM-Gateway); KI-Zone → Geldpfad (nur Projektschnittstelle); KI-Zone → Prüfmodul (nur Einreichungen); Prüfmodul → Geldpfad (nur signierte Torergebnisse); Betreiber → System (nur signierte Aktionen); Betreiber → Broker (eigener Zugang, Kundenportal mit Zwei-Faktor-Anmeldung).

## 3 STRIDE-Übersicht

| Bedrohung | Beispiel | Gegenmaßnahme | Test |
|---|---|---|---|
| Spoofing | Dritter oder Agent gibt sich als Betreiber aus | Signatur mit Hardware-Schlüssel, Ablauf nach P-SEC-SIG-EXPIRY-MIN | T-SEC-009, T-SEC-013 |
| Spoofing | fremde Anmeldung am MT5-Konto | Hauptpasswort nur im Geldpfad, Rotation, Fencing; Brokerwarnungen | T-SEC-010, KT-16 |
| Tampering | Artefakt nach Review getauscht | Importer mit eigenem Digest, Quarantäne, signierte Releases | T-SEC-006 |
| Tampering | gefälschtes Torergebnis | Evaluator im Prüfmodul, Signatur, Prüfung im Grant-Register | T-SEC-011 |
| Repudiation | unklare Urheberschaft einer Freigabe | Journal nur anhängend, signierte Aktionen, Autor ≠ Prüfer | T-SEC-009 |
| Information disclosure | Secrets, Holdout oder lizenzierte Daten fließen ab | keine Secrets in der KI-Zone, Holdout nur im Prüfmodul, Egress-Allowlist, Kanarienprüfung | T-SEC-001, T-SEC-003, T-SEC-012 |
| Denial of service | Forschungsjob oder Update blockiert den Geldpfad | getrennte Instanzen, Sandbox-Grenzen, Plattenstufen | DR-02 |
| Elevation of privilege | Prompt-Injection bringt den Agenten zu Orders | Werkzeug-Allowlist, kein Netzweg zum Broker, schreibgeschützte Konfiguration | T-SEC-002, T-SEC-004, T-SEC-005 |

## 4 Angriffsbäume

**A1 Externer Angreifer – Ziel: Orders im Konto platzieren oder Geld abziehen**
- A1.1 Fernzugang zum Geldpfad-VPS → kein öffentlicher RDP-Zugang, nur über WireGuard; Anwendungs-Allowlist; Updates binnen P-SEC-PATCH-CRIT-D (T-SEC-010, T-SEC-015).
- A1.2 MT5-Zugangsdaten stehlen → Hauptpasswort nur als geschütztes Secret im Geldpfad; Rotation (P-SEC-CRED-ROTATION-D); Broker meldet neue Anmeldungen (X-BRK-API) (T-SEC-008, KT-16).
- A1.3 Auszahlung veranlassen → Systemanmeldung hat kein Auszahlungsrecht; Kundenportal mit Zwei-Faktor-Anmeldung des Betreibers (T-SEC-007).

**A2 Innentäter oder Bedienfehler – Ziel: Grenzen umgehen oder falschen Modus aktivieren**
- A2.1 Limit im laufenden Betrieb erhöhen → Parameter nur per Release der Klasse D mit zweiter menschlicher Freigabe und Karenzzeit (§13).
- A2.2 Demo und Echtgeld verwechseln → Moduskontrolle PTC-10 gegen den Kontotyp laut Broker; nur der Betreiber signiert den Modus (RB-33, DR-08).
- A2.3 Hebel nach Verlusten erhöhen (RK-06) → Aufstieg nur nach Evidenzkriterien und doppelter Freigabe; automatischer Abstieg (§7.8).

**A3 Kompromittierter KI-Agent – Ziel: Orders, Freigaben oder Datenabfluss**
- A3.1 Order über die Projektschnittstelle → nicht in der Allowlist, Abweisung und Sicherheitsereignis (T-SEC-005).
- A3.2 Eigene Skills oder Konfiguration ändern → schreibgeschützt eingebunden; Änderungen nur als Release (T-SEC-004).
- A3.3 Daten oder Secrets an den Modellanbieter → LLM-Gateway mit Kanarienprüfung; keine Secrets in der KI-Zone (T-SEC-012, T-SEC-001).
- A3.4 Torergebnis fälschen → Evaluator im Prüfmodul, Signatur, kein Schlüssel in der KI-Zone (T-SEC-011).
- A3.5 Injection über Web, Logs, Daten oder Brokerfehlertexte → Inhalte sind Daten, nie Anweisungen; Korpus mit <!--v:param:P-SEC-INJECTION-CASES|d0-->30<!--/v--> Fällen führt zu keiner Rechteerweiterung (T-SEC-002).
- A3.6 Handelsabsicht mit Erzeuger HERMES oder aus dem Projektdienst → die Verträge des Geldpfads lassen nur Geldpfad-Erzeuger zu (`schemas/order_intent.schema.json`, `schemas/risk_decision.schema.json`); ungültige Beispiele `examples/invalid/order_intent_from_hermes.json` und `examples/invalid/risk_decision_from_hermes.json` (T-CON-001).
- A3.7 Schwachstelle in `svc-projectops` als Sprungbrett in den Geldpfad-Host → eigene Identität ohne Brokerzugriff, mTLS, Token-Rotation, Werkzeug-Allowlist; Restrisiko RK-32, bis in BS-05 über ein Pull-Modell ohne eingehende Verbindung entschieden ist (T-SEC-014).
- A3.8 Ein-VPS-Betrieb (DEC-CF-04) → Kompromittierung eines Dienstes erreicht den Geldpfad-Host und das Prüfmodul; getrennte Konten und Firewall-Regeln mindern, heben das Restrisiko RK-31 aber nicht auf (X-INF-ZONES sperrt G5).

**A4 Lieferkette – Ziel: Schadcode in Kern, Adapter oder Agent**
- A4.1 Kompromittierte Abhängigkeit → gepinnte Versionen mit Hashes, Schwachstellenprüfung, SBOM (T-SEC-006).
- A4.2 Kompromittiertes Agenten-Update → kein `hermes update`, Update nur als geprüftes Release mit Evaluationssuite (§11.3).
- A4.3 Manipuliertes MT5-Terminal-Update → Terminal nur aus der Quelle des Brokers; Integritätsprüfung nach Updates; Killer-Tests nach größeren Updates wiederholen.

**A5 Übernahme des Brokerkontos – Ziel: Handel oder Auszahlung außerhalb des Systems**
- A5.1 Phishing des Kundenportals → Hardware-Schlüssel oder Zwei-Faktor-Anmeldung, Auszahlungen nur auf hinterlegtes Referenzkonto (X-BRK-ACCOUNT).
- A5.2 Fremde Orders → Abgleich erkennt Fremdaktivität (FOREIGN_POSITION), Kill-Switch, Sperrung beim Broker (RB-13).
- A5.3 Schadensrahmen → beim Broker liegt nur ein Teil des Kapitals (P-ECO-CASH-AT-BROKER); Nachschussausschluss für Privatkunden, sofern die Kundeneinstufung ihn vorsieht (SRC-REG-BAFIN-FUT, X-BRK-NACHSCHUSS).

## 5 Tests

<!-- GEN:BEGIN tab.sec_tests -->
| Test | Inhalt | Stufe |
|---|---|---|
| T-SEC-007 | kein Auszahlungsrecht der Systemanmeldung | BS-01 (GATE-G1) |
| T-SEC-008 | Secret-Scan von Repository und Logs | BS-01 (GATE-G1) |
| T-SEC-001 | KI-Zone ohne Zugriff auf Broker, Secrets, Grants und Schlüssel | BS-05 (GATE-G5) |
| T-SEC-002 | Prompt-Injection-Korpus ohne Rechteerweiterung | BS-05 (GATE-G5) |
| T-SEC-003 | Egress-Allowlist der KI-Zone | BS-05 (GATE-G5) |
| T-SEC-004 | Schreibschutz von Konfiguration, Skills, Hooks und Gedächtnisdateien | BS-05 (GATE-G5) |
| T-SEC-005 | Projektschnittstelle: fremde Werkzeuge, Identität, Übergröße, Frist | BS-05 (GATE-G5) |
| T-SEC-006 | Importer: Symlink, Hardlink, Pfadausbruch, Austausch nach Review | BS-05 (GATE-G5) |
| T-SEC-009 | Signaturprüfung: Ablauf, Wiederholung, falscher Grund | BS-05 (GATE-G5) |
| T-SEC-010 | Geldpfad-Firewall | BS-05 (GATE-G5) |
| T-SEC-011 | Torergebnisse nur mit Evaluator-Signatur | BS-05 (GATE-G5) |
| T-SEC-012 | Kanarienprüfung am LLM-Gateway | BS-05 (GATE-G5) |
| T-SEC-014 | externer Penetrationstest | BS-05 (GATE-G5) |
| T-SEC-015 | Härtung des Windows-VPS | BS-05 (GATE-G5) |
| T-SEC-013 | Freigaben nur mit Hardware-Schlüssel; Break-glass-Ablauf | BS-06 (GATE-G6) |
<!-- GEN:END tab.sec_tests -->

Prozedur, Orakel und Bestehenskriterium je Test stehen im Testkatalog `implementation/test_catalog.json`; diese Tabelle ist daraus erzeugt. Der Secret-Scan (T-SEC-008) läuft ab BS-01 bei jedem Commit; er wird eingerichtet, bevor das erste Zugangsdatum existiert.
